import subprocess
import os
import sys
import json
import re

AI_QA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class HermesJudge:
    def __init__(self, executable="hermes.exe"):
        self.executable = executable

    def evaluate(self, tc_id, prompt_md_path, timeout_sec=120):
        """
        Tự động gọi Agent Hermes (Judge) qua CLI để thẩm định độc lập kết quả test.
        """
        if not os.path.exists(prompt_md_path):
            return {
                "test_id": tc_id,
                "verdict": "ERROR",
                "summary": f"Không tìm thấy file prompt: {prompt_md_path}",
                "reasoning": "Thiếu dữ liệu đầu vào cho Judge",
                "defect_details": None
            }

        with open(prompt_md_path, "r", encoding="utf-8") as f:
            prompt_content = f.read()

        strict_prompt = prompt_content + "\n\nQUAN TRỌNG: Hãy trả về CHỈ DUY NHẤT một khối JSON hợp lệ theo đúng schema trên, không kèm lời mở đầu hay kết luận ngoài JSON."

        print(f"  🤖 Đang chuyển giao hồ sơ sang Agent Hermes để thẩm định độc lập...")
        try:
            res = subprocess.run(
                [self.executable, "-z", strict_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout_sec
            )
            raw_output = res.stdout.strip()
            
            # Trích xuất JSON từ output của Hermes
            json_match = re.search(r'\{[\s\S]*\}', raw_output)
            parsed = None
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                except Exception:
                    pass

            verdict_label = parsed.get("verdict", "DONE") if parsed else "DONE"

            # Tự động gán tên cuộc hội thoại để hiển thị đẹp mắt trong Hermes Desktop App
            try:
                list_res = subprocess.run([self.executable, "sessions", "list"], capture_output=True, text=True, encoding="utf-8")
                lines = list_res.stdout.splitlines()
                if len(lines) >= 3:
                    parts = lines[2].split()
                    if parts:
                        latest_id = parts[-1]
                        subprocess.run([self.executable, "sessions", "rename", latest_id, f"[QA Audit] {tc_id} ({verdict_label})"], capture_output=True)
            except Exception:
                pass

            if parsed:
                return parsed
            else:
                return {
                    "test_id": tc_id,
                    "verdict": "UNCERTAIN",
                    "summary": "Hermes phản hồi nhưng không khớp định dạng JSON",
                    "reasoning": raw_output[:300],
                    "defect_details": None
                }
        except subprocess.TimeoutExpired:
            return {
                "test_id": tc_id,
                "verdict": "TIMEOUT",
                "summary": "Hermes xử lý quá thời gian quy định",
                "reasoning": f"Timeout sau {timeout_sec}s",
                "defect_details": None
            }
        except Exception as e:
            return {
                "test_id": tc_id,
                "verdict": "ERROR",
                "summary": f"Lỗi khi gọi Hermes: {str(e)}",
                "reasoning": str(e),
                "defect_details": None
            }
