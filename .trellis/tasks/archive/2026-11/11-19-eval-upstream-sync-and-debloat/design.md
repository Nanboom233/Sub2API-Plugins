# Technical Design: Sync codex-candy-eval v0.4.7 and Remove Redundant Designs

## 1. Architecture and Package Boundaries

Keep the established Sub2API `v0.2.23` seven-patch ownership in `plugins/codex-candy-eval/patches/`:
- `0001-evaluation-core.patch`: `backend/internal/codexeval/` runners, history state, and `v0.4.7` fingerprint detector.
- `0002-evaluation-data.patch`: `backend/internal/codexeval/data/` (`codex_context.json` and `lm-detector/{shared_detector.bin,models.json,enrollment-suite.json,LICENSE,README.md}`).
- `0003-vendor-assets.patch`: unchanged byte-identical vendor scripts/fonts.
- `0004-admin-channel.patch`: `AccountTestService` multi-provider evaluation bridge and admin evaluation HTTP handler.
- `0005-inspection.patch`: native background Candy/Fingerprint inspection coordinator, narrow conditional persistence, and admin inspection handler.
- `0006-evaluation-ui.patch`: `web.go` (`pluginVersion = "0.4.7"`) and embedded evaluation web UI (`ui.html`, `style.css`, `fingerprint.js`, `storage.js`, etc.).
- `0007-sub2api-integration.patch`: unchanged route registration, account extra preservation, and Vue `/admin/codex-eval` iframe route.

Per `.trellis/spec/backend/directory-structure.md:107-119`, keep all `v0.4.7` detector code inside `package codexeval` (`fingerprint.go` and `fingerprint_detector.go`) rather than creating a separate `internal/fingerprint` subpackage. Export only symbols required by sibling packages (`FingerprintModelID`, `Attribution` / record fields serialized to JSON or read by `service`/`handler` tests).

## 2. Upstream `v0.4.7` Fingerprint Sync Design

1. **Detector Engine (`0001-evaluation-core.patch`, `fingerprint_detector.go` & `fingerprint.go`)**:
   - Port upstream `v0.4.7` (`9682e768`) reply preparation (`<= 64,000` bytes, `[1, 355]` integer extraction, `max(80, ceil(expected * 0.55))` length gate, truncation to expected length), 3-lag sequence check (`sequenceShape`: lag-1 autocorrelation, small-step share, and lags 1..3 nearby-pair thresholds), feature extraction (Hellinger value shares, ordered blocks, position kernels, lag/transition/window-coverage features), and multi-signal ranker (LDA + nearest-reference + baseline + positional + sequential scores with calibrated softmax when all 3 challenges are valid).
   - Validate embedded `shared_detector.bin`, `models.json`, and `enrollment-suite.json` bindings and compute the SHA-256 `detectorRevision` label during initialization.
   - Simplify `fingerprint.go` collector/worker flow to match upstream `v0.4.7` (`collectedFingerprint` storing prepared reply + usage, eliminating the legacy inline number parser and intermediate `fingerprintOutput` struct).
2. **Detector Assets & Conformance Fixture (`0002-evaluation-data.patch`, `assets/`, `tests/`)**:
   - Update `0002-evaluation-data.patch` with upstream `v0.4.7` `shared_detector.bin` (`5,232,052` bytes, Git binary hunk), `models.json`, `enrollment-suite.json`, `LICENSE`, and `README.md`.
   - Replace `plugins/codex-candy-eval/assets/lm-detector-golden.json` with upstream `v0.4.7` `internal/fingerprint/testdata/analyze.json` (`1,905` lines) and update `tests/test_codexeval_fingerprint_test.go` to verify exact rankings, scores, calibrated probabilities, diagnostics, reply preparation, and revision parity.
3. **Fingerprint UI & Version (`0006-evaluation-ui.patch`)**:
   - Port upstream `v0.4.7` `internal/plugin/web/fingerprint.js` rendering (3-card `.fingerprint-summary`, probability ranking bars, sample `<details>` blocks, and `.detail-note` 3-lag adjacent-pair note for `not_model`), keeping Sub2API's native `fp-` credential/group/target wiring.
   - Sync upstream `v0.4.7` `style.css` rules for `.fingerprint-prediction`, `.fingerprint-summary`, `.fingerprint-rank*`, `.fingerprint-sample*`, and `.detail-note` so row model labels and percentages render with proper spacing.
   - Set `pluginVersion = "0.4.7"` in `web.go` (updating the page footer and `SIWC` `User-Agent: cpa-siwc-check/0.4.7`), and expose detector challenge count and MIT license text cleanly in `web.go`.

## 3. Redundancy and Bloat Removal Design

| Patch / File | Change | Contract Preservation |
| --- | --- | --- |
| `0001`: `candy.go`, `fingerprint.go`, `runtime.go`, `0005`: `inspection.go` | Remove dead non-checked `runCandy`, `evaluateCandy`, `runFingerprint`, and single-use `start`. Rename `runCandyChecked -> runCandy`, `evaluateCandyChecked -> evaluateCandy`, `runFingerprintChecked -> runFingerprint`, and `startChecked -> start`; update callers in `runtime.go` and `inspection.go`. | Public `Start(...)` signature and pre-send inspection participation hook behavior remain identical. |
| `0001`: `runtime.go`, `state.go` | Change `recordResponse(kind string, query url.Values)` to `recordResponse(kind string, accountID int64, recordID string)` and call directly from `Record(...)`, dropping `net/url` from `runtime.go`/`state.go` if unused. | Exact `{type, fingerprint\|pelican\|siwc}` JSON payload and HTTP status codes (`200`/`400`/`404`) remain unchanged. |
| `0001`: `siwc.go`, `pelican.go`, `fingerprint.go`, `state.go`, `runtime.go` | Embed shared `recordMeta` (`ID`, `RunID`, `CreatedAt`, `Model`, `Status`, `Error`, `DurationMS`, token fields) in `FingerprintRecord`, `PelicanRecord`, and `SIWCRecord` (matching upstream `state.go:49`). Delete `siwcRecord.summary()` and copy `SIWC` slice safely without a per-item identity helper. | Exact JSON keys, `schema_version: 3` `history.json` compatibility, and `Candy` legacy format remain unchanged. |
| `0004`: `account_codex_eval_service.go` | Replace manual SSE marshaling at `:747, :846` with `apicompat.ResponsesEventToSSE`; replace custom `int64FromAny` at `:992` with package-native `toInt64`; extract concise local helpers for non-2xx error-body restoration, SSE stream response headers, and shared Responses-to-Anthropic request preparation (`:483, :594`). | Keep all three pull-based stream readers, raw status propagation, cancellation, usage extraction, and Handler/Service HTTP `400` validation intact. |
| `0005`: `codex_inspection_handler.go` | Delete 1-line `persistCodexInspectionVerdict` wrapper at `:99` and assign `PersistVerdict: accounts.accountTestService.PersistCodexInspectionVerdict` directly at `:133`; fix `:73` error text from `"Candy inspection"` to `"Codex evaluation inspection"`. | Narrow conditional `UpdateCodexInspectionState` and error behavior remain identical. |
| `0006`: `web/storage.js`, `web/style.css` | Delete unused `preference` and `savePreference` from `storage.js:11-18`; delete dead `.principle-body` (`style.css:174-177`) and `.credential .api-key` (`style.css:222-223`) rules. | Existing object-keyed `localStorage` preferences across all tabs remain intact. |
| `tests/test_codexeval_inspection_test.go` | Extract one `resetInspectionTestState(t)` helper replacing the 6 repeated global reset blocks. | All inspection confirmation, recovery, wildcard, opt-out, and write-order assertions remain intact. |

## 4. Compatibility and Rollback

- Keep `plugins/sub2api-quota-extension` and `plugins/sub2api-plugin-template` untouched unless combined build verification surfaces a shared-file issue (none expected because `0007` and `admin_account.go` are unchanged).
- Snapshot `git -C plugins/codex-candy-eval status` / `HEAD` (`4301252`) before edits; apply and edit against clean `/tmp/eval-sync-sub2api` (`v0.2.23`) and `/tmp/eval-sync-upstream` (`v0.4.7`), then re-export clean `git diff --binary` patches per patch boundary (`0001`, `0002`, `0004`, `0005`, `0006`).
