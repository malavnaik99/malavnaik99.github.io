# Temporary: checks the live site once after the redesign merge. Deleted right after.
import json, re, urllib.request, urllib.error
B = "https://malavnaik.com"
def get(path):
    try:
        with urllib.request.urlopen(urllib.request.Request(B + path, headers={"User-Agent": "site-check"}), timeout=20) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
_, sm = get("/sitemap.xml")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
bad = []
for loc in locs:
    path = loc.replace(B, "")
    code, html = get(path)
    if not loc.endswith((".html", "/")):  # files such as the résumé PDF
        print(code, path); bad += [path] if code != 200 else []; continue
    canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    types = []
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(block); types += [x["@type"] for x in d.get("@graph", [d])]
        except Exception as e:
            types.append(f"INVALID JSON-LD: {e}")
    ok = code == 200 and canon and canon.group(1) == loc and not any("INVALID" in t for t in types)
    print(("OK  " if ok else "BAD ") + f"{code} {path}  canonical={'same' if canon and canon.group(1) == loc else (canon.group(1) if canon else 'missing')}  schema={','.join(types)}")
    if not ok: bad.append(path)
print(f"--- {len(locs)} sitemap URLs, {len(bad)} problems: {bad}")
for path, want in [("/projects/", "/work/"), ("/blog/", "/writing/")]:
    code, html = get(path)
    print(f"redirect {path}: {code}, points to {want}: {want in html}")
for path in ["/robots.txt", "/llms.txt", "/search.json", "/feed.xml", "/fef7c5983d932aef444f8519cd687495.txt", "/images/og-banner.png",
             "/favicon.ico", "/assets/site.css", "/assets/site.js", "/assets/islands/sql.js", "/assets/data/moderation-sweep.json",
             "/assets/data/dsa-examples.json", "/assets/data/dublin-bikes/fct_station_hour.parquet", "/blog/precision-recall-content-moderation/", "/no-such-page/"]:
    print(get(path)[0], path)
_, home = get("/")
print("google verification tags on home:", len(re.findall(r'google-site-verification', home)), "| og:image:", bool(re.search(r'og:image" content="https://malavnaik.com/images/og-banner.png', home)))
print("home <title>:", re.search(r"<title>([^<]+)", home).group(1))
