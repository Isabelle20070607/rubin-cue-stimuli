from __future__ import annotations

import numpy as np

from rubin_cues.combinations import CombinationSpec, combination_specs
from rubin_cues.factorial_render import (
    rasterize_factorial_svg,
    render_factorial_svg,
    shadow_offset,
)
from rubin_cues.source_geometry import source_bases


def _base(config):
    return next(
        base
        for base in source_bases(config.path.parent.parent)
        if base.base_id == "wm-cc0-classic-dark-outer"
    )


def test_vase_shadow_uses_unused_polarity_color(config) -> None:
    spec = CombinationSpec(
        "ambiguous",
        "ambiguous",
        "figure",
        "ambiguous",
        "outer-black_center-gray",
    )
    svg, params = render_factorial_svg(config, _base(config), spec)
    assert 'id="hard-shadow-vase"' in svg
    assert 'fill="#e8e8e8"' in svg
    assert params["shade_color"] == "white"
    assert params["figure_region"] == "vase"
    assert params["fixation_baked_in"] is False


def test_face_shadow_is_mirrored_and_face_directed(config) -> None:
    spec = CombinationSpec(
        "ambiguous",
        "face",
        "figure",
        "ambiguous",
        "outer-gray_center-white",
    )
    svg, params = render_factorial_svg(config, _base(config), spec)
    assert 'id="hard-shadow-faces"' in svg
    assert svg.count('transform="translate(') == 2
    assert params["shadow_pair_mirrored"] is True
    assert spec.face_cues == ("outline", "shading")
    assert spec.vase_cues == ()


def test_shadow_offsets_vary_by_condition_and_clear_component_thresholds(config) -> None:
    base = _base(config)
    active_specs = [spec for spec in combination_specs() if spec.shading == "figure"]
    offsets = [shadow_offset(config, base, spec)[:2] for spec in active_specs]
    assert len(set(offsets)) == len(active_specs)
    assert all(abs(dx) > config.shadow_min_abs_component for dx, _dy in offsets)
    assert all(abs(dy) > config.shadow_min_abs_component for _dx, dy in offsets)
    assert all(np.hypot(dx, dy) <= config.shadow_max_radius for dx, dy in offsets)
    assert offsets == [shadow_offset(config, base, spec)[:2] for spec in active_specs]


def test_klam_full_bank_face_outline_uses_lower_top_closure(config) -> None:
    base = next(
        base
        for base in source_bases(config.path.parent.parent)
        if base.base_id == "wm-bysa-klam-dark-outer"
    )
    spec = CombinationSpec(
        "ambiguous",
        "face",
        "none",
        "ambiguous",
        "outer-black_center-white",
    )
    svg, _params = render_factorial_svg(config, base, spec)
    assert "0.180000" in svg


def test_material_changes_only_the_vase_surface(config) -> None:
    base = _base(config)
    flat = CombinationSpec(
        "ambiguous",
        "ambiguous",
        "none",
        "ambiguous",
        "outer-black_center-white",
    )
    relief = CombinationSpec(
        "ambiguous",
        "ambiguous",
        "none",
        "vase",
        "outer-black_center-white",
    )
    flat_svg, _ = render_factorial_svg(config, base, flat)
    relief_svg, _ = render_factorial_svg(config, base, relief)
    assert "material-vase-diffuse" not in flat_svg
    assert "material-vase-diffuse" in relief_svg
    flat_image = np.asarray(rasterize_factorial_svg(flat_svg))
    relief_image = np.asarray(rasterize_factorial_svg(relief_svg))
    assert not np.array_equal(flat_image, relief_image)
    metadata = relief_svg.split("<metadata>", 1)[1].split("</metadata>", 1)[0]
    assert "fixation_baked_in&quot;: false" in metadata


def test_v2_uses_selected_texture_ranges_and_matched_flat_palette(v2_config) -> None:
    assert v2_config.palette_values == {"black": 43, "gray": 154, "white": 201}
    assert v2_config.material_value_ranges == {
        "black": (20, 58),
        "gray": (103, 186),
        "white": (132, 244),
    }
    assert v2_config.material_shape_rendering == "crispEdges"


def test_v2_material_uses_crisp_edges_to_avoid_mesh_seams(config, v2_config) -> None:
    spec = CombinationSpec(
        None,
        "ambiguous",
        "none",
        "vase",
        "outer-black_center-gray",
    )
    v2_svg, _ = render_factorial_svg(v2_config, _base(v2_config), spec)
    assert '<g id="material-vase-diffuse" shape-rendering="crispEdges">' in v2_svg

    v1_spec = CombinationSpec(
        "ambiguous",
        "ambiguous",
        "none",
        "vase",
        "outer-black_center-gray",
    )
    v1_svg, _ = render_factorial_svg(config, _base(config), v1_spec)
    assert 'shape-rendering="crispEdges"' not in v1_svg
