# Rubin Cue Stimuli

Deterministic, experiment-oriented Rubin profile/central-figure stimuli built from
licensed SVG source masters. The project preserves the downloaded vectors verbatim and
creates normalized derivatives; it does not crop figures from the papers or invent new
face contours.

## Quick start

```powershell
uv sync --extra dev
uv run pytest
uv run ruff check .
uv run rubin-cues combinations --config configs\v2.toml --output tmp\combination-audit-v2
uv run rubin-cues outline-proof --config configs\v1.toml --output tmp\outline-face-proof
uv run rubin-cues generate --config configs\v2.toml
uv run rubin-cues validate --manifest stimuli\v2\manifest.jsonl
uv run rubin-cues montage --manifest stimuli\v2\manifest.jsonl
```

The source registry retains six licensed face-vase SVG masters, and the formal bank uses
the four accepted profile-compatible sources. Each enabled source contour is crossed with
six ordered black/gray/white polarity mappings without hand-drawing faces.
Four files are CC0; two Wikimedia families are CC BY-SA 3.0 and remain separately
attributed. See
`assets/source/PROVENANCE.md` for exact URLs, licenses, and hashes.

The published v1 factorial design has content (`face/ambiguous/vase`), outline
(`ambiguous/face`), hard shading (`none/figure`), vase material (`ambiguous/vase`), and
six polarity mappings. Its four enabled sources use 96 valid conditions each, for 384
images under schema v7.

The v2 design removes the content axis and every condition containing opposing face- and
vase-directed cues. It retains outline, hard shading, vase material, and all six polarity
mappings. Five non-conflicting directional states produce 30 conditions per source and
120 images under schema v8. V2 manifests, IDs, SVG metadata, and filenames contain no
content or conflict fields. Across both banks, active figure shading never appears with
vase material relief. `oc-276846-profile` and `oc-276861-full-faces` remain excluded as
complete stimulus families; their immutable masters remain only for provenance.

The versioned banks are frozen under `stimuli/v1` and `stimuli/v2`; rendering-rule changes
require a new version or a full regeneration, manifest validation, and hash reproducibility
check. Experiment delivery targets NIMH MonkeyLogic, not PsychoPy. Stimulus files never
contain a baked-in fixation mark; MonkeyLogic may draw fixation dynamically and must
record that choice.

V1 audits and manifests assign `face`, `ambiguous`, `vase`, or `conflict`; v2 assigns only
`face`, `ambiguous`, or `vase`. Polarity remains a neutral control. An active
shadow follows the current figure and uses the third black/gray/white value not already
assigned to the figure and background. Its deterministic offset varies by stimulus; both
absolute displacement components exceed 0.020 canvas units and the total radius is at
most 0.065 canvas units.

See `docs/protocol.md`, `docs/data-dictionary.md`, `docs/literature.md`, and
`assets/source/PROVENANCE.md` for the current design and provenance details.
