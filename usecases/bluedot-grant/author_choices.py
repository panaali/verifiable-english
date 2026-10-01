"""Grant author's operational choices.  These rules classify supplied records;
they contain no observations about a real benchmark or risk event.

Each rule is a list of clauses.  A clause is both a conjunct of the term's
definition in the document environment and one executable check in
``clauses()``, so the embedded definition and the record classifier cannot
drift apart: ``decide`` is exactly the conjunction of the clause results.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from datetime import date


def _flag(name: str, words: str, sort: str) -> dict:
    return {"id": name, "predicate": name, "words": words, "sort": sort}


def _cost(component: str, constant: str) -> dict:
    return {"id": f"counts_{constant}", "predicate": "counts_cost", "constant": constant,
            "component": component, "words": f"counts the cost of {component}"}


CHOICES = {
    "matched_cost": {
        "signature": "grant-author",
        "sort": "comparison",
        "verbalisation": "{0} is at matched cost",
        "why": "A comparison must count the work that each method actually requires.",
        "rule": "same task; budget registered before the comparison starts; count authoring, formalisation, proof production, compute and review for both arms; absolute total-cost difference at most 5% of the larger total",
        "clauses": (
            _flag("same_task", "uses the same task for both arms", "comparison"),
            _flag("budget_preregistered", "has a budget registered before the comparison starts", "comparison"),
            _cost("authoring", "authoring"),
            _cost("formalisation", "formalisation_work"),
            _cost("proof production", "proof_production"),
            _cost("compute", "compute"),
            _cost("review", "review"),
            _flag("totals_within_tolerance", "has arm totals that differ by at most 5% of the larger total", "comparison"),
        ),
    },
    "real_artefact": {
        "signature": "grant-author",
        "sort": "artefact",
        "verbalisation": "{0} is a real artefact",
        "why": "The transfer arm should use material made for an independent purpose.",
        "rule": "provenance SHA-256 recorded; created for a non-benchmark task; created before it was selected; no flaw seeded by the evaluators",
        "clauses": (
            _flag("provenance_recorded", "has a recorded provenance hash", "artefact"),
            _flag("independent_task", "was created for a non-benchmark task", "artefact"),
            _flag("predates_selection", "was created before it was selected", "artefact"),
            _flag("no_seeded_flaw", "has no flaw seeded by the evaluators", "artefact"),
        ),
    },
    "affordable_proof": {
        "signature": "grant-author",
        "sort": "proof",
        "verbalisation": "{0} is an affordable proof",
        "why": "Affordability must include the full route to a checked certificate.",
        "rule": "proof cost and formalisation cost recorded; the checker accepts a complete certificate; budget and deadline registered before the claim; total cost within that budget and elapsed time within that deadline",
        "clauses": (
            _flag("proof_cost_recorded", "has its proof cost recorded", "proof"),
            _flag("formalisation_cost_recorded", "has its formalisation cost recorded", "proof"),
            _flag("certificate_complete", "has a complete certificate", "proof"),
            _flag("certificate_checked", "has a certificate the checker accepts", "proof"),
            _flag("claim_budget_preregistered", "has a budget registered before the claim", "proof"),
            _flag("claim_deadline_preregistered", "has a deadline registered before the claim", "proof"),
            _flag("within_budget", "has a total cost within its registered budget", "proof"),
            _flag("within_deadline", "has an elapsed time within its registered deadline", "proof"),
        ),
    },
    "misleading_formalisation": {
        "signature": "grant-author",
        "sort": "formalisation",
        "verbalisation": "{0} is a misleading formalisation",
        "why": "A fidelity failure needs an inspectable difference from the source task.",
        "rule": "source task and formula hashes pinned; a concrete input on which the formula and the source task give different answers; two distinct reviewers, each blind to the arm, reproduce that difference",
        "clauses": (
            _flag("source_pinned", "has a pinned source-task hash", "formalisation"),
            _flag("formula_pinned", "has a pinned formula hash", "formalisation"),
            _flag("answer_changing_counterexample", "has a concrete input with a different answer", "formalisation"),
            _flag("two_reproductions", "has the difference reproduced by two distinct reviewers", "formalisation"),
            _flag("reviewers_blind", "has every reproducing reviewer blind to the arm", "formalisation"),
        ),
    },
    "catastrophic_risk": {
        "signature": "grant-author",
        "sort": "pathway",
        "verbalisation": "{0} is a catastrophic risk",
        "why": "The grant question needs a severity boundary and a separate possibility judgment.",
        "rule": "documented pathway to human extinction or at least 1,000,000 projected deaths; pathway evidence and a severity assessment recorded; possibility is a separate judgment and is never inferred from this classification",
        "clauses": (
            _flag("pathway_documented", "has a documented pathway", "pathway"),
            _flag("evidence_recorded", "has its pathway evidence recorded", "pathway"),
            _flag("severity_assessed", "has a recorded severity assessment", "pathway"),
            _flag("meets_severity_threshold", "reaches human extinction or at least 1,000,000 projected deaths", "pathway"),
        ),
    },
}


def _number(value):
    if isinstance(value, bool):
        raise ValueError("a measured value must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError("a measured value must be numeric") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("a measured value must be finite and nonnegative")
    return result


def _sha256(value):
    return (type(value) is str and len(value) == 64 and
            all(c in "0123456789abcdef" for c in value))


def _date(value):
    if type(value) is not str:
        return None
    try:
        result = date.fromisoformat(value)
    except ValueError:
        return None
    return result if result.isoformat() == value else None


def _text(value):
    return type(value) is str and bool(value)


def _before(record, earlier, later):
    first, second = _date(record.get(earlier)), _date(record.get(later))
    return first is not None and second is not None and first < second


def _within(record, measured, limit):
    if measured not in record or limit not in record:
        return False
    return _number(record[measured]) <= _number(record[limit])


_COSTS = ("authoring", "formalisation", "proof", "compute", "review")


def _arms(record):
    arms = record.get("arms")
    if type(arms) is not dict or set(arms) != {"proof", "cross_examination"}:
        return None
    if any(type(arms[name]) is not dict for name in arms):
        return None
    return arms


def _counted(record, component):
    arms = _arms(record)
    return arms is not None and all(component in costs for costs in arms.values()) and all(
        _number(costs[component]) is not None for costs in arms.values())


def _matched_totals(record):
    arms = _arms(record)
    if arms is None or any(set(costs) != set(_COSTS) for costs in arms.values()):
        return False
    totals = [sum((_number(arms[name][c]) for c in _COSTS), Decimal(0))
              for name in ("proof", "cross_examination")]
    return max(totals) > 0 and abs(totals[0] - totals[1]) * 20 <= max(totals)


def _reviewers(record):
    reviewers = record.get("reviewers")
    if type(reviewers) is not list or not all(type(r) is dict and _text(r.get("id")) for r in reviewers):
        return None
    return reviewers


def _reproducing(record):
    reviewers = _reviewers(record)
    return [] if reviewers is None else [r for r in reviewers if r.get("reproduced") is True]


_CHECKS = {
    "matched_cost": {
        "same_task": lambda r: r.get("same_task") is True,
        "budget_preregistered": lambda r: _text(r.get("budget_record_id")) and
            _before(r, "budget_registered_on", "comparison_started_on"),
        "counts_authoring": lambda r: _counted(r, "authoring"),
        "counts_formalisation_work": lambda r: _counted(r, "formalisation"),
        "counts_proof_production": lambda r: _counted(r, "proof"),
        "counts_compute": lambda r: _counted(r, "compute"),
        "counts_review": lambda r: _counted(r, "review"),
        "totals_within_tolerance": _matched_totals,
    },
    "real_artefact": {
        "provenance_recorded": lambda r: _sha256(r.get("provenance_sha256")),
        "independent_task": lambda r: r.get("independent_task") is True,
        "predates_selection": lambda r: _before(r, "created_on", "selected_on"),
        "no_seeded_flaw": lambda r: r.get("evaluator_seeded_flaw") is False,
    },
    "affordable_proof": {
        "proof_cost_recorded": lambda r: r.get("proof_cost_recorded") is True,
        "formalisation_cost_recorded": lambda r: r.get("formalisation_cost_recorded") is True,
        "certificate_complete": lambda r: r.get("certificate_complete") is True,
        "certificate_checked": lambda r: r.get("certificate_checked") is True,
        "claim_budget_preregistered": lambda r: _before(r, "budget_registered_on", "claim_made_on"),
        "claim_deadline_preregistered": lambda r: _before(r, "deadline_registered_on", "claim_made_on"),
        "within_budget": lambda r: _within(r, "total_cost", "registered_budget"),
        "within_deadline": lambda r: _within(r, "elapsed_hours", "registered_deadline_hours"),
    },
    "misleading_formalisation": {
        "source_pinned": lambda r: _sha256(r.get("source_sha256")),
        "formula_pinned": lambda r: _sha256(r.get("formula_sha256")),
        "answer_changing_counterexample": lambda r: _text(r.get("counterexample_id")) and
            r.get("answer_changes") is True,
        "two_reproductions": lambda r: len({x["id"] for x in _reproducing(r)}) >= 2,
        "reviewers_blind": lambda r: bool(_reproducing(r)) and
            all(x.get("blind_to_arm") is True for x in _reproducing(r)),
    },
    "catastrophic_risk": {
        "pathway_documented": lambda r: _text(r.get("pathway_record_id")),
        "evidence_recorded": lambda r: _text(r.get("evidence_record_id")),
        "severity_assessed": lambda r: _text(r.get("severity_assessment_id")),
        "meets_severity_threshold": lambda r: r.get("human_extinction") is True or (
            "projected_deaths" in r and _number(r["projected_deaths"]) >= 1_000_000),
    },
}


def clauses(term: str, record: dict) -> dict[str, bool]:
    """Each definition clause's verdict on a complete record."""
    if term not in CHOICES or type(record) is not dict:
        raise ValueError("unknown term or invalid record")
    return {clause["id"]: bool(_CHECKS[term][clause["id"]](record))
            for clause in CHOICES[term]["clauses"]}


def decide(term: str, record: dict) -> bool:
    """Evaluate a complete record; absent evidence never counts as success."""
    return all(clauses(term, record).values())
