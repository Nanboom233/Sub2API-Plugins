# Installation support research progress

## 2026-10-31 survey

The user requested a child task under `10-30-inspection-settings-attribution`, starting with installation-form research.
The child was created and linked without changing the parent's active task or approving product implementation.

The researcher checked upstream v0.2.19, observed current upstream files, and actual release assets.
The user narrowed the survey to official-maintained installations intended for users.
The inventory now has three forms: Docker/Compose, native executable, and Apple container.
Release downloads and source builds share the native executable form. Systemd and manual launch are startup details.
Compose storage variants share one form. Community examples and developer workflows were removed from the report.
The local baseline records fixed paths, architecture, Docker commands, readiness, backup, and recovery behavior.

Important finding: Apple container starts a persistent runtime program and normally recreates containers without replacing that program.
Its base-image changes can reset the program. Data-only backups do not include the separate runtime program.
Published upstream programs cover Linux and Darwin amd64/arm64 plus Windows amd64. Current plugin outputs remain Linux/amd64 only.

Main reviewed the complete research and integrated it with the local baseline.
The recommendation shares version warnings, backup, replacement, readiness, and recovery while adapting to the actual startup owner.
Source links, versions, and relevant persistence and platform limits remain in the research files.

The research acceptance criteria are satisfied. The child remains in planning for later extension scope and implementation approval.
No build, deployment change, runtime test, personal credential use, commit, or remote write occurred.

## 2026-11-01 operational research

The user requested continued research within the three official user-facing forms.
The new `research/installation-operations.md` traces native configuration, process ownership, updater behavior, and Docker/Apple replacement operations.
The new `research/platform-artifacts.md` separates the installer host from its embedded application's runtime target.
Main read both reports and checked their recommendations against the current source baseline.

The built-in updater only selects official upstream releases. It cannot install a local plugin program or accept a custom download URL.
Its same-directory staging, backup, rename, and restoration pattern remains useful without extending its API.
Updates do not restart the process. The restart endpoint exits only on Linux, relying on the actual supervisor.
Native Darwin and Windows therefore cannot use that endpoint for automatic restart.
Official systemd has a known path and restart owner. Arbitrary manual launch state cannot be reconstructed from its executable path alone.

Apple replacement must target its persistent runtime program and preserve its existing base-image marker.
Application-container stop/start can avoid restarting PostgreSQL and Redis while their addresses remain valid.
The installer executes on Darwin/arm64 but needs a Linux/arm64 payload for that deployment.
Windows additionally needs platform-specific process handling, temporary paths, and executable-format checks.
Current code hardcodes one Linux/amd64 output pair. Inherited target variables cannot select another output.

The recommended plan shares version warnings, backup, staged replacement, readiness, and recovery across the three forms.
It adapts actual program paths and startup owners while separating installer-host and payload-runtime targets.
No new installation category, updater API, runtime test matrix, or product condition was added by this research.
The child remains in planning. No implementation, build, runtime test, installation, credential use, or remote write occurred.

## 2026-11-04 installation planning

The user requested continued planning for the three official installation forms.
The user selected manual stop/start for native programs without systemd. The installer owns backup, replacement, checks, and restoration.
The PRD now includes installation acceptance criteria. `design.md` and `implement.md` describe the proposed implementation.
Context manifests reference actual delivery specs and research, without product-source entries.

The design shares warnings, backup, staged replacement, readiness, and restoration while adapting executable paths and startup owners.
Docker retains its current container lifecycle and recreation limits. Native systemd controls its existing service.
Manual launch state remains with the user. Apple replaces the persistent runtime file and restarts only the application container.
The proposed output set covers the five official runtime platforms, with separate installer-host and payload-runtime selection.
Darwin installers additionally carry matching Linux payloads for containers. Windows retains `.exe` and platform-specific process handling.
The default builder prepares source and frontend once, runs existing common checks once, and emits platform-separated fixed-name outputs.

Further Apple source review confirmed that copy requires a running container and gives copied files mode 0644 by default.
The staged program needs executable access and the preserved owner before rename.
Failed child programs retain the supervisor. Stopped-container restoration first starts the original container before copying the backup.
If the runtime cannot start, retain the backup and report incomplete restoration rather than assuming offline copy support.

The plan extends existing flat tests without a runtime matrix, added logger, updater API, deployment manifest, or new build entry.
No product files, deployments, builds, tests, credentials, commits, or remote writes changed during this planning turn.

The read-only planning review found no new technical blocker or redundant runtime gate.
The execution plan now schedules affected Docker-only/Linux-only spec updates after approval and before new-target implementation.
Usage changes are limited to the user's explicitly requested root/template READMEs. Eval's restored README remains exact.
The complete proposal is ready for user review. Implementation remains unapproved.

## Confirmed flows and consolidated plan

The user confirmed the detailed three-form flows and requested that they be written into the task before the complete plan is shown.
The design now gives ordered Docker, native, and Apple steps, including version decisions, backup location, startup ownership, and recovery.
The PRD moves completed research out of implementation gates while preserving its records and source links.
The execution plan now has one focused verification section instead of duplicate acceptance-check lists.

Only existing native/Apple control-path cases and builder payload/output fixtures need changes.
Shared version, confirmation, readiness, Docker restoration, and cancellation cases are not multiplied by installation form or platform.
Existing failure propagation and output preservation cases remain. No menu-string, filename, workflow-mirror, or unchanged-log tests are added.
One default combined build checks the completed candidate and compiles required outputs. Review reuses that evidence.
Runtime matrices, repeated standalone builds, coverage/race gates, generated deployments, and deliberate remote failures remain excluded.

The independent read-only review confirmed that the consolidated artifacts preserve all user-confirmed flows without added conditions.
Scoped diff formatting passed. This turn changed Trellis artifacts only and did not activate or implement the child.

## Terminal redesign and Chinese localization

The user added a terminal presentation redesign with dynamic behavior where available and Chinese i18n.
R15-R16 and AC10-AC11 now cover interactive terminal rendering, readable plain output, and Simplified Chinese/English messages.
The design shows installation selection, target context, stage progress, manual prompts, warnings, and final recovery/backup results.
Dynamic rendering pauses for input and remains disabled for redirected or limited output.
Unknown-duration operations show activity and elapsed time rather than invented percentages.
Locale selection follows the system language, with English fallback and in-installer language switching.
External command diagnostics and literal paths, versions, and identifiers remain unchanged.

Use maintained terminal components rather than writing terminal primitives or another CLI/logging framework.
The dependency integration belongs in the build's existing temporary installer module. Installed binaries remain self-contained.
The four kits share the terminal integration and small Go message catalog.
Reuse single-owner error output and existing transaction checks. Do not multiply tests by language, translation key, or rendering mode.
The plan includes actual dynamic/plain presentation checks during implementation, without a platform runtime matrix.
This is a planning addition. No product code or tests changed, and implementation remains unapproved.

## Automatic terminal language correction

The user replaced language selection with automatic terminal-language detection.
R16, AC11, and the terminal design now use the first non-empty `LC_ALL`, `LC_MESSAGES`, or `LANG` value.
Chinese locales select Simplified Chinese. Other or absent locales, including `C` and `POSIX`, select English.
The initial view has installation choices only. No manual language action, language setting, or command argument remains.
Operating system UI-language lookup and a locale-helper dependency are unnecessary for this requirement.
The earlier proposed in-installer language switching is superseded. The terminal component research uses this updated scope.

## Terminal component and interaction plan

The user requested continued planning after adding dynamic terminal UI and Chinese i18n.
The researcher compared PTerm and Huh against original release metadata, source, cancellation, CJK, Windows, and plain-stream behavior.
The selected component is PTerm v0.12.84. Its Go 1.26.0 requirement is satisfied by the existing Go 1.27.3 CI selection.
The source comparison and original license links are in `research/terminal-ui.md`.

The design uses inline menus and step progress, keeping normal terminal scrollback and the existing transaction owner.
Entry offers installation forms only, using automatic terminal-locale language selection.
No extra language question, mandatory installation-confirmation screen, or persistent installer settings are added.
PTerm supplies selection, inputs, confirmations, CJK width, Windows terminal support, and timed spinners.
The plain path retains existing reader/writer injection, numbered prompts, and full-line `y`/`yes` acceptance.
Real stdin/stdout TTY and supported capabilities gate dynamic use. Redirected streams and `TERM=dumb` remain plain.

Every interactive prompt overrides PTerm's direct-exit Ctrl-C behavior and returns cancellation to the existing recovery flow.
After prompt cleanup, context cancellation takes priority over any returned default selection.
Stop and join spinner rendering before prompts or final diagnostics. Retain one error owner and the durable backup/result output.
The original dependency licenses use the existing resource layout. No localization framework, system-language helper, or new manifest is needed.

The task, design, execution plan, and context manifests now contain these decisions.
Existing tests cover shared transactions once. Changed terminal behavior receives focused existing-case updates and actual terminal inspection during implementation.
No product code, build, runtime test, installation, credentials, commit, or remote write occurred in this planning turn.

## Final presentation and recovery convergence

The user requested continued planning after selecting automatic terminal language.
Main reviewed the complete PRD, design, execution plan, and terminal component source findings together.
The design now shows one concrete Chinese progress view and its plain-text equivalent behavior.
It distinguishes cancellation before replacement from recovery after mutation.
Manual recovery uses the separate restoration context, so the canceled install context cannot immediately cancel its stop/start prompts.
Unavailable input leaves an explicit pending recovery action and the retained backup.
These details preserve the confirmed flows without adding another test matrix, prompt screen, or product prerequisite.

The complete proposal includes the three official forms, five platform bundles, PTerm dynamic/plain presentation, and automatic Chinese/English terminal locale.
The task remains in planning. No product implementation, dependency installation, build, test, deployment, credential operation, or commit occurred.

## Implementation approval

The user approved the complete consolidated plan on 2026-11-04.
The task is active with status `in_progress` on `feat/plugin-build-inspection`.
Main updates the affected delivery specifications and task records.
One implementation owner handles the coupled installer, builder, focused existing tests, four workflows, and requested usage instructions.
Independent review follows the completed candidate and reuses its valid build evidence.
No deployment change, personal credential use, work commit, or push is authorized by this approval.

## Implementation and acceptance

The four kits now share the three-form installer, PTerm dynamic/plain interface, automatic terminal locale, five-platform builder, and artifact workflow.
Root and template usage instructions describe the current paths and flows. Eval's restored README remains unchanged by this child.
The root and eval delivery specs now cover supported targets, startup owners, cancellation, payload selection, and publication recovery.

Independent source review found two defects. Both are repaired and reviewed.
Output publication now stages the complete candidate on the destination filesystem before directory rename and restoration.
The existing failure-preservation case covers partial-copy and publication-rename failures.
The message catalog now translates the installer-owned executable mismatch reason.

The default combined build exited with status zero and produced all five program/installer pairs under `dist/build/<os>-<arch>/`.
It passed frontend compilation, plugin checks, focused vet, four common builder cases, and the complete installer suite.
The running builder loaded the previous publisher before its repair. The completed outputs then passed through the corrected publisher successfully.
This local publication check reused the compiled programs rather than repeating the complete build.

Actual PTY checks covered Chinese selection, path input, timed spinner shutdown before version confirmation, and Ctrl-C before mutation.
Plain redirected output used English under `LC_ALL=C`, numbered input, no cursor escapes, and blank-confirmation cancellation.
The exact CI packaging shell produced five archives, each containing the matching two executable files.
All four build kits remain aligned. Diff formatting passed.

AC5-AC11 are complete with this evidence. Detailed results are in `research/implementation-result.md` and `research/implementation-check.md`.
The build log is `/tmp/sub2api-installation-build.log`.
Remote Actions and real Docker, Apple, or systemd installations were not run. Cross-compilation does not establish runtime installation on every target.
Work commits and the task finish workflow remain pending. Existing remote-operation authorization boundaries still apply.

## Readiness rendering repair on 2026-11-05

The user supplied repeated dynamic readiness frames with long clipped lines and requested repair, Docker installer checks, and CI output confirmation.
The earlier short terminal checks did not establish correct long-wait rendering. AC10 is open again.
The existing implementation owner handles reproduction, repair, four-kit synchronization, affected installer builds, and isolated Docker verification.
Main checks the actual CI output contract and updates task/spec records. Independent review follows the repaired candidate.
The user authorized test containers. Existing unrelated containers remain outside this test scope.
CI currently packages five platform tar archives, each with its matching native program and installer. Windows names add `.exe`.
Parent builds combine active plugins. Standalone plugin builds apply their own patches. The empty template builds original upstream code.
Failure logs upload only after a failed build step. Publication remains Actions artifacts only.

The implementation owner reproduced 113 retained readiness rows during an 11.2-second wait in a 40-column terminal.
PTerm's spinner only returned to the line start. Long state frames wrapped and left earlier rows behind.
The repaired frame keeps a short stage and one live timer. PTerm's existing AreaPrinter handles wrapped rows and CJK width.
Stopping joins the spinner before closing the area. Plain logs retain full readiness state and final failures retain actual diagnostics.
The four kits share the repair. The delivery specs now distinguish dynamic and plain readiness output.

Corrected 40-column English and 24-column English/Chinese captures retained one progress area through the full wait.
Eight synthetic packages from four kits passed real Docker replacement, delayed readiness, and same-container restart on arm64 and emulated amd64.
A failed candidate also passed stopped-container restoration. Complete common installer suites passed on both Linux architectures inside Docker.
A real native manual-process fixture passed stop/start prompts, backup retention, readiness, and permission preservation.

Actual combined Linux arm64 and emulated amd64 products separately passed version, plugin page, installer replacement, readiness, and restart checks.
The five actual installers were rebuilt from unchanged actual server programs in a module separate from fixture staging.
Independent follow-up review passed source and observed evidence. AC10 is complete again.
The report is `research/spinner-docker-check.md`. Raw captures and logs are under `/tmp/sub2api-spinner-check/`.
Only this check's isolated Docker resources were removed. Systemd and Apple remain command fixtures. Darwin and Windows were not executed in Docker.

Main confirmed that all four workflows are identical and each repository has only the current `build.yml` workflow.
Success publishes five platform tar artifacts. Each contains its native program and self-contained installer, with `.exe` on Windows.
Parent builds combine active plugins. Standalone plugin builds contain only their own changes. Empty templates contain original upstream code.
CI was inspected locally. No remote run, personal credential use, commit, or push occurred.

## Direct executable artifacts

The user removed tar packaging and supplied a versioned platform filename rule.
Raw programs use `sub2api-plugins-<upstream-tag>-<os>-<arch>`.
Installers use `sub2api-plugins-installer-<upstream-tag>-<os>-<arch>`. Windows files add `.exe`.
The selected tag includes `v`, for example `v0.2.19`. Canonical application metadata remains `0.2.19`.
CI uploads all ten executables directly. It retains validation, failure diagnostics, exact Action tags, and artifact-only publication.
Five platform directories remain under `dist/build/`. No old filename aliases or tar packages are part of the updated output.
Main synchronized the current child, parent delivery design, and root/eval specifications before implementation.

The four builders, workflows, common build fixtures, and root/template usage instructions now implement this delivery rule.
All ten retained actual programs were renamed without recompilation. No legacy aliases or old tar files remain under the output paths.
The existing four builder cases passed. The actual workflow validation shell passed against the renamed outputs.
Every direct upload path identifies one nonempty executable. Independent source and path review passed.
See `research/direct-artifacts.md` for the exact filenames and evidence. Prior runtime evidence remains valid for unchanged program contents.

## Configurable upstream tag

The user requested an Actions tag input instead of a hardcoded upstream version.
Manual runs require `upstream_tag`. The shared builder receives the value through `UPSTREAM_TAG`.
The user confirmed that push and pull-request builds resolve the actual tag from the latest official upstream release.
Local builds without an explicit environment value use the same public resolver.
The resolved tag owns source selection, version metadata, test context, executable names, validation, and artifact upload paths.
Public lookup uses no user credentials. Failure stops the build without substituting an older version or the literal string `latest`.
The verified v0.2.19 outputs remain evidence for that build, rather than a claim of compatibility with an untested newer release.

The four builders, workflows, existing build fixtures, and requested usage instructions now implement this selection rule.
The existing four builder cases passed with non-baseline tag `v1.2.3-rc.4`, including metadata, source checkout, both linker values, and filenames.
Explicit overrides skip lookup. Release lookup failures stop before output publication and preserve existing products.
The production entry exports its selected tag once through `GITHUB_OUTPUT`. Existing test fixtures do not overwrite that output.
The actual CI validation shell and all ten upload paths consumed the exported tag successfully.

An initial public lookup encountered a transient TLS reset and failed without fallback.
Subsequent unauthenticated curl and the actual product resolver both returned the official release tag `v0.2.19` successfully.
No product fallback or credential use was added. Existing outputs were neither rebuilt nor renamed for this parameter change.
The source and evidence are recorded in `research/upstream-tag-input.md`.

## Preserve and synchronize the user's current CI changes

The user requested synchronization back to all three plugins and explicitly required preservation of their edits.
The current root workflow adds the editable manual input default `v0.2.19`.
The three plugin workflows now include that same single line. No other product paths changed during this synchronization.
Builders, installer sources, and common test support already matched and needed no rewrite.
Direct content checks and independent review confirm four-kit alignment. Scoped diff formatting passed without repeating builds or tests.
The user's root and eval delivery specifications already reflect this default and were preserved.
The current task contract now matches the user change, which supersedes the earlier no-default input requirement.
Automatic push/PR selection remains unchanged.

## Closeout preparation

All three plugin root LICENSE files now contain only the standard LGPLv3 text and original FSF copyright.
Direct content comparison and independent review passed. Eval preserves its original final newline.
Current task requirements now preserve the user's subsequent README edits instead of restoring an earlier file over them.
The final read-only review found no remaining local source-commit blocker.
Existing relevant build, browser, terminal, Docker, and focused-check evidence was reused without another test gate.

Task work paths are staged in all four repositories. Git signing is enabled in each repository.
Plugin commits must exist and be published before finalizing the parent's three gitlinks.
Unrelated bootstrap files and generated products remain excluded from work commits.
The retained dist binaries predate the final footer and LICENSE corrections and cannot serve as final delivery products.
Fresh remote CI products, template state, and publication remain pending under the parent task.
No work commit, archive, credential operation, or remote operation occurred during this preparation.

## Approved commits and publication

The user approved the complete commit plan and push, including its stated GitHub credential scope.
The four work commits were signed, verified, and pushed to each repository's main branch:

- Eval: `11fe7c91d377846a9e40bfc48ca7c061e0e72848`.
- Quota: `2c1f79f590e46a506b7e33d819ca19db4f306fa7`.
- Template: `350b9678206c0bb076281dc4d9d73fd35722dc59`.
- Parent: `66f17f75726c3fadd9a5bf8d0bc2924378d755e4`.

The parent commit records all three published plugin gitlinks.
The feature branch was merged into local main by fast-forward before publication.
GitHub reports the new template repository as public with `is_template=true`.
Automatic builds are running for all four work commits. Their final outcomes and artifacts remain parent acceptance work.
This child's implementation, focused verification, work commit, and publication are complete.
