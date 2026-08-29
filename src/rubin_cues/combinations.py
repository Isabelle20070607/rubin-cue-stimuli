from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Literal

OutlineState = Literal["ambiguous", "face"]
ShadingState = Literal["none", "figure"]
MaterialState = Literal["ambiguous", "vase"]
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


@dataclass(frozen=True)
class CombinationSpec:
    outline: OutlineState
    shading: ShadingState
    material: MaterialState
    polarity: str

    def __post_init__(self) -> None:
        if self.shading == "figure" and self.material == "vase":
            raise ValueError("shading=figure and material=vase are mutually exclusive")
        if self.outline == "face" and self.material == "vase":
            raise ValueError("face outline and vase material point in opposing directions")

    @property
    def face_cues(self) -> tuple[str, ...]:
        if self.outline != "face":
            return ()
        return ("outline", "shading") if self.shading == "figure" else ("outline",)

    @property
    def vase_cues(self) -> tuple[str, ...]:
        cues: list[str] = []
        if self.shading == "figure" and self.outline == "ambiguous":
            cues.append("shading")
        if self.material == "vase":
            cues.append("material")
        return tuple(cues)

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
    def third_color(self) -> str:
        return next(
            color
            for color in ("black", "gray", "white")
            if color not in (self.outer_color, self.center_color)
        )

    @property
    def compact_id(self) -> str:
        outline_code = {"ambiguous": "a", "face": "f"}[self.outline]
        shading_code = {"none": "n", "figure": "f"}[self.shading]
        material_code = {"ambiguous": "a", "vase": "v"}[self.material]
        color_code = {"black": "b", "gray": "g", "white": "w"}
        polarity_code = color_code[self.outer_color] + color_code[self.center_color]
        return f"o{outline_code}-s{shading_code}-m{material_code}-p{polarity_code}"

def combination_specs() -> list[CombinationSpec]:
    specs: list[CombinationSpec] = []
    for outline, shading, material, polarity in product(
        OUTLINE_STATES,
        SHADING_STATES,
        MATERIAL_STATES,
        POLARITY_STATES,
    ):
        if shading == "figure" and material == "vase":
            continue
        if outline == "face" and material == "vase":
            continue
        specs.append(CombinationSpec(outline, shading, material, polarity))
    return specs
