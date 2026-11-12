"""Builds the data for the home page "sky": every Dublinbikes station as a light at its real position.

    python3 scripts/make_sky.py              # snapshot: _data/sky.json from assets/data/dublin-bikes/*.parquet (needs: pip install duckdb)
    python3 scripts/make_sky.py --river      # river: _data/sky_river.json, the River Liffey from OpenStreetMap (needs overpass-api.de)
    python3 scripts/make_sky.py --self-test  # offline checks of the river test and the snapshot format

_data/sky.json is also the saved fallback the page shows when there is no fresh live data, so the sky is never empty.
Its format is the one the pipeline's "latest" file must use (see docs/pipeline-latest-json.md):
    {"source", "generated_utc", "hours": ["YYYY-MM-DDTHH:00" local, oldest first],
     "stations": [[name, lat, lon, capacity], ...], "bikes": [[bikes per hour, null if missing], ...]  (same order as stations)}
STATION118 (a placeholder with no data) and stations with capacity 0 are left out.
"""
import json, math, pathlib, re, sys, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKY, RIVER = ROOT / "_data/sky.json", ROOT / "_data/sky_river.json"
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


def river():
    """The River Liffey through the station area, from OpenStreetMap (Overpass API); one polyline per OSM way."""
    q = f'[out:json][timeout:60];way["waterway"="river"]["name"="River Liffey"]({",".join(map(str, BBOX))});out geom;'
    req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(),
                                 headers={"User-Agent": "malavnaik.com site build (make_sky.py)"})
    d = json.load(urllib.request.urlopen(req, timeout=90))
    return parse_overpass(d)


def parse_overpass(d):
    return [[[round(g["lat"], 5), round(g["lon"], 5)] for g in el["geometry"]] for el in d.get("elements", []) if el.get("geometry")]


def self_test():
    assert nice("PRINCES STREET / O'CONNELL STREET") == "Princes Street / O'Connell Street"
    assert nice("ST. STEPHEN'S GREEN EAST") == "St. Stephen's Green East"
    assert nice("NORTH CIRCULAR ROAD (O'CONNELL'S)") == "North Circular Road (O'Connell's)"
    stations = [["Ormond Quay Upper", 53.3461, -6.2679, 30], ["Merrion Square South", 53.3386, -6.2479, 40]]
    near = parse_overpass({"elements": [{"geometry": [{"lat": 53.3459, "lon": -6.2700}, {"lat": 53.3458, "lon": -6.2650}]}]})
    far = parse_overpass({"elements": [{"geometry": [{"lat": 53.3300, "lon": -6.3000}]}]})
    assert check_river(near, stations) == [], "a river beside the quay must pass"
    assert check_river(far, stations), "a river 3 km away must fail"
    if SKY.exists():
        check_snapshot(json.loads(SKY.read_text()))
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
    else:
        d = snapshot()
        check_snapshot(d)
        SKY.write_text(json.dumps(d, separators=(",", ":")))
        print(f"wrote {SKY.relative_to(ROOT)}: {len(d['stations'])} stations x {len(d['hours'])} hours, {SKY.stat().st_size} bytes")
