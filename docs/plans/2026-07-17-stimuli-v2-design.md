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
`103-186`, and white `132-244`. These correspond to the visually selected black C, gray
B, and unchanged white texture candidates. Material patches use SVG `crispEdges` so
independently rasterized shared edges do not create a grid or moiré pattern. Across the
four enabled sources and all relevant polarity mappings at 1024 px, the final texture
means are 43.3397, 153.8391, and 200.6372. The non-textured palette uses black `43`, gray
`154`, and white `201`, producing flat means of 43.1419, 153.9663, and 200.8915; every
aggregate mismatch is below 0.26 gray level.

The v1 palette and texture ranges remain unchanged. Any later texture-range change must
repeat the four-source production-resolution measurement, update the v2 flat palette,
regenerate every v2 artifact, and refresh manifest hashes.

Generated phase-scrambled masks remain available as optional artifacts. Their presence
does not place them in the default v2 experiment; a backward-masking block must be
approved separately before a runner or schedule references them.
