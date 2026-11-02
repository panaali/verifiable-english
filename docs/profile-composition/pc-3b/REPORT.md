# pc-3b REPORT: G1 with G4, `composed_superpose_all` (profile-composition PC-3, the rest)

Status: built, ready for review; no DRI signature needed, and no `sorry`. HEAD: the last commit on `feature/pc-3b`.
Changed: `composed_superpose_all` in `Compose/Contract.lean`, one concrete instance in `ContractExamples.lean`, the
statement check extended to spec 1.6, regenerated inventories. No answer changes, trust +0.
Open: nothing in this item. Next item: G1b (`acceptanceXV`, PK-1's owner). Size: 165 Lean, tool and test lines.

## Inputs

- Plan and spec at 3dfadd302: plan PC-3 line 964, spec 1.6 lines 707-730 and line 1751. Main's copy of spec 1.6 is
  identical (`diff` of the `### 1.6` to `### 1.7` range printed nothing), so nothing was copied.
- Statement gate: pc-d2 confirmation review passed (task line; plan change log, sections 13-14). The statement did not
  change.
- Overlap: no in-flight branch edits `Contract.lean`, `ContractExamples.lean`, `tools/check_pc3_statements.py` or
  `tests/test_pc3_statements.py` (`git diff --name-only main...<branch>` over `lean-first/*`, `feature/*`, `infra/*`,
  `foundation/*`). Nine edit `lean/statements.txt`, which is generated.

## Plan rows delivered

| Row | Where | Evidence |
|---|---|---|
| (1) `composed_superpose_all`, by `superpose_all_extra` and `transfers_X`, `hq`, `hQw`, `hcf` as the spec writes them | `lean/VE/Compose/Contract.lean` (80bcb3c1f) | `lake build`; seeds 1-4; `tests/test_pc3_statements.py` |
| (2) One instance on a concrete document with a one-pack `qs`, hypotheses discharged | `ContractExamples.lean`, namespace `G1`, `composed_instance` (f67862ee2, 4bff3c69c) | seeds 4-9 |
| (3) `lean/statements.txt`, audit lists, through their generators | 56bcfa4f4 | `regen_generated.py --write` (35 entries); `lean/audit.py` PASS |

`Contract.lean` imports `VE.Readings.SupPacks`; that makes no cycle, so no new file was needed. `ve/assurance-manifest.json`
did not change under the generator. The same namespace and name as the spec: `VE.Readings.composed_superpose_all`
(`lean/axioms.txt`: `[propext, Classical.choice, Quot.sound]`). The instance calls it by its full name, so a move out of
`VE.Readings` breaks the build.

## The instance

`K1` (S2a's M1 document) under the strict reading `A = [("rs1", 0)]`, one `.constraint` pack whose one premise is
`noAsks`, over the frame's base vocabulary, at the finite model `bare`. Each hypothesis is discharged in Lean: `hq` by
`transfers_ask` (through `pull_denote_frame`), `hQw` by `slotCheck_sound`, `hcf` by `conflict_free_ask`, `hB` by
`bare_admissible_ask`, `hc`, `hA` and `hAc` by `decide` or directly.

The closed checker runs the kernel cannot reduce (`WellFormedDoc`, `accepted`, the conflict certificates) are the premise
`G1Checks`, run by `#guard G1Checks`. That is X3's pattern (`X1Checks`, `SupExtraExamples.lean:106`), for the reason
written there: the audit admits no decision by compiled code.

The certificate names the pack's premise by position and instantiates it (the goal has its quantifiers swapped), so it
reads the premise list's order. `#guard`s in both directions: accepted on `slotUnder K1 A ++ X qs`, refused on
`X qs ++ slotUnder K1 A` and with no pack; `slotCheck` accepts the pack and refuses X1's `noAvoid`; `bare` is admissible
and the conclusion holds, and a base where an agent asks a user is not admissible and the conclusion fails there.

## Deviations from the task's file list

- `tools/check_pc3_statements.py` and `tests/test_pc3_statements.py` (10 lines added): the check read spec 1.2 to 1.5, and
  the statement gate needs 1.6 compared (checklist 17). G1b's seven declarations join `LATER`.
- `tools/trust-classes.json` (11 entries): the new fixture definitions are class `T`. Without them `trust_map --check`
  exits 1 on 29 unclassified lines. pc-3, pc-9 and jt-3p class their fixtures the same way.

## Seeded bugs

`mutants.json` lists 11, each applied alone and restored; the file, the failing check and the build's error are there.

| # | File | Seed | Fails |
|---|---|---|---|
| 1 | `lean/VE/Compose/Contract.lean` | drop `hQw` (task's seed) | proof stops closing, `Contract.lean:226` |
| 2 | same | swap the list in `hcf` | proof, `:227` |
| 3 | same | `hB` without the carried family | proof, `:227` |
| 4 | same | an unused binder `A = []` (the proof closes) | `G1.composed_instance` |
| 5 | `lean/VE/Compose/ContractExamples.lean` | swap the list in the instance's `hcf` (task's seed) | `conflict_free_ask`, `composed_instance` |
| 6 | same | swap the list in the accepted guard (task's seed) | `#guard acceptedOn` |
| 7 | same | the pack carries nothing | `#guard X qs == [noAsks]`, accepted guards |
| 8 | same | `Qc` empty | `#guard !backgroundValidP`, `composed_instance` |
| 9 | same | the refusal guard inverted | `#guard !acceptedOn` |
| 10 | `tools/check_pc3_statements.py` | the section stops at 1.6 | both tests of `tests/test_pc3_statements.py` |
| 11 | same | `countermodelXV` not in `LATER` | `test_pc3_statements_equal_the_approved_text` |

## Trust

`uv run python tools/trust_map.py --check`: exit 0, "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0". No
allowance, no R16 row, no FOLLOW-UPS row, no `trust_mutants` run (nothing trusted is new). A theorem adds no trusted
line, as the task expected.

## Checks run

- `lake build`: "Build completed successfully (1240 jobs)", before and after the regen.
- `python3 lean/audit.py`: "PASS: 733 source files; 8187 named theorem declarations audited".
- `uv run python tools/check_pc3_statements.py`: "PC-3: 28 declarations equal the approved text (RouteFacts staged);
  later batches: 23".
- Selected tests: `mac-pytest.sh --select -- --base ea108ea4e... --run`, on HEAD 4e6127077: exit 0, 4 cloud shards, 111 units, 111 passed (26 + 27 + 26 + 32),
  run pc-3b-4e612707-t635769. The first attempt never started (it queued for the Mac slot past 50 min); I stopped it and
  reran it detached.
- `uv run python tools/gate_collection.py --check --prebuilt`: "31595 collected ... 0 added, 0 removed by a trailer, 0
  refused, 0 stale and 0 malformed trailers".
- `tools/check_lean_imports.py`: exit 0.
- Not run: the full gate (the chain runs it on the final HEAD).

## Spec re-read

- `composed_superpose_all` against the spec (lines 716-730): every binder, in order, by `check_pc3_statements.py`.
- Namespace and opens against the comment on spec line 715 and `SupExtra.lean:20-29`, the `section Extra` open included.
- Proof route against plan line 964 and spec lines 707-712: `superpose_all_extra` at `Q := Packs.X qs`, by `transfers_X`.

## Pilot bytes

0: the theorem is read by no route.

## Size

`git diff --numstat` against the merge base, excluding generated files: Lean 155, tool 4, test 6, trust classes 12,
`mutants.json` 83, DELTA 9, this report. Under the ~600 line.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A., no route, relay or schema changes (`git diff --name-only`: nothing under `ve/`).
2. Every deliverable built: PASS, the plan rows table above.
3. Tests and gates can fail: PASS, `mutants.json` (11 seeds, each failing).
4. Python, Lean and Rust agree: N.A., no language gains a copy and no verdict changes (0 changed paths under `ve/`, `rust/`).
5. R8 binding: N.A., nothing is relayed.
6. Gate evidence matches the final HEAD: the chain runs the gate on the final HEAD; the selected tests ran on 4e6127077, and
   only `REPORT.md` and one seed's wording in `mutants.json` changed after it (`git diff --stat 4e6127077 HEAD`).
7. No unsigned item: PASS, DELTA.md has no table, `trust_map --check` shows trusted +0, and no signature is reserved.
8. DELTA recomputed: PASS, `DELTA.md` (no row), `trust_map --check`.
9. Test selection: PASS, `select_tests.py --base ...` lists `tests/test_pc3_statements.py`, which seeds 10-11 fail.
10. Lean statements say what is claimed: PASS, `tests/test_pc3_statements.py`, `G1.composed_instance`, seeds 1-5.
11. Budgets and limits: N.A., no evaluator, runner or mode (the feed's evaluator rule does not apply).
12. CPU or memory: N.A., no run path changes.
13. Removed or renamed tests: PASS, `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS, the `#guard`s of "The instance", "Checks run", "Spec re-read".

Sibling lessons (pc-1-review F1, a reader that misses a field; F2, quadratic growth before a limit): N.A., this item adds
no reader and no evaluator.
