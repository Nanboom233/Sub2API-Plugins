# Sync codex-candy-eval Upstream v0.4.7 and Remove Redundant Designs

## Goal

Synchronize `plugins/codex-candy-eval` on Sub2API `v0.2.23` with upstream `haowang02/cpa-plugin-codex-candy-eval` `v0.4.7` (`9682e76812c035e523a748620bba00c55c5970cb`), align the Fingerprint page layout with upstream `v0.4.7`, and remove confirmed dead wrappers, pass-through methods, duplicate bridge helpers, and unused CPA styles without breaking Sub2API contracts.

## Confirmed Facts

- Upstream `v0.4.7` (`9682e76812c035e523a748620bba00c55c5970cb`, `2026-11-18`) is the sole functional release after `v0.4.6` (`0ae33b6`; `86d832c5` touches only CPA badge workflows and README badges). See [upstream updates since v0.4.6](./research/upstream-updates-since-v046.md).
- `v0.4.7` replaces the LM fingerprint detector scoring algorithm (Hellinger value shares, ordered blocks, position kernels, 3-lag adjacent-pair sequence check, LDA + nearest-reference + baseline + positional + sequential ranker with calibrated softmax, and init-time SHA-256 revision/binding validation), updates `shared_detector.bin` (`4,667,588` to `5,232,052` bytes, `Ikaleio/lm-detector` `33fb43f2`) and `models.json` (`2026-11-17T19:37:59Z`), replaces `lm-detector-golden.json` with `analyze.json` (`1,905` lines), updates `web/fingerprint.js` layout and 3-lag copy, and bumps `pluginVersion` from `"0.4.6"` to `"0.4.7"` (`User-Agent: cpa-siwc-check/0.4.7`).
- `.trellis/spec/backend/directory-structure.md:107-119` keeps detector Go code inside `backend/internal/codexeval/` (`fingerprint.go` and `fingerprint_detector.go`), detector assets under `codexeval/data/lm-detector/` in `0002-evaluation-data.patch`, and the conformance fixture at `plugins/codex-candy-eval/assets/lm-detector-golden.json`.
- Line-by-line comparison across `patches/0001..0007` and `tests/` against upstream `v0.4.7` and clean Sub2API `v0.2.23` established 13 safe redundancies and verified that handler/service dual validation (`HTTP 400` vs `500`), persisted `Candy` history fields (`ok`/`error`/`skipped`), existing `localStorage` preference keys, and Sub2API native multi-provider/inspection contracts must remain intact. See [redundancy and divergence audit](./research/redundancy-and-divergence-audit.md).

## Requirements

1. **Upstream `v0.4.7` detector and asset sync (`0001`, `0002`, `assets/`, `tests/`)**:
   - Port the complete `v0.4.7` fingerprint detector algorithm (reply preparation, 3-lag sequence shape check, feature extraction, calibrated multi-signal ranker, SHA-256 `Revision`, `ChallengeCount = 3`, and init-time data/calibration validation) inside `backend/internal/codexeval` (`fingerprint.go` and `fingerprint_detector.go`), keeping `FingerprintModelID` exported for `inspection.go` and unexporting internal detector types where external packages do not need them.
   - Update `0002-evaluation-data.patch` (`backend/internal/codexeval/data/lm-detector/`) with the `v0.4.7` `5,232,052`-byte `shared_detector.bin`, updated `models.json`, `enrollment-suite.json`, `LICENSE`, and `README.md`.
   - Replace `plugins/codex-candy-eval/assets/lm-detector-golden.json` with upstream `v0.4.7` `testdata/analyze.json` and update `tests/test_codexeval_fingerprint_test.go` to verify full conformance parity (rankings, scores, calibrated probabilities, diagnostics, reply preparation, and revision).
2. **Upstream `v0.4.7` Fingerprint UI alignment and version bump (`0006`, `tests/`, specs)**:
   - Align `backend/internal/codexeval/web/fingerprint.js` and matching `web/style.css` rules (`.fingerprint-prediction`, `.fingerprint-summary`, ranking bars, sample blocks, `.detail-note`) with upstream `v0.4.7` while retaining Sub2API's native account/group target wiring.
   - Update `pluginVersion` in `backend/internal/codexeval/web.go` to `"0.4.7"` (updating both the embedded page footer and `SIWC` `User-Agent: cpa-siwc-check/0.4.7`).
3. **Canonical `*Checked` renaming and dead-wrapper removal (`0001`, `0005`)**:
   - Delete unused non-checked wrappers (`runCandy` and `evaluateCandy` at `candy.go:47, :77`, `runFingerprint` at `fingerprint.go:131`, and single-use `start` at `runtime.go:88`).
   - Rename `runCandyChecked -> runCandy`, `evaluateCandyChecked -> evaluateCandy`, `runFingerprintChecked -> runFingerprint`, and `startChecked -> start`, and update all callers in `candy.go`, `fingerprint.go`, `runtime.go`, and `inspection.go`.
4. **Core, handler, CSS/JS, and record debloat (`0001`, `0005`, `0006`)**:
   - Remove the pass-through `persistCodexInspectionVerdict` method in `handler/admin/codex_inspection_handler.go:99` (wiring `accounts.accountTestService.PersistCodexInspectionVerdict` directly at `:133`) and update the `:73` error message to cover Candy/Fingerprint inspection.
   - Replace synthetic `url.Values` query packing/unpacking between `runtime.go:233` (`Record`) and `state.go:161` (`recordResponse`) with direct `(kind string, accountID int64, recordID string)` parameters.
   - Remove no-op `siwc.go:28` `summary()` and its copy loop in `runtime.go:227` while preserving lock and JSON serialization safety.
   - Embed one shared base record struct across `FingerprintRecord`, `PelicanRecord`, and `SIWCRecord` (matching upstream `state.go:49` while preserving exact JSON keys and schema v3 `history.json` compatibility; keep `Candy` unchanged).
   - Delete unused `preference` and `savePreference` in `web/storage.js:11, :15`, and delete dead CPA `.principle-body` (`web/style.css:174-177`) and `.credential .api-key` (`web/style.css:222-223`) rules.
5. **Service bridge and test deduplication (`0004`, `tests/`)**:
   - Reuse Sub2API native `apicompat.ResponsesEventToSSE` at `service/account_codex_eval_service.go:747, :846` and native `toInt64` (`scheduler_snapshot_service.go:1763`) instead of local `int64FromAny` at `:992`.
   - Consolidate duplicated non-2xx error-body restoration, SSE response header setup, and Responses-to-Anthropic request preparation across provider branches in `service/account_codex_eval_service.go` without altering HTTP `400`/`500` error boundaries, stream flushing, or cancellation.
   - Consolidate the six repeated global-state reset blocks in `tests/test_codexeval_inspection_test.go` into one test helper.
6. **Specification synchronization**:
   - Update `.trellis/spec/backend/runtime-installation.md` (and any affected frontend/backend spec anchors) to reflect the `v0.4.7` detector 3-lag sequence rule, `User-Agent: cpa-siwc-check/0.4.7`, and aligned Fingerprint UI.

## Acceptance Criteria

- [ ] `plugins/codex-candy-eval` ports the complete upstream `v0.4.7` detector algorithm and `5,232,052`-byte `shared_detector.bin` + `models.json` inside `codexeval`, passing all `analyze.json` conformance assertions in `test_codexeval_fingerprint_test.go`.
- [ ] `web/fingerprint.js` and `web/style.css` match upstream `v0.4.7`'s 3-card summary, probability bars, `.fingerprint-prediction` row spacing, and `.detail-note` 3-lag diagnostics, `pluginVersion` is `"0.4.7"` (`cpa-siwc-check/0.4.7`), and `node tests/test_ui.cjs` passes.
- [ ] `runCandy`, `evaluateCandy`, `runFingerprint`, and `start` replace all `*Checked` suffixes with zero dead wrapper functions remaining; `storage.js` unused preference helpers, `codex_inspection_handler.go` pass-through method, `url.Values` record plumbing, `siwc` no-op summary loop, dead `.principle-body`/`.api-key` CSS, and duplicate `ResponsesEventToSSE`/`toInt64`/stream-setup helpers in `account_codex_eval_service.go` are removed or consolidated.
- [ ] Standalone `codex-candy-eval` patches (`0001..0007`) and combined `codex-candy-eval` + `sub2api-quota-extension` patches apply cleanly to Sub2API `v0.2.23` with zero rejected hunks.
- [ ] `UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py` exits with status `0` with all Go, Vue, CJS, builder, and installer suites passing and all 10 `v0.2.23` binaries built cleanly.

## Out of Scope

- Importing upstream `.github/workflows/download-badge.yml`, CPA `auth_files` / `providers.js` / `host.js`, or CPA README badges.
- Splitting detector files into a separate Go subpackage outside `backend/internal/codexeval`.
- Changing persisted `Candy` history fields (`ok`/`error`/`skipped`), existing browser `localStorage` preference keys, or Handler/Service HTTP `400` validation boundaries.
- Executing `git commit`, `git push`, or live deployments without separate explicit user approval.
