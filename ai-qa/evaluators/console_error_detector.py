class ConsoleErrorDetector:
    def __init__(self, adb_client):
        self.adb = adb_client

    def scan_errors(self):
        try:
            out = self.adb.shell("logcat -d -s ReactNativeJS:E")
            return [line.strip() for line in out.splitlines() if "Error" in line]
        except Exception:
            return []
