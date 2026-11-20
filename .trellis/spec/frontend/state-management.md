# State Management

> Keep form draft state local, tag usage caches with refresh keys, and keep notification secrets in session memory only.

---

## Overview

Native admin views manage reactive state with Vue 3 `ref`, `computed`, and `watch` alongside upstream Pinia stores (`useAppStore`, `useAuthStore`).
Account usage cells and list views maintain bounded 5-minute in-memory caches tagged with each account's refresh key.
The embedded evaluation page manages mutable runtime state in module-scoped JavaScript variables (`evaluationState`, `credentials`, `switching`, `inspectionSwitching`).
Browser `localStorage` stores only non-sensitive UI preferences (`sub2api-codex-eval.prefs`, `sub2api-codex-eval.masked`, `theme`) and reads native `auth_token`.

---

## State Categories

1. **Local Component State**:
   Use `ref` and `computed` in `<script setup lang="ts">` for modal inputs, inline test results, and connection props.
   Clear inline test results synchronously (`flush: 'sync'`) whenever `model`, `props.connection`, or `props.active` changes.
2. **Shared Usage Caches**:
   Store single-cell usage in `_usageCache` (`AccountUsageCell.vue`) and batched usage in `usageBatchCache` (`AccountsView.vue`).
   Each cache entry stores `{ data, ts, refreshKey }` with a 5-minute TTL and `buildAccountUsageRefreshKey(account)`.
3. **Embedded Evaluation Page State**:
   Keep active runs, history maps, and group inventories in memory inside `backend/internal/codexeval/web/app.js` and `catalog.js`.
   Track per-account pending switch updates in `switching` and `inspectionSwitching` maps so background polls preserve in-flight user toggles.
4. **Session-Only Secret State**:
   In `backend/internal/codexeval/web/inspection.js`, retain entered `ntfy_password` values only in memory for the current page session.
   Never write notification passwords or Bark URLs to `localStorage` or `sessionStorage`.

---

## When to Use Shared State

Keep draft account fields and script test previews inside the owning modal and `QuotaScriptEditor.vue`.
Do not write draft test results into `_usageCache`, `usageBatchCache`, or the parent account table.
Use module-scoped state only when sibling component instances share requests, such as `_usageCache` in `AccountUsageCell.vue`.
Use existing Pinia stores (`useAppStore`, `useAuthStore`) only for global application mode and toast notifications where native views already do so.

---

## Server State Synchronization

The unified `buildAccountUsageRefreshKey(account)` owns native snapshot keys and API-key connection keys.
For API-key changes, use the existing `usageRefreshKey` watcher to invalidate that account and refresh immediately.
Native Claude and Gemini snapshot branches retain passive refresh behavior.

Example from `frontend/src/components/account/AccountUsageCell.vue` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
watch(usageRefreshKey, (nextKey, prevKey) => {
  if (!prevKey || nextKey === prevKey) return
  if (props.account.type === 'apikey') {
    usageRequest++
    _usageCache.delete(props.account.id)
    usageInfo.value = null
    error.value = null
    loading.value = false
    if (!shouldFetchUsage.value) return
    if (isBatchManaged.value) requestParentBatchUsage({ force: true })
    else void loadUsage({ bypassCache: true })
    return
  }
  // Existing native provider branches follow.
})
```

On single replies, compare the captured account ID and refresh key before changing usage or errors.
Passive single replies also check `usageRequest` and unmount state before changing loading state or cache entries.
In `AccountsView.vue`, keep native `refreshKeys`, `usageBatchRequestTokenByAccountId`, and `shouldReplaceAutoRefreshRow`.
For batch success and failure, reject missing accounts or changed keys before updating reactive state:

```ts
const currentAccount = accounts.value.find(account => account.id === accountID)
if (!currentAccount || buildAccountUsageRefreshKey(currentAccount) !== refreshKeys.get(accountID)) continue
```

The existing batch request token check still rejects obsolete replies for overlapping requests with the same key.
Do not add configuration fields, a second key map, or another invalidation watcher.

In `EditAccountModal.vue`, clone `props.account.extra` before setting or deleting `quota_script` so sibling keys remain intact:

```ts
if (props.account.type === 'apikey') {
  const extra: Record<string, unknown> = { ...(updatePayload.extra || props.account.extra || {}) }
  if (quotaScript.value.trim()) extra.quota_script = quotaScript.value
  else delete extra.quota_script
  updatePayload.extra = extra
}
```

In `backend/internal/codexeval/web/inspection.js`, track edited form inputs in a dirty-field set during automatic debounced saves.
After a save finishes, clear only dirty markers whose values stayed unchanged during the request.

---

## Common Mistakes

- Reusing cached `AccountUsageInfo` without comparing `cached.refreshKey` with the current `buildAccountUsageRefreshKey(account)`.
- Replacing `account.extra` with `{ quota_script }` during account save and losing unrelated metadata keys.
- Clearing all dirty markers after an automatic inspection settings save when the administrator edited another field during the request.
- Resubmitting an unchanged masked `ntfy_password` on unrelated settings saves or storing the secret in `localStorage`.
- Restoring removed accounts into the manual evaluation table when a subsequent `/state` request fails after a valid group inventory refresh.
