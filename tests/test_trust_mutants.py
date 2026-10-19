"""tools/trust_mutants.py on a tiny Lean package (speed-trustmut step 3): a well-guarded definition has no survivor,
a guard over `[]` leaves survivors, a failing proof is no kill, --allow suppresses exactly its operator, the mutants
are built in a scratch copy (the checkout's bytes and times are unchanged), and --max-mutants lists the rest as
NOT RUN. The package's declaration and predicate lists come from tools/lean_statements.py's own per-module script."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys

import pytest

from subprocesses import HANG_TIMEOUT

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lake_outputs  # noqa: E402
import lean_statements  # noqa: E402

PATH = {"PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}

DEFS = """namespace Demo

/-- Guarded on both sides of its bound. -/
def small (n : Nat) : Bool := n < 3

/-- Guarded over `[]` only. -/
def evens (xs : List Nat) : List Nat := xs.filter (· % 2 == 0)

/-- No guard reads it; three proofs do, one of them a theorem whose statement names it. -/
def double (n : Nat) : Nat := n + n + 0

theorem double_eq (n : Nat) : double n = 2 * n := by unfold double; omega

/-- No guard reads it; two `example`s proved by tactics do. -/
def triple (n : Nat) : Nat := n + n + n + 0

example : triple 1 = 3 := by simp [triple]

/-- Read only by a `decide` check outside this directory whose statement names it. -/
def half (n : Nat) : Nat := n / 2

/-- Read only by tactic `example`s wrapped in `#guard_msgs` (review F6). -/
def quad (n : Nat) : Nat := n + n + n + n + 0

/-- Read only by checks wrapped in `#guard_msgs`: an `#eval` and a `decide` example. -/
def twice (n : Nat) : Nat := 2 * n

/-- Read only by a definition (no check): its error is UNKNOWN. -/
def lone (n : Nat) : Nat := n + 0

/-- Read by subtype definitions, and by checks of their values only (review F8): their errors are UNKNOWN. -/
def boxed (n : Nat) : Nat := n + 0

end Demo
"""
PROOFS = """import Demo.Defs

theorem Demo.four : (2 : Nat) + 2 = 4 := by
  have h : Demo.double 2 = 4 := by simp [Demo.double]
  omega

theorem Demo.double_two : Demo.double 2 = 4 := by simp [Demo.double]
"""
FAR = """import Demo.Defs

theorem Demo.Far.half_four : Demo.half 4 = 2 := by decide
"""
EXAMPLES = """import Demo.Defs
import Demo.Proofs
open Demo

#guard small 2
#guard !small 3
#guard evens [] == []

example : triple 2 = 6 := by simp [triple]

#guard_msgs in
example : quad 1 = 4 := by
  simp [quad]

#guard_msgs in example : quad 2 = 8 := by simp [quad]

/-- info: 6 -/
#guard_msgs (whitespace := lax) in
#eval twice 3

#guard_msgs in example : twice 2 = 4 := by decide

def loneFin : Fin 1 := ⟨lone 0, by decide⟩

def boxedEval : {x : Nat // boxed x = x} := ⟨0, by decide⟩

/-- info: 0 -/
#guard_msgs in
#eval boxedEval.val

def boxedGuard : {x : Nat // boxed x = x} := ⟨0, by decide⟩

#guard boxedGuard.val == 0

def boxedDecide : {x : Nat // boxed x = x} := ⟨0, by decide⟩

example : boxedDecide.val = 0 := by decide
"""
STATED = ["Demo.Far.half_four", "Demo.double_eq", "Demo.double_two", "Demo.four"]


def short(value) -> str:
    """A test id without spaces (tools/mutants.py reads failing ids up to the first space)."""
    return re.sub(r"[^\w#!]+", "-", str(value)).strip("-")[:40]


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, check=True,
                   capture_output=True, timeout=HANG_TIMEOUT)


def dump(root: Path, folder: Path, stated: list[str] = STATED) -> None:
    """lean/declarations.txt and lean/predicates.txt of the package, as tools/lean_statements.py writes them."""
    modules = lean_statements.tree_modules(root)
    subprocess.run([lake_outputs.lean_executable(None, "lake"), "build", *modules], cwd=root / "lean", check=True,
                   capture_output=True, timeout=HANG_TIMEOUT)
    lines = [line for m in modules for line in lean_statements.run_lean(
        root, folder, f"import Lean\nimport {m}\n" + lean_statements.ALONE, m.replace(".", "_"),
        {"VE_PREDICATE_MODULE": m, **PATH}).splitlines()]
    declarations, pending = [], []
    for line in lines:
        if line.startswith("declaration "):
            pending.append(line.removeprefix("declaration "))
        elif line.startswith("module "):
            m = line.removeprefix("module ")
            source = root / "lean" / (m.replace(".", "/") + ".lean")
            declarations += [f"module {m} {lean_statements.source_hash(source)}", *pending]
            pending = []
    (root / "lean/declarations.txt").write_text(lean_statements.DECLARATIONS_HEADER + "\n".join(declarations) + "\n")
    (root / "lean/predicates.txt").write_text(
        lean_statements.PREDICATES_HEADER + "".join(f"module {m}\n" for m in modules)
        + "".join(line.removeprefix("predicate ") + "\n" for line in lines if line.startswith("predicate ")))
    (folder / "names.txt").write_text("".join(f"{name}\n" for name in stated))
    script = lean_statements.SCRIPT.replace("import VE\n", "".join(f"import {m}\n" for m in modules))
    (root / "lean/statements.txt").write_text(lean_statements.HEADER + lean_statements.run_lean(
        root, folder, script, "Statements", {"VE_STATEMENT_NAMES": str(folder / "names.txt"), **PATH}))


def scaffold(root: Path, *folders: str) -> None:
    """An empty Lean package `Demo` at `root` with the folders under lean/Demo/, committed as the base."""
    for folder in folders:
        (root / "lean/Demo" / folder).mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (root / "lean/lakefile.toml").write_text('name = "demo"\n\n[[lean_lib]]\nname = "Demo"\nglobs = ["Demo.*"]\n')
    (root / ".gitignore").write_text(".lake/\n")
    (root / "tools/trust-classes.json").write_text('{"modules": {}}\n')
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("package")
    scaffold(root, "Far")
    for name, text in (("Defs", DEFS), ("Proofs", PROOFS), ("Examples", EXAMPLES), ("Far/Check", FAR)):
        (root / f"lean/Demo/{name}.lean").write_text(text)
    dump(root, tmp_path_factory.mktemp("dump"))
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return root


def tool(root: Path, scratch: Path, *args: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
    out = scratch / "evidence.json"
    scratch.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, **PATH, "TMPDIR": str(scratch), "VE_LEAN_SHARE": "off"}
    done = subprocess.run([sys.executable, str(ROOT / "tools/trust_mutants.py"), "--root", str(root), "--base",
                           "HEAD~1", "--jobs", "4", "--json", str(out), *args], env=env, capture_output=True,
                          text=True, timeout=HANG_TIMEOUT)
    return done, json.loads(out.read_text())["mutants"] if out.is_file() else []


def snapshot(root: Path) -> dict[str, tuple[bytes, int]]:
    return {p.relative_to(root).as_posix(): (p.read_bytes(), p.stat().st_mtime_ns)
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.relative_to(root).parts}


@pytest.fixture(scope="module")
def default_run(package, tmp_path_factory):
    before = snapshot(package)
    done, mutants = tool(package, tmp_path_factory.mktemp("run"))
    return done, mutants, before, snapshot(package)


def of(mutants: list[dict], name: str) -> list[dict]:
    return [m for m in mutants if m["definition"] == f"Demo.{name}"]


def test_a_well_guarded_definition_has_no_survivor(default_run):
    _, mutants, _, _ = default_run
    small = of(mutants, "small")
    assert {m["operator"] for m in small} >= {"lt-le", "lt-eq", "lit-plus", "lit-minus", "body-true", "body-false"}
    assert all(m["status"] == "KILLED" for m in small), small
    assert all(m["detail"].startswith("lean/Demo/Examples.lean:") for m in small)


def test_a_guard_over_the_empty_list_leaves_survivors(default_run):
    done, mutants, _, _ = default_run
    evens = of(mutants, "evens")
    survivors = [m for m in evens if m["status"] == "SURVIVOR"]
    assert {"list-empty", "list-first", "lit-plus", "eq-ne"} <= {m["operator"] for m in survivors}
    assert done.returncode == 1
    printed = [line for line in done.stdout.splitlines() if line.startswith("SURVIVOR ")]
    assert len(printed) == sum(m["status"] == "SURVIVOR" for m in mutants)
    assert "SURVIVOR lean/Demo/Defs.lean:7 Demo.evens list-empty: xs.filter (· % 2 == 0) -> []" in printed


def test_a_failing_proof_is_no_kill(default_run):
    """The mutant breaks `double_eq` in its own module, and `four` and `double_two` in another (review F1:
    `double_two`'s statement names `double`, and only its proof script fails); no check reads `double`."""
    _, mutants, _, _ = default_run
    (double,) = of(mutants, "double")
    assert (double["operator"], double["after"], double["status"]) == ("lit-plus", "1", "SURVIVOR")


def test_an_example_proved_by_a_tactic_is_no_kill(default_run):
    """Review F1: an `example` not proved by `decide`/`native_decide`/`rfl` is a proof, cut in the mutated module
    and in the module of its checks alike."""
    _, mutants, _, _ = default_run
    (triple,) = of(mutants, "triple")
    assert (triple["operator"], triple["after"], triple["status"]) == ("lit-plus", "1", "SURVIVOR")


def test_a_proof_wrapped_in_guard_msgs_is_no_kill(default_run):
    """Review F6 (PROBE F6): Lean reports a wrapped proof's failure at its `#guard_msgs` line, written alone or with
    the `example`; the wrapper is the proof's, and it is blanked with the cut (else the `sorry` warning trips it)."""
    _, mutants, _, _ = default_run
    (quad,) = of(mutants, "quad")
    assert (quad["operator"], quad["after"], quad["status"]) == ("lit-plus", "1", "SURVIVOR"), quad


def test_a_check_wrapped_in_guard_msgs_kills(default_run):
    """Review F6: a `#guard_msgs` around an `#eval` (its spec in parentheses) or a `decide` example is a check."""
    _, mutants, _, _ = default_run
    twice = of(mutants, "twice")
    assert {m["operator"] for m in twice} == {"lit-plus", "lit-minus"}
    assert all(m["status"] == "KILLED" and m["detail"].split(": ")[0] in (
        "lean/Demo/Examples.lean:18", "lean/Demo/Examples.lean:21") for m in twice), twice


def test_a_guard_msgs_wrapper_is_in_the_span_of_what_it_wraps(tmp_path):
    """Review F6: trust_map.scan opens a command at the `#guard_msgs … in` line before it, as at `set_option … in`,
    so the role of the line Lean reports is the wrapped command's."""
    import trust_map
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text("#guard f 1\n\n#guard_msgs in\nexample : f 1 = 2 := by\n  simp [f]\n\n/-- info: 2 -/\n"
                    "#guard_msgs (whitespace := lax) in\n#eval f 1\n")
    decls, _, problems = trust_map.scan(path, [])
    code = trust_mutants.code_only(path.read_text()).split("\n")
    assert problems == []
    assert [(d.start, d.end, trust_mutants.classify(d.kind, "\n".join(code[d.start - 1:d.end]))) for d in decls] == [
        (1, 2, "check"), (3, 7, "proof"), (8, 9, "check")]


@pytest.mark.parametrize(("text", "last", "cut"), [
    ("-- #guard_msgs in\n#guard_msgs in\nexample : f 1 = 2 := by\n  simp [f]\n#guard f 1\n", 4,
     "-- #guard_msgs in\n" + " " * 14 + "\nexample : f 1 = 2  := sorry\n\n#guard f 1\n"),
    ("#guard_msgs in example : f 1 = 2 := by simp [f]\n\n/-- info: 2\n-/\n#guard_msgs in\n#eval f 1\n", 4,
     " " * 15 + "example : f 1 = 2  := sorry\n\n/-- info: 2\n-/\n#guard_msgs in\n#eval f 1\n"),
    ("example : f 1 = 2 := by\n  simp [f] /- a\n  b -/\n-- c\n", 4, "example : f 1 = 2  := sorry\n\n\n-- c\n")],
    ids=short)
def test_a_cut_proof_loses_its_guard_msgs_wrapper_and_keeps_the_comments_after_it(tmp_path, text, last, cut):
    """Review F6: the cut blanks the wrapper (the `sorry` warning would fail it) and keeps the whole comments after
    the proof (the next `#guard_msgs`'s docstring is in the span before it), every line kept."""
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text(text)
    first = 2 if text.startswith("--") else 1
    assert trust_mutants.cut_proof(path, first, last)
    assert path.read_text() == cut


def test_an_error_outside_every_check_is_unknown(default_run):
    """Only an error in a check (or a --test file) kills: `loneFin`'s proof term fails under the mutant, and it is
    a definition, which cannot be cut."""
    _, mutants, _, _ = default_run
    (lone,) = of(mutants, "lone")
    assert (lone["status"], lone["detail"].split(": ")[0]) == ("UNKNOWN", "lean/Demo/Examples.lean:23"), lone


def test_an_error_in_a_definition_beside_a_failing_check_is_unknown(default_run):
    """Review F8: the mutant breaks the `by decide` of three subtype definitions; Lean puts `sorry` there, and the
    `#eval` of one's value refuses it (the value is 0 whatever `boxed` is). The control has no such break, so
    it passes; the definitions' errors still decide: UNKNOWN at the first, never a kill."""
    _, mutants, _, _ = default_run
    (boxed,) = of(mutants, "boxed")
    assert (boxed["status"], boxed["detail"].split(": ")[0]) == ("UNKNOWN", "lean/Demo/Examples.lean:25"), boxed


def test_a_decide_check_outside_the_directory_naming_the_definition_kills(default_run):
    _, mutants, _, _ = default_run
    half = of(mutants, "half")
    assert {m["operator"] for m in half} == {"lit-plus", "lit-minus"}
    assert all(m["status"] == "KILLED" and m["detail"].startswith("lean/Demo/Far/Check.lean:3:") for m in half), half


@pytest.mark.parametrize(("kind", "text", "role"), [
    ("command", "#guard f [] == []", "check"),
    ("command", "#guard_msgs in\n#eval f 1", "check"),
    ("command", "example : f 1 = 2 := by decide", "check"),
    ("command", "@[simp] example : f 1 = 2 :=\n  by native_decide", "check"),
    ("command", "example : f 1 = 2 := rfl", "check"),
    ("theorem", "theorem t : f 1 = 2 := by decide +kernel", "check"),
    ("command", "example (n : Nat) : f n = n := by\n  simp [f]", "proof"),
    ("command", "example (h : p) : q :=\n  t h", "proof"),
    ("command", "#guard_msgs in\nexample : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs in example : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs (drop warning) in\n@[simp] example : f 1 = 2 := by\n  simp [f]", "proof"),
    ("theorem", "#guard_msgs in\ntheorem t : f 1 = 2 := by simp [f]", "proof"),
    ("command", "#guard_msgs in example : f 1 = 2 := by decide", "check"),
    ("command", "#guard_msgs (whitespace := lax) in\n#eval f 1", "check"),
    ("command", "#guard_msgs in\n#guard f 1", "check"),
    ("command", "#guard_msgs (drop\n  info) in\n#eval f 1", "other"),
    ("command", "#guard_msgs", "other"),
    ("theorem", "theorem t : f [] = [] := by\n  simp [f]\n  rfl", "proof"),
    ("theorem", "theorem t : f [] = [] := by simp [f]; decide", "proof"),
    ("def", "def f (n : Nat) : Nat := n", "other"),
    ("command", "open Demo", "other")], ids=short)
def test_only_guards_and_decide_rfl_proofs_are_checks(kind, text, role):
    """Review F1 (and SupExtra.lean's and Status.lean's `example`s): an `example` or theorem is a check only when
    `decide`, `native_decide` or `rfl` proves it, whatever its statement names."""
    import trust_mutants
    assert trust_mutants.classify(kind, text) == role


def test_mutants_are_built_in_a_scratch_copy(default_run):
    _, mutants, before, after = default_run
    assert any(m["status"] == "KILLED" for m in mutants)
    assert after == before


def test_allow_suppresses_exactly_its_operator(package, tmp_path):
    allow = tmp_path / "allow.json"
    allow.write_text(json.dumps({"allow": [{"definition": "Demo.evens", "operator": "list-empty",
                                            "reason": "the fixture's guard is over [] by design"}]}))
    done, mutants = tool(package, tmp_path / "run", "--allow", str(allow))
    evens = of(mutants, "evens")
    allowed = [m for m in evens if m["status"] == "ALLOWED"]
    assert allowed and all(m["operator"] == "list-empty" for m in allowed)
    assert [m for m in evens if m["operator"] == "list-empty" and m["status"] != "ALLOWED"] == []
    assert all(m["status"] != "ALLOWED" for m in mutants if m["definition"] != "Demo.evens")
    assert any(m["status"] == "SURVIVOR" for m in evens) and done.returncode == 1
    assert " list-empty: " not in "".join(line for line in done.stdout.splitlines() if line.startswith("SURVIVOR"))


def test_an_outside_test_that_fails_without_the_mutant_is_no_kill(package, default_run, tmp_path):
    """Review F7: a --test file outside lean/ kills only when it passes without the mutant (its control). One whose
    `#eval` reads `double_eq`, which the tool cuts up front in Demo/Defs.lean, fails either way: the mutants no
    check kills are UNKNOWN, never KILLED; a mutant that breaks the other file is KILLED by it."""
    (package / "outside").mkdir(exist_ok=True)
    (package / "outside/Value.lean").write_text("import Demo.Defs\n#guard Demo.small 2\n#guard !Demo.small 3\n")
    (package / "outside/Reads.lean").write_text(
        "import Demo.Defs\n"
        "#eval (⟨0, Nat.lt_of_lt_of_eq (by decide) (Demo.double_eq 1).symm⟩ : Fin (Demo.double 1)).val\n")
    done, mutants = tool(package, tmp_path / "run", "--test", "outside/Value.lean", "--test", "outside/Reads.lean")
    before = {m["id"]: m["status"] for m in default_run[1]}
    assert [m for m in mutants if "Reads.lean" in m["detail"] and m["status"] != "UNKNOWN"] == [], done.stdout
    assert "SURVIVOR" in {before[m["id"]] for m in mutants if m["file"] == "Demo/Defs.lean"}
    for m in mutants:
        if before[m["id"]] == "SURVIVOR" and m["file"] == "Demo/Defs.lean":  # Reads.lean imports it only
            assert m["status"] == "UNKNOWN" and m["detail"].endswith("Reads.lean fails without the mutant too"), m
        else:
            assert m["status"] == before[m["id"]], m


@pytest.mark.parametrize("limit", [0, 3])
def test_max_mutants_lists_the_rest_as_not_run(package, tmp_path, limit):
    """A budget of 0 runs nothing and never exits 0 (3: incomplete)."""
    done, mutants = tool(package, tmp_path / "run", "--max-mutants", str(limit))
    ran = [m for m in mutants if m["status"] != "NOT RUN"]
    assert len(ran) == limit and len(mutants) > limit
    printed = [line for line in done.stdout.splitlines() if line.startswith("NOT RUN ")]
    assert len(printed) == len(mutants) - limit
    assert done.returncode == (1 if any(m["status"] == "SURVIVOR" for m in ran) else 3)


def test_the_generator_cuts_every_list_a_condition_reads():
    """The list positions of reviews ap-2 F7, F10 and F11 (a method's receiver, `for ... in`, a `++` operand), and
    the token operators; nothing inside a string literal is mutated."""
    import trust_mutants
    text = ('def ok (fs : List (List String)) (ms : List String) : Bool := Id.run do\n'
            '  for f in fs do\n    if (f.find? (· == "x<1")).isSome then return false\n'
            '  return fs.all (·.isEmpty) && (ms ++ ["y"]).length < 3\n')
    found = {(op, text[s:e], new) for op, s, e, new in trust_mutants.mutants(text, "def", 0, len(text))}
    assert {("list-drop-first", "f", "(f.drop 1)"), ("list-drop-last", "fs", "(fs.dropLast)"),
            ("list-first", "ms", "(ms.take 1)"), ("append-left", ' ++ ["y"]', ""), ("lt-le", "<", "≤"),
            ("lit-plus", "3", "4"), ("all-any", "all", "any"), ("and-or", "&&", "||"),
            ("bool-flip", "false", "true")} <= found
    literal = text.index('"x<1"')
    assert not [m for m in trust_mutants.mutants(text, "def", 0, len(text)) if literal <= m[1] < literal + 5]


# Review F7's truth table: every command form `classify` can see, its class, and two readings of a definition: its
# value (`{v}`, which a check must catch) and a proof the tool cuts (`{p}`, through the witness `{w}`: up front in
# the mutated module, when the mutant breaks it in another). An outcome a cut or broken proof can change must never
# be a kill. `None`: the form has no proof reading of its own (its tactic block is the proof it reads).
FORMS = [  # (form, class, value reading, proof reading, the value reading's mutants: see `table_rows`)
    ("#guard", "check", "#guard {v} == {e}", "#guard {w}.val == 0", "KILLED"),
    # Review F11: definitional equality fails alike when the two sides differ and when a reduction got stuck.
    ("#guard_expr", "check", "#guard_expr {v} =~ {e}", "#guard_expr {w}.val =~ 0", "UNKNOWN"),
    # Review F11: the message an `#eval` throws is the file's own, no refutation Lean states.
    ("#eval", "check", '#eval (do if {v} != {e} then throw (IO.userError "changed") : IO Unit)', "#eval {w}.val",
     "UNKNOWN"),
    # Review F11: an `#eval`'s value under its docstring is an answer Lean computed.
    ("#eval value", "check", "#eval {v}", None, "doc KILLED"),
    # Review F11: `#reduce` prints a stuck term as readily as a value, so its docstring compares no answer.
    ("#reduce", "check", "#reduce {v}", "#reduce {w}.val", "doc UNKNOWN"),
    ("#check", "check", "#check (rfl : {v} = {e})", "#check {w}", "UNKNOWN"),
    ("#print", "proof", "#print {d}", "#print {p}", "SURVIVOR"),
    ("#print axioms", "proof", "#print axioms {d}", "#print axioms {p}", "SURVIVOR"),
    ("decide example", "check", "example : {v} = {e} := by decide", "example : {w}.val = 0 := by decide", "KILLED"),
    # Review F11: `rfl`'s failure kills only when `decide` (or `native_decide`) then refutes the statement.
    ("rfl example", "check", "example : {v} = {e} := rfl", "example : {w}.val = 0 := rfl", "KILLED"),
    ("tactic example", "proof", "example : {v} = {e} := by {tac}", "example : {w}.val = 0 := by {tac}", "SURVIVOR"),
    ("tactic theorem", "proof", "theorem {id}_t : {v} = {e} := by {tac}", "theorem {id}_t : {w}.val = 0 := by {tac}",
     "SURVIVOR"),
    ("#guard with a tactic block", "proof", "#guard (⟨0, by {tac}⟩ : Fin (2 - {n})).val == 0", None, "SURVIVOR"),
    # Review F8's form (the recheck's missing row): a definition with a proof inside it, and a check of its value
    # (0 whatever the definition is) beside it. The mutant breaks the proof: an error in a definition, UNKNOWN.
    ("definition with a proof", "other", "def {id}_s : {{x : Nat // x = 0 ∧ {v} = {e}}} := ⟨0, by decide⟩\n"
     "#guard {id}_s.val == 0", "def {id}_s : Fin ({n}) := {w}\n#guard {id}_s.val == 0", "UNKNOWN"),
]
WRAPS = ("bare", "wrapped", "doc")  # the command alone, under `#guard_msgs in`, and with its docstring too
# A definition's type and body, its values on 0..5, its value at 1, that value as a size `{n}` and the proof `{p}`
# (`{d} 1 = {one}`) turned into `1 = {n}`.
SIMPLE = {"type": "Nat", "body": "n + 0", "e": "[0, 1, 2, 3, 4, 5]", "one": "1", "n": "{d} 1",
          "one_eq": "{p}.symm"}  # one mutant: lit-plus
RICH = {"type": "Bool", "body": "!(n < 1) && (n ≤ 3 || decide (n = 5)) && n != 2 && ([n] ++ [1]).all (· ≥ 1) && "
        "[n, 3].any (· == 3) && true", "e": "[false, true, false, true, false, true]", "one": "true",
        "n": "({d} 1).toNat", "one_eq": "(congrArg Bool.toNat {p}).symm"}  # the sweep's: every operator but the arms


def table_rows(group: bool = True) -> list[dict]:
    """One row per form, reading, wrapping and setting, with the status its definition's mutants must have: a cut
    proof's reading is SURVIVOR; the value's is the form's (FORMS; "doc X": X with its docstring, else SURVIVOR,
    since a bare or info-dropping command compares nothing): KILLED when a check states a refutation of it,
    UNKNOWN when the check fails stating none, or when a command that is no check reads it (review F11: every
    error that is no refutation). With `group`, the rows that must survive share one definition per wrapping,
    setting and reading."""
    rows = []
    for setting in ("mutated", "other"):
        for wrap in WRAPS:
            for reads in ("value", "proof"):
                for form, cls, value, proof, verdict in FORMS:
                    if (text := value if reads == "value" else proof) is not None:
                        expected = "SURVIVOR" if reads == "proof" else verdict.split()[-1] if wrap == "doc" or \
                            not verdict.startswith("doc ") else "SURVIVOR"
                        rows.append({"form": form, "class": cls, "reads": reads, "wrap": wrap, "setting": setting,
                                     "expected": expected, "text": text,
                                     "key": (setting, wrap, reads, form if expected != "SURVIVOR" or not group
                                             else "")})
    names: dict[tuple, str] = {}
    for i, row in enumerate(rows):
        row["d"], row["id"] = names.setdefault(row["key"], f"r{len(names)}"), f"x{i}"
    return rows


def table_package(root: Path, folder: Path, rich: bool = False, group: bool = True) -> list[dict]:
    """The table as a Lean package at `root` (committed over an empty base): Demo/M/Defs.lean holds the mutated
    setting (definitions, proofs and readings in one module), Demo/O/Defs.lean the other setting's definitions and
    Demo/O/Checks.lean their proofs and readings. Each row's docstring is the messages Lean gives its bare command."""
    mode = RICH if rich else SIMPLE
    rows = table_rows(group)
    scaffold(root, "M", "O")
    files = {"mutated": "Demo/M/Defs.lean", "other": "Demo/O/Checks.lean"}

    def write(messages: dict[tuple[str, int], list[str]] | None) -> None:
        texts = {"Demo/M/Defs.lean": ["namespace Demo.M", ""], "Demo/O/Defs.lean": ["namespace Demo.O", ""],
                 "Demo/O/Checks.lean": ["import Demo.O.Defs", "", "namespace Demo.O", ""]}
        seen = set()
        for row in rows:
            d, lines = row["d"], texts[files[row["setting"]]]
            if d not in seen:
                seen.add(d)
                texts["Demo/M/Defs.lean" if row["setting"] == "mutated" else "Demo/O/Defs.lean"] += [
                    f"def {d} (n : Nat) : {mode['type']} := {mode['body']}", ""]
                if row["reads"] == "proof":
                    lines += [f"theorem {d}_p : {d} 1 = {mode['one']} := by exact (by decide)", ""]
            size, one_eq = mode["n"].format(d=d), mode["one_eq"].format(p=f"{d}_p")
            command = row["text"].format(d=d, id=row["id"], p=f"{d}_p", v=f"(List.range 6).map {d}", e=mode["e"],
                                         tac="exact (by decide)", n=size,
                                         w=f"(⟨0, Nat.lt_of_lt_of_eq Nat.zero_lt_one {one_eq}⟩ : Fin ({size}))")
            said = [] if messages is None else messages[files[row["setting"]], row["line"]]
            if messages is None or row["wrap"] == "bare":
                row["line"] = len(lines) + 1
                lines += [*command.split("\n"), ""]
                continue
            if row["wrap"] == "doc":
                lines += ["/--", *"\n---\n".join(said).split("\n"), "-/"] if said else ["/-- -/"]
            row["line"] = len(lines) + 2
            lines += ["#guard_msgs (drop info) in" if said and row["wrap"] == "wrapped" else "#guard_msgs in",
                      *command.split("\n"), ""]
        for name, lines in texts.items():
            (root / "lean" / name).write_text("\n".join([*lines, f"end Demo.{name.split('/')[1]}", ""]))

    write(None)
    lake = lake_outputs.lean_executable(None, "lake")
    subprocess.run([lake, "build", "Demo.O.Defs"], cwd=root / "lean", check=True, capture_output=True,
                   timeout=HANG_TIMEOUT, env={**os.environ, **PATH})
    messages: dict[tuple[str, int], list[str]] = {}
    for name in set(files.values()):
        done = subprocess.run([lake, "env", "lean", "--json", name], cwd=root / "lean", capture_output=True, text=True,
                              timeout=HANG_TIMEOUT, env={**os.environ, **PATH})
        for line in done.stdout.splitlines():
            said = json.loads(line)
            assert said["severity"] == "information", said  # the bare table builds cleanly
            messages.setdefault((name, said["pos"]["line"]), []).append(f"info: {said['data'].rstrip()}")
    for row in rows:
        messages.setdefault((files[row["setting"]], row["line"]), [])
    write(messages)
    helpers: dict[str, list[str]] = {}  # the rows' own definitions are test helpers (T), never mutated
    for row in rows:
        if row["text"].startswith("def "):
            name = files[row["setting"]]
            helpers.setdefault(name, []).append(f"Demo.{name.split('/')[1]}.{row['id']}_s")
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": {f: {"T": n} for f, n in helpers.items()}}))
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return rows


@pytest.mark.parametrize("wrap", WRAPS)
@pytest.mark.parametrize(("form", "cls", "value", "proof", "verdict"), FORMS,
                         ids=[f[0].replace(" ", "-") for f in FORMS])
def test_classify_truth_table(form, cls, value, proof, verdict, wrap):
    """Review F7: each form's class is the same bare, under `#guard_msgs in` and with a docstring too; a check form
    with a tactic block in it is a proof."""
    import trust_mutants
    for text in (value, proof):
        if text is None:
            continue
        command = text.format(d="f", id="t", p="f_p", v="f 1", e="1", tac="simp [f]", w="(⟨0, f_p⟩ : Fin 2)", n="f 1")
        span = {"bare": command, "wrapped": f"#guard_msgs (drop info) in\n{command}",
                "doc": f"/-- info: 1 -/\n#guard_msgs in\n{command}"}[wrap]
        code = trust_mutants.code_only(span)
        assert trust_mutants.classify("theorem" if form == "tactic theorem" else "command", code) == cls, span


@pytest.mark.parametrize(("text", "cls"), [
    ("#eval! f 1", "check"),
    ("set_option maxRecDepth 100 in\n#eval f 1", "check"),
    ("#guard_msgs in\nset_option maxRecDepth 100 in\n#reduce f 1", "check"),
    ("#eval (⟨0, by simp⟩ : Fin 2)", "proof"),
    ("#guard_msgs in\n#check (by simp : f 1 = 1)", "proof"),
    ("#reduce (⟨0, by decide⟩ : Fin 2)", "proof"),
    ("#print axioms f", "proof"),
    ("#guard_msgs in\n#guard_msgs in\n#print f", "proof"),
    ("#synth Inhabited Nat", "other"),
    ("#check_failure f true", "other"),
    ("#exit", "other"),
    ("example : (⟨0, by simp⟩ : Fin 2).val = 0 := by decide", "proof"),
    ("example : f 1 = 1 := by exact (by decide)", "proof")], ids=short)
def test_classify_reads_every_command(text, cls):
    """Review F7: a check form with a tactic block anywhere in it is a proof; `#print` in any spelling is a proof;
    a command that is none of the check forms is other (an error there is no kill)."""
    import trust_mutants
    assert trust_mutants.classify("command", trust_mutants.code_only(text)) == cls


def test_every_hash_command_opens_its_own_span(tmp_path):
    """Review F7: trust_map opens a span at every `#` command, so `classify` sees the command Lean reports."""
    import trust_map
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text("theorem t : True := by\n  trivial\n#check_failure f true\n#guard_expr f 1 =~ 1\n#eval! f 1\n"
                    "def g : Array Nat :=\n  #[1, 2]\n")
    decls, _, problems = trust_map.scan(path, [])
    code = trust_mutants.code_only(path.read_text()).split("\n")
    assert [(d.start, d.end, trust_mutants.classify(d.kind, "\n".join(code[d.start - 1:d.end])))
            for d in decls if d.kind == "command"] == [(3, 3, "other"), (4, 4, "check"), (5, 5, "check")]
    assert [(d.start, d.end) for d in decls if d.kind != "command"] == [(1, 2), (6, 7)]  # `#[` is a term


@pytest.mark.parametrize(("text", "first", "last", "cut"), [
    ("#guard f 1\n/-- info: 1\n-/\n#guard_msgs in\n#eval f 1\n-- c\n", 4, 6,
     "#guard f 1\n" + " " * 11 + "\n  \n" + " " * 14 + "\n" + " " * 9 + "\n-- c\n"),
    ('#eval "a\n-- b"\n#guard_msgs in #print axioms f\n', 3, 3, '#eval "a\n-- b"\n' + " " * 30 + "\n")], ids=short)
def test_a_cut_command_is_blanked_with_its_docstring(tmp_path, text, first, last, cut):
    """Review F7: a `#` command is cut whole, with the comment lines before it (its `#guard_msgs` docstring), but
    never a string the command before it is still writing; every line is kept."""
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text(text)
    assert trust_mutants.cut_proof(path, first, last)
    assert path.read_text() == cut


@pytest.fixture(scope="module")
def table_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("table")
    rows = table_package(root, tmp_path_factory.mktemp("table-dump"))
    done, mutants = tool(root, tmp_path_factory.mktemp("table-run"), "--max-mutants", "1000")
    return root, rows, done, mutants


def test_the_truth_table_classes(table_run):
    """Review F7: the role the tool gives each row's command, on the package's own spans (docstrings and wrappers
    in place), is the table's class."""
    import trust_mutants
    root, rows, _, _ = table_run
    _, tree, fatal = trust_mutants.plan(root, "HEAD~1")
    assert fatal == []
    module = {"mutated": "Demo/M/Defs.lean", "other": "Demo/O/Checks.lean"}
    m = trust_mutants.Mutant("M", "Demo/O/Defs.lean", 1, "Demo.O.r0", "lit-plus", 0, 0, (1, 1), "", "")
    assert [trust_mutants.role(tree, module[r["setting"]], r["line"], m) for r in rows] == [r["class"] for r in rows]


def test_the_truth_table_statuses(table_run):
    """Review F7 (the DRI's table): in the mutated module (its proofs cut up front) and in another (a proof the
    mutant breaks is cut there), whether the reading is the value or a cut proof, bare, wrapped or with a
    docstring: a check that compares the value kills, and nothing a cut or broken proof can change ever does; a
    definition whose proof the mutant breaks is UNKNOWN at its own line, whatever check fails beside it (F8)."""
    _, rows, done, mutants = table_run
    module = {"mutated": "lean/Demo/M/Defs.lean", "other": "lean/Demo/O/Checks.lean"}
    space = {"mutated": "Demo.M", "other": "Demo.O"}
    statuses = {m["definition"]: (m["status"], m["detail"].split(": ")[0]) for m in mutants}
    assert len(statuses) == len(mutants) == len({(r["setting"], r["d"]) for r in rows}), done.stdout
    for row in rows:
        status, where = statuses[f"{space[row['setting']]}.{row['d']}"]
        lines = range(row["line"] - (row["wrap"] != "bare"), row["line"] + 1)  # the wrapper's or the command's
        places = [f"{module[row['setting']]}:{n}" for n in lines] if row["expected"] != "SURVIVOR" else [""]
        assert status == row["expected"] and where in places, (row, done.stdout)


ARMS = "def f : Nat → List Nat\n  | 0 => [1]\n  | _ => [2,\n   3]"


@pytest.mark.parametrize(("decl", "rest", "before", "new", "mutated"), [
    ("def f :=\n  [1,\n   2]", "\n\n#guard f == [1, 2]\n", "[1,\n   2]", "[]",
     "def f :=\n  []\n\n\n#guard f == [1, 2]\n"),
    (ARMS, "\n\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]",
     "def f : Nat → List Nat\n  | 0 => [2,\n   3]\n  | _ => [2,\n   3]\n#guard f 1 == [2, 3]\n"),
    (ARMS, "\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]", None),
    (ARMS, " /-\n\n-/\n#guard f 1 == [2, 3]\n", "[1]", "[2,\n   3]", None)],
    ids=("fewer", "more", "more-no-blank", "more-blank-in-a-comment"))
def test_an_edit_keeps_every_line_after_its_declaration(decl, rest, before, new, mutated):
    """Review F9: a shorter replacement is padded; a longer one takes its extra line ends from the blank lines right
    after the declaration (never from a comment), else it is written as it is (`mutated` None) and `moved` finds
    the first line it moved, which `run` reports as UNKNOWN."""
    import trust_mutants
    text, s = decl + rest, decl.index(before)
    end, edit = trust_mutants.relined(text, s, s + len(before), new, len(decl))
    after = text[:s] + edit + text[end:]
    assert after == (mutated or text[:s] + new + text[s + len(before):])
    lines = (1, max(decl.count("\n") + 1, text.count("\n", 0, end)))
    assert trust_mutants.moved(text, after, lines) == (None if mutated else decl.count("\n") + 2)


@pytest.mark.parametrize(("after", "lines", "line"), [
    ("def f := [1,\n  2]\n#guard f == [1]\n#guard g\n", (1, 2), 3),
    ("def f := [1,\n  2]\n#guard f == [1]\n#guard g\n", (1, 1), 2),
    ("def f := [2]\n#guard f == [1]\n\n#guard g\n", (1, 1), None),
    ("def f := [1]\n#guard f == [1]\n\n#guard g", (1, 1), 5)], ids=("count-kept", "own-line", "same", "count"))
def test_moved_finds_the_first_line_after_the_declaration_that_moved(after, lines, line):
    """Review F9: `moved` compares each line outside the mutated declaration, not only the line count (an edit that
    took a blank line below a check keeps the count and moves the check)."""
    import trust_mutants
    assert trust_mutants.moved("def f := [1]\n#guard f == [1]\n\n#guard g\n", after, lines) == line


REFUTE = "Expression\n  f 1 == 2\ndid not evaluate to `true`"


@pytest.mark.parametrize(("message", "role", "built", "checkout", "verdict"), [
    (REFUTE, "check", "#guard f 1 == 2", "#guard f 1 == 2", "KILL"),
    ("unexpected token '<;>'; expected command", "check", "  <;> trivial", "#guard f 1 == 2", "UNKNOWN"),
    ("unexpected token '<;>'; expected command", "check", "#guard f 1 == 2", "#guard f 1 == 2", "UNKNOWN"),
    ("expected term", "check", "#guard f 1 == 2", "#guard f 1 == 2", "UNKNOWN"),
    (REFUTE, "check", "  <;> trivial", "#guard f 1 == 2", "UNKNOWN"),
    (REFUTE, "check", "", "", "UNKNOWN"),
    ("Tactic `decide` proved that the proposition\n  f 1 = 2\nis false", "other", "def s := ⟨0, by decide⟩",
     "def s := ⟨0, by decide⟩", "UNKNOWN"),
    ("Tactic `decide` proved that the proposition\n  f 1 = 2\nis false", "proof", "  constructor <;> decide",
     "  constructor <;> decide", "UNKNOWN"),
    (REFUTE, "other", "#guard g", "#guard g", "UNKNOWN"),
    ("unexpected end of input", "other", "#guard g", "#guard g", "UNKNOWN")], ids=short)
def test_only_a_checks_own_error_kills(message, role, built, checkout, verdict):
    """Review F9 (the DRI's step 2) under F11's rule: an error kills only at a check line the mutant and the cuts
    left as the checkout has it, never when Lean's parser reports it (a cut left behind, a moved line), and never
    outside a check, whatever it says (a `decide` inside a tactic proof refutes a goal the tactics made)."""
    import trust_mutants
    assert trust_mutants.judge(message, role, built, checkout, "#guard f 1 == 2") == verdict


GUARD = "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n"
# Review F11, the rule inverted: one row per message form at a check's own line, the check's code, and the verdict.
# KILL only when the message states a refutation; RFL when an `rfl` check failed (`settle` asks `decide` and
# `native_decide`); every other row is a safe case, UNKNOWN.
JUDGED = [
    ("decide-false", "Tactic `decide` proved that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by decide", "KILL"),
    ("native-false", "Tactic `native_decide` evaluated that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by native_decide", "KILL"),
    ("guard-false", REFUTE, "#guard f 1 == 2", "KILL"),
    ("eval-value-differs", GUARD + "- info: 5\n+ info: 4", "/-- info: 5 -/\n#guard_msgs in\n#eval f 3", "KILL"),
    ("eval-lines-differ", GUARD + "  info: 1\n- ---\n- info: 2\n+ 3", "#guard_msgs in\n#eval f", "KILL"),
    ("guard-under-guard-msgs", GUARD + "-\n+ error: Expression\n+   f 1 == 2\n+ did not evaluate to `true`",
     "#guard_msgs in\n#guard f 1 == 2", "KILL"),
    ("decide-under-guard-msgs", GUARD + "-\n+ error: Tactic `decide` proved that the proposition\n+   f 1 = 2\n"
     "+ is false", "#guard_msgs in example : f 1 = 2 := by decide", "KILL"),
    ("rfl-term", "Type mismatch\n  rfl\nhas type\n  ?m.7 = ?m.7\nbut is expected to have type\n  f 3 = 5",
     "example : f 3 = 5 := rfl", "RFL"),
    ("rfl-tactic", "Tactic `rfl` failed: The left-hand side\n  f 3\nis not definitionally equal to the right-hand "
     "side\n  5", "theorem t : f 3 = 5 := by\n  rfl", "RFL"),
    ("rfl-under-guard-msgs", GUARD + "-\n+ error: Type mismatch\n+   rfl", "#guard_msgs in\nexample : f 3 = 5 := rfl",
     "RFL"),
    ("rfl-out-of-budget", "maximum recursion depth has been reached", "example : f 3 = 5 := rfl", "RFL"),
    # The safe cases: each is UNKNOWN.
    ("rfl-shape-in-a-decide-check", "Type mismatch\n  rfl\nhas type", "example : f 3 = 5 := by decide", "UNKNOWN"),
    ("guard-expr-defeq", "Failed: `f 3` is not definitionally equal to `5`", "#guard_expr f 3 =~ 5", "UNKNOWN"),
    ("check-rfl", "Type mismatch\n  rfl\nhas type", "#check (rfl : f 3 = 5)", "UNKNOWN"),
    ("eval-throws", "changed", '#eval (do if f 3 != 5 then throw (IO.userError "changed") : IO Unit)', "UNKNOWN"),
    ("reduce-info-differs", GUARD + "- info: 0\n+ info: Acc.rec\n+   (fun x₁ h ih =>", "/-- info: 0 -/\n"
     "#guard_msgs in\n#reduce g 4", "UNKNOWN"),
    ("check-info-differs", GUARD + "- info: f 3 : Nat\n+ info: f 4 : Nat", "/-- info: f 3 : Nat -/\n#guard_msgs in\n"
     "#check f 3", "UNKNOWN"),
    ("eval-info-quotes-budget", GUARD + "- info: 3\n+ info: [Error pretty printing: maximum recursion depth has been "
     "reached", "/-- info: 3 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("eval-budget-error", GUARD + "- info: 3\n+ error: maximum recursion depth has been reached",
     "/-- info: 3 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("expected-budget-error", GUARD + "- error: maximum recursion depth has been reached\n+ info: 3",
     "/-- error: maximum recursion depth has been reached -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("eval-warning", GUARD + "- info: 3\n+ warning: declaration uses 'sorry'\n+ info: 3", "#guard_msgs in\n#eval f 3",
     "UNKNOWN"),
    ("no-diff", GUARD + "info: 4", "/-- info: 5 -/\n#guard_msgs in\n#eval f 3", "UNKNOWN"),
    ("refutation-with-more", "Tactic `decide` proved that the proposition\n  f 1 = 2\nis false\nNote: more",
     "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("refutation-quoted", "note: Tactic `decide` proved that the proposition\n  f 1 = 2\nis false",
     "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("decide-stuck", "Tactic `decide` failed for proposition\n  f 1 = 2\nbecause its `Decidable` instance\n"
     "  instDecidableEqNat (f 1) 2\ndid not reduce to `isTrue` or `isFalse`.", "example : f 1 = 2 := by decide",
     "UNKNOWN"),
    ("unsolved-goals", "unsolved goals\n⊢ False", "example : f 1 = 2 := by decide", "UNKNOWN"),
    ("unclassified", "something Lean 4.25 may say", "#guard f 1 == 2", "UNKNOWN"),
]


@pytest.mark.parametrize(("name", "message", "span", "verdict"), JUDGED, ids=[j[0] for j in JUDGED])
def test_a_check_kills_only_when_its_message_states_a_refutation(name, message, span, verdict):
    """Review F11 (the DRI's note 2026-10-19c, step 1): KILL needs a message that states a refutation (`REFUTED`,
    whole, or a `#guard_msgs` diff between answers: an `#eval`'s value or a refutation); an `rfl` check is RFL (its
    message is the same when the reduction got stuck); every other message is UNKNOWN, one test each."""
    import trust_mutants
    line = span.split("\n")[-1]
    assert trust_mutants.judge(message, "check", line, line, trust_mutants.code_only(span)) == verdict


@pytest.mark.parametrize(("text", "first", "last", "tactic", "after"), [
    ("example : f 3 = 5 := rfl\n#guard g\n", 1, 1, "decide", "example : f 3 = 5 := by decide\n#guard g\n"),
    ("#guard g\ntheorem t : f 3 = 5 := by\n  rfl -- c\n#guard h\n", 2, 3, "native_decide",
     "#guard g\ntheorem t : f 3 = 5 := by native_decide\n -- c\n#guard h\n"),
    ("#guard_msgs in\nexample : f 3 = 5 := rfl\n", 1, 2, "decide", "#guard_msgs in\nexample : f 3 = 5 := by decide\n"),
    ("example : f 3 = 5 := by decide\n", 1, 1, "decide", "example : f 3 = 5 := by decide\n")], ids=short)
def test_decided_rewrites_only_the_rfl_and_keeps_every_line(text, first, last, tactic, after):
    """Review F11: the follow-up asks `decide` (or `native_decide`) of the `rfl` check's own statement, in place."""
    import trust_mutants
    assert trust_mutants.decided(text, first, last, tactic) == after


DEFINITION = "def bS : {n : Nat // n + 0 = n} := ⟨3, by simp (config := { maxSteps := 9 })⟩ + (by exact 1)\n"
# Review F12, the rule inverted for INVALID: the message an error in the mutated declaration gives, whether it is
# inside a tactic block there, and the verdict. INVALID only when Lean refused the text; every other row is UNKNOWN.
REFUSALS = [
    ("parse", "unexpected token ']'; expected term", False, "INVALID"),
    ("parse-in-tactic", "unexpected token '<;>'; expected command", True, "INVALID"),
    ("unknown-identifier", "Unknown identifier `A`", False, "INVALID"),
    ("unknown-constant", "Unknown constant `VE.Cardinality.Body.all`", False, "INVALID"),
    ("invalid-field", "Invalid field `take`: The environment does not contain `Option.take`", False, "INVALID"),
    ("invalid-projection", "Invalid projection: Type of", False, "INVALID"),
    ("invalid-pattern", "Invalid pattern", False, "INVALID"),
    ("synthesize", "failed to synthesize\n  LE Bool", False, "INVALID"),
    ("implicit", "don't know how to synthesize implicit argument `α`", False, "INVALID"),
    ("missing-cases", "Missing cases:\n(Nat.succ _)", False, "INVALID"),
    # The safe cases: each is UNKNOWN.
    ("simp-steps", "`simp` failed: maximum number of steps exceeded", True, "UNKNOWN"),
    ("unsolved-goals", "unsolved goals\n⊢ 4 + 0 = 4", True, "UNKNOWN"),
    ("omega", "omega could not prove the goal:", True, "UNKNOWN"),
    ("decide-stuck", "Tactic `decide` failed for proposition", True, "UNKNOWN"),
    ("decide-false", "Tactic `decide` proved that the proposition\n  4 = 3\nis false", True, "UNKNOWN"),
    ("name-in-tactic", "Unknown identifier `A`", True, "UNKNOWN"),
    ("type-mismatch", "Type mismatch\n  \"a\"\nhas type\n  String", False, "UNKNOWN"),
    ("rfl-stuck", "Application type mismatch: The argument\n  rfl\nhas type\n  ?m.10 = ?m.10", False, "UNKNOWN"),
    ("termination", "fail to show termination for\n  Demo.h3", False, "UNKNOWN"),
    ("recursion", "maximum recursion depth has been reached", False, "UNKNOWN"),
    ("heartbeats", "(deterministic) timeout at `whnf`, maximum number of heartbeats (200000) has been reached",
     False, "UNKNOWN"),
    ("unclassified", "something Lean 4.25 may say", False, "UNKNOWN"),
]


@pytest.mark.parametrize(("name", "message", "inside", "verdict"), REFUSALS, ids=[r[0] for r in REFUSALS])
def test_invalid_only_when_lean_refuses_the_mutated_text(name, message, inside, verdict):
    """Review F12 (the DRI's note, step 1): an error in the mutated declaration is INVALID only when Lean refused its
    text (a parse error, or a name, field, pattern or instance error outside its tactic blocks); a tactic that
    fails, Lean's budget, a type mismatch (a false or stuck proof term gives one too) and anything else are
    UNKNOWN, which counts toward the exit code."""
    import trust_mutants
    assert ("INVALID" if trust_mutants.refused(message, inside) else "UNKNOWN") == verdict


@pytest.mark.parametrize(("token", "inside"), [("simp", True), ("maxSteps", True), ("⟨3", False), ("bS", False),
                                               ("+ (", False), ("exact", True), ("1)", True), ("n + 0", False)])
def test_in_tactic_reads_each_tactic_block_to_its_bracket(token, inside):
    """Review F12: a tactic block runs from its `by` to the end of the bracket group it is in."""
    import trust_mutants
    code = trust_mutants.code_only(DEFINITION)
    assert trust_mutants.in_tactic(code, DEFINITION.index(token), 0, len(DEFINITION)) is inside


# Review F9's axis: an operator whose replacement can span lines, with fewer, the same or more lines than what it
# replaces; each definition is followed by a tactic proof over three lines (cut up front in the mutated module: a
# cut at moved lines leaves `<;> trivial` behind) and then by its check. `arm-true`/`arm-false` write one token and
# the list cuts and `append-*` one line or fewer, so only `arm-default` has "more". "tight": no blank line follows the
# definition, so the longer replacement cannot keep the lines after it, and the mutant is UNKNOWN.
LINES = [  # (shape, the definition after its name, what the reading check compares, [(operator, before, lines)])
    ("default-more", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2,\n      3]", "({d} 0, {d} 1) == ([7], [2, 3])",
     [("arm-default", "[7]", "more")]),
    ("default-more-tight", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2,\n      3]",
     "({d} 0, {d} 1) == ([7], [2, 3])", [("arm-default", "[7]", "more")]),
    ("default-fewer", " : Nat → List Nat\n  | 0 => [7,\n      8]\n  | _ => [2]", "({d} 0, {d} 1) == ([7, 8], [2])",
     [("arm-default", "[7,\n      8]", "fewer")]),
    ("default-same", " : Nat → List Nat\n  | 0 => [7]\n  | _ => [2]", "({d} 0, {d} 1) == ([7], [2])",
     [("arm-default", "[7]", "same")]),
    ("arm-bool", " : Nat → Bool\n  | 0 => 1 <\n      2\n  | _ => 2 < 1", "{d} 0 && !{d} 1",
     [("arm-false", "1 <\n      2", "fewer"), ("arm-true", "2 < 1", "same")]),
    ("list-multi", " (n : Nat) : List Nat := [n,\n    5]", "({d} 0, {d} 1) == ([0, 5], [1, 5])",
     [("list-first", "[n,\n    5]", "same"), ("list-drop-last", "[n,\n    5]", "same"),
      ("list-empty", "[n,\n    5]", "fewer")]),
    ("list-single", " (n : Nat) : List Nat := [n, 5]", "({d} 0, {d} 1) == ([0, 5], [1, 5])",
     [("list-first", "[n, 5]", "same"), ("list-drop-last", "[n, 5]", "same"), ("list-empty", "[n, 5]", "same")]),
    ("append-left-multi", " (n : Nat) : List Nat := [n] ++ [5,\n    6]", "{d} 0 == [0, 5, 6]",
     [("append-left", " ++ [5,\n    6]", "fewer"), ("append-right", "[n] ++ ", "same")]),
    ("append-right-multi", " (n : Nat) : List Nat := [n,\n    5] ++ [6]", "{d} 0 == [0, 5, 6]",
     [("append-right", "[n,\n    5] ++ ", "fewer"), ("append-left", " ++ [6]", "same")]),
]


def lines_package(root: Path, folder: Path) -> list[dict]:
    """The axis as a Lean package at `root` (committed over an empty base): each shape read by a check that compares
    it and by one that reads nothing (`#guard true`), in the mutated module (Demo/LM/Defs.lean) and in another
    (Demo/LO/Checks.lean, its definitions and proofs in Demo/LO/Defs.lean)."""
    scaffold(root, "LM", "LO")
    texts = {"LM/Defs": ["namespace Demo.LM", ""], "LO/Defs": ["namespace Demo.LO", ""],
             "LO/Checks": ["import Demo.LO.Defs", "", "namespace Demo.LO", ""]}
    rows = []
    for setting, defs, checks in (("mutated", "LM/Defs", "LM/Defs"), ("other", "LO/Defs", "LO/Checks")):
        for shape, body, compares, targets in LINES:
            for reads in (True, False):
                d = f"s{len(rows)}"
                texts[defs] += [*f"def {d}{body}".split("\n"), *([""] if not shape.endswith("tight") else []),
                                f"theorem {d}_ok : True := by", "  skip", "  <;> trivial"]
                rows.append({"shape": shape, "setting": setting, "reads": reads, "d": d, "targets": targets,
                             "file": f"lean/Demo/{checks}.lean", "line": len(texts[checks]) + 1,
                             "space": f"Demo.{checks.split('/')[0]}"})
                texts[checks] += [f"#guard {compares.format(d=d)}" if reads else "#guard true", ""]
    for name, lines in texts.items():
        (root / f"lean/Demo/{name}.lean").write_text("\n".join([*lines, f"end Demo.{name.split('/')[0]}", ""]))
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")
    return rows


@pytest.fixture(scope="module")
def lines_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("lines")
    rows = lines_package(root, tmp_path_factory.mktemp("lines-dump"))
    done, mutants = tool(root, tmp_path_factory.mktemp("lines-run"), "--max-mutants", "100000")
    return rows, done, mutants


def lines_problems(rows: list[dict], mutants: list[dict]) -> list[tuple]:
    """The rows of the line axis whose mutants break its rule (the test's and sweep.py's one reading of it): a
    target's lines are those the axis names and its status is KILLED under the check that compares the value,
    SURVIVOR under the one that reads nothing, UNKNOWN when it is longer and no blank line can take its lines; every
    other mutant is KILLED only by the comparing check at its line, UNKNOWN only as such a target, else SURVIVOR or
    INVALID."""
    problems = []
    for row in rows:
        mine = [m for m in mutants if m["definition"] == f"{row['space']}.{row['d']}"]
        tight = row["shape"].endswith("tight")
        for operator, before, lines in row["targets"]:
            found = [m for m in mine if (m["operator"], m["before"]) == (operator, before)]
            if len(found) != 1:
                problems.append((row, operator, before, "not one mutant", found))
                continue
            m = found[0]
            change = m["after"].rstrip("\n").count("\n") - before.count("\n")
            expected = "UNKNOWN" if tight and lines == "more" else "KILLED" if row["reads"] else "SURVIVOR"
            if not {"fewer": change < 0, "same": change == 0, "more": change > 0}[lines] or m["status"] != expected:
                problems.append((row, m, f"expected {expected} with {lines} lines"))
        for m in mine:
            allowed = {"KILLED": row["reads"] and m["detail"].startswith(f"{row['file']}:{row['line']}: "),
                       "UNKNOWN": tight and m["operator"] == "arm-default" and "moves this line" in m["detail"],
                       "SURVIVOR": True, "INVALID": True}
            if not allowed.get(m["status"]):
                problems.append((row, m))
    return problems


def test_a_replacement_of_any_line_count_is_decided_by_the_checks(lines_run):
    """Review F9 (PROBE F9's form is the default-more row of the mutated module that no check reads): with fewer, the
    same or more lines, in the mutated module or another, a mutant is KILLED only by the check that compares the
    value, at that check's line; one no check reads survives; a longer replacement no blank line can take is
    UNKNOWN (`lines_problems`)."""
    rows, done, mutants = lines_run
    assert done.returncode in (0, 1) and mutants, done.stdout + done.stderr
    assert lines_problems(rows, mutants) == []


# Review F10: Lean's messages when it gives no answer, as Lean 4.24 prints them at a check (the budget ones
# end-to-end in `BUDGET`), and the refutations beside them, which still kill.
NO_ANSWERS = [
    "maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` to increase limit",
    "(deterministic) timeout at `whnf`, maximum number of heartbeats (1000) has been reached\n\nNote: Use `set_option "
    "maxHeartbeats <num>` to set the limit.",
    "[Error pretty printing: maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` to increase",
    "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n- info: 3\n+ error: maximum recursion depth "
    "has been reached",
    "Tactic `decide` failed for proposition\n  bigS 3 = 0\nbecause its `Decidable` instance\n  instDecidableEqNat "
    "(bigS 3) 0\ndid not reduce to `isTrue` or `isFalse`.",
    "Tactic `decide` failed. Internal error: The elaborator is able to reduce the `Decidable` instance, but the "
    "kernel is not able to",
    "Tactic `native_decide` failed: Could not evaluate decidable instance. Error: stack overflow",
    "(kernel) deep recursion detected", "(kernel) deterministic timeout", "(kernel) interrupted"]
ANSWERS = ["Tactic `decide` proved that the proposition\n  bigF 3 = 3\nis false",
           "Tactic `native_decide` evaluated that the proposition\n  bigF 3 = 3\nis false",
           "Expression\n  f 1 == 2\ndid not evaluate to `true`",
           "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n- info: 3\n+ info: 4"]


@pytest.mark.parametrize("message", NO_ANSWERS + ANSWERS, ids=short)
def test_a_check_that_gives_no_answer_never_kills(message):
    """Review F10: a check that runs out of budget, or whose decision procedure gets stuck, did not refute the
    mutant: `judge` refuses it at the check's own line (since F11 because no such message states a refutation)."""
    import trust_mutants
    line = "example : (List.replicate size true).length = size := by decide"
    span = "/-- info: 3 -/\n#guard_msgs in\n#eval f 3\n" if "#guard_msgs" in message else line
    assert trust_mutants.judge(message, "check", line, line, trust_mutants.code_only(span)) == (
        "KILL" if message in ANSWERS else "UNKNOWN")
    assert trust_mutants.brief(message).startswith("no answer: ") is (message not in ANSWERS)


def test_an_error_is_read_with_its_whole_message():
    """Review F10: `ERROR` reads each located error to the next line Lake or Lean starts, so a `#guard_msgs` that
    quotes a budget error on a later line, or a message with blank lines, is read whole (Lake's output, verbatim)."""
    import trust_mutants
    output = ("✖ [2/2] Building Demo.A (5.4s)\ntrace: .> LEAN_PATH=x lean Demo/A.lean\n"
              "error: Demo/A.lean:6:61: maximum recursion depth has been reached\nuse `set_option maxRecDepth <num>` "
              "to increase limit\nerror: Demo/A.lean:11:0: ❌️ Docstring on `#guard_msgs` does not match generated "
              "message:\n\n- info: 100000\n+ error: maximum recursion depth has been reached\n"
              "error: ./Demo/A.lean:15:61: (deterministic) timeout at `whnf`, maximum number of heartbeats (1000) has "
              "been reached\n\nNote: Use `set_option maxHeartbeats <num>` to set the limit.\n\n"
              "warning: Demo/B.lean:2:0: declaration uses 'sorry'\n"
              "error: Demo/A.lean:18:27: Tactic `decide` proved that the proposition\n  bigF 3 = 3\nis false\n"
              "error: Lean exited with code 1\nSome required targets logged failures:\n- Demo.A\nerror: build failed\n")
    found = trust_mutants.located(output)
    assert [(f, n, c) for f, n, c, _ in found] == [("Demo/A.lean", 6, 61), ("Demo/A.lean", 11, 0),
                                                   ("Demo/A.lean", 15, 61), ("Demo/A.lean", 18, 27)]
    assert found[1][3].endswith("+ error: maximum recursion depth has been reached")
    assert found[2][3].endswith("to set the limit.") and found[3][3].endswith("is false")
    assert [bool(trust_mutants.NO_ANSWER.search(m)) for *_, m in found] == [True, True, True, False]


def test_an_outside_files_errors_are_read_with_their_whole_message():
    """Review F11: `lake env lean` writes `<file>:<line>:<column>: error: …` (verbatim below); `LEAN_ERROR` reads each
    whole, to the next message Lean starts, info and diff lines included in theirs."""
    import trust_mutants
    output = ("/t/T.lean:2:29: error: Tactic `decide` proved that the proposition\n  Demo.k 3 = 5\nis false\n"
              "/t/T.lean:3:0: info: 4\n/t/T.lean:4:0: error: ❌️ Docstring on `#guard_msgs` does not match generated "
              "message:\n\n-\n+ error: Expression\n+   Demo.k 3 == 5\n+ did not evaluate to `true`\n"
              "/t/T.lean:6:26: error: Type mismatch\n  rfl\nhas type\n  ?m.7 = ?m.7\n")
    found = trust_mutants.located(output, trust_mutants.LEAN_ERROR)
    assert [(f, n, c) for f, n, c, _ in found] == [("/t/T.lean", 2, 29), ("/t/T.lean", 4, 0), ("/t/T.lean", 6, 26)]
    assert found[0][3].endswith("is false") and found[1][3].endswith("did not evaluate to `true`")
    assert trust_mutants.refutes(found[1][3], "guard") and found[2][3].endswith("?m.7 = ?m.7")


# Review F10's package: each definition is `if n ≤ 3 then n else 100000`, read at 3 by a check that holds for every
# value (and so cannot catch a mutant) but that Lean cannot finish at 100000 (`le-lt` and `lit-minus` of the 3 send
# it there): the mutant must never be KILLED. `refuted` is the same definition read by a check that does catch it.
# `size` is PROBE F10's form (124 passes, 125 hits the recursion limit on Lean 4.24).
BUDGET = [  # (definition, the check(s) after it; {d} is the definition, `in` says where the check is)
    ("decide", "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide"),
    ("rfl", "example : (List.replicate ({d} 3) true).length = {d} 3 := rfl"),
    ("reduce", "#reduce (List.replicate ({d} 3) true).length"),
    ("guard-msgs", "/-- info: 3 -/\n#guard_msgs in\n#reduce (List.replicate ({d} 3) true).length"),
    ("heartbeats", "set_option maxRecDepth 100000 in\nset_option maxHeartbeats 1000 in\n"
                   "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide"),
    ("kernel", "example : (List.replicate ({d} 3) true).length = {d} 3 := by decide +kernel"),
    ("stuck", "example : {d} 3 = {d} 3 + 0 := by decide"),
    ("in-definition", "def {d}Fin : Fin 5 := ⟨(List.replicate ({d} 3) true).length, by decide⟩"),
    ("outside", None),
    ("refuted", "example : {d} 3 = 3 := by decide"),
    ("refuted-outside", None)]


def budget_package(root: Path, folder: Path) -> None:
    scaffold(root, "")
    (root / "lean/Demo/Wf.lean").write_text(  # in the base: well-founded, so `decide` cannot unfold it
        "namespace Demo\n\ndef wf (n : Nat) : Nat := if _ : n = 0 then 0 else wf (n - 1)\ntermination_by n\n\n"
        "end Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "wf")
    text = ["import Demo.Wf\n\nnamespace Demo\n\ndef size : Nat := 124\n\n"
            "example : (List.replicate size true).length = size := by decide\n"]
    for name, check in BUDGET:
        d = "b" + name.title().replace("-", "")
        text.append(f"\ndef {d} (n : Nat) : Nat := if n ≤ 3 then n else {'wf 1' if name == 'stuck' else '100000'}\n\n"
                    + (check.replace("{d}", d) + "\n" if check else ""))
    (root / "lean/Demo/Defs.lean").write_text("".join(text) + "\nend Demo\n")
    (root / "outside").mkdir()
    (root / "outside/Budget.lean").write_text(
        "import Demo.Defs\nexample : (List.replicate (Demo.bOutside 3) true).length = Demo.bOutside 3 := by decide\n")
    (root / "outside/Refute.lean").write_text("import Demo.Defs\nexample : Demo.bRefutedOutside 3 = 3 := by decide\n")
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")


@pytest.fixture(scope="module")
def budget_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("budget")
    budget_package(root, tmp_path_factory.mktemp("budget-dump"))
    return tool(root, tmp_path_factory.mktemp("budget-run"), "--max-mutants", "1000", "--test", "outside/Budget.lean",
                "--test", "outside/Refute.lean")


def test_probe_f10_a_check_out_of_budget_is_no_kill(budget_run):
    """PROBE F10: `size` 124 -> 125 sends the `decide` check over Lean's recursion limit; it holds for every `size`,
    so no mutant of `size` is KILLED."""
    done, mutants = budget_run
    size = of(mutants, "size")
    assert size and not [m for m in size if m["status"] == "KILLED"], done.stdout + done.stderr


@pytest.mark.parametrize(("name", "check"), BUDGET, ids=[b[0] for b in BUDGET])
def test_a_check_out_of_budget_or_stuck_is_unknown(budget_run, name, check):
    """Review F10, every way Lean gives no answer at a check: the mutants that send it to 100000 (`le-lt`, `lit-minus`
    of the 3) are UNKNOWN with "no answer", never KILLED (nor INVALID, when it is inside the mutated definition's own
    proof), the others SURVIVOR; the refuting checks still kill them, inside lean/ and in a --test file."""
    done, mutants = budget_run
    mine = {(m["operator"], m["before"]): m for m in of(mutants, "b" + name.title().replace("-", ""))}
    far = {("le-lt", "≤"), ("lit-minus", "3")}
    assert far <= set(mine), (sorted(mine), done.stdout + done.stderr)
    for key, m in mine.items():
        if name.startswith("refuted"):
            expected = ("KILLED", "proved that") if key in far else ("SURVIVOR", "")
        else:
            expected = ("UNKNOWN", "no answer") if key in far else ("SURVIVOR", "")
        assert m["status"] == expected[0] and expected[1] in m["detail"], m
    if name == "in-definition":  # the Fin's own mutant 3 -> 4: Lean runs out of budget inside it, never INVALID
        own = [m for m in of(mutants, "bInDefinitionFin") if (m["operator"], m["before"]) == ("lit-plus", "3")]
        assert [(m["status"], "no answer" in m["detail"]) for m in own] == [("UNKNOWN", True)], own


# Review F11 and F12's package (the DRI's note 2026-10-19c): each definition is `if n ≤ 3 then n else <far>`, read at
# 3 by the check after it; `le-lt` and `lit-minus` of the 3 send it to <far>. `wf` (well-founded, in the base) is a
# value no reduction unfolds: `wf 1` is 0, so `n + wf 1` is the same value as `n` (the check holds for the mutant)
# and `wf 1` alone a different one; `100` is a different one any reduction reaches. The far mutants must be the
# row's verdict, every other mutant SURVIVOR. Before the fix every UNKNOWN row but `eval-throws`'s value was KILLED.
STUCK = [  # (row, <far>, the check after the definition ({d} is the definition), the far mutants' verdict, detail)
    ("rfl", "wf 1", "example : {d} 3 + 0 = 0 + {d} 3 := rfl", "UNKNOWN", "neither"),  # PROBE F11
    ("by-rfl", "wf 1", "theorem {d}_t : {d} 3 + 0 = 0 + {d} 3 := by rfl", "UNKNOWN", "neither"),
    ("rfl-equal", "n + wf 1", "example : {d} 3 = 3 := rfl", "UNKNOWN", "neither"),
    ("rfl-decide", "100", "example : {d} 3 = 3 := rfl", "KILLED", "(`decide`: Tactic `decide` proved"),
    ("rfl-native", "wf 1", "example : {d} 3 = 3 := rfl", "KILLED", "(`native_decide`: Tactic `native_decide` evaluated"),
    ("rfl-wrapped", "100", "#guard_msgs in\nexample : {d} 3 = 3 := rfl", "KILLED", "(`decide`:"),
    ("guard-expr", "n + wf 1", "#guard_expr {d} 3 =~ 3", "UNKNOWN", "Failed:"),
    ("reduce-doc", "n + wf 1", "/-- info: 3 -/\n#guard_msgs in\n#reduce {d} 3", "UNKNOWN", "Docstring"),
    ("eval-doc", "n + wf 1", "/-- info: 3 -/\n#guard_msgs in\n#eval {d} 3", "SURVIVOR", ""),
    ("eval-doc-refuted", "wf 1", "/-- info: 3 -/\n#guard_msgs in\n#eval {d} 3", "KILLED", "Docstring"),
    ("check-rfl", "100", "#check (rfl : {d} 3 = 3)", "UNKNOWN", "Type mismatch"),
    ("eval-throws", "100", '#eval (do if {d} 3 != 3 then throw (IO.userError "changed") : IO Unit)', "UNKNOWN",
     "changed"),
    ("rfl-in-definition", "100", "def {d}Sub : {x : Nat // x = 3} := ⟨{d} 3, rfl⟩", "UNKNOWN", "mismatch"),
    ("outside-native", "wf 1", None, "KILLED", "(`native_decide`:"),
    ("outside-equal", "n + wf 1", None, "UNKNOWN", "neither"),
]
F12_FORM = "def {d} : {n : Nat // n + 0 = n} := ⟨3, by simp (config := { maxSteps := 9 })⟩"  # PROBE F12
REFUSED_FORM = "def {d} (o : Option Nat) : Bool := o.any (· == 1)\n\n#guard !{d} none"  # no `Option.take`


def stuck_name(row: str) -> str:
    return "s" + row.title().replace("-", "")


def stuck_package(root: Path, folder: Path) -> None:
    scaffold(root, "")
    (root / "lean/Demo/Wf.lean").write_text(
        "namespace Demo\n\ndef wf (n : Nat) : Nat := if _ : n = 0 then 0 else wf (n - 1)\ntermination_by n\n\n"
        "end Demo\n")
    git(root, "add", ".")
    git(root, "commit", "-qm", "wf")
    text = ["import Demo.Wf\n\nnamespace Demo\n"]
    for row, far, check, _, _ in STUCK:
        d = stuck_name(row)
        text.append(f"\ndef {d} (n : Nat) : Nat := if n ≤ 3 then n else {far}\n\n"
                    + (check.replace("{d}", d) + "\n" if check else ""))
    text += [f"\n{F12_FORM.replace('{d}', 'sSimpSteps')}\n", f"\n{REFUSED_FORM.replace('{d}', 'sRefused')}\n"]
    (root / "lean/Demo/Defs.lean").write_text("".join(text) + "\nend Demo\n")
    (root / "outside").mkdir()
    for row in ("outside-native", "outside-equal"):
        (root / f"outside/{stuck_name(row)}.lean").write_text(
            f"import Demo.Defs\nexample : Demo.{stuck_name(row)} 3 = 3 := rfl\n")
    dump(root, folder, [])
    git(root, "add", ".")
    git(root, "commit", "-qm", "head")


@pytest.fixture(scope="module")
def stuck_run(tmp_path_factory):
    root = tmp_path_factory.mktemp("stuck")
    stuck_package(root, tmp_path_factory.mktemp("stuck-dump"))
    return tool(root, tmp_path_factory.mktemp("stuck-run"), "--max-mutants", "1000", "--test",
                "outside/sOutsideNative.lean", "--test", "outside/sOutsideEqual.lean")


@pytest.mark.parametrize(("row", "far", "check", "verdict", "detail"), STUCK, ids=[s[0] for s in STUCK])
def test_a_check_that_states_no_refutation_is_unknown(stuck_run, row, far, check, verdict, detail):
    """Review F11 (the rule inverted): the mutants that send the definition to <far> are KILLED only where Lean
    states a refutation (`decide` or `native_decide` asked after a failing `rfl`, an `#eval`'s value), UNKNOWN where
    the check fails stating none (a stuck `rfl` or `#guard_expr`, a `#reduce` that prints a stuck term, an `#eval`
    that throws, a `#check`), SURVIVOR where it passes; in lean/ and in an outside --test file alike."""
    done, mutants = stuck_run
    mine = {(m["operator"], m["before"]): m for m in of(mutants, stuck_name(row))}
    far_ones = {("le-lt", "≤"), ("lit-minus", "3")}
    assert far_ones <= set(mine), (sorted(mine), done.stdout + done.stderr)
    for key, m in mine.items():
        expected = (verdict, detail) if key in far_ones else ("SURVIVOR", "")
        assert m["status"] == expected[0] and expected[1] in m["detail"], m


def test_probe_f11_a_stuck_rfl_check_is_no_kill(stuck_run):
    """PROBE F11: `if n ≤ 3 then n else wf 1`, read by `rfl` at 3 by a check that holds for every value; the two
    mutants that reach `wf 1` got KILLED by rfl's "Type mismatch" (a stuck reduction). Now UNKNOWN."""
    done, mutants = stuck_run
    rfl = of(mutants, "sRfl")
    assert rfl and not [m for m in rfl if m["status"] == "KILLED"], done.stdout + done.stderr


def test_probe_f12_a_tactic_out_of_steps_in_the_mutated_definition_is_unknown(stuck_run):
    """PROBE F12: `simp`'s step limit (and any other tactic failure) inside the mutated declaration was INVALID,
    which counts for nothing; now UNKNOWN, which counts toward the exit code."""
    done, mutants = stuck_run
    simp = of(mutants, "sSimpSteps")
    assert simp and not [m for m in simp if m["status"] == "INVALID"], simp
    nine = [m for m in simp if (m["operator"], m["before"]) == ("lit-minus", "9")]
    assert [(m["status"], "maximum number of steps" in m["detail"]) for m in nine] == [("UNKNOWN", True)], nine
    assert done.returncode == 1


def test_a_proof_term_in_the_mutated_definition_is_no_refusal(stuck_run):
    """Review F12 (the DRI's step 1, INVALID only when the text does not elaborate): the `rfl` of
    `⟨sRflInDefinition 3, rfl⟩` fails under each of the subtype's own mutants (a type mismatch, which a stuck
    reduction gives too): UNKNOWN, never INVALID."""
    _, mutants = stuck_run
    own = of(mutants, "sRflInDefinitionSub")
    assert own and {m["status"] for m in own} == {"UNKNOWN"}, own


def test_a_name_lean_does_not_know_is_invalid(stuck_run):
    """Review F12: the one positive condition for INVALID holds: `(o.take 1).any …` and the other list cuts of an
    `Option` name a field Lean does not have, outside every tactic block."""
    _, mutants = stuck_run
    cuts = [m for m in of(mutants, "sRefused") if m["operator"].startswith("list-") and m["operator"] != "list-empty"]
    assert len(cuts) == 4 and all(m["status"] == "INVALID" and m["detail"].startswith("Invalid field") for m in cuts)
