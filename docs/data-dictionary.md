# Data dictionary

## Stimulus manifest

- `stimulus_id`: source ID plus compact factorial condition ID.
- `base_id`: one of the four enabled profile-compatible source-vector IDs.
- `source_id`, `source_sha256`, `source_license`: immutable SVG provenance.
- `combination_id`, `compact_id`: verbose audit key and filesystem-safe condition key.
- V1 schema v7 stores `content`, `outline`, `shading`, `material`, and `polarity`; v2
  schema v8 omits `content` and stores the remaining four factorial parameters.
- `design_tag`: v1 permits `face`, `ambiguous`, `vase`, or `conflict`; v2 permits only
  `face`, `ambiguous`, or `vase`.
- `face_cues`, `vase_cues`: directional-cue audit fields. V1 also stores `is_conflict`;
  v2 omits it because conflicting combinations are not generated.
- `figure_region`, `figure_color`, `background_color`, `third_color`, `shade_color`:
  palette-aware composition fields.
- `shadow_dx`, `shadow_dy`, `shadow_seed`, `shadow_pair_mirrored`: deterministic hard
  shadow provenance; active offsets vary by stimulus and clear the configured absolute
  component threshold, while inactive shadows store zero displacement.
- `seed`, `config_version`, `params_json`: generation provenance.
- V2 `generation.json` additionally records `palette_values` and
  `material_value_ranges`, plus `material_shape_rendering=crispEdges`; the palette and
  ranges also appear in row provenance where applicable.
- `png_path`, `svg_path`, `file_sha256`, `svg_sha256`: frozen artifact identity.
- `mean_luminance`, `rms_contrast`, `edge_energy`: PNG image metrics.
- `center_area_ratio`, `path_length`, `convexity_proxy`: geometry metrics.
- `masks.json` and `masks/*.png`: deterministic optional backward-masking assets, not
  members of the default v2 presentation schedule.

## Pre-render combination audit

`rubin-cues combinations --config configs/v1.toml` enumerates the v1 96-condition
parameter space. `--config configs/v2.toml` enumerates the v2 30-condition space without
content or conflict fields. OpenClipart 276846/276861 are excluded from the formal render.

- `design_tag`: v1 uses `face`, `ambiguous`, `vase`, or `conflict`; v2 uses the first
  three values only.
- `face_cues`, `vase_cues`: active directional cue axes, separated by `|` in CSV.
- `is_conflict` (v1 only): true whenever at least one face-directed cue and at least one
  vase-directed cue are simultaneously active. Cue counts do not resolve a conflict.
- `figure_region`: `vase` for an ambiguous outline and `face` for the face outline.
- `figure_color`, `background_color`: the two colors selected by `polarity` after
  accounting for which region is the figure.
- `shade_color`: blank when shading is `none`; otherwise the unused third member of
  black/gray/white. Shading follows the current figure, so it is vase-directed for an
  ambiguous outline and face-directed for the face outline.

In v1, `conflict` is a design class, not a participant response and not evidence of a
50/50 percept. V2 excludes those rows. `polarity` does not determine the design tag, but
it does determine the three colors used for figure, background, and an active shadow. The
approved experiment paradigm must define the behavioral response vocabulary independently.

## Proposed schedules (not implemented for schemas v7/v8)

The replacement schema should include participant/animal, session, block, trial, stimulus
ID/path, response mapping, requested durations, fixation-overlay policy, randomization
seed, and visual angle. A mask path is included only for an explicitly approved
backward-masking block. The current scheduling module targets the obsolete graded-axis
manifest and must not be used with the formal factorial bank.

## Proposed responses (not implemented for schemas v7/v8)

Brief-task rows should store stimulus onset, actual stimulus frames, dropped-frame count,
response, RT, response mapping, and display configuration ID. Mask frames are recorded
only when an approved block uses them. If the approved paradigm uses continuous reports,
event rows should add event index, percept state, event time, and stimulus duration. Final
fields depend on the MonkeyLogic paradigm and recording hardware defined in
`experiment-paradigm.md`.
