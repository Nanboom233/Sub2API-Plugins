# Sub2API v0.2.21 Implementation

Date: 2026-11-13.

## Changes

| File | Result |
| --- | --- |
| `plugins/codex-candy-eval/.github/workflows/build.yml` | Manual builds default to `v0.2.21`. |
| `plugins/sub2api-quota-extension/.github/workflows/build.yml` | Manual builds default to `v0.2.21`. |
| `plugins/codex-candy-eval/tests/native_inspection_fixture.py` | Preferred Linux amd64 and arm64 paths use `v0.2.21` for standalone and combined outputs. |

Both plugins retain the existing upstream tag resolver and compatible patch sets.
The implementation adds no package requirement or compatibility adapter.
The combined source at `/tmp/sub2api-v0.2.21-clean` still matches the production patch candidate.

## Checks

- Ruby YAML parsing and both manual build defaults passed.
- Python syntax compilation passed without cache files.
- Fixture binary resolution passed for both architectures and both output owners.
- `git diff --check` passed for the three changed files.
- `gofmt -l` reported no changes for the existing modified plugin Go tests.

Python PyYAML was absent. The workflow check used Ruby's standard YAML parser without adding a dependency.
Existing conflict, dependency, standalone compilation, and combined source evidence remains applicable.

## Handoff

Run the full-scope Trellis check against both plugins and the original task requirements.
Use `UPSTREAM_TAG=v0.2.21 python3 -B scripts/build.py` for combined behavior tests and five-platform outputs.
The main session owns active specification updates and commit coordination.
