# Coverage

Labels follow the DIRECT / REIFIED / OPAQUE / NO scheme from
`experiments/E0/SECOND_RATER.md`, relative to the enabled profile
(`relational-fol@0` only — this document needs no transitive closure; unlike
the constitution excerpt it needs `order@0`-style arithmetic in several
places, and `docs/spec/v0.1-profiles.md` states plainly that `order@0` "is
designed but NOT implemented", so those rows are NO or OPAQUE, never a
working numeric REIFIED). Rows follow `source.md`'s 14-sentence numbering,
split into lettered clauses where a sentence conjoins more than one
independently-labelled claim.

| # | Source clause (short form) | Label | Notes |
|---|---|---|---|
| 1 | S1a — "The Fed raised interest rates on Wednesday, Sept 16, 2026." | DIRECT | claims.ve #1: `raised_on(@fed, @sept16)`. A flat ground binary fact between two named things; no invented event entity needed. |
| 2 | S1b — "...signaled that further rate increases could come in the following months." | NO | Hedge-on-a-hedge ("flagged"/"signaled" a possibility) plus a vague, unspecified future window ("coming months"). |
| 3 | S1c — "new Fed chief Kevin Warsh joined a unanimous vote." | REIFIED | claims.ve #2: `unanimous(@rate_decision)` (flat fact, no different in kind from `deployed(service)` in the spec's own worked example) and `voted_for(@warsh, @rate_decision)`, reifying the vote as a `decision` entity. |
| 4 | S1d — "...which Reuters characterizes as an implicit acknowledgment that the Trump administration has not yet succeeded in controlling inflation." | NO | Reporter's own hedged inferential gloss ("effectively acknowledges"), not an attributed quote; embeds an evaluative "inability to control." |
| 5 | S2a — "President Trump had promised to lower prices." | OPAQUE | claims.ve #3: `promised(@trump, @lower_prices_goal)`. The commissive force of "promised" and the content of the goal are both opaque; named in the predicate's description. |
| 6 | S2b — "...the combined effect of tariffs, an energy-price shock..., and AI-driven capital spending kept inflation pressure high enough that the Fed judged a... increase necessary." | NO | Threshold-causal claim ("kept X high enough that... necessary") — the "causation" gap category from the brief. |
| 7 | S2c — "...taking the target range to 3.75%-4.00%." | REIFIED | claims.ve #4: `raised_to(@fed, @r375_400)`. The specific range is reified as an opaque named tag (`r375_400`), not a pair of numbers — see GAPS.md #1. |
| 7b | S2c (magnitude) — "a quarter-percentage-point rate increase" | NO | The *size* of the move (the arithmetic difference between the old and new range) is not stated anywhere in this vocabulary; see GAPS.md #1. |
| 8 | S3 — "16 of the 18 FOMC policymakers expect... at least one more... increase..., with only 2 of the 18 expecting rates to stay." | NO | Cardinality/counting quantifiers ("16 of 18", "2 of 18") — v0 has only ∀/∃, no "exactly n of m." See GAPS.md #2. |
| 9 | S4 — "Warsh again did not submit an individual rate projection." | OPAQUE | claims.ve #5: `not submitted_projection(@warsh, @sept_meeting)`. The core negative fact is reified cleanly; "apparently" (an evidentiality hedge on the reporter's own claim) and "again" (an implicit comparison to a past, unenumerated pattern of meetings) are dropped — named here, not silently lost. |
| 10 | S5a — "This was the first policy change of Warsh's tenure." | OPAQUE | claims.ve #6: `is_first_under(@rate_decision, @warsh)`. Hides an ordinal comparison against an unenumerated sequence of other decisions (a ranking claim, not a flat fact) — see GAPS.md #2. |
| 11 | S5b — "he took office in late May 2026 after Trump selected him." | REIFIED | claims.ve #7: `appointed_by(@warsh, @trump)` and `took_office_in(@warsh, @late_may_2026)`. "Late May" reified as one opaque imprecise-date tag rather than an exact date — noted, not hidden. |
| 12 | S5c — "...at the time expecting he would cut rates." | NO | Embedded counterfactual-flavoured attitude report ("an expectation that he would..."). |
| 13 | S6 — "...the policy rate projected to reach the 4.00%-4.25% range by the end of 2026 and to remain there through... 2027." | REIFIED | claims.ve #8: `projected_for(@r400_425, @y2026)` and `projected_for(@r400_425, @y2027)`. Two more opaque range/year tags, ground facts only. |
| 14 | S6 framing — "...opening the door on tighter monetary policy..." | NO | Figurative/metaphorical language ("opening the door on"), not a literal claim with stable truth conditions. |
| 15 | S7 — the FOMC statement quote: "Today's policy action will support a timelier return to the Committee's 2% goal." | OPAQUE | claims.ve #9: `stated(@fed, @statement_timelier)`. The attribution event (who said something, when) is a useful, checkable skeleton; the quoted propositional content is fully opaque, hidden inside the constant `@statement_timelier` — this is the paradigm "attribution" gap; see GAPS.md #3. |
| 16 | S8a — "The statement gave no forward guidance..., which is Warsh's preference." | NO | Negative existential over a vague category ("any forward guidance") plus an attributed preference/attitude. |
| 17 | S8b — "...this is likely to ease prior doubts that Warsh would avoid tightening policy out of deference to Trump." | NO | Hedged prediction ("is likely to"), an embedded attitude ("doubts that... would"), and a motivational/causal relation ("out of deference to"). |
| 18 | S9a — "The new statement dropped a reference, present in the previous statement, that had attributed elevated inflation partly to 'supply shocks'." | REIFIED | claims.ve #10: `attributes_to(@prev_statement, @supply_shocks)` and `not attributes_to(@new_statement, @supply_shocks)`. Reifies "before" and "after" as two distinct named `text` entities — a workable general technique for one-off change-over-time facts; see GAPS.md #4. |
| 19 | S9b — "...which Reuters reads as a signal that policymakers... now see price pressures as broader-based." | NO | Vague evaluative framing ("a nod to concerns... too broad for comfort") plus an unenumerated generic "policymakers." |
| 20 | S10 — "Warsh is scheduled to hold a press conference starting at 2:30 p.m. EDT (18:30 GMT)." | REIFIED | claims.ve #11: `scheduled_for(@press_conference, @t1430edt)`, `scheduled_for(@press_conference, @t1830gmt)`, and `@t1430edt equals @t1830gmt` — the two timezone labels are modelled as two constants denoting the *same* domain element, so the stated timezone equivalence is a genuine, checked equality, not just two independent facts. |
| 21 | S11 — "...raised the estimate of PCE inflation to 3.7%, up from the 3.6% projected... in June." | REIFIED | claims.ve #12: `exceeds(@pce_sep, @pce_jun)`. The two percentages are opaque tags; `exceeds` is a hand-populated ground fact for this one named pair only, not arithmetic — see GAPS.md #1. |
| 22 | S12a — "Inflation is now not projected to reach the Fed's 2% target until 2029." | REIFIED | claims.ve #13: `projected_year(@two_percent_target, @y2029)`. |
| 22b | S12b — "...a year later than previously expected." | NO | The comparandum (the previously-expected year) is not stated anywhere in this excerpt, and "a year later" is itself an arithmetic delta claim; doubly unformalisable here. |
| 23 | S13 — "Projected economic growth was raised... from 2.2% to 2.3%; the projected... unemployment rate was lowered... from 4.3% to 4.1%." | REIFIED | claims.ve #14: `exceeds(@growth_sep, @growth_jun)` and `exceeds(@unemployment_jun, @unemployment_sep)`. Two more hand-populated ground comparisons. |
| 24 | S14 — Warsh's pledge quote: "clearly and at sufficient speed." | OPAQUE | claims.ve #15: `pledged(@warsh, @pledge_lower_inflation)`. Same pattern as row 15: attribution event checkable, quoted content opaque. |

**Totals:** 26 rows (14 source sentences, several split into lettered
clauses). 1 DIRECT, 11 REIFIED, 3 OPAQUE, 11 NO.

All 15 `claims.ve` statements parse and `check` against `environment.json`
(`assurance: experimental`, `language: accepted`). `model-true.json`
satisfies all 15 (`Satisfied`, non-vacuously). `model-false.json` differs
only by removing the single `["pce_sep", "pce_jun"]` tuple from the `exceeds`
relation, which falsifies statement 12 alone (checked individually:
statements 1-11 and 13-15 remain `True`) — confirming the fifteen statements
are logically independent, not a single tautology.

## What REIFIED/OPAQUE mean here, honestly

Unlike the constitution excerpt (a normative document, dominated by OPAQUE
and NO), this news article is dominated by REIFIED and even has one clean
DIRECT statement. That is not a coincidence: hard-news reporting is
overwhelmingly ground factual claims about specific named entities and
events ("X did Y on date Z", "the statement said A", "figure F went from
V1 to V2") — exactly the shape relational FOL over a finite structure is
built for. Every REIFIED row here reifies one of three things: (a) an event
as an entity (`rate_decision`, `press_conference`), (b) a specific quantity
or range as an opaque named tag rather than a computed value
(`r375_400`, `pce_sep`), or (c) a point in time as an opaque tag
(`sept16`, `late_may_2026`). None of these hide the *substance* of the
clause they formalise — they hide only the internal structure of the tag
itself (what "3.75%-4.00%" numerically *is*, what "September 16" computes
to relative to another date), which is precisely the numeric/temporal gap
documented in `GAPS.md`, not a shortcut around the clause's own claim.

The three OPAQUE rows (9, 15, 24) all involve attribution: an entity issuing
or receiving a statement, pledge, or promise. In every case the *event* of
attribution is REIFIED (who said/pledged/promised something, and to/about
what named goal or statement) while the *content* of what was said is a
single opaque constant. This is an honest, deliberate choice, not
carelessness: v0 has no way to embed a formula as the object of another
predicate (no quotation, no propositional content as a first-class term), so
there is no faithful way to make the content checkable without inventing a
construct that does not exist yet (see GAPS.md #3).

The 11 NO rows split roughly three ways: numeric/cardinality claims this
vocabulary's opaque-tag trick cannot reach at all (row 8's "16 of 18", row
7b's "quarter point," row 22b's "a year later") because they require
comparing or counting quantities not already named as fixed tags; hedged,
causal, or attitude-laden reporter framing (rows 2, 4, 6, 12, 16, 17, 19);
and one figurative expression (row 14). See `GAPS.md` for the ranked detail.
