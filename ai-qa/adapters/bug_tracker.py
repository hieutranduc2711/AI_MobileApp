import json
import os
import time

class BugTrackerAdapter:
    """
    Adapter quản lý và xuất báo cáo Bug linh hoạt (Local JSON/Markdown, GitHub, Jira, Mantis).
    """
    def __init__(self, provider="local", output_dir="reports/bugs"):
        self.provider = provider
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def file_bug(self, testcase_id, title, details, screenshot_path=None, logcat_snippet=None):
        bug_id = f"BUG-{testcase_id}-{int(time.time())}"
        bug_data = {
            "bug_id": bug_id,
            "testcase_id": testcase_id,
            "title": title,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "details": details,
            "screenshot": screenshot_path,
            "logcat": logcat_snippet
        }

        # Lưu file JSON
        json_file = os.path.join(self.output_dir, f"{bug_id}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(bug_data, f, ensure_ascii=False, indent=2)

        # Lưu file Markdown dễ đọc
        md_file = os.path.join(self.output_dir, f"{bug_id}.md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# [BUG] {title}\n\n")
            f.write(f"- **Bug ID:** `{bug_id}`\n")
            f.write(f"- **Test Case:** `{testcase_id}`\n")
            f.write(f"- **Phát hiện lúc:** {bug_data['timestamp']}\n\n")
            f.write(f"### Chi tiết lỗi:\n{details}\n\n")
            if screenshot_path:
                f.write(f"### Bằng chứng ảnh:\n`{screenshot_path}`\n\n")
            if logcat_snippet:
                f.write(f"### Logcat trích xuất:\n```\n{logcat_snippet}\n```\n")

        print(f"[BugTracker] Đã ghi nhận bug tại: {md_file}")
        return bug_id
