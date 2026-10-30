#!/usr/bin/env python3
"""Mechanical mutants of the trusted Lean definitions a branch adds or changes, and the survivors (R16 signs trusted
growth only when "every new trusted definition is exercised by a test that can fail").

    uv run python tools/trust_mutants.py [--base REV] [--jobs N] [--max-mutants N] [--test FILE ...] [--deep]
                                         [--allow FILE] [--json OUT] [--root DIR] [--rescore PREV.json]
                                         [--classes LIST] [--shard K/N] [--plan]
    uv run python tools/trust_mutants.py --merge OUT.json PART.json...

Selected: each declaration tools/trust_map.py counts as trusted (not a theorem or check) whose lines hold a line
the tree adds or changes over REV (default: the merge base of HEAD and main).

--classes LIST widens the selection (`chosen`), as builder and reviewer evidence only. LIST is comma-separated:
`trusted` (the default: the selection above, exactly), trust_map's own class names (`SELECTABLE`: trust_map's
CLASSES but those its KIND_CLASSES give theorems and checks; each name picks its class, tied or not), or `all`
(every class but those two, and every trusted declaration). Theorems, proof helpers (P) and checks (T) are never
selected, whatever LIST says; an unknown name stops the run. Why: the declarations trust_map does not count as
trusted (`trust_map.is_trusted`: reject-only and identity decoders, admission checks and limits, checked code, tied
ones) are where reviewers plant mutants by hand. Under `all`, 17 of the 46 mutants reviewers planted in 7 items were
SURVIVOR at the reviewed tree on that very line, in declarations the default does not select (eff-20261026-1). A
survivor of a trusted declaration is R16's question; one of any other class is review risk. Each mutant records
its declaration's class (`trust_class`, " tied" added) and `trusted`, the SURVIVOR, UNKNOWN and NOT RUN lines name
it, and the summary counts the verdicts by class (`class_counts`). LIST is one of `inputs`' options, so --rescore
never reuses or carries a verdict across another selection.

The `OPERATORS` mutate each selected declaration inside its compiled range (lean/declarations.txt), comments and
strings excluded, on its changed lines only (all of a new one); an inductive's `ctor-drop` drops each constructor
alone (review sc-1ae F1: `JsonWF`'s `bool` and `num` read by no proof or check). Every edit keeps each line after
the declaration where it was (`relined`), so the cuts and the roles, which read the checkout's line numbers, read the
mutated text right (review F9).

Each mutant is built in a private scratch copy of lean/ (its build restored from tools/lean_share.py's checked build
of this tree, else copied from lean/.lake; the checkout is only read): the mutated module, then each module that imports it and holds checks for it: a check whose compiled
statement (lean/statements.txt) uses it, every other check in a module of its directory (of the whole cone with
--deep), the --test files and every module of lean/ an outside --test file imports (review F13). A check is a command whose outcome Lean computes from definitions alone, never from a
proof (`classify`): `#guard`, `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by
`decide`, `native_decide` or `rfl`, with no other tactic block in it; a `#guard_msgs … in` is what it wraps. Every
other `example` or theorem, a check form with a tactic block inside, and every `#print` (it lists or shows proofs)
is a proof, whatever its statement names. Each verdict that counts for nothing has one positive condition, and
every other case is UNKNOWN (review F11/F12, the DRI's note 2026-10-19c). The mutant is
- KILLED only when every error Lean reports, in lean/ or in an outside --test file, is a check's own refutation
  (`settle`, `judge`): inside a check, at a line the checkout has there, its message one of `REFUTED` (`decide`
  proved the proposition false, `native_decide` evaluated it false, a `#guard` did not evaluate to `true`) or a
  `#guard_msgs` diff between refutations (never an `info`: `#eval` and `#reduce` print no answer); an `rfl` check's
  failure, which a stuck reduction gives too, counts only when `decide` then refutes its statement. In the
  mutant's build Lean elaborates each such check as without the mutant (the same term, and every definition it
  reads outside the mutated one the same), with no hypothesis, no IO, and nothing it computes, compiled code
  included, reaches a proof the mutant broke (`probe`, `READS`: a `Decidable` instance or `@[csimp]` lemma on it
  computes through the mutated definition where the statement does not). And the same build without the mutant
  (its control: the same cuts) passes;
- INVALID only when Lean refused the text the mutant wrote (`invalid`, `refused`): every error in the mutated
  declaration a parse error or a name, field, pattern or exhaustiveness error (`REFUSED`), inside the mutant's own
  text and outside every tactic block;
- SURVIVOR when every check passes. A failing proof elsewhere is no kill (BUILDER-CHECKLIST 3): it is cut to
  `sorry` (a `#print` blanked) and the build repeated, before any other error is read; and a check that fails in
  the control too reads a cut proof (`#eval` refuses a value that depends on `sorry`), so it is cut the same way.
  Its detail names each proof it cut ("the proofs it breaks: <file>:<line>, ..."), empty when it broke none: a
  Prop no check can evaluate is exercised only by those proofs (R16), so an --allow reason for it cites one;
- UNKNOWN in every other case: an error in a definition, or in a command that is no check, even beside a failing
  check (review F8: a definition's broken proof term leaves `sorry` there, which a check may refuse); a check
  whose message states no refutation (out of budget, stuck, a tactic that fails, an unclassified message: F10,
  F11); an error in the mutated declaration that is no refusal (a tactic, a type mismatch, Lean's budget: F12);
  and a mutant that moves a line after its declaration (a longer replacement no blank line there can take: F9);
- NOT RUN past --max-mutants (every definition and operator gets its k-th mutant before any gets its k+1-th).

SURVIVOR and UNKNOWN print as `<STATUS> <file>:<line> <definition> (<class>) <operator>: <before> -> <after>`
(`kind`: the class, ", trusted" added when R16 counts it), unless --allow FILE lists the definition and operator
with a reason ({"allow": [{"definition": "VE.X.f", "operator": "lt-le", "reason": "one line"}]}); a `ctor-drop`
survivor that breaks no proof is never allowed (no proof or check reads its constructor), and an allowed one keeps
the proofs it breaks after its reason. Exit 0: all ran,
none left; 1: a survivor or UNKNOWN left; 3: none left but some NOT RUN; 2: cannot run. Builder and reviewer
evidence only: no gate, merge train or nightly reads it.

--rescore PREV.json (speed-tmrescore): every --json records `inputs`, digests of the bytes every verdict is computed
from (`inputs`, with each file's own in `files`), each mutant's verdict before --allow (`raw_status`, and
`raw_detail` on a row --allow changed: review sc-1ae recheck F6), and for each
KILLED and INVALID one what it reads (`reads`, `killed_at`: `Reads`). When PREV's mutants are this plan's and
- its `inputs` are this run's (mode "identical"): its KILLED, INVALID and SURVIVOR verdicts are the same by
  construction and are reused (`reused_from: <PREV head>`); only its UNKNOWN mutants (a build past its time limit
  among them) and the NOT RUN that now fit --max-mutants run;
- or only checks changed (mode "checks", speed-tmchecks): the tool, base and options (--deep, --test, --classes)
  are the same, and every file that changed is a module of lean/ outside every selected declaration's file and
  import closure, an outside --test file or a generated inventory (`check_only`). Then a KILLED or INVALID verdict
  (before --allow) whose reads read the same (`Reads.carry`) is carried (`reused_from`, `carried: "checks"`); every
  other mutant runs (a SURVIVOR, UNKNOWN or ALLOWED one: a new check may kill it, and a KILLED one whose killing
  check, or what it reads, changed).
  A carried KILLED stands on its unchanged check's refutation: a new check that the mutant would make fail some
  other way (no refutation: UNKNOWN in a full run) is not looked for. That is why reviewers run without --rescore.
The current --allow applies to all. With no mutant to run there is no build. Else (no `inputs`, no per-file digests
for a change, any other change, a file it cannot read) it is a full run, and one line says why. The JSON gains
`rescore: {file, head, mode, changed, reused, rerun}`.

--shard K/N, --merge and --plan (tm-shard) split one run into N parts that run on N machines, and combine them:
- --shard K/N (1 <= K <= N, else exit 2): after the plan and --max-mutants as without it, part K owns the mutants
  that run whose id M<i> has (i - 1) % N == K - 1 (`owns`: by id, so stable, balanced by count, and since the ids
  follow the run order a mix of every tier). It builds and judges only those (--rescore and the control build
  too), prints only their SURVIVOR and UNKNOWN lines, and its exit code reads only their verdicts. Its --json is
  the record (`record`) with `shard: {k, n, owned}` added; each mutant another part owns is listed in plan order
  with status and raw_status `OTHER SHARD`, a status only a part's record holds (counted under its own key);
- --merge OUT.json PART.json... reads only the parts (no checkout, no Lean; every other option is ignored) and
  writes the record one run with their options writes, but for "seconds" (the parts' longest), "jobs" and "steps"
  (their sums) and `shards: [{k, n, jobs, seconds, steps}]`, by k; it prints that run's lines and exits with its
  code. It refuses (exit 2) parts that are no part as this tool writes one (`unread`: a field or row not of its
  type, a status not one it writes, counts that are not its rows'), disagree on N, base, head, options, inputs, the plan or --rescore's
  file, head, mode, changed or full_run, miss or repeat a k, own a mutant twice, never, or with no verdict, or
  hold anything but the plan's row and its status (`idle`) for a mutant they do not run, OTHER SHARD or NOT RUN;
- --plan prints `{"base", "definitions", "mutants", "to_run", "not_run"}` ("owned" too with --shard) as one JSON
  line and builds nothing: what sizes N.

Every --json records where the time went (`steps`, eff-tm-control; a run fact, like "seconds", that no verdict
reads): `wall`, the seconds of each phase of the run in turn (`WALL`: the plan, the scratch copies, the control
build, the probe's install, the checks' probes without a mutant, the mutants, the reads); `lake`, the seconds Lake
ran in each step summed over the jobs (`LAKE`: those control phases, then in the mutants' builds the mutated
module's stage, the check modules' stage and the outside --test files, the stage controls, and the mutants' probes),
and `runs`, how many Lake runs each took. One line prints them. --merge writes each part's in its `shards` entry
and their sums as the record's.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
import difflib
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from types import UnionType
from typing import get_args, get_origin, get_type_hints

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
# depends on it (an answer is what `REFUTED` names): it marks the detail, and a refusal that quotes it is none.
# Anywhere in the message: a pretty-printer failure wraps it.
NO_ANSWER = re.compile(r"maximum recursion depth|maximum number of heartbeats|\(deterministic\) timeout|\(kernel\) "
                       r"(?:deep recursion|deterministic timeout|interrupted)|stack overflow|"
                       r"Tactic `(?:decide|native_decide)` failed")
KILL, RFL, NONE = "KILL", "RFL", "UNKNOWN"  # `judge`'s verdicts on one error
TIMED_OUT = -1000  # `Scratch.lake`'s code for a run killed past its time limit
STATUSES = ("KILLED", "SURVIVOR", "UNKNOWN", "INVALID", "ALLOWED", "NOT RUN")
OTHER = "OTHER SHARD"  # a --shard part's status of a mutant another part owns
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
                              "append-right", "ctor-drop"), 1), "list-first": 2, "list-drop-last": 2, "list-last": 3,
             "list-drop-first": 3, "list-drop-middle": 3}
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
    raw_status: str = "NOT RUN"  # the status before --allow, which --rescore reads
    raw_detail: str = ""  # the detail before --allow, which --rescore reads (a ctor-drop's names the proofs it breaks)
    reused_from: str = ""  # the head of the --rescore run whose verdict this is
    carried: str = ""  # "checks" when --rescore carried it across a check-only change (`Reads.carry`)
    reads: str = ""  # a KILLED or INVALID verdict's digest of what it reads (`Reads.verdict`)
    killed_at: tuple[int, int] | None = None  # a KILLED verdict's killing check (first, last line)
    trust_class: str = ""  # its declaration's trust_map class, " tied" added for a tied one (`chosen`)
    trusted: bool = True  # whether trust_map counts that declaration as trusted (R16's)


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
    if kind == "inductive":  # review sc-1ae F1: each constructor dropped alone, its doc comment with it
        starts = [lo + a.start() for a in re.finditer(r"(?m)^[ \t]*\|", code)
                  if sum((c in OPEN) - (c in CLOSE) for c in code[:a.start()]) == 0]
        for a, b in zip(starts, [*starts[1:], hi]):
            e = a + len(t[a:(depth0(t, a, b, r"\bderiving\b") or b)].rstrip())
            while (p := text.rfind("\n", lo, a - 1)) >= 0 and not t[p + 1:a - 1].strip() and text[p + 1:a - 1].strip():
                a = p + 1
            out.append(("ctor-drop", a, e, ""))
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
    literals = [(lo + m.start(), group(t, lo + m.start())) for m in re.finditer(r"(?<![\w'?!)\]@#])\[(?!\])", code)]
    lists += literals
    for s, e in literals:  # review ap-2b F1: each element of a literal list between its first and its last
        commas = [s]
        while (c := depth0(t, commas[-1] + 1, e - 1, ",")) is not None:
            commas.append(c)
        out += [("list-drop-middle", a + 1, b + 1, "") for a, b in zip(commas[1:-1], commas[2:])]
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


# Lean's answer about each check that can kill (`probe`), from elaborators run at the check's own position (its
# namespace, `open`s and section variables): `tm_trust_probe` in place of a `decide`/`rfl` check's proof,
# `#tm_trust_guard` in place of `#guard`. Each prints, for the check `<k>`:
# - `<k> hash <h>`: the hash of what it elaborates to, the instance Lean synthesizes for a `decide` check included.
#   A kill needs the mutant's to be the control's (`run`'s `reading`): an elaborator that reads the source text
#   (`by_elab`, `include_str`: hunt Q6, Q12), an instance search that runs out of budget and silently picks another
#   instance (Q10) or a mutant that changes which instance Lean picks (P8) changes it;
# - `<k> sorry`: what it computes reaches `sorryAx`, transitively through everything Lean would run or reduce for it
#   in this tree (definitions, `opaque` ones included, proofs, types, the `@[csimp]` lemmas and `implemented_by`
#   targets of each constant it reaches). Since the tool cuts only a proof that fails (`run`), that is a proof the
#   mutant broke: a `Decidable` instance or `@[csimp]` lemma resting on it computes through the mutated definition
#   where the statement does not (hunt H4, N1, N2, P1-P9, Q1-Q3, Q5);
# - `<k> hyps`: its goal has a hypothesis (a section `variable` included: hunt H1, N8).
# A check Lean cannot elaborate in the probe has `sorryAx` in its term, so it says `sorry` (hunt Q12).
# It is a module of its own (`install`), imported on the copy's first line, so the copy keeps the file's lines for
# what a check reads of its source (hunt Q6).
READS = """import Lean

open Lean in
def tmTrustCore (env : Environment) (c : Name) : Bool :=
  (env.getModuleIdxFor? c).any fun i => [`Init, `Std, `Lean, `Lake].any (·.isPrefixOf env.header.moduleNames[i.toNat]!)

open Lean Meta in
def tmTrustWalk (k : Name) (roots : List Expr) : MetaM Unit := do
  let env ← getEnv
  let say (s : String) : IO Unit := do IO.println s!"{(← IO.getEnv "TM_TRUST_NONCE").getD ""} {k} {s}"
  let mutated := ((← IO.getEnv "TM_TRUST_MUTATED").getD "").toName
  let lines := ((← IO.getEnv "TM_TRUST_LINES").getD "").splitOn " " |>.filterMap String.toNat?
  let moduleOf (c : Name) : Name :=
    ((env.getModuleIdxFor? c).map (env.header.moduleNames[·.toNat]!)).getD env.mainModule
  -- the declaration a generated constant belongs to: its name without internal parts (`_unsafe_rec`, `_unary`,
  -- `_default`, numbers) and matchers
  let rec owner (c : Name) (fuel : Nat) : Name := match fuel, c with
    | n + 1, .str p s => if s.startsWith "_" || Meta.isMatcherCore env c then owner p n else c
    | n + 1, .num p _ => owner p n
    | _, _ => c
  -- the mutated declaration and what Lean generated for it: its source range is inside the mutated one's
  let inside (c : Name) : MetaM Bool := do
    if mutated.isAnonymous then return false
    let o := owner c 100
    if o == mutated then return true
    if moduleOf o != moduleOf mutated then return false
    match ← findDeclarationRanges? o, lines with
    | some r, [s, e] => return s ≤ r.range.pos.line && r.range.endPos.line ≤ e
    | _, _ => return false
  -- every theorem `@f = @g` outside Lean's core: a `@[csimp]` lemma, wherever (and however locally) it is given
  let mut equations : NameMap (List Name) := {}
  let ours := (env.header.moduleNames.zip env.header.moduleData).foldl (init := env.constants.map₂.toList.map (·.1))
    fun a (m, d) => if [`Init, `Std, `Lean, `Lake].any (·.isPrefixOf m) then a else a ++ d.constNames.toList
  for t in ours do
    if let some (.thmInfo info) := env.find? t then
      if let some f := (info.type.getAppArgs[1]?).bind (·.constName?) then
        if info.type.isAppOfArity ``Eq 3 then equations := equations.insert f (t :: (equations.getD f []))
  let io := [``unsafeBaseIO, ``unsafeEIO, ``unsafeIO, ``IO, ``EIO, ``BaseIO, ``IO.RealWorld]
  say s!"hash {roots.foldl (fun h e => mixHash h e.hash) 7}"
  let mut seen : NameSet := {}
  let mut todo : List Name := roots.foldl (fun a e => a ++ e.getUsedConstants.toList) []
  let mut found := false
  while !todo.isEmpty do
    let c := todo.head!
    todo := todo.tail!
    if seen.contains c then continue
    seen := seen.insert c
    if c == ``sorryAx && !found then
      say "sorry"
      found := true
    let some info := env.find? c | continue
    if io.contains c || (Lean.getInitFnNameFor? env c).isSome || info.type.getUsedConstants.any io.contains then
      say "io"
    -- what the compiler runs for it (a core constant's `@[csimp]` lemma of this tree included: hunt T2)
    todo := todo ++ equations.getD c [] ++ (Lean.Compiler.getImplementedBy? env c).toList ++
      (Lean.getInitFnNameFor? env c).toList ++ [c ++ `_unsafe_rec]
    if tmTrustCore env c then continue
    if info matches .axiomInfo _ then say "axiom"
    let value := (info.value? (allowOpaque := true)).getD (mkConst ``True)
    if !(info matches .thmInfo _) && !(← inside c) then say s!"const {c} {mixHash info.type.hash value.hash}"
    todo := todo ++ info.type.getUsedConstants.toList ++ value.getUsedConstants.toList

open Lean Elab Tactic Meta in
elab "tm_trust_probe " k:ident : tactic => do
  let goal ← instantiateMVars (← getMainTarget)
  if (← getLCtx).foldl (fun n d => if d.isImplementationDetail then n else n + 1) 0 > 0 then
    IO.println s!"{(← IO.getEnv "TM_TRUST_NONCE").getD ""} {k.getId} hyps"
  let inst ← try pure [← instantiateMVars (← synthInstance (mkApp (mkConst ``Decidable) goal))] catch _ => pure []
  tmTrustWalk k.getId (goal :: inst)

open Lean Elab Command Term Meta in
elab "#tm_trust_guard " k:ident e:term : command => liftTermElabM do
  let e ← Term.elabTermEnsuringType e (mkConst ``Bool)
  Term.synthesizeSyntheticMVarsNoPostponing
  tmTrustWalk k.getId [← instantiateMVars e]
"""


def named(text: str, roles: list[tuple]) -> tuple[str, dict[str, tuple[int, int]]]:
    """`text` with each check that can kill (a `#guard`, an `example` or theorem proved by `decide`, `native_decide`
    or `rfl`) handed to `READS`'s elaborators in place, as `tmChk_<first line>`, its `#guard_msgs … in` blanked; and
    the spans by name."""
    starts = [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    spans: dict[str, tuple[int, int]] = {}
    for first, last, role, *_ in sorted(roles, reverse=True):
        lo, hi = starts[first - 1], starts[min(last, len(starts) - 1)] - 1
        code = code_only(text)[lo:hi]
        bare, name = unwrapped(code), f"tmChk_{first}"
        if role != "check":
            continue
        span = "".join(" " if bare[i] == " " and code[i] != " " else text[lo + i] for i in range(len(code)))
        if (which := command(code)) == "guard":
            at = re.search(r"#guard(?![\w!])", bare)
            head = "".join(" " if code[i] == " " and not span[i].isspace() else span[i] for i in range(at.start()))
            span = f"{head}#tm_trust_guard {name}{span[at.end():]}"  # comments blanked: no docstring
        elif which is None and (proved := CHECK_PROOF.search(bare)):
            span = (f"{span[:proved.start()]}:= by tm_trust_probe {name}; exact sorry" + "\n" * span.count(
                "\n", proved.start(), proved.end()) + span[proved.end():])
        else:
            continue
        spans[name] = (first, last)
        text = text[:lo] + span + text[hi:]
    return text, spans


def install(lake, lean: Path) -> bool:
    """`READS` compiled as the module `TmTrustProbe` into the build of the scratch copy `lean` (once: copies made
    from it link it). True when it compiled."""
    source = lean / "TmTrustProbe.lean"  # Lean compiles a module only from inside its package
    source.write_text(READS)
    target = lean / ".lake/build/lib/lean/TmTrustProbe.olean"
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        return lake("env", "lean", "-o", str(target), str(source))[0] == 0
    finally:
        source.unlink()


def probe(lake, env: dict, text: str, roles: list[tuple], path: Path, outside: bool = False
          ) -> dict[tuple[int, int], dict]:
    """(first, last line) -> {"flags": what `READS` prints for the check (`hash <h>`, `sorry`, `axiom`, `io`, `hyps`),
    "consts": {constant: hash} of what it reads outside the mutated definition} for each check of `text` (a file of
    one build, its `roles`), elaborated as the build elaborates it: written (`named`, with `import TmTrustProbe` on
    its first import line, every line kept) to the module's own `path` in the scratch copy and restored afterwards,
    and run by `lake("lean", path)` with that module's options (a package's or library's `leanOptions` decide which
    instance Lean picks: hunt R5, S8); an `outside` --test file, which the tool only reads, is written to `path`
    beside it and run by `lake env lean`, as `run` checks one. Only lines that start with this call's nonce are read
    (a check's own `#eval` can print anything: hunt S7). A check Lean could not read is absent (no kill)."""
    text, spans = named(text, roles)
    lines = text.split("\n")
    first = next((n for n, line in enumerate(code_only(text).split("\n")) if line.startswith("import ")), 0)
    lines[first] = "import TmTrustProbe " + lines[first]
    nonce = secrets.token_hex(12)
    before = path.read_text() if path.is_file() else None
    path.write_text("\n".join(lines))
    try:
        said = lake({**env, "TM_TRUST_NONCE": nonce}, *(("env", "lean") if outside else ("lean",)), str(path))[1]
    finally:
        path.write_text(before) if before is not None else path.unlink()
    out: dict = {}
    for line in said.splitlines():
        mark, _, line = line.partition(" ")
        name, _, rest = line.partition(" ")
        if mark == nonce and name in spans and rest:
            entry = out.setdefault(spans[name], {"flags": set(), "consts": {}})
            if rest.startswith("const "):
                constant, _, value = rest[6:].rpartition(" ")
                entry["consts"][constant] = value
            else:
                entry["flags"].add(rest)
    return out


def beside(lean: Path, f: str) -> Path:
    """Where `probe` writes `f`'s probe: the module itself in the scratch copy `lean` (restored afterwards), or for an
    outside --test file, which the tool only reads, a copy in the scratch directory."""
    return lean.parent / f"probe-{Path(f).name}" if Path(f).is_absolute() else lean / f


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
    # the modules of lean/ an outside --test file imports (`main`): built with the mutant, as a check module is
    imported: set[str] = field(default_factory=set)


# --classes (the docstring's "--classes LIST"): trust_map's class names but those its declarations' kinds fix (P, T:
# theorems, proofs and checks), read from trust_map, and the two words.
SELECTABLE = tuple(c for c in trust_map.CLASSES if c not in trust_map.KIND_CLASSES.values())
TRUSTED = ("trusted",)  # the default: R16's selection


def classes_of(text: str) -> tuple[str, ...] | None:
    """--classes LIST as its sorted names (`all` alone when it is one: it picks every other), None when one is not
    `trusted`, `all` or a `SELECTABLE` class."""
    names = tuple(sorted({x.strip() for x in text.split(",")}))
    if not names or not all(x in ("trusted", "all", *SELECTABLE) for x in names):
        return None
    return ("all",) if "all" in names else names


def chosen(c: trust_map.Classified, classes: tuple[str, ...]) -> bool:
    """Whether --classes picks the declaration: every one trust_map counts as trusted under `trusted` and `all`, and
    one of a `SELECTABLE` class under `all` or its class's name."""
    return c.trusted and ("trusted" in classes or "all" in classes) or c.cls in SELECTABLE and (
        "all" in classes or c.cls in classes)


def plan(root: Path, base: str, classes: tuple[str, ...] = TRUSTED) -> tuple[list[Mutant], Tree, list[str]]:
    """The mutants in run order of the declarations --classes picks (`chosen`), the tree's checks and imports, and the
    problems that stop the run."""
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
        if not (chosen(c, classes) and d.name and d.kind not in ("theorem", "command", "unrecorded")
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
                    r.end[0], text.count("\n", 0, edit[0]))), text[s:e], new, edit=edit,
                    trust_class=c.cls + (" tied" if c.tied else ""), trusted=c.trusted))
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
    """The mutated module, then the --test modules, the modules of its cone that hold checks for it and those an
    outside --test file imports (review F13: `lake env lean` builds nothing, so without them the file reads their
    pre-mutant `.olean`, and a proof the mutant broke there is never rechecked, cut or seen by the probe)."""
    module, home = module_name(m.file), m.file.rpartition("/")[0]
    cone, todo = {module}, [module]
    while todo:
        new = tree.importers.get(todo.pop(), set()) - cone
        cone |= new
        todo += new
    checks = {x for x in cone for s, e, r, n in tree.roles.get(tree.files[x], ())
              if r == "check" and (deep or tree.files[x].rpartition("/")[0] == home or stated(tree, n, m))}
    return [module, *sorted((checks | {module_name(t) for t in tests} | tree.imported) - {module})]


def moved(before: str, after: str, lines: tuple[int, int]) -> int | None:
    """The first line outside lines[0]..lines[1] that is not where it was in `before` (review F9), else None."""
    old, new = before.split("\n"), after.split("\n")
    return next((n for n in range(1, max(len(old), len(new)) + 1) if not lines[0] <= n <= lines[1]
                 and old[n - 1:n] != new[n - 1:n]), None)


def located(output: str, pattern: re.Pattern = ERROR) -> list[tuple[str, int, int, str]]:
    return [(f, int(n), int(c), message.rstrip()) for f, n, c, message in pattern.findall(output)]


def refutes(message: str, name: str | None) -> bool:
    """Whether `message`, an error at a check whose `#` command is `name` (`command`), states a refutation: one of
    `REFUTED`, whole, or a `#guard_msgs` diff with refutations on one side only (two refutations that differ are one
    statement printed otherwise: an unexpander can read the mutated definition, hunt R7). No `info` is an
    answer: `#reduce` prints a stuck term as readily as a value (review F11), and `#eval`'s is formatted by
    instances Lean picks after elaboration, which can run out of budget and fall back silently, and it can read
    files (hunt Q4, Q7, Q8); a message the diff cannot show as two sides (Lean's `guard_msgs.diff` off) is none."""
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
        return said if all(m.startswith("error:") and REFUTED.fullmatch(m[6:].strip()) for m in said) else None
    expected, generated = answers(sides["-"]), answers(sides["+"])  # the check's truth changed: one side is empty
    return expected is not None and generated is not None and bool(expected) != bool(generated)


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
    `reading` of `probe`: hunt H4, N1, N2, P1-P9). `rebuild` builds
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


def invalid(errors: list[tuple[str, int, str, int]], text: str, lines: tuple[int, int], edit: tuple[int, int]
            ) -> tuple[str, str]:
    """INVALID when every error (file, line, message, column) in the mutated declaration on `lines` of `text` says
    Lean refused the text the mutant wrote (`refused`: a parse error, or a refusal inside `edit`, its offsets in
    `text`), else UNKNOWN at the first that does not (review F12: a tactic that fails or Lean's budget there decides
    nothing, even beside a refusal it may have caused or followed; and a proof term the mutant broke outside its
    edit fails as a tactic does, hunt Q9)."""
    code, starts = code_only(text), [0, *(i + 1 for i, ch in enumerate(text) if ch == "\n"), len(text) + 1]
    lo, hi = starts[lines[0] - 1], starts[min(lines[1], len(starts) - 1)] - 1
    for f, n, message, column in errors:
        at = starts[min(n, len(starts)) - 1] + column
        if not refused(message, in_tactic(code, at, lo, hi) or not edit[0] <= at < max(edit[1], edit[0] + 1)):
            return "UNKNOWN", f"lean/{f}:{n}: {brief(message)}"
    return "INVALID", brief(errors[0][2])


def refused(message: str, elsewhere: bool) -> bool:
    """Whether an error in the mutated declaration says Lean refused its text (review F12): a parse error or one of
    `REFUSED`, not `elsewhere` (in a tactic block, or outside the mutant's own text: a parse error there can be the
    tool's own line padding, hunt R3): INVALID; any other error there makes the mutant UNKNOWN."""
    return not NO_ANSWER.search(message) and not elsewhere and bool(PARSE.match(message) or REFUSED.match(message))


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


# `main`'s phases, in turn
WALL = ("plan", "scratch", "control_build", "probe_install", "control_probes", "mutants", "cleanup", "reads")
LAKE = ("control_build", "probe_install", "control_probes", "mutant_builds", "mutant_checks", "outside_checks",
        "stage_controls", "mutant_probes", "other")  # the steps a Lake run counts under (`Steps.step`)


class Steps:
    """Where a run's time goes (`--json`'s `steps`): `wall` seconds by phase, and Lake's seconds and runs by step,
    summed over the jobs: `Scratch.lake` counts each run under its thread's current `step` ("other" outside one)."""

    def __init__(self):
        self.lock, self.local = threading.Lock(), threading.local()
        self.reset()

    def reset(self) -> None:
        self.wall, self.lake, self.runs = dict.fromkeys(WALL, 0.0), dict.fromkeys(LAKE, 0.0), dict.fromkeys(LAKE, 0)

    def step(self, name: str):
        """A context in which this thread's Lake runs count under `name`."""
        steps = self

        class Step:
            def __enter__(self):
                self.before, steps.local.name = getattr(steps.local, "name", None), name

            def __exit__(self, *_):
                steps.local.name = self.before
        return Step()

    def ran(self, seconds: float) -> None:
        name = getattr(self.local, "name", None) or "other"
        with self.lock:
            self.lake[name] += seconds
            self.runs[name] += 1

    def phase(self, name: str, since: float) -> float:
        """Adds the seconds since `since` to the phase `name`; now."""
        now = time.monotonic()
        self.wall[name] += now - since
        return now

    def record(self) -> dict:
        return {"wall": {k: round(v, 1) for k, v in self.wall.items()},
                "lake": {k: round(v, 1) for k, v in self.lake.items()}, "runs": dict(self.runs)}


STEPS = Steps()


def steps_line(steps: dict) -> str:
    """The printed line of a `steps` record: each phase and step that took any time."""
    def each(d: dict, runs: dict | None = None) -> str:
        return ", ".join(f"{k} {v:g} s" + (f" ({runs[k]})" if runs else "") for k, v in d.items()
                         if v or runs and runs[k])
    return f"trust_mutants: steps: wall {each(steps['wall'])}; lake {each(steps['lake'], steps['runs'])}"


def summed(each: list[dict]) -> dict:
    """The `steps` of the parts `each` added up, key by key."""
    return {"wall": {k: round(sum(s["wall"][k] for s in each), 1) for k in WALL},
            "lake": {k: round(sum(s["lake"][k] for s in each), 1) for k in LAKE},
            "runs": {k: sum(s["runs"][k] for s in each) for k in LAKE}}


def timed(d) -> bool:
    """Whether d is a `steps` record as `Steps.record` writes it: `WALL` and `LAKE` seconds (non-negative numbers)
    and `LAKE` runs (non-negative ints)."""
    return type(d) is dict and set(d) == {"wall", "lake", "runs"} and all(
        type(d[p]) is dict and list(d[p]) == list(keys) and all(type(v) in types and v >= 0 for v in d[p].values())
        for p, keys, types in (("wall", WALL, (int, float)), ("lake", LAKE, (int, float)), ("runs", LAKE, (int,))))


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

    def lake(self, env: dict, *args: str, timeout: float | None = None) -> tuple[int, str]:
        """Lake's exit code and output; past `timeout` seconds the whole process group is killed and the code is
        `TIMED_OUT` (a mutant can make Lean run forever: hunt T5w, T7). Its seconds count in `STEPS`."""
        started = time.monotonic()
        child = subprocess.Popen([lake_outputs.lean_executable(env, "lake"), *args], cwd=self.lean, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        try:
            out, err = child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
            return TIMED_OUT, f"lake {args[0]} did not finish in {timeout:g} s (--build-timeout)"
        finally:
            STEPS.ran(time.monotonic() - started)
        return child.returncode, out + err


def run(m: Mutant, scratch: Scratch, tree: Tree, tests: list[str], outside: list[Path], env: dict,
        deep: bool = False, controls: dict | None = None, hashes: dict | None = None,
        timeout: float | None = None) -> tuple[str, str]:
    """(status, detail) of one mutant, built in `scratch`, whose files are restored afterwards. A proof that fails
    is cut and the build repeated, before any other error is read: a check may fail only because a proof it reads
    failed. Nothing is cut up front, so a cut proof is one the mutant broke (or that fails without it), which is
    what `READS`'s `sorry` means. An error in a check is a kill only when its
    control, the same build without the mutant (the same cuts; `controls` caches it across mutants), passes: what
    fails there too reads a cut proof (review F7: `#eval` refuses a value that depends on `sorry`), so it is cut as
    well and never a kill; nor is one whose check cannot refute the mutated definition (`reading`)."""
    controls = {} if controls is None else controls

    def lake(env_: dict, *args: str) -> tuple[int, str]:  # every run of a mutant's build has `timeout` (UNKNOWN past it)
        return scratch.lake(env_, *args, timeout=timeout)
    hashes = {} if hashes is None else hashes  # (file, span) -> what `probe` gives each check without a mutant
    rebuilt: list[bool] = []  # the stages built with the mutant again, once (a control built them without it)
    current: dict = {"mutant": True, "stage": []}  # whether the stage's last build is the mutant's

    def built_mutant() -> bool:
        if not rebuilt:
            write(m.file, True)
            rebuilt.append(all(build(stage)[0] == 0 for stage in (built[:1], built[1:]) if stage))
        return rebuilt[0]

    probed: dict[str, dict] = {}  # file -> `probe` of its checks in this mutant's build

    def reading(key: tuple) -> str | None:
        """Why the check at `key` cannot refute the mutated definition (`probe`), or None."""
        f, span = key
        if f not in probed:
            outside_file = next((t for t in outside if str(t) == f), None)
            if outside_file is not None:
                built_mutant()
            elif not current["mutant"]:  # the probe reads the mutant's build
                build(current["stage"])
                current["mutant"] = True
            text, mine = (outside_file.read_text(), file_roles(outside_file)) if outside_file else (
                read(f), tree.roles.get(f, ()))
            with STEPS.step("mutant_probes"):
                probed[f] = probe(lake, {**env, "TM_TRUST_MUTATED": m.definition,
                                                 "TM_TRUST_LINES": f"{m.lines[0]} {m.lines[1]}"}, text, mine,
                                  beside(scratch.lean, f), outside_file is not None)
        entry, control = probed[f].get(span), hashes.get(key)
        if entry is None or control is None:
            return "Lean could not elaborate it in the probe"
        if "hyps" in entry["flags"]:
            return "its goal has a hypothesis"
        if "sorry" in entry["flags"]:
            return "it computes through a proof the mutant broke (an instance or `@[csimp]` lemma resting on it)"
        if "axiom" in entry["flags"]:
            return "it computes through an axiom of this tree, which the mutant can make false"
        if "io" in entry["flags"]:
            return "it runs IO (an `initialize`d value, `unsafeIO`), which can read the mutated source"
        if not control["flags"] >= {x for x in entry["flags"] if x.startswith("hash ")}:
            return "Lean elaborates it otherwise than without the mutant"
        if drift := next((c for c, h in entry["consts"].items() if control["consts"].get(c) != h), None):
            return f"{drift}, which it reads, is not what it is without the mutant"
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

    def build(stage: list[str], step: str | None = None) -> tuple[int, list[tuple[str, int, str]]]:
        for attempt in range(3):  # again: Lake can fail with no located error under load
            with STEPS.step(step or ("mutant_builds" if stage == built[:1] else "mutant_checks")):
                code, output = lake(env, "build", *(f"+{x}" for x in stage))
            if code == TIMED_OUT:
                return code, [("", 0, output)]
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
        for stage in (built[:1], built[1:]):  # the mutated module alone first: most mutants end there
            current["stage"] = stage
            for _ in range(12):
                code, found = build(stage) if stage else (0, [])
                if code == 0:
                    break
                if not found[0][0]:
                    return "UNKNOWN", found[0][2]
                roles = [(f, n, message, role(tree, f, n, m)) for f, n, message in found]
                if mutated := [x for x in roles if x[3] == "mutated"]:  # another command's on its last line too
                    # (hunt N10): `invalid` reads only errors inside the mutant's own text as refusals
                    return invalid([(f, n, message, columns.get((f, n, message), 0)) for f, n, message, _ in
                                    mutated], read(m.file), m.lines, (m.start, m.start + len(m.after)))
                if proofs := [x for x in roles if x[3] == "proof" and x[0] not in tests]:
                    for f, n, message in each(proofs):  # cut first: a check may fail only because it reads one
                        if why := cut(f, n, f"the failing proof cannot be cut: {brief(message)}"):
                            return "UNKNOWN", why
                    continue
                key = (tuple(stage), state())
                if (control := controls.get(key)) is None:  # the same build without the mutant
                    write(m.file, False)
                    control = build(stage, "stage_controls")[1]
                    write(m.file, True)
                    current["mutant"] = False  # the stage's build is the control's until it is built again
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
        with STEPS.step("outside_checks"):
            failing = {t: out for t in outside if (out := lake(env, "env", "lean", str(t)))[0]}
        if late := next((t for t in failing if failing[t][0] == TIMED_OUT), None):
            return "UNKNOWN", f"{late}: {failing[late][1]}"
        if not failing:  # review sc-1ae F1: the proofs it broke, each cut, which an --allow reason cites
            broke = [f"lean/{f}:{a}" for f, spans in cuts.items() for a, _ in spans]
            return "SURVIVOR", f"the proofs it breaks: {', '.join(broke)}" if broke else ""
        key = ("outside", tuple(built), state())
        if key not in controls:
            write(m.file, False)
            ok = all(build(stage, "stage_controls")[0] == 0 for stage in (built[:1], built[1:]) if stage)
            with STEPS.step("stage_controls"):
                controls[key] = [t for t in outside if not ok or lake(env, "env", "lean", str(t))[0]]
            write(m.file, True)
        if not (new := [t for t in failing if t not in controls[key]]):
            return "UNKNOWN", f"{next(iter(failing))} fails without the mutant too"
        def again(t: Path, now: dict[str, str]) -> list[tuple[str, int, str]] | None:
            """An outside file's errors with its text `now`, written to a copy in the scratch directory."""
            copy = scratch.lean.parent / "outside" / t.name
            copy.parent.mkdir(exist_ok=True)
            copy.write_text(now[str(t)])
            with STEPS.step("outside_checks"):
                code, output = lake(env, "env", "lean", str(copy))
            found = [(str(t) if f == str(copy) else f, n, message) for f, n, _, message in located(output, LEAN_ERROR)]
            return None if not built_mutant() or code and not found else found

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


REUSED = ("KILLED", "INVALID", "SURVIVOR")  # the verdicts --rescore reuses: no other depends on Lean's time
OVERALL = ("tool", "lean", "tests", "base", "options")  # `inputs`' digests; "files" holds the per-file ones
# the generated inventories of lean/ a check-only change regenerates: no Lean module reads them
INVENTORIES = {"lean/declarations.txt", "lean/statements.txt", "lean/predicates.txt", "lean/axioms.txt"}


def sha(*parts: str) -> str:
    return hashlib.sha256("\0".join(parts).encode()).hexdigest()


class Reads:
    """What a KILLED or INVALID verdict reads of one checkout, as digests (speed-tmrerun's rule.py, measured there
    and in docs/speed/tmchecks): `verdict` writes them on a mutant, `carry` compares them with PREV's.
    - INVALID reads the lines before the mutated declaration in its file and its module's import closure (`scope`);
    - KILLED reads those, and its killing check (the file:line in its detail) with the lines before it in its file
      and that file's import closure (`check`). A check moved by lines added above it keeps its kill.
    Of each file every line counts as written (comments and docstrings too: a `#guard_msgs` reads its docstring;
    blank lines dropped, so a line moved by an insertion above it reads the same) but the lines of a theorem,
    `example` or check command (`classify`: check or proof) with no attribute and a name no counted line names:
    nothing elaborated after them reads them. That is how a check appended before the killing one leaves it read
    the same."""

    def __init__(self, root: Path, tree: Tree, outside: list[Path]):
        self.tree, self.memo = tree, {}
        self.roles = {**tree.roles, **{str(t): file_roles(t) for t in outside}}
        self.texts = {**{f: (root / "lean" / f).read_text() for f in tree.files.values()},
                      **{str(t): t.read_text() for t in outside}}
        codes = {f: code_only(text).split("\n") for f, text in self.texts.items()}
        # file -> line -> the name of the theorem, `example` or check command on it with no attribute
        self.loose: dict[str, dict[int, str | None]] = {
            f: {n: name for s, e, r, name in self.roles.get(f, ()) if r != "other" and "@[" not in "\n".join(
                code[s - 1:e]) for n in range(s, e + 1)} for f, code in codes.items()}
        named = {w for f, code in codes.items() for n, line in enumerate(code, 1) if n not in self.loose[f]
                 for w in re.findall(r"[^\W\d][\w']*", line)}
        for lines in self.loose.values():
            for n in [n for n, name in lines.items() if name and name.rpartition(".")[2] in named]:
                del lines[n]

    def kept(self, f: str, before: int) -> str:
        """The digest of the lines of `f` before line `before` that count."""
        if (f, before) not in self.memo:
            self.memo[f, before] = sha(*(line.rstrip() for n, line in enumerate(
                self.texts[f].split("\n")[:before - 1], 1) if line.strip() and n not in self.loose[f]))
        return self.memo[f, before]

    def imported(self, f: str) -> set[str]:
        """The files of lean/ that `f` imports, transitively."""
        seen, todo = set(), [f]
        while todo:
            new = {self.tree.files[x] for x in imports(self.texts[todo.pop()]) if x in self.tree.files} - seen
            seen |= new
            todo += new
        return seen

    def closure(self, f: str) -> str:
        """The digest of every module of lean/ that `f` imports, transitively, as its lines count."""
        if f not in self.memo:
            self.memo[f] = sha(*(f"{x} {self.kept(x, 1 << 30)}" for x in sorted(self.imported(f))))
        return self.memo[f]

    def scope(self, m: Mutant) -> str:
        return sha(self.kept(m.file, m.lines[0]), self.closure(m.file))

    def check(self, m: Mutant, f: str, first: int, last: int) -> str:
        return sha(self.scope(m), "\n".join(self.texts[f].split("\n")[first - 1:last]), self.kept(f, first),
                   self.closure(f))

    def killer(self, detail: str) -> tuple[str, int] | None:
        """The file and line of the check a KILLED detail cites (`settle`)."""
        if not (at := re.match(r"(\S+?\.lean):(\d+): ", detail)):
            return None
        f = at[1].removeprefix("lean/") if at[1].removeprefix("lean/") in self.tree.roles else at[1]
        return (f, int(at[2])) if f in self.texts else None

    def verdict(self, m: Mutant) -> None:
        """m.reads (and m.killed_at) for a KILLED or INVALID verdict before --allow: what `carry` compares."""
        m.reads, m.killed_at = "", None
        if m.raw_status == "INVALID":
            m.reads = self.scope(m)
        elif m.raw_status == "KILLED" and (at := self.killer(m.raw_detail)):
            if span := next(((s, e) for s, e, r, _ in self.roles.get(at[0], ()) if r == "check" and s <= at[1] <= e),
                            None):
                m.reads, m.killed_at = self.check(m, at[0], *span), span

    def carry(self, m: Mutant, p: dict, built: list[str]) -> tuple[str, str] | None:
        """PREV's KILLED or INVALID verdict `p` on m (status before --allow, detail, reads, killed_at) when what it
        reads reads the same here, its killing check moved to where it now is; else None (m runs: any other status
        too). A kill's check must still be one m's build reads (`built`: `targets`)."""
        if p["status"] == "INVALID" and p["reads"] == self.scope(m):
            return "INVALID", p["detail"]
        if p["status"] != "KILLED" or not p["reads"] or not p["killed_at"] or not (at := self.killer(p["detail"])):
            return None
        (f, n), (s0, e0) = at, p["killed_at"]
        if f in self.tree.roles and module_name(f) not in built:
            return None
        for s, e, *_ in sorted((x for x in self.roles.get(f, ()) if x[2] == "check" and x[1] - x[0] == e0 - s0),
                               key=lambda x: abs(x[0] - s0)):
            if self.check(m, f, s, e) == p["reads"]:
                return "KILLED", re.sub(r"(?<=\.lean:)\d+", str(n - s0 + s), p["detail"], count=1)
        return None


def inputs(root: Path, base: str, tests: list[str], outside: list[Path], deep: bool, classes: tuple[str, ...]) -> dict:
    """What every verdict is computed from, as sha256 digests of bytes, which --rescore compares: the tool's own
    source (with the modules of this repository it imports); every file of lean/ that `Scratch` copies (the sources,
    lakefile, toolchain, manifest and the compiled lists `plan` reads; no `__pycache__`, which Lean never reads and
    differs between machines: speed-tmrescore review F1), with trust_map's table and .gitignore; the outside --test
    files; the base commit; and the options --deep, --test and --classes (a verdict never carries across another
    selection). --max-mutants is not one: it picks which mutants run, never a verdict, so a larger one runs only the
    mutants that now fit. `files` holds each file's digest (the lean/ ones, the table, .gitignore and the outside
    --test files), so a later run can tell which files changed."""
    files: dict[str, str] = {}

    def digest(named: list[tuple[str, Path]], each: bool = True) -> str:
        h = hashlib.sha256()
        for name, path in sorted(named):
            data = os.readlink(path).encode() if path.is_symlink() else path.read_bytes() if path.is_file() else b""
            h.update(f"{name}\0{len(data)}\0".encode() + data)
            if each:
                files[name] = hashlib.sha256(data).hexdigest()
        return h.hexdigest()
    tool = {Path(f).resolve() for m in list(sys.modules.values()) if isinstance(f := getattr(m, "__file__", None), str)}
    lean = []
    for top, dirs, names in os.walk(root / "lean"):
        dirs[:] = [d for d in dirs if d not in (".lake", ".cache", "__pycache__")]
        lean += [Path(top, n) for n in names + [d for d in dirs if Path(top, d).is_symlink()]]
    named = [(Path(os.path.relpath(p, root)).as_posix(), p) for p in outside]
    return {"tool": digest([(p.relative_to(ROOT).as_posix(), p) for p in tool if p.is_relative_to(ROOT / "tools")
                            or p.is_relative_to(ROOT / "lean")], False),
            "lean": digest([(p.relative_to(root).as_posix(), p) for p in [
                *lean, root / "tools/trust-classes.json", root / ".gitignore"]]),
            "tests": digest(named), "base": base,
            "options": json.dumps({"deep": deep, "test": sorted(tests) + [n for n, _ in named],
                                   "classes": list(classes)}), "files": files}


def reach(reads: Reads, found: list[Mutant]) -> set[str]:
    """Every selected declaration's file and the files of lean/ it imports, transitively."""
    return {x for f in {m.file for m in found} for x in {f, *reads.imported(f)}}


def check_only(changed: list[str], reach: set[str], tests: set[str]) -> str | None:
    """Why the files that `changed` (root-relative) are no check-only change, else None: each must be a module of
    lean/ outside `reach` (every selected declaration's file and import closure), an outside --test file (`tests`)
    or a generated inventory (`INVENTORIES`). A lakefile, toolchain, trust_map's table or any other file is none."""
    for name in changed:
        if name in tests or name in INVENTORIES:
            continue
        if not (name.startswith("lean/") and name.endswith(".lean")):
            return f"{name} is no module of lean/, --test file or generated inventory"
        if name.removeprefix("lean/") in reach:
            return f"{name} is a selected declaration's file or in its import closure"
    return None


def previous(path: Path, now: dict, found: list[Mutant], why_not) -> tuple[str, str, dict[str, dict], list[str]] | str:
    """--rescore PREV: (mode, its head, by mutant id its verdict {status before --allow, detail, reads, killed_at},
    the files that changed) when its mutants are `found` and its `inputs` are `now` (mode "identical"), or differ
    only in files `why_not` finds no reason in (mode "checks": the tool, base and options the same, and PREV records
    per-file digests); else why not (a full run)."""
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict) or "inputs" not in data:
            return "it records no inputs"
        old, changed = data["inputs"], []
        if not isinstance(old, dict):
            return "its inputs differ (keys)"
        if differ := [k for k in OVERALL if old.get(k) != now[k]]:
            if fixed := [k for k in differ if k in ("tool", "base", "options")]:
                return f"its inputs differ ({', '.join(fixed)})"
            if not isinstance(old.get("files"), dict):
                return f"its inputs differ ({', '.join(differ)}) and it records no per-file digests"
            changed = sorted(k for k in old["files"].keys() | now["files"].keys()
                             if old["files"].get(k) != now["files"].get(k))
            if why := why_not(changed) if changed else "its per-file digests show no change":
                return f"its inputs differ ({', '.join(differ)}): {why}"
        rows, head = data["mutants"], data["head"]
        if unwritten(rows) or not isinstance(head, str) or not head or any(r["raw_status"] == OTHER for r in rows):
            return "it cannot be read: a status, detail or digest is not one this tool writes"
        if [tuple(r[k] for k in ("id", "file", "line", "definition", "operator", "before", "after")) for r in rows] != [
                (m.id, m.file, m.line, m.definition, m.operator, m.before, m.after) for m in found]:
            return "its mutants are not this tree's"
        if any(r["raw_status"] != r["status"] and "raw_detail" not in r for r in rows):
            return "it records no detail before --allow (`raw_detail`) on a row --allow changed"
        verdicts = {r["id"]: {"status": r["raw_status"], "detail": r.get("raw_detail", r["detail"]),
                              "reads": r.get("reads", ""), "killed_at": r.get("killed_at")} for r in rows}
        return "checks" if differ else "identical", head, verdicts, changed
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        return f"it cannot be read ({type(error).__name__}: {error})"


def evidence(data: dict) -> str:
    """The --json text: one mutant per line."""
    rows = ",\n".join(json.dumps(m, ensure_ascii=False) for m in data["mutants"])
    head = json.dumps({k: v for k, v in data.items() if k != "mutants"}, ensure_ascii=False)
    return f'{head[:-1]}, "mutants": [\n{rows}\n]}}\n'


def show(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= 100 else text[:97] + "..."


def kind(m: Mutant) -> str:
    """Its declaration's class as the lines and the counts by class show it: R16 asks about a trusted one only."""
    return m.trust_class + (", trusted" if m.trusted else "")


def owns(mutant: str, shard: tuple[int, int] | None) -> bool:
    """Whether part K of N (`shard`, None: the whole run) owns the mutant of id M<i>: (i - 1) % N == K - 1."""
    return shard is None or (int(mutant[1:]) - 1) % shard[1] == shard[0] - 1


def tally(found: list[Mutant], part: bool) -> tuple[dict[str, int], dict[str, dict[str, int]]]:
    """The counts by status (every status, OTHER SHARD too in a part's) and the counts by class (those not 0)."""
    statuses = STATUSES + ((OTHER,) if part else ())
    return {s: sum(m.status == s for m in found) for s in statuses}, {
        k: {s: n for s in statuses if (n := sum(m.status == s for m in found if kind(m) == k))}
        for k in sorted({kind(m) for m in found})}


def line(m: Mutant) -> str:
    """A SURVIVOR, UNKNOWN or NOT RUN line."""
    return (f"{m.status} lean/{m.file}:{m.line} {m.definition} ({kind(m)}) {m.operator}: {show(m.before)} -> "
            f"{show(m.after)}{' (' + show(m.detail) + ')' if m.detail else ''}")


def summary(found: list[Mutant], part: bool, seconds: int, rescore: dict | None) -> dict[str, int]:
    """Print the counts line and the by-class lines; the counts."""
    counts, by_class = tally(found, part)
    mode, head, changed = (rescore["mode"], rescore["head"] or "", rescore["changed"]) if rescore else ("full", "", [])
    print("trust_mutants: " + ", ".join(f"{n} {s}" for s, n in counts.items()) + f" in {seconds} s"
          + (f"; {rescore['reused']} reused from {head[:12]} (identical inputs)" if mode == "identical" else
             f"; {rescore['reused']} carried from {head[:12]} (check-only change: {', '.join(changed)})"
             if mode == "checks" else ""))
    for k, n in by_class.items():
        print(f"trust_mutants: {k}: " + ", ".join(f"{x} {s}" for s, x in n.items()))
    return counts


def exit_code(counts: dict[str, int]) -> int:
    """The exit code over these verdicts: 1 a survivor or UNKNOWN left, 3 none left but some NOT RUN, 0 none."""
    return 1 if counts["SURVIVOR"] or counts["UNKNOWN"] else 3 if counts["NOT RUN"] else 0


def record(found: list[Mutant], base: str, head: str, jobs: int, max_mutants: int, deep: bool, tests: list[str],
           seconds: int, classes: list[str], digests: dict, rescore: dict | None, shard: dict | None = None,
           shards: list[dict] | None = None, steps: dict | None = None) -> dict:
    """The --json record, of a run, a part (`shard`) or a merge of the parts (`shards`); `steps`, where its time
    went (`Steps`)."""
    counts, by_class = tally(found, shard is not None)
    return {"base": base, "head": head, "jobs": jobs, "max_mutants": max_mutants, "deep": deep, "tests": tests,
            "seconds": seconds, **({"steps": steps} if steps else {}), "counts": counts, "classes": classes, "class_counts": by_class, "inputs": digests,
            **({"rescore": rescore} if rescore else {}),
            "definitions": [f"lean/{f}: {d}" for f, d in sorted({(m.file, m.definition) for m in found})],
            **({"shard": shard} if shard is not None else {}), **({"shards": shards} if shards else {}),
            "mutants": [{k: v for k, v in asdict(m).items() if k in ROW and (k not in OPTIONAL or v)
                         and (k != "raw_detail" or (m.raw_status, m.raw_detail) != (m.status, m.detail))}
                        for m in found]}


OPTIONAL = ("reused_from", "carried", "reads", "killed_at")  # a row holds these only when they are set
# raw_detail: only on a row --allow changed (review sc-1ae recheck F6); a row without it reads its detail
ROW = {k: t for k, t in get_type_hints(Mutant).items() if k not in ("start", "end", "edit")}  # a row's fields
PART = {"base": str, "head": str, "jobs": int, "max_mutants": int, "deep": bool, "tests": list[str], "seconds": int,
        "classes": list[str], "inputs": dict, "shard": dict}  # what `record` copies from its arguments
SHARD = {"k": int, "n": int, "owned": list[str]}
RESCORE = {"file": str, "head": str | None, "mode": str, "changed": list[str], "reused": int, "rerun": int,
           "full_run": str}  # full_run only when it was one
PLANNED = ("id", "file", "line", "definition", "operator", "before", "after", "lines", "trust_class", "trusted")
AGREED = ("base", "head", "max_mutants", "deep", "tests", "classes", "inputs")  # definitions: the plan's (`unread`)


def typed(v, t) -> bool:
    """Whether the JSON value v is of type t: str, int, bool, dict, None, list[X], tuple[X, Y] (a list of two) or
    X | Y; a bool is no int."""
    o, a = get_origin(t), get_args(t)
    return (type(v) is list and len(v) == len(a) and all(map(typed, v, a)) if o is tuple else
            type(v) is list and all(typed(x, a[0]) for x in v) if o is list else
            any(typed(v, x) for x in a) if o is UnionType else type(v) is t)


def fits(d, schema: dict, optional: tuple = ()) -> bool:
    """Whether d is a dict with exactly the keys of `schema` (those of `optional` may be absent), each of its type."""
    return type(d) is dict and set(d) <= set(schema) and all(
        typed(d[k], t) if k in d else k in optional for k, t in schema.items())


def unwritten(rows) -> str | None:
    """Why `rows` are not a --json record's mutants as `record` writes them, or None: each a row of `ROW`'s fields of
    their types, those of `OPTIONAL` only when set, distinct ids, a status of STATUSES or OTHER, and its raw_status
    that status (an ALLOWED one's: SURVIVOR or UNKNOWN)."""
    if type(rows) is not list:
        return "its mutants are not a list"
    for r in rows:
        if not fits(r, ROW, (*OPTIONAL, "raw_detail")) or not all(r[k] for k in OPTIONAL if k in r):
            return f"the row of {r.get('id') if type(r) is dict else r!r} is not one of its fields and types"
        if r["status"] not in (*STATUSES, OTHER) or not (r["raw_status"] in ("SURVIVOR", "UNKNOWN") if r[
                "status"] == "ALLOWED" else r["raw_status"] == r["status"]):
            return f"{r['id']} has status {r['status']!r} (before --allow {r['raw_status']!r})"
    if len({r["id"] for r in rows}) != len(rows):
        return "its mutant ids repeat"
    return None


def row_mutant(r: dict) -> Mutant:
    """The mutant of a row `record` writes: no span, and its detail before --allow its detail when the row holds none."""
    return Mutant(**{"start": 0, "end": 0, "raw_detail": r["detail"], **r})


def canon(v) -> str:
    """v as one JSON text, keys sorted: two values are the same when theirs are (so true is not 1)."""
    return json.dumps(v, sort_keys=True, ensure_ascii=False)


def idle(r: dict, status: str) -> dict:
    """The row a part writes for a mutant it does not run: r's plan, with `status` (OTHER, or NOT RUN past
    max_mutants) before and after --allow, and no detail."""
    return {**{f: r[f] for f in PLANNED}, "status": status, "raw_status": status, "detail": ""}


def unread(d) -> str | None:
    """Why the record d is not a --shard part's as `record` writes it, or None: the fields `record` copies of their
    types (`PART`, `SHARD`, `RESCORE`), its rows `unwritten`, and the rest (counts, by class, definitions) what
    `record` makes of them."""
    if not (fits({k: v for k, v in d.items() if k in PART}, PART) and fits(d["shard"], SHARD) and (
            "rescore" not in d or fits(d["rescore"], RESCORE, ("full_run",)) and d["rescore"]["mode"] in (
                "full", "identical", "checks"))):
        return "a field is missing or not of its type"
    if "steps" in d and not timed(d["steps"]):
        return "its steps are not a record of seconds by step"
    if why := unwritten(d.get("mutants")):
        return why
    found = [row_mutant(r) for r in d["mutants"]]
    again = record(found, d["base"], d["head"], d["jobs"], d["max_mutants"], d["deep"], d["tests"], d["seconds"],
                   d["classes"], d["inputs"], d.get("rescore"), shard=d["shard"], steps=d.get("steps"))
    if bad := sorted(k for k in again.keys() | d.keys() if canon(again.get(k)) != canon(d.get(k))):
        return f"its {', '.join(bad)} are not what its rows give"
    return None


def merge(out: Path, paths: list[Path]) -> int:
    """--merge OUT PART...: the parts' records as one, the record one run with their options writes (`record`)."""
    def refuse(why: str) -> int:
        return print(f"trust_mutants --merge: {why}", file=sys.stderr) or 2
    try:
        parts = [(json.loads(p.read_text()), p) for p in paths]
    except (OSError, ValueError) as error:
        return refuse(f"a part cannot be read ({type(error).__name__}: {error})")
    if bad := [str(p) for d, p in parts if not (isinstance(d, dict) and isinstance(s := d.get("shard"), dict) and all(
            type(s.get(x)) is int for x in ("k", "n")) and isinstance(s.get("owned"), list))]:
        return refuse(f'no "shard" key {{k, n, owned}} (no --shard part): {", ".join(bad)}')
    if bad := next(((p, why) for d, p in parts if (why := unread(d))), None):
        return refuse(f"{bad[0]} is not a part this tool writes: {bad[1]}")
    parts.sort(key=lambda x: x[0]["shard"]["k"])
    every = ", ".join(str(p) for _, p in parts)
    if len({d["shard"]["n"] for d, _ in parts}) > 1:
        return refuse(f"the parts disagree on shard.n: {', '.join(f'{p} ({d['shard']['n']})' for d, p in parts)}")
    ks, n = [d["shard"]["k"] for d, _ in parts], parts[0][0]["shard"]["n"]
    if ks != list(range(1, n + 1)):
        return refuse(f"shard.k of {n} parts: {sorted(set(range(1, n + 1)) - set(ks))} missing, "
                      f"{sorted({k for k in ks if ks.count(k) > 1})} repeated ({every})")
    (first, path), rows = parts[0], {}
    try:
        for d, p in parts[1:]:
            agreed = [*((f, d.get(f), first.get(f)) for f in AGREED), ("rescore", "rescore" in d, "rescore" in first),
                      *((f"rescore.{x}", (d.get("rescore") or {}).get(x), (first.get("rescore") or {}).get(x))
                        for x in ("mode", "head", "file", "changed", "full_run"))]
            if bad := next((f for f, a, b in agreed if canon(a) != canon(b)), None):
                return refuse(f"the parts disagree on {bad}: {path} and {p}")
            if len(d["mutants"]) != len(first["mutants"]):
                return refuse(f"the parts disagree on the plan (mutants): {path} and {p}")
            for a, b in zip(first["mutants"], d["mutants"]):
                if bad := next((f for f in PLANNED if canon(a[f]) != canon(b[f])), None):
                    return refuse(f"the parts disagree on the plan ({a.get('id')}.{bad}): {path} and {p}")
        run_now = {r["id"] for r in first["mutants"][:max(0, first["max_mutants"])]}
        for d, p in parts:
            mine = {r["id"]: r for r in d["mutants"]}
            for i in d["shard"]["owned"]:
                if i in rows:
                    return refuse(f"{i} is owned twice: {rows[i][1]} and {p}")
                if i not in run_now or mine[i]["status"] in (OTHER, "NOT RUN") or mine[i]["raw_status"] == OTHER:
                    return refuse(f"{i}, owned by {p}, has no verdict there")
                rows[i] = mine[i], p
            if bad := next((r["id"] for r in d["mutants"] if r["id"] not in d["shard"]["owned"] and canon(r) != canon(
                    idle(r, OTHER if r["id"] in run_now else "NOT RUN"))), None):
                return refuse(f"{bad} has a verdict in {p}, which does not run it")
        if missing := sorted(run_now - set(rows)):
            return refuse(f"{missing[0]} is owned by no part ({every})")
        for d, p in parts:
            shard = d["shard"]
            expected = [r["id"] for r in d["mutants"] if r["id"] in run_now and owns(r["id"], (shard["k"], n))]
            if shard["owned"] != expected:
                return refuse(f"{p} shard.owned does not follow the by-id split")
            owned = [rows[i][0] for i in expected]
            rescore_part = d.get("rescore")
            if rescore_part is None:
                if any("reused_from" in r or "carried" in r for r in owned):
                    return refuse(f"{p} has reused rows without rescore")
                continue
            mode, head = rescore_part["mode"], rescore_part["head"]
            reused_rows = [r for r in owned if "reused_from" in r]
            if (rescore_part["reused"] != len(reused_rows) or
                    rescore_part["rerun"] != len(owned) - len(reused_rows)):
                return refuse(f"{p} rescore.reused and rescore.rerun do not match its owned rows")
            if (mode == "full" and (head is not None or reused_rows) or
                    mode != "full" and (not head or any(r["reused_from"] != head for r in reused_rows))):
                return refuse(f"{p} rescore.head does not match its reused rows")
            if (mode == "full" and (rescore_part["changed"] or not rescore_part.get("full_run")) or
                    mode == "identical" and (rescore_part["changed"] or "full_run" in rescore_part) or
                    mode == "checks" and (not rescore_part["changed"] or "full_run" in rescore_part)):
                return refuse(f"{p} rescore.mode does not match its run facts")
            if any(r.get("carried") != ("checks" if mode == "checks" and "reused_from" in r else None)
                   for r in owned):
                return refuse(f"{p} rescore.mode does not match its carried rows")
            reusable = REUSED if mode == "identical" else ("KILLED", "INVALID")
            if any(r["raw_status"] not in reusable for r in reused_rows):
                return refuse(f"{p} rescore.mode cannot reuse the row's raw_status")
        found = [row_mutant(rows.get(r["id"], (r,))[0]) for r in first["mutants"]]
        rescore = first.get("rescore") and {**first["rescore"], **{x: sum(d["rescore"][x] for d, _ in parts)
                                                                   for x in ("reused", "rerun")}}
        shards = [{"k": d["shard"]["k"], "n": n, "jobs": d["jobs"], "seconds": d["seconds"],
                   **({"steps": d["steps"]} if "steps" in d else {})} for d, _ in parts]
        steps = summed([d["steps"] for d, _ in parts]) if all("steps" in d for d, _ in parts) else None
        data = record(found, first["base"], first["head"], sum(s["jobs"] for s in shards), first["max_mutants"],
                      first["deep"], first["tests"], max(s["seconds"] for s in shards), first["classes"],
                      first["inputs"], rescore, shards=shards, steps=steps)
    except (KeyError, TypeError, AttributeError, ValueError) as error:
        return refuse(f"a part cannot be read ({type(error).__name__}: {error})")
    for m in found:
        if m.status in ("SURVIVOR", "UNKNOWN", "NOT RUN"):
            print(line(m))
    counts = summary(found, False, data["seconds"], rescore)
    if steps:
        print(steps_line(steps))
    out.write_text(evidence(data))
    return exit_code(counts)


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
    parser.add_argument("--rescore", type=Path, metavar="PREV.json",
                        help="reuse PREV's KILLED, INVALID and SURVIVOR verdicts when its inputs are this run's, and "
                        "carry its KILLED and INVALID ones across a check-only change")
    parser.add_argument("--build-timeout", type=float, default=1800,
                        help="seconds a mutant's build may run before it is UNKNOWN (default: 1800)")
    parser.add_argument("--classes", default=",".join(TRUSTED), metavar="LIST",
                        help="the declarations selected: trusted (default), all, or trust_map class names "
                        f"({', '.join(SELECTABLE)}), comma-separated")
    parser.add_argument("--shard", metavar="K/N", help="build and judge only part K of N of the mutants that run")
    parser.add_argument("--merge", nargs="+", type=Path, metavar=("OUT.json", "PART.json"),
                        help="write OUT.json, the record of one run, from the --json of its N --shard parts; reads "
                        "only those files (every other option is ignored, --shard and --plan refused)")
    parser.add_argument("--plan", action="store_true",
                        help="print the plan's counts as one JSON line, and build nothing")
    args = parser.parse_args(argv)
    if args.merge:
        if args.shard or args.plan or len(args.merge) < 2:
            return print("--merge OUT.json PART.json...: at least one part, and no --shard or --plan",
                         file=sys.stderr) or 2
        return merge(args.merge[0], args.merge[1:])
    shard = None
    if args.shard is not None:
        if not (got := re.fullmatch(r"([0-9]+)/([0-9]+)", args.shard)) or not 1 <= int(got[1]) <= int(got[2]):
            return print(f"--shard {args.shard!r}: not K/N with 1 <= K <= N", file=sys.stderr) or 2
        shard = int(got[1]), int(got[2])
    root = args.root.resolve()
    if (classes := classes_of(args.classes)) is None:
        return print(f"--classes {args.classes!r}: not a comma-separated list of trusted, all, {', '.join(SELECTABLE)}"
                     " (theorems, proofs and checks, P and T, are never selected)", file=sys.stderr) or 2
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
    STEPS.reset()
    found, tree, fatal = plan(root, base, classes)
    for t in outside:
        try:
            tree.imported |= {x for x in imports(t.read_text()) if x in tree.files}
        except ValueError as error:
            fatal.append(f"{t}: {error}")
    if fatal:
        return print("\n".join(fatal), file=sys.stderr) or 2
    run_now, not_run = found[:max(0, args.max_mutants)], found[max(0, args.max_mutants):]
    mine = [m for m in run_now if owns(m.id, shard)]  # this part's (all of run_now with no --shard)
    if args.plan:
        print(json.dumps({"base": git(root, "rev-parse", base).stdout.strip(), "definitions": len(
            {(m.file, m.definition) for m in found}), "mutants": len(found), "to_run": len(run_now),
            "not_run": len(not_run), **({"owned": len(mine)} if shard else {})}))
        return 0
    for m in run_now:
        if not owns(m.id, shard):
            m.status = m.raw_status = OTHER
    jobs = args.jobs or max(1, min(8, (os.cpu_count() or 1) - int(os.getloadavg()[1])))
    digests = inputs(root, git(root, "rev-parse", base).stdout.strip(), tests, outside, args.deep, classes)
    reused, rescore, why, mode, changed = "", None, "", "full", []
    reads = Reads(root, tree, outside) if args.rescore or args.json else None
    if args.rescore:
        got = previous(args.rescore, digests, found, lambda names: check_only(
            names, reach(reads, found), {Path(os.path.relpath(t, root)).as_posix() for t in outside}))
        if isinstance(got, str):
            why = got
            print(f"trust_mutants: --rescore {args.rescore}: a full run, since {why}", flush=True)
        else:
            mode, reused, verdicts, changed = got
            for m in mine:
                p = verdicts[m.id]
                if mode == "identical" and p["status"] in REUSED:
                    m.status, m.detail = p["status"], p["detail"]
                elif mode == "checks" and (kept := reads.carry(m, p, targets(tree, m, tests, args.deep))):
                    (m.status, m.detail), m.carried = kept, "checks"
                else:
                    continue
                m.reused_from = reused
    todo = [m for m in mine if not m.reused_from]
    env = {**os.environ, "PATH": f"{Path.home() / '.elan/bin'}{os.pathsep}{os.environ.get('PATH', '')}"}
    definitions = sorted({(m.file, m.definition) for m in found})
    print(f"trust_mutants: {len(definitions)} definitions, {len(found)} mutants ({len(todo)} to run), {jobs} jobs, "
          f"base {base[:12]}", flush=True)

    def allowed(m: Mutant) -> None:
        """The current --allow on a verdict, run or reused, which is printed when it is left."""
        m.raw_status, m.raw_detail = m.status, m.detail  # the verdict before --allow, all of it: --rescore reads it
        unread = m.operator == "ctor-drop" and m.status == "SURVIVOR" and not m.detail  # review sc-1ae F1
        if m.status in ("SURVIVOR", "UNKNOWN") and (m.definition, m.operator) in allow and not unread:
            reason = allow[(m.definition, m.operator)]
            m.status, m.detail = "ALLOWED", f"{reason} ({m.detail})" if m.operator == "ctor-drop" else reason
        if m.status in ("SURVIVOR", "UNKNOWN"):
            print(line(m), flush=True)
    for m in mine:
        if m.reused_from:
            allowed(m)
    with tempfile.TemporaryDirectory(prefix="trust-mutants-") as scratch_dir:
        pool: queue.Queue = queue.Queue()
        controls: dict = {}  # the builds without a mutant, by stage and cuts: shared by every scratch
        hashes: dict = {}  # `probe`'s hash of each check without a mutant
        since = STEPS.phase("plan", started)
        if todo:  # the control build, and each check's elaboration, only for the mutants that run
            first = Scratch(root / "lean", Path(scratch_dir))
            since = STEPS.phase("scratch", since)
            with STEPS.step("control_build"):
                code, output = first.lake(env, "build", *sorted({f"+{x}" for m in todo for x in targets(
                    tree, m, tests, args.deep)}))
                failing = [t for t in outside if first.lake(env, "env", "lean", str(t))[0]]
            since = STEPS.phase("control_build", since)
            if code or failing:
                return print(f"the checks fail without a mutant:\n{output[-3000:]}{failing}", file=sys.stderr) or 2
            files = {f: (first.lean / f, tree.roles[f]) for f in sorted({tree.files[x] for m in todo for x in targets(
                tree, m, tests, args.deep)}) if any(r == "check" for _, _, r, _ in tree.roles.get(f, ()))}
            files.update({str(t): (t, file_roles(t)) for t in outside})
            with STEPS.step("probe_install"):
                if not install(lambda *a: first.lake(env, *a), first.lean):
                    return print("the Lean probe (READS) does not compile", file=sys.stderr) or 2
            since = STEPS.phase("probe_install", since)

            def control(item: tuple[int, tuple[str, tuple[Path, list]]]) -> dict:
                i, (key, (path, roles)) = item
                with STEPS.step("control_probes"):
                    got = probe(first.lake, env, path.read_text(), roles, beside(first.lean, key),
                                Path(key).is_absolute())
                return {(key, span): said for span, said in got.items()}
            with ThreadPoolExecutor(max_workers=jobs) as executor:  # each check's elaboration without a mutant
                hashes.update({k: v for part in executor.map(control, enumerate(files.items())) for k, v in
                               part.items()})
            since = STEPS.phase("control_probes", since)
            pool.put(first)
            for _ in range(min(jobs, len(todo)) - 1):
                pool.put(Scratch(root / "lean", Path(scratch_dir), first))
            since = STEPS.phase("scratch", since)

        def one(m: Mutant) -> None:
            scratch = pool.get()
            try:
                m.status, m.detail = run(m, scratch, tree, tests, outside, env, args.deep, controls, hashes,
                                         args.build_timeout)
            finally:
                pool.put(scratch)
            allowed(m)

        with ThreadPoolExecutor(max_workers=jobs) as executor:
            list(executor.map(one, todo))
        since = STEPS.phase("mutants", since)
    since = STEPS.phase("cleanup", since)  # the scratch copies removed
    for m in not_run:
        print(line(m))
    seconds = round(time.monotonic() - started)
    if args.rescore:
        rescore = {"file": str(args.rescore), "head": reused or None, "mode": mode, "changed": changed,
                   "reused": len(mine) - len(todo), "rerun": len(todo), **({} if reused else {"full_run": why})}
    counts = summary(found, shard is not None, seconds, rescore)
    if args.json:
        for m in found:  # what each KILLED and INVALID verdict reads, for a later --rescore
            reads.verdict(m)
        STEPS.phase("reads", since)
    print(steps_line(steps := STEPS.record()), flush=True)
    if args.json:
        args.json.write_text(evidence(record(
            found, digests["base"], git(root, "rev-parse", "HEAD").stdout.strip(), jobs, args.max_mutants, args.deep,
            args.test, seconds, list(classes), digests, rescore,
            shard={"k": shard[0], "n": shard[1], "owned": [m.id for m in mine]} if shard else None, steps=steps)))
    return exit_code(counts)


if __name__ == "__main__":
    sys.exit(main())
