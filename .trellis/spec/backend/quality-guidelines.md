# Quality Guidelines

## Current Sub2API scope

Use [administrator evaluation](./runtime-installation.md), [native inspection](./native-inspection.md), and [binary delivery](./minimal-linux-delivery.md) for current contracts.
Delivery uses the selected upstream tag on Linux amd64/arm64, Darwin amd64/arm64, and Windows amd64.
Sub2API v0.2.19 remains the verified integration baseline.
Installer version mismatches produce warnings and require explicit confirmation. Matching executable versions need no version prompt.
The common build downloads upstream source and discovers initialized plugin submodules with production patches under `plugins/`.
Each plugin and the template retain a complete aligned build kit. Local builds and CI use the same argument-free entry.
Plugins own patches and business tests. All assertions and test support code live in flat `tests/`. `assets/` contains data only.
Use [Directory Structure](./directory-structure.md) for file ownership.

For native behavior changes, use the approved focused checks:

```sh
python3 scripts/build.py
```

Reuse completed baseline and unchanged integration evidence.
Add only checks needed for changed behavior.
Format changed Go files with `gofmt`.
Check affected scripts, resources, and references.
Directory and documentation changes do not require another product build.
Report actual failures, skipped checks, and execution limits.

Use plugin `tests/test_ui.cjs` directly for existing native page assertions.
Manual `tests/native_*` helpers belong to the evaluation plugin and stay outside automatic `test_*` discovery.
Use [the native installer tests](../../../tests/test_installer_test.go) for shared transactions and changed native/Apple control paths.
Run them in the temporary host-platform installer module. Keep cross-compilation flags separate from host tests.
The fake-Docker `writeState` helper must write, close, and rename a unique temporary file beside `state.json`.
Readers must see complete JSON even when a timeout kills the writer. Keep malformed-state failures visible in `readState`.
Native Go suites use flat `test_*_test.go` files and `// sub2api-package:` annotations for temporary package placement.
Execute each discovered Go case once with native `go test`. Preserve standalone Go program support and direct Python/CJS execution.
Native Vue cases use flat `tests/test_*.test.ts` suites and the downloaded frontend's existing Vitest runtime.
The common runner stages suites and support files temporarily, runs explicit suite paths, and cleans the files after success or failure.
Keep upstream response mapping in backend tests. Vue tests consume mapped fields without repeating that response matrix.
Do not hide test suites in assets, encoded payloads, or source strings behind wrapper entries.
Reuse the existing command and local HTTP harness for changed installer behavior.
Check locale precedence, plain streams, and changed cancellation behavior within the existing suite.
Inspect actual dynamic terminal selection, spinner-to-prompt transitions, and cancellation for terminal presentation changes.
Compile the five approved outputs in one default combined build. Cross-compilation does not prove runtime installation on every platform.
Automatic acceptance requires no retained Docker container or manual browser session.
Do not create another suite for retired interfaces.
Replace obsolete version allowlist assertions with advisory-warning assertions instead of retaining both sets.
Test shared parsing and confirmation once. Do not multiply version cases by probe positions and confirmation inputs.
The default build already executes test entries. Do not rerun unchanged entries as a separate acceptance gate.
One CI build job runs shared checks once and compiles selected programs and installers sequentially.
Restore dependency caches once after source download. Upload only final executable pairs after the complete build succeeds.
Use native Actions logs and status. Do not add custom summaries, duplicate log artifacts, or intermediate artifact transfers.
Use builder output assembly and native Action/job failures instead of duplicate workflow output checks or successful-upload status aggregation.

Preserve native administrator authentication, account transport, cancellation, history errors, and settings storage.
Keep tests synthetic. Do not expose credentials in fixtures, logs, or reports.
Use existing result and error owners.
Review handler, service, runtime, and page fields together when a contract changes.
Keep generated output outside the user package and work commits.

Compatibility profiles, legacy migrations, shims, and multi-version adapters are retired mechanisms.
Gateway private keys, directed billing, activation, maintenance, and universal builders are retired mechanisms.
Race, coverage, full-suite, runtime architecture matrices, and source-resource parity are not current acceptance requirements.

## Commit and Finish Work

Use a hybrid workflow. Trellis owns development phases and managed task artifacts. `/git-commit` owns the review and approval of ordinary work commits.

### Ownership Boundary

| Change | Owner |
| --- | --- |
| Product code, project specs, and reviewed runtime or AI integration changes | Trellis work phase with `/git-commit` review |
| Task planning artifacts, status, and archive moves | Trellis task workflow |
| Session journals and generated workspace indexes | Trellis session workflow |
| Initial installation of portable Trellis and AI integration files | Reviewed work commit |
| Local identity, session pointers, caches, credentials, and machine-only settings | Local files, not a blanket work commit |

Do not mix task or workspace bookkeeping into an unrelated work commit. Do not rewrite an earlier commit to change this boundary.

### Ordinary Work Commits

1. Record source-backed findings in the relevant spec before drafting the commit.
2. Inspect the working tree and staged files.
3. Separate work changes from Trellis bookkeeping and unrelated changes.
4. Stage only the verified work paths.
5. Review the complete staged diff.
6. Draft an English Conventional Commit with an imperative subject.
7. Keep the subject within 74 characters.
8. Wrap body lines at 72 characters to follow `AGENTS.md`.
9. Check the effective Git signing policy.
10. If the signing policy is unset, ask the user to choose signed or unsigned.
11. Show the exact file list, message, and signing behavior.
12. Obtain final approval immediately before each non-temporary work commit.

Useful checks:

```sh
git status --short
git diff --cached --name-status
git diff --cached
git config --get --bool commit.gpgSign
```

For the signing-policy check, exit status `1` means unset. A configured value takes precedence unless the user explicitly chooses otherwise.

Task-creation consent and an earlier commit request do not replace final work-commit approval.

### Trellis-Managed Artifacts

Follow `.trellis/workflow.md` for task planning, completion, archival, and session records. Use the supported Trellis commands for lifecycle operations.

Create work commits before archive and journal commits. Once the workflow authorizes finish-work, use its native artifact and auto-commit steps.

Do not add `/git-commit` confirmation before every generated bookkeeping commit. Do not replace native artifact handling with manual staging or custom commits.

Honor `session_auto_commit` and `session_commit_message` in `.trellis/config.yaml`. Do not disable auto-commit merely to force the ordinary commit workflow.

The archive command commits task changes. The session command commits workspace records. Both use scoped Git pathspecs and preserve unrelated staged work.

Inspect their results after each step. Verify signatures when Git signing is enabled. Stop on signing or lifecycle failure.

Do not change Git configuration or downgrade signing to bypass a failure. Do not push without approval.

### Return to Main

If work uses a task branch, merge its completed commits into local `main` before the final handoff.
Include the work, archive, and session commits. Switch to local `main` after the merge.

References:

- [Trellis workflow](../../workflow.md): work commits, archive, and session order.
- [Lifecycle configuration](../../config.yaml): artifact auto-commit settings.
- [Archive implementation](../../scripts/common/task_store.py): scoped task commits.
- [Session implementation](../../scripts/add_session.py): scoped workspace commits.
- [Repository commit rules](../../../AGENTS.md): imperative subjects and body wrapping.

The user clarified this ownership boundary during the bootstrap task. Native artifact handling is not an exception to Trellis. It is part of the hybrid workflow.
