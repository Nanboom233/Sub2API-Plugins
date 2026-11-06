# Directory Structure

> Keep production frontend changes in plugin patches and keep all frontend test files flat under `plugins/<name>/tests/`.

---

## Overview

Plugins do not store a checked-out upstream `frontend/` directory in the repository root.
During `python3 scripts/build.py`, the builder downloads upstream Sub2API into a temporary workspace and applies `plugins/<name>/patches/*.patch`.
The builder then compiles the patched Vue 3 frontend and embeds `frontend/dist` into the Go server binary.
Evaluation web assets live in `backend/internal/codexeval/web/` inside `plugins/codex-candy-eval/patches/` and embed through `backend/internal/codexeval/web.go`.
All Vue and Node UI test suites live directly under each plugin's flat `tests/` directory.

Owners: [quota patch](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch), [evaluation UI patch](../../../plugins/codex-candy-eval/patches/0006-evaluation-ui.patch), and [integration patch](../../../plugins/codex-candy-eval/patches/0007-sub2api-integration.patch).

---

## Directory Layout

```text
plugins/sub2api-quota-extension/
├── patches/quota-extension.patch            Patched upstream Vue, TS, and Go files
└── tests/
    ├── test_quota_editor.test.ts            Staged Vitest suite for QuotaScriptEditor and modals
    └── test_usage_cell.test.ts              Staged Vitest suite for AccountUsageCell and bars

plugins/codex-candy-eval/
├── patches/
│   ├── 0003-vendor-assets.patch             Embedded markdown-it and Temml vendor assets
│   ├── 0006-evaluation-ui.patch             Embedded codexeval/web/* and CodexEvalView.vue
│   └── 0007-sub2api-integration.patch       Sidebar, router, i18n, and embedded-url patches
└── tests/
    └── test_ui.cjs                          Node UI verification suite for embedded web page

Temporary upstream workspace (applied by scripts/build.py):
frontend/src/
├── api/admin/accounts.ts                    Admin account API client and testQuotaScript
├── components/
│   ├── account/
│   │   ├── AccountUsageCell.vue             Account usage table cell and remote quota dispatch
│   │   ├── CreateAccountModal.vue           Account creation modal with QuotaScriptEditor
│   │   ├── EditAccountModal.vue             Account edit modal with QuotaScriptEditor
│   │   ├── QuotaScriptEditor.vue            Shared custom quota script editor and tester
│   │   ├── UpstreamQuotaUsage.vue           Remote quota progress bars and balance display
│   │   └── UsageProgressBar.vue             Window utilization bar and hover reset tooltip
│   └── layout/AppSidebar.vue                Admin navigation item for Account Evaluation
├── i18n/locales/{en,zh}/
│   ├── common.ts                            Navigation labels in English and Chinese
│   └── admin/accounts.ts                    Quota script and upstream quota translations
├── router/index.ts                          /admin/codex-eval route definition
├── types/index.ts                           Account and AccountUsageInfo TypeScript interfaces
├── utils/
│   ├── accountUsageRefresh.ts               Refresh key builders and hasQuotaScript helper
│   └── embedded-url.ts                      Same-origin iframe URL builder and theme detector
└── views/admin/
    ├── AccountsView.vue                     Account list view and batched usage queue
    └── CodexEvalView.vue                    Admin layout wrapper for /codex-eval iframe

backend/internal/codexeval/
├── web.go                                   Go embed declarations and HTML template assembly
└── web/
    ├── ui.html                              Standalone evaluation and inspection shell
    ├── style.css                            Layout, table, dialog, and control styles
    ├── theme.css                            Light and dark CSS custom properties
    ├── app.js                               API wrapper, polling, tab routing, and auth checks
    ├── catalog.js                           Group, account, and raw model catalog management
    ├── components.js                        Shared dropdowns, tags, and row switch builders
    ├── candy.js                             Candy tab controls, table rows, and history
    ├── fingerprint.js                       Fingerprint tab controls, rankings, and details
    ├── pelican.js                           Pelican tab controls, 4:3 previews, and dialogs
    ├── inspection.js                        Settings tab cards, model selector, and auto-save
    └── vendor/                              Bundled Markdown and math rendering scripts
```

---

## Module Organization

Place native admin UI extensions in the existing upstream `frontend/src/` domain folder that owns the feature.
Keep account table cells and account modal subcomponents in `frontend/src/components/account/`.
Keep admin route views in `frontend/src/views/admin/` and register routes in `frontend/src/router/index.ts`.
Keep pure refresh-key and URL helpers in `frontend/src/utils/` so components and tests can import them without side effects.
Keep standalone evaluation scripts split by tab and concern under `backend/internal/codexeval/web/`.
When you add an embedded file under `backend/internal/codexeval/web/`, register its `//go:embed` variable and replacement token in `web.go`.

---

## Naming Conventions

Use `PascalCase.vue` for Vue single-file components such as `QuotaScriptEditor.vue` and `UpstreamQuotaUsage.vue`.
Use `camelCase.ts` for TypeScript API modules and utilities such as `accountUsageRefresh.ts`.
Use `kebab-case.ts` only when modifying an existing upstream file that already uses kebab-case such as `embedded-url.ts`.
Use `test_*.test.ts` for native Vue Vitest suites under `plugins/<name>/tests/`.
Use `test_*.cjs` for Node verification scripts that exercise embedded HTML and JavaScript modules.
Do not create nested subdirectories inside `plugins/<name>/tests/`.

---

## Examples

- Native Vue component and modal patches: [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch)
- Embedded evaluation page and iframe view: [`0006-evaluation-ui.patch`](../../../plugins/codex-candy-eval/patches/0006-evaluation-ui.patch)
- Admin navigation and route integration: [`0007-sub2api-integration.patch`](../../../plugins/codex-candy-eval/patches/0007-sub2api-integration.patch)
- Staged Vitest component suites: [`test_quota_editor.test.ts`](../../../plugins/sub2api-quota-extension/tests/test_quota_editor.test.ts) and [`test_usage_cell.test.ts`](../../../plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts)
- Embedded UI contract test suite: [`test_ui.cjs`](../../../plugins/codex-candy-eval/tests/test_ui.cjs)
