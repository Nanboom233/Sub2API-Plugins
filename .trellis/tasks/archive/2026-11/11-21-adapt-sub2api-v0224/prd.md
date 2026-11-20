# Adapt the quota plugin to Sub2API v0.2.24

Restore the default combined build after upstream account usage refresh changes.
Phase 1 covers research and planning. Phase 2 requires separate approval.
Evidence: [upstream audit](research/v0224-upstream-diff.md). Parent: `11-20-gemini-thought-signature-rectifier`.

## Requirements

- **R1:** Adapt only `plugins/sub2api-quota-extension`. Keep eval, Gemini, template, and common build code unchanged.
- **R2:** Adapt the two Vue targets and their shared refresh utility against `v0.2.24` commit `5c2982a81b46e2142d0143d2f83c1ce9c4da1d24`.
- **R3:** Preserve native Claude/Gemini snapshot refresh and the existing OpenAI/Grok behavior.
- **R4:** Preserve API-key configuration invalidation, redacted-key updates, response ownership, cache lifetime, batching, lazy loading, and manual refresh.
- **R5:** Extend upstream `buildAccountUsageRefreshKey` for API-key configuration. Use its single `refreshKey` throughout both caches and asynchronous checks.
- **R6:** Preserve native estimated costs, reset tooltips, local data, zero balances, and custom-script error display.
- **R7:** Keep the quota script, persistence, scheduling, transport, and editor contracts unchanged.
- **R8:** Verify the affected plugin standalone and the default combined build against `v0.2.24` after approval.

## Parent dependency and limits

The combined build includes the parent's uncommitted `plugins/gemini-signature-rectifier` and path-only `.gitmodules` entry.
Keep both available and unchanged. The child does not create, publish, commit, or re-register that plugin.
The build must include all three production plugins through existing discovery.

Add no fallback query, dependency, version adapter, compatibility shim, or replacement build framework.
Do not change backend or editor tests without a demonstrated adaptation failure.
Do not run `task.py start`, product tests, builds, or browser checks during Phase 1.
Do not change plugin patches, code, tests, specs, Git state, or credentials during Phase 1.

## Acceptance criteria

- **AC1:** The quota patch applies cleanly to pristine `v0.2.24` alone and after eval/Gemini patches.
- **AC2:** Both caches retain upstream `{ data, ts, refreshKey }`. No parallel configuration key, computed value, map, watcher, or helper export remains.
- **AC3:** Claude/Gemini native snapshot changes refresh without forcing reads. Claude uses the native passive source.
- **AC4:** Script, connection, and saved-key changes invalidate only the affected account and reject obsolete single/batch responses.
- **AC5:** Unchanged keys reuse cached usage. One unified watcher refreshes changed accounts once and preserves native non-API-key routing.
- **AC6:** Existing quota, eval, and Gemini suites, i18n, TypeScript, Vite, vet, and common checks pass in the combined build.
- **AC7:** The argument-free combined build selects `v0.2.24`. The quota standalone build also passes with `UPSTREAM_TAG=v0.2.24`.
- **AC8:** Both builds publish ten executables. Record their exact paths, sizes, timestamps, selected tag, and exits.
- **AC9:** Chromium confirms native cost text and quota rows remain readable in both locales and themes, without overflow or runtime errors.
- **AC10:** Temporary workspaces, staged tests, browser processes, and task-created Python caches are removed after verification.
