# Update codex-candy-eval Plugin and Sync Upstream

## Goal

Update `plugins/codex-candy-eval` to restore three omitted capabilities (`跨供应商评估`, `指纹巡检`, and `名称／邮箱匹配巡检`) and synchronize upstream `v0.4.6` features and version number from `haowang02/cpa-plugin-codex-candy-eval`.

## Scope and Confirmed Product Decisions

1. **Cross-Provider Evaluation & Unrestricted Group Selection (`跨供应商评估与全分组支持`)**:
   - Adapt cross-provider evaluation to Sub2API's native multi-platform account system across all Sub2API groups and platforms (including `composite` groups, `openai`, `anthropic`, `gemini`, `antigravity`, and all OpenAI/Anthropic-compatible platforms across `oauth`, `setup-token`, `apikey`, and `upstream` credential types).
   - Remove all platform filtering from group and account selectors (`loadGroups` / `refreshCatalog` and `fetchNativeAccounts`) so all Sub2API groups are selectable directly.
   - Perform backend protocol translation between `openai-response` evaluation requests and each Sub2API account's native wire protocol.
   - Synchronize the frontend `<test>-credential-type` filter (`credentials.js`) so users can filter accounts by platform and credential type.
   - Do not read external local CPA authentication files from disk.
2. **Fingerprint Inspection, Single-Run Verdict, Mode-Aware `下次巡检` Display & Wildcard Matching (`指纹巡检` + `名称／邮箱匹配巡检`)**:
   - Add an inspection check-mode selector (`检查方式`: `candy` `糖果` or `fingerprint` `指纹`) to the native `自动巡检` (`inspection`) settings UI and backend coordinator.
   - Compute degradation verdicts per check mode: `Status == "wrong"` for `candy` (with `MaxTestsPerAccount` confirmation on state transitions), and `fingerprintModelID(Model) != fingerprintModelID(Attribution.Prediction)` for `fingerprint` on concluded runs (`Status == "completed" || Status == "partial"` with non-nil `Attribution`).
   - In `fingerprint` inspection mode, execute **1 fingerprint evaluation (3 challenges)** per account and apply state transitions directly without running `MaxTestsPerAccount - 1` extra fingerprint confirmation rounds or `240s` recovery wait (preventing `3 × 3 = 9` challenge rounds).
   - Move the original 3-span `#inspection-status` status bar (`#inspection-phase`, `#inspection-next` `下次巡检：...`, `#inspection-progress`) dynamically into the account header of the tab matching `test_type` (`糖果` `#candy-credentials` when `candy`, `指纹` `#fp-credentials` when `fingerprint`). Do **not** add any unsolicited `本轮...巡检` (`#inspection-round-summary` / `RoundSummary`) text or fields.
   - Add `INCLUDE` and `EXCLUDE` wildcard filter settings (`include_patterns` and `exclude_patterns`) to the native `自动巡检` settings UI and backend coordinator, matching against account `name` and `email` via `path.Match`.
3. **Upstream `v0.4.6` Feature and Version Sync (`同步上游更新`)**:
   - Synchronize the fourth evaluation tab **SIWC (`Sign In With ChatGPT · 授权状态`)** (`siwc.go`, `web/siwc.js`, `ui.html`), sending a 1-shot minimal Responses streaming probe (`{"model": model, "store": false, "stream": true, "input": [{"role": "user", "content": "Reply with OK."}]}` with `User-Agent: cpa-siwc-check/0.4.6`) via `SendCodexEvaluation` and classifying `available` (`SIWC 可用`), `restricted` (`订阅共享受限` / `subscription_sharing_user_not_eligible`), `limited` (`额度或频率受限`), `auth_error` (`认证异常`), `cancelled`, and `failed`.
   - Upgrade persisted evaluation history to `stateSchemaVersion = 3` (`siwc` bucket in `historyState`, retaining v0/v1/v2 migration backups).
   - Synchronize upstream `v0.4.5`–`v0.4.6` frontend module extractions (`web/storage.js` and `web/credentials.js`).
   - Update `pluginVersion` in `backend/internal/codexeval/web.go` from `"0.3.14"` to `"0.4.6"`.
   - Update `plugins/codex-candy-eval/README.md` and parent `README.md` feature tables if needed to reflect the restored and synchronized capabilities.

## Requirements

- **R1 (Cross-Provider Evaluation & Unrestricted Group Selection)**: Allow all Sub2API groups (including `composite` and all platform groups) without platform filtering in `/admin/codex-eval`, and support accounts across `openai`, `anthropic` (Claude), `gemini`, `antigravity`, and OpenAI/Anthropic-compatible platforms in `Candy`, `Fingerprint`, and `Code` evaluations with frontend credential-type filtering.
- **R2 (Fingerprint Inspection Single-Run Verdict & Mode-Aware `下次巡检` Display)**: Support selecting `candy` (`糖果`) or `fingerprint` (`指纹`) in the `自动巡检` settings UI and backend coordinator; run 1 fingerprint evaluation (3 challenges) per account in `fingerprint` mode without multi-run confirmation loops; display the original 3-span `#inspection-status` (`#inspection-phase`, `#inspection-next`, `#inspection-progress`, without any added `本轮...巡检` round-summary text) in the account header of the selected mode's tab (`糖果` or `指纹`).
- **R3 (Name / Email Wildcard Inspection Filtering)**: Support `include_patterns` (`INCLUDE`) and `exclude_patterns` (`EXCLUDE`) wildcard filters in the `自动巡检` settings UI and backend coordinator, matching against account `name` and `email` with `path.Match`.
- **R4 (Upstream `v0.4.6` Sync — SIWC, History v3, Version)**: Add the `SIWC` evaluation tab for OpenAI OAuth accounts (`evaluateSIWC` 1-shot Responses streaming probe with `User-Agent: cpa-siwc-check/0.4.6`), upgrade history state schema to v3 (`siwc` records), extract `storage.js` and `credentials.js`, and set `pluginVersion = "0.4.6"`.
- **R5 (Sub2API `v0.2.20` Baseline Upgrade)**:
  - Upgrade the upstream Sub2API baseline from `v0.2.19` to `v0.2.20` across the parent repository and plugin submodules (`codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`), adapting patches, workflow defaults (`build.yml`), and test fixtures so `python3 scripts/build.py` targets `v0.2.20` cleanly.
- **R6 (Unit/JSDOM Tests, Live Runtime & Browser Verification, and Documentation)**:
  - Add focused backend (`go test`) and frontend (`node tests/test_ui.cjs`) tests in `plugins/codex-candy-eval/tests/` covering multi-provider evaluation, fingerprint inspection mode, wildcard name/email matching, SIWC execution, history v3 migration, and `pluginVersion = "0.4.6"`.
  - Update `tests/native_inspection_fixture.py` and `tests/native_fixture_supplier.py` and execute live end-to-end runtime and real-browser verification against the retained `sub2api-codex-eval-test` container (`127.0.0.1:18081` synthetic supplier, zero external paid API calls) across all 5 tabs (`糖果`, `指纹`, `鹈鹕`, `SIWC`, `设置`), both inspection check modes (`candy` / `fingerprint`), and `INCLUDE` / `EXCLUDE` wildcard filters on the `v0.2.20` binary.
  - Update `plugins/codex-candy-eval/README.md` and parent `README.md`.

## Constraints

- Keep all changes inside `Sub2API-Plugins` and its plugin submodules (`plugins/codex-candy-eval`, `plugins/sub2api-quota-extension`, `plugins/sub2api-plugin-template`).
- Preserve existing Sub2API security boundaries: never leak raw credentials, tokens, or proxy URLs to the browser.
- Maintain clean patch application against the Sub2API `v0.2.20` baseline via `python3 scripts/build.py`.

## Acceptance Criteria

- [x] Group and account selectors in `/admin/codex-eval` allow all Sub2API groups without platform filtering (including `composite` and all provider platforms), and `<test>-credential-type` filters accounts by platform/type (`SIWC` filters to OpenAI OAuth accounts).
- [x] `SendCodexEvaluation` and `CodexEvalModels` support `openai`, `anthropic` (Claude), `gemini`, `antigravity`, and OpenAI/Anthropic-compatible accounts by translating `openai-response` requests and streaming `openai-response` SSE events.
- [x] `自动巡检` settings UI and backend coordinator support selecting check mode (`candy` / `fingerprint`) and configuring `INCLUDE` / `EXCLUDE` name/email wildcard patterns, run 1 three-challenge fingerprint evaluation per account without multi-run confirmation in `fingerprint` mode, and place the original 3-span `#inspection-status` (`#inspection-phase`, `#inspection-next`, `#inspection-progress`, with no added `本轮...巡检` summary) in the active check mode's tab (`糖果` vs `指纹`).
- [x] The `SIWC` tab runs against OpenAI OAuth accounts via a 1-shot minimal Responses streaming probe (`User-Agent: cpa-siwc-check/0.4.6`), classifies `available` / `restricted` / `limited` / `auth_error` / `failed`, persists records in history schema v3 (`history.v2.json` backup on upgrade), and displays `版本 v0.4.6` in the UI footer.
- [x] All plugin patches, workflow defaults (`build.yml`), and tests are upgraded to Sub2API `v0.2.20`, and `python3 scripts/build.py` in `plugins/codex-candy-eval` and parent `Sub2API-Plugins` passes all Go, frontend, and integration tests cleanly against `v0.2.20`.
- [x] Live container and real-browser verification (`sub2api-codex-eval-test` + `native_fixture_supplier.py` + Playwright browser) passes on `sub2api-plugins-v0.2.20-linux-amd64` for unrestricted group selection, multi-provider evaluations, `SIWC` checks, history v3 persistence, `设置` Row 1/Row 3 layout at `1280px` and `430px`, mode-aware `下次巡检` display on `糖果` and `指纹` tabs, and single-run `fingerprint` + `candy` `立即巡检` execution with `INCLUDE`/`EXCLUDE` wildcard matching, leaving zero console errors and restoring default fixture state.
