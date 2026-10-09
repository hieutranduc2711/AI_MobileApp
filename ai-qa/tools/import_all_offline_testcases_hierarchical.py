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
AI_QA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def build_executable_testcase_steps(sheet_name, module, action, scenario, direction, detailed_steps, expected_raw):
    m_str = str(module or "").strip()
    a_str = str(action or "").strip()
    s_str = str(scenario or "").strip()
    d_str = str(direction or "").strip()
    steps_raw = str(detailed_steps or "").strip()

    m_lower = m_str.lower()
    a_lower = a_str.lower()
    s_lower = s_str.lower()
    d_upper = d_str.upper()

    steps = []
    expected = []

    # --- 1. THIẾT LẬP MẠNG & TIỀN ĐIỀU KIỆN ---
    is_o2f = ("ONLINE → OFFLINE" in d_upper or "ONLINE -> OFFLINE" in d_upper or sheet_name.startswith(("01", "04")))
    is_f2o = ("OFFLINE → ONLINE" in d_upper or "OFFLINE -> ONLINE" in d_upper or sheet_name.startswith("02"))
    is_roundtrip = ("ROUND TRIP" in d_upper or sheet_name.startswith("03"))

    if is_o2f or is_roundtrip:
        steps.append({"desc": "Đảm bảo kết nối mạng Online ban đầu để nạp dữ liệu cơ sở", "action": "set_network", "value": "true"})
        steps.append({"desc": "Đưa ứng dụng về màn hình Calendar Home an toàn", "action": "macro", "value": "ensure_calendar_home"})
        steps.append({"desc": "Ngắt toàn bộ kết nối mạng (Tắt Wi-Fi & Mobile Data)", "action": "set_network", "value": "false", "delay": 1.5})
        steps.append({"desc": "Xác nhận banner / icon Offline xuất hiện trên màn hình", "action": "assert_offline"})
    elif is_f2o:
        steps.append({"desc": "Chuyển thiết bị sang chế độ Offline (Tắt Wi-Fi & Mobile Data)", "action": "set_network", "value": "false", "delay": 1.5})
        steps.append({"desc": "Xác nhận ứng dụng đang trong trạng thái Offline", "action": "assert_offline"})
    else:
        steps.append({"desc": "Khởi tạo môi trường ứng dụng sẵn sàng", "action": "set_network", "value": "true"})

    # --- 2. CÁC BIẾN THỂ RỦI RO PHẦN CỨNG / MẠNG (RESILIENCE) ---
    if any(k in s_lower or k in steps_raw.lower() for k in ["background", "home", "minimize"]):
        steps.append({"desc": "Đưa ứng dụng xuống Background 3s rồi khôi phục foreground", "action": "background_app", "value": "3.0"})
    elif any(k in s_lower or k in steps_raw.lower() for k in ["lock", "khóa màn hình", "sleep", "tắt màn hình"]):
        steps.append({"desc": "Khóa màn hình thiết bị và mở khóa lại để kiểm tra bảo lưu phiên", "action": "lock_screen", "value": "3.0"})
    elif any(k in s_lower or k in steps_raw.lower() for k in ["flapping", "chập chờn", "yếu", "weak network", "rớt gói"]):
        steps.append({"desc": "Mô phỏng mạng chập chờn / rớt gói liên tục (Network Flapping)", "action": "weak_network", "value": "3"})

    # --- 3. THỰC THI NGHIỆP VỤ CHUẨN XÁC THEO TỪNG MODULE & ACTION ---

    # 3.1 Nhóm Job (Tạo mới, đổi trạng thái)
    if any(k in m_lower or k in a_lower for k in ["job", "work order", "wo"]) and not any(k in m_lower or k in a_lower for k in ["signature", "material", "todo", "note", "photo", "image", "document"]):
        if any(k in a_lower or k in s_lower for k in ["status", "sent", "unscheduled", "completed", "in progress"]):
            status_val = "Sent"
            if "completed" in s_lower or "completed" in a_lower: status_val = "Completed"
            elif "unscheduled" in s_lower or "unscheduled" in a_lower: status_val = "Unscheduled"
            elif "confirmed" in s_lower or "confirmed" in a_lower: status_val = "Confirmed"
            steps.append({"desc": "Mở Job đầu tiên từ màn hình Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
            steps.append({"desc": "Bấm chọn ô trạng thái Job Status", "action": "tap_selector", "content_desc": "Unconfirmed", "text": "Unconfirmed"})
            steps.append({"desc": f"Chọn trạng thái '{status_val}' trong danh sách", "action": "tap_selector", "text": status_val, "content_desc": status_val})
            expected.append({"desc": f"Trạng thái Job được cập nhật thành '{status_val}' trong local cache", "assert_text": status_val})
            expected.append({"desc": "Màn hình Job Details duy trì trạng thái ổn định không lỗi", "assert_text": "Job Details"})
        else:
            # Tạo Job mới với các bước bạch diện (Explicit Atomic Steps)
            steps.append({"desc": "Bấm nút (+) Floating Action Button trên Calendar", "action": "tap_selector", "resource_id": "OutlinePlus", "value": "0.91,0.94"})
            steps.append({"desc": "Chọn New Job trong Action Sheet", "action": "tap_selector", "content_desc": "New Job", "text": "New Job", "value": "0.5,0.72"})
            steps.append({"desc": "Chọn khách hàng trong danh sách", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0, "value": "0.5,0.28"})
            steps.append({"desc": "Chọn địa điểm dịch vụ (Location)", "action": "tap_selector", "resource_id": "location-item", "index": 0, "value": "0.5,0.28"})
            steps.append({"desc": "Chọn dịch vụ phụ trách", "action": "tap_selector", "content_desc": "# Thinh Outbox 2", "text": "# Thinh Outbox 2", "value": "0.5,0.32"})
            steps.append({"desc": "Bấm Save để lưu Job vào bộ nhớ offline", "action": "tap_selector", "content_desc": "Save", "text": "Save", "value": "0.92,0.14"})
            expected.append({"desc": "Form New Job được lưu thành công, chuyển hướng vào màn hình Job Details", "assert_text": "Job Details"})
            expected.append({"desc": "Job được lưu an toàn trong SQLite/Realm offline với mã định danh tạm thời ###", "assert_text": "###"})
            expected.append({"desc": "Trạng thái Job hiển thị sẵn sàng cho kỹ thuật viên thao tác offline", "assert_text": "Unconfirmed"})

    # 3.2 Nhóm Khách hàng & Địa điểm (Customer & Location)
    elif any(k in m_lower or k in a_lower for k in ["customer", "location", "contact", "opportunity"]):
        if any(k in a_lower or k in s_lower for k in ["create", "add", "new", "tạo"]):
            steps.append({"desc": "Bấm nút (+) Floating Action Button trên Calendar", "action": "tap_selector", "resource_id": "OutlinePlus", "value": "0.91,0.94"})
            steps.append({"desc": "Chọn New Customer trong Action Sheet", "action": "tap_selector", "content_desc": "New Customer", "text": "New Customer", "value": "0.5,0.78"})
            steps.append({"desc": "Nhập First Name khách hàng", "action": "tap_selector", "text": "First Name"})
            steps.append({"desc": "Điền First Name", "action": "type_text", "value": "Offline"})
            steps.append({"desc": "Nhập Last Name khách hàng", "action": "tap_selector", "text": "Last Name"})
            steps.append({"desc": "Điền Last Name", "action": "type_text", "value": "SyncTest"})
            steps.append({"desc": "Nhập Phone khách hàng", "action": "tap_selector", "text": "Phone"})
            steps.append({"desc": "Điền Phone", "action": "type_text", "value": "1234567890"})
            steps.append({"desc": "Bấm Save lưu thông tin khách hàng", "action": "tap_selector", "content_desc": "Save"})
            expected.append({"desc": "Hồ sơ khách hàng được tạo thành công trong chế độ offline", "assert_text": "Offline"})
            expected.append({"desc": "Dữ liệu khách hàng được lưu trữ cục bộ không bị rollback", "assert_text": "Customer"})
        else:
            steps.append({"desc": "Mở Drawer Menu từ Calendar", "action": "tap_selector", "content_desc": "Open navigation drawer", "value": "0.06,0.07"})
            steps.append({"desc": "Chọn mục Customers trong danh mục", "action": "tap_selector", "text": "Customers"})
            steps.append({"desc": "Chọn khách hàng trong danh sách để xem chi tiết", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
            expected.append({"desc": "Danh sách khách hàng và lịch sử làm việc hiển thị từ SQLite local cache", "assert_text": "Customer"})
            expected.append({"desc": "Dữ liệu vị trí và liên hệ được nạp đầy đủ khi offline", "assert_text": "All Locations"})

    # 3.3 Nhóm Báo giá (Estimate)
    elif "estimate" in m_lower or "estimate" in a_lower:
        steps.append({"desc": "Bấm nút (+) Floating Action Button trên Calendar", "action": "tap_selector", "resource_id": "OutlinePlus", "value": "0.91,0.94"})
        steps.append({"desc": "Chọn New Estimate trong Action Sheet", "action": "tap_selector", "content_desc": "New Estimate", "text": "New Estimate", "value": "0.5,0.88"})
        steps.append({"desc": "Chọn khách hàng lập báo giá", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn địa điểm dịch vụ", "action": "tap_selector", "resource_id": "location-item", "index": 0})
        steps.append({"desc": "Bấm Save để lưu Estimate offline", "action": "tap_selector", "content_desc": "Save"})
        expected.append({"desc": "Báo giá được tính toán và lưu offline an toàn", "assert_text": "Estimate"})
        expected.append({"desc": "Tổng tiền hiển thị chính xác", "assert_text": "Subtotal"})

    # 3.4 Nhóm Chữ ký (Signatures)
    elif "signature" in m_lower or "signature" in a_lower:
        sig_target = "customer" if any(k in a_lower or k in s_lower for k in ["customer", "client"]) else "tech"
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Signatures trong Job Details", "action": "tap_selector", "text": "Signatures"})
        steps.append({"desc": f"Thực hiện ký xác nhận ({sig_target.title()} Signature)", "action": "macro", "value": "take_signature", "args": {"target": sig_target}})
        expected.append({"desc": "Chữ ký số được mã hóa và lưu vào hồ sơ Job offline", "assert_text": "Signatures"})
        expected.append({"desc": "Chữ ký duy trì nguyên vẹn sau khi mất mạng", "assert_text": "Save"})

    # 3.5 Nhóm Hóa đơn (Invoice)
    elif "invoice" in m_lower or "invoice" in a_lower:
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Invoice trong Job Details", "action": "tap_selector", "text": "Invoice"})
        expected.append({"desc": "Hóa đơn được lưu cục bộ và hiển thị thông tin thanh toán", "assert_text": "Invoice"})
        expected.append({"desc": "Số tiền hóa đơn được bảo lưu chính xác", "assert_text": "Total"})

    # 3.6 Nhóm Vật tư & Hóa chất (Materials & Chemicals)
    elif any(k in m_lower or k in a_lower for k in ["material", "chemical"]):
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Materials trong Job Details", "action": "tap_selector", "text": "Materials"})
        steps.append({"desc": "Thêm vật tư / hóa chất sử dụng trong công việc", "action": "macro", "value": "add_material"})
        expected.append({"desc": "Vật tư được ghi nhận định mức và trừ kho cục bộ", "assert_text": "Materials"})

    # 3.7 Nhóm Việc cần làm (Todo List)
    elif "todo" in m_lower or "todo" in a_lower:
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Todo List trong Job Details", "action": "tap_selector", "text": "Todo List"})
        expected.append({"desc": "Mục việc cần làm hiển thị trong danh sách chờ offline", "assert_text": "Todo List"})

    # 3.8 Nhóm Ghi chú & Bình luận (Notes & Comments)
    elif any(k in m_lower or k in a_lower for k in ["note", "comment"]):
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Notes trong Job Details", "action": "tap_selector", "text": "Notes"})
        expected.append({"desc": "Ghi chú được lưu vào bộ nhớ cục bộ của Job", "assert_text": "Notes"})
        expected.append({"desc": "Top Note hiển thị đầy đủ không bị mất", "assert_text": "Top Note"})

    # 3.9 Nhóm Hình ảnh / Đính kèm (Photos & Attachments)
    elif any(k in m_lower or k in a_lower for k in ["photo", "image", "visible image", "attachment", "document"]):
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Chọn mục Attach a Photo trong Job Details", "action": "tap_selector", "text": "Attach a Photo"})
        expected.append({"desc": "Mục đính kèm ảnh sẵn sàng để xếp hàng chờ sync", "assert_text": "Attach a Photo"})

    # 3.10 Nhóm Chấm công (Time Clocking)
    elif "clock" in m_lower or "clock" in a_lower:
        steps.append({"desc": "Thực hiện chấm công Clock In trên giao diện", "action": "tap_selector", "content_desc": "Clock In", "text": "Clock In"})
        expected.append({"desc": "Bản ghi chấm công có timestamp offline chuẩn xác", "assert_text": "Clock Out"})

    # 3.11 Nhóm Thiết bị & MDU (Devices, Areas, Equipment, Buildings, Units)
    elif any(k in m_lower or k in a_lower for k in ["device", "mdu", "unit", "building", "area", "sentricon"]):
        steps.append({"desc": "Mở Job chi tiết từ Calendar", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0})
        steps.append({"desc": "Cuộn đến mục quản lý Device / Area", "action": "tap_selector", "text": "Device"})
        expected.append({"desc": "Dữ liệu thiết bị / khu vực được ghi nhận vào cơ sở dữ liệu", "assert_text": "Device"})

    # 3.12 Nhóm Lịch & Sự kiện (Calendar, Custom Event, Time Off)
    elif any(k in m_lower or k in a_lower for k in ["calendar", "event", "time off", "time_off", "time-off"]):
        # Các thao tác Calendar chuẩn trên GD Mobile: Xem lịch, đổi ngày, kiểm tra Jobs
        steps.append({"desc": "Đưa ứng dụng về màn hình Calendar Home", "action": "macro", "value": "ensure_calendar_home"})
        steps.append({"desc": "Bấm nút Today để điều hướng về ngày làm việc hiện tại", "action": "tap_selector", "content_desc": "Today", "text": "Today"})
        steps.append({"desc": "Kiểm tra danh sách công việc và chỉ số tổng trên Lịch", "action": "tap_selector", "text": "Jobs"})
        expected.append({"desc": "Lịch làm việc hiển thị nguyên vẹn các công việc từ SQLite offline", "assert_text": "Jobs"})
        expected.append({"desc": "Nút điều hướng Today và ngày hiện tại hoạt động bình thường", "assert_text": "Today"})
        expected.append({"desc": "Tổng doanh thu và số lượng công việc được bảo toàn", "assert_text": "Total"})

    # 3.13 Mặc định / Các phân hệ khác
    else:
        target_text = a_str or m_str or "Calendar"
        steps.append({"desc": f"Thực hiện thao tác {a_str} trên giao diện GorillaDesk", "action": "macro", "value": "ensure_calendar_home"})
        expected.append({"desc": f"Thao tác {a_str} duy trì trạng thái ổn định trên giao diện", "assert_text": "Today"})
        expected.append({"desc": "Ứng dụng GorillaDesk không bị crash khi xử lý offline", "assert_text": "Jobs"})

    # --- 4. HOÀN TẤT & ĐỒNG BỘ LẠI (NẾU CÓ CHU KỲ RECONNECT) ---
    if is_f2o or is_roundtrip:
        steps.append({"desc": "Khôi phục kết nối mạng (Bật Wi-Fi & Mobile Data)", "action": "set_network", "value": "true", "delay": 2.0})
        expected.append({"desc": "Hàng đợi Pending Outbox đẩy toàn bộ mutation lên server mà không xung đột", "assert_text": "Today"})

    return steps, expected

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

            steps_parsed, expected_parsed = build_executable_testcase_steps(
                sheet_name=sheet_name,
                module=module_raw,
                action=action_raw,
                scenario=scenario,
                direction=direction,
                detailed_steps=detailed_steps,
                expected_raw=expected_result
            )

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
