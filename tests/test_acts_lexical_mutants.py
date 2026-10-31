"""Seeded mutants of the act-phrase decoder each fail a fixture (ap-1a review F1).

`lean/VE/Acts/LexicalExamples.lean` pins `VE.Acts.Lexical.check` and the profile-aware regulated decoder of
`VE.Norms.Wire` (`canonicalActIn`, `decodeRegulatedWith`, `decodeRegulatedIn`) with `#guard`s. The review found four
mutants that kept every guard passing: slots counted rather than read in order, a form allowed on every role, and a
permission's or an obligation's act checked by today's `canonicalAct` under `acts@0`; a fifth (the document's fixed
phrases not passed on) was caught only by a proof. This test plants those five and a mutant for every way the same
kind of behaviour can be lost, generated from the decoder's own source:

- every guard (`if … then`, `unless … do`, `if let`) made never to fire, and every conjunct of one dropped;
- every comparison (`==`, `!=`, `≤`, `≥`) negated or moved off its boundary;
- every role a comparison or an arm names replaced by each other role, every default arm's value negated;
- every read of `acts` fixed to `true` and to `false`, every read of the profiles' `acts@0` negated;
- the act check of each role replaced by today's `canonicalAct`, and every pass of the fixed phrases `fx` made `[]`.

Each mutant is elaborated with `lake env lean` in one file with the fixtures, the proofs replaced by `sorry`, so a
fixture must catch it: it must fail, and only at `#guard`s. The unmutated sources must elaborate cleanly, and every
mutation must change the source exactly once.
"""
from __future__ import annotations

from functools import partial
import re
import shutil
import subprocess

import pytest

import lean_pool
from subprocesses import HANG_TIMEOUT
from tests.lean_build import LEAN, lean_build

LEXICAL, WIRE, EXAMPLES = (LEAN / f"VE/{name}.lean" for name in ("Acts/Lexical", "Norms/Wire", "Acts/LexicalExamples"))
GUARD_FAILED = "did not evaluate to `true`"
THEOREMS = "/-! ### Theorems (4.3) -/"
INLINED = {"import VE.Acts.Lexical", "import VE.Norms.Wire"}
# The definitions the mutants change, by file: AP-1's act check and the decoder that calls it.
SCOPE = {"lexical": ("checkWith", "joinCheck"), "wire": ("canonicalActIn", "decodeRegulatedWith", "decodeRegulatedIn")}
# `check` is `checkWith (joinCheck name)` (ap-3d: conditions 1 to 5, then 6, in the order of its old body): its two
# parts keep `check`'s mutant names, numbered across both in source order.
LABEL = {"checkWith": "check", "joinCheck": "check"}
ROLES = ("permission", "obligation", "plain")


def _sources() -> dict[str, str]:
    return {"lexical": LEXICAL.read_text(), "wire": WIRE.read_text()}


def _without_proofs(text: str) -> str:
    """`text` with every tactic proof of a theorem replaced by `sorry` (a mutant must be caught by a fixture)."""
    lines, out, skipping = text.split("\n"), [], False
    for line in lines:
        if skipping and line.startswith(" "):
            continue
        skipping = False
        out.append(line)
        if line.rstrip().endswith(":= by") and any(o.startswith("theorem ") for o in out[-6:]):
            out[-1] = line.rstrip() + " sorry"
            skipping = True
    return "\n".join(out)


def _split_imports(text: str) -> tuple[list[str], str]:
    lines = text.split("\n")
    return ([line for line in lines if line.startswith("import ")],
            "\n".join(line for line in lines if not line.startswith("import ")))


def _assemble(sources: dict[str, str], examples: str) -> str:
    """One file: `Lexical.lean` without its theorems, `Wire.lean` and the fixtures, with their outside imports."""
    lexical = sources["lexical"]
    lexical = lexical[:lexical.index(THEOREMS)] + "end VE.Acts.Lexical\n"
    imports, bodies = [], []
    for text in (lexical, _without_proofs(sources["wire"]), examples):
        own, body = _split_imports(text)
        imports += [line for line in own if line not in INLINED and line not in imports]
        bodies.append(body)
    return "\n".join(imports) + "\n" + "\n".join(bodies)


def _masked(text: str) -> str:
    """`text` with the inside of every string literal blanked (same length), so a message is never read as code."""
    return re.sub(r'"[^"\n]*"', lambda m: '"' + " " * (len(m.group()) - 2) + '"', text)


def _span(text: str, name: str) -> tuple[int, int]:
    """The definition `name`: its `def` line to the next line that is not indented (its body)."""
    m = re.search(rf"^def {re.escape(name)} ", text, re.M)
    assert m, name
    end = re.compile(r"^\S", re.M).search(text, text.index("\n", m.start()) + 1)
    return m.start(), end.start() if end else len(text)


def _top_level(text: str, sep: str) -> list[tuple[int, int]]:
    """The spans of `text` split at the operator `sep`, with any spacing or line break around it, outside parentheses
    and brackets (`text` masked)."""
    parts, depth, start, i = [], 0, 0, 0
    spaced = re.compile(rf"\s+{re.escape(sep)}\s+")
    while i < len(text):
        depth += {"(": 1, "[": 1, ")": -1, "]": -1}.get(text[i], 0)
        if depth == 0 and (m := spaced.match(text, i)):
            parts.append((start, i))
            start = i = m.end()
            continue
        i += 1
    return parts + [(start, len(text))]


GUARD = re.compile(r"(?<![\w.])(if|unless) (?!let )(.*?) (then|do)(?= |$)", re.M | re.S)
IF_LET = re.compile(r"^( +)if let (.+?) := (.*?) then(?= |$)", re.M | re.S)
COMPARISON = re.compile(r" (==|!=|≤|≥) ")
ROLE = re.compile(r"(?:role (?:==|!=) \.|Role\.)(permission|obligation|plain)\b")
DEFAULT_ARM = re.compile(r'\| \.str "(?:allow|deny)" => pure (true|false)\b')
ACTS = re.compile(r"(?<![\w.])acts(?!\w)")
ACTS_PROFILE = re.compile(r'profiles\.contains "acts@0"')
FX = re.compile(r"(?<![\w.])fx(?!\w)")
NEGATED = {"==": "!=", "!=": "==", "≤": ">", "≥": "<"}
OFF_BOUNDARY = {"≤": "<", "≥": ">"}


def _at(where: str, start: int, end: int, new: str):
    def mutate(sources: dict[str, str]) -> dict[str, str]:
        text = sources[where]
        return {**sources, where: text[:start] + new + text[end:]}
    return mutate


def _replace(where: str, old: str, new: str):
    def mutate(sources: dict[str, str]) -> dict[str, str]:
        text = sources[where]
        assert text.count(old) == 1, f"{old!r} occurs {text.count(old)} times"
        return {**sources, where: text.replace(old, new)}
    return mutate


def _generated() -> dict:
    """The mutants of the module docstring's five kinds, named by kind, definition and number in source order."""
    sources, mutants, made = _sources(), {}, set()

    def add(kind: str, name: str, where: str, start: int, end: int, new: str) -> None:
        """A mutant, unless an earlier one makes the same source (`acts-true` of `acts && c` is a dropped conjunct)."""
        name = LABEL.get(name, name)
        mutate = _at(where, start, end, new)
        source = mutate(sources)[where]
        if source in made:
            return
        made.add(source)
        k = sum(1 for other in mutants if other.rsplit("-", 1)[0] == f"{kind}-{name}")
        mutants[f"{kind}-{name}-{k + 1}"] = mutate

    for where, names in SCOPE.items():
        text = sources[where]
        masked = _masked(text)
        for name in names:
            lo, hi = _span(masked, name)
            body = masked.index(":=", lo)
            for m in GUARD.finditer(masked, lo, hi):
                never = "false" if m[1] == "if" else "true"
                add("guard-off", name, where, *m.span(2), never)
                conjuncts = _top_level(masked[m.start(2):m.end(2)], "&&")
                for s, e in conjuncts if len(conjuncts) > 1 else []:
                    add("conjunct-dropped", name, where, m.start(2) + s, m.start(2) + e, "true")
            for m in IF_LET.finditer(masked, lo, hi):
                add("guard-off", name, where, *m.span(3), f"(if false then {text[m.start(3):m.end(3)]} else none)")
            for m in COMPARISON.finditer(masked, body, hi):
                add("negated", name, where, *m.span(1), NEGATED[m[1]])
                if m[1] in OFF_BOUNDARY:
                    add("off-boundary", name, where, *m.span(1), OFF_BOUNDARY[m[1]])
            for m in ROLE.finditer(masked, body, hi):
                for other in ROLES:
                    if other != m[1]:
                        add(f"role-{other}", name, where, *m.span(1), other)
            for m in DEFAULT_ARM.finditer(text, body, hi):
                add("default-negated", name, where, *m.span(1), "false" if m[1] == "true" else "true")
            for m in ACTS.finditer(masked, body, hi):
                for value in ("true", "false"):
                    add(f"acts-{value}", name, where, *m.span(), value)
            for m in ACTS_PROFILE.finditer(text, body, hi):
                add("acts-profile-negated", name, where, *m.span(), f"!{text[m.start():m.end()]}")
            for m in FX.finditer(masked, body, hi):
                add("fx-dropped", name, where, *m.span(), "([] : List String)")
            if name == "decodeRegulatedWith":
                call = masked.index("actCheck name", body, hi)
                for role in ROLES:
                    add(f"todays-check-{role}", name, where, call, call + len("actCheck"),
                        f"(if role == .{role} then canonicalAct else actCheck)")
    return mutants


SLOTS = "slots == (List.range arity).map toString"
MUTANTS = {
    # The review's four (F1), as it planted them.
    "review-slots-each-once": _replace("lexical", SLOTS, "slots.length == arity"),
    "review-form-on-every-role": _replace("wire", "(if acts && role == .plain then [", "(if acts then ["),
    "review-modal-act-by-todays-check": _replace(
        "wire", "else some <$> actCheck name",
        "else some <$> (if acts && role != .plain then canonicalAct else actCheck) name"),
    "review-obligation-act-by-todays-check": _replace(
        "wire", "else some <$> actCheck name",
        "else some <$> (if acts && role == .obligation then canonicalAct else actCheck) name"),
    # The review's sweep: the fixed phrases not passed on, caught only by a proof's `simp`.
    "review-fixed-phrases-not-passed-on": _replace(
        "wire", "decodeRegulatedWith (profiles.contains \"acts@0\") (canonicalActIn profiles fx)",
        "decodeRegulatedWith (profiles.contains \"acts@0\") (canonicalActIn profiles [])"),
    # The other ways to read the slots without their order or without each once.
    "slots-as-a-set": _replace("lexical", SLOTS, "((List.range arity).map toString).all slots.contains"),
    "slots-in-range-each-once": _replace(
        "lexical", SLOTS, "(slots.all ((List.range arity).map toString).contains && slots.eraseDups == slots)"),
    "slots-in-range-as-many": _replace(
        "lexical", SLOTS, "(slots.all ((List.range arity).map toString).contains && slots.length == arity)"),
    **_generated(),
}

# Mutants that change the source and cannot change an answer, each with the reason.
EQUIVALENT = {
    "conjunct-dropped-check-3": "`act` is normalised and begins with `{0} `, so it holds a second word: "
                                "`ws.length ≥ 2` always holds when the conjuncts before it do (as in `canonicalAct`)",
    "conjunct-dropped-decodeRegulatedWith-7": "`acts` dropped from `acts && role == .plain`: without acts@0 a plain "
                                              "declaration with `act` or `form` is refused by the fields check before, "
                                              "so the both-or-neither and form checks find neither",
    "acts-true-decodeRegulatedWith-1": "without acts@0 a plain declaration with `act` is refused by the fields check "
                                       "before, so `acts && keys.contains \"act\"` is `keys.contains \"act\"` there",
}


@pytest.fixture(scope="module")
def lake():
    path = shutil.which("lake")
    if path is None:
        pytest.skip("lake is not available")
    lean_build("VE")
    return path


def _elaborate(lake: str, tmp_path, source: str) -> subprocess.CompletedProcess:
    file = tmp_path / "LexicalMutant.lean"
    file.write_text(source)
    return subprocess.run([lake, "env", "lean", str(file)], cwd=LEAN, capture_output=True, text=True,
                          timeout=HANG_TIMEOUT)


def _unmutated() -> str:
    return _assemble(_sources(), EXAMPLES.read_text())


def _mutant(name: str) -> str:
    """The one file a mutant's test elaborates: its mutated sources and the fixtures."""
    return _assemble(MUTANTS[name](_sources()), EXAMPLES.read_text())


# The source each test that elaborates calls for, by its function: the pool (`elaborated`) builds them the same way.
SOURCES = {"test_the_unmutated_sources_elaborate_cleanly": _unmutated,
           "test_every_seeded_mutant_fails_a_fixture": _mutant,
           "test_an_equivalent_mutant_elaborates_and_passes_every_fixture": _mutant}


@pytest.fixture(scope="module")
def elaborated(lake, request, tmp_path_factory):
    """The selected tests' sources, elaborated at once (`tests/lean_pool.py`); empty under xdist or at width 1."""
    return lean_pool.elaborate_selected(request, SOURCES, partial(_elaborate, lake),
                                        lambda: tmp_path_factory.mktemp("lexical-pool"))


@pytest.fixture
def elaborate(lake, elaborated):
    """A test's elaboration of `source`: the pool's, else its own `_elaborate` call."""
    return lambda tmp_path, source: lean_pool.result(elaborated, source, lambda: _elaborate(lake, tmp_path, source))


def _killed(out: str) -> bool:
    """Every error is a `#guard` that failed, and there is one."""
    return 0 < out.count(GUARD_FAILED) == len(re.findall(r": error(?:\([\w.]+\))?:", out))


def test_the_unmutated_sources_elaborate_cleanly(elaborate, tmp_path):
    done = elaborate(tmp_path, _unmutated())
    out = done.stdout + done.stderr
    assert done.returncode == 0 and "error" not in out, out


def _changed_lines(sources: dict[str, str], mutated: dict[str, str]) -> set[tuple[str, int]]:
    return {(where, i) for where in sources
            for i, (a, b) in enumerate(zip(sources[where].split("\n"), mutated[where].split("\n"))) if a != b}


DECISION = re.compile(r"(?<![\w.])(?:if|unless|acts|fx)(?!\w)|" + "|".join(
    p.pattern for p in (COMPARISON, ROLE, DEFAULT_ARM, ACTS_PROFILE)))


def test_the_sweep_covers_every_decision_of_the_decoder():
    """Every line of the scoped definitions' bodies that decides something (a condition, a comparison, a role, a
    default, a read of `acts`, `fx` or the profiles' `acts@0`) is changed by a generated mutant, and each of the
    review's five changes a line that a generated mutant changes the same way."""
    sources, generated = _sources(), _generated()
    changed = {line for mutate in generated.values() for line in _changed_lines(sources, mutate(sources))}
    decisions = set()
    for where, names in SCOPE.items():
        lines = _masked(sources[where]).split("\n")
        unmasked = sources[where].split("\n")
        for name in names:
            lo, hi = _span(_masked(sources[where]), name)
            first = sources[where].count("\n", 0, lo)
            last = sources[where].count("\n", 0, hi)
            decisions |= {(where, i) for i in range(first + 1, last)
                          if DECISION.search(lines[i]) or DEFAULT_ARM.search(unmasked[i])
                          or ACTS_PROFILE.search(unmasked[i])}
    assert len(decisions) >= 20 and decisions <= changed, sorted(decisions - changed)
    same_way = {"review-form-on-every-role": "conjunct-dropped-decodeRegulatedWith-4",
                "review-modal-act-by-todays-check": "todays-check-permission-decodeRegulatedWith-1",
                "review-obligation-act-by-todays-check": "todays-check-obligation-decodeRegulatedWith-1",
                "review-fixed-phrases-not-passed-on": "fx-dropped-decodeRegulatedIn-1"}
    for review, name in same_way.items():
        assert _changed_lines(sources, MUTANTS[review](sources)) == \
            _changed_lines(sources, generated[name](sources)), review
    assert set(EQUIVALENT) <= set(generated)


@pytest.mark.parametrize("name", sorted(set(MUTANTS) - set(EQUIVALENT)))
def test_every_seeded_mutant_fails_a_fixture(elaborate, tmp_path, name):
    sources = _sources()
    assert MUTANTS[name](sources) != sources, f"{name} changes nothing"
    done = elaborate(tmp_path, _mutant(name))
    out = done.stdout + done.stderr
    assert done.returncode != 0, f"{name} survives every #guard"
    assert _killed(out), f"{name} fails before a #guard, or not only at #guards:\n{out}"


@pytest.mark.parametrize("name", sorted(EQUIVALENT))
def test_an_equivalent_mutant_elaborates_and_passes_every_fixture(elaborate, tmp_path, name):
    """A mutant listed as equivalent changes the source and still passes: if a fixture kills it, the list is wrong."""
    sources = _sources()
    assert MUTANTS[name](sources) != sources
    done = elaborate(tmp_path, _mutant(name))
    assert done.returncode == 0, f"{name} ({EQUIVALENT[name]}) fails:\n{done.stdout + done.stderr}"


def test_the_killed_check_counts_every_error():
    guard = f"F.lean:9:0: error: Expression\n  x == y\n{GUARD_FAILED}\n"
    assert _killed(guard) and not _killed("")
    assert not _killed("F.lean:3:2: error: unknown identifier 'x'\n" + guard)
    assert not _killed("F.lean:3:2: error(lean.redundantMatchAlt): Redundant alternative\n" + guard)
