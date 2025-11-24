"""
Pytest configuration and fixtures for Pipemind ComfyUI node tests.

This module provides common fixtures and utilities for testing ComfyUI custom nodes.
"""

import os
import sys
import pytest
from pathlib import Path

# Add parent directory to path so we can import the nodes
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_text_file(tmp_path):
    """
    Create a temporary text file with sample lines for testing.

    Args:
        tmp_path: Pytest fixture providing temporary directory

    Returns:
        Path: Path to the created text file
    """
    content = """Line 1: First line
Line 2: Second line
Line 3: Third line
Line 4: Fourth line
Line 5: Fifth line
Line 6: Sixth line
Line 7: Seventh line
Line 8: Eighth line
Line 9: Ninth line
Line 10: Tenth line"""

    file_path = tmp_path / "test_lines.txt"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_prompt_file(tmp_path):
    """
    Create a temporary prompt file for testing.

    Args:
        tmp_path: Pytest fixture providing temporary directory

    Returns:
        Path: Path to the created prompt file
    """
    prompts = """a beautiful landscape
a portrait of a person
an abstract artwork
a futuristic cityscape
a cozy interior scene"""

    file_path = tmp_path / "prompts.txt"
    file_path.write_text(prompts)
    return file_path


@pytest.fixture
def aspect_ratio_presets():
    """
    Provide common aspect ratio presets for testing.

    Returns:
        dict: Dictionary of aspect ratio presets with their dimensions
    """
    return {
        "flux": {
            "1:1": (1408, 1408),
            "3:2": (1728, 1152),
            "4:3": (1664, 1216),
            "16:9": (1920, 1088),
            "21:9": (2176, 960),
        },
        "qwen": {
            "1:1": (1328, 1328),
            "16:9": (1664, 928),
            "4:3": (1472, 1140),
            "3:2": (1584, 1056),
        },
        "sdxl": {
            # Add SDXL presets as needed
        }
    }


@pytest.fixture
def mock_comfyui_context():
    """
    Mock ComfyUI context for testing nodes that depend on ComfyUI infrastructure.

    Returns:
        dict: Mock context dictionary
    """
    return {
        "folder_paths": {},
        "server": None,
        "prompt_id": "test_prompt_id",
    }


def validate_node_structure(node_class):
    """
    Validate that a node class follows the correct ComfyUI structure.

    Args:
        node_class: The node class to validate

    Returns:
        bool: True if valid, raises AssertionError otherwise
    """
    # Check required class methods
    assert hasattr(node_class, 'INPUT_TYPES'), "Node must have INPUT_TYPES classmethod"
    assert callable(node_class.INPUT_TYPES), "INPUT_TYPES must be callable"

    # Check required class attributes
    assert hasattr(node_class, 'RETURN_TYPES'), "Node must have RETURN_TYPES"
    assert hasattr(node_class, 'FUNCTION'), "Node must have FUNCTION"
    assert hasattr(node_class, 'CATEGORY'), "Node must have CATEGORY"

    # Check that FUNCTION references an actual method
    function_name = node_class.FUNCTION
    assert hasattr(node_class, function_name), f"Node must have method '{function_name}'"

    return True


def validate_node_inputs(node_class):
    """
    Validate that INPUT_TYPES returns the correct structure.

    Args:
        node_class: The node class to validate

    Returns:
        dict: The INPUT_TYPES dictionary if valid
    """
    inputs = node_class.INPUT_TYPES()

    assert isinstance(inputs, dict), "INPUT_TYPES must return a dictionary"
    assert "required" in inputs or "optional" in inputs, \
        "INPUT_TYPES must have 'required' or 'optional' key"

    return inputs


def validate_node_outputs(node_class, output):
    """
    Validate that node output matches RETURN_TYPES.

    Args:
        node_class: The node class being tested
        output: The actual output from the node

    Returns:
        bool: True if valid, raises AssertionError otherwise
    """
    expected_count = len(node_class.RETURN_TYPES)

    assert isinstance(output, tuple), "Node output must be a tuple"
    assert len(output) == expected_count, \
        f"Expected {expected_count} outputs, got {len(output)}"

    return True


# Export validation helpers
__all__ = [
    'sample_text_file',
    'sample_prompt_file',
    'aspect_ratio_presets',
    'mock_comfyui_context',
    'validate_node_structure',
    'validate_node_inputs',
    'validate_node_outputs',
]
