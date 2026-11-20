# Plan Lock Update: Default `false` and Final Copy

Target task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any subagent from running `hc send`.

## Scope and Boundaries

- Planning doc convergence ONLY.
- Do **NOT** run `task.py start`, create submodules, edit repo production/test files, or alter Git state.
- Do **NOT** re-run Playwright or rebuild frontend (UI copy and layout are unchanged and already verified).

## Locked User Decisions

1. **Frontend en/zh copy**: Keep the exact wording already verified in the preview screenshots:
   - `en`: `Gemini Native Signature Rectifier` / `Fix rejected thought signatures and retry native Gemini requests once. Configured error policies take priority.`
   - `zh`: `Gemini 原生签名整流` / `原生 Gemini 请求遇到思考签名错误时，修正后重试一次。已配置的错误策略优先。`
2. **R6 default**: **`gemini_native_signature_enabled` defaults to `false`** (opt-in, matching `apikey_signature_enabled`).

## Required Updates

1. Verify upstream `v0.2.23` `backend/internal/service/setting_features.go` (`IsAPIKeySignatureRectifierEnabled` / `GetRectifierSettings`, public unauthenticated fetch or existing verified notes) to confirm exact upstream behavior on read error when default is `false` (fail-closed `false`).
2. Update `prd.md`, `design.md`, `implement.md`, and `research/count-tokens-and-settings.md` so all four documents are 100% consistent:
   - Lock `gemini_native_signature_enabled` default to **`false`** for fresh installs, legacy JSON missing the field, `null` field / top-level `null`, empty/malformed records, runtime settings read error (fail-closed `false`), and nil optional service dependency (`false`).
   - Remove the pre-unmarshal `true` initialization hack from `design.md` and `implement.md` (standard zero-value `bool` unmarshal naturally yields `false` for omitted/null fields, matching `apikey_signature_enabled`, with zero change to existing fields!).
   - Preserve explicit `true` and explicit `false` in DB and API round trips.
   - Keep `UpdateRectifierSettingsRequest.GeminiNativeSignatureEnabled *bool` so omitted/null fields from old PUT callers read and preserve the currently stored value (protecting an admin's enabled `true` from silent reset); if that required read fails, return the native admin error without saving.
   - Update Vue `rectifierForm` initial default to `false`, and update Vue/Go test expectations and browser check notes (initial default `false`, enable → save `true` → reload, disable → save `false` → reload, sibling preservation, master-off hide).
   - Remove all `[PENDING FINAL PLAN APPROVAL]` / proposed-default markers on R6 default; clearly note that **planning is complete and only user approval to start Phase 2 implementation (`task.py start`) remains**.
   - Keep concise active-voice English spec style and verify all local links/anchors and JSONL entries remain valid.
