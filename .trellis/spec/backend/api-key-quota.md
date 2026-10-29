# API Key Account Usage

## 1. Scope / Trigger

The `sub2api-quota-extension` plugin adds default upstream quota detection and custom JavaScript queries on Sub2API v0.2.19.
Both paths use the existing account-management usage column for API-key accounts.
Default detection also synchronizes native account expiration. It leaves channel monitor source and local quota counters unchanged.
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
Use native `AccountRepository.BulkUpdate` with optional `ExpiresAt *time.Time` for a narrow account update.
Retain its scheduler outbox and snapshot synchronization. Skip writes when the selected expiration is unchanged.
Keep decoder expiry internal. Add no usage response field or extra frontend request.
The existing account-expiry column reflects persistence on the next native account-list refresh.

Default detection reads custom API-key targets independently of the billing probe's switch or result.
Reuse official-domain and adaptive-target selection. Preserve native Gemini, Antigravity, and Grok results and errors.
Malformed nonempty URLs must reach URL validation rather than the official-target shortcut.

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
Create one runtime per invocation. Use synchronous calls without Node, timers, module loading, shell, or filesystem APIs.
Expose `http.request({url, method?, headers?, body?}) -> {status, body}`. The default method is GET, and body values are strings.
Reuse configured URL policy, proxy, header overrides, transport profile, and TLS profile.
Disable redirects and keep the existing 64 KiB response bound.
Share the existing ten-second deadline across JavaScript, host HTTP work, and result conversion.
Use runtime interruption for JavaScript and the same Go context for HTTP. Keep a call-stack bound.
Reject Promise results. Keep script-controlled exception text conversion under the same deadline.
Goja has no hard per-runtime memory quota. Administrator-authored scripts can exhaust server process memory.
Do not log response bodies or credentials. Redact saved account credentials, proxy credentials, and header-override values from error text.
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
`buildAPIKeyUsageRefreshKey(account)` includes `updated_at` for every API-key account, with or without a script.
Account responses omit the saved key. The save timestamp detects key-only changes without exposing credentials.
Use `admin.accounts.usageWindow.upstreamQuota` as the native title on remote bars and balance text.
Keep the native placeholder when no local or visible remote data exists. Zero balance counts as visible data.

## 4. Validation & Error Matrix

| Condition | Result |
| --- | --- |
| Default mode without usable fields | No mapped fields and no query error |
| Default HTTP, timeout, transport, or body-read failure | No mapped quota fields, added `error`, or added `error_code` |
| Default invalid response, URL-policy rejection, or account setup failure | No mapped quota fields, added `error`, or added `error_code` |
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
Base: an official target without a script returns no new remote fields and retains the native cell's empty placeholder.
Bad: a custom error triggers default detection, an empty response hides the placeholder, or a test replaces saved settings.

## 6. Tests Required

Use the focused cases in [the native Go suite](../../../plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go).
Cover response mapping once in the backend, including zero, omission, rate-only windows, and ignored unlimited values.
Extend the existing subscription case for the approved reset calculation and missing source timestamps.
Use existing default mapping and usage-entrypoint cases for expiry selection, narrow persistence, and removal of the monthly expiry reset.
Use existing single and batch entry points to check default behavior and the custom-script dispatch boundary.
Cover custom selection, visible failure, absence of fallback, and removal restoration without multiplying failure cases by entry point.
Use [the script runner suite](../../../plugins/sub2api-quota-extension/tests/test_quota_script_test.go) for execution, period/unit validation, and JavaScript/HTTP cancellation.
Use [the preview suite](../../../plugins/sub2api-quota-extension/tests/test_quota_script_handler_test.go) for draft overlays, proxy removal, native envelopes, and the absence of persistence.

Use [the native Vue suite](../../../plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts) for mapped rendering, query eligibility, and refresh.
Check native mapped display, custom units/errors, and changed-row refresh there.
Extend its existing cache-refresh case for a key-only save with redacted credentials and a changed `updated_at`.
Extend its existing display case for the formatted reset tooltip and its absence without a timestamp.
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
