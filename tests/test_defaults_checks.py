"""Every check of the defaults relay and of `--assume-no-exception` is needed by a test (review df-1b F1 and F9,
PROBE F1 and PROBE F9).

The checks are read from the source (tests/check_mutants.py): each `if ...: raise` of `ve/defaults.py`, and of
`ve/document/cli.py` where it is the flag's, weakened one sub-condition at a time or made always true; each
`if ...: return` (`answer`'s choice of binding, `ask`'s strict answer) with each sub-condition forced both ways; and
each helper check (`_tuple(...)`, `_situation(...)`, `check_row(...)`) deleted. Each seeded bug must fail one of the
both-sides tests, which read Lean's genuine rows asked once (tests/test_defaults_answer.py `_genuine`), so a check
written later is a seeded bug too and a check no fixture needs fails here.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from tests import check_mutants, test_defaults_lean
from tests.test_defaults_answer import BOTH_SIDES
from ve import defaults
from ve.document import cli

ROOT = Path(__file__).resolve().parents[1]
TESTS = (*BOTH_SIDES, test_defaults_lean.test_flag_refusals, test_defaults_lean.test_flag_asks_with_the_documents_norms_and_facts)


def _flag_check(function, node):
    return function == "_assume_no_exception" or "assume_no_exception" in ast.unparse(node.test)


def _defaults_functions():
    return {node.name for node in ast.parse((ROOT / "ve/defaults.py").read_text()).body
            if isinstance(node, ast.FunctionDef)}


# (module, its checks, the functions whose call statements are helper checks, the functions whose values feed checks)
TARGETS = ((defaults, lambda function, node: True, _defaults_functions(), lambda function: True),
           (cli, _flag_check, (), lambda function: function == "_assume_no_exception"))


def _fails(test):
    with pytest.MonkeyPatch.context() as patch:
        try:
            test(*[patch for _ in inspect.signature(test).parameters])  # each takes `monkeypatch` or nothing
        except KeyboardInterrupt:
            raise
        except BaseException:  # an assertion, `pytest.raises` unmet, or a crash: the seeded bug is found
            return True
    return False


def test_review_f1_every_check_is_needed_by_a_both_sides_test():
    assert [test.__name__ for test in TESTS if _fails(test)] == []  # control; asks Lean's genuine rows once
    survivors, count = [], 0
    for module, select, functions, feeding in TARGETS:
        path = Path(module.__file__)
        for function, description, tree in check_mutants.mutants(path.read_text(), str(path.relative_to(ROOT)),
                                                                  select, functions, feeding):
            count += 1
            namespace = {"__name__": module.__name__, "__package__": module.__package__, "__file__": str(path)}
            exec(compile(tree, str(path), "exec"), namespace)
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(module, function, namespace[function])
                if not any(_fails(test) for test in TESTS):
                    survivors.append(description)
    # the enumeration reaches every check and every value that feeds one (60 sites at review F1's fix, 93 with F9's
    # exits, 174 with F10's values)
    assert count >= 174
    assert survivors == [], "\n".join(survivors)


def test_review_f9_a_strict_answer_lean_rejected_is_never_shown():
    """PROBE F9's seeded bug: `ask` reading Lean's `valid` as `is not None` shows the strict answer for a certificate
    Lean rejected, which the both-sides test of the strict answer finds."""
    path = Path(defaults.__file__)
    source, site = path.read_text(), '["valid"] is True'
    assert source.count(site) == 1
    namespace = {"__name__": defaults.__name__, "__package__": defaults.__package__, "__file__": str(path)}
    exec(compile(source.replace(site, '["valid"] is not None'), str(path), "exec"), namespace)
    test = BOTH_SIDES[-1]
    assert test.__name__ == "test_strict_answer_only_when_lean_says_valid" and not _fails(test)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(defaults, "ask", namespace["ask"])
        assert _fails(test)
