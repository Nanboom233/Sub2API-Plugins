# Default Quota Time Research: v0.2.19

## Scope

Inspect the existing upstream response, plugin decoder, and native display.
The version upgrade passed build session `42194`. This document records the source before the later approved mapping changes.
Current requirements in `prd.md` and `design.md` govern weekly reset calculation and native account expiration.
The release commit is `dece26153621959ccd7635814f4b2d08304e681a`.
The local combined source is `/tmp/sub2api-v0219-upgrade.TcfHlc/source`.

## Key Limits Use Stored Window Anchors

`backend/internal/handler/gateway_handler.go:1624-1631` selects `quota_limited` when the key has a total quota or rate limits.
`usageQuotaLimited` returns key limits, not the subscription plan's limits.
Its supported rate windows are `5h`, `1d`, and `7d`. It supplies no monthly key window.

`backend/internal/service/api_key.go:18-27` defines durations of 5, 24, and 168 hours.
The stored start determines the reset. Do not substitute the browser's midnight or a calendar-week boundary.
Repository billing initializes the 5h start at database `NOW()` and the 1d/7d starts at database-day midnight.
Evidence: `backend/internal/repository/api_key_repo.go:827-853`.

| Window state | Upstream result | Current display |
| --- | --- | --- |
| Started and not expired | `window_start`, `reset_at = window_start + duration`, reported effective usage | Countdown and exact date on hover |
| Not started | Null start, no `reset_at`, zero effective usage | Bar without a reset-time area |
| Expired | Old start, no `reset_at`, zero effective usage | Bar without a reset-time area |

Evidence: `gateway_handler.go:1727-1774`, `api_key_service.go:143-165`, and `api_key.go:26-27`.
An uninitialized key window has no scheduled reset instant. Billing initializes its stored window start.
Adding a duration to the current time would invent a reset date.

## The Decoder Preserves Reported Key Times

`backend/internal/service/account_upstream_quota.go:21` decodes `reset_at` as `*time.Time`.
Lines 63-68 preserve it as `UsageProgress.ResetsAt` and calculate nonnegative remaining seconds.
Lines 88-95 map `5h`, `1d`, and `7d` into their existing native slots.
Lines 178-189 pass those progress objects to the saved account result.

The existing `TestUpstreamQuotaNativeMapping` checks a supplied reset timestamp and its 3600-second countdown.
The v0.2.19 combined build passed this case. It does not establish which response the user's upstream actually sent.

No reported key reset timestamp is discarded in this source path.
Malformed timestamp JSON causes decoding to fail. The default query then follows its existing silent-failure contract.

## The Renderer Requires a Timestamp

`frontend/src/components/account/UpstreamQuotaUsage.vue:26` passes `window.progress.resets_at` to `UsageProgressBar`.
`UsageProgressBar.vue:198-200` shows its time area when a timestamp exists.
Without a timestamp, it shows that area only when `showNowWhenIdle` is true and utilization is zero.
The upstream renderer does not set that option.
Some native OpenAI and Grok cells do set it. Their idle windows can show the native `usage.resetNow` text.

This is a concrete display difference. It does not justify inventing an absolute time for every zero-use quota window.
Subscription windows with unknown reset times must not inherit key-window idle semantics without source evidence.

The formatter accepts the reported date and uses the browser's local timezone.
Past timestamps show native `resetPending` or `resetNow` text according to utilization.
Evidence: `UsageProgressBar.vue:204-230` and `frontend/src/utils/format.ts:102-122,155-171`.

## Local Account Quotas Are Separate

`frontend/src/components/account/AccountUsageCell.vue:1583-1645` builds local daily, weekly, and total quota bars from the account object.
Fixed local windows use `extra.quota_daily_reset_at` and `extra.quota_weekly_reset_at`.
Rolling local windows use `extra.quota_daily_start` or `extra.quota_weekly_start`, plus the configured native duration.
These values are not the remote `/v1/usage` result.
Local total quota has no periodic reset date.

## Subscription and Wallet Results

Subscription and wallet results use `unrestricted`. A wallet response contains a balance, not a quota period.
Subscription amounts reach the daily, weekly, and monthly native slots through a separate decoder branch.
Subscription `remaining` is the smallest configured period allowance, clamped to zero. Without limits, it is `-1`.
The native period bars already represent these allowances. The current mapping does not present this summary as wallet balance.
Evidence: `gateway_handler.go:1868-1910`, `calculateSubscriptionRemaining`.
Use [the subscription investigation](./default-subscription-v0219.md) for the exact exposed anchors and their limits.

## Research Conclusion and Later Decision

The rejected upstream-field change changed the service boundary and did not repair an unchanged remote server.
Keep that change removed.

The current source proves that supplied key reset timestamps reach the renderer.
It also explains blank key times for idle or expired windows, and a native idle-text difference.
It does not prove which of these cases caused the user's report.

The user later accepted weekly subscription start plus seven days, with a code comment about the simplified calculation.
The user also assigned key/subscription expiry to native account expiration, using the earlier available date.
The implementation now follows these decisions. Daily and monthly reset timestamps remain absent without source anchors.
Existing key reset timestamps retain their mapping. No deployed user response was available for this research.

## Primary Sources

- [v0.2.19 usage handler](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/handler/gateway_handler.go#L1727).
- [Native key window durations](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/service/api_key.go#L18).
- [Native effective key usage](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/service/api_key_service.go#L143).
- [Native local account quotas](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/frontend/src/components/account/AccountUsageCell.vue).

Plugin-owned decoder and renderer changes are in the local quota production patch.
