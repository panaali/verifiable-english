"""No record claims the decoded route discharges the hypothesis `hk` of `legacy_labels_nodup_of_identifiers`,
unless a lean/VE/NormDefaults/ theorem concludes from a successful decode that act keys pass `VE.Bridge.identifier`."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELS = "lean/VE/NormDefaults/PacksLabels.lean"
EXAMPLES = "lean/VE/NormDefaults/PacksLegacyExamples.lean"
REPORT = "docs/premise-packs/pk-1c/REPORT.md"
THEOREM = "legacy_labels_nodup_of_identifiers"
NEGATED = re.compile(r"\b(?:not|never)\s+(?:yet\s+)?discharg\w*", re.IGNORECASE)
# The base wording of the same claim in PacksLegacyExamples.lean (DRI 2026-11-10, pk-1c-cfr-1 item 1).
OVERCLAIM = re.compile(
    r"decoded route ensures|route identifiers?\b|route's check on predicate|no decoded document reaches"
    r"|applies `VE\.Bridge\.identifier`"
)


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


def asserts_decoded(text: str) -> bool:
    """A clause about the decoded route, act keys or documents that does not say the link is unproved."""
    return any(
        re.search(r"decoded (?:route|act key|document)", clause)
        and not re.search(r"\b(?:no lemma|not proved|not yet|does not)\b", clause, re.IGNORECASE)
        for clause in re.split(r"[.;:]\s+", text)
    )


def comments(source: str) -> list[str]:
    """The `/-- -/` and `/-! -/` blocks and the runs of `--` lines, each on one line."""
    blocks = re.findall(r"/-[-!](.*?)-/", source, re.DOTALL)
    for run in re.findall(r"(?:^--.*\n?)+", source, re.MULTILINE):
        blocks.append(re.sub(r"^--", "", run, flags=re.MULTILINE))
    return [" ".join(b.split()) for b in blocks]


def claim_problems(labels: str, report: str, sources: dict[str, str]) -> list[str]:
    if decode_discharge_theorems(sources):
        return []
    problems = []
    for path, source in ((LABELS, labels), (EXAMPLES, sources[EXAMPLES])):
        for text in comments(source):
            if claims_discharge(text) or OVERCLAIM.search(text) or asserts_decoded(text) or (
                "decoded route" in text and "`Surface.identifier`" not in text
            ):
                problems.append(f"{path} claims a decoded-route discharge: {text}")
    doc = re.search(r"/--((?:(?!-/).)*)-/\s*theorem\s+" + THEOREM + r"\b", labels, re.DOTALL)
    doc_text = " ".join(doc.group(1).split()) if doc else ""
    needed = ("hypothesis `hk`", "`VE.Bridge.identifier`", "`Surface.identifier`")
    if not all(w in doc_text for w in needed) or not NEGATED.search(doc_text):
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
    old_comment = "-- The route's own repeated-label check refuses it (no decoded document reaches this: predicates are"
    old_examples = {**sources, EXAMPLES: sources[EXAMPLES] + "\n" + old_comment + " identifiers).\n"}
    assert any(EXAMPLES in p for p in claim_problems(labels, report, old_examples))
    assert asserts_decoded("It does not keep `:` out. On the decoded route the act keys pass `VE.Bridge.identifier`.")
    assert not asserts_decoded("That a decoded act key passes it is not proved: no lemma ties decoded act keys to it.")
    theorem = "theorem t (h : decodeRights j = .ok R) :\n  ∀ k ∈ condKeys R, Bridge.identifier k.2.1 := by"
    proved = {**sources, "X.lean": theorem}
    assert claim_problems(old_labels, old_report, proved) == []
    assert decode_discharge_theorems(sources) == []
