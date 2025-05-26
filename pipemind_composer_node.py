class KeywordPromptComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "keyword": ("STRING", {"forceInput": True}),
                "template_prompt": ("STRING", {
                    "multiline": True,
                    "default": "A picture of a goblin. <loc>"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("composed_prompt",)
    FUNCTION = "compose_prompt"
    CATEGORY = "Text/Custom"

    def compose_prompt(self, keyword, template_prompt):
        if "=" not in keyword:
            return (template_prompt,)

        key, value = keyword.split("=", 1)
        key = key.strip()
        value = value.strip()

        result = template_prompt.replace(f"<{key}>", value)
        return (result,)