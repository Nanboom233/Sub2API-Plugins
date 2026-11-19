# Sub2API v0.2.23 Acceptance Check

Date: 2026-11-18.
Build result: Pass, exit `0`.
Independent review: Pass.
Scope: Both production plugins, parent delivery files, active backend specs, and all task acceptance criteria.

## Accepted implementation

The integration target is upstream `v0.2.23`, commit `5af9afb588c4b014b3df9db7d4073af1f8ae01b6`, with Go `1.27.4`.

| Contract | Implementation and evidence |
| --- | --- |
| Quota patch context | Re-exported against clean v0.2.23. Retains direct jsonschema and the upstream `formatDateTime` import. |
| Active usage cache | `loadActiveUsage` captures `apiKeyUsageRefreshKey.value` before the request. Its cache write includes `config`. |
| Native usage display | Preserves upstream OpenAI stale-quota feedback and Gemini usage visibility during refetch. |
| Duplicated accounts | Discards all 13 `APIKeyQuotaManagedExtraKeys`, including `APIKeyQuotaBalanceExhaustedExtraKey`. The existing regression checks every key. |
| Model-control defaults | Appends `gpt-6.2-sol` after the existing five entries. Backend settings and embedded UI assertions pass. |
| Stored model settings | Retains ordered normalization, duplicate removal, and explicit empty-list behavior. |
| Quota persistence | Existing identity CAS, partial-source recovery, account-save preservation, scheduling, and memoization regressions pass. |
| Evaluation persistence | Existing narrow writes, concurrent-change rejection, native sender, and protocol-routing regressions pass. |
| SIWC admission | Existing UI regression retains SIWC admission during local rate limits and preserves other action restrictions. |
| Delivery references | Parent and production-plugin workflows use v0.2.23 and Go 1.27.4. README and active specs match. |

The default removal list is:

```text
["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra", "gpt-6.2-sol"]
```

The server remains the only default owner.
The page receives this list from saved settings.
The update changes no dependency version, schema, wrapper type, or public route.

## Standalone patch checks

Fresh temporary trees started at clean upstream v0.2.23.
The evaluation tree applied patches `0001` through `0007` in filename order.
The quota tree applied `quota-extension.patch` alone.

```sh
# Evaluation-only fresh tree
cd /tmp/sub2api-v0.2.23-verify-eval
for patch in /Users/minami/Code/S/Sub2API-Plugins/plugins/codex-candy-eval/patches/*.patch
do
  git apply --binary "$patch"
done
git diff --check

# Quota-only fresh tree after the final context adjustment
cd /tmp/sub2api-v0.2.23-verify-quota-final
git apply --binary /Users/minami/Code/S/Sub2API-Plugins/plugins/sub2api-quota-extension/patches/quota-extension.patch
git diff --check
```

Both application commands and both applied-source whitespace checks exited `0`.
The evaluation vendor patch retained its three existing whitespace warnings.
The warnings rejected no hunk.

The final quota patch uses shorter Git-generated context for three hunks.
Fresh application and applied-source whitespace checks passed after that representation change.
Direct `cmp` checks confirmed unchanged `go.mod`, `AccountUsageCell.vue`, and `admin_account.go` source.
The full build evidence therefore applies to the final production source.

## Authoritative combined build

The root ran this command once:

```sh
UPSTREAM_TAG=v0.2.23 python3 -B scripts/build.py
```

The build used `GOTOOLCHAIN=auto`, normal Go caches, and the normal pnpm store.
Git credential helpers and terminal authentication prompts were disabled for the public upstream clone.
The build used no GitHub credentials.

The build started at 18:10 and ended at 18:22, Asia/Shanghai.
The process ran in Herdr terminal `t3w` and exited `0`.
Its temporary workspace was `sub2api-plugins-dpfq09b0` under the host temporary directory.
The build removed that workspace after completion.

| Gate | Result |
| --- | --- |
| Combined ordinary patch application | Pass. No rejected hunk. |
| Frozen frontend installation | Pass, pnpm `12.16.1`. |
| Native i18n checks | Pass, three tests. |
| Native Vue/TypeScript compilation | Pass through `pnpm build`, which invokes `vue-tsc -b`. |
| Vite production bundle | Pass. |
| Evaluation repository, handler, runtime, and service suites | Pass. Includes six-model defaults and native persistence contracts. |
| Evaluation embedded UI suite | Pass. Includes six-model defaults and SIWC eligibility. |
| Quota repository, handler, and service suites | Pass. Includes all 13 duplication keys and quota recovery contracts. |
| Quota Vue suites | Pass, two files and nine tests. |
| Native server, route, and web `go vet` | Pass. |
| Shared builder suite | Pass, four tests. |
| Shared installer suite | Pass, including replacement, recovery, native, Apple, and terminal cases. |
| Five server targets | Pass. |
| Five installer targets | Pass. |

The build retained existing vendor whitespace, Node, Browserslist, and bundle-size warnings.
Those warnings did not fail compilation or tests.
Phase 1.2 also passed `vue-tsc --noEmit` against this frontend source.
The later implementation changes only backend code, model-default test fixtures, workflow versions, and the fallback binary names.
The fresh native `vue-tsc -b` result confirms the final frontend compile.

## Published local outputs

The build published ten executable files under `dist/build/`.
Each file has the final build timestamp, 2026-11-18 18:22, Asia/Shanghai.

| Directory | Server | Installer |
| --- | --- | --- |
| `linux-amd64` | `sub2api-plugins-v0.2.23-linux-amd64` | `sub2api-plugins-installer-v0.2.23-linux-amd64` |
| `linux-arm64` | `sub2api-plugins-v0.2.23-linux-arm64` | `sub2api-plugins-installer-v0.2.23-linux-arm64` |
| `darwin-amd64` | `sub2api-plugins-v0.2.23-darwin-amd64` | `sub2api-plugins-installer-v0.2.23-darwin-amd64` |
| `darwin-arm64` | `sub2api-plugins-v0.2.23-darwin-arm64` | `sub2api-plugins-installer-v0.2.23-darwin-arm64` |
| `windows-amd64` | `sub2api-plugins-v0.2.23-windows-amd64.exe` | `sub2api-plugins-installer-v0.2.23-windows-amd64.exe` |

The local version check was:

```sh
./dist/build/darwin-arm64/sub2api-plugins-v0.2.23-darwin-arm64 -version
```

It exited `0` and printed:

```text
Sub2API 0.2.23 (commit: unknown, built: unknown)
```

The current linker command sets the canonical version and release build type.
It does not supply commit or build-time metadata.

## Independent review

The independent `trellis-check` agent reviewed the full task scope against `prd.md`, `design.md`, `implement.md`, and `check.jsonl`.
It checked production patches, regression tests, workflows, README, active specs, and the successful build evidence.
It found no behavior or specification defect requiring a change.
It reused the valid build results and made no code or test changes.

Applied-source whitespace checks pass.
Whole-task Git whitespace checks also inspect context prefixes inside nested patch files.
Those patch-text diagnostics do not indicate whitespace changes in the applied production source.

## Commit boundary

No work commit, push, release, or deployment has run.
The work file lists remain in [the commit plan](./commit-plan.md).
The staged sets match that plan: five quota files, eleven evaluation files, and eleven parent files.
Task records, local editor files, build outputs, and plugin gitlinks remain outside this staging step.
Both production submodules have empty unstaged diffs.
The template submodule remains unchanged.
Temporary verification trees and the clean research clone moved to Trash after acceptance.
Rollback snapshots remain at `/tmp/sub2api-v0.2.21-rollback-{parent,quota,eval}.patch` until the user reviews the work commits.
