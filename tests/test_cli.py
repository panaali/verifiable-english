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
    assert limited.returncode == 4
    assert json.loads(limited.stdout)["evaluation"]["status"] == "ResourceLimit"


def test_cli_no_trace_omits_explanation():
    result = cli("evaluate", "--env", ENV, "--model", MODEL, "--no-trace", SOURCE)
    assert result.returncode == 0
    assert json.loads(result.stdout)["evaluation"]["explanation"] is None


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


def test_cli_countermodel_not_found_has_exit_code_three(tmp_path):
    tautology = tmp_path / "tautology.ve"
    tautology.write_text("true.\n")
    result = cli("countermodel", "--env", ENV, "--conclusion", tautology,
                 "--nonempty-domains", "--max-domain-size", "1")
    assert result.returncode == 3
    assert json.loads(result.stdout)["status"] == "NotFound"


def test_cli_named_fol_natural_view_and_canonical_output(tmp_path):
    path = tmp_path / "fol.json"
    path.write_text(json.dumps({"formulas": [{"op": "exists", "sort": "person",
                                             "variable": "someone", "body": {"op": "top"}}]}))
    canonical = cli("import-fol", "--env", ENV, path)
    natural = cli("import-fol", "--env", ENV, "--view", "natural", path)
    assert canonical.stdout == "there exists person x0, (true).\n"
    assert natural.returncode == canonical.returncode == 0
    view = json.loads(natural.stdout)
    assert view["text"] == "There is a person such that this holds in all cases.\n"
    assert view["environment_id"] and view["meaning_id"]
    assert view["renderer"] and view["version"]


def test_cli_five_e1_view_names_emit_plain_text(tmp_path):
    path = tmp_path / "fol.json"
    path.write_text(json.dumps({"formulas": [{"op": "exists", "sort": "person",
                                             "variable": "someone", "body": {"op": "top"}}]}))
    outputs = {view: cli("import-fol", "--env", ENV, "--view", view, path)
               for view in ("fol_symbols", "fol_keywords", "ve_strict", "ve_natural", "ve_fluent")}
    assert all(result.returncode == 0 for result in outputs.values())
    assert all(not result.stdout.lstrip().startswith("{") for result in outputs.values())
    assert len({result.stdout for result in outputs.values()}) == 5
    assert outputs["ve_fluent"].stdout == "there is a person such that true.\n"
    env = Environment.from_json(ENV.read_bytes())
    from ve import render
    assert cli("render", "--env", ENV, "--view", "ve_fluent", SOURCE).stdout == render(
        parse(env, SOURCE.read_bytes()), env, "ve_fluent")


@pytest.mark.parametrize("naming", ["per_statement", "per_document"])
@pytest.mark.parametrize("style", [None, "json", "compact"])
def test_cli_cell_legend_and_naming_across_all_views(tmp_path, naming, style):
    from ve.printer import VIEWS, render_cell
    env = Environment.from_json(ENV.read_bytes())
    source = tmp_path / "two.ve"
    source.write_text("for every service s, (s equals s).\n" * 2)
    document = parse(env, source.read_bytes())
    options = [] if style is None else ["--legend-style", style]
    for view in (*VIEWS, "canonical", "natural"):
        result = cli("render", "--env", ENV, "--view", view, "--with-legend",
                     "--naming", naming, *options, source)
        actual_view = {"canonical": "ve_strict", "natural": "ve_natural"}.get(view, view)
        assert result.returncode == 0, result.stdout
        assert result.stdout == render_cell(document, env, actual_view, naming, style=style or "json")


def test_cli_import_fol_compact_legend_and_claim_only_aliases(tmp_path):
    from ve.printer import VIEWS, render, render_cell
    env = Environment.from_json(ENV.read_bytes())
    path = tmp_path / "fol.json"
    path.write_text(json.dumps({"formulas": [{"op": "top"}]}))
    for view in (*VIEWS, "canonical", "natural"):
        actual_view = {"canonical": "ve_strict", "natural": "ve_natural"}.get(view, view)
        result = cli("import-fol", "--env", ENV, "--view", view, "--with-legend",
                     "--legend-style", "compact", path)
        assert result.returncode == 0, result.stdout
        assert result.stdout == render_cell(Document((Top(),)), env, actual_view, style="compact")
        for command, source in (("import-fol", path), ("render", SOURCE)):
            result = cli(command, "--env", ENV, "--view", view, "--legend-style", "compact", source)
            assert result.returncode == 0, result.stdout
            document = Document((Top(),)) if command == "import-fol" else parse(env, SOURCE.read_bytes())
            text = json.loads(result.stdout)["text"] if view == "natural" else result.stdout
            assert text == render(document, env, actual_view)


@pytest.mark.parametrize("command", ["render", "import-fol", "view-lengths"])
def test_cli_rejects_unknown_legend_style(command):
    result = cli(command, "--env", ENV, "--legend-style", "unknown", SOURCE)
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


@pytest.mark.parametrize("style", [None, "json", "compact"])
def test_cli_jsonl_view_lengths_and_invalid_records(tmp_path, style):
    from ve.printer import measure_jsonl_lengths
    env = Environment.from_json(ENV.read_bytes())
    path = tmp_path / "items.jsonl"
    path.write_text('{"id":"real-item-1","claim":"true.\\n"}\n')
    options = [] if style is None else ["--legend-style", style]
    result = cli("view-lengths", "--env", ENV, "--field", "claim", "--source-format", "ve", *options, path)
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout) == measure_jsonl_lengths(path, env, field="claim", source_format="ve",
                                                            style=style or "json")
    path.write_text('{}\n')
    result = cli("view-lengths", "--env", ENV, path)
    assert result.returncode == 2 and json.loads(result.stdout)["status"] == "InvalidInput"


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


def test_invalid_input_and_both_resource_limit_paths_have_distinct_exit_codes(tmp_path):
    invalid = tmp_path / 'invalid.ve'
    invalid.write_text('not a VE statement\n')
    assert cli('parse', '--env', ENV, invalid).returncode == 2
    huge = tmp_path / 'oversized.ve'
    huge.write_bytes(b'true.\n' * 12000)
    result = cli('parse', '--env', ENV, huge)
    assert result.returncode == 4 and json.loads(result.stdout)['status'] == 'ResourceLimit'
    result = cli('countermodel', '--env', ENV, '--conclusion', ROOT / 'examples/conclusion.ve',
                 '--max-models', '0')
    assert result.returncode == 4 and json.loads(result.stdout)['status'] == 'ResourceLimit'


def test_cli_semantic_nonvacuity_clause_guard(tmp_path):
    clause = tmp_path / 'clause.ve'
    clause.write_text('for every service s, ((not (s is deployed)) or (s is reviewed)).\n')
    bottom = tmp_path / 'bottom.ve'
    bottom.write_text('false.\n')
    result = cli('countermodel', '--env', ENV, '--conclusion', bottom, '--premises', clause,
                 '--nonvacuous-for', clause, '--semantic-nonvacuity')
    assert result.returncode == 0, result.stdout
    record = json.loads(result.stdout)
    assert record['semantic_nonvacuity'] is True
    assert record['model']['relations']['deployed'] and record['model']['relations']['reviewed']
    invalid = cli('countermodel', '--env', ENV, '--conclusion', bottom, '--semantic-nonvacuity')
    assert invalid.returncode == 2


def test_check_display_overflow_never_changes_acceptance(tmp_path):
    path = ROOT / 'usecases/us-constitution-14th-s1/environment.json'
    source = tmp_path / 'large.ve'
    source.write_text('for every person x0, (if (x0 is subject_to_us_jurisdiction), then (x0 is us_citizen)).\n' * 753)
    assert len(source.read_bytes()) == 65511
    result = cli('check', '--env', path, source)
    assert result.returncode == 0
    record = json.loads(result.stdout)
    assert record['language'] == 'accepted'
    assert record['display_omitted'] == 'ResourceLimit'
    assert 'display_text' not in record
    expected = check(Environment.from_json(path.read_bytes()), source.read_bytes())
    assert {k: record[k] for k in expected} == expected


@pytest.mark.parametrize('status,exit_code', [('Satisfied', 0), ('Violated', 1), ('ResourceLimit', 4)])
def test_unexpected_display_failure_preserves_verdict(monkeypatch, capsys, tmp_path, status, exit_code):
    import ve.__main__ as main
    def broken(*args, **kwargs): raise RuntimeError('display failed')
    monkeypatch.setattr(main, 'render', broken)
    model = json.loads(MODEL.read_text())
    if status == 'Violated': model['relations']['reviewed'] = []
    path = tmp_path / 'model.json'; path.write_text(json.dumps(model))
    args = ['check', '--env', str(ENV), '--model', str(path), str(SOURCE)]
    if status == 'ResourceLimit': args += ['--max-evaluations', '0']
    assert main.main(args) == exit_code
    record = json.loads(capsys.readouterr().out)
    assert record['evaluation']['status'] == status
    assert record['display_omitted'] == 'RuntimeError' and 'display_text' not in record


def test_render_default_is_canonical_strict_and_english_is_explicit(tmp_path):
    from ve import render
    env = Environment.from_json(ENV.read_bytes())
    doc = parse(env, SOURCE.read_bytes())
    strict, english = render(doc, env, 've_strict'), render(doc, env, 've_english')
    assert cli('render', '--env', ENV, SOURCE).stdout == strict
    assert cli('render', '--env', ENV, '--view', 've_english', SOURCE).stdout == english
    source = tmp_path / 'english.txt'; source.write_text(english)
    assert cli('render', '--env', ENV, '--surface', 'english', source).stdout == english
    assert cli('render', '--env', ENV, '--surface', 'english', '--view', 've_strict', source).stdout == strict


@pytest.mark.parametrize('overlay', ['{', '{}'])
def test_invalid_display_overlay_cannot_reject_strict_check(tmp_path, overlay):
    path = tmp_path / 'invalid-words.json'; path.write_text(overlay)
    result = cli('check', '--env', ENV, '--english-vocabulary', path, SOURCE)
    assert result.returncode == 0
    record = json.loads(result.stdout)
    assert record['language'] == 'accepted' and 'display_omitted' in record
    assert 'display_text' not in record
