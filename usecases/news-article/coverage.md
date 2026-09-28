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
| 7 | S2c — "...taking the target range to 3.75%-4.00%." | DIRECT | W6a: unit `s2_range` in `news-w6a.ve.md`, `new_target_lower = 3.75%` and `new_target_upper = 4.00%` (`bp`, coordinates 375 and 400), Lean-admitted; `375 < 400` certified (`N07-order`). A range is two bounds, not a midpoint or a realised rate. Formerly REIFIED (`raised_to(@fed, @r375_400)`, claims.ve #4). |
| 7b | S2c (magnitude) — "a quarter-percentage-point rate increase" | NO | The magnitude token `25:bp` is representable, but the old range endpoint is absent, so the old/new comparison is not stated; no 3.50% is invented. Unit `s2_move` records `missing_old_range`. |
| 8 | S3 — "16 of the 18 FOMC policymakers expect... at least one more... increase..., with only 2 of the 18 expecting rates to stay." | NO | W6a's exact counting is capped at 7 and the direct count (`16 of the 18`) rejects naming `CountingBound`. The plan's target for this row is REIFIED with an unchecked count; no such reification was added, so the row stays NO (unit `s3_count`, `count_exceeds_bound`). |
| 9 | S4 — "Warsh again did not submit an individual rate projection." | OPAQUE | claims.ve #5: `not submitted_projection(@warsh, @sept_meeting)`. The core negative fact is reified cleanly; "apparently" (an evidentiality hedge on the reporter's own claim) and "again" (an implicit comparison to a past, unenumerated pattern of meetings) are dropped — named here, not silently lost. |
| 10 | S5a — "This was the first policy change of Warsh's tenure." | OPAQUE | claims.ve #6: `is_first_under(@rate_decision, @warsh)`. Hides an ordinal comparison against an unenumerated sequence of other decisions (a ranking claim, not a flat fact) — see GAPS.md #2. |
| 11 | S5b — "he took office in late May 2026 after Trump selected him." | REIFIED | claims.ve #7: `appointed_by(@warsh, @trump)` and `took_office_in(@warsh, @late_may_2026)`. "Late May" reified as one opaque imprecise-date tag rather than an exact date — noted, not hidden. |
| 12 | S5c — "...at the time expecting he would cut rates." | NO | Embedded counterfactual-flavoured attitude report ("an expectation that he would..."). |
| 13 | S6 — "...the policy rate projected to reach the 4.00%-4.25% range..." | DIRECT | W6a: unit `s6_range`, `projected_range_lower = 4.00%`, `projected_range_upper = 4.25%`, attributed to the FOMC's projections (`attributed(fomc, expects)`), entering the claim graph only through the bridge leaf `bridge:accepts(fomc,s6_range)`; `400 < 425` certified. Not an observed future rate. Formerly REIFIED (claims.ve #8). |
| 13b | S6 (horizon) — "...by the end of 2026 and to remain there through the end of 2027." | NO | The year labels are exact (`calendar_year` 2026 and 2027, unit `s6_years`, certified `2026 < 2027` through its bridge leaf), but "by the end of" and "remain ... through" are temporal obligations of a projection with no W6a meaning: the unit's meaning is the open term `projection_horizon` (status OPEN). |
| 14 | S6 framing — "...opening the door on tighter monetary policy..." | NO | Figurative/metaphorical language ("opening the door on"), not a literal claim with stable truth conditions. |
| 15 | S7 — the FOMC statement quote: "Today's policy action will support a timelier return to the Committee's 2% goal." | OPAQUE | claims.ve #9: `stated(@fed, @statement_timelier)`. W6a adds the exact goal token: unit `s7_goal`, `statement_goal = 2.00%`, attributed (`attributed(fomc, says)`) and used only through its bridge leaf; with row 24 it certifies that the stated goal equals the pledged level. "Timelier" has no supplied metric (`vague_timelier`), so the quoted content as a whole stays OPAQUE. |
| 16 | S8a — "The statement gave no forward guidance..., which is Warsh's preference." | NO | Negative existential over a vague category ("any forward guidance") plus an attributed preference/attitude. |
| 17 | S8b — "...this is likely to ease prior doubts that Warsh would avoid tightening policy out of deference to Trump." | NO | Hedged prediction ("is likely to"), an embedded attitude ("doubts that... would"), and a motivational/causal relation ("out of deference to"). |
| 18 | S9a — "The new statement dropped a reference, present in the previous statement, that had attributed elevated inflation partly to 'supply shocks'." | REIFIED | claims.ve #10: `attributes_to(@prev_statement, @supply_shocks)` and `not attributes_to(@new_statement, @supply_shocks)`. Reifies "before" and "after" as two distinct named `text` entities — a workable general technique for one-off change-over-time facts; see GAPS.md #4. |
| 19 | S9b — "...which Reuters reads as a signal that policymakers... now see price pressures as broader-based." | NO | Vague evaluative framing ("a nod to concerns... too broad for comfort") plus an unenumerated generic "policymakers." |
| 20 | S10 — "Warsh is scheduled to hold a press conference starting at 2:30 p.m. EDT (18:30 GMT)." | REIFIED | claims.ve #11: `scheduled_for(@press_conference, @t1430edt)`, `scheduled_for(@press_conference, @t1830gmt)`, and `@t1430edt equals @t1830gmt` — the two timezone labels are modelled as two constants denoting the *same* domain element, so the stated timezone equivalence is a genuine, checked equality, not just two independent facts. |
| 21 | S11 — "...raised the estimate of PCE inflation to 3.7%, up from the 3.6% projected... in June." | DIRECT | W6a: unit `s11_pce`, `pce_september_estimate = 3.70%` and `pce_june_estimate = 3.60%`; certified `360 < 370` and the difference `0.10 percentage points` (10 `bp`). Formerly REIFIED (`exceeds(@pce_sep, @pce_jun)`, claims.ve #12). |
| 22 | S12a — "Inflation is now not projected to reach the Fed's 2% target until 2029." | DIRECT | W6a: unit `s12_target`, `target_rate = 2.00%`; the year keeps both readings of "not ... until 2029" in the open reading set `first_target_year` (first projected year equals 2029, or only no earlier than 2029), with a distinguishing model. The certified consequence, first projected target year >= 2029, holds under every reading (`readings:first_target_year@1:all`); which reading is meant stays unresolved in the residual. Formerly REIFIED (claims.ve #13). |
| 22b | S12b — "...a year later than previously expected." | NO | The previously expected year is absent; no 2028 is supplied and a year label is not 365 elapsed days. Unit `s12_later` records `missing_previous_expectation`. |
| 23 | S13 — "Projected economic growth was raised... from 2.2% to 2.3%; the projected... unemployment rate was lowered... from 4.3% to 4.1%." | DIRECT | W6a: units `s13_growth` and `s13_unemployment`, attributed to the projections and used through bridge leaves; certified increase `0.10 percentage points`, decrease `0.20 percentage points` and `410 < 430`, operands in source order. "Slightly" is its own unit (`vague_degree`). Formerly REIFIED (claims.ve #14). |
| 24 | S14 — Warsh's pledge quote: "clearly and at sufficient speed." | OPAQUE | claims.ve #15: `pledged(@warsh, @pledge_lower_inflation)`. W6a adds the exact goal token: unit `s14_goal`, `pledged_goal = 2.00%`, attributed (`attributed(warsh, promised)`), bridge leaf only. "Clearly and at sufficient speed" has no deadline, rate or probability (`vague_pledge_manner`), so the pledge stays OPAQUE. |

**Totals (recounted 2026-09-28 from the rows above):** 27 rows (14 source
sentences, several split into lettered clauses; row 13b is new). 6 DIRECT,
4 REIFIED, 5 OPAQUE, 12 NO. The totals published before W6a (1 DIRECT,
11 REIFIED, 3 OPAQUE, 11 NO) did not match that table's own rows, which
counted 1 DIRECT, 9 REIFIED, 5 OPAQUE and 11 NO. Against that recount, W6a
turns rows 7, 13, 21, 22 and 23 from REIFIED to DIRECT and splits row 13's
horizon into NO row 13b. Rows 7b, 8 and 22b stay NO, and rows 15 and 24 stay
OPAQUE with their goal tokens now exact.

## W6a admitted run (2026-09-28)

[`news-w6a.ve.md`](news-w6a.ve.md), built by
[`build_w6a_document.py`](build_w6a_document.py), is `source.md` byte for byte
(SHA-256 `b905818e…545b`, 5,448 bytes) with a ve-units@1 environment and a
unit partition. Lean's `ve_quantity` admits its claim graph: every fixture
consequence plus the S12 lower bound, with the root the conjunction of those
consequences. Python produces the same report and report id
(`tests/test_w6a_documents.py`). Its distinct leaves are 2 asserted leaves
(rows 7 and 21), 6 bridge leaves (FOMC projections and statement, Warsh's
pledge) and 1 reading-set leaf; the report lists a leaf once per use. The
S1 date and the S12 target are checked units that no consequence cites. The fixture model satisfies every leaf and the root,
by Lean's budgeted evaluation. `ve document check` reports premise status
UNKNOWN: its finite search does not choose integer values; the fixture model
is the non-vacuity evidence.

| Status | Source bytes |
|---|---|
| CHECKED | 507 |
| OPEN | 76 |
| UNFORMALISED | 4,865 |

The CHECKED bytes are exactly the numeric clauses. The OPEN bytes are the S6
horizon (open term `projection_horizon`) and S12's "until 2029" (unresolved
reading set). The UNFORMALISED bytes are the provenance preamble and the
duplicate quotation (2,789 bytes of `meta`), the clauses whose relational
claims are in `claims.ve` on the relational route (reason
`relational_route_claims_ve`), and the residuals named in the table: missing
operands, the 16-of-18 count, and vague degrees. The quantity route's profile
set (`order@0` with `time@0`) is not the relational document's profile set, so
one document cannot yet carry both.

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

Before W6a, the 11 NO rows split roughly three ways: numeric/cardinality claims this
vocabulary's opaque-tag trick cannot reach at all (row 8's "16 of 18", row
7b's "quarter point," row 22b's "a year later") because they require
comparing or counting quantities not already named as fixed tags; hedged,
causal, or attitude-laden reporter framing (rows 2, 4, 6, 12, 16, 17, 19);
and one figurative expression (row 14). See `GAPS.md` for the ranked detail.
