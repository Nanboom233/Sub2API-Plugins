# Go target builds and measured CI overhead

## Findings

A single `go build` uses one `GOOS` and `GOARCH` pair.
Building several target platforms requires separate Go invocations, through a loop or another orchestrator.
The `-p` flag controls package/tool parallelism within one invocation. Its default follows `GOMAXPROCS`.
Separate build processes on one runner share that runner's CPU and memory. More processes do not imply more compute capacity.

The Go build cache supports concurrent Go invocations.
Its action key includes both target OS and architecture.
Grouping Windows/amd64 and Darwin/amd64 does not make their compiled package objects interchangeable.
Architecture grouping can keep matching Linux installer payloads local, which is a data-flow benefit rather than a compiler optimization.

## Existing hosted measurements

The same matrix topology ran before and after reusable caches existed.
No extra build or benchmark ran for this assessment.

| Parent run | Cache state | Remaining server compile steps | Server group elapsed | Installer compile steps | Installer group elapsed |
| --- | --- | --- | --- | --- | --- |
| [41956595900](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/41956595900) | Initial caches | 124, 130, 127, 129 seconds | 187 seconds | 10, 17, 12, 8, 14 seconds | 109 seconds |
| [42021443875](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/42021443875) | Reused caches | 4, 4, 6, 5 seconds | 79 seconds | 6, 10, 15, 8, 13 seconds | 95 seconds |

Group elapsed spans the earliest job start through the latest job completion.
Prepare already produced Linux/amd64, so the server group contains only four remaining targets.
The warm server jobs consumed 282 aggregate runner seconds for 19 seconds of actual build commands.
Warm installer jobs consumed 375 aggregate runner seconds for 52 seconds of actual build commands.
Warm publication consumed another 41 seconds after downloading the compiled products.
These job times include setup, cache work, artifact transfers, and other native Action overhead.

The earlier sequential cold build [41944176807](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/41944176807) spent about 130 seconds on each server target.
Together, these observations support distributing expensive cold target compilation across independent runners.
They do not isolate architecture grouping or prove a speedup from multiple build processes on one runner.
The earlier sequential run had different cache conditions and code. Its total time is not a controlled matrix comparison.

## Judgment

The current two compilation matrices split warm work too finely for its measured command durations.
Keep dependency caching and shared preparation, but do not equate caching gains with matrix gains.
If zero intermediate artifacts is the priority, prefer one build runner with the existing target loop and native Go package parallelism.
Do not add custom cross-target concurrency until evidence justifies its complexity and resource use.
This assessment changes no product files or workflow configuration.

## Sources

- [Official Go build and environment reference](https://pkg.go.dev/cmd/go).
- Local `go help build`, `go help environment`, and `go help cache` from Go 1.27.2.
- Go 1.27.2 `src/cmd/go/internal/work/exec.go`, `buildActionID` and `linkActionID`, for target cache inputs.
- [Upstream CI research](upstream-build-ci.md), maintained by the delegated upstream researcher.
- `/tmp/sub2api-parent-41956595900-timing.json` and `/tmp/sub2api-parent-42021443875-timing.json`, containing hosted step timestamps.

## Repair trace completion

The fixture repair reached all four public main branches.
All matching automatic runs succeeded and each published ten final products at `v0.2.19`:

- [Parent 6809e44](https://github.com/Nanboom233/Sub2API-Plugins/actions/runs/42021443875).
- [Eval ea36f52](https://github.com/Nanboom233/codex-candy-eval/actions/runs/42021292516).
- [Quota d5897c2](https://github.com/Nanboom233/sub2api-quota-extension/actions/runs/42021342379).
- [Template 3ad8e71](https://github.com/Nanboom233/sub2api-plugin-template/actions/runs/42021396551).

Quota's previously failing installer suite passed in 7.064 seconds, then all target compilation and publication succeeded.
Eval, template, and parent preparation logs confirmed Go module, Go compilation, and pnpm cache reuse from the previous runs.
Quota had no saved caches from its failed run. It prepared normally and saved its caches after successful tests.
The branch pushes skipped optional Release publication.
