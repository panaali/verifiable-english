import json
import subprocess
import sys

import pytest

from conformance.p0 import MODEL, VOCAB, envelope, environment
from ve.document import check_document, coverage, load_document, render_document
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.ast import Top
from ve.model import FiniteModel
from ve.readings import check_readings, plan_choices


def write_doc(tmp_path, text, units, **extra):
    env_json = extra.pop("environment_json", environment())
    front = {"format": "ve-document@1", "environment": env_json, "units": units, **extra}
    path = tmp_path / "sample.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front).encode() + b"\n---\n" + text)
    return path


def unit(uid, start, stop, kind="asserted", meaning="specified", content=None):
    return {"id": uid, "span": [start, stop], "kind": kind, "meaning": meaning,
            "support": "assumption", "content": content}


def test_byte_partition_and_vacuity(tmp_path):
    source = "Café. Next.\n".encode()
    cut = len("Café. ".encode())
    path = write_doc(tmp_path, source, [unit("a", 0, cut, content={"ast": ["top"]}),
                                        unit("b", cut, len(source), ["unformalised", "future_profile"],
                                             {"unformalised": "future_profile"})])
    doc = load_document(path)
    report = coverage(doc)
    assert report["source_bytes"] == report["accounted_bytes"] == len(source)
    assert report["unformalised_reasons"] == {"future_profile": 1}
    assert check_document(path)["premises"]["status"] == "model"
    assert "Café" in render_document(path)


@pytest.mark.parametrize("spans", [[[0, 2], [3, 6]], [[0, 4], [3, 6]], [[3, 6], [0, 3]],
                                   [[0, 3], [3, 5]]])
def test_partition_rejects_gaps_overlap_order_and_tail(tmp_path, spans):
    path = write_doc(tmp_path, b"abcdef", [unit("a", *spans[0]), unit("b", *spans[1])])
    with pytest.raises(VEError, match="partition"):
        load_document(path)


def test_utf8_cut_and_nested_kind(tmp_path):
    source = "é".encode()
    nested = ["attributed", "alice", "believes", ["hedged", "likely",
              ["causal", "because", "asserted", "asserted"]]]
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), nested, content={"ast": ["top"]})])
    assert load_document(path)["units"][0]["kind"] == nested
    path = write_doc(tmp_path, source, [unit("a", 0, 1), unit("b", 1, 2)])
    with pytest.raises(VEError, match="UTF-8"):
        load_document(path)


def test_reading_route_never_disjoins_mixed_kinds():
    assertions = [{"id": str(i), "readings": [{"kind": "asserted", "content": ["top"]}] * 2}
                  for i in range(12)]
    assert plan_choices(assertions)["route"] == "assertion-disjunction"
    mixed = [{"id": str(i), "readings": [{"kind": "norm", "content": None},
                                            {"kind": ["unformalised", "open_term"], "content": None}]}
             for i in range(7)]
    assert plan_choices(mixed[:1])["route"] == "enumerate"
    assert len(plan_choices(mixed[:1])["choices"]) == 2
    assert plan_choices(mixed)["route"] == "UNKNOWN"


def test_unbound_fence_rejected(tmp_path):
    path = write_doc(tmp_path, b"text\n```ve a\ntrue.\n```\n", [unit("a", 0, 5)])
    with pytest.raises(VEError, match="unbound VE fence"):
        load_document(path)


def test_assertion_cannot_disappear_into_metadata(tmp_path):
    source = b"A claim.\n"
    path = write_doc(tmp_path, source, [unit("a", 0, len(source))])
    with pytest.raises(VEError, match="content or a reading set"):
        load_document(path)
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": ["top"]})],
                     unreviewed_field=True)
    with pytest.raises(VEError, match="unknown document metadata"):
        load_document(path)


def test_assertion_readings_all_some_none_have_checked_evidence():
    env = Environment(envelope(VOCAB))
    p = ["unary", "senior", ["const", "alice"]]
    q = ["not", p]
    rs = [{"id": "s", "version": 1, "readings": [{"kind": "asserted", "content": p},
                                                    {"kind": "asserted", "content": q}]}]
    some = check_readings(env, rs, p)
    assert some["verdict"] == "SOME"
    assert some["proof"]["certificate"]
    assert some["countermodel"]["model_id"]
    assert check_readings(env, rs, ["top"])["verdict"] == "ALL"
    compatible = [{"id": "t", "version": 1, "readings": [{"kind": "asserted", "content": p},
                                                          {"kind": "asserted", "content": ["top"]}]}]
    assert check_readings(env, compatible, ["bottom"])["verdict"] == "NONE"


def test_document_p0_admission_and_cli(tmp_path):
    source = b"This holds.\n"
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"], "unit": "a"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": ["top"]})], graph=graph)
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    output = subprocess.run([sys.executable, "-m", "ve", "document", "coverage", str(path)],
                            check=True, capture_output=True, text=True)
    assert json.loads(output.stdout)["accounted_bytes"] == len(source)


def test_quoted_content_needs_bridge_in_document(tmp_path):
    source = b"Alice says so.\n"
    quoted = unit("a", 0, len(source), ["attributed", "alice", "says", "asserted"],
                  content={"ast": ["top"]})
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"], "unit": "a"}]}
    path = write_doc(tmp_path, source, [quoted], graph=graph)
    with pytest.raises(VEError, match="bridge leaf"):
        check_document(path)
    graph["nodes"][0]["label"] = "bridge:accepts(alice,a)"
    path = write_doc(tmp_path, source, [quoted], graph=graph)
    result = check_document(path)
    assert result["coverage"]["residual"]["bridge_leaves"] == 1
    assert result["premises"]["status"] == "model"


def test_reading_identity_and_narrowing_schema(tmp_path):
    source = b"Maybe.\n"
    env = Environment(environment())
    mid = meaning_id(env, Top())
    reading = {"id": "r1", "kind": "asserted", "meaning_id": mid, "content": ["top"],
               "admission": {"who": "alice", "why": "literal", "distinguishing_models": {}}}
    rs = {"id": "s1", "unit": "a", "version": 1, "status": "open", "readings": [reading]}
    narrowing = {"id": "n1", "set": "s1", "version": 1, "keeps": ["r1"],
                 "by": "alice", "reason_spans": ["a"]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[rs], narrowings=[narrowing])
    assert coverage(load_document(path))["residual"]["unresolved_reading_sets"] == 1
    assert "This sentence could mean" in render_document(path)
    rs["readings"][0]["meaning_id"] = "wrong"
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[rs], narrowings=[narrowing])
    with pytest.raises(VEError, match="meaning id"):
        load_document(path)


def test_distinguishing_model_is_replayed(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    q = ["not", p]
    model = FiniteModel.from_dict(env, MODEL)
    mid = model.model_id
    readings = []
    for rid, ast, other in (("p", p, "notp"), ("notp", q, "p")):
        from ve.ast import formula_from_data
        readings.append({"id": rid, "kind": "asserted",
                         "meaning_id": meaning_id(env, formula_from_data(env, ast)), "content": ast,
                         "admission": {"who": "alice", "why": "competing interpretation",
                                       "distinguishing_models": {other: mid}}})
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": readings, "models": {mid: MODEL}}
    source = b"Claim.\n"
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     environment_json=env_json, reading_sets=[rs])
    assert load_document(path)["reading_plan"]["route"] == "assertion-disjunction"
    rs["models"][mid] = {**MODEL, "relations": {**MODEL["relations"], "senior": []}}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     environment_json=env_json, reading_sets=[rs])
    with pytest.raises(VEError, match="model id"):
        load_document(path)
