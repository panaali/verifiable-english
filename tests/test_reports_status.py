"""Directive 2 property: statuses and details computed for nested content reach
unit and document status and the residual, in Python and Lean alike.

For generated report documents (nesting depth 1 to 3; open assessments, stale,
missing and fresh carried scoped certificates, acts outside the slice and
unformalised nodes anywhere in a kind, on units with and without content),
`check_document`'s document status is at most every unit's status,
every nested result and every scoped check's replayed status; every nested
result that is not CHECKED appears in the residual lines; the Lean
`reports-status` case gives the same statuses; and each status is the one the
generator predicts. The loop's reproducers are the first cases.
"""
from __future__ import annotations

from collections import Counter
import json
import random

import pytest

from ve.document import check_document, load_document
from ve.errors import VEError
from ve.reports import ACTS, STATUS_RANK, verdict_status
from ve.reports_route import run_case

from test_reports import A1_RECORD, SAFE, contexts, scoped_certificate, write_report_document

W2_ACTS = ("says", "promised", "believes", "intends", "expects", "denies")
HOLDERS = ("article", "alice")
REASONS = ("opaque", "noun_complement")
STALE = {"environment_id": None, "document_id": "0" * 64}


def build(rng, depth, *, assessments):
    """A content tree of `depth` wrappers over `safe(alice)` and the payload path
    of its formula."""
    node = {"ast": SAFE}
    for _ in range(depth):
        if assessments and rng.random() < 0.4:
            node = {"assessment": {"judgment": rng.choice(("may", "probably")), "record": "a1", "content": node}}
        else:
            node = {"report": {"holder": rng.choice(HOLDERS), "act": rng.choice(sorted(ACTS)), "context": "c1",
                               "content": node}}
    return node, ".".join(["1"] * (depth - 1))


def leaf(rng, reasons):
    """`asserted`, or an unformalised kind whose reason is recorded."""
    if rng.random() < 0.3:
        reasons.append(rng.choice(REASONS))
        return ["unformalised", reasons[-1]]
    return "asserted"


def labelled_kind(rng, depth):
    """A content-free kind of `depth` wrappers, with any W2 act at any level and
    unformalised leaves, the acts outside the slice in it and the reasons of its
    unformalised nodes."""
    acts, reasons = [], []
    kind = leaf(rng, reasons)
    for _ in range(depth):
        shape = rng.choice(("attributed", "attributed", "hedged", "causal"))
        if shape == "attributed":
            act = rng.choice(W2_ACTS)
            acts += [act] if act not in ACTS else []
            kind = ["attributed", rng.choice(HOLDERS), act, kind]
        elif shape == "hedged":
            kind = ["hedged", "could", kind]
        else:
            kind = ["causal", "because", leaf(rng, reasons), kind]
    return kind, acts, reasons


def causal_kind(rng, depth, reasons):
    """A causal kind of `depth` levels over `asserted` and unformalised leaves,
    for a unit that carries content."""
    if depth == 0:
        return leaf(rng, reasons)
    inner = causal_kind(rng, depth - 1, reasons)
    return ["causal", "because", *((inner, leaf(rng, reasons)) if rng.random() < 0.5 else
                                   (leaf(rng, reasons), inner))]


def assessment_nodes(node):
    tag, value = next(iter(node.items()))
    if tag == "negated":
        return assessment_nodes(value)
    if tag in ("report", "assessment"):
        return ([value] if tag == "assessment" else []) + assessment_nodes(value["content"])
    return []


def kind_of(node):
    if "negated" in node:
        return kind_of(node["negated"])
    if "report" in node:
        r = node["report"]
        return ["attributed", r["holder"], r["act"], kind_of(r["content"])]
    if "assessment" in node:
        a = node["assessment"]
        return ["hedged", "could" if a["judgment"] == "may" else "likely", kind_of(a["content"])]
    return "asserted"


def generate(seed):
    """(pieces, payloads, scoped variants, expected unit statuses, expected acts,
    expected unformalised reasons). u1 is a report unit without assessments (the
    graph's leaf); a unit whose tree has an assessment node is `open` over every
    generated name (3.3); a content-free or causal unit with an unformalised node
    in its kind is UNFORMALISED whatever its meaning."""
    rng = random.Random(seed)
    units, payloads, acts, reasons, unformalised = [], [], [], [], []
    for index in range(rng.randint(1, 4)):
        shape = "report" if index == 0 else rng.choice(("report", "report", "labelled", "causal"))
        unit_reasons = []
        if shape == "report":
            node, path = build(rng, rng.randint(1, 3), assessments=index > 0)
            if rng.random() < 0.3:
                node = {"negated": node}
            units.append({"kind": kind_of(node), "support": "testimony", "content": node})
            payloads.append({"unit": f"u{index + 1}", "path": path} if path else f"u{index + 1}")
        elif shape == "labelled":
            kind, unit_acts, unit_reasons = labelled_kind(rng, rng.randint(1, 3))
            units.append({"kind": kind, "meaning": "specified", "support": "testimony"})
            acts += unit_acts
        else:
            kind = causal_kind(rng, rng.randint(1, 3), unit_reasons)
            units.append({"kind": kind, "meaning": "specified", "support": "testimony", "content": {"ast": SAFE}})
        reasons += unit_reasons
        unformalised.append(bool(unit_reasons))
    keys = {(n["judgment"], json.dumps(n["content"], sort_keys=True))
            for u in units if "content" in u and "ast" not in u["content"] for n in assessment_nodes(u["content"])}
    generated = [f"reports__{j}__{k}" for j in ("may", "probably")
                 for k in range(1, 1 + sum(key[0] == j for key in keys))]
    statuses = []
    for u, has_unformalised in zip(units, unformalised):
        if has_unformalised:
            statuses.append("UNFORMALISED")
        elif "content" not in u:
            statuses.append("LABELLED")
        elif "ast" in u["content"]:
            statuses.append("CHECKED")
        elif assessment_nodes(u["content"]):
            u["meaning"] = {"open": generated}
            statuses.append("OPEN")
        else:
            u["meaning"] = "specified"
            statuses.append("CHECKED")
    pieces = [(f"Unit u{i + 1}.\n", u) for i, u in enumerate(units)]
    variants = [rng.choice(("fresh", "stale", "missing", "none")) for _ in payloads[:rng.randint(0, 2)]]
    return pieces, payloads, variants, statuses, acts, reasons


EXPECTED_SCOPED = {"fresh": ("FOLLOWS", None), "stale": ("UNKNOWN", "envelope"),
                   "missing": ("UNKNOWN", "envelope"), "none": ("UNKNOWN", "no evidence")}


def write(tmp_path, pieces, payloads, variants, **front):
    checks = [{"id": f"s{i + 1}", "payloads": [payload], "conclusion": {"ast": SAFE}}
              for i, payload in enumerate(payloads[:len(variants)])]
    bare = write_report_document(tmp_path, pieces, assessments=[A1_RECORD], scoped=checks, **front)
    reports = load_document(bare)["reports"]
    envelope = reports.envelope
    [premise] = [p for p in reports.elaborated()["premises"] if p["label"].endswith(":u1")]
    graph = {"root": "R", "nodes": [{"name": "R", "label": premise["label"], "unit": "u1", "ast": premise["ast"]}]}
    certificate = scoped_certificate(envelope["environment_id"], [SAFE], SAFE)
    stale = dict(STALE, environment_id=envelope["environment_id"])
    carried = {"fresh": {"certificate": certificate, "envelope": envelope},
               "stale": {"certificate": certificate, "envelope": stale},
               "missing": {"certificate": certificate}, "none": {}}
    checks = [dict(check, **carried[variant]) for check, variant in zip(checks, variants)]
    return write_report_document(tmp_path, pieces, assessments=[A1_RECORD], scoped=checks, graph=graph, **front)


def rank(status):
    return STATUS_RANK[status]


def check_properties(path, variants, unit_statuses, acts, reasons=()):
    result = check_document(path)
    statuses = result["statuses"]
    document = statuses["document_status"]
    lines = result["coverage"]["residual_lines"]
    residual = result["coverage"]["residual"]
    # Python and Lean agree (check_document compares them; here, once more, by hand).
    meta = json.loads(path.read_text().split("\n---\n")[0][4:])
    route_doc = {k: meta[k] for k in ("units", "contexts", "assessments", "scoped", "graph") if k in meta}
    lean = run_case("reports-status", meta["environment"], route_doc)
    assert lean["units"] == statuses["units"] and lean["document_status"] == document
    assert [(v["status"], v.get("detail")) for v in lean["scoped"]] == \
        [(v["status"], v.get("detail")) for v in statuses["scoped"]]
    # The document status is at most every unit's, nested result's and scoped check's.
    nested = [item for unit in statuses["units"] for item in unit["nested"]]
    scoped = [verdict_status(v) for v in statuses["scoped"]]
    for status in [u["status"] for u in statuses["units"]] + [n["status"] for n in nested] + scoped:
        assert rank(document) <= rank(status), (document, status)
    for unit in statuses["units"]:
        assert all(rank(unit["status"]) <= rank(n["status"]) for n in unit["nested"])
    if result["status"] != "UNVERIFIED":
        assert result["status"] == document
    # Every nested result that is not CHECKED appears in the residual lines.
    for item in nested:
        assert item["status"] != "CHECKED"
        if item["item"] == "assessment":
            assert item["name"] in lines["open_terms"]
    assert Counter(n["act"] for n in nested if n["item"] == "act") == Counter(lines["unreviewed_acts"])
    for verdict in statuses["scoped"]:
        assert verdict in lines["scoped_checks"]
    assert residual["scoped_checks"] == len(statuses["scoped"])
    assert residual["unreviewed_acts"] == len([n for n in nested if n["item"] == "act"])
    unformalised = [n for n in nested if n["item"] == "unformalised"]
    assert all(n["status"] == "UNFORMALISED" for n in unformalised)
    assert Counter(n["reason"] for n in unformalised) == Counter(lines["unformalised_kinds"])
    assert residual["unformalised_kinds"] == len(unformalised)
    # A nested one's reason is among the coverage's unformalised reasons.
    reasons_seen = result["coverage"]["unformalised_reasons"]
    for reason, count in Counter(n["reason"] for n in unformalised if n["path"]).items():
        assert reasons_seen.get(reason, 0) >= count
    # Each status is the one the generator predicts.
    assert [(v["status"], v.get("detail")) for v in statuses["scoped"]] == [EXPECTED_SCOPED[v] for v in variants]
    assert [u["status"] for u in statuses["units"]] == unit_statuses
    assert sorted(n["act"] for n in nested if n["item"] == "act") == sorted(acts)
    assert sorted(n["reason"] for n in unformalised) == sorted(reasons)
    expected = min(unit_statuses + ["CHECKED" if v == "fresh" else "UNKNOWN" for v in variants], key=rank)
    assert document == expected
    return result


REPORT = {"report": {"holder": "article", "act": "says", "context": "c1", "content": {"ast": SAFE}}}
REPRODUCERS = [
    # Scoped-check outcomes: a valid carried certificate, and the same one under a stale envelope.
    ([("Unit u1.\n", {"kind": ["attributed", "article", "says", "asserted"], "meaning": "specified",
                      "support": "testimony", "content": REPORT})], ["u1"], ["fresh"], ["CHECKED"], []),
    ([("Unit u1.\n", {"kind": ["attributed", "article", "says", "asserted"], "meaning": "specified",
                      "support": "testimony", "content": REPORT})], ["u1"], ["stale"], ["CHECKED"], []),
    # Nested unreviewed acts: the attributed and the hedged wrapper.
    ([("Unit u1.\n", {"kind": ["attributed", "article", "says", "asserted"], "meaning": "specified",
                      "support": "testimony", "content": REPORT}),
      ("Unit u2.\n", {"kind": ["attributed", "article", "says", ["attributed", "alice", "promised", "asserted"]],
                      "meaning": "specified", "support": "testimony"}),
      ("Unit u3.\n", {"kind": ["hedged", "could", ["attributed", "alice", "promised", "asserted"]],
                      "meaning": "specified", "support": "testimony"})],
     [], [], ["CHECKED", "LABELLED", "LABELLED"], ["promised", "promised"]),
]


@pytest.mark.parametrize("case", range(len(REPRODUCERS)))
def test_loop_reproducers(tmp_path, case):
    pieces, payloads, variants, statuses, acts = REPRODUCERS[case]
    result = check_properties(write(tmp_path, pieces, payloads, variants), variants, statuses, acts)
    assert result["status"] == {0: "CHECKED", 1: "UNKNOWN", 2: "LABELLED"}[case]


def test_stale_by_changed_context(tmp_path):
    """The loop's own stale envelope: the certificate's envelope is the document's
    before its context's tense changed."""
    pieces, payloads, variants, statuses, acts = REPRODUCERS[0]
    fresh = write(tmp_path, pieces, payloads, variants)
    meta = json.loads(fresh.read_text().split("\n---\n")[0][4:])
    path = write_report_document(tmp_path, pieces, assessments=[A1_RECORD], scoped=meta["scoped"],
                                 graph=meta["graph"], contexts=contexts("past"))
    result = check_properties(path, ["stale"], statuses, acts)
    assert result["status"] == "UNKNOWN"


ADMITTED = ("Unit u1.\n", {"kind": ["attributed", "article", "says", "asserted"], "meaning": "specified",
                           "support": "testimony", "content": REPORT})
OPAQUE = ["unformalised", "opaque"]
UNFORMALISED_KINDS = [
    # Recheck B: a testimony-backed unit with specified meaning and valid AST
    # content, an unformalised node on either causal branch at depths 1 to 3.
    ["causal", "because", "asserted", OPAQUE],
    ["causal", "because", OPAQUE, "asserted"],
    ["causal", "because", "asserted", ["causal", "because", "asserted", OPAQUE]],
    ["causal", "because", ["causal", "because", OPAQUE, "asserted"], "asserted"],
    ["causal", "because", "asserted", ["causal", "because", ["causal", "because", OPAQUE, "asserted"], "asserted"]],
    ["causal", "because", ["causal", "because", "asserted", ["causal", "because", "asserted", OPAQUE]], "asserted"],
]
UNFORMALISED_PATHS = ["2", "1", "2.2", "1.1", "2.1.1", "1.2.2"]


@pytest.mark.parametrize("case", range(len(UNFORMALISED_KINDS)))
def test_nested_unformalised_kind_reaches_status_and_residual(tmp_path, case):
    """Recheck B: with an admitted report beside it, a unit whose kind nests
    `["unformalised", "opaque"]` under causal wrappers gave CHECKED, `nested: []`,
    a CHECKED document and no unformalised reason or residual entry, in Python and
    Lean, while the same marker at the root is rejected unless the meaning is
    unformalised. The node is now an UNFORMALISED nested result with its reason."""
    piece = ("Unit u2.\n", {"kind": UNFORMALISED_KINDS[case], "meaning": "specified", "support": "testimony",
                            "content": {"ast": SAFE}})
    result = check_properties(write(tmp_path, [ADMITTED, piece], ["u1"], ["fresh"]), ["fresh"],
                              ["CHECKED", "UNFORMALISED"], [], ["opaque"])
    assert result["status"] == "UNFORMALISED"
    assert result["statuses"]["units"][1]["nested"] == [
        {"item": "unformalised", "path": UNFORMALISED_PATHS[case], "reason": "opaque", "status": "UNFORMALISED"}]
    assert result["coverage"]["residual_lines"]["unformalised_kinds"] == {"opaque": 1}
    assert result["coverage"]["unformalised_reasons"] == {"opaque": 1}
    assert result["coverage"]["bytes_by_status"]["UNFORMALISED"] == len(piece[0])


def test_unformalised_kind_without_content_and_at_the_root(tmp_path):
    """The same class on content-free quoted and hedged kinds (LABELLED before)
    and at the root, where W2 already needs an unformalised meaning: every
    unformalised node, at any depth, is a nested result and a residual entry, its
    reason counted once per unit part."""
    pieces = [ADMITTED,
              ("Unit u2.\n", {"kind": ["attributed", "article", "says", ["unformalised", "noun_complement"]],
                              "meaning": "specified", "support": "testimony"}),
              ("Unit u3.\n", {"kind": ["hedged", "could", ["attributed", "alice", "promised", OPAQUE]],
                              "meaning": "specified", "support": "testimony"}),
              ("Unit u4.\n", {"kind": OPAQUE, "meaning": {"unformalised": "opaque"}, "support": "none"})]
    result = check_properties(write(tmp_path, pieces, [], []), [],
                              ["CHECKED", "UNFORMALISED", "UNFORMALISED", "UNFORMALISED"], ["promised"],
                              ["noun_complement", "opaque", "opaque"])
    assert result["status"] == "UNFORMALISED"
    assert [[(n["item"], n["path"]) for n in u["nested"]] for u in result["statuses"]["units"]] == \
        [[], [("unformalised", "1")], [("act", "1"), ("unformalised", "1.1")], [("unformalised", "")]]
    assert result["coverage"]["residual_lines"]["unformalised_kinds"] == {"noun_complement": 1, "opaque": 2}
    assert result["coverage"]["unformalised_reasons"] == {"noun_complement": 1, "opaque": 2}


def test_root_kind_reason_mismatch_is_rejected_before_coverage(tmp_path):
    """The review reproducer: the admitted report beside a content-free root
    cannot hide an opaque marker behind a different meaning reason."""
    pieces = [ADMITTED, ("Unit u2.\n", {"kind": OPAQUE,
                                   "meaning": {"unformalised": "noun_complement"}, "support": "none"})]
    path = write_report_document(tmp_path, pieces)
    meta = json.loads(path.read_text().split("\n---\n")[0][4:])
    route_doc = {k: meta[k] for k in ("units", "contexts")}
    with pytest.raises(VEError, match="^InvalidInput: unformalised kind reason does not match meaning of u2$"):
        load_document(path)
    with pytest.raises(VEError, match="^InvalidInput: unformalised kind reason does not match meaning of u2$"):
        run_case("reports-status", meta["environment"], route_doc)


def test_nested_reason_remains_independent_of_unit_meaning(tmp_path):
    pieces = [ADMITTED, ("Unit u2.\n", {
        "kind": ["causal", "because", OPAQUE, "asserted"],
        "meaning": {"unformalised": "noun_complement"}, "support": "none"})]
    result = check_document(write_report_document(tmp_path, pieces))
    assert result["coverage"]["unformalised_reasons"] == {"noun_complement": 1, "opaque": 1}
    assert result["coverage"]["residual_lines"]["unformalised_kinds"] == {"opaque": 1}
    assert result["statuses"]["units"][1]["nested"] == [
        {"item": "unformalised", "path": "1", "reason": "opaque", "status": "UNFORMALISED"}]


def test_explicit_checked_status_contradicts_a_nested_unformalised_kind(tmp_path):
    piece = ("Unit u2.\n", {"kind": UNFORMALISED_KINDS[0], "meaning": "specified", "support": "testimony",
                            "content": {"ast": SAFE}, "status": "CHECKED"})
    with pytest.raises(VEError, match="unit status contradicts"):
        load_document(write_report_document(tmp_path, [ADMITTED, piece]))


@pytest.mark.parametrize("seed", range(60))
def test_generated_documents(tmp_path, seed):
    pieces, payloads, variants, statuses, acts, reasons = generate(seed)
    check_properties(write(tmp_path, pieces, payloads, variants), variants, statuses, acts, reasons)
