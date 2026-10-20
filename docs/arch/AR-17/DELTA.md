# AR-17 delta: the readings S2 regeneration removed

`readings_route.elaborate` no longer rebuilds Lean's S2 row in Python to compare with it; it relays the row checked
for its schema and its binding to the request (R8). The A/B (`evidence/ab.json`, `pilot_parts.py compare`) compared
the merge base `beb5c463` with the code head `43570b7e` over every corpus of `tools/lean_first_diff.py` but the
whole pilots, plus the 55 UDHR and constitution readings part documents (L70): 99,902 records, 99,857 identical,
45 wording, 0 unlisted.

## User-visible deltas

| Row | Class | Change | Records | Ruling |
|---|---|---|---:|---|
| W1 | `wording` | The readings report's `checked_by.python` said Python compared S2 with Lean; it now says what Python does. Base: `... S2 choices, units, names, slot and sizes compared with Lean`; head: `... S2 choices, units, names, slot and sizes are Lean's, bound to the request (the sets, units, narrowings and choices they name)`. Every other member of the 45 reports is identical. The pair is listed in [`DELTA.json`](DELTA.json), and `compare --delta DELTA.json` exits 0 with 0 unlisted. R1 (a): the base text quotes no name or value, and every item it names (W2 structure, DRI ruling 3, S2 choices, units, names, slot, sizes) is in the head text. (b): there is no path. (c): the head is more specific (it names the bound relations). | 45 | SIGNED by standing ruling R1 (DRI-RULINGS.md) |

## Not user-visible on any recorded input

1. **Availability.** No record changes from `ReadingsConformance` to an answer, or the other way round: the A/B
   has no `availability` row. The deleted comparisons never fired on a genuine Lean answer in these corpora.
2. **Unavailable on both sides.** None (`unavailable_both` is empty), so R7 is not needed.
3. **A forged row.** A row that names a set, version, unit, narrowing, label or choice outside the request, or a
   count beyond it, is still `CheckerUnavailable`. Its text is now `the Lean readings route returned an invalid
   answer`, the text of the S1 and completion relays, instead of `ReadingsConformance: Python and Lean differ on
   ...`. Only a tampered service answer reaches it (`tests/test_readings_s2_answer.py`).
4. **Trust.** `tools/trust_map.py --check` on the final code: K +0, S +0, D +0, G +0, trusted +0. The one shape
   line changed (`lean/ResponseShape/Schemas/ReadingsRoute.lean`, the `elaborate` description) is a description,
   so no R6 allowance is recorded.
5. **Review fix F1, F2 (`d738cb08`).** The name map, the generated soft decisions' keys, a shared slot label, a
   `precedence under <rule>` cause and every refusal with ` under ` (also under the completion) are now bound to
   the request; a forged one is `CheckerUnavailable`. On every recorded input the head recording is byte-identical
   to the one before the fix, so no row of this file changes and none is added.
