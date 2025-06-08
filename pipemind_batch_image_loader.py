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


def validate_image(image_path):
    """Validate if the file is a valid image"""
    try:
        with Image.open(image_path) as img:
            img.verify()
        return True
    except Exception:
        print(f"Invalid or corrupted image: {image_path}")
        return False


class BatchImageLoad:
    def __init__(self):
        self.current_index = 0
        self.image_files = []
        self.total_files = 0

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
                "mode": (["single", "sequential"],),
                "image_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "image_count", "current_index")
    FUNCTION = "load_image"
    CATEGORY = "image/Custom"

    def get_image_files(self, directory):
        """Get list of valid image files from directory"""
        image_files = []
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

        if os.path.isfile(directory):
            if any(directory.lower().endswith(ext) for ext in allowed_extensions):
                if validate_image(directory):
                    image_files = [directory]
        else:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if any(file.lower().endswith(ext) for ext in allowed_extensions):
                        if validate_image(file_path):
                            image_files.append(file_path)

        return sorted(image_files)

    def load_image(self, directory: str, mode: str, image_index: int):
        try:
            # Handle directory path
            full_path = os.path.join(COMFY_INPUT_DIR, directory)
            if not os.path.exists(full_path):
                print(f"Path does not exist: {full_path}")
                return (create_empty_image(), 0, 0)

            # Get and cache list of valid image files
            if not self.image_files:
                self.image_files = self.get_image_files(full_path)
                self.total_files = len(self.image_files)

            if self.total_files == 0:
                print("No valid images found")
                return (create_empty_image(), 0, 0)

            # Select image based on mode
            if mode == "sequential":
                selected_index = self.current_index
                self.current_index = (self.current_index + 1) % self.total_files
            else:  # single mode
                selected_index = min(image_index, self.total_files - 1)
                self.current_index = selected_index

            # Load and process image
            image_path = self.image_files[selected_index]
            print(f"Loading image {selected_index + 1}/{self.total_files}: {image_path}")

            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image)  # Handle EXIF orientation

            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convert to tensor
            tensor_image = pil2tensor(image)

            return (tensor_image, self.total_files, selected_index)

        except Exception as e:
            print(f"Error loading image: {e}")
            import traceback
            traceback.print_exc()
            return (create_empty_image(), 0, 0)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return float("NaN")