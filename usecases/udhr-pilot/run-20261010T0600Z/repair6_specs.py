"""Words-only repair of the UDHR reading sets (lead's rule of 2026-10-08) and the repairs of the 2026-10-07T1800Z audit.

READINGS COME FROM THE WORDS ONLY. Where the English names no one who must act ("No one shall be held in slavery",
"Everyone has the right to life", "higher education shall be equally accessible to all"), the previous runs offered
readings that put the duty on every State (outside knowledge: who usually bears a duty) or on every State, group and person
(a bearer the words do not name). Those readings are gone. What the words support stays, with no bearer:

* a prohibition ("No one shall be X", "X shall be prohibited"): a permission predicate over the thing itself (the holding, the
  subjection, the measure) refused by the rule: X is not permitted (never "avoid", never a duty on anyone);
* "has the right to X": the entitlement (a plain predicate true of every person), the liberty where X is something one does
  (a permission), and claim readings that say, of no stated party, what must hold of the person (be spared a denial of X, be
  enabled in X, both). The obligation's one argument is the person, so the claim holds of every person and no relation can
  empty it; where the act phrase (80 bytes) cannot carry the source's whole phrase twice, the combined reading is over the
  *holder of the right* (a person), whose sort name is the source's phrase;
* a passive duty ("shall be made available"): the bearer-less obligation over the thing (the u099/u100 `unassigned` readings).

Audit repairs (previous-20261007T1800Z/AUDIT.md, 14/20 faithful; u046 u063 u077 u100b u105c u110 rejected):

* u046: the entitlement candidates said the law protects the person (a fact about protection); they now say the person has the
  right to the protection of the law against the intrusion, which stays true when no protection is given. The State candidates
  are replaced by a bearer-less claim that the intrusion be covered by the protection of the law.
* u063, u105c: the duty candidates quantified over right objects; the claim readings are now over every person.
* u077: no country is made a bearer; entitlement readings leave the responsibility unspecified, one for each reading of
  "his country" (nationality, residence), next to the bearer-less claims.
* u100b: the act phrase keeps "fundamental" in "fundamental freedoms"; the `education` candidate (a plain statement in place of
  "shall be directed") is gone, with the State candidate.
* u110: the `identified_community` reading kept the clause out of what is said (true when development is possible nowhere); it
  is removed. The two readings left keep the clause as part of what is asserted.
"""
from __future__ import annotations

import repair_specs as RS
import udhr_specs as U
from udhr_specs import PERSON, V0, base, case_sort, holds, norm, prohibition, regulated, slug, sort
from ve.ast import Top

UNSPEC = U.UNSPEC
NEW: dict[str, list[tuple[str, dict, str]]] = {}      # unit -> [(candidate id, spec, why)] written this run
KEEP: dict[str, list[str]] = {}                       # unit -> existing candidate ids kept as they are
ORDER: dict[str, list[str]] = {}                      # unit -> final candidate order
REASON: dict[str, str] = {}                           # unit -> what was repaired and why
ENTITLEMENT_ONLY_HERE = []


def add(unit, cid, spec, why):
    NEW.setdefault(unit, []).append((cid, spec, why + " " + UNSPEC))


NOBEARER = ("The words name no one who must act, so this reading names no bearer and mentions no State, group or person; nothing "
            "is said of anyone's duty.")


# ------------------------------------------------------------------ builders (no bearer)
def claim(unit, cid, stem, act, opens, *, holder=None):
    """An obligation whose one argument is the person: 'it is required, of no stated party, that the person <act>'.

    `holder`: (singular, plural, description) of a sort of persons used instead of `person` (the combined reading of a right whose
    phrase the 80-byte act cannot carry twice); its elements are persons, so the claim is over every holder."""
    assert len(act.encode()) <= 80, (unit, cid, len(act.encode()), act)
    if holder is None:
        sname, ssort = "person", PERSON
    else:
        sname, ssort = holder[0], sort(*holder[1:])
        assert sname.replace("_", " ") == holder[1] and len(sname.encode()) <= 64, sname
    desc = "It is required, of no stated party, that the " + ("person" if holder is None else "holder") + " " \
        + act[len("{0} "):]
    spec = dict(sorts={sname: ssort}, predicates={stem: regulated([sname], "obligation", desc, act)},
                rule=norm(slug(f"{unit}-{cid}"), stem, True, Top()), open=list(opens), soft=False)
    spec["witnesses"] = [({sname: ["p0"]}, {}, [(stem, ("p0",), ("SETTLED", True))])]
    return spec


def forbidden(unit, cid, stem, act, desc, case, opens, guard=None):
    """'No one shall be X': X is not permitted. The case sort's guard picks the forbidden cases; elsewhere UNDECIDED."""
    case = {**case, "guard": guard if guard is not None else case["guard"]}
    spec = prohibition(unit, cid, stem, act, desc, case, opens)
    return spec


# ------------------------------------------------------------------ passive prohibitions: one bearer-less reading each
FORBID = {
    "u020": ("distinction_by_country_status_permitted", "{0} be made",
             "The distinction against the person on the basis of the status of the person's country or territory is permitted "
             "to be made", U.U020_CASE, ["status_of_country_or_territory"],
             "Article 2, second sentence: 'no distinction shall be made on the basis of the political, jurisdictional or "
             "international status of the country or territory ...': a distinction on one of those three statuses is not "
             "permitted (the three statuses are the guard's explicit list; 'whether independent, trust, non-self-governing or "
             "under any other limitation of sovereignty' sets no condition)."),
    "u024": ("holding_in_slavery_or_servitude_permitted", "{0} take place",
             "The holding of a person in slavery or in servitude is permitted to take place", U.U024_CASE,
             ["slavery", "servitude"],
             "Article 4: 'No one shall be held in slavery or servitude': a holding in slavery and a holding in servitude (the "
             "explicit list) are not permitted."),
    "u027": ("subjection_to_ill_treatment_permitted", "{0} take place",
             "The subjection of a person to torture, or to cruel, inhuman or degrading treatment or punishment, is permitted to "
             "take place", U.U027_CASE, ["ill_treatment"],
             "Article 5: 'No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment': a "
             "subjection to torture, and a subjection to treatment or punishment that is cruel, inhuman or degrading, are not "
             "permitted. Punishment is explicitly covered (structure of the guard: treatment or punishment); which treatment or "
             "punishment counts as cruel, inhuman or degrading stays the open term."),
    "u037": ("arrest_detention_or_exile_permitted", "{0} take place",
             "The arbitrary arrest, detention or exile of a person is permitted to take place", U.U037_CASE, ["arbitrary"],
             "Article 9: 'No one shall be subjected to arbitrary arrest, detention or exile': an arrest, a detention and an exile "
             "that is arbitrary ('arbitrary' is read over all three acts; what makes a measure arbitrary is the open term) are "
             "not permitted. A measure that is not arbitrary is not decided by this rule."),
    "u045a": ("interference_with_private_domains_permitted", "{0} take place",
              "The arbitrary interference with a person's privacy, family, home or correspondence is permitted to take place",
              U.U045A_CASE, ["arbitrary"],
              "Article 12: 'No one shall be subjected to arbitrary interference with his privacy, family, home or "
              "correspondence': an arbitrary interference with the privacy, the family, the home or the correspondence of a "
              "person is not permitted (the four named domains are the guard's explicit list, not a single 'private life'). "
              "What makes an interference arbitrary is the open term."),
    "u045b": ("attack_upon_honour_or_reputation_permitted", "{0} take place",
              "The attack upon a person's honour or reputation is permitted to take place", U.U045B_CASE, [],
              "Article 12, second clause: 'nor to attacks upon his honour and reputation': an attack upon the honour or the "
              "reputation of a person is not permitted; the subject and 'shall' are carried from the previous unit (not a "
              "checked reference)."),
    "u059": ("entry_into_marriage_permitted", "{0} take place",
             "The entry into marriage is permitted to take place", U.U059_CASE, ["free_and_full_consent"],
             "Article 16(2): 'Marriage shall be entered into only with the free and full consent of the intending spouses' read "
             "as a necessary condition: an entry into marriage that lacks the free consent or the full consent of an intending "
             "spouse is not permitted. An entry that has both is not decided by this rule (UNDECIDED)."),
    "u064": ("deprivation_of_property_permitted", "{0} take place",
             "The arbitrary deprivation of a person of property is permitted to take place", U.U064_CASE, ["arbitrary"],
             "Article 17(2): 'No one shall be arbitrarily deprived of his property': an arbitrary deprivation of property is not "
             "permitted; what makes a deprivation arbitrary is the open term; a deprivation that is not arbitrary is not decided "
             "here."),
}
for _uid, (_stem, _act, _desc, _case, _opens, _why) in FORBID.items():
    add(_uid, "prohibited", forbidden(_uid, "prohibited", _stem, _act, _desc, _case, _opens), _why + " " + NOBEARER)
    ORDER[_uid] = ["prohibited"]
    REASON[_uid] = ("the State and anyone readings are gone: the words name no one who must refrain, so a duty on every State "
                    "(outside knowledge) or on every State, group and person (a bearer the words do not name) is not a reading of "
                    "them; one bearer-less prohibition is left")

# u055: two scopes of 'arbitrarily' (the words' order admits both), no bearer
_U055 = U.U055_CASE
for _scope, _guard in (
        ("both_acts", U.AND(U.OR(("p", "is_deprivation_of_nationality"), ("p", "is_denial_of_change")), ("p", "is_arbitrary"))),
        ("deprivation_only", U.OR(U.AND(("p", "is_deprivation_of_nationality"), ("p", "is_arbitrary")),
                                  ("p", "is_denial_of_change")))):
    add("u055", _scope, forbidden("u055", _scope, "loss_of_nationality_permitted", "{0} take place",
                                  "The deprivation of a person of nationality, or the denial to the person of the right to change "
                                  "nationality, is permitted to take place", _U055, ["arbitrary"], guard=_guard),
        "Article 15(2): 'No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality': "
        + ("'arbitrarily' is read over both acts (the deprivation and the denial): neither is permitted when arbitrary"
           if _scope == "both_acts" else
           "'arbitrarily' is read over the deprivation only: an arbitrary deprivation is not permitted, and a denial of the right "
           "to change nationality is not permitted whether or not it is arbitrary")
        + "; the source's word order admits both. What makes a measure arbitrary is the open term. " + NOBEARER)
ORDER["u055"] = ["both_acts", "deprivation_only"]
REASON["u055"] = ("the State and anyone readings are gone (the words name no one who must refrain); the two scopes of "
                  "'arbitrarily', which the word order admits, are kept as two bearer-less prohibitions")

# u025: 'shall be prohibited in all their forms': the practice is not permitted, or it is required that it be prohibited
add("u025", "required_prohibited", dict(
    sorts={"practice": U.U025_CASE["sort"]},
    predicates={**U.case_bases(U.U025_CASE),
                "prohibition_of_slavery_and_slave_trade_required": regulated(
                    ["practice"], "obligation",
                    "It is required, of no stated party, that the practice of slavery or of the slave trade be prohibited",
                    "{0} be prohibited")},
    rule=norm("u025-required-prohibited", "prohibition_of_slavery_and_slave_trade_required", True,
              U.ast(U.U025_CASE["guard"], V0, V0)), open=["slavery", "slave_trade"], soft=False,
    witnesses=[({"practice": ["c0", "c1", "c2"]}, {"is_slavery": [["c0"]], "is_slave_trade": [["c1"]]},
                [("prohibition_of_slavery_and_slave_trade_required", ("c0",), ("SETTLED", True)),
                 ("prohibition_of_slavery_and_slave_trade_required", ("c1",), ("SETTLED", True)),
                 ("prohibition_of_slavery_and_slave_trade_required", ("c2",), ("UNDECIDED", None))])]),
    "Article 4: 'slavery and the slave trade shall be prohibited in all their forms' read as a requirement that each practice of "
    "slavery and of the slave trade be prohibited (the passive names no one who prohibits, so no bearer is named). " + NOBEARER)
KEEP["u025"] = ["practice_prohibited"]
ORDER["u025"] = ["required_prohibited", "practice_prohibited"]
REASON["u025"] = ("the State reading (a duty on every State to prohibit) is gone, since the passive names no one who prohibits; the "
                  "reading that the prohibition is required, of no stated party, replaces it next to the unchanged prohibition of the practice")

# ------------------------------------------------------------------ u111: Article 29(2)
U111_CASE = case_sort(
    "limitation", "limitations",
    "one limitation on one person's exercise of one right or freedom set forth in this Declaration: the person and the right "
    "are the limitation's own",
    {"is_determined_by_law": "The limitation is determined by law",
     "serves_any_other_purpose": "The limitation also serves a purpose other than these two",
     "serves_recognition_of_rights_of_others": "The limitation is for the purpose of securing due recognition and respect for "
                                               "the rights and freedoms of others",
     "serves_just_requirements": "The limitation is for the purpose of meeting the just requirements of morality, public order "
                                 "and the general welfare in a democratic society"},
    None,
    [["is_determined_by_law", "serves_recognition_of_rights_of_others", "serves_just_requirements"],
     ["is_determined_by_law", "serves_recognition_of_rights_of_others"],
     ["is_determined_by_law", "serves_just_requirements"],
     ["serves_recognition_of_rights_of_others", "serves_just_requirements"],
     ["is_determined_by_law", "serves_recognition_of_rights_of_others", "serves_any_other_purpose"],
     []])
_ok_listed = U.AND(("p", "is_determined_by_law"), ("not", ("p", "serves_any_other_purpose")),
                   U.OR(("p", "serves_recognition_of_rights_of_others"), ("p", "serves_just_requirements")))
_ok_both = U.AND(("p", "is_determined_by_law"), ("not", ("p", "serves_any_other_purpose")),
                 ("p", "serves_recognition_of_rights_of_others"), ("p", "serves_just_requirements"))
_U111_OPEN = ["determined_by_law", "due_recognition_and_respect", "just_requirements", "morality", "public_order",
              "general_welfare", "democratic_society"]
for _cid, _ok, _what in (("listed_aims", _ok_listed, "'solely for the purpose of securing A and of meeting B' read as one or both of "
                                                    "the two listed aims, and no other"),
                         ("both_aims", _ok_both, "'solely for the purpose of securing A and of meeting B' read as requiring both "
                                                 "aims, and no other")):
    add("u111", _cid, forbidden("u111", _cid, "limitation_permitted", "{0} be imposed",
                                "The limitation on the person's exercise of a right or freedom is permitted to be imposed",
                                U111_CASE, _U111_OPEN, guard=("not", _ok)),
        f"Article 29(2): 'everyone shall be subject only to such limitations as are determined by law solely for the purpose of "
        f"securing due recognition and respect for the rights and freedoms of others and of meeting the just requirements of "
        f"morality, public order and the general welfare in a democratic society': {_what}; a limitation that is not determined "
        "by law, or serves another purpose, or fails the aims is not permitted (the necessary conditions of the sentence; a "
        "limitation that meets them is not decided by this rule). Strict, because the text states no exception. " + NOBEARER)
ORDER["u111"] = ["listed_aims", "both_aims"]
REASON["u111"] = ("the State and anyone readings are gone (the sentence names no one who limits); the two readings of the aims "
                  "('A and B' as one or both, or as both) are kept as two bearer-less prohibitions of a limitation that fails the conditions")

# ------------------------------------------------------------------ u099/u100: passive duties, bearer-less only
KEEP["u099a"], ORDER["u099a"] = ["unassigned"], ["unassigned"]
KEEP["u099b"], ORDER["u099b"] = ["unassigned"], ["unassigned"]
KEEP["u100a"], ORDER["u100a"] = ["unassigned"], ["unassigned"]
REASON["u099a"] = ("the State reading is gone (the passive names no one who makes education available); only the bearer-less "
                   "obligation over the education kinds is left")
REASON["u099b"] = ("the State reading is gone (the passive names no one who makes higher education accessible); one reading is "
                   "left: every person must be given equal access to higher education on the basis of merit")
REASON["u100a"] = ("the State reading is gone, and so is the `education` reading, which replaced 'shall be directed' by a plain "
                   "statement that education is directed (weaker than the text); only the bearer-less obligation is left")
COURSE = "course_of_education"
_u100b_sort = sort("course of education", "courses of education", "one course of education")
add("u100b", "unassigned", dict(
    sorts={COURSE: _u100b_sort},
    predicates={"education_directed_to_respect_for_rights_required": regulated(
        [COURSE], "obligation",
        "The course of education is required to be directed to the strengthening of respect for human rights and fundamental "
        "freedoms", "{0} be directed to strengthen respect of human rights plus fundamental freedoms")},
    rule=norm("u100b-unassigned", "education_directed_to_respect_for_rights_required", True, Top()),
    open=["rights_and_freedoms_set_forth"], soft=False,
    witnesses=[({COURSE: ["c0"]}, {}, [("education_directed_to_respect_for_rights_required", ("c0",), ("SETTLED", True))])]),
    "Article 26(2): 'and to the strengthening of respect for human rights and fundamental freedoms', with no one assigned to direct "
    "education; the subject and 'shall' are carried from u100a (not a checked reference): every course of education is required to "
    "be directed so. The act phrase keeps 'fundamental' in 'fundamental freedoms' and joins the two objects with 'plus' (the 80-byte act limit leaves no room for 'as well as'). " + NOBEARER)
ORDER["u100b"] = ["unassigned"]
REASON["u100b"] = ("audit: the act phrase dropped 'fundamental' from 'fundamental freedoms' and the `education` reading weakened 'shall "
                   "be directed' to a plain statement; both fixed, and the State reading is gone (the passive names no bearer)")

# ------------------------------------------------------------------ u098
KEEP["u098"], ORDER["u098"] = ["person_attends"], ["person_attends"]
REASON["u098"] = ("the State reading (a duty to make education compulsory) and the parent-or-guardian reading are gone: the words say "
                  "education is compulsory, not who makes it so or who sees to it; what 'compulsory' says is that the persons it "
                  "applies to are required to attend, which is the reading left")

# ------------------------------------------------------------------ rights: entitlement and liberty stay, claims lose their bearers
# unit: (what, [(cid, stem, act)...], open terms, comb holder phrase or None)
SPARED, ENABLED = "be spared", "be enabled"
RIGHT = {
    "u022a": ("the right to life", [
        ("claim_negative", "life_spared_required", "{0} be spared deprivation of life"),
        ("claim_positive", "life_protected_required", "{0} have their life protected"),
        ("claim_combined", "life_spared_and_protected_required", "{0} be spared deprivation of life as well as have it protected")], []),
    "u022b": ("the right to liberty", [
        ("claim_negative", "liberty_spared_required", "{0} be spared deprivation of liberty"),
        ("claim_positive", "liberty_secured_required", "{0} have their liberty secured"),
        ("claim_combined", "liberty_spared_and_secured_required",
         "{0} be spared deprivation of liberty as well as have it secured")], []),
    "u022c": ("the right to security of person", [
        ("claim_negative", "security_spared_required", "{0} be spared endangerment of the security of their person"),
        ("claim_positive", "security_safeguarded_required", "{0} have the security of their person safeguarded"),
        ("claim_combined", "security_spared_and_safeguarded_required",
         "{0} be spared endangerment of their security of person as well as have it safeguarded")], []),
    "u029": ("the right to recognition everywhere as a person before the law", [
        ("claim", "recognition_as_person_required", "{0} be recognised everywhere as a person before the law")], []),
    "u032": ("the entitlement without any discrimination to equal protection of the law", [
        ("claim", "equal_protection_required", "{0} be given equal protection of the law without any discrimination")],
        ["discrimination", "equal_protection_of_the_law"]),
    "u033a": ("the entitlement to equal protection against any discrimination in violation of this Declaration", [
        ("claim", "protection_against_discrimination_required",
         "{0} be protected equally against discrimination in violation of this Declaration")],
        ["discrimination", "equal_protection_of_the_law"]),
    "u033b": ("the entitlement to equal protection against any incitement to such discrimination", [
        ("claim", "protection_against_incitement_required", "{0} be protected equally against incitement to such discrimination")],
        ["discrimination", "equal_protection_of_the_law"]),
    "u048": ("the right to freedom of movement and residence within the borders of each state", [
        ("claim_negative", "movement_spared_required", "{0} be left free to move as well as reside within the borders of each state"),
        ("claim_positive", "movement_enabled_required",
         "{0} be enabled to move as well as reside within the borders of each state"),
        ("claim_combined", "movement_free_and_enabled_required", "{0} be left free as well as enabled to exercise the right")], []),
    "u049": ("the right to leave any country, including his own, and to return to his country", [
        ("claim", "leave_and_return_required", "{0} be left free to leave any country as well as return to their own")], []),
    "u051": ("the right to seek and to enjoy in other countries asylum from persecution", [
        ("claim_avoid", "asylum_free_required", "{0} be left free to seek as well as enjoy asylum from persecution abroad")],
        ["persecution"]),
    "u063": ("the right to own property alone as well as in association with others", [
        ("claim_negative", "property_free_required", "{0} be left free to own property alone as well as in association with others"),
        ("claim_positive", "property_enabled_required", "{0} be enabled to own property alone as well as in association with others"),
        ("claim_combined", "property_free_and_enabled_required", "{0} be left free as well as enabled to exercise the right")], []),
    "u066": ("the right to freedom of thought, conscience and religion", [
        ("claim_negative", "thought_spared_required", "{0} be spared denial of freedom of thought conscience as well as religion"),
        ("claim_positive", "thought_assured_required", "{0} be assured freedom of thought conscience as well as religion"),
        ("claim_combined", "thought_spared_and_assured_required", "{0} be spared denial of as well as assured the right")], []),
    "u070": ("the right to freedom of opinion and expression", [
        ("claim_negative", "opinion_spared_required", "{0} be spared denial of freedom of opinion as well as expression"),
        ("claim_positive", "opinion_assured_required", "{0} be assured freedom of opinion as well as expression"),
        ("claim_combined", "opinion_spared_and_assured_required", "{0} be spared denial of as well as assured the right")], []),
    "u073": ("the right to freedom of peaceful assembly and association", [
        ("claim_negative", "assembly_spared_required", "{0} be spared denial of freedom of peaceful assembly as well as association"),
        ("claim_positive", "assembly_assured_required", "{0} be assured freedom of peaceful assembly as well as association"),
        ("claim_combined", "assembly_spared_and_assured_required", "{0} be spared denial of as well as assured the right")], []),
    "u081": ("the right to social security", [
        ("claim", "social_security_required", "{0} be secured social security")], ["social_security"]),
    "u084a": ("the right to work", [
        ("claim_negative", "work_spared_required", "{0} be spared exclusion from work"),
        ("claim_positive", "work_provided_required", "{0} be provided with work"),
        ("claim_combined", "work_spared_and_provided_required", "{0} be spared exclusion from work as well as provided with it")], []),
    "u084b": ("the right to free choice of employment", [
        ("claim_negative", "employment_choice_spared_required", "{0} be spared restriction of the free choice of employment"),
        ("claim_positive", "employment_choice_assured_required", "{0} be assured free choice of employment"),
        ("claim_combined", "employment_choice_spared_and_assured_required", "{0} be spared restriction of as well as assured the right")],
        []),
    "u084c": ("the right to just and favourable conditions of work", [
        ("claim", "conditions_of_work_required", "{0} be secured just as well as favourable conditions of work")],
        ["just_and_favourable_conditions_of_work"]),
    "u084d": ("the right to protection against unemployment", [
        ("claim", "protection_against_unemployment_required", "{0} be protected against unemployment")], []),
    "u087": ("the right to form and to join trade unions for the protection of one's interests", [
        ("claim_negative", "unions_free_required", "{0} be left free to form as well as join trade unions to protect their interests"),
        ("claim_positive", "unions_enabled_required", "{0} be enabled to form as well as join trade unions to protect their interests")],
        []),
    "u096": ("the right to education", [
        ("claim_negative", "education_spared_required", "{0} be spared exclusion from education"),
        ("claim_positive", "education_provided_required", "{0} be provided with education"),
        ("claim_combined", "education_spared_and_provided_required", "{0} be spared exclusion from education as well as provided with it")],
        []),
    "u105a": ("the right freely to participate in the cultural life of the community", [
        ("claim_negative", "culture_free_required", "{0} be left free to take part in the cultural life of the community"),
        ("claim_positive", "culture_enabled_required", "{0} be enabled to take part in the cultural life of the community"),
        ("claim_combined", "culture_free_and_enabled_required", "{0} be left free as well as enabled to exercise the right")], []),
    "u105b": ("the right freely to enjoy the arts", [
        ("claim_negative", "arts_free_required", "{0} be left free to enjoy the arts"),
        ("claim_positive", "arts_enabled_required", "{0} be enabled to enjoy the arts"),
        ("claim_combined", "arts_free_and_enabled_required", "{0} be left free as well as enabled to enjoy the arts")], []),
    "u105c": ("the right freely to share in scientific advancement and its benefits", [
        ("claim_negative", "science_free_required", "{0} be left free to share in scientific advancement as well as its benefits"),
        ("claim_positive", "science_enabled_required", "{0} be enabled to share in scientific advancement as well as its benefits"),
        ("claim_combined", "science_free_and_enabled_required", "{0} be left free as well as enabled to exercise the right")], []),
}
# the units whose existing entitlement / liberty companions are kept as they are
HAS_LIBERTY = {"u048", "u049", "u051", "u063", "u066", "u070", "u073", "u084a", "u084b", "u087", "u105a", "u105b", "u105c"}
CLAIM_WHAT = {
    "claim_negative": "that the person be left free in it, or spared its denial (noninterference)",
    "claim_positive": "that the person be enabled in it, or have it secured (the opportunity or the thing itself, as the right names)",
    "claim_combined": "both the noninterference and the securing together, as one requirement",
    "claim": "what the right names",
    "claim_avoid": "that the person be left free in it (noninterference)"}
# the combined reading of a right whose phrase the 80-byte act cannot carry twice: a person as holder of the right. The sort
# noun may not hold 'the' or 'and' (the English view then falls back to 'entity of sort ...'), so it names the topic; the
# sort description carries the source's whole phrase, and the act carries what the noun leaves out.
GENERIC = "{0} be left free as well as enabled to exercise the right"
HOLDER = {
    "u022c": ("holder of right to security of person", GENERIC),
    "u048": ("holder of right to freedom of movement as well as residence",
             "{0} be left free as well as enabled to use it within the borders of each state"),
    "u063": ("holder of right to own property", "{0} be left free plus enabled to own alone as well as in association with others"),
    "u066": ("holder of right to freedom of thought conscience religion", GENERIC),
    "u070": ("holder of right to freedom of opinion as well as expression", GENERIC),
    "u073": ("holder of right to peaceful assembly as well as association", GENERIC),
    "u084b": ("holder of right to free choice of employment", GENERIC),
    "u105a": ("holder of right freely to take part in cultural life", "{0} be left free as well as enabled to exercise it in the community"),
    "u105c": ("holder of right freely to share in scientific advancement", "{0} be left free as well as enabled to share in it as well as its benefits")}
HOLDER_COMBINED = set()
for _uid, (_what, _claims, _opens) in RIGHT.items():
    for _cid, _stem, _act in _claims:
        holder = None
        if _cid == "claim_combined" and _uid in HOLDER:
            _noun, _act = HOLDER[_uid]
            _key = _noun.replace(" ", "_")
            holder = (_key, _noun, _noun.replace("holder", "holders", 1),
                      f"a person, as the holder of {_what} (the sentence gives it to everyone)")
            HOLDER_COMBINED.add(_uid)
        else:
            assert len(_act.encode()) <= 80, (_uid, _cid, _act)
        add(_uid, _cid, claim(_uid, _cid, _stem, _act, list(_opens), holder=holder),
            f"Claim reading of {_what} (reading '{_cid}'): it is required, of no stated party, {CLAIM_WHAT[_cid]}. The words give the "
            "right to everyone and name no one who must act, so the reading names no bearer and no State, group or person; it "
            "holds of every person" + (" (every holder of the right, a person; the sort name carries the source's phrase because "
                                       "the 80-byte act phrase cannot carry it twice)" if holder else "") + ".")
    ORDER[_uid] = (["entitlement"] + [c for c, _, _ in _claims] + (["liberty"] if _uid in HAS_LIBERTY else []))
    KEEP[_uid] = ["entitlement"] + (["liberty"] if _uid in HAS_LIBERTY else [])
    REASON[_uid] = ("the State and anyone readings are gone (the words name no one who must act: a duty on every State is outside "
                    "knowledge, a duty on every State, group and person names a bearer the words do not); the claim readings are "
                    "now bearer-less obligations over every person; the entitlement" + (" and the liberty" if _uid in HAS_LIBERTY else "")
                    + " are as before")
ORDER["u049"] = ["entitlement", "claim", "liberty"]
ORDER["u051"] = ["entitlement", "liberty", "claim_avoid"]

# u081: the claim and its reading within the resources clause
add("u081", "claim_within_resources",
    claim("u081", "claim_within_resources", "social_security_in_accordance_with_resources_required",
          "{0} be secured social security in accordance with the resources of each State",
          ["social_security", "organization_and_resources_of_each_state"]),
    "Claim reading of the right to social security qualified by Article 22's clause 'in accordance with the organization and "
    "resources of each State': it is required, of no stated party, that the person be secured social security in accordance with the "
    "organization and resources of each State (the open term organization_and_resources_of_each_state). The clause belongs "
    "grammatically to the entitlement of u082, so this candidate is one of two readings of its reach, not the only one. The "
    "States named are named by the clause, not made bearers.")
ORDER["u081"] = ["entitlement", "claim", "claim_within_resources"]

# ------------------------------------------------------------------ u035: the tribunals are named by the words
KEEP["u035"] = ["tribunal_claim"]
add("u035", "entitlement",
    RS.entitlement("u035", "entitlement", "has_the_right_to_an_effective_remedy",
                   "{0} has the right to an effective remedy by the competent national tribunals for acts violating the "
                   "fundamental rights granted to the person by the constitution or by law",
                   "The person has the right to an effective remedy by the competent national tribunals for acts violating the "
                   "fundamental rights granted to the person by the constitution or by law",
                   ["effective", "competent", "fundamental_rights_granted"]),
    "Entitlement reading of Article 8: every person has the right to an effective remedy by the competent national tribunals for acts "
    "violating the fundamental rights granted him by the constitution or by law; the words name the tribunals as the givers of the "
    "remedy but say nothing of what anyone must do, so the candidate names no bearer (a plain regulated predicate the rule makes true "
    "of every person); the responsibility stays unspecified.")
ORDER["u035"] = ["entitlement", "tribunal_claim"]
REASON["u035"] = ("the State reading (a duty to ensure that tribunals give a remedy) is gone: the words name the tribunals, not the "
                  "State, as the givers; the entitlement reading, which every other 'has the right' unit has, is added next to the tribunal claim")

# ------------------------------------------------------------------ u046: Article 12, second sentence (audit repair)
# the intrusion case sort and base predicates, taken from the existing candidates (the same words as before)
import json as _json
from pathlib import Path as _Path

_HERE = _Path(__file__).resolve().parent
_PREV = _HERE / "previous-20261007T1800Z" / "readings"


def _load_u046_base():
    meta = _json.loads((_PREV / "u046.state_arbitrary.ve.md").read_bytes()[4:].split(b"\n---\n", 1)[0])
    voc = meta["environment"]["vocabulary"]
    sorts = {"intrusion": voc["sorts"]["intrusion"]}
    preds = {n: p for n, p in voc["predicates"].items() if "regulated" not in p}
    return sorts, preds


_S046, _P046 = _load_u046_base()
_SCOPE_ANY = U.OR(U.OR(U.OR(("p", "concerns_privacy"), ("p", "concerns_family")), ("p", "concerns_home")),
                  ("p", "concerns_correspondence"))
_ATTACK = U.OR(("p", "is_attack_upon_honour"), ("p", "is_attack_upon_reputation"))
_G046 = {"any": U.OR(_SCOPE_ANY, _ATTACK), "arbitrary": U.OR(U.AND(_SCOPE_ANY, ("p", "is_arbitrary")), _ATTACK)}
_EX046 = [["concerns_privacy", "is_arbitrary"], ["concerns_home"], ["is_attack_upon_honour"], ["is_arbitrary"], []]


def _u046_spec(cid, scope, role):
    stem = "has_the_right_to_protection_of_the_law_against" if role == "plain" else "protection_of_the_law_against_required"
    preds = dict(_P046)
    if role == "plain":
        preds[stem] = {"arguments": ["intrusion"],
                       "description": "The person on whom the intrusion falls has the right to the protection of the law against it",
                       "verbalisation": "{0} is an intrusion against which its victim has the right to the protection of the law",
                       "regulated": {"role": "plain", "default": "unspecified"}}
    else:
        preds[stem] = regulated(["intrusion"], "obligation",
                                "It is required, of no stated party, that the intrusion be covered by the protection of the law",
                                "{0} be covered by the protection of the law")
    guard = _G046[scope]
    elems = [f"c{i}" for i in range(len(_EX046))]
    rels = {n: [[e] for e, t in zip(elems, _EX046) if n in t] for n in _P046}
    checks = [(stem, (e,), ("SETTLED", True) if holds(guard, set(), set(t)) else ("UNDECIDED", None))
              for e, t in zip(elems, _EX046)]
    return dict(sorts=dict(_S046), predicates=preds, rule=norm(slug(f"u046-{cid}"), stem, True, U.ast(guard, V0, V0)),
                open=["arbitrary"], soft=False, witnesses=[({"intrusion": elems}, rels, checks)])


for _cid, _scope, _role in (("entitlement_arbitrary", "arbitrary", "plain"), ("entitlement_any", "any", "plain"),
                            ("claim_arbitrary", "arbitrary", "obligation"), ("claim_any", "any", "obligation")):
    _kind = "Entitlement" if _role == "plain" else "Claim"
    _scope_why = ("'such interference' is the arbitrary interference with privacy, family, home or correspondence that the preceding "
                  "sentence names (arbitrariness included), and the attacks upon honour and reputation"
                  if _scope == "arbitrary" else
                  "'such interference' names only the four domains of the preceding sentence (privacy, family, home, correspondence), "
                  "whether arbitrary or not, and the attacks upon honour and reputation")
    _what = ("each person on whom an intrusion in scope falls has the right to the protection of the law against it (the right, not "
             "the fact that the law protects: the entitlement stands when no protection is given)" if _role == "plain" else
             "it is required, of no stated party, that each intrusion in scope be covered by the protection of the law")
    add("u046", _cid, _u046_spec(_cid, _scope, _role),
        f"{_kind} reading of Article 12, second sentence: {_what}; {_scope_why}. " + (NOBEARER if _role != "plain" else
            "The words name no one who must protect, so the candidate names no bearer."))
ORDER["u046"] = ["entitlement_arbitrary", "entitlement_any", "claim_arbitrary", "claim_any"]
REASON["u046"] = ("audit: the entitlement candidates said the law protects the person (a fact) rather than that the person has a right "
                  "to its protection; they now state the right, which stands when no protection is given; the State readings are "
                  "replaced by bearer-less claims (the words say 'the protection of the law', no State)")

# ------------------------------------------------------------------ u077: Article 21(2) (audit repair)
for _kind, _sing in (("nationality", "country of nationality"), ("residence", "country of residence")):
    add("u077", f"entitlement_{_kind}", RS.entitlement(
        "u077", f"entitlement_{_kind}", f"has_right_to_equal_public_service_access_{_kind}",
        f"{{0}} has the right of equal access to public service in their {_sing}",
        f"The person has the right of equal access to public service in the person's {_sing}", []),
        f"Entitlement reading of Article 21(2) with 'his country' as the {_sing}: every person has the right of equal access to public "
        "service there; the words name no one who must give the access, so the candidate names no bearer (the responsibility stays "
        "unspecified). 'His country' is the only thing the words leave to a reading; nationality and residence are the two meanings "
        "the English phrase has.")
    add("u077", f"claim_{_kind}", claim(
        "u077", f"claim_{_kind}", f"equal_public_service_access_{_kind}_required",
        f"{{0}} be given equal access to public service in their {_sing}", []),
        f"Claim reading of Article 21(2) with 'his country' as the {_sing}: it is required, of no stated party, that the person be "
        "given equal access to public service there. " + NOBEARER)
ORDER["u077"] = ["entitlement_nationality", "entitlement_residence", "claim_nationality", "claim_residence"]
REASON["u077"] = ("audit: both candidates made a country the bearer and the entitlement that leaves the responsibility unspecified was "
                  "missing; the country-as-bearer readings are gone and each reading of 'his country' (nationality, residence) now has "
                  "an entitlement and a bearer-less claim")

REASON["u110"] = ("audit: `identified_community` kept the relative clause out of what is said (it stays true when development is "
                  "possible nowhere); it is removed, and the two readings left (a community per person; one community for everyone) "
                  "keep the clause, with its 'alone', as part of what is asserted")
REPAIRED = sorted(set(ORDER) | {"u110"})
AUDIT_REJECTED = ["u046", "u063", "u077", "u100b", "u105c", "u110"]
