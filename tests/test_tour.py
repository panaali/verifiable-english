"""The newcomer tour (tour/README.md): every stop's output, the page, and the tour's texts stay as recorded.

tour/expected/<stop>.txt is written by tour/make_expected.py from a real run of tour/stops/<stop>.sh. This test runs
each stop again (with this test's Python in place of `uv run --frozen python`, through VE_TOUR_PYTHON) and fails when
its output differs, and fails when the page's output blocks differ from those files. The stops that use branch
after-release (tour/make_expected.py AFTER_RELEASE) need its checkout in .tour-after-release/ (sh tour/install.sh);
without it they are skipped with that reason, since their feature is not on this branch yet.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys

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
    "tour/data/relocation-R009-sealed.jsonl", "tour/stops/common.sh", "tour/stops/dates.py", "tour/stops/sums.py",
    "tour/stops/planted.py", "tour/stops/not_yet.py", "tour/expected/seconds.json",
)
make_expected = _load("tour_make_expected", TOUR / "make_expected.py")
build_texts = _load("tour_build_texts", TOUR / "texts" / "build_texts.py")


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


def test_the_page_has_no_project_words():
    page = (TOUR / "README.md").read_text(encoding="utf-8").lower()
    for word in ("certificate", "mutant", "w6", "seat", "codename"):
        assert word not in page, word


def test_the_tour_texts_are_built_from_their_sentences():
    for name, text in build_texts.documents().items():
        assert (TOUR / "texts" / name).read_text(encoding="utf-8") == text, name


@pytest.mark.parametrize("stop", make_expected.STOPS)
def test_each_stop_prints_its_recorded_output(stop):
    if stop in make_expected.AFTER_RELEASE and not (ROOT / ".tour-after-release" / ".venv").is_dir():
        pytest.skip("this stop runs from branch after-release (its checkout .tour-after-release/ is made by "
                    "sh tour/install.sh) until its feature reaches main")
    output, _ = make_expected.run_stop(stop, env={**os.environ, "VE_TOUR_PYTHON": sys.executable})
    assert output == (TOUR / "expected" / f"{stop}.txt").read_text(encoding="utf-8")


def test_every_tour_file_is_listed_and_present():
    on_disk = {str(p.relative_to(ROOT)) for p in TOUR.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
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
