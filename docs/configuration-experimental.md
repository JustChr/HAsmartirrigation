---
layout: default
title: "Configuration: Experimental"
---
# Experimental features

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Sensor group configuration](configuration-sensor-groups.md)<br/>
> Next: [Usage](usage.md)

The **Setup → Experimental** tab holds opt-in features that change how each zone's [bucket](how-it-works.md) is filled. They are **off by default** and still being refined, so turn them on one at a time and keep an eye on your zones — you can switch them back off at any time without losing data.

Both toggles are global (they apply to every zone) and take effect from the next calculation or watering event onward.

## Forecast-weighted durations

Normally, if you enable [*skip on forecasted precipitation*](configuration-when-to-water.md#skip-on-forecasted-precipitation), a run is either **fully skipped** (enough rain is coming) or **runs in full** (not enough). Forecast weighting adds a middle ground: instead of skipping, it waters **less**.

When enabled, at calculation time the upcoming precipitation — summed over the same [forecast look-ahead window](configuration-when-to-water.md#skip-on-forecasted-precipitation) you set under *When to Water* — is subtracted from the deficit used to compute the **duration**. The zone's actual bucket keeps the **true** deficit, so when the forecast rain falls it tops the bucket up the rest of the way. If the forecast rain misses, the next calculation/run simply makes up the difference.

**Example.** A zone has a 10 mm deficit and 4 mm of rain is forecast within the look-ahead window:

- Without weighting: the run delivers the full 10 mm (or, with *skip on precipitation* enabled and the threshold met, is skipped entirely).
- With weighting: the run delivers **6 mm** and stops. The bucket is left 4 mm short, which the forecast rain is expected to fill. If the rain doesn't come, the deficit is still there and the next run waters it.

Notes:

- **Requires a weather service** (the forecast comes from it). It has no effect for sensor-only setups.
- It works **alongside** the rain-skip guard. If *skip on forecasted precipitation* would skip the run outright, the skip still wins — weighting only matters for runs that aren't skipped.
- Because the bucket keeps the true deficit, this never double-counts the forecasted rain once it's actually collected.

## Credit bucket from observed watering

Smart Irrigation keeps its soil-moisture model honest by accounting for the water *it* applies. But if you water a zone by other means — a manual tap, a Home Assistant automation, your own schedule driving the valve — the integration normally doesn't know, and the bucket drifts from reality until the next weather calculation.

When enabled, Smart Irrigation watches each zone's [linked valve/switch entity](configuration-my-zones.md#linked-entity). Whenever that valve runs **outside** Smart Irrigation, the bucket is credited for the water applied. The amount is **estimated** from how long the valve ran and the zone's configured [throughput](configuration-my-zones.md#throughput) (`run time × throughput ÷ size`), so the zone needs both a linked valve and a throughput set.

Notes:

- Volume is **estimated from run time and throughput**, not measured by a flow meter. It's a model correction, not a billing-grade reading.
- Smart Irrigation's **own** runs are already accounted for and are never double-counted — only watering it didn't start is credited.
- External watering can push the bucket into surplus (capped at the zone's *maximum bucket*), since watering by hand can legitimately overshoot the deficit.
- Requires a linked valve **and** a throughput on the zone. Zones without both are ignored.

## Live-estimate run durations

By default, each zone's watering **duration** is fixed when the [daily calculation](how-it-works.md) runs — for example at 23:00 — which is correct *for the daily ledger* (the science needs a full day of weather). But the valve usually opens hours later, so the duration can be stale: overnight or early-morning evaporation isn't reflected in it.

When enabled, the duration is **recomputed at watering time** for scheduled runs from the same live intra-day deficit shown by each zone's *Live bucket* sensor (the drainage-aware ET and rainfall accumulated since the last calculation). A zone that dried out overnight waters a little longer; a zone that got intra-day rain waters less — and if the rain already covered it, that zone is skipped for that run.

**The daily bucket ledger is left exactly as-is** — only the duration of the run changes. The subtlety is avoiding a double-count: the live deficit can be deeper than the stored bucket because the intra-day ET hasn't been folded into the ledger yet. So after a live-estimate run, instead of forcing the bucket back to zero, Smart Irrigation **credits the water it actually delivered** (`run time × throughput ÷ size`, capped at *maximum bucket*). The leftover deficit therefore persists honestly, and when the next daily calculation subtracts the day's full ET it does so from a water-credited bucket — never subtracting the intra-day ET twice.

**Example.** Monday's calculation leaves a zone at −5 mm. Overnight, 3 mm of ET accrues, so by Tuesday's scheduled run the live deficit is −8 mm and the run delivers 8 mm. The bucket is credited to **+3 mm** (not 0). When Tuesday's calculation subtracts the day's full 8 mm ET, the +3 mm surplus cancels the overnight portion already watered, leaving the true −5 mm carryover — exactly right.

Notes:

- **Requires a weather service** (the live estimate comes from it). It has no effect for sensor-only setups.
- Affects **scheduled** runs only. *Irrigate now* and flow-meter zones are unchanged (flow-meter zones already deliver to a measured volume and credit the bucket from it).
- It does **not** add new runs: a zone the daily calculation decided not to water is not started by this feature; it only adjusts (or cancels) the runs that were already going to happen.

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Sensor group configuration](configuration-sensor-groups.md)<br/>
> Next: [Usage](usage.md)
