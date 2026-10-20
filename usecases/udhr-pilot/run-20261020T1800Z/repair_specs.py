"""Repaired candidates of the nine units the 2026-10-04T0600Z audit rejected (or that share a rejected unit's sentence).

The audit (AUDIT.md of run-20261004T0600Z) rejected u022a, u022c, u046, u054, u087, u098 and u099b. Its reasons and the repairs:

* u022a, u022c (and u022b, the same sentence): candidates replaced the unspecified responsibility with duties on every State
  or on every State, group and person, and no reading combined protection with noninterference. Repaired: the universal
  positive duty (anyone_positive) is gone, a plain entitlement candidate leaves the bearer unspecified, and a State candidate
  combines noninterference with protection in one act phrase.
* u046: "such interference or attacks" was unresolved. Repaired: the case sort's own definition carries the antecedent
  (arbitrary interference with privacy, family, home or correspondence; attacks upon honour or reputation), with a second scope
  where 'such' names the domains only.
* u054: the claim depended on the open relation owes_nationality_to (empty = no entitlement), and the permission-only liberty
  weakened the entitlement. Repaired: one candidate, a plain categorical entitlement of every person; claim and liberty removed.
* u087: the purpose clause was missing and the positive candidates required actual formation. Repaired: the purpose is in every act
  phrase, the positive candidate secures the opportunity (State only), the plain entitlement leaves the bearer open.
* u098: the age gate was invented and the parent/guardian responsibility was only a note. Repaired: no gate; a person candidate
  without a gate, a parent-or-guardian candidate, the State candidate.
* u099b (and u099a, the same sentence): the 'anyone' candidate gave every person and group a universal individual duty the passive
  does not assign; removed, the State candidate stays.
"""
from __future__ import annotations

import udhr_specs as U
from udhr_specs import (AND, OR, PERSON, STATE, V0, Top, ast, base, case_bases, case_sort, data, duty, liberty, norm, regulated,
                        sort)

REPAIRED = ["u022a", "u022b", "u022c", "u046", "u054", "u087", "u098", "u099a", "u099b"]
CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}
UNSPEC = U.UNSPEC


def add(unit, cid, spec, why):
    CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


def entitlement(unit, cid, stem, verbalisation, desc, opens, case=None):
    """A plain regulated predicate (norms 3.1, role plain, completion 'unspecified') that the rule makes true of every holder.

    It states the entitlement itself and names no bearer, so nothing about who must do what is invented, and no open
    relation can empty it."""
    if case is None:
        sorts = {"person": PERSON}
        args, predicates, guard, var = ["person"], {}, Top(), V0
    else:
        sorts = {case["name"]: case["sort"]}
        args, predicates, guard, var = [case["name"]], case_bases(case), ast(case["guard"], V0, V0), V0
    predicates[stem] = {"arguments": args, "description": desc, "verbalisation": verbalisation,
                        "regulated": {"role": "plain", "default": "unspecified"}}
    spec = dict(sorts=sorts, predicates=predicates, rule=norm(U.slug(f"{unit}-{cid}"), stem, True, guard), open=list(opens),
                soft=False)
    if case is None:
        spec["witnesses"] = [({"person": ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]
    else:
        elems = [f"c{i}" for i in range(len(case["examples"]))]
        rels = {n: [[e] for e, t in zip(elems, case["examples"]) if n in t] for n in case["bases"]}
        checks = [(stem, (e,), ("SETTLED", True) if U.holds(case["guard"], set(), set(t)) else ("UNDECIDED", None))
                  for e, t in zip(elems, case["examples"])]
        spec["witnesses"] = [({case["name"]: elems}, rels, checks)]
    return spec


# ---- Article 3: u022a, u022b, u022c ---------------------------------------------------------------------------------
LIFE = {
    "u022a": ("the right to life", "avoid_life_required", "{0} avoid depriving {1} of life",
              "{0} avoid depriving {1} of life as well as protect it", "secure_life_required", "{0} protect the life of {1}",
              "has_the_right_to_life", "{0} has the right to life", "The person has the right to life"),
    "u022b": ("the right to liberty", "avoid_liberty_required", "{0} avoid depriving {1} of liberty",
              "{0} avoid depriving {1} of liberty as well as secure it", "secure_liberty_required",
              "{0} secure the liberty of {1}", "has_the_right_to_liberty", "{0} has the right to liberty",
              "The person has the right to liberty"),
    "u022c": ("the right to security of person", "avoid_security_of_person_required",
              "{0} avoid endangering the security of the person of {1}",
              "{0} avoid endangering as well as safeguard the security of the person of {1}",
              "secure_security_of_person_required", "{0} safeguard the security of the person of {1}",
              "has_the_right_to_security_of_person", "{0} has the right to security of person",
              "The person has the right to security of person"),
}
for _uid, (_text, _nstem, _nact, _cact, _pstem, _pact, _estem, _everb, _edesc) in LIFE.items():
    add(_uid, "entitlement",
        entitlement(_uid, "entitlement", _estem, _everb, _edesc, []),
        f"Entitlement reading of {_text}: every person has it, and the source names no one who must do anything, so the "
        "candidate names no bearer (a plain regulated predicate the rule makes true of every person). The responsibility stays unspecified.")
    for _b, _who in (("state", "every State"), ("anyone", "every State, group and person")):
        add(_uid, f"{_b}_negative",
            duty(_uid, f"{_b}_negative", _nstem, _nact, f"The bearer is required to {_nact[len('{0} '):].replace('{1}', 'the person')}",
                 bearer=_b, arity="person", opens=[]),
            f"Claim reading of {_text} as noninterference: {_who} must {_nact[len('{0} '):].replace('{1}', 'each holder')}; "
            "the source names no bearer, so this is the translator's candidate.")
    add(_uid, "state_positive",
        duty(_uid, "state_positive", _pstem, _pact, f"The bearer is required to {_pact[len('{0} '):].replace('{1}', 'the person')}",
             bearer="state", arity="person", opens=[]),
        f"Claim reading of {_text} as protection: every State must {_pact[len('{0} '):].replace('{1}', 'each holder')}. Only States "
        "carry the positive duty; a universal duty of every State, group and person to protect would strengthen the source.")
    _cstem = _nstem.replace("avoid_", "avoid_and_secure_")
    add(_uid, "state_combined",
        duty(_uid, "state_combined", _cstem, _cact, f"The bearer is required to {_cact[len('{0} '):].replace('{1}', 'the person')}",
             bearer="state", arity="person", opens=[]),
        f"Claim reading of {_text} combining noninterference with protection: every State must {_cact[len('{0} '):].replace('{1}', 'each holder')} "
        "(one act phrase, so the combination is one duty).")

# ---- Article 12: u046 ---------------------------------------------------------------------------------------------------
_INTERFERENCE = OR(("p", "concerns_privacy"), ("p", "concerns_family"), ("p", "concerns_home"), ("p", "concerns_correspondence"))
_ATTACK = OR(("p", "is_attack_upon_honour"), ("p", "is_attack_upon_reputation"))
_U046_BASES = {
    "concerns_privacy": "The intrusion is an interference with the privacy of the person",
    "concerns_family": "The intrusion is an interference with the family of the person",
    "concerns_home": "The intrusion is an interference with the home of the person",
    "concerns_correspondence": "The intrusion is an interference with the correspondence of the person",
    "is_arbitrary": "The intrusion is arbitrary",
    "is_attack_upon_honour": "The intrusion is an attack upon the honour of the person",
    "is_attack_upon_reputation": "The intrusion is an attack upon the reputation of the person"}
_U046_EX = [["concerns_privacy", "is_arbitrary"], ["concerns_family", "is_arbitrary"], ["concerns_home", "is_arbitrary"],
            ["concerns_correspondence", "is_arbitrary"], ["concerns_home"], ["is_arbitrary"], ["is_attack_upon_honour"],
            ["is_attack_upon_reputation"]]
for _scope, _guard, _text in (
        ("arbitrary", OR(AND(_INTERFERENCE, ("p", "is_arbitrary")), _ATTACK),
         "'such interference' is the arbitrary interference with privacy, family, home or correspondence that the preceding "
         "sentence names (arbitrariness included), and 'attacks' are the attacks upon honour or reputation named there"),
        ("any", OR(_INTERFERENCE, _ATTACK),
         "'such interference' names only the four domains of the preceding sentence (privacy, family, home, correspondence), "
         "whether arbitrary or not, and 'attacks' are the attacks upon honour or reputation named there")):
    case = case_sort(
        "intrusion", "intrusions",
        "one interference with the privacy, family, home or correspondence of one person, or one attack upon the honour or "
        "reputation of one person: the interference and the attacks named in the preceding sentence of Article 12",
        _U046_BASES, _guard, _U046_EX)
    add("u046", f"state_{_scope}",
        duty("u046", f"state_{_scope}", "protect_by_law_against_intrusion_required", "{0} protect by law against {1}",
             "The bearer is required to protect the person by law against the intrusion", bearer="state", arity="case", case=case,
             opens=["arbitrary"]),
        f"Article 12 second sentence: every State must protect each person by law against such interference or attacks; {_text}. "
        "The protection of the law is the State's (a universal duty of every person and group to give it would strengthen the source).")
    add("u046", f"entitlement_{_scope}",
        entitlement("u046", f"entitlement_{_scope}", "is_protected_by_law", "{0} is protected by law",
                    "The intrusion is one against which the law protects the person", ["arbitrary"], case=case),
        f"Entitlement reading of the right to the protection of the law: against each intrusion in scope the person is entitled to "
        f"it; {_text}. No bearer is named.")

# ---- Article 15(1): u054 ----------------------------------------------------------------------------------------------
add("u054", "entitlement",
    entitlement("u054", "entitlement", "is_entitled_to_a_nationality", "{0} is entitled to a nationality",
                "The person is entitled to a nationality; who, if anyone, must grant it is the open term "
                "bearer_of_the_nationality_duty", ["bearer_of_the_nationality_duty"]),
    "Article 15(1) as a categorical entitlement of every person (a plain regulated predicate the rule makes true of every person). "
    "No bearer is named and no open relation can empty the entitlement; the right is not read as already fulfilled, and the person "
    "is not obliged to accept a nationality. Removed after the audit: the claim guarded by owes_nationality_to (it could leave "
    "everyone without the entitlement) and the permission-only liberty (it weakens an entitlement to a permission).")

# ---- Article 23(4): u087 -----------------------------------------------------------------------------------------------
_PURPOSE = "to protect their interests"
_U087 = {
    "negative": ("avoid_trade_unions_required", "{0} leave {1} free to form as well as join trade unions to protect interests"),
    "positive": ("secure_trade_unions_required", "{0} enable {1} to form as well as join trade unions " + _PURPOSE),
}
for _b, _who in (("state", "every State"), ("anyone", "every State, group and person")):
    _stem, _act = _U087["negative"]
    add("u087", f"{_b}_negative",
        duty("u087", f"{_b}_negative", _stem, _act, f"The bearer is required to {_act[len('{0} '):].replace('{1}', 'the person')}",
             bearer=_b, arity="person", opens=[]),
        f"Claim reading of the right to form and to join trade unions for the protection of one's interests as noninterference: "
        f"{_who} must leave each holder free to form as well as join trade unions to protect interests (the "
        "purpose clause is in the act phrase).")
_stem, _act = _U087["positive"]
add("u087", "state_positive",
    duty("u087", "state_positive", _stem, _act, f"The bearer is required to {_act[len('{0} '):].replace('{1}', 'the person')}",
         bearer="state", arity="person", opens=[]),
    "Claim reading as enabling: every State must enable each holder to form as well as join trade unions to protect their interests "
    "(the opportunity, not the formation or joining itself, which stays the holder's choice).")
add("u087", "liberty",
    liberty("u087", "liberty", "person_may_form_and_join_trade_unions",
            "{0} form as well as join trade unions " + _PURPOSE,
            "The person is permitted to form as well as join trade unions to protect their interests", []),
    "Liberty reading: each person is permitted to form as well as join trade unions to protect their interests (the permission names "
    "no other case and grants nothing to anyone else).")
add("u087", "entitlement",
    entitlement("u087", "entitlement", "has_the_right_to_form_and_join_trade_unions",
                "{0} has the right to form as well as join trade unions to protect their interests",
                "The person has the right to form and to join trade unions for the protection of their interests", []),
    "Entitlement reading: every person has the right, and the source names no one who must do anything, so no bearer is named.")

# ---- Article 26(1): u098, u099a, u099b ---------------------------------------------------------------------------------
GUARDIAN = sort("guardian", "guardians", "a parent or guardian of a person")


def gated_free_person_duty(unit, cid, stem, act, desc, opens):
    spec = dict(sorts={"person": PERSON}, predicates={stem: regulated(["person"], "obligation", desc, act)},
                rule=norm(U.slug(f"{unit}-{cid}"), stem, True, Top()), open=list(opens), soft=False)
    spec["witnesses"] = [({"person": ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]
    return spec


def guardian_duty(unit, cid, stem, act, desc, opens):
    spec = dict(sorts={"guardian": GUARDIAN, "person": PERSON},
                predicates={stem: regulated(["guardian", "person"], "obligation", desc, act)},
                rule=norm(U.slug(f"{unit}-{cid}"), stem, True, Top()), open=list(opens), soft=False)
    spec["witnesses"] = [({"guardian": ["g0"], "person": ["p0"]}, {}, [(stem, ("g0", "p0"), ("SETTLED", True))])]
    return spec


add("u098", "state_requires",
    duty("u098", "state_requires", "make_elementary_education_compulsory_required",
         "{0} make elementary education compulsory", "The bearer is required to make elementary education compulsory",
         bearer="state", arity="bearer", opens=["compulsory"]),
    "Article 26(1) read as a duty on every State to make elementary education compulsory (the passive names no one who makes it "
    "so). Who must attend, and to what age, is the open term compulsory.")
add("u098", "person_attends",
    gated_free_person_duty("u098", "person_attends", "attend_compulsory_elementary_education_required",
                           "{0} attend compulsory elementary education",
                           "The person is required to attend elementary education that is compulsory for the person", ["compulsory"]),
    "Article 26(1) read as a duty on a person to attend the elementary education that is compulsory for them. Who it is compulsory "
    "for is the open term compulsory (no age is stated and none is invented here, so no gate can leave everyone outside the duty).")
add("u098", "guardian_ensures",
    guardian_duty("u098", "guardian_ensures", "see_to_compulsory_elementary_education_required",
                  "{0} see that {1} attends compulsory elementary education",
                  "The parent or guardian is required to see that the person attends elementary education that is compulsory for the "
                  "person", ["compulsory"]),
    "Article 26(1) read as a duty of a parent or guardian to see that the person in their care attends the elementary education that is "
    "compulsory for that person (the open term compulsory decides for whom it is).")

for _uid in ("u099a", "u099b"):
    for _cid, _spec, _why in U.CANDIDATES[_uid]:
        if _cid == "state":
            CANDIDATES.setdefault(_uid, []).append((_cid, _spec, _why.replace(
                "read as a duty on every State", "read as a duty on every State (the only bearer the sentence can carry: the passive "
                "assigns no universal individual duty)")))
