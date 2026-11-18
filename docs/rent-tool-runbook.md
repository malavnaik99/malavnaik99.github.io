# Rent tool runbook (malavnaik.com/rent/)

Plain-English guide to the automatic refresh of the **Irish Rent Reality Check**: how to tell if it's broken, how to
re-run it, and how to undo a bad update. You never need to edit code to follow it.

## What runs, and when

- **Workflow:** GitHub → **Actions** → **Rent tool refresh** (file `.github/workflows/rent-refresh.yml`).
- **When:** every Wednesday at 05:23 UTC, plus whenever you press **Run workflow**.
- **What it does:**
  1. Downloads two official tables from the CSO's open data API:
     - **RIH02**: RTB average monthly rent of new tenancies, every half-year;
     - **DEA05**: median weekly earnings by county.
  2. Cleans and **checks** them with `scripts/rent_build.py`:
     - the expected columns are there;
     - the row count is in range and hasn't shrunk;
     - every county has a latest rent;
     - all rents are €50–€20,000;
     - all 26 counties have pay data.
  3. If everything passes **and** the data changed, it saves the new data, rebuilds the 26 county pages, commits to `main`
     and starts **Deploy site to Pages**. The site updates a few minutes later.
  4. If the data didn't change (most weeks: the CSO only publishes new rents a few times a year), it does nothing.
- **Where things live:**
  - `data/rent/rents.json`: all the numbers the page uses;
  - `data/rent/meta.json`: source, latest half-year, and the date the data last changed;
  - `rent/<county>/index.html`: the county pages. They're written by the script; don't edit them by hand.

## How to tell if it's broken

| You see | It means |
|---|---|
| Email from GitHub: *"Run failed: Rent tool refresh"*, and a red ❌ in **Actions** | This week's refresh failed. **The live site is fine**: it keeps the last good data. |
| Issue **Rent tool: weekly refresh failed** | Same thing. The issue quotes the reason (look for `CHECK FAILED`) and closes itself after the next good run. |
| Issue **Rent tool: update the tax rates** | It's a new year and the tax rates need updating. See "Update the tax rates" below. Rents still refresh. |
| The page's "Data last changed" date is old | Usually normal: the CSO hasn't published new rents yet. Check https://data.cso.ie/table/RIH02. If it has a newer half-year than the page's "Latest rents", something is wrong: re-run (below). |
| No **Rent tool refresh** run for weeks | GitHub pauses scheduled workflows after 60 days without repo activity. **Actions → Rent tool refresh → Enable workflow**. |

## How to re-run it

GitHub → **Actions** → **Rent tool refresh** (left list) → **Run workflow** → **Run workflow**. Takes 1–2 minutes.
Green ✅ = done (it either published new data or found nothing new; the run's log says which).

## The refresh failed: what to do

Open the failed run (or the issue) and find the line starting `CHECK FAILED`, or the last red error.

| The message says | It means | Do this |
|---|---|---|
| `HTTP Error 5xx`, `timed out`, `Connection reset`, `URLError` | The CSO's website was down or slow | Wait a day, then **Run workflow**. Usually fixes itself. |
| `The CSO table's columns changed` or `DEA05's columns changed` | The CSO renamed or restructured a table | Open Claude Code on this repo and paste the issue. Don't change the checks yourself. |
| `The table shrank` or `latest half-year went backwards` | The CSO republished the table with less data, possibly by mistake | Look at https://data.cso.ie/table/RIH02. If it looks wrong there too, wait a week and re-run. If it still fails, ask Claude. |
| `has no rent for …: the latest data looks incomplete` | The CSO published a half-year with missing counties | Wait a few days (they usually complete it), then re-run. |
| `rents are outside €50–€20,000` or `Median weekly pay outside €300–€3,000` | A number looks impossible | Ask Claude with the issue text. **Don't loosen the check** without looking at the data: it's what stops nonsense going live. |
| `Couldn't tell which county '…' is in` | The CSO added a place with a new kind of name | Ask Claude: "Add a county rule for this place in county_of() in scripts/rent_build.py". |
| `in the PRSI-credit range; take_home_monthly() needs updating` | A county's typical pay dropped below €424 a week (very unlikely) | Ask Claude to add the PRSI credit to `take_home_monthly()`. |
| `rejected` / `failed to push` | `main` changed while the job ran, or a branch rule blocked the bot | Just **Run workflow** again. If it keeps happening, check **Settings → Branches** for a rule on `main`. |

## Update the tax rates (once a year, after the Budget)

The "Can you afford it?" estimate uses one year's income tax, USC and PRSI rates, kept in the `TAX` block near the top of
`scripts/rent_build.py`. In January the workflow opens **Rent tool: update the tax rates**.

1. Open Claude Code on this repo and say: *"Update the TAX block in scripts/rent_build.py to this year's Irish tax rates for a single PAYE employee, verified on revenue.ie and gov.ie, update the self-test, and run it."*
2. Check that it quotes the official pages for each rate, then let it commit and (with your OK) merge.
3. Run **Actions → Rent tool refresh → Run workflow**. The issue closes itself.

## Roll back a bad update

Each update is a single commit by `github-actions[bot]` called **"Rent tool: new CSO data (latest …)"**.

**Easiest:** open Claude Code on this repo and say: *"Revert the last 'Rent tool: new CSO data' commit on main and redeploy."*

**By hand** (in a terminal, in this repo). Find the commit:

```bash
git log --oneline -5 -- data/rent
```

Revert it, using the ID shown next to "Rent tool: new CSO data":

```bash
git revert --no-edit COMMIT_ID
```

```bash
git push origin main
```

Then GitHub → **Actions** → **Deploy site to Pages** → **Run workflow**.

To stop the next weekly run putting the bad data back, pause the refresh first: **Actions → Rent tool refresh → ⋯ →
Disable workflow**. Turn it back on with **Enable workflow** once the CSO has fixed its data.

## Run it on your own computer (optional)

```bash
python3 scripts/rent_build.py --self-test
```

```bash
python3 scripts/rent_build.py
```

It uses only standard Python, so no packages need installing. It prints `Updated: …`, `No change: …` or
`CHECK FAILED, …`. A failed check never changes any files.
