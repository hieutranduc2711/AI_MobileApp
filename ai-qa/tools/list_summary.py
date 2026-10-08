import os
import sys
import glob

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

base = r"d:\artemis\ai-qa\testcases"
folders = sorted([f for f in os.listdir(base) if os.path.isdir(os.path.join(base, f))])
total = 0

print(f"{'THƯ MỤC PHÂN HỆ (MODULE FOLDER)':<35} | {'SỐ LƯỢNG TEST CASE':<20}")
print("-" * 60)
for f in folders:
    cnt = len(glob.glob(os.path.join(base, f, "*.yaml")))
    total += cnt
    print(f"{f:<35} | {cnt:<20}")
print("-" * 60)
print(f"{'TỔNG CỘNG TEST CASES':<35} | {total:<20}")
