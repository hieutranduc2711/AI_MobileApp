import os
import sys
import time
import re
import yaml
import xml.etree.ElementTree as ET
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_QA_ROOT = os.path.dirname(CURRENT_DIR)
if AI_QA_ROOT not in sys.path:
    sys.path.insert(0, AI_QA_ROOT)

from adapters.adb import ADBClient

def parse_xml_elements(xml_path):
    elements = []
    if not os.path.exists(xml_path):
        return elements
    try:
        tree = ET.parse(xml_path)
        for node in tree.getroot().iter('node'):
            text = node.get('text', '').strip()
            desc = node.get('content-desc', '').strip()
            res_id = node.get('resource-id', '').strip()
            cls = node.get('class', '').strip()
            clickable = node.get('clickable', 'false') == 'true'
            focusable = node.get('focusable', 'false') == 'true'
            bounds = node.get('bounds', '')

            # Chỉ giữ các element có ý nghĩa nhận diện (có text, desc, id hoặc là nút bấm/input)
            if text or desc or res_id:
                m = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                center = None
                if m:
                    x1, y1, x2, y2 = map(int, m.groups())
                    if x2 > x1 and y2 > y1:
                        center = [(x1 + x2) // 2, (y1 + y2) // 2]
                
                # Xác định loại control
                role = "unknown"
                if "EditText" in cls or "input" in res_id.lower() or text in ["First Name", "Last Name", "Search", "Email", "Phone"]:
                    role = "input"
                elif clickable or "Button" in cls or "highlight" in res_id.lower():
                    role = "button"
                elif text:
                    role = "label"

                elem_info = {
                    "role": role,
                    "text": text if text else None,
                    "content_desc": desc if desc else None,
                    "resource_id": res_id if res_id else None,
                    "class": cls,
                    "clickable": clickable,
                    "bounds": bounds,
                    "center": center
                }
                elements.append(elem_info)
    except Exception as e:
        print(f"Error parsing {xml_path}: {e}")
    return elements

def clean_elements(elements):
    # Loại bỏ trùng lặp
    unique = []
    seen = set()
    for el in elements:
        key = (el["role"], el["text"], el["content_desc"], el["resource_id"])
        if key not in seen:
            seen.add(key)
            unique.append(el)
    return unique

def capture_screen(adb, screen_name, out_dir):
    xml_path = os.path.join(out_dir, f"{screen_name}.xml")
    png_path = os.path.join(out_dir, f"{screen_name}.png")
    adb.dump_hierarchy(xml_path)
    adb.screencap(png_path)
    elems = parse_xml_elements(xml_path)
    elems = clean_elements(elems)
    return elems

def main():
    print("[Crawler] Đang khởi tạo kết nối ADB...")
    adb = ADBClient()
    out_dir = os.path.join(AI_QA_ROOT, "knowledge", "screens")
    os.makedirs(out_dir, exist_ok=True)
    registry_file = os.path.join(AI_QA_ROOT, "knowledge", "DYNAMIC_SELECTORS_REGISTRY.yaml")

    registry = {}
    if os.path.exists(registry_file):
        try:
            with open(registry_file, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f) or {}
        except Exception:
            registry = {}

    print(f"[Crawler] Bắt đầu quét màn hình hiện tại trên máy {adb.serial}...")
    
    # 1. Quét màn hình hiện tại
    curr_elems = capture_screen(adb, "current_focus", out_dir)
    print(f"  • Màn hình hiện tại thu thập được {len(curr_elems)} selectors định danh.")

    # 2. Quét Calendar Home (đưa về Calendar Home)
    print("\n[Crawler] Đang điều hướng về [Calendar Home]...")
    adb.shell("am start -n com.gorilladesk.rn/com.gorilladesk.rn.MainActivity")
    time.sleep(2)
    # Tắt banner cam nếu có
    adb.tap_by_selector(resource_id="close-button")
    time.sleep(0.5)
    cal_elems = capture_screen(adb, "calendar_home", out_dir)
    registry["calendar_home"] = {
        "title": "Calendar Main Home",
        "feature": "job",
        "elements": cal_elems
    }
    print(f"  • [Calendar Home]: {len(cal_elems)} selectors.")

    # 3. Mở Drawer Menu
    print("\n[Crawler] Đang mở [Drawer Menu]...")
    adb.tap_by_selector(resource_id="highlight-button", index=0)
    time.sleep(1.2)
    drawer_elems = capture_screen(adb, "drawer_menu", out_dir)
    registry["drawer_menu"] = {
        "title": "Navigation Drawer Menu",
        "feature": "global",
        "elements": drawer_elems
    }
    print(f"  • [Drawer Menu]: {len(drawer_elems)} selectors.")

    # 4. Vào Customers List
    print("\n[Crawler] Đang vào [Customers List]...")
    adb.tap_by_selector(content_desc="Customers")
    time.sleep(1.5)
    cus_list_elems = capture_screen(adb, "customers_list", out_dir)
    registry["customers_list"] = {
        "title": "Customers List",
        "feature": "customers",
        "elements": cus_list_elems
    }
    print(f"  • [Customers List]: {len(cus_list_elems)} selectors.")

    # 5. Mở New Customer Form
    print("\n[Crawler] Đang mở [New Customer Form]...")
    adb.tap_by_selector(resource_id="highlight-button", index=-1)
    time.sleep(1.5)
    new_cus_elems = capture_screen(adb, "customer_new", out_dir)
    registry["customer_new"] = {
        "title": "New Customer Form",
        "feature": "customers",
        "elements": new_cus_elems
    }
    print(f"  • [New Customer Form]: {len(new_cus_elems)} selectors.")

    # 6. Mở Service Address Modal
    print("\n[Crawler] Đang mở [Service Address Modal]...")
    adb.tap_by_selector(content_desc="Service Address")
    time.sleep(1.2)
    addr_elems = capture_screen(adb, "service_address_modal", out_dir)
    registry["service_address_modal"] = {
        "title": "Service Address Bottom Sheet",
        "feature": "customers",
        "elements": addr_elems
    }
    print(f"  • [Service Address Modal]: {len(addr_elems)} selectors.")

    # Đóng modal address
    adb.keyevent(4)
    time.sleep(0.5)
    # Thoát New Customer Form về Customers list
    adb.keyevent(4)
    time.sleep(0.8)

    # 7. Mở Drawer -> Invoices
    print("\n[Crawler] Đang mở Drawer và vào [Invoices List]...")
    adb.tap_by_selector(resource_id="highlight-button", index=0)
    time.sleep(1.0)
    adb.tap_by_selector(content_desc="Invoices")
    time.sleep(1.5)
    inv_list_elems = capture_screen(adb, "invoices_list", out_dir)
    registry["invoices_list"] = {
        "title": "Invoices List",
        "feature": "invoice",
        "elements": inv_list_elems
    }
    print(f"  • [Invoices List]: {len(inv_list_elems)} selectors.")

    # 8. Mở Drawer -> Estimates
    print("\n[Crawler] Đang mở Drawer và vào [Estimates List]...")
    adb.tap_by_selector(resource_id="highlight-button", index=0)
    time.sleep(1.0)
    adb.tap_by_selector(content_desc="Estimates")
    time.sleep(1.5)
    est_list_elems = capture_screen(adb, "estimates_list", out_dir)
    registry["estimates_list"] = {
        "title": "Estimates List",
        "feature": "estimate",
        "elements": est_list_elems
    }
    print(f"  • [Estimates List]: {len(est_list_elems)} selectors.")

    # 9. Quay về Calendar Home và mở New Job Form
    print("\n[Crawler] Đang quay về Calendar và mở [New Job Sheet]...")
    adb.tap_by_selector(resource_id="highlight-button", index=0)
    time.sleep(1.0)
    adb.tap_by_selector(content_desc="Calendar")
    time.sleep(1.5)
    # Bấm FAB (+) để mở Action Sheet
    adb.tap_by_selector(resource_id="OutlinePlus", index=0)
    time.sleep(1.0)
    action_sheet_elems = capture_screen(adb, "calendar_action_sheet", out_dir)
    registry["calendar_action_sheet"] = {
        "title": "Calendar Action Sheet (+)",
        "feature": "job",
        "elements": action_sheet_elems
    }
    print(f"  • [Calendar Action Sheet]: {len(action_sheet_elems)} selectors.")

    # Bấm New Job
    adb.tap_by_selector(text="New Job")
    time.sleep(2.0)
    new_job_elems = capture_screen(adb, "job_new", out_dir)
    registry["job_new"] = {
        "title": "New Job Screen",
        "feature": "job",
        "elements": new_job_elems
    }
    print(f"  • [New Job Form]: {len(new_job_elems)} selectors.")

    # Đóng New Job
    adb.keyevent(4)
    time.sleep(1.0)

    # Lưu lại toàn bộ Registry
    with open(registry_file, 'w', encoding='utf-8') as f:
        yaml.dump(registry, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"\n=======================================================")
    print(f"✅ THÀNH CÔNG! Đã bóc tách {len(registry)} màn hình lớn vào:")
    print(f"   {registry_file}")
    print(f"=======================================================")

if __name__ == "__main__":
    main()
