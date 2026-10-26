# Remaining Integration Contracts

## Source

Sub2API v0.2.18, commit `ac1b8f1271be0d674fa6f074403c1410f30a3a81`.
Local checkout: `/tmp/sub2api-native-tests.2lIzJP/vet-source`.
This source inspection used no live keys or inference requests.

## Transport Injection

`account_usage_service.go:309` defines the existing constructor.
`service/wire.go:224-255` constructs the service and then assigns its websocket invalidator.
`cmd/server/wire_gen.go:205` contains the generated caller.
The constructor has existing test callers that do not need remote transport.

Supply the shared `HTTPUpstream` and config through the production provider, without new mandatory constructor arguments.
Keep existing constructor callers usable under their original contract.
Use the existing TLS profile service.
Extract the URL-policy implementation from `account_test_service.go:283-299` into a shared package helper.
Keep the original method as its current caller entry point.
The billing probe must retain its behavior.

## Channel Monitor Scope

The user removed channel monitor changes from this task.
Channel quota detection keeps its native fetcher, validation, snapshot, and `MonitorQuotaView.vue` display.
The patch set must not touch channel monitor source files.

## Provider Dispatch Preservation

`account_usage_service.go:348-508` contains the native dispatch.
Gemini and Grok branches precede the generic unsupported-account error.
Custom API-key accounts can therefore already have local or passive provider information.
Preserve that result while attaching remote quota or a remote-specific error.
Do not replace valid native fields with an upstream error.

Use custom-target eligibility in backend dispatch.
The frontend adds the custom API-key fetch condition only for standard-cell platforms and renders mapped fields in that branch.
Existing multi-protocol eligibility remains authoritative. Empty responses retain the native no-data placeholder.
Reuse existing target selection and official-domain logic from the billing probe without checking its enabled state or result.
Known official targets and accounts without a custom target keep native behavior.
Adaptive protocol accounts use the existing chat-completions target selection rule.

## Flat Native Vue Tests

The common runner currently discovers Python, Go, and CJS entries in flat `tests/`.
The native frontend already has Vitest, jsdom, Vue Test Utils, and alias support.
Its config includes `src/**/*.{test,spec}.{js,ts,jsx,tsx}`.

Extend discovery for flat `test_*.test.ts` suites.
Temporarily stage these suites and their flat support files under a plugin-specific directory in the downloaded frontend's `src/`.
Run those explicit suite paths with the existing native Vitest config and installed dependencies.
Remove staged files after execution, including failure.
Test assertions remain in the real suites, not in a launcher or encoded source payload.
This needs no new test framework, dependency manifest, or Vitest config.
