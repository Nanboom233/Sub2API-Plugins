# Custom API-key quota scripts

## Goal

Let administrators configure a custom quota query script for an API-key account through the existing quota plugin.
Use cc-switch only as the reference for the script authoring and query experience.

## Background

The current plugin reads upstream `GET /v1/usage` and renders native quota fields in account management.
It targets Sub2API v0.2.19.
The backend has no JavaScript interpreter. The installer deploys static Go executables.

Sources:

- [cc-switch script contract](./research/cc-switch-quota-scripts.md).
- [Local integration](./research/local-integration.md).
- [Script runtime](./research/script-runtime.md).
- [v0.2.19 default quota research](./research/default-quota-v0219.md).
- [v0.2.19 subscription anchor research](./research/default-subscription-v0219.md).

## Requirements

- R1. Extend `plugins/sub2api-quota-extension` with per-account custom quota scripts for API-key accounts.
  Store only script text. Nonblank text selects the custom query. Clearing it restores default detection.
  Cover all API-key platforms, including accounts that currently use dedicated native quota cells.
- R2. Use cc-switch's configure, edit, test, and save interaction as the reference.
  Both create and edit forms provide the inline test action.
  Test current unsaved code against the form's effective connection settings.
  For edits, apply draft connection changes to the saved account settings. For new accounts, use the form draft.
  Show the result or error inside the editor.
  Testing must not save the account or replace the account list's usage cache.
  Saving requires no successful remote test.
- R3. A configured script is that account's remote quota source. An absent script retains the existing detection paths.
  Return an object with optional `session`, `day`, `week`, `month`, `total`, and `balance` fields.
  Balances support an optional unit, with `USD` as the default.
  Each quota window supplies used and limit amounts. Period keys select the native display slots.

  Keep the native inline countdown and show its reported reset date and time through the native hover tooltip.
  Apply this to both the previous task's default detector and custom-script results, including inline previews.
  For default subscriptions, read `weekly_window_start` and `expires_at` from the existing upstream response.
  The user accepts direct addition: calculate the weekly reset as `weekly_window_start + 7 days`.
  Use key expiry and subscription expiry as account expiration inputs. Save the earlier available date to native account expiration.
  One reported expiry supplies the date. No reported expiry leaves the saved account expiration unchanged.
  Subscription expiry is not a monthly quota reset. Keep the monthly quota bar without a fabricated reset date.
  Explain the simplified weekly addition in a code comment. Keep missing source timestamps absent.
  Do not infer custom-script reset dates from period labels.
  Compute percentages and reset countdowns in the application.

  Use the existing usage column, native progress bars, single/batch reads, cache, mobile loading, and manual refresh.
  Preserve the default detector's USD balance display.
  Apply a saved script change to that row without waiting for an old cached result to expire.
- R4. Custom-script failures appear in the account usage cell and after manual tests.
  Default-query failures remain silent. Use the existing error field instead of adding another error structure.
  Keep local usage and quota counters intact. Synchronize native account expiry without adding another account scheduling policy.
  Preserve native provider behavior for accounts without a custom script.
  A script failure must not trigger an automatic query through another quota source.
- R5. Preserve automatic plugin discovery and the existing build and installer flow.
  Deliver script execution inside the existing server binary without a target-side runtime installation.
- R6. Keep tests and test support in flat `tests/`. Add only checks needed for changed behavior.
- R7. Add no unsolicited product documentation or manifests. Trellis-managed artifacts remain permitted.
- R8. Use local evidence and anonymous public sources. GitHub credential use requires separate explicit approval.

## Acceptance Criteria

- [x] AC1 (R1). Create and edit forms save, reload, and clear one script string without losing other account settings.
- [x] AC2 (R1, R3). Single/batch reads display reported periods, native countdowns with reset date/time tooltips, total quota, and balance units.
  Default detection, custom scripts, and inline previews share the period display through existing desktop/mobile refresh paths.
  Default subscriptions use the approved timestamp calculation. Periods without usable source timestamps retain no countdown.
- [x] AC6 (R3). Default detection saves the earlier available key/subscription expiry to native account expiration.
  Missing expiry data preserves the saved expiration. Subscription expiry does not populate the monthly reset time.
- [x] AC3 (R3, R4). Custom failures display errors and preserve local information. Default-query failures stay silent. Neither triggers a fallback query.
- [x] AC4 (R2). Both forms test the current script against effective draft connection settings and show the result or error inside the editor.
  The test changes neither stored configuration nor the account list's cached usage.
- [x] AC5 (R5, R6). The default combined build runs focused tests and produces the server and installer for the updated candidate.

## Out of Scope

cc-switch script compatibility, multiple script languages, template catalogs, and new pages are excluded.
Enable switches and separate language or timeout settings are excluded.
Separate schedulers, automatic account actions beyond native expiry synchronization, channel monitor changes, and installer redesign are excluded.
