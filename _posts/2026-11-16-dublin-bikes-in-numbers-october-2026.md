---
title: "Dublin Bikes in numbers: 16–31 October 2026"
slug: dublin-bikes-in-numbers-october-2026
bikes_month: "2026-10"
last_modified_at: 2026-11-24
description: "When and where Dubliners picked up Dublinbikes during 16–31 October 2026, and what rain did to it, from my open bikes and weather data."
tags: [dublin, dublinbikes, opendata, dataengineering]
image: "/images/bikes-report/2026-10.png"
image_alt: "Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–31 October 2026. The busiest hour is 08:00–09:00 with 317 pickups on average."
---

A monthly look at Dublinbikes, built from my [bikes and weather pipeline](/projects/dublin-bikes-pipeline/). This is the first edition. My pipeline started collecting on 16 October, so it covers **16–31 October 2026**. Every edition and the running totals are on the [Dublin Bikes statistics](/dublin-bikes/) page.

**How I count pickups:** every 15 minutes I record how many bikes each station has, and whenever a station has fewer bikes than 15 minutes earlier, I count the difference as pickups, so the numbers are estimates (bikes moved by the rebalancing vans count too).

{% include bikes-edition.html month=page.bikes_month %}

## Use this data

You're welcome to reuse the chart in articles, slides or posts, as long as you link back to this post. The data behind it is open on Hugging Face: [raw snapshots](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw) and [modelled tables](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts), CC BY 4.0. Bikes: Dublinbikes GBFS feed, Dublin City Council / JCDecaux. Weather: Source: Met Éireann.

### Embed this chart

```html
<a href="https://malavnaik.com/blog/dublin-bikes-in-numbers-october-2026/"><img src="https://malavnaik.com/images/bikes-report/2026-10.png" alt="Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–31 October 2026. The busiest hour is 08:00–09:00 with 317 pickups on average." width="800" height="450"></a>
```
