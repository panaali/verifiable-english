# ap-parse-index report: an act phrase is read within the CPU deadline at 128 frames

- **Status:** built; no DRI signature reserved. Scope as the DRI decided it after the measurement
  (reviews/dri-decisions-20261109-ap-parse-index.md items 1 and 2; one deviation in section 3, sent to the DRI).
- **HEAD:** this branch's final commit; base `a0102f0e5` (main, `git merge-base HEAD main`).
- **Changed:** `lean/VE/Acts/Index.lean` (new), `Acts/Grammar.lean`, `Acts/Meaning.lean`, `Acts/Readings.lean`,
  `Acts/Run.lean`, `Grammar/Table.lean`; fixtures `Acts/GrammarExamples.lean`, `tests/test_ap_parse_index.py`,
  `tests/test_acts_readings_lean.py` (ap-4's condition (c), DRI item 2); the bench `lean/ParseIndexBench.lean`
  (exe `ve_parse_index_bench`, built on demand).
- **Bytes:** 0 (no unit's status changes; an availability fix). **Next item:** none in this chain.

## 1. Measurement first (deliverable 1)

VM, compiled (`lean/ParseIndexBench.lean`), main `a0102f0e5`, the deadline lifted. Raw rows, before and after:
[measure-20261109.txt](measure-20261109.txt). Microseconds unless marked; L6 is P64 (`V5`, 64 readings) with `n`
frames more; "table" is `fill` within the budget; "readings" is the whole `VE.Acts.readings` (grammar, table, meaning).

| Case | frames | rules | steps | grammar | prepare | table | readings |
|---|---|---|---|---|---|---|---|
| L6 | 2 | 234 | 23,152 | 5,919 | 204 | 7,650 | 183,404 |
| L6 | 32 | 2,004 | 82,672 | 848,559 | 1,881 | 14,292 | 19.96 s |
| L6 | 64 | 3,892 | 146,160 | 2,076,671 | 4,900 | 13,698 | 75.58 s |
| L6 (+126) | 128 | 7,550 | 269,168 | 9,455,583 | 7,460 | 26,646 | 304.68 s |
| 400-byte | 1 | 154 | 357,659 | 2,581 | 166 | 236,468 | 240,612 |
| 400-byte | 31 | 1,924 | over budget | 1,026,258 | 2,430 | 2.37 s | 3.18 s (LIMIT) |
| 400-byte | 127 | 7,588 | over budget | 17.67 s | 14,075 | 2.44 s | 21.46 s (LIMIT) |

Within a row (L6, 128 frames): `accepted` 189, `ntRowGo` 13,611, `sufGroups` over `byTerm` 4, over `byNt` 11,132.
Split of `readings` (L6, 64 frames): `schema` 1.6 ms, `closed` 1.89 s, `build` 2.53 s, parse 57 ms, the meaning of the
64 derivations with the rule table shared 2.7 ms, and as compiled (`meaning V` per derivation) 131.6 s.

**What grows with frames²:** not the table. A row is already charged every rule and every rule position
(`rowAt`: `s1 + P.positions + c2`), so the table's time follows its steps, 0.1 to 1.1 µs per step at every frame
count, and the steps grow linearly (1,984 per frame). The square is (a) building the act grammar, `closed` and `build`
(`firsts`, `rs.any` per nonterminal, `names.idxOf` per symbol): 9.5 s at 128 frames; and (b) `meaning V`, which
the compiler runs as a three-argument function, so `closed (schema V)` was computed again for **every derivation**
(64 × 2 s at 64 frames; the builder's 322.8 s). `prepare` (`termsOf`, `termIndex`) is 7 to 14 ms at 128 frames.

## 2. The fixes (deliverables 2 and 3, as the DRI ruled)

1. **The grammar in near-linear time.** `VE.Acts.Index`: `firstsGo` (first occurrences with a hash set) and `idxGo`
   (first places in a hash map), proved equal to `firsts` and `List.idxOf` (`firstsGo_eq`, `idxGo_getD`).
   `closedFast` and `buildFast` use them, proved equal to `closed` and `build`; `@[csimp]` makes compiled code run
   them, so `closed`, `build`, `grammar_wf` and every statement are unchanged (the `VE/Norms/Once.lean` pattern).
   `NT`, `FNT`, `Core` derive `Hashable`.
2. **The rule table read once per request.** `meaningWith rs V` is the meaning over a given table (`meaning V` is it
   at `closed (schema V)`, by definition); `readingsOnce`/`readOnce` (`@[csimp]`, `rfl`) compute the table once for
   the grammar and every derivation, which covers the norms decoder's `checkAct` and `sourceCheck` (both call
   `readings`); `witnessed` and `rowsOf` in `Run.lean` do the same (`tagged V` stays, as `taggedWith` its table).
3. **The one uncharged per-step loop.** `combine` read every tree of the first symbol's entry, also at an end
   position whose suffix entry is empty (charged one step for the attempt). `combineFast` (`@[csimp]`, proved equal)
   reads the suffix entry once per end position and skips an empty one without reading its trees.
4. **No first-terminal index** (DRI item 1): the scan it would save is already charged; an index charged by visited
   rules would lower step counts and move `LIMIT` boundaries the other way, which no ruling covers.

## 3. The charge, and the CPU per step

No charge changed, so `stepBudget` (2,100,000), every step pin and every boundary are as before; `measure_n.py`'s
rule is untouched. **Deviation from DRI item 1 (3):** charging the trees `combine` walks (built first) raised the
400-byte phrase with `V5`'s 2 frames to 2,191,550 steps, over `stepBudget`: a `LISTED` → `LIMIT` change on ap-4's
condition (a) fixture, and `measure_n.py`'s rule would keep 2,100,000. The skip of point 3 bounds the same loop
without a new charge (DRI informed, inbox 20261109T193620Z).

**The constant.** Per charged step, a row does at most: one look-up per end position of the first symbol's entry
(at most the sentence length `n` + 1), and per combination one insertion (a merge over at most `n` + 1 end positions,
an append to at most `cap` items, a sort of the attempt's candidates). So a step costs at most `c · (cap + n)`
elementary operations, with `cap` = `rawCap` = 256 and `n` ≤ 200 tokens (400 bytes); `accepted` costs at most the
vocabulary's exclusion list per distinct terminal, and the row is charged one step per terminal. Measured after: 0.61
µs per step (400-byte phrase, 128 frames, 38.7 M steps without the budget, 23.7 s), so the budget is at most 1.3 s of
table time on the VM (1.45 s measured at the budget).

## 4. Fixtures and the decision's conditions (deliverable 4)

After, VM (section 1's file): L6 with 0/30/62/126 frames more, `readings` 12/40/80/208 ms; the grammar 0.8/18/53/155
ms; the 400-byte phrase with 128 frames, `LIMIT` in 1.9 s.

| Condition | Fixture | Result |
|---|---|---|
| L6 with 126 frames more, within 5 s CPU, never `CheckerUnavailable` | `test_acts_readings_lean.py::test_p64_with_126_frames_more_is_listed_within_the_cpu_deadline`, `test_ap_parse_index.py::test_l6_reads_the_same_64_readings_with_up_to_128_frames[126]` | `LISTED`, the same 64 readings as `V5` alone |
| a norms document, 128 frames, a joined act | `test_ap_parse_index.py::test_a_norms_document_with_128_frames_reads_its_joined_act` | `p027__1`, `p027__2` |
| growing input 2, 32, 64, 126, 128 frames | `test_l6_reads_the_same_64_readings_with_up_to_128_frames[0-126]`; steps `#guard` (`GrammarExamples`, `l6Steps`: 23,152 + 1,984 n) | all `LISTED` 64 |
| (a) 32 frames, the one-act phrase | `test_acts_readings_lean.py::test_the_document_caps_on_fixed_phrases_and_frames_are_limits` | `LISTED`, unchanged |
| (a) 64 readings with V5 | `test_acts_readings_lean.py::test_64_readings_are_listed_and_more_are_a_limit`; `test_ap_parse_index.py` | `LISTED`, unchanged |
| (a) the 400-byte phrase, at most 2 frames | `test_acts_readings_lean.py::test_the_act_phrase_limit_is_400_bytes`; `test_the_400_byte_phrase_is_listed_with_two_frames_and_a_step_limit_with_32`; `RunExamples` line 129 | `LISTED`, unchanged; 32 frames a `LIMIT` |
| (b) 129 frames, `ResourceLimit` before any parse | `test_the_document_caps_on_fixed_phrases_and_frames_are_limits`; `test_a_norms_document_with_129_frames_is_a_resource_limit` | unchanged |
| a step stays bounded | `l6Steps` `#guard` and `once_installed%` (every `@[csimp]` installed), `GrammarExamples`; the deadline tests above | — |
| the deadline's kill and recovery (DRI item 2) | `tests/test_lean_service.py::test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried`, `::test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline` | unchanged, selected |

R4 (Lean CPU): no document check is slower; `act-readings` and the joined act's `norms` check are faster (L6 with
`V5`: `readings` 183 → 12 ms). `EngineExamples` elaborates in 5.8 s on main's `Table.lean` and 5.5 s on this one;
`GrammarExamples` 5.1 s with main's fixtures, 10.7 s with the new 128-frame guards (fixture time, not a check).

## 5. Trust (R16)

Filled after the heavy checks.

## 6. Seeded bugs

Filled after the heavy checks.

## 7. Tests

Filled after the heavy checks.
