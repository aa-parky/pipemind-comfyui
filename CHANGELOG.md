# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with pytest
  - Unit tests for aspect ratio nodes
  - Unit tests for utility nodes (Boolean switch)
  - Unit tests for text processing nodes (Random line)
  - Test fixtures and validation helpers
  - pytest configuration and markers
  - Test documentation in tests/README.md
- Development dependencies (requirements-dev.txt)
  - pytest and pytest plugins
  - Code quality tools (black, flake8, pylint, mypy)
  - Development tools (ipython, pre-commit)
- Testing documentation in README.md and CONTRIBUTING.md
- Development branch for ongoing work

### Changed
- Updated README with testing section
- Updated CONTRIBUTING with testing guidelines

## [0.2.0] - 2025-11-24

### Added
- Qwen Aspect Ratio node with official Qwen-Image resolutions
  - Supports 1:1, 16:9, 4:3, and 3:2 aspect ratios
  - Landscape/Portrait/Manual modes

### Fixed
- Fixed indentation error in Qwen aspect ratio node that caused import failure

## [0.1.9] - 2025-11-23

### Added
- Enhanced Keyword Prompt Composer with additional features
- Inline tagging support in composer mode

### Changed
- Composer mode updated to allow inline tagging
- Boolean switch color changes when enabled state is activated

## [0.1.8] - 2025-11-22

### Added
- Select Line node: Ignore line or sequence functionality
- Text search capability in Show Text Find node
- File preview output with line numbers in Select Line node

### Changed
- Select Line: Added ability to select string of numbered lines
- Select Line: Color change on false condition

## [0.1.7] - 2025-11-21

### Added
- Detailed documentation for Select Line node (README_SELECT_LINE.md)
- Increment tracking for line_index during batch runs

## [0.1.6] - 2025-11-20

### Added
- Batch Image Loader Input node for source directory processing
- Batch Image Loader Output node for batch handling

### Changed
- General code cleanup and organization

## [0.1.5] - 2025-11-19

### Added
- Load TXT File node for reading text file contents

### Removed
- Clipper functionality
- Count feature (was overwriting files on session restart)

## [0.1.4] - 2025-11-18

### Changed
- Preparing infrastructure for batch loader input/output nodes

## [0.1.3] - 2025-11-17

### Added
- WordNinja integration for text processing

## [0.1.0] - 2025-11-15

### Added
- Initial release of Pipemind ComfyUI Custom Nodes
- Random Line from File node with seed control
- Select Line from TXT node with multiple modes
- Keyword Prompt Composer
- Simple Prompt Combiner (5 inputs)
- Boolean Switch (Any type)
- Multiline Text Input
- Flux 2M Aspect Ratio presets
- SDXL Aspect Ratio presets
- Save Image with Caption
- Token Counter with HuggingFace tokenizers
- Show Text display node
- Display Any debug node
- LoRA Loader utility

---

[Unreleased]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.9...v0.2.0
[0.1.9]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/aa-parky/pipemind-comfyui/releases/tag/v0.1.0
