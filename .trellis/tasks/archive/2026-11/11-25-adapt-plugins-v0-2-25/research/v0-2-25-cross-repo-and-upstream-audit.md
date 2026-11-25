# Sub2API v0.2.25 cross-repository and upstream audit (independent worker)

Audit date: 2026-11-25 (04:16 to 04:55 +0800). Task: `11-25-adapt-plugins-v0-2-25`, Trellis Phase 1 research.
Method: public unauthenticated reads, `git apply --binary --check` in a private temporary directory, static symbol cross-checks, and Go type-checks in that directory.
No production file, patch, test, workflow, README, spec file, or Git state changed. The working tree equals its state at the start of the audit.

## 1. Results

| # | Question | Result |
| --- | --- | --- |
| 1 | Does `releases/latest` resolve to `v0.2.25`? | Yes. Published 2026-11-24T03:21:08Z. Not a draft. Not a prerelease. |
| 2 | Eval plugin, standalone on `v0.2.25` | 7 patches pass `git apply --binary --check`. The backend does not compile. Cause: 3 call sites of the old `ApplyHeaderOverrides(h)` method. |
| 3 | Gemini plugin, standalone on `v0.2.25` | The patch passes. The backend, the gate `go vet`, and the staged plugin tests type-check. No change is necessary. |
| 4 | Quota plugin, standalone on `v0.2.25` | `git apply --binary --check` fails: 25 of 107 hunks in 9 files. 3 more call sites will not compile after the rebase. |
| 5 | Combined build on `v0.2.25` | The eval patches and the Gemini patch pass. The quota patch fails with the same 25 hunks. The build stops at "Download and patch source". |
| 6 | Pull-request builds | They resolve the latest release, so they now build `v0.2.25`. They fail for the root repository, the eval plugin, and the quota plugin until the adaptation lands. |
| 7 | Build-kit alignment | 13 shared files are byte-identical across the root repository and the 4 submodules. |
| 8 | Toolchain | No change is necessary. Upstream keeps Go 1.27.4, the same `package.json`, and the same `pnpm-lock.yaml`. |
| 9 | Remote sync | Local `HEAD` equals remote `main` in all 5 repositories. Upstream CPA has no new commit or tag after `v0.4.7`. |
| 10 | Documentation drift (it exists before this task) | Root `README.md` shows `v0.2.23` in 11 places. The workflow default is `v0.2.24` since 2026-11-22. |

Names in this record: "eval plugin" is `codex-candy-eval`. "Gemini plugin" is `gemini-signature-rectifier`. "Quota plugin" is `sub2api-quota-extension`. "Template" is `sub2api-plugin-template`. "Root repository" is `Sub2API-Plugins`.

## 2. Upstream identity and toolchain facts

Source: `git ls-remote`, `git cat-file`, and `GET https://api.github.com/repos/Wei-Shaw/sub2api/releases/latest`. No credential was used.

| Fact | Value |
| --- | --- |
| `v0.2.24` tag object | `7515db6dc56c2a6120dfb7abed70ef089ebc1457` (annotated) |
| `v0.2.24` commit | `5c2982a81b46e2142d0143d2f83c1ce9c4da1d24` |
| `v0.2.25` tag object | `8fab111f92447a3edbcdf67a517e45b6a3cc4d31` (annotated, tagger `shaw`, 1795490015 +0800) |
| `v0.2.25` commit | `348997267d756eab5729bb6b78a275a15d18796a` (`Merge pull request #9052 from Wei-Shaw/feat/header-override-identity-variables`) |
| Upstream `main` | `0f6671457132425d1b84f3d80536b53e02942424`. It is one commit after the tag: `chore: sync VERSION to 0.2.25 [skip ci]` |
| `releases/latest` | `tag_name` `v0.2.25`, name `Sub2API 0.2.25`, `draft` false, `prerelease` false, `target_commitish` `main` |
| Release history | `v0.2.25` 2026-11-24, `v0.2.24` 2026-11-20, `v0.2.23` 2026-11-18, `v0.2.22` 2026-11-17, `v0.2.21` 2026-11-11, `v0.2.20` 2026-11-07 |
| `backend/cmd/server/VERSION` | `v0.2.24`: `0.2.23`. `v0.2.25`: `0.2.24`. `main`: `0.2.25`. The file lags one release behind its tag. |
| `backend/go.mod` | `go 1.27.4` at both tags and on `main`. No `toolchain` directive change. |
| Go dependency change | Only `github.com/gorilla/websocket v1.5.3` becomes `v1.5.4-0.20240701034025-d67f41855da4`. `go.sum` gains 2 lines and keeps the `v1.5.3` lines. |
| `frontend/package.json` | Blob `e42bcb03f8d152fb95f2f0c1a9c5b4ac64b5d0e9` at `v0.2.24`, `v0.2.25`, and `main`. It has no `packageManager` field and no `engines` field. `pnpm.overrides` does not change. |
| `frontend/pnpm-lock.yaml` | Blob `1bf73beac90414b189414988cd7cf4d311dc2b04` at both tags and on `main`. `lockfileVersion: '9.0'`. |
| Frontend scripts | `build` is `pnpm run check:i18n && vue-tsc -b && vite build`. No change. |
| Range size | 15 commits (12 content commits and 3 merges). 91 files: 5 added and 86 modified. +3486 and -319 lines. |

No file in the range touches `package.json`, `pnpm-lock.yaml`, `.npmrc`, `pnpm-workspace.yaml`, `.nvmrc`, `Dockerfile`, `Makefile`, `.github/`, Wire files, scheduler services, Gemini services, Antigravity services, `AccountUsageCell.vue`, `SettingsView.vue`, `accountUsageRefresh.ts`, or `embedded-url.ts`.

Comparison: [v0.2.24...v0.2.25](https://github.com/Wei-Shaw/sub2api/compare/5c2982a81b46e2142d0143d2f83c1ce9c4da1d24...348997267d756eab5729bb6b78a275a15d18796a).

The build does not read `backend/cmd/server/VERSION`. `scripts/build.py` passes the tag to the linker with `-X main.Version=`. The quota patch does not touch the `gorilla/websocket` line.

## 3. Upstream commits in `v0.2.24..v0.2.25`

| Content commit | Author and date | Change | Plugin relevance |
| --- | --- | --- | --- |
| [`328db26f4`](https://github.com/Wei-Shaw/sub2api/commit/328db26f4) | github-actions[bot], 2026-11-20 | `chore: sync VERSION to 0.2.24 [skip ci]` | None. |
| [`a95c9e263`](https://github.com/Wei-Shaw/sub2api/commit/a95c9e263) | Brisbanehuang, 2026-11-21 | Sync account name and notes from the upstream group (manual button) | Quota. It splits `probeLoadedAccount` into `fetchBilling` and adds the `errBillingUnsupported` sentinel. It adds `PreviewGroup`, the route `POST /admin/accounts/upstream-billing-probe/group-preview`, `UpstreamGroupSyncButton.vue`, and `previewUpstreamGroup`. |
| [`03aa05fd9`](https://github.com/Wei-Shaw/sub2api/commit/03aa05fd9) | Brisbanehuang, 2026-11-21 | Automatic group sync per account | Quota. It adds `AccountBillingSettingsUpdate`, `SetName` and `SetNotes`, `GroupSyncEnabled`, the extra key `upstream_billing_group_sync_enabled`, and the `group` argument of `UpdateUpstreamBillingProbeSnapshot`. |
| [`2b7437832`](https://github.com/Wei-Shaw/sub2api/commit/2b7437832) | itzhan, 2026-11-23 | OpenAI passthrough keeps `invalid_encrypted_content` and uses passthrough rules | None. No plugin uses `applyErrorPassthroughRuleWithRule`. |
| [`38903b6d1`](https://github.com/Wei-Shaw/sub2api/commit/38903b6d1) | shaw, 2026-11-24 | Validate group text before the database write. `include` accepts a list. | None. |
| [`ba9df6f1c`](https://github.com/Wei-Shaw/sub2api/commit/ba9df6f1c) and [`797fde4e9`](https://github.com/Wei-Shaw/sub2api/commit/797fde4e9) | shaw, 2026-11-24 | `gorilla/websocket` upgrade for GO-2026-6278 (the same change on two branches) | None. One net dependency change. |
| [`34423bf1e`](https://github.com/Wei-Shaw/sub2api/commit/34423bf1e) | shaw, 2026-11-24 | Trim group text before the control-character check | None. |
| [`eabf37852`](https://github.com/Wei-Shaw/sub2api/commit/eabf37852) | shaw, 2026-11-24 | Compact `response.failed` rewrites capacity-shed codes | None. |
| [`0f1e3c1f6`](https://github.com/Wei-Shaw/sub2api/commit/0f1e3c1f6) | shaw, 2026-11-24 | Header override identity variables `{{user_id}}`, `{{api_key_id}}`, `{{group_id}}`, `{{request_id}}` | **Eval and quota.** It changes `ApplyHeaderOverrides(h)` to `ApplyHeaderOverrides(ctx, h)` and updates 52 upstream call sites (test files included). It adds `account_header_override_vars.go`, `reportedIdentity` in the OpenAI WS pool, the variable panel in `HeaderOverrideEditor.vue`, and the template parser in `credentialsBuilder.ts`. |
| [`c5147eab1`](https://github.com/Wei-Shaw/sub2api/commit/c5147eab1) | shaw, 2026-11-24 | Audit fixes for the identity variables | It adds `withoutHeaderOverrideRequestScope` for shared model lists. `HeaderOverrideValue` returns `false` for a value with a variable. `ValidateHeaderOverrideVariableUsage` also runs on an account-type change. `OpsUpstreamErrorEvent` gains `ReportedHeaders`. |

Merges: `4d4433df0` (PR #9008), `00c51f07d` (PR #9045), and `348997267` (PR #9052). `v0.2.24` is an ancestor of `v0.2.25`. The tag did not move.

## 4. Complete list of signature and behavior changes

### 4.1 Breaking signatures

| Old declaration (v0.2.24) | New declaration (v0.2.25) | Commit |
| --- | --- | --- |
| `func (a *Account) ApplyHeaderOverrides(h http.Header)` | `func (a *Account) ApplyHeaderOverrides(ctx context.Context, h http.Header)` | `0f1e3c1f6` |
| `AccountBillingSettingsRepository.UpdateWithAccountBillingSettings(ctx, account, probeEnabled, rateSyncEnabled *bool, rateMultiplier *float64) error` | `UpdateWithAccountBillingSettings(ctx, account, settings AccountBillingSettingsUpdate) error` | `03aa05fd9` |
| `AccountRepository.UpdateWithAccountBillingSettings` (same 5 parameters) | Same struct parameter | `03aa05fd9` |
| `lockAndMergeAccountProbeExtra(ctx, client, account, explicitProbeEnabled, explicitRateSyncEnabled)` | `lockAndMergeAccountProbeExtra(ctx, client, account, settings)` | `03aa05fd9` |
| `updateAccount` and `updateLockedAccount` (same 3 pointer parameters) | Same struct parameter | `03aa05fd9` |
| `UpdateUpstreamBillingProbeSnapshot(ctx, account, snapshot, rateMultiplier *float64)` | Adds `group BillingGroupInfo` as the fifth argument. The interface `upstreamBillingProbeSnapshotWriter` changes in the same way. | `03aa05fd9` |
| `upstreamBillingProbeService.updateSnapshot(ctx, account, snapshot, rateMultiplier)` | Adds `group BillingGroupInfo` | `03aa05fd9` |

### 4.2 New declarations in package `service` (no collision with plugin names)

`AccountBillingSettingsUpdate{ProbeEnabled, RateSyncEnabled, GroupSyncEnabled *bool; RateMultiplier *float64; SetName, SetNotes bool}`, `BillingGroupInfo`, `ErrUpstreamBillingGroupSyncRequiresProbe`, `UpstreamBillingGroupSyncEnabledExtraKey`, `APIKeyService.GetBillingGroupInfo`, `UpstreamBillingProbeService.fetchBilling`, `UpstreamBillingProbeService.PreviewGroup`, `upstreamBillingGroupInfo`, `upstreamBillingReply`, `errBillingUnsupported`, `HeaderOverrideRequestScope`, `WithHeaderOverrideRequestScope`, `withoutHeaderOverrideRequestScope`, `withHeaderOverrideConnectionScope`, `ValidateHeaderOverrideVariableUsage`, `HeaderOverrideVar*` constants, `applyErrorPassthroughRuleWithRule`, `applyErrorPassthroughRuleDetailed`, `writeOpenAICompactSSEFailureWithCode`, `writeOpenAICompactSSEFailureEvent`, `isOpenAIInvalidEncryptedContentError`, `sanitizeOpenAIPassthroughClientErrorText`, `replaceCaseInsensitive`, `openAIPassthroughClientErrorField`, `openAIPassthroughClientErrorCode`, `writeOpenAIPassthroughStructuredErrorEnvelope`. Package `handler`: `AccountHandler.PreviewUpstreamGroup`, `keyBillingIncludes`.

### 4.3 Additive changes

- `CreateAccountRequest`, `UpdateAccountRequest`, `CreateAccountInput`, and `UpdateAccountInput` gain `upstream_billing_group_sync_enabled` / `GroupSyncEnabled *bool`.
- `UpdateAccount` passes `SetName: input.Name != ""` and `SetNotes: input.Notes != nil`. `Update(ctx, account)` passes `SetName: true, SetNotes: true, RateMultiplier: account.RateMultiplier`.
- `lockAndMergeAccountProbeExtra` selects one more column, `extra -> 'upstream_billing_group_sync_enabled'`, and scans `currentGroupSyncEnabled`.
- `schedulerNeutralExtraKeyPrefixes` gains `upstream_billing_group_sync`.
- `EditAccountModal.vue` omits `name` and `notes` from the update payload when they do not change (API-key accounts).
- `GET /v1/sub2api/billing?include=group` returns `group_name` and `group_description`.
- `validateHeaderOverrideRows(rows, options = {})` in `credentialsBuilder.ts` gains an optional second argument. Existing calls stay valid. `isMultiProtocolApiKeyPlatform` stays exported.
- New locale keys: `admin.accounts.upstreamBilling.{autoSyncGroup, autoSyncGroupHint, syncGroup, saveGroup, groupCredentials, groupUnavailable, groupFailed, groupSynced}`, `admin.accounts.headerOverride.{invalidVariable, variableNotAllowed, removeRow, previewLabel, variablesTitle, variablesHint, variablesUnavailable, variables, variableNotes}`, `admin.ops.reportedHeaders`. `en` and `zh` receive the same keys.
- `frontend/src/types/index.ts` gains `upstream_billing_group_sync_enabled?: boolean` in three interfaces.

### 4.4 Behavior changes

- `ApplyHeaderOverrides` does not send a header when a variable has no value. It removes a same-named client header in that case. Only API-key accounts resolve variables.
- `HeaderOverrideValue` returns `("", false)` when the value contains a variable.
- Shared model-list requests call `ApplyHeaderOverrides(withoutHeaderOverrideRequestScope(req.Context()), headers)`. They do not report a user identity.
- `probeLoadedAccount` now calls `fetchBilling`. `fetchBilling` returns `errBillingUnsupported` for a Grok account without `base_url` and for HTTP 404 and 405. It returns `errors.New("http_error")` with `reply.status` for all other non-2xx responses, HTTP 501 included.
- A successful probe can also write `accounts.name` and `accounts.notes` when group sync is on.

### 4.5 Changed test helpers (upstream `_test.go` files)

| Helper | Change |
| --- | --- |
| `openCodeGoMergeMockColumns()` (`repository`) | Adds the column `group_sync_enabled`. |
| sqlmock rows for the lock SELECT in `account_repo_grok_managed_extra_test.go`, `account_repo_opencode_go_usage_test.go`, and `account_repo_upstream_billing_probe_update_test.go` | One more column and one more value. Calls use `service.AccountBillingSettingsUpdate{}`. |
| `accountBillingSettingsAdminRepo.UpdateWithAccountBillingSettings` (`service`) | Takes `settings AccountBillingSettingsUpdate`. |
| `upstreamBillingProbeAccountRepo.UpdateUpstreamBillingProbeSnapshot` (`service`) | Takes `group BillingGroupInfo`. |
| `newKeyBillingRouteTestRouter(runMode string, groups service.GroupRepository)` (`server/routes`) | Adds the `groups` argument. |
| `setupUpstreamBillingProbeRouter()` (`handler/admin`) | Adds the route `/admin/accounts/upstream-billing-probe/group-preview`. |
| `AccountsView.lite.spec.ts` | Mocks `previewUpstreamGroup` and `updateAccount`. `DataTableStub` renders the `cell-name` slot. |

## 5. Patch application matrix

Command: `git apply --binary --check <patch>` in a detached checkout of the tag. This replicates `scripts/build.py` line 78 (`git apply --binary <patch>`). The build passes no `--3way`, `--reject`, or `-C` option.

| Scenario | Eval `0001` to `0007` | Gemini | Quota | Result |
| --- | --- | --- | --- | --- |
| Baseline: `v0.2.24`, combined | Pass | Pass | Pass | All 9 patches apply. Only `0003` reports 3 whitespace warnings (vendor assets, the same as before). |
| `v0.2.25`, eval standalone | Pass (7 of 7) | n/a | n/a | Text applies. Go does not compile (section 7). |
| `v0.2.25`, Gemini standalone | n/a | Pass | n/a | Text applies. Go compiles (section 7). |
| `v0.2.25`, quota standalone | n/a | n/a | **Fail** | 9 files do not apply. |
| `v0.2.25`, combined (eval, Gemini, quota) | Pass (7 of 7) | Pass | **Fail** | The same 9 files do not apply. Eval and Gemini do not change the quota result. |

`git apply --binary --check` output for the quota patch:

```text
error: patch failed: backend/internal/repository/account_repo.go:461
error: patch failed: backend/internal/repository/account_repo_grok_managed_extra_test.go:143
error: patch failed: backend/internal/repository/account_repo_opencode_go_usage_test.go:77
error: patch failed: backend/internal/repository/account_repo_upstream_billing_probe_update_test.go:81
error: patch failed: backend/internal/service/account_service.go:146
error: patch failed: backend/internal/service/admin_account.go:777
error: patch failed: backend/internal/service/admin_account_upstream_billing_probe_test.go:31
error: patch failed: backend/internal/service/upstream_billing_probe.go:640
error: patch failed: frontend/src/components/account/CreateAccountModal.vue:5665
```

## 6. Quota patch: rejected hunks and causes

`git apply --binary --verbose --reject` gives the exact hunk map. The quota patch has 107 hunks in 33 files. 25 hunks do not apply. 82 hunks apply. All 82 apply with full context at an offset (47 offset messages, 0 context reductions).

| File | Hunks | Rejected | Cause |
| --- | ---: | --- | --- |
| `backend/internal/repository/account_repo.go` | 18 | 8: #2 to #8 and #10 | A (5 hunks: #2 to #5 and #7), B (#8 and #10), C (#6) |
| `backend/internal/repository/account_repo_grok_managed_extra_test.go` | 1 | 1 | B |
| `backend/internal/repository/account_repo_opencode_go_usage_test.go` | 2 | 2 | B |
| `backend/internal/repository/account_repo_upstream_billing_probe_update_test.go` | 4 | 4 | B |
| `backend/internal/service/account_service.go` | 2 | 1 | A (the interface) |
| `backend/internal/service/admin_account.go` | 12 | 4: #5, #6, #8, #10 | A (#6), D (#5, #8, #10) |
| `backend/internal/service/admin_account_upstream_billing_probe_test.go` | 1 | 1 | A |
| `backend/internal/service/upstream_billing_probe.go` | 5 | 3: #3, #4, #5 | E |
| `frontend/src/components/account/CreateAccountModal.vue` | 5 | 1: #4 | D (`resetForm`) |
| Other 24 files | 57 | 0 | None |

Causes:

- **A. Billing-settings struct.** Upstream replaced the three pointer parameters with `settings service.AccountBillingSettingsUpdate`. The plugin adds `previousExpiresAt ...*time.Time` to the same signatures: `UpdateWithAccountBillingSettings`, `updateAccount`, `updateLockedAccount`, `lockAndMergeAccountProbeExtra`, the interface, the `UpdateAccount` call, and the upstream test stub.
- **B. Lock SELECT columns.** Upstream appends `extra -> 'upstream_billing_group_sync_enabled'` after `upstream_model_metadata`. The plugin appends `extra`, `expires_at`, `temp_unschedulable_until`, and `temp_unschedulable_reason` at the same position. The plugin also extends the sqlmock rows in three upstream test files. The merged query has 19 columns: 15 from upstream and 4 from the plugin.
- **C. Builder section.** Upstream replaced `if explicitRateMultiplier != nil {` with `if settings.RateMultiplier != nil {` and made `SetName` and `SetNotes` conditional. The plugin inserts the `TempUnschedulable*` block before that line.
- **D. Context only.** Upstream inserted `upstreamGroupSyncEnabled.value = false` in `resetForm` and `UpstreamBillingGroupSyncEnabledExtraKey` lines in `BulkUpdateAccounts`. The plugin logic does not conflict.
- **E. Probe split.** Upstream moved the request code from `probeLoadedAccount` to `fetchBilling`. The plugin hunks that memoize an unsupported probe (404, 405, 501, invalid 2xx body) and the hunk after `updateSnapshot` lost their context.

Compile-level breaks that `git apply --check` cannot see (they apply textually):

| File | Line | Current call | Required call |
| --- | ---: | --- | --- |
| `backend/internal/service/account_quota_script.go` | 325 | `account.ApplyHeaderOverrides(req.Header)` | `account.ApplyHeaderOverrides(<ctx>, req.Header)` |
| `backend/internal/service/account_quota_script.go` | 365 | `account.ApplyHeaderOverrides(headers)` | `account.ApplyHeaderOverrides(<ctx>, headers)` |
| `backend/internal/service/account_upstream_quota.go` | 289 | `account.ApplyHeaderOverrides(req.Header)` | `account.ApplyHeaderOverrides(<ctx>, req.Header)` |

Plugin test files that use a changed signature:

| File | Line | Use |
| --- | ---: | --- |
| `plugins/sub2api-quota-extension/tests/test_account_repo_quota_test.go` | 291 | sqlmock row for the lock SELECT (18 columns, no `group_sync` column) |
| `plugins/sub2api-quota-extension/tests/test_account_repo_quota_test.go` | 305 and 307 | `repo.UpdateWithAccountBillingSettings(context.Background(), account, nil, nil, nil)` and the same call with `&oldExpiry` |
| `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go` | 221 | `quotaAccountRepoFixture.UpdateWithAccountBillingSettings(..., previousExpiresAt ...*time.Time)` |

Contract to keep: `.trellis/spec/backend/api-key-quota.md` line 271. A default or billing probe with HTTP 404, 405, 501, or an invalid 2xx body saves the shared unsupported identity. Line 272 excludes 401, 403, 429, other 5xx responses, timeouts, and transport failures. `TestUpstreamQuotaProbeMemoization` covers these cases. On `v0.2.25`, HTTP 501 arrives as `errors.New("http_error")` with `reply.status == 501`. The sentinel `errBillingUnsupported` covers the Grok short-circuit and HTTP 404 and 405.

## 7. Compile evidence (Go)

Environment: Go 1.27.4 darwin/arm64 (equal to the workflow `go-version`). `GOFLAGS=-mod=readonly GOPROXY=off GOSUMDB=off GOTOOLCHAIN=local`. `GOCACHE` and `GOTELEMETRYDIR` pointed to the private directory. The user module cache was read only. Checks after the runs found 0 changed files in the user module cache, build cache, and telemetry directory.

| Run | Tree | Command | Exit | Output |
| --- | --- | --- | ---: | --- |
| A | `v0.2.25` + eval patches + Gemini patch | `go vet ./internal/server ./internal/server/routes ./internal/web` (the build gate) | 1 | Exactly 3 errors. All are `not enough arguments in call to credentialAccount.ApplyHeaderOverrides`. `have ("net/http".Header)`, `want ("context".Context, "net/http".Header)`. Positions: `internal/service/account_codex_eval_service.go:394:41`, `:547:41`, `:626:41`. |
| B1 | Run A + a throwaway change of the 3 calls to `ApplyHeaderOverrides(req.Context(), req.Header)` | Same gate | 0 | None |
| B2 | Same tree | `go build -o <private dir>/bin-probe ./cmd/server` | 0 | None |
| B3 | Same tree | `go vet ./internal/service ./internal/repository ./internal/handler/admin ./internal/codexeval` | 0 | None |
| B4 | Same tree | `go build ./...` | 0 | None |
| C | Same tree + the 16 eval and Gemini plugin `*_test.go` files staged as `tests/support.py` stages them | `go vet -tags=unit` on the same 7 packages | 0 | None. The plugin tests type-check against `v0.2.25`. |
| D | Same tree | `go vet` without `-tags=unit` | 1 | `test_gemini_native_signature_rectifier_test.go:94:11: undefined: errorPolicyRepoStub`. The upstream helper is behind the `unit` tag. The build uses `-tags=unit`, so run C is the applicable result. |

Eval call sites in `plugins/codex-candy-eval/patches/0004-admin-channel.patch` (patch lines 564, 717, and 796):

| Function in `account_codex_eval_service.go` | Line |
| --- | ---: |
| `(*AccountTestService).SendCodexEvaluation` | 394 |
| `(*AccountTestService).sendCodexAnthropicEvaluation` | 547 |
| `(*AccountTestService).sendCodexGeminiEvaluation` | 626 |

The three functions are methods of `AccountTestService`. Upstream changed the sibling functions in `account_test_service.go` to `account.ApplyHeaderOverrides(req.Context(), req.Header)` (30 call sites). The same argument is the direct equivalent for the eval call sites.

Behavior note: evaluation requests and quota probe requests have no API-key request scope. A header override that contains a variable is not sent on these requests. This equals the upstream rule for connection tests and model lists.

Static cross-check (Python script over `v0.2.24`, `v0.2.24` + all patches, and `v0.2.25`): 0 name collisions between plugin-added and upstream-new Go identifiers (production and test files). 0 upstream top-level names removed. 0 collisions between the 20 plugin flat test files with an upstream package target and upstream names in their target packages. 4 installer test files stage outside the upstream tree. The plugin-added call sites of changed signatures are the 6 `ApplyHeaderOverrides` calls and the quota uses in section 6. The Gemini patch uses `OpsUpstreamErrorEvent{` with keyed fields, which stays valid.

## 8. Semantic checks by area

| Area | Upstream change in the range | Effect on plugins |
| --- | --- | --- |
| Go services | Section 4 | Eval: compile break, 3 calls. Quota: compile break after the rebase, 3 calls, plus the struct and probe changes. Gemini: none. |
| Repositories | `account_repo.go`: `AccountBillingSettingsUpdate`, `SetName` and `SetNotes`, one more lock SELECT column, `UpdateUpstreamBillingProbeSnapshot(+group)`. `scheduler_cache.go` did not change. | Quota: 8 rejected hunks and 3 upstream test files. The quota SQL in `UpdateAPIKeyQuotaState` is a separate statement. |
| DTOs | `CreateAccountRequest` and `UpdateAccountRequest` gain `GroupSyncEnabled`. `keyBillingInfoResponse` embeds `BillingGroupInfo`. | None. No plugin handler reads these structs. |
| Wire | No change. | The quota changes in `wire.go` and `wire_gen.go` and the eval changes in `main.go` and `router.go` stay valid. |
| Routes | `routes/admin.go` gains one route. | None. The quota route and the eval routes do not conflict. Both patches apply. |
| Scheduler | Only `schedulerNeutralExtraKeyPrefixes` gains one prefix. | None. |
| Gemini | No Gemini service file changed. | None. The Gemini patch targets are not in the upstream change set. |
| OpenAI | Passthrough error forwarding, compact SSE failure codes, WS pool `reportedIdentity`. | None. The eval service sends its own requests through `httpUpstream.Do`. |
| Anthropic | One `ApplyHeaderOverrides` call in `gateway_anthropic_passthrough.go`. | None. |
| Antigravity | `PreviewGroup` accepts a legacy `upstream` relay account. | None. |
| `AccountsView.vue` | The `cell-name` slot has a new flex wrapper and a sync button. New `syncUpstreamGroup` and `syncingUpstreamGroup`. | Quota: 5 hunks apply with full context at an offset. They change the batch usage code only. |
| `AccountUsageCell.vue` | No change. | Quota patch applies. |
| `SettingsView.vue` | No change. | Gemini patch applies. |
| Locales | Section 4.3. | No key collision with `admin.accounts.quotaScript`, `admin.accounts.usageWindow.upstreamQuota`, `admin.settings.rectifier.geminiNativeSignature*`, or `nav.accountEvaluation`. |
| Types | 3 optional fields. | No collision with the 4 quota fields of `AccountUsageInfo`. |
| Utils | `credentialsBuilder.ts` gains functions. `accountUsageRefresh.ts` and `embedded-url.ts` did not change. | `AccountsView.vue` imports `isMultiProtocolApiKeyPlatform`, which stays exported. |
| Upstream frontend tests | `AccountsView.lite.spec.ts` and `admin.accounts.upstreamBillingProbe.spec.ts` change. No strict assertion on `accountsAPI` keys exists. | The quota `test_usage_batch.test.ts` uses its own `DataTable` stub with the `cell-usage` slot only. The new upstream code calls the new API only after a button click. |

## 9. Frontend status

No frontend type-check or test ran in this audit. A `vue-tsc` run needs a full dependency install. The static checks found no overlap for eval (`CodexEvalView.vue`, `AppSidebar.vue`, `router/index.ts`, `embedded-url.ts`, `common.ts`) and Gemini (`api/admin/settings.ts`, `admin/settings.ts`, `SettingsView.vue`). The quota frontend needs one context-only rebase (`CreateAccountModal.vue` hunk #4).

## 10. Five-repository sync status

Source: `git ls-remote` without credentials, compared with local `HEAD` and local tags.

| Repository | Remote URL | Local `HEAD` | Remote `main` | Tags | State |
| --- | --- | --- | --- | --- | --- |
| Root repository | `Nanboom233/Sub2API-Plugins` | `ba049b42e0e39bce63716c4080daef909c16e5d7` | `ba049b42` | `v0.2.19`, `v0.2.23`, `v0.2.24` (`ba049b4`). Local and remote tags are identical. | Equal |
| Eval plugin | `Nanboom233/codex-candy-eval` | `609f9798b7b7e220c929a33e41036f665b516abf` | `609f979` | `v0.2.24` points to `609f979`. Local and remote tags are identical. | Equal |
| Upstream CPA | `haowang02/cpa-plugin-codex-candy-eval` | n/a | `9682e76812c035e523a748620bba00c55c5970cb` | Latest tag `v0.4.7` points to `9682e76` (2026-11-18). | `9682e76` is an ancestor of the fork `HEAD`. The fork has 37 commits that upstream CPA does not have. Its 3 latest commits are `4301252`, `6fc5b1f`, and `609f979`. Upstream CPA has 0 commits that the fork does not have. The commits of `v0.4.2` to `v0.4.7` are present locally. The fork does not have these tags. No new upstream CPA commit or tag exists. |
| Gemini plugin | `Nanboom233/sub2api-gemini-signature-rectifier` | `406df210a84744021d810386a11a7ef29ac22b34` | `406df21` | `v0.2.24` points to `ccb2a98a8af307e15824d63b47849256a93aa06b`. | Equal to the remote. The root repository records `ccb2a98` and shows ` M plugins/gemini-signature-rectifier`. |
| Template | `Nanboom233/sub2api-plugin-template` | `d823e9c5ee5a86214e38b331597433f8539ef167` | `d823e9c` | None | Equal |
| Quota plugin | `Nanboom233/sub2api-quota-extension` | `79a5f71285f601a98358d9c11088af07df302ebf` | `79a5f71` | None | Equal |

## 11. Build-kit hashes

SHA-256 of each shared file in the root repository and the 4 submodules. Each row has one hash. All 5 copies are identical (65 comparisons).

| File | SHA-256 |
| --- | --- |
| `scripts/build.py` | `70ab4b4fc98bb281adc984a0d8b1f9cf08b489758d6af9a63a259da1b5951064` |
| `scripts/installer/apple.go` | `136504568baee4067260a4fa83d4f6a077c5414077f2480e864c460e2aef9d86` |
| `scripts/installer/executable.go` | `59635347bbe28abdccc3a6922c136b4c938b0a56e3472052e8355fcfc4fa7f21` |
| `scripts/installer/main.go` | `2b2b26ea1fd66a61489cd0f0371b04a52c4c2e8e8cbf7249ea1c645befc1a9f6` |
| `scripts/installer/messages.go` | `32ed10be109c44518483ac8f6158e43279afad49de77888b856e2fc19613afbf` |
| `scripts/installer/native.go` | `5bdfb556126c724e13a1c13db1985b6b41fc94283286eb2181b67b958049262c` |
| `scripts/installer/platform_unix.go` | `c52d2605c6aa7adeccc56f9ab271c391fbbb42c3b167ed7dcb73031d28d1cdfd` |
| `scripts/installer/platform_windows.go` | `18a267d4af388dd5bc0b7cebb602e71cab6635a7b1e2b94d6d70f2cb2a5dd6aa` |
| `scripts/installer/ui.go` | `5d32b0003c48c7ae1632e33104938ac8400b41478afd222171eeb6ee59dcab5c` |
| `tests/support.py` | `5b2f2bc1980e64686d2b30c2e3529c67e8fe6afb7f2497ddd1f32455e6c5a575` |
| `tests/test_build.py` | `cdac9ee418eae52cf29cc4c585d9306dcf8079747469ea6d999d67f691e21f84` |
| `tests/test_installer_test.go` | `9ad228bd5ba0c5a04c4d01725bce85306102a08d697132a7b916d14dcf44e95e` |
| `.github/workflows/build.yml` | `a23981a16719346d158463b03e3208526f3ce4b36994b2a08df2554cb49396b3` |

Toolchain pins in the 5 identical workflows and build scripts: Python `3.15.2`, Go `1.27.4`, Node `26.13.0`, corepack `0.36.0`, `pnpm@12.16.1`, `github.com/pterm/pterm@v0.12.84`, `actions/checkout@v7.0.1`, `actions/setup-python@v7.1.0`, `actions/setup-go@v7.0.0`, `actions/setup-node@v7.1.0`, `actions/cache@v6.1.0`, `actions/github-script@v9.0.0`, `@actions/artifact@6.3.1`. Upstream `v0.2.25` needs no change to these pins.

## 12. Version reference catalog and scope classes

Search: `v?0.2.(20|23|24|25)` over the root repository and the 4 submodules, with `.git`, `dist`, and `.trellis/workspace` excluded.

### 12.1 Required code, patch, and test changes (Phase 2)

| File | Change | Reason |
| --- | --- | --- |
| `plugins/codex-candy-eval/patches/0004-admin-channel.patch` | 3 call sites use `ApplyHeaderOverrides(req.Context(), ...)` | Compile break on `v0.2.25` (section 7). |
| `plugins/sub2api-quota-extension/patches/quota-extension.patch` | Rebase 25 hunks in 9 files. Change 3 `ApplyHeaderOverrides` calls. | Apply failure and compile break (section 6). |
| `plugins/sub2api-quota-extension/tests/test_account_repo_quota_test.go` | 2 calls and 1 sqlmock row | The test uses the changed signature and the changed lock SELECT. |
| `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go` | 1 fixture signature | The fixture implements the changed interface. |

No change: the Gemini patch and tests, the template, `scripts/build.py`, `scripts/installer/*`, `tests/support.py`, `tests/test_build.py`, `tests/test_installer_test.go`, and `.gitmodules`.

### 12.2 `.github/workflows/build.yml` default `upstream_tag` (5 repositories)

`default: v0.2.24` is at line 11 in each of the 5 identical files: root repository, eval plugin, Gemini plugin, template, quota plugin. The change to `v0.2.25` is part of the cut-over. After the adaptation, the quota patch does not apply to `v0.2.24` and the eval patch does not compile on `v0.2.24`. A manual run with the old default then fails. Keep the 5 files byte-identical. Precedent: `5b813d9` (root workflow and spec) with the submodule commits `609f979`, `ccb2a98`, `d823e9c`, and `79a5f71`.

### 12.3 Documentation: user scope decision is necessary

`.trellis/spec/guides/index.md` states: "Do not create or modify documentation or manifest files unless the user explicitly requests them. Trellis-managed artifacts are exempt."

| File | Reference | State | Effect |
| --- | --- | --- | --- |
| Root `README.md` lines 22, 24, 28 to 32, 39, 40, 46, 124 | `v0.2.23` (11 places). Line 22 states that the default is `v0.2.23`. | Wrong before this task. `0e15db5` and `5b813d9` set the workflow default to `v0.2.24` and did not change the README. | Documentation. Needs an explicit user request. |
| `plugins/sub2api-plugin-template/README.md` line 17 | `UPSTREAM_TAG=v0.2.20 python3 scripts/build.py` | Stale example since 2026-11-19. The same README also states that a push triggers the build. The workflow triggers on `pull_request` and `workflow_dispatch` only. | Documentation. Needs an explicit user request. |
| `plugins/codex-candy-eval/tests/native_inspection_fixture.py` lines 48 to 51 | 4 hard-coded names `sub2api-plugins-v0.2.23-linux-{arch}` | Stale. The build does not run this file (no `test_` prefix). `resolve_built_binary` falls back to a glob and finds the current tag. | A manual browser-fixture helper. Not part of the build contract. User decision: leave it, replace the tag, or delete the 4 stale candidates. |

### 12.4 `.trellis/spec/` baseline statements (Phase 3.3, after verification)

| File | Line | Current text |
| --- | ---: | --- |
| `backend/index.md` | 6 | "The verified integration baseline is Sub2API v0.2.24." |
| `backend/quality-guidelines.md` | 7 | "Sub2API v0.2.24 is the verified integration baseline." |
| `backend/api-key-quota.md` | 5 | "... on Sub2API v0.2.24." |
| `backend/gemini-signature-rectifier.md` | 6 | "The verified integration baseline is Sub2API v0.2.24." |
| `backend/runtime-installation.md` | 5 | "Use this contract for the evaluation plugin on Sub2API v0.2.24." |
| `backend/minimal-linux-delivery.md` | 6, 16, 17, 35, 43, 316, 360 | `v0.2.24` baseline, example commands, and the workflow default statement |
| `backend/minimal-linux-delivery.md` | 78 | "The v0.2.23 source retains `0.2.22` in `backend/cmd/server/VERSION`." On `v0.2.25` the file contains `0.2.24`. |

Possible contract additions after verification: the behavior of header overrides with variables on evaluation and quota probe requests, and the quota save path if its design changes.

### 12.5 Do not change

`tests/test_installer_test.go` line 661 in the root repository and in each submodule: `fakeState{Installed: "0.2.17", Candidate: "0.2.20", Image: "sub2api:0.2.18"}`. These are synthetic values for the installer version check. They are not a baseline.

Untracked local build outputs (`dist/` is ignored by Git): eval plugin `dist/build/*/sub2api-plugins-*-v0.2.20-*`, Gemini plugin and quota plugin `*-v0.2.24-*`, root repository `dist/build/*/sub2api-plugins-*-v0.2.24-*` (2026-11-22 02:15). They are not references in tracked files.

## 13. CI exposure

The root workflow runs on `pull_request` and `workflow_dispatch` only. A pull-request run has an empty `UPSTREAM_TAG`. `resolve_upstream_tag()` then reads `releases/latest`, which is now `v0.2.25`. Result at the current `HEAD`:

| Repository | Pull-request build on `v0.2.25` | First failure |
| --- | --- | --- |
| Root repository | Fails (inference from section 5) | "Download and patch source": `Patch failed: sub2api-quota-extension/quota-extension.patch` |
| Eval plugin | Fails (compile evidence in section 7) | The first Go test entry does not compile `internal/service` |
| Quota plugin | Fails (section 5) | "Download and patch source" |
| Gemini plugin | Expected to pass (compile evidence in section 7. No run.) | None |
| Template | Expected to pass (no patch. No run.) | None |

Public run history of the root repository (unauthenticated API): the latest run is `44943905201`, `Build v0.2.24 · main`, `workflow_dispatch`, success, 2026-11-21T20:00:11Z, `ba049b4`. The repository has no open pull request. No run used `v0.2.25` at the audit time.

## 14. Working-tree observations (they exist before this audit, user-owned)

- `git status --short` at the start and at the end: ` M plugins/gemini-signature-rectifier`, `?? .trellis/tasks/11-25-adapt-plugins-v0-2-25/`, `?? .vscode/`.
- The root repository records the gitlink `ccb2a98` for `plugins/gemini-signature-rectifier`. The checkout and the remote `main` are at `406df21` (`docs: remove misleading README.`, it deletes `README.md`). CI checks out `ccb2a98`. The difference is one README file, so the build result is the same.

## 15. Not verified in this audit

- Frontend type-check, i18n completeness check, Vitest, and Vite build on the patched `v0.2.25` tree.
- Execution of the plugin Go tests and Vue tests.
- The quota plugin after the rebase (the patch does not apply in full).
- Runtime and browser checks. Upstream changed the layout of the `AccountsView` name cell.
- CI runs on GitHub.

## 16. Method

- Upstream inspection: `git clone --filter=blob:none --no-checkout https://github.com/Wei-Shaw/sub2api.git` and `git worktree add --detach` for each scenario. Environment for each command: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 git -c credential.helper=`.
- Public API: `curl -fsSL` with an `Accept` header and a `User-Agent` header only.
- Python: `PYTHONDONTWRITEBYTECODE=1 python3 -B` with the script on standard input.
- Private directory: `/tmp/sub2api-omp-audit-kxHcG6`. Cleanup record: section 17.

## 17. Cleanup record

- The environment blocks direct deletion of files without Git records. It names `/usr/bin/trash` as the permitted method.
- Step 1: `GOCACHE=<private directory>/gocache go clean -cache` removed the Go build cache. The directory went from 3.5 GB to 926 MB.
- Step 2: `/usr/bin/trash /tmp/sub2api-omp-audit-kxHcG6` returned 0. `/tmp/sub2api-omp-audit-kxHcG6` does not exist. No `/tmp/sub2api-omp-audit-*` path remains.
- The directory content is in the macOS Trash. It is not erased. The audit could not read `~/.Trash` to report its size. Empty the Trash to erase it.
- Checks after the compile runs found 0 changed files in the user Go module cache, the Go build cache, and the Go telemetry directory.
- `git status --short` of the root repository is unchanged: ` M plugins/gemini-signature-rectifier`, `?? .trellis/tasks/11-25-adapt-plugins-v0-2-25/`, `?? .vscode/`. The 4 submodules have no change. No `__pycache__` exists under the repository.
- Files written by this audit: this record and `omp-plan-audit.md` in the Antigravity scratch directory. No subagent was started. `gh` was not used.
