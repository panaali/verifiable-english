"""Optional smoke tests against constrained-decoding backend compilers.

Run these separately so xgrammar and llguidance remain optional dependencies::

    UV_CACHE_DIR=/private/tmp/ve-uv-cache-grammar \
      uv run --python 3.12 --with xgrammar==0.2.7 --with llguidance==1.8.0 \
      pytest -q tests/test_grammar_backends.py
"""

from __future__ import annotations

import json

import pytest

from test_grammar import MIXED_ENV
from conformance.order import environment as order_environment
from ve.grammar import export_grammar


def test_llguidance_compiles_lark_and_gbnf_exports():
    llguidance = pytest.importorskip("llguidance")

    compiled = 0
    for vocabulary in (MIXED_ENV, order_environment()):
        for dialect in ("lark", "gbnf"):
            for mode in ("full", "syntax"):
                for wrapper in (False, True):
                    grammar = export_grammar(
                        vocabulary,
                        dialect=dialect,
                        mode=mode,
                        max_binder_depth=2,
                        wrapper=wrapper,
                    )
                    definition = llguidance.grammar_from(dialect, grammar)
                    # An invalid or unsupported grammar raises ValueError. An empty
                    # result means validation succeeded without warnings.
                    assert llguidance.LLMatcher.validate_grammar(definition) == ""
                    compiled += 1

    assert compiled == 16


def _xgrammar_accepts(xgrammar, compiled, text: str) -> bool:
    matcher = xgrammar.GrammarMatcher(compiled, terminate_without_stop_token=True)
    return matcher.accept_string(text) and matcher.is_completed()


def test_xgrammar_compiles_and_matches_ebnf_exports():
    xgrammar = pytest.importorskip("xgrammar")
    tokenizer = xgrammar.TokenizerInfo([bytes([value]) for value in range(256)])
    compiler = xgrammar.GrammarCompiler(tokenizer)

    compiled = {}
    for vocabulary in (MIXED_ENV, order_environment()):
        for mode in ("full", "syntax"):
            for wrapper in (False, True):
                grammar = export_grammar(
                    vocabulary,
                    dialect="ebnf",
                    mode=mode,
                    max_binder_depth=2,
                    wrapper=wrapper,
                )
                compiled[vocabulary.order, mode, wrapper] = compiler.compile_grammar(grammar)
    assert len(compiled) == 8

    valid = "for every item x0, (x0 is marked).\n"
    wrong_sort = "for every place x0, (x0 is marked).\n"
    scope_leak = "(for every item x0, (true)) and (x0 is marked).\n"
    assert _xgrammar_accepts(xgrammar, compiled[False, "full", False], valid)
    assert not _xgrammar_accepts(xgrammar, compiled[False, "full", False], wrong_sort)
    assert not _xgrammar_accepts(xgrammar, compiled[False, "full", False], scope_leak)
    assert _xgrammar_accepts(xgrammar, compiled[False, "syntax", False], wrong_sort)
    assert _xgrammar_accepts(xgrammar, compiled[False, "syntax", False], scope_leak)

    wrapped = json.dumps(
        {"ve": "true.\n", "explanation": 'why "yes"; caf\N{LATIN SMALL LETTER E WITH ACUTE}; \N{GRINNING FACE}'},
        ensure_ascii=False,
    )
    reversed_keys = json.dumps({"explanation": "why", "ve": "true.\n"})
    assert _xgrammar_accepts(xgrammar, compiled[False, "full", True], wrapped)
    assert not _xgrammar_accepts(xgrammar, compiled[False, "full", True], reversed_keys)
    for mode in ("full", "syntax"):
        assert _xgrammar_accepts(xgrammar, compiled[True, mode, False], "[-99 * @n] < -99.\n")
        assert _xgrammar_accepts(xgrammar, compiled[True, mode, True],
                                 json.dumps({"ve": "[-20 * @n] < 0.\n", "explanation": "ok"}))
