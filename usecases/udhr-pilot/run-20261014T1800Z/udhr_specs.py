"""Norm candidates of the 39 content-bearing units, as norm-defaults@0 companion documents (completion `unspecified`).

The 2026-10-03 audit rejected every sampled unit whose candidates declared the completion `deny` ("not required")
or `permission deny`: the source never says nothing else is required or permitted. norm-defaults@0 is the profile
that leaves such cases UNDECIDED, and it cannot sit beside readings@1 content, rights@0 or soft-norms@0 in one
document. So each candidate of the units below is a one-unit companion document (source = the unit's exact bytes)
cited by the main document's reading set, as the repaired units of the previous run already were.

What changed against the previous run's candidates, from the audit and the 2026-10-03 rules:

* no defeasible twin of a 'shall' or of 'has the right' (the text states no exception for them; Article 22's
  resources clause is attached by the text to the entitlement of u082, not to the rights of Articles 23-27);
* an explicit enumeration is structure: a case sort whose base predicates are the enumerated items and a guard that
  lists them (torture, cruel, inhuman, degrading, treatment, punishment; privacy, family, home, correspondence;
  slavery, servitude; ...), never an open factor;
* a cause for an open term stays an open term ('arbitrary', 'cruel') as a base predicate that the guard requires;
* u025's 'shall be prohibited' keeps a duty to prohibit and a prohibition of the practice, never 'avoid';
* every liberty candidate is a permission under `unspecified`, and 'freely' and the freedoms offer one.

A rule's guard is a necessary condition of its norm: where the guard fails VE reports UNDECIDED, never 'not required'.

DSL: a guard is a nested tuple ("p", name) | ("b", name) | ("and", g, h) | ("or", g, h) | ("not", g) | ("top",);
("p", ...) names a base predicate of the case (the last argument), ("b", ...) a base predicate of the bearer.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

from ve.ast import And, Not, Or, Top, Unary, Var
from ve.ast import _to_data as data

from companions import environment, sort

PROFILES = ("documents@1", "norm-defaults@0", "norms@0", "relational-fol@0")
V0, V1 = Var(0), Var(1)
RESERVED = {"true", "false", "is", "equals", "not", "and", "or", "if", "then", "for", "every", "there", "exists",
            "believes", "must", "eventually", "no"}

BEARER = sort("bearer", "bearers", "a State, group or person")
PERSON = sort("person", "people", "a human person")


def base(arguments, description, verbalisation):
    return {"arguments": arguments, "description": description, "verbalisation": verbalisation}


def regulated(arguments, role, description, act):
    assert len(act.encode()) <= 80, act
    assert not RESERVED & set(act.replace("{0}", "").replace("{1}", "").replace("'", " ").lower().split()), act
    assert "," not in act, act
    return {"arguments": arguments, "description": description,
            "regulated": {"role": role, "default": "unspecified", "act": act}}




# ------------------------------------------------------------------ guards
def ast(guard, bearer_var, case_var):
    tag = guard[0]
    if tag == "top":
        return Top()
    if tag == "p":
        return Unary(guard[1], case_var)
    if tag == "b":
        return Unary(guard[1], bearer_var)
    if tag == "not":
        return Not(ast(guard[1], bearer_var, case_var))
    left, right = ast(guard[1], bearer_var, case_var), ast(guard[2], bearer_var, case_var)
    return And(left, right) if tag == "and" else Or(left, right)


def holds(guard, bearer_true, case_true):
    tag = guard[0]
    if tag == "top":
        return True
    if tag == "p":
        return guard[1] in case_true
    if tag == "b":
        return guard[1] in bearer_true
    if tag == "not":
        return not holds(guard[1], bearer_true, case_true)
    left, right = holds(guard[1], bearer_true, case_true), holds(guard[2], bearer_true, case_true)
    return (left and right) if tag == "and" else (left or right)


def AND(*gs):
    out = gs[0]
    for g in gs[1:]:
        out = ("and", out, g)
    return out


def OR(*gs):
    out = gs[0]
    for g in gs[1:]:
        out = ("or", out, g)
    return out


def norm(name, predicate, sign, guard):
    return {"norm": {"guard": data(guard), "name": name, "over": [], "predicate": predicate,
                     "sign": sign, "unless": []}}


def slug(text):
    return text.replace("_", "-")[:46]


# ------------------------------------------------------------------ case sorts
def case_sort(singular, plural, description, bases, guard, examples):
    """A case sort: `bases` {name: description}, `guard` over them, `examples` lists of base names true of one element."""
    return dict(sort=sort(singular, plural, description), bases=bases, guard=guard, examples=examples,
                name=singular.replace(" ", "_"))


# English the renderer accepts for a unary base predicate is exactly "{0} is X" with one word X (ve/printer.py); where the
# clause has such a word it is used, elsewhere the wording stays plain and the document view shows the generic form.
VERB = {
    "is_slavery": "{0} is slavery", "is_servitude": "{0} is servitude", "is_torture": "{0} is torture",
    "is_treatment": "{0} is treatment", "is_punishment": "{0} is punishment", "is_arrest": "{0} is arrest",
    "is_detention": "{0} is detention", "is_exile": "{0} is exile", "is_technical": "{0} is technical",
    "is_professional": "{0} is professional", "based_on_political_status": "{0} is political",
    "based_on_jurisdictional_status": "{0} is jurisdictional", "based_on_international_status": "{0} is international",
}


def case_bases(case):
    return {n: base([case["name"]], d, VERB.get(n) or _verb(d)) for n, d in case["bases"].items()}


def _verb(description):
    # "The deprivation is arbitrary" -> "{0} is arbitrary"
    first, rest = description.split(" ", 1)
    assert first.lower() == "the", description
    words = rest.split(" ", 1)
    return "{0} " + words[1]


# ------------------------------------------------------------------ candidate builders
STATE = sort("State", "States", "a State")


def duty(unit, cid, stem, act, desc, *, bearer, opens, arity="person", case=None, resources=False):
    """An obligation. `arity`: 'person' (bearer, person), 'bearer' (bearer alone), or the case sort of `case`.
    `bearer`: 'state' (the bearer sort is State: a rule over States only, every other party unmentioned) or 'anyone' (the
    bearer sort is a State, group or person)."""
    bsort = "state" if bearer == "state" else "bearer"
    sorts = {bsort: STATE if bearer == "state" else BEARER}
    predicates = {}
    if arity == "person":
        sorts["person"] = PERSON
        args = [bsort, "person"]
    elif arity == "bearer":
        args = [bsort]
    else:
        sorts[case["name"]] = case["sort"]
        args = [bsort, case["name"]]
        predicates.update(case_bases(case))
    bearer_var = V1 if len(args) == 2 else V0
    guards = []
    if resources:
        predicates["resources_allow"] = base(
            [bsort], "The organization and resources of the bearer allow it (the open term "
                     "organization_and_resources_of_each_state)", "{0} has the organization and resources for it")
        guards.append(("b", "resources_allow"))
    if case is not None:
        guards.append(case["guard"])
    guard = AND(*guards) if guards else ("top",)
    predicates[stem] = regulated(args, "obligation", desc, act)
    spec = dict(sorts=sorts, predicates=predicates,
                rule=norm(slug(f"{unit}-{cid}"), stem, True, ast(guard, bearer_var, V0)), open=list(opens), soft=False)
    spec["witnesses"] = duty_witnesses(stem, args, guard, case, bsort, resources)
    return spec


def duty_witnesses(stem, args, guard, case, bsort, resources):
    # bearer b0 has the organization and resources (when the rule asks), b1 has not
    b_true = {"b0": {"resources_allow"}, "b1": set()}
    bearers = ["b0", "b1"]
    rels = {"resources_allow": [["b0"]]} if resources else {}
    checks = []
    if case is not None:
        elems = [f"c{i}" for i in range(len(case["examples"]))]
        domains = {bsort: bearers, case["name"]: elems}
        for n in case["bases"]:
            rels[n] = [[e] for e, trues in zip(elems, case["examples"]) if n in trues]
        for b in bearers:
            for e, trues in zip(elems, case["examples"]):
                ok = holds(guard, b_true[b], set(trues))
                checks.append((stem, (b, e), ("SETTLED", True) if ok else ("UNDECIDED", None)))
    else:
        domains = {bsort: bearers}
        if "person" in args:
            domains["person"] = ["p0"]
        for b in bearers:
            ok = holds(guard, b_true[b], set())
            row = (b, "p0") if "person" in args else (b,)
            checks.append((stem, row, ("SETTLED", True) if ok else ("UNDECIDED", None)))
    return [(domains, rels, checks)]


def scoped_person_duty(unit, cid, stem, act, desc, scope_name, scope_desc, scope_verb, opens):
    """An obligation on a person, scoped by a named open relation of the person (u098: an age the source does not state)."""
    predicates = {scope_name: base(["person"], scope_desc, scope_verb),
                  stem: regulated(["person"], "obligation", desc, act)}
    guard = ("p", scope_name)
    spec = dict(sorts={"person": PERSON}, predicates=predicates,
                rule=norm(slug(f"{unit}-{cid}"), stem, True, ast(guard, V0, V0)), open=list(opens), soft=False)
    spec["witnesses"] = [({"person": ["p0", "p1"]}, {scope_name: [["p0"]]},
                          [(stem, ("p0",), ("SETTLED", True)), (stem, ("p1",), ("UNDECIDED", None))])]
    return spec


def liberty(unit, cid, stem, act, desc, opens):
    spec = dict(sorts={"person": PERSON},
                predicates={stem: regulated(["person"], "permission", desc, act)},
                rule=norm(slug(f"{unit}-{cid}"), stem, True, Top()), open=list(opens), soft=False)
    spec["witnesses"] = [({"person": ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]
    return spec


def prohibition(unit, cid, stem, act, desc, case, opens):
    """The act itself is not permitted (sign False on a permission): the guard picks the prohibited cases."""
    predicates = {stem: regulated([case["name"]], "permission", desc, act), **case_bases(case)}
    spec = dict(sorts={case["name"]: case["sort"]}, predicates=predicates,
                rule=norm(slug(f"{unit}-{cid}"), stem, False, ast(case["guard"], V0, V0)), open=list(opens), soft=False)
    elems = [f"c{i}" for i in range(len(case["examples"]))]
    rels = {n: [[e] for e, trues in zip(elems, case["examples"]) if n in trues] for n in case["bases"]}
    checks = [(stem, (e,), ("SETTLED", False) if holds(case["guard"], set(), set(t)) else ("UNDECIDED", None))
              for e, t in zip(elems, case["examples"])]
    spec["witnesses"] = [({case["name"]: elems}, rels, checks)]
    return spec


def write_companion(directory: Path, unit_id: str, candidate: str, spec: dict, source: bytes, open_terms: list) -> Path:
    meta = {"format": "ve-document@1",
            "environment": environment(PROFILES, spec["sorts"], spec["predicates"]),
            "open_terms": [copy.deepcopy(t) for t in open_terms if t["name"] in spec["open"]],
            "units": [{"content": spec["rule"], "id": f"{unit_id}_{candidate}", "kind": "norm",
                       "meaning": ({"open": list(spec["open"])} if spec["open"] else "specified"),
                       "span": [0, len(source)], "support": "none"}]}
    path = directory / f"{unit_id}.{candidate}.ve.md"
    path.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                     + b"\n---\n" + source)
    return path


# ================================================================== the units
CANDIDATES: dict[str, list[tuple[str, dict, str]]] = {}   # unit -> [(candidate id, spec, why)]
OPEN_NEW: dict[str, list[str]] = {}                       # open terms newly named: name -> factors

UNSPEC = ("Completion 'unspecified' (norm-defaults@0): where the rule's guard fails, or the party is not one the rule names, the case is "
          "UNDECIDED, never 'not required' and never permitted; strict force, because the source states no exception.")

BEARER_WHO = {"state": "every State", "anyone": "every State, group and person"}


def add(unit, cid, spec, why):
    CANDIDATES.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


def by_bearer(unit, builder, why, *, ids=("state", "anyone")):
    for b in ids:
        add(unit, b, builder(b, b), why.replace("{who}", BEARER_WHO[b]))


# ---- norm units ----------------------------------------------------------------------------------------------
U020_CASE = case_sort(
    "distinction", "distinctions",
    "one distinction made against one person on the basis of the status of the country or territory to which the person "
    "belongs, whether it be independent, trust, non-self-governing or under any other limitation of sovereignty",
    {"based_on_political_status": "The distinction is based on the political status of the country or territory",
     "based_on_jurisdictional_status": "The distinction is based on the jurisdictional status of the country or territory",
     "based_on_international_status": "The distinction is based on the international status of the country or territory"},
    OR(("p", "based_on_political_status"), ("p", "based_on_jurisdictional_status"), ("p", "based_on_international_status")),
    [["based_on_political_status"], ["based_on_jurisdictional_status"], ["based_on_international_status"], []])
for b in ("state", "anyone"):
    add("u020", b, duty("u020", b, "avoid_distinction_by_country_status_required", "{0} avoid making {1}",
                        f"The bearer is required to avoid making the distinction against the person on the basis of the status "
                        f"of the person's country or territory",
                        bearer=b, arity="case", case=U020_CASE, opens=["status_of_country_or_territory"]),
        f"Article 2: no distinction on the basis of the political, jurisdictional or international status of the country or "
        f"territory of a person (the three statuses are the guard's explicit list; 'whether independent, trust, "
        f"non-self-governing or under any other limitation of sovereignty' sets no condition). The source names no bearer: "
        f"the duty is on {BEARER_WHO[b]} to avoid making such a distinction.")

U024_CASE = case_sort(
    "holding", "holdings", "one holding of one person in a condition",
    {"is_slavery": "The holding is a holding in slavery", "is_servitude": "The holding is a holding in servitude"},
    OR(("p", "is_slavery"), ("p", "is_servitude")), [["is_slavery"], ["is_servitude"], []])
for b in ("state", "anyone"):
    add("u024", b, duty("u024", b, "avoid_holding_in_slavery_or_servitude_required", "{0} avoid carrying out {1}",
                        "The bearer is required to avoid carrying out the holding of the person in slavery or servitude",
                        bearer=b, arity="case", case=U024_CASE, opens=["slavery", "servitude"]),
        f"Article 4: no one shall be held in slavery or servitude; the duty is on {BEARER_WHO[b]} (the source names no bearer) "
        "and covers a holding in slavery and a holding in servitude (the explicit list).")

U025_CASE = case_sort(
    "practice", "practices", "one practice of slavery or of the slave trade, in any of its forms",
    {"is_slavery": "The practice is slavery in one of its forms",
     "is_slave_trade": "The practice is the slave trade in one of its forms"},
    OR(("p", "is_slavery"), ("p", "is_slave_trade")), [["is_slavery"], ["is_slave_trade"], []])
add("u025", "state_prohibits",
    duty("u025", "state_prohibits", "prohibit_slavery_and_slave_trade_required", "{0} prohibit {1}",
         "The bearer is required to prohibit the practice of slavery or of the slave trade",
         bearer="state", arity="case", case=U025_CASE, opens=["slavery", "slave_trade"]),
    "Article 4: 'slavery and the slave trade shall be prohibited in all their forms' read as a duty on every State to prohibit each "
    "practice of slavery and of the slave trade (the passive names no one who prohibits).")
add("u025", "practice_prohibited",
    prohibition("u025", "practice_prohibited", "slavery_or_slave_trade_practice_permitted", "{0} be carried out",
                "The practice of slavery or of the slave trade is permitted to be carried out", U025_CASE,
                ["slavery", "slave_trade"]),
    "Article 4 read as a prohibition of the practices themselves: no practice of slavery or of the slave trade, in any of "
    "its forms, is permitted (a permission refused for each such practice; nothing else is decided). Never read as 'avoid'.")

U027_CASE = case_sort(
    "subjection", "subjections",
    "one subjection of one person to torture, or to treatment or punishment",
    {"is_torture": "The subjection is a subjection to torture",
     "is_cruel": "The subjection is cruel", "is_inhuman": "The subjection is inhuman",
     "is_degrading": "The subjection is degrading",
     "is_treatment": "The subjection is a subjection to treatment",
     "is_punishment": "The subjection is a subjection to punishment"},
    OR(("p", "is_torture"),
       AND(OR(OR(("p", "is_cruel"), ("p", "is_inhuman")), ("p", "is_degrading")),
           OR(("p", "is_treatment"), ("p", "is_punishment")))),
    [["is_torture"], ["is_cruel", "is_punishment"], ["is_degrading", "is_treatment"], ["is_inhuman"],
     ["is_treatment", "is_punishment"]])
for b in ("state", "anyone"):
    add("u027", b, duty("u027", b, "avoid_torture_or_ill_treatment_required", "{0} avoid carrying out {1}",
                        "The bearer is required to avoid subjecting the person to torture or to cruel, inhuman or degrading "
                        "treatment or punishment",
                        bearer=b, arity="case", case=U027_CASE, opens=["ill_treatment"]),
        f"Article 5: the duty is on {BEARER_WHO[b]} (the source names no bearer) not to carry out a subjection to torture, or to "
        "treatment or punishment that is cruel, inhuman or degrading. Punishment is explicitly covered (structure of the guard: "
        "treatment or punishment); which treatment or punishment counts as cruel, inhuman or degrading stays the open term.")

U037_CASE = case_sort(
    "measure", "measures", "one arrest, detention or exile of one person",
    {"is_arrest": "The measure is an arrest", "is_detention": "The measure is a detention",
     "is_exile": "The measure is an exile", "is_arbitrary": "The measure is arbitrary"},
    AND(OR(("p", "is_arrest"), ("p", "is_detention"), ("p", "is_exile")), ("p", "is_arbitrary")),
    [["is_arrest", "is_arbitrary"], ["is_exile", "is_arbitrary"], ["is_detention"], ["is_arbitrary"]])
for b in ("state", "anyone"):
    add("u037", b, duty("u037", b, "avoid_arbitrary_arrest_detention_exile_required", "{0} avoid carrying out {1}",
                        "The bearer is required to avoid subjecting the person to an arbitrary arrest, detention or exile",
                        bearer=b, arity="case", case=U037_CASE, opens=["arbitrary"]),
        f"Article 9: the duty is on {BEARER_WHO[b]} (the source names no bearer) not to carry out an arrest, a detention or an "
        "exile that is arbitrary ('arbitrary' is read over all three acts; what makes a measure arbitrary is the open term). A "
        "measure that is not arbitrary is not decided by this rule.")

U045A_CASE = case_sort(
    "interference", "interferences", "one interference with the privacy, family, home or correspondence of one person",
    {"concerns_privacy": "The interference concerns the privacy of the person",
     "concerns_family": "The interference concerns the family of the person",
     "concerns_home": "The interference concerns the home of the person",
     "concerns_correspondence": "The interference concerns the correspondence of the person",
     "is_arbitrary": "The interference is arbitrary"},
    AND(OR(("p", "concerns_privacy"), ("p", "concerns_family"), ("p", "concerns_home"), ("p", "concerns_correspondence")),
        ("p", "is_arbitrary")),
    [["concerns_privacy", "is_arbitrary"], ["concerns_family", "is_arbitrary"], ["concerns_home", "is_arbitrary"],
     ["concerns_correspondence", "is_arbitrary"], ["concerns_home"], ["is_arbitrary"]])
for b in ("state", "anyone"):
    add("u045a", b, duty("u045a", b, "avoid_arbitrary_interference_required", "{0} avoid carrying out {1}",
                         "The bearer is required to avoid subjecting the person to an arbitrary interference with privacy, "
                         "family, home or correspondence",
                         bearer=b, arity="case", case=U045A_CASE, opens=["arbitrary"]),
        f"Article 12: the duty is on {BEARER_WHO[b]} (the source names no bearer) not to carry out an arbitrary interference with "
        "the privacy, the family, the home or the correspondence of a person: the four named domains are the guard's explicit "
        "list, not a single 'private life'. What makes an interference arbitrary is the open term.")

U045B_CASE = case_sort(
    "attack", "attacks", "one attack upon the honour or the reputation of one person",
    {"concerns_honour": "The attack is upon the honour of the person",
     "concerns_reputation": "The attack is upon the reputation of the person"},
    OR(("p", "concerns_honour"), ("p", "concerns_reputation")),
    [["concerns_honour"], ["concerns_reputation"], []])
for b in ("state", "anyone"):
    add("u045b", b, duty("u045b", b, "avoid_attacks_upon_honour_and_reputation_required", "{0} avoid carrying out {1}",
                         "The bearer is required to avoid subjecting the person to an attack upon honour or reputation",
                         bearer=b, arity="case", case=U045B_CASE, opens=[]),
        f"Article 12 (second clause, 'nor to attacks upon his honour and reputation'): the duty is on {BEARER_WHO[b]} (the source "
        "names no bearer) not to carry out an attack upon the honour or the reputation of a person; the subject and 'shall' are "
        "carried from the previous unit (not a checked reference).")

U055_CASE = case_sort(
    "measure", "measures",
    "one deprivation of one person of nationality, or one denial to the person of the right to change nationality",
    {"is_deprivation_of_nationality": "The measure is a deprivation of nationality",
     "is_denial_of_change": "The measure is a denial of the right to change nationality",
     "is_arbitrary": "The measure is arbitrary"},
    None, [["is_deprivation_of_nationality", "is_arbitrary"], ["is_denial_of_change", "is_arbitrary"],
           ["is_denial_of_change"], ["is_deprivation_of_nationality"]])
for scope, guard in (("both_acts", AND(OR(("p", "is_deprivation_of_nationality"), ("p", "is_denial_of_change")),
                                       ("p", "is_arbitrary"))),
                     ("deprivation_only", OR(AND(("p", "is_deprivation_of_nationality"), ("p", "is_arbitrary")),
                                             ("p", "is_denial_of_change")))):
    case = {**U055_CASE, "guard": guard}
    for b in ("state", "anyone"):
        add("u055", f"{scope}_{b}",
            duty("u055", f"{scope}_{b}", "avoid_loss_of_nationality_required", "{0} avoid carrying out {1}",
                 "The bearer is required to avoid depriving the person of nationality arbitrarily and to avoid denying the "
                 "person the right to change nationality",
                 bearer=b, arity="case", case=case, opens=["arbitrary"]),
            "Article 15(2): the duty is on " + BEARER_WHO[b] + " (the source names no bearer). 'Arbitrarily' is read "
            + ("over both acts (the deprivation and the denial)" if scope == "both_acts" else
               "over the deprivation only (the denial is then barred whether or not it is arbitrary)")
            + "; the source's word order admits both. What makes a measure arbitrary is the open term.")

U059_CASE = case_sort(
    "marriage entry", "marriage entries", "one entry into marriage by its intending spouses",
    {"has_free_consent_of_each_spouse": "The entry has the free consent of each intending spouse",
     "has_full_consent_of_each_spouse": "The entry has the full consent of each intending spouse"},
    ("not", AND(("p", "has_free_consent_of_each_spouse"), ("p", "has_full_consent_of_each_spouse"))),
    [[], ["has_free_consent_of_each_spouse"], ["has_full_consent_of_each_spouse"],
     ["has_free_consent_of_each_spouse", "has_full_consent_of_each_spouse"]])
for b in ("state", "anyone"):
    add("u059", b, duty("u059", b, "avoid_marriage_without_free_and_full_consent_required",
                        "{0} avoid carrying out {1}",
                        "The bearer is required to avoid carrying out an entry into marriage that lacks the free consent or "
                        "the full consent of an intending spouse",
                        bearer=b, arity="case", case=U059_CASE, opens=["free_and_full_consent"]),
        f"Article 16(2): 'only with the free and full consent of the intending spouses' read as a necessary condition: the duty "
        f"is on {BEARER_WHO[b]} (the passive names no one) to avoid carrying out an entry into marriage unless each intending "
        "spouse's consent is both free and full. An entry that has both is not decided by this rule (UNDECIDED).")

U064_CASE = case_sort(
    "deprivation", "deprivations", "one deprivation of one person of property",
    {"is_arbitrary": "The deprivation is arbitrary"}, ("p", "is_arbitrary"), [["is_arbitrary"], []])
for b in ("state", "anyone"):
    add("u064", b, duty("u064", b, "avoid_arbitrary_deprivation_of_property_required", "{0} avoid carrying out {1}",
                        "The bearer is required to avoid depriving the person of property arbitrarily",
                        bearer=b, arity="case", case=U064_CASE, opens=["arbitrary"]),
        f"Article 17(2): the duty is on {BEARER_WHO[b]} (the source names no bearer) not to carry out an arbitrary deprivation of "
        "property; what makes a deprivation arbitrary is the open term; a deprivation that is not arbitrary is not decided here.")

# Article 26
add("u098", "person_receives",
    scoped_person_duty("u098", "person_receives", "receive_elementary_education_required", "{0} receive elementary education",
                       "The person is required to receive elementary education",
                       "of_age_for_elementary_education",
                       "The person is of the age at which elementary education is compulsory, if there is one; the source "
                       "states no age", "{0} is of the age for elementary education", ["compulsory"]),
    "Article 26(1): 'Elementary education shall be compulsory' read as a duty on a person of the age for it (the named open "
    "relation of_age_for_elementary_education: the source states no age) to receive it. " + UNSPEC)
add("u098", "state_requires",
    duty("u098", "state_requires", "make_elementary_education_compulsory_required",
         "{0} make elementary education compulsory", "The bearer is required to make elementary education compulsory",
         bearer="state", arity="bearer", opens=["compulsory"]),
    "Article 26(1) read as a duty on every State to make elementary education compulsory (the passive names no one who makes it "
    "so). Who must attend, and to what age, is the open term compulsory.")

U099A_CASE = case_sort(
    "education kind", "education kinds", "one kind of education",
    {"is_technical": "The education is technical education", "is_professional": "The education is professional education"},
    OR(("p", "is_technical"), ("p", "is_professional")), [["is_technical"], ["is_professional"], []])
for b in ("state", "anyone"):
    add("u099a", b, duty("u099a", b, "make_education_generally_available_required", "{0} make {1} generally available",
                         "The bearer is required to make the education generally available",
                         bearer=b, arity="case", case=U099A_CASE, opens=["generally_available"]),
        f"Article 26(1): 'Technical and professional education shall be made generally available' read as a duty on {BEARER_WHO[b]} "
        "(the passive names no one) to make technical education, and professional education, generally available (the two named "
        "kinds are the guard's explicit list). What makes education generally available is the open term.")


def unary(unit, cid, stem, act, desc, bearer, opens):
    return duty(unit, cid, stem, act, desc, bearer=bearer, arity="bearer", opens=opens)


for b in ("state", "anyone"):
    add("u099b", b, unary("u099b", b, "make_higher_education_accessible_required",
                          "{0} make higher education equally accessible to all on the basis of merit",
                          "The bearer is required to make higher education equally accessible to all on the basis of merit", b,
                          ["merit"]),
        f"Article 26(1): 'higher education shall be equally accessible to all on the basis of merit' read as a duty on "
        f"{BEARER_WHO[b]} (the passive names no one). The subject and 'shall' are carried from u099a (not a checked reference).")
    add("u100a", b, unary("u100a", b, "direct_education_to_personality_required",
                          "{0} direct education to the full development of the human personality",
                          "The bearer is required to direct education to the full development of the human personality", b,
                          ["full_development_of_the_human_personality"]),
        f"Article 26(2): 'Education shall be directed to the full development of the human personality' read as a duty on "
        f"{BEARER_WHO[b]} (the passive names no one who directs education).")
    add("u100b", b, unary("u100b", b, "direct_education_to_respect_for_rights_required",
                          "{0} direct education to strengthen respect of human rights as well as freedoms",
                          "The bearer is required to direct education to the strengthening of respect for human rights and "
                          "fundamental freedoms", b, ["rights_and_freedoms_set_forth"]),
        f"Article 26(2): 'and to the strengthening of respect for human rights and fundamental freedoms' read as a duty on "
        f"{BEARER_WHO[b]}; the subject and 'shall' are carried from u100a (not a checked reference).")


# ---- right units ---------------------------------------------------------------------------------------------
# unit: (negative stem, negative act, positive stem, positive act, liberty (stem, act) or None, open terms)
# polarity: 'both' (avoid and secure), 'positive' (secure only), 'claim' (one claim as the previous run had it)
RIGHTS = {
    "u022a": ("both", ("avoid_life_required", "{0} avoid depriving {1} of life"),
              ("secure_life_required", "{0} protect the life of {1}"), None, []),
    "u022b": ("both", ("avoid_liberty_required", "{0} avoid depriving {1} of liberty"),
              ("secure_liberty_required", "{0} secure the liberty of {1}"), None, []),
    "u022c": ("both", ("avoid_security_of_person_required", "{0} avoid endangering the security of the person of {1}"),
              ("secure_security_of_person_required", "{0} safeguard the security of the person of {1}"), None, []),
    "u029": ("claim", None, ("secure_recognition_as_person_required", "{0} recognise {1} everywhere as a person before the law"),
             None, []),
    "u032": ("claim", None, ("secure_equal_protection_required",
                              "{0} give {1} equal protection of the law without any discrimination"), None,
             ["discrimination", "equal_protection_of_the_law"]),
    "u033a": ("claim", None, ("secure_protection_against_discrimination_required",
                               "{0} protect {1} equally against discrimination in violation of this Declaration"), None,
              ["discrimination", "equal_protection_of_the_law"]),
    "u033b": ("claim", None, ("secure_protection_against_incitement_required",
                               "{0} protect {1} equally against incitement to such discrimination"), None,
              ["discrimination", "equal_protection_of_the_law"]),
    "u046": ("claim", None, ("secure_protection_against_interference_required",
                              "{0} protect {1} by law against such interference as well as attacks"), None, ["arbitrary"]),
    "u048": ("both", ("avoid_movement_and_residence_required",
                      "{0} avoid denying {1} freedom of movement as well as residence within each state"),
             ("secure_movement_and_residence_required",
              "{0} secure {1} freedom of movement as well as residence within each state"),
             ("person_may_movement_and_residence", "{0} move as well as reside within the borders of each state"), []),
    "u049": ("claim", None, ("avoid_leave_and_return_required",
                              "{0} avoid barring {1} from leaving any country as well as returning to their own"),
             ("person_may_leave_and_return", "{0} leave any country as well as return to their own country"), []),
    "u063": ("both", ("avoid_property_required",
                      "{0} avoid barring {1} from owning property alone as well as jointly with others"),
             ("secure_property_required", "{0} secure the ownership of property by {1} alone as well as with others"),
             ("person_may_property", "{0} own property alone as well as in association with others"), []),
    "u066": ("both", ("avoid_thought_conscience_religion_required",
                      "{0} avoid denying {1} freedom of thought conscience as well as religion"),
             ("secure_thought_conscience_religion_required",
              "{0} secure {1} freedom of thought conscience as well as religion"),
             ("person_may_thought_conscience_religion", "{0} enjoy freedom of thought conscience as well as religion"), []),
    "u070": ("both", ("avoid_opinion_and_expression_required",
                      "{0} avoid denying {1} freedom of opinion as well as expression"),
             ("secure_opinion_and_expression_required", "{0} secure {1} freedom of opinion as well as expression"),
             ("person_may_opinion_and_expression", "{0} enjoy freedom of opinion as well as expression"), []),
    "u073": ("both", ("avoid_assembly_and_association_required",
                      "{0} avoid denying {1} freedom of peaceful assembly as well as association"),
             ("secure_assembly_and_association_required",
              "{0} secure {1} freedom of peaceful assembly as well as association"),
             ("person_may_assembly_and_association", "{0} enjoy freedom of peaceful assembly as well as association"), []),
    # the 10 units newly stated last run (force_table.RIGHT_UNITS), their liberty candidates new
    "u081": ("claim", None, ("secure_social_security_required", "{0} secure {1} social security"), None, ["social_security"]),
    "u084a": ("both", ("avoid_work_required", "{0} avoid barring {1} from work"),
              ("secure_work_required", "{0} provide {1} with work"),
              ("person_may_work", "{0} work"), []),
    "u084b": ("both", ("avoid_free_choice_of_employment_required",
                       "{0} avoid restricting the free choice of employment of {1}"),
              ("secure_free_choice_of_employment_required", "{0} secure {1} free choice of employment"),
              ("person_may_choose_employment", "{0} choose their employment freely"), []),
    "u084c": ("claim", None, ("secure_just_and_favourable_conditions_of_work_required",
                               "{0} secure {1} just as well as favourable conditions of work"), None,
              ["just_and_favourable_conditions_of_work"]),
    "u084d": ("claim", None, ("secure_protection_against_unemployment_required", "{0} protect {1} against unemployment"),
              None, []),
    "u087": ("both", ("avoid_trade_unions_required",
                      "{0} avoid barring {1} from forming as well as joining trade unions"),
             ("secure_trade_unions_required", "{0} secure {1} forming as well as joining trade unions"),
             ("person_may_form_and_join_trade_unions", "{0} form as well as join trade unions"), []),
    "u096": ("both", ("avoid_education_required", "{0} avoid barring {1} from education"),
             ("secure_education_required", "{0} secure {1} education"), None, []),
    "u105a": ("both", ("avoid_cultural_life_required",
                       "{0} avoid barring {1} from taking part in the cultural life of the community"),
              ("secure_cultural_life_required", "{0} secure {1} free participation in the cultural life of the community"),
              ("person_may_take_part_in_cultural_life",
               "{0} freely take part in the cultural life of the community"), []),
    "u105b": ("both", ("avoid_enjoyment_of_the_arts_required", "{0} avoid barring {1} from enjoying the arts"),
              ("secure_enjoyment_of_the_arts_required", "{0} secure {1} the enjoyment of the arts"),
              ("person_may_enjoy_the_arts", "{0} freely enjoy the arts"), []),
    "u105c": ("claim", None, ("secure_scientific_advancement_required",
                               "{0} secure {1} a share in scientific advancement as well as its benefits"),
              ("person_may_share_in_scientific_advancement",
               "{0} freely share in scientific advancement as well as its benefits"), []),
}
RIGHT_TEXT = {
    "u022a": "the right to life", "u022b": "the right to liberty", "u022c": "the right to security of person",
    "u029": "the right to recognition everywhere as a person before the law",
    "u032": "the entitlement without any discrimination to equal protection of the law",
    "u033a": "the entitlement to equal protection against any discrimination in violation of this Declaration",
    "u033b": "the entitlement to equal protection against any incitement to such discrimination",
    "u046": "the right to the protection of the law against such interference or attacks",
    "u048": "the right to freedom of movement and residence within the borders of each state",
    "u049": "the right to leave any country, including his own, and to return to his country",
    "u063": "the right to own property alone as well as in association with others",
    "u066": "the right to freedom of thought, conscience and religion",
    "u070": "the right to freedom of opinion and expression",
    "u073": "the right to freedom of peaceful assembly and association",
    "u081": "the right to social security", "u084a": "the right to work",
    "u084b": "the right to free choice of employment",
    "u084c": "the right to just and favourable conditions of work",
    "u084d": "the right to protection against unemployment",
    "u087": "the right to form and to join trade unions for the protection of one's interests",
    "u096": "the right to education", "u105a": "the right freely to participate in the cultural life of the community",
    "u105b": "the right freely to enjoy the arts",
    "u105c": "the right freely to share in scientific advancement and its benefits",
}
RESOURCES_OPEN = "organization_and_resources_of_each_state"
OPEN_NEW[RESOURCES_OPEN] = ["what the organization and resources of a State allow",
                            "whether the clause of Article 22 limits the right to social security itself or only the "
                            "realization of the rights it names (u082)"]


def right_unit(uid, spec):
    kind, neg, pos, lib, opens = spec
    text = RIGHT_TEXT[uid]
    if kind == "both":
        pairs = [("negative", neg, "avoid denying or harming the right"), ("positive", pos, "secure the right")]
    else:
        pairs = [("claim", pos, "the one duty the previous reading gave the right")]
    for b in ("state", "anyone"):
        for pol, (stem, act), what in pairs:
            cid = f"{b}_{pol}"
            who = BEARER_WHO[b]
            add(uid, cid, duty(uid, cid, stem, act,
                               f"The bearer is required to {act[len('{0} '):].replace('{1}', 'the person')}",
                               bearer=b, arity="person", opens=opens),
                f"Claim reading of {text}: {who} must {act[len('{0} '):].replace('{1}', 'each holder')} ({what}); the source "
                "names no bearer and no polarity, so this is the translator's candidate.")
    if uid == "u081":
        for b in ("state", "anyone"):
            stem, act = pos
            cid = f"{b}_claim_within_resources"
            add(uid, cid, duty(uid, cid, stem, act,
                               f"The bearer is required to {act[len('{0} '):].replace('{1}', 'the person')}",
                               bearer=b, arity="person", opens=opens + [RESOURCES_OPEN], resources=True),
                f"Claim reading of {text} qualified by Article 22's clause 'in accordance with the organization and resources "
                f"of each State': {BEARER_WHO[b]} must secure each holder social security where its organization and resources "
                "allow it (the necessary condition is a guard over the named open relation resources_allow, term "
                f"{RESOURCES_OPEN}); where they do not allow it the case is UNDECIDED. The clause belongs grammatically to the "
                "entitlement of u082, so this candidate is one of two readings of its reach, not the only one.")
    if lib:
        stem, act = lib
        add(uid, "liberty",
            liberty(uid, "liberty", stem, act, "The person is permitted to " + act[len("{0} "):], opens),
            f"Liberty reading of {text}: each person is permitted to {act[len('{0} '):]} (the permission names no other case "
            "and grants nothing to anyone else).")


for _uid, _spec in RIGHTS.items():
    right_unit(_uid, _spec)

# ---- units repaired after the audit ----------------------------------------------------------------------------

# Article 29(1): 'Everyone has duties to the community in which alone the free and full development of his personality is
# possible.' The relative clause is read two ways: as restricting which community the duties are owed to (a guard over the
# open relation is_sole_setting_of_full_development), or as describing the one community and setting no condition (the
# audit: with the relation empty nobody would have a duty, though the source says everyone has duties).
import companions_nd as ND  # noqa: E402

add("u110", "restrictive", ND.SPECS["u110"]["duty"],
    "Article 29(1) read with the relative clause as a restriction: the person owes duties to a community that is the one "
    "'in which alone the free and full development of his personality is possible' (a guard over the open relation "
    "is_sole_setting_of_full_development). Where no community stands in that relation the case is UNDECIDED, so this reading "
    "alone would leave the persons of such a case without a stated duty; the next candidate does not.")
add("u110", "describing",
    dict(sorts={"person": PERSON},
         predicates={"perform_duties_to_the_community_required": regulated(
             ["person"], "obligation",
             "The person is required to perform the duties the person has to the community in which alone the free and full "
             "development of the person's personality is possible",
             "{0} perform duties to the community of their free as well as full development")},
         rule=norm("everyone-performs-duties-to-the-community", "perform_duties_to_the_community_required", True, Top()),
         open=["duties_to_the_community", "free_and_full_development", "community_of_full_development"], soft=False,
         witnesses=[({"person": ["p0"]}, {}, [("perform_duties_to_the_community_required", ("p0",), ("SETTLED", True))])]),
    "Article 29(1) read with the relative clause as describing the one community the duties are owed to, not as a condition: every "
    "person has duties to it. The clause (that such a community exists, and that development is possible only in it) is carried "
    "by the act phrase and the open term community_of_full_development, not stated as a checked condition.")
OPEN_NEW["community_of_full_development"] = [
    "whether there is a community in which alone the free and full development of a personality is possible",
    "which community that is, for each person", "whether it is the same community for every person"]
