
# pipemind_select_line.py
# -----------------------------------------------------------------------------
# SelectLineFromDropdown – ComfyUI custom node
# -----------------------------------------------------------------------------
# Reads a text file from the ComfyUI `input` directory, selects a single line by
# various strategies (manual index, random with seed, increment/decrement across
# batches, or user-defined sequences).
# -----------------------------------------------------------------------------

from __future__ import annotations

import os
import random
from typing import List, Tuple

# -----------------------------------------------------------------------------
# Helper utilities
# -----------------------------------------------------------------------------

# Locate the *input* folder two levels up from this file.
COMFY_INPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "input")
)


def list_txt_files_recursive(base_dir: str) -> List[str]:
    """Return *relative* paths of every .txt file under *base_dir*, sorted."""
    txt_files: List[str] = []
    for root, _, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".txt"):
                rel = os.path.relpath(os.path.join(root, f), base_dir)
                txt_files.append(rel)
    return sorted(txt_files)


def parse_custom_indices(indices: str) -> List[int]:
    """Turn a string like "1,3,5-7" into a list of ints [1,3,5,6,7]."""
    if not indices.strip():
        return []
    out: List[int] = []
    for part in indices.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                lo, hi = map(int, part.split('-', 1))
            except ValueError:
                continue
            if lo <= hi:
                out.extend(range(lo, hi + 1))
        else:
            try:
                out.append(int(part))
            except ValueError:
                continue
    return out


def add_line_numbers(lines: List[str]) -> str:
    """Add line numbers starting from 0 to the text content."""
    if not lines:
        return ""
    # Calculate the width needed for line numbers based on the total number of lines
    width = len(str(len(lines) - 1))
    # Format each line with its number, aligned properly
    return "\n".join(f"{i:>{width}}: {line}" for i, line in enumerate(lines))


# -----------------------------------------------------------------------------
# Node implementation
# -----------------------------------------------------------------------------

class SelectLineFromDropdown:
    """ComfyUI node that outputs a selected line and full text content."""

    # Batch-persistent state: {"file_mode" or "file_customSeq": (idx, line_start)}
    _batch_state: dict[str, Tuple[int, int]] = {}

    # ------------------------------ UI ------------------------------------- #
    @classmethod
    def INPUT_TYPES(cls):
        files = list_txt_files_recursive(COMFY_INPUT_DIR) or ["[No .txt files found]"]
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
                "file_name": (files,),
                "mode": ([
                    "manual",
                    "random",
                    "increment",
                    "decrement",
                    "custom_seq",
                    "custom_random",
                ],),
                "line_index": ("INT", {"default": 0, "min": 0, "max": 1_000_000}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "custom_indices": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING", "INT", "INT", "STRING")
    RETURN_NAMES = ("selected_line", "line_count", "current_index", "file_preview")
    FUNCTION = "run"
    CATEGORY = "Pipemind/Custom"
    JAVASCRIPT_FILE = "web/js/pipemind_selectLine.js"

    @staticmethod
    def IS_CHANGED(enabled: bool = True, **_) -> bool:  # noqa: D401
        """Re-run on every execution while *enabled* is True."""
        return enabled

    # ------------------------------ logic ---------------------------------- #
    def run(
        self,
        enabled: bool,
        file_name: str,
        mode: str,
        line_index: int,
        seed: int,
        custom_indices: str,
    ) -> Tuple[str, int, int, str]:
        """Select the line according to *mode* and return the preview text."""

        # Soft disable – propagate nothing if turned off
        if not enabled:
            return "", 0, 0, ""

        # ------------------------- read file ------------------------------- #
        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = [ln.rstrip("\n") for ln in f if ln.strip()]
        except FileNotFoundError:
            return "[Error: File not found]", 0, 0, ""
        except Exception as e:  # pragma: no cover – generic guard
            return f"[Error: {e}]", 0, 0, ""

        if not lines:
            return "[Error: File is empty]", 0, 0, ""

        n = len(lines)
        # Create numbered version of the full text
        full_text = add_line_numbers(lines)

        # ---------------------- select index ------------------------------- #
        state_key = f"{file_name}_{mode}"

        if mode == "manual":
            idx = max(0, min(line_index, n - 1))

        elif mode == "random":
            idx = random.Random(seed).randint(0, n - 1)

        elif mode in ("increment", "decrement"):
            step = 1 if mode == "increment" else -1
            if state_key in self._batch_state:
                saved_idx, saved_start = self._batch_state[state_key]
                if line_index != saved_start:
                    idx = max(0, min(line_index, n - 1))
                else:
                    idx = (saved_idx + step) % n
            else:
                idx = max(0, min(line_index, n - 1))
            self._batch_state[state_key] = (idx, line_index)

        elif mode in ("custom_seq", "custom_random"):
            seq = [i for i in parse_custom_indices(custom_indices) if 0 <= i < n]
            if not seq:
                return "[Error: No valid indices]", n, 0, full_text

            if mode == "custom_seq":
                seq_key = f"{file_name}_{custom_indices}"
                pos = (self._batch_state.get(seq_key, (-1,))[0] + 1) % len(seq)
                self._batch_state[seq_key] = (pos,)
                idx = seq[pos]
            else:  # custom_random
                idx = random.Random(seed).choice(seq)
        else:
            idx = 0  # defensive default

        # ---------------------- return values ------------------------------ #
        return lines[idx], n, idx, full_text