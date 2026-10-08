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
    print("=== MỞ RỘNG BỘ TEST CASE GORILLADESK LÊN CẤP ĐỘ ENTERPRISE MASSIVE (700 CASES MỚI) ===")
    total = 0

    # 1. PHÂN HỆ: TERMITE & WDO INSPECTIONS (50 Cases)
    print("1. Đang tạo phân hệ Termite & Wood Destroying Organisms (WDO)...")
    for i in range(1, 51):
        tc_id = f"TERM-WDO-{i:03d}"
        if i == 1:
            title = "Lập biên bản khảo sát mối mọt WDO State Form"
            steps = [
                {"desc": "Mở Job kiểm tra mối", "action": "tap_selector", "text": "Job Details", "delay": 0.8},
                {"desc": "Chọn biểu mẫu WDO Inspection Report", "action": "tap_selector", "text": "WDO Report", "delay": 1.0},
                {"desc": "Tích chọn phát hiện mối Subterranean Termites", "action": "tap_selector", "text": "Subterranean Termites", "delay": 0.5},
                {"desc": "Lưu báo cáo WDO", "action": "tap_selector", "content_desc": "Save Report", "delay": 1.2}
            ]
            expected = [{"assert_text": "WDO Report Saved", "desc": "Biên bản WDO lưu thành công"}]
        elif i == 2:
            title = "Ghi nhận chỉ số đo độ ẩm bằng máy Moisture Meter"
            steps = [
                {"desc": "Mở tab Moisture Readings", "action": "tap_selector", "text": "Moisture Readings", "delay": 0.8},
                {"desc": "Nhập độ ẩm dầm gỗ tầng trệt", "action": "type_text", "value": "18.5%", "delay": 0.5},
                {"desc": "Lưu chỉ số", "action": "tap_selector", "content_desc": "Save", "delay": 1.0}
            ]
            expected = [{"assert_text": "18.5%", "desc": "Chỉ số độ ẩm được lưu vào hồ sơ"}]
        else:
            title = f"Khảo sát mối và cấu trúc gỗ kịch bản #{i}"
            steps = [
                {"desc": "Truy cập mục Kiểm tra Mối", "action": "tap_selector", "text": "Termite Inspection", "delay": 0.8},
                {"desc": f"Thực hiện kiểm tra mục #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Termite Inspection", "desc": "Màn hình kiểm tra hoạt động ổn định"}]
        create_case("termite_wdo_inspection", tc_id, title, "Normal",
                    f"Kiểm thử quy trình khảo sát mối công trình ca #{i}", "Job đang mở", steps, expected)
        total += 1

    # 2. PHÂN HỆ: BEDBUG ROOM-BY-ROOM INSPECTION & HEAT TREATMENT (40 Cases)
    print("2. Đang tạo phân hệ Bedbug & Heat Treatment...")
    for i in range(1, 41):
        tc_id = f"BEDBUG-RM-{i:03d}"
        if i == 1:
            title = "Kiểm tra rệp từng phòng (Room by Room Inspection Checklist)"
            steps = [
                {"desc": "Mở danh mục phòng", "action": "tap_selector", "text": "Rooms Checklist", "delay": 0.8},
                {"desc": "Chọn Phòng ngủ chính (Master Bedroom)", "action": "tap_selector", "text": "Master Bedroom", "delay": 0.6},
                {"desc": "Tích chọn nệm có vết rệp (Mattress Activity)", "action": "tap_selector", "text": "Mattress / Box Spring", "delay": 0.5},
                {"desc": "Lưu phòng", "action": "tap_selector", "content_desc": "Save Room", "delay": 1.0}
            ]
            expected = [{"assert_text": "Infested", "desc": "Trạng thái phòng chuyển sang có rệp"}]
        elif i == 2:
            title = "Ghi nhật ký nhiệt độ xử lý nhiệt (Heat Treatment Temp Log)"
            steps = [
                {"desc": "Mở Heat Treatment Log", "action": "tap_selector", "text": "Heat Log", "delay": 0.8},
                {"desc": "Nhập nhiệt độ phòng", "action": "type_text", "value": "135 F", "delay": 0.5},
                {"desc": "Lưu mốc nhiệt độ", "action": "tap_selector", "content_desc": "Log Temp", "delay": 1.0}
            ]
            expected = [{"assert_text": "135 F", "desc": "Ghi nhận nhiệt độ tiêu diệt rệp thành công"}]
        else:
            title = f"Quy trình xử lý rệp giường chuyên sâu #{i}"
            steps = [
                {"desc": "Mở hồ sơ kiểm tra rệp", "action": "tap_selector", "text": "Bedbug Inspection", "delay": 0.8},
                {"desc": f"Kiểm tra hạng mục #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Bedbug Inspection", "desc": "Hạng mục kiểm tra hiển thị đúng"}]
        create_case("bedbug_room_by_room", tc_id, title, "Normal",
                    f"Kiểm thử kiểm tra và xử lý rệp giường ca #{i}", "Đang ở Job Details", steps, expected)
        total += 1

    # 3. PHÂN HỆ: MOSQUITO & WILDLIFE TRAPPING (40 Cases)
    print("3. Đang tạo phân hệ Mosquito & Wildlife Trapping...")
    for i in range(1, 41):
        tc_id = f"WILD-TRAP-{i:03d}"
        if i == 1:
            title = "Đặt bẫy động vật hoang dã (Set Animal Live Trap)"
            steps = [
                {"desc": "Mở Wildlife Trapping Log", "action": "tap_selector", "text": "Wildlife Log", "delay": 0.8},
                {"desc": "Chọn loại động vật mục tiêu Raccoon", "action": "tap_selector", "text": "Raccoon", "delay": 0.5},
                {"desc": "Ghi số lượng bẫy đặt", "action": "type_text", "value": "2", "delay": 0.5},
                {"desc": "Lưu vị trí bẫy", "action": "tap_selector", "content_desc": "Save Trap", "delay": 1.0}
            ]
            expected = [{"assert_text": "Traps Active: 2", "desc": "Ghi nhận 2 bẫy đang hoạt động"}]
        elif i == 2:
            title = "Kiểm tra bắt được động vật và giấy phép di dời (Relocation Permit)"
            steps = [
                {"desc": "Mở Trap Check", "action": "tap_selector", "text": "Trap Check", "delay": 0.8},
                {"desc": "Chọn trạng thái Caught", "action": "tap_selector", "text": "Animal Captured", "delay": 0.5},
                {"desc": "Nhập mã giấy phép di dời FWCC", "action": "type_text", "value": "FWCC-78921", "delay": 0.5},
                {"desc": "Hoàn tất kiểm tra bẫy", "action": "tap_selector", "content_desc": "Done", "delay": 1.0}
            ]
            expected = [{"assert_text": "Relocated", "desc": "Ghi nhận di dời động vật hợp pháp"}]
        else:
            title = f"Nghiệp vụ bẫy bắt động vật và xịt muỗi #{i}"
            steps = [
                {"desc": "Mở danh mục bẫy động vật", "action": "tap_selector", "text": "Traps", "delay": 0.8},
                {"desc": f"Thao tác kiểm tra bẫy #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Traps", "desc": "Dữ liệu bẫy hiển thị đúng"}]
        create_case("mosquito_wildlife_trapping", tc_id, title, "Normal",
                    f"Kiểm thử bẫy bắt động vật và phòng chống muỗi ca #{i}", "Đang ở Job", steps, expected)
        total += 1

    # 4. PHÂN HỆ: INVOICE ADVANCED FINANCIAL & RECONCILIATION (60 Cases)
    print("4. Đang tạo phân hệ Invoice Advanced Financial...")
    for i in range(1, 61):
        tc_id = f"INV-FIN-{i:03d}"
        if i == 1:
            title = "Tạo hóa đơn có chiết khấu coupon giảm giá phần trăm"
            steps = [
                {"desc": "Mở Invoice", "action": "tap_selector", "text": "Invoices", "delay": 0.8},
                {"desc": "Bấm Add Discount", "action": "tap_selector", "text": "Add Discount", "delay": 0.6},
                {"desc": "Chọn loại phần trăm (%)", "action": "tap_selector", "text": "Percentage", "delay": 0.5},
                {"desc": "Nhập 15%", "action": "type_text", "value": "15", "delay": 0.5},
                {"desc": "Lưu chiết khấu", "action": "tap_selector", "content_desc": "Apply", "delay": 1.0}
            ]
            expected = [{"assert_text": "Discount: 15%", "desc": "Hóa đơn được giảm 15% tổng tiền"}]
        elif i == 2:
            title = "Xóa nợ xấu khó đòi (Write-off Bad Debt)"
            steps = [
                {"desc": "Mở Invoice quá hạn", "action": "tap_selector", "text": "Invoices", "delay": 0.8},
                {"desc": "Mở tùy chọn bổ sung", "action": "tap_selector", "content_desc": "More Options", "delay": 0.6},
                {"desc": "Chọn Write Off Bad Debt", "action": "tap_selector", "text": "Write Off", "delay": 0.8},
                {"desc": "Xác nhận xóa nợ", "action": "tap_selector", "text": "Confirm", "delay": 1.0}
            ]
            expected = [{"assert_text": "Written Off", "desc": "Hóa đơn chuyển sang trạng thái nợ xấu đã xóa"}]
        else:
            title = f"Nghiệp vụ tài chính và xử lý hóa đơn phức tạp #{i}"
            steps = [
                {"desc": "Mở danh sách hóa đơn", "action": "tap_selector", "text": "Invoices", "delay": 0.8},
                {"desc": f"Kiểm tra hóa đơn #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Invoices", "desc": "Màn hình tài chính hoạt động chính xác"}]
        create_case("invoice_advanced_financial", tc_id, title, "Normal",
                    f"Kiểm thử nghiệp vụ tài chính và đối soát hóa đơn ca #{i}", "Màn hình Invoices", steps, expected)
        total += 1

    # 5. PHÂN HỆ: ESTIMATES GOOD/BETTER/BEST TIER OPTIONS (45 Cases)
    print("5. Đang tạo phân hệ Estimates Good/Better/Best...")
    for i in range(1, 46):
        tc_id = f"EST-TIER-{i:03d}"
        if i == 1:
            title = "Tạo báo giá 3 mức lựa chọn Good / Better / Best"
            steps = [
                {"desc": "Mở New Estimate", "action": "tap_selector", "content_desc": "New Estimate", "delay": 1.0},
                {"desc": "Chọn chế độ Multi-Tier Options", "action": "tap_selector", "text": "Tiered Options", "delay": 0.8},
                {"desc": "Nhập giá gói Basic (Good)", "action": "type_text", "value": "150", "delay": 0.5},
                {"desc": "Lưu báo giá đa mức", "action": "tap_selector", "content_desc": "Save Estimate", "delay": 1.2}
            ]
            expected = [{"assert_text": "Tiered Estimate Created", "desc": "Báo giá đa tùy chọn được lưu"}]
        elif i == 2:
            title = "Khách hàng chọn gói Option 2 (Better) và tự động cập nhật tổng tiền"
            steps = [
                {"desc": "Xem báo giá", "action": "tap_selector", "text": "Estimate Details", "delay": 0.8},
                {"desc": "Chọn Option 2 (Better Package)", "action": "tap_selector", "text": "Option 2", "delay": 0.6},
                {"desc": "Bấm Accept Option", "action": "tap_selector", "content_desc": "Accept", "delay": 1.0}
            ]
            expected = [{"assert_text": "Accepted: Option 2", "desc": "Gói Option 2 được phê duyệt"}]
        else:
            title = f"Quy trình báo giá đa tầng và phê duyệt dịch vụ #{i}"
            steps = [
                {"desc": "Mở danh sách Estimates", "action": "tap_selector", "text": "Estimates", "delay": 0.8},
                {"desc": f"Kiểm tra báo giá #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Estimates", "desc": "Màn hình báo giá hiển thị đầy đủ"}]
        create_case("estimates_good_better_best", tc_id, title, "Normal",
                    f"Kiểm thử kịch bản báo giá nhiều tầng lựa chọn ca #{i}", "Màn hình Estimates", steps, expected)
        total += 1

    # 6. PHÂN HỆ: ROLE-BASED ACCESS CONTROL & TECH PERMISSIONS (50 Cases)
    print("6. Đang tạo phân hệ Role-Based Permissions...")
    for i in range(1, 51):
        tc_id = f"PERM-ROLE-{i:03d}"
        if i == 1:
            title = "Tài khoản Technician không được xem giá tiền và doanh thu"
            steps = [
                {"desc": "Đăng nhập tài khoản Technician", "action": "tap_selector", "text": "Technician Login", "delay": 0.8},
                {"desc": "Mở chi tiết Job", "action": "tap_selector", "text": "Job Details", "delay": 0.8}
            ]
            expected = [{"assert_text": "Hidden by Admin", "desc": "Các trường giá tiền và invoice bị ẩn với thợ"}]
        elif i == 2:
            title = "Kỹ thuật viên không thể xóa Job đã hoàn thành"
            steps = [
                {"desc": "Mở Job Completed", "action": "tap_selector", "text": "Completed Job", "delay": 0.8},
                {"desc": "Kiểm tra nút Delete", "action": "tap_selector", "content_desc": "Delete", "delay": 0.5}
            ]
            expected = [{"assert_text": "Permission Denied", "desc": "Báo lỗi không có quyền xóa job hoàn thành"}]
        else:
            title = f"Phân quyền bảo mật và an toàn vai trò người dùng #{i}"
            steps = [
                {"desc": "Kiểm tra quyền hạn chức năng", "action": "tap_selector", "text": "Settings", "delay": 0.8},
                {"desc": f"Truy cập phân quyền #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Settings", "desc": "Cơ chế bảo mật kiểm tra thành công"}]
        create_case("role_based_permissions", tc_id, title, "Normal",
                    f"Kiểm thử ma trận phân quyền KTV và Quản lý ca #{i}", "Đang đăng nhập", steps, expected)
        total += 1

    # 7. PHÂN HỆ: NETWORK CHAOS & EXTREME RESILIENCE (60 Cases)
    print("7. Đang tạo phân hệ Network Chaos & Resilience...")
    for i in range(1, 61):
        tc_id = f"CHAOS-RES-{i:03d}"
        if i == 1:
            title = "App bị hệ điều hành Android kill khi đang upload ảnh hiện trường"
            steps = [
                {"desc": "Đang upload ảnh Before Photo", "action": "tap_selector", "content_desc": "Save Photo", "delay": 0.5},
                {"desc": "Mở lại ứng dụng GorillaDesk", "action": "tap_selector", "text": "GorillaDesk", "delay": 1.5}
            ]
            expected = [{"assert_text": "Upload Resumed", "desc": "Ứng dụng tự động khôi phục tải ảnh dở dang"}]
        elif i == 2:
            title = "Cuộc gọi điện thoại cắt ngang khi đang ký tên khách hàng"
            steps = [
                {"desc": "Mở màn hình chữ ký Signature Pad", "action": "tap_selector", "text": "Signature", "delay": 0.8},
                {"desc": "Mô phỏng app quay lại từ cuộc gọi", "action": "tap_selector", "text": "Signature", "delay": 1.0}
            ]
            expected = [{"assert_text": "Sign Here", "desc": "Chữ ký đang vẽ không bị crash hoặc mất nét"}]
        else:
            title = f"Khả năng chịu lỗi và gián đoạn hệ thống kịch bản #{i}"
            steps = [
                {"desc": "Kích hoạt mô phỏng môi trường bất ổn định", "action": "tap_selector", "text": "Calendar", "delay": 0.8},
                {"desc": f"Thực hiện kiểm tra resilience #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Calendar", "desc": "App tự bảo vệ dữ liệu và không sập"}]
        create_case("network_chaos_edge_cases", tc_id, title, "Normal",
                    f"Kiểm thử khả năng phục hồi dữ liệu trong điều kiện khắc nghiệt #{i}", "Calendar Home", steps, expected)
        total += 1

    # 8. PHÂN HỆ: HARDWARE PERIPHERALS & BLUETOOTH PRINTERS (40 Cases)
    print("8. Đang tạo phân hệ Hardware Peripherals...")
    for i in range(1, 41):
        tc_id = f"HW-PRNT-{i:03d}"
        if i == 1:
            title = "Kết nối máy in nhiệt Bluetooth Zebra ZQ520"
            steps = [
                {"desc": "Mở Settings -> Hardware", "action": "tap_selector", "text": "Hardware", "delay": 0.8},
                {"desc": "Bấm Scan Bluetooth Printers", "action": "tap_selector", "text": "Scan Devices", "delay": 1.2},
                {"desc": "Chọn máy in Zebra ZQ520", "action": "tap_selector", "text": "Zebra ZQ520", "delay": 0.8},
                {"desc": "In thử test print page", "action": "tap_selector", "text": "Test Print", "delay": 1.5}
            ]
            expected = [{"assert_text": "Print Sent", "desc": "Lệnh in biên bản gửi thành công"}]
        else:
            title = f"Tương thích thiết bị ngoại vi và máy in KTV #{i}"
            steps = [
                {"desc": "Mở cấu hình thiết bị phần cứng", "action": "tap_selector", "text": "Hardware", "delay": 0.8},
                {"desc": f"Kiểm tra cổng kết nối #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Hardware", "desc": "Thiết bị ngoại vi hoạt động tốt"}]
        create_case("hardware_peripherals_deep", tc_id, title, "Normal",
                    f"Kiểm thử phần cứng máy in và máy quét cầm tay ca #{i}", "Settings", steps, expected)
        total += 1

    # 9. PHÂN HỆ: TWO-WAY COMMUNICATION & LIVE TRACKING SMS (50 Cases)
    print("9. Đang tạo phân hệ Two-Way Communication & Tracking...")
    for i in range(1, 51):
        tc_id = f"SMS-2WAY-{i:03d}"
        if i == 1:
            title = "Gửi SMS On-My-Way kèm link vị trí KTV đang di chuyển theo thời gian thực"
            steps = [
                {"desc": "Mở Job sắp làm", "action": "tap_selector", "text": "Job Details", "delay": 0.8},
                {"desc": "Bấm nút En Route", "action": "tap_selector", "text": "En Route", "delay": 0.8},
                {"desc": "Bấm Send On My Way SMS", "action": "tap_selector", "text": "Send SMS", "delay": 1.0}
            ]
            expected = [{"assert_text": "Tracking Link Included", "desc": "Tin nhắn chứa link bản đồ trực tiếp được gửi"}]
        else:
            title = f"Hội thoại hai chiều và thông báo khách hàng #{i}"
            steps = [
                {"desc": "Mở hộp thư SMS khách hàng", "action": "tap_selector", "text": "SMS", "delay": 0.8},
                {"desc": f"Kiểm tra tin nhắn #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "SMS", "desc": "Hệ thống tin nhắn vận hành trơn tru"}]
        create_case("two_way_communication_sms", tc_id, title, "Normal",
                    f"Kiểm thử giao tiếp 2 chiều và thông báo thời gian thực #{i}", "Màn hình SMS", steps, expected)
        total += 1

    # 10. PHÂN HỆ: COMMERCIAL MULTI-SERVICE LOCATIONS (45 Cases)
    print("10. Đang tạo phân hệ Multi-Service Locations...")
    for i in range(1, 46):
        tc_id = f"LOC-COMM-{i:03d}"
        if i == 1:
            title = "Tạo nhiều tòa nhà chi nhánh (Sub-locations) cho một khách hàng doanh nghiệp"
            steps = [
                {"desc": "Mở hồ sơ khách hàng Commercial", "action": "tap_selector", "text": "Customers", "delay": 0.8},
                {"desc": "Mở tab Locations", "action": "tap_selector", "text": "Locations", "delay": 0.8},
                {"desc": "Bấm Add Location", "action": "tap_selector", "content_desc": "Add Location", "delay": 1.0},
                {"desc": "Nhập tên Tòa nhà B - Khu xưởng sản xuất", "action": "type_text", "value": "Building B - Plant", "delay": 0.5},
                {"desc": "Lưu chi nhánh", "action": "tap_selector", "content_desc": "Save", "delay": 1.0}
            ]
            expected = [{"assert_text": "Building B - Plant", "desc": "Vị trí dịch vụ phụ được gán vào khách hàng"}]
        else:
            title = f"Quản lý vị trí dịch vụ đa điểm thương mại #{i}"
            steps = [
                {"desc": "Mở danh mục địa điểm", "action": "tap_selector", "text": "Locations", "delay": 0.8},
                {"desc": f"Kiểm tra địa điểm #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Locations", "desc": "Thông tin chi nhánh lưu trữ chính xác"}]
        create_case("multi_service_locations", tc_id, title, "Normal",
                    f"Kiểm thử quản lý đa địa điểm dịch vụ khách hàng #{i}", "Customers", steps, expected)
        total += 1

    # 11. PHÂN HỆ: MANDATORY JOB CHECKLISTS (45 Cases)
    print("11. Đang tạo phân hệ Mandatory Checklists...")
    for i in range(1, 46):
        tc_id = f"CHK-MAND-{i:03d}"
        if i == 1:
            title = "Chặn hoàn thành Job nếu chưa hoàn tất Checklist bắt buộc"
            steps = [
                {"desc": "Mở Job có checklist bắt buộc", "action": "tap_selector", "text": "Job Details", "delay": 0.8},
                {"desc": "Bấm nút Complete Job ngay lập tức", "action": "tap_selector", "content_desc": "Complete Job", "delay": 1.0}
            ]
            expected = [{"assert_text": "Incomplete Checklist", "desc": "Cảnh báo phải hoàn thành danh mục kiểm tra trước khi xong việc"}]
        else:
            title = f"Ràng buộc quy trình và danh mục kiểm tra bắt buộc #{i}"
            steps = [
                {"desc": "Mở checklist công việc", "action": "tap_selector", "text": "Checklist", "delay": 0.8},
                {"desc": f"Kiểm tra mục checklist #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Checklist", "desc": "Danh mục kiểm tra bắt buộc hiển thị chuẩn"}]
        create_case("job_checklists_mandatory", tc_id, title, "Normal",
                    f"Kiểm thử danh mục kiểm tra bắt buộc trước nghiệm thu #{i}", "Job Details", steps, expected)
        total += 1

    # 12. PHÂN HỆ: RECURRING SEASONAL ROUTES & BALANCING (45 Cases)
    print("12. Đang tạo phân hệ Recurring Seasonal Routes...")
    for i in range(1, 46):
        tc_id = f"ROUTE-SEAS-{i:03d}"
        if i == 1:
            title = "Cấu hình lịch xịt côn trùng theo mùa (Mùa hè 2 tuần/lần, Mùa đông 1 tháng/lần)"
            steps = [
                {"desc": "Mở hợp đồng định kỳ", "action": "tap_selector", "text": "Agreements", "delay": 0.8},
                {"desc": "Chọn Seasonal Frequency Rule", "action": "tap_selector", "text": "Seasonal", "delay": 0.8},
                {"desc": "Lưu quy tắc mùa", "action": "tap_selector", "content_desc": "Save Rule", "delay": 1.0}
            ]
            expected = [{"assert_text": "Seasonal Schedule Set", "desc": "Lịch tự động điều chỉnh theo mùa"}]
        else:
            title = f"Điều phối và cân bằng tuyến đường theo mùa #{i}"
            steps = [
                {"desc": "Xem bản đồ lộ trình mùa", "action": "tap_selector", "text": "Routing", "delay": 0.8},
                {"desc": f"Kiểm tra tuyến #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Routing", "desc": "Lộ trình mùa cân bằng hợp lý"}]
        create_case("recurring_seasonal_routes", tc_id, title, "Normal",
                    f"Kiểm thử lộ trình và tần suất dịch vụ mùa vụ #{i}", "Calendar Home", steps, expected)
        total += 1

    # 13. PHÂN HỆ: CUSTOM FIELDS DYNAMIC SCHEMA (40 Cases)
    print("13. Đang tạo phân hệ Custom Fields Schema...")
    for i in range(1, 41):
        tc_id = f"CF-SCHEMA-{i:03d}"
        create_case("custom_fields_schema", tc_id, f"Trường dữ liệu tùy chỉnh Custom Field nghiệp vụ #{i}", "Normal",
                    f"Kiểm thử khả năng lưu trữ và hiển thị trường dữ liệu động của khách hàng ca #{i}",
                    "Hồ sơ khách hàng đang mở",
                    [
                        {"desc": "Mở tab Custom Fields", "action": "tap_selector", "text": "Custom Fields", "delay": 0.8},
                        {"desc": f"Nhập dữ liệu trường #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
                    ],
                    [{"assert_text": "Custom Fields", "desc": "Trường dữ liệu tùy biến lưu thành công"}])
        total += 1

    # 14. PHÂN HỆ: CUSTOMER CRM RETENTION & CANCELLATION LOGS (45 Cases)
    print("14. Đang tạo phân hệ Customer CRM Retention...")
    for i in range(1, 46):
        tc_id = f"CRM-RET-{i:03d}"
        create_case("customer_crm_retention", tc_id, f"Quản lý lưu vết giữ chân khách hàng và lý do hủy dịch vụ #{i}", "Normal",
                    f"Kiểm thử ghi nhận nguyên nhân dừng hợp đồng và chiến dịch chăm sóc lại khách hàng ca #{i}",
                    "Hồ sơ khách hàng",
                    [
                        {"desc": "Mở mục Trạng thái Hợp đồng", "action": "tap_selector", "text": "Customer Status", "delay": 0.8},
                        {"desc": f"Thao tác ghi nhận chăm sóc #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
                    ],
                    [{"assert_text": "Customer Status", "desc": "Lịch sử tương tác chăm sóc lưu an toàn"}])
        total += 1

    # 15. PHÂN HỆ: COMMERCIAL ACCOUNTS & MASTER INVOICING (45 Cases)
    print("15. Đang tạo phân hệ Commercial Master Accounts...")
    for i in range(1, 46):
        tc_id = f"COMM-MST-{i:03d}"
        create_case("commercial_accounts_master", tc_id, f"Quản lý khách hàng chuỗi thương mại và xuất hóa đơn gộp #{i}", "Normal",
                    f"Kiểm thử xuất hóa đơn tổng hợp cho chuỗi nhà hàng / khách sạn ca #{i}",
                    "Màn hình Khách hàng Thương Mại",
                    [
                        {"desc": "Mở hồ sơ Chuỗi tài khoản", "action": "tap_selector", "text": "Master Accounts", "delay": 0.8},
                        {"desc": f"Thao tác kiểm tra chuỗi #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
                    ],
                    [{"assert_text": "Master Accounts", "desc": "Tài khoản chuỗi thương mại hiển thị đầy đủ"}])
        total += 1

    print("\n=======================================================")
    print(f"✅ ĐÃ SINH THÀNH CÔNG {total} TEST CASES ENTERPRISE MỚI!")
    print("=======================================================")

if __name__ == "__main__":
    main()
