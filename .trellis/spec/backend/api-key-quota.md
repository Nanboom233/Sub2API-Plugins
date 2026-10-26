# API Key Account Usage

## 1. Scope / Trigger

The `sub2api-quota-extension` plugin adds upstream quota to the existing account-management usage column on Sub2API v0.2.18.
It does not change channel monitor source, local quota counters, or account scheduling.
The frontend uses native progress bars and balance text. Upstream quota failures remain silent.

Owner: [production patch](../../../plugins/sub2api-quota-extension/patches/quota-extension.patch).

## 2. Signatures

Keep the existing administrator routes:

```text
GET  /admin/accounts/:id/usage
POST /admin/accounts/usage/batch
```

`AccountUsageService` uses the configured account key to request upstream `GET /v1/usage` with Bearer authentication.
Keep existing constructor callers usable. Supply shared transport and config through the production provider and generated Wire caller.

## 3. Contracts

Map amounts into the native usage response:

| Upstream data | Native field |
| --- | --- |
| Key 5h window | `five_hour` |
| Key 1d window or subscription daily | Optional `one_day` |
| Key 7d window or subscription weekly | `seven_day` |
| Subscription monthly | `thirty_day` |
| Key total quota | Optional `quota_total` |
| Wallet balance or key remaining, USD | Optional `balance` |
| Query failure | No quota fields or user-visible quota error description |

Create progress only when reported used and a positive limit are available. Calculate utilization as `used / limit * 100`.
Rate-only windows do not require top-level `remaining` or `unit`.
Keep zero amounts present and omitted amounts absent. Ignore the subscription `remaining: -1` sentinel, plan names, and expiry for display.
Do not multiply reported amounts again. Key remaining does not expose the underlying wallet balance.

The backend reads custom API-key targets independently of the billing probe's switch or result.
Reuse official-domain and adaptive-target selection. Preserve native Gemini, Antigravity, and Grok results and errors.
Malformed nonempty URLs must reach URL validation rather than the official-target shortcut.

Reuse configured URL policy, proxy, header overrides, transport profile, and TLS profile.
Disable redirects. Use the existing ten-second probe timeout and bounded response-body read.
Do not log response bodies or credentials.

The frontend adds general usage requests only for standard-cell API-key platforms with a nonempty `base_url`.
Keep multi-protocol native eligibility and cells intact. Preserve existing cache, batch, lazy-load, and manual-refresh paths.
Use `admin.accounts.usageWindow.upstreamQuota` as the native title on remote bars and balance text.
Keep the native placeholder when no local or visible remote data exists. Zero balance counts as visible data.

## 4. Validation & Error Matrix

| Condition | Result |
| --- | --- |
| Recognized mode without usable fields | No mapped fields and no query error |
| HTTP, timeout, transport, or body-read failure | No mapped quota fields, added `error`, or added `error_code` |
| Invalid response, URL-policy rejection, or account setup failure | No mapped quota fields, added `error`, or added `error_code` |

Remove quota error types and descriptions. Preserve response validation, request deadlines, and response-size limits.
Failed quota queries retain native errors, local statistics, and quota bars.
Do not add an upstream quota error row, toast, or explanatory placeholder.

## 5. Good / Base / Bad Cases

Good: a rate-only response maps its `used` and `limit` into the matching native window without top-level remaining.
Base: an official target returns no new remote fields and retains the native cell's empty placeholder.
Bad: an empty response hides the placeholder, or a multi-protocol cell makes an unused general quota request.

## 6. Tests Required

Use the focused cases in [the native Go suite](../../../plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go).
Cover response mapping once in the backend, including zero, omission, rate-only windows, and ignored unlimited values.
Use existing single and batch entry points to check path, authentication, silent quota failures, native errors, and per-account isolation.

Use [the native Vue suite](../../../plugins/sub2api-quota-extension/tests/test_usage_cell.test.ts) for mapped rendering, query eligibility, and refresh.
Check local information after failed queries, absence of quota error text, empty-response placeholders, and zero balances there.
Use the default build once for integration. Reuse unchanged helper, cache, installer, and composition evidence.
Review unchanged source boundaries and local quota ownership through the diff.

## 7. Wrong vs Correct

Wrong: require a successful billing declaration or a top-level remaining amount before mapping quota windows.
Correct: query usage independently and map reported window used/limit pairs into native progress fields.
