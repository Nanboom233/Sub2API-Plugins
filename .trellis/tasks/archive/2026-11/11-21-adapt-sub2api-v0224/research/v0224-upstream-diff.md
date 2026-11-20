# Sub2API v0.2.24 plugin audit

Audit date: 2026-11-21. This record covers static research only.
No product patch, code, test, specification, or Git state changed. No build or test ran during this audit.

## Sources and complete comparison

- [Public comparison API](https://api.github.com/repos/Wei-Shaw/sub2api/compare/5af9afb588c4b014b3df9db7d4073af1f8ae01b6...5c2982a81b46e2142d0143d2f83c1ce9c4da1d24)
- [Per-commit patch series](https://github.com/Wei-Shaw/sub2api/compare/5af9afb588c4b014b3df9db7d4073af1f8ae01b6...5c2982a81b46e2142d0143d2f83c1ce9c4da1d24.patch)
- Tagged source archives: [v0.2.23](https://codeload.github.com/Wei-Shaw/sub2api/tar.gz/refs/tags/v0.2.23), [v0.2.24](https://codeload.github.com/Wei-Shaw/sub2api/tar.gz/refs/tags/v0.2.24)
- Previous failed build: [/tmp/gemini-single-shot-build.log](/tmp/gemini-single-shot-build.log)

The endpoints resolve to `5af9afb588c4b014b3df9db7d4073af1f8ae01b6` and `5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`.
The comparison contains 110 ancestry commits: 65 content commits and 45 merge commits. It lists 190 changed files.
The patch series contains all 65 content commits. Every aggregate changed path occurs in that series.
The three plugins patch 97 distinct paths. Sixteen paths intersect the aggregate upstream changes.

| Plugin | Patched paths | Changed upstream paths | Adaptation decision |
| --- | ---: | ---: | --- |
| `sub2api-quota-extension` | 33 | 11 | Unify both Vue targets through the native refresh utility. |
| `codex-candy-eval` | 56 | 0 | Keep patches and tests unchanged. |
| `gemini-signature-rectifier` | 10 | 5 | Keep patches and tests unchanged. Native recovery remains separate. |

## Commits that change plugin targets

These eleven content commits contain every changed plugin target.
The merge column identifies the integrating PR merge. The comparison API retains the complete 110-commit ancestry.

| Content commit | Change | Intersecting targets | Integrating merge |
| --- | --- | --- | --- |
| [bf292550](https://github.com/Wei-Shaw/sub2api/commit/bf292550a6d45088c46dd0792d9bffddb2c65e92) | Add Exa provider | `frontend/src/api/admin/settings.ts`, `frontend/src/views/admin/SettingsView.vue` | [fb60f041 / #8801](https://github.com/Wei-Shaw/sub2api/commit/fb60f041730f64c4d50d4811f1e416faf3b3f506) |
| [e2631bbb](https://github.com/Wei-Shaw/sub2api/commit/e2631bbb385a8fa04a7b006678417713600aa270) | Compaction TTL hint | `frontend/src/i18n/locales/{en,zh}/admin/settings.ts` | [30270019 / #8794](https://github.com/Wei-Shaw/sub2api/commit/3027001928870a71160ac68e8a3001208a3ef790) |
| [fa796b30](https://github.com/Wei-Shaw/sub2api/commit/fa796b309a613785396a0c658b710ba8c13b3a1f) | Refresh Claude and Gemini snapshots | `frontend/src/components/account/AccountUsageCell.vue`, `frontend/src/utils/accountUsageRefresh.ts`, `frontend/src/views/admin/AccountsView.vue` | [29d9fe2a / #8858](https://github.com/Wei-Shaw/sub2api/commit/29d9fe2ad0e091c104a24e916ff708ec057570cf) |
| [fb52c6e1](https://github.com/Wei-Shaw/sub2api/commit/fb52c6e136a9401d5c078bade0533b32715706f7) | Preserve rotated OpenAI credentials | `backend/internal/repository/account_repo.go` | [c38a534b / #8671](https://github.com/Wei-Shaw/sub2api/commit/c38a534be9a2e9600084b5f514badad828886958) |
| [18c42a29](https://github.com/Wei-Shaw/sub2api/commit/18c42a29d2edb2e314eef5115021fe33b7fa5af6) | Compact scheduler groups | `backend/internal/repository/scheduler_cache.go` | [84a29305 / #8845](https://github.com/Wei-Shaw/sub2api/commit/84a293056a000715b38f66ad41b6f8b2484fc32e) |
| [77ba3346](https://github.com/Wei-Shaw/sub2api/commit/77ba3346d1ae9aa3930dc1b347d05582e1bae93d) | Filter foreign OAuth models | `backend/internal/service/account.go` | [fe2d953f / #8893](https://github.com/Wei-Shaw/sub2api/commit/fe2d953f528ae05fd6fca494431a096fa6272d7e) |
| [f358f0a4](https://github.com/Wei-Shaw/sub2api/commit/f358f0a41a03c44230e6374e9e387d822047a9a0) | Estimate Claude window cost | `backend/internal/service/account_usage_service.go`, `frontend/src/components/account/AccountUsageCell.vue` | [88ff563f / #8900](https://github.com/Wei-Shaw/sub2api/commit/88ff563f7365dc55ff74b087bb43fa0a9e7018f9) |
| [65be2778](https://github.com/Wei-Shaw/sub2api/commit/65be27787cae797efb15af62a048215bf74f6cce) | Warn about repeated manual token refresh | `frontend/src/views/admin/AccountsView.vue`, `frontend/src/i18n/locales/{en,zh}/admin/accounts.ts` | [2f49048c / #8902](https://github.com/Wei-Shaw/sub2api/commit/2f49048cb80a8883df597bcfc4c66787d9662ed2) |
| [75290a9f](https://github.com/Wei-Shaw/sub2api/commit/75290a9f26e554db29bd06422f4dd5f2a196e7f0) | Omit rejected test temperature | `backend/internal/service/account_test_service.go` | [69237d2e / #8911](https://github.com/Wei-Shaw/sub2api/commit/69237d2ebd166674739b8ee5e6a343d0f3f635b4) |
| [a4b72bef](https://github.com/Wei-Shaw/sub2api/commit/a4b72bef0977b9174fd4c3cc19a8ad055649145c) | Initialize user platform quotas | `backend/cmd/server/wire_gen.go`, `frontend/src/i18n/locales/{en,zh}/admin/settings.ts` | [a912d13e / #8918](https://github.com/Wei-Shaw/sub2api/commit/a912d13e62514cd4d6233126da0cd77bef901d2b) |
| [44db3dd7](https://github.com/Wei-Shaw/sub2api/commit/44db3dd72b99467776be3db188be27767bc6b54d) | Keep trailing Parts outside the final tool-result turn | `backend/internal/service/gemini_messages_compat_service.go` | [16b67d9a / #8923](https://github.com/Wei-Shaw/sub2api/commit/16b67d9afd0f268ac46ef42a0c7dca15cd36d407) |

### Merge ancestry audit

All 45 merge commits were checked against their first parent through public commit metadata or complete recursive trees.
Sixteen merge diffs intersect plugin paths. Eleven are the integrating merges already listed above.
Five additional branch-sync merges intersect plugin paths before their branches join the release:

| Merge | Plugin-path intersections relative to its first parent |
| --- | --- |
| [e5e1162f](https://github.com/Wei-Shaw/sub2api/commit/e5e1162f424b09d037af65160f56f0d2a0afc4d9) | Shared twenty-path set below |
| [baf058f6](https://github.com/Wei-Shaw/sub2api/commit/baf058f645a29c397a2062c822c425f3db4264fc) | `frontend/src/types/index.ts` |
| [6d4fcbad](https://github.com/Wei-Shaw/sub2api/commit/6d4fcbad47d3e0a133296a713502a6823a06e618) | Shared twenty-path set below |
| [2cf2c332](https://github.com/Wei-Shaw/sub2api/commit/2cf2c33226947aea382e5809916a936319ec0400) | Shared twenty-path set below |
| [3eca473a](https://github.com/Wei-Shaw/sub2api/commit/3eca473aa152dc5cd798a751ae7a0615c4ff0408) | Shared twenty-path set below |

The shared set contains these exact paths:

```text
backend/cmd/server/wire_gen.go
backend/go.mod
backend/internal/repository/account_repo.go
backend/internal/repository/http_upstream.go
backend/internal/repository/scheduler_cache.go
backend/internal/service/account.go
backend/internal/service/account_scheduling_threshold_eval.go
backend/internal/service/account_service.go
backend/internal/service/account_test_service.go
backend/internal/service/account_usage_service.go
backend/internal/service/gemini_messages_compat_service.go
backend/internal/service/wire.go
backend/internal/web/embed_on.go
frontend/src/components/account/AccountUsageCell.vue
frontend/src/components/account/CreateAccountModal.vue
frontend/src/components/account/EditAccountModal.vue
frontend/src/components/account/UsageProgressBar.vue
frontend/src/i18n/locales/en/admin/accounts.ts
frontend/src/i18n/locales/zh/admin/accounts.ts
frontend/src/types/index.ts
```

These merges import existing mainline changes into older feature branches. Their parent-relative changes exceed the final tag delta.
For example, `http_upstream.go`, `embed_on.go`, `go.mod`, and `types/index.ts` have no net difference between the two tags.
Do not infer a released eval or toolchain change from these branch-relative diffs.
The eleven content commits and sixteen merge commits above exhaust all ancestry commits with plugin-path intersections.
The final sixteen-path tag delta determines adaptation scope.

Public `.diff` downloads for the merge audit returned HTTP/2 errors and HTTP 503.
The public commit API succeeded. Three 300-file responses required complete, untruncated recursive-tree comparisons.
Those tree identities served source comparison only. No local Git repository or state changed.

## Exact quota conflict causes

The observed failure is an application failure, before compilation or tests.
The eval and Gemini patches applied in that attempt. The quota patch failed atomically on two Vue targets.
Source links below refer to pristine tags. Patch line references refer to the current repository file.

### AccountUsageCell.vue

[Old lines 769–774](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/components/account/AccountUsageCell.vue#L769)
and [new lines 772–777](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/frontend/src/components/account/AccountUsageCell.vue#L772):

```diff
-import { buildOpenAIUsageRefreshKey } from '@/utils/accountUsageRefresh'
+import { buildAccountUsageRefreshKey } from '@/utils/accountUsageRefresh'
```

The quota patch expects the removed import at its line 2260.
It also replaces the old cache declaration and cache reads/writes at lines 2276 and 2318–2365.
Upstream now requires `refreshKey: string` in each cache entry and compares that key before reuse.
Its watcher now observes `usageRefreshKey`, rather than `openAIUsageRefreshKey`.
The plugin watcher insertion also uses the old watcher as context at patch line 2367.
Changing only the import context would leave further application conflicts and incompatible cache writes.

Exact cache context:

```diff
-const _usageCache = new Map<number, { data: AccountUsageInfo; ts: number }>()
+const _usageCache = new Map<number, { data: AccountUsageInfo; ts: number; refreshKey: string }>()
```

Upstream captures `usageRefreshKey.value` before single and active requests and stores it with each result.
Its reply guards do not compare that captured key with the current key.
Extend the native utility with the API-key configuration branch. Use that one key for cache reuse and reply checks.
The same utility keeps native Claude/Gemini snapshot branches. Claude snapshot refreshes retain the passive source.
Remove the plugin's separate computed key and watcher. Keep its request-order counter and captured account ID.

Upstream also adds estimated-cost props to Claude 5h/7d bars and passes 7d `window_stats`.
It generalizes the cost calculation helper. Keep these template and script changes intact.

### AccountsView.vue

[Old line 531](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/views/admin/AccountsView.vue#L531)
and [new line 531](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/frontend/src/views/admin/AccountsView.vue#L531):

```diff
-import { buildGrokUsageRefreshKey, buildOpenAIUsageRefreshKey } from '@/utils/accountUsageRefresh'
+import { buildGrokUsageRefreshKey, buildAccountUsageRefreshKey } from '@/utils/accountUsageRefresh'
```

The quota patch expects the removed import at line 2828.
Both versions also change `usageBatchCache`, the batch response write, and the cache reuse predicate.
Upstream captures unified refresh keys in the map named `refreshKeys` at line 804.
The brief names that map `capturedRefreshKeyByAccountId`. Keep the actual native name and add no second map.
Remove the plugin's `configs` map, configuration cache fields, and configuration watcher.
Add a current-account/key check beside each native request-token check. Keep the native tokens for same-key request ordering.

Upstream incremental row replacement now uses `buildAccountUsageRefreshKey`, preserving Claude/Gemini snapshot updates.
Keep that comparison and the existing Grok comparison. Do not restore the OpenAI-only comparison.
Upstream also adds a 60-second repeated-token-refresh warning. It warns without blocking the action.
Retain its locale keys, warning state, and handler behavior.

## Other quota intersections

| Upstream target | Tagged change | Quota impact |
| --- | --- | --- |
| `backend/cmd/server/wire_gen.go` | Add `serviceUserPlatformQuotaRepository` to `NewAdminService` | Quota modifies the account usage/test providers elsewhere. Preserve the new admin argument. |
| `backend/internal/repository/account_repo.go` | Add OpenAI OAuth conditional credential update through a shared private helper | Quota transaction and managed-key hunks target other functions. Existing signatures remain usable. |
| `backend/internal/repository/scheduler_cache.go` | Remove expanded groups from serialized account payload | Quota extends `filterSchedulerExtra`. Preserve both independent changes. |
| `backend/internal/service/account.go` | Reject foreign models for OAuth-like passthrough accounts | Quota extends exhaustion checks elsewhere. Preserve native model selection. |
| `backend/internal/service/account_test_service.go` | Omit temperature for rejecting Claude models and extract Bedrock payload helper | Quota changes the constructor, not these payloads. No fixture change follows from this delta. |
| `backend/internal/service/account_usage_service.go` | Separate 5h/7d local cost caches and validate current reset windows | Public usage fields and constructor remain compatible. Preserve native cost sampling. |
| `frontend/src/i18n/locales/en/admin/accounts.ts` | Add repeated-refresh warning text | No collision with quota keys. |
| `frontend/src/i18n/locales/zh/admin/accounts.ts` | Add matching warning text | Keep locale parity. |
| `frontend/src/utils/accountUsageRefresh.ts` | Add `buildAccountUsageRefreshKey` | Add the API-key branch inside this function. Remove the separate plugin builder. |

The backend changes provide no replacement for quota transport, persistence, or scheduling.
The OpenAI credential helper does not replace quota locks or conditional updates.
Scheduler group compaction does not replace quota fields in `filterSchedulerExtra`.
The native cost caches do not replace quota requests or their scheduling rules.
Keep these independent backend hunks unchanged.

`UpstreamQuotaUsage.vue` is a plugin-created component. Upstream provides no replacement.
`UsageProgressBar.vue` has no tag-to-tag change. Its quota reset-tooltip hunk remains necessary.
The concrete simplification is limited to the two usage owners and their shared utility.

## Unified refresh key and response ownership

All line numbers below refer to pristine `v0.2.24` source.

### Shared utility and consumer inventory

[accountUsageRefresh.ts](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/frontend/src/utils/accountUsageRefresh.ts#L73)
exports OpenAI, Grok, and unified account builders at lines 32, 55, and 73.
The serializer at lines 8–26 sorts object keys and omits undefined object values.
The unified builder delegates OpenAI at line 74 and handles Claude/Gemini snapshots at lines 76–97.

Insert the API-key branch before line 74. Extend its `Pick<Account, ...>` with `credentials` and `proxy_id`.
Reuse the existing serializer with this API-key snapshot:

```text
id, platform, script, base_url, api_base_urls, api_protocol, api_key,
header_override_enabled, header_overrides, proxy_id,
enable_tls_fingerprint, tls_fingerprint_profile_id, updated_at
```

Keep `updated_at` because saved API keys are redacted. Keep the native non-API-key branches unchanged.
The API-key branch must precede OpenAI delegation, which returns an empty key for OpenAI API-key accounts.

A repository-wide `rg --hidden --no-ignore` search found production helper references only in `quota-extension.patch`.
They are the standalone export, cell import/computed value, and view import/map/cache predicate/watcher.
The other references occur in three current specifications, this task, and archived research/context records.
The tests have no direct helper import. Delete `buildAPIKeyUsageRefreshKey` without a compatibility wrapper.
Keep `hasQuotaScript` for query eligibility and visible script errors.

### Cell cache, requests, and one watcher

| Native location | Verified behavior | Planned adaptation |
| --- | --- | --- |
| Cell line 796 | Cache stores `{ data, ts, refreshKey }`. | Keep this shape without a `config` field. |
| Line 950 | One computed `usageRefreshKey` calls the unified utility. | Keep it. Remove the plugin computed key. |
| Lines 1575–1587 | Cache reuse checks TTL and current key. The request captures `refreshKey`. | Keep both native operations. |
| Lines 1594–1604 | Single replies check mount state only. | Add request-order, account-ID, and captured-key checks before result/error updates. |
| Lines 1658–1675 | Active replies capture ID/key but check only mount/ID. | Compare the captured key on success and error. Keep independent active-button cleanup. |
| Lines 1841–1852 | One watcher handles native batch/passive routing. | Extend this watcher for API keys. Remove the separate plugin watcher. |

For API-key changes, advance `usageRequest`, delete the cell cache entry, and clear usage/error before the eligibility return.
Force one parent batch request when the row uses batching.
Otherwise, call existing `loadUsage({ bypassCache: true })` once when the row qualifies.
This explicit configuration refresh must run immediately, including outside the mobile viewport.
Keep ordinary mount/snapshot lazy loading at lines 1618–1627 unchanged.
Preserve passive Claude and non-forced Gemini routes in the native watcher.

Use the existing captured `refreshKey`, account ID, mount state, and `usageRequest` for single-request ownership.
Reject an old success or error after a key change. Let only the current automatic request change its loading state.
Active requests retain their separate `activeQueryLoading` cleanup. Add no automatic-request counter dependency to that button.
No separate configuration capture is needed.

### Batch cache and races

[AccountsView.vue lines 800–896](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/frontend/src/views/admin/AccountsView.vue#L800)
capture `refreshKeys` at line 804 and request tokens at lines 810–813.
Success lines 825–839 and failure lines 847–854 check tokens but omit the current-account/key check.
The cache write at line 835 already stores the captured unified key.
The cache predicate at line 873 already compares the current unified key and TTL.

In both response loops, find the current account and compare its key with `refreshKeys.get(accountID)`.
Skip removed accounts and changed keys before any usage, cache, error, or loading mutation.
Keep native `usageBatchRequestTokenByAccountId`, declared at line 749.
The queue advances tokens at lines 884–887. Native row removal prunes them at lines 1384–1398.
Tokens distinguish overlapping requests with the same key, including manual refreshes and changes from A to B and back to A.
A key comparison alone cannot reject those older replies.

The single child watcher forces changed API-key rows into the existing batch queue.
That queue deletes the affected cache entry and advances the native token.
A reply before the child callback fails the new current-key check.
A later reply also fails the token check after the new request enters the queue.
An old cached entry fails the native key predicate even before forced invalidation.
Unchanged accounts keep their cache entries and existing request ownership.
These checks replace the plugin's parent configuration watcher without a second key map.

`shouldReplaceAutoRefreshRow` already compares the unified key at line 1439 and Grok key at line 1440.
The utility extension makes API-key configuration changes visible to this existing row-replacement path.
Add zero patch lines to that function. Retain native queue coalescing and force aggregation.

### Expected patch reduction

The current patch contains these exact counts for the three affected targets.
Changed lines count additions plus removals. They exclude context and patch headers.
The unified counts are planning estimates, not an exported candidate diff.

| Target | Current hunks | Current additions/removals | Current changed lines | Expected unified hunks | Expected changed lines |
| --- | ---: | --- | ---: | ---: | ---: |
| `AccountUsageCell.vue` | 12 | 48 / 14 | 62 | 10–11 | 57–62 |
| `AccountsView.vue` | 8 | 19 / 4 | 23 | 5 | 9–10 |
| `accountUsageRefresh.ts` | 1 | 25 / 0 | 25 | 2 | 26 |
| **Total** | **21** | **92 / 18** | **110** | **17–18** | **92–98** |

Expect 3–4 fewer hunks and 12–18 fewer changed lines across these targets.
The utility moves its snapshot into the native builder and extends the parameter type.
The cell removes redundant cache/computed/capture edits and combines active reply checks into one hunk.
The view removes five configuration hunks and adds two small reply-check hunks.
The estimate includes both success/error guards and immediate API-key refresh.
Phase 2 must record the actual exported counts. Do not claim these estimates as build or test evidence.

## Tests and visible changes

Extend `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts` for native snapshots and the single unified cache key.
Retain existing API-key saved-key, script-change, stale-response, display, and manual-refresh assertions.
Add a small flat batch-usage suite for the changed `AccountsView` reply contract.
Reuse native mocks from `frontend/src/views/admin/__tests__/AccountsView.lite.spec.ts`.
Use the real usage cell for configuration changes. Stub unrelated layout and modals only.
Check old-key cache misses, unchanged-account hits, old success/error rejection, and same-key request ordering through the real view.
Check one request per configuration change. Add no shared mock framework or duplicate native token-warning tests.
Keep the shared editor suite and Go suites unchanged unless Phase 2 reveals a concrete failure.
The quota plugin currently has no README. There is no existing README baseline text to update.

The changes affect rendered Claude window statistics and estimated total costs.
The table keeps its existing structure, but stale-cache errors could hide current usage.
Phase 2.2 must inspect the actual built account table in Chromium with synthetic native and custom-quota rows.
Include both locales and themes, readable cost text, reset tooltips, zero-balance display, and refresh behavior.

## Specification synchronization after verification

Phase 3.3 should update verified-baseline statements in these backend guides:
`index.md`, `quality-guidelines.md`, `api-key-quota.md`, `runtime-installation.md`, and `minimal-linux-delivery.md`.
Update executable examples only where they describe the new verified build.
Keep unchanged workflow input defaults accurate. Do not replace every historical `v0.2.23` mention mechanically.
Replace obsolete separate-key examples in frontend `state-management.md` and `hook-guidelines.md` after verification.
Use `buildAccountUsageRefreshKey`, `{ data, ts, refreshKey }`, one watcher, and the final reply guards.
Update the old helper reference in backend `api-key-quota.md` during the same synchronization.
No specification changes belong to this planning phase.

## Eval, Gemini, and toolchain findings

Eval has no changed patched target. Static review found no broken provider, router, embedded-page, or settings contract consumed by its patches.
The combined build must still execute its existing suites.

The five Gemini intersections consist of one Go service, the settings API type, the Vue settings view, and two locale files.
Exa changes only the provider union and dropdown. Compaction and default-quota text changes use separate locale keys.
The rectifier type, translated keys, native Toggle, and save fields retain their existing contracts.

The only Gemini service delta changes `convertClaudeMessagesToGeminiContents` at
[new lines 3683–3711](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/backend/internal/service/gemini_messages_compat_service.go#L3683).
It moves trailing non-`functionResponse` Parts into a following user content, preserving order.
It does not change `ForwardNative`, its builders, native signature injection, cleaner, policies, or counting behavior.
The new upstream regression lives in `backend/internal/service/gemini_messages_compat_service_test.go`.

[PR #1309](https://github.com/Wei-Shaw/sub2api/pull/1309) remains open at this audit date and is absent from the tagged change.
Its proposed constructor injection and estimated-token fallback differ from the accepted rectifier contract.
Keep the dedicated default-false gate, unchanged constructors, actual successful token counts, and repeated-400 error behavior.

`backend/go.mod`, `frontend/package.json`, and `frontend/pnpm-lock.yaml` are unchanged between tags.
Go remains `1.27.4`. The lock resolves Vite `5.4.21`, TypeScript `5.6.3`, Vue `3.5.43`, and Vue I18n `11.4.16`.
The lockfile remains version `9.0`. The unchanged upstream Dockerfile activates pnpm 9.
The established local build still selects its existing `pnpm@12.16.1` entry. Do not change package managers for this adaptation.

No static symbol, type, translation-key, or toolchain break requires eval or Gemini edits.
Final acceptance requires the planned standalone and combined builds. Static research does not establish compile, test, or runtime success.

## Browser entry without another frontend build

The argument-free build removes its temporary source workspace after publication.
Use the host-platform combined executable to serve its embedded frontend during Phase 2.2.
This reuses the exact built assets without a second frontend build or a build-script change.

[main.go lines 77–114](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/backend/cmd/server/main.go#L77)
starts the HTTP setup server when configuration and installation markers are absent.
That server installs `web.ServeEmbeddedFrontend` and reads `SERVER_HOST`/`SERVER_PORT`.
[setup.go](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/backend/internal/setup/setup.go#L45)
uses `DATA_DIR` for its configuration and installation markers.
[handler.go](https://github.com/Wei-Shaw/sub2api/blob/v0.2.24/backend/internal/setup/handler.go#L23)
exposes `GET /setup/status` for readiness.
Set `AUTO_SETUP=false` and `SKIP_SETUP=false`. Use a new temporary data and working directory.
The browser must mock setup status and administrator APIs. The HTTP server needs no database configuration for this route.
Do not submit the setup wizard. Run the command without `--setup`, which selects the separate interactive CLI wizard.
