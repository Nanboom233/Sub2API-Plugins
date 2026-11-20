# Research Brief: Gemini Native Thought Signature Rectifier

Active task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Coordinator terminal: `t53`

## Role and Boundaries

- **Stage**: Phase 1.2 Research ONLY.
- **Strictly read-only on codebase**: Do NOT edit production code, patches, tests, `prd.md`, `design.md`, `implement.md`, or Git state. Do NOT run `task.py start` or commit anything.
- **Output file**: Write all findings to `.trellis/tasks/11-20-gemini-thought-signature-rectifier/research/existing-work.md`.
- **GitHub credential rule** (from `.trellis/spec/guides/index.md`): Do NOT use `gh` CLI or authenticated GitHub/Git credentials. Use ONLY local repository inspection and unauthenticated public web/HTTP reads (web search, public `github.com` / `raw.githubusercontent.com`).
- **Subagent safety**: Do NOT spawn extra `hc` terminals. If you use any internal subagent, explicitly forbid it from running `hc send`.
- **Temporary caches**: If you run Python, set `PYTHONDONTWRITEBYTECODE=1` or use `python3 -B`, and remove any temporary cache or scratch files created in the workspace before finishing.
- **Callback**: When the research report is written, report back to the coordinator via:
  `hc send t53 "Research complete: .trellis/tasks/11-20-gemini-thought-signature-rectifier/research/existing-work.md — <concise 1-2 line summary>"`
  If blocked, report the exact blocker with `hc send t53 "<blocker>"`.

## Background Context (Already Diagnosed)

- Baseline in this repo: Sub2API `v0.2.23` (see `.trellis/spec/backend/index.md` and `.trellis/spec/backend/directory-structure.md`).
- Live failure observed: AstrBot `v4.29.4` calling Sub2API `v0.2.23` native Gemini endpoint (`/v1beta/models` -> `GeminiMessagesCompatService.ForwardNative`) with `gemini-4-hydrogen` across a group containing both `AIStudio2API` (Gemini Key, emits protobuf-wrapped Tink signatures `0x12 ... 0x0a ...`) and `Vertex` (Agent Platform / ServiceAccount, emits raw Tink signatures `0x01 ...`).
- Upstream errors observed:
  - AI Studio upstream: `400 INVALID_ARGUMENT` — `Corrupted thought signature.`
  - Vertex AI upstream: `400 INVALID_ARGUMENT` — `Invalid thought signature.`
- Preliminary check showed Sub2API `v0.2.23` has Claude-compat signature retry in `Forward`, while `ForwardNative` has `ensureGeminiFunctionCallThoughtSignatures` but no signature 400 rectifier/retry.

## Research Questions to Answer with Primary Evidence

1. **Existing work in upstream `Wei-Shaw/sub2api` (at `v0.2.23` and post-`v0.2.23` / open or merged PRs & issues)**
   - Inspect `Wei-Shaw/sub2api` at tag `v0.2.23` AND check public GitHub PRs/issues/commits (including PR #1309, #935, #2380, and any newer commits/PRs up to latest `main`/releases):
     - What exact status does PR #1309 (and any related Gemini native signature rectifier PRs/issues) have? Merged, closed, reverted, or superseded?
     - What already exists in `v0.2.23` across ALL Gemini forwarding paths:
       - `GeminiMessagesCompatService.Forward` (Claude compat)
       - `GeminiMessagesCompatService.ForwardNative` (API Key, OAuth AI Studio, OAuth Code Assist, Vertex ServiceAccount)
       - `AntigravityGatewayService.ForwardGemini` (and any shared `CleanGeminiNativeThoughtSignatures` / `Rectifier` helpers in `v0.2.23`)
       - `SettingService` / admin settings for signature rectification (`signature_rectifier_enabled` or similar, including default values and existing UI/API exposure in `v0.2.23`).
     - Does upstream `v0.2.23` already have `CleanGeminiNativeThoughtSignatures` or `FilterThinkingBlocksForRetry` or a rectifier package we should inspect and reuse?

2. **Existing work in this local repository (`Sub2API-Plugins`) and its submodules**
   - Inspect `.trellis/tasks/` (including archive if any), `git log`, branches, `plugins/` (`codex-candy-eval`, `sub2api-quota-extension`, `sub2api-plugin-template`), and `scripts/build.py`.
   - Confirm whether any existing plugin, patch, branch, or archived task already touches `gemini_messages_compat_service.go`, `antigravity_gateway_service.go`, or thought-signature handling.
   - Note any patch-conflict risks with existing plugins when targeting Sub2API `v0.2.23`.

3. **Ecosystem & Protocol Reference (Google Gemini API / Vertex AI / Relay Implementations)**
   - Verify exact error patterns and edge cases for Gemini native thought signature 400s across AI Studio, Vertex AI, and Code Assist:
     - Error message patterns (`Invalid thought signature`, `Corrupted thought signature`, `thought_signature`, `thoughtSignature`, missing signature on `functionCall`).
     - JSON field naming variants (`thoughtSignature` vs `thought_signature`, `functionCall` vs `function_call`, `thought: true` parts).
     - Exact cleaning semantics required so retries do not trigger secondary 400 errors:
       - Removing `thoughtSignature` / `thought_signature` from non-`functionCall` parts.
       - Handling `thought: true` parts (when `text` is empty vs non-empty; avoiding empty `Part{}` or empty `contents[].parts` causing `required oneof field 'data' must have one initialized field`).
       - Handling `functionCall` parts (whether replacing invalid signature with `skip_thought_signature_validator` works on both AI Studio and Vertex AI vs stripping).
       - Handling `countTokens` vs `generateContent` / `streamGenerateContent`.
       - Interaction with `checkErrorPolicyInLoop`, `finalErrorPolicy`, `shouldRetryGeminiUpstreamError`, ops error logging (`OpsUpstreamErrorEvent`), and single-retry loop guard.
   - Briefly check whether other relays (e.g. `CLIProxyAPI`, `new-api`, `LiteLLM`) document known pitfalls for Vertex/AI Studio native signature rectification.

4. **Summary & Open Decisions for Planning**
   - Clear verdict: Does related work already exist locally or upstream (exact version/PR/commit)?
   - Smallest viable touchpoint list on Sub2API `v0.2.23` (exact files and functions).
   - Concise list of open decisions for the user before writing `prd.md` / `design.md` (e.g., new plugin submodule vs patch in an existing plugin, reuse existing `signature_rectifier_enabled` setting vs new toggle, scope of `ForwardNative` vs `Antigravity` vs `Code Assist`).

## Report Format

- Keep `.trellis/tasks/11-20-gemini-thought-signature-rectifier/research/existing-work.md` concise, factual, and evidence-backed.
- Cite exact file paths, line numbers, PR/issue numbers, and URLs for every material claim.
- Separate confirmed facts from inferences and mark any uncertainty explicitly.
