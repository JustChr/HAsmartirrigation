---
layout: default
title: Configuration: General
---
# General configuration

> Main page: [Configuration](configuration.md)<br/>
> Next: [Zone configuration](configuration-zones.md)

This page covers the global, set-once settings. In the panel they are spread across two Setup tabs grouped by purpose:

- **Weather & Location** — your weather service and location coordinates (see [weather service setup](installation-weatherservice.md)).
- **When to Water** — the automatic update/calculation times, days between irrigation, [zone sequencing](#zone-sequencing), [skip conditions](#skip-conditions), and [recurring schedules](configuration-schedules.md).

The settings below are documented together by topic.

### Automatic weather data update
If enabled, specify how often sensor update should happen (minutes, hours, days). You can also set up an update delay to be used to delay the first update. THis is useful in case your sensors do not provide a value immediately after Home Assistant starts.

As calculation needs weatherdata make sure to update your weather data at least once before calculating.

### Automatic duration calculation
If enabled, set the time of calculation (HH:MM). Calculation uses weatherdata that is collected in updates to determine irrigation duration. After automatic calculation has happened used weatherdata is deleted.

> **Note:** weather data is now pruned **automatically**. Each zone consumes the weather data it needs during calculation, and old readings are pruned from the shared buffer once every zone that needs them has consumed them (with a hard cap of a few days). There is no longer a "pruning time" to configure, and the old timed *auto-clear* setting has been removed. You can still wipe everything manually via **Setup → My Zones → Bulk Actions → Clear all weather data**.

### Days between irrigation events
Configure the minimum number of days that must pass between irrigation events. This setting allows you to control how frequently irrigation can occur, which is useful for:
* **Water conservation**: Ensure adequate time between watering sessions
* **Plant health**: Allow soil to partially dry between irrigations
* **Local restrictions**: Comply with watering schedules or restrictions

**How it works:**
* **Default value**: 0 (no restriction - maintains current behavior)
* **Range**: 0-365 days
* When set to 0: Irrigation events can fire daily if conditions are met (default behavior)
* When set to a value > 0: Irrigation events will only fire if the specified number of days have passed since the last irrigation event

**Example scenarios:**
* Set to 1: Allow irrigation every other day maximum
* Set to 3: Allow irrigation only every 3 days minimum  
* Set to 7: Weekly irrigation maximum

The system automatically tracks the number of days since the last irrigation event. If an irrigation trigger occurs but insufficient days have passed, the event is skipped and the days counter continues to increment. When enough days have passed, the next trigger will fire the irrigation event and reset the counter.

This feature works alongside existing precipitation forecasting - if both restrictions apply, both must be satisfied for irrigation to occur.

### Zone sequencing

When multiple zones have a [linked entity](configuration-zones.md#linked-entity) configured and irrigation fires, this setting controls whether they run at the same time or one after another.

- **Parallel** (default): all linked entities open simultaneously. Each closes after its own calculated duration.
- **Sequential**: zones run one after another. The integration waits for each zone to finish before starting the next. Zones with 0 seconds calculated duration are skipped automatically.

### Skip Conditions

These settings let you automatically skip irrigation when conditions are unfavourable. All checks are independent — any one of them can veto an irrigation event.

#### Skip on forecasted precipitation
If enabled, irrigation is skipped when the **total** forecasted precipitation across the look-ahead window exceeds the configured threshold (default 2 mm). Requires a weather service to be configured.

- **Forecast look-ahead (days)** — how many upcoming forecast days are added together for this check. The forecast starts at *tomorrow* (today is excluded), so `1` (the default) means just the next day, `2` the next two days, and so on.
- **Upgrade note:** before `v2026.06.13` this window was hard-wired to two days. The default is now **1 day**, so an existing install will skip less aggressively than before. If you preferred the old behaviour, set the look-ahead back to `2`.

![](assets/images/configuration-general-skip-1.png)

#### Skip on low temperature
If enabled, irrigation is skipped when the current temperature (from the weather service) is below the configured threshold (in °C). Useful for avoiding irrigation in near-freezing conditions.

- Default threshold: 5 °C
- Requires a weather service to be configured.

#### Skip on high wind speed
If enabled, irrigation is skipped when the current wind speed (from the weather service) is above the configured threshold (in m/s). Useful for avoiding evaporation or drift in windy conditions.

- Default threshold: 6.9 m/s (≈ 25 km/h)
- Requires a weather service to be configured.

#### Rain sensor
Optionally specify a `binary_sensor` entity. If that sensor is `on` when irrigation would normally fire, the event is skipped. No weather service is required for this check — it works with any binary sensor (e.g. a physical rain detector, a virtual sensor from a weather integration).

Leave this field empty to disable the rain sensor check.

### Unit System Responsiveness
Smart Irrigation automatically detects and responds to changes in your Home Assistant unit system setting (metric/imperial). When you change the unit system in Home Assistant:
* All sensor entities immediately update to display values in the new units
* The web interface refreshes to show measurements in the correct units  
* Stored configurations like precipitation thresholds maintain their values but display in appropriate units
* No restart or integration reload is required

This ensures seamless transitions between unit systems without losing your configuration data.


> Main page: [Configuration](configuration.md)<br/>
> Next: [Zone configuration](configuration-zones.md)
