
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
    # Class variable to store state across instances
    _batch_state = {}

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
    CATEGORY = "Pipemind/Custom"

    @staticmethod
    def IS_CHANGED(enabled=True, **kwargs):
        return enabled

    def get_select_line(self, enabled: bool, file_name: str, mode: str, line_index: int, seed: int):
        # Create a unique key for this file and mode combination
        state_key = f"{file_name}_{mode}"

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

            state_key = f"{file_name}_{mode}"

            if mode == "random":
                rng = random.Random(seed)
                self.current_index = rng.randint(0, n - 1)
            elif mode == "increment":
                # Get the saved state or initialize with line_index
                if state_key in self.__class__._batch_state:
                    saved_index, saved_line_index = self.__class__._batch_state[state_key]

                    # If line_index was changed by user, reset to that position
                    if line_index != saved_line_index:
                        self.current_index = max(0, min(line_index, n - 1))
                    else:
                        # Continue from last position and increment
                        self.current_index = (saved_index + 1) % n
                else:
                    # First time with this combination, start at line_index
                    self.current_index = max(0, min(line_index, n - 1))

                # Save the current state for next batch
                self.__class__._batch_state[state_key] = (self.current_index, line_index)

            elif mode == "decrement":
                # Similar logic for decrement
                if state_key in self.__class__._batch_state:
                    saved_index, saved_line_index = self.__class__._batch_state[state_key]

                    if line_index != saved_line_index:
                        self.current_index = max(0, min(line_index, n - 1))
                    else:
                        self.current_index = (saved_index - 1) % n
                else:
                    self.current_index = max(0, min(line_index, n - 1))

                self.__class__._batch_state[state_key] = (self.current_index, line_index)

            else:  # manual mode
                self.current_index = max(0, min(line_index, n - 1))
                # Clear any saved state for this file in manual mode
                if state_key in self.__class__._batch_state:
                    del self.__class__._batch_state[state_key]

            return (lines[self.current_index], n, self.current_index)

        except Exception as e:
            return (f"[Error: {e}]", 0, 0)