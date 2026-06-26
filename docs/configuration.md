---
layout: default
title: Configuration
---
# Configuration

You configure the integration from the Smart Irrigation panel in the Home Assistant sidebar. Make sure you [install](installation.md) it first.

![](assets/images/configuration-1.png)

## First-run setup wizard

The first time you open the panel — or any time via the **Setup wizard** button (top-right of the Setup tabs) — a guided wizard walks you through the four building blocks in order:

![](assets/images/setup-wizard-1.png)

1. **Weather** — pick a weather service (Open-Meteo needs no API key) or choose to use your own sensors.
2. **Module** — the calculation module that turns weather into an irrigation duration (PyETO by default).
3. **Sensor group** — where each weather value comes from (the chosen weather service, a sensor, a static value, or none).
4. **Zone** — your first irrigation zone, optionally linked to a switch/valve entity.

When you finish, the wizard creates a fully wired, ready-to-calculate zone. You can re-run it any time to add more, or configure everything manually using the tabs below.

## The panel layout

The panel has two top-level areas:

- **Zones** — the everyday **dashboard**. For each zone it shows at a glance whether it will water and why, plus one-tap **Update**, **Calculate** and **Irrigate now**. A gear icon on each card jumps to that zone's settings. See [Zones](configuration-my-zones.md).
- **Setup** — everything you configure once and rarely touch. The tabs are grouped around what you're trying to do rather than the internal data model, and the docs follow the same structure:
  1. [**Weather & Location**](configuration-weather-location.md) — your weather service and location coordinates, plus the weather forecast, per-source weather records and the seasonal outlook.
  2. [**My Zones**](configuration-my-zones.md) — add, edit and delete zones, link each to a switch/valve entity, and view each zone's calculation explanation.
  3. [**When to Water**](configuration-when-to-water.md) — the automatic update/calculation times, skip conditions, days between irrigation, zone sequencing, and [recurring schedules](configuration-schedules.md).
  4. **Advanced** — the raw [calculation modules](configuration-modules.md) (PyETO, Static, …) and [sensor groups](configuration-sensor-groups.md). Most setups never need to open these directly — the wizard wires them up for you.
  5. [**Experimental**](configuration-experimental.md) — opt-in features that change how the bucket is filled (crediting the bucket from observed watering, live-estimate watering). Off by default.
  6. **Help** — links to this documentation and the community/issue trackers.

Suggested reading order: [Weather & Location](configuration-weather-location.md) → [My Zones](configuration-my-zones.md) → [When to Water](configuration-when-to-water.md) → [Schedules](configuration-schedules.md) → [Modules](configuration-modules.md) and [Sensor groups](configuration-sensor-groups.md) if you need them. The [Experimental](configuration-experimental.md) features are optional extras you can explore once the basics work.