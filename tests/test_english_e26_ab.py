"""English E2.6: the corpus A/B of Lean's English authority, from the saved comparisons alone (no live checkout and no
git): every verdict row has a rule and a disposition, no availability row remains, and the wording and order rows
are split into those that keep the base's names and locations and those listed for the DRI."""
import copy
import gzip
import json
from pathlib import Path

import pytest

from conformance import english_lean_e2_ab as A

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def saved():
    return {name: A.read_json(A.HEAD / f"ab-{name}.json.gz")
            for name in ("base-head-other", "base-head-conformance", "main-head-other", "main-head-conformance")}


def records(saved, rule):
    return [r for r in saved["base-head-conformance"]["differences"] + saved["base-head-other"]["differences"]
            if A.rule(r) == rule]


def test_the_summary_and_dispositions_are_regenerated_from_the_saved_comparisons():
    result = A.report()
    assert json.loads((A.HEAD / "ab-summary.json").read_text()) == json.loads(json.dumps(result))
    assert (A.HEAD / "ab-dispositions.md").read_text() == A.markdown(result)


def test_no_unexplained_verdict_and_no_availability_row(saved):
    s = A.report()["summary"]
    assert s["records_per_side"] == 94498
    assert s["base_head"] == {"order": 192, "same": 93279, "verdict": 430, "wording": 597}
    assert s["unexplained"] == 0 and s["availability"] == 0
    assert set(s["verdict_rules"]) <= set(A.RULES)
    assert s["verdict_rules"] == {"V-english-source-limit-span": 230, "V-pilot-readings-slot": 4,
                                  "V-quantity-certificate-exhausted": 4, "V-quantity-model-path": 2,
                                  "V-rights-readings-head": 190}
    assert s["residue"] == {"V-quantity-model-path": 2}
    assert s["wording_order_rows"] == s["text_rows_kept_total"] + s["text_rows_for_dri_total"] == 789
    # E2.6's own rows: the English source limit and wording rows that keep everything, and four pilots main could
    # not check; nothing listed for the DRI changed between main and the head.
    assert s["e26"] == {"rules": {"V-english-source-limit-span": 230, "W-kept": 230}, "wording_not_kept": 0,
                        "availability_gained": 4, "availability_lost": 0, "dri_rows_changed_by_e26": 0}


def test_rights_under_the_readings_head_is_a_python_bug(saved):
    """composition-s1.md 1.1: `readings@1` sits on the `rights` route and its head hands every case but its reading
    sets to the lower chain; so a rights document under it is checked, never `UnsupportedProfile`."""
    spec = " ".join((ROOT / "docs/spec/composition-s1.md").read_text().split())
    assert "sits on the routes `norms`, `normDefaults`, `soft` and `rights`, and its head is `readings`" in spec
    assert "chain of a list rights if the list has rights@0" in spec
    rows = records(saved, "V-rights-readings-head")
    assert len(rows) == 190 and {r["op"] for r in rows} == {"document_check"}
    for r in rows:
        assert r["case"].endswith("/readings@1")
        assert r["base"]["raised"] == {"code": "UnsupportedProfile",
                                       "message": "UnsupportedProfile: Unsupported profile readings@1"}
        assert "returned" in r["head"]


def test_an_exhausted_certificate_replay_was_never_false(saved):
    """The base said `false` for the four certificate calls; their replay runs out of the 10,000 steps the base
    gave it and, with more, replays as valid: `false` was an exhausted budget, Lean's `ResourceLimit` is right."""
    from ve import units
    from ve.entailment import check_entailment_certificate
    from ve.environment import Environment
    rows = records(saved, "V-quantity-certificate-exhausted")
    assert len(rows) == 4 and {r["authority"] for r in rows} == {"python", "lean"}
    with gzip.open(ROOT / "docs/lean-first/quantity-corpus.json.gz", "rt") as f:
        calls = json.load(f)
    calls = {c["id"]: c for c in (calls if isinstance(calls, list) else calls["calls"])}
    for case in {r["case"] for r in rows}:
        call = calls[case]
        target, _, cores = units._core_problem(Environment(call["environment"]), call["premises"], call["conclusion"])
        short = check_entailment_certificate(target, cores[:-1], cores[-1], call["certificate"]["core"],
                                             max_steps=10_000)
        long = check_entailment_certificate(target, cores[:-1], cores[-1], call["certificate"]["core"],
                                            max_steps=1_000_000)
        assert (short.status, short.valid) == ("ResourceLimit", False)
        assert (long.status, long.valid) == ("Valid", True)
    for r in rows:
        assert r["base"] == {"returned": False}
        assert r["head"]["raised"]["message"].startswith("ResourceLimit: certificate replay exceeds 10,000 steps")


def test_the_residue_is_the_listed_rows(saved):
    rows = records(saved, "V-quantity-model-path")
    assert len(rows) == 2
    for r in rows:
        assert r["base"]["raised"]["path"] == "/domains/s" and "path" not in r["head"]["raised"]


def test_the_english_rows_keep_code_limit_and_names(saved):
    rows = records(saved, "V-english-source-limit-span")
    assert len(rows) == 230
    for r in rows:
        assert r["base"]["output"] == {"code": "ResourceLimit", "message": "English source exceeds 65536 bytes"}
        out = r["head"]["output"]
        assert (out["code"], out["message"]) == ("ResourceLimit", "The text is longer than 65,536 bytes.")
        assert out["span"]["start"] == 0 and out["span"]["end"] > 65536
    own = saved["main-head-other"]["differences"] + saved["main-head-conformance"]["differences"]
    assert {A.rule(r) for r in own if r["class"] == "verdict"} == {"V-english-source-limit-span"}
    assert all(A.kept(r)["kept"] for r in own if r["class"] == "wording")


def test_the_pilot_rows_differ_only_in_main_side_texts(saved):
    """Each differs from the base only in reading texts (and the soft hash). Main gives the head's very report for
    the UDHR translation; the three constitution readings documents main could not check at all (its V3 refusal
    of an apostrophe wording, which E2.6 removes), and E2.6 changes none of the reading texts' code."""
    rows = records(saved, "V-pilot-readings-slot")
    own = {r["case"]: r for r in saved["main-head-other"]["differences"] if r["corpus"] == "pilots"}
    assert len(rows) == 4
    for r in rows:
        assert A._only_readings_texts_and_hash(r["base"], r["head"])
        if r["case"] in own:
            assert own[r["case"]]["class"] == "availability" and A._unavailable(own[r["case"]]["base"])
            assert "invalidGrammar lexicon: V3 predicate system_prompt_" in json.dumps(own[r["case"]]["base"])
            assert own[r["case"]]["head"] == r["head"]
    assert sum(r["case"] not in own for r in rows) == 1


def _kept_record(saved, needle):
    return copy.deepcopy(next(r for r in saved["base-head-other"]["differences"] + saved["base-head-conformance"]
                              ["differences"] if r["class"] in ("wording", "order") and A.kept(r)["kept"]
                              and needle(r)))


def test_the_names_and_locations_check_can_fail(saved):
    """Each condition of the lf-12 rule can fail: a quoted name dropped, a path dropped, a span narrowed, an
    unquoted message reworded."""
    named = _kept_record(saved, lambda r: A.quoted(" ".join(A.texts(r["base"]))))
    name = A.quoted(" ".join(A.texts(named["base"])))[0]
    head = json.loads(json.dumps(named["head"]).replace(name, "x"))
    assert A.kept({**named, "head": head})["names_lost"] == [name]
    spanned = _kept_record(saved, lambda r: any(k[-1] == "span" for k in A.locations(r["base"])))
    where, span = next((k, v) for k, v in A.locations(spanned["base"]).items() if k[-1] == "span")
    narrowed = copy.deepcopy(spanned["head"])
    node = narrowed
    for part in where[:-1]:
        node = node[part]
    node["span"] = {**span, "start": span["start"] + 1, "end": span["start"] + 1}
    assert A.kept({**spanned, "head": narrowed})["locations_lost"]
    pathed = {"class": "wording", "corpus": "quantity", "op": "countermodel", "authority": "lean", "case": "x",
              "base": {"raised": {"code": "ResourceLimit", "message": "domain exceeds entity limit", "path": "/d/s"}},
              "head": {"raised": {"code": "ResourceLimit", "message": "ResourceLimit: domain exceeds entity limit"}}}
    assert A.kept(pathed)["locations_lost"] == ["raised/path"]
    plain = {**pathed, "head": {"raised": {"code": "ResourceLimit", "message": "ResourceLimit: too big",
                                           "path": "/d/s"}}}
    assert A.kept(plain)["messages_lost"] == ["domain exceeds entity limit"]


def test_an_unknown_verdict_or_availability_row_fails_the_report(saved, monkeypatch):
    original = A.read_json

    def planted(path):
        data = original(path)
        if path.name == "ab-base-head-other.json.gz":
            data = copy.deepcopy(data)
            data["differences"].append({"class": "verdict", "corpus": "readings", "op": "readings_validate",
                                        "authority": "default", "case": "x", "base": {"returned": 1},
                                        "head": {"returned": 2}})
            data["totals"]["availability"] = 1
        return data
    monkeypatch.setattr(A, "read_json", planted)
    s = A.report()["summary"]
    assert s["unexplained"] == 1 and s["availability"] == 1
    assert A.main(["report"]) == 1
