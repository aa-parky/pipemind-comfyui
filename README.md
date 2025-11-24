# 🧵 Pipemind ComfyUI Custom Nodes

A focused collection of custom nodes for ComfyUI, designed for efficient workflow management without the bloat of large node packs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Node Categories](#node-categories)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **Lightweight**: Minimal dependencies, focused functionality
- **Text Processing**: Advanced file reading and line selection
- **Prompt Tools**: Flexible prompt composition and combination
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
