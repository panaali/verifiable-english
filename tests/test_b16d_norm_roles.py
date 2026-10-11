"""Batch 16d review B1 and B2: which norm units make the norm-defaults document.

The class: a norm unit's role (a rule in force, a quoted rule checked alone, or a rule outside the free document) is
read in one place per language. Lean's document mode uses `Norms.Admission.normRole` (the table W1's admission
splits a document by) and `Service.Document.freeNorms`; Python's two paths share `ve.document._free_norms`. Each
case is a document the retained Python path decides; Lean's document mode must answer it (never fall back) and the
report, or the diagnostic, must be the same. The shapes are the ones no pilot has (review B2): quoted norm units
(B1), norm content on a unit under an active reading set (B2) and a fixed norm unit attached to an open
content-bearing set (S1 1.3).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from tests import lean_routes
from ve import document as D
from ve.errors import VEError

SEED = Path(__file__).parent / "data/readings_s2/constitution-nd-readings.ve.md"
QUOTED = (["attributed", "anthropic", "says", "norm"], ["hedged", "likely", "norm"])
TOP_CLARIFY = {"norm": {"name": "clarify-always", "predicate": "clarification_required", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}


@pytest.fixture(scope="module", autouse=True)
def lean():
    if not lean_routes.SERVICE.exists():
        pytest.skip("the Lean service has not been built")


def seed_with(tmp_path, edit, name="case"):
    meta, rest = SEED.read_bytes().split(b"\n---\n", 1)
    front = json.loads(meta[4:])
    units = {u["id"]: u for u, _ in D._parts(front["units"])}
    edit(front, units)
    path = tmp_path / f"{name}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(front, ensure_ascii=False).encode() + b"\n---\n" + rest)
    return path


def same_answer(path):
    """Lean's document mode answers the document, and its report (or diagnostic) is the retained path's."""
    raw = path.read_bytes()
    try:
        expected = D._report(D._load_document(raw, path, None))
    except VEError as exc:
        # Lean decides the refusal itself (its diagnostic, not a fall back to the retained path).
        with pytest.raises(type(exc)) as caught:
            D._lean_answer(raw, True)
        assert str(caught.value) == str(exc)
        with pytest.raises(type(exc)) as caught:
            D.check_document(path)
        assert str(caught.value) == str(exc)
        return None
    assert D._lean_answer(raw, True) is not None, "Lean's document mode must decide this document"
    assert D.check_document(path) == expected
    return expected


def kind(uid, value):
    def edit(front, units):
        units[uid]["kind"] = value
        units[uid].pop("meaning_id", None)
    return edit


@pytest.mark.parametrize("quoted", QUOTED, ids=["attributed", "hedged"])
@pytest.mark.parametrize("uid", ["u0165.s01", "u0168.s01"])
def test_quoted_norm_units_are_accepted_and_left_out_of_the_free_document(tmp_path, quoted, uid):
    """Review B1: a quoted norm is a single-rule check, never a layer; the seed with one quoted is Lean's and the
    retained path's alike, its predicate's gap included."""
    report = same_answer(seed_with(tmp_path, kind(uid, quoted)))
    assert report is not None
    base = D._report(D._load_document(SEED.read_bytes(), SEED, None))
    assert report["coverage"]["residual"]["gaps"] >= base["coverage"]["residual"]["gaps"]


def test_every_norm_unit_quoted_leaves_an_empty_free_document(tmp_path):
    def edit(front, units):
        for u in units.values():
            if type(u.get("content")) is dict and "norm" in u["content"]:
                u["kind"] = QUOTED[0]
    assert same_answer(seed_with(tmp_path, edit)) is not None


def test_quoted_norm_is_still_checked_as_a_rule(tmp_path):
    """A quoted norm's single-rule checks still apply: an undeclared predicate is refused on both paths."""
    def edit(front, units):
        kind("u0165.s01", QUOTED[1])(front, units)
        units["u0165.s01"]["content"]["norm"]["predicate"] = "no_such_predicate"
    with pytest.raises(VEError):
        D.check_document(seed_with(tmp_path, edit))
    same_answer(seed_with(tmp_path, edit, "again"))


def test_quoted_norm_precedence_is_not_resolved(tmp_path):
    """A quoted norm's precedence edges name rules of the quoted source and are not resolved here."""
    def edit(front, units):
        kind("u0165.s01", QUOTED[0])(front, units)
        units["u0165.s01"]["content"]["norm"]["over"] = ["a-rule-of-the-quoted-source"]
    assert same_answer(seed_with(tmp_path, edit)) is not None


def every_kind():
    """Every constructor of the kind grammar (`Route.Admission.Kind`, Python `_check_kind`): each atomic kind, and
    each compound one over `norm` and over `asserted`, nested to depth 2."""
    from ve.admission import ACTS, ATOMIC_KINDS, MODALITIES, RELATIONS
    wrap = [lambda k: ["attributed", "anthropic", ACTS[0], k], lambda k: ["hedged", MODALITIES[0], k],
            lambda k: ["causal", RELATIONS[0], k, "asserted"]]
    kinds = [*sorted(ATOMIC_KINDS), ["unformalised", "opaque"]]
    for body in ("norm", "asserted"):
        kinds += [w(body) for w in wrap] + [outer(inner(body)) for outer in wrap[:2] for inner in wrap[:2]]
    return kinds


@pytest.mark.parametrize("value", every_kind(), ids=json.dumps)
def test_norm_content_under_every_kind_has_one_answer(tmp_path, value):
    """Each kind's role for norm content (a rule, a quoted rule, or refused) is the retained path's, refusals by
    Lean's own diagnostic."""
    def edit(front, units):
        kind("u0165.s01", value)(front, units)
        if type(value) is list and value[0] == "unformalised":
            units["u0165.s01"]["meaning"] = {"unformalised": value[1]}
    same_answer(seed_with(tmp_path, edit))


def test_norm_content_under_an_open_set_claims_no_coverage(tmp_path):
    """Review B2: norm content on the unit of an open reading set is not in the free document. Lean accepted it as
    a rule, and the coverage lost the `clarification_required` gap (14 gaps, not 15)."""
    def edit(front, units):
        units["u0036.s05"]["content"] = copy.deepcopy(TOP_CLARIFY)
    report = same_answer(seed_with(tmp_path, edit))
    assert report is not None
    gaps = report["coverage"]["norm_defaults"]["gaps"]
    assert "clarification_required" in gaps
    base = D._report(D._load_document(SEED.read_bytes(), SEED, None))
    assert report["coverage"]["residual"]["gaps"] == base["coverage"]["residual"]["gaps"]


def test_norm_content_under_an_open_set_is_not_a_rule(tmp_path):
    """Its precedence edge is not resolved against the free document (a rule there, it would be UnknownRule)."""
    def edit(front, units):
        units["u0036.s05"]["content"] = copy.deepcopy(TOP_CLARIFY)
        units["u0036.s05"]["content"]["norm"]["over"] = ["a-rule-of-one-reading"]
    assert same_answer(seed_with(tmp_path, edit)) is not None


def test_norm_content_under_an_open_set_is_still_checked_as_a_rule(tmp_path):
    def edit(front, units):
        units["u0036.s05"]["content"] = copy.deepcopy(TOP_CLARIFY)
        units["u0036.s05"]["content"]["norm"]["predicate"] = "no_such_predicate"
    with pytest.raises(VEError):
        D.check_document(seed_with(tmp_path, edit))
    same_answer(seed_with(tmp_path, edit, "again"))


def attached_document(tmp_path):
    """F-ND1 with a fixed rule over the set's shared rule `must-help`: S1 1.3 attaches it to `rs_1`, so the free
    document leaves it out, and its precedence edge resolves only in each candidate's document."""
    from tests.test_readings_nd_document import as_document
    from tests.test_readings_nd_lean import ASKS, doc1, env1, norm
    from ve.readings_route import run_lean
    from ve.readings_s1 import record_situations, search

    raw = env1()
    document, _ = doc1(raw)
    document["units"].append({"id": "u3", "kind": "norm",
                              "content": norm("no-help", "help_required", False, guard=ASKS, over=("must-help",))})
    rs = document["reading_sets"][0]
    rs["situations"] = {}
    for r in rs["readings"]:
        r["admission"]["distinguishing_models"] = {o: "pending" for o in r["admission"]["distinguishing_models"]}
    [row] = run_lean([{"id": "e", "kind": "readings-elaborate", "environment": raw, "document": document}])
    assert row["status"] == "ok", row
    found = search(raw, document, "rs_1", filled=row)
    assert all(found.values())
    document["reading_sets"][0] = record_situations(rs, found)
    return as_document(tmp_path, raw, document, {"u1": "Every agent must help each user.\n",
                                                 "u3": "Unless the user asks, they need not.\n"})


def test_attached_norm_unit_is_left_out_of_the_free_document(tmp_path):
    path = attached_document(tmp_path)
    front = json.loads(path.read_bytes()[4:path.read_bytes().find(b"\n---\n")])
    assert D._s1_attached(D.base_environment(front), front) == {"u3"}
    assert same_answer(path) is not None


def test_one_selection_serves_both_python_paths():
    """`_free_norms` is the only Python reading of which norm units are rules of the free document."""
    import inspect
    source = inspect.getsource(D)
    assert source.count("def _free_norms(") == 1
    assert source.count("_free_norms(") == 3
