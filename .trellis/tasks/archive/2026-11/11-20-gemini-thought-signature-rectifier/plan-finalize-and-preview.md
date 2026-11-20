# Planning Finalization and Real-Browser UI Preview Brief

Target task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any subagent from running `hc send`.

## Scope and Hard Boundaries

1. **Planning + isolated `/tmp` visual preview ONLY**:
   - Do **NOT** run `task.py start`.
   - Do **NOT** create `plugins/gemini-signature-rectifier` or modify `.gitmodules`, patches, production code, test code, or Git state in `/Users/minami/Code/S/Sub2API-Plugins`.
   - Do **NOT** use `gh` or any authenticated Git/GitHub credentials (unauthenticated public fetches only).
   - Use `PYTHONDONTWRITEBYTECODE=1 python3 -B` for any Python invocation and remove any created `__pycache__` immediately.
   - Use synthetic data only in all mocked API responses and screenshots. Zero real credentials, tokens, or deployment data.

## Locked User Decisions

1. **Plugin directory and name**: **`plugins/gemini-signature-rectifier`** (replaces `plugins/sub2api-gemini-signature-rectifier`).
2. **Item 5 (`countTokens`)**: **Option B** ("估算不应该在这里处理 本来400就不会估算") — `countTokens` participates in the single signature-400 cleanup retry, returns upstream's actual `totalTokens` on retry success, and preserves actual HTTP 400 on repeated 400 with **no** new 400 local estimation. Existing untouched transport/transient-exhausted/OAuth-scope estimates stay in their tagged locations.
3. **Settings default (`gemini_native_signature_enabled`)**: Proposed `true` for fresh installs and legacy records missing the field (explicit `false` preserved, master-off preserved, fail-open on runtime read error) — still mark this default as awaiting final user plan approval alongside the visual preview.

## Deliverables

### 1. Audit Every Relevant `.trellis/spec/` File & Finalize Planning Artifacts

Read and verify compliance against:
- `.trellis/spec/backend/{index,directory-structure,database-guidelines,error-handling,logging-guidelines,quality-guidelines,native-inspection,runtime-installation}.md`
- `.trellis/spec/frontend/{index,directory-structure,component-guidelines,hook-guidelines,state-management,type-safety,quality-guidelines}.md`
- `.trellis/spec/guides/{index,cross-layer-thinking-guide,code-reuse-thinking-guide}.md`

Update these files in `.trellis/tasks/11-20-gemini-thought-signature-rectifier/`:

1. **`prd.md`**:
   - Lock `plugins/gemini-signature-rectifier` and Item 5 **Option B** (remove `[PENDING USER CONFIRMATION]` from both; keep only the R6 default rule marked for final plan approval).
   - Add an explicit UI/visual acceptance requirement for real-browser visual parity in light and dark themes and en/zh locales, using synthetic data only (aligned with `component-guidelines.md`, `logging-guidelines.md`, and `native-inspection.md:362` / `runtime-installation.md:250`).
   - Keep English concise, active voice, short sentences (no semicolons or contractions).

2. **`design.md`**:
   - Lock `plugins/gemini-signature-rectifier` and Item 5 **Option B** (remove Options A/C branching from the active design; keep concise pointer to `research/count-tokens-and-settings.md` for rejected options).
   - Inspect exact upstream `v0.2.23` `frontend/src/views/admin/SettingsView.vue` Request Rectifier markup (`lines ~554–746`) and confirm the new sub-option matches sibling sub-options (`thinking_signature_enabled`, `thinking_budget_enabled`, `apikey_signature_enabled`) **1:1** in DOM hierarchy, Tailwind classes, `dark:` variants, Toggle component, spacing, and accessibility (`component-guidelines.md:12,81-82,94-98,108`). Record exact verified markup contract (no extra cards, subtitles, or non-native wrappers).
   - Document the real-browser Playwright Chromium verification scope (synthetic mock API, light/dark + en/zh, zero console/page errors, zero overflow, layout parity with sibling toggles, temp preview cleanup).

3. **`implement.md`**:
   - Update Section 1 to reflect locked plugin name (`plugins/gemini-signature-rectifier`) and locked Item 5 (`Option B`); leave only final plan approval (including R6 default + UI preview) and implementation stage approval as gates before `task.py start`.
   - Use `PYTHONDONTWRITEBYTECODE=1 python3 -B` consistently in all Python build commands.
   - Add an explicit **Playwright Chromium real-browser visual check** step in validation/review (Section 5/6): render the patched native `SettingsView.vue` Request Rectifier card in Playwright Chromium with synthetic API mocks across light/dark and en/zh, inspect screenshots for alignment/contrast/wrapping parity and zero console/page errors, and remove temporary preview files/processes before handoff.

4. **`implement.jsonl` and `check.jsonl`**:
   - Add missing relevant spec entries so Phase 2 agents receive complete cross-layer context:
     - `.trellis/spec/backend/database-guidelines.md`
     - `.trellis/spec/frontend/index.md`
     - `.trellis/spec/frontend/directory-structure.md`
     - `.trellis/spec/frontend/type-safety.md`
     - `.trellis/spec/guides/cross-layer-thinking-guide.md`
   - Verify every JSONL line is valid JSON and every referenced file path exists.

### 2. Render Real-Browser Frontend Preview Screenshots (Isolated `/tmp` Preview)

Produce genuine Playwright Chromium screenshots of the **real Sub2API `v0.2.23` Vue 3 + Tailwind `SettingsView.vue` Request Rectifier card** with the proposed toggle added:

1. Use an isolated temporary directory `/tmp/gemini-rectifier-ui-preview/` (do NOT touch the repo tree).
   - Fetch or unpack public `Wei-Shaw/sub2api` `v0.2.23` frontend cleanly (unauthenticated public download only; reuse any clean local cache if present and verified against `v0.2.23`).
   - Apply ONLY the proposed 4 frontend edits (`frontend/src/api/admin/settings.ts`, `frontend/src/views/admin/SettingsView.vue`, `frontend/src/i18n/locales/en/admin/settings.ts`, `frontend/src/i18n/locales/zh/admin/settings.ts`) inside `/tmp/gemini-rectifier-ui-preview/`.
   - Run `pnpm run check:i18n` and verify the frontend compiles cleanly (`vue-tsc` / Vite).
2. Serve the real patched frontend on a local ephemeral port (e.g., `127.0.0.1`) and open `/admin/settings` in **Playwright Chromium** (`viewport: 1440x900`, `deviceScaleFactor: 2`):
   - Intercept `/api/v1/**` via Playwright `page.route` and return **synthetic** admin auth + settings + rectifier settings (`enabled: true`, `thinking_signature_enabled: true`, `thinking_budget_enabled: true`, `apikey_signature_enabled: false`, `gemini_native_signature_enabled: true`, plus valid empty/synthetic rules arrays). Zero real credentials or account data.
   - Ensure the actual Sub2API app shell, theme (`light` / `dark`), i18n (`zh` / `en`), Tailwind CSS, and `SettingsView.vue` render cleanly with **0 console errors** and **0 page errors**.
   - Scroll to / locate the **Request Rectifier** card (and verify full-card visibility including master toggle, all 4 sub-options, and Save button).
3. Capture crisp Retina PNG screenshots under `/tmp/gemini-rectifier-ui-preview/screenshots/`:
   - `rectifier-zh-light.png` — Chinese, Light mode, Request Rectifier card expanded
   - `rectifier-zh-dark.png` — Chinese, Dark mode, Request Rectifier card expanded
   - `rectifier-en-light.png` — English, Light mode, Request Rectifier card expanded
4. In the same Playwright run, exercise real DOM interactions and record metrics:
   - Verify sibling sub-option vs new sub-option row geometry (bounding box height, left/right alignment, toggle position, zero horizontal overflow).
   - Toggle `gemini_native_signature_enabled` OFF and click Save; verify the intercepted `PUT /api/v1/admin/settings/rectifier` JSON payload contains `"gemini_native_signature_enabled": false` and preserves sibling fields.
   - Toggle the master Request Rectifier switch OFF and confirm the new sub-option hides together with sibling sub-options.
5. **Visually inspect every generated PNG yourself** to confirm zero clipped text, broken icons, overlap, low contrast, or unintended styling.
6. **Clean up processes**: terminate the temporary Vite/HTTP server cleanly and verify no preview server process remains running. Keep `/tmp/gemini-rectifier-ui-preview/screenshots/*.png` in place for coordinator and user inspection (report exact paths).

## Final Report Format

Report concisely via `hc send t53` with:
- Updated planning files and confirmation that `plugins/gemini-signature-rectifier` and Item 5 Option B are locked and JSONL/links pass.
- Exact paths of the generated Retina PNG screenshots.
- Exact real-browser metrics: console error count, page error count, overflow check, sibling alignment/geometry parity, interactive PUT payload verification, and master-toggle visibility check.
- Confirmation that temporary preview server processes are stopped and no repo production/test/submodule/Git state was modified.
