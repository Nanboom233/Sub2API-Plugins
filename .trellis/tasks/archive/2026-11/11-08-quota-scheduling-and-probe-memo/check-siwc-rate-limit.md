# SIWC Rate-Limit Follow-up Check

Result: Accepted after the retried independent Trellis review. The reviewer found no code defects.
The review covers the same staged candidate as the passing implementation and main-session checks.

## Root cause and fix

The embedded evaluation page used one `unavailable` flag for every evaluation type.
`rate_limit_reset_at` set that flag and blocked SIWC rows, selection, select-all, and batches.
The backend account resolver and native sender did not apply this block.

The fix passes the page prefix through the existing eligibility helpers.
Only the `siwc-` prefix ignores `rate_limit_reset_at` when it checks action eligibility.
The page still renders the rate-limit restriction. A disabled, paused, error, overloaded, or busy account remains blocked.
Candy, Fingerprint, and Pelican keep the previous rate-limit behavior.
No backend, scheduler, sender, account state, or retry rule changed.

## Evidence

- The new UI case failed before the fix because the SIWC row action was disabled.
- The complete Node UI suite passed after the fix.
- The main session reran the complete Node UI suite after source review. It exited with status `0`.
- The case covers row start, selected batch, select-all batch, and selection retention after refresh.
- The case preserves unrelated restrictions and other evaluation tabs.
- `TestSIWCClassifications` passed. A real upstream HTTP 429 still maps to `limited`.
- `node --check` and applied-source whitespace checks passed.
- Evaluation-only and evaluation-plus-quota patches applied to fresh v0.2.21 trees.
- Playwright confirmed the rate-limit label, enabled SIWC row action, `/start` submission, and batch targets.
- The same account remained blocked on the Candy page.

Implementation report: `/tmp/sub2api-siwc-rate-limit-implementation.md`.
Independent review: `/tmp/sub2api-siwc-rate-limit-final-check.md`.
Fresh sources: `/tmp/sub2api-siwc-rate-limit-independent` and `/tmp/sub2api-siwc-rate-limit-combined`.

## Limits

The initial independent checker attempts failed with provider HTTP 429. The user-requested retry completed the source review.
The reviewer's optional Node rerun lacked `jsdom` in its selected tree.
The reviewer reused the owner's passing UI suite, the main-session rerun, and the browser evidence for this unchanged candidate.
An extra patch check targeted an already-patched tree and rejected existing files. It does not replace the fresh-tree application evidence.
No provider request, deployment, mount, or live account mutation ran.
