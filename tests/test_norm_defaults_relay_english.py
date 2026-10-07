"""The English display works on the Lean accepted norm-defaults container."""
from types import SimpleNamespace

from tests.test_norm_defaults import (CSAM_RULE, CSAM_SITUATION, ONE_ACT, csam, environment, obligation,
                                      permission, rule)
from ve import norm_defaults_english as english
from ve.norm_defaults import UnspecifiedDocument
from ve.norm_defaults_route import run_case, source_case
from ve.model import FiniteModel


def _sentence(document, raw, predicate, values):
    situation = FiniteModel.from_dict(document.situation_environment(), raw)
    answer = run_case(source_case(document, "norm-defaults-status", model=situation.to_dict(),
                                  predicate=predicate, tuple=list(values), method="enumerate"))
    assert answer["point_status"].startswith("SETTLED ")
    status = SimpleNamespace(predicate=predicate, values=values, status="SETTLED",
                             value=answer["point_status"] == "SETTLED yes")
    return english.status_sentence(document, situation, status)


def test_relay_renders_selected_author_rule_and_silence():
    document = UnspecifiedDocument(csam("unspecified"), [CSAM_RULE])
    assert _sentence(document, CSAM_SITUATION, "csam_generation_permitted", ("claude0",)) == (
        "The text says Claude must not generate child sexual abuse material (rule 1).")
    assert english.silence_sentence(document, "csam_generation_permitted") == (
        "the text does not say whether an agent other than Claude may generate child sexual abuse material")


def test_relay_renders_pair_inheritance_from_lean_status():
    env = environment({"x_required": obligation("deny"), "x_permitted": permission("unspecified")})
    document = UnspecifiedDocument(env, [rule("must", "x_required", True)])
    assert _sentence(document, ONE_ACT, "x_permitted", ("a",)) == (
        "A may be done: rule 1 requires it, and whatever must be done may be done.")
