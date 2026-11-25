"""Keeps the "Living in Ireland" guide (_data/stamps.yml) accurate.

  python3 scripts/stamps_check.py --self-test        data checks (run before every deploy): every quote is word for word
                                                     on the saved official page, wording rule, reviewed rows complete
  python3 scripts/stamps_check.py --review           rewrite REVIEW-living-in-ireland.md (the list Malav checks)
  python3 scripts/stamps_check.py --verify 4/work 2/checklist-6
                                                     mark rows checked: reviewed: true, last_verified: today
  python3 scripts/stamps_check.py --links            weekly: is every official link still there? (one issue)
  python3 scripts/stamps_check.py --content          monthly: did any official page's text change? (one issue per page)

--links and --content open/close GitHub issues when GITHUB_TOKEN and GITHUB_REPOSITORY are set (the workflow
.github/workflows/stamps-check.yml); otherwise they only print. --content saves each page's text to
data/stamps/snapshots/ so next month has something to compare with. It never changes what the site shows.
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "_data/stamps.yml"
SNAP = ROOT / "data/stamps/snapshots"
REVIEW = ROOT / "REVIEW-living-in-ireland.md"
UA = {"User-Agent": "malavnaik.com link checker (+https://malavnaik.com/contact/)"}
OFFICIAL = ("irishimmigration.ie", "gov.ie", "citizensinformation.ie", "mywelfare.ie", "revenue.ie", "hse.ie", "rtb.ie",
            "enterprise.gov.ie", "leapcard.ie")
BANNED = re.compile(r"(?i)\b(you are entitled|you're entitled|you will get|you will receive|you qualify|you can claim)\b")
LINKS_TITLE = "Living in Ireland: official links need attention"
BLOCKED_TITLE = "Living in Ireland: official pages could not be checked"


def load():
    return yaml.safe_load(DATA.read_text(encoding="utf-8"))


def all_rows(d):
    """Every checkable row: stamp × topic rows plus the Stamp 2 checklist (id checklist-1, -2, …)."""
    rows = [dict(r, key=f"{r['stamp']}/{r['topic']}") for r in d["rows"]]
    rows += [dict(r, stamp="2", topic=f"checklist-{i}", key=f"2/checklist-{i}") for i, r in enumerate(d["checklist"], 1)]
    return rows


def label(d, r):
    stamp = next(s["name"] for s in d["stamps"] if s["id"] == r["stamp"])
    topic = next((t["title"] for t in d["topics"] if t["id"] == r["topic"]), None) or \
        f"First 90 days: {d['checklist'][int(r['topic'].split('-')[1]) - 1]['step']}"
    return f"{stamp} → {topic}"


# ---------- page text (the same extraction for the saved copy and the monthly check) ----------

SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form", "aside"}
BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "tr", "div", "section", "br", "td", "th", "dt", "dd"}


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, t, a):
        self.skip += t in SKIP
        if t in BLOCK:
            self.out.append("\n")
        if t in ("h1", "h2", "h3", "h4") and not self.skip:
            self.out.append("#" * int(t[1]) + " ")

    def handle_endtag(self, t):
        if t in SKIP and self.skip:
            self.skip -= 1
        if t in BLOCK:
            self.out.append("\n")

    def handle_data(self, s):
        if not self.skip:
            self.out.append(s)


def main_text(raw_html):
    """The page's main text, without menus, footers or scripts."""
    m = re.search(r"<main\b.*?</main>", raw_html, re.S | re.I)
    p = Text()
    p.feed(m.group(0) if m else raw_html)
    text = re.sub(r"[ \t\xa0]+", " ", "".join(p.out))
    text = "\n".join(line.strip() for line in text.splitlines())
    return re.sub(r"\n{3,}", "\n\n", text).strip()


DATE = re.compile(r"(?i)(last (updated|reviewed|modified)|page updated|published)[^\n]*|\b\d{1,2}(st|nd|rd|th)? "
                  r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{4}\b")


def fingerprint(text):
    """Hash of the text with dates taken out, so a new 'last updated' date alone isn't a change."""
    return hashlib.sha256(re.sub(r"\s+", " ", DATE.sub("", text)).strip().encode()).hexdigest()


def snap_path(url):
    return SNAP / f"{hashlib.sha1(url.encode()).hexdigest()[:12]}.txt"


def read_snap(url):
    p = snap_path(url)
    return p.read_text(encoding="utf-8").split("\n\n", 1)[1].strip() if p.exists() else None


def write_snap(url, text):
    SNAP.mkdir(parents=True, exist_ok=True)
    snap_path(url).write_text(f"URL: {url}\nSAVED: {dt.date.today()}\n\n{text}\n", encoding="utf-8")


def fetch(url):
    """(status, final_url, body). status is 'ok', 'broken' (gone), or 'blocked' (couldn't tell: refused, timeout)."""
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return "ok", r.geturl(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return ("broken" if e.code in (404, 410) else "blocked"), url, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        gone = "Name or service not known" in str(e.reason) or "nodename nor servname" in str(e.reason)
        return ("broken" if gone else "blocked"), url, str(e.reason)
    except Exception as e:  # timeouts and the like: can't tell, so not "broken"
        return "blocked", url, str(e)


def same_page(a, b):
    norm = lambda u: re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()
    return norm(a) == norm(b)


# ---------- issues ----------

def github():
    return bool(os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY"))


def open_issues():
    sys.path.insert(0, str(ROOT / "scripts"))
    from site_health import gh
    issues = []
    for page in range(1, 6):
        batch = gh("GET", f"/issues?state=open&per_page=100&page={page}")
        issues += [i for i in batch if "pull_request" not in i]
        if len(batch) < 100:
            return issues, gh
    return issues, gh


def set_issue(title, body, problem, match=None):
    """Open (or update) the issue when there's a problem; close it when there isn't."""
    if not github():
        print(f"--- {title} ({'PROBLEM' if problem else 'fine'})\n{body if problem else ''}")
        return
    issues, gh = open_issues()
    found = next((i for i in issues if (match(i) if match else i["title"] == title)), None)
    if problem and found:
        gh("POST", f"/issues/{found['number']}/comments", {"body": "Still the case:\n\n" + body})
    elif problem:
        gh("POST", "/issues", {"title": title, "body": body})
    elif found and not match:
        gh("POST", f"/issues/{found['number']}/comments", {"body": "Fixed: every page checked fine this time."})
        gh("PATCH", f"/issues/{found['number']}", {"state": "closed", "state_reason": "completed"})


def run_url():
    return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"


def by_url(d):
    urls = {}
    for r in all_rows(d):
        if r.get("official_url"):
            urls.setdefault(r["official_url"], []).append(r)
    for h in d["help"]:
        urls.setdefault(h["url"], []).append({"key": "help", "label": f"Help box → {h['name']}"})
    return urls


def rows_list(d, rows):
    return "\n".join(f"- {r.get('label') or label(d, r)} (`{r['key']}`)" for r in rows)


def blocked_note(d, blocked):
    body = ("**What happened:** these official pages refused or timed out when GitHub tried to check them, so they "
            "couldn't be checked this time. **The site is unaffected** and keeps showing what you last reviewed.\n\n"
            + "\n".join(f"- {u} ({why})\n{rows_list(d, rows)}" for u, why, rows in blocked)
            + "\n\n**What to do:** open each link in your browser. If it loads, nothing is wrong: some government sites "
              "refuse automated checks, and this issue closes itself when a later check gets through. If it doesn't load, "
              "ask Claude: \"This official page has moved or gone: (link). Find the new official page and update "
              "_data/stamps.yml.\"\n\nRun: " + run_url())
    set_issue(BLOCKED_TITLE, body, bool(blocked))


def check_links():
    d = load()
    bad, blocked = [], []
    for url, rows in by_url(d).items():
        status, final, info = fetch(url)
        if status == "ok" and not same_page(url, final):
            bad.append((url, f"now redirects to {final}", rows))
        elif status == "broken":
            bad.append((url, f"gone ({info})", rows))
        elif status == "blocked":
            blocked.append((url, info, rows))
        print(f"{status:8} {url}" + ("" if same_page(url, final) else f" -> {final}"))
    body = ("**What happened:** the weekly check found official links in the Living in Ireland guide that are gone or now "
            "point somewhere else. Visitors following them may land on the wrong page.\n\n"
            + "\n".join(f"- {u}: **{why}**\n{rows_list(d, rows)}" for u, why, rows in bad)
            + "\n\n**What to do:** open Claude Code on this repo and say: \"Fix the official links in this issue: (paste it). "
              "Use only official sites, and keep reviewed: false on any row whose source changed.\"\n\nRun: " + run_url())
    set_issue(LINKS_TITLE, body, bool(bad))
    blocked_note(d, blocked)


def check_content():
    d = load()
    blocked, changed = [], 0
    for url, rows in by_url(d).items():
        if not any(r["key"] != "help" for r in rows):
            continue  # help-box homepages change all the time; the weekly link check covers them
        status, final, body = fetch(url)
        if status != "ok":
            blocked.append((url, body, rows))
            continue
        new, old = main_text(body), read_snap(url)
        if old is not None and fingerprint(old) != fingerprint(new):
            changed += 1
            diff = [l for l in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0)
                    if l[:1] in "+-" and l[:3] not in ("+++", "---")][:40]
            flat = re.sub(r"\s+", " ", new)
            hit = [r for r in rows if r["key"] != "help" and any(re.sub(r"\s+", " ", q) not in flat for q in r["quote"])]
            rows = hit + [r for r in rows if r not in hit]  # rows whose quoted words are gone come first
            first = rows[0]
            title = f"Official page changed — re-check: {label(d, first)}" + (f" (+{len(rows) - 1} more)" if len(rows) > 1 else "")
            text = (f"**What happened:** the text of this official page changed since last month's check:\n{url}\n\n"
                    f"**The site has not changed**: it keeps showing what you last reviewed until you confirm.\n\n"
                    + (f"**Rows whose quoted words are no longer on the page (check these first):**\n{rows_list(d, hit)}\n\n" if hit else
                       "**None of the quoted sentences changed**, so the rows below are probably still right; skim the change anyway.\n\n")
                    + f"**All rows that use this page:**\n{rows_list(d, rows)}\n\n**What changed** (− old, + new, first 40 lines):\n"
                    "```diff\n" + "\n".join(diff) + "\n```\n\n**What to do:** read the page. If each row above is still right, "
                    "tell Claude Code \"mark (row ids) verified\". If not, tell Claude what changed and it will update the "
                    f"summary (keeping reviewed: false until you check it).\n\n<!-- page: {url} -->\nRun: " + run_url())
            set_issue(title, text, True, match=lambda i, u=url: f"<!-- page: {u} -->" in (i.get("body") or ""))
        write_snap(url, new)
        print(f"{'changed' if old is not None and fingerprint(old) != fingerprint(new) else 'same':8} {url}")
    blocked_note(d, blocked)
    print(f"{changed} page(s) changed, {len(blocked)} could not be checked.")


# ---------- review file and verify ----------

def write_review():
    d = load()
    out = ["# Review: Living in Ireland guide\n",
           "Generated by `python3 scripts/stamps_check.py --review` from `_data/stamps.yml`. **Don't edit this file**: "
           "tell Claude what to fix, or \"mark 4/work verified\" for rows that are right.\n",
           "Only rows marked reviewed appear in full on the site; the rest show just the official link. Every quote below "
           "was checked word for word against the saved copy of the official page.\n"]
    rows = all_rows(d)
    todo = [r for r in rows if not r["reviewed"] and r.get("summary")]
    empty = [r for r in rows if not r.get("summary")]
    out.append(f"**{len(todo)} rows to review**, {sum(r['reviewed'] for r in rows)} already reviewed, "
               f"{len(empty)} still need an official source (see the end).\n")
    for r in todo:
        out += [f"## `{r['key']}`: {label(d, r)}\n", f"**Summary (appears on the site once you approve it):** {r['summary']}\n",
                f"**Official page:** [{r['source_name']}]({r['official_url']})  ", f"**Last verified:** {r['last_verified']}\n",
                "**Exact words on the official page:**\n"] + [f"> {q}\n" for q in r["quote"]]
        if r.get("notes"):
            out.append(f"**Note:** {r['notes']}\n")
        out.append("- [ ] Correct\n")
    out.append("## Still needs an official source\n")
    out.append("These show \"official source being added\" on the site. Paste the official page's text to Claude to fill them.\n")
    out += [f"- `{r['key']}`: {label(d, r)}" + (f" ({r['notes']})" if r.get("notes") else "") for r in empty]
    have = {(r["stamp"], r["topic"]) for r in d["rows"]}
    for t in d["topics"]:
        missing = [s["name"] for s in d["stamps"] if (s["id"], t["id"]) not in have]
        if missing:
            out.append(f"- {t['title']}: no row yet for {', '.join(missing)}")
    out.append("\n## Help box links not yet confirmed\n")
    out += [f"- {h['name']}: {h['url']} (UNVERIFIED: confirm this is the right official page)" for h in d["help"] if not h["checked"]]
    REVIEW.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {REVIEW.name}: {len(todo)} rows to review, {len(empty)} without a source.")


def verify(keys):
    """Mark rows reviewed with today's date, editing the two lines in place (comments and layout stay as they are)."""
    text = DATA.read_text(encoding="utf-8")
    d = yaml.safe_load(text)
    today = dt.date.today().isoformat()
    for key in keys:
        stamp, topic = key.lower().split("/", 1)
        if topic.startswith("checklist-"):
            n = int(topic.split("-")[1])
            start = [m.start() for m in re.finditer(r"^  - stage: ", text, re.M)][n - 1]
        else:
            m = re.search(rf'^  - stamp: "{re.escape(stamp)}"\n    topic: {re.escape(topic)}\n', text, re.M)
            assert m, f"No row {key} in _data/stamps.yml"
            start = m.start()
        end = text.find("\n  - ", start + 1)
        end = len(text) if end == -1 else end
        block = text[start:end]
        assert "summary: \"\"" not in block, f"{key} has no summary yet, so there's nothing to mark verified."
        block = re.sub(r'last_verified: "[^"]*"', f'last_verified: "{today}"', block)
        block = block.replace("reviewed: false", "reviewed: true")
        text = text[:start] + block + text[end:]
        print(f"Marked {key} verified ({today}).")
    DATA.write_text(text, encoding="utf-8")
    yaml.safe_load(text)
    del d


# ---------- self-test (runs before every deploy) ----------

def self_test():
    d = load()
    stamps, topics = {s["id"] for s in d["stamps"]}, {t["id"] for t in d["topics"]}
    seen = set()
    for r in all_rows(d):
        k = r["key"]
        assert k not in seen, f"{k} appears twice"
        seen.add(k)
        assert r["stamp"] in stamps, f"{k}: unknown stamp"
        assert r["topic"] in topics or r["topic"].startswith("checklist-"), f"{k}: unknown topic"
        assert not BANNED.search(r.get("summary") or ""), f"{k}: summary breaks the wording rule ({BANNED.search(r['summary']).group(0)})"
        if r.get("official_url"):
            host = re.sub(r"^https?://(www2?\.)?", "", r["official_url"]).split("/")[0]
            assert host.endswith(OFFICIAL), f"{k}: {host} is not one of the official sources"
            assert r["quote"] and r["summary"] and r["last_verified"], f"{k}: a sourced row needs summary, quote and date"
            page = read_snap(r["official_url"])
            if page is not None:
                flat = re.sub(r"\s+", " ", page)
                for q in r["quote"]:
                    assert re.sub(r"\s+", " ", q) in flat, f"{k}: quote not found word for word on the saved page: {q!r}"
        else:
            assert not r.get("summary") and not r["reviewed"], f"{k}: a row with a summary needs an official_url"
        if r["reviewed"]:
            dt.date.fromisoformat(r["last_verified"])
    # The wording rule also covers the FAQ text built from `depends`.
    for t in d["topics"]:
        assert not BANNED.search(t.get("depends", "")), f"topic {t['id']}: wording rule"
    # verify() edits only the row it's asked to: try it on a copy.
    global DATA
    import shutil
    import tempfile
    real, tmp = DATA, Path(tempfile.mkdtemp()) / "stamps.yml"
    shutil.copy(real, tmp)
    DATA = tmp
    try:
        todo = [r["key"] for r in all_rows(load()) if r.get("summary") and not r["reviewed"]]
        pick = [k for k in todo if "checklist" not in k][:1] + [k for k in todo if "checklist" in k][:1]
        verify(pick)  # practise on rows not yet reviewed, so real approvals never make this fail
        after = all_rows(load())
        changed = {r["key"] for r, b in zip(after, all_rows(yaml.safe_load(real.read_text()))) if r != b}
        assert changed == set(pick), (changed, pick)
        assert all(r["last_verified"] == dt.date.today().isoformat() for r in after if r["key"] in pick)
        assert tmp.read_text().startswith("# Living in Ireland")  # comments kept
    finally:
        DATA = real
    assert fingerprint("Rules\nLast updated: 3 May 2026\nText") == fingerprint("Rules\nLast updated: 9 June 2026\nText")
    assert fingerprint("You can work 20 hours") != fingerprint("You can work 15 hours")
    assert fingerprint("Same text\n") == fingerprint("Same text")  # a saved copy ends with a line break
    assert main_text("<html><nav>Menu</nav><main><h2>Title</h2><p>Body</p></main><footer>F</footer></html>") == "## Title\n\nBody"
    print(f"Self-test passed: {len(seen)} rows, every saved quote found word for word.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--verify", nargs="+", metavar="STAMP/TOPIC")
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--content", action="store_true")
    a = ap.parse_args()
    if a.verify:
        verify(a.verify)
        write_review()
    elif a.review:
        write_review()
    elif a.links:
        check_links()
    elif a.content:
        check_content()
    else:
        self_test()
