"""
Pipemind Media Metadata Reader.

Loads an image or a video that was produced in ComfyUI and displays the
embedded generation metadata - seed, steps, cfg, sampler, scheduler, prompts,
model and LoRAs - as a neatly formatted report, plus typed outputs that can be
wired into the rest of a workflow.

Where the metadata comes from:

* **PNG** - ``tEXt``/``iTXt`` chunks. ComfyUI writes ``prompt`` (API graph) and
  ``workflow`` (UI graph); A1111-style tools write ``parameters``.
* **JPEG / WebP / TIFF** - EXIF. ComfyUI's animated-WebP saver writes
  ``prompt:{...}`` / ``workflow:{...}`` into the Make/Model tags; A1111 writes
  its parameter string into ``UserComment``.
* **MP4 / WebM / MKV / MOV** - container tags, read with ``ffprobe`` when it is
  on PATH. Without ``ffprobe`` the file is byte-scanned for embedded JSON,
  which still recovers metadata from most VideoHelperSuite renders.

Only the standard library and Pillow are required. ``ffprobe`` is optional and
only improves video support.
"""

import json
import os
import re
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

try:  # Available inside a real ComfyUI install, absent when running tests.
    import folder_paths  # type: ignore
except Exception:  # noqa: BLE001 - the node must stay importable outside ComfyUI
    folder_paths = None


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".avif"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v", ".gif"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

NO_FILES = "[no media files found]"

# How many entries the file dropdown is allowed to hold. Output folders get
# very large and a multi-thousand entry combo is unusable in the browser.
MAX_LISTED_FILES = 500

# Guard rails for the ffprobe-less video fallback.
_SCAN_CHUNK = 8 * 1024 * 1024
_SCAN_MARKERS = (b'"workflow"', b'"prompt"', b'"extra_pnginfo"', b'"class_type"')

_PREFIXED_JSON_RE = re.compile(
    r"^\s*([A-Za-z0-9_ .\-]{1,40})\s*[:=]\s*([\[{].*[\]}])\s*$", re.DOTALL
)

# Values from control_after_generate / add_noise style widgets. They sit in the
# middle of a KSampler's widgets_values and must not be mistaken for a sampler
# or scheduler name.
_WIDGET_FLAG_VALUES = {
    "fixed",
    "increment",
    "decrement",
    "randomize",
    "enable",
    "disable",
    "true",
    "false",
}

_TEXT_INPUT_KEYS = (
    "text",
    "prompt",
    "string",
    "text_g",
    "text_l",
    "populated_text",
    "wildcard_text",
)
_MODEL_INPUT_KEYS = ("ckpt_name", "unet_name", "checkpoint_name", "model_name", "model_path")
_SCALAR_PASSTHROUGH_KEYS = ("value", "Value", "int", "float", "number", "seed", "text", "string")


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------


def _comfy_dir(kind: str) -> Optional[str]:
    """Resolve ComfyUI's input/output/temp directory, with an offline fallback."""
    if folder_paths is not None:
        getter = getattr(folder_paths, f"get_{kind}_directory", None)
        if callable(getter):
            try:
                return getter()
            except Exception:  # noqa: BLE001
                pass
    guess = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", kind))
    return guess if os.path.isdir(guess) else None


def list_media_files(limit: int = MAX_LISTED_FILES) -> List[str]:
    """
    List media files from ComfyUI's input and output directories.

    Entries are returned as ``input/<relative path>`` or ``output/<relative
    path>`` so a single dropdown can address both trees unambiguously, sorted
    newest first - when you want to inspect metadata you almost always want the
    render you just made.
    """
    found: List[Tuple[float, str]] = []

    for kind in ("input", "output"):
        base = _comfy_dir(kind)
        if not base or not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in files:
                if os.path.splitext(name)[1].lower() not in MEDIA_EXTENSIONS:
                    continue
                full = os.path.join(root, name)
                try:
                    mtime = os.path.getmtime(full)
                except OSError:
                    continue
                rel = os.path.relpath(full, base).replace("\\", "/")
                found.append((mtime, f"{kind}/{rel}"))

    found.sort(key=lambda item: (-item[0], item[1]))
    return [entry for _, entry in found[:limit]]


def resolve_media_path(selection: str, path_override: str = "") -> Optional[str]:
    """
    Turn a dropdown selection (or a manual path) into an absolute file path.

    ``path_override`` wins when it is non-empty, which is how you reach files
    that live outside ComfyUI's own folders.
    """
    candidate = (path_override or "").strip().strip('"').strip("'")
    if not candidate:
        candidate = (selection or "").strip()
    if not candidate or candidate == NO_FILES:
        return None

    candidate = os.path.expanduser(candidate)
    if os.path.isabs(candidate):
        return candidate if os.path.isfile(candidate) else None

    normalised = candidate.replace("\\", "/")
    head, _, tail = normalised.partition("/")
    if head in ("input", "output", "temp") and tail:
        base = _comfy_dir(head)
        if base:
            full = os.path.join(base, *tail.split("/"))
            if os.path.isfile(full):
                return full

    # Bare filename, or a path relative to one of the ComfyUI folders.
    for kind in ("input", "output", "temp"):
        base = _comfy_dir(kind)
        if not base:
            continue
        full = os.path.join(base, *normalised.split("/"))
        if os.path.isfile(full):
            return full

    return candidate if os.path.isfile(candidate) else None


# ---------------------------------------------------------------------------
# Raw metadata extraction
# ---------------------------------------------------------------------------


def _decode_bytes(value: bytes) -> Optional[str]:
    """Best-effort decode of an EXIF byte string, including UserComment blobs."""
    body = value
    for prefix, codec in (
        (b"UNICODE\x00", "utf-16"),
        (b"ASCII\x00\x00\x00", "ascii"),
        (b"JIS\x00\x00\x00\x00\x00", "shift_jis"),
        (b"\x00" * 8, "utf-8"),
    ):
        if body.startswith(prefix):
            body = body[len(prefix) :]
            for attempt in (codec, "utf-16-be", "utf-16-le", "utf-8", "latin-1"):
                try:
                    return body.decode(attempt).rstrip("\x00")
                except (UnicodeDecodeError, LookupError):
                    continue
            break

    for codec in ("utf-8", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            text = body.decode(codec).rstrip("\x00")
        except (UnicodeDecodeError, LookupError):
            continue
        if not text:
            continue
        printable = sum(1 for char in text if char.isprintable() or char in "\r\n\t")
        if printable / len(text) > 0.9:
            return text
    return None


def _store_candidate(raw: Dict[str, Any], key: str, text: Any) -> None:
    """
    Record one metadata string, parsing it into JSON when it is JSON.

    ComfyUI stores its graphs either as bare JSON (PNG text chunks) or as
    ``workflow:{...}`` style prefixed JSON (EXIF, video container tags), so both
    shapes are unwrapped here and filed under a normalised key.
    """
    if isinstance(text, bytes):
        text = _decode_bytes(text)
    if text is None:
        return
    if not isinstance(text, str):
        text = str(text)

    text = text.strip()
    if not text:
        return

    if text[0] in "{[":
        try:
            _store_parsed(raw, key, json.loads(text))
            return
        except (ValueError, TypeError):
            pass

    match = _PREFIXED_JSON_RE.match(text)
    if match:
        label, payload = match.group(1).strip().lower(), match.group(2)
        try:
            _store_parsed(raw, label or key, json.loads(payload))
            return
        except (ValueError, TypeError):
            pass

    raw.setdefault(key, text)


def _store_parsed(raw: Dict[str, Any], key: str, parsed: Any) -> None:
    """
    File a parsed JSON blob, lifting a wrapped graph up to the top level.

    VideoHelperSuite stores both graphs inside a single container tag as
    ``{"prompt": ..., "workflow": ...}``, so unwrap that here rather than
    leaving the graphs buried under the tag name.
    """
    raw.setdefault(key, parsed)
    if isinstance(parsed, dict):
        for inner in ("prompt", "workflow"):
            value = parsed.get(inner)
            if isinstance(value, (dict, list)):
                raw.setdefault(inner, value)


def _read_image_metadata(path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Pull text chunks and EXIF out of a still or animated image."""
    raw: Dict[str, Any] = {}
    info: Dict[str, Any] = {"kind": "image"}

    with Image.open(path) as img:
        info["format"] = img.format or os.path.splitext(path)[1].lstrip(".").upper()
        info["width"], info["height"] = img.size
        frames = getattr(img, "n_frames", 1)
        if isinstance(frames, int) and frames > 1:
            info["frames"] = frames

        for key, value in (img.info or {}).items():
            if key in ("exif", "icc_profile", "xmp", "dpi", "transparency", "background"):
                continue
            _store_candidate(raw, str(key), value)

        try:
            exif = img.getexif()
        except Exception:  # noqa: BLE001 - some formats have no EXIF support at all
            exif = None

        if exif:
            from PIL.ExifTags import TAGS  # local import: only needed on this path

            entries = dict(exif)
            for ifd_getter in ("get_ifd",):
                getter = getattr(exif, ifd_getter, None)
                if not callable(getter):
                    continue
                for ifd_tag in (0x8769, 0x8825):  # Exif IFD, GPS IFD
                    try:
                        entries.update(getter(ifd_tag) or {})
                    except Exception:  # noqa: BLE001
                        continue
            for tag, value in entries.items():
                if not isinstance(value, (str, bytes)):
                    continue
                _store_candidate(raw, str(TAGS.get(tag, f"exif_{tag}")), value)

    return raw, info


def _ffprobe_path() -> Optional[str]:
    return os.environ.get("FFPROBE_PATH") or shutil.which("ffprobe")


def _read_video_metadata(path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Read container tags from a video, preferring ffprobe over a byte scan."""
    raw: Dict[str, Any] = {}
    info: Dict[str, Any] = {
        "kind": "video",
        "format": os.path.splitext(path)[1].lstrip(".").upper(),
    }

    probe = _ffprobe_path()
    if probe:
        try:
            result = subprocess.run(
                [
                    probe,
                    "-v",
                    "quiet",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    path,
                ],
                capture_output=True,
                timeout=30,
                check=False,
            )
            payload = json.loads(result.stdout.decode("utf-8", "replace")) if result.stdout else {}
        except (OSError, ValueError, subprocess.SubprocessError):
            payload = {}

        fmt = payload.get("format") or {}
        if fmt.get("format_long_name"):
            info["format"] = fmt["format_long_name"]
        if fmt.get("duration"):
            try:
                info["duration"] = float(fmt["duration"])
            except (TypeError, ValueError):
                pass

        tag_sets = [fmt.get("tags") or {}]
        for stream in payload.get("streams") or []:
            if stream.get("codec_type") == "video":
                info.setdefault("width", stream.get("width"))
                info.setdefault("height", stream.get("height"))
                if stream.get("nb_frames"):
                    try:
                        info["frames"] = int(stream["nb_frames"])
                    except (TypeError, ValueError):
                        pass
                if stream.get("codec_name"):
                    info["codec"] = stream["codec_name"]
            tag_sets.append(stream.get("tags") or {})

        for tags in tag_sets:
            for key, value in tags.items():
                _store_candidate(raw, str(key), value)
        info["reader"] = "ffprobe"

    if not _has_graph(raw):
        for key, value in _scan_file_for_json(path).items():
            raw.setdefault(key, value)
        info.setdefault("reader", "byte scan")

    return raw, info


def _scan_file_for_json(path: str) -> Dict[str, Any]:
    """
    Recover embedded JSON from a container we cannot parse properly.

    Reads a bounded window from each end of the file, finds the marker keys
    ComfyUI graphs always contain, then walks backwards to the enclosing ``{``
    and decodes from there. Enough to rescue VideoHelperSuite MP4s on machines
    with no ffprobe installed.
    """
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as handle:
            head = handle.read(_SCAN_CHUNK)
            if size > _SCAN_CHUNK * 2:
                handle.seek(-_SCAN_CHUNK, os.SEEK_END)
                tail = handle.read(_SCAN_CHUNK)
            else:
                tail = handle.read()
    except OSError:
        return {}

    found: Dict[str, Any] = {}
    decoder = json.JSONDecoder()

    for blob in (head, tail):
        text = blob.decode("utf-8", "replace")
        for marker in _SCAN_MARKERS:
            start = 0
            marker_text = marker.decode("ascii")
            while True:
                hit = text.find(marker_text, start)
                if hit < 0:
                    break
                start = hit + 1
                # Walk back through the nearest few '{' openers; the first one
                # that decodes into an object covering the marker is the graph.
                cursor = hit
                for _ in range(64):
                    cursor = text.rfind("{", 0, cursor)
                    if cursor < 0:
                        break
                    try:
                        parsed, end = decoder.raw_decode(text, cursor)
                    except ValueError:
                        continue
                    if end <= hit or not isinstance(parsed, dict):
                        continue
                    for key in ("prompt", "workflow"):
                        if key in parsed and isinstance(parsed[key], (dict, list)):
                            found.setdefault(key, parsed[key])
                    if _looks_like_api_graph(parsed):
                        found.setdefault("prompt", parsed)
                    elif isinstance(parsed.get("nodes"), list):
                        found.setdefault("workflow", parsed)
                    break

    return found


def _looks_like_api_graph(data: Any) -> bool:
    """True when ``data`` is a ComfyUI API prompt: {node_id: {class_type, inputs}}."""
    if not isinstance(data, dict) or not data:
        return False
    for value in data.values():
        if isinstance(value, dict) and "class_type" in value:
            return True
    return False


def _has_graph(raw: Dict[str, Any]) -> bool:
    """True once we have something worth parsing, so the byte-scan can be skipped."""
    if _looks_like_api_graph(raw.get("prompt")):
        return True
    workflow = raw.get("workflow")
    return isinstance(workflow, dict) and isinstance(workflow.get("nodes"), list)


def read_raw_metadata(path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Extract every metadata blob we can find, plus basic container facts."""
    extension = os.path.splitext(path)[1].lower()
    if extension in VIDEO_EXTENSIONS and extension not in IMAGE_EXTENSIONS:
        raw, info = _read_video_metadata(path)
    else:
        try:
            raw, info = _read_image_metadata(path)
        except Exception:  # noqa: BLE001 - unreadable image, try the video path
            raw, info = _read_video_metadata(path)

    try:
        info["size_bytes"] = os.path.getsize(path)
    except OSError:
        pass
    return raw, info


# ---------------------------------------------------------------------------
# ComfyUI graph interpretation
# ---------------------------------------------------------------------------


def _is_link(value: Any) -> bool:
    """ComfyUI encodes a wired input as ``[source_node_id, output_slot]``."""
    return (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], (str, int))
        and not isinstance(value[0], bool)
        and isinstance(value[1], int)
        and not isinstance(value[1], bool)
    )


def _node(prompt: Dict[str, Any], node_id: Any) -> Optional[Dict[str, Any]]:
    node = prompt.get(str(node_id))
    return node if isinstance(node, dict) else None


def _inputs(node: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    inputs = (node or {}).get("inputs")
    return inputs if isinstance(inputs, dict) else {}


def _resolve_scalar(prompt: Dict[str, Any], value: Any, depth: int = 0) -> Any:
    """Follow a wired input back to the primitive node that supplies its value."""
    if not _is_link(value) or depth > 6:
        return None if _is_link(value) else value

    inputs = _inputs(_node(prompt, value[0]))
    for key in _SCALAR_PASSTHROUGH_KEYS:
        if key in inputs and not _is_link(inputs[key]):
            return inputs[key]
    for nested in inputs.values():
        if _is_link(nested):
            resolved = _resolve_scalar(prompt, nested, depth + 1)
            if resolved is not None:
                return resolved
    return None


def _resolve_text(
    prompt: Dict[str, Any], value: Any, visited: Optional[set] = None, depth: int = 0
) -> Optional[str]:
    """
    Walk a conditioning link back to the text that produced it.

    Recursing through the whole upstream chain means combiners, guidance nodes
    and conditioning modifiers between the encoder and the sampler do not hide
    the prompt.
    """
    if isinstance(value, str):
        return value
    if not _is_link(value) or depth > 8:
        return None

    visited = visited if visited is not None else set()
    node_id = str(value[0])
    if node_id in visited:
        return None
    visited.add(node_id)

    inputs = _inputs(_node(prompt, node_id))
    for key in _TEXT_INPUT_KEYS:
        if key in inputs and isinstance(inputs[key], str) and inputs[key].strip():
            return inputs[key]
    for key in _TEXT_INPUT_KEYS:
        if _is_link(inputs.get(key)):
            found = _resolve_text(prompt, inputs[key], visited, depth + 1)
            if found:
                return found
    for nested in inputs.values():
        if _is_link(nested):
            found = _resolve_text(prompt, nested, visited, depth + 1)
            if found:
                return found
    return None


def _resolve_model(
    prompt: Dict[str, Any], value: Any, visited: Optional[set] = None, depth: int = 0
) -> Optional[str]:
    """Walk a model link back to the checkpoint/UNet file that feeds it."""
    if isinstance(value, str):
        return value
    if not _is_link(value) or depth > 8:
        return None

    visited = visited if visited is not None else set()
    node_id = str(value[0])
    if node_id in visited:
        return None
    visited.add(node_id)

    inputs = _inputs(_node(prompt, node_id))
    for key in _MODEL_INPUT_KEYS:
        if isinstance(inputs.get(key), str) and inputs[key].strip():
            return inputs[key]
    for nested in inputs.values():
        if _is_link(nested):
            found = _resolve_model(prompt, nested, visited, depth + 1)
            if found:
                return found
    return None


def _pick_sampler(prompt: Dict[str, Any]) -> Optional[str]:
    """
    Choose the node that best represents "the sampler" for this render.

    Scored rather than matched by class name so custom samplers and the
    Flux-style split (RandomNoise + BasicScheduler + SamplerCustomAdvanced)
    both land on something sensible.
    """
    best_id, best_score = None, 0
    for node_id, node in prompt.items():
        if not isinstance(node, dict):
            continue
        inputs = _inputs(node)
        class_type = str(node.get("class_type", ""))
        score = 0
        if "steps" in inputs:
            score += 3
        if "cfg" in inputs or "cfg_scale" in inputs:
            score += 2
        if "seed" in inputs or "noise_seed" in inputs:
            score += 2
        if "sampler_name" in inputs:
            score += 2
        # Consuming a latent is what separates the real sampler from the
        # selector/scheduler helpers that also carry "Sampler" in their name.
        if "latent_image" in inputs:
            score += 4
        if "guider" in inputs:
            score += 2
        for key in ("sampler", "sigmas", "noise"):
            if key in inputs:
                score += 1
        if "sampler" in class_type.lower():
            score += 3
        if score < 5:
            continue
        # Ties go to the earliest node id, so repeated runs report the same one.
        if score > best_score or (
            score == best_score and _node_sort_key(node_id) < _node_sort_key(best_id)
        ):
            best_id, best_score = node_id, score
    return best_id


def _node_sort_key(node_id: Any) -> Tuple[int, str]:
    try:
        return (0, f"{int(node_id):012d}")
    except (TypeError, ValueError):
        return (1, str(node_id))


def _collect_upstream(
    prompt: Dict[str, Any], node_id: str, max_depth: int = 4
) -> List[Dict[str, Any]]:
    """Breadth-first list of the nodes feeding ``node_id``, nearest first."""
    seen = {str(node_id)}
    frontier = [str(node_id)]
    collected: List[Dict[str, Any]] = []

    for _ in range(max_depth):
        next_frontier: List[str] = []
        for current in frontier:
            for value in _inputs(_node(prompt, current)).values():
                if not _is_link(value):
                    continue
                upstream_id = str(value[0])
                if upstream_id in seen:
                    continue
                seen.add(upstream_id)
                node = _node(prompt, upstream_id)
                if node is not None:
                    collected.append(node)
                    next_frontier.append(upstream_id)
        frontier = next_frontier
        if not frontier:
            break
    return collected


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def _coerce_float(value: Any) -> Optional[float]:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _blank_info() -> Dict[str, Any]:
    return {
        "source": "none",
        "positive": "",
        "negative": "",
        "seed": None,
        "steps": None,
        "cfg": None,
        "sampler": "",
        "scheduler": "",
        "denoise": None,
        "model": "",
        "width": None,
        "height": None,
        "batch_size": None,
        "loras": [],
        "node_count": 0,
        "node_types": [],
        "extras": {},
    }


def parse_api_prompt(prompt: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the interesting generation parameters from a ComfyUI API graph."""
    info = _blank_info()
    info["source"] = "ComfyUI prompt graph"
    info["node_count"] = len(prompt)
    info["node_types"] = sorted(
        {str(node.get("class_type", "?")) for node in prompt.values() if isinstance(node, dict)}
    )

    sampler_id = _pick_sampler(prompt)
    if sampler_id is not None:
        sampler_inputs = _inputs(_node(prompt, sampler_id))
        chain = [sampler_inputs] + [_inputs(node) for node in _collect_upstream(prompt, sampler_id)]

        def first(*keys: str) -> Any:
            """First non-link value for any of ``keys``, sampler node first."""
            for inputs in chain:
                for key in keys:
                    if key not in inputs:
                        continue
                    value = inputs[key]
                    resolved = _resolve_scalar(prompt, value) if _is_link(value) else value
                    if resolved is not None and resolved != "":
                        return resolved
            return None

        info["seed"] = _coerce_int(first("seed", "noise_seed"))
        info["steps"] = _coerce_int(first("steps"))
        info["cfg"] = _coerce_float(first("cfg", "cfg_scale", "guidance"))
        info["denoise"] = _coerce_float(first("denoise"))
        sampler_name = first("sampler_name")
        scheduler = first("scheduler")
        info["sampler"] = str(sampler_name) if isinstance(sampler_name, str) else ""
        info["scheduler"] = str(scheduler) if isinstance(scheduler, str) else ""

        info["positive"] = _resolve_text(prompt, sampler_inputs.get("positive")) or ""
        info["negative"] = _resolve_text(prompt, sampler_inputs.get("negative")) or ""
        if not info["positive"] and "guider" in sampler_inputs:
            guider = (
                _inputs(_node(prompt, sampler_inputs["guider"][0]))
                if _is_link(sampler_inputs["guider"])
                else {}
            )
            info["positive"] = (
                _resolve_text(prompt, guider.get("conditioning") or guider.get("positive")) or ""
            )
            info["negative"] = _resolve_text(prompt, guider.get("negative")) or ""

        info["model"] = _resolve_model(prompt, sampler_inputs.get("model")) or ""
        if not info["model"]:
            for inputs in chain:
                for key in _MODEL_INPUT_KEYS:
                    if isinstance(inputs.get(key), str):
                        info["model"] = inputs[key]
                        break
                if info["model"]:
                    break

        latent = sampler_inputs.get("latent_image")
        for inputs in ([_inputs(_node(prompt, latent[0]))] if _is_link(latent) else []) + chain:
            width, height = _coerce_int(inputs.get("width")), _coerce_int(inputs.get("height"))
            if width and height:
                info["width"], info["height"] = width, height
                info["batch_size"] = _coerce_int(inputs.get("batch_size"))
                break

    # Fall back to any latent-shaped node when the sampler chain was a dead end.
    if not info["width"]:
        for node in prompt.values():
            inputs = _inputs(node if isinstance(node, dict) else None)
            width, height = _coerce_int(inputs.get("width")), _coerce_int(inputs.get("height"))
            if width and height:
                info["width"], info["height"] = width, height
                break

    if not info["positive"]:
        texts = [
            inputs["text"]
            for node in prompt.values()
            for inputs in [_inputs(node if isinstance(node, dict) else None)]
            if isinstance(inputs.get("text"), str) and inputs["text"].strip()
        ]
        if texts:
            info["positive"] = max(texts, key=len)

    for node_id, node in sorted(prompt.items(), key=lambda item: _node_sort_key(item[0])):
        inputs = _inputs(node if isinstance(node, dict) else None)
        name = inputs.get("lora_name")
        if isinstance(name, str) and name:
            info["loras"].append(
                {
                    "name": name,
                    "strength_model": _coerce_float(
                        inputs.get("strength_model", inputs.get("strength"))
                    ),
                    "strength_clip": _coerce_float(inputs.get("strength_clip")),
                }
            )

    extras = {}
    for key in ("vae_name", "clip_name", "clip_name1", "clip_name2", "style_model_name"):
        for node in prompt.values():
            value = _inputs(node if isinstance(node, dict) else None).get(key)
            if isinstance(value, str) and value:
                extras[key] = value
                break
    info["extras"] = extras
    return info


def parse_ui_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Best-effort read of a UI-format workflow (the ``workflow`` metadata key).

    The UI format only stores widget values positionally, so values are matched
    by type and plausibility rather than by index. Used only when no API prompt
    graph is embedded.
    """
    info = _blank_info()
    info["source"] = "ComfyUI workflow (UI format)"
    nodes = workflow.get("nodes") or []
    info["node_count"] = len(nodes)
    info["node_types"] = sorted(
        {str(node.get("type", "?")) for node in nodes if isinstance(node, dict)}
    )

    prompts: List[str] = []
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_type = str(node.get("type", ""))
        widgets = node.get("widgets_values")
        if isinstance(widgets, dict):
            widgets = list(widgets.values())
        if not isinstance(widgets, list):
            continue

        if "CLIPTextEncode" in node_type:
            for value in widgets:
                if isinstance(value, str) and value.strip():
                    prompts.append(value)

        if "Sampler" in node_type and info["steps"] is None:
            # KSampler widgets are ordered seed, control, steps, cfg, sampler,
            # scheduler, denoise. Drop the flag widgets, then read the numbers
            # and the names positionally - matching on value types alone is
            # unreliable because JSON turns a cfg of 8.0 into an integer.
            numbers = [
                value
                for value in widgets
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            ]
            names = [
                value
                for value in widgets
                if isinstance(value, str)
                and value.strip()
                and value.lower() not in _WIDGET_FLAG_VALUES
            ]
            for index, key in enumerate(("seed", "steps", "cfg")):
                if index < len(numbers):
                    info[key] = (
                        _coerce_int(numbers[index])
                        if key != "cfg"
                        else _coerce_float(numbers[index])
                    )
            # Only KSampler's own layout ends on denoise; the Advanced variant
            # trails step ranges instead, so require the simple shape.
            if len(numbers) == 4 and numbers[3] <= 1:
                info["denoise"] = _coerce_float(numbers[3])
            if names:
                info["sampler"] = names[0]
            if len(names) > 1:
                info["scheduler"] = names[1]

        if info["width"] is None and "Latent" in node_type:
            integers = [
                value for value in widgets if isinstance(value, int) and not isinstance(value, bool)
            ]
            if len(integers) >= 2:
                info["width"], info["height"] = integers[0], integers[1]
                if len(integers) >= 3:
                    info["batch_size"] = integers[2]

        if "Lora" in node_type:
            names = [value for value in widgets if isinstance(value, str) and value.strip()]
            strengths = [
                value
                for value in widgets
                if isinstance(value, (int, float)) and not isinstance(value, bool)
            ]
            if names:
                info["loras"].append(
                    {
                        "name": names[0],
                        "strength_model": _coerce_float(strengths[0]) if strengths else None,
                        "strength_clip": (
                            _coerce_float(strengths[1]) if len(strengths) > 1 else None
                        ),
                    }
                )

        if not info["model"] and ("Checkpoint" in node_type or "UNETLoader" in node_type):
            for value in widgets:
                if isinstance(value, str) and value.strip():
                    info["model"] = value
                    break

    if prompts:
        ordered = sorted(prompts, key=len, reverse=True)
        info["positive"] = ordered[0]
        if len(ordered) > 1:
            info["negative"] = ordered[1]
    return info


_A1111_PAIR_RE = re.compile(r"([A-Za-z][A-Za-z0-9 _/\-]*?):\s*([^,]+)(?:,|$)")


def parse_a1111_parameters(text: str) -> Dict[str, Any]:
    """Parse an A1111/Forge style ``parameters`` string."""
    info = _blank_info()
    info["source"] = "A1111 parameters string"

    lines = text.splitlines()
    settings_index = len(lines)
    for index, line in enumerate(lines):
        if re.match(r"^\s*(Steps|Sampler|CFG scale|Seed)\s*:", line):
            settings_index = index
            break

    body = "\n".join(lines[:settings_index])
    settings = " ".join(lines[settings_index:])

    negative_marker = re.search(r"^\s*Negative prompt:\s*", body, re.MULTILINE)
    if negative_marker:
        info["positive"] = body[: negative_marker.start()].strip()
        info["negative"] = body[negative_marker.end() :].strip()
    else:
        info["positive"] = body.strip()

    pairs = {key.strip().lower(): value.strip() for key, value in _A1111_PAIR_RE.findall(settings)}
    info["seed"] = _coerce_int(pairs.get("seed"))
    info["steps"] = _coerce_int(pairs.get("steps"))
    info["cfg"] = _coerce_float(pairs.get("cfg scale"))
    info["denoise"] = _coerce_float(pairs.get("denoising strength"))
    info["sampler"] = pairs.get("sampler", "")
    info["scheduler"] = pairs.get("schedule type", pairs.get("scheduler", ""))
    info["model"] = pairs.get("model", "")

    size = pairs.get("size", "")
    size_match = re.match(r"\s*(\d+)\s*[x×]\s*(\d+)", size)
    if size_match:
        info["width"], info["height"] = int(size_match.group(1)), int(size_match.group(2))

    info["extras"] = {
        key: value
        for key, value in pairs.items()
        if key
        not in {
            "seed",
            "steps",
            "cfg scale",
            "sampler",
            "scheduler",
            "schedule type",
            "model",
            "size",
            "denoising strength",
        }
    }
    return info


def interpret_metadata(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Turn the raw metadata blobs into one structured generation summary."""
    prompt_graph = raw.get("prompt")
    if _looks_like_api_graph(prompt_graph):
        return parse_api_prompt(prompt_graph)

    for value in raw.values():
        if _looks_like_api_graph(value):
            return parse_api_prompt(value)

    workflow = raw.get("workflow")
    if isinstance(workflow, dict) and isinstance(workflow.get("nodes"), list):
        return parse_ui_workflow(workflow)

    for key in ("parameters", "Parameters", "UserComment", "Description", "comment"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return parse_a1111_parameters(value)

    return _blank_info()


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

_WIDTH = 62
_TITLE = "🧵 Pipemind Media Metadata"
_HEADER = f"{_TITLE}\n{'=' * _WIDTH}"


def _rule(title: str = "") -> str:
    if not title:
        return "─" * _WIDTH
    return f"── {title} " + "─" * max(3, _WIDTH - len(title) - 4)


def _row(label: str, value: Any) -> str:
    return f"{label:<12}: {value}"


def _human_size(num_bytes: Optional[int]) -> str:
    if not num_bytes:
        return "?"
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _format_number(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        # Keep floats looking like floats: 1.0 rather than a bare 1.
        return f"{value:.1f}" if value.is_integer() else f"{value:g}"
    return str(value)


def format_report(
    display_path: str,
    container: Dict[str, Any],
    info: Dict[str, Any],
    raw: Dict[str, Any],
    detail: str,
) -> str:
    """Render the human-readable report shown on the node."""
    lines = [_TITLE, "=" * _WIDTH]

    descriptor = str(container.get("format", "unknown"))
    if container.get("width") and container.get("height"):
        descriptor += f" · {container['width']} × {container['height']}"
    if container.get("frames"):
        descriptor += f" · {container['frames']} frames"
    if container.get("duration"):
        descriptor += f" · {container['duration']:.2f}s"
    descriptor += f" · {_human_size(container.get('size_bytes'))}"

    lines.append(_row("File", display_path))
    lines.append(_row("Media", descriptor))

    source = info.get("source", "none")
    if source == "none":
        lines.append(_row("Metadata", "none found"))
        keys = sorted(raw)
        if keys:
            lines.append(_row("Raw keys", ", ".join(keys)))
        lines.append("")
        lines.append(
            "No generation metadata is embedded in this file. Re-saved, "
            "converted or screenshotted images usually lose it."
        )
        return "\n".join(lines)

    detail_suffix = f" ({info['node_count']} nodes)" if info.get("node_count") else ""
    lines.append(_row("Metadata", f"{source}{detail_suffix}"))
    if container.get("reader"):
        lines.append(_row("Read via", container["reader"]))

    lines += ["", _rule("Generation")]
    lines.append(_row("Model", info.get("model") or "—"))
    lines.append(_row("Seed", _format_number(info.get("seed"))))
    lines.append(_row("Steps", _format_number(info.get("steps"))))
    lines.append(_row("CFG", _format_number(info.get("cfg"))))
    sampler = " / ".join(part for part in (info.get("sampler"), info.get("scheduler")) if part)
    lines.append(_row("Sampler", sampler or "—"))
    if info.get("denoise") is not None:
        lines.append(_row("Denoise", _format_number(info["denoise"])))
    if info.get("width") and info.get("height"):
        size_line = f"{info['width']} × {info['height']}"
        if info.get("batch_size"):
            size_line += f" (batch {info['batch_size']})"
        lines.append(_row("Size", size_line))

    for key, value in (info.get("extras") or {}).items():
        lines.append(_row(key.replace("_", " ").title()[:12], value))

    if info.get("loras"):
        lines += ["", _rule("LoRAs")]
        for index, lora in enumerate(info["loras"], start=1):
            strengths = " / ".join(
                _format_number(lora[key])
                for key in ("strength_model", "strength_clip")
                if lora.get(key) is not None
            )
            lines.append(f"{index}. {lora['name']}" + (f"   [{strengths}]" if strengths else ""))

    lines += ["", _rule("Positive prompt"), info.get("positive") or "—"]
    lines += ["", _rule("Negative prompt"), info.get("negative") or "—"]

    if detail == "full" and info.get("node_types"):
        lines += ["", _rule(f"Node types ({len(info['node_types'])})")]
        lines += [f"• {node_type}" for node_type in info["node_types"]]
        if raw:
            lines += ["", _rule("Metadata keys"), ", ".join(sorted(raw))]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# The node
# ---------------------------------------------------------------------------


class PipemindMediaMetadata:
    """Read and display the generation metadata embedded in an image or video."""

    @classmethod
    def INPUT_TYPES(cls):
        files = list_media_files() or [NO_FILES]
        return {
            "required": {
                "file": (
                    files,
                    {"tooltip": "Media from ComfyUI's input/ and output/ folders, newest first."},
                ),
                "detail": (
                    ["summary", "full", "raw json"],
                    {
                        "tooltip": "summary: key settings. full: adds the node "
                        "inventory. raw json: the embedded metadata verbatim."
                    },
                ),
            },
            "optional": {
                "path_override": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": False,
                        "tooltip": "Absolute or relative path to read instead "
                        "of the dropdown selection.",
                    },
                ),
            },
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "INT",
        "INT",
        "FLOAT",
        "STRING",
        "STRING",
        "STRING",
        "INT",
        "INT",
        "STRING",
        "BOOLEAN",
    )
    RETURN_NAMES = (
        "report",
        "positive",
        "negative",
        "seed",
        "steps",
        "cfg",
        "sampler",
        "scheduler",
        "model",
        "width",
        "height",
        "raw_json",
        "has_metadata",
    )
    FUNCTION = "read"
    OUTPUT_NODE = True
    CATEGORY = "Pipemind"
    DESCRIPTION = (
        "Reads the metadata ComfyUI embeds in a saved image or video and shows "
        "seed, steps, cfg, sampler, model and prompts as a formatted report."
    )

    def read(self, file: str, detail: str = "summary", path_override: str = ""):
        path = resolve_media_path(file, path_override)
        if path is None:
            target = (path_override or file or "").strip() or "(nothing selected)"
            report = f"{_HEADER}\nFile not found: {target}"
            return self._package(report, _blank_info(), "{}", False)

        display_path = path_override.strip() or file
        try:
            raw, container = read_raw_metadata(path)
        except Exception as error:  # noqa: BLE001 - a bad file must not break the graph
            report = (
                f"{_HEADER}\n{_row('File', display_path)}" f"\n\nCould not read this file: {error}"
            )
            return self._package(report, _blank_info(), "{}", False)

        info = interpret_metadata(raw)
        has_metadata = info["source"] != "none"

        try:
            raw_json = json.dumps(raw, indent=2, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            raw_json = str(raw)

        if detail == "raw json":
            header = f"{_HEADER}\n{_row('File', display_path)}\n\n"
            report = header + (raw_json if raw else "No embedded metadata found.")
        else:
            report = format_report(display_path, container, info, raw, detail)

        return self._package(report, info, raw_json, has_metadata)

    @staticmethod
    def _package(report: str, info: Dict[str, Any], raw_json: str, has_metadata: bool):
        result = (
            report,
            info.get("positive") or "",
            info.get("negative") or "",
            int(info.get("seed") or 0),
            int(info.get("steps") or 0),
            float(info.get("cfg") or 0.0),
            info.get("sampler") or "",
            info.get("scheduler") or "",
            info.get("model") or "",
            int(info.get("width") or 0),
            int(info.get("height") or 0),
            raw_json,
            has_metadata,
        )
        return {"ui": {"text": (report,)}, "result": result}

    @classmethod
    def IS_CHANGED(cls, file: str, detail: str = "summary", path_override: str = ""):
        """Re-run when the selected file, its contents, or the detail level change."""
        path = resolve_media_path(file, path_override)
        if path is None:
            return f"missing:{path_override or file}:{detail}"
        try:
            stat = os.stat(path)
        except OSError:
            return f"missing:{path}:{detail}"
        return f"{path}:{stat.st_mtime_ns}:{stat.st_size}:{detail}"
