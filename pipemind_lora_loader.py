import folder_paths

# Import ComfyUI's built-in LoraLoader
try:
    from nodes import LoraLoader
except ImportError:
    # Fallback in case the import path changes
    from comfy_extras.nodes_custom_sampler import LoraLoader


class PipemindLoraLoader:
    """Load multiple LoRA files in sequence with individual strength controls."""

    @classmethod
    def INPUT_TYPES(cls):
        lora_list = ['None'] + folder_paths.get_filename_list("loras")
        return {
            "required": {
                "model": ("MODEL",),
                "clip": ("CLIP",),
                "lora_01": (lora_list,),
                "strength_01": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora_02": (lora_list,),
                "strength_02": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora_03": (lora_list,),
                "strength_03": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora_04": (lora_list,),
                "strength_04": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
                "lora_05": (lora_list,),
                "strength_05": ("FLOAT", {"default": 1.0, "min": -10.0, "max": 10.0, "step": 0.01}),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP")
    FUNCTION = "load_loras"
    CATEGORY = "utils"

    def load_loras(self, model, clip, lora_01, strength_01, lora_02, strength_02,
                   lora_03, strength_03, lora_04, strength_04, lora_05, strength_05):
        """Load multiple LoRA files sequentially."""

        # Create LoraLoader instance
        lora_loader = LoraLoader()

        # Load each LoRA if it's not "None" and strength is not 0
        loras = [
            (lora_01, strength_01),
            (lora_02, strength_02),
            (lora_03, strength_03),
            (lora_04, strength_04),
            (lora_05, strength_05),
        ]

        for lora_name, strength in loras:
            if lora_name != "None" and strength != 0:
                # LoraLoader.load_lora expects: model, clip, lora_name, strength_model, strength_clip
                # Using the same strength for both model and clip as in the original
                model, clip = lora_loader.load_lora(model, clip, lora_name, strength, strength)

        return (model, clip)

