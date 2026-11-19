# Work Commit Plan

Status: Completed and GPG-verified (`quota` `f9ba14b`, `eval` `4301252`, `parent` `a338468`). See [acceptance evidence](./check-v0.2.23.md).
Ready for Trellis task archival and session journal recording. No push has run.

## 1. Quota Plugin (`plugins/sub2api-quota-extension`, branch `main`)

Staged files (5):

- `M` `.github/workflows/build.yml`
- `M` `patches/quota-extension.patch`
- `A` `tests/test_account_repo_quota_test.go`
- `M` `tests/test_quota_script_test.go`
- `M` `tests/test_upstream_quota_test.go`

Exact commit message:

```text
feat(quota): integrate quota scheduling on Sub2API v0.2.23

- Sync default /v1/usage and quota_script exhaustion and recovery into
  native scheduling, threshold evaluation, and Redis snapshots.
- Share unsupported probe memoization across automatic usage and
  scheduled billing probes while keeping manual refreshes active.
- Guard async quota, expiry, and memo writes with atomic identity CAS,
  and preserve concurrent state on partial results and ordinary saves.
- Clear managed quota keys and apikey_quota_ pauses on identity or
  script edits across single and bulk updates.
- Rebase quota-extension.patch onto Sub2API v0.2.23 and update the
  workflow default tag and Go toolchain to v0.2.23 and 1.27.4.
```

## 2. Evaluation Plugin (`plugins/codex-candy-eval`, branch `main`)

Staged files (11):

- `M` `.github/workflows/build.yml`
- `M` `patches/0004-admin-channel.patch`
- `M` `patches/0005-inspection.patch`
- `M` `patches/0006-evaluation-ui.patch`
- `M` `tests/native_inspection_fixture.py`
- `A` `tests/test_account_codex_inspection_test.go`
- `M` `tests/test_codexeval_inspection_test.go`
- `M` `tests/test_service_account_codex_eval_service_test.go`
- `M` `tests/test_service_codex_inspection_models_test.go`
- `M` `tests/test_service_codex_inspection_settings_test.go`
- `M` `tests/test_ui.cjs`

Exact commit message:

```text
fix(eval): preserve account state, SIWC probes, and model defaults

- Persist inspection verdicts and model removals via narrow conditional
  updates without overwriting concurrent account or quota fields.
- Reuse native Gemini builders, Anthropic stream finalization, and
  Antigravity API-key Gemini/Claude routing, and refresh accounts on
  inspection completion.
- Allow SIWC row, selection, and batch checks on locally rate-limited
  accounts while keeping rate-limit labels and other tabs unchanged.
- Add gpt-6.2-sol to default degraded_remove_models alongside
  gpt-6.1-terra, and target Sub2API v0.2.23 with Go 1.27.4.
```

## 3. Parent Repository (`.`, branch `main`)

Staged files (11 now + 2 submodule gitlinks staged after commits 1 and 2):

- `M` `.github/workflows/build.yml`
- `M` `README.md`
- `M` `.trellis/spec/backend/api-key-quota.md`
- `M` `.trellis/spec/backend/database-guidelines.md`
- `M` `.trellis/spec/backend/directory-structure.md`
- `M` `.trellis/spec/backend/error-handling.md`
- `M` `.trellis/spec/backend/index.md`
- `M` `.trellis/spec/backend/minimal-linux-delivery.md`
- `M` `.trellis/spec/backend/native-inspection.md`
- `M` `.trellis/spec/backend/quality-guidelines.md`
- `M` `.trellis/spec/backend/runtime-installation.md`
- `M` `plugins/sub2api-quota-extension` (gitlink to commit 1)
- `M` `plugins/codex-candy-eval` (gitlink to commit 2)

Exact commit message:

```text
chore: upgrade plugin delivery to Sub2API v0.2.23

- Update plugin submodule pointers for Sub2API v0.2.23 quota scheduling
  and evaluation fixes.
- Update root workflow default tag to v0.2.23, Go toolchain to 1.27.4,
  and README installation examples.
- Synchronize backend specifications with the v0.2.23 baseline, quota
  contracts, SIWC admission, and model-control defaults.
```

Excluded local paths: `.vscode/settings.json`, `dist/`, `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/`, and `plugins/sub2api-plugin-template`.
