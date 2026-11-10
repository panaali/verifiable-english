"""ci-2b: `readInstruction_refused_classed` and `readInstruction_typed` in lean/VE/Commands/RunSplit.lean are the
statements of docs/spec/commands-imperatives.md section 6 word for word (whitespace normalised), the second with
`(hw : VE.Scope.JsonWF j)` beside `hd` (reviews/dri-decisions-20261102-ci-1.md item 1) and nothing else changed."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NAMES = ("readInstruction_refused_classed", "readInstruction_typed")
HD = "(hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)"
HW = "(hw : VE.Scope.JsonWF j)"


def declarations(code: str) -> dict[tuple[str, str], list[str]]:
    """Each theorem up to its proof's `:=` (or the blank line after a spec statement), whitespace normalised."""
    out: dict[tuple[str, str], list[str]] = {}
    for start in re.finditer(r"^theorem (\S+)", code, re.M):
        body = code[start.start():re.compile(r"\s:=(\s|$)|\n\s*\n|$").search(code, start.end()).start()]
        out.setdefault(("theorem", start[1]), []).append(re.sub(r"\s+", " ", body).strip())
    return out


def approved() -> dict[str, str]:
    text = (ROOT / "docs/spec/commands-imperatives.md").read_text()
    section = text.split("## 6. CI-2", 1)[1].split("\n## 7. ", 1)[0]
    found = declarations("\n".join(re.findall(r"```lean\n(.*?)```", section, re.S)))
    spec = {name: found[("theorem", name)][0] for name in NAMES}
    assert HD in spec["readInstruction_typed"] and HW not in spec["readInstruction_typed"]
    spec["readInstruction_typed"] = spec["readInstruction_typed"].replace(HD, f"{HW} {HD}")
    return spec


def problems(lean_text: str) -> list[str]:
    found = declarations(lean_text)
    return [name for name, text in approved().items() if found.get(("theorem", name)) != [text]]


def test_the_two_statements_are_the_specs_with_hw():
    assert problems((ROOT / "lean/VE/Commands/RunSplit.lean").read_text()) == []


def test_a_changed_statement_fails():
    text = (ROOT / "lean/VE/Commands/RunSplit.lean").read_text()
    for old, new, name in (("(hw : VE.Scope.JsonWF j)\n", "", "readInstruction_typed"),
                           ("    (hq : ∀ q ∈ ctx.queries", "    (hq' : ∀ q ∈ ctx.queries", "readInstruction_typed"),
                           ("(h : readInstruction ctx s = .refused code text)",
                            "(h : readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s = .refused code text)",
                            "readInstruction_refused_classed")):
        assert old in text
        assert problems(text.replace(old, new, 1)) == [name], name
