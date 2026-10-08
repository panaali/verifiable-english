"""Standalone Lean service bindings compared with Python's public identities."""
from __future__ import annotations

from pathlib import Path
from copy import deepcopy
import gzip
import json

import pytest

from tests.probe_matrix import model_wire, raw_environment
from ve import Environment, FiniteModel, Top
from ve.ast import formula_to_data
from ve.backends.relay import decide as run
from ve.identity import meaning_id, source_id

SERVICE = Path(__file__).resolve().parents[1] / "lean/.lake/build/bin/ve_service"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize(("case_id", "path"), [
    ("validation_007", "/complete"),
    ("validation_008", "/complete"),
    ("validation_010", "/relations"),
    ("validation_011", "/domains"),
    ("validation_012", "/domains/person"),
    ("validation_013", "/domains/person/1"),
    ("validation_014", "/relations/owns"),
    ("validation_015", "/relations/owns/0/0"),
    ("validation_016", "/relations/owns/0/0"),
    ("validation_017", "/relations/owns/0"),
    ("validation_028", "/domains/person/1"),
])
def test_model_rejection_retains_public_path(case_id, path):
    from ve.errors import VEError
    cases = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = next(item for item in cases if item["id"] == case_id)
    with pytest.raises(VEError) as caught:
        run("model", [case])
    assert caught.value.to_dict()["path"] == path


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize(("table", "key", "value", "path"), [
    ("domains", "item", "i", "/domains/item"),
    ("relations", "base", [["bad!"]], "/relations/base/0/0"),
])
def test_model_decoder_locates_wrong_shapes_and_invalid_cells(table, key, value, path):
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    model = model_wire(env)
    model[table][key] = value
    with pytest.raises(VEError) as caught:
        run("model", [{"id": "located", "environment": env.to_dict(), "model": model}])
    assert caught.value.to_dict()["code"] == "InvalidModel"
    assert caught.value.to_dict()["path"] == path


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_composed_environment_missing_vocabulary_table_keeps_frozen_path():
    from ve.errors import VEError
    raw = raw_environment(("data@0",))
    del raw["vocabulary"]["sorts"]
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "missing-sorts", "environment": raw}])
    assert caught.value.to_dict()["code"] == "InvalidInput"
    assert caught.value.to_dict()["path"] == "/vocabulary"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_legacy_environment_malformed_predicate_keeps_frozen_path():
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/closure.json").read_text())
    raw = next(row["environment"] for row in corpus
               if row["environment"].get("language") == "ve.core@0.1")
    name = next(iter(raw["vocabulary"]["predicates"]))
    raw["vocabulary"]["predicates"][name] = []
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "bad-predicate", "environment": raw}])
    assert caught.value.to_dict()["code"] == "InvalidInput"
    assert caught.value.to_dict()["path"] == f"/vocabulary/predicates/{name}"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_model_null_relation_cell_reaches_located_decoder():
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    model = model_wire(env)
    model["relations"]["base"] = [[None]]
    with pytest.raises(VEError) as caught:
        run("model", [{"id": "null-cell", "environment": env.to_dict(), "model": model}])
    assert caught.value.to_dict()["code"] == "InvalidModel"
    assert caught.value.to_dict()["path"] == "/relations/base/0/0"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_invalid_corpus_environment_precedes_model_shape():
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = next(row for row in corpus if row["id"] == "validation_000")
    case["model"] = []
    with pytest.raises(VEError) as caught:
        run("model", [case])
    assert caught.value.to_dict()["code"] == "UnsupportedProfile"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_legacy_envelope_error_precedes_nested_vocabulary_location():
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = next(row for row in corpus if row["id"] == "validation_008")
    raw = deepcopy(case["environment"])
    raw["extra"] = "unknown"
    del raw["vocabulary"]["sorts"]
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "outer-first", "environment": raw}])
    assert caught.value.to_dict()["code"] == "InvalidInput"
    assert caught.value.to_dict().get("path") is None


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_legacy_unknown_sort_precedes_description_type():
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = next(row for row in corpus if row["id"] == "validation_003")
    raw = deepcopy(case["environment"])
    raw["vocabulary"]["predicates"]["owns"]["description"] = 7
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "sort-first", "environment": raw}])
    assert caught.value.to_dict()["code"] == "UnknownSymbol"
    assert caught.value.to_dict().get("path") is None


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize(("field", "replacement"), [("profile", []), ("spec_revision", 7)])
def test_legacy_header_precedes_unknown_sort(field, replacement):
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = deepcopy(next(row for row in corpus if row["id"] == "validation_003"))
    case["environment"][field] = replacement
    with pytest.raises(VEError) as caught:
        run("environment", [case])
    assert caught.value.to_dict()["code"] == "InvalidInput"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("field", ("arguments", "description"))
def test_legacy_earlier_predicate_shape_precedes_later_unknown_sort(field):
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = deepcopy(next(row for row in corpus if row["id"] == "validation_003"))
    case["environment"]["vocabulary"]["predicates"]["deployed"][field] = 7
    with pytest.raises(VEError) as caught:
        run("environment", [case])
    assert caught.value.to_dict()["code"] == "InvalidInput"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("mutation", ("missing_sort", "wrong_entry"))
def test_legacy_sort_description_precedes_later_shape_faults(mutation):
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = deepcopy(next(row for row in corpus if row["id"] == "validation_002"))
    sorts = case["environment"]["vocabulary"]["sorts"]
    if mutation == "missing_sort":
        del sorts["service"]
    else:
        sorts["service"] = []
    with pytest.raises(VEError) as caught:
        run("environment", [case])
    assert caught.value.to_dict()["code"] == "InvalidInput"
    assert caught.value.to_dict().get("path") is None


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_relation_cell_shape_precedes_earlier_dangling_entity():
    from ve.errors import VEError
    corpus = json.loads((SERVICE.parents[4] / "conformance/validation.json").read_text())
    case = deepcopy(next(row for row in corpus if row["id"] == "validation_015"))
    case["model"]["relations"]["owns"][0][1] = 7
    with pytest.raises(VEError) as caught:
        run("model", [case])
    assert caught.value.to_dict()["code"] == "InvalidModel"
    assert caught.value.to_dict()["path"] == "/relations/owns/0/1"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_legacy_envelope_diagnostics_retain_quoted_extra_fields_and_arity():
    from ve.errors import VEError
    cases = {item["id"]: item for item in json.loads(
        (SERVICE.parents[4] / "conformance/validation.json").read_text())}
    with pytest.raises(VEError) as caught:
        run("environment", [cases["validation_001"]])
    assert caught.value.to_dict()["code"] == "InvalidInput"
    assert "'extra'" in caught.value.message

    with pytest.raises(VEError) as caught:
        run("environment", [cases["validation_004"]])
    assert "one to 2 sort identifiers" in caught.value.message

    with pytest.raises(VEError) as caught:
        run("model", [cases["validation_009"]])
    assert caught.value.to_dict()["code"] == "InvalidModel"
    assert "'extra'" in caught.value.message


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("extension", ("soft", "rights", "reports"))
def test_environment_decoder_preserves_composed_vocabulary_blocks(extension):
    if extension == "soft":
        from tests.test_soft_norms_lean import env
        raw = env({"parties": ["user"], "outranking": {"mode": "strict"}})
    elif extension == "rights":
        from tests.test_rights_lean import ARREST, env
        raw = env(ARREST)
    else:
        from tests.test_reports_lean import E0
        raw = E0()
    [row] = run("environment", [{"id": extension, "environment": raw}])
    assert row["status"] == "ok"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("closure@0",),
                                      ("closure@0", "nary@0"), ("order@0",)])
def test_environment_decoder_quotes_the_unknown_argument_sort(profiles):
    from ve.errors import VEError
    raw = raw_environment(profiles)
    raw["vocabulary"]["predicates"]["base"]["arguments"] = ["absent"]
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "quoted", "environment": raw}])
    assert caught.value.to_dict()["code"] == "UnknownSymbol"
    assert "'absent'" in caught.value.message


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_legacy_order_decoder_retains_unknown_sort_class():
    from conformance.order import environment
    from ve.errors import VEError
    raw = environment().to_dict()
    raw["vocabulary"]["predicates"]["p"]["arguments"] = ["absent"]
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "order-sort", "environment": raw}])
    assert caught.value.to_dict()["code"] == "UnknownSymbol"
    assert "'absent'" in caught.value.message


@pytest.mark.parametrize("case_id", ("9faa52839dc3fd3a", "bf433d08b683723b"))
def test_composed_route_keeps_constant_sort_precedence(case_id):
    from ve.errors import VEError
    corpus = SERVICE.parents[4] / "docs/lean-first/quantity-corpus.json.gz"
    with gzip.open(corpus, "rt") as source:
        case = next(item for item in json.load(source) if item["id"] == case_id)
    with pytest.raises(VEError) as caught:
        Environment(case["environment"])
    assert caught.value.to_dict() == {"code": "InvalidInput", "message": "unknown constant sort: c1"}


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("closure@0",),
                                      ("closure@0", "nary@0"), ("order@0",)])
def test_environment_decoder_quotes_unknown_constant_sort_and_field(profiles):
    from ve.errors import VEError
    raw = raw_environment(profiles)
    raw["vocabulary"]["constants"]["x"]["sort"] = "absent"
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "sort", "environment": raw}])
    assert "'absent'" in caught.value.message
    raw = raw_environment(profiles)
    raw["vocabulary"]["sorts"]["item"]["extra"] = 7
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "field", "environment": raw}])
    assert "'extra'" in caught.value.message
    assert caught.value.to_dict()["path"] == "/vocabulary/sorts/item"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("closure@0",),
                                      ("closure@0", "nary@0"), ("order@0",)])
@pytest.mark.parametrize(("name", "code", "fragment"), [
    ("x0", "DuplicateDeclaration", "Schema identifier 'x0' is reserved"),
    ("a" * 65, "ResourceLimit", "Identifier exceeds 64 ASCII bytes"),
    ("BAD", "InvalidInput", "Invalid ASCII identifier: 'BAD'"),
    ("é" * 40, "InvalidInput", "Invalid ASCII identifier"),
    ("é" * 65, "ResourceLimit", "Identifier exceeds 64 ASCII bytes"),
])
def test_environment_declaration_name_codes(profiles, name, code, fragment):
    from ve.errors import VEError
    raw = raw_environment(profiles)
    raw["vocabulary"]["sorts"][name] = raw["vocabulary"]["sorts"].pop("item")
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "name", "environment": raw}])
    assert caught.value.to_dict()["code"] == code
    assert fragment in caught.value.message


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("closure@0",),
                                      ("closure@0", "nary@0"), ("order@0",)])
def test_environment_cross_category_duplicate_keeps_name(profiles):
    from ve.errors import VEError
    raw = raw_environment(profiles)
    raw["vocabulary"]["constants"]["item"] = {"sort": "item", "description": "duplicate"}
    with pytest.raises(VEError) as caught:
        run("environment", [{"id": "duplicate", "environment": raw}])
    assert caught.value.to_dict()["code"] == "DuplicateDeclaration"
    assert "'item'" in caught.value.message


def _single_node_mutations(model):
    """Every JSON node, including container nodes and map field sets."""
    def walk(value, path=()):
        yield path
        if isinstance(value, dict):
            for key, child in value.items():
                yield from walk(child, (*path, key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, (*path, index))

    def replace(original, path, value):
        result = deepcopy(original)
        parent = result
        for step in path[:-1]:
            parent = parent[step]
        if path:
            parent[path[-1]] = value
        else:
            result = value
        return result

    seen = set()
    for path in walk(model):
        for value in (True, 7, "bad!", [], {}):
            mutant = replace(model, path, value)
            key = json.dumps(mutant, sort_keys=True)
            if key not in seen:
                seen.add(key)
                yield mutant
        node = model
        for step in path:
            node = node[step]
        if isinstance(node, dict):
            for key in node:
                mutant = replace(model, path, {k: v for k, v in node.items() if k != key})
                encoded = json.dumps(mutant, sort_keys=True)
                if encoded not in seen:
                    seen.add(encoded)
                    yield mutant
            mutant = replace(model, path, {**node, "extra": 7})
            encoded = json.dumps(mutant, sort_keys=True)
            if encoded not in seen:
                seen.add(encoded)
                yield mutant


def _corpus_inputs():
    """Every frozen conformance model/environment, with duplicate inputs run once."""
    from tools.lean_first_diff import CONFORMANCE

    root = SERVICE.parents[4]
    paths = [root / "conformance" / f"{name}.json" for name in CONFORMANCE]
    seen_environments, seen_models = set(), set()
    for path in paths:
        rows = json.loads(path.read_text())
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("environment"), dict):
                continue
            environment = row["environment"]
            key = json.dumps(environment, sort_keys=True)
            if key not in seen_environments:
                seen_environments.add(key)
                yield "environment", environment, None
            model = row.get("model")
            if isinstance(model, dict):
                key = json.dumps([environment, model], sort_keys=True)
                if key not in seen_models:
                    seen_models.add(key)
                    yield "model", environment, model


def _each_node_mutation(value):
    """Retype and null every node; delete every member of every object."""
    def walk(node, path=()):
        yield path, node
        if isinstance(node, dict):
            for key, child in node.items():
                yield from walk(child, (*path, key))
        elif isinstance(node, list):
            for index, child in enumerate(node):
                yield from walk(child, (*path, index))

    def changed(path, replacement, *, delete=False):
        result = deepcopy(value)
        if not path:
            return replacement
        parent = result
        for step in path[:-1]:
            parent = parent[step]
        if delete:
            del parent[path[-1]]
        else:
            parent[path[-1]] = replacement
        return result

    for path, node in walk(value):
        wrong_type = ([] if isinstance(node, dict) else {}
                      if isinstance(node, list) else 7
                      if isinstance(node, str) else "bad!" if node is None else [])
        yield path, "type", changed(path, wrong_type)
        if node is not None:
            yield path, "null", changed(path, None)
        if isinstance(node, dict):
            for key in node:
                yield (*path, key), "absent", changed((*path, key), None, delete=True)


@pytest.mark.nightly
@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_every_corpus_model_and_environment_node_matches_frozen_python(tmp_path):
    """Compare the full decoder diagnostic, including missing versus null fields.

    JSONL keeps corpus-scale mutations out of memory; both checkers read the
    same file, and the frozen oracle runs once in its isolated checkout.
    """
    from tools import lean_first_oracle
    from ve.backends.lean_service import LeanService
    from ve.backends.diagnostics import checker_error
    from ve.errors import VEError

    cases_path = tmp_path / "mutations.jsonl"
    counts = {"environment": 0, "model": 0}
    with cases_path.open("w") as output:
        for mode, environment, model in _corpus_inputs():
            subject = environment if mode == "environment" else model
            counts[mode] += 1
            for path, operation, mutant in _each_node_mutation(subject):
                case = {"mode": mode, "environment": mutant if mode == "environment" else environment}
                if mode == "model":
                    case["model"] = mutant
                case["origin"] = [counts[mode], list(path), operation]
                output.write(json.dumps(case, ensure_ascii=False) + "\n")
    assert counts["environment"] >= 20 and counts["model"] >= 1100

    answers_path = tmp_path / "oracle-answers.jsonl"
    script = tmp_path / "oracle.py"
    script.write_text(
        "import json\n"
        "from ve.environment import Environment\n"
        "from ve.model import FiniteModel\n"
        "from ve.errors import VEError\n"
        f"with open({str(cases_path)!r}) as cases, open({str(answers_path)!r}, 'w') as answers:\n"
        "    for line in cases:\n"
        "        case = json.loads(line)\n"
        "        try:\n"
        "            env = Environment(case['environment'])\n"
        "            if case['mode'] == 'model':\n"
        "                FiniteModel.from_dict(env, case['model'])\n"
        "            result = {'code': 'ok'}\n"
        "        except VEError as exc:\n"
        "            d = exc.to_dict()\n"
        "            result = {'code': d['code'], 'path': d.get('path')}\n"
        "        answers.write(json.dumps(result) + '\\n')\n"
    )
    assert lean_first_oracle.run(script, scratch=tmp_path) == 0

    def outcomes(service, mode, requests):
        try:
            rows = service.run(mode, requests)
        except VEError as exc:
            if len(requests) > 1:
                middle = len(requests) // 2
                return (outcomes(service, mode, requests[:middle]) +
                        outcomes(service, mode, requests[middle:]))
            return [{"code": exc.code, "path": exc.to_dict().get("path")}]
        return [({"code": "ok"} if row["status"] == "ok" else
                 {"code": checker_error(row["error"]).code, "path": row.get("path")})
                for row in rows]

    with LeanService() as service, cases_path.open() as cases, answers_path.open() as answers:
        while batch := [json.loads(line) for _, line in zip(range(200), cases)]:
            expected = [json.loads(answers.readline()) for _ in batch]
            actual = [None] * len(batch)
            for mode in ("environment", "model"):
                indexes = [i for i, case in enumerate(batch) if case["mode"] == mode]
                requests = [{"id": str(i), "environment": batch[i]["environment"],
                             **({"model": batch[i]["model"]} if mode == "model" else {})}
                            for i in indexes]
                for i, result in zip(indexes, outcomes(service, mode, requests), strict=True):
                    actual[i] = result
            for case, oracle, result in zip(batch, expected, actual, strict=True):
                assert result == oracle, (case["mode"], case["origin"], result, oracle)
        assert answers.readline() == ""


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_model_node_mutations_match_frozen_python_code_and_path(tmp_path, capfd):
    """The frozen decoder is independent of the current Python Lean relay."""
    from tools import lean_first_oracle
    from ve.backends.lean_service import LeanService
    from ve.backends.diagnostics import checker_error

    cases = []
    for profiles in ((), ("closure@0",), ("closure@0", "nary@0"), ("order@0",)):
        raw = raw_environment(profiles)
        model = model_wire(Environment(raw))
        cases += [{"environment": raw, "model": mutant}
                  for mutant in _single_node_mutations(model)]
    payload = tmp_path / "models.json"
    payload.write_text(json.dumps(cases))
    script = tmp_path / "oracle.py"
    script.write_text(
        "import json\n"
        "from ve.environment import Environment\n"
        "from ve.model import FiniteModel\n"
        "from ve.errors import VEError\n"
        f"cases = json.load(open({str(payload)!r}))\n"
        "answers = []\n"
        "for case in cases:\n"
        "    try:\n"
        "        FiniteModel.from_dict(Environment(case['environment']), case['model'])\n"
        "        answers.append({'code': 'ok'})\n"
        "    except VEError as exc:\n"
        "        d = exc.to_dict()\n"
        "        answers.append({'code': d['code'], 'path': d.get('path')})\n"
        "print(json.dumps(answers))\n"
    )
    assert lean_first_oracle.run(script, scratch=tmp_path) == 0
    expected = json.loads(capfd.readouterr().out)
    with LeanService() as service:
        rows = service.run("model", [{"id": str(i), **case} for i, case in enumerate(cases)])
    actual = []
    for case, row in zip(cases, rows, strict=True):
        if row["status"] == "ok":
            actual.append({"code": "ok"})
        else:
            if path := row.get("path"):
                node = case["model"]
                parts = path.lstrip("/").split("/")
                for part in parts[:-1]:
                    node = node[int(part)] if isinstance(node, list) else node[part]
                assert isinstance(node, (dict, list)), (path, case)
            actual.append({"code": checker_error(row["error"]).code, "path": row.get("path")})
    assert actual == expected


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_environment_node_mutations_match_frozen_python_code_and_path(tmp_path, capfd):
    from tools import lean_first_oracle
    from ve.backends.lean_service import LeanService
    from ve.backends.diagnostics import checker_error

    cases = [mutant for profiles in ((), ("closure@0",),
             ("closure@0", "nary@0"), ("order@0",))
             for mutant in _single_node_mutations(raw_environment(profiles))]
    payload = tmp_path / "environments.json"
    payload.write_text(json.dumps(cases))
    script = tmp_path / "oracle.py"
    script.write_text(
        "import json\n"
        "from ve.environment import Environment\n"
        "from ve.errors import VEError\n"
        f"cases = json.load(open({str(payload)!r}))\n"
        "answers = []\n"
        "for case in cases:\n"
        "    try:\n"
        "        Environment(case)\n"
        "        answers.append({'code': 'ok'})\n"
        "    except VEError as exc:\n"
        "        d = exc.to_dict()\n"
        "        answers.append({'code': d['code'], 'path': d.get('path')})\n"
        "print(json.dumps(answers))\n"
    )
    assert lean_first_oracle.run(script, scratch=tmp_path) == 0
    expected = json.loads(capfd.readouterr().out)
    with LeanService() as service:
        rows = service.run("environment", [{"id": str(i), "environment": case}
                                           for i, case in enumerate(cases)])
    actual = []
    for row in rows:
        if row["status"] == "ok":
            actual.append({"code": "ok"})
        else:
            actual.append({"code": checker_error(row["error"]).code, "path": row.get("path")})
    assert actual == expected


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("mutant", ["drop_path", "change_code"])
def test_model_oracle_detects_seeded_decoder_faults(mutant, monkeypatch, tmp_path, capfd):
    """Seed the two reported failure classes into genuine service responses."""
    from ve.backends.lean_service import LeanService

    original = LeanService.run
    seeded = False

    def altered(self, mode, cases, **kwargs):
        nonlocal seeded
        rows = original(self, mode, cases, **kwargs)
        if mode == "model" and not seeded:
            rows = deepcopy(rows)
            for row in rows:
                if row["status"] != "error" or "path" not in row:
                    continue
                if mutant == "drop_path":
                    del row["path"]
                else:
                    row["error"] = row["error"].replace("InvalidModel:", "InvalidInput:", 1)
                seeded = True
                break
        return rows

    monkeypatch.setattr(LeanService, "run", altered)
    with pytest.raises(AssertionError):
        test_model_node_mutations_match_frozen_python_code_and_path(tmp_path, capfd)
    assert seeded


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("closure@0",), ("closure@0", "nary@0"),
                                     ("order@0",), ("data@0", "definitions@0")])
def test_model_constant_fault_retains_path_across_families(profiles):
    from ve.errors import VEError
    env = Environment(raw_environment(profiles))
    model = model_wire(env)
    model["constants"]["x"] = "absent"
    with pytest.raises(VEError) as caught:
        run("model", [{"id": "constant", "environment": env.to_dict(), "model": model}])
    assert caught.value.to_dict()["path"] == "/constants/x"


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize(("count", "path"), [(1001, "/domains/item"),
                                             (100001, "/relations")])
def test_model_budget_fault_retains_path(count, path):
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    model = model_wire(env)
    if path.startswith("/domains"):
        model["domains"]["item"] = [f"i{index}" for index in range(count)]
    else:
        model["relations"]["base"] = [[f"i{index}"] for index in range(count)]
    with pytest.raises(VEError) as caught:
        run("model", [{"id": "limit", "environment": env.to_dict(), "model": model}])
    assert caught.value.to_dict()["path"] == path


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("order@0",)])
def test_environment_and_model_ids(profiles):
    env = Environment(raw_environment(profiles))
    model = FiniteModel.from_dict(env, model_wire(env))
    case = {"id": "binding", "environment": env.to_dict()}
    assert run("environment", [case])[0]["environment_id"] == env.environment_id
    assert run("model", [{**case, "model": model.to_dict()}])[0]["model_id"] == model.model_id


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_source_and_meaning_ids():
    env = Environment(raw_environment(()))
    case = {"id": "binding", "environment": env.to_dict()}
    assert run("identity", [{**case, "kind": "source", "source": "true.\n"}])[0][
        "identity_id"] == source_id("true.\n", env)
    assert run("identity", [{**case, "kind": "meaning", "ast": formula_to_data(env, Top())}])[0][
        "identity_id"] == meaning_id(env, Top())


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("data@0",), ("definitions@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("order@0",)])
def test_standalone_check_matches_python_identity(profiles):
    from ve.ast import Document, check_document, check_formula, document_to_data
    env = Environment(raw_environment(profiles))
    formula = Top()
    case = {"id": "check", "environment": env.to_dict()}
    check_formula(env, formula)
    row = run("check", [{**case, "ast": formula_to_data(env, formula)}])[0]
    assert row == {"id": "check", "status": "ok", "well_typed": True,
                   "meaning_id": meaning_id(env, formula)}
    document = Document((formula,))
    check_document(env, document)
    row = run("check", [{**case, "ast": document_to_data(env, document)}])[0]
    assert row["well_typed"] is True
    assert row["meaning_id"] == meaning_id(env, document)


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_standalone_check_rejects_undeclared_predicate():
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    with pytest.raises(VEError):
        run("check", [{"id": "bad", "environment": env.to_dict(),
                       "ast": ["unary", "missing", ["const", "x"]]}])


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
def test_public_typing_uses_standalone_lean(monkeypatch):
    from ve.ast import Document, Unary, Const, check_document, check_formula
    from ve.errors import VEError
    env = Environment(raw_environment(()))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert check_formula(env, Top()) == Top()
    assert check_document(env, Document((Top(),))) == Document((Top(),))
    with pytest.raises(VEError):
        check_formula(env, Unary("missing", Const("x")))


def _typing_error(env, formula):
    from ve.ast import check_formula
    from ve.errors import VEError
    try:
        check_formula(env, formula)
    except VEError as exc:
        return exc.code, exc.message
    return None


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("profiles", [(), ("norms@0",), ("definitions@0",), ("data@0",),
    ("closure@0",), ("closure@0", "nary@0"), ("closure@0", "nary@0", "definitions@0"),
    ("closure@0", "norms@0"), ("order@0",)])
def test_lean_typing_diagnostics_match_python(profiles, monkeypatch):
    """The decoder's rejection is named with Python's code and message."""
    from ve.ast import (Atom, Binary, Const, Eq, Exists, Forall, Named, Reach, Unary, Var)
    env = Environment(raw_environment(profiles))
    cases = [Unary("missing", Const("x")), Unary("base", Const("absent")),
             Binary("base", Const("x"), Const("x")), Forall("absent", Top()),
             Exists("item", Unary("base", Var(1))), Eq(Const("x"), Var(0))]
    if "closure@0" in profiles:
        cases += [Reach("star", Named("base"), Const("x"), Const("x")),
                  Reach("star", Named("absent"), Const("x"), Const("x"))]
    if "nary@0" in profiles:
        cases += [Atom("triple", (Const("x"), Const("x"))), Atom("absent", (Const("x"),) * 3)]
    for formula in cases:
        expected = _typing_error(env, formula)
        assert expected is not None, formula
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert _typing_error(env, formula) == expected, formula
        monkeypatch.delenv("VE_AUTHORITY")


def _legacy_environment(kind):
    from ve.environment import (LANGUAGE, PROFILE, SPEC_REVISION as V0_REV, CLOSURE_LANGUAGE,
                                CLOSURE_PROFILES, CLOSURE_REVISION, ORDER_PROFILES, ORDER_REVISION)
    raw = raw_environment(())
    raw.pop("profiles")
    if kind == "v0":
        raw.update(language=LANGUAGE, spec_revision=V0_REV, profile=PROFILE)
    else:
        raw.update(language=CLOSURE_LANGUAGE,
                   spec_revision=CLOSURE_REVISION if kind == "closure" else ORDER_REVISION,
                   profiles=list(CLOSURE_PROFILES if kind == "closure" else ORDER_PROFILES))
    return Environment(raw)


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("kind", ["v0", "closure", "order"])
def test_lean_typing_on_legacy_envelopes_matches_python(kind, monkeypatch):
    from ve.ast import Binary, Const, Forall, Unary, Var, check_formula
    env = _legacy_environment(kind)
    formula = Forall("item", Unary("base", Var(0)))
    monkeypatch.setenv("VE_AUTHORITY", "lean")
    assert check_formula(env, formula) == formula
    row = run("check", [{"id": "c", "environment": env.to_dict(), "ast": formula_to_data(env, formula)}])[0]
    assert row["meaning_id"] == meaning_id(env, formula)
    monkeypatch.delenv("VE_AUTHORITY")
    for bad in (Unary("missing", Const("x")), Binary("base", Const("x"), Const("x"))):
        expected = _typing_error(env, bad)
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert _typing_error(env, bad) == expected
        monkeypatch.delenv("VE_AUTHORITY")


def _nested(leaves):
    from ve.ast import And
    level = [Top() for _ in range(leaves)]
    while len(level) > 1:
        level = [And(level[i], level[i + 1]) if i + 1 < len(level) else level[i]
                 for i in range(0, len(level), 2)]
    return level[0]


def _negated(formula, times):
    from ve.ast import Not
    for _ in range(times):
        formula = Not(formula)
    return formula


@pytest.mark.skipif(not SERVICE.exists(), reason="Lean service has not been built")
@pytest.mark.parametrize("kind", ["current", "order", "closure", "closure+nary", "v0"])
def test_lean_typing_budget_diagnostics_match_python(kind, monkeypatch):
    """Budget rejections are named where `_Checker` meets them, with its message."""
    from ve.ast import Add, And, Const, Document, Le, Num, Unary, check_document
    from ve.errors import VEError
    profiles = {"current": (), "order": ("order@0",), "closure": ("closure@0",),
                "closure+nary": ("closure@0", "nary@0")}
    env = _legacy_environment("v0") if kind == "v0" else Environment(raw_environment(profiles[kind]))
    deep = _negated(Top(), 64)
    cases = [deep, _negated(_nested(5000), 2), And(Unary("missing", Const("x")), deep),
             And(deep, Unary("missing", Const("x"))), Document((_nested(3000), _nested(3000)))]
    if kind == "order":
        term = Num(0)
        for _ in range(64):
            term = Add(Num(1), term)
        cases.append(Le(term, Num(0)))

    def error(case):
        if type(case) is Document:
            try:
                check_document(env, case)
            except VEError as exc:
                return exc.code, exc.message
            return None
        return _typing_error(env, case)

    for case in cases:
        expected = error(case)
        assert expected is not None and expected[0] in ("ResourceLimit", "UnknownSymbol")
        monkeypatch.setenv("VE_AUTHORITY", "lean")
        assert error(case) == expected
        monkeypatch.delenv("VE_AUTHORITY")
