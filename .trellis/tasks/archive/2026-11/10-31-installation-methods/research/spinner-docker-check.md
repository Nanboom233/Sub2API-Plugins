# Spinner correction and Docker checks

## Root cause

The user reported repeated readiness lines and clipped elapsed times on 2026-11-05.
The previous narrow-terminal check covered selection and short operations. It did not cover a long readiness wait.

PTerm v0.12.84 `SpinnerPrinter.runAnimation` writes each frame through `Fprinto`.
`Fprinto` prefixes a carriage return. It does not track terminal wrapping or clear previous wrapped rows.
The installer replaced the short spinner stage with a long readiness message containing state, address, and a sampled elapsed time.
PTerm appended its own elapsed timer to that same frame.
Automatic wrapping therefore left rows behind, and the two elapsed values advanced differently.

A real 40-column PTY reproduced the report during an 11.2-second readiness wait.
The terminal screen retained 113 readiness rows.

Sources read:

- [PTerm spinner](https://github.com/pterm/pterm/blob/v0.12.84/spinner_printer.go)
- [PTerm output](https://github.com/pterm/pterm/blob/v0.12.84/print.go)
- [PTerm area](https://github.com/pterm/pterm/blob/v0.12.84/area_printer.go)
- [PTerm wrapping](https://github.com/pterm/pterm/blob/v0.12.84/internal/wrap_text.go)
- [Cursor area](https://github.com/atomicgo/cursor/blob/v0.2.0/area.go)

## Correction

All four `scripts/installer/ui.go` copies use the same correction.
The spinner retains a short translated stage and PTerm's elapsed timer.
Plain output retains the sampled state, restart count, address, elapsed time, and deadline.

A small writer sends complete spinner frames to PTerm's existing `AreaPrinter`.
PTerm owns wrapping, CJK display width, cursor movement, and removal of previous rows.
The adapter does not calculate width or emit terminal commands.
Stopping first joins the spinner, then stops the area, and finally prints the line break.
Prompts and final diagnostics keep their existing error owner.

## Terminal evidence

The final Darwin/arm64 installer contains the actual combined server payloads.
The PTY harness uses the existing fake-Docker test executable and an HTTP fixture that delays readiness for 11 seconds.
The saved screen includes terminal scrollback, rather than only the last visible frame.

| Terminal | Result |
| --- | --- |
| Previous English, 40 columns | 113 retained readiness rows after 11.2 seconds |
| Corrected English, 40 columns | One readiness row after 11.6 seconds, with one elapsed timer |
| Corrected English, 24 columns | One logical area across two rows, exit status 0 after 11.2 seconds |
| Corrected Chinese, 24 columns | One readiness row, exit status 0 after 11.2 seconds |

Raw captures and decoded terminal screens are under `/tmp/sub2api-spinner-check/`.
Files use the prefixes `before-en`, `fixed-en`, `fixed-en24`, and `fixed-zh24`.
The last rebuilt production installer repeated the 24-column English check as `final-en24`, with exit status 0 and one logical area.
The screen decoder uses Pyte. It is a temporary verification tool, not an installer dependency.

The first capture harness did not stop on an empty PTY read after program exit.
That harness timeout preserved the complete successful output. The harness now handles empty reads.

Reproduction commands:

```sh
uv run --no-project --with pyte python /tmp/sub2api-spinner-check/pty_readiness.py C 40 fixed-en
uv run --no-project --with pyte python /tmp/sub2api-spinner-check/pty_readiness.py C 24 fixed-en24
uv run --no-project --with pyte python /tmp/sub2api-spinner-check/pty_readiness.py zh_CN.UTF-8 24 fixed-zh24
```

## Docker package inventory

Docker Desktop reported Engine 29.8.2 on Linux/arm64.
Native arm64 and emulated amd64 Alpine programs both executed successfully.
Only containers and a network created for this check were changed.

| Kit source and license resources | Linux arm64 fixture installer | Linux amd64 fixture installer |
| --- | --- | --- |
| Parent repository | Passed | Passed through Docker emulation |
| `plugins/codex-candy-eval` | Passed | Passed through Docker emulation |
| `plugins/sub2api-quota-extension` | Passed | Passed through Docker emulation |
| `plugins/sub2api-plugin-template` | Passed | Passed through Docker emulation |

Each package compiled from that kit's installer source and carried that kit's license resources.
These eight integration packages embedded small Go fixture programs, not standalone plugin business builds.
The original and candidate report v0.2.19. The candidate delays healthy readiness for 12 seconds and exposes its identity.

Every package performed actual Docker copy, staged replacement, container restart, and HTTP health/setup checks.
The test then restarted the same container again and confirmed candidate identity.
Container ID and restart policy stayed unchanged.

A separate failing candidate exited with status 7.
The installer restored through Docker copy while the container was stopped, started the original, and verified readiness.
A later restart still served the original fixture program.

Commands and fixture sources:

```sh
python3 /tmp/sub2api-spinner-check/build_installers.py
python3 /tmp/sub2api-spinner-check/prepare_checks.py
python3 /tmp/sub2api-spinner-check/docker_installers.py
```

Run build and preparation serially. They use generated temporary modules and fixture payloads.
The integration log is `/tmp/sub2api-spinner-check/docker-installers.log`.
Per-package install logs use `<kit>-<arch>-install.log` in the same directory.

## Actual combined payload

The actual product checks used the existing combined `dist/build/linux-*/sub2api-plugins` programs and rebuilt installers.
They used independent PostgreSQL 15 and Redis 7 containers with synthetic local settings and data.

Both Linux/arm64 and emulated Linux/amd64 passed:

1. Start the actual combined server.
2. Read actual `-version` output and confirm v0.2.19.
3. Serve the combined `/codex-eval` page.
4. Run the matching actual installer against that container.
5. Pass `/health` and completed `/setup/status`.
6. Restart the same container and verify readiness and the plugin page again.

The first isolated application fixture omitted `/app/data`. Auto setup failed while writing its configuration.
The test fixture now creates that directory. No product change was needed for that failure.

```sh
python3 /tmp/sub2api-spinner-check/product_smoke.py
```

The result log is `/tmp/sub2api-spinner-check/product-smoke.log`.
Individual logs are `product-arm64.log` and `product-amd64.log`.
These are combined-product runtime checks. They do not establish standalone eval-only or quota-only business payload results.
Both actual product checks passed again after the final dedicated production rebuild.

## Native and common installer checks

The complete shared installer suite passed inside the Linux/arm64 Go container in 5.555 seconds.
The same suite passed as an amd64 executable under Docker emulation.
The four source copies are aligned. Shared test evidence applies to their identical installer implementation.
The eight separately compiled integration packages above check their actual package entry and resources.

The suite includes version parsing, explicit continuation, Docker transactions, recovery, cancellation, and native manual/systemd branches.
It also covers Apple command adaptation and its running-container restoration rule, locale selection, plain streams, and embedded resources.
Systemd and Apple cases use command fixtures. They are not runtime tests of those service managers.

```sh
docker exec -e SUB2API_BUILD_VERSION=0.2.19 -w /work/eval/installer spinner-kit-runner-20261105 go test -mod=vendor -tags=unit -failfast .
docker exec -e SUB2API_BUILD_VERSION=0.2.19 -e GOOS=linux -e GOARCH=amd64 -e CGO_ENABLED=0 -w /work/eval/installer spinner-kit-runner-20261105 go test -mod=vendor -tags=unit -c -o /work/installer-tests-amd64
docker exec -w /work/eval/installer -e SUB2API_BUILD_VERSION=0.2.19 spinner-kit-runner-20261105 /work/installer-tests-amd64 -test.failfast
```

The initial amd64 test invocation used `/` as its working directory and could not find license files.
The corrected invocation uses its module directory. The suite then passed.

A separate native manual installation controlled real fixture processes inside the isolated Linux container.
The harness stopped and started the application when the installer requested user action.
Delayed readiness, the retained original backup, and executable mode `0750` all passed.

```sh
docker exec spinner-kit-runner-20261105 python3 /work/native_manual.py
```

## Rebuilt outputs and limits

The server programs did not change. The five actual combined installers were rebuilt from their retained actual server programs.
A dedicated temporary module kept production payload staging separate from fixture staging.
The rebuilt outputs remain under `dist/build/<os>-<arch>/`.

```sh
python3 /tmp/sub2api-spinner-check/rebuild_product_installers.py
```

The build log is `/tmp/sub2api-spinner-check/product-rebuild.log`.
All five compilation commands completed successfully. `file` identified the expected ELF, Mach-O, and PE architectures.
The final shared builder, terminal source, workflow, and installer test copies remained aligned across all four kits.
CI workflow and artifact auditing remain with the parent task owner.
No remote workflow, credential operation, commit, or push ran here.
Docker does not execute Darwin or Windows installers. No actual Apple container runtime or systemd service was available for this check.

## Resource cleanup

The check created one runner, eight package targets, one recovery target, two product targets, PostgreSQL, Redis, and one network.
The test removed only those named resources, including their anonymous fixture volumes.
Existing `i022pg`, `i010pg`, and `i018linux` containers remained running.
Host evidence and generated verification tools remain under `/tmp/sub2api-spinner-check/`.
