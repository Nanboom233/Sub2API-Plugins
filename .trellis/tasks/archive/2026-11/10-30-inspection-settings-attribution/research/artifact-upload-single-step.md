# Research: One-Step Raw Artifact Upload

This report records the SDK capability and approved R21 implementation.
Use `mature-project-artifact-uploads.md` for the separate comparison of mature project workflows.
After that comparison, the user selected and approved the SDK approach.

- Query: Find the smallest maintained approach for one visible workflow step to upload each selected executable as its own unarchived Actions artifact.
- Scope: Internal and external
- Date: 2026-11-06

## Findings

The inspected official release page lists `v7.0.2` as latest. Its `archive: false` input accepts one file. The tagged source rejects multiple matches. Normal archive mode makes one ZIP artifact from multiple files. The action cannot upload ten raw files in one invocation.

The official `@actions/artifact` SDK is the supported API for raw uploads. Its current package version is `6.3.1`. The `v7.0.2` upload action depends on `^6.3.1`. The SDK exports `DefaultArtifactClient` and `UploadArtifactOptions.skipArchive`. A raw upload call accepts one file. The SDK uses the file basename as its artifact name. It ignores the supplied name. A loop can therefore create one raw artifact per output. The ten current output names are distinct. An upload error throws and must fail the step.

I found no suitable maintained third-party batch action. The closest candidate is `nanoufo/action-upload-artifacts-and-release-assets@v2.0`. It loops over files but does not set `skipArchive`. It creates archived artifacts and depends on `@actions/artifact@^2.0.0`. It does not meet the requirement.

**Approved implementation:** use the official SDK from one `actions/github-script@v9.0.0` step. Install exact `@actions/artifact@6.3.1` into `RUNNER_TEMP` inside its script. Import the ESM entrypoint by absolute file URL and upload one file per call.

`github-script@v9.0.0` uses Node 24 and runs as a JavaScript action. It receives the runner artifact environment. It does not include `@actions/artifact`. The script receives the `exec` helper for the temporary install. The actual `RUNNER_TEMP` install and ESM import passed local verification. This route avoids a local action bundle. It adds an npm install at runtime, and it does not lock transitive versions.

Do not use the SDK from a normal `run:` step until runtime-variable access is confirmed. The SDK reads `ACTIONS_RUNTIME_TOKEN` and `ACTIONS_RESULTS_URL`. These are runner artifact credentials, not the repository `GITHUB_TOKEN`. Raw artifact upload does not need `contents: write`.

The inspected `actions/runner` PR #4325 says Node and container actions receive these variables, but shell `ScriptHandler` did not. The PR appeared open in the inspected source. This report does not assume that shell steps receive the variables.

## Files Found

- `.github/workflows/build.yml:136` — one SDK step uploads each selected executable as its own raw artifact.
- `.trellis/tasks/10-30-inspection-settings-attribution/research/ci-step-consolidation.md` — prior pinned action and permissions findings.

## External References

- [Official upload-artifact releases](https://github.com/actions/upload-artifact/releases) — `v7.0.2` listed as latest in the inspected release page.
- [Upload-artifact v7.0.2 action metadata](https://github.com/actions/upload-artifact/blob/v7.0.2/action.yml) and [implementation](https://github.com/actions/upload-artifact/blob/v7.0.2/src/upload/upload-artifact.ts) — direct-file limit and failure behavior.
- [Upload-artifact v7.0.2 package metadata](https://github.com/actions/upload-artifact/blob/v7.0.2/package.json) — Node 24 runtime and `@actions/artifact` dependency.
- [Official artifact package metadata](https://github.com/actions/toolkit/blob/main/packages/artifact/package.json), [public exports](https://github.com/actions/toolkit/blob/main/packages/artifact/src/artifact.ts), [upload API](https://github.com/actions/toolkit/blob/main/packages/artifact/src/internal/upload/upload-artifact.ts), and [options](https://github.com/actions/toolkit/blob/main/packages/artifact/src/internal/shared/interfaces.ts) — current SDK version and raw upload behavior.
- [Artifact SDK runtime configuration](https://github.com/actions/toolkit/blob/main/packages/artifact/src/internal/shared/config.ts) — required runtime token and results URL.
- [GitHub Script v9.0.0 metadata](https://github.com/actions/github-script/blob/v9.0.0/action.yml), [package metadata](https://github.com/actions/github-script/blob/v9.0.0/package.json), and [script implementation](https://github.com/actions/github-script/blob/v9.0.0/src/main.ts) — Node 24 action and helpers supplied to the async script.
- [Runner PR #4325](https://github.com/actions/runner/pull/4325) — source discussion of runtime variables missing from shell `ScriptHandler` and available to Node/container actions; merge status was not rechecked.
- [Nanoufo v2.0 implementation](https://github.com/nanoufo/action-upload-artifacts-and-release-assets/blob/v2.0/src/main.ts) — per-file loop without `skipArchive`.

## Caveats / Not Found

The implementation uses the official raw-upload API through a short inline loop and a runtime install.
Local checks cover package loading, paths, options, missing-file behavior, and exception propagation.
Actual hosted artifact uploads remain untested. No hosted run is an added acceptance gate.

## Approved implementation evidence

The user selected the SDK approach after reviewing the project comparison and approved R21 implementation.
Anonymous public reads on 2026-11-06 confirmed `actions/github-script@v9.0.0` as the latest stable release and `@actions/artifact@6.3.1` as npm's latest version.
The exact Action metadata uses Node 24. The SDK package uses ESM and declares `lib/artifact.js` as its import entry.
The four workflows now use one inline JavaScript Action step. It installs the exact SDK under `RUNNER_TEMP` and imports that entry by file URL.
The step passes each selected final output to `DefaultArtifactClient.uploadArtifact` with `skipArchive: true`.
The installed SDK checks for a missing file before it reads runtime credentials or calls the artifact service. It throws `FilesNotFoundError` directly.
No extra missing-file loop is needed.

An actual temporary npm install and ESM import passed on local Node 24.21.0.
One temporary harness exercised the exact inline script with the real loaded SDK and stubbed upload calls.
It confirmed ten default paths, the Darwin-only pair, Windows `.exe` suffixes, raw-upload options, and first-upload failure propagation.
A real SDK missing-file invocation rejected without a remote upload. Four YAML files parsed and their contents matched.
No test file, product build, hosted run, or Release was added. Hosted upload behavior remains untested.

Primary version sources:

- [GitHub Script latest stable release metadata](https://api.github.com/repos/actions/github-script/releases/latest)
- [GitHub Script v9.0.0 runtime metadata](https://github.com/actions/github-script/blob/v9.0.0/action.yml)
- [Artifact npm latest metadata](https://registry.npmjs.org/@actions%2Fartifact/latest)
