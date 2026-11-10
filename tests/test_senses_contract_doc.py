"""The web app's JSON contract (docs/spec/senses.md 2.7.1) against the objects the three commands print (sn-b7b
review F1, F2): each command's table names exactly the members it prints, every field of their rows is named in
the member's row, and the definition of `lacking` is the one the code computes."""
from __future__ import annotations

import copy
import re
import sys
from pathlib import Path

import pytest

from ve.backends import senses as route

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_senses_display import AMUSING, RESOLVED, S16, STRANGE, TWO  # noqa: E402
from test_senses_display_cli import run  # noqa: E402
from test_senses_route import world  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/spec/senses.md"
# The commands of 2.7.1, by the text that introduces each one's table.
COMMANDS = {"render": "`ve render ", "resolve": "`ve senses resolve ", "propose-readings": "`ve senses propose-readings "}
# Members whose fields are documented elsewhere: Lean's reading (3.2 and its schema) and the pack-name map.
ELSEWHERE = {"reading", "review_status"}
# Fields whose values are data, not named fields: model ids, reading ids, formulas.
DATA = {"models", "distinguishing_models", "content", "model"}


def contract() -> dict[str, dict[str, str]]:
    """Each command's members as 2.7.1's tables give them: every backticked name of a row's first cell, mapped to
    the row's meaning cell."""
    text = SPEC.read_text(encoding="utf-8")
    section = text[text.index("### 2.7.1 "):text.index("### 2.8 ")]
    tables: dict[str, dict[str, str]] = {}
    command, paragraph, intro = None, "", ""
    for line in section.splitlines():
        if line.startswith("|"):
            if command is None:
                [command] = [name for name, start in COMMANDS.items() if start in (paragraph or intro)]
                tables[command] = {}
            first, meaning = (cell.strip() for cell in line.strip("|").split("|", 1))
            if first not in ("Member", "---"):
                for name in re.findall(r"`([^`]+)`", first):
                    if name.startswith("--"):  # the option that adds the member: `glossary` (with `--glossary`)
                        continue
                    assert name not in tables[command], (command, name)
                    tables[command][name] = meaning
            continue
        command = None
        if line.strip():
            paragraph += line + " "
        elif paragraph:
            intro, paragraph = paragraph, ""
    assert tables.keys() == COMMANDS.keys()
    return tables


def fields(value) -> set[str]:
    """The field names in a printed member, at any depth, skipping the values that are data."""
    if type(value) is dict:
        return set(value) | {name for key, item in value.items() if key not in DATA for name in fields(item)}
    if type(value) is list:
        return {name for item in value for name in fields(item)}
    return set()


def named(meaning: str) -> set[str]:
    """The identifiers inside the backticked spans of a meaning cell (`{word, gloss, text}` names three)."""
    return {word for span in re.findall(r"`([^`]+)`", meaning) for word in re.findall(r"\w+", span)}


@pytest.fixture(scope="module")
def place():
    return world()


def printed(tmp_path, capsys, monkeypatch, place) -> dict[str, list[dict]]:
    """Each command's printed objects over fixtures that give every member and row kind: an open and a resolved
    reading with the glossary and hover; a line Lean gives and one it refuses; a set, a resolving row and an
    unproposed pair (Lean's flip status `undistinguished`)."""
    out = {name: [] for name in COMMANDS}
    for source in (TWO, RESOLVED):
        out["render"].append(run(tmp_path, capsys, place, "render", source, "--glossary", "--json")[1])
    for gloss in ("strange", "purple"):
        out["resolve"].append(run(tmp_path, capsys, place, "resolve", S16, "--word", "odd", "--gloss", gloss)[1])
    for source in (TWO, S16):
        out["propose-readings"].append(
            run(tmp_path, capsys, place, "propose-readings", source, "--output", str(tmp_path / "sets.json"))[1])
    lean = route.read

    def undistinguished(*args, **kwargs):
        answer = lean(*args, **kwargs)
        if kwargs.get("reread") is None:
            answer = copy.deepcopy(answer)
            for flip in answer["reading"]["flips"]:
                flip["status"] = "undistinguished"
        return answer

    monkeypatch.setattr(route, "read", undistinguished)
    out["propose-readings"].append(run(tmp_path, capsys, place, "propose-readings", TWO)[1])
    return out


def test_each_commands_table_names_exactly_the_members_it_prints(tmp_path, capsys, monkeypatch, place):
    """F1: a printed member missing from its command's table (`output_written`, `review_status`), or a documented
    member the command never prints (`undistinguished` for `unproposed`), fails; so does a row field (at any depth)
    its member's row does not name. The fixtures give every member: each documented one is printed by one of them."""
    tables = contract()
    objects = printed(tmp_path, capsys, monkeypatch, place)
    for command, documented in tables.items():
        members = {name for o in objects[command] for name in o}
        assert members == documented.keys(), (command, sorted(members ^ documented.keys()))
        for name in members - ELSEWHERE:
            values = [o[name] for o in objects[command] if name in o]
            missing = {f for v in values for f in fields(v)} - named(documented[name])
            assert not missing, (command, name, sorted(missing))


def test_the_tables_name_every_row_kind_the_fixtures_give(tmp_path, capsys, monkeypatch, place):
    """The fixtures are not vacuous: each row member the field check reads has at least one row."""
    objects = printed(tmp_path, capsys, monkeypatch, place)
    for command, members in [("render", ("renderings", "glossary", "hover")),
                             ("propose-readings", ("reading_sets", "texts", "resolving", "unproposed"))]:
        for name in members:
            rows = [o[name]["senses"] if name == "glossary" else o[name] for o in objects[command] if name in o]
            assert any(rows), (command, name)


def test_lacking_is_defined_as_the_last_lines_of_the_choice(tmp_path, capsys, place):
    """F2: on a preamble line written with two spaces, `lines` gives Lean's spelling and `preamble` the line as
    written, so "the `lines` not among the `preamble` lines" names the odd line too; the code (and the contract)
    give the last len(`choice`) lines, the choice's alone."""
    written = "In this document,  odd means strange."
    code, out = run(tmp_path, capsys, place, "render", written + "\n" + TWO)
    assert code == 3 and out["reading"]["preamble"] == [written]
    for row, unit_candidate, choice_line in zip(out["renderings"], out["reading"]["units"][0]["candidates"],
                                                (AMUSING, STRANGE)):
        split = row["lines"].split("\n")
        assert row["lacking"] == split[len(split) - len(unit_candidate["choice"]):] == [choice_line]
        assert [line for line in split if line not in out["reading"]["preamble"]] != row["lacking"]
    lacking = contract()["render"]["renderings"]
    assert "that are not among the reading's `preamble` lines" not in SPEC.read_text(encoding="utf-8")
    assert "the last len(`choice`) of the `lines`" in lacking
    assert contract()["propose-readings"]["resolving"].count("`lacking` (as in `renderings`)") == 1
