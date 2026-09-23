"""``python -m ve_experiments.assist_eval``: run, audit and report the ve assist evaluation.

Commands
  items    --split dev|heldout             print the item ids
  smoke    [--run-id ID]                   ONE dev item, arm A3, Opus author, <= 30 tool calls
  run      --split S --run-id ID [...]     serial sessions (items x authors x arms); resumable
  audit-export --run-id ID                 blinded packets (no model calls)
  proposer-smoke [--run-id ID]             ONE A4 propose call on a DEV sentence (<= 2 proposer model calls)
  audit-run    --run-id ID [--account L]    Codex (GPT-6 Astra) audits every packet; Opus also audits Gemini's
  report       --run-id ID [--legacy-audit] report.json + audit-spotcheck.jsonl
  hashes   [--write]                       PREREG hash manifest (PREREG text, tool, prompts, W, items, config)
  waivers  [--write]                       the preregistered allowlist W (waivers.json)

A held-out run refuses to start unless PREREG-ASSIST.md line 1 is
"Status: FROZEN", the recomputed manifest equals PREREG-HASHES.txt, waivers.json
equals the recomputed W, and no command-line setting differs from CONFIG.
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
AUTHORS = ("opus", "gemini")  # Haiku 4.5 was dropped as an author after dev-tune-2 (disclosed dev selection)
WAIVERS = HERE / "waivers.json"

# Registered configuration (hashed). Every EXECUTABLE setting of a held-out run is here and the CLI rejects
# any deviation at held-out time (``heldout_gate``). Budget/limits are identical for every author and arm.
CONFIG = {
    "budget_usd_per_item": 2.00,
    "budget_scope": "author + proposer spend over EVERY attempt at the item (aborted attempts included); "
                    "an exhausted budget stops the item, a restart never resets it",
    "max_turns": 60,
    "max_tool_calls": 250,
    "calls_per_turn": 10,
    "author_output_tokens": 16000,
    "opus_effort": "medium",
    "gemini_thinking_level": "LOW (ve_experiments.paid.VertexBackend)",
    "gemini_max_input_tokens": 190000,
    "gemini_cap_usd": 40.0,
    "claude_account": "main",
    "auditor_claude_account": "main",
    "proposer_model": "haiku",
    "authors": list(AUTHORS),
    "author_roles": {"opus": "primary", "gemini": "secondary"},
    "arms": ["A2", "A3", "A4"],
    "heldout_items": "all 12 (no --items subset)",
    "ledger_verification": "ve.assist.verify_session on every final and A2 attempt ledger (dossier, arm options, "
                           "dedicated proposer calls ledger); a ledger that does not verify is never a success",
    "waivers": "waivers.json: W(item) from the public dossier text (dossier.py); waivers must lie in W; no anchor "
               "on a waive-only sentence; a given-anchored assumption must be entailed by its anchors' reference "
               "content; no assumption may entail a 'remain unassumed' check",
    "auditors": {"all packets": "GPT-6 Astra via codex exec (reasoning high)",
                 "gemini packets": "additionally Opus 5.5 (claude CLI, main account)",
                 "packet pass": "every required auditor passes it"},
    "pricing": "ve_experiments/assist_eval/pricing.py",
    "success": "evaluation tool success (scoring.eval_success: status success apart from waivers inside W, and "
               "no dossier graph violation) AND a verified ledger AND audit pass",
    "faithful_complete": "benign: certified and faithful; flawed: audit pass AND scoring.gap_route (verdict gap, "
                         "every claimed sentence has an anchored step, every non-gap step certified, every gap "
                         "step refuted by a checker countermodel and not entailed by the whole dossier, "
                         "verified ledger, no violations, gap_located)",
    "primary_endpoint": "Opus 5.5 A3 vs A2 faithful-complete, paired by held-out item at the same $2 total "
                        "budget; exact two-sided sign test on discordant pairs",
    "secondary": "Gemini 3.1 Pro (secondary author), same endpoints; A4 exploratory, reported as 'proposer "
                 "offered, uptake n'",
    "claim": "minimum claim: the prespecified pipeline reached k/12 faithful-complete (exact one-sided 95% "
             "bound) with alarms a/8 on unseen same-generator P5 families at <= $2/item; no 80% fidelity, "
             "non-inferiority or transfer claim",
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
    from .dossier import allowlist_document
    lines.append(f"{sha(allowlist_document())}  waivers:{WAIVERS.relative_to(ROOT)}")
    lines.append(f"{sha(PREREG.read_bytes() if PREREG.exists() else b'')}  prereg:{PREREG.relative_to(ROOT)}")
    for split in ("dev", "heldout"):
        ids = item_ids(split)
        lines.append(f"{sha(json.dumps(ids))}  items:{split}:{','.join(ids)}")
    lines.append(f"{sha(json.dumps(CONFIG, sort_keys=True))}  config:{json.dumps(CONFIG, sort_keys=True)}")
    return "\n".join(lines) + "\n"


def heldout_gate(args=None):
    """Refuse a held-out run unless PREREG is FROZEN, the manifest (PREREG text, tool, prompts, W, CONFIG)
    recomputes byte for byte, waivers.json equals the recomputed W, and every executable setting given on
    the command line equals the registered CONFIG."""
    first = PREREG.read_text(encoding="utf-8").splitlines()[0] if PREREG.exists() else ""
    if not first.startswith("Status: FROZEN"):
        raise SystemExit("held-out run refused: PREREG-ASSIST.md is not 'Status: FROZEN'")
    from .dossier import allowlist_document
    if not WAIVERS.exists() or WAIVERS.read_text(encoding="utf-8") != allowlist_document():
        raise SystemExit("held-out run refused: waivers.json does not match the recomputed allowlist W")
    if not MANIFEST.exists() or MANIFEST.read_text(encoding="utf-8") != manifest():
        raise SystemExit("held-out run refused: PREREG-HASHES.txt does not match the current tool/prompts/config")
    if args is not None:
        deviations = registered_deviations(args)
        if deviations:
            raise SystemExit("held-out run refused: settings differ from the registered CONFIG: "
                             + "; ".join(deviations))


def registered_deviations(args):
    """Every command-line setting that differs from CONFIG (held-out runs take none of them)."""
    out = []
    checks = {"budget": CONFIG["budget_usd_per_item"], "max_tool_calls": CONFIG["max_tool_calls"],
              "proposer_model": CONFIG["proposer_model"], "account": CONFIG["claude_account"],
              "gemini_cap_usd": CONFIG["gemini_cap_usd"]}
    for key, registered in checks.items():
        value = getattr(args, key, None)
        if value is not None and value != registered:
            out.append(f"--{key.replace('_', '-')} {value} (registered {registered})")
    if getattr(args, "items", None):
        out.append("--items (a held-out run covers every registered item)")
    for key, allowed in (("authors", CONFIG["authors"]), ("arms", CONFIG["arms"])):
        value = getattr(args, key, None)
        if value and set(value.split(",")) - set(allowed):
            out.append(f"--{key} {value} (registered {','.join(allowed)})")
    return out


def limits(args):
    return Limits(budget_usd=args.budget if args.budget is not None else CONFIG["budget_usd_per_item"],
                  max_turns=CONFIG["max_turns"],
                  max_tool_calls=args.max_tool_calls or CONFIG["max_tool_calls"],
                  calls_per_turn=CONFIG["calls_per_turn"])


DEFAULT_ACCOUNT = CONFIG["claude_account"]  # "main": the default Claude configuration directory


def account_label(args, default=DEFAULT_ACCOUNT):
    value = getattr(args, "account", None) or default
    return None if value == "main" else value


def prior_attempts(out):
    """Spend of every earlier attempt at this session (``result.aborted-N.json``), as a Decimal."""
    from decimal import Decimal
    total = Decimal(0)
    for path in sorted(out.glob("result.aborted-*.json")):
        spent = json.loads(path.read_text(encoding="utf-8"))["spent_usd"]
        # "total" of an attempt already includes the attempts before it; count only its own spend.
        total += Decimal(spent["author"]) + Decimal(spent["proposer"])
    return total


def make_author(name, out_dir, args):
    from .authors import ClaudeTextAuthor, GeminiAuthor
    if name in ("opus", "haiku"):
        return ClaudeTextAuthor(name, Path(out_dir) / "author-calls.jsonl", account=account_label(args),
                                effort=CONFIG["opus_effort"], output_tokens=CONFIG["author_output_tokens"])
    cap = args.gemini_cap_usd if args.gemini_cap_usd is not None else CONFIG["gemini_cap_usd"]
    if cap > CONFIG["gemini_cap_usd"]:
        raise SystemExit(f"--gemini-cap-usd {cap} exceeds the registered ${CONFIG['gemini_cap_usd']} per run")
    return GeminiAuthor(RUNS / args.run_id / "gemini-ledger.jsonl", cap_usd=cap,
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
                                    proposer_model=args.proposer_model or CONFIG["proposer_model"],
                                    restart=len(list(out.glob("result.aborted-*.json"))),
                                    prior_spent=prior_attempts(out)).run()
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


def proposer_smoke(args, factory=None):
    """Restore-and-smoke-test the A4 proposer on DEV: one ``propose`` through the harness (budget gate,
    dedicated calls ledger), hard-capped at 2 model calls (propose + at most one repair round)."""
    from .loop import CostedProposer
    item = items("dev")[0]
    out = RUNS / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    session = new_session(item, author="proposer-smoke", arm="A4", split="dev")
    account = account_label(args)
    proposer = (factory or (lambda: CostedProposer(out / "proposer-calls.jsonl", account,
                                                   CONFIG["proposer_model"], max_calls=2)))()
    if hasattr(proposer, "inner"):
        proposer.inner.client.infrastructure_retries = False  # a retry would be a third call
    session.proposer = proposer
    sentence = next(sid for sid in session.sentence_order if session.sentences[sid]["role"] == "given"
                    and session.sentences[sid]["text"].startswith("If "))
    result = session.apply("propose", {"sentence": sentence, "k": 1})
    (out / "session.json").write_text(json.dumps(session.to_ledger(), indent=1, default=str) + "\n")
    return {"ok": bool(result.get("ok")) and bool(result.get("candidates")), "sentence": sentence,
            "account": account or "main", "calls": len(proposer.costs),
            "cost_usd": str(sum(proposer.costs)), "candidates": result.get("candidates"),
            "error": result.get("error")}


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m ve_experiments.assist_eval")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("items"); s.add_argument("--split", required=True, choices=("dev", "heldout"))
    s = sub.add_parser("hashes"); s.add_argument("--write", action="store_true")
    s = sub.add_parser("waivers"); s.add_argument("--write", action="store_true")
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
                                         "proposer; 'main' (default) = the default Claude configuration")
        s.add_argument("--proposer-model", choices=("haiku", "sonnet", "opus"),
                       help="A4 proposer model (default: registered, haiku)")
    s = sub.add_parser("proposer-smoke")
    s.add_argument("--run-id", default="proposer-smoke")
    s.add_argument("--account")
    for name in ("audit-export", "audit-run", "report"):
        s = sub.add_parser(name); s.add_argument("--run-id", required=True)
        if name == "audit-run":
            s.add_argument("--account", help="Claude account label for the Opus auditor ('main' = default)")
        if name == "report":
            s.add_argument("--legacy-audit", action="store_true",
                           help="score with verdicts/<packet>.json from a run audited before the dual-audit "
                                "layout (replay only; labelled as a proxy)")
            s.add_argument("--out", help="report directory (default: the run directory)")
    args = p.parse_args(argv)
    if args.command == "items":
        print("\n".join(item_ids(args.split)))
    elif args.command == "waivers":
        from .dossier import allowlist_document
        text = allowlist_document()
        if args.write:
            WAIVERS.write_text(text, encoding="utf-8")
        print(text, end="")
    elif args.command == "hashes":
        text = manifest()
        if args.write:
            MANIFEST.write_text(text, encoding="utf-8")
        print(text, end="")
    elif args.command == "smoke":
        args.max_tool_calls = args.max_tool_calls or 30
        run(args, "dev", ["opus"], ["A3"], only={"0"})
    elif args.command == "proposer-smoke":
        print(json.dumps(proposer_smoke(args), indent=1))
    elif args.command == "run":
        if args.split == "heldout":
            heldout_gate(args)
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
        if any((RUNS / args.run_id).glob("heldout/*/*/*/result.json")):
            heldout_gate()
            if (args.account or CONFIG["auditor_claude_account"]) != CONFIG["auditor_claude_account"]:
                raise SystemExit("held-out audit refused: --account differs from the registered auditor account")
        missing = run_audit(RUNS / args.run_id, account=account_label(args, CONFIG["auditor_claude_account"]))
        if missing:
            print(f"{missing} packet(s) without a verdict; see audit/errors.jsonl and rerun audit-run")
            return 1
    elif args.command == "report":
        from .audit import report
        out = report(RUNS / args.run_id, legacy_audit=args.legacy_audit,
                     out_dir=Path(args.out) if args.out else None)
        print(out["a1"])
        print(json.dumps(out.get("primary")))
        for row in out["table"]:
            print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
