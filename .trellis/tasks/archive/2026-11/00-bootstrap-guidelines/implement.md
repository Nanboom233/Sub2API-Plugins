# Implementation Plan: Bootstrap Guidelines and Migrate Eval Trellis Artifacts

## Ordered Execution Checklist

1. **Migrate Eval Historical Task Archives (`R1`)**:
   - Copy `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/10-11-sub2api-runtime-patch`, `10-18-inspection-controls`, `10-18-inspection-verdict-state`, `10-19-inspection-model-control`, `10-19-upstream-compare-adaptation`, and `10-19-upstream-evaluation-sync` into `.trellis/tasks/archive/2026-10/`.
   - Copy `plugins/codex-candy-eval/.trellis/tasks/archive/2026-10/00-bootstrap-guidelines` to `.trellis/tasks/archive/2026-10/10-11-eval-bootstrap-guidelines` and update its `task.json` `id` and `name` fields to `"eval-bootstrap-guidelines"`.
2. **Migrate Eval Historical Workspace Journals (`R2`)**:
   - Copy `plugins/codex-candy-eval/.trellis/workspace/codex-candy-eval-plugin/` (`index.md` and `journal-1.md`) to `.trellis/workspace/codex-candy-eval-plugin/`.
3. **Update Stale `AGENTS.md` Links in Parent Backend Specs (`R3`)**:
   - Update `.trellis/spec/backend/directory-structure.md:97`, `.trellis/spec/backend/logging-guidelines.md:76`, and `.trellis/spec/backend/quality-guidelines.md:88,134` so they reference `.gitignore` and `.trellis/spec/` instead of removed `AGENTS.md` prose.
4. **Populate Parent Frontend Specifications (`R4`)**:
   - Rewrite `.trellis/spec/frontend/index.md`, `directory-structure.md`, `component-guidelines.md`, `hook-guidelines.md`, `state-management.md`, `type-safety.md`, and `quality-guidelines.md` with source-backed rules and examples from `plugins/sub2api-quota-extension` and `plugins/codex-candy-eval`.
5. **Restore `plugins/codex-candy-eval` to Native Plugin Structure (`R5`)**:
   - Remove `.trellis/`, `.claude/`, `.codex/`, `.devin/`, `AGENTS.md`, and `.gitattributes` from `plugins/codex-candy-eval`.
   - Update `plugins/codex-candy-eval/.gitignore` to match `plugins/sub2api-plugin-template/.gitignore`.
6. **Update Task Status in `prd.md`**:
   - Mark completed checklists in `.trellis/tasks/00-bootstrap-guidelines/prd.md`.

## Validation Commands

```bash
# 1. Verify archived tasks in 2026-10 and absence of slug collisions
python3 ./.trellis/scripts/task.py list-archive 2026-10

# 2. Verify migrated workspace journal files
cmp -s .trellis/workspace/codex-candy-eval-plugin/index.md .trellis/workspace/codex-candy-eval-plugin/index.md
test -f .trellis/workspace/codex-candy-eval-plugin/journal-1.md

# 3. Verify zero placeholders remain across all parent specs
! rg -i "To be filled|TODO: fill" .trellis/spec/

# 4. Verify plugins/codex-candy-eval tracked files and .gitignore alignment
cmp -s plugins/codex-candy-eval/.gitignore plugins/sub2api-plugin-template/.gitignore
git -C plugins/codex-candy-eval status --short

# 5. Verify whitespace and diff formatting
git -C plugins/codex-candy-eval diff --check
git diff --check
```

## Review Gates and Rollback Points

- **Subagent Implementation & Review Gate**: `trellis-implement` executes steps 1-6; `trellis-check` independently verifies AC1-AC5 and all validation commands.
- **Commit & Push Gate**: Both the `plugins/codex-candy-eval` submodule commit and the parent `Sub2API-Plugins` commit require explicit user approval before `git commit` or `git push`.
