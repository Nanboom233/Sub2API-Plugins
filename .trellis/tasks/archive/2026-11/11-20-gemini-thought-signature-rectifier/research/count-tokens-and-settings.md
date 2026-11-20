# Native Gemini counting and settings

Date: 2026-11-20. Baseline: `Wei-Shaw/sub2api@v0.2.23`.
Stage: research and planning supplement. No product code or provider calls ran.
Planning is complete. Only user approval to start Phase 2 implementation with `task.py start` remains.

The active design follows [plan-debloat.md](../plan-debloat.md).
It supersedes earlier compatibility recommendations and the shared-toggle recommendation in [existing-work.md](existing-work.md).

## Locked countTokens policy: B

Use one signature recovery attempt for `countTokens`.
Return the upstream count on success.
Preserve the actual error after a second 400.
Keep the existing transport, transient-status, and OAuth-scope estimates.
This choice repairs rejected history without expanding silent text-only estimates to permanent request errors.
The user locked Item 5 to Option B in [plan-finalize-and-preview.md](../plan-finalize-and-preview.md).

### Account builders and action handling

All ranges below refer to [gemini_messages_compat_service.go][native].

| Lines | Existing behavior |
| --- | --- |
| 1111–1114 | Removes contents with empty parts arrays. Does not remove empty Part objects. |
| 1116–1125 | Accepts generation, streaming generation, and `countTokens`. Injects missing camelCase function-call signatures. |
| 1128–1129 | Maps API Key and ServiceAccount model names. |
| 1131 | Excludes `countTokens` from the image-generation permission gate. |
| 1142–1147 | Project-based OAuth can force upstream streaming for generation. `forceAIStudio := action == "countTokens"`. |
| 1155–1181 | API Key uses the configured AI Studio-compatible base URL, action, native body, and `x-goog-api-key`. Relay URLs use this builder. |
| 1183–1249 | OAuth without a project uses direct AI Studio with Bearer authentication. |
| 1193–1227 | Project-based OAuth generation uses the `/v1internal` envelope. The builder wraps the current body under `request`. |
| 1228–1249 | Project-based OAuth `countTokens` also uses direct AI Studio. It does not call Code Assist countTokens. |
| 1252–1269 | ServiceAccount uses Vertex URL construction and `setVertexGeminiAuth`. Cached-content region selection remains active. |
| 1279–1280 | Ordinary attempt limit equals configured same-account retries plus one. |

The four account builders share one native loop.
Recovery must update its captured native body before the next builder call.
The Code Assist builder must then create a new envelope.
It must not reuse the first serialized envelope. [native:1155–1282]

### Existing estimates and exceptions

| Trigger | Exact tagged behavior |
| --- | --- |
| Local request setup failure | Lines 1282–1294 return cancellation, Vertex lookup failover, a local 400, or a local 502. No counting estimate. |
| Transport error | Lines 1298–1316 call the Gemini transport handler. Only `*UpstreamFailoverError` permits the estimate. |
| Client cancellation or parent deadline | The transport helper returns the original error. No estimate or new signature attempt. [transport:27–55] |
| Transient HTTP error | Lines 1336–1403 retry eligible statuses. An exhausted counting request returns an estimate. |
| Eligible statuses | Lines 1691–1708 include 429, 500, 502, 503, 504, and 529. Code Assist OAuth also permits 403. Never 400. |
| OAuth insufficient scope | Lines 1339–1346 exclude scope errors from transient retry. Lines 1429–1444 return an estimate for OAuth counting requests. |
| Ordinary HTTP 400 | No estimate. Final policy and Google error handling apply. |
| Cached-content errors | Lines 1319–1326 and 1419–1428 preserve explicit-cache exceptions before ordinary processing. |
| Configured error policy | Lines 1328–1334 stop retries on any non-`None` result. Final handling reuses that result. |

The scope predicate checks `Www-Authenticate: insufficient_scope` and two body phrases.
Those phrases are `insufficient authentication scopes` and `access_token_scope_insufficient`. [native:2741–2746]
The final scope fallback has no explicit HTTP-403 condition.
It applies to an OAuth error response with the predicate above. [native:1419–1444]

The scope-fallback comment says it precedes error policy.
The loop can already have evaluated policy and changed account state.
Thus, the comment does not describe the complete order. [native:1328–1334,1429–1449]
Keep this existing scope exception outside this feature's changes.
Signature recovery must never override a policy-selected response.

The Gemini transport helper records ordinary non-canceled failures and can temporarily remove an account from scheduling.
It then returns a Google-format 502 failover error.
The counting fallback can return HTTP 200 after those side effects. [transport:27–55]

### Exact local estimator

`estimateGeminiCountTokens` reads only these paths:

- `systemInstruction.parts[].text`
- `contents[].parts[].text`

For each text value, it trims outer whitespace and counts Unicode runes.
Let `n` be that count and `a` the number of runes at or below `0x7f`.
Empty text contributes zero.
If `a / n >= 0.8`, the contribution is integer `(n + 3) / 4`, or `ceil(n / 4)`.
Otherwise, the contribution is `n`.
The function sums contributions per Part and clamps a negative final total to zero. [native:2768–2817]

| Input | Local contribution |
| --- | --- |
| `text: "hello"` | 2 |
| `text: "你好世界"` | 4 |
| `text: "abcd中"` | 2, because the ASCII ratio is exactly 0.8 |
| `text: "abc中文"` | 5 |
| Two Parts containing `"a"` and `"b"` | 2. A single Part containing `"ab"` contributes 1. |
| `text: "  \n "` | 0 |
| `thought: true` with nonempty text | Counts the text. The estimator ignores the thought flag. |
| Large `inlineData.data` base64 image | 0, regardless of encoded size |
| `fileData`, audio, or video | 0 |
| `thoughtSignature` or `thought_signature` | 0, regardless of signature length |
| Function-call arguments or function-response JSON | 0 |
| Base64 or a signature copied into `.text` | Counts as ordinary text |
| `system_instruction`, tools, schema, roles, or opaque cached history | 0 |

This is a text heuristic, not the model tokenizer.
The encoded image size cannot supply the missing image-token count.
The function also omits formatting overhead and rounds each Part separately.

All three existing fallback branches return HTTP 200 with `{"totalTokens": estimated}`.
They return zero `ClaudeUsage`, `Stream: false`, model identifiers, and elapsed duration.
They do not mark the response as an estimate or copy `estimated` into `Usage.InputTokens`.
The scope branch retains upstream headers and request ID.
The transport and exhausted-transient branches do not. [native:1303–1314,1383–1394,1432–1444]

### Usage and billing

The native handler checks billing eligibility and reserves inflight capacity for counting requests too.
After success, it submits `RecordUsage` without an action-specific counting bypass. [handler:439–451,815–853]
Successful upstream counting responses use the normal nonstream response path.
That path extracts `usageMetadata`, when present.
A `totalTokens` value alone does not populate the normal usage fields. [native:2826–2871]

Zero usage normally gives zero token-based cost.
It does **not** guarantee zero charge under every configured tariff.
`calculateTokenCost` calls `CalculateTokenCostForRequest` even for zero usage. [billing:1029–1101,1288–1322]
That service can select unified pricing and sets `RequestCount: 1`. [token-cost:29–61]
Unified per-request pricing computes `unitPrice * units`, with one unit when no usage units exist. [prices:1721–1769,2027–2059]
Thus, a configured per-request tariff can charge a successful local estimate.
Simple mode skips normal billing unless its key-rate-limit-only billing option applies. [billing:862–867]
No billing change belongs in this plugin.

### Item 5 comparison

All options must preserve cached-content exceptions, cancellation, and configured policy precedence.
An unchanged or unusable cleanup result must not trigger a resend.

| Option | After signature 400 | After successful retry | After failed retry | Benefit and cost |
| --- | --- | --- | --- | --- |
| A | Clean and retry once | Return upstream count | Estimate on unmatched 400/5xx/transport, following PR #1309's continuity goal | More preflights continue. A permanent 400 becomes an unmarked, potentially low count. |
| **B, locked** | Clean and retry once | Return upstream count | Preserve actual error, except existing transport/transient/scope estimates | Repairs countable history and preserves request errors. Some preflights still stop. |
| C1 | No signature retry | Not applicable | Return baseline 400 | Smallest change. Leaves a recoverable counting failure unresolved. |
| C2 | No signature retry | Not applicable | Estimate directly | Avoids another call. Never obtains the corrected upstream count. |

Under B, a retry that receives 503 follows the existing transient budget and can ultimately estimate.
A retry transport failure already qualifies for an existing estimate unless cancellation prevents it.
Thus, A mainly expands behavior for a second 400 and non-transient failures outside existing fallback rules.
Neither option can repair opaque cached history through inline cleanup.
The selected design adds no estimation branch.

AstrBot's public empty-Part report covers v4.29.3.
Its associated PR remains open.
The current task reports a separate live v4.29.4 signature failure. [ecosystem]

Gemini CLI issue #5500 reports a CountTokens structural failure. [ecosystem]
The focused implementation checks cover recovered upstream `totalTokens` and a repeated 400 without estimation.
The estimator and existing fallback branches remain outside the change and its new tests.

## Verified matcher and Ops sources

The tagged [isGeminiSignatureRelatedError:1088–1094][native-matcher] uses `extractAntigravityErrorMessage`, then raw response text when extraction is empty.
Its final condition matches `thought_signature` or generic `signature`.
[extractAntigravityErrorMessage:539–557][antigravity-message] reads `error.message` and top-level `message`.
[extractUpstreamErrorMessage:294–313][upstream-message] reads `error.message`, including nested JSON strings, then `detail` or top-level `message`.
The new native matcher reuses `extractUpstreamErrorMessage` and matches only normalized `thoughtsignature`. It adds no raw-body fallback or rejection-verb list.

[antigravity_gateway_gemini.go][ops-signature] contains `signature_error` at line 251, `signature_retry` at 298, and `signature_retry_request_error` at 333.
Its HTTP retry event occurs only for status >=400 at lines 279–301.
The tagged `gateway_service.go` contains none of these event literals. Its forwarding code uses `signature_error` in `gateway_forward.go:470`.
All three selected kinds already exist in the tagged Antigravity path.

## Dedicated setting

### Tagged contract

| Source | Existing contract |
| --- | --- |
| [settings_view.go:525–539][schema] | Persisted bool fields plus a string-pattern list. First three bools default true. API Key signature default is false. |
| [setting_features.go:871–921][settings] | Existing getter and thinking gates remain unchanged. |
| [gateway_upstream_response.go:113–118][apikey-gate] | The API Key signature branch returns false on settings read errors or disabled master/sub-option. |
| [domain_constants.go:596–600][keys] | Existing key: `rectifier_settings`. No new database key or table is required. |
| [dto/settings.go:496–503][dto] | Separate response DTO repeats the settings fields. |
| [setting_handler_runtime.go:284–374][admin] | GET and PUT each project DTO fields explicitly. PUT uses nonpointer bool fields and replaces the settings object. |
| [admin.go:608–609][routes] | Existing GET/PUT routes require no changes. Frontend API prefix adds `/api/v1`. |

Use `GeminiNativeSignatureEnabled bool`, JSON `gemini_native_signature_enabled`, with default false, matching `apikey_signature_enabled`.
Keep `GetRectifierSettings` unchanged. The standard bool zero value needs no parsing adaptation.

The runtime gate is `enabled && gemini_native_signature_enabled`.
It is independent of `thinking_signature_enabled` and `apikey_signature_enabled`.
Return false on runtime settings read failure.
The tagged API Key branch returns false when its settings read fails or either required switch is false. [apikey-gate:113–118]
That branch lives in `gateway_upstream_response.go`, not a method named `IsAPIKeySignatureRectifierEnabled` in `setting_features.go`.
`GetRectifierSettings` propagates non-not-found repository errors. [settings:873–878]
The new gate follows the API Key branch's fail-closed rule. Existing thinking gates retain their fail-open behavior. [settings:906–921]
Use a plain bool in `UpdateRectifierSettingsRequest`, persisted settings, and GET/PUT response DTOs.
Assign the request value through the existing update flow without a preliminary settings read.
Keep existing validation and error handling. Focus new tests on default false, the dedicated gate, and true/false GET/PUT round-trips.

### Frontend contract

| File | Exact touchpoint |
| --- | --- |
| [api/admin/settings.ts:1452–1483][api] | Add a required boolean to `RectifierSettings`. Existing GET/PUT functions remain the entry points. |
| [SettingsView.vue:592–631][view] | Add the native Gemini sub-option beside the thinking signature option, under the master-controlled group. |
| [SettingsView.vue:9216–9225][view] | Add `gemini_native_signature_enabled: false` to `rectifierForm`. |
| [SettingsView.vue:12287–12325][view] | Existing load uses `Object.assign`. Save explicitly lists fields and must include the new bool. |
| [en/admin/settings.ts:1139–1158][en] | Add `geminiNativeSignature` and `geminiNativeSignatureHint` under `settings.rectifier`. |
| [zh/admin/settings.ts:1133–1152][zh] | Add the same keys. Full paths start with `admin.settings.rectifier`. |

The [locale test:63–89][locale-test] checks identical en/zh leaf keys, nonempty messages, and static production key references.
The existing locale aggregators already load these modules.
No new locale module or aggregator change is required.
The [package scripts:6–11][package] run `check:i18n` followed by `vue-tsc -b` and `vite build`.
The [TypeScript configuration:12,23–25][tsconfig] already sets `noEmit: true`.
Keep the exact en/zh copy and layout verified in the planning screenshots.
The preview used synthetic saved true and verified a false PUT plus master-off hiding.
During Phase 2, test initial false, enable/save true/reload, then disable/save false/reload, with sibling values preserved.
The existing visual evidence remains valid. This document update requires no frontend build or browser rerun.

### Settings dependency without constructor churn

`ForwardNative` already holds `rateLimitService`.
`RateLimitService` already holds `settingService`. [rate:22–31]
`ProvideRateLimitService` assigns that dependency before the Gemini constructor runs. [providers:504–526, wire:129,173]
Read the dedicated gate through this existing same-package dependency.
Guard that access with `s.rateLimitService != nil && s.rateLimitService.settingService != nil`.
This avoids constructor changes, a new provider, and generated wiring changes.
Existing handler tests call the nine-argument constructor. [constructor-test:68]
The implementation must preserve those calls.

## Patch-conflict inventory

Inspected plugin heads:

- `codex-candy-eval`: `6fc5b1fbd94359e2dde3dea86aa79452f9b8dc25`.
- `sub2api-quota-extension`: `f9ba14b95870d253c34b135ea434a7642fc2bdab`.

The inventory compares every proposed upstream target with each plugin's `diff --git` headers.

| Proposed upstream target | Eval overlap | Quota overlap |
| --- | --- | --- |
| `backend/internal/service/gemini_messages_compat_service.go` | None | None |
| `backend/internal/service/gemini_native_signature_cleaner.go` | None | None |
| `backend/internal/service/settings_view.go` | None | None |
| `backend/internal/service/setting_features.go` | None | None |
| `backend/internal/handler/dto/settings.go` | None | None |
| `backend/internal/handler/admin/setting_handler_runtime.go` | None | None |
| `frontend/src/api/admin/settings.ts` | None | None |
| `frontend/src/views/admin/SettingsView.vue` | None | None |
| `frontend/src/i18n/locales/en/admin/settings.ts` | None | None |
| `frontend/src/i18n/locales/zh/admin/settings.ts` | None | None |

No current production patch targets these ten files.
The selected design leaves `backend/cmd/server/wire_gen.go` unchanged.
The earlier injection proposal would have changed its line 173.
Quota changes `ProvideAccountUsageService` near line 211, with hunk context at lines 208–214.
Those hunks do not overlap. See local `plugins/sub2api-quota-extension/patches/quota-extension.patch:1–12`.
Existing routes, provider wiring, the Gemini v1beta handler, and Antigravity remain unchanged.

This establishes zero target overlap for the selected production files at these heads.
It is not a successful candidate patch-application test.
No candidate patch exists yet.
The future combined build must establish actual composition through `git apply --binary`.
Local `scripts/build.py:54–80,184–189,213–231` owns that check.
Flat test discovery and staging live in `tests/support.py:10–67`.

## Primary-source links

The linked source files use the fixed `v0.2.23` tag.
The ranges beside each claim identify its exact source lines.

[native]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gemini_messages_compat_service.go
[native-matcher]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gemini_messages_compat_service.go#L1088
[antigravity-message]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/antigravity_gateway_claude.go#L539
[upstream-message]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gateway_upstream_response.go#L294
[ops-signature]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/antigravity_gateway_gemini.go#L251
[transport]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gemini_upstream_transport_error.go#L27
[handler]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/gemini_v1beta_handler.go#L439
[billing]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gateway_usage_billing.go#L660
[token-cost]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/billing_token_cost_request.go#L29
[prices]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/billing_service.go#L1721
[schema]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/settings_view.go#L525
[settings]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/setting_features.go#L871
[apikey-gate]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gateway_upstream_response.go#L113
[keys]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/domain_constants.go#L596
[dto]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/dto/settings.go#L496
[admin]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/admin/setting_handler_runtime.go#L284
[routes]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/server/routes/admin.go#L608
[partial-tests]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/admin/setting_handler_partial_payload_test.go#L13
[api]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/api/admin/settings.ts#L1452
[view]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/views/admin/SettingsView.vue#L592
[en]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/i18n/locales/en/admin/settings.ts#L1139
[zh]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/i18n/locales/zh/admin/settings.ts#L1133
[locale-test]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/i18n/__tests__/localeKeyCompleteness.spec.ts#L63
[package]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/package.json#L6
[tsconfig]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/tsconfig.json#L12
[rate]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/ratelimit_service.go#L22
[providers]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/wire.go#L504
[wire]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/cmd/server/wire_gen.go#L129
[constructor-test]: https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/gemini_client_cancel_test.go#L68
[ecosystem]: existing-work.md#evidence-index
