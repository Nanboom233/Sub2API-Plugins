# Technical Design: Update codex-candy-eval and Sync Upstream v0.4.6

## 1. Architecture and Patch Ownership

All plugin code changes stay within `plugins/codex-candy-eval/`:

| Patch / Path | Responsibility |
| --- | --- |
| `patches/0001-evaluation-core.patch` | Core `backend/internal/codexeval/` package: `siwc.go`, `state.go` (`stateSchemaVersion = 3`, `SIWC` history bucket, `history.v2.json` backup), `runs.go` (`type: "siwc"` dispatch), `history.go` (`siwc` clear/detail), and exported `FingerprintModelID` helper. |
| `patches/0004-admin-channel.patch` | `AccountHandler` and `AccountTestService` in `backend/internal/`: multi-provider support in `CodexEvalModels`, `CodexEvalAccount`, and `SendCodexEvaluation` (`openai`, `anthropic`, `gemini`, `antigravity`), plus non-Responses-Lite OAuth payload normalization and `siwc_access_token` routing for `cpa-siwc-check/` probes. |
| `patches/0005-inspection.patch` | Native `Inspection` coordinator (`inspection.go`, `inspection_store.go`, `codex_inspection_handler.go`): `TestType` (`"candy"` / `"fingerprint"`), `IncludePatterns` and `ExcludePatterns` (`path.Match` on account `Name` and `Email`), single-run fingerprint attribution mismatch degradation verdict without multi-run confirmation loops, and unrestricted Sub2API account platform eligibility. |
| `patches/0006-evaluation-ui.patch` | Embedded UI (`web.go` and `web/*`): `pluginVersion = "0.4.6"`, `web/storage.js`, `web/credentials.js`, `web/siwc.js`, fourth tab (`SIWC`), multi-provider group/account loading and credential-type filtering, and `自动巡检` check-mode + wildcard filter settings UI. |
| `tests/` | Go and JSDOM test files (`test_codexeval_runtime_test.go`, `test_codexeval_inspection_test.go`, `test_service_account_codex_eval_service_test.go`, `test_service_codex_inspection_settings_test.go`, `test_admin_codex_inspection_handler_test.go`, `test_ui.cjs`): cover multi-provider translation, fingerprint inspection, wildcard matching, SIWC execution, history v3 migration, and UI version `0.4.6`. |
| `patches/0007-sub2api-integration.patch` & `sub2api-quota-extension/patches/quota-extension.patch` | Rebase integration and quota-extension hunks against Sub2API `v0.2.20` (`embed_on.go`, `AppSidebar.vue`, `routes/admin.go`, `admin_account.go`, `router/index.ts`, `backend/go.mod`, `account_usage_service.go`, `CreateAccountModal.vue`, `EditAccountModal.vue`), preserving standalone and combined patch compatibility. |
| `.github/workflows/build.yml` & `tests/test_installer_test.go` (4 repos) | Upgrade the default `upstream_tag` (`v0.2.20`) and installer test candidate version (`0.2.20`) across `Sub2API-Plugins`, `codex-candy-eval`, `sub2api-quota-extension`, and `sub2api-plugin-template` while keeping all 4 aligned copies byte-identical. |

## 2. Feature 1: Cross-Provider Evaluation & Unrestricted Group Selection (`跨供应商评估与全分组支持`)

### 2.1 Group Selection, Account Eligibility, and Credential Types
- **Unrestricted Group Selection**:
  - `refreshCatalog()` and `fetchNativeAccounts()` in `web/catalog.js` do **not** filter groups or accounts by `SUPPORTED_PLATFORMS` (`groups = available || [];` and `const items = data.items || [];`). All Sub2API groups (including `composite` multi-platform groups and all provider platforms) are selectable.
  - `PLATFORM_LABELS` in `web/credentials.js` provides labels for all Sub2API platforms (`openai`, `anthropic`, `gemini`, `antigravity`, `grok`, `kimi`, `zhipu`, `deepseek`, `minimax`, `opencode_go`, `typesafe`, `command_code`, `cline`), falling back to `PLATFORM_LABELS[platform] || platform`.
- **Supported Credential Types**: Any non-nil account with `IsOAuth()`, `setup-token`, `apikey`, or `upstream` across any Sub2API platform (`isCodexEvalAccountSupported`, `isInspectionSupportedAccount`, `validInspectionAccountType`).
- **Frontend Filtering (`web/credentials.js` & `web/catalog.js`)**:
  - `loadGroups()` calls `/api/v1/admin/groups/all` and keeps all returned groups without platform filtering.
  - `loadGroupAccounts(groupId)` calls `/api/v1/admin/accounts?group=${groupId}&lite=1` and keeps all returned accounts in the selected group.
  - `credentialType(a)` returns `${a.platform}:${a.type}`.
  - `populateCredentialTypes(test)` populates `<test>-credential-type` with `"all"` (`全部账户`) and platform/type options present in the loaded accounts. For `siwc`, only `openai:oauth` accounts are eligible.

### 2.2 Backend Protocol Translation (`SendCodexEvaluation` & `CodexEvalModels`)
- **`CodexEvalAccount(ctx, id)`**: Allows any account with a supported credential type (`IsOAuth()`, `apikey`, `upstream`) across any Sub2API platform.
- **`CodexEvalModels(ctx, id)`**:
  - For `openai`: uses `s.openaiGatewayService.FetchOpenAIModelsList(ctx, account)`.
  - For other OpenAI-compatible platforms (`deepseek`, `kimi`, `zhipu`, `minimax`, `grok`, `opencode_go`, `command_code`, `cline`), queries upstream `/v1/models` when a custom `base_url` is configured and falls back cleanly to `fallbackCodexEvalModels(account)`.
  - For `anthropic`, `gemini`, and `antigravity`: returns the platform's configured/known model catalog or queries the upstream `/v1/models` endpoint when available, falling back cleanly so custom models and preset models work across all providers.
- **`SendCodexEvaluation(ctx, id, body, headers)`**:
  - Accepts the incoming OpenAI Responses request (`model`, `stream: true`, `input`, `instructions`, `reasoning`, `max_output_tokens`).
  - Dispatches by `credentialAccount.Platform` and protocol:
    1. **`anthropic` (Claude) or `RoutesProtocolByInbound() && GetAPIProtocol() == APIProtocolAnthropic`**: Converts `apicompat.ResponsesRequest` into an Anthropic Messages streaming request (`/v1/messages` with `stream: true`), sends using the account's credentials and proxy, and adapts the SSE stream to OpenAI Responses SSE events.
    2. **`gemini` / `antigravity`**: Converts `apicompat.ResponsesRequest` into a Gemini `streamGenerateContent?alt=sse` request using `convertClaudeMessagesToGeminiGenerateContent(claudeBody, model)` and `geminiTextDelta.next(text)`, and adapts the SSE stream to OpenAI Responses SSE events.
    3. **`openai` and all OpenAI-compatible platforms**: Uses OAuth (`chatgptCodexAPIURL` Responses SSE) or API Key (`/v1/responses` or `/v1/chat/completions` converted via `apicompat.ResponsesToChatCompletionsRequest` + `codexChatStream`).

## 3. Feature 2 & 3: Fingerprint Single-Run Inspection, Mode-Aware `下次巡检` Display & Wildcard Matching

### 3.1 Settings & Data Contracts (`0005-inspection.patch`)
- Extend `InspectionSettings` (`inspection_settings.go`):
  - `TestType string` (`json:"test_type"`): `"candy"` (default when empty) or `"fingerprint"`.
  - `IncludePatterns []string` (`json:"include_patterns"`): normalized, trimmed wildcard patterns; validated with `path.Match(pattern, "")`.
  - `ExcludePatterns []string` (`json:"exclude_patterns"`): normalized, trimmed wildcard patterns; validated with `path.Match(pattern, "")`.
- Extend `InspectionAccount` (`inspection.go` and `codex_inspection_handler.go`):
  - Add `Email string` (`json:"email,omitempty"`), extracted from `account.Extra["email"]` or `account.Credentials["email"]`.
  - Support all eligible Sub2API accounts in the selected group and apply `matchesInspectionPatterns(account, settings.IncludePatterns, settings.ExcludePatterns)` using `path.Match` on `account.Name` and `account.Email`.

### 3.2 Single-Run Fingerprint Inspection Execution (No `RoundSummary` Addition)
- **Single-Run Fingerprint Verdict (Option A — No 9-Round Multiplication)**:
  - In `candy` mode (`testType == "candy"`), 1 Candy test sends 1 prompt; state transitions between normal and degraded run `MaxTestsPerAccount - 1` confirmation runs (with `240s` `recovery_wait` before normal recovery confirmation).
  - In `fingerprint` mode (`testType == "fingerprint"`), 1 Fingerprint evaluation already sends `fingerprintTarget = 3` distinct challenges and computes a 3-challenge statistical attribution (`r.Attribution.Prediction`). Therefore, in `run()` (`inspection.go`), when `testType == "fingerprint"` and a concluded first run (`Status == "completed" || Status == "partial"` with `Attribution != nil`) transitions state (`(current.Verdict == InspectionVerdictDegraded) != !answers[0]`), immediately set `r.TargetPriority = &target; r.Outcome = "recommended"` and call `apply(a, target)` without queueing into `groups[target]` (no `recovery_wait` and no `MaxTestsPerAccount - 1` confirmation loop; `batches := 1` in `testPhase`).
- **Remove Unsolicited `RoundSummary` (`本轮...巡检`)**:
  - Remove `InspectionRoundSummary`, `RoundSummary`, `round_summary`, `#inspection-round-summary`, and `formatInspectionRoundSummary` completely from `0005-inspection.patch` and `0006-evaluation-ui.patch`. Preserve the original rule: do not show a completed-phase caption or stale completed summary in `#inspection-status`.

### 3.3 Mode-Aware `下次巡检` Placement & Inspection UI Controls (`0006-evaluation-ui.patch`)
- In `web/ui.html` and `web/inspection.js`:
  - In `#inspection-auto-fields` (`自动巡检`), place the first three controls (`模型`, `推理强度`, `检查方式`) on the first row by nesting `推理强度` (`name="effort"`) and `检查方式` (`name="test_type"`, options `糖果` / `指纹`) inside a `<div class="settings-grid">` next to `模型`.
  - Place **包含账户通配符（INCLUDE）** (`name="include_patterns"`) and **排除账户通配符（EXCLUDE）** (`name="exclude_patterns"`) on the third row of `#inspection-auto-fields`.
  - **Mode-Aware `下次巡检` (`#inspection-status`) Placement**:
    - Restore the original 3-span `#inspection-status` (`#inspection-phase`, `#inspection-next`, `#inspection-progress`).
    - Add `syncInspectionStatusPlacement()` in `web/inspection.js` (called from `updateInspectionVisibility()` and `renderInspectionState(state)`) to move `#inspection-status` into `#fp-credentials .credential-head` (before `.credential-filters`) when the selected `test_type` is `"fingerprint"`, and into `#candy-credentials .credential-head` when `"candy"`.
    - Update `.candy-head .inspection-status` in `web/style.css` to `.credential-head .inspection-status`.

## 4. Upstream `v0.4.6` Sync (`SIWC`, History v3, `storage.js`, `credentials.js`, Version `0.4.6`)

### 4.1 SIWC (`Sign In With ChatGPT`)
- **Backend (`backend/internal/codexeval/siwc.go` + `account_codex_eval_service.go`)**:
  - Match upstream `v0.4.6` `evaluateSIWC`: send a 1-shot minimal Responses streaming probe (`{"model": model, "store": false, "stream": true, "input": [{"role": "user", "content": "Reply with OK."}]}`) with `User-Agent: cpa-siwc-check/0.4.6` and `siwcTimeout = time.Minute` via `executeResponse` (`SendCodexEvaluation`).
  - Classify outcome into `available` (`SIWC 可用`), `restricted` (`订阅共享受限`, error code `subscription_sharing_user_not_eligible`), `limited` (`额度或频率受限`, error code `subscription_sharing_usage_limit_exceeded` or HTTP 429), `auth_error` (`认证异常`, error code `subscription_sharing_invalid_user` or HTTP 401), `cancelled`, or `failed`, and record a `siwcResult` in the `siwc` history bucket.
  - In `AccountTestService.SendCodexEvaluation`, retain native model normalization for non-Responses-Lite OAuth requests through `normalizeOpenAIModelForUpstream`.
  - Normalize their payloads through `normalizeCodexOAuthNonLitePayload` for `chatgpt.com/backend-api/codex/responses`.
  - Retain Responses-Lite model behavior and bound `siwc_access_token` routing. Keep account-configured model mappings separate from native normalization.
- **History Schema v3 (`state.go` & `history.go`)**:
  - Bump `stateSchemaVersion` from `2` to `3`.
  - When migrating a v2 `history.json` to v3, write a backup copy to `history.v2.json` before saving v3.
  - Support `scope: "siwc"` in `Clear` and `type: "siwc"` in `Record` detail lookup.
- **Frontend (`web/siwc.js`, `web/storage.js`, `web/credentials.js`, `web/ui.html`, `web.go`)**:
  - Embed `web/storage.js`, `web/credentials.js`, and `web/siwc.js` in `web.go`.
  - Set `const pluginVersion = "0.4.6"` in `web.go`.
  - Add the 4th tab `SIWC` (`#tab-siwc`, label `SIWC` without `· 授权状态`, matching the concise style of `糖果`, `指纹`, `鹈鹕`, `设置`) in `web/ui.html` and wire it in `web/app.js`.

## 5. Feature 5: Sub2API `v0.2.20` Baseline Upgrade

Per `.trellis/tasks/11-07-eval-upstream-feature-sync/research/sub2api-v0220-upgrade.md`:

### 5.1 Patch Adaptations for Sub2API `v0.2.20`
1. **`plugins/codex-candy-eval/patches/0004-admin-channel.patch`**:
   - Rebase Hunk #1 in `backend/internal/repository/http_upstream.go` (`+12` lines offset after upstream `upstreamDrainTimeout` and `pkghttputil.NewUpstreamAttemptContext`).
   - Fix two upstream signature changes in `backend/internal/service/account_codex_eval_service.go` (`gemini_messages_compat_service.go` in `v0.2.20`):
     - Change `convertClaudeMessagesToGeminiGenerateContent(claudeBody)` to `convertClaudeMessagesToGeminiGenerateContent(claudeBody, model)`.
     - Replace `seenText string` / `seenThought string` and `computeGeminiTextDelta(...)` in `codexGeminiStream` with `seenText geminiTextDelta` / `seenThought geminiTextDelta` and `s.seenThought.next(text)` / `s.seenText.next(text)`.
2. **`plugins/codex-candy-eval/patches/0007-sub2api-integration.patch`**:
   - Rebase `backend/internal/web/embed_on.go` after the new `.well-known/oauth-*` MCP bypass lines in `shouldBypassEmbeddedFrontend`.
   - Rebase `frontend/src/components/layout/AppSidebar.vue` after the new `MCPIcon` definition (line 481) and shifted nav items (`+8` lines).
   - Rebase shifted hunks in `backend/internal/server/routes/admin.go`, `backend/internal/service/admin_account.go`, and `frontend/src/router/index.ts`.
3. **`plugins/sub2api-quota-extension/patches/quota-extension.patch`**:
   - Rebase `backend/go.mod` after `github.com/google/jsonschema-go v0.4.2 // indirect` (and `backend/go.sum`).
   - Rebase `backend/internal/service/account_usage_service.go`: preserve the new `adminaccess` import at line 16 and keep `if err := scopedAccountAccess(ctx, s.accountRepo, account, "accounts.usage.read", true); err != nil { return nil, err }` at the entry of `getUsageForAccount` before custom script or native usage probing.
   - Rebase `frontend/src/components/account/CreateAccountModal.vue` and `EditAccountModal.vue` around the new `OpenAIImageSizeTiersField` imports, plus shifted hunks in `wire_gen.go`, `routes/admin.go`, `admin_account.go`, `wire.go`, `api/admin/accounts.ts`, `AccountUsageCell.vue`, `en/admin/accounts.ts`, and `types/index.ts`.
   - Verify `quota-extension.patch` applies cleanly both standalone on `v0.2.20` and combined after `codex-candy-eval` `0001`–`0007`.

### 5.2 Aligned Workflows, Tests, Docs & Specs (`v0.2.19` -> `v0.2.20`)
- Update `.github/workflows/build.yml` (`default: v0.2.20` at line 11) and `tests/test_installer_test.go` (`Candidate: "0.2.20"` at line 661) identically across all 4 repositories (`Sub2API-Plugins`, `codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`).
- Update `plugins/codex-candy-eval/tests/native_inspection_fixture.py` to resolve `sub2api-plugins-v0.2.20-linux-{arch}`.
- Update `README.md` (root) and `plugins/sub2api-plugin-template/README.md` example tags/filenames from `v0.2.19` to `v0.2.20` (leaving `plugins/codex-candy-eval/README.md` untouched as it has no `0.2.19` references).
- Update `.trellis/spec/backend/{index.md,minimal-linux-delivery.md,quality-guidelines.md,runtime-installation.md,api-key-quota.md}` to record `v0.2.20` (noting that `v0.2.20` retains `0.2.19` in `backend/cmd/server/VERSION`).

## 6. Test Plan (`plugins/codex-candy-eval/tests/`)

### 6.1 Automated Unit & JSDOM Test Suite

| Test File | Package / Runner | Planned Test Cases & Assertions |
| --- | --- | --- |
| `tests/test_codexeval_runtime_test.go` | `backend/internal/codexeval` (`go test`) | 1. **SIWC Run & Cancellation (`TestCodexEvalSIWCRunAndCancel`)**: Verify `StartRequest{Type: "siwc"}` admission, 1-shot Responses probe (`User-Agent: cpa-siwc-check/0.4.6`) classification (`status: "available" \| "restricted" \| "limited" \| "auth_error" \| "failed"`), `Record("siwc", id, recordID)` detail retrieval, `Clear("siwc")` history clearing, and active run cancellation.<br>2. **Schema v2 -> v3 Migration (`TestCodexEvalRuntime`)**: Verify migrating a v2 `history.json` writes an exact `history.v2.json` backup with `0600` permissions, upgrades `schema_version` to `3` with the `siwc` bucket, and blocks writes when `schema_version > 3`.<br>3. **Page Version (`TestCodexEvalPageVersion`)**: Assert `codexeval.Page()` renders `版本 v0.4.6` and embeds `siwc.js`, `storage.js`, and `credentials.js`. |
| `tests/test_codexeval_inspection_test.go` | `backend/internal/codexeval` (`go test`) | 1. **Fingerprint Inspection Mode (`TestCodexInspectionFingerprintModeAndWildcards`)**: Verify `TestType: "fingerprint"` runs 1 three-challenge fingerprint evaluation per account without confirmation loops or `recovery_wait`, marks accounts degraded when `FingerprintModelID(Model) != FingerprintModelID(Attribution.Prediction)` on `completed`/`partial` runs, and marks matching predictions normal.<br>2. **Wildcard Account Filtering (`TestCodexInspectionCandySelection`)**: Verify `IncludePatterns` and `ExcludePatterns` match against both `InspectionAccount.Name` and `InspectionAccount.Email` via `path.Match`, and reject invalid wildcard syntax in `InspectionSettings.Validate()`. |
| `tests/test_service_account_codex_eval_service_test.go` | `backend/internal/service` (`go test -tags=unit`) | 1. **Multi-Provider Evaluation (`TestCodexEvalCrossProviderSender`)**: Verify `SendCodexEvaluation`, `CodexEvalAccount`, and `CodexEvalModels` for `anthropic` (Claude Messages SSE -> Responses SSE), `gemini` / `antigravity` (Gemini stream -> Responses SSE), and `openai` accounts.<br>2. **SIWC Probe Routing (`TestCodexEvalSendSIWC`)**: Verify `SendCodexEvaluation` handles `User-Agent: cpa-siwc-check/0.4.6` probes via OAuth non-Lite payload normalization and bound `siwc_access_token` routing. |
| `tests/test_service_codex_inspection_settings_test.go` | `backend/internal/service` (`go test -tags=unit`) | **Settings Persistence (`TestCodexInspectionSettingsPersistence`)**: Verify `test_type` (default `"candy"`, `"fingerprint"`), `include_patterns`, and `exclude_patterns` round-trip through `GetCodexInspectionSettings` and `UpdateCodexInspectionSettings`, normalize pattern slices, and reject malformed glob patterns (`[`). |
| `tests/test_admin_codex_inspection_handler_test.go` | `backend/internal/handler/admin` (`go test`) | **Account Email Extraction & Multi-Provider Inspection (`TestCodexInspectionAccountEmailAndPlatforms`)**: Verify `inspectionAccount` extracts `Email` from `account.Extra["email"]` and `account.Credentials["email"]` and preserves multi-platform account metadata. |
| `tests/test_ui.cjs` | `node` + `jsdom` | 1. **Settings Tab Controls**: Verify `#inspection-auto-fields` places `模型`, `推理强度`, and `检查方式` (`name="test_type"`) on the first row and `include_patterns` / `exclude_patterns` on the third row, auto-saves dirty edits, and restores saved values on reload.<br>2. **Multi-Provider Catalog & Credential Filter**: Verify `loadGroups` and `loadGroupAccounts` load non-OpenAI platforms and `<test>-credential-type` filters by `${platform}:${type}` (`siwc` restricted to `openai:oauth`).<br>3. **SIWC Tab**: Verify switching to `tab-siwc`, running batch/single SIWC checks, rendering authorization summaries, and opening `#siwc-detail`. |

### 6.2 Live Container Runtime & Browser Verification (`实测规划`)

Follow the established live verification pattern from earlier tasks (`tests/native_inspection_fixture.py`, `tests/native_fixture_supplier.py`, `tests/native_fixture_start.sh`):

1. **Retained Container & Synthetic Supplier (`sub2api-codex-eval-test`)**:
   - Reuse the single existing `sub2api-codex-eval-test` Docker container (PostgreSQL 18 + Redis + `native_fixture_supplier.py` on `127.0.0.1:18081` + built Linux binary `/app/sub2api` loaded from `dist/build/linux-amd64/sub2api-plugins-v0.2.20-linux-amd64`). Never create extra containers or send requests to paid external providers.
   - Extend `tests/native_inspection_fixture.py` and `tests/native_fixture_supplier.py` to seed synthetic accounts across `openai` (`oauth` with `id_token` + `apikey`), `anthropic` (`apikey` / `setup-token`), `gemini` (`apikey` / `oauth`), and `antigravity` (`apikey`) with `name` and `email` metadata, and serve synthetic responses for:
     - OpenAI `/v1/responses` and `/v1/chat/completions` (Candy `21`/`22`, Fingerprint numeric sequences, Pelican HTML, and SIWC `"Reply with OK."` probes);
     - Anthropic `/v1/messages` SSE stream;
     - Gemini `streamGenerateContent?alt=sse` stream;
     - Local notification sinks (`/ntfy/*` and `/bark/*`).
2. **Real Browser / Playwright End-to-End Verification**:
   - **L1 (Page Shell, Footer & 5 Tabs)**: Open `/admin/codex-eval` inside the native Sub2API admin shell; verify `版本 v0.4.6`, `MIT` and `LGPL-3.0` footer links, and switching across `糖果`, `指纹`, `鹈鹕`, `SIWC`, and `设置` with zero console/page errors.
   - **L2 (Cross-Provider Evaluation Live Run)**: Select multi-provider groups, verify `<test>-credential-type` filtering (`全部凭证`, `openai:oauth`, `anthropic:apikey`, `gemini:apikey`, `antigravity:apikey`), and execute live `Candy`, `Fingerprint`, and `Pelican` runs against `127.0.0.1:18081`.
   - **L3 (SIWC Tab Live Run & History v3 Persistence)**: Switch to `SIWC` tab, verify `#siwc-model-select` and `openai:oauth` filtering, run live SIWC checks (`available` / `SIWC 可用` and `restricted` / `订阅共享受限`), inspect `#siwc-detail`, and verify `history.json` (`schema_version: 3` + `history.v2.json` backup) survives container restart.
   - **L4 (Settings Layout & Live Inspection Rounds)**:
     - Verify `#inspection-auto-fields` Row 1 (`模型` 50% | `推理强度` 25% | `检查方式` 25%) and Row 3 (`包含账户通配符（INCLUDE）` 50% | `排除账户通配符（EXCLUDE）` 50%) at desktop (`1280px`) and mobile (`430px`) viewports without horizontal overflow.
     - Verify auto-save, same-page password retention, and fresh-reload persistence for `test_type`, `include_patterns`, and `exclude_patterns`.
     - Trigger live `立即巡检` (`run-now`) in **糖果 (`candy`)** mode and **指纹 (`fingerprint`)** mode with `INCLUDE` / `EXCLUDE` name and email wildcards, verifying single-run fingerprint degradation/recovery verdicts without `recovery_wait`, mode-aware `#inspection-status` placement, model mapping / priority updates, and local `/ntfy` + `/bark` notifications, then restore clean default settings.

