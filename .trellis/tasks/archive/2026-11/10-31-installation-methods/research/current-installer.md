# Current installer and build coverage

## Source baseline

This assessment reads the current working tree on 2026-10-31. No deployment was changed or restarted.
The existing Docker daemon was unreachable during the parent's persistence assessment. This report adds no runtime verification claim.

| Owner | Current contract | Extension consequence |
| --- | --- | --- |
| `scripts/build.py:16` | Downloads Sub2API tag `v0.2.19` and applies discovered patches | More installation forms do not change the application source target automatically |
| `scripts/build.py:110` | Builds both outputs with `GOOS=linux`, `GOARCH=amd64`, and `CGO_ENABLED=0` | Other architectures require build changes and matching installer payloads |
| `scripts/build.py:112` | Builds the native server with `-tags=embed` after frontend compilation | The replacement executable contains patched frontend assets |
| `scripts/installer/main.go:26` | Uses fixed paths `/app/sub2api` and `/app/sub2api.plugins-new` | Native installations and custom container layouts need target-path handling |
| `scripts/installer/main.go:33` | Checks a fixed 20-byte Linux/amd64 ELF header | Other architectures and executable formats cannot pass this check |
| `scripts/installer/main.go:92` | Calls the executable named `docker` | Native programs and Apple container need their actual startup commands |
| `scripts/installer/main.go:95` | Uses POSIX `syscall.SysProcAttr{Setpgid: true}` and fixed `/tmp` directories | A native Windows installer needs platform-specific process and temporary-path handling |
| `scripts/installer/main.go:131` | Lists running containers from the current Docker endpoint and requires numbered selection | Native programs and Apple container have no discovery path |
| `scripts/installer/main.go:185` | Derives host HTTP access from ports, host networking, or container network addresses | A remote Docker endpoint does not establish that the installer's host can reach those addresses |
| `scripts/installer/main.go:217` | Requires direct HTTP 200 responses from `/health` and `/setup/status` | Service discovery and readiness need deployment-specific endpoint resolution |
| `scripts/installer/main.go:371` | Copies a staged executable, then uses container UID 0, `sh`, `chmod`, and `mv` | Read-only filesystems, missing shell tools, and mount boundaries can prevent replacement |
| `scripts/installer/main.go:423` | Runs installed and staged programs with `docker exec ... -version` | Native processes need a local program probe rather than a container command |
| `scripts/installer/main.go:466` | Warns and asks for confirmation when either version is unresolved or differs | Preserve warning behavior when adding installation targets |
| `scripts/installer/main.go:518` | Retains a backup under the installer's host `/tmp` | This is temporary recovery storage, not migration persistence |
| `scripts/installer/main.go:533` | Restarts the selected container ID | Native programs and Apple container need their actual startup owner |
| `scripts/installer/main.go:543` | Restores the backup and checks readiness after failure | New targets need equivalent recovery through their deployment owner |

## Current coverage boundary

The existing path targets a running Docker container with a writable `/app` directory and the required commands.
The installer itself runs as Linux/amd64. Its Docker access and HTTP reachability must match the target environment.
Official Compose variants share this mechanism when their effective container layout matches these assumptions.

The installer does not read Compose configuration or mounts before replacement.
It cannot currently classify writable-layer replacement, a directory bind mount, and a file bind mount.
Renaming onto a file mount can fail. A persistent directory mount can behave differently from the normal writable layer.
These require inspection of the actual deployment, rather than a claim that every container shares one persistence rule.

## Program persistence and data persistence

An ordinary restart of the same container retains its writable-layer executable.
Recreation from the original image does not retain that executable without a persistent program source or reapplication.
Native installation updates can also overwrite a patched executable. Persistence follows the file and update owner, not the deployment label.

Settings and account state reside in PostgreSQL. Eval history uses the configured data directory under `codex-eval/history.json`.
Keeping those stores does not itself preserve the executable. In-memory work does not survive process restart.

## Planning implications

Eval's `shared_detector.bin` is embedded model data, not a native helper executable.
`fingerprint_detector.go` decodes it with Go's `encoding/binary`, JSON, and math packages in `0001-evaluation-core.patch:624`.
Do not treat that filename as evidence of an extra Linux/amd64 runtime dependency.
The quota patch runs custom JavaScript through the embedded Goja runtime, rather than a host Node.js command.
These source facts do not establish compilation or runtime success on additional platforms.

Separate artifact compatibility, installed-program discovery, service control, readiness, and persistence when comparing deployment forms.
Prefer shared replacement and recovery rules with small integrations for actual deployment owners.
Release downloads and source-built native programs use the same replacement mechanism.
Systemd, manual launch, Docker, and Apple container differ in how they control the running program.

These findings define current gaps. They do not authorize product changes or a new runtime test matrix.
