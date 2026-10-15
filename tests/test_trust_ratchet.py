"""The trust budget as a ratchet (architecture plan AR-4, DRI decision D3): `tools/trust_map.py`'s
`--check`, `--allow` and `--write` over small git histories, and the committed budget file."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lean_statements  # noqa: E402
import trust_map  # noqa: E402

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
       "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
SIGNED = ["--reason", "demo growth", "--signed", "DRI 2026-10-10"]


def test_review_f6_probe_rejects_float_budget():
    files = {"x.lean": {**trust_map.empty_counts(), "K": 1, "trusted": 1, "lines": 1}}
    now = trust_map.totals(files)
    record = {"files": files, "totals": now, "budget": trust_map.budget(now)}
    assert trust_map.files_problems(record) == []
    record["budget"]["K"] = 1.0
    assert trust_map.files_problems(record)


def git(root: Path, *args: str, check: bool = True) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=ENV)
    assert done.returncode == 0 or not check, done.stderr
    return done.stdout.strip()


def write(root: Path, modules: dict[str, list[tuple[str, int, str]]]) -> None:
    """A compiled tree: each module (a path under lean/) holds its definitions `(name, lines, class)`
    one after the other, and the dumps and side table record them as tools/lean_statements.py and
    a reviewer would. Every definition is `lines` long (at least two)."""
    for path in (root / "lean").rglob("*.lean"):
        path.unlink()
    blocks, table, names = [], {}, []
    for module, decls in sorted(modules.items()):
        name = lean_statements.module_name(module)
        names.append(name)
        source, entries = [f"namespace {name}"], []
        for decl, lines, cls in decls:
            start = len(source) + 1
            source += [f"def {decl} : Nat :=", *["  0 +"] * (lines - 2), "  0"]
            entries.append(f"{start}:0-{len(source)}:{len(source[-1])} def {name}.{decl}@{name}")
            table.setdefault(module, {}).setdefault(cls, []).append(f"{name}.{decl}")
        source.append(f"end {name}")
        path = root / "lean" / module
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(source) + "\n")
        blocks.append(f"module {name} {lean_statements.source_hash(path)}\n" + "".join(f"{e}\n" for e in entries))
    (root / "lean/declarations.txt").write_text("-- header\n" + "".join(blocks))
    (root / "lean/predicates.txt").write_text("-- header\n" + "".join(f"module {n}\n" for n in names))
    (root / "lean/statements.txt").write_text("")
    (root / "tools").mkdir(exist_ok=True)
    (root / "tools/trust-classes.json").write_text(json.dumps({"modules": table}, indent=1) + "\n")


def run(root: Path, *flags: str) -> int:
    return trust_map.main([*flags, "--root", str(root)])


def baseline(root: Path) -> dict:
    return json.loads((root / "docs/trust-baseline.json").read_text())


def commit(root: Path, message: str) -> str:
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """`main` with one untrusted definition (C, 3 lines) and its starting budget, written outside git."""
    write(tmp_path, {"VE/Demo.lean": [("base", 3, "C")]})
    (tmp_path / "docs").mkdir()
    assert run(tmp_path, "--write") == 0
    git(tmp_path, "init", "-q", "-b", "main")
    commit(tmp_path, "base")
    return tmp_path


def test_ten_untied_lines_need_a_signed_allowance(repo, capsys):
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-qb", "feature")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "decoder")
    capsys.readouterr()
    assert run(repo, "--check") == 1
    assert f"BUDGET against {base[:12]}: V grew from 0 to 10 (signed allowance 0): VE/Demo.lean +10" \
        in capsys.readouterr().err
    with pytest.raises(SystemExit):  # a signature is required
        run(repo, "--allow", "--reason", "demo growth")
    assert baseline(repo)["allowances"] == []
    assert run(repo, "--allow", *SIGNED) == 0
    assert baseline(repo)["allowances"] == [{"class": "V", "lines": 10, "reason": "demo growth",
                                             "signature": "DRI 2026-10-10", "commit": base}]
    assert baseline(repo)["budget"] == {"K": 0, "S": 0, "V": 0}  # the budget is the merge train's
    assert run(repo, "--check") == 0
    capsys.readouterr()
    assert run(repo, "--write") == 1  # a branch never writes the budget
    assert "written by the merge train on main" in capsys.readouterr().err
    assert baseline(repo)["budget"] == {"K": 0, "S": 0, "V": 0}
    assert run(repo, "--allow", *SIGNED) == 0 and len(baseline(repo)["allowances"]) == 1  # nothing more to allow
    # One more trusted line is growth over the allowance; an edited allowance is checked as written.
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 11, "D[V]")]})
    assert run(repo, "--check") == 1
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    assert run(repo, "--check") == 0
    edited = baseline(repo)
    edited["allowances"][0]["lines"] = 9
    (repo / "docs/trust-baseline.json").write_text(json.dumps(edited))
    assert run(repo, "--check") == 1


NOT_SIGNATURES = [trust_map.UNSIGNED, "unsigned", "DRI signature pending", "awaiting the DRI", "DRI: TBD",
                  "DRI (not yet signed)", "TODO DRI", "approved by the review", "x", "driver 2026-10-10"]
SIGNATURES = ["DRI 2026-10-10", "DRI (orchestrator), lf-6 fix directive, 2026-10-06", "R6 (DRI-RULINGS.md)"]


@pytest.mark.parametrize("signature", NOT_SIGNATURES)
def test_a_new_allowance_without_the_dris_signature_grants_nothing(repo, capsys, signature):
    """arch-AR-4 review F4: a new allowance carrying the migration's `UNSIGNED` marker (or any text
    that is no DRI signature) granted its growth. Every way in refuses it: `--allow --signed`, and an
    allowance written into the file by hand and checked."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-qb", "feature")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "decoder")
    with pytest.raises(SystemExit):
        run(repo, "--allow", "--reason", "demo growth", "--signed", signature)
    data = baseline(repo)
    entry = {"class": "V", "lines": 10, "reason": "demo growth", "signature": signature, "commit": base}
    (repo / "docs/trust-baseline.json").write_text(json.dumps({**data, "allowances": [entry]}))
    capsys.readouterr()
    assert run(repo, "--check") == 1
    err = capsys.readouterr().err
    assert "not the DRI's" in err or f"introduced since {base[:12]}" in err and "marks a rebaseline" in err, err


@pytest.mark.parametrize("signature", SIGNATURES)
def test_a_dri_or_standing_ruling_signature_grants_growth(repo, signature):
    git(repo, "checkout", "-qb", "feature")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "decoder")
    assert run(repo, "--allow", "--reason", "demo growth", "--signed", signature) == 0
    assert run(repo, "--check") == 0


def test_an_inherited_unsigned_allowance_stays_and_grants_nothing_new(repo, capsys):
    """The 45 rebaselines before AR-4 keep the marker: the base has them, so they are history, not
    growth; the probe of review F4 (the marker as a new allowance) fails, as written there."""
    data = baseline(repo)
    entry = {"class": "V", "lines": 10, "reason": "old growth", "signature": trust_map.UNSIGNED, "commit": "a" * 40}
    (repo / "docs/trust-baseline.json").write_text(json.dumps({**data, "allowances": [entry]}))
    commit(repo, "the migrated history")
    git(repo, "checkout", "-qb", "feature")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "decoder")
    capsys.readouterr()
    assert run(repo, "--check") == 1
    assert "V grew from 0 to 10 (signed allowance 0)" in capsys.readouterr().err


def test_review_f4_probe(monkeypatch, tmp_path):
    """PROBE F4 of arch-AR-4-review, as a test: `gate` over a measured base without allowances."""
    zero = dict.fromkeys(trust_map.BUDGET, 0)
    entry = dict(zip(trust_map.ALLOWANCE, ("V", 1, "growth", trust_map.UNSIGNED, "a" * 40)))
    monkeypatch.setattr(trust_map, "resolve_base", lambda *_: ("a" * 40, None))
    monkeypatch.setattr(trust_map, "measure_rev", lambda *_: ({}, [], {"budget": zero, "allowances": []}))
    monkeypatch.setattr(trust_map, "report", lambda *_: None)
    files = {"x": {**trust_map.empty_counts(), "D": 1, "D[V]": 1, "trusted": 1}}
    path = tmp_path / "trust-baseline.json"
    path.write_text(json.dumps({"budget": zero, "allowances": [entry]}))
    assert trust_map.gate(argparse.Namespace(since=None, allow=False, write=False), tmp_path, files, path) == 1


def test_an_allowance_the_base_has_is_not_this_changes(repo, capsys):
    """An allowance already in the base's file was spent there; a copy of it is refused."""
    git(repo, "checkout", "-qb", "first")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "first")
    assert run(repo, "--allow", *SIGNED) == 0
    commit(repo, "first's allowance")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "first", "-m", "merge first")
    git(repo, "checkout", "-qb", "second")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 20, "D[V]")]})
    commit(repo, "second")
    capsys.readouterr()
    assert run(repo, "--check") == 1
    assert "V grew from 10 to 20 (signed allowance 0)" in capsys.readouterr().err
    data = baseline(repo)
    (repo / "docs/trust-baseline.json").write_text(json.dumps({**data, "allowances": data["allowances"] * 2}))
    assert run(repo, "--check") == 1
    assert "is recorded 2 times" in capsys.readouterr().err


def test_an_allowance_is_never_removed(repo, capsys):
    """The allowances are the history: a change that drops one of its base's fails, even when the
    tree no longer needs it."""
    git(repo, "checkout", "-qb", "grow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "grow")
    assert run(repo, "--allow", *SIGNED) == 0
    commit(repo, "grow's allowance")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "grow", "-m", "merge grow")
    git(repo, "checkout", "-qb", "drop")
    write(repo, {"VE/Demo.lean": [("base", 3, "C")]})
    commit(repo, "drop the decoder")
    assert run(repo, "--check") == 0
    data = baseline(repo)
    (repo / "docs/trust-baseline.json").write_text(json.dumps({**data, "allowances": []}))
    capsys.readouterr()
    assert run(repo, "--check") == 1
    assert "the allowance ('V', 10, 'demo growth', 'DRI 2026-10-10') of " in capsys.readouterr().err
    edited = {**data, "allowances": [{**data["allowances"][0], "reason": "edited"}]}
    (repo / "docs/trust-baseline.json").write_text(json.dumps(edited))
    assert run(repo, "--check") == 1  # an edited allowance is a removal and a new one


def test_deleting_trusted_lines_lowers_the_budget_at_the_merge(repo, capsys):
    git(repo, "checkout", "-qb", "grow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "grow")
    assert run(repo, "--allow", *SIGNED) == 0
    commit(repo, "grow's allowance")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "grow", "-m", "merge grow")
    assert run(repo, "--write") == 0  # the merge train: against the first parent plus the merged allowance
    assert baseline(repo)["budget"] == {"K": 0, "S": 0, "V": 10}
    commit(repo, "budget after grow")
    git(repo, "checkout", "-qb", "shrink")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 4, "D[V]")]})
    assert run(repo, "--check") == 0  # deleting trusted lines needs nothing
    commit(repo, "shrink")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "shrink", "-m", "merge shrink")
    merged = git(repo, "rev-parse", "HEAD")
    # Before the merge train writes the lower budget, a branch that adds the lines back already fails:
    # its cap is main measured, not the recorded 10.
    git(repo, "checkout", "-qb", "regrow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "regrow")
    capsys.readouterr()
    assert run(repo, "--check") == 1
    err = capsys.readouterr().err
    assert f"BUDGET against {merged[:12]}: V grew from 4 to 10" in err
    git(repo, "checkout", "-q", "main")
    capsys.readouterr()
    assert run(repo, "--write") == 0
    assert baseline(repo)["budget"] == {"K": 0, "S": 0, "V": 4}
    assert "note: " not in capsys.readouterr().out  # the first parent's recorded budget was its measurement
    assert len(baseline(repo)["allowances"]) == 1  # the history stays


def test_an_uncommitted_merge_on_main_is_checked_against_head(repo, capsys):
    """The merge train checks before committing the merge (`regen_generated.py --resolve`): the base
    is HEAD, the merge's first parent, not HEAD's own parent. Here main grew 10 signed lines, then
    deleted 6; a branch that adds them back without an allowance must fail, although the commit
    before the deletion had them."""
    git(repo, "checkout", "-qb", "grow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "grow")
    assert run(repo, "--allow", *SIGNED) == 0
    commit(repo, "grow's allowance")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "grow", "-m", "merge grow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 4, "D[V]")]})
    shrunk = commit(repo, "shrink on main")
    git(repo, "checkout", "-qb", "regrow")
    write(repo, {"VE/Demo.lean": [("base", 3, "C"), ("decoder", 10, "D[V]")]})
    commit(repo, "regrow")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "--no-commit", "regrow")
    capsys.readouterr()
    assert run(repo, "--check") == 1
    assert f"BUDGET against {shrunk[:12]}: V grew from 4 to 10" in capsys.readouterr().err
    assert run(repo, "--since", "HEAD^1") == 0  # the commit before the deletion would have let it through
    git(repo, "merge", "--abort")
    assert run(repo, "--check") == 0  # committed, main's tip is checked against its first parent


def test_two_branches_each_adding_an_allowance_merge_without_a_conflict(repo):
    """Each branch adds a module and an allowance. The budget file merges by the repository's
    `ve-generated` driver (tools/regen_generated.py, json strategy): both allowances, one budget,
    no totals to conflict; the dumps and the table are regenerated, as the merge train does."""
    (repo / ".gitattributes").write_text("docs/trust-baseline.json merge=ve-generated\n")
    git(repo, "config", "merge.ve-generated.driver",
        f"{sys.executable} {ROOT / 'tools/regen_generated.py'} --merge-driver %O %A %B %P")
    commit(repo, "attributes")
    base = {"VE/Demo.lean": [("base", 3, "C")]}
    sides = {"x": {"VE/X.lean": [("x", 5, "D[V]")]}, "y": {"VE/Y.lean": [("y", 7, "G[V]")]}}
    for branch, added in sides.items():
        git(repo, "checkout", "-q", "main")
        git(repo, "checkout", "-qb", branch)
        write(repo, {**base, **added})
        assert run(repo, "--allow", "--reason", f"{branch} growth", "--signed", "DRI") == 0
        commit(repo, branch)
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "x", "-m", "merge x")
    git(repo, "merge", "-q", "--no-ff", "y", "-m", "merge y", check=False)
    conflicted = git(repo, "diff", "--name-only", "--diff-filter=U").split()
    assert "docs/trust-baseline.json" not in conflicted
    assert set(conflicted) <= {"lean/declarations.txt", "lean/predicates.txt", "tools/trust-classes.json"}
    merged = baseline(repo)
    assert set(merged) == {"comment", "budget", "allowances"} and merged["budget"] == {"K": 0, "S": 0, "V": 0}
    assert [(a["lines"], a["reason"]) for a in merged["allowances"]] == [(5, "x growth"), (7, "y growth")]
    write(repo, {**base, **sides["x"], **sides["y"]})
    commit(repo, "merge y")
    assert run(repo, "--check") == 0
    assert run(repo, "--write") == 0 and baseline(repo)["budget"] == {"K": 0, "S": 0, "V": 12}
    # Taking main's side of the file instead (dropping y's allowance) fails closed.
    data = baseline(repo)
    (repo / "docs/trust-baseline.json").write_text(json.dumps({**data, "allowances": data["allowances"][:1]}))
    assert run(repo, "--since", "HEAD^1") == 1


def test_files_go_to_the_gate_record_not_the_budget_file(repo, tmp_path_factory):
    record = tmp_path_factory.mktemp("record") / "trust-files.json"
    before = (repo / "docs/trust-baseline.json").read_text()
    assert run(repo, "--files", str(record)) == 0
    files = json.loads(record.read_text())
    assert files["files"]["VE/Demo.lean"]["C"] == 3 and files["budget"] == {"K": 0, "S": 0, "V": 0}
    assert trust_map.files_problems(files) == []  # what the gate record keeps (tools/gate.py, read_trust)
    assert (repo / "docs/trust-baseline.json").read_text() == before


def test_a_work_tree_without_a_base_fails_closed(repo, capsys):
    git(repo, "branch", "-m", "main", "trunk")
    assert run(repo, "--check") == 1
    assert "no merge base of HEAD and `main`" in capsys.readouterr().err
    assert run(repo, "--since", "trunk") == 0


FIELDS = {"class": "V", "lines": 4, "reason": "r", "signature": "DRI", "commit": "a" * 40}


@pytest.mark.parametrize("field", [*FIELDS, None])
@pytest.mark.parametrize("value", [7, True, None, [], {}, "", " ", -1, 0, 1.5, "x" * 3])
def test_every_allowance_field_is_typed(field, value):
    entry = dict(FIELDS) if field is None else {**FIELDS, field: value}
    if field is None:
        entry["extra"] = value
    good = field is not None and (field == "reason" and value == "x" * 3 or field == "lines" and value == 7)
    _, problems = trust_map.parse_baseline({"budget": {"K": 0, "S": 0, "V": 0}, "allowances": [entry]})
    assert bool(problems) != good, (field, value, problems)
    _, missing = trust_map.parse_baseline({"budget": {"K": 0, "S": 0, "V": 0},
                                           "allowances": [{k: v for k, v in FIELDS.items() if k != field}]})
    assert bool(missing) == (field is not None)


@pytest.mark.parametrize("budget", [{"K": 0, "S": 0}, {"K": 0, "S": 0, "V": -1}, {"K": 0, "S": 0, "V": True},
                                    {"K": 0, "S": 0, "V": "1"}, {"K": 0, "S": 0, "V": 0, "D": 0}, [], None])
def test_the_budget_is_typed(budget):
    assert trust_map.parse_baseline({"budget": budget, "allowances": []})[1]


@pytest.mark.parametrize("data", [{"budget": {"K": 0, "S": 0, "V": 0}}, {"allowances": []}, [],
                                  {"budget": {"K": 0, "S": 0, "V": 0}, "allowances": [], "files": {}},
                                  {"budget": {"K": 0, "S": 0, "V": 0}, "allowances": {}}])
def test_the_file_holds_only_the_budget_and_allowances(data):
    assert trust_map.parse_baseline(data)[1]


def test_history_becomes_allowances():
    """The baseline before AR-4: a signed `allow` keeps its signature, a rebaseline's growth is
    unsigned, a fall is no allowance, and an entry recorded twice is one allowance."""
    signed = {"change": "signed", "signed": "DRI", "allow": {"S": 5}, "rebaselined_from": {"K": 0, "S": 0, "V": 0}}
    old = {"totals": {**trust_map.empty_counts(), "S": 5, "trusted": 5}, "history": [
        signed, {**signed, "rebaselined_from": {"K": 1, "S": 1, "V": 1}},
        {"change": "moved", "rebaselined_from": {"K": 2, "S": 5, "V": 9}, "to": {"K": 3, "S": 5, "V": 1}}]}
    assert trust_map.from_history(old) == [
        {"class": "S", "lines": 5, "reason": "signed", "signature": "DRI"},
        {"class": "K", "lines": 1, "reason": "moved", "signature": trust_map.UNSIGNED}]
    parsed, problems = trust_map.parse_baseline(old, legacy=True)
    assert problems == [] and parsed["budget"] == {"K": 0, "S": 5, "V": 0}
    assert trust_map.parse_baseline(old)[1]  # only a base's file may be in the old format
    for broken in ({"history": old["history"]}, {**old, "history": [{"allow": {"S": 5}}]}, {**old, "totals": []}):
        assert trust_map.parse_baseline(broken, legacy=True)[1], broken  # fails closed, never raises
    head = [{**a, "commit": "b" * 40} for a in trust_map.from_history(old)]
    assert trust_map.introduced(head, parsed["allowances"]) == []


def test_committed_budget_passes_its_check(tmp_path):
    """The committed file is in the AR-4 format and the tree is within its base and the allowances
    introduced since (the base is the merge base with `main`, or the first parent on main's tip).
    The tree's per-file counts are what the gate record accepts."""
    data = json.loads(trust_map.BASELINE.read_text())
    assert trust_map.parse_baseline(data)[1] == []
    assert list(data) == ["comment", "budget", "allowances"]
    assert trust_map.main(["--check", "--files", str(tmp_path / "trust-files.json")]) == 0
    assert trust_map.files_problems(json.loads((tmp_path / "trust-files.json").read_text())) == []
