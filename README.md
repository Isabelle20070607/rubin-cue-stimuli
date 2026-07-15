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
uv run rubin-cues combinations --output tmp\combination-audit
uv run rubin-cues outline-proof --config configs\v1.toml --output tmp\outline-face-proof
uv run rubin-cues generate --config configs\v1.toml
uv run rubin-cues validate --manifest stimuli\v1\manifest.jsonl
uv run rubin-cues montage --manifest stimuli\v1\manifest.jsonl
```

The source registry retains six licensed face-vase SVG masters, and the formal bank uses
the four accepted profile-compatible sources. Each enabled source contour is crossed with
six ordered black/gray/white polarity mappings without hand-drawing faces.
Four files are CC0; two Wikimedia families are CC BY-SA 3.0 and remain separately
attributed. See
`assets/source/PROVENANCE.md` for exact URLs, licenses, and hashes.

The factorial design has content (`face/ambiguous/vase`), outline
(`ambiguous/face`), hard shading (`none/figure`), vase material
(`ambiguous/vase`), and six polarity mappings. It deliberately has no graded strengths.
The four enabled sources use 96 valid conditions each, so the bank contains 384 images.
Hard figure shading never appears with either vase material relief or the
different-colored-face content cue. `oc-276846-profile` and `oc-276861-full-faces` are
excluded as complete stimulus
families; their immutable masters remain only for provenance. Non-vase central figures
and queen variants are also excluded.

The current v1 bank is frozen under `stimuli/v1`; rendering-rule changes require a full
regeneration, manifest validation, and hash reproducibility check. Experiment delivery
targets NIMH MonkeyLogic, not PsychoPy. Stimulus files never contain a baked-in fixation
mark; MonkeyLogic may draw fixation dynamically and must record that choice.

The combination audit and manifest assign `face`, `ambiguous`,
`vase`, or `conflict`. Any mixture of face- and vase-directed cues is `conflict`; it is
never relabeled by majority vote, and polarity remains a neutral control. An active
shadow follows the current figure and uses the third black/gray/white value not already
assigned to the figure and background. Its deterministic offset varies by stimulus; both
absolute displacement components exceed 0.020 canvas units and the total radius is at
most 0.065 canvas units.

See `docs/protocol.md`, `docs/data-dictionary.md`, `docs/literature.md`, and
`assets/source/PROVENANCE.md` for the current design and provenance details.
