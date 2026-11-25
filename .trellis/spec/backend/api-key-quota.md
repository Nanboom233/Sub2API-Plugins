# API Key Account Usage

## 1. Scope / Trigger

The `sub2api-quota-extension` plugin adds default upstream quota detection and custom JavaScript queries on Sub2API v0.2.25.
Both paths use the existing account-management usage column for API-key accounts.
Both paths synchronize account scheduling state from reported balance and window utilization.
Default detection also synchronizes native account expiration and shares unsupported probe memoization with billing probes.
Default detection failures remain silent. Custom-script errors appear in the usage cell and inline test output.
Accounts without a custom script retain native provider results and errors.

Owner: [production patch](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch).

## 2. Signatures

Administrator routes use the `/api/v1` prefix:

```text
GET  /admin/accounts/:id/usage
POST /admin/accounts/usage/batch
POST /admin/accounts/quota-script/test
```

Default detection requests upstream `GET /v1/usage` with the configured account key and Bearer authentication.
Custom execution uses:

```go
func (s *AccountUsageService) ExecuteQuotaScript(
    ctx context.Context, account *Account, script string,
) (*UsageInfo, error)
```

Keep existing constructor callers usable. Supply shared transport and config through the production provider and generated Wire caller.

`UpdateAPIKeyQuotaState` owns conditional quota persistence on the account repository.
Pass the existing usage result, optional expiration, and optional unsupported-probe identity directly.
Merge reported sources with the locked current row. Update the caller's account only after the transaction commits.
Identity and script edits clear quota pauses within the native account update transaction.
Do not add scheduling fields to frontend DTOs or `AccountBulkUpdate`.

```go
UpdateAPIKeyQuotaState(context.Context, *Account, *UsageInfo, *time.Time, *string) (bool, error)
```

## 3. Contracts

### Default detection

Map upstream amounts into the native usage response:

| Upstream data | Native field |
| --- | --- |
| Key 5h window | `five_hour` |
| Key 1d window or subscription daily | Optional `one_day` |
| Key 7d window or subscription weekly | `seven_day` |
| Subscription monthly | `thirty_day` |
| Key total quota | Optional `quota_total` |
| Wallet balance or key remaining, USD | Optional `balance` |
| Default query failure | No quota fields or user-visible quota error description |

Create progress only when reported used and a positive limit are available. Calculate utilization as `used / limit * 100`.
Rate-only windows do not require top-level `remaining` or `unit`.
Keep zero amounts present and omitted amounts absent. Ignore the subscription `remaining: -1` sentinel and plan names.
Do not multiply reported amounts again. Key remaining does not expose the underlying wallet balance.
Subscription `remaining` summarizes the smallest remaining period allowance. Keep the three period bars instead of adding a wallet balance.

For default subscription weekly progress, use reported `weekly_window_start + 7 * 24 hours` as `ResetsAt`.
The user accepts this simplified calculation. Explain the omitted native legacy-anchor correction in a code comment.
Use the existing countdown calculation. Keep a missing weekly start absent.
Read key-level and nested subscription `expires_at`. Select the earlier available timestamp and save it to native account expiration.
Use the one reported timestamp when the other is absent. If neither is present, preserve saved expiration.
Do not use subscription expiry as monthly `ResetsAt`. Keep daily and monthly reset unknown without their source anchors.
Preserve native expiration settings and past-time behavior. Add no separate disable policy or scheduler.
Save expiration, quota keys, and cooldowns atomically through `UpdateAPIKeyQuotaState` with identity, proxy, and script compare-and-swap.
Keep scheduler outbox and snapshot synchronization when scheduling state changes. Skip writes when persisted state is unchanged.
Update `updated_at` from `UpdateAPIKeyQuotaState` only when `expires_at` changes so usage refresh keys stay stable.
Keep decoder expiry internal. Add no usage response field or extra frontend request.
The existing account-expiry column reflects persistence on the next native account-list refresh.

Default detection reads custom API-key targets independently of the billing probe's switch or result.
Reuse official-domain and adaptive-target selection. Preserve native Gemini, Antigravity, and Grok results and errors.
Forward `forceProbe` to native Antigravity usage queries. Retain upstream manual-query controls and account rows during refresh.
Malformed nonempty URLs must reach URL validation rather than the official-target shortcut.

Reuse `upstreamBillingProbeIdentity(account)` for shared probe memoization across `GET /v1/usage` and `GET /v1/sub2api/billing`.
Save its SHA-256 digest in `accounts.extra.apikey_usage_unsupported_identity` after HTTP 404, 405, 501, non-OpenAI official domains, or invalid 2xx bodies.
Skip automatic `GET /v1/usage` and scheduled `GET /v1/sub2api/billing` requests when the saved identity matches.
Allow manual usage refreshes and manual billing probes to run even when memoized.
Do not memoize transport errors, read timeouts, oversize bodies, HTTP 401, 403, 429, or 5xx responses.
Clear the saved identity when a later probe succeeds or the probe identity changes.

Centralize billing-probe failure memoization in `persistProbeFailure` after snapshot persistence succeeds.
Leave `fetchBilling` and `PreviewGroup` free of memoization writes.

### Scheduling synchronization

Synchronize non-error usage results from default detection and saved scripts into account scheduling state.
Draft script previews in `POST /admin/accounts/quota-script/test` do not change account scheduling state.
Save window utilization and RFC 3339 reset timestamps in `accounts.extra.apikey_quota_{5h,1d,7d,30d,total}_{used_percent,reset_at}`.
Set `accounts.extra.apikey_quota_exhausted` when balance is zero or negative, or when an exhausted window lacks a future reset.
Store the internal balance source in Boolean `accounts.extra.apikey_quota_balance_exhausted`.
Reuse existing utilization and reset keys for window sources. Include the balance key in managed-key cleanup and scheduler filtering.
Pause dated window exhaustion until the latest future reset with reason `apikey_quota_window_exhausted`.
Clear that pause and exhaustion flag when usage recovers, probe identity or `quota_script` changes, or quota resets.

Include `apikey_quota_*` keys in `filterSchedulerExtra` so Redis scheduler snapshots enforce quota exhaustion and threshold rules.
Evaluate saved window snapshots in `EvaluateAccountSchedulingThreshold` when native platform window keys are absent.
Guard temporary pause writes and clears with reason prefix `apikey_quota_` so non-quota pauses stay intact.
Skip database writes when persisted quota or memoization state is unchanged.

Build response-determined target values without comparing them with the account snapshot read before the request.
Merge reported balance and window observations with the current locked database state before deriving combined scheduling state.
A healthy reported source clears its own exhaustion. Keep exhaustion from sources that the response does not report.
Clear the combined flag only when no retained source requires it. Derive the quota pause from all retained dated windows.
Reported windows supply their current utilization and reset timestamp. Preserve window fields that the response cannot determine.
An empty quota result changes no scheduling state.
Use database-current `IS DISTINCT FROM` predicates to suppress unchanged writes.
Change `updated_at` only when the reported expiration differs from the current database expiration.
Default usage and saved scripts share these rules. A later healthy response can clear exhaustion from an overlapping same-identity request.
Use recorded balance and window sources to derive scheduling state.
Do not infer an additional balance block from an old aggregate flag or require an administrator reset for recovery.

### Identity changes and atomic writes

Compare platform, account type, complete credentials, proxy ID, hydrated proxy identity, and normalized `quota_script` before asynchronous write-back.
Check the proxy target under a shared lock and apply the account mutation through one conditional SQL update in the same transaction.
A stale snapshot returns `applied == false`. It must not change persisted quota, expiration, unsupported identity, or the caller's account snapshot.
Change the caller's snapshot only after persistence succeeds.
Report a missing quota writer through the existing error path. Do not fall back to unguarded writes.

Single and bulk credential, proxy, or script edits clear their previous quota scheduling state.
Probe identity includes adaptive routing fields `api_protocol`, `api_base_urls`, `provider_mode`, and `account_mode`.
An HTTP identity change clears shared billing and unsupported-probe state as well.
A script-only change clears quota scheduling state while retaining the billing snapshot.
Validate and normalize bulk `quota_script` input through the existing string-or-null contract.
Remove cleared managed keys from JSONB. Do not leave JSON null values.

Single and bulk account updates clear only pauses whose reason starts with `apikey_quota_`.
Use the existing update transaction and synchronize scheduler snapshots after commit.
Failed validation must leave persisted state unchanged. Preserve non-quota pauses in mixed batches and during concurrent updates.

Ordinary administrator saves merge quota state within the native account update transaction.
Lock the current account row within the existing update transaction. Preserve native administrator-save conditions.
For unchanged identity and script, merge quota-managed keys from that locked row, including newly absent keys.
A script-only change retains unsupported-probe state while clearing scheduling state. Identity changes retain their established cleanup rules.
Preserve current expiration unless the administrator supplies a value that differs from the pre-edit account snapshot.
An unchanged expiration submitted by a full form must not replace a newer probe expiration.
Pass `MergeAPIKeyQuotaState` and `PreviousExpiresAt` on `AccountBillingSettingsUpdate`. Zero-value callers skip the quota merge.
Retain current temporary pauses unless an identity or script edit clears a quota pause.
Run the locked merge, native billing-settings update, and scheduler event in one transaction.
Refresh the scheduler snapshot after commit. Keep existing repository callers and billing-settings contracts usable.

Both plugins edit native administrator routes and account metadata preservation.
Keep evaluation `codex_eval_inspection_*` keys separate from quota-managed keys.
Keep quota `HTTPUpstream` and configuration injection aligned with `wire_gen.go`.

### Script storage and results

Store one string in `accounts.extra.quota_script` through existing account save APIs.
Nonblank code selects custom execution for any API-key platform, including official targets and accounts with dedicated native cells.
Clearing and saving removes the field and restores the existing provider dispatch.
Preserve unrelated settings and existing callers that do not supply this field. Saving does not execute code or require a successful test.

Scripts define synchronous `queryQuota(ctx)`. Pass `ctx.apiKey` and `ctx.baseUrl` as data, never through source interpolation.
Return one object with optional fields:

| Script field | Value | Native field |
| --- | --- | --- |
| `session` | `{ used, limit, reset_at? }` | `five_hour` |
| `day` | `{ used, limit, reset_at? }` | `one_day` |
| `week` | `{ used, limit, reset_at? }` | `seven_day` |
| `month` | `{ used, limit, reset_at? }` | `thirty_day` |
| `total` | `{ used, limit, reset_at? }` | `quota_total` |
| `balance` | Number or `{ amount, unit? }` | `balance` |
| `unit` | Optional balance-unit fallback | Optional `balance_unit` |

```javascript
function queryQuota(ctx) {
  const response = http.request({
    url: ctx.baseUrl.replace(/\/$/, '') + '/balance',
    headers: { Authorization: 'Bearer ' + ctx.apiKey }
  });
  if (response.status !== 200) throw new Error('HTTP ' + response.status);
  const data = JSON.parse(response.body);
  return { balance: { amount: Number(data.remaining), unit: 'USD' } };
}
```

Each window requires finite `used >= 0` and finite `limit > 0`. Calculate utilization as `used / limit * 100`.
Accept optional RFC 3339 `reset_at`. Period keys select slots but do not determine reset timestamps or fixed durations.
Validate the complete result before mapping any fields. An empty object means no remote data. Preserve zero values and absent fields.
Balance amounts must be finite and may represent debt.
Resolve unit from `balance.unit`, then root `unit`, then `USD`. Trim a supplied unit and reject blank strings.
Resolve unit only when balance exists. Units affect display and do not request currency conversion or billing multiplication.
Keep default detection responses unchanged. The frontend uses `balance_unit || 'USD'` for balance text.
Do not add a custom quota array, display labels, or duplicate result fields.

### Script runtime and HTTP

Use pure Go Goja at `v0.0.0-20261024144015-2a9269b6b6de` inside the existing executable.
Keep its `regexp2/v2 v2.8.1` requirement, also selected for the upstream tokenizer.
Create one runtime per invocation. Use synchronous calls without Node, timers, module loading, shell, or filesystem APIs.
Expose `http.request({url, method?, headers?, body?}) -> {status, body}`. The default method is GET, and body values are strings.
Reuse configured URL policy, proxy, context-scoped header overrides, transport profile, and TLS profile.
Disable redirects and keep the existing 64 KiB response bound.
Share the existing ten-second deadline across JavaScript, host HTTP work, and result conversion.
Use runtime interruption for JavaScript and the same Go context for HTTP. Keep a call-stack bound.
Reject Promise results. Keep script-controlled exception text conversion under the same deadline.
Goja has no hard per-runtime memory quota. Administrator-authored scripts can exhaust server process memory.

Do not log response bodies or credentials. Redact saved account credentials, proxy credentials, and header-override values from error text.
Read configured overrides through `GetHeaderOverrides` so values containing identity variables are redacted too.
Host diagnostics do not append source, header, or response-body dumps. Administrator-authored exceptions retain their message after this redaction.

### Draft tests

The test body accepts `script` and optional `account_id`, `api_key`, `base_url`, `proxy_id`, and `extra`.
With `account_id`, copy the saved API-key account as the baseline. Without it, construct a temporary API-key account.
Nonblank draft key and base URL values replace the baseline. Omitted or blank strings retain baseline values.
An omitted proxy retains the baseline. Explicit `null` removes it, and an ID selects that proxy through server lookup.
Merge supplied extra keys over the baseline map, including supplied empty or null values.
Retain saved TLS settings in API-key forms, which expose no TLS controls.
Retain other saved connection settings, including credential header overrides. The test body does not accept a whole credentials map.
Reuse the native adaptive base-URL selection when resolving effective script context.
Test current unsaved code and effective draft settings in both create and edit forms.
Return native success/error envelopes without saving, quota write-back, or list-cache updates.

### Editor

Use one `QuotaScriptEditor.vue` in create and edit forms, including the separate Antigravity upstream creation path.
Use the native `HelpTooltip` beside its label for script input and output reference.
Use a CSS grid with highlighted `<pre>` text and a transparent `<textarea>` in the same cell.
Keep the editor auto-expanding and free of scrollbars. Use native token colors, input styles, and a small secondary test button.
Keep the starter code as placeholder text. Do not save or execute that placeholder as the account's script.
Disable testing for blank code or an active request. Display results and amber error text inside the editor.
Ignore obsolete test output after script, effective connection, account, or modal changes.
Use no editor package, example button, subtitle, or nested card.

### Display and refresh

Without a script, add general usage requests only for standard-cell API-key platforms with a nonempty `base_url`.
Keep existing multi-protocol eligibility and native platform cells for those accounts.
With a script, use the standard API-key remote quota display for every API-key platform.
Do not issue a second remote query or fall back after a custom failure. Keep local usage and quota information visible.
Reuse native `5h`, `1d`, `7d`, `30d`, and `total` badges, progress bars, and balance text.

Pass reported `resets_at` to native `UsageProgressBar.resetsAt`. Keep its inline countdown and existing expired-time behavior.
Show the mapped reset date/time in the native hover tooltip copied from `AccountStatusIndicator.vue`.
Reuse `formatDateTimeToMinute` and `dashboard.platformQuota.resetsAt`. A missing timestamp produces no reset tooltip.
Keep unknown reset times absent, except for the approved default subscription calculation above.
Do not infer custom-script reset times from period labels.

Preserve cache, batch, lazy-load, and manual-refresh paths.
After saved script or effective connection changes, invalidate only that account and reject stale in-flight results.
Extend native `buildAccountUsageRefreshKey(account)` with the API-key branch and reuse `serializeSnapshotRefreshValue`.
Include connection fields, `extra.quota_script`, proxy ID, TLS fields, and `updated_at` for API-key accounts.
Account responses omit the saved key. The save timestamp detects key-only changes without exposing credentials.

Both `_usageCache` and `usageBatchCache` store only `{ data, ts, refreshKey }` with the native five-minute TTL.
Use the single `usageRefreshKey` watcher for API-key invalidation and immediate refresh, including cells outside the viewport.
Accept single replies only when their captured account ID and refresh key still match.
Keep request counters and unmount checks on passive single replies.

For batch success and failure, compare the current account key with the captured `refreshKeys` entry.
Preserve `usageBatchRequestTokenByAccountId` for same-key ordering and native `shouldReplaceAutoRefreshRow` behavior.
Keep native Claude and Gemini snapshot refreshes passive. Unrelated metadata changes do not start another query.

Use `admin.accounts.usageWindow.upstreamQuota` as the native title on remote bars and balance text.
Keep the native placeholder when no local or visible remote data exists. Zero balance counts as visible data.

## 4. Validation & Error Matrix

| Condition | Result |
| --- | --- |
| Default mode without usable fields | No mapped fields and no query error |
| Default or billing probe HTTP 404, 405, 501, or invalid 2xx body | Save shared unsupported probe identity and skip automatic probes for that identity |
| Default HTTP 401, 403, 429, 5xx, timeout, or transport failure | No mapped quota fields, added `error`, or memoization |
| Default URL-policy rejection or account setup failure | No mapped quota fields, added `error`, or added `error_code` |
| Exhausted balance (`<= 0`) or undated exhausted window (`>= 100%`) | Set `apikey_quota_exhausted` so `IsQuotaExceeded` blocks scheduling |
| Exhausted dated window (`>= 100%` with future `reset_at`) | Pause scheduling until the latest future `reset_at` |
| Recovered balance (`> 0`) and windows (`< 100%`) | Clear `apikey_quota_exhausted` and any `apikey_quota_` temporary pause |
| Identity, proxy target, or script changes during a query | Reject stale quota, expiration, pause, and memoization writes atomically |
| Healthy response follows overlapping same-source exhaustion | Clear that source and recalculate combined exhaustion and quota pause |
| Partial response omits an exhausted balance or window source | Retain that source and its applicable scheduling block |
| Old exhausted account lacks balance-source metadata | Recalculate from recorded sources without an added administrator-reset requirement |
| Ordinary save overlaps a quota-state update | Preserve current database quota state and any unedited expiration |
| Response target state already matches the database | Skip the account write and scheduler event |
| Single or bulk identity/script edit | Remove managed quota keys and clear quota pauses. Preserve non-quota pauses. |
| Invalid bulk `quota_script` value | Reject the edit before persistence |
| Key or subscription expiry reported | Save the earlier available value to native account expiration |
| Neither expiry reported | Preserve the saved account expiration |
| Expiry persistence fails | Keep mapped quota output and default-query silence |
| Custom syntax, execution, HTTP, or result-validation failure | Safe text in existing `UsageInfo.error`, with no partial remote fields or fallback query |
| Custom test execution failure | Native error envelope with safe diagnostics inside the editor |
| Blank test script or invalid test request | Native bad-request response without account changes |
| Cleared script on save | Default detection resumes |

Keep default quota error types and descriptions absent. Add no custom runtime error-code field or global toast.
Preserve response validation, request deadlines, response-size limits, local statistics, and quota bars.
Accounts without scripts retain native errors. Custom errors use the existing usage error owner.

## 5. Good / Base / Bad Cases

Good: a rate-only response maps its `used` and `limit` into the matching native window without top-level remaining.
Good: an unsaved create-form script uses draft settings and returns a balance unit without creating an account.
Good: a healthy result clears exhaustion saved after that request read its account snapshot.
Good: a name edit retains a concurrent quota recovery rather than restoring its old exhausted flag.
Base: an official target without a script returns no new remote fields and retains the native cell's empty placeholder.
Bad: a custom error triggers default detection, an empty response hides the placeholder, or a test replaces saved settings.

## 6. Tests Required

Use the focused cases in [the native Go suite](../../../plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go).
Cover response mapping once in the backend, including zero, omission, rate-only windows, and ignored unlimited values.
Extend the existing subscription case for the approved reset calculation and missing source timestamps.
Use existing default mapping and usage-entrypoint cases for expiry selection, narrow persistence, and removal of the monthly expiry reset.
Use `TestUpstreamQuotaProbeMemoization` for shared probe memoization, manual pass-through, transient-error retries, and identity-change invalidation.
Use `TestUpstreamQuotaSchedulingIntegration` and `TestQuotaScriptSchedulingIntegration` for exhaustion pause, recovery resumption, and threshold evaluation.
Use [the repository suite](../../../plugins/sub2api-quota-extension/tests/test_account_repo_quota_test.go) for compare-and-swap SQL, reason-guarded pause clearing, and bulk key stripping.
Cover unchanged-state SQL rejection and conditional expiration timestamps in that suite.
Cover same-identity overlap recovery for both default usage and scripts, including exhaustion flags and dated pauses.
Cover omitted balance after balance exhaustion, omitted windows after window exhaustion, and recovery after each source returns.
Check that an omitted dated window keeps its pause. Check recovery without an added administrator-reset prerequisite.
Use deterministic request barriers or repository hooks. Do not use timing sleeps to create the concurrent update.
Check locked ordinary-save merges for concurrent exhaustion, recovery, absent managed keys, explicit expiration, and existing reset behavior.
Use existing single and batch entry points to check default behavior and the custom-script dispatch boundary.
Cover custom selection, visible failure, absence of fallback, and removal restoration without multiplying failure cases by entry point.
Use [the script runner suite](../../../plugins/sub2api-quota-extension/tests/test_quota_script_test.go) for execution, period/unit validation, and JavaScript/HTTP cancellation.
Use [the preview suite](../../../plugins/sub2api-quota-extension/tests/test_quota_script_handler_test.go) for draft overlays, proxy removal, native envelopes, and the absence of persistence.

Use [the native Vue suite](../../../plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts) for mapped rendering, query eligibility, and refresh.
Check native mapped display, custom units/errors, and changed-row refresh there.
Extend its existing cache-refresh case for a key-only save with redacted credentials and a changed `updated_at`.
Extend its existing display case for the formatted reset tooltip and its absence without a timestamp.
Use [the batch suite](../../../plugins/sub2api-quota-extension/tests/test_usage_batch.test.ts) for obsolete replies and native request ordering.

Check stale success and failure, same-key overlap, unchanged-key reuse, and native snapshot refresh in the cell and batch suites.
Check immediate saved-configuration refresh outside the viewport and script removal that clears obsolete state.
Use [the shared editor suite](../../../plugins/sub2api-quota-extension/tests/test_quota_editor.test.ts) for editor behavior and form wiring.
Preserve existing default-error, placeholder, local-information, and zero-balance cases.
Frontend and handler cases consume mapped output without repeating the backend result matrix.
Keep all tests and support flat under plugin `tests/`. Add no platform, period, race, coverage, browser, or container acceptance matrix.
Use the default build once for integration. Reuse unchanged helper, cache, installer, and composition evidence.
Review unchanged source boundaries and local quota ownership through the diff.

## 7. Wrong vs Correct

Wrong: require a successful billing declaration or a top-level remaining amount before mapping quota windows.
Correct: query usage independently and map reported window used/limit pairs into native progress fields.

Wrong: use display labels to identify periods or rerun default detection after a custom script fails.
Correct: map explicit period keys and show the custom error while preserving local information.

Wrong: omit healthy-state writes because the request's old account snapshot was already healthy.
Correct: emit the response target state and compare it with current values in the database.
