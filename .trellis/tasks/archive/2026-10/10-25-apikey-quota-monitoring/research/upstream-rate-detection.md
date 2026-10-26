# Research: upstream declared-rate detection

- Query: Does the existing upstream declared-rate probe accurately identify Sub2API before API-key quota monitoring?
- Scope: Internal source and focused local tests.
- Date: 2026-10-25.
- Source: `Wei-Shaw/sub2api` v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`, in `/tmp/sub2api-native-tests.2lIzJP/vet-source`. The checkout also contains the evaluation plugin patches. The billing producer and probe code are upstream source.

## Findings

### What the probe verifies

The UI calls this value `上游声明倍率` and warns that the upstream site supplies it. Sub2API cannot verify that it matches actual charges. A provider or intermediary can return false, stale, or altered values (`frontend/src/i18n/locales/zh/admin/accounts.ts:184-190`).

The probe is eligible for API-key accounts on any concrete platform. Eligibility does not assert that the provider is Sub2API (`backend/internal/service/upstream_billing_probe.go:999-1017`). For non-OpenAI platforms, known official provider domains and empty base URLs are classified unsupported without a request. OpenAI accounts with no base URL probe `api.openai.com` (`backend/internal/service/upstream_billing_probe.go:623-643`, `1019-1071`).

For other configured targets, the probe requests `GET <base-url>/v1/sub2api/billing`, authenticates with the configured account key, disables redirects, and uses a ten-second timeout (`backend/internal/service/upstream_billing_probe.go:659-680`). A 404 or 405 becomes `unsupported`. Other non-2xx responses become `failed` (`backend/internal/service/upstream_billing_probe.go:695-703`).

The response parser requires `object: "sub2api.key_billing"`, schema version `1`, token billing scope, required rate fields, valid timestamps, and consistent resolved/effective multipliers (`backend/internal/service/upstream_billing_probe.go:805-839`, `853-880`). These checks validate the endpoint contract.

### The v0.2.18 producer matches that contract

The upstream registers `GET /v1/sub2api/billing` in the API-key gateway route group (`backend/internal/server/routes/gateway.go:180-187`). `GatewayHandler.KeyBillingInfo` reads the authenticated API key, rejects Simple mode with 404, resolves that key's user/group rate, sends `Cache-Control: no-store`, and returns the versioned response (`backend/internal/handler/gateway_key_billing.go:14-61`).

The response fields report group rate, optional user override, resolved base rate, peak-rate configuration, effective token multiplier, timezone, and observation time (`backend/internal/handler/gateway_key_billing.go:16-30`, `80-108`). They do not report balance, quota remaining, or usage. The API-key middleware still authenticates the key and checks key, user, IP, and group access. It skips quota, expiry, subscription, and balance enforcement for this read-only endpoint (`backend/internal/server/middleware/api_key_auth.go:121-172`, `191-235`).

### Accuracy and failure cases

- **Positive capability result:** In v0.2.18 Standard mode, the producer emits the exact schema the probe validates. The focused end-to-end route test passed for an authenticated API key and confirmed the object marker (`backend/internal/server/routes/gateway_key_billing_test.go:121-151`).
- **Synthetic fixture:** The success test mocks `https://upstream.example/v1`, returns the protocol marker, and expects `ok` (`backend/internal/service/upstream_billing_probe_test.go:272-336`). This proves parser acceptance of the fixture. It does not establish an actual third-party implementation. No concrete compatible proxy was verified in this research. Copying the response is a theoretical possibility, not an observed misclassification.
- **Feature-disabled Sub2API:** Simple mode intentionally returns 404 (`backend/internal/handler/gateway_key_billing.go:41-43`), and the probe records 404 as `unsupported` (`backend/internal/service/upstream_billing_probe.go:695-697`). This is a correct feature-support result, but a false negative if callers interpret `unsupported` as proof that the server is not Sub2API.
- **Invalid response:** A generic JSON response, wrong object marker, unsupported schema, missing required fields, or inconsistent rates is rejected. Focused parser tests cover missing fields and inconsistent rate calculations (`backend/internal/service/upstream_billing_probe_test.go:586-598`, `661-700`).
- **Transient or authorization failure:** 401/403, other HTTP errors, transport errors, and malformed responses remain `failed`, not `unsupported`. That distinction prevents auth/network errors from being read as a definitive absence of the capability (`backend/internal/service/upstream_billing_probe.go:680-703`, `750-789`).
- **Unverified compatibility:** This research checked the v0.2.18 source only. It does not establish route availability in other Sub2API releases.

### Recommendation

The existing probe is suitable for detecting Sub2API billing-declaration support in the checked version.
Simple mode is a confirmed gap if quota monitoring requires a successful declaration first.
Query the quota interface independently. No observed third-party misclassification justifies an additional provider-verification mechanism.

## Focused Verification

The following existing upstream tests passed against the local v0.2.18 source:

```sh
go test ./internal/service -run '^(TestUpstreamBillingProbeSuccessPersistsSanitizedSnapshot|TestUpstreamBillingProbeRejectsMissingRequiredMultiplier|TestUpstreamBillingProbeRejectsInconsistentMultipliers|TestUpstreamBillingProbeNonOpenAIWithoutBaseURLIsUnsupportedWithoutRequest)$'
go test ./internal/server/routes -run '^TestGatewayRoutesKeyBillingInfoEndToEnd$'
```

These tests verify the accepted contract, schema rejection, empty-base-URL handling, API-key route, and Simple-mode response.

## Files Found

| Path | Role |
| --- | --- |
| `backend/internal/service/upstream_billing_probe.go` | Account eligibility, target selection, authenticated HTTP probe, response validation, and status classification. |
| `backend/internal/handler/gateway_key_billing.go` | Sub2API billing declaration producer. |
| `backend/internal/server/routes/gateway.go` | Registers the producer route in the `/v1` API-key gateway. |
| `backend/internal/server/middleware/api_key_auth.go` | API-key authentication and billing-enforcement bypass for this read-only endpoint. |
| `frontend/src/components/account/UpstreamBillingRateCell.vue` | Displays the probe snapshot and rate. |
| `frontend/src/i18n/locales/zh/admin/accounts.ts` | Names the field and states the trust limitation. |

## Caveats / Not Found

No live upstream account, credential, or paid API request was used. This artifact does not independently investigate quota endpoint units or balance semantics.
