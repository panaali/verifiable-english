"""W6a loop recheck 1, P1 (directive incomplete): citations on the quantity
document route.

A citation is bound by a checked lemma: its `ve-quantity-certificate@1`
establishes the conclusion from exactly its transitive leaves, bound to their
annotated meaning ids. A `cite` leaf states that conclusion, and the report
carries the lemma's leaves with their labels. Lean `VE.Time.Document` is the
authority (`cites_discharged`); Python relays it (Lean-first batch 9 deleted
Python's copy and Rust's quantity route). Each binding class is rejected the same
way by the relay and by Lean.
"""
import copy
from pathlib import Path

import pytest

from tests import lean_routes

from tests.test_units_lean_w6a import LEAN, lean
from tests.test_w6a_documents import DELETE, HIGH, LOW, MONEY_LOW, ORDER, doc_env, mutate, q, relay_and_lean
from ve.admission import AdmissionError
from ve.environment import Environment
from ve.errors import VEError
from ve.units import prove_quantity, quantity_meaning_id

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="build the Lean service first")

BRIDGE = "bridge:accepts(fed,u_high)"
LE = q(["le", ["const", "bp", "low"], ["const", "bp", "high"]])
MONEY_ORDER = q(["lt", ["const", "usd_cent", "cost"], ["const", "usd_cent", "price"]])


def lemma(env, conclusion=ORDER, leaves=((LOW, "asserted"), (HIGH, BRIDGE)), name="fed/order"):
    return {"name": name, "conclusion": conclusion,
            "leaves": [{"quantity": p, "label": label} for p, label in leaves],
            "certificate": prove_quantity(env, [p for p, _ in leaves], conclusion)}


def cited_document(env):
    """`order` is cited from a checked lemma; the root rests on it and on the
    lemma's leaves, which the report must carry."""
    return {"units": [{"id": "u_low", "span": [0, 10], "kind": "asserted", "content": LOW},
                      {"id": "u_high", "span": [10, 20], "kind": ["attributed", "fed", "says", "asserted"],
                       "content": HIGH}],
            "lemmas": [lemma(env)],
            "graph": {"root": "le", "nodes": [
                {"name": "low", "quantity": LOW, "unit": "u_low"},
                {"name": "high", "quantity": HIGH, "label": BRIDGE},
                {"name": "order", "quantity": ORDER, "label": "cite:fed/order"},
                {"name": "le", "quantity": LE, "premises": ["low", "high", "order"],
                 "certificate": prove_quantity(env, [LOW, HIGH, ORDER], LE)}]}}


def test_a_checked_lemma_is_cited_relay_and_lean():
    raw = doc_env()
    env = Environment(raw)
    document = cited_document(env)
    python, got = relay_and_lean(raw, document)
    assert got["status"] == "ok" and got["assurance"] == "lean-admitted", got
    assert got["report"] == python["report"] and got["report_id"] == python["report_id"]
    labels = [(a["name"], a.get("label", "asserted")) for a in got["report"]["assumptions"]]
    assert labels == [("low", "asserted"), ("high", BRIDGE), ("order", "cite:fed/order")]
    # The cited statement is bound by its annotated meaning id.
    assert got["report"]["assumptions"][2]["meaning_id"] == quantity_meaning_id(env, ORDER)


def test_the_review_reproducer_now_admits():
    # The recheck's reproducer: a quantity document with a cite label and a
    # lemma rejected as unsupported. With a checked lemma it is admitted.
    raw = doc_env()
    python, got = relay_and_lean(raw, cited_document(Environment(raw)))
    assert python["admitted"] is True and got["admitted"] is True


def citation_rejections(env):
    document = cited_document(env)
    certificate = document["lemmas"][0]["certificate"]
    return [
        # The report must carry every leaf of the cited lemma, with its label and statement.
        ("leaves missing", mutate(document, ["graph", "nodes", 3],
                                  {"name": "le", "quantity": LE, "premises": ["order"],
                                   "certificate": prove_quantity(env, [ORDER], LE)}),
         "a cited lemma's leaves are missing from the report"),
        ("leaf label changed", mutate(document, ["lemmas", 0], lemma(env, leaves=((LOW, "asserted"),
                                                                                (HIGH, "open:high")))),
         "a cited lemma's leaves are missing from the report"),
        ("leaf statement changed", mutate(document, ["lemmas", 0], lemma(
            env, leaves=((LOW, "asserted"), (q(["eq", ["const", "bp", "high"], ["decimal", "bp", "5.00"]]),
                                              BRIDGE)))),
         "a cited lemma's leaves are missing from the report"),
        # The lemma's certificate binds exactly its leaves and conclusion.
        ("leaves reordered", mutate(document, ["lemmas", 0, "leaves"],
                                    list(reversed(document["lemmas"][0]["leaves"]))),
         "lemma fed/order is not established by its certificate"),
        ("leaf dropped", mutate(document, ["lemmas", 0, "leaves"], document["lemmas"][0]["leaves"][:1]),
         "lemma fed/order is not established by its certificate"),
        ("conclusion strengthened", mutate(document, ["lemmas", 0, "conclusion"],
                                           q(["lt", ["const", "bp", "high"], ["const", "bp", "low"]])),
         "lemma fed/order is not established by its certificate"),
        ("relabelled to money", mutate(document, ["lemmas", 0, "conclusion"], MONEY_ORDER),
         "lemma fed/order is not established by its certificate"),
        ("certificate from another environment", mutate(document, ["lemmas", 0, "certificate"],
                                                        {**certificate, "environment_id": "0" * 64}),
         "lemma fed/order is not established by its certificate"),
        ("raw core certificate", mutate(document, ["lemmas", 0, "certificate"], certificate["core"]),
         "Invalid quantity certificate"),
        ("certificate missing", mutate(document, ["lemmas", 0, "certificate"], DELETE), "certificate"),
        # A cite leaf states exactly the lemma's conclusion, names a declared lemma, has no unit.
        ("cite states another statement", mutate(document, ["graph", "nodes", 2, "quantity"], LE),
         "node order is not admitted under label cite:fed/order"),
        ("cite names no lemma", mutate(document, ["graph", "nodes", 2, "label"], "cite:fed/other"),
         "node order is not admitted under label cite:fed/other"),
        ("cite with a unit", mutate(document, ["graph", "nodes", 2, "unit"], "u_low"),
         "node order is not admitted under label cite:fed/order"),
        # Lemma declarations.
        ("lemma leaf cites", mutate(document, ["lemmas", 0, "leaves", 0, "label"], "cite:fed/order"),
         "lemma leaves must be transitive (no cite labels)"),
        ("lemma leaf label invalid", mutate(document, ["lemmas", 0, "leaves", 0, "label"], "cite:x"),
         "invalid label cite:x"),
        ("lemma name invalid", mutate(document, ["lemmas", 0, "name"], "order"), "invalid lemma name order"),
        ("duplicate lemma", {**document, "lemmas": document["lemmas"] * 2}, "duplicate lemma"),
        ("lemma forged Q", mutate(document, ["lemmas", 0, "conclusion"],
                                  {**ORDER, "Q": ["lt", ["const", "bp", "high"], ["const", "bp", "low"]]}),
         "Q differs"),
        ("lemma leaf unit mismatch", mutate(document, ["lemmas", 0, "leaves", 0, "quantity"],
                                            q(["eq", ["const", "bp", "low"], ["decimal", "usd_cent", "3.75"]])),
         "UnitMismatch(bp,usd_cent)"),
    ]


CASES = len(citation_rejections(Environment(doc_env())))


@pytest.mark.parametrize("index", range(CASES))
def test_every_citation_binding_class_rejects_in_python_and_lean(index):
    raw = doc_env()
    name, document, message = citation_rejections(Environment(raw))[index]
    python, got = relay_and_lean(raw, document)
    assert isinstance(python, VEError) and message in str(python), (name, python)
    assert got["status"] == "error" and message in got["error"], (name, got)


def test_relabelling_the_whole_citation_to_money_fails():
    """Units-schema §3.2: relabelling percent to money must fail the outer
    binding even though every erased integer problem is unchanged."""
    raw = doc_env()
    env = Environment(raw)
    document = cited_document(env)
    money_high = q(["eq", ["const", "usd_cent", "price"], ["decimal", "usd_cent", "4.00"]])
    relabelled = copy.deepcopy(document)
    relabelled["lemmas"][0]["conclusion"] = MONEY_ORDER
    relabelled["lemmas"][0]["leaves"] = [{"quantity": MONEY_LOW, "label": "asserted"},
                                         {"quantity": money_high, "label": BRIDGE}]
    python, got = relay_and_lean(raw, relabelled)
    assert isinstance(python, AdmissionError) and "not established by its certificate" in str(python)
    assert "not established by its certificate" in got["error"]


def test_citation_soundness_is_audited():
    audit = (ROOT / "lean" / "VE" / "Audit.lean").read_text()
    for name in ("cites_discharged", "isCite_parse", "admitDecoded_sound", "admit_quantity_report_sound"):
        assert f"#print axioms VE.Time.Document.{name}\n" in audit
    source = (ROOT / "lean" / "VE" / "Time" / "Document.lean").read_text()
    assert "Entry.SoundOverLeaves.{v} res.root := by" in source


def test_quantity_lemmas_do_not_pass_the_core_bundle_checker():
    """The core `ve-bundle@0` checker never replays an extended environment, so
    a quantity citation cannot bypass annotated admission there."""
    from ve.bundle import check_bundle
    raw = doc_env()
    env = Environment(raw)
    item = lemma(env)
    bundle = {"version": "ve-bundle@0", "environment": raw, "lemmas": [
        {"name": "order", "environment_id": env.environment_id,
         "premises": [{"label": "asserted", "ast": ["lt", ["const", "low"], ["const", "high"]]}],
         "cites": [], "conclusion": ["lt", ["const", "low"], ["const", "high"]],
         "meaning_id": "0" * 64, "reading_choices": {}, "transitive_leaves": [],
         "certificate": item["certificate"]["core"]}]}
    with pytest.raises(VEError):
        check_bundle(bundle)
