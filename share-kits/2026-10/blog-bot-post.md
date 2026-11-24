---
id: -202610
title: 'Dublin Bikes in numbers: 16–31 October 2026'
slug: dublin-bikes-in-numbers-october-2026
description: When and where Dubliners picked up Dublinbikes during 16–31 October 2026, and what rain did to it, from my open bikes and weather data.
tags:
- dublin
- dublinbikes
- opendata
- dataengineering
image: images/bikes-report/2026-10.png
image_alt: Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–31 October 2026. The busiest hour is 08:00–09:00 with 317 pickups on average.
platforms:
- blog
- devto
- linkedin
- medium
linkedin_intro: New Dublin Bikes numbers for 16–31 October 2026. In the 61 rainy hours, about 34% fewer bikes were picked up than in dry hours at the same time of day. Dame Street averaged 81.2% of its docks full, so finding a free dock there was hard.
status: ready
---
# Dublin Bikes in numbers: 16–31 October 2026

![Bar chart of average estimated Dublinbikes pickups per hour by hour of day, 16–31 October 2026. The busiest hour is 08:00–09:00 with 317 pickups on average.](../images/bikes-report/2026-10.png)

In the 61 rainy hours, about 34% fewer bikes were picked up than in dry hours at the same time of day. Dame Street averaged 81.2% of its docks full, so finding a free dock there was hard.

The numbers for 16–31 October 2026, from my open Dublin Bikes and weather pipeline:

- About **48,783** estimated pickups across 113 stations, roughly 3,142 a day.
- Busiest hour: **08:00–09:00**, about 317 pickups on average.

## Busiest stations

| Station | Estimated pickups | Docks with a bike |
|---|---|---|
| Charlemont Place | 1,180 | 46.2% |
| Grand Canal Dock | 1,033 | 40% |
| Princes Street / O'Connell Street | 888 | 64.6% |
| Fownes Street Upper | 873 | 68.4% |
| Exchequer Street | 780 | 54.5% |

## Quietest stations

| Station | Estimated pickups | Docks with a bike |
|---|---|---|
| Grangegorman Lower (Central) | 72 | 20.4% |
| Hardwicke Place | 141 | 6.6% |
| Merrion Square South | 143 | 7.5% |
| Fitzwilliam Square East | 145 | 4.5% |
| Kilmainham Lane | 150 | 25.1% |

## Where to find a bike

| Usually full | Docks with a bike |
|---|---|
| Dame Street | 81.2% |
| Smithfield North | 77.7% |
| Talbot Street | 74.7% |
| Barrow Street | 74.2% |
| Buckingham Street Lower | 72.9% |

| Usually empty | Docks with a bike |
|---|---|
| Fitzwilliam Square East | 4.5% |
| Hardwicke Place | 6.6% |
| Merrion Square South | 7.5% |
| Hatch Street | 8.5% |
| Eccles Street East | 9.8% |

## What rain did

| Weather | Hours | Average estimated pickups per hour |
|---|---|---|
| Rainy (0.1 mm or more) | 61 | 94 |
| Dry (0 mm) | 212 | 162 |

## How the numbers are made

Every 15 minutes my pipeline records how many bikes each station has. When a station has fewer bikes than at the previous snapshot, the difference counts as pickups, so these are estimates: bikes moved by the rebalancing vans count too. The data is open on Hugging Face ([raw](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw), [modelled](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts), CC BY 4.0). Sources: Dublinbikes feed (Dublin City Council / JCDecaux) and Met Éireann.

Every edition and the running totals: [Dublin Bikes statistics](https://malavnaik.com/dublin-bikes/).
