"""The model environment Rust's search and Lean's metered evaluator read (lean-first batch 15b, review A1/B1).

Python validates every environment; the engines answer model questions over `profiles.model_environment`,
one table with a row per registered profile. These tests remove the class the review found (an engine
refusing an environment Python accepts, so that search, premise status and comparison stopped answering):
every registered profile has a row, the projection keeps everything a model reads, and the public operations
answer as Python's own search did at the base on every fixture environment, each also with English display
text everywhere (`tests/b15b_model_cases.py`, oracle `tests/data/b15b-model-oracle.json.gz`).
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import pytest

from tests import b15b_model_cases as model_cases
from ve.background import background
from ve.environment import Environment
from ve.profiles import BY_NAME, DISPLAY_FIELDS, MODEL_REDUCTIONS, model_environment

ORACLE = json.loads(gzip.decompress(
    (Path(__file__).parent / "data/b15b-model-oracle.json.gz").read_bytes()))
ENVIRONMENTS = [tuple(item) for item in ORACLE["environments"]]
GROUPS = sorted({name.split("#")[0] for name, _ in ENVIRONMENTS})


def test_every_registered_profile_has_one_model_reduction():
    assert set(MODEL_REDUCTIONS) == set(BY_NAME)
    with pytest.raises(Exception, match="Unsupported profile unknown@0"):
        model_environment({"language": "ve.core@0.2", "profiles": ["relational-fol@0", "unknown@0"],
                           "vocabulary": {}})


def test_the_oracle_reaches_every_profile_and_display_field():
    profiles = {p for _, raw in ENVIRONMENTS for p in raw.get("profiles", ()) if type(p) is str}
    assert profiles == set(BY_NAME)
    for table, fields in DISPLAY_FIELDS.items():
        for field in fields:
            assert any(field in entry for _, raw in ENVIRONMENTS
                       for entry in raw["vocabulary"].get(table, {}).values() if type(entry) is dict), field
    assert sum(name.endswith("+display") for name, _ in ENVIRONMENTS) > 100


def _model_vocabulary(env) -> dict:
    """Everything a finite model over `env` interprets or must satisfy from the environment itself."""
    return {"sorts": list(env.model_sorts),
            "predicates": {name: (decl.arguments, decl.functional, decl.total,
                                  None if decl.regulated is None else
                                  (decl.regulated.role, decl.regulated.permission))
                           for name, decl in env.predicates.items()},
            "constants": {name: decl.sort for name, decl in env.constants.items()},
            "definitions": env.definition_entries,
            "background": [(premise.generator, repr(premise.formula)) for premise in background(env)],
            "order": env.order, "closure": env.closure}


@pytest.mark.parametrize("name, raw", ENVIRONMENTS, ids=[name for name, _ in ENVIRONMENTS])
def test_model_environment_keeps_everything_a_model_reads(name, raw):
    env = model_cases.build(raw)
    projected = model_environment(env.to_dict())
    reduced = Environment(projected)
    assert _model_vocabulary(reduced) == _model_vocabulary(env), name
    # Idempotent, and free of every display field and statement-layer block (the frozen ve.core@0 envelope,
    # without profiles, is read by its frozen decoders as it is).
    assert model_environment(projected) == projected
    if "profiles" not in projected:
        assert projected == env.to_dict()
        return
    assert all(field not in entry for table, fields in DISPLAY_FIELDS.items() for field in fields
               for entry in projected["vocabulary"].get(table, {}).values() if type(entry) is dict)
    assert all(MODEL_REDUCTIONS[p].kept for p in projected.get("profiles", ()))


@pytest.mark.parametrize("group", GROUPS)
def test_search_status_and_comparison_answer_as_the_base_did(group):
    envs = [(name, raw) for name, raw in ENVIRONMENTS if name.split("#")[0] == group]
    answers = model_cases.run_all(envs)
    expected = {case: value for case, value in ORACLE["answers"].items()
                if case.split("|")[0].split("#")[0] == group}
    assert answers.keys() == expected.keys()
    for case, value in expected.items():
        assert answers[case] == value, case
