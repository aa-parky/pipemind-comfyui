"""
Pipemind ComfyUI custom nodes - package registration.

Each node module is imported individually so that a missing optional
dependency (e.g. torch outside a ComfyUI install) skips that node with a
warning instead of taking down the whole pack. This also keeps the package
importable when pytest collects the repository root as a package.
"""

import importlib

# (module, class name, display name)
_NODE_SPECS = [
    ("pipemind_random_line", "RandomLineFromDropdown", "🧵 Random Line from File (Seeded)"),
    ("pipemind_composer_node", "KeywordPromptComposer", "🧵 Keyword Prompt Composer"),
    ("pipemind_prompt_combiner_node", "SimplePromptCombiner", "🧵 Simple Prompt Combiner (5x)"),
    ("pipemind_boolean_switch_any", "BooleanSwitchAny", "🧵 Boolean Switch (Any)"),
    ("pipemind_select_line", "SelectLineFromDropdown", "🧵 Select Line from TxT (Any)"),
    ("pipemind_multiline_text", "PipemindMultilineTextInput", "🧵 Multiline Text Input"),
    ("pipemind_flux_2m_aspect_ratio", "PipemindFlux2MAspectRatio", "🧵 Flux 2M Aspect Ratios"),
    ("pipemind_sdxl_aspect_ratio", "PipemindSDXL15AspectRatio", "🧵 SDXL Aspect Ratios"),
    ("pipemind_qwen_aspect_ratio", "PipemindQwenAspectRatio", "🧵 Qwen Aspect Ratios"),
    ("pipemind_batch_image_loader_output", "BatchImageLoadOutput", "🧵 Batch Image Loader src Output"),
    ("pipemind_batch_image_loader_input", "BatchImageLoadInput", "🧵 Batch Image Loader src Input"),
    ("pipemind_image_saver_with_caption", "PipemindSaveImageWTxt", "🧵 Save Image with Caption"),
    ("pipemind_token_counter", "PipemindTokenCounter", "🧵 Token Counter"),
    ("pipemind_show_text", "PipemindShowText", "🧵 Show Text"),
    ("pipemind_display_any", "PipemindDisplayAny", "🧵 Display Any"),
    ("pipemind_lora_loader", "PipemindLoraLoader", "🧵 LoRA Loader"),
    ("pipemind_load_txt_file", "LoadTxtFile", "🧵 Load TXT File"),
    ("pipemind_show_text_find", "PipemindShowTextFind", "🧵 Show Text Find"),
    ("pipemind_enhanced_composer_node", "EnhancedKeywordPromptComposer", "🧵 Enhanced Keyword Composer"),
    ("pipemind_multifile_composer_node", "MultiFileKeywordPromptComposer", "🧵 Multi-File Keyword Composer"),
    ("pipemind_h3_prompt_assembler", "PipemindH3PromptAssembler", "🧵 MiniMax H3 Prompt Assembler"),
    ("pipemind_h3_camera_move", "PipemindH3CameraMove", "🧵 MiniMax H3 Camera Move"),
    ("pipemind_h3_dialogue", "PipemindH3Dialogue", "🧵 MiniMax H3 Dialogue"),
    ("pipemind_h3_prompt_lint", "PipemindH3PromptLint", "🧵 MiniMax H3 Prompt Lint"),
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for _module_name, _class_name, _display_name in _NODE_SPECS:
    try:
        if __package__:
            _module = importlib.import_module(f".{_module_name}", __package__)
        else:
            _module = importlib.import_module(_module_name)
        NODE_CLASS_MAPPINGS[_class_name] = getattr(_module, _class_name)
        NODE_DISPLAY_NAME_MAPPINGS[_class_name] = _display_name
    except Exception as _error:  # noqa: BLE001 - one broken node must not sink the pack
        print(f"[pipemind-comfyui] Skipping node '{_class_name}' ({_module_name}): {_error}")

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
