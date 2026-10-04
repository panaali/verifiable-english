"""The cross-language differential fuzzer (tools/difffuzz.py, conformance/DIFFFUZZ.md).

`test_ci_run` is the suite's run of `--ci`: no new disagreement, and every baseline entry still reproduces.
The tests after it show that the run can fail. Each seeded mutant of the comparison, such as ignoring texts or
dropping Lean, makes the CI verdict fail on the baseline alone, and so does a deliberately changed Python
diagnostic on the P0 sample.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import sys

import pytest

from tools import difffuzz as df

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def built():
    for name in ("ve_conformance", "ve_diagnose", "ve_service", *(b for b, _ in df.ROUTE_CASES.values())):
        assert (df.BIN / name).exists(), f"build {name} (lake build) before the fuzzer runs"
    assert df.rust_binary().exists(), "build the Rust release binary before the fuzzer runs"


def _summary(report):
    return json.dumps({"new": [{k: e[k] for k in ("surface", "profile", "classes", "input", "answers")}
                               for e in report["new"]][:5],
                       "baseline": report["baseline"]}, indent=1, ensure_ascii=False)[:6000]


def test_ci_run(built):
    """`difffuzz.py --ci`: the seeded sample of every surface, compared three ways, within 5 minutes of CPU."""
    report = df.fuzz()
    assert report["new"] == [], _summary(report)
    assert report["baseline"]["not_reproduced"] == [], _summary(report)
    assert report["baseline"]["unreviewed"] == [], _summary(report)
    assert report["passed"]
    for name, (ones, twos) in df.CI_BUDGET.items():
        assert report["mutants"][name] == {"one-fault": ones, "two-fault": twos}, name
        assert sum(report["corpus"][name].values()) > 0, name
    # Every implementation really ran: each answered mutants both ways on every surface it has a path for.
    for name, engines in (("p0", df.ENGINES), ("environment", df.ENGINES), ("wire", ("python", "lean"))):
        for engine in engines:
            for outcome in ("ok", "error"):
                assert report["answers"][name].get(f"{engine}:{outcome}", 0) > 0, (name, engine, outcome)
    assert sum(report["cpu_seconds"].values()) <= 300, report["cpu_seconds"]


# ---------------------------------------------------------------- the comparison can fail

def _ignore_texts(monkeypatch):
    for surface in df.SURFACES.values():
        monkeypatch.setattr(surface, "text_fixed", lambda self, seed, left, right: False)


def _ignore_codes(monkeypatch):
    compare = df.compare

    def without_codes(surface, seed, left, right):
        return compare(surface, seed, (left[0], {**left[1], "code": None}), (right[0], {**right[1], "code": None}))
    monkeypatch.setattr(df, "compare", without_codes)


def _crash_is_a_diagnostic(monkeypatch):
    call = df.call_python

    def calm(function, harness):
        answer = call(function, harness)
        return df.error("InvalidInput", answer["text"]) if answer.get("outcome") == "crash" else answer
    monkeypatch.setattr(df, "call_python", calm)


def _agree_on_outcome_only(monkeypatch):
    compare = df.compare
    monkeypatch.setattr(df, "compare", lambda surface, seed, left, right:
                        compare(surface, seed, left, right) & {"outcome"})


COMPARISON_MUTANTS = {
    "ignore texts": _ignore_texts,
    "ignore codes": _ignore_codes,
    "drop Lean": lambda monkeypatch: monkeypatch.setattr(df, "ENGINES", ("python", "rust")),
    "drop Rust": lambda monkeypatch: monkeypatch.setattr(df, "ENGINES", ("python", "lean")),
    "crash counted as a diagnostic": _crash_is_a_diagnostic,
    "accept/reject only": _agree_on_outcome_only,
    "every engine says the same": lambda monkeypatch: monkeypatch.setattr(
        df, "classes", lambda surface, seed, answers, root: ([], {})),
    "Lean always accepts": lambda monkeypatch: [
        monkeypatch.setattr(surface, "lean", lambda self, items: [df.ok() for _ in items])
        for surface in df.SURFACES.values()],
    "Lean always rejects": lambda monkeypatch: [
        monkeypatch.setattr(surface, "lean", lambda self, items: [df.error("InvalidInput", "") for _ in items])
        for surface in df.SURFACES.values()],
}


def test_the_baseline_alone_passes(built):
    """The control of the mutants below: replaying the baseline, with no sample, passes."""
    report = df.fuzz(scale=0)
    assert report["passed"], _summary(report)


@pytest.mark.parametrize("mutant", sorted(COMPARISON_MUTANTS))
def test_a_weakened_comparison_fails_the_ci_verdict(built, monkeypatch, mutant):
    COMPARISON_MUTANTS[mutant](monkeypatch)
    report = df.fuzz(scale=0)
    assert not report["passed"], mutant
    assert report["baseline"]["not_reproduced"], mutant


def _label_text(monkeypatch):
    from ve import admission

    def changed(s):
        if admission.parse_label(s) is None:
            raise admission.AdmissionError(f"AdmissionError: label {s} is invalid")
        return s
    monkeypatch.setattr(admission, "_validate_label_python", changed)


def _label_code(monkeypatch):
    from ve import admission
    from ve.errors import UnsupportedProfile

    def changed(s):
        # The P0 contract reads a code from its text's head (`three_way.error_verdict`).
        if admission.parse_label(s) is None:
            raise UnsupportedProfile(f"UnsupportedProfile: invalid label {s}")
        return s
    monkeypatch.setattr(admission, "_validate_label_python", changed)


@pytest.mark.parametrize("change", [_label_text, _label_code], ids=["text", "code"])
def test_a_changed_python_diagnostic_is_caught(built, monkeypatch, change):
    """A Python diagnostic that Lean and Rust agree with today (the invalid-label text, then its code) is
    changed in process: the P0 sample reports it as a new disagreement, minimised to a label case."""
    change(monkeypatch)
    monkeypatch.setattr(df, "MINIMISE_EVALUATIONS", 400)
    monkeypatch.setattr(df, "CI_BUDGET", {**df.CI_BUDGET, "p0": (3000, 0)})
    report = df.fuzz(surfaces=["p0"])
    assert not report["passed"]
    labels = [e for e in report["new"] if e["profile"] == "labels:label"]
    assert labels, _summary(report)
    assert any(e["answers"]["python"].get("code") != e["answers"]["lean"].get("code") or
               e["answers"]["python"].get("text") != e["answers"]["lean"].get("text") for e in labels)


# ---------------------------------------------------------------- the pieces

def test_mutations():
    root = {"name": "Kit 12", "list": [1, 2], "obj": {"a": 1, "b": 2}}
    assert df.apply(root, ["type", ["name"], "null"]) == {**root, "name": None}
    assert df.apply(root, ["type", ["list"], "array"]) == {**root, "list": []}
    assert df.apply(root, ["type", ["obj", "a"], "number"]) == {**root, "obj": {"a": 7, "b": 2}}
    assert df.apply(root, ["absent", ["obj", "a"], None]) == {**root, "obj": {"b": 2}}
    assert list(df.apply(root, ["reorder", ["obj"], None])["obj"]) == ["b", "a"]
    assert df.apply(root, ["reorder", ["list"], None])["list"] == [2, 1]
    assert df.apply(root, ["duplicate", ["list"], None])["list"] == [1, 1, 2]
    variants = {name: df.apply(root, ["unicode", ["name"], name])["name"] for name in df.UNICODE}
    assert variants == {"nbsp": "Kit\u00a012", "double-space": "Kit  12", "tab": "Kit\t12",
                        "cr": "Kit 12\r", "kelvin": "\u212ait 12", "dotted-i": "K\u0130t 12",
                        "upper": "KIT 12", "digits": "Kit \u0661\u0662", "curly-quote": "Kit 12\u2019",
                        "control": "Kit 12\x1c"}
    assert df.apply({"s": "it's"}, ["unicode", ["s"], "curly-quote"]) == {"s": "it\u2019s"}
    assert list(df.apply(root, ["key", ["obj", "a"], "upper"])["obj"]) == ["A", "b"]
    assert df.apply(root, ["limit", ["list"], 3])["list"] == [1, 2, 1]
    assert df.apply(root, ["limit", ["name"], 3])["name"] == "Kit"
    # A mutation that changes nothing does not apply.
    assert df.apply({"n": 7}, ["type", ["n"], "number"]) is None
    assert df.apply({"s": "abc"}, ["unicode", ["s"], "kelvin"]) is None
    assert df.apply({"l": [1, 1]}, ["reorder", ["l"], None]) is None
    every = df.one_faults(root, (), [])
    # Every listed mutation changes the input (key order included).
    assert all(json.dumps(df.apply(root, m)) not in ("null", json.dumps(root)) for m in every)
    assert {m[0] for m in every} == {"type", "absent", "key", "reorder", "duplicate", "unicode"}


def test_limits_come_from_the_wire_contract_tables():
    production = json.loads((ROOT / "ve/wire_contract/limits.json").read_text())
    found = {(unit, "/".join(pattern), kind, limit) for unit, pattern, kind, limit in df.limit_patterns()}
    assert (None, "norms", "max_items", production["MAX_RULES"]) in found
    assert (None, "environment/vocabulary/soft/parties", "max_items", production["MAX_SOFT_PARTIES"]) in found
    assert (None, "environment/vocabulary/soft/ranks", "max_items", production["MAX_SOFT_RANKS"]) in found
    assert (None, "norms/*/norm/exception/factors/*", "max_bytes", production["MAX_FACTOR_BYTES"]) in found
    assert ("demo@0", "doc/items", "max_items", 3) in found
    # The environment surface sees the soft block's limits at its root; P0 cases under `environment`.
    env, p0 = df.EnvironmentSurface(), df.P0()
    seed = df.Seed("environment", "envelope", "x", {})
    assert (("vocabulary", "soft", "parties"), "max_items", production["MAX_SOFT_PARTIES"]) in env.limits(seed)
    assert (("environment", "vocabulary", "soft", "parties"), "max_items",
            production["MAX_SOFT_PARTIES"]) in p0.limits(seed)
    parties = {"vocabulary": {"soft": {"parties": ["a", "b"]}}}
    sizes = {len(df.apply(parties, m)["vocabulary"]["soft"]["parties"])
             for m in df.one_faults(parties, (), env.limits(seed)) if m[0] == "limit"}
    limit = production["MAX_SOFT_PARTIES"]
    assert sizes == {limit - 1, limit, limit + 1}


def test_templates_keep_the_wording_and_drop_the_values():
    forms = df.input_forms({"constants": {"alice": {"sort": "Person!"}}})
    # A field name in the wording is replaced too, the same way wherever the input has the field.
    assert df.template("Undeclared constant sort: 'Person!' of alice at 12", forms) == \
        "Undeclared constant <v>: <v> of <v> at #"
    assert df.template({"text": "a b"}, forms) == {"text": "a b"}


class Toy(df.Surface):
    """Python rejects any object with a member `bad`; Lean rejects it only when `bad` is 1."""
    name = "toy"

    def python(self, seed, root):
        return df.error("InvalidInput", "bad") if "bad" in json.dumps(root) else df.ok()

    def lean(self, items):
        return [df.error("InvalidInput", "bad") if '"bad": 1' in json.dumps(root) else df.ok()
                for _, root in items]

    def text_fixed(self, seed, left, right):
        return True


def test_the_minimiser_keeps_the_signature_and_drops_the_rest():
    seed = df.Seed("toy", "toy", "toy", None, ("python", "lean"))
    root = {"keep": {"deep": [1, 2, 3], "x": "long text"}, "other": [{"bad": 2}, {"y": 1}], "z": "zz"}
    [(found, _, _, signature)] = df.evaluate(Toy(), [(seed, root)])
    assert found == ["outcome"]
    assert df.minimise(Toy(), seed, root, signature) == {"other": [{"bad": 2}]}


def test_a_runner_that_does_not_answer_is_found_by_bisection(tmp_path):
    script = tmp_path / "runner.py"
    script.write_text(
        "import json, sys\n"
        "cases = json.load(sys.stdin)\n"
        "if any(c.get('boom') for c in cases): sys.exit(134)\n"
        "if any(c.get('frame') for c in cases): sys.exit(2)\n"
        "print(json.dumps([{'id': c['id'], 'status': 'ok'} for c in cases]))\n")
    cases = [{"id": str(i)} for i in range(9)]
    cases[3]["boom"] = True
    cases[6]["frame"] = True
    rows = df.run_rows([sys.executable, script], cases)
    assert [sorted(row) for row in rows] == [["id", "status"]] * 3 + [["panic"]] + [["id", "status"]] * 2 + \
        [["framing"]] + [["id", "status"]] * 2
    assert df.panic(rows[3])["outcome"] == "panic"
    assert df.panic(rows[6]) == df.error("framing", "")


def test_only_veerror_is_a_python_answer():
    from ve.errors import UnsupportedProfile

    def raises(exc):
        def call():
            raise exc
        return call
    assert df.call_python(raises(UnsupportedProfile("no")), frozenset())["code"] == "UnsupportedProfile"
    assert df.call_python(raises(TypeError("x")), frozenset())["outcome"] == "crash"
    # The fuzzer's own adapter reading a field that is not there is no answer.
    assert df.call_python(lambda: {}["missing"], frozenset({"test_difffuzz.py"})) == df.NOT_APPLICABLE


def test_off_wire_inputs_reach_python_only():
    assert df.on_wire({"a": [1, "b"]})
    assert not df.on_wire({"a": None})


# ---------------------------------------------------------------- every registered item is covered

def test_every_p0_family_is_fuzzed_or_excluded_with_a_reason():
    from conformance.p0 import FAMILIES
    excluded = {"vacuity"}  # its Python adapter asserts its own witness (DIFFFUZZ.md, Surfaces)
    assert set(df.P0_FAMILIES) | excluded == set(FAMILIES)
    assert not set(df.P0_FAMILIES) & excluded


def test_every_route_is_a_built_lean_executable():
    from tools.layer_policy import lean_executables
    executables = lean_executables()
    for route, (binary, case) in df.ROUTE_CASES.items():
        assert binary in executables, route
        assert "kind" in case, route
    routes = {df.lean_route(data) for data in (
        {"language": "ve.core@0"}, {"profiles": ["risk@0"]}, {"profiles": ["alternatives@0"]},
        {"profiles": ["speech-acts@0"]}, {"profiles": ["reports@0"]}, {"profiles": ["soft-norms@0"]},
        {"profiles": [], "units": {}})}
    assert routes == set(df.ROUTE_CASES) | {"envelope"}


def test_every_wire_unit_is_fuzzed_or_included(built):
    from tests.test_wire_contract_corpus import CONTRACTS
    units = set(CONTRACTS) | {"soft-norms@0"}
    included = {"inner@0", "mid@0"}  # reached only through the includes of forms@0 (and Lean's own unit tests)
    seeded = {seed.profile for seed in df.Wire().seeds()}
    assert seeded | included == units
    for unit in units:
        done, _ = df.run_cpu_bounded([str(df.BIN / "ve_diagnose"), unit, "-"], "[]", df.BATCH_CPU, env=df.CHILD_ENV)
        assert done.returncode == 0, (unit, done.stderr)


def test_every_follow_up_is_documented_and_used():
    documented = set(re.findall(r"^\| (DF-\d+) \|", (ROOT / "conformance/DIFFFUZZ.md").read_text(), re.M))
    baseline = df.load_baseline()
    used = {entry["follow_up"] for entry in baseline["entries"]}
    assert used == documented
    assert df.baseline_problems(baseline) == []


def test_baseline_entries_are_well_formed():
    baseline = df.load_baseline()
    signatures = [entry["signature"] for entry in baseline["entries"]]
    assert len(signatures) == len(set(signatures))
    for entry in baseline["entries"]:
        assert entry["surface"] in df.SURFACES
        assert set(entry["engines"]) <= set(df.ENGINES) and "python" in entry["engines"]
        assert entry["classes"] and set(entry["classes"]) <= {
            "python-crash", "no-answer", "outcome", "code", "diagnostic", "value"}
        assert set(entry["answers"]) <= set(entry["engines"])
        assert all(type(m) is list and len(m) == 3 for m in entry["mutation"])


def test_an_unreviewed_entry_fails(tmp_path):
    baseline = df.load_baseline()
    entry = deepcopy(baseline["entries"][0])
    entry["follow_up"] = "TODO"
    assert df.baseline_problems({"format": df.FORMAT, "entries": [entry]}) == [f"{entry['id']}: no follow-up id"]
