"""
Tests for BooleanSwitchAny node.

This module tests the boolean switch functionality including:
- Switching between two inputs based on the `switch` boolean
- Pass-through of arbitrary values (implementation is type-agnostic)
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
        assert "switch" in inputs["required"]
        assert "on_true" in inputs["required"]
        assert "on_false" in inputs["required"]

        # Branch inputs are string sockets (connection-only)
        assert inputs["required"]["on_true"][0] == "STRING"
        assert inputs["required"]["on_true"][1]["forceInput"] is True
        assert inputs["required"]["on_false"][0] == "STRING"
        assert inputs["required"]["on_false"][1]["forceInput"] is True

        # The switch is a boolean widget defaulting to True
        assert inputs["required"]["switch"][0] == "BOOLEAN"
        assert inputs["required"]["switch"][1]["default"] is True

    @pytest.mark.unit
    def test_category(self):
        """Test that the node is in the correct category."""
        assert BooleanSwitchAny.CATEGORY == "Pipemind/Switch"

    @pytest.mark.unit
    def test_return_types(self):
        """Test that return types are correct."""
        assert BooleanSwitchAny.RETURN_TYPES == ("STRING",)
        assert BooleanSwitchAny.RETURN_NAMES == ("result",)

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_true_strings(self, node):
        """Test switching with switch=True and string inputs."""
        result = node.switch(
            on_true="value_true",
            on_false="value_false",
            switch=True,
        )

        output = result[0]
        assert output == "value_true"
        validate_node_outputs(BooleanSwitchAny, result)

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_false_strings(self, node):
        """Test switching with switch=False and string inputs."""
        result = node.switch(
            on_true="value_true",
            on_false="value_false",
            switch=False,
        )

        output = result[0]
        assert output == "value_false"

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_defaults_to_true(self, node):
        """Test that the switch parameter defaults to True."""
        result = node.switch(on_true="yes", on_false="no")
        assert result[0] == "yes"

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_passthrough_integers(self, node):
        """Non-string values pass through unchanged (type-agnostic impl)."""
        assert node.switch(on_true=42, on_false=99, switch=True)[0] == 42
        assert node.switch(on_true=42, on_false=99, switch=False)[0] == 99

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_lists(self, node):
        """Test switching with list inputs."""
        list_true = [1, 2, 3]
        list_false = [4, 5, 6]

        result_true = node.switch(on_true=list_true, on_false=list_false, switch=True)
        result_false = node.switch(on_true=list_true, on_false=list_false, switch=False)

        assert result_true[0] == list_true
        assert result_false[0] == list_false

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_dicts(self, node):
        """Test switching with dictionary inputs."""
        dict_true = {"key": "true"}
        dict_false = {"key": "false"}

        result_true = node.switch(on_true=dict_true, on_false=dict_false, switch=True)
        result_false = node.switch(on_true=dict_true, on_false=dict_false, switch=False)

        assert result_true[0] == dict_true
        assert result_false[0] == dict_false

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_none(self, node):
        """Test switching with None values."""
        result_true = node.switch(on_true=None, on_false="value", switch=True)
        result_false = node.switch(on_true="value", on_false=None, switch=False)

        assert result_true[0] is None
        assert result_false[0] is None

    @pytest.mark.unit
    @pytest.mark.utility
    def test_switch_with_mixed_types(self, node):
        """Test switching with different types for true/false branches."""
        result = node.switch(on_true="string", on_false=123, switch=True)
        assert result[0] == "string"
        assert isinstance(result[0], str)

        result = node.switch(on_true="string", on_false=123, switch=False)
        assert result[0] == 123
        assert isinstance(result[0], int)

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "switch,true_val,false_val",
        [
            (True, "a", "b"),
            (False, "a", "b"),
            (True, 1, 2),
            (False, 1, 2),
            (True, [1, 2], [3, 4]),
            (False, [1, 2], [3, 4]),
        ],
    )
    def test_switch_parametric(self, node, switch, true_val, false_val):
        """Test switching with various parameter combinations."""
        result = node.switch(on_true=true_val, on_false=false_val, switch=switch)
        expected = true_val if switch else false_val
        assert result[0] == expected

    @pytest.mark.unit
    def test_output_is_tuple(self, node):
        """Test that output is always a tuple."""
        result = node.switch(on_true="a", on_false="b", switch=True)

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.unit
    def test_is_changed_forces_reexecution(self):
        """IS_CHANGED always reports change so the switch re-evaluates."""
        assert BooleanSwitchAny.IS_CHANGED() is True

    @pytest.mark.smoke
    def test_basic_functionality(self, node):
        """Quick smoke test for basic functionality."""
        result_true = node.switch(on_true="yes", on_false="no", switch=True)
        result_false = node.switch(on_true="yes", on_false="no", switch=False)

        assert result_true[0] == "yes"
        assert result_false[0] == "no"
