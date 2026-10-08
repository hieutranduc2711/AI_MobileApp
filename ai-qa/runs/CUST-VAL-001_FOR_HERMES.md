# 🏛️ PROMPT THẨM ĐỊNH KẾT QUẢ KIỂM THỬ (CHO AGENT HERMES)

**Vai trò của bạn:** Bạn là **Senior QA Auditor & Judge Agent (Hermes)**. Nhiệm vụ của bạn là thẩm định độc lập kết quả chạy kiểm thử thực tế trên ứng dụng GorillaDesk, đối soát với tiêu chí nghiệm thu của Test Case và đưa ra phán quyết: **PASS** hoặc **FAIL** (kèm bằng chứng và phân tích chi tiết).

---

## 1. THÔNG TIN TEST CASE
- **Test ID:** `CUST-VAL-001`
- **Tiêu đề:** Negative Test - Block Save Customer When Service Address is Missing
- **Phân hệ:** customer
- **Mức độ ưu tiên:** High
- **Loại kiểm thử:** `NEGATIVE_VALIDATION` (Tier 1)
- **Mục tiêu / Mô tả:** Kiểm tra hệ thống bắt buộc nhập Service Address, chặn lưu và giữ người dùng ở lại form New Customer khi cố tình bỏ trống Service Address.
- **Điều kiện tiên quyết:** 

### Tiêu chí nghiệm thu (Expected Conditions):
- Hệ thống phải chặn lưu và giữ nguyên người dùng ở form New Customer
- Trường Service Address vẫn hiện diện (được đánh dấu đỏ bắt buộc)

---

## ⚠️ QUY TẮC THẨM ĐỊNH CA KIỂM THỬ CHẶN LỖI (STRICT NEGATIVE VALIDATION RUBRIC):
Đây là ca kiểm thử **Chặn Lỗi (Tier 1: Negative Validation)**.
Mục tiêu của bài test là chứng minh ứng dụng **chặn thành công hành vi không hợp lệ** (cố tình bỏ trống trường bắt buộc Service Address):
1. **Quy tắc Chặn Lưu (Block Enforcement):**
   - Ứng dụng **BẮT BUỘC PHẢI CHẶN**, giữ người dùng ở lại form `New Customer` và không được phép lưu vào hệ thống.
   - Trường `Service Address` phải được cảnh báo (bôi đỏ, chấm đỏ bắt buộc, hoặc thông báo 'Missed required fields').
2. **Quy tắc Không Được Lọt (No Validation Bypass):**
   - Nếu ứng dụng bị lỗi mà vẫn cho lưu (thoát form chuyển sang Customer Profile) -> **KẾT LUẬN FAIL** (Lý do: Bug bảo mật / Bỏ lọt validation dữ liệu bắt buộc).
   - Nếu ứng dụng bị crash hoặc văng app khi bấm Save -> **KẾT LUẬN FAIL**.
3. **Phán quyết PASS khi:**
   - Ứng dụng xử lý đúng chuẩn: Từ chối lưu, giữ nguyên ở form New Customer để người dùng sửa đổi, không bị crash!

---

## 2. HỒ SƠ BẰNG CHỨNG THỰC THI (EVIDENCE BUNDLE TỪ RUNNER)
- **Thời gian chạy:** 17.0s
- **Các bước Runner đã thao tác trên thiết bị:**
1. **Bấm nút Thêm mới (+) trên màn hình Customers** (`tap_selector`, duration: 3.4s, status: `OK`)
2. **Chạm vào ô First Name** (`tap_selector`, duration: 3.51s, status: `OK`)
3. **Nhập First Name** (`type_text`, duration: 0.78s, status: `OK`)
4. **Chạm vào ô Last Name** (`tap_selector`, duration: 3.14s, status: `OK`)
5. **Nhập Last Name** (`type_text`, duration: 0.84s, status: `OK`)
6. **Ẩn bàn phím ảo** (`hide_keyboard`, duration: 0.57s, status: `OK`)
7. **Cố tình bấm nút Save khi chưa chọn Service Address** (`tap_selector`, duration: 4.75s, status: `OK`)

- **Video ghi lại toàn bộ quá trình thực thi trên thiết bị (60fps Screen Recording):**
  - File: `D:\artemis\ai-qa\runs\videos\CUST-VAL-001.mp4`

- **Chuỗi khung hình then chốt trích xuất từ Video (Visual Chain Keyframes):**
  - Frame 1: `D:\artemis\ai-qa\runs\keyframes\CUST-VAL-001_keyframe_1.png`
  - Frame 2: `D:\artemis\ai-qa\runs\keyframes\CUST-VAL-001_keyframe_2.png`
  - Frame 3: `D:\artemis\ai-qa\runs\keyframes\CUST-VAL-001_keyframe_3.png`

- **Ảnh chụp màn hình kết quả cuối cùng (Final UI Screenshot - Full Resolution):**
  - File: `D:\artemis\ai-qa\runs\CUST-VAL-001_final.png`
  *(Hãy quan sát kỹ ảnh chụp màn hình và chuỗi khung hình đính kèm)*

- **Các đoạn Text/Nút bấm ghi nhận trên màn hình:**
  > "Your app version is not up to date.", "Update", "New Customer", "Fast form", "Save", "Active Customer", "NegativeQA", "NoAddressTest", "Title", "Email", "NegativeQA NoAddressTest", "Phone", "Mobile", "Company", "Address Name", "Service Address", "Billing Address, Same", "Billing Address", "Same", "Billing Email", "Work Order Email", "Additional Contacts"

- **Tình trạng hệ thống:**
  - Crash/ANR Logcat: **Không phát hiện crash (Sạch) ✅**
  - Gợi ý từ Runner Heuristic: `LIKELY_PASS`

---

## 3. YÊU CẦU ĐỐI VỚI HERMES
Hãy thẩm định độc lập và chặt chẽ các bằng chứng trên (đặc biệt là video/khung hình diễn tiến, ảnh chụp kết quả và danh sách text thực tế).
Đảm bảo đối soát chính xác theo tiêu chí nghiệm thu của Test Case, tránh False Positive và trả về kết luận theo JSON:

```json
{
  "test_id": "CUST-VAL-001",
  "verdict": "PASS" | "FAIL" | "BLOCKED",
  "confidence_score": 0.95,
  "summary": "<Tóm tắt nhận định trong 1-2 câu>",
  "reasoning": "<Phân tích chi tiết tại sao Pass hoặc Fail dựa trên video, ảnh và kết quả thao tác>",
  "defect_details": null
}
```
