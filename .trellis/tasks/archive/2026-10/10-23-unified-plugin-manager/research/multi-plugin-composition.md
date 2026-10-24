# Patch Composition Findings

- Date: 2026-10-23
- Source: `/Users/minami/Code/C/cpa-plugin-codex-candy-eval`

## Context-Free Shared Edits

Seven patches add 39 files and change 12 existing upstream files.
Patch 0007 changes ten shared integration files and has nine context-free insertion hunks.

| Evidence | Existing insertion |
| --- | --- |
| `patches/0007-sub2api-integration.patch:42` | Settings routes |
| `patches/0007-sub2api-integration.patch:47` | Import and shutdown call |
| `patches/0007-sub2api-integration.patch:65` | Sidebar declarations and entries |
| `patches/0007-sub2api-integration.patch:74` | Frontend route |
| `scripts/build.py:27` | Applies with `--unidiff-zero` |

A fixture represented an earlier plugin inserting a helper before the intended target function.
A second context-free patch still passed `git apply --check --unidiff-zero`.
The intended original line now belonged to the helper.
This read-only Git check proved that acceptance did not verify the intended scope.

The user requires normalized cooperative patches and build failure on patch failure.
Normalize the existing series while preserving actual source changes and binary data.
Allow contextual edits to a shared file in deterministic discovery order.
Stop immediately on invalid input or a patch conflict.
Patch 0007 uses traditional unified headers while earlier patches use Git headers.
Read both original forms during migration. Build from normalized Git diffs.

## Combined Checks and Dependencies

The plugin has 12 backend Go test files and a golden JSON fixture.
Native private fixtures are referenced by `tests/backend/internal/service/account_codex_eval_service_test.go:26`
and `tests/backend/internal/handler/admin/codex_inspection_handler_test.go:17`.
The runner supplies temporary native package context for test suites stored directly in flat `tests/`.
Let Go compilation report conflicting symbols. Do not add a symbol scanner.
The target `tests/` directory is flat and contains actual assertions and test support code.
Discover `test_*.py`, `test_*.go`, and `test_*.cjs`. Keep manual helpers outside those patterns.
Native Go suites use `test_*_test.go` names and `// sub2api-package:` context annotations.
The runner stages each suite in its native temporary package and executes the discovered test names once with `go test`.
This retains private package access without public test APIs or asset-based wrapper suites.
The UI CJS suite lives directly in `tests/`. The parent owns the single authoritative installer suite.
Only golden JSON and other data belong in `assets/`.
Do not add `scripts/check.py` or a test-command manifest.
Pass source and installer staging paths through internal test environment variables.

The source also contains three manual container tools under `tests/installer/`.
`native_fixture_start.sh` starts PostgreSQL, Redis, a supplier server, and the application.
`native_inspection_fixture.py:90` replaces a named container's executable with that fixture wrapper.
Keep these manual tools in flat `tests/native_*` files in the migrated worktree and update their references.
Keep them outside automatic test discovery. Preserve relevant coverage and fixture contents while removing duplicate tests.
The user confirmed that automatic tests run during the build, with no plugin test execution during runtime installation.

`scripts/build.py:38` links the original frontend dependency installation.
The new common build downloads source automatically and installs dependencies from the patched frozen lockfile in temporary source.
Use normal package caches instead of requiring an existing upstream dependency directory.
Keep Go modules readonly and preserve unrelated local source checkouts.

## Installer and Licenses

The installer embeds one compressed server and replaces the full executable.
Preserve backup, readiness, and restoration for that whole executable.
Keep ordinary build progress. The user did not request plugin-management records or an inventory UI.

`tests/installer/installer_test.go:434` assumes exactly five top-level license files.
Replace that assumption with a complete recursive comparison against automatically discovered license inputs.
Preserve namespaced equal filenames and actual embedded text.
Remove `THIRD_PARTY_NOTICES.txt` from both migrated repositories. The user requires the original license files only.
Keep original license texts and their copyright notices.
Each repository keeps its own license at root `LICENSE` and original third-party license files under `licenses/`.
Collect both inputs under installer resources `licenses/`, with separate plugin directories for equal filenames.
Always retain the base Sub2API license.

## Automatic Discovery Decision

All plugin submodules under `plugins/` participate in each build.
Native `.gitmodules` identifies required checkouts and detects missing initialization.
Sort submodule paths and each plugin's top-level `patches/*.patch` filenames lexically.
The original numbered filenames sort into exactly the original series order. Remove the migrated plugin's series file.
Use flat `tests/` directories with native Python, Go, and CJS discovery and fixed license paths.
There is no plugin registry, selection flag, enable state, central command configuration, or dependency resolver.
Target v0.2.18 in the shared build. Compare installed and candidate versions with that shared build version.
Mismatched or unreadable versions produce warnings and require explicit confirmation before backup or replacement.
Default, negative, EOF, and interrupted responses cancel installation. Remove the original installed-version allowlist.
Download v0.2.18 automatically and adapt plugin patches, tests, and installer metadata to that release.
The original v0.2.17 source can retain `0.2.16` in its VERSION marker. Preserve linker-based release metadata.
