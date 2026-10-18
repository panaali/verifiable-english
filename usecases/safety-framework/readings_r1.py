"""fsf-r1: the D1 reading sets with content under `readings@1`, each checked by VE alone and in D1.

    python usecases/safety-framework/readings_r1.py [--source PATH] [--check]

On 2026-10-01 every reading set of D1 had pending content (PLAN section 12, item 13: O2), so VE's own readings
query was UNKNOWN and the ALL, SOME and NONE answers came from the harness's per-choice documents. Content-bearing
sets have since merged on the soft chain (composition S1 and S2a; readings-defaults; the rd-9 soft chain).
`build_document.py` now gives every set whose readings are each one rule of `rules.d1.ve` that rule as content.

This writes `readings.json` here: for every set, either the reading that keeps it
pending (no rule, or several), or VE's answer on its part document (the set's source unit alone, its open terms and
the set: L70, no whole-document readings run on a large document) from `ve document check`, with the English VE
shows; and VE's answer on the whole D1 document. A unit with an open set stays OPEN: the text has two readings, and
a translation of someone else's text never picks one (PLAN 3.1). `--check` fails if the file would change.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402

OUT = HERE / "readings.json"


def set_units():
    """{set id: (unit id, open terms)} from the D1 unit specifications."""
    return {spec["reading_set"]: (uid, spec["meaning"]["open"] if type(spec["meaning"]) is dict else [])
            for _, uid, spec in B.UNITS if "reading_set" in spec}


def part_document(source, set_id):
    """The part document of one content-bearing set: its unit's bytes, its open terms and the set."""
    from ve.softnorms import SoftEnvironment
    uid, terms = set_units()[set_id]
    start, stop = dict(zip((u for _, u, _ in B.UNITS), B.spans(source)))[uid]
    raw = B.environment()
    unit = {"id": uid, "span": [0, stop - start], "kind": "norm",
            "meaning": {"open": terms} if terms else "specified", "support": "testimony", "content": None}
    [reading_set] = B.record_situations(raw, [unit], [B.content_set(SoftEnvironment(raw), set_id, uid,
                                                                    [0, stop - start], source[start:stop])])
    return source[start:stop], {"format": "ve-document@1", "environment": raw, "units": [unit],
                                "open_terms": B.open_term_declarations(terms), "reading_sets": [reading_set]}


def answer(path, whole=False):
    """VE's answer on one document (`ve document check`), or its refusal."""
    from ve.document import check_document, load_document
    from ve.errors import VEError
    try:
        units = load_document(path)["units"]
        report = check_document(path)
    except VEError as exc:
        return {"refused": str(exc)}
    readings = report.get("readings") or {}
    out = {"premises": report["premises"]["status"], "route": readings.get("route"),
           "conflict": (readings.get("conflict") or {}).get("status"), "findings": readings.get("findings"),
           "residual": {k: v for k, v in report["coverage"]["residual"].items()
                        if k in ("separations", "readings_findings", "pending_candidates", "unresolved_reading_sets")}}
    if not whole:
        out.update({"status": units[0]["status"], "english": readings.get("english"),
                    "pairs": [{"readings": p["readings"], "wording": p["wording"],
                               "text": p["text"]} for s in readings.get("sets", []) for p in s.get("pairs", [])]})
    return out


def write(path, text, front):
    path.write_bytes(b"---\n" + json.dumps(front, indent=1, ensure_ascii=False).encode() + b"\n---\n" + text)


def run(source, scratch):
    sets = {}
    for set_id, (harness_set, choices) in B.READINGS.items():
        uid = set_units()[set_id][0]
        if not B.content_bearing(set_id):
            # A reading with no rule, or with several, has no single content: W2's UNKNOWN, as on Oct 1.
            sets[set_id] = {"unit": uid, "harness_set": harness_set, "content": False,
                            "pending": {c: rules for c, rules in choices.items()
                                        if len(rules) != 1 or " or " in rules[0]}}
            continue
        text, front = part_document(source, set_id)
        write(scratch / f"{set_id}.ve.md", text, front)
        sets[set_id] = {"unit": uid, "harness_set": harness_set, "content": True,
                        "rules": {c: rules[0] for c, rules in choices.items()},
                        **answer(scratch / f"{set_id}.ve.md")}
    document, _ = B.build(source)
    (scratch / "fsf.d1.ve.md").write_bytes(document)
    return {"sets": sets, "whole_document": answer(scratch / "fsf.d1.ve.md", whole=True)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=B.DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    with tempfile.TemporaryDirectory() as scratch:
        results = run(args.source.read_bytes(), Path(scratch))
    text = json.dumps(results, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if args.check:
        if OUT.read_text() != text:
            raise SystemExit("readings.json is out of date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
