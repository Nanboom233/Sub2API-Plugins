# Quota patch adaptation design

Target: public Sub2API `v0.2.24`. Follow [requirements](prd.md) and the [audited source changes](research/v0224-upstream-diff.md).
Only the quota plugin needs changes. This document authorizes no implementation during Phase 1.

## Change boundary

| Repository file | Planned change |
| --- | --- |
| `plugins/sub2api-quota-extension/patches/quota-extension.patch` | Adapt the two Vue targets and shared refresh utility. Remove redundant plugin cache machinery. |
| `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts` | Extend unified-key, native snapshot, and stale single-response cases. |
| `plugins/sub2api-quota-extension/tests/test_usage_batch.test.ts` | Add a small real-view suite for changed-key batch rejection and cache reuse. |

Keep `test_quota_editor.test.ts` and all Go suites unchanged unless a concrete failure requires repair.
The quota plugin has no README. Add no baseline-only README for this task.
Keep eval/Gemini patches and tests, the template, workflows, `.gitmodules`, and common build scripts unchanged.

## One upstream refresh utility

Add the API-key branch directly before the OpenAI branch of `buildAccountUsageRefreshKey` at upstream utility line 74.
Extend its existing `Pick<Account, ...>` parameter with `credentials` and `proxy_id`.
Reuse `serializeSnapshotRefreshValue`. Include the existing API-key snapshot fields:

```text
id, platform, script, base_url, api_base_urls, api_protocol, api_key,
header_override_enabled, header_overrides, proxy_id,
enable_tls_fingerprint, tls_fingerprint_profile_id, updated_at
```

Keep `updated_at` because saved API keys are redacted. Preserve deterministic object ordering through the existing serializer.
Remove the plugin's separate `buildAPIKeyUsageRefreshKey` export and every production consumer.
Keep `hasQuotaScript` for eligibility and visible script errors. Preserve all native non-API-key helper branches.
The repository search found no external production consumer that requires a compatibility wrapper.

## AccountUsageCell.vue hunks

Keep upstream `_usageCache` as `{ data, ts, refreshKey }` and its existing TTL predicate.
Keep the single `usageRefreshKey` computed and existing captured `refreshKey` values.
Import only `hasQuotaScript` beside the existing upstream refresh helper.

Retain the quota `usageRequest` counter and captured account ID in `loadUsage`.
Compare the captured `refreshKey` with `usageRefreshKey.value` before applying a result.
Keep mount and request-order guards on success, errors, and loading changes. Capture no separate configuration value.
Use the existing active request's captured ID/key to reject changed-key success and error updates.
Retain its loading cleanup. It owns the active-request button independently of the automatic request state.

Extend only upstream `watch(usageRefreshKey, ...)` at cell lines 1841–1852.
For API-key changes, advance `usageRequest`, delete that account's cache entry, and clear `usageInfo` and `error`.
Do this before returning for a row that no longer qualifies for usage queries.
For batch-managed API keys, request `{ force: true }` once and return.
For eligible single API keys, use the existing manual-refresh `loadUsage({ bypassCache: true })` path once.
That explicit saved-configuration refresh does not wait for mobile visibility. Keep ordinary mount/snapshot lazy loading unchanged.
For other account types, retain the exact native watcher body, including passive Claude and non-forced Gemini routing.
Delete the plugin's separate computed key and configuration watcher.

Keep the upstream `estimateWindowTotalCost` helper and all new 5h/7d props.
Keep `UpstreamQuotaUsage`, local statistics, native provider cells, zero balances, and reset tooltips unchanged.

## AccountsView.vue hunks

Keep upstream imports and add only `hasQuotaScript` for the existing eligibility extension.
Keep `usageBatchCache` as `{ data, ts, refreshKey }` and the single captured map named `refreshKeys` at upstream line 804.
The brief calls this map `capturedRefreshKeyByAccountId`. Do not add that second map or rename the native owner unnecessarily.
Keep upstream cache reads and writes unchanged.

Before applying each success or failure, find its current account and compare its unified key with `refreshKeys.get(accountID)`.
Skip removed accounts and changed keys before changing usage, errors, loading, or cache state.
Add this small check beside the native token check in both response loops.
Keep native `usageBatchRequestTokenByAccountId` and its existing capture, queue updates, and removed-row cleanup.
Tokens protect request order when the key stays unchanged, including repeated manual refreshes. A key check cannot replace them.

Delete the plugin's extra configuration map, cache mutations, and account-configuration watcher.
The child cell's single watcher forces changed API-key rows into the existing queue, which advances their native token.
The current-key check covers replies that arrive before that child callback. The next cache read rejects the previous key.
No eager cache-deletion watcher is needed in the parent view.
Keep `shouldReplaceAutoRefreshRow` unchanged. Its native unified-key comparison already detects API-key configuration after the utility extension.
Retain native row pruning, queue coalescing, force aggregation, and token-refresh warnings.

No backend symbol, API type, locale key, provider, or module change is needed.

## Expected patch reduction

The three affected targets currently contain 21 hunks and 110 changed lines, including additions and removals.
The unified design should need 17–18 hunks and 92–98 changed lines.
This estimate includes both reply paths and immediate API-key refresh. The [audit](research/v0224-upstream-diff.md#expected-patch-reduction) gives per-target counts.
Measure the exported patch in Phase 2. Keep concrete backend and display hunks that have no upstream replacement.

## Focused evidence

Extend the existing cell suite through the real component and deferred synthetic responses.
Check native Claude/Gemini refresh, unchanged-key cache reuse, API-key saved-key/script invalidation, and one request per key change.
Keep existing stale-response and visible-data cases. Unmount every wrapper in `finally`.

Keep the batch suite small. Reuse native `AccountsView.lite.spec.ts` mocks and table slots with synthetic APIs.
Use the real usage cell for configuration changes. Stub unrelated modals and layout only.
Check an in-flight old success and old error, an existing old-key cache, unaffected-account reuse, and native same-key request ordering.
Do not add a shared mock framework or repeat unchanged token-warning tests.
Do not repeat backend quota mapping tests in Vue fixtures.

Chromium must inspect the final combined account table because upstream adds visible cost text.
Use synthetic authentication and usage responses. Include Claude 5h/7d costs and a custom API-key quota row.
Check en/zh and light/dark, full cost text, reset tooltips, zero balance, local data, and refresh behavior.
Record screenshots, console/page errors, and horizontal overflow. Stop the browser and preview server afterward.
