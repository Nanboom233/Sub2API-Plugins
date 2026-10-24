# Directory Structure

> Keep all test cases and support code in flat `tests/`. Use `assets/` for data resources only.

---

## Overview

Plugin submodules own production patches, business tests, and plugin license inputs.
The common build downloads Sub2API v0.2.18 and combines every plugin under `plugins/` in one temporary source tree.
This repository has no root Go module or shared-library entry point.
The user package replaces the server binary without compilation on the installation host.

Owners: [common build](../../../scripts/build.py), [evaluation patches](../../../plugins/codex-candy-eval/patches/), and [installer source](../../../scripts/installer/).

---

## Directory Layout

```text
.gitmodules                       Native plugin submodule paths
plugins/<name>/patches/*.patch    Lexically ordered production patches
plugins/<name>/tests/test_*.py    Python test cases
plugins/<name>/tests/test_*.go    Native Go suites or standalone Go cases
plugins/<name>/tests/test_*.cjs   Native UI test cases
plugins/<name>/tests/native_*     Manual test fixture and support code
plugins/<name>/assets/           Data resources
plugins/<name>/scripts/          Standalone build helpers
plugins/<name>/LICENSE           Plugin license
plugins/<name>/licenses/         Original third-party license files
scripts/build.py                Automatic common build
scripts/installer/              Go installer and restoration
tests/test_build.py             Shared build test cases
tests/test_installer_test.go    Native installer transaction and version cases
LICENSE                         Common build and installer license
licenses/                       Original third-party license files
dist/build/                     Ignored server and installer outputs
.trellis/                       Workflow, specifications, tasks, and session records
```

The self-extracting installer uses its embedded server and Docker CLI.
Users select a running container, retain its backup and open 账户评估 in the native administrator sidebar.
Builds download source and prepare dependencies in a temporary workspace. Rebuild the patched native frontend before embedding it.
Only the compressed server and required license texts enter the installer payload.
The build assembles the installer in a temporary Go module and stages the native `tests/test_installer_test.go` suite there.
Keep installer tests out of production source and keep the raw server as a local build output.

Private configuration and reusable dependency caches remain outside source and package inputs.
Keep user instructions in `README.md`. Do not create a separate `docs/` tree or source overlay.

The first plugin lives at `plugins/codex-candy-eval`.
Its existing numbered filenames sort into the original order below. Other plugins need no numeric prefix or series file.

```text
0001-evaluation-core.patch
0002-evaluation-data.patch
0003-vendor-assets.patch
0004-admin-channel.patch
0005-inspection.patch
0006-evaluation-ui.patch
0007-sub2api-integration.patch
```

Keep test source and test-only data out of production patches.
Keep `tests/` flat. Native suites use `test_*_test.go` names with their original Go package declarations.
The `// sub2api-package:` annotation identifies the native package in temporary source.
For example, `// sub2api-package: backend/internal/codexeval` preserves private package access without a public testing API.
The runner stages and executes native suites directly. Test code must not live in assets or encoded source strings.
Keep manual container fixture helpers under plugin `tests/native_*`, outside automatic `test_*` discovery.

Evidence: [repository layout and private configuration](../../../AGENTS.md).

---

## Native Module Organization

- Keep evaluation tasks and account admission in `codexeval/runtime.go`.
- Keep each evaluation's request types, results, runner, and algorithm in its existing package.
- Keep the LM detector in `fingerprint.go` and `fingerprint_detector.go`. Retired ModelTrace and probe algorithms have no runtime owner.
- Keep detector assets under `codexeval/data/lm-detector/` in patch `0002`, including its Git binary hunk.
- Keep the detector golden fixture at plugin `assets/lm-detector-golden.json`, outside production patches.
- Keep shared request retries in `model.go` and the shared context decoder in `codex.go`.
- Keep corresponding Go suites directly under plugin `tests/test_*_test.go` with explicit native package context.
- Keep history persistence in `codexeval/state.go`.
- Keep inspection scheduling and notifications in `codexeval/inspection*.go`.
- Keep native settings persistence and upstream account sending in `internal/service/` additions.
- Keep administrator HTTP adaptation in `internal/handler/admin/` additions.
- Keep page logic in `codexeval/web/` and assembly in `codexeval/web.go`.
- Keep the iframe view with the evaluation UI patch and upstream edits with the integration patch.

Do not create a router framework, service hierarchy, or new package solely to match a generic architecture template.

Examples: [evaluation core](../../../plugins/codex-candy-eval/patches/0001-evaluation-core.patch) and [native inspection](../../../plugins/codex-candy-eval/patches/0005-inspection.patch).

---

## Native Examples

| Work | Owner | Existing verification |
| --- | --- | --- |
| Change tasks, cancellation, or history | `runtime.go` and `state.go` | Plugin `tests/test_codexeval_runtime_test.go` |
| Change automatic Candy inspection | `inspection*.go` | Plugin `tests/test_codexeval_inspection_test.go` |
| Change native account transport | `account_codex_eval_service.go` | Plugin `tests/test_service_account_codex_eval_service_test.go` and lifetime suite |
| Change settings storage | `codex_inspection_settings.go` | Plugin `tests/test_service_codex_inspection_settings_test.go` |
| Change embedded page behavior | `web.go` and `web/` | Plugin `tests/test_ui.cjs` |

When adding an embedded asset, update its Go embed declaration and page assembly.
Keep source, tests, and package ownership aligned with [binary delivery](./minimal-linux-delivery.md).
