# Remaining implementation and validation

## Existing completed work

Keep the implementation and valid evidence already recorded in `progress.md`:

- Native eval synchronization to `179d6da`, detector assets/golden cases, and narrow-screen Pelican layout.
- Terra defaults, independent notifications, saved-verdict triggers, and same-page ntfy input retention.
- Restored Chinese README with subsequent user edits, standard license texts, preserved original notices, and embedded Lucide license.
- Complete aligned build kits and artifact-only workflows in the parent, eval, quota, and template.
- Updated parent/eval specs, passing combined build on 2026-10-31, and completed browser checks.

The four signed work commits and reviewed gitlinks are published on main. The public GitHub template flag is enabled.
The four prior matching automatic CI runs and their forty direct executable artifacts passed acceptance.
Do not repeat completed implementation, browser work, or current CI runs for reassurance.

## Remaining work order

### Current stage: approved repeated Release correction

The user rejected the guessed cache designs, requested a workflow reread, then authorized continued investigation.
The designated `trellis-research` agent has consolidated the source evidence in `research/cache-load-conclusion.md`.
R22/R23 and tag-precheck removal are published. The user approved repeated same-tag Release publication.
The designated implementation owner is updating the four publication steps using the current work section below.

Completed R22/R23 execution order:

1. Dispatch one `trellis-implement` owner for all four `.github/workflows/build.yml` files.
2. Declare supported absolute Go and pnpm cache paths in build-job environment settings.
3. Add IDs to existing Go/Node setup steps and use their version outputs in cache keys.
4. Remove `Locate dependency caches` and `steps.paths` references. Keep one `Load caches` restore step and one `Save caches` step.
5. Preserve the combined key/prefix, source-before-load timing, exact-hit skip, native success conditions, and SDK artifact uploads.
6. Rename the workflow and job to `Build and Release`. Use job ID `build-release`.
7. Save successful build caches after SDK upload, then conditionally publish Release using the current job's selected final files.
8. Remove the separate Release job, artifact download, and job outputs used only for that handoff.
9. Read Release metadata from `steps.source.outputs`. Preserve the title and generated CHANGELOG without a custom tag ownership precheck.
10. Give the combined job `contents: write`. Publish only after a successful manual build with `release` enabled.
11. Run the focused checks below. Dispatch `trellis-check` with those results for independent review.
12. Main synchronizes parent/eval delivery specs to the reviewed change and presents the commit plan.

No builder, installer, product-test, or license edits are needed. Add no test file, SDK dependency, full build, or hosted-run gate.
GitHub permissions are job-scoped. The combined job receives publication permission even when the Release step is skipped.
Keep the manual run title, PR-title display, existing inputs, approved dependency tags, and published SDK upload behavior.

Published SDK uploads, run titles, trigger changes, platform selection, and first cache consolidation are completed work.
Their commits, checks, hosted-run limits, and prior candidates remain in `progress.md` and `research/`.
Do not repeat their implementation or verification for unchanged behavior.

## Affected files after approval

Apply equivalent changes to the parent, eval, quota, and template:

- `.github/workflows/build.yml`: explicit cache paths, one load/save pair, and one combined Build and Release job.

Main updates parent/eval `.trellis/spec/backend/minimal-linux-delivery.md` for the resulting contract.
No README, builder, installer, test, license, or plugin-patch change is needed.

## Validation scope

Check changed YAML and inline shell syntax with existing local tools.
Review effective paths, setup outputs, key/prefix matching, save conditions, and source-before-load order.
Review Release conditions, metadata, selected-file paths, and removal of obsolete `needs.build` references.
Check four-copy alignment and run `git diff --check` in each affected repository.
These are focused change checks, not new test entries or a new CI lint job.

Reuse the completed Go/pnpm path probe, SDK integration checks, builder suites, and prior hosted evidence for unchanged behavior.
Keep tests enabled in the existing build entry. Add no tests, full build, cache benchmark, runtime matrix, or test Release.
Keep exact approved dependencies. Do not repeat version selection for unchanged dependencies.
Hosted SDK uploads and actual Release creation remain untested. A later user-requested run can exercise those operations.

## Commits and GitHub authorization

Complete local review and commit approval before work commits. Keep Git signing enabled.
Commit plugins/template before recording their new gitlinks in the parent.
Push and hosted execution retain their separate authorization boundaries.
Before personal credential use, present its source, account/repositories, operations, and visibility for explicit approval.
The template already exists. Do not recreate it or repeat its settings check.
The combined workflow uses its job token, with no personal token or repository secret.

## Change boundaries

Preserve unrelated dirty files, the user's current eval README, and parent attribution corrections.
Keep existing scheduling, confirmation counts, priority-update checks, account participation, secret handling, and silent runtime errors.
Use existing standard-library and GitHub facilities for output. Add no logger, CLI framework, output protocol, options, or build entry.
Do not change account data or stored settings during implementation verification outside synthetic fixtures.
Keep generated build output outside work commits.
The template Chinese README and parent Chinese usage, build, and license README are explicitly requested. Preserve eval's subsequent user edits.
The standard LGPL plugin licenses and parent MIT attribution are completed work.

## Execution result

R22/R23 are implemented in all four workflows. Independent `trellis-check` passed.
The reviewer moved cache save before optional Release to preserve successful-build caching when publication fails.
The reviewer checked final YAML, inline Bash, cache/Release wiring, copy alignment, and whitespace.
Main synchronized the parent/eval delivery specs and backend indexes.
No new tests, builds, or dependency changes occurred. The four approved work commits were subsequently pushed, as recorded in `progress.md`.

## Completed correction: remove added Release restrictions

The user rejected added restrictions after publication of the four work commits.
One implementation owner removes the Git reference lookup, annotated-tag traversal, and tag-to-build-commit equality check from all four workflows.
Call `gh release create` with the existing `UPSTREAM_TAG`. Remove the duplicate `RELEASE_TAG` environment entry.
Preserve cache behavior, selected files, title, generated notes, and native CLI failures.
Main removes corresponding task/spec requirements. The checker reviews the focused deletion and syntax without new tests or builds.
This correction is published in four signed commits recorded in `progress.md`.

## Current work: repeated Release publication

The tag-precheck correction is published. The user approved fixing repeated same-tag Release publication.
One implementation owner updates the existing publication step in all four workflows and names it `Publish Release`.
Check Release existence with `gh release view`. Keep native create-with-assets and `--generate-notes` when absent.
When present, generate notes through GitHub's API and edit title/body.
Use the existence query to list all old assets. Delete them all before uploading this build's selected files without `--clobber`.
Keep the existing asset paths, tag, title format, cache order, permissions, SDK artifacts, and inputs.
Main synchronizes the parent/eval delivery specs. Independent `trellis-check` reviews the focused change.
Use existing CLI help and focused syntax/wiring review. Add no tests, product build, hosted run, or test Release.
Work commits and push retain the ordinary approval boundary.

The first create/update candidate passed review. The user then corrected its old-asset retention behavior.
The existing implementation owner must now clear every old Release asset before uploading any new asset.
Synchronize specs, review the deletion/upload order and empty-list behavior, and check changed syntax/copy alignment.
No new tests or remote Release deletion is needed to prepare this correction.
The deletion/upload correction passed independent review, YAML/Bash syntax, four-copy alignment, and whitespace checks.
The candidate remains local and uncommitted. The revised commit plan must describe clearing all old assets before upload.

## Current work: simplify repeated Release publication and update source archive tag

The user selected the simplified delete-and-recreate Release publication design, awaiting final plan approval before implementation.
After user approval:
1. Dispatch `trellis-implement` to update `.github/workflows/build.yml` in all four repositories: replace the `gh release view` / `gh release edit` / `gh release delete-asset` / `gh release upload` branching block with `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true` followed by a single `gh release create` command.
2. Dispatch `trellis-check` to independently verify YAML syntax, Bash syntax, four-copy alignment, `git diff --check`, and full-scope task compliance.
3. Main synchronizes parent and eval `.trellis/spec/backend/minimal-linux-delivery.md` using `trellis-update-spec` and presents the commit plan for approval.
