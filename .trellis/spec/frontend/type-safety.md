# Type Safety

> Define explicit TypeScript interfaces for API contracts and validate untrusted `extra` fields before rendering.

---

## Overview

The native Sub2API frontend compiles with strict TypeScript checking via `vue-tsc --noEmit` during `python3 scripts/build.py`.
Shared domain models live in `frontend/src/types/index.ts`, and endpoint request types live in `frontend/src/api/admin/accounts.ts`.
Embedded evaluation modules in `backend/internal/codexeval/web/` use `"use strict"` JavaScript and explicit runtime property checks against Go JSON responses.

---

## Type Organization

Extend existing interfaces in `frontend/src/types/index.ts` when backend patches add optional response fields.
Keep endpoint-specific parameter interfaces in the corresponding API module under `frontend/src/api/admin/`.
Import types with `import type` so Vite strips type-only imports during bundling.

Example from `frontend/src/types/index.ts` and `frontend/src/api/admin/accounts.ts` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
// frontend/src/types/index.ts
export interface AccountUsageInfo {
  updated_at: string | null
  five_hour: UsageProgress | null
  seven_day: UsageProgress | null
  seven_day_sonnet: UsageProgress | null
  seven_day_fable?: UsageProgress | null
  thirty_day?: UsageProgress | null
  one_day?: UsageProgress | null
  quota_total?: UsageProgress | null
  balance?: number | null
  balance_unit?: string
  error?: string
}

// frontend/src/api/admin/accounts.ts
export interface QuotaScriptTestParams {
  script: string
  account_id?: number
  api_key?: string
  base_url?: string
  proxy_id?: number | null
  extra?: Record<string, unknown>
}
```

---

## Runtime Validation

Treat `account.extra` (`Record<string, unknown> | undefined`) as untyped JSON metadata at runtime.
Narrow `account.extra` fields with explicit type predicates before reading strings, booleans, or numbers.
Do not add external schema validation libraries such as Zod or Yup to the frontend bundle.

Example from `frontend/src/utils/accountUsageRefresh.ts` and `EditAccountModal.vue` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```ts
const isNonBlankString = (value: unknown): value is string => (
  typeof value === 'string' && value.trim().length > 0
)

export const hasQuotaScript = (account: Pick<Account, 'type' | 'extra'>): boolean =>
  account.type === 'apikey' && isNonBlankString(account.extra?.quota_script)

const readQuotaScript = (extra: Account['extra']): string =>
  typeof extra?.quota_script === 'string' ? extra.quota_script : ''
```

In `backend/internal/codexeval/web/`, check explicit values such as `extra?.codex_eval_inspection_verdict === "degraded"` and `schedulable !== false`.

---

## Common Patterns

Use `Pick<Account, ...>` and `Omit<QuotaScriptTestParams, 'script'>` to narrow helper and component inputs to the fields they actually read.
Check `usage.balance != null` rather than truthiness (`Boolean(usage.balance)`) so zero balances (`0`) render as valid data (`USD 0.00`).
Default `usage.balance_unit` to `'USD'` when formatting balances (`usage.balance_unit || 'USD'`).
Filter optional quota windows with `flatMap` so TypeScript narrows `UsageProgress | null | undefined` to `UsageProgress`.
Catch unknown request failures as `failure: unknown` and narrow `(failure as { message?: string })?.message` before falling back to `t('common.error')`.

---

## Forbidden Patterns

- Using truthy checks (`if (usage.balance)`) that hide valid zero balances or zero utilization values.
- Casting raw `account.extra` values with `as string` without checking `typeof value === 'string'`.
- Adding `any` types to new TypeScript helper functions, props, or API client signatures.
- Inferring reset timestamps on the frontend from window labels (`5h`, `1d`, `7d`, `30d`, `total`) when `resets_at` is null or absent.
- Inventing frontend-only quota or inspection fields that do not exist in the Go response structs.
