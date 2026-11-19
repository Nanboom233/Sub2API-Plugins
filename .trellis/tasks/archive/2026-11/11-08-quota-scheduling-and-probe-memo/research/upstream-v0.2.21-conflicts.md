# Research: Upstream v0.2.21 Source Conflicts

- Query: Assess source conflicts and shared-file interactions for both plugins on Sub2API v0.2.21.
- Scope: internal
- Date: 2026-11-13

## Findings

### Upstream path overlap

The evaluation plugin has no changed-path overlap with upstream v0.2.21. Its seven patches apply to a clean v0.2.21 source tree.

The quota plugin intersects five paths changed upstream:

| Path | Conflict and required preservation |
| --- | --- |
| `backend/go.sum` | Keep upstream checksum additions. The quota dependency entries are additive. Dependency versions and checks are recorded in `upstream-v0.2.21-dependencies.md`. |
| `backend/internal/service/account_usage_service.go` | Upstream added the `force` argument to `getAntigravityUsage`. The quota wrapper forwards `forceProbe` through `getNativeUsageForAccount`, which retains native provider dispatch. See upstream `account_usage_service.go:367-407` and `:1115-1125`, and the quota hunk at `quota-extension.patch:1617`. |
| `frontend/src/components/account/AccountUsageCell.vue` | Keep the upstream Antigravity active-query control. It calls `getUsage(..., 'active', true)` at `AccountUsageCell.vue:1650-1658`. The quota hunk adds API-key usage display and cache keys without removing this control. |
| `frontend/src/types/index.ts` | The quota hunk adds `one_day`, `quota_total`, `balance`, and `balance_unit` usage fields. It does not replace the existing upstream types, including cache-token fields at `index.ts:2048` and `:2112`. |
| `frontend/src/views/admin/AccountsView.vue` | Keep upstream rows visible during refresh: the table remains mounted while rows exist at `AccountsView.vue:194-199`. The quota changes add API-key usage batching and cache identity checks. They retain the parent manual-refresh token and per-account request tokens at `AccountsView.vue:738-756` and `:812-845`. |

These are compatibility overlaps, not rejected patch hunks. Both plugin patches applied independently to fresh v0.2.21 source trees. The combined patch set also applied.

### Shared plugin files

Both plugins edit `backend/internal/server/routes/admin.go` and `backend/internal/service/admin_account.go`. Their additions have separate routes and managed keys.

The evaluation routes use `/codex-eval` and account paths ending in `/codex-eval` or `/codex-eval-inspection`. The quota test route is `/quota-script/test`; the final combined route table contains both sets at `routes/admin.go:50-58` and `:408-422`.

The evaluation update path preserves `codex_eval_inspection_*` keys. The quota path preserves and clears `APIKeyQuotaManagedExtraKeys`. The combined update code keeps these key sets distinct at `admin_account.go:717-749`. The inspected shared hunks add no direct production-symbol dependency between the plugins.

### Build evidence

Standalone package compilation passed on the patched v0.2.21 source trees:

```sh
go test -run '^$' ./internal/service ./internal/handler/admin ./internal/codexeval
go test -run '^$' ./internal/service ./internal/handler/admin ./internal/repository
```

The first command covers evaluation packages. The second covers quota packages. These compile checks do not run product behavior tests or replace the combined production build.

### Files found

- `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch` — Adds evaluation routes and preserves evaluation-managed account fields.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch` — Adds quota routes, service behavior, usage display, and quota-managed fields.
- `/tmp/sub2api-v0.2.21-research` — Clean upstream v0.2.21 source used for the overlap review.
- `/tmp/sub2api-v0.2.21-clean` — Combined patched source used to inspect route and update behavior.
- `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/design.md` — Defines the v0.2.21 delivery boundary and preservation requirements.
- `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/research/upstream-v0.2.21-dependencies.md` — Records module, frontend, provider-injection, and dependency checks.
- `.trellis/spec/backend/api-key-quota.md` — Defines the quota usage and scheduling contract.
- `.trellis/spec/backend/index.md` — Lists active backend contracts and verification guidance.
- `.trellis/spec/frontend/index.md` — Lists frontend contracts and verification guidance.

### External references

- Sub2API `v0.2.21`, tag object `43f15294c477bec427d586ddfc3f918ce1284c98`, peeled commit `10ba8f9b4dc2e6023d4a9879ab77b21841babd10`, as recorded in the task PRD.
- No external documentation was needed for this source-level comparison.

### Related specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/index.md`
- `.trellis/spec/frontend/index.md`

## Caveats / Not Found

- This report covers patch application, source overlap, and package compilation. The full combined production build remains a separate acceptance check.
- The quota spec still describes v0.2.20 as its baseline. The task design calls for updating active specs after v0.2.21 acceptance passes.
