"""Builds the data for the Irish Rent Reality Check (malavnaik.com/rent/).

Downloads CSO table RIH02 (RTB average monthly rent of new tenancies, per half-year), cleans it the same way as
github.com/malavnaik99/irish-rents-dataset/clean.py, and CSO table DEA05 (median weekly earnings by county),
checks both, and only then writes:
  data/rent/rents.json   every place's rent per half-year, for "all bedrooms" and 1, 2, 3 and 4+ beds,
                         plus each county's typical pay and estimated take-home pay ("income")
  data/rent/meta.json    source, licence, latest half-year and the date the data last changed
  rent/<county>/index.html  one page per county: key facts, tables, neighbours, FAQ (regenerated every run)
  _data/rent_summary.json   one row per county, for the /rent/ hub's table and answers (regenerated every run)

If any check fails, nothing is written and the script exits with an error (the workflow then fails and opens an issue).

  python3 scripts/rent_build.py               download from the CSO and build
  python3 scripts/rent_build.py --source F --earnings G   build from saved copies of RIH02 and DEA05 (JSON-stat)
  python3 scripts/rent_build.py --pages-only  rewrite the pages from the saved data/rent files, no download
  python3 scripts/rent_build.py --self-test   quick checks of the code itself, no download
"""
import argparse
import datetime
import html
import itertools
import json
import os
import re
import statistics
import sys
import urllib.request

API = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{}/JSON-stat/2.0/en"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "rent")

# Same county list as clean.py.
COUNTIES = {"Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin", "Galway", "Kerry", "Kildare", "Kilkenny",
            "Laois", "Leitrim", "Limerick", "Longford", "Louth", "Mayo", "Meath", "Monaghan", "Offaly", "Roscommon",
            "Sligo", "Tipperary", "Waterford", "Westmeath", "Wexford", "Wicklow"}
# Bedroom categories shown on the page. "1 to 2 bed" and "1 to 3 bed" are left out: they overlap the others.
BEDS = {"All bedrooms": "all", "One bed": "1", "Two bed": "2", "Three bed": "3", "Four plus bed": "4"}
DIMS = {"HalfYear", "Number of Bedrooms", "Property Type", "Location"}  # the columns we expect from the CSO
TYPES = ["Apartment", "Detached house", "Semi detached house", "Terrace house", "Other flats"]  # county pages' type table
# Counties that share a land border (Republic of Ireland only). The self-test checks every pair goes both ways.
NEIGHBOURS = {
    "Carlow": ["Kildare", "Wicklow", "Wexford", "Kilkenny", "Laois"],
    "Cavan": ["Leitrim", "Longford", "Westmeath", "Meath", "Monaghan"],
    "Clare": ["Galway", "Tipperary", "Limerick"],
    "Cork": ["Kerry", "Limerick", "Tipperary", "Waterford"],
    "Donegal": ["Leitrim"],
    "Dublin": ["Meath", "Kildare", "Wicklow"],
    "Galway": ["Mayo", "Roscommon", "Offaly", "Tipperary", "Clare"],
    "Kerry": ["Cork", "Limerick"],
    "Kildare": ["Dublin", "Meath", "Offaly", "Laois", "Carlow", "Wicklow"],
    "Kilkenny": ["Carlow", "Laois", "Tipperary", "Waterford", "Wexford"],
    "Laois": ["Offaly", "Kildare", "Carlow", "Kilkenny", "Tipperary"],
    "Leitrim": ["Donegal", "Sligo", "Roscommon", "Longford", "Cavan"],
    "Limerick": ["Clare", "Tipperary", "Cork", "Kerry"],
    "Longford": ["Leitrim", "Roscommon", "Westmeath", "Cavan"],
    "Louth": ["Meath", "Monaghan"],
    "Mayo": ["Galway", "Roscommon", "Sligo"],
    "Meath": ["Louth", "Monaghan", "Cavan", "Westmeath", "Offaly", "Kildare", "Dublin"],
    "Monaghan": ["Cavan", "Meath", "Louth"],
    "Offaly": ["Westmeath", "Meath", "Kildare", "Laois", "Tipperary", "Galway", "Roscommon"],
    "Roscommon": ["Sligo", "Leitrim", "Longford", "Westmeath", "Offaly", "Galway", "Mayo"],
    "Sligo": ["Mayo", "Roscommon", "Leitrim"],
    "Tipperary": ["Galway", "Offaly", "Laois", "Kilkenny", "Waterford", "Cork", "Limerick", "Clare"],
    "Waterford": ["Cork", "Tipperary", "Kilkenny", "Wexford"],
    "Westmeath": ["Meath", "Cavan", "Longford", "Roscommon", "Offaly"],
    "Wexford": ["Wicklow", "Carlow", "Kilkenny", "Waterford"],
    "Wicklow": ["Dublin", "Kildare", "Carlow", "Wexford"],
}
RULE = 0.30  # "rent under 30% of take-home pay", a common budgeting rule of thumb, used for "what salary do I need"

# ---- Tax rates for a single PAYE employee. UPDATE ONCE A YEAR after the Budget (the build warns in January). ----
# Checked Nov 2026 on revenue.ie (USC standard rates, Budget 2026 summary) and gov.ie (PRSI Class A rates).
TAX = {
    "year": 2026,
    "band": 44_000, "low": 0.20, "high": 0.40,           # income tax: 20% up to the standard rate band, 40% above
    "credits": 4_000,                                     # personal tax credit €2,000 + employee (PAYE) credit €2,000
    "usc_exempt": 13_000,                                 # no USC at all if yearly income is €13,000 or less
    "usc": [(12_012, 0.005), (28_700, 0.02), (70_044, 0.03), (None, 0.08)],  # (band ends at €, rate)
    "prsi": 0.0435,                                       # Class A employee rate from 1 October 2026
}


def take_home_monthly(weekly):
    """Estimated monthly take-home pay of a single PAYE employee earning `weekly` gross, at TAX rates."""
    # shortcut: skips the PRSI credit for €352–€424 a week; fine while every county median is far above it.
    check(weekly > 424, f"Weekly pay €{weekly} is in the PRSI-credit range; take_home_monthly() needs updating.")
    year = weekly * 52
    tax = max(0, min(year, TAX["band"]) * TAX["low"] + max(0, year - TAX["band"]) * TAX["high"] - TAX["credits"])
    usc, start = 0, 0
    if year > TAX["usc_exempt"]:
        for end, rate in TAX["usc"]:
            top = year if end is None else min(year, end)
            usc += max(0, top - start) * rate
            start = end or start
    return (year - tax - usc - year * TAX["prsi"]) / 12


def salary_needed(rent):
    """Gross yearly pay (to the nearest €500) whose estimated take-home keeps `rent` at RULE of take-home pay."""
    want, lo, hi = rent / RULE, 425.0, 20_000.0
    check(take_home_monthly(lo) < want < take_home_monthly(hi), f"Rent €{rent} is outside what salary_needed() handles.")
    for _ in range(60):  # take-home rises with pay, so halve the range until it pins the weekly pay
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if take_home_monthly(mid) < want else (lo, mid)
    return round(hi * 52 / 500) * 500


def earnings_by_county(table, previous_meta=None):
    """CSO DEA05: median weekly earnings, both sexes, 15+, latest year, for each county. Raises CheckFailed."""
    names, rows = read_jsonstat(table)
    check({"Statistic", "Year", "Sex", "County", "Age Group"} <= set(names), f"DEA05's columns changed: {names}.")
    year = max(r["Year"] for r in rows if r["value"] not in (None, ""))
    if previous_meta and previous_meta.get("earnings_year"):
        check(year >= previous_meta["earnings_year"], f"The earnings year went backwards to {year}.")
    pay = {r["County"].replace("Co. ", ""): float(r["value"]) for r in rows
           if r["Year"] == year and r["Statistic"] == "Median Weekly Earnings" and r["Sex"] == "Both sexes"
           and r["Age Group"] == "15 years and over" and r["value"] not in (None, "")}
    check(COUNTIES <= set(pay), f"DEA05 has no {year} median pay for: {sorted(COUNTIES - set(pay))}.")
    bad = {c: v for c, v in pay.items() if not 300 <= v <= 3000}
    check(not bad, f"Median weekly pay outside €300–€3,000: {bad}.")
    if datetime.date.today().year > TAX["year"]:
        # GitHub shows this as a yellow warning; the refresh workflow turns it into an issue.
        print(f"::warning::The tax rates in scripts/rent_build.py are for {TAX['year']}. Update TAX for "
              f"{datetime.date.today().year} (see docs/rent-tool-runbook.md).")
    counties = {c: {"weekly": round(pay[c], 2), "take_home": round(take_home_monthly(pay[c]))} for c in sorted(COUNTIES)}
    return {"table": "DEA05", "year": year, "tax_year": TAX["year"], "counties": counties}


class CheckFailed(Exception):
    """A data check failed: the message says, in plain English, what is wrong."""


def check(ok, message):
    if not ok:
        raise CheckFailed(message)


def read_jsonstat(d):
    """Turn a JSON-stat 2.0 table into rows: one dict per cell, with 'value' None where nothing was published."""
    ids = d["id"]
    names, labels = [], []
    for k in ids:
        dim = d["dimension"][k]
        idx = dim["category"]["index"]
        order = sorted(idx, key=idx.get) if isinstance(idx, dict) else idx
        names.append(dim.get("label", k))
        labels.append([dim["category"]["label"][o] for o in order])
    values = d["value"]
    if isinstance(values, dict):  # JSON-stat may list only the filled cells
        values = [values.get(str(i)) for i in range(len(list(itertools.product(*labels))))]
    cells = list(itertools.product(*labels))
    check(len(cells) == len(values), f"The table's size doesn't add up ({len(cells)} cells, {len(values)} values).")
    return names, [dict(zip(names, c), value=v) for c, v in zip(cells, values)]


def level(name):
    """Same rule as clean.py: county by name, 'X, Y' is a smaller area, anything else a town or Dublin district."""
    if name in COUNTIES:
        return "county"
    return "area" if "," in name else "town"


def county_of(name):
    """'Tullow, Carlow' -> Carlow; 'Artane, Dublin 5' -> Dublin; 'Galway City' -> Galway; 'Dublin 6W' -> Dublin."""
    word = name.rsplit(",", 1)[-1].strip().split(" ")[0]
    check(word in COUNTIES, f"Couldn't tell which county '{name}' is in. Add a rule for it in county_of().")
    return word


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def build(table, earnings, previous_meta=None):
    """Clean and check the CSO table. Returns (rents, meta) or raises CheckFailed."""
    names, rows = read_jsonstat(table)
    check(DIMS <= set(names), f"The CSO table's columns changed. Expected {sorted(DIMS)}, got {names}.")
    check(next(iter(table["dimension"]["STATISTIC"]["category"]["label"].values())) == "RTB Average Monthly Rent Report",
          "The CSO table no longer holds the 'RTB Average Monthly Rent Report'.")

    # clean.py step 2: an empty cell means "not published" (too few tenancies), never zero, so drop it.
    pub = []
    for r in rows:
        v = r["value"]
        if v is None or v == "":
            continue
        r["value"] = float(v)
        r["Location"] = r["Location"].strip()
        pub.append(r)

    # clean.py step 5 checks: one row per half-year, place, bedrooms and property type; rents between €50 and €20,000.
    keys = {(r["HalfYear"], r["Location"], r["Number of Bedrooms"], r["Property Type"]) for r in pub}
    check(len(keys) == len(pub), "Some rents appear twice for the same half-year, place, bedrooms and property type.")
    bad = [r for r in pub if not 50 <= r["value"] <= 20000]
    check(not bad, f"{len(bad)} rents are outside €50–€20,000, e.g. {bad[:1]}.")
    check(150_000 <= len(pub) <= 600_000, f"The table has {len(pub):,} published rents; expected 150,000–600,000.")
    if previous_meta:
        check(len(pub) >= previous_meta["rows"] * 0.98,
              f"The table shrank from {previous_meta['rows']:,} to {len(pub):,} published rents.")

    periods = sorted({r["HalfYear"] for r in rows})
    check(all(re.fullmatch(r"\d{4}H[12]", p) for p in periods), f"Unexpected half-year labels: {periods[-3:]}.")
    latest = max(r["HalfYear"] for r in pub)
    if previous_meta:
        check(latest >= previous_meta["latest_period"],
              f"The latest half-year went backwards, from {previous_meta['latest_period']} to {latest}.")
    periods = [p for p in periods if p <= latest]  # ignore any future half-year the CSO lists before filling it

    # The page uses "All property types" and five bedroom categories (all, 1, 2, 3, 4+).
    col = {p: i for i, p in enumerate(periods)}
    rent, places = {}, {}
    for r in pub:
        if r["Property Type"] != "All property types" or r["Number of Bedrooms"] not in BEDS:
            continue
        name = r["Location"]
        pid = slug(name)
        places.setdefault(pid, {"id": pid, "name": name, "county": county_of(name), "level": level(name)})
        check(places[pid]["name"] == name, f"Two places share the web address '{pid}'.")
        series = rent.setdefault(pid, {}).setdefault(BEDS[r["Number of Bedrooms"]], [None] * len(periods))
        series[col[r["HalfYear"]]] = round(r["value"])

    # Each county's latest rent by property type (all bedrooms), for the county pages.
    types = {}
    for r in pub:
        if r["Location"] in COUNTIES and r["HalfYear"] == latest and r["Number of Bedrooms"] == "All bedrooms" \
                and r["Property Type"] in TYPES:
            types.setdefault(slug(r["Location"]), {})[r["Property Type"]] = round(r["value"])

    # No sudden empty data: every county must have an "all bedrooms" rent for the latest half-year, in a sane range.
    counties = [p for p in places.values() if p["level"] == "county"]
    check(len(counties) == 26, f"Expected 26 counties, found {len(counties)}.")
    check(400 <= len(places) <= 600, f"Expected 400–600 places, found {len(places)}.")
    for c in counties:
        v = rent[c["id"]].get("all", [None])[-1]
        check(v is not None, f"{c['name']} has no rent for {latest}: the latest data looks incomplete.")
        check(300 <= v <= 6000, f"{c['name']}'s average rent for {latest} is €{v}, outside €300–€6,000.")

    out = {
        "periods": periods,
        "places": sorted(places.values(), key=lambda p: (p["county"], p["level"] != "county", p["name"])),
        "rent": {pid: rent[pid] for pid in sorted(rent)},
        "types": {c: types[c] for c in sorted(types)},
        "income": earnings_by_county(earnings, previous_meta),
    }
    meta = {
        "source": "CSO table RIH02, RTB Average Monthly Rent Report (Residential Tenancies Board)",
        "source_url": "https://data.cso.ie/table/RIH02",
        "licence": "CC BY 4.0",
        "licence_url": "https://creativecommons.org/licenses/by/4.0/",
        "cso_updated": table.get("updated", "")[:10],
        "latest_period": latest,
        "rows": len(pub),
        "places": len(places),
        "earnings_source": "CSO table DEA05, median weekly earnings by county (Distribution of Earnings by Gender and County)",
        "earnings_url": "https://data.cso.ie/table/DEA05",
        "earnings_year": out["income"]["year"],
        "tax_year": TAX["year"],
    }
    return out, meta


def write(out, meta):
    """Write the files only if the data changed; 'last_updated' is the date it last changed."""
    os.makedirs(OUT, exist_ok=True)
    text = json.dumps(out, separators=(",", ":"), ensure_ascii=False)
    path = os.path.join(OUT, "rents.json")
    if os.path.exists(path) and open(path, encoding="utf-8").read() == text:
        print("No change: the CSO data is the same as last time, so nothing was written.")
        return False
    meta["last_updated"] = datetime.date.today().isoformat()
    for name, body in [("rents.json", text), ("meta.json", json.dumps(meta, indent=1, ensure_ascii=False) + "\n")]:
        tmp = os.path.join(OUT, name + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(body)
        os.replace(tmp, os.path.join(OUT, name))  # swap in whole, so a crash never leaves half a file
    print(f"Updated: {meta['rows']:,} rents, {meta['places']} places, latest {meta['latest_period']}.")
    return True


# ---- County pages (/rent/galway/ etc.): written from the checked data, so they always match the tool ----
def when(p):
    return ("January–June " if p.endswith("1") else "July–December ") + p[:4]


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def change(s, i, years):
    """'up €869 (67%)' between half-year i and the same half-year `years` earlier, or None if either is missing."""
    j = i - 2 * years
    if j < 0 or s[j] is None:
        return None
    d, pct = s[i] - s[j], round((s[i] / s[j] - 1) * 100)
    return f"{'up' if d >= 0 else 'down'} €{abs(d):,} ({abs(pct)}%)"


def nice_date(iso):
    d = datetime.date.fromisoformat(iso[:10])
    return f"{d.day} {d:%B %Y}"


def pct_text(p):
    return "–" if p is None else f"{'+' if p >= 0 else '−'}{abs(p)}%"


def summary(out, meta):
    """One row per county, most expensive first. The /rent/ hub (via _data/rent_summary.json) and the county pages read it."""
    P, rent, inc = out["periods"], out["rent"], out["income"]
    rows = []
    for c in sorted(COUNTIES):
        s = rent[slug(c)]["all"]  # build() checked every county has a rent for the latest half-year
        now, prev = s[-1], (s[-3] if len(s) > 2 else None)
        pay = inc["counties"][c]
        rows.append({"name": c, "id": slug(c), "rent": now, "rent_eur": f"€{now:,}",
                     "change_pct": round((now / prev - 1) * 100) if prev else None,
                     "weekly_pay": pay["weekly"], "take_home": pay["take_home"],
                     "share_pct": round(now / pay["take_home"] * 100)})
    rows.sort(key=lambda r: (-r["rent"], r["name"]))
    for k, r in enumerate(rows, 1):
        r["rank"] = k
    return {"latest_period": P[-1], "latest_label": when(P[-1]), "year": P[-1][:4],
            "data_updated": nice_date(meta.get("cso_updated") or meta["last_updated"]), "site_changed": nice_date(meta["last_updated"]),
            "earnings_year": inc["year"], "tax_year": inc["tax_year"],
            "median_rent": round(statistics.median(r["rent"] for r in rows)),
            "median_eur": f"€{round(statistics.median(r['rent'] for r in rows)):,}", "counties": rows}


def county_page(c, out, meta, summ):
    P, rent, e = out["periods"], out["rent"], html.escape
    by = {r["name"]: r for r in summ["counties"]}
    me, cid, inc = by[c], slug(c), out["income"]["counties"][c]
    s, i = rent[cid]["all"], len(P) - 1
    now, period, yr = s[i], when(P[i]), P[i][:4]
    ch1, ch10 = change(s, i, 1), change(s, i, 10)
    share, salary, med = me["share_pct"], salary_needed(now), summ["median_rent"]
    nbrs = sorted((by[n] for n in NEIGHBOURS[c]), key=lambda r: (-r["rent"], r["name"]))
    close = min(nbrs, key=lambda r: (abs(r["rent"] - now), r["name"]))  # the most interesting "is it cheaper than…"
    source = (f'Data last updated: {summ["data_updated"]} · Source: RTB via CSO (<a href="https://data.cso.ie/table/RIH02">RIH02</a>), '
              f'earnings CSO (<a href="https://data.cso.ie/table/DEA05">DEA05</a>)')

    # ---- FAQ: every answer is worked out from the data above ----
    faq = [(f"What is the average rent in {c}?",
            f"€{now:,} a month for a new tenancy in {period}, averaged over all homes (RTB figures published by the CSO).")]
    if ch1:
        faq.append((f"Is rent going up in {c}?",
                    f"{'Yes' if s[i] > s[i - 2] else 'No'}: the average new rent is {ch1} on a year earlier"
                    + (f", and {ch10} on ten years earlier." if ch10 else ".")))
    n, nr = close["name"], close["rent"]
    faq.append((f"Is {c} cheaper than {n}?",
                f"Yes. The average new rent is €{now:,} a month in {c} and €{nr:,} in {n}, so {c} is €{nr - now:,} a month cheaper ({period})."
                if now < nr else
                f"No. The average new rent is €{now:,} a month in {c} and €{nr:,} in {n}, so {c} is €{now - nr:,} a month dearer ({period})."
                if now > nr else f"They are the same: the average new rent is €{now:,} a month in both ({period})."))
    faq.append((f"What salary do I need to rent in {c}?",
                f"About €{salary:,} a year before tax, for one person paying the average new rent of €{now:,} a month. "
                f"That keeps rent to {round(RULE * 100)}% of take-home pay, a common budgeting rule of thumb "
                f"(estimated at {out['income']['tax_year']} Irish tax rates for a single PAYE employee)."))
    faq.append((f"How much of a typical wage goes on rent in {c}?",
                f"About {share}%. Median pay in Co. {c} is €{inc['weekly']:,.2f} a week before tax ({out['income']['year']}, CSO), "
                f"roughly €{inc['take_home']:,} a month after tax, and the average new rent is €{now:,} a month."))

    beds = "".join(
        f"<tr><td>{label}</td><td>{'€{:,}'.format(v[-1]) if v and v[-1] is not None else '–'}</td></tr>"
        for key, label in [("all", "All homes"), ("1", "1 bed"), ("2", "2 beds"), ("3", "3 beds"), ("4", "4+ beds")]
        for v in [rent[cid].get(key)])
    types = out.get("types", {}).get(cid, {})
    type_rows = "".join(f"<tr><td>{t.replace('Semi detached', 'Semi-detached').replace('Terrace house', 'Terraced house')}</td>"
                        f"<td>{'€{:,}'.format(types[t]) if t in types else '–'}</td></tr>" for t in TYPES)
    areas = []
    for p in out["places"]:
        a = rent[p["id"]].get("all", [])
        k = max((k for k, v in enumerate(a) if v is not None), default=-1)
        if p["county"] == c and p["level"] != "county" and k >= len(P) - 5:  # same 2-year rule as the finder
            areas.append((a[k], p, P[k]))
    rows = "".join(f'<tr><td><a href="/rent/?area={p["id"]}">{e(p["name"])}</a></td><td>€{v:,}</td><td>{when(w)}</td></tr>'
                   for v, p, w in sorted(areas, key=lambda r: (-r[0], r[1]["name"])))
    cmp_rows = "".join(
        f'<tr><td>{"<strong>" + e(r["name"]) + "</strong>" if r is me else f"""<a href="/rent/{r["id"]}/">{e(r["name"])}</a>"""}</td>'
        f'<td>€{r["rent"]:,}</td><td>{pct_text(r["change_pct"])}</td><td>{r["share_pct"]}%</td></tr>'
        for r in sorted(nbrs + [me], key=lambda r: (-r["rent"], r["name"])))
    gap = now - med
    vs_mid = ("exactly the middle county's" if gap == 0 else
              f"€{abs(gap):,} ({abs(round(gap / med * 100))}%) {'above' if gap > 0 else 'below'} the middle county's")

    title = f"Average Rent in {c} {yr}: €{now:,}/month"
    desc = (f"The average new rent in County {c} is €{now:,} a month ({period})"
            + (f", {ch1.split(' (')[0]} on a year" if ch1 else "")
            + f". By bedrooms, property type and town, rent vs pay, neighbouring counties and FAQs, from official RTB data.")
    dataset = {"name": f"Average monthly rent of new tenancies in County {c}, 2008–{yr}",
               "description": f"The Residential Tenancies Board's average monthly rent for new tenancies in County {c} and its towns, "
                              f"by bedrooms and property type, every half-year since 2008, published by the CSO in table RIH02.",
               "url": "https://data.cso.ie/table/RIH02", "license": "https://creativecommons.org/licenses/by/4.0/",
               "place": f"County {c}, Ireland", "keywords": ["rent", c, "Ireland", "RTB", "CSO", "housing"],
               "sources": ["https://data.cso.ie/table/RIH02", "https://data.cso.ie/table/DEA05"],
               "creator": "Residential Tenancies Board (RTB), published by the Central Statistics Office (CSO)"}
    fm = lambda v: json.dumps(v, ensure_ascii=False)  # JSON is valid YAML, and safe for any text
    return f"""---
# Written by scripts/rent_build.py from data/rent/rents.json. Don't edit by hand: changes are overwritten on the next refresh.
layout: default
title: {fm(title)}
description: {fm(desc)}
rent_county: {fm(c)}
image: {{ path: /images/rent/og.png, width: 1200, height: 630, alt: "Irish Rent Reality Check at malavnaik.com/rent" }}
dataset: {fm(dataset)}
faq: {fm([{"q": q, "a": a} for q, a in faq])}
---
<p class="eyebrow"><a href="/rent/">Irish Rent Reality Check</a> / {e(c)}</p>
<h1>Average rent in {e(c)} ({yr})</h1>
<p class="lead" style="max-width:46rem">The average monthly rent for a new tenancy in County {e(c)} was <strong>€{now:,}</strong> in {period}{f", {ch1} on a year earlier" if ch1 else ""}.</p>
<p class="small muted">{source}</p>
<p style="max-width:46rem">{e(c)} is the {'most' if me['rank'] == 1 else ordinal(me['rank']) + ' most'} expensive of Ireland's 26 counties for new rents{f", and rents are {ch10} on ten years earlier" if ch10 else ""}. On typical pay in Co. {e(c)}, the average rent takes about {share}% of take-home pay.</p>
<p><a class="btn btn-accent" href="/rent/?area={cid}">Explore {e(c)} in the rent tool</a></p>

<section class="card" style="margin:1.5rem 0" aria-labelledby="beds-title">
  <h2 id="beds-title">By number of bedrooms, {when(P[-1])}</h2>
  <table><thead><tr><th scope="col">Bedrooms</th><th scope="col">Average monthly rent</th></tr></thead><tbody>{beds}</tbody></table>
  <p class="small muted">– means the RTB published no average: too few new tenancies were registered.</p>
</section>
{f'''
<section class="card" style="margin:1.5rem 0" aria-labelledby="types-title">
  <h2 id="types-title">By property type, {when(P[-1])}</h2>
  <table><thead><tr><th scope="col">Property type</th><th scope="col">Average monthly rent</th></tr></thead><tbody>{type_rows}</tbody></table>
  <p class="small muted">All bedroom counts. – means the RTB published no average for that type.</p>
</section>
''' if types else ''}
<section class="card" style="margin:1.5rem 0" aria-labelledby="areas-title">
  <h2 id="areas-title">Towns and areas in {e(c)}, all homes</h2>
  <div style="overflow-x:auto"><table><thead><tr><th scope="col">Area</th><th scope="col">Average monthly rent</th><th scope="col">Half-year</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="small muted">Most expensive first. Areas without a published figure since {when(P[-5])} are left out.</p>
</section>

<section class="card" style="margin:1.5rem 0" aria-labelledby="pay-title">
  <h2 id="pay-title">Rent vs pay in {e(c)}</h2>
  <table><tbody>
    <tr><th scope="row">Median weekly pay, before tax ({out["income"]["year"]})</th><td>€{inc["weekly"]:,.2f}</td></tr>
    <tr><th scope="row">Estimated take-home pay a month</th><td>€{inc["take_home"]:,}</td></tr>
    <tr><th scope="row">Average new rent a month</th><td>€{now:,}</td></tr>
    <tr><th scope="row">Share of take-home pay on rent</th><td>{share}%</td></tr>
    <tr><th scope="row">Pay needed to keep rent to {round(RULE * 100)}% of take-home</th><td>about €{salary:,} a year</td></tr>
  </tbody></table>
  <p class="small muted">One person on the county's median pay, after income tax, USC and PRSI at {out["income"]["tax_year"]} rates (single PAYE employee). An estimate, not tax advice.</p>
</section>

<section class="card" style="margin:1.5rem 0" aria-labelledby="compare-title">
  <h2 id="compare-title">How {e(c)} compares</h2>
  <p>At €{now:,} a month, {e(c)}'s average new rent is {vs_mid} (€{med:,}: half of Ireland's 26 counties are dearer, half cheaper). The CSO's average-rent tables don't include a national figure, so this compares with the middle county instead. Neighbouring counties:</p>
  <div style="overflow-x:auto"><table><thead><tr><th scope="col">County</th><th scope="col">Average monthly rent</th><th scope="col">Change on a year</th><th scope="col">Share of take-home pay</th></tr></thead><tbody>{cmp_rows}</tbody></table></div>
  <p class="small muted">{when(P[-1])}. <a href="/rent/#counties-title">All 26 counties</a>.</p>
</section>

<section style="margin:1.5rem 0" aria-labelledby="faq-title">
  <h2 id="faq-title">Frequently asked questions</h2>
  {"".join(f"<h3>{e(q)}</h3><p>{e(a)}</p>" for q, a in faq)}
</section>

<p class="small muted">Averages for <strong>new</strong> tenancies registered with the RTB, not what every tenant pays, and not adjusted for inflation.
Take-home pay: median weekly earnings in Co. {e(c)} ({out["income"]["year"]}, €{inc["weekly"]:,.2f} before tax, CSO table DEA05), estimated after tax for one PAYE earner at {out["income"]["tax_year"]} rates.
Sources: <a href="https://data.cso.ie/table/RIH02">CSO table RIH02</a> and <a href="https://data.cso.ie/table/DEA05">DEA05</a>, © CSO and RTB, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.</p>
"""


def write_pages(out, meta):
    """Write rent/<county>/index.html for all 26 counties and _data/rent_summary.json for the hub.
    Same data in, same files out, so git only sees real changes."""
    summ = summary(out, meta)
    for c in COUNTIES:
        page = county_page(c, out, meta, summ)
        assert f"€{out['rent'][slug(c)]['all'][-1]:,}" in page and page.count("<h3>") >= 4 and "Data last updated" in page, c
        os.makedirs(os.path.join(ROOT, "rent", slug(c)), exist_ok=True)
        with open(os.path.join(ROOT, "rent", slug(c), "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
    with open(os.path.join(ROOT, "_data", "rent_summary.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(summ, indent=1, ensure_ascii=False) + "\n")
    print(f"Wrote {len(COUNTIES)} county pages in rent/ and _data/rent_summary.json (latest {out['periods'][-1]}).")


def self_test():
    assert county_of("Tullow, Carlow") == "Carlow" and county_of("Artane, Dublin 5") == "Dublin"
    assert county_of("Galway City") == "Galway" and county_of("Dublin 6W") == "Dublin"
    assert level("Cork") == "county" and level("Cork City") == "town" and level("Tullow, Carlow") == "area"
    assert slug("Artane, Dublin 5") == "artane-dublin-5" and slug("Dublin 6W") == "dublin-6w"
    try:
        county_of("Atlantis")
        raise AssertionError("county_of should reject unknown places")
    except CheckFailed:
        pass
    # A tiny JSON-stat table, read back cell by cell (sparse "value" form included).
    t = {"id": ["A", "B"], "dimension": {"A": {"label": "A", "category": {"index": ["x", "y"], "label": {"x": "X", "y": "Y"}}},
                                         "B": {"label": "B", "category": {"index": {"p": 0, "q": 1}, "label": {"p": "P", "q": "Q"}}}},
         "value": {"1": 5, "2": 7}}
    _, rows = read_jsonstat(t)
    assert [(r["A"], r["B"], r["value"]) for r in rows] == [("X", "P", None), ("X", "Q", 5), ("Y", "P", 7), ("Y", "Q", None)]
    # Hand-worked: €848.06 a week = €44,099.12 a year. Tax 8,800 + 99.12×40% − 4,000 = 4,839.65.
    # USC 60.06 + 333.76 + 15,399.12×3% = 855.79. PRSI 1,918.31. Take-home 36,485.37 / 12 = 3,040.45.
    assert round(take_home_monthly(848.06), 2) == 3040.45, take_home_monthly(848.06)
    # €500 a week = €26,000: tax 5,200 − 4,000 = 1,200; USC 60.06 + 13,988×2% = 339.82; PRSI 1,131.
    assert round(take_home_monthly(500), 2) == round((26000 - 1200 - 339.82 - 1131) / 12, 2)
    assert [ordinal(n) for n in (1, 2, 3, 4, 11, 12, 13, 21, 22)] == ["1st", "2nd", "3rd", "4th", "11th", "12th", "13th", "21st", "22nd"]
    assert change([100, None, 150], 2, 1) == "up €50 (50%)" and change([100, None, None, 150], 3, 1) is None
    assert set(NEIGHBOURS) == COUNTIES and all(c in NEIGHBOURS[n] for c in COUNTIES for n in NEIGHBOURS[c]), "NEIGHBOURS isn't two-way"
    for r in (900, 1500, 2600):  # the pay found really does keep rent at about 30% of take-home (within the €500 rounding)
        assert abs(take_home_monthly(salary_needed(r) / 52) * RULE - r) < 15, r
    assert nice_date("2026-05-14T11:00:00Z") == "14 May 2026" and pct_text(-3) == "−3%" and pct_text(None) == "–"
    print("Self-test passed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="saved JSON-stat copy of RIH02 instead of downloading")
    ap.add_argument("--earnings", help="saved JSON-stat copy of DEA05 instead of downloading")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--pages-only", action="store_true", help="rewrite the pages from the saved data, no download")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    meta_path = os.path.join(OUT, "meta.json")
    if a.pages_only:
        return write_pages(json.load(open(os.path.join(OUT, "rents.json"), encoding="utf-8")), json.load(open(meta_path)))
    def load(path, code):
        if path:
            return json.load(open(path, encoding="utf-8"))
        with urllib.request.urlopen(API.format(code), timeout=300) as r:
            return json.load(r)
    table, earnings = load(a.source, "RIH02"), load(a.earnings, "DEA05")
    previous = json.load(open(meta_path)) if os.path.exists(meta_path) else None
    try:
        out, meta = build(table, earnings, previous)
    except CheckFailed as e:
        sys.exit(f"CHECK FAILED, nothing was published: {e}")
    write(out, meta)
    write_pages(out, json.load(open(meta_path)))


if __name__ == "__main__":
    main()
