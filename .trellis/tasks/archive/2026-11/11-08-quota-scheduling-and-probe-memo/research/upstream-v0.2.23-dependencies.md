# Research: Dependencies for Both Plugins on Sub2API v0.2.23

- Query: Check dependency changes and both plugins against the v0.2.23 dependency graph.
- Scope: Phase 1.2 source comparison, readonly Go checks, frozen frontend installation, types, and embedded UI tests.
- Date: 2026-11-18

## Upstream dependency changes

The comparison uses the local clean source at `/tmp/sub2api-v0.2.23-research`.
The endpoints are `v0.2.21` (`10ba8f9b`) and `v0.2.23` (`5af9afb5`).
Source anchors in this section refer to clean v0.2.23.

The exact comparison command was:

```sh
git diff v0.2.21..v0.2.23 -- backend/go.mod backend/go.sum Dockerfile frontend/package.json frontend/pnpm-lock.yaml
```

The command exited 0.
Only `backend/go.mod` and `Dockerfile` contain changes.

| File | Exact change | Evidence |
| --- | --- | --- |
| `backend/go.mod` | `go 1.27.3` becomes `go 1.27.4` | `backend/go.mod:3` |
| `backend/go.mod` | `github.com/google/jsonschema-go v0.4.2` moves from indirect to direct requirements | `backend/go.mod:26` |
| `backend/go.sum` | No change | The tag comparison returns no hunk for this file. |
| `Dockerfile` | `ARG GOLANG_IMAGE=golang:1.27.3-alpine` becomes `ARG GOLANG_IMAGE=golang:1.27.4-alpine` | `Dockerfile:11` |
| `frontend/package.json` | No change | The tag comparison returns no hunk for this file. |
| `frontend/pnpm-lock.yaml` | No change | The tag comparison returns no hunk for this file. |

The module diff contains two added lines and two removed lines.
The Dockerfile diff contains one added line and one removed line.
The jsonschema version stays `v0.4.2`. Upstream changes its requirement class only.

Commit `e0cf4984f0d7c0d54ccb2d36292272a4231c07be` promotes jsonschema for OpenAI schema normalization tests.
Local blame attributes both Go version lines to shallow boundary commit `910d4d86b2c0d389f3201415123c386c98c6be2c`.
The local history cannot identify their original introduction commit beyond that boundary.

The Dockerfile retains Node `24-alpine` at `Dockerfile:10` and pnpm 9 preparation at `Dockerfile:29`.
The plugin build uses its own pinned pnpm version.
The upstream lockfile retains version `9.0` at `frontend/pnpm-lock.yaml:1`.

## Temporary combined source

Executable checks used `/tmp/sub2api-v0.2.23-deps-20261118-a`.
This tree contains both current workspace plugins on upstream commit `5af9afb5`.
The source contains only the required quota conflict repairs and the cache-value repair described below.

The module repair adds `google/pprof` while retaining upstream's direct jsonschema requirement.
The import repair retains `formatDateTime` and adds the quota imports.
The cache repair captures `const config = apiKeyUsageRefreshKey.value` before the active request.
It writes `{ data: result, ts: Date.now(), config }` in `loadActiveUsage`.
See temporary `frontend/src/components/account/AccountUsageCell.vue:1674` and `:1683`.

The [conflict report](./upstream-v0.2.23-conflicts.md) records the production patch changes required for these repairs.
These checks used the existing patches. They did not add the planned `gpt-6.2-sol` default.

## Go module selection

The quota patch owns all additional module requirements.
See `plugins/sub2api-quota-extension/patches/quota-extension.patch:14` and `:51`.
The evaluation patch set changes no module or npm manifest.

| Module | Upstream v0.2.23 | Selected combined version | Purpose |
| --- | --- | --- | --- |
| `github.com/dop251/goja` | Absent | `v0.0.0-20261024144015-2a9269b6b6de` | Execute quota JavaScript inside Go. |
| `github.com/dlclark/regexp2/v2` | `v2.1.0` indirect | `v2.8.1` | Satisfy Goja while retaining tokenizer compatibility. |
| `github.com/go-sourcemap/sourcemap` | Absent | `v2.1.3+incompatible` | Supply Goja source maps. |
| `github.com/google/pprof` | Transitive | `v0.0.0-20250317173921-a4b03ec1a45e` | Retain the existing selected version as an indirect requirement. |

The temporary combined `backend/go.mod` records these entries at lines `22`, `110`, `128`, and `136`.
The patch adds six checksum lines for Goja, regexp2, and sourcemap.
It retains existing regexp2 `v2.1.0` checksums and upstream pprof checksums.
No new pprof checksum is required.

Goja requires Go `1.26.0`, below upstream's Go `1.27.4` requirement.
Its cached `go.mod:7` requires regexp2 `v2.8.1`.
Tokenizer `v0.8.0` requires regexp2 `v2.1.0` at its cached `go.mod:7`.
Go selects `v2.8.1` for both callers.

The checks used `GOTOOLCHAIN=auto` and the host's normal caches:

```text
GOVERSION=go1.27.4
GOMODCACHE=/Volumes/User Data/caches/go/modules
GOCACHE=/Volumes/User Data/caches/go/build
```

The commands below ran from the temporary combined `backend/` directory.

```sh
GOTOOLCHAIN=auto GOFLAGS=-mod=readonly go list -m github.com/dop251/goja github.com/dlclark/regexp2/v2 github.com/go-sourcemap/sourcemap github.com/google/pprof
```

Exit result: `0`.
Output:

```text
github.com/dop251/goja v0.0.0-20261024144015-2a9269b6b6de
github.com/dlclark/regexp2/v2 v2.8.1
github.com/go-sourcemap/sourcemap v2.1.3+incompatible
github.com/google/pprof v0.0.0-20250317173921-a4b03ec1a45e
```

```sh
GOTOOLCHAIN=auto GOFLAGS=-mod=readonly go test github.com/tiktoken-go/tokenizer
```

Exit result: `0`.
Output: `ok github.com/tiktoken-go/tokenizer 0.638s`.
This test checks the existing caller affected by the shared regexp2 upgrade.
The commands required no module manifest repair beyond the stated quota conflict resolution.

The quota runtime imports Goja at temporary `backend/internal/service/account_quota_script.go:18`.
It does not require a deployed Node.js runtime.

## Provider injection

Quota HTTP requests still require native `HTTPUpstream` and `*config.Config` injection.
Temporary `backend/internal/service/wire.go:241` and `:242` declare both arguments.
Lines `258` and `259` store them on `AccountUsageService`.
The generated call supplies both arguments at temporary `backend/cmd/server/wire_gen.go:211`.

Upstream also adds `UsageBillingLaneCombiner` at temporary `backend/internal/service/wire.go:1000`.
The generated construction remains at temporary `backend/cmd/server/wire_gen.go:109`.
Retain this upstream provider when adapting the quota provider.
The two providers serve separate consumers and require no replacement module.

## Frontend preparation and frozen installation

All four build kits pin `pnpm@12.16.1` at `scripts/build.py:20` in their respective roots.
The parent preparation copies upstream overrides into `pnpm-workspace.yaml` at parent `scripts/build.py:213` through `:224`.
It also permits dependency scripts and disables strict peer checks.

The temporary frontend used this workspace file:

```json
{
  "overrides": {
    "js-cookie": "3.0.7",
    "form-data@<4.0.6": ">=4.0.6",
    "postcss@<8.5.18": ">=8.5.18",
    "dompurify@<3.4.17": ">=3.4.17",
    "source-map-js@<1.2.2": ">=1.2.2",
    "follow-redirects@<1.16.2": ">=1.16.2",
    "decode-uri-component@<0.5.1": ">=0.5.1"
  },
  "ignoreScripts": false,
  "dangerouslyAllowAllBuilds": true,
  "strictPeerDependencies": false
}
```

These overrides match upstream `frontend/package.json:64` through `:71`.
The checks used Node `v24.21.0`, Corepack `0.36.0`, and the normal pnpm store.
The store path was `/Users/minami/Library/pnpm/store/v11`.

The following commands ran from the temporary combined `frontend/` directory:

```sh
COREPACK_ENABLE_AUTO_PIN=0 COREPACK_ENABLE_PROJECT_SPEC=0 corepack prepare pnpm@12.16.1 --activate
COREPACK_ENABLE_AUTO_PIN=0 COREPACK_ENABLE_PROJECT_SPEC=0 corepack pnpm@12.16.1 install --frozen-lockfile
```

Both commands exited `0`.
Installation reused all 984 packages and downloaded none.
The installer completed in `39.5s`, including its lockfile policy check.
The vue-demi postinstall script completed successfully.

pnpm reports that it ignores `package.json`'s `pnpm.overrides` field.
The workspace file supplies the same overrides through the supported configuration path.
The install also printed slow registry request warnings and completed successfully.
The final diff for `frontend/package.json` and `frontend/pnpm-lock.yaml` was empty.

## Frontend types and evaluation UI

The type command ran from the temporary combined `frontend/` directory:

```sh
COREPACK_ENABLE_AUTO_PIN=0 COREPACK_ENABLE_PROJECT_SPEC=0 corepack pnpm@12.16.1 exec vue-tsc --noEmit
```

Exit result: `0`, with no diagnostics.
The `loadActiveUsage` cache repair therefore passes the requested combined type check.
Keep the upstream `formatDateTime` import and active-query behavior with that repair.

The evaluation suite ran from `plugins/codex-candy-eval/`:

```sh
SUB2API_SOURCE=/tmp/sub2api-v0.2.23-deps-20261118-a node tests/test_ui.cjs
```

Exit result: `0`.
The suite reported successful settings, account, manual-action, selection, history, SIWC, and inspection-control checks.
Its `createRequire` call loads jsdom from the combined frontend at `plugins/codex-candy-eval/tests/test_ui.cjs:7`.
The frozen installation selected `jsdom 24.1.3`, `vue-tsc 2.2.12`, and TypeScript `5.6.3`.
Upstream already declares these development dependencies at `frontend/package.json:54`, `:57`, and `:61`.

The evaluation UI test still uses the current five-item removal-list fixture at `tests/test_ui.cjs:19`.
The [model-default report](./codex-eval-model-control-defaults.md) records the required sixth item and its dependent assertions.

## Decision and acceptance boundary

Retain the existing plugin module versions, frontend dependencies, and pnpm preparation.
Use Go `1.27.4` for the v0.2.23 delivery.
Preserve upstream jsonschema's direct requirement and repair the quota patch context around it.
Keep the quota provider declaration and generated call together.

| Check | Exit result |
| --- | --- |
| Readonly combined module selection | `0` |
| Tokenizer tests against regexp2 `v2.8.1` | `0` |
| Pinned Corepack preparation | `0` |
| Frozen pnpm installation | `0` |
| Combined Vue type check after cache repair | `0` |
| Evaluation embedded UI suite | `0` |

The [conflict report](./upstream-v0.2.23-conflicts.md) records standalone and combined Go package compilation.
Implementation acceptance still requires the production patch repairs, model-default update, focused behavior suites, and full product build.

## Related specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/native-inspection.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/frontend/index.md`
- `.trellis/spec/guides/index.md`
