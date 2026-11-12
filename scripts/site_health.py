"""Weekly health check for malavnaik.com (run by .github/workflows/site-health.yml).

Runs seven checks. For each failing check it opens one GitHub Issue titled "Site health: <check>" (or updates the
one already open); when the check passes again it closes that issue. Without GITHUB_TOKEN it only prints results.

    python3 scripts/site_health.py                    # all checks
    python3 scripts/site_health.py --print-pages      # list the site's pages (for the link checker)
    python3 scripts/site_health.py --self-test        # test the parsing helpers offline
"""
import csv, datetime, hashlib, html, json, os, pathlib, re, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://malavnaik.com"
UA = {"User-Agent": "Mozilla/5.0 (compatible; malavnaik-site-health/1.0; +https://malavnaik.com)"}
MAINT = "https://github.com/malavnaik99/malavnaik99.github.io/blob/main/MAINTENANCE.md"
# Public government data that lists the client as one employer among many; Malav chose to keep it (5 Nov 2026).
CLIENT_SCAN_SKIP = {"permits-2025/index.html", "permits-issued-to-companies-2025.xlsx"}
# Fingerprints (SHA-256) of the employer's client's names, so this file never contains the names themselves.
CLIENT_HASH_ANY_CASE = {
    "3d59f7548e1af2151b64135003ce63c0a484c26b9b8b166a7b1c1805ec34b00a",
    "5ede56738376a8c53a7c99bf275b077a5c10df780a20cf3d8282fd59a2a9fb56",
    "ec8202b6f9fb16f9e26b66367afa4e037752f3c09a18cefab426165e06a424b1",
}
CLIENT_HASH_CAPITALISED = "ea3bd73e2b506e00527232b3ed743c066da83a8e3066f62a71e75eb9b4aa1db6"  # only as a capitalised word: the lowercase form is an HTML tag
BOT_BLOCKING_HOSTS = ("linkedin.com",)  # these refuse automated visits, so their tracker rows are listed but not checked


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def fetch(url, follow=True, timeout=30):
    """Return (status, final_url, location_header, body_text); status is an error string if the request failed."""
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(urllib.request.Request(url, headers=UA), timeout=timeout)
        return r.status, r.geturl(), r.headers.get("Location"), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, url, e.headers.get("Location"), ""
    except Exception as e:  # DNS failure, timeout, TLS error
        return f"no answer ({type(e).__name__}: {str(e)[:80]})", url, None, ""


def sha(word):
    return hashlib.sha256(word.encode()).hexdigest()


def is_client_word(word):
    return sha(word.lower()) in CLIENT_HASH_ANY_CASE or (word[0].isupper() and sha(word.lower()) == CLIENT_HASH_CAPITALISED)


def page_title(body):
    m = re.search(r"<title>(.*?)</title>", body, re.S)
    return html.unescape(m.group(1).strip()) if m else ""


def has_person(body):
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            data = json.loads(block)
        except ValueError:
            continue
        items = data.get("@graph", [data]) if isinstance(data, dict) else data
        if any(isinstance(i, dict) and i.get("@type") == "Person" for i in items):
            return True
    return False


def site_pages():
    status, _, _, body = fetch(SITE + "/sitemap.xml")
    if status != 200:
        raise RuntimeError(f"the sitemap ({SITE}/sitemap.xml) answered {status}")
    return [u for u in re.findall(r"<loc>(.*?)</loc>", body) if not u.lower().endswith(".pdf")]


# ---------- the seven checks: each returns a list of problems (empty = passed) ----------

def check_https():
    problems = []
    status, final, _, _ = fetch(SITE + "/")
    if status != 200:
        problems.append(f"{SITE}/ answered {status} instead of 200 (OK).")
    elif not final.startswith(SITE):
        problems.append(f"{SITE}/ ended up at {final} instead of staying on {SITE}.")
    for url in ("http://malavnaik.com/", "http://www.malavnaik.com/", "https://www.malavnaik.com/"):
        status, final, _, _ = fetch(url)
        if status != 200 or not final.startswith(SITE + "/"):
            problems.append(f"{url} should forward to {SITE}/ but ended at {final} with answer {status}.")
    return problems


def check_titles():
    title = json.loads((ROOT / "identity/identity.json").read_text())["title"]
    problems = []
    for url in site_pages():
        status, _, _, body = fetch(url)
        if status != 200:
            problems.append(f"{url} answered {status}.")
            continue
        if title not in page_title(body):
            problems.append(f"{url}: title is \"{page_title(body) or '(none)'}\" and doesn't contain \"{title}\".")
        if not has_person(body):
            problems.append(f"{url}: the Person profile data (JSON-LD) is missing or broken.")
    return problems


def check_links(report="lychee.json"):
    path = ROOT / report
    if not path.exists():
        return ["The link checker (lychee) didn't produce a report, so links weren't checked."]
    data = json.loads(path.read_text())
    print(f"Link checker: {data.get('total', '?')} links found, {data.get('successful', '?')} OK, {data.get('excludes', '?')} skipped on purpose, {data.get('errors', '?')} broken.")
    broken = {}  # one line per broken link, listing the pages it's on
    for page, fails in (data.get("error_map") or data.get("fail_map") or {}).items():
        for f in fails:
            status = f.get("status", {})
            reason = status.get("text") or status.get("code") or status
            entry = broken.setdefault(f.get("url"), {"reason": reason, "pages": []})
            if "cached" not in str(reason).lower():
                entry["reason"] = reason
            entry["pages"].append(page)
    return [f"{url} → {b['reason']} (on {len(b['pages'])} page(s), e.g. {b['pages'][0]})" for url, b in broken.items()]


def check_profiles():
    problems, notes = [], []
    with open(ROOT / "backlinks/tracker.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            if row["status"].strip() != "live" or not row["my_profile_url"].strip():
                continue
            url = row["my_profile_url"].strip()
            if any(h in url for h in BOT_BLOCKING_HOSTS):
                notes.append(f"{row['platform']}: {url} blocks automated checks; check it by hand now and then.")
                continue
            status, _, _, body = fetch(url)
            if status != 200:
                problems.append(f"{row['platform']}: {url} answered {status}.")
            elif "malavnaik.com" not in body:
                problems.append(f"{row['platform']}: {url} loads but no longer contains a link to malavnaik.com.")
    check_profiles.notes = notes
    return problems


def check_cname():
    path = ROOT / "CNAME"
    if not path.exists():
        return ["The CNAME file is missing."]
    content = path.read_text().strip()
    return [] if content == "malavnaik.com" else [f'The CNAME file says "{content}" instead of "malavnaik.com".']


def check_client():
    problems = []
    for f in sorted(ROOT.rglob("*")):
        rel = f.relative_to(ROOT).as_posix()
        if f.is_dir() or rel.startswith(".git/") or rel in CLIENT_SCAN_SKIP or rel == "lychee.json":
            continue
        raw = f.read_bytes()
        if b"\0" in raw[:4096]:  # binary file (images, PDF)
            continue
        for n, line in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
            if any(is_client_word(w) for w in re.findall(r"[A-Za-z]+", line)):
                problems.append(f"{rel}, line {n}")
    return problems


def check_sky():
    """The home page sky's live data (the pipeline's "latest" file) must be under two hours old. Skipped until switched on."""
    url = json.loads((ROOT / "_data/sky_live.json").read_text()).get("url")
    if not url:
        check_sky.notes = ["Bike sky: live data is not switched on yet (_data/sky_live.json has no url), so the page shows the saved snapshot."]
        return []
    status, _, _, body = fetch(url)
    if status != 200:
        return [f"{url} answered {status} instead of 200 (OK)."]
    try:
        made = json.loads(body)["generated_utc"]
        age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(made.replace("Z", "+00:00"))).total_seconds() / 3600
    except Exception as e:
        return [f"{url} isn't the expected data file ({type(e).__name__}: {e})."]
    return [] if age <= 2 else [f"The newest bike data was made at {made}, {age:.1f} hours ago; it should be under 2 hours."]


CHECKS = [
    ("Site not loading", check_https,
     "malavnaik.com didn't load over HTTPS, or the http:// / www addresses don't forward to it.",
     "GitHub Pages is down or re-deploying, the custom domain was removed in GitHub → Settings → Pages, or a Cloudflare DNS setting changed.",
     "1. Wait 15 minutes and click **Run workflow** on the Site health action; outages often fix themselves.\n2. GitHub → this repo → **Settings → Pages**: *Custom domain* must say `malavnaik.com` with a green tick, and **Enforce HTTPS** ticked.\n3. Cloudflare → malavnaik.com → **DNS**: the records pointing to GitHub must still be there. Don't change them yourself; ask Claude with a screenshot.\n4. If only the www address fails: Cloudflare needs a `www` record or a redirect rule. Ask Claude."),
    ("Page title or profile data missing", check_titles,
     "At least one page doesn't show the exact title from identity.json, or lost its hidden \"Person\" profile data (used by Google and AI assistants).",
     "A recent change to a page, `_config.yml`, `_layouts/default.html`, `_includes/schema.html` or `identity/identity.json`.",
     "1. Look at the list below to see which pages.\n2. Open this repo's **Commits** list and find the change made just before the problem started.\n3. Ask Claude: \"Site health says the title or profile data is missing on these pages: <paste the list>. Please fix it.\"\n4. Or undo the last change: see *Roll back a bad change* in MAINTENANCE.md."),
    ("Broken links", check_links,
     "Some links on malavnaik.com lead to a page that no longer exists or doesn't answer.",
     "An outside site moved or deleted a page, a project repo was renamed or made private, or a typo in a new post.",
     "1. Open each broken link below to confirm it's really broken (some sites are briefly down).\n2. If it is: ask Claude \"Fix these broken links on my site: <paste the list>\". It will update or remove them.\n3. If a link to your own GitHub repo fails, check the repo is still **Public**."),
    ("Profile no longer links to malavnaik.com", check_profiles,
     "A profile marked `live` in backlinks/tracker.csv no longer loads or no longer links to malavnaik.com.",
     "You changed the profile, the platform changed its page layout or address, or the account was suspended.",
     "1. Open the profile below while signed in and check the **Website** field still says `https://malavnaik.com`.\n2. Fix it on the platform, or, if you closed that account, change its row in `backlinks/tracker.csv` from `live` to `rejected`.\n3. Click **Run workflow** on the Site health action to re-check."),
    ("CNAME file changed", check_cname,
     "The `CNAME` file, which tells GitHub Pages to serve the site at malavnaik.com, is missing or changed.",
     "Someone edited or deleted it, or GitHub → Settings → Pages had its custom domain changed (GitHub rewrites this file).",
     "1. GitHub → **Settings → Pages** → *Custom domain*: type `malavnaik.com` → **Save**. GitHub recreates the file.\n2. Re-run this check. Don't change Cloudflare settings without asking Claude first."),
    ("Bike sky data is old", check_sky,
     "The live bike data behind the home page sky is more than two hours old, so visitors see the saved snapshot instead.",
     "The Dublin bikes pipeline (malavnaik99/dublin-data-pipeline) stopped running or stopped publishing its small \"latest\" file.",
     "1. Open the pipeline repo → **Actions**: is the latest run red, or missing?\n2. If it failed, ask Claude: \"The bike pipeline failed with this error: <paste it>\".\n3. Nothing on malavnaik.com is broken meanwhile: the sky shows the saved snapshot and says so.\n4. To stop these alerts for good, empty the `url` in `_data/sky_live.json`."),
    ("Employer's client named in the repo", check_client,
     "A file in this repo mentions the company your employer's client is, which your rules forbid anywhere.",
     "New text (a post, a page, notes or code) used the company's name instead of \"a global technology client\".",
     "1. Open each file and line listed below.\n2. Replace the name with **a global technology client**, or ask Claude: \"Remove the client name from these places: <paste the list>\".\n3. If it was in a published page, the fix goes live automatically once it's on `main`."),
]


# ---------- GitHub Issues ----------

def gh(method, path, payload=None):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}{path}", method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", **UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read() or "null")


def open_health_issues():
    found, page = {}, 1
    while True:
        batch = gh("GET", f"/issues?state=open&per_page=100&page={page}")
        for i in batch:
            if "pull_request" not in i and i["title"].startswith("Site health: "):
                found[i["title"]] = i["number"]
        if len(batch) < 100:
            return found
        page += 1


def issue_body(what, cause, fix, problems, run_url):
    shown = "\n".join(f"- {p}" for p in problems[:50]) + (f"\n- …and {len(problems) - 50} more" if len(problems) > 50 else "")
    return (f"**What broke:** {what}\n\n**Likely cause:** {cause}\n\n**How to fix it:**\n{fix}\n\n"
            f"**Details** (checked {datetime.datetime.now(datetime.timezone.utc):%d %b %Y %H:%M} UTC):\n{shown}\n\n"
            f"This issue updates itself while the problem continues and closes itself once the check passes.\n"
            f"Run log: {run_url} · Full guide: {MAINT}")


def main(only=None):
    results = []
    for name, fn, what, cause, fix in CHECKS:
        if only and name != only:
            continue
        try:
            problems = fn()
        except Exception as e:  # a check that crashes counts as a failure, never a silent pass
            problems = [f"The check itself couldn't run: {type(e).__name__}: {e}"]
        if os.environ.get("SITE_HEALTH_FORCE_FAIL") == name:  # used only to test the issue flow
            problems = problems + ["TEST: this failure was forced on purpose to test the alert. Ignore it."]
        results.append((name, what, cause, fix, problems))
        print(f"{'PASS' if not problems else 'FAIL'}  {name}" + "".join(f"\n      - {p}" for p in problems[:20]))
    for note in getattr(check_profiles, "notes", []) + getattr(check_sky, "notes", []):
        print(f"NOTE  {note}")

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write("## Site health\n\n| Check | Result |\n|---|---|\n")
            fh.writelines(f"| {n} | {'✅ passed' if not p else f'❌ {len(p)} problem(s)'} |\n" for n, _, _, _, p in results)

    if os.environ.get("GITHUB_TOKEN") and os.environ.get("GITHUB_REPOSITORY"):
        run_url = f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
        existing = open_health_issues()
        for name, what, cause, fix, problems in results:
            title, number = f"Site health: {name}", existing.get(f"Site health: {name}")
            if problems and number:
                gh("PATCH", f"/issues/{number}", {"body": issue_body(what, cause, fix, problems, run_url)})
                print(f"Updated issue #{number}: {title}")
            elif problems:
                number = gh("POST", "/issues", {"title": title, "body": issue_body(what, cause, fix, problems, run_url)})["number"]
                print(f"Opened issue #{number}: {title}")
            elif number:
                gh("POST", f"/issues/{number}/comments", {"body": f"✅ This check passed again ({run_url}). Closing automatically."})
                gh("PATCH", f"/issues/{number}", {"state": "closed", "state_reason": "completed"})
                print(f"Closed issue #{number}: {title}")
    return 1 if any(p for *_, p in results) else 0


def self_test():
    assert page_title("<html><title>A &amp; B</title></html>") == "A & B"
    assert has_person('<script type="application/ld+json">{"@graph":[{"@type":"Person"}]}</script>')
    assert not has_person('<script type="application/ld+json">{broken</script>')
    assert not is_client_word("meta") and not is_client_word("Metadata") and not is_client_word("Data")
    assert all(not is_client_word(w) for w in ["Google", "Accenture", "Anthropic", "OpenAI", "Airbnb"])
    assert check_cname() == [] and (ROOT / "backlinks/tracker.csv").exists()
    assert any(n == "Bike sky data is old" for n, *_ in CHECKS)
    print("Self-test passed.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif "--only" in sys.argv:  # one check by name, e.g. the hourly bike-sky check
        sys.exit(main(only=sys.argv[sys.argv.index("--only") + 1]))
    elif "--print-pages" in sys.argv:
        print(" ".join(site_pages()))
    else:
        sys.exit(main())
