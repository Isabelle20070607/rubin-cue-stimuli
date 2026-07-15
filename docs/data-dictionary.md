# Data dictionary

## Stimulus manifest

- `stimulus_id`: source ID plus compact factorial condition ID.
- `base_id`: one of the four enabled profile-compatible source-vector IDs.
- `source_id`, `source_sha256`, `source_license`: immutable SVG provenance.
- `combination_id`, `compact_id`: verbose audit key and filesystem-safe condition key.
- `content`, `outline`, `shading`, `material`, `polarity`: factorial parameter states.
- `design_tag`: `face`, `ambiguous`, `vase`, or `conflict`.
- `face_cues`, `vase_cues`, `is_conflict`: directional-cue audit fields.
- `figure_region`, `figure_color`, `background_color`, `third_color`, `shade_color`:
  palette-aware composition fields.
- `shadow_dx`, `shadow_dy`, `shadow_seed`, `shadow_pair_mirrored`: deterministic hard
  shadow provenance; active offsets vary by stimulus and clear the configured absolute
  component threshold, while inactive shadows store zero displacement.
- `seed`, `config_version`, `params_json`: generation provenance.
- `png_path`, `svg_path`, `file_sha256`, `svg_sha256`: frozen artifact identity.
- `mean_luminance`, `rms_contrast`, `edge_energy`: PNG image metrics.
- `center_area_ratio`, `path_length`, `convexity_proxy`: geometry metrics.

## Pre-render combination audit

`rubin-cues combinations` enumerates the 96-condition parameter space used by each of the
four enabled profile-compatible sources. OpenClipart 276846/276861 are excluded from the
formal render. `shading=figure` is mutually exclusive with both `material=vase` and
`content=face`. Each audit row records
`content`, `outline`, `shading`, `material`, and the neutral `polarity` control.

- `design_tag`: `face`, `ambiguous`, `vase`, or `conflict`.
- `face_cues`, `vase_cues`: active directional cue axes, separated by `|` in CSV.
- `is_conflict`: true whenever at least one face-directed cue and at least one
  vase-directed cue are simultaneously active. Cue counts do not resolve a conflict.
- `figure_region`: `vase` for an ambiguous outline and `face` for the face outline.
- `figure_color`, `background_color`: the two colors selected by `polarity` after
  accounting for which region is the figure.
- `shade_color`: blank when shading is `none`; otherwise the unused third member of
  black/gray/white. Shading follows the current figure, so it is vase-directed for an
  ambiguous outline and face-directed for the face outline.

`conflict` is a design class, not a participant response and not evidence of a 50/50
percept. `polarity` does not determine the design tag, but it does determine the three
colors used for figure, background, and an active shadow. The approved experiment paradigm
must define the behavioral response vocabulary independently.

## Proposed schedules (not implemented for schema v7)

The replacement schema should include participant/animal, session, block, trial, stimulus
ID/path, mask path, response mapping, requested durations, fixation-overlay policy,
randomization seed, and visual angle. The current scheduling module targets the obsolete
graded-axis manifest and must not be used with the formal factorial bank.

## Proposed responses (not implemented for schema v7)

Brief-task rows should store stimulus onset, actual stimulus/mask frames, dropped-frame
count, response, RT, response mapping, and display configuration ID. If the approved
paradigm uses continuous reports, event rows should add event index, percept state, event
time, and stimulus duration. Final fields depend on the MonkeyLogic paradigm and recording
hardware defined in `experiment-paradigm.md`.
