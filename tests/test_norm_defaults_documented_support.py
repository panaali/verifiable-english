"""The norm-defaults spec states, for each composed block, what the profile gate does with `norm-defaults@0`.

The gate is Lean's `todayGate` (lean/VE/Compose/Dispatch.lean), read from its source; the composed blocks are the ones
`pendingWithDefaults` names there. A spec sentence that mentions `norm-defaults@0` and says a combination is admitted,
refused or rejected at profile validation must name each block it speaks of, and say what the gate does with it
(norm-defaults-cfr-2, finding #4 of reviews/l1-c-regrade-norm-defaults-b-20261109.md).
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/norm-defaults.md"
DISPATCH = ROOT / "lean/VE/Compose/Dispatch.lean"
VERDICT = re.compile(r"\b(admitted|accepted|refused|rejected)\b")


def _definition(source: str, name: str) -> str:
    start = source.index(f"def {name} ")
    end = re.search(r"\n(?:/--|def |theorem )", source[start + 1:])
    return source[start:start + 1 + end.start()] if end else source[start:]


def gate_refusals(source: str) -> dict[str, str]:
    """Each profile `todayGate` refuses together with `norm-defaults@0`, with the refusal's text."""
    body = _definition(source, "todayGate")
    assert 'ps.contains "alternatives@0"' in body  # the parse reads the gate itself
    pair = r'ps\.contains "([^"]+)" && ps\.contains "norm-defaults@0"\s*then\s*\.error \(unsupported "([^"]+)"\)'
    return {p: "UnsupportedProfile: " + text for p, text in re.findall(pair, body)}


def composed_blocks(source: str) -> list[str]:
    body = _definition(source, "pendingWithDefaults")
    found = re.search(r"\(\[([^\]]+)\]\.find\? ps\.contains\)", body)
    blocks = re.findall(r'"([^"]+)"', found.group(1)) if found else []
    assert blocks, "pendingWithDefaults names no composed block"
    return blocks


def documented_claims(spec: str, blocks: list[str]) -> list[tuple[str, str | None, str]]:
    """(verdict, block or None, sentence) for each claim about profile validation with `norm-defaults@0`."""
    claims = []
    for sentence in re.split(r"(?<=[.;])\s+(?=[A-Z`])", " ".join(spec.split())):
        verdict = VERDICT.search(sentence)
        if "`norm-defaults@0`" not in sentence or "profile validation" not in sentence or not verdict:
            continue
        kind = "admitted" if verdict.group(1) in ("admitted", "accepted") else "refused"
        named = [b for b in blocks if f"`{b}`" in sentence]
        claims += [(kind, b, sentence) for b in named] or [(kind, None, sentence)]
    return claims


def test_norm_defaults_documented_support():
    source = DISPATCH.read_text(encoding="utf-8")
    refused, blocks = gate_refusals(source), composed_blocks(source)
    claims = documented_claims(SPEC.read_text(encoding="utf-8"), blocks)
    unnamed = [s for kind, block, s in claims if block is None]
    assert not unnamed, f"a profile-validation claim names no composed block: {unnamed}"
    for block in blocks:
        stated = {kind for kind, b, _ in claims if b == block}
        expected = "refused" if block in refused else "admitted"
        assert stated == {expected}, f"spec: {sorted(stated)} for {block} with norm-defaults@0; todayGate: {expected}"
        if block in refused:
            assert any(refused[block] in s for _, b, s in claims if b == block), f"spec omits {refused[block]!r}"
