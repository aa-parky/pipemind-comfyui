import os
import random

# Use ComfyUI's input folder as source for text files
COMFY_INPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "input"))

def list_txt_files_recursive(base_dir):
    txt_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".txt"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                txt_files.append(rel_path)
    return sorted(txt_files)

class RandomLineFromDropdown:
    @classmethod
    def INPUT_TYPES(cls):
        txt_files = list_txt_files_recursive(COMFY_INPUT_DIR)
        if not txt_files:
            txt_files = ["[No .txt files found]"]

        return {
            "required": {
                "file_name": (txt_files,),
                "seed": ("INT", {
                    "default": 42,
                    "min": 0,
                    "max": 4294967295,  # Full 32-bit unsigned seed range
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("random_line",)
    FUNCTION = "get_random_line"
    CATEGORY = "Text/Custom"

    def get_random_line(self, file_name, seed):
        random.seed(seed)

        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            if not lines:
                return ("[Error: File is empty]",)
            return (random.choice(lines),)
        except Exception as e:
            return (f"[Error: {str(e)}]",)