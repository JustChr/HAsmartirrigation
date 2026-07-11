"""No-demand run-log transparency (opt-in).

When ``Config.log_no_demand`` is on, a scheduled run that skips a zone/member
purely because it has no water demand records one ``skipped`` / ``no_demand``
run-log entry (deduped per zone per calendar day, suppressed under rain delay).
Coordinators are built with ``__new__`` like the other runner tests.
"""

import attr

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.store import Config


def test_config_defaults_log_no_demand_off():
    assert const.CONF_DEFAULT_LOG_NO_DEMAND is False
    field = attr.fields_dict(Config)["log_no_demand"]
    assert field.default == const.CONF_DEFAULT_LOG_NO_DEMAND
