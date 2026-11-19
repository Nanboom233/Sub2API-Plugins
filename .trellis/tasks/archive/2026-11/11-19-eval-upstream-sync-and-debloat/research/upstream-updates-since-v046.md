# Research: Upstream Updates Since v0.4.6

- Query: Inspect `haowang02/cpa-plugin-codex-candy-eval` after commit `0ae33b626aa27a191fd91731230521e90656c8b4`.
- Scope: Mixed. Inspect the public upstream Git history and map changes to the Sub2API patches.
- Date: 2026-11-19

## Baseline and exact history

The clone used isolated Git configuration and disabled credential helpers. Commit `0ae33b6` is tag `v0.4.6`.

| Ref | Commit or tag object | Date | Result |
| --- | --- | --- | --- |
| `v0.4.6` | commit `0ae33b626aa27a191fd91731230521e90656c8b4` | 2026-11-06 00:59 +0800 | Baseline. `pluginVersion` is `0.4.6`. |
| main | commit `86d832c58f85f33e0cff91368fae1cb1012899f8` | 2026-11-08 16:44 +0800 | Documentation and badge workflow only. No release tag. `pluginVersion` stays `0.4.6`. |
| main, `v0.4.7` | commit `9682e76812c035e523a748620bba00c55c5970cb` | 2026-11-18 14:41 +0800 | Fingerprint detector update. `pluginVersion` becomes `0.4.7`. |

Tag `v0.4.7` is annotated object `644cd842e116fcdbf3d08a81c3e8e2901a45d6d6` and points to commit `9682e76812c035e523a748620bba00c55c5970cb`.
The current `main` and `origin/main` point to that commit. No `v0.4.8` or later tag exists.
The `origin/badges` ref contains commit `8874759fe8f41fe07300c217704dc790c26238fa`, but that commit is not reachable from current `HEAD`.
The reachable history after `v0.4.6` therefore contains exactly two commits.

## Commit `86d832c58f85f33e0cff91368fae1cb1012899f8`

The commit changed two paths, with 81 insertions and five deletions.

| Upstream path | Change | Sub2API effect |
| --- | --- | --- |
| `.github/workflows/download-badge.yml` | Adds a scheduled workflow. It counts release archive downloads with `gh`, renders `badge/downloads.json`, and force-pushes the `badges` branch. | Do not copy it into a plugin patch or the Sub2API build. It needs GitHub workflow write permission and it is unrelated to runtime evaluation. Parent CI already owns build and release workflows. |
| `README.md` | Centers the heading, adds release, download, platform, and license badges, and keeps the CPA installation and usage text. | Do not copy the CPA installation commands or its badge workflow into the Sub2API plugin. A Sub2API README can update feature and version statements, but it must retain the repository license and build instructions. |

This commit changes no Go code, data, prompt, algorithm, embedded page, SIWC behavior, inspection behavior, history schema, or vendor asset.

## Commit `9682e76812c035e523a748620bba00c55c5970cb` (`v0.4.7`)

The commit changes 23 paths, with 2,924 insertions and 3,850 deletions.
It refreshes fingerprint scoring and moves the detector into a package.
It does not change Candy, Code, Pelican, SIWC, history persistence, inspection policy, or vendor libraries.

The complete changed-path inventory is:

- `AGENTS.md`
- `internal/fingerprint/analysis.go`
- `internal/fingerprint/analysis_test.go`
- `internal/fingerprint/data.go`
- `internal/fingerprint/data/LICENSE`
- `internal/fingerprint/data/README.md`
- `internal/fingerprint/data/enrollment-suite.json`
- `internal/fingerprint/data/models.json`
- `internal/fingerprint/data/shared_detector.bin`
- `internal/fingerprint/features.go`
- `internal/fingerprint/ranker.go`
- `internal/fingerprint/testdata/analyze.json`
- `internal/plugin/data/lm-detector/LICENSE` (rename source)
- `internal/plugin/data/lm-detector/README.md` (deleted)
- `internal/plugin/data/lm-detector/enrollment-suite.json` (rename source)
- `internal/plugin/data/lm-detector/models.json` (rename source)
- `internal/plugin/data/lm-detector/shared_detector.bin` (deleted source)
- `internal/plugin/fingerprint.go`
- `internal/plugin/fingerprint_detector.go` (deleted)
- `internal/plugin/fingerprint_test.go`
- `internal/plugin/inspection_test.go`
- `internal/plugin/plugin.go`
- `internal/plugin/plugin_test.go`
- `internal/plugin/testdata/lm-detector-golden.json` (deleted)
- `internal/plugin/ui.go`
- `internal/plugin/web/fingerprint.js`

### New fingerprint package

The new `internal/fingerprint` package separates data parsing, feature extraction, ranking, and public result types.

| Upstream path | Lines | Finding |
| --- | ---: | --- |
| `internal/fingerprint/analysis.go:13-183` | 183 | Adds `Reply`, diagnostics, attribution types, number preparation, and `Analyze`. `sequenceShape` now checks adjacent pairs at lags one through three. It marks a sequence as model-like with autocorrelation, small-step, or nearby-pair thresholds at lines 138-169. |
| `internal/fingerprint/features.go:8-170` | 170 | Adds Hellinger value shares, ordered blocks, position kernels, lag features, transitions, and window coverage. |
| `internal/fingerprint/ranker.go:8-218` | 218 | Combines LDA, nearest-reference, baseline, positional, and sequential scores. It applies calibrated softmax when all three challenges are valid. |
| `internal/fingerprint/data.go:13-196` | 196 | Embeds the detector binary, model metadata, enrollment suite, and MIT license. It exposes `Revision` as a SHA-256 label and `ChallengeCount = 3` at lines 23-25. It validates detector, model, and calibration bindings during package initialization at lines 131-181. |
| `internal/fingerprint/analysis_test.go:12-77` | 77 | Adds conformance tests for `testdata/analyze.json` and reply preparation. |
| `internal/fingerprint/testdata/analyze.json` | 1,905 | Adds detector conformance cases with expected rankings, scores, probabilities, and diagnostics. |

The new detector uses a 5,232,052-byte `shared_detector.bin`.
The v0.4.6 detector was 4,667,588 bytes.
The larger bank and updated `models.json` provide the new reference and calibration data.

### Data moves and replacements

The commit renames these paths from `internal/plugin/data/lm-detector/` to `internal/fingerprint/data/`:

- `LICENSE` remains the MIT license. The new package embeds it as `fingerprint.License`.
- `enrollment-suite.json` keeps the 36 challenge records.
- `models.json` changes 64 lines and removes eight lines. Its `built_at` changes from `2026-10-27T05:02:50.758637+00:00` to `2026-11-17T19:37:59.839365+00:00`.

The commit replaces `shared_detector.bin`, adds `internal/fingerprint/data/README.md`, deletes the old data README, and deletes the old golden fixture.
The new data README pins the source bank to `Ikaleio/lm-detector` commit `33fb43f26670be0ed7817ab13e5c4c4731ccb76a`.

### Runtime and record changes

`internal/plugin/fingerprint.go:1-186` now imports `internal/fingerprint` and uses its `Challenge`, `Reply`, `Attribution`, `Challenges`, `Prepare`, and `Analyze` APIs.
The run still uses three challenges and six global slots, but it obtains the count and detector revision from the package at lines 78-88.
The collector stores a parsed reply and usage in `collectedFingerprint` at lines 160-185.
The worker increments progress under the shared mutex and analyzes replies after all workers finish at lines 107-157.
The record stores `fingerprint.Revision` and `*fingerprint.Attribution` at lines 44-50 and 91-105.

The new collector preserves an empty parsed reply for invalid output, rejects text over 64,000 bytes, and records the parsed count from `fingerprint.Prepare` at lines 167-185.
This removes the old inline parser and old `fingerprintOutput` conversion.

### Test and UI changes

`internal/plugin/fingerprint_test.go` removes the old 2,867-line golden parity fixture and inline parser tests.
It uses repeated numeric answers for run tests and checks package revisions and complete history equality at lines 39-76.
`internal/plugin/inspection_test.go:38-40` and `internal/plugin/plugin_test.go:75-78` use `fingerprint.Attribution` and `fingerprint.License`.
`internal/plugin/ui.go:67-93` uses `fingerprint.ChallengeCount`, `fingerprint.License`, and the package attribution map when embedding the page.
`internal/plugin/web/fingerprint.js:31` changes the not-model detail text.
`internal/plugin/web/fingerprint.js:65-68` explains adjacent-number scoring and the new three-lag check.
`internal/plugin/plugin.go:15-22` changes `pluginVersion` from `0.4.6` to `0.4.7`.
The release workflow checks that value through `.github/workflows/release.yml:21`.

## Mapping to the Sub2API adaptation

The current plugin submodule commit `4301252` targets Sub2API v0.2.23 and keeps the v0.4.6 detector layout.
The relevant patch anchors are `0001-evaluation-core.patch:369-1347`, `0002-evaluation-data.patch:1-75574`, `0006-evaluation-ui.patch:1-99`, and `tests/test_codexeval_fingerprint_test.go:15-94`.

| Upstream v0.4.7 change | Current Sub2API owner | Required adaptation | Conflict or reason |
| --- | --- | --- | --- |
| New `internal/fingerprint` package and public result types | `patches/0001-evaluation-core.patch:369-1347` | Port the package under the patched Sub2API evaluation tree, or keep equivalent code in `codexeval` only if the package boundary would break the host module. Update imports to the Sub2API module path. Replace inline detector types and calls with one owner. | The upstream import path `cpa-codex-candy-eval/internal/fingerprint` cannot be copied unchanged into the Sub2API module. The patch must keep `codexeval` package contracts used by `0004` and `0005`. |
| New feature and ranker implementation | `patches/0001-evaluation-core.patch:647-1347` | Replace `fingerprint_detector.go` and its inline `analyzeFingerprint` implementation with the package implementation. Preserve exported `FingerprintModelID` because the inspection patch and native coordinator use it. | The algorithm is behaviorally significant. A partial copy can produce different verdicts, rankings, or detector revisions. |
| New detector data and package paths | `patches/0002-evaluation-data.patch:1-75574` | Replace the old 4,667,588-byte binary, updated models, and enrollment data. Add the package data README and MIT license. Move embedded paths from `data/lm-detector` to the selected package path. | The binary, models, and calibration must stay matched. Keep the Sub2API patch data owner instead of adding files to a user checkout. |
| New conformance fixture | `plugins/codex-candy-eval/assets/lm-detector-golden.json` and `tests/test_codexeval_fingerprint_test.go:15-94` | Replace the old golden fixture with `analyze.json` and call the new package API. Keep focused run, retry, cancellation, and history tests. | The old fixture validates the old algorithm. Keeping it after the port gives false parity confidence. |
| Detector revision and license embedding | `0001-evaluation-core.patch:673-682` and `0006-evaluation-ui.patch:72-82` | Expose the new package revision and license through the existing page and record JSON. Update `web.go` to use the package challenge count and license. | Retain the LGPL footer and Sub2API page embedding. Do not expose raw detector internals or credentials. |
| UI wording | `0006-evaluation-ui.patch:1348-1416` | Update the embedded fingerprint detail text and keep existing Sub2API selectors, inspection placement, and SIWC controls. | The wording change is safe. The surrounding UI is a Sub2API adaptation and must not be replaced by the CPA page wholesale. |
| Version | `0006-evaluation-ui.patch:16` and current `web.go` constant | Update the page version for the upstream release. Keep the specified SIWC header until the contract changes. | The current code builds the SIWC `User-Agent` from `pluginVersion`. The active runtime contract specifies `cpa-siwc-check/0.4.6`. Separate these values or obtain a contract decision before changing the header. |
| CPA documentation and workflow | `.github/workflows/download-badge.yml`, upstream `README.md` | Do not import CPA workflow, `gh` credentials, release badge branch, or CPA `auth_files` and `providers.js` instructions. Update only Sub2API feature/version documentation when the planning decision requires it. | Sub2API uses native groups, accounts, transports, and patch delivery. The upstream workflow needs write permission that the plugin build does not have. |

### Features unchanged after v0.4.6

The diff has no changes to `internal/plugin/candy.go`, `codex.go`, `model.go`, `pelican.go`, `siwc.go`, `state.go`, `inspection.go`, or their web modules.
It has no changes to prompts, response conversion, SIWC classification, history schema v3, account controls, inspection implementation, or vendor assets.
The Sub2API bridge in `0004-admin-channel.patch`, native inspection in `0005-inspection.patch`, and integration routes in `0007-sub2api-integration.patch` need no upstream v0.4.7 merge for those features.

## Recommended next action

Treat `v0.4.7` as one focused fingerprint detector sync, not a broad plugin rewrite.
Port the detector package and matched data first, then update the fingerprint tests and page version.
Run the existing Sub2API adapter and inspection tests after the port because detector types and revisions cross those boundaries.
Keep the native multi-provider sender, SIWC rate-limit policy, native inspection coordinator, iframe route, and LGPL footer unchanged.

## Caveats / Not Found

- The upstream clone used current `main` and fetched all tags. The reachable range after `v0.4.6` contains two commits.
- The `origin/badges` commit is a separate badge-only branch and is not part of current `HEAD`.
- This report did not apply Sub2API patches or modify plugin code. The exact patch application and redundancy audit belong to the companion research file.
