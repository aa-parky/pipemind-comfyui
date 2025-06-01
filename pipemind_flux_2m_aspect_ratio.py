class PipemindFlux2MAspectRatio:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (["Landscape", "Portrait", "Manual"],),
                "preset": (
                    [
                        "1:1 (1408x1408)",
                        "3:2 (1728x1152)",
                        "4:3 (1664x1216)",
                        "16:9 (1920x1088)",
                        "21:9 (2176x960)",
                        "Manual",
                    ],
                ),
                "manual_width": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 64}),
                "manual_height": ("INT", {"default": 512, "min": 64, "max": 4096, "step": 64}),
            }
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("width", "height",)
    FUNCTION = "select_resolution"
    CATEGORY = "Pipemind/Resolution"

    def select_resolution(self, mode, preset, manual_width, manual_height):
        # Preset dimensions (rounded to nearest 64)
        presets = {
            "1:1 (1408x1408)": (1408, 1408),
            "3:2 (1728x1152)": (1728, 1152),
            "4:3 (1664x1216)": (1664, 1216),
            "16:9 (1920x1088)": (1920, 1088),
            "21:9 (2176x960)": (2176, 960),
        }

        if preset == "Manual" or mode == "Manual":
            width, height = manual_width, manual_height
        else:
            width, height = presets.get(preset, (512, 512))
            if mode == "Portrait":
                width, height = height, width  # Swap for portrait mode

        return (width, height,)
