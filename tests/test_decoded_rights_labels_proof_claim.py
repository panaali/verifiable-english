"""The records of `legacy_labels_nodup_of_identifiers` claim no decoded-route discharge that is not proved (pk-1c-cfr-1).

The theorem proves rights-label distinctness under the hypothesis `hk` that every act key passes
`VE.Bridge.identifier`. No lemma ties a decoded `RightsDoc`'s act keys to that check (the decoder runs
`Surface.identifier`, lean/VE/Bridge.lean `checkVocabularyNames`), so the docstrings and the pk-1c REPORT row must not
say the decoded route discharges `hk`, unless a theorem in lean/VE/NormDefaults/ concludes it from a successful decode.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = ROOT / "lean/VE/NormDefaults/PacksLabels.lean"
NORM_DEFAULTS = ROOT / "lean/VE/NormDefaults"
REPORT = ROOT / "docs/premise-packs/pk-1c/REPORT.md"
THEOREM = "legacy_labels_nodup_of_identifiers"
# `bridge_identifier_sep` carried the same claim ("discharges the act-key hypothesis ... on the decoded route").
CHECKED_DOCSTRINGS = (THEOREM, "bridge_identifier_sep")

_NEGATED = re.compile(r"\b(?:not|never)\s+(?:yet\s+)?(?:been\s+|be\s+)?discharg\w*", re.IGNORECASE)
_DISCHARGE = re.compile(r"discharg\w*", re.IGNORECASE)


def docstring(source: str, name: str) -> str | None:
    """The `/-- … -/` docstring directly before `theorem <name>`, or None."""
    m = re.search(r"/--((?:(?!-/).)*)-/\s*theorem\s+" + re.escape(name) + r"\b", source, re.DOTALL)
    return " ".join(m.group(1).split()) if m else None


def claims_discharge(text: str) -> bool:
    """True when `text` affirms a discharge: any `discharg…` word left after removing negated ones."""
    return bool(_DISCHARGE.search(_NEGATED.sub("", text)))


def decode_discharge_theorems(sources: dict[str, str]) -> list[str]:
    """Theorems that conclude about act keys (`condKeys`, `Bridge.identifier` or label `Nodup`) from a successful decode."""
    found = []
    for path, text in sources.items():
        for m in re.finditer(r"^theorem\s+(\S+)(.*?):=", text, re.DOTALL | re.MULTILINE):
            name, stmt = m.group(1), m.group(2)
            from_decode = "decod" in name.lower() or re.search(r"decod\w*[^=\n]*=\s*(?:\.ok|Except\.ok)\b", stmt)
            about_act_keys = re.search(r"condKeys|Bridge\.identifier|Nodup", stmt) or re.search(
                r"actKey|identifier|labels", name
            )
            if from_decode and about_act_keys:
                found.append(f"{path}: {name}")
    return found


def claim_problems(labels: str, report: str, sources: dict[str, str]) -> list[str]:
    """Every unproved decoded-route discharge claim, and every missing statement of what the theorem gives."""
    if decode_discharge_theorems(sources):
        return []
    problems = []
    for name in CHECKED_DOCSTRINGS:
        doc = docstring(labels, name)
        if doc is None:
            problems.append(f"no docstring before `theorem {name}` in PacksLabels.lean")
        elif claims_discharge(doc):
            problems.append(f"the `{name}` docstring claims a discharge: {doc}")
    doc = docstring(labels, THEOREM) or ""
    for needed in ("`VE.Bridge.identifier`", "`Surface.identifier`", "hypothesis"):
        if needed not in doc:
            problems.append(f"the `{THEOREM}` docstring does not name {needed}: {doc}")
    if not _NEGATED.search(doc):
        problems.append(f"the `{THEOREM}` docstring does not say the decoded route does not yet discharge `hk`: {doc}")
    rows = [line for line in report.splitlines() if line.lstrip().startswith(f"- `{THEOREM}`")]
    if len(rows) != 1:
        problems.append(f"pk-1c REPORT has {len(rows)} code-map rows for `{THEOREM}`, expected 1")
    for row in rows:
        if claims_discharge(row) or "VE.Bridge.identifier" not in row or not _NEGATED.search(row):
            problems.append(f"pk-1c REPORT row claims a discharge or omits the open hypothesis: {row.strip()}")
    for n, line in enumerate(report.splitlines(), 1):
        low = line.lower()
        if "route discharge" in low or (claims_discharge(line) and "decoded route" in low):
            problems.append(f"pk-1c REPORT:{n} claims a route discharge: {line.strip()}")
    return problems


def _sources() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in sorted(NORM_DEFAULTS.rglob("*.lean"))}


def test_decoded_rights_labels_proof_claim() -> None:
    labels = LABELS.read_text(encoding="utf-8")
    assert f"theorem {THEOREM}" in labels
    assert claim_problems(labels, REPORT.read_text(encoding="utf-8"), _sources()) == []


OLD_DOC = """/-- On the decoded route the act keys are declared predicate names, which `VE.Bridge.identifier` admits; that
discharges the act-key hypothesis. -/
theorem legacy_labels_nodup_of_identifiers (U : UDoc) :"""
OLD_ROW = "  - `legacy_labels_nodup_of_identifiers` :392 (the route discharge)"


def test_decoded_rights_labels_proof_claim_refuses() -> None:
    """The base wording is refused, and a theorem from a successful decode lifts the refusal."""
    labels = LABELS.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    sources = _sources()
    current = re.search(r"/--(?:(?!-/).)*-/\s*theorem\s+" + THEOREM + r"\b[^\n]*", labels, re.DOTALL)
    assert current is not None
    old_labels = labels.replace(current.group(0), OLD_DOC)
    current_row = next(line for line in report.splitlines() if line.lstrip().startswith(f"- `{THEOREM}`"))
    old_report = report.replace(current_row, OLD_ROW)
    assert any("claims a discharge" in p for p in claim_problems(old_labels, report, sources))
    assert any("route discharge" in p for p in claim_problems(labels, old_report, sources))
    proved = dict(sources)
    proved["lean/VE/NormDefaults/X.lean"] = (
        "theorem decodeRights_actKeys_identifier (h : decodeRights j = .ok R) :\n"
        "    ∀ k ∈ VE.Rights.condKeys R, VE.Bridge.identifier k.2.1 = true := by\n  sorry\n"
    )
    assert claim_problems(old_labels, old_report, proved) == []
    assert decode_discharge_theorems(sources) == []
