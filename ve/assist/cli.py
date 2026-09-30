"""``python -m ve assist``: a small human CLI over the same session and ledger.

The session file IS the ledger: every command replays it (verifying that each
recorded result reproduces), applies one action, and writes it back.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from ..errors import CheckerUnavailable, VEError
from ..wire import loads_json
from .api import call_tool, tool_schemas, tools_for_session
from .session import AssistSession
from .sources import load_source, select_p5_item, source_from_p5, source_from_text


def _load(path):
    return AssistSession.from_ledger(json.loads(Path(path).read_text(encoding="utf-8")))


def _save(session, path):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(session.to_ledger(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _wrap(text, indent):
    return text.replace("\n", "\n" + indent)


def _node_lines(view, indent=""):
    head = f"{indent}[{view['name']}] {view['kind']}, {view['origin']}"
    if view.get("check"):
        head += f", check: {view['check']}"
    if view.get("matches_targets"):
        head += ", states target " + ", ".join(view["matches_targets"])
    lines = [head, f"{indent}  VE:   {view['text']}", f"{indent}  says: {_wrap(view['paraphrase'], indent + '        ')}"]
    if view["anchors"]:
        lines.append(f"{indent}  anchors: " + "; ".join(
            f"{a['id']} ({a['role']})" if isinstance(a, dict) else a for a in view["anchors"]))
    if view["parents"]:
        lines.append(f"{indent}  parents: " + ", ".join(view["parents"]))
    return lines


def _model_lines(model, indent="    "):
    lines = [indent + "entities: " + "; ".join(f"{s}: {', '.join(v) or '(empty)'}"
                                              for s, v in model["entities"].items())]
    if model["true"]:
        lines.append(indent + "true:  " + ", ".join(model["true"]))
    if model["false"]:
        lines.append(indent + "false: " + ", ".join(model["false"]))
    return lines


def render(command, result):
    if not result.get("ok", True):
        error = result["error"]
        return f"error: {error.get('code')}: {error.get('message')}"
    lines = []
    if "node" in result and isinstance(result["node"], dict):
        lines += _node_lines(result["node"])
        if result.get("invalidated_checks"):
            lines.append("  invalidated checks: " + ", ".join(result["invalidated_checks"]))
        if result["node"].get("countermodel"):
            lines += ["  countermodel:"] + _model_lines(result["node"]["countermodel"])
    elif command == "check":
        lines.append(f"{result['node']}: {result['status'].upper()}  ({', '.join(result['parents'])} => "
                     f"{result['conclusion']})")
        lines.append(f"  says: {result['conclusion_paraphrase']}")
        if result.get("warning"):
            lines.append("  warning: " + result["warning"])
        if result.get("countermodel"):
            lines += ["  countermodel (all parents true, conclusion false):"] + _model_lines(result["countermodel"])
        if result.get("detail"):
            lines.append("  " + result["detail"])
        for s in result.get("premise_suggestions", []):
            lines.append(f"  suggestion {s['id']} [{s['kind']}] {s['text']}  -- risk: {s['risk']}")
    elif command == "freeze":
        lines += [f"target {result['target']} frozen: {result['text']}", f"  says: {result['paraphrase']}",
                  f"  sentence {result['sentence']['id']}: {result['sentence']['text']}"]
    elif command == "sentences":
        for s in result["sentences"]:
            lines.append(f"{s['id']:>8} [{s['role']}{'' if s['asserting'] else ', non-asserting'}] {s['text']}")
        for t in result["targets"]:
            lines.append(f"target {t['id']} -> sentence {t['sentence']['id']}: "
                         + (t["text"] if t["frozen"] else "(not frozen)"))
        lines.append("predicates: " + ", ".join(f"{k}({', '.join(v['arguments'])})"
                                                for k, v in result["vocabulary"]["predicates"].items()))
        lines.append("constants: " + ", ".join(result["vocabulary"]["constants"]))
    elif command == "show":
        for t in result["targets"]:
            lines.append(f"target {t['id']}: " + (f"{t['text']}\n  says: {t['paraphrase']}" if t["frozen"]
                                                   else "(not frozen)"))
        for view in result["nodes"]:
            lines += _node_lines(view)
    elif command == "status":
        lines.append("SUCCESS" if result["success"] else "NOT YET: " + "; ".join(result["failures"]))
        for t in result["targets"]:
            lines.append(f"target {t['id']}: " + ("certified (graph replays)" if t.get("certified") else
                                                  f"not certified ({t.get('reason') or t.get('replay')})"))
        for row in result["unproved_steps"]:
            lines.append(f"unproved step {row['node']} ({row['check']})")
        for row in result["unanchored_assumptions"]:
            lines.append(f"unanchored assumption {row['node']} [{row['anchor_state']}]"
                         + (" LOAD-BEARING for " + ", ".join(row["needed_by"]) if row["load_bearing"] else ""))
        cov = result["coverage"]
        lines.append(f"coverage: {cov['derived']} claimed derived, {cov['covered']} given covered, "
                     f"{cov['waived']} waived, {len(cov['uncovered'])} uncovered"
                     + (f" ({', '.join(cov['uncovered'])})" if cov["uncovered"] else "")
                     + f", {len(cov['underived'])} claimed underived"
                     + (f" ({', '.join(cov['underived'])})" if cov["underived"] else ""))
        for row in result["waivers"]:
            lines.append(f"waiver {row['sentence']} [{row['role']}]: {row['reason']}"
                         + (" (blocks success)" if row["counts_against_success"] else ""))
        for row in result["renamed_conclusions"]:
            lines.append(f"renamed conclusion: {row['assumptions']} "
                         + ("may entail (undecided within budget; fail closed) " if row.get("undecided") else "entail ")
                         + row["target"])
        lines.append("provenance: " + ", ".join(f"{k} {v}" for k, v in result["provenance"].items() if v))
        tokens = result["usage"]["tokens"]
        if tokens:
            lines.append("tokens: " + json.dumps(tokens))
    elif command == "propose":
        lines.append(f"proposal {result['proposal']} for {result['sentence']['id']}: {result['sentence']['text']}")
        for c in result["candidates"]:
            lines += [f"  {c['id']}: {c['text']}", f"      says: {_wrap(c['paraphrase'], ' ' * 12)}"]
            if c["reading"]:
                lines.append(f"      reading: {c['reading']}")
        for d in result["dropped"]:
            error = d["error"] if isinstance(d["error"], str) else d["error"].get("message")
            lines.append(f"  dropped: {d['raw'][:80]!r}: {error}")
        for comp in result["comparisons"]:
            lines.append(f"  {comp['a']} vs {comp['b']}: {comp['relation']}")
            for model in comp.get("distinguishing_models", []):
                lines.append(f"    model where {'a' if model['a_value'] else 'b'} holds and "
                             f"{'b' if model['a_value'] else 'a'} does not:")
                lines += _model_lines(model, "      ")
        lines.append("  " + result["note"])
    elif command == "compare":
        lines.append(f"{result['relation']}: a = {result['a_text']} ; b = {result['b_text']}")
        for model in result.get("distinguishing_models", []):
            lines.append(f"  model ({model['kind']}):")
            lines += _model_lines(model, "    ")
    elif command == "waive":
        lines.append(f"waived {result['waived']}: {result['reason']}")
    elif command == "paraphrase":
        lines += [result["text"], "  says: " + result["paraphrase"]]
    else:
        lines.append(json.dumps(result, ensure_ascii=False, indent=1))
    return "\n".join(lines)


EXIT_CHECKER_UNAVAILABLE = 5


def exit_code(result):
    """0 for an ok result, 5 when no verdict was obtained (CheckerUnavailable), else 2.

    Session actions and tool calls return operational failures as results, so
    the code is read from the result, not only from a raised exception. Such an
    action is not saved: the ledger must replay, and an operational failure
    does not recur once the checker is available again.
    """
    if result.get("ok", True):
        return 0
    error = result.get("error")
    return EXIT_CHECKER_UNAVAILABLE if type(error) is dict and error.get("code") == "CheckerUnavailable" else 2


def _proposer(args):
    from ve_experiments.assist_haiku import ClaudeProposer
    ledger = args.calls_ledger or str(args.session) + ".calls.jsonl"
    return ClaudeProposer(ledger, model=args.proposer_model, account=args.account, max_calls=args.max_calls)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m ve assist",
                                     description="Interactive sentence-level assisted formalisation")
    parser.add_argument("--json", action="store_true", help="print raw JSON results")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new", help="create a session file")
    new.add_argument("session")
    new.add_argument("--env", help="environment JSON")
    new.add_argument("--english-vocabulary", help="English overlay JSON")
    new.add_argument("--text", help="source prose file (paragraphs tagged [given]/[claimed]/[context]; "
                                    "untagged paragraphs are claimed)")
    new.add_argument("--source", help="source JSON {'sentences': [...]}")
    new.add_argument("--target", action="append", default=[], metavar="SENTENCE_ID")
    new.add_argument("--p5", help="P5 dossier JSONL(.gz) file")
    new.add_argument("--item", help="P5 item id or index")
    new.add_argument("--p5-targets", choices=("root", "all"), default="root")
    new.add_argument("--premise-suggestions", action="store_true", help="enable premise suggestions (ablation)")

    def with_session(name, help_text):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("session")
        return p

    with_session("sentences", "list sentences, targets and vocabulary")
    p = with_session("freeze", "freeze a target's formal statement")
    p.add_argument("target"); p.add_argument("text", nargs="?")
    p.add_argument("--candidate")
    p = with_session("add", "add a node")
    p.add_argument("name"); p.add_argument("text", nargs="?")
    p.add_argument("--anchor", action="append", default=[]); p.add_argument("--parent", action="append", default=[])
    p.add_argument("--candidate"); p.add_argument("--suggestion")
    p = with_session("rewrite", "rewrite a node")
    p.add_argument("name"); p.add_argument("text", nargs="?")
    p.add_argument("--anchor", action="append"); p.add_argument("--parent", action="append")
    p = with_session("remove", "remove a node"); p.add_argument("name")
    p = with_session("declare", "declare vocabulary (gloss required)")
    p.add_argument("name"); p.add_argument("--gloss", required=True)
    p.add_argument("--kind", default="predicate", choices=("predicate", "constant", "sort"))
    p.add_argument("--arg", action="append", default=[], help="argument sort (repeat for binary)")
    p.add_argument("--sort"); p.add_argument("--verbalisation")
    p.add_argument("--acknowledge", action="append", default=[])
    p = with_session("check", "check a step")
    p.add_argument("name"); p.add_argument("--suggest-premises", action="store_true")
    p.add_argument("--invariant", action="append", default=[])
    with_session("status", "summarise success conditions")
    p = with_session("waive", "waive an asserting sentence"); p.add_argument("sentence"); p.add_argument("reason")
    p = with_session("show", "show nodes with paraphrases"); p.add_argument("name", nargs="?")
    p = with_session("paraphrase", "paraphrase VE text"); p.add_argument("text")
    p = with_session("compare", "compare two statements"); p.add_argument("a"); p.add_argument("b")
    p = with_session("propose", "proposer (Haiku 4.5 by default) candidates for one sentence")
    p.add_argument("sentence"); p.add_argument("--k", type=int); p.add_argument("--note")
    with_session("export", "export argument graphs and nodes")
    with_session("replay", "replay the ledger and report whether it reproduces")
    with_session("ledger", "print ledger usage summary")
    p = with_session("call", "raw JSON tool call (agent interface)")
    p.add_argument("tool"); p.add_argument("arguments", nargs="?", default="{}")
    p.add_argument("--proposer", action="store_true", help="enable the Haiku proposer tools")
    tools = sub.add_parser("tools", help="print tool schemas")
    tools.add_argument("--proposer", action="store_true"); tools.add_argument("--premise-suggestions", action="store_true")
    for p in sub.choices.values():
        if "session" in [a.dest for a in p._actions]:
            p.add_argument("--account", default=None,
                           help="Claude account label for propose (~/.claude-LABEL; default "
                                "$VE_ASSIST_CLAUDE_ACCOUNT, else the default Claude configuration)")
            p.add_argument("--proposer-model", choices=("haiku", "sonnet", "opus"), default="haiku",
                           help="proposer model (recorded with every call in the ledger)")
            p.add_argument("--max-calls", type=int, default=None, help="cap on proposer calls in the calls ledger")
            p.add_argument("--calls-ledger", help="claude CLI audit ledger (default SESSION.calls.jsonl)")
    args = parser.parse_args(argv)

    def emit(command, result):
        print(json.dumps(result, ensure_ascii=False, indent=1) if args.json else render(command, result))
        return exit_code(result)

    try:
        if args.command == "tools":
            return emit("tools", {"tools": tool_schemas(proposer=args.proposer,
                                                         premise_suggestions=args.premise_suggestions)})
        if args.command == "new":
            if Path(args.session).exists():
                raise VEError(f"{args.session} exists; sessions are never overwritten")
            options = {"premise_suggestions": args.premise_suggestions}
            if args.p5:
                item = select_p5_item(args.p5, args.item)
                built = source_from_p5(item, targets=args.p5_targets)
                session = AssistSession.create(built["environment"], built["source"], built["targets"],
                                               options=options, metadata=built["metadata"])
            else:
                if not args.env or not (args.text or args.source) or not args.target:
                    raise VEError("new needs --env, --text or --source, and at least one --target (or --p5)")
                env = loads_json(Path(args.env).read_bytes())
                overlay = (loads_json(Path(args.english_vocabulary).read_bytes())
                           if args.english_vocabulary else None)
                source = (source_from_text(Path(args.text).read_text(encoding="utf-8")) if args.text
                          else load_source(json.loads(Path(args.source).read_text(encoding="utf-8"))))
                targets = []
                for sid in args.target:
                    for row in source["sentences"]:
                        if row["id"] == sid:
                            row["role"] = "claimed"
                    targets.append({"id": "t_" + sid.replace(".", "_"), "sentence": sid})
                session = AssistSession.create(env, source, targets, english_vocabulary=overlay, options=options)
            _save(session, args.session)
            print(f"created {args.session}: {len(session.sentences)} sentences, targets "
                  + ", ".join(f"{t} -> {r['sentence']}" for t, r in session.targets.items()))
            return 0
        session = _load(args.session)
        command = args.command
        if command == "replay":
            print(f"ledger replays: {len(session.events)} events reproduce")
            return 0
        if command == "ledger":
            return emit("ledger", session.usage())
        if command == "call":
            if args.proposer:
                session.proposer = _proposer(args)
            result = call_tool(session, args.tool, args.arguments)
            code = exit_code({"ok": bool(result.get("ok")), "error": result.get("error")})
            if code != EXIT_CHECKER_UNAVAILABLE:
                _save(session, args.session)
            print(json.dumps(result, ensure_ascii=False, indent=1))
            return code
        mapping = {
            "sentences": ("sentences", {}),
            "freeze": ("freeze_target", {"target": args.__dict__.get("target"), "text": args.__dict__.get("text"),
                                         "candidate": args.__dict__.get("candidate")}),
            "add": ("add_node", {"name": args.__dict__.get("name"), "text": args.__dict__.get("text"),
                                 "anchors": args.__dict__.get("anchor"), "parents": args.__dict__.get("parent"),
                                 "candidate": args.__dict__.get("candidate"),
                                 "suggestion": args.__dict__.get("suggestion")}),
            "rewrite": ("rewrite", {"name": args.__dict__.get("name"), "text": args.__dict__.get("text"),
                                    "anchors": args.__dict__.get("anchor"), "parents": args.__dict__.get("parent")}),
            "remove": ("remove_node", {"name": args.__dict__.get("name")}),
            "declare": ("declare", {"name": args.__dict__.get("name"), "gloss": args.__dict__.get("gloss"),
                                    "kind": args.__dict__.get("kind"), "arguments": args.__dict__.get("arg"),
                                    "sort": args.__dict__.get("sort"),
                                    "verbalisation": args.__dict__.get("verbalisation"),
                                    "acknowledge": args.__dict__.get("acknowledge")}),
            "check": ("check_step", {"name": args.__dict__.get("name"),
                                     "suggest_premises": args.__dict__.get("suggest_premises"),
                                     "invariants": args.__dict__.get("invariant")}),
            "status": ("status", {}),
            "waive": ("waive", {"sentence": args.__dict__.get("sentence"), "reason": args.__dict__.get("reason")}),
            "show": ("show", {"name": args.__dict__.get("name")}),
            "paraphrase": ("paraphrase", {"text": args.__dict__.get("text")}),
            "compare": ("compare", {"a": args.__dict__.get("a"), "b": args.__dict__.get("b")}),
            "propose": ("propose", {"sentence": args.__dict__.get("sentence"), "k": args.__dict__.get("k"),
                                    "note": args.__dict__.get("note")}),
            "export": ("export", {}),
        }
        action, arguments = mapping[command]
        arguments = {k: v for k, v in arguments.items() if v not in (None, [], False)}
        if command == "propose":
            session.proposer = _proposer(args)
        result = session.apply(action, arguments)
        if exit_code(result) != EXIT_CHECKER_UNAVAILABLE:
            _save(session, args.session)
        return emit(command, result)
    except CheckerUnavailable as exc:
        print(f"error: CheckerUnavailable: {exc.message}", file=sys.stderr)
        return EXIT_CHECKER_UNAVAILABLE
    except (VEError, OSError, ValueError, RuntimeError) as exc:
        message = exc.message if isinstance(exc, VEError) else str(exc)
        print(f"error: {message}", file=sys.stderr)
        return 2
