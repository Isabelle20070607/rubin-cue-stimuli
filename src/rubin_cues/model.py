from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

CueAxis = Literal["baseline", "content", "outline", "shading", "combined"]
Percept = Literal["face", "vase", "ambiguous"]


@dataclass(frozen=True)
class StimulusSpec:
    base_id: str
    cue_axis: CueAxis
    signed_strength: int

    @property
    def target_percept(self) -> Percept:
        if self.signed_strength < 0:
            return "face"
        if self.signed_strength > 0:
            return "vase"
        return "ambiguous"

    @property
    def stimulus_id(self) -> str:
        if self.cue_axis == "baseline":
            return f"{self.base_id}-baseline-z0"
        sign = "m" if self.signed_strength < 0 else "p"
        return f"{self.base_id}-{self.cue_axis}-{sign}{abs(self.signed_strength)}"

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["stimulus_id"] = self.stimulus_id
        payload["target_percept"] = self.target_percept
        return payload


def specs_for_base(base_id: str) -> list[StimulusSpec]:
    specs = [StimulusSpec(base_id, "baseline", 0)]
    for axis in ("content", "outline", "shading"):
        specs.extend(StimulusSpec(base_id, axis, strength) for strength in (-3, -2, -1, 1, 2, 3))
    specs.extend((StimulusSpec(base_id, "combined", -3), StimulusSpec(base_id, "combined", 3)))
    return specs
