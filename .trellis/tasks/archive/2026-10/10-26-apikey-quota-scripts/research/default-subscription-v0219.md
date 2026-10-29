# Research: Default Subscription Quota Dates on v0.2.19

- Query: Determine why default API-key subscription periods have no reset dates and what the existing v0.2.19 data can support.
- Scope: Internal source research with official source references.
- Date: 2026-10-28

## Findings

### Later implementation decision

The user accepts direct addition and code comments instead of full native anchor reconstruction.
The weekly mapping is the reported weekly start plus seven days.
The user corrected the initial monthly-expiry assumption: key and subscription expiry now set native account expiration, using the earlier available date.
Subscription expiry is not a monthly reset time.
Keep the evidence below as the reason for the code comments. It does not block the accepted simplified implementation.

### The response has three different quota sources

`GET /v1/usage` selects `quota_limited` when the API key has a total quota or rate limits. It selects `unrestricted` otherwise (`backend/internal/handler/gateway_handler.go:1625-1633`).

The `quota_limited` branch emits each configured rate window with `window`, `limit`, `used`, `remaining`, and `window_start`. It emits `reset_at` only when the stored window start exists and the fixed window is not expired (`backend/internal/handler/gateway_handler.go:1724-1774`). The fixed periods are 5 hours, 1 day, and 7 days. An idle window or an expired stored window has no `reset_at` by design.

The `unrestricted` subscription branch emits `daily_usage_usd`, `weekly_usage_usd`, `monthly_usage_usd`, the three limits, `weekly_window_start`, and `expires_at` (`backend/internal/handler/gateway_handler.go:1796-1822`). It does not emit daily or monthly window starts. The wallet branch emits balance only (`backend/internal/handler/gateway_handler.go:1837-1861`).

### `/v1/usage` receives a subscription but skips maintenance

The standard API-key middleware loads the active subscription before `/v1/usage` (`backend/internal/server/middleware/api_key_auth.go:191-212`). It sets `skipBilling` for `/v1/usage` (`:166-173`). The window validation and maintenance block runs only when `skipBilling` is false (`:214-268`). The route then receives the loaded subscription in Gin context (`:270-275`).

Therefore, a usage read does not advance an expired daily, weekly, or monthly window. A later normal gateway request may advance it. The response can contain a stale persisted `weekly_window_start` while the usage request itself remains read-only.

### Parser omission before the approved implementation

Before the approved implementation, the combined parser omitted `weekly_window_start` and `expires_at` (`backend/internal/service/account_upstream_quota.go:31-38`).
It mapped subscription windows without a `ResetAt` (`:97-110`). These line references describe that research candidate.
The current parser follows the later implementation decision above.

The parser does map `rate_limits[].reset_at` for `quota_limited` responses (`backend/internal/service/account_upstream_quota.go:63-69,83-95`). It preserves the existing omission for missing or expired rate-window dates.

### Weekly start alone is not always an unambiguous reset instant

The native service has complete subscription data, including `StartsAt`, `ExpiresAt`, and all window starts (`backend/internal/service/user_subscription.go:11-27`). Its weekly display helper does not always use `WeeklyWindowStart + 7 days` (`:141-153`, `:191-197`). For a legacy subscription whose first weekly window was initialized at the start of the subscription day, it replaces that midnight anchor with the non-midnight `StartsAt` before adding seven days. The native test fixes this exact case (`backend/internal/service/user_subscription_reset_time_test.go:12-29`).

Counterexample: `StartsAt = 2026-07-31 13:37:06 +08:00` and `WeeklyWindowStart = 2026-07-31 00:00:00 +08:00`. The correct native reset is `StartsAt + 7 days`, not `WeeklyWindowStart + 7 days`. The `/v1/usage` subscription payload omits `StartsAt`, so a consumer cannot distinguish this legacy case from a genuine midnight anchor.

Daily and monthly reset dates are not present in this response. `expires_at` is the subscription end, not a daily or monthly window boundary. Period labels cannot provide the missing anchors.

### Other existing routes do not solve the API-key response contract

The user subscription progress endpoints are under the authenticated user group (`backend/internal/server/routes/user.go:129-136`) and return progress calculated from the full server-side subscription. They are not part of the API-key `/v1/usage` contract. The API-key route has no alternate authenticated header or response field that supplies `StartsAt`, daily window start, or monthly window start.

### Verified omission and limits

Verified omission: the local parser does not read `weekly_window_start`, although the existing `/v1/usage` subscription response reports it. This finding alone does not prove that `weekly_window_start + 7 days` is a valid reset date.

Verified limit: unmodified v0.2.19 does not expose enough data to calculate robust daily and monthly reset dates. It also cannot resolve the legacy weekly anchor in every case. Omitting `expires_at` from reset display is correct because it is the subscription end, not a period reset.

The earlier producer-side change was not a valid local fix. It changed the queried upstream API and required that separate server to deploy the change. It is fully rolled back.

## Research Recommendation Before the User Decision

The initial recommendation required authoritative reset anchors before adding default dates.
The user then accepted direct weekly addition with a code comment. The current design follows that decision.
Preserve `rate_limits[].reset_at`. Keep daily and monthly reset dates absent without source timestamps.
Use key and subscription expiry only for native account expiration, selecting the earlier available date.

For a robust exact date for all subscription periods, the API-key response needs additional authoritative anchors or an existing server-side progress endpoint available to that caller. That is a separate contract decision. It must not be hidden in the frontend or inferred from labels.

## Files Found

| Path | Role |
| --- | --- |
| `/tmp/sub2api-v0219-upgrade.TcfHlc/source/backend/internal/handler/gateway_handler.go` | v0.2.19 `/v1/usage` source branches and fields |
| `/tmp/sub2api-v0219-upgrade.TcfHlc/source/backend/internal/server/middleware/api_key_auth.go` | API-key subscription loading and `/v1/usage` billing skip |
| `/tmp/sub2api-v0219-upgrade.TcfHlc/source/backend/internal/service/user_subscription.go` | Native daily, weekly, and monthly reset rules |
| `/tmp/sub2api-v0219-upgrade.TcfHlc/source/backend/internal/service/user_subscription_reset_time_test.go` | Legacy weekly anchor regression evidence |
| `plugins/sub2api-quota-extension/patches/quota-extension.patch` | Local response model and subscription mapping |

## External References

- [Sub2API v0.2.19 tag](https://github.com/Wei-Shaw/sub2api/tree/v0.2.19)
- [Sub2API v0.2.19 release commit](https://github.com/Wei-Shaw/sub2api/commit/dece26153621959ccd7635814f4b2d08304e681a)
- [v0.2.19 API-key middleware](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/server/middleware/api_key_auth.go)
- [v0.2.19 subscription reset rules](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/service/user_subscription.go)
- [v0.2.19 legacy reset regression test](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/service/user_subscription_reset_time_test.go)

## Related Specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/tasks/10-26-apikey-quota-scripts/design.md`
- `.trellis/tasks/10-26-apikey-quota-scripts/implement.md`

## Caveats / Not Found

- No sanitized user `/v1/usage` payload was available. The source proves the response shape and the local drop.
- The API-key caller cannot obtain the full `UserSubscription.StartsAt` through the existing `/v1/usage` response.
- The user accepted the reported weekly anchor for the simplified display. Daily and monthly reset dates still lack source anchors.
