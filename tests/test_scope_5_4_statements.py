"""The statement gate for spec 5.4 (SC-2): each proved theorem is the reviewed text, whitespace aside (sc-2c, sc-2d).

The five effect statements take `(hw : JsonWF o)` after `hN` (before `h₁` in `commute_applies`), as the DRI signed
(reviews/dri-decisions-20261031-sc-2c.md item 1). Their binders are pinned twice (sc-2d-f1): in spec 5.4's text, every
bracketed binder of any kind (`(..)`, `{..}`, `⦃..⦄`, `[..]`) in order; and in the statement Lean elaborated, read
from the generated `lean/statements.txt`, whose telescope must match the spec's binder for binder (a named binder
keeps its name, a hypothesis is an anonymous premise, and the premise at `hw` is `JsonWF o`). So an extra binder of
any kind, or a lost one, fails even when the spec and the Lean source are changed together.

Every declaration of spec 5.4's Lean block is compared with the Lean source, not only the theorems (review sc-2d-f1
F1): the list is read from the spec block by the shared `declarations` parser of the RD statement gate, so a
definition (`Typed`) is compared with its body, and a declaration added to the spec is compared without editing this
file. A declaration runs to the next Lean command, as Lean reads it (review sc-2d-f1 F2): a blank line or a comment
inside a body or a statement does not end it, so a suffix after one is compared, and a commented-out declaration is
missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import lean_statements as L
from tools.check_readings_defaults_statements import declarations, normal, proof_cut, signature, span

ROOT = Path(__file__).resolve().parents[1]
EFFECTS = {
    "reguard_applies": "D u c o o' N N' G' h hN hw hN' hG S ρ",
    "restrict_applies": "D u C o o' C' N N' hC hC' h hN hw hN' S ρ",
    "carveOut_applies": "D u c o o' N N' C h hN hw hN' hC S ρ",
    "applyEffect_typed": "D u e o o' N N' E Γ hN hw h hN' hT hc",
    "commute_applies": "D u e₁ e₂ hc o o₁ o₂ N₁ N₂ hw h₁ h₂ hN₁ hN₂ S ρ",
}
# Spec 5.4's block by kind; a change in the count is a change to review.
EXPECTED = {"theorem": 8, "def": 1}


def spec_5_4() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.4 SC-2")
    return spec[start:spec.index("### 5.5", start)]


def lean() -> str:
    return (ROOT / "lean/VE/Scope/Theorems.lean").read_text()


def approved(section: str | None = None) -> dict[tuple[str, str], list[str]]:
    """Every declaration of spec 5.4's Lean block, `(kind, name)` → its normalised texts: a theorem to its proof's
    `:=`, a definition with its body."""
    code = (section if section is not None else spec_5_4()).split("```lean", 1)[1].split("```", 1)[0]
    return declarations(code, statements_only=True)


def declaration_faults(section: str, source: str) -> list[str]:
    """Why the Lean source `source` differs from spec 5.4's block `section`, declaration by declaration; empty when
    each is stated once in the spec and once, with the same text, in the source."""
    built = declarations(source, statements_only=True)
    faults = []
    for (kind, name), texts in approved(section).items():
        if len(texts) != 1:
            faults.append(f"{kind} {name} is stated {len(texts)} times in spec 5.4")
        if built.get((kind, name), []) != texts[:1]:
            faults.append(f"{kind} {name}: Lean {built.get((kind, name), [])} is not spec 5.4's {texts[:1]}")
    return faults


DECLARED = sorted(approved())
PROVED = tuple(name for kind, name in DECLARED if kind == "theorem")


def statement(text: str, name: str) -> str | None:
    """The statement of theorem `name` in `text` (Lean source, or spec 5.4's section: its Lean block), read by the
    shared scanner: from `theorem name` to the `:=` that starts the proof (`proof_cut`: a `:=` inside the statement,
    `{ L with scope := s }`, is kept), comments left out, whitespace normalised. A blank line or a comment inside the
    statement does not end it (review sc-2d-f1 F2)."""
    code = text.split("```lean", 1)[1].split("```", 1)[0] if "```lean" in text else text
    texts = declarations(code, statements_only=True).get(("theorem", name))
    return texts[0] if texts else None


CLOSE = {"(": ")", "{": "}", "⦃": "⦄", "[": "]", "⟨": "⟩"}
STOP = ("∀", "∃", "fun ", "λ", "↔")  # at depth 0, an arrow after one of these is inside its body, not a premise


def group_end(text: str, i: int) -> int:
    """The index after the bracket that closes the one at `text[i]`."""
    stack = []
    for j in range(i, len(text)):
        if text[j] in CLOSE:
            stack.append(CLOSE[text[j]])
        elif stack and text[j] == stack[-1]:
            stack.pop()
            if not stack:
                return j + 1
    raise ValueError(f"unclosed {text[i]!r}")


def groups(text: str) -> tuple[list[tuple[str, str | None, str]], str]:
    """The bracketed binder groups at the start of `text`, one `(bracket, name, type)` per name (`name` is None for an
    anonymous instance binder `[T]`), and the text after them."""
    out = []
    while text[:1] in ("(", "{", "⦃", "["):
        end = group_end(text, 0)
        names, colon, typ = text[1:end - 1].partition(" : ")
        if colon and all(n.replace("'", "").replace("_", "").isalnum() for n in names.split()):
            out += [(text[0], n, typ) for n in names.split()]
        else:
            out.append((text[0], None, text[1:end - 1]))
        text = text[end:].lstrip()
    return out, text


def spec_binders(stmt: str) -> list[tuple[str, str | None, str]]:
    """Every bracketed binder of a statement `theorem name <binders> : <type>`, in order, of any bracket kind."""
    found, rest = groups(stmt.split(" ", 2)[2])
    assert rest.startswith(": "), rest[:40]
    return found


def typed(name: str, text: str | None = None) -> str:
    """The statement Lean elaborated for `VE.Scope.<name>`, from `lean/statements.txt`, whitespace normalised."""
    lines = (text if text is not None else L.inventory_path(L.STATEMENTS).read_text()).splitlines()
    start = lines.index(f"theorem VE.Scope.{name}") + 1
    body = []
    for line in lines[start:]:
        if not line.startswith("  ") or line.startswith("  --"):
            break
        body.append(line)
    return " ".join(" ".join(body).split())


def top_arrow(text: str) -> int | None:
    """The index of the first `→` at depth 0 that ends a premise, or None when the rest is the conclusion."""
    depth = 0
    for i, ch in enumerate(text):
        if ch in CLOSE:
            depth += 1
        elif ch in CLOSE.values():
            depth -= 1
        elif depth == 0 and ch == "→":
            return i
        elif depth == 0 and text.startswith(STOP, i) and (i == 0 or text[i - 1] == " "):
            return None
    return None


def telescope(stmt: str) -> list[tuple[str, str | None, str]]:
    """The elaborated statement's binders in order: `∀` groups as `(bracket, name, type)`, each premise `A →` as
    `("→", None, A)`, up to the conclusion. A `∀` binder without brackets is refused (ValueError), never skipped."""
    items, text = [], stmt
    while True:
        text = text.strip()
        if text.startswith("∀ "):
            found, text = groups(text[2:])
            if not found or not text.startswith(","):
                raise ValueError(f"unbracketed binder: {text[:40]!r}")
            items += found
            text = text[1:]
            continue
        cut = top_arrow(text)
        if cut is None:
            return items
        items.append(("→", None, text[:cut].strip()))
        text = text[cut + 1:]


def binder_faults(name: str, spec: str, elaborated: str) -> list[str]:
    """Why the binders of effect statement `name` differ from the pin, in spec 5.4's text or in the elaborated
    statement; empty when both are exactly the pinned explicit binders."""
    faults = []
    want, given = EFFECTS[name].split(), spec_binders(spec)
    if [(b, n) for b, n, _ in given] != [("(", n) for n in want]:
        faults.append(f"spec binders {[(b, n) for b, n, _ in given]} are not the pinned {want}")
    got = telescope(elaborated)
    if len(got) != len(want):
        faults.append(f"elaborated telescope has {len(got)} binders, the pin {len(want)}")
    for n, (b, m, typ) in zip(want, got):
        expected = ("→", None) if n.startswith("h") else ("(", n)
        if (b, m) != expected:
            faults.append(f"elaborated binder {(b, m, typ)} where the pin has {n}")
        elif n == "hw" and typ != "VE.Scope.JsonWF o":
            faults.append(f"the premise at hw is {typ!r}")
    return faults


@pytest.mark.parametrize("name", PROVED)
def test_the_proved_statements_are_spec_5_4s_text(name):
    assert statement(spec_5_4(), name) is not None, name
    assert statement(lean(), name) == statement(spec_5_4(), name), name


@pytest.mark.parametrize("name", EFFECTS)
def test_an_effect_statement_takes_exactly_the_signed_premises(name):
    for text in (lean(), spec_5_4()):
        assert statement(text, name).count("(hw : JsonWF o)") == 1, name
    assert binder_faults(name, statement(spec_5_4(), name), typed(name)) == [], name


PLANTS = (("{hx : True} ", "∀ {hx : True}, "), ("[inst : Inhabited Nat] ", "∀ [inst : Inhabited Nat], "),
          ("[Inhabited Nat] ", "∀ [inst : Inhabited Nat], "), ("⦃hx : True⦄ ", "∀ ⦃hx : True⦄, "),
          ("(hx : True) ", "True → "))


@pytest.mark.parametrize("name", EFFECTS)
@pytest.mark.parametrize("plant", PLANTS, ids=lambda p: p[0].strip())
def test_a_binder_added_to_both_texts_fails(name, plant):
    """sc-2d-f1: a binder of any kind added before `hw` in spec 5.4's text and, as Lean prints it, in the elaborated
    statement fails the pin, though the Lean source would still equal the spec."""
    source, printed = plant
    spec = statement(spec_5_4(), name).replace("(hw : JsonWF o)", source + "(hw : JsonWF o)", 1)
    elaborated = typed(name).replace("VE.Scope.JsonWF o →", printed + "VE.Scope.JsonWF o →", 1)
    assert elaborated != typed(name) and spec != statement(spec_5_4(), name), name
    faults = binder_faults(name, spec, elaborated)
    assert any(f.startswith("spec binders") for f in faults), faults
    assert any(f.startswith("elaborated") for f in faults), faults


@pytest.mark.parametrize("name", [n for n in PROVED if " with " in (statement(lean(), n) or "")])
def test_the_statement_runs_past_a_record_update(name):
    """Review sc-6 F1: a `:=` inside `{ N with f := v }` is part of the statement, so the text after it is compared,
    and a change there is a different statement."""
    text, proved = lean(), statement(lean(), name)
    assert ":=" in proved and proved.rsplit(":=", 1)[1].strip(), name
    inner = text.index(":=", text.index(f"theorem {name} "))
    changed = text[:inner] + ":= changed" + text[inner + 2:]
    assert statement(changed, name) != statement(spec_5_4(), name), name


def test_the_check_tells_a_changed_statement():
    """The comparison is not vacuous: a dropped or added premise, or a weakened conclusion, is a different statement."""
    for name, old, new in (("own_congr", "(hs : ownSafe depthLimit c = true) ", ""),
                           ("order_refused", '"ScopeOrder"', '"Scope"'),
                           *((n, "(hw : JsonWF o) ", "") for n in EFFECTS),
                           *((n, "(hw : JsonWF o) ", "(hw : JsonWF o) (hx : True) ") for n in EFFECTS)):
        proved = statement(lean(), name)
        assert old in proved, name
        changed = proved.replace(old, new, 1)
        assert changed != statement(spec_5_4(), name), name
        if name in EFFECTS:
            assert binder_faults(name, changed, typed(name)), name
    for name in EFFECTS:  # the elaborated premise at `hw` is read, not only counted
        assert binder_faults(name, statement(spec_5_4(), name), typed(name).replace("JsonWF o →", "JsonWF o' →", 1))


def test_spec_5_4_declares_the_reviewed_declarations():
    """The block is read, not empty: its kinds are the reviewed counts, and it states every pinned effect theorem."""
    kinds = {kind: sum(k == kind for k, _ in DECLARED) for kind in EXPECTED}
    assert kinds == EXPECTED and len(DECLARED) == sum(EXPECTED.values()), DECLARED
    assert set(EFFECTS) <= set(PROVED) and ("def", "Typed") in DECLARED, DECLARED


@pytest.mark.parametrize("key", DECLARED, ids=" ".join)
def test_every_declaration_of_spec_5_4_is_the_lean_text(key):
    """Review sc-2d-f1 F1: each declaration of spec 5.4's block, a definition with its body, is the Lean source's."""
    faults = declaration_faults(spec_5_4(), lean())
    assert [f for f in faults if f.startswith(" ".join(key) + ":") or f.startswith(" ".join(key) + " is")] == [], faults


def mutant(source: str, kind: str, name: str) -> str:
    """`source` with declaration `kind name` made vacuous: a definition's body becomes `True`, a theorem's conclusion
    becomes `True` (its binders kept)."""
    start, stop = span(source, kind, name)
    head = source[start:start + proof_cut(source[start:stop])]
    if kind == "theorem":
        binders, _ = signature(normal(head))
        return source[:start] + f"theorem {name} {binders} : True " + source[start + len(head):]
    return source[:start] + head + ":= True" + source[stop:]


@pytest.mark.parametrize("key", DECLARED, ids=" ".join)
def test_a_vacuous_declaration_fails(key):
    """Review sc-2d-f1 F1, the probe for every declaration: `def Typed ... : Prop := True` (and each theorem with the
    conclusion `True`) differs from spec 5.4, and only that declaration is reported."""
    kind, name = key
    changed = mutant(lean(), kind, name)
    assert changed != lean() and declaration_faults(spec_5_4(), lean()) == [], key
    faults = declaration_faults(spec_5_4(), changed)
    assert len(faults) == 1 and faults[0].startswith(f"{kind} {name}: Lean"), faults
    assert "True" in faults[0], faults


# Text Lean reads as whitespace inside a declaration (review sc-2d-f1 F2): none of it ends the declaration, so a
# suffix after it is compared.
GAPS = {"blank line": "\n\n", "blank line of spaces": "\n   \n", "line comment at column 0": "\n-- note\n",
        "block comment": "\n/- note -/\n", "nested block comment": "\n/- a /- b -/ c -/\n\n"}


@pytest.mark.parametrize("gap", GAPS)
@pytest.mark.parametrize("key", DECLARED, ids=" ".join)
def test_a_suffix_after_a_gap_is_compared(key, gap):
    """Review sc-2d-f1 F2: `∧ False` after a blank line or a comment, at the end of a definition's body or of a
    theorem's statement, is part of the declaration Lean reads, and is reported as that declaration's difference."""
    kind, name = key
    source = lean()
    start, stop = span(source, kind, name)
    end = start + proof_cut(source[start:stop]) if kind == "theorem" else stop
    changed = source[:end].rstrip() + GAPS[gap] + "  ∧ False " + source[end:]
    faults = declaration_faults(spec_5_4(), changed)
    assert len(faults) == 1 and faults[0].startswith(f"{kind} {name}: Lean"), faults
    assert "∧ False" in faults[0], faults
    if kind == "theorem":
        assert statement(changed, name) != statement(spec_5_4(), name), name


@pytest.mark.parametrize("key", DECLARED, ids=" ".join)
def test_a_commented_out_declaration_is_missing(key):
    """A declaration inside a block comment is not one Lean reads: commented out, it is reported missing."""
    kind, name = key
    source = lean()
    start, stop = span(source, kind, name)
    faults = declaration_faults(spec_5_4(), source[:start] + "/-\n" + source[start:stop] + "\n-/" + source[stop:])
    assert faults == [f"{kind} {name}: Lean [] is not spec 5.4's {approved()[key]}"], faults
