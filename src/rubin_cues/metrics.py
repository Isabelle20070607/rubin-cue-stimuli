from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np


def match_moments(image: np.ndarray, target_mean: float, target_std: float) -> np.ndarray:
    work = image.astype(np.float64)
    current_std = float(work.std())
    if current_std < 1e-9:
        raise ValueError("cannot normalize a constant image")
    work = (work - work.mean()) * (target_std / current_std) + target_mean
    work = np.clip(work, 0.0, 255.0)
    for _ in range(2):
        current_std = float(work.std())
        if current_std < 1e-9:
            break
        work = (work - work.mean()) * (target_std / current_std) + target_mean
        work = np.clip(work, 0.0, 255.0)
    return np.rint(work).astype(np.uint8)


def image_metrics(image: np.ndarray) -> dict[str, float]:
    work = image.astype(np.float64) / 255.0
    mean = float(work.mean())
    std = float(work.std())
    horizontal = np.abs(np.diff(work, axis=1)).mean()
    vertical = np.abs(np.diff(work, axis=0)).mean()
    return {
        "mean_luminance": mean,
        "rms_contrast": 0.0 if mean == 0 else std / mean,
        "edge_energy": float((horizontal + vertical) / 2.0),
    }


def sha256_path(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
