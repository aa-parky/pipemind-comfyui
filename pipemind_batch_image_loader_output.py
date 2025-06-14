"""
BatchImageLoad Node - A ComfyUI custom node for loading images from directories.

This node allows users to easily load images from the ComfyUI input or output 
directories, with options for sequential or single image loading modes.
It presents a user-friendly dropdown interface for directory selection.
"""

import os
from PIL import Image, ImageOps  # Pillow for image processing
import numpy as np              # NumPy for array operations
import torch                    # PyTorch for tensor manipulation

# Define paths to standard ComfyUI directories
# These are used to provide easy access to input and output folders
COMFY_INPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "input")
)

COMFY_OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "output")
)

def pil2tensor(image):
    """
    Convert PIL image to tensor in the format ComfyUI expects.
    
    ComfyUI expects images as PyTorch tensors in NCHW format (batch, channels, height, width)
    with normalized float values between 0.0 and 1.0.
    
    Args:
        image: PIL Image object
        
    Returns:
        torch.Tensor: Image as tensor in NCHW format with values normalized to [0.0, 1.0]
    """
    # Convert PIL image to numpy array and normalize to float32 in range [0.0, 1.0]
    image = np.array(image).astype(np.float32) / 255.0
    
    # Convert to tensor and add batch dimension
    image = torch.from_numpy(image)[None,]
    
    # If the tensor has 3 dimensions (batch, height, width, channels), 
    # rearrange to (batch, channels, height, width)
    if len(image.shape) == 4:  # Already in BCHW format
        return image
    elif len(image.shape) == 3:  # In HWC format (height, width, channels)
        return image.permute(0, 3, 1, 2)
    else:
        raise ValueError(f"Unexpected tensor shape: {image.shape}")


def create_empty_image(width=64, height=64):
    """
    Create a small black image as a fallback when no valid image is found.
    
    Returns:
        torch.Tensor: A small black image tensor in the format expected by ComfyUI.
    """
    # Create a 64x64 black image with 3 color channels in NCHW format
    return torch.zeros((1, 3, width, height), dtype=torch.float32)


def validate_image(image_path):
    """
    Validate if a file is a valid, uncorrupted image that can be opened by PIL.
    
    Args:
        image_path: Path to the image file to validate
        
    Returns:
        bool: True if the image is valid, False otherwise
    """
    try:
        # Try to open and verify the image without fully loading it into memory
        with Image.open(image_path) as img:
            img.verify()
        
        # If the above didn't raise an exception, try actually loading the image
        # (some issues only appear when fully loading)
        with Image.open(image_path) as img:
            img.load()
            
        return True
    except Exception as e:
        print(f"Invalid image {image_path}: {e}")
        return False


def list_image_directories(base_dir):
    """
    Get a list of directories in the base_dir that contain images.
    
    This function is used to populate the directory dropdown in the UI.
    It filters out directories that don't contain any valid images.
    
    Args:
        base_dir: Base directory to search for image-containing subdirectories
        
    Returns:
        list: Sorted list of directories (relative to base_dir) containing images
    """
    # Check if the base directory exists
    if not os.path.exists(base_dir):
        print(f"Base directory does not exist: {base_dir}")
        return []
    
    # Define allowed image file extensions
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
    # Track which directories contain images
    dirs_with_images = set()
    
    # Walk the directory tree
    for root, dirs, files in os.walk(base_dir):
        # Check if any files in this directory are images
        has_images = any(
            any(file.lower().endswith(ext) for ext in allowed_extensions)
            for file in files
        )
        
        # If this directory has images, add it to our set
        if has_images:
            # Calculate the relative path from base_dir
            rel_path = os.path.relpath(root, base_dir)
            # Replace backslashes with forward slashes for cross-platform compatibility
            rel_path = rel_path.replace('\\', '/')
            # Don't include the root directory as "."
            if rel_path == '.':
                rel_path = ''
            
            # Add this directory and all its parent directories
            # This ensures that even if a parent doesn't directly contain images,
            # it will be shown if any of its children contain images
            current_path = rel_path
            while current_path:
                dirs_with_images.add(current_path)
                # Move up one directory level
                current_path = os.path.dirname(current_path)
            
            # Also add the empty string to represent the root directory
            dirs_with_images.add('')
    
    # Convert the set to a sorted list
    result = sorted(dirs_with_images)
    
    # If the root directory was added (as ''), replace it with a more user-friendly name
    if '' in result:
        result[result.index('')] = '[Root Output Directory]'
    
    return result


class BatchImageLoad_output:
    """
    ComfyUI custom node for loading images in batch from directories.
    
    This node allows users to:
    1. Choose a specific directory from a dropdown of directories in the output folder
    2. Load images in either "single" mode (selecting by index) or "sequential" mode (advancing automatically)
    
    The node maintains state between executions to support sequential loading.
    """
    
    def __init__(self):
        """
        Initialize the BatchImageLoad node with empty state.
        
        The state variables are:
        - current_index: Tracks the currently selected image index for sequential loading
        - image_files: Caches the list of valid image files in the selected directory
        - total_files: Caches the total number of valid images found
        """
        self.current_index = 0    # Index of the current image in sequential mode
        self.image_files = []     # Cache of valid image files in the selected directory  
        self.total_files = 0      # Total number of valid images in the selected directory

    @classmethod
    def INPUT_TYPES(cls):
        """
        Define the input UI elements for the BatchImageLoad node.
        
        This method is called by ComfyUI to determine what inputs to show in the node's UI.
        The method populates the directory dropdown with directories from the output folder.
    
        Returns:
            dict: Dictionary defining all the input fields and their properties
        """
        # Get list of all directories from the output folder
        output_dirs = list_image_directories(COMFY_OUTPUT_DIR)
    
        # Provide placeholder if no directories are found
        if not output_dirs:
            output_dirs = ["[No directories found]"]
    
        return {
            "required": {
                # Directory dropdown: shows directories from the output folder
                "directory": (output_dirs,),
    
                # Mode selection:
                # - "single": Load a specific image by index
                # - "sequential": Load images in sequence, advancing each time the node is executed
                "mode": (["single", "sequential"],),
    
                # Image index selection: used in "single" mode to select a specific image
                "image_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 1000000,  # Large max value to accommodate directories with many images
                }),
            }
        }

    # Define the output types and names
    RETURN_TYPES = ("IMAGE", "INT", "INT")
    RETURN_NAMES = ("image", "image_count", "current_index")
    
    # The function that will be called to process the inputs
    FUNCTION = "load_image"
    
    # The category this node will appear in within the ComfyUI interface
    CATEGORY = "Pipemind"

    def get_image_files(self, directory):
        """
        Get a list of valid image files from a directory or file path.
        
        This method handles two cases:
        1. If the directory parameter is a file, it validates if it's an image
        2. If the directory parameter is a directory, it recursively finds all valid images
        
        Each image is validated to ensure it can be properly loaded, helping to
        avoid runtime errors when processing corrupted or incompatible files.
        
        Args:
            directory: Path to a directory or an image file
            
        Returns:
            list: Sorted list of valid image file paths
        """
        image_files = []
        # Define allowed image file extensions
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
    
        # Case 1: directory is actually a file path
        if os.path.isfile(directory):
            # Check if it's an image file with allowed extension
            if any(directory.lower().endswith(ext) for ext in allowed_extensions):
                # Validate that the image is not corrupted
                if validate_image(directory):
                    image_files = [directory]
        # Case 2: directory is a directory path
        else:
            try:
                # Walk the directory recursively
                for root, _, files in os.walk(directory):
                    for file in files:
                        # Build full path to the file
                        file_path = os.path.join(root, file)
                        # Check if it's an image file with allowed extension
                        if any(file.lower().endswith(ext) for ext in allowed_extensions):
                            # Validate that the image is not corrupted
                            if validate_image(file_path):
                                image_files.append(file_path)
            except Exception as e:
                print(f"Error walking directory {directory}: {e}")
    
        # Return sorted list for consistent order of images
        return sorted(image_files)

    def load_image(self, directory: str, mode: str, image_index: int):
        """
        Main processing function for the BatchImageLoad node.
        
        This method:
        1. Resolves the full path to the selected directory in the output folder
        2. Collects all valid images from that directory
        3. Selects an image based on the mode (single or sequential)
        4. Loads, processes, and returns the selected image as a tensor
        
        Error handling is comprehensive to ensure the node doesn't crash the workflow
        when issues occur with directories or images.
        
        Args:
            directory: The relative path to the directory containing images
            mode: Either "single" (select by index) or "sequential" (advance automatically)
            image_index: The index of the image to load in "single" mode
            
        Returns:
            tuple: (image_tensor, total_image_count, current_index)
        """
        try:
            # Reset cached files list to ensure we're working with current data
            # This is important if the directory selection has changed
            self.image_files = []
            self.total_files = 0
            
            # Step 1: Use the output directory as the base directory
            base_dir = COMFY_OUTPUT_DIR
            # Combine the base directory with the selected relative directory
            full_path = os.path.join(base_dir, directory)
                
            # Verify the path exists before attempting to access it
            if not os.path.exists(full_path):
                print(f"Path does not exist: {full_path}")
                # Return a small empty image and zeros for counts on error
                return (create_empty_image(), 0, 0)
    
            # Step 2: Collect and validate all image files in the directory
            self.image_files = self.get_image_files(full_path)
            self.total_files = len(self.image_files)
    
            # If no valid images were found, return an empty image
            if self.total_files == 0:
                print("No valid images found")
                return (create_empty_image(), 0, 0)
    
            # Ensure image_index is an integer and within valid range
            if isinstance(image_index, str):
                try:
                    image_index = int(image_index)
                except ValueError:
                    print(f"Warning: Invalid image_index value '{image_index}'. Using 0 instead.")
                    image_index = 0
            
            # If this is the first run or directory has changed, initialize current_index with image_index
            if self.current_index >= self.total_files:
                self.current_index = min(max(0, image_index), self.total_files - 1)
                
            # Step 3: Select an image based on the operating mode
            if mode == "sequential":
                # In sequential mode, use the current index for this execution
                selected_index = self.current_index
                # Advance the index for next time, wrapping around if needed
                self.current_index = (self.current_index + 1) % self.total_files
            else:  # single mode
                # In single mode, always use the provided index (capped to valid range)
                selected_index = min(max(0, image_index), self.total_files - 1)
                # Also update the current index to match (for potential future sequential use)
                self.current_index = selected_index
    
            # Step 4: Load and process the selected image
            image_path = self.image_files[selected_index]
            # Log info about the image being loaded (1-based index for user-friendly display)
            print(f"Loading image {selected_index + 1}/{self.total_files}: {image_path}")
    
            # Open the image file using PIL
            image = Image.open(image_path)
            # Apply EXIF orientation correction (e.g., for photos from phones/cameras)
            image = ImageOps.exif_transpose(image)
    
            # Ensure the image is in RGB mode (convert if it's not)
            # This handles grayscale, RGBA, or other color formats
            if image.mode != 'RGB':
                image = image.convert('RGB')
    
            # Convert the PIL image to a tensor in the format ComfyUI expects
            tensor_image = pil2tensor(image)
    
            # Return the image tensor and metadata
            return (tensor_image, self.total_files, selected_index)
    
        except Exception as e:
            # Comprehensive error handling to prevent workflow crashes
            print(f"Error loading image: {e}")
            # Print full stack trace for debugging
            import traceback
            traceback.print_exc()
            # Return a fallback empty image on error
            return (create_empty_image(), 0, 0)

    @staticmethod
    def IS_CHANGED(**kwargs):
        """
        Control when ComfyUI should re-execute this node.
        
        This method is called by ComfyUI to determine if the node's output has
        potentially changed and should be re-executed.
        
        By returning float("NaN") (Not a Number), we're telling ComfyUI that
        this node's output cannot be predicted without execution. This ensures
        that in sequential mode, the node will execute each time and advance
        to the next image.
        
        Returns:
            float: NaN to indicate the node should always be considered changed
        """
        return float("NaN")