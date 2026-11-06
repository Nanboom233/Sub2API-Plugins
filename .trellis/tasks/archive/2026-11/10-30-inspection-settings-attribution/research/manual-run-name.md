# Research: Manual Workflow Run Name

- Query: Does GitHub provide a built-in dispatch parameter that sets a run name from the selected ref's latest commit subject?
- Scope: External, official GitHub documentation.
- Date: 2026-11-05.

## Findings

GitHub evaluates `run-name` before jobs start. Its allowed contexts are `github`, `inputs`, and `vars`. It cannot read step or job outputs. See the official [context availability table](https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability).

The manual `workflow_dispatch` event provides a ref and user inputs. GitHub sets `GITHUB_SHA` to the last commit on the selected branch or tag. The documented webhook payload has `ref` and `inputs`, but no commit subject. See the [manual trigger event reference](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch) and [webhook payload](https://docs.github.com/en/webhooks/webhook-events-and-payloads#workflow_dispatch).

The dispatch REST endpoint accepts `ref` and declared `inputs`. It has no run-name field. The [GitHub CLI command](https://cli.github.com/manual/gh_workflow_run) exposes ref and workflow-input flags, but no run-name flag. The [workflow run REST API](https://docs.github.com/en/rest/actions/workflow-runs) supports viewing, rerunning, canceling, and reading logs. It documents no endpoint to change a run name after creation.

The workflow syntax says that an omitted `run-name` uses event-specific information. It gives push commit messages and pull request titles as examples. It does not document a commit subject for manual dispatch. See [workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#run-name).

## Support Boundary

GitHub provides a YAML `run-name` key, but no built-in dispatch parameter that sets it to a commit subject. The Actions form, `gh workflow run`, and the dispatch REST endpoint cannot pass this value unless the workflow declares an input. The current manual event exposes the selected ref and commit SHA, not its subject.

Do not reference `github.event.head_commit.message` for this trigger. Do not treat a later step title or job log as the workflow run title. No supported API renames the run after creation.

## Files Found

| Source | Relevant contract |
| --- | --- |
| [Workflow syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#run-name) | Describes run-name and default event-specific titles. |
| [Context availability](https://docs.github.com/en/actions/learn-github-actions/contexts#context-availability) | Restricts run-name to github, inputs, and vars. |
| [Events reference](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch) | Defines the manual ref, inputs, and selected-ref commit SHA. |
| [Webhook payload](https://docs.github.com/en/webhooks/webhook-events-and-payloads#workflow_dispatch) | Lists workflow_dispatch payload fields without a commit subject. |
| [Dispatch REST endpoint](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event) | Accepts a ref and declared inputs. |
| [GitHub CLI `gh workflow run`](https://cli.github.com/manual/gh_workflow_run) | Accepts a ref and declared inputs through flags or JSON. It has no run-name flag. |
| [Workflow run REST API](https://docs.github.com/en/rest/actions/workflow-runs) | Lists run operations without a run-name update operation. |

## Caveats / Not Found

The selected commit SHA is available. The workflow expression language cannot call the commit API to resolve its subject before `run-name` evaluation.
The documentation does not promise what event-specific default title a manual run receives when `run-name` is omitted. Do not rely on that default to show the commit subject.
This was a read-only contract check. No workflow run or input was changed to test the UI.
