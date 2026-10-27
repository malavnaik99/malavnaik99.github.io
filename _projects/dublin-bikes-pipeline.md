---
title: "Dublin bikes + weather data pipeline"
summary: "Collects every Dublinbikes station every 15 minutes, models it with dbt and DuckDB into a tested star schema, and feeds a live dashboard – for €0."
problem: "The Dublinbikes feed only shows right now; questions about weather and time of day need history that can be trusted."
approach: "A collector every 15 minutes, then a daily dbt + DuckDB run into an incremental star schema with 14 automatic data tests and Telegram alerts."
result: "Every station, every 15 minutes, modelled and tested into a live dashboard and public dataset, for €0."
description: "A data engineering project by Malav Naik: a Python collector, a dbt + DuckDB star schema with freshness and volume tests, and a live Dublinbikes dashboard."
order: 2
featured: true
sandbox: sql
code_url: https://github.com/malavnaik99/dublin-data-pipeline
tech: [Python, GitHub Actions, dbt, DuckDB, Parquet, Hugging Face Datasets, GBFS, Met Éireann]
# Dataset JSON-LD (see _includes/schema.html); points at the modelled tables on Hugging Face.
dataset:
  name: "Dublin bikes and weather: hourly star schema"
  description: "Every Dublinbikes station's bikes and free docks, collected every 15 minutes and joined with Met Éireann Dublin Airport weather, modelled with dbt and DuckDB into a tested star schema (fct_station_hour, dim_station, dim_hour) and published as Parquet."
  url: https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts
  license: https://creativecommons.org/licenses/by/4.0/  # the dataset card's license (cc-by-4.0, set in transform.py of dublin-data-pipeline)
  place: "Dublin, Ireland"
  keywords: [Dublinbikes, bike sharing, weather, Dublin, GBFS, Met Éireann, dbt, DuckDB, Parquet]
  sources: [https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw]
---
## The problem
Public city data is published live and then gone: the Dublinbikes feed only shows *right now*. To answer a question like **"how do weather and time of day change how many bikes are free?"** you need history, collected reliably and modelled so it can be trusted.

## What I built
An end-to-end pipeline that runs on free tiers only:

- a **collector** that saves a snapshot of all Dublinbikes stations every 15 minutes, plus the hourly Dublin weather, without ever overwriting old data;
- **dbt + DuckDB models** that turn raw snapshots into a small star schema, with automatic data checks;
- a **live dashboard** (below) that reads the newest results straight from the published data.

## How it works

<svg viewBox="0 0 640 300" role="img" aria-labelledby="dp-title" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="16">
  <title id="dp-title">Flow: Dublinbikes and Met Éireann feeds are collected every 15 minutes into raw Parquet files on Hugging Face; a daily dbt run on DuckDB builds staging, hourly and star-schema tables with tests; the results feed the dashboard, and failures alert on Telegram</title>
  <g fill="none" stroke="currentColor" stroke-width="1.5">
    <rect x="10" y="10" width="290" height="50" rx="8"/><rect x="340" y="10" width="290" height="50" rx="8"/>
    <rect x="120" y="95" width="400" height="50" rx="8"/>
    <rect x="120" y="180" width="400" height="50" rx="8"/>
    <rect x="10" y="255" width="290" height="40" rx="8"/><rect x="340" y="255" width="290" height="40" rx="8"/>
    <path d="M155 60v18h330V60M320 78v13M320 145v31M320 230v10h-165v11M320 240h165v11"/>
  </g>
  <g fill="currentColor" text-anchor="middle">
    <text x="155" y="41">Dublinbikes feed (GBFS)</text><text x="485" y="41">Met Éireann weather</text>
    <text x="320" y="126">Every 15 min: raw Parquet, never overwritten</text>
    <text x="320" y="211">Daily: dbt + DuckDB models and data checks</text>
    <text x="155" y="281">Live dashboard</text><text x="485" y="281">Telegram alert if a check fails</text>
  </g>
</svg>

1. **Collect:** a Python job on GitHub Actions, started every 15 minutes, saves each station's bikes and free docks, and once an hour the Dublin Airport weather, as date-partitioned Parquet files in a public [Hugging Face dataset](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw). After three failures in a row it switches itself off and messages me on Telegram.
2. **Model:** every morning dbt builds, in DuckDB: *staging* views (types, time zones, de-duplication) → an *hourly* summary per station → a **star schema**: `fct_station_hour` with `dim_station` and `dim_hour` (local time, weekday and that hour's weather). The fact table is **incremental and idempotent**: each run recomputes only the last few hours, and rerunning gives the same result. See the [dbt docs and lineage graph](https://huggingface.co/spaces/Malavnaik/dublin-bikes-dbt-docs).
3. **Check:** 14 automatic data tests run every time: keys unique and never empty, every fact linked to its dimensions, counts never negative, **freshness** (newest data under 2 hours old) and **volume** (at least 75% of the expected snapshots in the last day). A failure sends me a Telegram alert.
4. **Publish:** the tables, a run log and the dashboard summary go to a second [Hugging Face dataset](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts). Cost: €0.

## Live dashboard
<div id="dash" aria-live="polite"><p class="muted">Loading the latest data…</p></div>

<script>
(async function () {
  const box = document.getElementById('dash');
  const base = 'https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts/resolve/main/';
  try {
    const [d, log] = await Promise.all(['dashboard.json', 'run_log.json'].map(f => fetch(base + f).then(r => { if (!r.ok) throw r.status; return r.json(); })));
    const s = d.summary, esc = t => String(t).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
    const series = w => d.by_local_hour.filter(r => r.is_weekend === w).map(r => [r.local_hour, r.pct_time_empty]);
    const max = Math.max(5, ...d.by_local_hour.map(r => r.pct_time_empty));
    const pts = w => series(w).map(([h, v]) => `${60 + h * 23},${190 - v / max * 160}`).join(' ');
    const ticks = [0, 6, 12, 18, 23].map(h => `<text x="${60 + h * 23}" y="218" text-anchor="middle">${h}:00</text>`).join('');
    const rows = d.most_often_empty.map(r => `<tr><td>${esc(r.station_name)}</td><td>${r.pct_time_empty}%</td></tr>`).join('');
    const rain = Object.fromEntries(d.rain.map(r => [r.weather, r]));
    box.innerHTML = `
      <p><strong>Pipeline status:</strong> last run ${esc(log.run_at.slice(0, 16).replace('T', ' '))} UTC ·
        ${log.tests_passed} of ${log.tests_total} data checks passed ${log.ok ? '✅' : '⚠️'} ·
        ${s.stations} active stations · ${s.n_hours} hours of data (${esc(s.first_day)} to ${esc(s.last_day)})</p>
      <p><strong>How often are stations empty, by hour of day (Dublin time)?</strong></p>
      <svg viewBox="0 0 640 228" role="img" aria-label="Line chart: percentage of time stations are empty by hour, weekdays and weekends" style="width:100%;height:auto;max-width:640px" font-family="sans-serif" font-size="20">
        <g stroke="currentColor" opacity=".25"><line x1="60" y1="190" x2="600" y2="190"/><line x1="60" y1="30" x2="600" y2="30"/></g>
        <text x="54" y="34" text-anchor="end" fill="currentColor">${max.toFixed(0)}%</text><text x="54" y="194" text-anchor="end" fill="currentColor">0%</text>
        <g fill="currentColor">${ticks}</g>
        <polyline points="${pts(false)}" fill="none" stroke="var(--link)" stroke-width="2.5"/>
        <polyline points="${pts(true)}" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4"/>
      </svg>
      <p class="muted">Solid line: weekdays. Dashed line: weekends. Average share of each hour that a station had no bikes.</p>
      ${rain.raining && rain.dry ? `<p><strong>Rain so far:</strong> on average ${rain.raining.pct_bikes_available}% of dock capacity held bikes in hours with rain (${rain.raining.n_hours} hours), against ${rain.dry.pct_bikes_available}% in dry hours (${rain.dry.n_hours} hours). Early data, not a conclusion yet.</p>` : ''}
      <p><strong>Stations most often empty</strong></p>
      <table><thead><tr><th>Station</th><th>Share of time empty</th></tr></thead><tbody>${rows}</tbody></table>`;
  } catch (e) {
    box.innerHTML = '<p class="muted">The live data couldn\'t load right now. It is published at <a href="https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts">Hugging Face</a>.</p>';
  }
})();
</script>

## What's next
The question needs weeks of data, across different weather, before any answer is honest. Once enough has built up, I'll publish an analysis notebook and write up what the data says.

## Data and credits
- [Read the story: I Built a Tested Data Pipeline for Dublin Bikes, for €0]({{ '/blog/dublin-bikes-data-pipeline/' | relative_url }})
- Bikes: Dublinbikes GBFS feed, Dublin City Council / JCDecaux, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- Weather: Source: Met Éireann, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- [Raw snapshots](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw) · [Modelled tables](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts) · [dbt docs](https://huggingface.co/spaces/Malavnaik/dublin-bikes-dbt-docs) · [Code on GitHub](https://github.com/malavnaik99/dublin-data-pipeline)
