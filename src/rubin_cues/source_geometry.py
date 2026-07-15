from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image, ImageFilter

from .source_assets import SOURCE_ASSETS, SourceAsset, render_source_preview

Polarity = Literal["dark-outer", "light-outer"]


@dataclass(frozen=True)
class SourceContour:
    source: SourceAsset
    y: np.ndarray
    widths: np.ndarray
    face_top: float
    face_bottom: float


@dataclass(frozen=True)
class SourceBase:
    base_id: str
    source: SourceAsset
    polarity: Polarity
    y: np.ndarray
    widths: np.ndarray
    face_top: float
    face_bottom: float


def _interpolate_missing(values: np.ndarray, valid: np.ndarray) -> np.ndarray:
    indices = np.arange(len(values), dtype=np.float64)
    if int(valid.sum()) < max(8, len(values) // 10):
        raise ValueError("too few shared-boundary samples in source SVG")
    return np.interp(indices, indices[valid], values[valid])


def _median_smooth(values: np.ndarray, window: int = 13) -> np.ndarray:
    if window % 2 == 0:
        raise ValueError("median window must be odd")
    radius = window // 2
    padded = np.pad(values, (radius, radius), mode="edge")
    windows = np.lib.stride_tricks.sliding_window_view(padded, window)
    return np.median(windows, axis=1)


def extract_source_contour(
    project_root: str | Path, asset: SourceAsset, samples: int = 384
) -> SourceContour:
    if samples < 64:
        raise ValueError("source contour requires at least 64 samples")
    preview = render_source_preview(project_root, asset)
    width, height = preview.size
    left, top, right, bottom = asset.crop_box
    crop = preview.crop(
        (
            round(left * width),
            round(top * height),
            round(right * width),
            round(bottom * height),
        )
    )
    flattened = Image.new("RGBA", crop.size, "white")
    flattened.alpha_composite(crop)
    blur_radius = max(0.8, crop.width / 700.0)
    grayscale = flattened.convert("L").filter(ImageFilter.GaussianBlur(blur_radius))
    pixels = np.asarray(grayscale, dtype=np.float64)
    gradient = np.abs(np.diff(pixels, axis=1))
    crop_height, crop_width = pixels.shape
    midpoint = crop_width // 2
    left_start = max(1, round(0.08 * crop_width))
    right_stop = min(crop_width - 2, round(0.92 * crop_width))

    left_region = gradient[:, left_start:midpoint]
    right_region = gradient[:, midpoint:right_stop]
    left_peak = left_region.max(axis=1)
    right_peak = right_region.max(axis=1)
    left_x = left_region.argmax(axis=1).astype(np.float64) + left_start
    right_x = right_region.argmax(axis=1).astype(np.float64) + midpoint
    threshold = max(6.0, float(np.percentile(np.r_[left_peak, right_peak], 30)) * 0.35)
    valid = (left_peak >= threshold) & (right_peak >= threshold) & (left_x < right_x)
    left_x = _median_smooth(_interpolate_missing(left_x, valid))
    right_x = _median_smooth(_interpolate_missing(right_x, valid))

    # The online masters are mirror-symmetric. Averaging the two detected sides removes
    # antialiasing noise while retaining the downloaded shared-boundary shape.
    half_width = np.clip((right_x - left_x) / 2.0, 2.0, None)
    center = float(np.median((right_x + left_x) / 2.0))
    left_x = center - half_width
    right_x = center + half_width

    horizontal_margin = 0.08 * crop_width
    content_left = max(0.0, float(left_x.min() - horizontal_margin))
    content_right = min(float(crop_width - 1), float(right_x.max() + horizontal_margin))
    content_width = content_right - content_left
    if content_width <= 1.0:
        raise ValueError(f"invalid content width for {asset.source_id}")

    normalized_half_width = half_width / content_width
    source_aspect = content_width / max(1.0, float(crop_height))
    if source_aspect >= 1.0:
        box_width = 0.86
        box_height = 0.86 / source_aspect
    else:
        box_height = 0.86
        box_width = 0.86 * source_aspect
    y_start = (1.0 - box_height) / 2.0
    sample_rows = np.linspace(0.0, crop_height - 1.0, samples)
    row_indices = np.arange(crop_height, dtype=np.float64)
    sampled_widths = np.interp(sample_rows, row_indices, normalized_half_width) * box_width
    sampled_y = y_start + np.linspace(0.0, box_height, samples)
    face_top = y_start + asset.face_y_range[0] * box_height
    face_bottom = y_start + asset.face_y_range[1] * box_height
    return SourceContour(
        source=asset,
        y=sampled_y,
        widths=sampled_widths,
        face_top=face_top,
        face_bottom=face_bottom,
    )


def source_bases(project_root: str | Path) -> list[SourceBase]:
    bases: list[SourceBase] = []
    for asset in SOURCE_ASSETS:
        contour = extract_source_contour(project_root, asset)
        for polarity in ("dark-outer", "light-outer"):
            bases.append(
                SourceBase(
                    base_id=f"{asset.source_id}-{polarity}",
                    source=asset,
                    polarity=polarity,
                    y=contour.y.copy(),
                    widths=contour.widths.copy(),
                    face_top=contour.face_top,
                    face_bottom=contour.face_bottom,
                )
            )
    return bases
