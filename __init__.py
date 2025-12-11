from .pipemind_random_line import RandomLineFromDropdown
from .pipemind_composer_node import KeywordPromptComposer
from .pipemind_prompt_combiner_node import SimplePromptCombiner
from .pipemind_boolean_switch_any import BooleanSwitchAny
from .pipemind_select_line import SelectLineFromDropdown
from .pipemind_multiline_text import PipemindMultilineTextInput
from .pipemind_flux_2m_aspect_ratio import PipemindFlux2MAspectRatio
from .pipemind_sdxl_aspect_ratio import PipemindSDXL15AspectRatio
from .pipemind_qwen_aspect_ratio import PipemindQwenAspectRatio
from .pipemind_batch_image_loader_output import BatchImageLoadOutput
from .pipemind_batch_image_loader_input import BatchImageLoadInput
from .pipemind_image_saver_with_caption import PipemindSaveImageWTxt
from .pipemind_token_counter import PipemindTokenCounter
from .pipemind_show_text import PipemindShowText
from .pipemind_display_any import PipemindDisplayAny
from .pipemind_lora_loader import PipemindLoraLoader
from .pipemind_load_txt_file import LoadTxtFile
from .pipemind_show_text_find import PipemindShowTextFind
from .pipemind_enhanced_composer_node import EnhancedKeywordPromptComposer

NODE_CLASS_MAPPINGS = {
    "RandomLineFromDropdown": RandomLineFromDropdown,
    "KeywordPromptComposer": KeywordPromptComposer,
    "SimplePromptCombiner": SimplePromptCombiner,
    "BooleanSwitchAny": BooleanSwitchAny,
    "SelectLineFromDropdown": SelectLineFromDropdown,
    "PipemindMultilineTextInput": PipemindMultilineTextInput,
    "PipemindFlux2MAspectRatio": PipemindFlux2MAspectRatio,
    "PipemindSDXL15AspectRatio": PipemindSDXL15AspectRatio,
    "PipemindQwenAspectRatio": PipemindQwenAspectRatio,
    "BatchImageLoadOutput": BatchImageLoadOutput,
    "BatchImageLoadInput": BatchImageLoadInput,
    "PipemindSaveImageWTxt": PipemindSaveImageWTxt,
    "PipemindTokenCounter": PipemindTokenCounter,
    "PipemindShowText": PipemindShowText,
    "PipemindDisplayAny": PipemindDisplayAny,
    "PipemindLoraLoader": PipemindLoraLoader,
    "LoadTxtFile": LoadTxtFile,
    "PipemindShowTextFind": PipemindShowTextFind,
    "EnhancedKeywordPromptComposer": EnhancedKeywordPromptComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLineFromDropdown": "🧵 Random Line from File (Seeded)",
    "KeywordPromptComposer": "🧵 Keyword Prompt Composer",
    "SimplePromptCombiner": "🧵 Simple Prompt Combiner (5x)",
    "BooleanSwitchAny": "🧵 Boolean Switch (Any)",
    "SelectLineFromDropdown": "🧵 Select Line from TxT (Any)",
    "PipemindMultilineTextInput": "🧵 Multiline Text Input",
    "PipemindFlux2MAspectRatio": "🧵 Flux 2M Aspect Ratios",
    "PipemindSDXL15AspectRatio": "🧵 SDXL Aspect Ratios",
    "PipemindQwenAspectRatio": "🧵 Qwen Aspect Ratios",
    "BatchImageLoadOutput": "🧵 Batch Image Loader src Output",
    "BatchImageLoadInput": "🧵 Batch Image Loader src Input",
    "PipemindSaveImageWTxt": "🧵 Save Image with Caption",
    "PipemindTokenCounter": "🧵 Token Counter",
    "PipemindShowText": "🧵 Show Text",
    "PipemindDisplayAny": "🧵 Display Any",
    "PipemindLoraLoader": "🧵 LoRA Loader",
    "LoadTxtFile": "🧵 Load TXT File",
    "PipemindShowTextFind": "🧵 Show Text Find",
    "EnhancedKeywordPromptComposer": "🧵 Enhanced Keyword Composer",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
