#!/usr/bin/env python3
"""Bind the four named properties to the excerpt's recorded content."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from ve import ast  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from ve.profiles import SPEC_REVISION  # noqa: E402
from ve.surface.definitions import wordings  # noqa: E402

ROOT = HERE.parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_conformance"
RUST = ROOT / "rust/target/release/ve"


def other_checkers(env, model_json, asts):
    """The same evaluation by the Lean route and the Rust conformance runner,
    each regenerating Background and computing the defined tables itself."""
    import subprocess
    case = {"id": "constitution", "environment": env.to_dict(), "model": model_json, "ast": asts}
    out = {}
    for name, command in (("lean", [str(LEAN), "route", "-"]), ("rust", [str(RUST), "conformance"])):
        if not Path(command[0]).exists():
            out[name] = None
            continue
        run = subprocess.run(command, input=json.dumps([case]), capture_output=True, text=True, timeout=600)
        out[name] = json.loads(run.stdout)[0].get("values")
    return out


def implication_guard(sort, guard, consequence):
    return ast.Forall(sort, ast.Implies(guard, consequence))


def definitions():
    model = ast.Var(0)
    return {
        "safety_content": implication_guard("mechanism", ast.Unary("appropriate", ast.Var(0)),
            ast.Not(ast.Binary("undermines", ast.Var(1), ast.Var(0)))),
        "ethics_content": ast.And(ast.Unary("honest", model),
            implication_guard("action", ast.Unary("inappropriately_harmful", ast.Var(0)),
                ast.Not(ast.Binary("performs", ast.Var(1), ast.Var(0))))),
        "guidelines_content": implication_guard("guideline", ast.Unary("relevant", ast.Var(0)),
            ast.Binary("follows", ast.Var(1), ast.Var(0))),
        "helpfulness_content": implication_guard("principal",
            ast.Binary("interacts", ast.Var(1), ast.Var(0)),
            ast.Binary("benefits", ast.Var(1), ast.Var(0))),
    }


def build_environment():
    raw = json.loads((HERE / "environment.json").read_text())
    raw["language"] = "ve.core@0.2"
    raw["profiles"] = ["closure@0", "definitions@0", "relational-fol@0"]
    raw["spec_revision"] = SPEC_REVISION
    vocabulary = raw["vocabulary"]["predicates"]
    for name, body in definitions().items():
        vocabulary[name] = {"arguments": ["claude_model"],
                            "description": f"The excerpt's recorded {name.replace('_', ' ')} condition.",
                            "defined": {"arguments": ["claude_model"], "body": ast._to_data(body)}}
    options = []
    for constant, predicate in (("safety", "safety_content"), ("ethics", "ethics_content"),
                                ("guidelines", "guidelines_content"),
                                ("helpfulness", "helpfulness_content")):
        options.append(ast.And(ast.Eq(ast.Var(0), ast.Const(constant)),
                               ast.Unary(predicate, ast.Var(1))))
    body = options[0]
    for option in options[1:]:
        body = ast.Or(body, option)
    vocabulary["holds_property"] = {
        "arguments": ["claude_model", "property"],
        "description": "Connects each named property constant to its recorded content.",
        "defined": {"arguments": ["claude_model", "property"], "body": ast._to_data(body)}}
    return Environment(raw)


def main():
    env = build_environment()
    (HERE / "definitions-environment.json").write_text(json.dumps(env.to_dict(), indent=2) + "\n")
    model_json = json.loads((HERE / "model-true.json").read_text())
    model = FiniteModel.from_dict(env, model_json)
    subject = model.constants["claude"]
    rows = []
    for constant, predicate in (("safety", "safety_content"), ("ethics", "ethics_content"),
                                ("guidelines", "guidelines_content"),
                                ("helpfulness", "helpfulness_content")):
        content = (subject,) in model.relations[predicate]
        linked = (subject, model.constants[constant]) in model.relations["holds_property"]
        assert content == linked
        rows.append((constant, predicate, content))
    asts = [["unary", predicate, ["const", "claude"]] for _, predicate, _ in rows] + [
        ["binary", "holds_property", ["const", "claude"], ["const", constant]] for constant, _, _ in rows]
    python_values = [value for _, _, value in rows] * 2
    checkers = other_checkers(env, model_json, asts)
    for name, values in checkers.items():
        if values is not None and values != python_values:
            raise RuntimeError(f"{name} disagrees: {values} != {python_values}")
    agreed = [name for name, values in checkers.items() if values is not None]
    lines = ["# Identity-bound property content", "",
             "The four unary definitions encode the excerpt's recorded conditions. `holds_property(model, property)` links `@safety`, `@ethics`, `@guidelines`, and `@helpfulness` to those bodies. The definitions are Background premises, not extra theorem hypotheses.",
             "", "| Constant | Defined predicate | Value in existing true-model fixture |", "|---|---|---|"]
    lines += [f"| `@{constant}` | `{predicate}` | `{value}` |" for constant, predicate, value in rows]
    lines += ["", "Python, " + " and ".join(n.capitalize() for n in agreed) + " decode the declarations, compute every "
              "defined table from its body and agree on all eight values above (four contents, four "
              "`holds_property` links)." if agreed else "Only Python was run.",
              "", "The definitions, as the English surface writes them:", ""]
    lines += [f"- {row['english'].strip()}" for row in wordings(env)]
    lines += ["", "The priority sentence still needs the W1 norm profile for its defeasible reading; this "
              "definition rerun makes no priority-rule claim.", ""]
    (HERE / "definitions-report.md").write_text("\n".join(lines))
    print(env.environment_id, rows)


if __name__ == "__main__":
    main()
