I couldn't save AUDIT.md because Write is denied in this session, so the audit is below. I changed no files and made no model calls.

## UDHR fidelity audit, run 20261019T1800Z

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units`, `plan_repairs` and `ledger_only_changes` are empty, and the four part documents are byte-identical to the 06:00Z run's.

- **Sample:** `sorted(random.Random("20261019T1800Z").sample(pool, 20))` over the 92 CHECKED, LABELLED, OPEN and READINGS units. It reproduces the last two runs' samples. The source hash and all 20 spans match.
- **What I read for each unit:** its content, descriptions, open-term records (AT4), rendering and Lean status rows. All 34 rows are as expected.

VERDICTS:
u014 FAITHFUL
u020 FAITHFUL
u023 FAITHFUL
u028 FAITHFUL
u029 FAITHFUL
u030 FAITHFUL
u033b FAITHFUL
u034 FAITHFUL
u036 FAITHFUL
u045a FAITHFUL
u055 FAITHFUL
u059 FAITHFUL
u066 FAITHFUL
u084a FAITHFUL
u095 FAITHFUL
u097 FAITHFUL
u099a FAITHFUL
u100b FAITHFUL
u104 FAITHFUL
u107 FAITHFUL

**Unfaithful:** none. No reading names a bearer the words don't name or raises a question they don't raise. Judgment calls I accepted:
- **u055:** whether "arbitrarily" reaches "nor denied" is a real scope question, and both readings are kept.
- **u059:** "only with" is read as a necessary condition only. Nothing permits marriages that have consent.
- **u097:** "at least" leaves higher education UNDECIDED.
- **u100b:** "Education" is read as every course of education, as in u100a.

**Targeted items:** I skipped JT-0p, ET-0 and QT-0p because neither `plan_repairs` nor the ledger shows a change.

**Integrity check:** no hits, either in the 4 sampled CHECKED units or in all 19 of the run's. u042 shares `committed_on` with u043 (OPEN), but u043's open term is `heavier`.

**Bytes (X5):** all 20 are `claimed: true` and already verified. Verified bytes stay at 5,270 (48.28%).

**Ledger nits:** u045a's residual note says "private life", but its content keeps all four items. u020's residual lists factors its record lacks.

**Three highest-value missing features:**
1. **Act-phrase grammar through a route:** the largest UNFORMALISED group (8 units, 1,403 B). It also costs u066 its list comma.
2. **Equality and non-discrimination norms** (7 units, 1,064 B): u019 "without distinction of any kind" and u031 "equal before the law". u020 and u033a/b depend on these, and they aren't formalised yet.
3. **Plain-English rendering:**
   - 7 of 11 sampled content units render as `classified as "…"`.
   - u020 shows "that distinction is political", dropping the country.
   - u055's readings differ "in a checked situation that VE cannot yet show in words".
