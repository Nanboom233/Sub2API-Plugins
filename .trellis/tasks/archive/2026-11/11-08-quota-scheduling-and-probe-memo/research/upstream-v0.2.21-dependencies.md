# Research: Dependencies for Both Plugins on Sub2API v0.2.21

Date: 2026-11-13.
Scope: `codex-candy-eval`, `sub2api-quota-extension`, and their shared upstream build dependencies.

## Upstream Dependency Changes

The source comparison uses `v0.2.20` and `v0.2.21` in `/tmp/sub2api-v0.2.21-research`.
The combined patched source is `/tmp/sub2api-v0.2.21-clean`.

| File | Change between upstream tags | Effect on both plugins |
| --- | --- | --- |
| `backend/go.mod` | None | Upstream module requirements and Go version remain unchanged. |
| `backend/go.sum` | Eight added lines for four existing module versions | Preserve these entries when applying the quota module patch. |
| `frontend/package.json` | None | No upstream npm requirement changes. |
| `frontend/pnpm-lock.yaml` | None | Preserve the existing version 9 lockfile. |
| `Dockerfile` | None | Upstream build images and pnpm 9 remain unchanged. |

The added `go.sum` entries cover `go-runewidth v0.0.15`, `tablewriter v0.0.5`, `uniseg v0.2.0`, and `cobra v1.7.0`.
Each version already appears in the upstream selected module graph. These entries do not introduce four new direct requirements.

## Quota Plugin

The quota patch changes `backend/go.mod` and `backend/go.sum`.
See `plugins/sub2api-quota-extension/patches/quota-extension.patch:14` and `:51`.

| Module | Upstream v0.2.21 | Quota plugin selection | Reason |
| --- | --- | --- | --- |
| `github.com/dop251/goja` | Absent | `v0.0.0-20261024144015-2a9269b6b6de` | Execute `quota_script` inside Go. |
| `github.com/dlclark/regexp2/v2` | `v2.1.0` | `v2.8.1` | Goja requires this version. |
| `github.com/go-sourcemap/sourcemap` | Absent | `v2.1.3+incompatible` | Goja dependency. |
| `github.com/google/pprof` | Selected transitively | Same `v0.0.0-20250317173921-a4b03ec1a45e` | The patch adds an indirect requirement without changing its selected version. |
| `golang.org/x/text` | `v0.43.0` | Same `v0.43.0` | Already satisfies Goja. |

The shared dependency is `regexp2/v2`.
`github.com/tiktoken-go/tokenizer v0.8.0` requires `v2.1.0`, while Goja requires `v2.8.1`.
Go selects `v2.8.1` for both callers. This is a shared version upgrade, not a module resolution failure.

Commands in the patched backend confirmed the selected graph with `GOFLAGS=-mod=readonly`:

```sh
go list -m github.com/dop251/goja github.com/dlclark/regexp2/v2 github.com/go-sourcemap/sourcemap github.com/google/pprof
go mod graph
go test github.com/tiktoken-go/tokenizer
```

The tokenizer test passed in 2.156 seconds against the selected `regexp2/v2 v2.8.1`.
The prior patched service and repository tests also passed.
These results support retaining the current Goja and regexp2 requirements.

The graph includes `goja_nodejs`, `semver`, and `go-yaml` through Goja command or test dependencies.
`go list -deps ./internal/codexeval ./internal/service` excludes these three modules from the application package dependency list.
The quota script runs inside Goja. It does not require a Node.js runtime on the deployed server.

The quota frontend imports existing Vue and vue-i18n packages.
Its tests use the upstream Vitest and Vue Test Utils packages.
The plugin adds no npm requirement or lockfile change.
See `quota-extension.patch:2343`, `tests/test_quota_editor.test.ts:1`, and `tests/test_usage_cell.test.ts:1`.

The service also requires native `HTTPUpstream` and `*config.Config` injection.
The patch updates both `service/wire.go` and generated `cmd/server/wire_gen.go`.
See `quota-extension.patch:1` and `:1980`.
Keep these changes together. Omitting the provider change removes the configured transport needed for quota HTTP requests.

## Evaluation Plugin

None of its seven patches modifies `go.mod`, `go.sum`, `package.json`, or the frontend lockfile.
Its Go services reuse upstream packages. Its embedded page uses resources included by the vendor-assets patch.

| Dependency | Source | Required action for v0.2.21 |
| --- | --- | --- |
| `markdown-it 15.0.2` | Embedded `web/vendor/markdown-it.min.js` | Keep the bundled resource. |
| `markdown-it-cjk-friendly 3.0.0` | Embedded vendor script | Keep the bundled resource. |
| `texmath` | Embedded `web/vendor/texmath.js` | Keep the bundled resource. |
| `Temml 0.13.5` | Embedded script, CSS, and inlined font | Keep the bundled resources. |
| Vue and vue-i18n | Existing upstream frontend packages | No version change. |
| `jsdom 24.1.3` | Existing upstream development dependency | Install frontend dependencies before the embedded-page test. |

The embed declarations are in patched `backend/internal/codexeval/web.go:21` through `:34`.
Vendor file headers identify their versions.
`plugins/codex-candy-eval/tests/test_ui.cjs:7` resolves jsdom from the downloaded frontend package.
No CDN or separate npm install is required to serve these embedded page resources.

## Shared Toolchain and Frontend Resolution

Upstream requires Go `1.27.3` in `backend/go.mod:3`.
Goja requires Go `1.26.0`, which is below the upstream requirement.
The shell reports Go `1.27.2`, but `go env GOVERSION` inside the module reports `go1.27.3` with `GOTOOLCHAIN=auto`.

Both standalone build kits pin `pnpm@12.16.1` and installer dependency `pterm@v0.12.84`.
See each plugin's `scripts/build.py:20` and `:22`.
The CI workflows select Go `1.27.3`, Node `26.13.0`, and Corepack `0.36.0`.
The local dependency check used Node `24.21.0` and Corepack `0.36.0`.

The upstream Dockerfile uses pnpm 9. The plugin build already adapts pnpm 12 configuration before installing dependencies.
It copies upstream overrides into `pnpm-workspace.yaml` and enables dependency scripts.
See parent `scripts/build.py:213` through `:224`.
Both standalone build scripts use the same preparation logic.

Using that existing configuration, the following command passed in the temporary combined frontend:

```sh
COREPACK_ENABLE_AUTO_PIN=0 COREPACK_ENABLE_PROJECT_SPEC=0 corepack pnpm@12.16.1 install --frozen-lockfile
```

The installer reused 984 packages and completed in 24.7 seconds.
`git diff -- frontend/package.json frontend/pnpm-lock.yaml` remained empty.
The pnpm warning about `package.json` overrides does not lose overrides because the build supplies their workspace equivalent.

## Checks That Resolve Dependency Questions

| Check | Result | Evidence boundary |
| --- | --- | --- |
| Readonly Go module selection | Pass | No module manifest update required to resolve the combined source. |
| Upstream tokenizer tests with regexp2 2.8.1 | Pass | Checks the caller affected by the shared version upgrade. |
| Frozen frontend dependency install | Pass | Existing manifests and lockfile resolve with the actual pinned pnpm version. |
| `pnpm exec vue-tsc --noEmit` | Pass | Both plugins' frontend imports and native types compile in the combined source. |
| Evaluation `node tests/test_ui.cjs` | Pass | Bundled JS resources and upstream jsdom work together. |

The full product build and quota Vue behavior suites remain implementation acceptance checks.
Dependency resolution and type checks do not replace those behavior checks.

## Decision

Retain both plugins' current dependency versions and the existing pnpm preparation step.
No upstream v0.2.21 dependency change requires a new adapter, npm package, or toolchain upgrade.
Keep the quota Goja module changes, HTTP provider injection, and generated Wire call together.
Keep evaluation vendor resources and the upstream jsdom development dependency available to their existing consumers.
