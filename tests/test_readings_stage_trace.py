"""The readings admission stage timer of `ve_service` (lean/VE/Readings/Stage.lean, lean/VE/Service/StageTimes.lean).

The production stage functions write their own markers; under `VE_READINGS_STAGE_TIMES=1` the service times them
into JSON lines, under `=markers` it passes the markers through as they are. The truth table runs every request shape
(kind x split x W2 x component x handle x admission ok or failing) both ways and asserts that the timed lines count
exactly the production markers, per (stage, component, status), and that no answer changes. F1-F9 of
scale-admission-profile (reviews/dri-decisions-20261029-scale-admission-profile.md) are regression cases."""
from collections import Counter
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess

import pytest

from tests.lean_routes import SERVICE
from tests.subprocesses import HANG_TIMEOUT


ROOT = Path(__file__).resolve().parents[1]
VARIABLE = "VE_READINGS_STAGE_TIMES"
STAGES = ("admitS2", "admitS2Of", "admitSDOf", "admitNDFull", "distinguishingModels")
KINDS = ("readings-elaborate", "readings-choice", "readings-verdicts")


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def serve(lines, value):
    env = {k: v for k, v in os.environ.items() if k != VARIABLE}
    if value is not None:
        env[VARIABLE] = value
    observed = subprocess.run([str(SERVICE)], input="".join(lines), text=True, capture_output=True,
                              timeout=HANG_TIMEOUT, env=env, check=True)
    return observed.stdout, observed.stderr


def request(case, rid="p"):
    return compact({"id": rid, "mode": "readings-route", "cases": [case]}) + "\n"


def answer(stdout, index=-1):
    return json.loads(stdout.splitlines()[index])["results"][0]["result"]


def timed_rows(stderr):
    rows = [json.loads(line) for line in stderr.splitlines()]
    for row in rows:
        assert set(row) == {"stage", "part", "status", "nanos", "cpu_ticks"}, row
        assert row["stage"] in STAGES and row["status"] in ("ok", "error"), row
        assert type(row["part"]) is str and row["part"], row
        assert type(row["nanos"]) is int and row["nanos"] >= 0, row
        assert type(row["cpu_ticks"]) is int and row["cpu_ticks"] >= 0, row
    return rows


def recorded(stderr):
    """The timed lines' count per (stage, component, status)."""
    return Counter((row["stage"], row["part"], row["status"]) for row in timed_rows(stderr))


def produced(stderr):
    """The production-side count: each `end` marker of a stage, in the innermost component open around it."""
    counts, parts, stages = Counter(), [], []
    for line in stderr.splitlines():
        prefix, word, rest = line.split(" ", 2)
        assert prefix == "ve-stage", line
        if word == "enter":
            parts.append(rest)
        elif word == "leave":
            assert rest.split(" ", 1)[1] == parts.pop(), line
        elif word == "begin":
            stages.append(rest)
        else:
            assert word == "end", line
            status, name = rest.split(" ", 1)
            assert name == stages.pop(), line
            counts[(name, parts[-1] if parts else "", status)] += 1
    assert not parts and not stages
    return counts


def observe(lines):
    """The answers and the timed lines of `lines`, after checking them against the markers and the silent run."""
    off, silent = serve(lines, None)
    timed, stderr = serve(lines, "1")
    raw, markers = serve(lines, "markers")
    assert silent == ""
    assert timed == off and raw == off
    counts = recorded(stderr)
    assert counts == produced(markers)
    return off, timed_rows(stderr), counts


# The truth table


def split_w2():
    from tests.test_readings_companions_lean import env_main, fc1

    return env_main(), fc1()[0], "rs_a"


def split_non_w2():
    from docs.perf.admission_cases import case_from

    case = case_from(ROOT / "docs/perf/inputs/prefix-50.ve.md", 1)
    return case["environment"], case["document"], "rs_u025"


def unsplit():
    from tests.test_readings_nd_lean import doc1, env1

    environment = env1()
    return environment, doc1(environment)[0], None


SHAPES = {"split-w2": split_w2, "split": split_non_w2, "unsplit": unsplit}
CELLS = [(kind, shape, component, handle, admission)
         for kind in KINDS for shape in SHAPES
         for component in (("product", "main", "companion") if shape != "unsplit" else ("product", "main"))
         for handle in ("fresh", "registered", "reused") for admission in ("ok", "failing")]


def cell_lines(kind, shape, component, handle, admission):
    environment, document, companion = SHAPES[shape]()
    document = copy.deepcopy(document)
    if admission == "failing":
        document["units"].append(document["units"][0])
    case = {"id": "p", "kind": kind, "document": document}
    if kind == "readings-verdicts":
        case.update(question="premises", assumed=[])
    if kind == "readings-choice":
        case.update(choice=[], inner={"kind": "norm-defaults-elaborate"})
    if component != "product":
        case["component"] = "main" if component == "main" else companion
    if handle == "fresh":
        return [request({**case, "environment": environment})]
    text = compact(environment)
    digest = hashlib.sha256(text.encode()).hexdigest()
    named = compact({**case, "environment_handle": digest})
    registered = ('{"id":"r","mode":"readings-route","environments":{' + json.dumps(digest) + ":" + text
                  + '},"cases":[' + named + "]}\n")
    if handle == "registered":
        return [registered]
    return [registered, '{"id":"u","mode":"readings-route","cases":[' + named + "]}\n"]


@pytest.mark.parametrize("cell", CELLS, ids=["-".join(c) for c in CELLS])
def test_stage_times_count_the_production_markers(cell):
    kind, shape, component, handle, admission = cell
    stdout, rows, counts = observe(cell_lines(*cell))
    results = [json.loads(line)["results"][0]["result"] for line in stdout.splitlines()[1:]]
    assert len(results) == (2 if handle == "reused" else 1)
    if admission == "failing":
        assert all(result["status"] == "error" for result in results)
        assert any(row["status"] == "error" for row in rows)
    else:
        assert all(row["status"] == "ok" for row in rows)
    # Every production stage call runs inside a component of the request; a split admits main first.
    assert sum(counts.values()) == len(rows) >= 1
    document = json.loads(cell_lines(*cell)[0])["cases"][0]["document"]
    assert {row["part"] for row in rows} <= {"main"} | {s["id"] for s in document["reading_sets"]}
    if shape != "unsplit" and handle != "reused":
        assert rows[0]["part"] == "main"


def test_truth_table_reaches_every_admission_stage_and_component():
    """The cells together record each admission stage of the three kinds, on main and on a companion."""
    seen = Counter()
    for cell in [c for c in CELLS if c[3] == "fresh" and c[4] == "ok" and c[2] == "product"]:
        _, rows, _ = observe(cell_lines(*cell))
        seen.update((row["stage"], row["part"] == "main") for row in rows)
    assert {key for key in seen} >= {("admitS2", True), ("admitS2", False), ("admitNDFull", True),
                                     ("admitNDFull", False)}


def test_stage_times_are_silent_by_default_and_pass_other_stderr_through():
    lines = cell_lines("readings-elaborate", "unsplit", "product", "fresh", "ok")
    for value in (None, "0", "", "yes"):
        assert serve(lines, value)[1] == ""
    for value in (None, "1", "markers"):
        env = {k: v for k, v in os.environ.items() if k != VARIABLE}
        if value is not None:
            env[VARIABLE] = value
        usage = subprocess.run([str(SERVICE), "extra"], input="", text=True, capture_output=True,
                               timeout=HANG_TIMEOUT, env=env)
        assert usage.returncode == 2
        assert usage.stderr == "usage: ve_service  (JSON lines on stdin and stdout)\n"


def test_normal_client_records_registered_and_reused_handle(monkeypatch):
    """F2: the client registers the environment, then reuses its handle; both requests are timed."""
    from tests.test_readings_nd_lean import doc1, env1
    from ve.backends.lean_service import LeanService

    environment = env1()
    case = {"id": "p", "kind": "readings-elaborate", "environment": environment, "document": doc1(environment)[0]}
    monkeypatch.setenv(VARIABLE, "1")
    with LeanService(timeout=HANG_TIMEOUT, allow_unlisted_build=True) as service:
        for repeat in range(2):
            start, _ = service.stderr()
            assert service.run("readings-route", [case], timeout=HANG_TIMEOUT)[0]["status"] == "ok"
            _, stderr = service.stderr(start)
            assert [row["stage"] for row in timed_rows(stderr)] == ["admitS2", "admitNDFull"], repeat


# F1-F9 of scale-admission-profile


def main_rows(rows, stage):
    return [row for row in rows if row["part"] == "main" and row["stage"] == stage]


@pytest.mark.parametrize("kind", KINDS)
def test_f1_split_w2_main_admits_twice_and_completes_its_fixed_part(kind):
    environment, document, _ = split_w2()
    case = {"id": "p", "kind": kind, "environment": environment, "document": document}
    if kind == "readings-verdicts":
        case.update(question="premises", assumed=[])
    stdout, rows, _ = observe([request(case)])
    if kind == "readings-verdicts":
        assert answer(stdout)["status"] == "ok"
    assert len(main_rows(rows, "admitS2")) >= 2
    assert any(row["status"] == "ok" for row in main_rows(rows, "admitNDFull"))


@pytest.mark.parametrize("kind", ["readings-elaborate", "readings-choice"])
def test_f3_split_non_w2_main_records_both_admissions(kind):
    environment, document, _ = split_non_w2()
    case = {"id": "p", "kind": kind, "environment": environment, "document": document}
    if kind == "readings-choice":
        main_sets = [s for s in document["reading_sets"] if not any("companion" in r for r in s["readings"])]
        case.update(choice=[[s["id"], 0] for s in main_sets], inner={"kind": "norm-defaults-elaborate"})
    stdout, rows, _ = observe([request(case)])
    assert answer(stdout)["status"] == "ok"
    main = main_rows(rows, "admitS2")
    assert len(main) == 2 and all(row["status"] == "ok" for row in main)


def test_f4_named_main_verdict_records_both_completions():
    environment, document, _ = split_non_w2()
    case = {"id": "p", "kind": "readings-verdicts", "environment": environment, "document": document,
            "component": "main", "question": "premises", "assumed": []}
    stdout, rows, _ = observe([request(case)])
    assert answer(stdout)["status"] == "ok"
    main = main_rows(rows, "admitNDFull")
    assert len(main) == 2 and all(row["status"] == "ok" for row in main)


@pytest.mark.parametrize("budget", [False, True], ids=["f4-enumerated", "f7-budgeted-superposed"])
def test_f4_f7_unsplit_verdict_records_both_completions(budget):
    from ve.readings_verdicts import BUDGET

    environment, document, _ = unsplit()
    case = {"id": "p", "kind": "readings-verdicts", "environment": environment, "document": document,
            "question": "premises", "assumed": []}
    if budget:
        case["budget"] = dict(BUDGET)
    stdout, rows, _ = observe([request(case)])
    assert answer(stdout)["status"] == "ok"
    main = main_rows(rows, "admitNDFull")
    assert len(main) == 2 and all(row["status"] == "ok" for row in main)


def test_f5_s1_validation_records_no_s2_stage():
    from tests.test_readings_companions_lean import env_main

    case = {"id": "p", "kind": "readings-validate", "environment": env_main(),
            "document": {"units": [], "reading_sets": []}}
    stdout, rows, _ = observe([request(case)])
    assert answer(stdout)["status"] == "ok"
    assert rows == []


def soft_case(kind):
    from tests.test_readings_s1_lean import SOFT_PROFILES, env_k, k1_document

    environment = env_k(profiles=("norm-defaults@0", *SOFT_PROFILES))
    case = {"id": "p", "kind": kind, "environment": environment, "document": k1_document(environment)[0]}
    if kind == "readings-verdicts":
        case.update(question="premises", assumed=[])
    return case


def test_f5_soft_validation_continues_into_s2_and_its_distinguishing_models():
    stdout, rows, _ = observe([request(soft_case("readings-validate"))])
    assert answer(stdout)["status"] == "ok"
    assert [row["stage"] for row in rows] == ["admitS2Of", "admitSDOf", "distinguishingModels"]
    assert all(row["status"] == "ok" and row["part"] == "main" for row in rows)


def test_f6_failed_main_admission_records_no_companion_stage():
    environment, document, _ = split_w2()
    document["units"].append(document["units"][0])
    stdout, rows, _ = observe([request({"id": "p", "kind": "readings-elaborate", "environment": environment,
                                        "document": document})])
    assert answer(stdout)["status"] == "error"
    assert [(row["part"], row["status"]) for row in rows] == [("main", "error")]


@pytest.mark.parametrize("kind", ["readings-elaborate", "readings-choice", "readings-verdicts"])
def test_f8_soft_kinds_record_the_soft_completion(kind):
    stdout, rows, _ = observe([request(soft_case(kind))])
    assert answer(stdout)["status"] == "ok" or kind == "readings-choice"
    assert [row["stage"] for row in rows] == ["admitS2", "admitSDOf"]


def test_f9_elaborate_records_no_distinguishing_models():
    environment, document, _ = unsplit()
    stdout, rows, _ = observe([request({"id": "p", "kind": "readings-elaborate", "environment": environment,
                                        "document": document})])
    assert answer(stdout)["status"] == "ok"
    assert [row["stage"] for row in rows] == ["admitS2", "admitNDFull"]
