"""The provenance block on every answer (ve/provenance.py; row answer-provenance-block, orchestrator ruling 2026-11-27
19:24Z item 2 of the demo sceptic code items).

Before: no answer said which text, translation, program version or checker it came from, or who translated, checked
and signed off its text (tour stop 7 printed "no" and nothing else). Now `ve ask --json` carries a `provenance` member
on every answer (both routes), the staged route prints the block after every answer it prints, `ve ask --provenance`
prints it after a ve-document's answer and usecases/eligibility/ask.py after its answers. Every test here fails on the
old code (no ve.provenance module, no block in any output). The role lines say what is true today and nothing more:
translated by an AI (Opus 5.5), checked by an AI of the same family, signed off by nobody; a value that cannot be
computed is "unknown". The per-text facts are in ve/provenance_records.json; usecases/eligibility/ask.py prints
the block after its answers.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from subprocesses import HANG_TIMEOUT
from test_ask_staged import ask, cli, staged

ROOT = Path(__file__).resolve().parents[1]
TODAY = {"translated_by": "AI (Opus 5.5)", "checked_by": "AI, same family", "signed_off_by": "nobody"}
LABELS = ("Source", "Translation", "Translation frozen at commit", "VE commit", "Checker (Lean build)", "Date",
          "Translated by", "Checked by", "Signed off by")
ENV_ALLOW = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "PYTHONPATH", "PYTHONNOUSERSITE", "PYTHONPYCACHEPREFIX")
GIT = ["git", "-c", "user.name=test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()


def block_of(out: str) -> list[str]:
    lines = out.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("Provenance of "))
    return lines[start:]


def labelled(lines: list[str]) -> dict:
    """label -> values (a label may repeat: one Source or Translation line per file)."""
    out: dict = {}
    for line in lines[1:]:
        label, _, value = line.strip().partition(": ")
        out.setdefault(label, []).append(value)
    return out


def test_a_staged_answer_prints_its_block_after_it(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "Has Ada taken the minimum time off the policy expects for 2026?", "--case", "C001") == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert lines[0] == "no" and lines[1] == "Provenance of this answer:"
    got = labelled(lines[1:])
    assert tuple(got) == LABELS[:2] + ("Also read",) + LABELS[2:], got
    # the runner and case files the answer also depends on, each with its real hash
    assert got.pop("Also read") == [f"policy/{n} sha256 {sha(d / n)}" for n in ("run.py", "questions-enc.jsonl")]
    assert all(len(v) == 1 for v in got.values()), got
    # the translation's hash is the file's real SHA-256; the text is in no checkout and no record: unknown
    assert got["Translation"] == [f"policy/translation.py sha256 {sha(d / 'translation.py')}"]
    assert got["Source"] == ["unknown"] and got["Translation frozen at commit"] == ["unknown; changed since: unknown"]
    assert [got[k][0] for k in ("Translated by", "Checked by", "Signed off by")] == ["unknown"] * 3
    assert got["VE commit"][0].startswith(head() + "; tracked files changed since: ")
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", got["Date"][0])
    checker = ROOT / "lean/.lake/build/bin/ve_service"
    if checker.is_file() and not os.environ.get("VE_LEAN_SERVICE"):
        assert got["Checker (Lean build)"] == [f"lean/.lake/build/bin/ve_service sha256 {sha(checker)}"]


def test_a_staged_json_answer_carries_the_block(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask("--json", d, "How many days off a year does the policy expect Ada to take at least?") == 0
    block = json.loads(capsys.readouterr().out)["provenance"]
    assert set(block) == {"source", "translation", "also_read", "ve_commit", "ve_tree_changed", "checker", "date",
                          *TODAY}
    assert block["also_read"] == [{"file": f"policy/{n}", "sha256": sha(d / n)} for n in ("run.py", "questions-enc.jsonl")]
    assert block["translation"] == {"files": [{"file": "policy/translation.py", "sha256": sha(d / "translation.py")}],
                                    "freeze_commit": "unknown", "changed_since_freeze": "unknown"}
    assert block["ve_commit"] == head() and block["source"] == "unknown"
    assert {k: block[k] for k in TODAY} == {k: "unknown" for k in TODAY}


def test_a_refusal_carries_no_block(tmp_path, capsys):
    d = staged(tmp_path)
    assert ask(d, "May Ada book it?", "--case", "C001") == 3
    out = capsys.readouterr()
    assert "Provenance" not in out.out + out.err
    assert ask("--json", d, "May Ada book it?", "--case", "C001") == 3
    assert "provenance" not in json.loads(capsys.readouterr().out)
    done = cli(d, "Has Ada taken the minimum time off the policy expects for 2026?", "--case", "C001", "--provenance")
    assert done.returncode == 0 and done.stdout.count("Provenance of this answer:") == 1, done.stderr


def test_the_records_role_lines_are_todays_and_name_no_person_or_other_family():
    from ve.provenance import RECORDS, records
    listed = records()
    assert set(listed) == {"tour/texts/club.ve.md", "usecases/eligibility", "usecases/gitlab_relocation"}, RECORDS
    for key, record in listed.items():
        assert record["roles"] == TODAY, key


@pytest.mark.parametrize("text", ["tour/texts/club.ve.md", "usecases/eligibility"])
def test_a_listed_text_prints_its_records_roles_and_its_files_real_hashes(text):
    from ve import provenance
    block = provenance.block(ROOT / text, root=provenance.ROOT)
    assert {k: block[k] for k in TODAY} == TODAY
    record = provenance.records()[text]
    assert block["translation"]["files"] == [{"file": f, "sha256": sha(ROOT / f)} for f in record["translation"]]
    if type(record["source"]) is str:
        assert block["source"] == record["source"]
    else:
        assert block["source"] == [{"file": s["file"], "sha256": sha(ROOT / s["file"])} for s in record["source"]]
    lines = provenance.lines(block)
    assert lines[-3:] == ["  Translated by: AI (Opus 5.5)", "  Checked by: AI, same family", "  Signed off by: nobody"]


def ve_repo(repo: Path, *, ve=True) -> Path:
    """A committed git repository with a staged-style text `policy/` (and, with `ve`, the marks of a VE checkout)."""
    (repo / "policy").mkdir(parents=True)
    (repo / "policy/translation.py").write_text("RULES = 1\n")
    (repo / "policy/run.py").write_text("RUN = 1\n")
    (repo / "policy/source.txt").write_text("The policy.\n")
    if ve:
        (repo / "ve").mkdir()
        (repo / "ve/__init__.py").write_text("")
        (repo / "lean").mkdir()
        (repo / "lean/lakefile.toml").write_text("")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*GIT, "-C", str(repo), "add", "."], check=True)
    subprocess.run([*GIT, "-C", str(repo), "commit", "-qm", "freeze"], check=True)
    return repo


def test_the_freeze_commit_and_a_recorded_source_hash(tmp_path, monkeypatch):
    monkeypatch.delenv("VE_LEAN_SERVICE", raising=False)
    from ve import provenance
    repo = ve_repo(tmp_path / "repo")
    frozen = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True,
                            check=True).stdout.strip()
    record = {"source": [{"file": "policy/source.txt"}, {"file": "elsewhere/original.txt", "sha256": "ab" * 32,
                                                          "kept": "in the working records"},
                         {"file": "elsewhere/lost.txt"}],
              "translation": ["policy/translation.py"], "freeze_commit": frozen, "roles": dict(TODAY),
              "translation_sha256": {"policy/translation.py": sha(repo / "policy/translation.py")}}
    file = tmp_path / "records.json"
    file.write_text(json.dumps({"texts": {"policy": record}}))
    when = datetime.datetime(2026, 11, 28, 3, 4, 5, tzinfo=datetime.timezone.utc)
    block = provenance.block(repo / "policy", record_file=file, now=when)
    assert block["source"] == [{"file": "policy/source.txt", "sha256": sha(repo / "policy/source.txt")},
                               {"file": "elsewhere/original.txt", "sha256": "ab" * 32,
                                "recorded": "in the working records"},
                               {"file": "elsewhere/lost.txt", "sha256": "unknown"}]
    assert block["translation"]["freeze_commit"] == frozen and block["translation"]["changed_since_freeze"] == "no"
    assert (block["ve_commit"], block["ve_tree_changed"], block["date"]) == (frozen, "no", "2026-11-28T03:04:05Z")
    assert block["checker"] == "unknown"  # the checkout has no Lean build
    assert "  Source: elsewhere/original.txt sha256 " + "ab" * 32 + " (recorded; in the working records)" in \
        provenance.lines(block)
    assert {k: block[k] for k in TODAY} == TODAY
    (repo / "policy/translation.py").write_text("RULES = 2\n")
    changed = provenance.block(repo / "policy", record_file=file)
    assert (changed["translation"]["changed_since_freeze"], changed["ve_tree_changed"]) == ("yes", "yes")
    # a changed translation is not the one that was translated and checked: its role lines are unknown (review B3)
    assert all(changed[k].startswith("unknown (the translation is not the one its record names)") for k in TODAY)
    file.write_text(json.dumps({"texts": {"policy": {**record, "freeze_commit": "0" * 40}}}))
    assert provenance.block(repo / "policy", record_file=file)["translation"]["changed_since_freeze"] == "unknown"
    assert provenance.block(repo / "policy", lean=False)["checker"] == "not run"


def test_outside_any_checkout_what_cannot_be_computed_is_unknown(tmp_path):
    from ve import provenance
    text = tmp_path / "own.ve.md"
    text.write_text("x")
    block = provenance.block(text, root=tmp_path)
    assert block["translation"]["files"] == [{"file": "own.ve.md", "sha256": sha(text)}]
    assert {k: block[k] for k in ("source", "ve_commit", "ve_tree_changed", "checker", *TODAY)} == {
        k: "unknown" for k in ("source", "ve_commit", "ve_tree_changed", "checker", *TODAY)}


def _ve(*args, cwd=ROOT):
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    return subprocess.run([sys.executable, "-m", "ve", *map(str, args)], cwd=cwd, env=env, text=True,
                          capture_output=True, timeout=HANG_TIMEOUT)


def test_ve_ask_on_a_document_carries_the_block_in_json_and_with_provenance():
    """Lean answers (the tour's stop 1); the JSON carries the block, the text prints it only with --provenance."""
    club = ROOT / "tour/texts/club.ve.md"
    plain = _ve("ask", club, "Is Ann eligible?")
    assert plain.returncode == 0 and "Provenance" not in plain.stdout, plain.stderr
    shown = _ve("ask", club, "Is Ann eligible?", "--provenance")
    assert shown.returncode == 0 and shown.stdout.startswith(plain.stdout), shown.stderr
    got = labelled(block_of(shown.stdout))
    assert got["Translation"] == [f"tour/texts/club.ve.md sha256 {sha(club)}"]
    assert [got[label][0] for label in LABELS[-3:]] == list(TODAY.values())
    record = json.loads(_ve("ask", club, "Is Ann eligible?", "--json").stdout)
    block = record["provenance"]
    assert record["proof"] == "lean_checked" and {k: block[k] for k in TODAY} == TODAY
    assert block["ve_commit"] == head() and block["source"].startswith("none: written for the tour")
    reading = json.loads(_ve("ask", club, "Is Ann eligible?", "--reading", "--json").stdout)
    assert "provenance" not in reading


def test_the_eligibility_checker_prints_the_block_after_its_answers():
    env = {k: v for k, v in os.environ.items() if k in ENV_ALLOW or k.startswith("VE_")}
    done = subprocess.run([sys.executable, "usecases/eligibility/ask.py", "usecases/eligibility/demo/b15.json",
                           "--no-lean"], cwd=ROOT, env=env, text=True, capture_output=True, timeout=HANG_TIMEOUT)
    assert done.returncode == 0, done.stderr
    lines = block_of(done.stdout)
    assert lines[0] == "Provenance of these answers:" and done.stdout.endswith(lines[-1] + "\n")
    got = labelled(lines)
    assert got["Source"][0] == ("usecases/eligibility/source/uksi-2025-969-made.txt sha256 "
                                + sha(ROOT / "usecases/eligibility/source/uksi-2025-969-made.txt"))
    assert got["Checker (Lean build)"] == ["not run"]  # --no-lean: no Lean build checked these answers
    assert [got[label][0] for label in LABELS[-3:]] == list(TODAY.values())


def test_ve_provenance_prints_the_block_of_the_checkout_that_holds_the_text(tmp_path):
    done = _ve("provenance", "tour/texts/club.ve.md")
    assert done.returncode == 0, done.stderr
    got = labelled(block_of(done.stdout))
    assert tuple(got) == LABELS and got["VE commit"][0].startswith(head() + ";")
    assert json.loads(_ve("provenance", "tour/texts/club.ve.md", "--json").stdout)["provenance"]["signed_off_by"] \
        == "nobody"
    assert _ve("provenance", tmp_path / "missing").returncode == 2


def test_another_repository_holding_a_text_is_not_the_code_that_answered(tmp_path, monkeypatch):
    """Review A2: `ve provenance` on a text in a plain repository printed that repository's HEAD as the VE commit."""
    from ve import provenance
    monkeypatch.delenv("VE_LEAN_SERVICE", raising=False)
    repo = ve_repo(tmp_path / "plain", ve=False)
    block = provenance.block(repo / "policy")
    assert (block["ve_commit"], block["ve_tree_changed"], block["checker"]) == ("unknown",) * 3
    assert block["also_read"] == [{"file": "policy/run.py", "sha256": sha(repo / "policy/run.py")}]  # review B6
    assert "  Also read: policy/run.py sha256 " + sha(repo / "policy/run.py") in provenance.lines(block)
    # review B8: a root inside a checkout but not its top (an installed copy of ve) has no commit or build of its own
    inner = repo / "policy"
    assert provenance.block(repo / "policy", root=inner)["ve_commit"] == "unknown"
    assert provenance.block(repo / "policy", root=inner)["checker"] == "unknown"
    done = _ve("provenance", repo / "policy")
    assert done.returncode == 0 and "  VE commit: unknown; tracked files changed since: unknown" in done.stdout


def test_the_checker_line_is_the_lean_build_and_its_real_hash(tmp_path, monkeypatch):
    """Review B5, B7: the checker line, with a build in the checkout, with VE_LEAN_SERVICE, without a build."""
    from ve import provenance
    monkeypatch.delenv("VE_LEAN_SERVICE", raising=False)
    repo = ve_repo(tmp_path / "ve")
    assert provenance.block(repo / "policy")["checker"] == "unknown"  # no Lean build in the checkout
    build = repo / "lean/.lake/build/bin/ve_service"
    build.parent.mkdir(parents=True)
    build.write_bytes(b"a Lean build")
    assert provenance.block(repo / "policy")["checker"] == {"file": "lean/.lake/build/bin/ve_service",
                                                            "sha256": sha(build)}
    service = tmp_path / "service"
    service.write_bytes(b"another build")
    monkeypatch.setenv("VE_LEAN_SERVICE", str(service))
    for root in (repo, provenance.ROOT):  # the executable both checkouts' Lean clients start
        assert provenance.block(repo / "policy", root=root)["checker"] == {"file": str(service),
                                                                           "sha256": sha(service)}
    assert provenance.block(repo / "policy", lean=False)["checker"] == "not run"
    assert "  Checker (Lean build): not run" in provenance.lines(provenance.block(repo / "policy", lean=False))


def test_the_tour_test_masks_only_the_values_that_vary():
    """Review B4: a block line that turns unknown or not run is drift; a new commit, date or build is not."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("tour_make_expected_p", ROOT / "tour/make_expected.py")
    make_expected = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(make_expected)
    a = ("  VE commit: " + "a" * 40 + "; tracked files changed since: no\n  Date: 2026-11-28T02:49:30Z\n"
         "  Checker (Lean build): lean/x sha256 " + "b" * 64 + "\n")
    b = ("  VE commit: " + "c" * 40 + "; tracked files changed since: yes\n  Date: 2026-12-01T00:00:00Z\n"
         "  Checker (Lean build): lean/x sha256 " + "d" * 64 + "\n")
    assert make_expected.comparable(a) == make_expected.comparable(b)
    for drift in ("  VE commit: unknown; tracked files changed since: unknown\n", "  Checker (Lean build): unknown\n",
                  "  Checker (Lean build): not run\n", "  Date: unknown\n"):
        line = drift.split(":")[0]
        changed = "".join(drift if x.startswith(line + ":") else x for x in a.splitlines(keepends=True))
        assert make_expected.comparable(changed) != make_expected.comparable(a), drift
