"""The fidmech command line: textcheck (the text-check report), furniture (every furniture match) and boundaries.

  uv run python -m tools.fidmech textcheck --doc anthropic-rsp [--checks L1,L1a,L2,L3,L4,D | all] [--span sentence]
                                           [--json OUT]
  uv run python -m tools.fidmech furniture --doc anthropic-rsp
  uv run python -m tools.fidmech boundaries --doc anthropic-rsp [--check | --write]

--doc is a use-case name under usecases/ or a case directory; --source overrides the case's pinned source path.
Exit 0 on a report, 1 when `boundaries --check` finds the frozen pairs stale, 2 on an input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.fidmech import segment as S
from tools.fidmech import sentchecks as C

CHECKS = C.CHECKS


def _case(args):
    case = S.accounting.case_dir(args.doc)
    if not case.is_dir():
        raise S.BoundariesError(f"no case directory {args.doc!r}")
    source = Path(args.source) if args.source else S.doc_source(case)
    return case, source.read_bytes(), case / "fidmech" / "boundaries.json"


def textcheck(args) -> int:
    args.checks = [c for arg in args.checks for c in arg.split(",") if c]
    if args.checks == ["all"]:
        args.checks = list(CHECKS)
    unknown = set(args.checks) - set(CHECKS)
    if unknown:
        raise S.BoundariesError(f"unknown checks {sorted(unknown)} (the checks are {', '.join(CHECKS)}, or all)")
    case, data, bpath = _case(args)
    result = C.report(case, data, bpath, args.checks)
    print(f"{result['document']}: {result['blocks']} blocks, {result['quotes']['checked']} quotes checked, "
          f"{result['quotes']['note']} note quotes, {result['quotes']['empty']} empty (info, outside the headline)")
    line = lambda counts: ", ".join(f"{c} {n}" for c, n in counts.items())  # noqa: E731
    print(f"{'+'.join(result['checks'])} hits: " + line(result["counts"]))
    for check, row in result.get("info", {}).items():
        print(f"  {check}: " + json.dumps({k: v for k, v in row.items() if k != "per_block"}, ensure_ascii=False))
    for lever, row in result["levers"].items():
        if "error" in row:
            print(f"  {lever} off: not segmentable ({row['error']})")
            continue
        print(f"  {lever} off: " + line(row["counts"])
              + f" (the lever clears {len(row['cleared'])} hits and adds {len(row['added'])})")
    print(f"unpaired digit runs left as text: {result['unpaired_digit_runs']}")
    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def furniture(args) -> int:
    _, data, bpath = _case(args)
    source, b = S.Source(data), S.load_boundaries(bpath)
    for k, page, s, e in S.furniture_matches(source, b.furniture):
        print(f"{k}\tpage {page + 1}\tbyte {source.byte[s]}\t{source.text[s:e]!r}")
    return 0


def boundaries(args) -> int:
    _, data, bpath = _case(args)
    source, b = S.Source(data), S.load_boundaries(bpath)
    hand = [f for f in b.footnotes if f["by"] == "hand"]
    pairs, unresolved = S.propose(source, b.furniture, [f["body"][0] for f in hand])
    rejected = {u["at"] for u in b.unpaired}
    decided = {f["body"][0] for f in hand} | {f["marker_at"] for f in hand} | rejected
    open_ = [u for u in unresolved if u["at"] not in decided]
    pairs = [f for f in pairs if f["body"][0] not in rejected]  # a proposal the builder rejected, with a reason
    frozen = [f for f in b.footnotes if f["by"] == "generator"]
    print(json.dumps({"generator": pairs, "unresolved": unresolved, "undecided": open_}, indent=1,
                     ensure_ascii=False))
    if args.write:
        data = json.loads(bpath.read_text(encoding="utf-8"))
        data["footnotes"] = sorted(hand + pairs, key=lambda f: f["body"][0])
        bpath.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        S.Segmentation(source, S.load_boundaries(bpath))
    elif args.check and (frozen != pairs or open_):
        print("stale: the frozen generator pairs differ from the proposal, or a candidate is undecided",
              file=sys.stderr)
        return 1
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.fidmech", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("textcheck", "furniture", "boundaries"):
        p = sub.add_parser(name)
        p.add_argument("--doc", required=True)
        p.add_argument("--source")
        if name == "textcheck":
            p.add_argument("--checks", nargs="+", default=["L1"])
            p.add_argument("--span", choices=("sentence",), default="sentence",
                           help="D's span: the full source sentences of each block's quotes (plan 3.6)")
            p.add_argument("--json")
        if name == "boundaries":
            g = p.add_mutually_exclusive_group()
            g.add_argument("--check", action="store_true")
            g.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    try:
        return {"textcheck": textcheck, "furniture": furniture, "boundaries": boundaries}[args.cmd](args)
    except (S.BoundariesError, OSError, ValueError) as e:
        print(f"fidmech: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
