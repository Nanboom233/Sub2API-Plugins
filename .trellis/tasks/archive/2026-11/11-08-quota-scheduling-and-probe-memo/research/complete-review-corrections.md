# Complete Review Corrections for Both Plugins

The user requested a complete read-only review after the v0.2.21 adaptation.
The user then approved the correction plan for all five findings.

## Confirmed findings

| Priority | Owner | Trigger and effect |
| --- | --- | --- |
| P1 | Evaluation inspection persistence | A changed model mapping causes a full account save after a service read. Concurrent credentials, status, priority, participation, and quota updates can disappear. |
| P1 | Evaluation stream adapters | Anthropic EOF without termination, Gemini EOF without finish reason, and Gemini `MAX_TOKENS` become completed answers. Partial answers can change inspection policy. |
| P2 | Evaluation provider routing | Antigravity API key Claude models use the Gemini `streamGenerateContent` endpoint instead of the native Anthropic route. |
| P2 | Quota scheduling mutation | Two requests share a healthy snapshot. A later healthy result omits exhaustion and pause clearing after the other request saves exhaustion. |
| P2 | Quota account edits | Ordinary saves preserve quota keys from their old service snapshot. The locked repository merge omits current quota keys and can restore or delete exhaustion. |

## Source owners

- Evaluation `patches/0005-inspection.patch`: `PersistCodexInspectionVerdict`.
- Evaluation `patches/0004-admin-channel.patch`: provider selection and Anthropic/Gemini stream adapters.
- Quota `patches/quota-extension.patch`: `buildAPIKeyQuotaSchedulingMutation`, administrator extra preservation, and native repository merge.
- Native repository `updateLockedAccount` performs full `SetCredentials` and `SetExtra` writes without an account-version condition.

The inspection write and quota edit findings share a repository write boundary.
The evaluation plugin must own a narrow atomic inspection operation without importing quota symbols.
The quota plugin must preserve its current managed state during ordinary saves.
Use one implementation owner for both patch sets to avoid conflicting repository edits.

## Evidence

The fresh isolated complete build exited with status 0 before correction.
All existing business, frontend, build-kit, and installer tests passed.
Five server binaries and five installer binaries were generated. The host server reported version `0.2.21`.

Temporary overlay tests confirmed incomplete stream completion and the wrong Antigravity request path.
A service mock confirmed inspection submitted old credentials, scheduling state, priority, and participation after a concurrent edit.
Quota correctness assertions failed for healthy balance recovery, dated-pause recovery, and current-state preservation during ordinary edits.
No live provider, production database, or installed service was used.

Original evidence remains under `/tmp/sub2api-v0.2.21-readonly-SeEPuj/`.
Detailed plugin reports are `/tmp/sub2api-v0.2.21-readonly-eval.md` and `/tmp/sub2api-v0.2.21-readonly-quota.md`.
Convert the uncovered behaviors into permanent tests under each plugin's flat `tests/` directory.

Independent review of the first correction candidate found a partial-response gap in the quota correction.
A healthy reported window cleared balance exhaustion when balance was absent.
A balance-only result also cleared the aggregate flag or pause while an exhausted window remained unreported.
The final correction must merge response-determined source state with current persisted sources before deriving combined scheduling state.
This refines the same quota write contract. It does not add another feature or change dependency scope.

## Approved acceptance boundary

Keep existing API callers, native provider behavior, cancellation, retry ownership, and identity CAS.
Keep non-quota pauses and intentional identity/script reset behavior.
Use response-determined quota target values instead of old-snapshot deltas.
Use native transactions, scheduler outbox, and immediate snapshot synchronization.
Do not add dependency upgrades, database migrations, or a plugin-to-plugin production dependency.
Verify each plugin independently, then run the corrected combined v0.2.21 build once.
