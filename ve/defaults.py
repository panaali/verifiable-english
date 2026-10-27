"""Answers that hold unless an exception applies: the relay of Lean's `defaults-*` rows (docs/spec/defeasible-PLAN.md
2.2 and 2.3, batch DF-1b; spec docs/spec/defeasible.md 7.2).

Lean owns every answer (`lean/VE/Defaults/Wire.lean`, service mode `norm-defaults`): `Dflt_T` and its labels, the
gate, the verdict, the basis, the form, the kept assumptions and the exceptions a situation forces. Python sends the
cases and binds each answer to the request it asked about (R8): every check here is the answer's shape or its binding,
and an answer that fails one is `CheckerUnavailable`, never a verdict of Python's.

`ask` is the two questions of `ve document readings --assume-no-exception`: the strict question first (Lean's layered
`norm-defaults-certificate`), and the default question only when the strict one has no certificate, with the strict
countermodel the search found sent as `strict_model`. The search is an untrusted generator, as readings' is: Python's
prover and model search run on the formulas of Lean's elaboration rows (`defaults-elaborate` and the layered
`norm-defaults-elaborate`), and Lean checks every certificate and model they find.
"""
from __future__ import annotations

from .errors import CheckerUnavailable

MODE = "norm-defaults"
# The search's budget: the prover's steps and the model search's largest domain (an exhausted search sends nothing).
MAX_STEPS = 20_000
MAX_DOMAIN = 2


def _unbound(what):
    return CheckerUnavailable(f"CheckerUnavailable: Lean's answer is not an answer to the defaults request ({what})")


def run(case):
    """Lean's row for one case, held to its shape: a rejection raises Lean's diagnostic (`relay.decide`)."""
    from .backends import relay
    from .backends.service_schema import Invalid, check_row
    [row] = relay.decide(MODE, [case])
    try:
        check_row(MODE, row, case, 0)
    except Invalid as error:
        raise _unbound(f"shape: {error}") from None
    if row.get("id") != case["id"]:
        raise _unbound("id")
    return row


# -- the binding (R8): every name, entity and index an answer gives is the request's

def _rules(case):
    """The request's rules by name: `{name: norm object}`."""
    return {item["norm"]["name"]: item["norm"] for item in case["norms"]}


def _sorts(case, rule):
    """The sorts of a rule's act (its regulated predicate's arguments), as the request declares them."""
    return case["environment"]["vocabulary"]["predicates"][rule["predicate"]]["arguments"]


def _decider(case, rule):
    """Who decides a rule's exception in the request: its own `decided_by`, else the source's default decider."""
    soft = case["environment"]["vocabulary"].get("soft") or {}
    return (rule.get("exception") or {}).get("decided_by") or soft.get("exception_decider") or "unstated"


def _entities(witness):
    """Every entity of a request's model (`{"model": {"domains": ...}}`), by sort."""
    return {sort: set(ids) for sort, ids in witness["model"]["domains"].items()}


def _in_model(rows, witness, what):
    """Every entity of a situation's rows is one of the request's model."""
    known = set().union(*_entities(witness).values())
    if any(value not in known for row in rows for value in row):
        raise _unbound(what)


def _tuple(case, rule, values, witness, what):
    """A tuple of a rule's act: its arity and sorts, each entity in the request's model with that sort."""
    sorts, entities = _sorts(case, rule), _entities(witness)
    if len(values) != len(sorts) or any(v not in entities.get(s, ()) for s, v in zip(sorts, values)):
        raise _unbound(what)


def _situation(row, witness):
    if "situation" in row:
        _in_model([r for rows in row["situation"]["filling"].values() for r in rows], witness, "situation")


def bind_elaborate(case, row):
    """`default_premises` under distinct labels; `coherence_targets` distinct pairs of two declared rules."""
    labels = [label for label, _ in row["default_premises"]]
    pairs = [(m, n) for m, n, _ in row["coherence_targets"]]
    rules = _rules(case)
    if len(set(labels)) != len(labels):
        raise _unbound("default premises")
    if len(set(pairs)) != len(pairs) or any(m == n or m not in rules or n not in rules for m, n in pairs):
        raise _unbound("coherence targets")
    return row


def bind_coherence(case, row, targets):
    """`pairs` are `coherence_targets`, one to one and in order; a collision names one of them, at a tuple of its
    first rule's act in the collision's model, with deciders of its two rules."""
    pairs = [[m, n] for m, n, _ in targets]
    if [entry["rules"] for entry in row["pairs"]] != pairs:
        raise _unbound("pairs")
    if "collision" in row:
        collision, witness = row["collision"], case.get("collision")
        if witness is None or collision["rules"] not in pairs or collision["rules"] != witness["rules"]:
            raise _unbound("collision rules")
        rules = [_rules(case)[name] for name in collision["rules"]]
        _tuple(case, rules[0], collision["tuple"], witness, "collision tuple")
        named = {_decider(case, rule) for rule in rules} | {"unstated"}
        if not 1 <= len(collision["deciders"]) <= 2 or not set(collision["deciders"]) <= named:
            raise _unbound("collision deciders")
        _situation(row, witness)
    return row


def bind_certificate(case, row, labels):
    """`basis`, `form` and `assumptions` exactly with FOLLOWS; each assumption, once, a label of the same source's
    `default_premises`; `needs` only when the request carried a `strict_model`."""
    follows = row["verdict"] == "FOLLOWS"
    if any((key in row) != follows for key in ("basis", "form", "assumptions")) or ("reason" in row) == follows:
        raise _unbound("verdict")
    if follows:
        if len(set(row["assumptions"])) != len(row["assumptions"]) or not set(row["assumptions"]) <= set(labels):
            raise _unbound("assumptions")
        if row["basis"] == "needs" and "strict_model" not in case:
            raise _unbound("basis")
    return row


def bind_model(case, row):
    """With DOES-NOT-FOLLOW, the situation is in the request's model, and each `forced` entry names a default rule of
    the request, a condition index below its number of stated conditions and a tuple of its act in that model."""
    if ("situation" in row) != (row["verdict"] == "DOES-NOT-FOLLOW") or ("forced" in row) != ("situation" in row):
        raise _unbound("verdict")
    rules = _rules(case)
    for entry in row.get("forced", ()):
        rule = rules.get(entry["rule"])
        if rule is None or rule.get("mode") != "default":
            raise _unbound("forced rule")
        if entry["condition"] >= len((rule.get("exception") or {}).get("sufficient", ())):
            raise _unbound("forced condition")
        _tuple(case, rule, entry["tuple"], case["model"], "forced tuple")
    _situation(row, case["model"])
    return row


def answer(case, labels=(), targets=()):
    """Lean's bound answer to a `defaults-*` case: `labels` and `targets` are the same source's `defaults-elaborate`
    rows (`default_premises` labels, `coherence_targets`), which a certificate's and a coherence answer bind to."""
    row = run(case)
    kind = case["kind"]
    try:
        if kind == "defaults-elaborate":
            return bind_elaborate(case, row)
        if kind == "defaults-coherence":
            return bind_coherence(case, row, targets)
        if kind == "defaults-certificate":
            return bind_certificate(case, row, labels)
        return bind_model(case, row)
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise _unbound(f"{type(error).__name__}: {error}") from None


# -- the two questions (plan DF-1b), with the untrusted search

class _Search:
    """Python's prover and model search on Lean's formulas for one source: `X` (the layered row's `soft` and
    `rights`), `Dflt_T` (`defaults-elaborate`), `Fill_T` and the filled layers, decoded over `E‴` (the source with
    each `unspecified` completion read as `deny`, the unsaid tables and the soft decisions declared, as the readings
    route's filled choice documents read them)."""

    def __init__(self, base, layered, dflt):
        from .ast import formula_from_data
        from .environment import Environment
        from .norm_defaults import _placeholder
        from .softnorms import SoftEnvironment
        raw = _placeholder(base["environment"])
        self.tables = [item["name"] for item in layered["unsaid"]]
        for item in layered["unsaid"]:
            raw["vocabulary"]["predicates"][item["name"]] = {"arguments": item["sorts"],
                                                             "description": item["description"]}
        declared = layered["base_environment"]["vocabulary"]["predicates"]
        for name, declaration in declared.items():
            raw["vocabulary"]["predicates"].setdefault(name, declaration)
        self.base = set(declared) - set(self.tables)
        self.env = SoftEnvironment(raw, generated=True)
        self.source = Environment(base["environment"])
        self.formula = lambda ast: formula_from_data(self.env, ast, _generated=True)
        self.X = [self.formula(item["ast"]) for item in (*layered["soft"], *layered["rights"])]
        self.dflt = [self.formula(ast) for _, ast in dflt["default_premises"]]
        self.fill = [self.formula(item["ast"]) for item in layered["fill"]]
        self.layers = [self.formula(item["ast"]) for item in layered["premises"]]

    def certificate(self, X, gamma, phi):
        """A certificate of `premisesX U X Γ ⊢ φ` bound to the source, or None within the budget."""
        from .norm_defaults_route import filled_certificate
        from .readings_verdicts.choice import _FilledView
        view = _FilledView(self.source, self.env, self.fill, self.layers, X)
        return filled_certificate(view, gamma, phi, max_steps=MAX_STEPS)

    def model(self, X, gamma, phi):
        """A model of `X`, `Fill_T`, the layers and Γ where `φ` fails, as a request carries it (its base and its
        filling apart), or None within the budget."""
        from .search import find_countermodel
        found = find_countermodel(self.env, [*X, *self.fill, *self.layers, *gamma], phi, max_domain_size=MAX_DOMAIN)
        if found.status != "Found":
            return None
        data = found.model.to_dict()
        relations = data["relations"]
        return {"model": {**data, "relations": {k: v for k, v in relations.items() if k in self.base}},
                "filling": {name: relations.get(name, []) for name in self.tables}}


def ask(environment, norms, premises, conclusion):
    """The strict question, then, when it has no certificate, the default question (plan DF-1b): `{"question":
    "strict", "valid": true}` from Lean's layered certificate check, or `{"question": "default", "kind", "answer"}`
    with Lean's bound `defaults-certificate` or `defaults-model` row (without `id` and `status`)."""
    from .ast import Bottom
    base = {"environment": environment, "norms": norms}
    elaborated = answer({"id": "defaults-elaborate", "kind": "defaults-elaborate", **base})
    layered = run({"id": "norm-defaults-elaborate", "kind": "norm-defaults-elaborate", **base})
    search = _Search(base, layered, elaborated)
    gamma, phi = [search.formula(p) for p in premises], search.formula(conclusion)
    question = {**base, "premises": premises, "conclusion": conclusion}
    strict = search.certificate(search.X, gamma, phi)
    if strict is not None and run({"id": "strict", "kind": "norm-defaults-certificate", **question,
                                   "certificate": strict})["valid"] is True:
        return {"question": "strict", "valid": True}
    X = [*search.X, *search.dflt]
    certificate = search.certificate(X, gamma, phi)
    countermodel = None if certificate is not None else search.model(X, gamma, phi)
    if countermodel is not None:
        case = {"id": "defaults", "kind": "defaults-model", **question, "model": countermodel}
    else:
        evidence = {"certificate": certificate, "model": search.model(X, gamma, Bottom()),
                    "strict_model": search.model(search.X, gamma, phi)}
        case = {"id": "defaults", "kind": "defaults-certificate", **question,
                **{key: value for key, value in evidence.items() if value is not None}}
    row = answer(case, [label for label, _ in elaborated["default_premises"]], elaborated["coherence_targets"])
    return {"question": "default", "kind": case["kind"],
            "answer": {key: value for key, value in row.items() if key not in ("id", "status")}}
