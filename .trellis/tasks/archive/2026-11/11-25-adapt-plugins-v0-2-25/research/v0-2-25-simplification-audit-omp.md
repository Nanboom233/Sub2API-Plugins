# Upstream v0.2.25 design intent and code reduction audit (independent worker)

Audit date: 2026-11-25. Task: `11-25-adapt-plugins-v0-2-25`, Trellis Phase 1 research.
Question from the user: does the intent of the upstream `v0.2.25` changes let us delete plugin code?
Method: one bare partial clone (`--bare --filter=blob:none`, 20 MB) and two sparse worktrees in a private directory. Tree A is `v0.2.24` plus the 9 plugin patches. Tree B is pristine `v0.2.25` (`348997267d756eab5729bb6b78a275a15d18796a`). No repository file changed. No build ran. No `gh` call. No subagent.
Line numbers marked "v0.2.25" point to tree B. Line numbers marked "plugin" point to tree A. "Patch line" points to a line of `plugins/sub2api-quota-extension/patches/quota-extension.patch` or `plugins/codex-candy-eval/patches/0004-admin-channel.patch`.

## 1. Summary table

Classes: **Adopted** = no documented contract changes. **Decision** = a contract or behavior trade-off exists. **Rejected** = unsafe or incompatible.

### 1.1 Adopted

| # | Candidate | File | Hunk change | Line change | Why it is safe |
| --- | --- | --- | ---: | ---: | --- |
| S1 | `quotaScriptDiagnostic` reads `account.GetHeaderOverrides()` and deletes the empty `http.Header` round-trip | `account_quota_script.go` (plugin file) | 0 | -6 | `GetHeaderOverrides()` returns the same values that `ApplyHeaderOverrides` wrote into the empty header. It also returns values that contain a variable. |
| S2 | Memoization moves to one hook at the end of `persistProbeFailure`. Two reason mappings go to its start | `upstream_billing_probe.go` | 0 | -9 against `design.md` section 2.3 | `persistProbeFailure` has 2 callers. It already decides `StatusUnsupported` from `reason == "unsupported"`. `fetchBilling` and the error branch of `probeLoadedAccount` stay at upstream text. |
| S3 | Delete the dead `AccountBulkUpdate.ExpiresAt` path | `account_service.go`, `account_repo.go`, `tests/test_upstream_quota_test.go` | -2 | -6 production, -3 test | No code sets the field. Spec `api-key-quota.md` line 39 says: "Do not add scheduling fields to frontend DTOs or `AccountBulkUpdate`." |
| S4 | `APIKeyQuotaManagedExtraKeys` becomes `append([]string{APIKeyUsageUnsupportedIdentityExtraKey}, APIKeyQuotaSchedulingExtraKeys...)` | `account_upstream_quota.go` (plugin file) | 0 | -14 | Same 13 keys in the same order. |
| S5 | `filterSchedulerExtra` appends `service.APIKeyQuotaSchedulingExtraKeys...` | `repository/scheduler_cache.go` | 0 | -10 | Same 12 keys. The loop reads by key, so the order has no effect. |
| S6 | `duplicateAccountExtra` adds one loop over `APIKeyQuotaManagedExtraKeys` | `service/admin_account.go` | 0 | -10 | Same 13 keys. |

Total for S1 to S6: 55 fewer production lines, 2 fewer hunks, 3 fewer test lines. One of the 3 quota `ApplyHeaderOverrides` call sites disappears (S1).

The plan in `design.md` section 2.2 stays valid: `MergeAPIKeyQuotaState` and `PreviousExpiresAt` on `AccountBillingSettingsUpdate` remove 5 signature hunks (patch lines 201, 212, 220, 228, 258) and the test-stub hunk.

### 1.2 Needs user decision

| # | Candidate | File | Hunk change | Line change | Trade-off |
| --- | --- | --- | ---: | ---: | --- |
| D1 | Also redact the fixed text segments of a value that contains `{{...}}` | `account_quota_script.go` | 0 | +7 | Hardening. It goes past PRD AC2 and spec line 209. It uses the unexported upstream helper `walkHeaderOverrideTemplate`. |
| D2 | Eval uses upstream `buildAnthropicMessagesURL` and deletes `buildAnthropicMessagesEvalURL` | `account_codex_eval_service.go` in `0004-admin-channel.patch` | 0 | -11 | Two behavior changes: Cloudflare REST endpoints stop receiving `?beta=true`. A base URL that ends with `/v1` or `/v1/messages` gets the suffix appended again, as in the gateway and the native connection test. |
| D3 | The edit form uses upstream `billingBaseUrl` | `EditAccountModal.vue` | 0 | -2 | One corner case changes: a field that contains only spaces now resolves to the default URL. Before, it resolved to an empty string. |
| D4 | The `TempUnschedulable*` builder block shrinks to the clear case | `account_repo.go` (patch line 239) | 0 | -8 | Same database result in all 5 states. It depends on one upstream fact: the native update does not write these 2 columns. |
| D5 | One plugin helper sends the request for `quotaScriptRequest` and `fillUpstreamAPIKeyUsage` | `account_quota_script.go`, `account_upstream_quota.go` | 0 | about -12 | Internal refactor of plugin code. It also centralizes the `ApplyHeaderOverrides` call. |
| D6 | The draft quota test sends `platform` | `account_quota_script_handler.go`, `api/admin/accounts.ts`, 2 modals | 0 | +3 to +5 | Parity with the upstream group preview. A draft for an OpenAI account then uses the OpenAI transport profile. It is a feature change. |
| D7 | `TestQuotaScript` stores the trimmed draft key and URL | `account_quota_script_handler.go` | 0 | 0 | Parity with `PreviewUpstreamGroup`, which stores trimmed values. |

### 1.3 Rejected

| # | Candidate | Exact reason |
| --- | --- | --- |
| R1 | Share the draft account code of `PreviewUpstreamGroup` | Incompatible with 5 rules of spec `api-key-quota.md` lines 211 to 221. Section 4.2 lists them. |
| R2 | Share `UpstreamGroupSource`, `previewUpstreamGroup`, or `UpstreamGroupSyncButton.vue` | The quota request shape is different: `script`, `proxy_id: null`, and `extra` do not exist upstream. The endpoints differ. |
| R3 | `fillUpstreamAPIKeyUsage` reuses `fetchBilling` | `fetchBilling` is a method of `*UpstreamBillingProbeService`. It uses `s.accountTestService` and the fixed path `/v1/sub2api/billing`. The quota code requests `/v1/usage` through `AccountUsageService`. |
| R4 | The create form reuses upstream `previewBaseUrl` | `previewBaseUrl` has no default and no placeholder fallback. The quota editor must test the displayed default URL. |
| R5 | Quota keys go into the upstream managed-key list of `UpdateAccount` | It changes 2 upstream lines that commit `03aa05fd9` just changed. It saves 4 lines and adds conflict surface. |
| R6 | The edit form sends the quota `extra` block only when the script changes | It saves 0 lines. |
| R7 | Eval or Gemini uses the new OpenAI passthrough and SSE helpers | No plugin code path writes a passthrough error envelope or a compact SSE failure. |
| R8 | Plugin requests use `withoutHeaderOverrideRequestScope` or `withHeaderOverrideConnectionScope` | Quota and evaluation requests have no API-key request scope. A plain `req.Context()` gives the same result. |
| R9 | A plugin helper returns the effective API-key base URL | It replaces 2 copies of 4 lines with a 7-line helper. Net +1 line. |
| R10 | `fetchBilling` treats HTTP 501 as `errBillingUnsupported` | `PreviewGroup` also calls `fetchBilling`. A 501 response would then show "no group information" instead of a failure. That changes the new upstream feature. |

## 2. Question 1: header override identity variables

### 2.1 How upstream stores and reads overrides (v0.2.25)

- Storage: `credentials["header_override_enabled"]` (bool) and `credentials["header_overrides"]` (`map[string]any`). `account_header_override.go` line 92 (`IsHeaderOverrideEnabled`) and line 109.
- Reader: `(*Account).GetHeaderOverrides()` at `account_header_override.go` lines 105 to 143. It returns the effective table with lowercase names. It caches the result. `resolveHeaderOverrides` (lines 146 to 164) removes entries with an empty value, an invalid name, or a blocked name.
- A method named `HeaderOverrides()` does not exist. The only readers are `GetHeaderOverrides()`, `HeaderOverrideValue(lowerName)`, and `ApplyHeaderOverrides(ctx, h)`.

### 2.2 The four contexts

| Context | Definition (v0.2.25) | Effect on `{{user_id}}`, `{{api_key_id}}`, `{{group_id}}`, `{{request_id}}` | Upstream call sites (production code) |
| --- | --- | --- | --- |
| `WithHeaderOverrideRequestScope(ctx, userID, apiKeyID, groupID)` | `account_header_override_vars.go` lines 67 to 73. It stores a `*HeaderOverrideRequestScope` in the context. | It is the only identity source. `resolveHeaderOverrideVariable` (lines 227 to 254) returns `""` when `scope == nil \|\| scope.userID <= 0` (line 230). | 2. Both are in the API-key authentication middleware: `server/middleware/api_key_auth.go:176` and `api_key_auth_google.go:120`. |
| `withoutHeaderOverrideRequestScope(ctx)` | Lines 78 to 83. It puts a nil scope into the context. | No variable resolves. | 5. Model lists and the models manifest: `upstream_models.go:1094`, `:1165`, `:1247`, `:1308`, and `openai_codex_models_service.go:1787`. These results are shared across users. |
| `withHeaderOverrideConnectionScope(ctx)` | Lines 61 to 63. It sets a marker. It does not replace the scope. | `request_id` does not resolve. The other 3 variables resolve when a request scope exists. | 1. The OpenAI WebSocket handshake: `openai_ws_forwarder_payload.go:187`. |
| Plain request context (`req.Context()`, `upstreamReq.Context()`, `ctx`) | The scope that the caller context already has. | Variables resolve only when an API-key request scope exists. Background requests have no scope, so the header is not sent. | 42. Forwarded traffic, account tests, probes, usage queries. |
| `context.Background()` | No scope. | No variable resolves. | 1. `model_protocol_catalog.go:228`. A background refresh. |

`v0.2.25` has 49 production call sites of `ApplyHeaderOverrides`. `expandHeaderOverrideTemplate` (lines 195 to 225) returns `ok == false` when a variable has no value. `ApplyHeaderOverrides` (lines 185 to 213) then deletes a same-named client header and does not send the override.

### 2.3 Candidate S1: `quotaScriptDiagnostic`

Current plugin code (`account_quota_script.go` lines 364 to 372, 9 lines):

```go
	headers := make(http.Header)
	account.ApplyHeaderOverrides(headers)
	for _, values := range headers {
		for _, secret := range values {
			if secret != "" {
				message = strings.ReplaceAll(message, secret, "[redacted]")
			}
		}
	}
```

Replacement (3 lines):

```go
	for _, secret := range account.GetHeaderOverrides() {
		message = strings.ReplaceAll(message, secret, "[redacted]")
	}
```

Evidence:

1. `ApplyHeaderOverrides` starts with `overrides := a.GetHeaderOverrides()` (`account_header_override.go` line 189). On an empty header, each entry ends as `h[resolveWireCasing(name)] = []string{value}` (line 213). The old loop read exactly the values of `GetHeaderOverrides()`.
2. The `secret != ""` check is redundant. `resolveHeaderOverrides` skips `value == ""` (line 155).
3. Fix for variables: `ApplyHeaderOverrides` skips a value with a variable when the context has no scope (lines 202 to 212). The old round-trip with `context.Background()` would lose that value. `GetHeaderOverrides()` returns it. PRD AC2 is satisfied: the configured value is redacted.
4. `GetHeaderOverrides()` returns `nil` when the account is not eligible. The loop then does nothing.

Result: -6 lines. The quota patch has 2 `ApplyHeaderOverrides` sites left: `account_quota_script.go` line 325 and `account_upstream_quota.go` line 289. Both take `req.Context()`.

The other 2 sites are real requests. `withoutHeaderOverrideRequestScope` adds nothing there, because usage queries and script tests run without an API-key request scope (R8).

### 2.4 Candidate D1: fixed text segments of a template value

The upstream comment at lines 191 to 194 states the rule: fixed text of a mixed template can be a relay key, for example `sk-xxx-{{user_id}}`. S1 redacts the complete configured value. It does not redact the fixed part alone. The quota request path never resolves the variable, so the expanded form cannot leak through that path.

Optional addition (7 lines) after the S1 loop:

```go
	for _, value := range account.GetHeaderOverrides() {
		_ = walkHeaderOverrideTemplate(value, func(literal string) {
			if literal = strings.TrimSpace(literal); literal != "" {
				message = strings.ReplaceAll(message, literal, "[redacted]")
			}
		}, func(string) bool { return true })
	}
```

Decision: the spec line 209 requires "header-override values". S1 satisfies it. D1 is a hardening that couples the plugin to one more unexported upstream helper.

## 3. Question 3a: the billing probe and `fetchBilling`

### 3.1 What upstream did (v0.2.25)

- `fetchBilling(ctx, account, includeGroup bool, now time.Time) (upstreamBillingReply, error)` at lines 631 to 723. It returns a value, not a pointer. `upstreamBillingReply` is at lines 623 to 627.
- `var errBillingUnsupported = errors.New("unsupported")` at line 629. Its message equals `UpstreamBillingProbeStatusUnsupported` (line 99).
- `fetchBilling` returns `errBillingUnsupported` for a non-OpenAI official domain (line 656) and for HTTP 404 and 405 (line 716). It returns `errors.New("http_error")` with `result.status` for all other non-2xx responses (line 719). HTTP 501 is one of them.
- `probeLoadedAccount` (lines 785 to 847) passes `err.Error()` as the reason (line 794) and uses `"invalid_response"` for a bad 2xx body (line 798).
- `persistProbeFailure` (lines 849 to 889) has exactly 2 callers: lines 794 and 798. It sets `status = UpstreamBillingProbeStatusUnsupported` when `reason == "unsupported"` (line 865).

### 3.2 Current plugin hunks (patch lines 2091 to 2156)

| Hunk | Plugin code | Added lines | Removed lines |
| --- | --- | ---: | ---: |
| Patch line 2091, `RunDue` | Adds `\|\| isAPIKeyUsageUnsupportedMemoized(&account)` | 1 | 1 |
| Patch line 2100, `probeAccountWithMode` | Adds `\|\| isAPIKeyUsageUnsupportedMemoized(account)` | 1 | 1 |
| Patch line 2109 | Grok official domain: persist `unsupported`, then memoize | 5 | 1 |
| Patch line 2122 | 404, 405, 501: memoize. Bad 2xx body: reason `unsupported`, memoize | 11 | 3 |
| Patch line 2149 | After a successful snapshot: clear the memo | 1 | 0 |

### 3.3 Candidate S2: one hook in `persistProbeFailure`

On `v0.2.25`, the 3 plugin cases all arrive in `persistProbeFailure` with reason `unsupported`, except the 2 plugin-specific cases. The replacement keeps the `RunDue` and `probeAccountWithMode` hunks and makes 3 edits.

Edit 1. Start of `persistProbeFailure`, before line 858 (+3 lines):

```go
	if reason == "invalid_response" || (reason == "http_error" && statusCode == http.StatusNotImplemented) {
		reason = "unsupported"
	}
```

Edit 2. End of `persistProbeFailure`, between lines 887 and 888 (+3 lines):

```go
	if status == UpstreamBillingProbeStatusUnsupported {
		memoizeUpstreamProbeUnsupported(ctx, s.accountRepo, account)
	}
```

Edit 3. `probeLoadedAccount`, after the `updateSnapshot` call at line 833 (+1 line, same as patch line 2149):

```go
	clearUpstreamProbeUnsupported(ctx, s.accountRepo, account)
```

Result:

| Shape | Hunks in the file | Added lines | Removed lines | Lines changed inside `fetchBilling` or the error branch |
| --- | ---: | ---: | ---: | ---: |
| Current plugin code on `v0.2.24` | 5 | 19 | 6 | n/a |
| `design.md` section 2.3 (inline blocks in `probeLoadedAccount`) | 5 | 18 | 4 | 2 multi-line blocks |
| S2 | 5 | 9 | 2 | 0 |

Contract check against spec `api-key-quota.md` lines 271 and 272:

- HTTP 404 and 405 and the Grok official domain arrive with reason `unsupported`. They use the same reason on `v0.2.24`. The hook covers them.
- HTTP 501 arrives as `http_error` with status 501. Edit 1 maps it. The snapshot keeps `HTTPStatus` 501 and `LastError` `unsupported`.
- A bad 2xx body arrives as `invalid_response`. Edit 1 maps it. The plugin used `unsupported` on `v0.2.24`.
- Transport errors, read timeouts, and oversize bodies keep their reasons. They do not memoize.
- Memoization runs only after `updateSnapshot` returns no error. This equals the `v0.2.24` order.
- `PreviewGroup` (lines 726 to 749) never calls `persistProbeFailure`. The preview does not memoize.

Guard: `TestUpstreamQuotaProbeMemoization` uses the keys `notfound`, `method`, `notimpl`, and `malformed` (`tests/test_upstream_quota_test.go` line 646). It fails when upstream renames one of the 2 reason literals.

### 3.4 `fillUpstreamAPIKeyUsage` and new upstream helpers

`fillUpstreamAPIKeyUsage` (plugin `account_upstream_quota.go` lines 254 to 346) requests `/v1/usage`. It reads the response with `parseUpstreamQuota`. `fetchBilling`, `PreviewGroup`, `upstreamBillingGroupInfo`, and `upstreamBillingReply` belong to the billing path. No helper of `v0.2.25` fits. R3.

## 4. Question 2: group preview and the quota script test

### 4.1 The upstream preview flow (v0.2.25)

- Backend: `(*AccountHandler).PreviewUpstreamGroup` at `handler/admin/account_upstream_billing_probe.go` lines 96 to 151. It has 2 exclusive modes. With `account_id > 0`, it rejects each draft field (lines 116 to 117). Without `account_id`, it requires `platform`, `base_url`, and `api_key` (lines 126 to 128). It then builds `&service.Account{Platform, Type: AccountTypeAPIKey, ProxyID, Credentials: {"base_url", "api_key"}}` inline (lines 131 to 134). No helper function builds the account. The request type is an anonymous struct.
- Service: `(*UpstreamBillingProbeService).PreviewGroup` at `upstream_billing_probe.go` lines 726 to 749. It calls `fetchBilling(ctx, account, true, ...)` and does not persist.
- Frontend: `UpstreamGroupSource` and `previewUpstreamGroup` at `api/admin/accounts.ts` lines 1053 to 1069. `previewBaseUrl` at `CreateAccountModal.vue` lines 4655 to 4659. `upstreamGroupSource` at lines 4661 to 4668 and at `EditAccountModal.vue` lines 4569 to 4580. `billingBaseUrl` at `EditAccountModal.vue` lines 4563 to 4567. `UpstreamGroupSyncButton.vue` (65 lines).

### 4.2 Contract check (spec `api-key-quota.md` lines 211 to 221)

| Spec rule | Quota plugin today | Upstream preview | Shareable? |
| --- | --- | --- | --- |
| With `account_id`, copy the saved account as the baseline. Draft key and URL replace it. Nonblank values replace. Blank values retain. | Yes. `account_quota_script_handler.go` lines 31 to 60. | No. A saved account rejects each draft field with 400 "Use either a saved account or draft credentials". | No |
| An omitted proxy retains the baseline. Explicit `null` removes it. | Yes. `proxy_id` is `json.RawMessage` (line 20, lines 68 to 82). | No. `ProxyID *int64` cannot separate omitted from `null`. | No |
| Merge supplied `extra` keys over the baseline, including empty and null values. | Yes. Lines 63 to 67. | No. `extra` is not accepted. | No |
| Retain saved TLS settings and credential header overrides. The body does not accept a credentials map. | Yes, through the baseline copy. | No baseline in draft mode. | No |
| Reuse the native adaptive base-URL selection. | Yes. Lines 52 to 60 set `base_url` and `api_base_urls`. | No. The draft account has no `api_base_urls`. | No |

Result: R1 and R2. The frontend request types also differ. `QuotaScriptTestParams` has `script`, `proxy_id?: number | null`, and `extra?`.

### 4.3 Candidate D3: `billingBaseUrl` in the edit form

Current plugin code (`EditAccountModal.vue` lines 6486 to 6494):

```ts
  base_url: isCNApiKeyAccount.value && editApiProtocol.value === 'adaptive'
    ? (editAdaptiveBaseUrls.value.chat_completions || defaultBaseUrl.value).trim()
    : editBaseUrl.value.trim() || defaultBaseUrl.value,
```

Replacement (1 line instead of 3):

```ts
  base_url: billingBaseUrl.value || defaultBaseUrl.value,
```

Upstream `billingBaseUrl` (v0.2.25 lines 4563 to 4567) is `(adaptive ? editAdaptiveBaseUrls.chat_completions : editBaseUrl).trim()`. The values are equal for each nonblank field. They differ for a field that contains only spaces: the plugin sends `''`, the replacement sends the default URL. `billingBaseUrl` is declared before `quotaScriptConnection`.

The create form keeps its own expression (R4). Upstream `previewBaseUrl` has no fallback to the preset default or to `apiKeyBaseUrlPlaceholder`.

### 4.4 Intent note

Upstream states at line 115: "A stored key must only be sent with its stored URL, headers and proxy." The quota test intentionally sends a saved key to a draft URL. This is the documented contract. The script also receives `ctx.apiKey`, so the upstream rule cannot apply to it. No change is necessary.

## 5. Question 3b: the billing-settings refactor

### 5.1 The struct (plan of `design.md` section 2.2)

`AccountBillingSettingsUpdate` is at `account_service.go` lines 141 to 145. The interface is at lines 147 to 149. The 2 plugin fields keep all upstream signatures. This removes 5 signature hunks and the stub hunk. No further reduction exists there.

### 5.2 Candidate S3: dead `AccountBulkUpdate.ExpiresAt`

Evidence:

1. Patch line 1322 adds `ExpiresAt *time.Time` to `AccountBulkUpdate` (v0.2.25 lines 161 to 177).
2. Production code constructs `AccountBulkUpdate` in 2 places: `admin_account.go` line 1198 and `ratelimit_service.go` line 2048. Neither sets `ExpiresAt`.
3. The only reader is the plugin code: patch line 630 adds 5 lines to `BulkUpdate`, and patch line 682 adds `updates.ExpiresAt != nil` to `shouldSync`.
4. `fillUpstreamAPIKeyUsage` wrote the expiry through `BulkUpdate` before task `11-08`. That task moved the write to `UpdateAPIKeyQuotaState` (plugin `account_upstream_quota.go` line 345). The old field stayed.
5. The handler line `ExpiresAt: item.ExpiresAt` (`account_handler.go` line 2152) belongs to `CreateAccountInput`.
6. Spec `api-key-quota.md` line 39 prohibits scheduling fields on `AccountBulkUpdate`.

Change:

- Delete patch line 1322 (the hunk disappears).
- Delete the 5 lines of patch line 630 (the hunk disappears).
- Patch line 682 becomes `shouldSync := clearAPIKeyQuotaState`.
- Delete `tests/test_upstream_quota_test.go` lines 323 to 325 (the fixture branch).

No test asserts the bulk `expires_at` clause.

### 5.3 Candidate D4: the builder block

Current plugin block (patch line 239, 12 added lines):

```go
	if len(previousExpiresAt) > 0 {
		if account.TempUnschedulableUntil != nil {
			builder.SetTempUnschedulableUntil(*account.TempUnschedulableUntil)
		} else {
			builder.ClearTempUnschedulableUntil()
		}
		if account.TempUnschedulableReason != "" {
			builder.SetTempUnschedulableReason(account.TempUnschedulableReason)
		} else {
			builder.ClearTempUnschedulableReason()
		}
	}
```

Replacement (4 lines):

```go
	if settings.MergeAPIKeyQuotaState && account.TempUnschedulableUntil == nil && account.TempUnschedulableReason == "" {
		builder.ClearTempUnschedulableUntil()
		builder.ClearTempUnschedulableReason()
	}
```

Evidence: the native `updateLockedAccount` (v0.2.25 lines 522 to 618) does not write the 2 columns. An Ent update writes only the columns that the builder names. The merge block copies the locked values into `account` (patch line 301). It clears them only when the scheduling identity changed and the reason starts with `apikey_quota_`. So the old block wrote the database values back, except in the clear case.

| Locked database state after the merge | Old block | Replacement | Same result |
| --- | --- | --- | --- |
| `until` and `reason` set, scheduling unchanged | Set both (no change) | Nothing (no change) | Yes |
| Quota pause, scheduling changed | Clear both | Clear both | Yes |
| `until` empty, `reason` set, pause kept | Clear (no change), Set (no change) | Nothing (no change) | Yes |
| `until` set, `reason` empty | Set (no change), Clear (no change) | Nothing (no change) | Yes |
| Both empty | Clear both (no change) | Clear both (no change) | Yes |

`TestQuotaAccountEditUsesNativeTransaction` expects `(?s)UPDATE .*accounts.*SET.*WHERE .*id.*` (`tests/test_account_repo_quota_test.go` line 293). It does not assert the 2 columns.

### 5.4 Candidates S4, S5, and S6: repeated key lists

The plugin declares the same keys 3 times.

S4. `account_upstream_quota.go` lines 36 to 49 declare `APIKeyQuotaSchedulingExtraKeys` (12 keys). Lines 51 to 65 declare `APIKeyQuotaManagedExtraKeys` with the same 12 keys and 1 more key. Replacement (1 line):

```go
var APIKeyQuotaManagedExtraKeys = append([]string{APIKeyUsageUnsupportedIdentityExtraKey}, APIKeyQuotaSchedulingExtraKeys...)
```

Go initializes `APIKeyQuotaSchedulingExtraKeys` first, because of the dependency.

S5. Patch line 796 adds 12 keys to `filterSchedulerExtra` (`scheduler_cache.go` v0.2.25 lines 1511 to 1609). The set equals `APIKeyQuotaSchedulingExtraKeys`. Replacement: line 1515 becomes `keys := append([]string{`, and line 1591 becomes `}, service.APIKeyQuotaSchedulingExtraKeys...)`. The loop at lines 1593 to 1604 reads by key.

S6. Patch line 1870 adds 13 keys to `duplicateAccountDiscardedExtraKeys` (`admin_account.go` line 100). The set equals `APIKeyQuotaManagedExtraKeys`. Replacement in `duplicateAccountExtra` (v0.2.25 lines 159 to 167), after the existing loop (+3 lines):

```go
	for _, key := range APIKeyQuotaManagedExtraKeys {
		delete(cloned, key)
	}
```

A script compared the 3 sets: all equal.

### 5.5 `EditAccountModal.vue` and the diffed update payload

Upstream now deletes `name` and `notes` from the payload when they did not change (v0.2.25 lines 5740 to 5741). The quota block (plugin lines 6446 to 6451) only builds `extra`. The 2 logic parts do not meet. The native block for `upstream_request_id_header` (plugin lines 6435 to 6444) is its model. A guard that sends `extra` only on a script change saves 0 lines (R6).

## 6. Question 4: OpenAI passthrough, SSE, and the other commits

New production helpers of commits `2b7437832`, `4339d5061`, and `eabf37852`: `applyErrorPassthroughRuleWithRule`, `applyErrorPassthroughRuleDetailed`, `writeOpenAICompactSSEFailureWithCode`, `writeOpenAICompactSSEFailureEvent`, `isOpenAIInvalidEncryptedContentError`, `sanitizeOpenAIPassthroughClientErrorText`, `replaceCaseInsensitive`, `openAIPassthroughClientErrorField`, `openAIPassthroughClientErrorCode`, `writeOpenAIPassthroughStructuredErrorEnvelope`. Commit `38903b6d1` adds `keyBillingIncludes` and text validation.

- Eval: `account_codex_eval_service.go` sends its own requests through `httpUpstream.Do`. The file has 0 references to a passthrough or SSE helper. It reads the response body itself (`restoreCodexEvaluationBody`).
- Gemini: the patch changes `GeminiMessagesCompatService.ForwardNative` and adds the native signature cleaner. It has 0 references to these helpers. It uses `OpsUpstreamErrorEvent{` with keyed fields, which stays valid with the new `ReportedHeaders` field.
- Result: R7. The only `v0.2.25` change for the 2 plugins is the signature of `ApplyHeaderOverrides`.

### 6.1 Candidate D2: eval uses `buildAnthropicMessagesURL`

Upstream has `buildAnthropicMessagesURL(baseURL string)` at `service/anthropic_messages_url.go` lines 11 to 26 (commit `210608151`, 2026-10-29, the same blob in `v0.2.24` and `v0.2.25`). It appends `/v1/messages`. It omits `?beta=true` for the Cloudflare account REST endpoint, because that endpoint rejects the parameter.

Callers: the gateway (`gateway_upstream_request.go:69`, `gateway_anthropic_passthrough.go:310`) and the native connection test (`account_test_service.go:553`). The native test passes the output of `validateUpstreamBaseURL`, the same input as the eval code.

Current plugin code (`account_codex_eval_service.go` lines 469 to 478, call sites at lines 505 and 527):

```go
func buildAnthropicMessagesEvalURL(normalizedBaseURL string) string {
	trimmed := strings.TrimRight(strings.TrimSpace(normalizedBaseURL), "/")
	if strings.HasSuffix(trimmed, "/v1/messages") {
		return trimmed + "?beta=true"
	}
	if strings.HasSuffix(trimmed, "/v1") {
		return trimmed + "/messages?beta=true"
	}
	return trimmed + "/v1/messages?beta=true"
}
```

Replacement: delete the function. Lines 505 and 527 become `apiURL = buildAnthropicMessagesURL(normalized)`.

Trade-off:

| Input | Plugin helper today | Upstream helper | Gateway |
| --- | --- | --- | --- |
| `https://api.anthropic.com` | `/v1/messages?beta=true` | Same | Same |
| `https://api.cloudflare.com/client/v4/accounts/{id}/ai` | `.../ai/v1/messages?beta=true` | `.../ai/v1/messages` | `.../ai/v1/messages` |
| Base URL that ends with `/v1` | `/v1/messages?beta=true` | `/v1/v1/messages?beta=true` | `/v1/v1/messages?beta=true` |

The validator does not remove a `/v1` suffix (`util/urlvalidator/validator.go` lines 69 and 101). So today an evaluation can pass for a base URL for which the gateway fails. No eval test uses a Cloudflare URL or a `/v1` suffix (`test_service_account_codex_eval_service_test.go` uses `https://api.anthropic.com`). The existing tests keep their result.

## 7. Question 5: bloat in the touched files

| Check | Result |
| --- | --- |
| Dead plugin functions, types, constants, and variables | A script compared each plugin-added top-level name of the 3 patches (362 names) with all uses in the patched tree. 0 dead functions. 1 test-only constant: `apiKeyQuotaTempUnschedulableReasonPrefix` (plugin `account_upstream_quota.go` line 33). Production code uses the literal 2 times in `repository/account_repo.go`. No change recommended. |
| Dead struct field | `AccountBulkUpdate.ExpiresAt`. See S3. |
| Repeated key lists | S4, S5, S6. |
| Duplicate checks | The service level clears a quota pause in `admin_account.go` (patch line 1932), and the repository level clears it again in the locked merge (patch line 301). Both are necessary. Repositories without `AccountBillingSettingsRepository` use only the service level. |
| `apiKeyQuotaClearKeys` block in `UpdateExtra` (patch line 342) and `BulkUpdate` (patch line 642) | 2 similar blocks of 8 lines. A shared helper saves about 4 lines and changes 4 upstream lines. Not recommended. |
| Effective base URL | 4 lines appear 2 times in plugin code (R9). |
| Eval `0004` | 3 call sites need `req.Context()`. D2 deletes 11 lines. |

## 8. Corrections to the current planning documents

1. `design.md` section 2.3 states that `fetchBilling(ctx, account)` returns `(*upstreamBillingReply, error)`. It then uses `reply != nil && reply.status == http.StatusNotImplemented`. The real signature is `fetchBilling(ctx context.Context, account *Account, includeGroup bool, now time.Time) (upstreamBillingReply, error)`. The return type is a value. A comparison with `nil` does not compile. S2 removes this comparison.
2. PRD R2 item 4 and `design.md` section 2.1 list 3 quota `ApplyHeaderOverrides` sites. With S1, 2 sites remain.
3. `design.md` section 2.1 item 2 plans to collect secrets from `ApplyHeaderOverrides(context.Background(), headers)` and from raw credentials. S1 needs neither.

## 9. Method and limits

- Bare clone: `git clone --bare --filter=blob:none https://github.com/Wei-Shaw/sub2api.git`. Environment: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_TERMINAL_PROMPT=0 git -c credential.helper=`.
- Sparse worktrees with `sparse-checkout set --no-cone`. Total size 122 MB with the checked-out files.
- Python: `PYTHONDONTWRITEBYTECODE=1 python3 -B` with the script on standard input.
- Not run: builds, tests, and type-checks. Each line count is a count of patch lines. Each "same result" statement comes from reading the code.
- Files of `v0225-worker` were not read and not changed.

## 10. Cleanup record

- Private directory: `/tmp/sub2api-v0225-simp-omp-JsDwFq`. It held the bare clone, 2 sparse worktrees, and 1 copy of `validator.go`.
- The environment blocks direct deletion of files without Git records. It permits `/usr/bin/trash` only.
- `/usr/bin/trash /tmp/sub2api-v0225-simp-omp-JsDwFq` returned 0. The directory is not in `/tmp`. No path `/tmp/sub2api-v0225-simp-omp-*` remains.
- The directory content is in the macOS Trash. It is not erased. Empty the Trash to erase it.
- `git status --short` of the root repository is unchanged: ` M plugins/gemini-signature-rectifier`, `?? .trellis/tasks/11-25-adapt-plugins-v0-2-25/`, `?? .vscode/`. The 4 submodules have no change. No `__pycache__` exists under the repository.
- Files written by this audit: this record only. The other 3 files in `research/` were not changed.
