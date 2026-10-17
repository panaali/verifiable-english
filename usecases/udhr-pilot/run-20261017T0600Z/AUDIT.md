## UDHR fidelity audit, run 20261016T1800Z (ve-green-trust-ties-rd9)

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` are both empty, so u097 was not added.

**Sample:** drawn with `sorted(random.Random("20261016T1800Z").sample(pool, 20))` from the 88 CHECKED/LABELLED/OPEN/READINGS units, sorted by id. The previous seed reproduces the previous sample. The draw gave 9 CHECKED, 5 OPEN, 4 LABELLED and 2 READINGS units. For each one I compared the source span with the part content, the predicate and sort descriptions, the open-term records (AT4), the reading sets, the rendering, the companion documents and the Lean status rows. The source hash matches, and the four parts are byte-identical to the previous run's.

VERDICTS:
u002 FAITHFUL
u022a FAITHFUL
u022c FAITHFUL
u034 FAITHFUL
u045b FAITHFUL
u048 FAITHFUL
u050 FAITHFUL
u059 FAITHFUL
u063 FAITHFUL
u066 FAITHFUL
u073 FAITHFUL
u074 FAITHFUL
u077 FAITHFUL
u084b FAITHFUL
u085 FAITHFUL
u087 FAITHFUL
u088 FAITHFUL
u100a FAITHFUL
u105c FAITHFUL
u106 FAITHFUL

**Unfaithful units:** none.

**Notes:**
- **No invented bearer:** no reading names a party the words don't name.
  - u074's actor is just whoever does the compelling in "be compelled", not someone given a duty.
  - u100a is an obligation on each course of education and names no one who must act.
- **u059:** consent is necessary, not sufficient ("only with"). When both spouses consent, the row is UNDECIDED, not permitted.
- **u045b:** an attack on honour alone, or on reputation alone, is prohibited, and "arbitrary" does not carry over to attacks. An attack outside these two kinds is UNDECIDED.
- **Reading sets:** u073 ("peaceful" scope) and u105c ("freely" scope, coupled with u105b) give exactly the readings the words support.
- **Open terms:** own_country, discrimination, equal_pay_for_equal_work, free_and_full_consent, full_development_of_the_human_personality and moral_and_material_interests use the source's own words; who decides them is "unstated".
- **Companions:** they differ from the parts only in the act's wording and `regulated: plain`. All Lean status rows are as expected.
- **Ledger gap (still open):** `readings/u114.no_implied_right.ve.md` is listed but does not exist.

**Bytes:** all 20 units were already audit-verified, so audit-verified bytes stay at 4,660 B (42.69%). u098 and u110 (160 B) are still unaudited. u035 and u111 are marked `claimed: false` and are not counted (X5).

**Three highest-value missing features:**
1. **Act phrases with internal structure, and checked links to the unit they continue.**
   - Phrases like "within the borders of each state", "without any discrimination" and "for the protection of his interests" are folded into single predicates.
   - u022c, u045b, u084b and u105c take their right or subject from an earlier unit, and nothing checks that link.
   - 8 units are blocked on this.
2. **References to the declared rights, and limits that apply to them.** All 16 non-heading sampled units are limited by u019, u108, u111, u112 and u114, and none of those links is checked. 98 units carry `other:scope`.
3. **Plain-English rendering:** 14 of the 16 non-heading sampled units render as `classified as "…"` or "recorded relation".

No model calls were made.

**AUDIT.md was not written:** the Write tool is denied in this session, so the audit is only printed here. The `AUDIT.md` now in the run directory is still the previous run's (20261016T0600Z), identical to `previous-20261016T0600Z/AUDIT.md`. No files were changed, so there was nothing to commit.
