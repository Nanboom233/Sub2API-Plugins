# Component Guidelines

> Build Vue components with `<script setup lang="ts">` and reuse native Sub2API UI primitives across views and modals.

---

## Overview

Native admin components use Vue 3 Composition API with `<script setup lang="ts">` and Tailwind CSS utility classes.
Components reuse upstream building blocks such as `AppLayout`, `HelpTooltip`, `UsageProgressBar`, and `Icon`.
The embedded evaluation page in `backend/internal/codexeval/web/` uses modular vanilla JavaScript functions and DOM templates.
Both surfaces preserve native light and dark theme switching, compact table alignment, and accessible form controls.

---

## Component Structure

Write Vue single-file components with `<script setup lang="ts">` and `<template>` blocks.
Keep imports grouped at the top of `<script setup lang="ts">`, followed by props, models, reactive state, watchers, and actions.
Extract shared display fragments into focused child components instead of duplicating template markup across cells and modals.

Example from `frontend/src/components/account/UpstreamQuotaUsage.vue` in [`quota-extension.patch`](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch):

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { AccountUsageInfo } from '@/types'
import UsageProgressBar from './UsageProgressBar.vue'

const props = defineProps<{ usage: AccountUsageInfo; showError?: boolean; balanceClass?: string }>()
const { t } = useI18n()
const windows = computed(() => [
  { label: '5h', progress: props.usage.five_hour, color: 'indigo' as const },
  { label: '1d', progress: props.usage.one_day, color: 'indigo' as const },
  { label: '7d', progress: props.usage.seven_day, color: 'emerald' as const },
  { label: '30d', progress: props.usage.thirty_day, color: 'purple' as const },
  { label: 'total', progress: props.usage.quota_total, color: 'purple' as const }
].flatMap(({ progress, ...window }) => progress ? [{ ...window, progress }] : []))
</script>

<template>
  <div class="space-y-1">
    <p v-if="showError && usage.error" class="text-xs text-amber-600 dark:text-amber-400">{{ usage.error }}</p>
    <UsageProgressBar
      v-for="window in windows"
      :key="window.label"
      :label="window.label"
      :utilization="window.progress.utilization"
      :resets-at="window.progress.resets_at"
      :color="window.color"
      :title="t('admin.accounts.usageWindow.upstreamQuota')"
    />
    <span
      v-if="usage.balance != null"
      :class="['text-[10px] font-medium leading-4', balanceClass]"
      :title="t('admin.accounts.usageWindow.upstreamQuota')"
    >{{ usage.balance_unit || 'USD' }} {{ usage.balance.toFixed(2) }}</span>
  </div>
</template>
```

Reuse `QuotaScriptEditor.vue` in both `CreateAccountModal.vue` and `EditAccountModal.vue`.
Reuse `UpstreamQuotaUsage.vue` inside both `AccountUsageCell.vue` and `QuotaScriptEditor.vue`.
For the embedded evaluation view, wrap the `/codex-eval` iframe in `CodexEvalView.vue` inside `AppLayout`.

---

## Props Conventions

Declare props with TypeScript type literals in `defineProps<...>()` and apply defaults through `withDefaults` when needed.
Use `defineModel<string>({ default: '' })` for two-way text bindings such as `v-model="quotaScript"`.
Pass draft connection parameters to `QuotaScriptEditor.vue` through a typed `connection` prop (`Omit<QuotaScriptTestParams, 'script'>`).
Pass boolean visibility flags such as `:active="show"` and `:show-error="usesQuotaScript"` explicitly.
Do not mutate object props inside child components.

---

## Styling Patterns

In native Vue components, use upstream utility classes (`input`, `input-label`, `btn`, `btn-secondary`, `btn-sm`, `card`) and Tailwind CSS utilities.
Pair light-mode text and surface classes with explicit `dark:` variants (`text-amber-600 dark:text-amber-400`).
In `QuotaScriptEditor.vue`, stack the syntax-highlighted `<pre>` and transparent `<textarea>` in one CSS grid cell (`grid-area: 1 / 1`).
Keep the script editor auto-expanding without internal scrollbars or third-party code editor packages.
In `UsageProgressBar.vue`, render the formatted reset timestamp inside a hover tooltip using `group-hover:opacity-100`.

In `backend/internal/codexeval/web/`, style elements with theme variables from `theme.css` and layout rules from `style.css`.
Match the native tag and dropdown layout when mirroring a widget in `inspection.js`.

---

## Accessibility

Bind form labels to inputs with matching `for` and `id` attributes (`useId()` in Vue or stable IDs in `ui.html`).
Provide `aria-label` on icon buttons, search fields, and switches that omit visible text captions.
Set `aria-hidden="true"` on decorative SVG icons and the syntax-highlight `<pre>` overlay in `QuotaScriptEditor.vue`.
Render inline script test failures with `role="alert"` so assistive tools announce errors without global toasts.
Maintain `role="switch"`, `aria-expanded`, and `aria-controls` on collapsible settings cards and model dropdown triggers in `ui.html`.

---

## Common Mistakes

- Showing default upstream quota probe errors in `AccountUsageCell.vue` instead of restricting visible errors to custom quota scripts (`:show-error="usesQuotaScript"`).
- Retaining stale inline test output in `QuotaScriptEditor.vue` after the script, draft connection, or modal visibility changes.
- Duplicating custom quota editor fields across create and edit modals instead of binding `QuotaScriptEditor.vue` in both forms.
- Using a hostname-only header for the evaluation iframe instead of resolving `/codex-eval` against `window.location.origin` in `CodexEvalView.vue`.
- Adding explanatory subtitles, example buttons, or nested cards that violate the compact native form layout.
