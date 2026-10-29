# Research: cc-switch Custom Quota Scripts

- Query: Verify cc-switch's custom quota script authoring, execution, output, and refresh behavior for planning an API-key account extension.
- Scope: external primary source
- Date: 2026-10-26

## Findings

Canonical source: [`farion1231/cc-switch`](https://github.com/farion1231/cc-switch), public default branch `main`. The inspected revision is `e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733`. Its `src-tauri/Cargo.toml` identifies version `4.0.20` and declares MIT; `rquickjs` is declared at `0.8`, locked to `0.8.1`.

### Authoring and persistence

The provider-card menu opens a usage-query editor. The user enables the query, selects a preset or custom script, edits JavaScript, tests it, and saves it. Presets include a Sub2API template. The editor accepts optional API key and base URL overrides, access token, user ID, request timeout, and auto-query interval. Empty key and URL values fall back to the provider's credentials. See the [usage-query guide](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/docs/user-manual/en/2-providers/2.5-usage-query.md#L60-L72) and [`UsageScriptModal.tsx`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src/components/UsageScriptModal.tsx#L539-L558).

cc-switch stores `usage_script` under provider `meta`, not per API-key account. The `UsageScript` structure includes enabled, language, code, timeout, credential overrides, template type, and interval fields. See [`provider.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/provider.rs#L282-L334) and [`provider.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/provider.rs#L503-L505).

### Script contract and runtime

A script evaluates to an object with a `request` descriptor and an `extractor(response)` function. The descriptor contains URL, HTTP method, headers, and optional body. Rust sends the HTTP request. JavaScript does not get a general `fetch` API. The extractor receives the JSON response and returns quota data. See [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L79-L141) and [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L143-L232).

The Rust backend embeds QuickJS through `rquickjs`. It evaluates the script to get the request descriptor, performs the request with `reqwest`, then evaluates the extractor in another QuickJS context. Script execution has a five-second interrupt deadline, a 16 MiB memory limit, and a 256 KiB stack limit. The request timeout is clamped to two through 30 seconds. See [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L32-L66), [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L246-L264), and [`Cargo.toml`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/Cargo.toml#L65-L68).

cc-switch replaces credential placeholders with string replacement before evaluating JavaScript. It does not escape inserted values as JavaScript string literals. Do not copy this interpolation mechanism. Pass credentials as data to an interpreter or request builder instead. See [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L424-L444).

The built-in templates require HTTPS and same host and port. Custom template mode bypasses those checks. Its tests explicitly accept an HTTP request to a different private host. This is materially unsafe to copy into a server-side account feature without the existing URL policy and a deliberate egress boundary. See [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L501-L555) and [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L597-L627).

The Sub2API preset calls `/v1/usage` with the provider API key. It extracts remaining, key total used/limit, and validity from the response. See the [Sub2API template in `UsageScriptModal.tsx`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src/components/UsageScriptModal.tsx#L124-L153) and the [usage-query guide](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/docs/user-manual/en/2-providers/2.5-usage-query.md#L175-L187).

### Results, testing, and refresh

The extractor may return one object or an array. Optional fields are `isValid`, `invalidMessage`, `remaining`, `unit`, `planName`, `total`, `used`, and `extra`. Arrays represent multiple plans; the provider card summarizes them and can expand the details. See [`usage_script.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/usage_script.rs#L314-L421), [`provider.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/provider.rs#L336-L368), and the [output guide](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/docs/user-manual/en/2-providers/2.5-usage-query.md#L235-L264).

The test button submits the current unsaved script and resolves credentials the same way as the saved query. It shows a success summary or an error. A successful test also writes the result to the provider-card usage query cache, although it does not save the edited script. See [`UsageScriptModal.tsx`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src/components/UsageScriptModal.tsx#L712-L759) and [`usage.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/services/provider/usage.rs#L191-L228).

The guide sets the request timeout default to 10 seconds. Auto-query interval is in minutes, with `0` disabling automatic refresh; the documented range is 0-1440. Background refresh runs only while a provider is in use. The card passes a nonzero interval only for its active provider state. See the [usage-query guide](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/docs/user-manual/en/2-providers/2.5-usage-query.md#L224-L233) and [`ProviderCard.tsx`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src/components/providers/ProviderCard.tsx#L279-L293).

The reference app shows query errors as `Quota unavailable`. It also propagates transport failures for frontend retry.
This task now requires visible custom-script errors and silent default-query failures.
See the [usage-query guide](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/docs/user-manual/en/2-providers/2.5-usage-query.md#L24-L26) and [`usage.rs`](https://github.com/farion1231/cc-switch/blob/e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733/src-tauri/src/services/provider/usage.rs#L59-L92).

## Practical Recommendation

Use cc-switch only as an interaction reference for configure, edit, test, and save actions.
The user selected genuine custom JavaScript without cc-switch script compatibility.
Use one stored script string and test current code against the create/edit form's effective draft connection settings.
Refer to the task design for the current test request, editor, and result contract.
Show custom errors in the account usage cell and editor. Keep default-query failures silent.
The selected Goja runtime and its actual limits appear in [runtime research](./script-runtime.md).
Pass credentials as data and reuse the existing URL policy. Do not copy cc-switch source or output fields.

## Files Found

| Path | Description |
| --- | --- |
| `src/components/UsageScriptModal.tsx` | Presets, editor, credential fields, test action, and save action |
| `src-tauri/src/usage_script.rs` | QuickJS evaluation, request descriptor, URL validation, HTTP request, result validation |
| `src-tauri/src/services/provider/usage.rs` | Credential fallback, saved query, unsaved test query, and error conversion |
| `src-tauri/src/provider.rs` | `UsageScript`, `UsageData`, `UsageResult`, and provider metadata field |
| `src/components/providers/ProviderCard.tsx` | Query eligibility, card state, and active-provider interval selection |
| `docs/user-manual/en/2-providers/2.5-usage-query.md` | User-facing behavior, templates, fields, and refresh contract |
| `src-tauri/Cargo.toml` and `src-tauri/Cargo.lock` | Version, MIT package license, and pinned QuickJS crate version |

## Related Specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/spec/backend/quality-guidelines.md`

## Caveats / Not Found

- cc-switch stores the script on a provider, while this task requires per-account API-key configuration. That storage difference must not be copied.
- The Sub2API preset documents that app's behavior. It does not define this task's script or response contract.
- The reviewed revision is the public `main` head obtained on 2026-10-26. It is cc-switch v4.0.20 at commit `e8e1cfbff4f2d93f2d6c4ba4ad10b511e012c733`.
- cc-switch is MIT licensed. This task uses its interaction as a reference and does not copy its source code.
