# Sub2API v0.2.25 Upstream and Patch Audit

Date: 2026-11-25

Stage: Trellis Phase 1 research only

Target: `Wei-Shaw/sub2api` tags `v0.2.24` and `v0.2.25`

## Scope and method

This audit used read-only Git and HTTP requests. GitHub credentials were not used.

The upstream source was fetched into `/tmp/sub2api-v0225-audit-y9V8vf`. Patch checks used clean temporary trees. No production, test, workflow, README, spec, or submodule file was edited.

The audit used these commands and checks:

- `git status --short --branch`, `git rev-parse HEAD`, and branch reads for the root and four submodules.
- Public Git fetch for tags `v0.2.24` and `v0.2.25`.
- `git log --oneline v0.2.24..v0.2.25`, `git diff --stat`, and focused metadata diffs.
- SHA-256 of the public `v0.2.25.tar.gz` archive.
- `git apply --binary --check` for each plugin and exact combined patch application order.
- Temporary compile, vet, Go test, i18n, and Vue type checks on patched trees.

## 1. Workspace baseline

The baseline was captured before this report was written.

| Repository | Branch or state | HEAD | Status |
|---|---|---|---|
| root | `main`, `main...origin/main` | `ba049b42e0e39bce63716c4080daef909c16e5d7` | `M plugins/gemini-signature-rectifier`, untracked `.vscode/settings.json`, and the existing active task directory |
| `plugins/codex-candy-eval` | `main`, `main...origin/main` | `609f9798b7b7e220c929a33e41036f665b516abf` | clean |
| `plugins/gemini-signature-rectifier` | `main`, `main...origin/main` | `406df210a84744021d810386a11a7ef29ac22b34` | clean inside the submodule |
| `plugins/sub2api-plugin-template` | `main`, `main...origin/main` | `d823e9c5ee5a86214e38b331597433f8539ef167` | clean |
| `plugins/sub2api-quota-extension` | `main`, `main...origin/main` | `79a5f71285f601a98358d9c11088af07df302ebf` | clean |

The root `M plugins/gemini-signature-rectifier` entry is a gitlink change. The root index records `ccb2a98a8af307e15824d63b47849256a93aa06b`. The checked-out submodule is `406df210a84744021d810386a11a7ef29ac22b34`, one commit ahead with `docs: remove misleading README.`. The submodule worktree has no file changes.

The root also has the pre-existing untracked file `.vscode/settings.json`. The active task directory was already untracked before this audit. These paths are preserved.

Host tools:

| Tool | Version |
|---|---|
| Go | `go1.27.4 darwin/arm64` |
| Node | `v24.21.0` |
| pnpm | `12.16.1` |
| Corepack | `0.36.0` |
| Python | `3.14.8` |

## 2. Upstream tag and release facts

The public tags resolve as follows:

| Tag | Commit |
|---|---|
| `v0.2.24` | `7515db6dc56c2a6120dfb7abed70ef089ebc1457` |
| `v0.2.25` | `8fab111f92447a3edbcdf67a517e45b6a3cc4d31` |

The checked-out `v0.2.25` commit is `348997267`. The tag points to that commit through the release tree. The unauthenticated release API reports `v0.2.25` as the latest release. Public tag listing shows no later version tag.

The archive command produced this SHA-256 value:

`824c09225b2a2474bd3a59137afb2e8791410cec3e20b47640d4e353cd9e60e2`

The existing Session 11 notes contain the workflow artifact prefix `a23981a16719`, not a comparable upstream tarball digest.

## 3. Upstream change summary

The range contains 15 commits and changes 91 files. The diff is 3,486 added lines and 319 removed lines.

The commits group into these areas:

1. Header override identity variables and audit support.
2. Upstream group name and description preview, persistence, and automatic sync.
3. OpenAI passthrough error rule support and structured error preservation.
4. Compact stream overload error conversion.
5. Input trimming and control-character validation for group text.
6. Gorilla WebSocket dependency security update.
7. `VERSION` file synchronization.

The exact commit list is:

```text
348997267 Merge pull request #9052 from Wei-Shaw/feat/header-override-identity-variables
c5147eab1 fix(accounts): identity report variable audit fix
0f1e3c1f6 feat(accounts): header override identity variables
00c51f07d Merge pull request #9045 from itzhan/fix/openai-passthrough-400-error-forwarding
4d4433df0 Merge pull request #9008 from Brisbanehuang/codex/key-billing-group-details
eabf37852 fix(openai): compact response.failed overload code conversion
34423bf1e fix(accounts): trim group text before control-character validation
797fde4e9 fix(deps): upgrade gorilla/websocket for GO-2026-6278
ba9df6f1c fix(deps): upgrade gorilla/websocket for GO-2026-6278
38903b6d1 fix(accounts): validate group text before persistence and support multiple include values
4339d5061 fix(openai): prevent passthrough error redaction overflow and tighten structured fields
2b7437832 fix(openai): preserve invalid_encrypted_content and apply passthrough rules
03aa05fd9 feat(accounts): automatic upstream group name and description sync
a95c9e263 feat(accounts): sync account name and notes from upstream group
328db26f4 chore: sync VERSION to 0.2.24
```

### Metadata and build behavior

| Area | v0.2.24 to v0.2.25 result | Planning effect |
|---|---|---|
| `backend/cmd/server/VERSION` | `0.2.23` to `0.2.24` | The `v0.2.25` tag contains a stale `0.2.24` embedded version. Do not infer the release version from this file alone. |
| `backend/go.mod` | Go directive remains `1.27.4`. `github.com/gorilla/websocket` changes from `v1.5.3` to `v1.5.4-0.20240701034025-d67f41855da4`. | Keep the current Go workflow pin. Preserve the upstream WebSocket version. |
| `backend/go.sum` | Adds two checksums for the WebSocket pseudo-version. | The quota patch can add its own module lines after the upstream dependency update. |
| `frontend/package.json` | No diff. `packageManager` and `engines` are absent. Scripts and dependency specifications are unchanged. | Keep the current pnpm 12 preparation step. |
| `frontend/pnpm-lock.yaml` | No diff. Lockfile version remains `9.0`. | No lockfile rebase is needed for this range. |
| Dockerfiles and deploy files | `Dockerfile`, `backend/Dockerfile`, `deploy/install.sh`, and `deploy/README.md` are unchanged. | No installer or image logic change is required from upstream. |
| Startup and version flag | `backend/cmd/server/main.go` is unchanged. `/health`, `/setup/status`, and `-version` behavior is unchanged. The binary still reads the embedded `VERSION` file unless a version linker flag overrides it. | Check the stale embedded version during Phase 2 release validation. |

## 4. Plugin patch checks

The build code discovers plugin directories in lexical order. The active patch order is:

1. `plugins/codex-candy-eval`, with patch files `0001` through `0007` in lexical order.
2. `plugins/gemini-signature-rectifier`.
3. `plugins/sub2api-quota-extension`.

| Check | Result |
|---|---|
| Codex standalone `git apply --binary --check` | Pass for all seven patch files. |
| Gemini standalone `git apply --binary --check` | Pass. |
| Quota standalone `git apply --binary --check` | Fail. |
| Combined Codex then Gemini | Pass. |
| Combined Codex then Gemini then quota | Fails in the quota patch. |

The quota patch has 25 rejected hunks in nine files:

- `backend/internal/repository/account_repo.go`: 8 rejects.
- `backend/internal/repository/account_repo_grok_managed_extra_test.go`: 1 reject.
- `backend/internal/repository/account_repo_opencode_go_usage_test.go`: 2 rejects.
- `backend/internal/repository/account_repo_upstream_billing_probe_update_test.go`: 4 rejects.
- `backend/internal/service/account_service.go`: 1 reject.
- `backend/internal/service/admin_account.go`: 4 rejects.
- `backend/internal/service/admin_account_upstream_billing_probe_test.go`: 1 reject.
- `backend/internal/service/upstream_billing_probe.go`: 3 rejects.
- `frontend/src/components/account/CreateAccountModal.vue`: 1 reject.

The quota patch also applies cleanly in many other files. A partial `--reject` application is not a usable build because the nine files above require a rebase.

## 5. Semantic and compile audit

### Header override contract drift

Upstream changed `Account.ApplyHeaderOverrides` from:

```go
ApplyHeaderOverrides(http.Header)
```

to:

```go
ApplyHeaderOverrides(context.Context, http.Header)
```

The upstream change also expands variables from the request context and removes unresolved variable headers.

The Codex patch adds three old-signature calls in `backend/internal/service/account_codex_eval_service.go`. The quota patch adds three old-signature calls in its new quota probe code. Clean patch application does not detect this contract drift.

The first temporary Go compile failed at all three Codex calls. A temporary audit-only update that passed `req.Context()` to those calls made the patched Codex and Gemini tree compile. Phase 2 must update all six patch-added calls. Do not add a compatibility shim.

### Account and billing contracts

Upstream changed `AccountBillingSettingsRepository` to accept `AccountBillingSettingsUpdate`. The struct now carries probe, rate sync, group sync, rate multiplier, name, and notes fields. The quota patch still uses the old three-pointer method signature. Rebase the patch onto the struct contract.

Upstream changed the account repository lock query. It now preserves group sync state and also selects `extra`, `expires_at`, `temp_unschedulable_until`, and `temp_unschedulable_reason`. The quota patch adds quota state and expiry handling at the same query and scan boundary. Merge the complete upstream column list and scan order before adding quota state.

Upstream changed `UpdateUpstreamBillingProbeSnapshot` to accept `BillingGroupInfo`. The quota patch changes the same probe persistence flow. Rebase the quota state write and group data write together.

Upstream added group sync handling in `admin_account.go`, `upstream_billing_probe.go`, account DTOs, and account UI. The quota patch must preserve this behavior when it clears or updates managed quota fields.

### Requested integration areas

- `wire.go` and `wire_gen.go` have no upstream diff. Quota provider additions can remain surgical.
- `AccountUsageService`, `AccountTestService`, `SettingService`, `GeminiMessagesCompatService`, and admin service constructors have no upstream wire signature drift.
- Upstream changed existing account test call sites to pass request context to header overrides. Codex and quota additions must match this form.
- Upstream did not change native Gemini forwarding, `RectifierSettings`, `SettingsView.vue`, or the Gemini settings locales. The Gemini rectifier patch has no upstream file intersection.
- Upstream changed `AccountsView.vue` and account editor components for group sync. `AccountUsageCell.vue`, `QuotaScriptEditor.vue`, `UpstreamQuotaUsage.vue`, `UsageProgressBar.vue`, and `accountUsageRefresh.ts` have no upstream diff in this range.
- Upstream did not change Codex routes, sidebar, CSP, or the model normalization helpers used by the Codex patch.

### Temporary checks

The following checks ran on a clean `v0.2.25` tree with the Codex and Gemini patches. The three Codex context arguments were applied only in the temporary tree.

| Check | Result |
|---|---|
| `go test -tags=unit -run '^$'` on Codex, service, repository, admin, server, and route packages | Pass after the three context arguments were added. |
| `go vet -tags=unit` on the same patched packages | Pass. |
| Codex evaluation plugin tests | Pass. |
| Codex service, admin, and repository plugin tests | Pass when selected by plugin test names. |
| Gemini rectifier service and admin plugin tests | Pass when selected by plugin test names. |
| `pnpm run check:i18n` | Pass on the Codex and Gemini patched tree. Three tests passed. |
| `pnpm exec vue-tsc --noEmit` | Pass on the Codex and Gemini patched tree. |
| `pnpm run check:i18n` on the partially applied quota tree | Pass. |
| `pnpm exec vue-tsc --noEmit` on the partially applied quota tree | Pass. |

A full unfiltered service package test run produced large existing service activity and was interrupted after about 226 seconds. The selected plugin tests and compile checks are the valid evidence for this Phase 1 audit. Do not treat the interrupted broad run as a pass.

## 6. Build-kit alignment and version references

The following copies are byte-for-byte aligned by direct `diff` checks across the root, template, Codex, quota, and Gemini repositories:

- `scripts/build.py`
- `scripts/installer/`
- `tests/test_build.py`
- `tests/test_installer_test.go`
- `.github/workflows/build.yml`

All five workflow copies currently hardcode:

- default `upstream_tag: v0.2.24`
- Go `1.27.4`
- Node `26.13.0`

All five build scripts pin `pnpm@12.16.1`. All five build test fixtures contain the synthetic module line `go 1.27.0`. The fixture value is test data, not a production toolchain pin.

The active root specs still name `v0.2.24` in these files. They require a later Phase 2 and Phase 3 decision:

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/gemini-signature-rectifier.md`
- `.trellis/spec/backend/index.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/backend/runtime-installation.md`

Historical task and journal files also contain `v0.2.24` references. Keep historical records unchanged unless a later task explicitly requires a correction.

## 7. Phase 1 decision and implementation checklist

Recommended scope: update all five aligned build-kit copies and adapt the three active plugin patch sets. This keeps the root, template, and plugin entry points consistent.

Recommended implementation order:

1. Rebase the six patch-added `ApplyHeaderOverrides` calls onto the context-aware API.
2. Rebase the quota patch around `AccountBillingSettingsUpdate`.
3. Merge the expanded account lock query and scan order.
4. Merge `BillingGroupInfo` probe persistence with quota state persistence.
5. Repair quota test fixtures for the expanded query columns and account fields.
6. Repair the `CreateAccountModal.vue` reset hunk against the v0.2.25 form state.
7. Run standalone checks for Codex, Gemini, and quota.
8. Run combined patches in the exact lexical order.
9. Run selected plugin Go tests, `go vet`, `check:i18n`, `vue-tsc`, and the existing build-kit checks.
10. Update active version references only after the Phase 2 result is accepted.

The implementation should use direct v0.2.25 code paths. Do not add version gates, compatibility shims, duplicate cache keys, or fallback interfaces.

## 8. User input and preserved state

No user input is needed to complete this Phase 1 research.

The evidence supports the all-five-repository scope. Phase 2 must preserve the existing root gitlink change, `.vscode/settings.json`, and the active task directory. Do not reset, checkout, stash, or overwrite those paths.

The upstream group sync and header identity features are real v0.2.25 behavior changes. The quota rebase must preserve both behaviors while keeping quota state changes surgical. This is an implementation dependency, not a reason to add a second compatibility mode.

## 9. Cleanup

The temporary audit path `/tmp/sub2api-v0225-audit-y9V8vf` and its path marker were removed from `/tmp`. No audit tree remains under `/tmp`.
