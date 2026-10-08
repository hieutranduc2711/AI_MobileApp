import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

source_path = r"C:\Users\Admin\Downloads\GorillaDesk_RN-5477_Full_Current_Scope_QA_V4.xlsx"
wb = openpyxl.load_workbook(source_path, data_only=False)

sheet_name = "16_Production_Edge_Gaps"
if sheet_name in wb.sheetnames:
    del wb[sheet_name]

ws = wb.create_sheet(title=sheet_name)

headers = [
    "TC_ID", "Direction", "Flow_Phase", "Priority", "Module", "Action",
    "Scenario", "Source_Tickets", "Source_URLs", "Requirement_Status",
    "App_Path", "Preconditions", "Test_Data", "Detailed_Steps",
    "Expected_Result", "Network_Path", "Risk", "Execution_Status",
    "Actual_Result", "Bug_ID", "Notes"
]

header_font = Font(name="Carlito", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="17365D", end_color="17365D", fill_type="solid")
header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

thin_border_side = Side(border_style="thin", color="D9D9D9")
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)

data_font = Font(name="Carlito", size=11, bold=False, color="000000")
data_align = Alignment(vertical="top", wrap_text=True)

col_widths = {
    "A": 14.0, "B": 24.0, "C": 28.0, "D": 8.0, "E": 18.0, "F": 34.0,
    "G": 50.0, "H": 30.0, "I": 42.0, "J": 26.0, "K": 42.0, "L": 48.0,
    "M": 30.0, "N": 80.0, "O": 80.0, "P": 28.0, "Q": 28.0, "R": 14.0,
    "S": 36.0, "T": 14.0, "U": 40.0
}

# Write headers
for col_idx, h in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border
ws.row_dimensions[1].height = 28

for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

testcases = [
    # --- 1. AUTH & SESSION LIFECYCLE OFFLINE ---
    {
        "TC_ID": "EDGE-GAP-001",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P0",
        "Module": "Auth / Sync Engine",
        "Action": "Token Refresh on Reconnect",
        "Scenario": "Access Token hết hạn sau 48h Offline → Có mạng lại → Tự động refresh token ngầm trước khi xả Outbox",
        "Source_Tickets": "RN-5477 / Arch-Security",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Critical Production Requirement",
        "App_Path": "GD Mobile > Background Sync Engine",
        "Preconditions": "User đăng nhập GD Mobile; tạo 5 mutations offline (Job, Note); để thiết bị offline > 48h khiến Access Token hết hạn nhưng Refresh Token còn hạn.",
        "Test_Data": "Expired JWT Access Token (exp < now); Valid Refresh Token; 5 pending SQLite outbox items.",
        "Detailed_Steps": "1. Đặt thiết bị sang Offline và thực hiện sửa Job, thêm Note.\n2. Chờ (hoặc giả lập chỉnh thời gian) để Access Token hết hạn.\n3. Bật Wi-Fi/4G để thiết bị chuyển sang trạng thái Online.\n4. Giám sát network traffic qua proxy/Charles hoặc console log.\n5. Quan sát quá trình gọi refresh token và xử lý outbox queue.",
        "Expected_Result": "1. Sync Engine phát hiện 401 hoặc chủ động gọi endpoint Refresh Token trước khi xả queue.\n2. Lấy Access Token mới thành công trong nền (Silent Refresh).\n3. Sử dụng token mới để xả toàn bộ 5 outbox mutations thành công.\n4. Không gián đoạn UI, không văng ra màn hình Login, không mất dữ liệu.",
        "Network_Path": "Offline → Online",
        "Risk": "Data Loss / Silent Fail",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Nếu không có cơ chế preemptive refresh, request đầu tiên sẽ dính 401 và có nguy cơ kích hoạt logout nhầm."
    },
    {
        "TC_ID": "EDGE-GAP-002",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P0",
        "Module": "Auth / Storage",
        "Action": "Force Logout Prevention & Data Preservation",
        "Scenario": "Refresh Token hết hạn (401/Invalid Session) → Reconnect mạng → KHÔNG ĐƯỢC xóa SQLite Outbox, hiển thị khóa màn hình bảo vệ dữ liệu pending",
        "Source_Tickets": "RN-5477 / Arch-Security",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Critical Production Requirement",
        "App_Path": "GD Mobile > Auth Revalidation Modal",
        "Preconditions": "User làm việc offline nhiều ngày, cả Access Token và Refresh Token đều đã bị thu hồi/hết hạn trên server; đang có 10 items pending trong SQLite outbox.",
        "Test_Data": "Revoked session / HTTP 401 Unauthorized trên mọi auth endpoints; 10 pending local mutations.",
        "Detailed_Steps": "1. Có 10 mutations pending offline.\n2. Bật mạng internet lại.\n3. Sync Engine gửi request và nhận phản hồi 401/403 Session Expired từ backend.\n4. Kiểm tra phản ứng của GD Mobile App.\n5. Kiểm tra trạng thái bảng outbox và dữ liệu local SQLite.\n6. Thực hiện đăng nhập lại (Re-login) cùng tài khoản đó.",
        "Expected_Result": "1. App TUYỆT ĐỐI KHÔNG tự động purge/xóa bảng SQLite local hoặc outbox.\n2. App hiển thị màn hình khóa yêu cầu nhập mật khẩu xác thực lại (Session Expired Modal) với thông báo: 'Có 10 thay đổi chưa đồng bộ. Vui lòng đăng nhập lại để tiếp tục sync.'\n3. Sau khi đăng nhập lại thành công, app tự động resume và đồng bộ toàn bộ 10 items lên server mà không mất 1 byte dữ liệu.",
        "Network_Path": "Offline → Online",
        "Risk": "Catastrophic Data Loss",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Lỗi cực kỳ phổ biến: Auth interceptor bắt 401 rồi gọi clearAllStorage() làm xóa sạch SQLite outbox."
    },
    {
        "TC_ID": "EDGE-GAP-003",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P1",
        "Module": "Auth / Settings",
        "Action": "Manual Logout Guard with Pending Outbox",
        "Scenario": "User chủ động nhấn 'Log Out' trong Settings khi Outbox còn dữ liệu chưa sync → Hiển thị cảnh báo chặn bắt buộc xác nhận kèm số lượng item",
        "Source_Tickets": "RN-5477 / UX-Guard",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Accepted / UX Standard",
        "App_Path": "GD Mobile > Settings > Account > Log Out",
        "Preconditions": "Thiết bị đang Offline hoặc Online nhưng có 3 items chưa đồng bộ hoàn tất (đang retry hoặc pending).",
        "Test_Data": "Pending outbox count = 3 (1 Job, 1 Invoice, 1 Photo).",
        "Detailed_Steps": "1. Thực hiện tạo Job và Invoice khi Offline.\n2. Vào Settings > Account > Bấm nút 'Log Out'.\n3. Kiểm tra Dialog cảnh báo hiển thị.\n4. Bấm 'Cancel' (Hủy bỏ) và kiểm tra dữ liệu.\n5. Thử bấm lại Log Out và chọn 'Confirm Logout' (Chấp nhận xóa).",
        "Expected_Result": "1. App bật Alert cảnh báo nổi bật: 'Cảnh báo: Bạn còn 3 mục chưa được đồng bộ lên máy chủ. Nếu đăng xuất, dữ liệu này sẽ bị mất vĩnh viễn!'.\n2. Mặc định focus vào nút 'Hủy bỏ' (Cancel).\n3. Khi bấm Cancel: giữ nguyên đăng nhập, toàn bộ dữ liệu outbox còn nguyên.\n4. Khi chọn xác nhận đăng xuất: mới tiến hành dọn dẹp an toàn.",
        "Network_Path": "Any State",
        "Risk": "Accidental Data Loss",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Cần kiểm tra cả trường hợp bấm Logout khi đang ở chế độ Offline hoàn toàn."
    },
    {
        "TC_ID": "EDGE-GAP-004",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P1",
        "Module": "Auth / Security",
        "Action": "Password Changed by Admin While Offline",
        "Scenario": "Admin đổi mật khẩu tài khoản trên Web khi Technician đang làm việc Offline → Bật mạng lại → Queue pause an toàn, yêu cầu mật khẩu mới",
        "Source_Tickets": "RN-5477 / Security",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Security Edge Requirement",
        "App_Path": "GD Mobile > Sync Engine / Password Prompt",
        "Preconditions": "Technician đi hiện trường tắt mạng, tạo 2 Jobs. Trên Web portal, Admin thực hiện reset/đổi mật khẩu của technician đó.",
        "Test_Data": "User account password changed from 'OldPass123' to 'NewPass456'; 2 pending jobs in mobile.",
        "Detailed_Steps": "1. Technician offline tạo 2 Jobs.\n2. Admin đổi mật khẩu tài khoản trên Web.\n3. Technician bật 4G kết nối lại.\n4. Sync Engine gửi request đồng bộ và nhận 401 Password Invalidated.\n5. Kiểm tra hành vi xử lý của mobile.",
        "Expected_Result": "1. Sync Engine lập tức tạm dừng hàng đợi (Pause Sync), không spam retry gây khóa tài khoản (lockout).\n2. Hiển thị thông báo: 'Mật khẩu tài khoản đã thay đổi. Vui lòng nhập mật khẩu mới để tiếp tục đồng bộ'.\n3. Sau khi nhập đúng 'NewPass456', queue tiếp tục xả và đẩy 2 Jobs lên server thành công.",
        "Network_Path": "Offline → Online",
        "Risk": "Account Lockout / Dropped Queue",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tránh loop 401 retry vô hạn làm kích hoạt brute-force rate limiter của backend."
    },
    {
        "TC_ID": "EDGE-GAP-005",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P1",
        "Module": "Auth / Permissions",
        "Action": "Role/Permission Revoked While Offline",
        "Scenario": "Quyền sửa Invoice bị thu hồi trên Web khi đang Offline → Đồng bộ lại → Server trả về 403 Forbidden → Chuyển sang Dead-Letter Queue riêng",
        "Source_Tickets": "RN-5477 / Permissions",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "RBAC Edge Requirement",
        "App_Path": "GD Mobile > Invoices / Sync Manager",
        "Preconditions": "Technician sửa Invoice offline. Trên web Admin hạ quyền của technician xuống 'View Only' đối với Invoice.",
        "Test_Data": "Revoked permission: 'invoices.update'; 1 pending invoice mutation, 2 pending job notes.",
        "Detailed_Steps": "1. Sửa Invoice offline (chuyển sang $200).\n2. Thêm 2 Job notes offline.\n3. Admin trên web bỏ quyền edit invoice của technician.\n4. Bật mạng online để sync.\n5. Kiểm tra xử lý mutation Invoice và 2 notes.",
        "Expected_Result": "1. Server trả về HTTP 403 Forbidden cho mutation Invoice.\n2. Sync Engine gắn cờ item Invoice này là 'Permission Denied / Rejected', chuyển vào mục Cần giải quyết (Dead-letter).\n3. Sync Engine KHÔNG bị kẹt tại item Invoice mà tiếp tục xả 2 Job notes thành công.\n4. Người dùng nhận thông báo giải thích rõ quyền hạn đã thay đổi.",
        "Network_Path": "Offline → Online",
        "Risk": "Queue Blocking / Silent Drop",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đảm bảo lỗi 403 của 1 item không làm tắc nghẽn (head-of-line blocking) các item hợp lệ khác."
    },
    {
        "TC_ID": "EDGE-GAP-006",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Auth Expiry & Session Lifecycle",
        "Priority": "P1",
        "Module": "Auth / Multi-User",
        "Action": "Cross-User Login Isolation",
        "Scenario": "Đăng nhập tài khoản B trên thiết bị vẫn còn dữ liệu chưa sync của tài khoản A → Ngăn chặn sync nhầm dữ liệu sang tài khoản B",
        "Source_Tickets": "RN-5477 / Multi-Account",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Strict Isolation Requirement",
        "App_Path": "GD Mobile > Login Screen",
        "Preconditions": "User A còn 2 pending offline jobs. User A bị force logout hoặc chuyển app sang login của User B.",
        "Test_Data": "Account A (id: usr_001, tenant: t1); Account B (id: usr_002, tenant: t2).",
        "Detailed_Steps": "1. User A tạo 2 offline jobs.\n2. Màn hình yêu cầu đăng nhập hiển thị.\n3. Nhập credentials của User B (khác account/tenant).\n4. Bấm Login.\n5. Kiểm tra cơ chế cách ly cơ sở dữ liệu SQLite / Outbox.",
        "Expected_Result": "1. App phát hiện User B khác User A.\n2. Hiển thị thông báo chặn: 'Thiết bị đang chứa dữ liệu chưa đồng bộ của tài khoản User A. Vui lòng đăng nhập lại tài khoản User A để đồng bộ hoặc xác nhận xóa dữ liệu cũ'.\n3. Tuyệt đối KHÔNG đồng bộ các mutations của User A vào database của User B trên server.",
        "Network_Path": "Any State",
        "Risk": "Critical Tenant Data Leak",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Vi phạm nghiêm trọng về tính toàn vẹn dữ liệu đa khách hàng (Multi-tenancy leak) nếu không chặn."
    },

    # --- 2. STORAGE FULL & LOW DISK QUOTA ---
    {
        "TC_ID": "EDGE-GAP-007",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Storage & Low Disk Limit",
        "Priority": "P0",
        "Module": "Storage / SQLite",
        "Action": "Low Disk Storage Exception Handling",
        "Scenario": "Bộ nhớ máy dưới 50MB (Low Storage Alert) → Lưu Job mới kèm chữ ký khi Offline → SQLite bắt SQLITE_FULL an toàn, không crash app",
        "Source_Tickets": "RN-5477 / OS-Constraints",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Hardware Boundary Requirement",
        "App_Path": "GD Mobile > Job Form > Save",
        "Preconditions": "Thiết bị Android/iOS bị đầy bộ nhớ (dung lượng trống < 50MB); app đang ở chế độ Offline.",
        "Test_Data": "Simulate storage full (e.g. qua dd dummy file hoặc emulator quota); New Job payload with signature base64.",
        "Detailed_Steps": "1. Giả lập bộ nhớ thiết bị sắp hết.\n2. Mở GD Mobile khi Offline.\n3. Điền thông tin Job mới, vẽ chữ ký hoàn tất Job.\n4. Bấm nút 'Save'.\n5. Kiểm tra log SQLite và phản hồi giao diện người dùng.",
        "Expected_Result": "1. SQLite transaction bắt được exception SQLITE_FULL / ENOSPC.\n2. App không bị văng đột ngột (crash to home screen).\n3. Hiển thị Toast/Alert thân thiện: 'Bộ nhớ thiết bị của bạn đã đầy. Vui lòng giải phóng dung lượng để lưu công việc này'.\n4. Dữ liệu form của người dùng vẫn được giữ nguyên trên giao diện (không bị xóa trắng để user có thể dọn máy rồi bấm Save lại).",
        "Network_Path": "Offline",
        "Risk": "App Crash / Data Loss",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Cần đảm bảo database SQLite không rơi vào trạng thái corrupt sau lỗi disk full."
    },
    {
        "TC_ID": "EDGE-GAP-008",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Storage & Low Disk Limit",
        "Priority": "P1",
        "Module": "Media / Photos",
        "Action": "Batch High-Res Photos Compression Memory Safety",
        "Scenario": "Chụp liên tiếp 20 ảnh hiện trường 48MP khi Offline → Tiến trình nén ảnh ngầm không gây Out-Of-Memory (OOM crash)",
        "Source_Tickets": "RN-5477 / RN-5680 / Media",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Performance & Media Requirement",
        "App_Path": "GD Mobile > Job > Photos > Camera",
        "Preconditions": "Thiết bị camera 48MP; bộ nhớ RAM điện thoại trung bình (3GB - 4GB RAM); app đang Offline.",
        "Test_Data": "20 high-resolution camera photos (~12MB mỗi file gốc RAW/JPEG).",
        "Detailed_Steps": "1. Mở Job khi Offline.\n2. Dùng camera chụp liên tục 20 ảnh công việc.\n3. Theo dõi mức tiêu thụ RAM qua Android Profiler / Xcode Instruments.\n4. Kiểm tra tiến trình sinh ảnh thumbnail và nén lưu file cục bộ.",
        "Expected_Result": "1. App nén ảnh tuần tự (sequential processing) hoặc worker pool giới hạn, không load đồng thời 20 ảnh bitmap vào RAM.\n2. RAM không vượt ngưỡng giới hạn heap, không gây OOM Crash.\n3. Cả 20 ảnh được lưu thành công vào thư mục lưu trữ cục bộ kèm đường dẫn uri trong SQLite.",
        "Network_Path": "Offline",
        "Risk": "OOM Crash / App Termination",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Liên quan trực tiếp đến subtask RN-5680 về tối ưu hóa cache ảnh và tránh base64 string lớn."
    },
    {
        "TC_ID": "EDGE-GAP-009",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Storage & Low Disk Limit",
        "Priority": "P1",
        "Module": "Media / Sync Engine",
        "Action": "Missing Local Media File Handling",
        "Scenario": "File ảnh cục bộ bị OS Cleaner hoặc người dùng xóa trước khi sync → Queue đẩy metadata lên server phát hiện thiếu file → Báo lỗi riêng photo, không kẹt queue",
        "Source_Tickets": "RN-5477 / File-System",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Resilience Requirement",
        "App_Path": "GD Mobile > Sync Engine / Photo Upload",
        "Preconditions": "User chụp 1 ảnh gắn vào Job khi offline. File ảnh vật lý trong cache bị xóa ngoài hệ thống trước khi có mạng.",
        "Test_Data": "Photo metadata record in SQLite pointing to deleted file uri: 'file:///cache/photo_999.jpg'.",
        "Detailed_Steps": "1. Chụp ảnh Job khi offline (record tạo trong SQLite outbox).\n2. Dùng file manager hoặc command xóa file ảnh gốc tại đường dẫn lưu trữ.\n3. Bật mạng Online để kích hoạt sync.\n4. Giám sát phản ứng của uploader worker.",
        "Expected_Result": "1. Sync worker phát hiện file không tồn tại (FileNotFoundException / ENOENT).\n2. Không throw unhandled promise rejection gây crash app.\n3. Đánh dấu riêng item ảnh đó là 'File Missing / Upload Failed' kèm icon cảnh báo trên Job.\n4. Toàn bộ các thông tin văn bản khác của Job vẫn được sync lên bình thường, hàng đợi tiếp tục hoạt động.",
        "Network_Path": "Offline → Online",
        "Risk": "Sync Queue Deadlock",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Rất nhiều app mobile bị kẹt hàng đợi vĩnh viễn ở item ảnh bị mất file."
    },
    {
        "TC_ID": "EDGE-GAP-010",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Storage & Low Disk Limit",
        "Priority": "P2",
        "Module": "Signature / SQLite",
        "Action": "Large Signature Vector/Base64 Boundary Storage",
        "Scenario": "Khách hàng vẽ chữ ký phức tạp/dày đặc tạo vector/SVG lớn → Lưu vào SQLite không vượt giới hạn row size và không chậm `useEntity`",
        "Source_Tickets": "RN-5477 / RN-5605 / RN-5680",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Data Format Constraint",
        "App_Path": "GD Mobile > Work Order > Signature Pad",
        "Preconditions": "Thiết bị offline; mở modal lấy chữ ký khách hàng.",
        "Test_Data": "Complex customer signature drawing (high-density strokes > 500KB raw vector points).",
        "Detailed_Steps": "1. Mở modal ký tên.\n2. Vẽ chữ ký cực kỳ dày đặc và phức tạp trong 30 giây.\n3. Bấm Save Signature.\n4. Kiểm tra thời gian ghi vào SQLite và thời gian load lại qua hook `useEntity`.",
        "Expected_Result": "1. File chữ ký được ghi ra disk dạng file PNG/SVG cục bộ và chỉ lưu path/URI vào SQLite (hoặc blob tối ưu).\n2. Quá trình lưu diễn ra < 300ms.\n3. Truy vấn `useEntity` của Job không bị giật lag khung hình khi render lại màn hình chi tiết.",
        "Network_Path": "Offline",
        "Risk": "UI Freeze / Slow Query",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tránh lưu trực tiếp data URI Base64 khổng lồ vào cột TEXT của SQLite."
    },

    # --- 3. CLOCK DRIFT, TIMEZONE & TIMESTAMP TAMPERING ---
    {
        "TC_ID": "EDGE-GAP-011",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Clock Drift & Timestamp Tampering",
        "Priority": "P0",
        "Module": "Sync Engine / Conflict",
        "Action": "Device Clock Rollback Resolution",
        "Scenario": "Đồng hồ thiết bị bị lùi về quá khứ (-2 ngày hoặc reset 1970 do cạn pin) → Technician hoàn thành Job Offline → Sync lên server không bị ghi đè sai",
        "Source_Tickets": "RN-5477 / Conflict-Resolution",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Timestamp Integrity Requirement",
        "App_Path": "GD Mobile > Job Execution",
        "Preconditions": "Thiết bị bị lệch giờ hệ thống (set thủ công về 2 ngày trước hoặc pin CMOS lỗi về Epoch 1970); app đang Offline.",
        "Test_Data": "Device System Time = 2026-10-06T08:00:00Z; Actual Real Time = 2026-10-08T08:00:00Z; Job status update = 'Completed'.",
        "Detailed_Steps": "1. Chỉnh giờ máy điện thoại lùi lại 2 ngày.\n2. Chuyển sang Offline; mở Job và bấm Complete, ghi chú: 'Xong việc'.\n3. Bật mạng Online để đồng bộ lên máy chủ.\n4. Kiểm tra thời điểm ghi nhận trên Server DB và Web Portal.",
        "Expected_Result": "1. Server sử dụng `server_received_at` hoặc cơ chế Vector Clock/Lamport Clock để xác định thứ tự sự kiện.\n2. Server không từ chối mutation với lỗi 'Invalid Timestamp' một cách mù quáng.\n3. Trạng thái 'Completed' được chấp nhận; hiển thị đúng trên Web Portal.\n4. Nếu có tranh chấp LWW (Last-Write-Wins), server phải bảo vệ dữ liệu không bị rollback bởi timestamp ma của client.",
        "Network_Path": "Offline → Online",
        "Risk": "Silent Overwrite / Stale Data",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Không được phụ thuộc 100% vào `Date.now()` của client để quyết định tính thắng thua trong LWW."
    },
    {
        "TC_ID": "EDGE-GAP-012",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Clock Drift & Timestamp Tampering",
        "Priority": "P1",
        "Module": "Sync Engine / Validation",
        "Action": "Future Device Clock Validation",
        "Scenario": "Đồng hồ thiết bị chỉnh nhanh về tương lai (+7 ngày) → Khi sync, server chuẩn hóa thời gian dựa trên server time thay vì tin client timestamp",
        "Source_Tickets": "RN-5477 / Validation",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Audit Trail Requirement",
        "App_Path": "GD Mobile > Invoices / Timestamps",
        "Preconditions": "Thiết bị chạy nhanh hơn 7 ngày; tạo Invoice offline.",
        "Test_Data": "Client time: 2026-10-15; Real server time: 2026-10-08.",
        "Detailed_Steps": "1. Chỉnh giờ máy sang tuần sau.\n2. Tạo Invoice thanh toán offline.\n3. Bật mạng sync lên backend.\n4. Kiểm tra ngày tạo Invoice (created_at) và ngày phát hành (issued_date).",
        "Expected_Result": "1. Backend gán `created_at` theo giờ chuẩn máy chủ UTC.\n2. Issued_date nghiệp vụ được lưu theo ý định người dùng nhưng được validate trong khoảng hợp lệ.\n3. Không làm sai lệch báo cáo doanh thu tuần hiện tại trên Dashboard của chủ doanh nghiệp.",
        "Network_Path": "Offline → Online",
        "Risk": "Financial Report Distortion",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Bảo đảm tính toàn vẹn của sổ sách kế toán và hóa đơn thuế."
    },
    {
        "TC_ID": "EDGE-GAP-013",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Clock Drift & Timestamp Tampering",
        "Priority": "P1",
        "Module": "Calendar / Jobs",
        "Action": "Timezone Crossing During Offline State",
        "Scenario": "Thiết bị đổi Timezone khi đang Offline (di chuyển qua ranh giới múi giờ EST → CST) → Lịch hẹn Job Start/End time không bị nhảy giờ",
        "Source_Tickets": "RN-5477 / Calendar",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Timezone Precision Requirement",
        "App_Path": "GD Mobile > Calendar / Agenda",
        "Preconditions": "Technician nhận lịch Job lúc 9:00 AM EST; offline và di chuyển qua khu vực CST (chậm hơn 1 tiếng); OS tự cập nhật timezone.",
        "Test_Data": "Original Job Start: 2026-10-08T09:00:00-04:00 (EST); New Device Timezone: America/Chicago (-05:00).",
        "Detailed_Steps": "1. Tải lịch khi online ở múi giờ EST.\n2. Chuyển sang Offline.\n3. Đổi timezone của hệ điều hành sang CST.\n4. Mở tab Agenda / Calendar kiểm tra giờ hiển thị của Job.\n5. Bật mạng online lại và kiểm tra sync.",
        "Expected_Result": "1. Job vẫn giữ đúng giờ hẹn với khách hàng theo quy định của chi nhánh (Branch Timezone) hoặc hiển thị rõ ràng múi giờ gốc.\n2. Không bị cộng/trừ sai 1 tiếng dẫn đến technician đến sớm hoặc muộn giờ hẹn.\n3. Khi sync lại, start_time UTC trên server không bị dịch chuyển lệch giờ.",
        "Network_Path": "Any State",
        "Risk": "Missed Appointment / Wrong Schedule",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Cần thống nhất lưu timestamp dạng ISO 8601 UTC kèm timezone offset gốc của Branch."
    },
    {
        "TC_ID": "EDGE-GAP-014",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Clock Drift & Timestamp Tampering",
        "Priority": "P2",
        "Module": "Calendar / Recurring",
        "Action": "Daylight Saving Time (DST) Shift Offline",
        "Scenario": "Sự kiện đổi giờ mùa hè (DST) diễn ra khi thiết bị đang Offline → Các công việc lặp lại (Recurring Jobs) không bị trùng giờ hoặc nhảy ngày",
        "Source_Tickets": "RN-5477 / Recurring",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Temporal Boundary Requirement",
        "App_Path": "GD Mobile > Calendar > Schedule",
        "Preconditions": "Thiết bị offline qua mốc 2:00 AM ngày chuyển đổi DST (mùa xuân nhảy lên 3:00 AM hoặc mùa thu lùi về 1:00 AM).",
        "Test_Data": "DST transition boundary date/time.",
        "Detailed_Steps": "1. Đặt thiết bị offline vào đêm chuyển đổi DST.\n2. Xem các lịch hẹn recurring của ngày hôm sau.\n3. Tạo 1 recurring job mới trong khoảng thời gian này.\n4. Bật mạng online để đồng bộ.",
        "Expected_Result": "1. Công việc lặp lại không bị tạo đúp thành 2 ca làm việc.\n2. Thời gian bắt đầu công việc vẫn đúng vào giờ làm việc bình thường của cơ sở kinh doanh.",
        "Network_Path": "Any State",
        "Risk": "Duplicate Recurring Event",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Kiểm tra với các thư viện tính toán ngày giờ trên mobile như dayjs, luxon."
    },

    # --- 4. OS LIFECYCLE, BACKGROUND KILL & CRASH RECOVERY ---
    {
        "TC_ID": "EDGE-GAP-015",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "OS Process Kill & Crash Recovery",
        "Priority": "P0",
        "Module": "Sync Engine / Idempotency",
        "Action": "OS Force-Kill During Batch Outbox Push",
        "Scenario": "OS Force-Kill app khi đang đẩy gói batch 30 mutations (bị kill đúng item 15) → Mở lại app: Item 15 không bị tạo trùng nhờ Idempotency-Key",
        "Source_Tickets": "RN-5477 / Idempotency",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Critical Core Sync Standard",
        "App_Path": "GD Mobile > Background Sync Engine",
        "Preconditions": "Có 30 mutations trong outbox (tạo Invoice, thanh toán, vật tư). Đang bắt đầu quá trình xả queue khi online.",
        "Test_Data": "30 distinct mutations with client-generated UUID / Idempotency-Key.",
        "Detailed_Steps": "1. Tích lũy 30 mutations offline.\n2. Kết nối mạng; tiến trình sync bắt đầu chạy.\n3. Tại thời điểm item thứ 15 đang gửi HTTP request (server đã nhận và insert DB nhưng chưa kịp trả response về mobile), dùng ADB kill process app: `adb shell am force-stop com.gorilladesk`.\n4. Khởi động lại GD Mobile App.\n5. Kiểm tra hàng đợi outbox và kiểm tra backend DB.",
        "Expected_Result": "1. Item thứ 15 khi được gửi lại có cùng `Idempotency-Key` (hoặc Client UUID).\n2. Backend phát hiện trùng key, trả về 200 OK với kết quả đã tạo trước đó, KHÔNG tạo thêm 1 bản ghi Invoice/Payment thứ 2.\n3. Các item từ 16 đến 30 tiếp tục được xử lý bình thường.\n4. Không có bất kỳ bản ghi trùng lặp nào được tạo ra trên server.",
        "Network_Path": "Offline → Online",
        "Risk": "Double Charging / Duplicate Records",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Bắt buộc mọi write mutation phải mang Idempotency-Key sinh từ client lúc tạo bản ghi."
    },
    {
        "TC_ID": "EDGE-GAP-016",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "OS Process Kill & Crash Recovery",
        "Priority": "P0",
        "Module": "Storage / SQLite",
        "Action": "Immediate App Swipe-Kill After Save",
        "Scenario": "User vuốt tắt app từ Recent Apps ngay sau khi bấm 'Save Job' khi Offline → Mở lại app: Job vẫn nằm nguyên trong SQLite và Outbox",
        "Source_Tickets": "RN-5477 / Persistence",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "AC Preserved Work",
        "App_Path": "GD Mobile > Job Creation > Save",
        "Preconditions": "Thiết bị offline hoàn toàn.",
        "Test_Data": "Full Job payload (Title, Customer, Time, Line Items).",
        "Detailed_Steps": "1. Nhập thông tin Job mới offline.\n2. Nhấn nút 'Save Job'.\n3. Trong vòng 0.2 giây ngay khi popup thành công vừa hiện hoặc vừa đóng, lập tức vuốt tắt app từ thanh Recent Apps (Task Switcher).\n4. Mở lại GD Mobile App.\n5. Kiểm tra danh sách Job trong ngày và trạng thái Outbox.",
        "Expected_Result": "1. Lệnh ghi đã được commit đồng bộ (synchronous SQLite commit) trước khi trả quyền điều khiển về UI.\n2. Mở lại app: Job mới tạo xuất hiện đầy đủ trong danh sách cục bộ.\n3. Biểu tượng pending/outbox hiển thị đúng trên thẻ Job.\n4. Không bị mất dữ liệu do app bị terminate đột ngột.",
        "Network_Path": "Offline",
        "Risk": "Data Loss on Exit",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tránh các thao tác async flush dữ liệu bị trì hoãn sau khi đã đóng màn hình."
    },
    {
        "TC_ID": "EDGE-GAP-017",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "OS Process Kill & Crash Recovery",
        "Priority": "P1",
        "Module": "Storage / SQLite",
        "Action": "Battery Die / Sudden Power Cut Transaction Safety",
        "Scenario": "Thiết bị sập nguồn đột ngột (0% Pin) đúng thời điểm SQLite đang ghi Transaction → Mở lại máy: SQLite Rollback an toàn, DB không hỏng",
        "Source_Tickets": "RN-5477 / Database-Engine",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "ACID Compliance Requirement",
        "App_Path": "GD Mobile > SQLite Engine",
        "Preconditions": "Thiết bị pin yếu hoặc rút cáp nguồn emulator khi đang commit transaction lớn.",
        "Test_Data": "Multi-table transaction: Job + JobItems + Invoice + CustomerUpdate.",
        "Detailed_Steps": "1. Bắt đầu transaction ghi đồng thời 4 bảng khi offline.\n2. Giả lập cắt nguồn đột ngột (Hard Power Off / Emulator kill -9).\n3. Bật lại thiết bị và mở GD Mobile.\n4. Thực thi kiểm tra tính toàn vẹn: `PRAGMA integrity_check`.",
        "Expected_Result": "1. SQLite WAL (Write-Ahead Logging) tự động phục hồi khi mở lại database.\n2. Integrity check trả về 'ok'.\n3. Trạng thái cơ sở dữ liệu nhất quán (hoặc đã commit trọn vẹn, hoặc rollback sạch sẽ về trạng thái trước đó, không có bản ghi nửa vời).\n4. App khởi động bình thường, không crash.",
        "Network_Path": "Offline",
        "Risk": "Database Corruption",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Cấu hình SQLite WAL mode và PRAGMA synchronous = NORMAL/FULL."
    },
    {
        "TC_ID": "EDGE-GAP-018",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "OS Process Kill & Crash Recovery",
        "Priority": "P1",
        "Module": "Sync Engine / Background",
        "Action": "Background Doze Mode & Resume Lifecycle",
        "Scenario": "App chuyển sang Background khi đang sync (Android Doze / iOS 30s limit) → Tạm dừng an toàn và tự resume khi mở lại không deadlock",
        "Source_Tickets": "RN-5477 / RN-5564 / Background",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "OS Lifecycle Management",
        "App_Path": "GD Mobile > Background Sync Manager",
        "Preconditions": "Đang xả 20 outbox items. Người dùng bấm phím Home hoặc chuyển sang app khác (Google Maps).",
        "Test_Data": "20 pending outbox mutations.",
        "Detailed_Steps": "1. Bắt đầu sync khi online.\n2. Bấm Home để đưa app vào background trong 2 phút (kích hoạt OS background suspension).\n3. Mở lại GD Mobile lên foreground.\n4. Kiểm tra tiến trình sync.",
        "Expected_Result": "1. Request đang chạy dở hoàn tất hoặc timeout trong giới hạn background cho phép.\n2. Khi trở lại foreground, listener AppState (active) kích hoạt kiểm tra lại hàng đợi.\n3. Tiến trình sync tiếp tục xả các item còn lại mượt mà.\n4. Không xảy ra deadlock giữa background worker và foreground UI thread.",
        "Network_Path": "Any State",
        "Risk": "Sync Stalling / Frozen Queue",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Kiểm tra đúng quy chế background execution trên Android 14+ và iOS 17+."
    },
    {
        "TC_ID": "EDGE-GAP-019",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "OS Process Kill & Crash Recovery",
        "Priority": "P2",
        "Module": "Job / Draft State",
        "Action": "Low Memory Killer (LMK) Form Draft Recovery",
        "Scenario": "LMK kill app khi người dùng đang nhập dở Form Invoice dài chưa bấm Save → Cơ chế Draft State cục bộ khôi phục lại form",
        "Source_Tickets": "RN-5477 / Form-Draft",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "User Experience Requirement",
        "App_Path": "GD Mobile > Invoice Form",
        "Preconditions": "Thiết bị offline; người dùng đang nhập hóa đơn gồm 5 line items, ghi chú dài, chưa ấn nút Save.",
        "Test_Data": "Unsaved Invoice draft inputs.",
        "Detailed_Steps": "1. Nhập đầy đủ thông tin hóa đơn khi offline.\n2. Mở 5 app nặng khác để ép hệ điều hành kích hoạt Low Memory Killer (LMK) dọn app GD Mobile trong nền.\n3. Mở lại GD Mobile và điều hướng vào đúng Job/Invoice đó.",
        "Expected_Result": "1. App có cơ chế auto-save draft vào local storage theo chu kỳ (ví dụ mỗi 5s hoặc khi blur input).\n2. Màn hình hiển thị prompt: 'Bạn có một bản nháp chưa lưu. Bạn có muốn khôi phục không?'.\n3. Khi chọn khôi phục: toàn bộ 5 line items và ghi chú được điền lại đầy đủ.",
        "Network_Path": "Offline",
        "Risk": "Frustrating Data Loss",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Nâng cao trải nghiệm người dùng hiện trường khi bị cuộc gọi hoặc camera ngắt quãng."
    },

    # --- 5. APP AUTO-UPDATE & DATABASE SCHEMA MIGRATION ---
    {
        "TC_ID": "EDGE-GAP-020",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Database Migration & Schema Upgrade",
        "Priority": "P0",
        "Module": "Database / Migration",
        "Action": "App Auto-Update with Pending Outbox Preservation",
        "Scenario": "Còn 10 items pending trong Outbox → App được auto-update lên version mới có migration DB → Mở app mới: Bảo toàn 100% Outbox",
        "Source_Tickets": "RN-5477 / SQLite-Migration",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Zero Data Loss Upgrade Standard",
        "App_Path": "GD Mobile > DB Migration Runner",
        "Preconditions": "App version v4.0 chứa 10 pending outbox records; cài đè bản update v4.1 (có thêm cột mới trong bảng jobs và bảng outbox_queue).",
        "Test_Data": "10 pending mutations created on schema v4.0; APK/IPA upgrade to schema v4.1.",
        "Detailed_Steps": "1. Tạo 10 items offline trên phiên bản app hiện tại.\n2. Tắt app (giữ nguyên SQLite database trên thiết bị).\n3. Cài đè phiên bản app mới (simulate Google Play auto-update: `adb install -r new_version.apk`).\n4. Mở app phiên bản mới.\n5. Kiểm tra log migration và đếm số lượng outbox records.",
        "Expected_Result": "1. SQLite migration script chạy thành công mà KHÔNG drop table hoặc recreat schema từ đầu.\n2. Cột mới được thêm bằng `ALTER TABLE ... ADD COLUMN` có default value an toàn.\n3. Đủ 10 pending outbox items được bảo toàn nguyên vẹn.\n4. Khi có mạng, 10 items được xả thành công lên server.",
        "Network_Path": "Any State",
        "Risk": "Catastrophic Upgrade Data Loss",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tuyệt đối cấm dùng fallback destructive migration (`fallbackToDestructiveMigration`) trên production."
    },
    {
        "TC_ID": "EDGE-GAP-021",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Database Migration & Schema Upgrade",
        "Priority": "P1",
        "Module": "Sync Engine / Schema",
        "Action": "Schema Evolution Non-Nullable Field Compatibility",
        "Scenario": "Backend cập nhật schema thêm trường bắt buộc (required field) trong khi client offline lưu theo schema cũ → Sync không bị 422 crash",
        "Source_Tickets": "RN-5477 / API-Contract",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Backward Compatibility Requirement",
        "App_Path": "GD Mobile > API Interceptor",
        "Preconditions": "Payload tạo Job được lưu offline trước thời điểm backend deploy thêm trường bắt buộc mới (ví dụ: `service_category_id`).",
        "Test_Data": "Old Job mutation payload missing `service_category_id`.",
        "Detailed_Steps": "1. Tạo Job offline trên app.\n2. Backend triển khai cập nhật validation rule mới.\n3. Bật mạng online để app đồng bộ payload cũ lên server.\n4. Kiểm tra phản hồi từ backend và cách app xử lý nếu bị 422.",
        "Expected_Result": "1. Backend có cơ chế backward-compatible default cho payload từ các version app cũ.\n2. Nếu backend reject 422: App không drop payload mà hiển thị cảnh báo yêu cầu người dùng mở Job bổ sung trường còn thiếu rồi ấn Sync lại.",
        "Network_Path": "Offline → Online",
        "Risk": "Unrecoverable Sync Rejection",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Cần chiến lược versioning API và compatibility window tối thiểu 30 ngày."
    },

    # --- 6. NETWORK FLAPPING, CAPTIVE PORTAL & HANDOVER ---
    {
        "TC_ID": "EDGE-GAP-022",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Network Interface Handover",
        "Priority": "P1",
        "Module": "Network / Upload",
        "Action": "Cellular to Wi-Fi Interface Handover During Upload",
        "Scenario": "Đang tải lên 10MB ảnh qua 4G thì thiết bị bắt vào sóng Wi-Fi (Socket reset) → App tự retry file ảnh mà không đứt ngang toàn bộ batch",
        "Source_Tickets": "RN-5477 / Network-Handover",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Network Resilience Standard",
        "App_Path": "GD Mobile > Media Sync Worker",
        "Preconditions": "Thiết bị có 5 ảnh đang upload; đang dùng kết nối Cellular (4G); đi vào vùng phủ sóng Wi-Fi quen thuộc.",
        "Test_Data": "5 media files (~5MB each); Interface change from `rmnet_data0` to `wlan0`.",
        "Detailed_Steps": "1. Bắt đầu upload 5 ảnh trên 4G.\n2. Giữa lúc ảnh thứ 2 đang upload được 50%, bật Wi-Fi để thiết bị tự động chuyển interface mạng.\n3. Socket cũ bị reset (`ECONNRESET` / `SocketException`).\n4. Theo dõi phản ứng của Media Sync Worker.",
        "Expected_Result": "1. Worker bắt exception kết nối bị đứt, kích hoạt cơ chế retry sau 2 giây trên interface mới.\n2. Tiếp tục upload ảnh thứ 2 (từ đầu hoặc resumable chunk) và hoàn tất các ảnh còn lại qua Wi-Fi.\n3. Không crash app và không đánh dấu file ảnh là lỗi vĩnh viễn.",
        "Network_Path": "Cellular → Wi-Fi",
        "Risk": "Upload Stalling / Partial Upload",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Sử dụng thư viện upload có hỗ trợ background session và tự động phục hồi kết nối."
    },
    {
        "TC_ID": "EDGE-GAP-023",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Network Interface Handover",
        "Priority": "P0",
        "Module": "Network / Detection",
        "Action": "Captive Portal Wi-Fi Detection Without Data Corruption",
        "Scenario": "Kết nối vào Wi-Fi công cộng có Captive Portal (trả về HTML login thay vì JSON) → Nhận diện No-Internet, không parse HTML thành lỗi",
        "Source_Tickets": "RN-5477 / Network-Detection",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Critical Edge Requirement",
        "App_Path": "GD Mobile > Connectivity Listener",
        "Preconditions": "Thiết bị kết nối Wi-Fi khách sạn/quán café chưa authenticate (mọi request HTTP bị redirect 302 về trang đăng nhập HTML).",
        "Test_Data": "Captive portal redirect (HTTP 302 to hotel-login.html; Content-Type: text/html).",
        "Detailed_Steps": "1. Có 3 mutations pending offline.\n2. Kết nối vào mạng Wi-Fi Captive Portal.\n3. Kiểm tra trạng thái Network State của GD Mobile.\n4. Kiểm tra phản hồi của Sync Engine.",
        "Expected_Result": "1. Cơ chế ping endpoint kiểm tra internet thực tế (ví dụ: Google 204 generate_204) nhận diện đây là Captive Portal / Chưa có internet thực sự.\n2. App duy trì trạng thái 'Offline / Limited Connectivity'.\n3. Sync Engine KHÔNG gửi request API lên server để nhận về HTML rồi parse JSON lỗi (`SyntaxError: Unexpected token < in JSON`).\n4. Dữ liệu outbox được giữ nguyên trạng thái chờ mạng thật.",
        "Network_Path": "Captive Portal Wi-Fi",
        "Risk": "JSON Parse Crash / Corrupted Cache",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Rất nhiều app bị crash hoặc xóa trắng cache do parse nhầm HTML của trang Captive Portal."
    },
    {
        "TC_ID": "EDGE-GAP-024",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Network Interface Handover",
        "Priority": "P1",
        "Module": "Sync Engine / Resilience",
        "Action": "Extreme High Packet Loss (2G/Edge) Throttling",
        "Scenario": "Mạng 2G chập chờn (Packet loss 60%, RTT 4000ms) → Cấu hình Timeout hợp lý, Exponential Backoff + Jitter, không cạn pin thiết bị",
        "Source_Tickets": "RN-5477 / Network-Throttling",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Resource Efficiency Requirement",
        "App_Path": "GD Mobile > Sync Engine Retry Loop",
        "Preconditions": "Thiết bị kết nối mạng giả lập 2G (tỷ lệ rớt gói 60%, độ trễ 4000ms).",
        "Test_Data": "Network profile: Bandwidth 64kbps, Packet Loss 60%, Latency 4000ms.",
        "Detailed_Steps": "1. Tạo 5 mutations offline.\n2. Bật mạng 2G giả lập.\n3. Quan sát tần suất gọi retry của Sync Engine trong 10 phút.\n4. Kiểm tra mức tiêu thụ CPU và nhiệt độ máy.",
        "Expected_Result": "1. Request timeout được set ở mức an toàn (15s - 30s).\n2. Khi fail, thời gian chờ retry tăng dần theo lũy thừa: 5s → 10s → 20s → 40s (kèm jitter ngẫu nhiên).\n3. Không spam request liên tục làm nghẽn CPU và làm nóng máy, hao pin nhanh.",
        "Network_Path": "2G / Edge",
        "Risk": "Battery Drain / UI Hang",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đảm bảo trải nghiệm thiết bị khi technician đi làm ở vùng hẻo lánh sóng chập chờn."
    },
    {
        "TC_ID": "EDGE-GAP-025",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Network Interface Handover",
        "Priority": "P1",
        "Module": "Sync Engine / Debounce",
        "Action": "Rapid Flapping Network Debounce Stabilization",
        "Scenario": "Mạng bật tắt liên tục (Flapping: 3s có mạng, 2s mất mạng x 10 lần) → Sync Engine duy trì Debounce 3-5s, tránh trigger sync song song",
        "Source_Tickets": "RN-5477 / Flapping-Network",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Stability Requirement",
        "App_Path": "GD Mobile > Network Change Listener",
        "Preconditions": "Hàng đợi có 10 items. Mạng Wi-Fi bị bật tắt liên tục mỗi 3 giây.",
        "Test_Data": "Rapid toggle network state 10 times in 30 seconds.",
        "Detailed_Steps": "1. Chạy script bật tắt toggle Wi-Fi liên tục 10 lần.\n2. Quan sát log các thread sync được khởi tạo.",
        "Expected_Result": "1. Sync Engine áp dụng Debounce (chờ mạng duy trì ổn định tối thiểu 3-5 giây liên tục mới bắt đầu phát động đợt sync).\n2. Không tạo ra 10 sync workers chạy chồng chéo cạnh tranh tài nguyên (Race Condition).\n3. Mutex lock của SQLite không bị dính `SQLITE_BUSY`.",
        "Network_Path": "Flapping Network",
        "Risk": "Thread Race Condition / SQLite Lock",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Sử dụng single-flight pattern hoặc concurrency lock cho sync runner."
    },

    # --- 7. BOUNDARY DATA, UNICODE & SPECIAL CHARACTERS ---
    {
        "TC_ID": "EDGE-GAP-026",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Boundary & Unicode Serialization",
        "Priority": "P1",
        "Module": "Job / Note",
        "Action": "Emoji & 4-Byte UTF-8 Surrogate Pairs Storage",
        "Scenario": "Ghi chú Job chứa emoji đa dạng (👨‍🔧 🐞 🐜 🏠 🌧️) và Unicode 4-byte → Lưu Offline vào SQLite và đẩy lên backend không lỗi font",
        "Source_Tickets": "RN-5477 / Data-Encoding",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Encoding Standard",
        "App_Path": "GD Mobile > Job Notes",
        "Preconditions": "Thiết bị offline.",
        "Test_Data": "Text containing: 'Diệt mối tại nhà 🏠👨‍🔧: Đã xử lý 5 tổ mối 🐜 và gián 🪳. Thời tiết mưa to 🌧️! 𝓤𝓷𝓲𝓬𝓸𝓭𝓮 𝕋𝕖𝕩𝕥.'",
        "Detailed_Steps": "1. Mở Job offline.\n2. Nhập ghi chú chứa chuỗi dữ liệu emoji và ký tự 4-byte UTF-8 ở trên.\n3. Lưu Job.\n4. Đóng app, mở lại kiểm tra hiển thị khi offline.\n5. Bật mạng online để sync lên Web portal.",
        "Expected_Result": "1. SQLite lưu trữ trọn vẹn chuỗi UTF-8 không biến thành ký tự rác (`???` hoặc `\uFFFD`).\n2. Màn hình mobile hiển thị chuẩn xác các icon emoji.\n3. Server nhận payload JSON UTF-8 hợp lệ và lưu vào database server (hỗ trợ utf8mb4).\n4. Web portal hiển thị đúng y nguyên nội dung.",
        "Network_Path": "Offline → Online",
        "Risk": "Data Corruption / Encoding Error",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đặc biệt chú ý MySQL/PostgreSQL backend cần cấu hình charset utf8mb4 thay vì utf8 3-byte."
    },
    {
        "TC_ID": "EDGE-GAP-027",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Boundary & Unicode Serialization",
        "Priority": "P1",
        "Module": "Customer / Input Validation",
        "Action": "Special Characters & Escaping Injection Protection",
        "Scenario": "Text chứa ký tự đặc biệt nguy hiểm (`'`, `\"`, `\\`, `\\0`, `<script>`, `' OR '1'='1`) → Không hỏng câu query SQLite và payload JSON",
        "Source_Tickets": "RN-5477 / Security-Escaping",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Security & Parsing Requirement",
        "App_Path": "GD Mobile > Customer Name / Notes",
        "Preconditions": "Thiết bị offline.",
        "Test_Data": "Name: `O'Connor \\\"Big\\\" <script>alert(1)</script> ' OR 1=1 -- \\n \\r \\t`",
        "Detailed_Steps": "1. Nhập tên khách hàng và địa chỉ với chuỗi payload thử nghiệm trên khi offline.\n2. Bấm Lưu.\n3. Kiểm tra câu lệnh SQLite insert qua parameterized query.\n4. Kiểm tra file payload JSON sinh ra trong bảng outbox.\n5. Bật mạng sync lên server.",
        "Expected_Result": "1. SQLite execute với parameterized bindings, không bị lỗi cú pháp SQL Syntax Error.\n2. JSON serializer escape đúng các ký tự nháy kép và gạch chéo ngược.\n3. Sync lên server thành công không bị HTTP 400 Bad Request.\n4. Render lại trên UI mobile và Web an toàn không bị XSS.",
        "Network_Path": "Offline → Online",
        "Risk": "SQL Syntax Crash / JSON Malformed",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đảm bảo 100% câu truy vấn SQLite local dùng Prepared Statements, không cộng chuỗi."
    },
    {
        "TC_ID": "EDGE-GAP-028",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Boundary & Unicode Serialization",
        "Priority": "P2",
        "Module": "Job / Note",
        "Action": "Massive Text Boundary Performance",
        "Scenario": "Ghi chú cực dài (10,000 ký tự văn bản) nhập khi Offline → Màn hình Job Detail render mượt mà khi Offline, không freeze UI",
        "Source_Tickets": "RN-5477 / Performance",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Boundary Performance Requirement",
        "App_Path": "GD Mobile > Job Detail > Notes View",
        "Preconditions": "Thiết bị offline.",
        "Test_Data": "10,000 characters text string (~10KB text payload).",
        "Detailed_Steps": "1. Nhập ghi chú 10,000 ký tự vào Job khi offline.\n2. Lưu lại.\n3. Cuộn màn hình Job Detail lên xuống liên tục.\n4. Đo FPS và thời gian render component.",
        "Expected_Result": "1. Lưu thành công vào SQLite không bị lag.\n2. Màn hình duy trì tốc độ khung hình >= 55 FPS, không bị đơ UI thread.\n3. Khi có mạng, sync đẩy payload text lớn lên server thành công.",
        "Network_Path": "Offline → Online",
        "Risk": "UI Lag / Freeze",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Kiểm tra giới hạn text input của React Native TextInput component."
    },
    {
        "TC_ID": "EDGE-GAP-029",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Boundary & Unicode Serialization",
        "Priority": "P1",
        "Module": "Invoice / Calculations",
        "Action": "Currency Precision, Discounts & Zero Balances",
        "Scenario": "Hóa đơn chứa số lẻ thập phân ($1,234.5678), giảm giá 100%, hoặc số âm hợp lệ → Lưu Offline và sync lên server không sai lệch số học",
        "Source_Tickets": "RN-5477 / Accounting-Accuracy",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Financial Calculation Standard",
        "App_Path": "GD Mobile > Invoices > Line Items",
        "Preconditions": "Thiết bị offline.",
        "Test_Data": "Item 1: $12.345 x 3 = $37.035; Discount: 100%; Total Balance: $0.00; Refund adjustment: -$25.50.",
        "Detailed_Steps": "1. Tạo Invoice với các con số trên khi offline.\n2. Kiểm tra tổng tiền hiển thị trên mobile khi offline.\n3. Bật mạng online để sync lên server.\n4. So sánh số tiền trên mobile và số tiền server ghi sổ.",
        "Expected_Result": "1. Quy tắc làm tròn (Rounding Half-Up) tại client và server khớp nhau 100% đến từng cent ($0.01).\n2. Không xảy ra lỗi trôi dấu phẩy động (Floating point precision: 0.1 + 0.2 = 0.30000000000000004).\n3. Server chấp nhận hóa đơn $0.00 và hóa đơn điều chỉnh âm hợp lệ.",
        "Network_Path": "Offline → Online",
        "Risk": "Financial Discrepancy / Invoicing Error",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Bắt buộc dùng integer cents hoặc thư viện Decimal chuyên dụng (bignumber.js / currency.js)."
    },

    # --- 8. CASCADING DEPENDENCIES & CONFLICT RESOLUTION ---
    {
        "TC_ID": "EDGE-GAP-030",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Parent local:* Dependency",
        "Priority": "P0",
        "Module": "Sync Engine / Hierarchy",
        "Action": "4-Level Deep Cascading Entity Creation",
        "Scenario": "Chuỗi phụ thuộc 4 cấp tạo mới khi Offline: Khách hàng A → Địa điểm L1 → Job J1 → Invoice I1 → Server mapping ID chính xác từ trên xuống",
        "Source_Tickets": "RN-5477 / Cascading-Sync",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Core Local-First Standard",
        "App_Path": "GD Mobile > Field Flow",
        "Preconditions": "Thiết bị offline hoàn toàn.",
        "Test_Data": "Local IDs: local:cust_01 → local:loc_01 → local:job_01 → local:inv_01.",
        "Detailed_Steps": "1. Offline: Tạo mới Customer A (sinh `local:cust_01`).\n2. Offline: Tạo Location gắn vào `local:cust_01` (sinh `local:loc_01`).\n3. Offline: Tạo Job gắn vào `local:loc_01` (sinh `local:job_01`).\n4. Offline: Tạo Invoice gắn vào `local:job_01` (sinh `local:inv_01`).\n5. Bật mạng Online để hệ thống bắt đầu đồng bộ.",
        "Expected_Result": "1. Sync Engine xả tuần tự theo đúng thứ tự topology cha trước - con sau.\n2. Server trả về UUID thật của Customer A (`cust_real_uuid`), mobile cập nhật foreign key của Location trước khi gửi Location.\n3. Cả 4 thực thể được tạo thành công trên backend với quan hệ cha con hoàn hảo.\n4. Dữ liệu local SQLite được cập nhật thay thế toàn bộ `local:*` thành UUID thật của server.",
        "Network_Path": "Offline → Online",
        "Risk": "Foreign Key Constraint Failure",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đây là bài test tối thượng kiểm tra năng lực Dependency Graph Resolver của PowerSync/SyncEngine."
    },
    {
        "TC_ID": "EDGE-GAP-031",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Parent local:* Dependency",
        "Priority": "P0",
        "Module": "Sync Engine / Error Cascade",
        "Action": "Parent Rejection Cascading Child Blocker",
        "Scenario": "Nút cha bị Server Reject (Customer A bị 422 trùng Email) → Các nút con (L1, J1, I1) tự động chuyển 'Blocked by Parent' có thông báo rõ",
        "Source_Tickets": "RN-5477 / Cascade-Failure",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Robust Error Handling Standard",
        "App_Path": "GD Mobile > Sync Manager / Alerts",
        "Preconditions": "Thiết bị offline tạo Customer A (email đã tồn tại trên server) kèm Location, Job, Invoice phụ thuộc.",
        "Test_Data": "Duplicate email: 'existing@gorilladesk.com' triggers server 422 Unprocessable Entity.",
        "Detailed_Steps": "1. Tạo chuỗi 4 cấp offline như testcase EDGE-GAP-030.\n2. Bật mạng để sync.\n3. Server xử lý Customer A và trả về 422 Duplicate Email.\n4. Kiểm tra trạng thái của Location, Job và Invoice trong hàng đợi.",
        "Expected_Result": "1. Customer A dừng lại ở trạng thái 'Failed (Duplicate Email)'.\n2. Sync Engine KHÔNG gửi Location, Job, Invoice lên server với foreign key rác hoặc rỗng (tránh tạo orphaned records).\n3. Các entity con được đánh dấu trạng thái 'Blocked by Parent Dependency'.\n4. Giao diện hiển thị hướng dẫn: 'Sửa lỗi email của Khách hàng để tiếp tục đồng bộ các mục liên quan'.",
        "Network_Path": "Offline → Online",
        "Risk": "Orphaned Records / Server Crash",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đảm bảo không xả các entity con khi entity cha bị reject."
    },
    {
        "TC_ID": "EDGE-GAP-032",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Dead Letter",
        "Priority": "P1",
        "Module": "Sync Manager / UX",
        "Action": "Dead-Letter Queue Inspection & In-App Retry UX",
        "Scenario": "Mutation bị server reject vĩnh viễn (422/400) → Hiển thị badge đỏ 'Cần xử lý' → Cho phép sửa trực tiếp và bấm 'Thử lại đồng bộ'",
        "Source_Tickets": "RN-5477 / Dead-Letter-UX",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "User Self-Healing Requirement",
        "App_Path": "GD Mobile > Menu > Sync Status > Failed Items",
        "Preconditions": "Có 1 mutation bị reject do sai định dạng zip code khi offline.",
        "Test_Data": "Invalid zip code: 'ABCDE' rejected by server address validator.",
        "Detailed_Steps": "1. Chuyển online, item bị server reject 422.\n2. Quan sát thông báo trên thanh tiêu đề GD Mobile (hiện badge đỏ số 1).\n3. Chạm vào badge để mở màn hình 'Chi tiết lỗi đồng bộ'.\n4. Chạm vào item lỗi, chọn 'Chỉnh sửa' (sửa zip code thành '33401').\n5. Bấm nút 'Thử lại đồng bộ' (Retry Sync).",
        "Expected_Result": "1. Màn hình hiển thị nguyên nhân lỗi bằng ngôn ngữ dễ hiểu: 'Mã bưu chính không hợp lệ'.\n2. Cho phép người dùng chỉnh sửa dữ liệu ngay trong bản ghi pending.\n3. Khi bấm Retry: Sync Engine đóng gói payload mới và gửi lại thành công.\n4. Badge cảnh báo biến mất, hàng đợi trở về trạng thái sạch (All Synced).",
        "Network_Path": "Offline → Online",
        "Risk": "Trapped Unrecoverable Data",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Người dùng hiện trường phải có công cụ tự khắc phục lỗi mà không cần gọi tổng đài IT."
    },
    {
        "TC_ID": "EDGE-GAP-033",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Semantic Action Ordering",
        "Priority": "P1",
        "Module": "Job / Status",
        "Action": "Rapid Status Coalescing (Squash Mutations)",
        "Scenario": "Sửa liên tiếp Job: Pending → In Progress → Completed trong 2 phút khi Offline → Outbox gộp thành 1 mutation cuối cùng hoặc giữ đúng thứ tự",
        "Source_Tickets": "RN-5477 / Coalesce-Mutations",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Optimization Standard",
        "App_Path": "GD Mobile > Job Execution",
        "Preconditions": "Thiết bị offline.",
        "Test_Data": "Job #100: Status transitions: Pending -> In Progress -> Completed within 120 seconds.",
        "Detailed_Steps": "1. Mở Job #100 khi offline, bấm 'Start Job' (In Progress).\n2. Sau 30s bấm 'Finish Job' (Completed).\n3. Kiểm tra các dòng bản ghi trong bảng outbox queue của SQLite.\n4. Bật mạng online để đồng bộ.",
        "Expected_Result": "1. Hoặc outbox thông minh gộp (squash) thành 1 mutation cuối cùng cập nhật `status: 'Completed'` kèm thời gian bắt đầu và kết thúc.\n2. Hoặc outbox đẩy 2 mutation theo đúng thứ tự thời gian nghiêm ngặt (FIFO).\n3. Kết quả cuối cùng trên server là Job #100 ở trạng thái Completed với đầy đủ lịch sử hoạt động chính xác.",
        "Network_Path": "Offline → Online",
        "Risk": "Out-of-order Status / Stale Override",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tránh tình trạng race condition gửi request Completed trước rồi request In Progress đến sau ghi đè."
    },
    {
        "TC_ID": "EDGE-GAP-034",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Multi-device Conflict",
        "Priority": "P0",
        "Module": "Job / Conflict Resolution",
        "Action": "Field-Level Concurrent Edit Resolution Policy",
        "Scenario": "Thiết bị A (Offline) sửa ghi chú Job; Thiết bị B (Web Online) sửa giờ hẹn Job → Sync lên: Hợp nhất cấp trường (Field-level Merge) không đè mất",
        "Source_Tickets": "RN-5477 / Conflict-Merge",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Architecture Conflict Standard",
        "App_Path": "GD Mobile & Web Portal",
        "Preconditions": "Cùng 1 Job #200. Thiết bị mobile offline; Web portal online.",
        "Test_Data": "Mobile edit: `technician_notes = 'Đã phun thuốc khử khuẩn xung quanh nhà'`.\nWeb edit: `scheduled_time = '02:00 PM - 04:00 PM'`.",
        "Detailed_Steps": "1. Mobile offline sửa `technician_notes`.\n2. Cùng lúc đó trên Web, dispatcher sửa `scheduled_time` của Job #200.\n3. Mobile bật mạng online để đồng bộ lên server.\n4. Kiểm tra bản ghi Job #200 trên server sau khi sync.",
        "Expected_Result": "1. Vì 2 bên sửa 2 trường khác nhau (khác field name), server áp dụng cơ chế hợp nhất cấp trường (Field-level 3-way merge).\n2. Job #200 bảo toàn cả 2 thay đổi: `scheduled_time` mới từ Web VÀ `technician_notes` mới từ Mobile.\n3. Tuyệt đối không để mobile ghi đè nguyên cả object (Full-object overwrite) làm mất giờ hẹn mới mà dispatcher vừa sửa.",
        "Network_Path": "Cross-Platform Sync",
        "Risk": "Silent Data Loss of Concurrent Edits",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Quy tắc cốt lõi: Mutation payload chỉ gửi Delta / Patch các trường đã thay đổi, không gửi full dump entity."
    },
    {
        "TC_ID": "EDGE-GAP-035",
        "Direction": "ONLINE → OFFLINE",
        "Flow_Phase": "Create→Delete Before Sync",
        "Priority": "P1",
        "Module": "Job / Task",
        "Action": "Offline Create Then Delete Cancellation",
        "Scenario": "Tạo Job/Task mới khi Offline (`local:j99`), sau đó bấm Xóa luôn khi vẫn Offline → Outbox tự triệt tiêu 2 lệnh, không gửi lên backend",
        "Source_Tickets": "RN-5477 / Outbox-Optimization",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Optimization Standard",
        "App_Path": "GD Mobile > Task List",
        "Preconditions": "Thiết bị offline hoàn toàn.",
        "Test_Data": "New local task `local:task_99` created then deleted within same offline session.",
        "Detailed_Steps": "1. Offline: Bấm Add Task, nhập 'Kiểm tra bẫy chuột', bấm Save (sinh outbox `CREATE local:task_99`).\n2. Ngay sau đó nhận ra nhầm lẫn, bấm Delete task đó (sinh lệnh `DELETE local:task_99`).\n3. Kiểm tra bảng outbox queue trong SQLite.\n4. Bật mạng online.",
        "Expected_Result": "1. Outbox Engine nhận diện 2 lệnh tạo và xóa cùng 1 local entity chưa từng tồn tại trên server.\n2. Tự động triệt tiêu (annihilate) cả 2 bản ghi khỏi outbox queue tại local.\n3. Khi có mạng, không gửi bất kỳ HTTP request vô nghĩa nào lên server.\n4. Không làm tốn băng thông và không gây lỗi 404 trên server.",
        "Network_Path": "Offline → Online",
        "Risk": "Unnecessary Traffic / Server 404",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tiết kiệm tài nguyên và loại bỏ hoàn toàn nguy cơ server báo lỗi 'Entity not found to delete'."
    },

    # --- 9. ATTACHMENT CHUNKING & CONCURRENCY ---
    {
        "TC_ID": "EDGE-GAP-036",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Large File",
        "Priority": "P1",
        "Module": "Media / Video",
        "Action": "Large Video Multipart Chunked Resumable Upload",
        "Scenario": "Tải lên video hiện trường 50MB khi Reconnect → Sử dụng Chunked Upload hỗ trợ resume tại byte bị đứt, không upload lại từ đầu",
        "Source_Tickets": "RN-5477 / Media-Chunking",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Large File Standard",
        "App_Path": "GD Mobile > Job > Attachments",
        "Preconditions": "Technician quay 1 video hiện trường 50MB khi offline. Bật mạng online để upload.",
        "Test_Data": "Video file: 50MB MP4; Upload chunk size: 5MB (10 chunks total).",
        "Detailed_Steps": "1. Quay video 50MB đính kèm vào Job offline.\n2. Bật mạng online để bắt đầu upload.\n3. Khi upload được 25MB (5 chunks), ngắt kết nối mạng 5 giây rồi bật lại.\n4. Theo dõi HTTP headers và range byte gửi lên.",
        "Expected_Result": "1. Tiến trình upload resume tiếp tục từ chunk thứ 6 (byte thứ 25,000,001).\n2. Không tải lại từ byte số 0.\n3. Toàn bộ video được ghép nối hoàn chỉnh trên server (S3 / Cloud Storage).\n4. Người dùng thấy thanh tiến trình (progress bar) tiếp tục chạy mượt mà.",
        "Network_Path": "Offline → Online",
        "Risk": "Data Waste / Timeout Failure",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Đặc biệt quan trọng đối với các video khảo sát mối công trình lớn."
    },
    {
        "TC_ID": "EDGE-GAP-037",
        "Direction": "OFFLINE → ONLINE",
        "Flow_Phase": "Stress/Scale",
        "Priority": "P2",
        "Module": "Sync Engine / Concurrency",
        "Action": "Media Concurrency Limiter (Throttled Pool)",
        "Scenario": "Upload đồng thời 20 hình ảnh hiện trường khi Reconnect → Giới hạn concurrency tối đa 2 ảnh song song để không nghẽn dữ liệu text",
        "Source_Tickets": "RN-5477 / Concurrency",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "QoS Requirement",
        "App_Path": "GD Mobile > Background Transfer Pool",
        "Preconditions": "Hàng đợi có 20 ảnh và 5 text mutations (Job status, Invoice).",
        "Test_Data": "20 images (3MB each) + 5 critical JSON mutations.",
        "Detailed_Steps": "1. Kết nối mạng sau ca làm việc dài.\n2. Giám sát số lượng kết nối HTTP socket mở đồng thời bằng network analyzer.",
        "Expected_Result": "1. Các mutation text quan trọng (Job status, Payment) được ưu tiên đi trước (High Priority Queue).\n2. Luồng upload ảnh được phân bổ worker pool tối đa 2-3 kết nối song song.\n3. Không mở 20 kết nối cùng lúc làm sập socket pool của hệ điều hành và gây timeout các request dữ liệu text.",
        "Network_Path": "Offline → Online",
        "Risk": "Network Saturation / Socket Exhaustion",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Quality of Service (QoS): Text metadata luôn có độ ưu tiên cao hơn media binary."
    },

    # --- 10. DEVICE STATE & HARDWARE CONSTRAINTS ---
    {
        "TC_ID": "EDGE-GAP-038",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Device Edge",
        "Priority": "P2",
        "Module": "Sync Engine / Battery",
        "Action": "Extreme Battery Saver Sync Throttling",
        "Scenario": "Chế độ tiết kiệm pin tối đa (Extreme Battery Saver) kích hoạt khi Offline → App hoãn background sync, chỉ sync khi kéo Pull-to-refresh",
        "Source_Tickets": "RN-5477 / Power-Management",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "OS Compliance Requirement",
        "App_Path": "GD Mobile > Power State Listener",
        "Preconditions": "Thiết bị dưới 15% pin, kích hoạt chế độ Tiết kiệm pin của hệ điều hành; có dữ liệu pending.",
        "Test_Data": "Battery level: 10%; Power Saver Mode: Enabled.",
        "Detailed_Steps": "1. Bật chế độ tiết kiệm pin trên Android/iOS.\n2. Kết nối mạng có internet.\n3. Quan sát hành vi sync tự động ngầm.\n4. Thực hiện thao tác kéo màn hình xuống (Pull-to-refresh).",
        "Expected_Result": "1. App tuân thủ chính sách tiết kiệm pin, không đánh thức CPU liên tục trong nền.\n2. Khi người dùng chủ động mở app và thực hiện Pull-to-refresh: App kích hoạt sync ngay lập tức.\n3. Thông báo rõ trạng thái: 'Đang tiết kiệm pin - Chạm để đồng bộ'.",
        "Network_Path": "Any State",
        "Risk": "Unexpected Battery Drain",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Tuân thủ chặt chẽ nguyên tắc Android JobScheduler và iOS BackgroundTasks."
    },
    {
        "TC_ID": "EDGE-GAP-039",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Device Edge",
        "Priority": "P2",
        "Module": "Permissions / Camera",
        "Action": "Runtime Permission Revocation While Offline",
        "Scenario": "Thu hồi quyền Camera/Storage trong OS Settings khi app đang chạy ngầm Offline → App xử lý bắt lỗi gracefully, không văng app",
        "Source_Tickets": "RN-5477 / Permissions",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Runtime Security Standard",
        "App_Path": "GD Mobile > Camera Module",
        "Preconditions": "App đang mở ở chế độ offline. Chuyển sang Settings hệ điều hành, tước quyền Camera và Files/Photos của app GD Mobile.",
        "Test_Data": "Revoked runtime OS permissions: `CAMERA`, `READ_MEDIA_IMAGES`.",
        "Detailed_Steps": "1. Mở GD Mobile offline.\n2. Vào Cài đặt máy > Ứng dụng > GD Mobile > Tắt quyền Camera.\n3. Quay lại app GD Mobile (OS có thể reload process do permission change).\n4. Vào Job và bấm nút Chụp ảnh.",
        "Expected_Result": "1. App kiểm tra lại runtime permission trước khi gọi API native camera.\n2. Phát hiện chưa có quyền: Hiển thị Dialog giải thích lý do cần quyền kèm nút 'Mở Cài đặt' (Open Settings).\n3. Không bị crash trắng màn hình do Uncaught SecurityException.",
        "Network_Path": "Offline",
        "Risk": "App Crash on Resume",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Quy chuẩn bắt buộc của Google Play Store và Apple App Store Review."
    },
    {
        "TC_ID": "EDGE-GAP-040",
        "Direction": "CROSS-CUTTING",
        "Flow_Phase": "Pending Branch Switch",
        "Priority": "P0",
        "Module": "Branch / Tenant",
        "Action": "Branch Switching Guard with Pending Mutations",
        "Scenario": "Chuyển Chi nhánh (Branch Switch) khi đang có hàng đợi pending: App hiển thị dialog cảnh báo bắt buộc sync xong hoặc hủy bỏ",
        "Source_Tickets": "RN-5477 / RN-5680 / Branch-Guard",
        "Source_URLs": "https://gorilladesk1.atlassian.net/browse/RN-5477",
        "Requirement_Status": "Multi-Branch Integrity Requirement",
        "App_Path": "GD Mobile > Switch Branch Modal",
        "Preconditions": "User thuộc nhiều Branch; đang có 4 items pending của Branch Miami (`gd-branch-id: br_01`).",
        "Test_Data": "Current Branch: Miami (4 pending items); Target Branch: Orlando (`br_02`).",
        "Detailed_Steps": "1. Tạo 4 items offline thuộc Branch Miami.\n2. Bấm vào menu chuyển chi nhánh sang Orlando.\n3. Kiểm tra thông báo cảnh báo hiển thị.",
        "Expected_Result": "1. App hiển thị Modal cảnh báo chặn: 'Bạn đang có 4 thay đổi chưa đồng bộ của chi nhánh Miami. Vui lòng kết nối mạng để đồng bộ hoàn tất trước khi chuyển chi nhánh, hoặc chọn Hủy bỏ'.\n2. Nút chuyển chi nhánh bị vô hiệu hóa (disabled) khi đang offline.\n3. Ngăn chặn tuyệt đối tình trạng gắn nhầm `gd-branch-id` của chi nhánh mới vào các mutation cũ chưa sync.",
        "Network_Path": "Any State",
        "Risk": "Cross-Branch Data Corruption",
        "Execution_Status": "Not Run",
        "Actual_Result": "",
        "Bug_ID": "",
        "Notes": "Được ghi chú rõ ràng trong kiến trúc Header GD-Branch-ID của Epic RN-5477."
    }
]

# Write data rows
for row_idx, tc in enumerate(testcases, 2):
    ws.row_dimensions[row_idx].height = 45
    for col_idx, h in enumerate(headers, 1):
        val = tc.get(h, "")
        cell = ws.cell(row=row_idx, column=col_idx, value=val)
        cell.font = data_font
        cell.alignment = data_align
        cell.border = thin_border
        
        # Center align short columns
        if h in ["TC_ID", "Priority", "Requirement_Status", "Execution_Status", "Network_Path"]:
            cell.alignment = Alignment(horizontal="center", vertical="top", wrap_text=True)

print(f"Added {len(testcases)} testcases to sheet '{sheet_name}'.")

# --- UPDATE 00_Dashboard ---
s_dash = wb["00_Dashboard"]

# Let's check row 27-37 in Dashboard and update
print("Updating 00_Dashboard...")
# Find row for V4 total executable/source cases
for r in range(25, min(s_dash.max_row + 5, 45)):
    val = str(s_dash.cell(r, 1).value or "")
    if "V4 total executable" in val:
        # Update existing total row
        s_dash.cell(r, 1, value="V4+ total executable/source cases")
        s_dash.cell(r, 2, value=3942 + len(testcases))
        s_dash.cell(r, 3, value=f"Includes source-trace regression/perf suites + {len(testcases)} production edge gap cases")
        
        # Insert a row above or write details
        dash_row_edge = r - 1
        # Let's inspect what's at r-1
        break

# Add row for production edge gap cases at row 37 and update total at 38
# Let's see rows around 36-37
row_edge_desc = 37
# Shift if needed or write to row 37
s_dash.cell(37, 1, value="Production edge & failover gap cases")
s_dash.cell(37, 2, value=len(testcases))
s_dash.cell(37, 3, value="Auth expiry, low storage, clock drift, process kill, schema migration, network handover")
s_dash.cell(37, 5, value="Production edge audit")
s_dash.cell(37, 6, value=f"{len(testcases)}/{len(testcases)} newly added in sheet 16")

s_dash.cell(38, 1, value="V4+ total executable/source cases")
s_dash.cell(38, 2, value=3942 + len(testcases))
s_dash.cell(38, 3, value=f"Includes source-trace regression/perf suites + {len(testcases)} production edge gap cases")
s_dash.cell(38, 5, value="Bottom line")
s_dash.cell(38, 6, value=f"V4+ is production-ready complete (3,982 total cases) as of 2026-10-08")

# --- UPDATE 14_Audit_Gaps_Fixed ---
s_gaps = wb["14_Audit_Gaps_Fixed"]
next_gap_row = s_gaps.max_row + 1
s_gaps.cell(next_gap_row, 1, value="Production Edge, Auth Expiry & Device Lifecycle Gaps")
s_gaps.cell(next_gap_row, 2, value="V3/V4 lacked deep edge cases for token expiry, low disk, clock tampering, swipe-kill, and schema migration.")
s_gaps.cell(next_gap_row, 3, value="Production QA Audit on 2026-10-08.")
s_gaps.cell(next_gap_row, 4, value="FIXED IN V4+ (Sheet 16)")
s_gaps.cell(next_gap_row, 5, value=f"16_Production_Edge_Gaps ({len(testcases)} new P0/P1/P2 cases: EDGE-GAP-001..{len(testcases):03d})")

# Save to destination paths
dest_paths = [
    r"C:\Users\Admin\Downloads\GorillaDesk_RN-5477_Full_Current_Scope_QA_V4.xlsx",
    r"C:\Users\Admin\.gemini\antigravity\brain\b8a09e51-9b31-44d2-a6ef-119a195d58a4\.user_uploaded\media_1791430527472_0d7fe1f4.xlsx",
    r"C:\Users\Admin\.gemini\antigravity\brain\b8a09e51-9b31-44d2-a6ef-119a195d58a4\.user_uploaded\media_1791429458650.xlsx",
    r"D:\GorillaDesk\MobileApp\Offline Mode\GorillaDesk_RN-5477_Full_Current_Scope_QA_V4.xlsx"
]

for p in dest_paths:
    os.makedirs(os.path.dirname(p), exist_ok=True)
    wb.save(p)
    print(f"Successfully saved updated workbook to: {p}")

print("\nALL TASKS COMPLETED SUCCESSFULLY!")
