# Planning & Deep-Dive Brief: Gemini Native Thought Signature Rectifier

Active task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Coordinator terminal: `t53`

## Role and Boundaries

- **Stage**: Phase 1.1 / 1.2 / 1.3 Planning ONLY.
- **Strictly read-only on codebase**: Do NOT create the plugin submodule, do NOT write patches or production/test code, do NOT run `task.py start`, do NOT modify Git state or remotes.
- **GitHub credential rule**: Do NOT use `gh` CLI or authenticated Git/GitHub credentials. Use ONLY local repository reads and unauthenticated public reads (`raw.githubusercontent.com` / public web).
- **Subagent safety**: Do NOT spawn extra `hc` terminals. Forbid any internal subagent from calling `hc send`.
- **Temporary caches**: Use `PYTHONDONTWRITEBYTECODE=1` / `python3 -B` for Python and leave no `__pycache__` or stray files.
- **Callback**: When all files below are written and checked, report via:
  `hc send t53 "Planning ready: count-tokens-and-settings.md, prd.md, design.md, implement.md, implement.jsonl, check.jsonl — <short summary>"`

## User Decisions Locked So Far

1. **Plugin ownership**: New independent plugin submodule under `plugins/` (following `plugins/sub2api-plugin-template` layout and `.trellis/spec/backend/directory-structure.md`). Note that any future GitHub repo creation or remote push requires explicit separate user credential approval; design local creation/build cleanly first.
2. **Setting toggle**: Add a dedicated sub-option under **Request Rectifier (请求整流器)** in admin settings (`/admin/settings/rectifier`, `rectifier_settings` JSON, backend `SettingService` + handler, Vue `SettingsView.vue`, `settings.ts`, and matching `en`/`zh` i18n keys).
3. **Forwarding scope**: Cover all 4 native paths in `GeminiMessagesCompatService.ForwardNative`:
   - API Key (AI Studio / relay URLs)
   - OAuth AI Studio
   - OAuth Code Assist (`/v1internal` wrapped envelope)
   - Vertex ServiceAccount
   Do NOT alter Claude compat `Forward`, `gemini_v1beta_handler.go` pre-cleaning, or `AntigravityGatewayService.ForwardGemini`. Keep existing exported `CleanGeminiNativeThoughtSignatures` unchanged; add a dedicated Part-aware recovery cleaner for `ForwardNative`.
4. **HTTP status and policy scope**: HTTP 400 only (`仅400策略`), with explicit error-policy-first precedence (`checkErrorPolicyInLoop` stays ahead of signature recovery; only rectify unmatched signature-related HTTP 400s, and evaluate fresh policy on the retry response).
5. **Item 5 (`countTokens` fallback)**: **User requested a detailed inspection and explanation before locking this decision.**

## Required Deliverables

### Deliverable 1: Deep-Dive Research Supplement
Write `.trellis/tasks/11-20-gemini-thought-signature-rectifier/research/count-tokens-and-settings.md` with primary-source citations from `Wei-Shaw/sub2api@v0.2.23`:

1. **Detailed `countTokens` inspection (for user decision on Item 5)**:
   - Exact line-by-line behavior of `action == "countTokens"` in `ForwardNative` across all 4 native account builders (including Code Assist forcing AI Studio `forceAIStudio := action == "countTokens"`).
   - Exact existing fallback rules in `v0.2.23`: transport error, exhausted transient retries, OAuth 403 insufficient scope, and ordinary 400.
   - Exact implementation of `estimateGeminiCountTokens(body)` in `v0.2.23`: formula, how it handles large base64 images or thought signatures, HTTP status/body returned, usage/billing impact, and edge cases.
   - Concrete side-by-side comparison of options when `countTokens` hits a signature 400:
     - **Option A**: Clean & retry once; if retry succeeds return upstream count; if retry fails (400/5xx/transport) fall back to `estimateGeminiCountTokens` (PR #1309 style).
     - **Option B**: Clean & retry once; if retry succeeds return upstream count; if retry fails return actual upstream error (except existing transport/transient/403 fallbacks — no local estimate on 400).
     - **Option C**: Do not run signature retry for `countTokens` (either pass through 400 or directly estimate).
   - Clear factual pros, cons, client impact (AstrBot, Gemini CLI, official SDKs), and a recommended default.

2. **Detailed `rectifier_settings` sub-option inspection (`v0.2.23`)**:
   - Exact backend definitions and handlers: `settings_view.go`, `setting_features.go`, `setting_handler_runtime.go`, `admin.go`, plus any existing Go tests for rectifier settings.
   - **Critical backward-compatibility check**: In `v0.2.23`, how does `GetRectifierSettings` unmarshal existing saved DB JSON when a new boolean field is added? Verify whether existing saved JSON without the new field would unmarshal to `false` (Go zero value), and design the exact cleanest way to give the new sub-option a predictable default (e.g., default `true` vs default `false`, pointer `*bool` or explicit default handling on unmarshal — check how upstream handles `enabled`, `thinking_signature_enabled`, `apikey_signature_enabled`).
   - Exact frontend touchpoints: `frontend/src/api/admin/settings.ts`, `frontend/src/views/admin/SettingsView.vue`, `frontend/src/i18n/locales/en/` and `zh/` (check exact filenames and key paths so `pnpm run check:i18n` passes!).
   - Verify zero patch conflicts with `plugins/codex-candy-eval` and `plugins/sub2api-quota-extension` across ALL touched upstream files (including `wire_gen.go` and any frontend files).

### Deliverable 2: Phase 1 Planning Artifacts (Lean & Bloat-Free)
Write/update inside `.trellis/tasks/11-20-gemini-thought-signature-rectifier/`:

1. **`prd.md`**:
   - Requirements, constraints, non-goals, and testable acceptance criteria ONLY (no low-level code design or execution checklists).
   - Clearly mark Item 5 (`countTokens` post-retry failure behavior) and plugin directory/submodule name (e.g., `sub2api-gemini-signature-rectifier`) as `[PENDING USER CONFIRMATION]` with concrete options and recommended default.
   - Confirm sub-option default behavior for fresh installs AND existing `rectifier_settings` DB records.

2. **`design.md`**:
   - Minimal, cohesive technical design on Sub2API `v0.2.23`:
     - Exact file/function boundaries (no speculative packages, no pass-through wrappers, no unused constants/env vars, no exported internal types unless cross-package callers need them).
     - Exact Part-aware recovery cleaner algorithm & edge cases (`thoughtSignature`/`thought_signature`, `functionCall`/`function_call`, `thought: true` with text vs empty metadata-only Part, `contents` becoming empty, nested tool args untouched, semantic-change boolean return instead of raw byte diff).
     - Exact `ForwardNative` control flow: cachedContent passthrough -> `checkErrorPolicyInLoop` -> signature-400 matcher + setting gate + single-recovery guard -> clean & rebuild request via existing account builder -> fresh policy check on retry response -> Ops events (`signature_error`, `signature_retry`, `signature_retry_request_error`) -> final error / `countTokens` branch.
     - Exact `rectifier_settings` backend + admin handler + Vue UI + `en`/`zh` i18n contract.
     - Exact plugin submodule layout (aligned with `sub2api-plugin-template` and `.trellis/spec/backend/directory-structure.md`: `patches/*.patch`, flat `tests/test_*_test.go` with `// sub2api-package:`, flat `tests/test_*.test.ts` for Vue toggle if needed, `LICENSE` LGPLv3 + `licenses/`, `scripts/` kit, parent `.gitmodules`).
     - Compatibility, rollout, and rollback shape.

3. **`implement.md`**:
   - Ordered checklist of implementation steps, explicit validation commands (`gofmt`, `python3 scripts/build.py` which runs `pnpm run check:i18n`, `vue-tsc --noEmit`, `vite build`, staged Go + Vitest tests, and standalone plugin build), review gates, and rollback points.

4. **`implement.jsonl` and `check.jsonl`**:
   - Curate with real repo-relative `.trellis/spec/` and `.trellis/tasks/11-20-gemini-thought-signature-rectifier/research/*.md` entries ONLY (one JSON object per line `{"file": "...", "reason": "..."}`, NO code paths!).

## Anti-Bloat & Spec Compliance Rules

- Reject split files/directories that belong in one cohesive module.
- No runtime version checks, no artificial path restrictions, no speculative preflight gates.
- No unused constants, unused env vars, pass-through wrappers, re-exports, single-call helpers, or redundant parameters.
- Follow `.trellis/spec/backend/index.md`, `.trellis/spec/backend/directory-structure.md`, `.trellis/spec/backend/quality-guidelines.md`, `.trellis/spec/frontend/quality-guidelines.md`, and `.trellis/spec/guides/index.md`.
- Write task documents in clear, concise English with real file/line citations.
