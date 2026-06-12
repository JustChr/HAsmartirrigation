---
layout: default
title: Usage: Valve Control & Automations
---
# Valve Control & Automations

> Main page: [Usage](usage.md)<br/>
> Previous: [Events](usage-events.md)<br/>
> Next: [Troubleshooting](usage-troubleshooting.md)

Smart Irrigation calculates *how long* to irrigate. You have two ways to act on that calculation:

## Option A — Linked entity (recommended, no automation needed)

Set a **linked switch or valve entity** directly on each zone in the [Zones tab](configuration-zones.md#linked-entity). The integration then controls the valve itself:

1. When an irrigation trigger fires (sunrise, schedule, or "Irrigate Now"), the integration calls `turn_on` on the linked entity.
2. It waits for the calculated duration (in seconds).
3. It calls `turn_off`.

No automation is needed. The integration also resets the bucket automatically after irrigation.

[Zone sequencing](configuration-general.md#zone-sequencing) (General Settings) controls whether multiple zones run **in parallel** (default) or **sequentially** one after another.

[Skip conditions](configuration-general.md#skip-conditions) (General Settings) let you automatically skip irrigation based on weather or a rain sensor — even in this mode.

### Irrigate Now

The **Zones dashboard** has a "Run all zones now" action that immediately irrigates all zones with linked entities, bypassing skip conditions, plus a per-zone **Irrigate Now** button on zones that have a linked entity and a calculated duration > 0.

---

## Option B — Automation-based (power users)

If you prefer full control via HA automations, leave the linked entity field empty on each zone. The integration fires the `smart_irrigation_start_irrigation_all_zones` [event](usage-events.md) when irrigation should start. Your automation listens for that event, reads `sensor.smart_irrigation_[zone_name]` for the duration, controls the valve, and calls `smart_irrigation.reset_bucket` when done.

> **Important:** Always call `smart_irrigation.reset_bucket` after irrigation so the integration knows irrigation happened and can reset the moisture deficit.

Experts recommend watering deeply but infrequently. Consider running automations that check both `sensor.smart_irrigation_[zone_name] > 0` and a day-of-week condition so you water once or twice per week rather than daily.

Check out the [blueprints](https://github.com/JustChr/HAsmartirrigation/tree/master/blueprints) for ready-made automation templates.

Also see [this discussion](https://github.com/JustChr/HAsmartirrigation/discussions/361) for an example using a timer helper for extra safety.

### Example 1: one valve, once per week

Runs daily, checks if it is Monday and duration > 0, or if the bucket < −25 mm.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/automations/1_one_valve_once_per_week.yaml)

### Example 2: one valve, potentially daily

Listens for `smart_irrigation_start_irrigation_all_zones`, checks `sensor.smart_irrigation_[zone_name] > 0`, turns on the valve, waits, turns off, resets bucket.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/automations/2_one_valve_potential_daily.yaml)

### Example 3: one valve, workday sensor

Like Example 2 but restricted to specific days using `binary_sensor.workday_sensor`.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/automations/3_one_valve_workday.yaml)

### Example 4: two valves, workday sensor

Two sequential valves on workdays.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/automations/4_two_valves_workday.yaml)

### Example 5: advanced multi-tap

Six-zone system controlled by ESPHome.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/automations/5_multi_tap.yaml)

> Main page: [Usage](usage.md)<br/>
> Previous: [Events](usage-events.md)<br/>
> Next: [Troubleshooting](usage-troubleshooting.md)
