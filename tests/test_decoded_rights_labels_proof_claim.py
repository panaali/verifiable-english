"""No record claims the decoded route discharges `legacy_labels_nodup_of_identifiers`' hypothesis `hk` (pk-1c-cfr-1).

The theorem assumes every act key passes `VE.Bridge.identifier`; no lemma ties decoded act keys to it (the decoder
checks `Surface.identifier`). The claim may return only with a theorem in lean/VE/NormDefaults/ that concludes from a
successful decode that the act keys (`condKeys`) pass `VE.Bridge.identifier`.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = "lean/VE/NormDefaults/PacksLabels.lean"
REPORT = "docs/premise-packs/pk-1c/REPORT.md"
THEOREM = "legacy_labels_nodup_of_identifiers"
NEGATED = re.compile(r"\b(?:not|never)\s+(?:yet\s+)?discharg\w*", re.IGNORECASE)


def claims_discharge(text: str) -> bool:
    """An affirmative `discharg…` word, negated ones ("does not yet discharge") removed."""
    return "discharg" in NEGATED.sub("", text).lower()


def decode_discharge_theorems(sources: dict[str, str]) -> list[str]:
    """Theorems with a successful-decode hypothesis whose statement names `condKeys` and `Bridge.identifier`."""
    return [
        f"{path}: {m.group(1)}"
        for path, text in sources.items()
        for m in re.finditer(r"^theorem\s+(\S+)(.*?):=", text, re.DOTALL | re.MULTILINE)
        if re.search(r"decod\w*[^=\n]*=\s*(?:\.ok|Except\.ok)\b", m.group(2))
        and "condKeys" in m.group(2)
        and "Bridge.identifier" in m.group(2)
    ]


def claim_problems(labels: str, report: str, sources: dict[str, str]) -> list[str]:
    if decode_discharge_theorems(sources):
        return []
    problems = []
    for block in re.findall(r"/-[-!](.*?)-/", labels, re.DOTALL):
        text = " ".join(block.split())
        if claims_discharge(text) or ("decoded route" in text and "`Surface.identifier`" not in text):
            problems.append(f"PacksLabels.lean claims a decoded-route discharge: {text}")
    doc = re.search(r"/--((?:(?!-/).)*)-/\s*theorem\s+" + THEOREM + r"\b", labels, re.DOTALL)
    doc_text = " ".join(doc.group(1).split()) if doc else ""
    if not all(w in doc_text for w in ("hypothesis `hk`", "`VE.Bridge.identifier`", "`Surface.identifier`")) or (
        not NEGATED.search(doc_text)
    ):
        problems.append(f"the `{THEOREM}` docstring does not state the open hypothesis `hk`: {doc_text!r}")
    rows = [line.strip() for line in report.splitlines() if line.lstrip().startswith(f"- `{THEOREM}`")]
    row = rows[0] if len(rows) == 1 else ""
    if not row or claims_discharge(row) or "VE.Bridge.identifier" not in row or not NEGATED.search(row):
        problems.append(f"pk-1c REPORT row of `{THEOREM}` claims a discharge or omits the open hypothesis: {rows}")
    problems += [
        f"pk-1c REPORT:{n} claims a route discharge: {line.strip()}"
        for n, line in enumerate(report.splitlines(), 1)
        if "route discharge" in line.lower() or (claims_discharge(line) and "decoded route" in line.lower())
    ]
    return problems


def _read() -> tuple[str, str, dict[str, str]]:
    files = (ROOT / "lean/VE/NormDefaults").rglob("*.lean")
    sources = {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in files}
    return sources[LABELS], (ROOT / REPORT).read_text(encoding="utf-8"), sources


def test_decoded_rights_labels_proof_claim() -> None:
    labels, report, sources = _read()
    assert f"theorem {THEOREM}" in labels
    assert claim_problems(labels, report, sources) == []


def test_decoded_rights_labels_proof_claim_refuses() -> None:
    """The base docstring and the base REPORT row are refused; a decode theorem about `hk` lifts the refusal."""
    labels, report, sources = _read()
    old_doc = (
        "/-- On the decoded route the act keys are declared predicate names, which `VE.Bridge.identifier` admits;"
        " that\ndischarges the act-key hypothesis. -/\ntheorem " + THEOREM
    )
    doc_re = r"/--(?:(?!-/).)*-/\s*theorem\s+" + THEOREM + r"\b"
    old_labels = re.sub(doc_re, lambda _: old_doc, labels, flags=re.DOTALL)
    old_row = f"  - `{THEOREM}` :392 (the route discharge)"
    old_report = re.sub(r"^  - `" + THEOREM + r"`.*$", old_row, report, flags=re.M)
    assert old_labels != labels and old_report != report
    assert any("discharge" in p for p in claim_problems(old_labels, report, sources))
    assert any("route discharge" in p for p in claim_problems(labels, old_report, sources))
    theorem = "theorem t (h : decodeRights j = .ok R) :\n  ∀ k ∈ condKeys R, Bridge.identifier k.2.1 := by"
    proved = {**sources, "X.lean": theorem}
    assert claim_problems(old_labels, old_report, proved) == []
    assert decode_discharge_theorems(sources) == []
