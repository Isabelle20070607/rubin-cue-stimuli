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
