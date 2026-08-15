from typing import Tuple

try:
    from .pipemind_h3_common import (
        FIELD_DESCRIPTION,
        FIELD_MUSIC,
        FIELD_SOUNDSCAPE,
        H3_FRAME_STEP,
        H3_MAX_FRAMES,
        H3_MIN_FRAMES,
        H3_MODES,
        alignment_line,
        snap_length,
    )
except ImportError:  # top-level import (tests)
    from pipemind_h3_common import (
        FIELD_DESCRIPTION,
        FIELD_MUSIC,
        FIELD_SOUNDSCAPE,
        H3_FRAME_STEP,
        H3_MAX_FRAMES,
        H3_MIN_FRAMES,
        H3_MODES,
        alignment_line,
        snap_length,
    )


class PipemindH3PromptAssembler:
    """
    Assemble a complete MiniMax H3 base-mode prompt (T2VA / I2VA / FL2VA / L2VA).

    Owns the mechanical parts of the H3 prompt grammar so they cannot drift:
    the mode-specific alignment first line (with its intentionally inconsistent
    bracketing), the effective duration to exactly two decimals derived from a
    17n+5-snapped frame count, and the three-field structure with blank lines.

    The `length` output is a passthrough of the snapped frame count. Wire it
    into the MiniMax H3 node's `length` input so the alignment line and the
    sampler duration always agree - the nominal-vs-aligned duration mismatch
    (10.00 vs 10.83) is the most common silent H3 prompt error.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(H3_MODES.keys()),),
                "length": (
                    "INT",
                    {
                        "default": 124,
                        "min": H3_MIN_FRAMES,
                        "max": H3_MAX_FRAMES,
                        "step": H3_FRAME_STEP,
                    },
                ),
                "final_shot_number": ("INT", {"default": 1, "min": 1, "max": 20}),
                "description": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "[Shot 1] Live-action, cinematic, ",
                    },
                ),
                "soundscape": ("STRING", {"multiline": True, "default": ""}),
                "music": ("STRING", {"multiline": True, "default": "N/A"}),
            }
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "length")
    FUNCTION = "assemble"
    CATEGORY = "Pipemind/MiniMax H3"

    @staticmethod
    def _strip_field_prefix(text: str, field: str) -> str:
        """Be forgiving if the user pasted text that already carries the label."""
        stripped = text.strip()
        prefix = f"{field}:"
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix):].strip()
        return stripped

    def assemble(
        self,
        mode: str,
        length: int,
        final_shot_number: int,
        description: str,
        soundscape: str,
        music: str,
    ) -> Tuple[str, int]:
        mode_token = H3_MODES[mode]
        frames = snap_length(length)

        description = self._strip_field_prefix(description, FIELD_DESCRIPTION)
        soundscape = self._strip_field_prefix(soundscape, FIELD_SOUNDSCAPE)
        music = self._strip_field_prefix(music, FIELD_MUSIC) or "N/A"

        parts = []
        first_line = alignment_line(mode_token, frames, final_shot_number)
        if first_line:
            parts.append(first_line)
        parts.append(f"{FIELD_DESCRIPTION}: {description}")
        parts.append(f"{FIELD_SOUNDSCAPE}: {soundscape}")
        parts.append(f"{FIELD_MUSIC}: {music}")

        return ("\n\n".join(parts), frames)


NODE_CLASS_MAPPINGS = {
    "PipemindH3PromptAssembler": PipemindH3PromptAssembler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PipemindH3PromptAssembler": "MiniMax H3 Prompt Assembler",
}
