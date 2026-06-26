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

### Schedule type

| Type | Description |
|---|---|
| **Daily** | Runs every day at a specified time |
| **Weekly** | Runs on selected days of the week at a specified time |
| **Monthly** | Runs on a specific day of the month at a specified time |
| **Every N hours** | Runs at a fixed interval (e.g. every 6 hours) |
| **Sunrise** | Runs at sunrise (with an optional offset in minutes) |
| **Sunset** | Runs at sunset (with an optional offset in minutes) |
| **Solar azimuth** | Runs when the sun reaches a given compass angle (0–359°), with an optional offset — e.g. fire when the sun is due east |

### Time (HH:MM)
For daily, weekly, and monthly schedules, specify the time of day to run (24-hour format).

### Days of week (weekly only)
Select one or more days of the week the schedule should fire.

### Day of month (monthly only)
The day of the month (1–31) the schedule should fire.

### Interval (interval type only)
The number of hours between runs.

You can optionally set a **Start time** (`HH:MM`). With it, the interval is anchored to that clock time — it fires at the start time and every *N* hours after (e.g. start `07:00`, every `12` hours → 07:00 and 19:00 each day), and the dashboard shows the real next run. Leave it empty to keep the legacy behaviour, where the interval simply runs every *N* hours counting from when Home Assistant last started (no fixed clock phase, and the dashboard can't show a next run).

> **Note:** an *interval-irrigate* schedule waters the deficit the [daily calculation](configuration-when-to-water.md) produced. Because the calculation runs once a day, a second run a few hours later normally finds the bucket already satisfied and does little. To genuinely water more than once a day on intra-day demand, also enable the live-estimate option (see [Experimental](configuration-experimental.md)).

### Offset (sun-based types only)
Minutes to shift the run relative to the solar event — negative for before, positive for after (e.g. `-30` = half an hour before sunrise).

### Start or finish at that time? {#time-anchor}
For every type except *interval* you can choose what the configured time means:

- **Start** (default for clock-based types) — the run begins at the target time.
- **Finish** — the integration starts **early enough that watering ends at the target time**, using the current estimated total duration. Combined with the *Sunrise* type this gives the classic lawn-watering pattern: *finish watering right at sunrise*, when evaporation loss is lowest and the grass dries during the day.

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

- Make sure your [automatic calculation time](configuration-when-to-water.md#automatic-duration-calculation) runs **before** your irrigate schedule, so each zone has an up-to-date duration when the schedule fires. The default calculation time (23:00) pairs naturally with a *Sunrise + finish* schedule the next morning.
- For seasonal use, set a **start date** and **end date** so schedules only fire during your irrigation season.
- To adapt irrigation intensity over the year, adjust each zone's **multiplier** under Setup → My Zones (the old Seasonal Adjustments tab was removed in favor of this simpler approach).

> Main page: [Configuration](configuration.md)<br/>
> Previous: [When to Water](configuration-when-to-water.md)<br/>
> Next: [Module configuration](configuration-modules.md)
