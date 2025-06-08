import os
from PIL import Image, ImageOps
import numpy as np
import torch

COMFY_INPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "input")
)


def pil2tensor(image):
    """Convert PIL image to tensor in the format ComfyUI expects"""
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    if len(image.shape) == 3:
        image = image.permute(0, 3, 1, 2)
    return image


def create_empty_image():
    """Create a small black image as a fallback"""
    return torch.zeros((1, 3, 64, 64), dtype=torch.float32)


class BatchImageLoad:
    def __init__(self):
        self.current_index = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "mode": (["single", "sequential", "random"],),
                "image_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,
                }),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT")
    RETURN_NAMES = ("image", "image_count")
    FUNCTION = "load_image"
    CATEGORY = "image/Custom"

    def load_image(self, directory: str, mode: str, image_index: int, seed: int):
        try:
            # Handle directory path
            full_path = os.path.join(COMFY_INPUT_DIR, directory)
            if not os.path.exists(full_path):
                print(f"Path does not exist: {full_path}")
                return (create_empty_image(), 0)

            # Get list of image files
            image_files = []
            allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
            if os.path.isfile(full_path):
                if any(full_path.lower().endswith(ext) for ext in allowed_extensions):
                    image_files = [full_path]
            else:
                for root, _, files in os.walk(full_path):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            image_files.append(os.path.join(root, file))

            image_files.sort()
            file_count = len(image_files)

            if file_count == 0:
                print("No images found")
                return (create_empty_image(), 0)

            # Select image based on mode
            if mode == "sequential":
                self.current_index = (self.current_index + 1) % file_count
                selected_index = self.current_index
            elif mode == "random":
                import random
                random.seed(seed)
                selected_index = random.randint(0, file_count - 1)
            else:  # single mode
                selected_index = min(image_index, file_count - 1)

            # Load and process image
            image_path = image_files[selected_index]
            print(f"Loading image: {image_path}")

            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image)  # Handle EXIF orientation

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to tensor
            tensor_image = pil2tensor(image)

            return (tensor_image, file_count)

        except Exception as e:
            print(f"Error loading image: {e}")
            import traceback
            traceback.print_exc()
            return (create_empty_image(), 0)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("NaN")