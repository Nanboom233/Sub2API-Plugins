# Research: CI Step Consolidation

- Query: Verify whether the current CI can combine cache restore/save and final artifact uploads without changing artifact semantics or expanding Release token permissions.
- Scope: Internal and external
- Date: 2026-11-06

## Findings

The pinned cache action accepts a list of paths, but each restore/save invocation has one `key`. A single restore and a single save can therefore handle the Go module, Go build, and pnpm paths without a wrapper. They become one cache entry under one key, so the caches no longer have independent hit and invalidation behavior. A combined key must account for every input that can invalidate those paths; a change to one dependency input can invalidate the whole entry. The current workflow has three independent restore and save pairs at `.github/workflows/build.yml:109` and `.github/workflows/build.yml:206`.

`actions/upload-artifact@v7.0.2` explicitly limits `archive: false` to one file. In this mode, the uploaded filename becomes the artifact name and `name` is ignored. One upload step cannot preserve the current ten separate raw executable artifacts (`.github/workflows/build.yml:136`). A single multi-file upload uses the normal archive mode and changes the download to one artifact containing multiple files. Keep the per-file upload steps if separate raw artifacts are required; otherwise, accept that artifact-format change explicitly.

`permissions` is workflow- or job-scoped, not step-scoped. GitHub documents that every action and `run` command in a job that uses `GITHUB_TOKEN` receives that job's configured access. The supported `contents` levels are fixed values (`read`, `write`, or `none`); the context-availability table does not list `jobs.<job_id>.permissions` as an expression-capable key. Do not try to make `contents: write` conditional on a Release input. Keep Release in its existing separate job so build steps do not inherit its write access (`.github/workflows/build.yml:224`).

The simplest acceptable consolidation is one cache restore and one cache save using multi-path input, after accepting the shared-key tradeoff. Preserve individual upload steps for raw artifacts and preserve the separate write-enabled Release job. This needs no wrapper or custom workflow scaffold.

## Files Found

- `.github/workflows/build.yml:38` — workflow-level read permission; cache restore/save steps; ten single-file uploads; separate Release job with `contents: write`.
- `.trellis/tasks/10-30-inspection-settings-attribution/research/ci-cache-matrix-result.md` — current CI design and prior validation evidence.

## External References

- [Cache action v6.1.0 metadata](https://github.com/actions/cache/blob/v6.1.0/action.yml) — `path` accepts a list; each invocation has one required `key`.
- [Cache restore v6.1.0 metadata](https://github.com/actions/cache/blob/v6.1.0/restore/action.yml) and [save metadata](https://github.com/actions/cache/blob/v6.1.0/save/action.yml) — pinned restore/save inputs.
- [Upload artifact v7.0.2 metadata](https://github.com/actions/upload-artifact/blob/v7.0.2/action.yml) — `archive: false` allows a single file and uses its filename as the artifact name.
- [Upload artifact v7.0.2 README](https://github.com/actions/upload-artifact/blob/v7.0.2/README.md) — multiple paths are supported in the normal archived upload mode.
- [GitHub workflow syntax: permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idpermissions) — permission scope, accepted levels, and job-wide effect.
- [GitHub contexts: availability](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#context-availability) — expression contexts are limited to the listed workflow keys; `jobs.<job_id>.permissions` is not listed.
- [GitHub Actions workflow JSON schema](https://github.com/SchemaStore/schemastore/blob/master/src/schemas/json/github-workflow.json) — `permissions` levels are schema enums, not arbitrary expressions.

## Caveats / Not Found

No native step-level permission control or dynamic `permissions` expression support was found in the current GitHub workflow syntax. Combining uploads without a format change is not supported by the pinned action.
