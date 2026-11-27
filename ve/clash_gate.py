# ve-layer: 4 (a refusal-only gate at four developer commands: untrusted Python that can only withhold an answer)
"""Refuse at a clash: no definite answer where two of the text's rules give opposite outcomes for one point.

Row duties-clash-refuse-gate (docs/spec/norm-defaults.md 2.5, "Refusal at a clash"). Two rules clash when they give
opposite outcomes for the same thing: the same regulated predicate at the same individuals ('must' and 'need not',
'may' and 'may not'), or an obligation and its declared permission ('must' and 'may not'). A clash counts when it
happens in a situation the text allows: one where both rules' conditions hold and which is consistent with the
document's facts and its other statements, leaving those two rules out. The clash points are the conflict check's
own (3.1): its targets, `conflict` per predicate and `pairConflict` per pair, read from Lean's elaboration row.

Four commands consult it before they print a definite answer: `ve document readings --conclusion` (a norms document
without a content-bearing reading set), the same with `--assume-no-exception` (a soft-norms document), `ve norms
completions --audit --situation`, and `ve read`. Where it finds a clash the answer is replaced by a refusal naming
the two rules; where it finds none the command prints what it printed before. It never adds or changes an answer.
The search is Python's and untrusted (no Lean line, no verdict of its own): a clash it reports is checked by
evaluating the conflict target on the model it found; a clash it cannot rule out within its budget is also refused
("could not check"), so a budget never turns into an answer.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import copy

from .errors import CheckerUnavailable, ResourceLimit, VEError

# The most unsaid atoms (`unsaid__*` points) a situation's clash check enumerates (2^12 fillings), as spec 2.5's
# MAX_UNSAID_ATOMS for a point's cone; over it the situation is refused as unchecked, never answered.
MAX_UNSAID_ATOMS = 12
REFUSED = "REFUSED"
LEAD = "VE could not decide this."
UNCHECKED = ("VE could not decide this. VE could not check whether the document's rules conflict in a situation the "
             "text allows, so it gives no definite answer.")
# The verbs of the conflict check's own report (ve/norms.py `_conflict_report`).
_VERBS = {"permission": ("permits", "forbids"), "obligation": ("requires", "releases")}


@dataclass(frozen=True)
class Clash:
    """Two rules (or more on one side) that give opposite outcomes at one point, and the sentence that refuses."""
    target: str          # the conflict target: a predicate, or `required->permission`
    tuple: tuple
    plus: tuple          # the rules on the '+' side (the obligation's, on a pair)
    minus: tuple         # the rules on the '-' side (the permission's, on a pair)
    who: tuple           # the tuple as the refusal names it (a constant, else the element or "some <sort>")
    text: str

    @property
    def rules(self) -> list:
        return [*self.plus, *self.minus]

    @property
    def points(self) -> tuple:
        """The points the target reads: the predicate, or both members of a pair, at the tuple."""
        return tuple((p, self.tuple) for p in self.target.split("->"))

    def as_dict(self) -> dict:
        return {"target": self.target, "tuple": list(self.tuple), "who": list(self.who), "rules": self.rules,
                "text": self.text}


class Unchecked(Exception):
    """The check could not rule a clash out within its budget: the caller refuses with UNCHECKED."""


# -- the document and its rules, as the conflict check reads them

def _norm_rows(norms):
    return [n.to_dict() if hasattr(n, "to_dict") else n for n in norms]


def lowered(env_data: dict, norms):
    """The environment and rules the norms chain reads: a soft-norms document's strict rules only (a default rule
    yields to an exception by design, so it is no clash), with the soft fields and the readings profile left out."""
    from .norm_defaults import _profiled
    from .readings_s1 import READINGS
    data = copy.deepcopy(env_data)
    soft = "soft-norms@0" in data["profiles"]
    data["profiles"] = [p for p in data["profiles"] if p not in (READINGS, "soft-norms@0")]
    data["vocabulary"].pop("soft", None)
    rows = []
    for item in _norm_rows(norms):
        norm = item["norm"]
        if soft and norm.get("mode", "strict") != "strict":
            continue
        rows.append({"norm": {k: norm[k] for k in ("name", "predicate", "sign", "guard", "unless", "over")}})
    names = {r["norm"]["name"] for r in rows}
    for r in rows:
        r["norm"]["over"] = [o for o in r["norm"]["over"] if o in names]
    return _profiled(data), rows


def _document(env, norms):
    from .norm_defaults import UnspecifiedDocument
    return UnspecifiedDocument(env, norms)


def _targets(nd):
    from .ast import _Decoder
    return [(t["target"], tuple(t["sorts"]), _Decoder().decode(t["ast"])) for t in nd.elaboration["conflict_targets"]]


def _background(nd):
    """Lean's layered base background over `E‴_base`: the literals' distinctness, then `Fill_T` (the conflict
    check's own premises, ve/readings_verdicts/choice.py `_base_background`)."""
    from .ast import formula_from_data
    base = nd.filled.base_environment()
    asts = ([item["ast"] for item in nd.elaboration["background"] if item["generator"] == "literals"]
            + [item["ast"] for item in nd.elaboration["fill"]])
    return [formula_from_data(base, ast, _generated=True) for ast in asts]


def _sides(nd, target, model, values):
    """The author rules selected at the point on each side of the target (generated fill rules left out)."""
    from .norm_defaults import fill_name
    display = nd.filled._display
    generated = {fill_name(p) for p in nd.unspec}

    def selected(predicate, sign):
        return tuple(r.name for r in display.selected_rules(predicate, model, tuple(values))
                     if r.sign is sign and r.name not in generated)
    if "->" in target:
        required, permitted = target.split("->", 1)
        return selected(required, True), selected(permitted, False)
    return selected(target, True), selected(target, False)


def _named(nd, model, sort, value, situation=False):
    """A constant that denotes the element, else the element itself in a given situation, else "some <sort>"."""
    for name, decl in nd.env.constants.items():
        if model.constants.get(name) == value:
            return decl.verbalisation if type(decl.verbalisation) is str and decl.verbalisation else name
    return str(value) if situation else f"some {sort}"


def _act(nd, predicate, who):
    reg = nd.env.predicates[predicate].regulated
    act = getattr(reg, "act", None)
    if type(act) is str and "{" in act:
        try:
            return f'"{act.format(*who)}" ({predicate})'
        except (IndexError, KeyError):
            pass
    return f"{predicate}({', '.join(who)})"


def _sentence(nd, target, plus, minus, who, situation=False):
    def role(p):
        return nd.env.predicates[p].regulated.role

    def rules(names):
        return " and ".join(f'rule "{n}"' for n in names) if names else None
    if "->" in target:
        required, permitted = target.split("->", 1)
        left = f"{rules(plus) or 'the default'} {'require' if len(plus) > 1 else 'requires'} {_act(nd, required, who)}"
        right = (f"{rules(minus)} {'forbid' if len(minus) > 1 else 'forbids'} it ({permitted})" if minus
                 else f"its permission {permitted} is not given")
        clash = f"{left}, but {right}"
    else:
        yes, no = _VERBS.get(role(target), ("affirms", "denies"))
        clash = f"{rules(plus)} {yes} and {rules(minus)} {no} {_act(nd, target, who)}"
    where = "both apply in this situation" if situation else "the text allows a situation where both apply"
    return f"{LEAD} The document's rules conflict in this situation, so VE cannot answer: {clash}; {where}."


def _clash(nd, target, sorts, model, values, situation=False):
    plus, minus = _sides(nd, target, model, values)
    who = tuple(_named(nd, model, s, v, situation) for s, v in zip(sorts, values))
    return Clash(target, tuple(values), plus, minus, who, _sentence(nd, target, plus, minus, who, situation))


# -- a document: some situation the text allows

def _facts(nd, facts):
    """The document's facts over `E‴_base`; a fact that reads a regulated predicate is left out (the check then
    allows more situations, so it refuses more, never less)."""
    from .ast import formula_from_data
    base = nd.filled.base_environment()
    out = []
    for item in facts:
        ast = item["ast"] if type(item) is dict and "ast" in item else item
        try:
            out.append(formula_from_data(base, ast))
        except VEError:
            continue
    return out


def document_clash(env_data: dict, norms, facts=()) -> Clash | None:
    """The first clash in a situation the document allows (its facts and background hold, a conflict target is
    true), or None when every target is refuted from them. Raises `Unchecked` when neither is found."""
    from .ast import Exists, Not
    from .evaluate import _Evaluator, _Exhausted
    from .norms import _bind
    from .readings_verdicts import BUDGET
    from .search import find_countermodel
    from .entailment import prove_entailment
    env, rows = lowered(env_data, norms)
    if not rows:
        return None
    nd = _document(env, rows)
    base = nd.filled.base_environment()
    premises = _background(nd) + _facts(nd, facts)
    unproved = []
    for target, sorts, formula in _targets(nd):
        found = find_countermodel(base, premises, _bind(Not(formula), sorts),
                                  max_domain_size=BUDGET["max_domain_size"], max_models=BUDGET["max_models"],
                                  max_evaluations=BUDGET["max_evaluations"])
        if found.status == "Found":
            model = found.model
            evaluator = _Evaluator(base, model, BUDGET["max_evaluations"], trace=False)
            try:
                values = next((v for v in product(*(model.domains[s] for s in sorts))
                               if evaluator.formula(formula, tuple(zip(reversed(sorts), reversed(v))))[0]), None)
            except _Exhausted:
                values = None
            if values is not None:
                return _clash(nd, target, sorts, model, values)
        proof = prove_entailment(base, premises, Not(_bind(formula, sorts, Exists)),
                                 max_steps=BUDGET["max_steps"], _background=False)
        if proof.status != "Found":
            unproved.append(target)
    if unproved:
        raise Unchecked(", ".join(unproved))
    return None


def _refusal(clash: Clash | None, unchecked: bool = False) -> dict:
    if unchecked:
        return {"status": "refused", "reason": "clash-unchecked", "text": UNCHECKED}
    return {"status": "refused", "reason": "rules-conflict", "rules": clash.rules, "target": clash.target,
            "who": list(clash.who), "text": clash.text}


def document_refusal(doc) -> dict | None:
    """The refusal `ve document readings --conclusion` prints instead of its answer on a document with rules, or
    None (no clash: the command prints what it printed before)."""
    norms = [u["content"] for u in doc["units"] if u.get("kind") == "norm" and u.get("content") is not None]
    if not norms:
        return None
    facts = [u["content"] for u in doc["units"] if u.get("kind") == "asserted" and u.get("content") is not None]
    try:
        clash = document_clash(doc["environment"].to_dict(), norms, facts)
    except (CheckerUnavailable, ResourceLimit):
        raise
    except (Unchecked, VEError):
        return _refusal(None, unchecked=True)
    return None if clash is None else _refusal(clash)


# -- one complete situation (`ve norms completions --situation`): the points that clash there

def situation_clashes(nd, situation: dict) -> list:
    """Every clash in the given complete situation under some admissible filling of its unsaid points: one per
    target and tuple, with the rules selected under the first filling that makes it true. Raises `Unchecked` over
    MAX_UNSAID_ATOMS unsaid points."""
    from .ast import formula_from_data
    from .evaluate import _Evaluator
    domains = situation["domains"]
    atoms = [(item["name"], values) for item in nd.elaboration["unsaid"]
             for values in product(*(domains[s] for s in item["sorts"]))]
    if len(atoms) > MAX_UNSAID_ATOMS:
        raise Unchecked(f"{len(atoms)} unsaid points")
    base = nd._raw_base()
    fill = [formula_from_data(base, item["ast"], _generated=True) for item in nd.elaboration["fill"]]
    tables = [item["name"] for item in nd.elaboration["unsaid"]]
    targets = _targets(nd)
    found = {}
    for bits in product((False, True), repeat=len(atoms)):
        filling = {name: frozenset() for name in tables}
        for (name, values), on in zip(atoms, bits):
            if on:
                filling[name] = filling[name] | {tuple(values)}
        model = nd.with_filling(situation, filling)
        evaluator = _Evaluator(base, model, 1_000_000, trace=False)
        if not all(evaluator.formula(f, ())[0] for f in fill):
            continue  # not admissible: `Fill_T` fails
        for target, sorts, formula in targets:
            for values in product(*(model.domains[s] for s in sorts)):
                key = (target, tuple(values))
                if key not in found and evaluator.formula(formula, tuple(zip(reversed(sorts), reversed(values))))[0]:
                    found[key] = _clash(nd, target, sorts, model, values, situation=True)
    return [found[k] for k in sorted(found)]


def _regulated_names(ast, regulated, out):
    if type(ast) is str:
        if ast in regulated:
            out.add(ast)
    elif type(ast) in (list, tuple):
        for item in ast:
            _regulated_names(item, regulated, out)
    elif type(ast) is dict:
        for item in ast.values():
            _regulated_names(item, regulated, out)


def dependants(nd) -> dict:
    """Each regulated predicate -> the regulated predicates its outcome reads (guards, carve-outs, the bodies of the
    defined predicates they name, and its pair partner), closed: a status at a point reading a clash rests on how the
    default broke it."""
    regulated = {p for p, d in nd.env.predicates.items() if d.regulated is not None}
    defined = nd.env.definition_entries
    names = regulated | set(defined)
    reads = {p: set() for p in names}
    for item in nd.norms:
        norm = item["norm"]
        _regulated_names([norm["guard"], norm["unless"]], names, reads.setdefault(norm["predicate"], set()))
    for name, body in defined.items():
        _regulated_names(body, names - {name}, reads[name])
    for required, permission, _ in nd.pairs():
        reads[required].add(permission)
        reads[permission].add(required)
    closed = {}
    for p in regulated:
        seen, todo = set(), [p]
        while todo:
            for q in reads.get(todo.pop(), ()):
                if q not in seen:
                    seen.add(q)
                    todo.append(q)
        closed[p] = seen & regulated
    return closed


def point_refusals(nd, situation: dict) -> tuple[list, dict]:
    """The clashes of a situation and, for each regulated predicate and tuple that rests on one, its clash: the
    clash's own points, and every point of a predicate whose outcome reads a clashing predicate (all tuples)."""
    clashes = situation_clashes(nd, situation)
    at = {}
    for clash in clashes:
        for point in clash.points:
            at.setdefault(point, clash)
    by_predicate = {}
    for clash in clashes:
        for p, _ in clash.points:
            by_predicate.setdefault(p, clash)
    reads = dependants(nd)
    refused = dict(at)
    for item in nd.elaboration["reached"]:
        p = item["predicate"]
        hit = next((by_predicate[q] for q in sorted(reads.get(p, ())) if q in by_predicate), None)
        if hit is None:
            continue
        for values in product(*(situation["domains"][s] for s in item["sorts"])):
            refused.setdefault((p, tuple(values)), hit)
    return clashes, refused


def gate_completions(env, units, situation, result: dict) -> dict:
    """`ve norms completions --audit --situation`'s output with every definite status that rests on a clash
    replaced by REFUSED (its sentence beside it) and the situation's clashes listed under `refused`; unchanged where
    the situation has none."""
    from .norm_defaults import UnspecifiedDocument, _profiled
    raw = env.to_dict()

    def refusals(switched=()):
        nd = UnspecifiedDocument(_profiled(raw, switched), units)
        try:
            return point_refusals(nd, situation)
        except Unchecked:
            return None, None
    clashes, refused = refusals()
    out = copy.deepcopy(result)
    for entry in out["completions"]:
        changes = [c for c in entry.get("changes_if_switched", ()) if c["before"].startswith("SETTLED")
                   or c["after"].startswith("SETTLED")]
        after = refusals((entry["predicate"],))[1] if changes else {}
        for change in changes:
            point = (change["predicate"], tuple(change["tuple"]))
            for side, table in (("before", refused), ("after", after)):
                if not change[side].startswith("SETTLED") or (table is not None and point not in table):
                    continue
                change.setdefault("refusal", {})[side] = UNCHECKED if table is None else table[point].text
                change[side] = REFUSED
    if clashes is None:
        out["refused"] = {"status": "refused", "reason": "clash-unchecked", "text": UNCHECKED}
    elif clashes:
        out["refused"] = [c.as_dict() for c in clashes]
    return out


# -- `ve read`: the plain shapes (one kind per rule, one property per word): a clash for one individual

def _clauses(rule):
    """A rule `Every N who is [not] A [and is [not] B] is [not] C.` as (conditions, head): literals (word, true?)."""
    noun, _, neg1, w1, neg2, w2, neg3, w3 = rule.groups
    conditions = [(w1, not neg1)] + ([(w2, not neg2)] if w2 else [])
    return conditions, (w3, not neg3)


def _satisfiable(clauses, fixed):
    """Whether a set of clauses (each a list of literals (word, value)) has a model extending `fixed` (a DPLL)."""
    assignment = dict(fixed)
    pending = [list(c) for c in clauses]
    while True:
        changed = False
        rest = []
        for clause in pending:
            if any(assignment.get(w) is v for w, v in clause):
                continue
            open_ = [(w, v) for w, v in clause if w not in assignment]
            if not open_:
                return False
            if len(open_) == 1:
                assignment[open_[0][0]] = open_[0][1]
                changed = True
            rest.append(clause)
        pending = rest
        if not changed:
            break
    pending = [c for c in pending if not any(assignment.get(w) is v for w, v in c)]
    if not pending:
        return True
    word = next(w for c in pending for w, _ in c if w not in assignment)
    return any(_satisfiable(pending, {**assignment, word: value}) for value in (True, False))


def plain_clash(d) -> str | None:
    """The refusal sentence for a `ve read` text two of whose rules give opposite answers for one individual the
    text allows (a named one where there is one, else any member of the kind), or None."""
    rules = [s for s in d.sentences if s.shape == "rule"]
    facts = {}
    for s in d.sentences:
        if s.shape == "fact":
            name, neg, word = s.groups
            facts.setdefault(name, {})[word] = not neg
    for i, first in enumerate(rules):
        for second in rules[i + 1:]:
            c1, h1 = _clauses(first)
            c2, h2 = _clauses(second)
            if h1[0] != h2[0] or h1[1] == h2[1] or first.groups[0] != second.groups[0]:
                continue
            others = []
            for s in rules:
                if s is first or s is second:
                    continue
                conditions, head = _clauses(s)
                if s.groups[0] == first.groups[0]:
                    others.append([(w, not v) for w, v in conditions] + [head])
            both = [[lit] for lit in c1 + c2]
            names = [n for n, row in d.names.items() if row["kind"] == first.groups[0]]
            who = next((n for n in names if _satisfiable(others + both, facts.get(n, {}))), None)
            if who is None and not _satisfiable(others + both, {}):
                continue
            noun = first.groups[0]
            whom = f"{who} to be one" if who is not None else "one"
            conditions = " and ".join(("" if v else "not ") + w for w, v in dict(c1 + c2).items())
            return (f"{LEAD} The text's rules conflict in this situation, so VE cannot answer: \"{first.text}\" "
                    f"({first.where}) and \"{second.text}\" ({second.where}) give opposite answers for a {noun} who "
                    f"is {conditions}, and the text allows {whom}.")
    return None
