"""Recurring schedules are irrigation-only, enforced on the way in.

The store never kept a schedule whose action was not ``irrigate``: ``async_load``
filtered them out on every load. Nothing on the write side applied that rule, so
one could be created, armed and run, and then vanish at the next restart with
nothing logged. The filter could not report what it dropped either, because it
ran on every load and could not tell a legacy row from one written a minute ago.

Rejection now happens where the write is applied, and the stored rows are
removed once by a latched repair that says what it removed. The tests below
cover both halves plus the two properties the repair shares with the solar
azimuth correction it is modeled on: it is idempotent, and a fresh install
latches the flag with nothing to repair.
"""

from unittest.mock import AsyncMock, Mock

import attr
import pytest

from custom_components.smart_irrigation import SmartIrrigationCoordinator, const
from custom_components.smart_irrigation.scheduler import RecurringScheduleManager
from custom_components.smart_irrigation.store import Config


def _sched(sid="s1", name="probe", action="irrigate"):
    """A start-anchored daily schedule, the shape the store keeps."""
    return {
        const.SCHEDULE_CONF_ID: sid,
        const.SCHEDULE_CONF_NAME: name,
        const.SCHEDULE_CONF_RECURRENCE: const.SCHEDULE_RECURRENCE_DAILY,
        const.SCHEDULE_CONF_START_MODE: const.SCHEDULE_BOUND_MODE_TIME,
        const.SCHEDULE_CONF_START_TIME: "22:00",
        const.SCHEDULE_CONF_FINISH_MODE: const.SCHEDULE_BOUND_MODE_NONE,
        const.SCHEDULE_CONF_ACTION: action,
        const.SCHEDULE_CONF_ZONES: "all",
        const.SCHEDULE_CONF_ENABLED: True,
    }


class _ConfigDocument:
    """In-memory stand-in with the store's evolve-and-return semantics."""

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self.writes = 0

    async def async_get_config(self):
        return attr.asdict(self.config)

    async def async_update_config(self, changes: dict):
        self.writes += 1
        valid = set(attr.fields_dict(Config).keys())
        self.config = attr.evolve(
            self.config, **{k: v for k, v in changes.items() if k in valid}
        )
        return attr.asdict(self.config)


@pytest.fixture
def coordinator(hass, mock_store):
    hass.data[const.DOMAIN] = {
        const.CONF_USE_WEATHER_SERVICE: False,
        const.CONF_WEATHER_SERVICE: None,
    }
    entry = Mock()
    entry.unique_id = "test_entry"
    entry.data = {}
    entry.options = {}
    coord = SmartIrrigationCoordinator(hass, None, entry, mock_store)
    coord.store = mock_store
    coord.get_total_irrigation_duration = AsyncMock(return_value=7200)
    return coord


class TestRejectionOnTheWayIn:
    @pytest.mark.parametrize("action", ["calculate", "update"])
    @pytest.mark.asyncio
    async def test_the_config_path_refuses_a_legacy_action(
        self, hass, coordinator, action
    ):
        """``coordinator.async_update_config`` is where the endpoint's write is
        applied, and where the value check belongs: every unlisted Config field
        reaches it through the schema's ``extra=vol.ALLOW_EXTRA``, so singling
        ``recurring_schedules`` out in the schema would reject legitimate
        payloads too."""
        store = _ConfigDocument()
        coordinator.store = store

        with pytest.raises(ValueError, match="irrigation-only"):
            await coordinator.async_update_config(
                {const.CONF_RECURRING_SCHEDULES: [_sched(action=action)]}
            )

        # Refused means not written, not written-then-complained-about.
        assert store.config.recurring_schedules == []

    @pytest.mark.asyncio
    async def test_the_config_path_still_accepts_irrigate(self, hass, coordinator):
        store = _ConfigDocument()
        coordinator.store = store
        await coordinator.async_update_config(
            {const.CONF_RECURRING_SCHEDULES: [_sched()]}
        )
        assert len(store.config.recurring_schedules) == 1

    @pytest.mark.asyncio
    async def test_a_missing_action_is_treated_as_irrigate(self, hass, coordinator):
        """The panel omits nothing, but a hand-written payload can. Defaulting
        to the one supported action keeps such a caller working rather than
        failing them for leaving out a field with only one legal value."""
        store = _ConfigDocument()
        coordinator.store = store
        bare = _sched()
        del bare[const.SCHEDULE_CONF_ACTION]
        await coordinator.async_update_config({const.CONF_RECURRING_SCHEDULES: [bare]})
        assert len(store.config.recurring_schedules) == 1

    @pytest.mark.parametrize("action", ["calculate", "update"])
    def test_schedule_save_refuses_a_legacy_action(self, hass, coordinator, action):
        """``_validate_schedule_data`` covers ``schedule_save``, which is the
        path ``async_create_schedule`` and ``async_update_schedule`` share."""
        mgr = RecurringScheduleManager(hass, coordinator)
        with pytest.raises(ValueError, match="irrigation-only"):
            mgr._validate_schedule_data(_sched(action=action))

    def test_schedule_save_accepts_what_the_panel_sends(self, hass, coordinator):
        """The panel and the setup wizard both hardcode ``irrigate`` and offer
        no action control, so validation must not be reachable from the UI.
        Pinned here against the exact shape the panel builds, since a validation
        error surfacing as a failed save in the panel would be a bad way to find
        out."""
        mgr = RecurringScheduleManager(hass, coordinator)
        # frontend emptySchedule(), verbatim.
        mgr._validate_schedule_data(
            {
                const.SCHEDULE_CONF_NAME: "",
                const.SCHEDULE_CONF_RECURRENCE: "daily",
                const.SCHEDULE_CONF_ENABLED: True,
                const.SCHEDULE_CONF_START_MODE: "time",
                const.SCHEDULE_CONF_START_TIME: "06:00",
                const.SCHEDULE_CONF_FINISH_MODE: "none",
                const.SCHEDULE_CONF_ACTION: "irrigate",
                const.SCHEDULE_CONF_ZONES: "all",
            }
        )
        # The setup wizard's payload, which builds its own dict rather than
        # calling emptySchedule() and so can drift from it independently.
        mgr._validate_schedule_data(
            {
                const.SCHEDULE_CONF_NAME: "Daily watering",
                const.SCHEDULE_CONF_RECURRENCE: "daily",
                const.SCHEDULE_CONF_START_MODE: "time",
                const.SCHEDULE_CONF_START_TIME: "06:00",
                const.SCHEDULE_CONF_FINISH_MODE: "none",
                const.SCHEDULE_CONF_ACTION: "irrigate",
                const.SCHEDULE_CONF_ZONES: "all",
                const.SCHEDULE_CONF_ENABLED: True,
            }
        )


class TestTheOneTimeRemoval:
    @pytest.mark.asyncio
    async def test_it_removes_legacy_rows_and_keeps_the_rest(self, hass, coordinator):
        store = _ConfigDocument(
            recurring_schedules=[
                _sched("s1", "keep me"),
                _sched("s2", "old calc", action="calculate"),
                _sched("s3", "old update", action="update"),
            ]
        )
        coordinator.store = store

        await coordinator.async_drop_legacy_schedule_actions()

        assert [
            s[const.SCHEDULE_CONF_ID] for s in store.config.recurring_schedules
        ] == ["s1"]
        assert store.config.legacy_schedule_actions_removed is True

    @pytest.mark.asyncio
    async def test_it_names_what_it_removed(self, hass, coordinator, caplog):
        """A silently dropped row is what made this invisible for so long. The
        user should be able to find out the schedule existed."""
        coordinator.store = _ConfigDocument(
            recurring_schedules=[_sched("s2", "nightly recalc", action="calculate")]
        )
        await coordinator.async_drop_legacy_schedule_actions()

        assert "nightly recalc" in caplog.text
        assert "calculate" in caplog.text

    @pytest.mark.asyncio
    async def test_a_stored_row_with_no_action_is_removed(self, hass, coordinator):
        """Deliberately not symmetric with the write path, which treats a
        missing action as irrigate.

        A stored row without an action is a legacy artefact that load has been
        discarding all along, so it has never watered. Reading it as irrigate
        here would turn it into a schedule that does, which is a run the user
        never configured. The write path has no such history: the only legal
        value is irrigate, so omitting the field is unambiguous.
        """
        bare = _sched("s2", "ancient")
        del bare[const.SCHEDULE_CONF_ACTION]
        store = _ConfigDocument(recurring_schedules=[_sched("s1"), bare])
        coordinator.store = store

        await coordinator.async_drop_legacy_schedule_actions()

        assert [
            s[const.SCHEDULE_CONF_ID] for s in store.config.recurring_schedules
        ] == ["s1"]

    @pytest.mark.asyncio
    async def test_it_is_idempotent(self, hass, coordinator):
        """Latched, so a second setup does not re-run it. The flag is the only
        thing standing between this and a repair that runs on every startup,
        which is the shape the load-time filter had."""
        store = _ConfigDocument(
            recurring_schedules=[
                _sched("s1"),
                _sched("s2", action="calculate"),
            ]
        )
        coordinator.store = store

        await coordinator.async_drop_legacy_schedule_actions()
        writes_after_repair = store.writes
        surviving = list(store.config.recurring_schedules)

        await coordinator.async_drop_legacy_schedule_actions()

        assert store.writes == writes_after_repair, "latched repair wrote again"
        assert store.config.recurring_schedules == surviving

    @pytest.mark.asyncio
    async def test_a_fresh_install_latches_with_nothing_to_repair(
        self, hass, coordinator
    ):
        store = _ConfigDocument()
        coordinator.store = store

        await coordinator.async_drop_legacy_schedule_actions()

        assert store.config.legacy_schedule_actions_removed is True
        assert store.config.recurring_schedules == []

    @pytest.mark.asyncio
    async def test_nothing_to_repair_does_not_rewrite_the_schedules(
        self, hass, coordinator
    ):
        """A store with only irrigate schedules should latch the flag without
        touching the list, so the repair cannot reorder or reshape rows it has
        no business changing."""
        original = [_sched("s1"), _sched("s2", "another")]
        store = _ConfigDocument(recurring_schedules=original)
        coordinator.store = store

        await coordinator.async_drop_legacy_schedule_actions()

        assert store.config.recurring_schedules is original


class TestTheStoreNoLongerFilters:
    @pytest.mark.asyncio
    async def test_load_keeps_what_is_stored(self, hass):
        """The filter has to go, or the repair can never see the rows it is
        meant to report: they would be gone before it looked."""
        from custom_components.smart_irrigation.store import async_get_registry

        reg = await async_get_registry(hass)
        # Straight to the store, the way the repair reads it back.
        await reg.async_update_config(
            {
                const.CONF_RECURRING_SCHEDULES: [
                    _sched("s1"),
                    _sched("s2", action="calculate"),
                ]
            }
        )
        cfg = await reg.async_get_config()
        assert len(cfg[const.CONF_RECURRING_SCHEDULES]) == 2

    def test_config_defaults_the_latch_to_false(self):
        """False is exactly the "not yet repaired" answer for every store
        written before this, which is why hydration is a .get default and
        STORAGE_VERSION does not move."""
        assert Config().legacy_schedule_actions_removed is False

    @pytest.mark.asyncio
    async def test_the_latch_round_trips_through_the_real_store(self, hass):
        """Not the mock: the migration filters ``data["config"]`` against
        ``attr.fields_dict(Config)``, so a key hydrated without an attribute is
        silently dropped on load."""
        from custom_components.smart_irrigation.store import async_get_registry

        reg = await async_get_registry(hass)
        await reg.async_update_config(
            {const.CONF_LEGACY_SCHEDULE_ACTIONS_REMOVED: True}
        )
        cfg = await reg.async_get_config()
        assert cfg[const.CONF_LEGACY_SCHEDULE_ACTIONS_REMOVED] is True
