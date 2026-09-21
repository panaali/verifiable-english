# Rendering (`ve_fluent`, with legend, compact style)

Command:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python -m ve render \
  --env usecases/news-article/environment.json \
  --view ve_fluent --with-legend --legend-style compact \
  usecases/news-article/claims.ve
```

Output:

```
Vocabulary: ve.vocabulary-legend@3; environment: b3f7afa3f97f000698d6fd0e9cd7024a7d7aed4773d2ed0241dabf9f26616371
Sorts:
  cause (noun: "cause"; declared: none) — "A named cause-of-inflation label that a Fed statement may or may not attribute inflation to."
  decision (noun: "decision"; declared: none) — "The Wednesday, September 16, 2026 rate decision, reified as an event-like entity."
  event (noun: "event"; declared: none) — "A scheduled event other than the rate decision itself."
  figure (noun: "figure"; declared: none) — "A specific reported economic statistic (e.g. one quarter's PCE inflation estimate), treated as an opaque tag, not a number."
  goal (noun: "goal"; declared: none) — "A named policy goal or promise the article attributes to someone."
  institution (noun: "institution"; declared: none) — "A named institution in the article (the Federal Reserve / FOMC / 'the central bank', merged into one entity)."
  moment (noun: "moment"; declared: none) — "A date, meeting, or clock time referred to in the article, treated as an opaque tag, not a computable timestamp."
  person (noun: "person"; declared: none) — "A named person in the article."
  rate_range (noun: "rate_range"; declared: none) — "A named federal funds target rate range, treated as an opaque tag, not a pair of numbers."
  text (noun: "text"; declared: none) — "A statement, quoted remark, or pledge, reified as an opaque entity standing for its (unmodelled) propositional content."
  year (noun: "year"; declared: none) — "A calendar year referred to as a target or projection horizon."
Constants:
  @fed : institution — "The Federal Reserve / FOMC / 'the central bank', as referred to in the article."
  @growth_jun : figure — "The June 2026 projection of economic growth (reported as 2.2%)."
  @growth_sep : figure — "The September 2026 projection of economic growth (reported as 2.3%)."
  @late_may_2026 : moment — "The imprecisely named period ('late May') when Warsh took office."
  @lower_prices_goal : goal — "Trump's promised goal of lowering prices."
  @new_statement : text — "The FOMC's September 16, 2026 policy statement, which dropped the 'supply shocks' reference."
  @pce_jun : figure — "The June 2026 projection of PCE inflation (reported as 3.6%)."
  @pce_sep : figure — "The September 2026 projection of PCE inflation (reported as 3.7%)."
  @pledge_lower_inflation : text — "Warsh's quoted pledge to lower inflation 'clearly and at sufficient speed'."
  @press_conference : event — "Warsh's press conference following the rate decision."
  @prev_statement : text — "The FOMC's previous policy statement, which attributed elevated inflation partly to 'supply shocks'."
  @r375_400 : rate_range — "The 3.75%-4.00% target range the Fed moved to on September 16, 2026."
  @r400_425 : rate_range — "The 4.00%-4.25% target range projected for year-end 2026 and 2027."
  @rate_decision : decision — "The Wednesday, September 16, 2026 decision to raise the target rate."
  @sept16 : moment — "Wednesday, September 16, 2026, the day of the rate decision."
  @sept_meeting : moment — "The September 2026 FOMC meeting, at which Warsh again did not submit a projection."
  @statement_timelier : text — "The quoted remark: 'Today's policy action will support a timelier return to the Committee's 2% goal.'"
  @supply_shocks : cause — "The 'supply shocks' label for a driver of elevated inflation."
  @t1430edt : moment — "2:30 p.m. EDT, the scheduled start of Warsh's press conference."
  @t1830gmt : moment — "18:30 GMT, the article's own restatement of the same press-conference start time."
  @trump : person — "Donald Trump, the U.S. president."
  @two_percent_target : goal — "The Fed's 2% inflation target."
  @unemployment_jun : figure — "The June 2026 projection of year-end unemployment (reported as 4.3%)."
  @unemployment_sep : figure — "The September 2026 projection of year-end unemployment (reported as 4.1%)."
  @warsh : person — "Kevin Warsh, the Fed chair."
  @y2026 : year — "Calendar year 2026 ('the end of this year')."
  @y2027 : year — "Calendar year 2027."
  @y2029 : year — "Calendar year 2029, the newly projected year for reaching the 2% inflation target."
Predicates:
  appointed_by(person, person) — "{0} appointed_by {1}" (strict fallback; declared: none) — "Recorded as the first person having been selected/appointed by the second."
  attributes_to(text, cause) — "{0} attributes_to {1}" (strict fallback; declared: none) — "Recorded as the statement attributing (elevated) inflation to this named cause."
  exceeds(figure, figure) — "{0} exceeds {1}" (strict fallback; declared: none) — "Recorded as the first reported figure being numerically greater than the second, as a ground fact asserted per named pair. This is NOT arithmetic: it carries no information about any figure not named in this vocabulary, and no magnitude; see GAPS.md."
  is_first_under(decision, person) — "{0} is_first_under {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as this decision being the first policy shift during this person's tenure. Hides the ordinal comparison against an unenumerated sequence of other decisions; see GAPS.md."
  pledged(person, text) — "{0} pledged {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as the person having pledged this statement. The commissive force of 'pledged' and the quoted content are not modelled; see GAPS.md."
  projected_for(rate_range, year) — "{0} projected_for {1}" (strict fallback; declared: none) — "Recorded as this rate range being the one projected to hold at the end of this year."
  projected_year(goal, year) — "{0} projected_year {1}" (strict fallback; declared: none) — "Recorded as this goal (e.g. reaching the 2% inflation target) being projected to occur in this year."
  promised(person, goal) — "{0} promised {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as the person having promised this goal. The commissive force of 'promised' and the propositional content of the goal are not modelled; see GAPS.md."
  raised_on(institution, moment) — "{0} raised_on {1}" (strict fallback; declared: none) — "Recorded as the institution having raised its policy rate on this date."
  raised_to(institution, rate_range) — "{0} raised_to {1}" (strict fallback; declared: none) — "Recorded as the institution having raised its policy rate to this named target range."
  scheduled_for(event, moment) — "{0} scheduled_for {1}" (strict fallback; declared: none) — "Recorded as the event being scheduled for this named clock time."
  stated(institution, text) — "{0} stated {1}" (strict fallback; declared: none) — "OPAQUE marker predicate. Recorded as the institution having issued this statement. The quoted content of the statement is opaque; see GAPS.md."
  submitted_projection(person, moment) — "{0} submitted_projection {1}" (strict fallback; declared: none) — "Recorded as the person having submitted an individual rate projection ('dot') for this meeting."
  took_office_in(person, moment) — "{0} took_office_in {1}" (strict fallback; declared: none) — "Recorded as the person having taken office during this (imprecisely named) period."
  unanimous(decision) — "{0} is unanimous" (strict fallback; declared: none) — "Recorded as approved without a dissenting vote, per the reported vote."
  voted_for(person, decision) — "{0} voted_for {1}" (strict fallback; declared: none) — "Recorded as the person having voted for (joined) this decision."
Fluent variable letters: cause = C, decision = D, event = E, figure = F, goal = G, institution = N, moment = M, person = P, rate_range = R, text = T, year = B
Fluent variable rule: Distinct sort letters exclude A/I/O and declared identifiers (case-insensitive). Choose the noun initial, then its unused consonants, then BCDEFGHJKLMNPQRSTUVWXYZ; on exhaustion use alphabetic codes BB, BC, ... . Within the naming scope, each sort's named binders use suffixes 1, 2, ... in preorder; omit 1. Constants have @; lexical words are lowercase.
Naming: per_statement — Allocate binders in preorder. Restart names in each statement.
Lint: none
@fed raised_on @sept16.
both @rate_decision is unanimous and @warsh voted_for @rate_decision.
@trump promised @lower_prices_goal.
@fed raised_to @r375_400.
it is false that @warsh submitted_projection @sept_meeting.
@rate_decision is_first_under @warsh.
both @warsh appointed_by @trump and @warsh took_office_in @late_may_2026.
both @r400_425 projected_for @y2026 and @r400_425 projected_for @y2027.
@fed stated @statement_timelier.
both @prev_statement attributes_to @supply_shocks and (it is false that @new_statement attributes_to @supply_shocks).
both @press_conference scheduled_for @t1430edt and (both @press_conference scheduled_for @t1830gmt and @t1430edt is the same moment as @t1830gmt).
@pce_sep exceeds @pce_jun.
@two_percent_target projected_year @y2029.
both @growth_sep exceeds @growth_jun and @unemployment_jun exceeds @unemployment_sep.
@warsh pledged @pledge_lower_inflation.
```

## Notes

No `verbalisation` metadata was declared, so every predicate uses the
strict-fallback fluent rendering; `Lint: none` again means there was nothing
to fall back *from*, matching the same deliberate choice made for the
companion `claude-constitution-excerpt` document.

The eleventh rendered line (statement 11, the press-conference scheduling
claim) is the one place the fluent view surfaces a genuine, checked equality
between two differently-named constants that denote the same model entity:
"@t1430edt is the same moment as @t1830gmt" — `model-true.json` maps both
`t1430edt` and `t1830gmt` to the single local id `press_time`, so this is not
merely two independent facts but one checked cross-timezone identity, exactly
mirroring the article's own "2:30 p.m. EDT (18:30 GMT)" parenthetical. This
document uses no `closure@0` profile (no `tc[]`/`rtc[]` atom appears
anywhere in `claims.ve`), so, unlike the constitution excerpt's legend, there
is no `Closure:` block here.
