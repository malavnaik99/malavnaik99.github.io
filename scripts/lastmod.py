"""Writes _data/lastmod.json: {source file path: date of its last commit}, for the sitemap's <lastmod> dates.

Runs in the deploy workflow before the Jekyll build (needs the full git history: checkout with fetch-depth: 0).
The output is a build file (gitignored), like _data/identity.json.
  python3 scripts/lastmod.py
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Newest commit first; the first date seen for a file is its last change.
log = subprocess.run(["git", "log", "--format=@%cs", "--name-only", "--no-renames"],
                     cwd=ROOT, check=True, capture_output=True, text=True).stdout
dates, current = {}, None
for line in log.splitlines():
    if line.startswith("@"):
        current = line[1:]
    elif line and line not in dates:
        dates[line] = current

# A shallow clone would give every page the same date: fail loudly instead of publishing wrong dates.
assert "index.md" in dates and len(set(dates.values())) > 1, \
    "Every file has the same date: the checkout has no history. Use fetch-depth: 0."
(ROOT / "_data/lastmod.json").write_text(json.dumps(dates, indent=0, sort_keys=True))
print(f"Wrote last-change dates for {len(dates)} files.")
