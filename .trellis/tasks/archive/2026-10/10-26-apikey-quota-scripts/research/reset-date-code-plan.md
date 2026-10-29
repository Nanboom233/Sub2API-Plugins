# Research: Reset Date and Time Code Plan

- Query: Define the smallest code and test changes for visible quota reset dates and times.
- Scope: Internal code research.
- Date: 2026-10-28.

## Findings

This document records the earlier v0.2.18 renderer plan.
The current PRD and design include the later v0.2.19 weekly calculation and native account expiry synchronization.

### Data flow at the renderer research stage

The previous key-rate detector preserves upstream reset timestamps. Its subscription branch originally omitted them.

1. `backend/internal/service/account_upstream_quota.go:16-32` decodes `rate_limits[].reset_at` into `upstreamQuotaAmount.ResetAt`.
2. `backend/internal/service/account_upstream_quota.go:66-82` copies that timestamp into `UsageProgress.ResetsAt` and computes `RemainingSeconds` from the supplied `now` value.
3. `backend/internal/service/account_usage_service.go:354-365` returns the default result through the native `UsageInfo` object.

The custom script path uses the same native fields.

1. `backend/internal/service/account_quota_script.go:206-255` maps each script window into `UsageProgress`.
2. The same function parses optional RFC 3339 `reset_at`, stores it in `ResetsAt`, and computes `RemainingSeconds`.
3. `AccountUsageCell.vue:692-697` sends `AccountUsageInfo` to `UpstreamQuotaUsage.vue` for saved account reads.
4. `QuotaScriptEditor.vue:105` sends inline test results to the same component.

`UsageProgress.resets_at` already exists at `frontend/src/types/index.ts:1397-1401`.
Key rate limits and custom results already serialize this native timestamp.
The later approved subscription mapping addresses the omitted weekly anchor.

### Native UI comparison

`UsageProgressBar.vue:36-60` is the native renderer for account quota periods.
It already shows the countdown inline in the existing reset-time `<span>` and receives `resetsAt` from every quota provider.
It does not show the absolute reset instant. Its existing `title` attribute is a category label that falls through to the root element.

`AccountStatusIndicator.vue:94-136` is the native reset-time precedent outside the bar.
It keeps a short countdown inline in the status badge and shows the exact date and time in a `group relative` hover tooltip.
The tooltip copies the existing classes at lines 123-135 and uses `formatDateTimeToMinute` at lines 127-131.
No native account quota component combines a countdown and an absolute date with an HTML `title`.

The closest account-usage implementation must therefore copy this existing group-hover tooltip pattern into the reset-time group.
Do not describe an HTML `title` as an existing native solution. The only new adaptation is the period-specific message and placement.
This preserves the existing row height, period badge, narrow layout, and all other provider cells.

### Shared Renderer Change

Change only `frontend/src/components/account/UsageProgressBar.vue` in the production patch.
Import `formatDateTimeToMinute` beside the existing `formatCompactNumber` import.
Add the native `group relative` pattern to the existing reset-time span.
Keep its font metrics and position. Use nested spans for the copied absolute tooltip and arrow:

```vue
<span v-if="shouldShowResetTime" class="group relative shrink-0 text-[10px] text-gray-400">
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

Keep `UpstreamQuotaUsage.vue` unchanged. It already passes `window.progress.resets_at` to `UsageProgressBar` for default results and script previews.
Keep the existing root `title` passed by `UpstreamQuotaUsage.vue` as the upstream-quota category tooltip.
The copied tooltip gives the exact local date and time on hover, while `formatResetTime` keeps the current countdown and expired behavior.
Reuse the existing `dashboard.platformQuota.resetsAt` locale key from `frontend/src/i18n/locales/en/dashboard.ts:30` and `zh/dashboard.ts:30`.
Do not add a visible date row, new tooltip classes, new i18n key, API field, date setting, or quota request.

### Date and time behavior

`formatDateTimeToMinute` at `frontend/src/utils/format.ts:155-171` delegates to `formatDate`.
`formatDate` at lines 102-122 calls `new Date(value)` and `Intl.DateTimeFormat(getLocale(), options)`.
The default options show year, two-digit month, two-digit day, 24-hour hour, and minute.
The browser local time zone controls the displayed wall time because no explicit `timeZone` option exists.
The active application locale controls ordering and separators through `getLocale()`.
The tooltip text is local and readable. The source `resetsAt` value remains the original RFC 3339 instant.
Invalid or absent values render no date because `formatDate` returns an empty string, while backend validation already rejects invalid script timestamps.

### Default subscription limitation

The v0.2.18 subscription response exposes usage, limits, `weekly_window_start`, and `expires_at`, but omits complete reset instants.
The user later accepted weekly start plus seven days, with a code comment about the simplified calculation.
Key and subscription expiry now set native account expiration, using the earlier available date.
Daily and monthly reset dates remain absent. The rejected upstream producer change remains removed.

### Existing test evidence

The existing backend evidence covers the source timestamp and countdown.
`plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go:28,51-54` asserts the `rate only` timestamp and 3600-second countdown.
`plugins/sub2api-quota-extension/tests/test_quota_script_test.go:39-50` asserts custom `reset_at` mapping and a positive countdown.
The existing `test_quota_editor.test.ts` already renders `UpstreamQuotaUsage` for inline results through `QuotaScriptEditor.vue:105`.
The native display case in `test_usage_cell.test.ts:28-58` can own the new tooltip assertions for the shared renderer.
Use [Reset Date Code Changes](../implement.md#reset-date-code-changes) as the single execution and validation plan.

## Files Found

| Path | Role |
| --- | --- |
| `backend/internal/service/account_upstream_quota.go` | Default response decoding and native reset mapping |
| `backend/internal/service/account_quota_script.go` | Custom script result validation and reset mapping |
| `backend/internal/service/account_usage_service.go` | Shared saved-account dispatch |
| `frontend/src/components/account/AccountUsageCell.vue` | Saved account usage owner |
| `frontend/src/components/account/QuotaScriptEditor.vue` | Inline test result owner |
| `frontend/src/components/account/UpstreamQuotaUsage.vue` | Shared quota renderer that already passes reset timestamps |
| `frontend/src/components/account/UsageProgressBar.vue` | Native countdown owner to receive the copied reset tooltip |
| `frontend/src/types/index.ts` | Existing `UsageProgress.resets_at` type |
| `frontend/src/utils/format.ts` | Existing locale-aware local date/time formatter |
| `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts` | Existing frontend display test owner |
| `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go` | Existing default timestamp test owner |
| `plugins/sub2api-quota-extension/tests/test_quota_script_test.go` | Existing custom timestamp test owner |

## Related Specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/frontend/index.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/tasks/10-26-apikey-quota-scripts/design.md`
- `.trellis/tasks/10-26-apikey-quota-scripts/implement.md`

## Caveats / Not Found

- The upstream subscription response cannot provide complete reset dates with the fields exposed by v0.2.18.
- The rejected upstream change remains removed. The later approved local mapping is specified in the current design.
- The Playwright tooltip inspection passed for supplied timestamps. It does not establish that default detection supplies those timestamps.
