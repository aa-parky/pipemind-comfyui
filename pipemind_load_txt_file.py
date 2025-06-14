import os

COMFY_INPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "input")
)


def list_txt_files_recursive(base_dir):
    """
    Recursively collect all .txt files under base_dir, returning paths relative to base_dir.
    """
    txt_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                txt_files.append(rel_path)
    return sorted(txt_files)


class LoadTxtFile:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        files = list_txt_files_recursive(COMFY_INPUT_DIR)
        if not files:
            files = ["[No .txt files found]"]
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "file_name": (files,),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("file_content", "line_count")
    FUNCTION = "load_txt_file"
    CATEGORY = "Text/Custom"

    @staticmethod
    def IS_CHANGED(enabled=True, **kwargs):
        return enabled

    def load_txt_file(self, enabled: bool, file_name: str):
        if not enabled:
            return ("", 0)  # Soft disable: return empty content when disabled

        # Compute full path and read content
        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Count non-empty lines
                line_count = sum(1 for line in content.splitlines() if line.strip())

            return (content, line_count)

        except Exception as e:
            return (f"[Error: {e}]", 0)
