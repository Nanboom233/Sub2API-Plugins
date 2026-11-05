# Installation operations for the three official forms

## Scope

This report checks operational contracts at upstream `v0.2.19`.
It covers Docker/Compose, native executables, and Apple container.
Downloaded and self-built executables use the same native installation form.
The review used source files only. No installation or runtime test ran.
See [deployment forms](deployment-forms.md) for release targets and persistence details.

## Native configuration and process ownership

The server declares `-setup` and `-version` flags. It does not declare a configuration-path flag. [S1]
The configuration loader uses `CONFIG_FILE` when set.
Otherwise, it searches these directories for `config.yaml`, in order: [S2]

1. `DATA_DIR`, when set.
2. `/app/data`.
3. The current directory.
4. `./config`.
5. `/etc/sub2api`.

Setup chooses its data directory separately: `DATA_DIR`, writable `/app/data`, then the current directory.
It writes `config.yaml` and `.installed` there. [S3]
An installer must preserve the actual working directory and environment.
The presence of `/etc/sub2api` does not establish the active configuration path.

The official systemd unit has these settings: [S4]

| Setting | Value and consequence |
| --- | --- |
| Program | `ExecStart=/opt/sub2api/sub2api` |
| Process owner | `User=sub2api`, `Group=sub2api` |
| Working directory | `/opt/sub2api` |
| Restart owner | `Restart=always`, `RestartSec=5` |
| Write restriction | `ProtectSystem=strict`, with `ReadWritePaths=/opt/sub2api` |
| Other restrictions | `ProtectHome=true`, `PrivateTmp=true`, `NoNewPrivileges=true` |
| Explicit environment | `GIN_MODE=release`, `SERVER_HOST=0.0.0.0`, `SERVER_PORT=8080` |
| Logs | Standard output and standard error go to the journal |

The service process needs filesystem permission as well as an allowed write path.
The unit's write allowance does not grant file ownership.
An external installer runs outside this unit and must preserve the service owner's access.

For a manual process, the operator owns its launch command, environment, working directory, and process lifecycle.
The executable path alone cannot reconstruct this state.
Automatic relaunch of an arbitrary manual process is therefore not established.

## What the built-in updater can reuse

`UpdateService` uses the fixed release repository `Wei-Shaw/sub2api`. [S5]
`PerformUpdate` selects the latest upstream release.
Version rollback selects an allowed older upstream release.
Neither update route accepts a local program or a custom download URL. [S5–S6]
These endpoints cannot install the plugin build directly.

The replacement pattern is useful: [S5]

1. Get the executable path with `os.Executable()`.
2. Resolve its symbolic links with `filepath.EvalSymlinks()`.
3. Create a temporary directory beside the executable.
4. Download and extract the matching runtime archive there.
5. Set executable permission before replacement.
6. Rename the current executable to its `.backup` path.
7. Rename the new executable to the original path.
8. Restore the backup if the second rename fails.

This keeps replacement files on the same filesystem.
The successful update retains `.backup` for a later rollback.
Local rollback renames that backup over the executable and consumes the backup.
Update and rollback return `need_restart: true`. They do not restart the process. [S6]

The separate restart endpoint calls `sysutil.RestartServiceAsync()`.
On Linux, this exits the process with status zero after a short delay. [S7]
Systemd, a Docker restart policy, or Apple's supervisor must start it again.
On Darwin and Windows, this function logs a message and returns without a restart.
Do not use this endpoint as cross-platform process control.
The server handles SIGINT and SIGTERM with an HTTP shutdown timeout of five seconds. [S1]

## Docker and Compose operations

The standard image executes `/app/sub2api` through its entrypoint. [S8–S9]
The entrypoint prepares `/app/data`, changes its owner, then switches to the `sub2api` user.
It does not copy a replacement executable at startup.
The executable belongs to UID/GID 1000 in the image.
The official Compose file uses `restart: unless-stopped`. [S10]

The reviewed Docker guide and standard Compose file document data and configuration mounts.
They do not define a persistent mount for `/app/sub2api`.
A replacement in the container's writable layer survives the same container's restart.
Container recreation starts from the image and loses that replacement.

The installer can retain its existing Docker backup, replacement, restart, readiness, and restoration flow.
The selected container's actual executable and mounts determine the replacement location.
Preserve Docker's process ownership and existing restart policy.
Changing Compose files or publishing a patched image is not necessary to establish this installation path.

## Apple container operations

The official script creates a Linux/arm64 application container with a custom shell supervisor. [S11]
It mounts the application volume at `/app/storage`.
The active executable is `/app/storage/runtime/sub2api`.
The image executable `/app/sub2api` is only its initial or replacement source.

The script stores the selected image ID in `/app/storage/runtime/base-image-id`.
When the executable is absent or this ID changes, it copies the image executable into the runtime directory.
That reset also removes the runtime `.backup` file.
Do not change the marker to disguise a different base image.

The supervisor runs the runtime executable as `sub2api`.
After a child exit, it waits one second and starts that executable again.
Its TERM/INT handler stops the child and exits the supervisor.
Thus the Linux web restart behavior works through this supervisor.

Apple `container` 1.1.0 supplies these operations: [S11–S13]

| Operation | Source contract |
| --- | --- |
| `container copy`, alias `cp` | Copies between a local path and a running container's `container-id:/absolute/path` |
| `container exec` | Runs a command in a running container, with process-user options |
| `container stop --time 30` | The upstream script uses this to stop the selected container |
| `container start` | The upstream script uses this to start an existing container |

A viable adapter can copy a staged executable, replace the runtime file, and use the application's container lifecycle.
It must preserve executable permission, `sub2api` ownership, and the existing image marker.
Source inspection establishes these operations. It does not verify their execution on a local Apple runtime.

Apple 1.1.0 explicitly rejects `copyIn` and `copyOut` unless the container status is `running`.
See [`ContainersService.copyIn` and `copyOut`](https://github.com/apple/container/blob/1.1.0/Sources/Services/ContainerAPIService/Server/Containers/ContainersService.swift).
The copy command has no named-volume target syntax.
Named volumes use ext4 `volume.img` files, not host directories that accept an ordinary file copy.
See [`VolumesService`](https://github.com/apple/container/blob/1.1.0/Sources/Services/ContainerAPIService/Server/Volumes/VolumesService.swift).
Thus stopped-container copy cannot provide the restoration path.

Copy the new program to a staging path while the container runs.
Set its owner and executable permission before the final rename.
The copy API defaults to mode `0644`.
See [`ContainerClient.copyIn`](https://github.com/apple/container/blob/1.1.0/Sources/Services/ContainerAPIService/Client/ContainerClient.swift).
Keep the backup in the persistent runtime directory.

If the new program fails readiness, the shell supervisor normally remains available for restoration.
It launches `su-exec` in the background and disables `set -e` while it waits.
A failed child execution therefore returns to its restart loop instead of terminating the shell. [S11]
Use `container exec` to restore the backup, then stop/start only the application container.
If the container has stopped, start that same container first, then restore through `exec`.
Stop/start retains its configured shell command and named-volume mount.
With the same image marker and an executable runtime file, startup retains the installed runtime program.

If the VM, volume, or supervisor cannot start, this path cannot restore the file automatically.
Retain the backup and report that restoration remains incomplete.
After the operator repairs that runtime failure, start the existing container and restore the backup through `exec`.

Script `up` always recreates the application container to refresh dependency addresses.
Script `restart` stops the application, Redis, and PostgreSQL, then calls `up`.
A direct application-container stop/start avoids that full-stack restart when dependency addresses have not changed.
The runtime volume retains the replacement across recreation while the selected image ID remains unchanged.
The script's data-only backup does not include the separate runtime directory.

## Recommended shared boundary

Share version warnings, backup, staged replacement, readiness, and restoration.
Adapt the executable location and actual launcher for each installation form.
Use the target runtime to select the executable, separately from the installer host.
Reuse the upstream replacement pattern without extending its release-update API.
For manual native launches, preserve operator control when the original launch state is unavailable.

## Primary sources

- S1. [Server flags and shutdown](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/cmd/server/main.go).
- S2. [Configuration loader, `configureConfigSource`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/config/config.go).
- S3. [Setup paths, `GetDataDir`](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/setup/setup.go).
- S4. [Official systemd unit](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/sub2api.service).
- S5. [Update source, replacement, and rollback](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/service/update_service.go).
- S6. [Update, rollback, and restart handlers](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/handler/admin/system_handler.go).
- S7. [Actual restart implementation](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/backend/internal/pkg/sysutil/restart.go).
- S8. [Docker runtime image](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/Dockerfile).
- S9. [Docker entrypoint](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-entrypoint.sh).
- S10. [Standard Compose](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-compose.yml) and [Docker guide](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/DOCKER.md).
- S11. [Apple runtime and lifecycle](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/apple-container.sh).
- S12. [Apple container 1.1.0 copy command](https://github.com/apple/container/blob/1.1.0/Sources/ContainerCommands/Container/ContainerCopy.swift).
- S13. [Apple container 1.1.0 exec command](https://github.com/apple/container/blob/1.1.0/Sources/ContainerCommands/Container/ContainerExec.swift).
