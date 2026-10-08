import os
import re
import yaml

SOURCE_DIR = r"C:\Users\Admin\Downloads\group by module\modules"
TARGET_ROOT = r"d:\artemis\ai-qa"

def sanitize_filename(name):
    return re.sub(r'[^\w\-_\.]', '_', name)

def main():
    print("=== START BULK IMPORT: 23 MODULES INTO AI-QA ===")
    
    modules = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    print(f"Detected {len(modules)} modules in Detox repository.")

    total_testcases_imported = 0
    all_suite_testcases = []

    for mod in modules:
        mod_src = os.path.join(SOURCE_DIR, mod)
        mod_target_tc = os.path.join(TARGET_ROOT, "testcases", mod)
        mod_target_kb = os.path.join(TARGET_ROOT, "knowledge", "features", mod)

        os.makedirs(mod_target_tc, exist_ok=True)
        os.makedirs(mod_target_kb, exist_ok=True)

        # 1. Tao file context.md cho module
        kb_context_file = os.path.join(mod_target_kb, "context.md")
        if not os.path.exists(kb_context_file):
            with open(kb_context_file, "w", encoding="utf-8") as f:
                f.write(f"# Feature: {mod.capitalize()}\n\n")
                f.write(f"Business logic and test knowledge for GorillaDesk Mobile module: {mod}.\n")

        kb_inv_file = os.path.join(mod_target_kb, "invariants.yaml")
        if not os.path.exists(kb_inv_file):
            with open(kb_inv_file, "w", encoding="utf-8") as f:
                f.write(f"invariants:\n  - id: {mod.upper()}-INV-001\n    description: 'Ensure data integrity for module {mod}'\n")

        kb_risks_file = os.path.join(mod_target_kb, "risks.yaml")
        if not os.path.exists(kb_risks_file):
            with open(kb_risks_file, "w", encoding="utf-8") as f:
                f.write(f"risks:\n  - id: RISK-{mod.upper()}-001\n    name: 'UI transition delay'\n    mitigation: 'Ensure minimum 650ms delay between screen transitions'\n")

        # 2. Quet cac file .md
        md_files = [f for f in os.listdir(mod_src) if f.endswith(".md")]
        mod_tc_count = 0
        mod_suite_cases = []

        for md_file in md_files:
            md_path = os.path.join(mod_src, md_file)
            with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            yaml_blocks = re.findall(r'```yaml\s*\n(.*?)\n```', content, re.DOTALL)
            for block in yaml_blocks:
                try:
                    data = yaml.safe_load(block)
                    if isinstance(data, dict) and "id" in data:
                        tc_id = data.get("id")
                        tc_title = data.get("title", "")
                        tc_goal = data.get("goal", "")
                        
                        formatted_tc = {
                            "id": tc_id,
                            "title": tc_title,
                            "module": mod,
                            "source_file": md_file,
                            "group": data.get("group", ""),
                            "profile": data.get("profile", "pro"),
                            "verification": data.get("verification", "final"),
                            "goal": tc_goal,
                            "detox_reference": data.get("detox", ""),
                            "expected": [
                                f"Goal reached: {tc_title}"
                            ]
                        }

                        tc_filename = f"{sanitize_filename(tc_id)}.yaml"
                        tc_out_path = os.path.join(mod_target_tc, tc_filename)
                        with open(tc_out_path, "w", encoding="utf-8") as f:
                            yaml.dump(formatted_tc, f, allow_unicode=True, sort_keys=False)

                        rel_tc_path = f"testcases/{mod}/{tc_filename}"
                        mod_suite_cases.append(rel_tc_path)
                        all_suite_testcases.append(rel_tc_path)
                        mod_tc_count += 1
                        total_testcases_imported += 1
                except Exception:
                    pass

        # 3. Tao Suite rieng
        if mod_suite_cases:
            suite_file = os.path.join(TARGET_ROOT, "suites", f"module-{mod}.yaml")
            with open(suite_file, "w", encoding="utf-8") as f:
                yaml.dump({
                    "name": f"Module {mod.capitalize()} Test Suite",
                    "description": f"All {len(mod_suite_cases)} test cases for module {mod}",
                    "testcases": mod_suite_cases
                }, f, allow_unicode=True, sort_keys=False)

            print(f"  * Module [{mod}]: Imported {mod_tc_count} test cases -> Suite: module-{mod}.yaml")

    # 4. Suite Full Coverage
    all_app_suite_file = os.path.join(TARGET_ROOT, "suites", "all-app-full-coverage.yaml")
    with open(all_app_suite_file, "w", encoding="utf-8") as f:
        yaml.dump({
            "name": "GorillaDesk All App Full Coverage Suite",
            "description": f"All {total_testcases_imported} test cases covering all 23 modules",
            "total_cases": total_testcases_imported,
            "testcases": all_suite_testcases
        }, f, allow_unicode=True, sort_keys=False)

    print("=" * 65)
    print(f" IMPORT COMPLETED: {total_testcases_imported} TEST CASES IMPORTED INTO AI-QA!")
    print(f" Full suite path: suites/all-app-full-coverage.yaml")
    print("=" * 65)

if __name__ == "__main__":
    main()
