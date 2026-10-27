---
id: 51
title: "I Built a Tested Data Pipeline for Dublin Bikes, for €0"
slug: dublin-bikes-data-pipeline
description: "How I collect every Dublinbikes station every 15 minutes, model it with dbt and DuckDB, test it daily and feed a live dashboard, using only free tiers."
series: data-engineering
tags: [dataengineering, dbt, duckdb, python]
image: "/images/malav-naik-dublin-docklands.jpg"
image_alt: "Malav Naik leaning on a red pole by the water in Dublin Docklands"
week: 26
platforms: [blog, devto, medium, linkedin]
canonical_url: "https://malavnaik.com/blog/dublin-bikes-data-pipeline/"
linkedin_intro: "Live city data is gone as soon as it updates, so I built a small pipeline that keeps it: every Dublinbikes station every 15 minutes, plus the weather, modelled with dbt and DuckDB, tested every morning and shown on a live dashboard. Total cost: €0. Here's how it fits together, and what I'd do differently."
x_post: "Live city data vanishes as it updates, so I built a pipeline that keeps it: every Dublinbikes station every 15 minutes plus the weather, modelled with dbt + DuckDB, tested every morning, with a live dashboard. Total cost: €0."
reddit: {"community": "r/Dublin", "title": "I've been logging Dublinbikes availability every 15 minutes, with a free dashboard of when stations run empty", "text": "A hobby data project: every station every 15 minutes since mid-October, plus Met Éireann weather. The page shows average free bikes by hour of day and which stations are most often empty. It's only a few weeks of data so far. Which stations do you find hardest at rush hour?"}
status: ready
tldr: "A Python job on GitHub Actions saves every Dublinbikes station every 15 minutes, plus Met Éireann weather, as append-only Parquet on Hugging Face. Every morning dbt on DuckDB builds a tested star schema with 14 data checks and Telegram alerts, and a static dashboard reads the results. Total cost: €0, on free tiers only."
faq:
  - q: "Why use cron-job.org instead of GitHub's own scheduler?"
    a: "GitHub's scheduler is unreliable for frequent jobs. The 15-minute schedule didn't fire once in its first hour, and a free external timer that calls GitHub's API fixed it."
  - q: "What do the freshness and volume tests catch?"
    a: "The real-world failures: a feed that goes quiet, or a collector that silently stops. Freshness checks the newest snapshot is under 2 hours old; volume checks that at least 75% of the expected snapshots arrived in the last 24 hours."
last_modified_at: 2026-10-27
---

![Malav Naik leaning on a red pole by the water in Dublin Docklands – I Built a Tested Data Pipeline for Dublin Bikes, for €0](/images/malav-naik-dublin-docklands.jpg){: width="1440" height="1440"}

The Dublinbikes feed tells you how many bikes are at each station *right now*. It doesn't keep history. So if you want to ask "how do weather and time of day change how many bikes are free?", you first need a pipeline that collects the data, keeps it safe and tells you when something breaks.

I built one, end to end, using only free tiers. The code is [on GitHub](https://github.com/malavnaik99/dublin-data-pipeline) and the [project page](https://malavnaik.com/projects/dublin-bikes-pipeline/) has a live dashboard.

## 1. Collect: small, boring and append-only

A Python script runs on GitHub Actions every 15 minutes. It reads the Dublinbikes GBFS feed (all 115 stations) and, once an hour, the Met Éireann observations for Dublin Airport. Both are open data under CC BY 4.0.

Each run writes a new Parquet file, partitioned by date, to a public Hugging Face dataset. Nothing is ever overwritten, so a bad run can't damage history.

Two lessons from this step:

- **GitHub's own scheduler is unreliable for frequent jobs.** My 15-minute schedule didn't fire once in its first hour. A free external timer (cron-job.org) that calls GitHub's API fixed it.
- **Fail loudly, then stop.** After three failed runs in a row the workflow switches itself off and sends me a Telegram message, instead of failing silently for days.

## 2. Model: dbt on DuckDB

Every morning, dbt builds the models inside a DuckDB file:

- **Staging:** proper types, UTC timestamps (the weather comes in Irish local time) and de-duplication. Each hourly weather file repeats the whole day so far, so only the latest copy of each observation is kept.
- **Intermediate:** one row per station per hour, with average, minimum and maximum bikes, and the share of the hour the station was empty or full.
- **Marts:** a small star schema. `fct_station_hour` sits in the middle, with `dim_station` (name, location, capacity) and `dim_hour` (Dublin local time, weekday and that hour's weather).

The fact table is **incremental**: each run only recomputes the last three hours. It is also **idempotent**: running it twice gives exactly the same table. That matters, because reruns are the first thing you reach for when something goes wrong.

DuckDB writes everything to a single file, so I store it in a second Hugging Face dataset between runs. That's how the incremental table "remembers" what it already built without a database server.

## 3. How do you test a data pipeline? 14 checks, every run

dbt runs 14 data tests on every build:

- keys are unique and never empty;
- every row in the fact table links to a station and an hour;
- bike and dock counts are never negative;
- **freshness**: the newest snapshot is less than 2 hours old;
- **volume**: at least 75% of the expected snapshots arrived in the last 24 hours.

The last two catch the real-world failures: a feed that goes quiet, or a collector that silently stops. If any check fails, I get a Telegram alert.

The data also taught me something: one "station" in the feed is a placeholder that never has a bike. Left in, it tops every "most often empty" list. The dashboard now leaves out stations that never had a bike in the period.

## 4. Publish: a dashboard with no backend

Each run publishes the tables as Parquet, a run log and a small `dashboard.json` summary. The [project page](https://malavnaik.com/projects/dublin-bikes-pipeline/) fetches that file in the browser and draws the chart. There's no server to keep running, and the dashboard updates as soon as the morning run finishes. The [dbt docs and lineage graph](https://huggingface.co/spaces/Malavnaik/dublin-bikes-dbt-docs) are published as a free static page.

## How much does it cost to run?

€0: public-repo GitHub Actions minutes, free Hugging Face datasets and a static Space, and one free cron-job.org job.

## What I'd do differently

- **Compact the small files.** About 100 small Parquet files a day is fine for now, but over a year I'd merge them into daily files.
- **Add a "late data" test per station**, not just overall, to spot a single broken dock.

## What's next

The pipeline is the easy part. The question needs weeks of data across different weather before any answer is honest. Once that has built up, I'll publish the analysis and write up what the data says.
