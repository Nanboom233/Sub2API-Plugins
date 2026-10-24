# Automatic Build Design

## Entry and Layout

```sh
git submodule update --init --recursive
python3 scripts/build.py
```

```text
plugins/<name>/patches/*.patch  Patches in lexical filename order
plugins/<name>/tests/test_*.py  Python test cases
plugins/<name>/tests/test_*.go  Native Go suites or standalone Go cases
plugins/<name>/tests/test_*.cjs Native UI test cases
plugins/<name>/assets/         Data resources only
plugins/<name>/LICENSE          Plugin license
plugins/<name>/licenses/        Original third-party license files
LICENSE                        Shared build and installer license
licenses/                      Original third-party license files, including Sub2API
scripts/build.py               Shared build entry
scripts/installer/             Shared Go installer
tests/test_build.py            Shared build test cases
tests/test_installer_test.go   Native installer transaction and version cases
dist/build/sub2api-plugins
dist/build/sub2api-plugins-installer
```

The build has no plugin registry, selection flag, enable state, or central plugin configuration.
The common build requires no operation arguments and downloads source automatically.
Every build runs tests. Provide no test-skipping argument.
Use Python standard-library code and Git rather than a plugin framework.
Use `plugins/codex-candy-eval` for the first plugin.

## Upstream Source

Use the existing upstream repository, `https://github.com/Wei-Shaw/sub2api.git`, and target tag `v0.2.18`.
Clone that tag with depth one into the build's temporary source directory.
Do not use the upstream default branch or infer the latest release.
Do not require or search for a local upstream checkout.
Apply plugin patches to this downloaded tree, then install its frontend dependencies with `pnpm install --frozen-lockfile`.
Use normal pnpm and Go caches. Let Go resolve downloads from the module files with readonly module behavior.
Keep pnpm 9.15.9 from the original release flow and prepare it before dependency installation.
The build host still supplies Python, Git, Go, Node.js, and Corepack.
Source download, dependency installation, patch, or check failure ends the build with a nonzero status.
Temporary workspace cleanup covers source preparation failures as well as later build failures.

## Discovery

Read native `.gitmodules` paths under `plugins/` and inspect their checked-out contents.
Include every plugin submodule, sorted by its relative directory path.
Apply discovered top-level `patches/*.patch` files in lexical filename order.
An absent or empty patches directory contributes no patches.
Keep the existing numbered filenames and remove `patches/series` from the migrated plugin.
Other plugins need no numeric filename prefix.
Report missing submodule contents instead of silently omitting a plugin.
Do not fetch, initialize, or update submodules during a build.
Add another plugin by adding its submodule with the same directory conventions.
Do not introduce another registration or ordering file.

Keep all actual test cases, assertions, and support code in flat `tests/` directories.
Discover `test_*.py`, `test_*.go`, and `test_*.cjs` inputs in lexical filename order.
Run Python and CJS cases directly with Python and Node. Retain `go run` for standalone Go programs.
Native Go files use `test_*_test.go` names and their real package declarations.
Their explicit package context identifies the native temporary package. Do not add a central mapping or command manifest.
Use `// sub2api-package: backend/internal/codexeval` for that backend package, or `// sub2api-package: installer` for installer tests.
Stage native test files into that package and run the discovered cases once with `go test`.
Order package groups by their first discovered file. Keep source-file order deterministic inside each group.
Use native upstream test helpers without adding public production test APIs.
Treat a nonzero command status, including compilation failure, as test failure and stop later tests and build operations.

Pass the combined source through the existing `SUB2API_SOURCE` environment variable. Disable Python bytecode files in repository test directories.
Pass each owning repository's data-only assets path through `SUB2API_ASSETS`.
Keep native execution support in flat `tests/support.py`. Build scripts supply source, installer, host environment, and command execution.
Run tests on the host platform. Apply Linux target variables only to product compilation commands.
A patch-only plugin can omit `tests/`. No separate `scripts/check.py` or test-command manifest exists.
Execute these entries during the build. The runtime installer performs installation and readiness checks without plugin test execution.

The evaluation plugin's native Go suites live directly in `tests/`, including algorithm, runtime, service, and administrator assertions.
Keep golden JSON under `assets/`. Test code supplies its data to the temporary native package as needed.
The runner supplies source/module context and focused vet. It does not conceal test suites in assets or source strings.
The UI assertions live directly in `tests/test_ui.cjs`, without a Python wrapper around an asset-based suite.

Keep manual native-container setup, supplier, and inspection preparation helpers in flat `tests/native_*` files.
Update their mutual references. These filenames remain outside automatic `test_*` discovery.
Preserve relevant backend, golden-data, UI, and installer transaction coverage. Test cleanup can consolidate duplicate assertions or fixtures.
Keep the original checkout unchanged and the new plugin worktree's standalone build usable after cleanup.

Discover the main repository's executable Python and Go test entries after installer staging.
Its `tests/test_installer_test.go` contains the actual native installer transaction and version assertions.
Pass the staging directory through `SUB2API_INSTALLER_SOURCE` for this internal test context.
Its Python test file contains build discovery, patch cooperation, and failure assertions.
Keep the authoritative installer suite in the parent repository and remove the duplicate plugin suite.
The plugin retains its own execution-support copy for independent standalone use. The common build uses the parent helper.

Discover each repository's root `LICENSE` and third-party texts under `licenses/`, without a license manifest.
Keep the plugin's own MIT license at `plugins/codex-candy-eval/LICENSE` without changing its text.
Copy each plugin's root license to installer resources `licenses/<plugin-directory>/LICENSE`.
Copy plugin license contents under installer resources `licenses/<plugin-directory>/`, preserving paths relative to the input `licenses/`.
Copy the main repository's root license to installer resources `licenses/LICENSE`.
Copy shared build and base Sub2API license inputs from the main repository's `licenses/` to installer resources `licenses/`.
Include the base Sub2API license and retain original copyright notices.
Adapt the existing installer test to verify the complete recursive inventory and actual contents.
Remove `THIRD_PARTY_NOTICES.txt` from both repositories. Use the original license files without a separate summary document.

## Build Flow

1. Discover plugin submodules, patch files, executable Python and Go test entries, and license inputs.
2. Report uninitialized submodules and download the target Sub2API source into a temporary workspace.
3. Apply every normalized patch to that evolving tree in plugin-path and patch-filename order.
4. Install frontend dependencies from the patched frozen lockfile and rebuild the combined frontend.
5. Execute discovered plugin test files against the combined source, including native tests, UI checks, and vet.
6. Compile one native embedded server for Linux/amd64 with CGO disabled.
7. Stage the compressed server, discovered license texts, and shared installer.
8. Run the main repository's discovered tests, including host installer transaction tests.
9. Compile the installer and publish outputs only after success.

Keep Go modules readonly.
A failed test returns nonzero and stops all later build operations.
Publish no new outputs after a failed test.
Do not add a general target configuration system.
Read toolchain requirements from the target release and preserve the established linker-based version metadata.
The v0.2.18 source VERSION file contains `0.2.17`. Derive canonical `0.2.18` from the selected tag instead.
Explicitly inject that value into both server and installer builds.

## Patch Contract

Generate standard Git diffs with repository-relative `a/` and `b/` paths.
Use normal contextual diffs for existing text files.
Retain standard file creation, whole-file deletion, and Git binary patch forms.
Keep binary bytes, line endings, patch boundaries, and the original patch order through numbered filenames.

Normalize the current evaluation series in the new submodule checkout as reviewed source changes.
Read both traditional unified and Git headers from the original series during this migration.
Normalize and adapt the series and plugin tests directly to v0.2.18.
Use the v0.2.18 upstream diff and combined tests to verify plugin integration and preserve binary assets.
Do not normalize patches silently during a build.

Use normal `git apply --binary`, without `--unidiff-zero`.
Use Git's context validation instead of a separate patch-format validator.
Multiple plugins may change one file when their contextual edits cooperate in discovery order.
Plugins maintain distinct feature names, routes, and metadata keys where integration requires them.
Do not infer registrations, generate menus, or add dependency resolution.
An invalid or conflicting patch returns nonzero with the plugin, patch, and actual error.
Run no later patch, check, compilation, or packaging after that failure.
Do not skip, reverse, partially apply, auto-merge, or retry with weaker context.

## Installer and Output

Reuse numbered container selection, ELF checks, backup, replacement, restart, and readiness handling.
Keep `/app/sub2api`, the 120-second readiness limit, and health/setup checks.
Preserve interrupted-installation and stopped-container restoration behavior.
Use generic completion text suitable for every automatically discovered plugin combination.
Each installer replaces the complete server.
Use discovered plugin paths in build progress without an inventory UI or embedded plugin-management records.

Compare installed and candidate versions with the shared build target for advisory warnings, without an accepted-version list.
The current build version is v0.2.18.
Read the installed and staged executable versions through successful `-version` commands inside the selected container.
Capture both streams and command status through a dedicated helper with a bounded timeout.

Parse the real bootstrap console message and the documented standard-log fallback forms.
Read complete `Sub2API <version> (commit: <commit>, built: <date>)` records across both streams.
Repeated records with the same version resolve to that version. Conflicting versions produce an unresolved warning.
Normalize only an optional leading `v`. Keep prerelease and build suffixes during exact comparison.
Ignore image tags, digests, and labels as version authorities. A `latest` image with matching executable version passes.

Collect mismatches, command failure, timeout, missing records, and ambiguous records as version warnings.
After both probes, show one warning with the build version, both executable versions, and probe errors.
Report literal executable versions such as `latest` as unresolved, without inferring a release from image metadata.
Before backup or replacement, ask `Continue installation? [y/N]` when any version warning exists.
Accept only an explicit `y` or `yes`, ignoring input case and surrounding whitespace.
Empty input, refusal, EOF, or interruption cancels installation before backup, replacement, or restart.

Matching versions need no version warning or extra confirmation.
Cancellation stops installation immediately and cannot become a warning that permits continuation.
ELF checks, staging failures, backup failures, and restoration keep their existing failure behavior.
Preserve staged-candidate cleanup.
Do not change the generic Docker helper to merge streams used by JSON inspection.
Use the [version research](./research/installer-version-detection.md) for source evidence and observed output.
Use the implementation plan for focused test scope.

Write outputs to temporary locations until the build succeeds.
On failure, preserve previous successful outputs and report that this invocation produced no new installer.
Clean temporary source and packaging workspaces on success or failure.

## Migration and Delivery

Initialize the parent Git repository and add the evaluation submodule.
Keep existing project files and the original plugin checkout unchanged.
Patch normalization, removal of the series file, and test cleanup belong in the new submodule worktree.
Update its standalone build to use patch filename order and executable test entries while preserving its command interface.
Keep submodule edits visible for review and follow the applicable commit approval process.
Report the checked-out submodule revision and any local patch changes with delivery.
Do not commit or push as part of repository setup.

Migrate common build code, Go installer code, and installer tests into this project.
Update imported specs to distinguish shared build rules from evaluation-plugin contracts.
Complete the automatic multi-plugin build in the same delivery.

## Task Context

This task replaces the imported v0.2.17 build contracts where they conflict with the approved requirements.
Those historical contracts include local source input, optional checks, a series file, zero-context application, and fixed license inventories.
They also include mandatory manual Docker and browser checks. Those checks are outside this task's acceptance scope.
Use this design and the PRD for the current build contract. Reuse the installer transaction without adding those historical gates.
