from __future__ import annotations

import html
import json
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from typing import Literal

import numpy as np
import resvg_py
from PIL import Image, ImageDraw, ImageFont

from .combinations import (
    CONTENT_STATES,
    MATERIAL_STATES,
    OUTLINE_STATES,
    POLARITY_STATES,
)
from .config import Config
from .source_geometry import SourceBase, source_bases

ProofDimension = Literal["content", "outline", "shading", "material", "polarity"]
ProofState = str

PROOF_DIMENSIONS: tuple[ProofDimension, ...] = (
    "content",
    "outline",
    "shading",
    "material",
    "polarity",
)
PROOF_STATES: dict[ProofDimension, tuple[ProofState, ...]] = {
    "content": CONTENT_STATES,
    "outline": OUTLINE_STATES,
    "shading": ("ambiguous", "paper-vase"),
    "material": MATERIAL_STATES,
    "polarity": POLARITY_STATES,
}

_DARK = "#181818"
_LIGHT = "#e8e8e8"
_MID = "#858585"
_POLARITY_COLORS = {"black": _DARK, "gray": _MID, "white": _LIGHT}


def _points_path(points: list[tuple[float, float]]) -> str:
    if not points:
        raise ValueError("cannot build an empty SVG path")
    commands = [f"M {points[0][0]:.6f} {points[0][1]:.6f}"]
    commands.extend(f"L {x:.6f} {y:.6f}" for x, y in points[1:])
    commands.append("Z")
    return " ".join(commands)


def _open_path(points: list[tuple[float, float]]) -> str:
    if not points:
        raise ValueError("cannot build an empty SVG path")
    commands = [f"M {points[0][0]:.6f} {points[0][1]:.6f}"]
    commands.extend(f"L {x:.6f} {y:.6f}" for x, y in points[1:])
    return " ".join(commands)


def _center_path(base: SourceBase) -> str:
    left = [(0.5 - float(width), float(y)) for y, width in zip(base.y, base.widths, strict=True)]
    right = [
        (0.5 + float(width), float(y))
        for y, width in zip(base.y[::-1], base.widths[::-1], strict=True)
    ]
    return _points_path(left + right)


def _face_paths(
    base: SourceBase, top_y_override: float | None = None
) -> tuple[str, str, str, str]:
    selected = [(float(y), float(width)) for y, width in zip(base.y, base.widths, strict=True)]
    if len(selected) < 8:
        raise ValueError(f"too few face-profile points for {base.base_id}")
    bottom_y = selected[-1][0]
    if top_y_override is not None:
        if not 0.0 <= top_y_override < bottom_y:
            raise ValueError(
                f"invalid face-outline top y for {base.base_id}: {top_y_override}"
            )
        original_top_y = selected[0][0]
        if top_y_override < original_top_y:
            selected.insert(0, (top_y_override, selected[0][1]))
        elif top_y_override > original_top_y:
            top_width = float(np.interp(top_y_override, base.y, base.widths))
            selected = [(top_y_override, top_width)] + [
                (y, width) for y, width in selected if y > top_y_override
            ]
    left_profile = [(0.5 - width, y) for y, width in selected]
    right_profile = [(0.5 + width, y) for y, width in selected]
    top_y = selected[0][0]
    # Use the complete shared contour. The side regions continue out of frame, so
    # the only added outline evidence is a top and bottom closure segment. This
    # avoids both a synthetic back-of-head arc and a moving local reveal window.
    left_closure = (
        f"M {left_profile[0][0]:.6f} {top_y:.6f} L 0.000000 {top_y:.6f} "
        f"M 0.000000 {bottom_y:.6f} "
        f"L {left_profile[-1][0]:.6f} {bottom_y:.6f}"
    )
    right_closure = (
        f"M {right_profile[0][0]:.6f} {top_y:.6f} L 1.000000 {top_y:.6f} "
        f"M 1.000000 {bottom_y:.6f} "
        f"L {right_profile[-1][0]:.6f} {bottom_y:.6f}"
    )
    return (
        _points_path(left_profile + [(0.0, bottom_y), (0.0, top_y)]),
        _points_path(right_profile + [(1.0, bottom_y), (1.0, top_y)]),
        left_closure,
        right_closure,
    )


def _cue_layer(base: SourceBase, cue_axis: str, signed_strength: int) -> str:
    center_path = _center_path(base)
    left_face, right_face, left_closure, right_closure = _face_paths(base)
    face_content = (
        '<g id="face-content"><rect width="1" height="1" fill="#e8e8e8"/>'
        f'<path d="{left_face}" fill="#181818"/>'
        f'<path d="{right_face}" fill="#181818"/></g>'
    )
    vase_content = (
        '<g id="vase-content"><rect width="1" height="1" fill="#767676"/>'
        f'<path d="{center_path}" fill="#dedede"/></g>'
    )
    face_outline = (
        '<g id="face-outline" fill="none" stroke="#d0d0d0" '
        'stroke-width=".006" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{left_closure}"/><path d="{right_closure}"/></g>'
    )
    top_y = float(base.y[0])
    bottom_y = float(base.y[-1])
    top_width = float(base.widths[0])
    bottom_width = float(base.widths[-1])
    vase_outline = (
        '<g id="vase-outline" fill="none" stroke="#4a4a4a" '
        'stroke-width=".008" stroke-linecap="round">'
        f'<path d="M {0.5 - top_width:.6f} {top_y:.6f} '
        f'L {0.5 + top_width:.6f} {top_y:.6f}"/>'
        f'<path d="M {0.5 - bottom_width:.6f} {bottom_y:.6f} '
        f'L {0.5 + bottom_width:.6f} {bottom_y:.6f}"/></g>'
    )
    face_shading = (
        '<g id="face-shading">'
        '<rect x="0" y="0" width=".5" height="1" fill="url(#face-shade-left)"/>'
        '<rect x=".5" y="0" width=".5" height="1" fill="url(#face-shade-right)"/>'
        f'<path d="{center_path}" fill="#e8e8e8"/></g>'
    )
    vase_shading = f'<g id="vase-shading"><path d="{center_path}" fill="url(#vase-shade)"/></g>'
    face_combined = (
        '<g id="face-combined"><rect width="1" height="1" fill="#e8e8e8"/>'
        f'<path d="{left_face}" fill="#181818"/>'
        f'<path d="{right_face}" fill="#181818"/>'
        '<g fill="none" stroke="#202020" stroke-width=".004">'
        f'<path d="{left_closure}"/><path d="{right_closure}"/></g></g>'
    )
    vase_combined = (
        '<g id="vase-combined"><rect width="1" height="1" fill="#767676"/>'
        f'<path d="{center_path}" fill="url(#vase-shade)" stroke="#4a4a4a" '
        'stroke-width=".006" stroke-linejoin="round"/>'
        f"{vase_outline}</g>"
    )
    negative = {
        "content": face_content,
        "outline": face_outline,
        "shading": face_shading,
        "combined": face_combined,
    }
    positive = {
        "content": vase_content,
        "outline": vase_outline,
        "shading": vase_shading,
        "combined": vase_combined,
    }
    try:
        return negative[cue_axis] if signed_strength < 0 else positive[cue_axis]
    except KeyError as exc:
        raise ValueError(f"unknown cue axis: {cue_axis}") from exc


def render_cue_svg(config: Config, base: SourceBase, cue_axis: str, signed_strength: int) -> str:
    if signed_strength < -3 or signed_strength > 3:
        raise ValueError("signed strength must be in [-3, 3]")
    if signed_strength == 0:
        cue_axis = "baseline"
    elif cue_axis not in ("content", "outline", "shading", "combined"):
        raise ValueError(f"unknown cue axis: {cue_axis}")
    center_path = _center_path(base)
    alpha = abs(signed_strength) / 3.0
    layer = "" if cue_axis == "baseline" else _cue_layer(base, cue_axis, signed_strength)
    polarity_filter = ' filter="url(#invert)"' if base.polarity == "light-outer" else ""
    metadata = html.escape(
        json.dumps(
            {
                "base_id": base.base_id,
                "source_id": base.source.source_id,
                "source_sha256": base.source.sha256,
                "source_license": base.source.license_id,
                "cue_axis": cue_axis,
                "signed_strength": signed_strength,
                "fixation_baked_in": False,
            },
            sort_keys=True,
        )
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" '
        f'width="{config.canvas_size}" height="{config.canvas_size}">'
        f"<metadata>{metadata}</metadata>"
        '<defs><linearGradient id="vase-shade" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#f5f5f5"/>'
        '<stop offset="0.45" stop-color="#dddddd"/>'
        '<stop offset="1" stop-color="#b7b7b7"/>'
        "</linearGradient>"
        '<radialGradient id="face-shade-left" cx="35%" cy="48%" r="75%">'
        '<stop offset="0" stop-color="#777777"/><stop offset="1" stop-color="#181818"/>'
        "</radialGradient>"
        '<radialGradient id="face-shade-right" cx="65%" cy="48%" r="75%">'
        '<stop offset="0" stop-color="#777777"/><stop offset="1" stop-color="#181818"/>'
        "</radialGradient>"
        '<filter id="invert" color-interpolation-filters="sRGB">'
        '<feComponentTransfer><feFuncR type="linear" slope="-1" intercept="1"/>'
        '<feFuncG type="linear" slope="-1" intercept="1"/>'
        '<feFuncB type="linear" slope="-1" intercept="1"/></feComponentTransfer>'
        "</filter></defs>"
        f'<g id="stimulus"{polarity_filter}>'
        '<rect width="1" height="1" fill="#181818"/>'
        f'<path d="{center_path}" fill="#e8e8e8"/>'
        + (f'<g opacity="{alpha:.6f}">{layer}</g>' if layer else "")
        + "</g></svg>\n"
    )


def render_endpoint_svg(config: Config, base: SourceBase, signed_strength: int) -> str:
    return render_cue_svg(config, base, "combined", signed_strength)


def _canonical_proof_base(project_root: str | Path) -> SourceBase:
    expected = "wm-cc0-classic-dark-outer"
    try:
        return next(base for base in source_bases(project_root) if base.base_id == expected)
    except StopIteration as exc:  # pragma: no cover - immutable registry invariant
        raise ValueError(f"missing canonical proof base: {expected}") from exc


def _moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window % 2 == 0:
        window += 1
    radius = window // 2
    padded = np.pad(values, (radius, radius), mode="edge")
    return np.convolve(padded, np.ones(window) / window, mode="valid")


def _proof_defs(
    dimension: ProofDimension,
    center_path: str,
) -> str:
    definitions = [f'<clipPath id="center-clip"><path d="{center_path}"/></clipPath>']
    if dimension == "content":
        definitions.append(
            '<pattern id="horizontal-stripes" width="1" height=".050" '
            'patternUnits="userSpaceOnUse">'
            f'<rect width="1" height=".050" fill="{_DARK}"/>'
            '<rect width="1" height=".018" fill="#666666"/></pattern>'
        )
    return "<defs>" + "".join(definitions) + "</defs>"


def _lambertian_gray(u: float, vertical_slope: float, mirror: float = 1.0) -> str:
    depth = float(np.sqrt(max(0.0, 1.0 - u * u)))
    normal = np.array([mirror * u, -vertical_slope * depth, depth], dtype=np.float64)
    normal /= max(float(np.linalg.norm(normal)), 1e-9)
    light = np.array([-0.46, -0.32, 0.83], dtype=np.float64)
    light /= float(np.linalg.norm(light))
    diffuse = max(0.0, float(np.dot(normal, light)))
    value = int(round(48 + 196 * (0.18 + 0.82 * diffuse)))
    value = max(48, min(244, value))
    return f"#{value:02x}{value:02x}{value:02x}"


def _material_vase_mesh(base: SourceBase) -> str:
    y_indices = np.unique(np.linspace(0, len(base.y) - 1, 129).astype(int))
    u_edges = np.linspace(-1.0, 1.0, 37)
    slope_widths = _moving_average(base.widths, max(15, len(base.widths) // 18))
    patches: list[str] = []
    for row_start, row_stop in zip(y_indices[:-1], y_indices[1:], strict=True):
        y0 = float(base.y[row_start])
        y1 = float(base.y[row_stop])
        width0 = float(base.widths[row_start])
        width1 = float(base.widths[row_stop])
        slope = (float(slope_widths[row_stop]) - float(slope_widths[row_start])) / max(
            y1 - y0, 1e-9
        )
        for u0, u1 in zip(u_edges[:-1], u_edges[1:], strict=True):
            midpoint = float((u0 + u1) / 2.0)
            fill = _lambertian_gray(midpoint, slope)
            path = (
                f"M {0.5 + u0 * width0:.6f} {y0:.6f} "
                f"L {0.5 + u1 * width0:.6f} {y0:.6f} "
                f"L {0.5 + u1 * width1:.6f} {y1:.6f} "
                f"L {0.5 + u0 * width1:.6f} {y1:.6f} Z"
            )
            patches.append(f'<path d="{path}" fill="{fill}"/>')
    return '<g id="material-vase-diffuse">' + "".join(patches) + "</g>"


def _outline_face_layer(base: SourceBase) -> str:
    top_y = float(base.y[0])
    bottom_y = float(base.y[-1])
    left_top = 0.5 - float(base.widths[0])
    right_top = 0.5 + float(base.widths[0])
    left_bottom = 0.5 - float(base.widths[-1])
    right_bottom = 0.5 + float(base.widths[-1])
    return (
        '<g id="outline-face-openings">'
        f'<path d="M {left_top:.6f} {top_y:.6f} L {left_top:.6f} 0 '
        f'L {right_top:.6f} 0 L {right_top:.6f} {top_y:.6f} Z" fill="{_LIGHT}"/>'
        f'<path d="M {left_bottom:.6f} {bottom_y:.6f} '
        f"L {left_bottom:.6f} 1 L {right_bottom:.6f} 1 "
        f'L {right_bottom:.6f} {bottom_y:.6f} Z" fill="{_LIGHT}"/>'
        "</g>"
    )


def _proof_layer(
    dimension: ProofDimension,
    state: ProofState,
    base: SourceBase,
    center_path: str,
    left_face: str,
    right_face: str,
) -> str:
    if state == "ambiguous":
        return ""
    if dimension == "content":
        if state == "face":
            return (
                '<g id="content-broken-profile-homogeneity">'
                f'<path d="{left_face}" fill="{_DARK}"/>'
                f'<path d="{right_face}" fill="#5b5b5b"/>'
                f'<path d="{center_path}" fill="{_LIGHT}"/></g>'
            )
        return (
            '<g id="content-profile-horizontal-stripes">'
            f'<path d="{left_face}" fill="url(#horizontal-stripes)"/>'
            f'<path d="{right_face}" fill="url(#horizontal-stripes)"/>'
            f'<path d="{center_path}" fill="{_LIGHT}"/></g>'
        )
    if dimension == "outline":
        return (
            '<g id="outline-face-paper-endpoint">'
            f'<rect width="1" height="1" fill="{_LIGHT}"/>'
            f'<path d="{left_face}" fill="{_DARK}"/>'
            f'<path d="{right_face}" fill="{_DARK}"/></g>'
        )
    if dimension == "shading":
        # The paper endpoint is a hard cast shadow, not a uniform inset contour.
        # A translated black copy of the vase is placed behind the white vase on gray.
        # The offset is measured from the rasterized Hardstone/Wang reference panel.
        return (
            '<g id="shading-paper-vase">'
            '<rect width="1" height="1" fill="#858585"/>'
            f'<path id="hard-cast-shadow" d="{center_path}" fill="#222222" '
            'transform="translate(.027 .054)"/>'
            f'<path id="unshifted-white-vase" d="{center_path}" fill="{_LIGHT}"/>'
            "</g>"
        )
    if dimension == "material":
        return _material_vase_mesh(base)
    if dimension == "polarity":
        outer_part, center_part = state.split("_", maxsplit=1)
        outer_name = outer_part.removeprefix("outer-")
        center_name = center_part.removeprefix("center-")
        outer_fill = _POLARITY_COLORS[outer_name]
        center_fill = _POLARITY_COLORS[center_name]
        return (
            f'<g id="polarity-{outer_name}-{center_name}">'
            f'<rect width="1" height="1" fill="{outer_fill}"/>'
            f'<path d="{center_path}" fill="{center_fill}"/></g>'
        )
    raise AssertionError(dimension)  # pragma: no cover


def render_dimension_proof_svg(
    config: Config,
    base: SourceBase,
    dimension: ProofDimension,
    state: ProofState,
) -> str:
    if dimension not in PROOF_DIMENSIONS:
        raise ValueError(f"unknown proof dimension: {dimension}")
    if state not in PROOF_STATES[dimension]:
        raise ValueError(f"unknown proof state: {state}")
    center_path = _center_path(base)
    outline_top_y = (
        base.source.face_outline_top_y if dimension == "outline" and state == "face" else None
    )
    left_face, right_face, _left_closure, _right_closure = _face_paths(
        base, top_y_override=outline_top_y
    )
    layer = _proof_layer(dimension, state, base, center_path, left_face, right_face)
    metadata = html.escape(
        json.dumps(
            {
                "active_dimension": dimension,
                "base_id": base.base_id,
                "fixation_baked_in": False,
                "other_dimensions": "neutral",
                "source_id": base.source.source_id,
                "source_sha256": base.source.sha256,
                "state": state,
            },
            sort_keys=True,
        )
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" '
        f'width="{config.canvas_size}" height="{config.canvas_size}">'
        f"<metadata>{metadata}</metadata>"
        f"{_proof_defs(dimension, center_path)}"
        f'<g id="baseline"><rect width="1" height="1" fill="{_DARK}"/>'
        f'<path d="{center_path}" fill="{_LIGHT}"/></g>'
        f'<g id="proof-{dimension}-{state}">{layer}</g></svg>\n'
    )


def rasterize_svg(svg: str) -> Image.Image:
    png = resvg_py.svg_to_bytes(svg_string=svg)
    with Image.open(BytesIO(png)) as image:
        rgba = image.convert("RGBA")
    flattened = Image.new("RGBA", rgba.size, "white")
    flattened.alpha_composite(rgba)
    return flattened.convert("L")


def _display_proof_state(state: ProofState) -> str:
    if state.startswith("outer-"):
        outer_part, center_part = state.split("_", maxsplit=1)
        outer = outer_part.removeprefix("outer-")
        center = center_part.removeprefix("center-")
        return f"outer {outer} / center {center}"
    return state.replace("-", " ")


def _stack_strips(strips: list[Image.Image], gap: int) -> Image.Image:
    width = max(strip.width for strip in strips)
    height = sum(strip.height for strip in strips) + gap * (len(strips) - 1)
    stacked = Image.new("L", (width, height), 150)
    y = 0
    for strip in strips:
        stacked.paste(strip, (0, y))
        y += strip.height + gap
    return stacked


def write_dimension_proof(config: Config, output: str | Path) -> dict[str, object]:
    output_path = Path(output).expanduser().resolve()
    images_path = output_path / "images"
    montages_path = output_path / "montages"
    images_path.mkdir(parents=True, exist_ok=True)
    montages_path.mkdir(parents=True, exist_ok=True)
    base = _canonical_proof_base(config.path.parent.parent)
    rows = [(dimension, base, PROOF_STATES[dimension], dimension) for dimension in PROOF_DIMENSIONS]

    cell_size = min(300, config.canvas_size)
    label_height = 48
    gap = 12
    font = ImageFont.load_default(size=15)
    entries: list[dict[str, object]] = []
    strips_by_dimension: dict[str, list[Image.Image]] = {
        dimension: [] for dimension in PROOF_DIMENSIONS
    }
    all_strips: list[Image.Image] = []
    for dimension, row_base, states, row_label in rows:
        strip = Image.new(
            "L",
            (
                len(states) * cell_size + (len(states) - 1) * gap,
                cell_size + label_height,
            ),
            150,
        )
        strip_draw = ImageDraw.Draw(strip)
        for column_index, state in enumerate(states):
            svg = render_dimension_proof_svg(config, row_base, dimension, state)
            stem = f"{dimension}-{state}"
            svg_path = images_path / f"{stem}.svg"
            png_path = images_path / f"{stem}.png"
            svg_path.write_text(svg, encoding="utf-8")
            image = rasterize_svg(svg)
            image.save(png_path, format="PNG", compress_level=9)
            entries.append(
                {
                    "active_dimension": dimension,
                    "base_id": row_base.base_id,
                    "other_dimensions": "baseline",
                    "png": str(png_path),
                    "sha256": sha256(png_path.read_bytes()).hexdigest(),
                    "state": state,
                    "svg": str(svg_path),
                }
            )
            preview = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
            x = column_index * (cell_size + gap)
            strip.paste(preview, (x, label_height))
            label = f"{row_label} / {_display_proof_state(state)}"
            strip_draw.text((x + 7, 14), label, fill=245, font=font)
        strips_by_dimension[dimension].append(strip)
        all_strips.append(strip)

    montage_paths: dict[str, str] = {}
    for dimension in PROOF_DIMENSIONS:
        montage = _stack_strips(strips_by_dimension[dimension], gap)
        montage_path = montages_path / f"{dimension}.png"
        montage.save(montage_path, format="PNG", compress_level=9)
        montage_paths[dimension] = str(montage_path)
    overview = _stack_strips(all_strips, gap)
    overview_path = output_path / "dimension-proof-overview.png"
    overview.save(overview_path, format="PNG", compress_level=9)
    manifest_path = output_path / "proof-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "dimensions": list(PROOF_DIMENSIONS),
                "entries": entries,
                "base_ids": [base.base_id],
                "states": PROOF_STATES,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "base_count": 1,
        "dimension_count": len(PROOF_DIMENSIONS),
        "image_count": len(entries),
        "manifest": str(manifest_path),
        "montages": montage_paths,
        "overview": str(overview_path),
    }


def write_face_outline_proof(
    config: Config,
    output: str | Path,
    source_ids: list[str] | tuple[str, ...] | None = None,
) -> dict[str, object]:
    """Render the paper-style face-outline endpoint for compatible source contours."""
    output_path = Path(output).expanduser().resolve()
    images_path = output_path / "images"
    images_path.mkdir(parents=True, exist_ok=True)
    for old_path in images_path.glob("*__outline-face.*"):
        old_path.unlink()
    compatible_bases = {
        base.source.source_id: base
        for base in source_bases(config.path.parent.parent)
        if base.polarity == "dark-outer" and base.source.face_outline_allowed
    }
    if source_ids is None:
        bases = [base for base in compatible_bases.values() if base.source.bank_enabled]
    else:
        requested = list(dict.fromkeys(source_ids))
        unavailable = [source_id for source_id in requested if source_id not in compatible_bases]
        if unavailable:
            raise ValueError(
                "source does not support face-outline proof: " + ", ".join(unavailable)
            )
        bases = [compatible_bases[source_id] for source_id in requested]

    cell_size = min(360, config.canvas_size)
    label_height = 42
    gap = 12
    columns = 2
    rows = (len(bases) + columns - 1) // columns
    font = ImageFont.load_default(size=15)
    montage = Image.new(
        "L",
        (
            columns * cell_size + (columns - 1) * gap,
            rows * (cell_size + label_height) + (rows - 1) * gap,
        ),
        150,
    )
    draw = ImageDraw.Draw(montage)
    entries: list[dict[str, object]] = []
    for index, base in enumerate(bases):
        svg = render_dimension_proof_svg(config, base, "outline", "face")
        stem = f"{base.source.source_id}__outline-face"
        svg_path = images_path / f"{stem}.svg"
        png_path = images_path / f"{stem}.png"
        svg_path.write_text(svg, encoding="utf-8")
        image = rasterize_svg(svg)
        image.save(png_path, format="PNG", compress_level=9)
        entries.append(
            {
                "active_dimension": "outline",
                "base_id": base.source.source_id,
                "content": "ambiguous",
                "material": "ambiguous",
                "outline": "face",
                "png": str(png_path),
                "polarity": "outer-black_center-white",
                "sha256": sha256(png_path.read_bytes()).hexdigest(),
                "shading": "none",
                "source_id": base.source.source_id,
                "source_sha256": base.source.sha256,
                "svg": str(svg_path),
            }
        )

        column = index % columns
        row = index // columns
        x = column * (cell_size + gap)
        y = row * (cell_size + label_height + gap)
        preview = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
        montage.paste(preview, (x, y + label_height))
        draw.text((x + 6, y + 12), f"{base.source.source_id} / outline face", fill=245, font=font)

    legacy_montage = output_path / "outline-face-four-sources.png"
    if legacy_montage.exists():
        legacy_montage.unlink()
    montage_path = output_path / "outline-face-supported-sources.png"
    montage.save(montage_path, format="PNG", compress_level=9)
    manifest_path = output_path / "outline-face-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "base_count": len(bases),
                "entries": entries,
                "other_dimensions": {
                    "content": "ambiguous",
                    "material": "ambiguous",
                    "polarity": "outer-black_center-white",
                    "shading": "none",
                },
                "outline": "face",
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "base_count": len(bases),
        "image_count": len(entries),
        "manifest": str(manifest_path),
        "montage": str(montage_path),
    }


def write_source_prototype(config: Config, output: str | Path) -> dict[str, object]:
    output_path = Path(output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    bases = [base for base in source_bases(config.path.parent.parent) if base.source.bank_enabled]
    cell_size = min(256, config.canvas_size)
    label_height = 42
    gap = 10
    columns = 3
    font = ImageFont.load_default(size=15)
    image_paths: list[str] = []
    montage_paths: dict[str, str] = {}
    rows = len(bases)
    for axis in ("content", "outline", "shading", "combined"):
        montage = Image.new(
            "L",
            (
                columns * cell_size + (columns - 1) * gap,
                rows * (cell_size + label_height) + (rows - 1) * gap,
            ),
            150,
        )
        draw = ImageDraw.Draw(montage)
        for row, base in enumerate(bases):
            for column, strength in enumerate((-3, 0, 3)):
                svg = render_cue_svg(config, base, axis, strength)
                if strength == 0:
                    strength_code = "z0"
                else:
                    sign = "m" if strength < 0 else "p"
                    strength_code = f"{sign}{abs(strength)}"
                stem = f"{base.base_id}-{axis}-{strength_code}"
                svg_path = output_path / f"{stem}.svg"
                png_path = output_path / f"{stem}.png"
                svg_path.write_text(svg, encoding="utf-8")
                image = rasterize_svg(svg)
                image.save(png_path, format="PNG", compress_level=9)
                image_paths.append(str(png_path))
                preview = image.resize((cell_size, cell_size), Image.Resampling.LANCZOS)
                x = column * (cell_size + gap)
                y = row * (cell_size + label_height + gap)
                montage.paste(preview, (x, y + label_height))
                label = f"{base.base_id}  {axis}  {strength:+d}"
                draw.text((x + 4, y + 12), label, fill=245, font=font)
        montage_path = output_path / f"source-{axis}-montage.png"
        montage.save(montage_path, format="PNG", compress_level=9)
        montage_paths[axis] = str(montage_path)
    return {
        "ok": True,
        "base_count": len(bases),
        "endpoint_count": len(image_paths),
        "images": image_paths,
        "montages": montage_paths,
    }


# Compatibility name for the existing CLI entry point while the visual gate is active.
write_paper_prototype = write_source_prototype
