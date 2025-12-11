"""
Tests for MultiFileKeywordPromptComposer node.

This module tests the multi-file keyword prompt composer functionality including:
- Node structure validation
- Single and multiple keyword data inputs
- Dynamic prompt processing
- Advanced syntax handling
- Placeholder replacement with multiple sources
- Key conflict resolution (last-wins)
"""

import pytest
from pipemind_multifile_composer_node import MultiFileKeywordPromptComposer
from tests.conftest import (
    validate_node_structure,
    validate_node_inputs,
    validate_node_outputs,
)


@pytest.mark.unit
@pytest.mark.prompt
class TestMultiFileKeywordPromptComposer:
    """Test suite for MultiFileKeywordPromptComposer node."""

    def setup_method(self):
        """Set up test fixtures."""
        self.node = MultiFileKeywordPromptComposer()

    @pytest.mark.smoke
    def test_node_structure(self):
        """Test that the node has the correct ComfyUI structure."""
        validate_node_structure(MultiFileKeywordPromptComposer)

    @pytest.mark.smoke
    def test_input_types(self):
        """Test INPUT_TYPES returns correct structure."""
        inputs = validate_node_inputs(MultiFileKeywordPromptComposer)

        # Check required inputs
        assert "prompt_template" in inputs["required"]
        assert "seed" in inputs["required"]

        # Check optional inputs
        assert "optional" in inputs
        assert "keyword_data_1" in inputs["optional"]
        assert "keyword_data_2" in inputs["optional"]
        assert "keyword_data_3" in inputs["optional"]
        assert "keyword_data_4" in inputs["optional"]
        assert "keyword_data_5" in inputs["optional"]

    def test_category(self):
        """Test node category is correct."""
        assert MultiFileKeywordPromptComposer.CATEGORY == "🧵 Pipemind"

    def test_return_types(self):
        """Test node return types are correct."""
        assert MultiFileKeywordPromptComposer.RETURN_TYPES == ("STRING",)
        assert MultiFileKeywordPromptComposer.RETURN_NAMES == ("composed_prompt",)

    def test_single_keyword_input(self):
        """Test composition with single keyword data input."""
        template = "A <adjective> portrait"
        result = self.node.compose_prompt(
            prompt_template=template, seed=-1, keyword_data_1="adjective=beautiful"
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == "A beautiful portrait"

    def test_multiple_keyword_inputs(self):
        """Test composition with multiple keyword data inputs."""
        template = "A <adj> <subject> wearing <clothing>"
        result = self.node.compose_prompt(
            prompt_template=template,
            seed=-1,
            keyword_data_1="adj=beautiful",
            keyword_data_2="subject=woman",
            keyword_data_3="clothing=red dress",
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == "A beautiful woman wearing red dress"

    def test_all_five_inputs(self):
        """Test composition with all 5 keyword data inputs."""
        template = "<word1> <word2> <word3> <word4> <word5>"
        result = self.node.compose_prompt(
            prompt_template=template,
            seed=-1,
            keyword_data_1="word1=first",
            keyword_data_2="word2=second",
            keyword_data_3="word3=third",
            keyword_data_4="word4=fourth",
            keyword_data_5="word5=fifth",
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == "first second third fourth fifth"

    def test_empty_optional_inputs(self):
        """Test that empty optional inputs are handled correctly."""
        template = "A <adjective> portrait"
        result = self.node.compose_prompt(
            prompt_template=template,
            seed=-1,
            keyword_data_1="adjective=stunning",
            keyword_data_2="",
            keyword_data_3="",
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == "A stunning portrait"

    def test_no_keyword_inputs(self):
        """Test template is returned unchanged when no keyword data provided."""
        template = "A <adjective> portrait"
        result = self.node.compose_prompt(prompt_template=template, seed=-1)

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == template

    def test_multiline_keyword_data(self):
        """Test parsing multi-line keyword data."""
        template = "A <adj> <subject> in a <location>"
        multiline_data = "adj=beautiful\nsubject=garden\nlocation=sunset"

        result = self.node.compose_prompt(
            prompt_template=template, seed=-1, keyword_data_1=multiline_data
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == "A beautiful garden in a sunset"

    def test_key_conflict_resolution(self):
        """Test that later inputs override earlier ones for conflicting keys."""
        template = "A <color> rose"
        result = self.node.compose_prompt(
            prompt_template=template,
            seed=-1,
            keyword_data_1="color=red",
            keyword_data_2="color=blue",
            keyword_data_3="color=yellow",
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        # Last one should win
        assert result[0] == "A yellow rose"

    def test_dynamic_prompts_simple(self):
        """Test simple dynamic prompt syntax."""
        template = "A portrait with {blue|green|red} eyes"
        result = self.node.compose_prompt(prompt_template=template, seed=42)

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        # With seed 42, should be deterministic
        assert "eyes" in result[0]
        assert result[0] in [
            "A portrait with blue eyes",
            "A portrait with green eyes",
            "A portrait with red eyes",
        ]

    def test_dynamic_prompts_deterministic(self):
        """Test that dynamic prompts are deterministic with same seed."""
        template = "A {beautiful|stunning|gorgeous} portrait"

        result1 = self.node.compose_prompt(prompt_template=template, seed=123)
        result2 = self.node.compose_prompt(prompt_template=template, seed=123)

        validate_node_outputs(MultiFileKeywordPromptComposer, result1)
        validate_node_outputs(MultiFileKeywordPromptComposer, result2)
        assert result1[0] == result2[0]

    def test_dynamic_prompts_different_seeds(self):
        """Test that different seeds can produce different results."""
        template = "A {option1|option2|option3|option4|option5} test"

        results = set()
        for seed in range(100):
            result = self.node.compose_prompt(prompt_template=template, seed=seed)
            results.add(result[0])

        # Should have multiple different results
        assert len(results) > 1

    def test_advanced_syntax(self):
        """Test advanced dynamic prompt syntax."""
        template = "Keywords: {2$$ and $$red|blue|green|yellow}"
        result = self.node.compose_prompt(prompt_template=template, seed=42)

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert "Keywords:" in result[0]
        assert " and " in result[0]

    def test_combined_dynamic_and_keywords(self):
        """Test combining dynamic prompts with keyword replacement."""
        template = "A {beautiful|stunning} <subject> with {blue|green} eyes"
        result = self.node.compose_prompt(
            prompt_template=template, seed=42, keyword_data_1="subject=warrior"
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert "warrior" in result[0]
        assert "eyes" in result[0]

    def test_parse_keyword_data_single_line(self):
        """Test parsing single-line keyword data."""
        data = "key=value"
        parsed = self.node._parse_keyword_data(data)

        assert parsed == {"key": "value"}

    def test_parse_keyword_data_multiline(self):
        """Test parsing multi-line keyword data."""
        data = "key1=value1\nkey2=value2\nkey3=value3"
        parsed = self.node._parse_keyword_data(data)

        assert parsed == {"key1": "value1", "key2": "value2", "key3": "value3"}

    def test_parse_keyword_data_with_spaces(self):
        """Test parsing keyword data with extra spaces."""
        data = "  key = value  "
        parsed = self.node._parse_keyword_data(data)

        assert parsed == {"key": "value"}

    def test_parse_keyword_data_empty(self):
        """Test parsing empty keyword data."""
        assert self.node._parse_keyword_data("") == {}
        assert self.node._parse_keyword_data(None) == {}

    def test_parse_keyword_data_invalid_lines(self):
        """Test that invalid lines are skipped."""
        data = "key1=value1\ninvalid line\nkey2=value2"
        parsed = self.node._parse_keyword_data(data)

        assert parsed == {"key1": "value1", "key2": "value2"}

    def test_parse_keyword_data_value_with_equals(self):
        """Test parsing values that contain equals signs."""
        data = "url=https://example.com?param=value"
        parsed = self.node._parse_keyword_data(data)

        assert parsed == {"url": "https://example.com?param=value"}

    def test_merge_keyword_dicts(self):
        """Test merging multiple keyword dictionaries."""
        dict1 = {"a": "1", "b": "2"}
        dict2 = {"c": "3", "d": "4"}
        dict3 = {"b": "5", "e": "6"}

        merged = self.node._merge_keyword_dicts(dict1, dict2, dict3)

        # Later dicts should override earlier ones
        assert merged == {"a": "1", "b": "5", "c": "3", "d": "4", "e": "6"}

    def test_merge_keyword_dicts_empty(self):
        """Test merging with empty dictionaries."""
        dict1 = {"a": "1"}
        dict2 = {}
        dict3 = {"b": "2"}

        merged = self.node._merge_keyword_dicts(dict1, dict2, dict3)

        assert merged == {"a": "1", "b": "2"}

    def test_replace_placeholders(self):
        """Test placeholder replacement."""
        text = "A <adj> <subject> in <location>"
        keywords = {"adj": "beautiful", "subject": "garden", "location": "spring"}

        result = self.node._replace_placeholders(text, keywords)

        assert result == "A beautiful garden in spring"

    def test_replace_placeholders_missing_keys(self):
        """Test that missing placeholders remain unchanged."""
        text = "A <adj> <subject>"
        keywords = {"adj": "beautiful"}

        result = self.node._replace_placeholders(text, keywords)

        assert result == "A beautiful <subject>"

    def test_replace_placeholders_no_placeholders(self):
        """Test text without placeholders."""
        text = "A simple text"
        keywords = {"key": "value"}

        result = self.node._replace_placeholders(text, keywords)

        assert result == "A simple text"

    def test_output_is_tuple(self):
        """Test that output is always a tuple."""
        result = self.node.compose_prompt(prompt_template="test", seed=-1)

        assert isinstance(result, tuple)
        assert len(result) == 1

    @pytest.mark.smoke
    def test_basic_functionality(self):
        """Smoke test for basic node functionality."""
        template = "A <style> portrait of a <subject>"
        result = self.node.compose_prompt(
            prompt_template=template,
            seed=-1,
            keyword_data_1="style=realistic",
            keyword_data_2="subject=warrior",
        )

        assert isinstance(result, tuple)
        assert len(result) == 1
        assert "realistic" in result[0]
        assert "warrior" in result[0]

    def test_complex_workflow_scenario(self):
        """Test a complex real-world scenario with multiple features."""
        template = (
            "{A portrait of|An image of} a <character> "
            "wearing <clothing> in a <location>, "
            "{photorealistic|artistic|stylized} style"
        )

        result = self.node.compose_prompt(
            prompt_template=template,
            seed=42,
            keyword_data_1="character=cyberpunk warrior",
            keyword_data_2="clothing=neon armor",
            keyword_data_3="location=futuristic city",
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        output = result[0]

        # Check all replacements happened
        assert "cyberpunk warrior" in output
        assert "neon armor" in output
        assert "futuristic city" in output
        assert "style" in output

    def test_empty_template(self):
        """Test handling of empty template."""
        result = self.node.compose_prompt(
            prompt_template="", seed=-1, keyword_data_1="key=value"
        )

        validate_node_outputs(MultiFileKeywordPromptComposer, result)
        assert result[0] == ""

    @pytest.mark.parametrize(
        "seed,expected_deterministic",
        [
            (0, True),
            (42, True),
            (12345, True),
            (-1, False),  # -1 means random, not deterministic
        ],
    )
    def test_seed_determinism(self, seed, expected_deterministic):
        """Test that seeds produce deterministic or random results as expected."""
        template = "A {red|blue|green|yellow|purple} flower"

        if expected_deterministic:
            result1 = self.node.compose_prompt(prompt_template=template, seed=seed)
            result2 = self.node.compose_prompt(prompt_template=template, seed=seed)
            assert result1[0] == result2[0]
        else:
            # With -1 seed, we can't guarantee different results,
            # but we can verify it doesn't crash
            result = self.node.compose_prompt(prompt_template=template, seed=seed)
            validate_node_outputs(MultiFileKeywordPromptComposer, result)
            assert "flower" in result[0]
