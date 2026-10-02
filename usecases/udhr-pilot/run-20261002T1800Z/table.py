"""Hand-authored translation table for the rights pilot (ve-green-risk; unchanged language since ve-green-discourse).

Every act phrase is the translator's wording of a source clause, held to the language's act-phrase grammar
(at most 80 bytes, plain words only, no "and", "or", "for", "no", "not", "is" or "if", each slot once).
Because of that grammar an act phrase can be shorter than the source clause; the full source clause is
carried in the predicate description and in `full` here, and `elided` names what the act phrase leaves out.

Audit repairs (2026-09-30 audit of run 20260930T0600Z): `polarity` is "both" only where the two duties really differ
(avoid harming the right, secure the right). Where "avoid denying X" and "give X" are one duty the unit keeps one
polarity ("positive" or "negative") and carries no polarity label. A scope clause the act phrase cannot hold moves
into a holder sort whose description carries it (`holder_sorts`, prose-scoped like u041); what no slot can hold stays
listed in `elided` and is repeated in every candidate's reason.
"""
from __future__ import annotations

# Right units: the source says "has the right to X" / "is entitled to X" with no weakening word, outside
# Articles 22 to 27. Each unit is a reading set over the axes the text leaves open: the incident (claim or
# liberty), the bearer (a state, or every state and every person) and the polarity (avoid harming X, or
# secure X). Fields:
#   right   right name (kebab)         key    predicate stem (snake)      full   the source clause
#   neg     act for the avoiding duty  pos    act for the securing duty   lib    act for the liberty reading
#   holder  holder sort (default person)
#   polarity "both" (default), "positive" or "negative": which duties are genuinely distinct readings
#   bearers (list, source words) when the source words themselves name the bearer
#   elided  what the act phrases leave to the description (act-phrase grammar limits)
#   open    open terms the unit names
RIGHT_UNITS = {
    "u022a": dict(right="life", key="life", full="the right to life",
                  neg="{0} avoid depriving {1} of life", pos="{0} protect the life of {1}", open=[],
                  note="Article 3: the first of three coordinated rights"),
    "u022b": dict(right="liberty", key="liberty", full="the right to liberty",
                  neg="{0} avoid depriving {1} of liberty", pos="{0} secure the liberty of {1}", open=[],
                  note="Article 3: 'liberty' (elliptical: 'Everyone has the right to' is carried from u022a)"),
    "u022c": dict(right="security-of-person", key="security_of_person", full="the right to security of person",
                  neg="{0} avoid endangering the security of the person of {1}",
                  pos="{0} safeguard the security of the person of {1}", open=[],
                  note="Article 3: 'security of person' (elliptical: 'Everyone has the right to' is carried from u022a)"),
    "u029": dict(right="recognition-as-a-person", key="recognition_as_person",
                 full="the right to recognition everywhere as a person before the law",
                 neg="{0} avoid refusing {1} recognition as a person before the law",
                 pos="{0} recognise {1} everywhere as a person before the law", open=[],
                 polarity="positive",
                 elided="none: 'refusing recognition' and 'recognising' are one duty, so only the positive act is kept",
                 note="Article 6"),
    "u032": dict(right="equal-protection-of-the-law", key="equal_protection",
                 full="to be entitled without any discrimination to equal protection of the law",
                 neg="{0} avoid denying {1} equal protection of the law",
                 pos="{0} give {1} equal protection of the law without any discrimination",
                 open=["discrimination", "equal_protection_of_the_law"], polarity="positive",
                 elided="none: 'avoid denying equal protection' is the same duty as 'give equal protection', so only the positive act is kept",
                 note="Article 7, first sentence, second clause ('All ... are entitled': the subject is carried from u031)"),
    "u033a": dict(right="protection-against-discrimination", key="protection_against_discrimination",
                  full="to be entitled to equal protection against any discrimination in violation of this Declaration",
                  neg="{0} avoid exposing {1} to discrimination in violation of this Declaration",
                  pos="{0} protect {1} equally against discrimination in violation of this Declaration",
                  open=["discrimination", "equal_protection_of_the_law"], polarity="positive",
                  elided="none: 'protection' fixes the positive duty; 'avoid exposing to discrimination' dropped 'equal "
                         "protection' and is no longer a candidate",
                  note="Article 7, second sentence, first clause"),
    "u033b": dict(right="protection-against-incitement", key="protection_against_incitement",
                  full="to be entitled to equal protection against any incitement to such discrimination",
                  neg="{0} avoid inciting discrimination against {1}",
                  pos="{0} protect {1} equally against incitement to such discrimination",
                  open=["discrimination", "equal_protection_of_the_law"], polarity="positive",
                  elided="none in the act phrase: 'such discrimination' keeps the source's anaphor, read as discrimination in "
                         "violation of this Declaration (u033a, not a checked reference); 'protection' fixes the positive duty, "
                         "so 'avoid inciting discrimination' (a narrower duty without 'equal protection') is no longer a candidate",
                  note="Article 7, second sentence, second clause; 'such discrimination' is read from u033a"),
    "u046": dict(right="protection-of-the-law-against-interference", key="protection_against_interference",
                 full="the right to the protection of the law against arbitrary interference with privacy, family, home "
                      "or correspondence and against attacks upon honour and reputation",
                 neg="{0} avoid denying {1} protection by law against arbitrary interference",
                 pos="{0} protect {1} by law against such interference as well as attacks", open=["arbitrary"],
                 polarity="positive",
                 elided="'such interference or attacks' keeps the source's anaphor: it is read as the arbitrary interference "
                        "with privacy, family, home or correspondence (u045a) and the attacks upon honour and reputation (u045b), "
                        "not a checked reference; 'or' is worded 'as well as' (protection against each)",
                 note="Article 12, second sentence"),
    "u048": dict(right="freedom-of-movement-and-residence", key="movement_and_residence",
                 full="the right to freedom of movement and residence within the borders of each state",
                 neg="{0} avoid denying {1} freedom of movement as well as residence within each state",
                 pos="{0} secure {1} freedom of movement as well as residence within each state",
                 lib="{0} move as well as reside within the borders of each state", open=[],
                 elided="'the borders of' in the two duties", note="Article 13(1)"),
    "u049": dict(right="freedom-to-leave-and-return", key="leave_and_return",
                 full="the right to leave any country, including the person's own, and to return to the person's country",
                 neg="{0} avoid barring {1} from leaving any country as well as returning to their own",
                 pos="{0} allow {1} to leave any country as well as return to their own country",
                 polarity="negative",
                 lib="{0} leave any country as well as return to their own country", open=[],
                 elided="'including his own'",
                 note="Article 13(2); 'allow to leave' repeats the negative duty and no securing reading exists, so the "
                      "claim is the avoiding duty only (plus the liberty reading)"),
    "u063": dict(right="ownership-of-property", key="property",
                 full="the right to own property alone as well as in association with others",
                 neg="{0} avoid barring {1} from owning property alone as well as jointly with others",
                 pos="{0} secure the ownership of property by {1} alone as well as with others",
                 lib="{0} own property alone as well as in association with others", open=[],
                 elided="'jointly with others' and 'with others' stand for 'in association with others' in the two duties",
                 note="Article 17(1)"),
    "u066": dict(right="freedom-of-thought-conscience-and-religion", key="thought_conscience_religion",
                 full="the right to freedom of thought, conscience and religion",
                 neg="{0} avoid denying {1} freedom of thought conscience as well as religion",
                 pos="{0} secure {1} freedom of thought conscience as well as religion",
                 lib="{0} enjoy freedom of thought conscience as well as religion", open=[],
                 note="Article 18, first clause (the list is worded without a comma, which the act-phrase grammar forbids)"),
    "u070": dict(right="freedom-of-opinion-and-expression", key="opinion_and_expression",
                 full="the right to freedom of opinion and expression",
                 neg="{0} avoid denying {1} freedom of opinion as well as expression",
                 pos="{0} secure {1} freedom of opinion as well as expression",
                 lib="{0} enjoy freedom of opinion as well as expression", open=[], note="Article 19, first clause"),
    "u073": dict(right="freedom-of-peaceful-assembly-and-association", key="assembly_and_association",
                 full="the right to freedom of peaceful assembly and association",
                 neg="{0} avoid denying {1} freedom of peaceful assembly as well as association",
                 pos="{0} secure {1} freedom of peaceful assembly as well as association",
                 lib="{0} enjoy freedom of peaceful assembly as well as association", open=[], note="Article 20(1)"),
}

# Prose-scoped holder sorts: (singular, plural, description). The description carries a scope clause the act phrase
# cannot hold. The sort has no checked meaning: it is the translator's carrier for the clause (missing feature
# other:structured_right_lines).
HOLDER_SORTS = {}  # none since 2026-10-02: the scope of u035 and u039 moved out of sort descriptions (companions_nd.py guards)

# Article 15(1) is an assertion set, not a right set: "Everyone has the right to a nationality" cannot be a claim on
# every state toward every person (the audit: that strengthens it), and a right block has no way to say "some state".
# The two admissible statements are asserted formulas; the claim reading stays out for want of a bearer-holder relation.
NATIONALITY = dict(
    predicates={
        "has_a_nationality": {"arguments": ["person"], "description": "The person has a nationality",
                              "verbalisation": "{0} has a nationality"},
        "grants_nationality": {"arguments": ["bearer", "person"], "description":
            "The bearer grants the person a nationality", "verbalisation": "{0} grants {1} a nationality"}},
    why={
        "each_person_has_a_nationality": "Article 15(1) read as a statement that each person has some nationality (the "
                                         "right is read as fulfilled for everyone; no bearer is named).",
        "some_state_grants_each": "Article 15(1) read as a statement that for each person some state grants that person "
                                  "a nationality (one state discharges the right; which state is not stated)."},
    note="Article 15(1)")

# Units that fit the rights vocabulary in shape but that this run leaves UNFORMALISED, with the blocker.
BLOCKED_BY_ACT_PHRASE_GRAMMAR = {
    "u076": "'directly or through freely chosen representatives' is a disjunction of ways; act phrases cannot hold 'or'",
    "u108": "the order 'in which the rights and freedoms set forth in this Declaration can be fully realized' does not "
            "fit an 80-byte act phrase without 'in which'-clauses",
}

# Open terms the right units name. Every decider is "unstated": the source names none.
OPEN_TERMS = {
    "discrimination": ["what counts as discrimination", "which distinctions are meant"],
    "equal_protection_of_the_law": ["what makes protection equal", "the comparators"],
    "effective": ["what makes a remedy effective"],
    "competent": ["which national tribunals are competent"],
    "fundamental_rights_granted": ["which rights the constitution or law grants", "which of them are fundamental"],
    "fair": ["what makes a hearing fair"],
    "independent_and_impartial": ["what makes a tribunal independent", "what makes a tribunal impartial"],
    "guarantees_necessary_for_defence": ["which guarantees are necessary for a defence"],
    "arbitrary": ["what makes an interference arbitrary"],
    "persecution": ["what counts as persecution"],
    "full_equality": ["who the comparators are for equality of the hearing", "what full equality requires"],
    "rights_and_freedoms_set_forth": ["which items of the Declaration count as rights and freedoms"],
}
