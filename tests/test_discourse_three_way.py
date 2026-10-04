"""Discourse three-way evidence (docs/spec/discourse.md 10 alpha and alpha-prime, 11).

One `ve-document@2` text is written once and read by all three implementations: Python
(`check_document` on the file), the Lean route (`ve_discourse_route` on the same bytes) and Rust,
which never resolves references and receives, as an untrusted `elaborated-document` case, the
elaborated formulas Python admitted. Identities (source, document, environment, meaning and
report ids), statuses, the report, the diagnostics of rejected manifests and the premise verdict
must agree. Alpha registers `bob` so that the type check is the only filter on its three
accessible candidates; alpha-prime covers every sub-case of the fixture, each with the
natural-view outcome it records.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tests import lean_routes

from tests.test_discourse_lean import run as lean_run
from ve.document import check_document, load_document
from ve.english import parse_english
from ve.environment import Environment
from ve.errors import VEError

ROOT = Path(__file__).resolve().parents[1]
LEAN = "ve_discourse_route"  # its service mode, through tests/lean_routes.py
RUST = ROOT / "rust/target/release/ve"
CONSTANTS = {"api": "service", "beta": "service", "gamma": "service", "alice": "person", "bob": "person"}
PREDICATES = {"reviewed": ["service"], "deployed": ["service"], "ready": ["person"]}
DISPLAY = {"api": "Api", "beta": "Beta", "gamma": "Gamma", "alice": "Alice", "bob": "Bob"}
CONTENT = {"Api is reviewed.": ["unary", "reviewed", ["const", "api"]],
           "Beta is reviewed.": ["unary", "reviewed", ["const", "beta"]],
           "Alice is ready.": ["unary", "ready", ["const", "alice"]],
           "It is deployed.": ["unary", "deployed", ["const", "api"]]}


def environment(profiles=("relational-fol@0", "ve.discourse@1")):
    return {"language": "ve.core@0.2", "profiles": list(profiles), "spec_revision": "ve-v0.2-expand2-2026-09-25",
            "vocabulary": {"sorts": {s: {"description": s} for s in ("service", "person")},
                           "predicates": {p: {"arguments": a, "description": p} for p, a in PREDICATES.items()},
                           "constants": {c: {"sort": s, "description": c} for c, s in CONSTANTS.items()}}}


def write(tmp_path, sentences, names, target="api", sections=None):
    """The shared document: a unit per sentence, the last one `It is deployed.` with its mention."""
    source, units = b"", []
    for i, sentence in enumerate(sentences):
        start = len(source)
        source += sentence.encode() + b"\n"
        content = CONTENT.get(sentence)
        unit = {"id": f"u{i + 1}", "span": [start, len(source)], "meaning": "specified",
                "kind": "asserted" if content else "exposition", "support": "assumption" if content else "none"}
        if content:
            unit["content"] = {"ast": content}
        units.append(unit)
    last = units[-1]
    anchors = [{"id": "doc", "kind": "document", "label": "Policy", "span": [0, len(source)]}]
    for sid, label, (first, final) in sections or ():
        anchors.append({"id": sid, "kind": "section", "parent": "doc", "label": label,
                        "span": [units[first]["span"][0], units[final]["span"][1]]})
    front = {"format": "ve-document@2", "environment": environment(), "units": units,
             "graph": {"root": "claim", "nodes": [{"name": "claim", "ast": CONTENT["It is deployed."], "unit": last["id"]}]},
             "discourse": {"version": "ve.discourse@1", "anchors": anchors,
                           "names": [{"constant": c, "display": DISPLAY[c], "scope": "doc"} for c in names],
                           "mentions": [{"id": "m1", "unit": last["id"], "span": [last["span"][0], last["span"][0] + 2],
                                         "form": "pronoun", "target": {"kind": "entity", "name": target}}]}}
    text = "---\n" + json.dumps(front) + "\n---\n" + source.decode()
    path = tmp_path / "shared.ve.md"
    path.write_text(text)
    return path, text


def python_outcome(path):
    try:
        return check_document(path), load_document(path)
    except VEError as exc:
        return str(exc), None


def lean_outcome(text):
    row = lean_run([{"id": "shared", "kind": "admission", "document": text}])[0]
    return row if row["status"] == "ok" else row["error"]


def rust_outcome(formulas):
    base = environment(("relational-fol@0",))
    case = {"id": "shared", "family": "elaborated-document", "untrusted": True, "environment": base,
            "formulas": formulas}
    rust = subprocess.run([str(RUST), "conformance"], input=json.dumps(case), text=True, capture_output=True,
                          timeout=60)
    assert rust.returncode == 0, rust.stdout + rust.stderr
    return json.loads(rust.stdout)[0]


def natural_view(sentences):
    env = Environment(environment(("relational-fol@0",)))
    try:
        parse_english(env, " ".join(sentences))
        return "accept"
    except (VEError, SyntaxError):
        return "reject"


def agree(tmp_path, sentences, names, target="api", sections=None):
    """Run the shared document through the three implementations; return the common outcome."""
    for binary in (LEAN, RUST):
        if not binary.exists():
            pytest.skip(f"{binary.name} is not built")
    path, text = write(tmp_path, sentences, names, target, sections)
    python, loaded = python_outcome(path)
    lean = lean_outcome(text)
    if isinstance(python, str) or isinstance(lean, str):
        assert python == lean, (python, lean)
        return python
    last = f"u{len(sentences)}"
    # identities on the same bytes
    assert lean["source_id"] == python["source_id"] == loaded["source_id"]
    assert lean["document_id"] == python["document_id"]
    assert lean["environment_id"] == loaded["environment"].environment_id
    # the elaborated formula, its meaning id, the report and the report identities
    assert lean["bound"] == {last: CONTENT["It is deployed."]}
    unit_ids = {u["id"]: u["meaning_id"] for u in loaded["units"]}
    assert lean["meaning_ids"] == {last: unit_ids[last]}
    assert lean["report"] == python["admission"]["report"]
    assert lean["inner_report_id"] == python["admission"]["report_id"]
    assert lean["report_id"] == python["report_id"]
    assert lean["statuses"] == {u["id"]: u["status"] for u in loaded["units"]}
    assert python["reviewed_presentations"][last].strip() == "Api is deployed."
    # Rust on the elaborated document Python admitted (untrusted input)
    formulas = [u["content"] for u in loaded["units"] if u["content"] is not None]
    rust = rust_outcome(formulas)
    assert rust["family"] == "elaborated-document" and rust["untrusted"] is True
    assert rust["environment_id"] == lean["environment_id"]
    assert rust["meaning_ids"] == [u["meaning_id"] for u in loaded["units"] if u["content"] is not None]
    assert rust["premises"]["status"] == python["premises"]["status"] == "model"
    return lean["bound"][last]


def test_alpha_three_way(tmp_path):
    """Alpha: three accessible candidates (api, alice, bob), one type-checks."""
    names = ["api", "alice", "bob"]
    assert agree(tmp_path, ["Api is reviewed.", "It is deployed."], names) == CONTENT["It is deployed."]
    _, text = write(tmp_path, ["Api is reviewed.", "It is deployed."], names)
    resolved = lean_run([{"id": "r", "kind": "discourse-resolve", "document": text}])[0]
    assert {t["name"] for t in resolved["mentions"]["m1"]["accessible"]} == set(names)
    assert agree(tmp_path, ["Api is reviewed.", "It is deployed."], names, target="alice") == \
        "IllTypedTarget: m1: alice"


ALPHA_PRIME = [
    # (sentences, registered names, sections, manifest outcome, natural view)
    (["Api is reviewed.", "Alice is ready.", "It is deployed."], ["api", "alice"], None,
     CONTENT["It is deployed."], "reject"),
    (["Api is reviewed.", "It is deployed."], ["api", "alice"], None, CONTENT["It is deployed."], "accept"),
    (["Api is reviewed.", "Beta is reviewed.", "It is deployed."], ["api", "beta"], None,
     "AmbiguousReference: m1: api, beta", "reject"),
    (["Api is reviewed.", "It is deployed."], ["api", "beta"], None, "AmbiguousReference: m1: api, beta", "accept"),
    (["Some service is deployed.", "Api is reviewed.", "It is deployed."], ["api", "alice"],
     [("sec1", "1", (0, 0)), ("sec2", "2", (1, 2))], CONTENT["It is deployed."], "reject"),
    (["Api is reviewed.", "Beta is reviewed.", "It is deployed."], ["api", "beta", "gamma"], None,
     "AmbiguousReference: m1: api, beta, gamma", "reject"),
]


@pytest.mark.parametrize("sentences,names,sections,manifest,natural", ALPHA_PRIME,
                         ids=["two-sorts", "unmentioned-other-sort", "second-service-mentioned",
                              "second-service-unmentioned", "binder-in-earlier-anchor", "three-versus-two"])
def test_alpha_prime_three_way(tmp_path, sentences, names, sections, manifest, natural):
    """Alpha-prime: the manifest's outcome, in all three, and the natural view's, as recorded."""
    assert agree(tmp_path, sentences, names, sections=sections) == manifest
    assert natural_view(sentences) == natural
