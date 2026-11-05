# Official user installation forms

## Scope and source versions

Research date: 2026-10-31. This report covers official user-facing deployment forms only.
No installation, build, or runtime test ran.

The plugin target is upstream `v0.2.19`, commit `dece26153621959ccd7635814f4b2d08304e681a`.
The observed current `main` commit is `d851a38477597157e78450d30af2d8504764d085`.
Its installation mechanisms remain the same. Compose and configuration contents differ, so `main` downloads do not select the target version. [S1–S2]

## Three installation forms

| Official form | Active program and launcher | Permissions, frontend, and persistent data |
| --- | --- | --- |
| Docker run or Docker Compose | `/app/sub2api`. The image entrypoint executes it as `sub2api`. Docker owns container lifecycle. | Entrypoint fixes `/app/data` ownership before dropping privileges. Frontend is embedded. Application files, PostgreSQL, and Redis have separate storage. [S3–S5] |
| Native executable, downloaded or self-built | Operator-selected program path. Official Linux installation uses `/opt/sub2api/sub2api` and `sub2api.service`. A manual launch uses the chosen process owner. | Linux installer needs root and creates the `sub2api` service user. The unit sets `/opt/sub2api` as its working directory. Frontend is embedded in release and production source builds. [S6–S8] |
| Apple container | `/app/storage/runtime/sub2api`, launched by an in-container supervisor. Host `apple-container.sh` owns the stack. | Requires Apple Silicon, macOS 26, and Apple `container` 1.1.0+. Uses Linux/arm64 images. Persistent `/app/storage` contains separate runtime and application-data directories. [S9–S10] |

Docker Compose variants belong to the same installation form.
Local-directory and named-volume variants change data storage. Standalone Compose uses external PostgreSQL and Redis. [S4–S5]
They do not change the standard active executable path.

A release download and a self-built native executable have the same runtime installation needs.
The source build first compiles the frontend, then uses `-tags embed` for the server. [S6, S8]
The program's origin does not require another installer type.
Systemd and manual launch differ in restart ownership, not in the installed program format.

## Restart, upgrade, and migration

| Form | Restart | Recreation or upgrade | Migration and recovery |
| --- | --- | --- | --- |
| Standard Docker/Compose | Restarting the same container retains its writable-layer executable replacement. | Recreating the container starts from the selected image. Standard `/app/data` mounts do not retain `/app/sub2api`. Image upgrades can replace the patched program. | Data-directory or volume migration alone omits the patched executable. Retain the program or installer separately. Restore the previous program and restart the selected container. |
| Native executable | Process, service, or host restart retains the installed file. | Upstream script upgrades, web updates, or copying another build can replace it. | Copy the executable, required configuration, and data. Restore the old executable and use its actual launcher to restart. |
| Apple container | Script `restart` recreates the application container but retains its runtime executable in the persistent volume. | Script `up` also recreates the application container. A changed base-image ID resets the runtime program from image `/app/sub2api`. | Preserve the runtime directory separately from application data. Restore its executable and use the Apple script's lifecycle. A data-only backup does not include the runtime program. |

The Apple script stores its active program at `/app/storage/runtime/sub2api` and records the base-image ID beside it. [S10]
It copies image `/app/sub2api` only when the runtime executable is absent or the configured image ID changes.
Thus the image path is not the active replacement path after setup.
The official guide requires `up` after host reboot. The runtime does not supply Docker's restart policy or Docker socket. [S9]

Program persistence is separate from data persistence.
Plugin settings and account metadata use PostgreSQL. Evaluation history uses the configured native data directory.
See [the current local baseline](current-installer.md) for those owners and paths.
Upstream database migrations are forward-only. Restoring an older program alone does not reverse a database migration. [S4]

## Published runtime targets

The actual `v0.2.19` release provides these five targets. [S7–S8]

| Runtime | Archive suffix | User-facing startup detail |
| --- | --- | --- |
| Linux/amd64 | `linux_amd64.tar.gz` | Native process, official systemd, or Docker guest |
| Linux/arm64 | `linux_arm64.tar.gz` | Native process, official systemd, Docker guest, or Apple container guest |
| Darwin/amd64 | `darwin_amd64.tar.gz` | Native executable |
| Darwin/arm64 | `darwin_arm64.tar.gz` | Native executable, distinct from Apple container's Linux guest |
| Windows/amd64 | `windows_amd64.zip` | Native executable |

Archive names start with `sub2api_0.2.19_`. GoReleaser explicitly excludes Windows/arm64 and builds the frontend into the server.
Official launchd or Windows service installation was not established. The Linux shell installer creates a systemd unit. [S6]

## Extension direction

Share the existing backup, version warning, replacement, readiness, and restoration behavior.
Adapt the actual program path and launcher for Docker, systemd, manual native processes, and Apple container.
Use the runtime's platform when selecting the program. The current Linux/amd64 build does not cover the other published targets.

Docker variants can share container handling. Native release and source-built programs can share file replacement.
Apple needs its persistent runtime path and script lifecycle.

## Official sources

- S1. [Target deployment instructions](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/README.md#deployment).
- S2. [Observed current deployment files](https://api.github.com/repos/Wei-Shaw/sub2api/contents/deploy?ref=d851a38477597157e78450d30af2d8504764d085).
- S3. [Target Dockerfile](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/Dockerfile), [entrypoint](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-entrypoint.sh), and [Docker run guide](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/DOCKER.md).
- S4. [Target deployment and migration guide](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/README.md).
- S5. Target Compose files: [named volumes](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-compose.yml), [local directories](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-compose.local.yml), and [external dependencies](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/docker-compose.standalone.yml).
- S6. [Target native installer](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/install.sh) and [systemd unit](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/sub2api.service).
- S7. [Actual v0.2.19 release asset inventory](https://api.github.com/repos/Wei-Shaw/sub2api/releases/tags/v0.2.19), published 2026-10-28.
- S8. [Target release configuration](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/.goreleaser.yaml) and [source build instructions](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/README.md#method-4-build-from-source).
- S9. [Target Apple container guide](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/APPLE_CONTAINER.md).
- S10. [Target Apple lifecycle and runtime program code](https://github.com/Wei-Shaw/sub2api/blob/v0.2.19/deploy/apple-container.sh).
