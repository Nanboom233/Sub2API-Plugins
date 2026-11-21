# Journal - sub2api-plugins (Part 1)

> AI development session journal
> Started: 2026-10-23

---



## Session 1: Automatic plugin build and installer
<!-- trellis-session: v=2 fp=f4afd942bc4c4a6b -->

**Date**: 2026-10-25
**Task**: Automatic plugin build and installer
**Branch**: `main`

### Summary

Complete the automatic Sub2API v0.2.18 plugin build and installer. Record the approved signed work commits.

### Main Changes

- Discover all plugin submodules, apply contextual patches, and build one combined server and installer.
- Keep actual test cases and support code under flat tests/. Retain original license files and remove THIRD_PARTY_NOTICES.txt.
- Record the user rule against unsolicited documents and manifests. Exclude the user-deleted root README.
- The archive command moved the task but failed on an untracked source path. Complete its scoped archive commit as f78f09b.

### Git Commits

| Hash | Message |
|------|---------|
| `6b3d8b6da6692cd7f20e1da0f8238eeb902745c2` | chore(trellis): add portable workflow and agent integrations |
| `9a56c084e274bfa60b07bb46f5c3023ccf746b8d` | feat(build): support automatic Sub2API v0.2.18 composition |
| `1afe6767aab95c13e1296acad0209de76c414303` | feat(build): build all plugin submodules and package installer |

### Testing

- [OK] The default build, focused composition tests, native Go and UI suites, installer tests, and integration vet passed.
- [OK] The refreshed installer passed TestEntryAndEmbeddedPayload. All work and archive commit signatures passed verification.

### Status

[OK] **Completed**

### Next Steps

- Publish plugin revision 9a56c08 before sharing a reproducible remote parent checkout.


## Session 2: API-key quota usage extension
<!-- trellis-session: v=2 fp=14af7892dcb9cfd3 -->

**Date**: 2026-10-26
**Task**: API-key quota usage extension
**Branch**: `feat/apikey-quota-extension`

### Summary

Extend native account usage with upstream quota through a submodule plugin. Failed quota queries remain silent.

### Main Changes

- Add independent upstream usage reads, native field mapping, and existing account-cell rendering.
- Add flat native Go and Vue tests and native Vue discovery in the common build.
- Preserve native provider errors, local usage, refresh behavior, and account scheduling.
- Record the GitHub credential approval rule. Perform only local signed commits during finish work.
- Archive the task. Recover its scoped commit after the native archive command included an untracked old source path.

### Git Commits

| Hash | Message |
|------|---------|
| `c15a45417e93b35372fcbcfdcfe8f1023c4be8cb` | feat(quota): extend native API-key usage reporting |
| `a5f792d90c07511c7abb19a4f8b9ae67faa63f03` | feat(quota): compose API-key quota extension builds |

### Testing

- [OK] Default combined build passed with exit 0: /tmp/sub2api-quota-silent-build.HOVWHm.
- [OK] Both plugin suites, Vue render and refresh cases, frontend type and i18n checks, Go vet, runner tests, and installer tests passed.
- [OK] Independent full-scope review and silent-failure review found no remaining defects.

### Status

[OK] **Completed**

### Next Steps

- Remote publication requires explicit approval for GitHub credential use and pushes.


## Session 3: Complete custom API-key quota scripts on Sub2API v0.2.19
<!-- trellis-session: v=2 fp=8e7962fca85d56c5 -->

**Date**: 2026-10-29
**Task**: Complete custom API-key quota scripts on Sub2API v0.2.19
**Branch**: `feat/apikey-quota-scripts`

### Summary

Add custom quota scripts, inline draft tests, native reset tooltips, and account expiry synchronization. Fix cache invalidation after API-key changes. Update both plugins and delivery to v0.2.19. The default combined build and complete review passed. Recover the archive commit after Trellis referenced an untracked source path.

### Git Commits

| Hash | Message |
|------|---------|
| `2212b3b` | feat(quota): integrate custom scripts on Sub2API v0.2.19 |

### Status

[OK] **Completed**


## Session 4: Synchronize plugins, inspection, licensing, and artifact CI
<!-- trellis-session: v=2 fp=ea7b45266acf35d9 -->

**Date**: 2026-11-06
**Task**: Synchronize plugins, inspection, licensing, and artifact CI
**Branch**: `feat/plugin-build-inspection`

### Summary

Synchronize eval and inspection, correct licensing, deliver five-platform standalone and combined installers, and unify cached single-job CI with SDK uploads and delete-and-recreate Release publication.

### Main Changes

- Synchronize eval with upstream v0.4.4, update inspection defaults, secret placeholders, and verdict notifications, and correct LGPLv3/MIT license scopes.
- Deliver five-platform standalone and combined installers and add the public sub2api-plugin-template repository and submodule.
- Unify all four build.yml workflows into one cached build-release job with SDK raw artifact uploads and gh release delete --cleanup-tag --yes before gh release create.
- Squash all 11 CI commits across all four repositories into one signed commit per repository (eval 4e6d167, quota a6c145c, template b3c40dd, parent 2fc4e90).

### Git Commits

| Hash | Message |
|------|---------|
| `66f17f75726c3fadd9a5bf8d0bc2924378d755e4` | feat(build): deliver portable combined plugin installers |
| `2fc4e904eb83f13e63a833d4a9be34e7f77f3a46` | feat(ci): add cached single-job platform builds and release publication |

### Testing

- [OK] Default combined five-platform build, plugin Go/Vue suites, common builder/installer suites, YAML/Bash checks, and four-repository hosted CI runs passed.

### Status

[OK] **Completed**


## Session 5: Bootstrap frontend guidelines and migrate eval Trellis artifacts
<!-- trellis-session: v=2 fp=0c6174676ca959d5 -->

**Date**: 2026-11-07
**Task**: Bootstrap frontend guidelines and migrate eval Trellis artifacts
**Branch**: `main`

### Summary

Populate .trellis/spec/frontend/ guidelines, migrate historical eval task archives and workspace journals into the parent repository, and restore codex-candy-eval to the native plugin layout.

### Main Changes

- Populate all seven .trellis/spec/frontend/ files with source-backed rules and examples for native Vue and embedded evaluation web components, and update stale AGENTS.md references in backend specs.
- Migrate all seven 2026-10 archived tasks (renaming eval's bootstrap archive to 10-11-eval-bootstrap-guidelines) and the codex-candy-eval-plugin workspace journal into the parent repository.
- Remove .trellis/, .claude/, .codex/, .devin/, AGENTS.md, and .gitattributes from plugins/codex-candy-eval, align .gitignore with sub2api-plugin-template, and track .trellis/.template-hashes.json and .trellis/workspace/index.md in the parent repository.

### Git Commits

| Hash | Message |
|------|---------|
| `6009fdd` | docs(trellis): populate frontend specs and migrate eval trellis archives |

### Testing

- [OK] Verified 2026-10 archive listing, byte-identical journal migration, zero template placeholders in .trellis/spec/, ASD-STE100 compliance, and native 48-file layout in plugins/codex-candy-eval.

### Status

[OK] **Completed**


## Session 6: Sync codex-candy-eval v0.4.6 and upgrade baseline to Sub2API v0.2.20
<!-- trellis-session: v=2 fp=fb1ba0823aa611de -->

**Date**: 2026-11-08
**Task**: Sync codex-candy-eval v0.4.6 and upgrade baseline to Sub2API v0.2.20
**Branch**: `main`

### Summary

Restored cross-provider evaluation with unrestricted group selection, single-run fingerprint inspection with mode-aware status placement, name/email wildcard filters, SIWC 1-shot Responses probes, history schema v3, and upgraded all four repositories to Sub2API v0.2.20.

### Git Commits

| Hash | Message |
|------|---------|
| `bef76e1` | feat(eval): sync plugins and specs for Sub2API v0.2.20 |

### Status

[OK] **Completed**


## Session 7: Adapt plugins to Sub2API v0.2.23, fix quota scheduling, and add model defaults
<!-- trellis-session: v=2 fp=6fbb485a02f45325 -->

**Date**: 2026-11-19
**Task**: Adapt plugins to Sub2API v0.2.23, fix quota scheduling, and add model defaults
**Branch**: `main`

### Summary

Adapt both plugins to Sub2API v0.2.23 on Go 1.27.4, integrate quota scheduling and probe memoization, allow SIWC checks under local rate limits, and add gpt-6.2-sol to default degraded model removals.

### Main Changes

- Synchronize default /v1/usage and Goja quota_script exhaustion and recovery into Sub2API scheduling, shared unsupported-probe memoization, and single-read locked account saves with atomic identity CAS (quota f9ba14b).
- Replace full inspection account writes with narrow conditional updates, retain native Gemini and Anthropic stream paths, allow SIWC actions during local rate limits, and append gpt-6.2-sol to default degraded_remove_models (eval 4301252).
- Rebase quota-extension.patch onto Sub2API v0.2.23, repair loadActiveUsage cache config typing, and upgrade workflows, README, and backend specs to v0.2.23 and Go 1.27.4 (parent a338468).

### Git Commits

| Hash | Message |
|------|---------|
| `a338468` | chore: upgrade plugin delivery to Sub2API v0.2.23 |

### Testing

- [OK] Standalone patch checks, UPSTREAM_TAG=v0.2.23 five-platform build (10 binaries), Darwin arm64 -version check, independent trellis-check review, and read-only audit passed.

### Status

[OK] **Completed**


## Session 8: Sync codex-candy-eval v0.4.7 and remove redundant code
<!-- trellis-session: v=2 fp=78c7ee96840e4613 -->

**Date**: 2026-11-19
**Task**: Sync codex-candy-eval v0.4.7 and remove redundant code
**Branch**: `main`

### Summary

Synchronize codex-candy-eval on Sub2API v0.2.23 with upstream v0.4.7 fingerprint detection and UI via a two-parent merge commit, remove redundant code, and document the fork merge rule.

### Main Changes

- Merge upstream cpa-plugin-codex-candy-eval through 9682e76 (v0.4.7) as a two-parent merge commit, porting v0.4.7 detector math, 5,232,052-byte shared_detector.bin, models.json, analyze.json fixture, 3-card Fingerprint UI, and 0.4.7 version and SIWC User-Agent (eval 6fc5b1f).
- Delete dead wrappers, rename *Checked functions to canonical names, embed shared recordMeta, remove url.Values record plumbing, deduplicate AccountTestService SSE and request helpers, and extract inspection test reset helper (eval 6fc5b1f).
- Update codex-candy-eval submodule pointer, synchronize runtime-installation.md for v0.4.7 3-lag sequence acceptance, UI layout, and cpa-siwc-check/0.4.7 header, and document the fork two-parent merge rule in quality-guidelines.md (parent 5fcff51).

### Git Commits

| Hash | Message |
|------|---------|
| `5fcff51` | feat(eval): sync codex-candy-eval v0.4.7 and backend specs |

### Testing

- [OK] Standalone patch checks, codexeval/service/admin/UI unit tests, Playwright Chromium render check (8 px gap, 0 errors), UPSTREAM_TAG=v0.2.23 five-platform build (10 binaries), two read-only audits, and byte-identical tree verification against 90cb278 passed.

### Status

[OK] **Completed**


## Session 9: Add Gemini signature rectifier plugin and adapt to Sub2API v0.2.24
<!-- trellis-session: v=2 fp=06d500fc119e4f4e -->

**Date**: 2026-11-21
**Task**: Add Gemini signature rectifier plugin and adapt to Sub2API v0.2.24
**Branch**: `main`

### Summary

Added independent plugins/gemini-signature-rectifier plugin (Nanboom233/sub2api-gemini-signature-rectifier, default-false toggle, 4-rule RawMessage cleaner, Option B countTokens), refactored plugins/sub2api-quota-extension onto Sub2API v0.2.24 unified buildAccountUsageRefreshKey and single refreshKey caches (-4 hunks / -18 lines), passed standalone/combined v0.2.24 builds, Playwright Chromium visual checks, independent audits, and synced backend/frontend specs.

### Git Commits

| Hash | Message |
|------|---------|
| `0e15db5` | feat(plugins): add Gemini signature rectifier and adapt to v0.2.24 |

### Status

[OK] **Completed**


## Session 10: Sanitize cross-endpoint Gemini signature envelopes and trim rectifier bloat
<!-- trellis-session: v=2 fp=d56bb1fe6718ba66 -->

**Date**: 2026-11-22
**Task**: Sanitize cross-endpoint Gemini signature envelopes and trim rectifier bloat
**Branch**: `main`

### Summary

Upgraded plugins/gemini-signature-rectifier (08174fe) to validate protobuf field-2 and Vertex bare-Tink thoughtSignature envelopes before upstream native Gemini requests, group parallel function calls on retained parts, reuse one request-scoped settings gate across preparation and HTTP 400 recovery, cut 48 lines across patch and tests, synced backend spec, and verified standalone plus argument-free combined Sub2API v0.2.24 builds.

### Git Commits

| Hash | Message |
|------|---------|
| `4fcac15` | fix(plugins): update Gemini signature envelope rectifier and spec |

### Status

[OK] **Completed**
