# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **MiniMax H3 usage guide** in the README (`Using the MiniMax H3 Nodes`)
  - Annotated screenshots of all four H3 nodes with widget/output reference
    tables, in `docs/images/`
  - A complete worked two-shot, two-speaker FL2VA workflow: graph diagram,
    full connection table, node settings, and real assembler/lint output
  - Mode reference table and a summary of the mistakes each node prevents

## [0.3.0] - 2026-08-15

### Added
- **MiniMax H3 Prompt Node Family** (4 nodes, `Pipemind/MiniMax H3` category)
  - MiniMax H3 Prompt Assembler (`PipemindH3PromptAssembler`)
    * Assembles complete base-mode prompts (T2VA / I2VA / FL2VA / L2VA)
    * Generates the mode-specific alignment first line with the official
      bracketing and the effective duration to exactly two decimals
    * Snaps frame counts to the model's 17n+5 grid (24 fps)
    * `length` INT passthrough keeps the alignment line and the sampler
      duration in sync from a single widget
  - MiniMax H3 Camera Move (`PipemindH3CameraMove`)
    * Builds camera sentences from the model's fixed 20-term motion
      vocabulary with optional amplitude and speed qualifiers
  - MiniMax H3 Dialogue (`PipemindH3Dialogue`)
    * Correctly tagged `<d>[Language] ...</d>` dialogue with stable (S1)
      speaker IDs and compound group IDs
    * Voiceover mode emits the required "off-screen voiceover" phrase and
      closed-lips clause; supports `<cutoff>` and `<scenetrans>` endings
  - MiniMax H3 Prompt Lint (`PipemindH3PromptLint`)
    * Validates field structure, shot numbering, cut timestamps, dialogue
      tags, speaker-ID ordering, and alignment-line/duration agreement
    * Warns on word count outside 350-500 and stray curly braces
    * `pass` BOOLEAN output pairs with Boolean Switch (Any) to gate queuing
  - Shared grammar module `pipemind_h3_common.py` and a 41-test suite

- **Multi-File Keyword Prompt Composer**
  - New node supporting up to 5 keyword data sources
  - Combines multiple input sources for flexible prompt composition
  - Supports dynamic prompts {option1|option2|option3}
  - Advanced syntax {N$$ separator $$options} for multi-selection
  - Multi-line keyword data format support
  - Last-wins conflict resolution for duplicate keys
  - Comprehensive test suite with 30+ test cases

- **CI/CD Infrastructure with GitHub Actions**
  - Test automation workflow (tests.yml)
    * Runs unit and smoke tests on Python 3.12
    * Coverage reporting with Codecov integration
    * Installation validation
  - Code quality workflow (code-quality.yml)
    * Linting with Flake8
    * Formatting checks with Black
    * Type checking with mypy
    * Security scanning with Bandit
    * Dependency vulnerability checks
  - PR validation workflow (pr-validation.yml)
    * PR title format validation
    * CHANGELOG update checks
    * Node structure validation
    * PR size reporting
  - Release automation workflow (release.yml)
    * Automated GitHub releases from tags
    * Changelog extraction
    * Release installation testing
  - CI status badges in README.md
  - Workflow documentation (.github/workflows/README.md)

- **Testing Infrastructure**
  - Comprehensive test suite with pytest
  - Unit tests for aspect ratio nodes (14 tests)
  - Unit tests for utility nodes (12 tests)
  - Unit tests for text processing nodes (10 tests)
  - Test fixtures and validation helpers
  - pytest configuration and markers
  - Test documentation in tests/README.md

- **Development Tools**
  - Development dependencies (requirements-dev.txt)
  - pytest and pytest plugins (cov, mock, xdist)
  - Code quality tools (black, flake8, pylint, mypy)
  - Development utilities (ipython, pre-commit)

### Changed
- Package registration in `__init__.py` now imports each node module
  individually: a missing optional dependency (e.g. torch outside ComfyUI)
  skips that node with a console warning instead of disabling the whole pack
- Updated README with testing section and CI badges
- Updated CONTRIBUTING with testing and CI guidelines

### Fixed
- Advanced dynamic-prompt syntax `{N$$ sep $$a|b}` in the Multi-File and
  Enhanced Keyword Composers now keeps the separator's surrounding spaces
  (previously `{2$$ and $$red|yellow}` joined as `redandyellow`)
- Test suite collection under pytest 8/9 (removed `tests/__init__.py` so the
  repository root is no longer imported as a test package)
- Stale tests updated to current node contracts: `BooleanSwitchAny`
  (`switch` parameter, STRING sockets, `Pipemind/Switch` category) and
  `RandomLineFromDropdown` (`file_name` input)

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

[Unreleased]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.9...v0.2.0
[0.1.9]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/aa-parky/pipemind-comfyui/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/aa-parky/pipemind-comfyui/releases/tag/v0.1.0
