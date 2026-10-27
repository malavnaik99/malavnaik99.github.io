"""Content check: proves a restyle changed no words, numbers or links.

Snapshot every page in the sitemap (text, then link URLs) from a built site folder or the live site:
    python3 docs/content-check.py snapshot _site docs/content-before
    python3 docs/content-check.py snapshot https://malavnaik.com docs/content-after
Compare two snapshots (prints added, removed and moved lines per page):
    python3 docs/content-check.py diff docs/content-before docs/content-after

Text includes hidden and aria-hidden elements (tab panels, answers), the page title, the meta
description, and alt / placeholder / aria-label / title attributes. Script, style and noscript are skipped.
"""
import os, re, sys, urllib.request
from collections import Counter
from html.parser import HTMLParser

SKIP = {"script", "style", "noscript", "template"}
BLOCK = {"address", "article", "aside", "blockquote", "br", "button", "caption", "dd", "details", "div", "dl",
         "dt", "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "header", "hr",
         "label", "li", "main", "nav", "ol", "option", "p", "pre", "section", "summary", "table", "td", "th",
         "title", "tr", "ul"}
ATTRS = ("alt", "placeholder", "aria-label", "title")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.links, self.buf, self.skip = [], [], [], 0

    def flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if text:
            self.lines.append(text)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in SKIP:
            self.skip += 1
        if tag in BLOCK:
            self.flush()
        if tag == "meta" and a.get("name") == "description":
            self.lines.append("[meta description] " + (a.get("content") or ""))
        if tag == "link" and a.get("rel") == "canonical":
            self.links.append("[canonical] " + (a.get("href") or ""))
        if tag in ("a", "area") and a.get("href") is not None:
            self.links.append(a["href"])
        for k in ATTRS:
            if a.get(k) and not self.skip:
                self.flush()
                self.lines.append("[%s] %s" % (k, re.sub(r"\s+", " ", a[k]).strip()))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        if tag in BLOCK:
            self.flush()

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def read(src, path):
    if src.startswith("http"):
        with urllib.request.urlopen(src.rstrip("/") + path, timeout=30) as r:
            return r.read().decode("utf-8")
    local = os.path.join(src, path.lstrip("/"))
    if path.endswith("/"):
        local = os.path.join(local, "index.html")
    with open(local, encoding="utf-8") as f:
        return f.read()


def snapshot(src, out):
    locs = re.findall(r"<loc>([^<]+)</loc>", read(src, "/sitemap.xml"))
    paths = [re.sub(r"^https?://[^/]+", "", u) for u in locs]
    paths = [p for p in paths if p.endswith("/") or p.endswith(".html")] + ["/404.html"]
    for p in paths:
        page = Page()
        page.feed(read(src, p))
        page.flush()
        name = "index" if p == "/" else p.strip("/").removesuffix(".html")
        dest = os.path.join(out, name + ".txt")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write("== TEXT ==\n" + "\n".join(page.lines) + "\n== LINKS ==\n" + "\n".join(page.links) + "\n")
    print("%d pages saved to %s" % (len(paths), out))


def diff(before, after):
    files = sorted({os.path.relpath(os.path.join(d, f), top) for top in (before, after)
                    for d, _, fs in os.walk(top) for f in fs if f.endswith(".txt")})
    clean = True
    for rel in files:
        a = open(os.path.join(before, rel), encoding="utf-8").read().splitlines() if os.path.exists(os.path.join(before, rel)) else []
        b = open(os.path.join(after, rel), encoding="utf-8").read().splitlines() if os.path.exists(os.path.join(after, rel)) else []
        if a == b:
            continue
        clean = False
        print("\n### " + rel)
        added, removed = Counter(b) - Counter(a), Counter(a) - Counter(b)
        for line, n in removed.items():
            print("  - removed%s: %s" % (" x%d" % n if n > 1 else "", line))
        for line, n in added.items():
            print("  + added%s: %s" % (" x%d" % n if n > 1 else "", line))
        if not added and not removed:
            print("  ~ same lines, different order")
    print("\nNo differences." if clean else "")
    return clean


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "snapshot":
        snapshot(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "diff":
        sys.exit(0 if diff(sys.argv[2], sys.argv[3]) else 1)
    else:
        sys.exit(__doc__)
