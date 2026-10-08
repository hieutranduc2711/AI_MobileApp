# 🧠 GorillaDesk Knowledge Base & System Logic

Thư mục này là **Trung Tâm Tri Thức Nghiệp Vụ (Source of Truth)** của GorillaDesk dành cho hệ thống AI-QA Automation Runner và Agent Hermes Auditor.

---

## 📚 1. Các Tài Liệu Logic Nghiệp Vụ Cốt Lõi (Core Logic Documents)

### 📗 [GORILLADESK_INTERCOM_OPERATING_MANUAL.md](./GORILLADESK_INTERCOM_OPERATING_MANUAL.md) (46 KB)
* **Nguồn:** GorillaDesk Help Center & Knowledge Base chính thức ([intercom.help/gorilladesk/en](https://intercom.help/gorilladesk/en/)).
* **Nội dung:**
  - Hướng dẫn vận hành hệ thống GorillaDesk cho Agent tự động.
  - Bản đồ thực thể (Entity Model): Customer, Location, Job, Invoice, Estimate, Payment, Schedule, Route, Addon...
  - Cơ chế suy luận hành động (Action Reasoning): chuyển ngữ cảnh tự nhiên thành hành vi chuẩn xác.
  - Ràng buộc phân quyền, add-on plan và điều kiện tiên quyết.

### 📘 [GORILLADESK_SYSTEM_LOGIC_AND_PRODUCT_KNOWLEDGE.md](./GORILLADESK_SYSTEM_LOGIC_AND_PRODUCT_KNOWLEDGE.md) (75 KB)
* **Nguồn:** Tổng hợp từ tài liệu nội bộ team cung cấp (`Logic GorillaDesk.docx`, `Customer.docx`, `Service.docx`).
* **Nội dung:**
  - Logic nghiệp vụ chuyên sâu và quan hệ dữ liệu: Customer Profile, Service Locations, Contact, Work Orders.
  - Vòng đời trạng thái (Lifecycle & State Machine) của Job: Pending → In Progress → Completed, Master Invoicing, Multi-stop routing.
  - Chuỗi phụ thuộc (Dependency Chain) và quy tắc toàn vẹn dữ liệu khi tạo offline/online.
  - Phân loại mức độ xác thực: `[Tester Confirmed]`, `[Guide Confirmed]`, `[UI Observed]`, `[Probe Passed]`.

---

## 🗺️ 2. Bản Đồ Selector & Định Danh Giao Diện (UI Object Repository)
* **`DYNAMIC_SELECTORS_REGISTRY.yaml`** (112 KB - 4,900+ dòng): Bản đồ Dynamic Selectors bóc tách từ thiết bị Android thực tế (Samsung Galaxy & Google Pixel 5).
* **`ELEMENT_REPOSITORY.yaml`** (142 KB): Kho lưu trữ thành phần UI theo từng màn hình.
* **`SCOPE_COVERAGE_MAP.md`**: Ma trận bao phủ tính năng và phân hệ kiểm thử.

---

## 📂 3. Vị Trí Đồng Bộ Trong Dự Án
Các tài liệu logic này được lưu trữ đồng bộ tại:
1. `d:\artemis\AI_MobileApp\ai-qa\knowledge\` (Dành cho AI-QA Runner & ADB Engine)
2. `D:\GorillaDesk\MobileApp\Offline Mode\` (Dành cho Hermes Desktop App & Workspace)
