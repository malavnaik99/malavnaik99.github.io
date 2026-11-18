# Irish Rent Reality Check — plan (malavnaik.com/rent/)

## Context
Malav wants a free, shareable tool at `/rent/` that answers "what does renting cost where I live, and where can I afford?", built on his existing cleaned RTB rents work, to earn backlinks and show recruiters data-engineering skill. It must be static, cheap to run, refresh by itself and fail safely. Once approved, this plan is copied to `docs/rent-tool-plan.md` (the first commit).

## What I found in the repo
- The site is **Jekyll on GitHub Pages** (`_config.yml`, `_layouts/default.html`). A page's `title:` automatically becomes `"<title> | Malav Naik | Data & GenAI Engineer | Dublin, Ireland"`, so the brand pattern comes for free.
- **The cleaning pipeline is not in this repo.** It's in `github.com/malavnaik99/irish-rents-dataset` (`clean.py`: download → tidy columns → drop unpublished rents → label county/town/area → flag totals → checks). This repo holds only the write-up (`_projects/irish-rents.md`, `_posts/2026-11-02-cleaning-irish-rents-open-data.md`).
- **Table:** your pipeline uses **RIH02 (half-yearly)**, not RIQ02. RIQ02 exists and is quarterly (a third-party mirror lists data up to 2025 Q4), but I couldn't check what it breaks down by, because this session can't reach the CSO. **UNVERIFIED** until Phase 2.
- I'll reuse what's already here:
  - **Chart.js 4.4.1** is already self-hosted at `assets/vendor/chart-4.4.1.umd.js`, and `permits-2025/index.html` already loads it lazily. Self-hosted is faster and safer than a CDN, so I'll reuse it.
  - `_includes/schema.html` already writes `Dataset` JSON-LD from a page's `dataset:` front matter.
  - `jekyll-sitemap` adds every new page to `sitemap.xml` automatically.
  - `robots.txt` already allows everything.
  - The analytics, GoatCounter, sets no cookies.
- **Blocker:** this cloud session's network refuses `ws.cso.ie` (the CSO API). At the start of Phase 2 I'll ask you to allow that one host. You'll get an approval prompt. GitHub Actions itself has no such limit.

## Decisions (one line each)
1. **Data table (decided in Phase 2): RIH02, half-yearly.** RIQ02 does exist with the same breakdowns, but it ends at the same point (late 2025, both updated by the CSO on 14 May 2026), so it isn't fresher, and it publishes fewer areas for the latest period (306 vs 324). RIH02 also matches the published dataset exactly (201,912 rents). The page says "half-year". The script reads the CSO's JSON-stat format (4 MB) instead of CSV (94 MB; the RIQ02 CSV even came back empty).
2. **Reusing your cleaning:** I copy the ~40 lines of cleaning logic from `clean.py` into one script here, `scripts/rent_build.py`, with a comment pointing to the original. Your `clean.py` downloads data the moment it's loaded, so it can't be safely plugged in from another repo. The page uses only the "All property types" rows.
3. **Places:** every place is given its county. Areas use the text after their last comma; towns and Dublin postal districts use a small lookup table. The script stops with an error if any place is left without a county.
4. **Data files:** the script writes a compact `data/rent/rents.json`, with `meta.json` beside it. If it's over ~150 KB gzipped, I split it into one file per county, loaded only when needed. I'll measure before choosing.
5. **Income (CSO earnings table):** the table ID is **UNVERIFIED** until I can reach the CSO in Phase 4.
   - **First choice:** CSO median weekly earnings by county (region of residence) from the *Earnings Analysis using Administrative Data Sources* release.
   - **Fallback:** the national average weekly earnings, EHQ03.
   - Take-home pay is estimated for a single PAYE worker, using this year's income tax, USC and PRSI rates, verified on gov.ie or Revenue. Those rates live in one small, clearly labelled block that needs updating once a year after the Budget, and the workflow opens an Issue when they're out of date.
   - "Enter my own monthly income" is always available.
6. **County SEO pages:** the build script writes `rent/<county>/index.html`, 26 static pages. Each has its own title and description, 2–3 sentences of facts, a table of that county's areas, and an "Open in the tool" link. They're regenerated on every refresh.
7. **Share image:** the browser draws it itself on a 1200×630 canvas: chart, title, figures and "malavnaik.com/rent", saved as a PNG. No library or server is needed. The default Open Graph image is one static PNG made once by the build script.
8. **Refresh workflow:**
   - **Schedule:** weekly, plus a "Run workflow" button.
   - **Checks:** columns, row counts, non-empty data and rent ranges. Each failure prints a plain-English reason.
   - **If any check fails:** nothing is written, the run fails (you get GitHub's email), and a GitHub Issue explains the fix, as your CLAUDE.md requires.
   - **If the data changed:** the workflow commits to `main`, then starts the "Deploy site to Pages" workflow itself, because a bot's push doesn't trigger it.
   - **If the data didn't change:** nothing is committed. `meta.json` therefore records when the data last changed and the latest period, not the weekly check, to avoid a pointless commit every week.

## Files
- **New:**
  - `scripts/rent_build.py`: download, clean, validate, write JSON and county pages; includes `--self-test` with small built-in checks.
  - `rent/index.html`: the tool, with inline JS and CSS, following the `permits-2025/index.html` pattern.
  - `rent/<county>/index.html`: generated.
  - `data/rent/rents.json` and `data/rent/meta.json`.
  - `images/rent/og.png`: the default share image.
  - `.github/workflows/rent-refresh.yml`.
  - `docs/rent-tool-plan.md` and `docs/rent-tool-runbook.md`.
- **Small edits, each only with your OK at that phase:**
  - `_includes/schema.html`: add a WebApplication block for the `/rent/` page only.
  - `_projects/irish-rents.md`: add a link to the tool.
  - Homepage `index.md`: **I'll ask you where before touching it.**
  - `MAINTENANCE.md`: one entry pointing to the runbook.
  - `llms.txt`: one line.
- **Never touched:** `CNAME`, DNS, existing URLs and styles.

## Phases (I stop after each one and wait for your OK)
1. Copy this plan into `docs/rent-tool-plan.md` and commit it on branch `rent-tool`.
2. Data script, checks and JSON. I'll show you the first rows and the figures for Dublin, Cork and Galway, so you can compare them with the numbers already on your project page (for example, Dublin €2,162 in late 2025).
3. `/rent/`: area and bedroom picker, rent card (latest figure, 1/5/10-year change in € and %), trend chart comparing up to 3 areas, and links that save your view in the address.
4. Affordability (I'll name the CSO table I picked and why) and the "Where can I afford?" finder.
5. Share image button, the 26 county pages, meta and Open Graph tags, JSON-LD, and links from your homepage and project page (homepage spot: I'll ask you).
6. Refresh workflow and the plain-English runbook.
7. Final check:
   - test at phone size with Playwright;
   - check for broken links;
   - run Lighthouse on mobile (target 90+);
   - compare 3 random areas against the CSO source;
   - give you a launch checklist.

## Verification
- `python3 scripts/rent_build.py --self-test`, plus a full run, compared with the totals your dataset already gives (201,912 rows on RIH02).
- Preview locally with `jekyll build` and a local server, then use Playwright at 390 px and 1280 px to check: keyboard use, the address saving your view, PNG export, and the county pages.
- Lighthouse for mobile, run on the local preview.
- Test the workflow's "checks failed" path by feeding it deliberately broken data. It must leave the old JSON untouched and fail the run.

## Git note
I commit locally on `rent-tool` after each phase. This cloud session can only push to the branch `claude/inspiring-euler-mnn6px`. When you OK a push, it goes there. Nothing goes to `main` without your approval.
