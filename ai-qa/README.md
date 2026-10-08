# AI-QA GorillaDesk Mobile Automation Framework

Framework kiểm thử tự động thế hệ mới cho ứng dụng **GorillaDesk Mobile** (`com.gorilladesk.rn`), kết hợp giữa **Cơ sở tri thức kiểm thử (Test Knowledge Base)**, **Bộ điều phối QA (QA Orchestrator)**, và **Bộ thực thi siêu tốc (Fast-Action ADB Runner & ARTEMIS Agent)**.

---

## 1. Sơ Đồ Kiến Trúc Hệ Thống (Architecture)

```text
Test Knowledge Base
  ├── Feature checklist (Detox / Google Sheet)
  ├── Context / setup (Accounts, Fixtures)
  └── Risks / history (UI traps, Bugs)
            │
      QA Orchestrator
            │
   generates test missions
            │
    ARTEMIS Pro Agent (or ADB Fast Burst)
            │
  Android device / emulator (Samsung A36)
  ├── Screenshot
  ├── Logcat
  └── UI hierarchy
            │
         Checker (Evaluators)
            │
     PASS / FAIL / BUG
```

---

## 2. Cấu Trúc Thư Mục (Directory Structure)

```text
ai-qa/
├── config/              # Cấu hình app, môi trường, chính sách thực thi
├── knowledge/           # Tri thức nghiệp vụ, luật toàn cục, rủi ro từng tính năng
│   ├── global/          # product-context.md, business-rules.yaml, qa-rules.md
│   ├── features/        # customers/, scheduling/, invoices/, offline/...
│   └── bugs/            # Lịch sử các lỗi để kiểm thử hồi quy
├── testcases/           # Kịch bản kiểm thử dạng YAML (declarative testcases)
├── suites/              # Gom nhóm kịch bản (smoke, critical, offline-mode)
├── datasets/            # Dữ liệu kiểm thử mẫu (accounts, customers, routes)
├── prompts/             # System prompts chuyên dụng cho AI Agent
├── orchestrator/        # Trình điều phối chạy test & nạp kịch bản (main.py, loader.py)
├── adapters/            # Kết nối thiết bị qua ADB & ARTEMIS, xuất báo cáo Bug
├── evaluators/          # Thẩm định lỗi: crash detector, console error, screenshot
├── reports/             # Báo cáo kết quả kiểm thử sau mỗi lượt chạy
└── runs/                # Ảnh chụp màn hình nghiệm thu từng test case
```

---

## 3. Hướng Dẫn Sử Dụng & Lệnh Chạy (Code Run)

### Yêu cầu tiên quyết:
- Python 3.10+
- Thiết bị Android đã bật **USB Debugging** và kết nối qua ADB (`adb devices`).

### Lệnh chạy kiểm thử:

1. **Chạy trọn gói bộ Smoke Test Suite:**
   ```bash
   python d:/artemis/ai-qa/orchestrator/main.py --suite smoke
   ```

2. **Chạy riêng một Test Case cụ thể (Ví dụ: Tạo Job):**
   ```bash
   python d:/artemis/ai-qa/orchestrator/main.py --test JOB-CREATE-001
   ```

3. **Chạy kịch bản Kiểm thử Ngoại tuyến (Offline Mode Suite):**
   ```bash
   python d:/artemis/ai-qa/orchestrator/main.py --suite offline-mode
   ```

---

## 4. Kế Hoạch Tuần Này: Đánh Giá Chế Độ Ngoại Tuyến (Offline Mode Plan)

- [x] **Xây dựng module điều khiển mạng:** Tích hợp `set_wifi()` và `set_data()` trực tiếp trong `adapters/adb.py`.
- [x] **Đặc tả tri thức Offline:** Tạo `knowledge/features/offline/context.md` và `risks.yaml`.
- [x] **Xây dựng Test Case mẫu:** `testcases/offline/OFFLINE-SYNC-001.yaml` (Ngắt mạng $\rightarrow$ Tạo Job $\rightarrow$ Bật mạng $\rightarrow$ Kiểm tra đồng bộ).
- [ ] **Mở rộng kịch bản:** Bổ sung Offline Estimate, Offline Invoices, và kiểm tra hàng đợi Sync Queue khi app bị đóng đột ngột (crash/kill).
