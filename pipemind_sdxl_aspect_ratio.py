class PipemindSDXL15AspectRatio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Landscape", "Portrait", "Manual"],),
                "preset": (
                    [
                        "1:1 (1024x1024)",
                        "3:2 (1216x832)",
                        "4:3 (1152x896)",
                        "16:9 (1344x768)",
                        "2:1 (1280x640)",
                        "Manual",
                    ],
                ),
                "manual_width": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 64}),
                "manual_height": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 64}),
            }
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height",)
    FUNCTION = "select_resolution"
    CATEGORY = "Pipemind/Resolution"

    def select_resolution(self, mode, preset, manual_width, manual_height):
        # Preset dimensions (optimized for SDXL 1.5, maintaining aspect ratios)
        presets = {
            "1:1 (1024x1024)": (1024, 1024),
            "3:2 (1216x832)": (1216, 832),
            "4:3 (1152x896)": (1152, 896),
            "16:9 (1344x768)": (1344, 768),
            "2:1 (1280x640)": (1280, 640),
        }

        if preset == "Manual" or mode == "Manual":
            width, height = manual_width, manual_height
        else:
            width, height = presets.get(preset, (1024, 1024))
            if mode == "Portrait":
                width, height = height, width  # Swap for portrait mode

        return (width, height,)