# Gemini Native Signature Rectifier

## 1. Scope / Trigger

Use this contract when changing native Gemini signature recovery or its administrator setting.
The verified integration baseline is Sub2API v0.2.24.
Owner: [production patch](../../../plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch).

`GeminiMessagesCompatService.ForwardNative` owns recovery across four request builders:

| Builder | Existing transport |
| --- | --- |
| API Key or relay | Native Gemini endpoint |
| OAuth AI Studio | Native Gemini endpoint |
| OAuth Code Assist | `/v1internal` request envelope |
| Vertex ServiceAccount | Native Vertex endpoint |

Keep Claude `Forward`, handler pre-cleaning, and Antigravity `ForwardGemini` unchanged.
Keep exported `CleanGeminiNativeThoughtSignatures` and `estimateGeminiCountTokens` unchanged.
The recovery cleaner acts only after an eligible upstream rejection.

## 2. Signatures

The patch extends existing service, DTO, handler, and frontend owners:

```go
func isGeminiNativeSignatureRelatedError(body []byte) bool
func cleanGeminiNativeThoughtSignaturesForRetry(body []byte) ([]byte, bool)
func (s *SettingService) IsGeminiNativeSignatureRectifierEnabled(ctx context.Context) bool

// Field in service.RectifierSettings and dto.RectifierSettings.
GeminiNativeSignatureEnabled bool `json:"gemini_native_signature_enabled"`
```

| Method | Path | Field |
| --- | --- | --- |
| GET | `/api/v1/admin/settings/rectifier` | Response `data.gemini_native_signature_enabled` is a Boolean |
| PUT | `/api/v1/admin/settings/rectifier` | Request and response use the same plain Boolean |

`UpdateRectifierSettingsRequest` uses `bool`, without pointer or omission semantics.
The TypeScript `RectifierSettings` interface requires `gemini_native_signature_enabled: boolean`.
`SettingsView.vue` binds the native `Toggle` to `rectifierForm.gemini_native_signature_enabled` and saves it with existing sibling fields.

## 3. Contracts

### Gate and settings UI

Recovery requires both `settings.Enabled` and `settings.GeminiNativeSignatureEnabled`.
The native option defaults to `false`. Missing saved fields and settings read errors also yield `false`.
The Thinking Signature and API Key Signature switches do not control this native option.
Read settings through `rateLimitService.settingService`. Preserve constructors and `wire_gen.go`.

The toggle uses ID `gemini-native-signature` and hint ID `gemini-native-signature-hint`.
Keep its label, `aria-label`, and `aria-describedby` bindings.
Both locale files define `admin.settings.rectifier.geminiNativeSignature` and `geminiNativeSignatureHint`.
GET, PUT, persistence, and the form retain other rectifier settings.

### Recovery order and budget

Apply cached-content handling first, then configured error policy, then native signature recovery.
Only an unmatched HTTP 400 can enter recovery.
Match the extracted upstream error message after lowercase conversion and removal of whitespace and underscores.
The normalized message must contain `thoughtsignature`. Unrelated body fields and authentication signatures do not qualify.

Clean the current native body once and resend only when the cleaner returns `changed == true`.
Set `signatureRecoveryUsed` before the resend. Allow at most one recovery resend per `ForwardNative` call.
The resend does not consume ordinary `maxAttempts`. Existing transient retries keep their budget and use the cleaned body.

Rebuild through the selected builder so transport, headers, model mapping, and Code Assist wrapping retain native behavior.
Check error policy again for each new response.

### Four direct-Part cleanup rules

Use `json.RawMessage` maps and arrays to preserve unrelated values and large integers.
Modify only direct `contents[].parts[]` metadata:

1. For `functionCall` or `function_call`, set `thoughtSignature` to `skip_thought_signature_validator` and remove `thought_signature`.
2. For other Parts, remove both signature aliases and remove `thought` only when its value is `true`.
3. Drop a modified Part only when empty or left with only `text: ""`. Drop a newly emptied content.
4. Return the original body with `false` for invalid input, unchanged input, or cleanup that removes all contents.

Preserve nested function arguments, business fields, whitespace text, unmarked empty Parts, and existing empty or null part arrays.
Keep `systemInstruction` and other locations outside `contents[].parts[]` unchanged.
A second cleanup returns `false` for the cleaned body.

### countTokens and Ops events

Use Option B for `countTokens`: attempt eligible signature recovery before its existing local-estimate behavior.
A successful resend returns upstream token counts. A second signature HTTP 400 remains an error, without a fabricated token result.
Preserve existing local estimates for their original transient failure conditions.

| Ops kind | Trigger |
| --- | --- |
| `signature_error` | An eligible HTTP 400 produces a changed body and starts recovery |
| `signature_retry` | The immediate recovery resend returns HTTP `>=400` |
| `signature_retry_request_error` | Recovery request construction or transport fails without cancellation |

Reset `isSignatureRetryAttempt` immediately after the recovery response or request failure.
Later ordinary transient retries must not inherit signature event labels.
Retain native retry and failover events alongside signature events.
Use native sanitized messages, detail handling, account/proxy fields, and upstream request IDs.

Close consumed response bodies and restore buffered bodies when later handlers need them.
Propagate cancellation and deadlines. Cancellation during the settings read returns the context error before recovery or error output.

## 4. Validation & Error Matrix

| Condition | Outcome |
| --- | --- |
| Master switch off, native option off, or settings read failure | Existing upstream error path without recovery |
| Cached-content rejection or configured error policy applies | Existing handling wins |
| HTTP 400 with matching message and changed body | One recovery resend |
| Different status or unrelated message | No signature recovery |
| Invalid body, unchanged body, or no remaining contents | Original body and existing error path |
| Recovery returns another signature HTTP 400 | Record `signature_retry`. Do not clean again. |
| Recovery returns 429 or 5xx | Record `signature_retry`. Retain ordinary policy and retry handling. |
| Non-cancellation construction or transport failure | Record `signature_retry_request_error`. Retain native error handling. |
| Context canceled during settings read | Close the response and return cancellation without signature events |
| Streaming recovery succeeds | Return native stream and usage results |

## 5. Good / Base / Bad Cases

Good: a rejected function-call signature becomes the dummy signature while nested business arguments retain exact integer values.
Good: a Code Assist resend keeps its project and request envelope.
Base: the default-disabled option leaves a native request on its existing error path.
Bad: recursively deleting nested business signatures or retrying every HTTP 400 changes unrelated requests.
Bad: treating a second `countTokens` signature rejection as successful local counting hides the upstream error.

## 6. Tests Required

All four business suites live directly under the plugin's flat `tests/` directory:

| Suite | Assertion points |
| --- | --- |
| [Native recovery](../../../plugins/gemini-signature-rectifier/tests/test_gemini_native_signature_rectifier_test.go) | Matcher, cleaner, four builders, counting, streaming, fresh policy, recovery guards, transient budget, Ops events, cancellation |
| [Settings service](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings_test.go) | Default false, both-switch gate, unrelated switches, read-error false |
| [Settings handler](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings_handler_test.go) | GET/PUT true and false, native envelope, sibling preservation |
| [Settings Vue](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings.test.ts) | English and Chinese labels, both Boolean saves, sibling preservation |

Use the built host executable for Chromium checks when settings UI behavior changes.
Check both locales and themes, toggle save/reload, visible labels, and browser errors.
Reuse completed checks when the candidate and inputs remain unchanged.
Spec-only changes require source and reference checks, without a product build.

## 7. Wrong vs Correct

Wrong: clean every request in the handler before upstream error policy runs.
Correct: recover only from an unmatched native signature HTTP 400 inside `ForwardNative`.

Wrong: add a recovery counter to the ordinary transient retry budget.
Correct: use one recovery flag and preserve ordinary `maxAttempts`.

Wrong: add constructor parameters or reuse another signature toggle.
Correct: read the dedicated default-false option through the existing settings service.
