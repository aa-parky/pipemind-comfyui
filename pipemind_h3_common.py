"""
Shared constants and helpers for the MiniMax H3 prompt nodes.

The grammar encoded here follows the official MiniMax base prompt guide
(VIDEO_PROMPT_WRITING_GUIDE_base_en.md) and the ComfyUI H3 node source
(nodes_minimax_h3.py): 24 fps, frame counts on the 17n+5 grid, mode-specific
alignment instructions, and the fixed camera-motion vocabulary.
"""

H3_FPS = 24
H3_MIN_FRAMES = 5
H3_MAX_FRAMES = 3600
H3_FRAME_STEP = 17

# Mode widget labels -> internal mode token
H3_MODES = {
    "T2VA (text only)": "T2VA",
    "I2VA (first frame)": "I2VA",
    "FL2VA (first + last frame)": "FL2VA",
    "L2VA (last frame)": "L2VA",
}

# Camera motion vocabulary: widget label -> sentence fragment.
# Phrasing follows the guide's own examples ("The camera pushes in with
# small amplitude at slow speed ...", "The camera holds a static shot ...").
H3_CAMERA_PHRASES = {
    "Static Shot": "The camera holds a static shot",
    "Push In": "The camera pushes in",
    "Pull Out": "The camera pulls out",
    "Zoom In": "The camera zooms in",
    "Zoom Out": "The camera zooms out",
    "Pan Left": "The camera pans left",
    "Pan Right": "The camera pans right",
    "Truck Left": "The camera trucks left",
    "Truck Right": "The camera trucks right",
    "Tilt Up": "The camera tilts up",
    "Tilt Down": "The camera tilts down",
    "Pedestal Up": "The camera pedestals up",
    "Pedestal Down": "The camera pedestals down",
    "Arc Shot": "The camera arcs around the subject",
    "Tracking Shot": "The camera tracks the subject",
    "Shake Slightly": "The camera shakes slightly",
    "Shake Strongly": "The camera shakes strongly",
    "Roll Clockwise": "The camera rolls clockwise",
    "Roll Counterclockwise": "The camera rolls counterclockwise",
    "POV": "The shot holds the subject's point of view",
}

H3_LANGUAGES = [
    "English",
    "Mandarin Chinese",
    "Japanese",
    "Korean",
    "French",
    "German",
    "Spanish",
    "Italian",
    "Portuguese",
    "Russian",
    "Arabic",
    "Hindi",
    "custom",
]

FIELD_DESCRIPTION = "integrated_multimodal_description"
FIELD_SOUNDSCAPE = "overall_soundscape"
FIELD_MUSIC = "non_diegetic_music"


def snap_length(frames: int) -> int:
    """Snap a frame count up to the model's valid 17n+5 grid."""
    frames = max(H3_MIN_FRAMES, min(H3_MAX_FRAMES, int(frames)))
    remainder = (frames - H3_MIN_FRAMES) % H3_FRAME_STEP
    if remainder:
        frames += H3_FRAME_STEP - remainder
        if frames > H3_MAX_FRAMES:
            # The ceiling itself may be off-grid; take the last valid count below it.
            frames -= H3_FRAME_STEP
    return frames


def duration_seconds(frames: int) -> str:
    """Effective duration at 24 fps, formatted to exactly two decimals."""
    return f"{frames / H3_FPS:.2f}"


def alignment_line(mode: str, frames: int, final_shot: int) -> str:
    """
    Build the mode-specific first-line alignment instruction.

    The bracketing genuinely differs between modes in the official guide:
    FL2VA uses bare `Picture 1` / `Shot 1`, while I2VA and L2VA use
    `<Picture 1>` / `[Shot 1]`. That asymmetry is intentional.
    """
    seconds = duration_seconds(frames)
    if mode == "T2VA":
        return ""
    if mode == "I2VA":
        return (
            "For the target video, at 0.00 seconds into the target video, "
            "<Picture 1> (from [Shot 1]) is fully referenced."
        )
    if mode == "FL2VA":
        return (
            "How the reference pictures align with the target video — "
            "Picture 1 (from Shot 1) aligns with the 0.00-second mark of the "
            f"target video; Picture 2 (from Shot {final_shot}) aligns with "
            f"the {seconds}-second mark of the target video."
        )
    if mode == "L2VA":
        return (
            "How the reference pictures align with the target video — "
            f"<Picture 1> (from [Shot {final_shot}]) aligns with the "
            f"{seconds}-second mark of the target video."
        )
    raise ValueError(f"Unknown H3 mode: {mode}")
