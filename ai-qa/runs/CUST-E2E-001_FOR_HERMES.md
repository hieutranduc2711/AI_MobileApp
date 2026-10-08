# 🏛️ PROMPT THẨM ĐỊNH KẾT QUẢ KIỂM THỬ (CHO AGENT HERMES)

**Vai trò của bạn:** Bạn là **Senior QA Auditor & Judge Agent (Hermes)**. Nhiệm vụ của bạn là thẩm định độc lập kết quả chạy kiểm thử thực tế trên ứng dụng GorillaDesk, đối soát với tiêu chí nghiệm thu của Test Case và đưa ra phán quyết: **PASS** hoặc **FAIL** (kèm bằng chứng và phân tích chi tiết).

---

## 1. THÔNG TIN TEST CASE
- **Test ID:** `CUST-E2E-001`
- **Tiêu đề:** Create New Customer with Real Data and Verify Persistence
- **Phân hệ:** customer
- **Mức độ ưu tiên:** High
- **Loại kiểm thử:** `E2E_MUTATION` (Tier 2)
- **Mục tiêu / Mô tả:** Tạo mới khách hàng hoàn chỉnh với tên độc nhất (Dynamic Nonce), chọn Service Address bắt buộc, lưu dữ liệu và kiểm tra hồ sơ Customer Profile.
- **Điều kiện tiên quyết:** 

### Tiêu chí nghiệm thu (Expected Conditions):
- Tên khách hàng độc nhất phải hiển thị trên màn hình Profile
- Giao diện đã chuyển từ Form sang Customer Profile Hub
- Form New Customer đã đóng hoàn toàn

---

## ⚠️ QUY TẮC THẨM ĐỊNH NGHIÊM NGẶT (STRICT AUDITOR RUBRIC - 5-POINT MUTATION CONTRACT):
Đây là ca kiểm thử **Biến Đổi Dữ Liệu Thực Tế (Tier 2: E2E Mutation)**. Để loại bỏ 100% rủi ro False Positive (lọt bug), Hermes **BẮT BUỘC** phải tuân thủ nghiêm ngặt 3 quy tắc sau:
1. **Quy tắc Nonce Độc Nhất (Mutation Proof):**
   - Giá trị Nonce được sinh ra cho lượt test này là: `HieuQA_57000`
   - Màn hình kết quả hoặc danh sách trích xuất **BẮT BUỘC PHẢI CHỨA ĐÚNG CHUỖI:** `HieuQA_57000`.
   - Nếu không tìm thấy đúng chuỗi này -> **KẾT LUẬN FAIL NGAY LẬP TỨC** (Lý do: Không có dữ liệu nào được tạo mới).
2. **Quy tắc Thoát Form (State Transition Proof):**
   - Màn hình **BẮT BUỘC phải chuyển sang Customer Profile Hub** (có 'All Locations', mã #ID).
   - Form 'New Customer' ban đầu **BẮT BUỘC PHẢI ĐÓNG HOÀN TOÀN**.
   - Nếu màn hình vẫn đứng im ở Form nhập liệu -> **KẾT LUẬN FAIL NGAY LẬP TỨC** (Lý do: Bấm Save nhưng form không lưu, có thể bị lỗi validation hoặc đơ).
3. **Quy tắc Sạch Lỗi Hệ Thống (Clean System):**
   - Logcat không có crash hoặc lỗi 500.

👉 **CHỈ ĐƯỢC PHÉP CẤP CỜ PASS KHI CẢ 3 ĐIỀU KIỆN TRÊN ĐỒNG THỜI ĐẠT 100%!**

---

## 2. HỒ SƠ BẰNG CHỨNG THỰC THI (EVIDENCE BUNDLE TỪ RUNNER)
- **Thời gian chạy:** 31.21s
- **Các bước Runner đã thao tác trên thiết bị:**
1. **Chạm vào ô First Name** (`tap_selector`, duration: 3.22s, status: `OK`)
2. **Nhập tên First Name độc nhất** (`type_text`, duration: 0.94s, status: `OK`)
3. **Chạm vào ô Last Name** (`tap_selector`, duration: 3.17s, status: `OK`)
4. **Nhập họ Last Name** (`type_text`, duration: 0.76s, status: `OK`)
5. **Ẩn bàn phím ảo để lộ trường địa chỉ** (`hide_keyboard`, duration: 0.57s, status: `OK`)
6. **Mở Modal chọn Service Address** (`tap_selector`, duration: 3.85s, status: `ELEMENT_NOT_FOUND`)
7. **Chạm vào ô tìm kiếm địa chỉ** (`tap_selector`, duration: 3.41s, status: `ELEMENT_NOT_FOUND`)
8. **Nhập từ khóa tìm địa chỉ 'Miami'** (`type_text`, duration: 2.16s, status: `OK`)
9. **Chọn địa chỉ gợi ý đầu tiên** (`tap_selector`, duration: 3.62s, status: `OK`)
10. **Bấm nút Save trên Modal địa chỉ** (`tap_selector`, duration: 3.68s, status: `OK`)
11. **Bấm nút Save New Customer (Hoàn tất tạo khách hàng)** (`tap_selector`, duration: 5.83s, status: `OK`)

- **Video ghi lại toàn bộ quá trình thực thi trên thiết bị (60fps Screen Recording):**
  - File: `D:\artemis\ai-qa\runs\videos\CUST-E2E-001.mp4`

- **Chuỗi khung hình then chốt trích xuất từ Video (Visual Chain Keyframes):**
  - Frame 1: `D:\artemis\ai-qa\runs\keyframes\CUST-E2E-001_keyframe_1.png`
  - Frame 2: `D:\artemis\ai-qa\runs\keyframes\CUST-E2E-001_keyframe_2.png`
  - Frame 3: `D:\artemis\ai-qa\runs\keyframes\CUST-E2E-001_keyframe_3.png`

- **Ảnh chụp màn hình kết quả cuối cùng (Final UI Screenshot - Full Resolution):**
  - File: `D:\artemis\ai-qa\runs\CUST-E2E-001_final.png`
  *(Hãy quan sát kỹ ảnh chụp màn hình và chuỗi khung hình đính kèm)*

- **Các đoạn Text/Nút bấm ghi nhận trên màn hình:**
  > "Your app version is not up to date.", "Update", "New Customer", "Fast form", "Save", "Active Customer", "HieuQA_57000", "MasterQAMiami", "Title", "Email", "HieuQA_57000 MasterQAMiami", "Phone", "Mobile", "Company", "Address Name", "Service Address", "Billing Address, Same", "Billing Address", "Same", "Billing Email", "Work Order Email", "Additional Contacts"

- **Tình trạng hệ thống:**
  - Crash/ANR Logcat: **Không phát hiện crash (Sạch) ✅**
  - Gợi ý từ Runner Heuristic: `HEURISTIC_WARNING: Missing expected text 'All Locations'`

---

## 3. YÊU CẦU ĐỐI VỚI HERMES
Hãy thẩm định độc lập và chặt chẽ các bằng chứng trên (đặc biệt là video/khung hình diễn tiến, ảnh chụp kết quả và danh sách text thực tế).
Đảm bảo đối soát chính xác theo tiêu chí nghiệm thu của Test Case, tránh False Positive và trả về kết luận theo JSON:

```json
{
  "test_id": "CUST-E2E-001",
  "verdict": "PASS" | "FAIL" | "BLOCKED",
  "confidence_score": 0.95,
  "summary": "<Tóm tắt nhận định trong 1-2 câu>",
  "reasoning": "<Phân tích chi tiết tại sao Pass hoặc Fail dựa trên video, ảnh và kết quả thao tác>",
  "defect_details": null
}
```
