"""relc-scan-buildnote-fix-1125: the repair builders' build notes are not omission records.

The omission counter's record scan (tests/omission_rule.py is its port) takes every README / docs REPORT.md sentence that
has a drop or merge word and names a unit as an omission record. Three notes the F7 and F9 repair builders wrote about
their own build (records 1, 2 and 4 of the Nov 25 flag analysis, reviews/pathf-q3/relc-r35-flag-analysis-20261125.md in
the manager repo) were counted that way. The fix moves them, unchanged, to BUILD-NOTES.md next to each REPORT.md, a file
the scan does not read; a real omission record in REPORT.md is still found.
"""

import json
import re

import tests.omission_rule as omission_rule

REPO = omission_rule.REPO
FSF = "safety-framework"
F7 = REPO / "docs/usecases/safety-framework/fsf-repair-f7-govadequacy-1119"
F9 = REPO / "docs/usecases/safety-framework/fsf-repair-f9-mcca-1119"

# The three build notes, verbatim (line breaks joined): record 1 (F7), record 2 (F9), record 4 (F9).
NOTE_1 = ("A merge after the R16 diagnostic voids that diagnostic for the answers that read the touched units: f3, f8, "
          "f9-acc, f10-acc, f11-acc, f12-p, f12-u, f13-p and f13-u (`c5check.log`).")
NOTE_2 = ("The R16 C2/C3 pinned lists are per commit: the counted read re-pins at the merge commit the train makes, and a "
          "merge after the R16 diagnostic voids the diagnostic for G6 and K4/CHECKPOINT_MCCA (and for any answer reading "
          "f2, f3 or f5, whose rendered units change).")
NOTE_4 = ("A first carrier mutant (\"... assessments\" without \"on various checkpoints\") survived: it is still a prefix "
          "of f5's rule wording, so the counter's own match still counts it; it is not a carrier break and was replaced "
          "by #4.")
NOTES = (NOTE_1, NOTE_2, NOTE_4)
# Build-note sentences allowed in a BUILD-NOTES.md although they name a unit with a drop word. Add a new one here only
# if it says nothing the translation leaves out (the reviewer checks it); a real omission goes in REPORT.md.
APPROVED_BUILD_NOTES = NOTES
REAL = "f3 drops the passage's second clause (\"when hazardous\"): no rule carries it."

CASE = "demo"
UNITS = ("f3", "f5")
BASE = {
    f"usecases/{CASE}/rules.d1.ve": ('## f3 | always | Src: "a widget must be inspected when hazardous"\n'
                                     "Rule 1. Every situation must have a widget inspected.\n"
                                     '## f5 | always | Src: "the blue widget is shiny"\n'
                                     "Rule 1. Every situation must have a blue widget polished.\n"),
    f"usecases/{CASE}/demo_vocabulary.py": ('VOCABULARY = {\n    "inspect": act(["situation"], "{0} have a widget inspected"),\n'
                                            '    "polish": act(["situation"], "{0} have a blue widget polished"),\n}\n'),
    f"usecases/{CASE}/environment.d1.json": json.dumps({"vocabulary": {"predicates": {}}}),
    f"usecases/{CASE}/PLAN.md": "# Plan\n\n## 12. Deviations\n\nNothing changed.\n\n## 13. Files\n\nNone.\n",
    f"usecases/{CASE}/README.md": "# Demo\n\nThe demo case.\n",
    f"usecases/{CASE}/spans.json": json.dumps({"units": []}),
    f"usecases/{CASE}/accounting.d1.txt": "f3 | omits:\nf5 | omits:\n",
}


def _build(root, report, notes=None):
    files = dict(BASE)
    files[f"docs/usecases/{CASE}/repair-1/REPORT.md"] = report
    if notes is not None:
        files[f"docs/usecases/{CASE}/repair-1/BUILD-NOTES.md"] = notes
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def _report_records(exp):
    return sorted({e[3] for es in exp.values() for e in es if e[2] == "report"})


def test_build_notes_beside_the_report_are_not_records_and_a_real_record_still_is(tmp_path):
    root = _build(tmp_path, f"# repair-1 REPORT\n\n{REAL}\n\nNotes on the build itself are in BUILD-NOTES.md.\n",
                  "# repair-1: build notes\n\n" + "\n\n".join(NOTES) + "\n")
    exp = omission_rule.exposures(CASE, UNITS, root)
    assert {u: [(e[2], e[3]) for e in es] for u, es in exp.items() if es} == {"f3": [("report", REAL)]}


def test_the_same_notes_inside_a_report_are_records(tmp_path):
    """Control: the scan does take the three notes as records when they sit in REPORT.md (as on the counted text), so the
    test above passes because of where the notes are, not because the scan cannot see them."""
    root = _build(tmp_path, f"# repair-1 REPORT\n\n{REAL}\n\n" + "\n\n".join(NOTES) + "\n")
    recs = _report_records(omission_rule.exposures(CASE, UNITS, root))
    for note in NOTES:
        assert any(r.startswith(note[:60]) for r in recs), note[:60]
    assert REAL in recs


def _fsf_units():
    rules = (REPO / "usecases" / FSF / "rules.d1.ve").read_text(encoding="utf-8")
    return set(omission_rule.rule_blocks(rules)) | {"FACTS", "CASES", "D2D3"}


def test_the_frozen_text_scan_takes_none_of_the_three_build_notes():
    """On this repository's safety-framework files, no record the scan builds is one of the three notes."""
    exp = omission_rule.exposures(FSF, _fsf_units(), REPO)
    assert exp is not None
    recs = [e[3] for es in exp.values() for e in es if e[2] in ("report", "plan12", "gaps")]
    for note in NOTES:
        assert not [r for r in recs if r.startswith(note[:60])], note[:60]


def _would_be_records(text, names):
    """The sentences of text the scan would take as records if text sat in a REPORT.md: a drop word and a unit name."""
    out = []
    for sent in omission_rule.SENTENCE_SPLIT.split(text):
        if omission_rule.OMIT_DROP_RE.search(sent) and \
                {t.rstrip(".:") for t in re.findall(r"[A-Za-z0-9_.:+-]+", sent)} & names:
            out.append(" ".join(sent.split()))
    return out


def _build_notes_offenders(root):
    """[(file, sentence)] for every docs/usecases/**/BUILD-NOTES.md sentence the scan would take as a record if it sat in
    REPORT.md, other than the three approved notes: BUILD-NOTES.md is not scanned, so a real omission must never go there."""
    approved = {" ".join(n.split()) for n in APPROVED_BUILD_NOTES}
    bad = []
    for p in sorted((root / "docs/usecases").rglob("BUILD-NOTES.md")):
        cases = [c for c in p.relative_to(root).parts[2:-1] if (root / "usecases" / c / "rules.d1.ve").is_file()]
        if not cases:
            bad.append((p.relative_to(root).as_posix(), "no use case directory in its path"))
            continue
        names = set()
        for c in cases:
            for f in ("rules.d1.ve", "facts.d1.ve"):
                fp = root / "usecases" / c / f
                names |= set(omission_rule.rule_blocks(fp.read_text(encoding="utf-8"))) if fp.is_file() else set()
        bad += [(p.relative_to(root).as_posix(), s) for s in _would_be_records(p.read_text(encoding="utf-8"), names)
                if s not in approved]
    return bad


def test_build_notes_files_hold_no_unapproved_record_sentence():
    """Guard for the route this fix opens: a BUILD-NOTES.md sentence with a drop word naming a unit fails unless it is one of
    the three approved build notes (a real omission belongs in REPORT.md or the accounting file)."""
    assert _build_notes_offenders(REPO) == []


def test_the_build_notes_guard_catches_a_real_omission_put_there(tmp_path):
    """Opposite direction of the guard: a real omission record in a BUILD-NOTES.md is reported; the approved notes are not."""
    for rel, text in BASE.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    p = tmp_path / f"docs/usecases/{CASE}/repair-1/BUILD-NOTES.md"
    p.parent.mkdir(parents=True)
    p.write_text("# notes\n\n" + "\n\n".join(NOTES) + "\n", encoding="utf-8")
    assert _build_notes_offenders(tmp_path) == []
    p.write_text("# notes\n\n" + "\n\n".join(NOTES) + f"\n\n{REAL}\n", encoding="utf-8")
    assert _build_notes_offenders(tmp_path) == [(f"docs/usecases/{CASE}/repair-1/BUILD-NOTES.md", REAL)]


def test_the_three_notes_are_kept_in_build_notes_files():
    """The notes are moved, not deleted: each is in its item's BUILD-NOTES.md, and neither REPORT.md holds it."""
    def flat(p):
        return " ".join(p.read_text(encoding="utf-8").split())
    assert NOTE_1 in flat(F7 / "BUILD-NOTES.md")
    assert NOTE_2 in flat(F9 / "BUILD-NOTES.md") and NOTE_4 in flat(F9 / "BUILD-NOTES.md")
    for note in NOTES:
        assert note not in flat(F7 / "REPORT.md") and note not in flat(F9 / "REPORT.md")
