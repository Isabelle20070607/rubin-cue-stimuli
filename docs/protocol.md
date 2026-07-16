# Protocol

## Stimulus bank

Six immutable online SVG masters are retained, and four accepted profile-compatible
masters supply the formal shared contours. The original path data remains unchanged in
`assets/source/`; every derived SVG and PNG records the source ID, license, and SHA-256.

Both formal banks use the four accepted profile-compatible sources. OpenClipart
276846/276861 remain in the immutable source registry for provenance, but their complete
stimulus families are excluded. Neither bank has graded cue strengths.

V1 schema v7 contains 3 content states, 2 outline states, 2 shading states, 2 material
states, and 6 ordered polarity mappings. Active figure shading cannot co-occur with either
vase material relief or `content=face`. This yields 96 conditions per source and 384
stimuli overall.

V2 schema v8 removes the content axis and excludes every combination containing both a
face-directed and a vase-directed cue. It retains 2 outline states, 2 shading states, 2
material states, and the same 6 polarity mappings. After the shading/material exclusion
and conflict filtering, five directional states remain: 30 conditions per source and 120
stimuli overall.

V2 reduces the material-lighting span for black and gray while retaining the selected
white material range. The texture ranges are black `20-58`, gray `103-186`, and white
`132-244`. With `crispEdges` eliminating antialiased patch seams, the final texture means
across all enabled sources and relevant polarities at 1024 px are 43.3397, 153.8391, and
200.6372. The matching flat means are 43.1419, 153.9663, and 200.8915 from the
black/gray/white palette `43/154/201`; every aggregate mismatch is below 0.26 gray level.
V1 retains its original palette and material rendering.

- `content=face` breaks lightness homogeneity between the two profile regions;
  `content=vase` gives both profile regions the same horizontal stripe structure.
- `outline=face` closes the two side profiles against the frame; `outline=ambiguous`
  retains the original Rubin organization and shared boundary. Both states are available
  for all four enabled profile-compatible sources.
- `shading=figure` places a translated copy of the current figure behind it as a hard
  shadow. With an ambiguous outline the figure is the central vase; with a face outline
  the two profile regions are the figures. The shadow uses the third black/gray/white
  value not used by figure and background. Displacement varies deterministically by
  stimulus and is recorded in the manifest. At 1024 px, the absolute horizontal and
  vertical components each exceed 20.48 px (0.020 canvas units), while total radius is at
  most 66.56 px (0.065 canvas units). Active shading cannot be combined with
  `content=face` or `material=vase`.
- `material=vase` adds a deterministic Lambertian surface field to the central vase;
  `material=ambiguous` leaves it flat. `material=vase` cannot be combined with active
  figure shading.
- `polarity` is a six-level neutral control containing every ordered pair of distinct
  black, gray, and white values.

Conditions containing at least one face-directed and one vase-directed cue are tagged
`conflict`, regardless of cue count. `conflict` is a design class, not a fourth behavioral
response and not a claim of equal face/vase probability. This rule describes v1; v2 does
not generate those conditions and has no conflict field or tag.

## Optional brief backward-masking calibration

The full factorial bank is a stimulus library; a presentation subset must be chosen before
participant scheduling. The generated phase-scrambled masks are retained only for an
explicitly approved backward-masking block; the default v2 experiment does not present
them. If such a human calibration block is approved, a brief trial may contain a 1.0-1.8 s
fixation interval, 150 ms stimulus, 200 ms mask, then a face/vase/unsure response. This
timing is a separate paradigm choice, not an implication of the files under `masks/`.

The fixation marker is drawn by MonkeyLogic and is absent from the stimulus files. The
default is not to overlay fixation during stimulus presentation.

Behavioral calibration estimates P(face), P(vase), and unsure rate for each selected
condition. Design tags are retained as predictors and are never substituted for measured
perception.

## Provisional continuous stability follow-up

For each selected primary base use the ambiguous baseline plus its selected face- and
vase-directed levels. Repetition count and session split are set in the schedule rather
than inferred from obsolete cue-axis counts. Each trial uses 2 s fixation, 30 s stimulus
presentation, and a 3-7 s inter-trial interval. Participants report face, vase, or unsure
initially and whenever their percept changes.

## Production display gate

The intended stimulus size is 16.9 degrees high by 17.6 degrees wide. Production mode must
refuse to start if monitor width, distance, resolution, refresh rate, or monitor name remain
placeholders. Durations are converted to whole frames using the measured refresh rate and
actual frame counts are recorded. The production runner targets NIMH MonkeyLogic; no
PsychoPy runtime is part of this project. Until the MonkeyLogic smoke test is complete,
the repository must not claim production-run readiness.
