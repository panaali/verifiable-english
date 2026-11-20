"""fsf-repair-f3-safetycase-1119 (row F3): the governance finding's legend carries the Glossary's Safety Cases sentence.

The blocks f12-p, f12-u, f13-p and f13-u (rules.d1.ve) use the open-term predicate
`governance_found_acceptable_with_safety_case_where_ccl_reached` and never `safety_case`, so the Glossary definition
of a safety case reaches those blocks only through this predicate's legend (the carrier guard of
reviews/pathf-q3/flag-analysis-1119/converge-AB.md section 0: a vocabulary legend of a predicate the block uses).
"""
import importlib.util
import json
import re
from pathlib import Path

from tests.pinned_source import pinned_source

HERE = Path(__file__).resolve().parents[1] / "usecases" / "safety-framework"
GOV = "governance_found_acceptable_with_safety_case_where_ccl_reached"
F3_BLOCKS = ("f12-p", "f12-u", "f13-p", "f13-u")
# The pinned source's sentence (Glossary, fsf-3.1.txt line 20, unit g-safety-cases of spans.json). The test reads it from the source when the source is
# stored and checks that this copy is the same; the copy keeps the legend check running where the source is absent.
SENTENCE = ("Safety Cases: are an assessable argument showing how severe risks associated with a model's CCLs have "
            "been reduced to an acceptable level.")


def _quote_normal(text):
    """The quote normalisation of the pinned-source tests: whitespace runs collapse to one space, curly quotes become
    straight ones."""
    return " ".join(text.split()).translate(str.maketrans("‘’“”", "''\"\""))


def _vocabulary():
    """usecases/safety-framework/vocabulary.py, loaded under its own name (usecases/eligibility has bare-name twins)."""
    spec = importlib.util.spec_from_file_location("fsf_f3_vocabulary", HERE / "vocabulary.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source_sentence():
    path = pinned_source("safety-framework", skip=False)
    if path is None:
        return SENTENCE
    found = re.findall(r"Safety Cases: [^.]*\.", _quote_normal(path.read_text(encoding="utf-8")))
    assert found == [SENTENCE]
    return found[0]


def test_the_governance_legend_quotes_the_glossary_safety_case_sentence_whole():
    """Row F3: the GOV legend holds the Glossary sentence byte for byte (in quotes), in the vocabulary and in the
    committed environment.d1.json; the f12/f13 blocks use that predicate and not `safety_case`; the legend's subject,
    open term OT3 and decider are unchanged."""
    sentence = _source_sentence()
    vocabulary = _vocabulary()
    committed = json.loads((HERE / "environment.d1.json").read_text(encoding="utf-8"))
    legends = (vocabulary.environment()["vocabulary"]["predicates"][GOV]["description"],
               committed["vocabulary"]["predicates"][GOV]["description"])
    for legend in legends:
        assert f'"{sentence}"' in _quote_normal(legend)
        assert legend.startswith("the appropriate governance function has determined the residual risk of {0} ")
        assert legend.endswith(". Open term OT3, decided by the appropriate governance function (unnamed)")
    assert vocabulary.OPEN_PREDICATES[GOV] == "OT3"
    blocks = re.split(r"^## ", (HERE / "rules.d1.ve").read_text(encoding="utf-8"), flags=re.M)
    for block_id in F3_BLOCKS:
        [block] = [b for b in blocks if b.startswith(f"{block_id} |")]
        assert f'"{GOV}"' in block and '"safety_case"' not in block
