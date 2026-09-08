# Stimulus sources and attribution

All images use shared contours derived from the sources below, with canvas/contour
normalization and outline, shading, material and polarity manipulations.
Each source ID maps to 30 images in `images/` and to `source_id` in `stimuli.csv`.

| Source ID | Source | Creator | License / status |
| --- | --- | --- | --- |
| `wm-cc0-classic` | [Two silhouette profile or a white vase](https://commons.wikimedia.org/wiki/File:Two_silhouette_profile_or_a_white_vase.svg) | Ian Remsen | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `wm-bysa-classic` | [Cup or faces paradox](https://commons.wikimedia.org/wiki/File:Cup_or_faces_paradox.svg) | Bryan Derksen; SVG conversion of an earlier image uploaded by Guam | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `wm-bysa-klam` | [Klam-DveTvareNeboPohar](https://commons.wikimedia.org/wiki/File:Klam-DveTvareNeboPohar.svg) | Kenjiro995; vectorization by Mrmw | [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) |
| `oc-274578-heads` | [Openclipart 274578](https://openclipart.org/detail/274578/heads-vase-illusion) | GDJ | [CC0 / public domain](https://openclipart.org/share) |
| `user-bird` | User-supplied black silhouette, `OIP.png` | Not established | Underlying license not supplied |
| `user-dog` | User-supplied black silhouette; supplied filename refers to stock photo 1494294344 | Not established | Underlying license not supplied |
| `user-woman` | Supplied `standing_woman_mirrored_body_visible.svg` | Embedded metadata attributes the contour to Cacciamani, Ayars & Peterson (2014), Figure 1A | Metadata claims and underlying reuse rights not independently verified |
| `user-macaque` | User-supplied black macaque silhouette, updated 2026-09-08 | Not established | Underlying license not supplied |

The derived `wm-bysa-classic` and `wm-bysa-klam` image sets are distributed under
CC BY-SA 3.0 with the attribution above. The user-supplied sets do not inherit
the older sources' licenses; no blanket license is asserted for the whole collection.

Animal silhouettes were vectorized from supplied masks, filled outward along the
inward contour, mirrored, and smoothed with a three-row filter. The accepted bird
and dog constructions retain the requested foot extension. The macaque was flipped
to face inward, retaining the front foot and excluding a final isolated tail-tip row.
The woman source was supplied already mirrored. All sets retain the accepted layout.
