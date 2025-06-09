from transformers import CLIPTokenizer
import wordninja

class PipemindWordninjaClipper:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True,
                    "tooltip": "Enter your prompt to be cleaned and clipped for CLIP."
                }),
                "max_tokens": ("INT", {
                    "default": 77,
                    "min": 1,
                    "max": 512,
                    "tooltip": "Maximum tokens allowed (CLIP limit is 77)."
                })
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("clipped_text",)
    FUNCTION = "clip_text"
    CATEGORY = "Pipemind/Utility"
    DESCRIPTION = "Splits long compound words using wordninja and truncates prompt to CLIP-safe length."

    def __init__(self):
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch16")

    def clip_text(self, text, max_tokens):
        # Step 1: Word-split compound blobs
        cleaned = " ".join(wordninja.split(text))

        # Step 2: Tokenize
        tokens = self.tokenizer.encode(cleaned, add_special_tokens=False)

        # Step 3: Clip to max_tokens
        truncated = tokens[:max_tokens]

        # Step 4: Decode back to string
        final = self.tokenizer.decode(truncated, skip_special_tokens=True)
        return (final,)