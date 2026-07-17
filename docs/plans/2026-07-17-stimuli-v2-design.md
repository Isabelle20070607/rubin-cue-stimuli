# Stimuli v2 design

`stimuli/v2` is a new deterministic factorial bank. It does not replace or mutate the
published `stimuli/v1` schema-v7 bank.

The v2 directional design removes the `content` axis completely. Its manifest, condition
identifiers, SVG metadata, and filenames contain only `outline`, `shading`, `material`,
and `polarity`. Shading remains active and follows the current figure: it is vase-directed
when the outline is ambiguous and face-directed when the outline closes the two profiles.

V2 excludes every combination in which face- and vase-directed cues are both active.
Consequently, `outline=face, material=vase` is never generated, active shading remains
mutually exclusive with vase material, and v2 design tags are limited to `face`,
`ambiguous`, and `vase`. The redundant v1 `is_conflict` and
`content_face_accent_side` fields are absent from the v2 manifest.

The resulting space has five directional states crossed with six ordered polarity
mappings: 30 conditions per enabled source, four enabled sources, and 120 stimuli total.
V2 uses schema version 8. Generation, validation, montage creation, and combination audit
must select behavior from the config design profile so that v1 remains reproducible.

## Luminance calibration

V2 uses independently selected vase-material texture ranges: black `20-58`, gray
`103-186`, and white `170-252`. Black C and gray B remain selected; the revised white
range raises its mean while narrowing its lighting span. Material patches use SVG
`crispEdges` so independently rasterized shared edges do not create a grid or moiré
pattern. Across the four enabled sources and all relevant polarity mappings at 1024 px,
the final texture means are 43.3429, 153.8423, and 220.2085. The non-textured palette uses
black `43`, gray `154`, and white `220`, producing means 43.1520, 153.9762, and 219.8716;
every aggregate mismatch is below 0.34 gray level.

The v1 palette and texture ranges remain unchanged. Any later texture-range change must
repeat the four-source production-resolution measurement, update the v2 flat palette,
regenerate every v2 artifact, and refresh manifest hashes.

V2 face-figure shadows use the same deterministic offset sampler and bounds as the rest
of the bank, but normalize both components positive before rendering. The left face moves
right, the mirrored right face moves left, and both move downward. Thus both horizontal
and vertical magnitudes exceed 0.020 canvas units without the visible shadow being clipped
away at the outer or upper frame; v1 directionality remains unchanged.

Generated phase-scrambled masks remain available as optional artifacts. Their presence
does not place them in the default v2 experiment; a backward-masking block must be
approved separately before a runner or schedule references them.
