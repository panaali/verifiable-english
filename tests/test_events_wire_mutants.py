"""Mutants of the `events` block's decoder each fail a fixture (et-4 review F1).

`lean/VE/Events/WireExamples.lean` pins `decodeEvents` (docs/spec/events-time-causation.md 4, items 2 to 7) with
`#guard`s, each check refused at its boundary and accepted just inside it. The review found seven mutants outside
`tools/trust_mutants.py`'s operators that kept every guard passing: a state role's wording, a state role's signature
and a state sort left unchecked, a state's and a link's unknown field accepted, a link's cause sort read as its effect
sort, and the node limit read on the first premise only. This test plants those seven and, generated from
`Wire.lean`'s own source, every mutant of their kinds:

- `drop`: each check step of a `do` block (a statement that can refuse and gives no value: `objectAt`, `firstFault`,
  a `check…` call, an `if … throw`) replaced by `pure ()`, so each check has a fixture that it alone refuses;
- `sibling`: each role list (`roleSorts V`, `eventSorts V`, `stateSorts V`; `rolePreds V` and its event and state
  halves) replaced by each of its siblings, and a link's cause and effect sorts read for each other, so each check
  reads every list it names;
- `swap`: each two adjacent check steps of a `do` block swapped when the second does not read what the first binds,
  so the fault order (spec 4's items, then each item's checks, as written) is pinned by a fixture with both faults.

By hand beside them: `HOOK`, et-4b's route hook, one per claimed behaviour, and `ORDER`, the two order pins across
the `decodeThroughLinks`/`finishEvents` split that no swap of one `do` block reaches (DRI 2026-11-08, et-4b-gate 3).

The checks' own conditions get the tool's operators (`--classes all`: docs/events-time-causation/et-4/
all-mutants.json). Each mutant is elaborated with `lake env lean` as one file, `Wire.lean` then the fixtures; it is
killed when `Wire.lean` elaborates and every error is a failed `#guard`. The unmutated file must elaborate cleanly, a
mutant must change the source, and a mutant listed as equivalent must elaborate and pass every fixture.
"""
from __future__ import annotations

from functools import partial
import json
import os
import re
import shutil
import subprocess

import pytest

import lean_pool
from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

WIRE = LEAN / "VE/Events/Wire.lean"
EXAMPLES = LEAN / "VE/Events/WireExamples.lean"
GUARD_FAILED = "did not evaluate to `true`"
ERROR = re.compile(r"^\S+?\.lean:(\d+):\d+: error", re.M)

# The review's seven (et-4 review F1, its probe's replacements as it wrote them).
REVIEW = {
    "review-state-role-wording": ("(rolePreds V).map fun p => (!(W", "(V.events.map (·.on)).map fun p => (!(W"),
    "review-state-role-signature": ("V.states.flatMap", "([]:List StateSort).flatMap"),
    "review-state-sort-declared": ("(roleSorts V).map fun s", "(eventSorts V).map fun s"),
    "review-state-fields": ('objectAt j ".states"', "pure () --"),
    "review-link-fields": ('objectAt j ".links"', "pure () --"),
    "review-link-cause-sort": ("contains c", "contains e"),
    "review-premise-after-first": ("(sized.map fun (l, n)", "((sized.take 1).map fun (l, n)"),
}

# et-4b's hook (seeded bugs): what the kinds below do not reach, each one behaviour the report claims.
HOOK = {
    "hook-no-profile-test": ('if (VE.Compose.listedProfiles environment).contains "events@0" then', "if true then"),
    "hook-no-row": ("let _ ← VE.Compose.gateOf VE.Compose.profileTable (VE.Compose.listedProfiles environment)",
                    "let _ := ()"),
    "hook-no-open-check": ("decodeEventsWith (checkOpen (openTermsOf terms)) environment", "decodeEvents environment"),
    "open-ignores-decider": ('(l.predicate, l.decidedBy.getD "unstated")', '(l.predicate, "the drafters")'),
    "open-first-link-only": ("firstFault (ls.map fun l =>\n    (!opens", "firstFault ((ls.take 1).map fun l =>\n    (!opens"),
    "open-terms-name-only": ('.ok n, .ok d => some (n, d)', '.ok n, _ => some (n, "the drafters")'),
    "hook-dates-before-open": ("let d ← decodeEventsWith (checkOpen (openTermsOf terms)) environment",
                               "let _ ← decodeEvents environment\n    "
                               "let d ← decodeEventsWith (checkOpen (openTermsOf terms)) environment"),
    "view-keeps-the-block": ('(·.1 != "events")', "(fun _ => true)"),
    "view-keeps-the-profile": ('.filter (· != "events@0")', ""),
    "view-no-dates": ("(constants ++ dated)", "constants"),
    "view-drops-the-constants": ("(constants ++ dated)", "dated"),
    "view-anchor-as-iso": ('if d.V.anchor == some D then "the date of this document" else D.iso', "D.iso"),
    "charge-states-once": ("2 * states.length", "states.length"),
    "charge-no-links": ("+ raw.length > VE.Limits.maxPredicates", "> VE.Limits.maxPredicates"),
    "charge-off-by-one": ("raw.length > VE.Limits.maxPredicates", "raw.length ≥ VE.Limits.maxPredicates"),
    "sum-off-by-one": ("(sized.map (·.2)).sum > limit", "(sized.map (·.2)).sum ≥ limit"),
    "sum-first-only": ("(sized.map (·.2)).sum > limit", "((sized.take 1).map (·.2)).sum > limit"),
    "repeat-ignores-seen": ("Std.HashSet.ofList seen", "(∅ : Std.HashSet String)"),
    "repeat-last-wins": ("| some r => (some r, acc.2)", "| some _ => (if acc.2.contains n then some n else acc.1, acc.2)"),
}

# Spec 4's item order across the split (reviews/dri-decisions-20261108-et-4b-gate.md item 3): the two swaps the
# generator made before `decodeEvents` was split into `decodeThroughLinks` and `finishEvents`, each killed by a
# fixture with both faults in WireExamples.lean: each item-4 sort fault (`EventsSort: deed` and the rest) beside the
# base block's link, whose sorts are then no role sorts; "Item 5 before item 6" (and `LinkNotOpen` on `badDate`).
ORDER = {
    "order-links-before-roles": ("  checkRoles W V0\n  pure ⟨W, V0, ← checkLinks W V0 raw, dates, anchor⟩",
                                 "  let ls ← checkLinks W V0 raw\n  checkRoles W V0\n  pure ⟨W, V0, ls, dates, anchor⟩"),
    "order-dates-before-links": ("  pure ⟨W, V0, ← checkLinks W V0 raw, dates, anchor⟩",
                                 "  let _ ← checkDates W dates anchor\n  pure ⟨W, V0, ← checkLinks W V0 raw, dates, anchor⟩"),
}

# Lists one check may read for another: each is replaced by each other one of its group.
SIBLINGS = (("roleSorts V", "eventSorts V", "stateSorts V"),
            ("rolePreds V", "(V.events.map (·.on))", "(V.states.flatMap fun s => [s.begins, s.ends])"),
            ("contains c", "contains e"))

# The statements that start a check step whatever their form; `if … throw` is one too.
HEADS = ("objectAt ", "firstFault ", "checkDay ", "checkRoles ", "checkPremiseSize ", "open_ ")

# Mutants that change the source and that no input tells apart from it, each with the reason.
EQUIVALENT = {
    "sibling-checkLinks-rolePreds-V-0-(V.events.map-(·.on))":
        "a link on a role predicate is refused as EventsSort first: a role's second sort is the day, never a role sort",
    "sibling-checkLinks-rolePreds-V-0-(V.states.flatMap-fun-s-=>-[s.begins,-s.ends])":
        "a link on a role predicate is refused as EventsSort first: a role's second sort is the day, never a role sort",
    "sibling-checkRoles-rolePreds-V-1-(V.states.flatMap-fun-s-=>-[s.begins,-s.ends])":
        "an event role named twice is refused first: one predicate has one signature, so two events on it share a "
        "sort (DuplicateDeclaration: event sort), and an event and a state on it share a sort (state sort)",
}


def _definitions(text: str) -> list[tuple[str, int, int]]:
    """(name, first line, line after the last) of each `def` of `text`: it runs to the next line that is not
    indented."""
    lines, out = text.split("\n"), []
    for i, line in enumerate(lines):
        if m := re.match(r"def ([\w.?]+)", line):
            j = i + 1
            while j < len(lines) and lines[j].startswith(" "):
                j += 1
            out.append((m.group(1), i, j))
    return out


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _blocks(text: str) -> list[tuple[str, list[tuple[int, int]]]]:
    """(definition, its statements as (first line, line after the last)) for each `do` block of each definition: a
    statement is a line at the block's indentation and the lines after it indented further or starting `else`."""
    lines, out = text.split("\n"), []
    for name, lo, hi in _definitions(text):
        for i in range(lo, hi):
            if not lines[i].rstrip().endswith(" do") or i + 1 >= hi:
                continue
            at, stmts, j = _indent(lines[i + 1]), [], i + 1
            while j < hi and _indent(lines[j]) >= at:
                k = j + 1
                while k < hi and (_indent(lines[k]) > at or lines[k][at:].startswith("else")):
                    k += 1
                stmts.append((j, k))
                j = k
            out.append((name, stmts))
    return out


def _bound(stmt: str) -> set[str]:
    """The names a `let … ←` binds."""
    m = re.match(r"\s*let\s+(.*?)\s*←", stmt)
    return set(re.findall(r"[A-Za-z_][\w']*", m.group(1))) if m else set()


def _step(stmt: str) -> bool:
    """A statement that can refuse: a check, an `if … throw`, or a `let … ←` (each bind may throw)."""
    s = stmt.lstrip()
    return s.startswith(HEADS) or s.startswith("if ") and "throw" in stmt or bool(_bound(stmt))


def _result(stmt: str) -> bool:
    """The statement that gives a block's value (only a last statement does)."""
    return bool(re.search(r"\bpure\b", stmt)) and not _bound(stmt)


def _droppable(stmt: str) -> bool:
    """A check step that gives no value: neither a bind nor the block's result."""
    return _step(stmt) and not _bound(stmt) and not _result(stmt)


def _slug(s: str) -> str:
    return re.sub(r"\s+", "-", s.strip())


def _generated(text: str) -> dict[str, str]:
    """{id: mutated Wire.lean} for the `drop`, `sibling` and `swap` mutants of `text`."""
    lines, out = text.split("\n"), {}
    for name, stmts in _blocks(text):
        for n, (a, b) in enumerate(stmts):
            stmt = "\n".join(lines[a:b])
            if _droppable(stmt):
                out[f"drop-{name}-{n}"] = "\n".join(lines[:a] + [" " * _indent(lines[a]) + "pure ()"] + lines[b:])
        for n, ((a, b), (c, d)) in enumerate(zip(stmts, stmts[1:])):
            first, second = "\n".join(lines[a:b]), "\n".join(lines[c:d])
            if not (_step(first) and _step(second)) or _result(second):
                continue
            if any(re.search(rf"(?<![\w.']){re.escape(v)}(?![\w'])", second) for v in _bound(first)):
                continue
            out[f"swap-{name}-{n}"] = "\n".join(lines[:a] + lines[c:d] + lines[a:b] + lines[d:])
    for name, lo, hi in _definitions(text):
        start, end = (sum(len(x) + 1 for x in lines[:k]) for k in (lo, hi))
        for group in SIBLINGS:
            for term in group:
                for k, m in enumerate(re.finditer(re.escape(term), text[start:end])):
                    s, e = start + m.start(), start + m.end()
                    for other in group:
                        if other != term:
                            out[f"sibling-{name}-{_slug(term)}-{k}-{_slug(other)}"] = text[:s] + other + text[e:]
    return out


def _review(name: str, text: str) -> str:
    old, new = REVIEW.get(name) or HOOK.get(name) or ORDER[name]
    assert text.count(old) == 1, name
    return text.replace(old, new)


def _mutants() -> dict[str, str]:
    text = WIRE.read_text()
    return {**{n: _review(n, text) for n in (*REVIEW, *HOOK, *ORDER)}, **_generated(text)}


MUTANTS = _mutants()


def mutant_cases() -> dict[str, str]:
    """Each mutant's operator, definition and changed lines by name: tools/gate_collection.py pairs by it."""
    before, out = WIRE.read_text().split("\n"), {}
    for name, text in MUTANTS.items():
        after = text.split("\n")
        start = len(os.path.commonprefix([before, after]))
        end = len(os.path.commonprefix([before[start:][::-1], after[start:][::-1]]))
        out[name] = json.dumps([*name.split("-")[:2], before[start:len(before) - end], after[start:len(after) - end]])
    return out


def _assemble(wire: str) -> str:
    """One file: `Wire.lean`, then the fixtures without their imports."""
    examples = "\n".join(line for line in EXAMPLES.read_text().split("\n") if not line.startswith("import "))
    return wire.rstrip("\n") + "\n" + examples


def _unmutated() -> str:
    return _assemble(WIRE.read_text())


def _mutant(name: str) -> str:
    return _assemble(MUTANTS[name])


def _killed(out: str, product_lines: int) -> bool:
    """Every error is a failed `#guard` after `Wire.lean`'s lines, and there is one."""
    lines = [int(n) for n in ERROR.findall(out)]
    return 0 < out.count(GUARD_FAILED) == len(lines) and all(n > product_lines for n in lines)


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def _elaborate(lake: str, tmp_path, source: str) -> subprocess.CompletedProcess:
    file = tmp_path / "EventsWireMutant.lean"
    file.write_text(source)
    return subprocess.run([lake, "env", "lean", str(file)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


SOURCES = {"test_the_unmutated_sources_elaborate_cleanly": _unmutated,
           "test_every_mutant_fails_a_fixture": _mutant,
           "test_an_equivalent_mutant_elaborates_and_passes_every_fixture": _mutant}


@pytest.fixture(scope="module")
def elaborated(lake, request, tmp_path_factory):
    """The selected tests' sources, elaborated at once (`tests/lean_pool.py`); empty under xdist or at width 1."""
    return lean_pool.elaborate_selected(request, SOURCES, partial(_elaborate, lake),
                                        lambda: tmp_path_factory.mktemp("events-wire-pool"))


@pytest.fixture
def elaborate(lake, elaborated):
    return lambda tmp_path, source: lean_pool.result(elaborated, source, lambda: _elaborate(lake, tmp_path, source))


def test_the_unmutated_sources_elaborate_cleanly(elaborate, tmp_path):
    done = elaborate(tmp_path, _unmutated())
    assert done.returncode == 0 and "error" not in done.stdout + done.stderr, done.stdout + done.stderr


@pytest.mark.parametrize("name", sorted(set(MUTANTS) - set(EQUIVALENT)))
def test_every_mutant_fails_a_fixture(elaborate, tmp_path, name):
    assert MUTANTS[name] != WIRE.read_text(), f"{name} changes nothing"
    done = elaborate(tmp_path, _mutant(name))
    out = done.stdout + done.stderr
    assert done.returncode != 0, f"{name} survives every #guard"
    assert _killed(out, MUTANTS[name].rstrip("\n").count("\n") + 1), \
        f"{name} fails in Wire.lean or not only at #guards:\n{out[:4000]}"


@pytest.mark.parametrize("name", sorted(EQUIVALENT))
def test_an_equivalent_mutant_elaborates_and_passes_every_fixture(elaborate, tmp_path, name):
    """If a fixture kills a mutant listed as equivalent, it was not equivalent, and the list is wrong."""
    assert MUTANTS[name] != WIRE.read_text()
    done = elaborate(tmp_path, _mutant(name))
    assert done.returncode == 0, f"{name} ({EQUIVALENT[name]}) fails:\n{(done.stdout + done.stderr)[:4000]}"


def test_the_killed_check_reads_only_guard_failures_after_the_product_code():
    guard = f"F.lean:90:0: error: Expression\n  x == y\n{GUARD_FAILED}\n"
    assert _killed(guard, 80) and not _killed("", 80)
    assert not _killed(guard, 95), "a failure inside Wire.lean's lines is the mutant's own error"
    assert not _killed("F.lean:85:2: error: unknown identifier 'x'\n" + guard, 80)


def test_the_generated_mutants_cover_every_check_step_list_and_order():
    """The generator reads `Wire.lean` as written: every `do` block's check steps are dropped, every adjacent pair of
    independent steps is swapped, every role list is read for each sibling, and the review's seven are among the
    generated kinds (each is a drop, a sibling or a cut the tool's `list-first` makes)."""
    text = WIRE.read_text()
    generated = _generated(text)
    blocks = dict(_blocks(text))
    assert set(blocks) == {"objectAt", "decodeEventSort", "decodeStateSort", "decodeLinkRaw", "checkRoles", "checkLinks",
                           "checkDates", "checkPremiseSize", "decodeThroughLinks", "finishEvents", "decodeEventsWith",
                           "routeView", "eventsHook"}
    drops = {n.rsplit("-", 1)[0] for n in generated if n.startswith("drop-")}
    assert drops == {f"drop-{d}" for d in blocks} - {"drop-routeView", "drop-eventsHook"}  # binds and a result only
    # Every `throw` of a `do` block is in a dropped step, a bind (whose value is needed), or a result.
    lines = text.split("\n")
    for name, stmts in blocks.items():
        for a, b in stmts:
            stmt = "\n".join(lines[a:b])
            if "throw" in stmt:
                assert _droppable(stmt) or _bound(stmt) or "pure" in stmt, (name, stmt)
    assert len([n for n in generated if n.startswith("drop-checkRoles-")]) == len(blocks["checkRoles"]) == 6
    assert len([n for n in generated if n.startswith("swap-checkRoles-")]) == 5
    # Spec 4's items 3 and 4 as the decoder runs them, and the open-term check a route adds before the dates.
    assert "swap-decodeThroughLinks-11" in generated and "drop-decodeEventsWith-1" in generated
    siblings = [n for n in generated if n.startswith("sibling-")]
    assert len(siblings) == sum(text.count(t) * (len(g) - 1) for g in SIBLINGS for t in g) == 22
    # The review's seven are of these kinds: five a generated mutant makes as written, up to the dropped line's
    # remainder; the premise cut is the tool's `list-first`.
    same = {"review-state-role-wording": "sibling-checkRoles-rolePreds-V-0-(V.events.map-(·.on))",
            "review-state-sort-declared": "sibling-checkRoles-roleSorts-V-0-eventSorts-V",
            "review-state-fields": "drop-decodeStateSort-0", "review-link-fields": "drop-decodeLinkRaw-0",
            "review-link-cause-sort": "sibling-checkLinks-contains-c-0-contains-e"}
    for review, name in same.items():
        changed = [[i for i, (x, y) in enumerate(zip(lines, MUTANTS[m].split("\n"))) if x != y] for m in (review, name)]
        assert changed[0] == changed[1] and len(changed[0]) == 1, (review, name)
    assert set(EQUIVALENT) <= set(generated)
