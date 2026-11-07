# Research: Fingerprint Inspection Rounds — Upstream (`cpa-plugin-codex-candy-eval` `v0.4.6`) vs Sub2API (`0005-inspection.patch`)

- **Query**: User asked: `如果模式采用指纹 那么实际如果发生状态转变 岂不是要测试9轮？ 读一下上游代码怎么写的` — Compare `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go` (and `fingerprint.go`, `examples/inspection.py`, `docs/inspection.md`) line-by-line with `plugins/codex-candy-eval/patches/0005-inspection.patch`.
- **Scope**: Read-only comparison of upstream CPA plugin `v0.4.6` vs `plugins/codex-candy-eval/patches/0005-inspection.patch`.
- **Date**: 2026-11-08

---

## 1. Files Found

- `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go` — Upstream `POST /inspection` (`inspectionRunResponse`) and `GET /inspection` (`inspectionResponse`) implementation (139 lines).
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection_test.go` — Upstream unit test for `fingerprint` inspection (52 lines).
- `/tmp/cpa-upstream-v0.4.6/internal/plugin/fingerprint.go` — Upstream fingerprint runner (`fingerprintTarget = 3` challenges per run; `fingerprintRunRequest` has no `runs` field).
- `/tmp/cpa-upstream-v0.4.6/examples/inspection.py` — Upstream external scheduled inspection script (`定时糖果巡检`, candy-only 1 + 2 confirmation rounds).
- `/tmp/cpa-upstream-v0.4.6/docs/inspection.md` — Upstream documentation for `examples/inspection.py`.
- `plugins/codex-candy-eval/patches/0005-inspection.patch` — Sub2API native background inspection coordinator (`backend/internal/codexeval/inspection.go`).

---

## 2. Exact Upstream Code (`/tmp/cpa-upstream-v0.4.6/internal/plugin/inspection.go`)

```go
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
	if json.Unmarshal(body, &req) != nil {
		return jsonError(http.StatusBadRequest, "请求格式错误")
	}
	run := inspectionRuns[req.Test]
	if run == nil {
		return jsonError(http.StatusBadRequest, "未知测试类型")
	}
	auths, err := selectedCredentials(nil, true)
	if err != nil {
		return jsonError(http.StatusBadGateway, err.Error())
	}
	ids := []string{}
	for _, auth := range auths {
		if (len(req.Include) == 0 || matchesAny(auth, req.Include)) && !matchesAny(auth, req.Exclude) {
			ids = append(ids, auth.ID)
		}
	}
	var fields map[string]json.RawMessage
	_ = json.Unmarshal(body, &fields)
	fields["credential_ids"], _ = json.Marshal(ids)
	delete(fields, "all")
	body, _ = json.Marshal(fields)
	started := time.Now()
	response := run(body)
	if response.StatusCode == http.StatusOK {
		mu.Lock()
		inspections[req.Test] = inspection{started, ids}
		mu.Unlock()
	}
	return response
}

func inspectionResponse(test string) managementResponse {
	...
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
	...
}
```

### How Upstream Handles `fingerprint` vs `candy`
1. **Upstream `internal/plugin/inspection.go` (`lines 23-139`)**:
   - `POST /inspection` is a **single-dispatch** trigger that forwards the body once to `candyRunResponse` or `fingerprintRunResponse`.
   - `fingerprintRunRequest` (`/tmp/cpa-upstream-v0.4.6/internal/plugin/fingerprint.go:106-133`) has **no `runs` field** (only `runRequest` + `Concurrency int`). One call to `fingerprintRunResponse` executes **1 fingerprint run per credential**, which internally sends `fingerprintTarget = 3` challenges (`fingerprint.go:20, 153-205`) and computes a 3-sample aggregate `Attribution.Prediction`.
   - `GET /inspection?test=fingerprint` (`inspection.go:108-116`) checks the single fingerprint record created since `latest.started` and immediately sets `degraded = fingerprintModelID(r.Model) != fingerprintModelID(r.Attribution.Prediction)`. There is **no multi-run confirmation loop** for fingerprint in upstream.
2. **Where Upstream's "1 Initial + 2 Confirmations = 3 Runs" Came From (`/tmp/cpa-upstream-v0.4.6/examples/inspection.py:80-143`, `docs/inspection.md:7-16`)**:
   - The "首测 1 次 + 状态变化复测 2 次（共 3 次一致才改 priority）" rule in upstream lives **exclusively in `examples/inspection.py`**, which is a **Candy-only** script (`run_candy(accounts, 1)` followed by `run_candy(group, 2)`).
   - In Candy mode, 1 test = 1 prompt/request, so 3 tests (`MaxTestsPerAccount = 3`) = 3 prompts total on state transition.
   - In Fingerprint mode, 1 fingerprint run **already** sends 3 distinct challenges (`fingerprintTarget = 3`) and aggregates them statistically via `analyzeFingerprint`.

---

## 3. Comparison with Sub2API `plugins/codex-candy-eval/patches/0005-inspection.patch`

In `0005-inspection.patch` (`backend/internal/codexeval/inspection.go:525-588, 703-789`):
1. `run()` executes:
   - Initial test: `first := i.testPhase(ctx, s, eligible, 1, false, ...)` -> `runs = 1`.
   - On state transition (`(current.Verdict == InspectionVerdictDegraded) != !answers[0]`), if `s.MaxTestsPerAccount > 1` (default `3`), it executes confirmation:
     `i.testPhase(ctx, s, group, s.MaxTestsPerAccount-1, true, confirmed)` -> `runs = s.MaxTestsPerAccount - 1` (`2` runs by default).
2. Inside `testPhase()` (`0005-inspection.patch:703-706`):
   ```go
   batches := 1
   if testType == "fingerprint" {
       batches = max(runs, 1)
   }
   ```
   Because `testPhase` loops `step := 0; step < batches; step++` and starts a full `StartRequest{Type: "fingerprint", ..., Concurrency: 1}` on each step, and each fingerprint run executes **3 challenges** (`fingerprintTarget = 3`):
   - **Stable state (no transition)**: `1` fingerprint run = **3 challenge requests** per account.
   - **State transition (with default `MaxTestsPerAccount = 3`)**: `1` initial fingerprint run (3 challenges) + `2` confirmation fingerprint runs (`2 × 3 = 6` challenges) = **3 fingerprint runs = 9 challenge requests** per account (and up to `9 × 3 = 27` HTTP attempts with retries), plus the 240s recovery wait!

This confirms the user's observation (`如果模式采用指纹 那么实际如果发生状态转变 岂不是要测试9轮？`): applying Candy's `MaxTestsPerAccount` (default 3) multi-run confirmation on top of Fingerprint's built-in 3-challenge run multiplies the challenge count to `3 × 3 = 9` challenges on state transition, whereas upstream only runs Fingerprint once (3 challenges total) per inspection.
