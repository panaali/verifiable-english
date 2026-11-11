"""cmp-s3-cfr-1b DELTA evidence: what `clauses-elaborate` answers without the head's two charges (`lineObjects`, `deepLine`).

Run on a build of the item's tree with the two checks in `elaborateCase` (lean/VE/RightClauses/Run.lean) commented out,
which is main's mode on these documents:
    uv run python docs/composition/cmp-s3-cfr-1b/main_answers_probe.py > docs/composition/cmp-s3-cfr-1b/main-answers.json
The saved output is evidence for DELTA rows 1 and 2; no test reads it live (D4).
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tests.test_right_clauses import CHARGED, NORM, RELATION, document, environment  # noqa: E402
from ve.backends.lean_service import LeanService  # noqa: E402


def conjuncts(n, relation=None):
    doc = document(clauses=[{**CHARGED, "role": "scope", "span": [i, i + 1]} for i in range(n)], relation=relation)
    doc[0]["span"] = [0, n + 1]
    return environment(), doc


def copies(k, bad=False):
    line = document()[0]["right"]["lines"][0]
    lines = [line] * k
    if bad:
        lines[0] = {**line, "relation": {**RELATION, "predicate": "nope"}}
    return environment(), [{"right": {**document()[0]["right"], "lines": lines}}]


def distinct(k):
    env = environment()
    regulated = env["vocabulary"]["predicates"]["public_service_access_required"]
    lines = []
    for i in range(k):
        env["vocabulary"]["predicates"][f"p{i}_required"] = {**regulated, "regulated": {
            **regulated["regulated"], "act": "{0} give {1} access to item" + str(i)}}
        lines.append({**document()[0]["right"]["lines"][0], "norm": {**NORM, "name": f"a{i}", "predicate": f"p{i}_required"}})
    return env, [{"right": {"name": "r21", "holder": "person", "lines": lines}, "span": [0, 100]}]


CASES = {**{f"conjuncts-{n}": conjuncts(n) for n in (64, 65, 100, 40000)}, "conjuncts-63-relation": conjuncts(63, RELATION),
         "copies-257": copies(257), "copies-257-first-bad": copies(257, True), "distinct-256": distinct(256),
         "distinct-257": distinct(257)}


def main():
    run = LeanService(allow_unlisted_build=True)
    out = {"head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip(),
           "build": run.build, "answers": {}}
    for name, (env, doc) in CASES.items():
        _, response = run.exchange("clauses-elaborate", json.dumps([{"id": name, "environment": env, "document": doc}]),
                                   1, timeout=1200)
        row = response["results"][0]
        out["answers"][name] = {"code": row.get("code"), "error": row["result"].get("error"),
                                "status": row["result"].get("status")}
    run.close()
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
