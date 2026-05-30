---
layout: default
title: Installation: Download
---
# Installation: Download

> Main page: [Installation](installation.md)<br/>
> Next: [Set up weather service](installation-weatherservice.md)

## Using HACS (recommended)

This integration is not in the default HACS catalogue. You need to add it as a custom repository first:

1. In Home Assistant, open **HACS → Integrations**
2. Click the **⋮** menu (top right) → **Custom repositories**
3. Enter `https://github.com/JustChr/HAsmartirrigation` and choose category **Integration**
4. Click **Add**, then search for **Smart Irrigation** and install it

## Manual installation

1. Download the [latest release](https://github.com/JustChr/HAsmartirrigation/releases/latest) as a `.zip` file
2. Extract the `custom_components/smart_irrigation` folder from the archive
3. Copy it into the `custom_components` folder of your Home Assistant configuration directory

## After installing

1. Restart Home Assistant to load the integration
2. Go to **Settings → Devices & Services → Add Integration**
3. Search for **Smart Irrigation** and click to add it
4. Follow the wizard — the first step is [setting up a weather service](installation-weatherservice.md)

> Main page: [Installation](installation.md)<br/>
> Next: [Set up weather service](installation-weatherservice.md)
