# Simplification Acceptance

Result: Accepted after independent Trellis review and the final combined build.
This report supersedes the previous correction candidate's implementation choices and stream requirements.

## Accepted changes

- Removed four state structures, the action enum, two interfaces, and the separate quota-edit wrapper.
- Removed the observation return pointer and separate quota-pause cleanup path.
- Merged quota state into the native locked account read and Ent update. No second account read or cleanup update remains.
- Preserved native administrator-save conditions and the original five-argument billing call behavior.
- Used an optional prior expiration to distinguish an unchanged form value from an actual edit.
- Kept asynchronous quota identity checks, recorded partial sources, overlapping recovery, and non-quota pauses.
- Limited inspection writes to their mapping and metadata fields.
- Reused native Gemini request builders and Anthropic finalization. Removed additional stream-termination requirements.
- Removed the inferred legacy balance block and its administrator-reset prerequisite.

The affected production Go sources contain 234 fewer lines than the previous correction candidate.
Both plugins remain independently usable on upstream v0.2.21 commit `10ba8f9b4dc2e6023d4a9879ab77b21841babd10`.

## Verification

Focused quota and evaluation checks passed in separate source trees.
The actual native account-save transaction tests cover expiration intent, existing calls, current quota state, and outbox rollback.
The final single-read repository checks exited with status `0`.
Combined native service, repository, administrator, and evaluation package tests passed.
Standalone and combined ordinary patch application passed. Applied-source Go formatting and whitespace checks passed.

The final temporary combined build exited with status `0`.
Frontend checks, both plugin test sets, `go vet`, builder tests, and installer tests passed.
The build generated five server binaries and five installer binaries under `/tmp/sub2api-simplify-build`.
The Darwin arm64 server reported `Sub2API 0.2.21`.

## Scope and internal contract

The native billing-save method adds an optional prior-expiration argument. Its Go method type changes.
The current repository implementation and explicit mock match that signature. Existing direct five-argument calls remain usable.
This direct argument avoids a new wrapper, account field, or hidden context state.

Repository checks use SQL mocks. No live database, provider request, deployment, or target-hardware installation ran.
These operations are outside this acceptance scope.
No work commit, push, or deployment forms part of this rework.

Evidence:

- Implementation: `/tmp/sub2api-simplification-implementation.md`.
- Independent review and build: `/tmp/sub2api-simplification-final-check.md`.
- Build command and execution record: `/tmp/sub2api-simplify-combined-build-v1.log`.
- Single-read repository log: `/tmp/sub2api-simplify-single-read-repository-v1.log`.
- Final applied source: `/tmp/sub2api-simplify-combined`.
