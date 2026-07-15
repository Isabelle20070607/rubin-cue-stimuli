from __future__ import annotations

import html
import json
from dataclasses import asdict

import numpy as np
from PIL import Image, ImageDraw

from .config import Config
from .geometry import BaseGeometry, center_mask, svg_center_path
from .metrics import match_moments
from .model import StimulusSpec


def _base_array(
    config: Config, base: BaseGeometry, outline_strength: int
) -> tuple[np.ndarray, np.ndarray]:
    scale = config.supersample
    size = config.canvas_size * scale
    mask = center_mask(config, base, outline_strength, scale)
    image = np.full((size, size), int(config.render["outer_gray"]), dtype=np.float64)
    image[mask] = int(config.render["center_gray"])
    return image, mask


def _draw_normalized_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    size: int,
    fill: int,
    width: float,
) -> None:
    draw.line(
        [(round(x * size), round(y * size)) for x, y in points],
        fill=fill,
        width=max(1, round(width * size)),
        joint="curve",
    )


def _content_delta(config: Config, base_mask: np.ndarray, strength: int) -> np.ndarray:
    size = base_mask.shape[0]
    amplitude = int(config.render["cue_contrast_step"]) * abs(strength)
    layer = Image.new("L", (size, size), 128)
    draw = ImageDraw.Draw(layer)
    line_width = 0.0035
    if strength < 0:
        # Six matched face-related strokes: eye, nostril, and mouth on each side.
        for mirror in (-1, 1):

            def mx(x: float, side: int = mirror) -> float:
                return 0.5 + side * (0.5 - x)

            _draw_normalized_line(
                draw,
                [(mx(0.245), 0.335), (mx(0.285), 0.325), (mx(0.315), 0.338)],
                size,
                128 + amplitude,
                line_width,
            )
            _draw_normalized_line(
                draw,
                [(mx(0.310), 0.430), (mx(0.327), 0.442)],
                size,
                128 - amplitude,
                line_width,
            )
            _draw_normalized_line(
                draw,
                [(mx(0.275), 0.535), (mx(0.310), 0.526), (mx(0.332), 0.536)],
                size,
                128 + amplitude,
                line_width,
            )
    else:
        # Six vessel-related strokes with comparable total length and line width.
        strokes = [
            [(0.438, 0.170), (0.470, 0.160), (0.500, 0.158)],
            [(0.500, 0.158), (0.530, 0.160), (0.562, 0.170)],
            [(0.455, 0.300), (0.445, 0.380)],
            [(0.545, 0.300), (0.555, 0.380)],
            [(0.430, 0.710), (0.455, 0.790), (0.480, 0.835)],
            [(0.570, 0.710), (0.545, 0.790), (0.520, 0.835)],
        ]
        for index, stroke in enumerate(strokes):
            _draw_normalized_line(
                draw,
                stroke,
                size,
                128 + amplitude if index % 2 == 0 else 128 - amplitude,
                line_width,
            )
    delta = np.asarray(layer, dtype=np.float64) - 128.0
    target_mask = ~base_mask if strength < 0 else base_mask
    return delta * target_mask


def _shading_delta(base_mask: np.ndarray, strength: int, amplitude: float) -> np.ndarray:
    height, width = base_mask.shape
    y, x = np.mgrid[0:height, 0:width]
    x = x / max(1, width - 1)
    y = y / max(1, height - 1)
    if strength < 0:
        left = np.exp(-(((x - 0.20) / 0.065) ** 2 + ((y - 0.48) / 0.24) ** 2))
        right = np.exp(-(((x - 0.80) / 0.065) ** 2 + ((y - 0.48) / 0.24) ** 2))
        pattern = (left + right) * np.cos(6.0 * np.pi * (y - 0.18))
        target_mask = ~base_mask
    else:
        axial = np.cos(6.0 * np.pi * (x - 0.5) / 0.24)
        envelope = np.exp(-(((x - 0.5) / 0.075) ** 2 + ((y - 0.52) / 0.30) ** 2))
        pattern = axial * envelope
        target_mask = base_mask
    values = pattern[target_mask]
    if values.size:
        pattern = pattern - float(values.mean())
        scale = float(pattern[target_mask].std())
        if scale > 1e-9:
            pattern = pattern / scale
    masked = pattern * target_mask
    gradient_y, gradient_x = np.gradient(masked)
    gradient_energy = float(np.mean(np.hypot(gradient_x, gradient_y)))
    if gradient_energy > 1e-9:
        # Match the global edge contribution of face- and vase-directed fields.
        # Moment matching later handles their luminance and RMS contrast.
        masked = masked / gradient_energy
    return masked * amplitude * 0.01 * abs(strength)


def render_baseline(config: Config, base: BaseGeometry) -> np.ndarray:
    high, _mask = _base_array(config, base, 0)
    source = Image.fromarray(np.rint(high).astype(np.uint8), mode="L")
    final = source.resize((config.canvas_size, config.canvas_size), Image.Resampling.LANCZOS)
    return np.asarray(final, dtype=np.uint8)


def render_stimulus(
    config: Config,
    base: BaseGeometry,
    spec: StimulusSpec,
    baseline: np.ndarray | None = None,
) -> np.ndarray:
    if spec.cue_axis == "baseline":
        return render_baseline(config, base)
    outline_strength = spec.signed_strength if spec.cue_axis in ("outline", "combined") else 0
    image, mask = _base_array(config, base, outline_strength)
    if spec.cue_axis in ("content", "combined"):
        image += _content_delta(config, mask, spec.signed_strength)
    if spec.cue_axis in ("shading", "combined"):
        image += _shading_delta(
            mask,
            spec.signed_strength,
            float(config.render["cue_contrast_step"]) * 0.75,
        )
    image = np.clip(image, 0.0, 255.0)
    source = Image.fromarray(np.rint(image).astype(np.uint8), mode="L")
    final_image = source.resize((config.canvas_size, config.canvas_size), Image.Resampling.LANCZOS)
    final = np.asarray(final_image, dtype=np.uint8)
    target = render_baseline(config, base) if baseline is None else baseline
    return match_moments(final, float(target.mean()), float(target.std()))


def _svg_content(spec: StimulusSpec) -> str:
    if spec.cue_axis not in ("content", "combined"):
        return ""
    opacity = min(0.85, 0.22 * abs(spec.signed_strength))
    if spec.signed_strength < 0:
        paths = [
            "M .245 .335 Q .285 .318 .315 .338",
            "M .310 .430 L .327 .442",
            "M .275 .535 Q .310 .520 .332 .536",
            "M .755 .335 Q .715 .318 .685 .338",
            "M .690 .430 L .673 .442",
            "M .725 .535 Q .690 .520 .668 .536",
        ]
    else:
        paths = [
            "M .438 .170 Q .470 .155 .500 .158",
            "M .500 .158 Q .530 .155 .562 .170",
            "M .455 .300 L .445 .380",
            "M .545 .300 L .555 .380",
            "M .430 .710 Q .455 .790 .480 .835",
            "M .570 .710 Q .545 .790 .520 .835",
        ]
    return "".join(
        f'<path d="{path}" fill="none" stroke="#808080" stroke-width=".004" '
        f'stroke-linecap="round" opacity="{opacity:.3f}"/>'
        for path in paths
    )


def render_svg(config: Config, base: BaseGeometry, spec: StimulusSpec) -> str:
    outline_strength = spec.signed_strength if spec.cue_axis in ("outline", "combined") else 0
    center_path = svg_center_path(config, base, outline_strength)
    outer = int(config.render["outer_gray"])
    center = int(config.render["center_gray"])
    metadata = html.escape(json.dumps({**asdict(spec), "seed": base.seed}, sort_keys=True))
    defs = ""
    shading = ""
    if spec.cue_axis in ("shading", "combined"):
        defs = (
            '<defs><linearGradient id="shade" x1="0" x2="1">'
            '<stop offset="0" stop-color="#555"/><stop offset=".5" stop-color="#ddd"/>'
            '<stop offset="1" stop-color="#555"/></linearGradient></defs>'
        )
        opacity = min(0.55, 0.14 * abs(spec.signed_strength))
        if spec.signed_strength > 0:
            shading = f'<path d="{center_path}" fill="url(#shade)" opacity="{opacity:.3f}"/>'
        else:
            shading = (
                f'<rect width="1" height="1" fill="url(#shade)" opacity="{opacity:.3f}"/>'
                f'<path d="{center_path}" fill="rgb({center},{center},{center})"/>'
            )
    content = _svg_content(spec)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1" '
        f'width="{config.canvas_size}" height="{config.canvas_size}">'
        f"<metadata>{metadata}</metadata>{defs}"
        f'<rect width="1" height="1" fill="rgb({outer},{outer},{outer})"/>'
        f'<path d="{center_path}" fill="rgb({center},{center},{center})"/>'
        f"{shading}{content}</svg>\n"
    )


def phase_scrambled_mask(baseline: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    centered = baseline.astype(np.float64) - float(baseline.mean())
    spectrum = np.fft.rfft2(centered)
    phases = rng.uniform(-np.pi, np.pi, size=spectrum.shape)
    scrambled = np.fft.irfft2(np.abs(spectrum) * np.exp(1j * phases), s=baseline.shape)
    return match_moments(scrambled, float(baseline.mean()), float(baseline.std()))
