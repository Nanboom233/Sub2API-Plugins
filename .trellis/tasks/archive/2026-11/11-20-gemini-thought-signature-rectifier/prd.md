# Gemini native thought signature rectifier

Recover native Gemini requests after an upstream thought-signature HTTP 400.
Deliver `plugins/gemini-signature-rectifier` for Sub2API `v0.2.23`.
Planning is complete. User approval to start Phase 2 with `task.py start` remains required.

## Requirements

- **R1:** Cover API Key/relay, OAuth AI Studio, OAuth Code Assist, and Vertex ServiceAccount builders in `ForwardNative`.
- **R2:** Recover only unmatched thought-signature HTTP 400 responses. Cached-content exceptions and configured error policy take priority.
- **R3:** Permit at most one recovery resend per invocation, independently of the ordinary retry budget.
- **R4:** Handle direct camelCase and snake_case signature/function-call fields. Preserve nested business JSON, numbers, other fields, and order.
- **R5:** Apply the deterministic cleanup in [design.md](design.md#private-matcher-and-cleaner). Do not resend unchanged results or results without contents.
- **R6:** Add `rectifier_settings.gemini_native_signature_enabled` across storage, admin GET/PUT, and Vue. Default false. Runtime read errors return false.
- **R7:** Require master and new sub-option. Thinking and API Key signature switches must not control native recovery.
- **R8:** Preserve cancellation, routing, error policy, response ownership, usage recording, and account failure handling.
- **R9:** Use verified native Ops event kinds for changed-body recovery and failed resend outcomes.
- **R10:** Deliver one production patch through the complete template kit, LGPLv3 license, flat tests, and standalone/combined builds.
- **R11:** Keep the locked en/zh copy and native layout. Verify the final UI in Chromium across both locales and themes.

## Counting: locked Option B

`countTokens` participates in one recovery resend. Success returns upstream `totalTokens`.
A second 400 remains a 400 error without a new estimate.
Existing estimation branches remain unchanged.

## Boundaries

Preserve Claude-compatible `Forward`, handler pre-cleaning, Antigravity `ForwardGemini`, and exported `CleanGeminiNativeThoughtSignatures`.
Keep normal forwarding signatures, constructors, `wire_gen.go`, and `GetRectifierSettings` unchanged.
Keep tests outside `patches/gemini-signature-rectifier.patch`. Add no dependencies, database migrations, or nested Trellis files.
Remote repository creation and publishing require separate authorization.

## Acceptance criteria

- **AC1 / R1–R3:** Each builder recovers a scripted signature 400, including zero ordinary retries and recovery on the last ordinary attempt.
- **AC2 / R2,R8:** Policy/cached-content precedence blocks recovery. The resend receives fresh policy evaluation and preserves native cancellation and response closure.
- **AC3 / R3–R5:** A second signature 400, disabled gate, invalid JSON, unchanged body, or no remaining contents causes no further signature resend.
- **AC4 / R4–R5:** Cleaner tests cover both field forms, function-call sentinels, marked empty carriers, preserved text/nested data, and semantic no-op results.
- **AC5 / R6–R7:** The default is false. The gate requires both switches, returns false on read error, and ignores unrelated switches.
- **AC6 / R6:** Admin GET/PUT round-trips true and false using the existing plain-bool request contract.
- **AC7 / R8–R9:** Unchanged cleanup emits no signature event. Successful resends emit no error event. Later transient retries use normal `retry` events.
- **AC8 / R8:** Counting recovery returns actual upstream tokens. A second 400 returns an error without estimation.
- **AC9 / R10:** Focused suites and standalone/combined `v0.2.23` builds pass. Production patches contain no tests.
- **AC10 / R6,R11:** Chromium shows the full native card at 1440×900, scale 2, in en/zh and light/dark with zero console/page errors or overflow.
- **AC11 / R6,R11:** Initial false, enable/save/reload, disable/save/reload, sibling preservation, and master-off hiding pass. Row geometry matches sibling controls.
