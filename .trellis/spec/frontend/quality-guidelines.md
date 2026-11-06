# Quality Guidelines

> Verify frontend changes through `python3 scripts/build.py`, staged Vitest suites, and Node UI contract tests.

---

## Overview

The unified build script (`python3 scripts/build.py`) validates all frontend patches and tests inside a temporary upstream workspace.
It runs `pnpm run check:i18n`, `pnpm run build` (`vue-tsc --noEmit` and `vite build`), and discovered plugin test suites.
Native Vue component suites (`test_*.test.ts`) run through the upstream Vitest configuration, and embedded UI checks (`test_ui.cjs`) run through Node.
See [Quality and Commits](../backend/quality-guidelines.md) for the repository build and commit workflow.

---

## Forbidden Patterns

- Placing test files, test fixtures, or mock helpers inside production patches (`plugins/<name>/patches/*.patch`).
- Displaying default upstream quota detection errors or global error toasts when an API-key account has no custom script.
- Issuing a fallback default quota query after a custom quota script fails.
- Storing notification secrets (`ntfy_password` or `bark_url`) in `localStorage` or `sessionStorage`.
- Adding external npm dependencies (such as Monaco, CodeMirror, or Zod) to the upstream `frontend/package.json` without explicit user approval.
- Leaving mounted Vue test wrappers alive after a test finishes instead of unmounting them in a `finally` block.

---

## Required Patterns

- Keep English (`frontend/src/i18n/locales/en/`) and Chinese (`frontend/src/i18n/locales/zh/`) translation keys identical in structure.
- Show custom quota script errors in amber text (`text-amber-600 dark:text-amber-400`) inside `QuotaScriptEditor.vue` and `UpstreamQuotaUsage.vue`.
- Preserve local account statistics (`todayStats`) and local quota bars even when remote quota queries fail or return empty objects.
- Pass relative `/codex-eval` to `buildEmbeddedUrl` so the browser resolves the full `window.location.origin` including nonstandard ports.
- Unmount every `@vue/test-utils` wrapper inside `try ... finally { wrapper.unmount() }`.

---

## Testing Requirements

Keep all frontend test files flat under `plugins/<name>/tests/`.
During `python3 scripts/build.py`, `run_patched_tests` stages `test_*.test.ts` into a temporary directory under `frontend/src/` and runs `pnpm test:unit -- --run` once.
Remove staged test files immediately after the Vitest run completes or fails.

Example from [`test_quota_editor.test.ts`](../../../plugins/sub2api-quota-extension/tests/test_quota_editor.test.ts):

```ts
const connection = { api_key: 'draft-key', base_url: 'https://draft.example', proxy_id: null }
const wrapper = mount(QuotaScriptEditor, { props: { modelValue: '', connection, active: true } })
try {
  expect(wrapper.get('button').attributes('disabled')).toBeDefined()
  await wrapper.get('textarea').setValue(script)
  expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([script])
} finally {
  wrapper.unmount()
}
```

Run `node plugins/codex-candy-eval/tests/test_ui.cjs` to verify embedded DOM rendering, catalog filtering, model selection, and settings auto-save.
Frontend tests consume mapped `AccountUsageInfo` fields directly without repeating backend upstream response parsing matrices.

---

## Code Review Checklist

- [ ] Both `en` and `zh` locale files define every new or modified translation key (`pnpm run check:i18n`).
- [ ] `vue-tsc --noEmit` and `vite build` succeed with zero TypeScript or bundling errors.
- [ ] Asynchronous requests verify request counters, mount state, and refresh keys before updating reactive state.
- [ ] Zero values (`balance: 0`, `utilization: 0`) render properly and are not treated as empty or absent.
- [ ] Production patches contain no test files, and `plugins/<name>/tests/` remains flat.
