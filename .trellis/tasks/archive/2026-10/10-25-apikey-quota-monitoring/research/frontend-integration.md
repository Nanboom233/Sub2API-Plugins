# Frontend Account Usage Integration

## Source

Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.
Local checkout: `/tmp/sub2api-native-tests.2lIzJP/vet-source`.

## Existing Display and Fetch Owners

`frontend/src/components/account/AccountUsageCell.vue` owns the existing account-list usage cell.
Its API-key branch already shows local request statistics and optional locally configured quota bars at lines 618-697.
Those bars read `account.quota_*`, not the upstream key's actual balance.
Keep them intact when adding remote quota data.

`AccountUsageCell.vue:794-804` routes `isMultiProtocolApiKeyPlatform(account.platform)` into the `showUsageWindows` branch at lines 441-476.
This task leaves that branch unchanged.

The component's `shouldFetchUsage` at lines 806-823 permits OAuth and selected Gemini cases, but excludes ordinary API-key accounts.
`AccountsView.vue:765-774` repeats eligibility for desktop batch requests.
Both conditions gain one check: type `apikey` with a non-empty `credentials.base_url` on standard-cell platforms.
Exclude multi-protocol platforms from the new check because their native cells do not render the mapped result.
The backend keeps the official-domain rule, so the frontend needs no domain list.
`frontend/src/types/index.ts:1455-1505` defines `AccountUsageInfo`. It already has `five_hour`, `seven_day`, `thirty_day`, `error`, and `error_code`.
It gains only optional `one_day`, `quota_total`, and `balance`.
`frontend/src/api/admin/accounts.ts:378-399` already exposes single and batch usage requests with unchanged paths.

## Refresh Behavior to Reuse

- `AccountUsageCell.vue:1454-1490` uses a five-minute cache and the existing request queue.
- Desktop instances delegate to the parent batch queue. Mobile instances load when their rows enter the viewport.
- `AccountsView.vue:746-755` owns batch state, a five-minute cache, and pending IDs.
- `AccountsView.vue:809-840` rejects obsolete per-account batch results through request tokens.
- `AccountUsageCell.vue:1729-1745` handles the existing manual-refresh token and bypasses cached data.
- `AccountsView.vue:1522-1525` increments that token after the user refreshes the list.

The list's ordinary automatic refresh updates account rows and local daily statistics.
It does not force a new upstream usage query on every tick (`AccountsView.vue:1503-1514`).
Extending this feature does not require a new timer or background service.

## Minimal Display Change

The goal is the smallest diff to native code, not a new look.
Add the remote fields after the native local quota bars at `AccountUsageCell.vue:671-690`. Use only existing elements:

- `UsageProgressBar` with labels `5h`, `1d`, `7d`, `30d`, and `total`, as native branches already use them (lines 44-60, 384-401, 671-690).
- The balance text style from `CNProviderBalanceCell.vue:5-11` for `balance`.
- The native error line from `AccountUsageCell.vue:40-42` for `usageInfo.error`.

Keep the native no-data placeholder at line 694 when no local or visible remote data exists.
An empty response does not hide it. A zero balance counts as visible remote data.
Remote and local bars can share labels such as `total`.
Pass a `title` to each remote bar and the balance text, as the native Grok `24h` bar does at line 373.
`UsageProgressBar` declares no `title` prop, so Vue applies it to the root element.
This adds one i18n key, `admin.accounts.usageWindow.upstreamQuota`, in `zh` and `en`.
Do not derive a percentage from an amount that has no reported limit.
Add no chips, badges, dividers, labels, or styles.

## Existing Validation Tools

The frontend already uses Vitest, Vue Test Utils, jsdom, vue-tsc, and Vite.
Relevant existing suites include `AccountUsageCell.spec.ts`, `UsageProgressBar.spec.ts`, and account-list usage tests.
Reuse that runtime for affected rendering behavior.
All newly added plugin test cases and support files must remain under its flat `tests/` directory.
