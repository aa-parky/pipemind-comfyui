from .pipemind_random_line import RandomLineFromDropdown
from .pipemind_composer_node import KeywordPromptComposer
from .pipemind_prompt_combiner_node import SimplePromptCombiner
from .pipemind_boolean_switch_any import BooleanSwitchAny
from .pipemind_select_line import SelectLineFromDropdown
from .pipemind_multiline_text import PipemindMultilineTextInput
from .pipemind_flux_2m_aspect_ratio import PipemindFlux2MAspectRatio
from .pipemind_sdxl_aspect_ratio import PipemindSDXL15AspectRatio
from .pipemind_batch_image_loader import BatchImageLoad
from .pipemind_image_saver_with_caption import  PipemindSaveImageWTxt
from .pipemind_token_counter import PipemindTokenCounter
from .pipemind_show_text import PipemindShowText
from .pipemind_display_any import PipemindDisplayAny
from .pipemind_lora_loader import PipemindLoraLoader


NODE_CLASS_MAPPINGS = {
    "RandomLineFromDropdown": RandomLineFromDropdown,
    "KeywordPromptComposer": KeywordPromptComposer,
    "SimplePromptCombiner": SimplePromptCombiner,
    "BooleanSwitchAny": BooleanSwitchAny,
    "SelectLineFromDropdown": SelectLineFromDropdown,
    "PipemindMultilineTextInput": PipemindMultilineTextInput,
    "PipemindFlux2MAspectRatio": PipemindFlux2MAspectRatio,
    "PipemindSDXL15AspectRatio": PipemindSDXL15AspectRatio,
    "BatchImageLoad": BatchImageLoad,
    "PipemindSaveImageWTxt": PipemindSaveImageWTxt,
    "PipemindTokenCounter": PipemindTokenCounter,
    "PipemindShowText": PipemindShowText,
    "PipemindDisplayAny": PipemindDisplayAny,
    "PipemindLoraLoader": PipemindLoraLoader,
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
    "BatchImageLoad": "🧵 Batch Image Loader",
    "PipemindSaveImageWTxt": "🧵 Save Image with Caption",
    "PipemindTokenCounter": "🧵 Token Counter",
    "PipemindShowText": "🧵 Show Text",
    "PipemindDisplayAny": "🧵 Display Any",
    "PipemindLoraLoader": "🧵 LoRA Loader",
}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
