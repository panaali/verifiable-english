"""Grant author's operational choices.  These rules classify supplied records;
they contain no observations about a real benchmark or risk event.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from datetime import date


CHOICES = {
    "matched_cost": {
        "signature": "grant-author",
        "why": "A comparison must count the work that each method actually requires.",
        "rule": "same task and preregistered budget; count authoring, formalisation, proof production, compute and review for both arms; absolute total-cost difference <= 5% of the larger total",
        "flags": ("same_task", "preregistered_budget", "all_costs_logged", "within_five_percent"),
    },
    "real_artefact": {
        "signature": "grant-author",
        "why": "The transfer arm should use material made for an independent purpose.",
        "rule": "provenance hash and creation date recorded; created for a non-benchmark task before selection; no flaw seeded by the evaluators",
        "flags": ("provenance_recorded", "independent_task", "predates_selection", "no_seeded_flaw"),
    },
    "affordable_proof": {
        "signature": "grant-author",
        "why": "Affordability must include the full route to a checked certificate.",
        "rule": "proof and formalisation costs recorded; checker accepts a complete certificate; total cost <= preregistered per-claim budget and elapsed time <= preregistered deadline",
        "flags": ("costs_recorded", "certificate_checked", "within_budget", "within_deadline"),
    },
    "misleading_formalisation": {
        "signature": "grant-author",
        "why": "A fidelity failure needs an inspectable difference from the source task.",
        "rule": "source task and formula pinned; a concrete input gives different answers; two independent reviewers reproduce the difference without knowing the arm",
        "flags": ("source_and_formula_pinned", "answer_changing_counterexample", "two_blind_reproductions"),
    },
    "catastrophic_risk": {
        "signature": "grant-author",
        "why": "The grant question needs a severity boundary and a separate possibility judgment.",
        "rule": "documented pathway to human extinction or at least 1,000,000 deaths; pathway evidence and severity assessment recorded; possibility is separately evaluated and is never inferred from this classification alone",
        "flags": ("severity_threshold", "pathway_documented", "evidence_recorded"),
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


def decide(term: str, record: dict) -> bool:
    """Evaluate a complete record; absent evidence never counts as success."""
    if term not in CHOICES or type(record) is not dict:
        raise ValueError("unknown term or invalid record")
    if term == "matched_cost":
        components = ("authoring", "formalisation", "proof", "compute", "review")
        arms = record.get("arms")
        if type(arms) is not dict or set(arms) != {"proof", "cross_examination"}:
            return False
        if not (record.get("same_task") is True and
                type(record.get("budget_record_id")) is str and record["budget_record_id"]):
            return False
        totals = []
        for name in ("proof", "cross_examination"):
            costs = arms[name]
            if type(costs) is not dict or set(costs) != set(components):
                return False
            totals.append(sum((_number(costs[c]) for c in components), Decimal(0)))
        return max(totals) > 0 and abs(totals[0] - totals[1]) * 20 <= max(totals)
    if term == "real_artefact":
        created, selected = _date(record.get("created_on")), _date(record.get("selected_on"))
        return (_sha256(record.get("provenance_sha256")) and created is not None and
                selected is not None and created < selected and
                record.get("independent_task") is True and
                record.get("evaluator_seeded_flaw") is False)
    if term == "affordable_proof":
        if not (record.get("certificate_checked") is True and
                record.get("formalisation_cost_recorded") is True):
            return False
        return (_number(record["total_cost"]) <= _number(record["preregistered_budget"]) and
                _number(record["elapsed_hours"]) <= _number(record["preregistered_deadline_hours"])) if all(
                    k in record for k in ("total_cost", "preregistered_budget", "elapsed_hours",
                                        "preregistered_deadline_hours")) else False
    if term == "misleading_formalisation":
        reviewers = record.get("blind_reviewers")
        return (_sha256(record.get("source_sha256")) and _sha256(record.get("formula_sha256")) and
                type(record.get("counterexample_id")) is str and bool(record["counterexample_id"]) and
                record.get("answer_changes") is True and type(reviewers) is list and
                len(reviewers) >= 2 and len(reviewers) == len(set(reviewers)) and
                all(type(r) is str and r for r in reviewers))
    return (type(record.get("pathway_record_id")) is str and bool(record["pathway_record_id"]) and
            type(record.get("evidence_record_id")) is str and bool(record["evidence_record_id"]) and
            (record.get("human_extinction") is True or
             "projected_deaths" in record and _number(record["projected_deaths"]) >= 1_000_000))
