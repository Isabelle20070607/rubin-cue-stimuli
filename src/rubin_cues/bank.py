from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from PIL import Image

from .combinations import combination_specs
from .config import Config
from .factorial_render import rasterize_factorial_svg, render_factorial_svg
from .source_geometry import source_bases


def _write_png(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", compress_level=9, optimize=False)


def generate_bank(
    config: Config,
    output: str | Path | None = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    project_root = config.path.parent
    output_path = (
        Path(output).expanduser().resolve()
        if output is not None
        else (project_root / "images").resolve()
    )
    if output_path.exists() and any(output_path.iterdir()):
        if not overwrite:
            raise FileExistsError(f"Output is not empty: {output_path}; pass --overwrite")
        if output_path == project_root or project_root not in output_path.parents:
            raise ValueError(f"Refusing to overwrite unsafe output path: {output_path}")
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    specs = combination_specs()
    bases = source_bases(project_root)
    for base in bases:
        for spec in specs:
            filename = f"{base.source.source_id}__{spec.compact_id}.png"
            svg = render_factorial_svg(config, base, spec)
            _write_png(output_path / filename, rasterize_factorial_svg(svg))

    return {
        "ok": True,
        "output": str(output_path),
        "source_count": len(bases),
        "image_count": len(bases) * len(specs),
    }
