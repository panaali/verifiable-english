"""The units the previous run could not state because a strict and a defeasible reading could not share a reading set.

Composition S1 (readings@1) lets one reading set hold both. Each unit below becomes an open set whose candidates are
content-bearing (a plain norm for a 'shall' duty, a right block for a 'has the right to' entitlement) over the axes the
source leaves open: bearer (a state, or every state, group and person), force (strict, or defeasible with an open
exception whose decider the source does not name), and, for entitlements, polarity (avoid denying, or secure).

Every act phrase is the translator's wording of the source clause under the act-phrase grammar (at most 80 bytes, no
comma, none of: true false is equals not and or if then for every there exists believes must eventually no). 'or'
under a negation is worded 'as well as'. What the phrase has to shorten is carried by a named open term and by the
predicate description, which quotes the full clause.

Fields: kind ('norm' or 'right'); full (the source clause); word (the source word, when the unit holds it);
readings: [(id, predicate stem, act, arguments, bearers, axis label or None)];
polarity: 'both' or the one polarity of an entitlement; open: open terms the unit names; note; elided.
"""
from __future__ import annotations

ARTICLE_22_FACTOR = "the organization and resources of each State (Article 22)"

STATE = "state"
ANYONE = "anyone"

NORM_UNITS = {
    "u020": dict(
        kind="norm", article="Article 2", word="shall", name="no-distinction-by-country-status",
        full="no distinction shall be made on the basis of the political, jurisdictional or international status of the "
             "country or territory to which a person belongs, whether it be independent, trust, non-self-governing or "
             "under any other limitation of sovereignty",
        readings=[("avoid", "avoid_distinction_by_country_status_required",
                   "{0} avoid making any distinction against {1} by the status of their country",
                   ("bearer", "person"), (STATE, ANYONE), None)],
        open=["status_of_country_or_territory"],
        elided="'country or territory' is worded 'their country'; the kinds of status (political, jurisdictional, "
               "international; independent, trust, non-self-governing, any other limitation of sovereignty) are the "
               "factors of the open term status_of_country_or_territory"),
    "u024": dict(
        kind="norm", article="Article 4", word="shall", name="no-slavery-or-servitude",
        full="No one shall be held in slavery or servitude",
        readings=[("avoid", "avoid_slavery_or_servitude_required", "{0} avoid holding {1} in slavery as well as servitude",
                   ("bearer", "person"), (STATE, ANYONE), None)],
        open=["slavery", "servitude"], elided="none"),
    "u025": dict(
        kind="norm", article="Article 4", word="shall", name="slavery-and-slave-trade",
        full="slavery and the slave trade shall be prohibited in all their forms",
        readings=[("prohibit", "prohibit_slavery_and_slave_trade_required",
                   "{0} prohibit slavery as well as the slave trade in all their forms", ("bearer",), (STATE,), "prohibit"),
                  ("avoid", "avoid_slavery_and_slave_trade_required",
                   "{0} avoid slavery as well as the slave trade in all their forms", ("bearer",), (STATE, ANYONE), "avoid")],
        open=["slavery", "slave_trade"],
        elided="none: the passive 'shall be prohibited' does not say who prohibits, so one reading is a duty on states to "
               "prohibit (in law) and the other a duty on a bearer to avoid them; the source names neither bearer"),
    "u027": dict(
        kind="norm", article="Article 5", word="shall", name="no-torture-or-ill-treatment",
        full="No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment",
        readings=[("avoid", "avoid_torture_or_ill_treatment_required",
                   "{0} avoid subjecting {1} to torture as well as ill-treatment", ("bearer", "person"), (STATE, ANYONE), None)],
        open=["ill_treatment"],
        elided="'cruel, inhuman or degrading treatment or punishment' is worded 'ill-treatment', whose factors are the "
               "source's own three adjectives and 'treatment or punishment'"),
    "u037": dict(
        kind="norm", article="Article 9", word="shall", name="arbitrary-arrest-detention-exile",
        full="No one shall be subjected to arbitrary arrest, detention or exile",
        readings=[("avoid", "avoid_arbitrary_arrest_detention_exile_required",
                   "{0} avoid arbitrarily arresting {1} as well as detaining as well as exiling them",
                   ("bearer", "person"), (STATE, ANYONE), None)],
        open=["arbitrary"], elided="none: 'arbitrary' is carried over all three acts"),
    "u045a": dict(
        kind="norm", article="Article 12", word="shall", name="interference-with-private-life",
        full="No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence",
        readings=[("avoid", "avoid_arbitrary_interference_private_life_required",
                   "{0} avoid arbitrary interference with the private life of {1}", ("bearer", "person"), (STATE, ANYONE), None)],
        open=["arbitrary", "private_life"],
        elided="'privacy, family, home or correspondence' is worded 'private life', whose factors are those four items"),
    "u045b": dict(
        kind="norm", article="Article 12", word=None, name="attacks-upon-honour-reputation",
        full="nor to attacks upon his honour and reputation (No one shall be subjected to ...)",
        readings=[("avoid", "avoid_attacks_upon_honour_and_reputation_required",
                   "{0} avoid attacks upon the honour as well as reputation of {1}", ("bearer", "person"), (STATE, ANYONE), None)],
        open=[], elided="none; the subject and 'shall' are carried from u045a (not a checked reference)"),
    "u055": dict(
        kind="norm", article="Article 15", word="shall", name="no-arbitrary-loss-of-nationality",
        full="No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality",
        readings=[("avoid", "avoid_arbitrary_loss_of_nationality_required",
                   "{0} avoid arbitrarily depriving {1} of nationality as well as barring its change",
                   ("bearer", "person"), (STATE, ANYONE), None)],
        open=["arbitrary"],
        elided="'arbitrarily' is carried over both acts; the source may mean it for the deprivation only"),
    "u059": dict(
        kind="norm", article="Article 16", word="shall", name="marriage-only-with-consent",
        full="Marriage shall be entered into only with the free and full consent of the intending spouses",
        readings=[("avoid", "avoid_marriage_without_free_and_full_consent_required",
                   "{0} avoid entering {1} into marriage without their free as well as full consent",
                   ("bearer", "person"), (STATE, ANYONE), None)],
        open=["free_and_full_consent"],
        elided="'the intending spouses' is the person: each intending spouse is one person; consent of both spouses "
               "is two applications of the duty"),
    "u064": dict(
        kind="norm", article="Article 17", word="shall", name="no-arbitrary-loss-of-property",
        full="No one shall be arbitrarily deprived of his property",
        readings=[("avoid", "avoid_arbitrary_deprivation_of_property_required",
                   "{0} avoid arbitrarily depriving {1} of property", ("bearer", "person"), (STATE, ANYONE), None)],
        open=["arbitrary"], elided="none"),
    "u098": dict(
        kind="norm", article="Article 26", word="shall", name="elementary-education-compulsory",
        full="Elementary education shall be compulsory",
        readings=[("receive", "receive_elementary_education_required", "{0} receive elementary education",
                   ("person",), (None,), "receive",
                   ("of_age_for_elementary_education",
                    "The person is of the age at which elementary education is compulsory, if there is one; the source "
                    "states no age", "{0} is of the age for elementary education")),
                  ("require", "make_elementary_education_compulsory_required",
                   "{0} make elementary education compulsory", ("bearer",), (STATE,), "require")],
        open=["compulsory"],
        elided="none: the passive 'shall be compulsory' names no bearer and no age, so one reading is a duty on a person of "
               "the age for elementary education (the open relation of_age_for_elementary_education: the source states no "
               "age) to receive it and the other a duty on states to make it compulsory; who must attend, and up to what "
               "age, is the open term compulsory"),
    "u099a": dict(
        kind="norm", article="Article 26", word="shall", name="technical-education-available",
        full="Technical and professional education shall be made generally available",
        readings=[("make", "make_technical_education_available_required",
                   "{0} make technical as well as professional education generally available", ("bearer",),
                   (STATE, ANYONE), None)],
        open=["generally_available"], elided="none"),
    "u099b": dict(
        kind="norm", article="Article 26", word="shall", name="higher-education-on-merit",
        full="and higher education shall be equally accessible to all on the basis of merit",
        readings=[("make", "make_higher_education_accessible_required",
                   "{0} make higher education equally accessible to all on the basis of merit", ("bearer",),
                   (STATE, ANYONE), None)],
        open=["merit"], elided="none"),
    "u100a": dict(
        kind="norm", article="Article 26", word="shall", name="education-to-personality",
        full="Education shall be directed to the full development of the human personality",
        readings=[("direct", "direct_education_to_personality_required",
                   "{0} direct education to the full development of the human personality", ("bearer",),
                   (STATE, ANYONE), None)],
        open=["full_development_of_the_human_personality"],
        elided="none: the passive 'shall be directed' names no bearer; the duty is read as one on whoever directs education"),
    "u100b": dict(
        kind="norm", article="Article 26", word=None, name="education-to-respect-for-rights",
        full="and to the strengthening of respect for human rights and fundamental freedoms (Education shall be directed ...)",
        readings=[("direct", "direct_education_to_respect_for_rights_required",
                   "{0} direct education to strengthen respect of human rights as well as freedoms", ("bearer",),
                   (STATE, ANYONE), None)],
        open=["rights_and_freedoms_set_forth"],
        elided="'fundamental freedoms' is worded 'freedoms'; the subject and 'shall' are carried from u100a"),
}

RIGHT_UNITS = {
    "u081": dict(
        kind="right", article="Article 22", right="social-security", key="social_security",
        full="Everyone, as a member of society, has the right to social security", polarity="positive",
        pos="{0} secure {1} social security", open=["social_security"],
        elided="none: 'as a member of society' is carried by the predicate and the open term member_of_society"),
    "u084a": dict(
        kind="right", article="Article 23", right="work", key="work", full="Everyone has the right to work",
        polarity="both", neg="{0} avoid barring {1} from work", pos="{0} provide {1} with work", open=[],
        elided="none"),
    "u084b": dict(
        kind="right", article="Article 23", right="free-choice-of-employment", key="free_choice_of_employment",
        full="Everyone has the right to free choice of employment (the right is carried from u084a)", polarity="both",
        neg="{0} avoid restricting the free choice of employment of {1}", pos="{0} secure {1} free choice of employment",
        open=[], elided="none"),
    "u084c": dict(
        kind="right", article="Article 23", right="favourable-work-conditions",
        key="just_and_favourable_conditions_of_work",
        full="Everyone has the right to just and favourable conditions of work (the right is carried from u084a)",
        polarity="positive", pos="{0} secure {1} just as well as favourable conditions of work",
        open=["just_and_favourable_conditions_of_work"], elided="none"),
    "u084d": dict(
        kind="right", article="Article 23", right="unemployment-protection",
        key="protection_against_unemployment",
        full="Everyone has the right to protection against unemployment (the right is carried from u084a)",
        polarity="positive", pos="{0} protect {1} against unemployment", open=[], elided="none"),
    "u087": dict(
        kind="right", article="Article 23", right="trade-unions", key="trade_unions",
        full="Everyone has the right to form and to join trade unions for the protection of his interests",
        polarity="both", neg="{0} avoid barring {1} from forming as well as joining trade unions",
        pos="{0} secure {1} forming as well as joining trade unions", open=[],
        elided="'for the protection of his interests' (the purpose; 'for' is a reserved word of the act-phrase grammar)"),
    "u096": dict(
        kind="right", article="Article 26", right="education", key="education", full="Everyone has the right to education",
        polarity="both", neg="{0} avoid barring {1} from education", pos="{0} secure {1} education", open=[],
        elided="none"),
    "u105a": dict(
        kind="right", article="Article 27", right="cultural-life", key="cultural_life",
        full="Everyone has the right freely to participate in the cultural life of the community", polarity="both",
        neg="{0} avoid barring {1} from taking part in the cultural life of the community",
        pos="{0} secure {1} free participation in the cultural life of the community", open=[], elided="none"),
    "u105b": dict(
        kind="right", article="Article 27", right="enjoyment-of-the-arts", key="enjoyment_of_the_arts",
        full="Everyone has the right freely to enjoy the arts (the right is carried from u105a)", polarity="both",
        neg="{0} avoid barring {1} from enjoying the arts", pos="{0} secure {1} the enjoyment of the arts", open=[],
        elided="none"),
    "u105c": dict(
        kind="right", article="Article 27", right="scientific-advancement", key="scientific_advancement",
        full="Everyone has the right freely to share in scientific advancement and its benefits (the right is carried "
             "from u105a)", polarity="positive",
        pos="{0} secure {1} a share in scientific advancement as well as its benefits", open=[], elided="none"),
}

# Open terms the new units name; every decider is 'unstated' (the source names none).
OPEN_TERMS = {
    "status_of_country_or_territory": [
        "which statuses count: political, jurisdictional, international",
        "whether the country or territory is independent, trust, non-self-governing or under another limitation of sovereignty",
        "whether the status of a territory counts as the status of the country to which a person belongs"],
    "slavery": ["what counts as slavery"],
    "servitude": ["what counts as servitude"],
    "slave_trade": ["what counts as the slave trade", "which forms are meant by 'all their forms'"],
    "ill_treatment": ["which treatment is cruel", "which treatment is inhuman", "which treatment is degrading",
                      "whether punishment is covered as well as treatment"],
    "private_life": ["whether privacy, family, home and correspondence are the whole of it",
                     "what makes interference with each of them arbitrary"],
    "free_and_full_consent": ["what makes consent free", "what makes consent full", "who the intending spouses are"],
    "compulsory": ["who must attend: persons, parents or children", "up to what age", "who makes it compulsory"],
    "generally_available": ["what makes education generally available"],
    "merit": ["what counts as merit", "who judges merit"],
    "full_development_of_the_human_personality": ["what the full development of the human personality requires"],
    "social_security": ["what social security covers"],
    "just_and_favourable_conditions_of_work": ["what makes conditions of work just", "what makes them favourable"],
}
