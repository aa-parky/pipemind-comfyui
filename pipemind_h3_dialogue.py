from typing import Tuple

try:
    from .pipemind_h3_common import H3_LANGUAGES
except ImportError:  # top-level import (tests)
    from pipemind_h3_common import H3_LANGUAGES


class PipemindH3Dialogue:
    """
    Build a correctly tagged MiniMax H3 dialogue sentence.

    Encodes the parts of the H3 speech grammar that are easy to get wrong:
    - delivery description stays OUTSIDE the <d> tag; only [Language] and the
      literal words go inside, punctuation preserved
    - stable (S1)/(S2) speaker IDs, with optional compound IDs like (S1,S2)
    - voiceover uses the fixed phrase "says in an off-screen voiceover" and
      REQUIRES a trailing statement that the character's lips remain closed -
      without it, a jointly generated audiovisual model will animate a
      talking mouth under the narration
    - <cutoff> for speech truncated by the end of the video, and <scenetrans>
      markers on both halves of a line that crosses a cut
    """

    LINE_ENDINGS = [
        "normal",
        "cutoff (video ends mid-line)",
        "scenetrans (line continues after a cut)",
        "scenetrans (line carried over from previous shot)",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "speaker_description": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "The man with a low, quiet voice",
                        "tooltip": "Identity and delivery, kept outside the <d> tag.",
                    },
                ),
                "speaker_number": ("INT", {"default": 1, "min": 1, "max": 9}),
                "verb": ("STRING", {"multiline": False, "default": "says"}),
                "language": (H3_LANGUAGES,),
                "line": ("STRING", {"multiline": True, "default": ""}),
                "delivery": (["on-screen", "off-screen voiceover"],),
                "pronoun": (["their", "his", "her"],),
                "line_ending": (cls.LINE_ENDINGS,),
            },
            "optional": {
                "custom_language": ("STRING", {"multiline": False, "default": ""}),
                "compound_ids": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                        "tooltip": "Overrides speaker_number for group speech, e.g. 'S1,S2'.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("dialogue_sentence",)
    FUNCTION = "build"
    CATEGORY = "Pipemind/MiniMax H3"

    def build(
        self,
        speaker_description: str,
        speaker_number: int,
        verb: str,
        language: str,
        line: str,
        delivery: str,
        pronoun: str,
        line_ending: str,
        custom_language: str = "",
        compound_ids: str = "",
    ) -> Tuple[str]:
        lang = custom_language.strip() if language == "custom" else language
        lang = lang or "English"

        speaker_id = compound_ids.strip().replace(" ", "") or f"S{speaker_number}"
        verb = verb.strip() or "says"

        words = line.strip()
        carried_over = line_ending == "scenetrans (line carried over from previous shot)"
        continues_after = line_ending == "scenetrans (line continues after a cut)"
        cutoff = line_ending == "cutoff (video ends mid-line)"

        if line_ending == "normal" and words and not words.endswith((".", "!", "?", "…")):
            words += "."
        if carried_over:
            words = f"<scenetrans> {words}"
        elif continues_after:
            words = f"{words} <scenetrans>"
        elif cutoff:
            words = f"{words} <cutoff>"

        tagged = f"<d>[{lang}] {words}</d>"

        if delivery == "off-screen voiceover":
            sentence = (
                f"{speaker_description.strip()} ({speaker_id}) {verb} in an "
                f"off-screen voiceover: {tagged} while {pronoun} lips remain "
                "completely closed."
            )
        else:
            sentence = f"{speaker_description.strip()} ({speaker_id}) {verb}: {tagged}"

        if carried_over:
            sentence += f" {pronoun.capitalize()} line carries over from the previous shot."
        elif continues_after:
            sentence += f" {pronoun.capitalize()} line continues seamlessly across the cut."

        return (sentence,)


NODE_CLASS_MAPPINGS = {
    "PipemindH3Dialogue": PipemindH3Dialogue,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PipemindH3Dialogue": "MiniMax H3 Dialogue",
}
