# Implementation Result

## Delivered Files

- `scripts/build.py` downloads Sub2API v0.2.18 and discovers all plugin submodules through `.gitmodules`.
- `plugins/codex-candy-eval` uses origin `https://github.com/Nanboom233/codex-candy-eval` at revision `146408053efcd443679bfdc4ce89b8c27e0acbb0`.
- Plugin patches 0004 and 0007 now use contextual existing-file edits. Patch order uses lexical filenames without `series`.
- Actual backend assertions live in plugin `tests/test_*_test.go` files, with explicit native package annotations.
- The actual UI suite lives in plugin `tests/test_ui.cjs`. The shared installer suite lives in parent `tests/test_installer_test.go`.
- Flat `tests/support.py` supplies native grouping and temporary package context in each independent repository.
- Only golden JSON remains under plugin `assets/lm-detector-golden.json`. Test cases and support code remain under flat `tests/`.
- Manual container fixtures use plugin `tests/native_*` paths, outside `test_*` automatic discovery.
- `scripts/installer/main.go` preserves the installation transaction and uses advisory executable-version checks.
- Root `LICENSE` and original third-party license files reach namespaced installer resources without a separate summary document.
- README files and release workflows describe the v0.2.18 build.

The plugin retains its standalone `--source` and `--check` entry and compatibility installer copy.
Standalone checks execute backend and UI suites and compile the installer. The parent owns the single installer transaction suite.

## Current Native Test Integration on 2026-10-25

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/build.py
```

The native integration build returned zero and refreshed both outputs. Its log is `/tmp/sub2api-native-tests.2lIzJP/build.log`.
Native Go groups passed in their original admin, codexeval, and service packages, with private upstream helpers available.
Each group ran only its discovered test names, once, with fail-fast behavior. Direct Node UI assertions passed.
Pipeline fixtures proved native grouping, private-helper access, unrelated-test exclusion, legacy Go execution, CJS discovery, and failure propagation.
The native installer suite passed against the temporary installer module. No wrapper suites or tests under `assets/` remain.

The final orchestration change retains integration vet coverage after native source tests.
The completed build had already removed its temporary source, so focused validation used the same patched v0.2.18 revision.
Source revision: `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.

```sh
go vet ./internal/server ./internal/server/routes ./internal/web
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_build.py
```

Both commands passed. Logs are `/tmp/sub2api-native-tests.2lIzJP/vet.log` and `/tmp/sub2api-native-tests.2lIzJP/pipeline-tests.log`.
The vet source is `/tmp/sub2api-native-tests.2lIzJP/vet-source` with the current seven production patches.
The focused validation required no second frontend, server, or installer build.

## Historical Integrated Build on 2026-10-24

Command:

```sh
python3 scripts/build.py
```

The successful invocation returned zero. Its original log was `/tmp/sub2api-plugin-migration.JWNmkh/build.log`.
It completed automatic shallow source download, all seven patches, frozen dependency installation, and the combined frontend build.
The frontend's existing i18n checks passed. Its TypeScript check and Vite build passed.
Focused Go tests passed for `internal/codexeval`, `internal/service`, and `internal/handler/admin`.
The existing focused vet command and evaluation page checks passed.
The shared build tests passed for two-plugin cooperation, mixed test entry execution, license collection, and failure propagation.
Installer tests passed for the existing transaction and the new parser, probe, warning, confirmation, and cancellation behavior.
No production container installation occurred.

Outputs:

- `dist/build/sub2api-plugins`
- `dist/build/sub2api-plugins-installer`

`file` identified both outputs as static Linux/amd64 ELF executables.
`go version -m` identified Go 1.27.3, Linux/amd64, and CGO disabled.
The build supplied canonical `0.2.18` through linker flags to the server and installer.

## Resolved Build Failure

The first invocation reached installer tests but failed because test-package linker injection left the test version empty.
The test fixture now reads `SUB2API_BUILD_VERSION`, which the build sets from its canonical version.
Production binaries still use linker injection.
The failed invocation published no outputs and removed its temporary workspace.
The second invocation passed and produced both outputs.

## Delivery State

The user approved the updated commit plan on 2026-10-25.
Parent commit `6b3d8b6` contains portable Trellis integration. Plugin commit `9a56c08` contains the migration and test refactor.
Parent commit `1afe676` contains the common build and records plugin revision `9a56c08`.
All three work commits use the configured signing policy, and signature verification passed.
The user removed the root README. It is absent from the work commits.
Remote checkout reproduction requires publication of the plugin commit. No push or container installation occurred.
The original checkout remains unchanged.

## Historical Partial Notice Cleanup on 2026-10-25

Removed the duplicate root `licenses/THIRD_PARTY_NOTICES.txt` through macOS Trash.
Removed own-license and build instructions from the plugin notice. Retained component attribution, source URLs, and included-license references.
Backend assets and product source did not change.

The user subsequently required deletion of the remaining plugin notice. This partial cleanup does not describe the final license inventory.

Reused `dist/build/sub2api-plugins` with `prepare_installer` and `discover_plugins` from `scripts/build.py`.
Temporary module metadata used Go 1.27.3 from the successful server build.
The affected existing assertion passed with `SUB2API_BUILD_VERSION=0.2.18` and `GOFLAGS=-mod=readonly`:

```sh
go test -run '^TestEntryAndEmbeddedPayload$' .
go build -trimpath '-ldflags=-s -w -X main.buildVersion=0.2.18' -o /tmp/sub2api-notice-refresh.QyLNpA/sub2api-plugins-installer .
```

The build used `GOOS=linux`, `GOARCH=amd64`, and `CGO_ENABLED=0`.
Replaced only `dist/build/sub2api-plugins-installer` after success. Reused the prior frontend, server, and transaction evidence.

## Final Notice Removal on 2026-10-25

Removed the remaining plugin `licenses/THIRD_PARTY_NOTICES.txt` through macOS Trash.
Both migrated repositories now use original license files without a separate summary document.
The plugin root `LICENSE` and its three original third-party license files remain unchanged.
Updated the README, active task contracts, specs, and commit inventory.

Reused `dist/build/sub2api-plugins` and staged the current license inventory with `prepare_installer`.
The existing `TestEntryAndEmbeddedPayload` passed against that inventory.
Rebuilt the Linux/amd64 installer with canonical version `0.2.18`, then refreshed `dist/build/sub2api-plugins-installer`.
The log is `/tmp/sub2api-original-licenses.wtzsIn/refresh.log`.
This packaging change required no frontend or server rebuild.
