# Quota Scheduling & Probe Memoization Research

- **Task**: `.trellis/tasks/11-08-quota-scheduling-and-probe-memo`
- **Date**: 2026-11-08
- **Scope**: Read-only investigation of Sub2API `v0.2.20` scheduling/quota architecture and `plugins/sub2api-quota-extension` (`patches/quota-extension.patch`, `tests/*`, `.trellis/spec/backend/api-key-quota.md`).

---

## 1. Files Inspected

| Path | Description |
| --- | --- |
| `plugins/sub2api-quota-extension/patches/quota-extension.patch` | Current quota extension patch on Sub2API `v0.2.20` (default `/v1/usage` probing, custom Goja quota scripts, expiry sync, Vue usage cells/editor) |
| `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go` | Go unit tests for `parseUpstreamQuota`, `fillUpstreamAPIKeyUsage`, `GetUsage`, and `GetUsageBatch` |
| `plugins/sub2api-quota-extension/tests/test_quota_script_test.go` | Go unit tests for `ExecuteQuotaScript`, validation, redaction, timeout/cancellation, and `quota_script` dispatch |
| `plugins/sub2api-quota-extension/tests/test_quota_script_handler_test.go` | Gin handler tests for `POST /api/v1/admin/accounts/quota-script/test` |
| `plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts` | Vitest suite for `AccountUsageCell.vue` rendering, batch/single loading, and `buildAPIKeyUsageRefreshKey` invalidation |
| `.trellis/spec/backend/api-key-quota.md` | Current specification for API-key account usage and custom quota scripts |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/account.go` | Core `Account` domain struct (`service.Account`), `IsSchedulable()`, `SupportsAccountQuota()`, `IsQuotaExceeded()` (note: `domain/account.go` does not exist in `v0.2.20`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/antigravity_quota_scope.go` | `IsSchedulableForModel` and `IsSchedulableForModelWithContext` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/account_scheduling_threshold_eval.go` | Per-platform window utilization threshold evaluator (`EvaluateAccountSchedulingThreshold`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/account_scheduling_threshold_reason.go` | Structured JSON reason builder/parser for `temp_unschedulable_reason` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/ratelimit_service.go` | `ApplyAccountSchedulingThreshold`, `HandleUpstreamError`, `ClearRateLimit`, `ClearTempUnschedulable`, `RecoverAccountState` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/ratelimit_cn_providers.go` | Reactive 403/429 balance and window cooldown handling for CN providers / OpenCode Go |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/cn_provider_balance_check_service.go` | Periodic balance/quota check service using `SetTempUnschedulable` and reason-prefix-matched `ClearTempUnschedulable` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/command_code_usage.go` | Command Code usage/credits probe and `clearCommandCodeWindowCooldown` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/cline_usage.go` | Cline usage/credits probe and per-wallet model rate limit cooldowns |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/gateway_scheduling.go` | Anthropic/Gemini/Antigravity candidate listing (`listSchedulableAccounts`), threshold filtering, and quota gates |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/openai_gateway_scheduling.go` | OpenAI-compatible candidate listing, `isOpenAICompatibleAccountEligibleForRequestBeforeProfit`, `shouldAutoPauseOpenAIAccountByQuota`, `shouldAutoPauseGrokAccountByQuota` |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/openai_account_scheduler.go` | Advanced OpenAI scheduler (`selectByLoadBalance`, sticky session checks) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/gemini_messages_compat_service.go` | Gemini native/compat scheduling and `IsSchedulableForModelWithContext` checks |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/account_usage_service.go` | `AccountUsageService` (`GetUsage`, `GetUsageForAccount`, `GetUsageBatch`, `UsageCache`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/upstream_billing_probe.go` | `UpstreamBillingProbeService` (`/v1/sub2api/billing` periodic/manual probe, `unsupported` status, `upstreamBillingProbeTargetIsOfficialAPI`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/openai_apikey_responses_probe.go` | `ProbeOpenAIAPIKeyResponsesSupport` (`accounts.extra.openai_responses_supported` capability memoization) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/service/admin_account.go` | `CreateAccount`, `UpdateAccount`, `UpdateAccountExtra`, `BulkUpdateAccounts`, `DuplicateAccount`, probe identity invalidation |
| `/tmp/sub2api-v0.2.20-base/backend/internal/repository/account_repo.go` | SQL/Ent persistence (`schedulableAccountsQuery`, `SetTempUnschedulable`, `ClearTempUnschedulable`, `SetRateLimited`, `UpdateExtra`, `BulkUpdate`, `lockAndMergeAccountProbeExtra`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/repository/scheduler_cache.go` | Redis scheduler snapshot projection (`buildSchedulerMetadataAccount`, `filterSchedulerCredentials`, `filterSchedulerExtra`) |
| `/tmp/sub2api-v0.2.20-base/backend/internal/handler/dto/mappers.go` | `AccountFromServiceShallow` and `redactAccountManagedExtra` |
| `/tmp/sub2api-v0.2.20-base/frontend/src/components/account/AccountStatusIndicator.vue` | Admin table status badge rendering (`isRateLimited`, `isOverloaded`, `isTempUnschedulable`, `isQuotaExceeded`) |

---

## 2. Official Sub2API `v0.2.20` Scheduling & Quota Mechanisms

### 2.1 How `Account` Schedulability Is Decided Across Layers

*(Note: In Sub2API `v0.2.20`, the `Account` domain type is defined in `backend/internal/service/account.go:24-89`, not in `internal/domain/`.)*

Sub2API enforces account schedulability at four layers:

#### Layer A: Database Query Layer (`accountRepository.schedulableAccountsQuery` & `queryAccountsByGroup`)
- **Locations**:
  - `backend/internal/repository/account_repo.go:2068-2079` (`schedulableAccountsQuery`)
  - `backend/internal/repository/account_repo.go:2172-2281` (`ListSchedulableByPlatform`, `ListSchedulableByPlatforms`, `ListSchedulableUngroupedByPlatform`, etc.)
  - `backend/internal/repository/account_repo.go:3367-3391` (`queryAccountsByGroup`)
- **SQL Predicates**:
  1. `deleted_at IS NULL`
  2. `status = 'active'` (`service.StatusActive`)
  3. `schedulable = true`
  4. `temp_unschedulable_until IS NULL OR temp_unschedulable_until <= now` (`tempUnschedulablePredicate()`)
  5. `expires_at IS NULL OR expires_at > now OR auto_pause_on_expired = false` (`notExpiredPredicate(now)`)
  6. `overload_until IS NULL OR overload_until <= now`
  7. `rate_limit_reset_at IS NULL OR rate_limit_reset_at <= now`
- JSONB fields inside `accounts.extra` (such as `quota_limit`/`quota_used` or window utilization) are **not** filtered in SQL; they are evaluated in memory after loading from DB or Redis scheduler snapshots.

#### Layer B: Redis Scheduler Snapshot Cache (`SchedulerSnapshotService` & `schedulerCache`)
- **Locations**:
  - `backend/internal/service/scheduler_snapshot_service.go:211-300` (`ListSchedulableAccounts`, `GetAccount`)
  - `backend/internal/repository/scheduler_cache.go:1157-1364` (`buildSchedulerMetadataAccount`, `filterSchedulerCredentials`, `filterSchedulerExtra`)
- **Projection Mechanics**:
  - Candidate lists read `sched:meta:<id>` (projected by `buildSchedulerMetadataAccount` at `scheduler_cache.go:1157-1187`).
  - All first-class `Account` columns (`Status`, `Schedulable`, `ExpiresAt`, `AutoPauseOnExpired`, `RateLimitedAt`, `RateLimitResetAt`, `OverloadUntil`, `TempUnschedulableUntil`, `TempUnschedulableReason`, `SessionWindowStart`, `SessionWindowEnd`, `SessionWindowStatus`) are preserved verbatim in `sched:meta:<id>`.
  - `Extra` in `sched:meta:<id>` is **strictly whitelisted** by `filterSchedulerExtra` (`scheduler_cache.go:1268-1364`). Any `Extra` key not listed in `filterSchedulerExtra` is stripped from `sched:meta:<id>` and therefore invisible during candidate-list filtering when `SchedulerSnapshotService` is active!
  - Mutations via `SetRateLimited` (`account_repo.go:2323-2338`), `SetTempUnschedulable` (`account_repo.go:2524-2549`), `ClearTempUnschedulable` (`account_repo.go:2596-2616`), `SetSchedulable` (`account_repo.go:2730-2748`), and `BulkUpdate` (`account_repo.go:3334-3356`) enqueue `SchedulerOutboxEventAccountChanged` / `SchedulerOutboxEventAccountBulkChanged` (which rebuilds bucket membership) and call `syncSchedulerAccountSnapshot`.
  - Mutations via `UpdateExtra` (`account_repo.go:2791-2869`) check `shouldEnqueueSchedulerOutboxForExtraUpdates` (`account_repo.go:55-73`, `3024-3051`): keys matching `schedulerNeutralExtraKeyPrefixes` / `schedulerNeutralExtraKeys` only refresh `sched:acc:<id>` + `sched:meta:<id>` via `syncSchedulerAccountSnapshot`, whereas non-neutral keys also enqueue `SchedulerOutboxEventAccountChanged`.

#### Layer C: In-Memory `Account.IsSchedulable()` and `IsSchedulableForModelWithContext()`
- **`Account.IsSchedulable()`** (`backend/internal/service/account.go:194-215`):
  ```go
  func (a *Account) IsSchedulable() bool {
      if !a.IsActive() || !a.Schedulable {
          return false
      }
      now := time.Now()
      if a.AutoPauseOnExpired && a.ExpiresAt != nil && !now.Before(*a.ExpiresAt) {
          return false
      }
      if a.OverloadUntil != nil && now.Before(*a.OverloadUntil) {
          return false
      }
      if a.RateLimitResetAt != nil && now.Before(*a.RateLimitResetAt) {
          return false
      }
      if a.TempUnschedulableUntil != nil && now.Before(*a.TempUnschedulableUntil) {
          return false
      }
      if a.SupportsAccountQuota() && a.IsQuotaExceeded() {
          return false
      }
      return true
  }
  ```
- **`Account.SupportsAccountQuota()` & `Account.IsQuotaExceeded()`** (`backend/internal/service/account.go:1436-1447`, `3074-3106`):
  - `SupportsAccountQuota()` returns `true` for `AccountTypeAPIKey`, `AccountTypeBedrock`, and `AccountTypeServiceAccount`.
  - `IsQuotaExceeded()` checks local counter limits in `account.Extra`:
    - Total quota: `quota_limit > 0 && quota_used >= quota_limit` (`account.go:3076-3078`)
    - Daily quota: `quota_daily_limit > 0 && !expired && quota_daily_used >= quota_daily_limit` (`account.go:3080-3091`)
    - Weekly quota: `quota_weekly_limit > 0 && !expired && quota_weekly_used >= quota_weekly_limit` (`account.go:3093-3104`)
- **`Account.IsSchedulableForModelWithContext()`** (`backend/internal/service/antigravity_quota_scope.go:37-52`):
  - Calls `a.IsSchedulable()`, then checks `a.isModelRateLimitedWithContext(ctx, requestedModel)` (`backend/internal/service/model_rate_limit.go:17-34`, `179-215`), which reads `account.Extra["model_rate_limits"]` and `account.Extra["antigravity_quota_scopes"]`.

#### Layer D: Gateway Candidate Filtering & Admission
- **`GatewayService` (Anthropic, Gemini, Antigravity)**:
  - `listSchedulableAccounts` (`backend/internal/service/gateway_scheduling.go:1014-1123`) filters candidates through `s.filterAccountsBySchedulingThreshold(ctx, accounts)` (`gateway_scheduling.go:1551-1571`) -> `rateLimitService.ApplyAccountSchedulingThreshold(ctx, account)`.
  - Candidate selection (`gateway_scheduling.go:288-329`, `357-368`, `564-580`, `1161-1173`, `1325-1330`) checks `account.IsSchedulable()`, `account.IsSchedulableForModelWithContext(ctx, requestedModel)`, and `isAccountSchedulableForQuota` (`!account.IsQuotaExceeded()`).
- **`OpenAIGatewayService` & `defaultOpenAIAccountScheduler` (OpenAI, Grok, Kimi, Zhipu, DeepSeek, MiniMax, OpenCode Go, TypeSafe, Command Code, Cline)**:
  - `listSchedulableAccounts` (`backend/internal/service/openai_gateway_scheduling.go:1505-1535`) filters candidates through `s.filterOpenAIAccountsBySchedulingThreshold(ctx, accounts)` (`openai_gateway_scheduling.go:1706-1726`) -> `rateLimitService.ApplyAccountSchedulingThreshold(ctx, account)`.
  - `selectByLoadBalance` (`backend/internal/service/openai_account_scheduler.go:1449-1452`), sticky session selection (`openai_account_scheduler.go:534`), `isOpenAICompatibleAccountEligibleForRequestBeforeProfit` (`openai_gateway_scheduling.go:407-442`), and `recheckSelectedOpenAIAccountFromDBBeforeProfit` (`openai_gateway_scheduling.go:1613-1663`) check `account.IsSchedulableForModelWithContext(ctx, requestedModel)`, `shouldAutoPauseOpenAIAccountByQuota`, `shouldAutoPauseGrokAccountByQuota`, and `isOpenAIAccountBlockedBySchedulingThreshold`.
- **`GeminiMessagesCompatService`**:
  - `listSchedulableAccountsOnce` (`backend/internal/service/gemini_messages_compat_service.go:458-477`) and `isAccountUsableForRequestWithPrecheck` (`gemini_messages_compat_service.go:272-274`) check `account.IsSchedulableForModelWithContext(ctx, requestedModel)`.

---

### 2.2 How Native Features Pause and Resume Scheduling on Quota Exhaustion & Recovery

Sub2API `v0.2.20` uses four native mechanisms to pause and recover accounts when quota/balance is exhausted:

1. **`SetTempUnschedulable` + Reason-Prefix-Matched `ClearTempUnschedulable` (Used by `CNProviderBalanceCheckService` & `CommandCode`)**:
   - **Pause**: In `CNProviderBalanceCheckService.applyBalanceResult` (`backend/internal/service/cn_provider_balance_check_service.go:329-345`), when balance is below threshold (or `!result.Available`):
     - Guards with `if !account.IsSchedulable() { return cnBalanceNoChange }` so it never overwrites an existing pause reason from another subsystem (`cn_provider_balance_check_service.go:335-337`).
     - Calls `s.accountRepo.SetTempUnschedulable(ctx, account.ID, time.Now().Add(s.cooldown()), reason)` where `reason` starts with `cnBalanceLowReasonPrefix` (`"cn_balance_low"`).
     - Reactive 402/429 in `RateLimitService.handleCNProviderInsufficientBalance` (`backend/internal/service/ratelimit_cn_providers.go:208-232`) also calls `s.notifyAccountSchedulingBlocked(account, until, "cn_insufficient_balance")` and `s.accountRepo.SetTempUnschedulable(ctx, account.ID, until, msg)`.
   - **Recovery**: When a subsequent check sees healthy balance (`cn_provider_balance_check_service.go:347-355` or `clearCommandCodeWindowCooldown` at `command_code_usage.go:347-362`):
     - Checks `if account.TempUnschedulableUntil != nil && strings.HasPrefix(account.TempUnschedulableReason, cnBalanceLowReasonPrefix)` (only clearing its own pause reason!).
     - Calls `s.accountRepo.ClearTempUnschedulable(ctx, account.ID)`, which sets `temp_unschedulable_until = NULL, temp_unschedulable_reason = NULL`, enqueues `SchedulerOutboxEventAccountChanged`, and syncs the Redis scheduler snapshot (`account_repo.go:2596-2616`).
   - **Important `SetTempUnschedulable` SQL constraint** (`backend/internal/repository/account_repo.go:2524-2533`):
     - `SetTempUnschedulable` has `WHERE id = $3 AND deleted_at IS NULL AND (temp_unschedulable_until IS NULL OR temp_unschedulable_until < $1)`. It only extends `temp_unschedulable_until` if the new `until` is later than the current `temp_unschedulable_until`.

2. **Window Reset Cooldown via `SetTempUnschedulable` or `SetRateLimited` (Used by `ApplyAccountSchedulingThreshold` & CN Coding Plan 429/403)**:
   - `ApplyAccountSchedulingThreshold` (`backend/internal/service/ratelimit_service.go:165-229`) and `EvaluateAccountSchedulingThreshold` (`backend/internal/service/account_scheduling_threshold_eval.go:33-77`) evaluate window utilization against configured thresholds (`< 100%`) when a future reset timestamp `until > now` is known.
   - When triggered, it sets `TempUnschedulableUntil = decision.Until` (the window's `ResetsAt`) and `TempUnschedulableReason` to a JSON payload with `source: "account_scheduling_threshold"` (`account_scheduling_threshold_reason.go:59-83`).
   - Similarly, `cooldownCNProviderToQuotaSnapshotReset` (`ratelimit_cn_providers.go:302-318`) calls `s.accountRepo.SetRateLimited(ctx, account.ID, *until)` with the earliest future window reset time.
   - **Recovery**: Automatically resumes as soon as `now >= until` (both in SQL predicates and in `Account.IsSchedulable()`).

3. **In-Memory `Extra` Evaluation in `Account.IsSchedulable()` (Used by Local `IsQuotaExceeded()`)**:
   - `Account.IsSchedulable()` (`backend/internal/service/account.go:211-213`) calls `a.SupportsAccountQuota() && a.IsQuotaExceeded()`.
   - `IsQuotaExceeded()` (`account.go:3074-3106`) checks `quota_limit`/`quota_used`, `quota_daily_limit`/`quota_daily_used`, and `quota_weekly_limit`/`quota_weekly_used` directly from `account.Extra`.
   - Because `filterSchedulerExtra` (`repository/scheduler_cache.go:1280-1293`) includes `quota_*` keys in `sched:meta:<id>`, `account.IsSchedulable()` blocks scheduling across all gateways without modifying `schedulable` or `temp_unschedulable_until`.
   - Admin UI `AccountStatusIndicator.vue:287-295`, `330-332`, `350` checks `isQuotaExceeded` only from the local `quota_used`/`quota_limit`, `quota_daily_used`/`quota_daily_limit`, and `quota_weekly_used`/`quota_weekly_limit` DTO fields, whereas `isTempUnschedulable` (`AccountStatusIndicator.vue:276-280`, `324-326`) and `isRateLimited` (`AccountStatusIndicator.vue:179-182`) render directly from `temp_unschedulable_until` and `rate_limit_reset_at`.

4. **Account Expiration (`ExpiresAt` + `AutoPauseOnExpired` + `AccountExpiryService`)**:
   - `Account.IsSchedulable()` (`account.go:199-201`) and `notExpiredPredicate(now)` (`account_repo.go:2074`) immediately block scheduling when `a.AutoPauseOnExpired && a.ExpiresAt != nil && !now.Before(*a.ExpiresAt)`.
   - In addition, `AccountExpiryService` (`backend/internal/service/account_expiry_service.go:59-71`) runs every minute and executes `AutoPauseExpiredAccounts` (`account_repo.go:2750-2789`), which permanently updates `SET schedulable = FALSE` for rows where `schedulable = TRUE AND auto_pause_on_expired = TRUE AND expires_at <= $1`.

---

### 2.3 How `quota-extension.patch` Currently Handles `UsageInfo` and Why Full-Quota Accounts Do Not Pause Scheduling

*(Note on naming: The prompt refers to `getDefaultAPIKeyUsage` and `SyncAccountExpiryFromUsage`; in the current `quota-extension.patch`, those responsibilities live in `parseUpstreamQuota` + `fillUpstreamAPIKeyUsage` in `backend/internal/service/account_upstream_quota.go`.)*

1. **Current `UsageInfo` Mapping in `quota-extension.patch`**:
   - **Default `/v1/usage` (`parseUpstreamQuota` & `fillUpstreamAPIKeyUsage`, `account_upstream_quota.go:50-218`, patch lines 694-863)**:
     - Parses `upstreamQuotaResponse` (`mode`: `"quota_limited"` or `"unrestricted"`, `unit`: `""` or `"USD"`, `balance`, `remaining`, `expires_at`, `quota`, `rate_limits`, `subscription`).
     - Window progress helper (`account_upstream_quota.go:67-85`): when `amount.Used != nil && amount.Limit != nil && *amount.Limit != 0` (with non-negative values), builds `&UsageProgress{Utilization: *amount.Used / *amount.Limit * 100, ResetsAt: amount.ResetAt, RemainingSeconds: ...}`.
     - In `mode == "quota_limited"` (`account_upstream_quota.go:86-110`):
       - `response.Quota` -> `usage.QuotaTotal`
       - `response.Remaining != nil && *response.Remaining >= 0` -> `usage.Balance = response.Remaining`
       - `response.RateLimits` (`"5h"`, `"1d"`, `"7d"`) -> `usage.FiveHour`, `usage.OneDay`, `usage.SevenDay`
     - In `mode == "unrestricted"` with `response.Subscription != nil` (`account_upstream_quota.go:111-132`):
       - `DailyUsed/DailyLimit` -> `usage.OneDay`
       - `WeeklyUsed/WeeklyLimit` (with `ResetAt = WeeklyWindowStart + 7*24h`) -> `usage.SevenDay`
       - `MonthlyUsed/MonthlyLimit` -> `usage.ThirtyDay`
     - In `mode == "unrestricted"` without `response.Subscription` (`account_upstream_quota.go:133-135`):
       - `usage.Balance = response.Balance`
     - Expiry synchronization (`account_upstream_quota.go:61-66`, `198-201`):
       - Picks the earlier of `response.ExpiresAt` and `response.Subscription.ExpiresAt`.
       - If `remote.ExpiresAt != nil && s.accountRepo != nil && (account.ExpiresAt == nil || !account.ExpiresAt.Equal(*remote.ExpiresAt))`, calls `s.accountRepo.BulkUpdate(ctx, []int64{account.ID}, AccountBulkUpdate{ExpiresAt: remote.ExpiresAt})`.
   - **Custom Quota Script (`ExecuteQuotaScript` & `readQuotaScriptResult`, `account_quota_script.go:51-265`, patch lines 273-487)**:
     - Maps `session` -> `usage.FiveHour`, `day` -> `usage.OneDay`, `week` -> `usage.SevenDay`, `month` -> `usage.ThirtyDay`, `total` -> `usage.QuotaTotal` (each with `Utilization = used / limit * 100` and optional RFC 3339 `ResetsAt`), and `balance` -> `usage.Balance` + `usage.BalanceUnit`.

2. **Why Full-Quota Accounts (`Balance <= 0` / `Remaining <= 0` or `Used >= Limit` / `Utilization >= 100`) Currently Do NOT Pause Scheduling**:
   - `fillUpstreamAPIKeyUsage` (`account_upstream_quota.go:198-218`) only writes `ExpiresAt` to `accountRepo.BulkUpdate`; it writes **no** scheduling state (`TempUnschedulableUntil`, `RateLimitResetAt`, `Schedulable`, or `account.Extra` quota state) when `usage.Balance <= 0` or any window has `Utilization >= 100` (`used >= limit`).
   - `ExecuteQuotaScript` (`account_usage_service.go:379-384`, `account_quota_script.go:51-132`) writes **nothing** to `accountRepo` at all.
   - `UsageInfo` is returned only to the HTTP caller (`/admin/accounts/:id/usage`, `/admin/accounts/usage/batch`, or `ChannelMonitorQuotaFetcher`) and is never inspected by `Account.IsSchedulable()`, `GatewayService`, or `OpenAIGatewayService`.
   - Additionally, `.trellis/spec/backend/api-key-quota.md:7`, `62` previously stated *"It leaves channel monitor source and local quota counters unchanged"* and *"Add no separate disable policy or scheduler"*, so scheduling integration was intentionally omitted in the earlier spec.

3. **How Usage Checks & Recovery Interact When Scheduling Is Paused**:
   - **Who triggers `GetUsage` / `GetUsageBatch` / `GetUsageForAccount`?**
     1. **Admin UI (`AccountsView.vue` / `AccountUsageCell.vue`)**: Queries usage for all eligible rows displayed in the table (`accountSupportsBatchUsage` at `AccountsView.vue:763-766`, `shouldFetchUsage` at `AccountUsageCell.vue:841-843`). **Crucially, neither function filters out unschedulable, rate-limited, or `temp_unschedulable` accounts** — paused accounts in the table are still queried on load, manual refresh, and cache expiry!
     2. **Channel Monitor (`ChannelMonitorQuotaFetcher.Fetch`)** (`channel_monitor_quota_fetcher.go:201-236`): Calls `GetUsageForAccount` for linked accounts regardless of `IsSchedulable()`.
     3. **No built-in background `/v1/usage` ticker exists in `AccountUsageService`**: Unlike `CNProviderBalanceCheckService` (which has a 10-minute background ticker) or `UpstreamBillingProbeService` (which has a 1-minute background ticker for `/v1/sub2api/billing`), `AccountUsageService` is invoked on demand (admin UI / channel monitor).
   - **Implications for Pause & Recovery Design**:
     - **Case 1: Window quota exhausted (`FiveHour`, `OneDay`, `SevenDay`, `ThirtyDay`, `QuotaTotal` with `Utilization >= 100`) WITH a future `ResetsAt` (`ResetsAt != nil && ResetsAt.After(now)`)**:
       - If paused until `ResetsAt` (e.g. via `TempUnschedulableUntil` or `RateLimitResetAt`, or an `Extra` timestamp that expires at `ResetsAt`), the account **automatically recovers at `ResetsAt`** even if no admin UI is open and no usage query is made!
       - If a usage query *does* run before `ResetsAt` and observes that the quota is no longer exhausted, it can clear the pause immediately.
     - **Case 2: Quota exhausted WITHOUT a future `ResetsAt` (e.g. `Balance != nil && *Balance <= 0`, or `QuotaTotal` / `OneDay` / `ThirtyDay` with `Utilization >= 100` and `ResetsAt == nil`, or `ResetsAt <= now`)**:
       - Because there is no known reset timestamp in the usage payload, if the account is paused (e.g. via `TempUnschedulableUntil` or an `Extra` quota-exhausted state checked in `IsSchedulable()`), recovery occurs when:
         - A subsequent usage query (`GetUsage` / `GetUsageBatch` / `GetUsageForAccount`) observes that all reported windows have `Utilization < 100` and (if reported) `Balance > 0`, and clears the quota-exhausted pause; OR
         - An admin manually clears temp-unschedulable / rate-limit / resets quota or updates the account credentials/configuration; OR
         - If `TempUnschedulableUntil` uses a bounded cooldown or if an `Extra` flag is used, note the tradeoff:
           - With `SetTempUnschedulable` + a reason prefix (e.g. `quota_exhausted` / `upstream_quota_exhausted`), `AccountStatusIndicator.vue` natively displays the warning badge and recovery time, `ClearTempUnschedulable` / `ClearRateLimit` / `ClearAccountError` natively clear it, and SQL `schedulableAccountsQuery` filters it at the DB level. However, remember `account_repo.go:2532` (`temp_unschedulable_until IS NULL OR temp_unschedulable_until < $1`): if shortening an existing pause or clearing on recovery, `ClearTempUnschedulable` must be called (only when `TempUnschedulableReason` matches our own prefix/source so other subsystems' pauses are not clobbered!).
           - Alternatively/additionally, if `Account.IsSchedulable()` checks an `Extra` key, that `Extra` key **must** be added to `filterSchedulerExtra` in `backend/internal/repository/scheduler_cache.go:1268-1364` so `SchedulerSnapshotService` candidate lists see it!
     - **Warning on `updated_at` and Frontend Refresh Loops**:
       - In `frontend/src/utils/accountUsageRefresh.ts` (`quota-extension.patch` line 1603), `buildAPIKeyUsageRefreshKey(account)` includes `updated_at: account.updated_at`.
       - In `AccountUsageCell.vue` (`quota-extension.patch` lines 1170-1178) and `AccountsView.vue` (`quota-extension.patch` lines 1679-1688), any change to `buildAPIKeyUsageRefreshKey(account)` invalidates the frontend cache and triggers `requestParentBatchUsage({ force: true })`!
       - Therefore, any DB write performed during `getUsageForAccount` (such as pausing/unpausing scheduling or persisting probe state) **must be strictly idempotent** (skipping DB writes when the state is already paused with the same state/reason or already unpaused), otherwise `AccountsView.vue` auto-refresh (every 5–30s) will see a new `updated_at`, which will trigger another `GetUsageBatch(force=true)`, which would write to DB again in an infinite loop!

---

## 3. Probe-to-Scheduling Pipelines in Official Sub2API `v0.2.20`

1. **`CNProviderBalanceCheckService` (`cn_provider_balance_check_service.go:101-357`)**:
   - Writes `<provider>_balance_*` to `account.Extra`. When `!result.Available` or all balances `< threshold` and `account.IsSchedulable()`, calls `accountRepo.SetTempUnschedulable(ctx, id, now+cooldown, "cn_balance_low: ...")`. When balance recovers and `TempUnschedulableReason` has prefix `"cn_balance_low"`, calls `accountRepo.ClearTempUnschedulable(ctx, id)`.
2. **`CNProviderQuotaService` (`cn_provider_quota_service.go:97-281`) & `OpenAIQuotaService` (`openai_quota_service.go:167-235`)**:
   - Write `<provider>_{5h,weekly,monthly}_{used_percent,reset_at}` / `codex_{5h,7d}_{used_percent,reset_at}` to `account.Extra`.
   - `GatewayService.listSchedulableAccounts` (`gateway_scheduling.go:1018`) and `OpenAIGatewayService.listSchedulableAccounts` (`openai_gateway_scheduling.go:1512`) call `RateLimitService.ApplyAccountSchedulingThreshold` (`ratelimit_service.go:165-229`) -> `EvaluateAccountSchedulingThreshold` (`account_scheduling_threshold_eval.go:33-77`), which pauses the account until `reset_at` when `used_percent >= threshold` and `reset_at > now`.
3. **See also**: `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/research/probe-memoization.md` for `/v1/usage` probe memoization and `upstreamBillingProbeAccountRepo` test fixture details.

