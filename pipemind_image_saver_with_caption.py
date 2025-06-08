
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
    _image_counter = 0

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
    DESCRIPTION = "Saves images with optional text files."

    def count_existing_images(self, path, filename_prefix):
        """Count existing images in the directory with the given prefix."""
        if not os.path.exists(path):
            return 0

        count = 0
        for filename in os.listdir(path):
            if filename.startswith(filename_prefix) and filename.endswith('.png'):
                count += 1
        return count

    def save_images(self, images, output_path, filename_prefix="tag", prompt=None, extra_pnginfo=None, caption=None,
                    caption_file_extension=".txt"):
        try:
            # Handle output path
            if os.path.isabs(output_path):
                full_path = output_path
            else:
                if not output_path.strip():
                    full_path = self.output_dir
                else:
                    full_path = os.path.join(self.output_dir, output_path.strip())

            # Create directory if it doesn't exist
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

                print(f"Saved: {file} (counter: {PipemindSaveImageWTxt._image_counter})")
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