"""JT-E1s frame, revision and scoring checks. These tests never invoke a reader model."""
import importlib.util
import json
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parents[1] / "docs/judgment-terms"
ROOT = DOCS / "jt-e1s"

spec = importlib.util.spec_from_file_location("jt_e1s_runner", ROOT / "runner.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
render = runner.render
FALLBACK = ["U17", "U18", "U19", "U20", "C17", "C18", "C19", "C20"]


def test_frozen_frame_and_real_capture_bytes():
    rows = render.rows()
    assert render.audit() == FALLBACK
    for source in "UC":
        group = [r for r in rows if r["id"].startswith(source)]
        assert len(group) == 20
        assert [r["answer"] for r in group] == ["turns", "settled", "conditional", "turns"] * 5
        assert [r["decider"] == "unstated" for r in group] == [False, True, False, False] * 5
    for row in rows:
        meta = json.loads((render.CAPTURES / f"{row['id']}.command.json").read_text())
        assert meta["commit"] == render.PIN
        assert meta["command"][1:4] == ["-m", "ve", "render"]
        assert meta["command"][-1].endswith(meta["document"])


def test_revision_keeps_the_declaration_and_adds_the_answer_row():
    for row in render.rows():
        old, new = render.displays(row)
        if row["lint"] != "accepted":
            assert old == new and render.english(row, old) == old
            continue
        atom, decider = row["atom"], row["decider"]
        ending = "; the text does not say who makes it." if decider == "unstated" else f" for {decider}."
        assert render.declaration(row) == f"Whether {atom} is a judgment{ending}\n"
        answer = {
            "settled": [f"Settled: whatever is judged here, the text requires that {row['conclusion']}."],
            "turns": [f"Left to {decider}: these two admissible completions give different answers and differ"
                      f" on whether {atom} (a judgment for {decider})."],
            "conditional": [f"These rules conflict where {atom}.",
                            f"Conflict-free, given these sentences: {row['criterion']}"],
        }[row["answer"]]
        assert new.decode().splitlines() == [render.declaration(row).rstrip("\n"), *answer]
        assert old != new and render.english(row, old) == new


def test_prompt_and_shared_information_are_jt_e1r_s():
    e1r = (DOCS / "jt-e1r/runner.py").read_text()
    assert runner.PROMPT in e1r.replace('"\n    "', "")
    for row in render.rows():
        for arm in ("identifier", "english"):
            body = runner.prompt(row, arm)
            assert body.startswith(runner.PROMPT) and render.common_text(row) in body
            for value in (row["source"], row["conclusion"], row["predicate"], row["atom"], row["decider"]):
                assert value in body
            assert "KEY:" not in body and row["answer"].upper() not in body[len(runner.PROMPT):]


def test_pre_registration_quotes_the_bars_verbatim():
    def bars(path):
        return [line.removeprefix("> ") for line in path.read_text().splitlines() if line.startswith("> (")]
    quoted = bars(ROOT / "PRE-REGISTRATION.md")
    assert len(quoted) == 2 and quoted == bars(DOCS / "jt-e1r/PRE-REGISTRATION.md")
    plan = (DOCS.parent / "spec/judgment-terms-PLAN.md").read_text()
    assert all(f"  - {line}\n" in plan for line in quoted)


def test_items_are_fresh():
    old = "".join((DOCS / f"{item}/items.tsv").read_text() for item in ("jt-e1", "jt-e1r"))
    for row in render.rows():
        assert row["source"] not in old and row["predicate"] not in old


def test_runner_is_bound_to_this_frame(monkeypatch):
    assert runner.base.RAW == ROOT / "raw" and runner.base.render is render
    assert runner.base.committed is runner.committed
    assert {"jt-e1s/items.tsv", "jt-e1r/runner.py", "jt-e1r/render.py"} <= set(runner.FROZEN)
    records = {f"{r['id']}-{arm}.json": None for r in render.rows() for arm in ("identifier", "english")}
    monkeypatch.setattr(runner.base, "existing", lambda: dict(list(records.items())[:-1]))
    with pytest.raises(RuntimeError, match="79 of 80"):
        runner.results()


def test_saved_records_reproduce_the_gate_line():
    result = runner.results()
    assert result["counts"] == {"identifier": 20, "english": 25}
    assert (result["bar_a"], result["bar_b"], result["critical"], result["errors"]) == (False, True, [], [])
    assert (result["calls"], result["cw"], result["fallback"]) == (80, 1_185_742, FALLBACK)
    gate = (ROOT / "RESULTS.md").read_text().splitlines()[2]
    assert gate.startswith("**JT-3 wording gate FAIL") and "25/40" in gate and "20/40" in gate
    for record in runner.base.existing().values():
        assert set(record["cli"]["modelUsage"]) == {runner.base.MODEL}
        assert record["cli"]["usage"]["fallback_credit"] is None


def test_commit_check_accepts_the_committed_frame_and_refuses_an_edit(tmp_path, monkeypatch):
    for name in runner.FROZEN:
        (tmp_path / name).parent.mkdir(exist_ok=True)
        (tmp_path / name).write_bytes((DOCS / name).read_bytes())
    monkeypatch.setattr(runner, "HERE", tmp_path / "jt-e1s")
    runner.committed()
    (tmp_path / "jt-e1r/runner.py").write_text("edited\n")
    with pytest.raises(RuntimeError, match="commit jt-e1r/runner.py"):
        runner.committed()
