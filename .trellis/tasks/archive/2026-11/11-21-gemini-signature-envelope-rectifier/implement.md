# Implementation Plan: Gemini Signature Envelope Rectifier

## Ordered Checklist

1. **Update production patch (`plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch`)**:
   - Extend `backend/internal/service/gemini_native_signature_cleaner.go` in place using `json.RawMessage`: add `isGeminiNativeVertexTarget`, `replayGeminiNativeThoughtSignature`, `hasPartKey`, and unified `sanitizeGeminiNativeThoughtSignatures(body, allowBareTink, force)` with retained-output parallel grouping.
   - Update `backend/internal/service/gemini_messages_compat_service.go`: at `ForwardNative:1123`, read `IsGeminiNativeSignatureRectifierEnabled(ctx)` once per request (returning `ctx.Err()` if canceled), run proactive `sanitizeGeminiNativeThoughtSignatures` when enabled or `ensureGeminiFunctionCallThoughtSignatures` when disabled, and reuse that boolean to guard the single `sanitizeGeminiNativeThoughtSignatures(body, false, true)` HTTP 400 retry branch.
   - Update `geminiNativeSignatureHint` in `frontend/src/i18n/locales/{en,zh}/admin/settings.ts`.
2. **Update focused flat tests (`plugins/gemini-signature-rectifier/tests/`)**:
   - In `test_gemini_native_signature_rectifier_test.go`: update residual HTTP 400 fixtures (`AllBuilders`, etc.) to use synthetic valid `field 2 -> field 1` wrapped signatures so they exercise the HTTP 400 force-clean retry; update preflight settings-cancellation test (`0` upstream calls on preflight cancel + separate response-time cancel); add non-multiplied focused assertions for `protobuf_field_2` vs `bare_tink` (Vertex vs non-Vertex), parallel grouping + retained-output regrouping after empty-carrier removal, Vertex host classification, and `toolCall`/`functionResponse` handling.
   - In `test_rectifier_settings.test.ts`: update the two expected `geminiNativeSignatureHint` string literals (`lines 88-92`).
3. **Verify via build entry**:
   - Standalone plugin build: `cd plugins/gemini-signature-rectifier && PYTHONDONTWRITEBYTECODE=1 UPSTREAM_TAG=v0.2.24 python3 -B scripts/build.py`
   - Root combined build: `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py`
   - Confirm `gofmt` clean, `0` test files in patch, and no unrequested doc/manifest modifications.

## Risky Files & Rollback

- `plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch` (keep exact 10-file patch set and builder error precedence).
- `plugins/gemini-signature-rectifier/tests/test_gemini_native_signature_rectifier_test.go` (use valid wrapped fixtures for residual-400 tests vs `bare_tink`/corrupt fixtures for preflight tests).
- Rollback: submodule `HEAD` (`6f18bc3`) and parent `HEAD` (`34686ba`).

## Pre-Start Gate

- `implement.jsonl` and `check.jsonl` curated and validated (`task.py validate` 0 warnings).
- Obtain explicit user approval on this debloated plan before running `task.py start`.
