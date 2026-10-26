# API Key Quota Extension Implementation

## Start Gate

- [x] Obtain approval of the complete planning summary.
- [x] Curate real spec and research entries in both context manifests.
- [x] Run `task.py start` only after that approval.

## GitHub Credential Authorization

The assistant used the existing `gh` login for authenticated repository queries and public repository creation without separate credential-use approval.
The user identified this authorization failure after implementation. The repository already exists. No code commit or push has occurred.
The earlier plan did not identify the credential source or repository visibility.
Before any further authenticated GitHub operation, obtain explicit approval for its credential source, target, and operation.
Use the [project credential rule](../../spec/guides/index.md#github-credential-use).

## Ordered Work

1. Prepare the local plugin repository and its submodule entry under `plugins/`.
   Remote creation requires the separate GitHub credential authorization above.
   Use the native submodule entry. Add no plugin registry, series file, or product documentation.
   Add the plugin's original root license.
2. Prepare the pinned v0.2.18 source with all discovered plugin patches.
   Inspect current changes and preserve the evaluation plugin.
3. Add the quota parser/client and the native field mapping.
   Reuse account transport and URL policy. Keep existing constructor callers usable.
   Update production provider injection and its generated Wire caller.
4. Extend existing single and batch usage flows.
   Preserve native provider results and errors. Fill mapped quota fields only on a valid response.
   Keep quota failures silent and remove their human-readable error descriptions.
   Keep local quota accounting and account scheduling unchanged.
5. Extend the existing account usage display.
   Add the `apikey` plus `base_url` condition for standard-cell platforms to both usage-fetch predicates.
   Preserve native multi-protocol eligibility and the no-data placeholder for empty responses.
   In the standard API-key branch only, render the mapped fields with `UsageProgressBar` and the native balance text.
   Remove the added quota error line. Preserve native provider error rendering.
   Give remote bars and the balance text the `upstreamQuota` title, and add that key to the `zh` and `en` locales.
   Retain native local displays and current loading, refresh, cache, and batch behavior.
6. Add focused tests for the changed behavior in the plugin's flat `tests/`.
   Extend common discovery for native Vue suites and their temporary placement.
   Extend existing common-runner tests for execution, cleanup, and failure propagation.
7. Save contextual production patches in lexical order.
   Exclude test source, test fixtures, and generated build outputs from production patches.
   Review the diff for preserved native behavior, local quota ownership, and untouched channel monitor files.
8. Run the default combined build.
   Fix material failures within this task before the quality handoff.
9. Update the applicable Trellis specs from verified behavior.
   Present the actual file list and commit plan through the established commit workflow.

## Focused Validation

Use the current quality and binary-delivery specs. Add cases only for changed behavior:

| Owner | Focused cases |
| --- | --- |
| Backend mapping | Wallet, key total quota, rate-only windows, and subscription fields. Include zero, omitted values, and ignored `remaining: -1` in these fixtures. |
| Backend query integration | Use single and batch entry points with local HTTP fixtures. Check the usage path, Bearer key, no declaration dependency, and per-account failure isolation. Check that failed quota queries add no error descriptions and preserve native errors. |
| Native Vue | Render mapped bars, balance, and the upstream title. Check that failed quota queries retain local information without error text. Exercise the added API-key query eligibility and existing manual-refresh path. |
| Common runner | Extend its existing cases only for new Vue-suite discovery, execution, cleanup, and failure propagation. |

Test each response mapping in the backend. Vue tests use mapped fields and do not repeat the upstream response matrix.
Use existing Vue mount tools, native stubs, and local HTTP fixtures. Keep assertions in real test files.
Review local quota ownership and unchanged channel monitor files through the diff, without separate source-string or no-write suites.
Reuse existing cache, mobile lazy-load, transport-helper, installer, and build-composition evidence for unchanged behavior.

The integrated entry is:

```sh
python3 scripts/build.py
```

The build already applies all plugin patches and runs discovered suites, frontend type/build checks, current Go vet checks, and installer tests.
Use one successful build for the final candidate. Do not add separate patch-composition, installer, or unchanged-suite acceptance runs.
Use focused native commands during development when they resolve changed behavior or an actual failure.
Do not require a retained container or a separate manual-browser acceptance step.
Race, coverage, full-suite, architecture, and fixed test-count gates do not apply.

## Sensitive Integration Points

- `AccountUsageService`: preserve public methods, native branches, batch isolation, and constructor callers.
- `ProvideAccountUsageService` and `cmd/server/wire_gen.go`: keep runtime injection consistent.
- Account URL validation: preserve existing callers and configured URL policy.
- Channel monitor files: the patch set must not touch them.
- `AccountUsageInfo` TypeScript type: all three added fields stay optional.
- `tests/support.py`: preserve Python, Go, and CJS discovery and cleanup.
- Evaluation plugin patches: both plugins must compose without context conflicts.

## Recovery and Handoff

Do not publish partial build outputs.
Use the current installer backup and restoration path for installed artifacts.
Quota tests use synthetic provider credentials and no paid inference requests.
New database migrations and installer redesign remain outside scope.
Keep product commits separate from task and journal bookkeeping.
Commit and push remain subject to their existing authorization rules.
