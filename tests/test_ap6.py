"""AP-6: the report's statement claims are bound to the plan's statement and the built one. No build, no model call.

Review F1 (ap-6-text-1): the report said the built `reify_faithful` was section 3's text unchanged, while its right-hand
side is `VE.Acts.Nary.NaryIntended` (event-based) where the plan has `VE.Core.NaryIntended` (tuple-based). The class:
any record (report or saved patch) that claims the built statement is the plan's, while the two differ.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "docs/act-phrases/ap-6"
PLAN = ROOT / "docs/spec/act-phrases-PLAN.md"
NAMESPACE = "VE.Acts.Nary."
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_.']*")
# Phrases that assert the built statement is the plan's text. Forbidden while the two differ.
IDENTITY_CLAIMS = re.compile(r"text unchanged|statement unchanged|verbatim\)|as written\.|matches plan:\d|"
                             r"statement as written", re.IGNORECASE)


def statement(lines, start):
    """The theorem header from `start` up to `:=` or the end of the second line, comments dropped, one line."""
    out = []
    for line in lines[start:start + 2]:
        line = re.sub(r"^\+", "", line).split("--")[0]
        out.append(line.split(":=")[0].strip())
        if ":=" in line:
            break
    return " ".join(out)


def find(lines, pattern):
    hits = [i for i, line in enumerate(lines) if re.search(pattern, line)]
    assert len(hits) == 1, (pattern, hits)
    return hits[0]


def qualify(text):
    """Every identifier in full: the plan and the patch both write `VE.Acts.Nary`'s own names unqualified."""
    local = {"reify", "ActsDoc", "OneEventPerTuple", "NaryIntended", "reify_faithful"}
    return IDENT.sub(lambda m: NAMESPACE + m.group(0) if m.group(0) in local else m.group(0), text)


def names(text):
    return {m.group(0) for m in IDENT.finditer(text) if "." in m.group(0) or m.group(0)[0].isupper()}


def plan_statement():
    lines = PLAN.read_text().splitlines()
    return qualify(statement(lines, find(lines, r"^theorem VE\.Acts\.Nary\.reify_faithful")))


def built_statement():
    lines = (HERE / "route-a.patch").read_text().splitlines()
    return qualify(statement(lines, find(lines, r"^\+theorem reify_faithful")))


def report_block():
    text = (HERE / "REPORT.md").read_text()
    block = re.search(r"\*\*Statement as built\*\*.*?```lean\n(.*?)```", text, re.DOTALL)
    assert block, "section 3 has no statement block"
    return " ".join(line.strip() for line in block.group(1).splitlines() if line.strip())


def test_report_block_is_the_built_statement():
    assert qualify(report_block().replace(NAMESPACE, "")) == built_statement()


def test_report_names_every_constant_where_built_and_plan_differ():
    plan, built = names(plan_statement()), names(built_statement())
    differing = (plan - built) | (built - plan)
    report = (HERE / "REPORT.md").read_text()
    for name in sorted(differing):
        assert f"`{name}`" in report, f"REPORT.md does not name {name}, where the built statement differs from the plan"
    # Pinned: the one difference F1 found. If the plan or the build changes, this test is reread with them.
    assert differing == {"VE.Core.NaryIntended", "VE.Acts.Nary.NaryIntended"}


def test_no_record_claims_the_plan_text_while_they_differ():
    if names(plan_statement()) == names(built_statement()):
        return
    for name in ("REPORT.md", "route-a.patch"):
        text = (HERE / name).read_text()
        hits = [(n + 1, line) for n, line in enumerate(text.splitlines()) if IDENTITY_CLAIMS.search(line)
                and ("reify_faithful" in line or "plan" in line or "section 3" in line or "Statement" in line)]
        assert not hits, (name, hits)


def test_bar_row_1_is_qualified_by_the_constant_proved():
    report = (HERE / "REPORT.md").read_text()
    row = next(line for line in report.splitlines() if line.startswith("| proves its faithfulness statement"))
    route_a = row.split("|")[2]
    assert "VE.Acts.Nary.NaryIntended" in route_a and "VE.Core.NaryIntended" in route_a
    assert "every row" not in report.split("## Notes for the DRI")[1].split("## Self-review")[0]


def test_seeded_identity_claims_are_caught():
    """The pattern catches each phrase F1 and its sweep found (REPORT :70, :316; patch :31, :449)."""
    for line in ("**Statement as built** (`lean/VE/Acts/Nary.lean:431`), section 3's text unchanged:",
                 "10. Lean statements say what is claimed: PASS. `reify_faithful` matches plan:701-702 (spec re-read",
                 "+tuples of its events (`ActHolds`). `reify_faithful` is section 3's statement as written. -/",
                 "+source rules say, given one event per argument tuple (plan section 3, verbatim). -/"):
        assert IDENTITY_CLAIMS.search(line), line
