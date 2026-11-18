"""Builds the data for the Irish Rent Reality Check (malavnaik.com/rent/).

Downloads CSO table RIH02 (RTB average monthly rent of new tenancies, per half-year), cleans it the same way as
github.com/malavnaik99/irish-rents-dataset/clean.py, and CSO table DEA05 (median weekly earnings by county),
checks both, and only then writes:
  data/rent/rents.json   every place's rent per half-year, for "all bedrooms" and 1, 2, 3 and 4+ beds,
                         plus each county's typical pay and estimated take-home pay ("income")
  data/rent/meta.json    source, licence, latest half-year and the date the data last changed
  rent/<county>/index.html  one page per county with key facts, for search engines (regenerated every run)

If any check fails, nothing is written and the script exits with an error (the workflow then fails and opens an issue).

  python3 scripts/rent_build.py               download from the CSO and build
  python3 scripts/rent_build.py --source F --earnings G   build from saved copies of RIH02 and DEA05 (JSON-stat)
  python3 scripts/rent_build.py --self-test   quick checks of the code itself, no download
"""
import argparse
import datetime
import html
import itertools
import json
import os
import re
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


def county_page(c, out, meta, rank):
    P, rent, inc = out["periods"], out["rent"], out["income"]["counties"][c]
    cid, e = slug(c), html.escape
    s = rent[cid]["all"]
    i = max(k for k, v in enumerate(s) if v is not None)
    now, ch1, ch10 = s[i], change(s, i, 1), change(s, i, 10)
    pct = round(now / inc["take_home"] * 100)
    facts = [f"The average monthly rent for a new tenancy in County {c} was <strong>€{now:,}</strong> in {when(P[i])}, for all homes."]
    if ch1 and ch10:
        facts.append(f"That is {ch1} on a year earlier, and {ch10} on ten years earlier.")
    facts.append(f"{c} is the {'most' if rank == 1 else ordinal(rank) + ' most'} expensive of Ireland's 26 counties for new rents."
                 f" On typical pay in Co. {c}, that rent takes about {pct}% of take-home pay.")
    beds = "".join(
        f"<tr><td>{label}</td><td>{'€{:,}'.format(v[-1]) if v and v[-1] is not None else '–'}</td></tr>"
        for key, label in [("all", "All homes"), ("1", "1 bed"), ("2", "2 beds"), ("3", "3 beds"), ("4", "4+ beds")]
        for v in [rent[cid].get(key)])
    areas = []
    for p in out["places"]:
        a = rent[p["id"]].get("all", [])
        k = max((k for k, v in enumerate(a) if v is not None), default=-1)
        if p["county"] == c and p["level"] != "county" and k >= len(P) - 5:  # same 2-year rule as the finder
            areas.append((a[k], p, P[k]))
    rows = "".join(f'<tr><td><a href="/rent/?area={p["id"]}">{e(p["name"])}</a></td><td>€{v:,}</td><td>{when(w)}</td></tr>'
                   for v, p, w in sorted(areas, key=lambda r: (-r[0], r[1]["name"])))
    title = f"Rent in {c}: average €{now:,} a month ({P[i][:4]})"
    desc = (f"The average new rent in County {c} is €{now:,} a month ({when(P[i])})"
            + (f", {ch10.split(' ')[0]} {ch10.split('(')[1][:-1]} in 10 years" if ch10 else "")  # "up 100%"
            + f". Rents for every town and area in {c}, by bedrooms, from official RTB data.")
    return f"""---
# Written by scripts/rent_build.py from data/rent/rents.json. Don't edit by hand: changes are overwritten on the next refresh.
layout: default
title: {json.dumps(title, ensure_ascii=False)}
description: {json.dumps(desc, ensure_ascii=False)}
rent_county: {json.dumps(c)}
image: {{ path: /images/rent/og.png, width: 1200, height: 630, alt: "Irish Rent Reality Check at malavnaik.com/rent" }}
---
<p class="eyebrow"><a href="/rent/">Irish Rent Reality Check</a> / {e(c)}</p>
<h1>Rent in {e(c)}</h1>
<p class="lead" style="max-width:46rem">{' '.join(facts)}</p>
<p><a class="btn btn-accent" href="/rent/?area={cid}">Explore {e(c)} in the rent tool</a></p>

<section class="card" style="margin:1.5rem 0" aria-labelledby="beds-title">
  <h2 id="beds-title">By number of bedrooms, {when(P[-1])}</h2>
  <table><thead><tr><th scope="col">Bedrooms</th><th scope="col">Average monthly rent</th></tr></thead><tbody>{beds}</tbody></table>
  <p class="small muted">– means the RTB published no average: too few new tenancies were registered.</p>
</section>

<section class="card" style="margin:1.5rem 0" aria-labelledby="areas-title">
  <h2 id="areas-title">Towns and areas in {e(c)}, all homes</h2>
  <div style="overflow-x:auto"><table><thead><tr><th scope="col">Area</th><th scope="col">Average monthly rent</th><th scope="col">Half-year</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="small muted">Most expensive first. Areas without a published figure since {when(P[-5])} are left out.</p>
</section>

<p class="small muted">Averages for <strong>new</strong> tenancies registered with the RTB, not what every tenant pays, and not adjusted for inflation.
Take-home pay: median weekly earnings in Co. {e(c)} ({out["income"]["year"]}, €{inc["weekly"]:,.2f} before tax, CSO table DEA05), estimated after tax for one PAYE earner at {out["income"]["tax_year"]} rates.
Sources: <a href="https://data.cso.ie/table/RIH02">CSO table RIH02</a> and <a href="https://data.cso.ie/table/DEA05">DEA05</a>, © CSO and RTB, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. Data last changed {meta["last_updated"]}.</p>
"""


def write_county_pages(out, meta):
    """Write rent/<county>/index.html for all 26 counties. Same data in, same pages out, so git only sees real changes."""
    P, rent = out["periods"], out["rent"]
    latest = {c: rent[slug(c)]["all"][-1] for c in COUNTIES}  # build() checked every county has one
    order = sorted(COUNTIES, key=lambda c: -latest[c])
    for c in COUNTIES:
        page = county_page(c, out, meta, order.index(c) + 1)
        assert f"€{latest[c]:,}" in page, c
        os.makedirs(os.path.join(ROOT, "rent", slug(c)), exist_ok=True)
        with open(os.path.join(ROOT, "rent", slug(c), "index.html"), "w", encoding="utf-8") as f:
            f.write(page)
    print(f"Wrote {len(COUNTIES)} county pages in rent/ (latest {P[-1]}).")


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
    print("Self-test passed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="saved JSON-stat copy of RIH02 instead of downloading")
    ap.add_argument("--earnings", help="saved JSON-stat copy of DEA05 instead of downloading")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    def load(path, code):
        if path:
            return json.load(open(path, encoding="utf-8"))
        with urllib.request.urlopen(API.format(code), timeout=300) as r:
            return json.load(r)
    table, earnings = load(a.source, "RIH02"), load(a.earnings, "DEA05")
    meta_path = os.path.join(OUT, "meta.json")
    previous = json.load(open(meta_path)) if os.path.exists(meta_path) else None
    try:
        out, meta = build(table, earnings, previous)
    except CheckFailed as e:
        sys.exit(f"CHECK FAILED, nothing was published: {e}")
    write(out, meta)
    write_county_pages(out, json.load(open(meta_path)))


if __name__ == "__main__":
    main()
