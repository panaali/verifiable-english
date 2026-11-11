"""The statement gate for spec 5.4 (SC-2): each proved theorem is the reviewed text, whitespace aside (sc-2c, sc-2d).

The five effect statements take `(hw : JsonWF o)` after `hN` (before `h₁` in `commute_applies`), as the DRI signed
(reviews/dri-decisions-20261031-sc-2c.md item 1). Their binders are pinned twice (sc-2d-f1): in spec 5.4's text, every
bracketed binder of any kind (`(..)`, `{..}`, `⦃..⦄`, `[..]`) in order; and in the statement Lean elaborated, read
from the generated `lean/statements.txt`, whose telescope must match the spec's binder for binder (a named binder
keeps its name, a hypothesis is an anonymous premise, and the premise at `hw` is `JsonWF o`). So an extra binder of
any kind, or a lost one, fails even when the spec and the Lean source are changed together.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.check_readings_defaults_statements import proof_cut

ROOT = Path(__file__).resolve().parents[1]
EFFECTS = {
    "reguard_applies": "D u c o o' N N' G' h hN hw hN' hG S ρ",
    "restrict_applies": "D u C o o' C' N N' hC hC' h hN hw hN' S ρ",
    "carveOut_applies": "D u c o o' N N' C h hN hw hN' hC S ρ",
    "applyEffect_typed": "D u e o o' N N' E Γ hN hw h hN' hT hc",
    "commute_applies": "D u e₁ e₂ hc o o₁ o₂ N₁ N₂ hw h₁ h₂ hN₁ hN₂ S ρ",
}
PROVED = ("own_congr", "order_refused", "listName_run", *EFFECTS)


def statement(text: str, name: str) -> str | None:
    """The statement of `name`: from `theorem name ` to the `:=` that starts the proof (`proof_cut`: a `:=` inside the
    statement, `{ L with scope := s }`, is kept) or the next blank line, whitespace normalised."""
    start = text.find(f"theorem {name} ")
    if start < 0:
        return None
    rest = text[start:]
    rest = rest[:rest.find("\n\n")] if "\n\n" in rest else rest
    return " ".join(rest[:proof_cut(rest)].split())


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
    lines = (text if text is not None else (ROOT / "lean/statements.txt").read_text()).splitlines()
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


def spec_5_4() -> str:
    spec = (ROOT / "docs/spec/scope.md").read_text()
    start = spec.index("### 5.4 SC-2")
    return spec[start:spec.index("### 5.5", start)]


def lean() -> str:
    return (ROOT / "lean/VE/Scope/Theorems.lean").read_text()


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
