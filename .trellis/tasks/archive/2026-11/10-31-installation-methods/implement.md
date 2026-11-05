# Implementation plan for official installation forms

## Stage

The user confirmed the three installation flows and selected user-controlled stop/start for unmanaged native programs.
The user approved the consolidated plan on 2026-11-04. This child is active for implementation.
Implementation and independent review are complete. The default combined build and actual terminal checks passed.
The 2026-11-05 readiness-spinner repair passed long-wait narrow-terminal checks and independent follow-up review.
The user authorized isolated Docker installer checks. Preserve unrelated containers and report unsupported host/runtime execution separately.
The latest delivery change removes tar packaging and names each direct executable with the upstream tag, operating system, and architecture.
Update the four builders, workflows, affected existing build fixtures, and requested usage instructions together.
Rename retained actual outputs without recompilation. Verify the affected builder checks and direct-upload paths, reusing existing runtime evidence.
The latest Actions change adds a required manual `upstream_tag` input and a public latest-release resolver for automatic runs.
Pass one resolved tag through the builder, metadata, tests, filenames, and direct upload paths.
Extend existing builder fixtures for explicit and automatic tag selection, resolver failures, and a non-baseline tag throughout the build flow.
Reuse prior runtime evidence. This parameter change does not require a full product build or another container matrix.
See [implementation evidence](research/implementation-result.md) and [review](research/implementation-check.md) for results and execution limits.

## Work order

1. After approval, activate the child and update delivery specs for the three forms and platform output layout.
2. Share the existing warning, backup, replacement, readiness, and restoration code while preserving Docker behavior.
   Integrate PTerm v0.12.84 for dynamic selection/progress, existing plain-stream interaction, and automatic terminal-locale Chinese/English messages.
3. Add native file replacement with official systemd control and user-controlled manual stop/start.
4. Add Apple runtime replacement and application-only restart, using the verified running-container recovery path.
5. Add platform-specific process handling, temporary paths, executable inspection, and separate installer-host/application-runtime payload selection.
6. Update the four aligned builders and workflows for one source preparation, five platform outputs, and platform artifacts.
7. Update only affected existing tests and exercise the changed terminal behavior during implementation.
   Run the default combined build once for the completed candidate and perform Trellis review.
8. Keep the explicitly requested root/template READMEs and delivery specs accurate. Present work commits through the existing approval process.

## Ownership and files

One implementer owns the coupled installer, packaging, and aligned copies in the parent, eval, quota, and template.
Main owns task records, specification integration, and final acceptance. An independent reviewer checks the candidate.
Affected paths are `scripts/installer/`, `scripts/build.py`, `.github/workflows/build.yml`, and existing flat `tests/`.
Use small platform-specific Go files where the operating system requires them.
Keep terminal integration and the small Go message catalog under `scripts/installer/`, aligned across all four kits.
Prepare the selected dependencies in the existing temporary installer module and retain original dependency license terms.
Preserve the user's current eval README and unrelated staged or unstaged work.

## Verification

Extend existing installer cases only for the new native and Apple control paths, including their distinct restoration behavior.
Reuse existing version parsing, confirmation, readiness, Docker rollback, and cancellation evidence. Do not repeat them per platform or mode.
Adjust existing build fixtures for platform output and embedded payload selection. Retain existing failure-propagation and previous-output preservation cases.
Do not add tests that mirror menu text, filenames, workflow YAML, or unchanged logging.
Extend existing installer cases only where needed for locale selection, plain-stream behavior, or interruption handling changed by terminal integration.
Do not assert every translation or multiply transaction tests by language and rendering mode.
Exercise a localized interactive selection, spinner-to-prompt transition, and cancellation using the actual terminal during implementation.
Reuse those observations with the existing plain-stream and transaction checks rather than creating a terminal snapshot suite.

Run `python3 scripts/build.py` once for the completed combined candidate.
It runs the existing frontend, plugin, common installer/build, and vet checks and compiles the required platform outputs.
Reuse that result during review. Repeat a check only after a relevant change or failure.
No runtime matrix, repeated standalone builds, coverage, race, generated deployment environment, or deliberate remote failure run is required.
Cross-compilation does not establish actual installation on a different operating system. State actual execution limits in the result.

## Recovery and authorization

Use the selected service or container owner for managed recovery. Manual recovery retains user-controlled stop/start.
Keep the backup and report incomplete restoration when recovery cannot finish.
Preserve program ownership, launch settings, database contents, and application files throughout replacement.
Do not change upstream update behavior, Compose definitions, images, or the Apple image marker.
Program rollback does not reverse database migrations.

The requested terminal component and localization replace the former static presentation restriction.
No new entry, manifest, logging framework, service manager, or deployment platform is part of this plan.
Actual deployment changes, personal GitHub credentials, work commits, and pushes retain their existing separate authorization boundaries.
The parent's pending remote CI publication scope remains separate from local implementation approval.
