"""Writes _data/pipeline.json: how many automatic data tests the Dublin bikes pipeline runs, read from its public
run log, so every "N automatic data tests" on the site matches the pipeline without hand edits.

Runs in the deploy workflow before the Jekyll build. If the run log can't be read, it keeps the committed
_data/pipeline.json (the last known count) and only warns, so a Hugging Face outage never blocks a deploy.
The weekly site health check opens an issue if the run log stays unreadable or the live site shows another number.

    python3 scripts/pipeline_tests.py              # update _data/pipeline.json
    python3 scripts/pipeline_tests.py --self-test  # test the reader offline
"""
import json, pathlib, sys, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "_data/pipeline.json"
RUN_LOG = "https://huggingface.co/datasets/Malavnaik/dublin-bikes-weather-marts/resolve/main/run_log.json"


def read(body):
    """The run log's test count, checked to be a sensible whole number; ValueError otherwise."""
    log = json.loads(body)
    n, run_at = log.get("tests_total"), log.get("run_at")
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 500:
        raise ValueError(f"tests_total should be a whole number from 1 to 500, got {n!r}")
    return {"tests_total": n, "run_at": run_at}


def fetch(url=RUN_LOG):
    req = urllib.request.Request(url, headers={"User-Agent": "malavnaik.com deploy (github.com/malavnaik99)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return read(r.read().decode("utf-8"))


def self_test():
    assert read('{"tests_total": 15, "run_at": "2026-11-25T14:20:56+00:00"}') == {"tests_total": 15, "run_at": "2026-11-25T14:20:56+00:00"}
    for bad in ('{"tests_total": 0}', '{"tests_total": "15"}', '{"tests_total": true}', '{}', 'not json'):
        try:
            read(bad)
            raise AssertionError(f"should reject {bad}")
        except ValueError:  # json.JSONDecodeError is a ValueError too
            pass
    assert read(OUT.read_text())["tests_total"] >= 1, "the committed _data/pipeline.json must be valid"
    print("Self-test passed.")


def main():
    try:
        data = fetch()
    except Exception as e:
        kept = json.loads(OUT.read_text())["tests_total"]
        print(f"::warning::Couldn't read the pipeline's run log ({type(e).__name__}: {e}). Keeping the last known count: {kept}.")
        return
    OUT.write_text(json.dumps(data, indent=1) + "\n")
    print(f"Pipeline runs {data['tests_total']} data tests (run log of {data['run_at']}).")


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else main()
