"""srccov-eligibility-1119: the source units the coverage map found unshown are now carried or recorded.

Carries: each kept unit's source line, read from usecases/eligibility/source/*.txt, must occur after the
counter's quote normalisation (`omit_norm`) in the legend the reader is shown (environment.json) of a
predicate a rule uses. Records: the out-of-scope comment block in translation.py (the document's record
file) must list exactly the recorded units, each under its kind and at the source line where that unit
starts. Rows, drops and reasons: docs/infra/srccov-eligibility-1119/REPORT.md.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import re
import tokenize

import pytest

from omission_rule import omit_norm

HERE = Path(__file__).resolve().parents[1] / "usecases" / "eligibility"
FILES = {"S1": "uksi-2025-969-made.txt", "S2": "wfp-print.txt", "Sch4": "ukpga-1995-26-sch4.txt"}

# unit -> (map row, source file, source line, predicate whose legend carries it)
CARRIES = {
    "S0005": ("srccov-eligibility-1-1119", "S1", 16, "reached_pa"),
    "S0015": ("srccov-eligibility-1-1119", "S1", 34, "reached_pa"),
    "S0033": ("srccov-eligibility-2-1119", "S1", 60, "entitled"),
}

# unit -> (kind, source file, line where the unit starts, the unit's opening words there)
RECORDS = {
    "S0001": ("metadata", "S1", 11, "The Secretary of State makes these Regulations"),
    "S0092": ("metadata", "S1", 133, "A full impact assessment has not been produced"),
    "S0374": ("metadata", "S2", 6, "This guide is also available in Welsh"),
    "S0114": ("title", "Sch4", 3, "SCHEDULE 4"),
    "S0223": ("title", "Sch4", 252, "48B Category B retirement pension for widows"),
    "S0243": ("title", "Sch4", 272, "48C Category B retirement pension: general."),
    "S0268": ("title", "Sch4", 312, "Graduated retirement benefit"),
    "S0293": ("title", "Sch4", 357, "“ Women, married women and widows"),
    "S0401": ("title", "S2", 35, "3. How much you'll get"),
    "S0432": ("title", "S2", 73, "4. Check if you need to claim"),
    "S0441": ("title", "S2", 104, "5. When you’ll get paid"),
    "S0446": ("title", "S2", 110, "6. Report a change"),
    "S0480": ("title", "S2", 163, "8. Opt out of the Winter Fuel Payment"),
    "S0073": ("navigation or page furniture", "S1", 114, "Regulation 3 sets out the amount"),
    "S0164": ("navigation or page furniture", "Sch4", 123, "Period within which birthday falls | Day pensionable age attained"),
    "S0177": ("navigation or page furniture", "Sch4", 152, "Period within which birthday falls | Age pensionable age attained"),
    "S0195": ("navigation or page furniture", "Sch4", 191, "Period within which birthday falls | Day pensionable age attained"),
    "S0386": ("navigation or page furniture", "S2", 16, "Report anything you think is suspicious."),
    "S0451": ("navigation or page furniture", "S2", 121, "You can either call the helpline or send a letter by post."),
    "S0487": ("navigation or page furniture", "S2", 175, "You can either call the helpline or send a letter by post."),
    "S0093": ("bare citation or pointer", "S1", 135, "See section 138(4) for the definition of “prescribed”."),
    "S0096": ("bare citation or pointer", "S1", 137, "See section 191 for the definition of “prescribed”."),
    "S0098": ("bare citation or pointer", "S1", 137, "See section 7A(6)(d) for the definition of “relevant benefit”."),
    "S0455": ("bare citation or pointer", "S2", 137, "Find out how to repay the money you owe"),
    "S0459": ("bare citation or pointer", "S2", 141, "You can check if your income is over the threshold."),
    "S0479": ("bare citation or pointer", "S2", 162, "Find out how to settle debts and taxes"),
    "S0067": ("change log", "S1", 100, "6. In regulation 4(6A)(a)(ii) of the Social Security (Claims and Payments)"),
    "S0068": ("change log", "S1", 102, "7. The following Regulations are revoked—"),
    "S0069": ("change log", "S1", 103, "(a)the Social Fund Winter Fuel Payment Regulations 2024(18);"),
    "S0070": ("change log", "S1", 104, "(b)the Social Fund Winter Fuel Payment (Amendment) Regulations 2024(19)."),
    "S0090": ("change log", "S1", 131, "Regulation 6 makes a consequential amendment"),
    "S0091": ("change log", "S1", 132, "Regulation 7 revokes the Social Fund Winter Fuel Payment Regulations 2024"),
    "S0094": ("history", "S1", 135, "Section 175(1) and (4) is amended by paragraph 29(2) and (4)"),
    "S0095": ("history", "S1", 135, "Act 1999 (c. 2)."),
    "S0097": ("history", "S1", 137, "Section 7A was inserted by section 71"),
    "S0099": ("history", "S1", 137, "Section 189(1) is amended by paragraph 109(a)"),
    "S0100": ("history", "S1", 137, "Act 1999 (c. 2) and Schedule 6 to the Tax Credits Act 2002 (c. 21)."),
    "S0101": ("history", "S1", 137, "Section 189(4), (5) and (6) is amended by paragraph 109(c)"),
    "S0102": ("history", "S1", 137, "Section 189(4) and (6) is amended by S.I. 2013/252."),
    "S0103": ("history", "S1", 139, "Section 79(1) is amended by paragraph 13(2)"),
    "S0104": ("history", "S1", 141, "Section 3 is amended by paragraph 3 of Schedule 3"),
    "S0105": ("history", "S1", 142, "(5) 2016 anaw 2. Paragraph 1 of Schedule 1 is amended"),
    "S0106": ("history", "S1", 147, "The definition of “health service hospital” is amended"),
    "S0107": ("history", "S1", 151, "Paragraph 1 of Schedule 4 is amended by paragraph 39"),
    "S0108": ("history", "S1", 161, "Section 3(1) is amended by paragraph 3(1) of Schedule 6"),
    "S0109": ("history", "S1", 163, "Section 115(1) is amended by section 4(2)"),
    "S0110": ("history", "S1", 164, "(16) Section 10 is amended by paragraph 23 of Schedule 7"),
    "S0111": ("history", "S1", 165, "Act 1999 and paragraph 4 of Schedule 12 to the Welfare Reform Act 2012"),
    "S0112": ("history", "S1", 166, "(17) S.I. 1987/1968, amended by S.I. 2003/1632, 2007/2911, 2024/869."),
    "S0113": ("history", "S1", 168, "(18) S.I. 2024/869, amended by S.I. 2024/898."),
    "S0071": ("editorial annotation", "S1", 112, "These Regulations make provision for winter fuel payments."),
    "S0449": ("rationale", "S2", 114, "These can affect how much Winter Fuel Payment you get."),
}

BLOCK = "Out of scope (srccov-eligibility-1119)"
GROUP = re.compile(r"^- (?P<kind>[a-z ]+), out of scope:")
UNIT = re.compile(r"\b(S\d{4}) (S1|S2|Sch4):(\d+)\b")


def source_line(file, line, count=1):
    """Source lines `line` .. `line + count - 1` of a source file, the line breaks as single spaces."""
    lines = (HERE / "source" / FILES[file]).read_text(encoding="utf-8").split("\n")
    return " ".join(lines[line - 1:line - 1 + count])


def shown_legends():
    env = json.loads((HERE / "environment.json").read_text(encoding="utf-8"))
    return {name: entry["description"] for name, entry in env["vocabulary"]["predicates"].items()}


def comments(text):
    """The comment text of a Python source, one entry per comment, the '#' and one space removed."""
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    return [tok.string[1:].strip() for tok in tokens if tok.type == tokenize.COMMENT]


def records(text):
    """unit -> (kind, file, line) from the out-of-scope comment block; a unit listed twice is refused."""
    lines = comments(text)
    starts = [i for i, line in enumerate(lines) if line.startswith(BLOCK)]
    assert len(starts) == 1, starts
    found, kind = {}, None
    for line in lines[starts[0] + 1:]:
        if not line:
            break
        group = GROUP.match(line)
        if group:
            kind = group["kind"]
        elif line.startswith("- "):
            raise AssertionError(f"group line without a kind: {line!r}")
        for unit, file, number in UNIT.findall(line):
            assert kind is not None, line
            assert unit not in found, f"{unit} recorded twice"
            found[unit] = (kind, file, int(number))
    return found


def translation_text():
    return (HERE / "translation.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("unit", sorted(CARRIES))
def test_each_carried_unit_is_on_the_shown_legend_word_for_word(unit):
    _, file, line, predicate = CARRIES[unit]
    sentence = source_line(file, line)
    assert sentence.strip(), (unit, file, line)
    assert omit_norm(sentence) in omit_norm(shown_legends()[predicate]), (unit, predicate)


@pytest.mark.parametrize("unit", sorted(CARRIES))
def test_each_carrying_legend_belongs_to_a_predicate_a_rule_uses(unit):
    """METHOD amendment 4: a legend carries only on a symbol some rule line uses."""
    rules = json.loads((HERE / "rules.json").read_text(encoding="utf-8"))["rules"]
    formulas = json.dumps([r["formula"] for r in rules if r["id"] != "B1"])
    assert f'"{CARRIES[unit][3]}"' in formulas, unit


def test_the_carry_check_refuses_a_legend_without_the_sentence():
    """Opposite direction: the legend with the carried sentence cut out no longer holds it."""
    legend = shown_legends()["entitled"]
    sentence = source_line("S1", 60)
    assert omit_norm(sentence) in omit_norm(legend)
    assert omit_norm(sentence) not in omit_norm(legend.replace(sentence, ""))


def test_the_record_block_lists_exactly_the_recorded_units_with_their_kind_and_line():
    expected = {unit: (kind, file, line) for unit, (kind, file, line, _) in RECORDS.items()}
    assert records(translation_text()) == expected


@pytest.mark.parametrize("unit", sorted(RECORDS))
def test_each_record_points_at_the_line_where_its_unit_starts(unit):
    _, file, line, opening = RECORDS[unit]
    assert omit_norm(opening) in omit_norm(source_line(file, line, 2)), (unit, file, line)


def test_no_unit_is_both_carried_and_recorded():
    assert not set(CARRIES) & set(RECORDS)


@pytest.mark.parametrize("edit", ["drop S0449", "duplicate S0071", "shift a line", "change a kind"])
def test_the_record_check_refuses_an_edited_block(edit):
    """Opposite direction: a record dropped, listed twice, at another line or under another kind fails."""
    text = translation_text()
    expected = {unit: (kind, file, line) for unit, (kind, file, line, _) in RECORDS.items()}
    if edit == "drop S0449":
        text = text.replace("S0449 S2:114", "")
    elif edit == "duplicate S0071":
        text = text.replace("S0071 S1:112", "S0071 S1:112, S0071 S1:112")
    elif edit == "shift a line":
        text = text.replace("S0001 S1:11,", "S0001 S1:12,")
    else:
        text = text.replace("# - rationale, out of scope:", "# - title, out of scope:")
    assert text != translation_text()
    try:
        got = records(text)
    except AssertionError:
        return
    assert got != expected
