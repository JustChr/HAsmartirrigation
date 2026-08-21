---
layout: default
title: Configuration: Schedules
---
# Schedules

> Main page: [Configuration](configuration.md)<br/>
> Previous: [When to Water](configuration-when-to-water.md)<br/>
> Next: [Module configuration](configuration-modules.md)

Recurring schedules let you irrigate your zones automatically on a repeating cadence — no Home Assistant automations needed. They live at the bottom of the **Setup → When to Water** tab.

Weather updates and duration calculations run on their own automatic times set in [When to Water](configuration-when-to-water.md#automatic-weather-data-update) — schedules here are about *when to actually water*.

## Creating a schedule

Click **Add Schedule** to open the schedule dialog. Fill in the following fields:

### Name
A descriptive name for the schedule, e.g. "Daily morning irrigation".

### Recurrence

How often the schedule occurs. This is only about *how often* — where in the day the run lands is set by the Start and Finish rows below, so any recurrence can be combined with any time of day.

| Recurrence | Description |
|---|---|
| **Daily** | Occurs every day |
| **Weekly** | Occurs on selected days of the week |
| **Monthly** | Occurs on a specific day of the month |
| **Every N hours** | Occurs at a fixed interval (e.g. every 6 hours) |

### Days of week (weekly only)
Select one or more days of the week the schedule should fire. This works with a sun-based Start or Finish too, so "finish by sunrise, Mondays and Thursdays only" is a single schedule.

### Day of month (monthly only)
The day of the month (1–31) the schedule should fire.

### Interval (interval type only)
The number of hours between runs.

You can optionally set a **Start time** (`HH:MM`). With it, the interval is anchored to that clock time — it fires at the start time and every *N* hours after (e.g. start `07:00`, every `12` hours → 07:00 and 19:00 each day), and the dashboard shows the real next run. Leave it empty to keep the legacy behaviour, where the interval simply runs every *N* hours counting from when Home Assistant last started (no fixed clock phase, and the dashboard can't show a next run).

> **Note:** an *interval-irrigate* schedule waters the deficit the [daily calculation](configuration-when-to-water.md) produced. Because the calculation runs once a day, a second run a few hours later normally finds the bucket already satisfied and does little. To genuinely water more than once a day on intra-day demand, also enable the live-estimate option (see [Experimental](configuration-experimental.md)).

### Start and Finish {#time-anchor}

A run's window is two independent ends: when watering **may begin**, and when it **must be finished by**. Every recurrence except *interval* shows both rows, and each takes the same set of options:

| Option | Meaning |
|---|---|
| **No limit** | That end is unbounded |
| **At a time** | A clock time (24-hour format) |
| **At sunrise** | Sunrise, with an optional offset |
| **At sunset** | Sunset, with an optional offset |
| **At solar azimuth** | When the sun reaches a given compass angle (0–359°), with an optional offset |

**Offset** shifts a sun-based bound by a number of minutes, negative for before and positive for after (e.g. `-30` = half an hour before sunrise). Solar azimuth takes an angle in degrees instead.

At least one end must be set. A schedule with both rows on *No limit* describes no time at all and is rejected when you save it.

What the schedule does follows from which ends are bounded, and the dialog states it under each row as you build it:

- **Start only** — the run begins at that time and every due zone runs to completion.
- **Finish only** — the integration starts **early enough that watering ends at the target time**, using the estimated run length. *Finish by sunrise* is the classic lawn-watering pattern: evaporation loss is lowest and the grass dries during the day.
- **Both ends** — the run is **fitted** to the window. The finish is a hard deadline, zones are watered driest first, and any that don't fit are deferred to the next run rather than overrunning. A third row appears asking whether to water **as early** or **as late as possible** in the window; either way the finish is enforced.

Fitting is not a setting. It follows from having bounded both ends, because a window with a finish you are willing to overrun is just a later finish.

> **Which zones get deferred.** Zones are ranked by how dry they are relative to their own [minimum deficit to irrigate](configuration-my-zones.md), so the driest zone is served first regardless of where it sits in your zone list, and a zone skipped one night leads the next run. The driest zone always runs even if it alone overruns the window — the deadline cuts it short rather than excluding it, so it can never be starved.

### What a schedule does
When a schedule fires it **irrigates**: it controls all [linked entities](configuration-my-zones.md#linked-entity) for the targeted zones that have a calculated duration > 0, and also fires the `smart_irrigation_start_irrigation_all_zones` event for any automation-based setups.

### Zones
Choose **All zones** or select specific zones by name. Only zones with a [linked entity](configuration-my-zones.md#linked-entity) and a calculated duration > 0 will actually open their valve.

### Enabled
Toggle a schedule on or off without deleting it. Disabled schedules are not tracked.

### Start date / End date (optional)
Limit the schedule to a date range. Leave empty for no restriction.

## Managing schedules

Each existing schedule is shown as a card with a summary of its settings. Use the **Edit** button to modify it or **Delete** to remove it.

## Tips

- Make sure your [automatic calculation time](configuration-when-to-water.md#automatic-duration-calculation) runs **before** your irrigate schedule, so each zone has an up-to-date duration when the schedule fires. The default calculation time (23:00) pairs naturally with a *Finish by sunrise* schedule the next morning.
- For seasonal use, set a **start date** and **end date** so schedules only fire during your irrigation season.
- To adapt irrigation intensity over the year, adjust each zone's **multiplier** under Setup → My Zones (the old Seasonal Adjustments tab was removed in favor of this simpler approach).

> Main page: [Configuration](configuration.md)<br/>
> Previous: [When to Water](configuration-when-to-water.md)<br/>
> Next: [Module configuration](configuration-modules.md)
