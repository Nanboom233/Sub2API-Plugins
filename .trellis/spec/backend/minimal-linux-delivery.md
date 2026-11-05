# Sub2API Binary Replacement Delivery

## 1. Scope / Trigger

Deliver combined programs from the selected upstream tag for Linux amd64/arm64, Darwin amd64/arm64, and Windows amd64.
The verified integration baseline is v0.2.19.
Each self-contained Go installer carries its native program, required Linux container program, and original license texts.
Support official Docker/Compose, native executable, and Apple container installations through their existing startup owners.
Standalone cleanup was removed from delivery.

## 2. Signatures

User installation:

```sh
chmod +x sub2api-plugins-installer-v0.2.19-linux-amd64
./sub2api-plugins-installer-v0.2.19-linux-amd64
```

The installer does not read or validate command-line arguments. Select the installation form, then its target.
Use embedded programs, a retained private backup, and the fixed 120-second readiness wait.
Native programs use same-filesystem staging. Other temporary files use the host's temporary directory.
There is no license command, external candidate override, or persistent installer configuration.

Combined build commands:

```sh
git submodule update --init --recursive
python3 scripts/build.py
```

Each plugin and the template also carry a complete build kit.
Run `python3 scripts/build.py` in that checkout for a standalone build. It needs no parent checkout or manual source preparation.
Both local builds and CI use this command. There is no CI adapter or external build Action.
Actions exposes a required string input named `upstream_tag` for manual runs, with default `v0.2.19`. The user can replace it before the run starts.
Manual runs also expose five platform booleans, all true: `linux_amd64`, `linux_arm64`, `darwin_amd64`, `darwin_arm64`, and `windows_amd64`.
The `release` boolean defaults false. Manual Release publication inherits the build's actual upstream tag. There is no `release_tag` input.
Manual run titles use `Build <upstream_tag> · <ref_name>` without a run number. PR runs use their PR title.
Top-level `run-name` reads existing inputs and GitHub context. Keep `name: Build` and add no title input.
Pass the requested value through `UPSTREAM_TAG` in the process environment. Do not interpolate user input into shell commands.
Local builds use the same entry and environment input, for example `UPSTREAM_TAG=v0.2.19 python3 scripts/build.py`.
Pull-request builds resolve the latest official release through the public upstream release API.
Local builds without `UPSTREAM_TAG` use the same resolver. Resolve once before source preparation and reuse the resulting actual `tag_name`.
Use no user credentials for this public lookup. Query failure or an unusable response fails the build without a version fallback.

Fixed outputs:

```text
dist/build/<os>-<arch>/sub2api-plugins-<upstream-tag>-<os>-<arch>
dist/build/<os>-<arch>/sub2api-plugins-installer-<upstream-tag>-<os>-<arch>
```

## 3. Contracts

Download `https://github.com/Wei-Shaw/sub2api.git` at the selected tag with depth one into a temporary workspace.
Read plugin submodule paths under `plugins/` from `.gitmodules`. Use current checkouts without fetching or updating plugins during builds.
Report uninitialized submodules with their initialization command.
Sort plugins by relative path and top-level `patches/*.patch` files by filename.
After initialization checks, skip plugins without top-level `patches/*.patch` files, including their tests and licenses.
Numeric filename prefixes are not required.
The template submodule under `plugins/sub2api-plugin-template` has no production patches and is skipped by the combined build.
A standalone root with a tracked `patches/` directory applies its own patches only.
An empty standalone template builds unmodified upstream Sub2API using its complete build kit.
Apply standard contextual Git diffs against the evolving combined source with `git apply --binary`.
Keep shared-file integration edits in their owning plugins. Compatible edits to one shared file are valid.
Patch failure stops later work with the plugin, patch, and actual Git error.
Use the command runner as the single patch-progress owner. Do not print another `Apply ...` line for the same command.
Do not skip, reverse, partially apply, auto-merge, or retry with weaker context.
The common build has no source-path, check, or test-skipping argument. There is no series file or plugin registry.
The vendor patch uses a Git binary hunk to preserve `texmath.js` CRLF bytes.
There is no source overlay. Production patches contain no tests or test-only data.
Every build executes discovered plugin tests against the combined source. The runner supplies temporary native package context.
Preserve existing local source and plugin checkouts. Clean temporary workspaces on success and failure.
Prepare source, dependencies, and the frontend once. Run host tests once and compile the selected targets, all five by default.
Use CGO disabled and the native `embed` tag. Add `.exe` to Windows programs.
The v0.2.19 source retains `0.2.18` in `backend/cmd/server/VERSION`.
Resolve the actual selected tag once. Remove only its leading `v` for canonical server and installer version metadata.
Use that same selection for source download, test context, both linker values, artifact names, validation, and upload paths.
Do not read a hardcoded version separately during output validation.
Install dependencies from the combined source's frozen lockfile. Reuse normal pnpm and Go caches and keep Go modules readonly.
Run native `pnpm build` before Go embed compilation. Original frontend output does not contain the patched routes.
Use the same selected stable pnpm for dependency installation, frontend compilation, and native Vue tests.
Translate upstream overrides and effective build settings into the current pnpm configuration in temporary source only.
Keep the frozen lockfile and original override values. Install current Corepack separately when required by Node.
The same build entry creates the installer after a successful server build.
The [installer source](../../../scripts/installer/) uses standard-library installation operations and PTerm v0.12.84 for terminal interaction.
Prepare dependencies, compressed programs, and license files in its temporary module. Do not add a root Go module.
Compile each installer for its host with CGO disabled. Keep each raw native program as a local output.
Linux installers reuse their native payload for Docker. Darwin installers additionally embed the matching Linux architecture for containers.
Darwin arm64 supports Apple container with Linux arm64. Windows amd64 embeds Linux amd64 for Docker.
Use the selected upstream tag, including `v`, in output names. Windows names add `.exe`.
Collect each repository's root `LICENSE` and third-party `licenses/` inputs under installer resources `licenses/`.
Plugin directories separate equal original filenames. Preserve relative paths, original license text, and its copyright notices.
Use original license files only. Do not add a separate `THIRD_PARTY_NOTICES.txt` summary.
Retain the base Sub2API license. Use the discovered recursive inventory instead of a fixed file count.
Build helpers, tests, fixture logs, and private files stay outside the installer payload.
Keep installation, manual rollback, and history instructions in `README.md`. There is no separate `docs/` directory.
Eval and quota patch adaptations and the template use `LGPL-3.0-or-later` while retaining inherited MIT and dependency notices.
The parent's own build/installer code retains its MIT license. All complete kits carry the upstream GPL and LGPL texts.

Each repository has `.github/workflows/build.yml` for pull-request and manual builds on `ubuntu-latest`.
Branch and tag pushes do not trigger builds. Keep the existing five platform checkboxes.
Use verified current stable tools and exact release tags for official Actions, such as `@v7.0.1`.
Do not use commit hashes or major-only tags. Keep build permissions at `contents: read`; only enabled Release publication gets `contents: write`.
Disable checkout credential persistence. Workflows need no personal token or repository secret.
Use the same selected platform output pairs in every repository, without repository-name inference or compatibility aliases.
Upload each executable directly with `archive: false`. Do not create tar files or another product archive.
This mode ignores `name` and derives the artifact name from the file's basename.
Publish two direct files per selected platform, ten by default. Unix downloads need `chmod +x` before execution.
Keep executable outputs under `dist/build/<os>-<arch>/`. Do not retain duplicate legacy output copies.
Stage the complete new output set on the destination filesystem before publication.
Swap directories through rename. If publication fails, restore the old directory at its original path.
Do not copy partial new outputs into the live directory or nest the old directory during restoration.
Run build commands directly and retain their exit status. Patch/test failures fail the job and prevent product upload.
The builder assembles expected selected outputs once. Native upload Actions use `if-no-files-found: error`.
Do not add a separate workflow output-validation loop, repeat the builder checks, or check executable access immediately after chmod.
Treat output paths as data in shell messages. Do not evaluate them through command substitution.
Use native Actions step logs, annotations, and workflow status for build and upload failures.
Do not add custom summaries, duplicate log artifacts, or file-capture pipelines.
Optional manual Release publication reuses the exact successful selected products. PR and Release-disabled manual runs remain artifact-only.
Set `RELEASE_TAG` from `needs.build.outputs.tag`, the actual upstream tag used for source and artifact names.
Use the built-in job token and `gh release create --generate-notes`, with no custom notes or notes file.
Titles use `Sub2API-Plugin <first-seven-commit-characters> (v<canonical-upstream-version>)`, with exactly one leading `v`.
An existing release tag, including an annotated tag, must resolve to the built source commit. Do not move tags or overwrite Releases/assets.
Do not publish container images, checksum manifests, or build-info manifests.

### Single build job and dependency caches

Local `python3 scripts/build.py` without stage inputs retains the complete build and atomic publication.
CI uses that entry with `SUB2API_BUILD_STAGE=source|resume` and `SUB2API_BUILD_WORKSPACE=dist/work` within one build job.
`SUB2API_BUILD_PLATFORMS` contains whitespace-separated final `os-arch` names. Unset means all platforms.
An empty or unsupported list fails before source work. There is no per-target stage or `SUB2API_BUILD_TARGET`.
The source stage resolves the upstream tag once, downloads source, applies patches, and exports `tag`, `pnpm`, and `platforms`.
The workflow also records `source_sha` from the checked-out build commit.
Restore caches after source exists so workspace-relative lockfile expressions identify actual dependencies.
Resume receives that same tag through `UPSTREAM_TAG`, the selected platforms, and the existing workspace.
It runs remaining preparation, tests, compilation, and atomic publication without another source download or release lookup.
Build the frontend, run plugin tests and vet, assemble installer dependencies/licenses, and run common tests once.
Compile the host architecture's Linux payload for common installer tests. Ubuntu amd64 uses Linux/amd64.
Preserve that host payload for local Darwin/arm64 builds even when it is outside the selected final platforms.
Compile remaining selected native programs and matching Linux container payloads sequentially, reusing programs already compiled for common tests.
Compile selected installers sequentially from their native and matching Linux programs. Each Go invocation retains native package parallelism.
Keep all source, programs, and installer resources in the same job workspace. Do not upload intermediate or diagnostic artifacts.
Publish selected final pairs only after the complete build succeeds. Unselected support payloads are not final products.
Only the optional Release job downloads final executable artifacts. Restore executable access without another bit assertion.
Use exact official tags: cache restore/save `v6.1.0`, download-artifact `v8.0.2`, and upload-artifact `v7.0.2`.
Cache paths come from `go env GOMODCACHE`, `go env GOCACHE`, and the selected pnpm's `store path --silent`.
Restore each cache once. Save each through one build-job owner after successful work, using the restore step's primary key.
Keys identify the runner, toolchain, actual dependency files, and builder dependency pins. Compilation keys also identify the source revision.
One Go compilation cache holds multiple targets. Go distinguishes target OS and architecture internally.
Use normal restore prefixes. Cache misses retain normal installation, frozen lockfiles, tests, and compilation.
Do not cache patched source, node_modules, final programs, or installer payloads.

Manual container fixtures remain optional test support under the evaluation plugin's flat `tests/native_*` paths.
Automatic build acceptance uses the existing installer command and local HTTP fixtures. It requires no retained container or manual browser session.
Preserve unrelated containers, volumes, images, and caches.

The target host needs no Python, compiler, or external extraction tool. Container modes use the selected runtime CLI.
Native mode controls the effective official systemd service or asks the user to stop/start through the original launch method.
It does not create a service or reconstruct manual arguments, environment, or working directory.
Resolve native symlinks and preserve ownership and permissions during same-filesystem replacement.
Ask for the native address with default `127.0.0.1:8080` and Linux program path default `/opt/sub2api/sub2api`.

Use PTerm inline selection, text input, confirmations, and timed spinners only with actual supported terminal stdin/stdout.
Injected or redirected streams and `TERM=dumb` use plain numbered prompts and sequential lines without cursor controls.
Honor `NO_COLOR`. Stop and join spinner rendering before prompts, diagnostics, and final results.
Show elapsed time for unknown-duration stages without an invented percentage.
Keep animated stage text short and width-aware. PTerm's spinner alone cannot clear automatic terminal wrapping.
Use the selected component's area rendering for wrapped frames. Do not build another terminal redraw engine.
Show one live elapsed timer. Do not embed sampled elapsed time, container state, or endpoint data in animated frame text.

Override every PTerm prompt's interrupt handler. Cancel the operation context and check it before accepting any returned choice.
UI callbacks do not exit directly or own rollback. Keep command diagnostics with one final error owner.

Resolve language once from the first nonempty `LC_ALL`, `LC_MESSAGES`, or `LANG` value.
Chinese locales use Simplified Chinese. Other, absent, `C`, and `POSIX` locales use English.
Accept locale case, `_`/`-` separators, and encoding suffixes. Higher-priority `C` overrides lower-priority Chinese.

Localize installer-owned messages. Keep paths, commands, versions, identifiers, and external diagnostics literal.
Do not add a language menu, argument, configuration file, OS-language lookup, or locale framework.

Docker target selection retains the following behavior.
List running containers through quiet IDs and JSON inspect.
First show names containing `sub2api`, without case sensitivity.
If other running containers exist, append `More` with the next numeric index.
Selecting that index shows all running containers. If no names match, show all running containers directly.
Omit `More` when the list already includes all running containers.
Require explicit selection even for one container. Plain prompts require a number from the currently displayed list.
Empty input has no default. Omit Cancel and the `q` shortcut. Keep Ctrl-C interruption.
Use the selected immutable container ID for all effects.
The Docker helper buffers child stdout and stderr. Forward buffered output only for successful non-quiet commands.
On command failure, return captured detail with operation context for the final error owner to print once.
Quiet failures retain their captured detail. Preserve cancellation causes and separate restoration outcomes.
Probe installed and staged executables with `-version` in their target environment.
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
Matching versions need no version prompt. Operational and executable-format failures retain their normal handling.
Use Go's ELF, Mach-O, and PE readers to check the selected runtime format and architecture before replacement.
Extract the embedded server silently into a private temporary directory. Remove this directory on exit.
Keep its lifetime separate from the retained executable backup.

Copy the current executable into a private backup and print its exact path.
Default backups remain available until the temporary directory is removed by the user or system.
Stage the replacement and rename it over `/app/sub2api`, then restart that container.
Wait for `/health` status `ok` and `/setup/status` with `needs_setup:false`.
Require HTTP 200 directly. Do not follow redirects for either readiness endpoint.
Use host HTTP access derived from inspected port bindings, host networking or container IP.
Inspect the selected container again on every readiness attempt so restarted addresses and bindings are current.
Retry restarting containers and connection resets within the deadline; limit each HTTP request and retry sleep to remaining time.
Stopped/dead/paused containers fail promptly with exit, OOM and runtime diagnostics.
Plain startup progress includes elapsed/deadline, current state, restart count, and endpoint without transient transport error text.
Dynamic progress uses the short readiness stage and live component timer. Final failures retain the actual endpoint and error.
Print `Application ready` only after both health and setup checks pass; terminal failures retain the last actual endpoint/error.
Print step progress and actual command failures.

Before any application or startup mutation, cancellation removes the stage without restarting the unchanged application.
After program replacement or a managed stop begins, recovery restores the original program and startup state, then checks readiness.
Recovery commands and manual prompts use a separate restoration context, rather than the canceled installation context.
Unavailable recovery input retains the backup and reports the pending manual action without claiming success.
For a stopped container, restore with Docker cp without requiring a running process inside it.
Keep the printed backup for manual restoration.
Container recreation discards writable-layer replacement and requires reapplication.

Native systemd installation stops the effective service, replaces the program, starts that service, and checks readiness.
Native manual installation asks the user to stop, replaces the program, asks for original-method startup, and checks readiness.
Recovery follows the same startup owner. Preserve data, service configuration, arguments, environment, and working directory.
Program rollback does not reverse database migrations.

Apple installation targets `/app/storage/runtime/sub2api` and preserves `/app/storage/runtime/base-image-id`.
Copy the stage into the running application container, preserve ownership, and set executable access before rename.
Keep the backup on the host. Stop/start only that application container, leaving PostgreSQL and Redis running.
Apple container copy requires a running container. If stopped, start the same container before restoration.
If its runtime or volume cannot start, retain the host backup and report incomplete recovery.
Normal recreation retains the runtime program while the base image ID is unchanged. Image changes require reinstallation.
Data-only backups do not include that runtime program.

## 4. Validation & Error Matrix

| Condition | Outcome |
| --- | --- |
| No running target or interruption during selection | Exit before replacement |
| Blank, nonnumeric, or out-of-range selection | Repeat the selection prompt without a default |
| Source preparation, dependency, patch, or test failure | Stop later build work and preserve previous outputs |
| A production patch cannot apply | Stop with the Git error before compilation |
| Expected upload file is absent | Native upload Action fails; do not repeat that check in a workflow loop |
| Empty manual platform selection | Reject before source preparation |
| Dependency cache misses | Install dependencies and build normally; do not skip checks |
| Existing Release tag identifies another commit | Fail publication without moving the tag |
| Release creation or asset upload fails | Report native CLI failure and retain successful Actions artifacts |
| CI build step fails | Fail the job, retain native step diagnostics, and prevent product uploads |
| Automatic upstream release lookup fails | Report the lookup failure and preserve previous outputs |
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
| Native startup has no service owner | Ask the user to stop/start through the original launcher |
| Apple container is stopped during recovery | Start the same container before copying the host backup |
| Recovery input or Apple runtime remains unavailable | Retain backup and report incomplete recovery |

## 5. Good / Base / Bad Cases

Good: include every plugin with production patches in one v0.2.19 server and retain the installed executable backup.
Base: a container recreated from its original image needs the same package reapplied.
Bad: compile upstream sources or require nc/buildx/helper images on the user's host.
Good: a Darwin/arm64-only CI build embeds Linux/arm64 while publishing only the selected Darwin pair.
Bad: repeat shared tests per target or publish support payloads as unselected products.

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
Keep execution support in flat `tests/support.py`. Every complete build kit retains an aligned support copy.
Standalone builds run their common and business cases once. Combined builds run active plugin business cases and parent common cases once.
`SUB2API_BUILD_VERSION` supplies the canonical build version to entries. It is internal build context, not a user argument.
Installer test setup reads this environment value. Production `-X main.buildVersion` linker injection does not initialize the Go test package.
Test failure stops later entries and the build. Runtime installation does not execute plugin tests.
Keep host tests separate from cross-compilation environments.
Use [the native installer tests](../../../tests/test_installer_test.go) directly with fake Docker and local HTTP.
Keep aligned copies of this suite in each complete build kit. Do not create separate cases for identical installer behavior.
Check selection, version/format checks, candidate cleanup, replacement, readiness, and restoration within that set.
Include numbered `More`, no-match selection, stopped-container restoration, and Ctrl-C in that same test set.
Keep timeout control inside tests. The public deadline stays fixed at 120 seconds.
Extend existing cases for changed native/Apple control and recovery, host/payload selection, locale precedence, and plain/cancellation behavior.
Do not multiply shared cases by installation form, language, rendering mode, or target.
Inspect actual terminal selection, spinner-to-prompt transitions, and cancellation without a snapshot suite.
For progress rendering changes, include a long readiness wait in a narrow terminal. Short prompts do not establish redraw correctness.
Build final platform pairs and retain their platform paths. Cross-compilation does not prove platform runtime installation.
Use focused fixtures for automatic discovery, shared-file cooperation, failure propagation, and recursive license contents.
Test shared version parsing and confirmation once. Use installer fixtures for matching versions and combined-warning continuation or cancellation.
Do not multiply parser cases by confirmation inputs or probe positions.
Use one real v0.2.19 build for integration evidence. Do not run its test entries separately as another acceptance gate.
Reuse passed evidence when inputs and affected behavior remain unchanged.
Extend the existing composition fixture for standalone roots, empty-template exclusion, and once-per-build common tests.
Adapt those same builder cases for source/resume, selected targets and Linux payload closure, and failed publication preserving previous outputs.
Inspect workflow conditions and Release CLI arguments directly. Do not add workflow-text suites or deliberate failing Release runs.
Capture expected failure output inside the existing failure-propagation fixture. Reveal it when an assertion unexpectedly fails.
Keep real child-process failure details visible. Do not suppress output globally.
Extend the existing Docker-helper case for single error output. Do not repeat installer transaction scenarios or mirror progress strings.
Do not add naming compatibility tests, generated-repository fixtures, separate workflow-lint gates, or deliberate remote failure runs.
No fixed test count, v0.2.17 comparison build, retained container, manual browser check, or additional full-suite matrix applies.

## 7. Wrong vs Correct

Wrong: report a restored executable before checking the restarted application.
Correct: complete readiness checks before reporting successful restoration.
Wrong: duplicate native Action missing-file checks and test executable access immediately after chmod.
Correct: assemble expected outputs once, restore permissions, and use native Action/job failures.
