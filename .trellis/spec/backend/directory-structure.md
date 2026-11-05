# Directory Structure

> Keep all test cases and support code in flat `tests/`. Use `assets/` for data resources only.

---

## Overview

Plugin submodules own production patches, business tests, and plugin license inputs.
The common build downloads the selected upstream tag and combines active plugin submodules in one temporary source tree.
An initialized plugin with no top-level `patches/*.patch` files contributes no patches, tests, or licenses to that build.
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
plugins/<name>/tests/test_*.test.ts Native Vue component suites
plugins/<name>/tests/native_*     Manual test fixture and support code
plugins/<name>/assets/           Data resources
plugins/<name>/scripts/          Standalone build helpers
plugins/<name>/.github/workflows/build.yml Independent build job and optional Release
plugins/<name>/LICENSE           Plugin license
plugins/<name>/licenses/         Original third-party license files
scripts/build.py                Automatic common build
.github/workflows/build.yml     Combined build job and optional Release
scripts/installer/              Go installer and restoration
tests/test_build.py             Shared build test cases
tests/test_installer_test.go    Native installer transaction and version cases
LICENSE                         Common build and installer license
README.md                       Chinese usage, build, and license instructions
licenses/                       Original third-party license files
dist/build/<os>-<arch>/          Ignored platform server and installer outputs
dist/work/                      Ignored workspace retained within one CI build job
.trellis/                       Workflow, specifications, tasks, and session records
```

The self-contained installer carries native and required Linux container payloads.
Users select Docker/Compose, a native program, or supported Apple container installation and retain the original program backup.
Builds download source and prepare dependencies in a temporary workspace. Rebuild the patched native frontend before embedding it.
Only compressed application programs and required license texts enter the installer payload.
The build assembles the installer in a temporary Go module and stages the native `tests/test_installer_test.go` suite there.
Keep installer tests out of production source and keep the raw server as a local build output.

Private configuration and reusable dependency caches remain outside source and package inputs.
Keep user instructions in `README.md`. Do not create a separate `docs/` tree or source overlay.

Each plugin and the template carry the complete build script, installer source, flat common tests, and license inputs.
Local builds and CI both run `python3 scripts/build.py` without arguments or external build Actions.
Standalone roots apply only their own patches. The parent applies active submodule patches in sorted order.
Keep equivalent build-kit files aligned. Run common cases once per build, not once per combined plugin.
All repositories produce versioned executable pairs under `dist/build/<os>-<arch>/`.
Names use `sub2api-plugins-[installer-]<upstream-tag>-<os>-<arch>`, where `installer-` is present only for installers.
Windows programs add `.exe`. CI uploads each file directly, with its basename as the artifact name.
Prepare PTerm and its dependencies in the temporary installer module. Do not add a root Go module.
Keep terminal messages under `scripts/installer/`, separate from installation decisions.

The template submodule lives at `plugins/sub2api-plugin-template` and has a Chinese usage README.
Its empty patches directory excludes it from combined builds. Its standalone build produces unmodified upstream Sub2API.

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
Native Vue suites use flat `test_*.test.ts` files. Keep their TypeScript support files in the same `tests/` directory.
The common runner stages these files under a temporary frontend `src/` directory and uses the native Vitest config.
Run explicit suite paths once. Remove staged files after success or failure.
Keep manual container fixture helpers under plugin `tests/native_*`, outside automatic `test_*` discovery.

The quota plugin lives at `plugins/sub2api-quota-extension`.
Its [production patch](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch) extends native account usage.
See [API Key Account Usage](./api-key-quota.md) for its service and frontend contracts.

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
