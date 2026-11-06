# Research: One Cache Load Step

- Query: Remove cache-path discovery and use one multi-path cache load for Go modules, Go compilation data, and pnpm, without changing the build interface.
- Scope: Internal and external
- Date: 2026-11-06

## Findings

### Preferred workflow-only design

Declare fixed paths in the build job environment:

```yaml
env:
  GOMODCACHE: ${{ github.workspace }}/dist/cache/go-mod
  GOCACHE: ${{ github.workspace }}/dist/cache/go-build
  pnpm_config_store_dir: ${{ github.workspace }}/dist/cache/pnpm
```

Use one `actions/cache/restore@v6.1.0` step after source preparation. Its `path` input lists those three paths. Keep one matching `actions/cache/save@v6.1.0` step after successful work. This is one load step for all caches and one save step. It removes `Locate dependency caches` without adding builder outputs or arguments.

The cache key can use runner OS and architecture, setup Action outputs for the installed Go and Node versions, the source step's pnpm version, the downloaded dependency files, `scripts/build.py`, and the source revision. The restore prefix omits only the source revision. Save with the restore step's primary key when there was no exact hit.

Add IDs to the existing setup steps and use their declared outputs. The tagged `actions/setup-go@v7.0.0/action.yml` declares `go-version`; `actions/setup-node@v7.1.0/action.yml` declares `node-version`. The source step already exports `pnpm`. This removes manual Go, Node, and pnpm discovery from the `Locate dependency caches` step.

Go reads `GOMODCACHE` and `GOCACHE`. pnpm 12.16.1 reads `pnpm_config_store_dir` and ignores `npm_config_store_dir`. A local probe verified that the configured store is stable across two working directories. pnpm added its `v11` directory under the configured parent, so the cache path must use the parent and must not hardcode the child directory.

`scripts/build.py:173-181` copies `os.environ` and only removes target variables. Its subprocesses therefore inherit these workflow paths without a builder change.

### Evaluated restore/save alternatives

The full `actions/cache@v6.1.0` Action is an alternative. Its metadata defines a restore main action and a save post action that runs after success. That can use one YAML step for both phases, but GitHub still runs a post phase. It is not the same lifecycle as one explicit restore/load step plus one explicit save step.

The revised task plan keeps one explicit load and one explicit save for review.
The earlier automatic post-save proposal was not approved. It is not the selected implementation.

The explicit restore/save design keeps cache loading and saving visible and separate. It also preserves the current save condition and primary-key handling. The full cache Action would make the step declaration shorter, but it changes the chosen lifecycle and its visible run-log behavior.

### Mature workflow examples

Tailscale's test workflow declares `GOMODCACHE` at workflow scope and uses the literal path in separate restore/save Actions. Vue's CI delegates pnpm caching to `setup-node` with `cache: pnpm`. Neither example combines Go and pnpm in one cache operation. The requested combined three-path cache is a project decision, not a pattern established by those examples.

### Trellis phase gate

The current cache correction has returned to Phase 1, while the parent task retains its existing `in_progress` status.
The revised planning artifacts need review before implementation. The status does not approve a replacement design.
After approval, dispatch `trellis-implement`, then `trellis-check`. Main owns integration, spec updates, commit approval, and finish-work.
This report does not authorize product edits.

## Files Found

- `.trellis/workflow.md:193-208` — Phase 1 requires planning review before task activation; Phase 2 and Phase 3 define implementation, check, spec update, commit, and wrap-up.
- `.trellis/tasks/10-30-inspection-settings-attribution/design.md:297-310` — R22 leaves the save lifecycle undecided and prohibits assuming automatic post-save.
- `.trellis/tasks/10-30-inspection-settings-attribution/implement.md:19-25` — current stage is research; do not edit product files or dispatch implementation before plan review.
- `.github/workflows/build.yml:66-117` — current setup steps, path-discovery step, and one multi-path restore step.
- `.github/workflows/build.yml:153-162` — current matching multi-path save step and primary-key handling.
- `plugins/codex-candy-eval/.github/workflows/build.yml`, `plugins/sub2api-quota-extension/.github/workflows/build.yml`, `plugins/sub2api-plugin-template/.github/workflows/build.yml` — same cache step structure as the parent workflow.
- `scripts/build.py:173-181` — build commands inherit workflow environment settings.
- `.trellis/tasks/10-30-inspection-settings-attribution/research/cache-path-configuration.md` — Go and pnpm path contracts and the local pnpm 12.16.1 probe.
- `.trellis/tasks/10-30-inspection-settings-attribution/research/mature-cache-workflows.md` — Tailscale and Vue workflow examples.
- `.trellis/spec/backend/minimal-linux-delivery.md:131-159` — current one-restore/one-save contract and cache-key requirements.

## External References

- [Go environment variables](https://pkg.go.dev/cmd/go#hdr-Environment_variables) — `GOMODCACHE` and `GOCACHE`.
- [pnpm environment variables](https://pnpm.io/configuring#environment-variables) — `pnpm_config_` values and ignored `npm_config_*` values.
- [setup-go v7.0.0 action metadata](https://github.com/actions/setup-go/blob/v7.0.0/action.yml) — `go-version` output.
- [setup-node v7.1.0 action metadata](https://github.com/actions/setup-node/blob/v7.1.0/action.yml) — `node-version` output.
- [actions/cache v6.1.0 metadata](https://github.com/actions/cache/blob/v6.1.0/action.yml) — restore main action and automatic successful post-save action.
- [actions/cache usage](https://github.com/actions/cache/blob/v6.1.0/README.md) — explicit restore/save example and cache key behavior.
- [Tailscale test workflow](https://github.com/tailscale/tailscale/blob/main/.github/workflows/test.yml) — declared Go cache path with restore/save Actions.
- [Vue CI workflow](https://github.com/vuejs/core/blob/main/.github/workflows/ci.yml) — setup-node-managed pnpm caching.

## Related Specs

`.trellis/spec/backend/minimal-linux-delivery.md:151-156` currently specifies paths discovered by Go and pnpm commands, one restore Action, and one save Action. If the user approves the fixed-environment design, update that spec to describe the fixed workflow paths and setup Action outputs. Do not change the spec during this research-only stage.

## Caveats / Not Found

The pnpm probe used pnpm 12.16.1 on Darwin arm64. The configuration contract is documented by pnpm, but this probe did not run a hosted Actions job.

One multi-path cache couples hit and invalidation behavior for all three directories. A cache prefix may restore dependency-compatible data after an exact key miss. Cache misses still run the normal frozen install, tests, and compilation.

The mature examples do not establish a combined Go/pnpm cache. This report supports removing path discovery.
The main session's R22/R23 plan owns the explicit save lifecycle and the original Release naming/structure request.
