# Where every number on the site comes from

Every metric shown on malavnaik.com must trace to a source below. If a number can't be traced, it doesn't go on the site.

| Shown | Where it appears | Source |
|---|---|---|
| ~10 years in data | Hero paragraph, Ask answer | About page ("about 10 years of experience across India and Ireland"); résumé dates 2015 to today |
| 0.957 ROC-AUC | Proof strip, ticker, Ask answer, project card 01 (home), project row (/work/) | Moderation classifier page, Results table: DistilBERT ROC-AUC 0.957 on 180,488 held-out comments ([Kaggle notebook](https://www.kaggle.com/code/malavnaik/moderation-classifier-civil-comments), final run v10) |
| 1.8 million comments | Ask answer, project row summary | Moderation classifier page: Civil Comments data, 1.8 million comments (CC0) |
| 15 min refresh / collection interval | Proof strip ("runs every 15 min"), ticker, featured card, project row summary, readout | Dublin bikes page: "a Python job on GitHub Actions, started every 15 minutes" (`ingest.yml`, nudged by cron-job.org every 15 minutes) |
| €0 a month | Ticker, featured card, project row summary, Ask answer | Dublin bikes page: "Cost: €0" (GitHub Actions on a public repo, Hugging Face free datasets) |
| 14 automatic data tests | Proof strip, ticker, featured card, project row (headline number), pipeline diagram, Ask answer | Dublin bikes page, step 3: "14 automatic data tests run every time" (dbt tests in `dublin-data-pipeline`) |
| Live "last run N min ago" | Proof strip, photo-card readout, featured badge | Fetched in the browser from the GitHub Actions API: the latest successful run of `ingest.yml` in the public repo `malavnaik99/dublin-data-pipeline`. Shown as live only if that run finished within the last 60 minutes; otherwise the page says "runs every 15 min" |
| MSc Data Analytics, NCI | Journey | Résumé and About: MSc in Data Analytics, National College of Ireland, 2024–2025 |
| 84% top-3 hit rate | Proof strip, ticker, project card 02 (home), project row (/work/) | Ask the DSA page, Results: semantic search had the right article in the top 3 for 84% of the 25 test questions |
| 48% skill match | Project card 03 (home), project row (/work/: headline number and chart, 4.8 of 10) | SkillBot page, Results: 48% of the 10 suggested skills were in the real ad (leave-one-out over 1,167 ads) |
| N posts published, platform counts, queued | Ticker, project card 04 (home), /work/ project row (headline number and posts-per-platform bars), bot status line | `_data/automation.json`, written by the blog bot after each post |
| ~25% lower infrastructure cost | Ask answer, journey |
| Bike sky summary ("N bikes at N stations, N empty") and every light in the hero | Home page hero | `_data/sky.json`, made by `scripts/make_sky.py` from `assets/data/dublin-bikes/*.parquet`: the last 48 hours of `fct_station_hour.avg_bikes` (rounded) for every station in `dim_station`, without STATION118 and the 0-dock station. Labelled "saved snapshot"; labelled "live" only when the pipeline's file (`_data/sky_live.json`) is under 2 hours old |
| Station map numbers ("X of Y bikes", the summary and the station list) | Dublin bikes project page, Station map | The same data as the hero sky: `_data/sky.json` (saved snapshot, newest hour) or the pipeline's live file when it is under 2 hours old; labelled "saved snapshot" or "live" |
| Project row charts | /work/ project rows | Drawn by `scripts/make_charts.py` from: `assets/data/dublin-bikes/*.parquet` (average bikes per station by local hour, weekdays vs weekends, without STATION118 and the 0-dock station), `assets/data/moderation-sweep.json` (precision against recall, 0.22 and 0.82 marked), `assets/data/dsa-examples.json` (keyword 17 / 25, vector 21 / 25, recomputed and checked) and the 48% above (4.8 of 10). The automation bars come from `_data/automation.json` at every build. `python3 scripts/make_charts.py --check` says whether the drawn charts still match the data |
| Other projects' headline numbers | /work/ project rows | Each project page's own result: 201,912 rents for 437 places (Irish rents page), 31,044 permits (the official 2025 spreadsheet in this repo), "1 tap" (Gmail auto-reply page: a routine reply becomes one tap) |
| Precision, recall, share flagged and wrongly-flagged rates at each threshold | Home hero demo (all groups plus black, white, gay or lesbian, muslim), moderation sandbox | `assets/data/moderation-sweep.json` (see Sandboxes below). The hero's four groups are the four with the highest wrongly-flagged rate at the 0.22 review threshold | Résumé and post 03: the Azure SQL migration at S&P Global Market Intelligence cut infrastructure costs by about 25% |

## Receipts (the cards behind the four proof-strip numbers)

`scripts/make_receipts.py` copies this table into `_data/receipts.json`, which the home page shows when a visitor opens one
of the four numbers under the hero. The deploy stops if the two differ, so edit here, then run `python3 scripts/make_receipts.py`.
Plain Markdown; links allowed; no "|" inside a cell.

| Key | Shown | Dataset | File | Test |
|---|---|---|---|---|
| pipeline | Pipeline status | Dublinbikes station data and Met Éireann weather, collected every 15 minutes into the public [Hugging Face dataset](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts) | `ingest.yml` in the public repo [malavnaik99/dublin-data-pipeline](https://github.com/malavnaik99/dublin-data-pipeline); your browser asks the GitHub Actions API for its latest successful run | Says "live" only if that run finished in the last 60 minutes; otherwise it says "runs every 15 min" and claims nothing live |
| tests | 14 | The Dublin bikes star schema: `fct_station_hour` with `dim_station` and `dim_hour`, built by dbt in DuckDB | The dbt tests in [malavnaik99/dublin-data-pipeline](https://github.com/malavnaik99/dublin-data-pipeline), described on the [case study](/projects/dublin-bikes-pipeline/), step 3 | 14 automatic tests on every run: keys unique and never empty, every fact linked to its dimensions, counts never negative, freshness (newest data under 2 hours old) and volume (at least 75% of the expected snapshots in the last day); a failure sends a Telegram alert |
| rocauc | 0.957 | Civil Comments (public, CC0): 180,488 held-out test comments, 8.0% toxic, which the model never saw in training | The [Kaggle notebook](https://www.kaggle.com/code/malavnaik/moderation-classifier-civil-comments), final run v10 (DistilBERT) | Re-scoring the same test comments for the threshold sweep reproduced ROC-AUC 0.9574 (`assets/data/moderation-sweep.json`) |
| dsa | 84% | 25 test questions about the EU Digital Services Act, over the official text from [EUR-Lex](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng) | The evaluation in [malavnaik99/eu-dsa-search](https://github.com/malavnaik99/eu-dsa-search); its saved results are `assets/data/dsa-examples.json` | Vector search put the right article in the top 3 for 21 of 25 questions (84%); this site recounts it from the saved results every time the charts are drawn (`scripts/make_charts.py`) |

## Sandboxes

| Sandbox | Data file | Source |
|---|---|---|
| Moderation threshold | `assets/data/moderation-sweep.json` | [moderation-classifier `results/threshold-sweep.json`](https://github.com/malavnaik99/moderation-classifier/blob/main/results/threshold-sweep.json), made by the Kaggle notebook `moderation-threshold-sweep`: the published DistilBERT re-scores the same 180,488 test comments (no retraining). It reproduced ROC-AUC 0.9574, 79.7% recall at the 0.219 review threshold, and the published false-positive rates (e.g. 35.6% for "black", 9.6% overall) before saving. |
| DSA keyword vs vector | `assets/data/dsa-examples.json` | [eu-dsa-search `out/sandbox.json`](https://github.com/malavnaik99/eu-dsa-search/blob/main/out/sandbox.json), made by `eval/sandbox_examples.py` with the same documents, tokenizer and model as the published evaluation. It reproduced the published top-3 hits (keyword 17/25 = 68%, vector 21/25 = 84%) before saving. |
| SQL console | `assets/data/dublin-bikes/*.parquet`, dates in `_data/sql_sample.json` | [dublin-data-pipeline `sample/`](https://github.com/malavnaik99/dublin-data-pipeline/tree/main/sample), made by `sample.py` from the published marts on [Hugging Face](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts): every station, 16–26 Oct 2026, 27,140 station-hours (170 KB). Queries run in the visitor's browser with DuckDB-WASM 1.29.0 from jsDelivr. |

## Job titles (journey)

From Malav, 26 Oct 2026:

- Data Analyst, Bright Info Solutions, 2015–2019
- Data Analyst & ETL Developer, S&P Global Market Intelligence, 2019–2024
- MSc Data Analytics, National College of Ireland, 2024–2025
- Escalation Operations Analyst, Accenture, Dublin, 2026–now (platform integrity, for a global technology client)

## Toolkit

Approved by Malav on 26 Oct 2026. It lists only tools that appear on the résumé or on a project page. See `_data/toolkit.yml`.
