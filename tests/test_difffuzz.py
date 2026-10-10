"""The cross-language differential fuzzer (tools/difffuzz.py, conformance/DIFFFUZZ.md).

`test_ci_run` is the suite's run of `--ci`: no new disagreement, and every baseline entry still reproduces.
The tests after it show that the run can fail. Each seeded mutant of the comparison, such as ignoring texts,
dropping Lean or reducing codes to the P0 contract's, makes the CI verdict fail on the baseline alone, and so
does a deliberately changed Python diagnostic. Then the regressions of the difffuzz review, one per class:
diagnostic codes are each implementation's own; an input off the restricted wire and a Python call that does
not finish are compared, not dropped; every fixture is read or excluded with a reason and every engine with a
path answers every seed; every runner row is checked against its producer's schema, and each field of a
genuine row dropped or retyped is a runner that did not answer.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import sys

import pytest

from tools import difffuzz as df
from tools import difffuzz_corpus as corpus
from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
# The one-shot routes and `ve_diagnose` are service modes since lean-first batch 1 (`df.SERVICE_MODES`).
LEAN_BINARIES = ("ve_conformance", "ve_service")


@pytest.fixture(scope="module")
def built():
    for name in LEAN_BINARIES:
        assert (df.BIN / name).exists(), f"build {name} (lake build) before the fuzzer runs"
    assert df.rust_binary().exists(), "build the Rust release binary before the fuzzer runs"


def _summary(report):
    return json.dumps({"new": [{k: e[k] for k in ("surface", "profile", "classes", "input", "answers")}
                               for e in report["new"]][:5],
                       "baseline": report["baseline"]}, indent=1, ensure_ascii=False)[:6000]


def test_ci_run(built, tmp_path):
    """`difffuzz.py --ci`: every seed and the seeded sample of every surface, compared three ways, within 5
    minutes of CPU. Run the meter in its own process so other pytest worker work cannot enter its CPU total."""
    output = tmp_path / "difffuzz-ci.json"
    completed = subprocess.run([sys.executable, "-m", "tools.difffuzz", "--ci", "--report", str(output)],
                               cwd=ROOT, capture_output=True, text=True, timeout=HANG_TIMEOUT)
    assert output.is_file(), completed.stderr[-2000:]
    report = json.loads(output.read_text())
    assert completed.returncode == 0, _summary(report)
    assert report["new"] == [], _summary(report)
    assert report["baseline"]["not_reproduced"] == [], _summary(report)
    assert report["baseline"]["unreviewed"] == [], _summary(report)
    assert report["passed"]
    for name, (ones, twos) in df.CI_BUDGET.items():
        seeds = sum(report["corpus"][name].values())
        assert seeds > 0, name
        assert report["mutants"][name] == {"zero-fault": seeds, "one-fault": ones, "two-fault": twos}, name
    # Every implementation really ran: each answered inputs both ways on every surface it has a path for.
    for name, engines in (("requests", df.ENGINES), ("environment", df.ENGINES), ("wire", ("python", "lean")),
                          ("document", ("python", "lean"))):
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


def _p0_codes_only(monkeypatch):
    """The review's B1: every code outside the P0 contract's `KNOWN` read as `rejected`."""
    verdict = df.Requests._verdict

    def reduced(self, seed, answer):
        if answer.get("status") == "error":
            answer = {**answer, "diagnostic_code": answer["code"]}
        return verdict(self, seed, answer)
    monkeypatch.setattr(df.Requests, "_verdict", reduced)


def _off_wire_dropped(monkeypatch):
    """The review's B2: an input off the restricted wire shown to Python alone."""
    answers = df.Surface.answers

    def dropped(self, items):
        out = answers(self, items)
        for (_, root), row in zip(items, out):
            if not df.on_wire(root):
                row.update({engine: df.NOT_APPLICABLE for engine in row if engine != "python"})
        return out
    monkeypatch.setattr(df.Surface, "answers", dropped)


def _rejecting_engine_removed(monkeypatch):
    """The review's B3: an engine that rejects an environment seed takes no part on it."""
    path = df.EnvironmentSurface.path

    def removed(self, engine, seed, root):
        return path(self, engine, seed, root) and not (engine != "python" and seed.profile in (
            "norm-defaults", "quantity", "soft-norms"))
    monkeypatch.setattr(df.EnvironmentSurface, "path", removed)


COMPARISON_MUTANTS = {
    "ignore texts": _ignore_texts,
    "ignore codes": _ignore_codes,
    "codes reduced to the P0 contract": _p0_codes_only,
    "off-wire inputs reach Python only": _off_wire_dropped,
    "an engine rejecting a seed is removed": _rejecting_engine_removed,
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


def _wrong_document_lean(mutant):
    lean = df.DocumentSurface.lean

    def wrong(self, items):
        out = lean(self, items)
        if mutant == "always accepts":
            return [df.ok(None) for _ in out]
        if mutant == "always rejects":
            return [df.error("InvalidInput", "rejected") for _ in out]
        if mutant == "always unavailable":
            return [df.error("CheckerUnavailable", "CheckerUnavailable: no") for _ in out]
        for answer in out:  # "bridge leaves uncounted"
            if answer["outcome"] == "ok":
                answer["value"]["coverage"]["residual"]["bridge_leaves"] = 0
        return out
    return wrong


@pytest.mark.parametrize("mutant", ["always accepts", "always rejects", "bridge leaves uncounted"])
def test_a_wrong_document_mode_is_a_finding(built, monkeypatch, tmp_path, mutant):
    """The `document` surface compares values and texts: a Lean mode that accepts everything, rejects everything
    or counts no bridge leaf disagrees with Python on its seeds (16a review B4)."""
    monkeypatch.setitem(df.CI_BUDGET, "document", (20, 5))
    monkeypatch.setattr(df, "MINIMISE_LIMIT", 0)  # a finding is enough; minimising it is not the point here
    monkeypatch.setattr(df.DocumentSurface, "lean", _wrong_document_lean(mutant))
    report = df.fuzz(surfaces=["document"], baseline_path=tmp_path / "baseline.json")
    assert report["new"] and not report["passed"], mutant


def test_a_document_mode_that_always_fails_closed_decides_no_seed(built, monkeypatch):
    """`CheckerUnavailable` agrees with any answer, so the comparison alone cannot see a mode that always
    refuses; the seed test does (`test_lean_document_wrapper.DECIDED`): every one of those seeds must agree."""
    from conformance import document_wrapper as dw
    from tests.test_lean_document_wrapper import DECIDED
    seeds = [(name, doc) for name, doc in dw.seeds() if name in DECIDED]
    answers = _wrong_document_lean("always unavailable")(df.DocumentSurface(), [(None, doc) for _, doc in seeds])
    verdicts = {dw.verdict(dw.python_answer(dw.text_of(doc)), answer) for (_, doc), answer in zip(seeds, answers)}
    assert verdicts == {"fail-closed"}  # what the seed test rejects: it requires "agree" on each


def test_the_baseline_alone_passes(built):
    """The control of the mutants below: replaying the baseline, with no sample, passes."""
    report = df.fuzz(scale=0)
    assert report["passed"], _summary(report)


def _crash_baseline(monkeypatch, tmp_path):
    """A baseline of one environment entry whose Python call crashes, with Python made to crash on that input
    alone. The real baseline holds no crash since the merge with `fix/env-field-types` fixed DF-2 (Python's
    `TypeError` on a malformed definition body), so the crash mutant needs one of its own."""
    entry = deepcopy(next(e for e in df.load_baseline()["entries"] if e["surface"] == "environment"))
    python = df.EnvironmentSurface.python

    def crash():
        raise TypeError("injected")

    def crashing(self, seed, root):
        return df.call_python(crash, self.harness) if root == entry["input"] else python(self, seed, root)
    monkeypatch.setattr(df.EnvironmentSurface, "python", crashing)
    surface = df.EnvironmentSurface()
    try:
        [(found, _, answers, signature)] = df.evaluate(surface, [(df.seed_of(entry), entry["input"])])
    finally:
        surface.close()
    assert "python-crash" in found, found
    entry.update(classes=found, answers=answers, signature=signature)
    path = tmp_path / "baseline.json"
    path.write_text(json.dumps({"format": df.FORMAT, "entries": [entry]}))
    return path


@pytest.mark.parametrize("mutant", sorted(COMPARISON_MUTANTS))
def test_a_weakened_comparison_fails_the_ci_verdict(built, monkeypatch, tmp_path, mutant):
    path = df.BASELINE
    if mutant == "crash counted as a diagnostic":
        path = _crash_baseline(monkeypatch, tmp_path)
        assert df.fuzz(scale=0, baseline_path=path)["passed"]
    COMPARISON_MUTANTS[mutant](monkeypatch)
    report = df.fuzz(scale=0, baseline_path=path)
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


def _labels_only(monkeypatch):
    seeds = df.Requests.seeds
    monkeypatch.setattr(df.Requests, "seeds", lambda self: [s for s in seeds(self) if s.profile == "labels:label"])


@pytest.mark.parametrize("change", [_label_text, _label_code], ids=["text", "code"])
def test_a_changed_python_diagnostic_is_caught(built, monkeypatch, change):
    """A Python diagnostic that Lean and Rust agree with today (the invalid-label text, then its code) is
    changed in process: the request sample reports it as a new disagreement, minimised to a label case."""
    change(monkeypatch)
    _labels_only(monkeypatch)
    monkeypatch.setattr(df, "MINIMISE_EVALUATIONS", 400)
    monkeypatch.setattr(df, "CI_BUDGET", {**df.CI_BUDGET, "requests": (1500, 0)})
    report = df.fuzz(surfaces=["requests"])
    assert not report["passed"]
    labels = [e for e in report["new"] if e["profile"] == "labels:label"]
    assert labels, _summary(report)
    assert any(e["answers"]["python"].get("code") != e["answers"]["lean"].get("code") or
               e["answers"]["python"].get("text") != e["answers"]["lean"].get("text") for e in labels)


# ---------------------------------------------------------------- B1: each implementation's own code

def _request_seed(origin):
    return next(s for s in df.Requests().seeds() if s.id == origin)


def test_a_python_code_outside_the_p0_contract_is_compared(built, monkeypatch):
    """The review's reproducer: on `literals-distinct` with constant `alpha` replaced by "x", Python says
    `UnknownSymbol`; deliberately changing that code to `SyntaxError` is a finding (the P0 contract would
    read both as `rejected`)."""
    from ve import errors
    seed = _request_seed("conformance/elaborated-document.json/0")
    assert seed.meta["kind"] == "evaluate" and df.get(seed.root, ["ast", 0, 1, 1]) == ["const", "alpha"]
    root = df.apply(seed.root, ["type", ["ast", 0, 1, 1, 1], "string"])
    surface = df.Requests()
    [(before, _, answers, signature)] = df.evaluate(surface, [(seed, root)])
    assert answers["python"]["code"] == "UnknownSymbol", answers
    monkeypatch.setattr(errors.UnknownSymbol, "code", "SyntaxError")
    [(after, _, changed, changed_signature)] = df.evaluate(surface, [(seed, root)])
    assert changed["python"]["code"] == "SyntaxError"
    assert "code" in after and changed_signature != signature, (before, after, changed)


def test_error_verdicts_keep_each_implementations_code():
    from conformance.three_way import error_verdict
    python = error_verdict("UnknownSymbol", "Undeclared constant 'x'")
    lean = error_verdict(None, "fields do not match: expected [a], got [b]")
    rust = error_verdict("SyntaxError", "premises must be an array")
    assert (python["code"], python["diagnostic_code"]) == ("rejected", "UnknownSymbol")
    assert (lean["code"], lean["diagnostic_code"]) == ("rejected", "InvalidInput")
    assert (rust["code"], rust["diagnostic_code"]) == ("rejected", "SyntaxError")
    assert error_verdict(None, "UnsupportedProfile: Unsupported language")["diagnostic_code"] == "UnsupportedProfile"


def _soft_reproducer():
    """The recheck's B1 reproducer: a soft-norms environment with `vocabulary.predicates: 7`, which the
    soft-norms route rejects with its own code `SOFT_INVALID_INPUT`. (B1's `vocabulary: 7` now gets Python's
    decoder type diagnostic, so its text is compared too: DF-13. The nested field still gets neither.)"""
    surface = df.EnvironmentSurface()
    seed = next(s for s in surface.seeds() if s.profile == "soft-norms")
    root = df.apply(seed.root, ["type", ["vocabulary", "predicates"], "number"])
    return surface, df.Seed("environment", "soft-norms", seed.id, root), root


def _with_lean_row(surface, seed, root, change):
    """The finding classes and projection of `root` when the Lean route's genuine row is changed by
    `change`; Python answers as it does."""
    answers, [(case, row)] = _genuine(surface, "lean", [seed])
    changed = deepcopy(row)
    change(changed)
    [lean] = _replay_rows(surface, "lean", [seed], [changed])
    live = {"python": surface.python(seed, root), "lean": lean, "rust": df.NOT_APPLICABLE}
    return row, lean, df.classes(surface, seed, live, root)


def test_a_routes_own_code_is_kept_compared_and_checked(built):
    """The environment surface compares the composed service diagnostic, not a nested route code."""
    surface, seed, root = _soft_reproducer()
    row, lean, (found, _) = _with_lean_row(surface, seed, root, lambda row: None)
    assert row["status"] == "error" and row["error"].startswith("InvalidInput:"), row
    assert lean["code"] == surface.python(seed, root)["code"] == "InvalidInput" and found == []
    _, lean, (found, projected) = _with_lean_row(
        surface, seed, root, lambda row: row.update(error="UnsupportedProfile: different refusal"))
    assert found == ["code"], (found, lean)
    assert (projected["python"]["code"], projected["lean"]["code"]) == ("InvalidInput", "UnsupportedProfile")
    for change in (lambda row: row.pop("error"), lambda row: row.update(error=7),
                   lambda row: row.update(code="SOFT_NOT_A_CODE")):
        _, lean, (found, _) = _with_lean_row(surface, seed, root, change)
        assert lean["outcome"] == "panic" and found == ["no-answer"], (lean, found)
    surface.close()


def test_the_compared_code_of_an_own_code_is_its_contract_class(built):
    """The service's public diagnostic prefix supplies the compared code."""
    surface, seed, root = _soft_reproducer()
    for code in ("UnsupportedProfile", "DuplicateDeclaration", "UnknownSymbol"):
        _, lean, _ = _with_lean_row(surface, seed, root,
                                   lambda row: row.update(error=f"{code}: different refusal"))
        assert lean["code"] == code
    surface.close()


def test_every_own_code_route_has_a_python_counterpart_that_agrees_on_its_seeds(built):
    """The composed environment service and public Python constructor agree on soft-norms seeds."""
    surface = df.EnvironmentSurface()
    owned = [name for name, route in df.ROUTES.items() if route.own]
    assert owned == ["soft-norms"]
    seeds = [s for s in surface.seeds() if s.profile in owned]
    try:
        rows = df.evaluate(surface, [(seed, seed.root) for seed in seeds])
    finally:
        surface.close()
    for seed, (_, _, answers, _) in zip(seeds, rows):
        assert (answers["python"]["outcome"], answers["python"].get("code"), answers["python"].get("text")) == (
            answers["lean"]["outcome"], answers["lean"].get("code"), answers["lean"].get("text")), (seed.id, answers)


# ---------------------------------------------------------------- B2: missing answers are findings

def test_python_accepting_an_off_wire_input_is_a_finding(built, monkeypatch):
    """A lower Python decoder mutation cannot bypass Lean's authored-model preflight."""
    from ve.model import FiniteModel
    seed = _request_seed("conformance/elaborated-document.json/0")
    original = FiniteModel._decode.__func__

    def accepting(cls, env, wire, *args, **kwargs):
        return original(cls, env, deepcopy(seed.root["model"]) if wire is None else wire, *args, **kwargs)
    root = df.apply(seed.root, ["type", ["model"], "null"])
    [(found, _, answers, _)] = df.evaluate(df.Requests(), [(seed, root)])
    assert answers["lean"]["code"] == answers["rust"]["code"] == df.FRAMING
    assert answers["python"]["outcome"] == "error" and found == [], answers
    monkeypatch.setattr(FiniteModel, "_decode", classmethod(accepting))
    [(found, _, answers, _)] = df.evaluate(df.Requests(), [(seed, root)])
    assert answers["python"]["outcome"] == "error" and found == [], answers


@pytest.mark.parametrize("command", [
    ["ve_conformance", "route", "-"], ["ve_conformance", "-"], ["ve_conformance", "check-certificate", "-"],
    ["ve_diagnose", "demo@0", "-"], *[[route.lean, "-"] for route in df.ROUTES.values() if route.case],
    ["rust", "conformance"]], ids=lambda command: " ".join(command[:2]))
def test_every_runner_refuses_an_off_wire_package(built, command):
    """The fuzzer's `framing` answer for an input off the restricted wire is what every runner does with it:
    it refuses the package (exit 2). The service is not run: its client refuses the input before sending."""
    executable = df.rust_binary() if command[0] == "rust" else df.BIN / command[0]
    for case in ({"id": "0", "kind": "evaluate", "environment": None}, {"id": "0", "model": 1.5}):
        assert not df.on_wire(case)
        [row] = df.run_rows([executable, *command[1:]], [case])
        assert type(row) is df.Refused, (command, row)


def test_a_python_timeout_is_a_finding(monkeypatch):
    def spin():
        while True:
            pass
    monkeypatch.setattr(df, "PYTHON_CPU", 0.2)
    assert df.call_python(spin, frozenset()) == {"outcome": "timeout"}
    seed = df.Seed("toy", "toy", "toy", None, ("python", "lean"))
    found, projected = df.classes(Toy(), seed, {"python": {"outcome": "timeout"}, "lean": df.ok()}, {})
    assert found == ["timeout"] and projected["python"] == {"outcome": "timeout"}


def test_off_wire_inputs_get_the_package_refusal():
    assert df.on_wire({"a": [1, "b"]})
    assert not df.on_wire({"a": None}) and not df.on_wire({"a": 1.5})
    seed = df.Seed("toy", "toy", "toy", None, ("python", "lean"))
    [answers] = Toy().answers([(seed, {"bad": None})])
    assert answers["lean"] == df.refusal(df.off_wire({"bad": None}))
    # A refusal agrees with a rejection and disagrees with an acceptance.
    assert df.classes(Toy(), seed, answers, {"bad": None})[0] == []
    assert df.classes(Toy(), seed, {**answers, "python": df.ok()}, {"bad": None})[0] == ["outcome"]


def test_a_runner_code_named_framing_is_a_code_not_a_refusal():
    """Only the fuzzer makes a refusal (`refusal`): a runner whose own error code is `framing` gives a code,
    compared like any other."""
    seed = df.Seed("toy", "toy", "toy", None, ("python", "lean"))
    answers = {"python": df.error("InvalidInput", "bad"), "lean": df.error(df.FRAMING, "bad")}
    assert df.classes(Toy(), seed, answers, {})[0] == ["code"]
    assert df.classes(Toy(), seed, {**answers, "lean": df.refusal("bad")}, {})[0] == []


# ---------------------------------------------------------------- recheck B4 and B: transport is not a row

def _fake_runner(monkeypatch, answer):
    """Every runner batch answered by `answer(cases)`: (returncode, stdout), or an exception to raise."""
    import subprocess

    def run(command, stdin, cpu_seconds, env=None):
        result = answer(json.loads(stdin))
        if isinstance(result, BaseException):
            raise result
        returncode, stdout = result
        return subprocess.CompletedProcess(command, returncode, stdout, ""), 0.0
    monkeypatch.setattr(df, "run_cpu_bounded", run)
    # A route's batch is the fake's too, read as a runner's output (not the service's).
    monkeypatch.setattr(df, "SERVICE_MODES", {})


def _invalid_label():
    """An invalid-label request (`labels:label` with the label replaced by "x"), which Python rejects."""
    seed = next(s for s in df.Requests().seeds() if s.profile == "labels:label")
    return seed, df.apply(seed.root, ["type", ["label"], "string"])


def _request_classes(seed, root):
    surface = df.Requests()
    [lean] = surface.lean([(seed, root)])
    answers = {"python": surface.python(seed, root), "lean": lean, "rust": df.NOT_APPLICABLE}
    return lean, df.classes(surface, seed, answers, root)[0]


def test_a_printed_framing_member_is_a_malformed_row_not_a_refusal(monkeypatch):
    """The recheck's B4 reproducer: a runner that exits 0 and prints `[{"id": "0", "framing": "oops"}]` for an
    invalid-label request once read as the fuzzer's own package refusal, which agrees with Python's
    rejection (no finding). It is a row, and a malformed one: no answer."""
    seed, root = _invalid_label()
    assert df.Requests().python(seed, root)["outcome"] == "error"
    for printed in ({"framing": "oops"}, {"panic": "oops"}, {"framing": "oops", "status": "error", "error": "x"}):
        _fake_runner(monkeypatch, lambda cases: (
            1 if "status" in printed else 0, json.dumps([{"id": c["id"], **printed} for c in cases])))
        [row] = df.run_rows(["runner"], [{"id": "0"}])
        assert type(row) is dict and df.panic(row) is None
        lean, found = _request_classes(seed, root)
        assert lean["outcome"] == "panic" and found == ["no-answer"], (printed, lean, found)


@pytest.mark.parametrize("failure", ["timeout", "cannot start", "not text", "too deep"])
def test_a_runner_that_fails_in_transport_is_isolated_and_does_not_answer(monkeypatch, failure):
    """The recheck's B: a runner that does not finish within HANG_TIMEOUT raised `TimeoutExpired` out of the
    fuzzer. Every transport failure (a hang, a runner that cannot start, output that is not UTF-8, output
    nested too deep to decode) is the case's runner not answering: the batch is split until that case is
    alone, the others answer, and the case is a `no-answer` finding."""
    import subprocess
    raised = {"timeout": subprocess.TimeoutExpired(["runner"], 1), "cannot start": FileNotFoundError(2, "absent"),
              "not text": UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")}

    def answer(cases):
        if any(c.get("bad") for c in cases):
            if failure in raised:
                return raised[failure]
            return 0, "[" * 100000
        return 0, json.dumps([{"id": c["id"], "status": "ok"} for c in cases])
    _fake_runner(monkeypatch, answer)
    cases = [{"id": str(i), **({"bad": True} if i == 5 else {})} for i in range(9)]
    rows = df.run_rows(["runner"], cases)
    assert [type(row).__name__ for row in rows] == ["dict"] * 5 + ["NoAnswer"] + ["dict"] * 3, rows
    seed, root = _invalid_label()
    _fake_runner(monkeypatch, lambda cases: answer([{**c, "bad": True} for c in cases]))
    lean, found = _request_classes(seed, root)
    assert lean["outcome"] == "panic" and found == ["no-answer"], (lean, found)


def test_a_runner_whose_output_is_not_utf8_does_not_answer(tmp_path):
    """The `not text` failure above, from a real process: `subprocess` raises while decoding its output."""
    script = tmp_path / "runner.py"
    script.write_text("import sys\nsys.stdin.read()\nsys.stdout.buffer.write(b'\\xff\\xfe')\n")
    [row] = df.run_rows([sys.executable, script], [{"id": "0"}])
    assert type(row) is df.NoAnswer and "UTF-8" in row.reason
    [row] = df.run_rows([tmp_path / "absent"], [{"id": "0"}])
    assert type(row) is df.NoAnswer and "cannot start" in row.reason


# ---------------------------------------------------------------- looprecheck2: rows of unread cases, text

def _position_rows(extra):
    """A runner that exits 1 and prints, for every case, the row of a case it could not read, with `extra`."""
    return lambda cases: (1, json.dumps([{"case_index": i, "status": "error",
                                          "error": "InvalidInput: invalid vocabulary", **extra}
                                         for i, _ in enumerate(cases)]))


def _environment_classes(surface, seed, root):
    [lean] = surface.lean([(seed, root)])
    answers = {"python": surface.python(seed, root), "lean": lean, "rust": df.NOT_APPLICABLE}
    return lean, df.classes(surface, seed, answers, root)[0]


def test_a_row_for_a_case_the_route_could_not_read_names_no_route_code(monkeypatch):
    """An unread environment service case has only the position-error fields."""
    surface, seed, root = _soft_reproducer()
    monkeypatch.setattr(surface, "_service", lambda cases: [
        {"case_index": i, "status": "error", "error": "InvalidInput: invalid vocabulary"}
        for i, _ in enumerate(cases)])
    lean, found = _environment_classes(surface, seed, root)
    assert lean["outcome"] == "error" and "own" not in lean and "no-answer" not in found, (lean, found)
    for code in (7, "SOFT_UNKNOWN_RANK", "SOFT_INVALID_INPUT", "SOFT_NOT_A_CODE", None, ["x"]):
        monkeypatch.setattr(surface, "_service", lambda cases: [
            {"case_index": i, "status": "error", "error": "InvalidInput: invalid vocabulary", "code": code}
            for i, _ in enumerate(cases)])
        lean, found = _environment_classes(surface, seed, root)
        assert lean["outcome"] == "panic" and "no-answer" in found, (code, lean, found)
    surface.close()


def _deep_case():
    """A case nested deeper than every Lean runner's case decoder reads (`JsonInput.parseCases`, 255
    levels in an array): the runner answers it by position."""
    deep = "x"
    for _ in range(300):
        deep = [deep]
    return {"id": "0", "kind": "evaluate", "deep": deep}


# Every Lean runner the fuzzer reads, with the check its rows get (`lean_row_check`, `route_row_check`,
# `diagnose_row_problem`; the service's environment mode is checked by its client's schemas).
LEAN_RUNNER_CHECKS = {
    "ve_conformance route": (["ve_conformance", "route"], df.route_row_problem),
    "ve_conformance": (["ve_conformance"], df.bound_row_problem("ve_conformance", "", [])),
    "ve_conformance check-certificate": (["ve_conformance", "check-certificate"],
                                         df.bound_row_problem("ve_conformance", "check-certificate", [])),
    "ve_diagnose": (["ve_diagnose", "demo@0"], df.diagnose_row_problem),
    **{route.lean: ([route.lean], df.route_row_check(name)) for name, route in df.ROUTES.items() if route.case},
}
# Every field some row of some runner prints beyond the position row.
ROUTE_ONLY_FIELDS = sorted({"id", "code", "valid", "generator", "outcome", "diagnostic", *df.RECORD_FIELDS,
                            *(field for fields in df.LEAN_ROUTE_FIELDS.values() for field in fields),
                            *(key for values in df.REQUEST_VALUES.values() for key in values)}
                           - set(df.POSITION_ROW))


@pytest.mark.parametrize("runner", sorted(LEAN_RUNNER_CHECKS))
def test_every_runner_rows_for_unread_cases_carry_the_position_row_alone(built, runner):
    """The class of the reproducer above, on every Lean runner: its genuine row for a case it could not read
    passes its check, and that row with any field another of its rows prints (a route code, `valid` where
    the mode does not print it, an answer field, an `id`) is a runner that did not answer."""
    command, check = LEAN_RUNNER_CHECKS[runner]
    case = _deep_case()
    [row] = df.run_rows([df.BIN / command[0], *command[1:], "-"], [case])
    assert type(row) is dict and "id" not in row and set(row) <= {*df.POSITION_ROW, "valid"}, (runner, row)
    assert df.checked(check, case, row) == (row, None), runner
    for field in ROUTE_ONLY_FIELDS:
        if field in row:
            continue
        value = {"code": "SOFT_INVALID_INPUT", "valid": False, "id": "0"}.get(field, "x")
        _, bad = df.checked(check, case, {**row, field: value})
        assert bad is not None and bad["outcome"] == "panic", (runner, field)


def test_the_position_row_is_the_service_schemas_case_error():
    """`POSITION_ROW` is the service schemas' row of an unread case (`Service.Protocol.caseError`), and its
    `valid` form belongs to the modes that print `valid` on every error row."""
    common = json.loads((ROOT / "ve/backends/lean_service_schema/common.json").read_text())["$defs"]
    assert set(common["case_error"]["required"]) == set(common["case_error"]["properties"]) == set(df.POSITION_ROW)
    assert set(common["case_error_valid"]["properties"]) == {*df.POSITION_ROW, "valid"}


SURROGATE_OUTPUTS = {
    "rust error.code": lambda c: {"id": c["id"], "status": "error", "error": {"code": "\ud800", "message": "m"}},
    "rust error.message": lambda c: {"id": c["id"], "status": "error", "error": {"code": "C", "message": "\udc00"}},
    "lean error": lambda c: {"id": c["id"], "status": "error", "error": "bad \ud800"},
    "ok value": lambda c: {"id": c["id"], "status": "ok", "label": "\udfff"},
    "key": lambda c: {"id": c["id"], "status": "ok", "\ud800": 1},
}


@pytest.mark.parametrize("where", sorted(SURROGATE_OUTPUTS))
def test_runner_output_that_is_not_unicode_text_does_not_answer(monkeypatch, where):
    """The looprecheck2 B reproducer: on an invalid-label request, runner stdout with the JSON escape `\\ud800`
    in Rust's `error.code` (or `error.message`) passed decoding and validation, then crashed the fuzzer
    (`UnicodeEncodeError` in `digest`). A lone surrogate anywhere in a runner's output (a value, a key, an ok
    row) is output that is not text: the case's runner did not answer, and the fuzzer goes on. Rust has no
    label route since lean-first batch 15b, so the request is an evaluation, which both runners answer."""
    make = SURROGATE_OUTPUTS[where]
    _fake_runner(monkeypatch, lambda cases: (
        1 if "error" in make(cases[0]) else 0, json.dumps([make(c) for c in cases])))
    assert "\\ud" in json.dumps([make({"id": "0"})])  # the escape, as a runner prints it
    [row] = df.run_rows(["runner"], [{"id": "0"}])
    assert type(row) is df.NoAnswer and "Unicode" in row.reason, row
    seed = next(s for s in df.Requests().seeds()
                if s.meta["kind"] == "evaluate" and {"lean", "rust"} <= set(s.engines))
    root = seed.root
    surface = df.Requests()
    [(found, projected, answers, signature)] = df.evaluate(surface, [(seed, root)])
    assert answers["rust"]["outcome"] == "panic" and answers["lean"]["outcome"] == "panic", answers
    assert "no-answer" in found and signature and df.unholdable(projected) is None


def test_every_answer_the_fuzzer_keeps_is_json_text():
    """The class of the reproducer above at the one place every engine's answer enters (`Surface.answers`):
    an answer that cannot be signed and stored as JSON text (a lone surrogate quoted in a Python diagnostic,
    a number JSON cannot print) is Python's crash, or a runner that did not answer; never an exception."""
    from decimal import Decimal

    class Unholdable(Toy):
        def python(self, seed, root):
            return df.error("InvalidInput", "quoted \ud800")

        def lean(self, items):
            return [df.ok({"n": Decimal("1" * 5000)}) for _ in items]
    seed = df.Seed("toy", "toy", "toy", {}, ("python", "lean"))
    [answers] = Unholdable().answers([(seed, {})])
    assert answers["python"]["outcome"] == "crash" and answers["lean"]["outcome"] == "panic", answers
    found, projected = df.classes(Unholdable(), seed, answers, {})
    assert found == ["no-answer", "python-crash"] and df.signature("toy", seed, found, projected)


def test_the_runner_reader_rejects_text_that_is_not_unicode():
    """The production mirror: the one reader of runner output (`lean_service._decode_json`, used by the
    service, which runs every route since lean-first batch 1, and the Rust JSONL checker) rejects a lone
    surrogate in any value or key, so none reaches a diagnostic."""
    from ve.backends.lean_service import _decode_json
    for text in ('"\\ud800"', '["a", ["\\udc00"]]', '{"\\ud800": 1}', '{"a": {"b": "x\\udfff"}}'):
        with pytest.raises(ValueError):
            _decode_json(text)
        with pytest.raises(ValueError):
            _decode_json(text.encode())
    assert _decode_json('{"a": ["\\ud83d\\ude00"]}') == {"a": ["\U0001F600"]}  # a surrogate pair is text


# ---------------------------------------------------------------- B3: coverage

def _load(relative):
    text = (ROOT / relative).read_text()
    return json.loads(text) if text.strip() else None


def test_every_fixture_is_read_or_excluded_with_a_reason():
    usecase_origins = [origin for origin, *_ in corpus.usecase_requests()]
    unread, hiding, matched = [], [], set()
    for relative in corpus.fixture_files():
        verdict = corpus.excluded(relative)
        data = _load(relative)
        if verdict is not None:
            matched |= {p for p in corpus.EXCLUDED if corpus.fnmatch.fnmatchcase(relative, p)}
            kind, reason = verdict
            assert kind in ("artifact", "no-input") and reason, relative
            if kind == "no-input" and data is not None and (corpus.environments_of(relative, data)
                                                            or corpus.requests_of(relative, data)):
                hiding.append(relative)
        elif not corpus.readers(relative, data, usecase_origins):
            unread.append(relative)
    assert unread == [] and hiding == [], (unread, hiding)
    assert matched == set(corpus.EXCLUDED), set(corpus.EXCLUDED) - matched


def test_gate_result_metadata_is_not_an_environment_seed():
    relative = "conformance/english-lean/e2-gate-result.json"
    assert corpus.excluded(relative)[0] == "artifact"
    assert all(not origin.startswith(relative) for origin, _ in corpus.environments())


def test_environments_and_requests_come_from_every_fixture_that_holds_them():
    """The review's B3: environments inside use-case documents and requests, and the conformance families,
    are seeds; so are the route requests of every family and the use cases' models."""
    seeded = {corpus.canonical(env) for _, env in corpus.environments()}
    for source in ("usecases/closure-induction/T9_induction/query.json",
                   "usecases/math-mini-paper/t7-definitions-bundle.json",
                   "usecases/news-article/w6a-quantity-fixtures.json", "conformance/closure.json",
                   "conformance/search.json", "conformance/evaluation.json", "conformance/validation.json",
                   "conformance/norm_defaults_rust.json", "conformance/soft_norms_rust.json",
                   "usecases/claude-constitution-excerpt/definitions-environment.json"):
        held = corpus.environments_of(source, _load(source))
        assert held and {corpus.canonical(env) for _, env in held} <= seeded, source
    profiles = {seed.profile for seed in df.Requests().seeds()}
    for family in ("evaluation:evaluate", "countermodels:countermodel", "closure:evaluate", "search:search",
                   "validation:evaluate", "identity:evaluate", "usecase:closure-induction:certificate",
                   "usecase:news-article:evaluate", "labels:label", "admission:admission"):
        assert family in profiles, family
    assert {seed.meta["kind"] for seed in df.Requests().seeds()} == set(corpus.REQUEST_FIELDS)


def test_every_request_kind_has_a_lean_runner_or_a_reason():
    for family in df.LEAN_REQUESTS:
        for kind in corpus.REQUEST_FIELDS:
            assert (kind in df.LEAN_REQUESTS[family]) != ((family, kind) in df.NO_LEAN), (family, kind)


def test_every_route_is_a_built_lean_executable_with_a_named_rust_path():
    from tools.layer_policy import lean_executables
    executables = lean_executables()
    for name, route in df.ROUTES.items():
        assert route.lean in executables or route.lean in df.SERVICE_MODES, name
        assert (route.rust is None) == bool(route.no_rust), name
        assert route.case is None or "kind" in route.case, name
    routes = {df.lean_route(data) for data in (
        {"language": "ve.core@0"}, *({"profiles": [profile]} for profile, _ in df.PROFILE_ROUTES),
        {"profiles": [], "units": {}})}
    assert routes == set(df.ROUTES)


def test_every_engine_with_a_path_answers_every_environment_seed(built):
    """The review's B3: an engine that rejects a seed still takes part; quantity seeds get a valid route
    request (Lean decodes them and reports Python's identity; Rust has no quantity route since Lean-first
    batch 9), and norm-defaults seeds reach Lean."""
    surface = df.EnvironmentSurface()
    try:
        seeds = surface.seeds()
        assert set(df.ROUTES) == {seed.profile for seed in seeds}
        rows = df.evaluate(surface, [(seed, seed.root) for seed in seeds])
    finally:
        surface.close()
    for seed, (_, _, answers, _) in zip(seeds, rows):
        for engine in df.ENGINES:
            expected = ("ok", "error") if surface.path(engine, seed, seed.root) else ("n/a",)
            assert answers[engine]["outcome"] in expected, (seed.id, engine, answers[engine])
        if seed.profile == "quantity":
            assert answers["lean"] == answers["python"], (seed.id, answers)
            assert answers["python"]["outcome"] == "ok" and answers["rust"]["outcome"] == "n/a"


# ---------------------------------------------------------------- B4: runner rows

def _genuine(surface, engine, seeds):
    """{seed id: (case, row)} of a runner's genuine rows: the rows it printed for the seeds, captured."""
    captured = {}
    batched = df.batched
    service = surface._service if surface.name == "environment" and engine == "lean" else None

    def capture(command, cases):
        rows = batched(command, cases)
        captured.update({case["id"]: (case, row) for case, row in zip(cases, rows)})
        return rows
    def capture_service(cases):
        rows = service(cases)
        captured.update({case["id"]: (case, row) for case, row in zip(cases, rows)})
        return rows
    df.batched = capture
    if service is not None:
        surface._service = capture_service
    try:
        answers = getattr(surface, engine)([(seed, seed.root) for seed in seeds])
    finally:
        df.batched = batched
        if service is not None:
            surface._service = service
    return answers, [captured[str(i)] for i in range(len(seeds))]


def _replay_rows(surface, engine, seeds, rows):
    """The answers of `engine` when its runner prints `rows` for the seeds (row i for case id i), bound to
    their cases as `run_rows` binds them; a row it cannot bind is the runner not answering for that case."""
    def printed(command, cases):
        chosen = [rows[int(case["id"])] for case in cases]
        bound = df.bind_rows(chosen, cases)
        if bound is not None:
            return bound
        return [(df.bind_rows([row], [case]) or [df.NoAnswer("rows out of order")])[0]
                for row, case in zip(chosen, cases)]
    batched = df.batched
    service = surface._service if surface.name == "environment" and engine == "lean" else None
    df.batched = printed
    if service is not None:
        surface._service = lambda cases: printed(None, cases)
    try:
        return getattr(surface, engine)([(seed, seed.root) for seed in seeds])
    finally:
        df.batched = batched
        if service is not None:
            surface._service = service


def _schema_fields(surface, engine, seed, case, row):
    """{path: type} of the fields of a genuine row its check reads (`json`: any value)."""
    if engine == "rust":
        _, fields, _ = df.RUST_ROWS[df.rust_operation(case)]
    elif surface.name == "environment" and engine == "lean":
        fields = {"environment_id": "string", "profiles": "array", "family": "string"}
    elif surface.name == "environment":
        fields = df.LEAN_ROUTE_FIELDS[df.lean_route(seed.root)]
    elif surface.name == "wire":
        fields = {"outcome": "string", **({"diagnostic": "object"} if "diagnostic" in row else {})}
    else:
        fields = {key: "json" for key in df.REQUEST_VALUES[seed.meta["kind"]] if key in row}
    out = {"status": "string", "id": "string", **({"error": "string"} if row.get("status") == "error" else {})}
    if row.get("status") != "error":
        out.update(fields)
    elif surface.name == "environment" and engine == "lean" and df.ROUTES[df.lean_route(seed.root)].own:
        out[df.ROUTES[df.lean_route(seed.root)].own.field] = "string"
    paths = {(name,): spec for name, spec in out.items() if name in row}
    if surface.name == "wire" and "diagnostic" in row:
        paths.update({("diagnostic", name): spec for name, spec in df.RECORD_FIELDS.items()})
    return paths


def _variants(row, path, spec):
    """The row with the field at `path` dropped, and given each JSON type it does not have."""
    def changed(value=None, drop=False):
        out = deepcopy(row)
        parent = df.get(out, path[:-1])
        if drop:
            del parent[path[-1]]
        else:
            parent[path[-1]] = value
        return out
    current = df.get(row, path)
    return [changed(drop=True)] + [changed(value) for value in RETYPED
                                   if spec != "json" and type(value) is not type(current)]


RETYPED = [None, 7, True, "x", [], {}]


def _row_cases():
    """(surface, engine, seeds): a few seeds of every runner and profile."""
    out = []
    requests = df.Requests().seeds()
    environment = df.EnvironmentSurface().seeds()
    wire = df.Wire().seeds()
    for surface, seeds, engines in ((df.Requests(), requests, ("lean", "rust")),
                                    (df.EnvironmentSurface(), [s for s in environment if s.profile != "envelope"],
                                     ("lean", "rust")),
                                    (df.Wire(), wire, ("lean",))):
        by_profile = {}
        for seed in seeds:
            by_profile.setdefault(seed.profile, []).append(seed)
        for engine in engines:
            chosen = [s for group in by_profile.values() for s in group[:2] if engine in s.engines
                      and surface.path(engine, s, s.root)]
            if chosen:
                out.append((surface, engine, chosen))
    return out


def _closed(surface, engine, seed, row):
    """Whether the row's check admits no field its producer does not print: the block routes, `ve_diagnose`
    and the service's route mode (its closed schemas); the error rows of the v0 runner and of Rust."""
    if engine == "lean" and (surface.name in ("environment", "wire") or seed.meta["lean"] == "route"):
        return True
    return row.get("status") == "error"


def test_genuine_rows_pass_their_checks_and_mutated_rows_are_not_answers(built):
    """Checklist 4 and the review's B4 reproducers (an alternatives answer reduced to `{"id": "0"}`; a row
    `{"id": "0", "framing": "oops"}`, which once read as the fuzzer's own package refusal): every genuine
    row of every runner passes its check; a row reduced to its id, alone or with a `framing` or `panic`
    member, is no answer; each field the check reads, dropped or given another JSON type, and a field the
    producer does not print, make the row a runner that did not answer (`panic`), whatever else the row
    says."""
    for surface, engine, seeds in _row_cases():
        answers, genuine = _genuine(surface, engine, seeds)
        assert all(a["outcome"] in ("ok", "error") for a in answers), [a for a in answers if a["outcome"] == "panic"]
        for extra in ({}, {"framing": "oops"}, {"panic": "oops"}):
            reduced = _replay_rows(surface, engine, seeds, [{"id": case["id"], **extra} for case, _ in genuine])
            assert all(a["outcome"] == "panic" for a in reduced), (surface.name, engine, extra, reduced)
        for index, (seed, (case, row)) in enumerate(zip(seeds, genuine)):
            variants = [(path, variant) for path, spec in _schema_fields(surface, engine, seed, case, row).items()
                        for variant in _variants(row, path, spec)]
            if _closed(surface, engine, seed, row):
                variants.append((("framing",), {**row, "framing": "oops"}))
            for path, variant in variants:
                rows = [r for _, r in genuine]
                rows[index] = variant
                answer = _replay_rows(surface, engine, seeds, rows)[index]
                assert answer["outcome"] == "panic", (surface.name, engine, seed.id, path, variant, answer)


def test_route_tables_are_the_genuine_rows_fields(built):
    """Every accepted environment row has the service's three reported fields."""
    surface = df.EnvironmentSurface()
    seeds = [s for s in surface.seeds() if df.ROUTES[s.profile].case is not None]
    _, genuine = _genuine(surface, "lean", seeds)
    seen = {}
    for seed, (_, row) in zip(seeds, genuine):
        if row.get("status") == "ok":
            seen.setdefault(seed.profile, set(row) - {"id", "status"})
    assert seen
    for route, fields in seen.items():
        assert fields == {"environment_id", "profiles", "family"}, (route, fields)
    from tests.test_wire_contract_corpus import CASES
    wire = df.Wire()
    records = [wire.python(df.Seed("wire", "demo@0", name, root), root) for name, root, _ in CASES]
    assert {frozenset(a["record"]) for a in records if a.get("record")} == {frozenset(df.RECORD_FIELDS)}


def test_a_row_that_names_its_case_by_position_is_bound_to_it(tmp_path):
    script = tmp_path / "runner.py"
    script.write_text(
        "import json, sys\n"
        "cases = json.load(sys.stdin)\n"
        "print(json.dumps([{'case_index': i, 'status': 'error', 'error': 'bad'} if c.get('bad') else\n"
        "                  {'id': c['id'], 'status': 'ok'} for i, c in enumerate(cases)]))\n"
        "sys.exit(1 if any(c.get('bad') for c in cases) else 0)\n")
    rows = df.run_rows([sys.executable, script], [{"id": "a"}, {"id": "b", "bad": True}])
    # Bound by position, the row keeps its form: its check knows the runner never ran the case.
    assert rows == [{"id": "a", "status": "ok"}, {"case_index": 1, "status": "error", "error": "bad"}]


def test_an_exit_status_that_disagrees_with_the_rows_is_no_answer(tmp_path):
    script = tmp_path / "runner.py"
    script.write_text(
        "import json, sys\n"
        "cases = json.load(sys.stdin)\n"
        "print(json.dumps([{'id': c['id'], 'status': 'error', 'error': 'x'} for c in cases]))\n")
    rows = df.run_rows([sys.executable, script], [{"id": "a"}])
    assert type(rows[0]) is df.NoAnswer


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
    assert variants == {"nbsp": "Kit 12", "double-space": "Kit  12", "tab": "Kit\t12",
                        "cr": "Kit 12\r", "kelvin": "Kit 12", "dotted-i": "Kİt 12",
                        "upper": "KIT 12", "digits": "Kit ١٢", "curly-quote": "Kit 12’",
                        "control": "Kit 12\x1c"}
    assert df.apply({"s": "it's"}, ["unicode", ["s"], "curly-quote"]) == {"s": "it’s"}
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


def test_drawn_faults_are_listed_faults_without_repeats():
    import random
    root = {"name": "Kit 12", "list": [1, 2], "obj": {"a": 1, "b": "x y"}}
    listed = {json.dumps(m) for m in df.one_faults(root, (), [])}
    faults, rng = df.Faults(root, (), [], False), random.Random(1)
    drawn = [faults.draw(rng) for _ in range(len(listed) * 4)]
    drawn = [json.dumps(m) for m in drawn if m is not None]
    assert len(drawn) == len(set(drawn)) and set(drawn) <= listed and len(drawn) > len(listed) // 2


def test_limits_come_from_the_wire_contract_tables():
    production = json.loads((ROOT / "ve/wire_contract/limits.json").read_text())
    found = {(unit, "/".join(pattern), kind, limit) for unit, pattern, kind, limit in df.limit_patterns()}
    assert (None, "norms", "max_items", production["MAX_RULES"]) in found
    assert (None, "environment/vocabulary/soft/parties", "max_items", production["MAX_SOFT_PARTIES"]) in found
    assert (None, "environment/vocabulary/soft/ranks", "max_items", production["MAX_SOFT_RANKS"]) in found
    assert (None, "norms/*/norm/exception/factors/*", "max_bytes", production["MAX_FACTOR_BYTES"]) in found
    assert ("demo@0", "doc/items", "max_items", 3) in found
    # The environment surface sees the soft block's limits at its root; requests under `environment`.
    env, requests = df.EnvironmentSurface(), df.Requests()
    seed = df.Seed("environment", "envelope", "x", {})
    assert (("vocabulary", "soft", "parties"), "max_items", production["MAX_SOFT_PARTIES"]) in env.limits(seed)
    assert (("environment", "vocabulary", "soft", "parties"), "max_items",
            production["MAX_SOFT_PARTIES"]) in requests.limits(seed)
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
    assert [type(row).__name__ for row in rows] == ["dict"] * 3 + ["NoAnswer"] + ["dict"] * 2 + \
        ["Refused"] + ["dict"] * 2
    assert df.panic(rows[3])["outcome"] == "panic"
    assert df.panic(rows[6]) == df.refusal("")


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


# ---------------------------------------------------------------- every registered item is covered

def test_every_wire_unit_is_fuzzed_or_included(built):
    from tests.test_wire_contract_corpus import CONTRACTS
    units = set(CONTRACTS) | set(df.corpus.WIRE_UNITS)
    included = {"inner@0", "mid@0"}  # reached only through the includes of forms@0 (and Lean's own unit tests)
    seeded = {seed.profile for seed in df.Wire().seeds()}
    assert seeded | included == units
    for unit in units:
        # The service's `diagnose` mode registers the unit: its row is no `no wire contract` error.
        [row] = df.service_rows(["ve_diagnose", unit], [{"id": "u"}])
        assert type(row) is dict and row.get("error") != f"UnsupportedProfile: no wire contract {unit}", (unit, row)


def test_every_follow_up_is_documented_and_used():
    documented = set(re.findall(r"^\| (DF-\d+) \|", (ROOT / "conformance/DIFFFUZZ.md").read_text(), re.M))
    baseline = df.load_baseline()
    used = {entry["follow_up"] for entry in baseline["entries"]}
    assert used <= documented
    assert df.baseline_problems(baseline) == []


def test_baseline_entries_are_well_formed():
    baseline = df.load_baseline()
    signatures = [entry["signature"] for entry in baseline["entries"]]
    assert len(signatures) == len(set(signatures))
    for entry in baseline["entries"]:
        assert entry["surface"] in df.SURFACES
        assert set(entry["engines"]) <= set(df.ENGINES) and "python" in entry["engines"]
        assert entry["classes"] and set(entry["classes"]) <= set(df.CLASSES)
        assert set(entry["answers"]) <= set(df.ENGINES)
        assert all(type(m) is list and len(m) == 3 for m in entry["mutation"])


def test_an_unreviewed_entry_fails(tmp_path):
    baseline = df.load_baseline()
    entry = deepcopy(baseline["entries"][0])
    entry["follow_up"] = "TODO"
    assert df.baseline_problems({"format": df.FORMAT, "entries": [entry]}) == [f"{entry['id']}: no follow-up id"]
