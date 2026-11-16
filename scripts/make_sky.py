"""Builds the data for the home page "sky": every Dublinbikes station as a light at its real position.

    python3 scripts/make_sky.py              # snapshot: _data/sky.json from assets/data/dublin-bikes/*.parquet (needs: pip install duckdb)
    python3 scripts/make_sky.py --river      # river: _data/sky_river.json, the River Liffey from OpenStreetMap (needs overpass-api.de)
    python3 scripts/make_sky.py --outlines   # outlines: _data/sky_outlines.json, coast, canals, Phoenix Park from OpenStreetMap (needs overpass-api.de)
    python3 scripts/make_sky.py --self-test  # offline checks of the river test and the snapshot format

_data/sky.json is also the saved fallback the page shows when there is no fresh live data, so the sky is never empty.
Its format is the one the pipeline's "latest" file must use (see docs/pipeline-latest-json.md):
    {"source", "generated_utc", "hours": ["YYYY-MM-DDTHH:00" local, oldest first],
     "stations": [[name, lat, lon, capacity], ...], "bikes": [[bikes per hour, null if missing], ...]  (same order as stations)}
STATION118 (a placeholder with no data) and stations with capacity 0 are left out.
"""
import json, math, pathlib, re, sys, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKY, RIVER, OUTLINES = ROOT / "_data/sky.json", ROOT / "_data/sky_river.json", ROOT / "_data/sky_outlines.json"
HOURS = 48
BBOX = (53.325, -6.33, 53.365, -6.21)  # south, west, north, east: the area the stations cover


def snapshot():
    import duckdb
    c = duckdb.connect()
    for t in ("fct_station_hour", "dim_station", "dim_hour"):
        c.execute(f"create view {t} as select * from '{ROOT}/assets/data/dublin-bikes/{t}.parquet'")
    hours = c.sql(f"""select hour_utc::varchar, strftime(local_date, '%Y-%m-%d') || 'T' || lpad(local_hour::varchar, 2, '0') || ':00'
                      from dim_hour where hour_utc in (select distinct hour_utc from fct_station_hour)
                      order by hour_utc desc limit {HOURS}""").fetchall()[::-1]
    stations = c.sql("""select station_id, station_name, lat, lon, capacity from dim_station
                        where capacity > 0 and station_name <> 'STATION118' order by station_id""").fetchall()
    cells = {(s, h): b for s, h, b in c.sql("select station_id, hour_utc::varchar, avg_bikes from fct_station_hour").fetchall()}  # text keys: no pytz needed
    gen = c.sql("select strftime(max(hour_utc), '%Y-%m-%dT%H:%M:%SZ') from fct_station_hour").fetchall()[0][0]
    return {
        "source": "Saved snapshot from the Dublin bikes pipeline (assets/data/dublin-bikes), hourly averages",
        "generated_utc": gen,
        "hours": [label for _, label in hours],
        "stations": [[nice(n), round(la, 5), round(lo, 5), cap] for _, n, la, lo, cap in stations],
        "bikes": [[None if cells.get((sid, h)) is None else round(cells[(sid, h)]) for h, _ in hours] for sid, *_ in stations],
    }


def nice(name):
    """STATION NAMES come in capitals: 'PRINCES STREET / O'CONNELL STREET' -> "Princes Street / O'Connell Street"."""
    s = re.sub(r"[A-Za-z]+(?:'[A-Za-z]+)*", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), name)
    return re.sub(r"\bO'([a-z])", lambda m: "O'" + m.group(1).upper(), s)


def check_snapshot(d):
    assert len(d["hours"]) == len(d["bikes"][0]) and len(d["stations"]) == len(d["bikes"]), "hours/stations/bikes don't line up"
    assert all(s[3] > 0 and s[0].lower() != "station118" for s in d["stations"]), "placeholder or 0-dock station included"
    assert all(BBOX[0] < s[1] < BBOX[2] and BBOX[1] < s[2] < BBOX[3] for s in d["stations"]), "a station is outside Dublin"


def metres(a, b):
    """Distance in metres between two (lat, lon) points (equirectangular; fine at city scale)."""
    x = math.radians(b[1] - a[1]) * math.cos(math.radians((a[0] + b[0]) / 2))
    return 6371000 * math.hypot(x, math.radians(b[0] - a[0]))


def check_river(lines, stations, limit=200):
    """A real Liffey passes right beside the stations named "... Quay". Some quays are on Grand Canal Dock instead
    (Hanover Quay), so at least two thirds of them must be within `limit` metres. Returns problems (empty = passed)."""
    pts = [p for line in lines for p in line]
    quays = [s for s in stations if "quay" in s[0].lower()]
    assert quays and pts, "no quay stations or no river points"
    far = [f"{s[0]} is {min(metres((s[1], s[2]), p) for p in pts):.0f} m from the river" for s in quays
           if min(metres((s[1], s[2]), p) for p in pts) > limit]
    return far if len(far) > len(quays) / 3 else []


def river_query():
    """Overpass query for the Liffey's river lines in the station area. In OpenStreetMap a big river's name is often only on
    its 'waterway' relation, not on each section, so this takes the named sections AND the sections of the named relation."""
    box = ",".join(map(str, BBOX))
    return (f'[out:json][timeout:120];rel["waterway"="river"]["name"~"Liffey"]({box})->.r;'
            f'(way["waterway"="river"]["name"~"Liffey"]({box});way(r.r)["waterway"="river"]({box}););out geom;')


def river(tries=4, query=None):
    """The River Liffey through the station area, from OpenStreetMap (Overpass API); one polyline per OSM way.
    Retries when the free public service is busy (HTTP 429/502/503/504, or a 'remark' saying it ran out of time)."""
    import time
    query = query or river_query()
    req = lambda: urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": query}).encode(),
                                         headers={"User-Agent": "malavnaik.com site build (make_sky.py)"})
    for n in range(1, tries + 1):
        try:
            d = json.load(urllib.request.urlopen(req(), timeout=150))
            if d.get("remark"):  # Overpass sends an empty answer plus a remark when it times out or runs short of memory
                raise RuntimeError("OpenStreetMap's service said: " + d["remark"])
            lines = parse_overpass(d)
            print(f"try {n}: {len(d.get('elements', []))} OpenStreetMap elements, {len(lines)} lines")
            return lines
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, TimeoutError) as e:
            busy = not isinstance(e, urllib.error.HTTPError) or e.code in (429, 502, 503, 504)
            print(f"try {n}: {e}")
            if not busy or n == tries:
                raise
            time.sleep(30 * n)  # back off: the service is shared and free


# The hero map's landmarks: wider than the stations so Dublin Bay and Phoenix Park show. (south, west, north, east)
OUTLINE_BOX = (53.31, -6.38, 53.38, -6.15)
OUTLINE_SELECT = {  # OpenStreetMap tags; "rel" also takes the member ways of a relation with those tags (often the only named record)
    "coast": ('["natural"="coastline"]', ""),
    "liffey": ('["waterway"="river"]["name"~"Liffey"]', '["waterway"="river"]'),
    "grand_canal": ('["waterway"="canal"]["name"="Grand Canal"]', '["waterway"="canal"]'),
    "royal_canal": ('["waterway"="canal"]["name"="Royal Canal"]', '["waterway"="canal"]'),
    "phoenix_park": ('["leisure"="park"]["name"="Phoenix Park"]', ""),
}


def outline_query(sel, member):
    box = ",".join(map(str, OUTLINE_BOX))
    return f'[out:json][timeout:120];rel{sel}({box})->.r;(way{sel}({box});way(r.r){member}({box}););out geom({box});'


def simplify(line, tol=20):
    """Ramer-Douglas-Peucker in metres: keeps the shape, drops points that move it less than `tol` metres."""
    if len(line) < 3:
        return line
    a, b = line[0], line[-1]
    ax, bx = (a[1], a[0]), (b[1], b[0])
    k = math.cos(math.radians(a[0]))
    def off(p):  # distance in metres from p to the chord a-b
        x, y = (p[1] - a[1]) * k, p[0] - a[0]
        dx, dy = (b[1] - a[1]) * k, b[0] - a[0]
        t = max(0, min(1, (x * dx + y * dy) / ((dx * dx + dy * dy) or 1)))
        return math.radians(math.hypot(x - t * dx, y - t * dy)) * 6371000
    i, d = max(((i, off(p)) for i, p in enumerate(line[1:-1], 1)), key=lambda t: t[1])
    return simplify(line[:i + 1], tol)[:-1] + simplify(line[i:], tol) if d > tol else [a, b]


def outlines():
    import time
    out = {}
    for name, (sel, member) in OUTLINE_SELECT.items():
        lines = [[[round(p[0], 4), round(p[1], 4)] for p in simplify(l)] for l in river(query=outline_query(sel, member))]
        out[name] = [l for l in lines if len(l) > 1]
        time.sleep(5)  # the service is shared and free
    return out


# Where each map label sits; the label's words are in index.md so Google Translate can translate them.
LABELS = {"liffey": [53.3478, -6.2865], "phoenix_park": [53.3575, -6.3200], "docklands": [53.3497, -6.2400],
          "dublin_bay": [53.3360, -6.1850], "grand_canal": [53.3305, -6.2580]}


def check_outlines(o, stations):
    """Problems with downloaded outlines (empty = passed): each must exist and sit where it should beside the stations."""
    named = {s[0]: s for s in stations}
    near = lambda pts, st, m: min(metres((st[1], st[2]), p) for p in pts) <= m
    pts = {k: [p for l in v for p in l] for k, v in o.items()}
    bad = [f"{k}: nothing downloaded" for k in OUTLINE_SELECT if not pts.get(k)]
    if bad:
        return bad
    for st in ("Portobello Road", "Herbert Place", "Wilton Terrace"):
        if st in named and not near(pts["grand_canal"], named[st], 150):
            bad.append(f"grand_canal: not beside the {st} station")
    if "Parkgate Street" in named and not near(pts["phoenix_park"], named["Parkgate Street"], 500):
        bad.append("phoenix_park: not near the Parkgate Street station")
    if check_river(o["liffey"], stations):
        bad.append("liffey: " + "; ".join(check_river(o["liffey"], stations)))
    if not any(p[1] > -6.23 for p in pts["coast"]):
        bad.append("coast: nothing east of the city centre")
    if min(p[0] for p in pts["royal_canal"]) < 53.345:
        bad.append("royal_canal: runs south of the Liffey")
    return bad


def parse_overpass(d):
    """One polyline per OSM way. With "out geom(box)" points outside the box come back as null: the line is split there."""
    lines = []
    for el in d.get("elements", []):
        if el.get("type", "way") != "way" or not el.get("geometry"):
            continue
        part = []
        for g in el["geometry"] + [None]:
            if g:
                part.append([round(g["lat"], 5), round(g["lon"], 5)])
            elif part:
                lines.append(part) if len(part) > 1 else None
                part = []
    return lines


def self_test():
    assert nice("PRINCES STREET / O'CONNELL STREET") == "Princes Street / O'Connell Street"
    assert nice("ST. STEPHEN'S GREEN EAST") == "St. Stephen's Green East"
    assert nice("NORTH CIRCULAR ROAD (O'CONNELL'S)") == "North Circular Road (O'Connell's)"
    stations = [["Ormond Quay Upper", 53.3461, -6.2679, 30], ["Merrion Square South", 53.3386, -6.2479, 40]]
    near = parse_overpass({"elements": [{"geometry": [{"lat": 53.3459, "lon": -6.2700}, {"lat": 53.3458, "lon": -6.2650}]}]})
    far = parse_overpass({"elements": [{"geometry": [{"lat": 53.3300, "lon": -6.3000}, {"lat": 53.3301, "lon": -6.3001}]}]})
    assert check_river(near, stations) == [], "a river beside the quay must pass"
    assert check_river(far, stations), "a river 3 km away must fail"
    # Ways that come back for the named relation (no name tag of their own) count; the relation itself has no geometry here.
    rel_answer = {"elements": [{"type": "relation", "id": 1}, {"type": "way", "geometry": [{"lat": 53.3459, "lon": -6.2700}, {"lat": 53.3458, "lon": -6.2650}]}]}
    assert parse_overpass(rel_answer) == [[[53.3459, -6.27], [53.3458, -6.265]]]
    gap = {"elements": [{"type": "way", "geometry": [{"lat": 1, "lon": 1}, {"lat": 2, "lon": 2}, None, {"lat": 3, "lon": 3}, {"lat": 4, "lon": 4}]}]}
    assert parse_overpass(gap) == [[[1, 1], [2, 2]], [[3, 3], [4, 4]]], "a way leaving the box is split, not broken"
    q = river_query()
    assert 'rel["waterway"="river"]["name"~"Liffey"]' in q and "way(r.r)" in q and q.count(",".join(map(str, BBOX))) == 3
    assert simplify([[53.0, -6.0], [53.0, -6.0001], [53.0, -6.0002]]) == [[53.0, -6.0], [53.0, -6.0002]], "a straight line keeps its ends only"
    assert len(simplify([[53.0, -6.0], [53.01, -6.0], [53.0, -6.0001]])) == 3, "a 1 km detour stays"
    if SKY.exists():
        check_snapshot(json.loads(SKY.read_text()))
    if OUTLINES.exists() and SKY.exists():
        o = json.loads(OUTLINES.read_text())
        assert not check_outlines(o["lines"], json.loads(SKY.read_text())["stations"]), check_outlines(o["lines"], json.loads(SKY.read_text())["stations"])
        assert o["labels"] == LABELS, "labels in the file are out of date: run --labels"
    print("Self-test passed.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif "--river" in sys.argv:
        lines = river()
        bad = check_river(lines, json.loads(SKY.read_text())["stations"])
        if bad:
            sys.exit("The downloaded river doesn't pass beside the quay stations, so it was not saved:\n  " + "\n  ".join(bad))
        RIVER.write_text(json.dumps({"source": "© OpenStreetMap contributors (ODbL), River Liffey ways", "lines": lines}, separators=(",", ":")))
        print(f"wrote {RIVER.relative_to(ROOT)}: {len(lines)} lines, {sum(map(len, lines))} points")
    elif "--outlines" in sys.argv:
        o = outlines()
        bad = check_outlines(o, json.loads(SKY.read_text())["stations"])
        for k, v in o.items():
            print(f"{k}: {len(v)} lines, {sum(map(len, v))} points")
        if bad:
            sys.exit("The downloaded outlines failed their checks, so they were not saved:\n  " + "\n  ".join(bad))
        OUTLINES.write_text(json.dumps({"source": "© OpenStreetMap contributors (ODbL): coastline, River Liffey, Grand Canal, Royal Canal, Phoenix Park; simplified to 20 m",
                                        "lines": o, "labels": LABELS}, separators=(",", ":")))
        print(f"wrote {OUTLINES.relative_to(ROOT)}: {OUTLINES.stat().st_size} bytes")
    elif "--labels" in sys.argv:  # label positions only, no download
        o = json.loads(OUTLINES.read_text()); o["labels"] = LABELS
        OUTLINES.write_text(json.dumps(o, separators=(",", ":")))
    else:
        d = snapshot()
        check_snapshot(d)
        SKY.write_text(json.dumps(d, separators=(",", ":")))
        print(f"wrote {SKY.relative_to(ROOT)}: {len(d['stations'])} stations x {len(d['hours'])} hours, {SKY.stat().st_size} bytes")
