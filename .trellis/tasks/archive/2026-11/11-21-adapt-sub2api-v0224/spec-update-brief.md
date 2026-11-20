# Phase 3.3 Spec Synchronization Brief

Active tasks to synchronize:
- Parent: `.trellis/tasks/11-20-gemini-thought-signature-rectifier` (`plugins/gemini-signature-rectifier`)
- Child: `.trellis/tasks/11-21-adapt-sub2api-v0224` (`plugins/sub2api-quota-extension` unified `v0.2.24` adaptation)
Callback terminal: `t53` (report completion or blockers via `hc send t53 "<concise summary>"`).
Subagent rule: prevent any internal subagent from running `hc send`.

## Scope & Hard Boundaries

- **Phase 3.3 `.trellis/spec/` updates ONLY**.
- Do **NOT** modify any plugin code, patch, test, README, `.gitmodules`, `dist/`, or Git staging/commit state.
- Do **NOT** run `task.py archive`, `add_session.py`, `git add`, `git commit`, `git push`, `gh`, or any product build (spec-only changes require no product build per `.trellis/spec/backend/quality-guidelines.md:25`).
- Follow `.trellis/spec/backend/index.md#documentation-rules` strictly:
  - English prose, active voice, short sentences, common words, one name per concept.
  - Limit instructions to 20 words and descriptions to 25 words; one instruction per sentence; NO semicolons; NO contractions; max 6 sentences per paragraph.
  - Cite real repository files, patches, and tests only; preserve historical mentions (e.g., `v0.2.17`, workflow input defaults, historical notes) accurately without mechanical global replace.
- Follow `.agent/skills/trellis-update-spec/SKILL.md`: include all 7 mandatory code-spec sections for the new cross-layer Gemini signature rectifier contract (`Scope / Trigger`, `Signatures`, `Contracts`, `Validation & Error Matrix`, `Good / Base / Bad Cases`, `Tests Required`, `Wrong vs Correct`).

## Required Spec Updates

1. **New backend code-spec**: `.trellis/spec/backend/gemini-signature-rectifier.md`
   - Capture the verified executable contract of `plugins/gemini-signature-rectifier` (`patches/gemini-signature-rectifier.patch` + 4 flat test suites):
     - Scope: `ForwardNative` across all 4 builders (API Key/relay, OAuth AI Studio, OAuth Code Assist `/v1internal`, Vertex ServiceAccount); excludes Claude `Forward`, handler pre-cleaning, Antigravity `ForwardGemini`, exported `CleanGeminiNativeThoughtSignatures`, and `estimateGeminiCountTokens`.
     - Signatures: `isGeminiNativeSignatureRelatedError`, `cleanGeminiNativeThoughtSignaturesForRetry`, `SettingService.IsGeminiNativeSignatureRectifierEnabled(ctx)`, `RectifierSettings.GeminiNativeSignatureEnabled` (`gemini_native_signature_enabled`), admin GET/PUT plain-bool contract, and `SettingsView.vue` native toggle row.
     - Contracts: cached-content → configured error policy → unmatched signature HTTP 400; max 1 recovery resend independent of ordinary `maxAttempts`; 4-rule direct-Part `json.RawMessage` cleaner; `rateLimitService.settingService` access without changing constructors/`wire_gen.go`; default `false` & read-error `false`; Option B `countTokens`; verified Ops kinds (`signature_error`, `signature_retry` on HTTP `>=400`, `signature_retry_request_error`) with immediate `isSignatureRetryAttempt` reset and cancellation propagation.
     - Validation & Error Matrix, Good/Base/Bad Cases, Tests Required (citing the 4 flat suites + Chromium check), and Wrong vs Correct pairs.
2. **Backend specs (baseline `v0.2.24` + new plugin + unified quota contract)**:
   - `.trellis/spec/backend/index.md`: update verified baseline to `Sub2API v0.2.24`; add `Gemini Native Signature Rectifier` row linking `./gemini-signature-rectifier.md`.
   - `.trellis/spec/backend/directory-structure.md`: document `plugins/gemini-signature-rectifier` and its `patches/gemini-signature-rectifier.patch` + 4 flat suites alongside eval and quota plugins.
   - `.trellis/spec/backend/quality-guidelines.md`: update verified baseline to `Sub2API v0.2.24`.
   - `.trellis/spec/backend/api-key-quota.md`: update verified baseline to `v0.2.24`, document unified `buildAccountUsageRefreshKey` + single `{ data, ts, refreshKey }` caches + current-key reply checks + `tests/test_usage_batch.test.ts` (replacing obsolete separate `buildAPIKeyUsageRefreshKey` / `config` cache statements if present).
   - `.trellis/spec/backend/runtime-installation.md` & `.trellis/spec/backend/minimal-linux-delivery.md`: update verified baseline statements to `v0.2.24` ONLY where describing the current verified delivery baseline (do NOT alter historical records or unchanged workflow input defaults).
3. **Frontend specs (unified `v0.2.24` refresh architecture + Gemini rectifier settings UI)**:
   - `.trellis/spec/frontend/index.md`: add link to `../backend/gemini-signature-rectifier.md` for native rectifier settings UI contract.
   - `.trellis/spec/frontend/directory-structure.md`: add `plugins/gemini-signature-rectifier/` layout, add `test_usage_batch.test.ts` under `plugins/sub2api-quota-extension/tests/`, and list the patched rectifier settings files (`api/admin/settings.ts`, `views/admin/SettingsView.vue`, `i18n/locales/{en,zh}/admin/settings.ts`).
   - `.trellis/spec/frontend/hook-guidelines.md`: replace obsolete `buildAPIKeyUsageRefreshKey` example and wording with the verified extended `buildAccountUsageRefreshKey` + `hasQuotaScript` contract.
   - `.trellis/spec/frontend/state-management.md`: replace obsolete `{ data, ts, config }` and `apiKeyUsageRefreshKey` watcher example with verified `{ data, ts, refreshKey }`, unified `usageRefreshKey` watcher, and single/batch current-key reply checks.
   - `.trellis/spec/frontend/type-safety.md`: replace any stale `buildAPIKeyUsageRefreshKey` reference if present; keep accurate.
   - `.trellis/spec/frontend/component-guidelines.md` / `quality-guidelines.md`: check if any stale reference to `buildAPIKeyUsageRefreshKey` or `v0.2.23` exists; update only if actually stale.

## Verification Before Callback

- Run `rg -n 'buildAPIKeyUsageRefreshKey|apiKeyUsageRefreshKey|capturedConfigByAccountId|\{ data, ts, config \}' .trellis/spec/` and confirm **0 matches**.
- Verify every relative markdown link and anchor in all created/edited `.trellis/spec/` files resolves to a real existing file/heading (using `PYTHONDONTWRITEBYTECODE=1 python3 -B`).
- Verify every edited/created spec obeys the documentation rules (no semicolons, no contractions, concise active sentences, real file citations).
- Verify `git status --short` shows ONLY `.trellis/spec/` changes beyond pre-existing task work (zero plugin/patch/test/Git commit edits, zero new `.pyc`).

Report exact modified/created spec files and verification results via `hc send t53`.
