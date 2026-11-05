# Installation implementation

## Candidate

The four kits share the installer, builder, common tests, and artifact workflow.
Root and template READMEs describe platform selection and the three installation flows.

The installer separates terminal presentation, executable inspection, native replacement, Apple operations, and platform-specific process and file operations.
Native restoration retains manual startup ownership or uses the existing `sub2api.service`.
Windows replacement preserves owner, group, and the discretionary access-control list through the Windows file APIs.
Apple restoration starts the same stopped application container before copying the retained host backup.
The installer does not change the Apple image marker or other application containers.

The builder prepares source and frontend once. It compiles five native programs and five host installers.
Each installer embeds its native program and the matching Linux container program.
PTerm v0.12.84 and original dependency license files enter the temporary installer module.

The CI keeps exact Action tags and one build entry. It uploads ten versioned executable files directly without tar packaging.
The current filenames and validation evidence are in [direct artifacts](direct-artifacts.md).
Failure diagnostics retain one build log. Summaries report status and diagnostic locations without copying the log body.

## Source confirmation

Apple 1.1.0 `ContainerInspect.swift` emits `ManagedContainer` objects.
`ManagedContainer.swift` serializes `id`, `configuration`, and `status`.
`ContainerConfiguration.swift` supplies process environment and published ports.
`ContainerStatus.swift` supplies runtime state and network attachments.
The implementation reads that shape rather than assuming Docker inspect fields.
Containerization 0.35.0 encodes `IPAddress` and `CIDRv4` as strings.
This confirms the published-port host address and network CIDR decoding.

Sources:

- [Inspect command](https://github.com/apple/container/blob/1.1.0/Sources/ContainerCommands/Container/ContainerInspect.swift)
- [Managed container](https://github.com/apple/container/blob/1.1.0/Sources/ContainerResource/Container/ManagedContainer.swift)
- [Configuration](https://github.com/apple/container/blob/1.1.0/Sources/ContainerResource/Container/ContainerConfiguration.swift)
- [Status](https://github.com/apple/container/blob/1.1.0/Sources/ContainerResource/Container/ContainerStatus.swift)
- [IP address encoding](https://github.com/apple/containerization/blob/0.35.0/Sources/ContainerizationExtras/IPAddress.swift)
- [CIDR encoding](https://github.com/apple/containerization/blob/0.35.0/Sources/ContainerizationExtras/CIDRv4.swift)

## Checks

- The existing builder suite passed its four cases, including automatic composition and failure preservation.
- Focused installer checks passed Docker transactions, native manual/systemd behavior, cancellation recovery, Apple restoration, and locale/plain-stream behavior.
- The temporary installer module compiled for Darwin/arm64 and Windows/amd64.
- A real PTY showed the Chinese installation menu, arrow selection, native path input, and Ctrl-C cancellation with terminal cleanup.
- The final default combined build exited successfully. Its log is `/tmp/sub2api-installation-build.log`.

The first development harness lacked a Linux/arm64 embedded fixture. Its entry test correctly failed before installation.
The final build supplied the actual platform programs before the complete common test run.
The default Go proxy reset the local connection. The build process uses `GOPROXY=https://goproxy.cn` with no product fallback.

## Final evidence and outputs

The default combined build passed frontend compilation, plugin checks, focused vet, and common tests.
The common builder suite passed four cases. The complete installer suite passed in 48.35 seconds.
The build produced five server programs and five installers.
`file` identified the expected ELF, Mach-O, and PE architectures.
The Darwin/arm64 server's actual `-version` output reported `0.2.19`.

The final Darwin/arm64 installer ran in a real PTY with Chinese locale and the existing fake-Docker helper.
It showed the installation menu, selected container, program path, and a changing spinner with elapsed time.
The spinner stopped before the localized version warning and confirmation.
Ctrl-C returned exit status 1 and restored terminal cursor visibility.
The fixture retained the original program, with zero restarts and no backup or replacement.
An earlier PTY check exercised arrow selection and native path input.
The final installer also used English numbered prompts with redirected streams and `LC_ALL=C`.
That output contained no cursor escapes. Blank version confirmation canceled before replacement.

Before the direct-artifact change, the CI's exact packaging shell processed completed outputs under `/tmp/sub2api-installation-dev/ci-check`.
Each of its five tar archives contained the matching two nonempty executable files.
The local macOS check used `COPYFILE_DISABLE=1` to omit AppleDouble metadata that the Ubuntu workflow does not create.
The first local archive assertion exposed those macOS metadata entries. No workflow change was necessary.

Program and installer pairs are under `dist/build/<os>-<arch>/`.
Platforms are `linux-amd64`, `linux-arm64`, `darwin-amd64`, `darwin-arm64`, and `windows-amd64`.
Current filenames use `sub2api-plugins-[installer-]<upstream-tag>-<os>-<arch>`, with `.exe` on Windows.

No remote GitHub Actions job ran. The initial recovery checks used local fixtures.
Later real Docker product checks and the readiness repair are recorded in [spinner and Docker checks](spinner-docker-check.md).
Cross-compilation does not establish actual installation on another operating system.

## Independent review corrections

The reviewer identified a partial-copy risk in cross-filesystem output publication.
The builder now completes its copy inside `dist` before it moves the existing output directory.
Same-filesystem rename publishes the complete candidate or restores the original directory at its original path.
If restoration also fails, the builder retains the previous directory and reports its location.
The existing failure-preservation case passed after adding partial-copy and publication-rename failures.
The focused command was `python3 tests/test_build.py BuildTests.test_failures_stop_publication`.
It completed successfully in 4.54 seconds.

The reviewer also found one untranslated installer-owned format error reason.
The message catalog now translates that reason while retaining actual operating-system and executable-parser diagnostics.
The combined build copied the corrected Go source before installer compilation.
Its Python process loaded the earlier publication function.
After the build passed, the finished outputs passed through the corrected `publish_outputs(output, output)` function without recompilation.
This published the complete actual output set successfully at its original path.
