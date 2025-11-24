"""
Tests for BooleanSwitchAny node.

This module tests the boolean switch functionality including:
- Switching between two inputs based on boolean
- Handling different data types
- Input/output validation
"""

import pytest
from pipemind_boolean_switch_any import BooleanSwitchAny
from tests.conftest import validate_node_structure, validate_node_inputs, validate_node_outputs


class TestBooleanSwitchAny:
    """Test suite for BooleanSwitchAny node."""

    @pytest.fixture
    def node(self):
        """Create a node instance for testing."""
        return BooleanSwitchAny()

    @pytest.mark.unit
    def test_node_structure(self):
        """Test that the node has the correct structure."""
        validate_node_structure(BooleanSwitchAny)

    @pytest.mark.unit
    def test_input_types(self):
        """Test that INPUT_TYPES returns correct structure."""
        inputs = validate_node_inputs(BooleanSwitchAny)

        # Check required inputs
        assert "boolean" in inputs["required"]
        assert "on_true" in inputs["required"]
        assert "on_false" in inputs["required"]

        # Check that inputs accept any type
        assert inputs["required"]["on_true"][0] == "*"
        assert inputs["required"]["on_false"][0] == "*"

    @pytest.mark.unit
    def test_category(self):
        """Test that the node is in the correct category."""
        assert BooleanSwitchAny.CATEGORY == "Pipemind/Logic"

    @pytest.mark.unit
    def test_return_types(self):
        """Test that return types are correct."""
        assert BooleanSwitchAny.RETURN_TYPES == ("*",)

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_true_strings(self, node):
        """Test switching with boolean True and string inputs."""
        result = node.switch(
            boolean=True,
            on_true="value_true",
            on_false="value_false"
        )

        output = result[0]
        assert output == "value_true"
        validate_node_outputs(BooleanSwitchAny, result)

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_false_strings(self, node):
        """Test switching with boolean False and string inputs."""
        result = node.switch(
            boolean=False,
            on_true="value_true",
            on_false="value_false"
        )

        output = result[0]
        assert output == "value_false"

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_true_integers(self, node):
        """Test switching with integer inputs."""
        result = node.switch(
            boolean=True,
            on_true=42,
            on_false=99
        )

        output = result[0]
        assert output == 42

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_false_integers(self, node):
        """Test switching with integer inputs."""
        result = node.switch(
            boolean=False,
            on_true=42,
            on_false=99
        )

        output = result[0]
        assert output == 99

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_lists(self, node):
        """Test switching with list inputs."""
        list_true = [1, 2, 3]
        list_false = [4, 5, 6]

        result_true = node.switch(boolean=True, on_true=list_true, on_false=list_false)
        result_false = node.switch(boolean=False, on_true=list_true, on_false=list_false)

        assert result_true[0] == list_true
        assert result_false[0] == list_false

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_dicts(self, node):
        """Test switching with dictionary inputs."""
        dict_true = {"key": "true"}
        dict_false = {"key": "false"}

        result_true = node.switch(boolean=True, on_true=dict_true, on_false=dict_false)
        result_false = node.switch(boolean=False, on_true=dict_true, on_false=dict_false)

        assert result_true[0] == dict_true
        assert result_false[0] == dict_false

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_none(self, node):
        """Test switching with None values."""
        result_true = node.switch(boolean=True, on_true=None, on_false="value")
        result_false = node.switch(boolean=False, on_true="value", on_false=None)

        assert result_true[0] is None
        assert result_false[0] is None

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_mixed_types(self, node):
        """Test switching with different types for true/false branches."""
        result = node.switch(
            boolean=True,
            on_true="string",
            on_false=123
        )

        assert result[0] == "string"
        assert isinstance(result[0], str)

        result = node.switch(
            boolean=False,
            on_true="string",
            on_false=123
        )

        assert result[0] == 123
        assert isinstance(result[0], int)

    @pytest.mark.unit
    @pytest.mark.parametrize("boolean,true_val,false_val", [
        (True, "a", "b"),
        (False, "a", "b"),
        (True, 1, 2),
        (False, 1, 2),
        (True, [1, 2], [3, 4]),
        (False, [1, 2], [3, 4]),
    ])
    def test_switch_parametric(self, node, boolean, true_val, false_val):
        """Test switching with various parameter combinations."""
        result = node.switch(boolean=boolean, on_true=true_val, on_false=false_val)
        expected = true_val if boolean else false_val
        assert result[0] == expected

    @pytest.mark.unit
    def test_output_is_tuple(self, node):
        """Test that output is always a tuple."""
        result = node.switch(boolean=True, on_true="a", on_false="b")

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.smoke
    def test_basic_functionality(self, node):
        """Quick smoke test for basic functionality."""
        # Test basic switching
        result_true = node.switch(boolean=True, on_true="yes", on_false="no")
        result_false = node.switch(boolean=False, on_true="yes", on_false="no")

        assert result_true[0] == "yes"
        assert result_false[0] == "no"
