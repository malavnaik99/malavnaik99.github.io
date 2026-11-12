"""Draws the small project charts used in the project rows (home page and /work/) as static SVG.

Every number comes from a data file in this repo:
    bikes       assets/data/dublin-bikes/*.parquet   average bikes per station by local hour, weekdays vs weekends
    moderation  assets/data/moderation-sweep.json    precision against recall across thresholds, 0.22 and 0.82 marked
    dsa         assets/data/dsa-examples.json        right article in the top 3: keyword vs vector, out of 25
    skillbot    docs/METRIC_SOURCES.md (48%)         suggested skills found in the real ad, out of 10

Writes _includes/charts/<name>.html (a <figure> with the SVG, its title/description for screen readers, and a caption).
Colours come from the site's CSS (classes ch-a / ch-m), so the charts follow the light and dark themes.

Run it again only when one of those data files changes (the bikes chart needs DuckDB: pip install duckdb):
    python3 scripts/make_charts.py            # write the charts
    python3 scripts/make_charts.py --check    # fail if the committed charts differ from the data (self-test)
"""
import html, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_includes" / "charts"
W, H = 300, 120          # SVG coordinate space; it scales to the row width
L, R, T, B = 30, 62, 10, 22   # plot margins: left axis labels, right direct labels, top, bottom axis labels


def fmt(x, nd=1):
    return f"{x:.{nd}f}".rstrip("0").rstrip(".") if nd else str(round(x))


def figure(name, title, desc, caption, body, h=H):
    """Wrap SVG body in an accessible figure. The SVG is described by <title>/<desc>; the caption repeats it for everyone."""
    t, d = f"ch-{name}-t", f"ch-{name}-d"
    return (f'<figure class="row-chart">\n<svg viewBox="0 0 {W} {h}" role="img" aria-labelledby="{t} {d}">'
            f'<title id="{t}">{html.escape(title)}</title><desc id="{d}">{html.escape(desc)}</desc>\n{body}</svg>\n'
            f'<figcaption>{html.escape(caption)}</figcaption>\n</figure>\n')


def line(points, cls, extra=""):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline class="{cls}" points="{pts}" fill="none"{extra}/>\n'


def text(x, y, s, cls="ch-t", anchor="start"):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{html.escape(s)}</text>\n'


def bikes():
    import duckdb  # only this chart needs it
    c = duckdb.connect()
    for t in ("fct_station_hour", "dim_station", "dim_hour"):
        c.execute(f"create view {t} as select * from '{ROOT}/assets/data/dublin-bikes/{t}.parquet'")
    rows = c.sql("""select h.is_weekend, h.local_hour, avg(f.avg_bikes)
        from fct_station_hour f join dim_hour h using (hour_utc) join dim_station s using (station_id)
        where s.capacity > 0 and s.station_name <> 'STATION118'
        group by all order by 1, 2""").fetchall()
    days = c.sql("select count(distinct local_date) filter (where is_weekend), count(distinct local_date) filter (where not is_weekend) from dim_hour").fetchall()[0]
    span = c.sql("select min(local_date), max(local_date) from dim_hour").fetchall()[0]
    series = {we: [v for w, h, v in rows if w == we] for we in (False, True)}
    assert all(len(s) == 24 for s in series.values()), "expected 24 hours per series"
    # A line chart's axis may start near the data (it is labelled); from 0 the hourly dip would be invisible.
    lo, hi = int(min(min(s) for s in series.values())) - 1, int(max(max(s) for s in series.values())) + 1
    x = lambda h: L + h / 23 * (W - L - R)
    y = lambda v: H - B - (v - lo) / (hi - lo) * (H - T - B)
    body = f'<line class="ch-axis" x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}"/>\n'
    for h in (0, 6, 12, 18, 23):
        body += text(x(h), H - 6, f"{h:02d}:00" if h in (0, 12) else f"{h:02d}", anchor="middle")
    body += text(L - 4, y(hi) + 4, fmt(hi, 0), anchor="end") + text(L - 4, y(lo) + 4, fmt(lo, 0), anchor="end")
    body += line([(x(h), y(v)) for h, v in enumerate(series[True])], "ch-m", ' stroke-dasharray="4 3"')
    body += line([(x(h), y(v)) for h, v in enumerate(series[False])], "ch-a")
    # Direct labels at the right end, nudged apart if the lines end close together.
    ya, ym = y(series[False][-1]), y(series[True][-1])
    if abs(ya - ym) < 12:
        ya, ym = (ya - 6, ym + 6) if ya <= ym else (ya + 6, ym - 6)
    body += text(W - R + 5, ya + 4, "weekday") + text(W - R + 5, ym + 4, "weekend", "ch-t ch-tm")
    wd, we = series[False], series[True]
    low_h = min(range(24), key=lambda h: wd[h] if 6 <= h <= 20 else 99)
    desc = (f"Average bikes available per Dublinbikes station, by hour, {span[0]:%-d} to {span[1]:%-d %b %Y} "
            f"({days[1]} weekdays, {days[0]} weekend days). Weekdays: about {fmt(wd[3])} bikes at 03:00, falling to "
            f"{fmt(wd[low_h])} at {low_h:02d}:00. Weekends: {fmt(min(we))} to {fmt(max(we))} through the day.")
    return figure("bikes", "Bikes per station by hour: weekdays against weekends", desc,
                  "Average bikes per station by hour of day, weekdays against weekends.", body)


def moderation():
    d = json.loads((ROOT / "assets/data/moderation-sweep.json").read_text())
    s = d["sweep"]
    x = lambda r: L + r * (W - L - R)          # recall 0..1
    y = lambda p: H - B - p * (H - T - B)      # precision 0..1
    body = f'<line class="ch-axis" x1="{L}" y1="{H-B}" x2="{W-R}" y2="{H-B}"/><line class="ch-axis" x1="{L}" y1="{T}" x2="{L}" y2="{H-B}"/>\n'
    body += text(L, H - 6, "0", anchor="middle") + text(W - R, H - 6, "100%", anchor="middle") + text((L + W - R) / 2, H - 6, "recall", anchor="middle")
    body += text(L - 4, y(1) + 4, "100%", anchor="end") + text(L - 4, y(0) + 4, "0", anchor="end")
    body += line([(x(r["recall"]), y(r["precision"])) for r in s], "ch-a")
    marks = {}
    for t, label in ((0.22, "0.22 review"), (0.82, "0.82 auto")):
        r = next(r for r in s if abs(r["t"] - t) < 1e-9)
        marks[t] = r
        body += f'<circle class="ch-dot" cx="{x(r["recall"]):.1f}" cy="{y(r["precision"]):.1f}" r="4"/>\n'
        # 0.22 sits low on the right of the curve: label it to the left, below the line; 0.82 is high: label above.
        body += text(x(r["recall"]) - 7, y(r["precision"]) + 16, label, anchor="end") if t == 0.22 else text(x(r["recall"]) + 7, y(r["precision"]) - 7, label)
    a, b = marks[0.22], marks[0.82]
    desc = (f"Precision against recall for every threshold from {s[0]['t']} to {s[-1]['t']}, on 180,488 held-out test comments. "
            f"At the 0.22 review threshold: precision {a['precision']*100:.1f}%, recall {a['recall']*100:.1f}%. "
            f"At the 0.82 auto-action threshold: precision {b['precision']*100:.1f}%, recall {b['recall']*100:.1f}%.")
    return figure("moderation", "Precision against recall across thresholds", desc,
                  "Precision against recall at every threshold; the two saved policies are marked.", body)


def dsa():
    d = json.loads((ROOT / "assets/data/dsa-examples.json").read_text())
    n = len(d["examples"])
    hits = {m: sum(any(a["article"] in ex["expected"] for a in ex[m]) for ex in d["examples"]) for m in ("keyword", "vector")}
    assert hits == {"keyword": 17, "vector": 21} and n == 25, (hits, n)  # the published figures (METRIC_SOURCES.md)
    x0, x1 = 64, W - 62
    body = ""
    for i, (m, cls, label) in enumerate((("keyword", "ch-mf", "keyword"), ("vector", "ch-af", "vector"))):
        yy = 24 + i * 44
        body += f'<rect class="ch-track" x="{x0}" y="{yy}" width="{x1-x0}" height="18" rx="4"/>\n'
        body += f'<rect class="{cls}" x="{x0}" y="{yy}" width="{(x1-x0)*hits[m]/n:.1f}" height="18" rx="4"/>\n'
        body += text(x0 - 6, yy + 13, label, anchor="end") + text(x1 + 6, yy + 13, f"{hits[m]} / {n}")
    desc = (f"Right article in the top 3 results, out of {n} test questions: keyword search (BM25) {hits['keyword']}, "
            f"vector search {hits['vector']} ({hits['vector']/n*100:.0f}%).")
    return figure("dsa", "Keyword against vector search", desc,
                  f"Test questions with the right article in the top 3: keyword {hits['keyword']} of {n}, vector {hits['vector']} of {n}.", body, h=92)


def skillbot():
    share = 0.48  # docs/METRIC_SOURCES.md: 48% of the 10 suggested skills were in the real ad (leave-one-out, 1,167 ads)
    filled = share * 10
    size, gap, x0, y0 = 22, 4, 12, 8
    body = '<defs><clipPath id="ch-sb-clip"><rect x="0" y="0" width="{:.1f}" height="{}"/></clipPath></defs>\n'.format(x0 + int(filled) * (size + gap) + (filled % 1) * size, H)
    for i in range(10):
        xx = x0 + i * (size + gap)
        body += f'<rect class="ch-box" x="{xx}" y="{y0}" width="{size}" height="{size}" rx="4"/>\n'
    body += '<g clip-path="url(#ch-sb-clip)">' + "".join(
        f'<rect class="ch-af" x="{x0 + i * (size + gap)}" y="{y0}" width="{size}" height="{size}" rx="4"/>' for i in range(10)) + "</g>\n"
    body += text(x0, y0 + size + 22, f"{fmt(filled)} of 10 in the real ad")
    desc = (f"Of 10 skills suggested from a job title alone, {fmt(filled)} on average ({share*100:.0f}%) were in the real job ad, "
            "in a leave-one-out test over 1,167 ads.")
    return figure("skillbot", "Suggested skills found in the real ad", desc,
                  "Suggested skills found in the real job ad, out of 10.", body, h=72)


CHARTS = {"bikes": bikes, "moderation": moderation, "dsa": dsa, "skillbot": skillbot}

if __name__ == "__main__":
    check = "--check" in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, make in CHARTS.items():
        out = OUT / f"{name}.html"
        new = "{%- comment -%} Made by scripts/make_charts.py from the repo's data; do not edit by hand. {%- endcomment -%}\n" + make()
        if check:
            if not out.exists() or out.read_text() != new:
                stale.append(name)
        else:
            out.write_text(new)
            print("wrote", out.relative_to(ROOT))
    if stale:
        sys.exit("Charts out of date with their data: " + ", ".join(stale) + ". Run: python3 scripts/make_charts.py")
    if check:
        print("Charts match their data.")
