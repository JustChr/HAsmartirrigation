---
layout: default
title: Installation: Moving from Smart Irrigation to Irrigation Plus
---
# Moving from Smart Irrigation to Irrigation Plus

> Main page: [Installation](installation.md)

This integration used to be called **Smart Irrigation** and used the
`smart_irrigation` domain. It is now **Irrigation Plus**, on `irrigation_plus`.

If you are installing for the first time, none of this applies to you — go to
[Download](installation-download.md).

## Why

This project is a community fork of
[jeroenterheerdt/HAsmartirrigation](https://github.com/jeroenterheerdt/HAsmartirrigation).
It kept the original `smart_irrigation` domain, and so does the
[upstream project that is maintained again](https://github.com/altmenorg/HAsmartirrigation).
Two integrations claiming one domain cannot coexist: they install into the same
folder, produce the same entity IDs, and register the same Lovelace card type —
so whichever loaded second silently lost, with no error anywhere.
[Issue #120](https://github.com/JustChr/HAsmartirrigation/issues/120) asked us to
stop sharing it, and we agreed. Renaming was the fork's job, not theirs.

## Do this in the right order

**Add Irrigation Plus BEFORE you remove Smart Irrigation.**

This is the opposite of what most integration guides tell you, and it matters:

- Your **weather service API key** lives in Smart Irrigation's *config entry*,
  not in its storage file. Removing the integration through the Home Assistant
  UI deletes that entry, and the key with it.
- Removing it also **deletes its storage file** (`.storage/smart_irrigation.storage`),
  which is where your zones, buckets, schedules and run history live.
- Your **history and long-term statistics** can only be carried across while the
  old entity registry entries still exist.

Delete the folder if you like — that leaves the config entry intact. But do not
remove the integration from **Settings → Devices & Services** until the new one
is set up and you are happy with it.

If you already deleted the folder *and* removed the entry that then showed as
broken, your storage file is still on disk and Irrigation Plus will import it —
zones, buckets, schedules and history all come back.

**Your API key does not.** It lives only in Smart Irrigation's config entry, and
nothing else on your system holds a copy, so once that entry is gone the key is
gone with it. v2026.09.06 was meant to stage a copy into the storage file for
exactly this case and never actually wrote one ([#128]); that release is tagged
and cannot be corrected, and the domain it shipped under now belongs to the
upstream project again, so there is no version of this that recovers it. The
import will tell you which service needs its key re-entered, and everything else
comes across untouched.

This is why the order above is not a convenience — it is the only path that
keeps the key.

[#128]: https://github.com/JustChr/HAsmartirrigation/issues/128

### Keep the window short, and pause watering before you open it

The order above asks you to run both installs at once for a while. While you do,
they are two complete, independently scheduling irrigation controllers pointed at
the same valves, and they do not know about each other. The import copies the
storage file whole, so both hold the same zones, the same schedules and the same
linked entities; `zone_run_in_flight` resolves "is this zone already watering"
against each integration's own memory and its own storage file, and nothing in
the watering path asks about the other domain.

Three consequences, worst first:

- **A distributor loses its physical position.** An indexing valve advances one
  outlet per inlet pressurisation. Both installs sweep the same distributor and
  pulse the same shared inlet, so the ring ends up somewhere neither believes it
  is — while both go on reporting `synced`. This one compounds: every later cycle
  builds on the wrong position.
- **The pump.** The second install sees its own master flag as off, so with the
  kicker enabled it pulses the pump off and on again while the first one's valves
  are open. With `master_off_after` set, the mirror case: whichever cycle ends
  first switches the master off while the other is still watering, and that zone
  runs its remaining time against a dead pump — and books the water anyway.
- **The buckets, and not the way it looks.** Two runs of the same length starting
  together deliver one run's worth of water: the second `turn_on` is a no-op, and
  each store is individually right. The damage starts once they stop firing
  together, which they will — only clock- and sun-anchored schedules arm on the
  same second, while a finish-anchored one fires at `target − estimated duration`
  computed from each install's own state. Then the shorter run closes the valve
  while the longer one keeps crediting from its own clock, both stores read
  "satisfied", and the zone stayed dry. That failure is quiet: the next day shows
  no demand, so nothing corrects it.

**So pause watering on Smart Irrigation before you add Irrigation Plus.** On its
**Zones** page use **Pause watering → Delay 24 h**, or call
`smart_irrigation.set_rain_delay` with `hours` for longer. The pause is part of
the stored configuration, so the import copies it and **both** installs stay
held — and manual runs are deliberately exempt from it, so you can still test the
new install by hand while nothing waters on a schedule. Clear it when you are
done (step 8).

If you would rather not pause anything, keep both installed for minutes rather
than days, and do it at a time of day when no schedule can fire.

## Steps

1. **Pause watering on Smart Irrigation** — see the section above for why this
   matters more than it sounds like it does.
2. **Update through HACS as normal.** HACS reads the new domain from the
   manifest and installs into `custom_components/irrigation_plus/`.
3. **Restart Home Assistant.**
4. Go to **Settings → Devices & Services → Add Integration** and add
   **Irrigation Plus**.
5. The first step of the setup asks whether to **import your existing Smart
   Irrigation installation**. Say yes.
6. Check the panel: your zones, schedules, buckets and history should all be
   there. Compare it against the old one — in this session, not next week. (If
   the sidebar panel or the card looks stale, hard-reload the browser with
   Ctrl-Shift-R — that is a cached frontend, not a failed import.)
7. **Let the repair finish the job.** Once your zones are across, a repair
   appears under **Settings → System → Repairs** offering to remove the old
   installation for you. It removes the Smart Irrigation integration entry
   first, then deletes the leftover `custom_components/smart_irrigation/`
   folder — in that order, because Home Assistant can only shut the old
   integration down properly while its files are still present. It also takes
   the `smart_irrigation.*` service names back, which the old integration leaves
   registered behind it. Restart afterwards to clear the duplicate entities.

   The repair is only offered when the migration demonstrably worked (your
   zones are here) and the folder belongs to this project rather than to the
   upstream one. Otherwise you get an informational notice instead, and the
   manual route below.
8. **Clear the pause** from step 1 — **Resume** on the panel, or
   `irrigation_plus.clear_rain_delay`. Until you do, scheduled runs are skipped
   with a `paused` entry in the run log, which is easy to read as "the migration
   broke my watering".
9. **Or do it by hand**, instead of steps 7 and 8: remove the integration at
   **Settings → Devices & Services → Smart Irrigation → ⋮ → Delete**, then
   delete `custom_components/smart_irrigation/` and restart. HACS does not
   remove that folder when an integration changes folder, and Home Assistant
   will otherwise load it as a second integration — two of every sensor, and a
   second scheduler on your valves.

   **The restart is not optional on this route.** Removing a config entry does
   not unregister the services its integration declared, and the pre-rename
   release never removed its own, so all 24 `smart_irrigation.*` names stay
   registered until you restart — bound to an integration that is no longer
   there. The repair in step 7 clears them for you; doing it by hand does not.

## What is carried across automatically

| | |
|---|---|
| Zones, buckets, schedules, modules, sensor groups | ✅ imported |
| Run history and flow-learning state | ✅ imported |
| Weather service settings | ✅ imported |
| Your weather API key | ⚠️ only while the old config entry still exists — see [above](#do-this-in-the-right-order) |
| Recorded history (the graphs on each entity) | ✅ follows the new entity IDs |
| Long-term statistics | ✅ follows the new entity IDs |
| Zone device **area** assignments | ✅ copied onto the new devices |
| Lovelace cards using `custom:smart-irrigation-zones-card` | ✅ keep working; a repair offers to repoint them |
| `smart_irrigation.*` service calls in your automations | ⚠️ not while both are installed — see below |

A **safety copy** of your old storage file is written to
`.storage/smart_irrigation.storage.pre-irrigation_plus.bak` before anything
else. Keep it until you are satisfied; it is the only copy that survives step 7.

## What you have to change yourself

### Entity IDs

Every entity ID changed: `sensor.smart_irrigation_lawn` is now
`sensor.irrigation_plus_lawn`. History and statistics follow, but an entity ID
you have typed into **your own** automations, scripts, templates or dashboards
does not — and nothing in Home Assistant rewrites those. A template pointing at
an old ID quietly renders `unknown` rather than raising an error, which is why
this is worth doing deliberately rather than waiting to notice.

The exact old → new table for **your** install is written to
`irrigation_plus_renamed_entities.md` next to your `configuration.yaml`, and a
repair notice points at it. Work through it with a find-and-replace, then
dismiss the notice.

### Event names

Automations triggered by `smart_irrigation_start_irrigation_all_zones` (or any
other `smart_irrigation_*` event) will **not** fire any more. Rename the trigger
to `irrigation_plus_start_irrigation_all_zones`. Unlike services, events are not
aliased — a mirrored event would fire a second time on any machine where both
integrations are installed, which is the collision this rename removed.

### Service calls (eventually)

Once the old installation is gone, `smart_irrigation.reset_bucket` and every
other old service name works again: it forwards to
`irrigation_plus.reset_bucket` and logs a deprecation warning the first time it
is used. **This is a temporary compatibility layer and will be removed in a
future release**, so repoint your automations while you are already in there for
the entity IDs.

**While both installations are up, those names are not aliases at all.** An
alias can only claim a service name that is free, and the still-loaded old
integration owns all 24 of them — so nothing is aliased, and an automation
calling `smart_irrigation.run_zone` drives the **old** install and credits the
**old** copy of your data, not the one you are about to keep. That is another
reason to close the window in the same session rather than leave it open.

Which of the three you are in:

| While… | `smart_irrigation.run_zone` reaches… |
|---|---|
| both installations are up | the **old** integration, and its data |
| after the repair in step 7 | the alias, forwarding to `irrigation_plus.run_zone` |
| after the manual route in step 9, before restarting | nothing usable — the old names outlive the integration that declared them |

The aliases are switched off entirely if a different `smart_irrigation`
integration is installed alongside this one — that project owns those names, and
claiming them would recreate the original collision.

### Blueprints

The bundled valve blueprints are now installed to
`config/blueprints/script/irrigation_plus/`. The old copies in
`config/blueprints/script/smart_irrigation/` are left alone on purpose: any
script you already created from one is still backed by that file. You will see
both sets in the blueprint list until you delete the old folder, which is safe
to do once no script depends on it.

## Running both integrations side by side

That is now supported, and is the point of the rename. This means **a different
project** on the `smart_irrigation` domain — not the old copy of this one, which
is what the migration window above is about and which you should close promptly.
If you install the upstream `smart_irrigation` integration as well:

- The old Lovelace card type `custom:smart-irrigation-zones-card` belongs to
  **that** integration. Switch your cards to
  `custom:irrigation-plus-zones-card`; the repair notice will offer to do it.
- The `smart_irrigation.*` service aliases are not registered, so your
  automations must use `irrigation_plus.*`.

## If something went wrong

- **The panel is empty after importing.** Do not remove the old integration.
  Check the log for a line naming
  `.storage/smart_irrigation.storage.pre-irrigation_plus.bak` and
  [open an issue](https://github.com/JustChr/HAsmartirrigation/issues) with your
  diagnostics file — the backup still holds your configuration.
- **Two of every sensor.** The old `custom_components/smart_irrigation/` folder
  is still there. Delete it and restart — and treat it as urgent rather than
  cosmetic: two loaded installations also means two schedulers on your valves.
- **`smart_irrigation.*` services stopped working, and the old install is gone.**
  You took the manual route and have not restarted since. Restart; the
  compatibility aliases are registered on the next start.
- **A zone reads as watered but the ground is dry.** If both installations were
  up over a scheduled run, they overlapped on one valve and each credited its own
  bucket in full. Correct the affected zones with `irrigation_plus.set_bucket`,
  or reset them and let the next daily calculation rebuild from the weather.
- **Weather updates are switched off after importing.** The API key could not be
  recovered, because the old config entry was already gone when the import ran
  and that entry is the only place the key ever lived. The setup flow says so at
  the time, naming the service. Everything else imported: re-enter the key under
  **Setup → Weather service** and it resumes.
- **Graphs start from scratch on one or two entities.** The recorder rename is
  applied per entity and any that failed are named in the log. The integration is
  fine; only those entities' history stays under the old ID.
- **The card shows a config error.** A stale cached frontend. Hard-reload
  (Ctrl-Shift-R) or restart Home Assistant.

---

> Looking for the old **V1 (0.0.X) to V2** guide? It is still at
> [Migrating from V1 to V2](installation-migration.md).
