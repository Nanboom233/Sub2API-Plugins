# Coordinator Plan Review & Convergence Notes

Active task: `.trellis/tasks/11-20-gemini-thought-signature-rectifier`
Coordinator terminal: `t53`

The draft planning set is strong and clean (especially avoiding `wire_gen.go` / constructor churn via `rateLimitService.settingService`). Resolve these three targeted defects before we present the plan to the user:

1. **Ops event semantics (`design.md` §ForwardNative response loop & §Ops events)**:
   - **Record `signature_error` only after cleanup succeeds (`changed == true`)**: Run `cleanGeminiNativeThoughtSignaturesForRetry(body)` before emitting `signature_error`. Do not emit a `signature_error` Ops event when cleanup returns `false` and no recovery resend occurs.
   - **Record `signature_retry` only on failed HTTP responses (`resp.StatusCode >= 400`)**: Cross-check `antigravity_gateway_gemini.go:230–341` in `v0.2.23` to confirm whether `appendOpsUpstreamError` records `signature_retry` only on error statuses. Do not emit an upstream *error* event (`signature_retry`) on a successful HTTP 200 retry response. Align `design.md` (and `prd.md` AC7 / `implement.md` test table if needed) with the verified upstream Ops convention.

2. **Explicit reset of per-attempt `isSignatureRetryAttempt` flag (`design.md` §ForwardNative response loop)**:
   - State explicitly that `isSignatureRetryAttempt` is consumed/cleared immediately after handling the signature resend's transport/HTTP outcome, so if the resend hits a retryable transient status (429/5xx) and falls into ordinary transient retries (reusing the already-cleaned body), later transient retries log normal `"retry"` events instead of `"signature_retry"`.

3. **Cut duplicate `vue-tsc --noEmit` command (`implement.md` §5)**:
   - Since `scripts/build.py` already runs `pnpm run build` (`pnpm run check:i18n && vue-tsc -b && vite build`) and `tsconfig.json` already sets `noEmit: true`, remove the redundant standalone `vue-tsc --noEmit` command in `implement.md` §5 and note in one sentence that `pnpm run build` already enforces type checking with `noEmit: true`.

## Boundaries

- Planning docs ONLY (`design.md`, `implement.md`, and `prd.md` / `count-tokens-and-settings.md` only if needed for exact alignment).
- Do NOT edit production code, patches, tests, or submodules, and do NOT run `task.py start`.
- Prevent any internal subagent from running `hc send`.
- Report back via: `hc send t53 "Plan converged: <concise 1-line summary of updates>"`
