# Custom Quota Script Design

## Boundary and Storage

Extend the existing quota plugin on Sub2API v0.2.19.
Use cc-switch only for the configure, edit, test, and save interaction.
The existing quota spec continues to govern default detection.
This task adds custom-script errors, balance units, and query eligibility.
Default detection also maps the approved weekly reset and synchronizes native account expiration.
Accounts without scripts retain their native provider dispatch.
Use the account's existing `extra` JSON field:

```json
{
  "quota_script": "function queryQuota(ctx) { return { balance: 0 }; }"
}
```

Only `type: apikey` accounts execute scripts.
Nonblank script text selects the custom query. Empty or whitespace-only text uses the default query.
Keep nonblank source text unchanged. Clearing the editor and saving removes `quota_script`.
Merge the script change with the form's other extra values. Preserve unrelated account and runtime values.
Use existing account create and update APIs. Add no database migration or script configuration route.
Validate the supplied script as a string. Add no enabled, language, code wrapper, or timeout field.
Validate newly provided script configuration without adding requirements to unrelated save callers.
Stored script configuration remains inactive if an account changes to a non-API-key type.
Saving does not execute code or require a successful test.
Unchanged callers and accounts without script configuration keep their current save contract.

## Editor

Add one shared `QuotaScriptEditor.vue` to the API-key areas of `CreateAccountModal.vue` and `EditAccountModal.vue`.
Place the native `HelpTooltip` beside the `自定义额度脚本` label.
Use `@/components/common/HelpTooltip.vue` with `width-class="w-max max-w-[calc(100vw-2rem)]"`.
Follow `UpstreamRequestIdHeaderField.vue` and `UpstreamBillingRateCell.vue` for placement.
Document the input and result contracts in this tooltip, including both balance forms and the optional root `unit`.

Use an auto-expanding CSS grid with `<pre aria-hidden="true">` and a transparent `<textarea>` in the same cell.
Use `overflow-hidden resize-none` and `.input font-mono text-xs` styles. Keep the editor free of scrollbars.
Add built-in JavaScript token highlighting with native Tailwind token classes from `UseKeyModal.vue`.
Use the starter `queryQuota(ctx)` example as placeholder text.
Use `.btn.btn-secondary.btn-sm` for inline testing in both forms.
Render results with `UsageProgressBar` and `{{ usageInfo.balance_unit || 'USD' }} {{ usageInfo.balance.toFixed(2) }}` balance text.
Use the native countdown and reset date/time tooltip described in Result Contract.
Use `text-xs text-amber-600 dark:text-amber-400` for errors.
Add no editor package, scroller, subtitle, example button, or nested card box.

Disable the test button when the script is blank or while a test request is in flight.
The parent form saves `extra.quota_script` with the account. Closing the form discards the draft.
Test current code against effective connection settings using the draft rules in Manual Test API.
Testing does not save the account or seed list caches.
Clear or ignore stale test output when the script, connection fields, account, or modal state changes.
Use no global error toast.

## JavaScript Contract

Use the pure Go Goja interpreter in the server process.
Pin `github.com/dop251/goja` to `v0.0.0-20261024144015-2a9269b6b6de` in the patched upstream module files.
This dependency supports the current Go toolchain and CGO-disabled delivery.
Use a fresh runtime for each invocation. Run each runtime on one goroutine.
Only the cancellation watchdog calls the documented thread-safe interruption method from another goroutine.

The script defines the synchronous function `queryQuota(ctx)`.
Pass `ctx` as data with `apiKey` and `baseUrl` strings from the account's effective connection settings.
Use existing adaptive base-URL selection when applicable. Do not substitute credentials into JavaScript source.
Expose one synchronous host function:

```text
http.request({url, method?, headers?, body?}) -> {status, body}
```

`url` is an absolute HTTP or HTTPS URL subject to the existing configured URL policy.
The method defaults to GET. Header values and an optional request body are strings.
The response body is text. Scripts can parse JSON with `JSON.parse` and inspect the HTTP status.
Requests use the account's existing proxy, header overrides, transport profile, and TLS settings.
Keep redirects disabled and reuse the current 64 KiB response-body boundary.
Do not install Node.js or expose process, filesystem, shell, or module-loading APIs.
The contract has no asynchronous jobs, timers, or Promise results.

Example:

```javascript
function queryQuota(ctx) {
  const response = http.request({
    url: ctx.baseUrl.replace(/\/$/, '') + '/balance',
    headers: { Authorization: 'Bearer ' + ctx.apiKey }
  });
  if (response.status !== 200) {
    throw new Error('HTTP ' + response.status);
  }
  const data = JSON.parse(response.body);
  return { balance: Number(data.remaining) };
}
```

An invocation shares the existing ten-second quota deadline across JavaScript execution and host HTTP requests.
Use runtime interruption for JavaScript and the same context for HTTP and response reads.
Keep a runtime call-stack bound. Context cancellation must stop the active script and its HTTP work.
Goja interruption does not cancel arbitrary native Go work. Register only the required HTTP host function.
Goja provides no per-runtime hard memory quota. This design runs administrator-authored code in the server process.

## Result Contract

Return one object. All root fields are optional:

| Script field | Meaning | Native usage field | Native badge |
| --- | --- | --- | --- |
| `session` | Short-window quota | `five_hour` | `5h` |
| `day` | Daily quota | `one_day` | `1d` |
| `week` | Weekly quota | `seven_day` | `7d` |
| `month` | Monthly quota | `thirty_day` | `30d` |
| `total` | Total quota | `quota_total` | `total` |
| `balance` | Number or `{ amount, unit? }` | `balance`, `balance_unit` | Unit, default `USD` |
| `unit` | Optional balance-unit fallback | `balance_unit` | Unit |

```javascript
return {
  session: { used: 10, limit: 50 },
  day: { used: 30, limit: 100, reset_at: '2026-10-28T00:00:00Z' },
  week: { used: 80, limit: 500 },
  month: { used: 200, limit: 2000 },
  total: { used: 300, limit: 5000 },
  balance: { amount: 25, unit: 'USD' }
};
```

Each quota window requires a finite nonnegative `used` and a finite positive `limit`.
Compute `used / limit * 100` for the native progress bar. Used amounts may exceed the limit.
Each window can include an optional RFC 3339 `reset_at`. Derive its reset countdown from that timestamp.
Use the mapping and renderer in [Reset Date and Time](#reset-date-and-time).

Period keys select the native usage slots.
`session` identifies the upstream short quota window.
The legacy `five_hour` and `thirty_day` storage names do not impose fixed durations or derive reset timestamps.
Reuse the existing `upstreamUsageWindows` (`5h`, `1d`, `7d`, `30d`, `total`) fixed-width `w-[32px]` badges in `UsageProgressBar`.
Do not infer reset boundaries from a period key or the current date.

Accept `balance: number` with optional root `unit`, or `balance: { amount, unit? }`.
The balance amount must be finite. Keep zero and debt visible.
Use `balance.unit` when present, then root `unit`, then `USD`. Trim a supplied unit and require a nonblank string.

Resolve a unit only when balance is present. This is a display unit and does not request currency conversion.
Map a supplied unit to optional `UsageInfo.balance_unit` (`json:"balance_unit,omitempty"`) and its frontend type.
Default detection keeps its current response. The frontend's `USD` fallback covers responses without `balance_unit`.
Do not reapply a billing multiplier.

An empty object is a valid no-data result. Omitted fields stay absent and zero values remain visible.
Read and validate only these fields. Errors use exceptions, not result fields.
Validate the complete result before mapping it into the existing native usage fields.
Reuse the native usage types. Add no custom quota array, label field, or duplicate serialization.
Keep the default detector's response fields and USD display unchanged. Reuse native progress bars and numeric text styles.
Use server time for `updated_at`.

## Reset Date and Time

The addition covers the previous default detector, saved custom scripts, and inline previews.
Keep the existing inline countdown and show its mapped reset date/time on hover.
Copy the native tooltip pattern from `AccountStatusIndicator.vue:94-136`, including its positioning, colors, spacing, and arrow.
The code-level research is [Reset Date and Time Code Plan](./research/reset-date-code-plan.md).

### Existing Data Contract

| Owner | Existing contract | Required change |
| --- | --- | --- |
| `backend/internal/service/account_upstream_quota.go`, `parseUpstreamQuota` | Reported rate-window resets map to native progress fields | Preserve rate-window mapping. Add weekly start plus seven days and select the earlier key/subscription expiry internally. |
| Native account repository and `AccountBulkUpdate` | Account expiration controls native expiry behavior | Add a narrow expiry update with existing scheduler synchronization. |
| `backend/internal/service/account_quota_script.go`, `readQuotaScriptResult` | Optional period `reset_at` uses RFC 3339 validation and the same native fields | None |
| `UsageInfo` and frontend `UsageProgress` | The response already contains `resets_at` | None |
| `AccountUsageCell.vue` | Saved default/custom usage passes to `UpstreamQuotaUsage` | None |
| `QuotaScriptEditor.vue` | Inline test usage passes to `UpstreamQuotaUsage` | None |
| `UsageProgressBar.vue` | `resetsAt` drives its existing countdown and expired-time display | Add the copied native hover tooltip |

Keep backend validation and error handling under their current owners.
The user accepts simplified subscription dates from the existing v0.2.19 response.
Decode optional `weekly_window_start` and `expires_at` as timestamps in the subscription response model.
Calculate weekly `ResetsAt` as `weekly_window_start.Add(7 * 24 * time.Hour)` and reuse the existing countdown calculation.
Keep a missing weekly start absent. Explain the direct addition and omitted legacy `StartsAt` correction in a code comment.
Decode the key-level and nested subscription `expires_at` values from the existing response.
Select the earlier available value and save it to native account expiration through the existing account update path.
Use the one reported value when the other is absent. With neither value, preserve the saved expiration.
Subscription expiry does not populate monthly `ResetsAt`. Keep daily and monthly reset times absent without their source anchors.
Preserve native expiration settings and behavior. Add no separate account-disable policy or background job.
`Account.ExpiresAt` uses `*time.Time`. Extend the existing `AccountBulkUpdate` with the same optional field.
Use native `AccountRepository.BulkUpdate` for the narrow write and its scheduler outbox and snapshot synchronization.
Skip an unchanged expiration. Preserve quota output when persistence fails, following the silent default-query contract.
Keep selected expiry in an internal decoder result. Add no usage API field or frontend request.
The existing account-expiry column displays the saved value after the next native account-list refresh.
Do not cap or advance the weekly timestamp. Reuse existing expired-time behavior.
Do not change the upstream response or require upstream deployment.
The [source research](./research/default-quota-v0219.md) records the accepted approximation's limits.

### Production Patch

Change `frontend/src/components/account/UsageProgressBar.vue` inside `patches/quota-extension.patch`.
Keep `UpstreamQuotaUsage.vue` unchanged. It already supplies `resets-at` for default results, saved scripts, and inline previews.
Extend the existing formatter import:

```ts
import { formatCompactNumber, formatDateTimeToMinute } from '@/utils/format'
```

Keep the existing reset-time span as the hover group. Copy the native tooltip and arrow inside it:

```vue
<span
  v-if="shouldShowResetTime"
  class="group relative shrink-0 text-[10px] text-gray-400"
>
  {{ formatResetTime }}
  <span
    v-if="resetsAt"
    class="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 w-max max-w-[320px] -translate-x-1/2 whitespace-nowrap rounded bg-gray-900 px-3 py-2 text-center text-xs leading-relaxed text-white opacity-0 transition-opacity group-hover:opacity-100 dark:bg-gray-700"
  >
    {{ t('dashboard.platformQuota.resetsAt', { time: formatDateTimeToMinute(resetsAt) }) }}
    <span
      class="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-gray-900 dark:border-t-gray-700"
    ></span>
  </span>
</span>
```

Use nested spans to retain the existing countdown font metrics and row height.
The tooltip stays outside normal flow, as in the native status indicator.
Keep the existing countdown calculation, timer, badges, colors, and root upstream-quota title.
A missing timestamp produces no reset tooltip. A known expired timestamp retains its exact date while the countdown keeps its native expired state.

`formatDateTimeToMinute` uses `Intl.DateTimeFormat(getLocale(), options)` through the existing `formatDate` helper.
It displays year, month, day, hour, and minute with a 24-hour clock.
It supplies no `timeZone` option, so the browser's local timezone applies.
Keep `resetsAt` unchanged. Reuse `dashboard.platformQuota.resetsAt`, which already renders `Resets {time}` and `{time} 重置`.
Use no new date row, formatter, timer, translation key, response field, date setting, or quota request.

The existing native Vue display case owns the tooltip regression check.
Use [Reset Date Code Changes](./implement.md#reset-date-code-changes) for the focused validation plan.

## Manual Test API

Add one route under the existing administrator middleware:

```text
POST /api/v1/admin/accounts/quota-script/test
```

Request fields:

```text
script: string
account_id?: number
api_key?: string
base_url?: string
proxy_id?: number | null
extra?: Record<string, any>
```

With `account_id`, use an in-memory copy of the saved API-key account from `AdminService.GetAccount`.
Without `account_id`, construct a temporary API-key account from the form draft, following `SyncUpstreamModelsPreview`.
Nonblank draft `api_key` and `base_url` replace baseline values. Omitted or blank strings retain the baseline values.
An omitted `proxy_id` retains the baseline proxy. Explicit `null` clears it, and an ID selects that proxy.
Merge supplied `extra` keys over the baseline extra map. Preserve unrelated keys and apply supplied empty or null values.
Retain other saved connection settings, including credential header overrides. The preview overlays only the listed draft fields.
Resolve an active proxy ID through `AdminService.GetProxy` if it is not attached.
Reject blank test scripts. This endpoint executes custom scripts only.
Reuse the injected `AccountUsageService`; add no new handler constructor dependency.

Expose one service execution entry for both testing and saved-account reads:

```go
func (s *AccountUsageService) ExecuteQuotaScript(
    ctx context.Context, account *Account, script string,
) (*UsageInfo, error)
```

Use the native success envelope containing the validated usage result.
Use the native error envelope for test diagnostics.
Return useful syntax locations, execution failures, HTTP status, or result-validation details.
Host diagnostics must not append source, header, or response-body dumps. Do not log credentials or response bodies.
Redact saved account credentials, proxy credentials, and header-override values before returning errors.
Administrator-authored exceptions retain their message after this redaction.
The endpoint does not persist an account or call a quota write-back path.

## Runtime Dispatch and Display

Check for nonblank script text before automatic upstream identity and official-domain filters.
Run it for any API-key platform. Do not require the automatic `/v1/usage` endpoint or billing declaration.
The custom script owns that account's remote quota query. Do not run a second native or automatic remote query.
On custom failure, return the safe diagnostic in the existing `UsageInfo.error` field and publish no partial quota readings.
Use the same diagnostic handling for single-account reads, batch reads, and manual tests. Add no new error-code field.
Display that error with native account-cell error styles while keeping local statistics and quota information.
The default quota query still adds no error text or error code when it fails.
An absent script follows the exact existing provider dispatch. Existing native provider errors retain their current behavior.

Use one shared native quota renderer for script results and existing standard-cell upstream results.
For configured scripts, bypass dedicated remote quota cells while keeping the existing local usage and local quota display.
This includes multi-protocol, Gemini, Antigravity, and Grok API-key accounts.
Keep native provider-specific views for all other accounts.

Extend the existing query predicates for configured scripts in desktop and mobile flows.
Retain the current batch queue, lazy loading, manual refresh, and response guards.
When saved script text or effective connection settings change, invalidate only that account's usage state.
Discard an in-flight result from the old configuration and fetch the current configuration through existing paths.
Include `updated_at` in every API-key refresh key. Account responses omit saved keys, so key-only changes need this save timestamp.
Use a direct configuration comparison. Add no hash or separate cache system.

## Delivery and Removal

Keep all product changes in the existing quota submodule's contextual patches and flat tests.
Patch the upstream `backend/go.mod` and `backend/go.sum` for the interpreter dependency.
Include applicable original dependency license files under the plugin's `licenses/` tree for existing packaging.
Keep the original root license. Add no notice summary, manifest, registry, or product document.
The common builder and installer require no new interface or runtime installation steps.
Removing this plugin from a later build removes execution. Empty or dormant configuration has no effect.
The current installer backup and restoration flow remains the installed recovery path.

## Validation Ownership

Backend cases own script execution, host requests, output validation, deadlines, and single/batch dispatch.
Handler cases own create/edit draft settings, proxy selection, native envelopes, and the absence of persistence.
Vue cases own editor state, script testing, clearing code, visible custom errors, and the changed account-cell branches.
Reuse existing automatic-quota, transport, cache, build-composition, and installer evidence where unchanged.
Use one successful default combined build as the final integration result.
Use the focused validation plan in `implement.md` for case ownership and reuse.
