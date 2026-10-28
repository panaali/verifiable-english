# ap-3c build report: elaboration and the split map (part 3 of AP-3; Lean only)

**No DRI signature is reserved.** Trust growth is K +0, S +71, V +76 (147 lines), signed by standing ruling R16
([DELTA.md](DELTA.md) row 1). **The item is cut by the size rule:** `splitMap_exact` and `elaborate_parts` (with eight
lemmas, 230 proof lines) move to **ap-3cb**. They are proved against this item's final definitions, unchanged, on the
local branch `wip/ap-3cb` (`6217fa5c1`, this HEAD plus the proofs). The form gap needs no DRI question (section 6).

Plan: [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) section 4 "AP-3" and 2.3. Spec:
[act-phrases.md](../../spec/act-phrases.md) 6.3, 6.5, 6.6, 10 (D-20 to D-28), 11.3 (E1 to E10, E16). Both files on main
equal `ab010c3f0`'s. DRI-DECISIONS-PHASE2: AP2 (this part claims no unit: it is reached by no route), AP4 (D9 (i): no
change here). SYNTHESIS 2.6: `SplitMap`, `elaborateMap`, `elaborateMap_fst` are here; `splitMap_exact` is ap-3cb's.

## 1. Statement gate

The spec's statement review converged on FIX, draft 2 applied it, and `act-phrases-p3ver1` verified it: PASS. The four
6.6 theorems proved here equal draft 2's text after whitespace normalisation
([`check_statements.py`](check_statements.py): 4 EQUAL). ap-3's and ap-3b's statements are untouched:
`lean/statements.txt` only gains entries (59 lines: the four theorems and four helper lemmas).

## 2. Plan rows delivered

| Row | Status | Where |
|---|---|---|
| (1) `ActsDoc`, `SplitMap`, `partPred`, `partRule`, `dualOf`, `readingOf` (D-20 to D-24, D-23's prefix around `numbered (paraphrases …)`), `splitAtoms`, `partNames`, `elaborateMap`, `elaborate` (6.3) | **done** | `lean/VE/Acts/Elaborate.lean` |
| `elaborateMap` steps 1 to 5 and 7 (6.3): readings; D-25; D-26; D-27; `validate` on the result; the backstop | **done** | `elaborateMap`, `refsOk`, `namesOk`, `partsDistinct` |
| Step 6 (`authorLimits` on the result; E13 to E15) | **ap-3d**: `authorLimits` lives in `NormDefaults/Wire.lean`, which this item may not edit (ap-3's report already planned it so). Until then the backstop's `WellFormedU` refuses those documents, with its own text | — |
| 6.5's table, every row `elaborateMap` owns: `E.predicates`, `Tree.regulated` (name, sorts, default, role, act, permission), `Definition.body` and `Node.guard`/`carveOuts` (D-25), `Tree.nodes` (name, pred, sign, `over`), `UDoc.unspec`; `Doc.lits`, `definitions` unchanged | **done** | `splitReg`, `splitNode`, `splitEnv`, `splitDoc`, `refsOk` |
| 6.5's other rows (W2 units decoded before elaboration; readings candidates; Python inputs, D-28; witnesses) and `test_reference_table_complete` | **ap-3d** (decoder and relay) | — |
| (2) `elaborate`; `elaborateMap_fst`, `elaborate_wellFormed`, `elaborate_one_reading`, `elaborate_unspec` | **done**, proved, audited | `Elaborate.lean`, `lean/VE/Audit.lean` |
| `splitMap_exact`, `elaborate_parts` (6.6; need no `read`) | **ap-3cb** (size): proved on `wip/ap-3cb` | — |
| 6.6 theorems that need `read`, the decoder or `authorLimits`: `elaborate_identity` (its hypothesis is `authorLimits`), `elaborate_faithful` with `readAs`, `IntendedActs` (`Faithful.lean`); 6.4's `checkAct_lexical`, `checkAct_joined`, `decodeElaboratedU_source`, `_wellFormed`, `_lexical`, `readings_lexical_only`, `checkAuthorN_split` | **ap-3d** | — |
| (3) E1 to E10 and E16 as `#guard`s, both sides of each check | **done** (section 3) | `lean/VE/Acts/ElaborateExamples.lean` |
| One mutant per new trusted definition | **done**: 39 seeded bugs, `trust_mutants` 0 survivors (section 4) | [`mutants.json`](mutants.json), [`trust-mutants.json`](trust-mutants.json) |

Not edited: `Grammar.lean`, `Linearize.lean`, `Tree.lean`, `Table.lean`, `Norms/Wire.lean`, `NormDefaults/Wire.lean`,
any route. New files only, plus `lean/VE.lean`'s two imports and the side tables.

## 3. Fixtures (`ElaborateExamples.lean`)

- **E1** exactly: the parts, the rules, `SplitMap`, `elaborate`'s regulated list; the parts declared with the source's
  sorts, the source undeclared, other predicates unchanged. **E2** unchanged with an empty map. **E3** five parts and
  rules, acts in order. **E4** precedence pairwise (and over two rules). **E5** `unspec = [k, p027__1, p027__2]`.
- **E6** D-25 on a guard, a carve-out and a definition (and accepted on a guard naming an unsplit predicate).
  **E7** D-24 from either side (obligation first or its dual first). Also accepted when both read alike, each part's
  dual then being the dual's part. A dual that does not split is refused by `validate` (step 5).
- **E8** D-26 at 65 bytes, accepted at 64; the part rule name at 65, accepted at 64. **E9** D-23's text exactly.
  **E10** D-21, with the accepting side (sign true splits with *to*). **E16** D-27 for a plain predicate and a
  permission, accepted with distinct atoms.
- D-20 (no rule; a rule on another predicate). D-22 (*need not*; T8; *must* on an *or* keeps one act). The first
  failing rule in document order. D-26's four causes (environment, regulated, unspecified, another part) and both
  rule-name causes. Step 5 at E12's boundary (64 accepted, 65 `ResourceLimit: regulated predicates`). The backstop,
  on an unregulated unspecified name and on a kept rule named like a split one. A join of one atom does not split.
- The order of the steps: one fixture per adjacent pair, failing both, shows the earlier step's text.
- Each position (first, middle, last) of each list a check reads, from `trust_mutants`' first-run survivors.

## 4. Seeded bugs and mutants (Lean only; no Python or Rust product code changed)

[`seed_bugs.py`](seed_bugs.py) plants each bug in `Elaborate.lean` and cuts its theorems, so a fixture must fail and
not only a proof. It then builds `VE.Acts.ElaborateExamples` and restores the file. It refuses to run when a new
definition has no bug. Result in [`mutants.json`](mutants.json), on `eca8a51bf`: **all 39 KILLED** by
`ElaborateExamples.lean`, and the restored build exits 0.

| Definition | Bugs (all killed) |
|---|---|
| `ActsDoc`; `SplitMap` | `acts-doc-fields-reordered`; `split-map-fields-swapped` |
| `partPred`; `partRule`; `partsOf` | `part-pred-one-underscore`; `part-rule-no-a`; `parts-from-zero` |
| `dualOf` | `dual-of-obligation-none`, `dual-of-permission-none` |
| `ruleReading` | `rule-reading-sign-ignored` (D-21), `rule-reading-first-listed-only`, `rule-reading-d23-prefix` (D-23, E9) |
| `readingOf` | `reading-of-unequal-accepted` (D-24), `reading-of-dual-ignored`, `reading-of-no-rule-accepted` (D-20) |
| `splitAtoms`; `splitMap`; `partNames` | `split-atoms-one`; `split-map-index-one`; `part-names-kept-dropped` |
| `splitReg` | `split-reg-act-kept`, `split-reg-dual-unmapped`, `split-reg-kept-dropped` |
| `splitNode` | `split-node-over-unmapped`, `split-node-kept-dropped` |
| `splitEnv`; `splitDoc` | `split-env-part-undeclared`, `split-env-source-kept`; `split-doc-unspec-unsplit` |
| `refsOk` (D-25) | `refs-carve-outs-unchecked`, `refs-definitions-unchecked` |
| `namesOk` (D-26) | `names-unspec-unchecked`, `names-regulated-unchecked`, `names-bytes-65`, `names-rule-used-unchecked`, `names-part-count-unchecked` |
| `partsDistinct` (D-27) | `parts-distinct-unchecked` |
| `elaborateMap` | `elaborate-map-refs-skipped`, `elaborate-map-validate-skipped`, `elaborate-map-backstop-rules`, `elaborate-map-steps-swapped`, `-steps-34-swapped`, `-steps-12-swapped` |
| `elaborate` | `elaborate-source` |

**trust_mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --jobs 6 --allow …`, ve-mac-1, on `eca8a51bf`, the
final Lean): 16 definitions with operators, 393 mutants. Result: 271 KILLED, 0 SURVIVOR, 0 UNKNOWN, 54 INVALID,
68 ALLOWED, 0 NOT RUN ([`trust-mutants.json`](trust-mutants.json)).

- The first run had 37 survivors: fixtures had exercised one position of a list only. Each one now has a fixture
  (section 3, last item).
- The allowances ([`trust-mutants-allow.json`](trust-mutants-allow.json), one reason per entry):
  - 6 equivalent drops: `drop 1`/`dropLast` of `M.preds` in `splitEnv`'s `any` and of `M.rules` in the backstop
    (every split source has two parts or more), and of `qs`/`ns` in `namesOk`'s counts (a duplicate source
    duplicates two parts or more);
  - 62 mutants that do not elaborate. One of them is the whole body of `splitReg`/`splitNode` cut to `[]`: the tool
    cannot certify its kill, so the seeded bugs `split-*-kept-dropped` plant it, and it is KILLED.
- The JSON's raw statuses show that the six equivalents are the only allowed survivors.

## 5. Trust, size, tests and checks

- **Trust:** `trust_map.py --check` PASS. K +0, S +71, V +76, trusted +147, all in `Elaborate.lean`. Recorded with
  `--allow` and signed by R16. The fixtures and their helpers are T, and the theorems P. FOLLOW-UPS "## ap-3c" asks for
  the ties pass (after ap-3cb) and records step 6 and the recomputation note.
- **Size** (`git diff --numstat` against the merge base, hand-written lines):

  | Lines | Files |
  |---|---|
  | 276 | `Elaborate.lean`: 165 of definitions, the rest the four theorems and their lemmas |
  | 250 | `ElaborateExamples.lean` |
  | 2 | `lean/VE.lean` |
  | 57 | `tools/trust-classes.json` |
  | 147 | `seed_bugs.py` |
  | 36 | `check_statements.py` |
  | 154 | the allow file, written by a script, one reason per entry |
  | 22 | DELTA |
  | this report | |

  - Without the documents that is about 770, over the ~600 guideline. Measured after the first build at 740, the cut
    removed 230 proof lines.
  - What remains is the definitions, the four cheap theorems, the fixtures R16 requires (62 of the fixture lines
    came from the survivors) and the evidence.
  - Cutting further would leave trusted definitions without fixtures, or remove the definitions the item exists for.
- **Builds:** `lake build` (1,123 jobs) passes. `python3 lean/audit.py`: PASS (641 files, 7,204 theorems).
  `regen_generated.py --check --skip route-cases`: 32 entries current. `route-cases` is skipped because its writer
  needs the Rust binary, which this worktree has not built; no route changed, and the chain's gate checks it.
- `gate_collection.py --check --prebuilt`: 19,797 collected; 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Selected tests:** `mac-pytest.sh --select -- --base 2b13707e7 --run` on ve-mac-1.
  - HEAD `50b48a693` (clean, the final code): 76 of 471 units, among them `lake build` (which builds every guard the
    seeded bugs break), `tests/test_lean_limits.py` and `tests/test_trust_budget.py`. Exit 0, 0 failed.
  - An earlier run (`39dc7475e`) failed only `tests/test_lean_limits.py::test_no_non_frozen_lean_check_hard_codes_a_limit`:
    D-26's byte limit was the literal 64. It now reads `VE.Limits.maxIdentifierBytes` (`eca8a51bf`), and the
    evidence was re-run on that code.
  - No test in `main-known-red.txt` was hit.
- **Not run:** the full gate (the chain runs it on the final HEAD), AP-7, any pilot.
- **Pilot bytes expected to move:** 0 B (*estimate*): no route reads the elaboration until ap-3d.
- **Overlap:** `feature/ap-2b`, `feature/qt-a3b` and `foundation/me-1` edit `lean/VE.lean`. They and `feature/ap-1be`
  and `feature/sc-1bb` also edit `tools/trust-classes.json`. Both are import or entry unions in other modules' lines.
  No in-flight branch touches the new files.

## 6. Deviations, choices and the form gap

- **The form gap (ap-3b section 6), bounded re-check.**
  - No 6.6 statement mentions the plain predicate's form, so none is false without the field. No field is added.
  - `ruleReading` passes `none`, the spec's default, *has the right*. So an *is entitled* predicate's D-23
    paraphrase reads *has the right* until `ActsDoc` carries the forms, which would be a spec change.
  - No DRI question was needed. Recorded in FOLLOW-UPS "## ap-3c".
- **Step 3's "already declared" and "already used"** (D-26). A part name counts as declared when the environment, a
  regulated predicate, the unspecified list or another part has it. A part rule name counts as used when a source
  rule or another part rule has it. Each cause is pinned by a fixture.
  - Draft 2's theorems hold with no well-formedness hypothesis on the source, and these are the conditions that make
    `splitMap_exact` and `elaborate_parts` true (proved on `wip/ap-3cb`).
  - The names are checked one at a time in map order: declared, then over 64 bytes; then the rule names.
- **The backstop (step 7)** also refuses a result in which a split rule's source name survives, with step 7's text.
  This happens only for a source with two rules of one name, one split and one kept, which `validate` does not see in
  the result. `splitMap_exact`'s fourth clause needs it. A fixture pins it.
- **D-25 for a definition** reads `InvalidInput: definition {d} names a predicate that is split into parts; name one
  of its parts` ("the same for a definition"). Rules are checked before definitions.
- **`splitAtoms`** reads the first `acts` entry of `p` (`List.lookup`); step 1 reads every entry. **`partNames`**
  reads the map, so a name is a part only of a regulated source. **`ActsDoc.V` and `declared`** are carried as the
  spec lists them: `declared` is step 6's (ap-3d), and `V` the decoder's.
- **Cost:** `splitAtoms` and `splitMap` are recomputed per call. No route runs them yet; ap-3d measures them on the
  route (FOLLOW-UPS).

## 7. Next items

1. **ap-3cb** (ready; Lean only): restore `splitMap_exact` and `elaborate_parts` with their lemmas from `wip/ap-3cb`
   (`6217fa5c1`; they prove against this item's definitions unchanged), then run `lean_statements.py`,
   `audit.py --write` and `regen_generated.py --write`. About 230 proof lines, trust +0. WG-2 and SC-4 can read the
   map from this item; ap-3cb proves it exact.
2. **ap-3d** (after ap-2c and ap-3cb; a release, after AP-7): `authorLimits`, `checkAuthorN_split` and step 6 (E13 to
   E15); `elaborate_identity`, `elaborate_faithful` (`Faithful.lean`); `checkAct`, `decodeElaboratedU` (E5j); the
   `acts-elaborate` relay and 6.5's reference-table test.

## 8. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer; no mode, route or row is added.
2. PASS: section 2 lists every row the task names, with its file or the item it is cut to (ap-3cb for size, ap-3d for
   `read`, the decoder and `authorLimits`). The diff has no Python or Rust product change, no report test and no
   authority switch. Overlap is in section 5.
3. PASS: [mutants.json](mutants.json) (39 seeded bugs killed, at least one per new definition, theorems cut);
   [trust-mutants.json](trust-mutants.json) (0 survivor, 0 unknown; every allowance with its reason in
   [trust-mutants-allow.json](trust-mutants-allow.json)).
4. N.A.: no Python or Rust path elaborates; no existing input changes behaviour.
5. N.A.: no Lean answer is read by Python.
6. PASS: no gate evidence is claimed. The selected run is on `50b48a693`, the final code (only this report follows).
   The commit list below is from `main..HEAD --no-merges`, and the base is `git merge-base` (`2b13707e7`).
7. PASS: DELTA row 1 cites R16 and meets it: per file, `trust_map.py --check` on the final code, every new trusted
   definition killed by a named fixture, and the FOLLOW-UPS row. No reserved signature.
8. PASS: there is no user-visible change, and DELTA says why it has only the trust row.
9. PASS: `select_tests.py --base 2b13707e7` selects 76 of 471 units, including `lake build`, which builds
   `VE.Acts.ElaborateExamples`, the target every seeded bug breaks. The earlier run's failure of
   `tests/test_lean_limits.py` is a seeded-change check that the selection held.
10. PASS: the four theorems are about `elaborateMap`'s and `elaborate`'s returned values. Each seeded bug breaks a
    fixture with the theorems cut. Statements equal draft 2 (`check_statements.py`).
11. PASS: the only limit is D-26's 64 bytes, read from `VE.Limits.maxIdentifierBytes`
    (`tests/test_lean_limits.py`), tested at 64 and 65 (E8). Steps 5 and 7 reuse `validate` and `WellFormedU`. The
    elaboration is total and has no budget.
12. N.A.: no route runs it (section 6, cost).
13. PASS: no test is removed or renamed. `gate_collection.py --check --prebuilt` reports 0 refused, 0 stale and
    0 malformed.

## 9. Commits (`main..HEAD --no-merges`)

- this report (the last commit)
- `50b48a693` ap-3c evidence: trust_mutants on the final Lean (ve-mac-1, eca8a51bf): 271 killed, 0 survivor, 0 unknown, 54 invalid, 68 allowed
- `eca8a51bf` ap-3c: the part name's byte limit reads VE.Limits.maxIdentifierBytes (tests/test_lean_limits.py); R16 allowance re-recorded S +71, V +76
- `39dc7475e` ap-3c: DELTA (R16 row) and the statement check against draft 2
- `397a4fd32` ap-3c: R16 allowance S +71, V +75 (Elaborate.lean), K +0
- `e18350f7a` ap-3c evidence: trust_mutants on 5a28f9c5 (273 killed, 0 survivor, 0 unknown); seeded bugs 39 killed
- `5a28f9c5c` ap-3c: fixtures at each position of each list a check reads; trust_mutants allow file; two more seeded bugs
- `65fb6cff1` ap-3c evidence: seeded bugs (37 killed with the theorems cut); fixtures for the order of the steps
- `e7ce2579c` ap-3c: regenerate the inventories after the cut
- `c964f4564` ap-3c: cut splitMap_exact and elaborate_parts with their lemmas to ap-3cb (size rule)
- `a59001434` ap-3c: trust classes, regenerated inventories; readingOf reads the dual once per predicate
- `7ffb8757a` ap-3c: elaboration and the split map, and fixtures E1-E10, E16 on both sides of each check
