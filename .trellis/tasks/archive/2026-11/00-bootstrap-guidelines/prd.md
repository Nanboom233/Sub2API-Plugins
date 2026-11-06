# Bootstrap Guidelines and Migrate Eval Trellis Artifacts

## Goal

Populate the remaining project development guidelines in `.trellis/spec/frontend/` with real source-backed rules and examples, and migrate all historical Trellis artifacts from `plugins/codex-candy-eval` into the main repository so `plugins/codex-candy-eval` returns to the native plugin directory structure.

## Confirmed Facts

- Detailed research evidence is recorded in `research/eval-trellis-migration.md`.
- `plugins/codex-candy-eval` tracks 530 files: 48 native plugin files and 482 Trellis/AI-assistant files (`.trellis/` with 370 files, `.claude/` with 52 files, `.devin/` with 51 files, `.codex/` with 8 files, and `AGENTS.md` with 1 file).
- Native plugins (`plugins/sub2api-quota-extension` and `plugins/sub2api-plugin-template`) contain only `.github/workflows/build.yml`, `.gitignore`, `LICENSE`, optional `README.md`, optional `assets/`, `licenses/`, `patches/`, `scripts/`, and `tests/`.
- Parent `.trellis/spec/backend/` (10 files) and `.trellis/spec/guides/` (3 files) are already complete, source-backed, and free of placeholders, superseding all 12 files in `plugins/codex-candy-eval/.trellis/spec/`.
- Parent `.trellis/spec/frontend/` contains `index.md` and 6 template files (`directory-structure.md`, `component-guidelines.md`, `hook-guidelines.md`, `state-management.md`, `type-safety.md`, and `quality-guidelines.md`) with 30 `(To be filled by the team)` placeholders.
- `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/` contains 7 archived task directories (320 files): `00-bootstrap-guidelines`, `10-11-sub2api-runtime-patch`, `10-18-inspection-controls`, `10-18-inspection-verdict-state`, `10-19-inspection-model-control`, `10-19-upstream-compare-adaptation`, and `10-19-upstream-evaluation-sync`.
- `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` contains `index.md` and `journal-1.md` (8 recorded sessions from 2026-10-11 to 2026-10-20), which do not collide with parent `.trellis/workspace/sub2api-plugins/`.
- `plugins/codex-candy-eval/.gitattributes` mixes two Trellis/Devin rules with `patches/*.patch -whitespace`, and `plugins/codex-candy-eval/.gitignore` includes `.playwright-cli/`, `.agents`, and `/output/` entries absent from `plugins/sub2api-plugin-template/.gitignore`.

## Requirements

- R1. Migrate all 7 archived task directories from `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/` into parent `.trellis/tasks/archive/2026-10/`.
  Rename the eval bootstrap archive directory from `00-bootstrap-guidelines` to `10-11-eval-bootstrap-guidelines` and update its `task.json` `id` and `name` fields to `eval-bootstrap-guidelines` so it does not collide with parent `00-bootstrap-guidelines`.
  Preserve the other 6 archived task directories (`10-11-sub2api-runtime-patch`, `10-18-inspection-controls`, `10-18-inspection-verdict-state`, `10-19-inspection-model-control`, `10-19-upstream-compare-adaptation`, and `10-19-upstream-evaluation-sync`) and all 320 archived files unchanged.
- R2. Migrate `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` (`index.md` and `journal-1.md`) into parent `.trellis/workspace/codex-candy-eval-plugin/` without modifying parent `.trellis/workspace/sub2api-plugins/`.
- R3. Retain parent `.trellis/spec/backend/` and `.trellis/spec/guides/` as the single authoritative backend and cross-layer specification set.
  Do not overwrite newer parent specifications with older standalone copies from `plugins/codex-candy-eval/.trellis/spec/`.
  Update stale `../../../AGENTS.md` evidence links in `.trellis/spec/backend/directory-structure.md:97`, `.trellis/spec/backend/logging-guidelines.md:76`, and `.trellis/spec/backend/quality-guidelines.md:88,134` so they point to the authoritative parent `.gitignore` and `.trellis/spec/` rules.
- R4. Populate parent `.trellis/spec/frontend/` (`index.md`, `directory-structure.md`, `component-guidelines.md`, `hook-guidelines.md`, `state-management.md`, `type-safety.md`, and `quality-guidelines.md`) with real project frontend guidelines and code examples backed by `plugins/sub2api-quota-extension` and `plugins/codex-candy-eval`.
  Cover both frontend surfaces in this repository:
  1. Native Sub2API Vue 3 + TypeScript + Tailwind CSS admin UI patches (`plugins/sub2api-quota-extension/patches/quota-extension.patch`, `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch`) and flat Vitest suites (`plugins/sub2api-quota-extension/tests/test_*.test.ts`).
  2. Standalone embedded evaluation web modules (`plugins/codex-candy-eval/patches/0006-evaluation-ui.patch` under `backend/internal/codexeval/web/`) and Node UI verification (`plugins/codex-candy-eval/tests/test_ui.cjs`).
  Remove all `(To be filled by the team)` and `TODO` placeholders across `.trellis/spec/`, and mark all frontend guides as `Current` in `.trellis/spec/frontend/index.md`.
- R5. Remove all Trellis and AI-assistant directories and files from `plugins/codex-candy-eval`: `.trellis/`, `.claude/`, `.codex/`, `.devin/`, `AGENTS.md`, and `.gitattributes`.
  Align `plugins/codex-candy-eval/.gitignore` with `plugins/sub2api-plugin-template/.gitignore` (`dist/`, `__pycache__/`, `*.py[cod]`, `.DS_Store`, `.env`, `.env.*`).
  Preserve all 48 native plugin files in `plugins/codex-candy-eval` (`.github/workflows/build.yml`, `.gitignore`, `LICENSE`, `README.md`, `assets/`, `licenses/`, `patches/`, `scripts/`, and `tests/`) untouched.

## Acceptance Criteria

- [x] AC1 (R1). Parent `.trellis/tasks/archive/2026-10/` contains all 7 migrated eval archived task directories (`10-11-eval-bootstrap-guidelines`, `10-11-sub2api-runtime-patch`, `10-18-inspection-controls`, `10-18-inspection-verdict-state`, `10-19-inspection-model-control`, `10-19-upstream-compare-adaptation`, and `10-19-upstream-evaluation-sync`) alongside the 3 existing parent `2026-10` archives, and `python3 ./.trellis/scripts/task.py list-archive 2026-10` lists all 10 tasks without slug collisions.
- [x] AC2 (R2). Parent `.trellis/workspace/codex-candy-eval-plugin/index.md` and `journal-1.md` match the migrated eval workspace history byte-for-byte, and `.trellis/workspace/sub2api-plugins/` remains intact.
- [x] AC3 (R3, R4). All files in `.trellis/spec/backend/`, `.trellis/spec/frontend/`, and `.trellis/spec/guides/` describe actual repository patterns with real file references and code examples, and `rg -i "To be filled|TODO: fill" .trellis/spec/` returns zero placeholder matches.
- [x] AC4 (R5). `plugins/codex-candy-eval` contains only the native plugin files (`.github/workflows/build.yml`, `.gitignore`, `LICENSE`, `README.md`, `assets/lm-detector-golden.json`, `licenses/*`, `patches/*`, `scripts/**`, and `tests/*`), with zero `.trellis/`, `.claude/`, `.codex/`, `.devin/`, `AGENTS.md`, or `.gitattributes` entries.
- [x] AC5 (R5). `plugins/codex-candy-eval/.gitignore` matches `plugins/sub2api-plugin-template/.gitignore`, and `git diff` in `plugins/codex-candy-eval` shows zero changes to any patch, script, asset, license, README, or test file.

## Out of Scope

- Modifying any runtime patch (`patches/*.patch`), installer source (`scripts/installer/*`), build script (`scripts/build.py`), CI workflow (`.github/workflows/build.yml`), or test file (`tests/*`) in any repository.
- Running a full five-platform Sub2API compilation or remote GitHub Actions workflow run (no product code changes).
- Modifying `plugins/sub2api-quota-extension` or `plugins/sub2api-plugin-template`.
