# ap-3 build report: act trees, ops and the modal × connective table (part 1 of AP-3; Lean only)

**No DRI signature is reserved.** Trust growth is S +64, K +0, signed by standing ruling R16 ([DELTA.md](DELTA.md)
row 1). **AP-7 was not run**, and it cannot run here. It needs blind auditors (model calls, which this item may not
make) and `phraseReadings` (AP-4), and that needs the act grammar's rule table and meaning (ap-2b, ap-2c), which are
not on main and are not queued. This part changes no route and not `_lean_route`, so merging it is not a release and
does not need AP-7. The part that changes the route (ap-3d below) must not merge before AP-7 has run and passed.

**The item is cut.** AP-3 as planned reads joined acts with `VE.Acts.read`. That needs the grammar `grammar V` and
`meaning V` (spec 5.2, 5.3). ap-2 delivered only their first part, and its report named the rest ap-2b (rule table),
ap-2c (meaning, `read`) and ap-2d (rendering). None of them is in FEATURE-QUEUE.tsv. So this item delivers the part
of AP-3 that needs no parser: the act trees, the ops and the table, with the table's 14 equations. The next items
are in section 6. The size rule cut it further (section 5).

Plan: `research/act-phrases-p1` at `bb5b2f90d`, [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4
"AP-3", 2.3, 2.6. Spec: [act-phrases.md](../../spec/act-phrases.md) 1.5, 1.7, 5.4, 6.1, 6.2, 11.2, 11.3. Both files
on main equal the pinned commit's (`diff` against `git show bb5b2f90d:…`: identical). DRI-DECISIONS-PHASE2:
AP2 (Group B only until queue 4.4; this part claims no unit), AP4 (D9 option (i)), SC1 (SC-4 names AP-3's split
rules through `VE.Acts.SplitMap`: not built here, see ap-3c).

## 1. Statement gate

The specification's statement review converged on **FIX**. Draft 2 applied it, and `act-phrases-p3ver1` verified
that: **PASS** (ap-2's report, section 1). Section 6's statements are draft 2's. `lean/statements.txt` gains only
this part's theorems (the 14 `table_*` equations). No existing statement changes. The table's equations stay
**provisional** until AP-7 passes (D3).

## 2. Plan rows delivered and not delivered

| Plan row (AP-3) | Status | Where |
|---|---|---|
| The table (2.3) | **done**: `Op`, `opOf` (spec 6.1: plain with sign false has no op), `Simple`, `freeTable`, `table` (6.2), for the five deontic modals only | `lean/VE/Acts/Table.lean` |
| Statements `table_*` | **done**: all 14 of spec 6.2 (`table_one`, `table_must_all`, `table_must_any`, `table_must_any_refused`, `table_mustNot_any`, `table_mustNot_all`, `table_mustNot_all_split`, `table_free_all_own`, `table_free_all_shared`, `table_free_all_split`, `table_free_any`, `table_free_any_split`, `table_free_nor`, `table_needNot`), proved, audited | `Table.lean`, `lean/VE/Audit.lean` |
| Act trees (spec 1.5, 5.4; needed by the table) | **done**: `Join`, `Part`, `Filler`, `Modifier`, `Atom`, `Act`, in a module of their own, so ap-2c's `meaning` builds these trees | `lean/VE/Acts/Tree.lean` |
| Table fixtures T1-T10 (11.3) | **done**, on the trees of 11.2 written by hand (G6, G7, G9, G10, G11, G12, G14v), plus every other cell of 2.3 and E3's count (five prohibitions for G14v) | `lean/VE/Acts/TableExamples.lean` |
| Seeded bug, Lean: *must* distributes over *or*, T8 fails | **done** (`must-distributes-over-or`) | [mutants.json](mutants.json) |
| Rendering (5.5: `Atom.normal`, `tokText`, `partAct`) and paraphrases (6.2: `paraphrase`, `paraphrases`, `distinctTexts`, `distinctTexts_ok`, `paraphrases_nodup`; D-23, D-32; E9, P12n) | **cut to ap-3b** (size): built, with fixtures and mutants, then removed from this branch; kept on local branch `wip/ap-3b` at `9c5bb9fe0` | — |
| `elaborate`, `elaborateMap`, `SplitMap` (SYNTHESIS 2.6), `ActsDoc`, `readingOf`; `elaborateMap_fst`, `splitMap_exact`, `elaborate_parts`, `elaborate_identity`, `elaborate_wellFormed`, `elaborate_one_reading`, `elaborate_unspec`, `elaborate_faithful`; fixtures E1-E10, E12-E16 | **ap-3c** (size, R16) | — |
| `checkAct` (6.4), `decodeElaboratedU` and its theorems, `authorLimits` / `checkAuthorN_split` (`NormDefaults/Wire.lean`), the frame decoder in `Norms/Wire.lean`, `readings_lexical_only`, twins of the reached soundness theorems | **ap-3d**; needs ap-2b and ap-2c (`read`) | — |
| The `acts-elaborate` relay (shape, encoder theorem, schema, `ve/norms.py` binding, fuzz tests), `_lean_route` true for `acts@0`, the reference table test, E5j, E11 | **ap-3d** (a release; AP-7 before it merges) | — |
| Seeded bug, Python: one row per source rule instead of the per-simple-act wordings | **ap-3d** (no Python changes here) | — |
| AP-7 | **not run** (above) | — |

## 3. Seeded bugs and mutants

[`seed_bugs.py`](seed_bugs.py) plants each bug in `lean/VE/Acts/Table.lean`, cuts the file's theorems (so the bug
must break a fixture, not only a proof), builds `VE.Acts.TableExamples` and restores the file. Result in
[`mutants.json`](mutants.json): all 16 bugs are **KILLED** (a failed `#guard` of `TableExamples.lean`, and no
other error). The restored build exits 0. One bug per claimed behaviour and per table cell:

| Bug | Claim it breaks |
|---|---|
| `must-distributes-over-or` | the plan's seeded bug: T8 (G6 under *must*: no reading) |
| `must-or-nor-refused-only`, `must-and-one-act` | *must* on *nor*; *must* distributes over *and* |
| `must-not-and-always-split`, `must-not-or-one-act` | T9; T1 and T3 (prohibition distributes over *or*, *nor*) |
| `need-not-reads` | T10 |
| `free-own-to-together`, `free-split-and-together`, `free-shared-split-only` | T6; a split marker's *and*; a shared *to* |
| `free-nor-reads`, `free-split-or-one-act`, `free-or-one-act-only` | T4; T7; T5 |
| `free-one-dropped`, `table-one-dropped` | `freeTable`'s own simple act; T2 |
| `prohibition-is-need-not`, `plain-false-has-op` | `opOf` |

The sweep in the same script replaces every `Op` in `opOf` and `table` with each other `Op`, one occurrence at a
time. 20 are killed. The other 28 are refused by Lean, because a swapped pattern op leaves a redundant or missing
case. Every one of `opOf`'s five results swapped four ways is killed.

R16's "every new trusted definition is exercised by a test that can fail":
- `tools/trust_mutants.py --max-mutants 1000` on the final Lean gave 159 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID,
  26 ALLOWED and 0 NOT RUN, over `opOf`, `freeTable` and `table` ([trust-mutants.json](trust-mutants.json)).
- Each allowance is a mutant that does not elaborate (a flipped pattern Bool, or `all` read as `any`, leaves a case
  missing), with its reason in [trust-mutants-allow.json](trust-mutants-allow.json).
- `Simple`, `Op` and the act trees are data types that every fixture constructs. A mutant that changes a constructor
  or a field of one does not elaborate, and swapping two constructors of the same arity changes no answer, since every
  use matches by name. The tool has no operator for them.

Only Lean product code changed, so all seeded bugs are Lean's.

## 4. Trust

`trust_map.py --check`: PASS. K +0, S +64, V +0, trusted +64. Table.lean +38 (`Simple`, `Op`, `opOf`, `freeTable`,
`table`) and Tree.lean +26 (the act trees), all S. `TableExamples.lean`'s definitions are T. The allowance is
recorded with `--allow` and signed by standing ruling R16. The FOLLOW-UPS "## ap-3" row asks for the ties pass: tie
`table` to its 14 equations, which characterise every cell.

## 5. Size, tests and checks

- **Size** (hand-written lines added, `git diff --numstat` against the merge base):
  - Lean product: Tree.lean 35 and Table.lean 90.
  - Fixtures: `TableExamples.lean` 118.
  - `lean/VE.lean` +3, the trust side table `tools/trust-classes.json` +41.
  - Evidence: `seed_bugs.py` 123, the allow file 16.
  - This report and DELTA.
  - Total about 420, and about 660 with this report (219) and DELTA (22), so a little over the ~600 guideline
    because of the documents. The JSON evidence is written by the scripts, and the inventories by
    `regen_generated.py`.
  - The first build of this item also held the rendering and the paraphrases. With them it measured about 770
    hand-written lines before the documents, and R16's count would have been S +110. So they were cut to ap-3b (see
    `wip/ap-3b`).
- **Builds and checks:**
  - `lake build` (all 1,069 jobs) passes.
  - `python3 lean/audit.py` PASS (614 files, 7,050 theorems).
  - `regen_generated.py --check` passes (see the test record below).
  - `trust_map.py --check` PASS.
- **Selected tests:** see section 8.
- **Overlap:** before I started, no in-flight branch (`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`) touched
  `lean/VE/Acts/`, `lean/VE/Norms/`, `lean/VE/NormDefaults/` or `tools/layer_policy.py`. This part adds new files
  only, plus the import root `lean/VE.lean`. `tools/trust-classes.json` is a side table that other items extend in
  other modules' entries.
- **Pilot bytes expected to move:** 0 B (*estimate*). No route reads the table yet. AP-3's u079b (76 B, *estimate*),
  M2's u027 and u045a, and the Group B units wait for ap-3d and for AP-7.

## 6. Next items

1. **ap-2b, ap-2c** (act-phrases AP-2, not queued): the rule table and `grammar_wf`; then the meaning (under D9 (i)),
   `readings`, `read`, `analyse`. They should build the act trees delivered here (`VE.Acts.Act`), not new ones.
   ap-3d and AP-4 need them, and so does AP-7.
2. **ap-3b** (ready, no dependency): rendering (`Linearize.lean`: `Atom.normal`, `tokText`, `Atom.text`, `partAct`)
   and paraphrases (`paraphrase`, `paraphrases`, `distinctTexts` with `distinctTexts_ok` and `paraphrases_nodup`;
   D-23, D-32; E9's exact text, P12n).
   - Built and measured on `wip/ap-3b` at `9c5bb9fe0`: S +46 (Linearize); the paraphrase texts are G[R].
   - Its evidence on that branch: `seed_bugs.py` with 17 bugs killed and a 131-row constructor sweep (31 killed,
     100 refused). A trust_mutants run of that code gave 332 killed, 46 that do not elaborate, and 5 equivalent
     survivors (`take 1` of a list of at most one element). Its JSON is not committed, so ap-3b reruns it. Restore
     the branch from there.
   - It overlaps ap-2d's `Linearize.lean`. Whichever lands first owns `Atom.normal`, and ap-2d adds `Atom.canon`,
     `normalOk` and `read_normal`.
3. **ap-3c** (after ap-3b; needs no parser, since the trees come in `ActsDoc.acts`). It is what WG-2 and SC-4 wait
   for (SYNTHESIS 2.6; DRI SC1):
   - `ActsDoc`, `SplitMap`, `readingOf` (D-20 to D-24), `elaborateMap` (steps 1-5 and 7 of spec 6.3), `elaborate`;
   - `elaborateMap_fst`, `splitMap_exact`, `elaborate_parts`, `elaborate_wellFormed`, `elaborate_one_reading`,
     `elaborate_unspec`;
   - fixtures E1-E10 and E16.
   - Expected trust: about 95 lines. A form that is easy to prove makes each refusal a `find?` / `firstDup` check,
     not a `for` loop.
4. **ap-3d** (after ap-2c and ap-3c; a release):
   - `authorLimits`, with `checkAuthorN_split` and step 6, then `elaborate_identity` (its hypothesis uses
     `authorLimits`) and `elaborate_faithful`;
   - `checkAct`, `decodeElaboratedU` and the twins;
   - `readings_lexical_only` (D-33);
   - the `acts-elaborate` relay through the full recipe, and `_lean_route`;
   - E5j, E11-E15, the reference-table test and the Python seeded bug.
   - AP-7 runs on its branch before it merges. AP-7 needs AP-4's `phraseReadings` prototype and the auditors (a
     model call, the orchestrator's pilot job).

## 7. Deviations from the plan and the spec (recorded here, not in the copied plan)

- **Act trees in their own module, `VE.Acts.Tree`.** They are AP-2 types (spec 5.4), and this item defines them
  first because the table needs them. They were first added to `Syntax.lean`, but ap-2's
  `tests/test_acts_vocab_mutants.py::test_the_list_valued_names_are_read_from_the_declarations` pins that file's
  list fields, and `Atom.args` would be a new one. So they moved, and `Syntax.lean` is unchanged.
- **Trees written by hand.** The fixtures build 11.2's trees by hand, because no parse exists yet. ap-2c should add
  a `#guard` that its `meaning` gives these trees.
- **Fixture file name.** The fixture file is `TableExamples.lean`. The plan's `ElaborateExamples.lean` belongs to
  ap-3c.
- **Spec gap for ap-3b/ap-3c.** `paraphrase` takes the plain predicate's form (*has the right* or *is entitled*),
  but neither `Regulated` nor spec 6.3's `ActsDoc` carries the form: the decoder reads it from the raw declaration
  (`Norms.Wire.plainWording`). So D-23 for an *is entitled* predicate needs `ActsDoc` to carry the forms, which is
  a field the spec does not list, or it defaults to *has the right*. ap-3c should take this to the bounded re-check.
- **Mutant tool host.** `tools/trust_mutants.py` ran directly on the VM, not through
  `mac-pytest.sh --trustmut` (BUILDER-CHECKLIST 3, build checklist 13a). The verdicts are the tool's either way.

## 8. Tests

- **Selected tests:** `mac-pytest.sh --select -- --base 058fea806c0b --run`, on the Mac runner, on `d449f36cc` (the
  final code; only this report and DELTA were uncommitted). 75 units ran, among them the lints, `lake build`,
  `lean/audit.py` and 70 test files. Exit 0, 0 failed. No test in `main-known-red.txt` was hit.
- **An earlier run failed one test.** It ran on `f07404ad9`, with the act trees still in `Syntax.lean`. The failing
  test was `tests/test_acts_vocab_mutants.py::test_the_list_valued_names_are_read_from_the_declarations`: `Atom.args`
  was a new list field of that file. Fixed by the move to `VE.Acts.Tree` (`c1a141b9e`).
- **A run that did not finish.** The first attempt, piped through `tail`, was stopped at the 2-hour background
  limit with no output. It was rerun with a log file.
- **Other checks:**
  - `tools/gate_collection.py --check --prebuilt`: 19,381 collected; 0 added, 0 removed, 0 refused, 0 stale and 0
    malformed trailers. No test was removed.
  - `regen_generated.py --check`: 33 entries, all current.
  - `trust_map.py --check`: PASS.
  - `lean/audit.py`: PASS.
- **Not run:** the full gate (the chain runs it on the final HEAD), AP-7 (above) and any pilot.

## 9. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer. No mode, route or row is added, and no Python reads anything new.
2. PASS: section 2 copies every AP-3 plan row, with its commit or file, or the next item it is cut to (size, R16,
   and the missing ap-2b/ap-2c). Grepping the diff finds no Python or Rust change, no report test and no authority
   switch. `git diff --name-only main...<branch>` over every in-flight branch shows no overlap.
3. PASS: [mutants.json](mutants.json) records 16 seeded bugs, all killed by `TableExamples.lean` with the theorems
   cut, and the op sweep (20 killed, 28 refused). [trust-mutants.json](trust-mutants.json) records 159 killed, 0
   survivor, 0 unknown and 26 allowed, each allowance with its reason in
   [trust-mutants-allow.json](trust-mutants-allow.json). The plan's *must*/*or* bug fails T8.
4. N.A.: no Python or Rust path computes the table, and no existing input changes behaviour. Nothing reaches the new
   modules but `lean/VE.lean`.
5. N.A.: no Lean answer is read by Python.
6. PASS: no gate evidence is claimed. The selected run is on `d449f36cc`. The commit list below is from
   `main..HEAD --no-merges`, and the base is `git merge-base` (`058fea806c0b`). The full gate is the chain's.
7. PASS: DELTA row 1 cites R16 and meets its conditions: per file, re-measured by `trust_map.py --check`, every
   definition exercised (item 3), and the FOLLOW-UPS "## ap-3" row. No other row, and no reserved signature.
8. PASS: there is no user-visible change. No route, mode, diagnostic or English line reaches the new code, and
   DELTA says why it has only the trust row.
9. PASS: `select_tests.py --base 058fea806c0b` selects 75 of 461 units, not all of them. The selection includes
   `lake build`, which builds `VE.Acts.TableExamples`, so every seeded bug in `Table.lean` fails a selected unit
   (`seed_bugs.py` runs the same `lake build` target).
10. PASS: the 14 `table_*` theorems are about `table`'s returned value. With them cut, each seeded bug still breaks a
    fixture. `lean/statements.txt` gains only these theorems, and every statement is spec 6.2's.
11. N.A.: no budget, limit or deadline is added. The table is total and has no budget.
12. N.A.: no route runs the table yet, and it is a single match with no enumeration.
13. PASS: no test is removed or renamed. `tools/gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and
    0 malformed trailers.

## 10. Commits (`main..HEAD --no-merges`)

- `d449f36cc` ap-3 evidence: trust_mutants on the final Lean (mac-pytest --trustmut; VM fallback): 159 killed, 0 survivor, 0 unknown, 26 allowed
- `c0533076c` ap-3 evidence: mutants.json re-recorded after the move (16 bugs killed; sweep 20 killed, 28 refused)
- `c1a141b9e` ap-3: the act trees in their own module VE.Acts.Tree (Syntax.lean unchanged: ap-2's test_acts_vocab_mutants pins its list fields); R16 allowance re-recorded per file (Table +38, Tree +26)
- `f07404ad9` ap-3 evidence: trust_mutants full run (159 killed, 0 survivor, 0 unknown, 26 allowed: non-elaborating)
- `daa7ef241` ap-3 evidence: mutants.json re-recorded on the cut item (16 bugs killed; sweep 20 killed, 28 refused)
- `28e144cca` ap-3: cut to the act trees, the ops and the table (size); rendering and paraphrases move to ap-3b (kept on wip/ap-3b)
- `9c5bb9fe0` ap-3 evidence: seeded bugs and the constructor sweep (seed_bugs.py, mutants.json: 17 bugs killed; 131 sweep rows killed or refused by Lean), trust_mutants allow file
- `a0c1eeab7` ap-3: fixtures for Atom.text with no form on an atom without to, and a fixed phrase rendered canonical (A19)
- `caceb12bb` ap-3: fixtures for the mutant survivors (several adverbs, objects, arguments and modifiers; multi-word list parts; freeTable's own simple act); R16 allowance S +110, K +0
- `61203f6f2` ap-3a: act trees, part rendering, the modal x connective table and the paraphrases of readings (Lean only)
- this report and DELTA (the last commit)
