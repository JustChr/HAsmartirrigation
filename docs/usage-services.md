---
layout: default
title: Usage: Services
---
# Services

> Main page: [Usage](usage.md)<br/>
> Previous: [Entities](usage-entities.md)<br/>
> Next: [Events](usage-events.md)

After installation, the following services are available:
| Service | Description|
| --- | --- |
|`Smart Irrigation: calculate_zone`|Triggers the calculation of one specific zone. The zone consumes only the weather data it needs; the shared buffer is kept for other zones and pruned automatically.|
|`Smart Irrigation: calculate_all_zones`|Triggers the calculation of all automatic zones. Use only if you disabled automatic calculation. Each zone consumes its own window of weather data; the buffer is pruned automatically afterwards.|
|`Smart Irrigation: clear_all_weather_data`|Deletes all weather data|
|`Smart Irrigation: clear_rain_delay`|Resumes automatic irrigation by clearing any active [rain delay / vacation hold](usage-dashboard.md#rain-delay).|
|`Smart Irrigation: generate_watering_calendar`|Generate a 12-month watering calendar for a zone based on representative climate data.|
|`Smart Irrigation: reset_all_buckets`|Resets all buckets to 0.|
|`Smart Irrigation: reset_bucket`|Resets one specific bucket to 0.|
|`Smart Irrigation: run_zone`|Waters one zone for a custom `duration` (minutes), **bypassing** the calculation, the deficit gate and any active rain delay. The delivered water is credited back to the bucket. Target the zone by its duration `sensor` entity.|
|`Smart Irrigation: set_all_buckets`|Sets all buckets to a specific `new_bucket_value` (default is 0).|
|`Smart Irrigation: set_all_multipliers`|Sets all multipliers to a specific `new_multiplier_value` (default is 1.0).|
|`Smart Irrigation: set_bucket`|Sets a specific bucket to to a specific `new_bucket_value` (default is 0).|
|`Smart Irrigation: set_multiplier`|Sets a specific multiplier to a specific `new_multiplier_value` (default is 1.0).|
|`Smart Irrigation: set_rain_delay`|Pauses all automatic/scheduled irrigation — either for `hours` from now, or until a specific datetime `until`. Manual runs still work. See [rain delay](usage-dashboard.md#rain-delay).|
|`Smart Irrigation: set_state`|Sets a zone's state to a specific `new_state_value` (`automatic`, `manual` or `disabled`).|
|`Smart Irrigation: set_zone`| Allows configuration for bucket (with `new_bucket_value` (default 0)), multiplier (with `new_multiplier_value` (default 1.0)), duration (with `new_duration_value` (default 0)), state (with `new_state_value` (default 'automatic')) and throughput (with `new_throughput_value` (default 50)) settings for a zone.|
|`Smart Irrigation: update_all_zones`|Updates all automatic zones with weather data|
|`Smart Irrigation: update_zone`|Updates one specific zone with weather data|

> Main page: [Usage](usage.md)<br/>
> Previous: [Entities](usage-entities.md)<br/>
> Next: [Events](usage-events.md)
