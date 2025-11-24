# Testing Guide

This directory contains the test suite for Pipemind ComfyUI Custom Nodes.

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=html --cov-report=term
```

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and utilities
├── nodes/                   # Tests for individual nodes
│   ├── test_qwen_aspect_ratio.py
│   ├── test_boolean_switch.py
│   └── test_random_line.py
└── utils/                   # Tests for utility functions
```

## 🏷️ Test Categories (Markers)

Tests are organized using pytest markers:

### Run Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run smoke tests (quick validation)
pytest -m smoke

# Run slow tests
pytest -m slow
```

### Available Markers

- `unit` - Unit tests for individual node functions
- `integration` - Integration tests requiring ComfyUI
- `slow` - Tests that take longer to run
- `smoke` - Quick smoke tests for basic functionality
- `aspect_ratio` - Tests for aspect ratio nodes
- `text` - Tests for text processing nodes
- `image` - Tests for image processing nodes
- `prompt` - Tests for prompt composition nodes
- `utility` - Tests for utility nodes

## 🎯 Running Specific Tests

### Run Tests for a Specific Node

```bash
pytest tests/nodes/test_qwen_aspect_ratio.py
```

### Run a Specific Test Class

```bash
pytest tests/nodes/test_qwen_aspect_ratio.py::TestPipemindQwenAspectRatio
```

### Run a Specific Test Method

```bash
pytest tests/nodes/test_qwen_aspect_ratio.py::TestPipemindQwenAspectRatio::test_landscape_1_1_preset
```

### Run Tests Matching a Pattern

```bash
# Run all tests with "aspect" in the name
pytest -k aspect

# Run all tests with "landscape" in the name
pytest -k landscape
```

## ⚡ Parallel Testing

Run tests in parallel for faster execution:

```bash
# Run with 4 parallel workers
pytest -n 4

# Run with auto-detected number of CPUs
pytest -n auto
```

## 📊 Coverage Reports

Generate coverage reports to see which code is tested:

```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# Open the report (Linux/Mac)
open htmlcov/index.html

# Open the report (Windows)
start htmlcov/index.html
```

## ✍️ Writing New Tests

### Test File Naming

- Place test files in `tests/nodes/` for node tests
- Name test files as `test_<node_name>.py`
- Use `test_<feature>.py` for utility/integration tests

### Test Class Structure

```python
import pytest
from your_node import YourNode
from tests.conftest import validate_node_structure

class TestYourNode:
    """Test suite for YourNode."""

    @pytest.fixture
    def node(self):
        """Create a node instance for testing."""
        return YourNode()

    @pytest.mark.unit
    def test_node_structure(self):
        """Test that the node has the correct structure."""
        validate_node_structure(YourNode)

    @pytest.mark.unit
    def test_basic_functionality(self, node):
        """Test basic node functionality."""
        result = node.your_function(param1="value")
        assert result is not None
```

### Using Fixtures

Common fixtures are available in `conftest.py`:

- `sample_text_file` - Temporary text file with sample lines
- `sample_prompt_file` - Temporary prompt file
- `aspect_ratio_presets` - Dictionary of aspect ratio presets
- `mock_comfyui_context` - Mock ComfyUI context

### Validation Helpers

Use the validation helpers from `conftest.py`:

```python
from tests.conftest import (
    validate_node_structure,
    validate_node_inputs,
    validate_node_outputs
)

# Validate node structure
validate_node_structure(YourNode)

# Validate inputs
inputs = validate_node_inputs(YourNode)

# Validate outputs
validate_node_outputs(YourNode, output_tuple)
```

## 🔍 Test Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Use Fixtures**: Leverage pytest fixtures for setup/teardown
3. **Parametrize**: Use `@pytest.mark.parametrize` for testing multiple inputs
4. **Mark Tests**: Use markers to categorize tests
5. **Clear Names**: Use descriptive test names that explain what's being tested
6. **Assert Messages**: Include helpful messages in assertions
7. **Test Edge Cases**: Include tests for edge cases and error conditions

## 🐛 Debugging Tests

### Run with Print Statements

```bash
pytest -s  # Don't capture output
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Show Local Variables on Failure

```bash
pytest -l
```

## 📝 Continuous Integration

Tests are automatically run on:
- Every pull request
- Every commit to `master` and `develop` branches

Ensure all tests pass before submitting a PR.

## ❓ Questions?

- Review existing tests for examples
- Check [pytest documentation](https://docs.pytest.org/)
- Ask in [GitHub Discussions](https://github.com/aa-parky/pipemind-comfyui/discussions)
