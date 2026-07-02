"""Bundled valve blueprints are copied into the config blueprint folder."""

from custom_components.smart_irrigation.blueprint_install import (
    install_bundled_blueprints,
)


def _src(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.yaml").write_text("blueprint A", encoding="utf-8")
    (src / "b.yaml").write_text("blueprint B", encoding="utf-8")
    return src


def test_copies_missing_blueprints(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "dst"
    installed = install_bundled_blueprints(src, dst)
    assert set(installed) == {"a.yaml", "b.yaml"}
    assert (dst / "a.yaml").read_text(encoding="utf-8") == "blueprint A"
    assert (dst / "b.yaml").read_text(encoding="utf-8") == "blueprint B"


def test_creates_destination_dir(tmp_path):
    install_bundled_blueprints(_src(tmp_path), tmp_path / "nested" / "dst")
    assert (tmp_path / "nested" / "dst").is_dir()


def test_does_not_overwrite_existing(tmp_path):
    src = _src(tmp_path)
    dst = tmp_path / "dst"
    dst.mkdir()
    (dst / "a.yaml").write_text("MY EDIT", encoding="utf-8")
    installed = install_bundled_blueprints(src, dst)
    # a.yaml preserved, only b.yaml newly installed
    assert installed == ["b.yaml"]
    assert (dst / "a.yaml").read_text(encoding="utf-8") == "MY EDIT"
    assert (dst / "b.yaml").read_text(encoding="utf-8") == "blueprint B"


def test_missing_source_is_noop(tmp_path):
    assert install_bundled_blueprints(tmp_path / "nope", tmp_path / "dst") == []


def test_only_yaml_copied(tmp_path):
    src = _src(tmp_path)
    (src / "README.txt").write_text("x", encoding="utf-8")
    dst = tmp_path / "dst"
    install_bundled_blueprints(src, dst)
    assert not (dst / "README.txt").exists()
