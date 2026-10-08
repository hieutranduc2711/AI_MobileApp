import subprocess

class CrashDetector:
    def __init__(self, adb_client, package_name="com.gorilladesk.rn"):
        self.adb = adb_client
        self.package = package_name

    def clear_logcat(self):
        try:
            self.adb.shell("logcat -c")
        except Exception:
            pass

    def check_for_crashes(self):
        """
        Kiểm tra logcat để tìm FATAL EXCEPTION hoặc ANR liên quan đến package.
        """
        try:
            out = self.adb.shell("logcat -d -v brief *:E")
            lines = out.splitlines()
            crashes = []
            for line in lines:
                if "FATAL EXCEPTION" in line or "ANR in " + self.package in line or "ReactNativeJS" in line and "Error" in line:
                    crashes.append(line.strip())
            return {
                "has_crash": len(crashes) > 0,
                "crash_lines": crashes[:10]
            }
        except Exception as e:
            return {"has_crash": False, "error": str(e)}
