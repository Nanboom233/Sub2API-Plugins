# Research: Sub2API v0.2.23 Plugin Conflicts

- Query: Check patch conflicts and semantic intersections for both plugins on Sub2API v0.2.23.
- Scope: Internal source comparison, temporary patch composition, and Go package compilation.
- Date: 2026-11-18

Unless noted, source anchors refer to the combined tree at `/tmp/sub2api-v0.2.23-conflicts-combined`.
Rejected-hunk source anchors and repository-interface anchors refer to clean upstream at `/tmp/sub2api-v0.2.23-research`.

## Findings

### Rejected quota hunks

The evaluation patches applied to the clean v0.2.23 source. The quota patch rejected two context hunks in standalone and combined application.

| Hunk | Upstream source and cause | Temporary resolution |
| --- | --- | --- |
| `backend/go.mod`, Hunk #4 (`quota-extension.patch:43-50`) | The hunk expects `github.com/google/jsonschema-go v0.4.2 // indirect` in the indirect block. Commit `e0cf4984f0d7c0d54ccb2d36292272a4231c07be` moved it to the direct block at `backend/go.mod:26`. | Keep the direct requirement and add the quota `github.com/google/pprof` requirement in the indirect block. |
| `frontend/src/components/account/AccountUsageCell.vue`, Hunk #3 (`quota-extension.patch:2257-2271`) | The hunk expects a `formatCompactNumber` import. Commit `e6774625` added `formatDateTime` to that import at `AccountUsageCell.vue:774`. | Keep `formatDateTime` and merge the quota imports into the same import block. |

The go.mod rejection is context drift, not a dependency conflict. The UI rejection is also context drift. The quota additions do not replace the upstream requirements or date formatter.

### Account usage cell

Quota Hunk #4 changes `_usageCache` to require a `config: string` field.
Commit `e6774625` writes active results without that field at clean upstream `AccountUsageCell.vue:1651-1659`.
The temporary resolution reads `apiKeyUsageRefreshKey.value` before the active request and stores it with the result.
The combined source does this at `AccountUsageCell.vue:1674-1683`.

`buildAPIKeyUsageRefreshKey` returns an empty string for non-API-key accounts at combined `accountUsageRefresh.ts:35-36`. This preserves their active-query cache behavior. API-key entries include credential and script inputs at `:39-53`. `vue-tsc` passed after this repair. See [the dependency report](./upstream-v0.2.23-dependencies.md).

Upstream commit `e6774625` adds stale-quota feedback, observation time, and `utilization_unknown` rendering for OpenAI OAuth. The quota patch keeps this branch at combined `AccountUsageCell.vue:125-164`. It adds API-key usage below the other-account quota bars at `:758-763`.

Upstream commit `17724301` changes the Gemini refresh skeleton to render only when `loading && !usageInfo`. This keeps the last usage visible during a refetch. The quota patch retains that condition at combined `AccountUsageCell.vue:646`. Its API-key display does not replace the Gemini branch.

### Account repository interface

Upstream commit `4114fedd1` added `AccountRepository.ClearModelRateLimit(ctx, id, scope)` for one model window. The interface declares it at `backend/internal/service/account_service.go:113`. The repository removes only that scope. It then enqueues a scheduler event and syncs the account snapshot at `backend/internal/repository/account_repo.go:2724-2761`.

That upstream commit also updated the repository-interface test doubles. These include `backend/internal/server/api_contract_test.go:2050`, `backend/internal/service/account_service_delete_test.go:198`, and `backend/internal/service/admin_service_clear_error_test.go:51`. They also include `backend/internal/service/gateway_multiplatform_test.go:215`, `gemini_multiplatform_test.go:176`, `ratelimit_service_clear_test.go:60`, and `ratelimit_session_window_test.go:58`. The quota patch does not change this method or its scope semantics. The quota-only and combined package compile checks pass with the updated interface.

### Wire providers

The quota patch extends `ProvideAccountUsageService` with `HTTPUpstream` and `*config.Config`. The combined provider assigns these values for upstream API-key probes at `backend/internal/service/wire.go:228-260`. The generated call passes both values at `backend/cmd/server/wire_gen.go:211`.

Upstream separately constructs `UsageBillingLaneCombiner` at `wire_gen.go:109`, accepts it in cleanup at `:431`, and stops it at `:651-654`. The quota provider does not replace or depend on this combiner. Both registrations remain in the combined generated file.

### Scheduler snapshot and account state

Upstream commit `9c328009` added `GetSnapshotValues` and the in-process snapshot cache. `GetSnapshot` delegates to it at `backend/internal/repository/scheduler_cache.go:330-362`. The quota patch only adds its managed quota keys to `filterSchedulerExtra`. Those keys appear at `scheduler_cache.go:1587-1598` in the combined tree, so scheduling reads retain the quota state from the projected account.

Upstream commit `9d5fb150` adds `openai_passthrough_model_filter` to the same projection at `scheduler_cache.go:1559-1560`. The quota hunk applies after this key and preserves it. The upstream comment explains that candidate filtering needs this setting before model mapping checks. Quota keys and the passthrough filter therefore remain available through the same snapshot path.

The quota patch adds API-key usage state to `Account.IsQuotaExceeded` at `backend/internal/service/account.go:3100-3168`. Existing `Account.IsSchedulable` calls that method when account quotas apply at `account.go:194-214`. The patch also adds API-key quota windows as threshold candidates at `account_scheduling_threshold_eval.go:67-69` and `:419-445`. Existing platform-specific candidates still take precedence when they match.

### Usage service and API compatibility

The combined source preserves upstream `UsageProgress.UtilizationUnknown` at `backend/internal/service/account_usage_service.go:153`.
It uses this field when local statistics exist without an upstream OpenAI quota value at `:888-895`.
The quota patch adds API-key usage fields but keeps the upstream field and its use.

The quota branch runs before native usage handling at `account_usage_service.go:388-423`.
Without a quota script, native-only accounts continue through `getNativeUsageForAccount` at `:400-401`.
Gemini, Antigravity, and Grok probe accounts also retain their native usage queries at `:404-409`.
Anthropic active usage still calls `syncActiveToPassive` at `:544`.
That function writes its snapshots and clears recovered Fable model limits at `:779-819`.
The quota patch does not alter these upstream recovery rules.

The evaluation service consumes native `apicompat` APIs. It calls `ResponsesToChatCompletionsRequest` at `backend/internal/service/account_codex_eval_service.go:335-345`. It also calls stream converters at `:426-437` and `:720-746`, plus `ResponsesToAnthropicRequest` at `:482-495`.

Upstream changed `apicompat` behavior between v0.2.21 and v0.2.23. Changes include cache accounting, strict-schema defaults, and mid-conversation system messages. The evaluation converter entry points remain available at `backend/internal/pkg/apicompat/chatcompletions_responses_bridge.go:39-45` and `backend/internal/pkg/apicompat/responses_to_anthropic_request.go:16-22`. The quota patch does not import or change `apicompat`.

### Shared plugin files

Both plugins edit `backend/internal/server/routes/admin.go`. The evaluation route group uses `/codex-eval` at combined `routes/admin.go:50-58`. Its account routes use `/codex-eval` and `/codex-eval-inspection` at `:408-410`. The quota test route uses `/accounts/quota-script/test` at `:419-425`. These route additions do not overlap.

Both plugins edit `backend/internal/service/admin_account.go`. Evaluation fields remain protected from normal account updates at `admin_account.go:718-722`. Quota-managed fields are preserved separately at `:745-749`. Quota state is removed from duplicated accounts through `duplicateAccountDiscardedExtraKeys` at `:100-166`, then deleted from the clone at `:169-177`.

The shared edits have no cross-plugin production symbol dependency. Evaluation production files use native service and `apicompat` symbols. Quota production files use quota symbols defined by the quota patch. The shared service file uses evaluation field names as strings and quota constants from its own service package. The standalone and combined Go checks below confirm these import and interface boundaries.

### Go package compile checks

The checks used `GOTOOLCHAIN=auto` and upstream Go directive `1.27.4`. The host used its normal Go caches. `GOMODCACHE` was `/Volumes/User Data/caches/go/modules`, and `GOCACHE` was `/Volumes/User Data/caches/go/build`.

The inherited evaluation and quota trees had Go directive `1.27.2`. I restored `1.27.4` in those temporary trees and reran both commands. The quota-only tree included both context repairs and the active-cache config repair. The combined tree applied evaluation patches first, then the quota patch with the same repairs.

| Tree | Command | Exit |
| --- | --- | ---: |
| Evaluation only | `cd /tmp/sub2api-v0.2.23-conflicts-eval/backend && GOTOOLCHAIN=auto go test -run '^$' ./internal/service ./internal/handler/admin ./internal/codexeval` | 0 |
| Quota only | `cd /tmp/sub2api-v0.2.23-conflicts-quota/backend && GOTOOLCHAIN=auto go test -run '^$' ./internal/service ./internal/handler/admin ./internal/repository` | 0 |
| Combined, evaluation packages | `cd /tmp/sub2api-v0.2.23-conflicts-combined/backend && GOTOOLCHAIN=auto go test -run '^$' ./internal/service ./internal/handler/admin ./internal/codexeval` | 0 |
| Combined, quota packages | `cd /tmp/sub2api-v0.2.23-conflicts-combined/backend && GOTOOLCHAIN=auto go test -run '^$' ./internal/service ./internal/handler/admin ./internal/repository` | 0 |

Each command compiled package tests without running test cases. The dependency report records the frozen pnpm install, `vue-tsc`, tokenizer, and embedded UI results.

## Files Found

- `plugins/codex-candy-eval/patches/0001-evaluation-core.patch` through `0007-sub2api-integration.patch` — Evaluation implementation and native integration.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch` — Quota service, scheduling, routes, and account usage UI.
- `/tmp/sub2api-v0.2.23-research/backend/internal/service/account_usage_service.go` — Upstream usage fields, active-to-passive synchronization, and OpenAI quota freshness.
- `/tmp/sub2api-v0.2.23-research/backend/internal/repository/scheduler_cache.go` — Upstream scheduler projection and `GetSnapshotValues`.
- `/tmp/sub2api-v0.2.23-conflicts-eval` — Evaluation-only patched source used for package compilation.
- `/tmp/sub2api-v0.2.23-conflicts-quota` — Quota-only patched source with temporary conflict repairs.
- `/tmp/sub2api-v0.2.23-conflicts-combined` — Combined patched source with temporary conflict repairs.

## Related Specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/native-inspection.md`
- `.trellis/spec/backend/index.md`
- `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/research/upstream-v0.2.23-compatibility.md`
- `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/research/upstream-v0.2.23-dependencies.md`

## Caveats / Not Found

- The compile checks establish package compatibility. They do not run product behavior tests or the full production build.
- The diagnostic tree retained patch reject files. The compiled source included both hunk repairs. All temporary verification trees moved to Trash after checks.
- Upstream v0.2.21 to v0.2.23 changed 16 `apicompat` files. The evaluation package compile confirms the used entry points, not every conversion behavior.
