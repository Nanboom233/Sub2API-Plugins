# Hook Guidelines

> Use Vue 3 composition helpers and pure utility modules with explicit request counters to coordinate asynchronous UI operations.

---

## Overview

This repository targets Vue 3 and vanilla ES modules rather than React.
Native Vue components use standard composition utilities (`useI18n`, `useId`, `useIntervalFn`, `ref`, `computed`, `watch`) and pure helper modules in `frontend/src/utils/`.
The embedded evaluation page coordinates requests through `api()` in `backend/internal/codexeval/web/app.js` and catalog helpers in `catalog.js` and `inspection.js`.
Every asynchronous request path guards against unmounted components and obsolete responses.

---

## Composition and Utility Patterns

Place reusable derivation logic in `frontend/src/utils/` as pure TypeScript functions.
Use `hasQuotaScript` and `buildAPIKeyUsageRefreshKey` in `frontend/src/utils/accountUsageRefresh.ts` to detect script usage and connection changes.
Include `account.updated_at` in `buildAPIKeyUsageRefreshKey` because account responses redact saved API keys.
Use `buildEmbeddedUrl` and `detectTheme` in `frontend/src/utils/embedded-url.ts` to synchronize iframe URL parameters with `document.documentElement`.

Example from `frontend/src/utils/accountUsageRefresh.ts` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
export const hasQuotaScript = (account: Pick<Account, 'type' | 'extra'>): boolean =>
  account.type === 'apikey' && isNonBlankString(account.extra?.quota_script)

export const buildAPIKeyUsageRefreshKey = (account: Account): string => {
  if (account.type !== 'apikey') return ''
  const credentials = account.credentials ?? {}
  const extra = account.extra ?? {}
  return serializeSnapshotRefreshValue({
    id: account.id,
    platform: account.platform,
    script: extra.quota_script,
    base_url: credentials.base_url,
    api_base_urls: credentials.api_base_urls,
    api_protocol: credentials.api_protocol,
    api_key: credentials.api_key,
    header_override_enabled: credentials.header_override_enabled,
    header_overrides: credentials.header_overrides,
    proxy_id: account.proxy_id,
    enable_tls_fingerprint: extra.enable_tls_fingerprint,
    tls_fingerprint_profile_id: extra.tls_fingerprint_profile_id,
    updated_at: account.updated_at
  })
}
```

---

## Data Fetching

Route native administrator requests through `adminAPI` (`frontend/src/api/admin/accounts.ts`).
Use `enqueueUsageRequest` in `AccountUsageCell.vue` for single-account usage queries and `adminAPI.accounts.getBatchUsage` in `AccountsView.vue` for batched queries.
Track a monotonic request counter (`++usageRequest` or `++request`) before awaiting an API call.
Verify that the counter, component mount state, account ID, and refresh key still match before applying the response.

Example from `frontend/src/components/account/QuotaScriptEditor.vue` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
async function testScript() {
  if (!model.value.trim() || inFlight > 0) return
  const current = ++request
  inFlight++
  testing.value = true
  usage.value = null
  error.value = ''
  try {
    const result = await adminAPI.accounts.testQuotaScript({ ...props.connection, script: model.value })
    if (current === request) usage.value = result
  } catch (failure: unknown) {
    if (current === request) {
      error.value = (failure as { message?: string })?.message || t('common.error')
    }
  } finally {
    inFlight--
    if (inFlight === 0) testing.value = false
  }
}
```

In `backend/internal/codexeval/web/app.js`, call `api(path, { method, body, signal })` with `AbortSignal.timeout(30000)` and the `Bearer` token from `localStorage.getItem('auth_token')`.
Cancel superseded group or catalog reads with `AbortController` or sequence counters before mutating page state.

---

## Naming Conventions

Name Vue composition utilities with the `use` prefix (`useI18n`, `useId`, `useIntervalFn`, `useAppStore`).
Name boolean predicate helpers with `is`, `has`, `should`, or `supports` (`hasQuotaScript`, `shouldFetchUsage`, `accountSupportsBatchUsage`).
Name deterministic snapshot key builders with `build*RefreshKey` (`buildAPIKeyUsageRefreshKey`, `buildOpenAIUsageRefreshKey`).
Name API client methods after the endpoint action (`getUsage`, `getBatchUsage`, `testQuotaScript`).

---

## Common Mistakes

- Applying an in-flight usage response after `apiKeyUsageRefreshKey` or `props.account.id` has changed.
- Triggering a fallback default quota query after a custom quota script fails.
- Fetching model suggestions for disabled accounts (`schedulable === false`) in `backend/internal/codexeval/web/catalog.js`.
- Starting a competing settings read during initial tab restoration in `app.js` that invalidates the first group catalog response.
- Disconnecting theme observers or timers without cleaning them up in `onUnmounted` or `onBeforeUnmount`.
