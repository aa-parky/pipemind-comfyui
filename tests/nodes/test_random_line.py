"""
Tests for RandomLineFromDropdown node.

This module tests the random line selection functionality including:
- File reading and line selection
- Seed reproducibility
- Edge cases
"""

import pytest
from pipemind_random_line import RandomLineFromDropdown
from tests.conftest import validate_node_structure, validate_node_inputs, validate_node_outputs


class TestRandomLineFromDropdown:
    """Test suite for RandomLineFromDropdown node."""

    @pytest.fixture
    def node(self):
        """Create a node instance for testing."""
        return RandomLineFromDropdown()

    @pytest.mark.unit
    def test_node_structure(self):
        """Test that the node has the correct structure."""
        validate_node_structure(RandomLineFromDropdown)

    @pytest.mark.unit
    def test_input_types(self):
        """Test that INPUT_TYPES returns correct structure."""
        inputs = validate_node_inputs(RandomLineFromDropdown)

        # Check required inputs
        assert "text_file" in inputs["required"]
        assert "seed" in inputs["required"]

    @pytest.mark.unit
    def test_category(self):
        """Test that the node is in the correct category."""
        assert "Pipemind" in RandomLineFromDropdown.CATEGORY

    @pytest.mark.unit
    def test_return_types(self):
        """Test that return types are correct."""
        assert "STRING" in RandomLineFromDropdown.RETURN_TYPES

    @pytest.mark.unit
    @pytest.mark.text
    def test_random_line_selection(self, node, sample_text_file):
        """Test that a random line is selected from file."""
        result = node.get_random_line(
            text_file=str(sample_text_file),
            seed=42
        )

        # Check that we got a tuple with a string
        assert isinstance(result, tuple)
        assert len(result) >= 1
        line = result[0]
        assert isinstance(line, str)
        assert len(line) > 0

    @pytest.mark.unit
    @pytest.mark.text
    def test_seed_reproducibility(self, node, sample_text_file):
        """Test that same seed produces same result."""
        seed = 12345

        result1 = node.get_random_line(str(sample_text_file), seed)
        result2 = node.get_random_line(str(sample_text_file), seed)

        assert result1 == result2

    @pytest.mark.unit
    @pytest.mark.text
    def test_different_seeds(self, node, sample_text_file):
        """Test that different seeds can produce different results."""
        results = []
        for seed in range(100):
            result = node.get_random_line(str(sample_text_file), seed)
            results.append(result[0])

        # With 10 lines and 100 attempts, we should see some variety
        # (unless we're extremely unlucky)
        unique_results = set(results)
        assert len(unique_results) > 1, "Should get different lines with different seeds"

    @pytest.mark.unit
    @pytest.mark.text
    def test_output_from_file(self, node, sample_text_file):
        """Test that output is actually from the file."""
        # Read the file to get expected lines
        with open(sample_text_file, 'r') as f:
            file_lines = [line.strip() for line in f.readlines() if line.strip()]

        # Get a random line
        result = node.get_random_line(str(sample_text_file), seed=42)
        line = result[0]

        # Check that the line is from the file
        assert line in file_lines, "Output should be a line from the file"

    @pytest.mark.unit
    @pytest.mark.text
    def test_empty_lines_handling(self, node, tmp_path):
        """Test handling of files with empty lines."""
        # Create file with some empty lines
        content = """Line 1

Line 3

Line 5"""
        file_path = tmp_path / "lines_with_empty.txt"
        file_path.write_text(content)

        # Should still work
        result = node.get_random_line(str(file_path), seed=42)
        assert isinstance(result[0], str)

    @pytest.mark.unit
    @pytest.mark.text
    def test_single_line_file(self, node, tmp_path):
        """Test file with only one line."""
        content = "Only one line"
        file_path = tmp_path / "single_line.txt"
        file_path.write_text(content)

        result = node.get_random_line(str(file_path), seed=42)
        # With only one line, it should always return that line
        assert result[0] == content

        # Test with different seeds - should still get same line
        result2 = node.get_random_line(str(file_path), seed=999)
        assert result2[0] == content

    @pytest.mark.smoke
    def test_basic_functionality(self, node, sample_text_file):
        """Quick smoke test for basic functionality."""
        result = node.get_random_line(str(sample_text_file), seed=42)

        # Basic sanity checks
        assert result is not None
        assert isinstance(result, tuple)
        assert len(result) >= 1
        assert isinstance(result[0], str)
        assert len(result[0]) > 0

    @pytest.mark.unit
    @pytest.mark.parametrize("seed", [0, 1, 42, 100, 999, 12345])
    def test_various_seeds(self, node, sample_text_file, seed):
        """Test that node works with various seed values."""
        result = node.get_random_line(str(sample_text_file), seed)

        assert isinstance(result, tuple)
        assert isinstance(result[0], str)
        assert len(result[0]) > 0
