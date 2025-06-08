import os
import json
import numpy as np
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import sys

# Add ComfyUI folder to path if needed
comfy_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if comfy_path not in sys.path:
    sys.path.append(comfy_path)

import folder_paths


class PipemindSaveImageWTxt:
    _current_batch = None
    _image_counter = 0
    _last_directory_count = 0
    _workflow_started = False

    def __init__(self):
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
        self.output_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "tag", "tooltip": "The prefix for the file to save."}),
                "output_path": ("STRING", {"default": "tagger", "tooltip": "The subfolder path (optional)"}),
            },
            "optional": {
                "caption_file_extension": ("STRING",
                                           {"default": ".txt", "tooltip": "The extension for the caption file."}),
                "caption": ("STRING", {"forceInput": True, "tooltip": "string to save as .txt file"}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "Pipemind/image"
    DESCRIPTION = "Saves images with batch folders and optional text files."

    def get_next_batch_folder(self, base_path):
        """Find the highest existing batch number and return the next one."""
        highest_batch = -1
        if os.path.exists(base_path):
            for item in os.listdir(base_path):
                if item.startswith("batch_"):
                    try:
                        batch_num = int(item.split("_")[1])
                        highest_batch = max(highest_batch, batch_num)
                    except (ValueError, IndexError):
                        continue
        return f"batch_{highest_batch + 1:02d}"

    def count_existing_images(self, batch_path, filename_prefix):
        """Count existing images in the batch directory with the given prefix."""
        if not os.path.exists(batch_path):
            return 0

        count = 0
        for filename in os.listdir(batch_path):
            if filename.startswith(filename_prefix) and filename.endswith('.png'):
                count += 1
        return count

    def detect_new_workflow(self, base_path, filename_prefix):
        """
        Enhanced detection logic for new workflow runs.

        Returns True if a new batch should be created.
        """
        # First run ever
        if PipemindSaveImageWTxt._current_batch is None:
            print("DEBUG: First run - creating initial batch")
            return True

        # Get current batch path
        current_batch_path = os.path.join(base_path, PipemindSaveImageWTxt._current_batch)

        # If current batch directory doesn't exist, create new batch
        if not os.path.exists(current_batch_path):
            print("DEBUG: Current batch directory doesn't exist - creating new batch")
            return True

        # Count existing images
        existing_count = self.count_existing_images(current_batch_path, filename_prefix)

        print(f"DEBUG: Current state - counter: {PipemindSaveImageWTxt._image_counter}, "
              f"existing files: {existing_count}, last_dir_count: {PipemindSaveImageWTxt._last_directory_count}")

        # Key detection logic: If counter reset to 0 but directory has images from previous run
        if PipemindSaveImageWTxt._image_counter == 0 and existing_count > 0:
            print("DEBUG: Counter reset detected - new workflow starting")
            return True

        # Additional check: If we're starting and the directory count doesn't match our expectations
        if (PipemindSaveImageWTxt._image_counter == 0 and
                existing_count != PipemindSaveImageWTxt._last_directory_count and
                existing_count > 0):
            print("DEBUG: Directory state mismatch - likely new workflow")
            return True

        # If counter is less than existing files, something reset
        if PipemindSaveImageWTxt._image_counter < existing_count:
            print("DEBUG: Counter behind existing files - workflow may have restarted")
            return True

        return False

    def save_images(self, images, output_path, filename_prefix="tag", prompt=None, extra_pnginfo=None, caption=None,
                    caption_file_extension=".txt"):
        try:
            # Handle output path
            if os.path.isabs(output_path):
                base_path = output_path
            else:
                if not output_path.strip():
                    base_path = self.output_dir
                else:
                    base_path = os.path.join(self.output_dir, output_path.strip())

            # Check if we should create a new batch
            if self.detect_new_workflow(base_path, filename_prefix):
                # Store the count from the previous batch before creating new one
                if PipemindSaveImageWTxt._current_batch is not None:
                    old_batch_path = os.path.join(base_path, PipemindSaveImageWTxt._current_batch)
                    PipemindSaveImageWTxt._last_directory_count = self.count_existing_images(old_batch_path,
                                                                                             filename_prefix)

                # Create new batch
                PipemindSaveImageWTxt._current_batch = self.get_next_batch_folder(base_path)
                PipemindSaveImageWTxt._image_counter = 0
                PipemindSaveImageWTxt._workflow_started = True
                print(f"*** CREATING NEW BATCH: {PipemindSaveImageWTxt._current_batch} ***")

            # Create full path for the batch
            full_path = os.path.join(base_path, PipemindSaveImageWTxt._current_batch)
            os.makedirs(full_path, exist_ok=True)

            results = list()
            for image in images:
                i = 255. * image.cpu().numpy()
                img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

                # Prepare metadata
                metadata = PngInfo() if prompt is not None or extra_pnginfo is not None else None
                if metadata:
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for x in extra_pnginfo:
                            metadata.add_text(x, json.dumps(extra_pnginfo[x]))

                # Create filenames
                base_file_name = f"{filename_prefix}_{PipemindSaveImageWTxt._image_counter:05}"
                file = f"{base_file_name}.png"
                file_path = os.path.join(full_path, file)

                # Save image
                img.save(file_path, pnginfo=metadata, compress_level=self.compress_level)

                # Save caption if provided
                if caption is not None:
                    txt_file = base_file_name + caption_file_extension
                    txt_path = os.path.join(full_path, txt_file)
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(caption)

                print(
                    f"Saved: {PipemindSaveImageWTxt._current_batch}/{file} (counter: {PipemindSaveImageWTxt._image_counter})")
                PipemindSaveImageWTxt._image_counter += 1

                results.append({
                    "filename": file,
                    "subfolder": os.path.basename(full_path),
                    "type": self.type
                })

            return file,

        except Exception as e:
            print(f"Error in save_images: {str(e)}")
            raise e


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "PipemindSaveImageWTxt": PipemindSaveImageWTxt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PipemindSaveImageWTxt": "Pipemind Save Image with Text (Enhanced)"
}

