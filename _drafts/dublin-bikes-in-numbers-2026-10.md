---
title: "Dublin Bikes in numbers: 16–27 October 2026"
slug: dublin-bikes-in-numbers-october-2026
description: "When and where Dubliners picked up Dublinbikes during 16–27 October 2026, and what rain did to it, from my open bikes and weather data."
tags: [dublin, dublinbikes, opendata, dataengineering]
image: "/images/bikes-report/2026-10.png"
image_alt: "Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–27 October 2026. The busiest hour is 08:00–09:00 with 291 pickups on average."
---

A monthly look at Dublinbikes, built from my [bikes and weather pipeline](/projects/dublin-bikes-pipeline/). This is the first edition. My pipeline started collecting on 16 October, so it covers **16–27 October 2026**.

**How I count pickups:** every 15 minutes I record how many bikes each station has, and whenever a station has fewer bikes than 15 minutes earlier, I count the difference as pickups, so the numbers are estimates (bikes moved by the rebalancing vans count too).

## The headline

About **34,327 estimated pickups** across 113 stations, or roughly 3,008 a day.

## The busiest hour

![Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–27 October 2026. The busiest hour is 08:00–09:00 with 291 pickups on average.](/images/bikes-report/2026-10.png){: width="800" height="450"}

The busiest hour was **08:00–09:00**, with 291 estimated pickups on average across all stations.

## Busiest and quietest stations

Most estimated pickups:

1. Charlemont Place: 827
2. Grand Canal Dock: 736
3. Fownes Street Upper: 616
4. Princes Street / O'Connell Street: 615
5. Exchequer Street: 563

Fewest:

1. Grangegorman Lower (Central): 57
2. Merrion Square South: 85
3. Kilmainham Lane: 106
4. Fitzwilliam Square East: 107
5. Hardwicke Place: 108

## Where to find a bike

Average share of docks holding a bike. Emptiest stations:

1. Fitzwilliam Square East: 4.8%
2. Merrion Square South: 6.0%
3. Mountjoy Square East: 7.7%
4. Hardwicke Place: 7.8%
5. Hatch Street: 7.8%

Fullest stations:

1. Talbot Street: 81.2%
2. Dame Street: 80.0%
3. Buckingham Street Lower: 79.4%
4. Smithfield North: 74.5%
5. Barrow Street: 73.4%

## What rain did

It rained (at least 0.1 mm at Dublin Airport) in 55 hours. In those hours there were **44.2% fewer estimated pickups** than in dry hours at the same time of day. Without adjusting for the time of day, rainy hours averaged 74 pickups and dry hours 158. Hours with only a trace of rain are left out. It's a small sample, so treat this as a first look.

Month-on-month comparisons start with the November edition.

## Use this data

You're welcome to reuse the chart in articles, slides or posts, as long as you link back to this post. The data behind it is open on Hugging Face: [raw snapshots](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw) and [modelled tables](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts), CC BY 4.0. Bikes: Dublinbikes GBFS feed, Dublin City Council / JCDecaux. Weather: Source: Met Éireann.

### Embed this chart

```html
<a href="https://malavnaik.com/blog/dublin-bikes-in-numbers-october-2026/"><img src="https://malavnaik.com/images/bikes-report/2026-10.png" alt="Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–27 October 2026. The busiest hour is 08:00–09:00 with 291 pickups on average." width="800" height="450"></a>
```
