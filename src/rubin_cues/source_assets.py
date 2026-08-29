from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

import resvg_py
from PIL import Image


@dataclass(frozen=True)
class SourceAsset:
    source_id: str
    relative_path: str
    crop_box: tuple[float, float, float, float]
    face_outline_top_y: float | None = None


SOURCE_ASSETS: tuple[SourceAsset, ...] = (
    SourceAsset(
        source_id="wm-cc0-classic",
        relative_path="wikimedia/two_silhouette_profile_or_a_white_vase.svg",
        crop_box=(0.0, 0.0625, 1.0, 0.9375),
    ),
    SourceAsset(
        source_id="wm-bysa-classic",
        relative_path="wikimedia/cup_or_faces_paradox.svg",
        crop_box=(0.0, 0.0, 1.0, 1.0),
    ),
    SourceAsset(
        source_id="wm-bysa-klam",
        relative_path="wikimedia/klam_dve_tvare_nebo_pohar.svg",
        crop_box=(0.0, 0.0, 1.0, 1.0),
        face_outline_top_y=0.18,
    ),
    SourceAsset(
        source_id="oc-274578-heads",
        relative_path="openclipart/274578_heads_vase_illusion.svg",
        crop_box=(0.1875, 0.0857025, 0.8125, 0.91534875),
    ),
)


def source_path(project_root: str | Path, asset: SourceAsset) -> Path:
    return (
        Path(project_root).expanduser().resolve()
        / "assets"
        / "source"
        / Path(asset.relative_path)
    )


def render_source_preview(project_root: str | Path, asset: SourceAsset) -> Image.Image:
    svg_text = source_path(project_root, asset).read_text(encoding="utf-8")
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg_text)
    with Image.open(BytesIO(png_bytes)) as image:
        return image.convert("RGBA")
