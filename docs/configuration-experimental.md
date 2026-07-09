---
layout: default
title: "Configuration: Experimental"
---
# Experimental features

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Sensor group configuration](configuration-sensor-groups.md)<br/>
> Next: [Distributors](configuration-distributors.md)

The **Setup → Experimental** tab holds opt-in features that are **off by default** and still being refined — turn them on one at a time and keep an eye on things; you can switch them back off at any time without losing data. Two change how each zone's [bucket](how-it-works.md) is filled; a third gates the experimental [mechanical water distributor](configuration-distributors.md) support.

The two bucket toggles are global (they apply to every zone) and take effect from the next calculation or watering event onward.

> **Looking for *forecast-weighted durations*?** That option moved out of this tab. It is now the **Water less** choice in the unified [*When rain is forecast*](configuration-when-to-water.md#when-rain-is-forecast) control under *Setup → When to Water*. The behaviour is unchanged.

## Credit bucket from observed watering

Smart Irrigation keeps its soil-moisture model honest by accounting for the water *it* applies. But if you water a zone by other means — a manual tap, a Home Assistant automation, your own schedule driving the valve — the integration normally doesn't know, and the bucket drifts from reality until the next weather calculation.

When enabled, Smart Irrigation watches each zone's [linked valve/switch entity](configuration-my-zones.md#linked-entity). Whenever that valve runs **outside** Smart Irrigation, the bucket is credited for the water applied. The amount is **estimated** from how long the valve ran and the zone's configured [throughput](configuration-my-zones.md#throughput) (`run time × throughput ÷ size`), so the zone needs both a linked valve and a throughput set.

Notes:

- Volume is **estimated from run time and throughput**, not measured by a flow meter. It's a model correction, not a billing-grade reading.
- Smart Irrigation's **own** runs are already accounted for and are never double-counted — only watering it didn't start is credited.
- External watering can push the bucket into surplus (capped at the zone's *maximum bucket*), since watering by hand can legitimately overshoot the deficit.
- Requires a linked valve **and** a throughput on the zone. Zones without both are ignored.

## Live-estimate watering

By default a zone waters **once a day**: the [daily calculation](how-it-works.md) runs — for example at 23:00 — produces a deficit, and the next scheduled run waters it off. That's correct for the daily ledger (the daily ET science needs a full day of weather), but it means a second scheduled run a few hours later finds the bucket already satisfied and does nothing. There is deliberately **no "calculate every N hours"** — daily ET0 can't be chopped into sub-daily pieces.

When enabled, each scheduled run instead **decides _and_ sizes itself from the live intra-day deficit** shown by each zone's *Live bucket* sensor (the drainage-aware ET and rainfall accumulated since the last calculation — computed with a valid *hourly* method). This means:

- a run can **start even when the once-daily bucket says "done"**, if intra-day ET has built a fresh deficit since the last calculation — so a zone on an *every-12-hours* [interval schedule](configuration-schedules.md) genuinely waters twice (morning deficit, then the daytime deficit), and
- a run **shrinks or cancels** when intra-day rain has already covered the zone.

The trigger honours each zone's **bucket threshold** (minimum deficit), so it won't churn out tiny runs — it only fires once the live deficit crosses that threshold.

**The daily bucket ledger is left exactly as-is** — only this run's start and duration come from the live estimate. The subtlety is avoiding a double-count: the live deficit can be deeper than the stored bucket because the intra-day ET hasn't been folded into the ledger yet. So after a live-estimate run, instead of forcing the bucket back to zero, Smart Irrigation **credits the water it actually delivered** (`run time × throughput ÷ size`, capped at *maximum bucket*). The leftover deficit therefore persists honestly, and when the next daily calculation subtracts the day's full ET it does so from a water-credited bucket — never subtracting the intra-day ET twice.

**Example (two runs in a day).** Monday's calculation leaves a zone at −5 mm. By the 07:00 run another 1 mm of ET has accrued (live deficit −6 mm) → it delivers 6 mm and the bucket is credited to **+1 mm**. By the 19:00 run the cumulative daytime ET is 5 mm, so the live deficit is now −4 mm → it delivers 4 mm and the bucket goes to **+5 mm**. At 23:00 the daily calculation subtracts the day's full ET; because the bucket only ever *banked* the water delivered (never had intra-day ET subtracted), the result lands on the true carryover — no double-count.

Notes:

- **Requires a weather service** (the live estimate comes from it). It has no effect for sensor-only setups.
- Affects **scheduled** runs only. *Irrigate now* and flow-meter zones keep the daily gate (flow-meter zones deliver to a measured volume and credit the bucket from it).
- **Keep `maximum bucket` ≥ roughly a day's ET** (the 24 mm default is fine). With several runs a day the stored bucket has to *bank* a full day's delivered water until the nightly calculation subtracts the day's ET once; if the maximum bucket is set very low, that banked water is clipped and the daily ledger can drift drier over time. Smart Irrigation logs a warning if you enable this with a small maximum bucket.
- Your stored **bucket** value will swing **positive** during the day (banked irrigation) before the nightly calculation pulls it back — that's expected; the *Live bucket* sensor shows the true intra-day deficit.

## Mechanical water distributors

Enables Smart Irrigation's support for a **mechanical pressure-distributor** (for example a Gardena Water Distributor) that splits one supply into several outlets. Turning it on reveals the **Distributors** setup tab and a per-zone **Water distributor** field; leaving it off keeps the feature entirely hidden. Unlike the bucket features above this does not change any calculation — it is a new, **experimental** capability that could not be fully hardware-tested, so treat it as a beta and watch the first days of use closely. Full details are on the **[Distributors](configuration-distributors.md)** page.

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Sensor group configuration](configuration-sensor-groups.md)<br/>
> Next: [Distributors](configuration-distributors.md)
