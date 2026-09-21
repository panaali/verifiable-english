"""Experiment attack validation and streaming JSONL CLI.

Run ``python -m ve.attacks --help``. A DIFFERENT label is necessary but not
sufficient: both implication directions must be decided to classify an attack.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import sys

from .ast import Exists, Top, formula_from_data
from .environment import Environment
from .equivalence import (DIFFERENT, EQUIVALENT, UNKNOWN, Budgets, ComparisonResult,
                          _budgets, compare, non_vacuity_conditions, witness_quality)
from .errors import ResourceLimit, VEError
from .limits import MAX_PACKAGE_BYTES
from .parser import parse
from .search import check_countermodel, find_countermodel
from .wire import loads_json


@dataclass(frozen=True, slots=True)
class AttackValidation:
    status: str
    reason: str
    comparison: ComparisonResult
    classification: str | None = None
    witnesses: tuple[dict, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def accepted(self):
        return None if self.status == UNKNOWN else self.status == "VALID"

    def to_dict(self):
        return {"status": self.status, "accepted": self.accepted, "reason": self.reason,
                "classification": self.classification, "comparison": self.comparison.to_dict(),
                "witnesses": list(self.witnesses), "warnings": list(self.warnings)}


def _preferred_witness(env, faithful, attacked, direction, original, budgets, *, empty_only=False):
    a, b = ((faithful, attacked) if direction == "a_not_implies_b" else (attacked, faithful))
    selected = original
    quality = witness_quality(env, selected, faithful, attacked, budgets=budgets)
    attempts = []
    if not empty_only and quality["non_vacuous"] is not True:
        # First seek full guard coverage, then at least inhabited sorts. Neither
        # failed bounded search changes the logical finding or proves impossibility.
        for label in ("non_vacuous", "non_empty"):
            if label == "non_empty" and quality["non_empty"]:
                break
            try:
                conditions = (non_vacuity_conditions(env, faithful, attacked) if label == "non_vacuous"
                              else tuple(Exists(sort, Top()) for sort in env.sorts))
                result = find_countermodel(env, (a, *conditions), b, **budgets.search_options())
                attempts.append({"preference": label, "status": result.status, "detail": result.detail})
                if result.model is None:
                    continue
                checked = check_countermodel(env, (a, *conditions), b, result.model,
                                             max_evaluations=budgets.max_evaluations)
                if not checked.valid:
                    continue
                selected = result.model
                quality = witness_quality(env, selected, faithful, attacked, budgets=budgets)
                if quality["non_vacuous"] is True:
                    break
            except ResourceLimit as exc:
                attempts.append({"preference": label, "status": "ResourceLimit", "detail": str(exc)})
    checked = check_countermodel(env, (a,), b, selected, max_evaluations=budgets.max_evaluations)
    if not checked.valid:
        # Public compare only supplies replayed witnesses. Keep this guard in case
        # a future search backend violates that contract.
        raise VEError("Distinguishing model failed final replay")
    return {"direction": direction, "model": selected.to_dict(), "model_id": selected.model_id,
            "faithful_value": direction == "a_not_implies_b",
            "attacked_value": direction == "b_not_implies_a", "quality": quality,
            "preference_attempts": attempts}


def validate_attack(env, faithful, attacked, budgets=None) -> AttackValidation:
    """Reject fake attacks; store checked witnesses and certify strict direction.

    Logical comparison retains VE's empty-sort semantics. Prefer inhabited,
    guard-covered witnesses, but retain a checked empty/vacuous witness with a
    warning if bounded preference searches fail. No claim of impossibility is
    made from those failures. Reference validation is a separate prerequisite.
    """
    budgets = _budgets(budgets)
    result = compare(env, faithful, attacked, budgets)
    if faithful == attacked:
        return AttackValidation("REJECTED", "fake_attack: alpha-identical formulas", result)
    if result.status == EQUIVALENT:
        return AttackValidation("REJECTED", "fake_attack: certified logical equivalence", result)
    if result.status != DIFFERENT:
        return AttackValidation(UNKNOWN, "No checked semantic difference", result)
    witnesses = tuple(_preferred_witness(env, faithful, attacked, direction, model, budgets,
                                         empty_only=result.relation_detail is not None)
                      for direction, model in result.models.items())
    warnings = tuple((f"{w['direction']}: differs_only_on_empty_sorts; inhabited equivalence certified"
                      if result.relation_detail else
                      f"{w['direction']}: non-empty, guard-covered witness not established within budgets")
                     for w in witnesses if w["quality"]["non_vacuous"] is not True)
    classification = {"weaker": "weakening", "stronger": "strengthening",
                      "incomparable": "incomparable"}.get(result.relation)
    if classification is None:
        return AttackValidation(UNKNOWN, "Difference checked, but the other implication is unresolved",
                                result, witnesses=witnesses, warnings=warnings)
    return AttackValidation("VALID", "Checked difference and attack classification", result,
                            classification, witnesses, warnings)


def _formula(env, value):
    if type(value) is list:
        return formula_from_data(env, value)
    if type(value) is not str:
        raise VEError("A formula must be VE source text or a tagged AST array")
    document = parse(env, value)
    if len(document.formulas) != 1:
        raise VEError("Expected exactly one closed formula per field")
    return document.formulas[0]


def validate_row(row, budgets=None):
    required = {"environment", "faithful", "attacked"}
    if type(row) is not dict or not required <= set(row) or set(row) - required - {"id", "budgets"}:
        raise VEError("Expected environment, faithful, attacked, and optional id/budgets fields")
    env = Environment.from_dict(row["environment"])
    result = validate_attack(env, _formula(env, row["faithful"]), _formula(env, row["attacked"]),
                             row.get("budgets", budgets))
    return {**({"id": row["id"]} if "id" in row else {}), **result.to_dict()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSONL file or '-' for stdin")
    parser.add_argument("--output", default="-", help="JSONL results; default stdout")
    for name, default in (("max-proof-steps", 10_000), ("max-domain-size", 2),
                          ("max-models", 10_000), ("max-evaluations", 100_000)):
        parser.add_argument("--" + name, type=int, default=default)
    args = parser.parse_args(argv)
    if args.input != "-" and args.output != "-" and Path(args.input).resolve() == Path(args.output).resolve():
        parser.error("Input and output must be different files")
    try:
        budgets = Budgets(args.max_proof_steps, args.max_domain_size, args.max_models, args.max_evaluations)
    except ValueError as exc:
        parser.error(str(exc))
    counts = {"VALID": 0, "REJECTED": 0, UNKNOWN: 0, "InvalidInput": 0}
    source = sys.stdin.buffer if args.input == "-" else open(args.input, "rb")
    output = sys.stdout if args.output == "-" else open(args.output, "w", encoding="utf-8")
    try:
        line_number = 0
        while raw := source.readline(MAX_PACKAGE_BYTES + 1):
            line_number += 1
            try:
                if len(raw) > MAX_PACKAGE_BYTES:
                    # Drain this row with bounded memory, then continue the batch.
                    while not raw.endswith(b"\n"):
                        raw = source.readline(MAX_PACKAGE_BYTES + 1)
                        if not raw:
                            break
                    raise ResourceLimit("JSONL row exceeds 16 MiB")
                row = loads_json(raw)
                result = validate_row(row, budgets)
            except (VEError, ValueError, TypeError) as exc:
                result = {"status": "InvalidInput", "accepted": False, "reason": str(exc)}
            counts[result["status"]] += 1
            output.write(json.dumps({"line": line_number, **result}, ensure_ascii=False, allow_nan=False) + "\n")
    finally:
        if source is not sys.stdin.buffer:
            source.close()
        if output is not sys.stdout:
            output.close()
    print(json.dumps({"rows": sum(counts.values()), "counts": counts}), file=sys.stderr)
    return 2 if counts["InvalidInput"] or counts[UNKNOWN] else 1 if counts["REJECTED"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
