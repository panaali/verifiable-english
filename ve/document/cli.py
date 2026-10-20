"""`ve document`: the command line (moved from `ve/document.py`, AR-16a)."""
from __future__ import annotations

import json
from pathlib import Path

from ..ast import decimal_value
from ..errors import VEError
from ..readings import active_reading_sets, check_readings
from .containers import _content_bearing
from .load import load_document
from .report import _checking_environment, _fixed_premises, check_document, coverage
from .render import render_document


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="ve document")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "render", "coverage", "readings"):
        sub.add_parser(name).add_argument("path")
    sub.choices["readings"].add_argument("--conclusion", help="formula AST JSON file to classify")
    sub.choices["readings"].add_argument("--narrowing", help="apply a recorded narrowing by id")
    sub.choices["readings"].add_argument("--under", action="append", metavar="SET:INDEX",
                                         help="a named reading of a content-bearing set (composition-s2.md 4.5)")
    sub.choices["readings"].add_argument("--sentence", metavar="UNIT",
                                         help="the sentence checked by itself the conclusion is about "
                                              "(readings-defaults 4.5)")
    args = parser.parse_args(argv)
    if args.command == "render":
        print(render_document(args.path), end="")
        return 0
    if args.command == "check":
        data = check_document(args.path)
    else:
        doc = load_document(args.path)
        if args.command == "coverage":
            data = coverage(doc)
        elif args.under and not args.conclusion:
            raise VEError("--under requires --conclusion")
        elif args.sentence and not args.conclusion:
            raise VEError("--sentence requires --conclusion")
        elif args.conclusion:
            conclusion = json.loads(Path(args.conclusion).read_text())
            if _content_bearing(doc):
                # composition-s2.md 4.5 and 4.6: ALL, SOME or NONE across the readings of a content-bearing
                # document. Every narrowing in force is already a premise there (1.2); `--narrowing` is W2's.
                if args.narrowing:
                    raise VEError("--narrowing applies to W2's route; on the superposed and enumerated routes "
                                  "every narrowing in force is a premise")
                from ..readings_verdicts import context
                from ..readings_s2_wording import query_english
                assumed = None
                if args.under:
                    assumed = []
                    for item in args.under:
                        set_id, _, index = item.rpartition(":")
                        if not set_id or not index.isdigit():
                            raise VEError("--under takes SET:INDEX")
                        assumed.append((set_id, decimal_value(index)))
                if doc.get("readings_components") is not None:
                    # readings-defaults 4.5 (RD-4b): the query is typed in one sentence checked by itself, Lean's.
                    from ..readings_components import query as components_query
                    data = components_query(doc, conclusion, assumed=assumed, sentence=args.sentence)
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    return 0
                if args.sentence:
                    raise VEError("--sentence names a sentence checked by itself; this document has none")
                data = context(doc).entailment(conclusion, assumed=assumed)
                data["english"] = query_english(doc, conclusion, data)
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return 0
            if args.under:
                raise VEError("--under names readings of a content-bearing set (composition-s2.md 4.5)")
            if args.sentence:
                raise VEError("--sentence names a sentence checked by itself; this document has none")
            active = active_reading_sets(doc["meta"].get("reading_sets", []))
            sets = [{**r, "readings": [{**c, "original_index": i}
                                      for i, c in enumerate(r["readings"])]} for r in active]
            joint = doc.get("discourse", {}).get("joint")
            if args.narrowing:
                matching = [n for n in doc["meta"].get("narrowings", []) if n["id"] == args.narrowing]
                if len(matching) != 1:
                    raise VEError("unknown narrowing")
                narrowing = matching[0]
                matching_sets = [r for r in sets if (r["id"], r["version"]) ==
                                 (narrowing["set"], narrowing["version"])]
                if not matching_sets:
                    raise VEError("narrowing does not target an active reading set")
                rs = matching_sets[0]
                # Lean's joint vectors enumerate open sets only. The signed
                # singleton of an authored set is in every choice implicitly.
                if (joint is not None and joint["status"] == "complete"
                        and rs["status"] == "open"):
                    kept = {i for i, candidate in enumerate(rs["readings"])
                            if candidate["id"] in narrowing["keeps"]}
                    key = f"{rs['id']}@{rs['version']}"
                    joint = {**joint, "choices": [c for c in joint["choices"]
                                                   if c.get(key) in kept]}
                    if not joint["choices"]:
                        raise VEError(f"InvalidCompatibility: narrowing {narrowing['id']}")
                    joint["count"] = len(joint["choices"])
                elif joint is None:
                    sets = [{**r, "readings": [c for c in r["readings"] if c["id"] in narrowing["keeps"]]}
                            if (r["id"], r["version"]) == (narrowing["set"], narrowing["version"]) else r
                            for r in sets]
            data = check_readings(_checking_environment(doc), sets, conclusion,
                                  fixed=_fixed_premises(doc, sets),
                                  joint_choices=joint,
                                  couplings=doc["meta"].get("couplings", []))
            if args.narrowing:
                data["narrowing"] = f"narrowing:{args.narrowing}"
        else:
            if args.narrowing:
                raise VEError("--narrowing requires --conclusion")
            data = doc["reading_plan"]
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
