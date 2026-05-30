---
layout: default
title: Introduction
---
# Smart Irrigation

Ever wondered if you're watering your lawn, garden, greenhouse, or crops too much or too little? Tired of guesswork and fixed timers? If you have an irrigation system you can switch on and off through Home Assistant, this integration is for you.

Smart Irrigation calculates the exact number of seconds to run your irrigation system to compensate for moisture lost through [evapotranspiration](https://en.wikipedia.org/wiki/Evapotranspiration). It takes into account precipitation (rain, snow) and adjusts accordingly — if it has rained enough, no irrigation is needed; if not, it tells you exactly how long to irrigate.

Key capabilities:

- **Multiple zones** — each with its own size, throughput, calculation module, and sensor group
- **Weather sources** — Open Weather Map, Pirate Weather, or your own local sensors (or a mix)
- **Moisture bucket** — tracks cumulative evapotranspiration and precipitation over time
- **Rain skip** — optionally skip irrigation when significant rain is forecast
- **Days between irrigation** — enforce a minimum rest period between irrigation events
- **Automations** — the integration fires Home Assistant events; your automations decide what to do with valves, timers, etc.

> **Use this integration at your own risk.** It provides calculated recommendations only — always apply common sense before irrigating. Irrigating during heavy rainfall can cause flooding. The maintainers accept no responsibility for any damage or inconvenience caused.

---

This is a community-maintained fork of [jeroenterheerdt/HAsmartirrigation](https://github.com/jeroenterheerdt/HAsmartirrigation). It is kept up to date with Home Assistant releases and includes bug fixes and improvements beyond the original.

---

**Ready to get started?** → [Installation](installation.md)

Want to understand the maths first? Read [how it works](how-it-works.md) or watch the [official tutorial videos on YouTube (English)](https://youtube.com/playlist?list=PLUHIAUPJHMiakbda92--fgb6A0hFReAo7&si=82Xc6mHoLDwFBfCP).
