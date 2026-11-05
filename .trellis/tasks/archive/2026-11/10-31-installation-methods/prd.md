# Support the three official Sub2API installation forms

## Goal

Extend the self-contained installer to the three official user-facing Sub2API installation forms and five published runtime targets.
Redesign its terminal presentation with dynamic interaction where supported and Simplified Chinese/English localization.

## Confirmed scope

The verified integration baseline is Sub2API v0.2.19. The user now selects the upstream tag through Actions input.
Official-source research and the current installer assessment are complete.
The user confirmed the three detailed installation flows and selected user-controlled stop/start for unmanaged native programs.
Downloaded and source-built native programs share one flow. Systemd is a startup method, not another installation form.
Compose storage variants share the Docker flow.

## Requirements

- R1. Include only installation forms maintained by upstream Sub2API and intended for users.
- R2. Group installations by runtime behavior: Docker/Compose, native executable, and Apple container.
- R7. Offer Docker/Compose, native executable, and Apple container installation in the existing self-contained installer.
  Keep one version-warning, backup, staged replacement, readiness, and restoration flow.
  Matching versions continue directly. Mismatched or unreadable versions warn and require explicit continuation.
- R8. Preserve Docker's numbered running-container selection and existing replacement/restart behavior.
  Report that ordinary image-based recreation replaces the installed program. Do not silently change Compose files or images.
- R9. Native installation uses the selected executable path. Downloaded and self-built programs use the same flow.
  Support the official Linux systemd service through its existing startup owner.
  Without systemd management, the user stops and starts the program through the original launch method.
  The installer backs up, replaces, checks readiness, and restores the program without taking over manual process management.
- R10. Apple installation replaces `/app/storage/runtime/sub2api` and controls only the selected application container.
  Preserve its persistent runtime volume, executable ownership, and base-image marker. Keep PostgreSQL and Redis running.
- R11. Cover upstream's published targets: Linux amd64/arm64, Darwin amd64/arm64, and Windows amd64.
  Select the application payload for its runtime, separately from the installer host.
- R12. Keep `python3 scripts/build.py` as the argument-free local and CI entry, with automatic source download, patch discovery, and tests.
  Prepare source and frontend once. Produce platform-separated outputs without repeating common business tests for each target.
  Name raw programs `sub2api-plugins-<upstream-tag>-<os>-<arch>` and installers `sub2api-plugins-installer-<upstream-tag>-<os>-<arch>`.
  Use the selected upstream tag, including `v`. Add `.exe` for Windows. Upload executables directly without tar packaging.
- R13. Keep equivalent installer/build/workflow copies aligned in the parent, both plugins, and template.
  Preserve exact Action version tags, artifact-only publication, concise output, and patch/test failure propagation.
  Manual Actions runs require an editable `upstream_tag` input. Preserve the user's workflow default `v0.2.19`.
  Pass the selected tag through source download, metadata, tests, filenames, and artifact uploads without another version authority.
  Push and pull-request runs use the latest official release's actual tag, as confirmed by the user.
  Local builds accept `UPSTREAM_TAG` or use that same public resolver when unset. Lookup failures fail without a version fallback.
- R14. Preserve settings, account data, configured data directories, and launch environments during executable replacement.
  Retain a usable backup and report incomplete restoration. Do not claim that program rollback reverses database migrations.
- R15. Redesign the installer's terminal interface around installation choice, target selection, current step, and final result.
  Use dynamic selection and in-place progress when an interactive terminal supports them.
  Use readable numbered prompts and plain output when terminal capabilities or redirected streams prevent dynamic rendering.
  Keep backup paths, version warnings, failures, and restoration outcomes visible without duplicate diagnostics.
  Do not present an artificial percentage for operations with unknown progress.
- R16. Provide Simplified Chinese and English for installer-owned user text.
  Select language automatically from the terminal locale, using the first non-empty value among `LC_ALL`, `LC_MESSAGES`, and `LANG`.
  Chinese locales select Simplified Chinese. Other, absent, `C`, and `POSIX` locales select English.
  Do not add a language menu, manual switch, configuration file, or language argument.
  Keep commands, paths, versions, and external command diagnostics unchanged.
  Preserve existing explicit-continuation and cancellation behavior in both languages.

## Acceptance Criteria

- [x] AC5 (R7, R8). Docker installation preserves the current selection, warning, readiness, cancellation, and restoration behavior.
- [x] AC6 (R7, R9). Native installation replaces the selected program and preserves its owner, configuration, and launch context.
  Systemd controls its existing service. Manual installations retain user-controlled stopping and starting, including recovery.
- [x] AC7 (R7, R10). Apple installation targets the persistent runtime file, restarts only the application container, and retains its image marker.
- [x] AC8 (R11, R12). Platform outputs contain matching native programs and installers, including the Linux payload needed by Apple container.
  The single default build runs common tests once and fails before publishing new outputs when patching or required checks fail.
- [x] AC9 (R13, R14). The four kits share the approved behavior and platform artifact layout without duplicate diagnostics or extra entry points.
- [x] AC10 (R15). Capable terminals show interactive choices and dynamic step progress. Plain output remains usable with redirected or limited terminals.
  Completed installation and restoration retain a readable result, actual errors, and the backup location.
- [x] AC11 (R16). Chinese and English cover selections, inputs, warnings, progress, manual stop/start, results, and restoration messages.
  Terminal locale selects the language automatically without another user interaction.

Completed research criteria AC1-AC4 are recorded in the research and progress files. They are not additional implementation gates.
R3-R5 covered that completed research. R6's planning approval boundary remains under Stage and Boundaries.

## Research Result

See [deployment forms](research/deployment-forms.md) for the official forms, comparisons, and published platforms.
See [current installer](research/current-installer.md) for the local implementation boundary and source anchors.
See [platform artifacts](research/platform-artifacts.md) for installer-host and application-runtime differences and current build constraints.
See [installation operations](research/installation-operations.md) for configuration, actual startup owners, upstream updates, and replacement operations.
See [terminal components](research/terminal-ui.md) for the PTerm selection, source-backed integration behavior, and terminal-locale language rules.
The confirmed installation flows are in [design](design.md). Work order and focused verification are in [execution plan](implement.md).

## Stage and Boundaries

The user confirmed the installation flows and requested a consolidated plan with redundant tests and added conditions removed.
The user approved the complete consolidated plan on 2026-11-04. Initial implementation and source review passed.
On 2026-11-05, the user reported repeated spinner lines during readiness and requested repair and Docker installer checks.
AC10 passed after the narrow-terminal repair, long-wait captures, isolated Docker checks, and independent follow-up review.
See [spinner and Docker evidence](research/spinner-docker-check.md) for the fixture packages, actual product checks, and runtime limits.
The default combined build and actual terminal inspection passed. See [implementation evidence](research/implementation-result.md) and [review](research/implementation-check.md).
Installation and recovery checks used local fixtures. No remote workflow or installation on every target platform ran.
Exclude community panels, forks, unmaintained examples, generic runtime possibilities, and development workflows.
This child is the active implementation task. The parent retains integration and unfinished parent work.
Keep the user's requested root and template usage instructions accurate. Preserve the user's current eval README.
Actual deployments, personal GitHub credentials, work commits, and pushes retain their existing separate authorization boundaries.
