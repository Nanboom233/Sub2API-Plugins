# Gemini native thought signature research

Research date: 2026-11-20. Stage: Phase 1.2. Coordinator: `t53`.

## Verdict

Sub2API `v0.2.23` lacks a signature-specific 400 retry in `GeminiMessagesCompatService.ForwardNative`.
Related upstream work already exists. PR [#1309](https://github.com/Wei-Shaw/sub2api/pull/1309) proposes this retry but remains open and unmerged.
The tag already includes a shared native cleaner, missing-function-call signature injection, handler pre-cleaning, and Antigravity native recovery. [S1–S4]

No existing local plugin patch implements this recovery in the inspected branches and history.
Prefer an independent plugin that adds one signature recovery stage to `ForwardNative` and reuses the existing rectifier setting.
Adapt the approach from #1309. Its old retry loop and recursive cleaner need changes for the current baseline. [L1, S1, S4]

## Upstream status and history

Public GitHub REST reads confirmed these states. Issue numbers #935 and #2380 do not identify pull requests.

| Work | Confirmed state | Meaning for this task |
| --- | --- | --- |
| [PR #1309](https://github.com/Wei-Shaw/sub2api/pull/1309) | Open. `merged=false`, `merged_at=null`. Head `36789928fd1732b707833ea9abb0692df02b4e29`. | Adds native retry, setting injection, Ops events, and countTokens fallback. No merged replacement appeared in the inspected native code. |
| [Issue #935](https://github.com/Wei-Shaw/sub2api/issues/935) | Closed on 2026-03-12. | Reports Antigravity native `Corrupted thought signature.` failures. |
| [PR #946](https://github.com/Wei-Shaw/sub2api/pull/946) | Merged on 2026-03-12. API merge commit `826090e0996761f69ef035a0ef70676c5104f7ac`. | Implements Antigravity native signature recovery. The tagged implementation remains present. |
| [PR #459](https://github.com/Wei-Shaw/sub2api/pull/459) | Merged. API merge commit `16f150caae5b2db169fb6c17abcbfa9e7ceff653`. | Adds missing `functionCall` signature injection to `Forward` and `ForwardNative`. |
| [PR #476](https://github.com/Wei-Shaw/sub2api/pull/476) | Merged. API merge commit `cb58daf38d211a4359e6133583a3ac1712b54b7d`. | Changes native cleaning from deletion to dummy replacement. Exports `DummyThoughtSignature`. |
| [Issue #2380](https://github.com/Wei-Shaw/sub2api/issues/2380) | Open. | Requests default API Key rectification for Anthropic thinking blocks. It does not fix Gemini native forwarding. |
| [PR #8822](https://github.com/Wei-Shaw/sub2api/pull/8822) | Merged on 2026-11-16. Commit `04503e001e3d5ac3c156b8293accbebc31afeb17`. | Improves native sticky-session hashes. It reduces account switching but adds no reactive native rectifier. |
| [PR #8316](https://github.com/Wei-Shaw/sub2api/pull/8316), [PR #8545](https://github.com/Wei-Shaw/sub2api/pull/8545), [PR #8925](https://github.com/Wei-Shaw/sub2api/pull/8925) | All open and unmerged. | Preserve Gemini signatures through Responses/Chat or improve Antigravity behavior. They do not close the native retry gap. |

The latest published release was [v0.2.23](https://github.com/Wei-Shaw/sub2api/releases/tag/v0.2.23), published on 2026-11-18.
Its commit is `5af9afb588c4b014b3df9db7d4073af1f8ae01b6`.
Current `main` is `2af3f1e15c98c893a89255a037f551046883b8c0`.
The [tag-to-main comparison](https://github.com/Wei-Shaw/sub2api/compare/v0.2.23...2af3f1e15c98c893a89255a037f551046883b8c0) contains one VERSION-only commit.
Thus, no post-tag production change currently resolves this gap.

Public issue searches covered `thought signature`, `thoughtSignature`, and `Gemini rectifier` in `Wei-Shaw/sub2api`.
The results establish the related work above. They cannot establish the absence of private or unindexed work.

## Forwarding behavior in v0.2.23

All source line numbers below refer to the tag unless a PR head is explicit.

| Path or helper | Confirmed behavior |
| --- | --- |
| `GeminiMessagesCompatService.Forward`, `gemini_messages_compat_service.go:533,720–819` | Converts Claude Messages to Gemini. On signature-related 400s, it permits two downgrade stages outside the ordinary retry budget. Stage one filters thinking. Stage two also downgrades tool history. This branch does not consult `SettingService`. [S1] |
| `ForwardNative`, same file `:1096–1406` | Filters empty parts arrays and injects missing camelCase function-call signatures. It has ordinary retries but no signature-specific 400 recovery. [S1] |
| API Key, `:1155–1181` | Sends the native body to the configured AI Studio-compatible URL with `x-goog-api-key`. This includes relay base URLs. [S1] |
| OAuth AI Studio, `:1183–1249` | Without `project_id`, sends the native body with Bearer authentication. [S1] |
| OAuth Code Assist, `:1142–1147,1193–1227` | With `project_id`, wraps the body under `request` for `/v1internal`. Non-stream generation uses upstream streaming and aggregation. `countTokens` instead forces AI Studio. [S1] |
| Vertex ServiceAccount, `:1252–1269` | Builds a Vertex URL and authenticates through `setVertexGeminiAuth`. The request builder captures the native body. [S1] |
| Handler, `gemini_v1beta_handler.go:642–660,754–766` | Cleans signatures after a bound-account switch or a missing binding with camelCase signatures. Then dispatches to Antigravity or `ForwardNative`. This pre-cleaning does not read the rectifier toggle. [S3] |
| `AntigravityGatewayService.ForwardGemini`, `antigravity_gateway_gemini.go:230–341` | On signature-related 400s, checks the existing setting and camelCase signature presence. Cleans once, then invokes `antigravityRetryLoop`. Preserves failover signals and records signature events. [S2] |
| Antigravity `countTokens`, same file `:71–84` | Returns HTTP 200 with `totalTokens: 0` locally. It does not contact an upstream. [S2] |

`CleanGeminiNativeThoughtSignatures` exists in `backend/internal/service/gemini_native_signature_cleaner.go:21–75`.
It recursively replaces every `thoughtSignature` key with the dummy value.
It ignores `thought_signature`, preserves `thought: true`, and does not inspect Part data or remove empty Parts.
Its recursion also reaches arbitrary nested JSON, including tool arguments with matching key names. [S4]

`ensureGeminiFunctionCallThoughtSignatures`, `gemini_messages_compat_service.go:3340–3390`, handles camelCase `functionCall` and `thoughtSignature` only.
It fills absent or blank signatures. It preserves nonempty invalid signatures. [S1]

`FilterThinkingBlocksForRetry` and `FilterSignatureSensitiveBlocksForRetry` exist in `backend/internal/service/gateway_request.go:767,1302`.
They process Anthropic `messages` and apply protocol-family guards. They are unsuitable for native Gemini `contents` directly. [S5]
The recursive upstream tree lists no separate rectifier package. Settings and filters live in the service package.

### Existing setting and admin exposure

The database key is `rectifier_settings`, defined in `backend/internal/service/domain_constants.go:596–600`.
The schema uses `enabled`, `thinking_signature_enabled`, `thinking_budget_enabled`, `apikey_signature_enabled`, and `apikey_signature_patterns`.
There is no separate `signature_rectifier_enabled` field in this schema. [S6]

`DefaultRectifierSettings` sets the first three booleans to true.
`apikey_signature_enabled` defaults to false through its omitted Go field.
`IsSignatureRectifierEnabled` returns `enabled && thinking_signature_enabled`. A settings read error returns true.
Missing, empty, or malformed settings use defaults. Valid JSON with omitted fields retains Go zero values. [S6]

Admin GET/PUT `/api/v1/admin/settings/rectifier` already exist.
The settings page exposes the master, thinking signature, budget, and API Key controls. [S7]
Prefer the existing thinking-signature gate for native Gemini, matching Antigravity and #1309.
Using `apikey_signature_enabled` would introduce a different default and conflate this task with issue #2380.

## Local repository and conflict findings

Local inspection used `rg`, `git log --all`, `git branch -a`, and submodule histories. No authenticated GitHub or Git read occurred.
The parent HEAD was `f9e3019`. Available feature branches cover quota and build inspection.
No inspected branch or patch history contained a Gemini native thought-signature rectifier.
This finding covers locally available refs, including origin tracking refs. No fetch changed their state.

| Local owner | Inspected commit and findings |
| --- | --- |
| `plugins/codex-candy-eval` | `6fc5b1fbd94359e2dde3dea86aa79452f9b8dc25`. Seven patches. No patch targets the native Gemini service, cleaner, or Antigravity gateway files. |
| `plugins/sub2api-quota-extension` | `f9ba14b95870d253c34b135ea434a7642fc2bdab`. One quota patch. It modifies `wire_gen.go`, but its hunk changes `ProvideAccountUsageService`, not the Gemini constructor. |
| `plugins/sub2api-plugin-template` | `9bcc921bc055072950166dc5babdcc90ca1de91e`. No top-level patch files. The combined build skips it. |

The submodule inventory is `.gitmodules:1–9`.
Build discovery sorts plugin paths and selects initialized modules with top-level patches.
Patch application sorts each plugin's patch names and uses `git apply --binary` without conflict resolution.
See `scripts/build.py:54–80`. [L1]

A new native service or cleaner patch has no current direct file overlap with these plugins.
Changing `wire_gen.go:173` shares a file with `quota-extension.patch:1–12`, whose hunk targets the account-usage call near line 211.
The current hunks are separate. Future generated Wire changes can still break patch context.
No patch application or build ran during this research.

Archived tasks mention Gemini helper compatibility and scheduling, not signature recovery:

- `archive/2026-11/11-07-eval-upstream-feature-sync/research/sub2api-v0220-upgrade.md:79–103` documents conversion-helper and text-delta API changes.
- `archive/2026-11/11-08-quota-scheduling-and-probe-memo/research/quota-scheduling-and-memoization.md:119–120` documents account admission checks.

Both paths are relative to `.trellis/tasks/`. Their historical helper-signature changes do not implement thought-signature handling.

## Protocol evidence and recovery semantics

### Confirmed contracts and observed errors

Google documents signatures on function calls and ordinary response Parts.
The first function call in each active-turn step requires its signature. Parallel sibling calls need no copied signature.
Keep original Parts and function-response order. Do not combine signed Parts. [P1, P2]

Both Gemini API and Vertex documentation support the literal `skip_thought_signature_validator` for synthetic or migrated function-call history.
Gemini API also documents `context_engineering_is_the_way_to_go`. Prefer the common sentinel already present in Sub2API.
The sentinel discards reasoning continuity. Normal forwarding should preserve authentic signatures. [P1, P2, S4]

| Error or shape | Primary evidence and implication |
| --- | --- |
| AI Studio `400 Corrupted thought signature.` | Sub2API #1309 and LiteLLM #49697 record this wording. A replayed Vertex signature can trigger it. [E1] |
| Vertex `400 Invalid thought signature.` | LiteLLM #49697 records the reverse-provider case. Its implementation matches status 400 plus `thought signature`. [E1] |
| Missing `thought_signature` on a function call | Google documents a 400 naming the function call and content index. Missing signatures differ from rejected nonempty signatures. [P1] |
| `thoughtSignature` / `thought_signature`, `functionCall` / `function_call` | Google protobuf defines snake_case fields. ProtoJSON accepts original names and lowerCamelCase names. Relay implementations can support fewer variants. [P3, E4] |
| `thought: true` with empty text | Google documents trailing streamed signatures with empty text. Empty text alone does not prove an invalid upstream response. [P1, P2] |
| `required oneof field 'data' must have one initialized field` | Google defines signature and thought metadata outside `Part.data`. A signature-only object cannot supply Part data. AstrBot #10866 reports the exact GenerateContent error after empty-string omission. [P3, E3] |
| CountTokens empty-Part 400 | Gemini CLI #5500 records the same structural failure in `CountTokensRequest`. Counting requests also need valid Parts. [E3] |

The existing `isGeminiSignatureRelatedError`, `gemini_messages_compat_service.go:1088–1093`, lowercases the extracted message and also scans raw fallback payloads.
It matches `thought_signature` or any `signature` substring. This catches both provider wordings and camelCase names, but can match unrelated signature errors. [S1]
Prefer a native-specific thought-signature matcher plus a real cleanup-change check. Keep the broader Claude-compat matcher unchanged.

Code Assist uses the same native contents inside a different envelope in Sub2API. [S1]
No authenticated Code Assist request ran. Exact provider-specific error wording and sentinel acceptance remain unverified for that path.
Likewise, this research did not reproduce either provider error against `gemini-4-hydrogen`.
The brief supplies the deployment observations. Public relay evidence independently supports the cross-provider explanation. [E1, E2]

### Recommended cleanup contract for planning

These are proposed recovery rules, derived from the contracts above. They are not behavior already implemented by the upstream cleaner.

| Retry Part | Recommended result |
| --- | --- |
| Non-function Part with either signature field | Remove signature metadata on the recovery attempt. Preserve valid text, media, code, and tool-response data. |
| Text thought Part with nonempty text | Remove its signature and `thought` marker. Retain the text as ordinary historical text. |
| Empty thought/signature carrier without useful data | Remove the whole Part. Do not leave `{}` or metadata-only objects. |
| Invalid signature on a required function-call Part | Replace it with the literal common sentinel. Preserve the call name, ID, arguments, and position. Stripping it alone can cause a missing-signature 400. |
| Snake_case native fields | Recognize both aliases at the direct Part boundary. Emit one field name for a logical field. Do not rewrite nested business JSON. |
| Content left with no Parts | Remove that content. If no usable contents remain, return the original failure rather than send an empty request. |

Ordinary requests must retain authentic signed empty-text Parts. Recovery can remove a carrier after discarding its rejected signature.
An explicit `text: ""` selects a protobuf oneof member, but an intermediate `omitempty` serializer can remove it.
Therefore, adding empty text to a metadata-only Part is an unreliable recovery strategy. [P1–P3, E3]

The existing `filterEmptyPartsFromGeminiRequest` removes contents with `parts: []` only.
It does not remove `{}`, metadata-only Parts, or blank text Parts.
See `antigravity_gateway_gemini.go:570–617`. A retry cleaner needs Part-level checks before this content-level filter. [S2]

Image-model behavior needs a separate boundary.
A Google forum report records `Text part is missing a thought_signature` for `gemini-3-pro-image-preview`.
Current Vertex documentation describes more permissive image behavior. Do not treat non-function signature removal as universal across model versions. [P2, E5]

### Retry, policy, countTokens, and Ops constraints

`shouldRetryGeminiUpstreamError` retries 429 and selected 5xx statuses, plus Code Assist OAuth 403s.
It excludes 400. Do not add all 400s to this transient-error classifier. [S1:1691–1708]

The native loop checks cached-content exceptions before error policy.
`checkErrorPolicyInLoop` reads and restores the response body, then can change account scheduling state.
`finalErrorPolicy` reuses the saved result so the same response does not execute policy twice. [S1:1319–1334,1629–1680]

Prefer preserving explicit error-policy precedence.
Place signature recovery after a nonmatching policy check, with a fresh policy result for the second response.
Giving rectification priority over a configured policy is a user-visible alternative that requires a planning decision.
PR #1309 checks signatures before its older policy helper. Its ordering needs review rather than direct copying. [S8]

Use a dedicated one-recovery guard and require an actual semantic cleanup change.
Serialized byte inequality alone can reflect JSON formatting changes.
The extra recovery must remain available when ordinary same-account retries equal zero or the transient budget is exhausted.
The #1309 head uses `geminiMaxRetries` and a simple `continue`. The baseline now uses configurable `maxAttempts` and different policy signatures. [S1, S8]

Rebuild the request from the cleaned inner body through the existing account-specific builder.
Code Assist must rebuild its `request` envelope. Vertex must keep its URL, authentication, and cached-content region behavior. [S1:1154–1270]
Do not unwrap, decrypt, or convert opaque signature envelopes between providers.

Keep existing countTokens transport, exhausted-transient, and insufficient-scope fallbacks.
The baseline does not estimate tokens after every arbitrary 400. A post-signature-retry fallback would extend that contract, as #1309 proposes.
Do not replace a successfully recovered countTokens response with an estimate. [S1:1298–1316,1383–1394,1429–1443, S8]

Reuse Ops kinds `signature_error`, `signature_retry`, and `signature_retry_request_error`.
Record account/proxy identity, upstream status, request ID, sanitized message, and existing bounded detail.
Close consumed response bodies and restore them for later policy or final-error handling.
Keep the second response authoritative and preserve failover signals. Antigravity provides the existing pattern. [S2:230–339]

`cachedContent` can hide signatures outside inline contents.
LiteLLM handles rejected cached prefixes separately. An inline-only cleaner cannot repair an opaque server-side cache.
Preserve Sub2API's existing explicit-cache routing unless the user adds cache reconstruction to this task. [E1, S1:1662–1680]

## Relay precedents

| Relay | Confirmed source and useful limits |
| --- | --- |
| LiteLLM | [PR #49697](https://github.com/BerriAI/litellm/pull/49697) merged on 2026-11-03 as `640a87f70db1e0fb2d08263a5337c6a5e007d12d`. Adds rejected-signature recovery for native and translated requests, both provider wordings, streaming, aliases, and cache interactions. Tests use scripted upstreams. [E1] |
| CLIProxyAPI | `internal/signature/gemini_validation.go:108–124` describes Vertex bare Tink and wrapped Gemini signatures. Its non-Vertex sanitizer rejects bare Tink. This supports the brief's format distinction, but describes observed formats, not a Google wire-format guarantee. [E2] |
| CLIProxyAPI cleanup | `gemini_sanitize.go:205–278` treats model Parts, function responses, first calls, and sibling calls separately. It avoids putting bypass values on ordinary text Parts. [E2] |
| new-api | `relaykit/relayconvert/internal/shared/gemini/request.go:64–94` supports optional bypass insertion using `context_engineering_is_the_way_to_go`. `relaykit/dto/gemini.go:340–343` uses `thought,omitempty` and `thoughtSignature`. This is missing-signature support, not proof of native rejected-signature retry. [E4] |

Sub2API issue #7147 reports strict-client failures with trailing signed empty-text SSE Parts.
Its claim that Google never emits this shape conflicts with Google's current documentation.
Use the issue as client-compatibility evidence. Do not adopt its proposed signature relocation as a normal forwarding rule. [P1, P2, E6]

## Smallest viable touchpoints and open decisions

Recommended baseline touchpoints:

1. `backend/internal/service/gemini_messages_compat_service.go`: service dependency, constructor, native setting gate, matcher, and bounded recovery.
2. `backend/cmd/server/wire_gen.go:173`: inject the existing `SettingService`. Update actual constructor callers if its signature changes.
3. `backend/internal/service/gemini_native_signature_cleaner.go`: retain helper ownership, but add a recovery-specific Part-aware helper.
4. Plugin-owned focused test files, after implementation approval: native recovery, cleaner structure, policy precedence, request builders, and countTokens results.

A new recovery helper can preserve the old exported cleaner's handler and Antigravity contract.
Changing the exported cleaner itself also changes both pre-cleaning and Antigravity behavior. That is a broader scope choice. [S2–S4]
No database migration or UI change is needed if the existing gate is reused. [S6, S7]
In this repository, these upstream changes belong in plugin patches. `scripts/build.py` already composes them. [L1]

The coordinator should settle these decisions before writing the planning artifacts:

| Decision | Preferred direction and reason |
| --- | --- |
| Plugin ownership | New plugin submodule. Signature recovery is independent of evaluation and quota features. |
| Setting | Reuse `enabled && thinking_signature_enabled`, matching Antigravity. Keep the API Key-specific default unchanged. |
| Forwarding scope | Cover all `ForwardNative` account builders through their shared loop. Preserve Claude compatibility and Antigravity retry behavior initially. |
| Shared cleanup | Add a recovery-specific helper first. Expand handler/Antigravity cleaning only if that scope is explicitly accepted. |
| Policy precedence | Keep configured policies first. A policy-first result can intentionally prevent rectification. |
| countTokens and images | Accept post-recovery counting fallback explicitly. Keep image-specific signature requirements outside the initial text/tool guarantee. |

No blocker prevents planning.
Runtime acceptance remains open for AIStudio2API, Vertex ServiceAccount, OAuth AI Studio, and OAuth Code Assist on the target model.
This research used source and public evidence. It did not execute provider calls or claim a working patch.

## Evidence index

- **S1:** [Gemini service, v0.2.23](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gemini_messages_compat_service.go). Exact functions and line numbers appear above.
- **S2:** [Antigravity Gemini service, lines 44–341 and 570–617](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/antigravity_gateway_gemini.go#L44). `ForwardGemini` has moved out of `antigravity_gateway_service.go`.
- **S3:** [Native handler, lines 642–660 and 754–766](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/gemini_v1beta_handler.go#L642).
- **S4:** [Native cleaner, lines 21–75](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gemini_native_signature_cleaner.go#L21). [Dummy constant, request_transformer.go:481–484](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/pkg/antigravity/request_transformer.go#L481).
- **S5:** [Anthropic filters, gateway_request.go:767 and 1302](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/gateway_request.go#L767).
- **S6:** [Settings schema/defaults, settings_view.go:525–539](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/settings_view.go#L525). [Reads/gate, setting_features.go:871–912](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/setting_features.go#L871). [Key, domain_constants.go:596–600](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/service/domain_constants.go#L596).
- **S7:** [Admin handlers, setting_handler_runtime.go:284–373](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/handler/admin/setting_handler_runtime.go#L284). [Routes, admin.go:608–609](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/backend/internal/server/routes/admin.go#L608). [UI, SettingsView.vue:554–746](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/views/admin/SettingsView.vue#L554). [API, settings.ts:1447–1483](https://github.com/Wei-Shaw/sub2api/blob/v0.2.23/frontend/src/api/admin/settings.ts#L1447).
- **S8:** [PR #1309 head source, lines 1054–1080 and 1235–1418](https://github.com/Wei-Shaw/sub2api/blob/36789928fd1732b707833ea9abb0692df02b4e29/backend/internal/service/gemini_messages_compat_service.go#L1235). [Changed files](https://github.com/Wei-Shaw/sub2api/pull/1309/files).
- **L1:** Local `.gitmodules:1–9`, `scripts/build.py:54–80`, plugin patch inventories, available refs, and local `git log --all -G` inspection.
- **P1:** [Google Gemini generateContent thought signatures](https://ai.google.dev/gemini-api/docs/generate-content/thought-signatures). Read Function calls, Non-function parts, and FAQ sections. The older short URL now emphasizes Interactions.
- **P2:** [Google Vertex thought signatures](https://cloud.google.com/vertex-ai/generative-ai/docs/thought-signatures?hl=en). Read REST/manual handling and Non-function Parts. Page date: 2026-11-12.
- **P3:** [Google Part protobuf, content.proto:96–144](https://github.com/googleapis/googleapis/blob/master/google/ai/generativelanguage/v1beta/content.proto#L96). [ProtoJSON field-name rules](https://protobuf.dev/programming-guides/json/#format-description).
- **E1:** [LiteLLM #49697](https://github.com/BerriAI/litellm/pull/49697). [Recovery source, lines 17–93 and 186–240](https://github.com/BerriAI/litellm/blob/640a87f70db1e0fb2d08263a5337c6a5e007d12d/litellm/llms/vertex_ai/gemini/rejected_thought_signature_retry.py#L17). [Mock tests, lines 147–219 and 439–478](https://github.com/BerriAI/litellm/blob/640a87f70db1e0fb2d08263a5337c6a5e007d12d/tests/unit/llms/vertex_ai/gemini/test_rejected_thought_signature_retry.py#L147).
- **E2:** [CLIProxyAPI sanitizer, gemini_sanitize.go:159–278](https://github.com/router-for-me/CLIProxyAPI/blob/6e6afab99a1939525ecb6bb1f0873c8e7a9df877/internal/signature/gemini_sanitize.go#L159). [Format observations, gemini_validation.go:108–124](https://github.com/router-for-me/CLIProxyAPI/blob/main/internal/signature/gemini_validation.go#L108). [Native executor use, gemini_executor.go:168](https://github.com/router-for-me/CLIProxyAPI/blob/main/internal/runtime/executor/gemini_executor.go#L168).
- **E3:** [AstrBot #10866](https://github.com/AstrBotDevs/AstrBot/issues/10866), [open PR #10867](https://github.com/AstrBotDevs/AstrBot/pull/10867). Reports cover v4.29.3, not an independent reproduction on v4.29.4. [Gemini CLI #5500](https://github.com/google-gemini/gemini-cli/issues/5500) documents countTokens structural errors.
- **E4:** [new-api bypass helper, request.go:64–94](https://github.com/QuantumNous/new-api/blob/main/relaykit/relayconvert/internal/shared/gemini/request.go#L64). [Part DTO, gemini.go:340–355](https://github.com/QuantumNous/new-api/blob/main/relaykit/dto/gemini.go#L340). [LiteLLM #41409](https://github.com/BerriAI/litellm/issues/41409) reports relay-specific alias differences.
- **E5:** [Google developer forum: text-part signature 400](https://discuss.ai.google.dev/t/400-invalid-argument-with-thought-signature-on-text-parts/109975). This is a user report for an image preview model.
- **E6:** [Sub2API #7147](https://github.com/Wei-Shaw/sub2api/issues/7147). Its response-shape claim conflicts with P1/P2.
