from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
from pathlib import Path

import resvg_py
from PIL import Image


@dataclass(frozen=True)
class SourceAsset:
    source_id: str
    relative_path: str
    family_kind: str
    rendering_kind: str
    creator: str
    license_id: str
    source_url: str
    sha256: str
    crop_box: tuple[float, float, float, float]
    face_y_range: tuple[float, float]
    face_outline_allowed: bool
    bank_enabled: bool
    formal_bank_member: bool = True
    face_outline_top_y: float | None = None


SOURCE_ASSETS: tuple[SourceAsset, ...] = (
    SourceAsset(
        source_id="wm-cc0-classic",
        relative_path="wikimedia/two_silhouette_profile_or_a_white_vase.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="Ian Remsen",
        license_id="CC0-1.0",
        source_url=(
            "https://commons.wikimedia.org/wiki/File:Two_silhouette_profile_or_a_white_vase.svg"
        ),
        sha256="596EEB6B073D2C83ECB93EDF53BF7EB1B7ADF8A7511997D49E7535B276479706",
        crop_box=(0.0, 0.0625, 1.0, 0.9375),
        face_y_range=(0.08, 0.92),
        face_outline_allowed=True,
        bank_enabled=True,
    ),
    SourceAsset(
        source_id="wm-bysa-classic",
        relative_path="wikimedia/cup_or_faces_paradox.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="Bryan Derksen",
        license_id="CC-BY-SA-3.0",
        source_url=("https://commons.wikimedia.org/wiki/File:Cup_or_faces_paradox.svg"),
        sha256="BB34384AC53365954798F19FB94DE3DA1913138B3177DAE5077C623FA1FEE610",
        crop_box=(0.0, 0.0, 1.0, 1.0),
        face_y_range=(0.08, 0.94),
        face_outline_allowed=True,
        bank_enabled=True,
    ),
    SourceAsset(
        source_id="wm-bysa-klam",
        relative_path="wikimedia/klam_dve_tvare_nebo_pohar.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="Kenjiro995; vectorization by Mrmw",
        license_id="CC-BY-SA-3.0",
        source_url=(
            "https://commons.wikimedia.org/wiki/File:Klam-DveTvareNeboPohar.svg"
        ),
        sha256="C00669A03066F139199AD755A4602B6BE1958669111B1CCAC726FDA7731591C8",
        crop_box=(0.0, 0.0, 1.0, 1.0),
        face_y_range=(0.02, 0.98),
        face_outline_allowed=True,
        bank_enabled=True,
        formal_bank_member=True,
        face_outline_top_y=0.18,
    ),
    SourceAsset(
        source_id="oc-274578-heads",
        relative_path="openclipart/274578_heads_vase_illusion.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="GDJ",
        license_id="CC0-1.0",
        source_url="https://openclipart.org/detail/274578/heads-vase-illusion",
        sha256="8CAE2F5E0D4DF810EFF9F4C745FB3573574F75BAB604F6038E3833CFE0C473F4",
        crop_box=(0.1875, 0.0857025, 0.8125, 0.91534875),
        face_y_range=(0.02, 0.98),
        face_outline_allowed=True,
        bank_enabled=True,
        formal_bank_member=True,
    ),
    SourceAsset(
        source_id="oc-276846-profile",
        relative_path="openclipart/276846_rubins_vase.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="yamachem",
        license_id="CC0-1.0",
        source_url="https://openclipart.org/detail/276846/rubins-gobletprofile",
        sha256="19F83DE704464555259BAFCBDF3B1A6700BB8720CA8E2195985F04DD4EF045E8",
        crop_box=(0.0, 0.0, 1.0, 1.0),
        face_y_range=(0.30, 0.92),
        face_outline_allowed=False,
        bank_enabled=False,
    ),
    SourceAsset(
        source_id="oc-276861-full-faces",
        relative_path="openclipart/276861_rubins_vase_variation.svg",
        family_kind="classic-face-vase",
        rendering_kind="filled",
        creator="GDJ",
        license_id="CC0-1.0",
        source_url=("https://openclipart.org/detail/276861/yamachems-rubins-vase-variation"),
        sha256="A948997561CEB5ECD131C6AD3B2270EDC51457EA6BDBC063E577A3101F859061",
        crop_box=(0.0, 0.0, 1.0, 1.0),
        face_y_range=(0.50, 0.94),
        face_outline_allowed=False,
        bank_enabled=False,
    ),
)


def source_root(project_root: str | Path) -> Path:
    return Path(project_root).expanduser().resolve() / "assets" / "source"


def source_path(project_root: str | Path, asset: SourceAsset) -> Path:
    return source_root(project_root) / Path(asset.relative_path)


def verify_source_assets(project_root: str | Path) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for asset in SOURCE_ASSETS:
        if asset.source_id in seen_ids:
            errors.append(f"duplicate source ID: {asset.source_id}")
        seen_ids.add(asset.source_id)
        path = source_path(project_root, asset)
        if not path.is_file():
            errors.append(f"missing source SVG: {path}")
            continue
        payload = path.read_bytes()
        actual_hash = sha256(payload).hexdigest().upper()
        if actual_hash != asset.sha256:
            errors.append(f"source hash mismatch: {asset.source_id}")
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as exc:
            errors.append(f"invalid SVG XML for {asset.source_id}: {exc}")
            continue
        if root.tag.rsplit("}", 1)[-1] != "svg":
            errors.append(f"unexpected root element for {asset.source_id}: {root.tag}")
        for element in root.iter():
            local_name = element.tag.rsplit("}", 1)[-1].lower()
            if local_name == "script":
                errors.append(f"embedded script in source SVG: {asset.source_id}")
            for value in element.attrib.values():
                if "javascript:" in value.lower():
                    errors.append(f"javascript URL in source SVG: {asset.source_id}")
    return errors


def render_source_preview(project_root: str | Path, asset: SourceAsset) -> Image.Image:
    """Rasterize an immutable source master without altering its XML or paths."""
    svg_text = source_path(project_root, asset).read_text(encoding="utf-8")
    png_bytes = resvg_py.svg_to_bytes(svg_string=svg_text)
    with Image.open(BytesIO(png_bytes)) as image:
        return image.convert("RGBA")
