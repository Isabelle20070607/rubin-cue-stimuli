from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any

from .bank import load_manifest
from .config import Config

SCHEDULE_FIELDS = [
    "participant",
    "mode",
    "session",
    "block",
    "trial",
    "stimulus_id",
    "base_id",
    "cue_axis",
    "signed_strength",
    "target_percept",
    "stimulus_path",
    "mask_path",
    "fixation_ms",
    "stimulus_ms",
    "mask_ms",
    "iti_ms",
    "fixation_during_stimulus",
    "face_key",
    "vase_key",
    "unsure_key",
    "visual_angle_height_deg",
    "visual_angle_width_deg",
    "random_seed",
]


def response_mapping(participant: str) -> dict[str, str]:
    parity = hashlib.sha256(participant.encode("utf-8")).digest()[0] % 2
    return {
        "face_key": "left" if parity == 0 else "right",
        "vase_key": "right" if parity == 0 else "left",
        "unsure_key": "down",
    }


def _constrained_shuffle(rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    for _attempt in range(500):
        shuffled = rows.copy()
        rng.shuffle(shuffled)
        if all(
            not (
                shuffled[index]["base_id"]
                == shuffled[index - 1]["base_id"]
                == shuffled[index - 2]["base_id"]
            )
            for index in range(2, len(shuffled))
        ):
            return shuffled
    raise RuntimeError("could not construct a schedule without three repeated base IDs")


def _mask_lookup(manifest_path: Path) -> dict[str, str]:
    masks = json.loads((manifest_path.parent / "masks.json").read_text(encoding="utf-8"))
    return {str(row["base_id"]): str(row["mask_path"]) for row in masks}


def make_short_schedule(
    config: Config, manifest: str | Path, participant: str, seed: int | None = None
) -> list[dict[str, Any]]:
    manifest_path = Path(manifest).expanduser().resolve()
    rows = load_manifest(manifest_path)
    actual_seed = config.seed if seed is None else int(seed)
    actual_seed += int.from_bytes(hashlib.sha256(participant.encode()).digest()[:4], "big")
    shuffled = _constrained_shuffle(rows, actual_seed)
    masks = _mask_lookup(manifest_path)
    mapping = response_mapping(participant)
    rng = random.Random(actual_seed + 17)
    schedule: list[dict[str, Any]] = []
    for index, row in enumerate(shuffled):
        schedule.append(
            {
                "participant": participant,
                "mode": "short",
                "session": 1,
                "block": index // 63 + 1,
                "trial": index + 1,
                "stimulus_id": row["stimulus_id"],
                "base_id": row["base_id"],
                "cue_axis": row["cue_axis"],
                "signed_strength": int(row["signed_strength"]),
                "target_percept": row["target_percept"],
                "stimulus_path": str((manifest_path.parent / row["png_path"]).resolve()),
                "mask_path": str((manifest_path.parent / masks[row["base_id"]]).resolve()),
                "fixation_ms": rng.randint(
                    int(config.experiment["short_fixation_min_ms"]),
                    int(config.experiment["short_fixation_max_ms"]),
                ),
                "stimulus_ms": int(config.experiment["short_stimulus_ms"]),
                "mask_ms": int(config.experiment["short_mask_ms"]),
                "iti_ms": 0,
                "fixation_during_stimulus": False,
                **mapping,
                "visual_angle_height_deg": config.experiment["visual_angle_height_deg"],
                "visual_angle_width_deg": config.experiment["visual_angle_width_deg"],
                "random_seed": actual_seed,
            }
        )
    return schedule


def make_continuous_schedule(
    config: Config,
    manifest: str | Path,
    selection: str | Path,
    participant: str,
    seed: int | None = None,
) -> list[dict[str, Any]]:
    manifest_path = Path(manifest).expanduser().resolve()
    rows = load_manifest(manifest_path)
    lookup = {
        (str(row["base_id"]), str(row["cue_axis"]), int(row["signed_strength"])): row
        for row in rows
    }
    selected = json.loads(Path(selection).expanduser().resolve().read_text(encoding="utf-8"))
    if not selected.get("ok"):
        raise ValueError("selection report is not successful")
    chosen: list[dict[str, Any]] = []
    for base in selected["selected_bases"]:
        base_id = base["base_id"]
        chosen.append(lookup[(base_id, "baseline", 0)])
        for axis in ("content", "outline", "shading"):
            strengths = base["axes"][axis]
            chosen.append(lookup[(base_id, axis, int(strengths["face_strength"]))])
            chosen.append(lookup[(base_id, axis, int(strengths["vase_strength"]))])
        chosen.append(lookup[(base_id, "combined", -3)])
        chosen.append(lookup[(base_id, "combined", 3)])
    if len(chosen) != int(config.selection["selected_base_count"]) * 9:
        raise ValueError(f"expected 72 selected trials, found {len(chosen)}")
    actual_seed = config.seed if seed is None else int(seed)
    actual_seed += int.from_bytes(hashlib.sha256(participant.encode()).digest()[:4], "big")
    shuffled = _constrained_shuffle(chosen, actual_seed)
    mapping = response_mapping(participant)
    rng = random.Random(actual_seed + 31)
    schedule: list[dict[str, Any]] = []
    for index, row in enumerate(shuffled):
        schedule.append(
            {
                "participant": participant,
                "mode": "continuous",
                "session": index // 24 + 1,
                "block": index // 24 + 1,
                "trial": index + 1,
                "stimulus_id": row["stimulus_id"],
                "base_id": row["base_id"],
                "cue_axis": row["cue_axis"],
                "signed_strength": int(row["signed_strength"]),
                "target_percept": row["target_percept"],
                "stimulus_path": str((manifest_path.parent / row["png_path"]).resolve()),
                "mask_path": "",
                "fixation_ms": int(config.experiment["continuous_fixation_ms"]),
                "stimulus_ms": int(config.experiment["continuous_stimulus_ms"]),
                "mask_ms": 0,
                "iti_ms": rng.randint(
                    int(config.experiment["continuous_iti_min_ms"]),
                    int(config.experiment["continuous_iti_max_ms"]),
                ),
                "fixation_during_stimulus": False,
                **mapping,
                "visual_angle_height_deg": config.experiment["visual_angle_height_deg"],
                "visual_angle_width_deg": config.experiment["visual_angle_width_deg"],
                "random_seed": actual_seed,
            }
        )
    return schedule


def write_schedule(rows: list[dict[str, Any]], output: str | Path) -> Path:
    output_path = Path(output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SCHEDULE_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path
