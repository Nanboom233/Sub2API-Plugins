# Phase 2 Implementation Brief: Adapt Quota Plugin to Sub2API v0.2.24

Active task: `.trellis/tasks/11-21-adapt-sub2api-v0224` (status: `in_progress`, user-approved for Phase 2)
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any internal subagent from running `hc send`.

## Read First

1. `.trellis/tasks/11-21-adapt-sub2api-v0224/prd.md`
2. `.trellis/tasks/11-21-adapt-sub2api-v0224/design.md`
3. `.trellis/tasks/11-21-adapt-sub2api-v0224/implement.md`
4. `.trellis/tasks/11-21-adapt-sub2api-v0224/research/v0224-upstream-diff.md`
5. All entries in `implement.jsonl` and `check.jsonl`

## Hard Boundaries & Anti-Bloat Rules

1. **Touch ONLY `plugins/sub2api-quota-extension`**:
   - Target files:
     - `plugins/sub2api-quota-extension/patches/quota-extension.patch` (adapt `frontend/src/utils/accountUsageRefresh.ts`, `frontend/src/components/account/AccountUsageCell.vue`, `frontend/src/views/admin/AccountsView.vue` onto upstream `v0.2.24` unified `buildAccountUsageRefreshKey` + single `{ data, ts, refreshKey }`, preserving all other backend/editor/display hunks)
     - `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts`
     - `plugins/sub2api-quota-extension/tests/test_usage_batch.test.ts`
   - Do **NOT** modify `plugins/codex-candy-eval`, `plugins/gemini-signature-rectifier`, `plugins/sub2api-plugin-template`, `.gitmodules`, `.trellis/spec/`, `test_quota_editor.test.ts`, or quota Go suites unless a concrete test/build failure proves a required fix (if so, report clearly).
   - Keep zero test files inside `quota-extension.patch`; keep `plugins/sub2api-quota-extension/tests/` completely flat; unmount every Vue wrapper in `finally`.
2. **Strict architectural unification (zero redundancy)**:
   - Plug `account.type === 'apikey'` into upstream `buildAccountUsageRefreshKey` (extending `Pick<Account, ...>` with `credentials` and `proxy_id`, reusing `serializeSnapshotRefreshValue`).
   - Delete `buildAPIKeyUsageRefreshKey`, `apiKeyUsageRefreshKey` computed, `config` cache fields, `capturedConfigByAccountId`, and extra invalidation watchers.
   - Keep upstream `{ data, ts, refreshKey }`, upstream `refreshKeys` map (`AccountsView.vue:804`), upstream `usageBatchRequestTokenByAccountId`, and upstream `shouldReplaceAutoRefreshRow` unchanged.
   - Add ONLY the minimal current-key checks on single and batch async success/error replies and the `apikey` branch in upstream's single `watch(usageRefreshKey, ...)`.
   - Record exact before vs after hunk and changed-line counts for the 3 refresh targets against the audited `21 hunks / 110 changed lines` baseline.
3. **Zero commits / zero credentials / clean caches**:
   - Do **NOT** run `git commit`, `git push`, `gh`, or any authenticated Git/GitHub operation.
   - Use `PYTHONDONTWRITEBYTECODE=1 python3 -B` for every Python invocation; create zero new `.pyc` files; preserve pre-existing `.trellis/scripts/common/__pycache__`.
   - Use `/usr/bin/trash` to remove temporary workspaces/authoring dirs/helpers/browser data after checks; never leave background server or browser processes running.

## Execution & Verification Sequence

1. **Adapt patch & tests** in an isolated temporary `v0.2.24` (`5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`) authoring workspace (unauthenticated public fetch only):
   - Verify `git diff --check`, forward `git apply --check --binary` on pristine `v0.2.24` alone AND after `codex-candy-eval` + `gemini-signature-rectifier` patches.
   - Run internal `trellis-check` (read-only/fix loop) against the adapted patch & tests BEFORE final builds (forbid subagents from running `hc send`).
2. **Run BOTH established builds** (with inputs frozen):
   - **Quota standalone build** (from `plugins/sub2api-quota-extension`):
     ```sh
     GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 UPSTREAM_TAG=v0.2.24 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
     ```
   - **Argument-free combined build** (from `/Users/minami/Code/S/Sub2API-Plugins`, confirming `UPSTREAM_TAG`, `SUB2API_BUILD_STAGE`, `SUB2API_BUILD_WORKSPACE`, `SUB2API_BUILD_PLATFORMS` are ALL unset):
     ```sh
     GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
     ```
   - Confirm the combined build auto-selects `v0.2.24` (`5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`), applies all 3 plugins, passes all focused/common Go, Vitest, i18n, `vue-tsc`, Vite, vet, Python, and installer checks, and publishes 5 platform program/installer pairs in BOTH output roots.
3. **Phase 2.2 Playwright Chromium real-browser check** (reusing the newly built host `darwin-arm64` combined executable — ZERO duplicate frontend rebuild!):
   - Create a fresh empty temp dir `/tmp/sub2api-v0224-browser` and launch:
     ```sh
     hc run --bg --name v0224-browser --cwd /tmp/sub2api-v0224-browser env AUTO_SETUP=false SKIP_SETUP=false DATA_DIR=/tmp/sub2api-v0224-browser/data SERVER_HOST=127.0.0.1 SERVER_PORT=4180 /Users/minami/Code/S/Sub2API-Plugins/dist/build/darwin-arm64/sub2api-plugins-v0.2.24-darwin-arm64
     ```
   - Verify `GET http://127.0.0.1:4180/setup/status` readiness; do NOT submit setup APIs.
   - Open `/admin/accounts` in Playwright Chromium (`1440×900`, `deviceScaleFactor: 2`) with synthetic intercepted auth, setup status, and accounts/usage responses (include Claude 5h/7d stats & estimated total costs + custom API-key quota bars + zero balance + reset tooltips).
   - Capture 4 crisp Retina PNG screenshots under `/tmp/sub2api-v0224-screenshots/`:
     - `accounts-zh-light.png`
     - `accounts-zh-dark.png`
     - `accounts-en-light.png`
     - `accounts-en-dark.png`
   - Visually inspect all 4 PNGs yourself! Verify readable cost text, custom API-key bars, zero balance, reset tooltips, 0 console errors, 0 page errors, 0 application error toasts, 0 horizontal overflow.
   - Exercise snapshot refresh, saved-configuration refresh, and native repeated-token-refresh warning.
   - Stop Chromium and `v0224-browser` (`hc kill` + `hc rm`), verify port 4180 closed, and move temporary authoring/browser workspaces and any `.playwright-cli/` to `/usr/bin/trash`. Keep `/tmp/sub2api-v0224-screenshots/` and `/tmp/sub2api-v0224-phase2-evidence.md` for coordinator review.
4. **Write concise evidence report** to `/tmp/sub2api-v0224-phase2-evidence.md` with:
   - Before vs after patch hunk & changed-line counts for the 3 refresh targets and full patch diffstat.
   - Exact standalone and combined build commands, selected tag/commit, exit codes, test counts, and exact paths/sizes/timestamps for all 10 published files in both output roots.
   - Exact Playwright Chromium measurements, interactive verification results, and screenshot paths.
   - Confirmation of cleanup and zero commits/pushes/GitHub credential usage.

## Final Callback

Report completion or any blocker concisely via `hc send t53` referencing `/tmp/sub2api-v0224-phase2-evidence.md`.
