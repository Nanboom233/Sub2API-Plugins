# Research: Same-Tag Release and Tag Recreation

- Query: Verify how `gh release delete` and `gh release create` replace an existing same-tag Release and Git tag during repeated `Publish Release` runs.
- Scope: Internal workflow contracts and external GitHub CLI v2.102.0 and GitHub REST API behavior
- Date: 2026-11-06

## Findings

### 1. Behavior of `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes`

In this repository's workflow, `Publish Release` creates Release tags with `gh release create`.
Repeated publication for the same `$UPSTREAM_TAG` therefore replaces an existing Release and its tag.
Local GitHub CLI v2.102.0 defines `--cleanup-tag` and `--yes` on `gh release delete <tag>`.
In `pkg/cmd/release/delete/delete.go:64-97`, `deleteRun` fetches the Release record and deletes the Release and its remote tag `refs/tags/$UPSTREAM_TAG`.
When no Release exists yet, `FetchRelease` returns `ErrReleaseNotFound` after HTTP 404.
Adding `2>/dev/null || true` makes `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true` a clean no-op when no Release exists.

### 2. Direct recreation with `gh release create`

After `gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true` removes the existing Release and tag, `refs/tags/$UPSTREAM_TAG` is absent.
Run `gh release create` directly with the selected assets, `--target "$SOURCE_SHA"`, `--title`, and `--generate-notes`:
```sh
gh release delete "$UPSTREAM_TAG" --cleanup-tag --yes 2>/dev/null || true
gh release create "$UPSTREAM_TAG" "${assets[@]}" \
  --target "$SOURCE_SHA" \
  --title "Sub2API-Plugin ${SOURCE_SHA:0:7} (v${UPSTREAM_TAG#v})" \
  --generate-notes
```
In `pkg/cmd/release/create/create.go:427-483`, `gh release create` with asset arguments creates a draft Release with `target_commitish` set to `$SOURCE_SHA`.
It generates the changelog for `$SOURCE_SHA`, uploads all selected assets concurrently, and publishes the Release with `PATCH /repos/{owner}/{repo}/releases/{release_id}`.
When publishing the Release, GitHub creates `refs/tags/$UPSTREAM_TAG` at `$SOURCE_SHA`, so `Source code (zip)` and `Source code (tar.gz)` match `$SOURCE_SHA`.
No separate `git push --force` command or `gh auth git-credential` helper is needed.

### 3. Evaluated `git push` alternatives

In `pkg/cmd/release/delete/delete.go:64-86`, `gh release delete` exits on HTTP 404 before `deleteTag` if an orphan tag exists without a Release.
A separate `git push --force origin "$SOURCE_SHA:refs/tags/$UPSTREAM_TAG"` or `git push --delete` would only be needed for out-of-band orphan tags.
Because `gh release create` stages a draft and only creates the tag when publishing the final Release, failed asset uploads do not leave orphan tags.
Deleting the Release and tag with `gh release delete --cleanup-tag --yes` and recreating with `gh release create --target "$SOURCE_SHA"` is sufficient.

## Files Found

- `.github/workflows/build.yml` — Parent workflow containing `Publish Release` at lines 157-192.
- `plugins/codex-candy-eval/.github/workflows/build.yml` — Evaluation plugin workflow with aligned `Publish Release` step at lines 157-192.
- `plugins/sub2api-quota-extension/.github/workflows/build.yml` — Quota plugin workflow with aligned `Publish Release` step at lines 157-192.
- `plugins/sub2api-plugin-template/.github/workflows/build.yml` — Plugin template workflow with aligned `Publish Release` step at lines 157-192.
- `.trellis/tasks/10-30-inspection-settings-attribution/prd.md` — Defines R19 and AC18 for same-tag Release deletion, tag update, and clean recreation.
- `.trellis/tasks/10-30-inspection-settings-attribution/design.md` — Defines the `Publish Release` design for all four workflows.
- `.trellis/tasks/10-30-inspection-settings-attribution/implement.md` — Lists the current work item for simplifying repeated Release publication.

## Code Patterns

- `.github/workflows/build.yml:174-192` — Current uncommitted step branches on `gh release view` instead of the two-command delete-and-create sequence.
- `.trellis/tasks/10-30-inspection-settings-attribution/prd.md:158` — R19 deletes any existing same-tag Release and tag before creating a clean Release with `gh release create`.

## External References

- [GitHub CLI v2.102.0 `pkg/cmd/release/delete/delete.go`](https://raw.githubusercontent.com/cli/cli/v2.102.0/pkg/cmd/release/delete/delete.go) — `deleteRun`, `deleteRelease`, and `deleteTag` execution order.
- [GitHub CLI v2.102.0 `pkg/cmd/release/shared/fetch.go`](https://raw.githubusercontent.com/cli/cli/v2.102.0/pkg/cmd/release/shared/fetch.go) — `FetchRelease` lookup for published and draft Releases.
- [GitHub CLI v2.102.0 `pkg/cmd/release/create/create.go`](https://raw.githubusercontent.com/cli/cli/v2.102.0/pkg/cmd/release/create/create.go) — `createRun`, `generate_release_notes`, and draft-upload-publish flow.
- [GitHub CLI v2.102.0 `pkg/cmd/release/create/http.go`](https://raw.githubusercontent.com/cli/cli/v2.102.0/pkg/cmd/release/create/http.go) — `createRelease` and `publishRelease` REST calls.
- [GitHub REST API Releases (2022-11-28)](https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28) — `target_commitish` and `generate_release_notes` contracts for `POST /repos/{owner}/{repo}/releases`.

## Related Specs

- `.trellis/spec/backend/minimal-linux-delivery.md:136-147` — Parent binary delivery specification for `Publish Release`.
- `plugins/codex-candy-eval/.trellis/spec/backend/minimal-linux-delivery.md:114-125` — Evaluation plugin binary delivery specification for `Publish Release`.

## Caveats / Not Found

- An out-of-band orphan tag without a Release is not deleted by `gh release delete --cleanup-tag` and would cause `target_commitish` to be ignored.
- If `$SOURCE_SHA` modifies `.github/workflows/` relative to the default branch, GitHub rejects tag creation with `GITHUB_TOKEN` because `GITHUB_TOKEN` lacks the `workflow` permission.
- No remote GitHub API write or test Release was executed during this research.
