# Automatic Submodule Patch Build

## Goal

Automatically download Sub2API source, combine all plugin submodules, and build one server and installer through one command.

## Background

The source is `/Users/minami/Code/C/cpa-plugin-codex-candy-eval`.
Its seven-patch series builds Sub2API v0.2.17 for Linux/amd64 and packages a Go installer.
Nine integration insertions lack context and need normalization.
The original installer accepts installed v0.2.16/v0.2.17 and requires a v0.2.17 candidate.
The current project contains Trellis files but no product code or Git repository.

## Requirements

### R1. Migrate the build and installer to Sub2API v0.2.18

- Connect the evaluation repository as the Git submodule `plugins/codex-candy-eval`.
- Move common build and installer code into this project.
- Keep plugin patches, business tests, and licenses in plugin repositories.
- Preserve binary assets, frontend rebuilding, native server embedding, focused checks, and installer recovery.
- Download the target Sub2API release into a temporary workspace automatically.
- Target Sub2API v0.2.18 and adapt plugin patches, tests, and release metadata to that version.
- Compare installed and candidate versions with the build version from shared build metadata for advisory warnings.
- Read actual executable version records from successful version commands, including stdout and stderr.
- Normalize only an optional leading `v`. Compare the complete version token, including any prerelease or build suffix.
- Image tags such as `latest`, image labels, and stale source VERSION files must not determine the installed version.
- If a version differs or cannot be determined, warn and request explicit confirmation before backup or replacement.
- Show the build version, installed version, candidate version, and any probe errors in the warning.
- Continue only after an explicit `y` or `yes`. Empty input, refusal, EOF, or interruption cancels installation.
- Matching versions need no version warning or extra confirmation. The current build version is v0.2.18.
- Prepare frontend and Go dependencies automatically using their lockfiles and existing package caches.
- Require no local upstream source checkout or manual dependency installation before the build.
- Preserve existing local source checkouts and plugin worktrees during normal builds.
- Keep the original plugin checkout and standalone build entry usable.
- Use current submodule contents without fetching or updating them during a build.
- Detect uninitialized plugin submodules and report their initialization command.

### R2. Discover every plugin automatically

- Discover all plugin submodules under `plugins/` during each build.
- Use fixed directory conventions for patches, tests, and licenses.
- Include every discovered plugin in one combined source tree.
- Adding a submodule must require no build configuration or build-code change.
- Apply plugins in stable directory-name order and each plugin's top-level `patches/*.patch` files in lexical filename order.
- Remove `patches/series` from the migrated plugin.
- Keep all test cases, assertions, and test support code in each repository's flat `tests/` directory.
- Discover `test_*.py`, `test_*.go`, and native UI `test_*.cjs` files automatically. Require no separate check script or test manifest.
- Run Python and CJS tests directly with Python and Node. Preserve standalone Go program support through `go run`.
- Execute native `test_*_test.go` suites with `go test` in their target temporary packages, without exposing private production APIs.
- Use explicit package context in native Go test sources instead of a central package mapping.
- Sort inputs and execute native Go package groups deterministically. Run each discovered case once and stop on failure.
- The build supplies temporary source and module context. Test files contain the actual assertions instead of delegating to asset-based suites.
- Keep `assets/` for data resources such as golden JSON. Keep manual test fixture and support code under flat `tests/`.
- Automatic discovery selects only matching test files. Manual fixture helpers do not execute during a default build.
- Automatic tests run during the build. The installer performs installation and readiness checks without executing plugin test entries.
- Always run shared installer tests. Provide no test-skipping argument.
- A failed test stops the build and prevents publication of new outputs.
- Collect all discovered plugin licenses without filename collisions.
- Store each repository's own license in its root `LICENSE` file.
- Store original third-party license files under its `licenses/` directory. Remove `THIRD_PARTY_NOTICES.txt` from both repositories.
- Collect both inputs under installer resources `licenses/`, with separate plugin directories.
- Install frontend dependencies from the combined source's frozen lockfile in the temporary workspace.
- Build the combined frontend, server, and installer once.

### R3. Normalize patches and verify cooperation

- Use standard Git diffs with contextual existing-file edits and binary patch support.
- Normalize and adapt the series directly to v0.2.18.
- Preserve plugin behavior and binary assets during the v0.2.18 adaptation.
- Preserve normal new-file, whole-file deletion, and binary representations.
- Keep shared routes, menus, startup, and shutdown changes in their owning plugin patches.
- Allow multiple plugins to edit a shared file when contextual changes cooperate in discovery order.
- Apply every patch against the evolving combined tree.
- Patch application failure means build failure, with a nonzero exit status.
- Report the plugin, patch, and actual error.
- Stop all later patches, checks, compilation, and packaging after a patch failure.
- Do not skip, reverse, auto-merge, partially apply, or weaken context requirements.

## Scope

Deliver migration and automatic multi-plugin composition together.
Use `https://github.com/Nanboom233/codex-candy-eval` as the first real plugin.
Upgrade Sub2API to v0.2.18 and keep the Linux/amd64 platform target.

## Out of Scope

Plugin registration, selection, enable/disable controls, dependency resolution, and central plugin configuration are excluded.
Runtime plugin loading, marketplaces, additional target platforms, and evaluation behavior changes are excluded.
Production installation is separate from building and checking the installer.

## Acceptance Criteria

The groups below retain the previous AC identifiers for traceability. Grouped identifiers share evidence and do not require separate tests.

- [x] AC1, AC8, AC9, AC10, AC12, AC13, AC14: The argument-free build downloads v0.2.18 and prepares dependencies.
  It includes every discovered plugin submodule.
  It produces one combined server and installer. An uninitialized submodule reports its initialization command.
- [x] AC2, AC16, AC17, AC19, AC28: Standard contextual patches preserve plugin behavior and binary assets on v0.2.18.
  Lexical filename order replaces `series`. Compatible edits to one shared file preserve both plugins' changes.
- [x] AC6, AC7, AC18, AC20, AC21: Two fixture plugins prove deterministic composition and one packaging operation.
  Patch, source preparation, dependency, or test failure stops later operations and preserves previous outputs. Patch errors identify the plugin and patch.
- [x] AC4, AC29, AC30: All actual test cases, assertions, and support code live in flat `tests/`, including native Go and UI suites.
  Automatic discovery runs the sorted Python, Go, and CJS inputs with their native tools and stops on failure.
  Native Go suites retain private-package access and execute each discovered case once. Assets contain data only.
  Preserve relevant Go, vet, UI, and installer coverage while removing wrapper entries and duplicate suites.
- [x] AC3, AC5: Builds clean temporary workspaces and preserve local checkouts. The migrated plugin retains its standalone command interface.
- [x] AC11, AC15: Root `LICENSE` and original third-party `licenses/` files reach installer resources with complete text and no separate summary document.
  Plugin directories keep equal original filenames separate.
- [x] AC22, AC23, AC24, AC25, AC27: Actual executable versions determine advisory warnings, independent of image tags and labels.
  Matching versions need no version prompt. Mismatch or unresolved probes produce one warning and confirmation before backup, replacement, or restart.
  Only `y` or `yes` continues. Cancellation preserves staged-candidate cleanup.
- [x] AC26: One canonical v0.2.18 build value supplies server and installer metadata despite the stale upstream VERSION file.

## Verification Scope

Reuse existing tests for unchanged behavior. Add focused tests for discovery, patch cooperation, failure propagation, and version warnings.
Use one real v0.2.18 build as integration evidence. Do not repeat it for already covered cases.
The implementation plan defines the focused checks. Research examples do not create additional acceptance gates.
No v0.2.17 comparison build, fixed test-file count, flat-assets rule, or nonempty-patch requirement applies.
No fixture-destination scanner, full-suite matrix, or manual Docker or browser session is required.

## Evidence

- [Source build flow](./research/source-build-flow.md)
- [Patch composition findings](./research/multi-plugin-composition.md)
- [Installer version detection](./research/installer-version-detection.md)
- [Implementation result](./research/implementation-result.md)
- [Implementation check](./research/check-result.md)
