# Live Container & Real Browser Verification Report (`实测模式` L1–L4)

## Environment & Runtime Baseline

- **Retained Container**: `sub2api-codex-eval-test` (`http://127.0.0.1:18080`, internal synthetic supplier `native_fixture_supplier.py` on `127.0.0.1:18081`)
- **Loaded Binary**: `dist/build/linux-amd64/sub2api-plugins-v0.2.20-linux-amd64` (`Sub2API 0.2.20`, plugin UI footer `版本 v0.4.6`)
- **Browser Engine**: Google Chrome Headless via Playwright (`1280x900` desktop viewport and `430x900` mobile viewport)
- **Console / Page Errors**: `0` console errors, `0` page errors across L1–L4
- **External Paid API Calls**: `0` (`/etc/hosts` inside `sub2api-codex-eval-test` pins `chatgpt.com` and `api.openai.com` to `127.0.0.1`, and all fixture accounts point `base_url` to `http://127.0.0.1:18081`)

---

## L1: Page Shell, Footer & 5 Tabs

- **Admin Route**: `http://127.0.0.1:18080/admin/codex-eval`
- **Embedded Iframe URL**: `http://127.0.0.1:18080/codex-eval?theme=light&lang=zh&ui_mode=embedded&src_host=http%3A%2F%2F127.0.0.1%3A18080&src_url=http%3A%2F%2F127.0.0.1%3A18080%2Fadmin%2Fcodex-eval`
- **Footer Text**: `© 2026 CPA Codex Candy Eval · MIT · LGPL-3.0 · 版本 v0.4.6`
  - `MIT` link: `https://github.com/haowang02/cpa-plugin-codex-candy-eval/blob/main/LICENSE`
  - `LGPL-3.0` link: `https://github.com/Wei-Shaw/sub2api/blob/main/LICENSE`
- **Tab Switching**:
  - `#tab-candy` (`糖果`) -> `#candy-panel` visible
  - `#tab-fingerprint` (`指纹`) -> `#fingerprint-panel` visible
  - `#tab-pelican` (`鹈鹕`) -> `#pelican-panel` visible
  - `#tab-siwc` (`SIWC`) -> `#siwc-panel` visible
  - `#tab-settings` (`设置`) -> `#settings-panel` visible
- **Screenshot**: [live-l1-shell-and-tabs.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-l1-shell-and-tabs.png)

---

## L2: Unrestricted Group Selection & Cross-Provider Evaluation Live Run

- **Unrestricted Group Selection (`refreshCatalog` / `fetchNativeAccounts`)**:
  - Verified that all Sub2API groups load without platform filtering (`U13 Group A`, `U13 Group B`, `U13 Claude Group`, `U13 Gemini Group`, `U13 Antigravity Group`, plus dynamically created `U13 DeepSeek Group` with `platform: "deepseek"` and `u13-deepseek-key` `deepseek:apikey`), with zero `（不可用）` labels.
- **Credential-Type Selector (`#<test>-credential-type`)**:
  - `U13 Group B`: `全部账户` (`all`), `OpenAI · API Key` (`openai:apikey`), `OpenAI · OAuth` (`openai:oauth`).
  - `U13 Claude Group`: `全部账户` (`all`), `Anthropic · API Key` (`anthropic:apikey`).
  - `U13 Gemini Group`: `全部账户` (`all`), `Gemini · API Key` (`gemini:apikey`).
  - `U13 Antigravity Group`: `全部账户` (`all`), `Antigravity · API Key` (`antigravity:apikey`).
  - `U13 DeepSeek Group`: `全部账户` (`all`), `DeepSeek · API Key` (`deepseek:apikey`).
- **Live Evaluation Runs**:
  - **Candy (`anthropic:apikey`, `u13-claude-key`)**: Completed via `/v1/messages?beta=true` SSE conversion (`status: "completed"`, `ok: true`, `answer: "21"`).
  - **Fingerprint (`gemini:apikey`, `u13-gemini-key`)**: Completed 3 concurrent challenges via `/v1beta/models/...:streamGenerateContent?alt=sse` (`status: "completed"`, `attribution.prediction: "deepseek-v3.2"`, `used_outputs: 3`).
  - **Pelican (`antigravity:apikey`, `u13-antigravity-key`)**: Completed via Gemini SSE bridge (`status: "completed"`, `variant: "original"`, sandboxed preview `<iframe sandbox="allow-scripts" srcdoc="...">` rendered in `#pl-rows`).
- **Screenshot**: [live-l2-cross-provider.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-l2-cross-provider.png)

---

## L3: SIWC Live Run & History v3 Persistence

- **Account Filtering & Toolbar**: Switching to `#tab-siwc` (`SIWC`) on `U13 Group B` (`u13-b-only`, `u13-shared`, `u13-oauth`) populates `#siwc-model-select` (`gpt-6.1-sol`, `inspection-literal`, `自定义模型…`), restricts `#siwc-credential-type` to `OpenAI · OAuth` (`openai:oauth`), and renders only `account_id=8` (`u13-oauth`).
- **Live SIWC 1-Shot Responses Probe Execution**:
  - **Run 1 (`model: "gpt-5"` -> normalized to `"gpt-5.4"`)**: Sends `{"model": "gpt-5.4", "store": false, "stream": true, "input": [{"role": "user", "content": [{"type": "input_text", "text": "Reply with OK."}]}], "instructions": "..."}` with `User-Agent: cpa-siwc-check/0.4.6` via `SendCodexEvaluation` (`normalizeOpenAIModelForUpstream` + `normalizeCodexOAuthNonLitePayload`) to `/v1/responses`. Recorded state: `status: "available"` (`SIWC 可用`), `input_tokens: 5`, `output_tokens: 1`.
  - **Run 2 (`model: "gpt-6.1-sol-restricted"`)**: Triggers upstream HTTP `403` (`{"error": {"code": "subscription_sharing_user_not_eligible", "message": "Your account is not eligible to use subscription sharing"}}`). Recorded state: `status: "restricted"` (`订阅共享受限`), `code: "subscription_sharing_user_not_eligible"`, `http_status: 403`, `error: "Your account is not eligible to use subscription sharing"`.
  - Expanding `u13-oauth` (`[data-toggle="8"]`) displays both history records (`订阅共享受限` and `SIWC 可用`), and clicking `[data-siwc-detail]` opens the `#siwc-detail` (`SIWC 检测详情`) modal displaying `gpt-6.1-sol-restricted · ... · HTTP 403`, `订阅共享受限 subscription_sharing_user_not_eligible`, and `Your account is not eligible to use subscription sharing`.
- **History v3 & v2 Backup Verification**:
  - `/app/data/codex-eval/history.json` written with `schema_version: 3`, mode `0600`, preserving `results`, `fingerprints`, `pelicans`, and `siwc` (and `history.v2.json` backup with mode `0600` on v2->v3 upgrade).
- **Screenshot**: [live-l3-siwc-detail.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-l3-siwc-detail.png)

---

## L4: Settings Layout, Mode-Aware `下次巡检` Placement & Single-Run Fingerprint Inspection

- **Desktop (`1280x900`) Layout Measurements (`#inspection-auto-fields`)**:
  - Horizontal overflow: `false` (`scrollWidth: 958 == clientWidth: 958`)
  - Row 1 (`top: 232px`):
    - `模型` (`#inspection-model-select`): `left: 54px`, `width: 415px` (50% / 2 columns)
    - `推理强度` (`[name="effort"]`): `left: 489px`, `width: 198px` (25% / 1 column)
    - `检查方式` (`[name="test_type"]`): `left: 707px`, `width: 198px` (25% / 1 column)
  - Row 3 (`top: 411px`):
    - `包含账户通配符（INCLUDE）` (`[name="include_patterns"]`): `left: 54px`, `width: 415px` (50% / 2 columns)
    - `排除账户通配符（EXCLUDE）` (`[name="exclude_patterns"]`): `left: 489px`, `width: 415px` (50% / 2 columns)
- **Mobile (`430x900`) Layout Measurements (`#inspection-auto-fields`)**:
  - Horizontal overflow: `false` (`scrollWidth: 376 == clientWidth: 376`)
  - Single-column stacked fields (`left: 33px`, `width: 310px`): `top = 224px, 314px, 403px, 762px, 852px`.
- **Absence of Unsolicited `本轮...巡检` & Mode-Aware `#inspection-status` (`下次巡检：...`) Placement**:
  - Verified `document.getElementById("inspection-round-summary") === null` and zero `本轮糖果巡检` / `本轮指纹巡检` text in the DOM.
  - `#inspection-status` contains only the original 3 child spans (`#inspection-phase`, `#inspection-next`, `#inspection-progress`).
  - When `test_type === "candy"`, `#inspection-status` (`下次巡检：...`) is placed inside `#candy-credentials .credential-head` (on the `糖果` tab).
  - When `test_type === "fingerprint"`, `#inspection-status` (`下次巡检：...`) moves into `#fp-credentials .credential-head` (on the `指纹` tab), and persists there across page reload when `test_type: "fingerprint"` is saved.
- **Auto-Save, Same-Page Password Retention & Fresh Reload**:
  - Selecting `test_type = "fingerprint"`, filling `include_patterns = "*@example.com, *@company.com"`, `exclude_patterns = "*b-only*"`, and entering `ntfy_password = "live-session-secret"` auto-saves via `PUT /api/v1/admin/settings/codex-eval-inspection`.
  - Switching tabs (`#tab-candy` -> `#tab-settings`) retains the typed `ntfy_password` in the same page session.
  - Reloading `/codex-eval` restores `test_type = "fingerprint"`, `include_patterns = "*@example.com, *@company.com"`, `exclude_patterns = "*b-only*"`, places `#inspection-status` in `#fp-credentials`, and renders `[name="ntfy_password"]` empty with placeholder `"已配置，留空保持不变"`.
- **Live Inspection Rounds (`#inspection-start`)**:
  - **Round 1 (Candy Mode + Wildcards)**: `test_type: "candy"`, `model: "inspection-degrade-a"`, `max_tests_per_account: 3`, `include_patterns: ["*@example.com", "*@company.com"]`, `exclude_patterns: ["*b-only*"]`. Evaluated `u13-a-only` (`tests: 3`, degraded: priority `10 -> 99`, removed `"inspection-degrade-a"` from `model_mapping`, kept `"keep-model"`) and `u13-shared` (`tests: 1`, `unchanged`).
  - **Round 2 (Fingerprint Mode Single-Run Degradation — Option A)**: `test_type: "fingerprint"`, `model: "inspection-literal"`, `max_tests_per_account: 3`, `include_patterns: ["*@company.com"]`, `exclude_patterns: ["u13-a-*"]`. Evaluated only `u13-shared` in **1 single fingerprint run (`tests: 1`, `len(run_ids) == 1`, 3 challenges total, `15.4s`)** without confirmation loops, attributed `"deepseek-v3.2" != "inspection-literal"`, degraded `u13-shared` (`priority: 99`, removed `"inspection-literal"` from `model_mapping`), and dispatched `ntfy` + `bark` notifications (`指纹检测 · inspection-literal\n确认状态：正常 → 降级\nu13-shared：正常 → 降级`).
  - **Round 3 (Fingerprint Mode Single-Run Recovery — Option A)**: `test_type: "fingerprint"`, `model: "deepseek-v3.2"`, `max_tests_per_account: 3`, `include_patterns: ["*@company.com"]`, `exclude_patterns: ["u13-a-*"]`. Evaluated `u13-shared` in **1 single fingerprint run (`tests: 1`, `len(run_ids) == 1`, 3 challenges total, `15.36s`)** without waiting `240s` `recovery_wait` or running confirmation rounds, attributed `"deepseek-v3.2" == "deepseek-v3.2"`, restored `u13-shared` (`priority: 10`, `verdict: "normal"`, restored `"inspection-literal": "inspection-literal"` in `model_mapping`), and dispatched `ntfy` + `bark` notifications (`指纹检测 · deepseek-v3.2\n确认状态：降级 → 正常\nu13-shared：降级 → 正常`).
  - **Clean Fixture Restoration**: Restored `u13-a-only` and `u13-shared` to `priority: 10`, `codex_eval_inspection_verdict: "normal"`, and reset default inspection settings.
- **Screenshots**:
  - [live-l4-settings-desktop-1280.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-l4-settings-desktop-1280.png)
  - [live-l4-settings-mobile-430.png](file:///Users/minami/.gemini/antigravity-cli/brain/4e98b527-896d-4a47-b5d4-09be3777f956/live-l4-settings-mobile-430.png)
