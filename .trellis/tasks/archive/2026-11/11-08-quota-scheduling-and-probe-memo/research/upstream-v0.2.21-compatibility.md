# Research: Sub2API v0.2.21 Plugin Compatibility

- Query: Assess the Sub2API v0.2.20 to v0.2.21 change for the quota and evaluation plugins.
- Scope: Mixed. Inspect public upstream tags, local patches, tests, specs, and build scripts.
- Date: 2026-11-13

This file records the initial combined application check.
Use [source conflicts](./upstream-v0.2.21-conflicts.md) for both plugins' file intersections and standalone contract checks.
Use [dependencies](./upstream-v0.2.21-dependencies.md) for module versions, provider injection, frontend resolution, and subsequent test evidence.

## Upstream Source

The upstream repository is `https://github.com/Wei-Shaw/sub2api.git`.

| Tag | Tag object | Peeled commit | Date |
| --- | --- | --- | --- |
| `v0.2.20` | `ec41309811cd30af310a0e4b9119b976ce65c9be` | `dab829a4e9b7d1cc307189aea8b0319eb29e29d0` | 2026-11-07 |
| `v0.2.21` | `43f15294c477bec427d586ddfc3f918ce1284c98` | `10ba8f9b4dc2e6023d4a9879ab77b21841babd10` | 2026-11-11 |

The tag objects are annotated. Use the tag names in builds. Use the peeled commits when a source identity is needed.

## Findings

### Upstream Changes That Touch Plugin Owners

The v0.2.21 source changes these plugin-owned areas:

1. `backend/internal/service/account_usage_service.go` adds a `force` argument to `getAntigravityUsage`.
   The argument bypasses the Antigravity usage cache for manual queries.
2. `frontend/src/components/account/AccountUsageCell.vue` adds the Antigravity active-query control.
   It also keeps stale usage visible during account-list refresh.
3. `frontend/src/views/admin/AccountsView.vue` keeps existing rows while a refresh is in progress.
4. `frontend/src/types/index.ts` adds optional `cache_creation_30m_tokens` and `cache_creation_12h_tokens` fields.
5. `backend/go.sum` gains cache and CLI dependency checksums used by the v0.2.21 source.

The current quota patch applies after these changes. The patched source keeps the upstream force path and passes the Go package tests.
At `/tmp/sub2api-v0.2.21-clean/backend/internal/service/account_usage_service.go:375-409`, `getUsageForAccount` passes `forceProbe` to both native usage and API-key quota paths.

The v0.2.21 release also adds migrations `249_add_usage_logs_api_key_cost_index_notx.sql` and `250_openai_cache_write_ttl.sql`.
The release notes correct the fixed memory-budget key to `gateway.request_body_memory_budget_bytes`.
The quota and evaluation patches do not use this configuration key or change the migration runner.

### Upstream Functionality That Does Not Replace This Task

The v0.2.21 source does not define `quota_script`, `UpdateAPIKeyQuotaState`, or `codex_eval_inspection`.
It contains only an unrelated Ent schema field named `apikey_quota_quota_used` at `backend/ent/migrate/schema.go:85`.
The quota scheduling, identity CAS, probe memoization, and evaluation inspection patches remain required.

### Patch Application Check

The clean source at `/tmp/sub2api-v0.2.21-clean` came from the peeled v0.2.21 commit.
The check applied these patches in the same order as `scripts/build.py`:

1. `plugins/codex-candy-eval/patches/0001-evaluation-core.patch`
2. `plugins/codex-candy-eval/patches/0002-evaluation-data.patch`
3. `plugins/codex-candy-eval/patches/0003-vendor-assets.patch`
4. `plugins/codex-candy-eval/patches/0004-admin-channel.patch`
5. `plugins/codex-candy-eval/patches/0005-inspection.patch`
6. `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch`
7. `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch`
8. `plugins/sub2api-quota-extension/patches/quota-extension.patch`

`git apply` accepted every patch. Patch `0003` printed three existing trailing-whitespace warnings. It did not reject a hunk.
The final temporary tree passed `git diff --check`.

### Backend Verification

The patched v0.2.21 source passed:

```sh
go test ./internal/service ./internal/repository ./internal/handler/admin
```

The package results were `ok` for all three packages. The service package took 148.590 seconds.
The repository package took 9.689 seconds. The administrator handler package took 3.003 seconds.

The plugin-specific test entries were not copied into the temporary source during this research step.
Frontend dependencies were absent during this initial pass.
The later dependency report records a successful frozen install, Vue type check, and evaluation UI test.

## Required Version Updates

The parent build accepts an explicit upstream tag through `scripts/build.py:25-40`.
Patch application uses sorted plugin patches at `scripts/build.py:74-80`.
Run the full acceptance command with `UPSTREAM_TAG=v0.2.21`.

The following direct references need review before delivery:

- `plugins/codex-candy-eval/tests/native_inspection_fixture.py:48-51` hardcodes v0.2.20 executable names.
- `.trellis/spec/backend/index.md:6` names v0.2.20 as the verified baseline.
- `.trellis/spec/backend/api-key-quota.md:5` names v0.2.20 as the plugin baseline.

Installer fixture values such as `Candidate: "0.2.20"` in `tests/test_installer_test.go:661` test version-warning behavior.
Keep those values unless the installer contract itself changes.

## Smallest Adaptation Plan

1. Keep the existing quota and evaluation patch logic.
2. Update the inspection binary resolver where v0.2.21 execution needs it.
3. Reuse the v0.2.21 Antigravity force-query and account-refresh behavior.
4. Run the focused plugin Go, frontend, and UI tests against the v0.2.21 source.
5. Run `UPSTREAM_TAG=v0.2.21 python3 -B scripts/build.py` once.
6. Update active specifications with the verified v0.2.21 baseline.

## Related Specs

- `.trellis/spec/backend/index.md`
- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/native-inspection.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `plugins/sub2api-quota-extension/patches/quota-extension.patch`
- `plugins/codex-candy-eval/patches/0001-evaluation-core.patch` through `0007-sub2api-integration.patch`

## Caveats / Not Found

- No v0.2.21 patch conflict appeared in the clean application check.
- The full combined build was not run during research.
- Frontend dependency installation and Vue checks were absent from this initial pass. See the later dependency report for their results.
- The three whitespace warnings belong to the vendor-assets patch and did not stop application.
- Existing v0.2.20 research remains valid only for the v0.2.20 source. Do not use it as v0.2.21 runtime evidence.
