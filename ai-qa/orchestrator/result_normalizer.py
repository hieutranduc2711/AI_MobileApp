import json
import time
import os

class ResultNormalizer:
    def __init__(self, output_dir="d:/artemis/ai-qa/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_summary(self, results):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.output_dir, f"run_report_{timestamp}.json")
        total = len(results)
        passed = sum(1 for r in results if r["status"] == "PASS")
        failed = sum(1 for r in results if r["status"] == "FAIL")

        summary = {
            "timestamp": timestamp,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{round((passed / total) * 100, 1)}%" if total > 0 else "0%",
            "results": results
        }

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n[Orchestrator] Báo cáo đã xuất tại: {report_path}")
        return summary
