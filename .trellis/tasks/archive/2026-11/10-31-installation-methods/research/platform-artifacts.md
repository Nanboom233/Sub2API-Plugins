# Installer host and application runtime

## Evidence and purpose

Assessment date: 2026-11-01. Sources are the current build kit and the locally installed Go standard library.
This is source research. No compilation, runtime test, or deployment operation ran.
The official application targets remain those verified in [deployment forms](deployment-forms.md).

## Host and payload are separate targets

An installer runs on the machine that controls the application. Its embedded program runs in the application environment.
These environments can differ even when their CPU architecture matches.

| Official installation | Installer execution environment | Application program format |
| --- | --- | --- |
| Native Linux | Linux with the target CPU architecture | Linux ELF |
| Native macOS | Darwin with the target CPU architecture | Mach-O |
| Native Windows | Windows/amd64 | PE executable |
| Docker/Compose on its Linux host | Linux host environment | Linux ELF matching the selected container |
| Apple container | Darwin/arm64 host | Linux/arm64 ELF in the guest |

Apple container therefore needs a Darwin installer that supplies a Linux/arm64 program.
A Darwin native program cannot replace the Linux guest program.
This does not add an installation category. It changes payload selection within the Apple category.

## Current source constraints

| Source | Confirmed behavior | Required planning consequence |
| --- | --- | --- |
| `scripts/build.py:98` | Removes inherited `GOOS`, `GOARCH`, and `CGO_ENABLED` before checks | Setting shell environment variables cannot select another output target today |
| `scripts/build.py:110` | Creates one Linux/amd64 target dictionary | Application and installer currently receive the same target |
| `scripts/build.py:74` | Compresses one application into `payload.gz` | A different host/payload combination needs deliberate packaging |
| `scripts/build.py:121` | Publishes one pair into `dist/build/` | Repeated target builds would overwrite the same paths without target separation |
| `scripts/installer/main.go:33` | Compares a literal Linux/amd64 ELF header | ARM64, Mach-O, and PE cannot pass this check |
| `scripts/installer/main.go:95` and `:431` | References POSIX `SysProcAttr.Setpgid` | Windows compilation needs platform-specific process handling |
| `scripts/installer/main.go:339` and `:518` | Creates files under literal `/tmp` | Windows needs its actual temporary directory |
| `.github/workflows/build.yml` | Runs one Ubuntu job and packages one fixed pair | Current artifact packaging has no platform distinction |

The installed Go source defines `Setpgid` for POSIX process attributes. Its Windows process-attribute type has no such field.
This is a source-level compilation obstacle, not only an untested runtime behavior.
Inspecting only the Go target variables would miss it.

Go supplies executable readers in `debug/elf`, `debug/macho`, and `debug/pe`.
They expose CPU architecture and file-format metadata. A future implementation can use these instead of another handwritten header parser.
File compatibility and application version remain separate checks. Preserve the existing version warning and explicit continuation behavior.

## Reusable build work

Source download, patch composition, dependency preparation, and frontend build do not require separate plugin processing for each runtime target.
The same patched source and frontend output can feed target-specific application compilation.
Installer packaging follows application compilation because it embeds the selected program and license resources.
Keep the argument-free `build.py` entry and automatic tests when planning those changes.

The existing tests run with host target variables cleared. Cross-compiling an output does not execute its application on that target.
Do not report target runtime support from a host test or compilation result alone.
Existing build cases also assert Linux/amd64 explicitly. Update their existing target assertions when the approved build contract changes.
The installer fake-Docker fixture uses a POSIX shell shim. It is not a Windows runtime acceptance result.
These observations identify affected checks. They do not require a new suite or a platform test matrix for this research.

## Preferred packaging direction

Keep one source-preparation flow and separate the installer host target from the embedded application's runtime target.
Preserve the current Linux/amd64 pair for its existing use.
For Apple, plan the Darwin/arm64 host and Linux/arm64 guest combination explicitly.
Keep platform identity in output directories or artifact grouping so different targets cannot overwrite each other.
Exact distribution names and payload combinations belong to the later implementation plan.

## Source references

- [Build source](../../../../scripts/build.py).
- [Installer source](../../../../scripts/installer/main.go).
- [Current CI](../../../../.github/workflows/build.yml).
- [Existing build cases](../../../../tests/test_build.py).
- [Existing installer cases](../../../../tests/test_installer_test.go).
- Local Go 1.27.2 source: `src/syscall/exec_windows.go:292`, `src/syscall/exec_libc.go:16`, and `src/debug/{elf,macho,pe}`.
