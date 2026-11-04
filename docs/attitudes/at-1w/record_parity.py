"""Record `_infinitive` and `_finite` (`ve/report_english.py`) on every phrase the suite's
`reports@0` English cases reach: the parity table of AT-1w (docs/spec/attitudes-PLAN.md, AT-1w).

Usage::

    uv run python docs/attitudes/at-1w/record_parity.py CHECKOUT OUT.json --label REV

CHECKOUT is a checkout whose `ve/report_english.py` still has both functions (main before
AT-1w, with its `lean/` built). Each function is wrapped and every call is recorded while
pytest runs CHECKOUT's `tests/test_report_english.py` and `tests/test_reports.py`, the two
test files that reach `reports@0`'s English; `PROBES` and `FINITE_PROBES` are computed by the
same functions before the tests run. `tests/data/reports_wants_parity.json` is this
script run on `94580b39b`; `tests/test_reports_wants.py` checks Lean's `reports-wants` kind
against it, and `lean/VE/Attribution/Words.lean`'s `#guard`s repeat its rows.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

TESTS = ("tests/test_report_english.py", "tests/test_reports.py")
# Phrases no test reaches, one or more per branch of each function (the `not ` refusal, the
# `is/has/does` table, the `-ies`/`-es`/`-s` rules, a failed round trip, a head outside
# `[a-z]+`, the empty phrase, NBSP, CR, curly quotes, U+212A, a dotted I, NUL), and fixture C-e's phrase (spec 7.1); recorded apart.
PROBES = (
    'is classified as "mass_casualty_weapon_uplift"', "is", "has a key", "does work", "is not safe",
    "does not work", "is not", "is  safe", "Is safe", " is", "is\tsafe", "", "s", "be", "isnt",
    "carries x", "studies", "plays x", "says x", "passes x", "wishes", "watches", "fixes", "fizzes",
    "goes", "toes", "buses", "runs", "pass x", "boxs", "trys", "gos", "ies", "oes", "es", "zes", "sses",
    "yies", "aies", "eies", "iies", "oies", "uies", "bathes", "x1s", "dоes", "élèves",
    "is\u00a0safe", "is safe\r", "is \u201csafe\u201d", "\u212aeeps x", "\u0130s safe", "is\u0000",
)
FINITE_PROBES = (
    'be classified as "mass_casualty_weapon_uplift"', "be safe", "have a key", "do work", "be not safe",
    "try x", "play", "pass", "wish", "watch", "fix", "buzz", "go", "", " x", "Be safe", "y", "ay", "Ay",
    "1y", "é", "run fast", "key", "skiy", "toy", "buy", "bath", "be\u00a0safe", "be safe\r", "\u212aeep",
)


class Recorder:
    """A pytest plugin that wraps both functions before the tests run."""

    def __init__(self):
        self.infinitive, self.finite = {}, {}

    def pytest_sessionstart(self, session):
        import ve.report_english as module
        infinitive, finite = module._infinitive, module._finite

        def recorded_infinitive(phrase):
            self.infinitive[phrase] = infinitive(phrase)
            return self.infinitive[phrase]

        def recorded_finite(phrase):
            self.finite[phrase] = finite(phrase)
            return self.finite[phrase]

        module._infinitive, module._finite = recorded_infinitive, recorded_finite


def record(checkout: Path, label: str) -> dict:
    import pytest
    os.chdir(checkout)
    sys.path.insert(0, str(checkout))
    import ve.report_english as module
    probes = [[p, module._infinitive(p)] for p in PROBES]
    finite_probes = [[p, module._finite(p)] for p in FINITE_PROBES]
    recorder = Recorder()
    code = pytest.main(["-q", "-p", "no:cacheprovider", *TESTS], plugins=[recorder])
    if code != 0:
        raise SystemExit(f"the recorded tests failed (pytest exit {code})")
    return {"format": "reports-wants-parity@1", "checkout": label, "tests": list(TESTS),
            "infinitive": [[p, recorder.infinitive[p]] for p in sorted(recorder.infinitive)],
            "finite": [[p, recorder.finite[p]] for p in sorted(recorder.finite)],
            "infinitive_probes": probes, "finite_probes": finite_probes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("checkout", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    table = record(args.checkout.resolve(), args.label)
    out.write_text(json.dumps(table, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
