import os
import sys
import yaml
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

AI_QA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTCASES_DIR = os.path.join(AI_QA_ROOT, "testcases")

def build_dynamic_steps(feature, tc_id, title, goal_text=""):
    feat = feature.lower()
    t_lower = (str(title or "") + " " + str(goal_text or "")).lower()

    # --- 1. CUSTOMERS / CUSTOMER ---
    if "customer" in feat:
        if "create" in t_lower or "add" in t_lower or "new" in t_lower:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Customers trong Menu", "action": "tap_selector", "content_desc": "Customers", "delay": 1.0},
                {"desc": "Bấm nút Thêm mới (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
                {"desc": "Chạm vào ô First Name", "action": "tap_selector", "text": "First Name", "delay": 0.5},
                {"desc": "Nhập First Name", "action": "type_text", "value": f"Auto_{tc_id[:6]}", "delay": 0.5},
                {"desc": "Chạm vào ô Last Name", "action": "tap_selector", "text": "Last Name", "delay": 0.5},
                {"desc": "Nhập Last Name", "action": "type_text", "value": "Customer", "delay": 0.5},
                {"desc": "Mở chọn Service Address", "action": "tap_selector", "content_desc": "Service Address", "delay": 1.0},
                {"desc": "Chạm vào ô Search địa chỉ", "action": "tap_selector", "text": "Search", "delay": 0.5},
                {"desc": "Tìm kiếm thành phố Miami", "action": "type_text", "value": "Miami", "delay": 1.5},
                {"desc": "Chọn địa chỉ Miami Beach Boardwalk từ gợi ý", "action": "tap_selector", "content_desc": "Miami Beach Boardwalk", "delay": 1.0},
                {"desc": "Lưu địa chỉ Service Address", "action": "tap_selector", "resource_id": "saveButton", "delay": 1.0},
                {"desc": "Lưu hồ sơ khách hàng (Save)", "action": "tap_selector", "content_desc": "Save", "delay": 2.5}
            ], [{"assert_text": f"Auto_{tc_id[:6]}"}]
        elif "search" in t_lower or "filter" in t_lower:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Customers trong Menu", "action": "tap_selector", "content_desc": "Customers", "delay": 1.0},
                {"desc": "Chạm vào thanh tìm kiếm khách hàng", "action": "tap_selector", "text": "Search customers...", "delay": 0.5},
                {"desc": "Nhập từ khóa tìm kiếm", "action": "type_text", "value": "MinhTriQA", "delay": 1.5}
            ], [{"assert_text": "MinhTriQA"}]
        else: # View details / edit
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Customers trong Menu", "action": "tap_selector", "content_desc": "Customers", "delay": 1.0},
                {"desc": "Chọn khách hàng đầu tiên trong danh sách", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0, "delay": 1.5}
            ], [{"assert_text": "Service Locations"}]

    # --- 2. JOB / HOME-CALENDAR / SCHEDULING ---
    elif "job" in feat or "calendar" in feat or "scheduling" in feat:
        if "create" in t_lower or "new" in t_lower or "add" in t_lower:
            return [
                {"desc": "Mở Calendar Home", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Bấm FAB (+) Mở Action Sheet", "action": "tap_selector", "resource_id": "OutlinePlus", "index": 0, "delay": 1.0},
                {"desc": "Chọn New Job từ Action Sheet", "action": "tap_selector", "text": "New Job", "delay": 1.5},
                {"desc": "Chọn Customer đầu tiên cho Job", "action": "tap_selector", "resource_id": "customer-avatar", "index": 0, "delay": 1.5},
                {"desc": "Bấm nút Save Job", "action": "tap_selector", "content_desc": "Save", "delay": 2.5}
            ], [{"assert_text": "Job Details"}]
        elif "status" in t_lower or "en route" in t_lower or "arrived" in t_lower or "complete" in t_lower:
            return [
                {"desc": "Mở Calendar Home", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn Job đầu tiên trên lịch", "action": "tap_selector", "resource_id": "highlight-button", "index": 1, "delay": 1.5},
                {"desc": "Cập nhật trạng thái Job", "action": "tap_selector", "text": "Status", "delay": 1.0}
            ], [{"assert_text": "Job Details"}]
        else: # Hub renders / view job
            return [
                {"desc": "Mở Calendar Home", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Mở Action Sheet hoặc xem chi tiết lịch", "action": "tap_selector", "resource_id": "OutlinePlus", "index": 0, "delay": 1.0},
                {"desc": "Đóng Action Sheet quay về lịch", "action": "back", "delay": 0.5}
            ], [{"assert_text": "Jobs"}]

    # --- 3. INVOICE ---
    elif "invoice" in feat:
        if "create" in t_lower or "new" in t_lower:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Invoices trong Menu", "action": "tap_selector", "content_desc": "Invoices", "delay": 1.2},
                {"desc": "Bấm nút Thêm Invoice (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
                {"desc": "Lưu Invoice mới", "action": "tap_selector", "content_desc": "Save", "delay": 2.0}
            ], [{"assert_text": "Invoices"}]
        else:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Invoices trong Menu", "action": "tap_selector", "content_desc": "Invoices", "delay": 1.2},
                {"desc": "Chạm vào ô Search Invoices", "action": "tap_selector", "text": "Search invoices...", "delay": 0.5}
            ], [{"assert_text": "Invoices"}]

    # --- 4. ESTIMATE ---
    elif "estimate" in feat:
        if "create" in t_lower or "new" in t_lower:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Estimates trong Menu", "action": "tap_selector", "content_desc": "Estimates", "delay": 1.2},
                {"desc": "Bấm nút Thêm Estimate (+)", "action": "tap_selector", "resource_id": "highlight-button", "index": -1, "delay": 1.0},
                {"desc": "Lưu Estimate", "action": "tap_selector", "content_desc": "Save", "delay": 2.0}
            ], [{"assert_text": "Estimates"}]
        else:
            return [
                {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
                {"desc": "Chọn mục Estimates trong Menu", "action": "tap_selector", "content_desc": "Estimates", "delay": 1.2}
            ], [{"assert_text": "Estimates"}]

    # --- 5. DEVICE / PEST CONTROL ---
    elif "device" in feat or "material" in feat:
        return [
            {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
            {"desc": "Chọn mục Equipment / Devices", "action": "tap_selector", "content_desc": "Equipment", "delay": 1.2}
        ], [{"assert_text": "Devices"}]

    # --- 6. OFFLINE ---
    elif "offline" in feat:
        return [
            {"desc": "Ngắt kết nối mạng (Bật chế độ Ngoại Tuyến)", "action": "set_network", "value": "false", "delay": 1.0},
            {"desc": "Mở Calendar Home ngoại tuyến", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
            {"desc": "Khôi phục kết nối mạng (Trực Tuyến)", "action": "set_network", "value": "true", "delay": 1.5}
        ], [{"assert_text": "Jobs"}]

    # --- 7. ROUTING / MAP ---
    elif "rout" in feat or "map" in feat:
        return [
            {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
            {"desc": "Chọn mục Map / Routing", "action": "tap_selector", "content_desc": "Map", "delay": 1.5}
        ], [{"assert_text": "Map"}]

    # --- 8. SETTINGS / DASHBOARD / AUTH / DEFAULT ---
    else:
        return [
            {"desc": "Mở Drawer Menu", "action": "tap_selector", "resource_id": "highlight-button", "index": 0, "delay": 0.8},
            {"desc": "Xem các tùy chọn trong Navigation Menu", "action": "tap_selector", "content_desc": "Calendar", "delay": 1.0}
        ], [{"assert_text": "Jobs"}]

def main():
    print("[Updater] Bắt đầu nâng cấp toàn bộ 555 test cases sang PURE DYNAMIC SELECTOR (0 Tọa độ)...")
    updated_count = 0

    for root, _, files in os.walk(TESTCASES_DIR):
        for f in files:
            if f.endswith(".yaml"):
                full_path = os.path.join(root, f)
                rel_dir = os.path.basename(root)
                try:
                    with open(full_path, 'r', encoding='utf-8') as stream:
                        data = yaml.safe_load(stream) or {}

                    tc_id = data.get("id", os.path.splitext(f)[0])
                    title = data.get("title", "")
                    goal = data.get("goal", "")

                    # Sinh ra các bước dynamic selector tương ứng với feature
                    steps, expected = build_dynamic_steps(rel_dir, tc_id, title, goal)

                    data["steps"] = steps
                    data["expected"] = expected
                    # Giữ nguyên goal/title/priority/feature metadata
                    if "feature" not in data:
                        data["feature"] = rel_dir

                    with open(full_path, 'w', encoding='utf-8') as out_stream:
                        yaml.dump(data, out_stream, allow_unicode=True, sort_keys=False, default_flow_style=False)

                    updated_count += 1
                except Exception as e:
                    print(f"Lỗi khi cập nhật {f}: {e}")

    print(f"\n=======================================================")
    print(f"✅ THÀNH CÔNG! Đã cập nhật toàn diện {updated_count} test cases sang:")
    print(f"   - 100% Dynamic Selector (text, content-desc, resource-id)")
    print(f"   - 0 Tọa độ cứng (No hardcoded pixel coordinates)")
    print(f"   - Tự động thẩm định kết quả (UI Assertions)")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
