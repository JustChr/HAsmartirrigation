---
layout: default
title: Usage: Events
---

# Events

> Main page: [Usage](usage.md)<br/>
> Previous: [Services](usage-services.md)<br/>
> Next: [Automations](usage-automations.md)

The integration fires the following Home Assistant events:

| Event | When it fires |
| --- | --- |
|`smart_irrigation_start_irrigation_all_zones`|When a [recurring schedule](configuration-schedules.md) with the irrigate action runs. The event carries the schedule name and the targeted zones. Listen to this event if you control your valves with your own [automations](usage-automations.md) instead of [linked entities](configuration-my-zones.md#linked-entity).|
|`smart_irrigation_recurring_schedule_triggered`|Whenever any recurring schedule fires (before the action runs); carries the schedule details.|
|`smart_irrigation_irrigation_started`|When a [self-closing](configuration-my-zones.md#watering-mode) zone starts a run (scheduled or manual). Carries the zone(s) with `zone_id`, `zone` (name) and `seconds`.|
|`smart_irrigation_irrigation_finished`|When a self-closing run completes. Carries the zone(s) with `zone_id`, `zone` and the resulting `bucket`.|
|`smart_irrigation_zone_problem`|When a self-closing zone's valve did not confirm open (e.g. the run service reported no state). Carries `zone_id`, `zone`, `entity_id` and a `reason`.|
|`smart_irrigation_zone_skipped`|When a zone is skipped on an automatic run because its [soil-moisture sensor](configuration-my-zones.md#soil-moisture-veto) reads wetter than the zone's threshold. Carries `zone_id`, `zone` (name), `entity_id` (the sensor), `reason` (`soil_moisture`), `observed` and `threshold`. The zone's bucket is reset to 0 at the same time. Listen to this to log/audit skips (e.g. write to InfluxDB).|

> The `irrigation_started` / `irrigation_finished` events let you drive a pump, a light or a notification from your own automation. If you only need a pump powered before watering, the built-in [pump / master switch](configuration-when-to-water.md#master-switch) usually removes the need for a custom automation.

> **Important:** the start event is fired **only by schedules** — if you have no irrigate schedule, it never fires. To reproduce the classic "irrigation finishes right at sunrise" behaviour, create a schedule of type **Sunrise** with the time anchor set to **Finish** (see [Schedules](configuration-schedules.md#time-anchor)); the schedule computes the start time from the estimated total duration for you.

Note that **Irrigate Now** (the dashboard button) does **not** fire the schedule event `smart_irrigation_start_irrigation_all_zones` — it actuates the zone directly. For a [self-closing](configuration-my-zones.md#watering-mode) zone it still fires `smart_irrigation_irrigation_started`, because that event tracks the *run*, not the schedule.

> Main page: [Usage](usage.md)<br/>
> Previous: [Services](usage-services.md)<br/>
> Next: [Automations](usage-automations.md)
