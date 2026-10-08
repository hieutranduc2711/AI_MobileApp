import subprocess
import os
import sys
import json
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

AI_QA_ROOT = r"d:\artemis\ai-qa"
prompt_file = os.path.join(AI_QA_ROOT, "runs", "KONG-AI-001_FOR_HERMES.md")

with open(prompt_file, "r", encoding="utf-8") as f:
    prompt_text = f.read()

# Add instruction to return ONLY JSON
strict_prompt = prompt_text + "\n\nQUAN TRỌNG: Hãy trả về CHỈ DUY NHẤT một khối JSON hợp lệ theo đúng schema trên, không kèm lời mở đầu hay kết luận ngoài JSON."

print("=== ĐANG GỌI AGENT HERMES (JUDGE) ĐỂ TỰ ĐỘNG CHẤM ĐIỂM TESTCASE ===")
res = subprocess.run(["hermes.exe", "-z", strict_prompt], capture_output=True, text=True, encoding="utf-8")

print("\n--- HERMES RAW STDOUT ---")
print(res.stdout)
if res.stderr:
    print("\n--- HERMES STDERR ---")
    print(res.stderr)
