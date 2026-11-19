# Final Check of Both Plugin Corrections

Result: The previous candidate passed independent Trellis review.
The user later rejected its unnecessary abstractions. Simplification is active, and this report does not accept the new candidate.
The final candidate fixes all five approved defects and the partial-response defect found during review.

## Accepted behavior

| Boundary | Result |
| --- | --- |
| Inspection persistence | Narrow conditional updates preserve concurrent credentials, account state, participation, and quota metadata. |
| Stream completion | Anthropic requires `message_stop`. Gemini requires `finishReason: STOP`. Incomplete output does not become a completed answer. |
| Antigravity API key routing | Gemini models use Gemini. Claude models use the native Anthropic sender. |
| Quota overlap recovery | Observations merge with current sources under an identity-qualified row lock before combined scheduling state is calculated. |
| Ordinary account saves | Locked merges retain current quota state and expiration unless the administrator changed the expiration value. |
| Partial quota responses | Unreported balance and window sources retain their current state. Dated pauses include retained windows. |
| Plugin independence | Each plugin applies and passes affected-package checks without the other plugin. |

The new internal source key is `apikey_quota_balance_exhausted`.
Managed cleanup, scheduler filtering, and administrator quota reset include that key.
Old exhausted accounts without source metadata retain ambiguous balance exhaustion.
Positive balance or `ResetQuotaUsedAndClearRateLimitCooldown` can clear it. Window expiration alone cannot.
Some old window-only exhausted accounts therefore require one administrator quota reset before automatic recovery resumes.

## Verification evidence

Focused regression cases first failed against the old behavior, then passed after correction.
The final quota standalone checks passed after the returned partial-response correction.
The evaluation standalone candidate did not change after its successful checks.

The final combined build completed frontend installation, i18n, Vue type checking, both plugin suites, `go vet`, builder tests, and installer tests.
It generated five server binaries and five installer binaries under `/tmp/sub2api-review-fixes-final/dist/build/`.
File inspection confirmed all target formats. The Darwin arm64 server reported `Sub2API 0.2.21`.
Direct file comparisons confirmed that the build snapshot contains the current plugin patches and tests.

The first fresh clone failed after a network connection reset.
The checker completed the prepared v0.2.21 workspace through the existing builder resume stage.
The final log contains the complete published output list after all build steps.
Server restart removed the process handle before its exact exit status could be read. No observed exit integer is claimed.

Evidence:

- Independent report: `/tmp/sub2api-review-fixes-final-check.md`.
- Implementation report and focused commands: `/tmp/sub2api-review-fixes-implementation.md`.
- Final complete build log: `/tmp/sub2api-review-fixes-final-build-resume.log`.
- Final quota standalone log: `/tmp/sub2api-review-fixes-partial-standalone.log`.
- Evaluation standalone log: `/tmp/sub2api-review-fixes-standalone-eval.log`.

## Limits and handoff

Repository checks use SQL mocks and source review. No live PostgreSQL concurrency test ran.
The account-edit tests cover the merge helper and service fixture, without a live public-wrapper transaction test.
No provider request or deployment ran. Cross-platform files were compiled and inspected, without target-hardware installation tests.
The host version command ran on the final Darwin arm64 binary.

Original delivery files remain unchanged. Final corrected outputs stay under `/tmp`.
The main session owns final work-commit approval. Task archive and session records follow the work commits.
