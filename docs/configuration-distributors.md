---
layout: default
title: "Configuration: Distributors"
---
# Mechanical water distributors

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Experimental](configuration-experimental.md)<br/>
> Next: [Usage](usage.md)

A **mechanical water distributor** splits one water supply into several outlets and steps to the next outlet each time the water is pulsed **off and on again**. There is no electronics and no wiring per outlet — the pressure surge itself advances an internal wheel. The best-known consumer example is the **Gardena Water Distributor**; the professional equivalent is an indexing valve such as K-Rain or FIMCO.

Smart Irrigation drives one inlet valve (or pump) and waters each of the distributor's outlets in turn, so a handful of zones can share a single supply line and a single controllable valve. Because the device has **no position feedback** — it cannot tell you which outlet is currently open — Smart Irrigation *tracks* the position itself, counting each advance. Getting that tracking right is what most of this page is about.

> **Experimental.** This is a new feature that could **not be fully hardware-tested** before release. Enable it, but **watch the first days of use closely** and keep the device's **manual override** (its selector knob) within reach. It is opt-in and you can switch it back **off at any time** without losing data — see [Enabling it](#enabling-it).

## Enabling it {#enabling-it}

The distributor is an opt-in feature and is **off by default**. Turn it on under **Setup → Experimental → Mechanical water distributors** (see [Experimental](configuration-experimental.md)). Enabling it reveals two things that stay hidden otherwise:

- a new **Distributors** tab under **Setup**, where you create and commission distributors, and
- a **Water distributor** field on each zone's settings, where you assign that zone to an outlet.

Turn the toggle back off and both disappear again; any distributors and zone assignments you already made are kept, not deleted.

## Creating a distributor

On the **Distributors** tab, add a distributor, give it a **name**, and choose how its inlet is opened and closed:

- **Classic** — Home Assistant opens and closes an inlet `switch`/`valve`/`input_boolean` entity directly. Set the **Inlet valve / switch** to that entity. Each advance is a timed open-then-close pulse.
- **Self-closing service** — a device that closes itself after each pulse (for example a battery valve driven by a script). You provide a **Run script** (and optionally a **Stop script**); Smart Irrigation calls the run script to open the inlet for the configured time. Here the **Inlet valve / switch** field is *optional and watch-only* — it is read to keep the tracked position in sync (see [Watching the inlet](#watching-the-inlet-for-foreign-pulses)), never actuated.

Then set the **pulse duration** and its **unit** (seconds or minutes) — how long the inlet stays open to water an outlet before advancing. Give the distributor a supply with enough pressure and flow to actually step the wheel (see [Troubleshooting](#troubleshooting--tips)).

## Assigning zones to outlets

A distributor is only useful once zones are mapped onto its outlets. On a zone's settings, the **Water distributor** selector assigns that zone to this distributor. The distributor's outlets are numbered and arranged on the **Distributors** tab as a contiguous **1…n** map; the distributor page flags any gaps in that mapping.

A zone assigned to a distributor is a **member zone**: it is watered *through* its outlet, so its own linked valve and its own schedule are managed by the distributor rather than run independently. A member zone therefore does not need its own valve entity.

An outlet with **no mapped zone** is not watered — the distributor passes it with a short **skip pulse** (just long enough to advance the wheel) and moves on to the next mapped outlet.

## Commissioning & position tracking

Because the outlets are blind, Smart Irrigation infers the position instead of reading it. An **advance is counted on the inlet valve's off-edge** — every time the water is switched off, the internal wheel is assumed to have stepped by one. From a known starting outlet, counting off-edges keeps the tracked position aligned with the hardware.

To establish that known starting point and confirm the mapping, the Distributors tab gives you:

- **Test run** — waters each mapped outlet for about 30 seconds in order, so you can stand at the distributor, watch it step, and read off how long a pause it needs between outlets.
- **Set current outlet** — re-anchors the tracked position to the outlet you tell it. Use this after you have turned the device by hand. It asks for confirmation first, because it marks the distributor as synced.
- **Confirm commissioning** — arms the distributor for automatic cycles. Until you confirm, automatic watering through the distributor is held back.

If the tracked position ever becomes ambiguous — for example after an unexpected pulse or an interrupted cycle — the distributor is marked **uncertain** and will not run automatically until you **re-sync** it (test run, set the current outlet, confirm).

## Advance pause & skip pulses

Two timings control how the distributor steps:

- The **advance pause** is the gap between finishing one outlet and starting the next. It must be long enough for the device to physically complete its step; the backend enforces a **minimum of 10 seconds**. The test run helps you find the right value for your device.
- The **skip pulse** is the short on/off used to pass an unmapped outlet without watering it. It also has a **10-second floor**.

## Master valve / pump coordination

If you use a **master valve or pump**, Smart Irrigation switches it for the distributor's cycle. Two interactions are worth knowing:

- With **master off after each zone** under **sequential** or **rotating** [sequencing](configuration-when-to-water.md), the pump is switched **per outlet**, so expect it to cycle between every outlet of the distributor.
- A distributor feeds **one outlet at a time**. So even under **parallel** sequencing — where several ordinary zones open at once — a distributor's mapped zones still water **in sequence**. Plan the supply draw accordingly.

## Watching the inlet for foreign pulses

The inlet may sometimes be opened **outside** a Smart Irrigation run — a manual turn, a Home Assistant automation, or your own script. If the tracked position is to stay correct, Smart Irrigation needs to know how to react. The optional **inlet-watch** does this, with three **watch modes**:

- **Count it** — treat the foreign pulse as a real advance and step the tracked position with it.
- **Warn** — mark the position **uncertain** (re-sync required) rather than guessing. This is the safe choice when you are not sure a foreign pulse actually stepped the wheel.
- **Ignore** — do nothing.

Only pulses that Home Assistant can actually **see** are detected. A purely mechanical turn of the knob, with no entity change reported to Home Assistant, stays invisible — which is exactly why **Set current outlet** exists.

## Optional flow sensor

If you assign the distributor's shared inlet **flow meter**, each outlet's **delivered volume is measured** and credited to the zone's [bucket](how-it-works.md) instead of the time-based estimate. And where the inlet **can be stopped mid-pulse** — a classic inlet valve, or a self-closing device with a stop script — an outlet can also **stop early** once it has delivered its target volume.

**Caveat:** this flow-metering path is **rate-only** and, unlike the rest of the feature, could **not be hardware-tested** at all. Treat it as the least-proven part of an already-experimental feature: enable it if you have a flow sensor and want to try it, but keep an eye on the delivered volumes at first.

## Troubleshooting & tips

- **Give it pressure and flow.** A mechanical distributor needs a firm surge to advance reliably — aim for at least **1 bar** of pressure and **20 l/h** of flow at the inlet. Too weak a pulse and the wheel may not step, which desynchronises the tracked position.
- **Re-sync after turning it by hand.** If you move the device manually, use **Set current outlet** afterwards so the tracked position matches reality.
- **"Uncertain" means the position may be wrong.** Clear it by re-syncing: run the test run, set the current outlet to where the device actually is, and confirm commissioning.
- **Parallel sequencing still waters distributor zones in turn.** The distributor can only feed one outlet at a time, so its zones never water simultaneously even when parallel sequencing is on.

> Main page: [Configuration](configuration.md)<br/>
> Previous: [Experimental](configuration-experimental.md)<br/>
> Next: [Usage](usage.md)
