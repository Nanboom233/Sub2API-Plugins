# v0.4.7 implementation check

## Line counts

| Patch | Before | After | Change |
| --- | ---: | ---: | ---: |
| 0001-evaluation-core.patch | 2448 | 2403 | -45 |
| 0002-evaluation-data.patch | 76365 | 85382 | +9017 |
| 0004-admin-channel.patch | 1194 | 1158 | -36 |
| 0005-inspection.patch | 1554 | 1550 | -4 |
| 0006-evaluation-ui.patch | 2944 | 2980 | +36 |

The four code patches have 49 fewer lines. The upstream detector data accounts for the data patch growth.

Applied source paths use `backend/internal/` as their root.

| File | Before | After | Change |
| --- | ---: | ---: | ---: |
| codexeval/candy.go | 113 | 104 | -9 |
| codexeval/fingerprint.go | 272 | 232 | -40 |
| codexeval/fingerprint_detector.go | 695 | 712 | +17 |
| codexeval/pelican.go | 136 | 127 | -9 |
| codexeval/siwc.go | 134 | 121 | -13 |
| codexeval/runtime.go | 278 | 287 | +9 |
| codexeval/state.go | 213 | 213 | 0 |
| codexeval/inspection.go | 829 | 829 | 0 |
| codexeval/web.go | 93 | 93 | 0 |
| service/account_codex_eval_service.go | 1006 | 970 | -36 |
| handler/admin/codex_inspection_handler.go | 181 | 177 | -4 |
| codexeval/web/fingerprint.js | 63 | 90 | +27 |
| codexeval/web/storage.js | 17 | 10 | -7 |
| codexeval/web/style.css | 454 | 470 | +16 |
| tests/test_codexeval_fingerprint_test.go | 94 | 176 | +82 |
| tests/test_codexeval_inspection_test.go | 795 | 779 | -16 |
| tests/test_ui.cjs | 1210 | 1225 | +15 |
| tests/test_service_account_codex_eval_service_test.go | 377 | 377 | 0 |

## Patch and test checks

- The micro-polish removed the Go `fingerprintModelID` wrapper and the unused Anthropic request return value.
- The updated 0001 and 0004 patches match their generated diffs. Each patch passed the standalone application check after this change.
- Each of the seven patches passed `git apply --check --binary` and `git apply --binary` on clean Sub2API v0.2.23.
- Patch 0003 emitted three existing vendor whitespace warnings. Patches 0003 and 0007 have no changes.
- `git diff --check` passed in the parent, plugin, and applied source trees.
- `SUB2API_ASSETS=<plugin>/assets go test -tags=unit -failfast ./internal/codexeval` passed in 1.818 seconds.
- `SUB2API_ASSETS=<plugin>/assets go test -tags=unit -failfast -run '^TestFingerprint' ./internal/codexeval` passed in 0.475 seconds.
- `go test -tags=unit -failfast -run '^(TestCodex|TestSendCodex|TestAccountCodex|Test.*Codex|TestInspection)' ./internal/service ./internal/handler/admin` passed. It covered 16 service tests and two admin tests.
- `node plugins/codex-candy-eval/tests/test_ui.cjs /tmp/eval-sync-work` passed.
- The five detector data files and the golden fixture match upstream bytes. The binary has 5,232,052 bytes. The metadata `built_at` is `2026-11-17T19:37:59.839365+00:00`.
- The modified text files use LF line endings. The workspace scan found no `__pycache__` or `._*` files. The removed checked wrappers and old version references were absent.

## Browser check

Playwright Chromium rendered the patched HTML, CSS, and JavaScript with simulated v0.4.7 results. The console and page each reported zero errors. The model label and probability had an 8 px gap. Three summary cards, three ranking bars, and three sample details were visible. The dialog had no horizontal overflow. The `not_model` three-lag note was visible. The preview did not run the full page icon initialization.

## Combined build

After the micro-polish, `PYTHONDONTWRITEBYTECODE=1 UPSTREAM_TAG=v0.2.23 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_TERMINAL_PROMPT=0 GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=credential.helper GIT_CONFIG_VALUE_0= python3 -B scripts/build.py` exited 0.

The Go, Vue, CJS, builder, and installer checks passed. The frontend i18n check passed three tests. The quota Vitest suite passed nine tests. The builder suite passed four tests. Go vet passed.

The build wrote these files under `dist/build/`. Times use UTC+08:00 on 2026-11-19.

| File | Time |
| --- | --- |
| linux-amd64/sub2api-plugins-installer-v0.2.23-linux-amd64 | 12:00:30 |
| linux-amd64/sub2api-plugins-v0.2.23-linux-amd64 | 12:00:30 |
| linux-arm64/sub2api-plugins-installer-v0.2.23-linux-arm64 | 12:00:30 |
| linux-arm64/sub2api-plugins-v0.2.23-linux-arm64 | 12:00:30 |
| darwin-amd64/sub2api-plugins-installer-v0.2.23-darwin-amd64 | 12:00:30 |
| darwin-amd64/sub2api-plugins-v0.2.23-darwin-amd64 | 12:00:30 |
| darwin-arm64/sub2api-plugins-installer-v0.2.23-darwin-arm64 | 12:00:30 |
| darwin-arm64/sub2api-plugins-v0.2.23-darwin-arm64 | 12:00:30 |
| windows-amd64/sub2api-plugins-installer-v0.2.23-windows-amd64.exe | 12:00:30 |
| windows-amd64/sub2api-plugins-v0.2.23-windows-amd64.exe | 12:00:30 |

All ten files are newer than the two updated patches.

## Git state

The parent has a modified runtime installation spec and a modified `codex-candy-eval` submodule. The task directory and `.vscode/` are untracked. The eval submodule has five modified patches, the golden fixture, and four test files. The quota extension and plugin template submodules have no changes. No Git commit was made.

## Temporary paths

Keep `/tmp/eval-sync-sub2api` and `/tmp/eval-sync-upstream` for the coordinator. The former contains earlier applied patches and is not a clean source tree. The standalone patch check used a clean v0.2.23 source copy.

The authoring tree, standalone copy, patch order file, evidence file, and browser screenshot went to the trash.
