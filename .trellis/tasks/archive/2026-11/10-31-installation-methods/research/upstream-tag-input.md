# Select the upstream tag for each build

## Candidate

All four workflows retain push, pull request, and manual triggers.
Manual runs require the string input `upstream_tag`. The input has no default version.
The workflow passes that value through `UPSTREAM_TAG`, outside its shell script.
Local builds use the same override and the same `python3 scripts/build.py` entry.

Without an override, the builder reads the public upstream `/releases/latest` endpoint once.
It uses the response's actual `tag_name`. The request supplies no authorization header or GitHub token.
Lookup or metadata failure stops the build. There is no old-version or literal `latest` fallback.
Version-tag validation keeps the tag suitable for program metadata and artifact filenames.
After cloning, checkout explicitly selects `refs/tags/<tag>`.

The resolved tag enters the builder as one explicit parameter.
The canonical program version removes only its optional leading `v`.
Source checkout, test context, both linker fields, and all ten filenames use these values.
The module no longer contains a fixed `TAG` or `VERSION` authority.

The production entry writes the actual tag once to the standard `GITHUB_OUTPUT` file.
Output validation and every direct artifact upload consume `steps.build.outputs.tag`.
The workflow does not resolve a second version or create another metadata manifest.
Root and template READMEs describe overrides, automatic selection, and example filenames.

## Existing checks

`PYTHONDONTWRITEBYTECODE=1 python3 -B tests/test_build.py` passed four existing cases in 9.369 seconds.
The composition fixture now uses `v1.2.3-rc.4` rather than the former fixed version.
It checks release metadata selection, source tag selection, test context, both linker fields, and all ten filenames.
The standalone fixture confirms that an explicit override skips the release lookup.
The existing failure case includes release lookup failure and preservation of previous outputs.

The persistent test suite calls the resolver and builder directly. It never runs the production entry.
Its synthetic tag therefore cannot overwrite a CI job's inherited `GITHUB_OUTPUT`.

A focused entry check used a mocked build and a private temporary output file.
It confirmed that the production entry exports the same explicit tag that it passes to the builder.
The actual workflow validation shell accepted that exported tag against the retained outputs.
All ten direct upload paths resolved to those files.
Output record: `/tmp/sub2api-upstream-tag-check-supzv_m8/output`.

Four builders, workflows, and existing builder suites have identical contents.
Diff formatting checks passed in all four repositories.
The affected source and test directories contain no generated Python or test caches.

## Network and build limits

The first unauthenticated release lookup encountered a TLS connection reset. The resolver reported that failure without a fallback tag.
A subsequent unauthenticated `curl` request reached the same endpoint and returned `v0.2.19`, with `draft:false` and `prerelease:false`.
The actual product resolver then passed independently with `UPSTREAM_TAG` empty, returning `Resolved upstream tag: v0.2.19` and exit status zero.
Neither check changed the resolver, supplied credentials, or added fallback behavior.

```sh
UPSTREAM_TAG= python3 -B -c 'import runpy; build=runpy.run_path("scripts/build.py"); print("Resolved upstream tag:", build["resolve_upstream_tag"]())'
```

No remote Actions run or full product build occurred for this revision.
The retained v0.2.19 products remain unchanged.
A later build will use normal patch and test failures to report any incompatibility.
