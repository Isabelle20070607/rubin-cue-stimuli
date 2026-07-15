from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from .config import Config

BASE_Y = np.array([0.14, 0.22, 0.30, 0.38, 0.46, 0.515, 0.59, 0.71, 0.86])
BASE_WIDTH = np.array([0.165, 0.140, 0.125, 0.090, 0.132, 0.105, 0.155, 0.205, 0.145])
VASE_OUTLINE_DELTA = np.array([0.025, -0.012, 0.004, 0.026, 0.012, 0.022, 0.018, 0.026, 0.020])

# Anatomical landmarks for the shared boundary of the paper-faithful prototype.
# Width is the distance from the center line to one profile. Local minima encode
# protruding nose, lips, and chin; the final two points close the vase foot.
PAPER_PROFILE_Y = np.array(
    [
        0.10,
        0.13,
        0.18,
        0.27,
        0.35,
        0.42,
        0.47,
        0.500,
        0.520,
        0.535,
        0.550,
        0.565,
        0.580,
        0.595,
        0.610,
        0.640,
        0.670,
        0.720,
        0.790,
        0.860,
        0.890,
        0.910,
    ]
)
PAPER_PROFILE_WIDTH = np.array(
    [
        0.350,
        0.300,
        0.260,
        0.235,
        0.220,
        0.195,
        0.165,
        0.145,
        0.075,
        0.120,
        0.112,
        0.103,
        0.118,
        0.106,
        0.120,
        0.100,
        0.130,
        0.148,
        0.140,
        0.140,
        0.145,
        0.340,
    ]
)


@dataclass(frozen=True)
class BaseGeometry:
    base_id: str
    seed: int
    y: np.ndarray
    widths: np.ndarray


def paper_base_geometry(seed: int = 1221945110) -> BaseGeometry:
    """Return the fixed, non-jittered Rubin profile used for visual approval."""
    return BaseGeometry(
        base_id="paper-prototype",
        seed=seed,
        y=PAPER_PROFILE_Y.copy(),
        widths=PAPER_PROFILE_WIDTH.copy(),
    )


def make_base_geometry(config: Config, index: int) -> BaseGeometry:
    if index < 1 or index > config.base_count:
        raise ValueError(f"base index must be between 1 and {config.base_count}")
    seed = config.seed + index * 1009
    rng = np.random.default_rng(seed)
    y = BASE_Y.copy()
    y[1:-1] += rng.normal(0.0, 0.0035, size=len(y) - 2)
    y = np.maximum.accumulate(y)
    widths = BASE_WIDTH + rng.normal(0.0, 0.0055, size=len(BASE_WIDTH))
    widths[0] += rng.uniform(-0.005, 0.005)
    widths[-1] += rng.uniform(-0.005, 0.005)
    widths = np.clip(widths, 0.075, 0.235)
    return BaseGeometry(f"b{index:02d}", seed, y, widths)


def widths_for_strength(base: BaseGeometry, strength: int) -> np.ndarray:
    if strength < -3 or strength > 3:
        raise ValueError("outline strength must be in [-3, 3]")
    if strength == 0:
        return base.widths.copy()
    if len(base.widths) != len(VASE_OUTLINE_DELTA):
        raise ValueError("this geometry does not support the deprecated outline-strength axis")
    widths = base.widths + (strength / 3.0) * VASE_OUTLINE_DELTA
    return np.clip(widths, 0.065, 0.25)


def bezier_segments(y: np.ndarray, widths: np.ndarray) -> list[tuple[np.ndarray, ...]]:
    points = np.column_stack([y, widths])
    segments: list[tuple[np.ndarray, ...]] = []
    for index in range(len(points) - 1):
        before = points[index - 1] if index > 0 else points[index]
        start = points[index]
        end = points[index + 1]
        after = points[index + 2] if index + 2 < len(points) else end
        control1 = start + (end - before) / 6.0
        control2 = end - (after - start) / 6.0
        segments.append((start, control1, control2, end))
    return segments


def sample_profile(
    y: np.ndarray, widths: np.ndarray, samples_per_segment: int = 32
) -> tuple[np.ndarray, np.ndarray]:
    sampled: list[np.ndarray] = []
    for segment_index, (p0, p1, p2, p3) in enumerate(bezier_segments(y, widths)):
        t = np.linspace(0.0, 1.0, samples_per_segment, endpoint=segment_index == len(y) - 2)
        one_minus = 1.0 - t
        curve = (
            one_minus[:, None] ** 3 * p0
            + 3 * one_minus[:, None] ** 2 * t[:, None] * p1
            + 3 * one_minus[:, None] * t[:, None] ** 2 * p2
            + t[:, None] ** 3 * p3
        )
        sampled.append(curve)
    points = np.concatenate(sampled, axis=0)
    return points[:, 0], points[:, 1]


def center_mask(config: Config, base: BaseGeometry, strength: int, scale: int) -> np.ndarray:
    y, widths = sample_profile(base.y, widths_for_strength(base, strength))
    size = config.canvas_size * scale
    center_x = float(config.geometry["center_x"])
    left = [
        ((center_x - width) * size, y_value * size)
        for y_value, width in zip(y, widths, strict=True)
    ]
    right = [
        ((center_x + width) * size, y_value * size)
        for y_value, width in zip(y[::-1], widths[::-1], strict=True)
    ]
    image = Image.new("L", (size, size), 0)
    ImageDraw.Draw(image).polygon(left + right, fill=255)
    return np.asarray(image, dtype=np.uint8) > 0


def svg_center_path(config: Config, base: BaseGeometry, strength: int) -> str:
    center_x = float(config.geometry["center_x"])
    segments = bezier_segments(base.y, widths_for_strength(base, strength))

    def point(pair: np.ndarray, side: int) -> tuple[float, float]:
        y_value, width = pair
        return (center_x + side * width, y_value)

    start_x, start_y = point(segments[0][0], -1)
    commands = [f"M {start_x:.6f} {start_y:.6f}"]
    for _p0, p1, p2, p3 in segments:
        c1 = point(p1, -1)
        c2 = point(p2, -1)
        end = point(p3, -1)
        commands.append(
            f"C {c1[0]:.6f} {c1[1]:.6f} {c2[0]:.6f} {c2[1]:.6f} {end[0]:.6f} {end[1]:.6f}"
        )
    bottom_x, bottom_y = point(segments[-1][3], 1)
    commands.append(f"L {bottom_x:.6f} {bottom_y:.6f}")
    for p0, p1, p2, _p3 in reversed(segments):
        c1 = point(p2, 1)
        c2 = point(p1, 1)
        end = point(p0, 1)
        commands.append(
            f"C {c1[0]:.6f} {c1[1]:.6f} {c2[0]:.6f} {c2[1]:.6f} {end[0]:.6f} {end[1]:.6f}"
        )
    commands.append("Z")
    return " ".join(commands)


def geometry_metrics(base: BaseGeometry, strength: int) -> dict[str, float]:
    y, widths = sample_profile(base.y, widths_for_strength(base, strength), 64)
    path_length = float(np.sum(np.hypot(np.diff(y), np.diff(widths))))
    area = float(2.0 * np.trapezoid(widths, y))
    second_derivative = np.diff(widths, n=2)
    convexity_proxy = float(np.mean(np.abs(second_derivative)))
    return {
        "path_length": path_length,
        "center_area_ratio": area,
        "convexity_proxy": convexity_proxy,
    }
