# Implementation Plan: Update codex-candy-eval and Sync Upstream v0.4.6

## Ordered Execution Checklist

1. **Stage Sub2API `v0.2.20` Workspace for Patch Authoring & Baseline Upgrade**:
   - Inspect `plugins/codex-candy-eval/patches/0001` through `0007` and `plugins/sub2api-quota-extension/patches/quota-extension.patch` against Sub2API `v0.2.20`, regenerate any patches with shifted context or upstream API updates, and update `v0.2.19` baseline references in `.github/workflows/build.yml` and test fixtures across the four repositories (`Sub2API-Plugins`, `codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`) to `v0.2.20`.
2. **Update `0001-evaluation-core.patch` (SIWC Core, History v3, Fingerprint Helper)**:
   - Add `backend/internal/codexeval/siwc.go` implementing SIWC run orchestration (`type: "siwc"`), 1-shot minimal Responses streaming probe (`{"model": model, "store": false, "stream": true, "input": [{"role": "user", "content": "Reply with OK."}]}` with `User-Agent: cpa-siwc-check/0.4.6`), and `available` / `restricted` / `limited` / `auth_error` / `cancelled` / `failed` outcome classification.
   - Update `state.go`, `history.go`, and `runs.go` to bump `stateSchemaVersion = 3`, add the `siwc` bucket to `historyState`, save `history.v2.json` backup during v2-to-v3 migration, and support `siwc` in `Start`, `Record`, and `Clear`.
   - Export `FingerprintModelID(model string) string` in `fingerprint.go` so `inspection.go` can compare model IDs and attribution predictions.
3. **Update `0004-admin-channel.patch` (Cross-Provider Evaluation, All-Platform Support & SIWC Transport)**:
   - Update `isCodexEvalAccountSupported`, `CodexEvalAccount`, and `CodexEvalModels` in `account_codex_eval_service.go` to accept accounts across all Sub2API platforms (`openai`, `anthropic`, `gemini`, `antigravity`, `grok`, `kimi`, `zhipu`, `deepseek`, `minimax`, `opencode_go`, `typesafe`, `command_code`, `cline`) and credential types (`oauth`, `setup-token`, `apikey`, `upstream`).
   - Extend `SendCodexEvaluation` to translate OpenAI Responses requests and stream Responses SSE events for `anthropic` (and Anthropic-protocol upstream accounts), `gemini` / `antigravity`, and `openai` / OpenAI-compatible accounts.
   - Support `cpa-siwc-check/` probes in `SendCodexEvaluation` through native non-Responses-Lite OAuth model and payload normalization (`normalizeOpenAIModelForUpstream` before `normalizeCodexOAuthNonLitePayload`) and bound `siwc_access_token` credentials.
4. **Update `0005-inspection.patch` (Single-Run Fingerprint Inspection, All-Platform Eligibility, Wildcard Matching & Remove `RoundSummary`)**:
   - Add `TestType` (`"candy"` / `"fingerprint"`), `IncludePatterns`, and `ExcludePatterns` to `InspectionSettings` in `inspection_settings.go`, with `path.Match` validation and unrestricted platform prefix support in `validInspectionAccountType`.
   - Add `Email` to `InspectionAccount` (extracted from `account.Extra` / `account.Credentials` in `codex_inspection_handler.go`), allow all supported Sub2API account platforms in `isInspectionSupportedAccount`, and filter accounts by `IncludePatterns` and `ExcludePatterns` using `path.Match` on `Name` and `Email`.
   - Update `run` and `testPhase` in `inspection.go`: in `testType == "fingerprint"`, execute 1 fingerprint evaluation (3 challenges) per account and immediately apply state transitions (`r.TargetPriority = &p; r.Outcome = "recommended"`, `apply(a, target)`) without `recovery_wait` or `MaxTestsPerAccount - 1` confirmation runs (`batches := 1`); completely remove `InspectionRoundSummary` and `RoundSummary` from `InspectionState`.
5. **Update `0006-evaluation-ui.patch` (Upstream `v0.4.6` UI, Unrestricted Groups, Mode-Aware `下次巡检`, SIWC Tab, Inspection Controls & Remove `#inspection-round-summary`)**:
   - Set `const pluginVersion = "0.4.6"` in `backend/internal/codexeval/web.go` and embed `web/storage.js`, `web/credentials.js`, and `web/siwc.js`.
   - Update `web/catalog.js` and `web/credentials.js` to load all Sub2API groups and accounts without `SUPPORTED_PLATFORMS` filtering (`groups = available || [];` and `const items = data.items || [];`), add `PLATFORM_LABELS` for all Sub2API platforms, integrate `<test>-credential-type` filtering (`all` or `<platform>:<type>`, restricted to `openai:oauth` on `siwc`), and wire the `SIWC` tab (`#tab-siwc` button text `SIWC`).
   - Update `web/ui.html`, `web/components.js`, `web/inspection.js`, and `web/style.css` to add the check-mode selector (`检查方式`: `糖果` / `指纹`), `INCLUDE` / `EXCLUDE` wildcard pattern inputs, remove `#inspection-round-summary` and `formatInspectionRoundSummary` (`本轮...巡检`), and add `syncInspectionStatusPlacement()` so the original 3-span `#inspection-status` (`#inspection-phase`, `#inspection-next` `下次巡检：...`, `#inspection-progress`) moves between `#candy-credentials .credential-head` and `#fp-credentials .credential-head` according to `test_type`.
6. **Upgrade Sub2API Baseline to `v0.2.20` Across All 4 Repositories**:
   - Adapt `plugins/codex-candy-eval/patches/0004-admin-channel.patch` (`convertClaudeMessagesToGeminiGenerateContent(claudeBody, model)` and `geminiTextDelta.next` in `account_codex_eval_service.go`, plus `http_upstream.go` hunk offset) and `0007-sub2api-integration.patch` (`embed_on.go`, `AppSidebar.vue`, `routes/admin.go`, `admin_account.go`, `router/index.ts`) against `/tmp/sub2api-v0.2.20-base`.
   - Rebase `plugins/sub2api-quota-extension/patches/quota-extension.patch` (`backend/go.mod`, `account_usage_service.go` preserving `scopedAccountAccess`, `CreateAccountModal.vue`, `EditAccountModal.vue`, and shifted files) against `/tmp/sub2api-v0.2.20-base`, verifying both standalone and combined patch application.
   - Update `.github/workflows/build.yml` (`default: v0.2.20`) and `tests/test_installer_test.go` (`Candidate: "0.2.20"`) identically across all 4 repositories (`Sub2API-Plugins`, `codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`).
   - Update `plugins/codex-candy-eval/tests/native_inspection_fixture.py`, root `README.md`, `plugins/sub2api-plugin-template/README.md`, and `.trellis/spec/backend/{index.md,minimal-linux-delivery.md,quality-guidelines.md,runtime-installation.md,api-key-quota.md}` to `v0.2.20`.
7. **Update Automated Tests, Live Fixture Scripts, and Documentation**:
   - Update `tests/test_codexeval_runtime_test.go` to test SIWC run/cancel/detail/clear, `schema_version` 2->3 migration (`history.v2.json` backup), and `pluginVersion = "0.4.6"`.
   - Update `tests/test_codexeval_inspection_test.go` to test single-run `TestType: "fingerprint"` degradation/recovery verdicts without confirmation loops, all-platform account eligibility, and `IncludePatterns` / `ExcludePatterns` matching on `Name` and `Email`.
   - Update `tests/test_service_account_codex_eval_service_test.go` to test cross-provider `SendCodexEvaluation` / `CodexEvalModels` (`anthropic`, `gemini`, `antigravity`, `openai`) and `cpa-siwc-check/` probe handling.
   - Update `tests/test_service_codex_inspection_settings_test.go` and `tests/test_admin_codex_inspection_handler_test.go` to test persistence of `test_type`, `include_patterns`, and `exclude_patterns`, and account `Email` extraction.
   - Update `tests/test_ui.cjs` to test the updated Settings layout (`模型` / `推理强度` / `检查方式` on row 1, `include_patterns` / `exclude_patterns` on row 3), multi-provider credential filtering, and the `SIWC` tab.
   - Update `tests/native_inspection_fixture.py` and `tests/native_fixture_supplier.py` to support the `v0.2.20` built binary path, synthetic multi-provider accounts (`openai`, `anthropic`, `gemini`, `antigravity`) with `email` fields, fingerprint challenge responses, and SIWC `"Reply with OK."` probe responses (`available` and `restricted`).
   - Update `plugins/codex-candy-eval/README.md` and parent `README.md` to document cross-provider evaluation, fingerprint inspection, wildcard filtering, and the `SIWC` tab.
8. **Execute Live Container & Browser Verification (`实测模式` — Owned by `trellis-check`)**:
   - During Phase 2.2 (`trellis-check`), the `trellis-check` agent loads the newly built Linux binary (`dist/build/linux-amd64/sub2api-plugins-v0.2.20-linux-amd64`) into the retained `sub2api-codex-eval-test` container and runs `python3 tests/native_inspection_fixture.py`.
   - `trellis-check` opens `/admin/codex-eval` in a real browser (Playwright CLI / Chrome) and verifies:
     1. Footer `版本 v0.4.6` (`MIT` + `LGPL-3.0`) and 5-tab navigation (`糖果`, `指纹`, `鹈鹕`, `SIWC`, `设置`) with zero console errors;
     2. Cross-provider account selection, `<test>-credential-type` filtering, and live `Candy` / `Fingerprint` / `Pelican` runs against `127.0.0.1:18081`;
     3. `SIWC` live check, `#siwc-detail` modal, and `history.json` v3 (`history.v2.json` backup) persistence across restart;
     4. `设置` tab Row 1 (`模型` | `推理强度` | `检查方式`) and Row 3 (`INCLUDE` | `EXCLUDE`) layout at `1280px` and `430px`, save/reload persistence, and live `立即巡检` execution in both `candy` and `fingerprint` modes with `INCLUDE`/`EXCLUDE` wildcard matching, model/priority updates, and synthetic `ntfy`/`Bark` notifications;
     5. Restores default settings and clean fixture state in `sub2api-codex-eval-test`.

## Validation Commands

1. Run standalone plugin build and test suite:
   ```sh
   UPSTREAM_TAG=v0.2.20 python3 -B scripts/build.py
   ```
   (inside `plugins/codex-candy-eval` and `plugins/sub2api-quota-extension`)
2. Run combined repository build and test suite:
   ```sh
   UPSTREAM_TAG=v0.2.20 python3 -B scripts/build.py
   ```
   (inside `/Users/minami/Code/S/Sub2API-Plugins`)
3. Run live container fixture & browser verification:
   ```sh
   python3 plugins/codex-candy-eval/tests/native_inspection_fixture.py
   ```

## Review Gates

- Gate 1: All 7 `codex-candy-eval` patches and `sub2api-quota-extension/patches/quota-extension.patch` apply cleanly with `git apply --check --binary` against Sub2API `v0.2.20` (both standalone and combined).
- Gate 2: Go tests (`test_codexeval_runtime_test.go`, `test_codexeval_inspection_test.go`, `test_service_account_codex_eval_service_test.go`, `test_service_codex_inspection_settings_test.go`, `test_admin_codex_inspection_handler_test.go`, `test_installer_test.go`), `test_build.py`, and JSDOM UI tests (`test_ui.cjs`) pass 100%, and all 4 aligned build-kit files (`.github/workflows/build.yml`, `tests/test_installer_test.go`) match byte-for-byte across the 4 repositories.
- Gate 3: Live container + real browser verification (`sub2api-codex-eval-test` + `native_fixture_supplier.py` + Playwright on `sub2api-plugins-v0.2.20-linux-amd64`) passes across all 5 tabs, cross-provider evaluations, SIWC, and both inspection check modes (`candy` / `fingerprint`) with wildcard filters and zero console errors.
- Gate 4: `trellis-check` verifies spec compliance, security boundaries, and zero untracked build artifacts.

## Rollback Points

- Each patch file (`0001` through `0007`) in `plugins/codex-candy-eval/patches/` is tracked in Git and can be restored individually with `git checkout -- patches/<file>` if a regression occurs during patch regeneration.
