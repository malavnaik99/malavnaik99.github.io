# Outreach drafts: top 10 prospects (2026-10-27)

Drafts only. Nothing has been sent and no pull requests have been opened. Before sending: check each recipient's current submission rules, add one line showing you've read something recent of theirs, and send from malavnaik.com email. Each draft links one project page. Anchors are plain project names, never keyword phrases.

---

## 1. awesome-duckdb: PR entry line
Repo: https://github.com/davidgasquez/awesome-duckdb. Put it in the section for projects, examples or resources; check the current headings and match the alphabetical order and punctuation of nearby lines.

```markdown
- [Dublin bikes + weather pipeline](https://malavnaik.com/projects/dublin-bikes-pipeline/) - Every Dublinbikes station every 15 minutes, modelled with dbt on DuckDB into an incremental star schema with 14 data tests, plus an in-browser DuckDB-WASM SQL console over the published Parquet.
```

---

## 2. MotherDuck DuckDB Ecosystem Newsletter: email
To: duckdbnews@motherduck.com
Subject: Community project: a €0 dbt + DuckDB pipeline on Dublin's bike-share feed

Hi Simon and the MotherDuck team,

[One line on a recent issue you liked.] Here's a community build that might fit a future issue.

I collect every Dublinbikes station every 15 minutes, then a daily dbt run on DuckDB builds an incremental, idempotent star schema with 14 tests, including freshness and volume checks. The marts are public Parquet, and the page has a DuckDB-WASM console so readers can query them in the browser:
https://malavnaik.com/projects/dublin-bikes-pipeline/

It all runs on free tiers. Happy to answer questions or share anything that would help.

Thanks,
Malav Naik, Dublin

---

## 3. data.gov.ie showcases: submission
To: opendata@per.gov.ie (or the showcase form linked from https://data.gov.ie/blog/submitashowcase)
Subject: Showcase submission: Dublin bikes and weather dashboard

Hello,

I'd like to submit a showcase built on the Dublinbikes API dataset listed on data.gov.ie.

It collects every station every 15 minutes, adds Met Éireann weather, and turns this into a tested history with a live dashboard of availability by hour and weather. The modelled data is published openly so others can reuse it. Credits to Dublin City Council / JCDecaux and Met Éireann are on the page:
https://malavnaik.com/projects/dublin-bikes-pipeline/

I can provide a screenshot, a short description or anything else the showcase needs.

Kind regards,
Malav Naik, Dublin

---

## 4. Everything in Moderation: email
To: the tip address in the newsletter footer
Subject: Open moderation classifier with review-queue and fairness numbers

Hi Ben,

[One line on a recent EiM issue.] Public examples rarely show what a threshold choice does to the review queue, so I built an open one.

On 1.8 million public Civil Comments, a DistilBERT model auto-actions 36.6% of toxic comments at ≥90% precision. The project also simulates the human queue and compares false-positive rates by identity group (cut from 12.8% to 9.6%). There's a threshold slider in the browser:
https://malavnaik.com/projects/moderation-classifier/

It's a personal project; by day I'm an Analyst at Accenture, working for a global technology client. Hope it's useful for a links section.

Best,
Malav Naik

---

## 5. Exposing the Invisible (Tactical Tech): email
To: contact form on exposingtheinvisible.org
Subject: A plain-English search tool for your DSA tools list

Hello,

Your article "What can the Digital Services Act do for you?" is one of the clearest guides I've found for non-lawyers.

Your readers might also find a free tool useful. They type a question in everyday words and get the DSA articles that answer it, quoted and linked to EUR-Lex. On 25 test questions, the right article is in the top 3 for 84% of them. It's free and runs in the browser, with no account needed:
https://malavnaik.com/projects/ask-the-dsa/

If it would fit the article's tools section, I'd be glad. Feedback on where it falls short is just as welcome.

Thanks,
Malav Naik, Dublin

---

## 6. Smart Dublin: email
To: contact on smartdublin.ie
Subject: Historical Dublinbikes data, rebuilt from the open API

Hello,

Your post on open data for Dublin's bike-share services said historical data matters for charts and visualisations. That's what I built on top of the Dublinbikes API.

Every station is collected every 15 minutes, joined with Met Éireann weather, tested daily and published as an open dataset with a live dashboard:
https://malavnaik.com/projects/dublin-bikes-pipeline/

If it's useful as an example of the API in use, for a post or a showcase, I'd be happy to share details or adapt it.

Kind regards,
Malav Naik, Dublin

---

## 7. ROOST awesome-safety-tools: PR entry line
Repo: https://github.com/roostorg/awesome-safety-tools. It goes under the classifiers/models (text) section; follow the list's contribution guide and entry format.

```markdown
- [Content moderation classifier, with a fairness check](https://malavnaik.com/projects/moderation-classifier/) - Open DistilBERT and TF-IDF toxicity models trained on Civil Comments, with precision-targeted thresholds, a simulated review queue, prevalence estimation and false-positive rates by identity group; ONNX model runs in the browser.
```

---

## 8. Open Data in Ireland: PR entry line
Repo: https://github.com/virtualarchitectures/Open-Data-in-Ireland. It goes in the housing or statistics section; match the existing format.

```markdown
- [Irish rents 2008–2025 (cleaned RTB/CSO table)](https://malavnaik.com/projects/irish-rents/) - The RTB average rent of new tenancies for 437 counties, towns and areas, cleaned into one documented table (201,912 rows) with a reproducible notebook; on Kaggle and Hugging Face.
```

---

## 9. Data Engineering Weekly: article contribution
Route: a pull request with the article entry under the weekly folder of the newsletter's GitHub repo, per its contributing guide. Use the field names in their current template; this is the content.

```yaml
author:
  name: Malav Naik
  linkedin: https://www.linkedin.com/in/malav-naik
article: https://malavnaik.com/blog/dublin-bikes-data-pipeline/
tags: dbt, DuckDB, data quality, incremental models
```

Note: this links the blog post, not the project page, because the newsletter curates articles. The post links on to the project page.

---

## 10. Irish Cycle: email
To: contact on irishcycle.com
Subject: Dublinbikes data: a public history to go with your 2024 piece

Hi,

I read your piece on Dublin bike-share data becoming more freely available. I've been building on that data: I record every Dublinbikes station every 15 minutes, with the weather, and publish the history openly with a live dashboard:
https://malavnaik.com/projects/dublin-bikes-pipeline/

It shows, for example, how availability changes by hour and with the weather. If it's useful for a follow-up on how the scheme is used, I'm happy to pull specific numbers for any stations or areas you're curious about.

Thanks for the coverage of cycling in Dublin.

Malav Naik
