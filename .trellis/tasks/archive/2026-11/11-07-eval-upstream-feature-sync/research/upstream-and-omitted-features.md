# Upstream Feature Sync and Omitted Features Audit

## Query, Scope, and Date

- **Query**: Audit upstream `haowang02/cpa-plugin-codex-candy-eval` commits since `v0.4.4` and compare cross-provider evaluation, fingerprint inspection, wildcard matching, version numbers, and new features.
- **Scope**: Read-only audit of upstream `haowang02/cpa-plugin-codex-candy-eval` (`v0.4.6`), archived Trellis research tasks, and `plugins/codex-candy-eval/patches/0001` through `0007`.
- **Date**: 2026-11-07

## Files Found

### Upstream Repository (`haowang02/cpa-plugin-codex-candy-eval` at `0ae33b626aa27a191fd91731230521e90656c8b4`, `v0.4.6`)

- `README.md`: Documents evaluation types (`Candy`, `Fingerprint`, `Code`, `SIWC`), cross-provider support, and scheduled inspection workflows.
- `docs/inspection.md`: Specifies the management inspection HTTP endpoints, wildcard filter parameters, and response schemas.
- `examples/inspection.py`: Provides the reference scheduled inspection script with `INCLUDE` and `EXCLUDE` wildcard matching for `candy` and `fingerprint`.
- `internal/plugin/plugin.go`: Defines `pluginVersion = "0.4.6"` and registers management endpoints for credentials, runs, history, and inspection.
- `internal/plugin/ui.go`: Builds the self-contained HTML page, injects `<!--PLUGIN_VERSION-->`, and embeds `storage.js`, `host.js`, and `siwc.js`.
- `internal/plugin/credentials.go`: Manages credential discovery from CPA auth files (`auth_files`) and synced AI provider keys (`ai_providers`).
- `internal/plugin/responses.go`: Executes upstream model requests through `host.model.execute_stream` with `forced_provider` and `openai-response` protocol translation.
- `internal/plugin/inspection.go`: Implements `POST /inspection` wildcard filtering and `GET /inspection` current-round degradation summaries for `candy` and `fingerprint`.
- `internal/plugin/inspection_test.go`: Tests `matchesAny` wildcard matching and `inspectionResponse` verdict aggregation across `candy` and `fingerprint` runs.
- `internal/plugin/siwc.go`: Implements `POST /siwc/run` to verify Sign In With ChatGPT (`SIWC`) authorization using OAuth `id_token` credentials.
- `internal/plugin/migration.go`: Defines `stateSchemaVersion = 3` and migrates persisted history state to include the `siwc` bucket.
- `internal/plugin/state.go`: Defines the `historyState` struct with `Candy`, `Fingerprint`, `Code`, and `SIWC` record slices.
- `internal/plugin/runs.go`: Implements history listing, deletion, import, and export across `candy`, `fingerprint`, `code`, and `siwc` buckets.
- `internal/plugin/web/providers.js`: Fetches CPA `/v0/management/config` and `/v8/management/config/api-keys` and normalizes provider credentials for `/credentials/sync`.
- `internal/plugin/web/credentials.js`: Implements the shared `<test>-credential-type` filter (`all` or `<source>:<provider>`) and credential table selection controls.
- `internal/plugin/web/siwc.js`: Implements the frontend controller and detail dialog for the `SIWC` tab.
- `internal/plugin/web/storage.js`: Centralizes browser `localStorage` persistence and decodes `CPAMC` and `CPAMP` saved login payloads.
- `internal/plugin/web/host.js`: Bridges `Oh My CPA` parent-frame `postMessage` authentication when the UI runs inside an embedded host.
- `internal/plugin/web/ui.html`: Declares the four-tab evaluation layout (`Candy`, `Fingerprint`, `Code`, `SIWC`) and renders `版本 v<!--PLUGIN_VERSION-->`.

### Current Repository (`plugins/codex-candy-eval`)

- `plugins/codex-candy-eval/README.md`: Documents the Sub2API patch stack (`0001` to `0007`), admin endpoints, and patch application workflow.
- `plugins/codex-candy-eval/patches/0001-evaluation-core.patch`: Adds `backend/internal/codexeval/` evaluation logic (`candy.go`, `fingerprint.go`, `code.go`, `history.go`, `runs.go`, `state.go`).
- `plugins/codex-candy-eval/patches/0004-admin-channel.patch`: Adds `codex_eval_handler.go` and `codex_eval_service.go` with OpenAI-only account filtering and upstream execution.
- `plugins/codex-candy-eval/patches/0005-inspection.patch`: Adds the native background `Inspection` coordinator (`inspection.go`, `inspection_store.go`, `codex_inspection_handler.go`).
- `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch`: Adds `web.go` (`pluginVersion = "0.3.14"`) and frontend assets (`app.js`, `catalog.js`, `inspection.js`, `ui.html`).
- `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch`: Registers `/api/v1/admin/codex-eval/*` routes and wires the `Inspection` coordinator into `admin_service.go`.

### Archived Trellis Research Files

- `.trellis/tasks/archive/2026-10/10-19-upstream-compare-adaptation/research/upstream-comparison.md`: Documents the earlier comparison against upstream `v0.4.2` (`672e0604c806941f925c5d87e22fd4fd642a596e`).
- `.trellis/tasks/archive/2026-10/10-19-upstream-evaluation-sync/research/upstream-evaluations.md`: Documents the sync of evaluation core logic (`candy`, `fingerprint`, `code`) from upstream `v0.4.2`.
- `.trellis/tasks/archive/2026-10/10-19-upstream-evaluation-sync/research/upstream-ui-history.md`: Documents the sync of history schema v2 and multi-run batch execution while retaining Sub2API account selectors.
- `.trellis/tasks/archive/2026-10/10-19-upstream-evaluation-sync/research/code-retry-inspection.md`: Documents why upstream's CPA `/inspection` endpoint was skipped in favor of the native Sub2API inspection coordinator.
- `.trellis/tasks/archive/2026-11/10-30-inspection-settings-attribution/research/upstream-sync.md`: Documents the sync of upstream `v0.4.3` and `v0.4.4` (`179d6dae48a0f0a735637ea2f373345b91caaca8`).
- `.trellis/tasks/archive/2026-10/10-11-sub2api-runtime-patch/research/native-inspection-implementation.md`: Documents the initial Sub2API native inspection design that originally included `include_patterns` and `exclude_patterns`.
- `.trellis/tasks/archive/2026-10/10-11-sub2api-runtime-patch/research/U11-settings-implementation.md`: Documents Task U11, which removed `IncludePatterns` and `ExcludePatterns` from native inspection settings and UI.

## Code Patterns

### 1. Upstream Commits Since `v0.4.4` (`179d6dae48a0f0a735637ea2f373345b91caaca8`)

Upstream `main` is at commit `0ae33b626aa27a191fd91731230521e90656c8b4` (tag `v0.4.6`, dated 2026-11-06). Four commits landed after `179d6dae48a0f0a735637ea2f373345b91caaca8` (`v0.4.4`):

1. `3bbef5850216fe0e0fe6ed71cbc64efb21f05d73` (merged via `504a10f2e27ea8ec40013260fcaf37939a263b63`): Fixes `CPAMC` v2 saved login decoding in `internal/plugin/web/app.js`.
2. `1dc8d2529388cb7eb722613de8fdbf7262deffea` (tag `v0.4.5`): Extracts browser storage helpers into `internal/plugin/web/storage.js` and bumps `pluginVersion` to `"0.4.5"`.
3. `56f22d7f60a2b3c029714d008b8d1e2052605783`: Moves HTML assembly to `internal/plugin/ui.go` and adds `internal/plugin/web/host.js` for `Oh My CPA` iframe hosting.
4. `0ae33b626aa27a191fd91731230521e90656c8b4` (tag `v0.4.6`): Adds `SIWC` checks (`internal/plugin/siwc.go`, `internal/plugin/web/siwc.js`), extracts `internal/plugin/web/credentials.js`, and bumps `pluginVersion` to `"0.4.6"`.

### 2. Cross-Provider Evaluation (`跨供应商评估`)

#### Upstream Implementation

- **Credential Model (`internal/plugin/credentials.go:14-43`)**: Upstream normalizes every credential into a `credential` struct with `ID`, `Name`, `Provider`, `Source` (`auth_files` or `ai_providers`), `Label`, `Status`, `Email`, `PlanType`, and `Attributes`.
- **Two Credential Sources (`internal/plugin/credentials.go:53-161`)**:
  - `loadCredentials` (`internal/plugin/credentials.go:88-107`) calls CPA `host.auth.list` to load auth files (`source = "auth_files"`) and merges cached provider records (`source = "ai_providers"`).
  - `credentialsSyncResponse` (`internal/plugin/credentials.go:53-68`) handles `POST /v0/management/plugins/cpa-codex-candy-eval/credentials/sync` and stores normalized provider credentials in `p.providerCredentials`.
- **Frontend Provider Extraction (`internal/plugin/web/providers.js:67-137`)**:
  - `fetchProviderCredentials` (`internal/plugin/web/providers.js:67-79`) fetches `/v0/management/config` and `/v8/management/config/api-keys` from the CPA host.
  - `extractProviderCredentials` (`internal/plugin/web/providers.js:113-135`) extracts credentials from `gemini-api-key` (`provider: "gemini"`), `interactions-api-key` (`provider: "gemini-interactions"`), `claude-api-key` (`provider: "claude"`), `codex-api-key` (`provider: "codex"`), `xai-api-key` (`provider: "xai"`), `meta-api-key` (`provider: "meta"`), `openai-compatibility` (`provider: "openai-compatible-<name>"`), and `vertex-api-key` (`provider: "vertex"`).
- **Execution Protocol Translation (`internal/plugin/responses.go:25-39`)**:
  - `queryResponses` (`internal/plugin/responses.go:25-39`) builds an OpenAI Responses payload and invokes CPA `host.model.execute_stream`.
  - It passes `"entry_protocol": "openai-response"`, `"exit_protocol": "openai-response"`, `"forced_provider": auth.Provider`, and `"auth_id": auth.ID` (`internal/plugin/responses.go:31-35`).
  - CPA translates the `openai-response` request into the target provider's native protocol (Claude Messages, Gemini GenerateContent, OpenAI Chat/Responses, or Vertex) and converts the stream back into `openai-response` SSE events.
- **Shared Credential Filter UI (`internal/plugin/web/credentials.js:4-9,86-129`)**:
  - `credentialType(c)` (`internal/plugin/web/credentials.js:4-9`) returns `"${c.source}:${c.provider.toLowerCase()}"`.
  - `populateCredentialTypes` (`internal/plugin/web/credentials.js:86-129`) populates `<test>-credential-type` with `"all"` (`全部凭证`) and `<source>:<provider>` options (such as `认证文件 · codex`, `AI 提供商 · claude`, `AI 提供商 · gemini`), defaulting to `"auth_files:codex"`.

#### Current Sub2API Implementation and Gaps

- **OpenAI-Only Backend Guard (`plugins/codex-candy-eval/patches/0004-admin-channel.patch:191-235`)**:
  - `CodexEvalModels` (`0004-admin-channel.patch:191-213`), `CodexEvalAccount` (`0004-admin-channel.patch:215-224`), and `SendCodexEvaluation` (`0004-admin-channel.patch:228-235`) reject any account where `account.Platform != PlatformOpenAI` or `!account.IsOAuth() && account.Type != AccountTypeAPIKey`.
  - `SendCodexEvaluation` (`0004-admin-channel.patch:268-398`) only implements two upstream transport paths: ChatGPT Codex OAuth (`chatgptCodexAPIURL`) and OpenAI API Key (`/v1/responses` or `/v1/chat/completions` via `apicompat.ResponsesToChatCompletionsRequest`).
- **OpenAI-Only Frontend Catalog (`plugins/codex-candy-eval/patches/0006-evaluation-ui.patch:544-573,868,912`)**:
  - `loadGroups` (`0006-evaluation-ui.patch:868`) requests `/api/v1/admin/groups/all?platform=openai`.
  - `loadGroupAccounts` (`0006-evaluation-ui.patch:912`) requests `/api/v1/admin/accounts?platform=openai&group=${encodeURIComponent(group)}&lite=1`.
  - `credentialType(a)` (`0006-evaluation-ui.patch:544-547`) only inspects `a.type` (`oauth` or `apikey`) instead of `a.platform` (`openai`, `anthropic`, `gemini`, `antigravity`).
- **Mapping to Sub2API's Account Model**:
  - Sub2API natively stores multi-provider accounts in its database with `Platform` (`openai`, `anthropic`, `gemini`, `antigravity`), `Type` (`oauth`, `setup-token`, `apikey`, `upstream`), and `Credentials` (`api_key`, `base_url`, `access_token`, `refresh_token`, `id_token`).
  - Supporting cross-provider evaluation in Sub2API requires either removing the `platform=openai` filter and adding protocol adapters in `SendCodexEvaluation` (using Sub2API's `apicompat` conversion helpers for Anthropic Claude and Gemini) or accepting ad-hoc provider credentials/auth files.

### 3. Fingerprint Inspection API (`指纹巡检接口`)

#### Upstream Implementation

- **Routes (`internal/plugin/plugin.go:145-146`)**:
  - Registers `POST /v0/management/plugins/cpa-codex-candy-eval/inspection` (`inspectionRunResponse`) and `GET /v0/management/plugins/cpa-codex-candy-eval/inspection` (`inspectionResponse`).
- **Trigger Endpoint (`internal/plugin/inspection.go:33-69`)**:
  - `inspectionRunResponse` parses `{"test": "candy" | "fingerprint", "include": [...], "exclude": [...]}` alongside the run parameters (`model`, `variant`, `runs`, `concurrency`, `fast`, `thinking`, `max_tokens`).
  - It filters `loadCredentials(ctx)` for enabled, non-unavailable credentials matching `include` and `exclude` (`internal/plugin/inspection.go:47-56`).
  - It injects the matched `credential_ids` into the request body, dispatches to `candyRunResponse` or `fingerprintRunResponse` (`internal/plugin/inspection.go:57-61`), and stores `p.inspections[req.Test] = inspection{started: started, credentialIDs: ids}` (`internal/plugin/inspection.go:64-66`).
- **Status and Verdict Endpoint (`internal/plugin/inspection.go:82-120`)**:
  - `inspectionResponse` reads `test := r.URL.Query().Get("test")` (`"candy"` or `"fingerprint"`).
  - For each credential in `latest.credentialIDs`, it collects records with `created >= latest.started` and computes `degraded` (`*bool`, `nil` when no record has concluded):
    - **`candy` verdict (`internal/plugin/inspection.go:104-107`)**: A record is concluded when `r.Status == "correct" || r.Status == "wrong"`. It sets `degraded = true` when `r.Status == "wrong"`.
    - **`fingerprint` verdict (`internal/plugin/inspection.go:108-116`)**: A record is concluded when `r.Attribution != nil && (r.Status == "completed" || r.Status == "partial")`. It sets `degraded = true` when `fingerprintModelID(r.Model) != fingerprintModelID(r.Attribution.Prediction)`. It serializes `records` via `summaries(found)`.

#### Current Sub2API Implementation and Gaps

- **Candy-Only Scheduled Coordinator (`plugins/codex-candy-eval/patches/0005-inspection.patch:1-689`)**:
  - Instead of upstream's stateless `/inspection` trigger/poll API, `0005-inspection.patch` implements a stateful background scheduler (`Inspection` in `backend/internal/codexeval/inspection.go`) exposed at `/api/v1/admin/codex-eval/inspection/{state,start,stop}` (`0007-sub2api-integration.patch:50-52`).
  - `testPhase` (`0005-inspection.patch:592-644`) hardcodes `Type: "candy"` at line `597` (`RunRequest{Type: "candy", ...}`) and evaluates outcomes strictly via `evalResult.Status == "wrong"` (`0005-inspection.patch:632-637`).
  - Neither `0005-inspection.patch` nor `0006-evaluation-ui.patch` exposes a `test: "fingerprint"` inspection mode or upstream's `GET/POST /inspection` contract with fingerprint attribution mismatch (`fingerprintModelID(r.Model) != fingerprintModelID(r.Attribution.Prediction)`) degradation verdicts.

### 4. Name / Email Wildcard Matching (`名称／邮箱匹配巡检`)

#### Upstream Implementation

- **Backend Wildcard Matcher (`internal/plugin/inspection.go:34-38,50-55,71-80`)**:
  - `inspectionRunResponse` accepts `Include []string` (`json:"include"`) and `Exclude []string` (`json:"exclude"`).
  - `matchesAny(auth credential, patterns []string) bool` (`internal/plugin/inspection.go:71-80`) tests each pattern against `auth.Email` and `auth.Name` using Go's `path.Match(pattern, value)`.
  - A credential is selected when `(len(req.Include) == 0 || matchesAny(auth, req.Include)) && !matchesAny(auth, req.Exclude)` (`internal/plugin/inspection.go:50-53`).
- **Reference Script Wildcard Matcher (`examples/inspection.py:15-16,75-77,157-158`)**:
  - Defines `INCLUDE = ["codex-*"]` and `EXCLUDE = []` (`examples/inspection.py:15-16`) and passes `"include": INCLUDE, "exclude": EXCLUDE` in `POST /inspection` (`examples/inspection.py:157-158`).
  - Client-side fallback helper `matches(c, patterns)` (`examples/inspection.py:75-77`) checks `fnmatch.fnmatchcase(c.get(key, ""), pattern)` for `key in ("name", "email")`.

#### Current Sub2API Implementation and Gaps

- **Removed in Task U11 (`plugins/codex-candy-eval/patches/0005-inspection.patch` & `0006-evaluation-ui.patch`)**:
  - As documented in `.trellis/tasks/archive/2026-10/10-11-sub2api-runtime-patch/research/native-inspection-implementation.md:27-29` and `U11-settings-implementation.md:10-20`, the initial Sub2API native inspection design included `IncludePatterns []string` (`include_patterns`) and `ExcludePatterns []string` (`exclude_patterns`) in `InspectionSettings`, wildcard validation via `filepath.Match`, name/email matching on `InspectionAccount`, and an `包含 / 排除账号` UI card.
  - Task U11 removed those fields and controls. Today:
    - `InspectionAccount` (`0005-inspection.patch:25-36`) only has `ID`, `Name`, `Platform`, `Type`, `Status`, `Schedulable`, `RateMultiplier`, `GroupIDs`, and `LastUsedAt` (no `Email` field).
    - `inspectionEligible` (`0005-inspection.patch:285-304`) only checks `Platform == "openai"`, `Type == "oauth" || Type == "apikey"`, `Status != "error"`, and `groupID > 0`.
    - `InspectionSettings` (`0005-inspection.patch:759-772`) has no `IncludePatterns` or `ExcludePatterns` fields.
    - `inspectionAccount` in `codex_inspection_handler.go` (`0005-inspection.patch:881-893`) does not extract account email from `account.Extra` or `account.Credentials`.
    - `web/inspection.js` (`0006-evaluation-ui.patch:1363-1865`) and `web/ui.html` (`0006-evaluation-ui.patch:2593-2645`) have no include/exclude pattern inputs.

### 5. Version Number (`版本号`) and New Upstream Features (`v0.4.5` – `v0.4.6`)

#### Version Number Locations

- **Upstream (`internal/plugin/plugin.go:17`, `internal/plugin/ui.go:74`, `internal/plugin/web/ui.html:144`)**:
  - `internal/plugin/plugin.go:17` defines `const pluginVersion = "0.4.6"`.
  - `internal/plugin/ui.go:74` replaces `"<!--PLUGIN_VERSION-->"` with `pluginVersion`.
  - `internal/plugin/web/ui.html:144` renders `<span>&thinsp;·&thinsp;版本 v<!--PLUGIN_VERSION--></span>`.
- **Current Sub2API Plugin (`plugins/codex-candy-eval/patches/0006-evaluation-ui.patch:16,70,2672`)**:
  - `backend/internal/codexeval/web.go` (`0006-evaluation-ui.patch:16`) still defines `const pluginVersion = "0.3.14"`.
  - `backend/internal/codexeval/web.go` (`0006-evaluation-ui.patch:70`) replaces `"<!--PLUGIN_VERSION-->"` with `pluginVersion`.
  - `backend/internal/codexeval/web/ui.html` (`0006-evaluation-ui.patch:2672`) renders `<span>&thinsp;·&thinsp;版本 v<!--PLUGIN_VERSION--></span>`.
  - Even though upstream `v0.4.2`, `v0.4.3`, and `v0.4.4` features were synced in earlier tasks, `pluginVersion` in `0006-evaluation-ui.patch:16` remained at `"0.3.14"`.

#### New Upstream Features in `v0.4.5` and `v0.4.6`

- **SIWC (`Sign In With ChatGPT`) Evaluation (`v0.4.6`)**:
  - **Backend (`internal/plugin/siwc.go:1-225`)**: Adds `POST /v0/management/plugins/cpa-codex-candy-eval/siwc/run`. It requires an `auth_files` credential with `Provider == "codex"`, sends a 1-shot minimal Responses streaming probe (`{"model": model, "store": false, "stream": true, "input": [{"role": "user", "content": "Reply with OK."}]}`) with `User-Agent: cpa-siwc-check/0.4.6`, and classifies the outcome into `available` (`SIWC 可用`), `restricted` (`订阅共享受限`, error code `subscription_sharing_user_not_eligible`), `limited` (`额度或频率受限`), `auth_error` (`认证异常`), `cancelled`, or `failed`.
  - **State Migration (`internal/plugin/migration.go:13,18-19,59`)**: Bumps `stateSchemaVersion` from `2` to `3` and adds the `siwc` history slice to `historyState` (`internal/plugin/state.go:15,23-35`).
  - **Frontend (`internal/plugin/web/siwc.js:1-193`, `ui.html:46-50,331-428`)**: Adds the fourth tab (`SIWC` in Sub2API to match the concise tab naming style) with model selector, concurrency selector, credential filter, progress bar, history table, and detail modal.
  - **Sub2API Applicability**: Sub2API OpenAI OAuth accounts can execute the 1-shot Responses probe via `SendCodexEvaluation` (`User-Agent: cpa-siwc-check/0.4.6`).
- **Storage Extraction (`v0.4.5`, `internal/plugin/web/storage.js`) and Shared Credentials Helper (`v0.4.6`, `internal/plugin/web/credentials.js`)**:
  - Upstream extracted `storage.js` (`readSaved`, `writeSaved`, `removeSaved`) and `credentials.js` (`credentialType`, `filteredCredentials`, `renderCredentials`, `populateCredentialTypes`) out of `app.js` and `components.js`.
- **Oh My CPA Hosting (`56f22d7`, `internal/plugin/web/host.js`)**:
  - Adds CPA-specific parent-frame `postMessage` handshake (`ohmycpa:host:init`). This is specific to Oh My CPA and is not needed for Sub2API's `/admin/codex-eval` iframe integration (`0006-evaluation-ui.patch` already reads Sub2API's `auth_token` from `localStorage`).

## External References

- Upstream repository: `https://github.com/haowang02/cpa-plugin-codex-candy-eval` (latest tag `v0.4.6`, commit `0ae33b626aa27a191fd91731230521e90656c8b4`).
- Previously synced upstream commit: `179d6dae48a0f0a735637ea2f373345b91caaca8` (tag `v0.4.4`).

## Related Specs

- `.trellis/spec/backend/native-inspection.md`: Documents the current Sub2API native inspection architecture and notes at line 80 that include/exclude account controls were removed in earlier iterations.
- `.trellis/spec/backend/runtime-installation.md`: Documents the runtime installation and patch stack conventions.

## Caveats and Notes

- **Spec Conflict on Wildcard Matching**: `.trellis/spec/backend/native-inspection.md` (line 80) currently states that include/exclude account controls, fields, persistence keys, and filtering logic are removed. Restoring name/email wildcard matching requires updating both `0005-inspection.patch` / `0006-evaluation-ui.patch` and `.trellis/spec/backend/native-inspection.md`.
- **Two Distinct Inspection Paradigms**: Upstream's `/inspection` API (`internal/plugin/inspection.go`) is a stateless REST endpoint pair driven by an external script (`examples/inspection.py`) that supports both `test: "candy"` and `test: "fingerprint"`. Sub2API's `0005-inspection.patch` is an internal background scheduler with a built-in UI tab (`自动巡检`) that currently only runs `candy` checks.
- **Cross-Provider Protocol Translation**: Upstream relies on CPA's host runtime (`host.model.execute_stream` with `entry_protocol: "openai-response"` and `forced_provider`) to translate OpenAI Responses requests into Claude, Gemini, or OpenAI-compatible calls. In Sub2API, `SendCodexEvaluation` (`0004-admin-channel.patch`) executes HTTP requests directly and must translate `openai-response` payloads for non-OpenAI platforms (`anthropic`, `gemini`, `antigravity`) or custom provider keys.
