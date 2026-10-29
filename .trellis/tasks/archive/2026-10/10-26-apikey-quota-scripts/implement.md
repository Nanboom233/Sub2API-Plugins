# Custom Quota Script Implementation

## Start Gate

- [x] Record the user's interaction-only reference choice.
- [x] Record visible custom-script errors and silent default-query failures.
- [x] Complete runtime research and record the latest editor, draft-test, and balance-unit requirements.
- [x] Obtain explicit approval of the complete plan before `task.py start`.
- [x] Obtain approval of the native reset-time tooltip addendum and its focused validation plan.

## Ordered Work

Implementation, the v0.2.19 upgrade, and the complete task review are complete.
The review covered scripts, native reset tooltips, weekly calculation, expiry synchronization, cache refresh, and build composition.
Use existing upstream responses. No upstream plugin deployment is required.

1. Create the local task branch after approval and inspect parent and quota-submodule changes.
   Prepare pinned Sub2API source with both plugin patches through anonymous public access.
   Preserve unrelated work. Builds use current plugin checkouts without fetching or updating them.
2. Add the pinned Goja dependency, synchronous runner, account context, and HTTP callback.
   Keep the shared deadline active through result conversion. Add required original licenses under the plugin's `licenses/` tree.
3. Add script-string storage and dispatch. Map period results and balance units according to `design.md`.
   Show custom failures through `UsageInfo.error`. Keep default detection silent and restore it after script removal.
   Preserve unrelated account settings and existing save callers.
4. Add `POST /api/v1/admin/accounts/quota-script/test` and its frontend client.
   Apply the create/edit draft rules from `design.md`, including explicit proxy removal.
   Reuse account usage injection, proxy lookup, and native envelopes. Testing must not save or seed list caches.
5. Add the shared editor to both forms, including the separate Antigravity creation path.
   Follow the exact tooltip, highlighting, sizing, placeholder, button, and error styles in `design.md`.
   Test effective draft settings and ignore stale output.
6. Route configured API-key accounts through the standard cell and existing usage request paths.
   Reuse native badges, progress bars, and balance text with the optional unit.
   Complete the reset-date code changes below for default results, saved scripts, and inline previews.
   Preserve local information, default platform views, and empty placeholders.
   Use existing per-account cache invalidation and response guards after saved configuration changes.
7. Update focused tests in flat `tests/` and regenerate contextual production patches against combined source.
   Keep tests outside production patches and preserve evaluation-plugin patch composition.
8. Format changed Go files and run the default combined build for the final candidate.
   Complete the normal Trellis implementation/check review. Reuse passed evidence for unchanged inputs.
9. Update the quota spec and affected frontend guidance with the verified custom-script contract.
   Keep default detection behavior separate from custom errors, units, and platform eligibility.
10. Present the actual work-commit plan for final approval. Follow native Trellis archive and journal operations after work commits.

## Reset Date Code Changes

1. For the tooltip, edit `frontend/src/components/account/UsageProgressBar.vue` in the combined source.
   Extend the formatter import and add the native hover tooltip to its existing reset-time span as shown in `design.md`.
   Copy the tooltip classes and arrow from `AccountStatusIndicator.vue:94-136`. Reuse `dashboard.platformQuota.resetsAt`.
   Keep the original countdown span's font metrics, position, timer, and expired state. Keep `UpstreamQuotaUsage.vue` unchanged.
2. Extend the existing native display case in plugin `tests/test_usage_cell.test.ts`.
   Add one mapped reset timestamp and let the existing translation stub include its `time` interpolation.
   Assert the formatted reset message for that period and its absence for a period without a timestamp.
3. Regenerate `plugins/sub2api-quota-extension/patches/quota-extension.patch` with that component change.
   Keep tests outside the production patch. Preserve both plugins' existing patch composition.
4. Inspect the added tooltip once with Playwright, as the user requested.
   Reuse the existing desktop, narrow-layout, editor-help, and error-state evidence.
5. Run `python3 scripts/build.py` for the updated final candidate and complete the normal Trellis check.
   The default entry applies patches and runs the discovered tests. Do not run those same entries separately first.
   Record the new output evidence, then update the quota spec and work-commit plan.

The user authorizes local decoding and native account expiry synchronization.
Read the key-level and subscription `expires_at` fields. Save the earlier reported value as native account expiration.
Preserve saved expiration when both fields are absent. Remove the previous monthly-expiry reset mapping.
Keep weekly reset as the reported weekly start plus seven days, with its explanatory code comment.
Reuse the native account update and display paths. Preserve other account fields and expiration settings.
Extend native `AccountBulkUpdate` and repository SQL with `ExpiresAt` for narrow persistence and existing snapshot synchronization.
Keep expiry in the internal decoder result. The existing account column uses it on the next list refresh.
Extend existing mapping and usage-entrypoint cases for selection and persistence, then run the default build once.
Reuse the existing native renderer checks. Add no tests for unchanged countdowns, formatters, prop forwarding, timers, or locale rules.
Use [the code-level research](./research/reset-date-code-plan.md) for exact owners and source anchors.

## Focused Validation

| Owner | Changed behavior |
| --- | --- |
| Go runner | Use a real script and local HTTP fixture for account inputs and result mapping. Cover periods, balance forms/units, defaults, zero, omission, and invalid output once. Include execution errors and cancellation of JavaScript and host HTTP work. |
| Existing usage and handler cases | Extend single/batch integration for script selection, visible failure, no fallback, and removal restoration. Cover create/edit draft preview settings, proxy removal, native envelopes, and no persistence in handler cases. |
| Native Vue | Check shared editor input, test feedback, stale output, and form wiring. Extend existing usage-cell cases for mapped units, the native reset-time tooltip, custom errors, query eligibility, and changed-row refresh. |

Keep result and unit validation in the runner cases. Frontend and handler cases consume mapped results without repeating that matrix.
Test shared behavior once. Do not multiply script failures by platform, period, balance form, or single/batch entry point.
Check platform dispatch changes through the diff and representative existing cell cases, not a new platform matrix.
Test shared editor behavior once and use existing form cases for create/edit wiring.
Do not add assertions that only copy CSS classes or implementation structure.
Reuse existing default-query, authentication, transport, cache-helper, patch-composition, and installer tests where behavior is unchanged.
Extend an existing suite when it owns the change. Add a flat suite only for a new owner.
Use synthetic keys and local HTTP fixtures. Add no live provider, stress, race, coverage, full-suite, browser, or container acceptance gate.
The integrated entry remains:

```sh
python3 scripts/build.py
```

The build already runs discovered tests, frontend checks, Go vet, server compilation, and installer tests.
Do not run its discovered test entries again as a separate acceptance gate.
Repeat affected checks only after a change or failure invalidates their evidence.

## Execution Evidence

- Current combined source: `/tmp/sub2api-v0219-upgrade.TcfHlc/source`, official tag `v0.2.19`.
  The release commit is `dece26153621959ccd7635814f4b2d08304e681a`.
  The source version file still says `0.2.18`. The selected tag supplies canonical `0.2.19` for both executables.
- Both plugin patches apply with normal `git apply` on v0.2.19. The version upgrade keeps Goja pinned.
  The module patch omits old dependency upgrades already present in the new upstream source.
- The repaired complete-review candidate passed `python3 scripts/build.py` in terminal session `82928`, exit code zero.
  The build covered frontend checks, discovered plugin tests, Go vet, server compilation, and installer tests and compilation.
  Log: `/tmp/sub2api-full-review-refresh-build.log`.
  Outputs: `dist/build/sub2api-plugins` and `dist/build/sub2api-plugins-installer`, both version `0.2.19`.
  Both outputs are static Linux/amd64 ELF executables. Git used anonymous public access without the user's global configuration.
- Default subscriptions use reported weekly start plus seven days. A code comment explains the omitted legacy anchor correction.
  Daily and monthly reset times remain absent without source anchors. Key rate-window `reset_at` mapping remains intact.
  See [default quota paths](./research/default-quota-v0219.md) and [subscription anchors](./research/default-subscription-v0219.md).
- The decoder selects the earlier available key/subscription expiry. Native `BulkUpdate` saves only expiration and synchronizes scheduler snapshots.
  Existing cases cover selection, persistence, unchanged values, preserved settings, and silent write failure.
  Subscription expiry does not populate monthly reset. The account-expiry column updates on the next native account-list refresh.
- The rejected upstream producer change remains rolled back. The implementation requires no upstream deployment.
- Previous independent reviews passed for script execution, editor behavior, native tooltips, version metadata, and expiry synchronization.
  The complete review found one refresh defect: default-query accounts ignored save timestamps despite omitted credentials.
  The repair includes `updated_at` in every API-key refresh key and extends the existing cache-refresh case.
  Single and batch requests retain their existing cache and stale-result owners. No new test case or suite was added for this repair.
  Complete backend and frontend reviews found no other confirmed product defect.
  Main inspected the staged repair and final build log.
  Approved signed work commits: evaluation `a9038c9`, quota `dcb0138`, and parent `2212b3b`.
  No remote operation was performed.
- Playwright inspected the actual editor and native renderer with synthetic preview responses.
  Desktop checks covered placeholder code, highlighting, blank-input controls, help, mapped bars, balance units, and inline errors.
  A 375-pixel viewport showed an expanding multiline editor without editor or page overflow.
  These checks verify rendering and interaction. They do not verify a deployed upstream response.
- The native tooltip showed `2099/01/01 13:00 重置` for `2099-01-01T05:00:00Z` on hover and retained its inline countdown.
  Screenshots: `/tmp/sub2api-quota-scripts-preview/output/playwright/`.
  Tooltip screenshot: `/tmp/sub2api-quota-scripts-preview/output/playwright/reset-time-tooltip.png`.
  The temporary browser and Vite preview are closed.

## Sensitive Files

- `backend/go.mod` and `backend/go.sum`: interpreter version and readonly dependency resolution.
- `backend/internal/service/account_usage_service.go`: script precedence and existing callers.
- `backend/internal/service/admin_account.go`: save validation and unrelated extra preservation.
- `backend/internal/handler/admin/account_handler.go` and the new quota-script handler: draft account construction, script execution, and diagnostics.
- `backend/internal/server/routes/admin.go`: administrator middleware and route composition.
- `frontend/src/components/account/CreateAccountModal.vue` and `EditAccountModal.vue`: shared string configuration and current-draft testing.
- `frontend/src/components/account/AccountUsageCell.vue` and `frontend/src/views/admin/AccountsView.vue`: display, eligibility, and changed-row cache state.
- Existing quota and evaluation patches: contextual composition against the pinned source.

## Authorization and Recovery

This plan requires no GitHub credential use or remote operation.
Use only local work and anonymous public downloads until separately authorized.
Do not call authenticated GitHub APIs, push, or publish under feature-plan approval.
Ordinary commits retain final approval and the configured signing policy.
Do not publish partial build outputs. Preserve the installed executable recovery flow.
