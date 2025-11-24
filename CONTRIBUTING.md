# Contributing to Pipemind ComfyUI Custom Nodes

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the best outcome for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.12.12 or higher
- ComfyUI installed and working
- Git for version control
- Basic understanding of ComfyUI custom node architecture

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/pipemind-comfyui.git
   cd pipemind-comfyui
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/aa-parky/pipemind-comfyui.git
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a development branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🔄 Development Workflow

### Branch Strategy

- `master` - Stable releases only
- `develop` - Active development branch
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Critical fixes for production

### Workflow Steps

1. **Sync with upstream**:
   ```bash
   git checkout develop
   git fetch upstream
   git merge upstream/develop
   ```

2. **Create your feature branch**:
   ```bash
   git checkout -b feature/my-new-node
   ```

3. **Make your changes** following the coding standards below

4. **Test your changes** in ComfyUI:
   - Load ComfyUI and verify your node appears
   - Test all functionality
   - Check for errors in console

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: New aspect ratio node for Model X"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/my-new-node
   ```

7. **Create a Pull Request** from your fork to `upstream/develop`

## 💻 Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable and function names

### Node Structure

All nodes should follow this structure:

```python
class PipemindYourNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Your required inputs
            },
            "optional": {
                # Your optional inputs
            }
        }

    RETURN_TYPES = ("TYPE1", "TYPE2",)
    RETURN_NAMES = ("output1", "output2",)
    FUNCTION = "your_function_name"
    CATEGORY = "Pipemind/YourCategory"

    def your_function_name(self, input1, input2):
        # Your implementation
        return (output1, output2,)
```

### Naming Conventions

- **File names**: `pipemind_your_node_name.py`
- **Class names**: `PipemindYourNodeName` (PascalCase)
- **Function names**: `your_function_name` (snake_case)
- **Constants**: `YOUR_CONSTANT` (UPPER_SNAKE_CASE)

### Documentation

- Add docstrings to all classes and methods
- Include inline comments for complex logic
- Update README.md with new node documentation
- Update CHANGELOG.md with your changes

### Example Docstring

```python
class PipemindYourNode:
    """
    A node that does something specific.

    This node takes input X and produces output Y by performing Z operation.
    Useful for workflows that require ABC functionality.
    """

    def your_function(self, input_param):
        """
        Process the input and return the result.

        Args:
            input_param (str): Description of the parameter

        Returns:
            tuple: (output1, output2) where output1 is...
        """
        # Implementation
        pass
```

## 📝 Submitting Changes

### Pull Request Guidelines

1. **Title Format**:
   - `Add: Description` for new features
   - `Fix: Description` for bug fixes
   - `Update: Description` for improvements
   - `Docs: Description` for documentation

2. **Description Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tested in ComfyUI
   - [ ] No console errors
   - [ ] Works with existing workflows

   ## Screenshots (if applicable)
   Add screenshots showing the node in action
   ```

3. **Checklist**:
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] No breaking changes (or documented if necessary)
   - [ ] Tested in ComfyUI

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

- Check existing issues to avoid duplicates
- Verify the bug with the latest version
- Test with a minimal workflow to isolate the issue

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Load node '...'
2. Set parameters '...'
3. Execute workflow
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- ComfyUI Version: [e.g., latest]
- Python Version: [e.g., 3.12.12]
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Pipemind Nodes Version: [e.g., 0.2.0]

**Error Log**
```
Paste relevant error messages here
```

**Additional context**
Any other relevant information.
```

## 💡 Suggesting Enhancements

### Enhancement Proposal Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Use Case**
Describe the workflow or use case for this feature.

**Additional context**
Add any other context or screenshots.
```

## 🔍 Code Review Process

1. Maintainers review PRs within 3-5 days
2. Feedback is provided via PR comments
3. Address review comments and push updates
4. Once approved, maintainer will merge
5. Your contribution will be included in the next release

## 📦 Release Process

- Releases follow [Semantic Versioning](https://semver.org/)
- CHANGELOG.md is updated with each release
- Contributors are credited in release notes

## ❓ Questions?

- Open a [Discussion](https://github.com/aa-parky/pipemind-comfyui/discussions)
- Ask in the [Issues](https://github.com/aa-parky/pipemind-comfyui/issues) if bug-related

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Coding!** 🧵
