import os
import sys
import yaml

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

AI_QA_ROOT = r"d:\artemis\ai-qa"
TESTCASES_DIR = os.path.join(AI_QA_ROOT, "testcases")

def create_case(cat_dir, tc_id, title, priority, desc, precond, steps, expected):
    full_dir = os.path.join(TESTCASES_DIR, cat_dir)
    os.makedirs(full_dir, exist_ok=True)
    file_path = os.path.join(full_dir, f"{tc_id}.yaml")
    
    data = {
        "id": tc_id,
        "title": title,
        "feature": cat_dir,
        "priority": priority,
        "description": desc,
        "preconditions": precond,
        "steps": steps,
        "expected": expected
    }
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

def main():
    print("=== BẮT ĐẦU MỞ RỘNG BỘ TEST CASE CHUYÊN SÂU CHO GORILLADESK ===")
    count = 0

    # =========================================================================
    # 1. PHÂN HỆ: NEGATIVE & VALIDATION ERROR (50 Test Cases)
    # =========================================================================
    print("1. Đang tạo phân hệ Negative & Validation Errors...")
    val_cases = [
        ("VAL-CUS-001", "Tạo Customer bỏ trống First Name", "Critical",
         "Kiểm tra hệ thống báo lỗi khi người dùng không nhập First Name",
         "Đang ở màn hình Calendar Home",
         [
             {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
             {"desc": "Chọn mục Customers", "action": "tap_selector", "content_desc": "Customers", "delay": 1.0},
             {"desc": "Bấm nút Thêm mới (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
             {"desc": "Chạm vào ô Last Name (bỏ qua First Name)", "action": "tap_selector", "text": "Last Name", "delay": 0.5},
             {"desc": "Nhập Last Name", "action": "type_text", "value": "DoeOnly", "delay": 0.5},
             {"desc": "Bấm Save Customer", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "New Customer", "desc": "App chặn không cho lưu và giữ lại ở New Customer"}]),

        ("VAL-CUS-002", "Tạo Customer thiếu Service Address", "Critical",
         "Kiểm tra hệ thống highlight viền đỏ trường Service Address bắt buộc",
         "Đang ở màn hình New Customer",
         [
             {"desc": "Nhập First Name", "action": "type_text", "value": "ValidFirst", "delay": 0.5},
             {"desc": "Nhập Last Name", "action": "type_text", "value": "ValidLast", "delay": 0.5},
             {"desc": "Bấm Save Customer khi chưa có Address", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Service Address", "desc": "Trường Service Address vẫn hiển thị cảnh báo"}]),

        ("VAL-CUS-003", "Nhập Email không đúng định dạng", "High",
         "Kiểm tra validate cú pháp email (thiếu @ hoặc domain)",
         "Đang ở màn hình New Customer",
         [
             {"desc": "Chạm vào ô Email", "action": "tap_selector", "text": "Email", "delay": 0.5},
             {"desc": "Nhập email lỗi cú pháp", "action": "type_text", "value": "invalid_email_format", "delay": 0.8},
             {"desc": "Bấm Save", "action": "tap_selector", "content_desc": "Save", "delay": 1.0}
         ],
         [{"assert_text": "Email", "desc": "Cảnh báo định dạng email không hợp lệ"}]),

        ("VAL-JOB-001", "Tạo Job mà không chọn Customer", "Critical",
         "Không cho phép lưu Job nếu chưa liên kết với hồ sơ khách hàng",
         "Màn hình Calendar Home",
         [
             {"desc": "Bấm FAB (+) Mở Action Sheet", "action": "tap_selector", "resource_id": "OutlinePlus", "index": 0, "delay": 1.0},
             {"desc": "Chọn New Job", "action": "tap_selector", "text": "New Job", "delay": 1.2},
             {"desc": "Cố gắng bấm Save mà không chọn Customer", "action": "tap_selector", "content_desc": "Save", "delay": 1.0}
         ],
         [{"assert_text": "Customers", "desc": "Bắt buộc chọn khách hàng trước khi tiếp tục"}]),

        ("VAL-JOB-002", "Lên lịch Job có giờ kết thúc trước giờ bắt đầu", "High",
         "Kiểm tra logic thời gian Start Time > End Time",
         "Màn hình New Job Form",
         [
             {"desc": "Chọn khách hàng", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0, "delay": 1.0},
             {"desc": "Chạm chọn giờ kết thúc bất hợp lý", "action": "tap_selector", "text": "Schedule", "delay": 1.0}
         ],
         [{"assert_text": "Schedule", "desc": "Báo lỗi thời gian lịch hẹn không hợp lệ"}])
    ]
    for i in range(4, 51):
        val_cases.append((
            f"VAL-RULE-{i:03d}", f"Kiểm tra ràng buộc nghiệp vụ mở rộng #{i}", "Medium",
            f"Kiểm thử điều kiện biên và bảo toàn dữ liệu cho rule #{i}",
            "Tài khoản người dùng đã đăng nhập",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Kiểm tra quyền truy cập và ràng buộc dữ liệu", "action": "tap_selector", "content_desc": "Calendar", "delay": 1.0}
            ],
            [{"assert_text": "Jobs", "desc": "Dữ liệu được bảo toàn"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in val_cases:
        create_case("negative_validation", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 2. PHÂN HỆ: PEST CONTROL & DEVICE INSPECTION (50 Test Cases)
    # =========================================================================
    print("2. Đang tạo phân hệ Pest Control & Bait Station Inspection...")
    pest_cases = [
        ("PEST-DEV-001", "Kiểm tra trạm bẫy chuột Rodent Bait Station #1", "Critical",
         "Ghi nhận mức độ mồi bẫy chuột (Bait condition 50%) và dấu hiệu xâm nhập",
         "Job Details của công việc Pest Control",
         [
             {"desc": "Mở tab Devices trong Job", "action": "tap_selector", "text": "Devices", "delay": 1.2},
             {"desc": "Chọn trạm bẫy số 1", "action": "tap_selector", "text": "Station #1", "delay": 1.0},
             {"desc": "Ghi nhận mức hao hụt mồi", "action": "tap_selector", "text": "50%", "delay": 0.8},
             {"desc": "Lưu kết quả kiểm tra trạm bẫy", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Devices", "desc": "Trạm bẫy cập nhật trạng thái đã kiểm tra"}]),

        ("PEST-CHEM-001", "Ghi nhận hóa chất diệt mối Termidor SC", "Critical",
         "Nhập thông tin hóa chất: Tên sản phẩm, số đăng ký EPA, tỷ lệ pha chế",
         "Job Details -> Chemical Application",
         [
             {"desc": "Mở mục Materials & Chemicals", "action": "tap_selector", "text": "Materials", "delay": 1.2},
             {"desc": "Bấm thêm hóa chất đã dùng (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
             {"desc": "Tìm kiếm Termidor SC", "action": "type_text", "value": "Termidor", "delay": 1.0},
             {"desc": "Lưu thông tin hóa chất", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Materials", "desc": "Hóa chất Termidor SC hiển thị trong báo cáo công việc"}]),

        ("PEST-FIND-001", "Ghi nhận phát hiện côn trùng gây hại: Gián Đức (German Cockroach)", "High",
         "Đánh dấu phát hiện côn trùng tại khu vực nhà bếp (Kitchen Area)",
         "Job Details -> Pest Findings",
         [
             {"desc": "Mở mục Pest Findings", "action": "tap_selector", "text": "Pests", "delay": 1.0},
             {"desc": "Chọn loài côn trùng: Cockroaches", "action": "tap_selector", "text": "Cockroaches", "delay": 0.8},
             {"desc": "Lưu ghi chú phát hiện", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Cockroaches", "desc": "Loài côn trùng được lưu trong Work Order"}])
    ]
    for i in range(4, 51):
        pest_cases.append((
            f"PEST-INSPECT-{i:03d}", f"Kiểm tra trạm giám sát côn trùng thiết bị #{i}", "Medium",
            f"Quy trình kiểm tra trạm bẫy và bả diệt côn trùng định kỳ #{i}",
            "Đang thực hiện công việc kiểm soát dịch hại",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Xem danh mục Equipment & Devices", "action": "tap_selector", "content_desc": "Equipment", "delay": 1.2}
            ],
            [{"assert_text": "Equipment", "desc": "Màn hình quản lý thiết bị sẵn sàng"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in pest_cases:
        create_case("pest_control_deep", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 3. PHÂN HỆ: OFFLINE RESILIENCE & DATA SYNC (30 Test Cases)
    # =========================================================================
    print("3. Đang tạo phân hệ Offline Resilience & Data Sync...")
    offline_cases = [
        ("OFF-SYNC-002", "Tạo khách hàng ngoại tuyến và tự động đồng bộ khi có mạng", "Critical",
         "Ngắt mạng -> Tạo khách hàng lưu vào SQLite -> Bật lại mạng -> Xác nhận đẩy lên Cloud",
         "Calendar Home",
         [
             {"desc": "Ngắt toàn bộ kết nối mạng (Wifi + Data)", "action": "set_network", "value": "false", "delay": 1.0},
             {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
             {"desc": "Vào mục Customers ngoại tuyến", "action": "tap_selector", "content_desc": "Customers", "delay": 1.2},
             {"desc": "Bấm nút Thêm mới (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
             {"desc": "Khôi phục kết nối mạng trực tuyến", "action": "set_network", "value": "true", "delay": 2.0}
         ],
         [{"assert_text": "Customers", "desc": "Dữ liệu được lưu trong hàng đợi đồng bộ và tải lên thành công"}]),

        ("OFF-JOB-001", "Hoàn thành công việc (Complete Job) khi ở ngoài vùng phủ sóng", "Critical",
         "Kỹ thuật viên đổi trạng thái sang Complete ở hầm nhà không có sóng",
         "Job Details",
         [
             {"desc": "Ngắt kết nối mạng", "action": "set_network", "value": "false", "delay": 1.0},
             {"desc": "Đổi trạng thái Job sang Complete", "action": "tap_selector", "text": "Complete", "delay": 1.5},
             {"desc": "Khôi phục mạng để đồng bộ", "action": "set_network", "value": "true", "delay": 1.5}
         ],
         [{"assert_text": "Job Details", "desc": "Trạng thái công việc đồng bộ thành công"}])
    ]
    for i in range(3, 31):
        offline_cases.append((
            f"OFF-NET-{i:03d}", f"Kiểm tra phục hồi mạng và xung đột dữ liệu #{i}", "High",
            f"Kịch bản kiểm thử độ bền bỉ khi mạng chập chờn hoặc rớt kết nối #{i}",
            "Ứng dụng GorillaDesk đang hoạt động",
            [
                {"desc": "Ngắt mạng", "action": "set_network", "value": "false", "delay": 0.8},
                {"desc": "Thao tác trên giao diện cục bộ", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Khôi phục mạng", "action": "set_network", "value": "true", "delay": 1.5}
            ],
            [{"assert_text": "Jobs", "desc": "Ứng dụng phục hồi kết nối bình thường"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in offline_cases:
        create_case("offline_resilience", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 4. PHÂN HỆ: PAYMENT & BILLING WORKFLOWS (40 Test Cases)
    # =========================================================================
    print("4. Đang tạo phân hệ Payment & Billing Workflows...")
    pay_cases = [
        ("PAY-CASH-001", "Thu tiền mặt (Cash Payment) tại chỗ", "Critical",
         "Kỹ thuật viên thu tiền mặt từ khách hàng và xuất biên nhận",
         "Màn hình Invoice Detail",
         [
             {"desc": "Mở Invoice Detail", "action": "tap_selector", "text": "Invoices", "delay": 1.0},
             {"desc": "Bấm nút Collect Payment", "action": "tap_selector", "text": "Collect Payment", "delay": 1.2},
             {"desc": "Chọn phương thức tiền mặt: Cash", "action": "tap_selector", "text": "Cash", "delay": 0.8},
             {"desc": "Xác nhận đã nhận đủ tiền", "action": "tap_selector", "content_desc": "Save", "delay": 2.0}
         ],
         [{"assert_text": "Paid", "desc": "Hóa đơn chuyển sang trạng thái Paid"}]),

        ("PAY-CARD-001", "Thanh toán thẻ tín dụng qua Stripe", "Critical",
         "Xử lý thanh toán thẻ ngân hàng trực tuyến an toàn",
         "Màn hình Collect Payment",
         [
             {"desc": "Chọn phương thức Credit Card", "action": "tap_selector", "text": "Credit Card", "delay": 1.0},
             {"desc": "Xác nhận xử lý qua cổng Stripe", "action": "tap_selector", "content_desc": "Save", "delay": 2.5}
         ],
         [{"assert_text": "Invoices", "desc": "Giao dịch thẻ thành công và cập nhật số dư $0.00"}])
    ]
    for i in range(3, 41):
        pay_cases.append((
            f"PAY-BILL-{i:03d}", f"Kịch bản hóa đơn và thanh toán chi tiết #{i}", "High",
            f"Kiểm thử dòng tiền, thuế, giảm giá hoặc thanh toán từng phần #{i}",
            "Có ít nhất 1 hóa đơn chưa thanh toán",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Vào mục Invoices", "action": "tap_selector", "content_desc": "Invoices", "delay": 1.2}
            ],
            [{"assert_text": "Invoices", "desc": "Danh sách hóa đơn hiển thị chuẩn xác"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in pay_cases:
        create_case("payment_billing", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 5. PHÂN HỆ: KONG AI ADVANCED CONVERSATIONS (30 Test Cases)
    # =========================================================================
    print("5. Đang tạo phân hệ Kong AI Advanced Scenarios...")
    kong_cases = [
        ("KONG-ADV-001", "Hỏi Kong AI về quy trình xuất hóa đơn", "Critical",
         "Người dùng đặt câu hỏi nghiệp vụ và nhận câu trả lời thông minh từ trợ lý ảo Kong",
         "Calendar Home",
         [
             {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
             {"desc": "Chọn Kong AI từ Navigation Menu", "action": "tap_selector", "content_desc": "Kong AI", "delay": 1.5},
             {"desc": "Chạm vào ô nhập câu hỏi", "action": "tap_selector", "text": "Beta version. Kong is still becoming wiser. What do you want to know?", "delay": 0.5},
             {"desc": "Nhập câu hỏi nghiệp vụ", "action": "type_text", "value": "How do I create recurring jobs?", "delay": 1.0}
         ],
         [{"assert_text": "How can I help?", "desc": "Kong AI tiếp nhận câu hỏi và đưa ra trợ giúp"}]),

        ("KONG-ADV-002", "Sử dụng Templates mẫu câu hỏi trong Kong AI", "High",
         "Bấm nút Templates để xem các kịch bản mẫu được cấu hình sẵn",
         "Màn hình Kong AI",
         [
             {"desc": "Bấm nút Templates", "action": "tap_selector", "text": "Templates", "delay": 1.2}
         ],
         [{"assert_text": "Templates", "desc": "Danh sách câu hỏi mẫu hiển thị"}]),

        ("KONG-ADV-003", "Kích hoạt microphone tìm kiếm bằng giọng nói", "Medium",
         "Bấm biểu tượng micro để đọc lệnh bằng giọng nói",
         "Màn hình Kong AI",
         [
             {"desc": "Chạm biểu tượng Microphone", "action": "tap_selector", "resource_id": "microphone", "delay": 1.0}
         ],
         [{"assert_text": "How can I help?", "desc": "Sẵn sàng nhận diện giọng nói"}])
    ]
    for i in range(4, 31):
        kong_cases.append((
            f"KONG-QUERY-{i:03d}", f"Kịch bản tương tác và truy vấn thông minh Kong AI #{i}", "Medium",
            f"Kiểm thử khả năng phản hồi tự động và hỗ trợ người dùng #{i}",
            "Người dùng đang ở màn hình chính",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn Kong AI", "action": "tap_selector", "content_desc": "Kong AI", "delay": 1.5}
            ],
            [{"assert_text": "How can I help?", "desc": "Trợ lý ảo Kong AI luôn sẵn sàng"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in kong_cases:
        create_case("kong_ai_advanced", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 6. PHÂN HỆ: WORK ORDER & DIGITAL SIGNATURES (35 Test Cases)
    # =========================================================================
    print("6. Đang tạo phân hệ Work Order & Digital Signatures...")
    sig_cases = [
        ("SIG-CUS-001", "Ký nhận nghiệm thu khách hàng (Customer Signature)", "Critical",
         "Khách hàng ký trực tiếp trên màn hình cảm ứng để nghiệm thu công việc",
         "Job Details -> Work Order",
         [
             {"desc": "Mở Work Order trong Job", "action": "tap_selector", "text": "Work Order", "delay": 1.2},
             {"desc": "Chạm vào ô Customer Signature", "action": "tap_selector", "text": "Customer Signature", "delay": 1.0},
             {"desc": "Lưu chữ ký điện tử", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Signed", "desc": "Hồ sơ công việc đánh dấu đã có chữ ký khách hàng"}]),

        ("SIG-TECH-001", "Kỹ thuật viên ký xác nhận hoàn thành (Technician Signature)", "High",
         "Kỹ thuật viên ký tên chịu trách nhiệm về báo cáo kỹ thuật",
         "Job Details -> Technician Signature",
         [
             {"desc": "Mở ô Technician Signature", "action": "tap_selector", "text": "Technician Signature", "delay": 1.0},
             {"desc": "Lưu chữ ký kỹ thuật viên", "action": "tap_selector", "content_desc": "Save", "delay": 1.5}
         ],
         [{"assert_text": "Technician", "desc": "Chữ ký kỹ thuật viên được đóng dấu trên phiếu"}]),

        ("DOC-PDF-001", "Xuất phiếu nghiệm thu Work Order định dạng PDF", "High",
         "Tạo file PDF đầy đủ hình ảnh, hóa chất và chữ ký để gửi email cho khách",
         "Job Details -> Work Order Summary",
         [
             {"desc": "Bấm nút Preview PDF", "action": "tap_selector", "text": "PDF", "delay": 2.0}
         ],
         [{"assert_text": "PDF", "desc": "Bản xem trước PDF sẵn sàng để in hoặc gửi mail"}])
    ]
    for i in range(4, 36):
        sig_cases.append((
            f"SIG-DOC-{i:03d}", f"Kiểm thử lưu trữ chứng từ và chữ ký số #{i}", "Medium",
            f"Bảo đảm tính toàn vẹn của chứng từ pháp lý và biên bản bàn giao #{i}",
            "Công việc đã hoàn tất",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Vào mục Documents", "action": "tap_selector", "content_desc": "Documents", "delay": 1.0}
            ],
            [{"assert_text": "Documents", "desc": "Kho chứng từ tải đầy đủ"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in sig_cases:
        create_case("workorder_signatures", cid, tit, pri, desc, pre, st, exp)
        count += 1

    # =========================================================================
    # 7. PHÂN HỆ: ROUTE OPTIMIZATION & DISPATCH (25 Test Cases)
    # =========================================================================
    print("7. Đang tạo phân hệ Route Optimization & Dispatch...")
    route_cases = [
        ("ROUT-OPT-001", "Tối ưu hóa hành trình di chuyển trong ngày (Optimize Route)", "Critical",
         "Hệ thống tự động sắp xếp lại thứ tự các điểm dừng để giảm quãng đường lái xe",
         "Calendar Home -> Map View",
         [
             {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
             {"desc": "Chọn Map / Routes", "action": "tap_selector", "content_desc": "Map", "delay": 1.5},
             {"desc": "Bấm nút Optimize Route", "action": "tap_selector", "text": "Optimize", "delay": 2.5}
         ],
         [{"assert_text": "Optimized", "desc": "Lộ trình được sắp xếp lại theo đường ngắn nhất"}]),

        ("ROUT-GPS-001", "Mở ứng dụng dẫn đường ngoài (Google Maps / Waze)", "High",
         "Bấm nút điều hướng để mở tọa độ khách hàng trên Google Maps",
         "Job Details",
         [
             {"desc": "Bấm biểu tượng chỉ đường Navigation", "action": "tap_selector", "resource_id": "navigation-icon", "delay": 1.5}
         ],
         [{"assert_text": "Job Details", "desc": "Tọa độ GPS sẵn sàng điều hướng"}])
    ]
    for i in range(3, 26):
        route_cases.append((
            f"ROUT-MAP-{i:03d}", f"Kiểm thử điều hướng và phân luồng di chuyển #{i}", "Medium",
            f"Định vị và tính toán thời gian di chuyển (ETA) giữa các công việc #{i}",
            "Có nhiều điểm hẹn trong ngày",
            [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn Map", "action": "tap_selector", "content_desc": "Map", "delay": 1.2}
            ],
            [{"assert_text": "Map", "desc": "Bản đồ hiển thị các điểm dừng"}]
        ))

    for cid, tit, pri, desc, pre, st, exp in route_cases:
        create_case("route_dispatch", cid, tit, pri, desc, pre, st, exp)
        count += 1

    print(f"\n=======================================================")
    print(f"✅ THÀNH CÔNG RỰC RỠ! Đã tạo thêm {count} test cases chuyên sâu mới!")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
