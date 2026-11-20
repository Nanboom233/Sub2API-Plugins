# Architectural Redesign Brief: Follow Upstream v0.2.24 Unified Refresh Key Architecture

Target task: `.trellis/tasks/11-21-adapt-sub2api-v0224` (status: `planning`)
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any internal subagent from running `hc send`.

## Directive

The user rejected the dual-key (`{ data, ts, refreshKey, config }`) design as redundant:
> "太冗余 你应该跟随上游的优化做架构上的优化"

Do **NOT** bolt a parallel `config` cache key, parallel `apiKeyUsageRefreshKey` computed, parallel `capturedConfigByAccountId` map, or parallel config-invalidation watcher onto upstream `v0.2.24`'s unified refresh-key system.
Instead, **align the quota plugin directly onto upstream `v0.2.24`'s unified `buildAccountUsageRefreshKey` + single `refreshKey` cache architecture**, shrinking `quota-extension.patch` instead of expanding it.

Planning-only boundary still applies:
- Do **NOT** run `task.py start`.
- Do **NOT** edit any plugin patch, code, test, spec, or Git state.
- Do **NOT** use `gh` or authenticated GitHub credentials.

## Factual Inspection Required (Zero Guessing)

Inspect pristine public `Wei-Shaw/sub2api@v0.2.24` (`5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`) for exact source lines in:
1. `frontend/src/utils/accountUsageRefresh.ts` (`buildAccountUsageRefreshKey` and every helper/export)
2. `frontend/src/components/account/AccountUsageCell.vue` (`_usageCache`, `usageRefreshKey`, `watch(usageRefreshKey, ...)`, `loadUsage` / `requestAutoLoad` / `requestParentBatchUsage`, stale response guards)
3. `frontend/src/views/admin/AccountsView.vue` (`usageBatchCache`, `capturedRefreshKeyByAccountId`, batch response write & cache reuse, `shouldReplaceAutoRefreshRow`, row invalidation)
4. Local repo search across ALL files (`rg buildAPIKeyUsageRefreshKey`) to confirm every consumer of `buildAPIKeyUsageRefreshKey` (and `usageBatchRequestTokenByAccountId`, etc.).

## Architectural Unification Target

Verify and design the cleanest possible unification onto upstream `v0.2.24`:

1. **`frontend/src/utils/accountUsageRefresh.ts`**:
   - Plug `account.type === 'apikey'` **directly into upstream `buildAccountUsageRefreshKey(account)`** (returning the deterministic API-key config snapshot key: `id`, `platform`, `script`, `base_url`, `api_base_urls`, `api_protocol`, `api_key`, `header_override_enabled`, `header_overrides`, `proxy_id`, `enable_tls_fingerprint`, `tls_fingerprint_profile_id`, `updated_at`).
   - Delete the redundant standalone `buildAPIKeyUsageRefreshKey` export if nothing outside our own quota patch & tests uses it (check all references first; do not leave dead or pass-through wrappers!).
   - Keep `hasQuotaScript` (still needed for script-only error visibility / eligibility).

2. **`frontend/src/components/account/AccountUsageCell.vue`**:
   - Keep upstream's exact `_usageCache` entry shape `{ data, ts, refreshKey }` — **NO** `config` field!
   - Keep upstream's exact single `usageRefreshKey` computed (`buildAccountUsageRefreshKey(props.account)`) — **NO** `apiKeyUsageRefreshKey` computed!
   - Reuse upstream's single `watch(usageRefreshKey, ...)`: check exact upstream watcher body in `v0.2.24`; for `account.type === 'apikey'`, join the exact upstream invalidation/force-refresh branch (clearing `usageInfo`/`error`, deleting `_usageCache` entry, bumping `usageRequest`, forcing reload so edited API-key credentials/script refresh immediately without a second watcher!).
   - Verify stale-response guard in `loadUsage` / async apply using ONLY upstream's already-captured `refreshKey` (and existing `usageRequest` / `account.id` / mount checks) — ZERO parallel `config` capture!

3. **`frontend/src/views/admin/AccountsView.vue`**:
   - Keep upstream's exact `usageBatchCache` shape `{ data, ts, refreshKey }` — **NO** `config` field!
   - Keep upstream's exact `capturedRefreshKeyByAccountId` map — **NO** `capturedConfigByAccountId` map!
   - Check whether upstream `v0.2.24` already checks `capturedRefreshKey === buildAccountUsageRefreshKey(currentAccount)` on batch write (or if adding a 1–3 line stale-key check against `capturedRefreshKeyByAccountId` eliminates `apiKeyUsageRefreshKeys` watcher and `usageBatchRequestTokenByAccountId` completely — verify exact `v0.2.24` batch flow first, including what happens when an API-key account's config changes while a batch request is in flight and when a cached entry exists!).
   - Because `shouldReplaceAutoRefreshRow` ALREADY compares `buildAccountUsageRefreshKey`, API-key config changes automatically trigger row replacement with **ZERO** extra patch lines!

4. **Check if ANY other `v0.2.24` upstream optimization simplifies `quota-extension.patch`**:
   - Check `account_usage_service.go`, `account_repo.go`, `scheduler_cache.go`, `AccountUsageCell.vue`, `AccountsView.vue`, `UpstreamQuotaUsage.vue`, `UsageProgressBar.vue` — if upstream `v0.2.24` introduced any helper or structure that lets us delete redundant plugin patch code cleanly, note and include it; do NOT touch unrelated working backend code without a concrete simplification or conflict.

5. **Quantify net patch simplification & update planning docs**:
   - Rewrite `.trellis/tasks/11-21-adapt-sub2api-v0224/{prd.md,design.md,implement.md}` and update `research/v0224-upstream-diff.md` to reflect the unified single-`refreshKey` architecture.
   - Report expected hunk/line reduction in `quota-extension.patch` (current `AccountUsageCell.vue` + `AccountsView.vue` + `accountUsageRefresh.ts` hunks vs unified single-key hunks).
   - Keep `implement.jsonl` and `check.jsonl` aligned (including `.trellis/spec/frontend/hook-guidelines.md` and `state-management.md` for later Phase 3.3 spec sync).
   - Keep `test_usage_cell.test.ts` (and check whether batch test should be a tiny focused test file or lean suite without redundant boilerplate — no over-engineered mock harnesses!).
   - Verify all JSONL entries and local markdown links pass.

## Final Callback

Report concisely via `hc send t53` with:
- Exact architectural simplification achieved (what parallel fields/maps/watchers/exports are eliminated and estimated hunk/line reduction).
- Exact verification of how stale in-flight single/batch responses and cache invalidation work under the single unified `refreshKey` (citing exact `v0.2.24` line numbers).
- Confirmation that `prd.md`, `design.md`, `implement.md`, `research/v0224-upstream-diff.md`, `implement.jsonl`, and `check.jsonl` are updated and zero production/test/Git files changed.
