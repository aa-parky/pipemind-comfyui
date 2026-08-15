from typing import Tuple

try:
    from .pipemind_h3_common import H3_CAMERA_PHRASES
except ImportError:  # top-level import (tests)
    from pipemind_h3_common import H3_CAMERA_PHRASES


class PipemindH3CameraMove:
    """
    Build a MiniMax H3 camera-motion sentence from the model's fixed vocabulary.

    The H3 base guide specifies motion type + amplitude + speed, written as a
    natural English action inside the shot ("The camera pushes in with small
    amplitude at slow speed toward the folded letter"). Amplitude and speed
    are only added when meaningful - medium amplitude and normal speed are
    expressed by omission, so both dropdowns default to "none".

    The output is a complete sentence fragment ready for a prompt combiner or
    a `<camera>` placeholder in the Keyword Prompt Composer.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "motion": (list(H3_CAMERA_PHRASES.keys()), {"default": "Push In"}),
                "amplitude": (["none", "small", "large"],),
                "speed": (["none", "slow", "fast"],),
            },
            "optional": {
                "action": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                        "tooltip": "Continues the sentence: 'as <action>' (e.g. 'he approaches the door').",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("camera_sentence",)
    FUNCTION = "build"
    CATEGORY = "Pipemind/MiniMax H3"

    def build(self, motion: str, amplitude: str, speed: str, action: str = "") -> Tuple[str]:
        sentence = H3_CAMERA_PHRASES[motion]
        if amplitude != "none":
            sentence += f" with {amplitude} amplitude"
        if speed != "none":
            sentence += f" at {speed} speed"

        action = action.strip()
        if action:
            sentence += f" as {action}"

        if not sentence.endswith((".", "!", "?")):
            sentence += "."

        return (sentence,)


NODE_CLASS_MAPPINGS = {
    "PipemindH3CameraMove": PipemindH3CameraMove,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PipemindH3CameraMove": "MiniMax H3 Camera Move",
}
