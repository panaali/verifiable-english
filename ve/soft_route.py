"""Python entry point for the proved soft-norm admission route."""
from __future__ import annotations

from .errors import CheckerUnavailable, VEError
from .softnorms import SoftEnvironment, SoftNormDocument, bind_soft_elaboration
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


def check_soft_conflict(soft_document: SoftNormDocument, *, packages=None, witness=None,
                        pairs=None, coherent_model=None, budget=None):
    """Replay a conflict package or finite witness against the soft route."""
    elaborated = elaborate_soft_document(soft_document)
    case = {"id": "soft-conflict", "kind": "soft-conflict",
            "environment": soft_document.env.to_dict(),
            "norms": [rule.to_dict() for rule in soft_document.rules]}
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
    except (KeyError, TypeError, ValueError) as error:
        raise CheckerUnavailable(f'CheckerUnavailable: Lean soft conflict is not bound to the request: {error}') from error
    return row


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
