---
layout: default
title: Configuration: Schedules
---
# Schedules

> Main page: [Configuration](configuration.md)<br/>
> Previous: [General configuration](configuration-general.md)

Recurring schedules let you irrigate your zones automatically on a repeating cadence — no Home Assistant automations needed. They live under **Setup → When to Water**.

Weather updates and duration calculations run on their own automatic times set in [General configuration](configuration-general.md#automatic-weather-data-update) — schedules here are about *when to actually water*.

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

### Time (HH:MM)
For daily, weekly, and monthly schedules, specify the time of day to run (24-hour format).

### Days of week (weekly only)
Select one or more days of the week the schedule should fire.

### Day of month (monthly only)
The day of the month (1–31) the schedule should fire.

### Interval (interval type only)
The number of hours between runs.

### What a schedule does
When a schedule fires it **irrigates**: it controls all [linked entities](configuration-zones.md#linked-entity) for the targeted zones that have a calculated duration > 0, and also fires the `smart_irrigation_start_irrigation_all_zones` event for any automation-based setups.

### Zones
Choose **All zones** or select specific zones by name. Only zones with a [linked entity](configuration-zones.md#linked-entity) and a calculated duration > 0 will actually open their valve.

### Enabled
Toggle a schedule on or off without deleting it. Disabled schedules are not tracked.

### Start date / End date (optional)
Limit the schedule to a date range. Leave empty for no restriction.

## Managing schedules

Each existing schedule is shown as a card with a summary of its settings. Use the **Edit** button to modify it or **Delete** to remove it.

## Tips

- Make sure your [automatic calculation time](configuration-general.md#automatic-duration-calculation) runs **before** your irrigate schedule, so each zone has an up-to-date duration when the schedule fires.
- For seasonal use, set a **start date** and **end date** so schedules only fire during your irrigation season.
- To adapt irrigation intensity over the year, adjust each zone's **multiplier** under Setup → My Zones (the old Seasonal Adjustments tab was removed in favor of this simpler approach).

> Main page: [Configuration](configuration.md)<br/>
> Previous: [General configuration](configuration-general.md)
