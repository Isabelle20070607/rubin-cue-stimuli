from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from rubin_cues.combinations import (
    CombinationSpec,
    combination_specs,
    combination_specs_for_source,
    write_combination_audit,
)


def test_factorial_combination_count_and_ids_are_unique() -> None:
    specs = combination_specs()
    assert len(specs) == 96
    assert len({spec.combination_id for spec in specs}) == 96
    assert len({spec.compact_id for spec in specs}) == 96


def test_v2_removes_content_and_conflict_while_retaining_shading() -> None:
    specs = combination_specs(design_profile="v2")
    assert len(specs) == 30
    assert len({spec.combination_id for spec in specs}) == 30
    assert len({spec.compact_id for spec in specs}) == 30
    assert all(spec.content is None for spec in specs)
    assert all("content" not in spec.as_dict() for spec in specs)
    assert all("content" not in spec.combination_id for spec in specs)
    assert all(not spec.compact_id.startswith("c") for spec in specs)
    assert all(spec.design_tag != "conflict" for spec in specs)
    assert all(not (spec.face_cues and spec.vase_cues) for spec in specs)
    assert any(spec.shading == "figure" for spec in specs)
    assert {
        tag: sum(spec.design_tag == tag for spec in specs)
        for tag in ("face", "ambiguous", "vase")
    } == {"face": 12, "ambiguous": 6, "vase": 12}


def test_shading_and_material_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        CombinationSpec(
            content="ambiguous",
            outline="ambiguous",
            shading="figure",
            material="vase",
            polarity="outer-black_center-white",
        )
    assert all(
        not (spec.shading == "figure" and spec.material == "vase") for spec in combination_specs()
    )


def test_shading_and_different_colored_faces_are_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        CombinationSpec(
            content="face",
            outline="ambiguous",
            shading="figure",
            material="ambiguous",
            polarity="outer-black_center-white",
        )
    assert all(
        not (spec.shading == "figure" and spec.content == "face") for spec in combination_specs()
    )


def test_face_outline_is_excluded_only_for_incompatible_sources() -> None:
    expected_counts = {
        "wm-cc0-classic": 96,
        "wm-bysa-classic": 96,
        "wm-bysa-klam": 96,
        "oc-274578-heads": 96,
        "oc-276846-profile": 48,
        "oc-276861-full-faces": 48,
    }
    for source_id, expected_count in expected_counts.items():
        specs = combination_specs_for_source(source_id)
        assert len(specs) == expected_count
        if source_id in {"oc-276846-profile", "oc-276861-full-faces"}:
            assert {spec.outline for spec in specs} == {"ambiguous"}
        else:
            assert {spec.outline for spec in specs} == {"ambiguous", "face"}


def test_design_tag_counts_keep_opposing_cues_as_conflict() -> None:
    specs = combination_specs()
    counts = {
        tag: sum(spec.design_tag == tag for spec in specs)
        for tag in ("face", "ambiguous", "vase", "conflict")
    }
    assert counts == {"face": 24, "ambiguous": 6, "vase": 30, "conflict": 36}
    for spec in specs:
        assert (spec.design_tag == "conflict") is bool(spec.face_cues and spec.vase_cues)


def test_polarity_does_not_change_the_design_tag() -> None:
    tags_by_directional_state: dict[tuple[str, ...], set[str]] = {}
    for spec in combination_specs():
        key = (spec.content, spec.outline, spec.shading, spec.material)
        tags_by_directional_state.setdefault(key, set()).add(spec.design_tag)
    assert all(len(tags) == 1 for tags in tags_by_directional_state.values())


def test_shading_follows_the_current_figure() -> None:
    for spec in combination_specs():
        if spec.shading == "none":
            assert "shading" not in spec.face_cues + spec.vase_cues
            assert spec.shade_color == ""
            continue
        assert spec.shade_color not in (spec.figure_color, spec.background_color)
        assert spec.shade_color == spec.third_color
        assert {spec.figure_color, spec.background_color, spec.shade_color} == {
            "black",
            "gray",
            "white",
        }
        if spec.outline == "face":
            assert spec.figure_region == "face"
            assert "shading" in spec.face_cues
            assert "shading" not in spec.vase_cues
        else:
            assert spec.figure_region == "vase"
            assert "shading" in spec.vase_cues
            assert "shading" not in spec.face_cues


def test_combination_audit_writes_all_rows(tmp_path: Path) -> None:
    result = write_combination_audit(tmp_path)
    assert result["combination_count"] == 96
    assert result["tag_counts"] == {
        "face": 24,
        "ambiguous": 6,
        "vase": 30,
        "conflict": 36,
    }
    csv_path = Path(str(result["csv"]))
    json_path = Path(str(result["json"]))
    with csv_path.open("r", encoding="utf-8-sig", newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 96
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["combination_count"] == 96


def test_v2_combination_audit_omits_removed_fields(tmp_path: Path) -> None:
    result = write_combination_audit(tmp_path, design_profile="v2")
    assert result["combination_count"] == 30
    assert result["tag_counts"] == {"face": 12, "ambiguous": 6, "vase": 12}
    with Path(str(result["csv"])).open(
        "r", encoding="utf-8-sig", newline=""
    ) as stream:
        reader = csv.DictReader(stream)
        assert "content" not in (reader.fieldnames or [])
        assert "is_conflict" not in (reader.fieldnames or [])
        assert len(list(reader)) == 30
