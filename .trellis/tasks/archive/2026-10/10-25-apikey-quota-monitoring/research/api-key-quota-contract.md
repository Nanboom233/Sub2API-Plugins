# API Key Quota Contract

## Source and Scope

Inspected Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.
Local source: `/tmp/sub2api-native-tests.2lIzJP/vet-source`.
Existing evaluation patches do not change the quota handler or authentication files cited below.
This report records source behavior. It uses no live provider credentials or paid inference requests.

## API Key Access

The existing interface is `GET /v1/usage` with `Authorization: Bearer <api-key>`.
It requires no user-session token or administrator token.
The native key-usage page calls this interface directly.

Sources:

- [Route and authentication](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/server/routes/gateway.go#L180).
- [Usage route](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/server/routes/gateway.go#L210).
- [Native browser caller](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/frontend/src/views/KeyUsageView.vue#L863).

Authentication still checks the key, user, IP restrictions, and group access.
The exact `/v1/usage` path skips billing enforcement, including key expiry, exhausted quota, and insufficient wallet balance.
This permits monitoring after those limits block inference.
Disabled or invalid credentials can still prevent monitoring.

Source: [API key middleware](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/server/middleware/api_key_auth.go#L121).
The bypass uses an exact path comparison at line 172.
The separate `/antigravity/v1/usage` alias does not match that comparison.

## Response Modes

The handler selects `quota_limited` when the key has a positive total quota or any positive spending-window limit.
Otherwise, it selects `unrestricted`.

| Mode | Returned information | Meaning and limits |
| --- | --- | --- |
| `quota_limited`, total quota | `quota.limit`, `used`, `remaining`, `unit: USD` | Key allocation. Remaining is `max(0, limit - used)`. |
| `quota_limited`, spending windows | `rate_limits[]` for `5h`, `1d`, and `7d` | Configured key spending limits, usage, remaining amount, and available reset times. |
| `unrestricted`, wallet | `balance`, `remaining`, `unit: USD` | Both amounts contain the current user wallet balance. |
| `unrestricted`, subscription | `subscription` and `remaining` | Remaining is the smallest configured daily, weekly, or monthly remainder, bounded below by zero. |

Sources:

- [Mode selection](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/handler/gateway_handler.go#L1625).
- [Limited response](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/handler/gateway_handler.go#L1703).
- [Wallet and subscription responses](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/handler/gateway_handler.go#L1796).
- [Subscription calculation](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/handler/gateway_handler.go#L1864).

The limited response does not include the user wallet or subscription remainder.
A key with only spending-window limits has no top-level `remaining` or `unit`.
Its window amounts use USD, as defined by the [key model](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/service/api_key.go#L50).
Missing fields therefore cannot safely mean zero or unlimited.

A subscription with no configured limits returns `remaining: -1`.
A missing subscription can produce a successful response without `remaining` or `subscription`.
These states must remain distinct from exhausted quota.

The usage response can report `isValid: true` for expired or exhausted keys.
This flag confirms neither inference readiness nor positive remaining quota.

## Billing Units and Freshness

The billing command applies `ActualCost` to wallet, subscription, key quota, and key spending windows.
That cost already includes applicable billing multipliers.
Do not multiply reported quota amounts by the rate declaration again.

Source: [Billing command](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/service/gateway_usage_billing.go#L329).

Wallet mode reloads the user through `userService.GetByID`.
Key quota fields come from the authenticated key, which can come from the authentication cache.
Spending windows use a database lookup. Subscription lookup can use its own cache.
The source therefore does not establish identical freshness across all fields.

Sources:

- [Cached key lookup](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/service/api_key_service.go#L740).
- [Cached subscription lookup](https://github.com/Wei-Shaw/sub2api/blob/ac1b8f1271be0d674fa6f074403c1410f30a3a81/backend/internal/service/subscription_service.go#L742).

Spending-window lookup failure can omit `rate_limits` while retaining HTTP 200.
Optional usage statistics also fail independently of the basic response.

## Source-Derived Counterexamples

These examples follow the source branches. They are not observations from a live provider.

1. A key has USD 100 remaining, but its user wallet has USD 0.
   Limited mode returns key remaining USD 100 and hides the wallet. A normal inference request can still fail balance enforcement.
2. A key has only a 5-hour spending limit.
   The response can contain `rate_limits` without top-level `remaining`. Reading only that field loses valid quota information.
3. An unlimited subscription returns `remaining: -1`.
   Treating every negative value as exhaustion reverses its meaning.
4. An exhausted or expired key can return `isValid: true`.
   Treating that flag as inference readiness misclassifies the key.

## Recommendation

Probe quota capability independently through `/v1/usage`; do not require a successful multiplier declaration first.
Validate the returned mode and fields instead of treating HTTP 200 as a complete quota result.
Preserve key quota, spending windows, wallet balance, and subscription limits as distinct observations.
Keep missing data, unlimited values, zero remaining, authentication failures, and transport failures distinct.
The current interface cannot always reveal every constraint that limits actual spendable quota.

The current [design](../design.md) defines the displayed subset through native account usage fields.
The source facts above do not require additional fields for plan names, expiry, or the unlimited sentinel.
