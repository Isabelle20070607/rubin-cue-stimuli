# AGENTS.md

Project guidance for `G:\workspace\rubin-cue-stimuli`.

- Keep downloaded masters under `assets/source/` immutable; register their license and SHA-256 in `source_assets.py` and `assets/source/PROVENANCE.md`.
- Preserve the categorical 384-stimulus bank: `wm-cc0-classic`, `wm-bysa-classic`, `wm-bysa-klam`, and `oc-274578-heads` are enabled, with 96 valid conditions each; `shading=figure` is mutually exclusive with both `material=vase` and `content=face`. Keep OpenClipart 276846/276861 and their provenance records but exclude their entire stimulus families. Do not reintroduce graded strengths or non-vase/queen variants.
- Tag any combination containing both face- and vase-directed cues as `conflict` without majority voting; active shading follows the current figure and uses the unused third black/gray/white value.
- Keep fixation markers out of stimulus PNG/SVG files; experiment scripts may overlay fixation dynamically.
- Keep generator outputs deterministic from config version, base ID, and seed, and update manifests and hashes whenever rendering changes.
- Write Excel-facing CSV as `utf-8-sig`; use UTF-8 for JSONL, TOML, Python, and Markdown.
- Target NIMH MonkeyLogic for experiment delivery; do not add PsychoPy as a project dependency or runner.
- Run the workspace validation profile in `..\.agents\validation\rubin-cue-stimuli.psd1`; detailed protocol and data contracts live under `docs/`.
