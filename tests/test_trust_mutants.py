"""tools/trust_mutants.py on a tiny Lean package (speed-trustmut step 3): a well-guarded definition has no survivor,
a guard over `[]` leaves survivors, a failing proof is no kill, --allow suppresses exactly its operator, the mutants
are built in a scratch copy (the checkout's bytes and times are unchanged), and --max-mutants lists the rest as
NOT RUN. The package's declaration and predicate lists come from tools/lean_statements.py's own per-module script."""
from __future__ import annotations

import json
import os
from pathlib import Path
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
"""
STATED = ["Demo.Far.half_four", "Demo.double_eq", "Demo.double_two", "Demo.four"]


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=root, check=True,
                   capture_output=True, timeout=HANG_TIMEOUT)


def dump(root: Path, folder: Path) -> None:
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
    (folder / "names.txt").write_text("\n".join(STATED) + "\n")
    script = lean_statements.SCRIPT.replace("import VE\n", "".join(f"import {m}\n" for m in modules))
    (root / "lean/statements.txt").write_text(lean_statements.HEADER + lean_statements.run_lean(
        root, folder, script, "Statements", {"VE_STATEMENT_NAMES": str(folder / "names.txt"), **PATH}))


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    root = tmp_path_factory.mktemp("package")
    (root / "lean/Demo/Far").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "lean/lean-toolchain").write_text((ROOT / "lean/lean-toolchain").read_text())
    (root / "lean/lakefile.toml").write_text('name = "demo"\n\n[[lean_lib]]\nname = "Demo"\nglobs = ["Demo.*"]\n')
    (root / ".gitignore").write_text(".lake/\n")
    (root / "tools/trust-classes.json").write_text('{"modules": {}}\n')
    git(root, "init", "-q")
    git(root, "add", ".")
    git(root, "commit", "-qm", "base")
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
    ("example : f 1 = 2 := by\n  simp [f] /- a\n  b -/\n-- c\n", 4, "example : f 1 = 2  := sorry\n\n\n-- c\n")])
def test_a_cut_proof_loses_its_guard_msgs_wrapper_and_keeps_the_comments_after_it(tmp_path, text, last, cut):
    """Review F6: the cut blanks the wrapper (the `sorry` warning would fail it) and keeps the whole comments after
    the proof (the next `#guard_msgs`'s docstring is in the span before it), every line kept."""
    import trust_mutants
    path = tmp_path / "A.lean"
    path.write_text(text)
    first = 2 if text.startswith("--") else 1
    assert trust_mutants.cut_proof(path, first, last)
    assert path.read_text() == cut


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
    ("command", "open Demo", "other")])
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
