I couldn't save AUDIT.md because the Write tool is denied in this session, so the audit is printed below. I changed no files and made no model calls.

## UDHR fidelity audit, run 20261018T0600Z

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` are both empty. u097 came up in the random sample and is judged there.

**Method:** `sorted(random.Random("20261018T0600Z").sample(pool, 20))` over the 88 CHECKED, LABELLED, OPEN and READINGS units. The source hash matches, and all 20 spans match the source apart from trailing whitespace. For each unit I read:
- its content in the part document;
- its predicate descriptions and open-term records (AT4);
- its rendering and its Lean witness rows, all of which came out as expected.

All 20 units are `claimed: true`. Neither `claimed: false` unit (u035, u111) was drawn.

VERDICTS:
u020 FAITHFUL
u022a FAITHFUL
u022c FAITHFUL
u032 FAITHFUL
u036 FAITHFUL
u040 FAITHFUL
u047 FAITHFUL
u054 FAITHFUL
u063 FAITHFUL
u065 FAITHFUL
u066 FAITHFUL
u069 FAITHFUL
u077 FAITHFUL
u081 FAITHFUL
u084a FAITHFUL
u090 FAITHFUL
u097 FAITHFUL
u100a FAITHFUL
u100b FAITHFUL
u107 FAITHFUL

**Unfaithful:** none.

**Notes:**
- **u097:** "at least" is kept. Elementary or fundamental education must be free, and whether higher education must be free stays UNDECIDED. Reading "elementary and fundamental" as two kinds of stage is the natural reading, but the translator chose it; the checker did not.
- **u020:** no bearer is invented. "Whether it be independent, trust, …" limits nothing, and the rule covers every country status, so the clause is kept. A distinction outside the three named statuses is UNDECIDED, not permitted.
- **No invented readings:** none of the 13 substantive units names a bearer the words don't name or raises a question the text doesn't.
- **Ledger only:** the u077 and u097 entries point to reading sets (`rs_u077`, `rs_u097`) that no part document contains. Both are single-reading units, so their meaning is unaffected.

**Bytes:** all 20 units were already audit-verified. Audit-verified bytes stay at 4,820 (44.16%), equal to the claimed bytes.

**Three highest-value missing features:**
1. **The checker works out modifier and coordination scope itself.** The translator still picks the "either one" reading of u097's "elementary and fundamental" and u020's "political, jurisdictional or international". u027 and u037 needed hand repairs after audits.
2. **Checked references and scoped limitations.**
   - u022c, u032 and u100b take their subject or verb from the unit before, recorded only in a note.
   - u020's "Furthermore" ties it to u019 only by description.
   - All 13 substantive units list u019, u108, u111, u112 and u114 as the units that limit them, and none of those links is checked.
3. **Plain-English rendering.**
   - All 9 entitlement units render as `classified as "has_the_right_to_…"`, and the names shown drop words: u063 loses "alone as well as in association with others", u077 loses "access".
   - u020 renders as "that distinction is political", where the meaning is "based on the political status of the country".
   - u100b renders as "respect of human rights plus fundamental freedoms".
