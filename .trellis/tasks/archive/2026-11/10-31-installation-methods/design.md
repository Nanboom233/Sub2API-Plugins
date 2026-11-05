# Three official installation forms

## Entry and shared behavior

Retain the self-contained Go installer and existing standard-library installation operations.
Offer installation choices for Docker/Compose, native executable, and Apple container where the platform supports them.
Show the chosen target and program path before replacement.
Do not add a plugin registry, deployment manifest, installer configuration file, or separate command entry.

Share version parsing and warnings, backup reporting, replacement errors, HTTP readiness, cancellation, and restoration results.
Version mismatch or unreadable output remains a warning with explicit continuation. Executable format and architecture must match the runtime.
Use Go's `debug/elf`, `debug/macho`, and `debug/pe` readers for the supported formats.
Run program version probes in the target environment. Do not execute a Linux container payload on the Darwin host.

Reuse direct `/health` and `/setup/status` readiness checks and their current timeout behavior.
Native mode asks for the local application address, defaulting to `127.0.0.1:8080`.
This avoids changing or guessing private configuration and handles non-default ports.
Container modes derive the address from their runtime's current port or network information.

## Terminal presentation and localization

Use the same three installation flows with a redesigned terminal presentation.
Use `github.com/pterm/pterm v0.12.84` for inline choices, text input, confirmations, and spinner timing.
The selected stable release uses Go 1.26.0 and supports CJK display width and Windows terminal handling.
Use its existing terminal dependency `golang.org/x/term` for capability detection. Do not add another CLI or logging framework.
The source comparison and integration limits are recorded in [terminal UI research](research/terminal-ui.md).

The initial view shows the installer version and available installation forms in the language selected from the terminal locale.
After target selection, keep the installation form, selected target, and program path visible above progress.
Use short stage names for program checks, backup, replacement, restart or user startup, and readiness.

Use an inline terminal layout. Keep the normal scrollback available for backup paths and final diagnostics.
The entry menu offers only the available installation forms. Language selection is automatic and has no menu or switch.
Confirming the installation form or target uses the existing selection step, not an extra installation-approval screen.

| View | Content | User action |
| --- | --- | --- |
| Installation choice | Version and available forms in the selected language | Choose an installation form |
| Target choice | Container name and short ID, or program path and native address | Select the target or enter its location |
| Version warning, when needed | Build, installed and candidate versions with unresolved errors | Explicitly continue or cancel, defaulting to cancellation |
| Installation progress | Target context, completed steps, current action, elapsed wait | Wait, or respond when a manual step needs input |
| Manual stop/start | Required user action and target path | Confirm after completing the original launch method's action |
| Final result | Installed, original restored, or recovery incomplete, plus backup location and actual error | Read the result and use the retained backup when needed |

Manual stop/start confirmations advance the existing transaction. They do not imply successful HTTP readiness.
Do not add installation options or a persistent settings screen solely for the presentation redesign.

Enable dynamic UI only for actual terminal stdin/stdout with supported terminal capabilities and `TERM` other than `dumb`.
Redirected streams and injected test readers/writers use plain mode.
PTerm output configuration alone cannot redirect every interactive cursor operation. Keep dynamic use on its supported process terminal streams.
In dynamic mode, allow keyboard selection and update the active step in place.
Keep the numbered choice mapping available. A selection is not accepted until the user confirms it.
Show a spinner and elapsed time while waiting for unknown-duration operations.
Use measured progress only where the operation supplies it. Do not invent overall completion percentages.
Pause dynamic rendering for version decisions and manual stop/start prompts so user input remains visible.
Use `SpinnerPrinter.WithShowTimer(true)` and `UpdateText` rather than writing another animation timer.
Stop the spinner and wait for rendering to finish before prompts, external command details, or the final result.

When streams are redirected or the terminal cannot support dynamic rendering, use the existing numbered text interaction and sequential status lines.
Do not emit cursor movement, animation frames, or layout control sequences into plain logs.
Treat color and animation as presentation capabilities rather than requirements for installation.
Keep successful completion, actual failure, recovery outcome, and backup path in the final readable output.
Render captured command failure detail through its existing single error owner.
Terminal cancellation restores the terminal and preserves the installation flow's recovery behavior.
After replacement has begun, cancellation uses the existing recovery path rather than exiting directly from a UI component.
During restoration, show its current step and retain the same final error owner for the original failure and recovery outcome.
Set `WithOnInterruptFunc` for every selected PTerm prompt. Its default Ctrl-C handler exits the process and cannot own cancellation here.
The callback cancels the operation context. After `Show` returns, check context cancellation before accepting any returned default choice or input.
Keep terminal setup errors readable without printing the same library diagnostic again at the top level.

Cancellation before application or startup mutation removes the staged candidate without restarting or restoring an unchanged installation.
Once program replacement or a managed stop begins, restore the original program and startup state before checking readiness.
Use the existing separate restoration context so the canceled operation cannot cancel recovery commands.
Manual recovery prompts use that restoration context, rather than the canceled installation context.
If user input is unavailable, retain the backup and report the pending manual recovery action instead of claiming restoration success.

Keep installer-owned Simplified Chinese and English messages in one small Go message catalog in `scripts/installer/`.
Resolve language once from the terminal environment, using the first non-empty value among `LC_ALL`, `LC_MESSAGES`, and `LANG`.
Normalize locale case and accept underscore or hyphen separators and encoding suffixes when recognizing Chinese locales.
Chinese locales select Simplified Chinese. Other, absent, `C`, and `POSIX` locales select English.
An explicit higher-priority locale wins even when a lower-priority variable names Chinese.
Do not query the operating system's UI language or introduce another locale dependency, prompt, configuration file, or language argument.
Localize menus, prompts, validation explanations, stage names, version warnings, manual actions, and installation/recovery results.
Commands, identifiers, executable versions, paths, and external process output remain literal data.
Share operation results between localized and plain/dynamic presentation without adding another installation state machine or output protocol.
Keep language and rendering choice separate from target and transaction decisions.
Messages receive values through normal Go formatting. The small catalog does not need external translation files or a localization framework.

The following is an illustrative Chinese progress view. Its elapsed value changes while readiness runs.

```text
Sub2API Plugins v0.2.19

安装方式  Docker / Compose
目标      sub2api-main
程序      /app/sub2api

[完成] 检查程序
[完成] 备份原程序
[完成] 替换程序
[完成] 重启应用
[等待] 服务就绪  12s / 120s

备份  /tmp/.../sub2api
```

Use the same stage meaning in plain mode, printed sequentially without redraw control sequences.
When readiness fails, replace the active stage with the actual failure and show restoration progress below it.
The final result retains the original failure, restoration result, and backup path without repeating raw command output.

## Docker and Compose

1. List running containers, preferring names that include `sub2api`. Let the user explicitly select the numbered target.
2. Check the installed `/app/sub2api` program's format, architecture, and version.
3. Copy the candidate to its container staging path, set executable access, and probe its version.
4. Apply the shared version-warning decision before backup or replacement.
5. Back up the original program on the host and print its path.
6. Rename the staged program over `/app/sub2api`, preserving executable access and process ownership.
7. Restart the selected container by ID.
8. Verify health and completed setup, then report installation success and the backup path.

After replacement, restart, or readiness fails, restore the original program, restart the same container, and verify recovery.
If recovery fails, retain the backup and report the actual error.
Preserve the current cancellation and stopped-container restoration behavior.
Do not recreate the container or change its image, Compose definition, data mounts, or restart policy.
Same-container restart retains the writable-layer program. Recreation from the original image requires reinstallation.

## Native executable

1. Ask for the program path, proposing `/opt/sub2api/sub2api` for the official Linux installation.
2. Resolve symbolic links to identify the file to replace.
3. Ask for the application address, defaulting to `127.0.0.1:8080`.
4. Check installed and candidate format, architecture, and version. Apply the shared version-warning decision.
5. Stage the candidate on the executable's filesystem and preserve permissions and ownership.
6. Back up the original program and print its path.
7. Complete replacement and readiness through the actual startup owner below.

| Startup owner | Installation | Recovery after replacement or readiness failure |
| --- | --- | --- |
| Official Linux systemd service | Stop the existing service, replace its program, start that service, and check readiness | Stop the candidate service, restore the backup, start the original service, and check readiness |
| Manual process | Ask the user to stop through the original launcher and confirm. Replace the file. Ask for original-method startup and confirmation, then check readiness | Ask the user to stop the candidate. Restore the backup. Ask for original-method startup and confirmation, then check readiness |

Read the effective service's program and working directory when resolving a systemd-managed target.
Do not create or change service units. Preserve the original environment, arguments, user, and working directory.
Manual stop/start also applies to native macOS and Windows. Retain the backup if interaction or restoration cannot complete.
Report completed replacement separately from verified readiness. Preserve configuration and application data.
Native process or host restart retains the installed file. Upstream updates or another file replacement can overwrite it.

## Apple container

1. Run the Darwin/arm64 installer and select Apple container.
2. List application containers and let the user explicitly select the numbered target.
3. Select the Linux/arm64 payload for `/app/storage/runtime/sub2api`.
4. Stage it in the running container, preserve ownership and executable access, and probe installed and candidate versions.
5. Apply the shared version-warning decision.
6. Back up the original program on the host and print its path.
7. Rename the candidate over the runtime program without changing `/app/storage/runtime/base-image-id`.
8. Stop and start only the selected application container. Keep PostgreSQL and Redis running.
9. Check health and completed setup, then report installation success.

Failed candidate children retain the official supervisor. Restore the backup through that running environment, then restart the application container and check recovery.
Apple copy requires a running container. If it is stopped, start the same container before restoring its runtime file.
If the runtime cannot start or restoration fails, retain the backup and report incomplete recovery.
Normal official recreation retains the runtime file while the base-image ID is unchanged.
A changed image ID resets the runtime program and requires reinstallation. Data-only backups omit the runtime program.

## Platform outputs

Build the five native application targets published by upstream v0.2.19.
Build one installer for each corresponding host target. Embed the host's native application and its matching Linux application when they differ.

| Installer host | Native program | Additional container program |
| --- | --- | --- |
| Linux/amd64 | Linux/amd64 | Reuse native payload |
| Linux/arm64 | Linux/arm64 | Reuse native payload |
| Darwin/amd64 | Darwin/amd64 | Linux/amd64 for Docker |
| Darwin/arm64 | Darwin/arm64 | Linux/arm64 for Docker and Apple container |
| Windows/amd64 | Windows/amd64 | Linux/amd64 for Docker |

Choose a packaged payload that matches the selected runtime. Do not silently use an incompatible host program.
The installer remains self-contained and needs no program download during installation.

Use `dist/build/<os>-<arch>/sub2api-plugins-<upstream-tag>-<os>-<arch>` for raw native programs.
Installers use `sub2api-plugins-installer-<upstream-tag>-<os>-<arch>` in the same directory. Windows names add `.exe`.
Use the selected tag, including `v`, for names and its canonical version for application metadata.
Do not publish duplicate compatibility copies at former paths.
The application in each directory is that platform's native program. The installer also carries its required container payload.
Upload all ten executables individually with `archive: false`. Do not create tar archives.
Each Actions artifact uses the file basename, for example `sub2api-plugins-installer-v0.2.19-linux-amd64`.
Validate every expected file before upload. Unix users set executable permission after download.

## Build and CI integration

Keep `python3 scripts/build.py` as the only local and CI entry, without command-line arguments.
Manual Actions runs require `upstream_tag`, passed through `UPSTREAM_TAG` without direct shell interpolation.
Push and pull-request builds resolve `tag_name` from the latest official upstream release through its public API.
Local builds without an explicit tag use the same resolver. No personal or Actions token is needed.
Resolve the tag once before source preparation, then reuse it for source, metadata, tests, filenames, and CI upload paths.
Lookup failure stops the build and preserves previous outputs. Do not substitute a hardcoded version or the literal string `latest`.
Download source, compose patches, install dependencies, build the frontend, and execute existing host checks once.
Compile the five application targets from that prepared source, then package and compile their installers.
Publish the new output set only after required work succeeds. Preserve previous outputs after failures.
Do not repeat plugin tests or common installer tests for every cross-compiled target.

Keep equivalent code and workflows aligned in the parent, eval, quota, and template.
Prepare selected terminal dependencies in the existing temporary installer module before compilation, keeping normal dependency resolution separate from user installation.
Use the verified PTerm version and normal module sums. Preserve its original MIT terms through the existing license resource layout.
The installer host still needs no Go runtime, terminal package installation, or network download.
Use the existing Ubuntu CI job for cross-compilation and direct executable upload.
Keep exact Action version tags, read-only permissions, failure logs, concise summaries, and artifact-only publication.
No new Release, container image publication, remote build provider, or runtime test matrix is proposed.

## Acceptance evidence

Use the focused verification in [implement.md](implement.md#verification).
