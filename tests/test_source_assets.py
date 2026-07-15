from __future__ import annotations

from pathlib import Path

from rubin_cues.source_assets import (
    SOURCE_ASSETS,
    render_source_preview,
    verify_source_assets,
)


def _project_root() -> Path:
    return Path(__file__).parents[1]


def test_source_registry_covers_all_imported_svg_files() -> None:
    project_root = _project_root()
    imported = {
        path.relative_to(project_root / "assets" / "source").as_posix()
        for path in (project_root / "assets" / "source").rglob("*.svg")
    }
    registered = {asset.relative_path for asset in SOURCE_ASSETS}
    assert len(SOURCE_ASSETS) == 6
    assert registered == imported


def test_only_profile_only_sources_allow_face_outline() -> None:
    allowed = {asset.source_id for asset in SOURCE_ASSETS if asset.face_outline_allowed}
    assert allowed == {
        "wm-cc0-classic",
        "wm-bysa-classic",
        "wm-bysa-klam",
        "oc-274578-heads",
    }


def test_four_accepted_profile_sources_are_enabled_for_the_bank() -> None:
    enabled = {asset.source_id for asset in SOURCE_ASSETS if asset.bank_enabled}
    assert enabled == {
        "wm-cc0-classic",
        "wm-bysa-classic",
        "wm-bysa-klam",
        "oc-274578-heads",
    }


def test_all_registered_sources_are_formal_bank_members() -> None:
    preview_only = {asset.source_id for asset in SOURCE_ASSETS if not asset.formal_bank_member}
    assert preview_only == set()


def test_source_svgs_are_immutable_valid_and_script_free() -> None:
    assert verify_source_assets(_project_root()) == []


def test_every_source_svg_rasterizes() -> None:
    project_root = _project_root()
    for asset in SOURCE_ASSETS:
        image = render_source_preview(project_root, asset)
        assert image.mode == "RGBA"
        assert image.width > 100
        assert image.height > 100
