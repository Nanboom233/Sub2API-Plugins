# Child Task Research & Planning Brief: Adapt Plugins to Sub2API v0.2.24

Target task: `.trellis/tasks/11-21-adapt-sub2api-v0224` (parent: `11-20-gemini-thought-signature-rectifier`, status: `planning`)
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any internal subagent from running `hc send`.

## Scope & Hard Boundaries

- **Phase 1 Research + Planning ONLY**:
  - Do **NOT** run `task.py start`.
  - Do **NOT** edit any plugin patch, production/test code, `.trellis/spec/`, `.gitmodules`, or Git state.
  - Do **NOT** run `gh` or any authenticated Git/GitHub operations (unauthenticated public fetches only).
  - Use `PYTHONDONTWRITEBYTECODE=1 python3 -B` for any Python command; create zero new `.pyc` files.
  - Strictly apply user's anti-bloat rule: **no redundant fallbacks, no speculation, no redundant compatibility shims** (and per `.trellis/spec/backend/quality-guidelines.md:60`, no multi-version compatibility adapters).

## Deliverables

### 1. Upstream `v0.2.23...v0.2.24` Audit (`research/v0224-upstream-diff.md`)
Using unauthenticated public GitHub API / `v0.2.23` vs `v0.2.24` (`5af9afb588c4b014b3df9db7d4073af1f8ae01b6` → `5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`) source comparison:
1. List all upstream commits and changed files in `v0.2.23...v0.2.24` that intersect ANY file patched by:
   - `plugins/sub2api-quota-extension/patches/quota-extension.patch`
   - `plugins/codex-candy-eval/patches/*.patch`
   - `plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch`
2. Diagnose the exact two `git apply` failures observed in `/tmp/gemini-single-shot-build.log`:
   - `frontend/src/components/account/AccountUsageCell.vue` (around line 769)
   - `frontend/src/views/admin/AccountsView.vue` (around line 531)
   Record exact before/after upstream context and whether upstream changed behavior, props, reactivity, styling, or only nearby lines.
3. Check for **silent semantic/compile/type/test drift** across ALL three plugins on `v0.2.24` (even where `git apply` succeeded):
   - Did `v0.2.24` change any Gemini native forwarding / rectifier / thought signature logic (e.g., PR #1309 or related)?
   - Did `v0.2.24` change any Go symbol/signature, frontend type, i18n key, Vue component contract, or Vite/pnpm/Go toolchain version?
   - Does `sub2api-quota-extension` need any test updates (`test_usage_cell.test.ts`, `test_quota_editor.test.ts`, Go tests) or README baseline updates?
   - Do `.trellis/spec/` baseline mentions (`v0.2.23`) need synchronization in Phase 3.3?
4. Note whether UI visual layout in `AccountUsageCell.vue` / `AccountsView.vue` changes on `v0.2.24`, so we know whether a Playwright Chromium visual check applies in Phase 2.2.

### 2. Lean Planning Artifacts (under `.trellis/tasks/11-21-adapt-sub2api-v0224/`)
Follow `.trellis/spec/backend/index.md#documentation-rules` (concise active-voice English, short sentences, no semicolons or contractions, real citations):
1. **`prd.md`**: Requirements, exact plugin scope (touch ONLY plugins actually affected by `v0.2.24`), explicit dependency on parent task (`11-20-gemini-thought-signature-rectifier`'s uncommitted `plugins/gemini-signature-rectifier` & `.gitmodules` in the combined build), constraints, and testable acceptance criteria.
2. **`design.md`**: Exact file-by-file adaptation hunks for `v0.2.24`, preserving `.trellis/spec/backend/api-key-quota.md` and frontend specs with zero redundant fallbacks or multi-version shims.
3. **`implement.md`**: Ordered checklist, focused verification, clean argument-free `scripts/build.py` (which selects `v0.2.24` automatically) + affected plugin standalone `UPSTREAM_TAG=v0.2.24` build, and Phase 2.2 real-browser check if UI rendering changed.
4. **`implement.jsonl` and `check.jsonl`**: Curated relevant `.trellis/spec/` entries + `.trellis/tasks/11-21-adapt-sub2api-v0224/research/v0224-upstream-diff.md` (delete seed `_example` rows, verify valid JSON and existing file paths).

## Final Callback

Report concisely via `hc send t53` with:
- Summary of upstream `v0.2.23...v0.2.24` changes intersecting each of the 3 plugins.
- Exact conflict cause in `AccountUsageCell.vue` and `AccountsView.vue`, plus any semantic/compile drift found (or confirmed zero drift) in `eval` and `gemini-signature-rectifier`.
- Whether UI layout changed (determining Playwright check scope).
- Confirmation that `prd.md`, `design.md`, `implement.md`, `implement.jsonl`, `check.jsonl`, and `research/v0224-upstream-diff.md` are ready and verified, and zero production/test/Git changes occurred.
