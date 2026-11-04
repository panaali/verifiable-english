"""cmp-s4c: the discourse route's entry on the composed path (docs/spec/discourse.md 14.5, 14.6 and 14.8) through the
Lean service: norm content answered on a list with `norms@0` and `ve.discourse@1`, the named abstentions still
refused by name, the relay's typing and binding of a composed answer (`ve/discourse.py`), the three-way agreement
of 14.6, and the saved byte-identity comparison (`docs/composition/cmp-s4c/byte-identity.json`, recorded on main's
service by `record_byte_identity.py`: S4-2's share, S4-3, S4-25, S4-28)."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests import lean_routes
from ve import discourse
from ve.backends import service_schema
from ve.document import load_document
from ve.errors import CheckerUnavailable
from ve.profiles import ROWS

EVIDENCE = Path(__file__).resolve().parents[1] / "docs/composition/cmp-s4c/byte-identity.json"
SRC1, SRC2 = "Web API is deployed.\n", "Every deployed service must be reviewed.\n"
B1, B2 = len(SRC1.encode()), len((SRC1 + SRC2).encode())
CHAIN = ("norms@0", "relational-fol@0", "ve.discourse@1")


def vocabulary(regulated=True):
    """14.8's α vocabulary (`ComposeExamples.lean` `vocabulary`); `regulated` adds `review_required`."""
    predicates = {"deployed": {"arguments": ["service"], "description": "Deployed"},
                  "api": {"arguments": ["service"], "description": "API"},
                  "owns": {"arguments": ["person", "service"], "description": "Owner"}}
    if regulated:
        predicates["review_required"] = {"arguments": ["service"], "description": "must be reviewed", "regulated": {
            "role": "obligation", "default": "allow", "act": "{0} be reviewed"}}
    return {"sorts": {"service": {"description": "Service"}, "person": {"description": "Person"}},
            "predicates": predicates, "constants": {"web_api": {"sort": "service", "description": "Web API"},
                                                    "alice": {"sort": "person", "description": "Alice"}}}


def norm(name="rule-u2", guard=("unary", "deployed", ["var", 0])):
    return {"norm": {"name": name, "predicate": "review_required", "sign": True, "guard": list(guard),
                     "unless": [], "over": []}}


U1 = {"id": "u1", "span": [0, B1], "kind": "asserted", "meaning": "specified", "support": "assumption",
      "content": {"ast": ["unary", "deployed", ["const", "web_api"]]}}
U2 = {"id": "u2", "span": [B1, B2], "kind": "norm", "meaning": "specified", "support": "none", "content": norm()}
GRAPH = {"graph": {"root": "n", "nodes": [{"name": "n", "ast": ["top"], "label": "open:t"}]}, "open_terms": [
    {"name": "t", "arguments": [], "decided_by": "reviewer", "necessary": [], "sufficient": [], "factors": [],
     "precedents": [], "jurisdiction": "policy", "version": 1}]}


def text(profiles=CHAIN, fmt="ve-document@2", units=(U1, U2), block=None, rest=GRAPH, regulated=True,
         body=SRC1 + SRC2, environment=None):
    """A document text over α (`ComposeExamples.lean` `doc`): its front matter, then the body."""
    front = {"format": fmt, "environment": environment or {
        "language": "ve.core@0.2", "spec_revision": "ve-v0.2-expand2-2026-09-25",
        "vocabulary": vocabulary(regulated), "profiles": list(profiles)}, "units": list(units)}
    if fmt == "ve-document@2":
        front["discourse"] = block or {"version": "ve.discourse@1", "anchors": []}
    return "---\n" + json.dumps({**front, **rest}) + "\n---\n" + body


def case(document, kind="admission"):
    return {"id": "s4c", "kind": kind, "document": document}


def answer(document, kind="admission"):
    [row] = lean_routes.rows("discourse", [case(document, kind)])
    return row


def error(document, kind="admission"):
    row = answer(document, kind)
    assert row["status"] == "error", row
    return row["error"]


def compact(row):
    return json.dumps(row, separators=(",", ":"), ensure_ascii=False)


# S4-18's soft document: two default rules whose exceptions give the coherence premise `soft:coherence:a,b`.
SOFT_PROFILES = ("norms@0", "relational-fol@0", "soft-norms@0", "ve.discourse@1")
SOFT_ENVIRONMENT = {"language": "ve.core@0.2", "spec_revision": "ve-v0.2-expand2-2026-09-25",
                    "profiles": list(SOFT_PROFILES), "vocabulary": {
                        "sorts": {"assistant": {"description": "assistant"}},
                        "predicates": {"x_required": {"arguments": ["assistant"], "description": "obligation",
                                                      "regulated": {"role": "obligation", "default": "deny",
                                                                    "act": "{0} do x", "permission": "x_permitted"}},
                                       "x_permitted": {"arguments": ["assistant"], "description": "permission",
                                                       "regulated": {"role": "permission", "default": "allow",
                                                                     "act": "{0} do x"}}},
                        "constants": {}}}
EXCEPTION = {"decided_by": "assistant", "sufficient": [], "necessary": [], "factors": []}


def soft_unit(uid, name, predicate, sign, span):
    return {"id": uid, "span": span, "kind": "norm", "meaning": "specified", "support": "none", "content": {"norm": {
        "name": name, "predicate": predicate, "sign": sign, "guard": ["top"], "unless": [], "over": [],
        "mode": "default", "exception": EXCEPTION}}}


SOFT_UNITS = (soft_unit("u0", "a", "x_required", True, [0, 8]), soft_unit("u1", "b", "x_permitted", False, [8, 16]))
RECORDED = [json.loads(line) for line in (Path(__file__).parent / "data/route-cases.jsonl").open()]
# the graph of the recorded soft-norms admission of rules `a` and `b` whose root is their coherence premise
SOFT_GRAPH = {"graph": next(c["document"]["graph"] for m, c in RECORDED if m == "soft-norms" and c["id"] == "0"
                            and c["document"]["graph"]["nodes"][0].get("label") == "soft:coherence:a,b")}
SOFT_TEXT = text(units=SOFT_UNITS, rest=SOFT_GRAPH, body="Rule a.\nRule b.\n", environment=SOFT_ENVIRONMENT)


def identity_cases():
    """The cases of the saved byte-identity comparison: every discourse case recorded from the suite
    (`tests/data/route-cases.jsonl`, S4-2's share), S4-3, S4-25 and S4-28."""
    recorded = [c for m, c in RECORDED if m == "discourse" and c.get("id") != "s4c"]  # not this module's own
    return [(f"S4-2 recorded {i}", c) for i, c in enumerate(recorded)] + [
        ("S4-3", case(text(units=(U1,), regulated=False, body=SRC1))),
        ("S4-25", case(text(profiles=("relational-fol@0", "ve.discourse@1"), units=(U1,), body=SRC1))),
        ("S4-28", case(text(profiles=("norms@0", "relational-fol@0"), fmt="ve-document@1")))]


# -- the composed path answers norm content (DELTA row; the DRI's conditions) --------------------------------------

def test_norm_content_is_answered_on_the_composed_path():
    row = answer(text())
    assert set(row) == discourse._COMPOSED and row["status"] == "ok"
    assert row["inner"]["admitted"] is True and row["inner"]["kinds"] == ["asserted", "norm"]
    assert row["inner_report_id"] == row["inner"]["report_id"] != row["report_id"]


def test_norm_content_the_chain_route_rejects_is_refused():
    # refused at 14.5 step 4 (the `@1` part's check, today's text)
    assert error(text(units=(U1, {**U2, "content": norm(guard=("unary", "owns", ["var", 0]))}))).endswith(
        "TypeMismatch: Predicate 'owns' has arity 2, not 1")


def test_large_document_ends_within_the_chain_document_limit():
    # cmp-s4's `large` fixture through the route: 200 norm units, charged against `Loader.maxDocumentBytes`
    line = "Rule.\n"
    units = [{**U2, "id": f"r{i}", "span": [6 * i, 6 * (i + 1)], "content": norm(f"rule-r{i}")} for i in range(200)]
    row = answer(text(units=units, body=line * 200))
    assert row["status"] == "ok" and len(row["inner"]["kinds"]) == 200


def test_s4_18_coherence_premises_are_the_soft_routes():
    row = answer(SOFT_TEXT)
    assert row["inner"]["conditional_on"] == ["soft:coherence:a,b"]
    # the soft route's own answer on the chain document (`chainDocument`: no discourse block, no `ve.discourse@1`)
    units = [{k: u[k] for k in ("id", "span", "kind", "content")} for u in SOFT_UNITS]
    base = {**SOFT_ENVIRONMENT, "profiles": [p for p in SOFT_PROFILES if p != "ve.discourse@1"]}
    [soft] = lean_routes.rows("soft-norms", [{"id": "", "kind": "admission", "environment": base, "document": {
        "units": units, **SOFT_GRAPH, "lemmas": [], "open_terms": [], "reading_sets": [], "narrowings": []}}])
    assert compact(row["inner"]) == compact(soft)


ABSTENTIONS = {
    "groups": ({"groups": [{"id": "g", "units": ["u1"]}]}, "NotImplemented: groups on the chain"),
    "constraints": ({"constraints": [{"id": "c"}]}, "NotImplemented: constraints on the chain"),
    "validity claims": ({"validity": [{"unit": "u1"}]}, "NotImplemented: validity claims on the chain"),
}


@pytest.mark.parametrize("name", ABSTENTIONS)
def test_named_abstentions_refuse_by_name(name):
    extra, expected = ABSTENTIONS[name]
    assert error(text(block={"version": "ve.discourse@1", "anchors": [], **extra})) == expected


def test_active_reading_sets_refuse_by_name():
    sets = {"reading_sets": [{"unit": "u1", "set": "s", "version": 1, "status": "open", "readings": []}]}
    assert error(text(rest={**GRAPH, **sets})) == "NotImplemented: reading sets on the chain"


def test_s4_14_a_provenance_mention_stays_an_unrecorded_slot():
    # OPEN 1: a norm unit whose prose has an unrecorded `It` is today's `UnrecordedSlot`, not a provenance mention
    body = SRC1 + "It must be reviewed by every deployed service.\n"
    units = (U1, {**U2, "span": [B1, len(body.encode())]})
    assert error(text(units=units, body=body)).startswith("UnrecordedSlot: u2: ")


def test_s4_21_a_document_without_a_claim_graph_stays_refused():
    assert error(text(rest={})) == "NotImplemented: a document without a claim graph"


@pytest.mark.parametrize("kind", ["discourse-validity", "discourse-resolve", "discourse-joint"])
def test_s4_27_other_kinds_on_the_chain_are_abstentions(kind):
    assert error(text(), kind) == f"NotImplemented: {kind} on the chain"


def test_s4_16_s4_17_lists_no_chain_route_reads_are_refused():
    assert error(text(profiles=("norms@0", "readings@1", "relational-fol@0", "ve.discourse@1"))) == (
        "UnsupportedProfile: ve.discourse@1 with readings@1")
    assert error(text(profiles=("norms@0", "relational-fol@0", "speech-acts@0", "ve.discourse@1"))) == (
        "UnsupportedProfile: ve.discourse@1 with speech-acts@0")


# -- 14.6's three-way agreement: the profile table Python reads, Lean's gate on the route, the wire schema -----------

BESIDE = {"norms": (), "norm-defaults": ("norm-defaults@0",), "soft": ("soft-norms@0",)}


@pytest.mark.parametrize("base", BESIDE)
def test_three_way_ve_discourse_beside_the_chain(base):
    [row] = [r for r in ROWS if r["profile"] == "ve.discourse@1"]
    refused = {p for p, _ in row["refuses"]}
    profiles = tuple(sorted(CHAIN + BESIDE[base]))
    assert not refused & set(profiles)
    lean = answer(text(profiles=profiles))
    assert lean["status"] == "ok" and "inner" in lean
    service_schema.check_row("discourse", lean, case(text(profiles=profiles)), 0)


# each outside route on a base list today's gate admits with `norms@0` (`reports@0` has none: D rows of
# tests/test_compose_dispatch.py)
OUTSIDE = {"alternatives@0": ("alternatives@0",), "risk@0": ("alternatives@0", "risk@0"),
           "speech-acts@0": ("speech-acts@0",)}


@pytest.mark.parametrize("outside", OUTSIDE)
def test_three_way_ve_discourse_refusals_agree(outside):
    [row] = [r for r in ROWS if r["profile"] == "ve.discourse@1"]
    profiles = tuple(sorted(CHAIN + OUTSIDE[outside]))
    assert error(text(profiles=profiles)) == "UnsupportedProfile: " + dict(row["refuses"])[outside]


# -- the relay: typed, then bound to the document (R8: no Python verdict) -------------------------------------------

UNAVAILABLE = "Lean admits the document on the composed path"


@pytest.fixture(scope="module")
def genuine():
    return answer(text())


def _relayed(tmp_path, monkeypatch, row):
    """The document report of the composed document with the relay's Lean answer replaced by `row`."""
    from ve.backends import relay
    path = tmp_path / "doc.md"
    path.write_text(text())
    monkeypatch.setattr(relay, "rows", lambda mode, cases: [{**row, "id": cases[0]["id"]}])
    with pytest.raises(CheckerUnavailable) as caught:
        load_document(path)
    return caught.value.message


def test_the_genuine_answer_passes_the_binding(tmp_path, monkeypatch, genuine):
    assert UNAVAILABLE in _relayed(tmp_path, monkeypatch, genuine)


@pytest.mark.parametrize("profiles", [CHAIN, tuple(sorted(CHAIN + ("norm-defaults@0",))), SOFT_PROFILES])
def test_f2_mixed_parent_passes_binding_on_each_available_chain(profiles):
    document = text(profiles=profiles, units=({"id": "parent", "span": [0, B2], "status": "MIXED",
                                               "parts": [dict(U1, status="CHECKED"), dict(U2, status="CHECKED")]},))
    row = answer(document)
    assert row["status"] == "ok" and row["inner"]["kinds"] == ["asserted", "norm"]
    assert discourse.bind_composed({"meta": json.loads(document.split("---\n")[1])}, row) is row


@pytest.mark.parametrize("profiles", [CHAIN, tuple(sorted(CHAIN + ("norm-defaults@0",))), SOFT_PROFILES])
@pytest.mark.parametrize("field,value", [("ast", ["bottom"]), ("label", "open:absent")])
@pytest.mark.parametrize("position", ["root", "assumptions"])
def test_f1_copied_claim_is_bound_to_its_complete_graph_node(profiles, field, value, position):
    document = SOFT_TEXT if profiles == SOFT_PROFILES else text(profiles=profiles)
    row = answer(document)
    assert row["status"] == "ok"
    mutant = copy.deepcopy(row)
    claim = mutant["inner"]["report"][position]
    if position == "assumptions":
        claim = claim[0]
    claim[field] = value
    service_schema.check_row("discourse", mutant, case(document), 0)
    with pytest.raises(CheckerUnavailable, match="answered another document \\(report\\)"):
        discourse.bind_composed({"meta": json.loads(document.split("---\n")[1])}, mutant)


def test_f1_default_label_is_omitted_from_both_copies():
    document = text()
    meta = json.loads(document.split("---\n")[1])
    row = answer(document)
    del meta["graph"]["nodes"][0]["label"]
    row = copy.deepcopy(row)
    del row["inner"]["report"]["root"]["label"]
    del row["inner"]["report"]["assumptions"][0]["label"]
    assert discourse.bind_composed({"meta": meta}, row) is row


def test_document_check_is_checker_unavailable_and_shows_no_verdict(tmp_path, capsys):
    # DRI 2026-11-04 item 1: Lean admits the document, the report has no unit statuses to show (14.7): exit 5
    from ve.__main__ import EXIT_CHECKER_UNAVAILABLE, main
    path = tmp_path / "doc.md"
    path.write_text(text())
    assert main(["document", "check", str(path)]) == EXIT_CHECKER_UNAVAILABLE == 5
    out = capsys.readouterr().out
    record = json.loads(out)
    assert record["status"] == "CheckerUnavailable" and UNAVAILABLE in record["error"]["message"]
    assert "admitted" not in out and not any(s in out for s in discourse._STATUSES)


def test_r2_the_composed_path_reports_its_first_fault():
    # two faults: a `groups` entry (step 1) and α's regulated predicate, which today's base vocabulary rejects first
    # (S4-25's saved answer on the same vocabulary)
    [(_, _, today)] = [e for e in json.loads(EVIDENCE.read_text()) if e[0] == "S4-25"]
    assert json.loads(today)["error"].endswith("got [arguments, description, regulated]")
    groups = {"version": "ve.discourse@1", "anchors": [], "groups": [{"id": "g", "units": ["u1"]}]}
    assert error(text(block=groups)) == "NotImplemented: groups on the chain"


def test_the_relay_returns_leans_answer_unchanged(tmp_path):
    raw = text().encode()
    row = discourse.lean_admission(raw, tmp_path)
    assert compact(row) == compact({**answer(text()), "id": row["id"]})


# each other JSON type, `1` beside `true`, a lone surrogate and a 10,000-deep list (BUILDER-CHECKLIST 1)
def _deep(n=10000):
    value = []
    for _ in range(n):
        value = [value]
    return value


def _same(a, b):
    return type(a) is type(b) and a == b


RETYPES = (7, 1, True, None, [], {}, 1.5, "\ud800", _deep())


def _mutants(row):
    """Each member dropped and retyped, and the bound arrays duplicated and reordered."""
    for key in row:
        if key != "id":
            yield f"drop {key}", {k: v for k, v in row.items() if k != key}
            for i, value in enumerate(RETYPES):
                if not _same(value, row[key]):
                    yield f"retype {key} {i}", {**row, key: value}
    for key in ("admitted", "report_id", "kinds", "report"):
        yield f"drop inner.{key}", {**row, "inner": {k: v for k, v in row["inner"].items() if k != key}}
        for i, value in enumerate(RETYPES):
            if not _same(value, row["inner"].get(key)):
                yield f"retype inner.{key} {i}", {**row, "inner": {**row["inner"], key: value}}
    yield "inner report id", {**row, "inner_report_id": "0" * 64}
    kinds = row["inner"]["kinds"]
    yield "duplicate kinds", {**row, "inner": {**row["inner"], "kinds": kinds + kinds[-1:]}}
    yield "reorder kinds", {**row, "inner": {**row["inner"], "kinds": kinds[::-1]}}
    report = row["inner"]["report"]
    yield "foreign root", {**row, "inner": {**row["inner"], "report": {**report, "root": {**report["root"], "name": "x"}}}}
    yield "foreign claim", {**row, "inner": {**row["inner"], "report": {
        **report, "assumptions": report["assumptions"] + [{"name": "x", "ast": ["top"]}]}}}
    yield "extra reference", {**row, "references": [{"mention": "m", "unit": "u1", "form": "pronoun",
                                                     "target": {"kind": "entity", "name": "web_api"},
                                                     "status": "resolved"}]}


@pytest.mark.parametrize("name", [name for name, _ in _mutants(copy.deepcopy({
    "id": "", "status": "ok", "document_id": "", "inner": {"admitted": True, "report_id": "", "kinds": ["k"],
                                          "report": {"root": {}, "assumptions": []}},
    "inner_report_id": "", "references": [], "report_id": ""}))])
def test_every_mutant_is_refused(tmp_path, monkeypatch, genuine, name):
    [mutant] = [m for n, m in _mutants(copy.deepcopy(genuine)) if n == name]
    message = _relayed(tmp_path, monkeypatch, mutant)
    assert UNAVAILABLE not in message, name
    assert "returned no answer to the case" in message or "answered another document" in message, message


# -- the saved byte-identity comparison (saved evidence, never live git) -------------------------------------------

def test_the_saved_evidence_holds_every_identity_case():
    saved = json.loads(EVIDENCE.read_text())
    assert [name for name, _, _ in saved] == [name for name, _ in identity_cases()]
    assert [c for _, c, _ in saved] == [c for _, c in identity_cases()]


@pytest.mark.parametrize("index", range(len(identity_cases())))
def test_answers_are_byte_identical_to_mains(index):
    name, saved_case, saved_answer = json.loads(EVIDENCE.read_text())[index]
    [row] = lean_routes.rows("discourse", [saved_case])
    assert compact(row) == saved_answer, name
