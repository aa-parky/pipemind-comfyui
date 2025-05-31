import os

# Use ComfyUI's input folder as source for text files
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
    @classmethod
    def INPUT_TYPES(cls):
        # Build a dropdown of available .txt files
        files = list_txt_files_recursive(COMFY_INPUT_DIR)
        if not files:
            files = ["[No .txt files found]"]
        return {
            "required": {
                # dropdown list of relative file paths
                "file_name": (files,),
                # zero-based line index
                "line_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("selected_line",)
    FUNCTION = "get_select_line"
    CATEGORY = "Text/Custom"

    def get_select_line(self, file_name: str, line_index: int):
        if line_index == 99:
            return ("",)  # Soft disable: return empty line

        # Compute full path and read lines
        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Strip out empty lines
                lines = [ln.rstrip("\n") for ln in f if ln.strip()]
            if not lines:
                return ("[Error: File is empty]",)
            # Clamp index to valid range
            idx = max(0, min(line_index, len(lines) - 1))
            return (lines[idx],)
        except Exception as e:
            return (f"[Error: {e}]",
                    )