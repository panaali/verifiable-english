"""``python -m ve_experiments.assist_eval``: run, audit and report the ve assist evaluation.

Commands
  items    --split dev|heldout             print the item ids
  smoke    [--run-id ID]                   ONE dev item, arm A3, Opus author, <= 30 tool calls
  run      --split S --run-id ID [...]     serial sessions (items x authors x arms); resumable
  audit-export --run-id ID                 blinded packets (no model calls)
  audit-run    --run-id ID [--account L]    Codex (GPT-6 Astra) audits Claude authors, Opus audits Gemini
  report       --run-id ID                 report.json + audit-spotcheck.jsonl
  hashes   [--write]                       PREREG hash manifest (tool, prompts, items, config)

A held-out run refuses to start unless PREREG-ASSIST.md line 1 is
"Status: FROZEN" and the recomputed manifest equals PREREG-HASHES.txt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from .items import ROOT, item_ids, items
from .loop import ARMS, Limits, SessionRun, new_session

HERE = ROOT / "experiments" / "assist-eval"
RUNS = HERE / "runs"
PREREG = HERE / "PREREG-ASSIST.md"
MANIFEST = HERE / "PREREG-HASHES.txt"
AUTHORS = ("opus", "haiku", "gemini")

# Registered configuration (hashed). Budget/limits identical for every author and arm.
CONFIG = {
    "budget_usd_per_item": 2.00,
    "max_turns": 60,
    "max_tool_calls": 250,
    "calls_per_turn": 10,
    "author_output_tokens": 16000,
    "opus_effort": "medium",
    "gemini_thinking_level": "LOW (ve_experiments.paid.VertexBackend)",
    "gemini_max_input_tokens": 190000,
    "claude_account": "saeedi.danial (default; --account main uses the default Claude configuration; one "
                      "account per author x arm)",
    "proposer_model": "haiku (default; --proposer-model sonnet|opus)",
    "ledger_verification": "ve.assist.verify_session on every final and A2 attempt ledger (dossier, arm options, "
                           "dedicated proposer calls ledger); a ledger that does not verify is never a success",
    "auditors": "GPT-6 Astra via codex exec (reasoning high) audits Claude authors; Opus 5.5 audits Gemini",
    "pricing": "ve_experiments/assist_eval/pricing.py",
    "arms": ["A2", "A3", "A4"],
    "authors": list(AUTHORS),
    "success": "tool status success (targets certified by replay, all steps certified, every claimed sentence "
               "derived, coverage, no load-bearing unanchored assumption, no renamed conclusion, consistent "
               "assumptions), where waivers of GIVEN sentences are the only tolerated failure, AND blind "
               "cross-family fidelity audit pass (every waiver judged acceptable)",
    "decision_threshold": "proceed to a cost-charged P5 VE-arm DEV run with the tool iff, for at least one author, "
                          "A3 or A4 reaches faithful_complete >= 6/12 on the HELD-OUT items",
    "heldout": "12 P5 scored items, seeded: one per family for 12 of 24 families, 4 benign/4 shift/4 smuggle",
}

TOOL_FILES = sorted([*(ROOT / "ve" / "assist").glob("*.py"), ROOT / "ve_experiments" / "assist_haiku.py",
                     ROOT / "ve_experiments" / "claude_cli.py", ROOT / "ve_experiments" / "paid.py",
                     *(ROOT / "ve_experiments" / "assist_eval").glob("*.py")])


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def manifest():
    from ve.assist import tool_schemas
    from ve.assist.session import TOOL_VERSION
    from ve.assist.proposer import PROMPT_VERSION as PROPOSE_VERSION
    from . import prompts
    lines = [f"tool_version {TOOL_VERSION} proposer_prompt {PROPOSE_VERSION} eval_prompts {prompts.PROMPT_VERSION}"]
    for path in TOOL_FILES:
        lines.append(f"{sha(path.read_bytes())}  {path.relative_to(ROOT)}")
    for arm, flags in ARMS.items():
        tools = (tool_schemas(proposer=flags["proposer"]) + [prompts.FINISH_TOOL]) if flags["tools"] else []
        for protocol in (True, False):
            text = prompts.author_system(arm, text_protocol=protocol, tools=tools, per_turn=CONFIG["calls_per_turn"])
            lines.append(f"{sha(text + json.dumps(tools, sort_keys=True))}  prompt:author:{arm}:"
                         f"{'text' if protocol else 'native'}")
    lines.append(f"{sha(prompts.AUDIT_SYSTEM + prompts.AUDIT_INSTRUCTIONS)}  prompt:auditor")
    for split in ("dev", "heldout"):
        ids = item_ids(split)
        lines.append(f"{sha(json.dumps(ids))}  items:{split}:{','.join(ids)}")
    lines.append(f"{sha(json.dumps(CONFIG, sort_keys=True))}  config:{json.dumps(CONFIG, sort_keys=True)}")
    return "\n".join(lines) + "\n"


def heldout_gate():
    first = PREREG.read_text(encoding="utf-8").splitlines()[0] if PREREG.exists() else ""
    if not first.startswith("Status: FROZEN"):
        raise SystemExit("held-out run refused: PREREG-ASSIST.md is not 'Status: FROZEN'")
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != manifest():
        raise SystemExit("held-out run refused: PREREG-HASHES.txt does not match the current tool/prompts/config")


def limits(args):
    return Limits(budget_usd=args.budget if args.budget is not None else CONFIG["budget_usd_per_item"],
                  max_turns=CONFIG["max_turns"],
                  max_tool_calls=args.max_tool_calls or CONFIG["max_tool_calls"],
                  calls_per_turn=CONFIG["calls_per_turn"])


DEFAULT_ACCOUNT = "saeedi.danial"


def account_label(args):
    value = getattr(args, "account", None) or DEFAULT_ACCOUNT
    return None if value == "main" else value


def make_author(name, out_dir, args):
    from .authors import ClaudeTextAuthor, GeminiAuthor
    if name in ("opus", "haiku"):
        return ClaudeTextAuthor(name, Path(out_dir) / "author-calls.jsonl", account=account_label(args),
                                effort=CONFIG["opus_effort"], output_tokens=CONFIG["author_output_tokens"])
    if args.gemini_cap_usd is None:
        raise SystemExit("gemini needs --gemini-cap-usd (hard cap for the run's paid ledger)")
    return GeminiAuthor(RUNS / args.run_id / "gemini-ledger.jsonl", cap_usd=args.gemini_cap_usd,
                        output_tokens=CONFIG["author_output_tokens"],
                        max_input_tokens=CONFIG["gemini_max_input_tokens"])


def run(args, split, authors, arms, only=None):
    rows = items(split)
    if only:
        rows = [r for r in rows if r["id"] in only or str(rows.index(r)) in only]
    summary = []
    for item in rows:
        for author_name in authors:
            for arm in arms:
                out = RUNS / args.run_id / split / author_name / arm / item["id"]
                if (out / "result.json").exists():
                    summary.append(json.loads((out / "result.json").read_text()))
                    continue
                calls = out / "proposer-calls.jsonl"
                if calls.exists():  # an interrupted A4 session restarts with a new session id: keep its
                    n = len(list(out.glob("proposer-calls.interrupted-*.jsonl"))) + 1  # calls apart
                    calls.rename(out / f"proposer-calls.interrupted-{n}.jsonl")
                out.mkdir(parents=True, exist_ok=True)
                author = make_author(author_name, out, args)
                result = SessionRun(item, split=split, author_name=author_name, author=author, arm=arm,
                                    out_dir=out, limits=limits(args), account=account_label(args),
                                    proposer_model=args.proposer_model,
                                    restart=len(list(out.glob("result.aborted-*.json")))).run()
                print(json.dumps({k: result[k] for k in ("item_id", "author", "arm", "stop_reason", "turns",
                                                         "tool_calls", "spent_usd", "tool_success")}), flush=True)
                if str(result["stop_reason"]).startswith(("abort: infrastructure", "abort: paid ledger")):
                    # e.g. an account session limit: not the author's failure. Keep the record aside so a
                    # rerun (same account, or the whole arm on another one) retries the session, and stop.
                    n = len(list(out.glob("result.aborted-*.json"))) + 1
                    (out / "result.json").rename(out / f"result.aborted-{n}.json")
                    raise SystemExit(f"infrastructure abort in {out}: {result['stop_reason']}")
                summary.append(result)
    return summary


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m ve_experiments.assist_eval")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("items"); s.add_argument("--split", required=True, choices=("dev", "heldout"))
    s = sub.add_parser("hashes"); s.add_argument("--write", action="store_true")
    for name in ("smoke", "run"):
        s = sub.add_parser(name)
        s.add_argument("--run-id", required=name == "run", default="smoke")
        s.add_argument("--budget", type=float)
        s.add_argument("--max-tool-calls", type=int)
        s.add_argument("--gemini-cap-usd", type=float)
        if name == "run":
            s.add_argument("--split", required=True, choices=("dev", "heldout"))
            s.add_argument("--authors", default=",".join(AUTHORS))
            s.add_argument("--arms", default="A2,A3,A4")
            s.add_argument("--items", help="comma-separated item ids or indexes (default all)")
        s.add_argument("--account", help="Claude account label (~/.claude-LABEL) for Claude authors and the "
                                         "proposer; 'main' = the default configuration (default saeedi.danial)")
        s.add_argument("--proposer-model", choices=("haiku", "sonnet", "opus"), default="haiku",
                       help="A4 proposer model (default haiku)")
    for name in ("audit-export", "audit-run", "report"):
        s = sub.add_parser(name); s.add_argument("--run-id", required=True)
        if name == "audit-run":
            s.add_argument("--account", help="Claude account label for the Opus auditor ('main' = default)")
    args = p.parse_args(argv)
    if args.command == "items":
        print("\n".join(item_ids(args.split)))
    elif args.command == "hashes":
        text = manifest()
        if args.write:
            MANIFEST.write_text(text, encoding="utf-8")
        print(text, end="")
    elif args.command == "smoke":
        args.max_tool_calls = args.max_tool_calls or 30
        run(args, "dev", ["opus"], ["A3"], only={"0"})
    elif args.command == "run":
        if args.split == "heldout":
            heldout_gate()
        authors = args.authors.split(",")
        arms = args.arms.split(",")
        if set(authors) - set(AUTHORS) or set(arms) - set(ARMS):
            raise SystemExit("unknown author or arm")
        run(args, args.split, authors, arms, set(args.items.split(",")) if args.items else None)
    elif args.command == "audit-export":
        from .audit import export
        print(f"{export(RUNS / args.run_id)} packets")
    elif args.command == "audit-run":
        from .audit import run_audit
        missing = run_audit(RUNS / args.run_id, account=account_label(args))
        if missing:
            print(f"{missing} packet(s) without a verdict; see audit/errors.jsonl and rerun audit-run")
            return 1
    elif args.command == "report":
        from .audit import report
        out = report(RUNS / args.run_id)
        print(out["a1"])
        for row in out["table"]:
            print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
