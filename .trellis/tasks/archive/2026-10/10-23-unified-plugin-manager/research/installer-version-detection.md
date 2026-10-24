# Installer Version Detection

- Date: 2026-10-24
- Target: Sub2API v0.2.18
- Scope: Source inspection, one official release executable, and an in-memory format experiment.

## Findings

Use the executable's reported application version for installation checks.
An image reference, image label, source VERSION file, and application version describe different objects.
The installer replaces `/app/sub2api` without changing the image reference or image labels.
Image metadata therefore cannot establish the current executable version.

Compare installed and candidate versions with the build version for advisory warnings.
Normalize an optional leading `v` before this comparison.
Mismatched or unresolved versions require explicit user confirmation before backup or replacement.
Do not resolve `latest` through a registry, GitHub, or an assumed current release.

## Primary Sources

All upstream source links below select the v0.2.18 tag.

| Source | Evidence |
| --- | --- |
| [Server main](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/backend/cmd/server/main.go#L29-L66) | Explicit linker Version takes precedence. The version flag prints the application version before server setup. |
| [Embedded VERSION](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/backend/cmd/server/VERSION) | The tagged file still contains `0.2.17`. |
| [Release preparation](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/.github/release-tools/release_matrix.py#L53-L69) | Release preparation resolves the selected tag and writes its version into the build's VERSION file. |
| [Release workflow](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/.github/workflows/release.yml#L117-L129) | Each binary build receives the prepared VERSION file. |
| [Image publication](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/.github/release-tools/release-images.sh#L29-L36) | Versioned and `latest` manifests refer to the same release architecture images at publication. |
| [Dockerfile](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/Dockerfile) | A source image build injects Version through linker flags. Explicit VERSION overrides the resolver. |
| [Version resolver](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/backend/scripts/resolve-version.sh) | The resolver prefers an exact Git tag and otherwise reads VERSION. |
| [Logger bridge](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/backend/internal/pkg/logger/logger.go#L212-L281) | The logger redirects standard Go logs. Informational records normally use stdout. |
| [Bootstrap options](https://github.com/Wei-Shaw/sub2api/blob/v0.2.18/backend/internal/pkg/logger/options.go#L106-L115) | Version output uses the console bootstrap logger. |
| [Official release](https://github.com/Wei-Shaw/sub2api/releases/tag/v0.2.18) | Published on 2026-10-23. Includes the tested Darwin/arm64 executable archive. |

The Dockerfile copies backend source without the repository's Git metadata.
Its resolver can therefore reach the stale VERSION file when no explicit version reaches the build.
The common build must inject its selected version explicitly instead of relying on this resolver.

## Original Installer Defects

The source checkout is `/Users/minami/Code/C/cpa-plugin-codex-candy-eval`.

- `scripts/installer/main.go:34` searches for `0.2.16` or `0.2.17` anywhere in the output.
- `scripts/installer/main.go:35` searches for `0.2.17` anywhere in the candidate output.
- `scripts/installer/main.go:61` captures both streams but returns only stdout on success.
- `scripts/installer/main.go:399` and `:420` run the candidate and installed executable with `-version`.
- `tests/installer/installer_test.go:145` supplies simplified `Sub2API <version>` output without actual logger fields.

The existing candidate expression, `\b0\.2\.17\b`, accepts each of these incorrect inputs:

```text
Sub2API 0.2.17-rc.1 (commit: unknown, built: unknown)
Sub2API 0.2.18 (commit: 0.2.17, built: unknown)
Sub2API 0.2.17.1 (commit: unknown, built: unknown)
```

An in-memory expression check reproduced all three false matches.
Changing only `17` to `18` retains these defects.

## Observed Release Output

Downloaded the official `sub2api_0.2.18_darwin_arm64.tar.gz` archive into a temporary research directory.
Extracted only `sub2api` and executed it with `-version`, with a 15-second timeout.
The command returned exit status zero without starting the server.
The complete output was on stdout. Stderr was empty.

The stdout record below uses `<TAB>` to show tab separators:

```text
2026-10-24T03:43:48.337+0800<TAB>INFO<TAB>stdlog<TAB>Sub2API 0.2.18 (commit: ac1b8f1271be0d674fa6f074403c1410f30a3a81, built: 2026-10-23T07:37:15Z)<TAB>{"service": "sub2api", "env": "bootstrap", "legacy_stdlog": true}
```

Research files remain under `/tmp/sub2api-version-research.3zhLIG/`.
This observation covers the official Darwin/arm64 executable.
The future Linux/amd64 installer still needs its container command and transaction tests.

## Detection Contract

1. Derive canonical `0.2.18` once from the selected `v0.2.18` build tag.
2. Inject that version into the server and installer from the same build value.
3. Run `/app/sub2api -version` inside the selected container, using its immutable container ID.
4. Run the staged candidate with `-version` inside that same container.
5. Capture stdout, stderr, and command status separately with a bounded command timeout.
6. If either command fails or times out, report an unresolved probe instead of trusting any matching text.
7. Decode the observed console record and extract its message field.
8. Also support the exact bare message and standard Go timestamp prefix for standard-log fallback output.
9. Require the complete message form `Sub2API <version> (commit: <commit>, built: <date>)`.
10. Resolve consistent version records across both streams. Repeated identical versions are valid. Conflicting versions produce an unresolved warning.
11. Remove only the optional leading `v` from its complete version token.
12. Compare that token with the canonical build version using exact equality.

Keep prerelease and build suffixes. Neither `0.2.18-rc.1` nor `0.2.18+custom` equals the selected stable target.
Do not extract versions from commit fields, build dates, arbitrary log text, or image metadata.
Do not require the installed and candidate commit fields to match. Plugin builds can have different source revisions.

Use a dedicated version-command result instead of changing the generic Docker helper to combine stdout and stderr.
Combining streams in the generic helper could corrupt Docker inspect JSON with warning text.
Collect both probe results before deciding whether to show a combined version warning.
Preserve candidate cleanup after probing and on cancellation.

A binary that literally reports `latest`, `dev`, or an unreadable version has an unresolved application version.
Report that state separately from a confirmed version mismatch.
Show the build version, both probe results, and any command errors in the warning.
Do not invent an application version from a tag or label to suppress a warning.

## Warning and Confirmation

When either version differs or remains unresolved, show the build version, both probe results, and the reasons.
Ask `Continue installation? [y/N]` once, before backup, executable replacement, or restart.
Continue only after `y` or `yes`, ignoring input case and surrounding whitespace.
Empty input, refusal, EOF, or interruption cancels installation.
Matching versions need no version warning or extra confirmation.

A version command failure or timeout produces a warning that the user can explicitly accept.
An interrupted installation stops immediately and cannot become a warning that permits continuation.
ELF checks and failures in staging, backup, replacement, readiness, or restoration keep their existing behavior.

## Historical Format Probe

An in-memory Python format probe checked the observed console record and 14 synthetic cases.
All 15 classifications matched the explicit expected outcomes.
These results record the earlier format experiment. They do not define a mandatory production test matrix.

| Input or condition | Detection result | Research evidence |
| --- | --- | --- |
| Observed official console record on stdout | Accept `0.2.18` | Observed executable and format probe |
| Successful command reports `v0.2.18` on stderr | Accept canonical `0.2.18` | Format probe |
| Standard Go timestamp prefix on stderr | Extract the complete version record | Format probe |
| Installed version `0.2.17` or `0.2.19` | Mismatch warning | Format probe |
| Version `0.2.180` | Mismatch warning | Format probe |
| Version `0.2.18-rc.1` or `0.2.18+custom` | Mismatch warning | Format probe |
| Version `0.2.18.1` | Unresolved version warning | Format probe |
| Version `0.2.17`, commit field contains `0.2.18` | Mismatch warning | Format probe |
| Unrelated log contains `Sub2API 0.2.18` | Missing version record warning | Format probe |
| Executable reports `latest` | Unresolved application version warning | Format probe |
| Empty output | Missing version record warning | Format probe |
| Multiple version records | Ambiguous under the earlier single-record rule | Format probe |
| Nonzero exit with matching output | Command failure warning | Format probe |
| Command timeout | Unresolved probe warning | Source-derived behavior, not exercised by the format probe |
| Image reference uses `latest` or a digest, executable reports `0.2.18` | Accept | Source-derived behavior, not exercised by the format probe |
| Image reference or label says `0.2.18`, executable reports another version | Mismatch warning | Source-derived behavior, not exercised by the format probe |

The current contract accepts repeated records when their versions agree. Only conflicting records require an ambiguity warning.

## Focused Implementation Checks

Use the observed record in the shared parser tests. Cover distinct parsing and command behavior once.
Test the shared confirmation function separately from version parsing.
Use installer fake-Docker fixtures for matching versions and one combined warning with continuation and cancellation outcomes.
Reuse transaction coverage for backup, replacement, readiness, restoration, and candidate cleanup.
Do not multiply parser cases by both probe positions and every confirmation input.
The [implementation plan](../implement.md) defines the test scope.
