from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from rubin_cues.config import Config
from rubin_cues.prototype import (
    PROOF_DIMENSIONS,
    PROOF_STATES,
    rasterize_svg,
    render_cue_svg,
    render_dimension_proof_svg,
    render_endpoint_svg,
    write_dimension_proof,
    write_face_outline_proof,
    write_source_prototype,
)
from rubin_cues.source_geometry import source_bases


def test_source_bases_are_valid_and_unique(config: Config) -> None:
    bases = source_bases(config.path.parent.parent)
    assert len(bases) == 12
    assert len({base.base_id for base in bases}) == 12
    for base in bases:
        assert np.all(np.diff(base.y) > 0)
        assert np.all(base.widths > 0)
        assert np.all(base.widths < 0.5)
        assert float(base.y[0]) < base.face_top < base.face_bottom < float(base.y[-1])


def test_endpoint_svgs_render_without_baked_fixation(small_config: Config) -> None:
    for base in source_bases(small_config.path.parent.parent):
        rendered = []
        for strength in (-3, 0, 3):
            svg = render_endpoint_svg(small_config, base, strength)
            assert "&quot;fixation_baked_in&quot;: false" in svg
            image = np.asarray(rasterize_svg(svg), dtype=np.uint8)
            assert image.shape == (
                small_config.canvas_size,
                small_config.canvas_size,
            )
            rendered.append(image)
        assert not np.array_equal(rendered[0], rendered[1])
        assert not np.array_equal(rendered[1], rendered[2])


def test_all_cue_axes_have_distinct_signed_endpoints(small_config: Config) -> None:
    base = source_bases(small_config.path.parent.parent)[0]
    baseline = np.asarray(rasterize_svg(render_cue_svg(small_config, base, "content", 0)))
    for axis in ("content", "outline", "shading", "combined"):
        face = np.asarray(rasterize_svg(render_cue_svg(small_config, base, axis, -3)))
        vase = np.asarray(rasterize_svg(render_cue_svg(small_config, base, axis, 3)))
        assert not np.array_equal(face, baseline)
        assert not np.array_equal(vase, baseline)
        assert not np.array_equal(face, vase)


def test_face_cues_use_full_contour_without_vertical_reveal_window(
    small_config: Config,
) -> None:
    base = source_bases(small_config.path.parent.parent)[0]
    content_svg = render_cue_svg(small_config, base, "content", -3)
    outline_svg = render_cue_svg(small_config, base, "outline", -3)
    top = float(base.y[0])
    bottom = float(base.y[-1])

    assert f"0.000000 {top:.6f}" in content_svg
    assert f"0.000000 {bottom:.6f}" in content_svg
    assert f"L 0.000000 {top:.6f} M 0.000000 {bottom:.6f}" in outline_svg
    assert f"M 0.000000 {top:.6f} L 0.000000 {bottom:.6f}" not in outline_svg


def test_source_endpoint_montage_contains_all_bases(small_config: Config, tmp_path: Path) -> None:
    result = write_source_prototype(small_config, tmp_path)
    assert result["base_count"] == 8
    assert result["endpoint_count"] == 96
    assert set(result["montages"]) == {"content", "outline", "shading", "combined"}
    assert all(Path(str(path)).is_file() for path in result["montages"].values())


def test_dimension_proof_changes_only_one_named_axis(small_config: Config) -> None:
    base = source_bases(small_config.path.parent.parent)[0]
    baseline_images = []
    for dimension in PROOF_DIMENSIONS:
        rendered = []
        for state in PROOF_STATES[dimension]:
            svg = render_dimension_proof_svg(small_config, base, dimension, state)
            assert f"&quot;active_dimension&quot;: &quot;{dimension}&quot;" in svg
            assert "&quot;fixation_baked_in&quot;: false" in svg
            rendered.append(np.asarray(rasterize_svg(svg), dtype=np.uint8))
        assert all(
            not np.array_equal(left, right)
            for index, left in enumerate(rendered)
            for right in rendered[index + 1 :]
        )
        baseline_state = "ambiguous"
        if baseline_state in PROOF_STATES[dimension]:
            svg = render_dimension_proof_svg(small_config, base, dimension, baseline_state)
            baseline_images.append(np.asarray(rasterize_svg(svg), dtype=np.uint8))
    assert all(np.array_equal(baseline_images[0], image) for image in baseline_images[1:])


def test_content_proof_uses_published_homogeneity_manipulations(
    small_config: Config,
) -> None:
    base = source_bases(small_config.path.parent.parent)[0]
    face = render_dimension_proof_svg(small_config, base, "content", "face")
    vase = render_dimension_proof_svg(small_config, base, "content", "vase")
    assert "content-broken-profile-homogeneity" in face
    assert "#5b5b5b" in face
    assert "content-profile-horizontal-stripes" in vase
    assert "horizontal-stripes" in vase
    assert "stipple" not in face + vase


def test_outline_has_only_ambiguous_and_paper_face_states() -> None:
    assert PROOF_STATES["outline"] == ("ambiguous", "face")


def test_face_outline_proof_writes_one_clean_derivative_per_source(
    small_config: Config, tmp_path: Path
) -> None:
    result = write_face_outline_proof(small_config, tmp_path)
    assert result["base_count"] == 4
    assert result["image_count"] == 4
    assert Path(str(result["montage"])).is_file()
    manifest = json.loads(Path(str(result["manifest"])).read_text(encoding="utf-8"))
    assert {entry["source_id"] for entry in manifest["entries"]} == {
        "wm-cc0-classic",
        "wm-bysa-classic",
        "wm-bysa-klam",
        "oc-274578-heads",
    }
    assert manifest["other_dimensions"] == {
        "content": "ambiguous",
        "material": "ambiguous",
        "polarity": "outer-black_center-white",
        "shading": "none",
    }
    for entry in manifest["entries"]:
        svg = Path(entry["svg"]).read_text(encoding="utf-8")
        assert "outline-face-paper-endpoint" in svg
        assert "hard-shadow" not in svg
        assert "material-vase" not in svg
        assert "content-" not in svg
        image = np.asarray(rasterize_svg(svg), dtype=np.uint8)
        assert image[0, image.shape[1] // 2] > 200
        assert image[-1, image.shape[1] // 2] > 200


def test_face_outline_proof_can_select_disabled_candidate_sources(
    small_config: Config, tmp_path: Path
) -> None:
    selected = ["wm-bysa-klam", "oc-274578-heads"]
    result = write_face_outline_proof(
        small_config,
        tmp_path,
        source_ids=selected,
    )
    assert result["base_count"] == 2
    manifest = json.loads(Path(str(result["manifest"])).read_text(encoding="utf-8"))
    assert [entry["source_id"] for entry in manifest["entries"]] == selected


def test_klam_face_outline_uses_source_specific_top_closure(small_config: Config) -> None:
    base = next(
        base
        for base in source_bases(small_config.path.parent.parent)
        if base.base_id == "wm-bysa-klam-dark-outer"
    )
    assert float(base.y[0]) < 0.18
    svg = render_dimension_proof_svg(small_config, base, "outline", "face")
    assert "0.180000" in svg


def test_hard_shading_and_vase_material_are_structurally_distinct(
    small_config: Config,
) -> None:
    base = source_bases(small_config.path.parent.parent)[0]
    shading = render_dimension_proof_svg(small_config, base, "shading", "paper-vase")
    material = render_dimension_proof_svg(small_config, base, "material", "vase")
    assert "Gradient" not in shading
    assert "filter" not in shading
    assert "shading-paper-vase" in shading
    assert 'fill="#858585"' in shading
    assert 'id="hard-cast-shadow"' in shading
    assert 'transform="translate(.027 .054)"' in shading
    assert 'id="unshifted-white-vase"' in shading
    assert 'fill-rule="evenodd"' not in shading
    assert "Gradient" not in material
    assert "filter" not in material
    assert "material-vase-diffuse" in material
    assert material.count("<path") > 1000


def test_material_has_only_ambiguous_and_vase_states() -> None:
    assert PROOF_STATES["material"] == ("ambiguous", "vase")


def test_polarity_is_six_ordered_gray_pair_mappings() -> None:
    assert len(PROOF_STATES["polarity"]) == 6
    assert len(set(PROOF_STATES["polarity"])) == 6
    for state in PROOF_STATES["polarity"]:
        outer, center = state.split("_", maxsplit=1)
        assert outer.removeprefix("outer-") != center.removeprefix("center-")


def test_dimension_proof_excludes_geometry_dimension(small_config: Config, tmp_path: Path) -> None:
    result = write_dimension_proof(small_config, tmp_path)
    assert "geometry" not in PROOF_DIMENSIONS
    assert result["dimension_count"] == 5
    assert result["base_count"] == 1
    assert result["image_count"] == 15
    assert set(result["montages"]) == set(PROOF_DIMENSIONS)
    assert Path(str(result["overview"])).is_file()
    assert Path(str(result["manifest"])).is_file()
    assert not list((tmp_path / "images").glob("geometry-*.png"))
    assert len(list((tmp_path / "images").glob("*.png"))) == 15
    assert len(list((tmp_path / "images").glob("*.svg"))) == 15
