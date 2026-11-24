"""Monthly "share kit": ready-to-post texts and a chart, written from the data. It never posts anything.

  python3 scripts/share_kit.py bikes [--month YYYY-MM]   kit for a published "Dublin Bikes in numbers" edition
                                                         (default: the newest edition in _posts/)
  python3 scripts/share_kit.py rent                      kit for new rent figures, only if the CSO period is new
  python3 scripts/share_kit.py --self-test

Writes share-kits/YYYY-MM/ (not published on the site, see _config.yml):
  bikes: chart.png (1200x630), reddit-dublin.md, email-pitch.md, blog-bot-post.md (the blog bot's copy of the edition)
  rent:  rent-chart.png (1200x630), reddit-irishpersonalfinance.md
and the issue text to share-kits/.issue.md, with its title on the first line. Run by .github/workflows/share-kit.yml.
Every sentence is built from numbers in _data/bikes/*.json or _data/rent_summary.json: findings are ranked by how
unusual they are, so each month leads with what actually stood out.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
SITE = "https://malavnaik.com"
KITS = ROOT / "share-kits"
RENT_DONE = KITS / "rent-periods-done.txt"  # CSO periods that already had a rent kit, one per line
CHECKLIST = """- [ ] Posted on r/Dublin (post body + first comment)
- [ ] Posted on r/irishbicycling
- [ ] (Every 2–3 months) Sent email pitch to IrishCycle / Dublin Cycling Campaign
- [ ] Close this issue when done"""
RULES = ("Before posting, read each subreddit's rules in its sidebar (self-promotion, [OC] and link rules change). "
         "UNVERIFIED: the kit could not check them for you.")


def month_name(m):
    return dt.datetime.strptime(m, "%Y-%m").strftime("%B %Y")


def front_matter(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8").split("---\n", 2)[1])


# ---------- Dublin Bikes ----------

def bikes_findings(r, prev):
    """(score, headline, sentence) for each finding the month's numbers support; the highest score is the most unusual."""
    f, st = [], r["busiest_stations"][0]
    mom = r.get("month_on_month")
    if mom:
        pct = mom["pct_change_estimated_pickups_per_day"]
        word = "rose" if pct >= 0 else "fell"
        f.append((abs(pct) * 2, f"Dublin Bikes pickups {word} {abs(pct):g}% on {month_name(mom['previous_month']).split()[0]}",
                  f"Estimated pickups per day {word} {abs(pct):g}% on {month_name(mom['previous_month']).split()[0]}, "
                  f"from about {mom['previous_estimated_pickups_per_day']:,} to {r['estimated_pickups_per_day']:,} a day."))
    rain = r["rain"]
    if rain["pct_change_vs_dry_same_hour"] is not None and rain["wet_hours"] >= 10:  # too few rainy hours says nothing
        pct = rain["pct_change_vs_dry_same_hour"]
        word = "fewer" if pct < 0 else "more"
        f.append((abs(pct), f"Rainy hours had {abs(pct):.0f}% {word} Dublin Bikes pickups",
                  f"In the {rain['wet_hours']} rainy hours, about {abs(pct):.0f}% {word} bikes were picked up than in dry hours "
                  f"at the same time of day."))
    old = prev["busiest_stations"][0]["station"] if prev else None
    if old and old != st["station"]:
        f.append((40, f"{st['station']} overtook {old} as the busiest Dublin Bikes station",
                  f"{st['station']} overtook {old} as the busiest station, with about {st['estimated_pickups']:,} estimated pickups."))
    else:
        again = " again" if old else ""
        f.append((15, f"{st['station']} was the busiest Dublin Bikes station{again}",
                  f"{st['station']} was the busiest station{again}, with about {st['estimated_pickups']:,} estimated pickups."))
    b = r["busiest_hour"]
    moved = prev and prev["busiest_hour"]["local_hour"] != b["local_hour"]
    f.append((25 if moved else 12, f"The busiest hour for Dublin Bikes was {b['label']}",
              f"The busiest hour was {b['label']}, with about {b['avg_estimated_pickups']} pickups across the network"
              + (f", moving from {prev['busiest_hour']['label']} the month before." if moved else " on average.")))
    e = r["emptiest_stations"][0]
    if e["pct_docks_with_bike"] < 10:
        f.append((30 - e["pct_docks_with_bike"], f"{e['station']} was almost always empty",
                  f"{e['station']} averaged just {e['pct_docks_with_bike']:g}% of its docks holding a bike, so it was usually empty."))
    full = r["fullest_stations"][0]
    if full["pct_docks_with_bike"] > 75:
        f.append((full["pct_docks_with_bike"] - 55, f"{full['station']} was often full",
                  f"{full['station']} averaged {full['pct_docks_with_bike']:g}% of its docks full, so finding a free dock there was hard."))
    f.append((10, f"About {r['estimated_pickups_per_day']:,} Dublin Bikes pickups a day",
              f"There were about {r['estimated_pickups_total']:,} estimated pickups across {r['coverage']['stations_reported']} "
              f"stations, roughly {r['estimated_pickups_per_day']:,} a day."))
    return sorted(f, key=lambda x: -x[0])


def bikes_texts(r, prev, post_url, edition):
    top = bikes_findings(r, prev)[:3]
    period = r["period"]["label"]
    title = f"{top[0][1]} ({period}) [OC]"
    body = (f"I record every Dublinbikes station every 15 minutes from the open feed, alongside Met Éireann rain data, "
            f"and three things stood out in {period}. " + " ".join(s for _, _, s in top))
    comment = (f"Source: the Dublinbikes station feed (Dublin City Council / JCDecaux) and Met Éireann hourly rainfall at Dublin "
               f"Airport, recorded by my open data pipeline (data on Hugging Face, CC BY 4.0). Pickups are estimates: drops in "
               f"available bikes between 15-minute snapshots, so bikes moved by rebalancing vans count too. Full tables, chart "
               f"and method: {post_url}")
    reddit = (f"# r/Dublin (also fine for r/irishbicycling)\n\n**Title**\n\n{title}\n\n**Post body**\n\n{body}\n\n"
              f"**First comment** (post it yourself straight after)\n\n{comment}\n\nAttach `chart.png` as the image.\n\n> {RULES}\n")
    bullets = "\n".join(f"- {s}" for _, _, s in top)
    pitch_body = (f"Hi,\n\nI'm Malav, a data engineer in Dublin. I keep an open record of every Dublinbikes station, every "
                  f"15 minutes, alongside Met Éireann rain data. Three things from {period}:\n\n{bullets}\n\n"
                  f"Tables, chart and method: {post_url}\nYou're welcome to use any of it, with a link back.\n\n"
                  f"Best,\nMalav Naik\nmalav@malavnaik.com")
    words = len(re.findall(r"\S+", pitch_body))
    assert words < 120, f"email pitch is {words} words, over 120"
    pitch = (f"# Email pitch (under 120 words: {words})\n\nFor IrishCycle or the Dublin Cycling Campaign, every 2–3 months. "
             f"Find the current address on their own contact page.\n\n**Subject:** {top[0][1]} ({period})\n\n{pitch_body}\n")
    intro = (f"{top[0][2]} {top[1][2]}\n\nThe numbers for {period}, from my open Dublin Bikes and weather pipeline:")
    return reddit, pitch, blog_bot_post(r, edition, intro)


def table(head, rows):
    return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, x)) + " |" for x in rows])


def blog_bot_post(r, edition, intro):
    """The edition as plain Markdown for the blog bot's queue: DEV gets real tables, not the site's template code."""
    m, period, rain = r["month"], r["period"]["label"], r["rain"]
    st = lambda rows: [(x["station"], f"{x['estimated_pickups']:,}", f"{x['pct_docks_with_bike']:g}%") for x in rows]
    fm = {"id": -int(m.replace("-", "")),  # negative: queued ahead of ordinary posts; unique per month (the bot matches taps by id)
          "title": edition["title"], "slug": edition["slug"], "description": edition["description"],
          "tags": edition.get("tags", []), "image": f"images/bikes-report/{m}.png", "image_alt": edition.get("image_alt", ""),
          "platforms": ["blog", "devto", "linkedin", "medium"], "linkedin_intro": f"New Dublin Bikes numbers for {period}. " + intro.split("\n\n")[0], "status": "ready"}
    body = f"""# {edition['title']}

![{edition.get('image_alt', '')}](../images/bikes-report/{m}.png)

{intro}

- About **{r['estimated_pickups_total']:,}** estimated pickups across {r['coverage']['stations_reported']} stations, roughly {r['estimated_pickups_per_day']:,} a day.
- Busiest hour: **{r['busiest_hour']['label']}**, about {r['busiest_hour']['avg_estimated_pickups']} pickups on average.

## Busiest stations

{table(["Station", "Estimated pickups", "Docks with a bike"], st(r['busiest_stations']))}

## Quietest stations

{table(["Station", "Estimated pickups", "Docks with a bike"], st(r['quietest_stations']))}

## Where to find a bike

{table(["Usually full", "Docks with a bike"], [(x['station'], f"{x['pct_docks_with_bike']:g}%") for x in r['fullest_stations']])}

{table(["Usually empty", "Docks with a bike"], [(x['station'], f"{x['pct_docks_with_bike']:g}%") for x in r['emptiest_stations']])}

## What rain did

{table(["Weather", "Hours", "Average estimated pickups per hour"], [("Rainy (0.1 mm or more)", rain['wet_hours'], rain['wet_avg_estimated_pickups_per_hour']), ("Dry (0 mm)", rain['dry_hours'], rain['dry_avg_estimated_pickups_per_hour'])])}

## How the numbers are made

Every 15 minutes my pipeline records how many bikes each station has. When a station has fewer bikes than at the previous snapshot, the difference counts as pickups, so these are estimates: bikes moved by the rebalancing vans count too. The data is open on Hugging Face ([raw](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-raw), [modelled](https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts), CC BY 4.0). Sources: Dublinbikes feed (Dublin City Council / JCDecaux) and Met Éireann.

Every edition and the running totals: [Dublin Bikes statistics]({SITE}/dublin-bikes/).
"""
    return "---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=1000) + "---\n" + body


def bikes(month=None):
    editions = {str(front_matter(p).get("bikes_month")): p for p in glob.glob(str(ROOT / "_posts/*dublin-bikes-in-numbers-*.md"))}
    month = month or max(editions)
    assert month in editions, f"No published edition for {month} in _posts/. Publish the post first, then make the kit."
    edition = front_matter(editions[month])
    r = json.loads((ROOT / f"_data/bikes/{month}.json").read_text())
    p = ROOT / f"_data/bikes/{(dt.date(int(month[:4]), int(month[5:]), 1) - dt.timedelta(1)):%Y-%m}.json"
    prev = json.loads(p.read_text()) if p.exists() else None
    post_url = f"{SITE}/blog/{edition['slug']}/"
    out = KITS / month
    out.mkdir(parents=True, exist_ok=True)
    from bikes_report import chart
    chart(r, out / "chart.png", size=(8, 4.2), dpi=150, corner="malavnaik.com/dublin-bikes")
    reddit, pitch, bot = bikes_texts(r, prev, post_url, edition)
    (out / "reddit-dublin.md").write_text(reddit, encoding="utf-8")
    (out / "email-pitch.md").write_text(pitch, encoding="utf-8")
    (out / "blog-bot-post.md").write_text(bot, encoding="utf-8")
    issue(f"Share kit ready: Dublin Bikes {month_name(month)}", out, ["reddit-dublin.md", "email-pitch.md"], "chart.png",
          CHECKLIST + "\n\n`blog-bot-post.md` is the blog bot's copy of this edition (for LinkedIn, DEV and Medium): "
          "see docs/blog-bot-bikes-editions.md for how the bot picks it up.")
    return out


# ---------- Rent ----------

def rent_texts(s):
    from rent_build import salary_needed
    c = s["counties"]
    hi, lo = max(c, key=lambda x: x["share_pct"]), min(c, key=lambda x: x["share_pct"])
    rise = max(c, key=lambda x: x["change_pct"])
    over_half = sum(x["share_pct"] > 50 for x in c)
    label = s["latest_label"]
    title = (f"Average new rent takes about {hi['share_pct']}% of take-home pay in {hi['name']} and {lo['share_pct']}% in "
             f"{lo['name']}: every county, {label} [OC]")
    body = (f"I compared the RTB's average rent for new tenancies in each county ({label}) with estimated take-home pay on "
            f"that county's median wage. It ranges from {hi['share_pct']}% in {hi['name']} ({hi['rent_eur']} a month) to "
            f"{lo['share_pct']}% in {lo['name']} ({lo['rent_eur']}), and in {over_half} of the 26 counties it is more than half. "
            f"The biggest rise on a year was in {rise['name']}, up {rise['change_pct']}%. "
            f"To keep {hi['name']}'s average new rent to 30% of take-home pay, one person would need roughly "
            f"€{salary_needed(hi['rent']):,} a year before tax.")
    comment = (f"Source: RTB average rent for new tenancies via the CSO (table RIH02) and CSO median weekly earnings by county "
               f"(DEA05, {s['earnings_year']}), both CC BY 4.0. Take-home pay is my estimate for a single PAYE employee at "
               f"{s['tax_year']} tax rates; these are rents for new tenancies, not what existing tenants pay. Every county, with "
               f"a budget calculator: {SITE}/rent/")
    return (f"# r/irishpersonalfinance\n\n**Title**\n\n{title}\n\n**Post body**\n\n{body}\n\n**First comment** (post it "
            f"yourself straight after)\n\n{comment}\n\nAttach `rent-chart.png` as the image.\n\n> {RULES}\n")


def rent_chart(s, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    c = sorted(s["counties"], key=lambda x: -x["share_pct"])
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    ax.bar([x["name"] for x in c], [x["share_pct"] for x in c], color="#2a78d6", width=0.75)
    ax.axhline(30, color="#52514e", linewidth=0.8, linestyle="--")
    ax.text(len(c) - 0.6, 30, "30% rule of thumb", ha="right", va="center", fontsize=7, color="#52514e",
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
    ax.tick_params(axis="x", labelrotation=60, labelsize=7, length=0)
    ax.tick_params(axis="y", labelsize=7, colors="#52514e", length=0)
    ax.grid(axis="y", color="#e5e4df", linewidth=0.6)
    ax.set_axisbelow(True)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_ylabel("% of take-home pay", fontsize=8, color="#52514e")
    fig.suptitle(f"Average new rent as a share of take-home pay, by county ({s['latest_label']})", x=0.06, ha="left",
                 fontsize=11, fontweight="bold")
    fig.text(0.06, 0.02, "Data: RTB via CSO (RIH02), CSO (DEA05). Take-home pay estimated on each county's median wage.",
             fontsize=6.5, color="#52514e")
    fig.text(0.97, 0.02, "malavnaik.com/rent", fontsize=7, color="#52514e", ha="right")
    fig.subplots_adjust(left=0.08, right=0.98, top=0.88, bottom=0.27)
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def rent(force=False):
    s = json.loads((ROOT / "_data/rent_summary.json").read_text())
    done = RENT_DONE.read_text().split() if RENT_DONE.exists() else []
    if s["latest_period"] in done and not force:
        print(f"Rent figures for {s['latest_period']} already had a share kit. Nothing to do.")
        return None
    out = KITS / dt.date.today().strftime("%Y-%m")
    out.mkdir(parents=True, exist_ok=True)
    rent_chart(s, out / "rent-chart.png")
    (out / "reddit-irishpersonalfinance.md").write_text(rent_texts(s), encoding="utf-8")
    if s["latest_period"] not in done:
        RENT_DONE.write_text("".join(f"{p}\n" for p in done + [s["latest_period"]]))
    issue(f"Share kit ready: Irish rents {s['latest_label']}", out, ["reddit-irishpersonalfinance.md"], "rent-chart.png",
          "- [ ] Posted on r/irishpersonalfinance (post body + first comment)\n- [ ] Close this issue when done")
    return out


# ---------- issue text ----------

def issue(title, out, files, png, checklist):
    rel = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'malavnaik99/malavnaik99.github.io')}/blob/main/share-kits/{out.name}"
    parts = [f"Everything below was written from the data. **Nothing has been posted**: you post it yourself.",
             f"![chart]({rel}/{png}?raw=true)\n\nChart: [`share-kits/{out.name}/{png}`]({rel}/{png}) (1200×630, download it to attach).",
             checklist]
    parts += [(out / f).read_text(encoding="utf-8") for f in files]
    (KITS / ".issue.md").write_text(title + "\n" + "\n\n---\n\n".join(parts) + "\n", encoding="utf-8")


# ---------- self-test ----------

def self_test():
    import shutil
    import tempfile
    global KITS, RENT_DONE
    r = json.loads((ROOT / "_data/bikes/2026-10.json").read_text())
    prev = json.loads(json.dumps(r))
    prev["busiest_stations"][0]["station"] = "Somewhere Else"
    nxt = dict(r, month="2026-11", month_on_month={"previous_month": "2026-10", "previous_estimated_pickups_per_day": 3142,
                                                   "pct_change_estimated_pickups_per_day": -12.4})
    edition = {"title": "Dublin Bikes in numbers: November 2026", "slug": "dublin-bikes-in-numbers-november-2026",
               "description": "d", "tags": ["dublin"], "image_alt": "a"}
    a = bikes_texts(r, None, "https://x/", edition)
    b = bikes_texts(nxt, prev, "https://x/", edition)
    for reddit, pitch, bot in (a, b):
        title = reddit.split("**Title**\n\n")[1].split("\n")[0]
        body = reddit.split("**Post body**\n\n")[1].split("\n\n")[0]
        assert title.endswith(" [OC]") and len(title) <= 300, title
        assert 3 <= len(re.findall(r"[.!?](?:\s|$)", body)) <= 4, body
        assert not re.search(r"(?i)\b(amazing|incredible|shocking|insane|huge|massive)\b", reddit + pitch), "hype word"
        fm = yaml.safe_load(bot.split("---\n")[1])
        assert fm["status"] == "ready" and fm["slug"] and fm["image"].startswith("images/") and "{%" not in bot
    assert a[0] != b[0], "two different months produced the same post"
    assert "overtook Somewhere Else" in b[0], b[0]
    assert any("12.4%" in x[2] for x in bikes_findings(nxt, prev)), "month-on-month change missing from the findings"
    fm = yaml.safe_load(b[2].split("---\n")[1])
    assert fm["id"] == -202611 and fm["linkedin_intro"]
    # Rent: a kit only when the period is new, and the chart is 1200x630
    tmp = Path(tempfile.mkdtemp())
    KITS, RENT_DONE = tmp, tmp / "rent-periods-done.txt"
    s = json.loads((ROOT / "_data/rent_summary.json").read_text())
    RENT_DONE.write_text(s["latest_period"] + "\n")
    assert rent() is None
    RENT_DONE.write_text("2020H1\n")
    out = rent()
    assert s["latest_period"] in RENT_DONE.read_text() and rent() is None
    from PIL import Image
    assert Image.open(out / "rent-chart.png").size == (1200, 630)
    from bikes_report import chart
    chart(r, tmp / "c.png", size=(8, 4.2), dpi=150, corner="malavnaik.com/dublin-bikes")
    assert Image.open(tmp / "c.png").size == (1200, 630)
    assert (tmp / ".issue.md").read_text().startswith("Share kit ready: Irish rents ")
    shutil.rmtree(tmp)
    print("Self-test passed.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", nargs="?", choices=["bikes", "rent"])
    ap.add_argument("--month")
    ap.add_argument("--force", action="store_true", help="rent: make a kit even if this period already had one")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        self_test()
    elif a.kind == "bikes":
        print(f"Wrote {bikes(a.month)}")
    elif a.kind == "rent":
        out = rent(a.force)
        print(f"Wrote {out}" if out else "")
    else:
        ap.error("say bikes, rent or --self-test")
