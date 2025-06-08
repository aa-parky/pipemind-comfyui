from transformers import AutoTokenizer

class PipemindTokenCounter:
    # Internal model ID map
    ENCODER_MODEL_MAPPING = {
        "T5 XXL v1.1 (Google)": "google/t5-v1_1-xxl",
        "CLIP I (OpenAI)": "openai/clip-vit-base-patch16",
        "CLIP Large (SDXL Default)": "openai/clip-vit-large-patch14"
    }

    tokenizer_cache = {}

    @classmethod
    def INPUT_TYPES(cls):
        encoder_keys = list(cls.ENCODER_MODEL_MAPPING.keys())
        default_encoder = "T5 XXL v1.1 (Google)"

        return {
            "required": {
                "primary_encoder": (
                    encoder_keys,
                    {
                        "default": default_encoder,
                        "tooltip": "Choose which tokenizer model to use.",
                    },
                ),
                "text": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": True,
                        "tooltip": "The text or prompt to count tokens for.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("total_tokens",)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = ("The total number of tokens in the given text.",)
    CATEGORY = "Pipemind/Utility"
    FUNCTION = "count_tokens"
    DESCRIPTION = "Token counter for T5/CLIP/SDXL prompts using HuggingFace tokenizer."

    def count_tokens(self, primary_encoder: str, text: str) -> tuple:
        if not text.strip():
            return (0,)

        model_name = self.ENCODER_MODEL_MAPPING.get(primary_encoder)
        if not model_name:
            print(f"[PipemindTokenCounter] Unknown encoder: {primary_encoder}")
            return (0,)

        try:
            tokenizer = self.tokenizer_cache.setdefault(
                model_name, AutoTokenizer.from_pretrained(model_name)
            )
            token_count = len(tokenizer.encode(text, add_special_tokens=True))
            return (token_count,)
        except Exception as e:
            print(f"[PipemindTokenCounter] Error with tokenizer '{model_name}': {e}")
            return (0,)