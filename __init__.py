from .pipemind_random_line import RandomLineFromDropdown
from .pipemind_composer_node import KeywordPromptComposer
from .pipemind_prompt_combiner_node import SimplePromptCombiner
from .pipemind_boolean_switch_any import BooleanSwitchAny
from .pipemind_select_line import SelectLineFromDropdown
from .pipemind_multiline_text import PipemindMultilineTextInput


NODE_CLASS_MAPPINGS = {
    "RandomLineFromDropdown": RandomLineFromDropdown,
    "KeywordPromptComposer": KeywordPromptComposer,
    "SimplePromptCombiner": SimplePromptCombiner,
    "BooleanSwitchAny": BooleanSwitchAny,
    "SelectLineFromDropdown": SelectLineFromDropdown,
    "PipemindMultilineTextInput": PipemindMultilineTextInput,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomLineFromDropdown": "🧵 Random Line from File (Seeded)",
    "KeywordPromptComposer": "🧵 Keyword Prompt Composer",
    "SimplePromptCombiner": "🧵 Simple Prompt Combiner (5x)",
    "BooleanSwitchAny": "🧵 Boolean Switch (Any)",
    "SelectLineFromDropdown": "🧵 Select Line from TxT (Any)",
    "PipemindMultilineTextInput": "🧵 Multiline Text Input",
}
