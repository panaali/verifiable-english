# ap-parse-index report: an act phrase is read within the CPU deadline at 128 frames

- **Status:** built; no DRI signature reserved. Scope as the DRI ruled after the measurement:
  reviews/dri-decisions-20261109-ap-parse-index.md (no first-terminal index; fixes 1-2; Run.lean and ap-4's test (c)),
  -2.md (`combineFast` instead of a charge), -3.md (the per-document budget is the follow-up `ap-parse-indexb`).
- **HEAD:** this branch's final commit; base `a0102f0e5` (`git merge-base HEAD main`). Bytes: 0 (availability only).
  Next item: none in this chain; FOLLOW-UP `ap-parse-indexb` (a per-document act-parse budget, spec 12 addendum).

## 1. Measurement first (deliverable 1)

VM, compiled bench (`lean/ParseIndexBench.lean`, at `b9c4ece84`; removed after, for size), main `a0102f0e5`, the
deadline lifted. Raw rows before and after: [measure-20261109.txt](measure-20261109.txt). µs unless marked; L6 is
P64 (`V5`, 64 readings) with frames added; "readings" is `VE.Acts.readings` whole (grammar, table, meaning).

| Case | frames | rules | steps | grammar | prepare | table | readings |
|---|---|---|---|---|---|---|---|
| L6 | 2 | 234 | 23,152 | 5,919 | 204 | 7,650 | 183,404 |
| L6 | 32 | 2,004 | 82,672 | 848,559 | 1,881 | 14,292 | 19.96 s |
| L6 | 64 | 3,892 | 146,160 | 2,076,671 | 4,900 | 13,698 | 75.58 s |
| L6 | 126 | 7,550 | 269,168 | 9,455,583 | 7,460 | 26,646 | 304.68 s |
| L6 (V5 + 126) | 128 | 7,668 | 273,136 | 7,976,846 | 5,676 | 23,079 | 479.26 s |
| 400-byte | 1 | 154 | 357,659 | 2,581 | 166 | 236,468 | 240,612 |
| 400-byte | 31 | 1,924 | over budget | 1,026,258 | 2,430 | 2.37 s | 3.18 s (LIMIT) |
| 400-byte | 127 | 7,588 | over budget | 17.67 s | 14,075 | 2.44 s | 21.46 s (LIMIT) |

Split of `readings` (L6, 64 frames): `closed` 1.89 s, `build` 2.53 s, parse 57 ms, the 64 meanings with one shared
rule table 2.7 ms, as compiled 131.6 s. **What grows with frames²:** not the table. A row is already charged every
rule and position (`rowAt`: `s1 + P.positions + c2`); its time follows its steps (0.1 to 1.1 µs per step at every
frame count), and the steps grow by 1,984 per frame. The square was (a) the grammar's build, `closed` and `build`
(`firsts`, `rs.any`, `idxOf` per symbol), and (b) `meaning V`, compiled as a three-argument function, so `closed
(schema V)` ran again for every derivation. `prepare` was 6 to 14 ms at 128 frames.

## 2. The fixes (deliverables 2 and 3, as ruled)

1. **The grammar in near-linear time.** `VE.Acts.Index`: `firstsGo`, `idxGo` (hash set and map), proved equal to
   `firsts` and `List.idxOf` (`firstsGo_eq`, `idxGo_getD`); `closedFast`, `buildFast` proved equal to `closed`, `build`;
   `@[csimp]` makes compiled code run them (the `VE/Norms/Once.lean` pattern). Definitions and statements unchanged.
2. **The rule table read once.** `meaningWith rs V` (`meaning V` is it at `closed (schema V)`); `reader V` (the table
   and the prepared grammar) and `readingsBy`, with `readings`/`read` compiled through them (`@[csimp]`, `rfl`).
   `Norms.Wire.actsOf` builds one reader for all a document's acts (`checkActBy`, `joinedActBy`; `checkAct` and
   `joinedAct` are them at `reader V`), found by the self-review: one grammar per act took 4.85 s for 16 acts at 128
   frames. `witnessed` and `rowsOf` (`Run.lean`) share one table. `sourceCheck` reads `readings`; no route calls it yet.
3. **The uncharged per-step loop.** `combine` read every tree of the first symbol's entry even at an end position
   whose suffix is empty. `combineFast` (`@[csimp]`, proved equal) skips such a position in one look-up.
4. **Not built:** the first-terminal index (item 1: the scan it saves is charged already), and a charge on the walked
   trees: built first, it put the 400-byte phrase with `V5`'s 2 frames at 2,191,550 steps (`LIMIT`, against ap-4's
   condition (a)) and moved `EngineExamples` g16 from 49 to 77; replaced by point 3 (-2.md, SIGNED).

## 3. The CPU per step

No charge changed: `stepBudget` (2,100,000), every step pin and boundary are as on main (`EngineExamples` g16 at 49
and G17 at 599; the full `lake build` passes). `lean/VE/Grammar/Table.lean`'s header names what a row does beyond its
steps: per row `accepted` (at most the longest exclusion list `E` per distinct terminal; a row is charged at least
one step per terminal), the row's arrays and groups (at most its rules and positions, charged); per attempt one
look-up per end position (at most `n + 1`); per combination one insertion (a merge over at most `n + 1` end positions,
an append to at most `cap`). So a step costs at most `c · (cap + n + E)` elementary operations, with `cap` = 256,
`n` ≤ 200 tokens (400 bytes) and `E` = 5 + the adverbs + a frame's markers + at most 128 heads. Measured after: at most
0.69 µs per step (the 400-byte phrase with 128 frames: 1,445,223 µs at the 2.1 M budget), so the budget is about
1.5 s of table time on the VM. **Not bounded here (DRI -3.md):** a norms document's total. Each of its up to 64 acts
may use `stepBudget`; 64 acts each driven to the budget would need an **estimated** 64 to 90 s (64 × 1 to 1.5 s, not
measured) and fail closed with `CheckerUnavailable`. FOLLOW-UP `ap-parse-indexb`.

## 4. Fixtures and the decision's conditions (deliverable 4)

After (VM, the file's AFTER rows): L6 with 2/32/64/128 frames, `readings` 12/40/80/208 ms; 400-byte with 128 frames,
`LIMIT` in 1.9 s. Service probes (wall, with Python): `act-readings` L6 + 126 frames 0.42 s; `norms` with 128 frames
and 1/16/64 joined acts 1.47/1.37/2.15 s. Tests (`uv run pytest tests/test_ap_parse_index.py` and the ids below,
passed; section 7):

| Condition | Fixture | Result |
|---|---|---|
| L6 with 126 frames more, never `CheckerUnavailable` | `test_acts_readings_lean.py::test_p64_with_126_frames_more_is_listed_within_the_cpu_deadline`; `test_ap_parse_index.py::test_l6_reads_the_same_64_readings_with_up_to_128_frames[126]` | `LISTED`, V5's 64 readings |
| growing input 2, 32, 64, 126, 128 frames | `test_l6_reads_the_same_64_readings_with_up_to_128_frames[0-126]`; `ParseIndexExamples` `l6Steps` (23,152 + 1,984 n) | `LISTED` 64 |
| a norms document, 128 frames, a joined act | `test_a_norms_document_with_128_frames_reads_its_joined_act`; 63 joined acts: `test_a_norms_document_reads_63_joined_acts_with_one_grammar` | parts `p027__1`, `p027__2` |
| long400 with 128 frames, deterministic `LIMIT` (-2.md) | `test_the_400_byte_phrase_is_listed_with_two_frames_and_a_step_limit_with_32_or_128[127]` | `LIMIT` |
| (a) 32 frames; 64 readings with V5; 400 bytes with at most 2 frames | `test_acts_readings_lean.py::test_the_document_caps_on_fixed_phrases_and_frames_are_limits`, `::test_64_readings_are_listed_and_more_are_a_limit`, `::test_the_act_phrase_limit_is_400_bytes`; `RunExamples`' `p400` guard | unchanged |
| (b) 129 frames, `ResourceLimit` before any parse | `test_the_document_caps_on_fixed_phrases_and_frames_are_limits`; `test_a_norms_document_with_129_frames_is_a_resource_limit` | unchanged |
| g16 at 49, p400 with V5 `LISTED` (-2.md) | `EngineExamples` g16 guards; `RunExamples` `p400` guard | unchanged |
| a step stays bounded | the deadline tests above (a step count cannot see time); `once_installed%` (every `@[csimp]` installed) | — |
| the deadline's kill and recovery | `tests/test_lean_service.py::test_a_request_past_its_cpu_deadline_names_its_mode_and_is_not_retried`, `::test_each_phase_of_a_request_is_bounded_by_its_cpu_deadline` | unchanged |

R4: no document check is slower (L6 with V5, `readings` 183 → 12 ms). `EngineExamples`: `/usr/bin/time lake env lean
VE/EnglishGrammar/EngineExamples.lean`, 5.66/5.65/6.09 s user on main's `Table.lean`, 5.71/5.36/5.41 s here.
`GrammarExamples` 5.17/5.11 s before the new 128-frame guards and 10.60/10.77 s with them (now in `ParseIndexExamples`; fixture time).

## 5. Trust (R16)

`uv run python tools/trust_map.py --check`: exit 0. Against `a0102f0e5`: **K +0, S +3, D +17, G +55, tied +44,
trusted +27** (`VE/Acts/Wire.lean` +10, `Acts/Index.lean` +6, `Acts/Readings.lean` +5, `Acts/Meaning.lean` +3 S,
`Norms/Wire.lean` +2, `Acts/Run.lean` +1). Allowance recorded (`docs/trust-baseline.json`) "SIGNED by standing ruling
R16"; FOLLOW-UPS.md "## ap-parse-index". Tied by equality theorems: `firstsGo`, `closedFast`, `buildFast`,
`combineFast`, `readingsBy`, `readingsOnce`, `readOnce`. `python3 lean/audit.py`: PASS, 797 files, 8,819 theorems.

## 6. Seeded bugs

[mutants.json](mutants.json) (`python3 docs/act-phrases/ap-parse-index/seed_bugs.py`): 21 plants, **21 KILLED**, one
per new definition and claimed behaviour (Lean only: no Python or Rust product code changed). Equality proofs kill
`firstsGo`, `idxGo`, `closedFast`, `buildFast`, `combineFast`, `reader`, `readingsBy`, `readingsOnce`, `readOnce`,
`witnessed`, `checkActBy`; `#guard`s kill `meaningWith`, `tagged`, `taggedWith`, `rowsOf`, `joinedActBy`, `actsOf`,
a row charged a constant (`l6Steps`), a dropped `@[csimp]` (`once_installed%`). Service plant, by hand: both `@[csimp]` of `closed`/`build` dropped, `ve_service` built and pinned with
it: 5 deadline tests fail with `CheckerUnavailable` (named in the JSON). The task's two index seeds are N.A. (no index,
item 1). "prepare rebuilt per step" cannot be planted as written (`Prepared.table` takes `P` once); rebuilt per row
it adds about 10 ms per row at 128 frames, under the deadline.

Trust mutants (`mac-pytest.sh --trustmut -- --max-mutants 1000 --rescore … --allow … --json …`, ve-cloud-3):
[trust-mutants.json](trust-mutants.json), 4 definitions, 27 mutants: **8 KILLED, 0 SURVIVOR, 0 UNKNOWN, 15 INVALID,
4 ALLOWED, exit 0**; reasons in [trust-mutants-allow.json](trust-mutants-allow.json) (two ill-typed list cuts; `idxGo`'s
two literal mutants, refuted by the direct `#guard` on `idxGo` but read by the tool through `build_eq_fast`).

## 7. Tests

Filled by the final selected run.

## Spec re-read

- `parse`'s type and every `TableProofs` statement against `lean/VE/Grammar/TableProofs.lean` (unchanged; `git diff
  a0102f0e5 -- lean/statements.txt` adds lines only).
- D-31's 128 frames against `lean/VE/Acts/Syntax.lean:67` (`checkVocab`), spec 12 limits against
  `lean/VE/Acts/Read.lean` (`rawCap`, `stepBudget`, `maxReadings` unchanged).

## Self-review against BUILDER-CHECKLIST

Filled with section 7.
