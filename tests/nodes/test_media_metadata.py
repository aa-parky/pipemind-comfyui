"""
Tests for the PipemindMediaMetadata node.

Covers the three metadata dialects the node understands (ComfyUI API prompt
graphs, ComfyUI UI workflows, A1111 parameter strings), the PNG round-trip, and
the node's own contract.
"""

import json

import pytest
from PIL import Image, PngImagePlugin

from pipemind_media_metadata import (
    PipemindMediaMetadata,
    format_report,
    interpret_metadata,
    parse_a1111_parameters,
    parse_api_prompt,
    parse_ui_workflow,
    read_raw_metadata,
    resolve_media_path,
)
from tests.conftest import validate_node_inputs, validate_node_outputs, validate_node_structure


def _api_prompt():
    """A minimal but realistic SD1.5-style API graph."""
    return {
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "dreamshaper_8.safetensors"},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 768, "height": 1024, "batch_size": 2},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "a windswept moor at dusk", "clip": ["10", 1]},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "blurry, watermark", "clip": ["10", 1]},
        },
        "10": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "film_grain.safetensors",
                "strength_model": 0.75,
                "strength_clip": 0.6,
                "model": ["4", 0],
                "clip": ["4", 1],
            },
        },
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 987654321,
                "steps": 28,
                "cfg": 7.5,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["10", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
    }


class TestNodeContract:
    """The ComfyUI-facing shape of the node."""

    @pytest.mark.unit
    def test_node_structure(self):
        validate_node_structure(PipemindMediaMetadata)

    @pytest.mark.unit
    def test_input_types(self):
        inputs = validate_node_inputs(PipemindMediaMetadata)
        assert "file" in inputs["required"]
        assert "detail" in inputs["required"]
        assert "path_override" in inputs["optional"]
        assert inputs["required"]["detail"][0] == ["summary", "full", "raw json"]

    @pytest.mark.unit
    def test_return_names_match_types(self):
        assert len(PipemindMediaMetadata.RETURN_TYPES) == len(PipemindMediaMetadata.RETURN_NAMES)
        assert PipemindMediaMetadata.RETURN_NAMES[0] == "report"
        assert PipemindMediaMetadata.CATEGORY == "Pipemind"

    @pytest.mark.unit
    def test_missing_file_does_not_raise(self):
        output = PipemindMediaMetadata().read(file="nope.png", detail="summary")

        assert "File not found" in output["ui"]["text"][0]
        validate_node_outputs(PipemindMediaMetadata, output["result"])
        assert output["result"][-1] is False


class TestApiPromptParsing:
    """Reading a ComfyUI API prompt graph."""

    @pytest.mark.unit
    def test_core_settings(self):
        info = parse_api_prompt(_api_prompt())

        assert info["seed"] == 987654321
        assert info["steps"] == 28
        assert info["cfg"] == 7.5
        assert info["sampler"] == "dpmpp_2m"
        assert info["scheduler"] == "karras"
        assert info["denoise"] == 1.0

    @pytest.mark.unit
    @pytest.mark.prompt
    def test_prompts_and_model(self):
        info = parse_api_prompt(_api_prompt())

        assert info["positive"] == "a windswept moor at dusk"
        assert info["negative"] == "blurry, watermark"
        # Resolved through the LoRA loader back to the checkpoint.
        assert info["model"] == "dreamshaper_8.safetensors"

    @pytest.mark.unit
    def test_dimensions_and_loras(self):
        info = parse_api_prompt(_api_prompt())

        assert (info["width"], info["height"]) == (768, 1024)
        assert info["batch_size"] == 2
        assert info["loras"] == [
            {"name": "film_grain.safetensors", "strength_model": 0.75, "strength_clip": 0.6}
        ]

    @pytest.mark.unit
    def test_prompt_found_through_conditioning_chain(self):
        """A guidance node between the encoder and the sampler must not hide the text."""
        prompt = _api_prompt()
        prompt["11"] = {
            "class_type": "FluxGuidance",
            "inputs": {"conditioning": ["6", 0], "guidance": 3.5},
        }
        prompt["3"]["inputs"]["positive"] = ["11", 0]

        assert parse_api_prompt(prompt)["positive"] == "a windswept moor at dusk"

    @pytest.mark.unit
    def test_seed_resolved_through_primitive_node(self):
        """Seeds are often converted to an input wired from a primitive."""
        prompt = _api_prompt()
        prompt["20"] = {"class_type": "PrimitiveNode", "inputs": {"value": 42}}
        prompt["3"]["inputs"]["seed"] = ["20", 0]

        assert parse_api_prompt(prompt)["seed"] == 42

    @pytest.mark.unit
    def test_split_flux_style_sampler(self):
        """Steps/sampler/seed living in upstream nodes are still collected."""
        prompt = {
            "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux1-dev.safetensors"}},
            "2": {"class_type": "RandomNoise", "inputs": {"noise_seed": 555}},
            "3": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
            "4": {
                "class_type": "BasicScheduler",
                "inputs": {"scheduler": "simple", "steps": 20, "denoise": 1.0, "model": ["1", 0]},
            },
            "5": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["2", 0],
                    "guider": ["6", 0],
                    "sampler": ["3", 0],
                    "sigmas": ["4", 0],
                    "latent_image": ["7", 0],
                },
            },
            "6": {
                "class_type": "BasicGuider",
                "inputs": {"model": ["1", 0], "conditioning": ["8", 0]},
            },
            "7": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024}},
            "8": {"class_type": "CLIPTextEncode", "inputs": {"text": "a brass orrery"}},
        }

        info = parse_api_prompt(prompt)

        assert info["seed"] == 555
        assert info["steps"] == 20
        assert info["sampler"] == "euler"
        assert info["scheduler"] == "simple"
        assert info["positive"] == "a brass orrery"
        assert info["model"] == "flux1-dev.safetensors"
        assert (info["width"], info["height"]) == (1024, 1024)


class TestOtherDialects:
    """UI workflows and A1111 parameter strings."""

    @pytest.mark.unit
    def test_ui_workflow_fallback(self):
        workflow = {
            "nodes": [
                {
                    "type": "KSampler",
                    "widgets_values": [12345, "randomize", 25, 8.0, "euler", "normal", 1.0],
                },
                {
                    "type": "CLIPTextEncode",
                    "widgets_values": ["a long descriptive positive prompt"],
                },
                {"type": "CLIPTextEncode", "widgets_values": ["bad"]},
                {"type": "EmptyLatentImage", "widgets_values": [512, 768, 1]},
                {
                    "type": "CheckpointLoaderSimple",
                    "widgets_values": ["sd_xl_base_1.0.safetensors"],
                },
            ]
        }

        info = parse_ui_workflow(workflow)

        assert info["seed"] == 12345
        assert info["steps"] == 25
        assert info["cfg"] == 8.0
        assert info["sampler"] == "euler"
        assert info["scheduler"] == "normal"
        assert info["positive"] == "a long descriptive positive prompt"
        assert info["negative"] == "bad"
        assert (info["width"], info["height"]) == (512, 768)
        assert info["model"] == "sd_xl_base_1.0.safetensors"

    @pytest.mark.unit
    def test_a1111_parameters(self):
        text = (
            "a cottage in the snow, lantern light\n"
            "Negative prompt: lowres, jpeg artifacts\n"
            "Steps: 30, Sampler: DPM++ 2M, Schedule type: Karras, CFG scale: 6.5, "
            "Seed: 1122334455, Size: 640x896, Model: revAnimated_v122"
        )

        info = parse_a1111_parameters(text)

        assert info["positive"] == "a cottage in the snow, lantern light"
        assert info["negative"] == "lowres, jpeg artifacts"
        assert info["steps"] == 30
        assert info["cfg"] == 6.5
        assert info["seed"] == 1122334455
        assert info["sampler"] == "DPM++ 2M"
        assert info["scheduler"] == "Karras"
        assert (info["width"], info["height"]) == (640, 896)
        assert info["model"] == "revAnimated_v122"

    @pytest.mark.unit
    def test_no_metadata_is_reported_not_raised(self):
        info = interpret_metadata({})

        assert info["source"] == "none"
        assert info["seed"] is None
        assert info["loras"] == []

    @pytest.mark.unit
    def test_prefixed_json_is_unwrapped(self, tmp_path):
        """ComfyUI writes EXIF/container tags as 'prompt:{...}', not bare JSON."""
        from pipemind_media_metadata import _store_candidate

        raw = {}
        _store_candidate(raw, "Model", "prompt:" + json.dumps(_api_prompt()))

        assert "prompt" in raw
        assert interpret_metadata(raw)["seed"] == 987654321

    @pytest.mark.unit
    def test_wrapped_graph_is_lifted_out_of_container_tag(self):
        """VideoHelperSuite packs both graphs into one tag: {"prompt": ..., "workflow": ...}."""
        from pipemind_media_metadata import _store_candidate

        raw = {}
        _store_candidate(
            raw, "comment", json.dumps({"prompt": _api_prompt(), "workflow": {"nodes": []}})
        )

        assert "prompt" in raw and "workflow" in raw
        assert interpret_metadata(raw)["steps"] == 28


class TestEndToEnd:
    """Reading a real file from disk."""

    @pytest.fixture
    def comfy_png(self, tmp_path):
        """A PNG carrying ComfyUI-style prompt/workflow text chunks."""
        path = tmp_path / "ComfyUI_00001_.png"
        info = PngImagePlugin.PngInfo()
        info.add_text("prompt", json.dumps(_api_prompt()))
        info.add_text("workflow", json.dumps({"nodes": []}))
        Image.new("RGB", (64, 48), "navy").save(path, pnginfo=info)
        return path

    @pytest.mark.unit
    @pytest.mark.image
    def test_round_trip_from_png(self, comfy_png):
        raw, container = read_raw_metadata(str(comfy_png))

        assert container["format"] == "PNG"
        assert (container["width"], container["height"]) == (64, 48)
        assert container["size_bytes"] > 0
        assert interpret_metadata(raw)["seed"] == 987654321

    @pytest.mark.unit
    @pytest.mark.image
    def test_node_reads_via_path_override(self, comfy_png):
        output = PipemindMediaMetadata().read(
            file="[no media files found]", detail="summary", path_override=str(comfy_png)
        )
        report, positive, negative, seed, steps, cfg = output["result"][:6]

        validate_node_outputs(PipemindMediaMetadata, output["result"])
        assert output["result"][-1] is True
        assert seed == 987654321
        assert steps == 28
        assert cfg == 7.5
        assert positive == "a windswept moor at dusk"
        assert negative == "blurry, watermark"
        assert "dreamshaper_8.safetensors" in report
        assert "dpmpp_2m / karras" in report
        assert "768 × 1024 (batch 2)" in report
        assert output["ui"]["text"][0] == report

    @pytest.mark.unit
    def test_raw_json_detail_returns_parsable_json(self, comfy_png):
        output = PipemindMediaMetadata().read(
            file="", detail="raw json", path_override=str(comfy_png)
        )

        assert json.loads(output["result"][11])["prompt"]["3"]["inputs"]["steps"] == 28

    @pytest.mark.unit
    def test_full_detail_lists_node_types(self, comfy_png):
        output = PipemindMediaMetadata().read(file="", detail="full", path_override=str(comfy_png))

        assert "Node types" in output["result"][0]
        assert "• KSampler" in output["result"][0]

    @pytest.mark.unit
    @pytest.mark.image
    def test_plain_image_reports_missing_metadata(self, tmp_path):
        path = tmp_path / "plain.png"
        Image.new("RGB", (16, 16), "white").save(path)

        output = PipemindMediaMetadata().read(file="", detail="summary", path_override=str(path))

        assert output["result"][-1] is False
        assert "none found" in output["result"][0]
        assert output["result"][3] == 0

    @pytest.mark.unit
    def test_is_changed_tracks_file_contents(self, comfy_png):
        first = PipemindMediaMetadata.IS_CHANGED(file="", path_override=str(comfy_png))
        second = PipemindMediaMetadata.IS_CHANGED(file="", path_override=str(comfy_png))
        missing = PipemindMediaMetadata.IS_CHANGED(file="", path_override="/nope/nope.png")

        assert first == second
        assert first != missing

    @pytest.mark.unit
    def test_resolve_path_handles_absolute_and_missing(self, comfy_png):
        assert resolve_media_path("", str(comfy_png)) == str(comfy_png)
        assert resolve_media_path("[no media files found]") is None
        assert resolve_media_path("", "  ") is None

    @pytest.mark.smoke
    def test_report_is_readable(self, comfy_png):
        raw, container = read_raw_metadata(str(comfy_png))
        report = format_report(
            "output/ComfyUI_00001_.png", container, interpret_metadata(raw), raw, "summary"
        )

        for expected in (
            "Seed",
            "Steps",
            "CFG",
            "Sampler",
            "Positive prompt",
            "Negative prompt",
            "LoRAs",
        ):
            assert expected in report
