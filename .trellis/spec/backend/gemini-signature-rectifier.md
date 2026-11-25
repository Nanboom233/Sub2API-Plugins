# Gemini Native Signature Rectifier

## 1. Scope / Trigger

Use this contract when changing native Gemini signature normalization, recovery, or its administrator setting.
The verified integration baseline is Sub2API v0.2.25.
Owner: [production patch](../../../plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch).

`GeminiMessagesCompatService.ForwardNative` owns normalization and recovery across four request builders:

| Builder | Existing transport |
| --- | --- |
| API Key or relay | Native Gemini endpoint |
| OAuth AI Studio | Native Gemini endpoint |
| OAuth Code Assist | `/v1internal` request envelope |
| Vertex ServiceAccount | Native Vertex endpoint |

Keep Claude `Forward`, handler pre-cleaning, and Antigravity `ForwardGemini` unchanged.
Keep exported `CleanGeminiNativeThoughtSignatures` and `estimateGeminiCountTokens` unchanged.
When enabled, normalize incompatible signatures before the first request. Retain one recovery resend after an eligible upstream rejection.

## 2. Signatures

The patch extends existing service, DTO, handler, and frontend owners:

```go
func isGeminiNativeSignatureRelatedError(body []byte) bool
func isGeminiNativeVertexTarget(account *Account, action string) bool
func replayGeminiNativeThoughtSignature(raw string, allowBareTink, allowBypass bool) string
func hasPartKey(part map[string]json.RawMessage, a, b string) bool
func sanitizeGeminiNativeThoughtSignatures(body []byte, allowBareTink, force bool) ([]byte, bool)
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

Normalization and recovery require both `settings.Enabled` and `settings.GeminiNativeSignatureEnabled`.
The native option defaults to `false`. Missing saved fields and settings read errors also yield `false`.
The Thinking Signature and API Key Signature switches do not control this native option.
Read settings through `rateLimitService.settingService`. Preserve constructors and `wire_gen.go`.

The toggle uses ID `gemini-native-signature` and hint ID `gemini-native-signature-hint`.
Keep its label, `aria-label`, and `aria-describedby` bindings.
Both locale files define `admin.settings.rectifier.geminiNativeSignature` and `geminiNativeSignatureHint`.
GET, PUT, persistence, and the form retain other rectifier settings.

### Request preparation and target envelopes

Read the gate once before request preparation. Immediately propagate `ctx.Err()` after that read.
Reuse this request-scoped value for HTTP 400 recovery.

When enabled, call `sanitizeGeminiNativeThoughtSignatures(body, isGeminiNativeVertexTarget(account, action), false)` instead of `ensureGeminiFunctionCallThoughtSignatures`.
When disabled, retain `ensureGeminiFunctionCallThoughtSignatures`. Do not add a model-prefix gate.

`isGeminiNativeVertexTarget` returns `true` for Vertex service accounts.
OAuth Code Assist requests with nonempty `project_id` return `false`, except for `countTokens`.
For other API Key or OAuth requests, parse `GetGeminiBaseURL(geminicli.AIStudioBaseURL)` and compare its lowercase hostname.
Accept `aiplatform.googleapis.com`, `aiplatform.us.rep.googleapis.com`, `aiplatform.eu.rep.googleapis.com`, and `<nonempty>-aiplatform.googleapis.com` as Vertex targets.
Other account types, parse errors, and other hosts return `false`.
Leave URL validation in the request builders to preserve error precedence.

Trim signature whitespace once in `replayGeminiNativeThoughtSignature`.
Return either bypass value only when `allowBypass` is `true`. Otherwise return an empty string for bypass values.
For other values, decode with `base64.StdEncoding`, then `base64.RawStdEncoding` if needed.
Reject empty or invalid decoded bytes. Return compatible signatures as trimmed strings without re-encoding.

| Envelope | Acceptance contract |
| --- | --- |
| `protobuf_field_2` | Use `protowire` to consume outer field 2 bytes, then inner field 1 bytes. Both fields must consume their complete input. |
| Inner field 1 payload | Require nonempty bytes. Keep the payload opaque. |
| Vertex `bare_tink` | Require `allowBareTink`, at least 21 decoded bytes, first byte `0x01`, and bytes 1 through 4 equal to `8f3d6b5f`. |

Both targets accept the complete protobuf envelope. Only Vertex targets accept the specified bare-Tink form.
The bypass values are `skip_thought_signature_validator` and `context_engineering_is_the_way_to_go`.
Set `allowBypass` only for the first call in a retained group.

### Recovery order and budget

Apply cached-content handling first, then configured error policy, then native signature recovery.
Only an unmatched HTTP 400 can enter recovery.
Match the extracted upstream error message after lowercase conversion and removal of whitespace and underscores.
The normalized message must contain `thoughtsignature`. Unrelated body fields and authentication signatures do not qualify.

Guard the HTTP 400 branch with the request-scoped gate before reading its body.
When disabled, skip the rectifier body read, close, and rewrap.
Call `sanitizeGeminiNativeThoughtSignatures(body, false, true)` and resend only when it returns `changed == true`.

Set `signatureRecoveryUsed` before the resend. Allow at most one recovery resend per `ForwardNative` call.
The resend does not consume ordinary `maxAttempts`. Existing transient retries keep their budget and use the cleaned body.

Rebuild through the selected builder so transport, headers, model mapping, and Code Assist wrapping retain native behavior.
Check error policy again for each new response.

### Shared direct-Part cleanup rules

Use `json.RawMessage` maps and arrays to preserve unrelated values and large integers.
Modify only direct `contents[].parts[]` metadata.

Proactive mode processes ordinary Parts only for missing, empty-string, or `model` roles. Null and non-string roles do not qualify.
Force mode ignores roles. Function-response cleanup applies to every role in both modes.

Preserve `toolCall`, `tool_call`, `toolResponse`, and `tool_response` Parts unchanged.
For `functionResponse` or `function_response`, remove direct signatures. In force mode, also remove Boolean `thought: true`.
These response and server-tool Parts do not change parallel-call grouping.

For other Parts, read `thoughtSignature` before `thought_signature`.
Use `hasPartKey` for paired Part aliases. Decode a signature only when its raw value exists.
Write retained signatures only as `thoughtSignature` and remove the other alias.
The dummy value is `skip_thought_signature_validator`.

| Part within the retained group | Proactive mode, `force == false` | Force mode, `force == true` |
| --- | --- | --- |
| First `functionCall` or `function_call` | Preserve a compatible real signature or either bypass value. Otherwise set the dummy value. | Set the dummy value. |
| Later parallel call | Preserve a compatible real signature. Otherwise remove direct signatures. | Remove direct signatures. |
| Other Part | Preserve a compatible real signature. Otherwise remove direct signatures. | Remove direct signatures and Boolean `thought: true`. |

Track groups within each Content using retained Parts. A retained call starts or continues the group.
A retained non-call Part ends the group unless it has Boolean `thought: true`.

Drop a modified Part only when empty or left with only `text: ""`. Dropped Parts do not change grouping.
Drop a newly emptied Content.
Return the original body with `false` for invalid input, unchanged input, or cleanup that removes all Contents.

Preserve nested function arguments, business fields, whitespace text, unmarked empty Parts, and existing empty or null part arrays.
Keep `systemInstruction` and other locations outside `contents[].parts[]` unchanged.
A second cleanup with the same mode and target returns `false` for the cleaned body.

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

After a successful transport call, check `ctx.Err()` before recording signature events or handling the response.
On cancellation, close the response body and return the context error.
Close consumed response bodies and restore buffered bodies when later handlers need them.

## 4. Validation & Error Matrix

| Condition | Outcome |
| --- | --- |
| Master switch off, native option off, or settings read failure | Existing preparation and error path. Skip native rectifier body reads and recovery. |
| Enabled option and incompatible request signature | Normalize before the first request using target envelope rules |
| Context canceled during the first gate read | Return cancellation before any upstream request |
| Context canceled when an upstream response arrives | Close the body and return cancellation without signature events |
| Cached-content rejection or configured error policy applies | Existing handling wins |
| HTTP 400 with matching message and changed body | One recovery resend |
| Different status or unrelated message | No signature recovery |
| Invalid body, unchanged body, or no remaining contents | Original body and existing error path |
| Recovery returns another signature HTTP 400 | Record `signature_retry`. Do not clean again. |
| Recovery returns 429 or 5xx | Record `signature_retry`. Retain ordinary policy and retry handling. |
| Non-cancellation construction or transport failure | Record `signature_retry_request_error`. Retain native error handling. |
| Streaming recovery succeeds | Return native stream and usage results |

## 5. Good / Base / Bad Cases

Good: a rejected first-call signature becomes the dummy signature while nested business arguments retain exact integer values.
Good: Vertex retains a compatible bare-Tink signature. A relay normalizes that same signature before its first request.
Good: removing an empty signature carrier keeps adjacent calls in one parallel group.
Good: a Code Assist resend keeps its project and request envelope.

Base: the default-disabled option leaves a native request on its existing error path.
Bad: recursively deleting nested business signatures or retrying every HTTP 400 changes unrelated requests.
Bad: treating a second `countTokens` signature rejection as successful local counting hides the upstream error.

## 6. Tests Required

All four business suites live directly under the plugin's flat `tests/` directory:

| Suite | Assertion points |
| --- | --- |
| [Native recovery](../../../plugins/gemini-signature-rectifier/tests/test_gemini_native_signature_rectifier_test.go) | Matcher, target envelopes, shared walker, grouping, Part boundaries, preflight, builders, counting, streaming, policy, budgets, events, cancellation |
| [Settings service](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings_test.go) | Default false, missing field, both-switch gate, unrelated switches, read-error false |
| [Settings handler](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings_handler_test.go) | GET/PUT true and false, native envelope, sibling preservation |
| [Settings Vue](../../../plugins/gemini-signature-rectifier/tests/test_rectifier_settings.test.ts) | English and Chinese labels, both Boolean saves, sibling preservation |

Cover both bypass values, Vertex host boundaries, invalid roles, function responses, server tools, and deleted-carrier regrouping.
Check exact large integers, all-Contents rollback, idempotence, disabled behavior, and cancellation at the single gate read.

Use the built host executable for Chromium checks when settings UI behavior changes.
Check both locales and themes, toggle save/reload, visible labels, and browser errors.
Reuse completed checks when the candidate and inputs remain unchanged.
Spec-only changes require source and reference checks, without a product build.

## 7. Wrong vs Correct

Wrong: recursively replace every signature in the handler or add a separate response parser for normalization.
Correct: normalize direct Part metadata inside `ForwardNative` before sending. Reuse the walker for policy-permitted HTTP 400 recovery.

Wrong: add a recovery counter to the ordinary transient retry budget.
Correct: use one recovery flag and preserve ordinary `maxAttempts`.

Wrong: add constructor parameters or reuse another signature toggle.
Correct: read the dedicated default-false option through the existing settings service.
