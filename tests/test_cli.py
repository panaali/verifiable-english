import json
from pathlib import Path
import subprocess
import sys

import pytest

from ve.ast import Document, Top
from ve.check import check
from ve.environment import Environment
from ve.errors import VEError
from ve.model import FiniteModel
from ve.parser import parse


ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "examples/environment.json"
SOURCE = ROOT / "examples/requirements.ve"
MODEL = ROOT / "examples/model.json"


def cli(*args):
    return subprocess.run([sys.executable, "-m", "ve", *map(str, args)], cwd=ROOT,
                          text=True, capture_output=True, timeout=20)


def test_cli_evaluation_and_source_binding():
    result = cli("evaluate", "--env", ENV, "--model", MODEL, SOURCE)
    assert result.returncode == 0, result.stderr
    record = json.loads(result.stdout)
    assert record["evaluation"]["status"] == "Satisfied"
    assert record["assurance"] == "experimental"
    assert record["proof"] == "not_checked"
    assert record["intent"] == "unconfirmed"
    assert record["canonical"] is False
    assert len(record["source_id"]) == len(record["meaning_id"]) == len(record["model_id"]) == 64


def test_cli_negative_and_resource_outcomes_are_distinct(tmp_path):
    model = json.loads(MODEL.read_text())
    model["relations"]["reviewed"] = []
    path = tmp_path / "violated.json"
    path.write_text(json.dumps(model))
    negative = cli("evaluate", "--env", ENV, "--model", path, SOURCE)
    limited = cli("evaluate", "--env", ENV, "--model", MODEL, "--max-evaluations", "0", SOURCE)
    assert negative.returncode == 1
    assert json.loads(negative.stdout)["evaluation"]["status"] == "Violated"
    assert limited.returncode == 2
    assert json.loads(limited.stdout)["evaluation"]["status"] == "ResourceLimit"


def test_cli_preserves_crlf_for_rejection(tmp_path):
    source = tmp_path / "bad.ve"
    source.write_bytes(b"true.\r\n")
    result = cli("parse", "--env", ENV, source)
    assert result.returncode == 2
    assert json.loads(result.stdout)["error"]["code"] == "SyntaxError"


def test_cli_finds_empty_domain_gap():
    result = cli("countermodel", "--env", ENV, "--premises", ROOT / "examples/premise.ve",
                 "--conclusion", ROOT / "examples/conclusion.ve")
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "Found"
    assert payload["model"]["domains"]["service"] == []


def test_cli_named_fol_natural_view_and_canonical_output(tmp_path):
    path = tmp_path / "fol.json"
    path.write_text(json.dumps({"formulas": [{"op": "exists", "sort": "person",
                                             "variable": "someone", "body": {"op": "top"}}]}))
    canonical = cli("import-fol", "--env", ENV, path)
    natural = cli("import-fol", "--env", ENV, "--view", "natural", path)
    assert canonical.stdout == "there exists person x0, (true).\n"
    assert natural.returncode == canonical.returncode == 0
    view = json.loads(natural.stdout)
    assert "there exists at least one person" in view["text"]
    assert view["environment_id"]
    assert view["meaning_id"]


def test_acceptance_rejects_individually_valid_substituted_ast():
    env = Environment.from_json(ENV.read_bytes())
    with pytest.raises(VEError, match="does not match"):
        check(env, SOURCE.read_bytes(), candidate_ast=Document((Top(),)))
    correct = parse(env, SOURCE.read_bytes())
    assert check(env, SOURCE.read_bytes(), candidate_ast=correct)["language"] == "accepted"


def test_environment_mutation_invalidates_models():
    env = Environment.from_json(ENV.read_bytes())
    model = FiniteModel.from_json(env, MODEL.read_bytes())
    changed = env.to_dict()
    changed["vocabulary"]["sorts"]["service"]["description"] = "Changed meaning."
    with pytest.raises(VEError):
        check(Environment.from_dict(changed), SOURCE.read_bytes(), model)
