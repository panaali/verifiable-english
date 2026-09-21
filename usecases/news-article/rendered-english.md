# English rendering

Generated from the unchanged environment and strict claims. Quoted predicate names indicate missing or rejected lexical metadata.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/news-article/environment.json --view ve_english \
  usecases/news-article/claims.ve
```

## Statements

```text
Fed has the recorded relation "raised_on" to "sept16".
Both "rate_decision" is unanimous and warsh has the recorded relation "voted_for" to "rate_decision".
Trump has the recorded relation "promised" to "lower_prices_goal".
Fed has the recorded relation "raised_to" to "r375_400".
It is not the case that warsh has the recorded relation "submitted_projection" to "sept_meeting".
"rate_decision" has the recorded relation "is_first_under" to warsh.
Both warsh has the recorded relation "appointed_by" to trump and warsh has the recorded relation "took_office_in" to "late_may_2026".
Both "r400_425" has the recorded relation "projected_for" to "y2026" and "r400_425" has the recorded relation "projected_for" to "y2027".
Fed has the recorded relation "stated" to "statement_timelier".
All of the following hold:
  (a) "prev_statement" has the recorded relation "attributes_to" to "supply_shocks";
  (b) it is not the case that "new_statement" has the recorded relation "attributes_to" to "supply_shocks".
All of the following hold:
  (a) "press_conference" has the recorded relation "scheduled_for" to "t1430edt";
  (b) both "press_conference" has the recorded relation "scheduled_for" to "t1830gmt" and "t1430edt" is the same as "t1830gmt".
"pce_sep" exceeds "pce_jun".
"two_percent_target" has the recorded relation "projected_year" to "y2029".
Both "growth_sep" exceeds "growth_jun" and "unemployment_jun" exceeds "unemployment_sep".
Warsh has the recorded relation "pledged" to "pledge_lower_inflation".
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: b3f7afa3f97f000698d6fd0e9cd7024a7d7aed4773d2ed0241dabf9f26616371
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: cause = C, decision = D, event = E, figure = F, goal = G, institution = N, moment = M, person = P, rate_range = T, text = X, year = R
Sort cause: {"noun": "cause", "description": "A named cause-of-inflation label that a Fed statement may or may not attribute inflation to."}
Sort decision: {"noun": "decision", "description": "The Wednesday, September 16, 2026 rate decision, reified as an event-like entity."}
Sort event: {"noun": "event", "description": "A scheduled event other than the rate decision itself."}
Sort figure: {"noun": "figure", "description": "A specific reported economic statistic (e.g. one quarter's PCE inflation estimate), treated as an opaque tag, not a number."}
Sort goal: {"noun": "goal", "description": "A named policy goal or promise the article attributes to someone."}
Sort institution: {"noun": "institution", "description": "A named institution in the article (the Federal Reserve / FOMC / 'the central bank', merged into one entity)."}
Sort moment: {"noun": "moment", "description": "A date, meeting, or clock time referred to in the article, treated as an opaque tag, not a computable timestamp."}
Sort person: {"noun": "person", "description": "A named person in the article."}
Sort rate_range: {"noun": "entity of sort \"rate_range\"", "description": "A named federal funds target rate range, treated as an opaque tag, not a pair of numbers."}
Sort text: {"noun": "text", "description": "A statement, quoted remark, or pledge, reified as an opaque entity standing for its (unmodelled) propositional content."}
Sort year: {"noun": "year", "description": "A calendar year referred to as a target or projection horizon."}
Predicate appointed_by: {"arguments": ["person", "person"], "template": "{0} has the recorded relation \"appointed_by\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the first person having been selected/appointed by the second."}
Predicate attributes_to: {"arguments": ["text", "cause"], "template": "{0} has the recorded relation \"attributes_to\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the statement attributing (elevated) inflation to this named cause."}
Predicate exceeds: {"arguments": ["figure", "figure"], "template": "{0} exceeds {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the first reported figure being numerically greater than the second, as a ground fact asserted per named pair. This is NOT arithmetic: it carries no information about any figure not named in this vocabulary, and no magnitude; see GAPS.md."}
Predicate is_first_under: {"arguments": ["decision", "person"], "template": "{0} has the recorded relation \"is_first_under\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as this decision being the first policy shift during this person's tenure. Hides the ordinal comparison against an unenumerated sequence of other decisions; see GAPS.md."}
Predicate pledged: {"arguments": ["person", "text"], "template": "{0} has the recorded relation \"pledged\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as the person having pledged this statement. The commissive force of 'pledged' and the quoted content are not modelled; see GAPS.md."}
Predicate projected_for: {"arguments": ["rate_range", "year"], "template": "{0} has the recorded relation \"projected_for\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as this rate range being the one projected to hold at the end of this year."}
Predicate projected_year: {"arguments": ["goal", "year"], "template": "{0} has the recorded relation \"projected_year\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as this goal (e.g. reaching the 2% inflation target) being projected to occur in this year."}
Predicate promised: {"arguments": ["person", "goal"], "template": "{0} has the recorded relation \"promised\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as the person having promised this goal. The commissive force of 'promised' and the propositional content of the goal are not modelled; see GAPS.md."}
Predicate raised_on: {"arguments": ["institution", "moment"], "template": "{0} has the recorded relation \"raised_on\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the institution having raised its policy rate on this date."}
Predicate raised_to: {"arguments": ["institution", "rate_range"], "template": "{0} has the recorded relation \"raised_to\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the institution having raised its policy rate to this named target range."}
Predicate scheduled_for: {"arguments": ["event", "moment"], "template": "{0} has the recorded relation \"scheduled_for\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the event being scheduled for this named clock time."}
Predicate stated: {"arguments": ["institution", "text"], "template": "{0} has the recorded relation \"stated\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "OPAQUE marker predicate. Recorded as the institution having issued this statement. The quoted content of the statement is opaque; see GAPS.md."}
Predicate submitted_projection: {"arguments": ["person", "moment"], "template": "{0} has the recorded relation \"submitted_projection\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the person having submitted an individual rate projection ('dot') for this meeting."}
Predicate took_office_in: {"arguments": ["person", "moment"], "template": "{0} has the recorded relation \"took_office_in\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the person having taken office during this (imprecisely named) period."}
Predicate unanimous: {"arguments": ["decision"], "template": "{0} is unanimous", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as approved without a dissenting vote, per the reported vote."}
Predicate voted_for: {"arguments": ["person", "decision"], "template": "{0} has the recorded relation \"voted_for\" to {1}", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as the person having voted for (joined) this decision."}
Constant fed: {"name": "fed", "sort": "institution", "description": "The Federal Reserve / FOMC / 'the central bank', as referred to in the article."}
Constant growth_jun: {"name": "\"growth_jun\"", "sort": "figure", "description": "The June 2026 projection of economic growth (reported as 2.2%)."}
Constant growth_sep: {"name": "\"growth_sep\"", "sort": "figure", "description": "The September 2026 projection of economic growth (reported as 2.3%)."}
Constant late_may_2026: {"name": "\"late_may_2026\"", "sort": "moment", "description": "The imprecisely named period ('late May') when Warsh took office."}
Constant lower_prices_goal: {"name": "\"lower_prices_goal\"", "sort": "goal", "description": "Trump's promised goal of lowering prices."}
Constant new_statement: {"name": "\"new_statement\"", "sort": "text", "description": "The FOMC's September 16, 2026 policy statement, which dropped the 'supply shocks' reference."}
Constant pce_jun: {"name": "\"pce_jun\"", "sort": "figure", "description": "The June 2026 projection of PCE inflation (reported as 3.6%)."}
Constant pce_sep: {"name": "\"pce_sep\"", "sort": "figure", "description": "The September 2026 projection of PCE inflation (reported as 3.7%)."}
Constant pledge_lower_inflation: {"name": "\"pledge_lower_inflation\"", "sort": "text", "description": "Warsh's quoted pledge to lower inflation 'clearly and at sufficient speed'."}
Constant press_conference: {"name": "\"press_conference\"", "sort": "event", "description": "Warsh's press conference following the rate decision."}
Constant prev_statement: {"name": "\"prev_statement\"", "sort": "text", "description": "The FOMC's previous policy statement, which attributed elevated inflation partly to 'supply shocks'."}
Constant r375_400: {"name": "\"r375_400\"", "sort": "rate_range", "description": "The 3.75%-4.00% target range the Fed moved to on September 16, 2026."}
Constant r400_425: {"name": "\"r400_425\"", "sort": "rate_range", "description": "The 4.00%-4.25% target range projected for year-end 2026 and 2027."}
Constant rate_decision: {"name": "\"rate_decision\"", "sort": "decision", "description": "The Wednesday, September 16, 2026 decision to raise the target rate."}
Constant sept16: {"name": "\"sept16\"", "sort": "moment", "description": "Wednesday, September 16, 2026, the day of the rate decision."}
Constant sept_meeting: {"name": "\"sept_meeting\"", "sort": "moment", "description": "The September 2026 FOMC meeting, at which Warsh again did not submit a projection."}
Constant statement_timelier: {"name": "\"statement_timelier\"", "sort": "text", "description": "The quoted remark: 'Today's policy action will support a timelier return to the Committee's 2% goal.'"}
Constant supply_shocks: {"name": "\"supply_shocks\"", "sort": "cause", "description": "The 'supply shocks' label for a driver of elevated inflation."}
Constant t1430edt: {"name": "\"t1430edt\"", "sort": "moment", "description": "2:30 p.m. EDT, the scheduled start of Warsh's press conference."}
Constant t1830gmt: {"name": "\"t1830gmt\"", "sort": "moment", "description": "18:30 GMT, the article's own restatement of the same press-conference start time."}
Constant trump: {"name": "trump", "sort": "person", "description": "Donald Trump, the U.S. president."}
Constant two_percent_target: {"name": "\"two_percent_target\"", "sort": "goal", "description": "The Fed's 2% inflation target."}
Constant unemployment_jun: {"name": "\"unemployment_jun\"", "sort": "figure", "description": "The June 2026 projection of year-end unemployment (reported as 4.3%)."}
Constant unemployment_sep: {"name": "\"unemployment_sep\"", "sort": "figure", "description": "The September 2026 projection of year-end unemployment (reported as 4.1%)."}
Constant warsh: {"name": "warsh", "sort": "person", "description": "Kevin Warsh, the Fed chair."}
Constant y2026: {"name": "\"y2026\"", "sort": "year", "description": "Calendar year 2026 ('the end of this year')."}
Constant y2027: {"name": "\"y2027\"", "sort": "year", "description": "Calendar year 2027."}
Constant y2029: {"name": "\"y2029\"", "sort": "year", "description": "Calendar year 2029, the newly projected year for reaching the 2% inflation target."}
```
