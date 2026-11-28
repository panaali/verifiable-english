"""The newcomer tour (tour/README.md): every stop's output, the page, and the tour's texts stay as recorded.

tour/expected/<stop>.txt is written by tour/make_expected.py from a real run of tour/stops/<stop>.sh. This test runs
each stop again (with this test's Python in place of `uv run --frozen python`, through VE_TOUR_PYTHON) and fails when
its output differs, and fails when the page's output blocks differ from those files. The stops that use branch
after-release (tour/make_expected.py AFTER_RELEASE) need its checkout in .tour-after-release/ (sh tour/install.sh).
Without that checkout, the test exercises the install diagnostic and verifies the pinned source tree instead.
"""
from __future__ import annotations

import gzip
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOUR = ROOT / "tour"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Every file of the tour, by path, so test selection (tools/select_tests.py) reaches each one from this test.
TOUR_FILES = (
    "tour/README.md", "tour/TEXTS.md", "tour/NEWCOMER-QUESTIONS.md", "tour/install.sh", "tour/measure.sh",
    "tour/make_expected.py", "tour/texts/build_texts.py", "tour/texts/club.ve.md", "tour/texts/own-rules.txt",
    "tour/texts/own-rules-new-word.txt", "tour/texts/own-rules-new-word-fixed.txt",
    "tour/data/relocation-R009-sealed.jsonl", "tour/data/reader-runs.json",
    "tour/data/reader-prompt.txt", "tour/stops/common.sh",
    "tour/stops/dates.py", "tour/stops/sums.py", "tour/stops/planted.py", "tour/stops/not_yet.py",
    "tour/expected/seconds.json", "tour/prebuilt.py", "tour/prebuilt.json", "tour/AFTER_RELEASE_COMMIT",
    ".github/workflows/tour-prebuilt.yml",
    "tour/newcomer/README.md", "tour/newcomer/SCORES.md", "tour/newcomer/render.py", "tour/newcomer/run1.md",
    "tour/newcomer/run2.md", "tour/newcomer/run3.md",
)
make_expected = _load("tour_make_expected", TOUR / "make_expected.py")
build_texts = _load("tour_build_texts", TOUR / "texts" / "build_texts.py")
prebuilt = _load("tour_prebuilt", TOUR / "prebuilt.py")
PIN = (TOUR / "AFTER_RELEASE_COMMIT").read_text(encoding="utf-8").strip()
SIDE = ROOT / ".tour-after-release"
AFTER_RELEASE_SOURCES = {
    "04-date": "ve/surface/dates.py",
    "05-sum": "ve/surface/sums.py",
    "07-company-policy": "usecases/gitlab_relocation/translation.py",
    "09-planted-mistake": "usecases/gitlab_relocation/translation.py",
    "10-not-yet": "ve/surface/time.py",
}


def test_every_stop_has_a_script_an_expected_output_and_a_block_on_the_page():
    blocks = make_expected.page_blocks((TOUR / "README.md").read_text(encoding="utf-8"))
    assert list(blocks) == list(make_expected.STOPS)
    for stop in make_expected.STOPS:
        assert (TOUR / "stops" / f"{stop}.sh").is_file(), stop
        assert (TOUR / "expected" / f"{stop}.txt").is_file(), stop


@pytest.mark.parametrize("stop", make_expected.STOPS)
def test_the_page_shows_the_recorded_output(stop):
    recorded = (TOUR / "expected" / f"{stop}.txt").read_text(encoding="utf-8")
    page = make_expected.page_blocks((TOUR / "README.md").read_text(encoding="utf-8"))
    assert page[stop] == make_expected.shown(stop, recorded)


# The project's own words, which a newcomer would not know; checked as whole words in every text file of the tour
# (code names joined by "_" are not whole words), except the data files that quote other material verbatim.
PROJECT_WORDS = ("certificate", "certificates", "mutant", "mutants", "w6", "seat", "seats", "codename", "orchestrator",
                 "dri", "decider", "delegate", "sprint", "codex", "chain", "batch", "pilot", "sweep")
QUOTED = {"tour/data/relocation-R009-sealed.jsonl", "tour/data/reader-runs.json", "tour/data/reader-prompt.txt",
          "tour/prebuilt.json"}
# planted.py quotes the lines of the translation it edits (its PLANT, CUT and LIST_USE), which name the translation's own list of
# test mistakes: those words are allowed there only
ALLOWED_WORDS = {"tour/stops/planted.py": {"mutant", "mutants"}}


def test_the_tour_has_no_project_words():
    words = re.compile(r"(?<![\w-])(" + "|".join(PROJECT_WORDS) + r")(?![\w-])", re.I)
    hits = []
    for rel in sorted(set(TOUR_FILES) - QUOTED) + [f"tour/stops/{s}.sh" for s in make_expected.STOPS] + [
            f"tour/expected/{s}.txt" for s in make_expected.STOPS]:
        text = (ROOT / rel).read_text(encoding="utf-8")
        hits.extend(f"{rel}: {m.group(0)}" for m in words.finditer(text)
                    if m.group(0).lower() not in ALLOWED_WORDS.get(rel, ()))
    assert hits == []


def test_the_tour_texts_are_built_from_their_sentences():
    for name, text in build_texts.documents().items():
        assert (TOUR / "texts" / name).read_text(encoding="utf-8") == text, name


def _require_pin(pin=PIN):
    """Every read of the pinned tree goes through here first. The pin is on branch after-release, which the GitHub
    Actions export does not carry: there only (GITHUB_ACTIONS=true) a missing pin skips; anywhere else it fails."""
    repo = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=ROOT, capture_output=True, text=True)
    if repo.returncode != 0:
        pytest.fail(f"the tour test needs a git checkout: {repo.stderr.strip()}")
    present = subprocess.run(["git", "cat-file", "-e", f"{pin}^{{commit}}"], cwd=ROOT,
                             capture_output=True).returncode == 0
    if present:
        return
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pytest.skip(f"tour pin {pin} is not in the Actions export (branch after-release is not exported)")
    pytest.fail(f"tour pin {pin} missing from this checkout")


def _outcome(pin):
    try:
        _require_pin(pin)
    except pytest.skip.Exception as e:
        return "skip", str(e)
    except pytest.fail.Exception as e:
        return "fail", str(e)
    return "pass", ""


def test_a_missing_pin_fails_outside_actions(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert _outcome("0" * 40) == ("fail", f"tour pin {'0' * 40} missing from this checkout")
    for value in ("1", "True", "false", ""):  # only the exact value GitHub sets skips
        monkeypatch.setenv("GITHUB_ACTIONS", value)
        assert _outcome("0" * 40)[0] == "fail", value


def test_a_missing_pin_skips_only_on_actions(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    kind, reason = _outcome("0" * 40)
    assert kind == "skip" and f"tour pin {'0' * 40} is not in the Actions export" in reason


def test_the_gate_passes_the_actions_signal_and_allows_only_this_skip(monkeypatch):
    """tools/gate.py builds its pytest environment from a list: GITHUB_ACTIONS reaches the tests only as "true",
    and the skip policy (tools/gate-optional.json) admits the pin skip for the stop tests only, by its reason."""
    from tools import gate
    assert "GITHUB_ACTIONS" in gate.STAGE_ENVIRONMENT["pytest"] and "GITHUB_ACTIONS" not in gate.ALLOWED_ENVIRONMENT
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    assert gate.actions_signal() == {"GITHUB_ACTIONS": "true"}
    for value in ("1", "false"):
        monkeypatch.setenv("GITHUB_ACTIONS", value)
        assert gate.actions_signal() == {}
    monkeypatch.delenv("GITHUB_ACTIONS")
    assert gate.actions_signal() == {}
    policy = json.loads((ROOT / "tools" / "gate-optional.json").read_text(encoding="utf-8"))["optional_tests"]
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    _, reason = _outcome("0" * 40)
    assert gate.permitted("tests/test_tour.py::test_each_stop_prints_its_recorded_output[04-date]", reason, policy)
    assert not gate.permitted("tests/test_tour.py::test_the_after_release_checkout_is_the_pinned_commit", reason, policy)
    assert not gate.permitted("tests/test_tour.py::test_each_stop_prints_its_recorded_output[04-date]",
                              "Skipped: something else", policy)


@pytest.mark.parametrize("stop", make_expected.STOPS)
def test_each_stop_prints_its_recorded_output(stop):
    if stop in make_expected.AFTER_RELEASE and not SIDE.is_dir():
        # The clean gate has no second checkout. Check the exact source that the recorded stop used and the useful
        # error the stop prints until install is run; a local installed tour still reruns the full recorded output.
        record = prebuilt.manifest()["sides"]["after-release"]
        assert record["commit"] == PIN
        _require_pin()
        for sub in ("lean", "rust"):
            got = subprocess.run(["git", "rev-parse", f"{PIN}:{sub}"], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.strip()
            assert got == record[f"{sub}_tree"]
        subprocess.run(["git", "cat-file", "-e", f"{PIN}:{AFTER_RELEASE_SOURCES[stop]}"], cwd=ROOT, check=True)
        output, _ = make_expected.run_stop(stop, env={**os.environ, "VE_TOUR_PYTHON": sys.executable})
        assert output == ("This stop needs the after-release checkout: run sh tour/install.sh first.\n"
                          "[the stop script itself exited with code 1]\n")
        return
    output, _ = make_expected.run_stop(stop, env={**os.environ, "VE_TOUR_PYTHON": sys.executable})
    assert output == (TOUR / "expected" / f"{stop}.txt").read_text(encoding="utf-8")


def test_every_tour_file_is_listed_and_present():
    on_disk = {str(p.relative_to(ROOT)) for p in TOUR.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    on_disk.add(".github/workflows/tour-prebuilt.yml")
    listed = set(TOUR_FILES) | {f"tour/stops/{s}.sh" for s in make_expected.STOPS} | {
        f"tour/expected/{s}.txt" for s in make_expected.STOPS}
    assert on_disk == listed


def test_the_texts_list_and_the_newcomer_questions():
    texts = (ROOT / "tour/TEXTS.md").read_text(encoding="utf-8")
    for path in ("tour/texts/club.ve.md", "usecases/question-answering/udhr-part07.ve.md", "usecases/eligibility/",
                 "usecases/gitlab_relocation/", "tour/texts/own-rules.txt", "tour/texts/own-rules-new-word.txt",
                 "tour/texts/own-rules-new-word-fixed.txt"):
        assert path in texts, path
    questions = (ROOT / "tour/NEWCOMER-QUESTIONS.md").read_text(encoding="utf-8")
    assert [line[:2] for line in questions.splitlines() if line[:2] in ("1.", "2.", "3.", "4.", "5.")] == [
        "1.", "2.", "3.", "4.", "5."] * 2  # the five questions, then their grading key
    import json
    rows = [json.loads(line) for line in open(ROOT / "tour/data/relocation-R009-sealed.jsonl", encoding="utf-8")]
    assert [(r["qid"], r["answer"]) for r in rows] == [("R009-1", "no"), ("R009-2", "no")]


# --- review findings of the merge round (tour revision 1126) ----------------------------------------------------------

def test_the_policy_stops_ask_only_case_R009():
    """Only case R009's answers were made public (tour/data/relocation-R009-sealed.jsonl); no stop asks another case."""
    for stop in make_expected.STOPS:
        script = (TOUR / "stops" / f"{stop}.sh").read_text(encoding="utf-8")
        assert set(re.findall(r"--case (\S+)", script)) <= {"R009"}, stop
        assert not set(re.findall(r"\bR0\d\d\b", (TOUR / "expected" / f"{stop}.txt").read_text())) - {"R009"}, stop
    assert re.findall(r'CASE = "(R\d+)"', (TOUR / "stops" / "planted.py").read_text()) == ["R009"]


def test_the_write_your_own_stop_shows_a_refusal_and_the_sense_notice():
    """Stop 12 comes after the longer example and reads plain texts with `ve read` on main. Its recorded output (a real
    run) shows a text read with the notice that a word has more than one sense; a text refused with the line that fixes
    it; and that text, with exactly that line added, read and answered. The page says in one sentence that one word is
    one meaning within a text."""
    stop = "12-write-your-own"
    assert make_expected.STOPS[-2:] == ("11-longer-example", stop)
    assert stop not in make_expected.AFTER_RELEASE
    texts = ["tour/texts/own-rules.txt", "tour/texts/own-rules-new-word.txt", "tour/texts/own-rules-new-word-fixed.txt"]
    script = (TOUR / "stops" / f"{stop}.sh").read_text(encoding="utf-8")
    assert re.findall(r"-m ve read (\S+)", script) == texts
    recorded = (TOUR / "expected" / f"{stop}.txt").read_text(encoding="utf-8")
    runs = re.split(r"^\$ uv run --frozen python -m ve read \S+\n", recorded, flags=re.M)
    assert len(runs) == 4 and runs[0] == ""
    read, refused, fixed = runs[1:]
    assert "Lean read every sentence: 5 of 5 CHECKED" in read and "\n  Yes.\n" in read
    assert "senses in the list: this text reads it with ONE meaning throughout" in read
    assert refused.startswith("Not read: 1 problem; nothing is answered.\n") and refused.endswith("[exit code 2]\n")
    offered = re.findall(r"^  Fix \(add this line\): (.*)$", refused, flags=re.M)
    assert offered == ["Words: overlimit (property of member)"]
    as_refused = (ROOT / texts[1]).read_text(encoding="utf-8")
    assert (ROOT / texts[2]).read_text(encoding="utf-8") == offered[0] + "\n" + as_refused
    assert "overlimit: a property of members (declared in the text, line 1)" in fixed
    assert "Lean read every sentence: 4 of 4 CHECKED" in fixed and "\n  No. " in fixed and "[exit code" not in fixed
    page = (TOUR / "README.md").read_text(encoding="utf-8")
    sentence = "one word is one meaning within a text; a word used in two meanings will give a wrong answer."
    assert sentence in " ".join(page.split())
    assert page.index("<!-- output 11-longer-example -->") < page.index(f"<!-- output {stop} -->")


def test_the_write_your_own_stop_answers_plainly_and_states_its_assumption(monkeypatch):
    """Word senses v1 (ruling amendment 2026-11-27T19:47Z): with no AI reader, stop 12's first text gets main's plain
    "Yes." with its sentences, then the one line stating the assumption, and its exit code 0; the fixed text the same
    with its "No.". No stop shows the reader's first-run offer (the stops set VE_READER_OFFER=off), and the recording
    uses none of this machine's reader settings (no VE_WORD_READER; VE_SETTINGS_DIR an empty directory)."""
    stop = "12-write-your-own"
    recorded = (TOUR / "expected" / f"{stop}.txt").read_text(encoding="utf-8")
    read, refused, fixed = re.split(r"^\$ uv run --frozen python -m ve read \S+\n", recorded, flags=re.M)[1:]
    assumption = "Reading each word with one meaning throughout."
    assert read.endswith('  Sentence 5 says: "Ann is not suspended."\n' + assumption + "\n")
    assert read.split("Question (line 7): Is Ann allowed?\n")[1].startswith("  You asked whether Ann is allowed.\n  Yes.\n")
    assert "Depends" not in recorded and "may mean different things" not in recorded and "[exit code 3]" not in recorded
    assert fixed.endswith(assumption + "\n") and assumption not in refused
    assert "First run:" not in recorded and "--reader-yes" not in recorded
    assert "\nexport VE_READER_OFFER=off\n" in (TOUR / "stops" / "common.sh").read_text(encoding="utf-8")
    seen = {}
    real = make_expected.subprocess.run

    def run(*args, **kwargs):
        seen.update(kwargs["env"])
        seen["settings files"] = sorted(p.name for p in Path(kwargs["env"]["VE_SETTINGS_DIR"]).iterdir())
        return real(["true"], **{k: v for k, v in kwargs.items() if k in ("stdout", "stderr", "text")})
    monkeypatch.setattr(make_expected.subprocess, "run", run)
    make_expected.run_stop(stop, env={"PATH": os.environ.get("PATH", ""), "VE_WORD_READER": "a-reader-program"})
    assert seen["VE_READER_OFFER"] == "off" and "VE_WORD_READER" not in seen and seen["settings files"] == []


def test_the_after_release_checkout_is_the_pinned_commit():
    """The after-release stops were recorded at tour/AFTER_RELEASE_COMMIT: a checkout at another commit fails here
    instead of drifting (the install checks out the pin); the prebuilt programs were built at the same commit."""
    assert re.fullmatch(r"[0-9a-f]{40}", PIN)
    assert prebuilt.manifest()["sides"]["after-release"]["commit"] == PIN
    assert PIN in (TOUR / "install.sh").read_text() or "AFTER_RELEASE_COMMIT" in (TOUR / "install.sh").read_text()
    if SIDE.is_dir():
        head = subprocess.run(["git", "-C", str(SIDE), "rev-parse", "HEAD"], capture_output=True, text=True).stdout
        assert head.strip() == PIN, "the after-release checkout is not at the pinned commit: run sh tour/install.sh"


def test_the_checker_excerpt_is_chosen_by_content():
    """The page shows stop 6's start, its assumptions and one "Lean check:" line per answer; its line count is right."""
    recorded = (TOUR / "expected" / "06-checker.txt").read_text(encoding="utf-8")
    shown = make_expected.shown("06-checker", recorded)
    assert [line for line in shown.splitlines() if line.startswith("Lean check:")] == [
        line for line in recorded.splitlines() if line.startswith("Lean check:")]
    assert len([line for line in shown.splitlines() if line.startswith("Lean check:")]) == 4
    assert make_expected.ASSUMPTIONS in shown
    page = (TOUR / "README.md").read_text(encoding="utf-8")
    assert f"({len(recorded.splitlines())} lines: it quotes every clause)" in page


def test_stop_3_is_at_most_six_lines():
    assert len((TOUR / "expected" / "03-every-or-some.txt").read_text(encoding="utf-8").splitlines()) <= 6


def _reader():
    planted = _load("tour_planted", TOUR / "stops" / "planted.py")
    record = json.loads((TOUR / "data" / "reader-runs.json").read_text(encoding="utf-8"))
    return planted, record


# The sentence the tour states for stop 9 and its video scene (ruled 2026-11-27 23:39Z, on the like-for-like
# re-record: reviews/reader-like-for-like-20261127.md in the project's notes)
STOP_9_SENTENCE = ("With the same prompt and no mistake list, in five runs the reader noticed the day-count problem "
                   "every time and named the right rule in three (two at high confidence); on the unaltered translation "
                   "it raised the day-count problem in none of five.")
# a word in a day-count flag that says how the days are counted
DAY_COUNT = re.compile(r"one day|off by one|\+ ?1|elapsed|last day|first day|inclusive", re.I)


def test_stop_9_states_the_counts_of_the_pinned_runs():
    """Stop 9 states what five planted runs and five runs on the translation as written did, counted here from the
    pinned record (tour/data/reader-runs.json), not one recorded run: its sentence is worked out from those counts, and
    it changes when the record does."""
    planted, record = _reader()
    runs = {copy: [r for r in record["runs"] if r["copy"] == copy] for copy in ("planted", "as written")}
    assert [r["run"] for r in runs["planted"]] == [r["run"] for r in runs["as written"]] == [1, 2, 3, 4, 5]
    for r in record["runs"]:
        assert r["units_answered"] == 34 and all(f["source"] and f["translation"] and f["why"] for f in r["flags"])
        assert len(set(r["day_count_flags"])) == len(r["day_count_flags"])
        for i in r["day_count_flags"]:
            flag = r["flags"][i]
            assert DAY_COUNT.search(flag["why"] + " " + flag["translation"]), (r["copy"], r["run"], i)
        if r["right_rule_flag"] is not None:
            assert r["right_rule_flag"] in r["day_count_flags"]
            assert r["flags"][r["right_rule_flag"]]["unit"] == record["planted_unit"]
    # the unscored flags that the same words find, each read by hand: both are about a planned stay's first day
    # (part 15), not the day count, so a day-count flag left unscored shows up here
    assert {(r["copy"], r["run"], i) for r in record["runs"] for i, f in enumerate(r["flags"])
            if i not in r["day_count_flags"] and DAY_COUNT.search(f["why"] + " " + f["translation"])} == {
        ("planted", 1, 3), ("as written", 3, 1)}
    noticed = sum(bool(r["day_count_flags"]) for r in runs["planted"])
    right = [r["flags"][r["right_rule_flag"]] for r in runs["planted"] if r["right_rule_flag"] is not None]
    high = sum(f["confidence"] == "high" for f in right)
    written = sum(bool(r["day_count_flags"]) for r in runs["as written"])
    assert planted.counts(record) == {"planted": {"runs": 5, "day_count": noticed, "right_rule": len(right),
                                                  "right_rule_high": high},
                                      "as written": {"runs": 5, "day_count": written, "right_rule": 0,
                                                     "right_rule_high": 0}}
    stated = planted.sentence(planted.counts(record))
    assert stated == STOP_9_SENTENCE and (noticed, len(right), high, written) == (5, 3, 2, 0)
    recorded = (TOUR / "expected" / "09-planted-mistake.txt").read_text(encoding="utf-8")
    assert f"  {stated}" in recorded.splitlines()
    for line in planted.run_rows(record) + [planted.other_flags_line(record), planted.elsewhere_line(record)]:
        assert line in recorded.splitlines()
    assert STOP_9_SENTENCE in " ".join((TOUR / "README.md").read_text(encoding="utf-8").split())
    # planted run 1 (its rule flag at low confidence) no longer naming the rule, and one as-written run raising the
    # day count: the sentence follows the record
    changed = json.loads(json.dumps(record))
    first = next(r for r in changed["runs"] if r["copy"] == "planted" and r["right_rule_flag"] is not None)
    assert first["run"] == 1 and first["flags"][first["right_rule_flag"]]["confidence"] == "low"
    first["right_rule_flag"] = None
    next(r for r in changed["runs"] if r["copy"] == "as written")["day_count_flags"] = [0]
    assert planted.sentence(planted.counts(changed)) == STOP_9_SENTENCE.replace(
        "in three (two at", "in two (two at").replace("in none of five", "in one of five")


def test_the_planted_and_as_written_runs_share_one_prompt():
    """Both copies were read with one prompt: the as-written runs read tour/data/reader-prompt.txt, the planted runs
    the same prompt with only the planted edits made; neither carries the translation's list of test mistakes. With
    the after-release checkout, the copies stop 9 makes now are the files inside those prompts."""
    import hashlib
    planted, record = _reader()
    prompt = (TOUR / "data" / "reader-prompt.txt").read_text(encoding="utf-8")
    planted_prompt = planted.edited(prompt, planted.PLANT)
    digest = {"as written": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
              "planted": hashlib.sha256(planted_prompt.encode("utf-8")).hexdigest()}
    assert digest["as written"] != digest["planted"]
    assert {r["copy"] for r in record["runs"]} == {"planted", "as written"}
    assert all(r["prompt_sha256"] == digest[r["copy"]] for r in record["runs"])
    assert record["prompt"] == "tour/data/reader-prompt.txt"
    for text in (prompt, planted_prompt):
        assert "MUTANTS" not in text and planted.CUT[0] not in text
    assert "+ 1 (both days" in prompt and "+ 1 (both days" not in planted_prompt
    if SIDE.is_dir():
        source = (SIDE / "usecases" / "gitlab_relocation" / "translation.py").read_text(encoding="utf-8")
        assert planted.without_list(source) in prompt and planted.plant(source) in planted_prompt
        assert planted.plant(source) == planted.edited(planted.without_list(source), planted.PLANT)
        assert "MUTANTS" not in planted.plant(source) and "+ 1 (both days" not in planted.plant(source)


# --- the prebuilt checker programs (tour/prebuilt.py) -------------------------------------------------------------

def test_the_archive_is_the_same_bytes_for_the_same_programs():
    files = {"main/b": b"two", "main/a": b"one"}
    first = prebuilt.archive_bytes(files)
    assert first == prebuilt.archive_bytes(dict(reversed(list(files.items()))))
    with tarfile.open(fileobj=io.BytesIO(first), mode="r:gz") as tar:
        assert [(m.name, m.mtime, m.uid, m.uname) for m in tar.getmembers()] == [("main/a", 0, 0, ""),
                                                                                  ("main/b", 0, 0, "")]
    assert gzip.decompress(first)  # a plain gzip stream


def _j(*parts):
    return "".join(parts)


def test_the_scan_finds_private_details_in_a_program():
    """The archive's privacy scan: the public tree's patterns, and any home-directory path but Lean's public ones."""
    body = b"\x00".join([
        _j("cfg ~/.claude", "-someone/x").encode(),
        _j("/ho", "me/somebody/.cargo/registry/src/lib.rs").encode(),
        _j("/ho", "me/runner/work/lean4/lean4/src/runtime/io.cpp").encode(),
        _j("/ho", "me/runner/work/lean-llvm/lean-llvm/llvm-project/libunwind/src/x.cpp").encode(),
        _j("mail someone", "@mail.test now").encode(),
    ])
    hits = prebuilt.scan_files({"main/x": body})
    assert len(hits) == 3, hits
    assert sum("home path" in h for h in hits) == 1
    assert prebuilt.scan_files({"main/x": _j("/ho", "me/runner/work/lean4/lean4/src/runtime/io.cpp\x00plain words").encode()}) == []
    assert any("kind e" in h for h in prebuilt.scan_files({"main/x": _j("~/co", "de/private-project").encode()}))


def test_the_recorded_programs_have_no_private_detail():
    """Scan each built tour program, including a newer build whose sources moved beyond the recorded archive."""
    files = {}
    for side, record in prebuilt.manifest()["sides"].items():
        for rel in record["files"]:
            path = prebuilt.checkout(side) / rel
            if path.is_file():
                files[f"{side}/{rel}"] = path.read_bytes()
    assert files, "build the tour's Lean checker before running the privacy scan"
    assert prebuilt.scan_files(files) == []


def _sides(tmp_path, monkeypatch, lean_main=None):
    m = prebuilt.manifest()
    for side in m["sides"]:
        (tmp_path / side).mkdir(exist_ok=True)
    monkeypatch.setattr(prebuilt, "checkout", lambda side: tmp_path / side)

    def tree(path, sub):
        if sub == "lean" and path.name == "main" and lean_main:
            return lean_main
        return m["sides"][path.name][f"{sub}_tree"]
    monkeypatch.setattr(prebuilt, "tree", tree)


def test_install_refuses_an_archive_that_is_not_the_recorded_one(tmp_path, monkeypatch):
    _sides(tmp_path, monkeypatch)
    fake = tmp_path / "archive.tar.gz"
    fake.write_bytes(prebuilt.archive_bytes({"main/lean/.lake/build/bin/ve_service": b"not the program"}))
    assert prebuilt.install(str(fake)) == 1
    assert not (tmp_path / "main" / "lean").exists()


def test_install_builds_from_source_when_the_sources_moved_on(tmp_path, monkeypatch):
    _sides(tmp_path, monkeypatch, lean_main="0" * 40)
    assert prebuilt.install(str(tmp_path / "never-fetched")) == 3


def test_install_builds_from_source_when_the_archive_cannot_be_fetched(tmp_path, monkeypatch, capsys):
    """A manifest whose archive is not uploaded yet (a 404) or cannot be reached falls back to the build (exit 3, so
    tour/install.sh builds from source), with the reason on its own line; it never stops the install."""
    import http.server
    import threading

    class NotFound(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_error(404)

        def log_message(self, *args):
            pass

    _sides(tmp_path, monkeypatch)
    server = http.server.HTTPServer(("127.0.0.1", 0), NotFound)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert prebuilt.install(f"http://127.0.0.1:{server.server_port}/{prebuilt.ARCHIVE}") == 3
    finally:
        server.shutdown()
        server.server_close()
    assert "could not fetch the archive (HTTP Error 404" in capsys.readouterr().err

    class Short(http.server.BaseHTTPRequestHandler):  # a download cut off before its Content-Length
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Length", "1000")
            self.end_headers()
            self.wfile.write(b"x" * 10)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Short)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert prebuilt.install(f"http://127.0.0.1:{server.server_port}/{prebuilt.ARCHIVE}") == 3
    finally:
        server.shutdown()
        server.server_close()
    assert "could not fetch the archive" in capsys.readouterr().err
    assert prebuilt.install(str(tmp_path / "not-downloaded.tar.gz")) == 3
    assert "could not fetch the archive" in capsys.readouterr().err
    assert not (tmp_path / "main" / "lean").exists()
    install = (TOUR / "install.sh").read_text(encoding="utf-8")
    assert 'if [ "$status" = 3 ]; then' in install and "building from source instead" in install


def test_the_freshness_check_finds_each_stale_record():
    """tour/prebuilt.py check (stale): a recorded tree that is not main's, or not the after-release pin's, or a
    recorded after-release commit that is not the pin, is each reported."""
    m = prebuilt.manifest()
    assert m["sides"]["after-release"]["commit"] == PIN
    for side, field in (("main", "lean_tree"), ("main", "rust_tree"), ("after-release", "lean_tree"),
                        ("after-release", "rust_tree"), ("after-release", "commit")):
        moved = json.loads(json.dumps(m))
        moved["sides"][side][field] = "0" * 40
        found = prebuilt.stale(moved)
        what = "commit" if field == "commit" else f"{field.split('_')[0]}/ tree"
        assert any(line.startswith(f"{side}:") and (what in line or "not in this repository" in line)
                   for line in found), (side, field, found)
    del moved["sides"]["main"]
    assert "main: no record in tour/prebuilt.json" in prebuilt.stale(moved)


def test_the_freshness_check_passes_a_record_of_these_trees():
    """stale() is empty for a record of this checkout's trees and the pin's (read from git here, not from the record)."""
    def rev(spec):
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "-q", spec], capture_output=True,
                              text=True).stdout.strip()
    m = json.loads(json.dumps(prebuilt.manifest()))
    m["sides"]["main"].update(lean_tree=rev("HEAD:lean"), rust_tree=rev("HEAD:rust"))
    m["sides"]["after-release"].update(lean_tree=rev(f"{PIN}:lean") or "0" * 40,
                                       rust_tree=rev(f"{PIN}:rust") or "0" * 40, commit=PIN)
    found = prebuilt.stale(m)
    if rev(f"{PIN}^{{commit}}"):
        assert found == []
    else:  # an export without the after-release history: only that side can be unknown
        assert found and all(line.startswith("after-release:") and "not in this repository" in line for line in found)


# Main only: the nightly rebuild job (manage-agents tools-local/tour-prebuilt-nightly.sh) runs it on main with
# VE_TOUR_PREBUILT_FRESH=1. A branch's Lean change is not a stale main, so every other run (chain gates, trains, the
# selected runs) skips it with this reason, which tools/gate-optional.json allows for this test only.
FRESH_SKIP = "the tour prebuilt freshness check runs on main only, in the nightly rebuild job (VE_TOUR_PREBUILT_FRESH=1)"
FRESH_NODE = "tests/test_tour.py::test_prebuilt_json_records_the_trees_of_main_and_the_after_release_pin"


def test_prebuilt_json_records_the_trees_of_main_and_the_after_release_pin():
    """tour/prebuilt.json is fresh: its recorded lean/ and rust/ trees are main's own (this checkout) and those of the
    commit tour/AFTER_RELEASE_COMMIT names, so `sh tour/install.sh` takes the fast path on main."""
    if os.environ.get("VE_TOUR_PREBUILT_FRESH") != "1":
        pytest.skip(FRESH_SKIP)
    assert prebuilt.stale() == [], "tour/prebuilt.json is stale: rebuild and re-record it (tour/prebuilt.py make)"


def test_the_freshness_check_stays_out_of_chain_gates_and_trains(monkeypatch):
    """Without VE_TOUR_PREBUILT_FRESH=1 the freshness test skips even when the record is stale, the gates' skip list
    allows exactly that skip (that node, that reason, no pattern), and with the variable it fails on a stale record."""
    monkeypatch.setattr(prebuilt, "stale", lambda m=None: ["main: lean/ tree moved"])
    monkeypatch.delenv("VE_TOUR_PREBUILT_FRESH", raising=False)
    with pytest.raises(pytest.skip.Exception, match="runs on main only"):
        test_prebuilt_json_records_the_trees_of_main_and_the_after_release_pin()
    rows = [row for row in json.loads((ROOT / "tools/gate-optional.json").read_text(encoding="utf-8"))["optional_tests"]
            if row["reason"] in FRESH_SKIP]
    assert [row["nodeid"] for row in rows] == [FRESH_NODE]
    monkeypatch.setenv("VE_TOUR_PREBUILT_FRESH", "1")
    with pytest.raises(AssertionError, match="stale"):
        test_prebuilt_json_records_the_trees_of_main_and_the_after_release_pin()


def test_the_published_address_and_the_manifest():
    m = prebuilt.manifest()
    assert m["format"] == prebuilt.FORMAT and m["archive"] == prebuilt.ARCHIVE
    assert prebuilt.url() == (f"{m['repository']}/releases/download/tour-prebuilt-{m['sides']['main']['lean_tree'][:10]}"
                              f"/{prebuilt.ARCHIVE}")
    assert set(m["sides"]) == set(prebuilt.PROGRAMS)
    for side, programs in prebuilt.PROGRAMS.items():
        assert sorted(m["sides"][side]["files"]) == sorted(programs)


# --- the sceptic reviews' wording fixes (row demo-wording-fixes, 2026-11-27) -----------------------------------------

def _stop_section(page: str, heading: str) -> str:
    """The page's text from the heading that starts with `heading` up to the next "## " heading."""
    start = page.index(f"\n{heading}")
    end = page.find("\n## ", start + 1)
    return " ".join(page[start:end if end != -1 else len(page)].split())


def test_stop_6_says_what_read_as_is_and_its_dates_python():
    """Stop 6's "Read as" lines are each rule's generated English, read back to that rule (row tour-stop6-wording;
    before it they were an unchecked hand-written gloss, and the page said so); the dates that decide the answer are
    worked out in Python, said next to the proof-step count."""
    page = (TOUR / "README.md").read_text(encoding="utf-8")
    section = _stop_section(page, "## Stop 6")
    assert "how the checker read them" not in " ".join(page.split())
    assert ("then \"Read as\": each rule the checker was given for that clause, in English generated from the rule "
            "itself (the stop runs `ask.py --wording`)") in section
    assert ("the parser is VE's Python code, which is tested but not checked by Lean, and the stop prints the recorded "
            "sentences") in section
    assert "hand-written summaries of its rules (glosses, not checked against the rules) are left out here" in section
    assert "It is not what the checker read" not in section
    assert ("About \"15 of 15 proof steps\".** Lean checks the reasoning; the dates that decide the answer are "
            "worked out in Python, not proved" in section)
    assert "follows the GOV.UK guide's £35,000 test, not a pinned clause of law" in section


SAME_FAMILY = ("is a program written by an AI, and so far it has been judged only by AIs of the same model family as "
               "its translator; a check by a different AI family is due on Monday 30 November 2026 and has not yet "
               "run.")


@pytest.mark.parametrize("stop", ("## Stop 6", "## Stop 7", "## Stop 9"))
def test_the_real_text_stops_say_who_judged_the_translation_and_when_the_other_family_checks(stop):
    page = (TOUR / "README.md").read_text(encoding="utf-8")
    assert SAME_FAMILY in _stop_section(page, stop)


def test_each_stop_says_which_lean_check_it_means():
    """"Lean checked" has four senses on the page; each is defined once, and every stop says which one it means."""
    page = (TOUR / "README.md").read_text(encoding="utf-8")
    flat = " ".join(page.split())
    for sense in ("**a replayed proof**", "**one reading only**", "**a per-text program's result**", "**no Lean**"):
        assert sense in flat, sense
    for stop in ("## Stop 1:", "## Stop 2:", "## Stop 3:", "## Stop 4:", "## Stop 5:", "## Stop 6:", "## Stop 7:",
                 "## Stop 8:", "## Stop 9:", "## Stop 10:", "## A longer example", "## Stop 12"):
        assert "What Lean checked here:" in _stop_section(page, stop), stop
    assert "CHECKED means Lean read the sentence in exactly one way" in _stop_section(page, "## Stop 12")


def test_no_tour_file_claims_zero_wrong_correct_or_an_unqualified_independent_reader():
    """No tour file says "0 wrong" or calls agreement with the sealed answers "correct"; the reader is never called
    "independent" (it is of the translators' model family). The grading key of the newcomer questions is not shown
    to readers and is fixed for the newcomer runs, so it is left as written."""
    bad = re.compile(r"\b0 wrong\b|\bnone is wrong\b|\bindependent (?:reader|check)\b|\bcorrect(?:ly)?\b", re.I)
    files = [p for p in sorted(TOUR.rglob("*")) if p.is_file() and p.suffix in (".md", ".txt", ".py", ".sh")
             and "__pycache__" not in p.parts and p.name != "NEWCOMER-QUESTIONS.md"]
    hits = [f"{p.relative_to(ROOT)}: {m.group(0)}" for p in files for m in bad.finditer(p.read_text(encoding="utf-8"))]
    assert hits == []


# --- stop 6 prints each rule's checked wording, not the hand-written gloss (row tour-stop6-wording, 2026-11-28) -------

def _eligibility():
    here = str(ROOT / "usecases" / "eligibility")
    if here not in sys.path:
        sys.path.insert(0, here)
    import ask
    import explain
    return ask, explain


def test_stop_6_reads_each_clause_as_its_rules_checked_wording():
    """Stop 6 runs ask.py --wording: its recorded output reads each clause as the checked English wording of each rule
    it uses (the wordings results.json records today) and prints no rule's hand-written gloss."""
    ask, X = _eligibility()
    assert "usecases/eligibility/ask.py --wording usecases/eligibility/demo/b15.json" in \
        (TOUR / "stops" / "06-checker.sh").read_text(encoding="utf-8")
    recorded = (TOUR / "expected" / "06-checker.txt").read_text(encoding="utf-8")
    flat = " ".join(recorded.split())
    assert "Read as:" not in recorded and "Checked English wording:" not in recorded
    assert recorded.count("Read as (each rule's checked English wording, generated from the rule):") >= 20
    assert " ".join(X.GLOSSES_WORDING_ONLY.split()) in flat
    for rule in X.load_rules():
        assert f"- {' '.join(rule['gloss'].split())}" not in flat, rule["id"]
    data = X.explanation(ask.build_profile(ROOT / "usecases" / "eligibility" / "demo" / "b15.json"), lean=False)
    used = {rid: w for e in data["answers"] for rid, w in e.get("wordings", {}).items()}
    assert len(used) >= 20 and None not in used.values()
    for rid, wording in used.items():
        assert f"- {' '.join(wording.split())}" in flat, rid


def test_stop_6_record_matches_the_printout_without_lean():
    """The recorded stop 6 is today's ask.py --wording printout for its profile, Lean lines aside: a change to a
    rule's wording, gloss or clause shows here without a Lean build (the full rerun is
    test_each_stop_prints_its_recorded_output)."""
    ask, _ = _eligibility()
    recorded = (TOUR / "expected" / "06-checker.txt").read_text(encoding="utf-8").split("\n", 1)[1]
    now = ask.ask(ask.build_profile(ROOT / "usecases" / "eligibility" / "demo" / "b15.json"), lean=False, wording=True)
    strip = lambda text: [line for line in text.splitlines() if not line.startswith("Lean check:")]
    assert strip(recorded) == strip(now)


# --- the stand-in newcomers' kept transcripts (row tour-newcomer-transcripts) -----------------------------------------

def _newcomer_render():
    """tour/newcomer/render.py, loaded inside the tests that use it so this file still collects where it is absent."""
    return _load("tour_newcomer_render", TOUR / "newcomer" / "render.py")


NEWCOMER = TOUR / "newcomer"
# what the scrub must hide, built in pieces so this file holds none of it whole
_PRIVATE = re.compile("|".join([
    _j("/ho", "me/"), _j("/Us", "ers/"), r"[\w.+-]+@[\w-]+\.[\w.]+", r"\bclaude-(?!(?:sonnet|opus|haiku|fable)-)[a-z0-9]+",
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", _j("-ho", "me-"), _j("-Us", "ers-"), "toolu_",
    "session_id", "cost_usd", "\x00"]))


def test_the_newcomer_transcripts_are_kept_whole_and_scrubbed():
    """tour/newcomer/run1-3.md: each stand-in's calls and its full report (all three parts, five answers), with no
    folder, account, address or session detail, and the page each read is the one tour/newcomer/README.md names."""
    readme = (NEWCOMER / "README.md").read_text(encoding="utf-8")
    assert "**stand-in**" in readme and "not" in readme and "lead's decision" in readme
    page = re.search(r"sha256 ([0-9a-f]{64})", readme).group(1)
    for n in (1, 2, 3):
        text = (NEWCOMER / f"run{n}.md").read_text(encoding="utf-8")
        assert text.startswith(f"# Stand-in newcomer, run {n}\n\nA stand-in, not a person:"), n
        assert f"sha256 of its text without the line numbers: {page}" in text, n
        assert "sh tour/install.sh" in text and "12-write-your-own" in text, n
        report = text[text.index("## Report (the session's final reply)"):]
        for part in ("A.", "B.", "C."):
            assert f"{part} " in report, (n, part)
        assert [q for q in ("1.", "2.", "3.", "4.", "5.") if f"\n{q} " in report] == ["1.", "2.", "3.", "4.", "5."], n
        assert _PRIVATE.findall(text) == [], n
    assert _PRIVATE.findall(readme) == []


def test_the_scrub_hides_folders_accounts_and_addresses():
    scrub = _newcomer_render().scrub
    assert scrub(_j("cd /ho", "me/someone/code/x-newcomer-2/verifiable-english && ls")) == \
        "cd <newcomer>/verifiable-english && ls"
    assert scrub(_j("/Us", "ers/someone/.cache/x")) == "<home>/.cache/x"
    assert scrub(_j("mail some.one", "@mail.test today")) == "mail <e-mail> today"
    assert scrub("config claude-someone2 for claude-sonnet-5-5") == "config <account> for claude-sonnet-5-5"
    assert scrub("as claude-first-last today") == "as <account> today"
    assert scrub("id 0000aaaa-1111-2222-3333-444455556666 done") == "id <uuid> done"
    assert scrub(_j("in .claude/projects/-ho", "me-someone-code-x/log")) == "in .claude/projects/<project>/log"
    assert scrub(_j("in .claude/projects/-Us", "ers-someone-x/log")) == "in .claude/projects/<project>/log"
    assert scrub("a\x00\x00\x00b\x07c") == "a[3 zero bytes]b\\x07c"


def test_the_transcript_keeps_calls_outputs_and_report_and_drops_ids(tmp_path):
    page = "1\t# A tour of Verifiable English\n2\t\n3\tsome words"
    record = [
        {"type": "system", "subtype": "init", "model": "claude-sonnet-5-5", "session_id": "0000aaaa-1111-2222-3333-444455556666",
         "cwd": _j("/ho", "me/someone/n-newcomer-1")},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": "toolu_A", "name": "Read", "input": {"file_path": _j("/ho", "me/someone/n-newcomer-1/verifiable-english/tour/README.md")}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_A", "content": page}]}},
        {"type": "rate_limit_event", "rate_limit_info": {"status": "allowed"}},
        {"type": "assistant", "message": {"content": [{"type": "thinking", "thinking": "", "signature": "zz"},
            {"type": "tool_use", "id": "toolu_B", "name": "Bash", "input": {"command": "sh tour/stops/01-yes.sh"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "toolu_B",
                                                  "content": [{"type": "text", "text": "Yes.\n```inner```"}]}]}},
        {"type": "result", "subtype": "success", "result": "A. none\nB. none\nC. 1. sentences", "duration_ms": 61400,
         "total_cost_usd": 0.07, "session_id": "0000aaaa-1111-2222-3333-444455556666"},
    ]
    src = tmp_path / "r.jsonl"
    src.write_text("\n".join(json.dumps(e) for e in record) + "\n", encoding="utf-8")
    text = _newcomer_render().render(1, src)
    assert "a fresh claude-sonnet-5-5 session" in text and "It made 2 tool calls in 61 seconds." in text
    assert '"file_path": "<newcomer>/verifiable-english/tour/README.md"' in text
    import hashlib
    assert hashlib.sha256("# A tour of Verifiable English\n\nsome words".encode()).hexdigest() in text
    assert "some words" not in text  # the page itself is not repeated
    assert "## Call 2: Bash\n\n```sh\nsh tour/stops/01-yes.sh\n```" in text
    assert "````\nYes.\n```inner```\n````" in text  # a longer fence around output that holds one
    assert text.rstrip().endswith("A. none\nB. none\nC. 1. sentences")
    assert _PRIVATE.findall(text) == [] and "allowed" not in text and "0.07" not in text


def test_the_scores_quote_each_answer_and_name_the_fixed_key():
    """tour/newcomer/SCORES.md grades 3 runs x 5 questions against tour/NEWCOMER-QUESTIONS.md as it is now (its
    sha256: changing the key fails this test until the scores are redone), each grade quoting the run's own words."""
    import hashlib
    scores = (NEWCOMER / "SCORES.md").read_text(encoding="utf-8")
    key = hashlib.sha256((ROOT / "tour/NEWCOMER-QUESTIONS.md").read_bytes()).hexdigest()
    assert f"sha256\n{key}" in scores or f"sha256 {key}" in scores
    rows = re.findall(r"^\| ([123]) \| ([1-5]) \| (right|wrong) \| (.+) \|$", scores, re.M)
    assert [(r[0], r[1]) for r in rows] == [(str(n), str(q)) for n in (1, 2, 3) for q in range(1, 6)]
    for run, question, _grade, words in rows:
        text = (NEWCOMER / f"run{run}.md").read_text(encoding="utf-8")
        report = text[text.index("## Report (the session's final reply)"):]
        for fragment in words.split(" / "):
            assert fragment in report, (run, question, fragment)
    right = {n: sum(1 for r in rows if r[0] == str(n) and r[2] == "right") for n in (1, 2, 3)}
    assert "run 1, run 2 and run 3 each answered 5 of 5 right" in scores and right == {1: 5, 2: 5, 3: 5}
    assert "No person has graded them." in scores
    for commit in ("4454de2d3f", "0d184debe9"):
        assert commit in scores

