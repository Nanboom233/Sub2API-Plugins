# Evaluation footer correction

## Final candidate

The footer retains the plugin HEAD's original CPA credit, original MIT link, and dynamic version.
It adds one `LGPL-3.0` link immediately after MIT, as the user requested.
That link points to `https://github.com/Wei-Shaw/sub2api/blob/main/LICENSE`.
The added link uses the existing separator, target, and relationship attributes.

This replaces the earlier unapproved footer changes.
Those changes pointed to the fork license and added separate Sub2API and GPLv3/LGPLv3 entries.
The final footer has no such entries.
The plugin's actual LGPL license and the other pending UI changes remain unchanged.

## Evidence

Source: `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch`.
The final `ui.html` hunk declares 184 lines and produces exactly 184 lines.
The complete final patch passed `git apply --check` and actual application in `/tmp/sub2api-footer-check.gnqfD`.
A literal comparison confirmed that removal of the single added LGPL span restores the exact plugin HEAD footer.
The plugin diff formatting check passed.

An isolated Playwright session loaded the resulting static HTML with its actual stylesheet and theme.
The final snapshot shows CPA, MIT, LGPL, and version `v0.3.14` in that order.
All three links point to their requested destinations.
Snapshot: `/tmp/sub2api-footer-check.gnqfD/.playwright-cli/page-2026-11-04T19-34-12-261Z.yml`.
Screenshot: `/tmp/sub2api-footer-check.gnqfD/footer-final.png`.
Visual inspection confirmed one centered footer row with the requested labels and separators.

The existing UI suite has no footer-specific assertion. No test changes or new tests were necessary.
No server or installer rebuild occurred for this static correction.
The retained binaries still contain the earlier footer until the next user build.

## Independent review

The reviewer confirmed that removing the single requested LGPL span produces the exact plugin HEAD footer.
The MIT and LGPL links appear in the requested order before the original dynamic version.
The final hunk declaration and actual content both contain 184 lines.
The reviewer read the final Playwright snapshot and inspected `footer-final.png`.
The screenshot shows one centered line with CPA, MIT, LGPL, and version, without additional footer entries.
The final source and static-render review passes. Existing binaries still require the next build to include this correction.

## Final label clarification

The user clarified the link label to exact `LGPL-3.0` after the checks above.
Only that display text changed. The link destination, original footer, and 184-line hunk remain unchanged.
The earlier snapshot and screenshot show the preceding `LGPL` label.
The final source diff and formatting check passed. Prior link, structure, and layout evidence remains applicable.
No new test, browser session, or rebuild was necessary for this literal text edit.
