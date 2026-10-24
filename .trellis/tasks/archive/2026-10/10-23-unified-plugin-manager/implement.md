# Automatic Build Implementation Plan

## Planning Gate

The user requires automatic discovery, normalized cooperative patches, and build failure on any patch failure.
Review the current plan before starting product implementation.
Validate task context manifests before `task.py start`.

## Work

1. Inspect current files and initialize the parent Git repository without a commit or remote.
2. Add the evaluation repository as `plugins/codex-candy-eval`.
3. Normalize its patch series in the new checkout for v0.2.18.
   Remove `patches/series` and preserve its order through lexical sorting of the existing numbered patch filenames.
   Inspect upstream v0.2.18 changes and adapt the normalized series and plugin tests while preserving plugin behavior and binary assets.
4. Migrate shared build code, the Go installer, and focused installer tests.
   Replace the common build's required source-path input with an automatic shallow checkout of upstream v0.2.18.
   Compare installed and candidate versions with the shared build version. Replace the allowlist with advisory warnings and explicit confirmation.
   Inject one canonical target version into both binaries instead of reading the stale upstream VERSION file.
   Replace substring matching with the researched version-record parser and dedicated command capture.
5. Discover all plugin submodules, top-level `patches/*.patch` files, executable Python and Go tests, and license inputs.
6. Keep all actual test cases, assertions, and support code in flat `tests/` directories.
   Discover Python, Go, and CJS inputs. Use native tools and exit status for success or failure.
   Refactor backend suites into direct `test_*_test.go` sources with explicit native package context.
   Stage and run native Go package groups deterministically, selecting each discovered case once. Preserve private upstream helpers.
   Move actual UI assertions into `tests/test_ui.cjs`. Remove the asset-based suite and Python wrapper.
   Keep manual container setup, supplier, and inspection preparation helpers in flat `tests/native_*` files and update their references.
   Keep installer assertions directly in main-repository `tests/test_installer_test.go`. Remove the duplicate plugin suite and wrapper.
   Keep `assets/` for data resources only. Do not embed old suites as source strings to simulate a refactor.
   Use no separate check script, mapping file, or test-command manifest.
   Adapt the new plugin worktree's standalone build and test references without changing its command interface.
   Always run discovered plugin and shared tests. Provide no test-skipping argument.
7. Apply normalized patches in plugin-path and patch-filename order and stop the entire build on any patch failure.
8. Prepare dependencies from the patched source, rebuild the frontend and server, and package one installer with discovered licenses.
   Keep each repository's own license at root `LICENSE` and third-party texts under `licenses/`.
   Collect both inputs under installer resources `licenses/`. Remove `THIRD_PARTY_NOTICES.txt` and retain original license files.
9. Add the focused checks below. Reuse existing tests for unchanged behavior.
10. Run the real evaluation build, check the complete result, and update README and relevant specs.

One implementation agent owns the complete build migration and composition path, including adjacent submodule changes.
It must preserve unrelated edits and the original plugin checkout.
The check agent reviews the complete result and fixes in-scope defects.

## Validation

### Existing Coverage

Keep relevant focused backend Go tests, vet, UI checks, and installer transaction tests directly under flat `tests/`.
Consolidate duplicate tests during cleanup. File counts and fixture directory depth are not acceptance criteria.
Use existing installer fake-Docker tests for backup, replacement, readiness, restoration, interruption, and candidate cleanup.
Replace obsolete allowlist assertions with advisory-warning assertions instead of keeping both sets.

### Changed Behavior

| Check | Evidence |
| --- | --- |
| Automatic composition | Two fixture submodules prove discovery, path and filename order, compatible shared-file edits, and one combined packaging input. Use real Git apply. |
| Input conventions | The fixture covers uninitialized submodules and direct Python, Go, and CJS discovery. Check deterministic execution and once-only native test selection. |
| Failure propagation | One conflicting patch and one failed test prove stop behavior. Stub source and dependency command failures without network retries or extra builds. |
| Output handling | Reuse the failure fixtures to check previous-output preservation, workspace cleanup, and unchanged local checkouts. |
| Licenses | Adapt the existing inventory assertion to recursive inputs, complete text, and plugin namespaces with equal filenames. |
| Version parsing | Use the observed console record, both streams, optional `v`, exact tokens, misleading metadata, and unresolved or conflicting output. |
| Probe failures | Use focused command tests for nonzero exit and timeout. Both installed and candidate probes use the same tested helper. |
| Confirmation | Test the shared confirmation function once for accepted and canceled input. Cover `y`, `yes`, whitespace/case, empty input, refusal, EOF, and interruption. |
| Installer integration | A matching executable under a `latest` image needs no warning. A fixture with both probe warnings produces one prompt. |
| Installer decision | Reuse that warning fixture for explicit continuation and cancellation. Check transaction entry and cancellation before backup, replacement, or restart. |

Parser cases need no repeated installer transaction. Warning causes need no cross-product with confirmation inputs or both probe positions.
Research tables are reference evidence, not mandatory production test matrices.
Use ordinary Git, subprocess, and Go failures. Do not add a patch validator or fixture-destination scanner.

### Real Build

```sh
python3 scripts/build.py
```

Run the argument-free v0.2.18 build once. It executes the automatic test entries before publishing outputs.
Do not run the same entries separately as another acceptance gate.
Use its result for dependency preparation, plugin behavior, binary assets, native embedding, shared version metadata, and both Linux/amd64 outputs.
Reuse that evidence. Repeat a check only after a relevant change or failure invalidates it.
Manual Docker installation, browser checks, v0.2.17 comparison builds, and extra full-suite matrices are outside this validation scope.

## Delivery

Deliver the working build, submodule edits, installer, documentation, and acceptance evidence together.
Preserve previous successful outputs after a failed invocation.
Report any real build failure or uncommitted submodule changes that prevent a reproducible checkout.
Do not commit or push without the applicable authorization.

## Approved Test Refactor

On 2026-10-25, the user required actual tests under `tests/` and rejected the asset-suite wrapper design.
Apply this correction to backend, UI, installer, standalone-build, and documentation paths together.
Revalidate changed native test integration. Reuse prior frontend/server and unchanged installer transaction evidence where applicable.
The refactor passed the default build, focused pipeline tests, integration vet, and independent review.
The commit inventory now lists the native test paths.
