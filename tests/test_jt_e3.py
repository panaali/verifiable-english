"""Small, model-free checks of JT-E3's agreement and blind runner."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / "docs/judgment-terms/jt-e3"
sys.path.insert(0, str(ROOT))
import analyze  # noqa: E402
import runner  # noqa: E402


def test_hand_computed_kappa():
    # [[3, 1], [1, 3]]: Po = 6/8, Pe = 1/2, kappa = 1/2.
    table = {"judgment": {"judgment": 3, "classification": 1},
             "classification": {"judgment": 1, "classification": 3}}
    po, pe, k = analyze.kappa(table)
    assert (str(po), str(pe), str(k)) == ("3/4", "1/2", "1/2")


def test_answer_retypes_and_rebinds_every_row():
    rows = [{"id": r["id"], "class": "judgment"} for r in runner.input_rows()]
    assert runner.parse_answer(json.dumps(rows)) == rows
    for bad in ([], rows[:-1], rows + [rows[0]]):
        try:
            runner.parse_answer(json.dumps(bad))
        except ValueError:
            pass
        else:
            raise AssertionError("bad row count passed")
    for value in (7, True, None, [], {}, "absent"):
        mutant = [dict(r) for r in rows]
        mutant[12]["id"] = value
        try:
            runner.parse_answer(json.dumps(mutant))
        except ValueError:
            pass
        else:
            raise AssertionError("bad id passed")
        mutant = [dict(r) for r in rows]
        mutant[12]["class"] = value
        try:
            runner.parse_answer(json.dumps(mutant))
        except ValueError:
            pass
        else:
            raise AssertionError("bad class passed")


def test_count_excludes_disagreement_and_borderline_independently():
    units = [
        {"id": "u001", "open_terms": ["a"], "span": [0, 10]},
        {"id": "u002", "open_terms": ["a", "b"], "span": [10, 30]},
        {"id": "u003", "open_terms": ["b"], "span": [30, 35]},
    ]
    classes = {("udhr", "a"): {"class": "judgment", "borderline": "no"},
               ("udhr", "b"): {"class": "judgment", "borderline": "yes"}}
    assert analyze.count_units(units, "udhr", classes, set(), False) == {"units": 3, "bytes": 35}
    assert analyze.count_units(units, "udhr", classes, {"a"}, False) == {"units": 2, "bytes": 25}
    assert analyze.count_units(units, "udhr", classes, set(), True) == {"units": 2, "bytes": 30}
    assert analyze.count_units(units, "udhr", classes, {"a"}, True) == {"units": 0, "bytes": 0}


def test_sample_and_prompt_are_blind():
    assert len(runner.input_rows()) == 60
    assert "stratum_class" not in runner.prompt()
    assert "source_sentence" in runner.prompt()
