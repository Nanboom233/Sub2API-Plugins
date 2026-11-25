# v0.2.25 Simplification Audit

Date: 2026-11-25

Stage: Trellis Phase 1 research only

## Scope and method

This audit compares upstream `v0.2.24..v0.2.25` with the full quota, Codex, and Gemini plugin patches.

The audit used a blobless public upstream clone in `/tmp/sub2api-v0225-simp-codex-xdgUfv/upstream`.
It used unauthenticated Git commands and read-only searches. It did not edit production files, tests, workflows, READMEs, specs, or submodules.

The current patch inventory is:

| Patch | Added lines | Deleted lines | Hunks |
| --- | ---: | ---: | ---: |
| `quota-extension.patch` | 1,874 | 60 | 107 |
| `0004-admin-channel.patch` | 1,123 | 1 | 4 |
| `0007-sub2api-integration.patch` | 45 | 1 | 14 |

The quota patch is based on the older billing repository contract. It has 25 rejected hunks against the v0.2.25 tree. The rejects affect nine files. This report treats those rejects as rebase work, not as proof that upstream code can replace quota behavior.

## Upstream intent table

| Upstream feature | Contract established by upstream | Effect on the plugins |
| --- | --- | --- |
| `a95c9e263` and `03aa05fd9` group preview and sync | `PreviewUpstreamGroup` accepts either a saved account or a complete draft. `PreviewGroup` calls the shared `fetchBilling` path. Automatic sync writes name and notes through `AccountBillingSettingsUpdate` and the locked account merge. | The quota editor still needs a saved account plus field overlays, arbitrary script requests, and script result parsing. The contracts differ. |
| `fetchBilling` and `upstreamBillingReply` | The helper owns the fixed `/v1/sub2api/billing` request. It owns adaptive base URL selection, proxy identity checks, TLS profile selection, redirect blocking, timeout, body limits, and billing unsupported classification. | The helper is reusable for group billing only. The quota `/v1/usage` request and the quota script HTTP API need different paths and result rules. |
| `AccountBillingSettingsUpdate` and `lockAndMergeAccountProbeExtra` | Account edits express optional probe, rate sync, group sync, rate, name, and notes changes. The repository locks the row and preserves database-managed billing fields. | Quota must rebase onto this struct and extend the same lock boundary with quota state. The old variadic `previousExpiresAt` path cannot be deleted without changing quota expiry and scheduling semantics. |
| `0f1e3c1f6` and `c5147eab1` header identity variables | `ApplyHeaderOverrides` receives a context. Request scope expands user, API key, group, and request identity. Connection scope omits request IDs. Shared model catalog calls remove the request scope. | Background quota probes and admin tests use plain context. Codex evaluation streams also use plain context. Only the WebSocket handshake uses connection scope. |
| `2b7437832`, `4339d5061`, and `eabf37852` OpenAI error passthrough | Error passthrough keeps selected structured fields, redacts account credentials and hosts, limits scalar fields, preserves compact SSE error codes, and rewrites capacity shed codes for retry. | The helpers operate on Gin OpenAI gateway responses. Codex evaluation returns an `http.Response` and converts three different upstream event formats. Gemini signature repair has its own retry and event state. |

## Concrete simplification opportunities

### A. Replace quota diagnostic header materialization with `HeaderOverrideValue`

This is a contract-preserving simplification.

The quota patch creates an empty `http.Header`, calls `ApplyHeaderOverrides` with no request identity, then walks the generated values in `quotaScriptDiagnostic` (`plugins/sub2api-quota-extension/patches/quota-extension.patch:1249-1257`). Upstream now provides `HeaderOverrideValue` at `backend/internal/service/account_header_override.go:166-174`.

`HeaderOverrideValue` returns only an enabled static override. It ignores variable templates. This matches the current diagnostic path because the dummy header call has no request scope. Variable templates are therefore removed and cannot produce a value to redact.

The replacement can iterate `account.GetHeaderOverrides()` and call `HeaderOverrideValue` for each lower-case name. It removes the dummy header allocation and the nested value loop. The affected block is one patch hunk and nine added lines. The direct lookup form is one hunk and about six added lines. The expected reduction is three added lines. The behavior remains the same for enabled flags, platform eligibility, static values, and variable values.

Use this change in Phase 2 only after updating the six old `ApplyHeaderOverrides` calls to the context-aware signature. Do not add a compatibility wrapper.

### A. Rebase the quota billing edits onto the upstream settings struct

This is a contract-preserving patch simplification, but it is a rebase operation rather than a new shared helper.

Upstream defines `AccountBillingSettingsUpdate` at `backend/internal/service/account_service.go:139-149`. The repository accepts that struct at `backend/internal/repository/account_repo.go:456-626`. The quota patch still targets the old pointer argument list and adds a variadic `previousExpiresAt` parameter in `plugins/sub2api-quota-extension/patches/quota-extension.patch:201-341`.

The Phase 2 patch should keep the upstream settings struct and add only quota-specific state to the existing locked row query. It should remove the stale old-signature context from the quota patch. The quota-specific SQL fields, quota state merge, expiry compare, and temporary pause handling must remain. They protect concurrent quota refreshes and cannot be dropped.

The old quota adapter section contains 66 added lines and three deleted lines in one repository region. The v0.2.25 rebase can remove the stale signature context from that region. The exact final count depends on the accepted quota persistence design. Do not claim that all 69 lines can be deleted. The expiry and pause contract still needs an explicit input path.

### A. Keep shared group sync in `lockAndMergeAccountProbeExtra`

Upstream already owns group sync preservation in `backend/internal/repository/account_repo.go:621-852`. The quota patch extends the same helper with quota columns and state in `plugins/sub2api-quota-extension/patches/quota-extension.patch:258-341`.

The safe simplification is to merge quota columns into the upstream query and scan once. Do not add a second quota merge helper. This keeps one row lock, one database snapshot, and one write path. It removes duplicate adapter code if the Phase 2 rebase currently creates it. It does not remove the quota state merge itself.

## Optional simplifications that need a product trade-off

### B. Generalize the billing HTTP transport for quota usage

`fetchBilling` is 92 source lines at `backend/internal/service/upstream_billing_probe.go:631-723`. The quota `quotaScriptRequest` block spans `plugins/sub2api-quota-extension/patches/quota-extension.patch:1148-1233`. The quota API-key usage request spans `plugins/sub2api-quota-extension/patches/quota-extension.patch:1619-1711`.

These blocks repeat URL validation, timeout, proxy checks, TLS profile selection, redirect blocking, header overrides, and response limits. A future generic transport could reduce repetition. It would need an explicit endpoint, authentication, unsupported status policy, response parser, and error policy.

This change needs approval because `fetchBilling` rejects official non-OpenAI roots as unsupported, sends a billing include query, and returns a billing-specific error class. Quota usage accepts `/v1/usage`, supports custom script URLs, and memoizes unsupported identities. A generic helper must preserve all three contracts.

### B. Share a frontend draft source builder

The quota patch adds separate draft connection computed values in `CreateAccountModal.vue` and `EditAccountModal.vue` (`plugins/sub2api-quota-extension/patches/quota-extension.patch:2414-2439` and `:2498-2511`). Upstream group preview uses `UpstreamGroupSource` and rejects mixed saved and draft inputs at `backend/internal/handler/admin/account_upstream_billing_probe.go:101-149`.

A shared builder could reduce duplicated Vue code. It would need to preserve the quota editor's saved-account overlay, `extra` map, adaptive base URL choice, and proxy selection. The upstream group source contract does not provide those fields. This is an optional UI refactor and needs a decision about the request contract.

## Rejected false simplifications

### Do not replace quota draft construction with `PreviewUpstreamGroup`

The upstream handler creates a minimal API-key account from `platform`, `base_url`, `api_key`, and `proxy_id`. It rejects any saved account request that also contains draft fields (`backend/internal/handler/admin/account_upstream_billing_probe.go:114-143`).

The quota test intentionally overlays draft fields on a saved account. It also preserves `extra`, resolves adaptive base URLs, and runs arbitrary validated scripts. Replacing it would remove required behavior.

### Do not replace quota HTTP calls with `fetchBilling`

`fetchBilling` always requests `/v1/sub2api/billing` and parses the billing envelope (`backend/internal/service/upstream_billing_probe.go:631-749`). Quota usage requests `/v1/usage` and parses `quota_limited` or `unrestricted` responses (`plugins/sub2api-quota-extension/patches/quota-extension.patch:1619-1711`). Quota scripts allow arbitrary validated request methods, headers, and URLs (`plugins/sub2api-quota-extension/patches/quota-extension.patch:1148-1233`). The endpoint, parser, and unsupported memoization rules differ.

### Do not apply header identity scope helpers to background quota probes

Upstream states that background probes have no inbound user identity and must not expand identity variables (`backend/internal/service/account_header_override_vars.go:227-255`). `withoutHeaderOverrideRequestScope` is for shared model catalog results (`backend/internal/service/account_header_override_vars.go:75-83`). `withHeaderOverrideConnectionScope` is for a WebSocket handshake (`backend/internal/service/account_header_override_vars.go:58-63`). Plain context is correct for quota probes and admin evaluation requests.

### Do not use OpenAI passthrough helpers in Codex evaluation or Gemini rectification

The OpenAI helpers are in `backend/internal/service/error_passthrough_runtime.go:48-100`, `openai_gateway_passthrough.go:868-1168`, and `openai_compact_stream_bridge.go:112-166`. They write Gin responses and compact `response.failed` events.

The Codex patch owns an `http.Response` admin channel and three stream converters in `plugins/codex-candy-eval/patches/0004-admin-channel.patch:396-810` and `:823-1060`. The Gemini patch owns signature retry and event handling in `plugins/gemini-signature-rectifier/patches/gemini-signature-rectifier.patch:97-217`. The data types and error timing differ. Direct reuse would change the plugin contracts.

### Do not remove Codex `ApplyHeaderOverrides` calls

Upstream changed the call signature to `ApplyHeaderOverrides(context.Context, http.Header)` at `backend/internal/service/account_header_override.go:177-215`. The three Codex calls at `plugins/codex-candy-eval/patches/0004-admin-channel.patch:564`, `:717`, and `:796` must receive the request context. The calls remain necessary to apply static account headers and to remove unresolved variable headers. This is an API adaptation, not a simplification.

### Do not merge `UpstreamGroupSyncButton` with `QuotaScriptEditor`

`UpstreamGroupSyncButton.vue` updates name and notes only. It aborts stale requests and preserves fields changed by the user during the request. `QuotaScriptEditor.vue` runs JavaScript, tests arbitrary HTTP requests, and displays quota usage (`plugins/sub2api-quota-extension/patches/quota-extension.patch:2513-2625`). The two components have different state, output, and failure contracts.

## Decision

Adopt the direct `HeaderOverrideValue` diagnostic reduction and the v0.2.25 settings-struct rebase in Phase 2. Keep quota-specific expiry, pause, usage, and script behavior.

Treat generic HTTP transport sharing and a shared frontend draft builder as optional design work. Request a product decision before using either change.

Reject direct reuse of `PreviewGroup`, `fetchBilling`, header scope helpers, OpenAI passthrough writers, or group sync UI for quota, Codex evaluation, or Gemini rectification.

No production, test, workflow, README, spec, or submodule file was changed during this Phase 1 audit.
