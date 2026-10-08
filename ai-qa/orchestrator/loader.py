import os
import yaml

class TestLoader:
    def __init__(self, root_dir="d:/artemis/ai-qa"):
        self.root_dir = root_dir

    def load_yaml(self, path):
        full_path = os.path.join(self.root_dir, path) if not os.path.isabs(path) else path
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {full_path}")
        with open(full_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_suite(self, suite_name):
        suite_path = os.path.join(self.root_dir, "suites", f"{suite_name}.yaml")
        return self.load_yaml(suite_path)

    def load_testcase(self, tc_relative_path):
        tc_path = os.path.join(self.root_dir, "testcases", tc_relative_path)
        return self.load_yaml(tc_path)
