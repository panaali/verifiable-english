"""The norm-defaults spec's profile-validation claims with `norm-defaults@0` agree with Lean's `todayGate`.

Read from lean/VE/Compose/Dispatch.lean; the blocks are those `pendingWithDefaults` names (norm-defaults-cfr-2)."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/norm-defaults.md"
DISPATCH = ROOT / "lean/VE/Compose/Dispatch.lean"
VERDICT = re.compile(r"\bis (admitted|accepted|refused|rejected)\b")


def _definition(source: str, name: str) -> str:
    start = source.index(f"def {name} ")
    end = re.search(r"\n(?:/--|def |theorem )", source[start + 1:])
    return source[start:start + 1 + end.start()] if end else source[start:]


def gate_refusals(source: str) -> dict[str, str]:
    """Each profile `todayGate` refuses together with `norm-defaults@0`, with the refusal's text."""
    body = _definition(source, "todayGate")
    pair = r'ps\.contains "([^"]+)" && ps\.contains "norm-defaults@0"\s*then\s*\.error \(unsupported "([^"]+)"\)'
    assert body.count('"norm-defaults@0"') == 1 + len(re.findall(pair, body)) and "pendingWith" not in body  # all read
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
    paragraphs = [" ".join(p.split()) for p in re.split(r"\n\s*\n|\n- ", spec)]
    for sentence in (s for p in paragraphs for s in re.split(r"(?<=[.;])\s+(?=[A-Z`*])", p)):
        verdict = VERDICT.search(sentence)
        if "`norm-defaults@0`" not in sentence or "profile validation" not in sentence or not verdict:
            continue
        kind = "admitted" if verdict.group(1) in ("admitted", "accepted") else "refused"
        named = [b for b in blocks if f"`{b}`" in sentence]
        claims += [(kind, b, sentence) for b in named] or [(kind, None, sentence)]
    return claims


def disagreements(spec: str, source: str) -> list[str]:
    """Where the spec's profile-validation claims with `norm-defaults@0` differ from `todayGate` (empty: none)."""
    refused, blocks = gate_refusals(source), composed_blocks(source)
    claims = documented_claims(spec, blocks)
    found = [f"names no composed block: {s}" for _, block, s in claims if block is None]
    for block in blocks:
        stated = {kind for kind, b, _ in claims if b == block}
        expected = "refused" if block in refused else "admitted"
        if stated != {expected}:
            found.append(f"spec: {sorted(stated)} for {block} with norm-defaults@0; todayGate: {expected}")
        elif block in refused and not any(refused[block] in s for _, b, s in claims if b == block):
            found.append(f"spec omits {refused[block]!r}")
    return found


def test_norm_defaults_documented_support():
    assert disagreements(SPEC.read_text(encoding="utf-8"), DISPATCH.read_text(encoding="utf-8")) == []


def test_norm_defaults_documented_support_refuses():
    """The opposite direction: main's old claim, a flipped row and a dropped row each disagree with the gate."""
    spec, source = SPEC.read_text(encoding="utf-8"), DISPATCH.read_text(encoding="utf-8")
    old = ("Their combination with `norm-defaults@0` is rejected at profile validation with `UnsupportedProfile`; "
           "neither route may report a two-valued decision for a silent permission.")
    risk = "- `risk@0` with `norm-defaults@0` is refused at profile validation"
    alternatives = "- `alternatives@0` with `norm-defaults@0` is admitted at profile validation"
    assert risk in spec and alternatives in spec
    assert disagreements(spec + "\n\n" + old + "\n", source)
    assert disagreements(spec.replace(risk, risk.replace("refused", "admitted")), source)
    assert disagreements(spec.replace(alternatives, alternatives.replace("admitted", "refused")), source)
    assert disagreements(spec.replace(risk, "- `risk@0` is described elsewhere"), source)
