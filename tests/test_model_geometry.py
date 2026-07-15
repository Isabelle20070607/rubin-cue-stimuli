from __future__ import annotations

import numpy as np

from rubin_cues.geometry import (
    center_mask,
    make_base_geometry,
    sample_profile,
    widths_for_strength,
)
from rubin_cues.metrics import image_metrics
from rubin_cues.model import specs_for_base
from rubin_cues.render import render_baseline, render_stimulus


def test_each_base_has_21_unique_conditions() -> None:
    specs = specs_for_base("b01")
    assert len(specs) == 21
    assert len({spec.stimulus_id for spec in specs}) == 21
    assert sum(spec.cue_axis == "baseline" for spec in specs) == 1
    assert [spec.signed_strength for spec in specs if spec.cue_axis == "combined"] == [
        -3,
        3,
    ]


def test_profile_is_monotone_symmetric_and_non_self_intersecting(config) -> None:
    base = make_base_geometry(config, 1)
    y, widths = sample_profile(base.y, base.widths, samples_per_segment=64)
    assert np.all(np.diff(y) >= 0)
    assert np.all(widths > 0)
    left = 0.5 - widths
    right = 0.5 + widths
    assert np.all(left < right)
    assert np.allclose(0.5 - left, right - 0.5)


def test_center_mask_and_inverse_form_complete_partition(small_config) -> None:
    base = make_base_geometry(small_config, 1)
    mask = center_mask(small_config, base, 0, scale=1)
    assert mask.dtype == np.bool_
    assert np.all(np.logical_xor(mask, ~mask))
    assert np.all(np.logical_or(mask, ~mask))


def test_only_outline_axis_changes_shared_boundary(small_config) -> None:
    base = make_base_geometry(small_config, 1)
    baseline_mask = center_mask(small_config, base, 0, scale=1)
    outline_mask = center_mask(small_config, base, 3, scale=1)
    assert not np.array_equal(baseline_mask, outline_mask)
    for axis in ("content", "shading"):
        negative = next(
            spec
            for spec in specs_for_base(base.base_id)
            if spec.cue_axis == axis and spec.signed_strength == -3
        )
        baseline = render_baseline(small_config, base)
        rendered = render_stimulus(small_config, base, negative, baseline)
        assert rendered.shape == baseline.shape
        assert not np.array_equal(rendered, baseline)
        assert np.array_equal(center_mask(small_config, base, 0, scale=1), baseline_mask)


def test_outline_parameter_varies_monotonically(config) -> None:
    base = make_base_geometry(config, 1)
    total_widths = [float(widths_for_strength(base, value).sum()) for value in range(-3, 4)]
    assert total_widths == sorted(total_widths)


def test_rendered_cue_magnitude_increases_with_strength(small_config) -> None:
    base = make_base_geometry(small_config, 1)
    baseline = render_baseline(small_config, base).astype(np.float64)
    for axis in ("content", "outline", "shading"):
        for direction in (-1, 1):
            distances = []
            for magnitude in (1, 2, 3):
                strength = direction * magnitude
                spec = next(
                    spec
                    for spec in specs_for_base(base.base_id)
                    if spec.cue_axis == axis and spec.signed_strength == strength
                )
                rendered = render_stimulus(
                    small_config, base, spec, baseline.astype(np.uint8)
                ).astype(np.float64)
                distances.append(float(np.mean(np.abs(rendered - baseline))))
            assert distances == sorted(distances)


def test_full_resolution_shading_pairs_match_edge_energy(config) -> None:
    base = make_base_geometry(config, 1)
    baseline = render_baseline(config, base)
    rendered = {}
    for strength in (-3, -2, -1, 1, 2, 3):
        spec = next(
            spec
            for spec in specs_for_base(base.base_id)
            if spec.cue_axis == "shading" and spec.signed_strength == strength
        )
        rendered[strength] = image_metrics(render_stimulus(config, base, spec, baseline))[
            "edge_energy"
        ]
    for magnitude in (1, 2, 3):
        first = rendered[-magnitude]
        second = rendered[magnitude]
        relative_difference = abs(first - second) / max(first, second)
        assert relative_difference <= float(config.quality["edge_pair_relative_max"])
