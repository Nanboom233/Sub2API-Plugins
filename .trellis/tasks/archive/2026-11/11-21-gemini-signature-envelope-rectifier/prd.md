# Gemini Signature Envelope Rectifier

## Goal

Prevent cross-endpoint Gemini thought-signature failures (such as Vertex AI bare-Tink signatures replayed by AstrBot to AIStudio2API / AI Studio / Code Assist) before sending upstream requests, while preserving valid same-endpoint signatures and retaining the single HTTP 400 force-clean fallback.

## Confirmed Facts

- Live MSub2 `v0.2.24` Ops/Usage logs show `plugins/gemini-signature-rectifier` recovers wire HTTP 400 rejections (`Ops 26850, 26853, 26855`), while `AIStudio2API` HTTP 200 raw JSON `Corrupted thought signature.` (`Ops 26851, 26852, 26854, 26856`, `stream_failed`) bypasses wire HTTP 400 recovery.
- `CLIProxyAPI` PR #7016 (`v8.0.45`) confirmed AI Studio / Code Assist emit protobuf `field 2 -> field 1` wrapped signatures, whereas Vertex AI emits bare-Tink signatures (`0x01` + 4-byte key ID `8f3d6b5f` + ciphertext, `>=21` bytes) rejected by non-Vertex endpoints.
- Upstream `Sub2API v0.2.24` (`5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`) already declares `google.golang.org/protobuf` (`protowire`) in `backend/go.mod` and enforces HTTP body limits on Gemini routes.
- Existing `gemini-signature-rectifier.patch` already walks `contents[].parts[]` with `json.RawMessage` maps/arrays in `gemini_native_signature_cleaner.go` (`.trellis/spec/backend/gemini-signature-rectifier.md:74`).
- Research notes: [pr7016-deep-code-research.md](./research/pr7016-deep-code-research.md).

## Requirements

1. **Endpoint-aware proactive sanitization (`R1`)**:
   - In `ForwardNative` (`gemini_messages_compat_service.go:1123-1125`), when `settings.Enabled && settings.GeminiNativeSignatureEnabled` is `true` (propagating `ctx.Err()` on cancellation), replace `ensureGeminiFunctionCallThoughtSignatures` with `sanitizeGeminiNativeThoughtSignatures(body, isGeminiNativeVertexTarget(account, action), false)`. Keep `ensureGeminiFunctionCallThoughtSignatures` when disabled.
   - Determine Vertex destination via `account.IsVertexServiceAccount()` (covering SA OAuth and `auth_mode=apikey`) or parsed official Vertex hostname (`aiplatform.googleapis.com`, `aiplatform.{us,eu}.rep.googleapis.com`, `<nonempty>-aiplatform.googleapis.com`) on custom-base API-key/OAuth paths without moving or duplicating builder URL validation.
   - Accept `protobuf_field_2` (complete outer field 2 bytes -> complete inner field 1 bytes with non-empty value via `protowire`) on all targets; accept `bare_tink` (`len >= 21`, byte `0 == 0x01`, bytes `1..4 == 8f3d6b5f`) only when `allowBareTink` is `true`. Accept padded/unpadded standard Base64 without re-encoding preserved values, and recognize bypass literals `skip_thought_signature_validator` and `context_engineering_is_the_way_to_go`.
2. **Extended `json.RawMessage` group-aware walker (`R2`)**:
   - Extend the existing `json.RawMessage` walker in `backend/internal/service/gemini_native_signature_cleaner.go` (`sanitizeGeminiNativeThoughtSignatures(body []byte, allowBareTink, force bool) ([]byte, bool)`) with no new upstream files and untouched exported `CleanGeminiNativeThoughtSignatures`.
   - Support `functionCall`/`function_call`, strip direct signatures from `functionResponse`/`function_response`, and preserve server-side `toolCall`/`tool_call`/`toolResponse`/`tool_response` Parts untouched.
   - Proactive mode (`force == false`) applies to `role == "model" || role == ""` (plus `functionResponse` cleanup) and preserves `thought: true`; force mode (`force == true`) remains role-agnostic and strips boolean `thought: true` on non-call Parts.
   - Compute parallel `functionCall` groups from **retained** Parts (after dropping modified `{}` / `{"text":""}` empty carriers and force-mode `thought: true` cleanup): only a missing/incompatible first call receives `skip_thought_signature_validator`; compatible real sibling/non-call signatures survive proactively; incompatible/bypass sibling and non-call signatures are deleted. Retain newly-empty-Content deletion and all-Contents/invalid-JSON rollback.
3. **Residual HTTP 400 fallback & locale hint sync (`R3`)**:
   - Retain existing `cachedContent` -> `checkErrorPolicyInLoop` -> reused request-scoped settings gate -> single `sanitizeGeminiNativeThoughtSignatures(body, false, true)` HTTP 400 retry, post-transport `ctx.Err()` check, `signatureRecoveryUsed`, `countTokens` Option B, and Ops events.
   - Update only the two `geminiNativeSignatureHint` strings in `frontend/src/i18n/locales/{en,zh}/admin/settings.ts` and their matching expected strings in `tests/test_rectifier_settings.test.ts`.

## Acceptance Criteria

- [ ] Non-Vertex native requests (`AIStudio2API`, AI Studio, Code Assist) replace Vertex `bare_tink` first-call signatures with `skip_thought_signature_validator` and strip sibling/non-call `bare_tink` signatures before sending upstream, while preserving valid `protobuf_field_2` signatures verbatim.
- [ ] Vertex native requests (`service_account` OAuth/`auth_mode=apikey` and official Vertex custom host) preserve both `bare_tink` and `protobuf_field_2` while normalizing corrupt/unknown signatures.
- [ ] Parallel-call grouping and retained-output regrouping (after empty-carrier deletion or force `thought: true` removal) never emit adjacent duplicate dummies, preserve `toolCall`/`toolResponse` and nested business integers (`9007199254740993`), and return `(body, false)` when unchanged or when all Contents would vanish.
- [ ] Disabled switch leaves existing behavior unchanged; preflight cancellation returns `ctx.Err()` with zero upstream requests; residual HTTP 400 rejections with shape-valid wrapped signatures trigger one force-clean retry with existing policy precedence and Ops events.
- [ ] Standalone (`UPSTREAM_TAG=v0.2.24`) and default combined (`python3 -B scripts/build.py`) builds pass all Go, Vitest, `check:i18n`, `vue-tsc`, and installer checks with zero test files in the patch and zero unrequested doc edits.

## Out of Scope

- Creating new upstream Go files, switching from `json.RawMessage` to `gjson`/`sjson`, adding model-name prefix gates (`gemini-2.*`), extra body-size caps, or cross-provider classifiers.
- HTTP 200 stream-prefix peeking, HTTP 400 array/plain-text error matcher changes, `pool_mode` policy changes, `gemini_v1beta_handler.go` edits, `SettingsView.vue` component edits, `README.md` edits, or manual Chromium runs.
