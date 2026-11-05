"""Before each build: copy identity/identity.json into _data/ (so pages can read it) and stop the deploy if
the site has drifted from it. Run from the repo root: python3 scripts/check_identity.py"""
import json, pathlib, re, shutil, sys

root = pathlib.Path(__file__).resolve().parent.parent
identity = json.loads((root / "identity/identity.json").read_text())
shutil.copy(root / "identity/identity.json", root / "_data/identity.json")

problems = []
config_title = re.search(r"^title: (.+)$", (root / "_config.yml").read_text(), re.M).group(1).strip()
if config_title != identity["title"]:
    problems.append(f'_config.yml title is "{config_title}" but identity.json says "{identity["title"]}".')

home_title = re.search(r'^title: "(.+)"$', (root / "index.md").read_text(), re.M).group(1)
if home_title != identity["title"]:
    problems.append(f'index.md title is "{home_title}" but identity.json says "{identity["title"]}".')

# Old wording that must not come back (old title, private email).
banned = ["AI Automation Engineer", "malavnaikie@gmail.com"]
for f in root.rglob("*"):
    if f.is_dir() or ".git" in f.parts or f.parts[len(root.parts)] in ("docs", "_site", "identity") or f.suffix in (".png", ".jpg", ".pdf", ".xlsx", ".ico", ".webp", ".parquet"):
        continue
    if f.name in ("CLAUDE.md", "check_identity.py"):
        continue
    text = f.read_text(errors="ignore")
    problems += [f"{f.relative_to(root)} still contains \"{b}\"." for b in banned if b in text]

if problems:
    print("The site no longer matches identity/identity.json:\n- " + "\n- ".join(problems))
    sys.exit(1)
print("Identity check passed.")
