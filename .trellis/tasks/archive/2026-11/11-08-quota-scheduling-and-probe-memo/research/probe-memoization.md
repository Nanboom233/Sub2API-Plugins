# Probe Memoization & Upstream Billing Probe Research

- **Task**: `.trellis/tasks/11-08-quota-scheduling-and-probe-memo`
- **Date**: 2026-11-09
- **Scope**: Read-only investigation of `/v1/usage` and native `/v1/sub2api/billing` (`UpstreamBillingProbeService`) probing & memoization in `plugins/sub2api-quota-extension/patches/quota-extension.patch`, Sub2API `v0.2.20` capability memoization (`UpstreamBillingProbeService`, `ProbeOpenAIAPIKeyResponsesSupport`), and existing test fixtures.

---

## Files Found

- `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe.go`: Native Sub2API `/v1/sub2api/billing` periodic & manual probe service (`UpstreamBillingProbeService`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe_test.go`: Unit tests and in-memory `upstreamBillingProbeAccountRepo` / `httpUpstreamRecorder` test doubles for `UpstreamBillingProbeService`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe_multiplatform_test.go`: Multi-platform eligibility and official domain short-circuit tests for `UpstreamBillingProbeService`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/admin_account.go`: Account CRUD, `BulkUpdateAccounts`, `DuplicateAccount`, and probe `Extra` key management/sanitization.
- `/tmp/sub2api-v0.2.20-base/backend/internal/service/admin_account_upstream_billing_probe_test.go`: Unit tests for `adminServiceImpl` handling of `upstream_billing_probe*` keys on create/update/bulk-update.
- `/tmp/sub2api-v0.2.20-base/backend/internal/handler/admin/account_upstream_billing_probe.go`: Admin HTTP handlers for settings, single-account manual probe (`POST /api/v1/admin/accounts/:id/upstream-billing-probe`), and batch manual probe (`POST /api/v1/admin/accounts/upstream-billing-probe/batch`).
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo.go`: `schedulerNeutralExtraKeys`, `lockAndMergeAccountProbeExtra`, `UpdateUpstreamBillingProbeSnapshot` (CAS), and `ListDueUpstreamBillingProbeAccounts`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo_upstream_billing_probe_due_test.go`: `sqlmock` test asserting the exact SQL query of `ListDueUpstreamBillingProbeAccounts`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo_upstream_billing_probe_update_test.go`: `sqlmock` tests asserting exact SQL queries and JSON payloads for `lockAndMergeAccountProbeExtra`, `UpdateExtra`, `BulkUpdate`, and `UpdateCredentials`.
- `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo_upstream_billing_probe_cas_test.go`: `sqlmock` tests for `UpdateUpstreamBillingProbeSnapshot` CAS semantics.
- `/tmp/sub2api-v0.2.20-base/backend/internal/handler/dto/mappers.go`: `redactAccountManagedExtra` and `extractUpstreamBillingProbeSummary` for admin DTO serialization.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch`: Current plugin patch adding `/v1/usage` quota synchronization, `quota_script` execution, and `/v1/usage` unsupported memoization.
- `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go`: Plugin unit test suite for quota syncing, scheduling guards, and probe memoization.

---

## 1. Current `/v1/usage` Probing in `quota-extension.patch`

1. **Entry Points**:
   - `GET /api/v1/admin/accounts/:id/usage` -> `AccountHandler.GetUsage` (`account_handler.go:2556-2578`) -> `AccountUsageService.GetUsage(ctx, accountID, force)` (`account_usage_service.go:517-525`) -> `getUsageForAccount(ctx, account, forceProbe)`.
   - `POST /api/v1/admin/accounts/usage/batch` -> `AccountHandler.GetBatchUsage` (`account_handler.go:2746-2772`) -> `AccountUsageService.GetUsageBatch(ctx, accountIDs, req.Force)` (`account_usage_service.go:538-625`, up to 6 concurrent goroutines) -> `getUsageForAccount(gctx, account, force)`.
   - `ChannelMonitorQuotaFetcher.Fetch` -> `AccountUsageService.GetUsageForAccount(ctx, account)` (`channel_monitor_quota_fetcher.go:236`).
   - `POST /api/v1/admin/accounts/quota-script/test` -> `AccountHandler.TestQuotaScript` (`account_quota_script_handler.go:100-180`) -> `AccountUsageService.ExecuteQuotaScript(ctx, account, request.Script)` (direct draft test, does not call `getUsageForAccount`).
2. **Dispatch in `AccountUsageService.getUsageForAccount` (`account_usage_service.go:376-412`)**:
   - Checks `scopedAccountAccess(ctx, s.accountRepo, account, "accounts.usage.read", true)`.
   - If `script := AccountQuotaScript(account); script != ""` (`account.Type == AccountTypeAPIKey` and non-blank `account.Extra["quota_script"]`): runs `s.ExecuteQuotaScript(ctx, account, script)`; does **not** fall back to `/v1/usage`.
   - If `account == nil || !IsUpstreamBillingProbeIdentity(account.Platform, account.Type) || account.GetCredential("base_url") == ""`: delegates to `s.getNativeUsageForAccount(ctx, account, forceProbe)`.
   - Resolves `baseURL := account.GetCredential("base_url")` (or `account.GetCNProtocolBaseURL(APIProtocolChatCompletions)` when `account.RoutesProtocolByInbound() && account.IsAdaptiveAPIProtocol()`).
   - Skips official domains (`upstreamBillingProbeTargetIsOfficialAPI(baseURL)`).
   - Calls `s.fillUpstreamAPIKeyUsage(ctx, account, baseURL, usage)` (`account_upstream_quota.go:139-218`).
3. **HTTP Request & Error Handling in `fillUpstreamAPIKeyUsage`**:
   - Sends `GET` to `buildOpenAIEndpointURL(baseURL, "/v1/usage")` with 10s timeout (`upstreamBillingProbeRequestTimeout`), redirects disabled, `Accept: application/json`, `Authorization: Bearer <apiKey>`, and `account.ApplyHeaderOverrides(req.Header)`.
   - Reads up to `upstreamBillingProbeMaxBodyBytes + 1` (64 KiB + 1 byte).
   - Memoizes definitive unsupported responses (`404`, `405`, `501`, or `2xx` `<= 64 KiB` that fails `parseUpstreamQuota`) under `APIKeyUsageUnsupportedIdentityExtraKey = "apikey_usage_unsupported_identity"`.

---

## 2. Existing Memoization Mechanisms in Sub2API `v0.2.20`

1. **`ProbeOpenAIAPIKeyResponsesSupport` (`backend/internal/service/openai_apikey_responses_probe.go:107-364`)**:
   - Stores `accounts.extra["openai_responses_supported"] = false` via `accountRepo.UpdateExtra` when upstream returns `404 Not Found` or `405 Method Not Allowed`, or `2xx` with a body that conclusively lacks the required capability.
   - Does **not** persist `false` on transient errors (`err != nil`, body read error/timeout, `401`/`403`, `429`, or `5xx`).
2. **How `admin_account.go`, `account_repo.go`, and `dto/mappers.go` Manage Persisted Probe State**:
   - In `admin_account.go:694-716`, `UpdateAccount` copies managed keys from `account.Extra` into `normalizedExtra`, and deletes probe keys when probe identity changes (`admin_account.go:780-786`).
   - In `BulkUpdateAccounts` (`admin_account.go:964-975`, `1137-1144`), managed keys are stripped from `input.Extra`, and cleared when credentials or `proxy_id` change.
   - In `DuplicateAccount` (`admin_account.go:100-156`), `duplicateAccountDiscardedExtraKeys` strips probe/observation keys so duplicated accounts start fresh.
   - In `dto/mappers.go:418-436`, `redactAccountManagedExtra` strips internal snapshots from `dto.Account.Extra`.
   - In `account_repo.go:55-73`, `schedulerNeutralExtraKeys` avoids enqueuing scheduler outbox events when non-scheduling probe metadata is updated via `UpdateExtra`.

---

## 3. Conditions for Persisting, Bypassing, and Clearing Memoized `/v1/usage` Unsupported State

1. **Definitive "Unsupported" vs "Transient Failure"**:
   - **Definitive "Unsupported" (memoize)**:
     - HTTP `404 Not Found`, `405 Method Not Allowed`, or `501 Not Implemented`; OR
     - HTTP `2xx` where the response body is read completely (`<= 64 KiB`, no read/timeout error) and `parseUpstreamQuota(body, now)` fails (e.g., HTML `200 OK`, empty `{}`, or non-Sub2API JSON like `{"balance": 999}`).
   - **Transient / Auth / Transport Failures (do NOT memoize)**:
     - Transport/network errors (`err != nil`), timeouts (`context.DeadlineExceeded`), body read errors (`io.ReadAll` error), or body `> 64 KiB`.
     - HTTP `401 Unauthorized`, `403 Forbidden`, `429 Too Many Requests`, or `5xx` (`500`, `502`, `503`, `504`).
2. **Identity Fingerprinting**:
   - Store a deterministic SHA-256 fingerprint of (`platform`, `type`, effective `baseURL`, `api_key`, `proxy_id`, `header_override_enabled`, `header_overrides`, `quota_script`) under `account.Extra["apikey_usage_unsupported_identity"]`.
   - Comparing the current account's probe identity fingerprint against the stored fingerprint automatically invalidates stale memoization whenever any credential, `base_url`, `proxy_id`, header override, or `quota_script` changes — both in production and in unit test fixtures.

---

## 4. Existing Test Fixtures & Caveats (`upstreamBillingProbeAccountRepo`)

- In `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe_test.go:21-148`, `upstreamBillingProbeAccountRepo` embeds the `AccountRepository` interface and only implements `Create`, `Update`, `BulkUpdate`, `GetByID`, `GetByIDs`, `UpdateExtra`, `UpdateUpstreamBillingProbeSnapshot`, and `FindByExtraField`.
- Calling unimplemented methods such as `SetTempUnschedulable` / `ClearTempUnschedulable` directly on an `upstreamBillingProbeAccountRepo` stub would panic in unit tests unless `BulkUpdate` / `UpdateExtra` is used or guarded.
- In `test_upstream_quota_test.go:177-178` and `199-200`, `TestUpstreamQuotaExistingUsageEntryPoints` checks `require.Equal(t, wantAccount, *repo.accounts[1])` and `require.Equal(t, []AccountBulkUpdate{{ExpiresAt: &wantExpiry}}, repo.bulkUpdates)` for `Account 1` (which returns `remaining: 25`, i.e., supported and non-exhausted with no windows). Therefore, for a supported, non-exhausted account with no windows and unchanged expiry, no extra `BulkUpdate` or `account[1]` mutation should occur.

---

## 5. Native `/v1/sub2api/billing` Probe Memoization (`阻断原生 /v1/sub2api/billing 探测`)

### 5.1 Entry Points & Call Graph in `UpstreamBillingProbeService` (`/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe.go`)

1. **Constants & Extra Keys (`upstream_billing_probe.go:31-53, 93-97`)**:
   - `UpstreamBillingProbeExtraKey = "upstream_billing_probe"` (stores `*UpstreamBillingProbeSnapshot` JSON object in `accounts.extra`)
   - `UpstreamBillingProbeEnabledExtraKey = "upstream_billing_probe_enabled"` (`bool`, defaults to `true` when creating an API Key account in `CreateAccountModal.vue:5658`)
   - `UpstreamBillingRateSyncEnabledExtraKey = "upstream_billing_rate_sync_enabled"` (`bool`)
   - Statuses: `UpstreamBillingProbeStatusOK = "ok"`, `UpstreamBillingProbeStatusUnsupported = "unsupported"`, `UpstreamBillingProbeStatusFailed = "failed"`.
   - Timing / sizing constants: `upstreamBillingProbeDefaultIntervalMinutes = 30` (`5..1440`), `upstreamBillingProbeCycleInterval = 1m`, `upstreamBillingProbeRequestTimeout = 10s`, `upstreamBillingProbeMaxBodyBytes = 64 KiB`, `upstreamBillingProbeMaxPerCycle = 20`, `upstreamBillingProbeConcurrency = 4`, `upstreamBillingProbeMaxDelay = 24h`, `upstreamBillingProbeUnsupportedDelayFactor = 8`.

2. **Background Runner Entry Point (`ProvideUpstreamBillingProbeService` -> `Start` -> `runLoop` -> `RunDue`)**:
   - `ProvideUpstreamBillingProbeService` (`upstream_billing_probe.go:296-307`) calls `svc.Start()` (`309-322`), which spawns `runLoop(ctx)` (`339-354`, 1m ticker calling `s.RunDue(ctx)`).
   - `RunDue(ctx)` (`upstream_billing_probe.go:357-438`):
     - Exits if `!settings.Enabled` (`364-370`); acquires distributed leader and cadence locks (`371-388`).
     - Calls `s.listDueAccounts(ctx, now)` (`440-447`) -> `accountRepo.ListDueUpstreamBillingProbeAccounts` (`account_repo.go:3814-3913`) or `FindByExtraField(ctx, UpstreamBillingProbeEnabledExtraKey, true)`.
     - Loops over returned accounts (`396-406`): requires `isUpstreamBillingProbeAccount(&account) && account.IsActive() && upstreamBillingProbeEnabled(&account)` and skips if `now.Before(snapshot.NextProbeAt)` (`401-403`).
     - Sorts due accounts by `NextProbeAt` (unset first), caps at `upstreamBillingProbeMaxPerCycle` (`20`), and spawns `s.probeScheduledAccount` (`427-435`) -> `s.probeAccountWithMode(ctx, accountID, intervalMinutes, true)` (`483-485`).

3. **Manual & Post-Creation Entry Points (`ProbeAccount` / `ProbeAccounts`)**:
   - `POST /api/v1/admin/accounts/:id/upstream-billing-probe` -> `AccountHandler.ProbeUpstreamBilling` (`handler/admin/account_upstream_billing_probe.go:76-94`) -> `s.ProbeAccount(ctx, accountID)` (`upstream_billing_probe.go:468-477`) -> `s.probeAccount(ctx, accountID, settings.IntervalMinutes)` (`479-481`) -> `s.probeAccountWithMode(ctx, accountID, intervalMinutes, false)`.
   - `POST /api/v1/admin/accounts/upstream-billing-probe/batch` -> `AccountHandler.ProbeUpstreamBillingBatch` (`handler/admin/account_upstream_billing_probe.go:97-122`) -> `s.ProbeAccounts(ctx, accountIDs)` (`upstream_billing_probe.go:528-562`) -> concurrently calls `s.probeAccount(ctx, accountID, settings.IntervalMinutes)` (`550`).
   - Note: `CreateAccountModal.vue:5598-5601` automatically invokes `adminAPI.accounts.probeUpstreamBilling(account.id)` immediately after creating an API Key account if `upstream_billing_probe_enabled === true`.

4. **Shared Execution Path (`probeAccountWithMode` -> `probeLoadedAccount` -> `parseUpstreamBillingProbeResponse` / `persistProbeFailure`)**:
   - `probeAccountWithMode(ctx, accountID, intervalMinutes, requireEnabled)` (`upstream_billing_probe.go:487-525`):
     - Deduplicates concurrent probes for the same `accountID` via `s.probeGroup.Do(key, ...)` (`singleflight.Group`) and acquires a slot from `s.probeSlots` (`489-495`).
     - Loads `account, loadErr := s.accountRepo.GetByID(ctx, accountID)` (`496-499`).
     - Validates `isUpstreamBillingProbeAccount(account)` (`500-502`).
     - If `requireEnabled` is `true` (scheduled background probe): re-checks `account.IsActive() && upstreamBillingProbeEnabled(account)` and `snapshot.NextProbeAt` (`503-511`).
     - Calls `s.probeLoadedAccount(ctx, account, intervalMinutes)` (`512`).
   - `probeLoadedAccount(ctx, account, intervalMinutes)` (`upstream_billing_probe.go:618-748`):
     - Checks `s.accountTestService == nil || s.accountTestService.httpUpstream == nil` -> `persistProbeFailure(..., 0, "transport_unavailable", 0)` (`620-622`).
     - Reads `apiKey := strings.TrimSpace(account.GetCredential("api_key"))`; if empty -> `persistProbeFailure(..., 0, "missing_api_key", 0)` (`625-628`).
     - Resolves `baseURL := strings.TrimSpace(account.GetCredential("base_url"))` (or `account.GetCNProtocolBaseURL(APIProtocolChatCompletions)` when `account.RoutesProtocolByInbound() && account.IsAdaptiveAPIProtocol()`) (`629-632`).
     - Official API domain check (`633-644`):
       - If `account.Platform == PlatformOpenAI && baseURL == ""`: sets `baseURL = "https://api.openai.com"`.
       - Else if `account.Platform != PlatformOpenAI && upstreamBillingProbeTargetIsOfficialAPI(baseURL)`: short-circuits **without making an HTTP request** and returns `s.persistProbeFailure(ctx, account, intervalMinutes, now, 0, "unsupported", 0)` (`638-644`).
     - Validates `normalizedBaseURL, err := s.accountTestService.validateUpstreamBaseURL(baseURL)` (`645-648`).
     - Resolves `proxyURL, err := s.resolveProxyURL(ctx, account)` (`649-658`).
     - Builds `GET` request to `buildOpenAIEndpointURL(normalizedBaseURL, "/v1/sub2api/billing")` (`659-679`), applies `Authorization: Bearer <apiKey>` and `account.ApplyHeaderOverrides(req.Header)`, and calls `s.accountTestService.httpUpstream.DoWithTLS(...)` (`680`).
     - Reads up to `upstreamBillingProbeMaxBodyBytes + 1` (64 KiB + 1 byte) (`688`).
     - Parses `retryAfterDuration := parseRetryAfterDuration(resp.Header.Get("Retry-After"), now)` (`694`).
     - Classifies HTTP status & body (`695-705`):
       - `resp.StatusCode == http.StatusNotFound (404) || resp.StatusCode == http.StatusMethodNotAllowed (405)` -> `s.persistProbeFailure(ctx, account, intervalMinutes, now, resp.StatusCode, "unsupported", retryAfterDuration)` (`695-697`).
       - `resp.StatusCode < 200 || resp.StatusCode >= 300` -> `s.persistProbeFailure(ctx, account, intervalMinutes, now, resp.StatusCode, "http_error", retryAfterDuration)` (`698-700`).
       - `parseUpstreamBillingProbeResponse(body)` (`805-883`): requires strict JSON matching `object == "sub2api.key_billing"`, `schema_version == 1`, `billing_scope == "token"`, valid `group_multiplier`, `effective_multiplier`, and optional `peak` config. If parsing fails -> `s.persistProbeFailure(ctx, account, intervalMinutes, now, resp.StatusCode, "invalid_response", retryAfterDuration)` (`701-705`).
       - On success (`706-747`): resets `FailureCount = 0`, sets `Status = UpstreamBillingProbeStatusOK`, `NextProbeAt = now.Add(nextProbeDelay(intervalMinutes, 0, 0))`, syncs `rate_multiplier` if `upstreamBillingRateSyncEnabled(account)` is true, and persists via `s.updateSnapshot(ctx, account, snapshot, rateMultiplier)` (`739`).
   - `persistProbeFailure(ctx, account, intervalMinutes, now, statusCode, reason, retryAfterDuration)` (`upstream_billing_probe.go:750-790`):
     - Increments `failureCount := previous.FailureCount + 1`.
     - Sets `status := UpstreamBillingProbeStatusFailed`, or `UpstreamBillingProbeStatusUnsupported` if `reason == "unsupported"` (`762-765`).
     - Sets `NextProbeAt`:
       - If `status == UpstreamBillingProbeStatusUnsupported`: `now.Add(unsupportedProbeDelay(intervalMinutes, retryAfterDuration))` (`767-768`), which is `8 * intervalMinutes` (e.g. `240m` for `30m` interval, or `40m` for `5m` interval) with `±20%` jitter, capped at `24h` (`1136-1146`).
       - Otherwise (`status == UpstreamBillingProbeStatusFailed`): `now.Add(nextProbeDelay(intervalMinutes, failureCount, retryAfterDuration))` (`769-773`), which starts at `1x intervalMinutes` (e.g. `5m` or `30m`) with exponential backoff up to `24h`.
     - Calls `s.updateSnapshot(ctx, account, snapshot, nil)` (`783`).

---

### 5.2 Why Native `v0.2.20` Continues Probing Non-Sub2API Upstreams

1. **`404` / `405` are only delayed, never stopped**:
   - When an upstream returns `404` or `405`, `persistProbeFailure` sets `Status = "unsupported"` and `NextProbeAt = now + 8 * interval` (40m to 4h, max 24h).
   - Once `NextProbeAt <= now`, `ListDueUpstreamBillingProbeAccounts` (`account_repo.go:3864-3868`) selects the account again (`parsed_next_probe_at <= $1`), and `RunDue` sends another `GET /v1/sub2api/billing` request indefinitely!
2. **`501 Not Implemented` and non-Sub2API `2xx` responses are treated as `"failed"` instead of `"unsupported"`**:
   - Many NewAPI / OneAPI / reverse-proxy upstreams return `501 Not Implemented` or `200 OK` (with an HTML SPA fallback page, `{"error": ...}`, or non-Sub2API JSON) for unknown `/v1/sub2api/billing` paths.
   - Native `probeLoadedAccount` (`698-705`) classifies `501` as `"http_error"` (`Status: "failed"`) and non-Sub2API `2xx` as `"invalid_response"` (`Status: "failed"`), scheduling the next probe after just `1x intervalMinutes` (5–30 minutes)!
3. **Manual / Batch probes (`ProbeAccount` / `ProbeAccounts`) always hit the network**:
   - Every call to `ProbeAccount` or `ProbeAccounts` ignores `NextProbeAt` and sends a live HTTP request to `/v1/sub2api/billing`.

---

### 5.3 Definitive Unsupported vs Transient Failure Criteria for `GET /v1/sub2api/billing`

1. **Definitive "Unsupported" (should record `reason = "unsupported"`, `Status = UpstreamBillingProbeStatusUnsupported`, and memoize unsupported identity)**:
   - Non-OpenAI official API domain short-circuit (`account.Platform != PlatformOpenAI && upstreamBillingProbeTargetIsOfficialAPI(baseURL)` at `upstream_billing_probe.go:638`).
   - HTTP `404 Not Found`, `405 Method Not Allowed`, or `501 Not Implemented`.
   - HTTP `2xx` (`200 <= resp.StatusCode < 300`) where the body is read completely (`readErr == nil && len(body) <= upstreamBillingProbeMaxBodyBytes`) and `parseUpstreamBillingProbeResponse(body)` returns an error (e.g., HTML page, empty JSON `{}`, or JSON missing `"object": "sub2api.key_billing"`).
     - *Verification against existing tests*: In `upstream_billing_probe_test.go`, `parseUpstreamBillingProbeResponse` unit tests (`lines 586-700`) call `parseUpstreamBillingProbeResponse` directly; `TestUpstreamBillingProbeEmptyResponseIsPersistedAsFailure` (`lines 838-864`) tests `resp == nil` (`"empty_response"` at line `684`). **No existing test in `upstream_billing_probe_test.go` asserts `LastError == "invalid_response"` or `Status == "failed"` for a `2xx` `ProbeAccount` call.**
2. **Transient / Auth / Transport / Config Failures (do NOT memoize as unsupported; keep `Status = UpstreamBillingProbeStatusFailed`)**:
   - Pre-request errors: `transport_unavailable`, `missing_api_key`, `invalid_base_url`, `proxy_unavailable`, `request_build_failed`.
   - Network / read errors: `request_failed` (`err != nil`), `empty_response` (`resp == nil || resp.Body == nil`), `response_read_failed` (`readErr != nil`), `response_too_large` (`len(body) > 64 KiB`).
   - HTTP `401 Unauthorized`, `403 Forbidden`, `408 Request Timeout`, `429 Too Many Requests`, or `5xx` (`500`, `502`, `503`, `504`, etc., excluding `501`).

---

### 5.4 Shared Unsupported Key & Unified Identity Fingerprinting (`APIKeyUsageUnsupportedIdentityExtraKey`)

1. **Single Shared Extra Key (`APIKeyUsageUnsupportedIdentityExtraKey = "apikey_usage_unsupported_identity"`)**:
   - Both `/v1/usage` and `/v1/sub2api/billing` are Sub2API-specific upstream endpoints. Sharing `APIKeyUsageUnsupportedIdentityExtraKey = "apikey_usage_unsupported_identity"` means that as soon as **either** `/v1/usage` **or** `/v1/sub2api/billing` returns a definitive unsupported response (`404`, `405`, `501`, non-OpenAI official domain, or non-conforming `2xx` body `<= 64 KiB`), **both** endpoints are immediately memoized as unsupported and blocked from making further HTTP requests!
2. **How `upstreamAPIKeyUsageProbeIdentity(account, baseURL)` Is Computed**:
   - Resolves `resolvedBaseURL` identically across both `AccountUsageService` and `UpstreamBillingProbeService` (`strings.TrimSpace(baseURL)`, falling back to `account.GetCredential("base_url")` or `account.GetCNProtocolBaseURL(APIProtocolChatCompletions)`, and `"https://api.openai.com"` when `account.Platform == PlatformOpenAI && resolvedBaseURL == ""`).
   - Computes a deterministic SHA-256 hex fingerprint over `platform`, `type`, `buildOpenAIEndpointURL(resolvedBaseURL, "/v1/usage")`, `api_key`, `proxy_id` (without `ProxyURL`, so preloaded vs nil `account.Proxy` produces the same hash), `header_override_enabled`, canonical JSON of `header_overrides`, and `AccountQuotaScript(account)`.
   - Changing `base_url`, `api_key`, `proxy_id`, `platform`, `type`, `header_overrides`, or `quota_script` automatically produces a new fingerprint and invalidates the memoized unsupported state for both endpoints!
   - When `fillUpstreamAPIKeyUsage` or `probeLoadedAccount` succeeds (`2xx` with valid schema), if `account.Extra` previously had `APIKeyUsageUnsupportedIdentityExtraKey`, clear it via `clearAPIKeyUsageUnsupported(ctx, accountRepo, account)`.

---

### 5.5 Short-Circuit Behavior & 100% Compatibility with Existing Upstream Tests

1. **Critical Upstream Test Constraints in `upstream_billing_probe_test.go`**:
   - **`TestUpstreamBillingProbeUnsupportedBackoffDefersRunnerButNotManualProbe` (`upstream_billing_probe_test.go:794-836`)**:
     - Account 31 (`PlatformAnthropic`, `base_url: "https://ollama.com/v1"`) runs `svc.RunDue(ctx)` -> gets `first.Status == "unsupported"`, `first.LastAttemptAt == start`, `FailureCount == 1`.
     - Advances clock by `90m`, runs `svc.RunDue(ctx)` -> asserts `deferred.LastAttemptAt == first.LastAttemptAt`.
     - Then calls `manual, err := svc.ProbeAccount(context.Background(), account.ID)` -> asserts:
       - `manual.Status == UpstreamBillingProbeStatusUnsupported`
       - `manual.LastAttemptAt == now`
       - `manual.FailureCount == 2`
   - **`TestUpstreamBillingProbeUnsupportedAndAccountToggle` (`upstream_billing_probe_test.go:866-909`)**:
     - Account 19 (`PlatformOpenAI`, `base_url: "https://upstream.example"`) configures `upstream := &httpUpstreamRecorder{resp: &http.Response{StatusCode: http.StatusNotFound, Header: http.Header{}, Body: io.NopCloser(strings.NewReader("not found"))}}`.
     - Calls `snapshot, err := svc.ProbeAccount(context.Background(), account.ID)` (1st call) -> asserts `snapshot.Status == "unsupported"`, `snapshot.LastError == "unsupported"`, `NextProbeAt` in `[192m, 288m]`.
     - Immediately calls `snapshot, err = svc.ProbeAccount(context.Background(), account.ID)` (2nd call on the same account!) -> asserts:
       - `require.NoError(t, err)`
       - `require.Equal(t, 2, snapshot.FailureCount)`!
   - **`sqlmock` Repository Tests (`account_repo_upstream_billing_probe_*_test.go`)**:
     - `TestAccountRepositoryListDueUpstreamBillingProbeAccountsBoundsQuery` (`account_repo_upstream_billing_probe_due_test.go:12-41`) asserts the exact SQL string of `ListDueUpstreamBillingProbeAccounts`.
     - `TestLockAndMergeAccountProbeExtraUsesCurrentDatabaseSnapshot` (`account_repo_upstream_billing_probe_update_test.go:82-85`) and `TestBulkUpdateDisablingProbeRemovesSnapshot` (`line 314`) assert exact SQL queries and JSON payloads in `account_repo.go`.
     - Therefore, **do not alter the SQL query text in `ListDueUpstreamBillingProbeAccounts` or `lockAndMergeAccountProbeExtra`**.

2. **How to Short-Circuit Scheduled Probes in `UpstreamBillingProbeService` Without Blocking Manual Probes**:
   - **In `RunDue(ctx)` (`upstream_billing_probe.go:396-406`) and `probeAccountWithMode(ctx, accountID, intervalMinutes, requireEnabled)` (`503-511`)**:
     - When `requireEnabled == true` (scheduled background probe): check `isAPIKeyUsageUnsupportedMemoized(account, "")`.
     - If `true`, skip the account immediately in `RunDue` (so it never consumes one of the 20 `upstreamBillingProbeMaxPerCycle` slots or spawns a goroutine) and return `decodeUpstreamBillingProbeSnapshot(account.Extra), nil` in `probeAccountWithMode`.
     - Result: Background runner (`RunDue`) **never** re-probes a memoized unsupported account even after `NextProbeAt` (4h–24h) expires!
   - **In `probeLoadedAccount(ctx, account, intervalMinutes)` (`upstream_billing_probe.go:633-747`)**:
     - Do **not** short-circuit on `isAPIKeyUsageUnsupportedMemoized` inside `probeLoadedAccount`, because `probeLoadedAccount` is called by manual `ProbeAccount` / `ProbeAccounts` (`requireEnabled == false`), and manual probes must remain unblocked!
     - When a definitive unsupported condition occurs in `probeLoadedAccount` (non-OpenAI official domain at line `638`, HTTP `404`/`405`/`501`, or HTTP `2xx` `<= 64 KiB` failing `parseUpstreamBillingProbeResponse`), call `s.persistProbeFailure(..., "unsupported", retryAfterDuration)` first, and then persist `APIKeyUsageUnsupportedIdentityExtraKey: upstreamAPIKeyUsageProbeIdentity(account, baseURL)` via `memoizeAPIKeyUsageUnsupported(ctx, s.accountRepo, account, ...)` (using `s.accountRepo.UpdateExtra`).
     - When `probeLoadedAccount` succeeds (`2xx` with valid `sub2api.key_billing` payload at lines `706-747`), call `clearAPIKeyUsageUnsupported(ctx, s.accountRepo, account)` after `s.updateSnapshot`.
     - Calling `UpdateExtra` **after** `persistProbeFailure` (which calls `UpdateUpstreamBillingProbeSnapshot`) guarantees that `UpdateUpstreamBillingProbeSnapshot`'s CAS check (`COALESCE(extra -> 'upstream_billing_probe', 'null'::jsonb) = $7::jsonb`) and all existing upstream tests (`TestUpstreamBillingProbeUnsupportedBackoffDefersRunnerButNotManualProbe`, `TestUpstreamBillingProbeUnsupportedAndAccountToggle`) pass 100% unmodified.

---

### 5.6 Integration with `account_repo.go`, `dto/mappers.go`, and `admin_account.go`

1. **`APIKeyQuotaManagedExtraKeys` (`account_upstream_quota.go`)**:
   - Include `UpstreamBillingUnsupportedIdentityExtraKey` (`"upstream_billing_unsupported_identity"`) alongside `APIKeyUsageUnsupportedIdentityExtraKey` (`"apikey_usage_unsupported_identity"`) in `APIKeyQuotaManagedExtraKeys()`.
   - Because `admin_account.go`, `account_repo.go`, and `dto/mappers.go` in `quota-extension.patch` already iterate over `service.APIKeyQuotaManagedExtraKeys()` (or `APIKeyQuotaManagedExtraKeys()`):
     - **`schedulerNeutralExtraKeys` & `isAPIKeyUsageInternalExtraUpdates` (`account_repo.go:55-82`)**: Add `"upstream_billing_unsupported_identity": {}` to `schedulerNeutralExtraKeys` and allow `UpstreamBillingUnsupportedIdentityExtraKey` in `isAPIKeyUsageInternalExtraUpdates` so `UpdateExtra` does not trigger unnecessary scheduler outbox rebuilds or touch `updated_at`.
     - **`redactAccountManagedExtra` (`dto/mappers.go:418-436`)**: Automatically strips `UpstreamBillingUnsupportedIdentityExtraKey` from admin API responses because it loops over `service.APIKeyQuotaManagedExtraKeys()`.
     - **`CreateAccount` / `UpdateAccount` / `UpdateAccountExtra` / `BulkUpdateAccounts` / `DuplicateAccount` (`admin_account.go`)**:
       - Stripped from untrusted client `Extra` payloads on `CreateAccount`, `UpdateAccount`, `UpdateAccountExtra`, and `BulkUpdateAccounts`.
       - Preserved across `UpdateAccount` when probe identity does not change, and deleted when `probeIdentityChanged` (`platform`, `type`, `base_url`, `api_key`, `proxy_id`, `header_overrides`) is true (`admin_account.go:780-790`).
       - Cleared in `BulkUpdateAccounts` when `credentials` or `proxy_id` are bulk-updated (`admin_account.go:1137-1149`).
       - Stripped in `DuplicateAccount` via `duplicateAccountDiscardedExtraKeys` (`admin_account.go:100-112`).

---

## 6. Caveats & Verification Notes

- **Do not modify SQL strings in `account_repo.go` tested by `sqlmock`**:
  - `account_repo_upstream_billing_probe_due_test.go` and `account_repo_upstream_billing_probe_update_test.go` use `sqlmock` regex/exact matching on `ListDueUpstreamBillingProbeAccounts` and `lockAndMergeAccountProbeExtra`. Filtering memoized accounts in Go inside `RunDue` / `probeAccountWithMode` / `probeLoadedAccount` and clearing `UpstreamBillingUnsupportedIdentityExtraKey` in `admin_account.go` (plus fingerprint comparison in Go) requires **zero changes** to those SQL queries and keeps all `internal/repository` tests green.
- **Order of persistence in `probeLoadedAccount`**:
  - Always run `s.persistProbeFailure(...)` before `s.memoizeUpstreamBillingUnsupported(ctx, account, baseURL)` so that `UpdateUpstreamBillingProbeSnapshot` completes before `UpdateExtra` mutates `account.Extra`.
