from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from .source_assets import SOURCE_ASSETS

ContentState = Literal["face", "ambiguous", "vase"]
OutlineState = Literal["ambiguous", "face"]
ShadingState = Literal["none", "figure"]
MaterialState = Literal["ambiguous", "vase"]
DesignTag = Literal["face", "ambiguous", "vase", "conflict"]

CONTENT_STATES: tuple[ContentState, ...] = ("face", "ambiguous", "vase")
OUTLINE_STATES: tuple[OutlineState, ...] = ("ambiguous", "face")
SHADING_STATES: tuple[ShadingState, ...] = ("none", "figure")
MATERIAL_STATES: tuple[MaterialState, ...] = ("ambiguous", "vase")
POLARITY_STATES = (
    "outer-black_center-gray",
    "outer-black_center-white",
    "outer-gray_center-black",
    "outer-gray_center-white",
    "outer-white_center-black",
    "outer-white_center-gray",
)

COMBINATION_FIELDS = (
    "combination_id",
    "content",
    "outline",
    "shading",
    "material",
    "polarity",
    "figure_region",
    "figure_color",
    "background_color",
    "third_color",
    "shade_color",
    "design_tag",
    "is_conflict",
    "face_cues",
    "vase_cues",
)


@dataclass(frozen=True)
class CombinationSpec:
    content: ContentState
    outline: OutlineState
    shading: ShadingState
    material: MaterialState
    polarity: str

    def __post_init__(self) -> None:
        if self.shading == "figure" and self.material == "vase":
            raise ValueError("shading=figure and material=vase are mutually exclusive")
        if self.shading == "figure" and self.content == "face":
            raise ValueError("shading=figure and content=face are mutually exclusive")

    @property
    def face_cues(self) -> tuple[str, ...]:
        cues: list[str] = []
        if self.content == "face":
            cues.append("content")
        if self.outline == "face":
            cues.append("outline")
            if self.shading == "figure":
                cues.append("shading")
        return tuple(cues)

    @property
    def vase_cues(self) -> tuple[str, ...]:
        cues: list[str] = []
        if self.content == "vase":
            cues.append("content")
        if self.shading == "figure" and self.outline == "ambiguous":
            cues.append("shading")
        if self.material == "vase":
            cues.append("material")
        return tuple(cues)

    @property
    def design_tag(self) -> DesignTag:
        has_face = bool(self.face_cues)
        has_vase = bool(self.vase_cues)
        if has_face and has_vase:
            return "conflict"
        if has_face:
            return "face"
        if has_vase:
            return "vase"
        return "ambiguous"

    @property
    def outer_color(self) -> str:
        outer_part, _center_part = self.polarity.split("_", maxsplit=1)
        return outer_part.removeprefix("outer-")

    @property
    def center_color(self) -> str:
        _outer_part, center_part = self.polarity.split("_", maxsplit=1)
        return center_part.removeprefix("center-")

    @property
    def figure_region(self) -> str:
        return "face" if self.outline == "face" else "vase"

    @property
    def figure_color(self) -> str:
        return self.outer_color if self.figure_region == "face" else self.center_color

    @property
    def background_color(self) -> str:
        return self.center_color if self.figure_region == "face" else self.outer_color

    @property
    def shade_color(self) -> str:
        if self.shading == "none":
            return ""
        return self.third_color

    @property
    def third_color(self) -> str:
        return next(
            color
            for color in ("black", "gray", "white")
            if color not in (self.figure_color, self.background_color)
        )

    @property
    def compact_id(self) -> str:
        content_code = {"face": "f", "ambiguous": "a", "vase": "v"}[self.content]
        outline_code = {"ambiguous": "a", "face": "f"}[self.outline]
        shading_code = {"none": "n", "figure": "f"}[self.shading]
        material_code = {"ambiguous": "a", "vase": "v"}[self.material]
        color_code = {"black": "b", "gray": "g", "white": "w"}
        polarity_code = color_code[self.outer_color] + color_code[self.center_color]
        return f"c{content_code}-o{outline_code}-s{shading_code}-m{material_code}-p{polarity_code}"

    @property
    def combination_id(self) -> str:
        return (
            f"content-{self.content}__outline-{self.outline}__"
            f"shading-{self.shading}__material-{self.material}__"
            f"polarity-{self.polarity}"
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "combination_id": self.combination_id,
            "content": self.content,
            "outline": self.outline,
            "shading": self.shading,
            "material": self.material,
            "polarity": self.polarity,
            "figure_region": self.figure_region,
            "figure_color": self.figure_color,
            "background_color": self.background_color,
            "third_color": self.third_color,
            "shade_color": self.shade_color,
            "design_tag": self.design_tag,
            "is_conflict": self.design_tag == "conflict",
            "face_cues": "|".join(self.face_cues),
            "vase_cues": "|".join(self.vase_cues),
        }


def combination_specs(*, allow_face_outline: bool = True) -> list[CombinationSpec]:
    outline_states: tuple[OutlineState, ...] = (
        OUTLINE_STATES if allow_face_outline else ("ambiguous",)
    )
    return [
        CombinationSpec(content, outline, shading, material, polarity)
        for content in CONTENT_STATES
        for outline in outline_states
        for shading in SHADING_STATES
        for material in MATERIAL_STATES
        for polarity in POLARITY_STATES
        if not (shading == "figure" and material == "vase")
        if not (shading == "figure" and content == "face")
    ]


def combination_specs_for_source(source_id: str) -> list[CombinationSpec]:
    try:
        source = next(asset for asset in SOURCE_ASSETS if asset.source_id == source_id)
    except StopIteration as exc:
        raise ValueError(f"unknown source ID: {source_id}") from exc
    return combination_specs(allow_face_outline=source.face_outline_allowed)


def write_combination_audit(output: str | Path) -> dict[str, object]:
    output_path = Path(output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    specs = combination_specs()
    rows = [spec.as_dict() for spec in specs]

    csv_path = output_path / "combinations.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COMBINATION_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    tag_counts: dict[str, int] = {
        tag: sum(spec.design_tag == tag for spec in specs)
        for tag in ("face", "ambiguous", "vase", "conflict")
    }
    json_path = output_path / "combinations.json"
    json_path.write_text(
        json.dumps(
            {
                "combination_count": len(rows),
                "rows": rows,
                "tag_counts": tag_counts,
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
        "combination_count": len(rows),
        "csv": str(csv_path),
        "json": str(json_path),
        "tag_counts": tag_counts,
    }
