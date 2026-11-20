# Native Gemini signature recovery design

Planning is complete. User approval to start Phase 2 with `task.py start` remains required.
Baseline: Sub2API `v0.2.23`. Requirements: [prd.md](prd.md). Evidence: [research supplement](research/count-tokens-and-settings.md).

## Boundaries

Plugin: `plugins/gemini-signature-rectifier`. Production patch: `patches/gemini-signature-rectifier.patch`.

| Upstream file | Change |
| --- | --- |
| `backend/internal/service/gemini_messages_compat_service.go` | Add recovery only inside `ForwardNative`. |
| `backend/internal/service/gemini_native_signature_cleaner.go` | Add private matcher and cleaner. Preserve exported functions. |
| `backend/internal/service/settings_view.go` | Add persisted bool, default false. |
| `backend/internal/service/setting_features.go` | Add the dedicated gate. Leave `GetRectifierSettings` unchanged. |
| `backend/internal/handler/dto/settings.go` | Add response bool. |
| `backend/internal/handler/admin/setting_handler_runtime.go` | Add plain-bool request field and both response projections. |
| `frontend/src/api/admin/settings.ts` | Extend `RectifierSettings` with a required boolean. |
| `frontend/src/views/admin/SettingsView.vue` | Add native toggle, false form default, and explicit save field. |
| `frontend/src/i18n/locales/en/admin/settings.ts` | Add the locked label and hint. |
| `frontend/src/i18n/locales/zh/admin/settings.ts` | Add matching keys. |

Read the gate through existing `rateLimitService.settingService`. Keep constructors, providers, and `wire_gen.go` unchanged.
Use `s.rateLimitService != nil && s.rateLimitService.settingService != nil` before that access.
Preserve Claude-compatible `Forward`, handler pre-cleaning, Antigravity, and normal signature injection.

## Private matcher and cleaner

The tagged `isGeminiSignatureRelatedError` matches generic signature text. Leave it unchanged.
The new `isGeminiNativeSignatureRelatedError([]byte) bool` uses existing `extractUpstreamErrorMessage`.
Lowercase the extracted message and remove underscores and whitespace. Match `thoughtsignature`.
This covers `thoughtSignature`, `thought_signature`, and `thought signature`. The caller enforces HTTP 400.
Verified helper locations appear in [source evidence](research/count-tokens-and-settings.md#verified-matcher-and-ops-sources).

Add `cleanGeminiNativeThoughtSignaturesForRetry([]byte) ([]byte, bool)` beside the matcher.
Use `json.RawMessage` for untouched values. Preserve nested business JSON, numbers, and array order.
Invalid JSON or failed serialization returns the original body and false.
Apply only these rules to direct `contents[].parts[]`:

1. If a Part has `functionCall` or `function_call`, set `thoughtSignature` to `geminiDummyThoughtSignature` and delete `thought_signature`.
   An existing canonical sentinel without `thought_signature` causes no change. Preserve all other fields, including either function-call key.
2. For other Parts with either signature field or `thought: true`, delete both signature fields. Remove `thought` only when true.
   Drop the Part only if no keys remain or its sole remaining key is `text: ""`. Keep all other fields unchanged.
3. Drop a content when its Parts array becomes empty. Preserve other content fields and remaining order.
4. If no contents remain or no actual cleanup change occurred, return the original body and false.

Parts outside these rules remain unchanged. Serialization whitespace and key order do not count as cleanup changes.

## ForwardNative response loop

Use the existing response loop and request builders at `gemini_messages_compat_service.go:1142–1660`.
Track `signatureRecoveryUsed` per invocation and `isSignatureRetryAttempt` for the added resend only.

1. Apply `cachedContentPassthroughInLoop`, then `checkErrorPolicyInLoop`.
2. Preserve existing handling when policy is non-`None`.
3. For an unmatched signature HTTP 400, require an unused recovery and the dedicated setting gate.
4. Clean the captured native body. If unchanged, use existing final handling.
5. Check parent cancellation. Record `signature_error`, close the consumed response, and replace the captured body.
6. Set both recovery flags. Decrement `attempt` before `continue`, so the loop increment preserves the ordinary retry budget.
7. Rebuild through the existing account-specific closure and use the native transport path.
8. Handle the resend outcome, then immediately clear `isSignatureRetryAttempt`.
9. Clear the prior `checkedPolicy` result. Process the new response through cached-content and fresh policy checks.

The recovery guard bounds sends at ordinary `maxAttempts + 1`, including recovery on the last ordinary attempt.
All four builders use the changed body. Code Assist rebuilds its `request` envelope and retains stream aggregation.
Keep native URL, authentication, proxy, model mapping, cached-region, cancellation, transport, and final-error behavior.
Use native bounded error reads. Reconstruct consumed error bodies when later processing needs them.
Ordinary transient retries reuse the cleaned body and retain their existing budget and backoff.
Recovery occurs before client response streaming starts.

### Ops events

Use `appendOpsUpstreamError`, native sanitization, detail limits, account/proxy attribution, status, and each response's request ID.
Never log request bodies, full signatures, or credentials.
All three kinds exist in [antigravity_gateway_gemini.go:251–333](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/antigravity_gateway_gemini.go#L251).

| Kind | New native recovery use |
| --- | --- |
| `signature_error` | Cleanup changed the body and recovery proceeds. |
| `signature_retry` | The signature resend returns HTTP status >=400. |
| `signature_retry_request_error` | Request construction or transport fails during the signature resend. |

Unchanged cleanup and successful resends emit no signature error event. Preserve native cancellation logging rules.
Consume the attempt flag immediately after the resend outcome. Later ordinary attempts use `retry` events.

### Counting

Apply locked Option B through the same loop. Recovery success returns upstream `totalTokens`.
A repeated 400 follows the native error path without a new estimate. Leave existing estimator branches unchanged.

## Settings and UI contract

Use `GeminiNativeSignatureEnabled bool`, JSON `gemini_native_signature_enabled`, in persisted settings, response DTO, and `UpdateRectifierSettingsRequest`.
The default is false, matching `apikey_signature_enabled`. Keep `GetRectifierSettings` unchanged.
Add `SettingService.IsGeminiNativeSignatureRectifierEnabled(ctx) bool` beside the existing gates.
Return `settings.Enabled && settings.GeminiNativeSignatureEnabled`. Return false on a settings read error.
Read this gate only for eligible recovery. Existing thinking and API Key switches remain independent.

Add the new bool to existing GET/PUT projections and the existing PUT assignment.
Use the existing plain-bool update flow and validation without a preliminary settings read.
The Vue form starts false, loads through existing `Object.assign`, and includes the bool in its explicit save payload.

Insert the row after thinking signature and before thinking budget in the existing master-controlled group.
Use the existing Toggle and Save owner. Preserve the [tagged markup](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/views/admin/SettingsView.vue#L554):

| Element | Native contract |
| --- | --- |
| Card/body | Existing `div.card`, header, loading state, master row, Save button, and `space-y-5 p-6` body |
| Sub-option group | `v-if`, `space-y-4 border-t border-gray-100 pt-4 dark:border-dark-700` |
| Row | `div.flex.items-center.justify-between`, one text `div`, then Toggle |
| Label | `text-sm font-medium text-gray-700 dark:text-gray-300` |
| Hint | `text-xs text-gray-500 dark:text-gray-400` |
| Toggle | Native `h-6 w-11 flex-shrink-0` button, `h-5 w-5` thumb, focus/dark variants, `role="switch"`, and `aria-checked` |

Set label `for` and Toggle `id` to `gemini-native-signature`. Add the translated `aria-label`.
Set hint `id` and Toggle `aria-describedby` to `gemini-native-signature-hint`. Add no visible wrappers or controls.

| Key under `admin.settings.rectifier` | en | zh |
| --- | --- | --- |
| `geminiNativeSignature` | Gemini Native Signature Rectifier | Gemini 原生签名整流 |
| `geminiNativeSignatureHint` | Fix rejected thought signatures and retry native Gemini requests once. Configured error policies take priority. | 原生 Gemini 请求遇到思考签名错误时，修正后重试一次。已配置的错误策略优先。 |

## Plugin delivery

Copy the complete `sub2api-plugin-template` kit after implementation approval. Keep its standalone build script, installer, workflow, and common tests.
Use unmodified LGPLv3 text in root `LICENSE`. Retain inherited notices and required license texts under `licenses/`.
Keep usage instructions in the Chinese README and suites flat under `tests/`. Add no nested Trellis or separate build framework.
Annotate service suites with `// sub2api-package: backend/internal/service` and the handler suite with `// sub2api-package: backend/internal/handler/admin`.
Use flat `tests/test_*.test.ts` Vue suites. Unmount wrappers in `finally`.
Parent submodule discovery owns combined builds. The [target inventory](research/count-tokens-and-settings.md#patch-conflict-inventory) found no overlap with current plugin patches.
The final standalone and combined builds establish actual patch composition.
Disable the sub-option to stop recovery. Restore the prior program through the existing installer for binary rollback.

## Phase 2.2 browser check

Reuse [planning preview evidence](/tmp/gemini-rectifier-ui-preview/preview-results.md) for the locked copy and layout.
Check the final patch in Playwright Chromium with synthetic API data at 1440×900, scale 2, in en/zh and light/dark.
Inspect the full card for readable text, complete icons, sibling geometry, zero overflow, and zero console/page errors.
Verify initial false, enable/save true/reload, disable/save false/reload, sibling preservation, and master-off hiding.
Stop temporary server/browser processes and remove runtime files. Retain screenshots and results.
The existing 2026-11-20 preview verified layout, false PUT, and master-off hiding with synthetic saved true.
