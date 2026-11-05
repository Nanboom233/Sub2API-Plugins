# Installation support review

## Scope and candidate

The review covers the approved child task across the parent, eval, quota, and template build kits.
Product files remain read-only during the implementation owner's combined build.
The implementation owner handles repairs and their affected checks.

The reviewed scope includes three installation forms, five targets, payload selection, terminal interaction, automatic locale, licenses, and artifact-only CI.
The review also checks the requested root/template usage instructions.
Eval's exact historical README restoration remains outside this child's rewrite scope.

## Findings

### Output restoration after publication failure

Status: repaired and reviewed.

The reviewed builder moves old outputs into its temporary workspace, then moves the complete new directory into `dist/build`.
Across filesystems, `shutil.move` uses `copytree` and can leave a partial destination after copying fails.
Its recovery then moves `previous-outputs` into the existing destination directory instead of restoring the original platform paths.
The standard-library implementation confirms both the copy fallback and existing-directory nesting behavior.
This violates the existing previous-output preservation contract.

`publish_outputs` now completes a private staging copy under `dist` before exchanging directories through same-filesystem rename.
Copy failure leaves existing outputs untouched. Publication rename failure restores the previous output path.
Failed recovery retains the previous directory and reports its location.
The existing failure-preservation case now covers partial copying and publication rename failure.
The implementation owner reported that case passed in 4.54 seconds after the repair.

### Executable mismatch translation

Status: repaired and reviewed.

`checkExecutable` creates the installer-owned reason `format or architecture mismatch`.
`checkProgram` localizes its wrapper but returns this reason in English in Chinese mode.
`checkProgram` now translates this owned reason through the existing message catalog.
Actual external parser and system diagnostics retain their original text.
No per-string translation test was added.

## Verified source contracts

The 13 shared build, workflow, installer, and common-test paths remain identical across all four kits after the repairs.
The review used direct content comparison.
No hashes were calculated.

Native installation resolves the selected program and preserves permissions and ownership through same-filesystem staging.
Systemd controls the existing service. Manual installation and recovery retain user-controlled stop/start.
Restoration uses a separate context and reports unavailable recovery input with the retained backup.

Apple installation targets `/app/storage/runtime/sub2api`, preserves the image marker, and retains a host backup.
Its adapter uses Apple's actual inspect fields and running-container copy behavior.
Recovery starts the same stopped application container before copying. Only that application container stops or starts.

The build prepares source and frontend once and runs common checks once before publishing five output pairs.
Each installer embeds its native program and the required Linux program.
The Darwin arm64 package includes Linux arm64 for Apple container.

Every PTerm prompt overrides interruption and checks cancellation before accepting returned input.
Spinner shutdown waits before prompts, final results, or raw command output.
Plain streams retain numbered input without cursor controls.
Locale resolution honors `LC_ALL`, `LC_MESSAGES`, then `LANG`, including a higher-priority `C` value.

Dependency licenses come from original module files in the temporary installer module.
The workflow preserves patch/test failures, validates platform outputs, and uploads each executable directly as a platform-specific artifact.
Failure logs upload only after build-step failure. Summaries link successful diagnostic uploads and do not copy raw logs.
Actions use exact release tags, credential persistence is disabled, and permissions remain read-only.

## Evidence and remaining acceptance

The review reuses the implementation owner's passing focused installer cases and four builder cases.
Those cases cover shared Docker behavior, native/Apple recovery, locale precedence, plain streams, and command output ownership.
The owner compiled Darwin arm64 and Windows amd64 installers and inspected actual PTY selection, path input, and cancellation.

The final source review passes after both repairs.
The default combined build exited successfully, with output at `/tmp/sub2api-installation-build.log`.
It passed frontend compilation, plugin checks, focused vet, common builder cases, and the complete installer suite.
The build produced all five program/installer pairs.
The running builder loaded the earlier publication function before the repair.
The completed actual output set passed through the repaired publication function successfully without recompilation.
Actual final-installer PTY inspection confirmed timed spinner shutdown before version confirmation and Ctrl-C cancellation before mutation.
Plain-stream cancellation passed. The latest direct-executable delivery checks appear below.
The detailed owner evidence is in [implementation results](implementation-result.md). Local acceptance is complete.
Cross-compilation does not establish runtime installation on every platform.
No actual deployment, credential operation, remote CI run, commit, or push is part of this review.

## Narrow-terminal progress correction

The user reported repeated readiness lines after the initial acceptance check.
The implementation owner reproduced 113 retained readiness rows during an 11.2-second wait in a 40-column terminal.
PTerm's spinner uses carriage return without clearing automatic wrapped rows.
The previous frame also mixed sampled elapsed time and state details with the component's live timer.

The corrected dynamic path sends short timed spinner frames through PTerm's `AreaPrinter`.
The existing component handles display width, CJK wrapping, and clearing of previous rows.
The adapter does not implement terminal cursor control or another redraw engine.
Dynamic readiness keeps one live timer. Plain readiness retains state, endpoint, and sampled progress lines.

Source review confirmed that `Spinner.Stop` joins the animation before `Area.Stop` and subsequent prompts or output.
Only the spinner goroutine updates the active area. Prompt and final-result paths stop progress first.
Cancellation and restoration ownership remain in the existing transaction.
The four `ui.go` and workflow copies match by direct comparison. The changed Go source passes formatting inspection.

The owner supplied narrow-terminal captures under `/tmp/sub2api-spinner-check/`.
The reviewer read `fixed-en.screen`, `fixed-en24.screen`, and `fixed-zh24.screen`.
The corrected 40-column capture retains one readiness area after an 11.6-second wait.
At 24 columns, English wraps into two physical rows within one area. Chinese retains one area without repeated state lines.
Both captures show the live timer reaching 11 seconds and successful completion.

The owner tested eight fixture installers through actual Docker: four build kits on Linux arm64 and amd64.
Those packages use each kit's source and licenses with a synthetic delayed application payload.
Replacement, readiness, and same-container restart passed for each package.
An additional failed synthetic payload passed stopped-container copy restoration and original-program readiness.
The reviewer read these outcomes in `/tmp/sub2api-spinner-check/docker-installers.log`.

These fixture packages establish installer and Docker behavior. They do not establish the final Sub2API application's runtime behavior.
The owner separately checked the actual combined application with isolated PostgreSQL and Redis and rebuilt the five actual installers.
Both actual Linux arm64 and emulated amd64 runs passed version, plugin page, installer replacement, readiness, and same-container restart checks.
The reviewer read `product-smoke.log`, the successful amd64 installation log, and `product-rebuild.log` under `/tmp/sub2api-spinner-check/`.
The rebuild log records the expected native/Linux payload pair for each platform. The five executable installer files exist at their platform paths.
The actual product module remains separate from synthetic fixture payload staging.

The owner's [spinner and Docker evidence](spinner-docker-check.md) records the complete commands, results, and fixture boundaries.
The native manual check controlled actual fixture processes. Systemd and Apple checks remain command-fixture evidence.
The source and evidence review of the progress correction passes. No further product repair is required by this review.

## Versioned direct executable delivery

The user removed product tar packaging and requested names that identify the program kind, upstream version, operating system, and architecture.
The builder uses `artifact_name` with the selected upstream tag as its filename version authority.
The retained baseline names include `v0.2.19`. Windows names end in `.exe`.
Raw programs use `sub2api-plugins-v0.2.19-<os>-<arch>`.
Installers use `sub2api-plugins-installer-v0.2.19-<os>-<arch>`.

The workflow consumes the actual tag exported by its build step during output validation.
All ten product upload steps consume the same output and use `archive: false` with exact executable paths.
There is no additional workflow version literal, product archive step, ignored product-name input, or legacy filename alias.
Validation retains one contextual error annotation and summary entry. Failure diagnostics keep their existing separate owner.

The reviewer resolved the ten upload paths against the current tag.
They identify ten separate, nonempty executable files in the five platform directories.
The retained `dist/build` contains exactly those files. The `dist` root contains no old product archive files.
The four builder, common-builder-test, and workflow copies match by direct content comparison.
Root and template instructions show direct execution, Unix `chmod`, and the Windows `.exe` name.

The owner recorded four passing existing builder cases in 9.411 seconds and a passing execution of the actual workflow validation shell.
See [direct artifact evidence](direct-artifacts.md) for those results and the complete retained file inventory.
Native rename operations changed filenames without recompiling or modifying program contents, so prior runtime evidence remains applicable.
The independent source and evidence review passes. No repeated build or runtime check is needed for this revision.

## Upstream tag selection

The user confirmed that push and pull-request builds must use the latest official release's actual tag.
Manual workflow runs require `upstream_tag`, without a default. The workflow passes it through the process environment.
The shared builder also accepts `UPSTREAM_TAG` for local builds without adding a command argument.

Source review confirmed that an absent override causes one public, unauthenticated `/releases/latest` request.
The resolver reads `tag_name` and rejects unusable metadata or version tokens before source preparation or output publication.
It accepts an optional leading `v`, prerelease identifiers, and build suffixes without allowing whitespace or shell syntax.
The builder retains no fixed `TAG` or `VERSION` authority and supplies no old-version fallback.

The resolved tag selects the cloned source and the explicit detached `refs/tags/<tag>` checkout.
Removing only the optional leading `v` supplies test context and both server and installer linker values.
All ten filenames use the original resolved tag, including its optional prefix and suffixes.
Only the production entry writes the tag to `GITHUB_OUTPUT`.
Common builder fixtures call the resolver and builder directly, so synthetic tags cannot replace the job's build output.
Output validation and all ten uploads consume `steps.build.outputs.tag` without another release query.

The four builder, builder-test, and workflow copies remain identical by direct content comparison.
Root and template instructions distinguish actual automatic selection from the retained `v0.2.19` filename examples.
The owner recorded four passing existing cases in 9.369 seconds, including the `v1.2.3-rc.4` propagation and lookup-failure paths.
The production-entry output check and actual workflow validation shell also passed.

The first real Python release request encountered a transient TLS reset and failed without a fallback.
Main subsequently confirmed the public endpoint through unauthenticated curl and reran the unchanged production resolver successfully.
The resolver returned `v0.2.19` with an empty override. No product retry or fallback was added.
See [tag-input evidence](upstream-tag-input.md) for the owner checks and network results.
This narrow source and evidence review passes. It does not establish patch compatibility with a different upstream release.
