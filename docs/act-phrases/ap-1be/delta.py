"""ap-1be's delta, base against head: every record that changes, and why.

    (cd <checkout> && uv run python <this file> --answers OUT)      # with that checkout's own `ve` and service
    uv run python docs/act-phrases/ap-1be/delta.py --compare BASE.json HEAD.json --out evidence/delta.json

`--answers` records, with the checkout it runs in (its schemas read its own service's rows), every case of
`tests/data/route-cases.jsonl` (the merge base's file: ap-1be adds none) and the probes below: the norm-defaults
route's `norm-defaults-elaborate` row over A1-A3's environment under `norm-defaults@0`, that environment's English
display, and the same display without `norm-defaults@0` (a control). `--compare` pairs the records and classifies
each difference: `wordings` (a `norm-defaults-elaborate` row that differs only by its added `wordings`) or `display`
(a probe's wording under `norm-defaults@0`). Exit 1 when any other difference exists, when nothing differs (head
against head) or when there are no records.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

CASES = "tests/data/route-cases.jsonl"
ND_PROFILES = ["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"]


def probes(service):
    from tests.test_acts_profile import environment
    from ve.english import EnglishVocabulary
    from ve.environment import Environment

    def answer(ask):
        try:
            return ask()
        except Exception as exc:  # the record is what a caller sees
            return {"refused": f"{type(exc).__name__}: {exc}"}

    def display(data):
        words = EnglishVocabulary(Environment(data)).predicates
        return {p: words[p] for p in ("heard", "paid", "protected")}

    nd = environment(ND_PROFILES)
    case = {"id": "norm-defaults-elaborate", "kind": "norm-defaults-elaborate", "environment": nd, "norms": []}
    yield "nd-elaborate/A1-A3", answer(lambda: service.run("norm-defaults", [case])[0])
    yield "nd-display/A1-A3", answer(lambda: display(nd))
    yield "norms-display/A1-A3", answer(lambda: display(environment()))


def record(out: Path) -> None:
    sys.path.insert(0, os.getcwd())  # this checkout's `ve` and `tests`
    from ve.backends.lean_service import LeanService
    from ve.errors import VEError
    rows = [json.loads(line) for line in Path(CASES).read_text().splitlines() if line.strip()]
    service = LeanService(Path("lean/.lake/build/bin/ve_service"), allow_unlisted_build=True)
    records = []
    try:
        for i, (mode, case) in enumerate(rows):
            try:
                [result] = service.run(mode, [case])
            except VEError as refused:
                result = {"refused": refused.message}
            records.append({"key": f"{i}:{mode}:{case.get('kind', '')}", "answer": result})
        records += [{"key": f"probe:{name}", "answer": answer} for name, answer in probes(service)]
    finally:
        service.close()
    out.write_text(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=0) + "\n")


def why(key: str, base, head) -> str | None:
    if (":norm-defaults-elaborate" in key or key == "probe:nd-elaborate/A1-A3") and isinstance(head, dict) \
            and isinstance(base, dict) and "wordings" in head and "wordings" not in base \
            and {k: v for k, v in head.items() if k != "wordings"} == base:
        return "wordings"
    if key == "probe:nd-display/A1-A3" and "refused" not in base and "refused" not in head:
        return "display"
    return None


def compare(base_file: Path, head_file: Path) -> dict:
    base, head = (json.loads(f.read_text()) for f in (base_file, head_file))
    if [r["key"] for r in base] != [r["key"] for r in head]:
        raise SystemExit("the two recordings answer different cases")
    changed = [{"key": b["key"], "why": why(b["key"], b["answer"], h["answer"]),
                "base": b["answer"], "head": h["answer"]}
               for b, h in zip(base, head) if b["answer"] != h["answer"]]
    counts: dict = {}
    for c in changed:
        counts[str(c["why"])] = counts.get(str(c["why"]), 0) + 1
    shown = [c if c["why"] != "wordings" else {**c, "base": "(the head's row without `wordings`)",
                                                 "head": {"wordings": c["head"]["wordings"]}} for c in changed]
    return {"records": len(base), "identical": len(base) - len(changed), "changed": counts, "records_changed": shown}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--answers", type=Path)
    parser.add_argument("--compare", nargs=2, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.answers:
        record(args.answers)
        return 0
    report = compare(*args.compare)
    if args.out:
        args.out.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("records", "identical", "changed")}))
    return 0 if report["records"] and report["records_changed"] and "None" not in report["changed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
