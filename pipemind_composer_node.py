class KeywordPromptComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "keyword": ("STRING", {"default": "item"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("composed_prompt",)
    FUNCTION = "compose_prompt"
    CATEGORY = "Pipemind/Text"

    def compose_prompt(self, text, keyword):
        if not text.strip():
            return ("",)

        # Remove angle brackets if present
        keyword = keyword.strip().strip("<>")

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(f"{keyword}="):
                return (line.split("=", 1)[1].strip(),)

        return ("",)