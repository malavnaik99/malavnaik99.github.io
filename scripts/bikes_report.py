"""Monthly "Dublin Bikes in numbers" report.

Reads the public Hugging Face datasets published by dublin-data-pipeline and writes, for one month:
  scripts/bikes_report_YYYY-MM.json      every number used in the post
  images/bikes-report/YYYY-MM.png        one chart (estimated pickups by hour of day)
  _drafts/dublin-bikes-in-numbers-YYYY-MM.md   a draft post built only from the JSON

Usage:
  python scripts/bikes_report.py                      # last calendar month
  python scripts/bikes_report.py --month 2026-10 --end 2026-10-27
  python scripts/bikes_report.py --self-test
Needs: pip install duckdb matplotlib huggingface_hub
"""
import argparse
import calendar
import datetime as dt
import json
import re
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
RAW = "Malavnaik/dublin-bikes-weather-raw"
MARTS = "Malavnaik/dublin-bikes-weather-marts"
SITE = "https://malavnaik.com"
CREDIT = "Data: malavnaik.com · Dublinbikes, Met Éireann"
WET_MM = 0.1   # Met Éireann reports a trace of rain as 0.01 mm; trace hours count as neither wet nor dry
MAX_GAP = "30 minutes"  # a drop across a longer gap (missed snapshots) is not counted

# One row per station per snapshot pair: bikes that left between two snapshots at most MAX_GAP apart.
PICKUPS_SQL = f"""
create or replace table pickups as
select station_id, t, greatest(prev - bikes, 0) as pickups
from (select station_id, t, bikes,
             lag(bikes) over w as prev, t - lag(t) over w as gap
      from snap window w as (partition by station_id order by t))
where prev is not null and gap <= interval {MAX_GAP}
"""


def month_arg(s):
    dt.datetime.strptime(s, "%Y-%m")  # validates the format; raises on anything else
    return s


def fetch(start, end):
    """Download the raw bike snapshots for the period and the marts' dimension tables; return their paths."""
    from huggingface_hub import hf_hub_download, snapshot_download
    # Partitions are UTC dates; take one extra day each side so Dublin local midnight is covered.
    days = [start + dt.timedelta(d) for d in range(-1, (end - start).days + 2)]
    raw = snapshot_download(RAW, repo_type="dataset", allow_patterns=[f"raw/bikes/date={d}/*" for d in days])
    dims = {t: hf_hub_download(MARTS, f"marts/{t}.parquet", repo_type="dataset") for t in ("dim_hour", "dim_station")}
    return f"{raw}/raw/bikes/*/*.parquet", dims


def label(start, end):
    if start.day == 1 and end.day == calendar.monthrange(end.year, end.month)[1]:
        return f"{end:%B %Y}"
    return f"{start.day}–{end.day} {end:%B %Y}"


def compute(con, month, start, end):
    q = lambda sql: con.sql(sql).fetchall()
    # Snapshots inside the period, by Dublin local date.
    con.sql(f"""create or replace table snap as
        select distinct station_id, cast(fetched_at as timestamptz) as t, num_vehicles_available as bikes
        from raw where station_id is not null
          and cast(timezone('Europe/Dublin', cast(fetched_at as timestamptz)) as date) between '{start}' and '{end}'""")
    con.sql(PICKUPS_SQL)
    first, last, n_snap, n_stations = q("select min(t), max(t), count(distinct t), count(distinct station_id) from snap")[0]
    if not n_snap:
        raise SystemExit(f"No snapshots between {start} and {end}.")
    start, end = q(f"select cast(timezone('Europe/Dublin', '{first}'::timestamptz) as date), cast(timezone('Europe/Dublin', '{last}'::timestamptz) as date)")[0]
    span_h = (last - first).total_seconds() / 3600
    total = q("select sum(pickups) from pickups")[0][0]

    # Stations that never had a bike in the period (the feed has a placeholder) or no capacity are left out.
    con.sql("""create or replace table st as
        select s.station_id, s.station_name, s.capacity, coalesce(p.pickups, 0) as pickups,
               round(100 * a.avg_bikes / s.capacity, 1) as pct_full
        from dim_station s
        join (select station_id, avg(bikes) as avg_bikes, max(bikes) as max_bikes from snap group by 1) a using (station_id)
        left join (select station_id, sum(pickups) as pickups from pickups group by 1) p using (station_id)
        where s.capacity > 0 and a.max_bikes > 0""")
    rows = lambda order: [{"station": re.sub(r"'S\b", "'s", n.title()), "estimated_pickups": int(p), "pct_docks_with_bike": f}
                          for n, p, f in q(f"select station_name, pickups, pct_full from st order by {order}, station_name limit 5")]

    con.sql("""create or replace table hours as
        select date_trunc('hour', t) as hour_utc, hour(timezone('Europe/Dublin', date_trunc('hour', t))) as local_hour,
               sum(pickups) as pickups
        from pickups group by all""")
    by_hour = [{"local_hour": h, "avg_estimated_pickups": round(v)} for h, v in
               q("select local_hour, avg(pickups) from hours group by 1 order by 1")]
    busiest = max(by_hour, key=lambda r: r["avg_estimated_pickups"])

    # Rain: compare each rainy hour with dry hours at the same hour of the day (weekday or weekend),
    # so night-time quiet and weekend patterns don't skew it.
    con.sql(f"""create or replace table wx as
        select h.*, d.is_weekend, case when d.rainfall_mm >= {WET_MM} then 'wet' when d.rainfall_mm = 0 then 'dry' end as weather
        from hours h join dim_hour d using (hour_utc)""")
    (wet_n, dry_n, wet_avg, dry_avg, matched), = q("""
        with dry as (select local_hour, is_weekend, avg(pickups) as dry_avg from wx where weather = 'dry' group by all)
        select count(*) filter (weather = 'wet'), count(*) filter (weather = 'dry'),
               avg(pickups) filter (weather = 'wet'), avg(pickups) filter (weather = 'dry'),
               sum(pickups) filter (weather = 'wet' and dry_avg is not null) / sum(dry_avg) filter (weather = 'wet')
        from wx left join dry using (local_hour, is_weekend)""")

    per_day = round(total / span_h * 24)
    prev = (dt.date(start.year, start.month, 1) - dt.timedelta(1)).strftime("%Y-%m")
    prev_path = ROOT / f"scripts/bikes_report_{prev}.json"
    mom = None
    if prev_path.exists():
        p = json.loads(prev_path.read_text())["estimated_pickups_per_day"]
        mom = {"previous_month": prev, "previous_estimated_pickups_per_day": p,
               "pct_change_estimated_pickups_per_day": round(100 * (per_day / p - 1), 1)}

    return {
        "month": month,
        "period": {"first_snapshot_utc": first.isoformat(), "last_snapshot_utc": last.isoformat(),
                   "first_day": str(start), "last_day": str(end), "label": label(start, end)},
        "coverage": {"snapshots": n_snap, "stations_in_feed": n_stations,
                     "stations_reported": q("select count(*) from st")[0][0]},
        "estimated_pickups_total": int(total),
        "estimated_pickups_per_day": per_day,
        "busiest_hour": {"local_hour": busiest["local_hour"], "label": f"{busiest['local_hour']:02d}:00–{(busiest['local_hour'] + 1) % 24:02d}:00",
                         "avg_estimated_pickups": busiest["avg_estimated_pickups"]},
        "by_local_hour": by_hour,
        "busiest_stations": rows("pickups desc"),
        "quietest_stations": rows("pickups asc"),
        "fullest_stations": rows("pct_full desc"),
        "emptiest_stations": rows("pct_full asc"),
        "rain": {"wet_hours": wet_n, "dry_hours": dry_n,
                 "wet_avg_estimated_pickups_per_hour": round(wet_avg) if wet_avg is not None else None,
                 "dry_avg_estimated_pickups_per_hour": round(dry_avg) if dry_avg is not None else None,
                 "pct_change_vs_dry_same_hour": round(100 * (matched - 1), 1) if matched else None},
        "month_on_month": mom,
        "method": {
            "estimated_pickups": f"Sum of drops in available bikes between consecutive snapshots of a station (about 15 minutes apart, gaps over {MAX_GAP} skipped). Includes bikes removed by rebalancing vans.",
            "stations_excluded": "Stations with no capacity or that never had a bike in the period.",
            "pct_docks_with_bike": "Average available bikes divided by station capacity.",
            "rain": f"Wet hour: at least {WET_MM} mm at Dublin Airport (Met Éireann). Dry hour: 0 mm. Trace hours (0.01 mm) and hours with no reading are left out. pct_change_vs_dry_same_hour compares rainy hours with the dry-hour average at the same hour of day, weekdays and weekends matched separately.",
            "sources": [f"https://huggingface.co/datasets/{RAW}", f"https://huggingface.co/datasets/{MARTS}"],
        },
    }


def chart(r, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    hours = [x["local_hour"] for x in r["by_local_hour"]]
    vals = [x["avg_estimated_pickups"] for x in r["by_local_hour"]]
    b = r["busiest_hour"]
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
    fig.patch.set_facecolor("white")
    ax.bar(hours, vals, width=0.8, color=["#2a78d6" if h == b["local_hour"] else "#9cc3ee" for h in hours])
    ax.annotate(f"{b['label']}: {b['avg_estimated_pickups']}", (b["local_hour"], b["avg_estimated_pickups"]),
                xytext=(0, 4), textcoords="offset points", ha="center", fontsize=10, color="#0b0b0b")
    ax.set_ylim(0, max(vals) * 1.12)
    ax.set_xticks(range(0, 24, 3), [f"{h:02d}:00" for h in range(0, 24, 3)], color="#52514e")
    ax.tick_params(axis="y", colors="#52514e")
    ax.tick_params(length=0)
    ax.grid(axis="y", color="#e5e4df", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_ylabel("Average estimated pickups per hour", color="#52514e")
    fig.suptitle(f"Dublin Bikes, {r['period']['label']}: when are bikes picked up?", x=0.06, ha="left", fontsize=14, fontweight="bold", color="#0b0b0b")
    ax.set_title("Average estimated pickups across all stations, by hour of day (Dublin time)", loc="left", fontsize=10, color="#52514e")
    fig.text(0.06, 0.02, CREDIT, fontsize=9, color="#52514e")
    fig.subplots_adjust(left=0.1, right=0.97, top=0.84, bottom=0.14)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    assert path.stat().st_size < 150_000, f"{path} is {path.stat().st_size} bytes, over 150 KB"


def post(r, png, slug):
    p, rain, b = r["period"], r["rain"], r["busiest_hour"]
    n = lambda x: f"{x:,}"
    url = f"{SITE}/blog/{slug}/"
    img = f"{SITE}/{png.relative_to(ROOT).as_posix()}"
    alt = (f"Bar chart of average estimated Dublinbikes pickups per hour by hour of day, {p['label']}. "
           f"The busiest hour is {b['label']} with {b['avg_estimated_pickups']} pickups on average.")
    stations = lambda key, field, unit: "\n".join(
        f"{i}. {s['station']}: {n(s[field])}{unit}" for i, s in enumerate(r[key], 1))
    if rain["pct_change_vs_dry_same_hour"] is None or rain["wet_hours"] < 5:
        rain_text = f"There were only {rain['wet_hours']} rainy hours, too few to compare with dry weather this time."
    else:
        pct = rain["pct_change_vs_dry_same_hour"]
        rain_text = (f"It rained (at least 0.1 mm at Dublin Airport) in {rain['wet_hours']} hours. In those hours there were "
                     f"**{abs(pct)}% {'fewer' if pct < 0 else 'more'} estimated pickups** than in dry hours at the same time of day. "
                     f"Without adjusting for the time of day, rainy hours averaged {rain['wet_avg_estimated_pickups_per_hour']} pickups "
                     f"and dry hours {rain['dry_avg_estimated_pickups_per_hour']}. Hours with only a trace of rain are left out. It's a small sample, so treat this as a first look.")
    mom = r["month_on_month"]
    mom_text = ("Month-on-month comparisons start with the November edition." if mom is None else
                f"Compared with {dt.datetime.strptime(mom['previous_month'], '%Y-%m'):%B}, estimated pickups per day "
                f"{'rose' if mom['pct_change_estimated_pickups_per_day'] >= 0 else 'fell'} by "
                f"{abs(mom['pct_change_estimated_pickups_per_day'])}%.")
    launch = (f"This is the first edition. My pipeline started collecting on {dt.date.fromisoformat(p['first_day']):%-d %B}, so it covers "
              if r["month"] == "2026-10" else "This edition covers ")
    body = f"""---
title: "Dublin Bikes in numbers: {p['label']}"
slug: {slug}
description: "When and where Dubliners picked up Dublinbikes during {p['label']}, and what rain did to it, from my open bikes and weather data."
tags: [dublin, dublinbikes, opendata, dataengineering]
image: "/{png.relative_to(ROOT).as_posix()}"
image_alt: "{alt}"
---

A monthly look at Dublinbikes, built from my [bikes and weather pipeline](/projects/dublin-bikes-pipeline/). {launch}**{p['label']}**.

**How I count pickups:** every 15 minutes I record how many bikes each station has, and whenever a station has fewer bikes than 15 minutes earlier, I count the difference as pickups, so the numbers are estimates (bikes moved by the rebalancing vans count too).

## The headline

About **{n(r['estimated_pickups_total'])} estimated pickups** across {r['coverage']['stations_reported']} stations, or roughly {n(r['estimated_pickups_per_day'])} a day.

## The busiest hour

![{alt}](/{png.relative_to(ROOT).as_posix()}){{: width="800" height="450"}}

The busiest hour was **{b['label']}**, with {b['avg_estimated_pickups']} estimated pickups on average across all stations.

## Busiest and quietest stations

Most estimated pickups:

{stations('busiest_stations', 'estimated_pickups', '')}

Fewest:

{stations('quietest_stations', 'estimated_pickups', '')}

## Where to find a bike

Average share of docks holding a bike. Emptiest stations:

{stations('emptiest_stations', 'pct_docks_with_bike', '%')}

Fullest stations:

{stations('fullest_stations', 'pct_docks_with_bike', '%')}

## What rain did

{rain_text}

{mom_text}

## Use this data

You're welcome to reuse the chart in articles, slides or posts, as long as you link back to this post. The data behind it is open on Hugging Face: [raw snapshots](https://huggingface.co/datasets/{RAW}) and [modelled tables](https://huggingface.co/datasets/{MARTS}), CC BY 4.0. Bikes: Dublinbikes GBFS feed, Dublin City Council / JCDecaux. Weather: Source: Met Éireann.

### Embed this chart

```html
<a href="{url}"><img src="{img}" alt="{alt}" width="800" height="450"></a>
```
"""
    words = len(body.split("\n---\n", 1)[1].split())
    assert words < 500, f"Draft is {words} words, keep it under 500"
    return body


def self_test():
    con = duckdb.connect()
    con.sql("""create table snap as select * from (values
        ('a', '2026-10-01 10:00'::timestamptz, 5), ('a', '2026-10-01 10:15', 3),  -- 2 picked up
        ('a', '2026-10-01 10:30', 4),                                              -- a return: 0
        ('a', '2026-10-01 11:30', 0),                                              -- 60 min gap: skipped
        ('b', '2026-10-01 10:00', 1), ('b', '2026-10-01 10:14', 0)                 -- 1 picked up
        ) t(station_id, t, bikes)""")
    con.sql(PICKUPS_SQL)
    assert con.sql("select sum(pickups) from pickups").fetchall()[0][0] == 3
    assert label(dt.date(2026, 10, 16), dt.date(2026, 10, 31)) == "16–31 October 2026"
    assert label(dt.date(2026, 11, 1), dt.date(2026, 11, 30)) == "November 2026"
    print("self-test ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--month", type=month_arg, help="YYYY-MM (default: last calendar month)")
    ap.add_argument("--end", type=dt.date.fromisoformat, help="stop early at this date, for testing (YYYY-MM-DD)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    month = a.month or (dt.date.today().replace(day=1) - dt.timedelta(1)).strftime("%Y-%m")
    start = dt.datetime.strptime(month, "%Y-%m").date()
    end = start.replace(day=calendar.monthrange(start.year, start.month)[1])
    if a.end:
        end = min(end, a.end)

    raw, dims = fetch(start, end)
    con = duckdb.connect()
    con.sql(f"create view raw as select * from read_parquet('{raw}', hive_partitioning = false, union_by_name = true)")
    for t, f in dims.items():
        con.sql(f"create view {t} as select * from read_parquet('{f}')")
    r = compute(con, month, start, end)

    out = ROOT / f"scripts/bikes_report_{month}.json"
    png = ROOT / f"images/bikes-report/{month}.png"
    draft = ROOT / f"_drafts/dublin-bikes-in-numbers-{month}.md"
    slug = f"dublin-bikes-in-numbers-{dt.datetime.strptime(month, '%Y-%m'):%B-%Y}".lower()
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    chart(r, png)
    draft.parent.mkdir(exist_ok=True)
    draft.write_text(post(r, png, slug))
    print(json.dumps(r, indent=2, ensure_ascii=False))
    print(f"\nWrote {out.relative_to(ROOT)}, {png.relative_to(ROOT)} ({png.stat().st_size // 1024} KB), {draft.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
