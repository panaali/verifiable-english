"""Compare the S3 fixture texts at the dispatched English reading boundary.

The Python side uses ``_python_reading`` (hand parser, Lark audit, typed check);
the Lean side uses the same request, response validator, and comparison record as
``english.admission`` shadow mode. Cases are sent in one foreground route process.
This is the fixture slice of G3, not a claim about its sealed or reverse corpus.

    .venv/bin/python -m conformance.english_lean_s3_compare --report-only

Without ``--report-only`` any unexplained difference makes the command fail. The JSON report
contains the individual records and the two spec dispositions so a gate cannot pass from a summary alone.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
from types import SimpleNamespace
import warnings

from conformance import english_lean_s3_python as fixtures
from ve import Environment
from ve.backends import english_lean as adapter
from ve.backends import relay
from ve.english import (EnglishParser, EnglishVocabulary, UnreviewedVocabularyWarning,
                        _normalise_english_source, _python_reading)
from ve.errors import CheckerUnavailable

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "conformance/english-lean/s3-fixture-comparison.json"
SPEC_DISPOSITIONS = {"or38a", "or38b"}


def cases() -> list[dict]:
    """The spec's exact texts and, where necessary, Python's selected wording."""
    output = []
    envs = {}
    words = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        for fixture_id, env_name, source, expected in fixtures._fixtures():
            if env_name not in envs:
                envs[env_name] = Environment(fixtures.environment_json(env_name))
                words[env_name] = EnglishVocabulary(envs[env_name])
            output.append({"id": fixture_id, "environment": env_name, "source": source,
                           "variant": "spec", "expected": expected})
            selected = fixtures.python_text(env_name, source, words[env_name])
            if selected is not None:
                output.append({"id": fixture_id, "environment": env_name, "source": selected,
                               "variant": "python-selection", "expected": expected})
    return output


def _attempt(fn):
    try:
        return fn()
    except Exception as exc:
        return exc


def _independent_readers(env, source: str, words) -> dict:
    """Run the hand grammar and Lark independently of the dispatched Python reading."""
    from ve.surface.unambiguity import require_unique_derivation

    def hand():
        normalised, _ = _normalise_english_source(source, words)
        return EnglishParser(env, normalised, words).document()

    def lark():
        return require_unique_derivation(env, source)

    out = {}
    for name, fn in (("hand", hand), ("lark", lark)):
        result = _attempt(fn)
        out[name] = ({"status": "error", "class": type(result).__name__}
                     if isinstance(result, Exception) else {"status": "one"})
    return out


def _disposition(item: dict, comparison: dict) -> str | None:
    """The two mixed-fault cases expressly accepted by S3 spec 2.11 and Q11."""
    if (item["id"] in SPEC_DISPOSITIONS and item["variant"] == "spec"
            and comparison["python"]["class"] == "ResourceLimit"
            and comparison["lean"]["status"] == "none"
            and set(comparison["classes"]) == {"diagnostic-code", "verdict"}):
        return "spec 2.11/Q11: depth check precedes malformed integer shape in Python"
    return None


def _lean_result(row: dict, request_id: str, env, source: str, words):
    if type(row) is not dict or row.get("id") != request_id:
        return CheckerUnavailable("CheckerUnavailable: the Lean English reader returned a mismatched row id")
    if row.get("status") != "ok" or row.keys() != {"id", "status", "result"}:
        return CheckerUnavailable(f"CheckerUnavailable: the Lean English reader did not read the case: "
                                  f"{row.get('error', row)!r}")
    response = row["result"]
    expected = adapter.identities(env, source, words, adapter.export(words))
    try:
        problem = adapter.response_problem(response, expected, env, source)
    except RecursionError:
        problem = "the response is nested too deeply"
    if problem:
        return CheckerUnavailable(f"CheckerUnavailable: the Lean English reader's answer is malformed: {problem}")
    reading = adapter.LeanReading(response, env, source)
    return SimpleNamespace(lean=reading) if reading.status == "one" else reading.rejection()


def service_rows(_executable, mode: str, cases: list[dict]) -> list[dict]:
    """The persistent service's rows for `cases` (spec 2.7: the one-shot route is retired as a transport)."""
    return relay.rows(mode, cases)


def compare(rows: list[dict] | None = None, *, transport=service_rows) -> dict:
    """Return every comparison record and counts derived from those records."""
    rows = cases() if rows is None else rows
    if not rows:
        raise ValueError("the comparison corpus is empty")
    envs = {}
    words = {}
    requests = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
        for index, item in enumerate(rows):
            name = item["environment"]
            if name not in envs:
                envs[name] = Environment(fixtures.environment_json(name))
                words[name] = EnglishVocabulary(envs[name])
            request = adapter.request(envs[name], item["source"], words[name], {})
            request["id"] = f"{item['id']}:{item['variant']}:{index}"
            requests.append(request)
        executable = Path(os.environ.get("VE_ENGLISH_ROUTE", adapter.EXECUTABLE))
        answers = transport(executable, adapter.MODE, requests)
        if len(answers) != len(requests):
            raise CheckerUnavailable("CheckerUnavailable: the Lean reader returned the wrong number of rows")
        records = []
        for item, request, answer in zip(rows, requests, answers, strict=True):
            name, source = item["environment"], item["source"]
            env, word = envs[name], words[name]
            python = _attempt(lambda: _python_reading(env, source, word, {}))
            lean = _lean_result(answer, request["id"], env, source, word)
            # G3 compares the grammatical reading and conclusion marks. The
            # entailment proof runs after dispatch and is a separate gate; the
            # fixture environments need not supply its checker.
            reading = (SimpleNamespace(comparison=python.comparison, conclusion_error=lambda: None)
                       if not isinstance(python, BaseException) else python)
            comparison = adapter.shadow_record(env, source, word, reading, lean)
            records.append({**item, "record": comparison, "disposition": _disposition(item, comparison),
                            "independent": _independent_readers(env, source, word)})
    by_environment: dict[str, dict] = {}
    for name in envs:
        own = [r for r in records if r["environment"] == name]
        by_environment[name] = {"cases": len(own),
                                "agreement": sum(not r["record"]["classes"] for r in own),
                                "differences": sum(bool(r["record"]["classes"]) for r in own),
                                "lean_statuses": dict(sorted(Counter(r["record"]["lean"]["status"]
                                                             for r in own).items()))}
    return {"format": "ve.english-lean-s3-fixture-comparison@1",
            "scope": "spec fixtures: independent hand, Lark and Lean readers; no sealed or reverse corpus",
            "cases": len(records),
            "agreement": sum(not r["record"]["classes"] for r in records),
            "differences": sum(bool(r["record"]["classes"]) for r in records),
            "unexplained": sum(bool(r["record"]["classes"]) and r["disposition"] is None for r in records),
            "by_environment": by_environment, "rows": records}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output", type=Path, default=REPORT)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args(argv)
    result = compare()
    args.output.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({key: result[key] for key in ("cases", "agreement", "differences", "unexplained",
                                                    "by_environment")}))
    return 0 if args.report_only or result["unexplained"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
