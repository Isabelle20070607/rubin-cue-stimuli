# Rubin Cue Stimuli

This repository contains 120 grayscale Rubin face-vase stimuli in `images/` and the
generator used to create them from four licensed source SVGs. The image set crosses four
source contours with 30 non-conflicting combinations of outline, shading, material, and
black/gray/white polarity. No fixation mark is baked into the images.

## Generate the images

```powershell
uv sync --extra dev
uv run rubin-cues --config config.toml --overwrite
```

The command writes the complete image set to `images/`. Use `--output <directory>` to
generate a candidate set elsewhere while adjusting a new source.

To add a source SVG, place it under `assets/source/` and add its source details and crop
box to `SOURCE_ASSETS` in `src/rubin_cues/source_assets.py`. Then add the source and license
information to `assets/source/PROVENANCE.md` and generate into a temporary directory for
visual review before replacing `images/`.

## File names

Files use this pattern:

```text
<source>__o{a|f}-s{n|f}-m{a|v}-p{outer}{center}.png
```

- `o`: ambiguous or face outline
- `s`: no shading or figure shading
- `m`: ambiguous or vase material
- `p`: ordered outer and center colors (`b`, `g`, or `w`)

Conditions that combine face-directed and vase-directed cues are omitted. Source and
license details are listed in `assets/source/PROVENANCE.md`.
