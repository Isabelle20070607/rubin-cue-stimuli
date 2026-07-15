from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

from .bank import load_manifest
from .config import Config


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).expanduser().resolve().open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summarize_short(
    config: Config, responses: str | Path, manifest: str | Path, output: str | Path
) -> dict[str, Any]:
    response_rows = _read_csv(responses)
    manifest_rows = load_manifest(manifest)
    manifest_lookup = {str(row["stimulus_id"]): row for row in manifest_rows}
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"face": 0, "vase": 0, "unsure": 0})
    for row in response_rows:
        stimulus_id = row["stimulus_id"]
        response = row["response"].strip().lower()
        if stimulus_id not in manifest_lookup:
            raise ValueError(f"unknown stimulus ID in responses: {stimulus_id}")
        if response not in ("face", "vase", "unsure"):
            raise ValueError(f"invalid response: {response}")
        counts[stimulus_id][response] += 1
    summary_rows: list[dict[str, Any]] = []
    probability_lookup: dict[str, float] = {}
    for stimulus_id, count in sorted(counts.items()):
        decisive = count["face"] + count["vase"]
        p_face = count["face"] / decisive if decisive else float("nan")
        probability_lookup[stimulus_id] = p_face
        manifest_row = manifest_lookup[stimulus_id]
        total = decisive + count["unsure"]
        summary_rows.append(
            {
                "stimulus_id": stimulus_id,
                "base_id": manifest_row["base_id"],
                "cue_axis": manifest_row["cue_axis"],
                "signed_strength": int(manifest_row["signed_strength"]),
                "face_count": count["face"],
                "vase_count": count["vase"],
                "unsure_count": count["unsure"],
                "p_face": p_face,
                "unsure_rate": count["unsure"] / total if total else float("nan"),
            }
        )
    output_path = Path(output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    _write_csv(
        output_path / "short-summary.csv",
        summary_rows,
        [
            "stimulus_id",
            "base_id",
            "cue_axis",
            "signed_strength",
            "face_count",
            "vase_count",
            "unsure_count",
            "p_face",
            "unsure_rate",
        ],
    )

    by_base: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in manifest_rows:
        by_base[str(row["base_id"])].append(row)
    candidate_bases: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    target_mid = (
        float(config.selection["target_probability_min"])
        + float(config.selection["target_probability_max"])
    ) / 2.0
    for base_id, rows in sorted(by_base.items()):
        baseline_row = next(row for row in rows if row["cue_axis"] == "baseline")
        baseline_p = probability_lookup.get(str(baseline_row["stimulus_id"]), float("nan"))
        reasons: list[str] = []
        if not (
            float(config.selection["baseline_face_min"])
            <= baseline_p
            <= float(config.selection["baseline_face_max"])
        ):
            reasons.append("baseline_outside_range")
        axes: dict[str, dict[str, Any]] = {}
        for axis in ("content", "outline", "shading"):
            axis_rows = sorted(
                [row for row in rows if row["cue_axis"] == axis],
                key=lambda row: int(row["signed_strength"]),
            )
            strengths: list[int] = []
            probabilities: list[float] = []
            for row in axis_rows:
                stimulus_id = str(row["stimulus_id"])
                if stimulus_id in probability_lookup and np.isfinite(
                    probability_lookup[stimulus_id]
                ):
                    strengths.append(int(row["signed_strength"]))
                    probabilities.append(probability_lookup[stimulus_id])
            if len(strengths) != 6:
                reasons.append(f"{axis}_missing_responses")
                continue
            slope = float(np.polyfit(strengths, probabilities, 1)[0])
            if slope >= 0:
                reasons.append(f"{axis}_nonnegative_slope")
            negative = [
                (strength, probability)
                for strength, probability in zip(strengths, probabilities, strict=True)
                if strength < 0
            ]
            positive = [
                (strength, probability)
                for strength, probability in zip(strengths, probabilities, strict=True)
                if strength > 0
            ]
            face_strength, face_probability = min(
                negative, key=lambda pair: abs(pair[1] - target_mid)
            )
            vase_strength, vase_p_face = min(
                positive, key=lambda pair: abs(pair[1] - (1.0 - target_mid))
            )
            target_min = float(config.selection["target_probability_min"])
            target_max = float(config.selection["target_probability_max"])
            if not target_min <= face_probability <= target_max:
                reasons.append(f"{axis}_face_target_outside_range")
            if not target_min <= 1.0 - vase_p_face <= target_max:
                reasons.append(f"{axis}_vase_target_outside_range")
            axes[axis] = {
                "slope": slope,
                "face_strength": face_strength,
                "face_probability": face_probability,
                "vase_strength": vase_strength,
                "vase_probability": 1.0 - vase_p_face,
            }
        payload = {
            "base_id": base_id,
            "baseline_p_face": baseline_p,
            "balance_score": abs(baseline_p - 0.5),
            "axes": axes,
            "reasons": reasons,
        }
        if reasons:
            rejected.append(payload)
        else:
            candidate_bases.append(payload)
    candidate_bases.sort(key=lambda row: row["balance_score"])
    required = int(config.selection["selected_base_count"])
    selection = {
        "ok": len(candidate_bases) >= required,
        "required_base_count": required,
        "passing_base_count": len(candidate_bases),
        "selected_bases": candidate_bases[:required],
        "rejected_bases": rejected,
    }
    selection_path = output_path / "selection.json"
    selection_path.write_text(json.dumps(selection, indent=2, sort_keys=True), encoding="utf-8")
    return {
        **selection,
        "summary_path": str(output_path / "short-summary.csv"),
        "selection_path": str(selection_path),
    }


def summarize_continuous(responses: str | Path, output: str | Path) -> dict[str, Any]:
    response_rows = _read_csv(responses)
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in response_rows:
        key = (row.get("participant", ""), row["trial"], row["stimulus_id"])
        groups[key].append(row)
    summaries: list[dict[str, Any]] = []
    for (participant, trial, stimulus_id), events in sorted(groups.items()):
        ordered = sorted(events, key=lambda row: float(row["event_time_ms"]))
        stimulus_ms = float(ordered[0]["stimulus_duration_ms"])
        durations: dict[str, list[float]] = {"face": [], "vase": [], "unsure": []}
        states: list[tuple[float, str]] = []
        last_state = ""
        for event in ordered:
            state = event["response"].strip().lower()
            if state not in durations:
                raise ValueError(f"invalid continuous response: {state}")
            if state == last_state:
                continue
            states.append((float(event["event_time_ms"]), state))
            last_state = state
        for index, (start, state) in enumerate(states):
            end = states[index + 1][0] if index + 1 < len(states) else stimulus_ms
            durations[state].append(max(0.0, end - start))
        first_percept = states[0][1] if states else "missing"
        reported_ms = sum(sum(values) for values in durations.values())
        summaries.append(
            {
                "participant": participant,
                "trial": trial,
                "stimulus_id": stimulus_id,
                "first_percept": first_percept,
                "switch_count": max(0, len(states) - 1),
                "face_ms": sum(durations["face"]),
                "vase_ms": sum(durations["vase"]),
                "unsure_ms": sum(durations["unsure"]),
                "unreported_ms": max(0.0, stimulus_ms - reported_ms),
                "face_median_ms": median(durations["face"]) if durations["face"] else "",
                "vase_median_ms": median(durations["vase"]) if durations["vase"] else "",
                "stimulus_duration_ms": stimulus_ms,
            }
        )
    output_path = Path(output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    fields = list(summaries[0].keys()) if summaries else ["participant", "trial", "stimulus_id"]
    summary_path = output_path / "continuous-summary.csv"
    _write_csv(summary_path, summaries, fields)
    return {"ok": True, "trial_count": len(summaries), "summary_path": str(summary_path)}
