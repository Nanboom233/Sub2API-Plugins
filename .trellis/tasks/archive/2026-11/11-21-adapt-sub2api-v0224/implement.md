# Adaptation implementation plan

Goal: restore quota composition on `v0.2.24` while retaining native snapshot and quota configuration invalidation.
Use [design.md](design.md) and the [upstream audit](research/v0224-upstream-diff.md).
Phase 1 stops after planning validation. Implementation requires separate approval.

## 1. Prepare the approved candidate

- [ ] Inspect current changes and preserve the parent's uncommitted Gemini plugin and `.gitmodules` dependency.
- [ ] Download pristine public `v0.2.24` source into a temporary workspace without GitHub credentials.
- [ ] Extend upstream `buildAccountUsageRefreshKey` with the deterministic API-key configuration branch.
- [ ] Remove the standalone API-key helper, parallel computed values, configuration fields/maps, and extra invalidation watchers.
- [ ] Rebase both Vue targets onto upstream's single `refreshKey` caches and captured keys.
- [ ] Add current-key checks to single and batch response ownership. Retain native batch request tokens for same-key ordering.
- [ ] Preserve upstream native utility, cost display, warning, backend, and locale changes.
- [ ] Extend `test_usage_cell.test.ts` and add flat `test_usage_batch.test.ts` for the changed contract.
- [ ] Verify changed-key success/error rejection, old-cache misses, same-key request ordering, native passive refresh, and one API-key refresh.
- [ ] Export the existing quota patch and check whitespace and forward application against pristine `v0.2.24`.
- [ ] Record actual hunk/addition/removal counts against the audited 21-hunk, 110-changed-line baseline for the three refresh targets.
- [ ] Check composition after eval and Gemini patches without changing those plugins.

Do not add a version shim, fallback query, dependency, new build path, or unrelated test cleanup.
Keep editor and Go suites unchanged unless their established entry reports a concrete adaptation failure.

## 2. Build through established entries

Use `PYTHONDONTWRITEBYTECODE=1` and `python3 -B` for every Python invocation.
Use only unauthenticated public source access. Keep code and suite inputs fixed while builds run.
The default entries already execute focused suites. Do not repeat passing suites as another gate.

From `plugins/sub2api-quota-extension`, run the standalone build:

```sh
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 UPSTREAM_TAG=v0.2.24 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
```

From `/Users/minami/Code/S/Sub2API-Plugins`, run one clean argument-free combined build:

```sh
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
```

- [ ] Confirm `UPSTREAM_TAG`, `SUB2API_BUILD_STAGE`, `SUB2API_BUILD_WORKSPACE`, and `SUB2API_BUILD_PLATFORMS` are unset for the combined entry.
- [ ] Record the automatically selected tag and resolved source commit. Acceptance targets `v0.2.24`.
- [ ] Verify all three plugins participate and all established focused suites execute.
- [ ] Record i18n, `vue-tsc`, Vite, Go tests, vet, Python build tests, and installer test results.
- [ ] Verify both builds publish five program/installer pairs. Record all exact paths, sizes, timestamps, and exits.

If automatic release selection changes, report that fact. Do not silently pin the combined command or claim `v0.2.24` acceptance.
If a build fails, repair only the demonstrated in-scope cause before another attempt.

## 3. Inspect the actual account UI

- [ ] Use the final combined executable's embedded frontend for the Chromium check. Do not rebuild an independent UI preview.
- [ ] Start the host-platform combined program in setup mode on loopback with a temporary working directory.
- [ ] Check `GET /setup/status` readiness. Intercept browser APIs with synthetic authentication and account data.
- [ ] Open the accounts table at 1440×900 and scale 2 in en/zh and light/dark.
- [ ] Inspect Claude 5h/7d statistics and estimated costs alongside custom API-key bars, zero balance, and reset tooltips.
- [ ] Exercise snapshot refresh, saved-configuration refresh, and the native repeated-token-refresh warning.
- [ ] Record readable screenshots, zero console/page errors, and zero horizontal overflow.
- [ ] Stop the program and Chromium. Remove temporary runtime files and task-created caches. Keep screenshots and evidence under `/tmp`.

The default build removes its source workspace automatically.
Use the final executable's existing setup-mode and port configuration. Do not change the build script to retain temporary assets.
The host program serves the same embedded frontend that the combined build produced.
The [audit](research/v0224-upstream-diff.md#browser-entry-without-another-frontend-build) records the actual setup-server owners.
On this Darwin arm64 host, use a new empty temporary directory with this command after the build succeeds:

```sh
hc run --bg --name v0224-browser --cwd /tmp/sub2api-v0224-browser env AUTO_SETUP=false SKIP_SETUP=false DATA_DIR=/tmp/sub2api-v0224-browser/data SERVER_HOST=127.0.0.1 SERVER_PORT=4180 /Users/minami/Code/S/Sub2API-Plugins/dist/build/darwin-arm64/sub2api-plugins-v0.2.24-darwin-arm64
```

Create the temporary directory first. Do not pass `--setup` or submit setup APIs.

## 4. Handoff and later specification synchronization

- [ ] Compare the final changes with all requirements and include actual failures or unrun required checks in the evidence.
- [ ] Report build/browser evidence and any blocker through `hc send t53` from the main session only.
- [ ] In Phase 3.3, update baseline statements and replace obsolete separate-key examples with the verified upstream unified helper and cache shape.
- [ ] Keep historical references and unchanged workflow input defaults accurate.

Do not create commits, publish repositories, push, or use GitHub credentials without separate authorization.
