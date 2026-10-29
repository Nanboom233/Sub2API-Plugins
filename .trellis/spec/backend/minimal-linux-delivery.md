# Sub2API Binary Replacement Delivery

## 1. Scope / Trigger

Deliver the combined Linux/amd64 v0.2.19 server for the standard `/app/sub2api` container layout.
One self-extracting Go installer contains the compressed server and required license texts.
Standalone cleanup was removed from delivery.

## 2. Signatures

User installation:

```sh
chmod +x sub2api-plugins-installer
./sub2api-plugins-installer
```

The installer does not read or validate command-line arguments. Select the container through its numbered menu.
Always use the embedded server, a private backup directory under `/tmp`, and a fixed 120-second readiness wait.
There are no installation options, license command, or external candidate override.

Developer build and package commands:

```sh
git submodule update --init --recursive
python3 scripts/build.py
```

Fixed outputs:

```text
dist/build/sub2api-plugins
dist/build/sub2api-plugins-installer
```

## 3. Contracts

Download `https://github.com/Wei-Shaw/sub2api.git` at tag `v0.2.19` with depth one into a temporary workspace.
Read plugin submodule paths under `plugins/` from `.gitmodules`. Use current checkouts without fetching or updating plugins during builds.
Report uninitialized submodules with their initialization command.
Sort plugins by relative path and top-level `patches/*.patch` files by filename.
An absent or empty patches directory contributes no patches. Numeric filename prefixes are not required.
Apply standard contextual Git diffs against the evolving combined source with `git apply --binary`.
Keep shared-file integration edits in their owning plugins. Compatible edits to one shared file are valid.
Patch failure stops later work with the plugin, patch, and actual Git error.
Do not skip, reverse, partially apply, auto-merge, or retry with weaker context.
The common build has no source-path, check, or test-skipping argument. There is no series file or plugin registry.
The vendor patch uses a Git binary hunk to preserve `texmath.js` CRLF bytes.
There is no source overlay. Production patches contain no tests or test-only data.
Every build executes discovered plugin tests against the combined source. The runner supplies temporary native package context.
Preserve existing local source and plugin checkouts. Clean temporary workspaces on success and failure.
Compile with Linux/amd64, CGO disabled and the native `embed` tag.
The v0.2.19 source retains `0.2.18` in `backend/cmd/server/VERSION`.
Derive canonical `0.2.19` from the selected tag and inject the same value into server and installer metadata.
Install dependencies from the combined source's frozen lockfile. Reuse normal pnpm and Go caches and keep Go modules readonly.
Run native `pnpm build` before Go embed compilation. Original frontend output does not contain the patched routes.
The build entry and release workflow use pnpm 9.15.9.
The same build entry creates the installer after a successful server build.
The [installer source](../../../scripts/installer/main.go) uses only the Go standard library.
Assemble its module, gzip server payload, and license files in a temporary directory. Do not add a root Go module.
Build the installer for Linux/amd64 with CGO disabled. Keep the raw server as a local build output.
Use `sub2api-plugins-installer` as the installation asset.
Collect each repository's root `LICENSE` and third-party `licenses/` inputs under installer resources `licenses/`.
Plugin directories separate equal original filenames. Preserve relative paths, original license text, and its copyright notices.
Use original license files only. Do not add a separate `THIRD_PARTY_NOTICES.txt` summary.
Retain the base Sub2API license. Use the discovered recursive inventory instead of a fixed file count.
Build helpers, tests, fixture logs, and private files stay outside the installer payload.
Keep installation, manual rollback, and history instructions in `README.md`. There is no separate `docs/` directory.

Manual container fixtures remain optional test support under the evaluation plugin's flat `tests/native_*` paths.
Automatic build acceptance uses the existing fake-Docker installer tests. It requires no retained container or manual browser session.
Preserve unrelated containers, volumes, images, and caches.

The installer uses the Go standard library and Docker CLI. The target host needs no Python, compiler, or external extraction tool.
List running containers through quiet IDs and JSON inspect.
First show names containing `sub2api`, without case sensitivity.
If other running containers exist, append `More` with the next numeric index.
Selecting that index shows all running containers. If no names match, show all running containers directly.
Omit `More` when the list already includes all running containers.
Require a numeric selection even for one container. Resolve numbers against the currently displayed list.
Empty input has no default. Omit Cancel and the `q` shortcut. Keep Ctrl-C interruption.
Use the selected immutable container ID for all effects.
Probe installed and staged executables with `-version` inside the selected container.
Capture stdout, stderr, command status, and a bounded timeout through a dedicated version helper.
Do not merge version streams through the generic Docker helper that reads inspect JSON.
Read complete application version records, including the observed bootstrap console output and standard-log fallback.
Normalize only an optional leading `v`. Compare complete tokens, including prerelease and build suffixes.
Consistent repeated records resolve to one version. Conflicting or unreadable records leave the version unresolved.
Image tags, digests, labels, commit fields, and arbitrary log text cannot supply the application version.
A `latest` image needs no warning when its executable matches the build version.
Mismatch, unresolved output, command failure, or timeout produces one combined warning after both probes.
Show the build version, both probe results, and errors. Ask `Continue installation? [y/N]` before backup, replacement, or restart.
Only explicit `y` or `yes` continues. Ignore case and surrounding whitespace.
Empty input, refusal, EOF, or interruption cancels installation and preserves candidate cleanup.
Matching versions need no version prompt. Operational and ELF failures retain their normal handling.
Retain the existing exact 20-byte ELF header check.
Extract the embedded server silently into a private temporary directory. Remove this directory on exit.
Keep its lifetime separate from the retained executable backup.

Copy the current executable into a private directory under `/tmp` and print its exact path.
Default backups remain available until the temporary directory is removed by the user or system.
Stage the replacement and rename it over `/app/sub2api`, then restart that container.
Wait for `/health` status `ok` and `/setup/status` with `needs_setup:false`.
Require HTTP 200 directly. Do not follow redirects for either readiness endpoint.
Use host HTTP access derived from inspected port bindings, host networking or container IP.
Inspect the selected container again on every readiness attempt so restarted addresses and bindings are current.
Retry restarting containers and connection resets within the deadline; limit each HTTP request and retry sleep to remaining time.
Stopped/dead/paused containers fail promptly with exit, OOM and runtime diagnostics.
Normal startup progress includes elapsed/deadline, current state, restart count and endpoint without transient transport error text.
Print `Application ready` only after both health and setup checks pass; terminal failures retain the last actual endpoint/error.
Print step progress and actual command failures.

After replacement fails or is interrupted, restore the backup and verify the restarted original.
For a stopped container, restore with Docker cp without requiring a running process inside it.
Keep the printed backup for manual restoration.
Container recreation discards writable-layer replacement and requires reapplication.

## 4. Validation & Error Matrix

| Condition | Outcome |
| --- | --- |
| No running target or interruption during selection | Exit before replacement |
| Blank, nonnumeric, or out-of-range selection | Repeat the selection prompt without a default |
| Source preparation, dependency, patch, or test failure | Stop later build work and preserve previous outputs |
| A production patch cannot apply | Stop with the Git error before compilation |
| Mismatched or unresolved version | Warn once and request explicit confirmation |
| Refused version confirmation | Cancel before backup, replacement, or restart |
| Wrong executable architecture | Reject before replacement |
| Replacement, restart or readiness fails | Restore the exact backup and verify the original |
| Ctrl-C after replacement | Restore, verify and propagate interruption |
| Candidate stops the container | Restore through Docker cp, restart and verify |
| Connection reset or restart changes address | Retry using current inspect facts within the deadline |
| Transient reset followed by readiness | Show startup progress, then explicit ready, without presenting the reset as an install failure |
| Readiness deadline expires | Report last state/request error and restore the backup |
| Restoration fails | Report failure and retained backup location |

## 5. Good / Base / Bad Cases

Good: include every plugin submodule in one v0.2.19 server and retain the installed executable backup.
Base: a container recreated from its original image needs the same package reapplied.
Bad: compile upstream sources or require nc/buildx/helper images on the user's host.

## 6. Tests Required

All test cases, assertions, and support code live in flat `tests/`. `assets/` contains data resources only.
The argument-free build discovers `test_*.py`, `test_*.go`, `test_*.cjs`, and `test_*.test.ts` files automatically.
Run Python and CJS tests directly with Python and Node. Preserve `go run` support for standalone Go cases.
Stage native Vue suites and their flat TypeScript support files under a temporary directory in the downloaded frontend's `src/`.
Run explicit suite paths with the existing pinned pnpm and native Vitest config. Clean that directory after success or failure.
Keep existing Python, Go, and CJS discovery and execution behavior.
Native suites use `test_*_test.go` names and `// sub2api-package:` annotations.
Use `backend/internal/codexeval`, `backend/internal/service`, or `backend/internal/handler/admin` for the evaluation plugin's native packages.
Use `installer` for the common installer suite.
Stage suites in the temporary target package. Run discovered Go cases once through native `go test -tags=unit -failfast`.
Order package groups by the first discovered filename. Test failure stops later cases, groups, and build operations.
Pass `SUB2API_SOURCE` or `SUB2API_INSTALLER_SOURCE` as internal test context.
`SUB2API_ASSETS` supplies the owning repository's data-only assets path.
Keep execution support in flat `tests/support.py`. The independent standalone plugin retains its own support copy.
`SUB2API_BUILD_VERSION` supplies the canonical build version to entries. It is internal build context, not a user argument.
Installer test setup reads this environment value. Production `-X main.buildVersion` linker injection does not initialize the Go test package.
Test failure stops later entries and the build. Runtime installation does not execute plugin tests.
Keep the host test environment separate from the Linux/amd64 release build environment.
Use [the native installer tests](../../../tests/test_installer_test.go) directly with fake Docker and local HTTP.
Keep this authoritative suite in the parent repository instead of maintaining a duplicate plugin suite.
Check selection, version/ELF checks, candidate cleanup, replacement, readiness, and restoration within that set.
Include numbered `More`, no-match selection, stopped-container restoration, and Ctrl-C in that same test set.
Keep timeout control inside tests. The public deadline stays fixed at 120 seconds.
Build the final installer and check its executable format and release asset path.
Use focused fixtures for automatic discovery, shared-file cooperation, failure propagation, and recursive license contents.
Test shared version parsing and confirmation once. Use installer fixtures for matching versions and combined-warning continuation or cancellation.
Do not multiply parser cases by confirmation inputs or probe positions.
Use one real v0.2.19 build for integration evidence. Do not run its test entries separately as another acceptance gate.
Reuse passed evidence when inputs and affected behavior remain unchanged.
No fixed test count, v0.2.17 comparison build, retained container, manual browser check, or additional full-suite matrix applies.

## 7. Wrong vs Correct

Wrong: report a restored executable before checking the restarted application.
Correct: complete readiness checks before reporting successful restoration.
