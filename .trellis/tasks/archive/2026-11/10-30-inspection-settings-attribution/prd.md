# Synchronize plugins, inspection, licensing, and artifact CI

## Goal

Synchronize the native evaluation plugin with the pinned upstream update.
Correct inspection defaults, saved-secret feedback, and independent verdict-based notifications.
Include the prepared README restoration and correct license scope and attribution.
Add a GitHub plugin template and CI with final artifacts and optional manual Release publication for all four repositories.
Simplify repeated build, installer, test-fixture, and CI output with existing tools and one owner for each detailed error.
Use dependency caches and one build job that compiles the selected targets in sequence.
Keep only final executable artifacts and native Actions failure logs.

## Requirements

- R1. Add `gpt-6.1-terra` to the default model-control removal list.
  Preserve the current entries and their order. Append the new model.
  Apply the default when no list is saved. Preserve saved custom lists and explicitly empty lists.
- R2. Show a gray placeholder in the ntfy password field when a saved password or token exists.
  Use `ntfy_password_configured` and the native input-placeholder pattern.
  Display `已配置，留空保持不变` with an empty input on a fresh page load.
  Keep a user-entered value masked in the same page session after saves and settings-tab revisits.
  A page reload starts empty again. Do not persist the entered secret in browser storage or return it from the API.
  Hide this placeholder when no secret is configured. Preserve newer input during asynchronous saves and reads.
  Preserve existing secret redaction and blank-update behavior.
- R3. Retain the evaluation plugin's restored Chinese README and the user's subsequent edits.
  The later instruction to preserve user changes supersedes exact comparison with `9a56c08^:README.md`.
- R4. Use `LGPL-3.0-or-later` for the quota plugin, which patches Sub2API services and frontend files.
  Replace its root MIT license with the unmodified standard LGPLv3 text, without project statements or explanations.
  Preserve original dependency licenses and attribution.
  Include official GPLv3 text under `licenses/GPL-3.0.txt` and retain the upstream Sub2API license.
- R5. Retain the parent MIT license and correct its copyright holder to `Nanboom233`, year `2026`.
  State that MIT covers the parent's own build and installer code.
  State that Sub2API and plugin code retain their respective licenses, including the bundled executable.
  Keep root `LICENSE` limited to the unchanged MIT text and correct attribution.
  Move the scope statement into a new Chinese root `README.md` with links to the license files.
  Include artifact installation and local build instructions in that README, using the current commands and output names.
  Link its plugin table directly to each plugin's GitHub repository URL instead of a relative submodule path.
  Explain prerequisites, automatic tests, and reinstallation after container recreation or migration.
  Add the official GPLv3 text as parent `licenses/GPL-3.0.txt`, alongside the existing Sub2API LGPLv3 text.
  The parent package must not depend on eval to supply these upstream license texts.
  Include the prepared attribution rule in `.trellis/spec/guides/index.md`.
  Update plugin/template references after their approved work commits.
  Preserve original evaluation and third-party license attribution.
- R6. Use `LGPL-3.0-or-later` for the evaluation adaptation, consistent with Sub2API v0.2.19's explicit license statement.
  Replace the evaluation root `LICENSE` with the unmodified standard LGPLv3 text, without project statements or explanations.
  Preserve the current MIT text, including `2026 Hao Wang`, in `licenses/CPA-Codex-Candy-Eval-MIT.txt`.
  Preserve existing third-party license texts and notices. Do not substitute another author for inherited work.
  Include the original Lucide ISC and Feather-derived MIT terms for the embedded icons under `licenses/`.
  Add the official GPLv3 text as `licenses/GPL-3.0.txt`, as required by LGPLv3.
  Preserve the original evaluation footer, including CPA attribution, its upstream MIT link, and the existing dynamic version.
  Add only an `LGPL-3.0` entry immediately after MIT, linking to `https://github.com/Wei-Shaw/sub2api/blob/main/LICENSE`.
  Remove all other assistant-added footer licensing changes. License-file corrections do not authorize other footer changes.
  Preserve the current README as required by R3. Do not add a notices file, license manifest, or licensing guide.
- R7. Send configured notifications for confirmed, successfully saved normal-to-degraded and degraded-to-normal verdict transitions.
  Do not require priority adjustment or model control to be enabled.
  An unchanged or failed priority write does not suppress a saved verdict transition's notification.
  Stable verdicts do not notify, including when their priority needs correction.
  Failed verdict saves, incomplete confirmations, and manual Candy tests do not produce transition notifications.
  Use the same rule for scheduled inspection rounds and the inspection coordinator's immediate-start action.
  Report the verdict transition in notification text. Do not claim a priority change that did not occur.
  Keep notification failures separate from saved verdicts and priority outcomes. Preserve silent page error handling.
- R8. Add one `notify_enabled` setting for both ntfy and Bark.
  Show a `通知` switch beside the notification card title, parallel to priority adjustment and model control.
  Use the existing switch style and automatic settings persistence.
  The switch controls only notifications. Turning it off keeps saved addresses, credentials, and inspection behavior.
  Hide notification fields when the switch is off, as with the other two cards.
  Default to true when no value is saved, preserving existing configured notification delivery.
  Preserve an explicitly saved false value across reads and restarts.
  No configured channel means no outbound notification, even when the switch is on.
  Do not add separate channel switches or another notification option.
- R9. Synchronize new changes from `haowang02/cpa-plugin-codex-candy-eval` into the native evaluation plugin.
  Use baseline `4f8367642cc1e629c4ee15a975e5e0fc53c4ac16` and target `179d6dae48a0f0a735637ea2f373345b91caaca8` (upstream v0.4.4).
  Update the detector binary and model references, including the four new models recorded in `research/upstream-sync.md`.
  Accept model-like sequences when autocorrelation is at most -0.23 or small-step share is at most 0.05.
  Update the existing golden fixture to the target's expected results.
  Match the upstream narrow-screen Pelican toolbar placement through the native CSS.
  Preserve native authentication, account selection, transport, history, inspection, and the task's notification behavior.
  Reconcile upstream changes with R1-R8. Do not overwrite these requirements during synchronization.
  Preserve R3's current README and the automatic multi-plugin build.
  Keep native version ownership and Sub2API v0.2.19. Exclude CPA saved-login decoding and release-only version changes.
  Exclude CPA-specific runtime, installers, release workflows, and unrelated project tooling.
  Record adopted changes and exclusions in Trellis research. Do not add another product document or manifest.
- R10. Create a plugin repository that GitHub marks as a template.
  Repository: public `Nanboom233/sub2api-plugin-template`, default branch `main`.
  Generated repositories must run their own build without repository-name edits.
  Provide tracked `patches/` and `tests/` directories and a working workflow without fake product features or vacuous tests.
  Add it as the submodule `plugins/sub2api-plugin-template`.
  Without `patches/*.patch`, it contributes no patches, plugin tests, or licenses to the combined build.
  Its standalone build still produces unmodified upstream Sub2API and its installer.
  Use `LGPL-3.0-or-later` for the template and include required upstream license texts.
  Keep its root `LICENSE` limited to the unmodified standard LGPLv3 text, without project statements or explanations.
  Add a Chinese README covering template use, patch naming, tests, standalone and combined builds, CI, and outputs.
- R11. Give eval and quota independent GitHub Actions builds that apply only their own patches.
  Add the parent combined build workflow using its existing automatic plugin discovery.
  Each plugin, the template, and the parent carry a complete build kit, installer source, and required test support.
  Standalone builds run common and business tests once. Combined builds run each active plugin's business tests and the parent's common tests once.
  Local builds and CI both run `python3 scripts/build.py` in the current repository.
  Update `build.py` to recognize standalone plugin roots and combined roots automatically.
  Keep equivalent build-kit files aligned across repositories. Standalone builds need no parent checkout or remote build Action.
  Remove eval's retired source/check arguments. Do not add a CI adapter or temporary composition root.
  Keep source download and tests automatic. Do not require a manual source path, separate check argument, or plugin manifest.
- R12. Every successful workflow must provide the approved platform executable and self-contained installer pairs as Actions artifacts.
  Name raw programs `sub2api-plugins-<upstream-tag>-<os>-<arch>` and installers `sub2api-plugins-installer-<upstream-tag>-<os>-<arch>`.
  Use the selected tag including `v`, and add `.exe` for Windows. Upload each executable directly without tar packaging.
  Child `10-31-installation-methods` defines the five targets and platform payloads.
  Do not derive names from repositories or retain old plugin-specific names.
  Replace the retired build implementations. R19 restores optional GitHub Release publication through the unified workflow.
  Do not publish container images.
- R13. Use official GitHub guidance and verified latest stable releases when selecting new CI dependencies.
  Exclude prereleases. Reuse the recorded selections for unchanged dependencies.
  Keep application dependencies locked and preserve their override semantics when adapting the latest pnpm.
  Reference official Actions with exact release tags such as `@v7.0.1`, without commit hashes or major-only tags.
- R14. Report errors through failed steps, workflow status, and native Actions command logs.
  Patch and test failures must fail the build. Missing expected outputs must fail artifact publication.
  Remove custom summary steps, duplicate downloadable logs, and the `tee` pipelines that only create those logs.
  Use native setup, command, and upload errors. Do not create external error reports.
  Do not repeat builder-owned output assembly checks in CI. Use native Action missing-file errors and job status.
  Remove the separate Validate outputs shell loop and custom successful-upload status aggregation.
- R15. Use pull-request and manual workflow triggers for all four repositories. Remove push-triggered builds, including tag pushes.
  Plugin CI must need no personal token or repository secret. Use the workflow job token.
  R23 merges publication into the build job. That job needs `contents: write` because permissions are job-scoped.
- R16. Simplify output consistently in the parent, eval, quota, and template build kits.
  Report each applied patch once and show each Docker failure's captured detail through one error owner.
  Keep useful command context, failure exit status, installation progress, version warnings, backup paths, readiness, and restoration results.
  Expected failure fixtures must not print apparent product failures during successful test runs.
  Preserve diagnostics when a fixture assertion fails. Reuse the existing test capture boundaries.
  Follow the verified output-ownership patterns in `research/output-conventions.md` with current standard-library and GitHub facilities.
  Do not add a logger, CLI framework, output protocol, verbosity option, new entry, or another diagnostic file.
  Keep existing page error contracts, including default quota silence and visible custom-script errors.
- R17. Use one build job with dependency caches and sequential target compilation.
  Apply the same design to the parent, eval, quota, and template workflows and build kits.
  Use native Go package parallelism. Do not add cross-target concurrency or GitHub target matrices.
  Remove separate server, installer, and publish jobs, their internal artifacts, and their stage/matrix plumbing.
  Keep cache restoration after source download so keys use actual dependency files.
  Keep the argument-free local build entry. CI uses the same `scripts/build.py` entry.
  Preserve automatic source selection, patch composition, tests once per workflow, and direct executable pairs for selected platforms.
  Preserve native and matching Linux container payloads in every self-contained installer.
  Upload final files after the complete selected build succeeds. Do not upload intermediate source, server, or installer handoffs.
  Do not add a cleanup workflow, artifact-delete permission, external storage, or cache-based transport.
- R18. Manual CI runs select the upstream tag and support platform multi-selection.
  Retain the editable `upstream_tag` default `v0.2.19`.
  Preserve arbitrary nonempty subsets of the five supported platforms. Do not replace multi-selection with all-or-one selection.
  Keep the existing five boolean platform inputs and their true defaults, as the user selected after research.
  The research is recorded in `research/workflow-platform-selection.md`. No platform input redesign remains in scope.
  Automatic PR builds use all platforms and resolve the latest official upstream release's actual tag.
  Build required Linux container payloads even when those Linux platforms are not selected for final download.
  Publish only the selected platform pairs. Default all-platform builds still publish ten final executables.
- R19. Keep optional manual GitHub Release publication in the same workflow, without a duplicate build entry.
  Retain the disabled-by-default `release` switch. Remove the separate `release_tag` input.
  Use the actual upstream tag selected for this build as the Release tag, without a separate naming rule.
  GitHub's automatic Source code archives must identify the same build commit as the executable assets.
  PR runs do not publish Releases. Tag pushes do not trigger the workflow.
  Publish the exact successful selected-platform outputs as direct Release assets after build and artifact upload succeed.
  Use the exact title `Sub2API-Plugin <hash> (v<upstream-version>)`, with the built repository commit's first seven hexadecimal characters.
  Normalize the upstream version to exactly one leading `v`. Use only GitHub-generated CHANGELOG content as the Release body.
  Do not add installation instructions, platform lists, provenance blocks, or another CHANGELOG file.
  Delete any existing same-tag Release and its tag with `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true`, then create a clean Release with `gh release create`.
  Do not add tag lookup, annotated-tag resolution, `git push` tag helpers, or a tag-to-build-commit equality requirement.
- R20. Name manual workflow runs `Build <upstream-tag> · <ref-name>`, for example `Build v0.2.19 · main`.
  Use existing inputs and GitHub context. Do not add a title input, commit lookup, or run number.
  Keep the existing PR-title display for pull-request runs. R23 controls the workflow and job names.
- R21. Replace the separate final-artifact upload steps with one SDK upload step in all four workflows.
  Preserve one raw Actions artifact per selected executable, with its existing basename and no ZIP or tar packaging.
  Upload the selected server and installer pairs only after the complete build succeeds. All platforms produce ten artifacts.
  Use the official artifact SDK. Dependency setup and all upload calls belong to that same workflow step.
  A missing selected file, dependency failure, or upload failure must fail the step and build.
  Use runner artifact credentials. Do not add a personal token, repository secret, or write permission for uploads.
  Keep native failure logs without custom summaries or diagnostic artifacts.
- R22. Present one cache-load step in all four workflows. Remove the separate cache-path discovery step.
  Keep one multi-path cache for Go modules, Go compilation data, and the pnpm store.
  Restore after source preparation. Include runner, toolchain, dependency files, builder, and source revision in the key.
  Preserve dependency-compatible cache reuse, successful-save behavior, and normal cache-miss builds.
  Keep one explicit cache-save step. The path and workflow research is complete.
  Previous cache-SDK and build.py path-output proposals were rejected. Neither is an approved requirement.
  Do not add workflow arguments, test files, or another product build.
- R23. Merge Release publication into a conditional step in the build job in all four workflows.
  Name the workflow and job `Build and Release`. Use job ID `build-release`.
  Run publication only for successful manual builds with `release` enabled. Other runs skip that step.
  Use the current job's selected final files directly. Remove the separate Release job and artifact download.
  Preserve R19's Release tag, title, and generated CHANGELOG. Remove the added tag ownership precheck.
  Preserve R20's manual run title and PR-title display.

## Acceptance Criteria

- [x] AC1 (R1). Fresh settings include `gpt-6.1-terra`. Saved custom and empty lists retain their values.
- [x] AC2 (R2). A fresh page shows the gray placeholder and an empty input for saved ntfy credentials.
  Entered values stay masked during the current page session, including automatic saves and settings-tab revisits.
  Reloading clears the input. Unconfigured credentials show no configured placeholder.
  Blank updates retain saved credentials. Unrelated saves do not resubmit an unchanged retained secret.
- [x] AC3 (R3). The restored Chinese README retains the user's subsequent edits.
- [x] AC4 (R4, R5). The parent retains MIT text and identifies `2026 Nanboom233`.
  Quota's root `LICENSE` contains only the standard LGPLv3 text. Required license texts and dependency attribution remain intact.
  The parent Chinese root README identifies its own code separately from Sub2API and plugins.
  The root license retains the MIT text and attribution without a scope appendix.
  The Chinese root README explains installation and builds with commands that match the current implementation.
  The parent license collection includes both GPLv3 and LGPLv3 without requiring the eval plugin.
  Original upstream and dependency license attribution stays intact.
- [x] AC5 (R5). Parent plugin references identify the reviewed work commits after commit approval.
- [x] AC6 (R6). The evaluation root `LICENSE` contains only the unmodified standard LGPLv3 text.
  The page footer retains original CPA attribution, the original upstream MIT link, and its dynamic version.
  Only the explicitly requested `LGPL-3.0` link to Sub2API's `LICENSE` follows MIT.
  The original CPA MIT notice remains complete. Existing third-party notices remain intact.
  Eval standalone and combined installers include GPLv3, LGPLv3, and the original CPA MIT notice.
- [x] AC7 (R7). Saved degradation and recovery transitions notify even with both other actions disabled.
  Matching priorities and priority-write failures do not suppress these notifications.
  Stable verdicts and failed verdict saves do not notify. Notification text describes the actual state change.
- [x] AC8 (R8). The notification switch saves and reloads independently of the other two switches.
  A saved false value suppresses both channels without clearing their settings or blocking verdict changes.
  Missing values retain existing delivery behavior. Hidden notification fields retain the saved-secret placeholder behavior in R2 when reopened.
- [x] AC9 (R9). The comparison identifies the baseline, target commit, and disposition of each incoming change.
  Native detection matches the target's six golden cases with the updated reference bank and sequence rule.
  The narrow-screen Pelican button follows normal grid placement while retaining the native group field.
  The final patches preserve R1-R8 and do not restore CPA-only delivery or retired code.
- [x] AC10 (R10). GitHub reports the template repository's template flag as true.
  A generated repository can run its workflow without repository-name edits.
  The template is a submodule under `plugins/`. Its empty patch set is excluded from the combined build.
  Its standalone build produces an upstream executable and installer. Its Chinese README explains actual usage.
- [x] AC11 (R11, R15). The template, eval, quota, and parent each have a working workflow for their intended source composition.
  Each has a complete build kit and one local/CI entry, without a parent checkout or remote build Action.
  Common build/installer cases execute once per build, including when active plugins carry their own copies.
  Existing tests run by default without manual source preparation or a separate check argument.
- [x] AC12 (R12). Every successful workflow provides the selected versioned server/installer pairs in their native executable formats, ten files by default.
  Unix download instructions retain `chmod +x`.
  Do not add a redundant executable-bit check immediately after setting that bit.
  The retired workflows stay replaced. Optional publication uses the unified build workflow and exact built assets.
- [x] AC13 (R13). Research records official sources and verified stable versions. Workflows use exact release tags.
  The latest pnpm can install the target source with a frozen lockfile and the original override semantics.
- [x] AC14 (R14). Build failures stop final product upload and remain visible in native Actions logs and workflow status.
  No custom summary or duplicate log artifact remains.
- [x] AC15 (R16). Each patch has one progress line, and Docker failure detail appears once with its operation context.
  Expected fixture failures stay quiet when their assertions pass and retain diagnostics when assertions fail.
  All four build kits use the same behavior. Required backup, readiness, version-warning, and restoration information remains available.
- [x] AC16 (R17). Four aligned workflows use one build job with dependency caches and sequential target compilation.
  Cache misses run the normal build. Source preparation and tests are not repeated for each platform.
  Only the selected final executable pairs enter Artifacts, ten by default. No intermediate handoff artifact exists at any point.
  Optional Release publication reuses those successful final artifacts.
- [x] AC17 (R15/R18). Manual runs support the approved platform multi-selection interface and upstream tag, without repeating shared tests.
  The five existing checkboxes preserve arbitrary nonempty platform combinations and their current defaults.
  Neither branch nor tag pushes trigger builds. PR builds remain enabled.
  A macOS/Windows-only selection still receives matching embedded Linux payloads without publishing unselected Linux products.
  PR/default runs retain all five platforms.
- [x] AC18 (R19). Manual Release-enabled runs publish selected built assets using the actual upstream tag as the Release tag.
  No `release_tag` input remains. Other runs retain Actions artifacts only.
  The title identifies the built source commit and upstream version with exactly one leading `v`.
  The body contains only the generated CHANGELOG.
  A repeated same-tag publication removes the old Release and tag with `gh release delete --cleanup-tag --yes`, then creates a clean Release at this build's source commit.
  The final assets contain only this build's selected platform files, and Source code archives match this build's source commit.
  No tag-to-build-commit precheck or separate `git push` tag command applies. Publication errors fail the step and retain Actions artifacts.
- [x] AC19 (R20). All four workflows show the selected upstream tag and ref in manual run titles without another input.
  PR runs retain their PR title. Build behavior, Release naming, and artifact names remain unchanged.
- [x] AC20 (R21). All four workflows use one final-artifact upload step.
  Selected executable pairs retain separate raw downloads and existing names. All-platform builds provide ten artifacts.
  SDK setup and upload failures fail that step. No intermediate or duplicate diagnostic artifact is added.
- [x] AC21 (R22). All four workflows provide one cache-load step without a separate locate step.
  The same three caches remain effective for actual build commands. A miss retains normal dependency installation and build behavior.
  One matching save step retains the primary key and skips exact hits.
- [x] AC22 (R23). All four workflows have one `build-release` job named `Build and Release` and the same workflow name.
  Release-disabled and PR runs skip publication. Release-enabled manual runs publish the current job's selected final files.
  No separate Release job or final-artifact download remains. Existing run titles and Release metadata retain their values.

## Current Delivery State

AC1-AC22 have completed local or hosted evidence recorded in `progress.md`.
Published parent work commits on `origin/main` are `66f17f7` and the squashed CI commit `2fc4e90`.
The squashed plugin CI commits on `origin/main` are eval `4e6d167`, quota `a6c145c`, and template `b3c40dd`.
The cache-path probe and designated research synthesis are complete in `research/cache-load-conclusion.md` and `research/release-recreation.md`.

## Scope and Authorization

The user approved the delete-and-recreate Release publication plan, the squashed CI commits, and task archival.
The completed installation-methods child is archived under `archive/2026-11/10-31-installation-methods`.
Use `design.md` and `implement.md` for the remaining technical changes and checks.
Historical research records earlier candidates. Current requirements and design take precedence over those candidates.
The parent, eval, quota, and template keep aligned workflows. No new task or child task is needed.
Preserve completed plugin behavior, installer behavior, licenses, README edits, build outputs, and default test execution.
No builder or product-test change is needed for this revision.
Reuse completed path probes, SDK integration checks, and build evidence.
Check the changed workflow syntax, cache wiring, Release wiring, and four-copy alignment without adding a test suite.
Do not add a full build, cache-hit benchmark, runtime matrix, browser/container rerun, remote failure run, or test Release.
Keep exact approved dependency tags. No dependency change requires another version-selection probe.
Work commits and remote operations retain their separate approval boundaries.
Before personal GitHub credential use, present its source, target account/repositories, operations, and visibility for explicit approval.
Use corresponding source and build material for the exact binaries distributed through CI artifacts.
