---
layout: default
title: Installation: Updating
---
# Updating

> Main page: [Installation](installation.md)<br/>
> Next: [Migrating from V1 to V2](installation-migration.md)

## Update to the latest version

- **Via HACS**: HACS notifies you when a new version is available. Click the notification and follow the prompts. You can also trigger a check manually via **HACS → Integrations → Smart Irrigation → ⋮ → Redownload**.
- **Manually**: Download the [latest release](https://github.com/JustChr/HAsmartirrigation/releases/latest) as a zip, extract `custom_components/smart_irrigation`, and overwrite the existing folder.

After updating, restart Home Assistant.

## Update to a specific version

- **Via HACS**: Use the `update.install` service:
  ```yaml
  service: update.install
  target:
    entity_id: update.smart_irrigation_update
  data:
    version: v2026.05.00
  ```
- **Manually**: Download the specific release zip from the [releases page](https://github.com/JustChr/HAsmartirrigation/releases) and overwrite as above.

After updating, restart Home Assistant.

## Verify the installed version

- **Backend version**: Settings → Devices & Services → Smart Irrigation → click the device → *Firmware version*
- **Frontend version**: visible in the top-right corner of the Smart Irrigation panel. If it doesn't match the backend, do a [hard refresh](https://refreshyourcache.com/en/cache/) in your browser to clear the cached bundle.

## Version scheme

This fork uses `vYYYY.MM.NN` — for example `v2026.05.00` = year 2026, May, first release of that month. The patch number (`NN`) increments for additional releases within the same month.

> Main page: [Installation](installation.md)<br/>
> Next: [Migrating from V1 to V2](installation-migration.md)
