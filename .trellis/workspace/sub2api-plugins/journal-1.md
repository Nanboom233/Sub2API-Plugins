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
