# API Key Quota Extension Design

## Delivery Boundary

Remote repository creation requires explicit approval of GitHub credential use and the create operation.
The planned target is `Nanboom233/sub2api-quota-extension`, using the existing `gh` login, with public visibility.
General feature approval does not grant this separate authorization.
Attach it at `plugins/sub2api-quota-extension` through the native submodule entry.
The existing build discovers this path automatically.

The plugin owns contextual production patches, flat tests, test support, and its root license.
Use descriptive patch names in lexical order. Do not add a series file or plugin manifest.
No runtime plugin manager is needed.

## Existing Flow

```text
Account list -> existing single/batch usage API -> AccountUsageService
AccountUsageService -> shared account transport -> upstream GET /v1/usage
                    -> mapped UsageInfo fields -> existing account usage cell
```

Keep the billing declaration probe separate.
Its result and enable switch do not control quota access.

## Eligibility and Native Behavior

An eligible account uses type `apikey`, has a concrete platform, and has a configured custom upstream target.
Reuse the existing official-domain check and adaptive protocol target selection.
Known official targets and accounts without a custom target keep their native usage paths.
Malformed custom URLs reach URL validation and fail the quota query silently.

Extend the existing usage dispatch without rewriting unaffected provider branches.
For eligible accounts, preserve any native usage result and fill the mapped fields.
The current unsupported-account result does not block the new remote branch.
Remote query failure must not remove native provider data or errors, or add a quota error message.
New transport requirements apply only to the new remote query.

Do not change channel monitor eligibility, dispatch, validation, snapshots, or views.

## Transport

Supply shared `HTTPUpstream` and config through `ProvideAccountUsageService`.
Keep `NewAccountUsageService` callers under their current contract.
Update the generated Wire caller with the provider change.

Reuse the URL validator through a small shared helper extracted from the account test service.
Preserve its existing method entry point and configured URL policy.
Use the account key, selected base URL, loaded proxy, header overrides, transport profile, and TLS profile.
Use the existing endpoint URL helper, disable redirects, and bound the request with a ten-second timeout.
Read and validate a bounded response body as the billing probe does.
Do not log response bodies or credentials.

Call the configured target's `/v1/usage` endpoint. Do not retry alternate provider hosts or authentication schemes.
The exact root path has the upstream expiry/quota enforcement bypass.
A configured path prefix can change upstream routing and does not inherit that bypass automatically.

## Native Field Mapping

Reuse existing `UsageInfo` fields where the meaning matches.
Add a field only where no native slot exists.

| Remote data | `UsageInfo` field |
| --- | --- |
| Key 5h window | existing `five_hour` (`UsageProgress`) |
| Key 7d window or subscription weekly | existing `seven_day` |
| Subscription monthly | existing `thirty_day` |
| Request failure | No quota fields or user-visible quota error description |
| Key 1d window or subscription daily | new optional `one_day` (`UsageProgress`) |
| Key total quota (used / limit) | new optional `quota_total` (`UsageProgress`) |
| Wallet balance or key remaining (USD) | new optional `balance` (number) |

Fill a `UsageProgress` only when the response has both used and limit.
Map rate-only windows with both used and limit to the corresponding progress fields.
These windows do not require top-level `remaining` or `unit`.
The `remaining: -1` sentinel, plan names, and expiry produce no field.
Add the three new fields to `AccountUsageInfo` as optional TypeScript fields.

Accept optional field omissions allowed by v0.2.18.
Validate modes, field types, and numeric values.
HTTP 200 with unrelated JSON fails validation without an error message in the interface.
A recognized response without usable quota produces no field and no error.

Amounts already include applicable billing costs. Do not apply another multiplier.
Limited-key allowance is not a wallet balance and does not expose hidden wallet or subscription constraints.

HTTP, timeout, transport, decoding, and account setup failures add no quota fields, `error`, or `error_code`.
Remove the added quota error types and descriptions. Preserve native provider errors and error codes.

## Existing Account Usage Views

Change only the standard API-key branch of `AccountUsageCell.vue`.
The multi-protocol API-key branch and its CN, Ollama, and OpenCode cells stay unchanged.
Add the custom API-key condition to `shouldFetchUsage` and `accountSupportsBatchUsage` for standard-cell platforms only.
Exclude `isMultiProtocolApiKeyPlatform(account.platform)` from this new condition. Keep existing native eligibility rules.
The backend applies the official-domain check and returns an empty result for official targets.
Keep existing five-minute frontend caches, batch queues, stale-response guards, manual refresh, and mobile lazy loading.

Render the remote fields after the native local quota bars with existing elements only:

- `UsageProgressBar` for `five_hour` (`5h`), `one_day` (`1d`), `seven_day` (`7d`), `thirty_day` (`30d`), and `quota_total` (`total`).
- The `CNProviderBalanceCell.vue` balance text style for `balance`.

Do not add an upstream quota error row, toast, or explanatory placeholder.
Keep the native no-data placeholder when no local data or visible remote window or balance exists.
An empty usage response must not hide the placeholder. A zero balance counts as visible data.
Pass `:title="t('admin.accounts.usageWindow.upstreamQuota')"` to each remote `UsageProgressBar` and to the balance text.
The title falls through to the root element, as the native Grok `24h` bar already does.
Add that one i18n key to the `zh` (`上游额度`) and `en` (`Upstream quota`) account locales.
Do not add chips, badges, dividers, labels, or new styles.

## Scheduling and Local Counters

Remote readings never change account scheduling.
Remote readings never write `quota_limit`, `quota_used`, daily, or weekly local counters.

## Tests and Build

Keep backend suites in plugin `tests/test_*_test.go` with the existing native package annotation.
Keep real Vue suites in `tests/test_*.test.ts` and support files in the same flat directory.
Extend the common runner to stage native Vue suites temporarily and execute their explicit paths with native Vitest.
Use the original config, aliases, setup, and installed dependencies.
Clean temporary test files after success or failure.

Use local HTTP fixtures for remote calls and existing native stubs for batch integration.
Test source and fixtures stay out of production patches.
Keep quota parsing and mapping cases in backend tests. Frontend tests consume mapped fields without repeating the response matrix.
Check unchanged source boundaries and local quota ownership through the implementation diff.
Use the focused validation in `implement.md`. Existing cache, scheduler, transport-helper, and installer suites need no duplicate tests.
The default `python3 scripts/build.py` applies both plugins, runs tests, and builds the server and installer.
Patch failure or test failure stops publication of new outputs.
Retain the existing installer and version-warning behavior.

## Compatibility and Removal

No schema migration or new background service is required.
Existing native usage consumers keep their fields and entry points.
Removing the submodule from a later build removes the extension.
The current installer backup and restoration flow remains the recovery path for an installed build.
