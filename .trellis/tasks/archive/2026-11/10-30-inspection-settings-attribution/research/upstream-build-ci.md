# Research: Upstream Sub2API build and CI organization

- Query: Determine whether per-architecture CI jobs add build capability or scheduling value, and inspect official Sub2API CI organization.
- Scope: External upstream source, official Go documentation, and local build implications.
- Date: 2026-11-05

## Findings

### Go target builds

Go can build supported targets from one host by setting `GOOS` and `GOARCH` and invoking `go build`. The official Go documentation lists these as target environment variables and says they identify the target rather than the build host.

One `go build` invocation emits one target executable. A script, GoReleaser, or CI matrix must still invoke builds for each target and collect the distinct outputs. Thus, the Go toolchain supports cross-compiling several platforms on one host, but it does not turn one `go build` invocation into several platform outputs.

At this workspace's Go `go1.27.2 darwin/arm64`, `go tool dist list` includes all five needed targets: Linux amd64/arm64, Darwin amd64/arm64, and Windows amd64. The upstream release configuration sets `CGO_ENABLED=0`, so its target builds do not require platform-specific C toolchains.

Official Go references:

- [Installing Go from source: GOOS and GOARCH](https://go.dev/doc/install/source#environment)
- [Go command build documentation](https://pkg.go.dev/cmd/go#hdr-Compile_packages_and_dependencies)

### Upstream v0.2.19 release workflow

The selected upstream tag is `v0.2.19`.
Its tag object is `e60cefeaf78f2fbfa95aa076029e28b40d0a5527` and its peeled commit is `dece26153621959ccd7635814f4b2d08304e681a`.
The tag is annotated. Consumers must dereference it before comparing a release tag with a source commit.

Files reviewed at that tag:

- [`.github/workflows/release.yml@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.github/workflows/release.yml): orchestrates source resolution, frontend build, binary target matrix, and final publication. Matrix and handoff lines are 36-81, 83-106, and 108-191.
- [`.goreleaser.yaml@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.goreleaser.yaml): defines Linux, Windows, and Darwin amd64/arm64 builds, excluding Windows arm64, plus Linux amd64/arm64 images. Build target lines are 9-32.
- [`release_matrix.py@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.github/release-tools/release_matrix.py): expands GoReleaser targets at lines 27-38, creates one-target configurations at lines 79-104, and validates per-target archives and provenance at lines 107-154.
- [`backend-ci.yml@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.github/workflows/backend-ci.yml): separates backend tests, frontend checks, lint, deployment shell tests, and release-tool tests from release building. Jobs are lines 10-95.
- [`Makefile@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/Makefile) and [`backend/Makefile@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/Makefile): provide local frontend/backend build and test commands. Backend build is lines 1-27.
- [`Dockerfile.goreleaser@v0.2.19`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/Dockerfile.goreleaser): packages prebuilt binaries and runtime resources. It does not compile Go.

The release workflow first resolves one tag, source commit, version, and matrix. A separate frontend job builds the frontend once and uploads its embedded distribution. One `build-binaries` matrix job runs per target on `ubuntu-latest`. Each downloads the same frontend and version inputs, configures Go for its target, restores a target-specific cache, creates a one-target GoReleaser config, and builds one archive with CGO disabled.

Each target job uploads one `release-binary-<os>-<arch>` artifact containing its archive and a manifest. The final release job downloads all target artifacts, verifies the exact expected set, source SHA, and archive checksums, then extracts Linux binaries to per-architecture contexts. Docker Buildx publishes the amd64/arm64 images and manifests. GoReleaser publishes the already-built binary archives and GitHub Release without recompiling them.

The target matrix therefore provides scheduling parallelism and isolates target work. It is not needed to make cross-compilation possible. Upstream uses intermediate artifacts because build and release occupy different runners, and because the release job needs all target archives together for completeness checks, Docker context creation, and publication.

The workflow uploads `release-tooling`, `version-file`, `frontend-dist`, and each `release-binary-*` artifact with one-day retention. Those are internal handoffs, not final products. Dry runs can also upload a diagnostic report. Upstream accepts visible intermediate artifacts as part of its matrix/release pipeline.

### Current default branch cross-check

The current default branch `main` preserves the same release graph, target matrix, target-specific cache, and artifact handoff.
The fetched current files confirm the same structure at [release.yml@main](https://github.com/Wei-Shaw/sub2api/blob/main/.github/workflows/release.yml) lines 36-81 and 108-191, [backend-ci.yml@main](https://github.com/Wei-Shaw/sub2api/blob/main/.github/workflows/backend-ci.yml) lines 10-95, and [release_matrix.py@main](https://github.com/Wei-Shaw/sub2api/blob/main/.github/release-tools/release_matrix.py) lines 27-154.
The material difference found in the release workflow is the frontend build Node version: v0.2.19 uses Node 20 at lines 93-97, while current `main` uses Node 24 at lines 93-97.
The current `.goreleaser.yaml` target set and the release helper are otherwise textually unchanged in the reviewed files.

### Separate validation CI

`backend-ci.yml` does not build a cross-architecture product matrix. It has independent jobs for shell scripts, Go unit/integration tests, frontend lint/type/critical tests, Go lint, and release-helper tests. This keeps validation separate from tagged release builds.

The workflow structure reflects distinct goals:

- Validation CI runs relevant suites by layer on suitable runners.
- Release CI performs reusable source/frontend preparation, then parallel target archive builds, then one aggregation/publication step.
- Buildx is for multi-platform container images, not required to produce the standalone Go executables.

## Implications for the plugin builder

The plugin builder does not need a matrix for cross-compilation. Its Go programs use `CGO_ENABLED=0` and its local entry already compiles each requested target from a common source tree. A single runner can emit all target outputs by invoking the existing build function once per target.

A matrix adds real wall-clock benefit only by assigning target invocations to concurrent runners. It also requires transferring the prepared patched source/frontend, installer inputs, and compiled payloads between runners. The upstream project explicitly accepts these intermediate artifacts and uses target manifests and a final aggregation check. The plugin project may reject that tradeoff because its required final run page should contain product downloads rather than build handoffs.

If the artifact list must contain only final products throughout, a single runner with cross-target Go builds is the direct fit. Keep preparation/tests once, loop over selected target pairs, build each server and installer, then upload the final pair only after the complete requested set succeeds. Any within-run parallelism would need to respect runner CPU/memory and avoid shared installer payload directories. Do not assume Go itself parallelizes different target outputs from one `go build` call.

The current artifact-per-target matrix has independent parallelism but produces visible internal artifacts. Upstream's pattern confirms those artifacts are a deliberate consequence of cross-job data handoff, not accidental packaging noise. Reducing them while keeping matrix execution requires a separate storage/cleanup policy or a changed job topology. A workflow-run cleanup is not part of the upstream pattern observed here.

## Caveats / Not Found

- The official workflow and supporting files were read from pinned `v0.2.19` and fetched again from the current `main` originals. Current-main details can change after this review.
- Go toolchain documentation establishes target support and environment semantics. It does not promise a wall-clock speedup for a particular single-runner loop or matrix. The parent separately measures local workflow timing.
- `go tool dist list` was read from local Go `1.27.2`; the upstream release checks for Go `1.27.3`. The five required target pairs are present in both the pinned Go command's documented supported set and local list.
- The tag is annotated. `git ls-remote --tags` returned tag object `e60cefe...` and peeled commit `dece261...`. The parent workflow must treat both forms correctly when checking source ownership.

## Related local files

- `scripts/build.py`: stages source, shared preparation, server builds, installer builds, and final output publication through the existing build entry.
- `.github/workflows/build.yml`: current internal artifact handoffs and target matrices.
- `.trellis/tasks/10-30-inspection-settings-attribution/research/ci-cache-matrix-result.md`: hosted run timings and artifact outcomes for the current workflow.
