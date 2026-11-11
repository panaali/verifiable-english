"""tools/trust_mutants.py's scoped probe (eff-tm-probe-scope, design reviews/eff-tm-probe-scope-design-20261031.md
section 8): a mutant's probe walks only the checks `settle` reads (`TM_TRUST_ONLY`) and drops the text after the last
of them (`kept`), an entry is whole only with its walk's `done`, a check of the set with no whole entry is read from
the whole file's probe, and `reading` refuses a key `settle` did not hand over. The seeds (real Lean, five modes:
off, on, dual, a cut one line early and the wrong design that leaves the other checks as written) must give the
whole-file probe's verdicts, and the two negative controls must show they can tell."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT
from test_trust_mutants import DECIDE_FALSE, PATH, REFUTE, ROOT, dump, git, scaffold, tool

sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402
import trust_mutants as tm  # noqa: E402


def whole(*flags: str, **consts: str) -> dict:
    return {"flags": {"hash 1", *flags, "done"}, "consts": consts}


# --- `Probes`: the keys `settle` hands over, the fallback --------------------------------------------------------


class Probing:
    """A fake `probing(file, only)`: `scoped` is what the scoped run gives, `full` the whole file's; it records the
    calls."""

    def __init__(self, scoped: dict, full: dict, probeable: set):
        self.scoped, self.full, self.probeable, self.calls = scoped, full, probeable, []

    def __call__(self, f: str, only):
        self.calls.append((f, None if only is None else set(only)))
        return (self.full if only is None else self.scoped), self.probeable


def test_reading_refuses_a_key_settle_did_not_hand_over():
    """Review 2 (F5): `settle` hands its keys to the probe before its first `reads`; any other key raises, before a
    probe runs."""
    probing = Probing({(1, 1): whole(), (2, 2): whole()}, {}, {(1, 1), (2, 2)})
    probes = tm.Probes(probing)
    with pytest.raises(LookupError):
        probes(("A.lean", (1, 1)))
    probes.scope({("A.lean", (1, 1))})
    for key in (("A.lean", (2, 2)), ("B.lean", (1, 1))):
        with pytest.raises(LookupError):
            probes(key)
    assert probing.calls == []
    assert probes(("A.lean", (1, 1))) == whole() and probing.calls == [("A.lean", {(1, 1)})]
    assert probes(("A.lean", (1, 1))) == whole() and len(probing.calls) == 1  # one probe per file
    probes.scope({("A.lean", (1, 1)), ("A.lean", (2, 2))})  # a file probed for fewer checks is probed again
    probes(("A.lean", (2, 2)))
    assert probing.calls[-1] == ("A.lean", {(1, 1), (2, 2)})


def test_settle_hands_its_keys_over_before_its_first_read():
    """`settle` calls `scope` once, with the key of every error it judged, before `reads`; a `reads` that refuses
    every other key (`run`'s `reading`) then settles as before. Without `scope` it raises."""
    text = "#guard f 1 == 2\n#guard f 2 == 3\nexample : f 3 = 5 := by decide\n"
    roles = {"A.lean": [(1, 1, "check", None), (2, 2, "check", None), (3, 3, "check", None)]}
    events: list = []
    probes = tm.Probes(lambda f, only: ({s: whole() for s in only}, {(1, 1), (2, 2), (3, 3)}))

    def scope(keys):
        events.append(("scope", set(keys)))
        probes.scope(keys)

    def reads(key):
        events.append(("reads", key))
        return tm.refusal(probes(key), whole())
    errors = [("A.lean", 1, REFUTE), ("A.lean", 3, DECIDE_FALSE)]
    got = tm.settle(errors, lambda f: text, lambda f: text, roles, None, reads, scope=scope)
    assert got[0] == "KILLED"
    assert events[0] == ("scope", {("A.lean", (1, 1)), ("A.lean", (3, 3))}) and len(events) == 3
    assert {e[1] for e in events[1:]} == {("A.lean", (1, 1)), ("A.lean", (3, 3))}
    with pytest.raises(LookupError):
        tm.settle(errors, lambda f: text, lambda f: text, roles, None,
                  lambda key: tm.refusal(tm.Probes(lambda f, only: ({}, set()))(key), whole()))


@pytest.mark.parametrize(("scoped", "probeable", "fallback"), [
    ({(1, 1): whole(), (5, 5): whole()}, {(1, 1), (5, 5)}, False),  # every entry whole
    ({(1, 1): whole(), (5, 5): {"flags": {"hash 1"}, "consts": {}}}, {(1, 1), (5, 5)}, True),  # a walk cut short
    ({(1, 1): whole()}, {(1, 1), (5, 5)}, True),  # a check of the set absent (a cut that changed a parse: F3)
    ({}, {(1, 1), (5, 5)}, True),  # the scoped run timed out or crashed (F4): no entry at all
    ({(1, 1): whole()}, {(1, 1)}, False),  # a check `named` cannot probe is absent in both (F7)
])
def test_a_check_of_the_set_with_no_whole_entry_is_read_from_the_whole_file(scoped, probeable, fallback):
    """Design 2.5, F3, F4: the fallback fires when a check of the set `named` can probe has no entry with `done` in
    the scoped probe, and then every entry read is the whole file's."""
    full = {(1, 1): whole("sorry"), (5, 5): whole("io"), (9, 9): whole()}
    probing = Probing(scoped, full, probeable)
    probes = tm.Probes(probing)
    probes.scope({("A.lean", (1, 1)), ("A.lean", (5, 5))})
    got = probes(("A.lean", (1, 1)))
    assert [only for _, only in probing.calls] == ([{(1, 1), (5, 5)}, None] if fallback else [{(1, 1), (5, 5)}])
    assert got == (full if fallback else scoped)[(1, 1)]


def test_an_entry_without_its_done_marker_is_absent():
    """Review 1: a walk Lean stopped midway leaves `hash` and some `const` lines but no `sorry`; without `done` the
    entry, the mutant's or the control's, reads as absent, never as no reason (a kill)."""
    cut = {"flags": {"hash 1"}, "consts": {"Demo.f": "3"}}
    assert tm.refusal(whole(**{"Demo.f": "3"}), whole(**{"Demo.f": "3"})) is None
    assert tm.complete(whole()) and not tm.complete(cut) and not tm.complete(None)
    for entry, control in ((cut, whole(**{"Demo.f": "3"})), (whole(**{"Demo.f": "3"}), cut), (None, whole())):
        assert tm.refusal(entry, control) == "Lean could not elaborate it in the probe"


def test_lazy_controls_only_probe_read_checks_and_reuse_entries():
    calls = []
    spans = {(1, 1), (2, 2), (3, 3)}

    def probing(file, only):
        calls.append((file, only))
        return {s: whole() for s in (spans if only is None else only)}, spans

    cache = tm.ControlProbes({"A.lean": None, "B.lean": None}, probing)
    assert calls == []  # a file with no candidate kill is never probed
    assert cache.get(("A.lean", (1, 1)), {(1, 1)}) == whole()
    assert cache.get(("A.lean", (1, 1)), {(1, 1)}) == whole()
    assert cache.get(("A.lean", (2, 2)), {(1, 1), (2, 2)}) == whole()
    assert calls == [("A.lean", {(1, 1)}), ("A.lean", {(2, 2)})]


def test_lazy_control_incomplete_scope_falls_back_and_timeout_stays_unknown():
    calls = []

    def probing(file, only):
        calls.append(only)
        if only is None:
            return {(1, 1): whole(**{"Demo.f": "old"}), (2, 2): whole()}, {(1, 1), (2, 2)}
        return {(1, 1): {"flags": {"hash 1"}, "consts": {}}}, {(1, 1), (2, 2)}

    cache = tm.ControlProbes({"A.lean": None}, probing)
    control = cache.get(("A.lean", (1, 1)), {(1, 1)})
    assert calls == [{(1, 1)}, None] and control == whole(**{"Demo.f": "old"})
    assert tm.refusal(whole(**{"Demo.f": "drift"}), control) == (
        "Demo.f, which it reads, is not what it is without the mutant")
    assert cache.get(("A.lean", (2, 2)), {(2, 2)}) == whole() and len(calls) == 2

    timed_out = tm.ControlProbes({"A.lean": None}, lambda f, only: ({}, {(1, 1)}))
    assert tm.refusal(whole(), timed_out.get(("A.lean", (1, 1)), {(1, 1)})) == (
        "Lean could not elaborate it in the probe")


def test_lazy_control_of_a_file_outside_the_targets_is_none_as_in_eager():
    """eff-20261108-1 F1: `settle` can read a check module no target names (in the mutated module's cone, imported by
    a target). Eager's `hashes` has no entry for it, so `.get` is None; the lazy cache gives the same None without
    probing, never a KeyError, and `refusal` reads it as not elaborated (UNKNOWN)."""
    calls = []
    cache = tm.ControlProbes({"A.lean": None}, lambda f, only: calls.append(f) or ({}, set()))
    eager: dict = {}
    for scope in ({(2, 2)}, set()):
        assert cache.get(("Far/Mid.lean", (2, 2)), scope) is None is eager.get(("Far/Mid.lean", (2, 2)))
    assert calls == []
    assert tm.refusal(whole(), cache.get(("Far/Mid.lean", (2, 2)), {(2, 2)})) == (
        "Lean could not elaborate it in the probe")


def test_concurrent_lazy_control_of_one_file_is_computed_once():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    entered, second, release = Event(), Event(), Event()
    calls = []

    def probing(file, only):
        calls.append(only)
        if len(calls) > 1:  # a second computation (no shared lock): the test fails on `calls`
            second.set()
            return {(1, 1): whole()}, {(1, 1)}
        entered.set()
        assert release.wait(timeout=HANG_TIMEOUT)
        return {(1, 1): whole()}, {(1, 1)}

    class Watched:  # the file's lock, which says when the second reader is waiting on it
        def __init__(self, inner):
            self.inner, self.tries = inner, 0

        def __enter__(self):
            self.tries += 1
            if self.tries == 2:
                second.set()
            self.inner.acquire()

        def __exit__(self, *exc):
            self.inner.release()

    cache = tm.ControlProbes({"A.lean": None}, probing)
    cache.locks["A.lean"] = Watched(cache.locks["A.lean"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        one = pool.submit(cache.get, ("A.lean", (1, 1)), {(1, 1)})
        assert entered.wait(timeout=HANG_TIMEOUT)
        two = pool.submit(cache.get, ("A.lean", (1, 1)), {(1, 1)})
        assert second.wait(timeout=HANG_TIMEOUT)  # the second reader is at the lock (or computing without it)
        release.set()
        assert one.result() == two.result() == whole()
    assert calls == [{(1, 1)}]


def test_lazy_controls_of_different_files_can_probe_together():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    both = Barrier(2)

    def probing(file, only):
        both.wait(timeout=HANG_TIMEOUT)
        return {(1, 1): whole()}, {(1, 1)}

    cache = tm.ControlProbes({"A.lean": None, "B.lean": None}, probing)
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(cache.get, ("A.lean", (1, 1)), {(1, 1)})
        b = pool.submit(cache.get, ("B.lean", (1, 1)), {(1, 1)})
        assert a.result() == b.result() == whole()


def test_run_reads_the_unmutated_control_for_a_drifted_constant(tmp_path, monkeypatch):
    lean = tmp_path / "lean"
    (lean / "Demo").mkdir(parents=True)
    (lean / "Demo/Defs.lean").write_text("abc")
    (lean / "Demo/Check.lean").write_text("import Demo.Defs\n#guard true\n")

    class Scratch:
        def __init__(self):
            self.lean = lean

        def lake(self, env, *args, timeout=None):
            return (1, "FAIL") if "+Demo.Check" in args and (lean / "Demo/Defs.lean").read_text() != "abc" else (0, "")

    key = ("Demo/Check.lean", (2, 2))
    control = tm.ControlProbes({key[0]: None}, lambda f, only: ({(2, 2): whole(**{"Demo.f": "old"})}, {(2, 2)}))
    monkeypatch.setattr(tm, "targets", lambda *args: ["Demo.Defs", "Demo.Check"])
    monkeypatch.setattr(tm, "moved", lambda *args: None)
    monkeypatch.setattr(tm, "located", lambda output, pattern=tm.ERROR: [(*key[:1], 2, 1, "bad")] if output else [])
    monkeypatch.setattr(tm, "named", lambda text, roles: (text, {"tmChk_2": (2, 2)}))
    monkeypatch.setattr(tm, "probe", lambda lake, env, text, roles, path, outside=False, only=None: {
        (2, 2): whole(**{"Demo.f": "drift"})})

    def settle(found, read, checkout, roles, rebuild, reads, scope):
        scope({key})
        return "UNKNOWN", reads(key)

    monkeypatch.setattr(tm, "settle", settle)
    mutant = tm.Mutant("M001", "Demo/Defs.lean", 1, "Demo.f", "body-true", 0, 1, (1, 1), "a", "X")
    mutant.edit = (1, "X")
    tree = tm.Tree({"Demo/Check.lean": [(2, 2, "check", None)]}, {}, {}, {})
    assert tm.run(mutant, Scratch(), tree, [], [], {}, hashes=control) == (
        "UNKNOWN", "Demo.f, which it reads, is not what it is without the mutant")


# --- `probe(only=...)` and `kept`, without Lean ------------------------------------------------------------------


PROBED = ("import Demo.Defs\n#guard f 1 == 2\ndef g := 1\n#guard f 2 == 3\n\n#guard f 3 == 4\n"
          "example : f 4 = 5 := by decide\n")
PROBED_ROLES = [(2, 2, "check", None), (3, 3, "other", None), (4, 5, "check", None), (6, 6, "check", None),
                (7, 7, "check", None)]


class FakeLake:
    """`probe`'s `lake`: records the env and the text written to the probe's path, and prints each named check's
    entry (`done` included but for the names in `cut`) under the call's nonce."""

    def __init__(self, path: Path, cut: tuple = ()):
        self.path, self.cut, self.calls = path, cut, []

    def __call__(self, env: dict, *args: str):
        text = self.path.read_text()
        self.calls.append((env.get("TM_TRUST_ONLY"), text))
        only = env.get("TM_TRUST_ONLY")
        names = [n for n in re.findall(r"tmChk_\d+", text) if only is None or n in only.split(" ")]
        nonce = env["TM_TRUST_NONCE"]
        said = [f"{nonce} {n} {x}" for n in names for x in ("hash 7", "const Demo.f 11", "done") if
                not (x == "done" and n in self.cut)]
        return 0, "\n".join(["noise", *said, f"{nonce[:-1]}x tmChk_2 sorry"])


def test_probe_walks_only_its_checks_and_drops_the_text_after_them(tmp_path):
    """`only`: the same rewritten text, every check named, cut before the command after the set's last check, and
    `TM_TRUST_ONLY` naming the set's checks; the controls' probe (`only` None) is the whole file, every check walked.
    A set with no check `named` can probe runs no Lean (the whole file's probe has no entry for it either)."""
    path = tmp_path / "A.lean"
    lake = FakeLake(path)
    full = tm.probe(lake, {}, PROBED, PROBED_ROLES, path)
    assert lake.calls[0][0] is None and lake.calls[0][1].count("\n") == PROBED.count("\n")
    assert set(full) == {(2, 2), (4, 5), (6, 6), (7, 7)} and not path.exists()
    assert full[(2, 2)] == {"flags": {"hash 7", "done"}, "consts": {"Demo.f": "11"}}
    scoped = tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(2, 2), (4, 5)})
    only, text = lake.calls[1]
    assert only == "tmChk_2 tmChk_4" and set(scoped) == {(2, 2), (4, 5)}
    assert text.split("\n") == lake.calls[0][1].split("\n")[:5]  # lines 1-5: up to the command after (4, 5)
    assert "#tm_trust_guard tmChk_6" not in text and text.startswith("import TmTrustProbe import Demo.Defs")
    assert scoped == {s: full[s] for s in scoped}
    assert tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(3, 3)}) == {} and len(lake.calls) == 2
    tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only={(7, 7)})  # the last command: every line kept
    assert lake.calls[2][1] == lake.calls[0][1] and lake.calls[2][0] == "tmChk_7"


def test_probe_keeps_an_entry_whose_walk_did_not_finish_without_done(tmp_path):
    path = tmp_path / "A.lean"
    got = tm.probe(FakeLake(path, cut=("tmChk_4",)), {}, PROBED, PROBED_ROLES, path, only={(2, 2), (4, 5)})
    assert tm.complete(got[(2, 2)]) and not tm.complete(got[(4, 5)])


def test_a_probe_past_the_build_timeout_says_so_and_stays_unknown(tmp_path):
    """tm-m509-reads-linear (2): a probe run killed at --build-timeout (`TIMED_OUT`, the scoped one and the whole
    file's) leaves each check it was to walk unknown with that reason, not "Lean could not elaborate it"; a run Lean
    failed keeps the old reason."""
    path, calls = tmp_path / "A.lean", []

    def lake(env, *args):
        calls.append(env.get("TM_TRUST_ONLY"))
        return tm.TIMED_OUT, f"lake {args[0]} did not finish in 500 s (--build-timeout)"
    probes = tm.Probes(lambda f, only: (tm.probe(lake, {}, PROBED, PROBED_ROLES, path, only=only),
                                        {(2, 2), (4, 5), (6, 6), (7, 7)}))
    probes.scope({("A.lean", (2, 2))})
    got = tm.settle([("A.lean", 2, REFUTE)], lambda f: PROBED, lambda f: PROBED, {"A.lean": PROBED_ROLES}, None,
                    lambda key: tm.refusal(probes(key), whole()))
    assert calls == ["tmChk_2", None]  # the scoped probe, then the whole file's (`Probes`)
    assert got[0] == "UNKNOWN" and got[1].endswith("(the probe did not finish in 500 s (--build-timeout))"), got
    failed = tm.probe(lambda env, *args: (1, "error"), {}, PROBED, PROBED_ROLES, path)
    assert failed == {} and tm.refusal(failed.get((2, 2)), whole()) == "Lean could not elaborate it in the probe"
    assert tm.refusal(whole(), probes(("A.lean", (2, 2)))) == "the probe did not finish in 500 s (--build-timeout)"


# F3's shapes (review 5): a `mutual … end` holding a `decide` theorem, `where` and `termination_by` tails, a docstring
# before the next command, `set_option … in`, an attribute on its own line and a multi-line `#guard`.
F3 = """import Demo.Defs
open Demo

mutual
theorem m1 : small 1 = true := by decide
theorem m2 : small 2 = true := by decide
end

def f (n : Nat) : Nat := g n
where
  g (m : Nat) : Nat := m + 1
#guard f 1 == 2
def h : Nat → Nat
  | 0 => 0
  | n + 1 => h n
termination_by n => n
#guard h 3 == 0

/-- a docstring before the next command -/
example : small 0 = true := by decide

set_option maxRecDepth 1000 in
#guard (f 2 ==
  3)
@[simp]
theorem s : f 0 = 1 := rfl
#guard_msgs in
#guard !small 5
"""
F3_THEOREMS = ("theorem m1", "theorem m2", "theorem s")


def f3_roles(path: Path) -> list[tuple]:
    """`file_roles` of F3, its theorems checks (as lean/'s recorded ones are)."""
    lines = F3.split("\n")
    return [(s, e, "check" if any(lines[n].startswith(F3_THEOREMS) for n in range(s - 1, e)) else role, x)
            for s, e, role, x in tm.file_roles(path)]


def f3_line(text: str) -> int:
    return next(n for n, line in enumerate(F3.split("\n"), 1) if line.startswith(text))


@pytest.mark.parametrize(("check", "keeps"), [
    ("theorem m1", "theorem m1"),  # inside `mutual`: cut before m2, the block left open
    ("theorem m2", ""),  # the last of the block: its `end` and the blank line after it kept
    ("#guard f 1 == 2", "#guard f 1 == 2"),  # after a `where` tail, kept whole
    ("#guard h 3 == 0", "/-- a docstring"),  # trust_map's span takes the next command's docstring: left dangling
    ("example : small 0", ""),  # its blank line kept, cut before `set_option … in`
    ("set_option", "  3)"),  # the multi-line `#guard` under `set_option … in`, whole
    ("@[simp]", "theorem s"),  # the attribute on its own line is the theorem's span
    ("#guard_msgs in", ""),  # the last command: every line kept, to the file's last newline
])
def test_kept_cuts_at_the_line_before_the_next_command(tmp_path, check, keeps):
    """F3: `kept` keeps every line up to the one before the first command that starts after the set's last check;
    what the cut leaves at the end is the check's own span (a trailing docstring or blank line included)."""
    path = tmp_path / "F3.lean"
    path.write_text(F3)
    roles = f3_roles(path)
    span = next((s, e) for s, e, *_ in roles if s == f3_line(check))
    lines = F3.split("\n")
    after = next((s for s, *_ in roles if s > span[1]), len(lines) + 1)
    got = tm.kept(lines, roles, span[1])
    assert got == lines[:after - 1] and len(got) >= span[1]
    assert got[-1].startswith(keeps) if keeps else got[-1] == ""


def lake_in(lean: Path):
    def lake(env: dict, *args: str) -> tuple[int, str]:
        done = subprocess.run([lake_outputs.lean_executable(None, "lake"), *args], cwd=lean, env=env,
                              capture_output=True, text=True, timeout=HANG_TIMEOUT)
        return done.returncode, done.stdout + done.stderr
    return lake


@pytest.fixture(scope="module")
def f3_package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("f3")
    scaffold(root, ".")
    (root / "lean/Demo/Defs.lean").write_text("namespace Demo\n\ndef small (n : Nat) : Bool := n < 3\n\nend Demo\n")
    (root / "lean/Demo/F3.lean").write_text(F3)
    env = {**os.environ, **PATH}
    assert lake_in(root / "lean")(env, "build", "Demo.F3")[0] == 0
    assert tm.install(lambda *a: lake_in(root / "lean")(env, *a), root / "lean")
    return root


def test_a_cut_that_changes_a_parse_fails_closed_in_lean(f3_package, monkeypatch):
    """F3 in Lean: each check of F3 probed alone gives the whole file's entry, or none (then `Probes` reads the
    whole file's): never another whole entry. A cut one line early (the negative control) changes some entries,
    and each of those is absent or refused (`refusal`), never a kill."""
    lean, env = f3_package / "lean", {**os.environ, **PATH}
    path, lake = lean / "Demo/F3.lean", lake_in(lean)
    roles = f3_roles(path)
    full = tm.probe(lake, env, F3, roles, path)
    spans = sorted(full)
    assert len(spans) == 8 and all(tm.complete(full[s]) for s in spans), full
    absent = []
    for span in spans:
        got = tm.probe(lake, env, F3, roles, path, only={span})
        assert set(got) <= {span}
        if tm.complete(got.get(span)):
            assert got[span] == full[span], span
        else:
            absent.append(span)
    assert path.read_text() == F3
    # Lean elaborates the `mutual` block a cut leaves open too (4.x); were it absent, `Probes` would fall back
    assert set(absent) <= {(f3_line("theorem m1"), f3_line("theorem m1"))}, absent
    early = tm.kept
    monkeypatch.setattr(tm, "kept", lambda lines, roles, last: early(lines, roles, last)[:-1])
    changed = 0
    for span in spans:
        got = tm.probe(lake, env, F3, roles, path, only={span})
        if got.get(span) != full[span]:
            changed += 1
            assert tm.refusal(got.get(span), full[span]) is not None, (span, got)
    assert changed, "a cut one line early changed no entry"


# --- `READS`: the gate first, `done` last, no effects ------------------------------------------------------------


GATE = ['  if let some only ← IO.getEnv "TM_TRUST_ONLY" then',
        '    if !((only.splitOn " ").contains k.toString) then return']
EFFECTS = re.compile(r"\b(?:modifyEnv|setEnv|addDecl|addAndCompile|compileDecl|setOption|withOptions|modifyScope|"
                     r"IO\.mkRef|ST\.mkRef|mkRef|initialize|builtin_initialize|pushInfoLeaf|pushInfoTree|logInfo|"
                     r"logWarning|logError|addInstance|setReducibilityStatus|modifyThe|set)\b")


def walk_faults(reads: str) -> list[str]:
    """What breaks design 3(b) in the walk of `reads` (the `READS` text): the `TM_TRUST_ONLY` gate not its first
    statement, `done` not its last line, a statement with an effect a later command could read (F6), or a theorem's
    value in a `const` line (its proof term, which a skipped walk's budget can change: 3b)."""
    lines = reads.split("\n")
    head = lines.index("def tmTrustWalk (k : Name) (roots : List Expr) : MetaM Unit := do")
    end = next(i for i in range(head + 1, len(lines)) if lines[i] and not lines[i].startswith(" "))
    body = [line for line in lines[head + 1:end] if line.strip() and not line.strip().startswith("--")]
    faults = []
    if body[:2] != GATE:
        faults.append("the gate is not the walk's first statement")
    if body[-1] != '  say "done"':
        faults.append("`done` is not the walk's last line")
    if hits := sorted({m for line in body for m in EFFECTS.findall(line)}):
        faults.append(f"effects: {hits}")
    if [line for line in body if "IO.println" in line] != [
            '  let say (s : String) : IO Unit := do IO.println s!"{(← IO.getEnv "TM_TRUST_NONCE").getD ""} {k} {s}"']:
        faults.append("it prints other than through `say`")
    const = [line for line in body if 'say s!"const ' in line]
    if len(const) != 1 or not const[0].strip().startswith("if !(info matches .thmInfo _) && "):
        faults.append("a theorem's value can reach a `const` line")
    return faults


@pytest.mark.parametrize(("edit", "fault"), [
    (None, None),
    (lambda r: r.replace("\n".join(GATE) + "\n  let env ← getEnv\n", "  let env ← getEnv\n" + "\n".join(GATE) + "\n"),
     "first statement"),
    (lambda r: r.replace('  say "done"\n', ""), "`done`"),
    (lambda r: r.replace('  say "done"\n', '  say "done"\n  modifyEnv id\n'), "`done`"),
    (lambda r: r.replace("  let mut seen", "  modifyEnv id\n  let mut seen"), "modifyEnv"),
    (lambda r: r.replace("  let mut seen", "  let r ← IO.mkRef 0\n  let mut seen"), "IO.mkRef"),
    (lambda r: r.replace("  let mut seen", "  setOption `x 0\n  let mut seen"), "setOption"),
    (lambda r: r.replace("  let mut seen", "  logInfo m!\"x\"\n  let mut seen"), "logInfo"),
    (lambda r: r.replace("if !(info matches .thmInfo _) && ", "if "), "theorem"),
    (lambda r: r.replace("  let mut seen", "  IO.println \"x\"\n  let mut seen"), "prints"),
])
def test_the_walk_reads_and_prints_only(edit, fault):
    """F6 (review 9b): in `READS` the `TM_TRUST_ONLY` gate is the walk's first statement, `done` its last line, it
    has no `modifyEnv`/`addDecl`/`setOption`/`IO.mkRef`/`initialize` (nor any other effect a later command reads),
    prints only through `say`, and keeps theorems (`thmInfo`) out of the `const` lines. Each edit is a negative
    control: the check must name it."""
    faults = walk_faults(tm.READS if edit is None else edit(tm.READS))
    if fault is None:
        assert faults == []
    else:
        assert edit(tm.READS) != tm.READS and any(fault in x for x in faults), faults


# tm-m509-reads-linear (1): the List worklist `READS` had (`++` copied it per constant), rebuilt from today's text
LIST_WORKLIST = [
    ("  let mut todo : Array Name := roots.foldl (fun a e => a ++ e.getUsedConstants) #[]\n  let mut head := 0\n",
     "  let mut todo : List Name := roots.foldl (fun a e => a ++ e.getUsedConstants.toList) []\n"),
    ("  while head < todo.size do\n    let c := todo[head]!\n    head := head + 1\n",
     "  while !todo.isEmpty do\n    let c := todo.head!\n    todo := todo.tail!\n"),
    ("todo ++ info.type.getUsedConstants ++ value.getUsedConstants\n",
     "todo ++ info.type.getUsedConstants.toList ++ value.getUsedConstants.toList\n")]
ORDER_DEFS = """namespace Demo

def helper (n : Nat) : Nat := n + 1
def shared (n : Nat) : Nat := helper n + helper (n + 1)
def other (n : Nat) : Nat := helper (2 * n)
def twice (n : Nat) : Nat := shared n + other n

mutual
def isEven : Nat → Bool
  | 0 => true
  | n + 1 => isOdd n
def isOdd : Nat → Bool
  | 0 => false
  | n + 1 => isEven n
end

end Demo
"""
ORDER = "import Demo.Defs\nopen Demo\n\n#guard twice 2 == 12\n\nexample : isEven 4 = true := by decide\n"


@pytest.fixture(scope="module")
def order_package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("order")
    scaffold(root, ".")
    (root / "lean/Demo/Defs.lean").write_text(ORDER_DEFS)
    (root / "lean/Demo/Order.lean").write_text(ORDER)
    assert lake_in(root / "lean")({**os.environ, **PATH}, "build", "Demo.Order")[0] == 0
    return root


def walk_lines(root: Path, reads: str, monkeypatch) -> list[str]:
    """Every line `reads`, installed, prints for `ORDER`'s checks, in order, without the call's nonce."""
    lean, env, said = root / "lean", {**os.environ, **PATH}, []
    with monkeypatch.context() as patch:
        patch.setattr(tm, "READS", reads)
        assert tm.install(lambda *a: lake_in(lean)(env, *a), lean)

    def lake(env_: dict, *args: str) -> tuple[int, str]:
        said.append((env_["TM_TRUST_NONCE"], got := lake_in(lean)(env_, *args)))
        return got
    tm.probe(lake, env, ORDER, [(4, 4, "check", None), (6, 6, "check", None)], lean / "Demo/Order.lean")
    (nonce, (code, out)), = said
    return [rest for mark, _, rest in (x.partition(" ") for x in out.splitlines()) if mark == nonce]


def test_the_linear_worklist_walks_in_the_list_order(order_package, monkeypatch):
    """tm-m509-reads-linear (1): `READS`'s Array queue prints exactly the lines the List worklist printed, in the
    same order (`hash`, each `const`, `done`), for a check over a shared closure (`helper` under `shared` and
    `other`) and one over a cycle (`isEven`/`isOdd`'s `_unsafe_rec`s)."""
    lines = walk_lines(order_package, tm.READS, monkeypatch)
    assert [x.split()[2] for x in lines if x.startswith("tmChk_4 const")] == [
        "Demo.twice", "Demo.shared", "Demo.other", "Demo.helper"]  # the List's order: breadth first
    assert any(" const Demo.isOdd._unsafe_rec " in x for x in lines)
    for k in ("tmChk_4", "tmChk_6"):
        mine = [x for x in lines if x.startswith(k + " ")]
        assert mine[-1] == f"{k} done" and sum(" const " in x for x in mine) >= 3, mine
    old = tm.READS
    for new, before in LIST_WORKLIST:
        assert old.count(new) == 1, new
        old = old.replace(new, before)
    assert lines == walk_lines(order_package, old, monkeypatch)


# --- the seeds, in real Lean, in five modes ----------------------------------------------------------------------


SEED_DEFS = """namespace Demo

def small (n : Nat) : Bool := n < 3

def big (n : Nat) : Bool := 5 < n

def tag (n : Nat) : Nat := n + 1

def lone (n : Nat) : Nat := n + 0

def far (n : Nat) : Nat := n * 2

def gate (n : Nat) : Bool := n < 7

def viaGate (n : Nat) : Bool := gate n && true

end Demo
"""
# S2: a proof in an imported module that the mutant breaks (cut to sorry) and a check that computes through it;
# S3: an import-time failure (a definition of the imported module fails under the mutant: the check file never loads)
SEED_MID = """import Demo.Defs

namespace Demo

theorem small_lt {n : Nat} (h : small n = true) : n < 3 := by simpa [small] using h

def bounded (n : Nat) : Bool := if h : small n = true then (⟨n, small_lt h⟩ : Fin 3).val == n else true

def loneMid : Fin 1 := ⟨lone 0, by decide⟩

end Demo
"""
FILLER = "".join(f"#guard Demo.tag {i} == {i + 1}\n" if i % 3 else f"example : Demo.big {i + 6} = true := by decide\n"
                 for i in range(40))
SEED_EXAMPLES = f"""import Demo.Mid
open Demo

-- S1: a named check theorem outside the verdict's set (it passes under the mutant), read by a check in the set
theorem pre : small 0 = true := by decide

def usesPre : Bool := (⟨0, pre⟩ : {{n : Nat // small n = true}}).1 == 0 && !small 3

#guard small 2
-- S4: a matcher an earlier check outside the set creates, which a later check of the set may reuse
#guard (match small 1 with | true => 1 | false => 0) == 1
#guard tag 0 == 1
{FILLER}#guard (tag 50 ==
  51)

#guard usesPre
#guard (match small 3 with | true => 1 | false => 0) == 0
#guard (bounded 3 && !small 3)
#guard !big 5

/-- S5: the last command, a docstring before it -/
example : big 6 = true := by decide
"""
# S6: a kill by a check whose text never names the mutated definition (`gate`, read through `viaGate`), after a
# check outside the set wrapped in `#guard_msgs`
SEED_SECOND = """import Demo.Defs

#guard Demo.tag 4 == 5

-- S7: an `rfl` check (the `decide` rebuild path)
example : Demo.tag 1 = 2 := rfl

#guard_msgs in example : Demo.gate 2 = true := by decide

#guard !Demo.viaGate 7
"""
SEED_OUTSIDE = """import Demo.Defs

#guard Demo.far 2 == 4
"""
# The modes, test-side only (the tool ships the scoped probe alone): `off` probes the whole file; `dual` also probes
# the whole file beside each scoped probe and logs both; `cut-1` cuts one line early (it must fall back and keep
# every verdict); `naive` leaves the other checks as written (the wrong design: it must change S1).
WRAPPER = r'''
import json, os, sys, threading
sys.path.insert(0, sys.argv[1])
import trust_mutants as tm

mode, log, lock, local = sys.argv[2], sys.argv[3], threading.Lock(), threading.local()
probe, kept, settle, run = tm.probe, tm.kept, tm.settle, tm.run


def norm(d, spans):
    return {f"{s[0]}-{s[1]}": {"flags": sorted(d[s]["flags"]), "consts": d[s]["consts"]} for s in spans if s in d}


def write(row):
    with lock, open(log, "a") as out:
        out.write(json.dumps({"id": getattr(local, "id", None), **row}) + "\n")


def probing(lake, env, text, roles, path, outside=False, only=None):
    row = {"file": path.name, "only": None if only is None else sorted(only),
           "control": "TM_TRUST_MUTATED" not in env}
    if mode == "naive" and only is not None:
        roles = [r for r in roles if (r[0], r[1]) in only]
    got = probe(lake, env, text, roles, path, outside, None if mode == "off" else only)
    if only is not None:
        row["got"] = norm(got, only)
        if mode in ("dual", "cut-1"):
            row["whole"] = norm(probe(lake, env, text, roles, path, outside), only)
    write(row)
    return got


def settling(*args, **kwargs):
    try:
        args[5](("Nowhere.lean", (0, 0)))
        write({"refused": False})
    except LookupError:
        write({"refused": True})
    return settle(*args, **kwargs)


def running(m, *args, **kwargs):
    local.id = m.id
    try:
        return run(m, *args, **kwargs)
    finally:
        local.id = None


tm.probe, tm.settle, tm.run = probing, settling, running
if mode == "cut-1":
    tm.kept = lambda lines, roles, last: kept(lines, roles, last)[:-1]
sys.exit(tm.main(sys.argv[4:]))
'''
MODES = ("off", "on", "dual", "cut-1", "naive")


def seeded(root: Path, scratch: Path, mode: str, control_mode: str = "eager",
           max_mutants: int = 1000, jobs: int = 4) -> tuple[dict, list[dict], str]:
    scratch.mkdir(parents=True, exist_ok=True)
    (wrapper := scratch / "wrapper.py").write_text(WRAPPER)
    log, out = scratch / "probes.jsonl", scratch / "evidence.json"
    env = {**os.environ, **PATH, "TMPDIR": str(scratch), "VE_LEAN_SHARE": "off"}
    done = subprocess.run([sys.executable, str(wrapper), str(ROOT / "tools"), mode, str(log), "--root", str(root),
                           "--base", "HEAD~1", "--jobs", str(jobs), "--control-probes", control_mode,
                           "--json", str(out), "--test", "outside/Check.lean",
                           "--max-mutants", str(max_mutants)], env=env, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)
    mutants = json.loads(out.read_text())["mutants"] if out.is_file() else []
    rows = [json.loads(x) for x in log.read_text().splitlines()] if log.is_file() else []
    return {m["id"]: (m["definition"], m["operator"], m["status"], m["raw_status"], m["detail"])
            for m in mutants}, rows, done.stderr[-3000:]


@pytest.fixture(scope="module")
def seed_package(tmp_path_factory):
    root = tmp_path_factory.mktemp("seeds")
    scaffold(root, ".")
    for name, text in (("Defs", SEED_DEFS), ("Mid", SEED_MID), ("Examples", SEED_EXAMPLES), ("Second", SEED_SECOND)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    (root / "outside").mkdir()
    (root / "outside/Check.lean").write_text(SEED_OUTSIDE)
    dump(root, tmp_path_factory.mktemp("dump"), ["pre", "Demo.small_lt"])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return root


def test_eager_and_lazy_controls_agree_on_seeded_package(seed_package, tmp_path_factory):
    eager, eager_rows, err = seeded(seed_package, tmp_path_factory.mktemp("eager-control"), "on", "eager", 30, 1)
    assert eager, err
    lazy, lazy_rows, err = seeded(seed_package, tmp_path_factory.mktemp("lazy-control"), "on", "lazy", 30, 1)
    assert lazy, err
    assert eager == lazy
    eager_controls = [r for r in eager_rows if r.get("control")]
    lazy_controls = [r for r in lazy_rows if r.get("control")]
    assert eager_controls and lazy_controls
    assert all(r["only"] is None for r in eager_controls)
    assert any(r["only"] is not None for r in lazy_controls)
    # eager: today's calls, one whole-file control per check file, all before any mutant; lazy: inside a mutant
    probes = [r for r in eager_rows if "file" in r]
    assert probes[:len(eager_controls)] == eager_controls and all(r["id"] is None for r in eager_controls)
    assert len({r["file"] for r in eager_controls}) == len(eager_controls)
    assert all(r["id"] is not None for r in lazy_controls)
    assert {r["file"] for r in lazy_controls} <= {r["file"] for r in eager_controls}


def test_the_scoped_probe_classifies_the_seeds_as_the_whole_file_probe(seed_package, tmp_path_factory):
    """Design 6 and review 8: the seed package's mutants get the same status, raw_status and detail with the scoped
    probe (`on`, `dual`, and `cut-1`, which must fall back) as with the whole file's (`off`); in `dual every scoped
    entry carries `done` and equals the whole file's, none absent in both and none falling back; eager controls
    are whole-file; `reading` refuses a key `settle` did not hand over. A KILLED detail cites the first kill in
    Lake's output order, which two check modules built at once can swap, so it is compared up to that."""
    got, rows = {}, {}
    for mode in MODES:
        got[mode], rows[mode], err = seeded(seed_package, tmp_path_factory.mktemp(mode), mode)
        assert got[mode], (mode, err)
    off = got["off"]
    same = lambda v: v[:4] + (("KILLED",) if v[3] == "KILLED" else (v[4],))  # noqa: E731
    for mode in ("on", "dual", "cut-1"):
        assert {i: same(v) for i, v in got[mode].items()} == {i: same(v) for i, v in off.items()}, mode
    assert {v[2] for v in off.values()} >= {"KILLED", "UNKNOWN"}, off
    # the controls' probes are whole-file; a mutant's probe is scoped, but in `off` and on a fallback
    for mode in MODES:
        assert all(r["only"] is None for r in rows[mode] if r["id"] is None and "file" in r), mode
    scoped = {mode: [r for r in rows[mode] if r["id"] and "file" in r and r["only"] is not None] for mode in MODES}
    fell = {mode: [r for r in rows[mode] if r["id"] and "file" in r and r["only"] is None] for mode in MODES}
    assert scoped["on"] and not fell["on"] and not fell["dual"] and not fell["off"]
    assert fell["cut-1"], "the cut one line early never fell back"
    # `dual`: every scoped entry is whole and is the whole file's; no check of a set is absent in both
    dual = scoped["dual"]
    assert dual and all(r["got"] == r["whole"] for r in dual), [r for r in dual if r["got"] != r["whole"]]
    assert all(len(r["got"]) == len(r["only"]) for r in dual), [r for r in dual if len(r["got"]) != len(r["only"])]
    assert all("done" in e["flags"] for r in dual for e in r["got"].values())
    # `reading` refuses a key `settle` did not hand over, in the tool as run
    refused = [r["refused"] for r in rows["on"] if "refused" in r]
    assert refused and all(refused)
    lines = SEED_EXAMPLES.split("\n")
    at = lambda text: next(n for n, line in enumerate(lines, 1) if line.startswith(text))  # noqa: E731
    by = lambda d, o: [(i, v) for i, v in off.items() if v[:2] == (f"Demo.{d}", o)]  # noqa: E731
    # S1: the named theorem outside the set reads as `sorry` (the probe's own rewrite), so UNKNOWN, as whole-file;
    # the wrong design differs exactly there
    s1 = by("small", "lt-le")
    assert s1 and all(v[2] == "UNKNOWN" and "proof the mutant broke" in v[4] and
                      f"Examples.lean:{at('#guard usesPre')}" in v[4] for _, v in s1), s1
    assert any(got["naive"][i] != v for i, v in s1), "the wrong design kept S1"
    # S2: the check through the cut proof reads `sorry`
    s2 = f"{at('#guard (bounded 3')}-{at('#guard (bounded 3')}"
    assert any("sorry" in r["got"].get(s2, {}).get("flags", []) for r in dual), s2
    # S3: the import-time failure: UNKNOWN at the imported module, and no probe
    s3 = by("lone", "lit-plus")
    assert s3 and all(v[2] == "UNKNOWN" and "Mid.lean" in v[4] for _, v in s3), s3
    assert not any(r["id"] == i for i, _ in s3 for mode in MODES for r in rows[mode] if "file" in r)
    # S4: the matcher check read in a dual row; S5: a kill by the last command, and a cut of 5 lines or more
    assert any(s == at("#guard (match small 3") for r in dual for s, _ in r["only"])
    assert any(s == at("example : big 6") for r in dual for s, _ in r["only"])
    assert any(r["file"] == "Examples.lean" and max(e for _, e in r["only"]) <= len(lines) - 5 for r in dual)
    # S6, S7: kills through `viaGate`, in the outside file, and by the `rfl` check
    assert any(v[2] == "KILLED" and "Second.lean:" in v[4] for _, v in by("gate", "lt-le"))
    s6 = by("far", "lit-plus")
    assert s6 and all(v[2] == "KILLED" and "outside/Check.lean" in v[4] for _, v in s6), s6
    rfl = SEED_SECOND.split("\n").index("example : Demo.tag 1 = 2 := rfl") + 1
    assert any(r["file"] == "Second.lean" and any(s <= rfl <= e for s, e in r["only"]) for r in dual)


def test_probe_f1_a_check_module_outside_the_targets_gives_lazy_the_eager_verdicts(tmp_path_factory):
    """eff-20261108-1 F1 (real Lean): `Demo/Far/Mid` sits in `Demo.Defs`' cone and `Demo/Check` (a target) imports
    it, but no target names it (another directory, no statement names `inc`, no --deep), so it is outside the
    control `files`. Its failing `#guard` is read by `settle`: eager gives UNKNOWN (no control), and lazy must give
    the same rows, not a KeyError in a worker that loses every verdict of the run."""
    root = tmp_path_factory.mktemp("f1") / "p"
    root.mkdir()
    scaffold(root, "Far")
    for name, text in (("Defs", "namespace Demo\n\ndef inc (n : Nat) : Nat := n + 1\n\nend Demo\n"),
                       ("Far/Mid", "import Demo.Defs\n#guard Demo.inc 1 == 2\n"),
                       ("Check", "import Demo.Far.Mid\n#guard Demo.inc 0 == 1\n")):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    dump(root, tmp_path_factory.mktemp("f1-dump"), [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    got = {}
    for mode in ("eager", "lazy"):
        done, mutants = tool(root, tmp_path_factory.mktemp(f"f1-{mode}"), "--control-probes", mode)
        assert "Traceback" not in done.stderr, done.stderr[-3000:]
        got[mode] = [(m["id"], m["status"], m["raw_status"], m["detail"]) for m in mutants]
    assert got["eager"] and got["lazy"] == got["eager"], got
    assert all(s == "UNKNOWN" and "Far/Mid.lean" in d and "could not elaborate" in d for _, s, _, d in got["lazy"])
