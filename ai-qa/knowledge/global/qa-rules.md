# QA Rules & Mobile Automation Best Practices

## 1. Dynamic First, Coordinate Fallback
- Ưu tiên tìm element theo content-desc hoặc text khi dùng Framework nhận diện.
- Khi cần tốc độ tối đa (< 8s), dùng Normalized Coordinates (% W, % H) tự động scale theo màn hình.

## 2. Fast-Action Burst Execution
- Không gọi LLM từng bước trong các kịch bản lặp lại đã được verify.
- Bắn chuỗi hành động trực tiếp bằng ADB driver để vượt qua turn latency.

## 3. UI Trap Avoidance (Tránh bẫy UI)
- Tránh vùng Search bar (Y = 200 - 350px) khi chọn item danh sách. Vị trí an toàn luôn là `(50%, 18.8%)`.
- Chờ form re-render tối thiểu 850ms sau khi đóng các modal (Line item, Template) trước khi nhấn Save.
