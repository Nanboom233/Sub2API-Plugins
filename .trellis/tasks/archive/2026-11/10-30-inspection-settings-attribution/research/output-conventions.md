# Research: Unified Build and Installer Output

- Query: Which mature open-source output patterns should this repository use to simplify progress, keep one owner for each error, separate stdout from diagnostics, and avoid redundant CI logs?
- Scope: mixed internal and external
- Date: 2026-10-31

## Findings

### 1. Mature tools assign one owner to each error

GitHub CLI disables Cobra's automatic error and usage output in its root command.
`pkg/cmd/root/root.go` sets `SilenceErrors` and `SilenceUsage`.
`internal/ghcmd/cmd.go` executes the command and prints ordinary errors once through `printError` on `ioStreams.ErrOut`.
The command can return `cmdutil.SilentError` when it already printed a user-facing error.
This keeps the exit code while preventing a second top-level message.

Relevant sources. The GitHub CLI raw files use the moving `trunk` branch and were read on 2026-10-31:

- [GitHub CLI command entry](https://raw.githubusercontent.com/cli/cli/trunk/internal/ghcmd/cmd.go)
- [GitHub CLI root command](https://raw.githubusercontent.com/cli/cli/trunk/pkg/cmd/root/root.go)
- [GitHub CLI command error sentinels](https://pkg.go.dev/github.com/cli/cli/v2@v2.102.1/pkg/cmdutil)

Adopt this behavior without adding Cobra. Keep one error owner in the existing Go installer.
The helper should either stream a non-quiet command's output and return a short contextual error, or capture output and let the caller print it.
It should not do both for the same failed command.

### 2. Mature Python subprocess wrappers avoid replaying visible output

pip's `call_subprocess()` in `src/pip/_internal/utils/subprocess.py` combines child stderr and stdout for its normal mode.
It logs each line as it arrives.
When the child fails, `InstallationSubprocessError` includes captured output only when the output was not already visible at the active log level.
The wrapper keeps the command description and exit code in the final error.
It also redacts `HiddenText` arguments before it displays a command.

Relevant sources. The pip raw file uses the moving `main` branch and was read on 2026-10-31:

- [pip subprocess helper](https://raw.githubusercontent.com/pypa/pip/main/src/pip/_internal/utils/subprocess.py)
- [pip duplicate-output regression](https://github.com/pypa/pip/issues/3521)

This repository already inherits child output through `subprocess.run()` in `scripts/build.py:22-24`.
Its top-level `Build failed` line adds only a stable failure category and does not replay child output.
Keep that separation.
Remove the second patch progress line at `scripts/build.py:50` or make the command runner own that progress line.
The current `Apply ...` line followed by `+ git apply ...` describes one patch twice.
Do not add a logging framework, verbosity flag, or second command runner.

### 3. GitHub Actions separates raw logs, artifacts, and summaries

GitHub records each step's stdout and stderr in the workflow log.
The official Actions context example writes a failure log under `${{ runner.temp }}` and uploads it only when the job fails.
The official workflow-command documentation describes job summaries as unique content that helps a reader avoid opening raw logs.
It does not require copying a tail of the raw log into the summary.

Relevant sources:

- [GitHub workflow commands and job summaries](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands)
- [GitHub Actions contexts log-artifact example](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts)
- [GitHub Actions workflow logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/using-workflow-run-logs)

Current copies of `.github/workflows/build.yml` in the parent, eval, quota, and template use `tee dist/build.log` at lines 33-39.
They upload `build.log` only when the build step fails at lines 69-75.
They also copy the last 40 lines into the job summary at lines 76-89.
The artifact and raw step log have different uses, but the summary tail repeats raw output.

Preferred CI shape:

1. Keep the native step log as the complete live record.
2. Keep the failure-only `build-log` artifact because R14 requires a downloadable diagnostic.
3. Keep the summary for status, failed step, output paths, and diagnostic artifact location.
4. Remove the summary `tail -n 40` block.

This is a simplification choice for this repository. The official documentation recommends useful unique summary content, but it does not prohibit a log tail.
Package and upload failures should keep their step errors and one summary sentence.
They should not upload the build log because the build step did not fail.

### 4. Docker CLI captures stderr only when it must return it

Docker CLI's `cli/connhelper/commandconn/commandconn.go` captures bounded stderr for helper commands.
It adds captured stderr to the returned error when the command exits unexpectedly.
The helper does not also stream the same captured stderr to the user in that path.
The Docker top-level command path owns final error formatting on its error stream.

Relevant sources:

- [Docker CLI command connection helper](https://raw.githubusercontent.com/docker/cli/master/cli/connhelper/commandconn/commandconn.go)
- [Docker CLI root error path](https://github.com/docker/cli/blob/master/cmd/docker/docker.go)

The source is a related subprocess pattern, not a drop-in replacement for this installer.
The installer needs command output for non-quiet copy, restart, and rollback commands.
Current `docker()` runs the command, stores stdout and stderr in buffers, and forwards those buffers after `cmd.Run()` when `quiet=false`.
The preferred local adaptation is simpler: forward buffered stdout and stderr only after a successful non-quiet command.
On failure, return the captured detail and let the existing final error owner print it once.
This keeps the command context and rollback result while avoiding a direct print plus a final error copy.
It does not claim real-time output because the current helper already waits for `cmd.Run()`.
For `quiet=true`, keep the captured detail in the returned error because no output is forwarded.

The Docker raw source uses the moving `master` branch and was read on 2026-10-31.

### 5. Default quota console output is separate from duplicate installer output

The quota patch still calls `console.error('Failed to load usage:', e)` in `plugins/sub2api-quota-extension/patches/quota-extension.patch:1154-1159`.
The current account usage page does not render this catch value as a detailed default error.
The console entry is extra developer-console output, not a second user-facing page message.
This review does not recommend changing other native account catches as part of this output consolidation.

## Internal Files Found

- `scripts/build.py:22-24` prints each command and inherits child stdout/stderr.
- `scripts/build.py:50-54` prints a patch label before printing the `git apply` command.
- `scripts/build.py:132-134` prints one stable top-level build failure after a child failure.
- `tests/support.py:41-67` delegates test commands to the shared runner and does not create another log file.
- `.github/workflows/build.yml:33-92` defines the parent CI output channels. Eval, quota, and template copies are aligned.
- `scripts/installer/main.go:92-114` forwards buffered non-quiet Docker output after the command exits and also copies it into the returned error.
- `scripts/installer/main.go:533-575` reports install failure and the final error. Restoration messages have separate user value.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch:1154-1159` logs the default usage exception to the browser console.
- `.trellis/spec/backend/minimal-linux-delivery.md` requires failure diagnostics, output checks, and no release log payload.
- `.trellis/spec/backend/logging-guidelines.md` separates native errors, result fields, and private-data limits.

## Recommended Minimal Change Set

1. Remove the CI summary tail from all four aligned workflows. Keep the status and diagnostic artifact location.
2. Change the Go Docker helper to forward buffered output only on successful non-quiet commands. Let the final error owner print captured failure detail once.
3. Remove the explicit `Apply ...` line, or make it replace the raw command echo. Prefer one progress line with the actual command.
4. Preserve `Build failed`, install rollback, readiness, and package/upload step errors. They serve different owners.
5. Keep the quota console error unchanged in this task. Do not widen the change to other native account catches.

Do not add Cobra, a logging framework, a verbosity argument, a manifest, a new build entry, or a second diagnostic file.
Use the existing standard-library streams and the existing GitHub Actions artifact action.

## Caveats / Not Found

- The uv search did not return a reliable primary source path for its current subprocess formatter. pip provides the needed Python reference.
- GitHub's documentation recommends unique job-summary content. It does not state that a log tail is forbidden. Removing the tail is this repository's deduplication decision.
- Docker CLI's command connection helper buffers remote-helper stderr. Its output ownership maps to the installer, but its remote connection lifecycle differs.
- The current fixture failure cases in `tests/test_build.py:224-252` intentionally print child failure output during their propagation checks.
  If that noise becomes a problem, use existing `contextlib.redirect_stdout` and `redirect_stderr` around the expected failure assertion, and capture subprocess output only at that test boundary.
  Assert the failure and publication result, not a second copy of the expected error. This is a project-level deduction, not a copied upstream pattern.
- No authenticated GitHub reads or remote CI runs were used.
- This research changed no product code, workflow, spec, or test file.
