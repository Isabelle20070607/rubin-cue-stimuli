# Rubin Cue-Transition Experiment Paradigm

Status: proposed v0.1 for scientific review; not production-ready  
Primary observer: macaque  
Primary recording: spikes and LFP from object-selective visual cortex, with eye tracking  
Runtime target: NIMH MonkeyLogic  
Stimulus bank: frozen `stimuli/v1` schema-v7 manifest

## 1. Decision summary

The first main experiment should be an **event-related ambiguous-to-cued transition task** rather
than a 30-60 s continuous bistable-viewing task.

Within each trial, the animal first views an ambiguous Rubin face-vase image. Without changing the
source contour, geometry, or polarity, the image then changes to a face-directed, vase-directed,
conflicting, or unchanged condition from the frozen stimulus bank. Neural activity is measured before
and after this cue transition. A delayed category report is collected after the stimulus has disappeared,
so that the principal neural analysis is separated from the motor response.

The report is a saccadic choice between face and vase reference targets whose left-right positions are
randomized on every trial. Clearly disambiguated catch trials have an objectively correct answer.
Ambiguous and cue-transition probe trials reward either valid report equally, following the logic of
classic monkey rivalry experiments: the animal is trained and behaviorally verified on physical control
trials, but is not taught that one subjective answer is "correct" on ambiguous trials.

An independent localizer provides empirically measured face and vase neural templates. The main
analysis asks whether the population trajectory evoked by the ambiguous image moves toward those
reference templates after a cue, whether the movement generalizes across physically different cue
families and source contours, and whether trial-by-trial neural evidence predicts the animal's report.

This design does **not** assume that the ambiguous representation must converge onto exactly one
category. Conflict trials and residual dimensions are retained to test delayed convergence, mixtures of
face/vase states, or a distinct non-endpoint state.

A continuous 30-60 s spontaneous-switching task is reserved as a follow-up after report validity and
recording stability have been demonstrated. It is not the recommended first experiment because its
switch time is uncertain, report-related activity is difficult to separate, and it does not exploit the
within-trial cue manipulation that motivates this project.

## 2. Scientific questions

### Primary question

How does population activity in object-selective cortex evolve when the same ambiguous object is
subsequently supplied with perceptually directional evidence?

### Secondary questions

1. Does cue-driven neural movement follow a cue-invariant face-vase identity axis, or does each
   physical cue produce a separate trajectory?
2. Does an ambiguous baseline occupy an intermediate point, a variable mixture of endpoint states,
   a low-confidence region, or a distinct state outside the face-vase endpoint axis?
3. Do congruent cues accelerate and stabilize category-template evidence, while conflicting cues
   delay it, increase trial-to-trial variability, or produce a third trajectory?
4. Does trial-by-trial neural evidence predict a face/vase report after controlling for physical cue,
   source contour, polarity, gaze, and response target position?
5. If simultaneous recordings from more than one visual area are available, does directed interaction
   change after cue onset? This is secondary and must not be inferred from trajectory timing alone.

## 3. Literature-derived design choices

- Hasson et al. (2001) showed that brief presentation and masking can make face- and vase-directed
  grouping conditions reliable while minimizing complementary reinterpretation. It also established
  that global grouping can modulate face-related cortex beyond local feature differences.
- Rassi et al. (2019) used a 1.0-1.8 s prestimulus interval, 150 ms Rubin stimulus, 200 ms mask, and
  delayed report to study onset-locked perceptual content. The present design adopts the separation of
  stimulus processing from report, but adds an explicit within-trial cue transition.
- Wang et al. (2013) and Hardstone et al. (2022) motivate separate unambiguous, continuous
  ambiguous, and discontinuous conditions. For the present project, unambiguous conditions become
  localizer/catch trials; continuous and discontinuous viewing are later mechanistic extensions rather
  than the first main task.
- Pitts et al. (2011) motivates resolving early border/figure-ground and later category-sensitive
  activity, but its report-triggered probe paradigm is not copied because the present project needs
  externally timed cue onset and clean single-trial trajectories.
- Leopold et al. (2002) shows that intermittent presentation creates strong perceptual memory. The
  schedule therefore treats recent percept, repeated source contour, and trial history as modeled
  variables rather than assuming independent trials.
- Logothetis and Schall (1989), Leopold and Logothetis (1996), and Sheinberg and Logothetis (1997)
  motivate interleaving ambiguous trials with objectively verifiable physical controls, randomizing
  motor mappings, and using catch trials to establish that monkey reports are meaningful.

## 4. Experimental program

The project should proceed through four stages. Only Stages 0-2 are required for the first neural
experiment.

### Stage 0: stimulus calibration and subset selection

The 384-image bank is a screening library, not a single recording-session condition table.

A brief behavioral calibration should estimate, for each candidate condition:

- probability of face report;
- probability of vase report;
- omission/late-response rate;
- response time;
- fixation-break rate;
- dependence on source contour, polarity, and preceding trial.

A human pilot is useful because it is inexpensive and directly comparable with the published work,
but it cannot replace monkey-specific calibration. The final subset must be validated in the trained
animal.

The human version may use the Rassi-style static presentation for initial screening:

1. fixation: 1.0-1.8 s jitter;
2. image: 150-200 ms;
3. phase-scrambled mask: 200 ms;
4. face/vase/unsure response.

A second, smaller human pilot should use the same ambiguous-to-cued transition timing proposed for
the monkey experiment, because a cue that works when shown alone may not produce the same effect
when it appears after an ambiguous baseline.

### Stage 1: monkey category training and neural localizer

The animal learns a delayed match-to-category report:

- face and vase reference targets are displayed after the sample period;
- their left-right positions are randomized every trial;
- the animal must maintain fixation until the go cue and then saccade to the selected target;
- clearly face-directed or vase-directed trials have a correct answer and provide correctness feedback;
- source contour and polarity are varied during training so the rule cannot be solved by memorizing one
  bitmap.

Training gates:

- at least 90% correct overall on unambiguous trials;
- at least 85% correct within every trained source/polarity stratum;
- no persistent spatial-choice bias greater than 10 percentage points after target-position
  randomization;
- stable fixation and response timing across blocks.

The independent neural localizer has two parts:

1. **General category localizer:** natural or line-drawn faces, vases/containers, non-face objects, and
   scrambled controls.
2. **Bank-specific endpoint localizer:** strongly face-directed and strongly vase-directed Rubin
   endpoints from multiple source contours, cue families, and polarities.

The bank-specific localizer defines the principal face-vase reference templates used in the main
analysis. Unit selection, template fitting, and testing must use independent data splits to avoid
circularity.

### Stage 2: main ambiguous-to-cued transition experiment

#### 4.2.1 Trial timeline

All durations are provisional and must be converted to integer frames using the measured display
refresh rate.

| Epoch | Proposed duration | Purpose |
| --- | ---: | --- |
| Intertrial interval | 700-1200 ms jitter | reduce temporal expectation and allow recovery |
| Fixation acquisition | up to 2000 ms | acquire central fixation |
| Fixation hold | 500-800 ms jitter | prestimulus baseline |
| Ambiguous baseline image | 300, 450, or 600 ms | establish an onset-locked ambiguous state; jitter separates cue response from adaptation |
| Cue-transition image | 400 ms | add face, vase, conflict, or no-change evidence while preserving source and polarity |
| Phase-scrambled mask | 200 ms | terminate visual processing and prevent continued reinterpretation |
| Memory/response delay | 300-500 ms jitter | separate visual activity from motor preparation |
| Choice targets and go cue | up to 1000 ms | delayed face/vase report |
| Feedback/reward | hardware dependent | objective feedback on catch trials; equal reward for either valid report on ambiguous probes |

A small central fixation marker is drawn dynamically by MonkeyLogic and remains visible during the
sample epochs for the macaque task. It must not be baked into any PNG/SVG. Its exact size and color
must be chosen so it does not obscure the face-vase boundary and must be logged in the display
configuration.

#### 4.2.2 Primary transition families

The first experiment should use a deliberately interpretable subset. For every transition, `base_id`
and `polarity` remain unchanged between the ambiguous baseline and the post-transition image.

The ambiguous baseline predicate is:

```text
content=ambiguous
outline=ambiguous
shading=none
material=ambiguous
```

Recommended primary endpoints are:

| Family | Manifest predicate after transition | Interpretation |
| --- | --- | --- |
| No change | `content=ambiguous, outline=ambiguous, shading=none, material=ambiguous` | adaptation/time control |
| Face content | `content=face, outline=ambiguous, shading=none, material=ambiguous` | single face-directed cue |
| Face outline | `content=ambiguous, outline=face, shading=none, material=ambiguous` | single face-directed cue |
| Vase content | `content=vase, outline=ambiguous, shading=none, material=ambiguous` | single vase-directed cue |
| Vase material | `content=ambiguous, outline=ambiguous, shading=none, material=vase` | single vase-directed cue |
| Face congruent | `content=face, outline=face, shading=none, material=ambiguous` | two congruent face cues |
| Vase congruent | `content=vase, outline=ambiguous, shading=none, material=vase` | two congruent vase cues |
| Conflict A | `content=face, outline=ambiguous, shading=none, material=vase` | face content against vase material |
| Conflict B | `content=vase, outline=face, shading=none, material=ambiguous` | vase content against face outline |

Hard figure shading is excluded from the primary block because its direction changes with the current
figure assignment and an unconditional shading effect would be uninterpretable. It should enter a
separate replication block with analysis stratified by outline:

- ambiguous outline plus figure shading: vase-directed shading condition;
- face outline plus figure shading: face-directed shading condition.

This preserves the shading manipulation without contaminating the first, simpler test.

#### 4.2.3 Sources, polarity, and session load

All four source contours should appear across the experiment so category evidence can be tested for
cross-source generalization. A single recording session should normally use two source contours and a
reversed pair of polarity mappings. This gives:

```text
9 transition families x 2 sources x 2 polarity mappings = 36 main cells
```

A pilot target is 12-16 valid repetitions per main cell, giving 432-576 valid main trials before catch
trials and fixation failures. Source pairs and polarity pairs rotate across sessions. With chronically
stable populations, all four sources may be included in one session after the initial pilot.

Trials are divided into blocks of approximately 80-120 valid trials with short rest periods. Maximum
session length must be set from the animal's stable performance rather than by forcing completion of a
precomputed table.

#### 4.2.4 Catch and report-validity trials

Twenty-five to forty percent of trials during training, and at least twenty percent during recording,
should be objectively verifiable catch trials. They include:

- static strongly face-directed endpoints;
- static strongly vase-directed endpoints;
- baseline-to-congruent face transitions;
- baseline-to-congruent vase transitions;
- occasional physically unambiguous images from outside the Rubin bank, if already used in training.

On catch trials, only the correct category report is rewarded. On ambiguous/no-change/single-cue/
conflict probe trials, either valid category report receives the same reward. The animal must not be
trained that the experimenter's `design_tag` is the correct subjective answer.

The following checks establish report validity:

1. high accuracy on physical catch trials;
2. report generalization to held-out source contours and polarities;
3. no fixed spatial response after target-position randomization;
4. cue conditions shift report probability in the predicted direction at the group/session level;
5. trial-by-trial reports covary with independently measured neural category evidence;
6. gaze and microsaccade distributions do not explain the report effect.

A binary report is the primary design because it is trainable and directly comparable with the classic
monkey rivalry literature. It does not imply that the neural state is binary. A later opt-out/uncertainty
extension may add a third target after the binary task is stable. That extension requires separate
training with physically degraded or conflicting examples and cannot by itself prove human-like
metacognitive awareness.

#### 4.2.5 No-report trials

After the animal has learned the report task, a minority of main trials may omit the choice targets and
provide passive reward after a matched delay. These trials test whether cue-driven neural movement
persists without an overt report or motor plan.

No-report trials cannot identify subjective percept on a particular trial. Their interpretation is limited
to cue-driven movement toward or away from independently defined category templates.

### Stage 3: optional continuous-bistability follow-up

Only after Stage 2 passes its behavioral and neural gates should the project add a long continuous
condition resembling Wang et al. (2013) and Hardstone et al. (2022):

- 30-60 s continuously visible ambiguous image;
- continuous lever hold or validated state report;
- spontaneous report changes aligned to neural activity;
- unambiguous and physically induced transitions as temporal controls.

This follow-up addresses spontaneous stability and switching. It is not required to answer the first
cue-transition question and should not delay the initial experiment.

## 5. Randomization and history control

Randomization must be deterministic from participant/animal, session, block, and seed.

Constraints:

- no immediate repetition of the same `stimulus_id`;
- limit repeated source contour and repeated transition direction;
- balance face/vase target positions within every condition family;
- balance cue-onset duration across condition, source, and polarity;
- distribute catch trials throughout the block rather than clustering them;
- record the previous stimulus, previous report, previous reward, and time since the previous trial.

Because intermittent presentation can preserve the preceding percept, the primary behavioral and
neural models must include recent report/history terms. Trial shuffling alone is not an adequate
control.

## 6. Eye tracking and fixation policy

- Fixation is required from acquisition through mask offset.
- The initial training window may be approximately 2 degrees radius and should be tightened toward
  1.5 degrees if performance permits; the final value is a hardware/training decision.
- A fixation break aborts the trial before report targets appear and receives a distinct trial-error code.
- Horizontal/vertical gaze, pupil size, saccades, and microsaccades around image onset and cue onset are
  retained for analysis.
- Trials containing cue-direction-specific gaze shifts must be excluded or explicitly modeled.
- The fixation marker's visibility during each epoch is logged; stimulus files remain marker-free.

## 7. Provisional MonkeyLogic event-code scheme

Exact hardware mappings remain pending, but the semantic code table should follow this structure:

| Code | Event |
| ---: | --- |
| 10 | trial start |
| 20 | fixation target on |
| 21 | fixation acquired |
| 30 | ambiguous baseline image on |
| 40 | cue-transition frame on |
| 41 | no-change transition |
| 42 | face-directed transition |
| 43 | vase-directed transition |
| 44 | conflict transition |
| 50 | mask on |
| 60 | response targets/go cue on |
| 61 | face target left / vase target right |
| 62 | vase target left / face target right |
| 70 | response registered |
| 71 | face report |
| 72 | vase report |
| 73 | omission/late response |
| 80 | reward onset |
| 90 | fixation break |
| 91 | early response |
| 92 | manual abort |

Stimulus onset and cue-transition onset must additionally be verified with a photodiode or equivalent
display-timing signal. Requested frame numbers, actual timestamps, and dropped/late frames are stored
in BHV2 and exported tables.

## 8. Primary neural analyses

### 8.1 Endpoint-template decoder

Train a regularized linear decoder on independent bank-specific unambiguous face and vase endpoint
trials. Test it on the ambiguous baseline and cue-transition epochs.

Report:

- time-resolved face-vase evidence;
- temporal generalization;
- cross-source generalization;
- cross-polarity generalization;
- cross-cue-family generalization.

A decoder that generalizes from content cues to outline/material cues is stronger evidence for a
category-level representation than a decoder tested on the same physical cue family.

### 8.2 Population trajectory

Construct population trajectories without assuming that all information lies on one face-vase axis.
At minimum quantify:

- distance to the face endpoint template;
- distance to the vase endpoint template;
- projection onto the endpoint discriminant;
- orthogonal distance from the endpoint axis;
- trial-to-trial dispersion;
- cue-onset change-point latency.

Conflict trials should be compared using explicit model alternatives:

1. a single intermediate state;
2. a trial mixture of face-like and vase-like endpoint states;
3. delayed convergence to either endpoint;
4. a distinct state with large orthogonal distance from the endpoint axis.

### 8.3 Demixing physical cue and category evidence

Use source contour, polarity, cue family, cue direction, report, and time as separate predictors.
Suitable approaches include cross-validated regression, demixed PCA, targeted dimensionality
reduction, or encoding models. Ordinary PCA may visualize the data but cannot by itself assign a
component to perceptual category.

### 8.4 Report prediction

Within the same physical condition, test whether pre-response neural evidence predicts face versus
vase report. Models should include:

- transition family;
- source contour;
- polarity;
- cue-onset duration;
- previous report and previous reward;
- target position;
- gaze and microsaccade variables.

This analysis is the strongest available bridge from cue-driven neural movement to the animal's
reported percept.

### 8.5 Timing interpretation

Use descriptive windows rather than labeling them feedforward or feedback by latency alone:

- 0-100 ms after cue transition: immediate physical-change response;
- 100-250 ms: emerging figure-ground/category reorganization;
- 250-400 ms: later stabilization or decision-related state.

Feedforward/feedback claims require simultaneous multiarea data or another direct interaction
measure. A delayed category decoder, attractor-like convergence, or a curved trajectory is not by
itself evidence for feedback.

### 8.6 LFP and directed interaction

If simultaneous recordings from multiple areas are available, analyze spike-field coupling,
frequency-specific coherence, and carefully validated directed measures as secondary endpoints.
Any Granger-style analysis must address common reference, common input, stationarity, model order,
and time-reversal/surrogate controls. It must not be used merely because Wang et al. and Rassi et al.
used Granger causality with fMRI/MEG.

## 9. Required controls

1. **No-change control:** separates cue effects from elapsed time and adaptation.
2. **Independent unambiguous localizer:** supplies noncircular face/vase templates.
3. **Cross-cue generalization:** separates category direction from a particular pixel manipulation.
4. **Cross-source generalization:** tests identity evidence beyond one silhouette.
5. **Polarity reversal:** controls figure/background luminance assignment.
6. **Delayed response:** separates main visual dynamics from the motor report.
7. **Random target position:** removes fixed category-to-movement mapping.
8. **Catch trials:** verifies that the monkey follows the task and reports physical category changes.
9. **Eye tracking:** rules out cue- or report-specific gaze explanations.
10. **Report/no-report comparison:** tests whether the neural effect depends on overt choice.

## 10. Pilot and production gates

The project proceeds to full neural recording only if:

- selected ambiguous baselines produce both reports across sessions and are not effectively
  unambiguous for the animal;
- face- and vase-directed conditions shift choice probability in the intended directions;
- catch-trial accuracy meets the training gates;
- an independent endpoint decoder distinguishes face and vase conditions above chance and shows at
  least some held-out source/cue generalization;
- cue-onset timing and photodiode timing are stable with no systematic dropped frames;
- fixation performance supports the planned valid-trial count;
- the complete session can be finished without a late-session collapse in behavior.

If a reliable percept report cannot be trained, the same sensory sequence may still be used as a
no-report experiment. The permitted conclusion is then limited to **cue-driven movement of neural
activity toward independently measured face/vase templates**. It must not be described as a change in
the monkey's subjective percept.

## 11. Remaining hardware decisions

The scientific paradigm is defined above. The following implementation values remain intentionally
pending until the laboratory setup is confirmed:

- MonkeyLogic and MATLAB versions;
- display resolution, measured refresh rate, monitor geometry, and viewing distance;
- final visual angle and fixation-marker size;
- eye tracker and calibrated eye window;
- response target eccentricity and saccade acceptance window;
- reward duration/volume;
- electrophysiology acquisition system and event interface;
- photodiode channel and neural-clock synchronization;
- stable number of simultaneously recorded units and realistic session length.

These values belong in a display/hardware configuration and must not be silently inferred from the
human MEG studies.

## 12. References guiding this design

- Hasson U, Hendler T, Ben Bashat D, Malach R. 2001. *Vase or Face? A Neural Correlate
  of Shape-Selective Grouping Processes in the Human Brain.*
- Pitts MA, Martínez A, Brewer JB, Hillyard SA. 2011. *Early Stages of Figure-Ground
  Segregation during Perception of the Face-Vase.*
- Wang M, Arteaga D, He BJ. 2013. *Brain mechanisms for simple perception and bistable
  perception.*
- Rassi E, Wutz A, Müller-Voggel N, Weisz N. 2019. *Prestimulus feedback connectivity
  biases the content of visual experiences.*
- Hardstone R, Flounders MW, Zhu M, He BJ. 2022. *Frequency-specific neural signatures
  of perceptual content and perceptual stability.*
- Logothetis NK, Schall JD. 1989. *Neuronal Correlates of Subjective Visual Perception.*
- Leopold DA, Logothetis NK. 1996. *Activity changes in early visual cortex reflect monkeys'
  percepts during binocular rivalry.*
- Sheinberg DL, Logothetis NK. 1997. *The role of temporal cortical areas in perceptual
  organization.*
- Leopold DA, Wilke M, Maier A, Logothetis NK. 2002. *Stable perception of visually
  ambiguous patterns.*
