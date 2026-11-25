# Sub2API v0.2.25 Adaptation & Simplification Implementation Plan

Goal: adapt active plugins, workflows, approved READMEs/fixtures, and backend specs to Sub2API `v0.2.25` while cutting ~70 added lines and 8 hunks of redundant patch code via `v0.2.25` upstream abstractions.
References: [prd.md](prd.md), [design.md](design.md).
Status: Implementation, standalone/combined builds, 1440×900 Chromium inspection, cross-agent audits, and Phase 3.3 spec synchronization completed.

---

## 1. Adapt `plugins/codex-candy-eval`

- [x] Apply patches `0001`–`0007` to a clean temporary `v0.2.25` tree (`348997267d756eab5729bb6b78a275a15d18796a`) using unauthenticated Git.
- [x] Update all three `credentialAccount.ApplyHeaderOverrides` calls in `backend/internal/service/account_codex_eval_service.go` (`SendCodexEvaluation`, `sendCodexAnthropicEvaluation`, `sendCodexGeminiEvaluation`) to `credentialAccount.ApplyHeaderOverrides(req.Context(), req.Header)`.
- [x] Re-export `plugins/codex-candy-eval/patches/0004-admin-channel.patch` and verify all 7 patches pass `git apply --binary --check` and `git diff --check` on pristine `v0.2.25`.
- [x] Update the 4 binary candidate strings in `plugins/codex-candy-eval/tests/native_inspection_fixture.py:48-51` from `v0.2.23` to `v0.2.25`.
- [x] Update `plugins/codex-candy-eval/.github/workflows/build.yml:11` from `default: v0.2.24` to `default: v0.2.25`.

## 2. Rebase & Simplify `plugins/sub2api-quota-extension`

- [x] Rebase and simplify `plugins/sub2api-quota-extension/patches/quota-extension.patch` on pristine `v0.2.25`:
  - **S0 + S3 (`account_service.go`)**: Add `MergeAPIKeyQuotaState bool` and `PreviousExpiresAt *time.Time` to `service.AccountBillingSettingsUpdate`, keep `UpdateWithAccountBillingSettings` signature identical to upstream, delete dead `ExpiresAt *time.Time` from `AccountBulkUpdate`, and drop the obsolete `admin_account_upstream_billing_probe_test.go` hunk.
  - **S0 + S3 + D4 (`account_repo.go` & 3 upstream repo tests)**: Merge the 15 upstream lock `SELECT` columns (`group_sync_enabled`) with the 4 quota columns (19 total) in `lockAndMergeAccountProbeExtra`; gate quota `extra`/expiry merge on `settings.MergeAPIKeyQuotaState`; shrink the `updateLockedAccount` `TempUnschedulable*` block to the 4-line clear-only guard; delete the dead `BulkUpdate` `updates.ExpiresAt` branch; update 19-column `sqlmock` rows and `service.AccountBillingSettingsUpdate{}` calls in `account_repo_grok_managed_extra_test.go`, `account_repo_opencode_go_usage_test.go`, and `account_repo_upstream_billing_probe_update_test.go`.
  - **S2 (`upstream_billing_probe.go`)**: Leave `fetchBilling`, `PreviewGroup`, and `probeLoadedAccount`'s error branch at upstream text; normalize `"invalid_response"` and `statusCode == http.StatusNotImplemented` to `"unsupported"` at the top of `persistProbeFailure`, call `memoizeUpstreamProbeUnsupported` when `status == UpstreamBillingProbeStatusUnsupported` at the end of `persistProbeFailure`, and keep `clearUpstreamProbeUnsupported` after `updateSnapshot(ctx, account, snapshot, syncRate, group)`.
  - **S1 (`account_quota_script.go` & `account_upstream_quota.go`)**: Pass `req.Context()` at the two outbound `ApplyHeaderOverrides` sites (`quotaScriptRequest` and `fillUpstreamAPIKeyUsage`), and replace the 9-line dummy `http.Header` round-trip in `quotaScriptDiagnostic` with a 3-line loop over `account.GetHeaderOverrides()`.
  - **S4–S6 (`account_upstream_quota.go`, `scheduler_cache.go`, `admin_account.go`)**: Derive `APIKeyQuotaManagedExtraKeys` from `APIKeyQuotaSchedulingExtraKeys`, append `service.APIKeyQuotaSchedulingExtraKeys...` in `filterSchedulerExtra`, delete `APIKeyQuotaManagedExtraKeys` in `duplicateAccountExtra` instead of duplicating literals in `duplicateAccountDiscardedExtraKeys`, set `MergeAPIKeyQuotaState: true, PreviousExpiresAt: previousExpiresAt` in `UpdateAccount`, and refresh `BulkUpdateAccounts` around `UpstreamBillingGroupSyncEnabledExtraKey`.
  - **D3 + Modal Rebase (`CreateAccountModal.vue` & `EditAccountModal.vue`)**: Refresh `CreateAccountModal.vue` `resetForm` hunk around `upstreamGroupSyncEnabled.value = false`, and simplify `EditAccountModal.vue` `quotaScriptConnection.base_url` to `billingBaseUrl.value || defaultBaseUrl.value`.
- [x] Update plugin Go tests:
  - `tests/test_account_repo_quota_test.go`: 19-column `sqlmock` row and `service.AccountBillingSettingsUpdate` calls (`MergeAPIKeyQuotaState: false` vs `MergeAPIKeyQuotaState: true, PreviousExpiresAt: &oldExpiry`).
  - `tests/test_upstream_quota_test.go`: `quotaAccountRepoFixture.UpdateWithAccountBillingSettings` signature and removal of dead `updates.ExpiresAt` fixture lines (`:323-325`).
  - `tests/test_quota_script_test.go`: add assertion verifying `quotaScriptDiagnostic` redacts a configured `header_overrides` value containing `{{user_id}}` / `{{request_id}}`.
- [x] Record exact before-and-after hunk and line counts of `quota-extension.patch` (`33 -> 32` files, `107 -> 99` hunks, `+1874/-60 -> +1805/-49`) and verify standalone + combined `git apply --binary --check` and `git diff --check` on pristine `v0.2.25`.
- [x] Update `plugins/sub2api-quota-extension/.github/workflows/build.yml:11` from `default: v0.2.24` to `default: v0.2.25`.

## 3. Align Remaining Workflows & Approved Documentation

- [x] Update `.github/workflows/build.yml:11` from `default: v0.2.24` to `default: v0.2.25` in `plugins/gemini-signature-rectifier` (on `406df21`), `plugins/sub2api-plugin-template`, and root.
- [x] Verify all 5 `.github/workflows/build.yml` files have matching SHA-256 digests (`e5ad88012ad1d617bf3c1266126f92e93b609cece96856bdc43ca0d22273c48a`) and all 12 other shared build-kit files remain byte-identical across all 5 repositories.
- [x] Update stale version references in root `README.md` (`v0.2.23` -> `v0.2.25`, 11 places) and `plugins/sub2api-plugin-template/README.md:17,57` (`v0.2.20` -> `v0.2.25` and accurate `pull_request` / `workflow_dispatch` trigger wording).
- [x] Preserve untracked `.vscode/settings.json` and leave synthetic `tests/test_installer_test.go:661` untouched.

## 4. Build & Visual Verification Gates

- [x] **Standalone `codex-candy-eval` build** (`UPSTREAM_TAG=v0.2.25`): exit `0`, 10 binaries built, `darwin-arm64 -version` = `0.2.25`.
- [x] **Standalone `sub2api-quota-extension` build** (`UPSTREAM_TAG=v0.2.25`): exit `0`, 10 binaries built, `darwin-arm64 -version` = `0.2.25`.
- [x] **Argument-free combined root build** (`python3 -B scripts/build.py`): exit `0`, auto-selected `v0.2.25` (`348997267...`), all 3 active plugins + common suites passed, 10 binaries built under `dist/build/`, `darwin-arm64 -version` = `0.2.25`.
- [x] **Chromium UI check (1440×900, scale 2, `en`/`zh`, `light`/`dark`)**: verified `scrollWidth = innerWidth = 1440`, 0 console/page errors, `cell-name` group-sync control + `AccountUsageCell` remote bars, `USD 0.00` balance, and localized `resets_at` tooltips; server stopped by exact PID and `/tmp` cleaned.

## 5. Review Gate, Spec Synchronization & Commit Prep (Phase 3)

- [x] Run independent cross-review (`omp` + read-only `flash` subagent) verifying requirements, hunk/line reductions, error order, async timing, SHA-256 alignment, and binary timestamps.
- [x] Phase 3.3: Synchronize `.trellis/spec/backend/{index,quality-guidelines,api-key-quota,gemini-signature-rectifier,runtime-installation,minimal-linux-delivery}.md` to `v0.2.25` (including `minimal-linux-delivery.md:78` recording embedded `0.2.24` in `VERSION`, `AccountBillingSettingsUpdate` quota fields, `persistProbeFailure` memoization, `GetHeaderOverrides()` redaction, and non-gateway header-override variable omission).
- [ ] Phase 3.4: Awaiting user request/authorization before any `git commit` or branch operation.
