"""
Tests for PipemindQwenAspectRatio node.

This module tests the Qwen aspect ratio node functionality including:
- Preset resolutions
- Landscape/Portrait modes
- Manual input handling
"""

import pytest
from pipemind_qwen_aspect_ratio import PipemindQwenAspectRatio
from tests.conftest import validate_node_structure, validate_node_inputs, validate_node_outputs


class TestPipemindQwenAspectRatio:
    """Test suite for PipemindQwenAspectRatio node."""

    @pytest.fixture
    def node(self):
        """Create a node instance for testing."""
        return PipemindQwenAspectRatio()

    @pytest.mark.unit
    def test_node_structure(self, node):
        """Test that the node has the correct structure."""
        validate_node_structure(PipemindQwenAspectRatio)

    @pytest.mark.unit
    def test_input_types(self):
        """Test that INPUT_TYPES returns correct structure."""
        inputs = validate_node_inputs(PipemindQwenAspectRatio)

        # Check required inputs
        assert "mode" in inputs["required"]
        assert "preset" in inputs["required"]
        assert "manual_width" in inputs["required"]
        assert "manual_height" in inputs["required"]

        # Check mode options
        mode_options = inputs["required"]["mode"][0]
        assert "Landscape" in mode_options
        assert "Portrait" in mode_options
        assert "Manual" in mode_options

    @pytest.mark.unit
    def test_category(self):
        """Test that the node is in the correct category."""
        assert PipemindQwenAspectRatio.CATEGORY == "Pipemind/Resolution"

    @pytest.mark.unit
    def test_return_types(self):
        """Test that return types are correct."""
        assert PipemindQwenAspectRatio.RETURN_TYPES == ("INT", "INT",)
        assert PipemindQwenAspectRatio.RETURN_NAMES == ("width", "height",)

    @pytest.mark.unit
    @pytest.mark.aspect_ratio
    def test_landscape_1_1_preset(self, node):
        """Test 1:1 landscape preset."""
        width, height = node.select_resolution(
            mode="Landscape",
            preset="1:1 (1328x1328)",
            manual_width=512,
            manual_height=512
        )

        assert width == 1328
        assert height == 1328
        validate_node_outputs(PipemindQwenAspectRatio, (width, height))

    @pytest.mark.unit
    @pytest.mark.aspect_ratio
    def test_landscape_16_9_preset(self, node):
        """Test 16:9 landscape preset."""
        width, height = node.select_resolution(
            mode="Landscape",
            preset="16:9 (1664x928)",
            manual_width=512,
            manual_height=512
        )

        assert width == 1664
        assert height == 928

    @pytest.mark.unit
    @pytest.mark.aspect_ratio
    def test_portrait_16_9_preset(self, node):
        """Test 16:9 portrait preset (should swap dimensions)."""
        width, height = node.select_resolution(
            mode="Portrait",
            preset="16:9 (1664x928)",
            manual_width=512,
            manual_height=512
        )

        # In portrait mode, dimensions should be swapped
        assert width == 928
        assert height == 1664

    @pytest.mark.unit
    @pytest.mark.aspect_ratio
    def test_portrait_4_3_preset(self, node):
        """Test 4:3 portrait preset."""
        width, height = node.select_resolution(
            mode="Portrait",
            preset="4:3 (1472x1140)",
            manual_width=512,
            manual_height=512
        )

        # In portrait mode, dimensions should be swapped
        assert width == 1140
        assert height == 1472

    @pytest.mark.unit
    @pytest.mark.aspect_ratio
    def test_portrait_3_2_preset(self, node):
        """Test 3:2 portrait preset."""
        width, height = node.select_resolution(
            mode="Portrait",
            preset="3:2 (1584x1056)",
            manual_width=512,
            manual_height=512
        )

        # In portrait mode, dimensions should be swapped
        assert width == 1056
        assert height == 1584

    @pytest.mark.unit
    def test_manual_mode(self, node):
        """Test manual mode with custom dimensions."""
        width, height = node.select_resolution(
            mode="Manual",
            preset="1:1 (1328x1328)",  # Should be ignored
            manual_width=2048,
            manual_height=1024
        )

        assert width == 2048
        assert height == 1024

    @pytest.mark.unit
    def test_manual_preset(self, node):
        """Test manual preset regardless of mode."""
        width, height = node.select_resolution(
            mode="Landscape",  # Should be ignored when preset is Manual
            preset="Manual",
            manual_width=1920,
            manual_height=1080
        )

        assert width == 1920
        assert height == 1080

    @pytest.mark.unit
    @pytest.mark.parametrize("preset,expected", [
        ("1:1 (1328x1328)", (1328, 1328)),
        ("16:9 (1664x928)", (1664, 928)),
        ("4:3 (1472x1140)", (1472, 1140)),
        ("3:2 (1584x1056)", (1584, 1056)),
    ])
    def test_all_landscape_presets(self, node, preset, expected):
        """Test all landscape presets parametrically."""
        width, height = node.select_resolution(
            mode="Landscape",
            preset=preset,
            manual_width=512,
            manual_height=512
        )

        assert (width, height) == expected

    @pytest.mark.unit
    def test_output_is_tuple(self, node):
        """Test that output is always a tuple."""
        result = node.select_resolution(
            mode="Landscape",
            preset="1:1 (1328x1328)",
            manual_width=512,
            manual_height=512
        )

        assert isinstance(result, tuple)
        assert len(result) == 2

    @pytest.mark.smoke
    def test_basic_functionality(self, node):
        """Quick smoke test for basic functionality."""
        # Test that node can be instantiated and called
        result = node.select_resolution(
            mode="Landscape",
            preset="1:1 (1328x1328)",
            manual_width=512,
            manual_height=512
        )

        # Basic sanity checks
        assert result is not None
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)
        assert all(x > 0 for x in result)
