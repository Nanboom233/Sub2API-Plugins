# Plugin, inspection, licensing, and artifact CI design

## Current revision

R22/R23 and tag-precheck removal are published. The user approved repeated same-tag Release publication.
The settings, synchronization, licenses, build kits, installer, and SDK uploads below describe completed contracts to preserve.
Use `progress.md` for completed execution and validation evidence. Historical research candidates do not override this design.

## Settings and page ownership

`plugins/codex-candy-eval/patches/0005-inspection.patch` owns the coordinator, settings type, notification sender, and native settings service.
Add `NotifyEnabled bool` with JSON name `notify_enabled` next to `AdjustPriority` and `ControlModels`.
Set its default to true. The existing service reads stored fields into `DefaultInspectionSettings()`.
This preserves missing-field behavior and an explicitly stored false without a migration or a new configuration file.
Use the existing native setting serialization and public settings response.

`patches/0006-evaluation-ui.patch` owns `backend/internal/codexeval/web/inspection.js` and `web/ui.html`.
Add the notification switch to the existing card header. Give its body the ID `inspection-notification-fields`.
Update `updateInspectionVisibility()` to follow `notify_enabled` independently of the other two action switches.
Reuse checkbox serialization, dirty-field preservation, and automatic saves.
Do not clear hidden values or credentials.

Use `ntfy_password_configured` to set the password input placeholder to `已配置，留空保持不变`.
Start with an empty input on a fresh page load, then retain the user's masked value during that page session.
Successful saves and settings-tab rereads must not replace that value with the API's redacted empty string.
Clear the input on page reload. Do not put the secret in browser storage or expose it in API responses.
Use the existing dirty-field state so unrelated saves do not resubmit an unchanged retained secret.
Keep newer edits intact while earlier saves complete.
Use `frontend/src/components/account/EditAccountModal.vue` and `frontend/src/i18n/locales/zh/admin/overview.ts` as native references.
Do not add a separate configured-status label or extend this placeholder to Bark.

Append `gpt-6.1-terra` to `DefaultInspectionSettings().DegradedRemoveModels`.
Keep existing entries and saved-list behavior.

## Notify from verdict transitions

Record confirmed verdict transitions separately from priority-update results.
Use the fresh account verdict from the apply path and the successfully persisted target verdict.
Treat an absent verdict as normal, as the current coordinator does.
Do not record a transition if verdict persistence fails or the verdict remains unchanged.
Keep existing confirmation, cancellation, participation, and persistence rules.
Do not add priority availability or busy checks to verdict persistence.

Collect saved transitions before the optional priority-update path.
Later priority failures retain their existing backend errors but do not remove a saved transition from notification collection.
Use the existing per-direction batch delivery. Gate delivery on `notify_enabled` and configured channels.
Stable-state priority repairs do not enter these batches.
Notification failures retain `notification_error` without reversing saved state or successful priority changes.
Use state-change wording in messages instead of unconditional `priority X -> Y` wording.

Scheduled rounds and the immediate-start inspection action share this coordinator.
Ordinary fixed-count Candy tests remain outside transition notifications.
Do not introduce a notification queue, retry mechanism, event store, or new result schema.

## Repository and license corrections

Use `research/eval-license.md` for the verified license scope, original MIT provenance, and planned license files.
Preserve eval's restored Chinese README and the user's subsequent edits. Do not restore an earlier file over those edits.
Preserve the completed quota LGPL licensing and parent attribution/spec correction.
Use only the unmodified standard LGPLv3 text in the eval, quota, and template root `LICENSE` files.
Remove project statements and explanations. Preserve the standard FSF copyright and inherited files under `licenses/`.
Keep the parent root `LICENSE` limited to MIT text and its copyright attribution.
Place its license scope in the Chinese root `README.md`, with links to `LICENSE` and `licenses/`.
Use that README for artifact extraction, container installation, local prerequisites, and the argument-free build entry.
Describe the fixed output pair and reinstallation after container recreation or migration. Verify commands against the current build and installer owners.
Restore the original footer within `0006-evaluation-ui.patch`: CPA author credit, the original upstream MIT link, and the existing dynamic version.
Immediately after MIT, add only `LGPL-3.0` linked to `https://github.com/Wei-Shaw/sub2api/blob/main/LICENSE`.
Use the existing separator and external-link attributes. Do not add other footer entries as part of license-file changes.
Reuse recursive root `LICENSE` and `licenses/` collection in each complete build kit.
Update parent gitlinks after separately approved plugin commits.

## Upstream evaluation synchronization

Use `research/upstream-sync.md` for the source repository and historical synchronization baseline.
The completed comparison targets `179d6dae48a0f0a735637ea2f373345b91caaca8` (upstream v0.4.4).
Use anonymous public reads. Do not use GitHub credentials without the separate approval required by the project spec.
Port changes into the current native patch owners instead of replacing the repository with the CPA source tree.
Keep the root's automatic build, flat tests, native account APIs, and native installer ownership.
Preserve the current README, license scope, notification switch, and transition rules when resolving overlapping changes.
Update `sequenceShape` in patch `0001` from conjunction to disjunction without changing either threshold.
Update the existing reference source note, model JSON, and binary asset in patch `0002` together.
Replace `assets/lm-detector-golden.json` with the target fixture. Keep its existing flat Go test consumer.
The enrollment suite and original LM-detector MIT license remain unchanged.
In patch `0006`, remove the forced Pelican button spanning at both 900px and 768px breakpoints.
Retain the native group field, two-column grid, and existing control widths.
The completed Playwright session covers narrow-screen placement. Reuse that result while the UI remains unchanged.
Do not port CPA saved-login decoding, its test cases, or CPA release-only version changes.
The upstream page's release number alone does not establish that native patches contain its changes.

## Complete build kits and workflows

Each repository owns a complete, runnable build kit:

```text
.github/workflows/build.yml
scripts/build.py
scripts/installer/main.go
tests/support.py
tests/test_build.py
tests/test_installer_test.go
LICENSE
licenses/
```

Plugin business tests remain in the same flat `tests/` directory.
Use aligned copies of the build kit in the parent, eval, quota, and template.
Update these copies together for this task. Do not create a synchronization service or another build entry.
Each checkout must build without the parent checkout, an external build Action, or downloaded build scripts.
Local builds and CI run the same command: `python3 scripts/build.py`.
Replace eval's historical `--source` and `--check` builder with this complete automatic implementation.
Do not create `.github/actions/build/action.yml` or `scripts/ci_build.py`.

Every repository has its own complete `.github/workflows/build.yml` for setup, build, and final artifact upload.
Generated repositories use their own checkout and repository context without template-name edits.
Use `pull_request` and `workflow_dispatch` on GitHub-hosted `ubuntu-latest`. Remove the `push` trigger, including tag pushes.
Use workflow-level `contents: read`, `persist-credentials: false`, and no inherited personal secrets.
Reference current official Actions by exact release tags such as `@v7.0.1`. Do not use commit hashes or major-only tags.
Do not run plugin source under `pull_request_target`.
Keep the retired parent and eval `release.yml` implementations replaced by the unified `build.yml`.
R23 moves optional manual publication into a conditional step in the same build job.
All four repositories already have working workflows. The current revision simplifies those workflows.

## Automatic source composition in build.py

Recognize a standalone plugin root by its tracked `patches/` directory, including an empty template directory.
Apply only that root's `patches/*.patch` files to automatically downloaded source.
Run its flat common and business tests once, then build both outputs using its local installer source and licenses.
An empty standalone template builds unmodified upstream source and still runs its common build/installer tests.

The parent uses initialized submodule paths under `plugins/` from its existing `.gitmodules`.
Retain the explicit error for uninitialized submodules before checking patch contents.
Select initialized plugin directories with at least one top-level `patches/*.patch` file.
An empty template is skipped entirely as a combined-build participant, including its common tests and licenses.
Sort active plugin paths and patch filenames as before. Apply patches against the evolving combined source.
Run each active plugin's business tests against that source and run the parent's common build/installer tests once.
Do not execute duplicate common build/installer suites from every plugin during a combined build.
Use one explicit common-test file set in the build runner to separate those suites from plugin business tests.
Do not add a plugin manifest, mode flag, temporary composition root, symlink checkout, or generated `.gitmodules`.
Generalize license namespaces for the standalone root and combined child plugins.
Publish platform output pairs under the current repository's `dist/build/<os>-<arch>/` only after success.
Preserve source download, patch order, and failure propagation. Manual runs select an upstream tag through `upstream_tag`.
Pull-request runs use the latest official release's actual tag. Sub2API v0.2.19 remains the verified integration baseline.

## Template and CI artifacts

The public `Nanboom233/sub2api-plugin-template` repository is a submodule under `plugins/sub2api-plugin-template`.
Its GitHub `is_template` flag is already enabled.
Include the complete build kit, root `LGPL-3.0-or-later` license, upstream license texts, and tracked `patches/` and `tests/` directories.
Keep an empty `patches/` directory through a marker. Do not add fake production changes or vacuous tests.
The template's real common tests live in flat `tests/` and do not make it an active combined plugin.
Add a Chinese README with prerequisites, template creation, standard patches, flat tests, local build, parent submodule use, CI, and outputs.
Explain that empty patch directories are skipped by the parent and that patch/test failures fail the build.

Use these fixed outputs in every repository:

```text
dist/build/<os>-<arch>/sub2api-plugins-<upstream-tag>-<os>-<arch>
dist/build/<os>-<arch>/sub2api-plugins-installer-<upstream-tag>-<os>-<arch>
```

Remove repository-name inference and old-name compatibility from the design.
No output-name input, argument, alias, or generated-repository naming test is needed.

Child `10-31-installation-methods` defines the approved five platforms and separate installer-host/runtime payload selection.
Windows programs add `.exe`. Do not retain duplicate outputs at the former paths.
Use the selected upstream tag, including `v`. Keep expected-file assembly in the builder.
Use the published single SDK upload step with `skipArchive: true`.
Upload each selected platform's two executables individually within that step. Default all-platform runs upload ten files.
Each Actions product artifact uses the executable's basename.
Pass that basename to each SDK upload. Do not create tar files or another product archive.
Executable pairs stay under `dist/build/<os>-<arch>/`. Unix downloads need `chmod +x` before execution.
Use repository defaults for retention.
Optional GitHub Release publication follows R19 below. Do not add container images, checksum manifests, or build-info manifests.

## Latest CI tools and frozen dependencies

Retain the approved stable tool and Action versions recorded in `research/github-actions.md`.
This revision adds no dependency upgrade or repeated version-selection probe.
Install Corepack separately for current Node.
Use the same selected pnpm for frontend installation, frontend build, and native Vue tests.
Remove stale pnpm 9.15.9 references from all build-kit and test-runner copies together.

The pnpm 12 probe found that upstream v0.2.19's `package.json` overrides are no longer read.
Preserve those overrides in a generated `pnpm-workspace.yaml` in the temporary downloaded frontend tree.
Preserve effective dependency build settings when applying the new configuration format.
Do not modify the upstream lockfile or fall back to a non-frozen install.
Do not commit a frontend workspace manifest to the parent or plugin repositories.
The translation passed frozen-lock validation and the completed hosted Linux builds.
Restore dependency caches only after the builder has downloaded and patched source, so the actual dependency files exist.
The following single-job design supersedes the published matrix implementation.

## Single build job

The user selected this design after reviewing Go target behavior and measured hosted overhead.
Use `research/go-build-parallelism.md` and `research/upstream-build-ci.md` for the evidence.
The earlier sequential compilation implementation is published. Reuse its valid results for the approved R22/R23 correction.

Keep `scripts/build.py` as the only build entry. Its default argument-free invocation performs the complete local build.
Use one CI `build-release` job and one local workspace for source, tests, compilation, output assembly, and optional Release publication.
Compile targets sequentially. Let each `go build` use its native package parallelism.
Do not add a target matrix, architecture scheduler, process pool, or custom concurrency option.

```text
build-release job: Build and Release
  download source and apply patches
  restore dependency caches
  build frontend, run plugin tests and vet
  build common-test payload and run common tests
  compile remaining required servers in sequence
  compile selected installers in sequence
  assemble and upload selected final executable pairs
  save successful dependency caches
  publish Release when enabled for this manual run
```

Source and dependency use remain separate steps in this same job so cache keys can read actual downloaded lockfiles.
Keep only the internal source/resume boundary needed by that cache timing. Remove per-target and publication-only stage dispatch.
The resume path performs remaining preparation, tests, compilation, and atomic output assembly through the existing functions.
It uses the same tag and workspace without another source download or release lookup.
Local invocation continues to call those same functions without CI environment fields.

Common installer tests extract a real Linux payload. Reuse servers already compiled for common tests during later target compilation.
Preserve the host-architecture Linux payload required by the current Darwin/arm64 local entry.
Each installer embeds its native program and matching Linux program. Linux hosts reuse their native program as that payload.
Keep tests and vet once per build. The installer transaction and fixture logic are outside this revision.

## Platform selection and Release publication

Use these manual workflow inputs in every repository:

| Input | Type | Default and purpose |
| --- | --- | --- |
| `upstream_tag` | String | Editable `v0.2.19`, selecting source and program metadata |
| `linux_amd64` | Boolean | true, Linux x86_64 final pair |
| `linux_arm64` | Boolean | true, Linux ARM64 final pair |
| `darwin_amd64` | Boolean | true, macOS Intel final pair |
| `darwin_arm64` | Boolean | true, macOS Apple Silicon final pair |
| `windows_amd64` | Boolean | true, Windows x86_64 final pair |
| `release` | Boolean | false, publish the successful outputs to GitHub Releases |

The user chose to keep the existing five platform checkboxes after the requested research.
Keep their defaults, existing mapping, and builder validation. No dropdown, string input, or external interface is added.
PR builds select all platforms and resolve the latest official upstream source tag. Pushes do not run this workflow.
The published workflows have no `release_tag` input, tag-push publication, or required-field preflight for a separate tag.
Manual Release-enabled runs use the source stage's actual `tag` output through the existing `UPSTREAM_TAG` variable.
No separate plugin release identity or tag suffix is required.

Set the workflow run title with top-level `run-name` using existing expression contexts.
Manual runs use `Build <inputs.upstream_tag> · <github.ref_name>`, including manual Release-enabled runs.
PR runs use `github.event.pull_request.title`, preserving their existing native display without an unavailable manual version input.
Set workflow and job names to `Build and Release`, with job ID `build-release`.
Keep the existing `run-name` expression. Add no title input, run number, commit-title lookup, or dispatch wrapper.

The build entry receives the selected platform list through `SUB2API_BUILD_PLATFORMS`; absence preserves the complete local build.
Keep source-step outputs needed for selected uploads, tool identity, and Release. Remove obsolete build-to-release job outputs.
Required servers are the selected native targets plus each selected installer's matching Linux target.
Compile each required server once, including any program already produced for shared tests.
Reuse existing builder platform validation for the final selected list.
A failed build prevents later product upload steps through normal job success handling.

Only selected platforms enter final Actions artifacts and Release assets.
For example, Darwin/arm64 selection requires a Linux/arm64 intermediate payload, but does not publish a Linux product unless selected.
Always run shared checks once, including single-platform builds. Do not introduce a user test-skipping option.

Place `Save caches` after SDK artifact upload and before `Publish Release` in the same job.
Release failure must not suppress saving successful build caches.
Use `if: github.event_name == 'workflow_dispatch' && inputs.release` with normal success handling.
Use the selected files under `dist/build/<os>-<arch>/` directly. Do not download the uploaded artifacts.
Pass `steps.source.outputs.tag`, `steps.source.outputs.source_sha`, and selected platforms through the step environment.
Construct the same two final file paths per selected platform as the existing upload step.
Remove the separate Release job, its download action, and `needs.build` references.
Set workflow permissions to `contents: read` and combined-job permissions to `contents: write`.
GitHub permissions are job-scoped. All steps in the combined job receive that permission, subject to event restrictions.
Do not claim that the publication condition restricts the job token's permissions to that step.
Use `GH_TOKEN: ${{ github.token }}` and the installed GitHub CLI. Do not add a personal access token or repository secret.
Before `gh release create`, remove any existing same-tag Release and its tag:

```sh
gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true
```

This single CLI command deletes both the existing Release (with all old assets) and `refs/tags/$UPSTREAM_TAG` when present, and is a no-op when absent.
Then create the Release with `gh release create`, selected assets, `--target "$SOURCE_SHA"`, the title, and `--generate-notes`.
`gh release create` stages assets in a draft Release, generates notes for `$SOURCE_SHA`, publishes the Release, and creates `refs/tags/$UPSTREAM_TAG` at `$SOURCE_SHA`.
GitHub's automatic source archives follow the exact repository commit and its recorded plugin references.
Keep the deleted tag-equality gate removed. Do not add a `git push` tag step, tag lookup, or separate source archive upload.
Publication errors fail the step and job while retaining the uploaded Actions artifacts.

All four repositories use the literal title prefix `Sub2API-Plugin`.
Titles follow `Sub2API-Plugin <hash> (v<upstream-version>)`.
The hash is the first seven hexadecimal characters of the exact repository commit that produced the programs.
Remove an existing leading `v` from the upstream tag before adding the title's single `v` prefix.
For example, parent commit `66f17f7` and upstream tag `v0.2.19` produce:

```text
Sub2API-Plugin 66f17f7 (v0.2.19)
```

The body is only the actual GitHub-generated CHANGELOG, including its normal change list and comparison link when available.
Use `--generate-notes` in `gh release create`.
Do not add installation text, platform lists, source/build link blocks, custom notes templates, or a committed CHANGELOG document.

## Final artifacts and dependency caches

Keep all current-run source, programs, installer resources, and payloads in the build runner's workspace.
Upload only the selected final program and installer files. No intermediate artifact exists, even during the run.
Remove `internal-prepared`, `internal-server-*`, `internal-installer-*`, and all matching downloads.
Keep source, compilation, artifact upload, and optional Release publication in the same job.
No cleanup workflow, artifact-delete permission, external storage, or cache-based handoff is needed.

The builder assembles selected outputs once after every required compilation succeeds.
Propagate SDK missing-file and upload exceptions without a separate output-validation loop or upload-status aggregation.

Restore Go module downloads, Go compilation data, and pnpm store once at their use boundary in the build job.
The user approved this R22 design after the task cleanup.
Use the evidence in `research/cache-load-conclusion.md`, `research/cache-path-configuration.md`, and `research/mature-cache-workflows.md`.
Keep cache configuration in each workflow. Do not add cache SDK loading or cache-path outputs to `build.py`.
Declare these absolute paths in the build job environment:

```yaml
GOMODCACHE: ${{ github.workspace }}/dist/cache/go-mod
GOCACHE: ${{ github.workspace }}/dist/cache/go-build
pnpm_config_store_dir: ${{ github.workspace }}/dist/cache/pnpm
```

The current builder inherits these settings. pnpm appends its versioned store directory under the configured parent.
Cache that parent directory. Do not hardcode `v11` or use the ignored `npm_config_store_dir` variable.
Add `id: go` and `id: node` to existing setup Actions. Read `go-version` and `node-version` from their declared outputs.
Keep the source stage's existing `pnpm` output for the package-manager identity.
Delete `Locate dependency caches` and all `steps.paths` references.
Name the existing single official restore Action `Load caches`. Its path list uses the three environment settings directly.
Keep one official save Action named `Save caches`, with the same paths, primary key, and exact-hit condition.
The key identifies runner OS/architecture, Go and Node versions, selected pnpm version, actual dependency files, builder, and source revision.
Use a restore prefix without the source revision to reuse the latest dependency-compatible compilation cache.
This preserves the original explicit load/save arrangement. Automatic post-save is not part of this plan.
The combined cache shares hit and invalidation behavior across all three paths.
Use the configured effective paths, dependency lockfiles, builder dependency pins, and installed tool versions.
One Go compilation cache may contain multiple targets. Go distinguishes OS/architecture internally.
Remove matrix-specific target/role cache copies. Retain normal restore prefixes and primary-key save behavior.
Do not cache patched source, node_modules, final programs, or installer payloads.
Cache misses retain normal dependency installation, frozen-lockfile behavior, tests, and compilation.
Retain exact approved Action tags. This revision does not require unrelated dependency upgrades.

Keep the internal workspace and source/resume controls only where cache timing requires them.
Remove `SUB2API_BUILD_TARGET`, server/installer matrix outputs, matrix counts, and per-target stage dispatch.
Do not introduce a skip-test switch, user plugin configuration, separate check command, or another build entry.

## CI failures and logs

### Published SDK upload contract

Preserve the published single `actions/github-script@v9.0.0` upload step in every workflow.
Keep the wrapper inline in `.github/workflows/build.yml`. Do not add a local Action, package manifest, or separate build entry.
Keep the verified SDK version `@actions/artifact@6.3.1`. This correction introduces no dependency change.

Within that one JavaScript action, install the exact SDK version into a unique directory under `RUNNER_TEMP`.
Resolve its package entry from that directory and dynamically import the ESM module by file URL.
This keeps temporary npm files outside the checkout. SDK installation and import errors fail this step.
The runtime install resolves transitive dependencies through npm. No repository lockfile or bundled local Action is introduced.

Pass the actual source tag and selected platforms through environment variables.
Use them to form the existing two output paths per platform, including `.exe` for Windows.
Do not glob the workspace or include unselected Linux installer payloads.
Await one `DefaultArtifactClient.uploadArtifact` call per file, with `skipArchive: true`.
Use the file basename as its artifact name. Each selected file remains a separate raw download.
Let filesystem and SDK exceptions fail the step. Do not add a separate validation loop or catch-and-continue behavior.

The JavaScript action receives runner artifact credentials. Do not export those credentials to later steps or log them.
Artifact upload needs no repository write permission. R23 adds job-wide write permission for Release publication.
Reuse the completed SDK installation, ESM import, selected-path, and error-propagation checks.
Hosted uploads remain unverified until the user requests a CI run.

Run build commands directly and keep their exit status.
Do not use `continue-on-error` for source preparation, patches, tests, compilation, or product upload.
Use native Actions logs, failed-step annotations, and workflow status for errors.
Remove custom `Report result` steps, `GITHUB_STEP_SUMMARY` writes, `build-log-*` uploads, and their file-capture pipelines.
Keep setup, build, and upload failures with their native step owner. Do not replay log bodies or add a summary replacement.
Upload direct products only after the complete selected build succeeds.
Do not open issues, send external notifications, or add another diagnostic file.

## Unified output ownership

Use `research/output-conventions.md` for verified GitHub CLI, pip, Docker CLI, and GitHub Actions patterns.
Keep child output and contextual errors with their existing owners. Use native Actions logs for CI.
Keep current Python and Go standard-library implementations.

The command runner remains the builder's single command-progress owner.
Remove the separate `Apply ...` print before `git apply`, retaining the actual command and plugin/patch path.
Keep child stdout/stderr inheritance and the concise final `Build failed` context. Do not replay child output in the final message.
Keep final output paths and existing installation prompts in their current streams.

The installer's `docker()` helper already buffers stdout and stderr until `cmd.Run()` finishes.
Forward those buffers only after a successful non-quiet command.
On failure, return the captured detail with command context, and let the existing error caller print it once.
Quiet commands retain their captured failure detail. Preserve cancellation causes and the separate rollback outcome.
Do not change the Docker transaction, readiness retry policy, version confirmation, or exit status.
No custom silent-error type, shared formatter, or logging framework is required.

In `tests/test_build.py`, capture only expected failure scenarios in the existing failure-propagation case.
Use existing standard-library redirection and capture the child descriptors at the existing test runner boundary.
Keep that output silent when assertions pass. Include it when an assertion unexpectedly fails.
Preserve assertions that later work stops and previous outputs remain intact.
Do not add a global suppression mode or hide real build failures.

Apply these changes to all four aligned kits through the same owner.
The native quota console catch is outside this consolidation. Preserve default silent page errors and custom-script diagnostics.

## Build-kit ownership and publication

One implementation owner keeps the builder, installer, common tests, and workflow behavior aligned across all four repositories.
Each repository retains its own complete implementation. There is no shared remote provider to publish first.
All README and license corrections remain part of this unified task.
Publish reviewed plugin/template commits before updating the parent's submodule references.

## Spec updates

The earlier inspection, licensing, build-kit, directory, and output spec updates are complete.
Main updates parent and eval `.trellis/spec/backend/minimal-linux-delivery.md` after the R22/R23 implementation review.
Record declared cache paths, setup Action outputs, one load/save pair, combined-job naming, direct Release files, and job-wide write permission.
Preserve the existing product contracts and test-state atomic-write rule.
