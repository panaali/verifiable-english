"""Committed W1 wire gate: regenerated Python/Lean formulas and Rust evaluation.

Rust receives generated formulas as untrusted inputs, as specified in 11.6;
it does not elaborate norms. The conflict and certificate verdicts are replayed
by Python and Lean, while Rust independently evaluates the generated formulas.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
from pathlib import Path

import pytest
from subprocesses import HANG_TIMEOUT

from ve.ast import Const, Exists, Not, Top, Unary, Var, _to_data, formula_to_data
from ve.adapters.cedar import translate
from ve.environment import Environment
from ve.errors import VEError
from ve.evaluate import evaluate
from ve.model import FiniteModel
from ve.norms import (NormDocument, _bind, _instantiate, check_conflict,
                      prove_norm_entailment, check_norm_entailment_certificate)
from tests.test_norms import environment, model, obligation, permission, rule

ROOT = Path(__file__).resolve().parents[1]
LEAN = ROOT / "lean/.lake/build/bin/ve_norms_route"
RUST = ROOT / "rust/target/release/ve"


@pytest.fixture(scope="module")
def lean_executable():
    if not LEAN.exists():
        lake = shutil.which("lake")
        if lake is None:
            pytest.skip("lake is required for the W1 wire gate")
        built = subprocess.run([lake, "build"], cwd=ROOT / "lean", capture_output=True,
                               text=True, timeout=HANG_TIMEOUT)
        assert built.returncode == 0, built.stdout + built.stderr
    return LEAN


@pytest.fixture(scope="module")
def rust_executable():
    cargo = shutil.which("cargo")
    if cargo is None:
        pytest.skip("cargo is required for the W1 wire gate")
    env = {**os.environ, "CARGO_HOME": str(ROOT / ".cargo-home"),
           "CARGO_TARGET_DIR": str(ROOT / "rust/target")}
    built = subprocess.run([cargo, "build", "-j", "2", "--locked", "--release",
                            "--manifest-path", str(ROOT / "rust/Cargo.toml")],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert built.returncode == 0, built.stdout + built.stderr
    return RUST


def run(executable, cases):
    command = [str(executable)] + (["conformance"] if executable == RUST else []) + ["-"]
    result = subprocess.run(command, input=json.dumps(cases),
                            text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert result.returncode in (0, 1), result.stderr
    rows = json.loads(result.stdout)
    assert len(rows) == len(cases)
    return rows


def corpus(count=1000):
    rng = random.Random(1102)
    for i in range(count):
        env = environment({"permitted": permission("allow" if i % 2 else "deny")},
                          base={"condition": {"arguments": ["act"], "description": "condition"}})
        rules = []
        for j in range(rng.randrange(1, 6)):
            parents = tuple(r.name for r in rules if rng.randrange(4) == 0)[:2]
            guard = (Top() if rng.randrange(2) else Unary("condition", Var(0)))
            unless = tuple(rng.choice((Top(), Unary("condition", Var(0))))
                           for _ in range(rng.randrange(3)))
            rules.append(rule(f"r{j}", "permitted", bool(rng.randrange(2)), guard,
                              unless=unless, over=parents))
        yield NormDocument(env, rules)


def pair_corpus(count=100):
    rng = random.Random(1103)
    for i in range(count):
        env = environment({"permitted": permission("allow" if i % 2 else "deny"),
                           "required": obligation("allow" if i % 3 else "deny")})
        rules = []
        for name in ("permitted", "required"):
            if rng.randrange(2):
                rules.append(rule(f"r-{name}", name, bool(rng.randrange(2))))
        yield NormDocument(env, rules)


def lean_case(index, doc):
    return {"id": str(index), "kind": "norms-elaborate", "environment": doc.env.to_dict(),
            "norms": [r.to_dict() for r in doc.rules]}


def test_noninitial_subject_act_rejected_across_languages(lean_executable, rust_executable):
    raw = environment({"permitted": permission()}).to_dict()
    raw["vocabulary"]["predicates"]["permitted"]["regulated"]["act"] = "a report be filed about {0}"
    with pytest.raises(Exception, match="invalid act phrase"):
        Environment(raw)
    lean_result = run(lean_executable, [{"id": "act", "kind": "norms-elaborate",
                                         "environment": raw, "norms": []}])[0]
    rust_result = run(rust_executable, [{"id": "act", "environment": raw, "ast": []}])[0]
    assert "invalid act phrase" in lean_result["error"]
    assert "invalid act phrase" in rust_result["error"]["message"]


# Every separator of Python's no-argument `str.split()` (str.isspace).
PY_WHITESPACE = ("\t", "\n", "\x0b", "\x0c", "\r", "\x1c", "\x1d", "\x1e", "\x1f", "\x85",
                 "\xa0", " ", " ", " ", " ", " ", " ",
                 " ", "　")


def test_act_whitespace_canonicalises_identically_across_languages(lean_executable,
                                                                   rust_executable):
    assert all(len(f"a{sep}b".split()) == 2 for sep in PY_WHITESPACE)
    doc = NormDocument(environment({"permitted": permission()}),
                       [rule("allow", "permitted", True)])
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    lean_cases, rust_cases = [], []
    for i, sep in enumerate(PY_WHITESPACE + ("​",)):
        raw = doc.env.to_dict()
        raw["vocabulary"]["predicates"]["permitted"]["regulated"]["act"] = f"{{0}}{sep}be done"
        lean_cases.append({"id": str(i), "kind": "norms-certificate", "environment": raw,
                           "norms": [r.to_dict() for r in doc.rules], "premises": [["top"]],
                           "conclusion": formula_to_data(doc.env, conclusion),
                           "certificate": proof.certificate})
        rust_cases.append({"id": str(i), "environment": raw, "ast": [["top"]]})
    lean_rows, rust_rows = run(lean_executable, lean_cases), run(rust_executable, rust_cases)
    for sep, lean_row, rust_row in zip(PY_WHITESPACE, lean_rows, rust_rows):
        raw = lean_cases[int(lean_row["id"])]["environment"]
        assert Environment(raw).environment_id == doc.env.environment_id, repr(sep)
        assert lean_row["valid"] is True, (repr(sep), lean_row)
        assert rust_row["environment_id"] == doc.env.environment_id, (repr(sep), rust_row)
    # U+200B is not whitespace in Python: every language rejects the act phrase.
    with pytest.raises(Exception, match="invalid act phrase"):
        Environment(lean_cases[-1]["environment"])
    assert "invalid act phrase" in lean_rows[-1]["error"]
    assert "invalid act phrase" in rust_rows[-1]["error"]["message"]


def test_norm_certificate_producer_and_canonical_identity_match_lean(lean_executable):
    doc = NormDocument(environment({"permitted": permission()}),
                       [rule("allow", "permitted", True)])
    conclusion = doc.elaborate("permitted")
    proof = prove_norm_entailment(doc, (Top(),), conclusion)
    assert proof.status == "Found"
    assert check_norm_entailment_certificate(doc, (Top(),), conclusion, proof.certificate).valid
    raw_env = doc.env.to_dict()
    raw_env["vocabulary"]["predicates"]["permitted"]["regulated"]["act"] = "{0}  be done"
    case = {"id": "certificate", "kind": "norms-certificate", "environment": raw_env,
            "norms": [r.to_dict() for r in doc.rules], "premises": [["top"]],
            "conclusion": formula_to_data(doc.env, conclusion), "certificate": proof.certificate}
    assert run(lean_executable, [case])[0]["valid"] is True
    changed = json.loads(json.dumps(case))
    changed["norms"][0]["norm"]["sign"] = False
    assert run(lean_executable, [changed])[0]["status"] == "error"

    from ve.entailment import prove_entailment
    packages = {}
    for target, sorts, formula in doc.conflict_targets():
        inner = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
        assert inner.status == "Found"
        packages[target] = {"environment_id": doc.env.environment_id,
                            "document_hash": doc.document_hash, "target": target,
                            "certificate": inner.certificate}
    conflict_case = {"id": "conflict", "kind": "norms-conflict", "environment": raw_env,
                     "norms": [r.to_dict() for r in doc.rules], "packages": packages}
    assert run(lean_executable, [conflict_case])[0]["verdict"] == "CONFLICT-FREE"



def test_norm_document_admission_and_provenance_match_lean(lean_executable):
    from copy import deepcopy
    from tests.test_norm_admission import source
    from ve.admission import admit_document

    env, document = source()
    cases = []
    for i, doc in enumerate((document,)):
        cases.append({"id": str(i), "kind": "admission", "environment": env.to_dict(),
                      "document": doc})
    expected = admit_document(env, document)
    result = run(lean_executable, cases)[0]
    assert result["status"] == "ok"
    assert {k: result[k] for k in expected} == expected


def test_mixed_document_norm_part_reaches_lean_and_rust(tmp_path, lean_executable,
                                                         rust_executable):
    from tests.test_document import write_doc, unit
    from ve.document import load_document, check_document
    from ve.admission import admit_document

    env = environment({"csam_permitted": permission(
        act="{0} generate child sexual abuse material", args=("assistant",))},
        sorts=("assistant",))
    norm = rule("no-csam", "csam_permitted", False)
    doc = NormDocument(env, [norm])
    source = (b"Claude should never generate child sexual abuse material (CSAM).\n"
              b"Other restrictions require causal and classification judgments.\n")
    cut = source.index(b"\n") + 1
    parts = [{**unit("rule", 0, cut, "norm", content=norm.to_dict()), "status": "CHECKED"},
             {**unit("rest", cut, len(source), ["unformalised", "causation"],
                      {"unformalised": "causation"}), "status": "UNFORMALISED"}]
    premise = doc.elaborate("csam_permitted")
    graph = {"root": "layer", "nodes": [{"name": "layer",
        "ast": formula_to_data(env, premise), "label": "layer:norms:csam_permitted"}]}
    path = write_doc(tmp_path, source, [{"id": "u0165", "span": [0, len(source)],
        "status": "MIXED", "parts": parts}], environment_json=env.to_dict(), graph=graph)
    loaded = load_document(path)
    admission = {"units": [{"id": u["id"], "span": u["span"], "kind": u["kind"],
                             **({"content": u["content"]} if u["content"] is not None else {})}
                            for u in loaded["units"]], "graph": graph,
                 "lemmas": [], "open_terms": [], "reading_sets": [], "narrowings": []}
    expected = admit_document(env, admission)
    checked = check_document(path)
    assert checked["admission"]["core_report_id"] == expected["report_id"]
    case = {"id": "mixed-csam", "kind": "admission", "environment": env.to_dict(),
            "document": admission}
    lean = run(lean_executable, [case])[0]
    assert lean["status"] == "ok"
    assert {k: lean[k] for k in expected} == expected

    model = FiniteModel.from_dict(env, {"complete": True,
        "domains": {"assistant": ["claude"]}, "constants": {},
        "relations": {"csam_permitted": []}})
    rust = run(rust_executable, [{"id": "mixed-csam-layer", "environment": env.to_dict(),
        "model": model.to_dict(), "ast": [formula_to_data(env, premise)]}])[0]
    assert rust["values"] == [True]


def test_norm_document_quoted_and_joined_match_lean(lean_executable):
    from copy import deepcopy
    from tests.test_norm_admission import source
    from ve.admission import admit_document
    env, document = source()
    cases = [{"id": "base", "kind": "admission", "environment": env.to_dict(),
              "document": document}]
    quoted = deepcopy(document)
    quoted["units"][0]["kind"] = ["attributed", "alice", "says", "norm"]
    quoted["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                            "content": ["top"]})
    quoted["graph"] = {"root": "asserted", "nodes": [
        {"name": "asserted", "ast": ["top"], "unit": "u2"}]}
    quoted_case = {"id": "quoted", "kind": "admission", "environment": env.to_dict(),
                   "document": quoted}
    quoted_expected = admit_document(env, quoted)
    quoted_result = run(lean_executable, [quoted_case])[0]
    assert {k: quoted_result[k] for k in quoted_expected} == quoted_expected

    stale = deepcopy(cases[0])
    stale["document"]["graph"]["nodes"][0]["ast"] = ["top"]
    assert run(lean_executable, [stale])[0]["status"] == "error"

    from ve.ast import And, formula_to_data
    from ve.entailment import prove_entailment
    joined = deepcopy(document)
    layer = NormDocument(env, [rule("allow", "permitted", True)]).elaborate("permitted")
    joined["units"].append({"id": "u2", "span": [20, 30], "kind": "asserted",
                             "content": ["top"]})
    joined["graph"]["nodes"].extend([
        {"name": "asserted", "ast": ["top"], "unit": "u2"},
        {"name": "joined", "ast": formula_to_data(env, And(layer, Top())),
         "premises": ["layer", "asserted"],
         "certificate": prove_entailment(env, (layer, Top()), And(layer, Top())).certificate}])
    joined["graph"]["root"] = "joined"
    joined_case = {"id": "joined", "kind": "admission", "environment": env.to_dict(),
                   "document": joined}
    expected = admit_document(env, joined)
    result = run(lean_executable, [joined_case])[0]
    assert {k: result[k] for k in expected} == expected


def test_admission_answer_is_the_bound_encoding_of_the_checked_report(lean_executable):
    """11.4: the answer encodes the checked report; its id binds the canonical
    environment and the complete source document; Background and layer leaves
    are regenerated; certificates are bound to the recomputed inputs."""
    from ve.admission import admit_document
    from ve.ast import And, Const, Eq
    from ve.entailment import prove_entailment
    from ve.wire import digest

    raw = environment({"permitted": permission()}).to_dict()
    raw["vocabulary"]["constants"] = {"alpha": {"sort": "$string"}, "beta": {"sort": "$string"}}
    env = Environment(raw)
    layer = NormDocument(env, [rule("allow", "permitted", True)]).elaborate("permitted")
    literal = Not(Eq(Const("alpha"), Const("beta")))
    joined = And(layer, literal)
    # The certificate's premises are Background (the literal) ++ (layer,).
    proof = prove_entailment(env, (layer,), joined)
    assert proof.status == "Found"
    document = {"units": [{"id": "u1", "span": [0, 20], "kind": "norm",
                           "content": rule("allow", "permitted", True).to_dict()}],
                "graph": {"root": "joined", "nodes": [
                    {"name": "layer", "ast": formula_to_data(env, layer),
                     "label": "layer:norms:permitted"},
                    {"name": "literal", "ast": formula_to_data(env, literal),
                     "label": "background:literals"},
                    {"name": "joined", "ast": formula_to_data(env, joined),
                     "premises": ["literal", "layer"], "certificate": proof.certificate}]}}
    respanned = json.loads(json.dumps(document))
    respanned["units"][0]["span"] = [0, 21]
    quoted = json.loads(json.dumps(document))
    quoted["units"].append({"id": "u2", "span": [30, 40],
                            "kind": ["attributed", "alice", "says", "norm"],
                            "content": rule("deny", "permitted", False).to_dict()})
    # A non-canonical but equivalent act phrase keeps every binding.
    spaced = json.loads(json.dumps(raw))
    spaced["vocabulary"]["predicates"]["permitted"]["regulated"]["act"] = "{0}  be done"
    variants = [(raw, document), (raw, respanned), (raw, quoted), (spaced, document)]
    rows = run(lean_executable, [{"id": f"v{i}", "kind": "admission", "environment": e,
                                  "document": d} for i, (e, d) in enumerate(variants)])
    ids = []
    for (e, d), row in zip(variants, rows):
        expected = admit_document(Environment(e), d)
        assert row["status"] == "ok", row
        assert row == {"id": row["id"], "status": "ok", **expected}
        assert [a["label"] for a in row["report"]["assumptions"]] == [
            "background:literals", "layer:norms:permitted"]
        assert row["report_id"] == digest(
            f"ve-report-{env.identity_version}\n",
            {"environment_id": env.environment_id, "document": d, "report": row["report"]})
        ids.append(row["report_id"])
    assert len(set(ids[:3])) == 3 and ids[3] == ids[0]

    tampered = []
    stale_env = json.loads(json.dumps(document))
    stale_env["graph"]["nodes"][2]["certificate"]["environment_id"] = "0" * 64
    tampered.append(stale_env)
    stale_premise = json.loads(json.dumps(document))
    stale_premise["graph"]["nodes"][2]["certificate"]["premise_meaning_ids"].reverse()
    tampered.append(stale_premise)
    wrong_literal = json.loads(json.dumps(document))
    wrong_literal["graph"]["nodes"][1]["ast"] = ["top"]
    tampered.append(wrong_literal)
    wrong_label = json.loads(json.dumps(document))
    wrong_label["graph"]["nodes"][1]["label"] = "layer:norms:permitted"
    tampered.append(wrong_label)
    rows = run(lean_executable, [{"id": f"t{i}", "kind": "admission", "environment": raw,
                                  "document": d} for i, d in enumerate(tampered)])
    for d, row in zip(tampered, rows):
        with pytest.raises(VEError):
            admit_document(env, d)
        assert row["status"] == "error", row


def test_profile_leaves_are_admitted_only_as_regenerated_pair_premises(lean_executable):
    from ve.admission import admit_document
    from ve.ast import Forall, Implies
    from ve.background import background

    env = environment({"permitted": permission(), "required": obligation()})
    premise = next(p.formula for p in background(env) if p.generator == "profile")
    reversed_premise = Forall("act", Implies(Unary("permitted", Var(0)), Unary("required", Var(0))))

    def document(ast, **extra):
        return {"units": [{"id": "u1", "span": [0, 20], "kind": "norm",
                           "content": rule("allow", "permitted", True).to_dict()}],
                "graph": {"root": "p", "nodes": [
                    {"name": "p", "ast": formula_to_data(env, ast),
                     "label": "background:profile", **extra}]}}

    good, wrong, pointed = (document(premise), document(reversed_premise),
                            document(premise, unit="u1"))
    rows = run(lean_executable, [{"id": str(i), "kind": "admission", "environment": env.to_dict(),
                                  "document": d} for i, d in enumerate((good, wrong, pointed))])
    expected = admit_document(env, good)
    assert rows[0] == {"id": "0", "status": "ok", **expected}
    for d, row in zip((wrong, pointed), rows[1:]):
        with pytest.raises(VEError):
            admit_document(env, d)
        assert row["status"] == "error", row


def test_regulated_environment_without_norm_units_matches_lean(lean_executable):
    from ve.admission import admit_document
    from tests.test_norm_admission import no_norm_unit_documents

    env, documents = no_norm_unit_documents()
    rows = run(lean_executable, [{"id": k, "kind": "admission", "environment": env.to_dict(),
                                  "document": d} for k, d in documents.items()])
    for row in rows:
        assert row == {"id": row["id"], "status": "ok", **admit_document(env, documents[row["id"]])}


def test_inactive_norm_content_is_rejected_by_lean(lean_executable):
    from ve.admission import admit_document
    from tests.test_norm_admission import inactive_norm_mutants, source

    env, _ = source()
    mutants = dict(inactive_norm_mutants())
    rows = run(lean_executable, [{"id": label, "kind": "admission", "environment": env.to_dict(),
                                  "document": doc} for label, doc in mutants.items()])
    for row in rows:
        with pytest.raises(Exception):
            admit_document(env, mutants[row["id"]])
        assert row["status"] == "error", row
    assert any(r["error"] == "norm content requires a norm or quoted kind" for r in rows)

    quoted = json.loads(json.dumps(mutants["quoted unknown predicate"]))
    quoted["units"][0]["content"]["norm"]["predicate"] = "permitted"
    quoted["units"][0]["content"]["norm"]["over"] = ["alices-other-rule"]
    expected = admit_document(env, quoted)
    result = run(lean_executable, [{"id": "edges", "kind": "admission",
                                    "environment": env.to_dict(), "document": quoted}])[0]
    assert {k: result[k] for k in expected} == expected


def test_1100_regenerated_documents_match_lean(lean_executable):
    docs = [*corpus(), *pair_corpus()]
    results = run(lean_executable, [lean_case(i, d) for i, d in enumerate(docs)])
    for i, (doc, got) in enumerate(zip(docs, results, strict=True)):
        assert got["status"] == "ok", (i, got)
        assert got["order"] == list(doc.order), i
        assert got["premises"] == [
            {"label": label, "ast": formula_to_data(doc.env, ast)}
            for label, ast in doc.premises()], i
        assert got["conflict_targets"] == [
            {"target": target, "sorts": list(sorts), "ast": _to_data(ast)}
            for target, sorts, ast in doc.conflict_targets()], i


def test_conflict_witness_and_certificates_match_lean(lean_executable):
    env = environment({"permitted": permission()},
                      base={"condition": {"arguments": ["act"], "description": "condition"}})
    yes = rule("yes", "permitted", True)
    no = rule("no", "permitted", False)
    pair = environment({"permitted": permission(), "required": obligation()})
    default_pair = environment({"permitted": permission(),
                                "required": obligation("allow")})
    examples = [NormDocument(env, [yes, no]),
                NormDocument(env, [no, rule("exception", "permitted", True, over=("no",))]),
                NormDocument(env, [no, rule("carved", "permitted", True, unless=(Top(),))]),
                NormDocument(pair, [rule("must", "required", True)]),
                NormDocument(default_pair, []),
                NormDocument(pair, [rule("must", "required", True),
                                    rule("may", "permitted", True)])]
    cases = []
    expected = []
    for i, doc in enumerate(examples):
        report = check_conflict(doc, model=model(doc))
        if report.status == "CONFLICT":
            cases.append({**lean_case(i, doc), "kind": "norms-conflict",
                          "witness": {"target": report.target, "model": model(doc).to_dict(),
                                      "tuple": list(report.tuple)}})
        else:
            from ve.entailment import prove_entailment
            packages = {}
            for target, sorts, formula in doc.conflict_targets():
                proof = prove_entailment(doc.base_environment(), (), _bind(Not(formula), sorts))
                assert proof.status == "Found"
                packages[target] = {"environment_id": doc.env.environment_id,
                                    "document_hash": doc.document_hash, "target": target,
                                    "certificate": proof.certificate}
            assert check_conflict(doc, certificates=packages).status == "CONFLICT-FREE"
            cases.append({**lean_case(i, doc), "kind": "norms-conflict", "packages": packages})
        expected.append("CONFLICT" if report.status == "CONFLICT" else "CONFLICT-FREE")
    results = run(lean_executable, cases)
    assert [r["verdict"] for r in results] == expected
    stale = json.loads(json.dumps(cases[1]))
    stale["packages"]["permitted"]["document_hash"] = "0" * 64
    assert run(lean_executable, [stale])[0]["verdict"] == "UNKNOWN"


def test_rust_evaluates_python_generated_conflicts(rust_executable):
    docs = list(corpus(48))
    cases = []
    expected = []
    for i, doc in enumerate(docs):
        base = doc.base_environment()
        witness = model(doc, condition=[["act0"]] if i % 2 else [])
        _, _, conflict = doc.conflict_targets()[0]
        closed = _bind(conflict, ("act",), binder=Exists)
        cases.append({"id": str(i), "environment": base.to_dict(), "model": witness.to_dict(),
                      "ast": [formula_to_data(base, closed)]})
        expected.append(evaluate(base, closed, witness).value)
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected


def test_rust_evaluates_python_generated_completions(rust_executable):
    from ve.evaluate import _Evaluator
    docs = list(corpus(48))
    cases = []
    expected = []
    for i, doc in enumerate(docs):
        condition = [["act0"]] if i % 2 else []
        base = model(doc, condition=condition)
        outcome = _Evaluator(doc.base_environment(), base, 100000, trace=False).formula(
            doc.outcome("permitted", base=True), (("act", "act0"),))[0]
        full = FiniteModel.from_dict(doc.env, {"complete": True,
            "domains": {"act": ["act0"]}, "constants": {},
            "relations": {"condition": condition,
                          "permitted": [["act0"]] if outcome else []}})
        premise = doc.elaborate("permitted")
        expected.append(evaluate(doc.env, premise, full).value)
        cases.append({"id": str(i), "environment": doc.env.to_dict(), "model": full.to_dict(),
                      "ast": [formula_to_data(doc.env, premise)]})
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected
    assert set(expected) == {False, True}


def test_rust_agrees_on_22_pinned_cedar_decisions(rust_executable):
    root = ROOT / "experiments/P3-formalisation-tax/items"
    cases = []
    expected = []
    for path in sorted(root.glob("c*_cit_*/item.json")):
        item = json.loads(path.read_text())
        policy = (path.parent / "source.cedar").read_text()
        questions = item["questions"]
        translated = translate(policy, item["world"].get("linked", []),
                               item["world"]["entities"], [q["request"] for q in questions])
        if translated.exclusions:
            continue
        base_data = translated.document.base_environment().to_dict()
        base_data["vocabulary"]["constants"]["query"] = {"sort": "request",
                                                          "description": "chosen request"}
        base = Environment(base_data)
        outcome = _instantiate(translated.document.outcome("permitted", base=True),
                               (Const("query"),))
        for decision, request_id in zip(translated.decisions(), translated.request_ids, strict=True):
            model_data = translated.model.to_dict()
            model_data["relations"].pop("permitted")
            model_data["constants"]["query"] = request_id
            finite = FiniteModel.from_dict(base, model_data)
            truth = decision["decision"] == "allow"
            assert evaluate(base, outcome, finite).value == truth
            cases.append({"id": f"cedar-{len(cases)}", "environment": base.to_dict(),
                          "model": finite.to_dict(), "ast": [formula_to_data(base, outcome)]})
            expected.append(truth)
    assert len(cases) == 22
    got = run(rust_executable, cases)
    assert [row["values"][0] for row in got] == expected
