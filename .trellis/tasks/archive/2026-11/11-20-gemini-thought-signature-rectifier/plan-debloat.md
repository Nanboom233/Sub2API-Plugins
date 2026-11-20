# Plan Debloat Review: Cut Redundant Fallbacks, Speculation, and Redundant Compatibility

Target task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any subagent from running `hc send`.

## Directive

The user rejected redundant fallbacks, speculation, and redundant compatibility shims (`/chief-coordinator 不要冗余兜底 不要猜测 不要冗余兼容`).
Rewrite `prd.md`, `design.md`, and `implement.md` (and align any contradictory recommendation text in `research/count-tokens-and-settings.md`) to be minimal, factual, and free of every item below.

Planning-only boundary still applies:
- Do **NOT** run `task.py start`.
- Do **NOT** edit repo production/test/submodule/Git state.
- Do **NOT** rebuild frontend or re-run Playwright.

## Mandatory Cuts

### 1. Cut `*bool` and "old PUT client" compatibility shim
- In `UpdateRectifierSettingsRequest`, make `GeminiNativeSignatureEnabled` a plain `bool`, identical to the existing four booleans (`Enabled`, `ThinkingSignatureEnabled`, `ThinkingBudgetEnabled`, `APIKeySignatureEnabled`).
- Delete the `nil` check, the preliminary `GetRectifierSettings` read, the required-read failure branch, and all "old PUT client omitted/null field" requirements and handler tests.

### 2. Cut untouched `GetRectifierSettings` JSON compatibility matrix
- Do **NOT** modify `GetRectifierSettings` at all (`var settings RectifierSettings` + `json.Unmarshal` already yields `false` for plain `bool`).
- Delete requirements, tables, and test cases for legacy-omitted, null-field, top-level-null, empty, and malformed JSON parsing — those test Go's `encoding/json` and untouched upstream code, not our changes.
- Keep only tests for our new code: `DefaultRectifierSettings().GeminiNativeSignatureEnabled == false`, `IsGeminiNativeSignatureRectifierEnabled` (`Enabled && GeminiNativeSignatureEnabled`, returns `false` on read error, independent of thinking/API Key switches), and admin GET/PUT round-trip (`true` and `false`).

### 3. Cut cleaner speculation and redundant compatibility logic
Replace the 13-rule speculative cleaner with a minimal, deterministic, zero-guessing rule on direct `contents[].parts[]` (using `json.RawMessage` so nested business JSON and numbers are untouched):
- **Delete**: dual-alias (`functionCall` + `function_call` on the same Part) equality/conflict detection.
- **Delete**: guessed metadata field lists (`videoMetadata`, `mediaResolution`, etc.), guessed data-field spelling dictionaries (`inlineData`/`fileData`/`executableCode`/`codeExecutionResult`), and guessed relay `omitempty` speculation.
- **Keep ONLY**:
  1. If a direct Part has `functionCall` or `function_call`: set `thoughtSignature` to `geminiDummyThoughtSignature` and delete `thought_signature` if present. (If already `thoughtSignature == geminiDummyThoughtSignature` with no `thought_signature`, no change.)
  2. Else if a direct Part has `thoughtSignature`, `thought_signature`, or `thought: true`: delete `thoughtSignature`, `thought_signature`, and (when `true`) `thought`. If the remaining Part has no keys (`len == 0`) or only an empty `text: ""`, drop that Part. Otherwise keep the Part with all remaining fields untouched.
  3. Drop any `content` whose `parts` array becomes empty.
  4. If no contents remain or no actual change occurred (`changed == false`), return the original body and `false`.

### 4. Cut guessed rejection-verb list in error matcher
- Verify upstream `v0.2.23` `isGeminiSignatureRelatedError` and upstream error-message extraction helper.
- For `isGeminiNativeSignatureRelatedError([]byte) bool`: on HTTP 400 (enforced by caller), match normalized case-insensitive `thought signature` (`thoughtSignature`, `thought_signature`, `thought signature`) in the extracted upstream error message.
- **Delete** the guessed list of English rejection verbs (`invalid`, `corrupted`, `missing`, `required`, `must-have`).

### 5. Verify Ops event kinds against upstream `v0.2.23` (zero guessing)
- Verify exact Ops event kind strings present in public `v0.2.23` `antigravity_gateway_gemini.go` and `gateway_service.go` (`signature_error`, `signature_retry`, `signature_retry_request_error`).
- Only use event kind strings that genuinely exist in `v0.2.23`. Cut any invented kind string.

### 6. Cut untouched upstream tests and speculative fallback prose
- In `implement.md` tests:
  - Delete `existing estimate exceptions, image/signature text-estimator limits` (we do not touch `estimateGeminiCountTokens` or existing transport/transient/scope fallback branches). For `countTokens` Option B, test only: (a) signature-400 recovery succeeds → returns actual upstream `totalTokens`; (b) second 400 → returns 400 error without estimate.
  - Delete `nil-dependency` contract/test matrices (standard Go nil check `s.rateLimitService != nil && s.rateLimitService.settingService != nil` in one expression is enough; do not elevate it into a requirement/test matrix).
  - Delete Code Assist `any` numeric-conversion prose/test workarounds (untouched upstream builder).
  - Delete redundant duplicate prose across `prd.md`, `design.md`, and `implement.md`. Aim for crisp, tight docs (`design.md` <= ~180 lines, `implement.md` <= ~115 lines, `prd.md` <= ~50 lines) while keeping every locked user requirement and real spec contract intact.

## Preserve Locked Decisions (Do Not Alter)

- Plugin directory: `plugins/gemini-signature-rectifier` (template kit, LGPLv3, flat `tests/`, no nested `.trellis/`).
- Scope: all 4 `ForwardNative` builders; HTTP 400 only; cached-content + configured error policy take priority; max 1 recovery resend independent of ordinary `maxAttempts`.
- `countTokens`: Option B (participates in 1 recovery retry, returns upstream `totalTokens` on success, preserves 400 on repeated 400 with no new estimate).
- Setting: `rectifier_settings.gemini_native_signature_enabled`, default `false`, read error → `false`, master + sub-option required.
- Frontend copy & verified layout: exact locked en/zh text, initial `false`, Playwright Chromium visual check on final patch in Phase 2.2.
- Zero `wire_gen.go` / constructor changes (`rateLimitService.settingService`).
- Single production patch (`patches/gemini-signature-rectifier.patch`), zero test files in patch, standalone + combined `v0.2.23` builds.
