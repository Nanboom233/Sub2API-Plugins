# Direct executable artifacts

## Candidate

The four build kits use the selected upstream tag in every output filename.
Server names use `sub2api-plugins-<upstream_version>-<os>-<architecture>`.
Installer names add `-installer` after `sub2api-plugins`.
Windows files add `.exe`. The current tag is `v0.2.19`.

The five platform directories remain under `dist/build/`.
Each workflow uploads ten separate executable files with `archive: false`.
The workflow derives the tag in its output validation step and supplies that step output to each upload path.
It creates no product tar archive and keeps no legacy filename aliases.
The existing failure-only diagnostic log remains separate from product outputs.

Root and template READMEs show direct downloads, versioned filenames, and Unix execution permissions.
The evaluation README remains unchanged by this revision.

## Checks

`python3 tests/test_build.py` passed all four existing cases in 9.411 seconds.
The existing composition case checks all ten versioned platform filenames.
The failure case still checks preservation of previous outputs.

The actual workflow validation shell passed against the retained combined outputs.
All ten direct upload paths resolved to separate, nonempty executable files.
The tag output record is `/tmp/sub2api-direct-artifact-check-00hm816a/output`.
All four builders, builder test files, and workflows have identical contents.
Diff formatting checks passed in all four repositories.

Native `mv` operations renamed the retained programs without recompilation.
Their sizes and executable permissions remain unchanged.
Previous runtime evidence therefore applies to the same program contents.
No remote Actions run occurred for this revision.

## Retained outputs

Paths are relative to `dist/build/`. All files have mode `0755`.

| File | Bytes |
| --- | ---: |
| `linux-amd64/sub2api-plugins-v0.2.19-linux-amd64` | 136290464 |
| `linux-amd64/sub2api-plugins-installer-v0.2.19-linux-amd64` | 52736160 |
| `linux-arm64/sub2api-plugins-v0.2.19-linux-arm64` | 126681248 |
| `linux-arm64/sub2api-plugins-installer-v0.2.19-linux-arm64` | 48169120 |
| `darwin-amd64/sub2api-plugins-v0.2.19-darwin-amd64` | 141480336 |
| `darwin-amd64/sub2api-plugins-installer-v0.2.19-darwin-amd64` | 98642464 |
| `darwin-arm64/sub2api-plugins-v0.2.19-darwin-arm64` | 132830882 |
| `darwin-arm64/sub2api-plugins-installer-v0.2.19-darwin-arm64` | 91689266 |
| `windows-amd64/sub2api-plugins-v0.2.19-windows-amd64.exe` | 139274240 |
| `windows-amd64/sub2api-plugins-installer-v0.2.19-windows-amd64.exe` | 98229248 |
