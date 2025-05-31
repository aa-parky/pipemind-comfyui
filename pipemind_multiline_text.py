class PipemindMultilineTextInput:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "{a goblin|a dwarf} tapdancing with {a wrench|a kettle}",
                    "multiline": True,
                    "dynamicPrompts": False
                }),
                "enable_dynamic": ("BOOLEAN", {
                    "default": False
                }),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):  # 👈 Accept any input args to silence warning
        return float("nan")

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_text",)
    FUNCTION = "return_text"
    CATEGORY = "Pipemind/Text"

    def return_text(self, text, enable_dynamic):
        if enable_dynamic:
            import re
            from random import choice

            def replace_match(match):
                options = match.group(1).split('|')
                return choice(options)

            text = re.sub(r'\{([^}]+)\}', replace_match, text)

        return (text,)