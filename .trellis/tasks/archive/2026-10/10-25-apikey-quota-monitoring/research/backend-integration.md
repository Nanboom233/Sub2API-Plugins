# Research: Account Usage Pipeline Integration

- Query: Where does the existing account usage flow exclude API-key accounts, and where can Sub2API `GET /v1/usage` fit?
- Scope: Internal Sub2API source and project specs.
- Date: 2026-10-25.
- Source: Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`, checkout `/tmp/sub2api-native-tests.2lIzJP/vet-source`.

## Findings

### Existing owner and exclusion

`AccountUsageService` owns account usage reads. `GetUsage` and `GetUsageForAccount` share `getUsageForAccount`. Platform-specific handlers run first. The general OAuth path requires `Account.CanGetUsage()`, which checks only `Type == oauth`. Setup Tokens use a local estimate. An API-key account that falls through those branches, including OpenAI API-key accounts, returns `account type apikey does not support usage query` (`backend/internal/service/account_usage_service.go:348-508`, `backend/internal/service/account.go:361-363`). Gemini and Grok have earlier platform branches, so the final error is not a universal API-key filter.

`GetUsageBatch` does not filter by account type. It loads accounts once, runs up to six account queries concurrently, and returns per-account errors without failing the full batch (`account_usage_service.go:511-583`). One API-key branch in `getUsageForAccount` therefore serves both single and batch routes.

The administrator already has `GET /admin/accounts/:id/usage` and `POST /admin/accounts/usage/batch`. Both call `AccountUsageService` through `AccountHandler` (`backend/internal/server/routes/admin.go:414-416`, `backend/internal/handler/admin/account_handler.go:2543-2567`, `2733-2760`). No new route is needed for this pipeline.

### Refresh and persistence behavior

Usage reads are request-driven. The account table loads eligible rows on mount, delays mobile requests until the row enters view, and sends managed reads through its batch queue. The frontend and batch caches each retain results for five minutes (`frontend/src/components/account/AccountUsageCell.vue:874-875`, `1454-1490`, `1659-1682`; `frontend/src/views/admin/AccountsView.vue:746-750`, `823-840`). There is no backend periodic runner for this account-usage route.

The backend has provider-specific cache and persistence rules. Anthropic responses use a three-minute success cache, a one-minute error cache, and singleflight. Active results update selected passive fields in account `extra`. OpenAI OAuth snapshots also use account `extra`. These paths do not define a generic persisted usage snapshot (`account_usage_service.go:107-127`, `396-449`, `674-707`, `709-749`).

`UsageInfo` has provider-specific progress fields but no direct Sub2API quota response structure (`account_usage_service.go:182-247`).
The current [design](../design.md) maps matching remote windows into these progress fields and adds only missing native slots.
Calculate utilization from reported used and limit values. Do not assign raw USD amounts to percentage fields or local account counters.
The source response contract is recorded in [api-key-quota-contract.md](./api-key-quota-contract.md).

### Remote Sub2API query and transport

Sub2API v0.2.18 exposes API-key-authenticated `GET /v1/usage`. The rate-declaration endpoint `GET /v1/sub2api/billing` is a separate capability. A valid declaration response proves that its schema is supported; it does not prove server identity. Simple mode returns 404 for the declaration, so requiring a successful rate probe would exclude a supported usage query (`backend/internal/server/routes/gateway.go:180-187`, `210`; [upstream-rate-detection.md](./upstream-rate-detection.md)).

The billing probe already reads API keys and base URLs from account credentials. It validates the URL, uses the account proxy and shared `HTTPUpstream`, applies account header overrides and TLS profiles, disables redirects, and uses the endpoint URL helper (`backend/internal/service/upstream_billing_probe.go:623-680`, `backend/internal/service/account_test_service.go:283-299`, `backend/internal/service/http_upstream_port.go:16-30`, `backend/internal/service/openai_endpoint_url.go:8-27`). `AccountUsageService` does not currently own a generic upstream HTTP transport. This is the narrow integration gap for a remote usage branch; the existing billing-probe runner is not the account-usage owner.

The API-key middleware skips billing enforcement for the exact `/v1/usage` path, including expiry and exhausted quota. It still validates the key, user, IP restrictions, and group access (`backend/internal/server/middleware/api_key_auth.go:121-172`, `191-235`). The endpoint can therefore report exhausted or expired keys, but disabled or invalid keys can still fail authentication.

The response contract has separate `quota_limited` and `unrestricted` modes. Limited responses contain key quota, spending windows, or both.
Unrestricted responses expose wallet balance or subscription limits. Missing values do not mean zero. `isValid` does not establish inference readiness.
Use the current design's native field mapping rather than adding a separate remote-observation structure.
Do not require a rate declaration or multiply reported amounts again.
Source references and response details are in [api-key-quota-contract.md](./api-key-quota-contract.md).

### Local account quota is separate

API-key accounts already support the local `quota_limit`, `quota_used`, daily, and weekly quota fields. The gateway accumulates local usage from requests served by this Sub2API instance, and `Account.IsSchedulable` excludes locally exhausted accounts (`backend/internal/service/account.go:1434-1447`, `2617-2635`, `3073-3090`; `backend/internal/service/gateway_usage_billing.go:139-140`). These fields do not represent the remote API key's wallet or quota. Remote usage monitoring should not write into them or change local scheduling behavior.

### Focused validation

`TestAccountUsageService_GetUsageBatch_BestEffortByAccount` at `backend/internal/service/account_usage_service_batch_test.go:131-190` supplies existing stubs and behavior evidence.
Its current API-key case asserts the unsupported error.
Add changed-behavior cases in the plugin's flat native test files. Do not place test edits in production patches.
The [execution plan](../implement.md) defines the focused validation and prevents duplicate acceptance runs.

## Files Found

| Path | Role |
| --- | --- |
| `backend/internal/service/account_usage_service.go` | Existing account usage owner, account-type dispatch, cache, batch reads, and provider-specific persistence. |
| `backend/internal/service/account.go` | OAuth eligibility and local API-key account quota semantics. |
| `backend/internal/handler/admin/account_handler.go` | Existing single and batch administrator handlers. |
| `backend/internal/server/routes/admin.go` | Existing usage route registration. |
| `backend/internal/service/upstream_billing_probe.go` | API-key credentials, target selection, shared transport, and separate billing-capability probe. |
| `backend/internal/service/account_test_service.go` | Base URL validation reused by the billing probe. |
| `backend/internal/service/http_upstream_port.go` | Shared upstream HTTP transport interface. |
| `backend/internal/service/openai_endpoint_url.go` | Base-path normalization for `/v1` endpoints. |
| `backend/internal/service/account_usage_service_batch_test.go` | Existing focused batch behavior test with an API-key exclusion assertion. |
| `backend/internal/handler/gateway_handler.go` | Sub2API v0.2.18 API-key usage response construction. |
| `backend/internal/server/middleware/api_key_auth.go` | API-key access checks and usage-path billing bypass. |
| `frontend/src/components/account/AccountUsageCell.vue` | On-demand account-table usage loading. |
| `frontend/src/views/admin/AccountsView.vue` | Batch request queue and frontend usage cache. |

## Related Specs

`.trellis/spec/backend/index.md` requires the smallest change boundary, owner and caller inspection, and reuse of existing helpers. `.trellis/spec/backend/database-guidelines.md` describes native `extra` update patterns but does not define remote account usage. No quota-specific project spec was found.

## Caveats / Not Found

No live account, credentials, or provider request was used. The user chose direct extension of existing detection.
Transport injection and native dispatch contracts are recorded in [integration-contracts.md](./integration-contracts.md).

External source references use the pinned Sub2API v0.2.18 commit: https://github.com/Wei-Shaw/sub2api/tree/ac1b8f1271be0d674fa6f074403c1410f30a3a81
