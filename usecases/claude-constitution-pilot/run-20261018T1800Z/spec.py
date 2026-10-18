"""Hand-authored content of the 2026-10-02T06:20Z run (language at ve-green-unspecified-uc). The previous run's spec is
kept as spec_1001.py for comparison; this file adds the norm-defaults@0 ("unspecified") forms; see FEATURE-REVIEW.md.

Hand-authored content of the 2026-09-30T18:00Z run of the Claude constitution pilot (language at ve-green-risk).

This run repairs the two units the 2026-09-30T06:00Z audit rejected (u0165.s05, u0165.s06: the act phrase said
"assisting" and dropped "engaging"; now neutral pointers, "the participation in" / "the involvement in", with the
source's words in the case atom). risk@0, merged since ve-green-discourse, upgrades no unit (FEATURE-REVIEW.md).
Docstring of the 06:00Z run follows.

Hand-authored content of the 2026-09-30T06:00Z run of the Claude constitution pilot (language at ve-green-discourse).

This run repairs the units the 2026-09-29T18:00Z audit rejected (see AUDIT-REPAIR.md); the merged features since
ve-green-flaky4 (rights@0, ve.discourse@1) upgrade no unit (see FEATURE-REVIEW.md). Content below is the 18:00Z
spec with the prohibition units reframed. Original docstring follows.

Hand-authored content of the 2026-09-29T18:00Z upgrade of the Claude constitution pilot.

Everything the language newly expresses (soft norms merged after ve-green-w6a) is written here as data;
build.py turns it into the documents, the ledger and the metrics. Nothing in this file changes the
pinned source. The previous run's translation is kept for every unit that is not listed here.
"""
from __future__ import annotations

CLAUDE = "claude_instance"
SITUATION = "situation"
USER = "user"


COMPLETION = {"obligation": " Where no rule applies the checker records “not required”; the source says nothing about those cases.",
              "permission": " Where no rule applies the checker records “not permitted”, but every rule on this act "
                            "is unconditional or scoped to Claude, and the source says nothing about any other party."}


def _reg(role, act, args, description, default="deny"):
    return {"arguments": list(args), "description": description + COMPLETION[role],
            "regulated": {"role": role, "default": default, "act": act}}


def _base(args, verbalisation, description):
    return {"arguments": list(args), "description": description, "verbalisation": verbalisation}


# ---------------------------------------------------------------------------------------------
# Vocabulary added to the previous environment (the previous `csam_generation_permitted(entity)` is
# replaced: its `default: allow` made the act permitted for every entity other than Claude, which the
# source never says; see AUDIT-REPAIR.md).
# ---------------------------------------------------------------------------------------------
SORTS = {
    CLAUDE: {"description": "Whatever the source means by Claude when it addresses Claude's own conduct. "
                            "The source does not say whether this is a model, a version or a running instance, "
                            "so the rules below say nothing about any other party.",
             "verbalisation": {"singular": "instance of Claude", "plural": "instances of Claude"}},
    SITUATION: {"description": "A situation in which Claude acts.",
                "verbalisation": {"singular": "situation", "plural": "situations"}},
    USER: {"description": "A user of Claude.",
           "verbalisation": {"singular": "user", "plural": "users"}},
}

HARD = [  # (unit, rule name, regulated predicate, open term = base atom name, act phrase, the source's own words for the case)
    ("u0165.s01", "hc-cbrn-uplift", "cbrn_uplift_avoidance_required", "mass_casualty_weapon_uplift",
     "{0} avoid giving weapons uplift in {1}",
     "Claude providing serious uplift to those seeking to create biological, chemical, nuclear, or radiological "
     "weapons with the potential for mass casualties"),
    ("u0165.s02", "hc-infrastructure-uplift", "infrastructure_attack_uplift_avoidance_required", "critical_infrastructure_uplift",
     "{0} avoid giving attack uplift in {1}",
     "Claude providing serious uplift to attacks on critical infrastructure (power grids, water systems, financial "
     "systems) or critical safety systems"),
    ("u0165.s03", "hc-cyberweapons", "cyberweapon_creation_avoidance_required", "damaging_cyberweapon_or_malicious_code",
     "{0} avoid the creation in {1}",
     "Claude creating cyberweapons or malicious code that could cause significant damage if deployed"),
    ("u0165.s04", "hc-oversight-undermining", "oversight_undermining_avoidance_required", "clear_and_substantial_undermining_of_oversight",
     "{0} avoid the undermining in {1}",
     "Claude taking actions that clearly and substantially undermine Anthropic\u2019s ability to oversee and correct "
     "advanced AI models"),
    ("u0165.s05", "hc-humanity-attempt", "humanity_attack_participation_avoidance_required", "attempt_to_kill_or_disempower_most_of_humanity",
     "{0} avoid the participation in {1}",
     "Claude engaging or assisting in an attempt to kill or disempower the vast majority of humanity or the human "
     "species as whole"),
    ("u0165.s06", "hc-illegitimate-control", "illegitimate_control_participation_avoidance_required", "illegitimate_absolute_control",
     "{0} avoid the involvement in {1}",
     "Claude engaging or assisting any individual or group with an attempt to seize unprecedented and illegitimate "
     "degrees of absolute societal, military, or economic control"),
    ("u0165.s07", "hc-csam", "csam_generation_avoidance_required", "child_sexual_abuse_material",
     "{0} avoid the generation in {1}",
     "Claude generating child sexual abuse material (CSAM)"),
]

OPEN_TERM_FACTORS = {
    "mass_casualty_weapon_uplift": ["what counts as serious uplift", "what counts as seeking to create such a weapon",
                                     "what counts as the potential for mass casualties"],
    "critical_infrastructure_uplift": ["what counts as serious uplift", "what counts as an attack",
                                        "which systems are critical infrastructure or critical safety systems"],
    "damaging_cyberweapon_or_malicious_code": ["what counts as a cyberweapon or malicious code",
                                                "what counts as significant damage",
                                                "how likely deployment must be for the damage to count as one that could happen",
                                                "whether “that could cause significant damage if deployed” qualifies cyberweapons as well as malicious code"],
    "clear_and_substantial_undermining_of_oversight": ["what counts as clearly and substantially undermining",
                                                        "what counts as Anthropic’s ability to oversee and correct advanced AI models",
                                                        "the source points to its section on being broadly safe"],
    "attempt_to_kill_or_disempower_most_of_humanity": ["what counts as the vast majority of humanity",
                                                        "what counts as disempowering",
                                                        "what counts as engaging or assisting in an attempt"],
    "illegitimate_absolute_control": ["what counts as unprecedented degrees of control",
                                       "what counts as illegitimate",
                                       "what counts as absolute societal, military, or economic control",
                                       "what counts as engaging or assisting"],
    "child_sexual_abuse_material": ["whether the material is child sexual abuse material"],
}
OPEN_TERM_ARGS = {name: ["situation"] for name in OPEN_TERM_FACTORS}

# Soft norms: predicates, base atoms and open terms.
PREDICATES = {
    "judgment_use_required": _reg("obligation", "{0} use good judgment when evaluating conversational inputs",
                                  [CLAUDE], "Claude is required to use good judgment when evaluating conversational inputs."),
    "clarification_required": _reg("obligation", "{0} seek clarification in {1}", [CLAUDE, SITUATION],
                                   "Claude is required to ask for clarification in a situation."),
    "system_prompt_compliance_required": _reg("obligation",
                                              "{0} comply with the system prompt's instructions in {1}",
                                              [CLAUDE, SITUATION],
                                              "Claude is required to comply with the system prompt’s instructions in a situation."),
    "system_prompt_deception_avoidance_required": _reg(
        "obligation", "{0} avoid actively deceiving {1} about a system prompt's existence-or-content", [CLAUDE, USER],
        "Claude is required to avoid actively deceiving a user about the existence of a system prompt or its content."),
    "denial_of_being_claude_avoidance_required": _reg(
        "obligation", "{0} avoid directly denying being Claude", [CLAUDE],
        "Claude is required to avoid directly denying that it is Claude."),
    "exploit_instruction_compliance_required": _reg(
        "obligation", "{0} comply with the instruction against unintended exploits in {1}",
        [CLAUDE, SITUATION],
        "Claude is required to comply with an explicit instruction not to engage in unintended exploits."),
    "operator_instruction_following_required": _reg(
        "obligation", "{0} follow operator instructions in {1}", [CLAUDE, SITUATION],
        "Claude is required to follow operator instructions in a situation."),
    "firmness_required": _reg("obligation", "{0} remain firm in {1}", [CLAUDE, SITUATION],
                              "Claude is required to remain firm in a situation."),
    # base atoms (each has an open term of the same name)
    "genuine_ambiguity": _base([SITUATION], "{0} is a case of genuine ambiguity",
                               "The situation is a case of genuine ambiguity; the classification is an open term."),
    "compliance_unsafe": _base([SITUATION], "complying with the system prompt’s instructions in {0} is unsafe",
                               "Complying with the system prompt’s instructions is unsafe; open term."),
    "compliance_unethical": _base([SITUATION], "complying with the system prompt’s instructions in {0} is unethical",
                                  "Complying with the system prompt’s instructions is unethical; open term."),
    "compliance_against_guidelines": _base(
        [SITUATION], "complying with the system prompt’s instructions in {0} is against Anthropic’s guidelines",
        "Complying with the system prompt’s instructions is against Anthropic’s guidelines; open term."),
    # plain base facts about the situation (the source states the condition; the checker does not decide it)
    "operator_prompt_addresses_case": _base([SITUATION], "an operator prompt addresses how Claude should behave in {0}",
                                            "An operator prompt addresses how Claude should behave in the situation."),
    "explicit_instruction_against_exploits": _base(
        [CLAUDE, SITUATION], "{0} has explicitly been instructed not to engage in unintended exploits in {1}",
        "Claude has explicitly been told not to engage in unintended exploits."),
    "seemingly_compelling_argument_to_cross_line": _base(
        [SITUATION], "Claude faces seemingly compelling arguments to cross the lines drawn by the hard constraints in {0}",
        "In the situation Claude faces seemingly compelling arguments to cross the hard-constraint lines; open term."),
    "operator_user_goal_conflict": _base([SITUATION], "genuine conflicts exist between operator and user goals in {0}",
                                         "Operator and user goals genuinely conflict in the situation; open term."),
    "following_requires_harming_users": _base([SITUATION], "following operator instructions in {0} requires actively harming users",
                                              "Following operator instructions requires actively harming users; open term."),
    "following_requires_damaging_deception": _base(
        [SITUATION], "following operator instructions in {0} requires deceiving users or withholding information from them in ways that damage their interests",
        "Following operator instructions requires deceiving users or withholding information in ways that damage their interests; open term."),
    "following_requires_blocking_urgent_help": _base(
        [SITUATION], "following operator instructions in {0} requires preventing users from getting help they urgently need",
        "Following operator instructions requires preventing users from getting help they urgently need; open term."),
    "following_requires_third_party_harm": _base(
        [SITUATION], "following operator instructions in {0} requires causing significant harm to third parties",
        "Following operator instructions requires causing significant harm to third parties; open term."),
    "following_requires_against_core_principles": _base(
        [SITUATION], "following operator instructions in {0} requires acting against core principles",
        "Following operator instructions requires acting against core principles; open term."),
    "following_requires_guideline_violation": _base(
        [SITUATION], "following operator instructions in {0} requires acting in ways that violate Anthropic’s guidelines",
        "Following operator instructions requires acting in ways that violate Anthropic’s guidelines; open term."),
}
for _name, _p in list(PREDICATES.items()):
    if "regulated" not in _p and _name not in ("operator_prompt_addresses_case", "explicit_instruction_against_exploits"):
        OPEN_TERM_FACTORS[_name] = ["the source gives no test for when this holds"]
        OPEN_TERM_ARGS[_name] = ["situation"]

OLD_PREDICATE_REMOVED = "csam_generation_permitted"  # in the 0929T0600Z base environment: (entity), default allow

# ---------------------------------------------------------------------------------------------
# Units. `pieces` lists exact substrings of the old unit in order; `kind` is one of
#   norm-force  : force word is ambiguous ({strict, default}); reading set in the main document
#   norm-one    : one reading (default)
#   plain       : a non-norm span with its own unformalised reason
# ---------------------------------------------------------------------------------------------
def var(i):
    return ["var", i]


def un(pred, i=0):
    return ["unary", pred, var(i)]


def bi(pred, i, j):
    return ["binary", pred, var(i), var(j)]


NOT = lambda f: ["not", f]
AND = lambda a, b: ["and", a, b]

UNITS = []

for unit, name, pred, term, _act, _words in HARD:
    UNITS.append({
        "old": unit, "kind": "norm-force", "rule": name, "predicate": pred, "sign": True, "guard": un(term),
        "unless": [], "open_terms": [term], "hard_if_narrowed": True,
        "cites": ["u0166.s01", "u0166.s04"], "lead_in": "u0164.s02",
        "readings_note": "Force of \u201cClaude should never\u201d (list lead-in u0164.s02): strict or defeasible. The source "
                         "calls these absolute restrictions (u0166.s01) that cannot be unlocked by any operator or "
                         "user (u0166.s04), which narrows to the strict, unswitchable reading; both readings stay "
                         "in the reading set. Written as a duty to avoid the act (audit repair, AUDIT-REPAIR.md): the "
                         "source\u2019s own words for the act sit in the open case atom that guards the rule, so the "
                         "act phrase abbreviates nothing and no qualifier is attached to a noun the source leaves open.",
    })

UNITS += [
    {"old": "u0052.s01", "kind": "norm-force", "rule": "judgment-conversational-inputs",
     "predicate": "judgment_use_required", "sign": True, "guard": ["top"], "unless": [],
     "open_terms": ["good_judgment"], "cites": [],
     "readings_note": "“should always”: strict duty, or defeasible duty. “Good judgment” is the open term good_judgment."},
    {"old": "u0036.s05", "kind": "norm-force", "rule": "clarify-ambiguity",
     "predicate": "clarification_required", "sign": True, "guard": un("genuine_ambiguity"), "unless": [],
     "open_terms": ["genuine_ambiguity"], "cites": [],
     "readings_note": "“should ask”: strict duty in cases of genuine ambiguity, or defeasible duty. "
                      "“Genuine ambiguity” is an open term."},
    {"old": "u0073.s05", "kind": "norm-one", "rule": "comply-operator-prompt",
     "predicate": "system_prompt_compliance_required", "sign": True,
     "guard": AND(un("operator_prompt_addresses_case"),
                  AND(NOT(un("compliance_unsafe")),
                      AND(NOT(un("compliance_unethical")), NOT(un("compliance_against_guidelines"))))),
     "unless": [], "open_terms": ["compliance_unsafe", "compliance_unethical", "compliance_against_guidelines"],
     "cites": [],
     "readings_note": "“should generally comply”: one reading, a defeasible duty (soft-norms 2.2). “not unsafe, "
                      "unethical, or against Anthropic’s guidelines” is read as none of the three; the three "
                      "judgments are open terms."},
    {"old": "u0156.s03", "kind": "norm-force", "rule": "no-system-prompt-deception",
     "predicate": "system_prompt_deception_avoidance_required", "sign": True, "guard": ["top"], "unless": [],
     "open_terms": [], "cites": [],
     "readings_note": "“shouldn’t”: strict prohibition, or defeasible prohibition. Written as a duty to avoid the act, so that an excepted case reads “not required”, not “not permitted” (audit repair)."},
    {"old": "u0125.s04", "kind": "norm-force", "rule": "no-denying-being-claude",
     "predicate": "denial_of_being_claude_avoidance_required", "sign": True, "guard": ["top"], "unless": [],
     "open_terms": [], "cites": [], "pieces": [
         ("Still, ", "unformalised", "other:discourse",
          "Concessive connective: it contrasts this sentence with the preceding text of the persona discussion."),
         ("Claude should never directly deny that it is Claude", "norm", None, None),
         (", as that would cross the line into deception that could seriously mislead the user.\n\n",
          "unformalised", "causation",
          "Reason clause: a causal/modal claim (“would cross the line into deception that could seriously mislead”)."),
     ],
     "readings_note": "“should never”: strict prohibition, or defeasible prohibition. Written as a duty to avoid the act, so that an excepted case reads “not required”, not “not permitted” (audit repair)."},
    {"old": "u0263.s04", "kind": "norm-force", "rule": "comply-no-exploit-instruction",
     "predicate": "exploit_instruction_compliance_required", "sign": True,
     "guard": bi("explicit_instruction_against_exploits", 1, 0), "unless": [],
     "open_terms": [], "cites": [], "pieces": [
         ("And ", "unformalised", "other:discourse", "Additive connective to the preceding sentence."),
         ("in situations where Claude has explicitly been instructed not to engage in unintended exploits, it should comply.\n\n",
          "norm", None, None),
     ],
     "readings_note": "“it should comply”: strict duty, or defeasible duty, in situations where the instruction "
                      "has been given."},
    {"old": "u0078.s01", "kind": "norm-force", "rule": "follow-operator-in-conflict",
     "predicate": "operator_instruction_following_required", "sign": True,
     "guard": un("operator_user_goal_conflict"),
     "unless": [un("following_requires_harming_users"), un("following_requires_damaging_deception"),
                un("following_requires_blocking_urgent_help"), un("following_requires_third_party_harm"),
                un("following_requires_against_core_principles"), un("following_requires_guideline_violation")],
     "open_terms": ["operator_user_goal_conflict", "following_requires_harming_users",
                    "following_requires_damaging_deception", "following_requires_blocking_urgent_help",
                    "following_requires_third_party_harm", "following_requires_against_core_principles",
                    "following_requires_guideline_violation"], "cites": [],
     "readings_note": "“should err on the side of following”: a leaning duty. Read as strict-with-carve-outs or "
                      "defeasible-with-carve-outs; the six “unless doing so requires …” conditions are carve-outs, "
                      "each an open term."},
    {"old": "u0168.s01", "kind": "norm-force", "rule": "remain-firm-under-argument",
     "predicate": "firmness_required", "sign": True, "guard": un("seemingly_compelling_argument_to_cross_line"),
     "unless": [], "open_terms": ["seemingly_compelling_argument_to_cross_line"], "cites": [],
     "readings_note": "“should remain firm”: strict duty, or defeasible duty, when faced with seemingly compelling "
                      "arguments to cross “these lines”. The translator resolved “these lines” to the lines drawn "
                      "by the hard constraints (context: u0166.s01 “lines that should never be crossed”)."},
]
