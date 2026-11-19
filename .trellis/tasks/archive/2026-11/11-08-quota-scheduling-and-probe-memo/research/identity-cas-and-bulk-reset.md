# Research: Bulk Identity/Script Quota Reset & Atomic Identity CAS for Async Usage/Probe Writes

- **Query**: Investigate two P1 review findings on `plugins/sub2api-quota-extension/patches/quota-extension.patch` against `/tmp/sub2api-v0.2.20-base`:
  1. **[P1] Bulk credential/identity update leaves `TempUnschedulableUntil` intact (`quota-extension.patch:1445`)** — plus all identity/script mutation paths in `UpdateAccount` and `BulkUpdateAccounts`, atomic conditional SQL clearing in `accountRepository.BulkUpdate`, JSON `null` avoidance in `accounts.extra`, and immediate Redis scheduler snapshot sync (`shouldSync`).
  2. **[P1] Stale in-flight usage/quota query can overwrite new credential state (`quota-extension.patch:1221`)** — atomic identity + proxy + `quota_script` CAS across all post-network writes (`apikey_quota_*` extra keys, `temp_unschedulable_until` / `temp_unschedulable_reason`, `expires_at`, and `apikey_usage_unsupported_identity`) in `AccountUsageService` and `UpstreamBillingProbeService`.
- **Scope**: `/tmp/sub2api-v0.2.20-base/backend/internal/{service,repository,handler}` and `/Users/minami/Code/S/Sub2API-Plugins/plugins/sub2api-quota-extension/{patches,tests}`
- **Date**: 2026-11-11

---

## 1. Key Files Inspected

- `plugins/sub2api-quota-extension/patches/quota-extension.patch` (`:1110-1500`): `account_upstream_quota.go`, `account_usage_service.go`, `admin_account.go`, `account_repo.go`, `scheduler_cache.go`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/admin_account.go`: `UpdateAccount` (`:620-928`), `BulkUpdateAccounts` (`:1007-1266`), `updatesUpstreamBillingProbeIdentity` (`:1268-1275`), `upstreamBillingProbeIdentity` (`:1277-1291`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/account_upstream_quota.go`: `APIKeyQuotaManagedExtraKeys` (`:33-46`), `memoizeUpstreamProbeUnsupported` (`:191-210`), `clearUpstreamProbeUnsupported` (`:212-226`), `fillUpstreamAPIKeyUsage` (`:228-317`), `syncAPIKeyQuotaSchedulingState` (`:330-445`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/account_quota_script.go`: `QuotaScriptExtraKey` (`:21`), `AccountQuotaScript` (`:23-32`), `normalizeQuotaScriptExtra` (`:34-48`), `ExecuteQuotaScript` (`:50-132`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe.go`: `upstreamBillingProbeSnapshotWriter` (`:164-171`), `probeLoadedAccount` (`:623-761`), `persistProbeFailure` (`:763-803`), `updateSnapshot` (`:805-815`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo.go`: `updateLockedAccount` (`:528-623`), `lockAndMergeAccountProbeExtra` (`:625-862`), `UpdateCredentials` (`:875-970`), `SetGrokCredentialTempUnschedulableIfMatch` (`:2552-2598`), `UpdateExtra` (`:2803-2870`), `UpdateUpstreamBillingProbeSnapshot` (`:2874-2993`), `lockAndMatchProbeProxyIdentity` (`:2995-3037`), `BulkUpdate` (`:3069-3395`), `ResetQuotaUsedAndClearRateLimitCooldown` (`:4086-4119`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/scheduler_cache.go` (`:1320-1375`): `filterSchedulerAccountExtra` caches all 11 `apikey_quota_*` keys in Redis.
- Upstream tests: `account_repo_upstream_billing_probe_cas_test.go`, `account_repo_upstream_billing_probe_update_test.go`, `account_repo_ollama_cloud_usage_test.go` (`:346-382`), `upstream_billing_probe_test.go` (`:600-627`), `admin_account_upstream_billing_probe_test.go` (`:260-405`, `:707-752`).
- Plugin tests: `plugins/sub2api-quota-extension/tests/{test_upstream_quota_test.go,test_quota_script_test.go}`.

---

## 2. Finding 1 Analysis: Bulk & Single Account Identity / Script Quota Reset

### 2.1 Exact Defects Identified in Current Code

1. **`BulkUpdateAccounts` leaves `TempUnschedulableUntil` / `TempUnschedulableReason` intact (`admin_account.go:1184-1194`, `quota-extension.patch:1445`)**:
   - When `updatesUpstreamBillingProbeIdentity(input.Credentials) || input.ProxyID != nil`, `BulkUpdateAccounts` sets `repoUpdates.Extra[key] = nil` for `APIKeyQuotaManagedExtraKeys`, **but never clears `temp_unschedulable_until` / `temp_unschedulable_reason`**.
   - Any account paused by a dated quota window (`temp_unschedulable_reason = "apikey_quota_window_exhausted"`, `account_upstream_quota.go:30, 426`) stays unschedulable in `Account.IsSchedulable()` (`account.go:208-210`) and `Account.IsCredentialUsableForShadow()` (`account.go:237-239`) until the old credential's `reset_at` expires, even after bulk rotating `api_key`, `base_url`, `header_override*`, or `proxy_id`.

2. **`BulkUpdate` writes literal JSON `null`s into `accounts.extra` for `APIKeyQuotaManagedExtraKeys` (`account_repo.go:3204-3224`)**:
   - In `accountRepository.BulkUpdate` (`account_repo.go:3208-3223`), `updates.Extra` is marshaled and merged with `COALESCE(extra, '{}'::jsonb) || $N::jsonb`.
   - PostgreSQL `||` does **not** remove keys with `null` values; `UpstreamBillingProbeExtraKey: nil` only works because `upstreamBillingProbeSnapshotClearRequested(updates.Extra)` (`account_repo.go:3059-3062`) explicitly appends `- 'upstream_billing_probe'` at `:3219-3221` (and similarly in `UpdateExtra` at `:2807, 2826-2828`).
   - Currently `APIKeyQuotaManagedExtraKeys` are **not** stripped with `- '<key>'`, so bulk identity updates pollute `accounts.extra` with 12 `null`-valued keys (`{"apikey_quota_exhausted": null, ...}`) on every row in the batch (including OAuth rows).

3. **`BulkUpdate` does NOT immediately sync Redis scheduler account snapshots (`account_repo.go:3352-3361`)**:
   - `scheduler_cache.go:1346-1356` projects all 11 `apikey_quota_*` scheduling keys (plus `TempUnschedulableUntil` on the `Account` struct) into the per-account Redis snapshot (`SetAccount`).
   - In `accountRepository.BulkUpdate` (`account_repo.go:3355-3361`), `shouldSync` is only `true` when `updates.ExpiresAt != nil`, `updates.Status` is `error`/`disabled`, or `updates.Schedulable` is `false`.
   - Although `SchedulerOutboxEventAccountBulkChanged` is enqueued (`:3340`), `r.syncSchedulerAccountSnapshots(baseCtx, ids)` is skipped when `shouldSync == false`, leaving stale `TempUnschedulableUntil` and `apikey_quota_*` keys in Redis per-account snapshots (read by sticky sessions and `GetAccount`) until async outbox worker catch-up.

4. **`quota_script` changes in `UpdateAccount` and `BulkUpdateAccounts` do NOT reset quota scheduling state (`admin_account.go:632, 809-827, 1009-1021, 1184-1194`)**:
   - **In `UpdateAccount` (`admin_account.go:632, 809-827`)**:
     - `previousProbeIdentity := upstreamBillingProbeIdentity(account)` (`:632`) only tracks `platform`, `type`, `proxy_id`, `api_key`, `base_url`, `header_override_enabled`, and `header_overrides` (`:1277-1291`).
     - When `input.Extra` adds, edits, or clears `quota_script` (`QuotaScriptExtraKey`) without changing HTTP probe credentials/proxy, `!reflect.DeepEqual(previousProbeIdentity, upstreamBillingProbeIdentity(account))` is `false`. Because lines `728-733` copied `APIKeyQuotaManagedExtraKeys` forward from the old `account.Extra`, stale `apikey_quota_*` values and `apikey_quota_window_exhausted` `TempUnschedulableUntil` remain stuck!
   - **In `BulkUpdateAccounts` (`admin_account.go:1009-1021, 1184-1194`)**:
     - `AccountHandler.BulkUpdate` (`account_handler.go:2370`) forwards `req.Extra` directly to `BulkUpdateAccountsInput.Extra`.
     - `BulkUpdateAccounts` currently does **not** normalize/validate `input.Extra["quota_script"]` via `normalizeQuotaScriptExtra` (unlike `CreateAccount` at `:425` and `UpdateAccount` at `:701`), and does **not** clear `apikey_quota_*` / `apikey_quota_%` temp pause when `quota_script` is updated or cleared in `input.Extra`.

5. **All quota/probe identity inputs across single & bulk updates**:
   - **Standard probe/usage identity (`admin_account.go:1268-1291`)**: `platform`, `type`, `proxy_id`, and credentials `api_key`, `base_url`, `header_override_enabled`, `header_overrides`.
   - **Adaptive CN provider credentials (`account.go:1606-1623`, `account_usage_service.go:402-404`, `upstream_billing_probe.go:630-632`, `account_quota_script.go:108-110`)**:
     - When `account.RoutesProtocolByInbound() && account.IsAdaptiveAPIProtocol()`, all three paths (`fillUpstreamAPIKeyUsage`, `probeLoadedAccount`, `ExecuteQuotaScript`) compute `baseURL = account.GetCNProtocolBaseURL(APIProtocolChatCompletions)`, which reads `api_protocol` (`credKeyAPIProtocol`), `api_base_urls`, and `provider_mode` (`account_mode`).
     - Including `"api_protocol"`, `"api_base_urls"`, `"provider_mode"`, `"account_mode"` in `updatesUpstreamBillingProbeIdentity` and `upstreamBillingProbeIdentity` ensures adaptive CN accounts also invalidate stale probe/quota state when their effective `chat_completions` endpoint changes (none of the upstream tests in `admin_account_upstream_billing_probe_test.go:260-318, 707-752` pass those keys in negative cases).
   - **Single-account `UpdateAccount` ordering & race safety (`admin_account.go:820-926`)**:
     - Currently `UpdateAccount` calls `s.accountRepo.ClearTempUnschedulable(ctx, account.ID)` at `:824`:
       1. **Before** `RateMultiplier`, `GroupIDs`, and `checkMixedChannelRisk` validations (`:858-900`) — mutating DB even if validation fails and returns an error!
       2. **Unconditionally** (`SET temp_unschedulable_until = NULL, temp_unschedulable_reason = NULL` at `account_repo.go:2601-2608`) — wiping a concurrent non-quota pause if one arrived after `GetByID` (`:623`).
       3. **Gated on stale `t0` memory (`strings.HasPrefix(account.TempUnschedulableReason, "apikey_quota_")`)** — if an in-flight `GetUsage` for the *old* credential committed `temp_unschedulable_reason = 'apikey_quota_window_exhausted'` between `UpdateAccount`'s `GetByID` (`t0`) and `Update` (`t2`), `account.TempUnschedulableReason` in memory at `t0` was `""`, so `UpdateAccount` would skip clearing it!

### 2.2 Recommended Design for Finding 1

- **Respect `design.md` constraint (line 5)**: Do **NOT** add temp-unschedulable fields to `service.AccountBulkUpdate` (`account_service.go:159-175`). Follow the existing `upstreamBillingProbeSnapshotClearRequested(updates.Extra)` pattern (`account_repo.go:3059-3066`).
- **Distinguish HTTP probe identity vs `quota_script` source cleanly**:
  - Define two key slices in `account_upstream_quota.go`:
    - `APIKeyQuotaSchedulingExtraKeys` (the 11 `apikey_quota_*` keys: `APIKeyQuotaExhaustedExtraKey` + the 5 window `used_percent`/`reset_at` pairs).
    - `APIKeyQuotaManagedExtraKeys` (`APIKeyUsageUnsupportedIdentityExtraKey` + `APIKeyQuotaSchedulingExtraKeys`).
  - **In `UpdateAccount` (`admin_account.go:632, 809-926`)**:
    - Capture `previousProbeIdentity := upstreamBillingProbeIdentity(account)` and `previousQuotaScript := AccountQuotaScript(account)` before mutating `account`.
    - Compute `probeIdentityChanged := !reflect.DeepEqual(previousProbeIdentity, upstreamBillingProbeIdentity(account))` and `quotaScriptChanged := AccountQuotaScript(account) != previousQuotaScript`.
    - If `probeIdentityChanged`: delete `UpstreamBillingProbeExtraKey` and all `APIKeyQuotaManagedExtraKeys` from `account.Extra`.
    - Else if `quotaScriptChanged`: delete `APIKeyQuotaSchedulingExtraKeys` (or all `APIKeyQuotaManagedExtraKeys`) from `account.Extra` while keeping `UpstreamBillingProbeExtraKey` intact (since `/v1/sub2api/billing` does not use `quota_script`).
    - If `(probeIdentityChanged || quotaScriptChanged)` and `strings.HasPrefix(account.TempUnschedulableReason, "apikey_quota_")`: clear in-memory `account.TempUnschedulableUntil = nil` and `account.TempUnschedulableReason = ""`.
    - **After** `s.updateAccountRecord(...)` succeeds (`:903`), if `probeIdentityChanged || quotaScriptChanged` (unconditionally, regardless of `t0` `account.TempUnschedulableReason`!), invoke conditional quota temp-unschedulable clear so:
      1. Failed validations never mutate DB.
      2. A concurrent `GetUsage` pause committed between `GetByID` and `Update` is still cleared.
      3. Any concurrent non-quota `temp_unschedulable_reason` is preserved (`WHERE id = $1 AND deleted_at IS NULL AND temp_unschedulable_reason LIKE 'apikey_quota_%'`).
  - **In `BulkUpdateAccounts` (`admin_account.go:1009-1025, 1184-1196`)**:
    - When `len(input.Extra) > 0`, check `rawScript, quotaScriptProvided := input.Extra[QuotaScriptExtraKey]` before stripping managed keys:
      - Validate `quota_script`: if `quotaScriptProvided`:
        - If `rawScript == nil`: set `input.Extra[QuotaScriptExtraKey] = nil` (to delete `quota_script` in bulk).
        - Else if `s, ok := rawScript.(string); ok`: if `strings.TrimSpace(s) == ""` set `input.Extra[QuotaScriptExtraKey] = nil`, else keep `s`.
        - Else return `infraerrors.BadRequest("INVALID_QUOTA_SCRIPT", "quota_script must be a string")` (matching `normalizeQuotaScriptExtra` at `account_quota_script.go:39-42`).
    - Compute `probeIdentityUpdated := updatesUpstreamBillingProbeIdentity(input.Credentials) || input.ProxyID != nil`.
    - If `probeIdentityUpdated`:
      - Set `repoUpdates.Extra[UpstreamBillingProbeExtraKey] = nil` and set all `APIKeyQuotaManagedExtraKeys` to `nil` in `repoUpdates.Extra`.
    - Else if `quotaScriptProvided`:
      - Set all `APIKeyQuotaSchedulingExtraKeys` to `nil` in `repoUpdates.Extra` (preserving `UpstreamBillingProbeExtraKey` and `APIKeyUsageUnsupportedIdentityExtraKey`).
  - **In `accountRepository.BulkUpdate` (`account_repo.go:3204-3235, 3352-3361`) and `UpdateExtra` (`account_repo.go:2807-2830`)**:
    - Add helper `apiKeyQuotaClearKeys(extra map[string]any) []string` checking `APIKeyQuotaManagedExtraKeys` (plus `QuotaScriptExtraKey`) for `ok && value == nil`, and `apiKeyQuotaSchedulingClearRequested(extra map[string]any) bool` checking `val, ok := extra[service.APIKeyQuotaExhaustedExtraKey]; ok && val == nil`.
    - Append `- '<key>'` to `extraExpression` for every key returned by `apiKeyQuotaClearKeys(updates.Extra)` (both in `BulkUpdate` and `UpdateExtra`), preventing JSON `null` pollution on any row.
    - In `BulkUpdate`, when `clearAPIKeyQuotaState := apiKeyQuotaSchedulingClearRequested(updates.Extra)` is `true`:
      1. Append conditional SQL `SET` clauses (using zero extra `$N` bind parameters so `argIdx` order is unchanged):
         ```sql
         temp_unschedulable_until = CASE WHEN temp_unschedulable_reason LIKE 'apikey_quota_%' THEN NULL ELSE temp_unschedulable_until END,
         temp_unschedulable_reason = CASE WHEN temp_unschedulable_reason LIKE 'apikey_quota_%' THEN NULL ELSE temp_unschedulable_reason END
         ```
         This atomically unpauses quota-paused API-key accounts while preserving non-quota temporary pauses on any account in a mixed batch (matching `ResetQuotaUsedAndClearRateLimitCooldown` at `account_repo.go:4098-4099`).
      2. Include `clearAPIKeyQuotaState` in `shouldSync` (`account_repo.go:3355`):
         ```go
         shouldSync := updates.ExpiresAt != nil || clearAPIKeyQuotaState
         ```
         so `r.syncSchedulerAccountSnapshots(baseCtx, ids)` immediately updates Redis account snapshots after `tx.Commit()`.

---

## 3. Finding 2 Analysis: Atomic Identity CAS for Stale In-Flight Usage/Quota/Memoization Writes

### 3.1 Complete Inventory of Post-Network Writes

Every asynchronous network/script execution path loads `*Account` at `t0` (via `GetUsage` `:564`, `GetUsageForAccount` `:574`, `GetUsageBatch` `:650` goroutines, or `UpstreamBillingProbeService` `:550-625`), performs a slow network/JS call (up to `upstreamBillingProbeRequestTimeout = 10s`), and then writes back to `AccountRepository`:

| Path | Call Site (`file:line`) | Current Repo Call(s) | Stale Overwrite Risk if Credential / Proxy / `quota_script` Changed in Flight |
| --- | --- | --- | --- |
| **1a. `/v1/usage` 404/405/501 or invalid 2xx** | `fillUpstreamAPIKeyUsage` (`account_upstream_quota.go:279, 294`) -> `memoizeUpstreamProbeUnsupported` (`:206`) | `repo.UpdateExtra(ctx, id, {"apikey_usage_unsupported_identity": identity})` | Overwrites a newly rotated credential's memoization marker (or writes stale marker after rotation). |
| **1b. `/v1/usage` valid 2xx — clear memoization** | `fillUpstreamAPIKeyUsage` (`account_upstream_quota.go:297`) -> `clearUpstreamProbeUnsupported` (`:222`) | `repo.UpdateExtra(ctx, id, {"apikey_usage_unsupported_identity": ""})` | Wipes out `apikey_usage_unsupported_identity` already memoized by the newly rotated credential! |
| **1c. `/v1/usage` valid 2xx — expiry sync** | `fillUpstreamAPIKeyUsage` (`account_upstream_quota.go:298-301`) | `repo.BulkUpdate(ctx, []int64{id}, AccountBulkUpdate{ExpiresAt: remote.ExpiresAt})` | Overwrites the rotated credential's `expires_at` with the old key's upstream expiration (potentially auto-pausing the new key via `AutoPauseOnExpired`)! |
| **1d. `/v1/usage` valid 2xx — quota scheduling sync** | `getUsageForAccount` (`account_usage_service.go:410`) -> `syncAPIKeyQuotaSchedulingState` (`account_upstream_quota.go:416, 431-433, 442`) | `repo.UpdateExtra` + `repo.ClearTempUnschedulable` + `repo.SetTempUnschedulable` | Writes old key's `apikey_quota_exhausted` / window percentages into `extra` AND sets (or clears!) `temp_unschedulable_until`, re-pausing the newly rotated account! Also splits shortening into 2 transactions (`ClearTempUnschedulable` then `SetTempUnschedulable`). |
| **2. `ExecuteQuotaScript` — quota scheduling sync** | `getUsageForAccount` (`account_usage_service.go:384`) -> `syncAPIKeyQuotaSchedulingState` (`account_upstream_quota.go:416, 431-433, 442`) | `repo.UpdateExtra` + `repo.ClearTempUnschedulable` + `repo.SetTempUnschedulable` | Same as 1d; additionally, if admin edited or removed `quota_script` while the old script's `http.request` was in flight, the old script's result clobbers the new script/credential state! |
| **3a. `/v1/sub2api/billing` unsupported / official short-circuit** | `probeLoadedAccount` (`upstream_billing_probe.go:645, 702, 713`) -> `memoizeUpstreamProbeUnsupported` | `persistProbeFailure` (CAS) **followed by separate unguarded** `repo.UpdateExtra` | Although `persistProbeFailure` checks CAS first, a credential rotation occurring right after `persistProbeFailure` commits still gets hit by unguarded `UpdateExtra` (and incurs a redundant 2nd DB tx). |
| **3b. `/v1/sub2api/billing` 200 OK — clear memoization** | `probeLoadedAccount` (`upstream_billing_probe.go:749`) -> `clearUpstreamProbeUnsupported` | `updateSnapshot` (CAS) **followed by separate unguarded** `repo.UpdateExtra` | Same post-`updateSnapshot` race window as 3a. |

### 3.2 Native Precedents in `account_repo.go`

Sub2API uses narrow, fail-closed repository interfaces for every conditional background state write:
1. `upstreamBillingProbeSnapshotWriter` (`upstream_billing_probe.go:164-171`, `account_repo.go:2874-3037`):
   - Runs in a transaction; calls `lockAndMatchProbeProxyIdentity(ctx, client, account)` (`SELECT ... FROM proxies WHERE id = $1 AND deleted_at IS NULL FOR SHARE`) so in-place edits to proxy host/port/auth/status also invalidate in-flight probes.
   - Executes `UPDATE accounts SET ... WHERE id = $2 AND platform = $3 AND type = $4 AND credentials = $5::jsonb AND proxy_id IS NOT DISTINCT FROM $6 ... AND deleted_at IS NULL`.
   - Enqueues `SchedulerOutboxEventAccountChanged` inside the tx and calls `r.syncSchedulerAccountSnapshot(ctx, account.ID)` after commit.
2. `ollamaCloudUsageSnapshotWriter` (`account_repo_ollama_cloud_usage.go:141-258`) and `openCodeGoUsageSnapshotWriter` (`account_repo_opencode_go_usage.go:148-262`):
   - Same narrow-interface pattern; mutates in-memory `account.Extra` **only after** `tx.Commit()` succeeds with `affected > 0`.
3. `grokCredentialStateRepository.SetGrokCredentialTempUnschedulableIfMatch` (`account_repo.go:2552-2598`):
   - Returns `(bool, error)` where `(false, nil)` means CAS mismatch (stale snapshot silently discarded without error).

### 3.3 Recommended Zero-Redundancy Unified CAS Design

Instead of scattering 4 separate CAS methods or modifying `UpdateUpstreamBillingProbeSnapshot` (whose exact SQL and bind args are asserted by upstream `sqlmock` tests in `account_repo_upstream_billing_probe_cas_test.go`), introduce **one** narrow interface and mutation struct in `service` (`account_upstream_quota.go`) and implement it on `*accountRepository` (`account_repo.go`) and `*quotaAccountRepoFixture` (`test_upstream_quota_test.go`):

```go
type APIKeyQuotaTempUnschedAction uint8

const (
	APIKeyQuotaTempUnschedNone APIKeyQuotaTempUnschedAction = iota
	APIKeyQuotaTempUnschedSet
	APIKeyQuotaTempUnschedClear
)

type APIKeyQuotaStateMutation struct {
	ExtraUpdates             map[string]any
	ExpiresAt                *time.Time
	TempUnschedAction        APIKeyQuotaTempUnschedAction
	TempUnschedUntil         *time.Time
	TempUnschedReason        string
	ClearQuotaTempUnschedOnly bool // used by UpdateAccount post-save conditional clear if desired, or keep dedicated helper
}

type apiKeyQuotaStateWriter interface {
	UpdateAPIKeyQuotaState(ctx context.Context, account *Account, mutation APIKeyQuotaStateMutation) (bool, error)
}
```

#### How All Call Sites Collapse Into Single Atomic Mutations

1. **`getUsageForAccount` (`account_usage_service.go:379-412` + `account_upstream_quota.go`)**:
   - **Script branch (`ExecuteQuotaScript`)**:
     - `mutation := buildAPIKeyQuotaSchedulingMutation(account, usage, time.Now().UTC())`
     - Single call: `applyAPIKeyQuotaStateMutation(ctx, s.accountRepo, account, mutation)`
   - **HTTP `/v1/usage` branch (`fillUpstreamAPIKeyUsage` + scheduling sync)**:
     - On 404 / 405 / 501 / invalid 2xx body: `memoizeUpstreamProbeUnsupported(ctx, s.accountRepo, account)` -> builds `APIKeyQuotaStateMutation{ExtraUpdates: map[string]any{APIKeyUsageUnsupportedIdentityExtraKey: identity}}` -> **1 CAS write**.
     - On valid 2xx body:
       - Collect into **one** `APIKeyQuotaStateMutation`:
         1. If `account.Extra[APIKeyUsageUnsupportedIdentityExtraKey]` is non-empty string: `ExtraUpdates[APIKeyUsageUnsupportedIdentityExtraKey] = ""`
         2. If `remote.ExpiresAt != nil && (account.ExpiresAt == nil || !account.ExpiresAt.Equal(*remote.ExpiresAt))`: `mutation.ExpiresAt = remote.ExpiresAt`
         3. Merge `buildAPIKeyQuotaSchedulingMutation(account, usage, time.Now().UTC())` (`ExtraUpdates` for `apikey_quota_*` + `TempUnschedAction` / `TempUnschedUntil` / `TempUnschedReason`)
       - Execute **one** `applyAPIKeyQuotaStateMutation(ctx, s.accountRepo, account, mutation)` call!
       - Result: **1 transaction, 1 `FOR SHARE` proxy check, 1 `UPDATE accounts` CAS statement, at most 1 `scheduler_outbox` insert, and at most 1 `syncSchedulerAccountSnapshot` Redis write**, instead of up to 4 separate non-atomic transactions!
       - If persistence returns an error or `applied == false` (CAS mismatch), `usage` is still returned to the caller (`api-key-quota.md` line 207: *"Expiry persistence fails -> Keep mapped quota output and default-query silence"*), and in-memory `account` is **not** mutated with stale or failed writes!

2. **`UpstreamBillingProbeService.probeLoadedAccount` (`upstream_billing_probe.go:645, 702, 713, 749`)**:
   - Calls the exact same `memoizeUpstreamProbeUnsupported(ctx, s.accountRepo, account)` / `clearUpstreamProbeUnsupported(ctx, s.accountRepo, account)` helpers, which now go through `UpdateAPIKeyQuotaState`!
   - Even if credentials/proxy/script change in the microsecond window after `persistProbeFailure` / `updateSnapshot` commits, `UpdateAPIKeyQuotaState` rejects the stale `apikey_usage_unsupported_identity` write via CAS.

#### Exact SQL CAS & Atomic `SET` Semantics in `(*accountRepository).UpdateAPIKeyQuotaState`

Inside a transaction (`r.client.Tx(ctx)` when `dbent.TxFromContext(ctx) == nil`, matching `UpdateUpstreamBillingProbeSnapshot` at `account_repo.go:2886-2907`):

1. **Proxy identity check**:
   - Call `lockAndMatchProbeProxyIdentity(ctx, client, account)` (`account_repo.go:2995-3037`). If `!proxyMatches`, rollback and return `(false, nil)`.
2. **Account + Credential + Proxy + `quota_script` CAS `WHERE` clause**:
   - Normalize `credentialsMap := account.Credentials; if credentialsMap == nil { credentialsMap = map[string]any{} }` -> `credentialsJSON`.
   - Expected script: `expectedScript := service.AccountQuotaScript(account)` (returns `""` if non-APIKey or `strings.TrimSpace(script) == ""`, else exact `script`).
   - SQL `WHERE`:
     ```sql
     WHERE id = $...
       AND deleted_at IS NULL
       AND platform = $...
       AND type = $...
       AND COALESCE(credentials, '{}'::jsonb) = $...::jsonb
       AND proxy_id IS NOT DISTINCT FROM $...
       AND CASE
             WHEN BTRIM(COALESCE(extra ->> 'quota_script', '')) = '' THEN ''
             ELSE COALESCE(extra ->> 'quota_script', '')
           END = $...
     ```
3. **Atomic `SET` clauses**:
   - `extra`: if `len(mutation.ExtraUpdates) > 0`, `extra = COALESCE(extra, '{}'::jsonb) || $...::jsonb` (note: keep `apikey_usage_unsupported_identity: ""` when clearing so `repo.accounts[recoverID].Extra[APIKeyUsageUnsupportedIdentityExtraKey] == ""` in `test_upstream_quota_test.go:435, 470` continues to match identically across SQL and fixture!).
   - `expires_at`: if `mutation.ExpiresAt != nil`, `expires_at = $...`.
   - `temp_unschedulable_until` & `temp_unschedulable_reason`:
     - When `mutation.TempUnschedAction == APIKeyQuotaTempUnschedSet`:
       ```sql
       temp_unschedulable_until = CASE
           WHEN status = 'active' AND schedulable = TRUE AND (
               temp_unschedulable_until IS NULL
               OR temp_unschedulable_until <= NOW()
               OR COALESCE(temp_unschedulable_reason, '') LIKE 'apikey_quota_%'
           ) THEN $until
           ELSE temp_unschedulable_until
       END,
       temp_unschedulable_reason = CASE
           WHEN status = 'active' AND schedulable = TRUE AND (
               temp_unschedulable_until IS NULL
               OR temp_unschedulable_until <= NOW()
               OR COALESCE(temp_unschedulable_reason, '') LIKE 'apikey_quota_%'
           ) THEN $reason
           ELSE temp_unschedulable_reason
       END
       ```
       *Why this is strictly better than `ClearTempUnschedulable` + `SetTempUnschedulable`*:
       - Shortening an `apikey_quota_%` `reset_at` happens in **one atomic statement** (never briefly making an exhausted account schedulable).
       - If a concurrent non-quota temporary pause (`temp_unschedulable_until > NOW()` with `reason NOT LIKE 'apikey_quota_%'`) or `schedulable = FALSE` / `status != 'active'` landed in DB while the probe was in flight, SQL preserves that non-quota pause instead of overwriting its reason with `'apikey_quota_window_exhausted'`.
     - When `mutation.TempUnschedAction == APIKeyQuotaTempUnschedClear`:
       ```sql
       temp_unschedulable_until = CASE
           WHEN COALESCE(temp_unschedulable_reason, '') LIKE 'apikey_quota_%' THEN NULL
           ELSE temp_unschedulable_until
       END,
       temp_unschedulable_reason = CASE
           WHEN COALESCE(temp_unschedulable_reason, '') LIKE 'apikey_quota_%' THEN NULL
           ELSE temp_unschedulable_reason
       END
       ```
4. **Post-update checks, outbox, Redis sync, and in-memory update**:
   - If `RowsAffected() == 0`: return `(false, nil)` without touching `account` in memory or enqueueing outbox.
   - Check `schedulerChanged := mutation.ExpiresAt != nil || mutation.TempUnschedAction != APIKeyQuotaTempUnschedNone || hasSchedulerOutboxExtraChanges(mutation.ExtraUpdates)` (`account_repo.go:2855` — returns `false` when only `apikey_usage_unsupported_identity` changed!).
   - If `schedulerChanged`: call `enqueueSchedulerOutbox(txCtx, client, service.SchedulerOutboxEventAccountChanged, &account.ID, nil, nil)` before `tx.Commit()`.
   - After `tx.Commit()` succeeds:
     - Apply `mutation` to the caller's in-memory `account` (`Extra`, `ExpiresAt`, `TempUnschedulableUntil`, `TempUnschedulableReason`).
     - If `schedulerChanged && dbent.TxFromContext(ctx) == nil`: call `r.syncSchedulerAccountSnapshot(context.WithoutCancel(ctx), account.ID)`.
   - Return `(true, nil)`.

---

## 4. References & Related Specs

- PostgreSQL `jsonb || jsonb` retains `null`-valued keys; key removal requires `- 'key'` (`account_repo.go:2827, 3220, 4092-4097`).
- Specs: `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/{prd.md,design.md}` and `.trellis/spec/backend/{api-key-quota.md,database-guidelines.md}`.

---

## 6. Critical Caveats & Test Constraints

1. **Do NOT modify `UpdateUpstreamBillingProbeSnapshot`, `lockAndMergeAccountProbeExtra`, or `UpdateCredentials` SQL/args**:
   - `account_repo_upstream_billing_probe_cas_test.go:20-206` asserts exact SQL and positional bind args on `UpdateUpstreamBillingProbeSnapshot`.
   - `account_repo_upstream_billing_probe_update_test.go:82-86` asserts exact 5 bind args and 14 scanned columns on `lockAndMergeAccountProbeExtra`.
   - `account_repo_ollama_cloud_usage_test.go:378` asserts exact `THEN COALESCE(extra, '{}'::jsonb) - 'upstream_billing_probe' - 'ollama_cloud_usage_session' - 'ollama_cloud_usage_auto_refresh' - 'ollama_cloud_usage_snapshot'` in `UpdateCredentials` (which is only called by OAuth refresh / reconciliation paths; admin API-key edits always use `UpdateAccount` or `BulkUpdateAccounts`).
   - `account_repo_upstream_billing_probe_update_test.go:273-275, 288-299` assert exact `sqlmock` queries on `UpdateExtra` and `BulkUpdate` when only `UpstreamBillingProbeExtraKey: nil` is passed. Only append `- 'apikey_quota_...'` / `temp_unschedulable_*` clauses when those keys are requested in `updates.Extra`.
2. **Preserve existing `test_upstream_quota_test.go` fixture expectations (or update cleanly in lockstep)**:
   - In `TestUpstreamQuotaExistingUsageEntryPoints` (`plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go:195-245`):
     - Asserts `require.Equal(t, wantAccount, *repo.accounts[1])` (`:204, 226, 234, 244`) — in-memory `account` / `repo.accounts[1]` must **not** be mutated when `repo.writeErr != nil` (`:237-244`) or when CAS fails!
     - Asserts `repo.bulkUpdates` contains `AccountBulkUpdate{ExpiresAt: &wantExpiry}` (`:205, 210, 227, 235`) and `TestUpstreamProbeMemoizesUnsupportedAndRecoversOnForceOrIdentityChange` asserts `require.Len(t, repo.updates[id], 1)` (`:334, 344, 353`).
     - In `quotaAccountRepoFixture.UpdateAPIKeyQuotaState`: recording `r.updates[account.ID] = append(..., maps.Clone(mutation.ExtraUpdates))` when `len(mutation.ExtraUpdates) > 0` and `r.bulkUpdates = append(r.bulkUpdates, AccountBulkUpdate{ExpiresAt: mutation.ExpiresAt})` when `mutation.ExpiresAt != nil` keeps **100%** of existing assertions green while testing the exact `UpdateAPIKeyQuotaState` CAS path!
   - Also update `quotaAccountRepoFixture.BulkUpdate` (`test_upstream_quota_test.go:110-123`) to apply `Credentials`, `ProxyID`, `Extra` (deleting `nil`-valued keys), and conditional `apikey_quota_` `TempUnschedulableUntil` clearing on `r.accounts[id]` so bulk reset + mixed-batch non-quota pause preservation can be unit-tested end-to-end through `adminServiceImpl.BulkUpdateAccounts`.
3. **Fail-closed behavior when `repo` does not implement `apiKeyQuotaStateWriter`**:
   - Match `upstreamBillingProbeSnapshotWriter` / `ollamaCloudUsageSnapshotWriter` / `grokCredentialStateRepository`: if `s.accountRepo` does not implement `apiKeyQuotaStateWriter` (e.g., raw `upstreamBillingProbeAccountRepo` in `TestQuotaScriptStorageAndDispatch` at `test_quota_script_test.go:152` or `upstream_billing_probe_test.go:600`), do **not** fall back to unguarded `UpdateExtra` / `BulkUpdate` / `SetTempUnschedulable`. Returning `(false, nil)` keeps `TestUpstreamBillingProbeDiscardsResultWhenIdentityChangesInFlight` (`upstream_billing_probe_test.go:600`) and `TestQuotaScriptStorageAndDispatch` (`test_quota_script_test.go:152`, which performs no scheduling/expiry writes anyway) completely safe and race-free.
