"""Every bundled language must match en.json exactly, in both catalogues.

This project ships eight languages in two independent places (see CLAUDE.md /
the contributor notes): `translations/*.json` for Home Assistant entity names,
and `frontend/localize/languages/*.json` for the panel. Both fall back to
English per key at runtime, so a gap is invisible in testing and in the
maintainer's own (German) install — it only shows up as an English string in
someone else's UI, which nobody files a bug about.

Two real classes of drift this pins, both found on 2026-08-03:

* MISSING keys — PR #73 existed only because the continuous-updates card
  shipped English-only, and separately `entity.button.reset_usage.name` was
  absent from six of the eight backend catalogues.
* ORPHAN keys — 24 of them, mostly old names left behind by a rename
  (`auto-calc-time` → `calc-time`, `sensor-debounce` → `sensor_debounce`)
  plus stale `*-todo` placeholders. Harmless at runtime, but they make the
  files look like they cover something they do not, and they mislead the next
  person doing a translation pass.

en.json is the reference for both directions on purpose: it is the file the
frontend bundles and the one every fallback resolves to.
"""

import json
import re
from pathlib import Path

import pytest

_PLACEHOLDER = re.compile(r"\{[^}]*\}")
_NAMED_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
_ROOT = Path(__file__).resolve().parents[1] / "custom_components" / "irrigation_plus"
_CATALOGUES = {
    "backend": _ROOT / "translations",
    "panel": _ROOT / "frontend" / "localize" / "languages",
}


def _flatten(data, prefix=""):
    """Dotted leaf paths, so a key moving depth counts as a change."""
    if not isinstance(data, dict):
        return {prefix}
    keys = set()
    for key, value in data.items():
        keys |= _flatten(value, f"{prefix}.{key}" if prefix else key)
    return keys


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _cases():
    for catalogue, folder in _CATALOGUES.items():
        for path in sorted(folder.glob("*.json")):
            if path.name != "en.json":
                yield pytest.param(catalogue, path, id=f"{catalogue}-{path.stem}")


@pytest.mark.parametrize(("catalogue", "path"), list(_cases()))
def test_no_missing_keys(catalogue, path):
    """Anything in en.json must exist here, or that UI renders in English."""
    en = _flatten(_load(_CATALOGUES[catalogue] / "en.json"))
    missing = sorted(en - _flatten(_load(path)))
    assert not missing, (
        f"{path.name} is missing {len(missing)} key(s) present in en.json; "
        f"those strings will silently fall back to English: {missing[:10]}"
    )


@pytest.mark.parametrize(("catalogue", "path"), list(_cases()))
def test_no_orphan_keys(catalogue, path):
    """Anything here must exist in en.json, or it is dead weight."""
    en = _flatten(_load(_CATALOGUES[catalogue] / "en.json"))
    orphans = sorted(_flatten(_load(path)) - en)
    assert not orphans, (
        f"{path.name} has {len(orphans)} key(s) that no longer exist in "
        f"en.json — usually the old name left behind by a rename: {orphans[:10]}"
    )


class TestTheCopyHeuristicIsCalibrated:
    """Pins both sides, so the test above is neither vacuous nor noisy."""

    def test_a_format_string_is_not_prose(self):
        """The real false positive that forced this refinement."""
        assert len(_prose_words("{observed} mm (≥ {threshold} mm)")) < 4

    def test_a_short_label_is_not_prose(self):
        assert len(_prose_words("Reset water usage")) < 4

    def test_a_service_identifier_is_not_prose(self):
        """The second real false positive: an HA service name shown as an
        example, which must stay byte-identical in every language."""
        assert _prose_words("notify.mobile_app_phone") == []

    def test_an_entity_id_is_not_prose(self):
        assert _prose_words("sensor.irrigation_plus_front_lawn") == []

    def test_a_real_untranslated_sentence_is_caught(self):
        text = (
            "When on, a scheduled run that skips a zone because it currently "
            "has no water demand is recorded in that zone's history."
        )
        assert len(_prose_words(text)) >= 4

    def test_placeholders_alone_never_count(self):
        assert _prose_words("{a} {b} {c} {d} {e}") == []


def test_both_catalogues_ship_the_same_eight_languages():
    """A language added to one catalogue but not the other is half-translated."""
    langs = {
        name: {p.stem for p in folder.glob("*.json")}
        for name, folder in _CATALOGUES.items()
    }
    assert langs["backend"] == langs["panel"], langs
    assert len(langs["backend"]) == 8, sorted(langs["backend"])


def _prose_words(text):
    """Words that a translator would actually have to translate.

    Calibrated against two real false positives, both of which SHOULD be
    identical in all eight languages:

    * `{observed} mm (≥ {threshold} mm)` — placeholders, punctuation and a
      unit. Counting raw whitespace tokens flagged it in all seven files.
    * `notify.mobile_app_phone` — a Home Assistant service name shown as an
      example. Splitting on `.` and `_` turned one identifier into four
      "words".

    So: drop placeholders, then keep only whitespace tokens that are purely
    alphabetic once outer punctuation is trimmed (which excludes identifiers,
    numbers and entity ids) and longer than two characters (which excludes
    units like `mm` and articles).
    """
    words = []
    for token in _PLACEHOLDER.sub(" ", text).split():
        word = token.strip(".,;:!?()[]{}\"'“”„«»…-–—")
        if len(word) > 2 and all(c.isalpha() for c in word):
            words.append(word)
    return words


@pytest.mark.parametrize(("catalogue", "path"), list(_cases()))
def test_no_value_is_left_as_the_english_string(catalogue, path):
    """A copied-in English string is worse than a missing key.

    A missing key falls back to English *and* is caught by the test above; a
    copy looks translated and so never gets revisited. Only flags real prose —
    proper nouns, units and format strings legitimately match across languages.
    """
    en_data = _load(_CATALOGUES[catalogue] / "en.json")

    def walk(en_node, node, prefix=""):
        same = []
        if isinstance(en_node, dict) and isinstance(node, dict):
            for key, en_value in en_node.items():
                if key in node:
                    same += walk(en_value, node[key], f"{prefix}.{key}")
        elif isinstance(en_node, str) and en_node == node:
            if len(_prose_words(en_node)) >= 4:
                same.append(prefix)
        return same

    copies = walk(en_data, _load(path))
    assert not copies, (
        f"{path.name} has {len(copies)} value(s) identical to the English "
        f"text: {copies[:10]}"
    )


def _placeholders(data, prefix=""):
    """``{leaf path: set of named placeholders}`` for every string in a file."""
    found = {}
    if isinstance(data, dict):
        for key, value in data.items():
            found.update(_placeholders(value, f"{prefix}.{key}" if prefix else key))
    elif isinstance(data, str):
        found[prefix] = set(_NAMED_PLACEHOLDER.findall(data))
    return found


@pytest.mark.parametrize(("catalogue", "path"), list(_cases()))
def test_placeholders_match_the_english_string(catalogue, path):
    """A translation must carry the same named placeholders as its English text.

    Key parity (above) does not catch this: the key is present, the string looks
    fine, and the value the integration passes in simply never appears. A
    dropped `{path}` leaves a repair telling the user to open nothing; a typo
    like `{dashbords}` renders literally. Neither raises, and neither shows up
    in a diff review of a language nobody on the project reads.

    Only the English side is required to appear. A translation is free to use a
    placeholder more than once or reorder them, but not to invent or lose one.
    """
    english = _placeholders(_load(_CATALOGUES[catalogue] / "en.json"))
    translated = _placeholders(_load(path))

    mismatches = {
        key: (sorted(expected), sorted(translated[key]))
        for key, expected in english.items()
        if key in translated and translated[key] != expected
    }
    assert not mismatches, (
        f"{path.name} has {len(mismatches)} string(s) whose placeholders differ "
        f"from en.json, so a value the integration supplies will not be "
        f"substituted: {dict(list(mismatches.items())[:5])}"
    )
