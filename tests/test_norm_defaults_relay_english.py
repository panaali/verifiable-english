"""The English display works on the Lean accepted norm-defaults container."""
from types import SimpleNamespace

from tests.test_norm_defaults import (CSAM_RULE, CSAM_SITUATION, ONE_ACT, csam, environment, latent,
                                      obligation, permission, rule)
from ve import norm_defaults_english as english
from ve.norm_defaults import UnspecifiedDocument, report
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


def test_relay_renders_reachable_gap_report_lines():
    for completion, expected in (
        ("unspecified", "The text does not say whether Sol may generate child sexual abuse material: "
                        "no rule decides this situation."),
        ("deny", "No rule decides whether Sol may generate child sexual abuse material; "
                 "the default decides that Sol must not generate child sexual abuse material."),
        ("allow", "No rule decides whether Sol may generate child sexual abuse material; "
                  "the default decides that Sol may generate child sexual abuse material."),
    ):
        document = UnspecifiedDocument(csam(completion), [CSAM_RULE])
        situation = FiniteModel.from_dict(document.situation_environment(), CSAM_SITUATION)
        line = report(document, model=situation)["report"][0]
        assert line["reached"] == "reachable" and isinstance(line["witness"], dict)
        assert english.gap_sentence(document, situation, line) == expected


def test_relay_renders_latent_conflict_verdict_and_finding():
    frozen = latent("unspecified")
    document = UnspecifiedDocument(frozen.env, frozen.author.rules)
    situation = FiniteModel.from_dict(document.situation_environment(), ONE_ACT)
    filled = document.with_filling(situation, {"unsaid__y_permitted": frozenset({("a",)})})
    verdict = run_case(source_case(document, "norm-defaults-conflict", witness={
        "target": "x_required->x_permitted", "model": filled.to_dict(), "tuple": ["a"]}))
    assert verdict["verdict"] == "CONFLICT"
    assert english.latent_conflict_sentence(document, situation, verdict) == (
        "Rules 1 and 2 contradict each other if a may be tried, and the text does not say whether a may be "
        "tried. To settle it, add a rule about whether a may be tried, or add a condition to one of the rules.")
    assert english.latent_conflict_finding(document, situation, verdict) == (
        "LatentConflict: must-x, not-x under y_permitted(a) = yes")
