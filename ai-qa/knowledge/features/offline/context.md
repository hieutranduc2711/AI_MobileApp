# Feature: Offline Mode & Data Synchronization

## 1. Overview
Kỹ thuật viên GorillaDesk thường làm việc ở khu vực không có sóng di động (tầng hầm, vùng ngoại ô). Ứng dụng phải hoạt động trơn tru ở chế độ ngoại tuyến:
- Tạo / Xem / Sửa Job, Invoices, Estimates khi không có kết nối Internet.
- Chụp ảnh hiện trường, lấy chữ ký nghiệm thu và lưu trữ vào WatermelonDB / SQLite cục bộ.

## 2. Sync Lifecycle
1. **Offline State:** Icon đồng bộ trên header hiển thị cảnh báo (màu cam/chấm vàng). Mọi thao tác được xếp vào `Sync Queue`.
2. **Network Restored:** Khi có mạng trở lại, background worker tự động đẩy các payload trong hàng đợi lên API GorillaDesk.
3. **Completion:** Icon đồng bộ chuyển sang màu xanh lá (`synced`), các thực thể nhận ID chính thức từ server.
