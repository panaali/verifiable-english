## UDHR fidelity audit, run 20261016T0600Z (ve-green-premise-scale)

**Faithful: 20/20 sampled + 0/0 changed.** `changed_units` and `plan_repairs` are empty. u097 came up in the random sample and is judged there.

**Sample:** `random.Random("20261016T0600Z").sample(…, 20)` over the 88 CHECKED, LABELLED, OPEN and READINGS units, sorted by id. The same call with the previous seed reproduces the previous run's sample. It drew 3 CHECKED, 9 LABELLED, 4 OPEN and 4 READINGS units. For each I compared the source span with the content, the predicate and sort descriptions, the open-term records, the reading set, the rendering and the companion documents.

```text
VERDICTS:
u012 FAITHFUL
u022a FAITHFUL
u034 FAITHFUL
u035 FAITHFUL
u036 FAITHFUL
u044 FAITHFUL
u045b FAITHFUL
u051 FAITHFUL
u053 FAITHFUL
u055 FAITHFUL
u073 FAITHFUL
u083 FAITHFUL
u084c FAITHFUL
u084d FAITHFUL
u090 FAITHFUL
u095 FAITHFUL
u097 FAITHFUL
u105c FAITHFUL
u107 FAITHFUL
u114 FAITHFUL
```

**Unfaithful units:** none.

**Notes:**
- **u035:** the predicate's description ties "him" to the person who holds the right. The open terms are the source's own words, and who decides them is left unstated. The `claimed: false` mark could be lifted. While it stands, the unit's 168 bytes count as neither claimed nor verified (X5).
- **u055, u073, u105c, u114:** every reading is one the words support. The choices are what "arbitrarily", "peaceful" and "freely" apply to, and whether "may be interpreted" is a ban or a statement. u105b and u105c share one "freely" choice. No reading names a bearer the text doesn't name.
- **u097:** "at least" is kept. Elementary or fundamental education must be free; whether other stages must be free stays UNDECIDED.
- **LABELLED units:** article headings, plus "The General Assembly,", which introduces the speaker; u013a attributes the proclamation to it.
- **Ledger gaps:**
  - `readings/u114.no_implied_right.ve.md` is listed in the ledger but the file does not exist.
  - The 20261015T1800Z audit judged u110 FAITHFUL and the unit hasn't changed, but `metrics.json` still lists it as pending.

**Bytes:** this sample adds no verified bytes, so audit-verified stays 4,660 B (42.69%). Crediting u110 would make it 4,778 B (43.77%).

**Three highest-value missing features:**
1. **Act phrases with internal structure, and checked links to the unit they continue.** "Granted him" exists only in the wording (u035). u045b, u084c/d and u105b/c take their subject from an earlier unit with nothing checking that link. Eight units are blocked on this.
2. **References to the declared rights, and limits that apply to them.** "Rights and freedoms set forth herein" (u114) is only an open term, and 98 units carry the `other:scope` blocker.
3. **Plain-English rendering.**
   - 10 of the 11 non-label units render as `classified as "…"`.
   - u055 says its two readings "differ in a checked situation that VE cannot yet show in words".

No model calls were made.

**AUDIT.md was not written:** the Write tool is denied in this session, so the audit is only printed here. The `AUDIT.md` now in the run directory is still the previous run's (20261015T1800Z) audit carried over, so don't read it as this run's.
