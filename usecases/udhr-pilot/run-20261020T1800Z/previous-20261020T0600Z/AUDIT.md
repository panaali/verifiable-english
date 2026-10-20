All 20 sampled units are faithful, and no unit changed in this run. I saved the audit (342 words) to `run-20261020T0600Z/AUDIT.md`. The file it replaced was a byte-identical copy of the previous audit, which is still kept in `previous-20261019T1800Z/AUDIT.md`. That directory isn't under git, so there was nothing to commit. I made no model calls.

## UDHR fidelity audit, run 20261020T0600Z

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` are empty, and the four part documents are byte-identical to the last run's.

- **Sample:** `sorted(random.Random("20261020T0600Z").sample(pool, 20))` over the 92 CHECKED, LABELLED, OPEN and READINGS units. The source hash and all spans match.
- **What I read:** each unit's content, readings, descriptions, open-term records (AT4) and rendering. All 25 Lean status rows are as expected.

VERDICTS:
u018 FAITHFUL
u025 FAITHFUL
u033b FAITHFUL
u035 FAITHFUL
u054 FAITHFUL
u060 FAITHFUL
u063 FAITHFUL
u070 FAITHFUL
u073 FAITHFUL
u077 FAITHFUL
u083 FAITHFUL
u084d FAITHFUL
u085 FAITHFUL
u090 FAITHFUL
u099a FAITHFUL
u099b FAITHFUL
u100a FAITHFUL
u107 FAITHFUL
u112 FAITHFUL
u114 FAITHFUL

**Unfaithful:** none. No reading names a bearer the words don't name or raises a question they don't raise. Judgment calls I accepted:
- **u025, u073, u114:** each keeps both readings.
- **u099a:** "technical and professional" means either kind.
- **u100a:** "Education" means every course of education.
- **u112:** "These rights" means the Declaration's rights, and the open term leaves which ones open.

**Targeted items:** I skipped JT-0p, ET-0 and QT-0p because neither `plan_repairs` nor the ledger shows a change. u060 came up in the random sample and is FAITHFUL; it stays `claimed: false`.

**Integrity check:** no hits, either in the 4 sampled CHECKED units or in all 19 of the run's.

**Bytes (X5):** u035 and u060 are `claimed: false`, so they claim no bytes. The other 18 were already verified, so verified bytes stay at 5,270 (48.28%).

**Nit:** u033b uses the open term `equal_protection_of_the_law`, but its own phrase ("equal protection against … incitement") does not say "of the law".

**Three highest-value missing features:**
1. **Act-phrase grammar through a route (ap-1b):** it would formalise the 8 UNFORMALISED act-phrase units. Every sampled entitlement is also a single opaque predicate that the checker can't look inside.
2. **Plain-English rendering:**
   - 13 of the 16 sampled content units render as `classified as "…"`.
   - u025's explanation of where its readings differ lists 20 unrelated sorts.
   - u073 and u114 only say their readings differ "in a checked situation that VE cannot yet show in words".
   - u112 reads "Every exercise must not be exercised".
3. **Checked cross-unit references:** "such discrimination" (u033b), subjects carried over from an earlier unit (u084d, u099b) and "These rights" (u112) are resolved only in description text. With presupposition (u060) and a victim argument (u035), this would let the `claimed: false` units count their bytes.
