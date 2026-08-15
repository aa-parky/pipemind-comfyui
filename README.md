# 🧵 Pipemind ComfyUI Custom Nodes

A focused collection of custom nodes for ComfyUI, designed for efficient workflow management without the bloat of large node packs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/tests.yml/badge.svg)](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/tests.yml)
[![Code Quality](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/code-quality.yml/badge.svg)](https://github.com/aa-parky/pipemind-comfyui/actions/workflows/code-quality.yml)
[![codecov](https://codecov.io/gh/aa-parky/pipemind-comfyui/branch/master/graph/badge.svg)](https://codecov.io/gh/aa-parky/pipemind-comfyui)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Node Categories](#node-categories)
- [Requirements](#requirements)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Lightweight**: Minimal dependencies, focused functionality
- **Text Processing**: Advanced file reading and line selection
- **Prompt Tools**: Flexible prompt composition and combination
- **MiniMax H3 Prompting**: Structured prompt assembly, camera/dialogue tagging, and validation for H3 video generation
- **Resolution Helpers**: Aspect ratio presets for Flux, SDXL, and Qwen models
- **Image Batch Processing**: Efficient batch loading and saving
- **Debugging Tools**: Text display and any-type visualization
- **Utilities**: Boolean switches, token counters, LoRA loading

## 🚀 Installation

### Method 1: ComfyUI Manager (Recommended)

1. Install [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
2. Search for "Pipemind" in the manager
3. Click Install

### Method 2: Manual Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aa-parky/pipemind-comfyui.git
cd pipemind-comfyui
pip install -r requirements.txt
```

### Method 3: Git URL in ComfyUI Manager

```
https://github.com/aa-parky/pipemind-comfyui
```

## 📦 Node Categories

### 🔤 Text Processing & File I/O

#### 🧵 Random Line from File (Seeded)
**Node ID**: `RandomLineFromDropdown`
- Randomly selects a line from a text file with seed control
- Perfect for random prompt generation with reproducibility
- Supports custom file paths

#### 🧵 Select Line from TxT (Any)
**Node ID**: `SelectLineFromDropdown`
- Advanced line selection with multiple modes
- Supports line ranges, sequences, and filtering
- Includes search/find functionality
- Outputs selected line and preview

#### 🧵 Load TXT File
**Node ID**: `LoadTxtFile`
- Loads entire text file contents
- Returns as string for further processing

#### 🧵 Multiline Text Input
**Node ID**: `PipemindMultilineTextInput`
- Multi-line text input widget
- Useful for prompt templates and long-form text

---

### ✍️ Prompt Composition

#### 🧵 Keyword Prompt Composer
**Node ID**: `KeywordPromptComposer`
- Compose prompts from keyword categories
- Tag-based organization
- Supports inline tagging

#### 🧵 Enhanced Keyword Composer
**Node ID**: `EnhancedKeywordPromptComposer`
- Extended version of Keyword Composer
- Additional features and options
- More flexible composition modes

#### 🧵 Simple Prompt Combiner (5x)
**Node ID**: `SimplePromptCombiner`
- Combines up to 5 prompts with custom separators
- Clean, straightforward merging
- Optional whitespace handling

---

### 🎬 MiniMax H3 Prompting

Nodes for building well-structured [MiniMax H3](https://docs.comfy.org/tutorials/video/minimax/minimax-h3) audiovisual prompts in the model's preferred tagged format. The family owns the mechanical grammar (alignment lines, `[Shot N]` timestamps, `<d>[Language]` dialogue tags, camera vocabulary) so the prompt text can focus on the creative description.

#### 🧵 MiniMax H3 Prompt Assembler
**Node ID**: `PipemindH3PromptAssembler`
- Assembles complete base-mode prompts (T2VA / I2VA / FL2VA / L2VA)
- Generates the exact mode-specific alignment first line with the effective duration to two decimals
- Snaps frame counts to the model's 17n+5 grid (24 fps)
- `length` INT passthrough keeps the alignment line and the sampler duration in sync — wire it into the MiniMax H3 node's `length` input

#### 🧵 MiniMax H3 Camera Move
**Node ID**: `PipemindH3CameraMove`
- Builds camera sentences from the model's fixed motion vocabulary (Push In, Truck Left, Arc Shot, ...)
- Optional amplitude (small/large) and speed (slow/fast) qualifiers; defaults omit them, matching the guide
- Output fragment feeds the prompt combiners or a `<camera>` placeholder in the Keyword Composer

#### 🧵 MiniMax H3 Dialogue
**Node ID**: `PipemindH3Dialogue`
- Correctly tagged `<d>[Language] ...</d>` dialogue with stable `(S1)` speaker IDs and compound group IDs
- Voiceover mode emits the required "off-screen voiceover" phrase plus the closed-lips clause
- Supports `<cutoff>` (speech truncated by video end) and `<scenetrans>` (line crossing a cut) endings

#### 🧵 MiniMax H3 Prompt Lint
**Node ID**: `PipemindH3PromptLint`
- Validates field structure, shot numbering, cut timestamps, dialogue tags, speaker-ID ordering, and alignment-line/duration agreement
- Warns on description word count outside 350–500 and stray curly braces
- `pass` BOOLEAN output pairs with 🧵 Boolean Switch (Any) to gate queuing on a valid prompt

---

### 📐 Resolution & Aspect Ratios

#### 🧵 Flux 2M Aspect Ratios
**Node ID**: `PipemindFlux2MAspectRatio`
- Optimized presets for Flux.1 models
- Landscape/Portrait/Manual modes
- Presets: 1:1 (1408x1408), 3:2 (1728x1152), 4:3 (1664x1216), 16:9 (1920x1088), 21:9 (2176x960)

#### 🧵 SDXL Aspect Ratios
**Node ID**: `PipemindSDXL15AspectRatio`
- SDXL-optimized resolutions
- Multiple common aspect ratios
- Portrait orientation support

#### 🧵 Qwen Aspect Ratios
**Node ID**: `PipemindQwenAspectRatio`
- Official Qwen-Image resolutions
- Presets: 1:1 (1328x1328), 16:9 (1664x928), 4:3 (1472x1140), 3:2 (1584x1056)
- Landscape/Portrait modes with auto-swap

---

### 🖼️ Image Processing

#### 🧵 Batch Image Loader src Input
**Node ID**: `BatchImageLoadInput`
- Load images from directory as batch
- Source directory input mode
- Maintains batch structure

#### 🧵 Batch Image Loader src Output
**Node ID**: `BatchImageLoadOutput`
- Complementary output for batch processing
- Efficient batch handling
- Preserves image metadata

#### 🧵 Save Image with Caption
**Node ID**: `PipemindSaveImageWTxt`
- Saves images with accompanying text files
- Perfect for dataset creation
- Automatic caption file generation

---

### 🔍 Display & Debugging

#### 🧵 Show Text
**Node ID**: `PipemindShowText`
- Display text values in the UI
- Simple text visualization
- Useful for debugging workflows

#### 🧵 Show Text Find
**Node ID**: `PipemindShowTextFind`
- Text display with search functionality
- Highlight matching patterns
- Regex support

#### 🧵 Display Any
**Node ID**: `PipemindDisplayAny`
- Display any data type
- Universal debugging node
- Automatic type detection and formatting

---

### 🛠️ Utilities

#### 🧵 Boolean Switch (Any)
**Node ID**: `BooleanSwitchAny`
- Route any data type based on boolean condition
- Visual feedback (color changes on state)
- Essential for conditional workflows

#### 🧵 Token Counter
**Node ID**: `PipemindTokenCounter`
- Count tokens in text using HuggingFace tokenizers
- Supports multiple tokenizer models
- Returns token count as integer

#### 🧵 LoRA Loader
**Node ID**: `PipemindLoraLoader`
- Load LoRA models into your workflow
- Standard LoRA loading interface
- Compatible with ComfyUI model management

---

## 📋 Requirements

- **Python**: 3.12.12+ (recommended for PyTorch CUDA compatibility)
- **ComfyUI**: Latest version
- **Dependencies**:
  - Pillow >= 10.0.0
  - transformers >= 4.30.0
  - PyTorch (provided by ComfyUI)
  - NumPy (provided by ComfyUI)

## 🧪 Testing

This project includes a comprehensive test suite to ensure reliability and quality.

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m unit        # Unit tests only
pytest -m smoke       # Quick smoke tests
pytest -m aspect_ratio # Aspect ratio node tests
```

### Test Categories

Tests are organized using markers:
- `unit` - Unit tests for individual functions
- `integration` - Integration tests with ComfyUI
- `smoke` - Quick validation tests
- `slow` - Longer-running tests
- Category-specific: `aspect_ratio`, `text`, `image`, `prompt`, `utility`

For detailed testing documentation, see [tests/README.md](tests/README.md).

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/aa-parky/pipemind-comfyui.git
cd pipemind-comfyui

# Create a development branch
git checkout -b feature/your-feature-name

# Install dependencies
pip install -r requirements.txt

# Make your changes and commit
git add .
git commit -m "Description of changes"
git push origin feature/your-feature-name
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [ComfyUI](https://github.com/comfyanonymous/ComfyUI) community
- Inspired by the need for lightweight, focused node collections

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aa-parky/pipemind-comfyui/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aa-parky/pipemind-comfyui/discussions)

---

**Note**: All nodes are prefixed with 🧵 in the ComfyUI interface for easy identification.
