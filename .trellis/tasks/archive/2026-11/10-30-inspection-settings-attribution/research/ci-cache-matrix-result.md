# CI cache, matrix, and Release implementation

## Build stages

The four kits share the same builder, workflow, and affected existing builder tests.
The default `python3 scripts/build.py` invocation still builds every platform through the same phase functions.
CI resumes those functions through `SUB2API_BUILD_STAGE`, `SUB2API_BUILD_WORKSPACE`, and `SUB2API_BUILD_TARGET`.
`SUB2API_BUILD_PLATFORMS` selects the final platform pairs.

Source resolves the upstream tag once, clones its exact tag, applies patches, and exports the matrices and selection.
Prepare builds the frontend, runs plugin checks and vet, and prepares installer dependencies and original licenses.
It compiles Linux/amd64 for the common tests and also supplies the local host's Linux architecture when necessary.
This preserves the existing Darwin/arm64 local test requirement.
Common tests run once. Remaining server and selected installer jobs perform compilation only.

The server matrix contains selected native targets and required Linux payloads, excluding servers already prepared for common tests.
The installer matrix contains only the selected final platforms.
Only Linux/amd64 selection skips the server job intentionally on the CI host.
Explicit native job-result conditions permit that skip and reject failures, cancellations, and unexpected skips.

## Handoffs and publication

Standard internal Actions artifacts transfer the prepared backend, installer sources and license resources, and uniquely named server and installer files.
The prepared handoff includes the frontend output inside the backend.
It excludes the source repository metadata, frontend dependencies, and prepared installer payload directory.
Each installer reconstructs only its native and matching Linux payloads in its own job workspace.

Publish assembles the expected selected pairs through the existing builder entry and atomic directory replacement.
Normal file-copy failures reject missing expected files before final publication.
It restores executable permissions for downloaded program data.
Native `upload-artifact` missing-file errors own artifact failures.
The workflow has no separate output-validation loop, repeated executable-mode check, or custom upload-status aggregation.
It creates no product tar file or output manifest.

## Cache ownership

Prepare restores caches after source download, using the actual upstream sums and frontend lockfile.
Tool commands supply the Go module, Go compilation, and selected pnpm store paths.
Only prepare saves module and pnpm caches.
Each target and role owns a distinct Go compilation cache key.
Save steps use each restore action's primary-key output after successful work and an exact-key miss.
Matrix jobs download prepared inputs before reading cache dependency keys.
Cache hits retain normal installation, tests, and compilation.

Cache actions use exact `v6.1.0` restore/save references.
Artifact download uses `v8.0.2`, and upload retains `v7.0.2`.
Other approved Action and tool versions remain unchanged.

## Inputs and optional Release

Manual inputs retain editable upstream tag `v0.2.19`, five enabled platform booleans, and a disabled Release switch.
An empty platform selection fails before source download.
Manual Release publication requires a separate nonempty plugin Release tag.
Branch and pull-request builds select all platforms and resolve the upstream's latest official release tag.
Pushed `v*` repository tags select all platforms and enable publication to that plugin tag.

Only the downstream Release job has `contents: write` and the built-in job token.
It downloads the exact successful direct product artifacts from the same run.
An existing Release tag must identify the built source commit after any annotated-tag dereference.
The job never moves a tag or updates an existing Release.
Native `gh release create` reports existing Releases and publication failures.

The title is `Sub2API-Plugin <first-seven-source-commit-characters> (v<canonical-upstream-version>)`.
The CLI receives `--generate-notes` without custom notes or a notes file.
The workflow retains concise stage-specific failure artifacts and summaries without replaying log bodies.

## Verification and limits

`PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_build.py` passed the four existing cases in 11.066 seconds.
The composition case covers staged backend-only handoff, Darwin/arm64 plus its Linux payload closure, deferred publication, and checks once.
The standalone case covers only Linux/amd64 and the intentionally empty remaining server matrix.
The existing cases also cover the default argument-free dispatch and preserved previous outputs after compilation or missing-output failures.
No new test suite, cache test, workflow-text test, or runtime matrix was added.

The workflow YAML and every inline Bash block parse successfully.
Direct comparison confirms identical builders, workflows, builder suites, and unchanged test support across the four kits.
Diff formatting checks pass in all four repositories.
The affected script and test directories contain no generated Python or test caches.

No new product build or remote workflow ran during local implementation.
Earlier successful runtime, platform, license, and direct-artifact evidence remains applicable to unchanged behavior.
An asset-upload failure can leave a partial GitHub draft. Native CLI failure reporting preserves the successful Actions products.

## Hosted trace after publication

The approved commits reached all four remote main branches on 2026-11-05.

| Repository | Commit | Run | Result | Elapsed |
| --- | --- | --- | --- | --- |
| Main | `3a5f9f2` | [41956595900](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/41956595900) | Success | 16m06s |
| Eval | `62b615c` | [41956522478](https://github.com/Nanboom233/codex-candy-eval/actions/runs/41956522478) | Success | 14m08s |
| Quota | `f75831f` | [41956544123](https://github.com/Nanboom233/sub2api-quota-extension/actions/runs/41956544123) | Failure | 8m12s |
| Template | `b7389ab` | [41956569984](https://github.com/Nanboom233/sub2api-plugin-template/actions/runs/41956569984) | Success | 11m55s |

Elapsed values use run creation and final update timestamps.
Each successful run published ten final product artifacts for the five selected platforms at upstream tag `v0.2.19`.
All four server targets and five installer targets passed in each successful run.
The branch pushes skipped Release publication as configured.
Actual Release creation and later-run cache reuse remain untested.

Prepare cache logs show initial misses and successful module, Go compilation, and pnpm saves.
The template server job restored module and preparation compilation caches in the same run.
Prepared source download and server-to-installer handoffs succeeded.
Internal handoff artifacts remain separate from the ten final products.

Quota plugin checks, vet, backend compilation, and the four builder tests passed.
The common installer test `TestInstallTransaction/restore-failure-keeps-path` then failed with `unexpected end of JSON input`.
The stack identifies `readState` at generated `test_installer_test.go:69`, called from line 429.
Downstream jobs skipped and no final product artifacts were published.
The run uploaded one `build-log-prepare` artifact for diagnosis.
Research found a truncation window in the shared JSON fixture writer that matches the hosted failure.
The user approved repair of the four aligned fixture copies with same-directory temporary writes and rename.
See [the state-file research](ci-quota-installer-state-race.md) for evidence and its limits.
The original helper reproduced the JSON panic under a temporary concurrent-reader probe. The fixed helper passed the same probe.
The existing seven transaction subcases and a killed-writer check passed. Independent Trellis review found no blocking issues.
The repair remains local until work-commit approval and publication.
