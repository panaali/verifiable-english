import json
import subprocess
import sys

import pytest

from conformance.p0 import MODEL, VOCAB, definitions_envelope, envelope, environment
from ve.document import _check_narrowing_choices, check_document, coverage, load_document, render_document
from ve.environment import Environment
from ve.errors import VEError
from ve.identity import meaning_id
from ve.ast import Top, Exists, Unary, Var
from ve.ast import formula_from_data
from ve.model import FiniteModel
from ve.readings import check_readings, plan_choices
from tests.test_norms import environment as norm_environment, permission, rule
from ve.norms import NormDocument
from ve.ast import formula_to_data


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


def test_mixed_csam_norm_is_checked_without_losing_rest_of_paragraph(tmp_path):
    env = norm_environment({"generate_csam_permitted": permission(
        act="{0} generate child sexual abuse material", args=("assistant",))},
        sorts=("assistant",))
    norm = rule("no-csam", "generate_csam_permitted", False)
    norm_doc = NormDocument(env, [norm])
    header = b"Claude should never:\n"
    bullets = (
        "* Provide serious uplift to those seeking to create biological, chemical, nuclear, or radiological weapons with the potential for mass casualties.\n"
        "* Provide serious uplift to attacks on critical infrastructure (power grids, water systems, financial systems) or critical safety systems.\n"
        "* Create cyberweapons or malicious code that could cause significant damage if deployed.\n"
        "* Take actions that clearly and substantially undermine Anthropic’s ability to oversee and correct advanced AI models (see [Being broadly safe](#being-broadly-safe) below).\n"
        "* Engage or assist in an attempt to kill or disempower the vast majority of humanity or the human species as whole.\n"
        "* Engage or assist any individual or group with an attempt to seize unprecedented and illegitimate degrees of absolute societal, military, or economic control.\n"
        "* Generate child sexual abuse material (CSAM).\n\n").encode()
    assert len(bullets) == 874  # The pilot review's complete u0165 span.
    source = header + bullets
    cut = source.index(b"* Generate child sexual abuse material")
    parts = [
        {**unit("remaining-text", len(header), cut, ["unformalised", "causation"],
                 {"unformalised": "causation"}), "status": "UNFORMALISED"},
        {**unit("csam-rule", cut, len(source), "norm", content=norm.to_dict()),
         "status": "CHECKED"},
    ]
    graph = {"root": "layer", "nodes": [{
        "name": "layer", "ast": formula_to_data(env, norm_doc.elaborate("generate_csam_permitted")),
        "label": "layer:norms:generate_csam_permitted"}]}
    classification = {"name": "csam-classification", "arguments": ["material"],
                      "decided_by": "policy-reviewer", "necessary": [], "sufficient": [],
                      "factors": ["Which material falls within this class is unresolved."],
                      "precedents": [], "jurisdiction": "policy", "version": 1}
    path = write_doc(tmp_path, source, [
        {**unit("u0164", 0, len(header), "meta"), "status": "LABELLED"},
        {"id": "u0165", "span": [len(header), len(source)],
         "status": "MIXED", "parts": parts}],
                     environment_json=env.to_dict(), graph=graph,
                     open_terms=[classification])
    loaded = load_document(path)
    assert [u.get("parent_id") for u in loaded["units"]] == [None, "u0165", "u0165"]
    result = check_document(path)
    assert result["admission"]["admitted"]
    assert result["admission"]["kinds"] == ["meta", ["unformalised", "causation"], "norm"]
    assert result["admission"]["report"]["assumptions"][0]["label"] == graph["nodes"][0]["label"]
    assert result["coverage"]["bytes_by_status"] == {
        "LABELLED": len(header), "UNFORMALISED": cut - len(header),
        "CHECKED": len(source) - cut}
    assert result["coverage"]["accounted_bytes"] == len(source)
    assert result["coverage"]["residual"]["open_terms"] == 1
    assert "must not generate child sexual abuse material" in render_document(path)


@pytest.mark.parametrize("spans", [[[0, 2], [3, 6]], [[0, 4], [3, 6]],
                                   [[0, 3], [3, 5]]])
def test_mixed_parts_reject_gap_overlap_and_tail(tmp_path, spans):
    parts = [{**unit("a", *spans[0]), "status": "LABELLED"},
             {**unit("b", *spans[1]), "status": "LABELLED"}]
    path = write_doc(tmp_path, b"abcdef", [{"id": "whole", "span": [0, 6],
                                              "status": "MIXED", "parts": parts}])
    with pytest.raises(VEError, match="partition"):
        load_document(path)


def test_unresolved_norm_reading_does_not_activate_stale_unit_content(tmp_path):
    env = norm_environment({"permitted": permission()})
    source = b"This rule has another reading.\n"
    old = rule("old", "permitted", True).to_dict()
    candidate = {"id": "choice", "kind": "norm", "meaning_id": "pending",
                 "content": None, "admission": {"who": "reviewer", "why": "pending",
                                                 "distinguishing_models": {}}}
    reading_set = {"id": "readings", "unit": "rule", "version": 1,
                   "status": "open", "readings": [candidate]}
    path = write_doc(tmp_path, source,
                     [unit("rule", 0, len(source), "norm", content=old)],
                     environment_json=env.to_dict(), reading_sets=[reading_set])
    loaded = load_document(path)
    assert loaded["norms"].rules == ()
    assert coverage(loaded)["bytes_by_status"] == {"OPEN": len(source)}
    assert check_document(path)["premises"]["status"] == "UNKNOWN"


@pytest.mark.parametrize("env,broken,diagnostic", [
    (norm_environment({}), rule("bad", "missing", True), "regulated predicate missing"),
    (norm_environment({"permitted": permission()}),
     rule("bad", "permitted", True, Unary("missing", Var(0))), "Unknown predicate"),
    (Environment(environment()), rule("bad", "missing", True), "norms@0 is required"),
])
def test_every_active_norm_is_validated_without_a_graph(tmp_path, env, broken, diagnostic):
    source = b"Rule.\n"
    path = write_doc(tmp_path, source,
                     [unit("rule", 0, len(source), "norm", content=broken.to_dict())],
                     environment_json=env.to_dict())
    with pytest.raises(VEError, match=diagnostic):
        check_document(path)


def test_unresolved_norm_never_produces_a_false_inconsistency_or_layer(tmp_path):
    env = norm_environment({"permitted": permission()})
    source = b"Rule.\nSome act is permitted.\n"
    cut = len(b"Rule.\n")
    candidate = {"id": "choice", "kind": "norm", "meaning_id": "pending",
                 "content": None, "admission": {"who": "reviewer", "why": "pending",
                                                 "distinguishing_models": {}}}
    reading_set = {"id": "readings", "unit": "rule", "version": 1,
                   "status": "open", "readings": [candidate]}
    existence = formula_to_data(env, Exists("act", Unary("permitted", Var(0))))
    path = write_doc(tmp_path, source,
                     [unit("rule", 0, cut, "norm", content=rule("allow", "permitted", True).to_dict()),
                      unit("claim", cut, len(source), content={"ast": existence})],
                     environment_json=env.to_dict(), reading_sets=[reading_set])
    assert check_document(path)["premises"]["status"] == "UNKNOWN"
    assert query(path, tmp_path, existence)["verdict"] == "UNKNOWN"
    graph = {"root": "layer", "nodes": [{"name": "layer", "ast": ["top"],
                                           "label": "layer:norms:permitted"}]}
    path = write_doc(tmp_path, source,
                     [unit("rule", 0, cut, "norm", content=rule("allow", "permitted", True).to_dict()),
                      unit("claim", cut, len(source), content={"ast": existence})],
                     environment_json=env.to_dict(), reading_sets=[reading_set], graph=graph)
    with pytest.raises(VEError, match="needs an elaborator"):
        check_document(path)


def test_active_norm_layer_enters_readings_queries(tmp_path):
    env = norm_environment({"permitted": permission()})
    source = b"All acts may be done.\n"
    norm = rule("allow", "permitted", True)
    path = write_doc(tmp_path, source,
                     [unit("rule", 0, len(source), "norm", content=norm.to_dict())],
                     environment_json=env.to_dict())
    loaded = load_document(path)
    assert loaded["units"][0]["meaning_id"] == loaded["norms"].meaning_id("allow")
    conclusion = formula_to_data(env, loaded["norms"].elaborate("permitted"))
    assert check_document(path)["premises"]["status"] == "model"
    assert query(path, tmp_path, conclusion)["verdict"] == "ALL"


def test_quoted_norm_renders_its_own_opposite_content(tmp_path):
    env = norm_environment({"permitted": permission()})
    source = b"Allow.\nAlice forbids.\n"
    cut = len(b"Allow.\n")
    path = write_doc(tmp_path, source,
                     [unit("allow", 0, cut, "norm", content=rule("same", "permitted", True).to_dict()),
                      unit("quote", cut, len(source), ["attributed", "alice", "says", "norm"],
                           content=rule("same", "permitted", False).to_dict())],
                     environment_json=env.to_dict())
    rendered = render_document(path)
    assert "may be done" in rendered
    assert "must not be done" in rendered
    assert rendered.index("may be done") < rendered.index("must not be done")


@pytest.mark.parametrize("meaning,content", [
    ({"unformalised": "future_profile"}, None),
    ({"open": ["uncertain"]}, None),
])
def test_explicit_label_cannot_hide_unresolved_meaning(tmp_path, meaning, content):
    env = environment()
    open_terms = [{"name": "uncertain", "arguments": [], "decided_by": "reviewer",
                   "necessary": [], "sufficient": [], "factors": [], "precedents": [],
                   "jurisdiction": "local", "version": 1}] if "open" in meaning else []
    source = b"Text.\n"
    path = write_doc(tmp_path, source,
                     [{**unit("part", 0, len(source), "meta", meaning, content),
                       "status": "LABELLED"}], open_terms=open_terms)
    with pytest.raises(VEError, match="status contradicts"):
        load_document(path)


def test_explicit_status_must_match_active_reading_override(tmp_path):
    env = Environment(environment())
    source = b"Claim.\n"
    rs = {"id": "s", "unit": "claim", "version": 1, "status": "open",
          "readings": [reading(env, "r", ["top"])]}
    path = write_doc(tmp_path, source,
                     [{**unit("claim", 0, len(source), "asserted", content={"ast": ["top"]}),
                       "status": "CHECKED"}], reading_sets=[rs])
    with pytest.raises(VEError, match="status contradicts"):
        load_document(path)


def test_mixed_parent_span_requires_integer_byte_offsets(tmp_path):
    source = b"abcdef"
    parts = [{**unit("a", 0, 3), "status": "LABELLED"},
             {**unit("b", 3, 6), "status": "LABELLED"}]
    path = write_doc(tmp_path, source,
                     [{"id": "whole", "span": [0.0, 6.0], "status": "MIXED", "parts": parts}])
    with pytest.raises(VEError, match="partitioned parts"):
        load_document(path)


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


@pytest.mark.parametrize("surface,formula", [("english", "This holds in all cases."),
                                             ("strict", "true.")])
def test_document_fence_parses_one_checked_sentence(tmp_path, monkeypatch, surface, formula):
    from ve.surface import unambiguity
    source = b"The claim.\n"
    path = write_doc(tmp_path, source + b"```ve a\n" + formula.encode() + b"\n```\n",
                     [{**unit("a", 0, len(source), content={"fence": "a"}),
                       "surface": surface}])
    calls = []
    original = unambiguity.require_unique_derivation

    def checked(*args, **kwargs):
        calls.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(unambiguity, "require_unique_derivation", checked)
    doc = load_document(path)
    assert doc["units"][0]["content"] == ["top"]
    assert calls == ([True] if surface == "english" else [])
    assert check_document(path)["premises"]["status"] == "model"


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


def test_some_reports_the_winning_choice_vacuity():
    env = Environment(envelope(VOCAB))
    p = ["unary", "senior", ["const", "alice"]]
    q = ["unary", "in_finance", ["const", "alice"]]
    rs = [{"id": "s", "version": 1,
           "readings": [{"kind": "asserted", "content": p},
                        {"kind": "asserted", "content": q}]}]
    result = check_readings(env, rs, ["bottom"], fixed=[["not", p]])
    assert result["verdict"] == "SOME"
    assert result["proof"]["choice"] == ["readings:s@1:0"]
    assert result["vacuous"] is True
    assert result["premises"]["status"] == "INCONSISTENT"
    assert result["proof"]["premises"] == result["premises"]
    assert result["countermodel"]["choice"] == ["readings:s@1:1"]


def test_document_p0_admission_and_cli(tmp_path):
    source = b"This holds.\n"
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"], "unit": "a"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": ["top"]})], graph=graph)
    result = check_document(path)
    assert result["admission"]["admitted"] is True
    output = subprocess.run([sys.executable, "-m", "ve", "document", "coverage", str(path)],
                            check=True, capture_output=True, text=True)
    assert json.loads(output.stdout)["accounted_bytes"] == len(source)
    prior = result["document_id"]
    changed = unit("a", 0, len(source), content={"ast": ["top"]})
    changed["support"] = "observation"
    path = write_doc(tmp_path, source, [changed], graph=graph)
    assert check_document(path)["document_id"] != prior


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
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text('["top"]')
    output = subprocess.run([sys.executable, "-m", "ve", "document", "readings", str(path),
                             "--conclusion", str(conclusion), "--narrowing", "n1"],
                            check=True, capture_output=True, text=True)
    narrowed = json.loads(output.stdout)
    assert narrowed["verdict"] == "ALL"
    assert narrowed["narrowing"] == "narrowing:n1"
    before = check_document(path)
    weighted = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                         reading_sets=[rs], narrowings=[narrowing],
                         weights=[{"set": "s1", "by": "translator", "values": {"r1": 0.8}}])
    after = check_document(weighted)
    assert before["reading_plan"] == after["reading_plan"]
    assert before["document_id"] == after["document_id"]
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


def test_narrowing_rejects_excluded_graph_choice():
    meta = {"reading_sets": [{"id": "s", "version": 1,
                               "readings": [{"id": "left"}, {"id": "right"}]}],
            "narrowings": [{"id": "n", "set": "s", "version": 1, "keeps": ["left"]}]}
    _check_narrowing_choices(meta, ["narrowing:n", "readings:s@1:0"])
    with pytest.raises(VEError, match="conflicts with narrowing"):
        _check_narrowing_choices(meta, ["narrowing:n", "readings:s@1:1"])


def reading(env, rid, ast, kind="asserted"):
    return {"id": rid, "kind": kind,
            "meaning_id": meaning_id(env, formula_from_data(env, ast)), "content": ast,
            "admission": {"who": "reviewer", "why": "recorded interpretation",
                          "distinguishing_models": {}}}


def separate_readings(env, rs):
    from ve.evaluate import evaluate
    candidates = [MODEL, {**MODEL, "relations": {**MODEL["relations"], "senior": []}}]
    models = {FiniteModel.from_dict(env, data).model_id: data for data in candidates}
    rs["models"] = models
    for r in rs["readings"]:
        for other in rs["readings"]:
            if r is other:
                continue
            for mid, data in models.items():
                model = FiniteModel.from_dict(env, data)
                left = evaluate(env, formula_from_data(env, r["content"]), model, trace=False).value
                right = evaluate(env, formula_from_data(env, other["content"]), model, trace=False).value
                if left != right:
                    r["admission"]["distinguishing_models"][other["id"]] = mid
                    break
            else:
                raise AssertionError("test readings need a separating model")
    used = {mid for r in rs["readings"]
            for mid in r["admission"]["distinguishing_models"].values()}
    rs["models"] = {mid: models[mid] for mid in used}


def query(path, tmp_path, ast, narrowing=None):
    conclusion = tmp_path / "conclusion.json"
    conclusion.write_text(json.dumps(ast))
    command = [sys.executable, "-m", "ve", "document", "readings", str(path),
               "--conclusion", str(conclusion)]
    if narrowing:
        command += ["--narrowing", narrowing]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def test_quoted_candidate_cannot_enter_p0_as_assertion(tmp_path):
    source = b"Alice says so.\n"
    env = Environment(environment())
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": [reading(env, "r", ["top"], ["attributed", "alice", "says", "asserted"])]}
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"],
                                           "label": "readings:s@1:0"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[rs], graph=graph)
    with pytest.raises(VEError, match="non-assertion reading admission"):
        check_document(path)
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[rs])
    assert check_document(path)["premises"]["status"] == "UNKNOWN"


@pytest.mark.parametrize("reading_kind,reading_ast,status", [
    ("asserted", ["not", ["unary", "senior", ["const", "alice"]]], "authored"),
    (["attributed", "alice", "says", "asserted"],
     ["unary", "senior", ["const", "alice"]], "open"),
    ("asserted", ["unary", "senior", ["const", "alice"]], "open"),
])
def test_active_readings_cannot_be_bypassed_by_unit_reference(
        tmp_path, reading_kind, reading_ast, status):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    source = b"Claim.\n"
    rs = {"id": "s", "unit": "a", "version": 1, "status": status,
          "readings": [reading(env, "r", reading_ast, reading_kind)]}
    if status == "authored":
        rs["signature"] = "alice"
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": p, "unit": "a"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": p})],
                     environment_json=env_json, reading_sets=[rs], graph=graph)
    if status == "authored":
        assert query(path, tmp_path, p)["verdict"] == "NONE"
    with pytest.raises(VEError, match="not admitted"):
        check_document(path)
    if reading_kind == "asserted" and reading_ast == p:
        graph["nodes"][0] = {"name": "claim", "ast": p, "label": "readings:s@1:0"}
        path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": p})],
                         environment_json=env_json, reading_sets=[rs], graph=graph)
        report = check_document(path)["admission"]["report"]
        assert report["assumptions"][0]["label"] == "readings:s@1:0"


def test_active_readings_cannot_be_bypassed_by_bridge_reference(tmp_path):
    env = Environment(environment())
    source = b"Alice says so.\n"
    quoted = unit("a", 0, len(source), ["attributed", "alice", "says", "asserted"],
                  content={"ast": ["top"]})
    rs = {"id": "s", "unit": "a", "version": 1, "status": "authored",
          "signature": "alice", "readings": [reading(env, "r", ["top"])]}
    for node in ({"name": "claim", "ast": ["top"], "label": "bridge:accepts(alice,a)"},
                 {"name": "claim", "ast": ["top"], "unit": "a",
                  "label": "bridge:accepts(alice,a)"}):
        path = write_doc(tmp_path, source, [quoted], reading_sets=[rs],
                         graph={"root": "claim", "nodes": [node]})
        with pytest.raises(VEError, match="not admitted"):
            check_document(path)


def test_document_vacuity_includes_fixed_assertions_outside_graph(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    source = b"Positive.\nNegative.\n"
    cut = len(b"Positive.\n")
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": p, "unit": "a"}]}
    units = [unit("a", 0, cut, content={"ast": p}),
             unit("b", cut, len(source), content={"ast": ["not", p]})]
    path = write_doc(tmp_path, source, units, environment_json=env_json, graph=graph)
    result = check_document(path)
    assert result["premises"]["status"] == "INCONSISTENT"
    assert result["admission"]["vacuous"] is True

    units[1] = unit("b", cut, len(source), "meta")
    rs = {"id": "s", "unit": "b", "version": 1, "status": "authored",
          "signature": "alice", "readings": [reading(env, "notp", ["not", p])]}
    path = write_doc(tmp_path, source, units, environment_json=env_json,
                     graph=graph, reading_sets=[rs])
    result = check_document(path)
    assert result["premises"]["status"] == "INCONSISTENT"
    assert result["admission"]["vacuous"] is True


def test_fixed_and_authored_premises_enter_every_readings_query(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    source = b"Fixed.\n"
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": p})],
                     environment_json=env_json)
    assert query(path, tmp_path, p)["verdict"] == "ALL"
    rs = {"id": "s", "unit": "a", "version": 1, "status": "authored", "signature": "alice",
          "readings": [reading(env, "p", p)]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")], reading_sets=[rs],
                     environment_json=env_json)
    assert query(path, tmp_path, p)["verdict"] == "ALL"


def test_false_reading_is_inconsistent_and_vacuous(tmp_path):
    env = Environment(environment())
    source = b"False.\n"
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": [reading(env, "false", ["bottom"])]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")], reading_sets=[rs])
    assert check_document(path)["premises"]["status"] == "INCONSISTENT"
    result = query(path, tmp_path, ["top"])
    assert result["verdict"] == "ALL" and result["vacuous"] is True
    assert result["premises"]["status"] == "INCONSISTENT"


def test_only_latest_version_contributes_one_choice_per_unit(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    source = b"Claim.\n"
    older = {"id": "s", "unit": "a", "version": 1, "status": "open",
             "readings": [reading(env, "p", p)]}
    current = {"id": "s", "unit": "a", "version": 2, "status": "open",
               "readings": [reading(env, "p", p), reading(env, "notp", ["not", p])]}
    separate_readings(env, current)
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[older, current], environment_json=env_json)
    result = query(path, tmp_path, p)
    assert result["verdict"] == "SOME"
    assert result["proof"]["choice"] == ["readings:s@2:0"]
    assert result["countermodel"]["choice"] == ["readings:s@2:1"]
    stale_graph = {"root": "claim", "nodes": [{"name": "claim", "ast": p,
                                                 "label": "readings:s@1:0"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[older, current], environment_json=env_json,
                     graph=stale_graph)
    with pytest.raises(VEError, match="stale or unknown reading set version"):
        check_document(path)
    other = {**current, "id": "other"}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[older, other], environment_json=env_json)
    with pytest.raises(VEError, match="one reading set per source unit"):
        load_document(path)


def test_narrowing_keeps_original_choice_indices(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    p = ["unary", "senior", ["const", "alice"]]
    source = b"Claim.\n"
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": [reading(env, "one", ["top"]), reading(env, "two", p),
                       reading(env, "three", ["not", p])]}
    separate_readings(env, rs)
    n = {"id": "n", "set": "s", "version": 1, "keeps": ["two", "three"],
         "by": "reviewer", "reason_spans": ["a"]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     reading_sets=[rs], narrowings=[n], environment_json=env_json)
    result = query(path, tmp_path, p, "n")
    assert result["verdict"] == "SOME"
    assert result["proof"]["choice"] == ["readings:s@1:1"]
    assert result["countermodel"]["choice"] == ["readings:s@1:2"]


def test_report_identity_binds_candidate_kind_and_narrowing(tmp_path):
    env_json = envelope(VOCAB)
    env = Environment(env_json)
    source = b"Claim.\nIndependent.\n"
    cut = len(b"Claim.\n")
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"], "unit": "b"}]}
    units = [unit("a", 0, cut, content={"ast": ["top"]}),
             unit("b", cut, len(source), content={"ast": ["top"]})]
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": [reading(env, "r", ["top"]), reading(env, "other", ["bottom"])]}
    separate_readings(env, rs)
    path = write_doc(tmp_path, source, units, graph=graph, reading_sets=[rs],
                     environment_json=env_json)
    first = check_document(path)["admission"]
    rs["readings"][0]["kind"] = ["attributed", "alice", "says", "asserted"]
    path = write_doc(tmp_path, source, units, graph=graph, reading_sets=[rs],
                     environment_json=env_json)
    second = check_document(path)["admission"]
    assert first["report_id"] != second["report_id"]
    assert first["core_report_id"] != second["core_report_id"]
    n = {"id": "n", "set": "s", "version": 1, "keeps": ["r"],
         "by": "reviewer", "reason_spans": ["a"]}
    path = write_doc(tmp_path, source, units, graph=graph, reading_sets=[rs], narrowings=[n],
                     environment_json=env_json)
    narrowed = check_document(path)["admission"]
    assert narrowed["report_id"] != second["report_id"]
    n["keeps"] = ["other"]
    path = write_doc(tmp_path, source, units, graph=graph, reading_sets=[rs], narrowings=[n],
                     environment_json=env_json)
    changed = check_document(path)["admission"]
    assert changed["report_id"] != narrowed["report_id"]
    assert changed["core_report_id"] == narrowed["core_report_id"]


def test_report_identity_ignores_weights_and_json_layout(tmp_path):
    source = b"Claim.\n"
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"], "unit": "a"}]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), content={"ast": ["top"]})],
                     graph=graph)
    before = check_document(path)
    weighted = {**load_document(path)["meta"], "weights": []}
    path.write_bytes(b"---\n" + json.dumps(weighted, indent=2).encode() + b"\n---\n" + source)
    after = check_document(path)
    assert before["document_id"] == after["document_id"]
    assert before["admission"]["report_id"] == after["admission"]["report_id"]
    assert before["admission"]["core_report_id"] == after["admission"]["core_report_id"]


def test_render_keeps_nested_kind_and_candidate_attribution(tmp_path):
    env = Environment(environment())
    source = b"Maybe Alice.\n"
    nested = ["attributed", "alice", "says", ["hedged", "likely", "asserted"]]
    rs = {"id": "s", "unit": "a", "version": 1, "status": "open",
          "readings": [reading(env, "r", ["top"], nested)]}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), nested,
                                             content={"ast": ["top"]})], reading_sets=[rs])
    rendered = render_document(path)
    assert rendered.count("attributed to alice as something alice says") == 2
    assert "qualified as likely" in rendered
    assert "[" not in rendered and "]" not in rendered
    causal = ["causal", "because", ["hedged", "could", "asserted"], "asserted"]
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), causal,
                                             content={"ast": ["top"]})])
    rendered = render_document(path)
    assert "a causal statement connecting a direct assertion qualified as could" in rendered
    assert "to a direct assertion with the relation because" in rendered
    assert rendered.count("This holds in all cases.") == 1


def test_render_places_only_current_readings_beside_their_sentence(tmp_path):
    source = b"First. Second."
    env = Environment(environment())
    old = {"id": "first", "unit": "a", "version": 1, "status": "open",
           "readings": [reading(env, "old", ["bottom"])]}
    current = {"id": "first", "unit": "a", "version": 2, "status": "open",
               "readings": [reading(env, "new", ["top"])]}
    second = {"id": "second", "unit": "b", "version": 1, "status": "open",
              "readings": [reading(env, "other", ["bottom"])]}
    path = write_doc(tmp_path, source,
                     [unit("a", 0, 7, "meta"), unit("b", 7, len(source), "meta")],
                     reading_sets=[old, current, second])
    rendered = render_document(path)
    assert rendered.index("First.") < rendered.index("This holds in all cases.") < rendered.index("Second.")
    assert rendered.index("Second.") < rendered.index("This is impossible.")
    assert rendered.count("This is impossible.") == 1


def test_document_rejects_unchecked_citation_manifests(tmp_path):
    source = b"Citation.\n"
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"],
                                           "label": "cite:library/truth"}]}
    lemma = {"name": "library/truth", "conclusion": ["top"], "leaves": []}
    path = write_doc(tmp_path, source, [unit("a", 0, len(source), "meta")],
                     graph=graph, lemmas=[lemma])
    with pytest.raises(VEError, match="document citations require a checked bundle binding"):
        check_document(path)


def test_definition_kind_uses_pinned_environment_and_graph_gap_is_explicit(tmp_path):
    source = b"Lead means senior finance boss.\n"
    raw_env = definitions_envelope()
    env = Environment(raw_env)
    from ve.definitions import compile_definitions, premise
    from ve.ast import formula_to_data
    lead = next(d for d in compile_definitions(env, env.definition_entries,
                                                version=env.environment_id) if d.name == "lead")
    unit_data = unit("definition", 0, len(source), "definition",
                     content={"ast": formula_to_data(env, premise(lead))})
    path = write_doc(tmp_path, source, [unit_data], environment_json=raw_env)
    checked = check_document(path)
    assert checked["premises"]["status"] == "model"
    assert checked["coverage"]["bytes_by_kind"]["definition"] == len(source)
    graph = {"root": "claim", "nodes": [{"name": "claim", "ast": ["top"]}]}
    path = write_doc(tmp_path, source, [unit_data], environment_json=raw_env, graph=graph)
    with pytest.raises(VEError, match="admission of documents with definitions is deferred"):
        check_document(path)
