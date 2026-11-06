# Sub2API Development Guidelines

## Current scope

Active delivery builds the selected upstream tag on Linux amd64/arm64, Darwin amd64/arm64, and Windows amd64.
The verified integration baseline is Sub2API v0.2.19.
Builds discover plugin submodules automatically.
The common build downloads upstream source. Plugins own production patches, business tests, and their licenses.
Each plugin and the template carry a complete standalone build kit. Local builds and CI both run `python3 scripts/build.py`.
Combined builds skip empty patch sets and run common build/installer tests once.
One CI build job restores dependency caches, compiles selected targets sequentially, and uploads only final executable pairs.
An optional Release step publishes those same local files within the build job. Errors stay in native Actions logs.
All test cases and support code live in flat `tests/`. `assets/` contains data resources only.
Each platform has a self-contained Go installer for Docker/Compose, native programs, and supported Apple container installations.
The installer uses dynamic terminal interaction where supported, plain numbered prompts otherwise, and automatic Chinese/English terminal locale.

## Active guidelines

| Guide | Purpose |
| --- | --- |
| [Directory Structure](./directory-structure.md) | Current native code, tests, and delivery owners |
| [Administrator Evaluation](./runtime-installation.md) | Sending, task APIs, history, page and native session contracts |
| [Native Candy Inspection](./native-inspection.md) | Automatic rounds, native settings, priority changes and the Settings tab |
| [API Key Account Usage](./api-key-quota.md) | Default/custom quota queries, draft previews, native cells, and focused tests |
| [Binary Delivery](./minimal-linux-delivery.md) | Automatic source download, composition, version warnings, and replacement/restoration |
| [Persistence](./database-guidelines.md) | Native settings and versioned three-map JSON history |
| [Error Handling](./error-handling.md) | Actual errors, cancellation and shared bounded retries |
| [Diagnostics](./logging-guidelines.md) | Error visibility and private-data boundaries |
| [Quality and Commits](./quality-guidelines.md) | Changed-code checks and commit workflow |

The current task and active contracts supersede historical v0.2.17 build rules and retired adapter, gateway, and activation designs.
Historical specification files remain evidence; they do not add implementation or test requirements.
Plugin registration, dependency resolution, standalone cleanup, compatibility configurations, and assistant-added race gates are excluded.

## Pre-Development Checklist

1. Read the active task's requirements and approved planning artifacts.
2. Read `AGENTS.md`.
3. Identify the smallest change boundary.
4. Read the directory guide and the specific guides for the affected behavior.
5. Inspect the patched native owners and corresponding tests before editing.
6. Search for existing helpers before adding scheduling, response, history, or model-execution logic.
7. Read the [shared thinking guides](../guides/index.md) when changes span boundaries or repeat existing behavior.
8. Check native handler, runner and page consumers before changing their contracts.
9. Preserve unrelated work.
10. Keep private deployment values out of files and reports.

The shared guides contain upstream Trellis examples. Apply their general reasoning to this delivery. Do not assume their upstream package paths exist here.

## Quality Check

For changed native code, use the current entry:

```sh
python3 scripts/build.py
```

It downloads source, combines plugins, runs executable test entries, and builds versioned program and installer outputs.
Reuse completed baseline and unchanged integration evidence.
Add focused checks only for changed behavior lacking coverage.
Format changed Go files and check affected scripts/resources.
Do not run retired universal helpers, full root suites or a repeated pristine baseline for this task.
No race, coverage, runtime architecture matrix, v0.2.17 comparison build, or manual Docker or browser gate is required.
Report actual results and any visual or hardware execution limits.
Keep task/fixture logs outside the user package.

For spec-only changes, verify current source claims and local references.
Follow [the commit workflow](./quality-guidelines.md#commit-and-finish-work) after implementation, check and spec synchronization.

## Documentation Rules

Follow the shared [documentation and manifest rule](../guides/index.md#documentation-and-manifest-files).

Write project specs in English. Keep assistant replies in Chinese. Use `/output` style: short sentences, active voice, common words, and one name for each concept.

Limit instructions to 20 words. Limit descriptions to 25 words. Use one instruction per sentence. Do not use semicolons or contractions. Keep each paragraph to one topic and at most six sentences.

Describe current repository patterns. Cite real owner files or tests. Do not invent dependencies, frameworks, migration systems, or production guarantees.

For ordinary work commits, follow the [hybrid commit process](./quality-guidelines.md#commit-and-finish-work). Record spec changes before the work commit.

Trellis manages task artifacts, archive commits, and session records through its native workflow. Do not apply ordinary `/git-commit` gates to each generated bookkeeping commit.
