---
layout: default
title: Live dashboard
---
# The Zones dashboard

> Main page: [Usage](usage.md)

The **Zones** tab is the everyday dashboard. For each zone it answers the daily question — *will it water, when, and if not, why?* — and offers one-tap actions. Full configuration lives under **Setup → Zones**; a gear icon on each card jumps there.

![](assets/images/usage-dashboard-1.png)

## Per-zone decision

Each card leads with a plain-language decision derived from the zone's state, its moisture balance and the next scheduled run:

- **Will water ~X at &lt;time&gt;** — a deficit exists and the next run will irrigate it.
- **Deficit ~X, but the next run will likely be skipped (…)** — a deficit exists, but a [skip condition](configuration-general.md#skip-conditions) will probably veto the run.
- **No watering needed** — the soil has enough moisture.
- **Deficit ~X — no schedule waters this zone; trigger manually** — there is a deficit but nothing scheduled targets the zone.
- **Turned off / Not calculated yet** — the zone is disabled, or hasn't been calculated yet.

The decision uses the same gate as the actual irrigation runner, so it will not promise watering that a skip condition would cancel.

## Outlook banner {#outlook-banner}

Above the zone cards, a banner summarises what happens next, globally:

- **Next run** — the next scheduled *irrigate* run, with its time, schedule name and target zones.
- **Skip preview** — whether that run will likely be skipped. When it will, tap **“Why?”** to expand the reasons (for example *Rain forecast — 8.6 mm ≥ 2 mm*). This is a forecast and may change before the run.
- If no schedule waters your zones, the banner says so and (in the admin panel) offers a link to set one up.

![](assets/images/usage-dashboard-3.png)

## Live estimate {#live-estimate}

The official **bucket** is recalculated once a day, at your [calculation time](configuration-general.md#automatic-duration-calculation). To give you a current picture in between, each zone also shows a small read-only **“Now ≈ −X mm (est.)”** chip next to the bucket — an estimate of how much the moisture balance has drifted **since the last calculation**.

![](assets/images/usage-dashboard-2.png)

- Where your weather service provides **hourly solar radiation** (e.g. Open-Meteo), it uses the dedicated **hourly** FAO-56 Penman-Monteith reference-ET equation — not the daily equation run more often. Hover/tap the chip to see which method was used and the “as of” time.
- Other providers fall back to an estimate based on the day's temperature range, distributed across the day by sun position.
- The estimate is **display-only**: it never changes the stored bucket or the watering decision, and it is anchored to the last calculation so it does not double-count. See [How it works](how-it-works.md#live-status-estimate).

## Actions

For automatic zones, each card offers **Update** (fetch the latest weather/sensor data), **Calculate** (recompute the watering duration), and **Irrigate now** (open the linked valve immediately — this **bypasses skip conditions**). A run-all row at the top applies the same actions to every zone at once.

## A card for non-admin users

The panel itself is admin-only, but you can put the same everyday view on any dashboard with the shipped **[Lovelace card](usage-lovelace-card.md)** so non-admin household members can see status and water on demand.

> Main page: [Usage](usage.md)
