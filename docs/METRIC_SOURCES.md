# Where every number on the site comes from

Every metric shown on malavnaik.com must trace to a source below. If a number can't be traced, it doesn't go on the site.

| Shown | Where it appears | Source |
|---|---|---|
| ~10 years in data | Hero label, metric strip, Ask answer | About page ("about 10 years of experience across India and Ireland"); résumé dates 2015 to today |
| 0.957 ROC-AUC | Metric strip, Ask answer, project row 01 | Moderation classifier page, Results table: DistilBERT ROC-AUC 0.957 on 180,488 held-out comments ([Kaggle notebook](https://www.kaggle.com/code/malavnaik/moderation-classifier-civil-comments), final run v10) |
| 1.8 million comments | Ask answer, project row 01 | Moderation classifier page: Civil Comments data, 1.8 million comments (CC0) |
| 15 min refresh / collection interval | Metric strip, featured card, readout | Dublin bikes page: "a Python job on GitHub Actions, started every 15 minutes" (`ingest.yml`, nudged by cron-job.org every 15 minutes) |
| €0 a month | Metric strip, featured card, Ask answer | Dublin bikes page: "Cost: €0" (GitHub Actions on a public repo, Hugging Face free datasets) |
| 14 automatic data tests | Featured card, pipeline diagram, Ask answer | Dublin bikes page, step 3: "14 automatic data tests run every time" (dbt tests in `dublin-data-pipeline`) |
| Live "last run N min ago" | Photo-card readout, featured badge | Fetched in the browser from the GitHub Actions API: the latest successful run of `ingest.yml` in the public repo `malavnaik99/dublin-data-pipeline`. Shown as live only if that run finished within the last 60 minutes; otherwise the page says "runs every 15 min" |
| MSc Data Analytics, NCI | Metric strip, journey | Résumé and About: MSc in Data Analytics, National College of Ireland, 2024–2025 |
| 84% top-3 hit rate | Project row 02 | Ask the DSA page, Results: semantic search had the right article in the top 3 for 84% of the 25 test questions |
| 48% skill match | Project row 03 | SkillBot page, Results: 48% of the 10 suggested skills were in the real ad (leave-one-out over 1,167 ads) |
| N posts published, platform counts, queued | Project row 04, bot status line | `_data/automation.json`, written by the blog bot after each post |
| ~25% lower infrastructure cost | Ask answer, journey | Résumé and post 03: the Azure SQL migration at S&P Global Market Intelligence cut infrastructure costs by about 25% |

## Job titles (journey)

From Malav, 26 Oct 2026:

- Data Analyst, Bright Info Solutions, 2015–2019
- Data Analyst & ETL Developer, S&P Global Market Intelligence, 2019–2024
- MSc Data Analytics, National College of Ireland, 2024–2025
- Escalation Operations Analyst, Accenture, Dublin, 2026–now (platform integrity, for a global technology client)

## Toolkit

Approved by Malav on 26 Oct 2026. It lists only tools that appear on the résumé or on a project page. See `_data/toolkit.yml`.
