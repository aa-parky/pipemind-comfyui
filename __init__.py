from .pipemind_random_line import RandomLineFromDropdown
from .pipemind_composer_node import KeywordPromptComposer
from .pipemind_prompt_combiner_node import SimplePromptCombiner
from .pipemind_boolean_switch_any import BooleanSwitchAny
from .pipemind_select_line import SelectLineFromDropdown
from .pipemind_multiline_text import PipemindMultilineTextInput
from .pipemind_flux_2m_aspect_ratio import PipemindFlux2MAspectRatio
from .pipemind_sdxl_aspect_ratio import PipemindSDXL15AspectRatio
from .pipemind_room_mapper import PipemindRoomNode
from .pipemind_batch_image_loader import BatchImageLoad
from .pipemind_image_saver_with_caption import  PipemindSaveImageWTxt


NODE_CLASS_MAPPINGS = {
    "RandomLineFromDropdown": RandomLineFromDropdown,
    "KeywordPromptComposer": KeywordPromptComposer,
    "SimplePromptCombiner": SimplePromptCombiner,
    "BooleanSwitchAny": BooleanSwitchAny,
    "SelectLineFromDropdown": SelectLineFromDropdown,
    "PipemindMultilineTextInput": PipemindMultilineTextInput,
    "PipemindFlux2MAspectRatio": PipemindFlux2MAspectRatio,
    "PipemindSDXL15AspectRatio": PipemindSDXL15AspectRatio,
    "PipemindRoomNode": PipemindRoomNode,
    "BatchImageLoad": BatchImageLoad,
    "PipemindSaveImageWTxt": PipemindSaveImageWTxt,
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
    "PipemindRoomNode": "🧵 Room Mapper",
    "BatchImageLoad": "🧵 Batch Image Loader",
    "PipemindSaveImageWTxt": "🧵 Save Image with Caption",
}
