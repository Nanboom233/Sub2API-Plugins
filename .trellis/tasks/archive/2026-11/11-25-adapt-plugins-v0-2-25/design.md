# Sub2API v0.2.25 Adaptation & Simplification Technical Design

Target: upstream `Wei-Shaw/sub2api` `v0.2.25` (tag `8fab111f92447a3edbcdf67a517e45b6a3cc4d31`, commit `348997267d756eab5729bb6b78a275a15d18796a`).
References: [prd.md](prd.md), [upstream audit](research/v0-2-25-upstream-and-patch-audit.md), [cross-repo audit](research/v0-2-25-cross-repo-and-upstream-audit.md), [Codex simplification audit](research/v0-2-25-simplification-audit-codex.md), [OMP simplification audit](research/v0-2-25-simplification-audit-omp.md).
Phase 1 authorizes planning only; Phase 2 code edits require explicit user approval of the final planning summary.

---

## 1. Architecture & Change Boundary

Adapt active plugin patches directly to `v0.2.25` contracts while adopting every contract-preserving upstream simplification (~70 fewer added lines and 8 fewer hunks in `quota-extension.patch`, 1 fewer patched upstream file, 3 fewer test lines, and 1 fewer `ApplyHeaderOverrides` call site).

| Repository | Files Modified | Planned Change |
| --- | --- | --- |
| `plugins/codex-candy-eval` | `patches/0004-admin-channel.patch`, `tests/native_inspection_fixture.py`, `.github/workflows/build.yml` | Pass plain `req.Context()` to 3 `ApplyHeaderOverrides` calls; update fixture binary candidates from `v0.2.23` to `v0.2.25`; bump workflow `upstream_tag` default to `v0.2.25`. |
| `plugins/sub2api-quota-extension` | `patches/quota-extension.patch`, `tests/test_account_repo_quota_test.go`, `tests/test_upstream_quota_test.go`, `tests/test_quota_script_test.go`, `.github/workflows/build.yml` | Rebase onto `v0.2.25` and apply simplifications S0–S6 + D3–D4 (`AccountBillingSettingsUpdate` fields, 19-column lock `SELECT`, clear-only `TempUnschedulable*` builder, `persistProbeFailure` memoization hook, `GetHeaderOverrides()` redaction, dead `AccountBulkUpdate.ExpiresAt` removal, key-slice deduplication, `billingBaseUrl` reuse, `resetForm` context); update Go tests; bump workflow `upstream_tag` default to `v0.2.25`. |
| `plugins/gemini-signature-rectifier` | `.github/workflows/build.yml` | Bump workflow `upstream_tag` default to `v0.2.25` on top of existing `406df21` (`main`). Keep patch and tests unchanged. |
| `plugins/sub2api-plugin-template` | `.github/workflows/build.yml`, `README.md` | Bump workflow `upstream_tag` default to `v0.2.25`; update stale `v0.2.20` example and trigger note in `README.md`. |
| Root `Sub2API-Plugins` | `.github/workflows/build.yml`, `README.md`, `.trellis/spec/backend/*.md`, submodule gitlinks | Bump workflow `upstream_tag` default to `v0.2.25`; update 11 stale `v0.2.23` references in `README.md` to `v0.2.25`; sync 6 backend spec files after verification; advance all 4 submodule pointers. |

Unchanged across all 5 repositories: `scripts/build.py`, `scripts/installer/*` (8 files), `tests/support.py`, `tests/test_build.py`, `tests/test_installer_test.go`, `.gitmodules`, and toolchain pins (`Go 1.27.4`, `Node 26.13.0`, `pnpm@12.16.1`, `Python 3.15.2`).

---

## 2. Upstream Intent & Simplification Designs

### 2.1 Context-Aware Header Overrides & `GetHeaderOverrides()` Redaction (S1)

Upstream commits `0f1e3c1f6` and `c5147eab1` changed `(*Account).ApplyHeaderOverrides(http.Header)` to `(*Account).ApplyHeaderOverrides(context.Context, http.Header)`. Across 49 upstream production call sites:
- API-key auth middleware attaches `WithHeaderOverrideRequestScope(ctx, userID, apiKeyID, groupID)`.
- Shared model catalogs strip it via `withoutHeaderOverrideRequestScope(ctx)`.
- OpenAI WS handshakes mark `withHeaderOverrideConnectionScope(ctx)` (omitting `request_id` only).
- All 42 forwarded/test/probe/usage HTTP requests pass plain request context (`req.Context()`), where background/admin calls have `scope == nil` and therefore omit any header containing `{{user_id}}`, `{{api_key_id}}`, `{{group_id}}`, or `{{request_id}}`.

1. **5 Outbound HTTP Call Sites (plain `req.Context()`)**:
   - `codex-candy-eval` (`backend/internal/service/account_codex_eval_service.go:394,547,626` in `0004-admin-channel.patch`, patch lines `564, 717, 796`): `credentialAccount.ApplyHeaderOverrides(req.Context(), req.Header)`.
   - `sub2api-quota-extension` (`account_quota_script.go:325` and `account_upstream_quota.go:289`): `account.ApplyHeaderOverrides(req.Context(), req.Header)`.
   - Do **not** wrap with `withoutHeaderOverrideRequestScope` or `withHeaderOverrideConnectionScope` (admin/probe contexts carry no API-key auth scope).

2. **Eliminate Dummy `http.Header` Materialization in `quotaScriptDiagnostic` (S1, `-6 lines`, `-1 call site`)**:
   - Previously, `quotaScriptDiagnostic(account *Account, err error) string` (`account_quota_script.go:364-372`) allocated an empty `http.Header`, called `account.ApplyHeaderOverrides(headers)`, and walked nested slices to redact configured header values. On `v0.2.25`, `ApplyHeaderOverrides(context.Background(), headers)` drops template-bearing entries (`Bearer sk-secret-{{user_id}}`), losing redaction of the configured value.
   - Upstream `(*Account).GetHeaderOverrides()` (`account_header_override.go:105-143`) already checks `IsHeaderOverrideEnabled()`, filters empty/invalid/blocked names, caches the effective lowercase map, and returns every non-empty configured override value (both static and template-bearing).
   - Replace the 9-line block with:
     ```go
     for _, secret := range account.GetHeaderOverrides() {
         message = strings.ReplaceAll(message, secret, "[redacted]")
     }
     ```

### 2.2 `AccountBillingSettingsUpdate` Struct, Clear-Only Pause Builder & Dead Bulk Field Removal (S0, S3, D4)

Upstream commit `03aa05fd9` consolidated billing-settings save parameters into `service.AccountBillingSettingsUpdate` (`account_service.go:141-145`) so new optional save controls no longer alter 5 repository/service method signatures:

```go
type AccountBillingSettingsUpdate struct {
    ProbeEnabled          *bool
    RateSyncEnabled       *bool
    GroupSyncEnabled      *bool
    RateMultiplier        *float64
    SetName               bool
    SetNotes              bool
    MergeAPIKeyQuotaState bool
    PreviousExpiresAt     *time.Time
}
```

- **S0 (`-5 signature hunks`, `-1 patched upstream file`)**: Keep `UpdateWithAccountBillingSettings(ctx, account, settings)` parameter lists identical to upstream across `AccountBillingSettingsRepository`, `accountRepository.UpdateWithAccountBillingSettings`, `updateAccount`, `updateLockedAccount`, and `lockAndMergeAccountProbeExtra`. Drop the `admin_account_upstream_billing_probe_test.go` hunk completely. Set `MergeAPIKeyQuotaState: true, PreviousExpiresAt: previousExpiresAt` only in `adminServiceImpl.UpdateAccount` (`admin_account.go`), preserving zero-value omission semantics for `repo.Update(ctx, account)` and upstream tests.
- **19-Column `SELECT ... FOR UPDATE` (`account_repo.go`)**: Merge upstream's 15 columns (ending with `extra -> 'upstream_billing_group_sync_enabled'` scanned into `currentGroupSyncEnabled`) with the 4 quota columns (`extra`, `expires_at`, `temp_unschedulable_until`, `temp_unschedulable_reason`). Update the 19-column `sqlmock` rows in the 3 patched upstream repo test files and `tests/test_account_repo_quota_test.go:291-292,305,307`.
- **D4 (`-8 lines` in `updateLockedAccount`)**: Native `updateLockedAccount` (`account_repo.go:522-618`) never writes `temp_unschedulable_until` or `temp_unschedulable_reason` on the Ent update builder, and `lockAndMergeAccountProbeExtra` holds `FOR UPDATE` on the row in the same transaction. Replace the 12-line `SetTempUnschedulable*` / `ClearTempUnschedulable*` branch matrix with the 4-line clear-only guard:
  ```go
  if settings.MergeAPIKeyQuotaState && account.TempUnschedulableUntil == nil && account.TempUnschedulableReason == "" {
      builder.ClearTempUnschedulableUntil()
      builder.ClearTempUnschedulableReason()
  }
  ```
- **S3 (`-2 hunks`, `-6 prod lines`, `-3 test lines`)**: Delete unused `ExpiresAt *time.Time` on `AccountBulkUpdate` (`account_service.go`), its dead `BulkUpdate` builder/sync branch (`account_repo.go`), and the unused fixture branch in `tests/test_upstream_quota_test.go:323-325`. Zero callers set `AccountBulkUpdate.ExpiresAt` since `UpdateAPIKeyQuotaState` took over expiry persistence, and `api-key-quota.md:39` explicitly forbids adding scheduling fields to `AccountBulkUpdate`.

### 2.3 Centralized Billing Probe Memoization in `persistProbeFailure` (S2)

Upstream commits `a95c9e263` and `03aa05fd9` extracted `fetchBilling(ctx, account, includeGroup, now) (upstreamBillingReply, error)` (shared by both `probeLoadedAccount` and non-persisting `PreviewGroup`) and routed all persisted probe failures in `probeLoadedAccount` through `persistProbeFailure` (`upstream_billing_probe.go:849-889`), which sets `status = UpstreamBillingProbeStatusUnsupported` whenever `reason == "unsupported"`.

Instead of modifying `fetchBilling` or scattering multi-line memoization blocks in `probeLoadedAccount` (`+19/-6` lines in `v0.2.24`), align with upstream's centralization (`+9/-2` lines total across 5 small hunks):
1. Retain the two 1-line `isAPIKeyUsageUnsupportedMemoized` skip guards in `RunDue` and `probeAccountWithMode`.
2. At the top of `persistProbeFailure`, normalize the two quota-specific unsupported cases to `"unsupported"`:
   ```go
   if reason == "invalid_response" || (reason == "http_error" && statusCode == http.StatusNotImplemented) {
       reason = "unsupported"
   }
   ```
   (Grok official domains and HTTP `404`/`405` already arrive from `fetchBilling` with `errBillingUnsupported.Error() == "unsupported"`.)
3. At the end of `persistProbeFailure` (after `updateSnapshot` succeeds), memoize in one place:
   ```go
   if status == UpstreamBillingProbeStatusUnsupported {
       memoizeUpstreamProbeUnsupported(ctx, s.accountRepo, account)
   }
   ```
   (`PreviewGroup` never calls `persistProbeFailure`, so draft group previews never mutate persisted memoization.)
4. In `probeLoadedAccount`, retain the single `clearUpstreamProbeUnsupported(ctx, s.accountRepo, account)` line after `s.updateSnapshot(ctx, account, snapshot, syncRate, group)`.

### 2.4 Quota Key-Slice Deduplication & Modal Rebase (S4–S6, D3)

- **S4–S6 (`-34 lines` of duplicated string literals)**:
  - `account_upstream_quota.go`: Define `APIKeyQuotaManagedExtraKeys = append([]string{APIKeyUsageUnsupportedIdentityExtraKey}, APIKeyQuotaSchedulingExtraKeys...)` (`-14 lines`).
  - `repository/scheduler_cache.go`: Append `service.APIKeyQuotaSchedulingExtraKeys...` in `filterSchedulerExtra` instead of repeating the 12 key literals (`-10 lines`).
  - `service/admin_account.go`: Loop over `APIKeyQuotaManagedExtraKeys` in `duplicateAccountExtra` instead of repeating the 13 key literals in `duplicateAccountDiscardedExtraKeys` (`-10 lines`), and refresh `BulkUpdateAccounts` context around `UpstreamBillingGroupSyncEnabledExtraKey`.
- **Frontend Modals (`CreateAccountModal.vue` & `EditAccountModal.vue`, D3)**:
  - `CreateAccountModal.vue`: Refresh Hunk #4 context in `resetForm` around `upstreamGroupSyncEnabled.value = false`. (Keep create-form base URL expression independent because upstream `previewBaseUrl` omits preset/placeholder fallbacks.)
  - `EditAccountModal.vue` (**D3**, `-2 lines`): Replace the 3-line adaptive/standard base-URL ternary in `quotaScriptConnection` with `base_url: billingBaseUrl.value || defaultBaseUrl.value`, reusing upstream `v0.2.25`'s `billingBaseUrl` computed (`EditAccountModal.vue:4563-4567`).

### 2.5 Explicitly Rejected False Simplifications

- **Do not reuse `PreviewUpstreamGroup` / `UpstreamGroupSource` for `quota-script/test`**: Upstream rejects requests supplying both saved `account_id` and draft fields (`400`), uses `*int64` for `proxy_id` (cannot distinguish omitted vs `null`), and omits `extra` and saved TLS/header-override overlays required by `api-key-quota.md:210-221`.
- **Do not reuse `fetchBilling` for `/v1/usage` or script HTTP**: `fetchBilling` lives on `UpstreamBillingProbeService` with hardcoded `/v1/sub2api/billing` and billing-envelope rules.
- **Do not reuse Gin OpenAI passthrough/SSE helpers in `codex-candy-eval` or `gemini-signature-rectifier`**: Different transport layers (`*http.Response` stream adapters vs Gin gateway writers).

---

## 3. Compatibility, Trade-Offs & Rollback

- **Single-version baseline**: Adapted patches target `v0.2.25` directly; `v0.2.24` remains reproducible at tagged commit `ba049b4`.
- **Binary version injection**: Upstream `v0.2.25` retains `0.2.24` in `backend/cmd/server/VERSION`; `scripts/build.py` injects `0.2.25` via `-X main.Version=0.2.25` and `-X main.buildVersion=0.2.25`.
- **Rollback**: Changes remain uncommitted until standalone builds, combined 5-platform build, Chromium inspection, and independent audits pass, followed by explicit `/git-commit` approval per repository. Untracked `.vscode/settings.json` stays untouched.
