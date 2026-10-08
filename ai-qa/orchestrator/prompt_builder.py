import os

class PromptBuilder:
    def __init__(self, prompts_dir="d:/artemis/ai-qa/prompts"):
        self.prompts_dir = prompts_dir

    def load_prompt_template(self, template_name):
        path = os.path.join(self.prompts_dir, f"{template_name}.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def build_test_prompt(self, testcase_data, feature_context=""):
        base_prompt = self.load_prompt_template("artemis-pro")
        tc_id = testcase_data.get("id", "")
        tc_title = testcase_data.get("title", "")
        steps = testcase_data.get("steps", [])
        expected = testcase_data.get("expected", [])

        steps_str = "\n".join([f"- Bước {i+1}: {s.get('desc', '')}" for i, s in enumerate(steps)])
        expected_str = "\n".join([f"- {e}" for e in expected])

        prompt = f"""{base_prompt}

## Nhiệm Vụ Kiểm Thử Hiện Tại: [{tc_id}] {tc_title}

### 1. Ngữ cảnh tính năng:
{feature_context}

### 2. Các bước cần thực thi:
{steps_str}

### 3. Kết quả mong đợi (Assertions):
{expected_str}
"""
        return prompt
