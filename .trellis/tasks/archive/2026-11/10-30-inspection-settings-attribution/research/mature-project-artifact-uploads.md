# Research: Mature Project Artifact Uploads

- Query: Inspect mature binary projects and record how their workflows group Actions artifacts and publish Release assets.
- Scope: External and parent-provided source
- Date: 2026-11-06

## Findings

### sharkdp/bat

The `build` job uses a Rust target matrix. Each matrix job creates that target's release package. It uploads the tarball in an `actions/upload-artifact` step. It uploads an optional Debian package in a second step. The workflow labels these steps `Artifact upload: tarball` and `Artifact upload: Debian package`.

The same matrix job publishes its files to the GitHub Release with one `softprops/action-gh-release@v2` step. Its `files:` input lists the tarball and Debian package paths. These are Release assets, not Actions artifacts. This is a direct example of one Release action call attaching multiple files. It is not one action call for all target jobs. Each target job publishes the package files that it built. The project packages its executable in a tarball, so that package format does not match the no-tar requirement.

Source: [CICD.yml](https://github.com/sharkdp/bat/blob/master/.github/workflows/CICD.yml). Short source text: `Artifact upload: tarball`; `Publish archives and packages`; `files: |`.

### rustdesk/rustdesk

The Flutter build workflow uses separate Actions artifact upload steps for EXE and MSI outputs. The same workflow also uses `softprops/action-gh-release` to publish multiple files in one step. One `files:` list includes `./SignOutput/rustdesk-*.msi` and `./SignOutput/rustdesk-*.exe`. Another lists seven platform installers. The Release entries are independent Release assets, not one Actions artifact.

This shows two distinct interfaces in one workflow: named Actions artifacts for workflow-run handoff, and a multi-file Release action for user downloads. The Release action accepts multiple file patterns or paths in one invocation. It does not merge the files into one product archive.

Source: [flutter-build.yml, Actions artifacts](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml#L556-L570), [Release upload](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml#L572-L580), and [signed update assets](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml#L1281-L1294). Short source text: `files: |`; `./SignOutput/rustdesk-*.msi`; `./SignOutput/rustdesk-*.exe`.

### sub2api v0.2.19

The upstream `release.yml` uses a `build-binaries` matrix. Each platform job writes its package files and manifest to `matrix-output/`, then uploads that directory as one Actions artifact named `release-binary-<os>-<arch>`. The release job downloads `release-binary-*` with `merge-multiple: true`. It then calls GoReleaser once to publish the collected files and release notes.

This is one directory upload step per platform job, not one upload invocation for all platforms. The upload is a workflow-run artifact handoff. The later GoReleaser step publishes Release assets. The two artifact types are not interchangeable.

Source: [Sub2API v0.2.19 release.yml](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.github/workflows/release.yml#L108-L191). Short source text: `path: matrix-output/`; `pattern: release-binary-*`; `merge-multiple: true`.

## Application

These projects separate Actions artifacts from Release assets. Actions artifacts support workflow handoff. Release steps attach user-downloadable files to a Release.

For Sub2API-Plugins, one `actions/upload-artifact` step can upload a product directory as one workflow artifact. The action stores that directory as one ZIP artifact. This does not create a product tarball, but it changes workflow downloads from separate files to one ZIP. A platform-named artifact per matrix job follows the Sub2API pattern.

The current Release creation command already attaches matching product files as separate Release assets. Keep that path. The mature examples do not require a new SDK loop or a replacement Release action.

The `bat` workflow shows separate Actions artifact steps for package types and one Release action call with multiple paths per target job. RustDesk shows Release actions with multiple installer paths in one step. The Sub2API workflow shows one directory artifact per platform, followed by one aggregate publish job. None of these examples requires a custom artifact SDK.

## Files Found

- `sharkdp/bat/.github/workflows/CICD.yml` — target matrix, per-package Actions artifact steps, and multi-file Release upload.
- `rustdesk/rustdesk/.github/workflows/flutter-build.yml` — separate EXE/MSI Actions artifact steps and multi-file Release uploads.
- `Wei-Shaw/sub2api/.github/workflows/release.yml` — per-platform directory artifact handoff and merged GoReleaser publish.

## External References

- [Upload artifact v7.0.2 README](https://github.com/actions/upload-artifact/blob/v7.0.2/README.md) — normal multi-file uploads create one archived Actions artifact; `archive: false` accepts one file.
- [Sub2API v0.2.19 release workflow](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.github/workflows/release.yml#L108-L191) — platform artifacts and aggregate publish job.
- [RustDesk Flutter build workflow](https://github.com/rustdesk/rustdesk/blob/master/.github/workflows/flutter-build.yml) — installer Actions artifacts and Release assets.
- [bat CI/CD workflow](https://github.com/sharkdp/bat/blob/master/.github/workflows/CICD.yml) — target matrix and Release file list.

## Caveats / Not Found

The RustDesk and Sub2API source details came from the parent agent's source inspections. The `bat` workflow uses `actions/upload-artifact@master`, so its action reference is not a version-pinning recommendation.
