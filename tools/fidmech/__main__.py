"""The fidmech command line: textcheck (the text-check report), furniture (every furniture match) and boundaries.

  uv run python -m tools.fidmech textcheck --doc anthropic-rsp [--checks L1,L1a,L2,L3,L4,D | all] [--span sentence]
                                           [--json OUT]
  uv run python -m tools.fidmech furniture --doc anthropic-rsp
  uv run python -m tools.fidmech boundaries --doc anthropic-rsp [--check | --write]
  uv run python -m tools.fidmech mutants --doc anthropic-rsp [--kinds structural,wording] [--no-parse-wording]
                                         [--jsonl OUT]   (counts per op, stillborn listed; needs the Lean service)
  uv run python -m tools.fidmech actors --doc anthropic-rsp [--check | --write]   (actors.json's generated list)
  uv run python -m tools.fidmech batch --doc <doc> --jobs auto --out DIR [--budget S] [--resume FILE] [--inputs DIR]
                                       (one document's mutant batch, tools/fidmech/runner.py; exit 75 when loaded)
  uv run python -m tools.fidmech report BATCH_DIR... --out DIR [--inputs DIR] [--cr FILE] [--rows DIR]
                                       (kill tables and the report, tools/fidmech/report.py; counts only)

--doc is a use-case name under usecases/ or a case directory; --source overrides the case's pinned source path.
Exit 0 on a report, 1 when `boundaries --check` finds the frozen pairs stale or a batch is INVALID, 2 on an input
error, 65 when an inputs file or a --resume file does not match its sha256, 75 when the host is too loaded to start.
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


def mutants(args) -> int:
    from tools.fidmech import mutants as M
    kinds = tuple(k for arg in args.kinds for k in arg.split(",") if k)
    if set(kinds) - {"structural", "wording"}:
        raise ValueError(f"unknown kinds {kinds} (structural, wording)")
    from tools.fidmech.worker import REPO
    records, report = M.document_mutants(REPO if args.worktree is None else Path(args.worktree), args.doc,
                                         kinds=kinds, parse_wording=not args.no_parse_wording)
    print(f"{args.doc}: {len(records)} mutants, generator {M.S.GENERATOR}, inputs_sha256 "
          f"{records[0]['inputs_sha256'] if records else None}")
    print(f"{'op':18} {'mutants':>7} {'ok':>5} {'stillborn':>9} {'syntactic':>9} {'duplicates':>10}")
    for op, row in M.counts(records, {"duplicates": {k: v for part in ("structural", "wording") if part in report
                                                     for k, v in report[part]["duplicates"].items()}}).items():
        print(f"{op:18} {row['mutants']:>7} {row['ok']:>5} {row['stillborn']:>9} {row['syntactic']:>9} "
              f"{row['duplicates']:>10}")
    for part in ("structural", "wording"):
        for key, value in report.get(part, {}).items():
            if key not in ("duplicates",) and value:
                print(f"{part} {key}: {json.dumps(value, ensure_ascii=False)}")
    undecided = [s["id"] for part in ("structural", "wording") for s in report.get(part, {}).get("stillborn", ())
                 if s["reason"].startswith("undecided: ")]
    print(f"stillborn because VE gave no answer (undecided, never scored): {len(undecided)} {undecided}")
    print("declarations: " + json.dumps({k: len(v) for k, v in report["declarations"].items()}))
    if args.jsonl:
        Path(args.jsonl).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
                                    encoding="utf-8")
    return 0


def actors(args) -> int:
    from tools.fidmech import mutants as M
    from tools.fidmech import wording as W
    case = S.accounting.case_dir(args.doc)
    path = case / "fidmech" / "actors.json"
    generated = W.propose_actors(M.case_files(case))
    print(json.dumps(generated, indent=1, ensure_ascii=False))
    if args.write:
        data = json.loads(path.read_text(encoding="utf-8"))
        data["generated"] = generated
        removed, added = [r["phrase"] for r in data["removed"]], [r["phrase"] for r in data["added"]]
        data["actors"] = sorted((set(generated) - set(removed)) | set(added), key=lambda a: (-len(a), a))
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    elif args.check and json.loads(path.read_text(encoding="utf-8"))["generated"] != generated:
        print("stale: actors.json's generated list differs from the generator's", file=sys.stderr)
        return 1
    W.load_actors(path)
    return 0


def batch(args) -> int:
    from tools.fidmech import runner
    return runner.main(args)


def report(args) -> int:
    from tools.fidmech import report as REP
    return REP.main(args)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.fidmech", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("batch")
    b.add_argument("--doc", required=True)
    b.add_argument("--jobs", default="auto")
    b.add_argument("--out", required=True)
    b.add_argument("--budget", type=float)
    b.add_argument("--resume")
    b.add_argument("--inputs", help="manage-agents reviews/fid-mech-harness/inputs/ (plants and defects; read by sha256)")
    r = sub.add_parser("report")
    r.add_argument("batches", nargs="+")
    r.add_argument("--out", required=True)
    r.add_argument("--inputs")
    r.add_argument("--cr")
    r.add_argument("--rows", help="where the per-plant and per-defect rows go (manage-agents, never VE)")
    for name in ("textcheck", "furniture", "boundaries", "mutants", "actors"):
        p = sub.add_parser(name)
        p.add_argument("--doc", required=True)
        p.add_argument("--source")
        if name == "textcheck":
            p.add_argument("--checks", nargs="+", default=["L1"])
            p.add_argument("--span", choices=("sentence",), default="sentence",
                           help="D's span: the full source sentences of each block's quotes (plan 3.6)")
            p.add_argument("--json")
        if name == "mutants":
            p.add_argument("--kinds", nargs="+", default=["structural,wording"])
            p.add_argument("--no-parse-wording", action="store_true")
            p.add_argument("--worktree")
            p.add_argument("--jsonl")
        if name in ("boundaries", "actors"):
            g = p.add_mutually_exclusive_group()
            g.add_argument("--check", action="store_true")
            g.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)
    try:
        return {"textcheck": textcheck, "furniture": furniture, "boundaries": boundaries, "mutants": mutants,
                "actors": actors, "batch": batch, "report": report}[args.cmd](args)
    except (S.BoundariesError, OSError, ValueError) as e:
        print(f"fidmech: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
