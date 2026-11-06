# Cache paths in mature project workflows

## Scope

This report records two public workflow examples read on 2026-11-06.
Both examples avoid a separate cache-path discovery step.
The examples support workflow-owned cache configuration.
They do not establish the final cache design for this project.

## Tailscale declares the Go module cache path

Source: [tailscale/tailscale, `.github/workflows/test.yml`](https://github.com/tailscale/tailscale/blob/main/.github/workflows/test.yml).

The workflow declares one module cache location for all operating systems:

```yaml
env:
  GOMODCACHE: ${{ github.workspace }}/gomodcache
```

Cache restore steps use the declared directory directly:

```yaml
- name: Restore Go module cache
  uses: actions/cache/restore@668228422ae6a00e4ad889ee87cd7109ec5666a7 # v5.0.4
  with:
    path: gomodcache
    key: ${{ needs.gomod-cache.outputs.cache-key }}
    enableCrossOsArchive: true
```

Go compilation cache steps also use known platform paths:

```yaml
path: |
  ~/.cache/go-build
  ~\AppData\Local\go-build
```

The workflow has separate restore and save actions.
Save steps apply branch and cache-miss conditions where needed.
This example supports direct cache paths without a discovery step.
It does not support a claim that Tailscale combines all cache operations into one action.

## Vue delegates the pnpm cache to tool setup

Source: [vuejs/core, `.github/workflows/ci.yml`](https://github.com/vuejs/core/blob/main/.github/workflows/ci.yml).

The `continuous-release` job uses these steps:

```yaml
- name: Install pnpm
  uses: pnpm/action-setup@73e46992e05b19abd31f2f3c20e0e7370d762115 # v6.1.1
- name: Install Node.js
  uses: actions/setup-node@949feb2413d6458794dcd2491c4babbbce0c15c1 # v7.1.0
  with:
    node-version-file: '.node-version'
    registry-url: 'https://registry.npmjs.org'
    cache: 'pnpm'
- name: Install deps
  run: pnpm install
```

The setup action owns the pnpm cache operation.
The workflow has no separate store-path discovery step.
It does not change a product build script to return cache paths.
The setup action manages cache restore and its later save operation.

This example does not declare `store-dir` explicitly.
It does not establish which environment variables pnpm 12 accepts.
It also does not combine the Go and pnpm caches into one operation.

## Application to this project

Keep cache paths and cache operations in CI configuration.
Use declared paths when the tools support explicit configuration.
Confirm the actual pnpm 12 configuration before selecting its store path.
Do not add cache-path discovery outputs to `build.py`.
The final cache load and save design requires separate lifecycle evidence.
