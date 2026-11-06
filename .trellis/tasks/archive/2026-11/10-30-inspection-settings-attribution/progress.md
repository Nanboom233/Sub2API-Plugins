# Execution record

## Authorization

The user approved implementation after fixed output names and focused validation were agreed.
The task is in progress on `feat/plugin-build-inspection`.
Work commits and personal GitHub credential use still need separate approval.
Do not use `gh auth status`, authenticated reads, pushes, or remote repository creation yet.

## Owners

- `eval`: eval production patches, assets, existing business tests, and the affected manual fixture binary path.
- `builds`: complete build kits and workflows in all four repositories, plus template Chinese README.
- Main: licenses, template local Git setup, specs, integration, browser acceptance, and final handoff.

Workers must preserve one another's edits. They do not run independent full builds or duplicate test gates.
Use the default combined build for the completed candidate, then one Playwright session.

## Current state

Main added LGPL roots and original license inputs for eval, quota, and the template.
Main retained the parent's MIT scope and added the official GPLv3 text.
The template is initialized locally on `main` under `plugins/sub2api-plugin-template`.
Its local origin URL and `.gitmodules` entry are prepared without remote access.
The template has no commit or staged gitlink yet. These follow work-commit approval.
Main updated inspection, detector, delivery, and directory specs for the approved contracts.
Both implementation owners finished their files. The `check` agent completed independent review and the first combined build.
The final corrected candidate passed the default combined build. Its log is `/tmp/sub2api-inspection-build-license.log`.
The eval README matches `9a56c08^:README.md` exactly. Its inherited MIT text matches the original root license exactly.
All standalone kits contain the required original GPL/LGPL texts. Eval's existing LGPL copy keeps its original final-newline form.
The Playwright session `plugin-inspection` is open and logged into the retained synthetic container on port 18080.
The retained container now uses the final built binary through its existing read-only bind mount.

## Verification

The first combined build passed, including all discovered tests, frontend compilation, `go vet`, and both fixed Linux/amd64 outputs.
The check agent reviewed all four kits/workflows and original license packaging. It fixed one added whitespace-only line.
The retained container mounts `dist/build/sub2api-plugins` at `/app/sub2api-bin`; restarting loaded the new binary.
The attempted Docker copy reported a busy mount. No copy was needed. The new runtime serves the changed page and reports 0.2.19.
Playwright confirmed the independent notification switch, field hiding with retained topic, gray configured placeholder, LGPL footer, and two-column Pelican placement.
At an iframe width of 726px, Pelican has no horizontal overflow and its button uses `grid-column: auto`.
Screenshots are under `/tmp/.playwright-cli/`.

The user rejected clearing an entered secret during the same page session.
Playwright reproduced this bug with a routed synthetic settings API: input length changed from 27 to 0 after automatic save.
The response's redacted empty secret overwrites the input after the save clears its dirty marker.
PRD, design, implementation notes, and inspection spec now require same-page masked retention, with empty input only on fresh reload.
The eval owner fixed the existing UI owner and existing test case. No separate suite or browser secret storage was added.
The second default combined build passed and emitted a new binary with same-page retention.
The affected Playwright path then found a second issue: blur emits a password `change` event after automatic save.
That event marks the already saved value dirty again, causing an unrelated toggle save to resubmit it.
The eval owner restricted password edits to input events and extended the same existing asynchronous case with the blur/change event.
The final default combined build passed with that correction and produced both executable Linux/amd64 outputs for version 0.2.19.
Playwright then verified the final candidate against a routed synthetic settings API in the retained container.
The input started empty. A successful HTTP 200 save retained all 28 synthetic characters as a password input.
Blur, notification toggles, and settings-tab revisits retained that value. An unrelated toggle PUT sent an empty password.
Reloading cleared the input and showed `已配置，留空保持不变` with placeholder color `rgb(156, 163, 175)`.
Screenshots: `/tmp/ntfy-same-page-retention-final.png` and `/tmp/ntfy-fresh-load-placeholder-final.png`.
The route was removed and the page reloaded. The test did not change stored settings or send a public notification.
The final `trellis-check` review found no remaining issue in the retention fix or its existing asynchronous test case.
The parent page's blocked inline-script console entry does not affect the settings iframe or the verified save flow.
Actual GitHub template state and four CI runs require later remote authorization.
No artificial remote failure run, naming compatibility suite, or standalone workflow-lint gate applies.

## Full-scope Trellis review

The user requested the final Phase 2.2 review across the complete task.
The check agent loaded both affected spec layers and reviewed parent, eval, quota, and template changes.
It confirmed aligned builders, installers, common tests, and workflows, with once-per-build common execution and empty-template exclusion.

The review found two CI reporting defects and one missing original dependency license.
All four workflows now name missing, empty, or non-executable outputs in annotations and job summaries.
Package and upload failures report their own errors. Only an actual build-step failure attaches its build log as diagnostics.
Shell messages use a single-quoted printf format, so output paths cannot become command substitutions.
Temporary shell probes verified successful packaging, failure exit statuses, summaries, and no execution of fixture output files.
These checks added no committed test suite or workflow gate.

Eval now includes the official Lucide ISC license and its Feather-derived MIT notice in `licenses/Lucide-LICENSE.txt`.
The exact source revision and copied-icon context are recorded in `research/eval-license.md`.
The changed installer license payload required one new default combined build, which passed.
`TestEntryAndEmbeddedPayload` verified that collected license contents match their embedded installer copies.
The final executable sizes are 136,290,464 bytes for the server and 51,757,216 bytes for the installer.
Both outputs are executable Linux/amd64 ELF files. Existing browser behavior evidence remains valid because runtime code did not change.

Main synchronized the parent's delivery spec and eval's six tracked backend specs with the implemented contracts.
No local acceptance defect remains after these repairs.
The exact-restored eval README retains historical installation/output names and build arguments under R3. It was not rewritten.

Local evidence completes AC1-AC4, AC6-AC9, and AC13.
AC5 awaits approved work commits and updated gitlinks.
AC10-AC12 await the template's remote state and the four actual workflow/artifact results.
AC14 has passing local failure-path checks and workflow review. Actual remote execution remains pending with the other CI criteria.
Work commits, personal GitHub credential use, and task archival have not been authorized or performed.

## User-requested build on 2026-10-31

The user requested another default combined build. `python3 scripts/build.py` completed with exit code 0.
Log: `/tmp/sub2api-plugins-build-20261031.log`.
Frontend type/build, plugin tests, common build and installer tests, and `go vet` passed.
The build emitted both executable Linux/amd64 static ELF outputs with version 0.2.19.
The server is 136,290,464 bytes. The installer is 51,757,216 bytes.
The check agent's model connection failed after launching the build. The build continued and finished successfully.
The resumed session recovered the original completion result without rerunning the build or tests.

## Diagnostic duplication review

The user requested a read-only review of redundant logging across all four CI/build/installer kits and affected plugin paths.
Two output paths repeat content: CI summaries copy the last 40 build-log lines, and non-quiet Docker failures can print details twice.
The latter prints command output in `docker()`, then includes those details in the returned error printed by `main()`.
Recommended cleanup: keep summaries to status and diagnostic locations, and print Docker failure details through one error owner.
The required failure build-log artifact remains distinct as a downloadable diagnostic copy. Successful product archives contain no build log.
Build command context, installation progress, readiness, and restoration results each serve a separate purpose.
Expected fixture failures remain visible in common-test output. They verify failure propagation and are not repeated real build failures.
The quota usage catch retains an upstream `console.error` with the error object. This is extra console noise, not duplicate plugin logging.
Default quota errors remain hidden in the page. Custom-script errors retain their required visible result.
This review changed no product code or workflow. No build or tests were repeated.

## Output simplification research

The user requested research before output changes. Findings are in `research/output-conventions.md`.
The researcher checked GitHub CLI, pip, Docker CLI, and official GitHub Actions documentation against original sources.
The preferred direction uses existing standard-library streams and GitHub features, with one owner for each detailed error.
The proposed changes remove summary log tails, duplicate patch progress, and duplicate Docker failure output in all four kits.
Docker output is already buffered. Forward successful non-quiet output, and return failed-command detail for the final error owner to print once.
Use existing test capture boundaries to hide expected failure output while preserving diagnostics when an assertion fails.
Keep downloadable failure logs, the final build failure context, readiness progress, backup paths, and restoration outcomes.
Do not add Cobra, a logging framework, verbosity options, another output protocol, or another build entry.
The quota console catch does not duplicate a page message. This proposal does not broaden into other native account catches.
These are research recommendations. No product, workflow, test, or executable spec changed in this research step.

## Revised task plan

The user requested a consolidated complete plan with redundant tests and added conditions removed.
PRD R16 and AC15 now cover output simplification. R14 and AC14 require concise summaries without copied log tails.
The design records one output owner using existing standard-library and GitHub facilities.
The execution plan separates completed evidence from remaining output changes, commits, and remote acceptance.
Only existing Docker-helper assertions and failure-fixture capture change. No new test suite or output-string/YAML mirror tests apply.
One final combined build runs all existing checks for the changed candidate. Do not run each aligned kit locally or repeat valid browser evidence.
The existing four remote workflow/artifact checks remain the CI acceptance path, without deliberate failure runs or a generated test repository.
Context manifests include the completed output research. Original requirements, approval boundaries, and README restoration remain intact.
The revised output work awaits review of the complete plan. No product code changed during this planning pass.

## Approved output implementation

The user approved the revised complete plan. Output implementation is in progress under the existing task.
The `output_implement` owner handles all four code/workflow/common-test copies and one final combined build.
Main owns spec and task synchronization. Independent Trellis review follows the completed candidate.
Work commits and personal GitHub credential use still require their separate approvals.

## Output candidate verification

The implementer updated all four aligned builders, installers, workflows, and existing common tests.
Patch progress now comes from the command runner alone.
Docker command failures return captured detail without also printing it. Successful non-quiet commands retain their buffered output.
CI summaries no longer copy log tails. Diagnostic links use the upload action's actual artifact URL.
The existing expected-failure fixture captures Python and child-process output and reveals it on an unexpected assertion failure.
The existing Docker-helper test checks quiet/non-quiet success and a single detailed error owner.

One default combined build completed with exit code 0. Log: `/tmp/sub2api-output-build.log`.
Frontend checks, plugin tests, common build cases, installer cases, and `go vet` passed.
The successful build log contains no expected-failure fixture error output.
Both fixed outputs are executable Linux/amd64 static ELF files with build version 0.2.19.
No standalone suite, repeated build, browser session, public notification, or remote operation was added.
Main synchronized the parent and eval delivery specs. Independent final review is pending.

The primary review agent's model endpoint failed twice with HTTP 503 before review completion.
A separate available review agent followed the Trellis check skill and completed the independent local review.
It found no blocking issue and confirmed all five changed file groups are aligned across the four repositories.
It checked expected-failure capture, Docker error ownership, rollback preservation, artifact conditions, and actual diagnostic URL use.
The reviewer reused the final build and prior full-task evidence without another test run.
AC15 is complete. AC14 has passing local implementation evidence and still awaits its planned actual CI acceptance.
The local implementation and spec synchronization are complete. Work commits, gitlinks, template remote state, and CI remain pending.

## Requested complete CI recheck

The user requested another full review, especially CI. A reviewer traced clean-checkout source composition and all workflow stages.
The preferred Trellis review model again returned HTTP 503. The available fallback reviewer used the same Trellis check instructions.
It found a real artifact-name defect that earlier reviews missed.
`upload-artifact` with `archive: false` ignores `name` and uses the uploaded file's basename.
The former `dist/sub2api-plugins-installer.tar` would therefore create the wrong artifact name.
All four workflows now create and upload the tar at `dist/sub2api-plugins-installer` and omit the ignored product `name` input.
The two executable outputs remain under `dist/build/` with their existing names.
The template README shows extraction into a separate directory so the download cannot overwrite itself with the enclosed installer.
Eval's exact-restored README remains unchanged.

The reviewer verified Action inputs, Node 24 Action runtimes, direct-upload naming, and artifact URL generation against official source.
It reviewed checkout/submodules, standalone discovery, dependency setup, exit propagation, skipped uploads, diagnostics, and removed Release triggers.
The changed package shell passed in a temporary directory. Tar members were exactly the two expected executables with mode 0755.
Both extracted files retained execution bits. Four workflow copies and diff formatting checks passed.
Only workflow packaging and the template usage text changed. Existing product build and test evidence remains valid.
The parent/eval delivery specs, design, and existing CI research now record the verified direct-upload naming behavior.

No further local defect was found. Actual Linux CI toolchain execution, remote template state, approved commits/gitlinks, and four uploaded artifacts remain pending.
No personal credentials, remote runs, commits, or pushes were used during this recheck.

## Requested patch persistence assessment

The user requested an additional check of patch persistence after container restart and migration.
Patches, frontend resources, and eval resources compile into the replacement executable.
The installer stages and renames that executable over `/app/sub2api`, then restarts the same container.
It does not change the image, Compose configuration, or mounts.
The upstream v0.2.19 entrypoint executes the installed program without replacing it during startup.

An ordinary restart preserves the replacement in the same container's writable layer.
Recreation from the original image, including migration with only database and data volumes, does not preserve the replacement.
The upstream Compose file persists `/app/data`, not `/app/sub2api`.
Keep the built installer and server. Reapply the installer after recreation or migration to a new container.

Settings and account state reside in PostgreSQL. Eval history resides in the configured data directory under `codex-eval/history.json`.
Both database and file data need their normal migration. In-memory work and scheduling state do not survive process restart.
The host `/tmp` executable backup is a recovery aid, not long-term persistence.

This was a read-only source assessment. The Docker daemon was unreachable, so no actual container restart or migration was tested.
The existing test container's host-bound executable does not establish normal installer persistence across recreation.
No product code, deployment configuration, or tests changed for this assessment.

## Requested parent license-scope move

The user requested a Chinese root README for the license scope.
The root `LICENSE` now contains only the original MIT text and `2026 Nanboom233` attribution.
The new Chinese `README.md` states the same scope and links to `LICENSE` and `licenses/`.
The task requirements, design, execution boundary, and specs now identify the new location.
Text, existing link targets, and diff formatting were checked. No product build or tests were needed for this documentation change.

## Requested exact Action version tags

The user requested exact release tags instead of commit hashes in CI references.
All four workflows now use checkout `v7.0.1`, setup-python `v7.1.0`, setup-go `v7.0.0`, setup-node `v7.1.0`, and upload-artifact `v7.0.2`.
Both artifact upload steps use the same exact tag. Redundant version comments were removed.
The existing verified release evidence applies to these tags. No dependency version or workflow behavior changed.
The PRD, design, research, and parent/eval delivery specs now use this reference policy.
The four workflow copies match, active workflow references contain no commit hashes, and scoped diff formatting passed.
No build or remote workflow run was repeated for this reference-only change. Actual remote CI acceptance remains pending.

## Requested Chinese usage and build instructions

The user requested installation and build instructions in the parent README.
The Chinese README now covers artifact download, separate-directory tar extraction, target-host requirements, container selection, and installer behavior.
It explains version confirmation, retained backups, restoration, and reinstallation after container recreation or migration.
Build instructions cover prerequisites, recursive checkout, submodule initialization, the single build entry, automatic tests, and fixed output paths.
They distinguish combined and standalone builds and explain that outputs target Linux/amd64 even when built on another system.
The license scope remains in the README. Eval's exact-restored README stays unchanged.
The implementer checked commands and paths against current source. Main reviewed the complete document and corrected target-host wording.
Document and diff checks apply to this change. No product build or remote run was needed.

## Requested installation-support child task

The user explicitly requested a child task for broader Sub2API installation support, starting with deployment research.
Created and linked `10-31-installation-methods` in planning. The parent remains active.
The child PRD defines the deployment inventory, persistence and recovery comparison, and evidence requirements.
Local installer coverage is recorded in the child's `research/current-installer.md`.
Research covers official-maintained, user-facing installations. No installer or deployment changes are authorized at this stage.

The child survey is complete. The user narrowed it to Docker/Compose, native programs, and Apple container.
Release downloads and source-built programs share the native form. Systemd and manual launch are startup details.
Community examples, generic runtime possibilities, and development workflows were removed from its report.
Apple container uses a persistent runtime program, so normal container recreation does not imply program loss for that deployment.
The child remains in planning. Its recommended installation mechanisms and unresolved implementation selections are in its research artifacts.

On 2026-11-01, continued child research traced actual update/restart operations and host/payload platform differences for those three forms.
The upstream updater cannot install custom local builds. Apple needs a Darwin host installer with a Linux/arm64 application payload.
The findings and existing-source constraints are in the child's operational and platform research reports. Product implementation remains unapproved.

On 2026-11-04, the user requested installation planning and selected user-controlled stop/start for unmanaged native programs.
The child now has proposed requirements, design, execution plan, and curated context for the three official installation forms.
Its platform artifacts, shared checks, and Apple-specific recovery remain subject to final plan review. The parent remains active.

The user subsequently confirmed the child's detailed flows and requested consolidation without redundant tests or added conditions.
The flows are recorded in the child design. Its PRD and execution plan now separate completed research from focused implementation acceptance.
Independent read-only review found no material drift or added gate. The consolidated complete plan awaits implementation approval.

The user added dynamic installer terminal presentation and Chinese i18n to the child plan.
The child now includes capable-terminal rendering, plain-stream output, Chinese/English message selection, and existing single-owner diagnostics.
This presentation change preserves the confirmed three installation flows and adds no duplicate language/runtime test matrix.

The user then chose automatic terminal-language detection instead of in-installer language switching.
The child now resolves the first non-empty `LC_ALL`, `LC_MESSAGES`, or `LANG` value and shows Chinese or English accordingly.
Language menus, manual switches, and operating system UI-language lookup are excluded from the current plan.

The user approved the complete child plan on 2026-11-04. The child is now the active implementation task.
Its three-form installer, PTerm terminal presentation, automatic locale, and five-platform output layout supersede earlier delivery limits.
The parent PRD and design now reference the approved platform pairs and artifact basenames.
Parent integration, approved work commits, and pending remote operations retain their existing ownership and authorization.

The child implementation and independent local review passed on 2026-11-04.
Its default combined build produced five platform program/installer pairs and passed the existing required checks.
Actual terminal interaction and the CI packaging shell passed local checks.
The four kits and requested usage instructions now share the approved installation and output behavior.
See the child's implementation and review evidence for the output-publication correction, terminal observations, and execution limits.
Pending work commits, template publication, gitlinks, and authorized remote CI remain parent follow-up work.

The user subsequently removed tar packaging and requested versioned executable names.
The four kits now upload ten files directly, using `sub2api-plugins-[installer-]<upstream-tag>-<os>-<arch>` and Windows `.exe`.
Current parent/child contracts and root/template usage instructions reflect this rule. Retained verified binaries were renamed without recompilation.
Existing builder tests, actual CI validation, and independent source/path review passed. No remote workflow ran for this change.

## Original evaluation footer restoration

The user requested removal of the assistant's unapproved footer rewrite.
The original footer retains CPA attribution, its upstream MIT link, and the existing dynamic version.
The replacement LGPL link and added Sub2API and GPL/LGPL entries must be removed from the UI patch.
The PRD, design, and page specification now preserve this boundary. License files retain their separately requested corrections.
This supersedes the earlier LGPL-footer plan and its browser observation. Those records describe the former candidate, not current acceptance.

The user then authorized one specific addition immediately after the original MIT link.
Add `LGPL` linked to `https://github.com/Wei-Shaw/sub2api/blob/main/LICENSE`, using the existing separator and external-link attributes.
All other original footer content remains. No additional Sub2API, GPL, or adaptation-license entry is requested.
The current PRD, design, and root/eval page contracts reflect this precise addition.

The final footer now contains the original CPA attribution, original MIT link, the single requested upstream LGPL link, and dynamic version.
Removing the new LGPL span produces the exact original footer. The UI patch applies successfully and declares the correct 184 HTML lines.
Playwright confirmed the final text, link order, destinations, and visible layout. The temporary page server and browser session were closed.
Evidence is in `../10-31-installation-methods/research/footer-restoration.md`.
This change updates the production patch. Existing server and installer binaries were not rebuilt and still contain the earlier footer.

The user clarified the added link's exact label as `LGPL-3.0`. The link destination and all other footer content remain unchanged.

The user then requested an Actions upstream-tag input and confirmed latest official release selection for automatic push/PR builds.
The four kits now pass one selected tag through source checkout, metadata, tests, executable names, and direct artifact upload paths.
Manual `upstream_tag` has no default. Local `UPSTREAM_TAG` overrides automatic public release lookup.
Existing builder cases, actual resolver smoke, and local CI output checks passed without a full product rebuild or remote workflow run.
The child task's `research/upstream-tag-input.md` records the implementation and evidence.

## Approved publication and remote acceptance

The user approved the complete commit plan and push after reviewing the explicit GitHub credential scope.
All four work commits are signed and published on main:

| Repository | Work commit | Automatic build |
| --- | --- | --- |
| codex-candy-eval | `11fe7c91d377846a9e40bfc48ca7c061e0e72848` | [41943966813](https://github.com/Nanboom233/codex-candy-eval/actions/runs/41943966813) |
| sub2api-quota-extension | `2c1f79f590e46a506b7e33d819ca19db4f306fa7` | [41943992185](https://github.com/Nanboom233/sub2api-quota-extension/actions/runs/41943992185) |
| sub2api-plugin-template | `350b9678206c0bb076281dc4d9d73fd35722dc59` | [41944017188](https://github.com/Nanboom233/sub2api-plugin-template/actions/runs/41944017188) |
| Sub2API-Plugins | `66f17f75726c3fadd9a5bf8d0bc2924378d755e4` | [41944176807](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/41944176807) |

The public template repository exists and GitHub reports `is_template=true`.
The parent work commit contains all three published plugin gitlinks.
The feature branch was merged into local main by fast-forward before its push.
The user's current README edits and editable workflow default `v0.2.19` remain intact.

The installation child is archived under `archive/2026-11/10-31-installation-methods` in signed commit `562fdc2`.
Native archival moved and staged its files, but the generated commit included an untracked old path and failed.
The same archive commit was completed using only the native-staged destination path. No lifecycle source changed.
The parent remains active while the four matching automatic builds and their direct artifacts are checked.
No duplicate workflow dispatch or local build was added.

## Cache and matrix planning

While the four real workflows ran, the user requested cache support and a multi-architecture build matrix.
This addition is R17/AC16 in the same parent task. It does not create another task or change the running workflows.
The earlier single-job compilation design is superseded by this requested planning scope.
Runtime test matrices, repeated business suites, and additional product build entry scripts remain excluded.

The template run completed successfully in 11 minutes 47 seconds and published all ten direct v0.2.19 products.
Serial server compilation began at 00:51:13 UTC, platform build commands continued through 00:56:46, and installers completed at 00:59:23.
The actual logs therefore identify serial multi-platform compilation as material optimization work.
The acceptance owner checked native executable headers for all ten template products and a complete installer payload/license sample.
Eval and quota subsequently completed successfully. Their artifact inspection is in progress.
The parent run is still building. Its outcome remains independent of the new planning work.

Source research found that common installer tests execute an embedded Linux/amd64 payload.
Preparation must provide that real program once, and the later server matrix can reuse it.
The preferred graph prepares source and tests once, compiles remaining servers in a matrix, builds installers in a matrix, then publishes final products.
Installers consume the native program and matching Linux payload. A final success dependency prevents partial product publication after matrix failures.
Official Actions artifacts transfer current-run state between jobs. They are separate from reusable Go and pnpm dependency caches.
Final design and cache details remain under official-source research. No product implementation is approved for this addition yet.

## Actual four-repository CI acceptance

All four automatic push runs passed on their exact published work commits:

| Repository | Run | Job duration |
| --- | --- | --- |
| Eval | `41943966813` | 16m53s |
| Quota | `41943992185` | 18m29s |
| Template | `41944017188` | 11m47s |
| Parent | `41944176807` | 20m17s |

Each run published ten versioned direct executables for v0.2.19.
The reviewer checked actual download headers for all forty files against ELF64, Mach-O64, PE, and the named architecture.
No product used tar or zip packaging.
Four complete Linux/amd64 installers were downloaded under /tmp without execution.
Each contains the matching embedded ELF program and all original license texts required by its repository.
The parent installer includes parent, eval, and quota license resources while excluding the empty template.
Actual logs confirm source refs/tags/v0.2.19 and both application and installer metadata version 0.2.19.
All output validation, product uploads, and result reports passed. Failure-log uploads correctly skipped on successful builds.
Existing local failure fixtures and source review remain the failure-path evidence. No deliberate failing remote build was added.
Downloaded programs were not executed. Existing local runtime checks remain applicable for unchanged installation behavior.
AC10-AC12 and AC14 are complete. The requested cache/matrix addition remains in planning under R17/AC16.

The official-source cache/matrix research is complete in research/ci-cache-matrix.md.
The final design retains the existing build.py entry with internal source/prepare/server/installer/publish stages.
Cache restore follows source preparation in the same prepare job. CI uses ignored dist/work so actual lockfiles are visible to hashFiles.
Prepare owns Go module and pnpm store saves. Go compilation saves have distinct target/role identities.
Official cache restore/save v6.1.0, download-artifact v8.0.2, and upload-artifact v7.0.2 are selected by exact release tag.
Standard Actions internal artifacts transfer prepared backend source, installer inputs, and programs. No manual tar packaging is added.
Four remaining server targets and five installer targets run as matrices after shared tests complete once.
A final publish stage keeps normal output validation and publication before all ten direct uploads.
The implementation plan and both context manifests reference the research. Product code remains unchanged pending plan approval.

## Platform/version inputs and restored Release planning

The user added platform and version selection, optional Release publication, and requested the Release title and body.
R18/R19 and AC17/AC18 extend the same current task. Existing upstream_tag remains editable with default v0.2.19.
Five platform booleans default true. Manual Release defaults false and uses a conditional separate plugin release tag.
Restore v* tag-push publication through a dependent job in build.yml rather than another build workflow.
Ordinary branch and PR runs remain artifact-only. Only Release publication gets contents write permission through the built-in token.

Dynamic server targets include selected native programs and their matching Linux payloads, excluding the prepared Linux/amd64 program.
Only selected platform pairs enter final artifacts and Release assets.
An expected empty server matrix must not skip downstream installer/publication jobs, while failures and unexpected skips still block products.
The release tag and actual source commit must match, including annotated existing tags. CLI target alone only creates an absent tag.
No existing Releases/assets are overwritten and no tags move. Publication reuses the exact successful built files.
Official-source findings and Chinese copy examples are in research/ci-cache-matrix.md and design.md.
The initial title/body proposal was superseded by the user's exact title and CHANGELOG-only body below.
No product code, new workflow, Release, tag, test, or build was created during this planning addition.

## Release title and CHANGELOG correction

The user selected the exact title shape `Sub2API-Plugin <hash> (v<upstream-tag>)`.
Use the built source commit's first seven hexadecimal characters and exactly one leading v on the upstream version.
All four repositories use that literal singular prefix. Example: `Sub2API-Plugin 66f17f7 (v0.2.19)`.
The body contains only the actual GitHub-generated CHANGELOG through `gh release create --generate-notes`.
The prior custom installation/platform/provenance body template was removed from the active PRD, design, execution plan, and research.
No additional CHANGELOG file or notes template is required. This correction changes planning artifacts only.

## Cache/matrix execution approval and check consolidation

The user approved the latest R17-R19 plan for implementation, then requested removal of redundant CI checks.
One implementation owner handles four aligned builders, workflows, and affected existing build fixtures.
Main updates specs and task records. Independent review follows the completed candidate.
Remove the separate Validate outputs shell loop, duplicated output assertions, and custom successful-upload status aggregation.
Builder output assembly and native Actions/job failures retain error ownership. Do not check executable access immediately after chmod.
Input selection and existing-tag commit ownership remain because native job/upload behavior does not establish those contracts.
No additional check entry, test suite, runtime matrix, checksum, or manifest is authorized by this consolidation.
The existing READMEs, licenses, business patches, and user changes remain outside this implementation boundary.

The implementer completed staged builders, five-job cache/matrix/Release workflows, and affected existing fixtures in all four kits.
The existing four-case builder suite passed in 11.066 seconds.
It covers staged Darwin/arm64 output with its Linux payload, a Linux/amd64 empty server group, tests once, and the default complete main path.
Existing failure cases retain old published outputs after compilation or required-file assembly failure.
Initial static YAML parsing found two single-line summary colon errors. Block-style run values corrected them and all five jobs now parse.
Artifact path and Release/job-barrier inspection is still in progress. No full build or repeated business/runtime suite was added.

## Local implementation review complete

The independent Trellis reviewer found no blocking issue in the completed candidate.
Prepared artifact paths, cache save ownership, planned empty-server skip, Linux payload closure, success barriers, and Release arguments match the approved design.
All four builders, workflows, and affected existing test files are identical by direct content comparison.
The reviewer reused the four passing builder cases and YAML/inline Bash syntax evidence without repeating suites.
The separate Validate outputs loop, repeated post-chmod checks, successful-upload status aggregation, and redundant Release existence preflight are removed.
Main updated root/eval delivery, index, quality, and directory specs and corrected stale current-state task statements.
Implementation evidence is in research/ci-cache-matrix-result.md.
No README, LICENSE, production plugin patch, or installer-runtime code changed in this increment.
The new workflow has not run on GitHub. Hosted cache/artifact/matrix behavior awaits reviewed commit publication.
No commit, push, or real Release occurred during this implementation increment. The parent stays active for remaining delivery.

## Single build job execution

The user approved the revised plan after the Go parallelism and upstream CI research.
The matrix implementation above is historical evidence. It no longer defines the current workflow design.
One owner now updates the workflows, builders, and existing builder cases in all four kits.
The replacement uses one build job, sequential target compilation, dependency caches once, and final executable artifacts only.
An optional Release job consumes those final artifacts. Custom summaries, duplicate downloadable logs, and intermediate artifact transfers are removed.
Source and resume remain separate steps in the same workspace so cache keys read actual downloaded dependency files.
Main synchronized the parent and eval backend specs with that contract.
The owner completed the twelve product files: workflow, builder, and existing builder tests in each of the four kits.
The existing four-case builder suite passed in 19.576 seconds.
All four workflows passed YAML parsing and their twenty inline Bash commands passed syntax checks.
The three product files match across the four kits. Diff checks passed, and no Python cache remained after validation.
The candidate retains only source/resume stages and tag, pnpm, and platforms source outputs.
Main synchronized the detailed specs with that actual contract. Independent Trellis review passed without findings.
The review confirmed cache timing, selected payload closure, build-success upload barriers, and unchanged Release permissions and tag ownership.
It reused the owner's passing checks. No repeated suite or syntax check was needed.
No new full product build, test suite, remote run, commit, or push is part of this local implementation increment.

## Single build job publication and trace

The user approved the exact four-commit plan, then requested push and trace through the existing GitHub credentials.
All four signed commits passed signature verification and are published on main:

| Repository | Commit | Automatic run |
| --- | --- | --- |
| Parent | `76dcd31025ed47a67d10adbd251882cee691addd` | [42043047594](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/42043047594) |
| Eval | `5d94e67a7823aeb659e98a863318796d7fb945ae` | [42042619011](https://github.com/Nanboom233/codex-candy-eval/actions/runs/42042619011) |
| Quota | `fb337bf1a3729b61b9229bb2241e31f3bd2efa7d` | [42042674565](https://github.com/Nanboom233/sub2api-quota-extension/actions/runs/42042674565) |
| Template | `45bdb4ef9ba120ce71bfa32570b9fc6a22c3d22c` | [42042766584](https://github.com/Nanboom233/sub2api-plugin-template/actions/runs/42042766584) |

The parent gitlinks identify those exact plugin commits.
All four matching automatic push runs passed:

| Repository | Build duration | Final artifacts |
| --- | --- | --- |
| Parent | 20m19s | 10 |
| Eval | 19m03s | 10 |
| Quota | 15m51s | 10 |
| Template | 12m19s | 10 |

Each inventory contains the five v0.2.19 platform program/installer pairs, including Windows .exe names.
No internal artifact, tar archive, or duplicate diagnostic log appears in those inventories.
Artifact lists remained empty during sampled compilation, before the final upload steps.
Native logs confirm source/resume in one build job, frontend compilation and vet once, and common build/installer tests once.
Each native server and installer target compiles sequentially with version metadata 0.2.19.
The new Go compilation cache key missed on all four runs. Normal builds completed and saved all four new compilation caches.
Module downloads reused prior caches. Eval, quota, and parent reused pnpm caches. The template populated its missing pnpm cache.
These first runs do not establish warm-cache timing. No extra build was added to measure it.
All four branch pushes skipped Release publication as intended. No duplicate workflow, manual dispatch, tag, or Release was created.
Manual subset behavior retains the passing local builder cases. Release title, tag ownership, permissions, and generated notes retain independent source review.
No executable format, payload, or runtime contract changed, so earlier format and embedded-license evidence remains applicable.
Native logs are retained locally under /tmp/sub2api-{parent,eval,quota,template}-<run-id>.log.
AC14 and AC16-AC18 now have their approved local, reviewed, and hosted evidence. Real Release creation remains untested as planned.

## Workflow input correction planning

The user requested removal of push builds, a platform dropdown, and a Release tag inherited directly from upstream.
R15/R18/R19 now describe PR/manual triggers, one `platform` choice, and no `release_tag` input.
Choices are `all`, `linux-amd64`, `linux-arm64`, `darwin-amd64`, `darwin-arm64`, and `windows-amd64`, defaulting to `all`.
Keep the manual `release` switch disabled by default. Use the source stage's actual tag for Release publication.
Retain the current title, generated CHANGELOG, single-job build, caches, default tests, and final-only artifact behavior.
The same correction applies to all four workflows. Update only the root README trigger sentence and affected delivery specs with them.
No product file changed during planning. Existing builder/hosted evidence remains valid. No new test suite or full build is required.
AC17/AC18 are reopened for this interface change. Implementation approval is pending.

## Platform multi-selection research

The requested researcher examined official GitHub input support and mature project workflow sources.
The report is `research/workflow-platform-selection.md`.
GitHub documents native `choice` as single selection. GitHub CLI, Microsoft OpenJDK, and Weasis accept comma-separated platform strings.
The researcher recommends existing checkboxes when graphical selection is required, or a `platforms` string when one field is preferred.
The proposed alternative to the user's rejected checkboxes is that string input, default `all`, mapped to the builder's space-separated list.
It preserves arbitrary subsets without an external interface, new build entry, or matrix.
The final interface remains pending user review. No product file changed.

## Two workflow fixes and README links

The user retained the existing platform checkboxes and explicitly authorized only the remaining two workflow fixes.
The user also requested direct GitHub repository URLs in the root README plugin table.
One owner changed all four workflows and the root README.
Push triggers and the separate release_tag input/preflight are removed. PR/manual triggers and platform checkbox mapping remain.
Manual Release publication inherits `needs.build.outputs.tag`. Title, generated notes, permissions, and tag ownership handling remain unchanged.
The three README URLs match `.gitmodules`. Its source-selection sentence now describes PR builds without push builds.
Parent and eval delivery specs describe the new trigger/tag contract.
All four YAML files and twenty inline Bash commands passed syntax checks. Workflow copies align and diff checks pass.
Independent Trellis review passed without findings. It confirmed event gates, inherited tag, retained permissions/tag handling, and README URLs.
No builder, installer, test, license, or plugin-patch file changed.
No suite, full build, remote workflow, commit, or push ran during this increment.

## Trigger and Release-tag fix publication

The user approved the exact four signed commits, push, and trace.
All four signatures verified and the commits are published on main:

| Repository | Commit |
| --- | --- |
| Parent | `8bac711f15057721bc4c5f746370dca301870dbc` |
| Eval | `0263c637ff54910a042294c0d9e05eb705c359eb` |
| Quota | `0115418005410cf138bad61e4449bab8436439e3` |
| Template | `1ea0e7a389a5c1613584e6400ec2e3ef3a50f649` |

The parent references those exact three plugin commits. None of the four pushes created a workflow run.
One manual parent build now traces the published candidate at [42056694011](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/42056694011).
Its inputs select upstream v0.2.19 and Linux/amd64 only, with all other platform checkboxes and Release disabled.
The manual run passed in 3m42s. Its Release job skipped as requested.
Its artifact inventory contains only `sub2api-plugins-v0.2.19-linux-amd64` and `sub2api-plugins-installer-v0.2.19-linux-amd64`.
Native logs confirm selected platform `linux-amd64`, one frontend build, shared checks once, and one server/installer compilation each.
Go modules, Go compilation data, and pnpm store restored from existing caches. The new source revision saved its updated Go build cache.
The final push-event query returned no runs for all four exact published commits.
No four-repository repeat build or real Release was created. Release-tag inheritance retains the passing independent source review.
The actual native log is retained at `/tmp/sub2api-trigger-fix-42056694011.log`.

## Manual run title

The user selected `Build v0.2.19 · main` after reviewing the supported expression contexts.
R20/AC19 records the manual format `Build <upstream-tag> · <ref-name>` without a run number or new input.
One owner added top-level `run-name` to the four workflows. PR runs keep their existing PR-title display.
The parent/eval delivery specs describe this same contract.
All four YAML files, workflow copy alignment, and diff checks passed. Independent review passed without findings.
No new tests, build, remote operation, commit, or push ran for this display-only change.

## Run-title commits and partial publication

The user approved the four exact signed commits and push, and reserved build testing for themselves.
All four commits passed local signature verification:

| Repository | Commit | Publication |
| --- | --- | --- |
| Parent | `a2c60ae9c0d4d8062a45139e85befb5f1f25d270` | Held until plugin commits are available remotely |
| Eval | `24d322a0bed7c3133f68eccb1a59b48763d6483b` | Pushed to main |
| Quota | `0d66b1b0dc2f1ec15e7f32f68fd189117a4ade14` | Remote rejected twice with `fatal error in commit_refs` |
| Template | `58944ac7ab191452d1d26845051573e2229bcb25` | Remote rejected with `fatal error in commit_refs` |

Quota's remote main remains at `0115418`. Template's remote main remains at `1ea0e7a`.
The GitHub commit API does not expose either failed commit. No remote branch move was observed.
GitHub Status reports Git Operations operational and no active incident. The returned page update was 2026-11-05T08:19:24Z.
The failures do not report a local conflict or a branch-policy rule. No force push, signing change, or API write workaround was attempted.
The parent commit references the exact three new plugin commits. Keep its push pending while quota/template commits are unavailable remotely.
Resume by retrying those ordinary plugin pushes after the remote failure clears, then push parent main.
No build was dispatched, run, or traced because the user owns build testing.

## Run-title publication retry

The user requested another ordinary push attempt. Quota and template pushes now succeeded without any commit or configuration change.
After those plugin commits became available, parent main pushed successfully to `a2c60ae`.
All four approved run-title commits are now published on main. The parent gitlinks match those plugin commits.
The earlier `commit_refs` failure no longer blocks publication. No build was dispatched or tested.

## Build and Release step consolidation assessment

The user requested assessment of a single Build and Release job, with optional Release as a conditional step.
The requested workflow/job display name is `Build and Release`, with job ID `build-release`.
The user also requested one cache-restore step, one final-artifact-upload step, and one cache-save step.
One researcher owns primary-source review of the pinned cache/upload Actions and GitHub permission rules.
The assessment must preserve direct individual executable artifacts, selected platforms, no push trigger, and the existing build entry.
Check whether one direct upload call supports multiple files and whether job permissions can retain the current read/write boundary.
No product change, permission change, new test, build, or remote operation is authorized by this assessment request.

The completed assessment is in `research/ci-step-consolidation.md`.
Cache restore/save supports multiple paths in one native call, with one shared cache key and archive.
The pinned upload Action supports only one file when `archive: false`. One normal multi-file call changes downloads to an archive.
Keeping individual raw files with one visible upload step would require a wrapper or an SDK-based upload loop.
Release can use local final files in the existing build runner, removing the second runner and final-artifact download.
However, its write permission would apply to the whole combined job. GitHub has no step-level permission or dynamic permissions expression.
The researcher recommends native cache consolidation while retaining direct uploads and separate Release permission ownership.
Main reports the supported choices and their actual contract changes for user review. No implementation decision has been inferred from this assessment.

The user requested deeper research on mature solutions for one artifact-upload step while preserving independent raw files.
The same researcher owns `research/artifact-upload-single-step.md` and will inspect maintained Actions and real SDK-based integrations.
The comparison must check actual raw-file support, current artifact APIs, dependencies, token requirements, naming, and failure propagation.
Do not substitute one ZIP artifact, ten zipped artifacts, or a hidden matrix for the requested independent raw outputs.
This remains research only. No product edit, dependency installation, remote workflow, or publication is authorized.

The follow-up report is `research/artifact-upload-single-step.md`.
The official `@actions/artifact@6.3.1` SDK supports `skipArchive` for one file per call.
One JavaScript action step can call that API for each selected executable and retain separate raw artifacts.
The inspected third-party batch action does not use this option and still creates ZIP artifacts.
The proposed integration uses `actions/github-script`, which does not bundle the artifact SDK.
Its script would install the exact SDK version under `RUNNER_TEMP`, import it, and upload each output.
This avoids a maintained local action bundle but adds a runtime npm install. Transitive dependencies remain unlocked.
The SDK needs runner artifact credentials. The repository token alone is insufficient.
The exact temporary-package import and remote uploads remain untested because this increment is research only.
Main recommends the official SDK direction and reports this integration cost. No product change was made.

## Corrected research: mature project upload workflows

The user rejected the Action-capability survey. The requested evidence is how mature projects organize multiple product uploads.
The previous SDK integration recommendation is withdrawn in its research report.
One researcher owns `research/mature-project-artifact-uploads.md`. Main inspected upstream Sub2API and RustDesk source separately.
Sub2API v0.2.19 uploads each target directory as one named Actions artifact. It later collects all targets and publishes through GoReleaser.
RustDesk's Flutter workflow publishes Windows MSI and EXE files together through one `files` list.
Its signed-update publication also lists seven platform installers in one Release upload step.
That workflow uses separate named Actions artifact steps for Windows EXE and MSI handoffs.
These examples distinguish one grouped Actions artifact from multiple independent Release assets in one publication step.
The current project already uses one `gh release create` command with a glob for all selected Release assets.
One native directory upload could simplify Actions artifacts, but it would change the current independent-file downloads to a ZIP bundle.
No product change or new packaging requirement follows from this research. Keep the raw-download requirement explicit when choosing the plan.

## SDK upload plan selected

The user selected the SDK approach and requested a concrete plan.
R21/AC20 and the design/implementation records now describe one inline JavaScript action step in each of the four workflows.
The step installs the official SDK under `RUNNER_TEMP`, imports it, and uploads each selected file with `skipArchive: true`.
It retains independent raw artifacts and current filenames. SDK setup and upload exceptions fail the build.
The proposed validation covers syntax, actual temporary-package loading, copy alignment, and independent review.
No new test files, full build, remote operation, or product edit ran for this planning increment.
The separate Release-job and cache-step consolidation proposals are not included in R21.

## SDK upload review and spec synchronization

Independent Trellis review found no workflow defect. It confirmed GitHub Script's injected `exec` helper and the SDK call contract.
The review reused the implementation owner's YAML, copy-alignment, real package-loading, and focused harness evidence.
Parent and eval delivery specs now describe the one-step SDK signature, environment fields, raw downloads, and native failures.
The SDK research report now reflects the approved implementation rather than its earlier withdrawn recommendation.
AC20 passes locally. Actual hosted uploads remain untested and are not an added acceptance gate.
No new persistent test files, full product build, commit, push, or remote workflow ran for this increment.

## SDK upload publication

The user approved the exact four commit messages with bodies and requested push.
All four signed work commits passed signature verification and pushed to `main`:

| Repository | Commit |
| --- | --- |
| Eval | `4586ac274f573b29ae51f9dbe2653f709587f013` |
| Quota | `577c74983b8cb05e55202da5975dd5abc96f4466` |
| Template | `b925a0c65833c54d289e91fe18cdfe0cb8597602` |
| Parent | `a82bb87` |

The parent records the exact three published plugin commits. Product working trees are clean.
No build was dispatched or traced. Actual hosted SDK uploads remain untested.

## Correction: omitted cache consolidation

The user identified the omitted request to combine cache restore and save steps.
Main incorrectly treated this original requirement as pending. R22 restores it to active implementation.
One owner consolidates all four workflows to one native multi-path cache restore and one matching save.
The combined key covers tools, actual dependencies, builder, and source revision. The restore prefix omits only the source revision.
Parent and eval delivery specs now record this shared cache contract.
No new test file, full build, remote run, or dependency wrapper is required.
The original Release-step consolidation and workflow/job naming request is still outstanding; it has not been cancelled by the user.

R22 is implemented in all four workflows. Each has one official multi-path restore and one save with the same three paths.
The save uses `steps.dependencies.outputs.cache-primary-key`, skips exact hits, and retains normal success handling.
One YAML/wiring check confirmed copy equality, paths, key/prefix relation, condition, and source/restore/build/upload/save order.
All four whitespace checks passed. Independent review passed with no findings.
The original reviewer hit two provider 503 errors. A separate available reviewer completed the same bounded source review.
AC21 passes locally. No tests were added or full build/remote run started. The correction is not yet committed or pushed.

## Cache consolidation commits

The user approved the four exact work commits with bodies. All four commits passed signature verification:

| Repository | Commit |
| --- | --- |
| Eval | `e8b044fbe8f6f0c35069e60acc9af7a4ef774d83` |
| Quota | `1e0f6fffea19de906688cebb6bfe45fa932a1de8` |
| Template | `1572f897c0dd6d53e9ce7d324e81ed9c21e978aa` |
| Parent | `ec992b4` |

The parent records those exact plugin commits. No push or hosted build ran for this commit-only request.

The user then requested push. Eval, quota, and template main pushed successfully before parent main.
All four cache-consolidation commits are now published. No hosted build was dispatched or traced.

## Corrected single-cache plan

The user rejected the remaining split cache flow and requested a corrected plan.
The proposed cache SDK wrapper was withdrawn before any workflow edit.
The earlier full-cache Action proposal was not approved. Do not treat automatic post-save as a user decision.
The designated `trellis-research` agent completed `research/cache-load-conclusion.md` on 2026-11-06.
Its preferred design declares explicit Go and pnpm cache paths in each workflow.
Use existing setup Action version outputs and delete `Locate dependency caches` and all `steps.paths` references.
Keep one native multi-path `Load caches` restore and one matching `Save caches` action.
Preserve primary-key saving, exact-hit skipping, dependency-compatible prefixes, and source-before-load ordering.
The local probe confirmed `pnpm_config_store_dir` with pnpm 12.16.1. The older `npm_config_store_dir` was ignored.
Tailscale and Vue provide workflow examples without a separate path-discovery step. Their examples do not prove combined Go/pnpm caching.
The revised design and execution plan are ready for review. Main has not dispatched implementation.
No product file has changed since the published cache-consolidation commits.
The original Release-step consolidation and workflow/job naming request remains outstanding in this task.

## Task cleanup for the latest decisions

The user requested a task review and removal of redundant tests and added requirements.
R22 now states one explicit cache load and one save, without a locate step.
R23 restores the original conditional Release step and `Build and Release` workflow/job names, using job ID `build-release`.
The design records job-wide `contents: write`, because GitHub does not support step-scoped permissions.
Release publication uses the current job's selected final files without downloading artifacts.
The SDK upload contract replaces obsolete upload-artifact instructions. Manual run titles remain unchanged.
The execution plan no longer schedules completed SDK, trigger, README, template, or run-title work.
Context manifests now contain only the relevant specs and cache/permission research.
Validation is limited to changed YAML/shell syntax, workflow wiring, four-copy alignment, and whitespace.
Reuse completed probes and build evidence. No tests, builds, dependency upgrades, hosted runs, or test Releases are added.
The parent remains active. The revised product implementation awaits review.

## Approved R22/R23 execution

The user approved the cleaned plan for execution.
Main dispatched `/root/cache_release_implementation` as `trellis-implement`, owning the four workflow files.
Main owns the delivery spec updates and task artifacts. Independent `trellis-check` follows implementation.
The approved scope retains existing dependency tags, SDK uploads, run titles, platform inputs, and build commands.
No commit, remote operation, hosted run, or product build is included in this execution approval.

The implementation owner finished all four workflows.
Each workflow now has declared effective cache paths, setup version outputs, one load/save pair, and one `build-release` job.
Release publication uses current selected files after SDK artifact upload and keeps the existing tag check and generated notes.
The owner passed YAML parsing, inline Bash syntax, cache/job wiring, four-copy equality, and whitespace checks.
Main synchronized parent/eval delivery specs and their backend indexes to these contracts.
Main dispatched `/root/cache_release_review` as `trellis-check` for the four workflows and four spec files.
The reviewer receives the implementation checks and reuses completed probe/build evidence.

Independent `trellis-check` passed and fixed one lifecycle regression in all four workflows.
It moved `Save caches` before `Create Release`, so a publication failure retains successful-build cache saving.
The reviewer verified final YAML parsing, inline Bash syntax, paths/conditions, direct Release assets, copy equality, and whitespace.
No unresolved in-scope finding remains. The approved job-wide write permission is retained.
Main synchronized the task and delivery specs to the final save-before-Release order.
AC21 and AC22 pass locally. Actual hosted SDK uploads and real Release publication remain untested, without adding an acceptance gate.
The code/spec candidate is ready for work-commit approval. No build, new test, dependency change, or remote operation occurred.

## R22/R23 work commits and push

The user approved the exact four-commit plan and requested push.
All commits use the approved subject and body and passed `git verify-commit` with the configured signing policy.

| Repository | Commit |
| --- | --- |
| Eval | `94ba5fc103ab8fc99aff313520ab181463334bdb` |
| Quota | `79c44f9c6baae5c562817e0bbfc141817780de56` |
| Template | `a498d8acc8a1e741d52abd9b5ce0ee1d1471170b` |
| Parent | `d8b6022` |

The three plugin main branches pushed successfully before the parent.
The parent records their exact new commits, and its main branch also pushed successfully to origin.
No unrelated untracked Trellis artifacts entered the work commits.
No hosted workflow or real Release was started. Task archival and session recording remain for finish-work.

## Remove the added Release-tag gate

The user rejected added restrictions after the four work commits were published.
Main identified the custom tag-to-build-commit equality gate as an added publication requirement and removed it from PRD/design/specs.
The existing implementation owner now removes its Git API preflight and the duplicate tag environment variable from all four workflows.
The Release command uses `UPSTREAM_TAG` directly and retains native CLI behavior.
No replacement policy, new test, build, remote run, commit, or push is included in this correction.

The implementation owner removed the custom tag gate and duplicate `RELEASE_TAG` variable in all four workflows.
Independent `trellis-check` passed and removed the no-longer-needed `GH_REPO` environment override.
The Release command now uses native repository discovery and `gh release create "$UPSTREAM_TAG"` directly.
The selected files, title, generated notes, target commit, cache flow, and SDK uploads retain their existing behavior.
Final YAML parsing, Release Bash syntax, copy alignment, and whitespace checks passed.
No in-scope issue remains. The correction is local and uncommitted. No new tests, build, or remote execution occurred.

## Release-tag correction commits and push

The user approved the exact four correction commits and requested push.
All four use `fix(ci): remove custom release tag restrictions` with the approved body.
Each commit passed signature verification under the configured signing policy.

| Repository | Commit |
| --- | --- |
| Eval | `324c7651b0ba192357fedfa692362c925c8923d1` |
| Quota | `022140c4018f1cad665728af188415db02bfb18e` |
| Template | `779d73610bf8a6e0bd7953590c38ecc07a86f689` |
| Parent | `91d10f4` |

All plugin commits pushed successfully to their main branches before the parent.
The parent records these exact new plugin commits, and its main branch pushed successfully to origin.
No new tests, builds, hosted runs, or real Release publication occurred.

## Approved repeated Release publication correction

The user identified the remaining duplicate-Release failure and approved its correction.
The current implementation creates absent Releases and updates the same-tag Release when already present.
Existing Releases receive the current title, GitHub-generated CHANGELOG, and selected same-name assets through CLI `--clobber`.
Other assets and tags stay unchanged. No tag-to-commit gate is restored.
Local CLI help confirms create, edit, upload, API fields/placeholders, and create-with-assets staging semantics.
Main updated requirements/design/specs. The existing implementation owner handles all four workflows, followed by independent review.
No new tests, product build, hosted run, or test Release is part of this correction.

The implementation owner completed the four `Publish Release` steps and passed YAML, Bash, copy alignment, and whitespace checks.
Independent `trellis-check` reviewed the actual create/update branches and matching delivery specs without finding a defect.
The existing-release branch updates title/generated body and overwrites only selected same-name assets.
The absent-release branch retains native create-with-assets staging. No tag/SHA precheck returned.
Main completed spec/task synchronization. AC18 passes locally. No real Release or hosted workflow was run.
The correction remains uncommitted pending the ordinary work-commit approval.

## Clear old Release assets before upload

The user corrected the repeated-publication plan: delete all old Release assets before uploading the new selected files.
This supersedes the earlier same-name-only overwrite and retention of other assets.
Main updated requirements, design, execution plan, and parent/eval delivery specs.
The existing implementation owner updates the four workflows. One query provides Release existence and the old asset names.
The update branch deletes every old asset before the new upload. The new-release branch remains unchanged.
Only the same-tag Release's attachments are affected. Its tag and Release object remain.
No real remote deletion or upload is part of local implementation and review.

The owner implemented delete-all-before-upload in all four workflows.
Independent review checked the combined staged/unstaged candidate and found no defect.
The single Release query lists old names. Empty output triggers no deletion.
Each old asset deletion completes before upload. A deletion failure exits before uploading under the existing Actions Bash behavior.
New-release creation is unchanged. YAML, Bash syntax, copy alignment, and whitespace checks passed.
The corrected candidate and parent/eval specs are ready for the revised work-commit plan.

## Repeated Release work commits and push

The user approved the revised four-commit plan and requested push.
Every commit uses the approved title `fix(ci): replace release assets on repeated publication` and body.
All four passed signature verification with the configured signing policy.

| Repository | Commit |
| --- | --- |
| Eval | `cfb9345a09e2e19d282abcae340cd4348c9044b3` |
| Quota | `2e6de85d7c6ca84091eacb7b41827daf110fefd6` |
| Template | `4a6919c9c81f5031b1f0c3274d8b51f63d9ac8f8` |
| Parent | `3ff444b` |

All plugin main branches pushed successfully before the parent.
The parent records their exact new commits, and its main branch pushed successfully to origin.
No new tests, builds, hosted runs, actual asset deletion, or Release publication occurred.

## Release recreation simplification implemented and checked

The user approved the simplified delete-and-recreate Release publication plan.
`trellis-implement` updated all four `.github/workflows/build.yml` files to run `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true` followed by a single `gh release create` command.
Independent `trellis-check` verified YAML parsing, Bash syntax, four-copy byte alignment, `git diff --check`, and full-scope task compliance without findings.
Main synchronized parent and eval `.trellis/spec/backend/minimal-linux-delivery.md`.
The user approved the four local signed work commits and remote push: eval `a8e4bf2`, quota `17fdf92`, template `3cc6282`, and parent `fbd92c7`. All four passed signature verification and pushed to `origin/main`.
Subsequently, the user requested squashing all 11 CI commits since `562fdc2` / `11fe7c9` / `2c1f79f` / `350b967`.
Each repository now has one signed commit on `origin/main`: eval `4e6d167`, quota `a6c145c`, template `b3c40dd`, and parent `2fc4e90`.
All four squashed commits passed signature verification and force-pushed to `origin/main`.

## SDK upload implementation

The user approved execution after removing redundant checks and added conditions.
All four workflows replace ten conditional file upload steps with one `Upload artifacts` JavaScript Action step.
Anonymous version checks selected `actions/github-script@v9.0.0` and `@actions/artifact@6.3.1`.
The wrapper installs the SDK in a unique runner temporary directory and dynamically imports its ESM entry.
It uploads each selected server/installer pair with `skipArchive: true`, preserving raw artifact names and Windows suffixes.
Missing files fail through the SDK's native `FilesNotFoundError`. Upload exceptions stop the loop and fail the step.

Local Node 24.21.0 and npm 11.19.0 installed the real SDK under `/tmp/sub2api-artifact-sdk.5l55oY`.
The actual ESM import passed. A temporary inline harness exercised the exact workflow script with SDK upload calls stubbed after import.
It checked ten default outputs, the Darwin/arm64-only pair, raw options, Windows suffixes, and first-upload failure propagation.
A real SDK invocation rejected a missing file before any service call.
Ruby's native YAML parser accepted all four workflows, and their contents matched. Diff whitespace checks passed.
No persistent test, product rebuild, hosted run, Release, commit, or push ran in this increment.
Independent review and spec synchronization remain with main.
