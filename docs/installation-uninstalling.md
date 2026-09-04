---
layout: default
title: Installation: Uninstalling
---
# Uninstalling

> Main page: [Installation](installation.md)<br/>
> Previous: [Migrating from V1 to V2](installation-migration.md)

To remove Irrigation Plus from Home Assistant, go to Configuration > Integrations. In the Irrigation Plus card, click the button with the 3 dots, and click 'Delete'.

To remove all files, do the following:
* **If installed with HACS**: in the HACS panel, find Irrigation Plus. Click the button with the 3 dots and click 'Uninstall'.
* **If installed manually**: in the `custom_components` directory, remove the `irrigation_plus` folder.

If you used this integration before it was renamed, also check for a leftover
`custom_components/smart_irrigation/` folder — HACS does not remove it when an
integration changes folder. See
[Moving from Smart Irrigation to Irrigation Plus](installation-rename.md).

Restart HA to remove all traces of the integration from your sytem.

> Main page: [Installation](installation.md)<br/>
> Previous: [Migrating from V1 to V2](installation-migration.md)