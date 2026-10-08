class RegressionDetector:
    """
    So sánh kết quả kiểm thử hiện tại với baseline lịch sử để phát hiện hồi quy.
    """
    def __init__(self, baseline_report=None):
        self.baseline = baseline_report or {}

    def check_regression(self, current_results):
        regressions = []
        for r in current_results:
            tc_id = r.get("id")
            status = r.get("status")
            baseline_status = self.baseline.get(tc_id, {}).get("status", "PASS")

            if status == "FAIL" and baseline_status == "PASS":
                regressions.append({
                    "id": tc_id,
                    "reason": "Test case từng PASS trong baseline nhưng hiện tại bị FAIL"
                })
        return {
            "has_regression": len(regressions) > 0,
            "regressions": regressions
        }
