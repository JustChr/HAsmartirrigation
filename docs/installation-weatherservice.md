---
layout: default
title: Installation: Configuring weather service
---
# Installation: Configuring weather service

> Main page: [Installation](installation.md)<br/>
> Previous: [Downloading the integration](installation-download.md)<br/>
> Next: [Configuration](configuration.md) or [Changing your settings for weather service](installation-options.md)

When you add the integration (**Settings → Devices & Services → Add Integration → Smart Irrigation**), a short two-step setup asks how you want to get weather data. You can change any of this later from the panel under **Setup → Weather & Location**.

## Step 1 — Do you want to use a weather service?

Give the integration a name and choose whether to **use a weather service**.

- **Leave it on** if you want the integration to pull weather data and/or forecasts from an online service. You'll pick the service in the next step.
- **Turn it off** if you want to rely entirely on your own sensors (configured later in a [sensor group](configuration-sensor-groups.md)). In that case there are no forecasts, so forecast-based features — the precipitation [skip condition](configuration-general.md#skip-conditions) and PyETO's *forecast days* — won't be available.

> If you use a weather service, make sure your Home Assistant **home-zone coordinates** are correct, as the data is fetched for that location. You can also set coordinates manually later in the panel.

## Step 2 — Pick a weather service

Three services are supported:

| Service | API key | Notes |
|---|---|---|
| **Open-Meteo** | **Not required** | Free, no sign-up — the easiest way to get started. |
| **Open Weather Map** | Required | Free tier available; see below. |
| **Pirate Weather** | Required | See below. |

Select a service and, for Open Weather Map or Pirate Weather, paste its API key (leave the key blank for Open-Meteo). If the key is valid you'll see a success message; if not, double-check it — newly created keys can take a while to activate.

After setup finishes, a **Smart Irrigation** panel appears in your sidebar. [Use it to configure your zones, sensor groups and modules](configuration.md).

## Getting an Open Weather Map API key

Create an account at [OpenWeatherMap](https://openweathermap.org). You need the **One Call API 3.0** plan (free for a limited number of calls per day, but it requires a card on file to activate). Then open **API keys** and copy your key. A new key can take a couple of hours to become active, so don't worry if it doesn't work immediately. To avoid any charge, set a call limit below the free threshold on the **Billing plans** page of your profile.

## Getting a Pirate Weather API key

Follow the instructions on the [Pirate Weather API docs](https://docs.pirateweather.net/en/latest/API/) (see the `API Key` section).

> Main page: [Installation](installation.md)<br/>
> Previous: [Downloading the integration](installation-download.md)<br/>
> Next: [Configuration](configuration.md) or [Changing your settings for weather service](installation-options.md)
