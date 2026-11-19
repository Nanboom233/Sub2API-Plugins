# Implementation Plan: Sync codex-candy-eval v0.4.7 and Remove Redundant Designs

## Execution Checklist

Precondition: Do not run `task.py start`, edit production/test/spec files, or dispatch implementation until the user explicitly approves this plan.

1. **Activate task (`Phase 1.4`)**:
   - Run `PYTHONDONTWRITEBYTECODE=1 python3 -B ./.trellis/scripts/task.py start 11-19-eval-upstream-sync-and-debloat` (using session identity if required) after user approval.
2. **Prepare clean `v0.2.23` patch-authoring worktree in `/tmp`**:
   - Clone/copy clean Sub2API `v0.2.23` (`/tmp/eval-sync-sub2api`) into `/tmp/eval-sync-work` and apply `0001..0007` step-by-step with commits per patch (`0001`..`0007`) so each modified patch (`0001`, `0002`, `0004`, `0005`, `0006`) can be cleanly edited, formatted with `gofmt`, and re-exported via `git format-patch` / `git diff --binary` without corrupting hunk headers or mixing patch boundaries!
3. **Update `0001-evaluation-core.patch` and `0002-evaluation-data.patch` (`v0.4.7` detector + core debloat)**:
   - Port upstream `v0.4.7` (`9682e768` in `/tmp/eval-sync-upstream`) detector analysis, 3-lag sequence check, features, calibrated ranker, SHA-256 revision, and init-time binding checks into `backend/internal/codexeval/fingerprint_detector.go` and `fingerprint.go` (preserving `FingerprintModelID`).
   - Delete dead non-checked `runCandy`, `evaluateCandy`, `runFingerprint`, and single-use `start`; rename `runCandyChecked -> runCandy`, `evaluateCandyChecked -> evaluateCandy`, `runFingerprintChecked -> runFingerprint`, and `startChecked -> start`.
   - Embed shared base record metadata across `FingerprintRecord`, `PelicanRecord`, and `SIWCRecord`; remove `siwcRecord.summary()`; change `recordResponse` to take `(kind string, accountID int64, recordID string)` directly.
   - Replace `backend/internal/codexeval/data/lm-detector/{shared_detector.bin,models.json,enrollment-suite.json,LICENSE,README.md}` in `0002-evaluation-data.patch` with upstream `v0.4.7` files (`git diff --binary`).
4. **Update `0004-admin-channel.patch` and `0005-inspection.patch` (bridge & handler debloat)**:
   - In `backend/internal/service/account_codex_eval_service.go`: reuse `apicompat.ResponsesEventToSSE` (`:747, :846`) and `toInt64` (`:992`), and extract concise local helpers for non-2xx error-body restoration, SSE stream headers, and shared Responses-to-Anthropic request preparation.
   - In `backend/internal/codexeval/inspection.go`: update `startChecked` call to `start`.
   - In `backend/internal/handler/admin/codex_inspection_handler.go`: remove pass-through `persistCodexInspectionVerdict` (`:99`), wire `accounts.accountTestService.PersistCodexInspectionVerdict` directly (`:133`), and update `:73` error wording.
5. **Update `0006-evaluation-ui.patch` (`v0.4.7` Fingerprint UI + CSS/JS cleanup + version `0.4.7`)**:
   - Set `pluginVersion = "0.4.7"` in `backend/internal/codexeval/web.go` and wire detector challenge count / license constants cleanly.
   - Align `backend/internal/codexeval/web/fingerprint.js` and matching `web/style.css` rules (`.fingerprint-prediction`, `.fingerprint-summary`, ranking bars, sample blocks, `.detail-note`) with upstream `v0.4.7` while retaining Sub2API account/group target wiring.
   - Remove unused `preference` / `savePreference` in `web/storage.js` and dead `.principle-body` / `.credential .api-key` rules in `web/style.css`.
6. **Re-export patches & update plugin assets, tests, and specs**:
   - Export updated patches (`0001`, `0002`, `0004`, `0005`, `0006`) cleanly into `plugins/codex-candy-eval/patches/`.
   - Replace `plugins/codex-candy-eval/assets/lm-detector-golden.json` with upstream `v0.4.7` `testdata/analyze.json`.
   - Update `plugins/codex-candy-eval/tests/test_codexeval_fingerprint_test.go` (conformance & revision parity), `test_codexeval_inspection_test.go` (shared reset helper + `v0.4.7` attribution compatibility), `test_codexeval_runtime_test.go` / `test_siwc_test.go` (`cpa-siwc-check/0.4.7` & `v0.4.7`), and `tests/test_ui.cjs` (upstream `v0.4.7` Fingerprint summary/bar/detail assertions and `v0.4.7` version).
   - Update `.trellis/spec/backend/runtime-installation.md` (3-lag sequence acceptance rule, `User-Agent: cpa-siwc-check/0.4.7`, and aligned Fingerprint detail view) and `plugins/codex-candy-eval/README.md` / parent `README.md` only if `v0.4.6` version text appears there.
7. **Verification, Browser Visual Check, & Independent Review (`Phase 2.2`)**:
   - Verify standalone `codex-candy-eval` patch application (`git apply --binary` + `git diff --check`) on clean `v0.2.23`.
   - Run full combined build & test gate once:
     ```sh
     UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py
     ```
   - Verify rendered Fingerprint row spacing (`.fingerprint-prediction`) and detail view in headless Chromium (`0` console errors, clean spacing between model ID and percentage).
   - Run `trellis-check` + Coordinator read-only subagent audit (verifying requirements, line-count reduction on code patches, error order, async timing, ASD-STE100 specs, and build timestamps) and write `check-v0.4.7-debloat.md`.
   - Stop before `git commit` (`Phase 3.4` gate).

## Validation Commands

```sh
# Standalone patch check
git apply --check --binary plugins/codex-candy-eval/patches/*.patch

# Combined v0.2.23 build + all Go/Vue/CJS/builder/installer suites
UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py
```

## Rollback Point

- `plugins/codex-candy-eval` clean Git `HEAD` (`4301252`) and parent `Sub2API-Plugins` clean Git `HEAD` (`8f809b2`) provide instant zero-loss `git checkout` rollback if any hunk or test regresses.
