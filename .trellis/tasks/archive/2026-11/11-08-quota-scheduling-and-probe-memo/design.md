# Technical Design: Sub2API v0.2.23 Adaptation, Model-Control Defaults, Quota Scheduling, Probe Memoization, Identity CAS, and SIWC Admission

## Active Sub2API v0.2.23 and Model-Control Design

Sub2API `v0.2.23` (tag `ce19a640eab5c4b5ef1827c7c1fcfce49569411a`, peeled commit `5af9afb588c4b014b3df9db7d4073af1f8ae01b6`) supersedes `v0.2.21` as the verified delivery target.
All simplified quota persistence, narrow inspection persistence, native sender reuse, and SIWC page admission contracts remain unchanged.
Add no wrapper types, compatibility shims, or runtime version branches.

### 1. Upstream v0.2.23 Adaptation Boundaries

| Boundary | Verified upstream fact | Adaptation design |
| --- | --- | --- |
| Go toolchain and `go.mod` | `backend/go.mod:3` bumps `go 1.27.3` to `1.27.4` (`Dockerfile:11` matches). Commit `e0cf4984` moves `jsonschema-go v0.4.2` to direct `require` at line `26`. | Repair `quota-extension.patch` `backend/go.mod` Hunk #4 context around `github.com/google/pprof`. Update `go-version` to `"1.27.4"` in parent, quota, and evaluation `.github/workflows/build.yml:73`. |
| `AccountUsageCell.vue` imports and cache | Commit `e6774625` imports `formatDateTime` at line `774` and calls `_usageCache.set(accountID, { data: result, ts: Date.now() })` inside `loadActiveUsage` at line `1659`. Commit `17724301` keeps Gemini usage visible during refetch. | Repair `quota-extension.patch` Hunk #3 context to retain `formatDateTime`. In `loadActiveUsage`, capture `const config = apiKeyUsageRefreshKey.value` before the active request and store `{ data: result, ts: Date.now(), config }` (verified `exit 0` with `vue-tsc --noEmit`). |
| `AccountRepository`, Wire DI, scheduler cache | Upstream adds `ClearModelRateLimit` (`account_service.go:113`), `UsageBillingLaneCombiner` (`wire.go:1000`), `GetSnapshotValues`, `"openai_passthrough_model_filter"`, and `UsageProgress.UtilizationUnknown`. | Zero symbol or signature conflict; standalone and combined Go package compile checks exited `0`. Refresh `quota-extension.patch` against clean `v0.2.23`. |
| Evaluation model-control default removal list | `gpt-6.1-terra` already exists in the 5-item default at `0005-inspection.patch:941`; `gpt-6.2-sol` is absent. Upstream `v0.2.23` natively supports both models (`useModelWhitelist.ts:13-16`, `openai/constants.go:22-34`). Server `DefaultInspectionSettings` is the sole default owner (`0006-evaluation-ui.patch` initializes `[]` and hydrates from server). | Append `"gpt-6.2-sol"` to `DefaultInspectionSettings` at `0005-inspection.patch:941` (`["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra", "gpt-6.2-sol"]`), `tests/test_service_codex_inspection_settings_test.go:105`, `tests/test_ui.cjs:19`, and `.trellis/spec/backend/native-inspection.md:58`. Keep ordering, deduplication, and explicit `[]` handling unchanged. |
| Delivery defaults, README, and specs | Workflows, `README.md`, `native_inspection_fixture.py`, and `.trellis/spec/backend/` still cite `v0.2.21` (and embedded `0.2.20` at `minimal-linux-delivery.md:77`). | Update workflow `upstream_tag` defaults and active docs/specs to `v0.2.23`, and update `minimal-linux-delivery.md:77` to record embedded `0.2.22` in `backend/cmd/server/VERSION`. |

### 2. Retained Simplified Architecture

- **Quota persistence (`plugins/sub2api-quota-extension/patches/quota-extension.patch`)**:
  - `UpdateAPIKeyQuotaState(ctx, account, usage, expiresAt, unsupportedIdentity)` locks the proxy (`FOR SHARE`) and current account `extra` (`FOR NO KEY UPDATE` matching platform, type, credentials JSON, `proxy_id`, and normalized `quota_script`), merges partial balance (`apikey_quota_balance_exhausted`) and window sources, writes one conditional SQL `UPDATE` with `IS DISTINCT FROM` guards, updates `updated_at` only when `expires_at` changes, enqueues `scheduler_outbox` only when scheduling or expiry changes, and mutates caller memory only after commit.
  - Ordinary saves (`UpdateWithAccountBillingSettings(..., previousExpiresAt ...*time.Time)`) merge managed quota keys and preserve unedited `expires_at` inside the single native locked read and Ent update transaction.
  - Single and bulk identity or `quota_script` edits strip managed keys via JSONB `- '<key>'` and clear only `apikey_quota_%` pauses.
  - Include `APIKeyQuotaBalanceExhaustedExtraKey` in `duplicateAccountDiscardedExtraKeys` (`admin_account.go`) so all 13 managed keys match.
- **Evaluation persistence and SIWC UI (`plugins/codex-candy-eval`)**:
  - `PersistCodexInspectionVerdict` writes exclusively through narrow conditional `UpdateCodexInspectionState`, preserving concurrent credentials, status, priority, quota keys, and participation opt-outs.
  - Native Gemini builders, Anthropic stream finalization, and Antigravity API-key Gemini/Claude routing remain owned by upstream helpers.
  - `patches/0006-evaluation-ui.patch` passes `prefix` through eligibility helpers so only `siwc-` ignores local `rate_limit_reset_at` for row, selection, select-all, refresh retention, and batch actions while retaining the displayed rate-limit label and Candy/Fingerprint/Pelican restrictions.

### 3. Change Ownership and Rollback

- One `hc` implementation worker updates both plugins, workflow defaults, `README.md`, and `.trellis/spec/backend/`, exports clean `v0.2.23` diffs, and runs verification.
- Save current `v0.2.21` staged diffs under `/tmp/sub2api-v0.2.21-rollback-*.patch` before editing so rollback is exact.
- Reuse clean upstream `/tmp/sub2api-v0.2.23-research` for patch export and standalone checks; run `UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py` once for final five-platform build and test verification.
- Keep `plugins/sub2api-plugin-template`, `.vscode/`, and synthetic `0.2.20` installer warning fixtures untouched.
