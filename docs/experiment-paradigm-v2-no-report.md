# Rubin Cue-Transition Experiment Paradigm v2: No Category Report

Status: proposed alternative v0.2 for scientific review; not production-ready  
Primary observer: macaque  
Primary recording: spikes and LFP from object-selective visual cortex, with eye tracking  
Behavioral requirement: fixation only; no face/vase report  
Runtime target: NIMH MonkeyLogic  
Stimulus bank: frozen `stimuli/v1` schema-v7 manifest

## 1. Decision summary

This version removes all monkey face/vase reports from the experiment. The animal is rewarded only
for maintaining fixation through the visual sequence. No choice targets, category training, category
feedback, category-dependent reward, or report-aligned neural analysis are used.

The main experiment remains an **event-related ambiguous-to-cued transition task**. Each trial first
presents a neutral Rubin face-vase baseline. The image then changes, while preserving its source
contour and polarity, to a face-directed, vase-directed, conflicting, or unchanged condition from the
frozen bank. Neural activity is measured relative to the externally controlled cue-transition onset.

The primary endpoint is no longer the animal's reported percept. Instead, the experiment asks whether
physical cues drive the neural population toward independently measured face-directed and
vase-directed endpoint representations, whether that movement generalizes across cue families and
source contours, and whether conflict produces an intermediate, mixed, delayed, or off-axis state.

This is a valid and potentially cleaner experiment, but it answers a narrower question. It can support
claims about **cue-driven representational dynamics** and **state-dependent integration**. It cannot
identify the monkey's subjective percept on an individual trial and cannot establish that a cue caused a
face-to-vase or vase-to-face perceptual switch.

Human behavioral calibration is therefore retained as a manipulation check showing that the selected
stimuli bias human perception in the expected direction. It improves the perceptual relevance of the
stimulus set but does not substitute for a monkey report.

A long continuous spontaneous-bistability task is not recommended in the no-report version. Without a
validated percept label or proxy, a spontaneous transition cannot be distinguished from adaptation,
state drift, eye movements, arousal changes, or other endogenous fluctuations. The externally timed cue
transition provides the interpretable event that such a design requires.

## 2. Scientific scope

### 2.1 Primary question

How does population activity in object-selective cortex evolve when directional figure-ground and
object-category cues are added to an initially ambiguous Rubin stimulus, in the absence of an overt
category report?

### 2.2 Primary hypotheses

1. Face-directed and vase-directed cues will shift population activity in opposite directions along an
   independently defined endpoint axis.
2. A shift that generalizes across content, outline, material, source contour, and polarity will reflect a
   more abstract representation than a shift restricted to one pixel manipulation.
3. Congruent cues will produce earlier, larger, or more stable endpoint-directed movement than
   single-cue conditions.
4. Conflict conditions will show one or more of the following: reduced endpoint projection, delayed
   movement, increased single-trial dispersion, a mixture of endpoint-like trials, or increased distance
   orthogonal to the endpoint axis.
5. The same final image will evoke different early trajectories when reached directly from blank versus
   after an ambiguous prelude, revealing state/history dependence.

### 2.3 Explicit non-claims

This experiment alone must not be described as showing:

- which percept the monkey experienced on a given trial;
- the probability that the monkey saw a face or a vase;
- a subjective perceptual switch;
- perceptual dominance duration or spontaneous reversal dynamics;
- awareness, confidence, uncertainty, or metacognition;
- feedforward or feedback processing based only on response latency or trajectory shape.

The permitted language is that neural activity became more similar to an independently defined
face-directed or vase-directed endpoint representation after a physical cue.

## 3. Why the literature supports this version

- Hasson et al. (2001) showed that cue-controlled Rubin variants can modulate face-related cortex while
  most local image structure is preserved. Their participants performed an orthogonal one-back task
  rather than continuously reporting face versus vase, demonstrating that category-report-free neural
  contrasts are feasible.
- Pitts et al. (2011) provides approximate timing anchors for border ownership, figure-ground
  segregation, and later face-sensitive processing. These are descriptive analysis windows, not fixed
  assumptions about macaque object-selective cortex.
- Rassi et al. (2019) demonstrates the value of brief onset-locked Rubin presentation, masking, and a
  prestimulus baseline. The present design retains the temporal control but removes the category report.
- Wang et al. (2013) and Hardstone et al. (2022) establish unambiguous endpoint conditions as useful
  references for ambiguous perception. In this version those conditions define physical/neural
  endpoints, not verified monkey percepts.
- Leopold et al. (2002) shows that intermittent presentation carries strong history effects. The schedule
  and analysis therefore model prior stimulus state even though prior percept is unavailable.
- The classic monkey rivalry studies by Logothetis and colleagues show why subjective-percept claims
  normally require validated animal reports. Their absence here is a reason to narrow interpretation,
  not a reason to infer the missing label from neural activity.

## 4. Experimental program

### Stage 0: human behavioral calibration

The frozen 384-stimulus bank remains a screening library. A human pilot should estimate the actual
perceptual effect of candidate conditions before selecting the monkey subset.

The first human screen may use:

1. fixation: 1.0-1.8 s jitter;
2. single image: 150-200 ms;
3. source-matched phase-scrambled mask: 200 ms;
4. face/vase/unsure report.

A second human pilot should use the same ambiguous-to-cued transition sequence planned for the
monkey experiment. For each condition estimate:

- change in face-report probability relative to no-change baseline;
- change in vase-report probability;
- unsure rate;
- response time;
- source-contour and polarity dependence;
- sequential dependence on the preceding trial.

Selection should favor conditions that:

- produce a reliable directional shift across observers;
- retain some uncertainty rather than becoming trivial replicas of ordinary face or vase images;
- remain directionally consistent across more than one source contour and polarity;
- provide both strong congruent endpoints and genuinely competing conflict conditions.

Human calibration is a stimulus manipulation check only. A human P(face) value must not be assigned
to the monkey's trial-level neural data as though it were the animal's percept.

### Stage 1: fixation training and independent neural localizers

The monkey is trained only to acquire and maintain central fixation. Reward depends on fixation success
and trial completion, never on stimulus category or cue direction.

No face/vase category rule needs to be learned. This substantially reduces training burden and removes
category-decision and response-mapping activity from the main experiment.

Two independent localizers are recommended.

#### 4.1.1 General object-category localizer

Present natural or line-drawn examples from at least these groups:

- faces, including profile faces;
- vases, cups, or containers;
- other non-face objects;
- scrambled or texture controls.

This localizer identifies face-selective and general object-responsive units and tests whether the
recorded population contains a meaningful face-versus-central-object organization.

#### 4.1.2 Bank-specific endpoint localizer

Present strongly face-directed and strongly vase-directed Rubin endpoints from multiple source
contours, cue families, and polarities. These trials define the main endpoint templates.

The endpoint axis should be named the **face-directed versus vase-directed physical endpoint axis**.
It must not be called a percept axis unless a separate experiment validates monkey percepts.

Localizer and main-task data must remain independent. Unit selection, dimensionality reduction,
decoder fitting, hyperparameter tuning, and endpoint-template construction must use training data that
are separate from the main tests.

### Stage 2: main no-report cue-transition experiment

#### 4.2.1 Trial structure

All durations remain provisional until display refresh rate and frame timing are measured.

| Epoch | Proposed duration | Purpose |
| --- | ---: | --- |
| Intertrial interval | 700-1200 ms jitter | recovery and reduced temporal predictability |
| Fixation acquisition | up to 2000 ms | acquire central fixation |
| Fixation hold | 500-800 ms jitter | prestimulus neural baseline |
| Ambiguous baseline image | 300 or 600 ms | establish an ambiguous sensory state; two onset times separate cue response from simple elapsed time |
| Cue-transition image | 400 ms | add directional, conflicting, or unchanged evidence |
| Phase-scrambled mask | 200 ms | terminate stimulus-driven processing |
| Post-mask fixation | 400-700 ms jitter | measure poststimulus recovery without motor preparation |
| Reward | hardware dependent | reward successful fixation only |

The fixation marker is drawn dynamically by MonkeyLogic and remains visible throughout the image and
mask epochs. It is never embedded in the stimulus files.

There are no face/vase targets, response window, category feedback, or category-dependent rewards.
The reward schedule must be condition-independent so the animal cannot learn cue value indirectly.

#### 4.2.2 Attention and wakefulness

The cleanest main task uses fixation-contingent reward only. Pupil size, fixation stability, blink rate,
and fixation failures provide online measures of wakefulness and engagement.

If passive fixation proves insufficient, an **orthogonal fixation-dimming block** may be added as a
separate control condition. A small luminance change occurs at the fixation marker after mask offset,
and the animal reports only that change using a single invariant response. Target trials are excluded
from the primary cue-transition analysis. The dimming event must not occur during the ambiguous or
cue epochs because it would introduce attention and motor-preparation effects into the critical window.

An orthogonal task must never require attending to the face or vase region, because that would itself
bias figure-ground assignment.

#### 4.2.3 Core transition families

For every transition, `base_id` and `polarity` remain unchanged from baseline to cue image.

The neutral baseline predicate is:

```text
content=ambiguous
outline=ambiguous
shading=none
material=ambiguous
```

The core main-task families are:

| Family | Final-image predicate | Main contrast |
| --- | --- | --- |
| No change | `content=ambiguous, outline=ambiguous, shading=none, material=ambiguous` | elapsed time and repeated-frame control |
| Face content | `content=face, outline=ambiguous, shading=none, material=ambiguous` | isolated face-directed content cue |
| Face outline | `content=ambiguous, outline=face, shading=none, material=ambiguous` | isolated face-directed closure cue |
| Vase content | `content=vase, outline=ambiguous, shading=none, material=ambiguous` | isolated vase-directed content cue |
| Vase material | `content=ambiguous, outline=ambiguous, shading=none, material=vase` | isolated vase-directed relief cue |
| Face congruent | `content=face, outline=face, shading=none, material=ambiguous` | combined face-directed evidence |
| Vase congruent | `content=vase, outline=ambiguous, shading=none, material=vase` | combined vase-directed evidence |
| Conflict A | `content=face, outline=ambiguous, shading=none, material=vase` | face content against vase material |
| Conflict B | `content=vase, outline=face, shading=none, material=ambiguous` | vase content against face outline |

Figure shading remains outside the first core block because its direction depends on outline state. It
should be introduced only in a separate stratified block:

- ambiguous outline plus figure shading: vase-directed shading;
- face outline plus figure shading: face-directed shading.

#### 4.2.4 Path-matched controls

The no-report design needs a stronger physical control than the report version. For a selected subset of
final images, present the same final image by two routes:

1. **Direct route:** fixation baseline followed directly by the final image;
2. **Ambiguous-prelude route:** neutral ambiguous image followed by the identical final image.

The final image, duration, source contour, polarity, and reward are identical. Only the preceding visual
state differs.

A trajectory difference after final-image onset demonstrates state/history dependence. It does not by
itself prove perceptual hysteresis, but it helps distinguish a simple static image-response account from a
state-dependent integration account.

A smaller optional reversal block may compare:

- face-directed prelude to vase-directed final image;
- vase-directed prelude to face-directed final image;
- ambiguous prelude to the same final images.

This is useful only after the core design is stable because it increases the condition count sharply.

#### 4.2.5 Session composition

A practical core session may use:

```text
9 transition families x 2 source contours x 2 reversed polarity mappings
x 2 cue-onset delays = 72 cells
```

Target 8-10 valid repetitions per cell within a session, yielding 576-720 valid core trials. If that is too
long for stable fixation or unit recording, split the design by source pair or cue-onset delay and combine
across sessions only when population stability permits.

The path-control block should use a smaller subset, preferably:

- no-change;
- one face-content endpoint;
- one face-outline endpoint;
- one vase-content endpoint;
- one vase-material endpoint;
- face-congruent and vase-congruent endpoints.

Blocks should contain approximately 80-120 valid trials with rest periods. Session stopping rules should
be based on fixation performance, pupil/wakefulness measures, and recording stability rather than a
requirement to exhaust every precomputed trial.

## 5. Randomization and trial-history control

Randomization is deterministic from animal, session, block, and seed.

Constraints:

- no immediate repetition of the same `stimulus_id`;
- balance cue direction and cue-onset delay across each block;
- limit repeated source contour, polarity, and final-image family;
- balance direct and ambiguous-prelude routes within path-control blocks;
- distribute no-change and endpoint trials throughout the session;
- keep reward probability and amount independent of cue condition;
- record previous stimulus family, previous source, previous cue direction, previous fixation outcome,
  previous reward, and intertrial interval.

Because no percept report is available, trial history cannot include previous percept. The analysis must
therefore use observable history variables and avoid interpreting unexplained sequential dependence as
perceptual memory.

## 6. Eye tracking and exclusion policy

Eye data are controls, not no-report percept labels.

- Fixation is required from fixation acquisition through post-mask hold.
- The initial fixation window may be approximately 2 degrees radius and tightened toward 1.5 degrees
  if training and hardware permit.
- A fixation break aborts the trial and receives no reward.
- Gaze position, pupil size, blinks, saccades, microsaccades, and fixation dispersion are stored
  continuously.
- Cue-family or direction effects must be re-estimated after matching or regressing eye variables.
- Trials with saccades or blinks in the critical cue window are excluded from primary analyses.
- Differences in eye behavior may be exploratory correlates of stimulus processing but are not treated
  as validated face/vase percept proxies.

## 7. Provisional MonkeyLogic event codes

| Code | Event |
| ---: | --- |
| 10 | trial start |
| 20 | fixation target on |
| 21 | fixation acquired |
| 30 | ambiguous baseline image on |
| 31 | direct-route final image on |
| 40 | cue-transition image on |
| 41 | no-change transition |
| 42 | face-directed transition |
| 43 | vase-directed transition |
| 44 | conflict transition |
| 45 | path-control final image on |
| 50 | mask on |
| 55 | post-mask fixation period on |
| 80 | fixation-contingent reward onset |
| 90 | fixation break |
| 91 | blink/saccade exclusion flag |
| 92 | manual abort |
| 95 | optional orthogonal fixation-dimming target |
| 96 | optional orthogonal response |

Stimulus and transition onset must be verified by photodiode or an equivalent display-timing channel.
BHV2 and exported tables must store requested frames, actual timestamps, timing errors, display
configuration, stimulus IDs for both prelude and final image, route type, and all eye-event flags.

## 8. Primary dependent variables and analyses

### 8.1 Independent endpoint templates

Build face-directed and vase-directed endpoint templates using the independent bank-specific localizer.
Use regularized decoding or cross-validated distance estimates.

Primary outputs:

- time-resolved endpoint-axis projection;
- distance to face-directed endpoint template;
- distance to vase-directed endpoint template;
- cross-temporal generalization;
- cross-source generalization;
- cross-polarity generalization;
- cross-cue-family generalization.

A content-trained decoder that generalizes to outline or material cues is more informative than one
that only discriminates images from the same cue family.

### 8.2 Cue-locked population trajectory

Align activity to cue-transition onset and estimate:

- trajectory position;
- velocity and acceleration;
- cue-onset change-point latency;
- endpoint-axis projection;
- orthogonal distance from the endpoint axis;
- within-condition single-trial dispersion;
- distance from the no-change trajectory.

The ambiguous baseline should not be assumed to be the arithmetic midpoint of endpoint templates.
Its geometry is an empirical result.

### 8.3 Conflict-state model comparison

Compare at least four models:

1. **Intermediate-state model:** conflict trials cluster near a stable point between endpoints.
2. **Mixture model:** individual conflict trials are endpoint-like, but average to an intermediate state.
3. **Delayed-selection model:** activity initially remains ambiguous or off-axis, then moves toward one
   endpoint late in the trial.
4. **Distinct-state model:** conflict produces a reproducible trajectory with large orthogonal distance
   from the endpoint axis.

Without report labels, endpoint-like single trials cannot be called perceived-face or perceived-vase
trials. They are only neural-state classes defined relative to physical endpoint templates.

### 8.4 Path-dependence analysis

For physically identical final images, compare direct versus ambiguous-prelude routes.

Primary tests:

- early post-onset trajectory difference;
- time required for the two routes to converge;
- route-dependent endpoint projection;
- route-dependent trial dispersion;
- interaction of route with cue family and cue direction.

A persistent route effect suggests history-dependent neural dynamics. A transient early difference that
rapidly disappears is more compatible with ordinary adaptation or visual-transition responses.

### 8.5 Demixing cue identity and endpoint direction

Model these predictors separately:

- source contour;
- polarity;
- content state;
- outline state;
- material state;
- shading state, in its separate block;
- directional class: face, vase, conflict, or neutral;
- cue-onset delay;
- route: direct or ambiguous prelude;
- time;
- gaze and pupil variables.

Suitable methods include cross-validated encoding models, targeted dimensionality reduction, demixed
PCA, and representational similarity analysis. Ordinary PCA remains useful for visualization but cannot
label an axis as category or perceptual content by itself.

### 8.6 Low-level image-model control

Because there is no behavioral report to anchor interpretation, physical-image control is especially
important.

For every image and transition compute or model:

- mean luminance and RMS contrast;
- edge energy and changed-pixel area;
- image difference between baseline and final frame;
- source contour and polarity;
- optional early-layer image features or other prespecified low-level visual embeddings.

Test whether endpoint-axis neural movement explains variance beyond these physical predictors. The
strongest evidence for a category-level organization is cross-cue and cross-source generalization, not a
large within-family decoding score.

### 8.7 Cross-species condition-level validation

Relate human pilot cue efficacy to monkey neural endpoint movement at the condition level:

- human change in P(face) or P(vase);
- monkey endpoint-axis displacement;
- trajectory latency or magnitude;
- conflict-state dispersion.

A correlation supports perceptual relevance across conditions. It still does not identify the monkey's
trial-level percept and must be described as a cross-species condition-level association.

### 8.8 LFP and interareal interaction

If multiple areas are recorded simultaneously, analyze frequency-specific power, coherence,
spike-field coupling, and directed interaction as secondary endpoints.

Any Granger-style analysis must address common reference, common input, stationarity, model order,
trial count, time reversal, and surrogate controls. Timing alone, later divergence, or curved trajectories
do not establish feedback.

## 9. Required controls

1. **No-change transition:** elapsed time, adaptation, and frame-update control.
2. **Direct-onset final image:** tests whether trajectory depends on the ambiguous prelude.
3. **Independent endpoint localizer:** prevents circular endpoint definition.
4. **Cross-cue generalization:** separates direction from one cue's pixels.
5. **Cross-source generalization:** tests abstraction beyond one silhouette.
6. **Polarity reversal:** controls figure/background luminance assignment.
7. **Human behavioral calibration:** verifies that the selected cues are perceptually directional in
   humans.
8. **Low-level image model:** controls luminance, contrast, edge, and changed-pixel effects.
9. **Eye tracking:** removes gaze, blink, pupil, and microsaccade explanations.
10. **Condition-independent reward:** prevents learned cue value or reward prediction from masquerading
    as category evidence.
11. **Optional fixation-task control:** checks whether results survive a matched orthogonal engagement
    task.

## 10. Pilot and production gates

Proceed to a full recording program only if:

- human calibration confirms that selected face- and vase-directed cues shift reports in the intended
  directions;
- the monkey maintains stable fixation for the required trial duration and valid-trial count;
- independent endpoint trials are separable in the recorded population;
- endpoint decoding shows at least one held-out generalization test across source, polarity, or cue
  family;
- no-change trajectories are stable and timing artifacts are absent;
- photodiode timing confirms cue onset with acceptable frame precision;
- cue effects remain after eye-variable and low-level-image controls;
- recording and behavior remain stable across the planned block length.

If endpoint conditions are not separable in the recorded population, the experiment cannot support a
face-versus-vase representational-trajectory claim. It may still support lower-level cue-response
analyses, but that would be a different and substantially weaker project.

## 11. Comparison with the category-report version

| Design issue | v1 category-report version | v2 no-report version |
| --- | --- | --- |
| Monkey training | face/vase category rule and delayed saccade | fixation only |
| Primary endpoint | neural evidence plus monkey report | neural endpoint movement only |
| Trial-level subjective percept | partially inferable from validated report | unavailable |
| Motor/decision contamination | reduced by delayed report, not eliminated | largely removed from critical epoch |
| Session efficiency | lower because of response and catch trials | higher |
| Main interpretive strength | link between neural state and reported percept | cleaner cue-driven sensory dynamics |
| Main interpretive limitation | report and training may alter processing | cannot claim subjective perception |
| Most important added control | report validity and target randomization | direct-versus-prelude path matching and physical-image model |

## 12. Remaining implementation decisions

The following values remain pending until the laboratory setup is confirmed:

- MonkeyLogic and MATLAB versions;
- display resolution and measured refresh rate;
- monitor geometry, viewing distance, and final visual angle;
- fixation-marker size and eye window;
- reward volume and schedule;
- eye tracker and synchronization interface;
- electrophysiology acquisition hardware;
- photodiode channel and event-clock alignment;
- stable unit count and maximum reliable session duration;
- whether an orthogonal fixation-dimming block is needed.

No MonkeyLogic runner or schema-v7 condition table should be implemented until this no-report design
is explicitly selected or merged with the category-report alternative.

## 13. References guiding this design

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
