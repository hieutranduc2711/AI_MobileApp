import os

class ContextBuilder:
    def __init__(self, root_dir="d:/artemis/ai-qa"):
        self.root_dir = root_dir

    def get_feature_context(self, feature_name):
        feature_dir = os.path.join(self.root_dir, "knowledge", "features", feature_name)
        context_file = os.path.join(feature_dir, "context.md")
        if os.path.exists(context_file):
            with open(context_file, "r", encoding="utf-8") as f:
                return f.read()
        return ""
