# Research: Codex evaluation model-control defaults

- Query: Audit the default degraded model removal list for Codex Candy evaluation.
- Scope: Mixed. Inspect plugin patches, tests, specifications, and Sub2API v0.2.23 model catalogs.
- Date: 2026-11-18

## Findings

### Current owner arrays

The backend default already contains `gpt-6.1-terra`. It does not contain `gpt-6.2-sol`.

| Owner | Current value | Evidence |
| --- | --- | --- |
| `plugins/codex-candy-eval/patches/0005-inspection.patch` | `["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra"]` | `0005-inspection.patch:941` |
| Backend settings test | `["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra"]` | `tests/test_service_codex_inspection_settings_test.go:105` |
| Embedded UI test fixture | `["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra"]` | `tests/test_ui.cjs:19` |
| Inspection runtime test | No literal array. It checks `DegradedRemoveModels[0] == "gpt-6.1-sol"`. | `tests/test_codexeval_inspection_test.go:545` |
| Native inspection specification | `["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra"]` | `.trellis/spec/backend/native-inspection.md:58` |

The other plugin patches define no removal-list default. Patch `0006` starts the hidden field with `[]` at `0006-evaluation-ui.patch:2833`.
The page replaces it with the server response at `0006-evaluation-ui.patch:1467`. The server remains the only default owner.

Patch `0002` contains `gpt-6.1-terra` in its static evaluation model catalog at `0002-evaluation-data.patch:76358`.
It contains no `gpt-6.2-sol` occurrence. This catalog is separate from the settings default.

### Upstream v0.2.23 model evidence

The v0.2.23 upstream model catalogs support both requested identifiers.

- `frontend/src/composables/useModelWhitelist.ts:13-16` lists `gpt-6.2-sol` and `gpt-6.1-terra` in `openaiModels`.
- `frontend/src/composables/useModelWhitelist.ts:362-363` defines display entries for both models.
- `backend/internal/pkg/openai/constants.go:22-34` includes both IDs in `DefaultModels`.
- `backend/resources/model-pricing/model_prices_and_context_window.json:2` defines pricing for `gpt-6.1-terra`.
- `backend/resources/model-pricing/model_prices_and_context_window.json:47` defines pricing for `gpt-6.2-sol`.
- `backend/internal/pkg/openai/codex_gpt61_terra.json:2` identifies the Terra Codex descriptor.
- `backend/internal/pkg/openai/codex_gpt62_sol.json:2` identifies the Sol Codex descriptor.

The v0.2.23 upstream catalog therefore does not require a new model identifier or catalog entry. The plugin default list only needs the missing `gpt-6.2-sol` item.

### Normalization, validation, and empty-list behavior

`DefaultInspectionSettings` supplies the five current models at `0005-inspection.patch:941`.
`NormalizeModels` selects defaults only when `DegradedRemoveModels == nil` at `0005-inspection.patch:992`.
It trims each model and removes duplicates by first occurrence at `0005-inspection.patch:997-1001`.
The function preserves input order. It does not sort the saved removal list.

`ValidInspectionRemovalModel` rejects wildcard characters and `blacklist` at `0005-inspection.patch:1007`.
`Validate` applies that rule to each configured model at `0005-inspection.patch:1018-1021`.
An empty string fails the existing model-name validation.

`GetCodexInspectionSettings` starts from defaults at `0005-inspection.patch:1411` and overlays stored keys at `0005-inspection.patch:1422-1427`.
An absent setting keeps the default list. A stored JSON `[]` decodes as a non-nil empty slice and remains empty after normalization.
The backend test asserts this behavior at `tests/test_service_codex_inspection_settings_test.go:153-164`.

The UI serializes the server list into the hidden field at `0006-evaluation-ui.patch:1467`.
The model picker deduplicates and sorts display options at `0006-evaluation-ui.patch:1747`.
Custom entry avoids exact duplicates before saving at `0006-evaluation-ui.patch:1764`.
The tag renderer preserves stored order at `0006-evaluation-ui.patch:1510`.

### Smallest required change set

Preserve the existing five-item order and append `gpt-6.2-sol`.
This keeps the current defaults stable and makes the new item explicit.

1. Add `"gpt-6.2-sol"` to the array at `plugins/codex-candy-eval/patches/0005-inspection.patch:941`.
2. Append the same item to the expected array at `tests/test_service_codex_inspection_settings_test.go:105`.
3. Append the same item to the UI fixture at `tests/test_ui.cjs:19`.
4. Append the same item to the specification table at `.trellis/spec/backend/native-inspection.md:58`.

The exact backend array after the change should be:

```text
["gpt-6.1-sol", "gpt-6-sol", "gpt-5.6-sol", "gpt-6-astra", "gpt-6.1-terra", "gpt-6.2-sol"]
```

The backend settings test compares the full array. The UI test compares rendered tags at `tests/test_ui.cjs:500`.
It compares submitted values at `tests/test_ui.cjs:559`.
Those assertions cover the required default propagation after the fixture update.
The runtime test checks only the first item at `tests/test_codexeval_inspection_test.go:545`.
The backend and UI tests already provide full-array coverage.

No change is required in `0006-evaluation-ui.patch:2833`, because `[]` is the form bootstrap value and the server owns defaults.
No change is required in `0002-evaluation-data.patch` for the model-control requirement. Its static catalog is independent of `degraded_remove_models`.

## Files found

- `plugins/codex-candy-eval/patches/0005-inspection.patch`: Defines inspection settings, defaults, normalization, and validation.
- `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch`: Defines embedded settings UI, list rendering, and model picker behavior.
- `plugins/codex-candy-eval/patches/0002-evaluation-data.patch`: Embeds the evaluation model catalog.
- `plugins/codex-candy-eval/tests/test_service_codex_inspection_settings_test.go`: Checks settings defaults, persistence, normalization, and empty-list behavior.
- `plugins/codex-candy-eval/tests/test_service_codex_inspection_models_test.go`: Checks degraded removal, deduplication, restoration, and empty-list skips.
- `plugins/codex-candy-eval/tests/test_codexeval_inspection_test.go`: Checks runtime settings passed to inspection rounds.
- `plugins/codex-candy-eval/tests/test_ui.cjs`: Checks UI defaults, tags, custom models, and submitted settings.
- `.trellis/spec/backend/native-inspection.md`: Records the inspection settings contract and default list.
- `/tmp/sub2api-v0.2.23-research/frontend/src/composables/useModelWhitelist.ts`: Lists upstream OpenAI model IDs and display entries.
- `/tmp/sub2api-v0.2.23-research/backend/internal/pkg/openai/constants.go`: Lists upstream default OpenAI models.
- `/tmp/sub2api-v0.2.23-research/backend/resources/model-pricing/model_prices_and_context_window.json`: Defines upstream pricing entries.
- `/tmp/sub2api-v0.2.23-research/backend/internal/pkg/openai/codex_gpt61_terra.json`: Defines the Terra Codex descriptor.
- `/tmp/sub2api-v0.2.23-research/backend/internal/pkg/openai/codex_gpt62_sol.json`: Defines the Sol Codex descriptor.

## Related specs

- `.trellis/spec/backend/native-inspection.md`
- `.trellis/spec/guides/index.md`
- `.trellis/tasks/11-08-quota-scheduling-and-probe-memo/prd.md`

## Caveats / Not Found

- The plugin workspace contains no `gpt-6.2-sol` occurrence before the required default change.
- `gpt-6.1-terra` already satisfies its part of the requirement in the backend default, test fixture, and specification.
- This research made no plugin, test, or specification edits outside this research file.
