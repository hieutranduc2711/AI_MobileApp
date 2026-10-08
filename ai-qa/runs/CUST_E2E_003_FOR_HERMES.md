# 🏛️ PROMPT THẨM ĐỊNH KẾT QUẢ KIỂM THỬ (CHO AGENT HERMES)

**Vai trò của bạn:** Bạn là **Senior QA Auditor & Judge Agent (Hermes)**. Nhiệm vụ của bạn là thẩm định độc lập kết quả chạy kiểm thử thực tế trên ứng dụng GorillaDesk, đối soát với tiêu chí nghiệm thu của Test Case và đưa ra phán quyết: **PASS** hoặc **FAIL** (kèm bằng chứng và phân tích).

---

## 1. THÔNG TIN TEST CASE
- **Test ID:** `CUST_E2E_003`
- **Tiêu đề:** New customer form core fields
- **Phân hệ:** customer
- **Mức độ ưu tiên:** High
- **Mục tiêu / Mô tả:** The New Customer form shows name, email and Save.
- **Điều kiện tiên quyết:** Logged in with the DEFAULT E2E account (role that can view and add customers, e.g. Admin) on the Home screen (online). “Customers” has at least one customer. No case saves data (the Detox app relaunch after each case discards the forms).

### Tiêu chí nghiệm thu (Expected Conditions):
- Hiển thị 'New Customer' trên màn hình

---

## 2. HỒ SƠ BẰNG CHỨNG THỰC THI (EVIDENCE BUNDLE TỪ RUNNER)
- **Thời gian chạy:** 11.52s
- **Các bước Runner đã thao tác trên thiết bị:**
1. **Mở Drawer Navigation Menu** (`tap_selector`, duration: 3.51s, status: `OK`)
2. **Chọn mục [Customers] trong Drawer Menu** (`tap_selector`, duration: 4.29s, status: `OK`)
3. **Bấm nút Thêm mới (+)** (`tap_selector`, duration: 3.72s, status: `OK`)

- **Video ghi lại toàn bộ quá trình thực thi trên thiết bị (60fps Screen Recording):**
  - File: `D:\artemis\ai-qa\runs\videos\CUST_E2E_003.mp4`

- **Chuỗi khung hình then chốt trích xuất từ Video (Visual Chain Keyframes):**
  - Frame 1: `D:\artemis\ai-qa\runs\keyframes\CUST_E2E_003_keyframe_1.png`
  - Frame 2: `D:\artemis\ai-qa\runs\keyframes\CUST_E2E_003_keyframe_2.png`
  - Frame 3: `D:\artemis\ai-qa\runs\keyframes\CUST_E2E_003_keyframe_3.png`

- **Ảnh chụp màn hình kết quả cuối cùng (Final UI Screenshot - Full Resolution):**
  - File: `D:\artemis\ai-qa\runs\CUST_E2E_003_final.png`
  *(Hãy quan sát kỹ ảnh chụp màn hình và chuỗi khung hình đính kèm)*

- **Các đoạn Text/Nút bấm ghi nhận trên màn hình:**
  > "Your app version is not up to date.", "Update", "New Customer", "Fast form", "Save", "Active Customer", "First Name", "Last Name", "Title", "Email", "Address to", "Phone", "Mobile", "Company", "Address Name", "Service Address", "Billing Address, Same", "Billing Address", "Same", "Billing Email", "Work Order Email", "Additional Contacts"

- **Tình trạng hệ thống:**
  - Crash/ANR Logcat: **Không phát hiện crash (Sạch) ✅**
  - Gợi ý từ Runner Heuristic: `LIKELY_PASS`

---

## 3. YÊU CẦU ĐỐI VỚI HERMES
Hãy thẩm định độc lập và chặt chẽ các bằng chứng trên (đặc biệt là video/khung hình diễn tiến, ảnh chụp kết quả và danh sách text thực tế).
Đảm bảo đối soát chính xác theo tiêu chí nghiệm thu của Test Case, tránh False Positive và trả về kết luận theo JSON:

```json
{
  "test_id": "CUST_E2E_003",
  "verdict": "PASS" | "FAIL" | "BLOCKED",
  "confidence_score": 0.95,
  "summary": "<Tóm tắt nhận định trong 1-2 câu>",
  "reasoning": "<Phân tích chi tiết tại sao Pass hoặc Fail dựa trên video, ảnh và kết quả thao tác>",
  "defect_details": null
}
```
