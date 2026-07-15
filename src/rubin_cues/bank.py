from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from .combinations import CombinationSpec, combination_specs_for_source
from .config import Config
from .factorial_render import PALETTE_VALUES, rasterize_factorial_svg, render_factorial_svg
from .metrics import image_metrics, sha256_path
from .render import phase_scrambled_mask
from .source_assets import SOURCE_ASSETS, verify_source_assets
from .source_geometry import SourceBase, source_bases

MANIFEST_FIELDS = [
    "stimulus_id",
    "base_id",
    "source_id",
    "source_sha256",
    "source_license",
    "combination_id",
    "compact_id",
    "content",
    "outline",
    "shading",
    "material",
    "polarity",
    "design_tag",
    "is_conflict",
    "face_cues",
    "vase_cues",
    "figure_region",
    "figure_color",
    "background_color",
    "third_color",
    "shade_color",
    "content_face_accent_side",
    "shadow_dx",
    "shadow_dy",
    "shadow_pair_mirrored",
    "shadow_seed",
    "seed",
    "config_version",
    "png_path",
    "svg_path",
    "file_sha256",
    "svg_sha256",
    "mean_luminance",
    "rms_contrast",
    "edge_energy",
    "center_area_ratio",
    "path_length",
    "convexity_proxy",
    "params_json",
]


def _write_png(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="L").save(
        path,
        format="PNG",
        compress_level=9,
        optimize=False,
    )


def _source_geometry_metrics(base: SourceBase) -> dict[str, float]:
    area = float(np.trapezoid(2.0 * base.widths, base.y))
    segment_lengths = np.hypot(np.diff(base.widths), np.diff(base.y))
    path_length = 2.0 * float(segment_lengths.sum())
    bbox_area = max(1e-9, 2.0 * float(base.widths.max()) * float(base.y[-1] - base.y[0]))
    return {
        "center_area_ratio": area,
        "path_length": path_length,
        "convexity_proxy": area / bbox_area,
    }


def _factorial_bases(config: Config) -> list[SourceBase]:
    project_root = config.path.parent.parent
    candidates = [
        base
        for base in source_bases(project_root)
        if base.polarity == "dark-outer" and base.source.bank_enabled
    ]
    if config.base_count > len(candidates):
        raise ValueError(
            f"project.base_count={config.base_count} exceeds {len(candidates)} source vectors"
        )
    return candidates[: config.base_count]


def _neutral_spec() -> CombinationSpec:
    return CombinationSpec(
        content="ambiguous",
        outline="ambiguous",
        shading="none",
        material="ambiguous",
        polarity="outer-black_center-white",
    )


def generate_bank(
    config: Config,
    output: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    project_root = config.path.parent.parent
    source_errors = verify_source_assets(project_root)
    if source_errors:
        raise ValueError("source asset verification failed: " + "; ".join(source_errors))
    output_path = (
        Path(output).expanduser().resolve()
        if output is not None
        else (project_root / "stimuli" / config.version).resolve()
    )
    if output_path.exists() and any(output_path.iterdir()):
        if not overwrite:
            raise FileExistsError(f"Output is not empty: {output_path}; pass --overwrite")
        if output_path == project_root or project_root not in output_path.parents:
            raise ValueError(f"Refusing to overwrite unsafe output path: {output_path}")
        shutil.rmtree(output_path)

    png_dir = output_path / "png"
    svg_dir = output_path / "svg"
    mask_dir = output_path / "masks"
    for directory in (png_dir, svg_dir, mask_dir):
        directory.mkdir(parents=True, exist_ok=True)

    bases = _factorial_bases(config)
    specs_by_base = {
        base.source.source_id: combination_specs_for_source(base.source.source_id) for base in bases
    }
    rows: list[dict[str, Any]] = []
    mask_rows: list[dict[str, Any]] = []
    for base_index, base in enumerate(bases):
        neutral_svg, _neutral_params = render_factorial_svg(config, base, _neutral_spec())
        neutral = np.asarray(rasterize_factorial_svg(neutral_svg), dtype=np.uint8)
        mask = phase_scrambled_mask(neutral, config.seed + base_index + 41)
        mask_path = mask_dir / f"{base.source.source_id}-mask.png"
        _write_png(mask_path, mask)
        mask_rows.append(
            {
                "base_id": base.source.source_id,
                "mask_path": mask_path.relative_to(output_path).as_posix(),
                "sha256": sha256_path(mask_path),
            }
        )
        geometry_metrics = _source_geometry_metrics(base)

        for spec in specs_by_base[base.source.source_id]:
            stimulus_id = f"{base.source.source_id}__{spec.compact_id}"
            svg, render_params = render_factorial_svg(config, base, spec)
            image = np.asarray(rasterize_factorial_svg(svg), dtype=np.uint8)
            png_path = png_dir / f"{stimulus_id}.png"
            svg_path = svg_dir / f"{stimulus_id}.svg"
            _write_png(png_path, image)
            svg_path.write_text(svg, encoding="utf-8")
            spec_row = spec.as_dict()
            row = {
                "stimulus_id": stimulus_id,
                "base_id": base.source.source_id,
                "source_id": base.source.source_id,
                "source_sha256": base.source.sha256,
                "source_license": base.source.license_id,
                "combination_id": spec.combination_id,
                "compact_id": spec.compact_id,
                **{
                    key: spec_row[key]
                    for key in (
                        "content",
                        "outline",
                        "shading",
                        "material",
                        "polarity",
                        "design_tag",
                        "is_conflict",
                        "face_cues",
                        "vase_cues",
                        "figure_region",
                        "figure_color",
                        "background_color",
                        "third_color",
                        "shade_color",
                    )
                },
                "content_face_accent_side": render_params["content_face_accent_side"],
                "shadow_dx": render_params["shadow_dx"],
                "shadow_dy": render_params["shadow_dy"],
                "shadow_pair_mirrored": render_params["shadow_pair_mirrored"],
                "shadow_seed": render_params["shadow_seed"],
                "seed": config.seed,
                "config_version": config.version,
                "png_path": png_path.relative_to(output_path).as_posix(),
                "svg_path": svg_path.relative_to(output_path).as_posix(),
                "file_sha256": sha256_path(png_path),
                "svg_sha256": sha256_path(svg_path),
                **image_metrics(image),
                **geometry_metrics,
                "params_json": json.dumps(
                    {
                        "fixation_baked_in": False,
                        "palette_values": PALETTE_VALUES,
                        "render": render_params,
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            }
            rows.append(row)

    csv_path = output_path / "manifest.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    jsonl_path = output_path / "manifest.jsonl"
    with jsonl_path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    masks_path = output_path / "masks.json"
    masks_path.write_text(
        json.dumps(mask_rows, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    tag_counts = {
        tag: sum(row["design_tag"] == tag for row in rows)
        for tag in ("face", "ambiguous", "vase", "conflict")
    }
    generation = {
        "schema_version": 7,
        "bank_kind": "factorial",
        "config_version": config.version,
        "config_path": str(config.path),
        "canvas_size": config.canvas_size,
        "base_count": len(bases),
        "conditions_by_base": {
            base.source.source_id: len(specs_by_base[base.source.source_id]) for base in bases
        },
        "stimulus_count": len(rows),
        "mask_count": len(mask_rows),
        "base_ids": [base.source.source_id for base in bases],
        "excluded_source_ids": [
            asset.source_id
            for asset in SOURCE_ASSETS
            if asset.formal_bank_member and not asset.bank_enabled
        ],
        "tag_counts": tag_counts,
        "shadow_bounds": {
            "max_radius": config.shadow_max_radius,
            "min_abs_component": config.shadow_min_abs_component,
        },
        "quality": config.quality,
        "output": str(output_path),
    }
    (output_path / "generation.json").write_text(
        json.dumps(generation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return generation


def load_manifest(path: str | Path) -> list[dict[str, Any]]:
    manifest_path = Path(path).expanduser().resolve()
    if manifest_path.suffix.lower() == ".jsonl":
        with manifest_path.open("r", encoding="utf-8") as stream:
            return [json.loads(line) for line in stream if line.strip()]
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))
