# Source Build Flow

- Source: `/Users/minami/Code/C/cpa-plugin-codex-candy-eval`
- Date: 2026-10-23

## Existing Owners

| Source | Behavior |
| --- | --- |
| `scripts/build.py:19` | Copy source, apply ordered patches, and attach backend tests |
| `scripts/build.py:33` | Reuse dependencies, rebuild frontend, run focused checks, and compile the server |
| `scripts/build.py:62` | Stage the installer, compressed server, and licenses |
| `scripts/build.py:79` | Test the installer on the host and compile Linux/amd64 output |
| `scripts/build.py:98` | Accept `--source` and `--check` and own temporary workspace cleanup |
| `patches/series:1` | Order seven production patches |
| `scripts/installer/main.go:26` | Container paths and the 120-second readiness limit |
| `scripts/installer/main.go:34` | Installed v0.2.16/v0.2.17 and candidate v0.2.17 checks |
| `tests/installer/installer_test.go:20` | Fake Docker state and transaction checks |
| `.github/workflows/release.yml` | Prepare upstream v0.2.17, call the build, and publish the installer |

## Migration Boundary

The plugin origin is `https://github.com/Nanboom233/codex-candy-eval`.
Use it as `plugins/codex-candy-eval` through a Git submodule.
The original checkout was clean during inspection.
Move common build and installer code into this project.
Keep patches, business checks, and license inputs in the plugin.
The original root `LICENSE` contains the plugin's MIT license.
The original `licenses/` contains Sub2API, detector, renderer licenses, and redistribution notices.
The new plugin worktree retains root `LICENSE` for its MIT license and the original third-party license files under `licenses/`.
Remove `THIRD_PARTY_NOTICES.txt` from both migrated repositories. Do not create a replacement summary document.
Collect both inputs under the plugin's directory in the shared installer's `licenses/` resources.

The user rejected plugin management and requires automatic build discovery.
Discover all plugin submodules and use fixed input directories.
The original global plugin ROOT must become separate common-build and discovered-plugin paths.
Discover top-level `patches/*.patch` files in lexical filename order, without `patches/series` in the migrated plugin.
The existing numbered filename order matches the original series order.
Keep all actual test cases and support code under flat `tests/` in each repository.
Discover Python, Go, and CJS inputs. Run native Go suites through `go test` in their annotated temporary packages.
Keep standalone Go program support. Execute each discovered case once in deterministic order.
Store golden JSON under data-only `assets/`. Keep native Go suites and UI assertions directly under `tests/`.
Keep manual fixture helpers under flat `tests/native_*`, outside automatic discovery.
Use `tests/support.py` for native execution support, without a separate `scripts/check.py` or central package mapping.
The user confirmed build-time execution. Runtime installation only performs installation and readiness checks.
Preserve the original standalone command interface while adapting the new plugin worktree to these conventions.
Move upstream checkout and dependency preparation from the old release workflow into the common build entry.
The existing workflow already identifies `Wei-Shaw/sub2api`, tag `v0.2.17`, depth one, and pnpm 9.15.9.
The new common build targets v0.2.18 under the user's upgrade requirement.
Normalize and adapt plugin patches and tests directly to v0.2.18.
Compare installed and candidate versions with the shared build version, currently v0.2.18.
Replace the original allowlist with advisory warnings for mismatched or unreadable versions.
Request explicit confirmation before backup or replacement. Default, negative, EOF, and interrupted responses cancel installation.
The common command is `python3 scripts/build.py`, with no local source-path input.
Every build runs discovered plugin checks and shared installer tests.
The parent repository owns the authoritative installer suite. Remove the duplicate plugin suite during the approved test refactor.
A failed test stops the build and prevents publication of new outputs.
The original plugin's standalone source-path interface remains usable.
Migration and automatic multi-plugin composition are one delivery.
No product build or installation occurred during this research.

## Context Boundary

The imported backend specs describe the original v0.2.17 plugin workflow.
Use the current task PRD, design, and implementation plan where those specs conflict with this migration.
The common build must not restore local-source arguments, optional tests, `patches/series`, `--unidiff-zero`, or the fixed five-license inventory.
Reuse existing installer transaction tests. Historical manual Docker and browser checks are not acceptance gates for this task.
