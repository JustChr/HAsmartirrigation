"""The repair issue of a silent weather sensor, in Home Assistant's own issue
registry and over the integration's real store (#188): it clears when the sensor
reports again, it survives a restart in the middle of an outage, and it goes when
its sensor group is deleted."""

from datetime import timedelta

from homeassistant.const import (
    EVENT_HOMEASSISTANT_FINAL_WRITE,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import CoreState, callback
from homeassistant.helpers import issue_registry as ir

from custom_components.irrigation_plus import SmartIrrigationCoordinator, const
from custom_components.irrigation_plus.store import SmartIrrigationStorage

ENTITY = "sensor.station_temperature"
EVENT = f"{const.DOMAIN}_{const.EVENT_WEATHER_STALE}"
# One minute past the limit: the outage opens at the next check.
SILENCE = timedelta(seconds=const.SENSOR_STALE_AFTER_SECONDS + 60)


def _coordinator_over(hass, store):
    coord = SmartIrrigationCoordinator.__new__(SmartIrrigationCoordinator)
    coord.hass = hass
    coord.store = store
    return coord


async def _garden(hass):
    """A coordinator over a fresh real store with one sensor group reading ENTITY."""
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    group = await store.async_create_mapping(
        {
            const.MAPPING_NAME: "Garden",
            const.MAPPING_MAPPINGS: {
                const.MAPPING_TEMPERATURE: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: ENTITY,
                }
            },
        }
    )
    return _coordinator_over(hass, store), group[const.MAPPING_ID]


def _notice(hass, mapping_id):
    """The group's repair issue as Home Assistant shows it, or None."""
    issue = ir.async_get(hass).async_get_issue(
        const.DOMAIN, f"{const.ISSUE_WEATHER_SENSOR_STALE}_{mapping_id}"
    )
    return issue if issue is not None and issue.active else None


def _listen(hass):
    """Every irrigation_plus_weather_stale event, as (entity_id, stale)."""
    heard = []

    @callback
    def _on(event):
        heard.append((event.data["entity_id"], event.data["stale"]))

    hass.bus.async_listen(EVENT, _on)
    return heard


async def _silent_past_the_limit(hass, freezer, coord):
    """ENTITY reports once, then nothing for longer than the limit; one check."""
    hass.states.async_set(ENTITY, "21.5")
    freezer.tick(SILENCE)
    await coord.async_check_sensor_liveness()


async def test_the_notice_clears_when_the_sensor_reports_again(hass, freezer):
    coord, mapping_id = await _garden(hass)
    heard = _listen(hass)
    await _silent_past_the_limit(hass, freezer, coord)
    assert _notice(hass, mapping_id) is not None

    hass.states.async_set(ENTITY, "18.0")
    await coord.async_check_sensor_liveness()
    await hass.async_block_till_done()

    assert _notice(hass, mapping_id) is None
    assert heard == [(ENTITY, True), (ENTITY, False)]


async def test_the_notice_survives_a_restart_in_the_middle_of_an_outage(hass, freezer):
    coord, mapping_id = await _garden(hass)
    await _silent_past_the_limit(hass, freezer, coord)
    since = _notice(hass, mapping_id).translation_placeholders["since"]
    # A clean stop as Home Assistant runs it, with nothing saved by hand: what
    # reaches the disk is the store's pending write, flushed at FINAL_WRITE.
    hass.set_state(CoreState.stopping)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
    await hass.async_block_till_done()
    hass.set_state(CoreState.final_write)
    hass.bus.async_fire(EVENT_HOMEASSISTANT_FINAL_WRITE)
    await hass.async_block_till_done()
    hass.set_state(CoreState.running)

    # The restart. Home Assistant does not put a non-persistent issue back on
    # screen by itself, the station's entity comes back unavailable, and a new
    # store reads what the old one wrote.
    ir.async_delete_issue(
        hass, const.DOMAIN, f"{const.ISSUE_WEATHER_SENSOR_STALE}_{mapping_id}"
    )
    hass.states.async_set(ENTITY, "unavailable")
    store = SmartIrrigationStorage(hass)
    await store.async_load()
    after = _coordinator_over(hass, store)

    await after.async_setup_sensor_liveness()
    try:
        notice = _notice(hass, mapping_id)
        assert notice is not None
        assert notice.translation_placeholders["since"] == since
        # Still silent at the first check after the grace: same outage, same start.
        freezer.tick(timedelta(seconds=const.SENSOR_LIVENESS_STARTUP_GRACE_SECONDS))
        await after.async_check_sensor_liveness()
        notice = _notice(hass, mapping_id)
        assert notice is not None
        assert notice.translation_placeholders["since"] == since
    finally:
        after.async_teardown_sensor_liveness()


async def test_the_notice_goes_when_its_sensor_group_is_deleted(hass, freezer):
    coord, mapping_id = await _garden(hass)
    heard = _listen(hass)
    await _silent_past_the_limit(hass, freezer, coord)
    assert _notice(hass, mapping_id) is not None

    await coord.async_update_mapping_config(mapping_id, {const.ATTR_REMOVE: True})
    await hass.async_block_till_done()

    assert coord.store.get_mapping(mapping_id) is None
    assert _notice(hass, mapping_id) is None
    assert heard == [(ENTITY, True), (ENTITY, False)]


async def test_the_notice_goes_when_its_sensor_is_replaced(hass, freezer):
    coord, mapping_id = await _garden(hass)
    heard = _listen(hass)
    await _silent_past_the_limit(hass, freezer, coord)
    assert _notice(hass, mapping_id) is not None

    await coord.async_update_mapping_config(
        mapping_id,
        {
            const.MAPPING_MAPPINGS: {
                const.MAPPING_TEMPERATURE: {
                    const.MAPPING_CONF_SOURCE: const.MAPPING_CONF_SOURCE_SENSOR,
                    const.MAPPING_CONF_SENSOR: "sensor.new_station_temperature",
                }
            }
        },
    )
    await hass.async_block_till_done()

    assert _notice(hass, mapping_id) is None
    assert heard == [(ENTITY, True), (ENTITY, False)]
    assert coord.store.get_mapping(mapping_id)[const.MAPPING_SENSOR_OUTAGES] == []
