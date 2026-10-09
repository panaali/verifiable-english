#!/usr/bin/env python3
"""Batch 17 paired public-path evidence. The case matrix is shared by both checkouts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OPTIONS = {"max_proof_steps": 10_000, "max_domain_size": 2,
           "max_models": 10, "max_evaluations": 1000}


def cases():
    # Both proof and witness budgets cross zero independently. Include the
    # adequate-budget controls, both polarities, and both assist call sites.
    for formula in ("top", "bottom", "forall"):
        for budget in ("adequate", "proof_zero", "models_zero"):
            for operation in ("decide", "entails"):
                yield {"path": "assist", "case": f"{operation}/{formula}/{budget}",
                       "operation": operation, "formula": formula, "budget": budget}
    for policy in ("permit", "forbid"):
        yield {"path": "cedar", "case": policy, "operation": "decisions", "policy": policy}


def run_case(case):
    if case["path"] == "assist":
        from ve.assist.session import AssistSession
        from ve.ast import Bottom, Forall, Top, Unary, Var
        from ve.environment import Environment, LANGUAGE, PROFILE, SPEC_REVISION
        vocabulary = {"sorts": {}, "predicates": {}, "constants": {}}
        if case["formula"] == "forall":
            vocabulary = {"sorts": {"s": {"description": "A member"}},
                          "predicates": {"p": {"arguments": ["s"], "description": "Property p"}},
                          "constants": {}}
        environment = {"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
                       "vocabulary": vocabulary}
        session = object.__new__(AssistSession)
        session.env = Environment(environment)
        session.options = dict(OPTIONS)
        if case["budget"] == "proof_zero":
            session.options["max_proof_steps"] = 0
        elif case["budget"] == "models_zero":
            session.options["max_models"] = 0
        formula = {"top": lambda: Top(), "bottom": lambda: Bottom(),
                   "forall": lambda: Forall("s", Unary("p", Var(0)))}[case["formula"]]()
        return getattr(session, "_" + case["operation"])((), formula)
    from ve.adapters.cedar import translate
    effect = case["policy"]
    source = (f'{effect}(principal, action, resource) when '
              '{ principal == User::"alice" };')
    requests = [{"principal": f'User::"{user}"', "action": 'Action::"read"',
                 "resource": 'Doc::"one"'} for user in ("alice", "bob")]
    return translate(source, [], [], requests).decisions()


def record(root: Path, output: Path):
    # A child process imports ve from the selected checkout, never from this tool.
    env = {**os.environ, "PYTHONPATH": str(root)}
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "_child",
                                "--root", str(root), "--out", str(output)],
                               cwd=root, env=env, check=False)
    return completed.returncode


def child(root: Path, output: Path):
    import ve
    if not Path(ve.__file__).resolve().is_relative_to(root.resolve()):
        raise RuntimeError(f"ve imported from {ve.__file__}, not {root}")
    rows = []
    for case in cases():
        try:
            value = run_case(case)
            # JSON round trip gives tuple/list equality the same shape on both sides.
            outcome = {"returned": json.loads(json.dumps(value))}
        except Exception as exc:  # record the public failure, then compare it
            outcome = {"raised": {"code": getattr(exc, "code", type(exc).__name__),
                                  "message": str(exc)}}
        rows.append({"path": case["path"], "case": case["case"], "outcome": outcome})
    output.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")


def load(path: Path):
    rows = json.loads(path.read_text())
    expected = {(c["path"], c["case"]) for c in cases()}
    if type(rows) is not list or len(rows) != len(expected):
        raise ValueError(f"{path}: incomplete case matrix")
    found = set()
    for row in rows:
        if type(row) is not dict or set(row) != {"path", "case", "outcome"}:
            raise ValueError(f"{path}: malformed row")
        key = (row["path"], row["case"])
        if key in found or key not in expected:
            raise ValueError(f"{path}: duplicate or unknown case {key}")
        found.add(key)
        outcome = row["outcome"]
        if type(outcome) is not dict or len(outcome) != 1 or not set(outcome) <= {"returned", "raised"}:
            raise ValueError(f"{path}: malformed outcome {key}")
        if "raised" in outcome and (type(outcome["raised"]) is not dict or
                                    set(outcome["raised"]) != {"code", "message"} or
                                    any(type(v) is not str or not v for v in outcome["raised"].values())):
            raise ValueError(f"{path}: malformed error {key}")
        if "returned" in outcome:
            value = outcome["returned"]
            if key[0] == "assist" and (type(value) is not (str if key[1].startswith("decide/") else bool)
                                         or value not in ({"yes", "no", "unknown"} if type(value) is str else {True, False})):
                raise ValueError(f"{path}: malformed assist result {key}")
            if key[0] == "cedar" and (type(value) is not list or len(value) != 2 or
                                      any(type(item) is not dict or type(item.get("decision")) is not str
                                          or item["decision"] not in ("allow", "deny") or
                                          type(item.get("errors")) is not list for item in value)):
                raise ValueError(f"{path}: malformed Cedar result {key}")
    if found != expected:
        raise ValueError(f"{path}: missing cases")
    return {(row["path"], row["case"]): row["outcome"] for row in rows}


def compare(base: Path, head: Path, delta: Path, output: Path):
    def same_json(a, b):
        return json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False)
    left, right = load(base), load(head)
    signed = json.loads(delta.read_text())["verdict"]
    listed = {}
    for row in signed:
        key = (row["path"], row["case"])
        if key in listed or key not in left or set(row) != {"path", "case", "base", "head"}:
            raise ValueError(f"invalid signed delta {key}")
        listed[key] = row
    differences = []
    for key in sorted(left):
        if same_json(left[key], right[key]):
            continue
        row = listed.get(key)
        differences.append({"path": key[0], "case": key[1], "base": left[key], "head": right[key],
                            "listed": row is not None and same_json(row["base"], left[key])
                            and same_json(row["head"], right[key])})
    if set(listed) - {(row["path"], row["case"]) for row in differences}:
        raise ValueError("signed delta names an unchanged or missing case")
    result = {"base_sha256": hashlib.sha256(base.read_bytes()).hexdigest(),
              "head_sha256": hashlib.sha256(head.read_bytes()).hexdigest(),
              "records": {path: sum(key[0] == path for key in left) for path in ("assist", "cedar")},
              "same": len(left) - len(differences), "differences": differences,
              "unlisted": sum(not row["listed"] for row in differences)}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0 if result["unlisted"] == 0 else 1


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("record", "_child"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--root", type=Path, required=True)
        cmd.add_argument("--out", type=Path, required=True)
    cmd = sub.add_parser("compare")
    for name in ("base", "head", "delta", "out"):
        cmd.add_argument(name, type=Path)
    args = parser.parse_args()
    if args.command == "record":
        return record(args.root, args.out)
    if args.command == "_child":
        child(args.root, args.out)
        return 0
    return compare(args.base, args.head, args.delta, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
