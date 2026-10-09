import subprocess
import time
import re
import os
import xml.etree.ElementTree as ET

DEFAULT_ADB = r"C:\Users\Admin\AppData\Local\Android\Sdk\platform-tools\adb.exe"

class ADBClient:
    def __init__(self, serial=None):
        self.adb_bin = DEFAULT_ADB if os.path.exists(DEFAULT_ADB) else "adb"
        self.serial = serial or self._detect_device()
        self.width, self.height = self.get_screen_size()

    def _detect_device(self):
        for _ in range(5):
            res = subprocess.run([self.adb_bin, "devices"], capture_output=True, text=True, check=True)
            lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    return parts[0]
            time.sleep(1.0)
        return "0B171FDD4005K3"

    def shell(self, cmd, timeout=10):
        full_cmd = [self.adb_bin, "-s", self.serial, "shell", cmd]
        try:
            res = subprocess.run(full_cmd, capture_output=True, text=True, check=True, timeout=timeout)
            return res.stdout
        except Exception:
            return ""

    def get_screen_size(self):
        try:
            out = self.shell("wm size")
            match = re.search(r'Physical size:\s*(\d+)x(\d+)', out)
            if match:
                return int(match.group(1)), int(match.group(2))
        except Exception:
            pass
        return 1080, 2340

    def tap_abs(self, x, y):
        self.shell(f"input tap {int(x)} {int(y)}")

    def tap_rel(self, pct_x, pct_y):
        real_x = int(self.width * (pct_x / 100.0))
        real_y = int(self.height * (pct_y / 100.0))
        self.tap_abs(real_x, real_y)
        return real_x, real_y

    def keyevent(self, code):
        self.shell(f"input keyevent {code}")

    def type_text(self, text):
        safe_text = str(text).replace(" ", "%s")
        self.shell(f"input text {safe_text}")

    def back(self):
        self.keyevent(4)

    def home(self):
        self.keyevent(3)

    def hide_keyboard(self):
        self.keyevent(111)

    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        self.shell(f"input swipe {int(x1)} {int(y1)} {int(x2)} {int(y2)} {duration_ms}")

    def ensure_app_open(self, package="com.gorilladesk.rn"):
        try:
            self.shell(f"am start -n {package}/.MainActivity")
            time.sleep(2.0)
        except Exception:
            pass

    def get_parsed_hierarchy(self):
        dump_xml = "runs/temp_verify_dump.xml"
        os.makedirs("runs", exist_ok=True)
        try:
            self.dump_hierarchy(dump_xml)
            if os.path.exists(dump_xml):
                return ET.parse(dump_xml)
        except Exception:
            pass
        return None

    def has_text(self, text, tree=None):
        try:
            if tree is None:
                tree = self.get_parsed_hierarchy()
            if tree:
                for node in tree.getroot().iter('node'):
                    n_text = node.get('text', '')
                    n_desc = node.get('content-desc', '')
                    if text.lower() in n_text.lower() or text.lower() in n_desc.lower():
                        return True
        except Exception:
            pass
        return False

    def get_visible_texts(self, max_items=60, tree=None):
        texts = []
        try:
            if tree is None:
                tree = self.get_parsed_hierarchy()
            if tree:
                for node in tree.getroot().iter('node'):
                    t = (node.get('text') or '').strip()
                    d = (node.get('content-desc') or '').strip()
                    if t and t not in texts:
                        texts.append(t)
                    if d and d not in texts:
                        texts.append(d)
        except Exception:
            pass
        return texts[:max_items]

    def screencap(self, host_path):
        os.makedirs(os.path.dirname(host_path), exist_ok=True)
        try:
            with open(host_path, "wb") as f:
                subprocess.run([self.adb_bin, "-s", self.serial, "exec-out", "screencap", "-p"], stdout=f, check=True, timeout=5)
        except Exception:
            # Fallback nếu exec-out gặp lỗi
            device_tmp = "/sdcard/ai_qa_tmp.png"
            self.shell(f"screencap -p {device_tmp}")
            subprocess.run([self.adb_bin, "-s", self.serial, "pull", device_tmp, host_path], capture_output=True, check=True)

    def dump_hierarchy(self, host_path):
        os.makedirs(os.path.dirname(host_path), exist_ok=True)
        device_tmp = "/sdcard/ai_qa_dump.xml"
        try:
            self.shell(f"uiautomator dump {device_tmp}", timeout=3.5)
            subprocess.run([self.adb_bin, "-s", self.serial, "pull", device_tmp, host_path], capture_output=True, check=True, timeout=3)
        except Exception:
            pass

    # --- ĐỊNH DANH ĐỘNG: DYNAMIC-FIRST, COORDINATE-FALLBACK ---
    def find_element(self, text=None, content_desc=None, resource_id=None, index=0, tree=None):
        """
        Tìm kiếm vị trí tâm của element trên màn hình theo text, content-desc hoặc resource-id.
        Hỗ trợ index (0: phần tử đầu tiên, -1: phần tử cuối cùng) và nhận tree sẵn để tránh dump lặp lại.
        """
        dump_xml = "runs/temp_locator_dump.xml"
        try:
            if tree is None:
                self.dump_hierarchy(dump_xml)
                if not os.path.exists(dump_xml):
                    return None
                tree = ET.parse(dump_xml)

            matches = []
            for node in tree.getroot().iter('node'):
                n_text = node.get('text', '')
                n_desc = node.get('content-desc', '')
                n_id = node.get('resource-id', '')

                # Dynamic matching logic:
                match_text = True
                if text:
                    match_text = (text.lower() in n_text.lower()) or (text.lower() in n_desc.lower())

                match_desc = True
                if content_desc:
                    match_desc = (content_desc.lower() in n_desc.lower()) or (content_desc.lower() in n_text.lower())

                match_id = True
                if resource_id:
                    match_id = resource_id.lower() in n_id.lower()

                if text and content_desc:
                    text_or_desc = match_text or match_desc
                elif text:
                    text_or_desc = match_text
                elif content_desc:
                    text_or_desc = match_desc
                else:
                    text_or_desc = True

                is_match = text_or_desc and match_id

                if is_match and (text or content_desc or resource_id):
                    bounds = node.get('bounds', '')
                    m = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                    if m:
                        x1, y1, x2, y2 = map(int, m.groups())
                        if x2 > x1 and y2 > y1:
                            area = (x2 - x1) * (y2 - y1)
                            matches.append((area, (x1 + x2) // 2, (y1 + y2) // 2))

            if matches:
                # Prefer the tightest matching node. React Native accessibility
                # trees often expose both a card container and its text child;
                # taking the first match can tap the entire calendar grid.
                matches.sort(key=lambda item: item[0])
                idx = index if (0 <= index < len(matches)) else (len(matches) - 1 if index == -1 else 0)
                return matches[idx][1], matches[idx][2]
        except Exception:
            pass
        return None

    def tap_by_selector(self, text=None, content_desc=None, resource_id=None, index=0, fallback_rel=None, tree=None):
        """
        Ưu tiên bấm theo định danh động (Dynamic-first: text, desc, id).
        Nếu không tìm thấy hoặc đổi sang máy lạ thì dùng fallback tọa độ % (Coordinate-fallback).
        """
        target = self.find_element(text=text, content_desc=content_desc, resource_id=resource_id, index=index, tree=tree)
        if target:
            self.tap_abs(target[0], target[1])
            return target[0], target[1], "dynamic"
        elif fallback_rel:
            x, y = self.tap_rel(fallback_rel[0], fallback_rel[1])
            return x, y, "fallback_rel"
        return None, None, "not_found"

    def tap(self, text=None, content_desc=None, resource_id=None, index=0, fallback_rel=None, tree=None):
        """
        Thực hiện tap và trả về boolean (True nếu tap thành công, False nếu không tìm thấy).
        """
        x, y, method = self.tap_by_selector(text=text, content_desc=content_desc, resource_id=resource_id, index=index, fallback_rel=fallback_rel, tree=tree)
        return method != "not_found"

    # --- HỖ TRỢ OFFLINE MODE ---
    def set_wifi(self, enabled=True):
        state = "enable" if enabled else "disable"
        self.shell(f"svc wifi {state}")

    def set_data(self, enabled=True):
        state = "enable" if enabled else "disable"
        self.shell(f"svc data {state}")

    def set_airplane_mode(self, enabled=True):
        state = "1" if enabled else "0"
        self.shell(f"settings put global airplane_mode_on {state}")
        self.shell(f"am broadcast -a android.intent.action.AIRPLANE_MODE --ez state {'true' if enabled else 'false'}")

    def background_app(self, duration_sec=3.0, package="com.gorilladesk.rn"):
        """Đưa app xuống chế độ background (Home), chờ X giây rồi đưa app quay lại foreground"""
        self.keyevent(3) # KEYCODE_HOME
        time.sleep(duration_sec)
        self.shell(f"am start -n {package}/.MainActivity")
        time.sleep(1.5)

    def lock_screen(self, duration_sec=3.0, package="com.gorilladesk.rn"):
        """Khóa màn hình (Screen Off / Sleep), chờ X giây, mở màn hình lại và unlock về app"""
        self.keyevent(26) # KEYCODE_POWER (tắt màn hình)
        time.sleep(duration_sec)
        self.keyevent(224) # KEYCODE_WAKEUP (đánh thức màn hình)
        time.sleep(0.5)
        self.shell("input swipe 500 1800 500 500 200") # Vuốt mở khóa
        time.sleep(0.5)
        self.shell(f"am start -n {package}/.MainActivity")
        time.sleep(1.5)

    def simulate_weak_network(self, flaps=3, interval=1.0):
        """Mô phỏng mạng yếu / chập chờn / rớt gói bằng cơ chế network flapping"""
        for _ in range(flaps):
            self.set_wifi(False)
            time.sleep(interval)
            self.set_wifi(True)
            time.sleep(interval)

    # --- HỖ TRỢ QUAY VIDEO & TRÍCH XUẤT KEYFRAMES (CHỨNG CỨ SỐNG ĐỘNG) ---
    def start_recording(self, remote_path="/sdcard/ai_qa_run.mp4"):
        """Bật quay video màn hình thiết bị ngầm ở 60fps"""
        try:
            self.shell(f"rm -f {remote_path}")
            # Dùng subprocess.Popen để chạy nền screenrecord
            cmd = [self.adb_bin, "-s", self.serial, "shell", f"screenrecord --time-limit 180 {remote_path}"]
            self.record_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._record_remote_path = remote_path
            time.sleep(0.5) # chờ 0.5s để screenrecord khởi động
            return True
        except Exception as e:
            print(f"  ⚠️ Không thể bật quay video: {e}")
            return False

    def stop_recording(self, local_path="runs/videos/test.mp4"):
        """Dừng quay video, đồng bộ moov atom và kéo file mp4 về máy host"""
        remote_path = getattr(self, "_record_remote_path", "/sdcard/ai_qa_run.mp4")
        try:
            # Gửi SIGINT (signal 2) đến tiến trình screenrecord trên Android để đóng chuẩn MP4 header
            self.shell("pkill -2 screenrecord || killall -2 screenrecord")
            if hasattr(self, "record_proc") and self.record_proc:
                try:
                    self.record_proc.wait(timeout=3)
                except Exception:
                    self.record_proc.terminate()
            time.sleep(1.2) # Chờ thiết bị hoàn tất ghi moov atom

            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            pull_res = subprocess.run([self.adb_bin, "-s", self.serial, "pull", remote_path, local_path], capture_output=True, text=True)
            self.shell(f"rm -f {remote_path}")
            if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
                return local_path
        except Exception as e:
            print(f"  ⚠️ Lỗi khi lấy video: {e}")
        return None

    def extract_keyframes(self, video_path, output_dir, tc_id, max_frames=5):
        """Dùng ffmpeg trích xuất các khung hình then chốt (keyframes) từ video mp4"""
        if not video_path or not os.path.exists(video_path):
            return []
        os.makedirs(output_dir, exist_ok=True)
        keyframe_paths = []
        try:
            # Lấy thông tin duration của video qua ffprobe
            probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
            dur_res = subprocess.run(probe_cmd, capture_output=True, text=True)
            duration = float(dur_res.stdout.strip()) if dur_res.stdout.strip() else 3.0

            # Tính 5 mốc thời gian trải đều theo toàn bộ tiến trình test
            if duration <= 5.0:
                timestamps = [1.0, max(1.5, duration - 0.5)]
            else:
                timestamps = [
                    1.0,
                    round(duration * 0.25, 1),
                    round(duration * 0.50, 1),
                    round(duration * 0.75, 1),
                    round(duration - 1.0, 1)
                ]
            # Loại trùng
            timestamps = sorted(list(set(timestamps)))

            for i, ts in enumerate(timestamps):
                out_img = os.path.join(output_dir, f"{tc_id}_keyframe_{i+1}.png")
                cmd = ["ffmpeg", "-y", "-ss", str(ts), "-i", video_path, "-vframes", "1", "-q:v", "2", out_img]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if os.path.exists(out_img) and os.path.getsize(out_img) > 1024:
                    keyframe_paths.append(out_img)
        except Exception as e:
            print(f"  ⚠️ Lỗi trích xuất keyframes: {e}")
        return keyframe_paths
