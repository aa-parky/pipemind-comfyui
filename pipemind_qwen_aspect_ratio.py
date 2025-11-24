class PipemindQwenAspectRatio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Landscape", "Portrait", "Manual"],),
                "preset": (
                    [
                        "1:1 (1328x1328)",
                        "16:9 (1664x928)",
                        "4:3 (1472x1140)",
                        "3:2 (1584x1056)",
                        "Manual",
                    ],
                ),
                "manual_width": ("INT", {"default": 1328, "min": 64, "max": 4096, "step": 64}),
                "manual_height": ("INT", {"default": 1328, "min": 64, "max": 4096, "step": 64}),
            }
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height",)
    FUNCTION = "select_resolution"
    CATEGORY = "Pipemind/Resolution"

    def select_resolution(self, mode, preset, manual_width, manual_height):
        # Preset dimensions (optimized for Qwen-Image, official resolutions)
        presets = {
            "1:1 (1328x1328)": (1328, 1328),
            "16:9 (1664x928)": (1664, 928),
            "4:3 (1472x1140)": (1472, 1140),
            "3:2 (1584x1056)": (1584, 1056),
        }

        if preset == "Manual" or mode == "Manual":
            width, height = manual_width, manual_height
        else:
            width, height = presets.get(preset, (1328, 1328))
            if mode == "Portrait":
                width, height = height, width  # Swap for portrait mode

        return (width, height,)
