"""Answers that hold unless an exception applies: the relay of Lean's `defaults-*` rows (docs/spec/defeasible-PLAN.md
2.2 and 2.3, batch DF-1b; spec docs/spec/defeasible.md 7.2).

Lean owns every answer (`lean/VE/Defaults/Wire.lean`, service mode `norm-defaults`): `Dflt_T` and its labels, the
gate, the verdict, the basis, the form, the kept assumptions and the exceptions a situation forces. Python sends the
cases and binds each answer to the request it asked about (R8): every check here is the answer's shape or its binding,
and an answer that fails one is `CheckerUnavailable`, never a verdict of Python's.

The relay accepts and shows a row on one condition only: Lean's reply is a row of the mode's shape for this case
(`run`), and every member the binding names is the value the request gives it (the closed list of R11's D1, `bind_*`:
an equality, such as the collision's deciders and `_decider`'s fallback chain, or membership in the request's own
list). Everything else is refused: a shape fault or `CheckerUnavailable`. `ask` shows the strict answer only when
Lean's layered check says `valid` is true.

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
    """Lean's row for one case, held to its shape, which binds its `id` to the case's: a rejection raises Lean's
    diagnostic (`relay.decide`)."""
    from .backends import relay
    from .backends.service_schema import Invalid, check_row
    [row] = relay.decide(MODE, [case])
    try:
        check_row(MODE, row, case, 0)
    except Invalid as error:
        raise _unbound(f"shape: {error}") from None
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


def _deciders(case, rules):
    """The deciders a collision of two rules names (Lean's `giveWayDeciders`): one when the two rules' deciders are the
    same, otherwise both, in pair order."""
    first, second = (_decider(case, rule) for rule in rules)
    return [first] if first == second else [first, second]


def _bind_decider_names(case, names, has_decisions):
    """R8: each Lean name occurs in this source, once; a row for decisions is not empty."""
    rules = _rules(case).values()
    soft = case["environment"]["vocabulary"].get("soft") or {}
    available = {"unstated", *(_decider(case, rule) for rule in rules if rule.get("mode") == "default"),
                 *(party for rule in _rules(case).values() for party in rule.get("alterable", ())),
                 (soft.get("outranking") or {}).get("decided_by") or "unstated"}
    if bool(names) != bool(has_decisions) or len(names) != len(set(names)) or any(n not in available for n in names):
        raise _unbound("deciders")


def _entities(witness):
    """Every entity of a request's model (`{"model": {"domains": ...}}`), by sort."""
    return {sort: set(ids) for sort, ids in witness["model"]["domains"].items()}


def _tuple(case, rule, values, witness, what):
    """A tuple of a rule's act: its arity and sorts, each entity in the request's model with that sort."""
    sorts, entities = _sorts(case, rule), _entities(witness)
    if len(values) != len(sorts) or any(v not in entities.get(s, ()) for s, v in zip(sorts, values)):
        raise _unbound(what)


def _situation(case, row, witness):
    """The displayed filling has exactly the tables of the request's unspecified regulated predicates.

    Each table uses its predicate's declared argument sorts and the request model's domains. Lean emits all tables,
    including empty ones (`witnessRow`); its filling decoder accepts an omitted input table as empty.
    """
    if "situation" in row:
        predicates = case["environment"]["vocabulary"]["predicates"]
        tables = {"unsaid__" + name: predicate["arguments"] for name, predicate in predicates.items()
                  if (predicate.get("regulated") or {}).get("default") == "unspecified"}
        filling = row["situation"]["filling"]
        if set(filling) != set(tables):
            raise _unbound("situation")
        entities = _entities(witness)
        for name, rows in filling.items():
            sorts = tables[name]
            for values in rows:
                if len(values) != len(sorts):
                    raise _unbound("situation")
                for sort, value in zip(sorts, values):
                    if value not in entities.get(sort, ()):
                        raise _unbound("situation")


def bind_elaborate(case, row, source):
    """`default_premises` under distinct labels; `coherence_targets` the colliding pairs of the source (`source`,
    `soft_source`), in their order."""
    labels = [label for label, _ in row["default_premises"]]
    if len(set(labels)) != len(labels):
        raise _unbound("default premises")
    if [[m, n] for m, n, _ in row["coherence_targets"]] != source["pairs"]:
        raise _unbound("coherence targets")
    _bind_decider_names(case, row["deciders"], labels)
    return row


def bind_coherence(case, row, targets):
    """`pairs` are `coherence_targets`, one to one and in order; a collision names one of them, at a tuple of its
    first rule's act in the collision's model, with exactly the deciders of its two rules (`_deciders`)."""
    pairs = [[m, n] for m, n, _ in targets]
    if [entry["rules"] for entry in row["pairs"]] != pairs:
        raise _unbound("pairs")
    if "collision" in row:
        collision, witness = row["collision"], case.get("collision")
        if witness is None or collision["rules"] not in pairs or collision["rules"] != witness["rules"]:
            raise _unbound("collision rules")
        rules = [_rules(case)[name] for name in collision["rules"]]
        _tuple(case, rules[0], collision["tuple"], witness, "collision tuple")
        if collision["deciders"] != _deciders(case, rules):
            raise _unbound("collision deciders")
        _situation(case, row, witness)
    return row


def bind_certificate(case, row, labels):
    """`basis`, `form` and `assumptions` exactly with FOLLOWS; the assumptions are labels of the same source's
    `default_premises`, each once and in their order, none exactly with `strict`; `needs` only when the request
    carried a `strict_model`; a reason is not empty."""
    follows = row["verdict"] == "FOLLOWS"
    if any((key in row) != follows for key in ("basis", "form", "assumptions", "deciders")) or ("reason" in row) == follows:
        raise _unbound("verdict")
    if not follows and not row["reason"]:
        raise _unbound("reason")
    if follows:
        _bind_decider_names(case, row["deciders"], labels)
        if (row["assumptions"] != [label for label in labels if label in row["assumptions"]] or
                (row["basis"] == "strict") != (row["assumptions"] == [])):
            raise _unbound("assumptions")
        if row["basis"] == "needs" and "strict_model" not in case:
            raise _unbound("basis")
    return row


def bind_model(case, row, source):
    """With DOES-NOT-FOLLOW, the situation is in the request's model, and each `forced` entry names a default rule of
    the request, a condition index below its number of stated conditions and a tuple of its act in that model; the
    entries are the rows of the default rules' exception tables (`source`, `soft_source`) in the request's model, each
    once, in rule order and then the model's entity order."""
    if ("situation" in row) != (row["verdict"] == "DOES-NOT-FOLLOW") or ("forced" in row) != ("situation" in row):
        raise _unbound("verdict")
    rules, forced = _rules(case), row.get("forced", [])
    for entry in forced:
        rule = rules.get(entry["rule"])
        if rule is None or rule.get("mode") != "default":
            raise _unbound("forced rule")
        if entry["condition"] >= len((rule.get("exception") or {}).get("sufficient", ())):
            raise _unbound("forced condition")
        _tuple(case, rule, entry["tuple"], case["model"], "forced tuple")
    domains, relations = case["model"]["model"]["domains"], case["model"]["model"]["relations"]
    held = {(name, tuple(values)) for name, table in source["excepted"].items()
            if rules.get(name, {}).get("mode") == "default" for values in relations.get(table, ())}
    if row["verdict"] == "DOES-NOT-FOLLOW" and {(e["rule"], tuple(e["tuple"])) for e in forced} != held:
        raise _unbound("forced exceptions")
    order = [(list(rules).index(e["rule"]), [domains[s].index(v) for s, v in zip(_sorts(case, rules[e["rule"]]),
                                                                                e["tuple"])]) for e in forced]
    if order != sorted(order) or len({repr(o) for o in order}) != len(order):
        raise _unbound("forced order")
    _situation(case, row, case["model"])
    return row


def answer(case, labels=(), targets=(), source=None):
    """Lean's bound answer to a `defaults-*` case: `labels` and `targets` are the same source's `defaults-elaborate`
    rows (`default_premises` labels, `coherence_targets`), which a certificate's and a coherence answer bind to;
    `source` its colliding pairs and exception tables (`soft_source`), which an elaboration and a model bind to."""
    row = run(case)
    kind = case["kind"]
    try:
        if kind in ("defaults-elaborate", "defaults-model") and source is None:
            source = soft_source(case)
        if kind == "defaults-elaborate":
            return bind_elaborate(case, row, source)
        if kind == "defaults-coherence":
            return bind_coherence(case, row, targets)
        if kind == "defaults-certificate":
            return bind_certificate(case, row, labels)
        return bind_model(case, row, source)
    except (KeyError, TypeError, ValueError, IndexError) as error:
        raise _unbound(f"{type(error).__name__}: {error}") from None


def soft_source(case):
    """The request's source as Lean's soft elaboration gives it (`SoftNormDocument`, which binds it to the source):
    its colliding pairs, in order, and each rule's exception table."""
    from .softnorms import SoftEnvironment, SoftNormDocument
    document = SoftNormDocument(SoftEnvironment(case["environment"]), case["norms"])
    return {"pairs": [[a.core.name, b.core.name] for a, b in document.collisions],
            "excepted": {key[1]: name for key, name in document.decision_by_key.items() if key[0] == "excepted"}}


# -- the two questions (plan DF-1b), with the untrusted search

class _Search:
    """Python's prover and model search on Lean's formulas for one source: `X` (the layered row's `soft` and
    `rights`), `Dflt_T` (`defaults-elaborate`), `Fill_T` and the filled layers, decoded over `E‴` (the source with
    each `unspecified` completion read as `deny`, the unsaid tables and the soft decisions declared, as the readings
    route's filled choice documents read them)."""

    def __init__(self, base, layered, dflt, budget=None):
        from .ast import formula_from_data
        from .environment import Environment
        from .norm_defaults import _placeholder
        from .softnorms import SoftEnvironment
        # A readings request supplies its own search limits. Keep the mapping live so a
        # cached free gate cannot hide a later exhausted query budget.
        self.budget = budget
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
        # The gate's premises (Lean's `bindPair`): the base background, `Exc_T` (the soft premises before `Coh_T`,
        # which are the coherence targets' premises, last and in their order), `R`, `Dflt_T` and `Fill_T`.
        self.targets = dflt["coherence_targets"]
        soft, k = [item["ast"] for item in layered["soft"]], len(self.targets)
        exc = soft[:len(soft) - k] if soft[len(soft) - k:] == [ast for _, _, ast in self.targets] else None
        self.gate = None if exc is None else [
            *(item["ast"] for item in layered["background"] if item["generator"] == "literals"), *exc,
            *(item["ast"] for item in layered["rights"]), *(ast for _, ast in dflt["default_premises"]),
            *(item["ast"] for item in layered["fill"])]

    def coherence(self):
        """The request's gate evidence: `coherence`, each colliding pair with the certificate of its coherence premise
        the prover finds (bound as `bindPair` binds it), and a `collision` where some pair's premise fails in a model
        of the gate's premises; each None when there is nothing to send."""
        from .entailment import prove_entailment
        from .norm_defaults_route import _source_binding
        from .readings_verdicts.choice import _FilledView
        if not self.targets or self.gate is None:
            return {}
        premises = [self.formula(ast) for ast in self.gate]
        view = _FilledView(self.source, self.env, (), ())
        pairs, collision = [], None
        for m, n, ast in self.targets:
            entry, target = {"rules": [m, n]}, self.formula(ast)
            proof = prove_entailment(self.env, premises, target,
                                    max_steps=self.budget["max_steps"] if self.budget is not None else MAX_STEPS,
                                    _background=False)
            if proof.status == "Found":
                entry["certificate"] = {**proof.certificate, **_source_binding(view, (), target, listed=premises)}
            elif collision is None and (found := self.model(premises, [], target, layered=False)):
                collision = {**found, "rules": [m, n]}
            pairs.append(entry)
        return {"coherence": pairs, **({"collision": collision} if collision else {})}

    def certificate(self, X, gamma, phi):
        """A certificate of `premisesX U X Γ ⊢ φ` bound to the source, or None within the budget."""
        from .norm_defaults_route import filled_certificate
        from .readings_verdicts.choice import _FilledView
        view = _FilledView(self.source, self.env, self.fill, self.layers, X)
        return filled_certificate(view, gamma, phi,
                                  max_steps=self.budget["max_steps"] if self.budget is not None else MAX_STEPS)

    def model(self, X, gamma, phi, layered=True):
        """A model of `X`, `Fill_T`, the layers and Γ (of `X` and Γ alone when not `layered`) where `φ` fails, as a
        request carries it (its base and its filling apart), or None within the budget."""
        from .search import find_countermodel
        premises = [*X, *self.fill, *self.layers, *gamma] if layered else [*X, *gamma]
        limits = ({"max_domain_size": self.budget["max_domain_size"], "max_models": self.budget["max_models"],
                   "max_evaluations": self.budget["max_evaluations"]} if self.budget is not None else
                  {"max_domain_size": MAX_DOMAIN})
        found = find_countermodel(self.env, premises, phi, **limits)
        if found.status != "Found":
            return None
        data = found.model.to_dict()
        relations = data["relations"]
        return {"model": {**data, "relations": {k: v for k, v in relations.items() if k in self.base}},
                "filling": {name: relations.get(name, []) for name in self.tables}}


def ask(environment, norms, premises, conclusion):
    """The strict question, then, when it has no certificate, the default question (plan DF-1b): `{"question":
    "strict", "valid": true}` from Lean's layered certificate check, or `{"question": "default", "kind", "answer"}`
    with Lean's bound `defaults-certificate` or `defaults-model` row (without `id` and `status`), the gate's
    `coherence` row when the source has colliding pairs, and the `english` of both (`ve.defaults_english`)."""
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
        out = {"question": "strict", "valid": True}
        if elaborated["default_premises"]:
            from .defaults_english import strict_sentence
            out.update(deciders=elaborated["deciders"], english=[strict_sentence(elaborated["deciders"])])
        return out
    X = [*search.X, *search.dflt]
    gate = search.coherence()
    certificate = search.certificate(X, gamma, phi)
    countermodel = None if certificate is not None else search.model(X, gamma, phi)
    if countermodel is not None:
        case = {"id": "defaults", "kind": "defaults-model", **question, "model": countermodel}
    else:
        evidence = {"certificate": certificate, "model": search.model(X, gamma, Bottom()),
                    "strict_model": search.model(search.X, gamma, phi), **gate}
        case = {"id": "defaults", "kind": "defaults-certificate", **question,
                **{key: value for key, value in evidence.items() if value is not None}}
    from .defaults_english import sentences
    targets = elaborated["coherence_targets"]
    row = answer(case, [label for label, _ in elaborated["default_premises"]], targets)
    out = {"question": "default", "kind": case["kind"], "answer": _shown(row)}
    english = sentences(case, row)
    if targets:
        coherence = {"id": "coherence", "kind": "defaults-coherence", **base, **gate}
        row = answer(coherence, targets=targets)
        out["coherence"] = _shown(row)
        english += sentences(coherence, row)
    out["english"] = english
    return out


def _shown(row):
    """What the relay shows of a bound row: all of it but `id`, `status` and the situation, which is the request's
    own model and filling (`situationJson` shows the unsaid tables of the situation the request sent)."""
    return {key: value for key, value in row.items() if key not in ("id", "status", "situation")}
