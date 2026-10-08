# Hướng Dẫn Vận Hành Hệ Thống GorillaDesk Automation QA (1,753 Test Cases)

Tài liệu chuẩn dành cho QA Team, Developer và Tech Lead để vận hành bộ kiểm thử tự động hóa 100% Dynamic Selector (Zero Hardcoded Coordinates) trên thiết bị thật.

---

## 1. Nguyên Tắc Cốt Lõi Của Hệ Thống
1. **100% Dynamic Selector First**: Định danh mọi element qua `text`, `content_desc`, `resource_id`. Tuyệt đối không dùng tọa độ pixel cứng (`tap_rel`, `tap_abs`), đảm bảo chạy ổn định trên mọi kích thước màn hình Android.
2. **Deterministic Fast Execution**: Không để LLM suy nghĩ lại từ đầu ở từng bước thao tác cơ bản. Thời gian chạy mỗi test case chỉ mất **10 - 20 giây**.
3. **Multi-layer Assertion**: Mọi bước đều có kiểm tra xác thực UI (UI Text Assertions) và đối soát màn hình.

---

## 2. Chuẩn Bị Thiết Bị (30 giây)
1. Cắm điện thoại Android (Samsung, Pixel...) vào cổng USB máy tính.
2. Đảm bảo điện thoại đã bật **USB Debugging** (Gỡ lỗi USB).
3. Kiểm tra kết nối thiết bị:
   ```cmd
   adb devices -l
   ```
   *(Thấy serial thiết bị kèm trạng thái `device` là sẵn sàng).*

---

## 3. Cài Đặt Thư Viện (1 lần duy nhất)
```cmd
pip install -r requirements.txt
```

---

## 4. Các Cách Chạy Kiểm Thử

### Cách 1: Chạy 1 Test Case Cụ Thể
```cmd
run.bat --test CUSTOMER-CREATE-001
run.bat --test KONG-AI-001
run.bat --test CHEM-EPA-001
run.bat --test TERM-WDO-001
run.bat --test BEDBUG-RM-001
run.bat --test WILD-TRAP-001
run.bat --test VAL-CUS-001
```

### Cách 2: Chạy Theo Phân Hệ Nghiệp Vụ (Suite)
- **Khảo sát mối WDO Inspection (50 cases)**:
  ```cmd
  run.bat --suite module-termite_wdo_inspection
  ```
- **Xử lý rệp từng phòng & Heat Treatment (40 cases)**:
  ```cmd
  run.bat --suite module-bedbug_room_by_room
  ```
- **Bẫy động vật hoang dã & Xịt muỗi (40 cases)**:
  ```cmd
  run.bat --suite module-mosquito_wildlife_trapping
  ```
- **Hóa chất & Quy chuẩn EPA (35 cases)**:
  ```cmd
  run.bat --suite module-chemical_epa_tracking
  ```
- **Bẫy chuột & Bait Stations (50 cases)**:
  ```cmd
  run.bat --suite module-pest_control_deep
  ```
- **Tài chính & Xử lý nợ xấu Invoices (60 cases)**:
  ```cmd
  run.bat --suite module-invoice_advanced_financial
  ```
- **Báo giá đa tầng Good/Better/Best (45 cases)**:
  ```cmd
  run.bat --suite module-estimates_good_better_best
  ```
- **Phân quyền KTV & Bảo mật (50 cases)**:
  ```cmd
  run.bat --suite module-role_based_permissions
  ```
- **Kiểm thử chịu lỗi gián đoạn mạng (60 cases)**:
  ```cmd
  run.bat --suite module-network_chaos_edge_cases
  ```
- **Máy in nhiệt Bluetooth & Quét mã vạch (40 cases)**:
  ```cmd
  run.bat --suite module-hardware_peripherals_deep
  ```
- **Hội thoại SMS 2 chiều & Link vị trí KTV (50 cases)**:
  ```cmd
  run.bat --suite module-two_way_communication_sms
  ```
- **Khách hàng thương mại đa chi nhánh (45 cases)**:
  ```cmd
  run.bat --suite module-multi_service_locations
  ```
- **Danh mục kiểm tra bắt buộc Checklist (45 cases)**:
  ```cmd
  run.bat --suite module-job_checklists_mandatory
  ```
- **Lộ trình dịch vụ theo mùa vụ (45 cases)**:
  ```cmd
  run.bat --suite module-recurring_seasonal_routes
  ```
- **Tùy biến trường dữ liệu Custom Fields (40 cases)**:
  ```cmd
  run.bat --suite module-custom_fields_schema
  ```
- **Giữ chân khách hàng & Lưu vết hủy dịch vụ (45 cases)**:
  ```cmd
  run.bat --suite module-customer_crm_retention
  ```
- **Tài khoản thương mại chuỗi Master Invoicing (45 cases)**:
  ```cmd
  run.bat --suite module-commercial_accounts_master
  ```
- **Kong AI Assistant (30 cases)**:
  ```cmd
  run.bat --suite module-kong_ai_advanced
  ```
- **Negative & Validation Errors (52 cases)**:
  ```cmd
  run.bat --suite module-negative_validation
  ```
- **Quản lý tồn kho xe tải Truck Inventory (30 cases)**:
  ```cmd
  run.bat --suite module-inventory_truck_stock
  ```
- **Chấm công & Đội thợ Timesheet (30 cases)**:
  ```cmd
  run.bat --suite module-timesheet_crew_management
  ```
- **Kiểm tra xe & Đội xe Fleet Inspection (25 cases)**:
  ```cmd
  run.bat --suite module-fleet_vehicle_inspection
  ```
- **Chữ ký điện tử & Biên bản Work Order (35 cases)**:
  ```cmd
  run.bat --suite module-workorder_signatures
  ```

### Cách 3: Chạy Toàn Bộ 1,753 Test Cases (Master Suite)
```cmd
run.bat --suite suite-master-exhaustive
```

---

## 5. Xem Kết Quả & Báo Cáo Nghiệm Thu
Sau khi chạy xong:
* **Báo cáo JSON tổng hợp:** `reports/run_report_YYYYMMDD_HHMMSS.json` (thống kê tổng số test, Pass/Fail, thời gian chạy).
* **Ảnh chụp bằng chứng từng bước:** Thư mục `runs/` (ảnh chụp màn hình thực tế lưu trữ tự động).
* **Bản đồ định danh:** `knowledge/DYNAMIC_SELECTORS_REGISTRY.yaml` (Object Repository 4,900+ dòng bóc tách từ Samsung Galaxy A36).
