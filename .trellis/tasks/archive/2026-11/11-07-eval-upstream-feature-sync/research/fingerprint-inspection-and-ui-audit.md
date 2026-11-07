# Research: Fingerprint Single-Run Inspection, Mode-Aware `下次巡检` Display, and Unrestricted Group Selection

- **Query**:
  1. **Option A (`fingerprint` single-run without multi-run confirmation)**: Investigate how `backend/internal/codexeval/inspection.go` (`0005-inspection.patch`) should execute 1 fingerprint evaluation (3 challenges) per account without triggering the `MaxTestsPerAccount - 1` confirmation loop (`240s` recovery wait + extra runs).
  2. **Mode-Aware `下次巡检` Display (`下次巡检 的显示需要按照方式选择走`)**: Audit `0006-evaluation-ui.patch` (`web/components.js`, `web/inspection.js`, `web/style.css`, `web/ui.html`) and `0005-inspection.patch` for every place where `下次巡检` (`#inspection-status`, `#inspection-phase`, `#inspection-next`, `#inspection-progress`, `#inspection-round-summary`) is rendered and how it must follow the selected `检查方式` (`test_type`: `candy` vs `fingerprint`).
  3. **Unrestricted Group Selection (`模型分组选择还有问题 就别筛选了 直接允许所有分组`)**: Audit every place in frontend (`web/catalog.js`, `web/credentials.js`) and backend (`0004-admin-channel.patch`, `0005-inspection.patch`) that filters groups or accounts by `SUPPORTED_PLATFORMS`.
- **Scope**: Read-only audit of `plugins/codex-candy-eval/patches/0004-admin-channel.patch`, `0005-inspection.patch`, `0006-evaluation-ui.patch`, `tests/test_codexeval_inspection_test.go`, `tests/test_ui.cjs`, `/tmp/cpa-upstream-v0.4.6/`, and `/tmp/sub2api-v0.2.20-base/backend/internal/domain/platforms.go`.
- **Date**: 2026-11-08

---

## 1. Files Found

- `plugins/codex-candy-eval/patches/0005-inspection.patch` — Contains `backend/internal/codexeval/inspection.go` (coordinator `run()`, `testPhase()`, `configure()`), `inspection_settings.go` (`validInspectionAccountType`), and `codex_inspection_handler.go` (`isInspectionSupportedAccount`).
- `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch` — Contains `web/components.js` (`credentialCard` where `#inspection-status` is created), `web/inspection.js` (`fillInspectionSettings`, `updateInspectionVisibility`, `renderInspectionState`, `formatInspectionRoundSummary`), `web/catalog.js` (`refreshCatalog` and `fetchNativeAccounts` group/account platform filtering), `web/credentials.js` (`SUPPORTED_PLATFORMS` and `PLATFORM_LABELS`), and `web/style.css` (`.candy-head .inspection-status`).
- `plugins/codex-candy-eval/patches/0004-admin-channel.patch` — Contains `backend/internal/service/account_codex_eval_service.go` (`isCodexEvalAccountSupported`, `CodexEvalModels`, `SendCodexEvaluation`).
- `plugins/codex-candy-eval/tests/test_codexeval_inspection_test.go` — Go unit tests for `inspection.go` (`TestCodexInspectionFingerprintModeAndWildcards`).
- `plugins/codex-candy-eval/tests/test_ui.cjs` — JSDOM tests for `#inspection-status` placement, `test_type`, and group/account catalog loading.
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go` & `fingerprint.go` — Upstream single-run fingerprint inspection reference (`fingerprintTarget = 3` challenges per run, no multi-run confirmation loop).
- `/tmp/sub2api-v0.2.20-base/backend/internal/domain/platforms.go` — Sub2API platform registry (`anthropic`, `openai`, `gemini`, `antigravity`, `grok`, `kimi`, `zhipu`, `deepseek`, `minimax`, `opencode_go`, `typesafe`, `command_code`, `cline`, plus `composite` for groups).

---

## 2. Topic 1: Option A — Single-Run Fingerprint Inspection (No 9-Round Multiplication)

### 2.1 Root Cause in `0005-inspection.patch`
In `plugins/codex-candy-eval/patches/0005-inspection.patch` (`backend/internal/codexeval/inspection.go`):
1. `run()` (`0005-inspection.patch:525-588`) runs `first := i.testPhase(ctx, s, eligible, 1, false, ...)` and, whenever `(current.Verdict == InspectionVerdictDegraded) != !answers[0]`, appends `a` to `groups[target]` (`line 546`).
2. For each non-empty `groups[target]`, if `s.MaxTestsPerAccount > 1` (default `3`), `run()` waits `i.recovery` (`240s` when `target == s.NormalPriority`, `lines 556-561`) and calls `i.testPhase(ctx, s, group, s.MaxTestsPerAccount-1, true, confirmed)` (`line 582`).
3. Inside `testPhase()` (`0005-inspection.patch:703-710`), `if testType == "fingerprint" { batches = max(runs, 1) }` runs `s.MaxTestsPerAccount - 1` (`2`) additional full fingerprint evaluations. Since each fingerprint evaluation (`fingerprint.go:19`) sends `fingerprintTarget = 3` challenges, a state transition with default `max_tests_per_account = 3` executes **`3` fingerprint runs × `3` challenges = `9` challenges** per account.

### 2.2 Required Change in `0005-inspection.patch` (Option A)
1. **In `run()` (`backend/internal/codexeval/inspection.go`, `0005-inspection.patch:525-547`)**:
   - When `testType == "fingerprint"`, a single fingerprint evaluation already executes 3 challenges and produces a 3-challenge statistical attribution (`r.Attribution.Prediction`).
   - Therefore, in the `first` phase completion callback, when `(current.Verdict == InspectionVerdictDegraded) != !answers[0]` (a state transition between normal and degraded) and `testType == "fingerprint"`, immediately mark the result `"recommended"` with `TargetPriority = &target` and call `apply(a, target)` instead of queueing `a` into `groups[target]`:
     ```go
     if (current.Verdict == InspectionVerdictDegraded) == !answers[0] {
     	apply(a, target)
     	return
     }
     if testType == "fingerprint" {
     	i.result(n, func(r *InspectionResult) { p := target; r.TargetPriority = &p; r.Outcome = "recommended" })
     	apply(a, target)
     	return
     }
     groups[target] = append(groups[target], a)
     ```
2. **In `testPhase()` (`backend/internal/codexeval/inspection.go`, `0005-inspection.patch:688-790`)**:
   - Because `testType == "fingerprint"` only ever executes 1 fingerprint run in `first` (`runs = 1`), `testPhase` does not need multi-step fingerprint batching (`batches := 1`). Each account executes exactly 1 fingerprint run (`r.Tests == 1`, `len(r.RunIDs) == 1`, 3 challenges total), with no `recovery_wait` and no confirmation runs.
3. **In `web/ui.html` & `web/inspection.js` (`0006-evaluation-ui.patch`)**:
   - Keep `推理强度` (`effort`) and `每账户最多测试次数` (`max_tests_per_account`) in `#inspection-auto-fields`, or optionally disable/dim them when `test_type === "fingerprint"`?
   - **Important check**: Existing `tests/test_ui.cjs:408-415` asserts the exact 6-child 3-row 2-column grid structure of `#inspection-auto-fields`. Keeping the grid layout intact (and either leaving the inputs enabled or keeping their values in the form payload) preserves the 3-row layout contract verified in L4 (`1280px` and `430px`).

---

## 3. Topic 2: Mode-Aware `下次巡检` Display (`下次巡检 的显示需要按照方式选择走`)

### 3.1 Root Cause in `0006-evaluation-ui.patch` & `0005-inspection.patch`
1. **`#inspection-status` Is Hardcoded Only in `#candy-credentials` (`web/components.js`, `0006-evaluation-ui.patch:1217-1220`)**:
   ```js
   function credentialCard(prefix, test, columns) {
     const clearLabel = `清空${test}记录`;
     const inspection = prefix ? "" : `<span id="inspection-status" class="inspection-status" aria-live="polite" hidden><span id="inspection-phase"></span><span id="inspection-next"></span><span id="inspection-progress"></span><span id="inspection-round-summary" hidden></span></span>`;
     return `<div class="section-head credential-head${prefix ? "" : " candy-head"}"><h2>账户</h2><label class="switch credential-enabled-filter"><input id="${prefix}enabled-only" type="checkbox" role="switch"><span>仅启用</span></label>${inspection}<div class="credential-filters">...
   ```
   - `#inspection-status` (which contains `#inspection-phase`, `#inspection-next` `下次巡检：...`, `#inspection-progress`, and `#inspection-round-summary`) is only created inside `#candy-credentials .credential-head` (`prefix === ""`).
   - When the user selects `检查方式` = `指纹` (`test_type === "fingerprint"`), `#inspection-status` (`下次巡检：...`) remains on the **糖果 (`#candy-panel`)** tab and is **absent** from the **指纹 (`#fingerprint-panel`)** tab (`#fp-credentials .credential-head`)!
2. **Mobile Responsive CSS Selector Is Scoped to `.candy-head` (`web/style.css`, `0006-evaluation-ui.patch:2596`)**:
   ```css
   .candy-head .inspection-status { order: 1; flex-basis: 100%; }
   ```
   - Scoped to `.candy-head` instead of `.credential-head .inspection-status`.
3. **Stale Round Summary Across Mode Switches (`0005-inspection.patch:173-187` & `web/inspection.js:1812-1840`)**:
   - In `backend/internal/codexeval/inspection.go` (`configure(s)` at `0005-inspection.patch:173-187`), changing `s.TestType` while idle (`!i.state.Running`) leaves `i.state.RoundSummary` from the previous mode intact.
   - In `web/inspection.js`, changing `test_type` calls `updateInspectionVisibility()`, which does not relocate `#inspection-status` or re-render `renderInspectionState(inspectionState)`.

### 3.2 Required Changes so `下次巡检` Follows `test_type` (`检查方式`) — and Removal of Unsolicited `本轮...巡检` Summary
1. **Remove Unsolicited `InspectionRoundSummary` / `#inspection-round-summary` (`本轮...巡检`)**:
   - Upstream `/tmp/cpa-upstream-v0.4.6/` has **zero** `本轮...巡检` UI text or `round_summary` struct (`internal/plugin/inspection.go` only returns `{"running": busy, "credentials": items}` with per-credential `degraded *bool` for an external script, and `internal/plugin/web/` has no inspection status UI at all).
   - In `plugins/codex-candy-eval` `HEAD` (before this task's uncommitted changes), `#inspection-status` only had `<span id="inspection-phase"></span><span id="inspection-next"></span><span id="inspection-progress"></span>`, and `.trellis/spec/backend/native-inspection.md:100` explicitly required: `Do not show a completed-phase caption or stale completed progress. Hide empty status containers.`
   - `InspectionRoundSummary`, `RoundSummary`, `<span id="inspection-round-summary" hidden></span>`, and `formatInspectionRoundSummary` (`本轮糖果巡检：...` / `本轮指纹巡检：...`) were newly invented in this task's uncommitted diff and **must be removed** from `0005-inspection.patch`, `0006-evaluation-ui.patch`, `test_codexeval_inspection_test.go`, `test_ui.cjs`, and `.trellis/spec/backend/native-inspection.md`.
2. **Dynamic Placement of `#inspection-status` Between `#candy-credentials` and `#fp-credentials` (`web/inspection.js`)**:
   - Determine the active inspection mode from `inspectionField("test_type")?.value`:
     ```js
     function currentInspectionTestType() {
       return inspectionField("test_type")?.value === "fingerprint" ? "fingerprint" : "candy";
     }
     ```
   - Move the single `#inspection-status` element (`#inspection-phase`, `#inspection-next` `下次巡检：...`, `#inspection-progress`) into the matching tab's `.credential-head` (right before `.credential-filters`):
     ```js
     function syncInspectionStatusPlacement() {
       const statusEl = document.getElementById("inspection-status");
       const targetCard = document.getElementById(currentInspectionTestType() === "fingerprint" ? "fp-credentials" : "candy-credentials");
       const targetHead = targetCard?.querySelector(".credential-head");
       if (statusEl && targetHead && statusEl.parentElement !== targetHead) {
         targetHead.insertBefore(statusEl, targetHead.querySelector(".credential-filters") || null);
       }
     }
     ```
   - Call `syncInspectionStatusPlacement()` in both `updateInspectionVisibility()` (so switching `检查方式` in `设置` immediately moves `#inspection-status` to the selected tab) and `renderInspectionState(state)`.
3. **Responsive CSS (`web/style.css`, `0006-evaluation-ui.patch:2596`)**:
   - Change `.candy-head .inspection-status { order: 1; flex-basis: 100%; }` to `.credential-head .inspection-status { order: 1; flex-basis: 100%; }` so narrow viewports wrap `#inspection-status` identically in both `#candy-credentials` and `#fp-credentials`.

---

## 4. Topic 3: Allow All Groups Without Platform Filtering (`模型分组选择还有问题 就别筛选了 直接允许所有分组`)

### 4.1 Why Group Selection Failed on Real Sub2API Deployments
In Sub2API (`/tmp/sub2api-v0.2.20-base/backend/internal/domain/platforms.go:37-86`), a group's `platform` can be:
- `composite` (`PlatformComposite = "composite"` — a multi-platform composite group)
- `anthropic`, `openai`, `gemini`, `antigravity`
- `grok`, `kimi`, `zhipu`, `deepseek`, `minimax`, `opencode_go`, `typesafe`, `command_code`, `cline`

Because `web/credentials.js` (`0006-evaluation-ui.patch:1271`) defined `const SUPPORTED_PLATFORMS = ["openai", "anthropic", "gemini", "antigravity"]` and `web/catalog.js` filtered both `groups` and `accounts` by `SUPPORTED_PLATFORMS`:
1. Any `composite`, `deepseek`, `kimi`, `zhipu`, `minimax`, `grok`, `opencode_go`, `command_code`, `cline`, or `typesafe` group was **dropped** from `groups` at `web/catalog.js:847`.
2. If `selectedGroup` pointed to one of those groups, `syncGroupControls()` (`web/catalog.js:804`) displayed it as `分组 <id>（不可用）`!
3. Even if selected, `fetchNativeAccounts` (`web/catalog.js:891`) dropped any account whose `a.platform` was not in those 4 strings!

### 4.2 Complete Inventory of Group & Platform Filters to Remove / Relax

| File (`Patch`) | Line(s) | Current Filter | Required Fix |
| --- | --- | --- | --- |
| `backend/internal/codexeval/web/catalog.js` (`0006-evaluation-ui.patch`) | `847` | `groups = (available \|\| []).filter((g) => !g.platform \|\| SUPPORTED_PLATFORMS.includes(String(g.platform).toLowerCase()));` | Replace with `groups = available \|\| [];` — **do not filter groups at all**. |
| `backend/internal/codexeval/web/catalog.js` (`0006-evaluation-ui.patch`) | `891` | `const items = (data.items \|\| []).filter((a) => !a.platform \|\| SUPPORTED_PLATFORMS.includes(String(a.platform).toLowerCase()));` | Replace with `const items = data.items \|\| [];` — load all accounts belonging to the selected group. |
| `backend/internal/codexeval/web/credentials.js` (`0006-evaluation-ui.patch`) | `1271-1277` | `PLATFORM_LABELS` only lists `openai`, `anthropic`, `gemini`, `antigravity` | Add labels for all Sub2API platforms (`grok: "Grok"`, `kimi: "Kimi"`, `zhipu: "Zhipu GLM"`, `deepseek: "DeepSeek"`, `minimax: "MiniMax"`, `opencode_go: "OpenCode"`, `typesafe: "TypeSafe"`, `command_code: "Command Code"`, `cline: "Cline"`), keeping `PLATFORM_LABELS[platform] \|\| platform` fallback. |
| `backend/internal/service/account_codex_eval_service.go` (`0004-admin-channel.patch`) | `192-202` | `isCodexEvalAccountSupported` only allows `PlatformOpenAI, PlatformAnthropic, PlatformGemini, PlatformAntigravity` | Allow any non-nil account with a supported credential type (`account.IsOAuth() \|\| account.Type == AccountTypeAPIKey \|\| account.Type == AccountTypeUpstream`, or any concrete Sub2API platform). |
| `backend/internal/service/account_codex_eval_service.go` (`0004-admin-channel.patch`) | `214-306` | `CodexEvalModels` only runs OpenAI discovery for `account.Platform == PlatformOpenAI` and fallback only lists Anthropic/Gemini/Antigravity | For `account.Platform == PlatformOpenAI`: keep existing discovery. For other `account.IsOpenAICompatible()` accounts (`deepseek`, `kimi`, `zhipu`, `minimax`, `grok`, `opencode_go`, `command_code`, `cline`), try `s.FetchUpstreamSupportedModels(ctx, account)` when a custom `base_url` is present and fall back to `fallbackCodexEvalModels(account)` (returning mapped models + platform defaults such as `xai.DefaultModels()` for `grok` or `openai.DefaultModels`) without failing model discovery when an upstream `/v1/models` endpoint is absent. |
| `backend/internal/service/account_codex_eval_service.go` (`0004-admin-channel.patch`) | `411-416` | `SendCodexEvaluation` switches on `PlatformAnthropic` and `PlatformGemini, PlatformAntigravity` | Also route `account.RoutesProtocolByInbound() && account.GetAPIProtocol() == APIProtocolAnthropic` to `sendCodexAnthropicEvaluation`; all other OpenAI-compatible platforms (`deepseek`, `kimi`, `zhipu`, `minimax`, `grok`, `opencode_go`, `command_code`, `cline`) naturally use the OpenAI / Chat Completions branch (`GetOpenAIProtocolAPIKey()`, `GetOpenAIBaseURL()`). |
| `backend/internal/handler/admin/codex_inspection_handler.go` (`0005-inspection.patch`) | `1148-1158` | `isInspectionSupportedAccount` only allows `PlatformOpenAI, PlatformAnthropic, PlatformGemini, PlatformAntigravity` | Match `isCodexEvalAccountSupported`: allow any non-nil account with `a.IsOAuth() \|\| a.Type == service.AccountTypeAPIKey \|\| a.Type == service.AccountTypeUpstream`. |
| `backend/internal/codexeval/inspection_settings.go` (`0005-inspection.patch`) | `1011-1031` | `validInspectionAccountType` only allows `platform` in `"openai", "anthropic", "gemini", "antigravity"` | Accept any non-empty lowercase platform identifier `[a-z0-9_-]+` paired with `oauth`, `setup-token`, `apikey`, or `upstream`. |

---

## 5. Related Specs

- `.trellis/spec/backend/native-inspection.md`:
  - Update lines 70, 105, 233, 249, 262 to reflect:
    1. Single-run fingerprint inspection without multi-run confirmation (`test_type == "fingerprint"` runs 1 three-challenge fingerprint evaluation per account without `max_tests_per_account - 1` confirmation runs or `240s` recovery wait).
    2. `#inspection-status` (`下次巡检：...`, phase, progress, round summary) is displayed in the account header of the tab matching `test_type` (`糖果` when `candy`, `指纹` when `fingerprint`).
    3. All Sub2API groups are selectable without platform filtering.
- `.trellis/spec/backend/runtime-installation.md`:
  - Update lines 47, 134 to reflect that all Sub2API groups are loaded without platform filtering.
