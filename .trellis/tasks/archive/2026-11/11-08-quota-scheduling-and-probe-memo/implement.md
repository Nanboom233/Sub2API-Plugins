# Implementation Plan: Sub2API v0.2.23 Adaptation, Model-Control Defaults, and Final Verification

## Active Execution Checklist

Precondition: Do not edit production, test, workflow, README, or spec files until the user explicitly approves this updated plan.

1. **Snapshot current `v0.2.21` staged diffs for rollback**:
   - Save staged diffs from parent, `plugins/sub2api-quota-extension`, and `plugins/codex-candy-eval` to `/tmp/sub2api-v0.2.21-rollback-*.patch` before editing.
2. **Rebase `plugins/sub2api-quota-extension` onto `v0.2.23`**:
   - Apply `quota-extension.patch` onto a temporary copy of `/tmp/sub2api-v0.2.23-research` and resolve the two rejected hunks (`backend/go.mod` Hunk #4 context around `github.com/google/pprof` and `AccountUsageCell.vue` Hunk #3 `formatDateTime` import).
   - Update `loadActiveUsage` in `frontend/src/components/account/AccountUsageCell.vue` to capture `const config = apiKeyUsageRefreshKey.value` before the active request and store `{ data: result, ts: Date.now(), config }` in `_usageCache.set`.
   - Add `APIKeyQuotaBalanceExhaustedExtraKey: {}` to `duplicateAccountDiscardedExtraKeys` in `backend/internal/service/admin_account.go` so all 13 managed keys match.
   - Re-export clean `git diff` against `v0.2.23` to `plugins/sub2api-quota-extension/patches/quota-extension.patch`.
   - Update `plugins/sub2api-quota-extension/.github/workflows/build.yml` (`default: v0.2.23` at line `11`, `go-version: "1.27.4"` at line `73`).
3. **Update `plugins/codex-candy-eval` for `v0.2.23` and `gpt-6.2-sol` model-control default**:
   - Append `"gpt-6.2-sol"` to the 5-item default array (keeping `"gpt-6.1-terra"`) in `plugins/codex-candy-eval/patches/0005-inspection.patch:941` (`["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra", "gpt-6.2-sol"]`).
   - Append `"gpt-6.2-sol"` to the expected default arrays in `plugins/codex-candy-eval/tests/test_service_codex_inspection_settings_test.go:105` and `plugins/codex-candy-eval/tests/test_ui.cjs:19`.
   - Update `plugins/codex-candy-eval/.github/workflows/build.yml` (`default: v0.2.23` at line `11`, `go-version: "1.27.4"` at line `73`).
   - Update fallback executable names in `plugins/codex-candy-eval/tests/native_inspection_fixture.py:48-51` from `v0.2.21` to `v0.2.23`.
4. **Update parent delivery files and active backend specifications**:
   - Update `.github/workflows/build.yml` (`default: v0.2.23` at line `11`, `go-version: "1.27.4"` at line `73`) and `README.md` (`v0.2.21` to `v0.2.23` across all 11 active references).
   - Append `gpt-6.2-sol` to the `degraded_remove_models` default row in `.trellis/spec/backend/native-inspection.md:58`.
   - Update `.trellis/spec/backend/{index.md,api-key-quota.md,runtime-installation.md,quality-guidelines.md,minimal-linux-delivery.md}` from `v0.2.21` to `v0.2.23` (and `minimal-linux-delivery.md:77` embedded `VERSION` note from `0.2.20` to `0.2.22`).
5. **Run verification and independent read-only audit**:
   - Verify standalone patch application (`git apply --binary` and `git diff --check`) for `codex-candy-eval` and `sub2api-quota-extension` separately on clean `v0.2.23` copies.
   - Run the full combined build and test entry once via `hc`:
     ```sh
     UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py
     ```
     This runs `pnpm install --frozen-lockfile`, `check:i18n`, `vue-tsc --noEmit`, `vite build`, quota Go/Vue suites, evaluation Go/UI suites (including the updated 6-item `degraded_remove_models` default assertions), `go vet`, common builder/installer suites, and compiles all 10 `v0.2.23` executables into `dist/build/`.
   - Verify `dist/build/darwin-arm64/sub2api-plugins-v0.2.23-darwin-arm64 -version` outputs `Sub2API 0.2.23`.
   - Run an independent read-only audit across staged diffs, specs, requirements, and build timestamps, and record results in `check-v0.2.23.md`.
6. **Stage verified files and stop at Commit Gate (Phase 3.4)**:
   - Stage only the verified work paths in `plugins/sub2api-quota-extension` (5 files), `plugins/codex-candy-eval` (11 files, adding `tests/test_service_codex_inspection_settings_test.go`), and parent `Sub2API-Plugins` (11 files).
   - Update `commit-plan.md` and present the exact commit plan for user approval. Do not run `git commit`, `git push`, or deployment commands without explicit approval.

## Validation Commands

```sh
# Standalone patch cleanliness checks against /tmp/sub2api-v0.2.23-research
git apply --check --binary plugins/codex-candy-eval/patches/*.patch
git apply --check --binary plugins/sub2api-quota-extension/patches/quota-extension.patch

# Combined v0.2.23 test + five-platform build gate
UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py

# Binary version check
"./dist/build/darwin-arm64/sub2api-plugins-v0.2.23-darwin-arm64" -version
```

## Rollback Point

- Restore `/tmp/sub2api-v0.2.21-rollback-*.patch` if any `v0.2.23` check regresses and requires design revision.
- Move temporary `/tmp/sub2api-v0.2.23-*` scratch trees to Trash and remove any temporary Python caches after verification completes.
