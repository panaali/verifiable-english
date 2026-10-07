"""Frozen-base A/B for the 1,000 generated reports documents of fixture χ."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
FIELDS = ("environment_reports_id", "keys", "premises", "open_terms", "bridge_formulas",
          "content_ids", "envelope", "warnings")


def generate(path: Path) -> None:
    from tests.test_reports_lean import E0, U, assess, ast, doc, neg, report
    rng = random.Random(20260928)
    leaves = [ast(U("safe", "service")), ast(U("helpful", "claude")),
              ast(["not", U("safe", "service")])]

    def content(depth: int):
        node = deepcopy(rng.choice(leaves))
        for _ in range(depth):
            if rng.randrange(5) == 0:
                node = assess(rng.choice(["may", "probably"]), node)
            else:
                act = rng.choice(["says", "believes", "wants", "intends"])
                holder = rng.choice(["anthropic", "the_team", "the_article"])
                node = report(holder, act, rng.choice(["c1", "c2", "c3"]), node,
                              literal=rng.choice([None, None, "exact words"]))
        return node

    cases = []
    for _ in range(1000):
        nodes = [content(rng.randint(1, 3)) for _ in range(rng.randint(1, 3))]
        nodes = [neg(n) if rng.randrange(4) == 0 else n for n in nodes]
        cases.append(doc(*nodes))
    path.write_text(json.dumps({"environment": E0(), "cases": cases}, ensure_ascii=False) + "\n")


def record(root: Path, cases_path: Path, out: Path) -> None:
    sys.path.insert(0, str(root))
    from ve.environment import Environment
    from ve.errors import VEError
    from ve.reports import ReportsDocument

    corpus = json.loads(cases_path.read_text())
    environment = Environment(corpus["environment"])
    with out.open("w") as target:
        for index, d in enumerate(corpus["cases"]):
            try:
                doc = ReportsDocument(environment, d.get("contexts", []), d.get("assessments", []), d["units"],
                                      bridges=d.get("bridges", []), scoped=d.get("scoped", []),
                                      open_terms=d.get("open_terms", []))
                result = {"elaborated": {key: doc.elaborated()[key] for key in FIELDS},
                          "document_id": doc.document_id,
                          "unit_statuses": [doc.unit_status(unit) for unit in d["units"]],
                          "residual_lines": doc.residual_lines(),
                          "meaning_ids": [doc.meaning_id(unit["content"]) for unit in d["units"]]}
            except VEError as exc:
                result = {"error": str(exc), "class": type(exc).__name__}
            target.write(json.dumps({"case": index, "result": result}, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path)
    parser.add_argument("--head", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--record-root", type=Path)
    parser.add_argument("--cases", type=Path)
    args = parser.parse_args()
    if args.record_root:
        record(args.record_root.resolve(), args.cases, args.out)
        return 0
    if not args.base or not args.out:
        parser.error("--base and --out are required")
    cases = args.out.with_suffix(".cases.json")
    generate(cases)
    paths = []
    for label, root in (("base", args.base), ("head", args.head)):
        output = args.out.with_name(args.out.stem + f".{label}.jsonl")
        command = [sys.executable, str(Path(__file__).resolve()), "--record-root", str(root.resolve()),
                   "--cases", str(cases), "--out", str(output)]
        env = dict(os.environ, PYTHONPATH=str(root.resolve()))
        subprocess.run(command, cwd=root, env=env, check=True)
        paths.append(output)
    old, new = [[json.loads(line) for line in path.read_text().splitlines()] for path in paths]
    changed = [i for i, (a, b) in enumerate(zip(old, new, strict=True)) if a != b]
    summary = {"cases": len(old), "same": len(old) - len(changed), "changed": changed}
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(summary)
    return 1 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
