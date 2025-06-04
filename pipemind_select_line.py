
import os
import random

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


class SelectLineFromDropdown:
    def __init__(self):
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        files = list_txt_files_recursive(COMFY_INPUT_DIR)
        if not files:
            files = ["[No .txt files found]"]
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "file_name": (files,),
                "mode": (["manual", "random", "increment", "decrement"],),
                "line_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,
                }),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff
                }),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT")
    RETURN_NAMES = ("selected_line", "line_count", "current_index")
    FUNCTION = "get_select_line"
    CATEGORY = "Text/Custom"

    @staticmethod
    def IS_CHANGED(enabled=True, **kwargs):
        return enabled

    def get_select_line(self, enabled: bool, file_name: str, mode: str, line_index: int, seed: int):
        if not enabled:
            return ("", 0, 0)  # Soft disable: return empty line when disabled

        # Compute full path and read lines
        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Strip out empty lines
                lines = [ln.rstrip("\n") for ln in f if ln.strip()]

            if not lines:
                return ("[Error: File is empty]", 0, 0)

            n = len(lines)

            if mode == "random":
                rng = random.Random(seed)
                self.current_index = rng.randint(0, n - 1)
            elif mode == "increment":
                self.current_index = (self.current_index + 1) % n
            elif mode == "decrement":
                self.current_index = (self.current_index - 1) % n
            else:  # manual mode
                self.current_index = max(0, min(line_index, n - 1))

            return (lines[self.current_index], n, self.current_index)

        except Exception as e:
            return (f"[Error: {e}]", 0, 0)