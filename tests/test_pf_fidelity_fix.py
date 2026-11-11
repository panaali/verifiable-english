"""openai-preparedness-fidelity-fix: the T fixes of the use-case audit and the K findings of PLAN section 12.

Each test pins one behaviour the fix claims, read from the case's own modules and saved results: the safeguard acts
carry Table 1's standard and F2/F3's sufficiency, CAPREP asks 3.3's compilation sentence, F11's exception precedes
every F2 rule, RS11 = final stays excluded, every header quotes whole source sentences, and answer-key.json equals
PLAN section 6 cell by cell except the six transcription findings PLAN 12 item 15 records.
"""
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PF = REPO / "usecases" / "openai-preparedness"
LEAN_SERVICE = REPO / "lean/.lake/build/bin/ve_service"
NAMES = ("pf_vocabulary", "pf_translation", "build_document", "stage0", "run")


def _load():
    import importlib
    import sys
    saved = {name: sys.modules.pop(name) for name in NAMES if name in sys.modules}
    sys.path.insert(0, str(PF))
    try:
        return {name: importlib.import_module(name) for name in NAMES}
    finally:
        sys.path.remove(str(PF))
        for name in NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


MODULES = _load()
V, T, B, R = (MODULES[n] for n in ("pf_vocabulary", "pf_translation", "build_document", "run"))


@pytest.fixture
def pf(monkeypatch):
    import sys
    for name, module in MODULES.items():
        monkeypatch.setitem(sys.modules, name, module)


def act(predicate):
    return V.environment()["vocabulary"]["predicates"][predicate]["regulated"]["act"]


def blocks_for(predicate):
    """The rule blocks whose norm regulates `predicate`."""
    return [b for b in T.rule_blocks() if json.loads(T.parsed_rule(b.id))["predicate"] == predicate]


# --- PLAN section 6 against answer-key.json, cell by cell ------------------------------------------------------

def section_6(plan_text):
    lines = plan_text.split("\n")
    start = next(i for i, line in enumerate(lines) if line.startswith("## 6. "))
    stop = next(i for i, line in enumerate(lines) if line.startswith("## 7. "))
    return "\n".join(lines[start:stop])


def tables(text):
    """Section 6's tables: subsection number -> (header cells, rows of cells)."""
    out = {}
    for number, body in re.findall(r"### (6\.\d) [^\n]*\n(.*?)(?=\n### |\Z)", text, re.S):
        rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in body.split("\n")
                if line.startswith("|") and not line.startswith("|---")]
        out[number] = (rows[0], rows[1:])
    return out


def verdict(cell):
    """The first ALL, NONE or SOME(...) of a cell, in answer-key.json's ASCII notation."""
    match = re.search(r"ALL|NONE|SOME\(", cell)
    if match.group() != "SOME(":
        return match.group()
    depth, i = 0, match.start() + 4
    while True:
        depth += {"(": 1, ")": -1}.get(cell[i], 0)
        if depth == 0:
            break
        i += 1
    return cell[match.start():i + 1].replace("∧", "&").replace("∨", "|")


def soft(cell):
    found = re.search(r"soft(?: under (RS\d+) = (\w+))?", cell)
    if not found:
        return None
    return f"{found[1]}={found[2]}" if found[1] else "RS1=default"


def family_a(header, rows):
    activities = re.search(r"\((.*)\)", header[1]).group(1).split(", ")
    atoms = [h.split()[0] for h in header[1:6]]
    by_level = {row[0]: row for row in rows}

    def expand(level, column):
        cell = by_level[level][column]
        if cell.startswith("as "):
            return expand(cell[3:], column)
        if cell.endswith(" ×4"):
            return dict.fromkeys(activities, cell[:-3])
        out = {}
        for clause in cell.split("; "):
            names, value = ((activities, clause[5:]) if clause.startswith("else ")
                            else (clause.split(": ", 1)[0].split(", "), clause.split(": ", 1)[1]))
            for name in names:
                out.setdefault(name, value)
        assert set(out) == set(activities), (level, column, cell)
        return out

    return {f"A-{level}-{activity}/{atom}": value for level in by_level for column, atom in enumerate(atoms, 1)
            for activity, value in expand(level, column).items()}


def section_6_cells(plan_text):
    """id -> (key, soft) as section 6 states them."""
    found = tables(section_6(plan_text))
    cells = family_a(*found["6.1"])
    header, rows = found["6.2"]
    cells.update({f"B-{row[0]}/{h.split()[0]}": row[i] for row in rows for i, h in enumerate(header) if i})
    key_column = {"6.3": 3, "6.4": 3, "6.5": 2, "6.6": 2, "6.7": 2, "6.8": 2, "6.9": 2}
    for number, column in key_column.items():
        cells.update({row[0]: row[column] for row in found[number][1]})
    return {id_: (verdict(cell), soft(cell)) for id_, cell in cells.items()}


# PLAN 12 item 15: the six B-*/MREP cells truncated in the transcription ("SOME(N" and a stray "soft"). Fixed list.
TRANSCRIPTION_FINDINGS = tuple(f"B-{level}/MREP" for level in ("BIO-H", "BIO-C", "CYB-H", "CYB-C", "AIS-H", "AIS-C"))


def mismatches(key_items, plan_text):
    plan = section_6_cells(plan_text)
    assert set(plan) == {k["id"] for k in key_items}
    return sorted(k["id"] for k in key_items if plan[k["id"]] != (k["key"], k.get("soft")))


def test_answer_key_equals_section_6_cell_by_cell():
    """Every answer-key.json cell is its section 6 cell, except exactly the six recorded transcription findings."""
    key = json.loads((PF / "answer-key.json").read_text())["items"]
    assert len(TRANSCRIPTION_FINDINGS) == 6
    assert mismatches(key, (PF / "PLAN.md").read_text(encoding="utf-8")) == sorted(TRANSCRIPTION_FINDINGS)


@pytest.mark.parametrize("id_, field, value", [("A-BIO-C-INT/SUF", "key", "SOME(nest)"), ("K13", "soft", None),
                                               ("G9", "key", "SOME(P | scoped)"), ("C6", "key", "NONE")])
def test_the_cell_comparison_catches_one_changed_cell(id_, field, value):
    """A scratch copy with one other cell changed (even to a K entry's answer) is caught."""
    key = json.loads((PF / "answer-key.json").read_text())["items"]
    for item in key:
        if item["id"] == id_:
            item[field] = value
            if value is None:
                item.pop(field)
    found = mismatches(key, (PF / "PLAN.md").read_text(encoding="utf-8"))
    assert found == sorted(TRANSCRIPTION_FINDINGS + (id_,))


# --- The corrected acts and the questions that ask them ---------------------------------------------------------

STANDARD = {"misuse_safeguards": "(Appendix C.1)", "alignment_safeguards": "(Appendix C.2)",
            "security_controls": "(Appendix C.3)"}


def test_table_1_acts_name_the_high_standard(pf):
    """f1 (class 1): the MIS, ALN and SEC acts are safeguards "meeting the High standard" of their appendix."""
    assert set(R.ATOMS["MIS"]) | set(R.ATOMS["ALN"]) <= set(STANDARD) and "security_controls" in R.ATOMS["SEC"]
    for predicate, appendix in STANDARD.items():
        assert "meeting the High standard" in act(predicate), predicate
        users = blocks_for(predicate)
        assert users and all(b.id.startswith("f1-") and "meeting High standard" in b.source and appendix in b.source
                             for b in users), predicate


def test_f2_f3_acts_carry_the_sufficiency(pf):
    """f2, f3 (class 1): SUF asks safeguards that sufficiently minimize the risk, and sufficient controls."""
    assert set(R.ATOMS["SUF"]) == {"safeguards_before_deployment", "safeguards_during_development"}
    assert "sufficiently minimizing severe-harm risk" in act("safeguards_before_deployment")
    assert "sufficient safety as well as security controls" in act("safeguards_during_development")
    for name in ("f2-deploy", "f2-deploy-any", "f2-reminder", "f2-reminder-any"):
        block = next(b for b in T.rule_blocks() if b.id == name)
        assert "sufficiently minimize the associated risk of severe harm" in block.source, name
        assert json.loads(T.parsed_rule(name))["predicate"] == "safeguards_before_deployment"


def test_capabilities_report_items_ask_the_compilation_sentence(pf):
    """B-*/CAPREP and K4 ask 3.3's "compiled into a Capabilities Report that is submitted to the SAG", not the
    SAG's review of it."""
    asked = set(R.ATOMS["CAPREP"]) | set(R.K_ITEMS["CAPABILITIES_REPORT"])
    users = [b for p in asked for b in blocks_for(p)]
    assert [b.id for b in users] == ["f7-compile"]
    assert "are compiled into a Capabilities Report that is submitted to the SAG." in users[0].source
    assert "f7-compile" in T.RS0_STATEMENTS


def test_g9_asks_every_safeguard_rule_the_nuclear_one_included(pf):
    assert "nuclear_safeguards" in R.SAFEGUARD_PREDICATES
    assert {json.loads(T.parsed_rule(n))["predicate"] for n in ("f12-nuclear", "f12-nuclear-unscoped")} == {
        "nuclear_safeguards"}


# --- F11's exception and RS11 ----------------------------------------------------------------------------------

def test_f11_exception_precedes_every_f2_deployment_rule(pf):
    """C1 (class 3): under RS5 = exception an F11 rule precedes each rule of F2's two deployment parts."""
    f2 = [n for part in R.COMMITMENTS["F2"][:2] for n in part]
    overridden = {low: high for high, lows in T.PRECEDENCE.items() for low in lows}
    assert set(f2) <= set(overridden)
    for name in f2:
        exception = next(b for b in T.rule_blocks() if b.id == overridden[name])
        assert exception.id.startswith("f11-exception") and exception.when == (("RS5", "exception"),)
        assert json.loads(T.parsed_rule(exception.id))["predicate"] == json.loads(T.parsed_rule(name))["predicate"]
    assert set(R.CLUSTERS["C1"]) >= set(f2) | {"f11-exception", "f11-exception-deploy"}


@pytest.mark.skipif(not LEAN_SERVICE.exists(), reason="the Lean service is not built")
def test_c1_is_conflict_free_on_every_choice(pf):
    R.MUTANT = R.WITHOUT_NARROWING = None
    result = R.conflict("C1")
    assert "undecided" not in result and result["cone"] == ["RS3", "RS5"]
    assert [row["holds"] for row in result["choices"]] == [False] * 4


def test_rs11_final_is_excluded_and_no_rule_of_it_returns(pf):
    """f16-final, f16-process (classes 5, 9): RS11 = final is not offered, and no rule is selected by RS11."""
    assert T.READING_SETS["RS11"] == ("process",) and T.EXCLUDED_READINGS == {"RS11": ("final",)}
    assert B.READINGS["rs11-final"] == ("RS11", {"process": []})
    blocks = T.rule_blocks() + T.read_blocks("facts.d1.ve")
    assert not [b.id for b in blocks if any(s == "RS11" for s, _ in b.when)]
    assert not {"f16-final", "f16-process"} & {b.id for b in blocks}
    assert "decision_reversal" in {json.loads(T.parsed_rule(b.id))["predicate"] for b in blocks
                                   if b.id.startswith("f16-board")}
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "**Excluded reading: RS11 = final.**" in plan
    assert "Where necessary, the Board may reverse a decision and/or mandate a revised course of action." in plan


def test_k_entries_are_the_saved_answers():
    """C6 and C-doc are NONE and G9 is SOME(P ∨ scoped) (PLAN 12 items 19, 20); section 6 keeps its cells."""
    saved = json.loads((PF / "results.json").read_text())
    rows = {r["id"]: r for r in saved["comparison"]}
    assert rows["C6"]["ve"] == rows["C-doc"]["ve"] == "NONE"
    g9 = saved["items"]["G9"]["choices"]
    assert g9 and all(row["holds"] == (row["choice"]["RS4"] == "P" or row["choice"]["RS4s"] == "scoped")
                      for row in g9)
    for id_ in ("C6", "C-doc", "G9"):
        assert rows[id_]["cause"]["kind"] == "key finding"
    plan = (PF / "PLAN.md").read_text(encoding="utf-8")
    assert "19. **Key finding (K): C6 and C-doc are NONE" in plan and "20. **Key finding (K): G9 is SOME(P ∨ scoped)" in plan


# --- Class 11: whole source sentences ---------------------------------------------------------------------------

def _plain(text):
    """Source and header text compared without layout: page numbers inside a sentence, line-break hyphens,
    whitespace and quote styles do not count."""
    text = re.sub(r" \d{1,2} (?=[a-z])", " ", text.replace("\n", " "))
    return re.sub(r"[\s\-‐]+", "", text.replace("’", "'").replace("“", '"').replace("”", '"'))


def quote_faults(blocks, source_text):
    """(block id, quote) for every header with no quote, a cut quote ("…") or a quote the source does not contain."""
    source, faults = _plain(source_text), []
    for block in blocks:
        quotes = re.findall(r"“((?:[^“”]|“[^“”]*”)*)”", block.source)
        faults += [(block.id, None)] if not quotes else [
            (block.id, q) for q in quotes if "…" in q or _plain(q) not in source]
    return faults


@pytest.mark.skipif(not B.DEFAULT_SOURCE.exists(), reason="the pinned source text is not present")
def test_every_header_quotes_whole_source_text(pf):
    assert quote_faults(T.rule_blocks() + T.read_blocks("facts.d1.ve"), B.DEFAULT_SOURCE.read_text()) == []


def test_a_cut_altered_or_missing_quote_is_a_fault():
    source = "We will review and potentially update the Pre- paredness Framework for continued sufficiency.\n"
    good = T.Block("good", (), "A: “We will review and potentially update the Preparedness Framework for "
                                        "continued sufficiency.”", "")
    cut = T.Block("cut", (), "A: “We will review … continued sufficiency.”", "")
    altered = T.Block("altered", (), "A: “We will review the Preparedness Framework.”", "")
    none = T.Block("none", (), "A: a paraphrase", "")
    assert quote_faults([good, cut, altered, none], source) == [
        ("cut", "We will review … continued sufficiency."), ("altered", "We will review the Preparedness Framework."),
        ("none", None)]
