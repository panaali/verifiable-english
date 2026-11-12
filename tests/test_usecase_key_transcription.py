"""Every frozen-key use case: answer-key.json is a cell-for-cell transcription of PLAN.md section 6.

A use case with a KEY-FREEZE.md has its answer key frozen as PLAN.md section 6 (the section-6 SHA-256 test in
tests/test_safetyfw_usecases.py pins that text). answer-key.json is a copy of it made for the run scripts. This
test re-parses section 6 itself, cell by cell, and asserts that (a) every answer-key.json item is a section-6
cell, with the same key and the same soft marker, string-equal after whitespace normalisation, and (b) no
answer-key.json item, field or note exists that section 6 lacks. The connectives are compared in the notation
the transcription's own `source` field declares ("| for or and & for and"), so `∧` and `&` are the same cell.
A cell with several verdicts (anthropic-rsp G7) is read as {label phrase: verdict} and compared label by label, never
by member order: each transcribed label names exactly one section-6 phrase by its content words.

The parser reads only section 6 (and the notation paragraph at its head); it never reads answer-key.json to
decide what a cell says.
"""
import json
import re
from pathlib import Path

import pytest

from tests.test_safetyfw_usecases import section

REPO = Path(__file__).resolve().parents[1]
USECASES = REPO / "usecases"
FROZEN_KEY_CASES = sorted(p.parent.name for p in USECASES.glob("*/KEY-FREEZE.md"))

# Fields an answer-key.json item may carry. id, case, item and plan locate the cell; key, soft and note are the
# cell; dates, quantities and years are the section 5 situation the run script feeds VE (section 5, not 6).
LOCATORS = {"id", "case", "item", "plan"}
CELL_FIELDS = {"key", "soft", "note"}
SITUATION_FIELDS = {"dates", "quantities", "years"}
VERDICT = re.compile(r"\b(?:ALL|NONE)\b|\bSOME\(")
SOFT = re.compile(r",\s*soft\b(.*)$")
ACTIVITIES = ("DEV", "INT", "LINT", "EXT")


def norm(text):
    """Whitespace removed; the section-6 connectives written in the transcription's declared notation."""
    return re.sub(r"\s+", "", text.replace("∧", "&").replace("∨", "|"))


def rows(table):
    """The body rows of a markdown table as lists of stripped cells; the header row first."""
    lines = [line for line in table.split("\n") if line.startswith("|")]
    split = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    return [split[0]] + [r for r in split[2:]]


def subsections(case):
    """Section 6 as {"6.n": (body text, [header, *rows])}."""
    out = {}
    for number, body in re.findall(r"### (6\.\d) [^\n]*\n(.*?)(?=\n### |\Z)", section(case, 6), re.S):
        out[number] = (body, rows(body))
    return out


def bare_soft(case):
    """What a bare "soft" means, from the notation paragraph of section 6 (the reading it names first)."""
    head = section(case, 6).split("### ")[0]
    found = re.search(r"holds only as a default rule under (\w+) = (\w+)", head)
    return f"{found.group(1)}={found.group(2)}" if found else None


def verdict(text):
    """The verdict tokens of one key cell, in order, each with its balanced parentheses."""
    out = []
    for m in VERDICT.finditer(text):
        if m.group(0) != "SOME(":
            out.append(m.group(0))
            continue
        depth, i = 0, m.start() + 4
        while True:
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
            if depth == 0:
                break
        out.append(text[m.start():i])
    return out


def cell(case, text):
    """One section-6 value as {"key": ..., "soft": ...}: the key with its soft marker parsed off."""
    found = SOFT.search(text)
    soft = None
    if found:
        qualifier = found.group(1).strip()
        soft = (bare_soft(case) if not qualifier else
                qualifier[len("under "):] if qualifier.startswith("under ") else qualifier)
        text = text[:found.start()]
    keys = verdict(text)
    if not keys:  # a harm word (anthropic-rsp S1): the cell's first word is the key
        keys = [text.split()[0].lower()]
    return {"key": keys[0] if len(keys) == 1 else labelled(text, keys), "soft": soft}


def labelled(text, keys):
    """A cell with several verdicts ("prompt Board notice required: NONE; covered by the quarterly update: ALL")
    as {label phrase: verdict}: one verdict per ";" clause, each named by the words before its ":"."""
    out = {}
    for clause in (c.strip() for c in text.split(";")):
        found = verdict(clause)
        assert len(found) == 1, (text, clause)
        phrase = clause[:clause.index(found[0])].rstrip().removesuffix(":").strip()
        assert phrase and phrase not in out, (text, clause)
        out[phrase] = found[0]
    assert list(out.values()) == keys, text  # no verdict lost, doubled or reordered by the split
    return out


# Function words a section-6 label phrase may carry that a transcribed label (REQUIRED:PROMPT_BOARD_NOTICE) drops.
FUNCTION_WORDS = {"a", "an", "the", "by", "of", "on", "to", "in"}


def label_words(label):
    """The content words of a label, lower case: a transcribed label splits at ":" and "_", a phrase at spaces."""
    return {w for w in re.split(r"[\s:_]+", label.lower()) if w} - FUNCTION_WORDS


def key_mismatch(transcribed, wanted):
    """None when the transcribed key is the section-6 key, else why not. A labelled key is compared label by label
    (each transcribed label names exactly one section-6 phrase by its content words, and every phrase is named once),
    so member order is irrelevant and a verdict moved to another label is caught."""
    if not isinstance(wanted, dict):
        return None if isinstance(transcribed, str) and norm(transcribed) == norm(wanted) else "key"
    if not isinstance(transcribed, dict):
        return "key: section 6 labels its verdicts"
    named = {}
    for label in transcribed:
        phrases = [p for p in wanted if label_words(p) == label_words(label)]
        if len(phrases) != 1:
            return f"key: label {label!r} names {len(phrases)} section-6 phrases"
        named[label] = phrases[0]
    if sorted(named.values()) != sorted(wanted):
        return "key: labels do not name every section-6 phrase once"
    wrong = [label for label, phrase in named.items()
             if not isinstance(transcribed[label], str) or norm(transcribed[label]) != norm(wanted[phrase])]
    return f"key: wrong verdict under {wrong}" if wrong else None


def per_activity(text, column, table):
    """A family-A cell of openai-preparedness: activity -> value ("NONE ×4", "EXT: ALL, soft; else NONE",
    "INT, LINT: SOME(any)", "as BIO-H")."""
    if text.startswith("as "):
        return per_activity(table[text[3:]][column], column, table)
    if text.endswith("×4"):
        return dict.fromkeys(ACTIVITIES, text[:-2].strip())
    out, rest = {}, None
    for clause in (c.strip() for c in text.split(";")):
        if clause.startswith("else "):
            rest = clause[5:]
            continue
        acts, value = clause.split(":", 1)
        out |= dict.fromkeys((a.strip() for a in acts.split(",")), value.strip())
    out |= {a: rest for a in ACTIVITIES if a not in out}
    assert set(out) == set(ACTIVITIES) and None not in out.values(), text
    return out


def family_a(case, number, body, table):
    header, *body_rows = table
    found = {}
    if case == "openai-preparedness":
        by_level = {r[0]: r for r in body_rows}
        for row in body_rows:
            for column, head in enumerate(header[1:-1], start=1):
                item = head.split()[0]
                for activity, value in per_activity(row[column], column, by_level).items():
                    found[f"A-{row[0]}-{activity}/{item}"] = (cell(case, value), row)
        return found
    # anthropic-rsp: PROTk/ARGk are the row's own threshold, PROTj/ARGj ("each j") the other rows.
    for row in body_rows:
        levels = range(1, 5) if row[0].startswith("A-Tk") else [int(row[0][3:])]
        for k in levels:
            for column, head in enumerate(header[1:-1], start=1):
                name, own = head.split()[0][:-1], head.split()[0].endswith("k")
                for j in range(1, 5):
                    if (j == k) == own and row[column] != "—":
                        value = re.sub(r",\s*each j(\s*≠\s*k)?$", "", row[column])
                        found[f"A-T{k}/{name}{j}"] = (cell(case, value), row)
    return found


def family_b(case, number, body, table):
    header, *body_rows = table
    found = {}
    for row in body_rows:
        prefix = "" if row[0].startswith("B-") else "B-"
        for column, head in enumerate(header):
            item = head.split()[0]
            if item.isupper() and item not in {"CASE", "LEVEL"}:
                found[f"{prefix}{row[0]}/{item}"] = (cell(case, row[column]), row)
    return found


def case_ids(text):
    """"S1-T1 … S1-T3" names three cases; anything else names one."""
    found = re.fullmatch(r"(\w+-T)(\d) … \1(\d)", text)
    if found:
        return [f"{found.group(1)}{n}" for n in range(int(found.group(2)), int(found.group(3)) + 1)]
    return [text]


def family_keyed(case, number, body, table):
    header, *body_rows = table
    column = header.index("Key")
    return {ident: (cell(case, row[column]), row) for row in body_rows for ident in case_ids(row[0])}


def section_6_cells(case):
    """id -> (subsection, {"key", "soft"}, the section-6 row it came from), read from section 6 alone."""
    out = {}
    for number, (body, table) in subsections(case).items():
        parse = {"6.1": family_a, "6.2": family_b}.get(number, family_keyed)
        for ident, (value, row) in parse(case, number, body, table).items():
            assert ident not in out, (case, ident)
            out[ident] = (number, value, row)
    return out


def transcription(case):
    return json.loads((USECASES / case / "answer-key.json").read_text(encoding="utf-8"))["items"]


def mismatches(case, rows_=None):
    """Every transcription cell that differs from section 6, and every item or field section 6 lacks; `rows_` is a
    scratch copy of answer-key.json's items (default: the file)."""
    cells = section_6_cells(case)
    rows_ = transcription(case) if rows_ is None else rows_
    bad = []
    for entry in rows_:
        extra = set(entry) - LOCATORS - CELL_FIELDS - SITUATION_FIELDS
        if extra:
            bad.append((entry["id"], "fields section 6 lacks", sorted(extra)))
        if entry["id"] not in cells:
            bad.append((entry["id"], "no section-6 cell", entry.get("key")))
            continue
        number, value, row = cells[entry["id"]]
        if entry["plan"] != number:
            bad.append((entry["id"], "plan", entry["plan"], number))
        why = key_mismatch(entry.get("key"), value["key"])
        if why:
            bad.append((entry["id"], why, entry.get("key"), value["key"]))
        soft = entry.get("soft")
        if (soft is None) != (value["soft"] is None) or (soft is not None and norm(soft) != norm(value["soft"])):
            bad.append((entry["id"], "soft", soft, value["soft"]))
        if "note" in entry and norm(entry["note"]) not in norm(" ".join(row)):
            bad.append((entry["id"], "note not in its section-6 row", entry["note"]))
    missing = sorted(set(cells) - {e["id"] for e in rows_})
    bad += [(ident, "section-6 cell not transcribed") for ident in missing]
    return bad


def test_every_frozen_key_use_case_is_checked():
    """The glob finds the frozen keys this test was written for; a new one is checked the same way."""
    assert {"anthropic-rsp", "openai-preparedness"} <= set(FROZEN_KEY_CASES)


@pytest.mark.parametrize("case", FROZEN_KEY_CASES)
def test_section_6_parses_into_every_item(case):
    """The parser reads one cell per item of section 5's total: none is lost or doubled."""
    total = int(re.search(r"\| Items \| (\d+) ", (USECASES / case / "KEY-FREEZE.md").read_text()).group(1))
    assert len(section_6_cells(case)) == total


@pytest.mark.parametrize("case", FROZEN_KEY_CASES)
def test_answer_key_transcribes_section_6(case):
    """Every answer-key.json cell equals its section-6 cell, and none exists that section 6 lacks."""
    assert mismatches(case) == []


def _changed(case, change):
    rows_ = transcription(case)
    change(rows_)
    return {m[0] for m in mismatches(case, rows_)}


def _set(ident, field, value):
    def change(rows_):
        item = next(r for r in rows_ if r["id"] == ident)
        if value is None:
            item.pop(field)
        else:
            item[field] = value
    return change


# One scratch change per kind of transcription error, in each frozen-key use case: a key retyped, cut or given in
# the wrong notation, a soft marker added, dropped or moved to another reading, a note section 6 lacks, an item
# moved to another subsection, added, dropped or given an extra field.
SCRATCH = [
    ("openai-preparedness", "B-BIO-H/MREP", _set("B-BIO-H/MREP", "key", "SOME(N")),
    ("openai-preparedness", "B-AIS-C/MREP", _set("B-AIS-C/MREP", "soft", "RS1=default")),
    ("openai-preparedness", "B-BIO-C/CONTRIB", _set("B-BIO-C/CONTRIB", "soft", None)),
    ("openai-preparedness", "K13", _set("K13", "soft", "RS1=default")),
    ("openai-preparedness", "A-BIO-C-INT/SUF", _set("A-BIO-C-INT/SUF", "key", "SOME(inuse | nest & any)")),
    ("openai-preparedness", "C6", _set("C6", "key", "SOME(final | bperm)")),
    ("openai-preparedness", "G5", _set("G5", "note", "only K18 under P")),
    ("openai-preparedness", "D2", _set("D2", "plan", "6.8")),
    ("openai-preparedness", "N3", _set("N3", "verdict", "NONE")),
    ("openai-preparedness", "K21", lambda rows_: rows_.append({**rows_[-1], "id": "K21"})),
    ("openai-preparedness", "S8", lambda rows_: rows_.remove(next(r for r in rows_ if r["id"] == "S8"))),
    ("anthropic-rsp", "A-T2/PROT2", _set("A-T2/PROT2", "key", "SOME(uncond)")),
    ("anthropic-rsp", "A-T3/ARG3", _set("A-T3/ARG3", "soft", None)),
    ("anthropic-rsp", "A-T0/PROT1", _set("A-T0/PROT1", "soft", "only under the default force")),
    ("anthropic-rsp", "T4b", _set("T4b", "key", "SOME(iffo | iffi)")),
    ("anthropic-rsp", "G7", _set("G7", "key", {"REQUIRED:PROMPT_BOARD_NOTICE": "ALL",
                                                "COVERED:QUARTERLY_UPDATE": "ALL"})),
    # A labelled key (G7) checked label by label: verdicts swapped between labels (review F1), a label section 6
    # lacks, a label dropped, the labels flattened to one verdict.
    ("anthropic-rsp", "G7", _set("G7", "key", {"COVERED:QUARTERLY_UPDATE": "NONE",
                                                "REQUIRED:PROMPT_BOARD_NOTICE": "ALL"})),
    ("anthropic-rsp", "G7", _set("G7", "key", {"REQUIRED:PROMPT_BOARD_NOTICE": "NONE",
                                                "COVERED:ANNUAL_UPDATE": "ALL"})),
    ("anthropic-rsp", "G7", _set("G7", "key", {"COVERED:QUARTERLY_UPDATE": "ALL"})),
    ("anthropic-rsp", "G7", _set("G7", "key", "ALL")),
    ("anthropic-rsp", "S1-T4", _set("S1-T4", "key", "catastrophic")),
    ("anthropic-rsp", "D3a", _set("D3a", "note", "42 days > 31")),
    ("anthropic-rsp", "B-VOL/ASSESS", lambda rows_: rows_.remove(next(r for r in rows_ if r["id"] == "B-VOL/ASSESS"))),
]


def _reversed_labels(rows_):
    for item in rows_:
        if isinstance(item["key"], dict):
            item["key"] = dict(reversed(item["key"].items()))


@pytest.mark.parametrize("case", FROZEN_KEY_CASES)
def test_labelled_keys_compare_by_label_not_member_order(case):
    """Review F1: reordering the members of every labelled key keeps the transcription exact; the label, not the
    JSON order, says which verdict is which (the swapped verdicts are SCRATCH rows above)."""
    assert _changed(case, _reversed_labels) == set()


def test_section_6_labels_g7_verdicts():
    """The parser reads G7's two verdicts with their section-6 labels, and each transcribed label names one."""
    _, value, _ = section_6_cells("anthropic-rsp")["G7"]
    assert value["key"] == {"prompt Board notice required": "NONE", "covered by the quarterly update": "ALL"}
    assert label_words("REQUIRED:PROMPT_BOARD_NOTICE") == label_words("prompt Board notice required")
    assert label_words("COVERED:QUARTERLY_UPDATE") == label_words("covered by the quarterly update")
    assert label_words("REQUIRED:BOARD") != label_words("prompt Board notice required")


def _scratch_ids():
    """One id per SCRATCH row: case:item, with #n on the second and later rows for the same item."""
    seen, out = {}, []
    for case, ident, _ in SCRATCH:
        n = seen[case, ident] = seen.get((case, ident), -1) + 1
        out.append(f"{case}:{ident}" + (f"#{n}" if n else ""))
    return out


@pytest.mark.parametrize("case, ident, change", SCRATCH, ids=_scratch_ids())
def test_one_changed_cell_is_caught(case, ident, change):
    """A scratch copy of answer-key.json with one cell changed is caught at that cell and nowhere else."""
    assert _changed(case, change) == {ident}
