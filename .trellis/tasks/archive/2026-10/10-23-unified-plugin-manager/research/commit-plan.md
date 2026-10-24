# Work Commit Plan

The file inventory includes the substantive test refactor requested on 2026-10-25.
The native integration build, focused pipeline tests, integration vet, and final independent review passed.
Both repositories enable Git commit signing.
Use the configured signing policy without overrides.

The user approved this updated plan on 2026-10-25.
Signed work commits are `6b3d8b6` for portable integration, `9a56c08` for the plugin, and `1afe676` for the parent build.
Their signatures passed verification. Trellis archive and journal commits follow these work commits.

## Rules and Commit Order

The [ownership boundary](../../../spec/backend/quality-guidelines.md#ownership-boundary) assigns initial portable Trellis and AI integration files to reviewed work commits.
Task and workspace records use Trellis lifecycle commands after work commits.
Do not exclude portable integration files merely because they live under a hidden directory.

## 1. Portable Trellis and AI Integration

Repository: the parent repository.

Exact commit message:

```text
chore(trellis): add portable workflow and agent integrations
```

Exact file inventory (156 files):

```text
.agents/skills/trellis-before-dev/SKILL.md
.agents/skills/trellis-brainstorm/SKILL.md
.agents/skills/trellis-break-loop/SKILL.md
.agents/skills/trellis-channel/SKILL.md
.agents/skills/trellis-channel/references/command-reference.md
.agents/skills/trellis-channel/references/forum.md
.agents/skills/trellis-channel/references/progress-debugging.md
.agents/skills/trellis-channel/references/workers.md
.agents/skills/trellis-channel/references/workflows.md
.agents/skills/trellis-check/SKILL.md
.agents/skills/trellis-continue/SKILL.md
.agents/skills/trellis-finish-work/SKILL.md
.agents/skills/trellis-meta/SKILL.md
.agents/skills/trellis-meta/references/customize-local/add-project-local-conventions.md
.agents/skills/trellis-meta/references/customize-local/change-agents.md
.agents/skills/trellis-meta/references/customize-local/change-context-loading.md
.agents/skills/trellis-meta/references/customize-local/change-hooks.md
.agents/skills/trellis-meta/references/customize-local/change-skills-or-commands.md
.agents/skills/trellis-meta/references/customize-local/change-spec-structure.md
.agents/skills/trellis-meta/references/customize-local/change-task-lifecycle.md
.agents/skills/trellis-meta/references/customize-local/change-workflow.md
.agents/skills/trellis-meta/references/customize-local/overview.md
.agents/skills/trellis-meta/references/local-architecture/bundled-skills.md
.agents/skills/trellis-meta/references/local-architecture/context-injection.md
.agents/skills/trellis-meta/references/local-architecture/generated-files.md
.agents/skills/trellis-meta/references/local-architecture/multi-agent-channel.md
.agents/skills/trellis-meta/references/local-architecture/overview.md
.agents/skills/trellis-meta/references/local-architecture/spec-system.md
.agents/skills/trellis-meta/references/local-architecture/task-system.md
.agents/skills/trellis-meta/references/local-architecture/workflow.md
.agents/skills/trellis-meta/references/local-architecture/workspace-memory.md
.agents/skills/trellis-meta/references/platform-files/agents.md
.agents/skills/trellis-meta/references/platform-files/hooks-and-settings.md
.agents/skills/trellis-meta/references/platform-files/overview.md
.agents/skills/trellis-meta/references/platform-files/platform-map.md
.agents/skills/trellis-meta/references/platform-files/skills-and-commands.md
.agents/skills/trellis-session-insight/SKILL.md
.agents/skills/trellis-session-insight/references/cli-quick-reference.md
.agents/skills/trellis-session-insight/references/triggering-patterns.md
.agents/skills/trellis-spec-bootstrap/SKILL.md
.agents/skills/trellis-spec-bootstrap/references/mcp-setup.md
.agents/skills/trellis-spec-bootstrap/references/repository-analysis.md
.agents/skills/trellis-spec-bootstrap/references/spec-task-planning.md
.agents/skills/trellis-spec-bootstrap/references/spec-writing.md
.agents/skills/trellis-start/SKILL.md
.agents/skills/trellis-update-spec/SKILL.md
.codex/agents/trellis-check.toml
.codex/agents/trellis-implement.toml
.codex/agents/trellis-research.toml
.codex/config.toml
.codex/hooks.json
.codex/hooks/inject-subagent-context.py
.codex/hooks/inject-workflow-state.py
.codex/hooks/session-start.py
.gitattributes
.opencode/agents/trellis-check.md
.opencode/agents/trellis-implement.md
.opencode/agents/trellis-research.md
.opencode/commands/trellis/continue.md
.opencode/commands/trellis/finish-work.md
.opencode/commands/trellis/start.md
.opencode/lib/context-visibility.js
.opencode/lib/session-utils.js
.opencode/lib/trellis-context.js
.opencode/package.json
.opencode/plugins/inject-subagent-context.js
.opencode/plugins/inject-workflow-state.js
.opencode/plugins/session-start.js
.opencode/skills/trellis-before-dev/SKILL.md
.opencode/skills/trellis-brainstorm/SKILL.md
.opencode/skills/trellis-break-loop/SKILL.md
.opencode/skills/trellis-channel/SKILL.md
.opencode/skills/trellis-channel/references/command-reference.md
.opencode/skills/trellis-channel/references/forum.md
.opencode/skills/trellis-channel/references/progress-debugging.md
.opencode/skills/trellis-channel/references/workers.md
.opencode/skills/trellis-channel/references/workflows.md
.opencode/skills/trellis-check/SKILL.md
.opencode/skills/trellis-meta/SKILL.md
.opencode/skills/trellis-meta/references/customize-local/add-project-local-conventions.md
.opencode/skills/trellis-meta/references/customize-local/change-agents.md
.opencode/skills/trellis-meta/references/customize-local/change-context-loading.md
.opencode/skills/trellis-meta/references/customize-local/change-hooks.md
.opencode/skills/trellis-meta/references/customize-local/change-skills-or-commands.md
.opencode/skills/trellis-meta/references/customize-local/change-spec-structure.md
.opencode/skills/trellis-meta/references/customize-local/change-task-lifecycle.md
.opencode/skills/trellis-meta/references/customize-local/change-workflow.md
.opencode/skills/trellis-meta/references/customize-local/overview.md
.opencode/skills/trellis-meta/references/local-architecture/bundled-skills.md
.opencode/skills/trellis-meta/references/local-architecture/context-injection.md
.opencode/skills/trellis-meta/references/local-architecture/generated-files.md
.opencode/skills/trellis-meta/references/local-architecture/multi-agent-channel.md
.opencode/skills/trellis-meta/references/local-architecture/overview.md
.opencode/skills/trellis-meta/references/local-architecture/spec-system.md
.opencode/skills/trellis-meta/references/local-architecture/task-system.md
.opencode/skills/trellis-meta/references/local-architecture/workflow.md
.opencode/skills/trellis-meta/references/local-architecture/workspace-memory.md
.opencode/skills/trellis-meta/references/platform-files/agents.md
.opencode/skills/trellis-meta/references/platform-files/hooks-and-settings.md
.opencode/skills/trellis-meta/references/platform-files/overview.md
.opencode/skills/trellis-meta/references/platform-files/platform-map.md
.opencode/skills/trellis-meta/references/platform-files/skills-and-commands.md
.opencode/skills/trellis-session-insight/SKILL.md
.opencode/skills/trellis-session-insight/references/cli-quick-reference.md
.opencode/skills/trellis-session-insight/references/triggering-patterns.md
.opencode/skills/trellis-spec-bootstrap/SKILL.md
.opencode/skills/trellis-spec-bootstrap/references/mcp-setup.md
.opencode/skills/trellis-spec-bootstrap/references/repository-analysis.md
.opencode/skills/trellis-spec-bootstrap/references/spec-task-planning.md
.opencode/skills/trellis-spec-bootstrap/references/spec-writing.md
.opencode/skills/trellis-update-spec/SKILL.md
.trellis/.gitignore
.trellis/.version
.trellis/agents/check.md
.trellis/agents/implement.md
.trellis/config.yaml
.trellis/scripts/__init__.py
.trellis/scripts/add_session.py
.trellis/scripts/common/__init__.py
.trellis/scripts/common/active_task.py
.trellis/scripts/common/cli_adapter.py
.trellis/scripts/common/config.py
.trellis/scripts/common/developer.py
.trellis/scripts/common/git.py
.trellis/scripts/common/git_context.py
.trellis/scripts/common/io.py
.trellis/scripts/common/log.py
.trellis/scripts/common/packages_context.py
.trellis/scripts/common/paths.py
.trellis/scripts/common/safe_commit.py
.trellis/scripts/common/session_context.py
.trellis/scripts/common/task_context.py
.trellis/scripts/common/task_queue.py
.trellis/scripts/common/task_store.py
.trellis/scripts/common/task_utils.py
.trellis/scripts/common/tasks.py
.trellis/scripts/common/trellis_config.py
.trellis/scripts/common/types.py
.trellis/scripts/common/workflow_phase.py
.trellis/scripts/get_context.py
.trellis/scripts/get_developer.py
.trellis/scripts/hooks/linear_sync.py
.trellis/scripts/init_developer.py
.trellis/scripts/task.py
.trellis/spec/frontend/component-guidelines.md
.trellis/spec/frontend/directory-structure.md
.trellis/spec/frontend/hook-guidelines.md
.trellis/spec/frontend/index.md
.trellis/spec/frontend/quality-guidelines.md
.trellis/spec/frontend/state-management.md
.trellis/spec/frontend/type-safety.md
.trellis/spec/guides/code-reuse-thinking-guide.md
.trellis/spec/guides/cross-layer-thinking-guide.md
.trellis/spec/guides/index.md
.trellis/workflow.md
AGENTS.md
```

The current backend contracts stay with the parent build work in commit 3.

## 2. Evaluation Plugin

Repository: `plugins/codex-candy-eval`.

Exact commit message:

```text
feat(build): support automatic Sub2API v0.2.18 composition
```

Staged modified or added files:

```text
.gitattributes
.github/workflows/release.yml
.trellis/spec/backend/database-guidelines.md
.trellis/spec/backend/directory-structure.md
.trellis/spec/backend/error-handling.md
.trellis/spec/backend/index.md
.trellis/spec/backend/logging-guidelines.md
.trellis/spec/backend/minimal-linux-delivery.md
.trellis/spec/backend/native-inspection.md
.trellis/spec/backend/quality-guidelines.md
.trellis/spec/backend/runtime-installation.md
README.md
patches/0004-admin-channel.patch
patches/0007-sub2api-integration.patch
scripts/build.py
scripts/installer/main.go
tests/support.py
```

Deletions:

```text
licenses/THIRD_PARTY_NOTICES.txt
patches/series
tests/installer/installer_test.go
```

Staged renames:

```text
tests/backend/internal/codexeval/candy_test.go -> tests/test_codexeval_candy_test.go
tests/backend/internal/codexeval/codex_test.go -> tests/test_codexeval_codex_test.go
tests/backend/internal/codexeval/fingerprint_test.go -> tests/test_codexeval_fingerprint_test.go
tests/backend/internal/codexeval/inspection_test.go -> tests/test_codexeval_inspection_test.go
tests/backend/internal/codexeval/model_test.go -> tests/test_codexeval_model_test.go
tests/backend/internal/codexeval/pelican_test.go -> tests/test_codexeval_pelican_test.go
tests/backend/internal/codexeval/runtime_test.go -> tests/test_codexeval_runtime_test.go
tests/backend/internal/handler/admin/codex_inspection_handler_test.go -> tests/test_admin_codex_inspection_handler_test.go
tests/backend/internal/service/account_codex_eval_service_test.go -> tests/test_service_account_codex_eval_service_test.go
tests/backend/internal/service/codex_eval_lifetime_test.go -> tests/test_service_codex_eval_lifetime_test.go
tests/backend/internal/service/codex_inspection_models_test.go -> tests/test_service_codex_inspection_models_test.go
tests/backend/internal/service/codex_inspection_settings_test.go -> tests/test_service_codex_inspection_settings_test.go
tests/backend/internal/codexeval/testdata/lm-detector-golden.json -> assets/lm-detector-golden.json
tests/ui/sub2api-dropdowns.cjs -> tests/test_ui.cjs
tests/installer/native_fixture_start.sh -> tests/native_fixture_start.sh
tests/installer/native_fixture_supplier.py -> tests/native_fixture_supplier.py
tests/installer/native_inspection_fixture.py -> tests/native_inspection_fixture.py
```

The parent owns the single installer suite. The plugin retains its standalone build and installer source.
Wrapper entries `tests/test_backend.go` and `tests/test_ui.py` are absent from the final inventory.
`assets/` contains only the golden JSON data. All actual test cases and support code remain in flat `tests/`.

## 3. Parent Build

After the plugin commit, stage its resulting revision in the parent gitlink.

Exact commit message:

```text
feat(build): build all plugin submodules and package installer
```

Staged files:

```text
.github/workflows/release.yml
.gitignore
.gitmodules
.trellis/spec/backend/database-guidelines.md
.trellis/spec/backend/directory-structure.md
.trellis/spec/backend/error-handling.md
.trellis/spec/backend/index.md
.trellis/spec/backend/logging-guidelines.md
.trellis/spec/backend/minimal-linux-delivery.md
.trellis/spec/backend/native-inspection.md
.trellis/spec/backend/quality-guidelines.md
.trellis/spec/backend/runtime-installation.md
LICENSE
licenses/Sub2API-LGPL-3.0.txt
plugins/codex-candy-eval
scripts/build.py
scripts/installer/main.go
tests/support.py
tests/test_build.py
tests/test_installer_test.go
```

The plugin gitlink will name commit 2 instead of the original `1464080` revision.
Both repositories remove `THIRD_PARTY_NOTICES.txt`. The installer includes the original license files without a separate summary document.

## 4. Task Archive

Repository: the parent repository. Trellis creates this commit through its native archive command.

```sh
python3 .trellis/scripts/task.py archive 10-23-unified-plugin-manager
```

Generated commit message:

```text
chore(task): archive 10-23-unified-plugin-manager
```

Destination: `.trellis/tasks/archive/2026-10/10-23-unified-plugin-manager/`.
The task becomes completed. The archive contains these files:

```text
check.jsonl
design.md
implement.jsonl
implement.md
prd.md
research/check-result.md
research/commit-plan.md
research/implementation-result.md
research/installer-version-detection.md
research/multi-plugin-composition.md
research/source-build-flow.md
task.json
```

Do not archive `00-bootstrap-guidelines`, which remains incomplete.

## 5. Session Journal

Repository: the parent repository. Trellis creates this commit through its native session command.

```sh
python3 .trellis/scripts/add_session.py \
  --title "Automatic plugin build and installer" \
  --commit "<portable-commit>,<plugin-commit>,<parent-build-commit>" \
  --commit-subject "<portable-commit>=chore(trellis): add portable workflow and agent integrations" \
  --commit-subject "<plugin-commit>=feat(build): support automatic Sub2API v0.2.18 composition" \
  --commit-subject "<parent-build-commit>=feat(build): build all plugin submodules and package installer" \
  --summary "Migrate portable Trellis files and complete the automatic Sub2API v0.2.18 plugin build. The default build and independent review passed."
```

Use the actual work commit IDs. The explicit subjects identify the plugin commit across repositories.
Generated commit message, from the current configuration:

```text
chore: record journal
```

Workspace files:

```text
.trellis/workspace/sub2api-plugins/index.md
.trellis/workspace/sub2api-plugins/journal-1.md
```

The journal records the work commits, build evidence, independent review, and remaining remote publication step.
Keep default lifecycle auto-commit enabled. Do not require another ordinary-commit approval for these generated records.

## Excluded Files and Operations

Keep developer identity, session pointers, `.trellis/.runtime/`, caches, credentials, and machine-only settings local.
Keep `.trellis/.template-hashes.json` as local update state.
Keep `dist/` outside source commits.
The incomplete `.trellis/tasks/00-bootstrap-guidelines/` is outside this task's archive.
The existing `.trellis/workspace/index.md` remains unchanged and outside these commit scopes.
No unmatched work files were found outside the listed scopes and these exclusions.
Create signed commits with the current Git settings. Do not amend or push.
Remote checkout reproduction still requires publication of the plugin revision.

## Evidence

- [Implementation result](./implementation-result.md)
- [Independent check](./check-result.md)
