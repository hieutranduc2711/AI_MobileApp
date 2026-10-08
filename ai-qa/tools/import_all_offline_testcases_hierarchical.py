import os
import sys
import re
import yaml
import openpyxl
from collections import defaultdict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

EXCEL_PATH = r"C:\Users\Admin\Downloads\GorillaDesk_RN-5477_Full_Current_Scope_QA_V4.xlsx"
AI_QA_ROOT = r"d:\artemis\ai-qa"
BASE_TESTCASE_DIR = os.path.join(AI_QA_ROOT, "testcases", "offline_sync")
BASE_SUITE_DIR = os.path.join(AI_QA_ROOT, "suites")

def clean_slug(name):
    if not name:
        return "general"
    s = str(name).strip().lower()
    s = re.sub(r'[/\\+&,\s]+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or "general"

def clean_text(text):
    if text is None:
        return ""
    s = str(text).strip()
    s = re.sub(r'[\r]', '', s)
    return s

def parse_steps_to_actions(steps_raw, action_hint="", module_hint=""):
    steps_list = []
    if not steps_raw:
        # Default fallback steps
        return [
            {"desc": "Bật mạng ổn định để chuẩn bị", "action": "set_network", "value": "true", "delay": 1.0},
            {"desc": f"Mở phân hệ {module_hint}", "action": "tap_selector", "text": module_hint or "Calendar", "delay": 1.5},
            {"desc": "Tắt Wi-Fi & 4G chuyển sang Offline", "action": "set_network", "value": "false", "delay": 2.0},
            {"desc": f"Thực hiện {action_hint}", "action": "tap_selector", "text": action_hint or "Save", "delay": 1.5},
            {"desc": "Bật lại kết nối mạng để đồng bộ", "action": "set_network", "value": "true", "delay": 2.0}
        ]

    lines = [l.strip() for l in steps_raw.split("\n") if l.strip()]
    for idx, line in enumerate(lines, 1):
        # Clean leading numbers like "1.", "1)", "Step 1:"
        clean_line = re.sub(r'^(\d+[\.\)]|step\s*\d+:?)\s*', '', line, flags=re.IGNORECASE).strip()
        line_lower = clean_line.lower()

        # Detect network actions
        if any(kw in line_lower for kw in ["tắt wi-fi", "tắt wifi", "tắt mạng", "turn off wi-fi", "turn off wifi", "ngắt mạng", "mất mạng", "offline"]):
            steps_list.append({
                "desc": clean_line,
                "action": "set_network",
                "value": "false",
                "delay": 2.0
            })
        elif any(kw in line_lower for kw in ["bật wi-fi", "bật wifi", "bật mạng", "turn on wi-fi", "turn on wifi", "reconnect", "khôi phục mạng", "online"]):
            steps_list.append({
                "desc": clean_line,
                "action": "set_network",
                "value": "true",
                "delay": 2.0
            })
        elif any(kw in line_lower for kw in ["quay lại", "navigate ra màn hình khác", "back", "trở về"]):
            steps_list.append({
                "desc": clean_line,
                "action": "back",
                "delay": 1.0
            })
        elif any(kw in line_lower for kw in ["bấm nút save", "nhấn save", "lưu dữ liệu", "save job", "save"]):
            steps_list.append({
                "desc": clean_line,
                "action": "tap_selector",
                "content_desc": "Save",
                "delay": 2.0
            })
        else:
            # UI interaction step
            # Check if there is a target in quotes
            quoted = re.findall(r'["\'](.*?)["\']', clean_line)
            target_text = quoted[0] if quoted else (action_hint if "thực hiện" in line_lower else clean_line[:30])
            steps_list.append({
                "desc": clean_line,
                "action": "tap_selector",
                "text": target_text,
                "delay": 1.0
            })

    return steps_list

def parse_expected_to_assertions(expected_raw, module_hint=""):
    assertions = []
    if not expected_raw:
        return [{"desc": "Giao diện và dữ liệu phản hồi đúng kỳ vọng", "assert_text": module_hint or "GorillaDesk"}]

    lines = [l.strip() for l in expected_raw.split("\n") if l.strip()]
    for line in lines:
        clean_line = re.sub(r'^(\d+[\.\)]|item\s*\d+:?)\s*', '', line, flags=re.IGNORECASE).strip()
        if not clean_line:
            continue
        # Check quoted text
        quoted = re.findall(r'["\'](.*?)["\']', clean_line)
        assert_kw = quoted[0] if quoted else (module_hint or "GorillaDesk")
        assertions.append({
            "desc": clean_line,
            "assert_text": assert_kw
        })
    if not assertions:
        assertions.append({"desc": "Xác thực trạng thái hoàn tất", "assert_text": module_hint or "GorillaDesk"})
    return assertions

def main():
    print("==================================================================")
    print("🚀 BẮT ĐẦU IMPORT ALL TESTCASES OFFLINE SYNC VÀO DỰ ÁN AI-QA")
    print(f"📖 Nguồn Excel: {EXCEL_PATH}")
    print(f"📂 Thư mục đích: {BASE_TESTCASE_DIR}")
    print("==================================================================")

    wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
    os.makedirs(BASE_TESTCASE_DIR, exist_ok=True)
    os.makedirs(BASE_SUITE_DIR, exist_ok=True)

    sheet_configs = [
        # (sheet_name, type)
        ("01_Online_to_Offline", "standard_21"),
        ("02_Offline_to_Online", "standard_21"),
        ("03_Round_Trip", "standard_21"),
        ("04_Server_to_Local_Offline", "standard_21"),
        ("05_Cross_Cutting", "standard_21"),
        ("09_New_TwoWay_Delta", "delta_09"),
        ("10_Dev_Checklist_167", "dev_10"),
        ("11_Bug_Regression_91", "bug_11"),
        ("12_Perf_ReRender_245", "perf_12"),
        ("13_Jira_Current_Delta", "jira_13"),
        ("16_Production_Edge_Gaps", "standard_21")
    ]

    total_imported = 0
    sheet_counts = defaultdict(int)
    module_testcases = defaultdict(list)          # module_slug -> [rel_paths]
    sheet_module_testcases = defaultdict(lambda: defaultdict(list)) # sheet_slug -> module_slug -> [rel_paths]
    sheet_testcases = defaultdict(list)           # sheet_slug -> [rel_paths]
    all_testcase_paths = []

    for sheet_name, s_type in sheet_configs:
        if sheet_name not in wb.sheetnames:
            print(f"⚠️ Bỏ qua sheet {sheet_name} (không tồn tại trong workbook)")
            continue

        ws = wb[sheet_name]
        sheet_slug = clean_slug(sheet_name)
        sheet_target_dir = os.path.join(BASE_TESTCASE_DIR, sheet_slug)
        os.makedirs(sheet_target_dir, exist_ok=True)

        print(f"\n▶ Đang xử lý Sheet: [{sheet_name}] ({ws.max_row - 1} dòng)...")

        for r in range(2, ws.max_row + 1):
            if s_type == "standard_21":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = clean_text(ws.cell(r, 2).value)
                flow_phase = clean_text(ws.cell(r, 3).value)
                priority = clean_text(ws.cell(r, 4).value) or "P1"
                module_raw = clean_text(ws.cell(r, 5).value) or "General"
                action_raw = clean_text(ws.cell(r, 6).value)
                scenario = clean_text(ws.cell(r, 7).value)
                source_tickets = clean_text(ws.cell(r, 8).value)
                source_urls = clean_text(ws.cell(r, 9).value)
                req_status = clean_text(ws.cell(r, 10).value)
                app_path = clean_text(ws.cell(r, 11).value)
                preconditions = clean_text(ws.cell(r, 12).value)
                test_data = clean_text(ws.cell(r, 13).value)
                detailed_steps = clean_text(ws.cell(r, 14).value)
                expected_result = clean_text(ws.cell(r, 15).value)
                network_path = clean_text(ws.cell(r, 16).value)
                risk = clean_text(ws.cell(r, 17).value)
                notes = clean_text(ws.cell(r, 21).value)

            elif s_type == "delta_09":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = clean_text(ws.cell(r, 2).value)
                flow_phase = "Two-Way Delta Action"
                priority = clean_text(ws.cell(r, 3).value) or "P1"
                module_raw = clean_text(ws.cell(r, 4).value) or "General"
                action_raw = clean_text(ws.cell(r, 5).value)
                scenario = clean_text(ws.cell(r, 7).value)
                source_tickets = clean_text(ws.cell(r, 8).value)
                source_urls = clean_text(ws.cell(r, 9).value)
                req_status = "Confirmed Delta"
                app_path = clean_text(ws.cell(r, 10).value)
                preconditions = clean_text(ws.cell(r, 11).value)
                test_data = ""
                detailed_steps = clean_text(ws.cell(r, 12).value)
                expected_result = clean_text(ws.cell(r, 13).value)
                network_path = direction
                risk = "Delta Missing Action"
                notes = ""

            elif s_type == "dev_10":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = "OFFLINE"
                flow_phase = "Dev Implementation Checklist"
                priority = clean_text(ws.cell(r, 3).value) or "High"
                module_raw = clean_text(ws.cell(r, 4).value) or "General"
                action_raw = clean_text(ws.cell(r, 5).value)
                scenario = clean_text(ws.cell(r, 5).value)
                source_tickets = "RN-5477 Dev Checklist"
                source_urls = clean_text(ws.cell(r, 12).value)
                req_status = clean_text(ws.cell(r, 8).value)
                app_path = "GD Mobile"
                preconditions = "Logged in GD Mobile"
                test_data = ""
                detailed_steps = clean_text(ws.cell(r, 6).value)
                expected_result = clean_text(ws.cell(r, 7).value)
                network_path = "Offline / Online"
                risk = "Dev Checklist Coverage"
                notes = clean_text(ws.cell(r, 13).value)

            elif s_type == "bug_11":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = "REGRESSION"
                flow_phase = "Historical Bug Regression"
                priority = "High"
                module_raw = clean_text(ws.cell(r, 4).value) or "General"
                action_raw = clean_text(ws.cell(r, 5).value)
                scenario = clean_text(ws.cell(r, 5).value)
                source_tickets = "Historical Bug Report"
                source_urls = clean_text(ws.cell(r, 13).value)
                req_status = clean_text(ws.cell(r, 8).value)
                app_path = "GD Mobile"
                preconditions = "Logged in GD Mobile"
                test_data = ""
                detailed_steps = clean_text(ws.cell(r, 6).value)
                expected_result = clean_text(ws.cell(r, 7).value)
                network_path = "Regression Path"
                risk = "Bug Regression"
                notes = clean_text(ws.cell(r, 14).value)

            elif s_type == "perf_12":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = "PERFORMANCE"
                flow_phase = "Component Re-render Baseline"
                priority = clean_text(ws.cell(r, 7).value) or "P1"
                module_raw = clean_text(ws.cell(r, 3).value) or "General"
                action_raw = clean_text(ws.cell(r, 5).value)
                scenario = f"Re-render benchmark for {ws.cell(r, 4).value} on {action_raw}"
                source_tickets = "RN-5477 Perf Re-render"
                source_urls = ""
                req_status = clean_text(ws.cell(r, 8).value)
                app_path = f"GD Mobile > {ws.cell(r, 4).value}"
                preconditions = "Logged in with downloaded local data"
                test_data = f"Baseline Re-render: {ws.cell(r, 6).value}"
                detailed_steps = clean_text(ws.cell(r, 9).value)
                expected_result = clean_text(ws.cell(r, 10).value)
                network_path = "Offline / Sync"
                risk = "Performance Degradation"
                notes = f"Recorded Re-render benchmark: {ws.cell(r, 6).value}"

            elif s_type == "jira_13":
                tc_id = clean_text(ws.cell(r, 1).value)
                if not tc_id:
                    continue
                direction = "CROSS-CUTTING"
                flow_phase = "Jira Comment & Schema Delta"
                priority = clean_text(ws.cell(r, 2).value) or "P1"
                module_raw = clean_text(ws.cell(r, 3).value) or "General"
                action_raw = clean_text(ws.cell(r, 4).value)
                scenario = clean_text(ws.cell(r, 4).value)
                source_tickets = clean_text(ws.cell(r, 5).value)
                source_urls = clean_text(ws.cell(r, 6).value)
                req_status = clean_text(ws.cell(r, 7).value)
                app_path = "GD Mobile"
                preconditions = "Configured account"
                test_data = ""
                detailed_steps = clean_text(ws.cell(r, 8).value)
                expected_result = clean_text(ws.cell(r, 9).value)
                network_path = "Sync Path"
                risk = "Schema / Comment Regression"
                notes = ""

            module_slug = clean_slug(module_raw)
            module_target_dir = os.path.join(sheet_target_dir, module_slug)
            os.makedirs(module_target_dir, exist_ok=True)

            steps_parsed = parse_steps_to_actions(detailed_steps, action_hint=action_raw, module_hint=module_raw)
            expected_parsed = parse_expected_to_assertions(expected_result, module_hint=module_raw)

            tc_data = {
                "id": tc_id,
                "title": f"{action_raw or tc_id}: {scenario[:100]}",
                "sheet": sheet_name,
                "module": module_raw,
                "action": action_raw,
                "priority": priority,
                "flow_phase": flow_phase,
                "direction": direction,
                "app_path": app_path,
                "preconditions": preconditions,
                "test_data": test_data,
                "steps": steps_parsed,
                "expected": expected_parsed,
                "source_tickets": source_tickets,
                "source_urls": source_urls,
                "risk": risk,
                "notes": notes
            }

            tc_filename = f"{tc_id}.yaml"
            tc_filepath = os.path.join(module_target_dir, tc_filename)
            with open(tc_filepath, "w", encoding="utf-8") as out_f:
                yaml.dump(tc_data, out_f, allow_unicode=True, sort_keys=False, default_flow_style=False)

            rel_path = os.path.relpath(tc_filepath, AI_QA_ROOT).replace("\\", "/")
            module_testcases[module_slug].append(rel_path)
            sheet_module_testcases[sheet_slug][module_slug].append(rel_path)
            sheet_testcases[sheet_slug].append(rel_path)
            all_testcase_paths.append(rel_path)

            total_imported += 1
            sheet_counts[sheet_name] += 1

        print(f"  ✅ Đã import {sheet_counts[sheet_name]} testcases cho [{sheet_name}]")

    print("\n==================================================================")
    print("📁 ĐANG SINH CÁC BỘ SUITE KIỂM THỬ THEO PHÂN CẤP TỪNG SCOPE...")
    print("==================================================================")

    # 1. Sinh Suite cho từng (Sheet + Module) -> e.g. suites/offline_sync/01_online_to_offline/calendar.yaml
    # Và sinh alias ngắn gọn ngay tại suites/ -> e.g. suites/offline-01-calendar.yaml
    total_suites = 0
    for sheet_slug, mod_dict in sheet_module_testcases.items():
        # Sheet-specific suites subfolder
        sheet_suite_subfolder = os.path.join(BASE_SUITE_DIR, "offline_sync", sheet_slug)
        os.makedirs(sheet_suite_subfolder, exist_ok=True)

        # Prefix ngắn cho sheet, ví dụ: 01_online_to_offline -> 01
        m = re.match(r'^(\d+)', sheet_slug)
        sheet_num_prefix = m.group(1) if m else sheet_slug[:2]

        for mod_slug, paths in mod_dict.items():
            suite_data = {
                "name": f"offline-{sheet_num_prefix}-{mod_slug}",
                "description": f"Offline Suite for Sheet [{sheet_slug}] > Module [{mod_slug}] ({len(paths)} cases)",
                "testcases": paths
            }
            # File in subfolder
            sub_file = os.path.join(sheet_suite_subfolder, f"{mod_slug}.yaml")
            with open(sub_file, "w", encoding="utf-8") as sf:
                yaml.dump(suite_data, sf, allow_unicode=True, sort_keys=False)

            # Flat alias in main suites/ folder
            flat_file = os.path.join(BASE_SUITE_DIR, f"offline-{sheet_num_prefix}-{mod_slug}.yaml")
            with open(flat_file, "w", encoding="utf-8") as ff:
                yaml.dump(suite_data, ff, allow_unicode=True, sort_keys=False)
            total_suites += 1

    # 2. Sinh Suite cho từng Sheet toàn bộ -> e.g. suites/offline-sheet-01-online-to-offline.yaml
    for sheet_slug, paths in sheet_testcases.items():
        m = re.match(r'^(\d+)', sheet_slug)
        prefix = m.group(1) if m else sheet_slug[:2]
        suite_data = {
            "name": f"offline-sheet-{prefix}",
            "description": f"All testcases in sheet [{sheet_slug}] ({len(paths)} cases)",
            "testcases": paths
        }
        flat_file = os.path.join(BASE_SUITE_DIR, f"offline-sheet-{prefix}.yaml")
        with open(flat_file, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, allow_unicode=True, sort_keys=False)

        # Alias tên đầy đủ
        flat_file_full = os.path.join(BASE_SUITE_DIR, f"offline-{sheet_slug}.yaml")
        with open(flat_file_full, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, allow_unicode=True, sort_keys=False)
        total_suites += 2

    # 3. Sinh Suite cho từng Module gộp trên TẤT CẢ các sheet -> e.g. suites/offline-module-job.yaml
    for mod_slug, paths in module_testcases.items():
        suite_data = {
            "name": f"offline-module-{mod_slug}",
            "description": f"Cross-sheet comprehensive offline suite for Module [{mod_slug}] ({len(paths)} cases)",
            "testcases": paths
        }
        flat_mod_file = os.path.join(BASE_SUITE_DIR, f"offline-module-{mod_slug}.yaml")
        with open(flat_mod_file, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, allow_unicode=True, sort_keys=False)
        total_suites += 1

    # 4. Sinh Suite đặc biệt cho 40 Edge Cases tab 16: suites/offline-16-edge-gaps.yaml
    if "16_production_edge_gaps" in sheet_testcases:
        edge_paths = sheet_testcases["16_production_edge_gaps"]
        edge_suite = {
            "name": "offline-16-edge-gaps",
            "description": f"Top Priority Production Edge Gaps Suite (Auth Expiry, Low Disk, Clock Drift, Kill, Migration) ({len(edge_paths)} cases)",
            "testcases": edge_paths
        }
        with open(os.path.join(BASE_SUITE_DIR, "offline-16-edge-gaps.yaml"), "w", encoding="utf-8") as f:
            yaml.dump(edge_suite, f, allow_unicode=True, sort_keys=False)

    # 5. Sinh Master Suite cho toàn bộ 3,982 test cases: suites/offline-master-all.yaml
    master_suite = {
        "name": "offline-master-all",
        "description": f"Master Offline Two-Way Sync Comprehensive Suite ({len(all_testcase_paths)} cases)",
        "testcases": all_testcase_paths
    }
    with open(os.path.join(BASE_SUITE_DIR, "offline-master-all.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(master_suite, f, allow_unicode=True, sort_keys=False)

    print(f"\n==================================================================")
    print(f"🎉 HOÀN THÀNH XUẤT SẮC IMPORT TOÀN BỘ TESTCASES!")
    print(f"   • Tổng số test cases đã import: {total_imported:,} cases")
    print(f"   • Cấu trúc thư mục: testcases/offline_sync/<sheet>/<module>/<tc_id>.yaml")
    print(f"   • Đã tạo {total_suites} bộ Suite kiểm thử phân cấp trong 'suites/'")
    print("==================================================================")

if __name__ == "__main__":
    main()
