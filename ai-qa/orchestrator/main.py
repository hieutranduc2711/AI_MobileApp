import argparse
import sys
import os
import time
import json

# Đảm bảo UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_QA_ROOT = os.path.dirname(CURRENT_DIR)
if AI_QA_ROOT not in sys.path:
    sys.path.insert(0, AI_QA_ROOT)

from adapters.adb import ADBClient
from adapters.artemis import ArtemisAdapter
from adapters.bug_tracker import BugTrackerAdapter
from evaluators.crash_detector import CrashDetector
from evaluators.hermes_judge import HermesJudge
from orchestrator.loader import TestLoader
from orchestrator.result_normalizer import ResultNormalizer
from reports.html_reporter import HtmlReporter

def generate_hermes_evidence_bundle(tc_data, executed_steps, elapsed, screenshot_path, visible_texts, crash_info, runner_hint, video_path=None, keyframes=None, nonce=None):
    tc_id = tc_data.get("id", "UNKNOWN")
    is_mutation = (tc_data.get("type") == "E2E_MUTATION" or nonce is not None)
    runs_dir = os.path.join(AI_QA_ROOT, "runs")
    os.makedirs(runs_dir, exist_ok=True)

    # 1. Evidence Data JSON (cho Hermes API / automated evaluator)
    evidence_json_path = os.path.join(runs_dir, f"{tc_id}_evidence.json")
    evidence_data = {
        "test_id": tc_id,
        "title": tc_data.get("title", ""),
        "feature": tc_data.get("feature", ""),
        "tier": tc_data.get("tier", 0),
        "type": tc_data.get("type", "STANDARD"),
        "dynamic_nonce": nonce,
        "priority": tc_data.get("priority", "Normal"),
        "description": tc_data.get("description", ""),
        "preconditions": tc_data.get("preconditions", ""),
        "expected_criteria": tc_data.get("expected", []),
        "execution_duration_sec": elapsed,
        "video_recording": os.path.abspath(video_path) if video_path else None,
        "video_keyframes": [os.path.abspath(k) for k in keyframes] if keyframes else [],
        "steps_executed": executed_steps,
        "final_screen_state": {
            "screenshot": os.path.abspath(screenshot_path) if screenshot_path else None,
            "visible_texts_sample": visible_texts,
            "crash_detected": crash_info.get("has_crash", False),
            "crash_log": crash_info.get("crash_lines", [])
        },
        "runner_heuristic_hint": runner_hint
    }
    with open(evidence_json_path, "w", encoding="utf-8") as f:
        json.dump(evidence_data, f, ensure_ascii=False, indent=2)

    # 2. Prompt Markdown (để Hiếu xem và Hermes thẩm định)
    prompt_md_path = os.path.join(runs_dir, f"{tc_id}_FOR_HERMES.md")
    
    steps_md = "\n".join([f"{i+1}. **{s.get('desc', 'Action')}** (`{s.get('action')}`, duration: {s.get('duration_sec', 0)}s, status: `{s.get('status', 'OK')}`)" for i, s in enumerate(executed_steps)]) or "*(Chạy bằng ARTEMIS Autonomous Goal)*"
    expected_md = "\n".join([f"- {exp.get('desc', exp.get('assert_text', str(exp)))}" if isinstance(exp, dict) else f"- {exp}" for exp in tc_data.get("expected", [])]) or "- Xác thực trạng thái giao diện tương ứng mục tiêu"
    texts_md = ", ".join([f'"{t}"' for t in visible_texts[:35]]) if visible_texts else "Không trích xuất được text"

    rubric_md = ""
    is_negative = (tc_data.get("type") == "NEGATIVE_VALIDATION")
    if is_negative:
        rubric_md = f"""
---

## ⚠️ QUY TẮC THẨM ĐỊNH CA KIỂM THỬ CHẶN LỖI (STRICT NEGATIVE VALIDATION RUBRIC):
Đây là ca kiểm thử **Chặn Lỗi (Tier 1: Negative Validation)**.
Mục tiêu của bài test là chứng minh ứng dụng **chặn thành công hành vi không hợp lệ** (cố tình bỏ trống trường bắt buộc Service Address):
1. **Quy tắc Chặn Lưu (Block Enforcement):**
   - Ứng dụng **BẮT BUỘC PHẢI CHẶN**, giữ người dùng ở lại form `New Customer` và không được phép lưu vào hệ thống.
   - Trường `Service Address` phải được cảnh báo (bôi đỏ, chấm đỏ bắt buộc, hoặc thông báo 'Missed required fields').
2. **Quy tắc Không Được Lọt (No Validation Bypass):**
   - Nếu ứng dụng bị lỗi mà vẫn cho lưu (thoát form chuyển sang Customer Profile) -> **KẾT LUẬN FAIL** (Lý do: Bug bảo mật / Bỏ lọt validation dữ liệu bắt buộc).
   - Nếu ứng dụng bị crash hoặc văng app khi bấm Save -> **KẾT LUẬN FAIL**.
3. **Phán quyết PASS khi:**
   - Ứng dụng xử lý đúng chuẩn: Từ chối lưu, giữ nguyên ở form New Customer để người dùng sửa đổi, không bị crash!
"""
    elif is_mutation:
        rubric_md = f"""
---

## ⚠️ QUY TẮC THẨM ĐỊNH NGHIÊM NGẶT (STRICT AUDITOR RUBRIC - 5-POINT MUTATION CONTRACT):
Đây là ca kiểm thử **Biến Đổi Dữ Liệu Thực Tế (Tier 2: E2E Mutation)**. Để loại bỏ 100% rủi ro False Positive (lọt bug), Hermes **BẮT BUỘC** phải tuân thủ nghiêm ngặt 3 quy tắc sau:
1. **Quy tắc Nonce Độc Nhất (Mutation Proof):**
   - Giá trị Nonce được sinh ra cho lượt test này là: `{nonce}`
   - Màn hình kết quả hoặc danh sách trích xuất **BẮT BUỘC PHẢI CHỨA ĐÚNG CHUỖI:** `{nonce}`.
   - Nếu không tìm thấy đúng chuỗi này -> **KẾT LUẬN FAIL NGAY LẬP TỨC** (Lý do: Không có dữ liệu nào được tạo mới).
2. **Quy tắc Thoát Form (State Transition Proof):**
   - Màn hình **BẮT BUỘC phải chuyển sang Customer Profile Hub** (có 'All Locations', mã #ID).
   - Form 'New Customer' ban đầu **BẮT BUỘC PHẢI ĐÓNG HOÀN TOÀN**.
   - Nếu màn hình vẫn đứng im ở Form nhập liệu -> **KẾT LUẬN FAIL NGAY LẬP TỨC** (Lý do: Bấm Save nhưng form không lưu, có thể bị lỗi validation hoặc đơ).
3. **Quy tắc Sạch Lỗi Hệ Thống (Clean System):**
   - Logcat không có crash hoặc lỗi 500.

👉 **CHỈ ĐƯỢC PHÉP CẤP CỜ PASS KHI CẢ 3 ĐIỀU KIỆN TRÊN ĐỒNG THỜI ĐẠT 100%!**
"""

    content = f"""# 🏛️ PROMPT THẨM ĐỊNH KẾT QUẢ KIỂM THỬ (CHO AGENT HERMES)

**Vai trò của bạn:** Bạn là **Senior QA Auditor & Judge Agent (Hermes)**. Nhiệm vụ của bạn là thẩm định độc lập kết quả chạy kiểm thử thực tế trên ứng dụng GorillaDesk, đối soát với tiêu chí nghiệm thu của Test Case và đưa ra phán quyết: **PASS** hoặc **FAIL** (kèm bằng chứng và phân tích chi tiết).

---

## 1. THÔNG TIN TEST CASE
- **Test ID:** `{tc_id}`
- **Tiêu đề:** {tc_data.get('title', '')}
- **Phân hệ:** {tc_data.get('feature', '')}
- **Mức độ ưu tiên:** {tc_data.get('priority', 'Normal')}
- **Loại kiểm thử:** `{tc_data.get('type', 'STANDARD')}` (Tier {tc_data.get('tier', 0)})
- **Mục tiêu / Mô tả:** {tc_data.get('description', '')}
- **Điều kiện tiên quyết:** {tc_data.get('preconditions', '')}

### Tiêu chí nghiệm thu (Expected Conditions):
{expected_md}
{rubric_md}
---

## 2. HỒ SƠ BẰNG CHỨNG THỰC THI (EVIDENCE BUNDLE TỪ RUNNER)
- **Thời gian chạy:** {elapsed}s
- **Các bước Runner đã thao tác trên thiết bị:**
{steps_md}

- **Video ghi lại toàn bộ quá trình thực thi trên thiết bị (60fps Screen Recording):**
  - File: `{os.path.abspath(video_path) if video_path else 'N/A'}`

- **Chuỗi khung hình then chốt trích xuất từ Video (Visual Chain Keyframes):**
{chr(10).join([f"  - Frame {i+1}: `{os.path.abspath(k)}`" for i, k in enumerate(keyframes)]) if keyframes else "  - Không có keyframes riêng (dùng ảnh final)"}

- **Ảnh chụp màn hình kết quả cuối cùng (Final UI Screenshot - Full Resolution):**
  - File: `{os.path.abspath(screenshot_path) if screenshot_path else 'N/A'}`
  *(Hãy quan sát kỹ ảnh chụp màn hình và chuỗi khung hình đính kèm)*

- **Các đoạn Text/Nút bấm ghi nhận trên màn hình:**
  > {texts_md}

- **Tình trạng hệ thống:**
  - Crash/ANR Logcat: **{"CÓ CRASH ❌" if crash_info.get("has_crash") else "Không phát hiện crash (Sạch) ✅"}**
  - Gợi ý từ Runner Heuristic: `{runner_hint}`

---

## 3. YÊU CẦU ĐỐI VỚI HERMES
Hãy thẩm định độc lập và chặt chẽ các bằng chứng trên (đặc biệt là video/khung hình diễn tiến, ảnh chụp kết quả và danh sách text thực tế).
Đảm bảo đối soát chính xác theo tiêu chí nghiệm thu của Test Case, tránh False Positive và trả về kết luận theo JSON:

```json
{{
  "test_id": "{tc_id}",
  "verdict": "PASS" | "FAIL" | "BLOCKED",
  "confidence_score": 0.95,
  "summary": "<Tóm tắt nhận định trong 1-2 câu>",
  "reasoning": "<Phân tích chi tiết tại sao Pass hoặc Fail dựa trên video, ảnh và kết quả thao tác>",
  "defect_details": null
}}
```
"""
    with open(prompt_md_path, "w", encoding="utf-8") as f:
        f.write(content)

    return evidence_json_path, prompt_md_path

def run_testcase(tc_data, adb, artemis_adapter, crash_detector, bug_tracker, hermes_judge=None):
    tc_id = tc_data.get("id", "UNKNOWN")
    tc_title = tc_data.get("title", "")
    tc_goal = tc_data.get("goal", "")
    print(f"\n=======================================================")
    print(f"▶ RUNNING TEST: [{tc_id}] {tc_title}")
    if tc_goal:
        print(f"  🎯 Goal: {tc_goal[:120]}...")
    print(f"=======================================================")

    # Tiêm Nonce độc nhất nếu test case yêu cầu
    nonce = None
    tc_data_str = json.dumps(tc_data)
    if "{{DYNAMIC_NONCE}}" in tc_data_str:
        nonce = f"HieuQA_{int(time.time()) % 100000}"
        tc_data_str = tc_data_str.replace("{{DYNAMIC_NONCE}}", nonce)
        tc_data = json.loads(tc_data_str)
        print(f"  🔑 Injected Dynamic Nonce: {nonce}")

    crash_detector.clear_logcat()
    adb.ensure_app_open()

    # Bật quay video màn hình thiết bị ngầm (60fps)
    print("  🎥 Đang bật quay video màn hình thiết bị (Background Screen Recording)...")
    adb.start_recording()

    steps = tc_data.get("steps", [])
    t0 = time.perf_counter()
    executed_steps_log = []

    # TH1: Test case có sẵn các bước thao tác (Dynamic Selector Execution)
    if steps:
        for idx_step, s in enumerate(steps):
            desc = s.get("desc", f"Step {idx_step+1}")
            act = s.get("action")
            val = s.get("value")
            delay = s.get("delay", 0.5)

            print(f"  • {desc}...", end="", flush=True)
            step_t0 = time.perf_counter()
            step_status = "OK"

            if act == "tap_rel":
                coords = [float(x) for x in val.split(",")]
                adb.tap_rel(coords[0], coords[1])
            elif act == "tap_abs":
                coords = [int(x) for x in val.split(",")]
                adb.tap_abs(coords[0], coords[1])
            elif act == "tap_selector":
                text = s.get("text")
                desc_val = s.get("content_desc")
                res_id = s.get("resource_id")
                idx = s.get("index", 0)
                fallback = [float(x) for x in val.split(",")] if val else None
                x, y, method = adb.tap_by_selector(text=text, content_desc=desc_val, resource_id=res_id, index=idx, fallback_rel=fallback)
                if method == "dynamic":
                    print(f" [Dynamic: ({x},{y})]", end="")
                elif method == "not_found":
                    print(f" ⚠️ [Element Not Found!]", end="")
                    step_status = "ELEMENT_NOT_FOUND"
            elif act == "type_text":
                adb.type_text(val)
            elif act == "set_network":
                is_online = (str(val).lower() == "true")
                adb.set_wifi(is_online)
                adb.set_data(is_online)
                print(f" [Network: {'ONLINE' if is_online else 'OFFLINE'}]", end="")
            elif act == "hide_keyboard":
                adb.hide_keyboard()
            elif act == "swipe":
                coords = [int(x) for x in val.split(",")]
                adb.swipe(coords[0], coords[1], coords[2], coords[3])
            elif act == "back":
                adb.back()
            elif act == "assert_text":
                if not adb.has_text(val):
                    print(f" ⚠️ [Hint: Text '{val}' not found]", end="")
                    step_status = "TEXT_NOT_FOUND"

            if delay > 0:
                time.sleep(delay)

            step_duration = round(time.perf_counter() - step_t0, 2)
            executed_steps_log.append({
                "step": idx_step + 1,
                "desc": desc,
                "action": act,
                "duration_sec": step_duration,
                "status": step_status
            })
            print(f" [{step_status}]")

    # TH2: Test case định nghĩa bằng ARTEMIS Goal
    elif tc_goal:
        profile = tc_data.get("profile", "pro")
        verification = tc_data.get("verification", "final")
        artemis_res = artemis_adapter.execute_mission(tc_goal, profile=profile, verification=verification)
        executed_steps_log.append({
            "step": 1,
            "desc": f"ARTEMIS Mission: {tc_goal}",
            "action": "artemis_goal",
            "duration_sec": round(time.perf_counter() - t0, 2),
            "status": artemis_res.get("status", "COMPLETED")
        })

    elapsed = round(time.perf_counter() - t0, 2)

    # 0. Dừng quay video và trích xuất keyframes
    video_path = os.path.join(AI_QA_ROOT, "runs", "videos", f"{tc_id}.mp4")
    saved_video = adb.stop_recording(local_path=video_path)
    keyframes = []
    if saved_video:
        print(f"  🎬 Video đã được lưu: {saved_video}")
        keyframes_dir = os.path.join(AI_QA_ROOT, "runs", "keyframes")
        keyframes = adb.extract_keyframes(saved_video, keyframes_dir, tc_id)
        if keyframes:
            print(f"  🖼️  Đã trích xuất {len(keyframes)} khung hình then chốt (Keyframes) từ video")

    # 1. Chụp ảnh màn hình siêu tốc qua exec-out (~0.3s)
    screenshot_path = os.path.join(AI_QA_ROOT, "runs", f"{tc_id}_final.png")
    try:
        adb.screencap(screenshot_path)
    except Exception:
        screenshot_path = None

    # 2. Dump UI đúng 1 LẦN DUY NHẤT dùng chung cho cả get_visible_texts và has_text
    ui_tree = adb.get_parsed_hierarchy()
    visible_texts = adb.get_visible_texts(tree=ui_tree)

    # 3. Thu thập thông tin Logcat / Crash
    crash_info = crash_detector.check_for_crashes()

    # 4. Tính toán Runner Heuristic Hint (dùng chung ui_tree, 0s latency)
    runner_hint = "LIKELY_PASS"
    expected_list = tc_data.get("expected", [])
    for exp in expected_list:
        if isinstance(exp, dict) and "assert_text" in exp:
            req_text = exp["assert_text"]
            if not adb.has_text(req_text, tree=ui_tree):
                runner_hint = f"HEURISTIC_WARNING: Missing expected text '{req_text}'"
                break
        elif isinstance(exp, dict) and "assert_no_text" in exp:
            forbidden_text = exp["assert_no_text"]
            if adb.has_text(forbidden_text, tree=ui_tree):
                runner_hint = f"HEURISTIC_WARNING: Forbidden text '{forbidden_text}' still visible"
                break

    if nonce and not adb.has_text(nonce, tree=ui_tree):
        runner_hint = f"HEURISTIC_WARNING: Dynamic Nonce '{nonce}' not found on result screen"

    if crash_info.get("has_crash"):
        runner_hint = "HEURISTIC_FAIL: Crash detected in Logcat"

    # 5. XUẤT EVIDENCE BUNDLE CHO HERMES
    ev_json, ev_prompt = generate_hermes_evidence_bundle(
        tc_data, executed_steps_log, elapsed, screenshot_path, visible_texts, crash_info, runner_hint,
        video_path=saved_video, keyframes=keyframes, nonce=nonce
    )

    print("\n-------------------------------------------------------")
    print(f"🏛️  EVIDENCE BUNDLE CHO AGENT HERMES ĐÃ ĐƯỢC TẠO:")
    print(f"  📄 File Dữ Liệu (JSON): {ev_json}")
    print(f"  📝 Prompt Sẵn Cho Hermes: {ev_prompt}")
    print(f"  🎬 Video Thực Thi Toàn Bộ : {saved_video if saved_video else 'N/A'}")
    print(f"  🖼️  Ảnh Chụp Màn Hình Cuối : {screenshot_path}")
    print(f"  ⏱️  Thời Gian Thực Thi    : {elapsed}s | Gợi ý sơ bộ: {runner_hint}")
    # 6. TỰ ĐỘNG GỌI AGENT 2 (HERMES) ĐỂ THẨM ĐỊNH PASS / FAIL
    judge_res = {}
    verdict = "EVIDENCE_COLLECTED"
    summary = ""
    reasoning = ""
    if hermes_judge:
        judge_res = hermes_judge.evaluate(tc_id, ev_prompt)
        verdict = judge_res.get("verdict", "UNCERTAIN")
        score = judge_res.get("confidence_score", 0)
        summary = judge_res.get("summary", "")
        reasoning = judge_res.get("reasoning", "")

        print("\n=======================================================")
        print(f"🏛️  PHÁN QUYẾT TỰ ĐỘNG TỪ AGENT 2 (HERMES AUDITOR): [{verdict}]")
        print(f"  • Độ tin cậy : {score}")
        print(f"  • Tóm tắt    : {summary}")
        print(f"  • Nhận định  : {reasoning[:200]}...")
        print("=======================================================")

        if verdict == "FAIL":
            bug_tracker.file_bug(tc_id, f"Hermes Verdict FAIL on {tc_id}", reasoning, screenshot_path)

        # Tự động xuất báo cáo HTML và đẩy vào 1 conversation duy nhất trong Hermes Desktop
        try:
            reporter = HtmlReporter()
            with open(ev_json, "r", encoding="utf-8") as f:
                ev_data = json.load(f)
            html_path = reporter.generate_report(ev_data, judge_res)
            reporter.inject_to_hermes_conversation(tc_id, verdict, html_path, summary, reasoning, evidence_data=ev_data)
        except Exception as e:
            print(f"  [Reporter Warning] Lỗi khi tạo HTML / inject Hermes: {e}")

    return {
        "id": tc_id,
        "status": verdict,
        "runner_hint": runner_hint,
        "judge_summary": summary,
        "judge_reasoning": reasoning,
        "evidence_json": ev_json,
        "prompt_md": ev_prompt,
        "screenshot": screenshot_path,
        "time_sec": elapsed
    }

_TESTCASE_INDEX = {}

def get_testcase_index():
    global _TESTCASE_INDEX
    if not _TESTCASE_INDEX:
        tc_dir = os.path.join(AI_QA_ROOT, "testcases")
        for root, _, files in os.walk(tc_dir):
            for f in files:
                if f.endswith(".yaml"):
                    tc_id = f[:-5]
                    _TESTCASE_INDEX[tc_id] = os.path.join(root, f)
    return _TESTCASE_INDEX

def find_testcase_file(tc_id):
    index = get_testcase_index()
    if tc_id in index:
        return index[tc_id]
    for k, v in index.items():
        if k.startswith(tc_id):
            return v
    return None

def main():
    parser = argparse.ArgumentParser(description="AI-QA GorillaDesk Mobile Test Runner (Dual-Agent: Artemis Runner + Hermes Judge)")
    parser.add_argument("--suite", help="Suite name (e.g. smoke, critical, offline-mode, module-job, all-app-full-coverage)")
    parser.add_argument("--test", help="Test case ID (e.g. JOB-CREATE-001, JOB-001, DEV-001)")
    parser.add_argument("--device", help="Device serial (e.g. RFCY7018MSF)", default=None)
    parser.add_argument("--limit", type=int, default=0, help="Limit number of testcases to run in suite")
    parser.add_argument("--judge", default="hermes", choices=["hermes", "none"], help="Judge agent to evaluate test outcomes (default: hermes)")
    args = parser.parse_args()

    loader = TestLoader(AI_QA_ROOT)
    normalizer = ResultNormalizer(os.path.join(AI_QA_ROOT, "reports"))
    adb = ADBClient(args.device)
    artemis_adapter = ArtemisAdapter(device_serial=adb.serial)
    crash_detector = CrashDetector(adb)
    bug_tracker = BugTrackerAdapter(output_dir=os.path.join(AI_QA_ROOT, "reports", "bugs"))
    hermes_judge = HermesJudge() if args.judge == "hermes" else None

    print(f"[AI-QA] Connected Device: {adb.serial} (Resolution: {adb.width}x{adb.height})")
    if hermes_judge:
        print(f"[AI-QA] 🤖 Dual-Agent Auto-Judge: AGENT 2 (Hermes) Đang Kích Hoạt Tự Động!")

    results = []
    if args.test:
        tc_file = find_testcase_file(args.test)
        if not tc_file or not os.path.exists(tc_file):
            print(f"Không tìm thấy test case {args.test} trong kho kịch bản!")
            return
        tc_data = loader.load_yaml(tc_file)
        results.append(run_testcase(tc_data, adb, artemis_adapter, crash_detector, bug_tracker, hermes_judge=hermes_judge))
    elif args.suite:
        suite_data = loader.load_suite(args.suite)
        testcase_list = suite_data.get("testcases", [])
        if args.limit > 0:
            testcase_list = testcase_list[:args.limit]
            print(f"[AI-QA] Đang chạy giới hạn {args.limit} test cases trong suite...")
        for tc_ref in testcase_list:
            tc_path = os.path.join(AI_QA_ROOT, tc_ref)
            if os.path.exists(tc_path):
                tc_data = loader.load_yaml(tc_path)
                results.append(run_testcase(tc_data, adb, artemis_adapter, crash_detector, bug_tracker, hermes_judge=hermes_judge))
    else:
        parser.print_help()
        return

    normalizer.export_summary(results)

if __name__ == "__main__":
    main()
