# Custom Quota Script Integration

## Source

The current plugin commit is `c15a45417e93b35372fcbcfdcfe8f1023c4be8cb`.
The parent work commit is `a5f792d90c07511c7abb19a4f8b9ae67faa63f03`.
The patched development source remains at `/tmp/sub2api-quota-dev.LOZjym/source`.
Its upstream baseline is Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.
No product source changed during this research.

## Existing Storage and Forms

Account create and update requests already accept `extra: map[string]any`.
The handler forwards this map to the account service.
The repository writes the resulting map through the existing account JSON field.
Custom script configuration can use this storage without a new database column.

Source anchors:

- `backend/internal/handler/admin/account_handler.go:123`: create request.
- `backend/internal/handler/admin/account_handler.go:144`: update request.
- `backend/internal/handler/admin/account_handler.go:1049`: create service call, including `Extra`.
- `backend/internal/repository/account_repo.go:517`: account update and merged extra map.

The create and edit forms already contain API-key-specific configuration.
Edit reads `props.account.extra` and constructs the update payload from existing extra values.
Any script control must preserve unrelated extra keys and clear its own configuration deliberately.
The create form has a separate Antigravity upstream path and a general API-key path.
Both must receive any shared API-key configuration.

Source anchors:

- `frontend/src/components/account/CreateAccountModal.vue:1201`: Antigravity upstream settings.
- `frontend/src/components/account/CreateAccountModal.vue:6103`: general API-key creation.
- `frontend/src/components/account/CreateAccountModal.vue:6219`: general extra construction.
- `frontend/src/components/account/CreateAccountModal.vue:6275`: shared account-create helper.
- `frontend/src/components/account/EditAccountModal.vue:2093`: API-key settings area.
- `frontend/src/components/account/EditAccountModal.vue:4328`: extra state loading.
- `frontend/src/components/account/EditAccountModal.vue:6080`: preserve other extra values when adding a field.

## Existing Quota Query and Display

`AccountUsageService.getUsageForAccount` dispatches the plugin's upstream query.
Single-account and batch usage reads reuse this function.
Batch reads already limit concurrent account operations to six.
The current plugin queries custom upstream targets and skips known official targets.
It maps valid results into native usage fields after the complete response passes validation.
Failed queries return without adding quota fields, `error`, or `error_code`.

Source anchors:

- `backend/internal/service/account_usage_service.go:355`: quota dispatch.
- `backend/internal/service/account_usage_service.go:524`: single-account usage.
- `backend/internal/service/account_usage_service.go:540`: loaded-account usage.
- `backend/internal/service/account_usage_service.go:548`: batch usage.
- `backend/internal/service/account_upstream_quota.go:117`: current quota HTTP query.

The frontend reuses the current batch queue, cache, mobile loading, and manual refresh.
The standard API-key cell renders upstream windows and balance after local quota information.
Multi-protocol API-key accounts use separate native cells and currently skip the added generic quota fetch condition.
Supporting custom scripts for these accounts requires an explicit route through their existing display branch.

Owners:

- `frontend/src/components/account/AccountUsageCell.vue`.
- `frontend/src/views/admin/AccountsView.vue`.
- `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go`.
- `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts`.

## Execution and Delivery Constraints

The native Go dependency files contain no Goja, QuickJS, or Otto runtime.
A JavaScript execution feature therefore needs an interpreter dependency or a different execution design.
The existing build sets `CGO_ENABLED=0` and produces Linux/amd64 executables.
The installer does not install Node.js, Python, or a separate script runtime in the target container.
An in-process pure Go interpreter can preserve this delivery contract.

Sources: `backend/go.mod`, `backend/go.sum`, and `scripts/build.py:104` in the parent repository.

Custom script execution should reuse account transport and URL policy when it makes HTTP requests.
The existing account usage column remains the display owner.
No new account scheduler or local quota writes are required by the user request.

## Script Test and Changed-Row Refresh

`AccountHandler` already receives `AccountUsageService`. Its `AdminService` dependency exposes `GetAccount` and `GetProxy`.
The existing model-preview handler constructs an unsaved account from request credentials.
Use this native preview pattern for script tests in both forms.
Create tests use draft connection settings. Edit tests overlay those settings on an in-memory saved-account copy.
The task design defines the request fields and overlay rules. Neither route requires another constructor dependency.

Source anchors:

- `backend/internal/handler/admin/account_handler.go:51`: handler dependencies.
- `backend/internal/handler/admin/account_handler.go:3088`: unsaved model-preview handler.
- `backend/internal/service/admin_service.go:81`: saved-account lookup.
- `backend/internal/service/admin_service.go:122`: proxy lookup.
- `frontend/src/api/admin/accounts.ts:644`: draft-preview request and API call.

The account list's `queueBatchedUsage` already supports forced per-account cache invalidation and request tokens.
`patchAccountInList` merges saved account data but does not invalidate general usage by changed script configuration.
The quota cell's current identity watcher observes account ID, platform, and type, rather than script code.
The new script feature must connect saved script changes to these existing refresh paths.

Source anchors:

- `frontend/src/views/admin/AccountsView.vue:862`: batch queue, forced cache bypass, and request token.
- `frontend/src/views/admin/AccountsView.vue:2245`: saved-account merge.
- `frontend/src/components/account/AccountUsageCell.vue:1728`: current identity watcher.

## Settled Adaptation

The user selected interaction reference only. Existing cc-switch scripts do not require compatibility.
The latest user correction requires visible custom-script errors during refresh and manual tests.
Default quota-query failures remain silent.
The revised design stores one script string. Refer to the task design for the current result proposal.
Both forms test unsaved scripts against effective draft connection settings without saving or changing list caches.
The current editor and balance-unit requirements are defined in the task design.
Use [the selected runtime research](./script-runtime.md) for interpreter APIs and limitations.
The task design defines the complete custom-script contract.

## Reset Date and Time Addition

The user requested reset dates and times while retaining countdowns for both default detection and custom scripts.
The default mapper already transfers `rate_limits[].reset_at` into native `UsageProgress.ResetsAt`.
The script runner maps optional RFC 3339 `reset_at` into the same field.
`UpstreamQuotaUsage.vue` serves both paths and inline previews. Its native `UsageProgressBar` currently shows only the countdown.
Copy the native countdown-plus-hover pattern from `AccountStatusIndicator.vue` into the existing `UsageProgressBar` reset span.
Use `formatDateTimeToMinute` and the existing `dashboard.platformQuota.resetsAt` message. Keep the shared quota renderer unchanged.

Sub2API v0.2.18 subscription output includes `weekly_window_start` and `expires_at`, but no complete period reset timestamps.
The native weekly reset calculation also uses `StartsAt` to correct a legacy anchor. The response does not supply that input.
Daily and monthly boundaries also lack sufficient response inputs. Preserve unknown reset times instead of reconstructing them.

Source anchors in `/tmp/sub2api-quota-scripts.MSf70s/source`:

- `backend/internal/handler/gateway_handler.go:1733`: key-window `reset_at` output.
- `backend/internal/handler/gateway_handler.go:1812`: subscription output fields.
- `backend/internal/service/user_subscription.go:148`: weekly/monthly anchor correction.
- `backend/internal/service/account_upstream_quota.go:67`: existing timestamp mapping.
- `frontend/src/components/account/UsageProgressBar.vue:210`: countdown display.
- `frontend/src/utils/format.ts:155`: native date/time formatter.
