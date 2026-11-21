# Research: CLIProxyAPI PR #7016 to Sub2API v0.2.24 (Converged)

## Source Baseline

- Upstream Sub2API `v0.2.24` (`5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`), `backend/internal/`.
- CLIProxyAPI `v8.0.45` (`router-for-me/CLIProxyAPI` PR #7016 / `023dd2ad`): `internal/signature/gemini_validation.go`, `internal/signature/gemini_sanitize.go`.
- Existing plugin patch: `plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch` (459 lines across 10 files).

## 1. Incident & Wire Envelope Facts

- Live MSub2 `v0.2.24` Ops logs show wire HTTP 400 signature errors (`Ops 26850, 26853, 26855`) recover via `signature_error`, while `AIStudio2API` HTTP 200 raw JSON `Corrupted thought signature.` (`Ops 26851, 26852, 26854, 26856`, `stream_failed`, `ttft=None`, `0/0` usage) bypasses wire HTTP 400 recovery (`gemini_messages_compat_service.go:2972-2977`, `gemini_response_signal.go:349-377`).
- `CLIProxyAPI` PR #7016 proved AI Studio / Gemini API / Code Assist emit protobuf `field 2 -> field 1` wrapped signatures (`0x12` outer bytes -> `0x0a` inner bytes), while Vertex AI emits bare-Tink signatures (`0x01` + 4-byte key ID + ciphertext, `>=21` bytes, key ID `8f 3d 6b 5f`). Non-Vertex endpoints reject Vertex bare-Tink with `400 Corrupted thought signature.`.

## 2. Spec-Aligned Cuts Applied

1. **No unrequested `README.md` edits**: `.trellis/spec/guides/index.md:7` forbids modifying docs unless requested.
2. **No Chromium gate or multiplied test matrices**: `.trellis/spec/backend/gemini-signature-rectifier.md:140-142` and `backend/quality-guidelines.md:21-22,44,47-48` require Chromium only when settings UI behavior changes and forbid multiplying test cases.
3. **Keep `json.RawMessage` in existing `gemini_native_signature_cleaner.go`**: `.trellis/spec/backend/gemini-signature-rectifier.md:74` mandates `json.RawMessage` maps/arrays. Extending the existing walker avoids creating a new upstream file or rewriting in `gjson`/`sjson`.
4. **No `gemini-2.` model-prefix gate or `mappedModel` reordering**: Gemini 2.5 uses no non-function signatures and optional `functionCall` signatures where `skip_thought_signature_validator` is valid; residual-400 test fixtures in `test_gemini_native_signature_rectifier_test.go` update `old-signature`/`old-call` to synthetic `field 2 -> field 1` wrapped signatures so they pass preflight and reach HTTP 400 force-clean.
5. **No extra `32 MiB` cap or cross-provider inner classifiers**: Gemini routes already enforce request body limits (`server/routes/gateway.go:358-370`, `middleware/request_body_limit.go:18`). Complete `protowire` consumption of outer field 2 (bytes, exact end) -> inner field 1 (bytes, exact end, `len > 0`) deterministically accepts wrapped Gemini payloads and rejects `0x01` bare-Tink, malformed lengths, and trailing bytes without Claude disambiguation sub-parsers.
6. **Inline `bare_tink` check**: `len(decoded) >= 21 && decoded[0] == 0x01 && bytes 1..4 == 8f3d6b5f`, gated by `allowBareTink`, with no envelope registry or options structs.
7. **In-place hint update**: Only the two `geminiNativeSignatureHint` values in `frontend/src/i18n/locales/{en,zh}/admin/settings.ts` (`patch:393,406`) and their matching literals in `tests/test_rectifier_settings.test.ts:88-92` change.
