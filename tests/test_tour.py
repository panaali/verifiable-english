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
    "tour/make_expected.py", "tour/texts/build_texts.py", "tour/texts/club.ve.md",
    "tour/data/relocation-R009-sealed.jsonl", "tour/data/reader-planted.json",
    "tour/data/reader-as-written.json", "tour/stops/common.sh",
    "tour/stops/dates.py", "tour/stops/sums.py", "tour/stops/planted.py", "tour/stops/not_yet.py",
    "tour/expected/seconds.json", "tour/prebuilt.py", "tour/prebuilt.json", "tour/AFTER_RELEASE_COMMIT",
    ".github/workflows/tour-prebuilt.yml",
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
QUOTED = {"tour/data/relocation-R009-sealed.jsonl", "tour/data/reader-planted.json", "tour/prebuilt.json"}
# planted.py quotes the lines of the translation it edits (its EDITS and CUT), which name the translation's own list of
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
    present = subprocess.run(["git", "cat-file", "-e", f"{pin}^{{commit}}"], cwd=ROOT,
                             capture_output=True).returncode == 0
    if present:
        return
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pytest.skip(f"tour pin {pin} is not in the Actions export (branch after-release is not exported)")
    pytest.fail(f"tour pin {pin} missing from this checkout")


def test_a_missing_pin_fails_outside_actions(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(pytest.fail.Exception, match="tour pin 0{40} missing from this checkout"):
        _require_pin("0" * 40)


def test_a_missing_pin_skips_only_on_actions(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    with pytest.raises(pytest.skip.Exception, match="tour pin 0{40} is not in the Actions export"):
        _require_pin("0" * 40)
    monkeypatch.setenv("GITHUB_ACTIONS", "1")  # only the exact value GitHub sets
    with pytest.raises(pytest.fail.Exception):
        _require_pin("0" * 40)


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
                 "usecases/gitlab_relocation/"):
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


def test_the_reader_record_is_the_planted_translation():
    """Stop 9 shows the reader's recorded flags: one high-confidence flag on the planted part, quoting both sides."""
    record = json.loads((TOUR / "data" / "reader-planted.json").read_text(encoding="utf-8"))
    hit = [f for f in record["flags"] if f["unit"] == record["planted_unit"] and f["confidence"] == "high"]
    assert len(hit) == 1 and hit[0]["source"] and hit[0]["translation"] and hit[0]["why"]
    assert re.fullmatch(r"[0-9a-f]{64}", record["translation_sha256"])
    if SIDE.is_dir():
        planted = _load("tour_planted", TOUR / "stops" / "planted.py")
        source = (SIDE / "usecases" / "gitlab_relocation" / "translation.py").read_text(encoding="utf-8")
        text = planted.plant(source)
        import hashlib
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == record["translation_sha256"]
        assert "MUTANTS" not in text and "+ 1 (both days" not in text


def test_stop_9_names_the_other_flags_from_the_records():
    """Stop 9's line on the reader's other flags is worked out from the two records, not written by hand: it names
    each other flag's part and confidence, and counts those also raised on the translation as written."""
    planted = _load("tour_planted_flags", TOUR / "stops" / "planted.py")
    record = json.loads((TOUR / "data" / "reader-planted.json").read_text(encoding="utf-8"))
    as_written = json.loads((TOUR / "data" / "reader-as-written.json").read_text(encoding="utf-8"))
    others = [f for f in record["flags"] if not (f["unit"] == record["planted_unit"] and f["confidence"] == "high")]
    line = planted.other_flags_line(record, as_written)
    assert re.findall(r"part (\d+) \((\w+)\)", line) == [(f["unit"][1:], f["confidence"]) for f in others]
    recorded = (TOUR / "expected" / "09-planted-mistake.txt").read_text(encoding="utf-8")
    assert line in recorded.splitlines()
    assert f"It raised {len(others)} of them" in line
    changed = {**as_written, "flags": [f for f in as_written["flags"] if f["unit"] != "U15"]}
    assert f"It raised {len(others) - 1} of them" in planted.other_flags_line(record, changed)
    assert re.fullmatch(r"[0-9a-f]{64}", as_written["translation_sha256"])
    if SIDE.is_dir():
        import hashlib
        source = (SIDE / "usecases" / "gitlab_relocation" / "translation.py").read_bytes()
        assert hashlib.sha256(source).hexdigest() == as_written["translation_sha256"]


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


def test_the_published_address_and_the_manifest():
    m = prebuilt.manifest()
    assert m["format"] == prebuilt.FORMAT and m["archive"] == prebuilt.ARCHIVE
    assert prebuilt.url() == (f"{m['repository']}/releases/download/tour-prebuilt-{m['sides']['main']['lean_tree'][:10]}"
                              f"/{prebuilt.ARCHIVE}")
    assert set(m["sides"]) == set(prebuilt.PROGRAMS)
    for side, programs in prebuilt.PROGRAMS.items():
        assert sorted(m["sides"][side]["files"]) == sorted(programs)
