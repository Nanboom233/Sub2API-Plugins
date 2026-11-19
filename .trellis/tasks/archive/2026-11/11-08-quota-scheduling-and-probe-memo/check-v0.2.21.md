# Sub2API v0.2.21 Quality Check

This report describes the earlier adaptation candidate.
The later complete review found behavior defects. Final acceptance is recorded in [the correction check](./check-review-corrections.md).

Date: 2026-11-13.
Result: Pass.
Scope: Both plugins and all original task requirements.

## Review

The review found no defect that requires another code change.
It covered the applied production source and the changed regression tests.

| Contract | Review and evidence |
| --- | --- |
| Quota scheduling | Dated exhaustion selects the latest future reset. Undated exhaustion sets the native quota flag. Recovery clears quota state. |
| Atomic writes | Usage, script, expiry, and unsupported memo writes use SQL identity CAS. The guard includes full credentials, proxy identity, and normalized script. |
| Single and bulk edits | Managed keys are removed without JSON null values. Quota pauses clear conditionally. Other pauses remain. Scheduler snapshots update immediately. |
| Probe memo | Automatic usage and scheduled billing probes share the unsupported identity. Manual probes bypass the memo. Official billing targets retain short-circuit behavior. |
| Inspection page | A completed round reloads account inventory and priority badges. Idle inspection polls do not reload accounts. |
| Upstream integration | Native provider dispatch forwards `forceProbe`. Upstream Antigravity controls, usage types, and row-preserving refresh remain present. |
| Plugin independence | Existing research confirms standalone patch application and compilation for each plugin. Shared route and account additions remain separate. |
| Dependencies | Existing readonly module, tokenizer, frozen-lockfile, and type-check evidence remains valid. The upgrade needs no package change. |

## Combined Build

The existing build ran once:

```sh
UPSTREAM_TAG=v0.2.21 python3 -B scripts/build.py
```

The process exited with status `0`.
A macOS process-exit monitor captured the status of PID `19039` after the original checker lost its session.
The recovery checker did not start another build.
The complete log is `/tmp/sub2api-plugins-v0.2.21-check.log`.

| Check | Result |
| --- | --- |
| Frozen frontend install, i18n, Vue type check, and Vite build | Pass |
| Evaluation handler, runtime, service, and embedded page suites | Pass |
| Quota SQL CAS, outbox, conditional pause, and bulk cleanup suite | Pass |
| Quota Vue suites | Pass, two files and nine tests |
| Quota draft handler and quota service suites | Pass |
| Server, route, and web `go vet` | Pass |
| Common builder tests | Pass, four tests |
| Common installer suite | Pass |
| Five server and five installer builds | Pass |

## Published Local Outputs

`dist/build/` contains ten executable files.
Each directory contains the v0.2.21 server and installer:

- `linux-amd64`
- `linux-arm64`
- `darwin-amd64`
- `darwin-arm64`
- `windows-amd64`

The `file` command confirmed each executable's platform and architecture.
The Darwin arm64 server's `-version` command exited with status `0` and reported `Sub2API 0.2.21`.
Cross-compilation verifies build compatibility. Other platform programs and installations were not executed on hardware.

## Formatting and Warnings

The parent repository, evaluation plugin, and applied production source passed `git diff --check`.
The quota patch text reports whitespace in newly added unified-diff context lines.
Those lines require the context prefix. The applied source has no corresponding whitespace errors.

The build reported existing vendor whitespace, old Browserslist data, a Node shell deprecation, and large Vite chunks.
These warnings did not fail the build.
No new test matrix, dependency upgrade, or unrelated warning cleanup was added.

## Handoff

The main session can record v0.2.21 as the verified baseline and complete task acceptance.
The main session owns work-commit review and approval.
