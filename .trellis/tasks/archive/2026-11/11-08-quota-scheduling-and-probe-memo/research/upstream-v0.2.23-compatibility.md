# Research: Sub2API v0.2.23 Plugin Compatibility

- Query: Assess the Sub2API v0.2.21 to v0.2.23 upgrade for both production plugins.
- Scope: Phase 1.2 source research, temporary patch application, and baseline inventory.
- Date: 2026-11-18

## Upstream Tags

The upstream repository is `https://github.com/Wei-Shaw/sub2api.git`.
The existing local clone is `/tmp/sub2api-v0.2.23-research`.
It had no tracked or untracked changes before this research.
All upstream source anchors refer to its `v0.2.23` tree unless another tag appears.

| Tag | Tag object | Peeled commit | Date |
| --- | --- | --- | --- |
| `v0.2.21` | `43f15294c477bec427d586ddfc3f918ce1284c98` | `10ba8f9b4dc2e6023d4a9879ab77b21841babd10` | 2026-11-11 |
| `v0.2.22` | `b11573c9d55d39b6780e1e9f6e193ba2e6ca2321` | `b0fa9f3e6eeab1968a53e1289b69daa4bb40ca2b` | 2026-11-17 |
| `v0.2.23` | `ce19a640eab5c4b5ef1827c7c1fcfce49569411a` | `5af9afb588c4b014b3df9db7d4073af1f8ae01b6` | 2026-11-18 |

`git for-each-ref` confirmed that all three tags are annotated objects.
It also confirmed their peeled commit IDs and these timestamps.

| Tag | Tagger timestamp | Commit timestamp | `backend/cmd/server/VERSION:1` |
| --- | --- | --- | --- |
| `v0.2.21` | `2026-11-11T10:14:17+08:00` | `2026-11-11T09:37:34+08:00` | `0.2.20` |
| `v0.2.22` | `2026-11-17T10:40:35+08:00` | `2026-11-17T10:13:23+08:00` | `0.2.21` |
| `v0.2.23` | `2026-11-18T11:43:54+08:00` | `2026-11-18T11:40:09+08:00` | `0.2.22` |

`git show <tag>:backend/cmd/server/VERSION` confirmed each embedded version.
The parent sets the server version from the selected tag at `scripts/build.py:197`.
It sets the installer version from that tag at `scripts/build.py:243`.
The old embedded version therefore does not require an upstream source edit.

| Comparison | Files | Insertions | Deletions |
| --- | ---: | ---: | ---: |
| `v0.2.21..v0.2.22` | 340 | 20,708 | 1,652 |
| `v0.2.22..v0.2.23` | 90 | 5,251 | 453 |
| `v0.2.21..v0.2.23` | 399 | 25,947 | 2,093 |

These counts come from `git diff --shortstat` for each tag pair.
The file counts overlap between releases.

## SQL Migrations and Ent Schema

| Release interval | New SQL migration | Effect and source anchor |
| --- | --- | --- |
| `v0.2.21..v0.2.22` | `251_group_force_openai_ultrafast.sql` | Adds `groups.force_openai_ultrafast`, Boolean false. See `backend/migrations/251_group_force_openai_ultrafast.sql:1`. |
| `v0.2.21..v0.2.22` | `251_group_usage_rollup_nonblocking_build.sql` | Adds rollup expiration and build markers. See `backend/migrations/251_group_usage_rollup_nonblocking_build.sql:8`. |
| `v0.2.22..v0.2.23` | `252_channel_pricing_ultrafast_multiplier.sql` | Adds a nullable positive channel multiplier. See `backend/migrations/252_channel_pricing_ultrafast_multiplier.sql:1`. |

The rollup migration also replaces invalidation functions at `backend/migrations/251_group_usage_rollup_nonblocking_build.sql:20`.
Its upstream cause is commit `829bf2cd`.
The group option comes from commits `33019832` and `ad9eeede`.
The channel multiplier comes from commit `b36cb244`.
Both `251` filenames are distinct migration identities.
The runner sorts complete filenames at `backend/internal/repository/migrations_runner.go:178`.

The only changed Ent schema owner is `backend/ent/schema/group.go:256`.
It adds `force_openai_ultrafast` with default false.
The generated schema adds the matching column at `backend/ent/migrate/schema.go:960`.
Generated changes also affect `group.go`, `group/group.go`, `group/where.go`, `group_create.go`, and `group_update.go` under `backend/ent/`.
They also affect `backend/ent/mutation.go` and `backend/ent/runtime/runtime.go`.
There are no Ent changes from `v0.2.22` to `v0.2.23`.

No changed SQL migration or Ent schema alters `accounts`.
The upstream search found no `quota_script`, `UpdateAPIKeyQuotaState`, `apikey_usage_unsupported_identity`, or `codex_eval_inspection` implementation.
The plugins still own these task behaviors.

## Toolchain and Dependency Changes

| File | Change from `v0.2.21` to `v0.2.23` | Plugin impact |
| --- | --- | --- |
| `backend/go.mod` | `go 1.27.3` becomes `go 1.27.4`. `jsonschema-go v0.4.2` moves to direct `require`. | Update `quota-extension.patch` context and CI `go-version` to `1.27.4`. |
| `backend/go.sum` | None | Keep existing Goja and `regexp2/v2 v2.8.1` checksum entries. |
| `frontend/package.json` | None | Keep existing Vue, Vitest, and `jsdom` expectations. |
| `frontend/pnpm-lock.yaml` | None | Keep the existing frozen lockfile flow with `pnpm@12.16.1`. |
| `Dockerfile` | `golang:1.27.3-alpine` becomes `golang:1.27.4-alpine`. | Align `.github/workflows/build.yml` `go-version` with `1.27.4`. |

See [dependency checks](./upstream-v0.2.23-dependencies.md) for exact upstream commits, selected modules, and executable evidence.

## Patch Application Results

Clean upstream `v0.2.23` source lives in `/tmp/sub2api-v0.2.23-research`.

The checks used three independent local clones of the peeled `v0.2.23` commit.
Their names were `/tmp/sub2api-v0.2.23-matrix-eval`, `/tmp/sub2api-v0.2.23-matrix-quota`, and `/tmp/sub2api-v0.2.23-matrix-combined`.
Each clone used the current workspace patch contents, including the existing staged task work.
No workspace patch or Git index changed.

The build sorts plugin paths at `scripts/build.py:67`.
It skips empty patch sets at `scripts/build.py:71`.
It applies each plugin's sorted patches with `git apply --binary` at `scripts/build.py:74`.
Thus, evaluation patches `0001` through `0007` precede the quota patch.
The template has no production patch and does not enter this sequence.

| Configuration | `git apply --binary` result | Rejected hunks | `git diff --check` |
| --- | --- | --- | --- |
| Evaluation standalone | Exit 0 for `0001` through `0007` | None | Exit 0 |
| Quota standalone | Exit 1 | `backend/go.mod` hunk 4 and `AccountUsageCell.vue` hunk 3 | Exit 0 on the unchanged tree |
| Evaluation then quota | Evaluation exits 0. Quota exits 1. | The same two quota hunks | Exit 0 on the evaluation tree |

Ordinary `git apply` leaves the failed quota patch unapplied.
The next diagnostic pass used `git apply --binary --reject` in both quota configurations.
Each pass produced exactly `backend/go.mod.rej` and `frontend/src/components/account/AccountUsageCell.vue.rej`.
All remaining hunks applied, including the shared route and account-service hunks.
Both partial diagnostic trees passed `git diff --check` with exit 0.
A whitespace check on a partial tree does not establish complete patch acceptance.

The evaluation vendor patch prints three existing whitespace warnings at `0003-vendor-assets.patch:238`, `:290`, and `:354`.
They do not reject application.
`git diff --check` examines tracked changes and does not inspect new untracked vendor files.

## Quota Plugin Conflicts and TypeScript Intersection

### Rejected hunks

1. `backend/go.mod` Hunk #4 (`v0.2.23` lines `132-136`):
   Context expected `github.com/google/jsonschema-go v0.4.2 // indirect` before `github.com/google/pprof`.
   Upstream moved `jsonschema-go v0.4.2` to the direct `require` block at line `26`.
2. `frontend/src/components/account/AccountUsageCell.vue` Hunk #3 (`v0.2.23` lines `769-780`):
   Context expected `import { formatCompactNumber } from '@/utils/format'`.
   Upstream commit `e6774625` added `formatDateTime` to that import on line `774`.

### Required TypeScript adjustment in `AccountUsageCell.vue`

Quota Hunk #4 changes `_usageCache` (`AccountUsageCell.vue:793`) to `Map<number, { data: AccountUsageInfo; ts: number; config: string }>`.
Upstream commit `e6774625` added `_usageCache.set(accountID, { data: result, ts: Date.now() })` inside `loadActiveUsage` (`AccountUsageCell.vue:1659`).
Without `config`, `vue-tsc` fails during `pnpm build` because `config` is missing from the cache value.
`loadActiveUsage` must read `const config = apiKeyUsageRefreshKey.value` and pass `config` to `_usageCache.set`.

### Semantic and interface checks

Clean application alone does not establish semantic compatibility.
The [conflict report](./upstream-v0.2.23-conflicts.md) audits all requested shared owners and standalone Go compilation.
The [dependency report](./upstream-v0.2.23-dependencies.md) records frontend type checks and embedded UI results.
The [model-default report](./codex-eval-model-control-defaults.md) audits backend, UI, tests, specs, and upstream catalogs.

## Version Reference Audit

The inventory searched the parent, all three plugins, current specs, scripts, tests, and hidden workflow files.
It excluded Git internals and historical task and journal records.
These production references must move to `v0.2.23` and Go `1.27.4`:

- `.github/workflows/build.yml:11` and `:73`
- `plugins/codex-candy-eval/.github/workflows/build.yml:11` and `:73`
- `plugins/sub2api-quota-extension/.github/workflows/build.yml:11` and `:73`
- `README.md:21`, `:23`, `:27`, `:28`, `:29`, `:30`, `:31`, `:38`, `:39`, `:45`, `:123`
- `plugins/codex-candy-eval/tests/native_inspection_fixture.py:48`, `:49`, `:50`, `:51`
- `.trellis/spec/backend/index.md:6`
- `.trellis/spec/backend/api-key-quota.md:5`
- `.trellis/spec/backend/runtime-installation.md:5`
- `.trellis/spec/backend/quality-guidelines.md:7`
- `.trellis/spec/backend/minimal-linux-delivery.md:6`, `:16`, `:17`, `:35`, `:42`, `:77`, `:315`, `:359`

The three production workflows currently use `v0.2.21` at line 11 and Go `1.27.3` at line 73.
All listed documentation and binary fallback references currently use `v0.2.21`.
The delivery spec's line 77 must describe embedded version `0.2.22` on the new baseline.

All four workflow cache keys use `steps.go.outputs.go-version` at lines 112 and 114.
These expressions follow the selected toolchain and contain no baseline literal.
Their setup steps retain `id: go` at line 71.
All four workflows select Node `26.13.0` at line 78 and Corepack `0.36.0` at line 81.
All four build scripts pin `pnpm@12.16.1` at line 20.

All four build scripts resolve the latest release when `UPSTREAM_TAG` is empty at `scripts/build.py:25`.
Workflow defaults do not replace that existing behavior.
The parent passes the manual input to the source stage at `.github/workflows/build.yml:87`.

Intentional fixtures that must stay unchanged:

- `tests/test_installer_test.go:661` (`Candidate: "0.2.20"` version-warning fixture)
- `plugins/codex-candy-eval/tests/test_installer_test.go:661` (the same intentional fixture)
- `plugins/sub2api-quota-extension/tests/test_installer_test.go:661` (the same intentional fixture)
- `plugins/sub2api-plugin-template/tests/test_installer_test.go:661` (the same intentional fixture)
- Historical task and journal records under `.trellis/tasks/` and `.trellis/workspace/`

The template workflow uses `v0.2.20` at `plugins/sub2api-plugin-template/.github/workflows/build.yml:11`.
It uses Go `1.27.3` at line 73.
Its active local-build example uses `v0.2.20` at `plugins/sub2api-plugin-template/README.md:17`.
These references remain outside this delivery under the PRD's template exclusion.
Combined builds skip the template's empty patch set.

## Verification Boundary

Use `v0.2.23` as the next delivery baseline with Go `1.27.4`.
The evaluation patches apply directly.
The quota patch needs two context repairs and one cache-value type repair.
The companion reports contain standalone compilation, module resolution, frontend types, and model-default evidence.
The full ten-artifact build remains an implementation acceptance step.
Prior `v0.2.21` logs retain their original source and behavior scope.

The repaired temporary sources passed standalone and combined Go package compilation with the upstream `1.27.4` directive.
Readonly module selection and tokenizer tests passed with `regexp2/v2 v2.8.1`.
The frozen frontend install reused 984 packages and downloaded none.
The repaired combined source passed `vue-tsc --noEmit` and the evaluation embedded UI suite.
These results verify the temporary repairs described in the companion reports.
The workspace production patches still require those repairs.

`gpt-6.1-terra` already appears in the default removal list.
The model-control change only needs to append the missing `gpt-6.2-sol` and update its test and spec owners.
Absent settings must retain defaults, while an explicit `[]` must stay empty.

The research used local upstream source and required no GitHub credentials.
The three matrix clones moved to macOS Trash after the checks.
The cleanup hook required Trash instead of direct deletion.
The original clean upstream clone remains available.
Final parent and submodule status entries match the initial production-file status entries.
The existing staged diff counts also match the initial counts.
Only the four authorized research reports changed in the workspace during this research.
