I couldn't save AUDIT.md because the Write tool is denied in this session, so the audit is printed below (378 words). I changed no files and made no model calls.

## UDHR fidelity audit, run 20261019T0600Z

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` are both empty.

- **Sample:** `sorted(random.Random("20261019T0600Z").sample(pool, 20))` over the 92 CHECKED, LABELLED, OPEN and READINGS units, in units.json order. The same call with the last run's seed gives the last run's sample, so the method matches.
- **Source:** the hash matches, and every unit's span gives its source bytes, both in units.json and in its part document.
- **What I read for each unit:** its content, the vocabulary descriptions, its open-term records (AT4), its rendering and its Lean status rows. All 22 status rows are as expected: a case outside the guard is UNDECIDED, never permitted.

VERDICTS:
u002 FAITHFUL
u022c FAITHFUL
u024 FAITHFUL
u029 FAITHFUL
u030 FAITHFUL
u034 FAITHFUL
u036 FAITHFUL
u042 FAITHFUL
u045b FAITHFUL
u047 FAITHFUL
u049 FAITHFUL
u064 FAITHFUL
u075 FAITHFUL
u080 FAITHFUL
u084a FAITHFUL
u084b FAITHFUL
u096 FAITHFUL
u100b FAITHFUL
u105b FAITHFUL
u112 FAITHFUL

**Unfaithful:** none. No unit names a bearer the words don't name, and none raises a question the text doesn't raise. Judgment calls I accepted:
- **u045b:** "arbitrary" stays on "interference", because "nor to" starts a new object. "Honour and reputation" applies to each separately: an attack on either is barred.
- **u105b:** the scope of "freely" is a real ambiguity. Both readings are kept, coupled with u105c.
- **u112:** "These rights and freedoms" is read as the Declaration's set, left open through the open term rights_and_freedoms_set_forth.
- **u042:** I again accept the event reification: the finding of guilt, the act and the day are treated as things, and "committed on" is a recorded relation.

**Targeted items:** I skipped JT-0p (u010, u060) and ET-0 (u043). `plan_repairs` is empty and their content hasn't changed. The only ledger change is the claim the last audit allowed.

**Integrity check:** no hits. None of the 8 sampled CHECKED units uses an open-term predicate or a catalogue word, and neither do any of the run's 19. u064's "arbitrarily" is a declared open term in an OPEN unit.

**Bytes (X5):** all 20 sampled units are `claimed: true` and were already audit-verified. Verified bytes stay at 5,270 (48.28%).

**Three highest-value missing features:**
1. **Act-phrase grammar through a route.** It is the largest UNFORMALISED group: 8 units, 1,403 B (for example Article 11(1) and Article 28). The ap-2 work is in Lean, but no route reads it yet.
2. **Checked references.**
   - u022c, u045b, u084b and u105b carry "Everyone has the right to" or "No one shall be subjected to" from an earlier unit only by description.
   - u112's "These" is handled as an open term.
   - u111 (337 B) stays `claimed: false`.
3. **Plain-English rendering.**
   - 11 of the 13 sampled content units render as `classified as "has_the_right_to_work"`.
   - u100b shows "respect of human rights plus fundamental freedoms".
   - u112 shows "Every exercise must not be exercised".
   - u042 shows its relations as "recorded relation".
