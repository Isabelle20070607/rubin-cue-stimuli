from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .bank import load_manifest
from .combinations import POLARITY_STATES, combination_specs_for_source


def _lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, Any]]:
    result: dict[tuple[str, int], dict[str, Any]] = {}
    baseline = next(row for row in rows if row["cue_axis"] == "baseline")
    for axis in ("content", "outline", "shading"):
        result[(axis, 0)] = baseline
    for row in rows:
        result[(str(row["cue_axis"]), int(row["signed_strength"]))] = row
    return result


def create_montages(
    manifest: str | Path, output: str | Path | None = None, cell_size: int = 160
) -> dict[str, Any]:
    manifest_path = Path(manifest).expanduser().resolve()
    root = manifest_path.parent
    output_path = Path(output).expanduser().resolve() if output else (root / "montages").resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    rows = load_manifest(manifest_path)
    if rows and "design_tag" in rows[0]:
        return _create_factorial_montages(root, output_path, rows, cell_size)
    base_ids = sorted({str(row["base_id"]) for row in rows})
    font = ImageFont.load_default()
    label_height = 22
    strengths = [-3, -2, -1, 0, 1, 2, 3]
    axes = ["content", "outline", "shading", "combined"]
    montage_paths: list[str] = []
    for base_id in base_ids:
        base_rows = [row for row in rows if row["base_id"] == base_id]
        lookup = _lookup(base_rows)
        canvas = Image.new(
            "L", (len(strengths) * cell_size, len(axes) * (cell_size + label_height)), 128
        )
        draw = ImageDraw.Draw(canvas)
        for row_index, axis in enumerate(axes):
            y_offset = row_index * (cell_size + label_height)
            draw.text((4, y_offset + 5), axis, font=font, fill=255)
            for column, strength in enumerate(strengths):
                x_offset = column * cell_size
                draw.text(
                    (x_offset + cell_size - 28, y_offset + 5),
                    f"{strength:+d}",
                    font=font,
                    fill=255,
                )
                entry = lookup.get((axis, strength))
                if entry is None:
                    continue
                with Image.open(root / entry["png_path"]) as image:
                    thumb = image.convert("L").resize(
                        (cell_size, cell_size), Image.Resampling.LANCZOS
                    )
                canvas.paste(thumb, (x_offset, y_offset + label_height))
        montage_path = output_path / f"{base_id}-cue-grid.png"
        canvas.save(montage_path, compress_level=9)
        montage_paths.append(str(montage_path))

    baseline_rows = [row for row in rows if row["cue_axis"] == "baseline"]
    columns = 4
    rows_count = (len(baseline_rows) + columns - 1) // columns
    overview = Image.new("L", (columns * cell_size, rows_count * (cell_size + label_height)), 128)
    overview_draw = ImageDraw.Draw(overview)
    for index, entry in enumerate(sorted(baseline_rows, key=lambda row: row["base_id"])):
        column = index % columns
        row_index = index // columns
        x_offset = column * cell_size
        y_offset = row_index * (cell_size + label_height)
        overview_draw.text((x_offset + 4, y_offset + 5), entry["base_id"], font=font, fill=255)
        with Image.open(root / entry["png_path"]) as image:
            thumb = image.convert("L").resize((cell_size, cell_size), Image.Resampling.LANCZOS)
        overview.paste(thumb, (x_offset, y_offset + label_height))
    overview_path = output_path / "all-baselines.png"
    overview.save(overview_path, compress_level=9)
    return {
        "output": str(output_path),
        "base_montages": montage_paths,
        "baseline_overview": str(overview_path),
    }


def _create_factorial_montages(
    root: Path,
    output_path: Path,
    rows: list[dict[str, Any]],
    cell_size: int,
) -> dict[str, Any]:
    font = ImageFont.load_default()
    left_label_width = 230
    header_height = 34
    tag_height = 18
    base_ids = sorted({str(row["base_id"]) for row in rows})
    montage_paths: list[str] = []
    for base_id in base_ids:
        base_rows = [row for row in rows if str(row["base_id"]) == base_id]
        design_profile = "v1" if "content" in base_rows[0] else "v2"
        directional_keys: list[tuple[str, ...]] = []
        for spec in combination_specs_for_source(base_id, design_profile=design_profile):
            key = (
                (str(spec.content), spec.outline, spec.shading, spec.material)
                if design_profile == "v1"
                else (spec.outline, spec.shading, spec.material)
            )
            if key not in directional_keys:
                directional_keys.append(key)
        if design_profile == "v1":
            lookup = {
                (
                    str(row["content"]),
                    str(row["outline"]),
                    str(row["shading"]),
                    str(row["material"]),
                    str(row["polarity"]),
                ): row
                for row in base_rows
            }
        else:
            lookup = {
                (
                    str(row["outline"]),
                    str(row["shading"]),
                    str(row["material"]),
                    str(row["polarity"]),
                ): row
                for row in base_rows
            }
        width = left_label_width + len(POLARITY_STATES) * cell_size
        height = header_height + len(directional_keys) * (cell_size + tag_height)
        canvas = Image.new("L", (width, height), 150)
        draw = ImageDraw.Draw(canvas)
        draw.text((6, 10), base_id, font=font, fill=248)
        for column, polarity in enumerate(POLARITY_STATES):
            x = left_label_width + column * cell_size
            draw.text(
                (x + 4, 10),
                polarity.replace("outer-", "o:").replace("_center-", "/c:"),
                font=font,
                fill=248,
            )
        for row_index, key in enumerate(directional_keys):
            if design_profile == "v1":
                content, outline, shading, material = key
                label = f"c:{content}  o:{outline}  s:{shading}  m:{material}"
            else:
                outline, shading, material = key
                label = f"o:{outline}  s:{shading}  m:{material}"
            y = header_height + row_index * (cell_size + tag_height)
            draw.text((6, y + 5), label, font=font, fill=248)
            for column, polarity in enumerate(POLARITY_STATES):
                entry = lookup[(*key, polarity)]
                x = left_label_width + column * cell_size
                draw.text((x + 4, y + 5), str(entry["design_tag"]), font=font, fill=248)
                with Image.open(root / str(entry["png_path"])) as image:
                    thumb = image.convert("L").resize(
                        (cell_size, cell_size),
                        Image.Resampling.LANCZOS,
                    )
                canvas.paste(thumb, (x, y + tag_height))
        montage_path = output_path / f"{base_id}-factorial-grid.png"
        canvas.save(montage_path, compress_level=9)
        montage_paths.append(str(montage_path))

    neutral_rows = [
        row
        for row in rows
        if ("content" not in row or row["content"] == "ambiguous")
        and row["outline"] == "ambiguous"
        and row["shading"] == "none"
        and row["material"] == "ambiguous"
        and row["polarity"] == "outer-black_center-white"
    ]
    overview = Image.new("L", (len(neutral_rows) * cell_size, cell_size + tag_height), 150)
    overview_draw = ImageDraw.Draw(overview)
    for index, entry in enumerate(sorted(neutral_rows, key=lambda row: row["base_id"])):
        x = index * cell_size
        overview_draw.text((x + 4, 5), str(entry["base_id"]), font=font, fill=248)
        with Image.open(root / str(entry["png_path"])) as image:
            thumb = image.convert("L").resize(
                (cell_size, cell_size),
                Image.Resampling.LANCZOS,
            )
        overview.paste(thumb, (x, tag_height))
    overview_path = output_path / "all-neutral-bases.png"
    overview.save(overview_path, compress_level=9)
    return {
        "output": str(output_path),
        "base_montages": montage_paths,
        "baseline_overview": str(overview_path),
    }
