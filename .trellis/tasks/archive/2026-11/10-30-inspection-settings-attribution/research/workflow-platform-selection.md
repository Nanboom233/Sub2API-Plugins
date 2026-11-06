# Research: Manual Platform Selection

- Query: Find mature GitHub Actions patterns for selecting multiple build platforms in a manual run.
- Scope: Internal and external.
- Date: 2026-11-05.

## Findings

GitHub's native `choice` input accepts one value. It does not create a multi-select dropdown. The workflow input limit is 25 fields, so five platform booleans fit the native form. See the [official workflow input reference](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#defining-inputs-for-manually-triggered-workflows).

Three mature projects use one string field for arbitrary platform subsets:

- [GitHub CLI deployment workflow](https://github.com/cli/cli/blob/trunk/.github/workflows/deployment.yml#L24-L27) defines `platforms` as a string. Its default is `linux,macos,windows`. Platform jobs consume the field with `contains(inputs.platforms, ...)` ([Linux job](https://github.com/cli/cli/blob/trunk/.github/workflows/deployment.yml#L50-L55), [macOS job](https://github.com/cli/cli/blob/trunk/.github/workflows/deployment.yml#L94-L99)).
- [Microsoft OpenJDK workflow](https://github.com/microsoft/openjdk-jdk/blob/main/.github/workflows/main.yml#L32-L37) accepts a comma-separated platform string. A shell helper removes spaces and checks each known platform name against that list ([selection helper](https://github.com/microsoft/openjdk-jdk/blob/main/.github/workflows/main.yml#L103-L147)).
- [Weasis installer workflow](https://github.com/nroduit/Weasis/blob/master/.github/workflows/build-installer.yml#L3-L8) accepts `all`, `none`, or a comma-separated subset. `jq` maps exact platform names to selected targets ([selection mapping](https://github.com/nroduit/Weasis/blob/master/.github/workflows/build-installer.yml#L21-L50)). It then creates matrices, which this task does not need.

These examples provide a text input, not a multi-select dropdown. A single-choice dropdown can offer `all` or one target, but it cannot represent arbitrary subsets. A list of prebuilt combinations would limit valid selections and grow with each added target.

The current builder already accepts any nonempty supported subset as whitespace-separated `SUB2API_BUILD_PLATFORMS`. It rejects empty or unsupported values and returns targets in canonical order ([`scripts/build.py`](../../../../scripts/build.py#L151-L158)).

## Recommendation

Keep the five existing boolean inputs if users need a native graphical multi-select. GitHub renders these as separate controls. Users can select any nonempty subset without typing platform names. Five fields stay below the 25-input limit.

If one input is required, use a string named `platforms`. Set its default to `all` and accept exact comma-separated names, such as `linux-amd64,darwin-arm64`. At the workflow boundary, map `all` to the five targets and convert commas to spaces for `SUB2API_BUILD_PLATFORMS`. Keep the builder's current validation and sequential build path. This pattern has direct examples in GitHub CLI, Microsoft OpenJDK, and Weasis.

Neither choice creates a multi-select dropdown. GitHub's native `workflow_dispatch` form cannot provide one. That control needs an external dispatch interface. The reviewed examples do not justify adding one to this task.

## Files Found

| File or source | Pattern |
| --- | --- |
| [`scripts/build.py`](../../../../scripts/build.py) | Validates supported platform names and accepts whitespace-separated subsets. |
| [GitHub CLI `deployment.yml`](https://github.com/cli/cli/blob/trunk/.github/workflows/deployment.yml) | Uses a string input with a comma-separated platform list. |
| [Microsoft OpenJDK `main.yml`](https://github.com/microsoft/openjdk-jdk/blob/main/.github/workflows/main.yml) | Normalizes and matches a comma-separated list against known platforms. |
| [Weasis `build-installer.yml`](https://github.com/nroduit/Weasis/blob/master/.github/workflows/build-installer.yml) | Supports `all` and exact comma-separated target subsets. |

## Related Specs

- `.trellis/tasks/10-30-inspection-settings-attribution/prd.md`, requirements R15-R19 and acceptance criteria AC17-AC18.
- `.trellis/spec/backend/minimal-linux-delivery.md` in the parent and evaluation plugin.

## Caveats / Not Found

The Grok search connection failed. The research used the available web search fallback, then checked official GitHub documentation and public source files.
The GitHub CLI and Microsoft OpenJDK examples also support other event triggers. This report uses only their manual input schema and platform-selection code.
The Weasis workflow uses target matrices. Its list parsing is relevant, but its matrix orchestration is outside this task's design.
