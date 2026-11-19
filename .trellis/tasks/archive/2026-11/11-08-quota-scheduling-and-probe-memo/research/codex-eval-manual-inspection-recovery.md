# Research: Codex Candy Eval Manual Inspection & Recovery Bug Investigation (`手动巡检没有参与恢复过程`)

- **Query**: Investigate why manual inspection / manual evaluation in `plugins/codex-candy-eval` does not participate in (or fails to complete) the recovery process for degraded accounts (`手动巡检没有参与恢复过程`), with exact `file:line` anchors across all patches and specs.
- **Scope**: Read-only investigation of `plugins/codex-candy-eval/patches/0001-evaluation-core.patch`, `0004-admin-channel.patch`, `0005-inspection.patch`, `0006-evaluation-ui.patch`, `0007-sub2api-integration.patch`, `tests/test_codexeval_inspection_test.go`, `tests/test_ui.cjs`, `.trellis/spec/backend/native-inspection.md`, and `/tmp/cpa-upstream-v0.4.6/`.
- **Date**: 2026-11-08

---

## 1. Files Found

- `plugins/codex-candy-eval/patches/0001-evaluation-core.patch` — Defines `codexeval.Start()`, `start()`, `startChecked()`, `runCandyChecked()`, and `runFingerprintChecked()` (`backend/internal/codexeval/runtime.go`, `candy.go`, `fingerprint.go`).
- `plugins/codex-candy-eval/patches/0004-admin-channel.patch` — Defines `AccountHandler.CodexEvalStart` (`POST /api/v1/admin/codex-eval/start`) and `AccountTestService.SendCodexEvaluation` (`backend/internal/handler/admin/account_codex_eval_handler.go`, `backend/internal/service/account_codex_eval_service.go`).
- `plugins/codex-candy-eval/patches/0005-inspection.patch` — Defines `inspector.start()`, `inspector.startRun(automatic bool)`, `inspector.run()`, `inspector.applyAccount()`, `inspector.testPhase()`, `inspectionEligible()`, `AccountHandler.CodexInspectionStart` (`POST /api/v1/admin/codex-eval/inspection/start`), and `AccountTestService.PersistCodexInspectionVerdict()` (`backend/internal/codexeval/inspection.go`, `backend/internal/handler/admin/codex_inspection_handler.go`, `backend/internal/service/codex_inspection_models.go`).
- `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch` — Defines manual row/batch test handlers (`web/candy.js`, `web/fingerprint.js`, `web/app.js`), the `降级` row badge (`web/components.js`), and the `设置` tab `立即巡检` (`#inspection-start`) / `loadInspectionState()` flow (`web/inspection.js`, `web/ui.html`).
- `plugins/codex-candy-eval/patches/0007-sub2api-integration.patch` — Registers `/api/v1/admin/codex-eval/*` routes and preserves `codex_eval_inspection_*` keys in `adminServiceImpl.UpdateAccount`.
- `plugins/codex-candy-eval/tests/test_codexeval_inspection_test.go` — Unit tests for inspection confirmation, recovery, and participation boundaries.
- `.trellis/spec/backend/native-inspection.md` — Specification for native Candy and Fingerprint inspection.

---

## 2. Root-Cause Analysis by Subsystem (with Exact `file:line` Anchors)

There are **two distinct entry points** that users refer to as "手动巡检" (manual inspection/testing), and **both** exhibit defects that prevent or stall recovery of a degraded (`降级`) account:

1. **Path A — Manual Evaluation on the `糖果` (Candy) / `指纹` (Fingerprint) Tabs (`测试` / `测试所选` / `测试全部` -> `POST /api/v1/admin/codex-eval/start`)**: Completely isolated from the inspection verdict, model-restoration, and priority-recovery pipeline.
2. **Path B — Manual Immediate Inspection on the `设置` (Settings) Tab (`立即巡检` `#inspection-start` -> `POST /api/v1/admin/codex-eval/inspection/start`)**: Shares `inspector.run()` with background scheduled inspection without distinguishing manual vs. automatic trigger, causing a 240-second hidden `recovery_wait` in Candy mode, premature `Done = Total` (`1/1`) completion reporting, missing account-list refresh on completion in the UI, and exclusion of accounts whose `启用自动巡检` (`AutoInspectionEnabled`) switch is off.

---

### 2.1 Path A: Manual Tests on `糖果` / `指纹` Tabs Never Participate in Recovery (`POST /api/v1/admin/codex-eval/start`)

1. **How Degraded State Is Displayed on `糖果` / `指纹` Tabs**:
   - In `plugins/codex-candy-eval/patches/0006-evaluation-ui.patch:1049-1054` (`backend/internal/codexeval/web/components.js`), `credentialView(a, open)` renders the account row tags on all evaluation tabs (`糖果`, `指纹`, `鹈鹕`, `SIWC`):
     ```js
     <span class="tag"><span>${a.priority == null ? "—" : "P" + esc(a.priority)}</span></span>${a.extra?.codex_eval_inspection_verdict === "degraded" ? '<span class="tag"><span>降级</span></span>' : ""}
     ```
   - When an account has been degraded by inspection (`PersistCodexInspectionVerdict` at `0005-inspection.patch:1283-1364` and `UpdatePriority` at `0005-inspection.patch:617, 1217-1219`):
     - `account.Extra["codex_eval_inspection_verdict"]` is `"degraded"` (showing the `降级` badge on the row).
     - `account.Extra["codex_eval_inspection_removed_models"]` holds removed model IDs, and `account.Credentials["model_mapping"]` has those models removed or replaced with `{"blacklist": "blacklist"}` (`0005-inspection.patch:1312-1327`).
     - `account.Priority` is set to `DegradedPriority` (default `99`, showing `P99`).

2. **What Happens When the User Manually Tests a Degraded Account on `糖果` or `指纹`**:
   - Clicking a row's `测试` button (`[data-candy-run]` at `0006-evaluation-ui.patch:708, 763-764`; `[data-fp-run]` at `0006-evaluation-ui.patch:535-536, 1102`) or toolbar `测试全部` / `测试所选` (`#run-batch` / `#fp-run-batch` at `0006-evaluation-ui.patch:625-629`) calls `runCandy()` (`0006-evaluation-ui.patch:715-719`) or `runFingerprint()` (`0006-evaluation-ui.patch:1401-1405`).
   - Both send `POST /api/v1/admin/codex-eval/start` (`AccountHandler.CodexEvalStart` in `0004-admin-channel.patch:53-65`).
   - `CodexEvalStart` calls `codexeval.Start(c.Request.Context(), req)` (`0001-evaluation-core.patch:1895-1897`), which calls `start(ctx, req, false)` -> `startChecked(ctx, req, false, nil)` (`0001-evaluation-core.patch:1899-2009`).
   - Inside `startChecked` (`0001-evaluation-core.patch:1990-2006`), the worker goroutine executes:
     - `runCandyChecked(a, req.Model, req.Effort, req.Runs, beforeSend)` (`0001-evaluation-core.patch:48-81`), which only appends `r` to `candyResults[id]` and saves `history.json` (`saveStateLocked()`).
     - Or `runFingerprintChecked(runCtx, a, req.Model, fpProgress, beforeSend)` (`0001-evaluation-core.patch:509-531`), which only appends `r` to `fingerprintResults[auth.ID]` and saves `history.json`.
   - **Zero Recovery Participation**:
     - `startChecked` (`inspection == false`) **never** interacts with `inspection` (`0005-inspection.patch:85`), **never** calls `PersistCodexInspectionVerdict` (`0005-inspection.patch:1283`), and **never** calls `UpdatePriority` (`0005-inspection.patch:1217`).
     - Even if the degraded account answers `21` (`r.OK == true`, whether 1 time or `max_tests_per_account` times) on the `糖果` tab, or attributes to the expected model (`FingerprintModelID(r.Model) == FingerprintModelID(r.Attribution.Prediction)`) on the `指纹` tab:
       1. `extra.codex_eval_inspection_verdict` remains `"degraded"` (the **`降级`** badge stays on the account row).
       2. `extra.codex_eval_inspection_removed_models` is **not** restored to `credentials.model_mapping`, and `{"blacklist": "blacklist"}` is **not** removed, so the account remains blocked from normal gateway traffic for those models.
       3. `account.Priority` remains at `DegradedPriority` (`99`) instead of recovering to `NormalPriority` (`10`).
       4. No recovery notification (`降级 → 正常`) is sent.
   - Note: This separation was previously codified in `.trellis/spec/backend/native-inspection.md:8, 193` (`Read the saved verdict for both scheduled and immediate rounds. Manual tests do not change it.`) and `plugins/codex-candy-eval/README.md:93` (`定时巡检和「立即巡检」会应用这些设置。手动单账户和批量测试不会应用这些设置。`).

---

### 2.2 Path B: Manual Immediate Inspection (`立即巡检` `#inspection-start` -> `POST /api/v1/admin/codex-eval/inspection/start`) Recovery Issues

Even when the user goes to the `设置` tab and clicks **`立即巡检`** (`#inspection-start`, `0006-evaluation-ui.patch:2845`), which calls `POST /api/v1/admin/codex-eval/inspection/start` (`AccountHandler.CodexInspectionStart` at `0005-inspection.patch:1254-1260` -> `codexeval.StartInspection()` at `0005-inspection.patch:130-135` -> `inspector.start()` at `0005-inspection.patch:240-242` -> `inspector.startRun(false)` at `0005-inspection.patch:251-280`), four issues affect recovery:

#### Issue B1: `startRun(false)` (`立即巡检`) Enforces a 240-Second (`4 min`) `recovery_wait` in Candy Mode While Reporting `账户进度：N/N` Done After the First Test
- In `0005-inspection.patch:251-280`, `startRun(automatic bool)` only uses `automatic` at line 254 (`if automatic && (!i.settings.Enabled || ...)`), and then launches `go i.run(ctx, i.settings, i.runDone)` (`line 277`) without passing `automatic`.
- In `inspector.run()` (`0005-inspection.patch:474-540`):
  1. Phase 1 runs `first := i.testPhase(ctx, s, eligible, 1, false, ...)` (`line 474`).
  2. When a degraded account (`current.Verdict == InspectionVerdictDegraded`) answers `21` (`answers[0] == true`) in `candy` mode (`testType == "candy"`):
     - Line 476 sets `r.Outcome = "unchanged"`.
     - Line 491 checks `if (current.Verdict == InspectionVerdictDegraded) == !answers[0]` (`true == false` -> `false`).
     - Line 500 appends `a` to `groups[s.NormalPriority]`.
  3. Meanwhile, inside `testPhase()` (`0005-inspection.patch:782-785`), as soon as the 1st test finishes:
     ```go
     if step == batches-1 {
         i.mu.Lock()
         i.state.Done = i.state.Total - len(tracked) + len(finished)
         i.mu.Unlock()
     }
     ```
     `i.state.Done` is immediately set to `i.state.Total` (e.g., `账户进度：1/1`), and the worker deletes `active[id]` (`0001-evaluation-core.patch:1992`).
  4. Next, at `0005-inspection.patch:504-514`:
     ```go
     for _, target := range []int{s.DegradedPriority, s.NormalPriority} {
         group := groups[target]
         if len(group) == 0 {
             continue
         }
         if target == s.NormalPriority && s.MaxTestsPerAccount > 1 {
             i.phase("recovery_wait")
             if !waitInspection(ctx, i.recovery) {
                 return
             }
         }
     ```
     - Whereas degradation (`target == s.DegradedPriority`) runs its `MaxTestsPerAccount - 1` (`2`) confirmation tests **immediately**, recovery (`target == s.NormalPriority`) enters `phase = "recovery_wait"` and blocks for **`i.recovery = 240 * time.Second` (4 full minutes)** (`0005-inspection.patch:97, 511`) even during a manual `立即巡检` (`automatic == false`)!
     - During those 240 seconds:
       - On the `设置` tab (where the user clicked `立即巡检`), there is **no phase or progress text** (`#inspection-status` is rendered inside `#candy-credentials` or `#fp-credentials`, not `#settings-panel`, `0006-evaluation-ui.patch:1483-1490`).
       - On the `糖果` tab, the account row's spinner has stopped (`active[id]` is `nil`), the row button is back to `测试`, the latest Candy result shows **`答对`** (`21`), and `#inspection-progress` shows **`账户进度：1/1`**, yet the account still shows **`降级`** and `P99`!
       - Because `active[id]` is `nil` during the 240-second `recovery_wait`, the account's manual `测试` button is enabled; if the user clicks `测试` (or `停止当前巡检`) during those 4 minutes, the recovery confirmation fails or is cancelled.

#### Issue B2: Frontend `loadInspectionState()` Never Refreshes `accountList` (`/api/v1/admin/accounts`) When an Inspection Round Finishes
- Look at the `立即巡检` click handler in `0006-evaluation-ui.patch:1952-1964` (`backend/internal/codexeval/web/inspection.js`):
  ```js
  for (const action of ["start", "stop"]) document.getElementById("inspection-" + action).addEventListener("click", async () => {
    if (inspectionActionPending) return;
    inspectionActionPending = true;
    document.getElementById("inspection-" + action).disabled = true;
    try {
      if (action === "start" && inspectionDirtyFields.size && !await saveInspectionSettings()) return;
      renderInspectionState(await api(BASE + "/inspection/" + action, { method: "POST", body: {} }));
      if (action === "start") await load();
    }
    catch (err) {
      if (err instanceof AuthError) return showLogin(err.message);
    } finally { inspectionActionPending = false; if (!sessionBlocked) await loadInspectionState(); }
  });
  ```
  - `await load()` at line 1959 executes **immediately after `POST /inspection/start` spawns the background `go i.run(...)` goroutine** — while the inspection has just started (`running: true, done: 0`) and **before** `PersistVerdict` or `UpdatePriority` has updated the account!
  - When the background inspection round later completes (`state.running` transitions from `true` to `false`), `loadInspectionState()` (`0006-evaluation-ui.patch:1845-1863`) fetches `/api/v1/admin/codex-eval/inspection/state` and calls `renderInspectionState(state)` (`0006-evaluation-ui.patch:1832-1844`):
    ```js
    function renderInspectionState(state) {
      inspectionState = state;
      syncInspectionStatusPlacement();
      ...
      renderCandy();
      renderFingerprints();
    }
    ```
  - `renderInspectionState` only re-renders `renderCandy()` and `renderFingerprints()` using the **stale in-memory `accountList` / `credentials`**; it **never calls `load()` (or `refreshCatalog()`)** when `inspectionState.running` transitions from `true` to `false`! Thus the UI continues displaying the stale `降级` badge (`a.extra.codex_eval_inspection_verdict === "degraded"`) and stale `P99` priority until the next unrelated catalog refresh.
  - Also note: in `0006-evaluation-ui.patch:1961-1962`, `catch (err)` silently swallows any non-`AuthError` error from `POST /inspection/start` (e.g. `409 Conflict`) without calling `inspectionMessage(err.message, true)`.

#### Issue B3: Accounts with `启用自动巡检` (`AutoInspectionEnabled`) Off Are Excluded from Manual `立即巡检` (`startRun(false)`)
- On the `糖果` tab, the per-account switch is explicitly labeled **`启用自动巡检`** (`data-inspection-enable`, `aria-label="启用自动巡检"`, `0006-evaluation-ui.patch:1076, 1222, 2596`), which saves `extra.codex_eval_inspection_enabled` (`0005-inspection.patch:1123, 1159`).
- However, in `0005-inspection.patch`:
  - `inspectionEligible(a, s)` (`line 347`): `if !a.AutoInspectionEnabled || !a.Available || ... { return false }`
  - `testPhase` pre-send `check` (`line 671`): `if err == nil && !current.AutoInspectionEnabled { ... return errInspectionStopped }`
  - `applyAccount` (`line 581`): `if err == nil && !current.AutoInspectionEnabled { ... return false }`
- Because `startRun(false)` (`立即巡检`) uses the exact same `inspectionEligible`, `testPhase`, and `applyAccount` checks without distinguishing `automatic == false` vs `automatic == true`, any degraded account whose `启用自动巡检` switch was turned off is **completely skipped** by manual `立即巡检` (`startRun(false)`), and (combined with Path A) has **no way to recover** via either manual `测试` or manual `立即巡检`.

#### Issue B4: When `自动巡检` (`#inspection-enabled`) Is Off, `#inspection-auto-fields` Is Hidden on the `设置` Tab
- In `0006-evaluation-ui.patch:1492` (`backend/internal/codexeval/web/inspection.js`) and `2794` (`web/ui.html`):
  ```js
  document.getElementById("inspection-auto-fields").hidden = !document.getElementById("inspection-enabled").checked;
  ```
- When `自动巡检` is off (the user only wants to run manual `立即巡检`), `#inspection-auto-fields` (`模型`, `推理强度`, `检查方式` `糖果`/`指纹`, `每账户最多测试次数`, `INCLUDE`, `EXCLUDE`) is hidden, preventing the user from viewing or changing the model or check mode used by `立即巡检` unless they enable scheduled `自动巡检`.

---

### 2.3 Verification of Specific Questions from Dispatch Prompt

1. **Eligibility (`inspectionEligible` / `ListAccounts` / `PersistCodexInspectionVerdict`)**:
   - `PersistCodexInspectionVerdict` (`0005-inspection.patch:1283-1364`) keeps `account.Schedulable` unchanged (`true`) and replaces an emptied `model_mapping` with `{"blacklist": "blacklist"}` (`line 1325`).
   - `Account.IsSchedulable()` (`/tmp/sub2api-v0.2.20-base/backend/internal/service/account.go:194-215`) checks `IsActive()`, `Schedulable`, `ExpiresAt`, `OverloadUntil`, `RateLimitResetAt`, `TempUnschedulableUntil`, and `IsQuotaExceeded()`. It does **not** check `model_mapping` or `Priority` or `Verdict`.
   - Therefore, a degraded account with `Verdict == "degraded"`, `Priority == 99`, and `model_mapping == {"blacklist": "blacklist"}` still has `Available == true` (`IsSchedulable() == true`) **unless** it is also rate-limited/overloaded/temp-unschedulable/disabled or has `AutoInspectionEnabled == false` (`启用自动巡检` off) or fails the active Candy group/type/plan/wildcard filters (`0005-inspection.patch:346-368`).

2. **Model Mapping Interference During Inspection (`SendCodexEvaluation`)**:
   - `AccountTestService.SendCodexEvaluation` (`0004-admin-channel.patch:396-610`), `sendCodexAnthropicEvaluation` (`lines 649-758`), and `sendCodexGeminiEvaluation` (`lines 760-880`) send the requested `model` directly without calling `Account.IsModelSupported` or `Account.GetMappedModel`.
   - Thus `{"blacklist": "blacklist"}` in `credentials.model_mapping` blocks ordinary user gateway scheduling (`IsModelSupported` returns `false`), while allowing `SendCodexEvaluation` to send the evaluation request during inspection.

3. **State Transition & Recovery Logic in `run()` (`0005-inspection.patch:468-628`)**:
   - `inspectionAccount(a)` (`0005-inspection.patch:1122-1135`) sets `Verdict = InspectionVerdictDegraded` iff `a.Extra["codex_eval_inspection_verdict"] == "degraded"`, otherwise `InspectionVerdictNormal`.
   - What if an account has `Verdict == InspectionVerdictNormal` (e.g., degraded before verdict tracking existed, or priority manually set to `99`, or verdict cleared) while `Priority == 99` (`s.DegradedPriority`)?
     - When it answers `21` (`answers[0] == true`), `target` is `s.NormalPriority` (`10`), and `(current.Verdict == InspectionVerdictDegraded) == !answers[0]` is `false == false` (`true`, stable normal).
     - It calls `apply(a, s.NormalPriority)` (`0005-inspection.patch:492`) -> `applyAccount` (`lines 579-628`).
     - In `applyAccount`, `PersistVerdict` sees `current == verdict` (`normal == normal`) and `len(removed) == 0`, returning `nil`. Then, if `s.AdjustPriority` is `true`, `UpdatePriority(ctx, a.AccountID, 10)` repairs `Priority` from `99` to `10` (`lines 613-618`).
   - What if an account has `Verdict == InspectionVerdictDegraded`?
     - In `fingerprint` mode (`testType == "fingerprint"`), if `answers[0] == true`, lines 495-499 immediately set `Outcome = "recommended"` and call `apply(a, s.NormalPriority)` in 1 run without `recovery_wait`.
     - In `candy` mode (`testType == "candy"`), if `answers[0] == true`, line 500 queues `a` into `groups[s.NormalPriority]`, which waits `i.recovery` (`240s`, `line 511`) and then runs `s.MaxTestsPerAccount - 1` confirmation tests (`line 533`). Only if all `s.MaxTestsPerAccount` answers are `true` does `confirmed` call `apply(a, s.NormalPriority)` (`line 529`).

---

## 3. Summary of Why "手动巡检没有参与恢复过程" Happens

| # | Mechanism | Exact Location | Effect on Degraded Account Recovery |
| --- | --- | --- | --- |
| 1 | **Manual tests on `糖果` / `指纹` tabs (`POST /api/v1/admin/codex-eval/start`) never invoke verdict/model/priority recovery** | `0004-admin-channel.patch:53-65` (`CodexEvalStart`), `0001-evaluation-core.patch:1895-2009` (`Start` -> `startChecked`), `0006-evaluation-ui.patch:715-719, 1401-1405` | Running a manual test (`测试` / `测试所选` / `测试全部`) on a `降级` account in the `糖果` or `指纹` tab only appends to `history.json`. Even when the account passes (`21` or matching fingerprint), `codex_eval_inspection_verdict` stays `"degraded"` (`降级` badge remains), `codex_eval_inspection_removed_models` / `blacklist` in `model_mapping` is never restored, and `Priority` stays at `DegradedPriority` (`99`). |
| 2 | **Manual `立即巡检` (`POST /api/v1/admin/codex-eval/inspection/start`) in `candy` mode blocks for 240s (`recovery_wait`) after marking progress `Done = Total` (`1/1`)** | `0005-inspection.patch:97, 251-280, 474-514, 782-785` | `startRun(false)` does not distinguish manual `立即巡检` from scheduled automatic inspection. After the 1st test answers `21`, `testPhase` sets `Done = Total` (`账户进度：1/1`), `active[id]` is cleared (row spinner stops), and `run()` sleeps for `240s` (`recovery_wait`) before running confirmation tests. |
| 3 | **`loadInspectionState()` never refreshes `accountList` when an inspection round finishes** | `0006-evaluation-ui.patch:1832-1863, 1952-1964` (`web/inspection.js`) | Clicking `立即巡检` calls `await load()` immediately at start (before tests run), and when `loadInspectionState()` later observes `state.running` transition to `false` (`phase: "completed"`), `renderInspectionState()` only calls `renderCandy()` / `renderFingerprints()` with stale `accountList` data without calling `load()` / `refreshCatalog()`, leaving the `降级` tag and `P99` on screen. |
| 4 | **`启用自动巡检` (`AutoInspectionEnabled`) filters out accounts during manual `立即巡检` (`startRun(false)`)** | `0005-inspection.patch:347, 581, 671` | Accounts with `启用自动巡检` unchecked are skipped by `立即巡检` (`startRun(false)`), leaving zero manual recovery path when combined with #1. |

---

## 4. Upstream `/tmp/cpa-upstream-v0.4.6/` Logic Comparison (`同步查上游逻辑`)

### 4.1 Upstream Files Inspected
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go` (lines 1–139) — In-plugin `/inspection` (`POST` & `GET`) endpoints.
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection_test.go` (lines 1–52) — Unit test for `/inspection`.
- `/tmp/cpa-upstream-v0.4.6/examples/inspection.py` (lines 1–185) — Standalone Python inspection script (`定时糖果巡检`).
- `/tmp/cpa-upstream-v0.4.6/docs/inspection.md` (lines 1–125) — Upstream inspection documentation and rules table.
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/candy.go` (lines 1–93) & `fingerprint.go` (lines 1–254) — Upstream evaluation runners.
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/web/app.js` (lines 1–401), `candy.js` (lines 1–104), `fingerprint.js` (lines 1–93), `components.js` (lines 1–330) — Upstream frontend UI (only 4 tabs: `candy`, `fingerprint`, `pelican`, `siwc`; no `settings` tab, no `降级` badge, no model-removal state).

### 4.2 How Upstream Separates In-Plugin Evaluation from External Inspection Script

1. **Upstream Go Plugin (`internal/plugin/inspection.go:11-139`)**:
   - Upstream's Go plugin has **no background timer, no `settings` tab, no persistent `verdict` field on credentials, no `降级` UI badge (`web/components.js:107` only renders `<span class="tag"><span>P${esc(a.priority ?? 0)}</span></span>`), and no `model_mapping` removal**.
   - Instead, `internal/plugin/inspection.go` only provides a lightweight wrapper around `candyRunResponse` and `fingerprintRunResponse`:
     ```go
     // /tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go:23-69
     var inspectionRuns = map[string]func([]byte) managementResponse{
     	"candy": candyRunResponse, "fingerprint": fingerprintRunResponse,
     }

     // The latest inspection of each test, kept until the plugin stops.
     var inspections = map[string]inspection{}

     func inspectionRunResponse(body []byte) managementResponse {
     	var req struct {
     		Test    string   `json:"test"`
     		Include []string `json:"include"`
     		Exclude []string `json:"exclude"`
     	}
     ...
     	started := time.Now()
     	response := run(body)
     	if response.StatusCode == http.StatusOK {
     		mu.Lock()
     		inspections[req.Test] = inspection{started, ids}
     		mu.Unlock()
     	}
     	return response
     }
     ```
   - And `GET /inspection?test=<candy|fingerprint>` (`internal/plugin/inspection.go:85-139`) inspects **all records in `records.Candies[auth.ID]` or `records.Fingerprints[auth.ID]` whose timestamp is `>= latest.started`** (note: this includes any record appended to `records.Candies` / `records.Fingerprints` since `latest.started`):
     ```go
     // /tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go:100-139
     		switch test {
     		case "candy":
     			item.Records, item.Degraded = inspected(records.Candies[auth.ID], latest.started, func(r candyRecord) (bool, bool) {
     				return r.Status == "correct" || r.Status == "wrong", r.Status == "wrong"
     			})
     		case "fingerprint":
     			found, degraded := inspected(records.Fingerprints[auth.ID], latest.started, func(r fingerprintRecord) (bool, bool) {
     				if r.Attribution == nil || (r.Status != "completed" && r.Status != "partial") {
     					return false, false
     				}
     				return true, fingerprintModelID(r.Model) != fingerprintModelID(r.Attribution.Prediction)
     			})
     			item.Records, item.Degraded = summaries(found), degraded
     		}
     ```

2. **Upstream Python Script (`examples/inspection.py:111-181` & `docs/inspection.md:5-19`)**:
   - In upstream `examples/inspection.py`, there is **no separate `verdict` flag** (`codex_eval_inspection_verdict`). The script determines whether an account is currently degraded or normal **purely from its current `priority` (`c["priority"] == DEGRADED_PRIORITY` vs `c["priority"] == NORMAL_PRIORITY`)**:
     ```python
     # /tmp/cpa-upstream-v0.4.6/examples/inspection.py:19-21, 111-143
     DEGRADED_PRIORITY = 0                # 降智账号的 priority
     NORMAL_PRIORITY = 99                 # 正常账号的 priority
     RECOVERY_DELAY_SECONDS = 240         # 降智账号首测答对后，复测前等待的秒数

     def inspect(accounts):
         first = run_candy(accounts, 1)
         decisions = {}
         groups = {DEGRADED_PRIORITY: [], NORMAL_PRIORITY: []}
         for c in accounts:
             answers = first[c["id"]]
             reason = "无有效结论" if answers is None else ("首测答对" if answers[0] else "首测答错")
             decisions[c["id"]] = (reason, None)
             if answers is None or c["source"] != "auth_files":
                 continue
             if c["priority"] == DEGRADED_PRIORITY and answers[0]:
                 groups[NORMAL_PRIORITY].append(c)
             elif c["priority"] == NORMAL_PRIORITY and not answers[0]:
                 groups[DEGRADED_PRIORITY].append(c)

         for priority in (DEGRADED_PRIORITY, NORMAL_PRIORITY):
             group = groups[priority]
             if not group:
                 continue
             correct = priority == NORMAL_PRIORITY
             if correct:
                 print(f"  恢复确认：{len(group)} 个账号，等待 {RECOVERY_DELAY_SECONDS} 秒后复测")
                 time.sleep(RECOVERY_DELAY_SECONDS)
             repeated = run_candy(group, 2)
             for c in group:
                 answers = repeated[c["id"]]
                 if answers is None:
                     decisions[c["id"]] = ("复测无有效结论", None)
                 elif answers == [correct, correct]:
                     decisions[c["id"]] = ("三次均答对" if correct else "三次均答错", priority)
                 else:
                     decisions[c["id"]] = ("三次答题结果不一致", None)
         return decisions
     ```
   - And `docs/inspection.md:7-18` states:
     ```markdown
     以巡检开始时的 priority 为准，默认 `0` 表示降智账号，`99` 表示正常账号：
     | 原 priority | 首测结果 | 处理 |
     | `0` | 答错 | 保持 `0`，不复测、不通知 |
     | `0` | 答对 | 等待 240 秒，再测两次；三次都答对才调为 `99`，通知恢复正常 |
     | `99` | 答对 | 保持 `99`，不复测、不通知 |
     | `99` | 答错 | 直接再测两次；三次都答错才调为 `0`，通知确认降智 |
     没有设置过 priority 的认证文件视为 `0`。其他 priority 和配置中的 API Key 只测试，不自动调整。
     ```

### 4.3 Key Architectural Divergences Between Upstream CPA and Our Sub2API Plugin (`plugins/codex-candy-eval`)

| Aspect | Upstream (`/tmp/cpa-upstream-v0.4.6/`) | Our Sub2API Plugin (`plugins/codex-candy-eval`) | Why This Causes the User-Perceived Bug in Sub2API |
| --- | --- | --- | --- |
| **Where Degraded State Lives** | Only in `priority` (`0` = degraded, `99` = normal in CPA). No `verdict` metadata, no `降级` badge in UI, no `model_mapping` removal. | Stored in `extra.codex_eval_inspection_verdict` (`"degraded"` / `"normal"`), `extra.codex_eval_inspection_removed_models` + `credentials.model_mapping` (`{"blacklist":"blacklist"}`), AND `account.Priority` (`99` = degraded, `10` = normal). Rendered as `<span class="tag"><span>降级</span></span>` on every evaluation tab (`0006-evaluation-ui.patch:1052`). | Because our Sub2API plugin attaches sticky inspection state (`降级` badge + `removed_models` / `blacklist` + `P99`) to the account, a degraded account remains visibly degraded and model-blocked until `PersistCodexInspectionVerdict(..., InspectionVerdictNormal, ...)` runs. |
| **Manual Test on `糖果` / `指纹` Tabs (`测试` / `测试全部`)** | Calls `POST /candy/run` or `POST /fingerprint/run`. Does not change `priority`, because upstream UI has no `降级` state or model control at all. | Calls `POST /api/v1/admin/codex-eval/start` (`0004-admin-channel.patch:53-65` -> `startChecked(..., false, nil)` at `0001-evaluation-core.patch:1895-2009`). Never calls `PersistCodexInspectionVerdict` or `UpdatePriority`. | In our UI, the `降级` tag is displayed right on the `糖果` and `指纹` account rows (`0006-evaluation-ui.patch:1052`). When a user clicks `测试` / `测试所选` / `测试全部` on a `降级` account and it passes (`答对` `21` or fingerprint `与测试模型一致`), the account **does not recover** (`降级` tag, `removed_models`/`blacklist`, and `P99` all stay unchanged). |
| **How Inspection Classifies Current State** | `examples/inspection.py:121-124` checks `c["priority"] == DEGRADED_PRIORITY` vs `c["priority"] == NORMAL_PRIORITY`. | `0005-inspection.patch:491, 1127-1130` checks `current.Verdict == InspectionVerdictDegraded` (`extra.codex_eval_inspection_verdict == "degraded"`), ignoring `current.Priority`. | If an account's `extra.codex_eval_inspection_verdict` is `"degraded"`, `candy` mode requires `240s` `recovery_wait` + `MaxTestsPerAccount - 1` confirmation runs (`0005-inspection.patch:509-534`). Conversely, if `codex_eval_inspection_verdict` is absent/`"normal"` while `Priority == DegradedPriority` (`99`), `run()` treats it as already normal (`(current.Verdict == InspectionVerdictDegraded) == !answers[0]` is `true`). |
| **Manual `立即巡检` (`#inspection-start`) Progress & UI Refresh** | `examples/inspection.py:132` prints `恢复确认：... 等待 240 秒后复测` in terminal stdout synchronously. | `0005-inspection.patch:784` sets `Done = Total` (`账户进度：1/1`) after the 1st test before sleeping `240s` in `recovery_wait`; and `0006-evaluation-ui.patch:1832-1863` (`loadInspectionState`) never calls `load()` / `refreshCatalog()` when `state.running` finishes. | During `立即巡检`, after the 1st test answers `21`, progress already shows `1/1` and the row spinner stops while `run()` silently waits `240s`; and even after completion, `loadInspectionState()` does not refresh `accountList`, leaving the `降级` badge on screen. |
| **Per-Account `启用自动巡检` Switch** | Upstream has no per-account `AutoInspectionEnabled` switch. | `0005-inspection.patch:347, 581, 671` checks `a.AutoInspectionEnabled` (`启用自动巡检`) in both scheduled (`startRun(true)`) and manual `立即巡检` (`startRun(false)`). | If a user turns off `启用自动巡检` on an account so it won't be polled on a timer, manual `立即巡检` also skips it completely. |

---

## 5. Related Specs

- `.trellis/spec/backend/native-inspection.md` (lines 8–9, 165–225, 240–278)

