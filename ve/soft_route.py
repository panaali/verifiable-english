"""Python entry point for the proved soft-norm admission route."""
from __future__ import annotations

from .errors import CheckerUnavailable, VEError
from .softnorms import (SoftEnvironment, SoftNormDocument, bind_selected, bind_soft_elaboration,  # noqa: F401
                        selected_at as _selected_at)
from .backends.soft_relay import run as _run, wire as _wire


def elaborate_soft_document(soft_document: SoftNormDocument):
    """Return the bound Lean soft elaboration."""
    env = soft_document.env
    norms = [rule.to_dict() for rule in soft_document.rules]
    elaborated = _run({"id": "soft-elaborate", "kind": "soft-elaborate",
                       "environment": env.to_dict(), "norms": norms})
    vocabulary = env.to_dict()['vocabulary']
    bind_soft_elaboration(elaborated, norms, vocabulary['predicates'],
                          soft=vocabulary.get('soft', {}), environment=env.to_dict())
    return elaborated


def classify_soft_pairs(soft_document: SoftNormDocument, *, pairs=None):
    """Replay the pair certificates or witnesses over the regenerated base."""
    elaborated = elaborate_soft_document(soft_document)
    row = _run({"id": "soft-pairs", "kind": "soft-pairs",
                 "environment": soft_document.env.to_dict(),
                 "norms": [rule.to_dict() for rule in soft_document.rules],
                 "pairs": {} if pairs is None else pairs})
    try:
        expected = [(entry['pair'], entry['label']) for entry in elaborated['colliding_pairs']]
        actual = [(entry['pair'], entry['label']) for entry in row['pairs']]
        if actual != expected:
            raise ValueError('missing or extra classified pair')
        discharged = [entry['label'] for entry in row['pairs']
                      if entry['status'] in ('RANK-RESOLVED', 'DISJOINT')]
        open_labels = [entry['label'] for entry in row['pairs']
                       if entry['status'] not in ('RANK-RESOLVED', 'DISJOINT')]
        if row['discharged'] != discharged or row['weighing_points'] != open_labels:
            raise ValueError('unbound pair classification labels')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft pairs are not bound to the request: {error}') from error
    return row


def _slot_case(kind, case, facts, facts_model):
    """The case of the soft kind `kind`, or of its slot twin with `facts` (kb-3): `facts`, closed formulas over the
    regenerated base vocabulary, sent as given for Lean to decode or refuse; `facts_model`, the base model Lean asks
    for beside non-empty facts."""
    if facts is None:
        if facts_model is not None:
            raise VEError("InvalidInput: a facts_model needs facts")
        return {"id": kind, "kind": kind, **case}
    slot = kind.replace("soft-", "slot-", 1)
    case = {"id": slot, "kind": slot, **case, "facts": list(facts)}
    if facts_model is not None:
        case["facts_model"] = facts_model.to_dict() if hasattr(facts_model, "to_dict") else facts_model
    return case


def bind_facts(row, case):
    """A slot answer's `facts` is the number of facts the case SENT (never a count the answer brings with it); a soft
    answer has none."""
    if "facts" not in case:
        if "facts" in row:
            raise ValueError('a soft answer names facts')
        return
    if type(row.get("facts")) is not int or type(case["facts"]) is not list or row["facts"] != len(case["facts"]):
        raise ValueError('facts count is not the number of facts sent')


def check_soft_conflict(soft_document: SoftNormDocument, *, packages=None, witness=None,
                        pairs=None, coherent_model=None, budget=None, facts=None, facts_model=None):
    """Replay a conflict package or finite witness against the soft route; with `facts` (a list, possibly empty),
    the `slot-conflict` kind relative to them (and `facts_model` with non-empty facts)."""
    elaborated = elaborate_soft_document(soft_document)
    case = _slot_case("soft-conflict", {"environment": soft_document.env.to_dict(),
                                        "norms": [rule.to_dict() for rule in soft_document.rules]}, facts, facts_model)
    if witness is not None:
        case["witness"] = witness
    else:
        case["packages"] = {} if packages is None else packages
        case["pairs"] = {} if pairs is None else pairs
        if coherent_model is not None:
            case["coherent_model"] = coherent_model
        if budget is not None:
            case["budget"] = budget
    row = _run(case)
    try:
        bind_conflict(row, case, elaborated, budget)
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft conflict is not bound to the request: {error}') from error
    return row


def bind_conflict(row, case, elaborated, budget=None):
    """A `soft-conflict` or `slot-conflict` row bound to its case and to the document's elaboration."""
    targets = [entry['target'] for entry in elaborated['conflict_targets']]
    # Run.lean: a conflict-free verdict is conditional on open coherence premises only.
    labels = {entry['label'] for entry in elaborated['colliding_pairs'] if not entry['comparable']}
    if row['targets'] != targets:
        raise ValueError('unbound conflict targets')
    if 'conditional_on' in row and (len(row['conditional_on']) != len(set(row['conditional_on'])) or
                                     not set(row['conditional_on']) <= labels):
        raise ValueError('unbound conflict conditional labels')
    if budget is not None and row['budget'] != budget:
        raise ValueError('unbound conflict budget')
    bind_facts(row, case)


def check_soft_certificate(soft_document: SoftNormDocument, *, premises, conclusion, certificate, pairs=None,
                           facts=None, facts_model=None):
    """Lean's `soft-certificate` answer for `certificate`, a certificate of `conclusion` from `background′`, the layer
    premises and `premises` over `E′`; with `facts` (a list, possibly empty), the `slot-certificate` kind, whose
    certificate premises are `background′`, the facts, the layer premises and `premises` (and `facts_model` with
    non-empty facts). The answer is checked for its schema and its binding only; anything else is CheckerUnavailable,
    and Lean's refusal is raised as its diagnostic."""
    elaborated = elaborate_soft_document(soft_document)
    case = _slot_case("soft-certificate", {"environment": soft_document.env.to_dict(),
                                           "norms": [rule.to_dict() for rule in soft_document.rules],
                                           "premises": list(premises), "conclusion": conclusion,
                                           "certificate": certificate, "pairs": {} if pairs is None else pairs},
                      facts, facts_model)
    row = _run(case)
    try:
        return bind_certificate(row, case, elaborated)
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft certificate is not bound to the request: {error}') from error


def bind_certificate(row, case, elaborated):
    """A `soft-certificate` or `slot-certificate` row bound to its case: its id; its counts, Lean's `background′` and
    layer premises (the document's elaboration) and the facts SENT, which with the premises sent are the
    certificate's premise list, one meaning id each; its coherence labels open ones of the document, once, and none
    beside an invalid certificate."""
    fields = {"id", "status", "valid", "background", "layers", "conditional_on"} | ({"facts"} if "facts" in case else set())
    if type(row) is not dict or set(row) != fields:
        raise ValueError('unexpected soft certificate fields')
    if row["id"] != case["id"] or row["status"] != "ok" or type(row["valid"]) is not bool:
        raise ValueError('mistyped soft certificate')
    if type(row["background"]) is not int or row["background"] != len(elaborated["background"]):
        raise ValueError('background count is not the elaboration\'s')
    if type(row["layers"]) is not int or row["layers"] != len(elaborated["premises"]):
        raise ValueError('layer count is not the elaboration\'s')
    bind_facts(row, case)
    listed = row["background"] + len(case.get("facts", [])) + row["layers"] + len(case["premises"])
    if listed != len(case["certificate"]["premise_meaning_ids"]):
        raise ValueError('the counts are not the certificate\'s premise list')
    conditional, labels = row["conditional_on"], {entry['label'] for entry in elaborated['colliding_pairs']
                                                  if not entry['comparable']}
    if (type(conditional) is not list or not all(type(x) is str for x in conditional)
            or len(conditional) != len(set(conditional)) or not set(conditional) <= labels
            or (conditional and not row["valid"])):
        raise ValueError('unbound certificate conditional labels')
    return {key: value for key, value in row.items() if key not in ("id", "status")}


def selected_at(soft_document: SoftNormDocument, model, queries):
    """Lean's `soft-selected` answer for `queries` of the base `model` (`ve.softnorms.selected_at`, the one owner
    of the request and its binding), sent through this route's runner."""
    return _selected_at(soft_document, model, queries, run=_run)


def admit_soft_document(environment, document, *, soft_document=None):
    """Ask Lean about the source before constructing Python display containers."""
    active = [u["content"] for u in document["units"]
              if u["kind"] == "norm" and type(u.get("content")) is dict
              and "norm" in u["content"]]
    source = environment.to_dict() if isinstance(environment, SoftEnvironment) else environment
    _run({"id": "soft-elaborate", "kind": "soft-elaborate",
          "environment": _wire(source), "norms": _wire(active)})
    if soft_document is None:
        try:
            env = environment if isinstance(environment, SoftEnvironment) else SoftEnvironment(environment)
            soft_document = SoftNormDocument(env, active)
        except VEError as error:
            raise CheckerUnavailable(f"CheckerUnavailable: Python could not construct Lean-accepted soft source: {error}") from error
    else:
        env = environment if isinstance(environment, SoftEnvironment) else SoftEnvironment(environment)
    elaborated = elaborate_soft_document(soft_document)
    row = _run({"id": "admission", "kind": "admission", "environment": env.to_dict(),
                "document": _wire(document)})
    try:
        from .admission import bind_report
        bind_report(document, row['report'])
        open_labels = {entry['label'] for entry in elaborated['colliding_pairs']
                       if not entry['comparable']}
        reported = {assumption.get('label') for assumption in row['report']['assumptions']}
        expected = [label for label in elaborated['conditional_on'] if label in reported]
        if row['conditional_on'] != expected or not set(row['conditional_on']) <= open_labels:
            raise ValueError('unbound soft admission conditional labels')
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft admission is not bound to the request: {error}') from error
    return {key: value for key, value in row.items() if key not in ("id", "status")}
