import os
import sys
import glob
import yaml

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

AI_QA_ROOT = r"d:\artemis\ai-qa"
TESTCASES_DIR = os.path.join(AI_QA_ROOT, "testcases")
SUITES_DIR = os.path.join(AI_QA_ROOT, "suites")
os.makedirs(SUITES_DIR, exist_ok=True)

def main():
    print("=== TỰ ĐỘNG TẠO VÀ CẬP NHẬT TOÀN BỘ TEST SUITES CHO 1,053 TEST CASES ===")
    
    # 1. Quét tất cả thư mục trong testcases
    folders = [f for f in os.listdir(TESTCASES_DIR) if os.path.isdir(os.path.join(TESTCASES_DIR, f))]
    
    all_tests = []
    category_map = {}

    for folder in sorted(folders):
        fpath = os.path.join(TESTCASES_DIR, folder)
        yaml_files = sorted(glob.glob(os.path.join(fpath, "*.yaml")))
        tests_in_folder = []
        for yf in yaml_files:
            tc_id = os.path.splitext(os.path.basename(yf))[0]
            tests_in_folder.append(tc_id)
            all_tests.append(tc_id)
        
        category_map[folder] = tests_in_folder

        # Tạo suite riêng cho từng module/folder
        suite_data = {
            "name": f"Module {folder.replace('_', ' ').replace('-', ' ').title()} Suite",
            "description": f"Chạy toàn bộ {len(tests_in_folder)} test cases cho phân hệ {folder}",
            "tests": tests_in_folder
        }
        suite_file = os.path.join(SUITES_DIR, f"module-{folder}.yaml")
        with open(suite_file, "w", encoding="utf-8") as f:
            yaml.dump(suite_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        print(f"- Module '{folder}': {len(tests_in_folder)} test cases -> {os.path.basename(suite_file)}")

    # 2. Tạo Suite toàn diện 1,000+ Test Cases
    exhaustive_suite = {
        "name": "GorillaDesk Master Exhaustive Suite (1,000+ Tests)",
        "description": "Bộ kiểm thử toàn diện toàn bộ 1,053 test cases thực địa, compliance và AI",
        "total_cases": len(all_tests),
        "tests": all_tests
    }
    with open(os.path.join(SUITES_DIR, "suite-master-exhaustive.yaml"), "w", encoding="utf-8") as f:
        yaml.dump(exhaustive_suite, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

    print(f"\n✅ Đã cập nhật xong toàn bộ suites! Tổng số test cases trong Master Suite: {len(all_tests)}")

if __name__ == "__main__":
    main()
