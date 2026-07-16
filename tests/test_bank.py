from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from rubin_cues.bank import generate_bank, load_manifest
from rubin_cues.montage import create_montages
from rubin_cues.validate import validate_manifest


def test_small_bank_is_complete_valid_and_reproducible(small_config, tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_report = generate_bank(small_config, first)
    second_report = generate_bank(small_config, second)
    assert first_report["bank_kind"] == second_report["bank_kind"] == "factorial"
    assert first_report["stimulus_count"] == second_report["stimulus_count"] == 192
    assert first_report["mask_count"] == second_report["mask_count"] == 2
    assert first_report["tag_counts"] == {
        "face": 48,
        "ambiguous": 12,
        "vase": 60,
        "conflict": 72,
    }

    first_rows = load_manifest(first / "manifest.jsonl")
    second_rows = load_manifest(second / "manifest.jsonl")
    assert [row["file_sha256"] for row in first_rows] == [row["file_sha256"] for row in second_rows]
    assert [row["svg_sha256"] for row in first_rows] == [row["svg_sha256"] for row in second_rows]
    assert validate_manifest(first / "manifest.csv")["ok"]

    masks = json.loads((first / "masks.json").read_text(encoding="utf-8"))
    with Image.open(first / masks[0]["mask_path"]) as image:
        assert image.mode == "L"
        assert image.size == (small_config.canvas_size, small_config.canvas_size)


def test_v2_bank_has_versioned_schema_without_content_or_conflict(
    small_v2_config, tmp_path: Path
) -> None:
    output = tmp_path / "v2"
    report = generate_bank(small_v2_config, output)
    assert report["schema_version"] == 8
    assert report["design_profile"] == "v2"
    assert report["stimulus_count"] == 60
    assert report["tag_counts"] == {"face": 24, "ambiguous": 12, "vase": 24}

    rows = load_manifest(output / "manifest.jsonl")
    assert rows
    assert all("content" not in row for row in rows)
    assert all("is_conflict" not in row for row in rows)
    assert all("content_face_accent_side" not in row for row in rows)
    assert all(row["design_tag"] != "conflict" for row in rows)
    assert any(row["shading"] == "figure" for row in rows)
    assert validate_manifest(output / "manifest.csv")["ok"]
    montage_report = create_montages(output / "manifest.jsonl", cell_size=32)
    assert Path(montage_report["baseline_overview"]).exists()
    assert len(montage_report["base_montages"]) == 2
