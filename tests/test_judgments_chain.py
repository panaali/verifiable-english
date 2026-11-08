"""PC-1: `judgments@0` beside the soft chain in Lean's document mode, and row 16, the clash validation
(docs/spec/profile-composition.md 1.7, 3.1 and 5.1; the G3 amendment, synthesis round 2 edit 2).

Every case is built from `tests/data/composition/pc1/soft-judgments.json` (constitution u0052.s01 and u0036.s05 as
soft default rules) and sent to the service; Lean decides every value. A request's twin is the same document with
`judgments@0` taken out of its profiles; the clash cases' twins keep their stated values (their exchange is not one
to one), except F1.3o's `j₁`, whose twin is `t`. The same cases are `#guard`s in lean/VE/Judgments/ChainExamples.lean,
which also check `swapInjective` on each request and twin."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import pytest

from conformance.p0 import LANGUAGE, SPEC_REVISION
from ve.backends.lean_service import LeanService
from ve.wire import digest

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "tests/data/composition/pc1/soft-judgments.json").read_text())
LAYER = ["documents@1", "judgments@0", "norms@0", "relational-fol@0", "soft-norms@0"]
PLAIN = [p for p in LAYER if p != "judgments@0"]
CLASH = ("distinguishing model ids and references do not map one to one between the environments with and without "
         "judgments@0")
EXCEPTION = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}


@pytest.fixture(scope="module")
def service():
    with LeanService() as instance:
        yield instance


def record(name):
    return {"name": name, "arguments": ["situation"], "decided_by": "unstated", "necessary": [],
            "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "document", "version": 1}


def front(uid, profiles=LAYER, listed=None, rule=None, sets=None):
    """The front matter of one unit's document: its rule, its bound terms listed (`listed`) and declared."""
    unit = DATA["units"][uid]
    listed = unit["terms"] if listed is None else listed
    return {"format": "ve-document@1", "environment": {
                "language": LANGUAGE, "profiles": list(profiles), "spec_revision": SPEC_REVISION,
                "vocabulary": deepcopy(DATA["vocabulary"])},
            "units": [{"id": uid, "span": [0, len(unit["body"])], "kind": "norm", "meaning": {"open": listed},
                       "support": "assumption",
                       "content": {"norm": {**(rule or unit["rule"]), "exception": EXCEPTION}}}],
            "open_terms": [record(t) for t in listed], **({"reading_sets": sets} if sets else {})}


def text(uid, fm):
    return "---\n" + json.dumps(fm) + "\n---\n" + DATA["units"][uid]["body"]


def twin(fm):
    out = deepcopy(fm)
    out["environment"]["profiles"].remove("judgments@0")
    return out


def answer(service, uid, fm):
    return service.run("document", [{"id": "c", "document": text(uid, fm)}])[0]


def verdict(row):
    """The answer without the fields the layer may change and the environment-dependent identities (spec 2e)."""
    out = {k: v for k, v in row.items()
           if k not in ("judgments", "judgment_lines", "undeclared_evaluative", "document_id", "source_id",
                         "coverage")}
    out["units"] = [{k: v for k, v in u.items() if k not in ("status", "meaning_id")} for u in row["units"]]
    return out


def test_f1_1_a_soft_default_rule_with_a_bound_judgment_is_admitted_and_open(service):
    """F1.1 and F1.6: admitted, the unit OPEN, `good_judgment: [u0052.s01]`; the twin has the same verdict fields and
    other identities."""
    fm = front("u0052.s01")
    row, plain = answer(service, "u0052.s01", fm), answer(service, "u0052.s01", twin(fm))
    assert row["status"] == plain["status"] == "ok", (row, plain)
    assert [u["status"] for u in row["units"]] == ["OPEN"]
    assert row["judgments"] == {"used": [{"term": "good_judgment", "units": ["u0052.s01"]}], "unused": []}
    assert "judgments" not in plain
    # judgment-terms 8.4 beside the soft route: the base predicates that match the catalogue and are not bound.
    assert row["undeclared_evaluative"] == ["genuinely_ambiguous", "reasonable"]
    assert "undeclared_evaluative" not in plain
    assert verdict(row) == verdict(plain) and row["document_id"] != plain["document_id"]
    # Identities over the list as written (jt-2c item 1(b)), the soft route's E″ included.
    assert row["units"][0]["meaning_id"] != plain["units"][0]["meaning_id"]


def test_a_unit_may_list_its_rule_s_soft_decision_predicate_with_the_layer(service):
    """An `open` meaning cites the soft route's decision predicates as without the layer (found by the trust mutants:
    `judgedViews` read the records' names alone, so the layer refused what its twin admits)."""
    fm = front("u0052.s01", listed=["good_judgment"])
    fm["units"][0]["meaning"]["open"].append("soft__excepted__good_judgment")
    rows = [answer(service, "u0052.s01", side) for side in (fm, twin(fm))]
    assert [r["status"] for r in rows] == ["ok", "ok"], rows
    assert [[u["status"] for u in r["units"]] for r in rows] == [["OPEN"], ["OPEN"]]


@pytest.mark.parametrize("where", ["guard", "unless"])
def test_f1_2_the_reader_scans_the_guard_and_the_author_carve_outs(service, where):
    """F1.2 and F1.2b: the judgment in the guard, or only in the `unless` clause, is found (`softContent_formulas`)."""
    rule = deepcopy(DATA["units"]["u0036.s05"]["rule"])
    if where == "unless":
        rule["unless"], rule["guard"] = [rule["guard"]], ["top"]
    row = answer(service, "u0036.s05", front("u0036.s05", rule=rule))
    assert row["status"] == "ok", row
    assert [u["status"] for u in row["units"]] == ["OPEN"]
    assert row["judgments"]["used"] == [{"term": "genuinely_ambiguous", "units": ["u0036.s05"]}]


@pytest.mark.parametrize("case, expected", [
    ("F1.3", "JudgmentListedUnused: u0036.s05 reasonable"),
    ("F1.3d", "UnsupportedProfile: judgments@0 requires documents@1"),
    ("F1.5", "CheckerUnavailable: judgments@0 with alternatives@0 needs its composed Lean route"),
    ("rights", "CheckerUnavailable: judgments@0 with rights@0 needs its composed Lean route"),
    ("risk", "CheckerUnavailable: judgments@0 with risk@0 needs its composed Lean route")])
def test_the_layer_s_own_refusals_and_the_profiles_it_stays_apart_from(service, case, expected):
    """F1.3 (a listed judgment the unit does not use, today's text and order), F1.3d (the gate) and F1.5 (kept), each
    a refusal with the layer whose twin is admitted; `rights@0` stays apart until pc-1g's reader."""
    uid = "u0036.s05" if case == "F1.3" else "u0052.s01"
    profiles = {"F1.3d": [p for p in LAYER if p != "documents@1"], "F1.5": sorted(LAYER + ["alternatives@0"]),
                "rights": sorted(LAYER + ["rights@0"]), "risk": sorted(LAYER + ["risk@0"])}.get(case, LAYER)
    fm = front(uid, profiles, listed=["genuinely_ambiguous", "reasonable"] if case == "F1.3" else None)
    assert answer(service, uid, fm).get("error") == expected
    if case in ("F1.3", "F1.3d"):
        assert answer(service, uid, twin(fm))["status"] == "ok"


APART = "CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route"


@pytest.mark.parametrize("term", ["good_judgment", "evaluating_inputs"])
@pytest.mark.parametrize("listed", [True, False], ids=["listed", "not listed"])
@pytest.mark.parametrize("where", ["sufficient", "necessary"])
def test_a_rule_with_exception_conditions_keeps_main_s_refusal_of_the_pairing(service, where, listed, term):
    """pc-1 review F1 (PROBE F1): the soft route makes `exception.sufficient` and `exception.necessary` rules of its
    theory, which `softContent` does not read, so a document with one keeps main's refusal of `judgments@0` beside
    `soft-norms@0` (`exceptionConditioned`), whether the condition is a judgment and whether the term is listed. It
    was CHECKED with the judgment reported unused, or refused `JudgmentListedUnused`. The twin is answered."""
    fm = front("u0052.s01", listed=["good_judgment"] if listed else [])
    norm = fm["units"][0]["content"]["norm"]
    norm["guard"] = ["unary", "evaluating_inputs", ["var", 0]]
    norm["exception"] = {**EXCEPTION, where: [["unary", term, ["var", 0]]]}
    if not listed:
        fm["units"][0]["meaning"] = "specified"
    assert answer(service, "u0052.s01", fm).get("error") == APART
    plain = answer(service, "u0052.s01", twin(fm))
    assert plain["status"] == "ok" and [u["status"] for u in plain["units"]] == ["OPEN" if listed else "CHECKED"]


def model_id(service, profiles, model):
    env = {"language": LANGUAGE, "profiles": profiles, "spec_revision": SPEC_REVISION, "vocabulary": DATA["vocabulary"]}
    eid = service.run("environment", [{"id": "e", "environment": env}])[0]["environment_id"]
    return digest(f"ve-model-v0.2:{','.join(profiles)}\n", {"environment_id": eid, "model": DATA["model"]})


def reading(rid, refs):
    return {"id": rid, "kind": "asserted", "meaning_id": "pending", "content": None,
            "admission": {"who": "reviewer", "why": "a reading", "distinguishing_models": refs}}


def reading_set(readings, models):
    return [{"id": "s", "unit": "u0052.s01", "version": 1, "status": "open", "readings": readings, "models": models}]


def clashes(service, fm, twin_fm):
    """Row 16 first with the layer and in the twin (`swapInjective` false on each side: ChainExamples' guards)."""
    for side in (fm, twin_fm):
        assert answer(service, "u0052.s01", side).get("error") == CLASH, side["environment"]["profiles"]


@pytest.mark.parametrize("profiles", [LAYER, [p for p in LAYER if p != "documents@1"]], ids=["F1.3l", "F1.3m"])
def test_f1_3l_a_dangling_reference_reading_a_model_s_twin_key_is_refused_first_on_both_sides(service, profiles):
    """F1.3l, and F1.3m without `documents@1`: row 16 comes before the gate's `judgments@0 requires documents@1`."""
    v2 = model_id(service, [p for p in profiles if p != "judgments@0"], DATA["model"])
    sets = reading_set([reading("r0", {"r1": "d", "r2": "d"}), reading("r1", {"r0": "d", "r2": "d"}),
                        reading("r2", {"r0": v2, "r1": "d"})], {"d": DATA["model"]})
    fm = front("u0052.s01", profiles, sets=sets)
    clashes(service, fm, twin(fm))


def test_f1_3o_the_check_reads_the_request_and_its_twin(service):
    """F1.3o: `j₁` states A under `a1` (its identity with the layer) and B under `w`; `j₂` states A under `a2`; `t`,
    the plain request with A under `a2`, is the twin of both. All three answer row 16 first."""
    a1, a2 = model_id(service, LAYER, DATA["model"]), model_id(service, PLAIN, DATA["model"])

    def case(profiles, key):
        sets = reading_set([reading("r0", {"r1": key}), reading("r1", {"r0": "w"})],
                           {key: DATA["model"], "w": DATA["model"]})
        return front("u0052.s01", profiles, sets=sets)
    t = case(PLAIN, a2)
    clashes(service, case(LAYER, a1), t)
    clashes(service, case(LAYER, a2), t)


def documents():
    """Every document-mode request of tests/data (the relay gate's recorded `document` cases and the document
    files), as `(name, case)`."""
    out = []
    for n, line in enumerate((ROOT / "tests/data/relay-gate-cases.jsonl").read_text().splitlines()):
        if not line.startswith('["service","document",'):
            continue
        stack = [json.loads(line)]
        while stack:
            x = stack.pop()
            if isinstance(x, dict) and isinstance(x.get("document"), str) and x["document"].startswith("---\n"):
                out.append((f"relay-gate:{n}:{len(out)}", x))
            stack.extend(x.values() if isinstance(x, dict) else x if isinstance(x, list) else [])
    for path in sorted(p for p in (ROOT / "tests/data").rglob("*.ve.*") if p.suffix in (".md", ".txt")):
        out.append((str(path.relative_to(ROOT)), {"id": "c", "document": path.read_text()}))
    return out


def plain_documents():
    return [(n, c) for n, c in documents() if '"judgments@0"' not in c["document"]]


def test_f1_3n_no_plain_request_of_tests_data_meets_the_clash_check(service):
    """F1.3n: the check refuses no request of tests/data without `judgments@0` (their answers before and after PC-1
    are compared byte for byte in docs/profile-composition/pc-1/f13n.json, by f13n.py)."""
    cases = plain_documents()
    assert len(cases) >= 13
    rows = service.run("document", [c for _, c in cases])
    assert [n for (n, _), r in zip(cases, rows) if r.get("error") == CLASH] == []


def test_a_large_reading_set_is_checked_once_within_the_limits(service):
    """64 readings (the most a set holds), each with 63 distinct dangling references: the check's values and pairs
    are computed once per request (`swapInjective_eq_fast`), and the case is answered by the later checks."""
    ids = [f"r{i}" for i in range(64)]
    readings = [reading(r, {o: f"m-{r}-{o}" for o in ids if o != r}) for r in ids]
    fm = front("u0052.s01", sets=reading_set(readings, {"d": DATA["model"]}))
    row = answer(service, "u0052.s01", fm)
    assert row["status"] == "error" and row["error"] != CLASH, row


@pytest.mark.parametrize("extra, expected", [(61, CLASH), (62, "reading sets hold 1 to 64 readings")],
                         ids=["64 readings", "65 readings"])
def test_row_16_reads_reading_sets_of_at_most_64_readings(service, extra, expected):
    """pc-1 review F2: F1.3l's clash with readings added. At 64 readings row 16 refuses it; at 65 the chain's own
    size check does, in its order, as at the merge base (`sizedSets`), on both sides."""
    v2 = model_id(service, PLAIN, DATA["model"])
    sets = reading_set([reading("r0", {"r1": "d", "r2": "d"}), reading("r1", {"r0": "d", "r2": "d"}),
                        reading("r2", {"r0": v2, "r1": "d"})] + [reading(f"x{i}", {}) for i in range(extra)],
                       {"d": DATA["model"]})
    fm = front("u0052.s01", sets=sets)
    assert [answer(service, "u0052.s01", side).get("error") for side in (fm, twin(fm))] == [expected, expected]


def test_a_plain_request_over_the_readings_limit_is_refused_within_its_budget(service, monkeypatch):
    """pc-1 review F2 (PROBE F2): 256 readings with 255 distinct references each (1.46 MB). Row 16 compared every
    stated value with every other before the chain's size check (75 to 99 s of CPU); it now reads no set over 64
    readings and hashes each value once. The service's own budget for the request is lowered to 5 s of CPU, so a
    request that needs more raises `CheckerUnavailable` (lean_service.DEADLINES)."""
    from ve.backends import lean_service
    monkeypatch.setitem(lean_service.DEADLINES, "document", (5.0, 0.0))
    ids = [f"r{i}" for i in range(256)]
    fm = front("u0052.s01", PLAIN, sets=reading_set([reading(r, {o: f"m-{r}-{o}" for o in ids if o != r})
                                                     for r in ids], {}))
    assert answer(service, "u0052.s01", fm) == {"id": "c", "status": "error",
                                                 "error": "reading sets hold 1 to 64 readings"}
