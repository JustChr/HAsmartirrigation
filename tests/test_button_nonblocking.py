"""The irrigation action buttons must fire-and-forget.

The per-zone "irrigate now" and the hub "irrigate all" buttons call
``async_irrigate_now``, which for a distributor member (or any run that touches a
distributor) drives a full ring cycle that can take minutes. Awaiting that in
``async_press`` blocked the button press the whole time. These pin the contract:
schedule the run as a background task and return immediately.
"""

import asyncio
from unittest.mock import AsyncMock, Mock

from custom_components.smart_irrigation import const
from custom_components.smart_irrigation.button import (
    SmartIrrigationIrrigateAllButton,
    SmartIrrigationZoneIrrigateNowButton,
)


def _hass_with_coord():
    hass = Mock()
    coord = Mock()
    coord.async_irrigate_now = AsyncMock()
    hass.data = {const.DOMAIN: {"coordinator": coord}}
    scheduled = []
    hass.async_create_task = Mock(
        side_effect=lambda coro: scheduled.append(asyncio.ensure_future(coro))
    )
    return hass, coord, scheduled


async def test_zone_irrigate_now_button_non_blocking():
    hass, coord, scheduled = _hass_with_coord()
    zone = {const.ZONE_ID: 7, const.ZONE_NAME: "Beet"}
    b = SmartIrrigationZoneIrrigateNowButton(hass, "button.si_beet_irrigate_now", zone)
    await b.async_press()
    hass.async_create_task.assert_called_once()  # scheduled, not awaited inline
    await asyncio.gather(*scheduled)
    coord.async_irrigate_now.assert_awaited_once_with("7")


async def test_irrigate_all_button_non_blocking():
    hass, coord, scheduled = _hass_with_coord()
    b = SmartIrrigationIrrigateAllButton(hass)
    await b.async_press()
    hass.async_create_task.assert_called_once()  # scheduled, not awaited inline
    await asyncio.gather(*scheduled)
    coord.async_irrigate_now.assert_awaited_once_with()
