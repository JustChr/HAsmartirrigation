"""Shipped self-closing valve script blueprints are well-formed and render."""

import json
from pathlib import Path

import yaml

import custom_components.irrigation_plus as si

BP_DIR = Path(si.__file__).parent / "blueprints" / "script"
NAMES = ("tuya_z2m_valve.yaml", "sonoff_z2m_valve.yaml", "entity_valve.yaml")


class _BlueprintLoader(yaml.SafeLoader):
    """SafeLoader that tolerates the blueprint `!input` tag."""


_BlueprintLoader.add_constructor(
    "!input", lambda loader, node: {"__input__": loader.construct_scalar(node)}
)


def _load(name):
    with open(BP_DIR / name, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=_BlueprintLoader)


def test_all_three_blueprints_present():
    for name in NAMES:
        assert (BP_DIR / name).is_file(), name


def test_blueprints_are_script_blueprints_with_duration():
    for name in NAMES:
        data = _load(name)
        assert data["blueprint"]["domain"] == "script"
        assert data["blueprint"]["input"], f"{name}: empty input"
        assert "duration" in data.get("fields", {}), f"{name}: no duration field"
        assert data.get("sequence"), f"{name}: no sequence"


def test_mqtt_blueprints_publish():
    for name in ("tuya_z2m_valve.yaml", "sonoff_z2m_valve.yaml"):
        text = (BP_DIR / name).read_text(encoding="utf-8")
        assert "mqtt.publish" in text, name


def test_entity_blueprint_sets_countdown_and_toggles():
    text = (BP_DIR / "entity_valve.yaml").read_text(encoding="utf-8")
    assert "number.set_value" in text
    assert "homeassistant.turn_on" in text
    assert "homeassistant.turn_off" in text


async def test_the_duration_expression_survives_a_stop_call(hass):
    """A stop reaches these scripts with no `duration` at all — reported by
    @pnaklicki on #83.

    `duration | int(0)` looks like it defaults, but `int`'s fallback only
    catches a value that cannot be converted; an unset variable raises before
    the filter runs. The `default: 0` under `fields:` is no help either — Home
    Assistant builds the UI form from it and never injects it into the script's
    variables. So the script errored instead of closing the valve, and because
    the service call is not blocking that showed up only in the log while the
    run was settled as stopped.
    """
    from homeassistant.helpers.template import Template

    for name in NAMES:
        expr = _load(name)["sequence"][0]["variables"]["dur"]
        # The open still works...
        assert Template(expr, hass).async_render({"duration": 600}) == 600
        # ...and the stop, which passes nothing, must yield 0 rather than raise.
        assert Template(expr, hass).async_render({}) == 0, name


def test_the_duration_expression_does_not_rely_on_int_s_fallback(hass):
    """Pin the idiom itself, since the failure is invisible in a rendered open.

    Any future edit back to `duration | int(0)` re-breaks stopping, and every
    test that renders WITH a duration would still pass.
    """
    for name in NAMES:
        expr = _load(name)["sequence"][0]["variables"]["dur"]
        assert "default(0)" in expr.replace(" ", ""), name


async def test_tuya_payload_templates_render(hass):
    """The Tuya open payloads (variable JSON key) render to valid JSON."""
    from homeassistant.helpers.template import Template

    countdown = Template("{{ {ckey: dur} | to_json }}", hass).async_render(
        {"ckey": "countdown_l1", "dur": 5}, parse_result=False
    )
    assert json.loads(countdown) == {"countdown_l1": 5}

    valve = Template("{{ {vkey: oval} | to_json }}", hass).async_render(
        {"vkey": "valve_l1", "oval": "on"}, parse_result=False
    )
    assert json.loads(valve) == {"valve_l1": "on"}


async def test_sonoff_payload_template_renders(hass):
    """The SONOFF nested cyclic_timed_irrigation payload renders to valid JSON."""
    from homeassistant.helpers.template import Template

    tpl = (
        "{{ {'cyclic_timed_irrigation': {'current_count': 0, 'total_number': 1, "
        "'irrigation_duration': dur, 'irrigation_interval': 0}} | to_json }}"
    )
    out = json.loads(Template(tpl, hass).async_render({"dur": 42}, parse_result=False))
    assert out["cyclic_timed_irrigation"]["irrigation_duration"] == 42
    assert out["cyclic_timed_irrigation"]["total_number"] == 1
