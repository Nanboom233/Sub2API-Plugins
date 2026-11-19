# Research: Redundancy and divergence audit

- Query: Perform the Round 2 line-by-line redundancy and divergence audit for patches 0001-0007, the account evaluation bridge and handlers, the inspection integration, the embedded UI, and the plugin test suite against clean Sub2API v0.2.23 and upstream CPA v0.4.7.
- Scope: mixed (internal applied-tree code, public upstream comparison, and project specifications)
- Date: 2026-11-19

## Baseline and method

The applied tree uses Sub2API v0.2.23 commit `5af9afb588c4b014b3df9db7d4073af1f8ae01b6` and patches 0001 through 0007.
All seven patches applied in order. Patch 0003 reported three trailing whitespace warnings.
The comparison uses the public plugin HEAD and the clean Sub2API tree.
Paths under `backend/` and `frontend/` below refer to the applied tree unless marked clean or upstream.
Patch files and tests reside under `plugins/codex-candy-eval/`.
Line impacts count existing source lines. They are estimates, not promised net reductions.

## Files found

- `backend/internal/service/account_codex_eval_service.go`: native account model discovery, request conversion, provider branches, and three pull-based stream readers.
- `backend/internal/handler/admin/account_codex_eval_handler.go`: protected evaluation page, JSON endpoints, request validation, and SSE response forwarding.
- `backend/internal/codexeval/*.go` and `backend/internal/codexeval/web/*`: evaluation runners, history, inspection hooks, embedded page, CSS, and browser modules.
- `backend/internal/service/codex_inspection_settings.go`, `codex_inspection_models.go`, `backend/internal/repository/account_codex_inspection.go`, and `backend/internal/handler/admin/codex_inspection_handler.go`: settings, atomic verdict persistence, and inspection API integration.
- `frontend/src/views/admin/CodexEvalView.vue` and `frontend/src/utils/embedded-url.ts`: native iframe page and relative URL/theme handling.
- `plugins/codex-candy-eval/patches/0001` through `0007` and `plugins/codex-candy-eval/tests/*`: patch source and Go/Node test coverage.

## External references and related specs

- Public upstream `haowang02/cpa-plugin-codex-candy-eval` v0.4.7 at commit `9682e76812c035e523a748620bba00c55c5970cb`.
- Clean Sub2API v0.2.23 at commit `5af9afb588c4b014b3df9db7d4073af1f8ae01b6`.
- `.trellis/spec/backend/directory-structure.md:107-119` requires the detector package boundary and asset ownership; `.trellis/spec/backend/runtime-installation.md` defines evaluation sending, history, page, and SIWC contracts.
- `.trellis/spec/backend/native-inspection.md` and `.trellis/spec/frontend/index.md` define inspection persistence, route, and embedded-page ownership.

## Findings

## Safe High-Value Cuts

| Finding | Evidence and action | Line impact |
| --- | --- | --- |
| Dead Candy wrappers | `backend/internal/codexeval/candy.go:47` and `:77` have no Go callers in the applied package or plugin tests. The runtime calls `runCandyChecked` at `backend/internal/codexeval/runtime.go:187`. Delete both wrappers and retain the checked functions. | 7 lines, excluding the obsolete comment. |
| Dead Fingerprint wrapper | `backend/internal/codexeval/fingerprint.go:131` only forwards to `runFingerprintChecked`. The runtime uses the checked function. No Go test calls the wrapper. | 3 lines. |
| Dead preference helpers | `backend/internal/codexeval/web/storage.js:11` defines `preference`, and `:15` defines `savePreference`. No embedded script calls either. Upstream uses these helpers, but this adaptation uses object-valued keys at `web/candy.js:7` and `web/app.js:71`. Delete the two unused functions or migrate all preferences deliberately. Preserve existing stored keys during any migration. | 7 lines for deletion. A migration has an unknown net impact. |
| Pass-through inspection method | `backend/internal/handler/admin/codex_inspection_handler.go:99` only calls `AccountTestService.PersistCodexInspectionVerdict`. The hook at `:133` can use `accounts.accountTestService.PersistCodexInspectionVerdict` directly. The method signatures match. | 3 lines. |
| Single-use start layer | `backend/internal/codexeval/runtime.go:84` calls `start`, which only calls `startChecked` at `:88`. Inspection calls `startChecked` directly at `backend/internal/codexeval/inspection.go:684`. Call `startChecked` from `Start` with the existing arguments. Preserve the public `Start` contract. | 3 lines. |
| Transport-shaped history plumbing | `backend/internal/codexeval/runtime.go:233` builds `url.Values` solely for `recordResponse` at `backend/internal/codexeval/state.go:161`. That function immediately reads the same two values. Pass account ID and record ID directly. `managementResponse` and JSON helpers at `runtime.go:264` also serve clear and error paths, so their removal needs a coordinated API rewrite. | Removes two query conversions and an import if unused. Net line count depends on signatures. |
| Redundant SIWC summary copy | `backend/internal/codexeval/siwc.go:28` returns the record unchanged. `State` uses the generic summary loop at `runtime.go:227`. Assign the SIWC slice directly only if the existing lock and marshal lifetime remain unchanged. | 3 method lines and one loop. The replacement adds one line. |
| Dead CPA credential style | `web/style.css:222` includes `.credential .api-key` in a shared rule. `:223` styles it separately. Native `web/components.js:133` emits no such element. Remove the unused selector and its dedicated rule. | One rule line and part of one selector line. |
| Dead CPA principle panel CSS | `web/style.css:174-177` defines `.principle-body` and its paragraph/link descendants, but `web/ui.html` and all `web/*.js` emit no `principle-body` element. The static selector scan found no dynamic construction for this class. Remove the four rules. | 4 lines. |
| Repeated SSE framing | `service/account_codex_eval_service.go:747` and `:846` marshal typed Responses events and append identical SSE frames. Native `internal/pkg/apicompat/anthropic_to_responses_response.go:323` provides `ResponsesEventToSSE` with the same framing and error return. Reuse it in both loops. Gemini emits maps at `account_codex_eval_service.go:884`, so it cannot use that typed helper unchanged. | About 6–10 lines after error handling. |
| Repeated integer conversion | `service/account_codex_eval_service.go:992` duplicates the type cases in native `service/scheduler_snapshot_service.go:1763`. The three callers at `:947` can use `toInt64` and ignore its boolean while keeping the returned value. | About 12 lines after call-site changes. |
| Shared response setup | Non-2xx body restoration is duplicated at `service/account_codex_eval_service.go:574-579` and `:677-682`; successful stream header setup is duplicated at `:584-589` and `:685-690` (with the Chat branch at `:437-440`). A small local helper can share the identical blocks while keeping status and body ownership. | Approximately 10–16 net lines. Confirm with the final helper. |
| Inspection test reset | `tests/test_codexeval_inspection_test.go:20`, `:226`, `:432`, `:526`, `:625`, and `:689` repeat global reset blocks. The runtime test also resets globals at `tests/test_codexeval_runtime_test.go:33`. A test-only helper can share the common assignments and retain case-specific setup. | About 25 lines before helper and call-site adjustments. |

The estimates do not overlap except where stated. They exclude future detector sync changes.
The history and preference findings need contract tests before a rewrite.
The applied Candy result uses `ok`, `error`, and `skipped` at `candy.go:24` and `web/candy.js:11`.
Upstream HEAD uses status values in `internal/plugin/web/candy.js:10`.
History schema compatibility makes a direct field replacement unsafe without a migration.

## Contract-Changing Candidates Requiring User Decision

| Candidate | Evidence and decision | Line impact |
| --- | --- | --- |
| Anthropic URL owner | `service/account_codex_eval_service.go:471` supports base URLs ending in `/v1` and `/v1/messages`. Native `service/anthropic_messages_url.go:11` always appends `/v1/messages` and omits `beta=true` for a specific Cloudflare account endpoint. Direct substitution breaks the first two existing forms and changes Cloudflare behavior. Reconcile both contracts in one native owner only after deciding the URL behavior. | The local helper has 10 lines. A combined owner needs additional cases and tests. |
| Handler and service validation | `handler/admin/account_codex_eval_handler.go:117` and `service/account_codex_eval_service.go:227` both validate model and stream. Removing the handler validation changes the HTTP error path. `handler/admin/codex_inspection_handler.go:156` and `service/codex_inspection_settings.go:55` also normalize and validate twice. The handler returns 400 while its service error path returns 500. Preserve those responses if validation moves. | About 8 evaluation-handler lines and 5 inspection-handler lines before error classification. |
| Shared request conversion | `service/account_codex_eval_service.go:483` and `:594` repeat Responses-to-Anthropic conversion, model assignment, stream selection, and token defaults. Gemini also needs the encoded Claude body for its next conversion. Extract one typed helper only if it retains both outputs and error behavior. | About 15 net lines, depending on the helper signature. |
| Shared account predicate | `handler/admin/codex_inspection_handler.go:15` and `service/account_codex_eval_service.go:23` check the same native account types. Sharing across packages needs an exported service helper or Account method. Keep the same support policy for both consumers. | Roughly 8–10 repeated lines before the shared API. |
| Email lookup | `handler/admin/codex_inspection_handler.go:22` selects email from `Extra` and credentials in key order. Native `service/account_scheduling_threshold_eval.go:198` uses `firstStringValue`, but its source order differs. Sharing it without preserving lookup order changes wildcard matching. | No safe line saving established. |
| Record embedding | `fingerprint.go:92`, `pelican.go:47`, and `siwc.go:15` repeat record fields. Upstream `internal/plugin/state.go:49` embeds a common record. An embedded record can preserve JSON names, but constructors and schema-3 history need verification. Candy has different legacy fields and no record ID. | About 18 repeated field lines before constructor changes. Net savings remain unknown. |
| Preference format | `web/candy.js:7` stores an object at the base key. Other tabs use separate objects at `web/fingerprint.js:7`, `web/pelican.js:5`, and `web/siwc.js:5`. Re-aligning upstream storage requires a read migration for existing preferences. | No reliable net saving established. |
| Fingerprint result presentation | Applied `web/fingerprint.js:14` uses a compact result and table. Upstream v0.4.7 `internal/plugin/web/fingerprint.js:31` and `:65` use a different summary and detailed sample layout. Native account prefixes and targets do not require this presentation difference. Choose the desired presentation before restoring upstream markup. | Upstream file has about 30 more lines before native adaptation. |
| Version and SIWC header | `web.go:10` supplies the footer version and `siwc.go:62` also uses it in the probe header. Upstream v0.4.7 changes the version, while `.trellis/spec/backend/runtime-installation.md` specifies `cpa-siwc-check/0.4.6`. Separate display and probe versions to satisfy both, or change the contract explicitly. | One separate constant and one reference. |

`web/style.css:363` defines `.detail-note`, which the current fingerprint page does not emit.
Upstream v0.4.7 uses that class. Keep it until the fingerprint presentation decision.
The handler message at `codex_inspection_handler.go:73` says Candy inspection although fingerprint inspection is supported.
Correct the message when the handler changes. This is a copy correction, not a line reduction.

## Required Sub2API Adaptations

| Area | Evidence and reason | Trim boundary |
| --- | --- | --- |
| Native accounts and groups | `web/catalog.js:1`, `web/credentials.js:1`, and `web/app.js:180` use native account data. Upstream `web/providers.js` owns CPA providers and authentication files. Native accounts must not become local CPA credential files. | Retain the native selection, account identity, and restriction behavior. Remove only proven unused UI code. |
| Provider bridge | `backend/internal/service/account_codex_eval_service.go:226` routes native accounts. `:340` and `:489` use native `apicompat` request conversion. `:804` uses native Anthropic stream finalization. Clean Sub2API's `backend/internal/service/gateway_forward_as_responses.go:731` also uses that finalizer. | The 1,006-line adapter has three stream readers. Do not replace them with gateway handlers without preserving raw stream, cancellation, usage, and account-test semantics. |
| SIWC | `codexeval/siwc.go:46` sends the one-shot probe through the native sender. `web/app.js:190` excludes only the local rate limit from SIWC blocking. | Remove the identity summary method above. Keep the probe and the other eligibility checks. |
| Native inspection | `codexeval/inspection.go:36` defines native hooks. `handler/admin/codex_inspection_handler.go:103` connects account and settings services. `codexeval/inspection_notify.go:1` owns notifications. | The pass-through method can go. Keep scheduling, fingerprint single-run verdicts, name and email patterns, model control, ntfy, and Bark. |
| Narrow inspection write | `service/codex_inspection_models.go:104` calls `UpdateCodexInspectionState`. `repository/account_codex_inspection.go:37` performs the conditional update. This protects unrelated account fields and stale credentials. | Do not replace this with a full account update. Keep removed-model recovery and verdict ordering. |
| History | `codexeval/state.go:14` fixes schema 3. `:42` protects legacy fingerprint decoding and `:70` blocks saves on load errors. Four maps and migration copies are approved contracts. | Simplify transport-shaped parameters only. Preserve migration, atomic replacement, clear rollback, and latest-20 retention. |
| Native page and authorization | `server/routes/admin.go:50` registers protected APIs. `server/router.go:117` starts inspection and serves the page. `frontend/src/router/index.ts:552` supplies the admin route. `web/app.js:35` reads the native session token. | Keep the iframe route, native session, and API boundary. |
| License | `web/ui.html:189` links to LGPL-3.0. | Retain the footer link. |
| Codex request and detector | `codexeval/codex.go:134` builds the captured request. `fingerprint_detector.go:119` loads the detector and `:233` analyzes outputs. These files support approved evaluation semantics. | Upstream `codex.go` differs mainly in package and the local `mustDecode` helper. Do not delete detector math on line count alone. |

### Bridge and handler comparison

The bridge already uses native base URL validation at `service/account_codex_eval_service.go:281`, `:518`, and `:645`.
It uses native OpenAI URL, identity, and account transport helpers at `:285`, `:356`, and `:402`.
It uses native Gemini request builders at `:621` and `:662`, and native upstream transport at `:570` and `:673`.
The model catalog at `:32` deliberately returns raw evaluation model names rather than applying the normal account picker mappings.
The OAuth payload normalization at `:183` has narrower evaluation rules than the native gateway transform.
The tools filter at `:445` removes additional tools for the Anthropic and Gemini conversions.

Chat Completions converts events through `apicompat` at `:741`, and Anthropic uses the native finalizer at `:804`.
Gemini transforms its own payload and emits Responses events at `:593` and `:884`.
Their readers differ in upstream formats, finish conditions, usage, and errors.
No native gateway handler is a drop-in replacement for all three readers.
Keep their close, cancellation, error, and usage behavior if their framing is shared.

`handler/admin/account_codex_eval_handler.go:99` flushes each response write.
The handler's status and JSON wrappers preserve the admin API envelope and raw stream behavior.
Do not remove those wrappers solely because the service also validates the request.

The handler audit found no safe duplicate JSON or header wrapper beyond the validation overlap already listed as contract-sensitive. `account_codex_eval_handler.go:112-124` must read the body and reject malformed or non-streaming admin requests with HTTP 400; `:135-145` must copy the upstream content type, disable buffering, preserve the upstream status, close on request cancellation, and flush each SSE write. The service-side validation at `account_codex_eval_service.go:227-236` is still required for direct service callers, so deleting either layer changes an error boundary.

### Inspection and native integration comparison

`codexeval/inspection.go:36` has distinct list, recheck, verdict, priority, and notification hooks.
The coordinator rechecks participation before sends and writes at `inspection.go:468` and `:572`.
It persists the verdict before the optional priority update. The two hooks therefore have distinct failure behavior.
`handler/admin/codex_inspection_handler.go:48` keeps availability and native scheduling state separate.
`service/admin_account.go:693` preserves inspection metadata on full account edits.
`repository/account_codex_inspection.go:37` compares account state and writes inspection fields atomically with the scheduler outbox.

`server/router.go:117` starts inspection and registers the embedded page.
`server/routes/admin.go:50` registers protected APIs. `web/embed_on.go:362` bypasses the native frontend for the page.
`frontend/src/views/admin/CodexEvalView.vue:1` embeds the page and tracks the theme.
Clean `CustomPageView.vue:156` has a similar observer, but no shared composable exists.
`frontend/src/utils/embedded-url.ts:25` supports same-origin relative URLs. Its other consumers still need its shared parameters.
The page CSP and frame headers at `handler/admin/account_codex_eval_handler.go:18` serve the inline same-origin iframe.

### Core and page comparison

The v0.4.7 fingerprint implementation replaces the detector algorithm and data, not just its file layout.
Keep the existing `codexeval` package and its inspection-facing model identity while porting the matched algorithm and data.
Upstream `runs.go` and `plugin.go` use CPA credentials and progress. Applied `runtime.go:18` uses native account and group IDs.
Upstream `state.go` and `migration.go` use the CPA history shape. Applied `state.go:14` preserves the approved native schema and migration rules.
Upstream `ui.go` assembles CPA modules. Applied `web.go:36` embeds the native modules and inspection page.
Upstream `pelican.go` corresponds to applied `pelican.go`; there is no separate upstream `code.go` in v0.4.7.
The applied Candy, Pelican, SIWC, and model paths retain native sender, task, and history contracts.

The CSS selector scan checked static selectors against `web/ui.html` and `web/*.js`.
The unused `.api-key` and `.principle-body` rules and sync-dependent `.detail-note` rule are listed above.
Dynamic `plan-*` classes remain live through `web/components.js:137`. Status and row classes also use generated markup.
The page uses native account catalog and filters at `web/catalog.js:2` and `web/credentials.js:1`.
`web/app.js:425` binds shared collection actions to native targets and run IDs.
The CPA `providers.js` and `host.js` have no equivalent role in this native session.
No other unused JavaScript helper or DOM ID was established by the scan.

### Test review

No Go test calls the dead Candy or Fingerprint wrappers. `tests/test_ui.cjs:859` calls the distinct JavaScript `runCandy`.
The inspection cases cover different confirmation, cancellation, matching, and write-order paths.
The UI suite shares its harness at `tests/test_ui.cjs:26` and group fixture at `:60`.
Its cases cover distinct account, settings, stale-response, SIWC, and rate-limit behavior.
Settings tests at `tests/test_service_codex_inspection_settings_test.go:23` exercise a different layer from model write tests at `tests/test_service_codex_inspection_models_test.go:78`.
Repository and handler tests cover separate atomic writes and account translation at `tests/test_account_codex_inspection_test.go:19` and `tests/test_admin_codex_inspection_handler_test.go:30`.
No complete test case was established as redundant.
The existing `backend/internal/web/embed_test.go:793` tests API aliases rather than the evaluation iframe route.
If integration changes, check page bypass, route registration, and the iframe URL on a nonstandard port.

## Data and vendor assets

The five files in patch 0003 match upstream v0.4.7 byte for byte.
`web.go:21` embeds them and `web/candy.js:19` uses their Markdown and math functions.
The standalone iframe loads them at `web/ui.html:193`. The clean frontend has no matching dependencies in its package manifest.
No vendor deletion is supported by this comparison. The expected reduction is zero lines.

The applied `data/codex_context.json` and `data/lm-detector/enrollment-suite.json` match the upstream v0.4.7 files.
The detector binary and model data changed upstream. Port their matched versions together.
The active directory contract at `.trellis/spec/backend/directory-structure.md:107` keeps detector code in the existing package.
It also keeps detector assets in patch 0002. A new package solely to copy upstream layout conflicts with that contract.

## Caveats / Not Found

The applied core comprises `candy.go` 113 lines, `codex.go` 243, `fingerprint.go` 272, `fingerprint_detector.go` 695, `pelican.go` 136, `siwc.go` 134, `model.go` 310, `runtime.go` 278, `state.go` 213, and `web.go` 93.
The embedded page includes `ui.html` 209, `style.css` 454, `app.js` 550, and `inspection.js` 554 lines.
Patch 0002 includes 76,365 lines of detector data. Its size alone does not establish redundancy.
The tests include a 1,210-line `tests/test_ui.cjs` and a 795-line inspection test.
Their size alone does not establish duplicate coverage.
Compare each upstream update with the companion upstream history report before adopting its schema or UI changes.

No complete test case was proven redundant, and no obsolete assertion for the removed Go wrappers was found. The repeated test resets are shared scaffolding only; each inspection case exercises a different cancellation, matching, persistence, or write-order contract. No other unused CSS selector, DOM ID, JavaScript helper, or provider branch was established after checking static markup and dynamic class generation. Line impacts are source-line estimates and can change with helper signatures and tests.

This research update changed only this file. It did not modify production code, specifications, patch files, or tests.
