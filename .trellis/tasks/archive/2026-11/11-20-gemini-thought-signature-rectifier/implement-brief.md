# Phase 2 Implementation & Verification Brief

Active task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier` (status: `in_progress`, user-approved for Phase 2 local implementation)
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any internal subagent from running `hc send`.

## Read First

1. `.trellis/tasks/11-20-gemini-thought-signature-rectifier/prd.md`
2. `.trellis/tasks/11-20-gemini-thought-signature-rectifier/design.md`
3. `.trellis/tasks/11-20-gemini-thought-signature-rectifier/implement.md`
4. All 20 specs/research entries in `implement.jsonl` and `check.jsonl`

## Hard Boundaries & Anti-Bloat Rules

1. **Zero Git commits / zero remote operations**:
   - Do **NOT** run `git commit`, `git push`, `gh`, or any authenticated Git/GitHub operation in either the parent repo or `plugins/gemini-signature-rectifier`.
   - Before touching `.gitmodules` or creating `plugins/gemini-signature-rectifier`, inspect `scripts/build.py:54-80`, `tests/test_build.py`, and `.gitmodules` to confirm exact discovery and test expectations for an uncommitted local plugin submodule.
   - Do **NOT** put temporary `/tmp` or local filesystem paths in `.gitmodules`. If any check in `scripts/build.py` or `tests/test_build.py` strictly requires a gitlink commit that cannot pass uncommitted, **STOP and report that exact blocker** rather than committing.
   - Preserve all existing dirty/untracked files and do **NOT** modify `plugins/codex-candy-eval`, `plugins/sub2api-quota-extension`, or `plugins/sub2api-plugin-template`.
2. **Zero redundant fallbacks, zero speculation, zero redundant compatibility**:
   - Follow the debloated `design.md` strictly:
     - `UpdateRectifierSettingsRequest.GeminiNativeSignatureEnabled` is a plain `bool` (no `*bool`, no preliminary read).
     - Leave `GetRectifierSettings` unchanged.
     - Leave constructors, providers, `wire_gen.go`, Claude `Forward`, handler pre-cleaning, Antigravity `ForwardGemini`, exported `CleanGeminiNativeThoughtSignatures`, and `estimateGeminiCountTokens` unchanged.
     - Cleaner implements ONLY the 4 deterministic rules on direct `contents[].parts[]` using `json.RawMessage` (no dual-alias conflict checks, no guessed metadata/media field dictionaries).
     - Matcher checks ONLY normalized `thoughtsignature` on `extractUpstreamErrorMessage` output (HTTP 400 enforced by caller; no guessed verb list, no raw-body fallback).
     - Ops events use ONLY the 3 verified `v0.2.23` kinds (`signature_error`, `signature_retry`, `signature_retry_request_error`), with `signature_retry` only on HTTP `>=400`, no signature event when `changed == false`, and `isSignatureRetryAttempt` cleared immediately after the resend outcome.
     - Setting default `false`, `IsGeminiNativeSignatureRectifierEnabled(ctx)` returns `settings.Enabled && settings.GeminiNativeSignatureEnabled` and `false` on read error; guard `s.rateLimitService != nil && s.rateLimitService.settingService != nil` cleanly in one expression.
     - Locked en/zh copy verbatim (from `design.md`), initial Vue form value `false`, exact sibling markup + `for`/`id`/`aria-label`/`aria-describedby`.
3. **Code quality & anti-bloat**:
   - No split files that belong in one cohesive unit, no runtime version checks, no unused constants/env vars/exported internal types, no pass-through wrappers/re-exports/single-call helpers/redundant params/duplicate fields, no crowded multi-statement lines, no braceless `if`/`for` blocks, include concise contract comments where helpful.
   - Keep `patches/gemini-signature-rectifier.patch` strictly production code (zero test files or fixtures inside the patch).
   - Keep `plugins/gemini-signature-rectifier/tests/` completely flat; unmount every Vue wrapper in `finally`; format all changed/added Go files with `gofmt`.
   - Keep root `plugins/gemini-signature-rectifier/LICENSE` as unmodified LGPLv3 text and retain inherited notices under `licenses/`. Keep Chinese usage instructions in `plugins/gemini-signature-rectifier/README.md` with no nested `.trellis/`, `.agents/`, or `docs/`.
4. **Python, caches, and process cleanup**:
   - Always run Python with `PYTHONDONTWRITEBYTECODE=1 python3 -B` and immediately remove any `__pycache__` / `.pyc` created.
   - Use `/usr/bin/trash` when deleting untracked temporary directories/files.
   - Never leave background Vite/preview/Playwright processes running.

## Execution Steps

1. **Create `plugins/gemini-signature-rectifier`** from the complete `plugins/sub2api-plugin-template` kit (`scripts/build.py`, `scripts/installer/*.go`, `.github/workflows/build.yml`, `.gitignore`, `LICENSE`, `licenses/*`, `tests/support.py`, `tests/test_build.py`, `tests/test_installer_test.go`), update its Chinese `README.md`, and register it cleanly in parent `.gitmodules` (preserving existing submodule entries and format).
2. **Implement the single cohesive production patch** (`plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch`) against pristine public `Wei-Shaw/sub2api@v0.2.23` (unauthenticated public fetch only; `gofmt` all 6 Go files; verify `git apply --check --binary` and `git diff --check`).
3. **Implement the 4 flat focused test suites** under `plugins/gemini-signature-rectifier/tests/`:
   - `test_gemini_native_signature_rectifier_test.go` (`// sub2api-package: backend/internal/service`)
   - `test_rectifier_settings_test.go` (`// sub2api-package: backend/internal/service`)
   - `test_rectifier_settings_handler_test.go` (`// sub2api-package: backend/internal/handler/admin`)
   - `test_rectifier_settings.test.ts` (real `SettingsView.vue` + `Toggle`, synthetic mocks, `finally` unmount)
   Format all 3 Go test suites with `gofmt`.
4. **Run BOTH established builds pinned to `UPSTREAM_TAG=v0.2.23`**:
   - **Combined build** (parent root, retaining `/tmp/gemini-rectifier-combined` temporarily so Step 5 reuses its built patched frontend with zero duplicate frontend build!):
     ```sh
     UPSTREAM_TAG=v0.2.23 SUB2API_BUILD_STAGE=source SUB2API_BUILD_WORKSPACE=/tmp/gemini-rectifier-combined PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
     UPSTREAM_TAG=v0.2.23 SUB2API_BUILD_STAGE=resume SUB2API_BUILD_WORKSPACE=/tmp/gemini-rectifier-combined PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
     ```
     (Check whether parent `dist/build` already has prior outputs; note exact output paths and timestamps.)
   - **Standalone build** (inside `plugins/gemini-signature-rectifier`):
     ```sh
     UPSTREAM_TAG=v0.2.23 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
     ```
5. **Phase 2.2 Playwright Chromium real-browser check** on the **final built patched frontend** from `/tmp/gemini-rectifier-combined`:
   - Serve built frontend on loopback, open `/admin/settings` in Playwright Chromium at `1440×900`, `deviceScaleFactor: 2`, with synthetic mocked APIs (zero real credentials/data).
   - Verify **initial default `false`** across all 4 locale/theme combinations (`zh-light`, `zh-dark`, `en-light`, `en-dark`):
     - 0 console errors, 0 page errors, 0 application error toasts, 0 horizontal overflow, 0 px row/toggle alignment difference vs sibling controls.
   - Capture fresh Retina PNG screenshots under `/tmp/gemini-rectifier-phase2-screenshots/`:
     - `rectifier-zh-light-default-false.png`
     - `rectifier-zh-dark-default-false.png`
     - `rectifier-en-light-default-false.png`
     - `rectifier-en-dark-default-false.png`
   - Exercise full interactive round-trip:
     - Initial state is `false` → enable → click Save → verify PUT payload has `"gemini_native_signature_enabled": true` & siblings unchanged → reload page → verify toggle remains `true`.
     - Disable → click Save → verify PUT payload has `"gemini_native_signature_enabled": false` & siblings unchanged → reload page → verify toggle remains `false`.
     - Turn master toggle OFF → verify all 4 sub-options hide together.
   - Visually inspect every generated PNG yourself.
   - Stop preview server & browser cleanly; verify port closed; move `/tmp/gemini-rectifier-combined`, any temporary authoring tree, and any `.playwright-cli/` in repo root to `/usr/bin/trash`. Keep `/tmp/gemini-rectifier-phase2-screenshots/` and `/tmp/gemini-rectifier-phase2-evidence.md` for coordinator review.
6. **Write concise evidence report** to `/tmp/gemini-rectifier-phase2-evidence.md` containing:
   - Exact file list created/modified, patch stats (`diffstat` + line counts), and confirmation of zero test files in patch.
   - Exact Go, Vitest, i18n, `vue-tsc`, Vite, standalone build, and combined build commands, exit codes, counts, and output timestamps.
   - Exact Playwright Chromium measurements, interactive PUT payloads, and screenshot paths.
   - Confirmation that temporary servers/workspaces/caches are cleaned up and no Git commit or remote operation occurred.

## Final Callback

Report completion or any blocker concisely via `hc send t53` referencing `/tmp/gemini-rectifier-phase2-evidence.md`.
