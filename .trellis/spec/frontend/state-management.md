# State Management

> Keep form draft state local, tag usage caches with configuration keys, and keep notification secrets in session memory only.

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
   Each cache entry stores `{ data, ts, config }` with a 5-minute TTL and `buildAPIKeyUsageRefreshKey(account)`.
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

Invalidate cached usage for a single account whenever its `buildAPIKeyUsageRefreshKey(account)` changes after an edit.
Increment the request token for that account, delete its cache entry, and trigger a fresh single or batched usage request.

Example from `frontend/src/components/account/AccountUsageCell.vue` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
watch(apiKeyUsageRefreshKey, (next, previous) => {
  if (next === previous) return
  usageRequest++
  _usageCache.delete(props.account.id)
  usageInfo.value = null
  error.value = null
  if (isBatchManaged.value) requestParentBatchUsage({ force: true })
  else requestAutoLoad()
})
```

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

- Reusing a cached `AccountUsageInfo` entry without comparing `cached.config === buildAPIKeyUsageRefreshKey(account)`.
- Replacing `account.extra` with `{ quota_script }` during account save and losing unrelated metadata keys.
- Clearing all dirty markers after an automatic inspection settings save when the administrator edited another field during the request.
- Resubmitting an unchanged masked `ntfy_password` on unrelated settings saves or storing the secret in `localStorage`.
- Restoring removed accounts into the manual evaluation table when a subsequent `/state` request fails after a valid group inventory refresh.
