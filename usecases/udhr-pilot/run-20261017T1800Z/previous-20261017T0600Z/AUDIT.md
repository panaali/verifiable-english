I couldn't write `AUDIT.md`: the Write tool is denied in this session, as it was in the last run. The `AUDIT.md` now in the run directory is still the 20261016T1800Z audit (a copy of the one in `run-20261016T1800Z/`). No files changed, so there was nothing to commit. The audit:

## UDHR fidelity audit, run 20261017T0600Z

**Faithful: 19/20 sampled + 2/2 changed** (u052, u114). `plan_repairs` is empty, so u097 was not added.

**Method:** `sorted(random.Random("20261017T0600Z").sample(pool, 20))` over the 88 CHECKED/LABELLED/OPEN/READINGS units. The source hash and every span match the source. For each unit I read the content, the predicate and sort descriptions, the open-term records (AT4), the reading sets, the companions, the Lean rows and the rendering.

VERDICTS:
u002 FAITHFUL
u011 FAITHFUL
u021 FAITHFUL
u022c FAITHFUL
u028 FAITHFUL
u037 UNFAITHFUL
u038 FAITHFUL
u048 FAITHFUL
u050 FAITHFUL
u072 FAITHFUL
u074 FAITHFUL
u075 FAITHFUL
u083 FAITHFUL
u085 FAITHFUL
u088 FAITHFUL
u090 FAITHFUL
u098 FAITHFUL
u099a FAITHFUL
u105c FAITHFUL
u113 FAITHFUL
u052 FAITHFUL
u114 FAITHFUL

**Unfaithful:**
- **u037 (Art. 9): a reading is missing.** In "arbitrary arrest, detention or exile", "arbitrary" can cover all three nouns or "arrest" alone.
  - The run splits this same structure into two readings for u073 ("peaceful assembly and association") and u055.
  - u037 keeps only the wide reading. Its Lean row c2 makes a non-arbitrary detention UNDECIDED; the narrow reading would prohibit it.
  - Only outside knowledge (that some detention is lawful) rules the narrow reading out.
  - Fix: a reading set like u055's. u027 (Art. 5, not sampled) has the same structure.

**Notes:**
- **u098:** first audit since its repair. It is an obligation with no one named to carry it out, with the open term `compulsory`, and it adds no recipient.
- **u052, u114:** the ledger repair is right: each lists only its norm companion, and that file exists. Both reading sets, a ban or a statement, are supported by the words. u114's wide scope for "aimed at" is forced, because the narrow parse would deny the Declaration's own rights.
- **u074:** its actor is just whoever does the compelling in "be compelled", not an invented bearer.

**Bytes:** taking out u037 (68 B) and adding u098 (42 B) gives 4,634 B audit-verified (42.45%). Claimed falls to 4,752 B (43.53%) until u037 is repaired. u110 (118 B) is still unaudited. No sampled unit is marked `claimed: false`.

**Three highest-value missing features:**
1. **The checker finds the scope of a modifier over a list itself.** "arbitrary", "peaceful", "freely" and "within the borders of each state" should each produce their scope readings automatically. Today the translator decides, and does it unevenly: u037 and u027 get one reading, u055, u073 and u105 get two.
2. **Checked references and scoped limitations.** "This right" (u052→u051), the ellipses (u022c←u022a, u105c←u105a) and "rights and freedoms set forth herein" are linked only by description text. 9 of the 10 substantive units audited are limited by u019, u108, u111, u112 and u114, and none of those links is checked.
3. **Plain-English rendering.** 9 of those 10 units render only as "The passage is recorded as a rule". Only u074 shows its reading in English.

No model calls were made.
