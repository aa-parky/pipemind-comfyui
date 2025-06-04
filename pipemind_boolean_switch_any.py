class BooleanSwitchAny:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "on_true": ("STRING", {"forceInput": True}),
                "on_false": ("STRING", {"forceInput": True}),
                "switch": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)
    FUNCTION = "switch"
    CATEGORY = "Pipemind/Switch"

    @classmethod
    def INPUT_IS_PREVIEW(cls):
        return True

    def switch(self, on_true, on_false, switch=True):
        print(f"[BooleanSwitchAny] switch = {switch}")
        return (on_true if switch else on_false,)

    @staticmethod
    def IS_CHANGED(**kwargs):
        return True