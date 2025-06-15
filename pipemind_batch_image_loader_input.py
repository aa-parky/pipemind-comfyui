"""
BatchImageLoad Node - A ComfyUI custom node for loading images from directories.

This node allows users to easily load images from the ComfyUI input directory,
with options for sequential or single image loading modes.
It presents a user-friendly dropdown interface for directory selection.
"""

import os
from PIL import Image, ImageOps  # Pillow for image processing
import numpy as np  # NumPy for array operations
import torch  # PyTorch for tensor manipulation

# Define paths to standard ComfyUI directories
COMFY_INPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "input")
)


def pil2tensor(image):
    """Convert PIL image to tensor in the format ComfyUI expects."""
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.from_numpy(image)[None,]
    if len(image.shape) == 4:
        return image
    elif len(image.shape) == 3:
        return image.permute(0, 3, 1, 2)
    else:
        raise ValueError(f"Unexpected tensor shape: {image.shape}")


def create_empty_image(width=64, height=64):
    """Create a small black image as a fallback when no valid image is found."""
    return torch.zeros((1, 3, width, height), dtype=torch.float32)


def validate_image(image_path):
    """Validate if a file is a valid, uncorrupted image that can be opened by PIL."""
    try:
        with Image.open(image_path) as img:
            img.verify()
        with Image.open(image_path) as img:
            img.load()
        return True
    except Exception as e:
        print(f"Invalid image {image_path}: {e}")
        return False


def list_image_directories(base_dir):
    """Get a list of directories in the base_dir that contain images."""
    if not os.path.exists(base_dir):
        print(f"Base directory does not exist: {base_dir}")
        return []

    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    dirs_with_images = set()

    for root, dirs, files in os.walk(base_dir):
        has_images = any(
            any(file.lower().endswith(ext) for ext in allowed_extensions)
            for file in files
        )

        if has_images:
            rel_path = os.path.relpath(root, base_dir)
            rel_path = rel_path.replace('\\', '/')
            if rel_path == '.':
                rel_path = ''

            current_path = rel_path
            while current_path:
                dirs_with_images.add(current_path)
                current_path = os.path.dirname(current_path)

            dirs_with_images.add('')

    result = sorted(dirs_with_images)
    if '' in result:
        result[result.index('')] = '[Root Input Directory]'

    return result


class BatchImageLoadInput:
    """ComfyUI custom node for loading images in batch from input directory."""

    def __init__(self):
        self.current_index = 0
        self.image_files = []
        self.total_files = 0

    @classmethod
    def INPUT_TYPES(cls):
        """Define the input UI elements for the BatchImageLoad node."""
        input_dirs = list_image_directories(COMFY_INPUT_DIR)

        if not input_dirs:
            input_dirs = ["[No directories found]"]

        return {
            "required": {
                "directory": (input_dirs,),
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
    CATEGORY = "Pipemind"

    def get_image_files(self, directory):
        """Get a list of valid image files from a directory or file path."""
        image_files = []
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}

        if os.path.isfile(directory):
            if any(directory.lower().endswith(ext) for ext in allowed_extensions):
                if validate_image(directory):
                    image_files = [directory]
        else:
            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            if validate_image(file_path):
                                image_files.append(file_path)
            except Exception as e:
                print(f"Error walking directory {directory}: {e}")

        return sorted(image_files)

    def load_image(self, directory: str, mode: str, image_index: int):
        """Main processing function for the BatchImageLoad node."""
        try:
            self.image_files = []
            self.total_files = 0

            base_dir = COMFY_INPUT_DIR
            full_path = os.path.join(base_dir, directory)

            if not os.path.exists(full_path):
                print(f"Path does not exist: {full_path}")
                return (create_empty_image(), 0, 0)

            self.image_files = self.get_image_files(full_path)
            self.total_files = len(self.image_files)

            if self.total_files == 0:
                print("No valid images found")
                return (create_empty_image(), 0, 0)

            if isinstance(image_index, str):
                try:
                    image_index = int(image_index)
                except ValueError:
                    print(f"Warning: Invalid image_index value '{image_index}'. Using 0 instead.")
                    image_index = 0

            if self.current_index >= self.total_files:
                self.current_index = min(max(0, image_index), self.total_files - 1)

            if mode == "sequential":
                selected_index = self.current_index
                self.current_index = (self.current_index + 1) % self.total_files
            else:
                selected_index = min(max(0, image_index), self.total_files - 1)
                self.current_index = selected_index

            image_path = self.image_files[selected_index]
            print(f"Loading image {selected_index + 1}/{self.total_files}: {image_path}")

            image = Image.open(image_path)
            image = ImageOps.exif_transpose(image)

            if image.mode != 'RGB':
                image = image.convert('RGB')

            tensor_image = pil2tensor(image)

            return (tensor_image, self.total_files, selected_index)

        except Exception as e:
            print(f"Error loading image: {e}")
            import traceback
            traceback.print_exc()
            return (create_empty_image(), 0, 0)

    @staticmethod
    def IS_CHANGED(**kwargs):
        """Control when ComfyUI should re-execute this node."""
        return float("NaN")