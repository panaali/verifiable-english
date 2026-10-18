"""The 22 units that stay UNFORMALISED after composition S1, each with the blocker that remains.

Before S1 these units, and the 25 now stated, carried one reason: other:force_variants_in_one_reading_set (43 units) or
other:right_lines_in_reading_sets (4). S1 removes that reason. What the 18 force units still lack, and why the 4
inclusion units are still refused, is the second blocker below; it is a measurement of the language, not a choice.

Entry: unit -> (tag in the document's kind, missing feature as the units table writes it, detail).
"""
from __future__ import annotations

INCLUDES_DETAIL = (
    "The inclusion adds lines to a right that the previous unit states as an open reading set. S1 admits right_lines "
    "candidates, but a candidate may use only names that its own document declares (composition-s1.md 4.2), so the "
    "set is refused: `UnknownRight: {right} under rs_{unit}@1:0` (tested on a one-set document built from the previous "
    "run). A fixed right_lines unit would give every candidate of the earlier set one line of one kind and would pick "
    "its incident silently, so it is not offered. The copy mapping from one open set to another is S2.")

BLOCKERS = {
    "u042": ("time", "time",
             "'which did not constitute a penal offence ... at the time when it was committed' compares the time of an act "
             "with the time of the law; time is not expressible, and the clause is 200 bytes. 'Shall' is no longer the "
             "blocker (S1)."),
    "u043": ("time", "time",
             "'a heavier penalty ... than the one that was applicable at the time the penal offence was committed' compares two "
             "penalties (an order on penalties: quantities) and fixes one of them at a past time (time). 'Shall' is no longer "
             "the blocker (S1)."),
    "u078": ("other_grounding_of_authority", "other:grounding_of_authority",
             "'shall be the basis of the authority of government' says what authority rests on: it is no duty of a named bearer "
             "and no link the language states (the nearest feature, causation, does not hold a basis of authority). 'Shall' "
             "is no longer the blocker (S1)."),
    "u079a": ("time", "time",
              "'periodic' elections (time), 'universal and equal suffrage' (equality and counting of votes), 'genuine' (open) "
              "and a second 'shall' inside a relative clause; 'this will' is an anaphor to u078, which is itself blocked. "
              "'Shall' is no longer the blocker (S1)."),
    "u079b": ("other_act_phrase_grammar", "other:act_phrase_grammar",
              "'secret vote or equivalent free voting procedures' is a disjunction of ways; an act phrase cannot hold 'or' "
              "(the u076 precedent). 'Shall' is no longer the blocker (S1)."),
    "u082": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "277 bytes: realization 'through national effort and international co-operation and in accordance with the "
             "organization and resources of each State, of the economic, social and cultural rights indispensable for his "
             "dignity and the free development of his personality'. The means and the resources limit cannot be dropped "
             "(dropping a limit strengthens the entitlement), the object quantifies over rights, and no act phrase of 80 "
             "bytes holds them. Its limit is the clause the other Article 22 to 27 default candidates cite as the factor of "
             "their exception."),
    "u085": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "'equal pay for equal work': 'for' is a reserved word of the act-phrase grammar, and no wording without it keeps "
             "the comparison of pay across persons who do equal work; 'without any discrimination' also needs a place."),
    "u086": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "216 bytes: 'just and favourable remuneration ensuring for himself and his family an existence worthy of human "
             "dignity, and supplemented, if necessary, by other means of social protection' has an outcome clause and a "
             "conditional supplement; no act phrase of 80 bytes holds them and dropping either weakens the right."),
    "u089": ("time", "time",
             "'periodic holidays with pay' (time) and 'reasonable limitation of working hours' (a bound on hours: quantities) "
             "make the right; the clause is also 126 bytes."),
    "u091": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "201 bytes: a standard of living 'adequate for the health and well-being of himself and of his family, including "
             "food, clothing, housing and medical care and necessary social services'; the list and the beneficiary clause "
             "cannot be dropped and 'for' is reserved."),
    "u092": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "163 bytes: security 'in the event of unemployment, sickness, disability, widowhood, old age or other lack of "
             "livelihood in circumstances beyond his control' is a list of events with a condition; 'or' is reserved."),
    "u093": ("other_comparison", "other:comparison",
             "'special care and assistance' is a degree above ordinary care (a comparison), and the entitled parties are "
             "'motherhood and childhood', abstractions with no person-level holder sort."),
    "u094": ("other_comparison", "other:comparison",
             "'the same social protection' is an equality of protection across children 'whether born in or out of wedlock': "
             "a comparison of treatment across a class (the u031 precedent) with a disjunction."),
    "u097": ("quantities", "quantities",
             "'free, at least in the elementary and fundamental stages' states a minimum extent over ordered stages of "
             "education (a bound); stating the minimum alone would drop 'at least'."),
    "u101": ("causation", "causation",
             "'shall promote understanding, tolerance and friendship among all nations, racial or religious groups' is a "
             "causal aim of education, with a list of groups ('or')."),
    "u102": ("causation", "causation",
             "'shall further the activities of the United Nations for the maintenance of peace': furthering activities is a "
             "causal aim, and 'for' is reserved."),
    "u103": ("other_priority_of_rights", "other:priority_of_rights",
             "'a prior right to choose' says the parents' choice takes precedence over some other claim that the source does "
             "not name; no precedence is expressible without naming what it precedes, and 'for' is reserved."),
    "u106": ("other_act_phrase_grammar", "other:act_phrase_grammar",
             "171 bytes: protection of 'the moral and material interests resulting from any scientific, literary or artistic "
             "production of which he is the author'; the production clause cannot be dropped and 'or' is reserved."),
    "u067": ("other_right_lines_across_open_sets", "other:right_lines_across_open_sets",
             INCLUDES_DETAIL.format(right="freedom-of-thought-conscience-and-religion", unit="u067")),
    "u068": ("other_right_lines_across_open_sets", "other:right_lines_across_open_sets",
             INCLUDES_DETAIL.format(right="freedom-of-thought-conscience-and-religion", unit="u068")),
    "u071a": ("other_right_lines_across_open_sets", "other:right_lines_across_open_sets",
              INCLUDES_DETAIL.format(right="freedom-of-opinion-and-expression", unit="u071a")),
    "u071b": ("other_right_lines_across_open_sets", "other:right_lines_across_open_sets",
              INCLUDES_DETAIL.format(right="freedom-of-opinion-and-expression", unit="u071b")),
}

# The 43 units the previous run listed as force-blocked, and the 4 inclusion units.
FORCE_BLOCKED = ("u020 u024 u025 u027 u037 u042 u043 u045a u045b u055 u059 u064 u078 u079a u079b u094 u097 u098 u099a u099b "
                 "u100a u100b u101 u102 u081 u082 u084a u084b u084c u084d u085 u086 u087 u089 u091 u092 u093 u096 u103 "
                 "u105a u105b u105c u106").split()
INCLUDES = "u067 u068 u071a u071b".split()
