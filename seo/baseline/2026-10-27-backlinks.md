# Backlink baseline: malavnaik.com (2026-10-27)

**How this was run:** no `/seo backlinks` command or backlink index (Ahrefs, Moz, Majestic, Search Console) was available in this session. Referring domains were found with web searches for `"malavnaik.com"` and the profile handles, plus the Kaggle API. So this is a **lower bound**, not a complete link index. For an exact count, check Search Console → Links → "Top linking sites" for the `malavnaik.com` property.

## Referring domains found: 3

| Domain | Linking page | Points to | Type | Notes |
|---|---|---|---|---|
| github.com | [malavnaik99/malavnaik99](https://github.com/malavnaik99/malavnaik99) (profile README) | malavnaik.com | profile | Self-owned |
| dev.to | [What 1.8 Million Comments Taught Me…](https://dev.to/malavnaik_0381711024683d4/what-18-million-comments-taught-me-about-fair-content-moderation-2828) | malavnaik.com post | syndication ("Originally published at") | Self-owned |
| dev.to | [I Built a Tested Data Pipeline for Dublin Bikes…](https://dev.to/malavnaik_0381711024683d4/i-built-a-tested-data-pipeline-for-dublin-bikes-for-eu0-3kc8) | malavnaik.com post | syndication | Self-owned |
| dev.to | [Migrating On-Prem SQL Server to Azure SQL PaaS…](https://dev.to/malavnaik_0381711024683d4/migrating-on-prem-sql-server-to-azure-sql-paas-how-we-cut-infrastructure-costs-by-25-2oo9) | not verified | syndication | Check that `canonical_url` is set |
| kaggle.com | [malavnaik/irish-rents-rtb](https://www.kaggle.com/datasets/malavnaik/irish-rents-rtb) | **malavnaik99.github.io** | dataset description | Old domain, so the link passes through a redirect. Update it to `https://malavnaik.com/projects/irish-rents/` |

Profiles listed in `_config.yml` that weren't found in the search index, so their links back are unverified: LinkedIn, Hugging Face (`Malavnaik`), Medium (`@malavnaik206`), X, Reddit. Kaggle notebooks found (5): moderation-threshold-sweep, searching-the-eu-digital-services-act, moderation-classifier-civil-comments, cleaning-irish-rents-rtb, and one untitled (`notebookea98a91e25`).

## Assessment
- Every referring domain found is **self-owned** (profiles and syndication). There are **no third-party editorial links** yet, so the prospect list in `seo/prospects.csv` is where real gains will come from.
- The only anchor text seen is the bare domain or "Originally published at…", which is natural.

## Quick wins (you do these on the other platforms)
1. Kaggle `irish-rents-rtb` description: change `malavnaik99.github.io` → `https://malavnaik.com/projects/irish-rents/`. Do the same in every Kaggle notebook and Hugging Face dataset/Space README that has the old domain.
2. Hugging Face: add a link to the matching project page in each Space and dataset card (moderation classifier demo, Ask the DSA, SkillBot explorer, Dublin bikes dataset).
3. GitHub repos: set each repo's "Website" field to its project page, e.g. `https://malavnaik.com/projects/dublin-bikes-pipeline/`.
