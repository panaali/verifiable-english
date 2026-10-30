"""ap-1bd's delta, base against head: every record that changes, and why.

    (cd <checkout> && uv run python <this file> --answers OUT)      # with that checkout's own `ve` and service
    # the base checkout with the head's tests/test_acts_profile.py copied in (the probes' fixtures)
    uv run python docs/act-phrases/ap-1bd/delta.py --compare BASE.json HEAD.json --out evidence/delta.json

`--answers` records every case of `tests/data/route-cases.jsonl` (the merge base's file: ap-1bd adds none) and the
probes below, which only `acts@0` sources reach: typing, a model and the readings route over A1-A3, a joined act on
the readings route, and the UDHR pilot's u076 part document through `ve document check`. `--compare` classifies each
difference: `acts` (an `acts@0` source refused as an unsupported profile at the base, answered at the head) or `d33`
(a joined act on the readings route: the base's profile refusal, the head's D-33). Exit 1 when any other difference
exists, when nothing differs (head against head) or when there are no records.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

CASES = "tests/data/route-cases.jsonl"
BASE_REFUSAL = "UnsupportedProfile: Unsupported profile acts@0"


def probes(service):
    from tests.test_acts_profile import A5, U076, environment, predicate, u076
    from ve.document import check_document
    readings = ["acts@0", "norms@0", "readings@1", "relational-fol@0"]
    joined = environment(readings, p=predicate(["person"], {"role": "plain", "default": "deny", "act": A5,
                                                             "form": "has the right"}))
    del joined["vocabulary"]["predicates"]["heard"]
    model = {"complete": True, "domains": {"person": ["p"], "case": ["c"]}, "constants": {},
             "relations": {"heard": [], "paid": [["p"]], "protected": []}}
    cases = {"check/A1-A3": ("check", {"id": "c", "environment": environment(), "ast": ["top"]}),
             "model/A1-A3": ("model", {"id": "m", "environment": environment(), "model": model}),
             "readings/A1-A3": ("readings-route", {"id": "v", "kind": "readings-validate",
                                                   "environment": environment(readings),
                                                   "document": {"units": [], "reading_sets": []}}),
             "readings/A5": ("readings-route", {"id": "v", "kind": "readings-validate", "environment": joined,
                                                "document": {"units": [], "reading_sets": []}})}
    for name, (mode, case) in cases.items():
        yield name, service.run(mode, [case])[0]
    path = u076(Path(tempfile.mkdtemp()), ["acts@0", "documents@1", "norm-defaults@0", "norms@0", "relational-fol@0"])
    try:
        yield "document/u076", check_document(path)["coverage"]["bytes_by_status"]
    except Exception as exc:  # the record is what a caller sees
        yield "document/u076", {"refused": str(exc), "bytes": len(U076.encode())}


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


def refusal(answer) -> str | None:
    return answer.get("error", answer.get("refused")) if isinstance(answer, dict) else None


def why(key: str, base, head) -> str | None:
    if not key.startswith("probe:") or refusal(base) != BASE_REFUSAL:
        return None
    if key == "probe:readings/A5":
        return "d33" if refusal(head) == ("UnsupportedProfile: acts@0 on the readings route admits single acts only; "
                                          "the act of p joins acts") else None
    return "acts" if refusal(head) is None else None


def compare(base_file: Path, head_file: Path) -> dict:
    base, head = (json.loads(f.read_text()) for f in (base_file, head_file))
    if [r["key"] for r in base] != [r["key"] for r in head]:
        raise SystemExit("the two recordings answer different cases")
    changed = [{"key": b["key"], "why": why(b["key"], b["answer"], h["answer"]), "base": b["answer"],
                "head": h["answer"]} for b, h in zip(base, head) if b["answer"] != h["answer"]]
    counts: dict = {}
    for c in changed:
        counts[str(c["why"])] = counts.get(str(c["why"]), 0) + 1
    return {"records": len(base), "identical": len(base) - len(changed), "changed": counts, "records_changed": changed}


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
