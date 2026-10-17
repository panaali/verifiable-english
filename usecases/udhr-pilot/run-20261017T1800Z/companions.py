"""Candidate readings of the four audit-rejected units, each as its own checked document.

A reading set in a `ve-document@1` cannot hold norm content (a candidate's `content` must be a
formula), so each norm-kind candidate is elaborated here as a one-unit companion document whose
source is exactly the unit's bytes. The main translation cites each companion's meaning id.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

SPEC_REVISION = "ve-v0.2-expand2-2026-09-25"
UNSTATED = "unstated"


def sort(singular, plural, description):
    return {"description": description, "verbalisation": {"singular": singular, "plural": plural}}


def prohibition_predicate(arguments, description, act):
    """A permission-role predicate that only the unconditional rule below decides.

    The rule's guard is true for every tuple of the named sorts, so the completion
    `allow` is never consulted; `default_independence` in build.py checks that.
    """
    return {"arguments": arguments, "description": description,
            "regulated": {"role": "permission", "default": "allow", "act": act}}


def environment(profiles, sorts, predicates):
    return {"language": "ve.core@0.2", "profiles": sorted(profiles), "spec_revision": SPEC_REVISION,
            "vocabulary": {"constants": {}, "predicates": predicates, "sorts": sorts}}


def strict_rule(name, predicate, sign):
    return {"norm": {"guard": ["top"], "name": name, "over": [], "predicate": predicate,
                     "sign": sign, "unless": []}}


def default_rule(name, predicate, sign):
    rule = strict_rule(name, predicate, sign)
    rule["norm"].update(mode="default", exception={"decided_by": UNSTATED, "factors": [],
                                                    "necessary": [], "sufficient": []})
    return rule


BROTHERHOOD = {
    "human_being": sort("human being", "human beings", "a human being"),
}


def brotherhood_predicates():
    return {"act_in_brotherhood_required": {
        "arguments": ["human_being"],
        "description": "The human being is required to act towards each other human being in a spirit of brotherhood",
        "regulated": {"role": "obligation", "default": "deny",
                      "act": "{0} act towards each other human being in a spirit of brotherhood"}}}


COMPANIONS = {
    # unit -> candidate id -> (profiles, sorts, predicates, rule, open terms named by the unit)
    "u017": {
        "strict": (("documents@1", "norms@0", "relational-fol@0"), BROTHERHOOD, brotherhood_predicates(),
                   strict_rule("brotherhood-strict", "act_in_brotherhood_required", True),
                   ["spirit_of_brotherhood"]),
        "default": (("documents@1", "norms@0", "relational-fol@0", "soft-norms@0"), BROTHERHOOD,
                    brotherhood_predicates(),
                    default_rule("brotherhood-default", "act_in_brotherhood_required", True),
                    ["spirit_of_brotherhood"]),
    },
    "u052": {
        "invocation_barred": (
            ("documents@1", "norms@0", "relational-fol@0"),
            {"person": sort("person", "people", "a human person"),
             "excluded_prosecution": sort(
                "excluded prosecution", "excluded prosecutions",
                "a prosecution that genuinely arises from a non-political crime or from acts contrary to the "
                "purposes and principles of the United Nations")},
            {"invoke_asylum_right_in_case_permitted": prohibition_predicate(
                ["person", "excluded_prosecution"],
                "The person is permitted to invoke the right to seek and to enjoy asylum (Article 14, paragraph 1) "
                "in the case of the excluded prosecution",
                "{0} invoke the right to seek as well as enjoy asylum in the case of {1}")},
            strict_rule("asylum-not-invocable-in-the-case-of-such-prosecutions",
                        "invoke_asylum_right_in_case_permitted", False),
            ["genuine", "non_political_crime", "contrary_to_un_purposes_and_principles"]),
    },
    "u112": {
        "exercise_prohibited": (
            ("documents@1", "norms@0", "relational-fol@0"),
            {"contrary_exercise": sort(
                "contrary exercise", "contrary exercises",
                "an exercise by someone of a right or freedom set forth in this Declaration, carried out contrary to "
                "the purposes and principles of the United Nations")},
            {"contrary_exercise_permitted": prohibition_predicate(
                ["contrary_exercise"], "The contrary exercise is permitted to be carried out", "{0} be carried out")},
            strict_rule("no-exercise-contrary-to-un", "contrary_exercise_permitted", False),
            ["rights_and_freedoms_set_forth", "contrary_to_un_purposes_and_principles"]),
    },
    "u114": {
        "interpretive_ban": (
            ("documents@1", "norms@0", "relational-fol@0"),
            {"destructive_interpretation": sort(
                "destructive interpretation", "destructive interpretations",
                "an interpretation of this Declaration as implying, for any State, group or person, a right to "
                "engage in any activity or to perform any act aimed at the destruction of any of the rights and "
                "freedoms set forth in it")},
            {"destructive_interpretation_permitted": prohibition_predicate(
                ["destructive_interpretation"], "The destructive interpretation is permitted to be adopted",
                "{0} be adopted")},
            strict_rule("no-interpretation-implying-a-right-to-destroy-rights",
                        "destructive_interpretation_permitted", False),
            ["rights_and_freedoms_set_forth", "aimed_at_destruction_of_rights"]),
    },
}


def write_companion(directory: Path, unit_id: str, candidate: str, source: bytes, open_terms: list):
    profiles, sorts, predicates, rule, unit_open = COMPANIONS[unit_id][candidate]
    meta = {"format": "ve-document@1",
            "environment": environment(profiles, sorts, predicates),
            "open_terms": [copy.deepcopy(t) for t in open_terms if t["name"] in unit_open],
            "units": [{"content": rule, "id": f"{unit_id}_{candidate}", "kind": "norm",
                       "meaning": {"open": list(unit_open)}, "span": [0, len(source)],
                       "support": "none"}]}
    path = directory / f"{unit_id}.{candidate}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                     + b"\n---\n" + source)
    return path


def open_term(name, factors, decided_by=UNSTATED):
    """An open term the source leaves undecided; no necessary or sufficient condition is invented."""
    return {"arguments": [], "decided_by": decided_by, "factors": factors, "jurisdiction": "universal",
            "name": name, "necessary": [], "precedents": [], "sufficient": [], "version": 1}


NEW_OPEN_TERMS = [
    open_term("contrary_to_un_purposes_and_principles",
              ["which purposes and principles count", "what makes an act contrary to them"]),
    open_term("non_political_crime",
              ["what separates a political from a non-political crime", "who classifies the crime"]),
    open_term("rights_and_freedoms_set_forth",
              ["which items of the Declaration count as rights and freedoms"]),
    open_term("aimed_at_destruction_of_rights",
              ["what it is to aim at the destruction of a right", "whether purpose or effect decides"]),
]
