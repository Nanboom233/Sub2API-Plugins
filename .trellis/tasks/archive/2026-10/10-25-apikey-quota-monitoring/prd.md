# API key account quota monitoring

## Goal

Show upstream Sub2API quota for API-key accounts in the existing account management usage column.
Administrators can inspect and refresh quota without a separate monitoring system.

## Background

The build targets Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.
Initial source research and focused upstream tests are complete.
The user approved the final plan on 2026-10-26. The first implementation and full-scope quality check passed.
The user then requested silent upstream quota failures. The revision passed review and the default combined build.

The billing probe validates the upstream declaration contract. Simple mode returns 404 for that declaration.
Quota access uses the independent `GET /v1/usage` endpoint with Bearer API-key authentication.
No concrete third-party compatible proxy was verified. The synthetic success fixture does not establish one.

- [Rate detection research](./research/upstream-rate-detection.md).
- [API key quota contract](./research/api-key-quota-contract.md).
- [Backend integration](./research/backend-integration.md).
- [Frontend integration](./research/frontend-integration.md).
- [Remaining integration contracts](./research/integration-contracts.md).

## Requirements

- R1. Extend the existing account usage read directly, as requested by the user.
  Reuse single and batch account usage reads and their current refresh paths.
- R2. Query eligible API-key accounts with a configured custom upstream.
  Use the existing key, base URL, proxy, URL policy, header overrides, and TLS settings.
  Keep quota access independent of the billing declaration and its enable switch.
- R3. Map remote key windows, key total quota, subscription windows, and USD balance into `UsageInfo`.
  Reuse existing fields where the meaning matches. Add a field only where no native slot exists.
  Keep zero amounts visible and missing values absent. Upstream quota failures must remain silent in the interface.
  Do not multiply reported amounts by the billing multiplier.
- R4. Show remote quota in the existing account usage column only.
  Keep the frontend diff minimal: reuse existing elements and add no new visual elements.
  Preserve native provider usage, local statistics, initial loading, mobile lazy loading, batching, caching, and manual refresh.
  A remote quota failure must not remove existing local information or add an error message.
  Remove upstream quota error descriptions. Preserve existing native provider error behavior.
- R5. Do not change channel monitor code, validation, snapshots, or views.
- R6. Preserve local account quota counters and existing account scheduling behavior.
  Remote observations must not overwrite those counters or add account stop and recovery actions.
- R7. Deliver an independent submodule plugin named `sub2api-quota-extension` under `plugins/`.
  Use the existing automatic patch build alongside `codex-candy-eval`.
  Patch or test failure must fail the build.
- R8. Keep actual tests and test support in flat `tests/`. Keep `assets/` for data only.
  Reuse native Go and Vue test runtimes. Do not put tests inside production patches or encoded source strings.
- R9. Create no additional product documents or manifests unless the user requests them.
  Trellis artifacts and the required native submodule entry remain within the agreed workflow.

## Acceptance Criteria

- [x] AC1 (R1, R2). Single and batch usage reads retrieve API-key quota even when the billing declaration returns 404.
- [x] AC2 (R3, R4). The usage cell shows remote windows with `UsageProgressBar` and the USD balance with existing styles.
- [x] AC3 (R3, R4). Zero remains visible. Missing values and failed upstream queries add no error text or invalid quota fields.
- [x] AC4 (R4). Eligible API-key rows use existing initial load, mobile lazy load, cache, batch, and manual refresh behavior.
- [x] AC5 (R4, R6). Remote failures retain local statistics, local quota bars, and existing native provider usage and errors.
- [x] AC6 (R5). The extension patches change no channel monitor source file.
- [x] AC7 (R6). Remote reads leave local quota counters and account scheduling unchanged.
- [x] AC8 (R7, R8). The default combined build discovers both plugins and executes their actual tests before publishing outputs.
- [x] AC9 (R8, R9). Test sources stay in flat `tests/`, and the change adds no unsolicited product documents or manifests.

## Out of Scope

Channel monitor changes, new monitoring pages, separate schedulers, additional quota protocols, new user-configured thresholds, and automatic account actions are excluded.
Provider identity verification, database schema migrations, a plugin registry, and an installer redesign are excluded.
Retain the existing installer version warning and confirmation contract.
