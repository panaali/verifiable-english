"""The kb-10c conflict shadow (`usecases/safetyfw_conflict_shadow.py`): it records Python's `check_conflict`
status unchanged and pairs it with the soft route's answer to the same question, asked with Python's own
witness or certificates, never with Python's answer again.

Fixtures: the two-rule soft document of tests/test_soft_norms_lean.py (`a` requires `x`, `b` forbids
permitting it), whose soft CONFLICT-FREE is conditional on the coherence premise `soft:coherence:a,b`; and
stand-in documents and soft answers for the witness, rebinding and pairing checks.
"""
from __future__ import annotations

import importlib.util
import types
from pathlib import Path

from tests.test_soft_norms_lean import env, should
from ve.errors import VEError
from ve.norms import ConflictReport, check_conflict
from ve.softnorms import SoftEnvironment, SoftNormDocument

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("kb10c_conflict_shadow_under_test",
                                               ROOT / "usecases" / "safetyfw_conflict_shadow.py")
shadow_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shadow_module)


def soft_document():
    return SoftNormDocument(SoftEnvironment(env()), [should("a", "x_required", True), should("b", "x_permitted", False)])


def run_real(soft=None):
    """The real `check_conflict` on the real document, under the wrappers; Python's two answers and the shadow."""
    shadow = shadow_module.ConflictShadow(soft=soft)
    module = types.SimpleNamespace(check_conflict=check_conflict)
    doc = soft_document()
    with shadow_module.installed(shadow, module, {}):
        answers = (module.check_conflict(doc.elaborated, prove=True), module.check_conflict(doc.elaborated))
    return shadow, answers


def test_python_and_the_soft_route_agree_and_the_condition_is_counted():
    shadow, (proved, unproved) = run_real()
    assert (proved.status, unproved.status) == ("CONFLICT-FREE", "UNKNOWN")
    report = shadow.report()
    assert report["status_pairs"] == {"CONFLICT-FREE / CONFLICT-FREE": 1, "UNKNOWN / UNKNOWN": 1}
    assert report["classes"] == {"identical": 2} and report["differences"] == []
    assert report["unexplained_calls"] == 0 and report["targets_disagree"] == 0
    # The soft route names the condition the W1 status leaves unsaid.
    assert report["conflict_free_conditional"]["labels"] == ["soft:coherence:a,b"]
    free = next(q for q in shadow.questions.values() if q["python"]["status"] == "CONFLICT-FREE")
    assert free["soft"]["case"] == "packages" and free["soft"]["packages"] == len(free["python"]["targets"]) > 0


def test_a_planted_difference_is_listed_with_python_and_soft_answers():
    """Seeded bug (b) of the task: a shadow that pairs Python with Python (or with another call's answer) lists
    nothing here. The soft answer is flipped after Lean gives it; Python's answer is untouched."""
    from ve import soft_route

    def flipped(source, **case):
        row = soft_route.check_soft_conflict(source, **case)
        return {**row, "verdict": "UNKNOWN"} if row["verdict"] == "CONFLICT-FREE" else row
    shadow, (proved, _) = run_real(soft=flipped)
    assert proved.status == "CONFLICT-FREE"
    report = shadow.report()
    assert report["unexplained_calls"] == 1
    [difference] = report["differences"]
    assert (difference["python"]["status"], difference["soft"]["status"]) == ("CONFLICT-FREE", "UNKNOWN")
    assert difference["class"] == "unexplained"
    assert report["items"]["(outside an item)"]["differ"] == [difference["question"]]


class Source:
    """A stand-in soft source: what the shadow reads (identity, rules, environment)."""
    def __init__(self, name):
        self.name, self.document_hash = name, f"hash-{name}"
        self.env = types.SimpleNamespace(environment_id=f"env-{name}", to_dict=lambda: {"env": name})
        self.rules = (types.SimpleNamespace(to_dict=lambda: {"rule": name}),)


class Elaborated:
    def __init__(self, source):
        self._soft_source = source

    def conflict_targets(self):
        return (("t1", ("s",), None), ("t2", ("s",), None))


def stand_in(answers):
    """A harness whose `check_conflict` answers from `answers` (document name -> report) and whose prover runs."""
    def check(document, **options):
        report, proofs = answers[document._soft_source.name]
        if proofs is not None:
            shadow_module.ve_norms._prove_targets(document, None, 0)
        return report
    return types.SimpleNamespace(check_conflict=check)


def install_prover(monkeypatch, proofs):
    monkeypatch.setattr(shadow_module.ve_norms, "_prove_targets",
                        lambda document, *a, **k: proofs[document._soft_source.name])


def test_each_call_is_paired_with_the_soft_answer_to_its_own_question(monkeypatch):
    certificate = {"t1": {"certificate": {"trace": 1}}, "t2": {"certificate": {"trace": 2}}}
    install_prover(monkeypatch, {"x": certificate, "y": certificate})
    sent = []

    def soft(source, **case):
        sent.append((source.name, case))
        verdict = "CONFLICT-FREE" if source.name == "x" else "UNKNOWN"
        return {"verdict": verdict, "status_text": verdict, "targets": ["t1", "t2"], "conditional_on": []}
    shadow = shadow_module.ConflictShadow(soft=soft)
    answers = {"x": (ConflictReport("CONFLICT-FREE"), True), "y": (ConflictReport("CONFLICT-FREE"), True)}
    module = stand_in(answers)
    module.item = lambda label: [module.check_conflict(Elaborated(Source(n)), prove=True) for n in label]
    with shadow_module.installed(shadow, module, {"item": lambda h, label: label}):
        module.item("xyx")
    report = shadow.report()
    assert report["calls_compared"] == 3 and report["questions"] == 2 and len(sent) == 2
    assert report["status_pairs"] == {"CONFLICT-FREE / CONFLICT-FREE": 2, "CONFLICT-FREE / UNKNOWN": 1}
    assert report["items"]["xyx"]["pairs"] == {"CONFLICT-FREE / CONFLICT-FREE": 2, "CONFLICT-FREE / UNKNOWN": 1}
    # Python's certificates, re-bound to each soft source's identity, are what the soft route is sent.
    name, case = sent[1]
    assert name == "y" and set(case) == {"packages"}
    assert case["packages"]["t2"] == {"environment_id": "env-y", "document_hash": "hash-y", "target": "t2",
                                      "certificate": {"trace": 2}}


def test_pythons_witness_is_sent_and_a_refused_model_is_explained(monkeypatch):
    install_prover(monkeypatch, {})
    sent = []

    def soft(source, **case):
        sent.append(case)
        raise VEError("InvalidModel: soft background")
    model = types.SimpleNamespace(to_dict=lambda: {"domains": {"s": ["e"]}})
    shadow = shadow_module.ConflictShadow(soft=soft)
    module = stand_in({"w": (ConflictReport("CONFLICT", "t1", ("e",)), None)})
    with shadow_module.installed(shadow, module, {}):
        module.check_conflict(Elaborated(Source("w")), model=model)
    assert sent == [{"witness": {"target": "t1", "model": {"domains": {"s": ["e"]}}, "tuple": ["e"]}}]
    [entry] = shadow.questions.values()
    assert entry["soft"]["status"] == "refused"
    assert entry["class"].startswith("explained: the witness model is outside the soft premises")
    assert shadow.report()["unexplained_calls"] == 0


def test_a_document_without_a_soft_source_is_counted_not_compared(monkeypatch):
    install_prover(monkeypatch, {})
    shadow = shadow_module.ConflictShadow(soft=lambda source, **case: {})
    plain = types.SimpleNamespace(conflict_targets=lambda: ())
    module = types.SimpleNamespace(check_conflict=lambda document, **options: ConflictReport("UNKNOWN"))
    with shadow_module.installed(shadow, module, {}):
        assert module.check_conflict(plain).status == "UNKNOWN"
    assert shadow.calls == [] and shadow.report()["calls_without_soft_source"] == {"(outside an item)": 1}
