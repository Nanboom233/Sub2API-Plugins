# Eval Trellis Artifact Migration and Guideline Bootstrap Research

- **Query**: Compare `plugins/codex-candy-eval` Trellis artifacts against parent `.trellis/` and audit `.trellis/spec/` for `00-bootstrap-guidelines`.
- **Scope**: `plugins/codex-candy-eval`, `plugins/sub2api-quota-extension`, `plugins/sub2api-plugin-template`, and `.trellis/`.
- **Date**: 2026-11-06

---

## 1. Files Found

| File or Directory | One-Line Description |
| --- | --- |
| `plugins/codex-candy-eval/.trellis/` | Evaluation plugin Trellis directory with 370 tracked files across specs, tasks, workspace, scripts, and config. |
| `plugins/codex-candy-eval/.claude/` | Claude Code platform integration directory with 52 tracked agent, command, hook, setting, and skill files. |
| `plugins/codex-candy-eval/.codex/` | Codex platform integration directory with 8 tracked agent, config, and hook files. |
| `plugins/codex-candy-eval/.devin/` | Devin platform integration directory with 51 tracked agent, local config, hook, skill, and workflow files. |
| `plugins/codex-candy-eval/AGENTS.md` | Managed 22-line Trellis instruction block for AI assistants. |
| `plugins/codex-candy-eval/.gitattributes` | Git attributes file with two Trellis/Devin rules and one `patches/*.patch -whitespace` rule. |
| `plugins/codex-candy-eval/.gitignore` | Plugin ignore file that adds `.playwright-cli/`, `.agents`, and `/output/` entries. |
| `plugins/sub2api-quota-extension/.gitignore` | Native quota plugin ignore file with five standard build and Python cache rules. |
| `plugins/sub2api-plugin-template/.gitignore` | Native template plugin ignore file with seven build, Python cache, and `.env` rules. |
| `.trellis/spec/backend/` | Ten complete parent backend specification files covering combined and standalone plugin contracts. |
| `.trellis/spec/frontend/` | One filled frontend index file and six unfilled template specification files with 30 placeholders. |
| `.trellis/spec/guides/` | Three parent thinking guides with repository license, cache, and GitHub credential rules. |
| `.trellis/tasks/00-bootstrap-guidelines/` | Active parent bootstrap task directory containing `task.json` and template `prd.md`. |

---

## 2. Eval vs Native Plugin Structure

### Tracked and Untracked File Comparison

All three plugin submodules have clean Git working trees with zero untracked or ignored files on disk.
Each plugin checkout contains a `.git` file that points to `../../.git/modules/plugins/<name>`.

| Top-Level Entry | `codex-candy-eval` | `sub2api-quota-extension` | `sub2api-plugin-template` | Category |
| --- | --- | --- | --- | --- |
| `.claude/` | 52 | 0 | 0 | AI assistant integration |
| `.codex/` | 8 | 0 | 0 | AI assistant integration |
| `.devin/` | 51 | 0 | 0 | AI assistant integration |
| `.trellis/` | 370 | 0 | 0 | Trellis workflow and records |
| `AGENTS.md` | 1 | 0 | 0 | AI assistant instructions |
| `.gitattributes` | 1 | 0 | 0 | Mixed Trellis and patch attributes |
| `.github/workflows/build.yml` | 1 | 1 | 1 | Native plugin build workflow |
| `.gitignore` | 1 | 1 | 1 | Native plugin ignore rules |
| `LICENSE` | 1 | 1 | 1 | Native plugin root license |
| `README.md` | 1 | 0 | 1 | Native plugin documentation |
| `assets/` | 1 | 0 | 0 | Native plugin data resources |
| `licenses/` | 7 | 7 | 3 | Native plugin third-party licenses |
| `patches/` | 7 | 1 | 1 | Native plugin patches (`.gitkeep` in template) |
| `scripts/` | 9 | 9 | 9 | Standalone build and Go installer kit |
| `tests/` | 19 | 8 | 3 | Flat plugin and common test files |
| **Total Tracked Files** | **530** | **28** | **20** | **482 Trellis/AI files + 48 plugin files** |

### Trellis and AI-Assistant Files in `plugins/codex-candy-eval`

`plugins/codex-candy-eval` tracks 482 dedicated Trellis and AI-assistant files plus mixed rules in `.gitattributes` and `.gitignore`:

1. `plugins/codex-candy-eval/.trellis/` (370 files): `.gitignore`, `.template-hashes.json`, `.version`, `config.yaml`, `workflow.md`, `agents/` (2), `scripts/` (26), `spec/` (12), `tasks/archive/2026-10/` (320), and `workspace/` (3).
2. `plugins/codex-candy-eval/.claude/` (52 files): `agents/trellis-{check,implement,research}.md` (3), `commands/trellis/{continue,finish-work}.md` (2), `hooks/*.py` (3), `settings.json` (1), and `skills/trellis-*` (43).
3. `plugins/codex-candy-eval/.codex/` (8 files): `agents/trellis-{check,implement,research}.toml` (3), `config.toml` (1), `hooks.json` (1), and `hooks/*.py` (3).
4. `plugins/codex-candy-eval/.devin/` (51 files): `agents/trellis-{check,implement,research}.md` (3), `config.local.json` (1), `hooks.v1.json` (1), `skills/trellis-*` (43), and `workflows/trellis-{continue,finish-work,start}.md` (3).
5. `plugins/codex-candy-eval/AGENTS.md` (1 file): Byte-identical to parent `AGENTS.md` (1073 bytes, lines 1-22).
6. `plugins/codex-candy-eval/.gitattributes` (1 file): Lines 1-9 define `.trellis/workspace/*/journal-*.md merge=union`, line 12 defines `patches/*.patch -whitespace`, and line 13 defines `.devin/agents/*.md text eol=lf`.

Note on `.codex/` in `plugins/codex-candy-eval` versus parent `.codex/`:
- `plugins/codex-candy-eval/.codex/config.toml:38-39` includes machine-local `[mcp_servers.pycharm]` (`url = "http://127.0.0.1:64462/stream"`), which parent `.codex/config.toml` omits.
- `plugins/codex-candy-eval/.codex/hooks.json` and hook scripts invoke `python`, whereas parent `.codex/` invokes `python3` and enables `allow_single_session_fallback=True` in `.codex/hooks/inject-subagent-context.py:1125-1129`.
- `plugins/codex-candy-eval/.devin/config.local.json` and `hooks.v1.json` are tracked in `plugins/codex-candy-eval` despite earlier bootstrap notes that marked them machine-only.

### `.gitignore` Comparison Across Repositories

| Entry | `plugins/codex-candy-eval/.gitignore` | `plugins/sub2api-quota-extension/.gitignore` | `plugins/sub2api-plugin-template/.gitignore` | Parent `.gitignore` |
| --- | --- | --- | --- | --- |
| `dist/` | Yes (line 1) | Yes (line 1) | Yes (line 1) | Yes (line 1) |
| `__pycache__/` | Yes (line 11) | Yes (line 2) | Yes (line 2) | Yes (line 2) |
| `*.py[cod]` | Yes (line 12) | Yes (line 3) | Yes (line 3) | Yes (line 3) |
| `.DS_Store` | Yes (line 2) | Yes (line 4) | Yes (line 4) | Yes (line 4) |
| `.env` and `.env.*` | Yes (lines 5-6) | No | Yes (lines 5-6) | Yes (lines 5-6) |
| `.playwright-cli/` | Yes (line 7) | No | No | No |
| `.agents` | Yes (line 8) | No | No | No |
| `/output/` | Yes (line 13) | No | No | No |
| `.trellis/.runtime/` | No | No | No | Yes (line 7) |

Matching `plugins/sub2api-plugin-template/.gitignore` (7 lines: `dist/`, `__pycache__/`, `*.py[cod]`, `.DS_Store`, `.env`, `.env.*`) returns `plugins/codex-candy-eval/.gitignore` to the native plugin template convention.

---

## 3. Eval `.trellis/` Artifact Inventory and Parent Comparison

### A. Specs (`plugins/codex-candy-eval/.trellis/spec/` vs `.trellis/spec/`)

Parent `.trellis/spec/` contains 20 files across `backend/` (10), `frontend/` (7), and `guides/` (3).
`plugins/codex-candy-eval/.trellis/spec/` contains 12 files across `backend/` (9) and `guides/` (3).
No spec file exists only in `plugins/codex-candy-eval`.
Eight spec files exist only in parent `.trellis/spec/`: `backend/api-key-quota.md` and all seven files under `frontend/`.

| Relative Spec Path | Status | Size (Parent vs Eval) | Key Differences |
| --- | --- | --- | --- |
| `guides/code-reuse-thinking-guide.md` | Byte-identical | 7381 B vs 7381 B | Identical content. |
| `guides/cross-layer-thinking-guide.md` | Byte-identical | 14979 B vs 14979 B | Identical content. |
| `guides/index.md` | Parent is newer | 5612 B vs 4378 B | Parent adds Documentation and Manifest Files (`lines 5-16`) and GitHub Credential Use (`lines 25-31`). |
| `backend/database-guidelines.md` | Parent is newer | 8867 B vs 8860 B | Parent `line 120` adds the word `plugin` before `tests/test_service_codex_inspection_settings_test.go`. |
| `backend/directory-structure.md` | Parent is newer | 8425 B vs 6210 B | Parent documents multi-plugin submodule layout, `plugins/<name>/` paths, template, and quota plugin (`lines 9-96`). |
| `backend/error-handling.md` | Parent is newer | 6712 B vs 6412 B | Parent updates ten relative links from `../../../patches/` and `../../../tests/` to `../../../plugins/codex-candy-eval/...`. |
| `backend/index.md` | Parent is newer | 5438 B vs 5159 B | Parent describes submodule discovery, links `api-key-quota.md`, and references `../guides/index.md#documentation-and-manifest-files`. |
| `backend/logging-guidelines.md` | Parent is newer | 4729 B vs 4454 B | Parent updates nine relative links to `../../../plugins/codex-candy-eval/patches/` and `tests/`. |
| `backend/minimal-linux-delivery.md` | Parent is newer | 32766 B vs 29327 B | Parent covers combined and standalone builds, recursive licenses, Vue test staging, and dedicated `-version` probing. |
| `backend/native-inspection.md` | Parent is newer | 25364 B vs 25336 B | Parent `lines 13-19` prefix owner paths with `Plugin` and note relativity to `plugins/codex-candy-eval/`. |
| `backend/quality-guidelines.md` | Parent is newer | 8755 B vs 7893 B | Parent adds submodule discovery, Vue Vitest staging, and advisory version-warning test rules (`lines 8-47`). |
| `backend/runtime-installation.md` | Parent is newer | 18207 B vs 18598 B | Parent updates links to `plugins/codex-candy-eval/` and removes three dead links to eval archived task `10-11-sub2api-runtime-patch`. |
| `backend/api-key-quota.md` | Only in parent | 15429 B vs absent | Documents the `sub2api-quota-extension` backend and frontend contracts. |
| `frontend/*` (7 files) | Only in parent | 6508 B total vs absent | `frontend/index.md` links `api-key-quota.md`. The other six files are unfilled templates. |

Every difference in `plugins/codex-candy-eval/.trellis/spec/` represents an older standalone-only phrasing or relative path.
Parent `.trellis/spec/` already incorporates all evaluation, inspection, persistence, error, logging, and delivery rules from `plugins/codex-candy-eval/.trellis/spec/`.

### B. Archived Tasks (`plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/*` vs `.trellis/tasks/archive/*`)

`plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/` contains 7 archived task directories (320 files total):

| Eval Archived Task Directory | `id` / `name` | Created / Completed | Commit | Files (Top + Research) |
| --- | --- | --- | --- | --- |
| `00-bootstrap-guidelines` | `00-bootstrap-guidelines` | 2026-10-11 / 2026-10-11 | `f84347d` | 6 total (6 top, 0 research) |
| `10-11-sub2api-runtime-patch` | `sub2api-runtime-patch` | 2026-10-11 / 2026-10-18 | `6cac3a2788...` | 237 total (7 top, 230 research) |
| `10-18-inspection-controls` | `inspection-controls` | 2026-10-18 / 2026-10-18 | `75f5a3f` | 18 total (6 top, 12 research) |
| `10-18-inspection-verdict-state` | `inspection-verdict-state` | 2026-10-18 / 2026-10-18 | `8c22806` | 10 total (9 top, 1 research) |
| `10-19-inspection-model-control` | `inspection-model-control` | 2026-10-19 / 2026-10-19 | `c4cc8e8df5...` | 20 total (6 top, 14 research) |
| `10-19-upstream-compare-adaptation` | `upstream-compare-adaptation` | 2026-10-19 / 2026-10-20 | `b67452ee31...` | 12 total (6 top, 6 research) |
| `10-19-upstream-evaluation-sync` | `upstream-evaluation-sync` | 2026-10-19 / 2026-10-19 | `null` | 17 total (6 top, 11 research) |

Parent `.trellis/tasks/` contains:
- Active task: `.trellis/tasks/00-bootstrap-guidelines` (`status: "planning"`, `createdAt: "2026-10-22"`, 2 files before research).
- `.trellis/tasks/archive/2026-10/`: `10-23-unified-plugin-manager` (12 files), `10-25-apikey-quota-monitoring` (11 files), and `10-26-apikey-quota-scripts` (12 files).
- `.trellis/tasks/archive/2026-11/`: `10-30-inspection-settings-attribution` (25 files) and `10-31-installation-methods` (18 files).

Collision analysis:
- None of the 7 directory names in `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/` currently exist under parent `.trellis/tasks/archive/2026-10/`.
- However, `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/00-bootstrap-guidelines` shares the exact task name `00-bootstrap-guidelines` with the active parent task `.trellis/tasks/00-bootstrap-guidelines`.
- If the active parent task `.trellis/tasks/00-bootstrap-guidelines` is later archived in `2026-11`, `task.py archive` places it under `.trellis/tasks/archive/2026-11/00-bootstrap-guidelines`.
- Even across different archive month directories, `task.py` lookups and `list-archive` output would show two `00-bootstrap-guidelines` tasks. Rename or merge the eval bootstrap archive (for example, `10-11-eval-bootstrap-guidelines`).

### C. Workspace Journals (`plugins/codex-candy-eval/.trellis/workspace/` vs `.trellis/workspace/`)

1. `plugins/codex-candy-eval/.trellis/workspace/index.md` (126 lines, 2310 bytes) is byte-identical to parent `.trellis/workspace/index.md` (which is currently untracked in parent Git).
2. `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` contains `index.md` (49 lines, 1624 bytes) and `journal-1.md` (293 lines, 10086 bytes).
3. `codex-candy-eval-plugin/index.md` and `journal-1.md` record 8 completed AI development sessions from `2026-10-11` to `2026-10-20` under developer identity `codex-candy-eval-plugin`.
4. Parent `.trellis/workspace/sub2api-plugins/` contains `index.md` (44 lines, 1471 bytes) and `journal-1.md` (145 lines, 5593 bytes). It records 4 completed sessions from `2026-10-25` to `2026-11-06` under `sub2api-plugins`.
5. Distinct developer directory names (`codex-candy-eval-plugin` vs `sub2api-plugins`) allow copying `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` into `.trellis/workspace/` without file collisions.

### D. Other `.trellis/` Files in `plugins/codex-candy-eval`

| Relative Path in `.trellis/` | Parent Size | Eval Size | Comparison Result |
| --- | --- | --- | --- |
| `.gitignore` | 461 B | 461 B | Byte-identical. |
| `.template-hashes.json` | 18429 B (143 keys) | 24129 B (184 keys) | Differ. Parent tracks `.agents`, `.codex`, `.opencode`, `.trellis`, `AGENTS.md` (untracked in parent Git). Eval tracks `.agents`, `.claude`, `.codex`, `.devin`, `.trellis`. |
| `.version` | 6 B (`0.6.17`) | 6 B (`0.6.17`) | Byte-identical. |
| `agents/check.md` | 2537 B | 2537 B | Byte-identical. |
| `agents/implement.md` | 2344 B | 2344 B | Byte-identical. |
| `config.yaml` | 7027 B | 7027 B | Byte-identical. |
| `scripts/**` (26 `.py` files) | 26 files | 26 files | All 26 Python script files are byte-identical. |
| `workflow.md` | 39348 B | 39348 B | Byte-identical. |

---

## 4. Parent `.trellis/spec/` Current State (for `00-bootstrap-guidelines`)

### A. Backend Guidelines (`.trellis/spec/backend/`)

All 10 files in `.trellis/spec/backend/` are fully populated with source-backed project guidelines and contain zero template placeholders:
1. `index.md` (83 lines): Defines v0.2.19 scope, active guideline table, pre-development checklist, quality check, and `/output` documentation rules.
2. `directory-structure.md` (135 lines): Defines parent and submodule directory layout, patch application order, flat `tests/` rules, and native module owners.
3. `database-guidelines.md` (133 lines): Defines PostgreSQL `settings` storage, account `extra` keys, and `schema_version: 2` JSON evaluation history.
4. `error-handling.md` (111 lines): Defines native response helpers, `executeModel`, `HTTPUpstreamRequestError`, bounded retries, and cancellation.
5. `logging-guidelines.md` (79 lines): Defines diagnostic channels, `storage_error`, 500-rune truncation, and credential redaction rules.
6. `quality-guidelines.md` (137 lines): Defines `python3 scripts/build.py` checks, Go/Vue/CJS test staging, and the hybrid `/git-commit` and Trellis finish workflow.
7. `runtime-installation.md` (239 lines): Defines administrator evaluation sending, tasks, history, Pelican/fingerprint rules, and embedded page behavior.
8. `native-inspection.md` (341 lines): Defines automatic Candy inspection settings, scheduling, participation, verdicts, model removal/recovery, and notifications.
9. `minimal-linux-delivery.md` (382 lines): Defines five-platform standalone and combined builds, single-job cached CI, SDK uploads, Release recreation, and the Go installer.
10. `api-key-quota.md` (227 lines): Defines default upstream quota detection, Goja custom scripts, draft test previews, and Vue account cell behavior.

### B. Thinking Guides (`.trellis/spec/guides/`)

All 3 files in `.trellis/spec/guides/` are populated and contain zero template placeholders:
1. `index.md` (126 lines): Defines project rules for documentation/manifests (`lines 5-16`), temporary caches (`lines 18-23`), and GitHub credential approval (`lines 25-31`), followed by standard thinking triggers.
2. `code-reuse-thinking-guide.md` (225 lines): Standard Trellis code-reuse thinking guide.
3. `cross-layer-thinking-guide.md` (290 lines): Standard Trellis cross-layer thinking guide.

### C. Frontend Guidelines (`.trellis/spec/frontend/`)

Only `.trellis/spec/frontend/index.md` has project-specific text (`lines 7-28`), and it explicitly marks the 6 individual frontend guideline files as `To fill`:
- `.trellis/spec/frontend/index.md:13` states: `The template guides below remain unfilled and do not add acceptance requirements.`
- `.trellis/spec/frontend/directory-structure.md` (55 lines): Unfilled template with 4 `(To be filled by the team)` placeholders and a generic `src/` tree comment.
- `.trellis/spec/frontend/component-guidelines.md` (60 lines): Unfilled template with 6 `(To be filled by the team)` placeholders.
- `.trellis/spec/frontend/hook-guidelines.md` (52 lines): Unfilled template with 5 `(To be filled by the team)` placeholders (uses React-oriented prompts such as React Query/SWR).
- `.trellis/spec/frontend/state-management.md` (52 lines): Unfilled template with 5 `(To be filled by the team)` placeholders.
- `.trellis/spec/frontend/type-safety.md` (52 lines): Unfilled template with 5 `(To be filled by the team)` placeholders.
- `.trellis/spec/frontend/quality-guidelines.md` (52 lines): Unfilled template with 5 `(To be filled by the team)` placeholders.

Actual frontend architecture in this repository for populating `.trellis/spec/frontend/`:
1. **Two distinct frontend surfaces in plugin patches**:
   - **Native Sub2API Vue 3 + TypeScript + Tailwind CSS admin UI**: Patched by `quota-extension.patch`, `0006-evaluation-ui.patch`, and `0007-sub2api-integration.patch`.
   - Patched Vue files include `frontend/src/components/account/*.vue` (`AccountUsageCell.vue`, `QuotaScriptEditor.vue`, `UpstreamQuotaUsage.vue`, `UsageProgressBar.vue`, `CreateAccountModal.vue`, `EditAccountModal.vue`), `AppSidebar.vue`, and `frontend/src/views/admin/{AccountsView,CodexEvalView}.vue`.
   - Patched TypeScript modules include `frontend/src/api/admin/accounts.ts`, `frontend/src/utils/{accountUsageRefresh,embedded-url}.ts`, `frontend/src/types/index.ts`, `frontend/src/router/index.ts`, and `frontend/src/i18n/locales/{en,zh}/`.
   - **Standalone embedded evaluation web app** (`plugins/codex-candy-eval/patches/0006-evaluation-ui.patch`): Vanilla ES modules (`backend/internal/codexeval/web/*.js`), `ui.html`, `style.css`, and `theme.css` assembled by `web.go`.
2. **Flat frontend test suites**:
   - Native Vue suites live in `plugins/sub2api-quota-extension/tests/test_quota_editor.test.ts` and `test_usage_cell.test.ts`.
   - They use `@vue/test-utils` and `vitest`, and `python3 scripts/build.py` stages them temporarily under downloaded `frontend/src/`.
   - Embedded evaluation UI assertions live in `plugins/codex-candy-eval/tests/test_ui.cjs` and run directly with Node.

### D. References in Parent `.trellis/spec/` to Eval `.trellis/` or `AGENTS.md`

1. Parent `.trellis/spec/` contains **zero references** to `plugins/codex-candy-eval/.trellis/`, `plugins/codex-candy-eval/.claude/`, `plugins/codex-candy-eval/.codex/`, `plugins/codex-candy-eval/.devin/`, or `plugins/codex-candy-eval/AGENTS.md`.
2. Parent `.trellis/spec/` contains **zero rules** requiring dual spec synchronization into `plugins/codex-candy-eval/.trellis/spec/`.
3. The only mention of `plugins/codex-candy-eval/.trellis/` in the parent repository is one historical research note at `.trellis/tasks/archive/2026-11/10-30-inspection-settings-attribution/research/release-recreation.md:67`.
4. Three parent backend spec files link to root `../../../AGENTS.md` for legacy rules that no longer appear in root `AGENTS.md`:
   - `.trellis/spec/backend/directory-structure.md:97`: `Evidence: [repository layout and private configuration](../../../AGENTS.md).`
   - `.trellis/spec/backend/logging-guidelines.md:76`: `Evidence: [private configuration rules](../../../AGENTS.md)...`
   - `.trellis/spec/backend/quality-guidelines.md:88` and `134`: References `AGENTS.md` for 72-character commit body wrapping and imperative subjects.

---

## 5. Related Specs

- `.trellis/spec/backend/index.md`
- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/frontend/index.md`
- `.trellis/spec/guides/index.md`

---

## 6. Caveats and Migration Notes

- **Submodule Git Boundary**: Deleting Trellis and AI files inside `plugins/codex-candy-eval` modifies that submodule repository and updates the submodule gitlink in the parent repository.
- **`.gitattributes` Rule Retention**: `plugins/codex-candy-eval/.gitattributes:12` contains `patches/*.patch -whitespace`. Decide whether to delete `.gitattributes` entirely or keep only line 12.
- **Bootstrap Task Name Collision**: `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/00-bootstrap-guidelines` uses task slug `00-bootstrap-guidelines`, which collides with active parent task `.trellis/tasks/00-bootstrap-guidelines`.
- **Eval Task `10-11-sub2api-runtime-patch` Links**: Moving `10-11-sub2api-runtime-patch` to `.trellis/tasks/archive/2026-10/` keeps historical research files intact, and no active parent spec links to them.
- **Untracked Parent Files**: `.trellis/.template-hashes.json`, `.trellis/workspace/index.md`, and `.trellis/tasks/00-bootstrap-guidelines/` are currently untracked in the parent repository (`git status --short`).
