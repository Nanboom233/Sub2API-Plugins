# Design: Gemini Signature Envelope Rectifier

## Architecture & Patch Boundary

Keep the exact existing 10-file patch set in `plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch` with zero new files:

| Patched File | Change |
| --- | --- |
| `backend/internal/service/gemini_messages_compat_service.go` | At `ForwardNative:1123`, read `IsGeminiNativeSignatureRectifierEnabled(ctx)` once per request (propagating `ctx.Err()`), run proactive `sanitizeGeminiNativeThoughtSignatures` when enabled else `ensureGeminiFunctionCallThoughtSignatures`, and reuse that boolean to guard the single `force=true` HTTP 400 retry branch. |
| `backend/internal/service/gemini_native_signature_cleaner.go` | Extend the existing `json.RawMessage` walker with `allowBareTink`/`force`, retained-output parallel grouping, `isGeminiNativeVertexTarget`, and single `replayGeminiNativeThoughtSignature` helper. Keep exported `CleanGeminiNativeThoughtSignatures` untouched. |
| `frontend/src/i18n/locales/{en,zh}/admin/settings.ts` | Update `geminiNativeSignatureHint` text in place. |
| Remaining 6 DTO/handler/service/API/Vue files | Unchanged. |

## Core Contracts

### 1. Target Detection (`isGeminiNativeVertexTarget`)

```go
func isGeminiNativeVertexTarget(account *Account, action string) bool
```

- `account.IsVertexServiceAccount()` -> `true` (SA OAuth and `auth_mode=apikey`, generation and `countTokens`).
- `account.Type == AccountTypeOAuth` with non-empty `project_id` and `action != "countTokens"` -> `false` (Code Assist).
- Other `AccountTypeAPIKey` / `AccountTypeOAuth` -> `url.Parse(account.GetGeminiBaseURL(geminicli.AIStudioBaseURL))` hostname check only (`aiplatform.googleapis.com`, `aiplatform.{us,eu}.rep.googleapis.com`, `<nonempty>-aiplatform.googleapis.com`), with no `validateUpstreamBaseURL` call so builder error precedence stays identical.

### 2. Inline Envelope Validation

```go
func replayGeminiNativeThoughtSignature(raw string, allowBareTink, allowBypass bool) string
```

- `sig := strings.TrimSpace(raw)` once; return `""` when empty; for bypass literals `skip_thought_signature_validator` and `context_engineering_is_the_way_to_go`, return `sig` when `allowBypass` else `""`.
- Decode `base64.StdEncoding`, fallback `base64.RawStdEncoding`; reject empty decoded bytes; return `sig` without re-encoding.
- **`protobuf_field_2`**: `protowire.ConsumeTag` outer `#2 BytesType` (exact end) -> inner `#1 BytesType` (exact end, `len(value) > 0`).
- **`bare_tink`**: allowed only when `allowBareTink`: `len(decoded) >= 21 && decoded[0] == 0x01 && [4]byte(decoded[1:5]) == [4]byte{0x8f, 0x3d, 0x6b, 0x5f}`.

### 3. Unified `json.RawMessage` Walker

```go
func sanitizeGeminiNativeThoughtSignatures(body []byte, allowBareTink, force bool) ([]byte, bool)
```

- Unmarshal top-level map and `contents`/`parts` as `json.RawMessage` slices/maps (matching `.trellis/spec/backend/gemini-signature-rectifier.md:74`); return `(body, false)` when unchanged, invalid, or when all Contents would be removed.
- Preserve `toolCall`/`tool_call`/`toolResponse`/`tool_response` Parts untouched; strip direct signatures (`thoughtSignature`, `thought_signature`) from `functionResponse`/`function_response` (plus boolean `thought: true` in `force` mode).
- Skip non-model roles (`role != "model" && role != ""`) when `!force`.
- Track `firstCallSeen` on **retained** Parts:
  - First call (`hasCall && !firstCallSeen`): when `!force` and signature is compatible or bypass, canonicalize to `thoughtSignature`; otherwise set `skip_thought_signature_validator`.
  - Sibling call (`hasCall && firstCallSeen`): when `!force` and signature is compatible (non-bypass), canonicalize to `thoughtSignature`; otherwise delete signature keys.
  - Non-call Part: when `!force` and signature is compatible (non-bypass), canonicalize to `thoughtSignature`; otherwise delete signature keys (and in `force` mode, delete boolean `thought: true`).
  - Drop modified Parts left as `{}` or `{"text":""}` without updating `firstCallSeen`; for retained Parts, set `firstCallSeen = hasCall` whenever `hasCall || !retainedThoughtTrue`.

## Trade-Offs & Boundaries

- Shape-valid signatures that still fail contextually on upstream HTTP 400 recover via the existing `force=true` retry; shape-valid signatures failing via HTTP 200 in-band `stream_failed` remain outside static preflight scope.
- Handler pre-clean (`gemini_v1beta_handler.go:642-664`) still runs on missing sticky binding / account switch; the proactive walker removes its stray sibling/text dummies while keeping the first-call dummy.
