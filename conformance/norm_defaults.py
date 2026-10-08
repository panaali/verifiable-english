"""Rust fixtures for norm-defaults@0 (docs/spec/norm-defaults.md section 8).

Rust never elaborates. It receives Python's filled premise lists as untrusted
ordinary VE inputs: over the filled base vocabulary (the unsaid tables are base
tables) the Fill_T premises, the conflict targets and the reached targets, and
over E‴ the layers of `fill U`. Each row fixes one situation and one filling,
and records the Python evaluator's values, which the Rust test must reproduce.

`python conformance/norm_defaults.py` rewrites `norm_defaults_rust.json`;
tests/test_norm_defaults.py checks that the committed file equals this output.
"""
from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ve.ast import Exists, formula_to_data  # noqa: E402
from ve.environment import Environment  # noqa: E402
from ve.errors import InvalidModel  # noqa: E402
from ve.evaluate import _Evaluator  # noqa: E402
from ve.model import FiniteModel  # noqa: E402
from conformance import frozen_norm_defaults as nd  # noqa: E402
from ve.norms import NormDocument, _bind  # noqa: E402

RUST_FIXTURES = ROOT / "conformance/norm_defaults_rust.json"
PROFILES = ["norm-defaults@0", "norms@0", "relational-fol@0"]


def _environment(predicates, sorts=("act",), constants=None, profiles=PROFILES):
    from ve.profiles import LANGUAGE, SPEC_REVISION
    return {"language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in sorts},
                           "predicates": predicates, "constants": constants or {}}}


def _regulated(role, default, act="{0} be done", permission=None, args=("act",)):
    reg = {"role": role, "default": default, "act": act}
    if permission is not None:
        reg["permission"] = permission
    return {"arguments": list(args), "description": role, "regulated": reg}


def _norm(name, predicate, sign, guard=("top",), over=()):
    return {"norm": {"name": name, "predicate": predicate, "sign": sign, "guard": list(guard),
                     "unless": [], "over": list(over)}}


def between():
    """Review B1: `x_permitted` unspecified with no rules, `a_permitted` "may A if may X" placed
    between the members of the pair, `x_required` "must X if c"."""
    return (_environment({"x_required": _regulated("obligation", "deny", permission="x_permitted"),
                          "x_permitted": _regulated("permission", "unspecified"),
                          "a_permitted": _regulated("permission", "deny", "{0} be audited"),
                          "c": {"arguments": ["act"], "description": "c"}}),
            [_norm("may-a", "a_permitted", True, ["unary", "x_permitted", ["var", 0]]),
             _norm("must-x", "x_required", True, ["unary", "c", ["var", 0]])])


# Loop recheck B1: the second guard of `x_required`, reading `x_permitted` at another row.
ROW_GUARDS = {"exists": (["exists", "act", ["unary", "x_permitted", ["var", 0]]], {}),
              "const": (["unary", "x_permitted", ["const", "k"]], {"k": {"sort": "act", "description": "k"}})}


def rows_close(kind):
    """`x_permitted` unspecified with no rules; `x_required` "must X if c" and "must X if
    `ROW_GUARDS[kind]`". Over acts a and b with `c(a)`, the pair closes `x_permitted(a)` at row
    `a` of `x_required`; its row `b` reads the table before `x_required`, as Lean's `tabK` does,
    so `x_required(b)` is unknown in `table3` whichever row `c` holds on (enumeration settles it)."""
    guard, constants = ROW_GUARDS[kind]
    return (_environment({"x_required": _regulated("obligation", "deny", permission="x_permitted"),
                          "x_permitted": _regulated("permission", "unspecified"),
                          "c": {"arguments": ["act"], "description": "c"}}, constants=constants),
            [_norm("must-x", "x_required", True, ["unary", "c", ["var", 0]]),
             _norm("must-x-2", "x_required", True, guard)])


def rows_situations(kind):
    """The rows-close situations: acts a and b, `c` on one of them, `k` naming a."""
    constants = {"k": "a"} if ROW_GUARDS[kind][1] else {}
    return [{"complete": True, "domains": {"act": ["a", "b"]}, "constants": constants,
             "relations": {"c": [[row]]}} for row in ("a", "b")]


def switch_counterexample(p_default):
    """Review A1, spec 6.3: `x_required` unspecified with no rules, paired with `x_permitted` (deny,
    "may X if may P"); `p_permitted` (`p_default`), "may P if X need not be done"."""
    return (_environment({"x_required": _regulated("obligation", "unspecified", permission="x_permitted"),
                          "x_permitted": _regulated("permission", "deny"),
                          "p_permitted": _regulated("permission", p_default, "{0} be tried")}),
            [_norm("may-x", "x_permitted", True, ["unary", "p_permitted", ["var", 0]]),
             _norm("may-p", "p_permitted", True, ["not", ["unary", "x_required", ["var", 0]]])])


def sources():
    """(name, document, situations) for the norms, soft and rights routes."""
    y = ["unary", "y_permitted", ["var", 0]]
    act = {"complete": True, "domains": {"act": ["a", "b"]}, "constants": {}, "relations": {}}
    items = [
        ("u1", _environment(
            {"csam_generation_permitted": _regulated("permission", "unspecified",
                                                     "{0} generate child sexual abuse material",
                                                     args=("agent",))},
            sorts=("agent",), constants={"claude": {"sort": "agent", "description": "Claude"}}),
         [_norm("no-csam-generation", "csam_generation_permitted", False,
                ("eq", ["var", 0], ["const", "claude"]))],
         [{"complete": True, "domains": {"agent": ["c", "s"]}, "constants": {"claude": "c"}, "relations": {}}]),
        ("u5a", _environment({"x_required": _regulated("obligation", "unspecified", permission="x_permitted"),
                              "x_permitted": _regulated("permission", "deny")}), [], [act]),
        ("u5b", _environment({"x_required": _regulated("obligation", "deny", permission="x_permitted"),
                              "x_permitted": _regulated("permission", "unspecified")}),
         [_norm("must", "x_required", True)], [act]),
        ("u5c", _environment({"x_required": _regulated("obligation", "unspecified", permission="x_permitted"),
                              "x_permitted": _regulated("permission", "unspecified")}), [], [act]),
        ("u6", _environment({"x_required": _regulated("obligation", "deny", permission="x_permitted"),
                             "x_permitted": _regulated("permission", "deny"),
                             "y_permitted": _regulated("permission", "unspecified", "{0} be tried")}),
         [_norm("must-x", "x_required", True, y), _norm("not-x", "x_permitted", False)], [act]),
        ("u7", _environment({"report_required": _regulated("obligation", "deny", "{0} be reported"),
                             "permitted": _regulated("permission", "unspecified")}),
         [_norm("rule-1", "report_required", True, ["unary", "permitted", ["var", 0]])], [act]),
        ("u12", _environment({"x_permitted": _regulated("permission", "deny"),
                              "y_permitted": _regulated("permission", "unspecified", "{0} be tried")}),
         [_norm("r", "x_permitted", True, ["or", y, ["not", y]])], [act]),
        ("b1", *between(), [{**act, "domains": {"act": ["a"]}, "relations": {"c": [["a"]]}}]),
        ("a1-deny", *switch_counterexample("deny"), [{**act, "domains": {"act": ["a"]}}]),
        *((f"b1-rows-{kind}", *rows_close(kind), rows_situations(kind)) for kind in ROW_GUARDS),
        ("a1-unspecified", *switch_counterexample("unspecified"), [{**act, "domains": {"act": ["a"]}}]),
    ]
    for name, raw, units, situations in items:
        yield name, nd.UnspecifiedDocument(Environment(raw), [NormDocument._decode(u) for u in units]), situations
    from ve.softnorms import SoftEnvironment
    soft = _environment({"x_required": _regulated("obligation", "deny", "{0} do x", "x_permitted",
                                                  ("assistant",)),
                         "x_permitted": _regulated("permission", "unspecified", "{0} do x", args=("assistant",))},
                        sorts=("assistant", "user"),
                        profiles=["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"])
    rule = _norm("s", "x_required", True)
    rule["norm"].update(mode="default", exception={"decided_by": "assistant", "sufficient": [],
                                                   "necessary": [], "factors": []})
    yield "u8", nd.UnspecifiedSoftDocument(SoftEnvironment(soft), [rule]), [
        {"complete": True, "domains": {"assistant": ["a"], "user": []}, "constants": {},
         "relations": {"soft__excepted__s": rows}} for rows in ([], [["a"]])]
    from ve.rights import RightsEnvironment
    rights = _environment({"arrest_permitted": _regulated("permission", "unspecified", "{0} arrest {1}",
                                                          args=("state", "person")),
                           "arbitrary": {"arguments": ["state", "person"], "description": "arbitrary",
                                         "verbalisation": "{0} arrests {1} arbitrarily"}},
                          sorts=("state", "person"),
                          profiles=["norm-defaults@0", "norms@0", "relational-fol@0", "rights@0",
                                    "soft-norms@0"])
    rights["vocabulary"]["rights"] = {"holders": ["person"], "bearers": ["state"], "protected": [], "alters": {}}
    units = [{"right": {"name": "liberty", "holder": "person", "guard": ["top"], "lines": [
        {"kind": "claim", "holder_slot": None, "cites": {},
         "norm": {"name": "art9", "predicate": "arrest_permitted", "sign": False,
                  "guard": ["binary", "arbitrary", ["var", 1], ["var", 0]], "unless": [], "over": []}}]}},
             {"limitation": {"name": "l29", "scope": ["liberty"], "kinds": ["claim"], "decided_by": "unstated",
                             "conditions": [{"name": "law", "role": "necessary", "decided_by": None,
                                             "verbalisation": "determined by law"}], "factors": []}}]
    yield "u9", nd.UnspecifiedRightsDocument(RightsEnvironment(rights), units), [
        {"complete": True, "domains": {"state": ["s"], "person": ["p"]}, "constants": {},
         "relations": {"arbitrary": [["s", "p"]], "rights__lim__1": rows, "rights__cond__1": rows}}
        for rows in ([], [["s", "p"]])]


def _closed(formula, sorts):
    return _bind(formula, sorts, binder=Exists)


def _fillings(document, situation):
    """Every filling of the unsaid tables over the situation (the corpus is small)."""
    atoms = [(nd.unsaid_name(p), row) for p in document.unspec
             for row in product(*(situation.domains[s] for s in document.env.predicates[p].arguments))]
    for bits in product((False, True), repeat=len(atoms)):
        filling = {nd.unsaid_name(p): set() for p in document.unspec}
        for (name, row), bit in zip(atoms, bits):
            if bit:
                filling[name].add(row)
        yield {k: frozenset(v) for k, v in filling.items()}


def _values(env, model, formulas):
    evaluator = _Evaluator(env, model, 1_000_000, trace=False)
    return [evaluator.formula(f)[0] for f in formulas]


def rust_fixture_rows():
    rows = []
    for name, document, situations in sources():
        raw_base = document._raw_base()
        base_formulas = [f for _, f in document.fill_premises]
        target_start = len(base_formulas)
        base_formulas += [_closed(f, sorts) for _, sorts, f in document.filled.conflict_targets()]
        reached_start = len(base_formulas)
        base_formulas += [_closed(document.reached(p), document.env.predicates[p].arguments)
                          for p in document.filled.order]
        filled_env = document.filled.env
        layers = [f for _, f in document.filled.premises()]
        for index, raw_situation in enumerate(situations):
            situation = document.situation(raw_situation)
            for number, filling in enumerate(_fillings(document, situation)):
                model = document.with_filling(situation, filling, checked=False)
                admissible = document.fill_valid(situation, filling)
                rows.append({"id": f"{name}-{index}-{number}", "untrusted": True, "kind": "base",
                             "environment": raw_base.to_dict(), "model": model.to_dict(),
                             "formulas": [formula_to_data(raw_base, f, _generated=True) for f in base_formulas],
                             "expected": _values(raw_base, model, base_formulas),
                             "target_start": target_start, "reached_start": reached_start,
                             "admissible": admissible})
                if not admissible:
                    continue
                # E‴ with every regulated table the W1 expansion of this filling.
                data = model.to_dict()
                for p in document.filled.order:
                    sorts = document.env.predicates[p].arguments
                    data["relations"][p] = [
                        list(values) for values in product(*(situation.domains[s] for s in sorts))
                        if document.value(situation, filling, p, values)]
                if hasattr(filled_env, "soft"):
                    stripped = filled_env.to_dict()
                    stripped["vocabulary"].pop("soft", None)
                    stripped["profiles"] = [p for p in stripped["profiles"] if p != "soft-norms@0"]
                    for decl in stripped["vocabulary"]["predicates"].values():
                        decl.pop("instruction_of", None)
                    layer_env = Environment(stripped)
                else:
                    layer_env = filled_env
                try:
                    full = FiniteModel.from_dict(layer_env, {**data, "relations": {
                        k: v for k, v in data["relations"].items() if k in layer_env.predicates}})
                except InvalidModel:
                    continue  # a pair conflict under this filling: no expansion to evaluate
                rows.append({"id": f"{name}-{index}-{number}-layers", "untrusted": True, "kind": "layers",
                             "environment": layer_env.to_dict(), "model": full.to_dict(),
                             "formulas": [formula_to_data(layer_env, f, _generated=True) for f in layers],
                             "expected": _values(layer_env, full, layers)})
    return rows


def fixture_text(rows):
    """One compact row per line."""
    return "[\n" + ",\n".join(json.dumps(row, sort_keys=True, separators=(",", ":"))
                               for row in rows) + "\n]\n"


if __name__ == "__main__":
    RUST_FIXTURES.write_text(fixture_text(rust_fixture_rows()))
