"""Directive 2 property: statuses and details computed for nested content reach
unit and document status and the residual, in Python and Lean alike.

For generated report documents (nesting depth 1 to 3; open assessments, stale,
missing and fresh carried scoped certificates, acts outside the slice anywhere
in a kind), `check_document`'s document status is at most every unit's status,
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
from ve.reports import ACTS, STATUS_RANK, verdict_status
from ve.reports_route import run_case

from test_reports import A1_RECORD, SAFE, contexts, scoped_certificate, write_report_document

W2_ACTS = ("says", "promised", "believes", "intends", "expects", "denies")
HOLDERS = ("article", "alice")
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


def labelled_kind(rng, depth):
    """A content-free kind of `depth` wrappers, with any W2 act at any level, and
    the acts outside the slice in it."""
    kind, acts = "asserted", []
    for _ in range(depth):
        shape = rng.choice(("attributed", "attributed", "hedged", "causal"))
        if shape == "attributed":
            act = rng.choice(W2_ACTS)
            acts += [act] if act not in ACTS else []
            kind = ["attributed", rng.choice(HOLDERS), act, kind]
        elif shape == "hedged":
            kind = ["hedged", "could", kind]
        else:
            kind = ["causal", "because", "asserted", kind]
    return kind, acts


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
    """(pieces, payloads, scoped variants, expected unit statuses, expected acts).
    u1 is a report unit without assessments (the graph's leaf); a unit whose tree
    has an assessment node is `open` over every generated name (3.3)."""
    rng = random.Random(seed)
    units, payloads, acts = [], [], []
    for index in range(rng.randint(1, 4)):
        if index == 0 or rng.random() < 0.6:
            node, path = build(rng, rng.randint(1, 3), assessments=index > 0)
            if rng.random() < 0.3:
                node = {"negated": node}
            units.append({"kind": kind_of(node), "support": "testimony", "content": node})
            payloads.append({"unit": f"u{index + 1}", "path": path} if path else f"u{index + 1}")
        else:
            kind, unit_acts = labelled_kind(rng, rng.randint(1, 3))
            units.append({"kind": kind, "meaning": "specified", "support": "testimony"})
            acts += unit_acts
    keys = {(n["judgment"], json.dumps(n["content"], sort_keys=True))
            for u in units if "content" in u for n in assessment_nodes(u["content"])}
    generated = [f"reports__{j}__{k}" for j in ("may", "probably")
                 for k in range(1, 1 + sum(key[0] == j for key in keys))]
    statuses = []
    for u in units:
        if "content" not in u:
            statuses.append("LABELLED")
        elif assessment_nodes(u["content"]):
            u["meaning"] = {"open": generated}
            statuses.append("OPEN")
        else:
            u["meaning"] = "specified"
            statuses.append("CHECKED")
    pieces = [(f"Unit u{i + 1}.\n", u) for i, u in enumerate(units)]
    variants = [rng.choice(("fresh", "stale", "missing", "none")) for _ in payloads[:rng.randint(0, 2)]]
    return pieces, payloads, variants, statuses, acts


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


def check_properties(path, variants, unit_statuses, acts):
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
    # Each status is the one the generator predicts.
    assert [(v["status"], v.get("detail")) for v in statuses["scoped"]] == [EXPECTED_SCOPED[v] for v in variants]
    assert [u["status"] for u in statuses["units"]] == unit_statuses
    assert sorted(n["act"] for n in nested if n["item"] == "act") == sorted(acts)
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


@pytest.mark.parametrize("seed", range(60))
def test_generated_documents(tmp_path, seed):
    pieces, payloads, variants, statuses, acts = generate(seed)
    check_properties(write(tmp_path, pieces, payloads, variants), variants, statuses, acts)
