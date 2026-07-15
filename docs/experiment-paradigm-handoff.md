# Experiment Paradigm Design Handoff

Status: stimulus bank complete; experiment paradigm not yet designed or production-ready  
Last verified: 2026-07-14  
Audience: the next Codex session taking over experimental design and MonkeyLogic delivery

## 1. Handoff objective

Design an experimentally defensible workflow for measuring how cues applied to Rubin
face-vase stimuli bias perceptual interpretation and, if required, perceptual stability.
The next session should begin with design and clarification, not by modifying the frozen
stimulus bank.

The publication figures are the mechanistic and visual reference. They are not permission
to collapse the library to a few paper panels, nor a requirement to copy paper bitmaps into
the bank. Independent cue variants and factorial exploration remain intentional, but the
core cue logic must have a defensible relationship to the cited work.

## 2. Collaboration instructions from the user

- Do not interpret every question as an instruction to delete, revert, or redraw.
- When the user asks about an element, first explain what it is, why it exists, whether it
  comes from a paper or from this project, and what effect it may have.
- Change the design only after an explicit request such as “删掉”, “改掉”, or “重做”. If
  intent is unclear, restate the interpretation in one sentence and wait for confirmation.
- Exclude queen and other non-vase central-figure variants.
- Use the Edge Chrome extension for web work, not the application’s built-in browser.
- Prefer the local paper PDFs when checking the original figures:
  - `G:\Zotero\storage\65AXVJ36\Wang 等 - 2013 - Brain mechanisms for simple perception and bistable perception.pdf`
  - `G:\Zotero\storage\XEUUKZX6\Hardstone 等 - 2022 - Frequency-specific neural signatures of perceptual content and perceptual stability.pdf`
- The experiment runner must target NIMH MonkeyLogic. Do not introduce PsychoPy.

## 3. Frozen v1 stimulus-bank contract

The formal bank is under `stimuli/v1` and should be treated as immutable input while the
paradigm is being designed. Changing rendering rules requires explicit user approval, a
full regeneration, validation, montage review, and reproducibility comparison.

### 3.1 Size and sources

- 4 enabled source contours, each with 96 valid conditions: 384 stimuli total.
- 384 grayscale 1024×1024 PNG files, 384 SVG derivatives, and 4 phase-scrambled masks.
- Enabled sources:
  - `wm-cc0-classic`
  - `wm-bysa-classic`
  - `wm-bysa-klam`
  - `oc-274578-heads`
- `oc-276846-profile` and `oc-276861-full-faces` are retained for provenance but excluded
  as complete families.
- Downloaded masters under `assets/source/` are immutable. Exact creators, licenses, URLs,
  and hashes are in `assets/source/PROVENANCE.md`.

### 3.2 Factor definitions

| Factor | Values | Directional interpretation |
| --- | --- | --- |
| `content` | `face`, `ambiguous`, `vase` | Face-region lightness difference, neutral, or matched stripes favoring vase organization |
| `outline` | `ambiguous`, `face` | Original shared-boundary organization or side profiles closed against the frame |
| `shading` | `none`, `figure` | No shadow or a hard translated copy of the current figure behind it |
| `material` | `ambiguous`, `vase` | Flat central region or deterministic Lambertian vase relief |
| `polarity` | six ordered pairs | Every ordered pair of distinct black, gray, and white; intended as a neutral control |

The bank deliberately has no graded cue strengths and no geometry dimension. Material has
only neutral and vase-relief states; the rejected face-relief version must not be restored.

`shading=figure` means a displaced copy of the currently assigned figure, not a glossy
highlight and not the material-relief cue. With `outline=ambiguous`, the figure is the
central vase; with `outline=face`, the two side profiles are figures. The shadow uses the
third black/gray/white value not already assigned to figure and background. Horizontal and
vertical displacement magnitudes each exceed 0.020 canvas units (20.48 px at 1024), total
radius is at most 0.065, and the offset varies deterministically by stimulus.

The Klam family has a source-specific derived face-outline closure at normalized `y=0.18`.
This does not alter its downloaded SVG master.

### 3.3 Structural exclusions and labels

- `shading=figure` cannot co-occur with `material=vase`.
- `shading=figure` cannot co-occur with `content=face`.
- The result is a constrained, non-orthogonal factorial library rather than a complete
  Cartesian product.
- Any condition containing both face-directed and vase-directed cues is tagged `conflict`.
  There is no majority vote among cues.
- `design_tag` is a design prediction (`face`, `ambiguous`, `vase`, or `conflict`), not an
  observed perceptual response and not proof that the stimulus has the intended effect.
- `conflict` is not a fourth behavioral response. Participant/animal states remain to be
  defined by the paradigm; the old human-oriented proposal used face/vase/unsure.

Current tag totals are:

- `face`: 96
- `ambiguous`: 24
- `vase`: 120
- `conflict`: 144

## 4. Verified artifacts and entry points

Use these as the source of truth:

- `stimuli/v1/manifest.csv`: Excel-facing UTF-8 BOM manifest.
- `stimuli/v1/manifest.jsonl`: machine-readable manifest.
- `stimuli/v1/generation.json`: schema version, source IDs, counts, quality settings, and
  shadow bounds.
- `stimuli/v1/png/` and `stimuli/v1/svg/`: experimental images and vector derivatives.
- `stimuli/v1/masks/` and `stimuli/v1/masks.json`: per-source masks and hashes.
- `stimuli/v1/montages/`: visual QC grids for every source.
- `configs/v1.toml`: rendering values and provisional timing values.
- `docs/protocol.md`: current stimulus and provisional task description.
- `docs/data-dictionary.md`: current manifest fields.
- `docs/literature.md`: paper references and scope of claims.
- `assets/source/PROVENANCE.md`: immutable-master provenance.

Last completed verification:

- 384 stimuli and 4 masks validated with no errors.
- Ruff passed and 49 tests passed.
- A second complete 1024×1024 generation matched all 384 PNG hashes, all 384 SVG hashes,
  and all 4 mask hashes; the temporary reproduction directory was removed afterward.
- Each source has 24 active-shading conditions and 24 distinct offsets; every horizontal
  and vertical component clears the configured threshold.

Validation command:

```powershell
& ..\.agents\scripts\Invoke-WorkspaceValidation.ps1 `
  -Path . `
  -Profile ..\.agents\validation\rubin-cue-stimuli.psd1 `
  -Tier ship `
  -Run `
  -AsJson
```

## 5. What is not ready

### 5.1 No MonkeyLogic runner exists

There are currently no MATLAB/MonkeyLogic task files, condition files, event-code tables,
eye-window definitions, response-device mappings, reward rules, or hardware smoke tests.
The repository must not claim production readiness.

### 5.2 The scheduling and summary modules are legacy

`src/rubin_cues/schedule.py` and `src/rubin_cues/summarize.py` still implement the obsolete
12-base, seven-level cue-axis model (`baseline`, signed strengths `-3…+3`, and combined
endpoints). Their tests use synthetic legacy manifests. The current schema-v7 factorial
manifest instead has categorical fields such as `content`, `outline`, `shading`,
`material`, `polarity`, and `design_tag`; it has no `cue_axis`, `signed_strength`, or
`target_percept` columns.

Therefore:

- Do not run the existing `schedule --mode short|continuous` commands against the formal
  v1 manifest.
- Do not interpret the passing legacy schedule/summary tests as evidence of v1 task
  compatibility.
- `configs/v1.toml` still contains `selected_base_count = 8`, which is inherited from the
  obsolete 12-base plan and is impossible with the current four source IDs.
- Redesign the condition-table and response schemas only after the scientific paradigm is
  approved.

### 5.3 Existing timing values are provisional

The current config contains literature-derived placeholders: 1.0–1.8 s fixation, 150 ms
stimulus, 200 ms mask for a brief initial-percept task, plus 2 s fixation and 30 s stimulus
for a continuous stability task. These are not a final MonkeyLogic protocol. The proposed
16.9° × 17.6° visual angle is also not production-ready without monitor geometry, viewing
distance, resolution, refresh rate, and measured frame timing.

### 5.4 Paper-anchor equivalence is not yet an automated acceptance test

The user previously specified that the independently generated library should contain
three stimuli equivalent to the three relevant paper examples as a validation of the
generation method. The current project does not copy paper-image bytes into the manifest,
which is correct, but it also does not yet contain an automated or documented comparison
showing which three generated IDs satisfy that criterion. Do not claim exact paper-anchor
equivalence until the three target panels and the acceptable equivalence rule have been
agreed and checked.

## 6. Questions the next session must resolve first

Ask these before writing a task runner or fixing trial counts:

1. Are the observers human participants, non-human primates, or both?
2. What is the primary endpoint: first percept, forced-choice accuracy, perceptual
   dominance/reversal dynamics, or a neural signature of content/stability?
3. Is the study behavioral-only, or synchronized with eye tracking, EEG/MEG, ECoG, LFP,
   spikes, imaging, or another recording system?
4. How will face/vase/uncertain states be reported: buttons, lever, joystick, gaze target,
   delayed probe, continuous hold, or no-report proxy?
5. Is fixation required during stimulus presentation, and what eye-window/break policy is
   appropriate?
6. What is the maximum trials and duration per session, and how many sessions/repetitions
   are realistic?
7. Is calibration within observer, across observers, or a separate pilot cohort?
8. Is the full 384-image bank a screening library, or must every condition enter the main
   experiment? How should `conflict` trials be used?
9. Should polarity be modeled as a six-level factor, counterbalanced nuisance, or reduced
   after a luminance-control pilot?
10. What MonkeyLogic version, MATLAB version, display hardware, response hardware, eye
    tracker, and digital/analog event interfaces are available?

## 7. Recommended design workflow

### Stage A: write and approve the paradigm specification

Create `docs/experiment-paradigm.md` before implementing MonkeyLogic code. It should state:

- scientific questions and falsifiable hypotheses;
- observer population and recording modality;
- estimable factorial contrasts despite structural exclusions;
- the role of baseline, directional, polarity, and conflict conditions;
- calibration versus main-task phases;
- trial timeline and response semantics;
- repetitions, blocks, sessions, randomization, and counterbalancing;
- exclusion criteria and missing/unsure handling;
- planned dependent variables and analysis model;
- MonkeyLogic event codes, trial errors, fixation policy, and recovery behavior;
- pilot gates and production display requirements.

Do not implement the runner until the user approves this design document.

### Stage B: behavioral/pilot validation

The generated `design_tag` values must be tested empirically. At minimum, estimate
P(face), P(vase), and any unsure/no-response rate by stimulus or pre-specified condition
group. Verify that intended face/vase cues produce directional effects and that ambiguous
conditions are sufficiently bistable for the chosen observer population.

The bank is structurally unbalanced, and shading changes direction with outline. Avoid a
naive fully crossed ANOVA or interpreting a single unconditional “shading main effect”.
Pre-specify estimable contrasts or use an appropriate categorical/mixed-effects model with
observer and source contour accounted for. Treat `conflict` as a designed predictor class,
not as an observed percept.

### Stage C: MonkeyLogic implementation

After approval, derive a new condition table from `manifest.jsonl` without renaming or
copying stimulus IDs. The runtime should log at least:

- participant/animal, session, block, trial, and randomization seed;
- `stimulus_id`, source and all five factor values;
- requested and actual frame counts/timestamps;
- fixation acquisition, hold, break, and trial-error codes;
- response state, response time, and response-device code;
- mask onset/offset if used;
- fixation-during-stimulus policy;
- display calibration ID and stimulus size;
- neural/eye-tracker event codes and synchronization timestamps when applicable.

Stimulus PNG/SVG files must remain free of baked-in fixation. MonkeyLogic may draw fixation
dynamically and must record whether it remains visible during the stimulus.

### Stage D: smoke and production gates

Run, in order:

1. offline condition-table completeness and deterministic randomization tests;
2. MonkeyLogic syntax/load test;
3. a short hardware-free or simulated-input run where supported;
4. display timing, dropped-frame, key/lever/gaze mapping, abort/recovery, and CSV/BHV2
   logging checks;
5. eye-tracker and neural-trigger loopback checks if applicable;
6. a small behavioral pilot before freezing the production schedule.

Do not install software or change host/MATLAB/MonkeyLogic configuration without first
listing the exact path, effect, and rollback method and obtaining approval.

## 8. Acceptance criteria for the next handoff

The experimental-design session is complete only when:

- the user has approved `docs/experiment-paradigm.md`;
- the observer population, response method, primary endpoint, trial load, and recording
  modality are explicit;
- all selected conditions and exclusions can be derived reproducibly from schema-v7
  manifest fields;
- design-tag predictions are clearly separated from measured percepts;
- the constrained factorial structure and estimable contrasts are documented;
- the MonkeyLogic condition/response/event schemas are specified;
- provisional timings and display values are either approved or clearly marked pending;
- no claim of production readiness is made before a real MonkeyLogic smoke test.

## 9. Suggested opening message for the next session

> 我已读完 `docs/experiment-paradigm-handoff.md`。我会先设计并请你确认实验范式，不修改冻结的 384 张刺激，也不会沿用旧的 `-3…+3` schedule。开始前我需要确认：被试是人还是猴、主要因变量是首次知觉还是持续翻转、记录模态与响应装置是什么，以及单次 session 可接受的 trial 数和时长。

