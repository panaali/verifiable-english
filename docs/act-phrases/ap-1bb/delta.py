"""ap-1bb's delta, base against head: every record that changes, and why.

    (cd <checkout> && uv run python <this file> --answers OUT)      # with that checkout's own `ve` and service
    uv run python docs/act-phrases/ap-1bb/delta.py --compare BASE.json HEAD.json --out evidence/delta.json

`--answers` records, with the checkout it runs in (its schemas read its own service's rows), every case of this
item's `tests/data/route-cases.jsonl` (the merge base's file: ap-1bb adds none) and the probes below, which load
`acts@0` environments through Python (`Environment`, `EnglishVocabulary`). `--compare` pairs the records and
classifies each difference: `wordings` (a `norms-elaborate` row that differs only by its added `wordings`, empty
for an environment without a plain act), `loads` (a probe that was CheckerUnavailable and now answers) or
`display` (a probe's wording). Exit 1 when any other difference exists, when nothing differs (head against head)
or when there are no records.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CASES = "tests/data/route-cases.jsonl"
A19 = "{0} comply with the operator’s instructions in {1}"


def probes():
    from tests.test_acts_profile import environment, predicate
    from ve.english import EnglishVocabulary
    from ve.environment import Environment
    curly = environment(p=predicate(["person", "case"], {"role": "permission", "default": "allow", "act": A19}))
    for name, data in [("load/A1-A3", environment()), ("load/A19", curly)]:
        try:
            env = Environment(data)
            words = EnglishVocabulary(env).predicates
            yield name, {"environment_id": env.environment_id,
                         "wordings": {p: words[p] for p in ("heard", "paid", "protected")}}
        except Exception as exc:  # the record is what a caller sees
            yield name, {"refused": f"{type(exc).__name__}: {exc}"}


def record(out: Path) -> None:
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
    finally:
        service.close()
    records += [{"key": f"probe:{name}", "answer": answer} for name, answer in probes()]
    out.write_text(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=0) + "\n")


def why(key: str, base, head) -> str | None:
    if ":norms-elaborate" in key and isinstance(head, dict) and "wordings" in head and "wordings" not in base \
            and {k: v for k, v in head.items() if k != "wordings"} == base:
        return "wordings"
    if key.startswith("probe:") and "refused" in base and "refused" not in head:
        return "loads"
    if key.startswith("probe:") and "refused" not in base and base["environment_id"] == head.get("environment_id"):
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
