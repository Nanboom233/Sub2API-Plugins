# Design: Bootstrap Guidelines and Migrate Eval Trellis Artifacts

## 1. Architecture and Boundaries

This task operates strictly on Trellis artifacts, repository specifications, and AI-assistant scaffolding across two Git boundaries:

1. **Parent Repository (`Sub2API-Plugins`)**:
   - Owns the single authoritative `.trellis/` tree (`spec/`, `tasks/`, `workspace/`, `scripts/`, `config.yaml`, `workflow.md`).
   - Receives migrated historical archives from `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/` into `.trellis/tasks/archive/2026-10/`.
   - Receives migrated historical developer journals from `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` into `.trellis/workspace/codex-candy-eval-plugin/`.
   - Houses the completed `.trellis/spec/frontend/` guidelines alongside `.trellis/spec/backend/` and `.trellis/spec/guides/`.
2. **Submodule (`plugins/codex-candy-eval`)**:
   - Returns to the native plugin directory layout shared by `plugins/sub2api-quota-extension` and `plugins/sub2api-plugin-template`.
   - Removes `.trellis/`, `.claude/`, `.codex/`, `.devin/`, `AGENTS.md`, and `.gitattributes`.
   - Replaces `.gitignore` with the 6-line native plugin ignore set (`dist/`, `__pycache__/`, `*.py[cod]`, `.DS_Store`, `.env`, `.env.*`).

## 2. Artifact Migration Flow

```
plugins/codex-candy-eval/.trellis/
  ├── tasks/archive/2026-10/
  │     ├── 00-bootstrap-guidelines/  ──(rename id/name + dir)──> .trellis/tasks/archive/2026-10/10-11-eval-bootstrap-guidelines/
  │     └── 10-11..10-19 (6 dirs)     ──(copy unchanged)────────> .trellis/tasks/archive/2026-10/<same-name>/
  ├── workspace/codex-candy-eval-plugin/
  │     ├── index.md                  ──(copy unchanged)────────> .trellis/workspace/codex-candy-eval-plugin/index.md
  │     └── journal-1.md              ──(copy unchanged)────────> .trellis/workspace/codex-candy-eval-plugin/journal-1.md
  └── spec/                           ──(superseded by parent)──> (removed with eval .trellis/)
```

### Slug Disambiguation for `00-bootstrap-guidelines`

- `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/00-bootstrap-guidelines` was archived on `2026-10-11`.
- Copying it as `00-bootstrap-guidelines` into `.trellis/tasks/archive/2026-10/` would duplicate the slug of the active parent task `.trellis/tasks/00-bootstrap-guidelines`.
- Rename the destination directory to `.trellis/tasks/archive/2026-10/10-11-eval-bootstrap-guidelines` and update `id` and `name` in its `task.json` to `"eval-bootstrap-guidelines"`.

## 3. Frontend Specification Design (`.trellis/spec/frontend/`)

Populate the 7 files under `.trellis/spec/frontend/` using ASD-STE100 English and real code examples from the two frontend surfaces in this repository:

1. **`index.md`**:
   - Summarize both frontend surfaces: (a) native Sub2API Vue 3 + TypeScript + Tailwind CSS admin components patched by plugins, and (b) the standalone embedded evaluation web UI (`backend/internal/codexeval/web/`).
   - Mark all 6 frontend guideline files as `Current` in the Guidelines Index table and remove the "How to Fill These Guidelines" boilerplate.
2. **`directory-structure.md`**:
   - Document how plugin patches target upstream `frontend/src/` (`components/account/*.vue`, `views/admin/*.vue`, `api/admin/*.ts`, `utils/*.ts`, `i18n/locales/{en,zh}/*.ts`, `router/index.ts`, `types/index.ts`) and embedded `backend/internal/codexeval/web/` (`ui.html`, `style.css`, `theme.css`, `app.js`, `api.js`, `history.js`, `inspection.js`, `renderers.js`, `state.js`, `utils.js`).
   - Document flat frontend test placement under `plugins/<plugin>/tests/` (`test_*.test.ts` for Vitest and `test_ui.cjs` for Node).
3. **`component-guidelines.md`**:
   - Document Vue 3 `<script setup lang="ts">` conventions (`defineProps`, `defineEmits`, `withDefaults`), shared modal/editor reuse (`QuotaScriptEditor.vue` in `CreateAccountModal.vue` and `EditAccountModal.vue`), native cell rendering (`AccountUsageCell.vue`, `UpstreamQuotaUsage.vue`, `UsageProgressBar.vue`), and embedded iframe hosting (`CodexEvalView.vue`).
   - Document vanilla ES module component rendering and DOM updates in `backend/internal/codexeval/web/renderers.js` and `inspection.js`.
4. **`hook-guidelines.md`**:
   - Document composition utilities and asynchronous data fetching patterns in this repository (which uses Vue 3 `<script setup>` + explicit utility modules rather than React hooks): `frontend/src/utils/accountUsageRefresh.ts` (batch/single usage refresh), `frontend/src/utils/embedded-url.ts` (authenticated iframe URL assembly), `frontend/src/api/admin/accounts.ts`, and `backend/internal/codexeval/web/api.js`.
5. **`state-management.md`**:
   - Document local reactive state (`ref`, `computed`, `watch`) in Vue components, draft connection state isolation before save (`QuotaScriptEditor.vue`), centralized mutable state in `backend/internal/codexeval/web/state.js`, and session-only masked secret handling (`ntfy_password_configured` in `inspection.js` without persisting secrets in `localStorage`).
6. **`type-safety.md`**:
   - Document TypeScript interface definitions in `frontend/src/types/index.ts` and `frontend/src/api/admin/accounts.ts`, strict `vue-tsc --noEmit` verification during `python3 scripts/build.py`, nullable upstream quota field normalization, and structured JSON payload contracts between Go handlers and frontend callers.
7. **`quality-guidelines.md`**:
   - Document frontend verification executed by `python3 scripts/build.py`: `pnpm run check:i18n`, `vue-tsc --noEmit`, `vite build`, staged Vitest runs (`test_*.test.ts`), and Node UI contract checks (`test_ui.cjs`).
   - Document error visibility contracts: silent default upstream quota errors vs visible custom-script test errors, and bilingual `en`/`zh` i18n key parity.

## 4. Compatibility and Rollback

- No runtime code, patch file, build script, or CI workflow changes.
- If any check fails during migration, `git -C plugins/codex-candy-eval status` and parent `git status` identify every modified or untracked path for immediate restoration before commit approval.
