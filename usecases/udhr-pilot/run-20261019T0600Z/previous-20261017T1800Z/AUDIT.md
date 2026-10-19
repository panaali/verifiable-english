I couldn't write `AUDIT.md`: the Write tool is denied in this session. The file in the run directory is still the old 20261017T0600Z audit. I changed nothing; the only file I created is a scratch helper in `/tmp/udhr-audit-1800z/`.

## UDHR fidelity audit, run 20261017T1800Z

**Faithful: 20/20 sampled + 2/2 changed** (u027, u037). u037 was also drawn in the sample, so it is listed once below. `plan_repairs` is empty, so u097 was not added.

**Method:** `sorted(random.Random("20261017T1800Z").sample(pool, 20))` over the 88 CHECKED/LABELLED/OPEN/READINGS units. The source hash and all 21 spans match. For each unit I read the content, descriptions, open-term records (AT4), reading sets, companions, Lean rows and rendering. No audited unit is marked `claimed: false`.

VERDICTS:
u001 FAITHFUL
u011 FAITHFUL
u012 FAITHFUL
u020 FAITHFUL
u021 FAITHFUL
u032 FAITHFUL
u033a FAITHFUL
u033b FAITHFUL
u036 FAITHFUL
u037 FAITHFUL
u049 FAITHFUL
u054 FAITHFUL
u056 FAITHFUL
u075 FAITHFUL
u084c FAITHFUL
u090 FAITHFUL
u099a FAITHFUL
u105a FAITHFUL
u107 FAITHFUL
u110 FAITHFUL
u027 FAITHFUL

**Unfaithful:** none.

**Notes:**
- **u037 and u027 (repaired):** each now has two readings. The modifier ("arbitrary"; "cruel, inhuman or degrading") covers the whole list or only the first noun.
  - Both readings come from the word order alone, and a flat list allows no third parse.
  - Both u027 readings cover punishment.
  - Lean tells the readings apart: a detention that is not arbitrary, or a punishment that is not cruel, inhuman or degrading, is SETTLED under the narrow reading and UNDECIDED under the wide one.
- **u110** (pending since its repair): "has duties" stays a statement of fact. "In which alone" means possible in that community and in no other, and the community's existence is asserted. "The community" supports both readings: one per person, or one for everyone. I checked both formulas by hand.

**Bytes:** u110, u027 and u037 (283 B) pass. Audit-verified bytes rise from 4,537 to 4,820 (44.16%), which now equals the claimed bytes.

**Three highest-value missing features:**
1. **The checker works out a modifier's scope over a list itself.** u027 and u037 were again fixed by hand after an audit. The scope in u055, u073, u105 and u099a ("technical and professional") is still the translator's call.
2. **Checked references and scoped limitations.**
   - u032 and u084c take their subject or "the right" from the unit before.
   - u033b's "such discrimination" exists only in description text.
   - All 12 substantive units audited are limited by u019, u108, u111, u112 or u114, and none of those links is checked.
3. **Plain-English rendering.**
   - All 7 entitlement units audited render as `classified as "…"`.
   - u110 shows raw relation names.
   - u020 renders as "that distinction is political", where the meaning is "based on the political status".

No model calls were made.
