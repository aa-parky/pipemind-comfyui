
# Standard library imports
import os
import random
import re

# Define the path to ComfyUI's input directory
# This uses relative paths to locate the 'input' folder from the current script location
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

def parse_custom_indices(indices_str):
    """
    Parse a string of comma-separated indices into a list of integers.
    Supports ranges like "1-5" and "10-15" as well as individual indices.

    Args:
        indices_str (str): String of comma-separated indices/ranges (e.g., "1,3,5-8,10")

    Returns:
        list: List of integer indices
    """
    if not indices_str.strip():
        return []

    result = []
    parts = indices_str.split(',')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Check if it's a range (e.g., "5-10")
        if '-' in part:
            try:
                start, end = map(int, part.split('-', 1))
                # Ensure start <= end
                if start <= end:
                    result.extend(range(start, end + 1))
            except ValueError:
                # If conversion fails, skip this part
                continue
        else:
            # Single number
            try:
                result.append(int(part))
            except ValueError:
                # If conversion fails, skip this part
                continue

    return result



class SelectLineFromDropdown:
    """
    ComfyUI node for selecting lines from text files with various selection modes.

    This node allows users to read lines from text files in the ComfyUI input directory
    and select specific lines using different modes:
    - manual: Select a specific line by index
    - random: Select a random line based on a seed
    - increment: Start from a line and increment with each batch
    - decrement: Start from a line and decrement with each batch

    The node maintains state across batch processing, allowing for proper
    sequencing through file lines even when ComfyUI creates new instances
    for each batch.
    """
    # Class variable to store state across instances - persists between batch operations
    # Format: {"file_name_mode": (current_index, line_index)}
    _batch_state = {}

    def __init__(self):
        # Instance-specific current line index
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        """
        Define the input parameters for this ComfyUI node.

        This method scans the input directory for text files and creates
        a dropdown selection of available files. It also defines other
        parameters like mode, line index, and seed for random selection.

        Returns:
            dict: A dictionary defining all input parameters and their types
        """
        # Get list of all .txt files in the input directory
        files = list_txt_files_recursive(COMFY_INPUT_DIR)
        if not files:
            files = ["[No .txt files found]"]

        return {
            "required": {
                # Enable/disable the node without removing it
                "enabled": ("BOOLEAN", {"default": True}),

                # Dropdown with all available .txt files
                "file_name": (files,),

                # Selection mode
                "mode": (["manual", "random", "increment", "decrement", "custom_seq", "custom_random"],),

                # Starting line index for selection
                "line_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,  # Large enough for any reasonable file
                }),

                # Seed value for random selection mode
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 0xffffffffffffffff  # Max 64-bit unsigned int
                }),

                # Custom indices as comma-separated string (e.g., "12,18,78,91")
                "custom_indices": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }

    # Define output types for ComfyUI
    RETURN_TYPES = ("STRING", "INT", "INT")

    # Names for the output values
    RETURN_NAMES = ("selected_line", "line_count", "current_index")

    # The method to call when this node is executed
    FUNCTION = "get_select_line"

    # Category in the ComfyUI node browser
    CATEGORY = "Pipemind/Custom"

    # JavaScript file for UI customization
    JAVASCRIPT_FILE = "web/js/pipemind_selectLine.js"

    @staticmethod
    def IS_CHANGED(enabled=True, **kwargs):
        """
        Tell ComfyUI when this node should be re-executed.

        Returns True when enabled, causing the node to process on each execution.
        This is important for proper batch processing and state updates.

        Args:
            enabled (bool): Whether the node is enabled
            **kwargs: Other input parameters (unused)

        Returns:
            bool: True if the node should be considered as changed
        """
        return enabled

    def get_select_line(self, enabled: bool, file_name: str, mode: str, line_index: int, seed: int, custom_indices: str):
        """
        Main processing function that selects a line from the specified text file.

        This method reads the text file and selects a specific line based on the mode:
        - manual: Select exactly the line specified by line_index
        - random: Select a random line using the provided seed
        - increment: Select the next line (with state persistence across batches)
        - decrement: Select the previous line (with state persistence across batches)

        The method maintains state across ComfyUI batch operations using a class-level
        dictionary that persists between instances.

        Args:
            enabled (bool): Whether the node is enabled
            file_name (str): Path to the text file (relative to input directory)
            mode (str): Selection mode (manual, random, increment, decrement)
            line_index (int): Starting or specific line index (0-based)
            seed (int): Seed for random selection

        Returns:
            tuple: (selected_line, total_line_count, current_index)
        """
        # Create a unique key for this file and mode combination to track state
        state_key = f"{file_name}_{mode}"

        # Early return if node is disabled
        if not enabled:
            return ("", 0, 0)  # Soft disable: return empty line when disabled

        # Compute full path and read lines
        file_path = os.path.join(COMFY_INPUT_DIR, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # Strip out empty lines and trailing newlines
                lines = [ln.rstrip("\n") for ln in f if ln.strip()]

            # Handle empty files
            if not lines:
                return ("[Error: File is empty]", 0, 0)

            # Store the number of lines for convenience
            n = len(lines)

            # Parse custom indices if provided
            custom_idx_list = []
            if custom_indices and (mode == "custom_seq" or mode == "custom_random"):
                # Parse the custom indices string using the helper function
                parsed_indices = parse_custom_indices(custom_indices)
                # Filter indices to only those within valid range for the file
                custom_idx_list = [idx for idx in parsed_indices if 0 <= idx < n]

                if not custom_idx_list:
                    return (f"[Error: No valid indices in custom sequence. File has {n} lines.]", n, 0)

            # CUSTOM SEQUENCE MODE: Iterate through custom indices
            if mode == "custom_seq":
                if not custom_idx_list:
                    return ("[Error: No custom indices provided]", n, 0)

                # Key for storing state specific to this sequence
                seq_key = f"{file_name}_{mode}_{custom_indices}"

                if seq_key in self.__class__._batch_state:
                    # Get the position in the sequence, not the line index itself
                    seq_pos, _ = self.__class__._batch_state[seq_key]
                    # Move to next position in sequence
                    next_pos = (seq_pos + 1) % len(custom_idx_list)
                    # Get the actual line index from the custom sequence
                    self.current_index = custom_idx_list[next_pos]
                    # Store position in sequence, not the line index
                    self.__class__._batch_state[seq_key] = (next_pos, custom_indices)
                else:
                    # Start at the first index in the sequence
                    self.current_index = custom_idx_list[0]
                    # Store position 0 in the sequence
                    self.__class__._batch_state[seq_key] = (0, custom_indices)

            # CUSTOM RANDOM MODE: Randomly select from custom indices
            elif mode == "custom_random":
                if not custom_idx_list:
                    return ("[Error: No custom indices provided]", n, 0)

                # Use the seed for consistent random selection
                rng = random.Random(seed)
                # Select a random index from the custom list
                self.current_index = rng.choice(custom_idx_list)

            # RANDOM MODE: Select a random line based on the seed
            elif mode == "random":
                # Create a random number generator with the provided seed
                # This ensures consistent results for the same seed
                rng = random.Random(seed)
                self.current_index = rng.randint(0, n - 1)  # Select random line

            # INCREMENT MODE: Move to the next line with each batch
            elif mode == "increment":
                # Check if we have saved state for this file+mode combination
                if state_key in self.__class__._batch_state:
                    # Retrieve previously saved state
                    saved_index, saved_line_index = self.__class__._batch_state[state_key]

                    # If user changed the line_index input, reset to that position
                    if line_index != saved_line_index:
                        # Ensure index is within bounds
                        self.current_index = max(0, min(line_index, n - 1))
                    else:
                        # Continue from previous position and increment
                        # The modulo (%) operation handles wrapping around to the start
                        # when we reach the end of the file
                        self.current_index = (saved_index + 1) % n
                else:
                    # First time with this combination, start at requested line_index
                    # Ensure the index is within bounds
                    self.current_index = max(0, min(line_index, n - 1))

                # Save current state for next batch operation
                self.__class__._batch_state[state_key] = (self.current_index, line_index)

            # DECREMENT MODE: Move to the previous line with each batch
            elif mode == "decrement":
                # Similar logic to increment mode, but going backwards
                if state_key in self.__class__._batch_state:
                    saved_index, saved_line_index = self.__class__._batch_state[state_key]

                    # Reset if user changed the line_index
                    if line_index != saved_line_index:
                        self.current_index = max(0, min(line_index, n - 1))
                    else:
                        # Go to previous line, wrap around to the end if at the beginning
                        self.current_index = (saved_index - 1) % n
                else:
                    # First time initialization
                    self.current_index = max(0, min(line_index, n - 1))

                # Save state for next batch
                self.__class__._batch_state[state_key] = (self.current_index, line_index)

            # MANUAL MODE: Always use the exact line_index specified
            else:  # manual mode
                # Simply use the specified line_index (bounded to file size)
                self.current_index = max(0, min(line_index, n - 1))

                # In manual mode, we don't want to remember state between batches
                # So remove any saved state for this file+mode combination
                if state_key in self.__class__._batch_state:
                    del self.__class__._batch_state[state_key]

            # Return the selected line, total line count, and current index
            # This allows downstream nodes to use this information
            return (lines[self.current_index], n, self.current_index)

        except Exception as e:
            # Handle any errors (file not found, permission issues, etc.)
            # Return a descriptive error message and zeros for counts
            return (f"[Error: {e}]", 0, 0)