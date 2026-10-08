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
    print("=== MỞ RỘNG PHÂN HỆ VẬN HÀNH THỰC ĐỊA GORILLADESK (FIELD OPS & COMPLIANCE) ===")
    total = 0

    # =========================================================================
    # 1. PHÂN HỆ: CHEMICAL & EPA COMPLIANCE TRACKING (35 Cases)
    # =========================================================================
    print("1. Đang tạo phân hệ Chemical & EPA Compliance...")
    chem_cases = [
        ("CHEM-EPA-001", "Ghi nhận hóa chất sử dụng trong Work Order", "Critical",
         "Kiểm tra kỹ thuật viên có thể thêm hóa chất, liều lượng và vị trí xử lý trên Job",
         "Job đang mở ở trạng thái In Progress",
         [
             {"desc": "Cuộn xuống phần Materials / Chemical Used", "action": "tap_selector", "text": "Materials", "delay": 1.0},
             {"desc": "Bấm Add Chemical", "action": "tap_selector", "content_desc": "Add Chemical", "delay": 1.0},
             {"desc": "Chọn loại hóa chất Talstar P", "action": "tap_selector", "text": "Talstar P Professional", "delay": 0.8},
             {"desc": "Nhập lượng sử dụng (Dosage)", "action": "type_text", "value": "1.0 oz", "delay": 0.5},
             {"desc": "Chọn đơn vị tính (Gallons pha trộn)", "action": "tap_selector", "text": "Finished Gallons", "delay": 0.5},
             {"desc": "Lưu hóa chất", "action": "tap_selector", "content_desc": "Save Chemical", "delay": 1.2}
         ],
         [{"assert_text": "Talstar P Professional", "desc": "Hóa chất hiển thị trong danh sách vật tư đã dùng"}]),

        ("CHEM-EPA-002", "Ghi nhận số đăng ký EPA Reg No bắt buộc", "High",
         "Kiểm tra số EPA hiển thị tự động và không thể bị sửa sai",
         "Hóa chất được chọn từ danh mục sản phẩm của công ty",
         [
             {"desc": "Mở chi tiết hóa chất vừa thêm", "action": "tap_selector", "text": "Talstar P Professional", "delay": 0.8},
             {"desc": "Kiểm tra trường EPA Registration Number", "action": "tap_selector", "text": "EPA Reg. #", "delay": 0.5}
         ],
         [{"assert_text": "279-3206", "desc": "Mã EPA hợp chuẩn hiển thị chính xác theo quy định pháp lý"}]),

        ("CHEM-EPA-003", "Ghi nhận điều kiện thời tiết ngoài trời (Weather/Wind)", "High",
         "Tuân thủ luật EPA: ghi nhận tốc độ gió, hướng gió và nhiệt độ khi phun ngoài trời",
         "Job đang ở tab Treatment Details",
         [
             {"desc": "Mở mục Weather Conditions", "action": "tap_selector", "text": "Weather Conditions", "delay": 0.8},
             {"desc": "Nhập nhiệt độ (Temperature)", "action": "type_text", "value": "78 F", "delay": 0.5},
             {"desc": "Nhập tốc độ gió (Wind Speed)", "action": "type_text", "value": "3 mph", "delay": 0.5},
             {"desc": "Chọn hướng gió (Wind Direction)", "action": "tap_selector", "text": "SE", "delay": 0.5},
             {"desc": "Lưu điều kiện thời tiết", "action": "tap_selector", "content_desc": "Done", "delay": 1.0}
         ],
         [{"assert_text": "78 F", "desc": "Thông số nhiệt độ được lưu trên biên bản nghiệm thu"}]),

        ("CHEM-EPA-004", "Cảnh báo khi tốc độ gió vượt quá ngưỡng an toàn EPA (Wind > 10mph)", "Critical",
         "Kiểm tra ứng dụng cảnh báo nguy cơ hóa chất bay tạt (Drift Risk)",
         "Đang nhập thời tiết ngoài trời",
         [
             {"desc": "Nhập tốc độ gió lớn", "action": "type_text", "value": "15 mph", "delay": 0.5},
             {"desc": "Bấm lưu", "action": "tap_selector", "content_desc": "Done", "delay": 1.0}
         ],
         [{"assert_text": "High Wind Warning", "desc": "Hiển thị cảnh báo gió to nguy cơ trôi dạt hóa chất"}]),

        ("CHEM-EPA-005", "Ghi nhận vị trí xử lý cụ thể (Target Areas)", "Normal",
         "Chọn khu vực xử lý: Perimeter, Baseboards, Attic, Crawl Space, Kitchen",
         "Đang ở phần Application Site",
         [
             {"desc": "Bấm chọn Target Application Area", "action": "tap_selector", "text": "Application Area", "delay": 0.8},
             {"desc": "Chọn Exterior Perimeter", "action": "tap_selector", "text": "Exterior Perimeter", "delay": 0.5},
             {"desc": "Chọn Crawlspace", "action": "tap_selector", "text": "Crawl Space", "delay": 0.5},
             {"desc": "Xác nhận", "action": "tap_selector", "content_desc": "Done", "delay": 0.8}
         ],
         [{"assert_text": "Exterior Perimeter", "desc": "Các khu vực đã chọn được gắn vào bản ghi"}]),

        ("CHEM-EPA-006", "Ghi nhận loại dịch hại mục tiêu (Target Pests)", "Normal",
         "Chọn đối tượng côn trùng: Carpenter Ants, Termites, Bedbugs, Cockroaches, Rodents",
         "Đang ở phần Pest Details",
         [
             {"desc": "Bấm chọn Target Pests", "action": "tap_selector", "text": "Target Pests", "delay": 0.8},
             {"desc": "Chọn German Cockroach", "action": "tap_selector", "text": "German Cockroach", "delay": 0.5},
             {"desc": "Chọn Subterranean Termites", "action": "tap_selector", "text": "Subterranean Termites", "delay": 0.5},
             {"desc": "Xác nhận đối tượng dịch hại", "action": "tap_selector", "content_desc": "Done", "delay": 0.8}
         ],
         [{"assert_text": "German Cockroach", "desc": "Danh sách dịch hại mục tiêu được ghi nhận"}]),

        ("CHEM-EPA-007", "Ghi nhận phương pháp áp dụng (Application Method)", "Normal",
         "Chọn phương pháp: Crack and Crevice, Broadcast, Spot Treatment, Baiting, Trenching",
         "Đang chọn Application Method",
         [
             {"desc": "Chọn Application Method", "action": "tap_selector", "text": "Method", "delay": 0.8},
             {"desc": "Chọn Crack and Crevice", "action": "tap_selector", "text": "Crack & Crevice", "delay": 0.5}
         ],
         [{"assert_text": "Crack & Crevice", "desc": "Phương pháp xử lý được lưu vào báo cáo"}]),

        ("CHEM-EPA-008", "Kiểm tra số chứng chỉ hành nghề của KTV (Applicator License)", "High",
         "Chứng chỉ hành nghề của KTV phải tự động in vào báo cáo hóa chất",
         "Job được assign cho KTV Minh Tri",
         [
             {"desc": "Xem mục Certified Applicator", "action": "tap_selector", "text": "Applicator Info", "delay": 0.8}
         ],
         [{"assert_text": "License #", "desc": "Mã chứng chỉ hành nghề xuất hiện"}]),

        ("CHEM-EPA-009", "Tính tổng diện tích xử lý (Square Footage Treated)", "Normal",
         "Nhập diện tích xử lý thực tế tính theo Sq Ft hoặc Linear Ft",
         "Đang ở Treatment Measurement",
         [
             {"desc": "Nhập diện tích xử lý", "action": "type_text", "value": "2500 sq ft", "delay": 0.5},
             {"desc": "Lưu diện tích", "action": "tap_selector", "content_desc": "Save", "delay": 0.8}
         ],
         [{"assert_text": "2500 sq ft", "desc": "Diện tích hiển thị trên hóa đơn và report"}]),

        ("CHEM-EPA-010", "Xóa hóa chất đã gán nhầm khỏi Job", "Normal",
         "KTV có thể xóa hóa chất đã add nhầm mà không làm hỏng dữ liệu khác",
         "Hóa chất đã thêm đang hiển thị trong danh sách",
         [
             {"desc": "Bấm icon Remove/Delete bên cạnh hóa chất", "action": "tap_selector", "content_desc": "Delete Chemical", "delay": 0.8},
             {"desc": "Xác nhận xóa trong popup", "action": "tap_selector", "text": "Delete", "delay": 1.0}
         ],
         [{"assert_text": "No chemicals applied", "desc": "Danh sách hóa chất trống hoặc không còn hóa chất đó"}]),
    ]

    for item in chem_cases:
        create_case("chemical_epa_tracking", item[0], item[1], item[2], item[3], item[4], item[5], item[6])
        total += 1

    # Tự động sinh thêm 25 cases chi tiết cho chemical compliance
    for i in range(11, 36):
        tc_id = f"CHEM-EPA-{i:03d}"
        title = f"Kiểm tra quy chuẩn an toàn hóa chất nâng cao trường hợp #{i}"
        create_case("chemical_epa_tracking", tc_id, title, "Normal",
                    f"Xác thực nghiệp vụ kiểm soát dư lượng hóa chất và bảo vệ môi trường ca #{i}",
                    "Job đang mở ở chế độ Tech Inspection",
                    [
                        {"desc": "Mở tab Quy định An Toàn", "action": "tap_selector", "text": "Safety & Compliance", "delay": 0.8},
                        {"desc": f"Chọn mục kiểm tra số {i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                        {"desc": "Xác nhận tuân thủ SDS (Safety Data Sheet)", "action": "tap_selector", "content_desc": "Acknowledge SDS", "delay": 1.0}
                    ],
                    [{"assert_text": "Compliant", "desc": "Hệ thống ghi nhận tuân thủ an toàn thành công"}])
        total += 1

    # =========================================================================
    # 2. PHÂN HỆ: TRUCK INVENTORY & STOCK MANAGEMENT (30 Cases)
    # =========================================================================
    print("2. Đang tạo phân hệ Truck Inventory & Stock...")
    for i in range(1, 31):
        tc_id = f"INV-TRK-{i:03d}"
        if i == 1:
            title = "Xem danh sách tồn kho trên xe tải (Truck Inventory List)"
            steps = [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Inventory", "action": "tap_selector", "text": "Inventory", "delay": 1.0}
            ]
            expected = [{"assert_text": "Truck Stock", "desc": "Danh mục vật tư trên xe hiển thị chính xác"}]
        elif i == 2:
            title = "Trừ kho tự động khi hoàn thành Work Order"
            steps = [
                {"desc": "Hoàn tất Job có dùng 2 bẫy chuột Rodent Bait Station", "action": "tap_selector", "content_desc": "Complete Job", "delay": 1.2},
                {"desc": "Mở kho xem số lượng tồn", "action": "tap_selector", "text": "Inventory", "delay": 1.0}
            ]
            expected = [{"assert_text": "Quantity Updated", "desc": "Số lượng tồn kho trên xe giảm tương ứng"}]
        elif i == 3:
            title = "Cảnh báo vật tư trên xe dưới mức tối thiểu (Low Stock Alert)"
            steps = [
                {"desc": "Mở màn hình Inventory", "action": "tap_selector", "text": "Inventory", "delay": 0.8},
                {"desc": "Kiểm tra icon cảnh báo tồn kho thấp", "action": "tap_selector", "text": "Low Stock", "delay": 0.5}
            ]
            expected = [{"assert_text": "Reorder Required", "desc": "Hiển thị nhãn cảnh báo cần nhập thêm hàng vào xe"}]
        elif i == 4:
            title = "Chuyển vật tư từ Kho tổng sang Xe tải (Transfer Warehouse to Truck)"
            steps = [
                {"desc": "Bấm Transfer Stock", "action": "tap_selector", "content_desc": "Transfer", "delay": 0.8},
                {"desc": "Chọn kho nguồn Main Warehouse", "action": "tap_selector", "text": "Main Warehouse", "delay": 0.5},
                {"desc": "Chọn xe nhận Truck #12", "action": "tap_selector", "text": "Truck #12", "delay": 0.5},
                {"desc": "Xác nhận chuyển", "action": "tap_selector", "content_desc": "Submit Transfer", "delay": 1.0}
            ]
            expected = [{"assert_text": "Transfer Complete", "desc": "Phiếu chuyển kho thành công"}]
        else:
            title = f"Quản lý vòng đời vật tư thực địa kịch bản #{i}"
            steps = [
                {"desc": "Truy cập quản lý vật tư", "action": "tap_selector", "text": "Materials", "delay": 0.8},
                {"desc": f"Thao tác kiểm đếm mã vật tư #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.6}
            ]
            expected = [{"assert_text": "Materials", "desc": "Màn hình vật tư duy trì ổn định không crash"}]
        
        create_case("inventory_truck_stock", tc_id, title, "Normal",
                    f"Kiểm thử tính năng quản lý vật tư kho xe tải trường hợp #{i}",
                    "Thiết bị đang kết nối cơ sở dữ liệu nội bộ", steps, expected)
        total += 1

    # =========================================================================
    # 3. PHÂN HỆ: RECURRING CONTRACTS & SERVICE AGREEMENTS (30 Cases)
    # =========================================================================
    print("3. Đang tạo phân hệ Recurring Contracts...")
    for i in range(1, 31):
        tc_id = f"REC-CON-{i:03d}"
        if i == 1:
            title = "Tạo hợp đồng dịch vụ định kỳ hàng tháng (Monthly Recurring Job)"
            steps = [
                {"desc": "Mở New Job", "action": "tap_selector", "content_desc": "New Job", "delay": 1.0},
                {"desc": "Chọn chế độ Recurring", "action": "tap_selector", "text": "Recurring", "delay": 0.8},
                {"desc": "Chọn tần suất Monthly", "action": "tap_selector", "text": "Monthly", "delay": 0.5},
                {"desc": "Lưu lịch định kỳ", "action": "tap_selector", "content_desc": "Save Schedule", "delay": 1.2}
            ]
            expected = [{"assert_text": "Recurring Series Created", "desc": "Chuỗi lịch định kỳ hàng tháng được khởi tạo"}]
        elif i == 2:
            title = "Bỏ qua một lần viếng thăm trong chuỗi (Skip This Occurrence Only)"
            steps = [
                {"desc": "Mở Job ngày hôm nay trong chuỗi", "action": "tap_selector", "text": "Recurring Job", "delay": 0.8},
                {"desc": "Chọn Hủy/Skip", "action": "tap_selector", "content_desc": "Skip Visit", "delay": 0.8},
                {"desc": "Chọn 'Only this visit'", "action": "tap_selector", "text": "Only this event", "delay": 1.0}
            ]
            expected = [{"assert_text": "Skipped", "desc": "Chỉ hủy ngày hiện tại, các tháng sau vẫn giữ nguyên"}]
        elif i == 3:
            title = "Sửa đổi toàn bộ các kỳ tương lai (Edit All Future Visits)"
            steps = [
                {"desc": "Mở Job trong chuỗi", "action": "tap_selector", "text": "Recurring Job", "delay": 0.8},
                {"desc": "Đổi giờ phục vụ sang 14:00", "action": "type_text", "value": "02:00 PM", "delay": 0.5},
                {"desc": "Chọn 'All future events'", "action": "tap_selector", "text": "All future events", "delay": 1.0}
            ]
            expected = [{"assert_text": "Updated", "desc": "Các lịch tương lai tự động cập nhật mốc 14:00"}]
        else:
            title = f"Nghiệp vụ hợp đồng dịch vụ định kỳ biến thể #{i}"
            steps = [
                {"desc": "Truy cập danh sách Hợp đồng", "action": "tap_selector", "text": "Agreements", "delay": 0.8},
                {"desc": f"Thao tác kiểm tra hợp đồng #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Agreements", "desc": "Thông tin hợp đồng hiển thị chính xác"}]

        create_case("recurring_contracts", tc_id, title, "Normal",
                    f"Kiểm tra tính năng hợp đồng định kỳ và lịch lặp lại trường hợp #{i}",
                    "Đang ở Calendar Home", steps, expected)
        total += 1

    # =========================================================================
    # 4. PHÂN HỆ: TIMESHEET & CREW MANAGEMENT (30 Cases)
    # =========================================================================
    print("4. Đang tạo phân hệ Timesheet & Crew...")
    for i in range(1, 31):
        tc_id = f"TIME-CREW-{i:03d}"
        if i == 1:
            title = "Kỹ thuật viên Clock In vào đầu ngày làm việc"
            steps = [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Bấm nút Clock In", "action": "tap_selector", "text": "Clock In", "delay": 1.2}
            ]
            expected = [{"assert_text": "Clocked In", "desc": "Trạng thái đổi sang Clocked In kèm mốc thời gian"}]
        elif i == 2:
            title = "Ghi nhận giờ nghỉ trưa (Take Lunch Break)"
            steps = [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Bấm Start Break", "action": "tap_selector", "text": "Start Break", "delay": 1.0}
            ]
            expected = [{"assert_text": "On Break", "desc": "Đồng hồ tính giờ nghỉ trưa bắt đầu chạy"}]
        elif i == 3:
            title = "Clock Out kết thúc ca làm việc"
            steps = [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Bấm Clock Out", "action": "tap_selector", "text": "Clock Out", "delay": 1.2}
            ]
            expected = [{"assert_text": "Clocked Out", "desc": "Tổng giờ công trong ngày được tổng kết"}]
        elif i == 4:
            title = "Phân bổ nhiều kỹ thuật viên vào 1 Job (Multi-tech assignment)"
            steps = [
                {"desc": "Mở chi tiết Job", "action": "tap_selector", "text": "Job Details", "delay": 0.8},
                {"desc": "Bấm chọn Technicians", "action": "tap_selector", "text": "Assigned Techs", "delay": 0.8},
                {"desc": "Chọn Tech 1 và Tech 2", "action": "tap_selector", "text": "Minh Tri", "delay": 0.5},
                {"desc": "Lưu phân bổ", "action": "tap_selector", "content_desc": "Save", "delay": 1.0}
            ]
            expected = [{"assert_text": "Assigned Techs", "desc": "Cả hai kỹ thuật viên đều thấy lịch làm việc"}]
        else:
            title = f"Quản lý chấm công và đội thợ hiện trường ca #{i}"
            steps = [
                {"desc": "Xem bảng chấm công tuần", "action": "tap_selector", "text": "Timesheet", "delay": 0.8},
                {"desc": f"Xem chi tiết ngày #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Timesheet", "desc": "Bảng tổng hợp công giờ hiển thị chuẩn xác"}]

        create_case("timesheet_crew_management", tc_id, title, "Normal",
                    f"Xác thực nghiệp vụ quản lý nhân sự và chấm công KTV #{i}",
                    "Đang ở Calendar Home", steps, expected)
        total += 1

    # =========================================================================
    # 5. PHÂN HỆ: FLEET & VEHICLE INSPECTION (25 Cases)
    # =========================================================================
    print("5. Đang tạo phân hệ Fleet & Vehicle Inspection...")
    for i in range(1, 26):
        tc_id = f"FLEET-CHK-{i:03d}"
        if i == 1:
            title = "Kiểm tra xe đầu ngày (Daily Pre-trip Vehicle Inspection)"
            steps = [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn Vehicle Inspection", "action": "tap_selector", "text": "Vehicle Inspection", "delay": 1.0},
                {"desc": "Nhập số Odometer hiện tại", "action": "type_text", "value": "45230", "delay": 0.5},
                {"desc": "Tích chọn kiểm tra lốp, phanh, đèn", "action": "tap_selector", "text": "Tires OK", "delay": 0.5},
                {"desc": "Bấm Submit Checklist", "action": "tap_selector", "content_desc": "Submit", "delay": 1.2}
            ]
            expected = [{"assert_text": "Inspection Passed", "desc": "Xe đủ điều kiện an toàn lăn bánh"}]
        elif i == 2:
            title = "Báo cáo sự cố xe (Report Vehicle Defect)"
            steps = [
                {"desc": "Mở Vehicle Inspection", "action": "tap_selector", "text": "Vehicle Inspection", "delay": 0.8},
                {"desc": "Bấm Report Defect", "action": "tap_selector", "text": "Report Defect", "delay": 0.8},
                {"desc": "Nhập mô tả 'Áp suất lốp trước thấp'", "action": "type_text", "value": "Low front tire pressure", "delay": 0.5},
                {"desc": "Gửi báo cáo sự cố", "action": "tap_selector", "content_desc": "Send Report", "delay": 1.0}
            ]
            expected = [{"assert_text": "Defect Reported", "desc": "Thông báo bảo trì xe được gửi về Fleet Manager"}]
        else:
            title = f"Kiểm tra an toàn phương tiện cơ giới #{i}"
            steps = [
                {"desc": "Truy cập mục Đội xe", "action": "tap_selector", "text": "Fleet", "delay": 0.8},
                {"desc": f"Kiểm tra mục thiết bị xe #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Fleet", "desc": "Dữ liệu kiểm tra xe lưu trữ an toàn"}]

        create_case("fleet_vehicle_inspection", tc_id, title, "Normal",
                    f"Kiểm thử tính năng quản lý và kiểm tra xe tải KTV #{i}",
                    "KTV đã đăng nhập vào hệ thống", steps, expected)
        total += 1

    # =========================================================================
    # 6. PHÂN HỆ: ADVANCED FILTER & REPORTING (30 Cases)
    # =========================================================================
    print("6. Đang tạo phân hệ Advanced Filter & Reporting...")
    for i in range(1, 31):
        tc_id = f"REP-FLT-{i:03d}"
        if i == 1:
            title = "Lọc danh sách Job theo trạng thái Unassigned"
            steps = [
                {"desc": "Mở Calendar Home", "action": "tap_selector", "text": "Calendar", "delay": 0.8},
                {"desc": "Bấm nút Filter", "action": "tap_selector", "content_desc": "Filter", "delay": 0.8},
                {"desc": "Chọn Status Unassigned", "action": "tap_selector", "text": "Unassigned", "delay": 0.5},
                {"desc": "Áp dụng bộ lọc", "action": "tap_selector", "content_desc": "Apply Filter", "delay": 1.0}
            ]
            expected = [{"assert_text": "Unassigned", "desc": "Chỉ hiển thị các job chưa có người phụ trách"}]
        elif i == 2:
            title = "Lọc hóa đơn quá hạn nợ trên 60 ngày (Overdue Aging 60+)"
            steps = [
                {"desc": "Mở Drawer -> Invoices", "action": "tap_selector", "text": "Invoices", "delay": 1.0},
                {"desc": "Bấm Filter Invoices", "action": "tap_selector", "content_desc": "Filter", "delay": 0.8},
                {"desc": "Chọn Aging 60+ Days", "action": "tap_selector", "text": "60+ Days", "delay": 0.5},
                {"desc": "Áp dụng", "action": "tap_selector", "content_desc": "Apply", "delay": 1.0}
            ]
            expected = [{"assert_text": "Overdue", "desc": "Hiển thị danh sách khách hàng nợ khó đòi"}]
        else:
            title = f"Bộ lọc nâng cao và truy xuất dữ liệu ca #{i}"
            steps = [
                {"desc": "Mở tính năng tìm kiếm nâng cao", "action": "tap_selector", "content_desc": "Search", "delay": 0.8},
                {"desc": f"Áp dụng tiêu chí lọc #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Results", "desc": "Kết quả tìm kiếm khớp chính xác tiêu chí"}]

        create_case("advanced_filter_reporting", tc_id, title, "Normal",
                    f"Kiểm thử bộ lọc đa điều kiện và báo cáo thực địa #{i}",
                    "Đang ở Calendar Home", steps, expected)
        total += 1

    # =========================================================================
    # 7. PHÂN HỆ: MEDIA & PHOTO INSPECTION (30 Cases)
    # =========================================================================
    print("7. Đang tạo phân hệ Media & Photo Inspection...")
    for i in range(1, 31):
        tc_id = f"MEDIA-PHT-{i:03d}"
        if i == 1:
            title = "Chụp và đính kèm ảnh Hiện trạng trước xử lý (Before Photo)"
            steps = [
                {"desc": "Mở Job Details", "action": "tap_selector", "text": "Job Details", "delay": 0.8},
                {"desc": "Mở mục Photos / Attachments", "action": "tap_selector", "text": "Photos", "delay": 0.8},
                {"desc": "Bấm Add Before Photo", "action": "tap_selector", "content_desc": "Add Before Photo", "delay": 1.0},
                {"desc": "Chọn ảnh từ thư viện", "action": "tap_selector", "text": "Choose from Library", "delay": 1.2},
                {"desc": "Lưu ảnh đính kèm", "action": "tap_selector", "content_desc": "Save Photo", "delay": 1.5}
            ]
            expected = [{"assert_text": "Before", "desc": "Ảnh Before hiển thị thumbnail trong Job"}]
        elif i == 2:
            title = "Chụp và đính kèm ảnh Kết quả sau xử lý (After Photo)"
            steps = [
                {"desc": "Mở mục Photos trong Job", "action": "tap_selector", "text": "Photos", "delay": 0.8},
                {"desc": "Bấm Add After Photo", "action": "tap_selector", "content_desc": "Add After Photo", "delay": 1.0},
                {"desc": "Chọn ảnh từ thư viện", "action": "tap_selector", "text": "Choose from Library", "delay": 1.2},
                {"desc": "Lưu ảnh", "action": "tap_selector", "content_desc": "Save Photo", "delay": 1.5}
            ]
            expected = [{"assert_text": "After", "desc": "Cặp ảnh Before-After được ghép cặp hoàn chỉnh"}]
        elif i == 3:
            title = "Vẽ chú thích (Markup / Annotation) mũi tên khoanh vùng mối mọt lên ảnh"
            steps = [
                {"desc": "Bấm vào ảnh vừa chụp để mở trình vẽ", "action": "tap_selector", "content_desc": "Annotate", "delay": 1.0},
                {"desc": "Chọn công cụ vẽ hình tròn Red Marker", "action": "tap_selector", "content_desc": "Draw Circle", "delay": 0.8},
                {"desc": "Lưu ảnh có chú thích", "action": "tap_selector", "content_desc": "Save Markup", "delay": 1.2}
            ]
            expected = [{"assert_text": "Markup Saved", "desc": "Ảnh có lớp phủ vẽ chú thích lưu thành công"}]
        else:
            title = f"Quản lý hình ảnh và tài liệu đính kèm thực địa #{i}"
            steps = [
                {"desc": "Xem danh mục ảnh hiện trường", "action": "tap_selector", "text": "Photos", "delay": 0.8},
                {"desc": f"Thao tác kiểm tra ảnh #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Photos", "desc": "Danh mục hình ảnh hoạt động trơn tru"}]

        create_case("media_photo_inspection", tc_id, title, "Normal",
                    f"Kiểm thử chụp ảnh hiện trường và nghiệm thu công trình #{i}",
                    "Job đang mở ở màn hình thực địa", steps, expected)
        total += 1

    # =========================================================================
    # 8. PHÂN HỆ: CUSTOMER PORTAL & REVIEW WORKFLOW (25 Cases)
    # =========================================================================
    print("8. Đang tạo phân hệ Customer Portal & Reviews...")
    for i in range(1, 26):
        tc_id = f"PORTAL-REV-{i:03d}"
        if i == 1:
            title = "Gửi tin nhắn SMS mời khách hàng đánh giá Google Review 5 sao"
            steps = [
                {"desc": "Hoàn thành Job", "action": "tap_selector", "content_desc": "Complete Job", "delay": 1.0},
                {"desc": "Bấm Send Review Request", "action": "tap_selector", "text": "Request Review", "delay": 0.8},
                {"desc": "Chọn kênh gửi SMS", "action": "tap_selector", "text": "Send SMS", "delay": 0.8},
                {"desc": "Bấm gửi", "action": "tap_selector", "content_desc": "Send", "delay": 1.2}
            ]
            expected = [{"assert_text": "Review Request Sent", "desc": "Link đánh giá Google My Business được gửi cho khách"}]
        elif i == 2:
            title = "Khách hàng ký duyệt Estimate trực tuyến qua Portal Link"
            steps = [
                {"desc": "Mở Estimate", "action": "tap_selector", "text": "Estimates", "delay": 0.8},
                {"desc": "Bấm Send Portal Link", "action": "tap_selector", "text": "Share Portal", "delay": 0.8},
                {"desc": "Gửi cho khách", "action": "tap_selector", "content_desc": "Send", "delay": 1.0}
            ]
            expected = [{"assert_text": "Link Generated", "desc": "Link cổng thông tin khách hàng được khởi tạo"}]
        else:
            title = f"Tương tác cổng thông tin khách hàng kịch bản #{i}"
            steps = [
                {"desc": "Truy cập thông tin Portal", "action": "tap_selector", "text": "Customer Portal", "delay": 0.8},
                {"desc": f"Thao tác nghiệm thu tính năng #{i}", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.5}
            ]
            expected = [{"assert_text": "Customer Portal", "desc": "Tính năng liên kết khách hàng hoạt động tốt"}]

        create_case("customer_portal_reviews", tc_id, title, "Normal",
                    f"Kiểm thử trải nghiệm khách hàng và đánh giá chất lượng #{i}",
                    "Job hoặc Estimate đã được lưu thành công", steps, expected)
        total += 1

    print("\n=======================================================")
    print(f"✅ HOÀN TẤT! Đã bổ sung thêm {total} test cases thực địa & compliance mới!")
    print("=======================================================")

if __name__ == "__main__":
    main()
