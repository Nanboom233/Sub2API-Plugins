# CI dependency caches and build matrices

## Decision

Keep `python3 scripts/build.py` as the only build entry in all four kits.
Split CI execution into source preparation, shared checks, server compilation, installer compilation, and final publication.
Use dependency caches for reusable dependencies and Go compilation data.
Use ordinary Actions artifacts for current-run source and executable handoffs.
Do not create tar files, output manifests, wrappers, or another build entry.

This planning review ran on 2026-11-05.
The prior successful runs took 11m47s for template, 16m53s for eval, 18m29s for quota, and 20m17s for parent.
Those durations establish a baseline, not a promised reduction.
The existing four successful runs and their artifact evidence remain valid. This research did not query or rerun them.

## Build entry and phase contract

Use three internal environment variables:

| Variable | Meaning |
| --- | --- |
| `SUB2API_BUILD_STAGE` | `source`, `prepare`, `server`, `installer`, or `publish`. Unset means the complete local build |
| `SUB2API_BUILD_WORKSPACE` | Existing work directory for CI phases. CI uses ignored `dist/work`. Unset retains the temporary local workspace |
| `SUB2API_BUILD_TARGET` | One approved `<os>-<arch>` for a server or installer phase |

Retain `UPSTREAM_TAG` as the existing tag input.
Only `source` resolves the default upstream tag. It exposes the selected tag through the existing `GITHUB_OUTPUT` mechanism.
Later phases receive that exact tag and prepared source. They do not resolve latest again, clone, or reapply patches.
The default argument-free local build calls the same phase functions in order and retains atomic output replacement.
The stage interface supplies orchestration context. It does not expose test-skipping or check flags.

## Job graph and current-run data

```text
prepare job
  build.py source -> cache restore -> build.py prepare
          |
          v
server matrix: linux-arm64, darwin-amd64, darwin-arm64, windows-amd64
          |
          v
installer matrix: all five approved targets
          |
          v
publish job: validate and upload all ten direct executables
```

The prepare job downloads and patches once, builds the frontend once, and runs plugin tests and vet once.
It also prepares installer dependencies and license resources.
Compile Linux/amd64 there before common installer tests because those tests extract and execute that embedded payload.
That requirement describes Ubuntu amd64 CI. Local builds must also prepare the current host architecture's Linux payload, which the test entry selects at runtime.
Darwin/arm64 therefore needs its Linux/arm64 fixture payload before shared tests, preserving existing local invocation behavior.
Run common tests once with that payload. Reuse the resulting Linux/amd64 server rather than compiling it in the server matrix.
No matrix job repeats source preparation, frontend work, business tests, or common installer tests.

| Producer | Internal artifact content | Consumer |
| --- | --- | --- |
| Prepare | `internal-prepared`: `source/backend`, including built embedded frontend, plus installer sources, `go.mod`, `go.sum`, and original licenses | Server and installer jobs |
| Prepare and server matrix | `internal-server-<target>`: one native server under its unique target filename | Installer and publish jobs |
| Installer matrix | `internal-installer-<target>`: one versioned installer | Publish job |

The prepared handoff excludes `node_modules`, source `.git`, and generated installer payload directories.
Use `upload-artifact` path inputs and its standard archive format for internal handoffs.
Use matching named downloads, or `pattern` with `merge-multiple` when unique target filenames prevent collisions. [S1–S2]
Do not add manual tar packaging or artifact cleanup permissions.

An installer job receives only its native server and matching Linux server.
Linux targets use one payload. Darwin and Windows targets embed both their native payload and matching Linux payload.
Each installer job creates its own payload directory. Parallel jobs do not modify a shared directory.
Downloaded programs are data for embedding, not cross-platform programs to execute.

Standard archived artifacts do not preserve executable mode. [S2]
Restore `0755` on server and installer output files before existing executable-output validation or final publication.
The prepare tests use their original local Linux executable, before artifact upload.
No required source symlink has been identified. Do not add a new packaging mechanism without a concrete affected path.

Use `needs` to place a success barrier before each downstream group. [S3]
Installer jobs need prepare and the server matrix. Publish needs prepare and both matrices.
No product upload occurs in a compilation job.
Publish downloads all required current-run files, checks the existing expected outputs, and calls the build entry's publish phase.
Only then do the ten existing direct uploads run, with versioned basenames and `archive: false`. [S1]
Do not collect matrix file lists through one overwritten job-output name. Target-derived artifact names identify the files.

Internal artifacts remain visible in the workflow run, including after a later failure.
They are intermediate data, separate from the ten final product artifacts.
This design does not promise that a successful run contains only ten artifact entries.

## Cache timing and ownership

Keep `setup-go` automatic caching disabled. The repository has no root `go.sum` for it to read before source download.
`hashFiles` can read only files inside `GITHUB_WORKSPACE` and returns an empty string for unmatched paths. [S4]
Therefore, run `source` in `dist/work` before computing lockfile-based keys.
Matrix jobs download the prepared handoff before restoring their Go caches.

Restore these caches through `actions/cache/restore@v6.1.0`:

| Data and actual path lookup | Key inputs | Save owner |
| --- | --- | --- |
| Go module downloads, `go env GOMODCACHE` | Runner OS/architecture, Go version, upstream `backend/go.sum`, and `scripts/build.py` installer dependency declaration | Prepare only. Matrix jobs restore this cache without saving it |
| Go compilation data, `go env GOCACHE` | Runner OS/architecture, Go version, target, phase role, dependency identity, checkout revision | Prepare for Linux/amd64 checks. Each server and installer job owns its distinct target/role key |
| pnpm store, selected pnpm's `store path --silent` | Runner OS/architecture, Node and pnpm versions, downloaded frontend lockfile, and `scripts/build.py` | Prepare only |

Read cache paths from those tools. Do not assume a fixed pnpm store directory or cache `node_modules`.
Source preparation can expose the selected pnpm spec as a step output, avoiding a second workflow-owned version constant.
The builder file hash includes its PTerm pin and pnpm adaptation settings.
The upstream sum and builder pin identify Go downloads before installer `go.sum` exists.
After prepare, its generated installer `go.sum` is also available for target compilation cache keys.

Example key shapes use normal workflow expressions:

```text
gomod-<host>-go<version>-<hashFiles(source/backend/go.sum,scripts/build.py)>
pnpm-<host>-node<version>-pnpm<version>-<hashFiles(source/frontend/pnpm-lock.yaml,scripts/build.py)>
gobuild-<host>-go<version>-<target>-<role>-<dependency-hash>-<github.sha>
```

Use full `dist/work/...` paths in the actual `hashFiles` expressions.
For Go compilation data, remove only the revision suffix for a same-target/role restore prefix.
An installer may also restore the current run's same-target server cache, or prepare's native cache, through explicit restore keys.
The installer saves under its own role key, so concurrent jobs cannot compete for the same new key.
Module and pnpm restore prefixes may reuse an older same-host/tool cache. Normal dependency installation still runs.
Go's dependency and compilation checks determine reusable entries. A cache never substitutes for a required build phase.

Save explicitly with `actions/cache/save@v6.1.0` after the owning work succeeds and the exact primary key missed.
Use the restore step's `cache-primary-key` output rather than recalculating a changed key. [S5]
A miss uses the normal build path. Do not set `fail-on-cache-miss` or skip tests, installation, or compilation on a cache hit.
Do not cache prepared source, final binaries, installer payloads, or current-run publication state.

## Official Action versions and reporting

The official latest-release endpoints returned these non-prerelease tags on 2026-11-05:

| Action | Exact selected tag |
| --- | --- |
| `actions/cache/restore` and `actions/cache/save` | `v6.1.0` |
| `actions/download-artifact` | `v8.0.2` |
| `actions/upload-artifact` | `v7.0.2` |
| `actions/checkout` | `v7.0.1` |
| `actions/setup-go` | `v7.0.0` |
| `actions/setup-node` | `v7.1.0` |
| `actions/setup-python` | `v7.1.0` |

Use exact tags, not commit hashes or major-only references.
Keep read-only repository permissions and disabled checkout credential persistence.
Current-run artifact download needs no personal token or cross-run credential. [S2]
Keep the current Go, Node, Python, Corepack, and pnpm selections. Cache/matrix work does not require unrelated tool upgrades.

Each failed build phase retains its existing native log and one distinct failure-log artifact.
Use stage/target-specific diagnostic names to avoid collisions between matrix jobs.
Summaries identify the failed job and available diagnostic location without copying log bodies.
Artifact transfer or upload failures retain their own step errors. They do not become compiler failures.
No Release, image publication, external provider, `actions: write`, or cleanup job is required.

## Focused verification

Extend the existing build composition and failure cases for stage handoff, tests once, correct payload selection, and deferred publication.
Keep the default no-argument path covered by the existing builder cases.
Do not add workflow-text tests, generated deployment fixtures, a runtime matrix, repeated business tests, or deliberate remote failures.
Use one approved final workflow candidate per repository for changed CI execution evidence.
Reuse current successful runtime, format, payload, and license evidence where behavior remains unchanged.

## Official sources

- S1. [Upload Artifact v7.0.2: direct files, unique matrix names, archive behavior](https://github.com/actions/upload-artifact/blob/v7.0.2/README.md).
- S2. [Download Artifact: same-run download, patterns, and permission behavior](https://github.com/actions/download-artifact/blob/v8.0.2/README.md).
- S3. [GitHub artifact handoffs and needs](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow) and [matrix producers and consumers](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs).
- S4. [GitHub expressions: hashFiles workspace limits](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions#hashfiles).
- S5. Cache v6.1.0 [restore contract](https://github.com/actions/cache/blob/v6.1.0/restore/README.md) and [save contract](https://github.com/actions/cache/blob/v6.1.0/save/README.md).
- Release verification: [cache](https://api.github.com/repos/actions/cache/releases/latest), [download](https://api.github.com/repos/actions/download-artifact/releases/latest), [upload](https://api.github.com/repos/actions/upload-artifact/releases/latest), [checkout](https://api.github.com/repos/actions/checkout/releases/latest), [Go](https://api.github.com/repos/actions/setup-go/releases/latest), [Node](https://api.github.com/repos/actions/setup-node/releases/latest), and [Python](https://api.github.com/repos/actions/setup-python/releases/latest).

## Follow-up: selected platforms and optional Releases

The user subsequently requested platform/version inputs and restored Release publication in the same workflow.
This section supersedes the earlier fixed-five-output and artifact-only publication boundary for that addition.
Retain the cache design, one build entry, shared checks once, and direct executable files.

### Manual inputs and automatic events

GitHub supports typed dispatch inputs, but `choice` selects only one option. [S6]
Use five Boolean inputs, each defaulting to true: `linux_amd64`, `linux_arm64`, `darwin_amd64`, `darwin_arm64`, and `windows_amd64`.
Retain editable `upstream_tag`, default `v0.2.19`. Automatic events retain the existing latest-stable upstream selection.
Resolve that source tag once, then reuse it in all jobs and program names.
Do not infer the Sub2API source version from the plugin repository's Release tag.

Add `release`, Boolean, default false, and `release_tag`, string.
Require a nonempty `release_tag` only when manual Release publication is enabled.
Keep ordinary branch pushes and pull requests artifact-only, with all platforms selected.
Restore automatic publication for pushed `v*` repository tags in this same `build.yml`.
For that event, derive the Release tag from `github.ref_name` and build all platforms.
No parallel release workflow or second build is needed.

### Target closure and empty matrices

Let `S` contain the selected output platforms. Reject an empty selection before expensive work.
Compile the servers in `S`, their matching Linux installer payloads, and the Linux/amd64 common-test payload.
Prepare still compiles Linux/amd64 once. The server matrix compiles only required targets not already supplied by prepare.
The installer matrix contains only `S`.
Publish and Release attach only the selected platform pairs, which means `2 * len(S)` product files.
Supporting Linux payloads do not become extra product assets.

Example: selecting only Darwin/arm64 compiles Linux/amd64 for common tests, then Darwin/arm64 and Linux/arm64 for the installer.
Only the Darwin/arm64 server and installer become final products.
Selecting only Linux/amd64 produces an empty server matrix.

Emit ordinary JSON matrix and count outputs from prepare and use `fromJSON` for expansion. [S7]
Use a job-level condition to skip the server group when its count is zero.
GitHub evaluates job `if` before matrix expansion. [S6]
Do not expand an empty matrix or replace it with a fake platform.

Default `needs` success handling would also skip the installer and publish groups after an intentionally skipped server group. [S6]
Use `!cancelled()` with explicit dependency-result conditions to allow only that expected skip.
Prepare must succeed. A nonempty server matrix must succeed. An empty server matrix may be skipped.
The selected installer matrix must succeed before publication.
An actual failure, cancellation, or unexpected skip must not pass the product barrier.
Do not use an unconditional `always()` publication path.

### Release job and exact commit ownership

Add one Release job after successful selected-output publication.
Keep workflow-level `contents: read` and grant only this job `contents: write`. [S6, S8]
Use `GH_TOKEN: ${{ github.token }}`. GitHub-hosted runners already include `gh`. [S8–S9]
No personal token, repository secret, new Release Action, or `actions: write` permission is needed.
Tag creation through this built-in token does not trigger another push workflow run. [S11]

Download the selected successful products from the same run and pass those exact files to `gh release create`.
Use the explicit user-selected title and `--generate-notes`. The body contains only the actual generated CHANGELOG.
Pass inputs through quoted environment values and asset arguments.
Do not concatenate user-supplied tags or notes into shell code.

Use `--target "$GITHUB_SHA"` when creating a missing repository tag.
The CLI documents that `--target` controls automatic tag creation. It does not move an existing tag. [S10]
If the tag already exists, resolve its commit, including annotated-tag dereference, and compare it with the built commit.
Fail publication on a mismatch. Do not force or move the tag.
For a tag-push build, the triggering tag identifies the same built source commit.

Create a new Release. Do not update an existing Release or use asset clobber behavior.
An existing Release, tag conflict, or upload failure reports its actual error and preserves successful Actions artifacts.
`gh release create` can leave a draft after a partial asset-upload failure because its API requests are not atomic. [S10]
Report that failure without claiming a completed Release or adding automatic cleanup.

### Proposed title and body

Use the literal prefix `Sub2API-Plugin` in all four repositories.
Use the built source commit's first seven hexadecimal characters and upstream version with exactly one leading `v`.
The final title shape is `Sub2API-Plugin <hash> (v<upstream-version>)`.
For parent commit `66f17f7` and upstream tag `v0.2.19`, the title is:

```text
Sub2API-Plugin 66f17f7 (v0.2.19)
```

Use only the actual GitHub-generated CHANGELOG in the body.
Pass `--generate-notes` without `--notes` or `--notes-file`.
Do not add installation text, platform lists, provenance blocks, a body template, or another CHANGELOG file.

### Follow-up sources

- S6. [Workflow syntax: dispatch input types, job conditions, skipped needs, and permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
- S7. [Dynamic matrices from a prior job's outputs](https://docs.github.com/en/actions/using-jobs/using-a-matrix-for-your-jobs#using-an-output-to-define-two-matrices).
- S8. [Built-in token and job-specific permissions](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token).
- S9. [GitHub CLI in workflows](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-what-your-workflow-does/using-github-cli-in-workflows).
- S10. [gh release create: target, title, notes file, assets, and partial-failure behavior](https://cli.github.com/manual/gh_release_create).
- S11. [Built-in token event behavior](https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow#triggering-a-workflow-from-a-workflow).
