from __future__ import annotations

import csv
import json
from pathlib import Path

from rubin_cues.model import specs_for_base
from rubin_cues.summarize import summarize_continuous, summarize_short

PROBABILITIES = {-3: 0.9, -2: 0.8, -1: 0.65, 1: 0.35, 2: 0.2, 3: 0.1}


def _write_short_inputs(path: Path, failing_from: int) -> tuple[Path, Path]:
    manifest_rows = []
    responses = []
    for index in range(1, 13):
        for spec in specs_for_base(f"b{index:02d}"):
            manifest_rows.append(spec.as_dict())
            if spec.cue_axis == "baseline":
                p_face = 0.5 if index < failing_from else 0.9
            elif spec.cue_axis in ("content", "outline", "shading"):
                p_face = PROBABILITIES[spec.signed_strength]
            else:
                p_face = 0.95 if spec.signed_strength < 0 else 0.05
            face_count = round(20 * p_face)
            responses.extend(
                {"stimulus_id": spec.stimulus_id, "response": response}
                for response in (["face"] * face_count + ["vase"] * (20 - face_count))
            )
    manifest = path / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(row) + "\n" for row in manifest_rows), encoding="utf-8")
    response_path = path / "responses.csv"
    with response_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["stimulus_id", "response"])
        writer.writeheader()
        writer.writerows(responses)
    return manifest, response_path


def test_selection_succeeds_with_eight_eligible_bases(config, tmp_path: Path) -> None:
    manifest, responses = _write_short_inputs(tmp_path, failing_from=9)
    result = summarize_short(config, responses, manifest, tmp_path / "success")
    assert result["ok"]
    assert result["passing_base_count"] == 8
    assert len(result["selected_bases"]) == 8
    assert all(
        base["axes"][axis]["face_strength"] == -2 and base["axes"][axis]["vase_strength"] == 2
        for base in result["selected_bases"]
        for axis in ("content", "outline", "shading")
    )


def test_selection_fails_instead_of_backfilling(config, tmp_path: Path) -> None:
    manifest, responses = _write_short_inputs(tmp_path, failing_from=8)
    result = summarize_short(config, responses, manifest, tmp_path / "failure")
    assert not result["ok"]
    assert result["passing_base_count"] == 7
    assert len(result["selected_bases"]) == 7


def test_continuous_event_parser_computes_dominance(config, tmp_path: Path) -> None:
    del config
    path = tmp_path / "events.csv"
    rows = [
        {
            "participant": "P001",
            "trial": "1",
            "stimulus_id": "b01-baseline-z0",
            "event_time_ms": value,
            "response": response,
            "stimulus_duration_ms": 30000,
        }
        for value, response in ((1000, "face"), (5000, "vase"), (12000, "unsure"), (15000, "face"))
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = summarize_continuous(path, tmp_path / "summary")
    assert result["ok"]
    assert result["trial_count"] == 1
    text = (tmp_path / "summary" / "continuous-summary.csv").read_text(encoding="utf-8-sig")
    assert "face,3,19000.0,7000.0,3000.0,1000.0" in text
