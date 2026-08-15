import re
from typing import List, Tuple

try:
    from .pipemind_h3_common import (
        FIELD_DESCRIPTION,
        FIELD_MUSIC,
        FIELD_SOUNDSCAPE,
        duration_seconds,
    )
except ImportError:  # top-level import (tests)
    from pipemind_h3_common import (
        FIELD_DESCRIPTION,
        FIELD_MUSIC,
        FIELD_SOUNDSCAPE,
        duration_seconds,
    )

WORD_COUNT_MIN = 350
WORD_COUNT_MAX = 500


class PipemindH3PromptLint:
    """
    Validate a MiniMax H3 base-mode prompt against the official grammar.

    Errors (structural violations that break the prompt format):
    - a required field label missing or duplicated
    - a timestamp on [Shot 1]
    - shot numbers out of sequence, or cut timestamps not strictly increasing
    - a timestamp at or beyond the video duration (when `length` is wired in)
    - a <d> block without a leading [Language] tag
    - speaker IDs whose first appearances are out of numeric order
    - an alignment-line duration that disagrees with the wired `length`
    - <cutoff> anywhere except the final dialogue block

    Warnings (advisory):
    - main description outside the 350-500 word range the model expects
    - curly braces, which ComfyUI's dynamic_prompts widget parsing would
      consume if this text were ever pasted back into a prompt widget
    - an empty overall_soundscape (valid only for deliberate total silence)

    `pass` is true when there are no errors; with `strict` enabled, warnings
    also fail. Pair it with Boolean Switch (Any) to gate queuing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"forceInput": True}),
                "strict": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "length": ("INT", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("report", "pass")
    FUNCTION = "lint"
    CATEGORY = "Pipemind/MiniMax H3"

    @staticmethod
    def _timestamp_to_seconds(mm: str, ss: str, mmm: str) -> float:
        return int(mm) * 60 + int(ss) + int(mmm) / 1000.0

    def lint(self, prompt: str, strict: bool, length: int = 0) -> Tuple[str, bool]:
        errors: List[str] = []
        warnings: List[str] = []

        # --- field structure ---
        for field in (FIELD_DESCRIPTION, FIELD_SOUNDSCAPE, FIELD_MUSIC):
            count = len(re.findall(rf"{field}:", prompt))
            if count == 0:
                errors.append(f"missing field '{field}:'")
            elif count > 1:
                errors.append(f"field '{field}:' appears {count} times")

        desc_match = re.search(
            rf"{FIELD_DESCRIPTION}:(.*?)(?=\n\s*{FIELD_SOUNDSCAPE}:|\Z)",
            prompt,
            re.S,
        )
        description = desc_match.group(1).strip() if desc_match else ""

        sound_match = re.search(
            rf"{FIELD_SOUNDSCAPE}:(.*?)(?=\n\s*{FIELD_MUSIC}:|\Z)", prompt, re.S
        )
        soundscape = sound_match.group(1).strip() if sound_match else ""
        if sound_match and not soundscape:
            warnings.append(
                "overall_soundscape is empty; H3 generates audio jointly, so "
                "an empty soundscape wastes half the model (use 'N/A' only "
                "for deliberate total silence)"
            )

        # --- word count (advisory) ---
        if description:
            words = len(description.split())
            if words < WORD_COUNT_MIN:
                warnings.append(
                    f"description is {words} words; the model expects "
                    f"{WORD_COUNT_MIN}-{WORD_COUNT_MAX} for generation tasks"
                )
            elif words > WORD_COUNT_MAX:
                warnings.append(
                    f"description is {words} words; the model expects "
                    f"{WORD_COUNT_MIN}-{WORD_COUNT_MAX} for generation tasks"
                )

        # --- shots and timestamps ---
        # Analyze the description body only: the L2VA/I2VA alignment line
        # legitimately contains a bracketed [Shot N] of its own.
        shot_text = description if description else prompt

        if re.search(r"\[Shot 1\]\s+At \d", shot_text):
            errors.append("[Shot 1] must not carry a timestamp")

        shot_numbers = [int(n) for n in re.findall(r"\[Shot (\d+)\]", shot_text)]
        if shot_numbers and shot_numbers != list(range(1, len(shot_numbers) + 1)):
            errors.append(f"shot numbers {shot_numbers} are not sequential from 1")

        stamps = re.findall(r"\[Shot \d+\] At (\d{2}):(\d{2})\.(\d{3})", shot_text)
        seconds = [self._timestamp_to_seconds(*s) for s in stamps]
        if seconds != sorted(seconds) or len(set(seconds)) != len(seconds):
            errors.append(f"cut timestamps {seconds} are not strictly increasing")

        malformed = re.findall(r"\[Shot [2-9]\d*\](?!\s+At \d{2}:\d{2}\.\d{3})", shot_text)
        if malformed:
            errors.append(
                f"{len(malformed)} shot(s) after [Shot 1] lack a valid " "'At MM:SS.mmm' timestamp"
            )

        duration = None
        if length:
            duration = length / 24.0
            late = [s for s in seconds if s >= duration]
            if late:
                errors.append(f"timestamp(s) {late} at or beyond the {duration:.2f}s duration")

        # --- alignment line vs duration ---
        aligned = re.findall(r"aligns with the (\d+\.\d{2})-second mark", prompt)
        if aligned and length:
            expected = duration_seconds(length)
            final_mark = aligned[-1]
            if final_mark != expected and final_mark != "0.00":
                errors.append(
                    f"alignment line ends at {final_mark}s but length={length} "
                    f"frames gives {expected}s"
                )

        # --- dialogue blocks ---
        for block in re.findall(r"<d>(.*?)</d>", prompt, re.S):
            if not re.match(r"\[[^\]]+\]\s", block):
                errors.append(f"<d> block missing leading [Language] tag: '{block[:40]}...'")

        open_d, close_d = prompt.count("<d>"), prompt.count("</d>")
        if open_d != close_d:
            errors.append(f"unbalanced dialogue tags: {open_d} <d> vs {close_d} </d>")

        # --- speaker ID ordering ---
        first_seen: List[int] = []
        for match in re.findall(r"\((S\d+(?:,\s*S\d+)*)\)", prompt):
            for sid in re.findall(r"S(\d+)", match):
                n = int(sid)
                if n not in first_seen:
                    first_seen.append(n)
        if first_seen and first_seen != sorted(first_seen):
            errors.append(
                f"speaker IDs first appear in order {first_seen}; they must be "
                "assigned in order of first vocal event (S1 speaks first)"
            )

        # --- cutoff placement ---
        cutoff_count = prompt.count("<cutoff>")
        if cutoff_count > 1:
            errors.append("<cutoff> appears more than once")
        elif cutoff_count == 1:
            last_block = re.findall(r"<d>.*?</d>", prompt, re.S)
            if last_block and "<cutoff>" not in last_block[-1]:
                errors.append(
                    "<cutoff> must sit in the final dialogue block (it marks "
                    "speech truncated by the end of the video)"
                )

        # --- wildcard hazard ---
        if re.search(r"\{[^{}]*\}", prompt):
            warnings.append(
                "curly braces present; ComfyUI dynamic_prompts parsing will "
                "consume {a|b} if this text is pasted into a prompt widget"
            )

        # --- report ---
        passed = not errors and not (strict and warnings)
        if not errors and not warnings:
            report = "H3 prompt lint: OK - no issues found."
        else:
            lines = [f"H3 prompt lint: {len(errors)} error(s), {len(warnings)} warning(s)"]
            lines += [f"ERROR: {e}" for e in errors]
            lines += [f"WARN: {w}" for w in warnings]
            report = "\n".join(lines)

        return (report, passed)


NODE_CLASS_MAPPINGS = {
    "PipemindH3PromptLint": PipemindH3PromptLint,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PipemindH3PromptLint": "MiniMax H3 Prompt Lint",
}
