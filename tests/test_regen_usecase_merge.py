"""tools/regen_generated.py on files that carry hashes of a use-case environment (genconflict-1120).

Two branches that edit different legends of one environment each regenerate the same derived hash, so the
lexicon report, the route cases and a use case's results and coverage conflict on one value that only
regeneration on the merged tree settles. Hermetic: throwaway repositories with the registry's paths, whose
writers are small deterministic scripts (no service, no use-case harness):

* (i) both branches add an environment row, a recorded route case, an english.statement fixture change and a
  use-case case: `--resolve` exits 0 and the four files are the writers' output on the merged sources;
* (ii) the same recorded route case changed differently on both sides, or the same legend of the environment
  source, still declines (exit 2, nothing written, the merge still in progress);
* (iii) git's driver keeps a one-sided change of a `derived` file and stops on a two-sided one;
* (iv) a plain `--write`, `--check`, `--names` or `--resolve` with none of the use case's files conflicted does
  not run its writers; a conflict on them runs them, also after a `--resolve --only ...` staged them.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import regen_generated as R  # noqa: E402
from subprocesses import HANG_TIMEOUT  # noqa: E402

LEXICON = "conformance/english-lean/lexicon-report.json"
ROUTES = "tests/data/route-cases.jsonl"
RESULTS, COVERAGE, SPANS = (f"usecases/safety-framework/{name}" for name in ("results.json", "coverage.json",
                                                                             "spans.json"))
ENVIRONMENT = "usecases/safety-framework/environment.d1.json"
FOUR = (LEXICON, ROUTES, RESULTS, COVERAGE)

# The writers' stand-ins: each reads only sources of the scratch tree and writes its file(s) deterministically;
# `--check` compares instead. The use-case ones note each run in ran.log beside the repository.
STUB = r'''
import hashlib, json, pathlib, sys
mode, check = sys.argv[1], sys.argv[2:] == ["--check"]
here = pathlib.Path.cwd()
digest = lambda data: hashlib.sha256(data).hexdigest()[:16]
env = (here / "usecases/safety-framework/environment.d1.json").read_bytes()
def emit(path, text):
    if check:
        sys.exit(0 if (here / path).read_text() == text else 1)
    (here / path).parent.mkdir(parents=True, exist_ok=True)
    (here / path).write_text(text)
if mode in ("run", "document"):
    with open(here.parent / "ran.log", "a") as log:
        log.write(mode + (" --check" if check else "") + "\n")
if mode == "lexicon":
    rows = [{"path": str(p.relative_to(here)), "lexicon_id": digest(p.read_bytes())}
            for p in sorted([*here.glob("envs/*.json"), here / "usecases/safety-framework/environment.d1.json"])]
    emit("conformance/english-lean/lexicon-report.json", json.dumps({"environments": rows}, indent=1) + "\n")
elif mode == "routes":
    path = here / "tests/data/route-cases.jsonl"
    kept = [l for l in path.read_text().splitlines() if json.loads(l)[0] != "english.statement"]
    cases = [{"id": p.stem, "text": p.read_text().strip()} for p in sorted(here.glob("fixtures/*.txt"))]
    cases.append({"id": "stale", "lexicon": digest(env)})
    emit(str(path), "\n".join(kept + [json.dumps(["english.statement", c], separators=(",", ":")) for c in cases]) + "\n")
elif mode == "run":
    cases = sorted(p.stem for p in here.glob("usecases/safety-framework/cases/*.json"))
    emit("usecases/safety-framework/results.json",
         json.dumps({"cases": cases, "certificate_sha256": digest(env)}, indent=1) + "\n")
elif mode == "document":
    results = (here / "usecases/safety-framework/results.json").read_bytes()
    cases = json.loads(results)["cases"]
    emit("usecases/safety-framework/coverage.json",
         json.dumps({"document_sha256": digest(env + results), "units": len(cases)}, indent=1) + "\n")
    if not check:
        (here / "usecases/safety-framework/spans.json").write_text(json.dumps({"units": cases}, indent=1) + "\n")
'''

@pytest.fixture(autouse=True)
def _no_timing_log(monkeypatch):
    monkeypatch.setenv("VE_REGEN_LOG", "off")


STEPS = {"english-lexicon-report": ("lexicon",), "recorded-route-cases": ("routes",), "usecase-safety-framework": ("run", "document")}


def _git(root, *args, check=True):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=check, timeout=HANG_TIMEOUT)


def _stubbed(tmp_path: Path, root: Path) -> tuple:
    """The registry's entries owning the four files, their writers and checks replaced by the stubs (run in
    `root`, no service). On a registry without such entries: none."""
    stub = tmp_path / "stub.py"
    stub.write_text(STUB)
    entries = []
    for path in FOUR:
        entry = R.owner(path)
        if entry is None or entry.name in {done.name for done in entries}:
            continue
        modes = STEPS[entry.name]
        entries.append(dataclasses.replace(
            entry, cwd=str(root), service="",
            write=tuple((sys.executable, str(stub), mode) for mode in modes),
            check=tuple((sys.executable, str(stub), mode, "--check") for mode in modes)))
    return tuple(entries)


def _write_all(tmp_path, root):
    for entry in _stubbed(tmp_path, root) or _fallback(tmp_path, root):
        for step in entry.write:
            subprocess.run(list(step), cwd=root, check=True, timeout=HANG_TIMEOUT)


def _fallback(tmp_path, root):
    """The same writers outside the registry (only to build the scratch history on a registry without them)."""
    stub = tmp_path / "stub.py"
    stub.write_text(STUB)
    return [R.Generated(name, (), tuple((sys.executable, str(stub), m) for m in modes), None, cwd=str(root))
            for name, modes in STEPS.items()]


def _environment(**legends) -> str:
    # Separator keys keep the legends on lines git merges independently.
    value = {"a": "alpha", "m1": "-", "m2": "-", "m3": "-", "z": "zeta"}
    value.update(legends)
    return json.dumps(value, indent=1) + "\n"


RECORDED = [["alternatives", {"id": "admission", "n": 1}], ["diagnose", {"id": "c0", "v": "base"}],
            ["alternatives", {"id": "admission", "n": 2}], ["diagnose", {"kind": "no id"}]]


def _lines(rows) -> str:
    return "".join(json.dumps(row, separators=(",", ":")) + "\n" for row in rows)


def _commit(tmp_path, root, files: dict, message: str):
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    _write_all(tmp_path, root)
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)


def _repository(tmp_path, ours: dict, theirs: dict, driver: bool = False) -> Path:
    """Base, then branches `theirs` and `ours` (checked out) with the given source edits, each with its
    generated files rewritten by the writers, as a branch commits them."""
    root = tmp_path / "repo"
    root.mkdir()
    for args in (("init", "-q", "-b", "base"), ("config", "user.email", "t@example.com"), ("config", "user.name", "t")):
        _git(root, *args)
    if driver:
        _git(root, "config", f"merge.{R.DRIVER}.driver",
             f"{sys.executable} {ROOT / 'tools/regen_generated.py'} --merge-driver %O %A %B %P")
    _commit(tmp_path, root, {".gitattributes": R.attributes_text(), **BASE}, "base")
    _git(root, "checkout", "-q", "-b", "theirs")
    _commit(tmp_path, root, theirs, "theirs")
    _git(root, "checkout", "-q", "-b", "ours", "base")
    _commit(tmp_path, root, ours, "ours")
    return root


BASE = {ROUTES: _lines(RECORDED), ENVIRONMENT: _environment(), "envs/base.json": "{}\n", "fixtures/f1.txt": "one\n",
        "fixtures/f2.txt": "two\n", "usecases/safety-framework/cases/c1.json": "{}\n"}


OURS = {ENVIRONMENT: _environment(a="alpha, ours"), "envs/ours.json": '{"o": 1}\n', "fixtures/f1.txt": "one, ours\n",
        "usecases/safety-framework/cases/ours.json": "{}\n"}
THEIRS = {ENVIRONMENT: _environment(z="zeta, theirs"), "envs/theirs.json": '{"t": 1}\n',
          "fixtures/f2.txt": "two, theirs\n", "usecases/safety-framework/cases/theirs.json": "{}\n"}
NEW_OURS, NEW_THEIRS = ["diagnose", {"id": "ours-new"}], ["norms", {"id": "theirs-new"}]


def _with_route(sources: dict, row) -> dict:
    """`sources` plus a recorded route case appended to the base's recorded lines."""
    return {**sources, ROUTES: _lines(RECORDED + [row])}


@pytest.fixture
def stubbed(tmp_path, monkeypatch):
    """The registry reduced to the stubbed entries for the scratch repository (none on a registry without them)."""
    def install(root):
        entries = _stubbed(tmp_path, root)
        monkeypatch.setattr(R, "GENERATED", entries)
        return entries
    return install


def _files(root) -> dict:
    return {path: (root / path).read_bytes() for path in (*FOUR, SPANS)}


def _fresh(tmp_path, sources: dict) -> dict:
    """The writers' files on `sources` in a new directory: no merge, no conflict."""
    fresh = tmp_path / "fresh"
    for name, text in sources.items():
        (fresh / name).parent.mkdir(parents=True, exist_ok=True)
        (fresh / name).write_text(text)
    _write_all(tmp_path, fresh)
    return _files(fresh)


# (i) both branches extend every file kind: --resolve regenerates instead of declining


def test_resolve_regenerates_environment_hash_conflicts_to_the_writers_output(tmp_path, stubbed, capsys):
    root = _repository(tmp_path, _with_route(OURS, NEW_OURS), _with_route(THEIRS, NEW_THEIRS))
    entries = stubbed(root)
    assert _git(root, "merge", "--no-commit", "-q", "theirs", check=False).returncode != 0
    assert set(_git(root, "diff", "--name-only", "--diff-filter=U").stdout.split()) == {*FOUR, SPANS}
    code = R.resolve(entries, root)
    assert code == 0, capsys.readouterr().err  # on a registry without these entries: 2, "conflicts outside ..."
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout == ""
    resolved = _files(root)
    # The merged sources: both legends, both environment rows, both fixtures, both cases.
    assert json.loads((root / ENVIRONMENT).read_text())["a"] == "alpha, ours"
    assert json.loads((root / ENVIRONMENT).read_text())["z"] == "zeta, theirs"
    rows = [json.loads(line) for line in (root / ROUTES).read_text().splitlines()]
    assert rows[:len(RECORDED) + 2] == RECORDED + [NEW_OURS, NEW_THEIRS]  # ours' order, then theirs' new case
    assert [row[1]["id"] for row in rows[len(RECORDED) + 2:]] == ["f1", "f2", "stale"]
    assert [row[1].get("text") for row in rows[-3:-1]] == ["one, ours", "two, theirs"]
    assert {row["path"] for row in json.loads(resolved[LEXICON])["environments"]} >= {"envs/ours.json",
                                                                                      "envs/theirs.json"}
    assert json.loads(resolved[RESULTS])["cases"] == ["c1", "ours", "theirs"]
    # Byte-identical to the writers run on the merged sources, with no merge involved.
    merged = {**BASE, **OURS, **THEIRS, ENVIRONMENT: _environment(a="alpha, ours", z="zeta, theirs"),
              ROUTES: _lines(RECORDED + [NEW_OURS, NEW_THEIRS])}
    assert _fresh(tmp_path, merged) == resolved
    assert _git(root, "commit", "-q", "--no-edit", check=False).returncode == 0
    assert _git(root, "status", "--porcelain").stdout == ""


# (ii) a value no merge and no writer can settle still declines


def test_a_recorded_route_case_both_sides_changed_differently_declines(tmp_path, stubbed, capsys):
    changed = lambda v: _lines([RECORDED[0], ["diagnose", {"id": "c0", "v": v}], *RECORDED[2:]])  # noqa: E731
    root = _repository(tmp_path, {**OURS, ROUTES: changed("ours")}, {**THEIRS, ROUTES: changed("theirs")})
    entries = stubbed(root)
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    (tmp_path / "ran.log").unlink()
    before = _git(root, "status", "--porcelain").stdout, {path: (root / path).read_text() for path in FOUR}
    assert R.resolve(entries, root) == 2
    err = capsys.readouterr().err
    assert "diagnose/c0" in err and "needs a person" in err
    assert (_git(root, "status", "--porcelain").stdout, {path: (root / path).read_text() for path in FOUR}) == before
    assert _git(root, "rev-parse", "-q", "--verify", "MERGE_HEAD", check=False).returncode == 0
    assert not (tmp_path / "ran.log").exists()  # no writer ran


def test_the_same_environment_legend_changed_on_both_sides_declines(tmp_path, stubbed, capsys):
    root = _repository(tmp_path, {**OURS, ENVIRONMENT: _environment(a="ours")},
                       {**THEIRS, ENVIRONMENT: _environment(a="theirs")})
    entries = stubbed(root)
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    before = _git(root, "status", "--porcelain").stdout, (root / LEXICON).read_text()
    assert R.resolve(entries, root) == 2
    declined = capsys.readouterr().err.split("\n", 1)[1].split()
    assert declined == [ENVIRONMENT]  # the source alone: its derived files would have been regenerated
    assert (_git(root, "status", "--porcelain").stdout, (root / LEXICON).read_text()) == before


# (iii) git's driver on a `derived` file: one side's change is clean, two sides' changes stop the merge


def test_the_driver_stops_on_a_derived_file_both_sides_changed(tmp_path, stubbed):
    root = _repository(tmp_path, _with_route(OURS, NEW_OURS), _with_route(THEIRS, NEW_THEIRS), driver=True)
    stubbed(root)
    assert _git(root, "merge", "--no-commit", "-q", "theirs", check=False).returncode != 0
    # The route cases too: both sides rewrote their english.statement block (a fixture each, the stale case's hash).
    assert set(_git(root, "diff", "--name-only", "--diff-filter=U").stdout.split()) == {*FOUR, SPANS}
    assert "<<<<<<<" in (root / RESULTS).read_text() and "<<<<<<<" in (root / ROUTES).read_text()


@pytest.mark.parametrize("driver", [True, False])
def test_the_driver_merges_recorded_route_cases_by_key(tmp_path, stubbed, driver):
    """Both sides append a recorded case and leave the derived block alone: git's own merge stops on the two
    appends; the driver keeps both, ours' first."""
    root = _repository(tmp_path, _with_route({}, NEW_OURS), _with_route({}, NEW_THEIRS), driver=driver)
    stubbed(root)
    code = _git(root, "merge", "--no-edit", "-q", "theirs", check=False).returncode
    assert (code == 0) is driver
    if driver:
        rows = [json.loads(line) for line in (root / ROUTES).read_text().splitlines()]
        assert rows[:len(RECORDED) + 2] == RECORDED + [NEW_OURS, NEW_THEIRS]
        assert [row[0] for row in rows[len(RECORDED) + 2:]] == ["english.statement"] * 3


def test_the_driver_takes_a_one_sided_change_of_a_derived_file(tmp_path, stubbed):
    root = _repository(tmp_path, {"envs/ours.json": "{}\n"}, {"usecases/safety-framework/cases/t.json": "{}\n"},
                       driver=True)
    stubbed(root)
    for path in (*FOUR, SPANS):
        assert _git(root, "check-attr", "merge", "--", path).stdout.split()[-1] == R.DRIVER, path
    theirs = _git(root, "show", f"theirs:{RESULTS}").stdout
    assert _git(root, "merge", "--no-edit", "-q", "theirs", check=False).returncode == 0
    assert (root / RESULTS).read_text() == theirs


@pytest.mark.parametrize("path", [LEXICON, RESULTS, COVERAGE, SPANS])
def test_merge_text_of_a_derived_file(path):
    assert R.owner(path).merge == "derived"
    assert R.merge_text(path, "b\n", "b\n", "t\n") == ("t\n", True)
    assert R.merge_text(path, "b\n", "o\n", "b\n") == ("o\n", True)
    assert R.merge_text(path, "b\n", "x\n", "x\n") == ("x\n", True)
    text, clean = R.merge_text(path, "b\n", "o\n", "t\n")
    assert not clean and "<<<<<<<" in text
    assert R.merge_text(path, "b\n", "o\n", "t\n", resolving=True) == ("o\n", True)


# The keyed-lines merge of the recorded route cases


def _keyed(base, ours, theirs):
    return R.merge_keyed_lines(_lines(base), _lines(ours), _lines(theirs), ("english.statement",))


def test_keyed_lines_merge_by_mode_and_id():
    block_o, block_t = ["english.statement", {"id": "s", "o": 1}], ["english.statement", {"id": "s", "t": 1}]
    a1, a2, c0, noid = RECORDED
    new_o, new_t = ["norms", {"id": "x"}], ["norms", {"id": "y"}]
    # One side changed a group (both lines of a duplicated key), the other added one: both kept, the derived
    # block is ours', after every recorded line.
    group = ["alternatives", {"id": "admission", "n": 9}]
    assert _keyed([*RECORDED, block_o], [*RECORDED, new_o, block_o], [group, c0, noid, new_t, block_o]) == _lines(
        [group, c0, noid, new_o, new_t, block_o])
    # The derived block: a one-sided change is taken; a two-sided one stops git's driver, and --resolve takes
    # ours (its writer rewrites it next).
    assert _keyed([a1, block_o], [a1, block_o], [a1, block_t]) == _lines([a1, block_t])
    with pytest.raises(R.Conflict, match="english.statement block"):
        _keyed([a1], [a1, block_o], [a1, block_t])
    assert R.merge_keyed_lines(_lines([a1]), _lines([a1, block_o]), _lines([a1, block_t]), ("english.statement",),
                               resolving=True) == _lines([a1, block_o])
    # A deletion on one side is taken; the same change on both sides is taken once.
    assert _keyed(RECORDED, [a1, c0, a2], RECORDED) == _lines([a1, c0, a2])
    assert _keyed(RECORDED, [*RECORDED, new_o], [*RECORDED, new_o]) == _lines([*RECORDED, new_o])
    # Nothing changed: ours byte for byte, also with a key's lines apart.
    assert _keyed(RECORDED, RECORDED, RECORDED) == _lines(RECORDED)
    # A line without an id is its own group: two different ones are both kept.
    other = ["diagnose", {"kind": "other"}]
    assert _keyed(RECORDED, [*RECORDED, other], [*RECORDED, ["diagnose", {"kind": "third"}]]) == _lines(
        [*RECORDED, other, ["diagnose", {"kind": "third"}]])


@pytest.mark.parametrize("ours, theirs", [
    ([RECORDED[0], ["diagnose", {"id": "c0", "v": 1}]], [RECORDED[0], ["diagnose", {"id": "c0", "v": 2}]]),
    ([["norms", {"id": "x", "v": 1}]], [["norms", {"id": "x", "v": 2}]]),          # both added one key differently
    ([RECORDED[0]], [RECORDED[0], ["diagnose", {"id": "c0", "v": 2}]]),             # deleted against changed
    ([["alternatives", {"id": "admission", "n": 3}]], [["alternatives", {"id": "admission", "n": 4}]]),
])
def test_keyed_lines_refuse_a_group_both_sides_changed_differently(ours, theirs):
    base = RECORDED[:2]
    with pytest.raises(R.Conflict):
        _keyed(base, ours, theirs)
    text, clean = R.merge_text(ROUTES, _lines(base), _lines(ours), _lines(theirs))
    assert not clean and "<<<<<<<" in text


# (iv) the use case's writers run only when its files conflict


def _plain_registry(tmp_path, monkeypatch, root):
    """The stubbed entries plus a cheap one, for main()'s plain runs; returns the use-case entry."""
    entries = _stubbed(tmp_path, root)
    usecase = next(entry for entry in entries if entry.name == "usecase-safety-framework")
    assert usecase.on_conflict and not any(entry.on_conflict for entry in entries if entry is not usecase)
    monkeypatch.setattr(R, "GENERATED", entries)
    return usecase


def _ran(tmp_path) -> list[str]:
    log = tmp_path / "ran.log"
    lines = log.read_text().splitlines() if log.is_file() else []
    log.unlink(missing_ok=True)
    return lines


def test_plain_write_check_and_names_skip_the_use_case(tmp_path, monkeypatch, capsys):
    root = _repository(tmp_path, {"envs/ours.json": "{}\n"}, {"envs/theirs.json": "{}\n"})
    _plain_registry(tmp_path, monkeypatch, root)
    _ran(tmp_path)
    assert R.main(["--write"]) == 0 and R.main(["--check"]) == 0
    assert _ran(tmp_path) == []
    assert R.main(["--names"]) == 0
    assert "usecase-safety-framework" not in capsys.readouterr().out.split()
    assert R.main(["--write", "--only", "usecase-safety-framework"]) == 0
    assert R.main(["--check", "--only", "usecase-safety-framework"]) == 0
    assert _ran(tmp_path) == ["run", "document", "run --check", "document --check"]


def test_a_resolve_without_a_use_case_conflict_skips_it(tmp_path, monkeypatch, capsys):
    root = _repository(tmp_path, {"envs/ours.json": "{}\n"}, {"envs/theirs.json": "{}\n"})
    _plain_registry(tmp_path, monkeypatch, root)
    _ran(tmp_path)
    assert _git(root, "merge", "--no-commit", "-q", "theirs", check=False).returncode != 0
    assert _git(root, "diff", "--name-only", "--diff-filter=U").stdout.split() == [LEXICON]
    assert R.resolve(R.GENERATED, root) == 0, capsys.readouterr().err
    assert _ran(tmp_path) == []


def test_a_use_case_conflict_runs_it_also_after_a_partial_resolve(tmp_path, monkeypatch, capsys):
    """The merge train first runs `--resolve --only lake-build --only checker-pins`, which stages every
    resolved file; the full `--resolve` after it still knows the use case's files conflicted."""
    root = _repository(tmp_path, OURS, THEIRS)
    _plain_registry(tmp_path, monkeypatch, root)
    _ran(tmp_path)
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    lexicon = [entry for entry in R.GENERATED if entry.name == "english-lexicon-report"]
    assert R.resolve(lexicon, root, only=["english-lexicon-report"]) == 0, capsys.readouterr().err
    assert _ran(tmp_path) == [] and _git(root, "diff", "--name-only", "--diff-filter=U").stdout == ""
    assert R.resolve(R.GENERATED, root) == 0, capsys.readouterr().err
    assert _ran(tmp_path) == ["run", "document", "run --check", "document --check"]
    assert json.loads((root / RESULTS).read_text())["cases"] == ["c1", "ours", "theirs"]


def test_a_failed_use_case_writer_fails_the_resolve(tmp_path, monkeypatch, capsys):
    """Without the pinned text build_document.py fails: --resolve exits 1, never skips it."""
    root = _repository(tmp_path, OURS, THEIRS)
    usecase = _plain_registry(tmp_path, monkeypatch, root)
    failing = dataclasses.replace(usecase, write=(*usecase.write[:1], (sys.executable, "-c", "raise SystemExit(1)")))
    monkeypatch.setattr(R, "GENERATED", tuple(failing if entry is usecase else entry for entry in R.GENERATED))
    _git(root, "merge", "--no-commit", "-q", "theirs", check=False)
    assert R.resolve(R.GENERATED, root) == 1
    assert "usecase-safety-framework" in capsys.readouterr().err
