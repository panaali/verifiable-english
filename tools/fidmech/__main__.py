"""The fidmech command line: textcheck (L1 report), furniture (every furniture match) and boundaries (footnote pairs).

  uv run python -m tools.fidmech textcheck --doc anthropic-rsp [--checks L1] [--json OUT]
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
from tools.fidmech import textchecks as T

CHECKS = ("L1",)


def _case(args):
    case = S.accounting.case_dir(args.doc)
    if not case.is_dir():
        raise S.BoundariesError(f"no case directory {args.doc!r}")
    source = Path(args.source) if args.source else S.doc_source(case)
    return case, source.read_bytes(), case / "fidmech" / "boundaries.json"


def textcheck(args) -> int:
    args.checks = [c for arg in args.checks for c in arg.split(",") if c]
    unknown = set(args.checks) - set(CHECKS)
    if unknown:
        raise S.BoundariesError(f"checks {sorted(unknown)} are not built in this batch (only {', '.join(CHECKS)})")
    case, data, bpath = _case(args)
    result = T.report(case, data, bpath)
    print(f"{result['document']}: {result['blocks']} blocks, {result['quotes']['checked']} quotes checked, "
          f"{result['quotes']['note']} note quotes, {result['quotes']['empty']} empty (info, outside the headline)")
    print("L1 hits: " + ", ".join(f"{c} {n}" for c, n in result["counts"].items()))
    for lever, row in result["levers"].items():
        print(f"  {lever} off: " + ", ".join(f"{c} {n}" for c, n in row["counts"].items())
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
    pairs, unresolved = S.propose(source, b.furniture)
    hand = [f for f in b.footnotes if f["by"] == "hand"]
    decided = {f["body"][0] for f in hand} | {f["marker_at"] for f in hand} | {u["at"] for u in b.unpaired}
    open_ = [u for u in unresolved if u["at"] not in decided]
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
            p.add_argument("--checks", nargs="+", default=list(CHECKS))
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
