"""
Tests for the MiniMax H3 prompt node family.

Covers:
- 17n+5 frame snapping and two-decimal duration formatting
- Mode-specific alignment lines, including the intentional bracketing
  differences between I2VA/L2VA (<Picture 1>, [Shot N]) and FL2VA (bare)
- Camera sentence construction from the fixed vocabulary
- Dialogue tagging: <d>[Language] ...</d>, voiceover closed-lips clause,
  <cutoff> and <scenetrans> handling
- Lint checks for shots, timestamps, speaker order, and duration agreement
"""

import pytest

from pipemind_h3_common import alignment_line, duration_seconds, snap_length
from pipemind_h3_prompt_assembler import PipemindH3PromptAssembler
from pipemind_h3_camera_move import PipemindH3CameraMove
from pipemind_h3_dialogue import PipemindH3Dialogue
from pipemind_h3_prompt_lint import PipemindH3PromptLint
from tests.conftest import validate_node_structure, validate_node_inputs

VALID_DESCRIPTION = (
    "[Shot 1] Live-action, cinematic, a man stands in a hallway. "
    "The camera pushes in with small amplitude at slow speed. "
    "The man with a low voice (S1) says: <d>[English] Goodbye everyone.</d> "
    "[Shot 2] At 00:03.500, the camera cuts to a close-up of the door."
)


class TestH3Common:
    """Duration math shared by the assembler and lint nodes."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "frames,expected",
        [
            (5, 5),
            (124, 124),
            (125, 141),
            (100, 107),
            (260, 260),
            (3600, 3592),
        ],
    )
    def test_snap_length(self, frames, expected):
        snapped = snap_length(frames)
        assert snapped == expected
        assert (snapped - 5) % 17 == 0

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "frames,expected",
        [
            (124, "5.17"),
            (175, "7.29"),
            (260, "10.83"),
            (345, "14.38"),
        ],
    )
    def test_duration_two_decimals(self, frames, expected):
        assert duration_seconds(frames) == expected

    @pytest.mark.unit
    def test_alignment_bracketing_is_mode_specific(self):
        # FL2VA uses bare Picture/Shot; I2VA and L2VA use angle/square brackets.
        fl = alignment_line("FL2VA", 260, 1)
        assert "Picture 1 (from Shot 1)" in fl
        assert "<Picture" not in fl
        assert "10.83-second mark" in fl

        i2 = alignment_line("I2VA", 124, 1)
        assert "<Picture 1> (from [Shot 1]) is fully referenced." in i2

        l2 = alignment_line("L2VA", 260, 3)
        assert "<Picture 1> (from [Shot 3])" in l2
        assert "10.83-second mark" in l2

        assert alignment_line("T2VA", 124, 1) == ""


class TestPipemindH3PromptAssembler:
    @pytest.fixture
    def node(self):
        return PipemindH3PromptAssembler()

    @pytest.mark.unit
    def test_node_structure(self):
        validate_node_structure(PipemindH3PromptAssembler)
        validate_node_inputs(PipemindH3PromptAssembler)
        assert PipemindH3PromptAssembler.CATEGORY == "Pipemind/MiniMax H3"

    @pytest.mark.unit
    def test_t2va_has_no_alignment_line(self, node):
        prompt, frames = node.assemble(
            "T2VA (text only)", 124, 1, "[Shot 1] A scene.", "Wind.", "N/A"
        )
        assert prompt.startswith("integrated_multimodal_description:")
        assert frames == 124

    @pytest.mark.unit
    def test_fl2va_full_structure(self, node):
        prompt, frames = node.assemble(
            "FL2VA (first + last frame)", 260, 1, "[Shot 1] A scene.", "Wind.", "N/A"
        )
        blocks = prompt.split("\n\n")
        assert len(blocks) == 4
        assert blocks[0].startswith("How the reference pictures align")
        assert "10.83-second mark" in blocks[0]
        assert blocks[1].startswith("integrated_multimodal_description: ")
        assert blocks[2].startswith("overall_soundscape: ")
        assert blocks[3] == "non_diegetic_music: N/A"
        assert frames == 260

    @pytest.mark.unit
    def test_length_snaps_and_feeds_alignment(self, node):
        # 250 is invalid; snaps to 260 and the alignment line must agree.
        prompt, frames = node.assemble(
            "L2VA (last frame)", 250, 2, "[Shot 1] A scene.", "Rain.", "N/A"
        )
        assert frames == 260
        assert "<Picture 1> (from [Shot 2]) aligns with the 10.83-second mark" in prompt

    @pytest.mark.unit
    def test_pasted_field_prefixes_are_stripped(self, node):
        prompt, _ = node.assemble(
            "T2VA (text only)",
            124,
            1,
            "integrated_multimodal_description: [Shot 1] A scene.",
            "overall_soundscape: Wind.",
            "non_diegetic_music: N/A",
        )
        assert prompt.count("integrated_multimodal_description:") == 1
        assert prompt.count("overall_soundscape:") == 1
        assert prompt.count("non_diegetic_music:") == 1

    @pytest.mark.unit
    def test_empty_music_defaults_to_na(self, node):
        prompt, _ = node.assemble("T2VA (text only)", 124, 1, "[Shot 1] A scene.", "Wind.", "")
        assert prompt.endswith("non_diegetic_music: N/A")


class TestPipemindH3CameraMove:
    @pytest.fixture
    def node(self):
        return PipemindH3CameraMove()

    @pytest.mark.unit
    def test_node_structure(self):
        validate_node_structure(PipemindH3CameraMove)

    @pytest.mark.unit
    def test_full_formula(self, node):
        (sentence,) = node.build("Push In", "small", "slow", "he approaches the door")
        assert sentence == (
            "The camera pushes in with small amplitude at slow speed " "as he approaches the door."
        )

    @pytest.mark.unit
    def test_defaults_are_omitted(self, node):
        # Medium amplitude / normal speed are expressed by omission.
        (sentence,) = node.build("Static Shot", "none", "none")
        assert sentence == "The camera holds a static shot."
        assert "amplitude" not in sentence
        assert "speed" not in sentence

    @pytest.mark.unit
    def test_vocabulary_is_complete(self):
        options = PipemindH3CameraMove.INPUT_TYPES()["required"]["motion"][0]
        for term in [
            "Zoom In",
            "Pull Out",
            "Pan Left",
            "Truck Right",
            "Tilt Up",
            "Pedestal Down",
            "Arc Shot",
            "Tracking Shot",
            "Static Shot",
            "Shake Slightly",
            "POV",
            "Roll Clockwise",
        ]:
            assert term in options


class TestPipemindH3Dialogue:
    @pytest.fixture
    def node(self):
        return PipemindH3Dialogue()

    @pytest.mark.unit
    def test_node_structure(self):
        validate_node_structure(PipemindH3Dialogue)

    @pytest.mark.unit
    def test_on_screen_line(self, node):
        (sentence,) = node.build(
            "The older man with a low, quiet voice",
            1,
            "says",
            "English",
            "Goodbye everyone.",
            "on-screen",
            "his",
            "normal",
        )
        assert sentence == (
            "The older man with a low, quiet voice (S1) says: " "<d>[English] Goodbye everyone.</d>"
        )

    @pytest.mark.unit
    def test_voiceover_appends_closed_lips_clause(self, node):
        (sentence,) = node.build(
            "The man",
            1,
            "says",
            "English",
            "I remember that road.",
            "off-screen voiceover",
            "his",
            "normal",
        )
        assert "says in an off-screen voiceover: <d>[English]" in sentence
        assert sentence.endswith("while his lips remain completely closed.")

    @pytest.mark.unit
    def test_cutoff_marker_without_added_period(self, node):
        (sentence,) = node.build(
            "The signalman",
            2,
            "shouts",
            "English",
            "she's coming round",
            "on-screen",
            "his",
            "cutoff (video ends mid-line)",
        )
        assert "<d>[English] she's coming round <cutoff></d>" in sentence

    @pytest.mark.unit
    def test_compound_ids_and_custom_language(self, node):
        (sentence,) = node.build(
            "The two children",
            1,
            "shout together",
            "custom",
            "Wait for us!",
            "on-screen",
            "their",
            "normal",
            custom_language="Welsh",
            compound_ids="S1, S2",
        )
        assert "(S1,S2)" in sentence
        assert "<d>[Welsh] Wait for us!</d>" in sentence

    @pytest.mark.unit
    def test_terminal_punctuation_added_when_missing(self, node):
        (sentence,) = node.build(
            "The man",
            1,
            "says",
            "English",
            "Hello there",
            "on-screen",
            "his",
            "normal",
        )
        assert "<d>[English] Hello there.</d>" in sentence


class TestPipemindH3PromptLint:
    @pytest.fixture
    def node(self):
        return PipemindH3PromptLint()

    @staticmethod
    def make_prompt(
        description=VALID_DESCRIPTION, soundscape="Wind and rain.", music="N/A", first_line=""
    ):
        parts = [first_line] if first_line else []
        parts += [
            f"integrated_multimodal_description: {description}",
            f"overall_soundscape: {soundscape}",
            f"non_diegetic_music: {music}",
        ]
        return "\n\n".join(parts)

    @pytest.mark.unit
    def test_node_structure(self):
        validate_node_structure(PipemindH3PromptLint)

    @pytest.mark.unit
    def test_valid_prompt_passes(self, node):
        report, passed = node.lint(self.make_prompt(), False, 124)
        assert passed, report
        assert "0 error" in report or "OK" in report

    @pytest.mark.unit
    def test_short_description_warns_but_passes(self, node):
        report, passed = node.lint(self.make_prompt(), False)
        assert passed
        assert "WARN" in report and "words" in report

    @pytest.mark.unit
    def test_strict_fails_on_warnings(self, node):
        _, passed = node.lint(self.make_prompt(), True)
        assert not passed

    @pytest.mark.unit
    def test_missing_field_is_error(self, node):
        prompt = "integrated_multimodal_description: [Shot 1] A scene."
        report, passed = node.lint(prompt, False)
        assert not passed
        assert "overall_soundscape" in report

    @pytest.mark.unit
    def test_shot_1_timestamp_is_error(self, node):
        desc = "[Shot 1] At 00:00.000, a scene begins."
        _, passed = node.lint(self.make_prompt(description=desc), False)
        assert not passed

    @pytest.mark.unit
    def test_timestamps_must_increase(self, node):
        desc = (
            "[Shot 1] A scene. [Shot 2] At 00:05.000, a cut. " "[Shot 3] At 00:03.000, another cut."
        )
        report, passed = node.lint(self.make_prompt(description=desc), False)
        assert not passed
        assert "strictly increasing" in report

    @pytest.mark.unit
    def test_timestamp_beyond_duration_is_error(self, node):
        desc = "[Shot 1] A scene. [Shot 2] At 00:09.000, a cut."
        # 124 frames = 5.17 s, so a 9 s cut is invalid.
        report, passed = node.lint(self.make_prompt(description=desc), False, 124)
        assert not passed
        assert "duration" in report

    @pytest.mark.unit
    def test_dialogue_without_language_tag_is_error(self, node):
        desc = "[Shot 1] The man (S1) says: <d>Goodbye everyone.</d>"
        report, passed = node.lint(self.make_prompt(description=desc), False)
        assert not passed
        assert "[Language]" in report

    @pytest.mark.unit
    def test_speaker_order_violation_is_error(self, node):
        desc = (
            "[Shot 1] The man (S2) says: <d>[English] First.</d> "
            "The woman (S1) says: <d>[English] Second.</d>"
        )
        report, passed = node.lint(self.make_prompt(description=desc), False)
        assert not passed
        assert "first vocal event" in report

    @pytest.mark.unit
    def test_l2va_alignment_shot_ref_not_flagged(self, node):
        # The [Shot 2] inside the alignment line must not trip shot checks.
        first = (
            "How the reference pictures align with the target video — "
            "<Picture 1> (from [Shot 2]) aligns with the 5.17-second mark "
            "of the target video."
        )
        desc = "[Shot 1] A scene. [Shot 2] At 00:03.000, the camera cuts to a door."
        report, passed = node.lint(self.make_prompt(description=desc, first_line=first), False, 124)
        assert passed, report

    @pytest.mark.unit
    def test_alignment_duration_mismatch_is_error(self, node):
        first = (
            "How the reference pictures align with the target video — "
            "<Picture 1> (from [Shot 1]) aligns with the 10.00-second mark "
            "of the target video."
        )
        report, passed = node.lint(self.make_prompt(first_line=first), False, 260)
        assert not passed
        assert "10.83" in report

    @pytest.mark.unit
    def test_curly_braces_warn(self, node):
        desc = VALID_DESCRIPTION + " The camera {pushes in|trucks left} slowly."
        report, passed = node.lint(self.make_prompt(description=desc), False)
        assert passed
        assert "curly braces" in report

    @pytest.mark.smoke
    def test_assembler_output_passes_lint(self, node):
        assembler = PipemindH3PromptAssembler()
        prompt, frames = assembler.assemble(
            "FL2VA (first + last frame)",
            260,
            2,
            VALID_DESCRIPTION,
            "Wind and rain throughout.",
            "N/A",
        )
        report, passed = node.lint(prompt, False, frames)
        assert passed, report
