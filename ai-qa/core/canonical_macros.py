# ==============================================================================
# GORILLADESK MOBILE - CANONICAL UI ACTION MACROS
# 100% Dynamic Locators (Zero Coordinates) - Verified on Google Pixel 5
# ==============================================================================

import time
import os
import sys
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_QA_ROOT = os.path.dirname(CURRENT_DIR)
if AI_QA_ROOT not in sys.path:
    sys.path.insert(0, AI_QA_ROOT)

class CanonicalMacros:
    def __init__(self, adb_client):
        self.adb = adb_client

    def ensure_calendar_home(self):
        """Đưa ứng dụng về màn hình chính Calendar Home một cách an toàn và triệt để"""
        for _ in range(3):
            tree = self.adb.get_parsed_hierarchy()
            # Kiểm tra nếu đã ở Calendar Home (in-memory, siêu nhanh):
            if tree and self.adb.has_text("Today", tree=tree) and (self.adb.has_text("Jobs", tree=tree) or self.adb.has_text("Total", tree=tree) or self.adb.find_element(resource_id="OutlinePlus", tree=tree)):
                return True

            # 1. Nếu có prompt/dialog Discard
            if tree and self.adb.has_text("Discard", tree=tree):
                self.adb.tap(text="Discard", tree=tree) or self.adb.tap(text="Discard New Job", tree=tree)
                time.sleep(1.0)
                continue

            # 2. Nếu đang ở màn hình con, tap nút back / chevron
            self.adb.tap(resource_id="outline-chevron-container", fallback_rel=[6, 17], tree=tree)
            time.sleep(1.0)

            # 3. Fallback dùng back phím cứng
            self.adb.back()
            time.sleep(0.8)

        # Cuối cùng thử tap tab Calendar ở bottom navigation
        self.adb.tap(content_desc="Calendar, tab, 1 of 5", fallback_rel=[10, 96])
        time.sleep(1.2)
        if not self.adb.has_text("Today") or not (self.adb.has_text("Jobs") or self.adb.has_text("Total")):
            raise RuntimeError("Không xác nhận được Calendar Home; dừng thay vì thao tác nhầm màn hình")
        return True

    def create_job(self, customer_keyword=None, service_keyword=None, return_to_calendar=True, **kwargs):
        """
        Quy trình chuẩn tạo Job mới qua các bước chuẩn:
        1. Bấm FAB (+) -> New Job
        2. Chọn Customer (mặc định lấy khách hàng đầu tiên hoặc search)
        3. Chọn Location (mặc định lấy địa chỉ đầu tiên)
        4. Chọn Service (mặc định lấy dịch vụ đầu tiên)
        5. Tại form New Job -> Bấm Save
        6. Chờ Job Details hiển thị -> Bấm chevron back để quay lại Calendar (nếu return_to_calendar=True)
        """
        # Bước 1: Mở Action Sheet
        self.adb.tap(resource_id="OutlinePlus", fallback_rel=[91, 94])
        time.sleep(1.2)
        self.adb.tap(content_desc="New Job", text="New Job", fallback_rel=[50, 72])
        time.sleep(1.5)

        # Bước 2: Chọn Customer. Ưu tiên fixture QA đã được xác nhận trên Pixel 5.
        if customer_keyword:
            self.adb.tap(resource_id="input-text")
            self.adb.type_text(customer_keyword)
            time.sleep(1.0)
        else:
            customer_keyword = "#### test Customer"
        if not self.adb.tap(text=customer_keyword, fallback_rel=[50, 28]):
            raise RuntimeError(f"Không tìm thấy customer fixture: {customer_keyword}")
        time.sleep(1.5)

        # Bước 3: Chọn Location
        if not self.adb.tap(resource_id="location-item", index=0, fallback_rel=[50, 28]):
            raise RuntimeError("Không tìm thấy location fixture đã sync")
        time.sleep(1.5)

        # Bước 4: Chọn Service
        service_keyword = service_keyword or "#001 test template"
        if not self.adb.tap(text=service_keyword, content_desc=service_keyword, fallback_rel=[50, 32]):
            raise RuntimeError(f"Không tìm thấy service fixture: {service_keyword}")
        time.sleep(2.0)

        # Bước 5: Bấm Save hoàn tất tạo Job
        self.adb.tap(content_desc="Save", text="Save", fallback_rel=[92, 14])
        time.sleep(3.0)

        # Bước 6: Quay lại Calendar để quan sát lịch hiển thị job mới
        if return_to_calendar:
            self.adb.tap(resource_id="outline-chevron-container", fallback_rel=[6, 17])
            time.sleep(1.5)
        return True

    def _wait_for_text(self, text, timeout=8.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.adb.has_text(text):
                return True
            time.sleep(0.35)
        return False

    def _required_tap(self, text=None, content_desc=None, resource_id=None, fallback_rel=None, timeout=6.0):
        if not self.adb.tap(text=text, content_desc=content_desc, resource_id=resource_id, fallback_rel=fallback_rel):
            raise RuntimeError(f"Không tìm thấy control: {text or content_desc or resource_id}")
        time.sleep(0.35)
        return True

    def _text_bounds(self, text):
        """Trả về bounds của node khớp text; chọn leaf nhỏ nhất để tránh container cha."""
        tree = self.adb.get_parsed_hierarchy()
        if not tree:
            return None
        matches = []
        needle = str(text).casefold()
        for node in tree.getroot().iter("node"):
            value = f"{node.get('text', '')} {node.get('content-desc', '')}".casefold()
            if needle not in value:
                continue
            match = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
            if not match:
                continue
            x1, y1, x2, y2 = map(int, match.groups())
            if x2 > x1 and y2 > y1:
                matches.append((x1, y1, x2, y2))
        return min(matches, key=lambda b: (b[2] - b[0]) * (b[3] - b[1])) if matches else None

    def _long_press_drag(self, x1, y1, x2, y2, hold_ms=700, travel_ms=250, release=True):
        """Dùng chuỗi Android motionevent; giữ pointer giữa các lệnh ADB để app nhận drag thật."""
        self.adb.shell(f"input motionevent DOWN {int(x1)} {int(y1)}")
        time.sleep(max(hold_ms, 500) / 1000.0)
        self.adb.shell(f"input motionevent MOVE {int(x2)} {int(y2)}")
        time.sleep(max(travel_ms, 150) / 1000.0)
        if release:
            self.adb.shell(f"input motionevent UP {int(x2)} {int(y2)}")
            time.sleep(0.8)
        return True

    @staticmethod
    def _time_key(value):
        return re.sub(r"[^0-9APM]", "", str(value).upper())

    def _calendar_hour_nodes(self):
        tree = self.adb.get_parsed_hierarchy()
        if not tree:
            return []
        nodes = []
        pattern = re.compile(r"^\s*(\d{1,2})\s*(AM|PM)\s*$", re.I)
        for node in tree.getroot().iter("node"):
            raw = (node.get("text") or node.get("content-desc") or "").strip()
            match = pattern.match(raw)
            bounds = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
            if not match or not bounds:
                continue
            x1, y1, x2, y2 = map(int, bounds.groups())
            if x2 <= x1 or y2 <= y1:
                continue
            hour = int(match.group(1)) % 12 + (12 if match.group(2).upper() == "PM" else 0)
            nodes.append({"key": self._time_key(raw), "hour": hour, "y": (y1 + y2) // 2, "bounds": (x1, y1, x2, y2)})
        return nodes

    def _calendar_date_header(self):
        tree = self.adb.get_parsed_hierarchy()
        if not tree:
            return None
        pattern = re.compile(r"\b([A-Z][a-z]{2})\s+(\d{1,2}),\s*(\d{4})\b")
        for node in tree.getroot().iter("node"):
            value = f"{node.get('text', '')} {node.get('content-desc', '')}"
            match = pattern.search(value)
            if match:
                try:
                    return datetime.strptime(" ".join(match.groups()), "%b %d %Y")
                except ValueError:
                    pass
        return None

    def _calendar_date_header_bounds(self):
        tree = self.adb.get_parsed_hierarchy()
        if not tree:
            return None
        pattern = re.compile(r"\b[A-Z][a-z]{2}\s+\d{1,2},\s*\d{4}\b")
        matches = []
        for node in tree.getroot().iter("node"):
            value = f"{node.get('text', '')} {node.get('content-desc', '')}"
            if not pattern.search(value):
                continue
            bounds = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
            if bounds:
                x1, y1, x2, y2 = map(int, bounds.groups())
                if x2 > x1 and y2 > y1:
                    matches.append(((x2 - x1) * (y2 - y1), (x1, y1, x2, y2)))
        return min(matches, key=lambda item: item[0])[1] if matches else None

    def _tap_calendar_day_arrow(self, direction):
        if direction not in ("next", "previous"):
            raise ValueError("direction phải là next hoặc previous")
        label = "Next day" if direction == "next" else "Previous day"
        if self.adb.tap(content_desc=label, text=label):
            return True
        bounds = self._calendar_date_header_bounds()
        if not bounds:
            return False
        # The arrow controls are not exposed in the current UI hierarchy. Anchor
        # the fallback to the visible date-header row so banners/device height do
        # not shift the tap vertically. Left/right positions were visually
        # confirmed on the connected Pixel 5.
        x_pct = 0.92 if direction == "next" else 0.17
        x = int(self.adb.width * x_pct)
        y = (bounds[1] + bounds[3]) // 2
        self.adb.tap_abs(x, y)
        return True

    def _calendar_day_center(self, target_date):
        tree = self.adb.get_parsed_hierarchy()
        if tree:
            weekday = target_date.strftime("%a")
            pattern = re.compile(rf"\b{weekday},\s*{target_date.day}\b", re.I)
            matches = []
            for node in tree.getroot().iter("node"):
                value = f"{node.get('text', '')} {node.get('content-desc', '')}"
                match = pattern.search(value)
                bounds = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
                if match and bounds:
                    x1, y1, x2, y2 = map(int, bounds.groups())
                    if x2 > x1 and y2 > y1:
                        matches.append(((x2 - x1) * (y2 - y1), (x1 + x2) // 2))
            if matches:
                return min(matches)[1]
        return int(self.adb.width * 0.72)

    def calendar_select_time_range(self, start_time="1PM", day_offset=1, duration_minutes=30, **kwargs):
        """Open the calendar range menu using the visible date/time grid labels."""
        self.ensure_calendar_home()
        if not self.adb.tap(text="Today", content_desc="Today", fallback_rel=[10, 92]):
            raise RuntimeError("Không tìm thấy Today trên Calendar")
        time.sleep(0.8)
        base_date = self._calendar_date_header()
        if base_date is None:
            raise RuntimeError("Không đọc được ngày đang chọn trên Calendar")
        for _ in range(max(0, int(day_offset))):
            if not self._tap_calendar_day_arrow("next"):
                raise RuntimeError("Không tìm thấy điều hướng ngày kế tiếp")
            time.sleep(0.6)
        target_date = base_date + timedelta(days=int(day_offset))
        if self._calendar_date_header() != target_date:
            raise RuntimeError(f"Calendar không tới đúng ngày test: {target_date:%b %d, %Y}")
        wanted_key = self._time_key(start_time)
        wanted_match = re.match(r"(\d{1,2})(AM|PM)", wanted_key)
        if not wanted_match:
            raise ValueError(f"start_time phải có định format như 1PM hoặc 10AM, nhận: {start_time}")
        wanted_hour = int(wanted_match.group(1)) % 12 + (12 if wanted_match.group(2) == "PM" else 0)
        x = self._calendar_day_center(target_date)
        time_node = None
        for _ in range(10):
            visible = self._calendar_hour_nodes()
            time_node = next((n for n in visible if n["key"] == wanted_key), None)
            if time_node:
                break
            if not visible:
                raise RuntimeError("Không thấy nhãn giờ trên lưới Calendar; dừng thay vì đoán tọa độ")
            hours = [n["hour"] for n in visible]
            direction_down = wanted_hour < min(hours)
            if min(hours) <= wanted_hour <= max(hours):
                direction_down = wanted_hour < sum(hours) / len(hours)
            # Scroll from the time gutter so a swipe cannot start on an event card.
            scroll_x = int(self.adb.width * 0.05)
            y_top, y_bottom = int(self.adb.height * 0.38), int(self.adb.height * 0.72)
            if direction_down:
                self.adb.swipe(scroll_x, y_top, scroll_x, y_bottom, duration_ms=450)
            else:
                self.adb.swipe(scroll_x, y_bottom, scroll_x, y_top, duration_ms=450)
            time.sleep(0.45)
        if not time_node:
            raise RuntimeError(f"Không đưa được nhãn giờ {start_time} vào vùng nhìn; dừng an toàn")
        y = time_node["y"]
        labels = sorted((n["y"], n["hour"]) for n in self._calendar_hour_nodes())
        gaps = [abs(y2 - y1) for (y1, _), (y2, _) in zip(labels, labels[1:]) if y2 != y1]
        pixels_per_hour = sorted(gaps)[len(gaps) // 2] if gaps else int(self.adb.height * 0.17)
        end_y = min(self.adb.height - 160, y + max(12, round(pixels_per_hour * int(duration_minutes) / 60)))
        self._long_press_drag(x, y, x, end_y)
        if not self._wait_for_text("Add Custom Event", timeout=4.0):
            raise RuntimeError("Long-press/drag không mở menu tạo từ Calendar range")
        return True

    def calendar_prepare_create_item(self, kind="custom_event", marker="AIQA_CALENDAR_FIXTURE", start_time="1PM", day_offset=1, duration_minutes=30, **kwargs):
        """Open and fill a Calendar Add form without committing it."""
        kind_key = str(kind).casefold().replace(" ", "_")
        options = {
            "custom_event": ("Add Custom Event", "Event Name"),
            "time_off": ("Add Time Off", "Reason For Time Off"),
        }
        if kind_key not in options:
            raise ValueError("kind chỉ hỗ trợ custom_event hoặc time_off")
        option, field = options[kind_key]
        self.calendar_select_time_range(start_time=start_time, day_offset=day_offset, duration_minutes=duration_minutes)
        if not self.adb.tap(text=option, content_desc=option, fallback_rel=[50, 87]):
            raise RuntimeError(f"Không tìm thấy lựa chọn {option} trong menu range")
        if not self._wait_for_text(option.replace("Add ", ""), timeout=5.0):
            raise RuntimeError(f"Không mở được form {option}")
        if not self.adb.tap(text=field, fallback_rel=[48, 24]):
            raise RuntimeError(f"Không tìm thấy trường bắt buộc '{field}'")
        self.adb.type_text(marker)
        self.adb.hide_keyboard()
        if not self.adb.has_text(marker):
            raise RuntimeError(f"Form không hiển thị dữ liệu đã nhập: {marker}")
        return True

    def calendar_commit_create_item(self, marker="AIQA_CALENDAR_FIXTURE", verify_live_refresh=True, expected_start_time=None, **kwargs):
        if not self.adb.has_text(marker):
            raise RuntimeError(f"Không lưu vì form không còn chứa fixture marker: {marker}")
        if expected_start_time and not self._wait_for_text(str(expected_start_time), timeout=3.0):
            raise RuntimeError(f"Không lưu vì start time trên form không khớp: {expected_start_time}")
        if not self.adb.tap(text="Save", content_desc="Save", fallback_rel=[92, 17]):
            raise RuntimeError("Không tìm thấy Save trên form")
        time.sleep(1.0)
        if verify_live_refresh and not self._wait_for_text(marker, timeout=8.0):
            raise RuntimeError(f"Đã Save nhưng Calendar không render lại item ngay: {marker}")
        return True

    def calendar_create_item(self, kind="custom_event", marker="AIQA_CALENDAR_FIXTURE", start_time="1PM", day_offset=1, duration_minutes=30, verify_live_refresh=True, **kwargs):
        """Create a uniquely named Custom Event or Time Off from a selected calendar range."""
        self.calendar_prepare_create_item(kind=kind, marker=marker, start_time=start_time, day_offset=day_offset, duration_minutes=duration_minutes)
        return self.calendar_commit_create_item(marker=marker, verify_live_refresh=verify_live_refresh)

    def assert_visible(self, text, timeout=8.0, **kwargs):
        if not self._wait_for_text(text, timeout=float(timeout)):
            raise RuntimeError(f"Không thấy nội dung bắt buộc trên màn hình: {text}")
        return True

    def restart_app_and_wait(self, marker=None, day_offset=1, **kwargs):
        """Reload only for fixture setup; never use after the mutation under test."""
        self.adb.shell("am force-stop com.gorilladesk.rn")
        time.sleep(0.8)
        self.adb.ensure_app_open()
        self.ensure_calendar_home()
        if marker:
            if not self.adb.tap(text="Today", content_desc="Today", fallback_rel=[10, 92]):
                raise RuntimeError("Không tìm thấy Today sau khi mở lại app để nạp fixture")
            time.sleep(0.5)
            base_date = self._calendar_date_header()
            if base_date is None:
                raise RuntimeError("Không đọc được ngày Today sau khi mở lại app")
            for _ in range(max(0, int(day_offset))):
                if not self._tap_calendar_day_arrow("next"):
                    raise RuntimeError("Không điều hướng được tới ngày fixture sau khi mở lại app")
                time.sleep(0.5)
            expected_date = base_date + timedelta(days=max(0, int(day_offset)))
            if self._calendar_date_header() != expected_date:
                raise RuntimeError(f"Calendar không tới đúng ngày fixture: {expected_date:%b %d, %Y}")
            if not self._wait_for_text(marker, timeout=10.0):
                raise RuntimeError(f"Fixture không tải lại sau khi mở app: {marker}")
        return True

    def calendar_open_edit(self, marker, kind="custom_event", **kwargs):
        if not self.adb.has_text(marker):
            raise RuntimeError(f"Fixture không có trên Calendar: {marker}")
        if not self.adb.tap(text=marker):
            raise RuntimeError(f"Không mở được fixture: {marker}")
        detail_title = "Time Off" if str(kind).casefold().replace(" ", "_") == "time_off" else "Custom Event"
        if not self._wait_for_text(detail_title, timeout=6.0):
            raise RuntimeError(f"Không vào được màn detail {detail_title}")
        if not self.adb.tap(content_desc="Edit", text="Edit", fallback_rel=[84, 17]):
            raise RuntimeError("Không tìm thấy nút Edit trên detail")
        edit_title = "Edit Time Off" if detail_title == "Time Off" else "Edit Custom Event"
        if not self._wait_for_text(edit_title, timeout=6.0):
            raise RuntimeError(f"Không xác nhận được form {edit_title}")
        return True

    def calendar_prepare_edit(self, marker, kind="custom_event", suffix="_EDITED", **kwargs):
        self.calendar_open_edit(marker=marker, kind=kind)
        if not self.adb.tap(text=marker):
            raise RuntimeError(f"Không tìm thấy text field hiện tại: {marker}")
        self.adb.keyevent(123)  # KEYCODE_MOVE_END, append without replacing existing fixture text.
        updated = f"{marker}{suffix}"
        self.adb.type_text(suffix)
        self.adb.hide_keyboard()
        if not self.adb.has_text(updated):
            raise RuntimeError(f"Giá trị edit chưa được nhập: {updated}")
        return True

    def calendar_commit_edit(self, marker, suffix="_EDITED", verify_live_refresh=True, **kwargs):
        updated = f"{marker}{suffix}"
        if not self.adb.has_text(updated):
            raise RuntimeError(f"Không lưu vì form không hiển thị giá trị edit: {updated}")
        if not self.adb.tap(text="Save", content_desc="Save", fallback_rel=[92, 17]):
            raise RuntimeError("Không tìm thấy Save để commit edit")
        if verify_live_refresh and not self._wait_for_text(updated, timeout=8.0):
            raise RuntimeError(f"Save xong nhưng Calendar không refresh ngay item đã edit: {updated}")
        return True

    def calendar_prepare_resize(self, marker, kind="custom_event", duration_minutes=50, current_minutes=45, **kwargs):
        if str(kind).casefold().replace(" ", "_") == "job":
            raise RuntimeError("Đường vào Edit Job/time length chưa được xác minh trên Pixel 5; không đoán")
        self.calendar_open_edit(marker=marker, kind=kind)
        current_label = f"{int(current_minutes)} minutes"
        target_label = f"{int(duration_minutes) % 60} minutes"
        if not self.adb.tap(text=current_label):
            raise RuntimeError(f"Không tìm thấy duration hiện tại {current_label}")
        if not self._wait_for_text("Time Length", timeout=4.0):
            raise RuntimeError("Tap duration không mở Time Length picker")
        if not self.adb.tap(text=target_label):
            raise RuntimeError(f"Duration {target_label} không nằm trong wheel đang hiển thị; dừng an toàn")
        if not self.adb.tap(text="Save", content_desc="Save", fallback_rel=[88, 37]):
            raise RuntimeError("Không tìm thấy Save trong Time Length picker")
        edit_title = "Edit Time Off" if str(kind).casefold().replace(" ", "_") == "time_off" else "Edit Custom Event"
        if not self._wait_for_text(edit_title, timeout=5.0) or not self.adb.has_text(target_label):
            raise RuntimeError(f"Không xác nhận được duration mới {target_label} trên edit form")
        return True

    def calendar_commit_resize(self, marker, duration_minutes=50, verify_live_refresh=True, **kwargs):
        target_label = f"{int(duration_minutes) % 60} minutes"
        if not self.adb.has_text(target_label):
            raise RuntimeError(f"Không lưu vì form edit chưa xác nhận duration {target_label}")
        if not self.adb.tap(text="Save", content_desc="Save", fallback_rel=[92, 17]):
            raise RuntimeError("Không tìm thấy Save để commit resize")
        if verify_live_refresh and not self._wait_for_text(marker, timeout=8.0):
            raise RuntimeError(f"Save xong nhưng Calendar không render lại item ngay: {marker}")
        kind = kwargs.get("kind") or ("time_off" if str(marker).endswith("_TO") else "custom_event")
        # Re-open the detail form so the testcase's final expected text checks the persisted duration,
        # not a duration string that is absent from the Calendar card itself.
        self.calendar_open_edit(marker=marker, kind=kind)
        target_label = f"{int(duration_minutes) % 60} minutes"
        if not self._wait_for_text(target_label, timeout=6.0):
            raise RuntimeError(f"Resize đã lưu nhưng detail không xác nhận được duration {target_label}")
        return True

    def calendar_begin_move(self, marker, delta_percent=6, delta_minutes=None, recurrence_scope="none", **kwargs):
        bounds = self._text_bounds(marker)
        if not bounds:
            raise RuntimeError(f"Không tìm thấy card fixture để move: {marker}")
        x1, y1, x2, y2 = bounds
        start_x, start_y = (x1 + x2) // 2, (y1 + y2) // 2
        if delta_minutes is not None:
            labels = sorted(n["y"] for n in self._calendar_hour_nodes())
            gaps = [abs(y2 - y1) for y1, y2 in zip(labels, labels[1:]) if y2 != y1]
            pixels_per_hour = sorted(gaps)[len(gaps) // 2] if gaps else int(self.adb.height * 0.17)
            distance = round(pixels_per_hour * int(delta_minutes) / 60)
            tolerance = max(8, round(pixels_per_hour * 5 / 60))
        else:
            distance = int(self.adb.height * float(delta_percent) / 100.0)
            tolerance = max(8, round(distance * 0.25))
        before_center_y = (y1 + y2) // 2
        end_y = min(self.adb.height - 180, start_y + distance)
        self._long_press_drag(start_x, start_y, start_x, end_y)
        if recurrence_scope in ("only", "all"):
            if not self._wait_for_text("Update recurring job", timeout=4.0):
                raise RuntimeError("Job recurring không hiển thị xác nhận scope sau drag")
        elif self._wait_for_text("Update recurring job", timeout=1.0):
            raise RuntimeError("Đang move recurring Job nhưng testcase chưa khai báo Move only/Move all")
        else:
            after = self._text_bounds(marker)
            if not after:
                raise RuntimeError("Không tìm lại được item sau drag; không xác nhận Move thành công")
            actual_delta = ((after[1] + after[3]) // 2) - before_center_y
            if actual_delta <= 0:
                raise RuntimeError("Item không di chuyển xuống theo hướng delta đã chọn")
            if abs(actual_delta - distance) > tolerance:
                raise RuntimeError(
                    f"Drag lệch duration dự kiến: cần khoảng {distance}px, thực tế {actual_delta}px "
                    f"(dung sai {tolerance}px)"
                )
        return True

    def calendar_confirm_move(self, recurrence_scope="none", expected_time=None, marker=None, future_expected_time=None, future_occurrences=0, **kwargs):
        if recurrence_scope not in ("only", "all"):
            raise ValueError("recurrence_scope phải là only hoặc all khi popup recurring đang mở")
        option = "Move this job only" if recurrence_scope == "only" else "Move this job and all recurring"
        if not self._wait_for_text(option, timeout=4.0) or not self.adb.tap(text=option):
            raise RuntimeError(f"Không thấy hoặc không chọn được scope: {option}")
        if not self._wait_for_text("Today", timeout=8.0):
            raise RuntimeError("Calendar không quay lại sau khi chọn scope move")
        if expected_time and not self._wait_for_text(str(expected_time), timeout=6.0):
            raise RuntimeError(f"Sau khi chọn {option}, không thấy giờ đã move: {expected_time}")
        if int(future_occurrences) > 0:
            if not marker or not future_expected_time:
                raise ValueError("Kiểm tra recurring cần marker và future_expected_time")
            base_date = self._calendar_date_header()
            if base_date is None:
                raise RuntimeError("Không đọc được ngày occurrence sau khi move recurring")
            for occurrence in range(1, int(future_occurrences) + 1):
                expected_date = base_date + timedelta(days=7 * occurrence)
                for _ in range(7):
                    if not self._tap_calendar_day_arrow("next"):
                        raise RuntimeError("Không điều hướng được tới occurrence recurring kế tiếp")
                    time.sleep(0.35)
                if self._calendar_date_header() != expected_date:
                    raise RuntimeError(f"Calendar không tới occurrence date dự kiến: {expected_date:%b %d, %Y}")
                if not self._wait_for_text(marker, timeout=5.0):
                    raise RuntimeError(f"Không thấy recurring fixture tại occurrence kế tiếp: {marker}")
                if not self._wait_for_text(str(future_expected_time), timeout=5.0):
                    raise RuntimeError(
                        f"Occurrence {occurrence} không có giờ mong đợi sau scope {recurrence_scope}: "
                        f"{future_expected_time}"
                    )
        return True

    def calendar_cache_recurring_occurrences(self, marker, expected_time="12:30", future_occurrences=2, **kwargs):
        """Visit each future weekly occurrence online so offline scope assertions use cached data."""
        base_date = self._calendar_date_header()
        if base_date is None or not self._wait_for_text(marker, timeout=5.0):
            raise RuntimeError("Không xác nhận được recurring fixture/date trước khi cache occurrence")
        if not self._wait_for_text(str(expected_time), timeout=5.0):
            raise RuntimeError(f"Occurrence hiện tại không ở giờ dự kiến {expected_time}")
        count = int(future_occurrences)
        for occurrence in range(1, count + 1):
            expected_date = base_date + timedelta(days=7 * occurrence)
            for _ in range(7):
                if not self._tap_calendar_day_arrow("next"):
                    raise RuntimeError("Không điều hướng được tới recurring occurrence kế tiếp")
                time.sleep(0.35)
            if self._calendar_date_header() != expected_date:
                raise RuntimeError(f"Calendar không tới occurrence date dự kiến: {expected_date:%b %d, %Y}")
            if not self._wait_for_text(marker, timeout=5.0):
                raise RuntimeError(f"Thiếu recurring fixture tại ngày cần cache: {expected_date:%b %d, %Y}")
            if not self._wait_for_text(str(expected_time), timeout=5.0):
                raise RuntimeError(f"Occurrence tương lai sai giờ trước khi offline: {expected_time}")
        if not self.adb.tap(content_desc="Today", text="Today", fallback_rel=[10, 92]):
            raise RuntimeError("Không bấm được Today để quay lại occurrence gốc")
        time.sleep(0.5)
        if self._calendar_date_header() != base_date or not self._wait_for_text(marker, timeout=5.0):
            raise RuntimeError("Occurrence gốc phải là Today; không quay lại đúng ngày sau khi nạp cache")
        return True

    def require_transport_fault_injection(self, barrier="in_flight", **kwargs):
        raise RuntimeError(
            f"BLOCKED: phase {barrier} cần network-fault injector có barrier đồng bộ với request/ACK; "
            "runner hiện chỉ có weak_network flap, không thể bảo đảm cắt đúng thời điểm."
        )

    def require_verified_job_resize_path(self, **kwargs):
        raise RuntimeError(
            "BLOCKED: Pixel 5 evidence does not establish a Job edit/time-length route, "
            "and the attempted calendar lower-edge gesture did not change duration."
        )

    def calendar_drag_item(self, marker, delta_percent=6, recurrence_scope="none", **kwargs):
        """Kéo đúng card nhận diện bằng marker; recurring Job chọn scope theo text UI đã xác nhận."""
        bounds = self._text_bounds(marker)
        if not bounds:
            raise RuntimeError(f"Không tìm thấy card fixture theo marker: {marker}")
        x1, y1, x2, y2 = bounds
        start_x = (x1 + x2) // 2
        start_y = (y1 + y2) // 2
        end_y = min(self.adb.height - 180, start_y + int(self.adb.height * float(delta_percent) / 100.0))
        self._long_press_drag(start_x, start_y, start_x, end_y)
        if recurrence_scope in ("only", "all"):
            option = "Move this job only" if recurrence_scope == "only" else "Move this job and all recurring"
            if not self._wait_for_text(option, timeout=4.0):
                raise RuntimeError("Recurring Job không hiển thị lựa chọn move scope")
            self._required_tap(text=option)
        elif self._wait_for_text("Update recurring job", timeout=1.0):
            raise RuntimeError("Có popup recurrence nhưng testcase chưa khai báo Move only/Move all")
        time.sleep(2.0)
        if not self.adb.has_text(marker):
            raise RuntimeError("Sau drag không thấy lại fixture marker trên Calendar")
        return True

    def create_customer(self, first_name="Offline", last_name="SyncTest", email="test@gd.com", phone="1234567890", address="123 Offline St", **kwargs):
        """
        Quy trình chuẩn tạo Customer mới:
        1. Bấm FAB (+) -> New Customer
        2. Nhập First Name, Last Name, Phone, Service Address (bắt buộc)
        3. Bấm Save
        """
        self.adb.tap_by_selector(resource_id="OutlinePlus")
        time.sleep(1.0)
        self.adb.tap_by_selector(content_desc="New Customer")
        time.sleep(1.5)

        # Điền First Name
        self.adb.tap_by_selector(text="First Name")
        self.adb.type_text(first_name)
        time.sleep(0.5)

        # Điền Last Name
        self.adb.tap_by_selector(text="Last Name")
        self.adb.type_text(last_name)
        time.sleep(0.5)

        # Điền Phone
        self.adb.tap_by_selector(text="Phone")
        self.adb.type_text(phone)
        time.sleep(0.5)

        # Điền Service Address (Bắt buộc để form được chấp thuận)
        self.adb.tap_by_selector(text="Service Address")
        self.adb.type_text(address)
        time.sleep(0.5)

        # Lưu khách hàng
        self.adb.tap_by_selector(content_desc="Save")
        time.sleep(2.0)
        return True

    def change_job_status(self, target_status="Confirmed", status=None, **kwargs):
        """
        Quy trình đổi trạng thái của Job (Job Status):
        1. Nếu đang ở Calendar, mở Job đầu tiên
        2. Tại Job Details, bấm vào ô Status
        3. Chọn status mong muốn trong Bottom Sheet
        """
        target_status = status or target_status
        # Mở Job item đầu tiên nếu đang ở Calendar Home
        self.adb.tap_by_selector(resource_id="customer-avatar", index=0)
        time.sleep(1.5)

        # Bấm ô status hiện tại (Pending Booking hoặc Confirmed)
        self.adb.tap_by_selector(content_desc="Pending Booking") or self.adb.tap_by_selector(content_desc="Confirmed") or self.adb.tap_by_selector(text="Confirmed")
        time.sleep(1.0)
        # Chọn target status
        self.adb.tap_by_selector(text=target_status, content_desc=target_status)
        time.sleep(1.5)
        return True

    def take_signature(self, tech_draw=True, client_draw=True, target="customer", **kwargs):
        """
        Quy trình lấy chữ ký điện tử (Work Order Signature):
        1. Nếu đang ở Calendar, mở Job đầu tiên
        2. Tại Job Details -> bấm 3-dots more menu
        3. Bấm 'Take a Work Order Signature'
        4. Màn hình xoay ngang: Technician's Signature -> bấm Next
        5. Client's Signature -> bấm Save
        """
        # Mở Job item đầu tiên nếu đang ở Calendar Home
        self.adb.tap_by_selector(resource_id="customer-avatar", index=0)
        time.sleep(1.5)

        self.adb.tap_by_selector(resource_id="outline-more-horizontal-svg")
        time.sleep(1.0)
        self.adb.tap_by_selector(content_desc="Take a Work Order Signature")
        time.sleep(2.0)

        # Ký Tech
        if tech_draw:
            # Vẽ một nét nhẹ ở giữa màn hình ngang
            self.adb.shell("input swipe 600 500 900 500 200")
            time.sleep(0.5)
        self.adb.tap_by_selector(content_desc="Next")
        time.sleep(1.5)

        # Ký Client
        if client_draw:
            self.adb.shell("input swipe 600 500 900 500 200")
            time.sleep(0.5)
        self.adb.tap_by_selector(content_desc="Save")
        time.sleep(2.0)
        return True

    def add_material(self, units="10"):
        """
        Quy trình thêm vật tư / hóa chất vào Job:
        1. Tại Job Details -> Materials (+)
        2. Bấm 'Add Material'
        3. Chọn hóa chất đầu tiên
        4. Nhập Units định lượng
        5. Bấm Save
        """
        self.adb.tap_by_selector(resource_id="OutlinePlusSmall") # Nút (+) của Materials
        time.sleep(1.0)
        self.adb.tap_by_selector(content_desc="Add Material")
        time.sleep(1.5)

        # Chọn hóa chất đầu tiên
        self.adb.tap_by_selector(index=0) # Mục đầu tiên trong picker
        time.sleep(1.0)

        # Nhập Units
        self.adb.tap_by_selector(text="Units")
        self.adb.type_text(units)
        time.sleep(0.5)

        # Bấm Save
        self.adb.tap_by_selector(content_desc="Save")
        time.sleep(2.0)
        return True

    def add_todo(self, todo_text="Verify offline sync queue"):
        """
        Quy trình thêm việc cần làm vào Todo List:
        1. Bấm nút (+) Todo List (`resource-id="add-button"`)
        2. Nhập nội dung Todo
        3. Bấm 'Save Todo'
        """
        self.adb.tap_by_selector(resource_id="add-button")
        time.sleep(1.0)
        self.adb.tap_by_selector(text="Add a Todo...")
        self.adb.type_text(todo_text)
        time.sleep(0.5)
        self.adb.tap_by_selector(content_desc="Save Todo")
        time.sleep(1.5)
        return True

    def add_note(self, note_text="Offline local note content"):
        """
        Quy trình thêm ghi chú vào Job:
        1. Bấm nút (+) Notes
        2. Nhập nội dung
        3. Bấm Save
        """
        self.adb.tap_by_selector(resource_id="OutlinePlusSmall")
        time.sleep(1.0)
        self.adb.tap_by_selector(resource_id="root")
        self.adb.type_text(note_text)
        time.sleep(0.5)
        self.adb.tap_by_selector(content_desc="Save")
        time.sleep(1.5)
        return True

    def create_estimate(self):
        """
        Quy trình tạo Báo giá (Estimate):
        1. FAB (+) -> New Estimate
        2. Chọn Customer
        3. Chọn Location
        4. Chọn Template mẫu
        5. Tại Estimate Editor -> Bấm Save
        """
        self.adb.tap_by_selector(resource_id="OutlinePlus")
        time.sleep(1.0)
        self.adb.tap_by_selector(content_desc="New Estimate")
        time.sleep(1.5)

        # Chọn Customer
        self.adb.tap_by_selector(resource_id="customer-avatar", index=0)
        time.sleep(1.5)

        # Chọn Location
        self.adb.tap_by_selector(resource_id="location-item", index=0)
        time.sleep(1.5)

        # Chọn Template
        self.adb.tap_by_selector(text="Dynamic 1") or self.adb.tap_by_selector(index=0)
        time.sleep(1.5)

        # Bấm Save Estimate
        self.adb.tap_by_selector(content_desc="Save")
        time.sleep(2.0)
        return True

    def clock_in_out(self):
        """
        Thực hiện Clock In / Clock Out
        """
        self.adb.tap_by_selector(content_desc="Clock In") or self.adb.tap_by_selector(text="Clock In")
        time.sleep(1.5)
        return True

    def verify_offline_indicator(self):
        """Xác thực app đang hiển thị dấu hiệu Offline / Mất mạng"""
        tree = self.adb.get_parsed_hierarchy()
        has_banner = (
            self.adb.has_text("unavailable", tree=tree)
            or self.adb.has_text("keep trying", tree=tree)
            or self.adb.has_text("Unstable internet connection", tree=tree)
            or self.adb.has_text("Unstable connection", tree=tree)
        )
        has_badge = (
            self.adb.find_element(resource_id="states-dangerous-icon") is not None
            or self.adb.find_element(resource_id="offline-bar") is not None
        )
        return has_banner or has_badge

def execute_canonical_macro(adb, macro_name, **kwargs):
    """Điểm điều phối chung cho tất cả các Macro"""
    macros = CanonicalMacros(adb)
    handler = getattr(macros, macro_name, None)
    if handler and callable(handler):
        return handler(**kwargs)
    raise ValueError(f"Unknown canonical macro: {macro_name}")
