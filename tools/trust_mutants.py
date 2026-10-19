#!/usr/bin/env python3
"""Mechanical mutants of the trusted Lean definitions a branch adds or changes, and the survivors (R16 signs trusted
growth only when "every new trusted definition is exercised by a test that can fail").

    uv run python tools/trust_mutants.py [--base REV] [--jobs N] [--max-mutants N] [--test FILE ...] [--deep]
                                         [--allow FILE] [--json OUT] [--root DIR]

Selected: each declaration tools/trust_map.py counts as trusted (not a theorem or check) whose lines hold a line
the tree adds or changes over REV (default: the merge base of HEAD and main). The `OPERATORS` mutate it inside its
compiled range (lean/declarations.txt), comments and strings excluded, on its changed lines only (all of a new one).
Every edit keeps each line after the declaration where it was (`relined`), so the cuts and the roles, which read
the checkout's line numbers, read the mutated text right (review F9).

Each mutant is built in a private scratch copy of lean/ (its build restored from tools/lean_share.py's checked build
of this tree, else copied from lean/.lake; the checkout is only read): the mutated module, its proofs cut to `sorry`
(no proof there is a check), then each module that imports it and holds checks for it: a check whose compiled
statement (lean/statements.txt) uses it, every other check in a module of its directory (of the whole cone with
--deep), and the --test files. A check is a command whose outcome Lean computes from definitions alone, never from a
proof (`classify`): `#guard`, `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by
`decide`, `native_decide` or `rfl`, with no other tactic block in it; a `#guard_msgs … in` is what it wraps. Every
other `example` or theorem, a check form with a tactic block inside, and every `#print` (it lists or shows proofs)
is a proof, whatever its statement names. Each verdict that counts for nothing has one positive condition, and
every other case is UNKNOWN (review F11/F12, the DRI's note 2026-10-19c). The mutant is
- KILLED only when every error Lean reports, in lean/ or in an outside --test file, is a check's own refutation
  (`settle`, `judge`): inside a check, at a line the checkout has there, its message one of `REFUTED` (`decide`
  proved the proposition false, `native_decide` evaluated it false, a `#guard` did not evaluate to `true`) or a
  `#guard_msgs` diff between answers (an `#eval`'s value, a refutation); an `rfl` check's failure, which a stuck
  reduction gives too, counts only when `decide` then refutes its statement. Each such check's statement reads the
  mutated definition, as Lean computes it (`dependencies`: a refutation that came through a cut proof, an instance
  or a `@[csimp]` lemma, refutes nothing about it), and it has no hypothesis (`classify`). And the same build
  without the mutant (its control: the same cuts) passes;
- INVALID only when Lean refused the mutated declaration's text (`invalid`, `refused`): every error there a parse
  error, or a name, field, pattern or exhaustiveness error (`REFUSED`) outside its tactic blocks;
- SURVIVOR when every check passes. A failing proof elsewhere is no kill (BUILDER-CHECKLIST 3): it is cut to
  `sorry` (a `#print` blanked) and the build repeated, before any other error is read; and a check that fails in
  the control too reads a cut proof (`#eval` refuses a value that depends on `sorry`), so it is cut the same way;
- UNKNOWN in every other case: an error in a definition, or in a command that is no check, even beside a failing
  check (review F8: a definition's broken proof term leaves `sorry` there, which a check may refuse); a check
  whose message states no refutation (out of budget, stuck, a tactic that fails, an unclassified message: F10,
  F11); an error in the mutated declaration that is no refusal (a tactic, a type mismatch, Lean's budget: F12);
  and a mutant that moves a line after its declaration (a longer replacement no blank line there can take: F9);
- NOT RUN past --max-mutants (every definition and operator gets its k-th mutant before any gets its k+1-th).

SURVIVOR and UNKNOWN print as `<STATUS> <file>:<line> <definition> <operator>: <before> -> <after>` unless --allow
FILE lists the definition and operator with a reason ({"allow": [{"definition": "VE.X.f", "operator": "lt-le",
"reason": "one line"}]}). Exit 0: all ran, none left; 1: a survivor or UNKNOWN left; 3: none left but some NOT RUN;
2: cannot run. Builder and reviewer evidence only: no gate, merge train or nightly reads it.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
import difflib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools"), str(ROOT / "lean")]
from audit import code_only  # noqa: E402
from check_lean_imports import imports  # noqa: E402
from lean_statements import declaration_list, module_name, source_hash, sources  # noqa: E402
from tools import lake_outputs, lean_share, trust_map  # noqa: E402

OPEN, CLOSE = "([{⟨", ")]}⟩"
CHECK_COMMANDS = {"guard", "guard_expr", "eval", "eval!", "reduce", "check"}
TACTIC = re.compile(r"\bby\b")
EXAMPLE = re.compile(r"(?m)^\s*(?:@\[[^\]]*\]\s*)*example\b")
CHECK_PROOF = re.compile(r":=\s*(?:by\s+)?(?:decide|native_decide|rfl)(?:\s+\+\w+)*\s*$")
# A located error with its whole message (file, line, column, message): its lines run to the next line Lake or Lean
# starts itself. Lake writes `error: <file>:<line>:<column>: …`, `lake env lean` (an outside --test file) `<file>:…:
# error: …`.
REST = r"(.*(?:\n(?!(?:error|warning|info|trace|note):|[✖⚠✔ℹ] |Some required |\S+?\.lean:\d+:\d+: ).*)*)"
ERROR = re.compile(r"^error: (?:\./)*(\S+?\.lean):(\d+):(\d+): " + REST, re.M)
LEAN_ERROR = re.compile(r"^(\S+?\.lean):(\d+):(\d+): error: " + REST, re.M)
PARSE = re.compile(r"(?:unexpected|expected) ")  # how Lean's parser errors start ("unexpected token '<;>'; ...")
# The one condition under which an error kills (review F11, the DRI's note 2026-10-19c: the rule inverted, so a
# message nobody classified is no kill): it is a check's own error and states a refutation, a value Lean computed
# that is not the one the check states. These are Lean 4.24's refutations, matched whole; every other message
# refutes nothing (a stuck reduction, a tactic that fails, Lean's budget, `rfl`'s, which a stuck reduction gives
# too, `#guard_expr`'s and `#check`'s definitional equality, an `#eval` that throws).
REFUTED = re.compile(r"Tactic `decide` proved that the proposition\n.*\nis false|Tactic `native_decide` evaluated "
                     r"that the proposition\n.*\nis false|Expression\n.*\ndid not evaluate to `true`", re.S)
GUARD_DIFF = "❌️ Docstring on `#guard_msgs` does not match generated message:\n\n"
EVALUATED = {"eval", "eval!"}  # the commands whose `info` is a value Lean computed (`#reduce` prints a stuck term)
# Lean refused the mutated text itself (review F12, the rule inverted): a parse error anywhere in the mutated
# declaration, or one of these elaboration errors outside every tactic block of it (`in_tactic`), and every error
# there is one. Any other error there makes the mutant UNKNOWN: a tactic that fails, Lean's budget, a type mismatch
# (a proof term that is false or whose reduction got stuck gives one too, review F11), an instance or implicit
# argument Lean could not synthesize, and a term that is no function (instance search, a coercion's included, fails
# alike on its own budget, size and heartbeats: hunt H2, H3, N5), and anything not classified.
REFUSED = re.compile(r"[Uu]nknown (?:identifier|constant)|Invalid (?:field|projection|pattern)|Missing cases|"
                     r"ambiguous, possible interpret")
# Lean gave no answer (review F10): it ran out of budget (Lean's runtime exceptions, maxRecDepth and maxHeartbeats,
# and the kernel's), or `decide`/`native_decide` could not reduce or evaluate the instance. Since F11 no verdict
# depends on it (an answer is what `REFUTED` names): it marks the detail, and an `#eval`'s `info` that quotes it is
# no answer. Anywhere in the message: a pretty-printer failure wraps it.
NO_ANSWER = re.compile(r"maximum recursion depth|maximum number of heartbeats|\(deterministic\) timeout|\(kernel\) "
                       r"(?:deep recursion|deterministic timeout|interrupted)|stack overflow|"
                       r"Tactic `(?:decide|native_decide)` failed")
KILL, RFL, NONE = "KILL", "RFL", "UNKNOWN"  # `judge`'s verdicts on one error
STOP = {"then", "else", "do", "with", "in", "fun", "if", "let", "match", "return", "throw", "by", "at", "from", "where",
        "for", "unless", "mut", "have", "show"}
LIST_METHODS = ("find\\?|any|all|contains|map|filter|flatMap|filterMap|length|head\\?|isEmpty|foldl|foldr|zip|lookup|"
                "elem|isPrefixOf|take|drop|reverse|sum|count|findSome\\?|eraseDups|dropLast|tail|getLast\\?|mapM|forM")
LIST_RESULTS = {"map", "filter", "flatMap", "filterMap", "take", "drop", "reverse", "eraseDups", "dropLast", "tail",
                "zip"}
CUTS = {"list-empty": None, "list-first": ".take 1", "list-drop-last": ".dropLast", "list-last": ".reverse.take 1",
        "list-drop-first": ".drop 1"}
# The operators and their tiers: --max-mutants runs every earlier tier first.
OPERATORS = {**dict.fromkeys(("arm-true", "arm-false", "arm-default", "body-true", "body-false", "not-drop", "and-or",
                              "or-and", "lt-le", "le-lt", "lt-eq", "le-eq", "eq-le", "eq-ne", "ne-eq", "all-any",
                              "any-all", "bool-flip", "lit-plus", "lit-minus", "list-empty", "append-left",
                              "append-right"), 1), "list-first": 2, "list-drop-last": 2, "list-last": 3,
             "list-drop-first": 3}
LT, LE, EQ = r"(?<![<-])<(?![-|$*;=<>])", r"≤|(?<!<)<=(?!>)", r"(?<![:=!<>])=(?![=>])"
TOKENS = [("not-drop", r"¬\s*|(?<![\w'!?)\]⟩])!(?=[\w(·])", ""), ("and-or", "∧", "∨"),
          ("and-or", r"(?<![&|])&&(?![&|])", "||"), ("or-and", "∨", "∧"), ("or-and", r"(?<!\|)\|\|(?!\|)", "&&"),
          ("lt-le", LT, "≤"), ("lt-eq", LT, "="), ("le-lt", LE, "<"), ("le-eq", LE, "="), ("eq-le", EQ, "≤"),
          ("eq-ne", EQ, "≠"), ("eq-ne", r"(?<!=)==(?!=)", "!="), ("ne-eq", "≠", "="), ("ne-eq", "!=", "=="),
          ("all-any", r"(?<=\.)all\b", "any"), ("any-all", r"(?<=\.)any\b", "all")]
BOOLS = {"true": "false", "false": "true", "True": "False", "False": "True"}


@dataclass
class Mutant:
    id: str
    file: str  # under lean/
    line: int
    definition: str
    operator: str
    start: int  # offsets in the file's text
    end: int
    lines: tuple[int, int]  # the mutated declaration's
    before: str
    after: str
    status: str = "NOT RUN"
    detail: str = ""
    edit: tuple[int, str] = (0, "")  # what `run` writes: text[start:edit[0]] -> edit[1] (`relined`)
    shared: bool = False  # another command starts on the declaration's last line (hunt N10)


def group(t: str, i: int, step: int = 1) -> int:
    """From the bracket at t[i], the index past its partner (step 1) or of its partner (step -1)."""
    depth, j = 0, i
    while 0 <= j < len(t):
        depth += (t[j] in OPEN) - (t[j] in CLOSE)
        if depth == 0:
            return j + (step > 0)
        j += step
    return len(t) if step > 0 else 0


def depth0(t: str, lo: int, hi: int, pattern: str) -> int | None:
    """The first match of `pattern` in t[lo:hi] outside every bracket group."""
    depth = 0
    for i in range(lo, hi):
        depth += (t[i] in OPEN) - (t[i] in CLOSE)
        if depth == 0 and re.match(pattern, t[i:hi]):
            return i
    return None


def name_char(t: str, i: int) -> bool:
    return t[i].isalnum() or t[i] in "_'?.·" or t[i] == "!" and i > 0 and t[i - 1].isalnum()


def atom_before(t: str, j: int, lo: int) -> int | None:
    """The start of the dotted name, or bracket group with dotted names after it, that ends at j."""
    i = j
    while i > lo and name_char(t, i - 1):
        i -= 1
    if i > lo and t[i - 1] in CLOSE and (i == j or t[i] == "."):
        i = group(t, i - 1, -1)
    return i if i < j and t[i] != "." else None


def atom_after(t: str, i: int, hi: int, args: bool = True) -> int:
    """The end of the atom at t[i] and (with `args`) the arguments applied to it on its line; i when there is none."""
    j = group(t, i) if t[i] in OPEN else i
    while j < hi and name_char(t, j):
        j += 1
    if t[i:j] in STOP or t[i:j].startswith("."):
        return i
    while args and j + 1 < hi and t[j] == " " and (k := atom_after(t, j + 1, hi, False)) > j + 1:
        j = k
    return min(j, hi)


def cut(atom: str, chain: str | None) -> str:
    if chain is None:
        return "[]"
    single = re.fullmatch(r"[\w'?.!]+", atom) or atom[0] in OPEN and group(atom, 0) == len(atom)
    return f"({atom}{chain})" if single else f"(({atom}){chain})"


def mutants(text: str, kind: str, lo: int, hi: int) -> list[tuple[str, int, int, str]]:
    """(operator, start, end, replacement) for the declaration at text[lo:hi]."""
    t, code = code_only(text), code_only(text)[lo:hi]
    out = [(op, lo + m.start(), lo + m.end(), new) for op, pattern, new in TOKENS for m in re.finditer(pattern, code)]
    out += [("bool-flip", lo + m.start(), lo + m.end(), BOOLS[m[0]])
            for m in re.finditer(r"(?<![\w.'])(?:true|false|True|False)(?![\w'])", code)]
    for m in re.finditer(r"(?<![\w.'])\d+(?![\w.])", code):
        out += [(op, lo + m.start(), lo + m.end(), str(int(m[0]) + d)) for op, d in (("lit-plus", 1), ("lit-minus", -1))
                if int(m[0]) + d >= 0]
    lists: list[tuple[int, int]] = []
    assign, arm = depth0(t, lo, hi, ":="), re.search(r"(?m)^\s*\|", code)
    head = min(x for x in (assign, lo + arm.start() if arm else None, hi) if x is not None)
    colon, depth = None, 0
    for i in range(lo, head):
        depth += (t[i] in OPEN) - (t[i] in CLOSE)
        colon = i if depth == 0 and t[i] == ":" and t[i + 1] != "=" else colon
    result = re.split("→|->", t[colon + 1:head])[-1].strip() if kind == "def" and colon is not None else ""
    consts = {"Prop": ("True", "False"), "Bool": ("true", "false")}.get(result)
    if result and assign == head:  # a body: `:= ...`
        end = depth0(t, assign, hi, r"\b(?:where|termination_by|decreasing_by)\b") or hi
        rest = t[assign + 2:end]
        body = (assign + 2 + len(rest) - len(rest.lstrip()), assign + 2 + len(rest.rstrip()))
        out += [("body-true", *body, consts[0]), ("body-false", *body, consts[1])] if consts else []
        lists += [body] if result.startswith("List") else []
    elif result and arm:  # arms: `| pattern => result`
        starts = [lo + a.start() for a in re.finditer(r"(?m)^[ \t]*\|", code)]
        arms = []
        for a, b in zip(starts, [*starts[1:], hi]):
            if (arrow := depth0(t, a + t[a:b].index("|") + 1, b, "=>")) is not None:
                rhs = t[arrow + 2:b]
                arms.append((t[a:arrow], arrow + 2 + len(rhs) - len(rhs.lstrip()), arrow + 2 + len(rhs.rstrip())))
        default = arms[-1] if arms and re.fullmatch(r"\s*\|[\s_,]*", arms[-1][0]) else None
        for _, s, e in arms:
            if consts:
                out += [("arm-true", s, e, consts[0]), ("arm-false", s, e, consts[1])]
            elif default and (s, e) != default[1:]:
                out.append(("arm-default", s, e, text[default[1]:default[2]]))
    for m in re.finditer(rf"\.({LIST_METHODS})(?![\w?!'])", code):  # a list method's receiver and list result
        if (start := atom_before(t, lo + m.start(), lo)) is not None:
            lists += [(start, lo + m.start())] + ([(start, atom_after(t, start, hi))] if m[1] in LIST_RESULTS else [])
    lists += [(lo + m.end(), e) for m in re.finditer(r"\bfor \w+ in ", code)
              if (e := t.find(" do", lo + m.end(), hi)) > 0]
    for m in re.finditer(r" \+\+ ", code):
        op = lo + m.start()
        left, right = atom_before(t, op, lo), atom_after(t, op + 4, hi)
        if left is not None and right > op + 4:
            lists += [(left, op), (op + 4, right)]
            out += [("append-left", op, right, ""), ("append-right", left, op + 4, "")]
    lists += [(lo + m.start(), group(t, lo + m.start())) for m in re.finditer(r"(?<![\w'?!)\]@#])\[(?!\])", code)]
    for s, e in dict.fromkeys(lists):
        atom = text[s:e]
        if t[s] == "(" and (s + 1, e - 1) in lists or not atom.strip():  # `(xs)` is the list `xs`
            continue
        if atom.startswith("·"):  # `(·.head.contains a)`: the argument is named first
            out += [(op, s - 1, e, f"(fun x_tm => {cut('x_tm' + atom[1:], chain)}") for op, chain in CUTS.items()
                    if t[s - 1] == "("]
            continue
        one = t[s] == "[" and group(t, s) == e and depth0(t, s + 1, e - 1, ",") is None
        out += [(op, s, e, cut(atom, chain)) for op, chain in CUTS.items()
                if not (one and op in ("list-first", "list-last"))]  # `[x].take 1` is `[x]`
    kept: dict[tuple[int, int, str], str] = {}
    for op, s, e, new in out:
        if (edit := relined(text, s, e, new, hi))[0] == e:  # a shorter one padded
            new = edit[1]
        if new != text[s:e]:
            kept.setdefault((s, e, new), op)
    return [(op, s, e, new) for (s, e, new), op in kept.items()]


def relined(text: str, s: int, e: int, new: str, hi: int) -> tuple[int, str]:
    """(end, replacement) of the edit text[s:e] -> `new` in the declaration ending at text[hi] that keeps every line
    after the declaration where it was (review F9: the cuts and the roles read the checkout's line numbers). A
    shorter replacement is padded with line ends; a longer one takes its extra line ends from the blank lines right
    after the declaration (outside every comment), so the edit runs over them. With too few, the edit is `new` as it
    is, and `run` refuses the mutant (UNKNOWN), since the lines after it moved."""
    extra = new.count("\n") - text.count("\n", s, e)
    if extra <= 0:
        return e, new + "\n" * -extra
    first = text.find("\n", hi) + 1  # the line after the declaration's last
    blank = re.match(r"(?:[ \t]*\n)*", text[first:]) if first else None
    if blank is None or blank[0].count("\n") < extra or not code_only(text[:first] + "X").endswith("X"):
        return e, new
    end = first + len("".join(blank[0].splitlines(keepends=True)[:extra]))
    return end, new + text[e:first]


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)


def changed_lines(root: Path, base: str) -> dict[str, set[int]]:
    """The lines of each file under lean/ that differ from `base` (difflib's; a line next to a deletion counts)."""
    names = git(root, "diff", "--name-only", "-z", base, "--", "lean").stdout.split("\0")
    names += git(root, "ls-files", "--others", "--exclude-standard", "-z", "--", "lean").stdout.split("\0")
    out: dict[str, set[int]] = {}
    for name in sorted({n for n in names if n.endswith(".lean") and (root / n).is_file()}):
        old = git(root, "show", f"{base}:{name}")
        matcher = difflib.SequenceMatcher(None, old.stdout.split("\n") if old.returncode == 0 else [],
                                          (root / name).read_text().split("\n"), autojunk=False)
        out[name.removeprefix("lean/")] = {n for tag, _, _, j1, j2 in matcher.get_opcodes() if tag != "equal"
                                           for n in (range(j1 + 1, j2 + 1) if j2 > j1 else (j1, j1 + 1))}
    return out


def unwrapped(span: str) -> str:
    """`span` (code only) with its `#guard_msgs … in` wrappers blanked."""
    return trust_map.GUARD_WRAPPER.sub(lambda w: " " * len(w[0]), span)


def command(span: str) -> str | None:
    """The `#` command a span (code only) runs, past its `#guard_msgs … in`, `set_option … in` and `open … in`
    prefixes: `guard`, `eval!`, `print`, ...; None for a declaration or an `example`."""
    found = re.match(r"(?:\s|(?:set_option|open)\b[^\n]*?\bin\b)*#([A-Za-z_]\w*!?)", unwrapped(span))
    return found[1] if found else None


def classify(kind: str, span: str) -> str:
    """check, proof or other, for a declaration of `kind` whose code (comments and strings blanked) is `span`. A
    check is a command whose outcome Lean computes from definitions alone, never from a proof: `#guard`,
    `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by `decide`, `native_decide` or
    `rfl`, with no other tactic block (`by`) in it and no binder before its colon (`decide` reads the goal only, not
    a hypothesis: hunt H1). Every other `example` or theorem is a proof (review F1), and so
    is a check form with a tactic block inside (a mutant can break the tactic and nothing else) and every `#print`
    (`#print axioms` lists `sorryAx` once the tool cuts a proof, and `#print` shows the definition's text and its
    proofs: review F7). A `#guard_msgs … in` is the command it wraps (trust_map puts both in one span: review F6).
    Any other command, and one this cannot read, is other: an error there is no kill. A check whose outcome a cut
    proof still changes (`#eval` refuses a value that depends on `sorry`) is caught by the control build in `run`."""
    bare = unwrapped(span)
    if len(re.findall(r"(?<![\w.'])(?:example|theorem|lemma|def|abbrev|instance|#[a-z_]+!?)(?![\w'])", bare)) > 1:
        return "other"  # two commands on its lines (hunt N7): trust_map's spans are whole lines
    proved = CHECK_PROOF.search(bare)
    tactics = len(TACTIC.findall(bare)) - (len(TACTIC.findall(proved[0])) if proved else 0)
    if kind == "theorem" or kind == "command" and EXAMPLE.search(bare):
        head = re.search(r"\b(?:example|theorem\s+[^\s:({\[⦃]+)", bare)
        colon = depth0(bare, head.end(), len(bare), r":(?!=)") if head else None
        # A binder before the colon is a hypothesis `decide` never reads (hunt H1): the check would refute only
        # its goal, so the statement is a proof's.
        closed = colon is not None and not bare[head.end():colon].strip()
        return "check" if proved and not tactics and closed else "proof"
    name = command(span) if kind == "command" else None
    if name == "print" or name in CHECK_COMMANDS and tactics:
        return "proof"
    return "check" if name in CHECK_COMMANDS else "other"


# Lean's answer to "what does each check state, and through what" (`dependencies`), from elaborators run at the
# check's own position (its namespace, `open`s and section variables): `tm_trust_probe` replaces the proof of a
# `decide`/`rfl` check, `#tm_trust_guard` and `#tm_trust_eval` replace `#guard` and `#eval`. Each walks the
# constants the statement uses, transitively through definitions of this tree, never into a theorem's proof, and
# prints per check `<k>` and then:
# - `<k> <definition>` for each mutated definition the statement reads, never through a `Decidable` instance
#   (`decide p` is `p`'s value whatever instance decides it: hunt H4);
# - `<k> ! <theorem>` for each theorem of this tree behind such an instance, the statement's own included (a cut
#   one makes `decide` compute through the mutated definition where the statement does not: hunt N1, N2);
# - `<k> hyps` when the check's goal has a hypothesis (a section `variable` included: hunt H1, N8);
# - `<k> ?` when it reflects on the environment (it reads a definition's text, as `#print` does: hunt N3).
READS = """
open Lean Meta in
def tmTrustWalk (k : Name) (roots : List (Expr × Bool)) : MetaM Unit := do
  let env ← getEnv
  let names (xs : List String) : NameSet := xs.foldl (fun s n => s.insert n.toName) {}
  let targets := names TARGETS
  let mods := names MODULES
  let reflect := [``Lean.Environment, ``Lean.ConstantInfo, ``Lean.MonadEnv]
  let decidable (t : Expr) : Bool := t.getForallBody.getAppFn.constName?.any
    ([``Decidable, ``DecidableEq, ``DecidablePred, ``DecidableRel].contains ·)
  let used (es : List Expr) (behind : Bool) : List (Name × Bool) :=
    es.foldl (fun a e => a ++ e.getUsedConstants.toList.map (·, behind)) []
  IO.println s!"{k}"
  let mut seen : NameSet := {}
  let mut seenBehind : NameSet := {}
  let mut todo := roots.foldl (fun a (e, b) => a ++ used [e] b) []
  while !todo.isEmpty do
    let (c, behind) := todo.head!
    todo := todo.tail!
    if behind then
      if seenBehind.contains c then continue
      seenBehind := seenBehind.insert c
    else
      if seen.contains c then continue
      seen := seen.insert c
    if !behind && targets.contains c then IO.println s!"{k} {c}"
    let some info := env.find? c | continue
    if reflect.contains c || info.type.getUsedConstants.any reflect.contains then IO.println s!"{k} ?"
    if (env.getModuleIdxFor? c).any (fun i => !mods.contains env.header.moduleNames[i.toNat]!) then continue
    let behind' := behind || decidable info.type
    match info with
    | .thmInfo _ => if behind then IO.println s!"{k} ! {c}"
    | .defnInfo d => todo := todo ++ used [d.type, d.value] behind'
    | _ => todo := todo ++ used [info.type] behind'

open Lean Elab Tactic Meta in
elab "tm_trust_probe " k:ident : tactic => do
  let goal ← instantiateMVars (← getMainTarget)
  if (← getLCtx).foldl (fun n d => if d.isImplementationDetail then n else n + 1) 0 > 0 then
    IO.println s!"{k.getId} hyps"
  let inst ← try pure [(← synthInstance (mkApp (mkConst ``Decidable) goal), true)] catch _ => pure []
  tmTrustWalk k.getId ((goal, false) :: inst)

open Lean Elab Command Term Meta in
elab "#tm_trust_guard " k:ident e:term : command => liftTermElabM do
  let e ← Term.elabTermEnsuringType e (mkConst ``Bool)
  Term.synthesizeSyntheticMVarsNoPostponing
  tmTrustWalk k.getId [(← instantiateMVars e, false)]

open Lean Elab Command Term Meta in
elab "#tm_trust_eval " k:ident e:term : command => liftTermElabM do
  let e ← Term.elabTerm e none
  Term.synthesizeSyntheticMVarsNoPostponing
  tmTrustWalk k.getId [(← instantiateMVars e, false)]
"""


def named(text: str, roles: list[tuple]) -> tuple[str, dict[str, tuple[int, int]]]:
    """`text` with each check that can kill (a `#guard`, an `#eval`, an `example` or theorem proved by `decide`,
    `native_decide` or `rfl`) handed to `READS`'s elaborators in place, as `tmChk_<first line>`, its
    `#guard_msgs … in` blanked; and the spans by name."""
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    spans: dict[str, tuple[int, int]] = {}
    for first, last, role, *_ in sorted(roles, reverse=True):
        lo, hi = starts[first - 1], starts[min(last, len(starts) - 1)] - 1
        code = code_only(text)[lo:hi]
        bare, name = unwrapped(code), f"tmChk_{first}"
        if role != "check":
            continue
        span = "".join(" " if bare[i] == " " and code[i] != " " else text[lo + i] for i in range(len(code)))
        if (which := command(code)) in ("guard", "eval", "eval!"):
            at = re.search(r"#(?:guard|eval!?)(?![\w!])", bare)
            head = "".join(" " if code[i] == " " and not span[i].isspace() else span[i] for i in range(at.start()))
            span = f"{head}#tm_trust_{which.rstrip('!')} {name}{span[at.end():]}"  # comments blanked: no docstring
        elif which is None and (proved := CHECK_PROOF.search(bare)):
            span = f"{span[:proved.start()]}:= by tm_trust_probe {name}; exact sorry{span[proved.end():]}"
        else:
            continue
        spans[name] = (first, last)
        text = text[:lo] + span + text[hi:]
    return text, spans


def dependencies(lake, files: dict[str, tuple[Path, list[tuple]]], definitions: list[str], modules: list[str],
                 folder: Path, jobs: int) -> dict[tuple[str, tuple[int, int]], dict[str, set[str]]]:
    """(file, (first, last line)) -> {"reads": the mutated definitions its statement reads, "behind": the theorems
    behind its `Decidable` instances, "flags": `hyps`, `?`}, as `READS` prints it for a copy of the file under
    `folder` that `lake("env", "lean", copy)` elaborates (`named`; the probe's elaborators after its imports). A
    check Lean could not read is absent (no kill). `files`: key -> (its path, its roles)."""
    probe = READS.replace("TARGETS", json.dumps(definitions, ensure_ascii=False)).replace(
        "MODULES", json.dumps(modules, ensure_ascii=False))

    def one(item: tuple[int, tuple[str, tuple[Path, list]]]) -> dict:
        i, (key, (path, roles)) = item
        text, spans = named(path.read_text(), roles)
        lines = text.split("\n")
        after = max((n + 1 for n, line in enumerate(code_only(text).split("\n")) if line.startswith("import ")),
                    default=0)
        copy = folder / f"reads{i}.lean"
        copy.write_text("\n".join(["import Lean", *lines[:after], probe, *lines[after:]]))
        out: dict = {}
        for line in lake("env", "lean", str(copy))[1].splitlines():
            name, _, rest = line.partition(" ")
            if name in spans:
                entry = out.setdefault((key, spans[name]), {"reads": set(), "behind": set(), "flags": set()})
                if rest.startswith("! "):
                    entry["behind"].add(rest[2:])
                elif rest in ("hyps", "?"):
                    entry["flags"].add(rest)
                elif rest:
                    entry["reads"].add(rest)
        return out

    folder.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        return {k: v for part in executor.map(one, enumerate(files.items())) for k, v in part.items()}


def file_roles(path: Path) -> list[tuple[int, int, str, None]]:
    """(first, last line, role, None) of each command of an outside --test file, read as `plan` reads lean/
    (`trust_map.scan`, `classify`), but with no compiled declarations: a named theorem there is unrecorded, so other."""
    decls, _, _ = trust_map.scan(path, [])
    code = code_only(path.read_text()).split("\n")
    return [(d.start, d.end, classify(d.kind, "\n".join(code[d.start - 1:d.end])), None) for d in decls]


@dataclass
class Tree:
    roles: dict[str, list[tuple[int, int, str, str | None]]]  # file -> (first, last line, check|proof|other, name)
    uses: dict[str, set[tuple[str, str]] | None]  # theorem -> the constants its statement uses
    files: dict[str, str]  # module -> file under lean/
    importers: dict[str, set[str]]


def plan(root: Path, base: str) -> tuple[list[Mutant], Tree, list[str]]:
    """The mutants in run order, the tree's checks and imports, and the problems that stop the run."""
    classified, _, problems = trust_map.walk(root, root / "tools/trust-classes.json", root / "lean/statements.txt")
    declared, hashes = declaration_list(root / "lean/declarations.txt")
    changed = changed_lines(root, base)
    fatal = [p for p in problems if "not compiled from this source" in p or "missing" in p]
    fatal += [f"lean/declarations.txt was not compiled from lean/{f}; rerun tools/lean_statements.py"
              for f in changed if hashes.get(module_name(f)) != source_hash(root / "lean" / f)]
    texts = {f: (root / "lean" / f).read_text() for f in {c.module for c in classified}}
    masked = {f: code_only(text).split("\n") for f, text in texts.items()}
    roles: dict[str, list] = {}
    found: list[Mutant] = []
    for c in classified:
        d, text = c.decl, texts[c.module]
        span = "\n".join(masked[c.module][d.start - 1:d.end])
        roles.setdefault(c.module, []).append((d.start, d.end, classify(d.kind, span), d.name))
        lines = changed.get(c.module, set())
        if not (c.trusted and d.name and d.kind not in ("theorem", "command", "unrecorded")
                and lines & set(range(d.start, d.end + 1))):
            continue
        ranged = [x for x in declared.get(module_name(c.module), []) if x.name == d.name and x.start]
        if not ranged:
            fatal.append(f"lean/{c.module}: {d.name} has no compiled range; rerun tools/lean_statements.py")
            continue
        starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n")]
        r = ranged[0]
        hi = starts[r.end[0] - 1] + r.end[1]
        for op, s, e, new in sorted(mutants(text, d.kind, starts[r.start[0] - 1] + r.start[1], hi),
                                    key=lambda x: x[1]):
            first, edit = text.count("\n", 0, s) + 1, relined(text, s, e, new, hi)
            if lines & set(range(first, first + text.count("\n", s, e) + 1)):  # its lines run over the blanks it takes
                found.append(Mutant("", c.module, first, d.name, op, s, e, (r.start[0], max(
                    r.end[0], text.count("\n", 0, edit[0]))), text[s:e], new, edit=edit, shared=bool(
                    code_only(text)[hi:text.find("\n", hi) % (len(text) + 1)].strip())))
    seen: Counter = Counter()  # each tier in turn; in it, the k-th of every (definition, operator) first
    keys = []
    for i, m in enumerate(found):
        keys.append((OPERATORS[m.operator], seen[m.definition, m.operator], list(OPERATORS).index(m.operator), i))
        seen[m.definition, m.operator] += 1
    out = [m for _, m in sorted(zip(keys, found), key=lambda x: x[0])]
    for i, m in enumerate(out, 1):
        m.id = f"M{i:03d}"
    files, importers = {}, {}
    for path in sources(root):
        key = path.relative_to(root / "lean").as_posix()
        files[module_name(key)] = key
        try:
            for imported in imports(path.read_text()):
                importers.setdefault(imported, set()).add(module_name(key))
        except ValueError as error:
            fatal.append(f"lean/{key}: {error}")
    return out, Tree(roles, trust_map.statements(root / "lean/statements.txt"), files, importers), fatal


def stated(tree: Tree, theorem: str | None, m: Mutant) -> bool:
    return (module_name(m.file), m.definition) in (tree.uses.get(theorem) or ())


def targets(tree: Tree, m: Mutant, tests: list[str], deep: bool = False) -> list[str]:
    """The mutated module, then the --test modules and the modules of its cone that hold checks for it."""
    module, home = module_name(m.file), m.file.rpartition("/")[0]
    cone, todo = {module}, [module]
    while todo:
        new = tree.importers.get(todo.pop(), set()) - cone
        cone |= new
        todo += new
    checks = {x for x in cone for s, e, r, n in tree.roles.get(tree.files[x], ())
              if r == "check" and (deep or tree.files[x].rpartition("/")[0] == home or stated(tree, n, m))}
    return [module, *sorted((checks | {module_name(t) for t in tests}) - {module})]


def moved(before: str, after: str, lines: tuple[int, int]) -> int | None:
    """The first line outside lines[0]..lines[1] that is not where it was in `before` (review F9), else None."""
    old, new = before.split("\n"), after.split("\n")
    return next((n for n in range(1, max(len(old), len(new)) + 1) if not lines[0] <= n <= lines[1]
                 and old[n - 1:n] != new[n - 1:n]), None)


def located(output: str, pattern: re.Pattern = ERROR) -> list[tuple[str, int, int, str]]:
    return [(f, int(n), int(c), message.rstrip()) for f, n, c, message in pattern.findall(output)]


def refutes(message: str, name: str | None) -> bool:
    """Whether `message`, an error at a check whose `#` command is `name` (`command`), states a refutation: one of
    `REFUTED`, whole, or a `#guard_msgs` diff whose two sides hold answers only and differ. An answer is an
    `#eval`'s `info` (a value it computed) or a refutation; a message the diff cannot show as two sides (Lean's
    `guard_msgs.diff` off) is none."""
    if REFUTED.fullmatch(message):
        return True
    if not message.startswith(GUARD_DIFF):
        return False
    sides: dict[str, list[str]] = {"-": [], "+": []}
    for line in message[len(GUARD_DIFF):].split("\n"):
        if line[:1] not in ("-", "+", " ") or line[1:2] not in ("", " "):
            return False
        for side in ("-+" if line[0] == " " else line[0]):
            sides[side].append(line[2:])

    def answers(lines: list[str]) -> list[str] | None:
        said = [m.strip() for m in re.split(r"(?m)^---$", "\n".join(lines)) if m.strip()]
        return said if all(m.startswith("info:") and name in EVALUATED and not NO_ANSWER.search(m)
                           or m.startswith("error:") and REFUTED.fullmatch(m[6:].strip()) for m in said) else None
    expected, generated = answers(sides["-"]), answers(sides["+"])
    return expected is not None and generated is not None and expected != generated


def judge(message: str, role: str, built: str, checkout: str, span: str) -> str:
    """KILL, RFL or UNKNOWN for one error left after the cuts and the control (review F11: one positive condition).
    KILL only when it is a check's own error (`role` check, at a line the mutant and the cuts left as the checkout
    has it: `built`, `checkout`; review F9) whose message states a refutation (`refutes`; `span` is the check's
    code). RFL when that check is proved by `rfl`: its failure reads the same whether the two sides differ or their
    reduction got stuck, so `settle` asks `decide` of its statement. Anything else is UNKNOWN:
    a parse error (a cut left behind, a moved line), an error outside every check, any other message (fail closed)."""
    if role != "check" or built != checkout or not built.strip() or PARSE.match(message):
        return NONE
    if refutes(message, command(span)):
        return KILL
    proved = CHECK_PROOF.search(unwrapped(span))
    return RFL if proved and re.search(r"\brfl\s*$", proved[0]) else NONE


def decided(text: str, first: int, last: int) -> str:
    """`text` with the `rfl` (or `by rfl`) that proves the check on lines first..last replaced by `by decide`, every
    line kept."""
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi = starts[first - 1], starts[min(last, len(starts) - 1)] - 1
    found = re.search(r"(?:\bby\s+)?\brfl(?=\s*$)", unwrapped(code_only(text)[lo:hi]))
    if found is None:
        return text
    s, e = lo + found.start(), lo + found.end()
    return text[:s] + "by decide" + "\n" * text.count("\n", s, e) + text[e:]


def settle(errors: list[tuple[str, int, str]], read, checkout, roles: dict[str, list], rebuild, reads,
           where=lambda f: f"lean/{f}") -> tuple[str, str]:
    """KILLED or UNKNOWN for the errors (file, line, message) a build left after the cuts and its control (review
    F11): KILLED only when every one is KILL (`judge`), or RFL and `decide` then refutes its check's statement, and
    every such check can refute the mutated definition (`reads`: (file, (first, last line)) -> None, else why not:
    Lean does not find the definition in its statement, or its `decide` rests on a theorem the tool cut, `run`'s
    `reading` of `dependencies`: hunt H4, N1, N2). `rebuild` builds
    with the given files' texts (those checks' `rfl` replaced: `decided`) and returns the errors, None when none is
    located; a rewritten check that gives no error there, or an error that is no refutation, refutes nothing, and any
    other error must still be KILL. `read`, `checkout`: a file's built and checkout text; `roles`: file -> (first,
    last line, role, ...). `decide` only: `native_decide` evaluates compiled code, which an `rfl` check never reads
    (an `implemented_by` can differ from the definition: hunt H7)."""
    def verdicts(found: list[tuple[str, int, str]], now: dict[str, tuple[str, str]]) -> list[tuple]:
        """`judge` on each error; `now`: file -> its built and checkout text with the rewrites, if any."""
        rows = []
        for f, n, message in found:
            span = next(((s, e, r) for s, e, r, *_ in roles.get(f, ()) if s <= n <= e), None)
            text, original = now[f] if f in now else (read(f), checkout(f))
            built, original = text.split("\n"), original.split("\n")
            code = "\n".join(code_only(text).split("\n")[span[0] - 1:span[1]]) if span else ""
            rows.append(((f, span and span[:2]), n, message, judge(
                message, span[2] if span else "other", built[n - 1] if 0 < n <= len(built) else "",
                original[n - 1] if 0 < n <= len(original) else "", code)))
        return rows

    rows = verdicts(errors, {})
    if bad := next((x for x in rows if x[3] == NONE), None):
        return "UNKNOWN", f"{where(bad[0][0])}:{bad[1]}: {brief(bad[2])}"
    if bad := next(((x, why) for x in rows if (why := reads(x[0]))), None):
        return "UNKNOWN", f"{where(bad[0][0][0])}:{bad[0][1]}: {brief(bad[0][2])} ({bad[1]})"
    confirmed = ""
    if pending := {x[0]: x for x in rows if x[3] == RFL}:
        now: dict[str, tuple[str, str]] = {}  # the same rewrite in the checkout's text, which `judge` compares
        for f, (s, e) in pending:
            now[f] = tuple(decided(x, s, e) for x in (now[f] if f in now else (read(f), checkout(f))))
        if (found := rebuild({f: texts[0] for f, texts in now.items()})) is None:
            return "UNKNOWN", f"{where(next(iter(pending))[0])}: the build with `decide` has no located error"
        again = verdicts(found, now)
        if bad := next((x for x in again if x[0] not in pending and x[3] != KILL), None):
            return "UNKNOWN", f"{where(bad[0][0])}:{bad[1]}: {brief(bad[2])}"
        for key, (_, n, message, _) in pending.items():
            if not (mine := [x for x in again if x[0] == key]) or any(x[3] != KILL for x in mine):
                return "UNKNOWN", f"{where(key[0])}:{n}: {brief(message)} (an `rfl` check `decide` does not refute)"
            confirmed = confirmed or f" (`decide`: {brief(mine[0][2], 60)})"
    (f, _), n, message, verdict = next((x for x in rows if x[3] == KILL), rows[0])
    return "KILLED", f"{where(f)}:{n}: {brief(message, 120)}" + (confirmed if verdict == RFL else "")


def in_tactic(code: str, at: int, lo: int, hi: int) -> bool:
    """Whether code[at] is inside a tactic block of the declaration code[lo:hi] (code only): from a `by` to the end
    of the bracket group it is in, else of the declaration, and from `decreasing_by` to the end."""
    for found in re.finditer(r"\bby\b|\bdecreasing_by\b", code[lo:hi]):
        if (start := lo + found.start()) > at:
            break
        depth, j = 0, start
        while j < hi and (depth := depth + (code[j] in OPEN) - (code[j] in CLOSE)) >= 0:
            j += 1
        if at < j:
            return True
    return False


def invalid(errors: list[tuple[str, int, str, int]], text: str, lines: tuple[int, int]) -> tuple[str, str]:
    """INVALID when every error (file, line, message, column) in the mutated declaration on `lines` of `text` says
    Lean refused its text (`refused`), else UNKNOWN at the first that does not (review F12: a tactic that fails or
    Lean's budget there decides nothing, even beside a refusal it may have caused or followed)."""
    code, starts = code_only(text), [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi = starts[lines[0] - 1], starts[min(lines[1], len(starts) - 1)] - 1
    for f, n, message, column in errors:
        if not refused(message, in_tactic(code, starts[min(n, len(starts)) - 1] + column, lo, hi)):
            return "UNKNOWN", f"lean/{f}:{n}: {brief(message)}"
    return "INVALID", brief(errors[0][2])


def refused(message: str, inside_tactic: bool) -> bool:
    """Whether an error in the mutated declaration says Lean refused its text (review F12, `REFUSED`): INVALID; any
    other error there makes the mutant UNKNOWN."""
    return not NO_ANSWER.search(message) and bool(PARSE.match(message) or REFUSED.match(message) and not inside_tactic)


def brief(message: str, size: int = 200) -> str:
    """The first line of an error message (`ERROR` reads all of it), marked when Lean gave no answer (`NO_ANSWER`)."""
    return ("no answer: " if NO_ANSWER.search(message) else "") + message.split("\n", 1)[0][:size]


def role(tree: Tree, file: str, line: int, m: Mutant) -> str:
    """mutated (inside the mutated declaration), else the role `classify` gave the declaration at `line`."""
    if file == m.file and m.lines[0] <= line <= m.lines[1]:
        return "mutated"
    return next((r for s, e, r, _ in tree.roles.get(file, ()) if s <= line <= e), "other")


def cut_proof(path: Path, first: int, last: int) -> bool:
    """The theorem or `example` on lines first..last of `path` with its proof replaced by `sorry` and its
    `#guard_msgs … in` wrappers and its attributes blanked (the `sorry` warning would fail a wrapper: review F6; a
    `@[csimp]` lemma cut to `sorry` would still send compiled code through the mutated definition: hunt N2), or the
    `#` command there
    blanked whole with the comments before it (it declares nothing; its docstring is the `#guard_msgs`'s: review
    F7), every line kept. The comment lines after the span stay: a docstring there is the next command's
    (trust_map's span ends before that command's first code line), and a `#guard_msgs` reads its docstring."""
    text = path.read_text()
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi, t = starts[first - 1], starts[min(last, len(starts) - 1)] - 1, code_only(text)
    if command(t[lo:hi]):
        begin = lo  # back over the lines with no code before it, to the first outside every string and comment
        while begin and not t[starts[n := text.count("\n", 0, begin) - 1]:lo].strip():
            begin = starts[n]
        while not code_only(text[:begin] + "X").endswith("X"):  # a string or comment still open there
            begin = text.index("\n", begin) + 1
        end = lo + len(t[lo:hi].rstrip())
        path.write_text(text[:begin] + re.sub(r"[^\n]", " ", text[begin:end]) + text[end:])
        return True
    arm = re.search(r"(?m)^\s*\|", t[lo:hi])
    found = [x for x in (depth0(t, lo, hi, ":="), lo + arm.start() if arm else None) if x is not None]
    if found:
        head, at = list(text), min(found)
        for w in trust_map.GUARD_WRAPPER.finditer(t, lo, at):
            head[w.start():w.end()] = re.sub(r"[^\n]", " ", w[0])
        for a in re.finditer(r"@\[", t[lo:at]):  # and its attributes: a `sorry` is no `@[csimp]` lemma (hunt N2)
            head[lo + a.start():group(t, lo + a.start() + 1)] = re.sub(r"[^\n]", " ", text[lo + a.start():group(
                t, lo + a.start() + 1)])
        end = next((s for s in starts if at < s <= hi and not t[s:hi].strip() and not code_only(text[s:hi]).strip()),
                   hi)  # the first line from which only whole comments are left
        path.write_text("".join(head[:at]) + " := sorry" + "\n" * text.count("\n", at, end) + text[end:])
    return bool(found)


class Scratch:
    """A private copy of lean/, sources and build, that mutants are built in; the checkout is only read."""

    def __init__(self, lean: Path, parent: Path, source: Scratch | None = None):
        self.lean = Path(tempfile.mkdtemp(prefix="lean-", dir=parent)) / "lean"
        if source:  # another scratch's .olean files are linked: Lake replaces them by renaming, never in place
            shutil.copytree(source.lean, self.lean, symlinks=True,
                            copy_function=lambda s, d: os.link(s, d) if s.endswith(".olean") else shutil.copy2(s, d))
            return
        shutil.copytree(lean, self.lean, symlinks=True, ignore=shutil.ignore_patterns(".lake", ".cache"))
        try:  # lean_share's checked build of this tree, without its executables
            entry = lean_share.default_store() / "v1" / lean_share.entry_id(lean_share.key(lean))
            for name, record in lean_share.check_entry(entry)["files"].items():
                if not name.startswith("build/bin/") and not lean_share._place(
                        entry / "lake" / name, self.lean / ".lake" / name, record["link"]):
                    os.chmod(self.lean / ".lake" / name, record["mode"] | 0o200)
        except (lean_share.Refused, OSError, RuntimeError, TypeError, subprocess.SubprocessError):
            shutil.rmtree(self.lean / ".lake", ignore_errors=True)
            if (lean / ".lake").is_dir():
                shutil.copytree(lean / ".lake", self.lean / ".lake", symlinks=True,
                                ignore=lambda d, names: ["bin"] if Path(d).name == "build" else [])

    def lake(self, env: dict, *args: str) -> tuple[int, str]:
        done = subprocess.run([lake_outputs.lean_executable(env, "lake"), *args], cwd=self.lean, env=env,
                              capture_output=True, text=True, check=False)
        return done.returncode, done.stdout + done.stderr


def run(m: Mutant, scratch: Scratch, tree: Tree, tests: list[str], outside: list[Path], env: dict,
        deep: bool = False, controls: dict | None = None, reads: dict | None = None) -> tuple[str, str]:
    """(status, detail) of one mutant, built in `scratch`, whose files are restored afterwards. The mutated module's
    proofs are cut up front, and a proof that fails elsewhere is cut and the build repeated, before any other error
    is read: a check may fail only because a proof it reads failed. An error in a check is a kill only when its
    control, the same build without the mutant (the same cuts; `controls` caches it across mutants), passes: what
    fails there too reads a cut proof (review F7: `#eval` refuses a value that depends on `sorry`), so it is cut as
    well and never a kill. `reads`: `dependencies` (a kill needs its check to read the mutated definition)."""
    controls = {} if controls is None else controls
    reads = {} if reads is None else reads

    def reading(key: tuple) -> str | None:
        """Why the check at `key` cannot refute the mutated definition (`dependencies`), or None."""
        entry = reads.get(key)
        cut = {name for f, spans in cuts.items() for s, e, _, name in tree.roles.get(f, ()) if (s, e) in spans}
        if entry is None or m.definition not in entry["reads"]:
            return f"Lean does not find {m.definition} in its statement"
        if "hyps" in entry["flags"]:
            return "its goal has a hypothesis"
        if "?" in entry["flags"]:
            return "it reads the environment, as `#print` does"
        if behind := sorted(entry["behind"] & cut):
            return f"its `Decidable` instance rests on {behind[0]}, which the tool cut"
        return None
    built = targets(tree, m, tests, deep)
    texts: dict[str, str] = {}  # file -> the checkout's text, written back at the end
    cuts: dict[str, list[tuple[int, int]]] = {}  # file -> the spans cut in it

    def write(f: str, mutated: bool) -> None:
        path = scratch.lean / f
        text = texts.setdefault(f, path.read_text())
        path.write_text(text[:m.start] + m.edit[1] + text[m.edit[0]:] if mutated and f == m.file else text)
        for s, e in cuts.get(f, ()):
            cut_proof(path, s, e)

    columns: dict[tuple[str, int, str], int] = {}  # each error's column, which `in_tactic` reads

    def build(stage: list[str]) -> tuple[int, list[tuple[str, int, str]]]:
        for attempt in range(3):  # again: Lake can fail with no located error under load
            code, output = scratch.lake(env, "build", *(f"+{x}" for x in stage))
            found = located(output)
            columns.update(((f, n, message), c) for f, n, c, message in found)
            if code == 0 or found:
                return code, [(f, n, message) for f, n, _, message in found]
        return code, [("", 0, "the build failed with no located error: " + output[-300:])]

    def read(f: str) -> str:
        return (scratch.lean / f).read_text()

    def rebuild(stage: list[str], now: dict[str, str]) -> list[tuple[str, int, str]] | None:
        """The errors of `stage` built with the files' texts `now`, which are restored afterwards."""
        before = {f: read(f) for f in now}
        try:
            for f, text in now.items():
                (scratch.lean / f).write_text(text)
            code, found = build(stage)
            return None if found[:1] and not found[0][0] else found
        finally:
            for f, text in before.items():
                (scratch.lean / f).write_text(text)

    def state() -> tuple:
        return tuple(sorted((f, tuple(c)) for f, c in cuts.items() if c))

    def each(found: list[tuple]) -> list[tuple[str, int, str]]:
        """The first error of each declaration in `found`."""
        first: dict[tuple[str, int], tuple[str, int, str]] = {}
        for f, n, message, *_ in found:
            first.setdefault((f, next((s for s, e, *_ in tree.roles.get(f, ()) if s <= n <= e), n)), (f, n, message))
        return list(first.values())

    def cut(f: str, n: int, why: str) -> str | None:
        """Cuts the proof, check or `#` command at f:n, unless already cut; else the reason (UNKNOWN)."""
        found = next(((s, e, r) for s, e, r, _ in tree.roles.get(f, ()) if s <= n <= e), None)
        why = f"lean/{f}:{n}: {why}" if f else why
        if found is None or role(tree, f, n, m) == "mutated" or found[:2] in cuts.get(f, ()):
            return why
        s, e, r = found
        path = scratch.lean / f
        texts.setdefault(f, path.read_text())
        if r == "other" and not command("\n".join(code_only(path.read_text()).split("\n")[s - 1:e])) \
                or not cut_proof(path, s, e):
            return why
        cuts.setdefault(f, []).append((s, e))
        return None

    try:
        write(m.file, True)
        if (n := moved(texts[m.file], (scratch.lean / m.file).read_text(), m.lines)) is not None:
            return "UNKNOWN", f"lean/{m.file}:{n}: the mutant moves this line (no blank line after it takes its lines)"
        for first, last, r, _ in sorted(tree.roles[m.file], reverse=True):
            if r == "proof" and not first <= m.line <= last and cut_proof(scratch.lean / m.file, first, last):
                cuts.setdefault(m.file, []).append((first, last))
        for stage in (built[:1], built[1:]):  # the mutated module alone first: most mutants end there
            for _ in range(12):
                code, found = build(stage) if stage else (0, [])
                if code == 0:
                    break
                if not found[0][0]:
                    return "UNKNOWN", found[0][2]
                roles = [(f, n, message, role(tree, f, n, m)) for f, n, message in found]
                if (mutated := [x for x in roles if x[3] == "mutated"]) and m.shared:  # whose error: unknown
                    return "UNKNOWN", (f"lean/{m.file}:{m.lines[1]}: {brief(mutated[0][2])} (another command shares "
                                       "the mutated declaration's last line)")
                if mutated:
                    return invalid([(f, n, message, columns.get((f, n, message), 0)) for f, n, message, _ in
                                    mutated], read(m.file), m.lines)
                if proofs := [x for x in roles if x[3] == "proof" and x[0] not in tests]:
                    for f, n, message in each(proofs):  # cut first: a check may fail only because it reads one
                        if why := cut(f, n, f"the failing proof cannot be cut: {brief(message)}"):
                            return "UNKNOWN", why
                    continue
                key = (tuple(stage), state())
                if (control := controls.get(key)) is None:  # the same build without the mutant
                    write(m.file, False)
                    control = build(stage)[1]
                    write(m.file, True)
                    if control[:1] and not control[0][0]:  # no located error: not kept for others
                        return "UNKNOWN", f"its control: {control[0][2]}"
                    controls[key] = control
                for f, n, message in each(control):  # it fails there too: it reads a cut proof, so cut it
                    if why := cut(f, n, f"fails without the mutant too: {brief(message)}"):
                        return "UNKNOWN", why
                if control:
                    continue
                # A kill only when every error is a check's own refutation (`settle`): one elsewhere (a definition
                # whose proof term the mutant breaks, review F8) leaves `sorry` that a check may refuse, a parse
                # error or a line that is not the checkout's is the tool's own edit (review F9), and a message that
                # states no refutation refutes nothing (F10, F11), so each decides UNKNOWN.
                return settle(found, read, lambda f: texts[f] if f in texts else read(f), tree.roles,
                              lambda now: rebuild(stage, now), reading)
            else:
                return "UNKNOWN", "the proof cuts did not settle"
        failing = {t: out for t in outside if (out := scratch.lake(env, "env", "lean", str(t)))[0]}
        if not failing:
            return "SURVIVOR", ""
        key = ("outside", tuple(built), state())
        if key not in controls:
            write(m.file, False)
            ok = all(build(stage)[0] == 0 for stage in (built[:1], built[1:]) if stage)
            controls[key] = [t for t in outside if not ok or scratch.lake(env, "env", "lean", str(t))[0]]
            write(m.file, True)
        if not (new := [t for t in failing if t not in controls[key]]):
            return "UNKNOWN", f"{next(iter(failing))} fails without the mutant too"
        mutant_built = []  # the stages rebuilt with the mutant once (the control built them without), for `rfl`

        def again(t: Path, now: dict[str, str]) -> list[tuple[str, int, str]] | None:
            """An outside file's errors with its text `now`, written to a copy in the scratch directory."""
            if not mutant_built:
                mutant_built.append(all(build(stage)[0] == 0 for stage in (built[:1], built[1:]) if stage))
            copy = scratch.lean.parent / "outside" / t.name
            copy.parent.mkdir(exist_ok=True)
            copy.write_text(now[str(t)])
            code, output = scratch.lake(env, "env", "lean", str(copy))
            found = [(str(t) if f == str(copy) else f, n, message) for f, n, _, message in located(output, LEAN_ERROR)]
            return None if not mutant_built[0] or code and not found else found

        first = ""
        for t in new:  # the same rule as inside lean/ (`settle`), on the file's own commands (`file_roles`)
            found = [(f, n, message) for f, n, _, message in located(failing[t][1], LEAN_ERROR)]
            if not found:
                return "UNKNOWN", f"{t} fails with no located error: {failing[t][1][-200:]}"
            text = t.read_text()
            status, detail = settle(found, lambda f: text if f == str(t) else "", lambda f: text if f == str(t) else "",
                                    {str(t): file_roles(t)}, lambda now, t=t: again(t, now), reading, str)
            if status != "KILLED":
                return status, detail
            first = first or detail
        return "KILLED", first
    finally:
        for f, text in texts.items():
            (scratch.lean / f).write_text(text)


def evidence(data: dict) -> str:
    """The --json text: one mutant per line."""
    rows = ",\n".join(json.dumps(m, ensure_ascii=False) for m in data["mutants"])
    head = json.dumps({k: v for k, v in data.items() if k != "mutants"}, ensure_ascii=False)
    return f'{head[:-1]}, "mutants": [\n{rows}\n]}}\n'


def show(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 100 else text[:97] + "..."


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", help="the commit compared with (default: the merge base of HEAD and main)")
    parser.add_argument("--root", type=Path, default=ROOT, help="the checkout (default: this one); only read")
    parser.add_argument("--jobs", type=int, help="mutants built at once (default: min(8, cores - 5-min load))")
    parser.add_argument("--max-mutants", type=int, default=60)
    parser.add_argument("--test", action="append", default=[], help="a Lean file that must fail for a kill too")
    parser.add_argument("--deep", action="store_true", help="every check module of the cone, not only its directory's")
    parser.add_argument("--allow", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    entries = json.loads(args.allow.read_text()).get("allow") if args.allow else []
    if not isinstance(entries, list) or not all(
            isinstance(e, dict) and set(e) == {"definition", "operator", "reason"} and e["operator"] in OPERATORS
            and all(isinstance(v, str) and v.strip() and "\n" not in v for v in e.values()) for e in entries):
        return print('--allow: {"allow": [{"definition", "operator", "reason": one line}, ...]}', file=sys.stderr) or 2
    allow = {(e["definition"], e["operator"]): e["reason"] for e in entries}
    base = args.base or git(root, "merge-base", "HEAD", "main").stdout.strip()
    if not base or git(root, "rev-parse", "--verify", "-q", base + "^{commit}").returncode:
        return print(f"no base commit {base!r}", file=sys.stderr) or 2
    tests = [t.removeprefix("lean/") for t in args.test if (root / "lean" / t.removeprefix("lean/")).is_file()]
    outside = [(root / t).resolve() for t in args.test if t.removeprefix("lean/") not in tests]
    if bad := [t for t in [*outside, *(root / "lean" / t for t in tests)] if t.suffix != ".lean" or not t.is_file()]:
        return print(f"--test: not a Lean file: {bad}", file=sys.stderr) or 2
    started = time.monotonic()
    found, tree, fatal = plan(root, base)
    if fatal:
        return print("\n".join(fatal), file=sys.stderr) or 2
    jobs = args.jobs or max(1, min(8, (os.cpu_count() or 1) - int(os.getloadavg()[1])))
    run_now, not_run = found[:max(0, args.max_mutants)], found[max(0, args.max_mutants):]
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    definitions = sorted({(m.file, m.definition) for m in found})
    print(f"trust_mutants: {len(definitions)} definitions, {len(found)} mutants ({len(run_now)} to run), {jobs} jobs, "
          f"base {base[:12]}", flush=True)
    with tempfile.TemporaryDirectory(prefix="trust-mutants-") as scratch_dir:
        pool: queue.Queue = queue.Queue()
        controls: dict = {}  # the builds without a mutant, by stage and cuts: shared by every scratch
        reads: dict = {}  # `dependencies`: what each check reads, from the checkout's text
        if run_now:
            first = Scratch(root / "lean", Path(scratch_dir))
            code, output = first.lake(env, "build", *sorted({f"+{x}" for m in run_now for x in targets(tree, m, tests,
                                                                                                    args.deep)}))
            failing = [t for t in outside if first.lake(env, "env", "lean", str(t))[0]]
            if code or failing:
                return print(f"the checks fail without a mutant:\n{output[-3000:]}{failing}", file=sys.stderr) or 2
            checked = {tree.files[x] for m in run_now for x in targets(tree, m, tests, args.deep)}
            probed = {f: (first.lean / f, tree.roles[f]) for f in sorted(checked)
                      if any(r == "check" for _, _, r, _ in tree.roles.get(f, ()))}
            probed.update({str(t): (t, file_roles(t)) for t in outside})
            reads = dependencies(lambda *a: first.lake(env, *a), probed, sorted({m.definition for m in run_now}),
                                 sorted(tree.files), Path(scratch_dir) / "reads", jobs)
            pool.put(first)
            for _ in range(min(jobs, len(run_now)) - 1):
                pool.put(Scratch(root / "lean", Path(scratch_dir), first))

        def one(m: Mutant) -> None:
            scratch = pool.get()
            try:
                m.status, m.detail = run(m, scratch, tree, tests, outside, env, args.deep, controls, reads)
            finally:
                pool.put(scratch)
            if m.status in ("SURVIVOR", "UNKNOWN") and (m.definition, m.operator) in allow:
                m.status, m.detail = "ALLOWED", allow[(m.definition, m.operator)]
            if m.status in ("SURVIVOR", "UNKNOWN"):
                print(f"{m.status} lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> "
                      f"{show(m.after)}{' (' + show(m.detail) + ')' if m.detail else ''}", flush=True)

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            list(executor.map(one, run_now))
    for m in not_run:
        print(f"NOT RUN lean/{m.file}:{m.line} {m.definition} {m.operator}: {show(m.before)} -> {show(m.after)}")
    counts = {s: sum(m.status == s for m in found) for s in ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID", "ALLOWED",
                                                            "NOT RUN")}
    seconds = round(time.monotonic() - started)
    print("trust_mutants: " + ", ".join(f"{n} {s}" for s, n in counts.items()) + f" in {seconds} s")
    if args.json:
        args.json.write_text(evidence({
            "base": git(root, "rev-parse", base).stdout.strip(), "head": git(root, "rev-parse", "HEAD").stdout.strip(),
            "jobs": jobs, "max_mutants": args.max_mutants, "deep": args.deep, "tests": args.test, "seconds": seconds,
            "counts": counts, "definitions": [f"lean/{f}: {d}" for f, d in definitions],
            "mutants": [{k: v for k, v in asdict(m).items() if k not in ("start", "end", "edit", "shared")}
                          for m in found]}))
    return 1 if counts["SURVIVOR"] or counts["UNKNOWN"] else 3 if not_run else 0


if __name__ == "__main__":
    sys.exit(main())
