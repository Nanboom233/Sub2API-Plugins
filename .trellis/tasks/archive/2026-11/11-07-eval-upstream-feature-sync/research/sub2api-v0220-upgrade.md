# Research: Sub2API Baseline Upgrade (`v0.2.19` -> `v0.2.20`)

- **Query**: Read-only investigation of upgrading the upstream Sub2API baseline from `v0.2.19` to `v0.2.20` across `Sub2API-Plugins` and its three plugin submodules (`codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`).
- **Scope**:
  1. Upstream `Wei-Shaw/sub2api` diff `v0.2.19..v0.2.20`, patch application (`git apply -v --check --binary`), shifted/failing hunks, and semantic changes in upstream functions/types/routes called by plugin patches.
  2. Repository-wide inventory of `0.2.19` / `v0.2.19` references across all 4 repositories, distinguishing files that must be updated to `v0.2.20` from files/lines that must remain untouched.
- **Date**: 2026-11-08

---

## 1. Files Found

### Plugin Patches
- `plugins/codex-candy-eval/patches/0001-evaluation-core.patch` — Core evaluation package (`backend/internal/codexeval/*.go`); applies cleanly at `v0.2.20`.
- `plugins/codex-candy-eval/patches/0002-evaluation-data.patch` — Embedded evaluation context and LM detector data (`backend/internal/codexeval/data/**`); applies cleanly at `v0.2.20`.
- `plugins/codex-candy-eval/patches/0003-vendor-assets.patch` — Embedded vendor JS/CSS assets (`backend/internal/codexeval/web/vendor/**`); applies cleanly at `v0.2.20`.
- `plugins/codex-candy-eval/patches/0004-admin-channel.patch` — Admin evaluation handler, upstream transport error wrapper, and `account_codex_eval_service.go`; applies with 1 shifted hunk (`http_upstream.go`) **but contains 2 semantic Go signature breakages in `account_codex_eval_service.go` against `v0.2.20`**.
- `plugins/codex-candy-eval/patches/0005-inspection.patch` — Automatic Candy/Fingerprint inspection coordinator, settings, and admin handlers; applies cleanly at `v0.2.20`.
- `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch` — Embedded standalone evaluation UI (`backend/internal/codexeval/web/**`) and `CodexEvalView.vue`; applies cleanly at `v0.2.20`.
- `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch` — Server lifecycle, router, admin routes, account extra preservation, `embed_on.go`, `AppSidebar.vue`, i18n, and Vue router integration; **fails `git apply --check` on 2 files (`embed_on.go`, `AppSidebar.vue`) and shifts on 3 files (`routes/admin.go`, `admin_account.go`, `router/index.ts`)**.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch` — API-key default upstream `/v1/usage` detection and Goja custom quota script runtime/UI; **fails `git apply --check` on 4 files (`backend/go.mod`, `account_usage_service.go`, `CreateAccountModal.vue`, `EditAccountModal.vue`) and shifts on 9 files**.

### Build Workflows, Scripts, Tests, and Docs with `0.2.19` / `v0.2.19` References
- `.github/workflows/build.yml` (and identical copies in `plugins/codex-candy-eval/.github/workflows/build.yml`, `plugins/sub2api-quota-extension/.github/workflows/build.yml`, `plugins/sub2api-plugin-template/.github/workflows/build.yml`) — CI workflow with `workflow_dispatch.inputs.upstream_tag.default`.
- `plugins/codex-candy-eval/tests/native_inspection_fixture.py` — Local container fixture helper resolving built `sub2api-plugins-v0.2.19-linux-*` binaries.
- `tests/test_installer_test.go` (and identical copies in `plugins/codex-candy-eval/tests/test_installer_test.go`, `plugins/sub2api-quota-extension/tests/test_installer_test.go`, `plugins/sub2api-plugin-template/tests/test_installer_test.go`) — Native Go installer test suite containing a version-warning test fixture at line 661.
- `README.md` — Root Chinese user documentation with default workflow tag, artifact table examples, and `UPSTREAM_TAG` example.
- `plugins/sub2api-plugin-template/README.md` — Template repository Chinese README with `UPSTREAM_TAG` example.
- `.trellis/spec/backend/index.md` — Backend spec index recording the verified integration baseline.
- `.trellis/spec/backend/minimal-linux-delivery.md` — Binary delivery spec recording the verified baseline, workflow default, CLI examples, and `backend/cmd/server/VERSION` note.
- `.trellis/spec/backend/quality-guidelines.md` — Quality guidelines recording the verified integration baseline.
- `.trellis/spec/backend/runtime-installation.md` — Administrator evaluation spec recording the target Sub2API baseline.
- `.trellis/spec/backend/api-key-quota.md` — API-key quota spec recording the target Sub2API baseline.

---

## 2. Upstream Sub2API `v0.2.19` -> `v0.2.20` Diff & Patch Compatibility Analysis

### 2.1 Upstream Release Metadata (`v0.2.19..v0.2.20`)
- Tag `v0.2.20` resolves to commit `dab829a4` (`Merge pull request #8365 from lyy0709/codex/gpt61-terra-followup`).
- Between `v0.2.19` and `v0.2.20`, 459 files changed (`29,482 insertions(+), 1,457 deletions(-)`).
- `backend/cmd/server/VERSION` at `v0.2.20` contains `0.2.19` (upstream synced `VERSION` to `0.2.19` in commit `a9240d501`, just as `v0.2.19` retained `0.2.18`).
- `backend/go.mod` retains `go 1.27.3`. `frontend/package.json` upgrades `vue-i18n` and `@intlify/message-compiler` to `11.4.16` and adds `"decode-uri-component@<0.5.1": ">=0.5.1"` to `pnpm.overrides`.

### 2.2 Patch-by-Patch `git apply -v --check --binary` Results Against `/tmp/sub2api-v0.2.20-base`

| Patch | `git apply --check` Status | Failing Files | Shifted Files (Offsets) | Semantic / Compile Issues on `v0.2.20` |
| --- | --- | --- | --- | --- |
| `codex-candy-eval/patches/0001-evaluation-core.patch` | PASS (`rc=0`) | None | None | None |
| `codex-candy-eval/patches/0002-evaluation-data.patch` | PASS (`rc=0`) | None | None | None |
| `codex-candy-eval/patches/0003-vendor-assets.patch` | PASS (`rc=0`) | None | None | None |
| `codex-candy-eval/patches/0004-admin-channel.patch` | PASS (`rc=0`) | None | `backend/internal/repository/http_upstream.go` (Hunk #1 `+12` lines) | **YES — 2 Go compile errors in `backend/internal/service/account_codex_eval_service.go`** (see §2.3) |
| `codex-candy-eval/patches/0005-inspection.patch` | PASS (`rc=0`) | None | None | None |
| `codex-candy-eval/patches/0006-evaluation-ui.patch` | PASS (`rc=0`) | None | None | None |
| `codex-candy-eval/patches/0007-sub2api-integration.patch` | **FAIL (`rc=1`)** | `backend/internal/web/embed_on.go`, `frontend/src/components/layout/AppSidebar.vue` | `backend/internal/server/routes/admin.go` (`+2`, `+5`, `+6`), `backend/internal/service/admin_account.go` (`+5`), `frontend/src/router/index.ts` (`+23`) | None once hunks are rebased |
| `sub2api-quota-extension/patches/quota-extension.patch` | **FAIL (`rc=1`)** | `backend/go.mod`, `backend/internal/service/account_usage_service.go`, `frontend/src/components/account/CreateAccountModal.vue`, `frontend/src/components/account/EditAccountModal.vue` | `wire_gen.go` (`+4`), `go.sum` (`+2`, `+2`), `routes/admin.go` (`-7` standalone / `-1` combined), `admin_account.go` (`+2`), `wire.go` (`+4`, `+4`), `api/admin/accounts.ts` (`+3`, `+3`), `AccountUsageCell.vue` (`+17`..`+53`), `en/admin/accounts.ts` (`+62`), `types/index.ts` (`+51`) | `getUsageForAccount` in `account_usage_service.go` added `scopedAccountAccess` guard (see §2.5) |

---

### 2.3 Detailed Findings for `0004-admin-channel.patch`

1. **Shifted Hunk — `backend/internal/repository/http_upstream.go`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `457602c8f` (`fix(backend): bound gateway resources and background work`) imported `pkghttputil "github.com/Wei-Shaw/sub2api/internal/pkg/httputil"`, added `upstreamDrainTimeout()` at lines 300–305, and updated `doUpstreamRequest` at lines 309–323:
     ```go
     func doUpstreamRequest(client *http.Client, req *http.Request, drainTimeouts ...time.Duration) (*http.Response, error) {
     	var drainTimeout time.Duration
     	if len(drainTimeouts) > 0 {
     		drainTimeout = drainTimeouts[0]
     	}
     	ctx, cancel := pkghttputil.NewUpstreamAttemptContext(req.Context(), drainTimeout)
     	resp, err := servertiming.Do(client, req.WithContext(ctx))
     	if err != nil {
     		cancel()
     		return resp, err
     	}
     ```
   - **Impact**: Hunk #1 of `0004-admin-channel.patch` (`return resp, &service.HTTPUpstreamRequestError{Err: err}`) still applies at line 315 with `+12` lines offset, and `doUpstreamRequest` is variadic (`drainTimeouts ...time.Duration`), so existing callers remain compatible. Rebasing the hunk removes the line offset.

2. **CRITICAL Semantic Breakage #1 in `backend/internal/service/account_codex_eval_service.go` (New File in `0004-admin-channel.patch`) — `convertClaudeMessagesToGeminiGenerateContent` Signature Changed**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `aae31c743` (`fix(gemini): preserve tool media in native function responses`) changed `backend/internal/service/gemini_messages_compat_service.go:3472`:
     ```go
     // v0.2.19:
     func convertClaudeMessagesToGeminiGenerateContent(body []byte) ([]byte, error)
     // v0.2.20:
     func convertClaudeMessagesToGeminiGenerateContent(body []byte, model string) ([]byte, error)
     ```
   - **Impact on `0004-admin-channel.patch`**: In `account_codex_eval_service.go` (`0004-admin-channel.patch:752`), `sendCodexGeminiEvaluation` calls:
     ```go
     geminiPayload, err := convertClaudeMessagesToGeminiGenerateContent(claudeBody)
     ```
     On `v0.2.20`, this fails Go compilation (`not enough arguments in call to convertClaudeMessagesToGeminiGenerateContent`). It must pass `(claudeBody, model)`:
     ```go
     geminiPayload, err := convertClaudeMessagesToGeminiGenerateContent(claudeBody, model)
     ```

3. **CRITICAL Semantic Breakage #2 in `backend/internal/service/account_codex_eval_service.go` (New File in `0004-admin-channel.patch`) — `computeGeminiTextDelta` Removed and Replaced by `geminiTextDelta`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `457602c8f` (`fix(backend): bound gateway resources and background work`) removed `func computeGeminiTextDelta(seen, incoming string) (delta, newSeen string)` from `backend/internal/service/gemini_messages_compat_service.go:3430-3459` and replaced it with:
     ```go
     type geminiTextDelta struct {
     	seen strings.Builder
     }
     func (d *geminiTextDelta) next(incoming string) string
     func (d *geminiTextDelta) reset()
     ```
   - **Impact on `0004-admin-channel.patch`**: In `account_codex_eval_service.go` (`0004-admin-channel.patch:1029-1030, 1133-1140`), `codexGeminiStream` declares `seenText string` and `seenThought string` and calls `computeGeminiTextDelta(s.seenThought, text)` and `computeGeminiTextDelta(s.seenText, text)`.
     On `v0.2.20`, this fails Go compilation (`undefined: computeGeminiTextDelta`). `codexGeminiStream` must instead use `seenText geminiTextDelta` and `seenThought geminiTextDelta` and call `delta := s.seenThought.next(text)` and `delta := s.seenText.next(text)`.

---

### 2.4 Detailed Findings for `0007-sub2api-integration.patch`

1. **Failing Hunk #1 — `backend/internal/web/embed_on.go:355`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `f17918ea1` (`feat(backend): add OAuth-authenticated management MCP`) added three `.well-known` MCP OAuth bypass conditions immediately after `strings.HasPrefix(trimmed, "/api/") ||` in `shouldBypassEmbeddedFrontend(path string)` (`backend/internal/web/embed_on.go:355-361`):
     ```go
     func shouldBypassEmbeddedFrontend(path string) bool {
     	trimmed := strings.TrimSpace(path)
     	return strings.HasPrefix(trimmed, "/api/") ||
     		trimmed == "/.well-known/oauth-protected-resource" ||
     		trimmed == "/.well-known/oauth-protected-resource/api/v1/mcp" ||
     		trimmed == "/.well-known/oauth-authorization-server" ||
     		strings.HasPrefix(trimmed, "/v1/") ||
     ```
   - **Impact**: `0007-sub2api-integration.patch` expects `strings.HasPrefix(trimmed, "/v1/") ||` immediately after `strings.HasPrefix(trimmed, "/api/") ||` in its trailing context and fails to apply. Rebasing the hunk context onto `v0.2.20` resolves the conflict cleanly.

2. **Failing Hunk #2 — `frontend/src/components/layout/AppSidebar.vue:481`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `cf3300633` / `8a34f1ecf` added `MCPIcon` right between `PluginIcon` and `BellIcon` (`frontend/src/components/layout/AppSidebar.vue:480-488`):
     ```ts
     const PluginIcon = {
       render: () => h(Icon, { name: 'cube' })
     }

     const MCPIcon = {
       render: () => h(Icon, { name: 'mcp' })
     }

     const BellIcon = {
     ```
   - **Impact**: Hunk #1 of `AppSidebar.vue` in `0007-sub2api-integration.patch` inserts `EvaluationIcon` between `PluginIcon` and `BellIcon`, failing context match. Hunk #2 of `AppSidebar.vue` (inserting `{ path: '/admin/codex-eval', label: t('nav.accountEvaluation'), icon: EvaluationIcon }` after `/admin/accounts` at line 801) has unchanged surrounding lines (`subscriptions`, `accounts`, `plugins`, `announcements`, `proxies`), shifted by `+8` lines.

3. **Shifted Hunks in `0007-sub2api-integration.patch`**:
   - `backend/internal/server/routes/admin.go`:
     - Hunk #1 (`RegisterAdminRoutes` at line 49): offset `+2` lines.
     - Hunk #2 (`registerAccountRoutes` at line 398): offset `+5` lines (upstream added `users.POST("/batch-disable", ...)` and `users.POST("/blacklist-matches", ...)` at lines 319–320).
     - Hunk #3 (`registerSettingsRoutes` at line 577): offset `+6` lines (note also signature `func registerSettingsRoutes(admin *gin.RouterGroup, h *handler.Handlers, stepUpAuth middleware.StepUpAuthMiddleware)` at line 572).
   - `backend/internal/service/admin_account.go`:
     - Hunk #1 (`UpdateAccount` extra-key preservation at line 694): offset `+5` lines.
   - `frontend/src/router/index.ts`:
     - Hunk #1 (`AdminCodexEval` route after `/admin/accounts` at line 548): offset `+23` lines (upstream added `/settings/mcp` and `/oauth/mcp/authorize` at lines 279–301).
   - `backend/internal/server/router.go`:
     - Applies at line 113 without offset; note that upstream added `routes.RegisterMCPRoutes` and `routes.RegisterMCPOAuthRoutes` further down at lines 131–132.

---

### 2.5 Detailed Findings for `sub2api-quota-extension/patches/quota-extension.patch`

1. **Failing Hunk #1 — `backend/go.mod:128`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Upstream added `github.com/MoeForge/moego v0.1.0-alpha.1` and `github.com/modelcontextprotocol/go-sdk v1.4.1`, and upgraded `andybalholm/brotli` (`v1.2.7`) and `klauspost/compress` (`v1.20.2`). In the indirect `require` block (`backend/go.mod:130-136`), upstream inserted `github.com/google/jsonschema-go v0.4.2 // indirect` right after `github.com/google/go-tpm v0.9.8 // indirect`:
     ```go
     	github.com/google/go-cmp v0.7.0 // indirect
     	github.com/google/go-querystring v1.1.0 // indirect
     	github.com/google/go-tpm v0.9.8 // indirect
     	github.com/google/jsonschema-go v0.4.2 // indirect
     	github.com/grpc-ecosystem/grpc-gateway/v2 v2.27.3 // indirect
     ```
   - **Impact**: Hunk #4 of `backend/go.mod` in `quota-extension.patch` (inserting `github.com/google/pprof v0.0.0-20250317173921-a4b03ec1a45e // indirect` after `github.com/google/go-tpm v0.9.8 // indirect`) fails context matching. Rebasing `backend/go.mod` against `v0.2.20` fixes it cleanly (`backend/go.sum` hunks still apply with `+2` offset).

2. **Failing Hunk #2 — `backend/internal/service/account_usage_service.go`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**:
     - At line 16 (Hunk #1), upstream imported `"github.com/Wei-Shaw/sub2api/internal/pkg/adminaccess"` immediately before `httppool "github.com/Wei-Shaw/sub2api/internal/pkg/httpclient"`, breaking the import hunk context.
     - At lines 158–171 and 215–217, upstream added `AntigravityQuotaGroup`, `AntigravityQuotaWindow`, and `AntigravityQuotaGroups`, shifting subsequent hunks by `+19` lines.
     - At lines 364–369 (Hunk #4), upstream added a scoped-admin-key access check at the top of `getUsageForAccount`:
       ```go
       func (s *AccountUsageService) getUsageForAccount(ctx context.Context, account *Account, forceProbe bool) (*UsageInfo, error) {
       	if err := scopedAccountAccess(ctx, s.accountRepo, account, "accounts.usage.read", true); err != nil {
       		return nil, err
       	}
       	if account == nil {
       		return nil, fmt.Errorf("account is required")
       	}
       ```
   - **Impact**: Both Hunk #1 (imports) and Hunk #4 (`getUsageForAccount` wrapper) fail context matching. When rebasing Hunk #4 onto `v0.2.20`, `if err := scopedAccountAccess(ctx, s.accountRepo, account, "accounts.usage.read", true); err != nil { return nil, err }` should remain at the entry of `getUsageForAccount` (before `AccountQuotaScript(account)` and `getNativeUsageForAccount`) so restricted admin keys are checked before any custom script or upstream quota query runs, while normal calls (`RestrictedFromContext(ctx) == nil`) remain a no-op.

3. **Failing Hunk #3 — `frontend/src/components/account/CreateAccountModal.vue:4154`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `e452e41e4` (`feat(openai): 生图账号按 1K/2K/4K 尺寸档位分流`) added `<OpenAIImageSizeTiersField v-model="openAIImageSizeTiers" />` at lines 3665–3671 and imported `OpenAIImageSizeTiersField` and `openaiImageSizeTiers` helpers right after `UpstreamRequestIdHeaderField` (`CreateAccountModal.vue:4164-4172`):
     ```ts
     import UpstreamRequestIdHeaderField from '@/components/account/UpstreamRequestIdHeaderField.vue'
     import OpenAIImageSizeTiersField from '@/components/account/OpenAIImageSizeTiersField.vue'
     import {
       OPENAI_IMAGE_SIZE_TIERS,
       applyOpenAIImageSizeTiersToExtra,
       type OpenAIImageSizeTier
     } from '@/components/account/openaiImageSizeTiers'
     import PlatformIcon from '@/components/common/PlatformIcon.vue'
     ```
   - **Impact**: Hunk #2 of `CreateAccountModal.vue` in `quota-extension.patch` (importing `QuotaScriptEditor` between `UpstreamRequestIdHeaderField` and `PlatformIcon`) fails context matching. Hunks #3, #4, and #5 shift by `+14` to `+20` lines.

4. **Failing Hunk #4 — `frontend/src/components/account/EditAccountModal.vue:3254`**:
   - **Upstream change (`v0.2.19..v0.2.20`)**: Commit `e452e41e4` similarly imported `OpenAIImageSizeTiersField` and `openaiImageSizeTiers` helpers right after `UpstreamRequestIdHeaderField` (`EditAccountModal.vue:3417-3426`):
     ```ts
     import UpstreamRequestIdHeaderField from '@/components/account/UpstreamRequestIdHeaderField.vue'
     import OpenAIImageSizeTiersField from '@/components/account/OpenAIImageSizeTiersField.vue'
     import {
       OPENAI_IMAGE_SIZE_TIERS,
       applyOpenAIImageSizeTiersToExtra,
       readOpenAIImageSizeTiers,
       type OpenAIImageSizeTier
     } from '@/components/account/openaiImageSizeTiers'
     import Toggle from '@/components/common/Toggle.vue'
     ```
   - **Impact**: Hunk #2 of `EditAccountModal.vue` in `quota-extension.patch` (importing `QuotaScriptEditor` between `UpstreamRequestIdHeaderField` and `Toggle`) fails context matching. Hunk #1 shifts by `+152` lines and Hunks #3–#6 shift by `+160` to `+311` lines.

5. **Shared-File Cooperation Between `0007-sub2api-integration.patch` and `quota-extension.patch`**:
   - Both plugins touch `backend/internal/server/routes/admin.go` and `backend/internal/service/admin_account.go`.
   - In `routes/admin.go`, `0007-sub2api-integration.patch` inserts 3 routes after `accounts.POST("/:id/test", ...)` (around line 398), while `quota-extension.patch` inserts `accounts.POST("/quota-script/test", ...)` after `accounts.POST("/usage/batch", ...)` (around line 409). Because 11 unchanged lines separate the two insertion points, `quota-extension.patch` works in both standalone mode and combined mode (after `0007-sub2api-integration.patch`).
   - In `admin_account.go`, `quota-extension.patch` modifies `CreateAccount` (line 496) and `UpdateAccount` (line 607), while `0007-sub2api-integration.patch` modifies `UpdateAccount` (line 694). Over 80 unchanged lines separate the hunks, so both standalone and combined modes remain compatible.

---

## 3. Repository-Wide `v0.2.19` / `0.2.19` Reference Inventory

### 3.1 Files That MUST Be Updated to `v0.2.20` / `0.2.20`

| Repository | File Path | Line(s) | Current Content (`v0.2.19` / `0.2.19`) | Required Action |
| --- | --- | --- | --- | --- |
| `Sub2API-Plugins` | `.github/workflows/build.yml` | `11` | `default: v0.2.19` | Update default `upstream_tag` to `v0.2.20` |
| `plugins/codex-candy-eval` | `.github/workflows/build.yml` | `11` | `default: v0.2.19` | Update default `upstream_tag` to `v0.2.20` (keep aligned across all 4 repos) |
| `plugins/sub2api-quota-extension` | `.github/workflows/build.yml` | `11` | `default: v0.2.19` | Update default `upstream_tag` to `v0.2.20` (keep aligned across all 4 repos) |
| `plugins/sub2api-plugin-template` | `.github/workflows/build.yml` | `11` | `default: v0.2.19` | Update default `upstream_tag` to `v0.2.20` (keep aligned across all 4 repos) |
| `plugins/codex-candy-eval` | `tests/native_inspection_fixture.py` | `48-51` | `sub2api-plugins-v0.2.19-linux-{arch}` / `{other}` | Update explicit candidate binary paths to `sub2api-plugins-v0.2.20-linux-{arch}` / `{other}` |
| `Sub2API-Plugins` | `tests/test_installer_test.go` | `661` | `fakeState{Installed: "0.2.17", Candidate: "0.2.19", Image: "sub2api:0.2.18"}` | Update `Candidate: "0.2.20"` (or `Installed: "0.2.18", Candidate: "0.2.20", Image: "sub2api:0.2.19"`) and keep all 4 repo copies byte-identical |
| `plugins/codex-candy-eval` | `tests/test_installer_test.go` | `661` | `fakeState{Installed: "0.2.17", Candidate: "0.2.19", Image: "sub2api:0.2.18"}` | Sync aligned copy with root `tests/test_installer_test.go` |
| `plugins/sub2api-quota-extension` | `tests/test_installer_test.go` | `661` | `fakeState{Installed: "0.2.17", Candidate: "0.2.19", Image: "sub2api:0.2.18"}` | Sync aligned copy with root `tests/test_installer_test.go` |
| `plugins/sub2api-plugin-template` | `tests/test_installer_test.go` | `661` | `fakeState{Installed: "0.2.17", Candidate: "0.2.19", Image: "sub2api:0.2.18"}` | Sync aligned copy with root `tests/test_installer_test.go` |
| `Sub2API-Plugins` | `README.md` | `21, 23, 27-31, 38-39, 45, 123` | `默认值为 v0.2.19`, artifact table `sub2api-plugins-installer-v0.2.19-*`, CLI examples, `UPSTREAM_TAG=v0.2.19 python3 scripts/build.py` | Update default tag note and example commands/filenames to `v0.2.20` |
| `plugins/sub2api-plugin-template` | `README.md` | `17` | `UPSTREAM_TAG=v0.2.19 python3 scripts/build.py` | Update example tag to `v0.2.20` |
| `Sub2API-Plugins` | `.trellis/spec/backend/index.md` | `6` | `The verified integration baseline is Sub2API v0.2.19.` | Update during Phase 3.3 spec sync to `v0.2.20` |
| `Sub2API-Plugins` | `.trellis/spec/backend/minimal-linux-delivery.md` | `6, 16-17, 35, 42, 77, 315, 359` | Baseline `v0.2.19`, installer CLI examples, `upstream_tag` default `v0.2.19`, `UPSTREAM_TAG=v0.2.19`, `The v0.2.19 source retains 0.2.18 in backend/cmd/server/VERSION` | Update during Phase 3.3 spec sync to `v0.2.20` (note: line 77 becomes `The v0.2.20 source retains 0.2.19 in backend/cmd/server/VERSION.`) |
| `Sub2API-Plugins` | `.trellis/spec/backend/quality-guidelines.md` | `7` | `Sub2API v0.2.19 remains the verified integration baseline.` | Update during Phase 3.3 spec sync to `v0.2.20` |
| `Sub2API-Plugins` | `.trellis/spec/backend/runtime-installation.md` | `5` | `Use this contract for the evaluation plugin on Sub2API v0.2.19.` | Update during Phase 3.3 spec sync to `v0.2.20` |
| `Sub2API-Plugins` | `.trellis/spec/backend/api-key-quota.md` | `5` | `... on Sub2API v0.2.19.` | Update during Phase 3.3 spec sync to `v0.2.20` |
| `Sub2API-Plugins` | `.trellis/tasks/11-07-eval-upstream-feature-sync/{implement.md,design.md}` | `implement.md:33,60`, `design.md:102` | Residual `v0.2.19` references in task planning docs | Update task docs if desired during planning synchronization |

### 3.2 Files Checked That Have NO `0.2.19` References or Must Remain Untouched

| File / Path | Findings & Guidance |
| --- | --- |
| `tests/test_build.py` (all 4 repos) | Uses synthetic `TAG = "v1.2.3-rc.4"` (`tests/test_build.py:22`); contains **no** `0.2.19` reference. Must remain aligned across all 4 repos if modified. |
| `scripts/build.py` (all 4 repos) | Resolves `UPSTREAM_TAG` dynamically from environment or GitHub latest release API (`scripts/build.py:25-40`); contains **no** hardcoded `0.2.19`. |
| `scripts/installer/main.go`, `messages.go`, `ui.go` (all 4 repos) | Uses linker-injected `main.buildVersion`; contains **no** `main_test.go` (tests live in `tests/test_installer_test.go`) and **no** hardcoded `0.2.19`. |
| `tests/test_installer_test.go:585-597` (`TestVersionParsing`) | Uses synthetic `"0.2.17"` / `"0.2.18"` strings to test version parser edge cases (`commit-is-not-version`, `conflicting`, etc.). Keep untouched. |
| `.trellis/spec/backend/index.md:31,63` & `minimal-linux-delivery.md:372` | Historical exclusions referencing `v0.2.17` (`supersede historical v0.2.17 build rules`, `No ... v0.2.17 comparison build`). Keep untouched. |
| `plugins/codex-candy-eval/README.md` | Contains **no** `0.2.19` references. Keep untouched unless evaluation feature docs change for task requirements. |
| `plugins/sub2api-quota-extension/` | Has no `README.md`. |
| `.trellis/tasks/11-07-eval-upstream-feature-sync/research/live-browser-verification.md` | Historical research log from an earlier verification run (`Loaded Binary: ... v0.2.19`). Keep untouched as historical evidence. |
| `.trellis/tasks/archive/**` & `.trellis/workspace/**` | Archived tasks and historical session journals. Keep untouched. |

---

## 4. Related Specs

- `.trellis/spec/backend/index.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/backend/runtime-installation.md`
- `.trellis/spec/backend/native-inspection.md`
- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/directory-structure.md`
- `.trellis/spec/frontend/index.md`

---

## 5. Caveats & Notes

1. **Hidden Compile Errors Beyond `git apply --check`**:
   - `plugins/codex-candy-eval/patches/0004-admin-channel.patch` passes `git apply --check --binary` (`rc=0`) because `backend/internal/service/account_codex_eval_service.go` is a newly created file. However, `v0.2.20` changed two internal `service` package helpers in `backend/internal/service/gemini_messages_compat_service.go`:
     - `convertClaudeMessagesToGeminiGenerateContent(claudeBody)` -> `convertClaudeMessagesToGeminiGenerateContent(claudeBody, model)`
     - `computeGeminiTextDelta(seen, text)` -> replaced by `geminiTextDelta` struct with `.next(text)` method.
   - Updating `0004-admin-channel.patch` for those two calls is mandatory for `go test` and `go build` to succeed on `v0.2.20`.
2. **Common Build-Kit Alignment Rule**:
   - `.github/workflows/build.yml`, `scripts/build.py`, `scripts/installer/*`, `tests/support.py`, `tests/test_build.py`, and `tests/test_installer_test.go` are currently 100% byte-for-byte identical across `Sub2API-Plugins`, `plugins/codex-candy-eval`, `plugins/sub2api-quota-extension`, and `plugins/sub2api-plugin-template`. Any update to `.github/workflows/build.yml` or `tests/test_installer_test.go` must be synchronized across all 4 repositories.
3. **Standalone vs Combined Patch Application**:
   - When regenerating `plugins/sub2api-quota-extension/patches/quota-extension.patch`, ensure context lines around `backend/internal/server/routes/admin.go` and `backend/internal/service/admin_account.go` apply cleanly both on a standalone `v0.2.20` tree and after `plugins/codex-candy-eval/patches/0001..0007` are applied.
