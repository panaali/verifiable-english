# ps-2a: the readings block and PS-E1's candidate table (spec 4.7, Wire.lean) (build report)

No DRI signature is reserved in this item. There are no DELTA rows (DELTA.md): the item adds only Lean that no route
reads. Trusted growth is +117 (K +0, S +74, V +43), covered by standing ruling R16 (see "Trust").
Status: built to the cut the DRI signed: deliverables (1) and (2) (reviews/dri-decisions-20261109-ps-2a.md item 1).
`admit`, A1-A28, the 19 `admit_*` statements and Run.lean go to ps-2ab (see "Cut").
Checks: probe 38/39 equal (`candidateTable` is filled by design), audit PASS, trust_map --check PASS, trust_mutants
exit 0, selected tests: see "Final checks". Size: 767 hand-written lines, over the ~600 line (see "Size").
Open: the chain runs the full gate on the final HEAD. Next item: ps-2ab.

Feature item ps-2a (PS-2a's second part, after ps-2aa; plan `docs/spec/presupposition-PLAN.md:847-863`, 4.6
`:498-520`; spec `docs/spec/presupposition.md` 4.7). Branch `feature/ps-2a`, merge base 098dbe688 (main's tip at
launch). Command outputs: `evidence/tests.txt`.

## Preconditions

- **Statement gate.** PASSED, as the task states. ps-2aa's probe form, rerun over Wire.lean (`evidence/tests.txt`):
  39 declarations, each compared with the stub's 4.7 declaration of the same name and with spec 4.7's lean blocks
  (`presupposition.md:841-1069`), comments stripped and whitespace normalised (script `evidence/probe.py`, run at
  2412b516f when `candidateTable` was still in Wire.lean). 38 are equal. `candidateTable` differs from both, and
  deliverable (2) requires that: the stub and the spec hold the empty placeholder until PS-E1 fills it (spec `:1218`,
  section 6). It now lives in the generated `Table.lean` (see "Deviations").
- **ps-2aa merged.** Wire.lean on main has every type `admit` needs except the cut readings block. This item
  restores that block, so ps-2ab finds `RReading` to `PDoc` in place.
- **Synthesis round 2.** Item 1 (no mode; the report is a layer field): kept. The item adds no mode, schema or relay.
  Item 5 (the RF row) and DEC 10 (a heading presupposition is the heading unit's `.layer` assumption) belong to
  `admit` and the A24 fixture, so they move to ps-2ab. This item implements none of them.
- **Layers.** `tools/check_lean_imports.py`: "Lean layer graph kept (791 modules, 18 reviewed legacy edges)". Wire.lean
  now also imports `VE.Presupposition.Rules` (for `conditionNode`), as ps-2aa's full version did. `Table.lean` imports
  Wire.lean. I made no `layer_policy` edit.
- **In-flight overlap.** No branch in flight touches `lean/VE/Presupposition/`. Shared files: `tools/trust-classes.json`
  (added entries; `candidateTable` moved to `Table.lean`'s entry), `docs/trust-baseline.json` (two allowances, S and V),
  `tools/regen_generated.py` (one entry, which foundation/me-1 and infra/arch-AR-1 also edit; both are 4 weeks old) and
  generated inventories.

## Plan rows delivered

| Row (task "Deliver") | Commit | Evidence |
|---|---|---|
| (1) `RContent`, `RReading`, `UContent`, `DocUnit`, `PDoc`, `env`, `unitOf`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`, `premisesBefore`, `claimReading`, `ruleReading`, `emitted`, `aliasesOf`, `expectedReadings` (ps-2aa's 9cdd78473 text, copied) | 2412b516f | Wire.lean:100-161, :181-215 |
| (1) the 7.1 `expected` row; S12 and S26 reading shapes; S25; S27's alias half (seeded bug 2); S17; the rule-act readings (9cdd78473's guards, copied, renamed where ps-2aa's later fixtures took the name) | 2412b516f, 2f03e4baf | Examples.lean:616-712 |
| (2) `candidateTable` = `docs/research/presupposition-E1/candidate-table.json` cell by cell, generated (spec 6) by `tools/presupposition_table.py`; `tableOk` holds; one guard per row and one for an unknown row | 2412b516f, generator after the self-review | Table.lean; Examples.lean:498, :512-519; tests/test_presupposition_table.py |
| (3) `admit` + A1-A28 | cut to ps-2ab | "Cut" |
| (4) Run.lean | cut to ps-2ab | "Cut" |
| (5) the 19 `admit_*` statements | cut to ps-2ab | "Cut" |

Guards in Examples.lean: 213 → 258 (`grep -c '^#guard'`). ps-2aa's guard `!carrierAllowed candidateTable chk12 .assumed`
was a fact about the empty table. It now reads `carrierAllowed … .assumed && !carrierAllowed … .conditioned`, plus the
empty table's `!carrierAllowed (fun _ _ => []) …` (:533-534). The empty table's `tableOk` is kept at :498.

## Cut (reviews/dri-decisions-20261109-ps-2a.md item 1, SIGNED by the DRI)

I measured at the (2) boundary with `tools/trust_map.py --check`: trusted +102 (S +59, D[V] +25, G[V] +18, K +0). The
readings block alone is 97 of these. ps-2aa's "~47" was a partial measure; its REPORT's own numbers give 217 - 120 = 97.
That leaves 48 of R16's 150 lines. Untied, `admit` (spec 4.7's five steps) cannot fit in 48. The task's pre-approved
seam cuts only (5) and then (4), so I asked the DRI (msg.sh, 2026-11-09T10:18Z). The DRI ruled that ps-2a ends at (1)+(2).
**ps-2ab** takes (3) `admit` with A1-A28, (5) the 19 statements, which tie `admit` so its lines leave the trusted
count, and (4) Run.lean last. ps-2ab has its own seam: Run.lean to ps-2ac. The M2 seeded bug and the "admit drops one
emitted candidate" bug move with `admit`. Item 2 of the same decision confirms `admit := admitWith candidateTable
<fixed inputs>`, which is spec 4.7 step 5's text (`:1105-1108`), for ps-2ab.

## Deviations

- **`candidateTable` moved to a generated file.** Spec section 6 (`:1333`) says a generator writes it from PS-E1's JSON.
  So `tools/presupposition_table.py` writes `lean/VE/Presupposition/Table.lean`, one `match` arm per non-empty cell, in
  the JSON's candidate order. The generator is registered in `tools/regen_generated.py` (`presupposition-table`, fresh
  test `tests/test_presupposition_table.py::test_the_lean_table_is_the_e1_table`). It refuses an unknown class or
  candidate, a missing or extra class and a repeated row (4 tests), and it follows a changed JSON (1 test). The
  declaration keeps its name, `VE.Presupposition.candidateTable`, so the statements ps-2ab proves are unchanged. It
  moved out of Wire.lean because `Candidate` is defined there. Wire.lean's text is otherwise the stub's.
- **Guards renamed on copy.** ps-2aa's later fixtures took `repR` and `chkR` (a rule-name argument). The copied
  rule-act guards use `repRR` and `chkR "…" "r1"`. The copy of `unitModes rep26 …` is dropped, because ps-2aa's
  `rep26` (with `chk12`) already guards `unitModes` (:561).
- **regen skipped `route-cases`** (`--skip route-cases`), as ps-2aa did. It reads no presupposition file. The chain's
  gate checks it.

## Seeded bugs (Lean and Python; no Rust changed)

`mutants.json` lists 39 hand mutants with `file`, `find`, `replace` and `test`. 37 are Lean, at least one per new
trusted definition (the five types included). 2 are Python, in `tools/presupposition_table.py`. I applied each alone,
built `VE.Presupposition.Examples` (Lean) or ran `tests/test_presupposition_table.py` (Python), and restored the file.
All 39 fail (`evidence/tests.txt`). The first Lean run left 3 survivors, lookups that the fixtures never put second.
Two fixtures kill them: a foreign-unit conditioned obligation (Examples.lean:645-647) and a foreign rule first in the
tree (:682-687). The claimed behaviours:

| Id | Behaviour | Mutant | Fails |
|---|---|---|---|
| M-aliasesOf-shallow | R-D1, S27 (task seeded bug 2): in place aliases conditioned only at a shallow frame | drops `decide c.frame.shallow` | Examples.lean:638, :648, :651, :653 |
| M-emitted-inPlace | R-D1, R-4: in place is never a reading of its own | keeps in place in `emitted` | :624, :626, :628, :629 |
| L-premisesBefore-strict | S17: premises strictly before the unit | every unit | :705, :723 |
| L-candidateTable-generic | PS-E1's open cell (Table.lean) | generic's consequent loses unconditional | :517 |
| L-candidateTable-shape | `tableOk` on PS-E1's table (Table.lean) | assumed beside asserted | :498, :517 |
| P-table-repeated-row | the generator refuses a repeated row (Python) | check dropped | `test_names_outside_the_spec_are_refused[repeated row]` |
| P-table-empty-arms | one arm per non-empty cell (Python) | arms for empty cells | `test_the_lean_table_is_the_e1_table` |

**R16 mechanical mutants** (`trust-mutants.json`, `trust-mutants-allow.json`). The first sweep, at bd818c4d, gave
171 KILLED, 16 SURVIVOR, 21 UNKNOWN and 36 INVALID. The survivors were list positions my guards did not move: a
lookup whose entry was first or last, a one-element background or proof list, a condition never last on its rule, an
alias cell with in place last, and no unformalised unit. The guards at Examples.lean:714-730 kill each one; I replayed
all 16 locally first. The 21 UNKNOWN are constructor drops and bare `[]`s that do not elaborate. Each is allowed by
definition and operator, with a reason that names the hand mutant covering it. INVALID means Lean refused the mutant's
own text (`Option.take`). The rescore (176 carried) gave 186 KILLED, 0 SURVIVOR, 0 UNKNOWN, 36 INVALID and 22 ALLOWED,
exit 0. `Table.lean` is not swept, because the sweep selects the trusted lines a branch changes in hand-written files.
The hand mutants L-candidateTable-* cover it.

## Trust

`tools/trust_map.py --check` PASS against 098dbe6886d6: trusted +117, K +0. Wire.lean +94 (S +51, D[V] +25, G[V] +18),
Table.lean +23 (S, `candidateTable`). Examples.lean is T (its new fixtures are classed T), and unclassified is +0.
Classes: S for `RContent`, `RReading`, `premisesBefore`, `claimReading`, `ruleReading`, `emitted`, `aliasesOf`,
`expectedReadings` and `candidateTable`; D[V] for the document's shapes `UContent`, `DocUnit`, `PDoc`; G[V] for the
accessors `env`, `unitOf`, `unitContent`, `unitAsserted`, `unitReadings`, `nodeCertificate`. `docs/trust-baseline.json`
gains two allowances (S 74, V 43), each "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-2a, 2026-10-18". The
"## ps-2a" ties-pass row is in FOLLOW-UPS.md.

## Size, bytes, evaluators

- **Size.** `git diff --numstat 098dbe688`, without generated files (codemap, inventories, trust-baseline, Table.lean,
  `.gitattributes`, `tests/history-dependent.json`) and the sweep's output `trust-mutants.json`: Examples.lean 133,
  Wire.lean 112, tools/presupposition_table.py 79, tests/test_presupposition_table.py 60, trust-classes.json 43,
  mutants.json 44, trust-mutants-allow.json 44, evidence 64, regen_generated.py 3, VE.lean 1, merge-tooling.md 1,
  DELTA.md 9, and this REPORT. That is 767 lines with this REPORT (174), over the ~600 line. The overage is the generator and its tests (142 lines),
  which spec 6 requires and which the self-review asked for (one owner for the table). The rest is 9cdd78473's copied
  guards and the sweep's survivor fixtures. There is no product code left to cut. I did not cut the generator,
  because a hand copy of the table is the finding it fixes.
- **Pilot bytes.** 0: no route reads Wire.lean or Table.lean yet.
- **Evaluators.** None added. `expectedReadings` maps over one cell (at most 5 candidates in a `tableOk` table).
  `premisesBefore` walks the unit list once. Neither is a runner or a mode. `admit`'s limits are ps-2ab's (step 1).

## Spec re-read

- 4.7 definitions against `presupposition.md:941-1069`, by the probe (38/39 equal; `candidateTable` as above).
- Section 6 `:1324-1335`: one object per row, class names `top` … `rule_guard`, candidate names with `in_place`, the
  measured order kept (`tools/presupposition_table.py`, `CLASSES`, `CANDIDATES`; tests/test_presupposition_table.py).
- 7.1 S12 `:1369` (two readings; conditioned's aliases `[inPlace]`; no in-place reading: :624-629), S25 `:1370`
  (:636-637), S26 `:1371` (in place T, asserted F, assumed premise `q` F: :640-647), S27 `:1372` (no in-place reading,
  no alias: :650-654). `expected` (7.1, one-candidate cell gives one reading; heading none: :657-665). S17 `:1379`
  (the second unit's premises are the background and the first's claim: :705).
- Section 6 against `candidate-table.json` (candidate order as listed; `tableOk` holds: :498).

## Final checks

Each ran once, on committed trees of this branch (`evidence/tests.txt`):
- `uv run python tools/regen_generated.py --write --skip route-cases`: exit 0, 37 entries (codemap, inventories,
  `.gitattributes` with the new entry, `tests/history-dependent.json`).
- Full `lake build` (inside regen) and `python3 lean/audit.py`: PASS, 791 source files.
- `tools/trust_map.py --check`: PASS, trusted +117, K +0.
- trust_mutants (`mac-pytest.sh --trustmut`): first run exit 1 (16 survivors), rescore exit 0 (see "Seeded bugs").
- Selected tests, `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base 098dbe688 --run` at e5591823d (clean):
  498 units, 1 failed: `tests/test_merge_tooling_evidence.py::test_the_generated_file_table_names_every_entry`.
  `docs/merge-tooling.md` lacked the new `presupposition-table` row. I fixed it (fcded573) and reran only that id
  through `mac-pytest.sh`: 1 passed, exit 0. That run does not count as the gate's same-tree reuse, so the chain
  gate runs in full.
- Size: `git diff --numstat 098dbe688` without generated files: 767 lines (753 added, 14 deleted), REPORT.md 174 of
  them. That is over the ~600 line (see "Size, bytes, evaluators").

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 1 A, 3 B, 5 C; fixed 9. A: the hand-copied table, now generated (`tools/presupposition_table.py`). B:
the empty table's guards restored (:498, :534); a mutant that `tableOk` catches (L-candidateTable-shape, :498); the
Wire.lean docstring no longer overclaims. C: the stray comment, the REPORT's :559 to :561, the probe script committed
(evidence/probe.py), S17's own shape guarded (:705), the allowance count given (two).

1. Typed Lean answers: N.A., no relay or service mode added (`git diff --name-only 098dbe688...HEAD` has no Protocol.lean or schema).
2. Deliverables: PASS, (1) and (2) are built (table above); the cut of (3)-(5) is SIGNED (dri-decisions-20261109-ps-2a.md item 1).
3. Tests can fail: PASS, `mutants.json` (39/39 fail), `trust-mutants.json` exit 0 with `trust-mutants-allow.json`.
4. Three-way agreement: N.A., no Lean answer reaches Python or Rust. The Python generator only spells the JSON in
   Lean, and Lean checks the table (`#guard tableOk rowNames candidateTable`, Examples.lean:498).
5. R8 binding: N.A., no Lean answer is read by Python.
6. Gate evidence: PASS, the sweep and the selected tests ran on committed trees of this branch (`evidence/tests.txt`, "Final checks").
7. Unsigned items: PASS, `trust_map --check` exit 0 with the two R16 allowances; no DELTA rows.
8. User-visible changes: PASS, no answer path edited; `grep -rl Presupposition.Wire lean/VE --include=*.lean` lists only lean/VE/Presupposition/ files.
9. Test selection: PASS, `select_tests` picked 498 units and `tests/test_presupposition_table.py` among them ("changed"); the Lean seeded bugs fail at `lake build` of Examples.lean, which the gate builds.
10. Statements: N.A., no theorem added (the 19 `admit_*` statements are ps-2ab's); `lean/statements.txt` unchanged ("changed: 0").
11. Budgets: N.A., no operation with a budget.
12. CPU or memory: N.A., the new Lean runs only in `#guard`s at build time; the generator reads one 1.2 KB JSON.
13. Test-removed trailers: N.A., no test removed or renamed (the commits remove none; `git log 098dbe688..HEAD --diff-filter=D --name-only` lists only evidence/runmut.py, not a test).
14. Both directions: PASS, `candidateTable` accepted (:498, :512-519) and refused shapes (L-candidateTable-shape);
    the generator renders (`test_the_lean_table_is_the_e1_table`, `test_a_changed_table_changes_the_rendering`) and
    refuses (`test_names_outside_the_spec_are_refused`, 4 cases); aliases at shallow and non-shallow frames (:624, :650-654).
    Claims cite `evidence/tests.txt`; "Spec re-read" above.
15. Overclaim: PASS, I checked "no", "every", "none" and "all" here and in DELTA.md against the probe, the grep and
    `evidence/tests.txt`. Silent cut: PASS, the cut was ruled before I stopped (msg.sh 10:18Z, decision item 1). New
    checks can fail: PASS, `mutants.json`. Limits: N.A., no evaluator.

FOLLOW-UP: ps-2ab admit, A1-A28, the 19 admit_* statements and Run.lean (PS-2a part 3)
