# Research: Quota CI installer state-file race

- Query: Explain the quota CI failure in `TestInstallTransaction/restore-failure-keeps-path`.
- Scope: Internal code, hosted CI evidence, and Go standard-library behavior.
- Date: 2026-11-05

## Findings

The quota workflow failed in the common installer test. The failed step was
`Prepare and test` in run
`https://github.com/Nanboom233/sub2api-quota-extension/actions/runs/41956544123`.
The failure was a test-process panic, not an installer error:

```text
--- FAIL: TestInstallTransaction/restore-failure-keeps-path
panic: unexpected end of JSON input
sub2api-plugins-installer.readState(.../test_installer_test.go:69)
TestInstallTransaction(.../test_installer_test.go:429)
```

The fixture stores Docker command state in a shared `state.json` file. The
fake Docker process reads the file at lines 117-120 and writes it with
`os.WriteFile` at lines 74-81. `os.WriteFile` truncates an existing file before
writing. A concurrent HTTP readiness handler reads the same file at lines
277-278. Therefore, a reader can observe an empty or partial JSON document.

The failing case deliberately enters the readiness timeout path. The fixture
returns incomplete setup at lines 289-295. `readiness` invokes Docker commands
with a timeout context. The installer uses `exec.CommandContext`, which kills a
child process when the context ends. If the fake Docker child is killed after
the truncate and before the write completes, the empty state file remains.
The later assertion at line 429 then panics while reading that file.

The same fixture has a second race window. The readiness HTTP handler can read
the file while a fake Docker process rewrites it. That handler can panic at
line 278 and return a failed request, which changes the timeout path.

The issue is confined to test support. Production installer code does not read
`INSTALLER_FAKE_DOCKER_STATE`, `state.json`, or `fakeState`. The hosted eval,
template, and parent runs passed the same common installer test. The four
`tests/test_installer_test.go` copies are content-identical, so the shared
fixture defect can affect all four build kits.

## Minimal repair recommendation

Change only the shared test helper. Make `writeState` write to a temporary file
in the same directory, close it, and rename it over `state.json`. A same-
directory rename gives readers either the old complete JSON or the new complete
JSON. Keep the existing `readState` assertions so real fixture corruption still
fails the test.

Apply the identical helper change to:

- `tests/test_installer_test.go`
- `plugins/codex-candy-eval/tests/test_installer_test.go`
- `plugins/sub2api-quota-extension/tests/test_installer_test.go`
- `plugins/sub2api-plugin-template/tests/test_installer_test.go`

Do not change installer transaction logic, readiness behavior, CI retry rules,
or the test timeout. Those changes would hide the fixture race or alter the
installation contract.

## Evidence and references

- `tests/test_installer_test.go:62-81`: JSON state reader and non-atomic writer.
- `tests/test_installer_test.go:117-120`: fake Docker process state update.
- `tests/test_installer_test.go:270-303`: readiness server reads shared state.
- `tests/test_installer_test.go:409-429`: restore-failure case and final state read.
- `scripts/installer/main.go:276-341`: readiness loop and timeout context.
- `scripts/installer/main.go:406-425`: context-bound version command execution.
- `scripts/installer/main.go:485-560`: rollback path after readiness failure.
- `tests/support.py:8,48-67`: common installer test selection and execution.
- Go `os.WriteFile` documentation: it truncates before writing and can leave a
  partially written file if the operation stops mid-write.
- Go `exec.CommandContext` documentation: it kills the child process when the
  context is done before the command completes.

## Reproduction and caveats

A temporary copy of the installer package ran the failing subtest 30 times on
the local machine and passed. The hosted panic did not reproduce locally.
The code exposes a truncation window that matches the hosted timeout failure.
The exact process interruption was not captured by the hosted log.
No product output or installer artifact was published by the failed quota run.

## Repair verification

All four `writeState` helpers now use `os.CreateTemp` beside the destination.
They write and close the temporary file before `os.Rename` replaces the destination.
Normal returns remove the temporary path. Test-directory cleanup removes files left by a killed helper.
The existing strict reader, production installer, timeouts, and CI configuration remain unchanged.

The existing `TestInstallTransaction` suite passed all seven subcases in 8.744 seconds.
A temporary concurrent-reader probe reproduced `unexpected end of JSON input` with the original helper.
The same probe passed with the fixed helper: 300 writes and 959 complete JSON reads.
A killed-writer probe preserved the original complete JSON after termination during temporary-file preparation.
These probes stayed under `/tmp`. No permanent suite or build gate was added.

Logs:

- `/tmp/quota-installer-state-old.log`
- `/tmp/quota-installer-state-fixed.log`

All four fixture copies match and pass formatting checks.
Independent Trellis review passed with no blocking findings. It reused the existing focused evidence without repeating a full build.
No repaired commit or hosted rerun exists yet.
