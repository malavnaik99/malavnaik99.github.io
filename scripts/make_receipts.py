"""Copies the "Receipts" table in docs/METRIC_SOURCES.md into _data/receipts.json, which the home page shows
when a visitor opens one of the four numbers in the proof strip (where each number came from: dataset, file, test).

    python3 scripts/make_receipts.py             # write _data/receipts.json
    python3 scripts/make_receipts.py --check     # fail if it differs from METRIC_SOURCES.md (run by the deploy)
    python3 scripts/make_receipts.py --self-test # test the table reader
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC, OUT = ROOT / "docs/METRIC_SOURCES.md", ROOT / "_data/receipts.json"
KEYS = ("pipeline", "tests", "rocauc", "dsa")  # the four proof-strip numbers, in page order
COLS = ("key", "shown", "dataset", "file", "test")


def read(md):
    """Rows of the table under '## Receipts', as {key: {shown, dataset, file, test}}."""
    sec = md.split("\n## Receipts", 1)[1].split("\n## ", 1)[0]
    rows = [l for l in sec.splitlines() if l.startswith("|") and not l.startswith("|---")][1:]  # skip the header row
    out = {}
    for l in rows:
        cells = [c.strip() for c in l.strip().strip("|").split(" | ")]
        if len(cells) != len(COLS):
            raise ValueError(f"a Receipts row has {len(cells)} cells instead of {len(COLS)} (no '|' inside a cell): {l[:60]}")
        out[cells[0]] = dict(zip(COLS[1:], cells[1:]))
    missing = [k for k in KEYS if k not in out]
    if missing:
        raise ValueError(f"Receipts table is missing: {', '.join(missing)}")
    return {k: out[k] for k in KEYS}


def self_test():
    md = "x\n## Receipts (t)\n\n| Key | Shown | Dataset | File | Test |\n|---|---|---|---|---|\n" + "".join(
        f"| {k} | n | d [a](u) | `f` | t |\n" for k in KEYS) + "\n## Next\n| a | b |\n"
    r = read(md)
    assert list(r) == list(KEYS) and r["dsa"]["dataset"] == "d [a](u)" and r["tests"]["file"] == "`f`"
    try:
        read(md.replace("| t |\n", "| t | extra |\n", 1)); assert False, "a row with too many cells must fail"
    except ValueError:
        pass
    read(DOC.read_text())  # the real table parses
    print("Self-test passed.")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test(); sys.exit()
    new = json.dumps(read(DOC.read_text()), indent=1, ensure_ascii=False) + "\n"
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != new:
            sys.exit("The receipt cards (_data/receipts.json) don't match docs/METRIC_SOURCES.md. Run: python3 scripts/make_receipts.py")
        print("Receipts match METRIC_SOURCES.md.")
    else:
        OUT.write_text(new)
        print("wrote", OUT.relative_to(ROOT))
