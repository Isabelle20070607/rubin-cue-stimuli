from __future__ import annotations

import html
import json
from hashlib import sha256
from io import BytesIO

import numpy as np
import resvg_py
from PIL import Image

from .combinations import CombinationSpec
from .config import Config
from .source_geometry import SourceBase

PALETTE_VALUES = {"black": 24, "gray": 133, "white": 232}
PALETTE_HEX = {
    name: f"#{value:02x}{value:02x}{value:02x}" for name, value in PALETTE_VALUES.items()
}


def _points_path(points: list[tuple[float, float]]) -> str:
    if not points:
        raise ValueError("cannot build an empty SVG path")
    commands = [f"M {points[0][0]:.6f} {points[0][1]:.6f}"]
    commands.extend(f"L {x:.6f} {y:.6f}" for x, y in points[1:])
    commands.append("Z")
    return " ".join(commands)


def center_path(base: SourceBase) -> str:
    left = [(0.5 - float(width), float(y)) for y, width in zip(base.y, base.widths, strict=True)]
    right = [
        (0.5 + float(width), float(y))
        for y, width in zip(base.y[::-1], base.widths[::-1], strict=True)
    ]
    return _points_path(left + right)


def face_paths(
    base: SourceBase, top_y_override: float | None = None
) -> tuple[str, str]:
    selected = [(float(y), float(width)) for y, width in zip(base.y, base.widths, strict=True)]
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
    return (
        _points_path(left_profile + [(0.0, bottom_y), (0.0, top_y)]),
        _points_path(right_profile + [(1.0, bottom_y), (1.0, top_y)]),
    )


def shadow_offset(
    config: Config, base: SourceBase, spec: CombinationSpec
) -> tuple[float, float, int]:
    payload = (
        f"{config.version}|{config.seed}|{base.source.source_id}|"
        f"{spec.compact_id}|hard-shadow"
    ).encode()
    seed = int.from_bytes(sha256(payload).digest()[:8], "big")
    rng = np.random.default_rng(seed)
    minimum = config.shadow_min_abs_component
    maximum = config.shadow_max_radius
    for _attempt in range(128):
        dx, dy = rng.normal(0.0, 0.027, size=2)
        radius = float(np.hypot(dx, dy))
        if abs(dx) > minimum and abs(dy) > minimum and radius <= maximum:
            return float(dx), float(dy), seed
    component = (minimum + maximum / float(np.sqrt(2.0))) / 2.0
    signs = rng.choice((-1.0, 1.0), size=2)
    return component * float(signs[0]), component * float(signs[1]), seed


def _moving_average(values: np.ndarray, window: int) -> np.ndarray:
    if window % 2 == 0:
        window += 1
    radius = window // 2
    padded = np.pad(values, (radius, radius), mode="edge")
    return np.convolve(padded, np.ones(window) / window, mode="valid")


def _material_gray(u: float, vertical_slope: float, center_color: str) -> str:
    depth = float(np.sqrt(max(0.0, 1.0 - u * u)))
    normal = np.array([u, -vertical_slope * depth, depth], dtype=np.float64)
    normal /= max(float(np.linalg.norm(normal)), 1e-9)
    light = np.array([-0.46, -0.32, 0.83], dtype=np.float64)
    light /= float(np.linalg.norm(light))
    diffuse = max(0.0, float(np.dot(normal, light)))
    low, high = {
        "black": (18, 92),
        "gray": (52, 220),
        "white": (132, 244),
    }[center_color]
    value = int(round(low + (high - low) * (0.16 + 0.84 * diffuse)))
    value = max(0, min(255, value))
    return f"#{value:02x}{value:02x}{value:02x}"


def _material_vase_mesh(base: SourceBase, center_color: str) -> str:
    y_indices = np.unique(np.linspace(0, len(base.y) - 1, 65).astype(int))
    u_edges = np.linspace(-1.0, 1.0, 33)
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
            fill = _material_gray(midpoint, slope, center_color)
            path = (
                f"M {0.5 + u0 * width0:.6f} {y0:.6f} "
                f"L {0.5 + u1 * width0:.6f} {y0:.6f} "
                f"L {0.5 + u1 * width1:.6f} {y1:.6f} "
                f"L {0.5 + u0 * width1:.6f} {y1:.6f} Z"
            )
            patches.append(f'<path d="{path}" fill="{fill}"/>')
    return '<g id="material-vase-diffuse">' + "".join(patches) + "</g>"


def _content_side(base: SourceBase) -> str:
    digest = sha256(f"{base.source.source_id}|content-face-side".encode()).digest()
    return "left" if digest[0] % 2 == 0 else "right"


def render_factorial_svg(
    config: Config,
    base: SourceBase,
    spec: CombinationSpec,
) -> tuple[str, dict[str, object]]:
    vase_path = center_path(base)
    outline_top_y = base.source.face_outline_top_y if spec.outline == "face" else None
    left_face, right_face = face_paths(base, top_y_override=outline_top_y)
    outer_fill = PALETTE_HEX[spec.outer_color]
    center_fill = PALETTE_HEX[spec.center_color]
    third_fill = PALETTE_HEX[spec.third_color]
    dx, dy, shadow_seed = shadow_offset(config, base, spec)

    content_pattern = ""
    if spec.content is not None:
        content_pattern = (
            '<pattern id="content-stripes" width="1" height=".050" '
            'patternUnits="userSpaceOnUse">'
            f'<rect width="1" height=".050" fill="{outer_fill}"/>'
            f'<rect width="1" height=".018" fill="{third_fill}"/>'
            "</pattern>"
        )
    definitions = (
        f'<defs>{content_pattern}<clipPath id="canvas-clip"><rect width="1" height="1"/>'
        "</clipPath></defs>"
    )

    shadow = ""
    if spec.shading == "figure":
        if spec.figure_region == "vase":
            shadow = (
                f'<path id="hard-shadow-vase" d="{vase_path}" fill="{third_fill}" '
                f'transform="translate({dx:.6f} {dy:.6f})"/>'
            )
        else:
            shadow = (
                '<g id="hard-shadow-faces">'
                f'<path d="{left_face}" fill="{third_fill}" '
                f'transform="translate({dx:.6f} {dy:.6f})"/>'
                f'<path d="{right_face}" fill="{third_fill}" '
                f'transform="translate({-dx:.6f} {dy:.6f})"/></g>'
            )

    if spec.outline == "ambiguous":
        base_layers = (
            f'<rect width="1" height="1" fill="{outer_fill}"/>'
            f"{shadow}"
            f'<path id="vase-figure" d="{vase_path}" fill="{center_fill}"/>'
        )
    else:
        base_layers = (
            f'<rect width="1" height="1" fill="{center_fill}"/>'
            f"{shadow}"
            '<g id="face-figures">'
            f'<path d="{left_face}" fill="{outer_fill}"/>'
            f'<path d="{right_face}" fill="{outer_fill}"/></g>'
        )

    content = ""
    content_side = ""
    if spec.content == "face":
        content_side = _content_side(base)
        selected_path = left_face if content_side == "left" else right_face
        content = (
            '<g id="content-broken-profile-homogeneity">'
            f'<path d="{selected_path}" fill="{third_fill}"/></g>'
        )
    elif spec.content == "vase":
        content = (
            '<g id="content-profile-horizontal-stripes">'
            f'<path d="{left_face}" fill="url(#content-stripes)"/>'
            f'<path d="{right_face}" fill="url(#content-stripes)"/></g>'
        )

    material = _material_vase_mesh(base, spec.center_color) if spec.material == "vase" else ""
    render_params = {
        "background_color": spec.background_color,
        "figure_color": spec.figure_color,
        "figure_region": spec.figure_region,
        "fixation_baked_in": False,
        "shadow_dx": dx if spec.shading == "figure" else 0.0,
        "shadow_dy": dy if spec.shading == "figure" else 0.0,
        "shadow_max_radius": config.shadow_max_radius,
        "shadow_min_abs_component": config.shadow_min_abs_component,
        "shadow_pair_mirrored": spec.figure_region == "face" and spec.shading == "figure",
        "shadow_seed": shadow_seed,
        "shade_color": spec.shade_color,
        "third_color": spec.third_color,
    }
    if spec.content is not None:
        render_params["content_face_accent_side"] = content_side
    metadata = html.escape(
        json.dumps(
            {
                **spec.as_dict(),
                **render_params,
                "source_id": base.source.source_id,
                "source_license": base.source.license_id,
                "source_sha256": base.source.sha256,
            },
            sort_keys=True,
        )
    )
    svg = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" '
        f'width="{config.canvas_size}" height="{config.canvas_size}">'
        f"<metadata>{metadata}</metadata>{definitions}"
        '<g id="factorial-stimulus" clip-path="url(#canvas-clip)">'
        f"{base_layers}{content}{material}</g></svg>\n"
    )
    return svg, render_params


def rasterize_factorial_svg(svg: str) -> Image.Image:
    png = resvg_py.svg_to_bytes(svg_string=svg)
    with Image.open(BytesIO(png)) as image:
        rgba = image.convert("RGBA")
    flattened = Image.new("RGBA", rgba.size, "white")
    flattened.alpha_composite(rgba)
    return flattened.convert("L")
