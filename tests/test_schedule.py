from __future__ import annotations

import json
from pathlib import Path

from rubin_cues.model import specs_for_base
from rubin_cues.schedule import (
    make_continuous_schedule,
    make_short_schedule,
    response_mapping,
    write_schedule,
)


def _write_manifest(path: Path, base_count: int) -> Path:
    rows = []
    for index in range(1, base_count + 1):
        for spec in specs_for_base(f"b{index:02d}"):
            rows.append(
                {
                    **spec.as_dict(),
                    "png_path": f"png/{spec.stimulus_id}.png",
                }
            )
    manifest = path / "manifest.jsonl"
    manifest.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    (path / "masks.json").write_text(
        json.dumps(
            [
                {"base_id": f"b{index:02d}", "mask_path": f"masks/b{index:02d}.png"}
                for index in range(1, base_count + 1)
            ]
        ),
        encoding="utf-8",
    )
    return manifest


def test_short_schedule_has_four_balanced_blocks(config, tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, 12)
    rows = make_short_schedule(config, manifest, "P001")
    assert len(rows) == 252
    assert {int(row["block"]) for row in rows} == {1, 2, 3, 4}
    assert all(
        not (rows[index]["base_id"] == rows[index - 1]["base_id"] == rows[index - 2]["base_id"])
        for index in range(2, len(rows))
    )
    output = write_schedule(rows, tmp_path / "short.csv")
    assert output.read_bytes().startswith(b"\xef\xbb\xbf")
    assert response_mapping("P001") == response_mapping("P001")


def test_continuous_schedule_has_72_trials_in_three_sessions(config, tmp_path: Path) -> None:
    manifest = _write_manifest(tmp_path, 12)
    selection = {
        "ok": True,
        "selected_bases": [
            {
                "base_id": f"b{index:02d}",
                "axes": {
                    axis: {"face_strength": -2, "vase_strength": 2}
                    for axis in ("content", "outline", "shading")
                },
            }
            for index in range(1, 9)
        ],
    }
    selection_path = tmp_path / "selection.json"
    selection_path.write_text(json.dumps(selection), encoding="utf-8")
    rows = make_continuous_schedule(config, manifest, selection_path, "P002")
    assert len(rows) == 72
    assert {int(row["session"]) for row in rows} == {1, 2, 3}
    assert all(sum(row["session"] == session for row in rows) == 24 for session in (1, 2, 3))
