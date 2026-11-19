# Live Container & Real Browser Verification Report (`实测模式` Q1, Q2 & Q3)

## Environment & Runtime Baseline

- **Retained Container**: `sub2api-codex-eval-test` (`http://127.0.0.1:18080`, internal synthetic supplier on `127.0.0.1:18081`)
- **Loaded Binary**: `dist/build/linux-amd64/sub2api-plugins-v0.2.20-linux-amd64` (`Sub2API 0.2.20`)
- **Browser Engine**: Google Chrome Headless via Playwright (`1860x920` desktop viewport)
- **Console / Page Errors**: `0` console errors, `0` uncaught page errors across Q1, Q2, and Q3
- **External Paid API Calls**: `0` (all test accounts point `base_url` to `http://127.0.0.1:18081`)

---

## Q1: Unsupported `/v1/usage` Probe Memoization & Config-Change Reset

- **Accounts Tested**:
  - `live-q1-probe-404` (`id=37`, `openai:apikey`, `base_url: "http://127.0.0.1:18081"`, `api_key: "fixture-q1-404-key1"`): Upstream `GET /v1/usage` returns HTTP `404 Not Found`.
  - `live-q1-probe-200-json` (`id=38`, `openai:apikey`, `base_url: "http://127.0.0.1:18081"`, `api_key: "fixture-q1-malformed-key1"`): Upstream `GET /v1/usage` returns HTTP `200 OK` with non-conforming JSON `{"object":"list","data":[{"id":"inspection-literal","object":"model"}]}`.
- **Initial Load & Memoization Persistence**:
  - Opening `http://127.0.0.1:18080/admin/accounts` triggered `POST /api/v1/admin/accounts/usage/batch`.
  - Both accounts hit `GET /v1/usage` **once** (`usage_hits["/v1/usage|Bearer fixture-q1-404-key1"] == 1`, `usage_hits["/v1/usage|Bearer fixture-q1-malformed-key1"] == 1`).
  - PostgreSQL `accounts.extra->>'apikey_usage_unsupported_identity'` persisted the 64-character SHA-256 identity fingerprints (`7779145c177ede663200e52ea44c6760e90fb26f49013c9c1b0bc9bf73b104ba` and `2942dcbf9f1c48de4162d51e23d9072d4caf0e6ceb4eee0ac89c5864cba78e7b`).
  - Verified `GET /api/v1/admin/accounts/37` redacts `apikey_usage_unsupported_identity` from the DTO `extra` payload (`undefined`).
- **Repeated Forced UI Refreshes (Zero Duplicate Probes & Zero `updated_at` Loop)**:
  - Clicked the manual Refresh button in `/admin/accounts` multiple times (sending `POST /api/v1/admin/accounts/usage/batch` with `force: true`).
  - Supplier request logs confirmed `/v1/usage` hit counts remained **1** for both `live-q1-probe-404` and `live-q1-probe-200-json`, while supported Q2 accounts incremented on every forced refresh.
  - PostgreSQL `updated_at` timestamps (`2026-11-08T01:16:59.49686+00:00` and `2026-11-08T01:16:59.500343+00:00`) remained completely unchanged across repeated refreshes, preventing any frontend `buildAPIKeyUsageRefreshKey` refresh loop.
- **Credential / Base-URL Update Reset**:
  - Updated `live-q1-probe-404` (`id=37`) via `PUT /api/v1/admin/accounts/37` with `api_key: "fixture-q1-404-key2"` and `base_url: "http://127.0.0.1:18081/custom"`.
  - Clicked Refresh in `/admin/accounts`: supplier recorded exactly **1** new probe to `/custom/v1/usage` (`usage_hits["/custom/v1/usage|Bearer fixture-q1-404-key2"] == 1`), and PostgreSQL updated `apikey_usage_unsupported_identity` to the new identity fingerprint (`fffbf43fffc8da1edc9734f40862b27b3bdacf65063a5179855f0fc2a2194b17`).

---

## Q2: Full-Quota Pause, UI Status Badge, Gateway Scheduling & Recovery Resumption

- **Accounts Tested (in `Q1-Q2 Live Verification Group`)**:
  - `live-q2-dated-usage` (`id=39`, `openai:apikey`, default `/v1/usage`): Reports `5h` window `used: 100, limit: 100, reset_at: "2099-01-01T00:00:00Z"`, `total` `used: 90, limit: 100`, `remaining: 10`.
  - `live-q2-undated-usage` (`id=40`, `openai:apikey`, default `/v1/usage`): Reports `remaining: 0`, `total` `used: 100, limit: 100` (no `reset_at`).
  - `live-q2-custom-script` (`id=41`, `openai:apikey`, custom `quota_script` querying `/custom-quota`): Returns `{ day: { used: 100, limit: 100 }, balance: { amount: 0, unit: "USD" } }`.
- **Phase 2A — Exhausted Quota State**:
  - **UI Rendering (`/admin/accounts`)**:
    - `live-q2-dated-usage` (`#39`): Status badge displays `临时不可调度` (`预计 2099/01/01 08:00:00 恢复`), usage cell displays `5h 100% 26351d 22h`, `total 90%`, `USD 10.00`.
    - `live-q2-undated-usage` (`#40`): Status badge displays `配额超限`, usage cell displays `total 100%`, `USD 0.00`.
    - `live-q2-custom-script` (`#41`): Status badge displays `配额超限`, usage cell displays `1d 100%`, `USD 0.00`.
  - **Database State**:
    - `#39`: `temp_unschedulable_until = "2099-01-01T00:00:00+00:00"`, `temp_unschedulable_reason = "apikey_quota_window_exhausted"`, `apikey_quota_5h_used_percent = 100`, `apikey_quota_total_used_percent = 90`.
    - `#40`: `apikey_quota_exhausted = true`, `apikey_quota_total_used_percent = 100`.
    - `#41`: `apikey_quota_exhausted = true`, `apikey_quota_1d_used_percent = 100`.
  - **Live Gateway Routing (`POST /v1/chat/completions`)**:
    - Request with group API key returned HTTP `503 Service Unavailable` (`{"error":{"message":"Service temporarily unavailable","type":"api_error"}}`), confirming all three exhausted accounts were skipped by the scheduler.
  - **Screenshot**: [live-q1-q2-exhausted.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-q1-q2-exhausted.png)
- **Phase 2B — Recovered Quota State**:
  - Switched synthetic supplier quota mode to `recovered` (`remaining: 50`, `used: 10, limit: 100`) and clicked the Refresh button in `/admin/accounts` **once**.
  - **UI Rendering (`/admin/accounts`)**:
    - All three accounts (`#39`, `#40`, `#41`) immediately transitioned their status badge to `正常` (`Active`) on that single refresh, with progress bars showing `10%` and balance `USD 50.00`.
  - **Database State**:
    - `#39`: `temp_unschedulable_until = NULL`, `temp_unschedulable_reason = NULL`, `apikey_quota_5h_used_percent = 10`, `apikey_quota_total_used_percent = 10`.
    - `#40`: `apikey_quota_exhausted = false`, `apikey_quota_total_used_percent = 10`.
    - `#41`: `apikey_quota_exhausted = false`, `apikey_quota_1d_used_percent = 10`.
  - **Live Gateway Routing (`POST /v1/chat/completions`)**:
    - Request with group API key succeeded with HTTP `200 OK` (`choices[0].message.content == "21"`).
  - **Screenshot**: [live-q1-q2-recovered.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-q1-q2-recovered.png)
- **Clean Fixture Restoration**:
  - Deleted temporary test accounts, group, and API key, restored user balance and `/app/fixture-supplier.py`, and verified clean default fixture state in `sub2api-codex-eval-test`.

---

## Q3: `codex-candy-eval` Manual Inspection (`立即巡检`) UI Recovery Refresh Live Check

- **Account Tested (in `U13 Group A`, `id=3`)**:
  - `u13-a-only` (`id=2`, `openai:apikey`, `base_url: "http://127.0.0.1:18081"`, `api_key: "fixture-a-only"`).
- **Phase 3A — Seeded Degraded State (`live-q3-eval-degraded.png`)**:
  - Seeded `u13-a-only` (`id=2`) with degraded inspection state:
    - `priority = 99`
    - `extra.codex_eval_inspection_verdict = "degraded"`
    - `extra.codex_eval_inspection_removed_models = ["inspection-degrade-a"]`
    - `credentials.model_mapping = {"blacklist": "blacklist"}`
  - Opened `http://127.0.0.1:18080/admin/codex-eval` (`糖果` tab) in Playwright + Google Chrome (`1860x920`).
  - Verified the live DOM row `[data-row="2"]` displayed tags `["apikey", "P99", "降级"]`.
  - **Screenshot**: [live-q3-eval-degraded.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-q3-eval-degraded.png)
- **Phase 3B — Manual `立即巡检` & Automatic Live DOM Recovery Refresh (`live-q3-eval-recovered.png`)**:
  - Switched to the `设置` tab (`#tab-settings`), enabled `自动调整优先级` (`adjust_priority = true`, `normal_priority = 10`, `degraded_priority = 99`) and `模型控制` (`control_models = true`, `degraded_remove_models = ["inspection-degrade-a"]`, `max_tests_per_account = 1`, `model = "inspection-literal"`).
  - Clicked `立即巡检` (`#inspection-start`) and switched back to the `糖果` tab (`#tab-candy`) **without reloading the page** (`mainFrameNavigations == 0`).
  - Once the inspection round completed (`running: true -> false`, `phase: "completed"`, `finished_at: "2026-11-08T16:39:26.121056755Z"`), `loadInspectionState()` automatically invoked `load()` to refresh `/api/v1/admin/accounts` and `/api/v1/admin/codex-eval/state`:
    - **Live DOM Tags (`糖果`, `指纹`, `鹈鹕` tabs)**: `[data-row="2"]` automatically updated from `["apikey", "P99", "降级"]` to `["apikey", "P10"]` (zero `降级` badge), with latest Candy result showing `答对 inspection-literal(low)` (`100% 1/1`).
    - **Backend / PostgreSQL State (`id=2`)**:
      - `priority = 10`
      - `extra.codex_eval_inspection_verdict = "normal"`
      - `extra.codex_eval_inspection_removed_models = []`
      - `credentials.model_mapping = {"inspection-degrade-a": "inspection-degrade-a"}` (`"blacklist"` placeholder removed and `"inspection-degrade-a"` restored).
    - **Idle Polling Check**: Confirmed `0` `/api/v1/admin/accounts` requests during subsequent idle `loadInspectionState()` polling.
    - **Errors**: `0` console errors and `0` uncaught page errors.
  - **Screenshot**: [live-q3-eval-recovered.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-q3-eval-recovered.png)
- **Clean Fixture Restoration**:
  - Cleared evaluation history across all four scopes (`candy`, `fingerprint`, `pelican`, `siwc`), restored default inspection settings, and reset accounts `#2` and `#4` to clean baseline state in `sub2api-codex-eval-test`.
