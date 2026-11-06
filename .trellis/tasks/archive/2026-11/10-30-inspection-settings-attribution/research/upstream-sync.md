# Upstream synchronization scope

## Source and current evidence

Upstream is `https://github.com/haowang02/cpa-plugin-codex-candy-eval`, branch `main`.
The local native fork is `plugins/codex-candy-eval`, with origin `Nanboom233/codex-candy-eval`.
Do not confuse the original CPA plugin with `haowang02/codex-candy-eval`, the separately credited Candy project.

Baseline: `4f8367642cc1e629c4ee15a975e5e0fc53c4ac16`, upstream v0.4.2.
The archived `10-19-upstream-compare-adaptation/research/upstream-comparison.md` records this revision.
Local merge commit `c2a93f8` has this upstream revision as its second parent.
It is an ancestor of local main. Commit `b67452e` implemented the native Pelican adaptation.

Target: `179d6dae48a0f0a735637ea2f373345b91caaca8`, upstream v0.4.4, committed 2026-10-27.
An anonymous bare clone confirmed this revision as upstream main on 2026-10-30.
The research repository is `/tmp/codex-eval-upstream-plan.TxVTAt/upstream.git`.
No credentials, local repository refs, or product files changed during the comparison.

[Original comparison](https://github.com/haowang02/cpa-plugin-codex-candy-eval/compare/4f8367642cc1e629c4ee15a975e5e0fc53c4ac16...179d6dae48a0f0a735637ea2f373345b91caaca8).
The GitHub page lists commits but cannot render the full diff. Local Git supplied the complete diff.

The current native UI reports `pluginVersion = "0.3.14"` in `patches/0006-evaluation-ui.patch`.
That native version does not identify upstream synchronization completeness.
Keep native release numbering independent. Do not replace it with CPA's v0.4.4 release-only version change.
The combined program still targets Sub2API v0.2.19.

## Incoming commit decisions

| Commit | Change | Decision |
| --- | --- | --- |
| `19e29f9` | Pelican toolbar button follows normal narrow-screen grid placement. | Adopt through native CSS. |
| `a7435d9` | Decode CPAMP `enc::v2::` saved login as well as CPAMC v1. | Exclude. Native Sub2API authentication does not use CPA login storage. |
| `e84acaf` | CPA release v0.4.3. | Exclude release-only version change. |
| `989d97d` | Update LM detector data, sequence acceptance, and expected results. | Adopt through native detector, resource patch, and existing golden fixture. |
| `179d6da` | CPA release v0.4.4. | Pin as comparison target. Exclude release-only version change. |

## Complete file disposition

The comparison changes ten files. No other production behavior changes appear in this range.

| Upstream file | Native destination and action |
| --- | --- |
| `internal/plugin/data/lm-detector/README.md` | Update the existing embedded source note in patch `0002` to detector revision `a4ef212df06817e8071acd05f00219f4c9eb2f9a`. |
| `internal/plugin/data/lm-detector/models.json` | Replace the matching data in patch `0002`. Reference models increase from 60 to 64. |
| `internal/plugin/data/lm-detector/shared_detector.bin` | Replace the binary hunk in patch `0002` with the target's complete binary. Size changes from 4,385,348 to 4,667,588 bytes. |
| `internal/plugin/fingerprint_detector.go` | Update `sequenceShape` in patch `0001`. Change threshold conjunction to disjunction and update the existing explanation. |
| `internal/plugin/fingerprint_test.go` | The change only describes the new golden case. Reuse native `tests/test_codexeval_fingerprint_test.go`. |
| `internal/plugin/testdata/lm-detector-golden.json` | Replace `assets/lm-detector-golden.json`. The existing native test already consumes its cases. |
| `internal/plugin/web/style.css` | Update native `#pl-toolbar` rules in patch `0006`. Remove forced button column spanning at both existing 900px and 768px breakpoints. |
| `internal/plugin/web/app.js` | Exclude CPA saved-login decoding. Keep native authentication. |
| `scripts/test-ui.cjs` | Exclude tests for the excluded CPA login change. Keep native flat UI tests. |
| `internal/plugin/plugin.go` | Exclude CPA ABI and release-version ownership. Keep native page assembly and version ownership. |

## Detector behavior and evidence

The old rule accepts a sequence only when both medians satisfy their limits:
`autocorrelation <= -0.23 && small_step_share <= 0.05`.
The new rule accepts a sequence when either median satisfies its limit:
`autocorrelation <= -0.23 || small_step_share <= 0.05`.
Reject as `not_model` only when both limits fail.

The target adds `kimi-k3.1-pro`, `gemini-3.5-flash-lite`, `minimax-m3.1-flash`, and `gpt-6.1-terra` references.
The enrollment suite and MIT license do not change.
The golden fixture grows from four cases to six and updates expected rankings for the new reference bank.
One new case identifies `gpt-6.1-terra`.
The other identifies `kimi-k3.1-pro` despite a small-step share above 0.05, which verifies the changed acceptance rule.
The existing native golden test compares predictions, model likelihood, diagnostics, scores, and rankings.
Use that test with the updated fixture. Do not add another detector parity suite or a new numerical matrix.

Current native code still uses the old conjunction. Its fixture still has four cases.
Current native CSS forces the Pelican button across both columns at two breakpoints.
These updates are not already present.

## Integration boundaries

Port applicable evaluation behavior, prompts, data, resources, and UI changes.
Preserve native Sub2API authentication, account APIs, transport, history handling, inspection, model control, and current task requirements.
Exclude CPA-only runtime, installation, release workflows, and unrelated project tooling.
Preserve the exact README restoration. Do not copy upstream README or license changes over this task's explicit requirements.
Use existing flat tests and one combined build after the complete patch update.
Do not create an upstream-parity test matrix or another entry besides each repository's complete `scripts/build.py`.
Update `.trellis/spec/backend/runtime-installation.md:104` from the old conjunction to the new sequence rule.
Inspect the actual Pelican toolbar at narrow width during the task's existing Playwright session.
