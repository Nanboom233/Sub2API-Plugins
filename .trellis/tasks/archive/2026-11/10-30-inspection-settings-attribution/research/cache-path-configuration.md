# Research: Explicit CI Cache Paths

- Question: Can CI use known Go and pnpm cache paths without a separate locate step or changes to `build.py`?
- Date: 2026-11-06
- Scope: Tool configuration and a local path probe. Product files remain unchanged.

## Result

Yes. Declare `GOMODCACHE`, `GOCACHE`, and `pnpm_config_store_dir` in the workflow environment.
The current `build_environment()` copies `os.environ` and preserves all three variables.
The existing Go and pnpm commands therefore use those paths without builder changes.

Use the pnpm store's configured parent directory as the cached path. pnpm 12.16.1 adds its own `v11` subdirectory.
Do not hardcode `v11`. Do not use `npm_config_store_dir`, which pnpm 12 ignores.

## Supported Configuration

| Setting | Verified effect |
| --- | --- |
| `GOMODCACHE` | Selects the Go module download cache directory. |
| `GOCACHE` | Selects the Go compilation cache directory. It must be an absolute path. |
| `pnpm_config_store_dir` | Selects pnpm's store parent directory and overrides workspace configuration. |
| `npm_config_store_dir` | Ignored by pnpm 12.16.1. It leaves the default store in use. |

The [pnpm configuration reference](https://pnpm.io/configuring#environment-variables) states that `pnpm_config_` and `PNPM_CONFIG_` variables configure pnpm.
It also states that these values override workspace settings, while CLI arguments take precedence.
It explicitly says that pnpm no longer reads `npm_config_*` variables.
The [store reference](https://pnpm.io/settings/store#storedir) defines the `storeDir` setting.

The [Go environment reference](https://pkg.go.dev/cmd/go#hdr-Environment_variables) defines `GOCACHE` and `GOMODCACHE`.
Local `go help environment` confirms both contracts.

## Actual Local Probe

The probe used the already installed Node 24.21.0, Corepack 0.36.0, pnpm 12.16.1, and Go 1.27.2 on Darwin arm64.
It created two empty working directories under `/tmp/sub2api-cache-paths.7FiFZX`.
It did not install packages, run a product build, or access the remote cache service.

From the first working directory:

```text
pnpm_config_store_dir=/tmp/sub2api-cache-paths.7FiFZX/store
corepack pnpm@12.16.1 store path --silent
=> /tmp/sub2api-cache-paths.7FiFZX/store/v11
```

The same command and variable from the second working directory returned the identical path.
The configured absolute store is therefore independent of the command's working directory.

Using only the old variable produced the default path:

```text
npm_config_store_dir=/tmp/sub2api-cache-paths.7FiFZX/legacy-store
corepack pnpm@12.16.1 store path --silent
=> /Users/minami/Library/pnpm/store/v11
```

Go accepted explicit paths:

```text
GOMODCACHE=/tmp/sub2api-cache-paths.7FiFZX/go-mod
GOCACHE=/tmp/sub2api-cache-paths.7FiFZX/go-build
go env GOMODCACHE GOCACHE
=> /tmp/sub2api-cache-paths.7FiFZX/go-mod
=> /tmp/sub2api-cache-paths.7FiFZX/go-build
```

## Application to This Repository

An example workflow-level configuration is:

```yaml
env:
  GOMODCACHE: ${{ github.workspace }}/dist/cache/go-mod
  GOCACHE: ${{ github.workspace }}/dist/cache/go-build
  pnpm_config_store_dir: ${{ github.workspace }}/dist/cache/pnpm
```

Cache those three directories directly. The pnpm path includes pnpm's versioned child automatically.
This removes path-discovery commands and their output wiring. It adds no builder interface or committed configuration file.
The local argument-free build retains its current defaults when these workflow environment variables are absent.

The existing `scripts/build.py:172` copies the process environment for build commands.
It removes only target variables and does not remove or replace these cache settings.
Its generated pnpm workspace configuration does not defeat the environment override.

This evidence establishes path configuration only. It does not choose between explicit restore/save steps and native post-save.
The main session owns that workflow lifecycle decision and the next plan review.
