# GitHub Actions research for the unified plugin task

## Existing implementation

- Parent `.github/workflows/release.yml` builds both common binaries, then publishes a Release on tag pushes.
- Eval `.github/workflows/release.yml` checks out Sub2API v0.2.18 despite its local builder targeting v0.2.19.
  It uses Node 20, passes the retired manual source/check arguments, uploads only the installer, and publishes Releases.
- Quota has no `.github` workflow or standalone builder.
- Parent `scripts/build.py` already owns source download, plugin discovery, tests, server build, licenses, and installer packaging.
- Parent `tests/support.py` still hardcodes pnpm 9.15.9 for native Vue suites.
- Eval has a separate historical builder with retired arguments.
  The user requires complete aligned build kits in the parent, eval, quota, and template.
  Each local build and CI runs its own `python3 scripts/build.py` without a remote build Action.

## Verified stable releases on 2026-10-30

Anonymous GitHub `releases/latest` and tag-ref API reads verified these releases.
The user requires exact release tags in workflow references, without commit hashes or major-only tags.

| Action | Exact release tag |
| --- | --- |
| [actions/checkout](https://github.com/actions/checkout/releases/tag/v7.0.1) | v7.0.1 |
| [actions/setup-go](https://github.com/actions/setup-go/releases/tag/v7.0.0) | v7.0.0 |
| [actions/setup-node](https://github.com/actions/setup-node/releases/tag/v7.1.0) | v7.1.0 |
| [actions/setup-python](https://github.com/actions/setup-python/releases/tag/v7.1.0) | v7.1.0 |
| [actions/upload-artifact](https://github.com/actions/upload-artifact/releases/tag/v7.0.2) | v7.0.2 |

Toolchain sources confirmed these stable releases:

| Tool | Current stable version | Original source |
| --- | --- | --- |
| Go | 1.27.3 | [go.dev download JSON](https://go.dev/dl/?mode=json) |
| Node.js | 26.13.0, Lithium LTS | [Node distribution index](https://nodejs.org/dist/index.json) |
| Python | 3.15.2 | [CPython release tag](https://github.com/python/cpython/releases/tag/v3.15.2) |
| pnpm | 12.16.1 | [Official release](https://github.com/pnpm/pnpm/releases/tag/v12.16.1) and npm `latest` metadata |
| Corepack | 0.36.0 | [Official release](https://github.com/nodejs/corepack/releases/tag/v0.36.0) and npm `latest` metadata |

Exclude Node 27 alpha and Python 3.16 alpha from stable selections.
Recheck before implementation if new stable releases appear.
Do not add an auto-update bot or workflow lock manifest solely for this task.

## Official practices used

- [GitHub security hardening](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
  recommends full commit SHA pins and minimal token permissions.
  The user's explicit reference policy selects exact release tags. Minimal token permissions remain unchanged.
- [Checkout README](https://github.com/actions/checkout) documents `persist-credentials: false`.
- [upload-artifact v7.0.2 README](https://github.com/actions/upload-artifact/blob/v7.0.2/README.md)
  documents `archive: false` for a direct single-file upload and `if-no-files-found: error`.
  Its Permission Loss section recommends tar before direct upload to preserve executable modes.
  A later source review found that direct mode ignores `name` and uses the uploaded filename as the artifact name.
  See the release [action.yml](https://github.com/actions/upload-artifact/blob/v7.0.2/action.yml).
  The upload tar must be `dist/sub2api-plugins-installer`, without `.tar`, to meet the fixed artifact-name requirement.
  This archive is separate from `dist/build/sub2api-plugins-installer`, which remains the executable installer.
  The release [upload flow](https://github.com/actions/upload-artifact/blob/v7.0.2/src/upload/upload-artifact.ts) passes `skipArchive` to artifact storage.
  The release [shared upload helper](https://github.com/actions/upload-artifact/blob/v7.0.2/src/shared/upload-artifact.ts) returns `artifact-url` for the uploaded artifact ID.
- [GitHub job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#adding-a-job-summary)
  use `GITHUB_STEP_SUMMARY` without another reporting Action.
- [Template repository guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository)
  requires the template setting. Generated repositories copy the default-branch files with their own history.
- [Corepack README](https://github.com/nodejs/corepack) explains separate installation for current Node versions.
- [pnpm settings](https://pnpm.io/settings) places project settings in `pnpm-workspace.yaml`.
  The package.json `pnpm` section no longer supplies overrides in pnpm 12.

Search summaries were checked against original release APIs and fetched official documentation.
No personal GitHub credentials were used.

## Latest pnpm compatibility probe

Use detached Sub2API v0.2.19 source commit `dece26153621959ccd7635814f4b2d08304e681a`.
Probe directory: `/tmp/sub2api-ci-pnpm.3b8za4/source`.
Command: `corepack pnpm@12.16.1 install --frozen-lockfile --lockfile-only --ignore-scripts`.

The unchanged source failed with `ERR_PNPM_LOCKFILE_CONFIG_MISMATCH` because pnpm 12 ignored `package.json` overrides.
The source declares six overrides and no existing `pnpm-workspace.yaml`.
Adding those same overrides to a temporary `frontend/pnpm-workspace.yaml` made the probe pass.
Git showed no changes to `package.json` or `pnpm-lock.yaml` afterward.
This preserves override values and the existing lockfile. It does not establish full install or Linux compilation success.
Translate effective dependency build settings during implementation, then verify the actual build on the selected runner.

The probe used local Node 24.21.0 and Corepack 0.36.0. The planned CI uses current Node 26 LTS.
No global tools or product files changed. Corepack downloaded its normal cached pnpm binary.

## Review boundaries

Keep the current application source version and lockfile. Latest CI tools do not mean latest application dependencies.
Use complete aligned build kits and independent workflows in all four repositories.
The shared composite Action and CI adapter proposal is superseded by the user's correction.
Place the template in `plugins/` as a submodule. Exclude it from combined builds while its patch set is empty.
Keep common build/installer test files aligned, and execute common cases only once per build.
Add the explicitly requested template README in Chinese.
All repositories use fixed `sub2api-plugins` and `sub2api-plugins-installer` output names.
Do not add repository-name inference, old-name aliases, or naming compatibility tests.
Use existing tests through the default build and inspect actual workflow runs without deliberate remote failures or a separate lint gate.
Keep product outputs separate from failure diagnostic artifacts.
Create no Release, container image, issue, or external notification.
Personal credential approval remains required for repository creation, pushes, dispatches, and authenticated result reads.

## Full CI recheck on 2026-10-31

The selected checkout, Python, Go, Node, and upload Actions' original metadata supports the configured inputs and Node 24 Action runtime.
That runtime is separate from the selected Node 26.13.0 application build tool.
The fixed upload filename now matches direct-upload artifact naming. The ignored product `name` input was removed from all four workflows.
The actual package shell passed in a temporary directory. Its tar contains only the two expected files with mode 0755.
Unpack the suffix-free download into a separate directory because its name matches the enclosed executable installer.
The template README now shows that extraction path.

The passing local build used Python 3.14.8, Go 1.27.2 on Darwin/arm64, and Node 24.21.0.
It does not establish execution with CI's Python 3.15.2, Go 1.27.3, Node 26.13.0, or Linux runner.
Those selected tools and actual artifact uploads remain covered by the planned four remote CI runs after authorization.
