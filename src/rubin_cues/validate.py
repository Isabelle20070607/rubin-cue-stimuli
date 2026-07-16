from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from PIL import Image

from .bank import load_manifest
from .combinations import CombinationSpec, combination_specs_for_source
from .metrics import sha256_path
from .source_assets import SOURCE_ASSETS


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes")


def validate_manifest(path: str | Path) -> dict[str, Any]:
    manifest_path = Path(path).expanduser().resolve()
    root = manifest_path.parent
    rows = load_manifest(manifest_path)
    generation_path = root / "generation.json"
    if not generation_path.exists():
        raise FileNotFoundError(f"Missing generation metadata: {generation_path}")
    generation = json.loads(generation_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    warnings: list[str] = []

    if generation.get("bank_kind") != "factorial":
        errors.append("generation metadata is not a factorial bank")
    design_profile = str(generation.get("design_profile", "v1"))
    if design_profile not in ("v1", "v2"):
        errors.append(f"unknown generation design profile: {design_profile}")
        design_profile = "v1"
    expected_schema_version = 7 if design_profile == "v1" else 8
    if int(generation.get("schema_version", -1)) != expected_schema_version:
        errors.append(
            f"expected schema version {expected_schema_version} for {design_profile}"
        )
    shadow_bounds = generation.get("shadow_bounds", {})
    try:
        shadow_min_abs_component = float(shadow_bounds["min_abs_component"])
        shadow_max_radius = float(shadow_bounds["max_radius"])
    except (KeyError, TypeError, ValueError):
        errors.append("generation metadata has invalid shadow bounds")
        shadow_min_abs_component = 0.0
        shadow_max_radius = 0.0
    if (
        shadow_min_abs_component <= 0.0
        or shadow_max_radius <= (2.0**0.5) * shadow_min_abs_component
    ):
        errors.append("generation metadata has infeasible shadow bounds")
    ids = [str(row.get("stimulus_id", "")) for row in rows]
    base_ids = sorted({str(row.get("base_id", "")) for row in rows})
    declared_base_ids = [str(base_id) for base_id in generation.get("base_ids", [])]
    enabled_source_ids = {asset.source_id for asset in SOURCE_ASSETS if asset.bank_enabled}
    disabled_source_ids = sorted(
        asset.source_id
        for asset in SOURCE_ASSETS
        if asset.formal_bank_member and not asset.bank_enabled
    )
    if not set(declared_base_ids).issubset(enabled_source_ids):
        errors.append("generation metadata includes a disabled source")
    if sorted(str(value) for value in generation.get("excluded_source_ids", [])) != (
        disabled_source_ids
    ):
        errors.append("generation metadata has the wrong excluded source IDs")
    expected_specs_by_base: dict[str, list[CombinationSpec]] = {}
    for base_id in declared_base_ids:
        try:
            expected_specs_by_base[base_id] = combination_specs_for_source(
                base_id, design_profile=design_profile
            )
        except ValueError as exc:
            errors.append(str(exc))
    expected_count = sum(len(specs) for specs in expected_specs_by_base.values())
    if len(ids) != len(set(ids)):
        errors.append("manifest contains duplicate stimulus IDs")
    if len(rows) != expected_count:
        errors.append(f"expected {expected_count} stimuli, found {len(rows)}")
    expected_conditions_by_base = {
        base_id: len(specs) for base_id, specs in expected_specs_by_base.items()
    }
    actual_conditions_by_base = {
        str(base_id): int(count)
        for base_id, count in dict(generation.get("conditions_by_base", {})).items()
    }
    if actual_conditions_by_base != expected_conditions_by_base:
        errors.append("generation metadata has the wrong conditions-by-base counts")
    if int(generation.get("stimulus_count", -1)) != len(rows):
        errors.append("generation metadata stimulus count does not match manifest")
    if len(base_ids) != int(generation.get("base_count", 0)):
        errors.append("generation metadata base count does not match manifest")
    if set(base_ids) != set(declared_base_ids):
        errors.append("generation metadata base IDs do not match manifest")

    by_base: dict[str, list[dict[str, Any]]] = defaultdict(list)
    tag_counts: Counter[str] = Counter()
    for row in rows:
        stimulus_id = str(row.get("stimulus_id", ""))
        base_id = str(row.get("base_id", ""))
        by_base[base_id].append(row)
        try:
            spec = CombinationSpec(
                content=(
                    str(row["content"]) if design_profile == "v1" else None
                ),  # type: ignore[arg-type]
                outline=str(row["outline"]),  # type: ignore[arg-type]
                shading=str(row["shading"]),  # type: ignore[arg-type]
                material=str(row["material"]),  # type: ignore[arg-type]
                polarity=str(row["polarity"]),
            )
        except (KeyError, ValueError) as exc:
            errors.append(f"{stimulus_id}: invalid combination fields ({exc})")
            continue
        if str(row.get("combination_id", "")) != spec.combination_id:
            errors.append(f"{stimulus_id}: combination ID mismatch")
        if str(row.get("compact_id", "")) != spec.compact_id:
            errors.append(f"{stimulus_id}: compact ID mismatch")
        if str(row.get("design_tag", "")) != spec.design_tag:
            errors.append(f"{stimulus_id}: design tag mismatch")
        if design_profile == "v1":
            if _as_bool(row.get("is_conflict")) != (spec.design_tag == "conflict"):
                errors.append(f"{stimulus_id}: conflict flag mismatch")
        else:
            for forbidden_field in ("content", "is_conflict", "content_face_accent_side"):
                if forbidden_field in row:
                    errors.append(f"{stimulus_id}: v2 contains {forbidden_field}")
            if spec.design_tag == "conflict":
                errors.append(f"{stimulus_id}: v2 contains a conflict condition")
        for field, expected in (
            ("figure_region", spec.figure_region),
            ("figure_color", spec.figure_color),
            ("background_color", spec.background_color),
            ("third_color", spec.third_color),
            ("shade_color", spec.shade_color),
        ):
            if str(row.get(field, "")) != expected:
                errors.append(f"{stimulus_id}: {field} mismatch")
        if str(row.get("face_cues", "")) != "|".join(spec.face_cues):
            errors.append(f"{stimulus_id}: face cue list mismatch")
        if str(row.get("vase_cues", "")) != "|".join(spec.vase_cues):
            errors.append(f"{stimulus_id}: vase cue list mismatch")
        dx = float(row.get("shadow_dx", 0.0))
        dy = float(row.get("shadow_dy", 0.0))
        if spec.shading == "figure":
            radius = (dx * dx + dy * dy) ** 0.5
            if (
                abs(dx) <= shadow_min_abs_component
                or abs(dy) <= shadow_min_abs_component
                or radius > shadow_max_radius
            ):
                errors.append(f"{stimulus_id}: shadow displacement outside bounds")
        elif abs(dx) > 1e-12 or abs(dy) > 1e-12:
            errors.append(f"{stimulus_id}: inactive shading has a displacement")
        tag_counts[spec.design_tag] += 1

        png_path = root / str(row.get("png_path", ""))
        svg_path = root / str(row.get("svg_path", ""))
        for artifact in (png_path, svg_path):
            if not artifact.exists():
                errors.append(f"missing artifact: {artifact}")
        if png_path.exists():
            with Image.open(png_path) as image:
                if image.mode != "L":
                    errors.append(f"{stimulus_id}: expected grayscale L, got {image.mode}")
                expected_size = int(generation["canvas_size"])
                if image.size != (expected_size, expected_size):
                    errors.append(f"{stimulus_id}: unexpected image size {image.size}")
            if sha256_path(png_path) != str(row.get("file_sha256", "")):
                errors.append(f"{stimulus_id}: PNG hash mismatch")
        if svg_path.exists() and sha256_path(svg_path) != str(row.get("svg_sha256", "")):
            errors.append(f"{stimulus_id}: SVG hash mismatch")

    for base_id, base_rows in by_base.items():
        actual = {str(row.get("compact_id", "")) for row in base_rows}
        expected_compact_ids = {spec.compact_id for spec in expected_specs_by_base.get(base_id, [])}
        if actual != expected_compact_ids:
            errors.append(f"{base_id}: incorrect source-compatible combination set")

    if dict(tag_counts) != generation.get("tag_counts"):
        errors.append("generation tag counts do not match manifest")

    masks_path = root / "masks.json"
    if not masks_path.exists():
        errors.append(f"missing mask registry: {masks_path}")
        masks: list[dict[str, Any]] = []
    else:
        masks = json.loads(masks_path.read_text(encoding="utf-8"))
    if len(masks) != len(base_ids):
        errors.append(f"expected {len(base_ids)} masks, found {len(masks)}")
    for mask in masks:
        mask_path = root / str(mask["mask_path"])
        if not mask_path.exists():
            errors.append(f"missing mask: {mask_path}")
        elif sha256_path(mask_path) != str(mask["sha256"]):
            errors.append(f"mask hash mismatch: {mask['base_id']}")

    warnings.append(
        "Polarity deliberately changes luminance; compare image metrics within planned contrasts."
    )
    return {
        "ok": not errors,
        "manifest": str(manifest_path),
        "stimulus_count": len(rows),
        "base_count": len(base_ids),
        "mask_count": len(masks),
        "tag_counts": dict(tag_counts),
        "errors": errors,
        "warnings": warnings,
    }
