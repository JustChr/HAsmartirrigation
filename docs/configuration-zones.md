---
layout: default
title: Configuration: Zones
---
# Zone configuration

> Main page: [Configuration](configuration.md)<br/>
> Previous: [General configuration](configuration-general.md)<br/>
> Next: [Module configuration](configuration-modules.md)

Specify one or more irrigation zones here. The integration calculates irrigation duration per zone, depending on size, throughput, state, [module](configuration-modules.md) and [sensor group](configuration-sensor-groups.md). A zone can be:
* **disabled**: The zone is then not calculated and duration will be set to 0.
* **automatic**: The zones duration is automatically calculated.
* **manual**: You can specify the zones duration yourself.

> When entering any values in the configuration of this integration, take notice of the labels provided so you enter values in the correct units.

## Where zones live: dashboard vs. settings

Zones appear in two places:

- The top-level **Zones** tab is the everyday **dashboard**. Each zone card shows an at-a-glance verdict (e.g. *"Watering needed: ~6 min"*, *"No watering needed"* or *"Turned off"*), a one-line status (bucket and when it was last checked), and the operational buttons **Update**, **Calculate** and **Irrigate now**. A gear icon on each card opens that zone's settings.
- **Setup → My Zones** is where you **add, configure and delete** zones, and view per-zone reporting (calculation explanation, weather data, watering calendar). The sections below ("Adding a zone", "Configuring a zone") all live here.

## Multi-zone support
For irrigation systems that have multiple zones which you want to run in series or independent you need to create multiple zones. The configuration should be done for each zone, including the area the zone covers and the corresponding settings.

## Adding a zone
Zones are added and configured under **Setup → My Zones**. Click the **+** button and provide:

- **Name**: The name of your zone, e.g. 'garden'
- **Size**: The size of this zone (m<sup>2</sup> or sq ft)
- **Throughput**: The flow of this zone (liter/minute or gallon/minute)

After clicking **Add**, the new zone appears in the list (and as an entity in Home Assistant). Expand its **Settings** to finish configuring it.

![](assets/images/configuration-zones-1.png)

## Actions on all automatic Zones
These bulk actions are split across the two surfaces:

- **Update all zones** / **Calculate all zones** — on the **Zones** dashboard (top tab): collect weather data for, and recalculate the duration of, every automatic zone.
- **Reset all buckets** / **Clear all weather data** — under **Setup → My Zones → Bulk Actions**: reset every automatic zone's bucket to `0`, or remove all collected weather data for the [sensor groups](configuration-sensor-groups.md) in use. Both ask for confirmation first.

## Configuring a zone
Open **Setup → My Zones**, expand a zone's **Settings**, and you can change:

- **Name**: change the name of a zone
- **Size**: change the size of a zone
- **Throughput**: change the throughput of a zone
- **Drainage rate**: set the drainage rate of a zone (mm/h or in/h). This is only applied when the bucket is above 0 (i.e. there is surplus moisture above field capacity). The full drainage rate only takes effect when the bucket is at its maximum value; below that it is applied as a fraction of the rate, following the hydraulic conductivity method of [Brooks and Corey, Eq. 4-6](https://open.library.okstate.edu/rainorshine/chapter/1-8-models-for-soil-hydraulic-conductivity/). New zones default to **20 mm/h** (a reasonable medium/loam soil value); existing zones keep whatever value they were created with. The right value depends heavily on your soil type — values quoted online (around 50.8 mm / 2 inch per hour) assume fully saturated soil and won't apply to most setups. Too low and a drainage problem isn't solved; too high and evapotranspiration has little impact. If you have drainage problems, adjust by ~5 mm/h every 24 hours until your area waters well without puddles forming.
- **State**:
  - _Automatic_: Automatic updating and calculation of that zone. [module](configuration-modules.md) and [sensor group](configuration-sensor-groups.md) is mandatory.
  - _Manual_: Only manual updating and calculation of that zone. No [module](configuration-modules.md) and [sensor group](configuration-sensor-groups.md) is required.
  - _Disabled_: The zone is disabled. No updating and calculation of that zone. Setting a [module](configuration-modules.md) and [sensor group](configuration-sensor-groups.md) on the zone is optional.
- **Module**: Choose the [calculation module](configuration-modules.md) that should be used to calculate irrigation for the zone.
- **Sensor group**: Choose the [sensor group](configuration-sensor-groups.md) that provides the weather data for this zone.
- **Bucket**: Either calculated or manually set. If `bucket >= 0` then no irrigation is necesarry, if `bucket < 0` irrigation is necessary. See [automations](usage-automations.md) for examples on how to use this value to decide to irrigate.
- **Maximum bucket**: You can manually set a maximum bucket size which represents the soil's water holding capacity. The maximum recommended bucket size is based on the type of soil:
    - clay soil: 30 mm (1.18")
    - sandy soil: 12 mm (0.47"). 
This recommendation is based on the soil water holding capacity. See [this discussion for more details](https://github.com/JustChr/HAsmartirrigation/discussions/448).

- **Lead time**: Time needed to warm up your irrigation system (in seconds), e.g. time to establish a connection, start a pump, build pressure, etc. After the duration is calculated, the lead time is added but only if the duration is > 0.
- **Maximum duration**: The maximum duration of the irrigation, to avoid flooding, wasting water, etc.
- **Multiplier**: Multiplies / divides the duration of the irrigation. For lawns, it is recommended to set the multiplier depending on your grass type (See [this discussion for more details](https://github.com/JustChr/HAsmartirrigation/discussions/448)):
    * Cool-reason grasses (such as fescue, bluegrass) should be set to `0.8`
    * Warm-season grasses (such as bermuda, zoysia) should be set to `0.7`. 
- **Duration**: Irrigation duration in seconds. Either calculated or manually set.

### Linked entity {#linked-entity}

Optionally link a Home Assistant `switch` or `valve` entity to a zone. When irrigation fires, the integration will:

1. Call `turn_on` on the entity
2. Wait for the calculated duration (in seconds)
3. Call `turn_off` on the entity

This means **no automation is needed** to control your valve — the integration does it directly. The [zone sequencing](configuration-general.md#zone-sequencing) setting in General controls whether multiple linked zones run in parallel or one after another.

> **Tip:** Start typing `switch.` or `valve.` in the field and all matching entities in your HA instance will appear as autocomplete suggestions.

If you prefer to keep using automations, simply leave this field empty. The integration will still fire the `smart_irrigation_start_irrigation_all_zones` event as usual.

### Available actions per zone

On the **Zones** dashboard, each zone card shows an at-a-glance verdict, a one-line status (bucket and when it was last checked), and the everyday action buttons:

![](assets/images/configuration-zones-2.png)

* **Update** — Collect weather data from the sensor group for the zone.
* **Calculate** — Recalculate the zone's irrigation duration. Weather data for the zone's sensor group is deleted after calculation.
* **Irrigate Now** — Immediately turn on the zone's [linked entity](#linked-entity) for the calculated duration, then turn it off. Bypasses all skip conditions. Shown disabled with a hint until the zone has a linked entity.

The remaining per-zone tools live under **Setup → My Zones**, in each zone's expandable panels:

* **Calculation explanation** — After a calculation, a detailed breakdown of how the bucket was updated and how the lead time and multiplier affected the final duration.
* **View weather data** — The last 10 weather data records for the zone's sensor group.
* **View watering calendar** — View a 12-month estimated watering calendar based on the zone's location and typical weather patterns.
* **Delete** — Remove the zone. 

> Main page: [Configuration](configuration.md)<br/>
> Previous: [General configuration](configuration-general.md)<br/>
> Next: [Module configuration](configuration-modules.md)
