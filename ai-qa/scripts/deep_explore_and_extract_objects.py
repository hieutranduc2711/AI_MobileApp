import subprocess
import time
import re
import os
import xml.etree.ElementTree as ET
import yaml

DEVICE = "RFCY7018MSF"
AI_QA_DIR = r"D:\artemis\ai-qa"
OUT_REPO_FILE = os.path.join(AI_QA_DIR, "knowledge", "ELEMENT_REPOSITORY.yaml")
OUT_MAP_FILE = os.path.join(AI_QA_DIR, "knowledge", "SCOPE_COVERAGE_MAP.md")
TEMP_XML = os.path.join(AI_QA_DIR, "runs", "temp_hierarchy.xml")
TEMP_PNG = os.path.join(AI_QA_DIR, "runs", "temp_screen.png")

element_repo = {}
visited_screens = []

def adb_shell(cmd):
    full = ["adb", "-s", DEVICE, "shell", cmd]
    res = subprocess.run(full, capture_output=True, text=True)
    return res.stdout

def tap(x, y, delay=0.8):
    adb_shell(f"input tap {x} {y}")
    time.sleep(delay)

def back(delay=0.8):
    adb_shell("input keyevent 4")
    time.sleep(delay)

def dump_and_extract(screen_id, screen_name, module):
    print(f"\n[Explore] Dang trich xuat: [{module}] {screen_name} ({screen_id})...")
    # Screencap & dump
    adb_shell("screencap -p /sdcard/tmp_screen.png")
    subprocess.run(["adb", "-s", DEVICE, "pull", "/sdcard/tmp_screen.png", TEMP_PNG], capture_output=True)
    
    adb_shell("uiautomator dump /sdcard/tmp_dump.xml")
    subprocess.run(["adb", "-s", DEVICE, "pull", "/sdcard/tmp_dump.xml", TEMP_XML], capture_output=True)

    if not os.path.exists(TEMP_XML):
        print(f"  Khong the dump XML cho {screen_id}")
        return

    try:
        tree = ET.parse(TEMP_XML)
        root = tree.getroot()
    except Exception as e:
        print(f"  Loi parse XML: {e}")
        return

    elements = []
    for node in root.iter('node'):
        text = node.get('text', '').strip()
        cdesc = node.get('content-desc', '').strip()
        rid = node.get('resource-id', '').strip()
        bounds = node.get('bounds', '')
        clickable = node.get('clickable', 'false') == 'true'

        if text or cdesc or rid:
            # Parse bounds [x1,y1][x2,y2]
            match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
            center = None
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                center = [(x1 + x2) // 2, (y1 + y2) // 2]

            elements.append({
                "text": text if text else None,
                "content_desc": cdesc if cdesc else None,
                "resource_id": rid if rid else None,
                "clickable": clickable,
                "bounds": bounds,
                "center": center
            })

    # Loc bot cac element trung lap hoac qua nho
    unique_elements = []
    seen = set()
    for el in elements:
        key = (el['text'], el['content_desc'], el['resource_id'])
        if key not in seen:
            seen.add(key)
            unique_elements.append(el)

    element_repo[screen_id] = {
        "screen_name": screen_name,
        "module": module,
        "total_elements": len(unique_elements),
        "elements": unique_elements
    }

    visited_screens.append({
        "id": screen_id,
        "name": screen_name,
        "module": module,
        "element_count": len(unique_elements)
    })
    print(f"  -> Da tim thay {len(unique_elements)} elements.")

def main():
    print("=" * 65)
    print("BAT DAU CHIEN DICH KHAM PHA & TRICH XUAT TOAN BO SCOPES GORILLADESK")
    print("=" * 65)

    # 1. Calendar Home
    dump_and_extract("calendar_home", "Calendar Main Schedule", "home-calendar")

    # 2. Action Sheet (+)
    print("-> Mo Action Sheet (+)...")
    tap(996, 2217, delay=0.8)
    dump_and_extract("fab_action_sheet", "Quick Add Bottom Sheet", "home")
    back(delay=0.6)

    # 3. Drawer Menu
    print("-> Mo Drawer Menu...")
    tap(64, 175, delay=0.8)
    dump_and_extract("drawer_menu", "Main Navigation Drawer", "home")

    # 4. Customers Hub
    print("-> Vao Customers Hub...")
    tap(440, 695, delay=1.2)
    dump_and_extract("customers_hub", "Customers 360 Hub", "customer")

    # 5. Customer Profile
    print("-> Mo Customer Profile dau tien...")
    tap(540, 440, delay=1.5)
    dump_and_extract("customer_profile", "Customer Profile Details & Locations", "customer")
    back(delay=0.8)
    back(delay=0.8) # Ve lai Home

    # 6. Kong AI Assistant
    print("-> Mo Kong AI Assistant tu header...")
    tap(540, 175, delay=1.5) # Icon Kong o giua header
    dump_and_extract("kong_ai_assistant", "Kong AI Conversational Assistant", "ai-help-agent")
    tap(194, 185, delay=1.2) # Back to app button

    # 7. Form New Estimate
    print("-> Vao luong New Estimate...")
    tap(996, 2217, delay=0.8) # FAB
    tap(300, 2160, delay=1.0) # New Estimate
    dump_and_extract("estimate_customer_select", "Select Customer for Estimate", "estimate")
    tap(540, 440, delay=1.0) # Pick customer
    dump_and_extract("estimate_location_select", "Select Location for Estimate", "estimate")
    tap(540, 440, delay=1.0) # Pick location
    dump_and_extract("estimate_template_select", "Choose Estimate Template", "estimate")
    back(delay=0.6)
    back(delay=0.6)
    back(delay=0.6) # Ve lai Home

    # 8. Time Clocking
    print("-> Vao Time Clocking tu Drawer...")
    tap(64, 175, delay=0.8) # Drawer
    tap(335, 1088, delay=1.5) # Time Clocking
    dump_and_extract("time_clocking_hub", "Weekly Timesheet & Clock In/Out", "todo")
    back(delay=0.8)

    # 9. Settings
    print("-> Vao Settings tu Drawer...")
    tap(64, 175, delay=0.8) # Drawer
    tap(440, 1351, delay=1.5) # Settings
    dump_and_extract("settings_hub", "System Settings & Hardware Integration", "settings")
    back(delay=0.8)

    # 10. Dashboard
    print("-> Vao Dashboard tu Drawer...")
    tap(64, 175, delay=0.8) # Drawer
    tap(440, 826, delay=1.5) # Dashboard
    dump_and_extract("dashboard_hub", "KPI & Revenue Dashboard", "dashboard")
    back(delay=0.8)

    print("\n" + "=" * 65)
    print("XUAT DU LIEU ELEMENT REPOSITORY & SCOPE COVERAGE MAP...")
    print("=" * 65)

    # Ghi file YAML Element Repository
    os.makedirs(os.path.dirname(OUT_REPO_FILE), exist_ok=True)
    with open(OUT_REPO_FILE, "w", encoding="utf-8") as f:
        yaml.dump(element_repo, f, allow_unicode=True, sort_keys=False)
    print(f"File YAML Element Repository: {OUT_REPO_FILE}")

    # Ghi file Markdown Scope Coverage Map
    with open(OUT_MAP_FILE, "w", encoding="utf-8") as f:
        f.write("# BẢN ĐỒ PHẠM VI NGHIỆP VỤ & ĐỊNH DANH ĐỘNG (GORILLADESK SCOPE COVERAGE MAP)\n\n")
        f.write("> **Thiết bị khảo sát:** Samsung Galaxy A36 (`RFCY7018MSF`) - Android 15\n")
        f.write(f"> **Thời gian khảo sát:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> **Tổng số màn hình đã trích xuất:** {len(visited_screens)}\n\n")
        f.write("---\n\n")
        f.write("## 1. Danh Sách Màn Hình & Phân Hệ Đã Bóc Tách\n\n")
        f.write("| ID Màn hình | Tên Giao Diện | Phân Hệ (Module) | Số Elements Bóc Tách |\n")
        f.write("| :--- | :--- | :---: | :---: |\n")
        for s in visited_screens:
            f.write(f"| `{s['id']}` | **{s['name']}** | `{s['module']}` | **{s['element_count']}** elements |\n")

        f.write("\n---\n\n## 2. Chi Tiết Định Danh Động Từng Màn Hình (Object Repository)\n\n")
        for sid, sdata in element_repo.items():
            f.write(f"### Màn hình: `{sid}` — {sdata['screen_name']} (`{sdata['module']}`)\n\n")
            f.write("| Text hiển thị | Content-Desc (Khuyên dùng) | Resource-ID | Tọa độ tâm Fallback `(X, Y)` |\n")
            f.write("| :--- | :--- | :--- | :---: |\n")
            for el in sdata['elements'][:25]: # Lay top 25 elements quan trong
                txt = el['text'] or "-"
                cd = el['content_desc'] or "-"
                rid = el['resource_id'] or "-"
                center_str = f"({el['center'][0]}, {el['center'][1]})" if el['center'] else "-"
                f.write(f"| `{txt}` | `{cd}` | `{rid}` | `{center_str}` |\n")
            f.write("\n")

    print(f"File Markdown Scope Map: {OUT_MAP_FILE}")
    print("HOAN TAT CHIEN DICH KHAM PHA!")

if __name__ == "__main__":
    main()
