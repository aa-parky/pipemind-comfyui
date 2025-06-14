class SimplePromptCombiner:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"forceInput": True}),
                "delimiter": (["space", "newline", "comma", "slash", "nothing"], {"default": "space"}),
            },
            "optional": {
                "prompt_2": ("STRING", {"forceInput": True}),
                "prompt_3": ("STRING", {"forceInput": True}),
                "prompt_4": ("STRING", {"forceInput": True}),
                "prompt_5": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("combined_prompt",)
    FUNCTION = "combine"
    CATEGORY = "Pipemind"

    def combine(self, prompt_1, delimiter, prompt_2=None, prompt_3=None, prompt_4=None, prompt_5=None):
        prompts = [prompt_1, prompt_2, prompt_3, prompt_4, prompt_5]
        prompts = [p.strip() for p in prompts if p and isinstance(p, str) and p.strip()]
        combined = self.get_delimiter(delimiter).join(prompts)
        return (combined,)

    @staticmethod
    def get_delimiter(delimiter):
        return {
            "space": " ",
            "newline": "\n",
            "comma": ", ",
            "slash": "/",
            "nothing": ""
        }.get(delimiter, " ")