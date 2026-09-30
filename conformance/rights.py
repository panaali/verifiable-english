"""Deterministic rights-to-soft regeneration checks against the Lean soft route."""
from __future__ import annotations

from ve.ast import formula_to_data
from ve.rights import correlate
from ve.soft_route import elaborate_soft_document
from tests.test_rights import rights_env, claim, right


def case(index):
    raw = rights_env()
    lines = [claim(f"claim-{index}")]
    if index % 2:
        lines.append({"kind": "liberty", "holder_slot": None, "cites": {},
                      "norm": {"name": f"liberty-{index}", "predicate": "person_may_act",
                               "sign": True, "guard": ["top"], "unless": [], "over": []}})
    units = [right(lines)]
    if index % 3:
        units.append({"limitation": {"name": f"limit-{index}", "scope": "all",
                                      "kinds": ["claim"] if index % 4 else "all",
                                      "decided_by": "unstated", "conditions": [
                                          {"name": "law", "role": "necessary",
                                           "decided_by": None, "verbalisation": "determined by law"},
                                          {"name": "purpose", "role": "sufficient",
                                           "decided_by": None, "verbalisation": "serves the stated purpose"}],
                                      "factors": ["rights of others"]}})
    if index % 2:
        units.append({"bar": {"name": f"bar-{index}", "reading": "rule" if index % 5 else "query",
                              "decided_by": "unstated"}})
    return raw, units


def run(count=32):
    for index in range(count):
        raw, units = case(index)
        rights = correlate(raw, units)
        elaborate_soft_document(rights.soft_document)
        labels = [label for label, formula in rights.limitation_premises
                  if formula_to_data(rights.environment, formula, _generated=True)]
        assert len(labels) == len(set(labels))
        assert len(rights.limitation_names) == len(set(rights.limitation_names.values()))
    return count


if __name__ == "__main__":
    print(f"PASS: {run()} rights sources correlated and replayed by the Lean soft route")
