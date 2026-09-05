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
broken, your storage file is still on disk and Irrigation Plus will import it.
Your API key comes back too, as long as Home Assistant ran **v2026.09.06** at
least once — that release copied it into the storage file for exactly this case.

## Steps

1. **Update through HACS as normal.** HACS reads the new domain from the
   manifest and installs into `custom_components/irrigation_plus/`.
2. **Restart Home Assistant.**
3. Go to **Settings → Devices & Services → Add Integration** and add
   **Irrigation Plus**.
4. The first step of the setup asks whether to **import your existing Smart
   Irrigation installation**. Say yes.
5. Check the panel: your zones, schedules, buckets and history should all be
   there. Compare it against the old one before going any further. (If the
   sidebar panel or the card looks stale, hard-reload the browser with
   Ctrl-Shift-R — that is a cached frontend, not a failed import.)
6. **Let the repair finish the job.** Once your zones are across, a repair
   appears under **Settings → System → Repairs** offering to remove the old
   installation for you. It removes the Smart Irrigation integration entry
   first, then deletes the leftover `custom_components/smart_irrigation/`
   folder — in that order, because Home Assistant can only shut the old
   integration down properly while its files are still present. Restart
   afterwards.

   The repair is only offered when the migration demonstrably worked (your
   zones are here) and the folder belongs to this project rather than to the
   upstream one. Otherwise you get an informational notice instead, and the
   manual route below.
7. **Or do it by hand**, if you would rather: remove the integration at
   **Settings → Devices & Services → Smart Irrigation → ⋮ → Delete**, then
   delete `custom_components/smart_irrigation/` and restart. HACS does not
   remove that folder when an integration changes folder, and Home Assistant
   will otherwise load it as a second integration — you would see two of every
   sensor.

## What is carried across automatically

| | |
|---|---|
| Zones, buckets, schedules, modules, sensor groups | ✅ imported |
| Run history and flow-learning state | ✅ imported |
| Weather service settings **and your API key** | ✅ imported |
| Recorded history (the graphs on each entity) | ✅ follows the new entity IDs |
| Long-term statistics | ✅ follows the new entity IDs |
| Zone device **area** assignments | ✅ copied onto the new devices |
| Lovelace cards using `custom:smart-irrigation-zones-card` | ✅ keep working; a repair offers to repoint them |
| `smart_irrigation.*` service calls in your automations | ✅ keep working, for now — see below |

A **safety copy** of your old storage file is written to
`.storage/smart_irrigation.storage.pre-irrigation_plus.bak` before anything
else. Keep it until you are satisfied; it is the only copy that survives step 6.

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

`smart_irrigation.reset_bucket` and every other old service name still works: it
forwards to `irrigation_plus.reset_bucket` and logs a deprecation warning the
first time it is used. **This is a temporary compatibility layer and will be
removed in a future release**, so repoint your automations while you are already
in there for the entity IDs.

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

That is now supported, and is the point of the rename. If you install the
upstream `smart_irrigation` integration as well:

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
  is still there. Delete it and restart.
- **Weather updates are switched off after importing.** The API key could not be
  recovered — the old config entry was already gone and the storage file held no
  copy of it (installs that never ran v2026.09.06 have none). Everything else
  imported: re-enter the key under **Setup → Weather service** and it resumes.
- **Graphs start from scratch on one or two entities.** The recorder rename is
  applied per entity and any that failed are named in the log. The integration is
  fine; only those entities' history stays under the old ID.
- **The card shows a config error.** A stale cached frontend. Hard-reload
  (Ctrl-Shift-R) or restart Home Assistant.

---

> Looking for the old **V1 (0.0.X) to V2** guide? It is still at
> [Migrating from V1 to V2](installation-migration.md).
