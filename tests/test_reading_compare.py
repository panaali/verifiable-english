"""Feature C's sealed-answer gate (usecases/reading_compare.py): gates (1), (2), (4) and (6) of the orchestrator's
2026-11-24T00:00Z ruling. The last test runs the gate on the real reading tables (usecases/reading_tables/), so a change
to any table, run, match, register or check record there selects it and fails until the table is run, compared and
checked again."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from usecases import reading_compare as rc

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "reading_compare" / "uc-award-843bed8223"
COLS = ["block", "citation", "words", "reading", "name", "rules_en", "edits", "questions", "differ_case", "differ_expect"]


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def _mini(d, names=("x is read narrowly", "x is read widely"), answers=("YES", "NO"), match="A=a B=b",
          status="LIVE", check_on_current=True, plain_key=False):
    """A one-law, one-block gate directory: law 'toy', block B1, question C1/Q1, sealed a=YES b=NO."""
    d.mkdir(parents=True, exist_ok=True)
    rows = ["# law\t{}", "\t".join(COLS)]
    for r, n in zip("AB", names):
        rows.append("\t".join(["B1", "s. 1", "x", r, n, "rule", "[]", "C1/Q1", "{}", "{}"]))
    table = "\n".join(rows) + "\n"
    (d / "toy.tsv").write_text(table)
    tsha = _sha(table)
    (d / "runs").mkdir(exist_ok=True)
    (d / "runs" / "toy.json").write_text(json.dumps({"table_sha256": tsha, "blocks": {"B1": {"questions": {"C1/Q1": {
        "status": "per-reading", "answers": dict(zip("AB", answers)), "decided": {"A": True, "B": True}}}}}}))
    (d / "match").mkdir(exist_ok=True)
    for g in ("g1", "g2"):
        m = match if isinstance(match, str) else match[g == "g2"]
        (d / "match" / f"{g}.txt").write_text(f"# table toy {tsha}\ntoy:C1:B1: {m} | reason\n")
    if plain_key:
        key = 'question\tlaw\tsealed_a\tsealed_b\nC1/Q1\ttoy\t"YES"\t"NO"\n'
    else:
        key = "question\tlaw\tsealed_a\tsealed_b\n" + "\t".join(
            ["C1/Q1", "toy", json.dumps(rc.seal("C1/Q1", "a", "", "YES")), json.dumps(rc.seal("C1/Q1", "b", "", "NO"))]) + "\n"
    (d / "SEALED.tsv").write_text(key)
    reg = ["law\tblock\treading\tname_sha256\tstatus\tsince\tnote"]
    reg += [f"toy\tB1\t{r}\t{_sha(n)}\t{status}\t2026-11-24T00:00Z\tfixture" for r, n in zip("AB", ("x is read narrowly",
                                                                                                 "x is read widely"))]
    (d / "READINGS.tsv").write_text("\n".join(reg) + "\n")
    csha = tsha if check_on_current else "0" * 64
    (d / "CHECKS.tsv").write_text(f"law\tcheck\ttable_sha256\tutc\tverdict\tfile\ntoy\tsource-check\t{csha}\t"
                                  "2026-11-24T00:00Z\tSOUND\tx\n")
    return d


def _kinds(res):
    return sorted(f.split(" ", 1)[0] for f in res["failures"])


def test_843bed8223_uc_award_table_fails_on_u021_reading_b():
    """Failing first: the uc-award table and run the 843bed8223 build stopped on, with the only match on record."""
    res = rc.check(FIX)
    wrong = sorted(f for f in res["failures"] if f.startswith("WRONG"))
    assert [w.split(":")[0] for w in wrong] == ["WRONG uc-award U021/U021-2 reading B", "WRONG uc-award U021/U021-3 reading B"]
    assert rc.main(["--dir", str(FIX)]) == 1
    assert any(f.startswith("STALE uc-award: match grader") for f in res["failures"])  # the match predates fix 1


def test_matching_answers_pass(tmp_path):
    res = rc.check(_mini(tmp_path / "g"))
    assert res["failures"] == []
    assert res["laws"]["toy"]["per_reading"] == {"answered": 2, "disputed": 0, "wrong": 0, "not answered": 0}


def test_plain_key_also_compares(tmp_path):
    assert rc.check(_mini(tmp_path / "g", plain_key=True))["failures"] == []
    assert _kinds(rc.check(_mini(tmp_path / "h", plain_key=True, answers=("YES", "YES")))) == ["WRONG"]


def test_a_mismatch_fails(tmp_path):
    res = rc.check(_mini(tmp_path / "g", answers=("YES", "YES")))
    assert _kinds(res) == ["WRONG"]
    assert res["laws"]["toy"]["per_reading"]["wrong"] == 1


def test_a_mismatch_under_one_grader_fails_though_not_counted(tmp_path):
    res = rc.check(_mini(tmp_path / "g", answers=("YES", "YES"), match=("A=a B=b", "NO MATCH")))
    assert _kinds(res) == ["WRONG"]


def test_a_changed_table_is_stale_until_run_again(tmp_path):
    d = _mini(tmp_path / "g")
    (d / "toy.tsv").write_text((d / "toy.tsv").read_text().replace("\trule\t", "\trule, changed\t"))
    kinds = _kinds(rc.check(d))
    assert kinds.count("STALE") == 4  # the run, the source check and both match graders saw the old table


def test_a_check_on_an_older_table_is_stale(tmp_path):
    assert _kinds(rc.check(_mini(tmp_path / "g", check_on_current=False))) == ["STALE"]


def test_a_replaced_reading_is_a_swap(tmp_path):
    d = _mini(tmp_path / "g", names=("x is read narrowly", "x is read some third way"))
    assert "SWAP" in _kinds(rc.check(d))


def test_an_unregistered_reading_fails(tmp_path):
    d = _mini(tmp_path / "g")
    (d / "READINGS.tsv").write_text("law\tblock\treading\tname_sha256\tstatus\tsince\tnote\n")
    assert _kinds(rc.check(d)) == ["MISSING", "MISSING"]


def test_a_stopped_block_is_disputed_never_answered(tmp_path):
    res = rc.check(_mini(tmp_path / "g", status="STOPPED", answers=("YES", "YES")))
    assert res["failures"] == []  # no answer of a stopped block is graded, so none is counted, right or wrong
    assert res["laws"]["toy"]["per_reading"] == {"answered": 0, "disputed": 2, "wrong": 0, "not answered": 0}


@pytest.mark.parametrize("match", ["NO MATCH", ("A=a B=b", "A=b B=a")])
def test_not_the_writers_reading_or_graders_differ_is_disputed(tmp_path, match):
    res = rc.check(_mini(tmp_path / "g", match=match, answers=("YES", "YES") if match == "NO MATCH" else ("YES", "NO")))
    assert res["laws"]["toy"]["per_reading"]["answered"] == 0
    assert res["laws"]["toy"]["per_reading"]["disputed"] + res["laws"]["toy"]["per_reading"]["wrong"] == 2


def test_two_graders_needed(tmp_path):
    d = _mini(tmp_path / "g")
    (d / "match" / "g2.txt").unlink()
    assert "MISSING:" in [f.split(" ", 1)[0] for f in rc.check(d)["failures"]]


def test_per_reading_counts_stand_apart_from_any_headline(tmp_path):
    """Gate (6): the gate's output has per-reading counts only; it has no single-answer count to add them to."""
    res = rc.check(_mini(tmp_path / "g"))
    assert set(res) == {"failures", "laws", "questions"}
    assert set(res["laws"]["toy"]) == {"table_sha256", "per_reading", "stopped"}
    assert not any(re.search("headline|correct|single", k) for k in json.dumps(res["laws"]).split('"'))


def test_the_sealed_key_on_the_branch_shows_no_answer():
    text = (rc.HERE / "SEALED.tsv").read_text()
    for plain in ('"YES"', '"NO"', "99.90", "HIGHER JOINT", "2028-05-31", "Zack"):
        assert plain not in text


def test_the_reading_tables_pass_the_sealed_gate():
    """The gate itself, on every reading table in usecases/reading_tables/."""
    res = rc.check(rc.HERE)
    assert res["failures"] == [], "\n".join(res["failures"])
    assert sorted(p.stem for p in rc.HERE.glob("*.tsv") if not p.stem.isupper()) == sorted(res["laws"])


def test_fixture_is_a_copy_not_the_live_dir(tmp_path):
    shutil.copytree(FIX, tmp_path / "f")
    assert rc.check(tmp_path / "f")["failures"] == rc.check(FIX)["failures"]


def _verdict(d, verdict, findings=()):
    tsha = _sha((d / "toy.tsv").read_text())
    (d / "CHECKS.tsv").write_text(f"law\tcheck\ttable_sha256\tutc\tverdict\tfile\ntoy\tsource-check\t{tsha}\tt\t{verdict}\tx\n")
    rows = ["law\ttable_sha256\tcheck\tseverity\tmoves_listed_answer\tfinding\tdisposition"]
    rows += [f"toy\t{tsha}\tsource-check\tHIGH\t{m}\tgap\t{disp}" for m, disp in findings]
    (d / "FINDINGS.tsv").write_text("\n".join(rows) + "\n")
    return [f.split(" ", 1)[0] for f in rc.check(d)["failures"]]


def test_a_source_check_with_findings_fails_unless_each_high_is_recorded(tmp_path):
    d = _mini(tmp_path / "g")
    assert _verdict(d, "FINDINGS (1 WRONG, 0 HIGH)") == ["SOURCE-CHECK"]
    assert _verdict(d, "0 WRONG, 1 HIGH (no listed answer moves)") == ["SOURCE-CHECK"]
    assert _verdict(d, "0 WRONG, 1 HIGH (no listed answer moves)", [("yes", "kept")]) == ["SOURCE-CHECK"]
    assert _verdict(d, "0 WRONG, 1 HIGH (no listed answer moves)", [("no", " ")]) == ["SOURCE-CHECK"]
    assert _verdict(d, "0 WRONG, 2 HIGH (no listed answer moves)", [("no", "filed")]) == ["SOURCE-CHECK"]
    assert _verdict(d, "0 WRONG, 1 HIGH (no listed answer moves)", [("no", "filed as row x")]) == []
