---
layout: default
title: Usage: Entities
---
# Entities

> Main page: [Usage](usage.md)<br/>
> Next: [Services](usage-services.md)

## Devices

Smart Irrigation creates one **hub device** ("Smart Irrigation") and one **device per zone**, named after the zone (e.g. a zone called *Lawn* becomes a device called **Lawn**). Each zone device hangs off the hub device, and all of a zone's entities are grouped under it.

Entity **names** follow Home Assistant's `has_entity_name` convention: the friendly name is the device name plus the entity descriptor, e.g. **Lawn Duration**, **Lawn Bucket**, **Lawn Live bucket**. The descriptors are translated into all supported languages.

## Zone entities

For a zone called *Lawn*, the following entities are created (entity IDs shown for the default install):

| Entity | Name | Entity ID |
| --- | --- | --- |
| Irrigation duration (the headline sensor) | Lawn Duration | `sensor.smart_irrigation_lawn` |
| Water balance "bucket" (mm/inch) | Lawn Bucket | `sensor.smart_irrigation_lawn_bucket` |
| Intra-day live estimate of the bucket | Lawn Live bucket | `sensor.smart_irrigation_lawn_live_deficit` |
| Net daily change applied to the bucket | Lawn Bucket delta | `sensor.smart_irrigation_lawn_et` |
| Last irrigation (timestamp) | Lawn Last irrigation | `sensor.smart_irrigation_lawn_last_irrigation` |
| Next scheduled irrigation (timestamp) | Lawn Next irrigation | `sensor.smart_irrigation_lawn_next_irrigation` |
| Irrigation multiplier (adjustable) | Lawn Multiplier | `number.smart_irrigation_lawn_multiplier` |
| Would the zone water now? | Lawn Irrigation needed | `binary_sensor.smart_irrigation_lawn_irrigation_needed` |
| Linked valve/switch currently running | Lawn Watering now | `binary_sensor.smart_irrigation_lawn_watering_now` |
| Irrigate this zone immediately | Lawn Irrigate now | `button.smart_irrigation_lawn_irrigate_now` |

A few **diagnostic** sensors (Last calculated, Last weather update, Weather data points, Drainage) are also created but **disabled by default** — enable them from the device page if you want them.

> The internal entity ID suffixes are kept stable for backwards compatibility, so they don't always match the new display names (e.g. *Live bucket* lives at `…_live_deficit`, *Bucket delta* at `…_et`). Reference entities by their entity ID in automations.

## Hub entities

On the hub device:

| Name | Entity ID |
| --- | --- |
| Any zone needs water | `binary_sensor.smart_irrigation_irrigation_needed` |
| Water all zones | `button.smart_irrigation_irrigate_all` |
| Recalculate durations | `button.smart_irrigation_calculate_all` |
| Refresh weather data | `button.smart_irrigation_update_weather` |
| Pause automatic watering until a moment ([rain delay](usage-dashboard.md#rain-delay)) | `datetime.smart_irrigation_rain_delay` |
| Delay automatic watering 24 h | `button.smart_irrigation_delay_24h` |
| Delay automatic watering 48 h | `button.smart_irrigation_delay_48h` |
| Resume automatic watering (clear the delay) | `button.smart_irrigation_resume_irrigation` |

## Duration sensor attributes

The duration sensor (`sensor.smart_irrigation_[zone_name]`) carries the full zone state as attributes:

| Attribute | Description |
| --- | --- |
|`id`|internal identification|
|`size`|the total area the irrigation system reaches in m<sup>2</sup> or sq ft.|
|`throughput`|total amount of water that flows through the irrigation system in liters or gallon per minute.|
|`state`|disabled, manual, automatic |
|`bucket`|the bucket size in mm or inch|
|`unit_of_measurement`|seconds|
|`device_class`|duration|
|`icon`|default: mdi:sprinkler|
|`friendly_name`|`[zone] Duration`|

Sample screenshot:

![](assets/images/sensor.[zone_name].png)

Most of these attributes are now also exposed as their own entities (see the table above), so you can usually reference those directly instead of building [template sensors](https://www.home-assistant.io/integrations/template/#state-based-template-binary-sensors-buttons-images-numbers-selects-and-sensors). If you do want a template sensor for an attribute, use a template like the following example for `bucket`:

`{{state_attr('sensor.smart_irrigation_your_zone_sensor_name', 'bucket')}}`

> Main page: [Usage](usage.md)<br/>
> Next: [Services](usage-services.md)
