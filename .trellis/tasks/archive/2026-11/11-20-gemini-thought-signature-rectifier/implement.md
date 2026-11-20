# Native Gemini rectifier implementation plan

Planning is complete. User approval to start Phase 2 with `task.py start` remains required.
Read [prd.md](prd.md), [design.md](design.md), and the [source supplement](research/count-tokens-and-settings.md).
This checklist is future work. Do not run builds or browser checks during planning.

## 1. Create the plugin after implementation approval

- [ ] Inspect current changes and preserve unrelated work.
- [ ] Copy the complete template kit into the independent local `plugins/gemini-signature-rectifier` submodule for parent discovery.
- [ ] Retain the standalone build script, installer, workflow, common tests, LGPLv3 root license, and inherited notices under `licenses/`.
- [ ] Update the Chinese README with settings, scope, and `v0.2.23` build usage.

Remote repository creation, authenticated GitHub operations, and publishing require separate authorization.

## 2. Create one production patch

- [ ] Prepare temporary upstream `v0.2.23` source. Edit only the ten targets in [design.md](design.md#boundaries).
- [ ] Add the normalized thought-signature matcher and the four-rule direct-Part cleaner with `json.RawMessage`.
- [ ] Add one policy-ordered recovery resend in `ForwardNative`, using the existing builders and ordinary retry loop.
- [ ] Add the verified Ops events and clear the resend-attempt flag immediately after its outcome.
- [ ] Apply Option B without editing the estimator or existing fallback branches.
- [ ] Add the false-default bool and dedicated read-error-false gate. Leave `GetRectifierSettings`, constructors, providers, and `wire_gen.go` unchanged.
- [ ] Add the plain-bool admin request/response fields through the existing GET/PUT flow.
- [ ] Add the native Vue row, false form default, explicit save field, API type, and locked locale keys.
- [ ] Export `patches/gemini-signature-rectifier.patch` with production changes only.

Format changed native Go files in that temporary source tree:

```sh
gofmt -w backend/internal/service/gemini_messages_compat_service.go backend/internal/service/gemini_native_signature_cleaner.go backend/internal/service/settings_view.go backend/internal/service/setting_features.go backend/internal/handler/dto/settings.go backend/internal/handler/admin/setting_handler_runtime.go
```

## 3. Add focused flat suites

Use synthetic credentials and scripted `HTTPUpstream` responses. Keep tests outside the production patch.

| Suite under `tests/` | Changed behavior to verify |
| --- | --- |
| `test_gemini_native_signature_rectifier_test.go` | Four builders, cleaned-body replay, preserved request routing/authentication, Code Assist envelope, streaming/nonstream success |
| Same suite | HTTP400-only matcher, three signature spellings, unrelated signature rejection, cached-content/policy precedence, fresh resend policy |
| Same suite | Zero ordinary retries, last-attempt recovery, second400 guard, disabled gate, cancellation, closed response bodies |
| Same suite | Both direct field forms, canonical sentinel no-op, marked empty-carrier removal, nonempty text, untouched unmarked Parts and nested JSON/numbers |
| Same suite | Actual-change guard, no remaining contents, invalid JSON, correct Ops kinds/request IDs, no success error event, ordinary retry flag reset |
| Same suite | Counting recovery returns upstream `totalTokens`. Second400 returns 400 without estimation. |
| `test_rectifier_settings_test.go` | `DefaultRectifierSettings().GeminiNativeSignatureEnabled == false`. Gate requires both switches, returns false on read error, and ignores thinking/API Key switches. |
| `test_rectifier_settings_handler_test.go` | Admin GET/PUT round-trips true and false. |
| `test_rectifier_settings.test.ts` | Initial false, enable/save/reload, disable/save/reload, sibling preservation, master-off hiding, locked en/zh copy |

Apply the package annotations in the design. Use the real SettingsView and Toggle. Unmount Vue wrappers in `finally`.

```sh
gofmt -w tests/test_gemini_native_signature_rectifier_test.go tests/test_rectifier_settings_test.go tests/test_rectifier_settings_handler_test.go
```

## 4. Validate through established builds

From the parent root, run the combined entry with a retained temporary workspace:

```sh
UPSTREAM_TAG=v0.2.23 SUB2API_BUILD_STAGE=source SUB2API_BUILD_WORKSPACE=/tmp/gemini-rectifier-combined PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
UPSTREAM_TAG=v0.2.23 SUB2API_BUILD_STAGE=resume SUB2API_BUILD_WORKSPACE=/tmp/gemini-rectifier-combined PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
```

From `plugins/gemini-signature-rectifier`, run the standalone entry:

```sh
UPSTREAM_TAG=v0.2.23 PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/build.py
```

These entries apply patches, run the native frontend build, stage focused Go/Vitest suites, and build program/installer outputs.
The native frontend build includes `check:i18n`, `vue-tsc -b` with `noEmit: true`, and Vite.
Existing discovery runs focused `go test -tags=unit -failfast` and explicit staged Vitest paths, then removes staged files.
Owners: `scripts/build.py:54–80,184–231,263–330` and `tests/support.py:10–67`.
Repair a failing patch before another build. Reuse passing checks for an unchanged candidate.

## 5. Phase 2.2 browser check and handoff

- [ ] Serve the final patched Vue application on loopback with synthetic API/authentication mocks.
- [ ] Use Playwright Chromium at 1440×900 and scale 2. Inspect en/zh in both light and dark themes.
- [ ] Capture the full Request Rectifier card. Check readable contrast, complete icons, unclipped text, sibling row geometry, and switch alignment.
- [ ] Verify zero console/page errors and zero document/card horizontal overflow.
- [ ] Verify initial false. Enable, save true, reload, then disable, save false, and reload.
- [ ] Verify both PUT payloads and reloaded states preserve siblings. Master-off must hide all four sub-options.
- [ ] Stop preview processes and remove temporary runtime files. Retain screenshots and results.
- [ ] Compare the final patch with PRD acceptance and verify production patches contain no tests or private data.
- [ ] Record final build/browser evidence and follow the authorized repository review workflow.

The planning preview already verifies the locked copy and layout. This planning revision requires no rebuild or browser rerun.
For rollback, disable the new sub-option or restore the prior program through the existing installer.
