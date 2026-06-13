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

Set a **linked switch or valve entity** directly on each zone in the [Zones tab](configuration-my-zones.md#linked-entity). The integration then controls the valve itself:

1. When a [recurring schedule](configuration-schedules.md) fires (or you press "Irrigate Now"), the integration calls `turn_on` on the linked entity.
2. It waits for the calculated duration (in seconds).
3. It calls `turn_off`.

No automation is needed. The integration also resets the bucket automatically after irrigation.

[Zone sequencing](configuration-when-to-water.md#zone-sequencing) (Setup → When to Water) controls whether multiple zones run **in parallel** (default) or **sequentially** one after another.

[Skip conditions](configuration-when-to-water.md#skip-conditions) (Setup → When to Water) let you automatically skip irrigation based on weather or a rain sensor — even in this mode.

### Irrigate Now

The **Zones dashboard** has a "Run all zones now" action that immediately irrigates all zones with linked entities, bypassing skip conditions, plus a per-zone **Irrigate Now** button on zones that have a linked entity and a calculated duration > 0.

---

## Option B — Automation-based (power users)

If you prefer full control via HA automations, leave the linked entity field empty on each zone and:

1. **Create an irrigate [schedule](configuration-schedules.md)** — the `smart_irrigation_start_irrigation_all_zones` [event](usage-events.md) is fired **by schedules**; without one, it never fires. For the classic "finish watering right at sunrise" pattern, use a **Sunrise**-type schedule with the time anchor set to **Finish**.
2. Your automation listens for that event, reads `sensor.smart_irrigation_[zone_name]` for the duration, controls the valve, and calls `smart_irrigation.reset_bucket` when done. (Zones without a linked entity are left alone by the schedule itself — your automation does the watering.)

Alternatively, skip the event entirely and trigger your automation on your own schedule (time trigger, workday sensor, …), using the duration sensor and bucket as conditions — see the examples below.

> **Important:** Always call `smart_irrigation.reset_bucket` after irrigation so the integration knows irrigation happened and can reset the moisture deficit.

Experts recommend watering deeply but infrequently. Consider running automations that check both `sensor.smart_irrigation_[zone_name] > 0` and a day-of-week condition so you water once or twice per week rather than daily.

Check out the [blueprints](https://github.com/JustChr/HAsmartirrigation/tree/master/blueprints) for ready-made automation templates.

## Notifications blueprint

A ready-made **Smart Irrigation Notifications** blueprint sends a push notification to your phone when a watering run **starts** or when a **zone fault** is detected (a valve that didn't open or a flow that never started — surfaced by the hub `binary_sensor.smart_irrigation_problem` sensor). Import it, pick the device to notify and the problem sensor, and you get one notification automation for the whole system; each notification type can be toggled independently.

[yaml](https://github.com/JustChr/HAsmartirrigation/blob/master/blueprints/automation/smart_irrigation_notify.yaml)

Also see [this discussion](https://github.com/jeroenterheerdt/HAsmartirrigation/discussions/361) (upstream) for an example using a timer helper for extra safety.

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
