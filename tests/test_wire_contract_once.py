"""Each value of a wire-contract input is read once per run, in both engines (ap-1bfb review F2).

Rule typing (4.7 of `norms@0`, which `acts@0` and `norm-defaults@0` include, and 5.7 to 5.8 of `soft-norms@0`) ran
once per rule and decoded the environment, and in `norms@0` re-typed every earlier rule, at each one. Lean's
`Hooks.*.hooksFor` and Python's `registry.once` now build these values once per run. Large valid sources within the
limits come back clean before the deadline, and the Python counts show each value read once."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from conformance import softnorms_legacy
from conformance.acts_contract import REGISTRY as ACTS
from conformance.softnorms_contract import REGISTRY as SOFT
from conformance.wire_contract_engine import CLEAN, load, run
from conformance.wire_contract_faults_acts import base as acts_base
from conformance.wire_contract_faults_norms import base as norms_base
from tests import lean_routes
from ve import norms_contract
from ve.norms import NormDocument
from ve.wire_contract.registry import once, one_run

pytestmark = pytest.mark.skipif(not lean_routes.SERVICE.exists(), reason="ve_service is not built")
ROOT = Path(__file__).resolve().parents[1]
# The CPU deadline of the large sources: far above what they need now, far below what 4.7 spent per rule before.
CPU_SECONDS = 30.0
RULES = 256  # `norms@0`'s rule limit, which the base's `NormDocument` admits


def test_once_reads_a_value_once_per_run_and_root():
    calls = []

    def compute(root):
        calls.append(root)
        return len(calls)

    a, b = {"x": 1}, {"x": 1}
    assert [once("v", a, compute), once("v", a, compute)] == [1, 2]  # outside a run, at each call
    with one_run():
        assert [once("v", a, compute), once("v", a, compute), once("v", b, compute), once("w", a, compute)] == [3, 3, 4, 5]
    with one_run():
        assert once("v", a, compute) == 6

    def refuse(root):
        calls.append(root)
        raise ValueError("refused")

    with one_run():
        for _ in range(2):
            with pytest.raises(ValueError, match="refused"):
                once("r", a, refuse)
    assert len(calls) == 7


def counting(monkeypatch, owner, name, wrap=lambda f: f):
    calls = []
    real = getattr(owner, name)

    def counted(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(owner, name, wrap(counted))
    return calls


def joined_source():
    """The review's PROBE F2: 60 joined acts read by one frame, and `RULES` rules."""
    raw, _ = acts_base()
    vocabulary = raw["vocabulary"]
    words = [chr(97 + i // 26) + chr(97 + i % 26) for i in range(60)]
    vocabulary["acts"] = {"fixed": ["equal pay for equal work"] + [f"cruel {w} treatment" for w in words],
                          "frames": [{"head": "subjected", "markers": ["to"], "split": ["to"], "modifiers": []}]}
    vocabulary["predicates"].update({f"j{i:03d}": {
        "arguments": ["person"], "description": "d", "regulated": {
            "role": "permission", "default": "deny", "act": f"{{0}} be subjected to torture or to cruel {w} treatment"}}
        for i, w in enumerate(words)})
    norms = [{"norm": {"name": f"r{i}", "predicate": "protected", "sign": True, "guard": ["unary", "c", ["var", 0]],
                       "unless": [], "over": []}} for i in range(RULES)]
    return raw, norms


def many_rules(raw, norms):
    """`RULES` copies of the source's first rule, each with its own name and over no other."""
    return raw, [{"norm": {**deepcopy(norms[0]["norm"]), "name": f"r{i}", "over": []}} for i in range(RULES)]


@pytest.mark.parametrize("unit, source, registry", [
    ("acts@0", joined_source, ACTS),
    ("norms@0", lambda: many_rules(*norms_base()), norms_contract.REGISTRY)])
def test_rule_typing_reads_the_environment_and_each_rule_once_per_run(monkeypatch, unit, source, registry):
    """PROBE F2 (`acts@0`: about 120 s of the service's CPU before, near `diagnose`'s deadline; about 1 s now), and
    `norms@0` at its rule limit: clean in Lean under a lowered CPU deadline (`completed_within`, which no stored
    answer serves); clean in Python, with one environment decode and one decode of each rule in the run."""
    raw, norms = source()
    assert len(norms) == RULES
    case = {"id": "c", "unit": unit, "kind": "norms-elaborate", "environment": raw, "norms": norms}
    completed = lean_routes.completed_within("diagnose", [case], cpu_seconds=CPU_SECONDS)
    assert completed.returncode == 0, (completed.returncode, completed.stderr[-2000:])
    assert json.loads(completed.stdout) == [{"id": "c", "status": "ok", "outcome": "clean"}]
    environments = counting(monkeypatch, norms_contract, "Environment")
    decodes = counting(monkeypatch, NormDocument, "_decode", staticmethod)
    assert run(load(unit), {"environment": deepcopy(raw), "norms": deepcopy(norms)}, registry=registry) is CLEAN
    assert (len(environments), len(decodes)) == (1, RULES)


def test_a_typing_fault_at_a_late_rule_is_found_with_each_rule_typed_once(monkeypatch):
    """The last rule's unknown name is 4.7b in both engines; Python types each rule once."""
    raw, norms = many_rules(*norms_base())
    norms[-1]["norm"]["guard"] = ["unary", "nope", ["var", 0]]
    [row] = lean_routes.diagnose("norms@0", [{"id": "c", "kind": "norms-elaborate", "environment": raw, "norms": norms}])
    typed = counting(monkeypatch, norms_contract._Checker, "formula")
    outcome = run(load("norms@0"), {"environment": deepcopy(raw), "norms": deepcopy(norms)},
                  registry=norms_contract.REGISTRY)
    assert (outcome.record["check"], outcome.record["path"]) == ("4.7b", f"/norms/{RULES - 1}")
    assert (row["diagnostic"]["check"], row["diagnostic"]["path"]) == ("4.7b", f"/norms/{RULES - 1}")
    assert len(typed) < 4 * RULES  # each rule's guard once (its nodes' recursion included), not once per later rule


def test_soft_rule_typing_reads_the_declarations_once_per_run(monkeypatch):
    """5.7 and 5.8 at each of several rules read one decode of the declarations."""
    source = json.loads((ROOT / "ve/wire_contract/examples/soft-norms@0/default-rule.json").read_text())
    [first] = source["norms"]
    norms = [{"norm": {**deepcopy(first["norm"]), "name": f"a{i}"}} for i in range(8)]
    declarations = counting(monkeypatch, softnorms_legacy, "_declarations")
    assert run(load("soft-norms@0"), {"environment": deepcopy(source["environment"]), "norms": norms},
               registry=SOFT) is CLEAN
    assert len(declarations) == 1
