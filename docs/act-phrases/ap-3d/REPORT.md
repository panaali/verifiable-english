# ap-3d build report: the act check, step 6 and the decoder after AP-3 (part 4 of AP-3; Lean only)

**Status:** deliverable (1) is built: the Lean core. It is merged with main (`e8ea6a70d`), and the selected tests pass
on `e53527e7c`. **No DRI signature is reserved.** Trust is K +0, S −2, V +104 (trusted +102), signed by standing
ruling R16 ([DELTA.md](DELTA.md) row 1). **Cut by the size and safety rule:** the hook, the entry points and the
`readings_lexical_only` refusal move to **ap-3db**. The relay, Python and the route tests move to **ap-3dc**
(section 6). No route changes; pilot bytes expected to move: 0 B.

Plan: section 4, "AP-3. Joined acts", of the edited plan at `80f056f9e`, read with `git -C … show`. Main's
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) is an earlier draft: `diff` shows 80 lines, in the hours table and
synthesis round 2's AP-3 text. Where the two differ, `80f056f9e` wins. No plan file is copied, because main has one.
Spec: [act-phrases.md](../../spec/act-phrases.md) 6.3, 6.4, 6.6 and 10 (D-15 to D-18), and 11.3 (E13 to E15, A6, A7,
A14). Since `70da2be4d` it has changed only at lines 832, 1640 and 1667, outside those sections (ap-2bb's D9 (i)).
Read first: ap-3c's REPORT (its **ap-3d** rows) and ap-3b's REPORT section 7.
**Synthesis round 2:** this item implements none of its edits. DEC 16 (u0218.s18 unsplit) is untouched, because no
route elaborates yet; ap-3dc's regression document carries it.

## 1. Statement gate

The plan's statement review accepted AP-3's statements (ap-3, ap-3b and ap-3c were built on them). Every theorem
this item proves equals the spec's text after whitespace normalisation:
`python3 docs/act-phrases/ap-3d/check_statements.py` prints 7 EQUAL (`checkAuthorN_split`, `checkAct_lexical`,
`checkAct_joined`, `decodeElaboratedU_source`, `decodeElaboratedU_wellFormed`, `decodeElaboratedU_lexical`,
`elaborate_identity`). No approved statement changed, and none needed to.

## 2. Plan rows delivered

| Row (task order) | Status | Where |
|---|---|---|
| (1) `decodeElaboratedU`, `ElaboratedU` (`Decode.lean`, 6.4) | **done** | `lean/VE/Acts/Decode.lean`: `actsOf`, `elaborateSource`, `decodeElaboratedU` |
| (1) `checkAct`, `meaningTexts` (D-15; also D-16, D-17 and D-18) | **done** | `lean/VE/Acts/Wire.lean` (`joinedAct`, `checkAct`); `Table.lean` (`meaningTexts`) |
| (1) `checkAuthorN` through `authorLimits`, `checkAuthorN_split` | **done** | `lean/VE/NormDefaults/Wire.lean` (`reservedNamesOk`, `authorLimits`) |
| (1) step 6 (E13 to E15) | **done** | `elaborateMap`: `authorLimits (declaredAfter D sa M) U'`, after `validate` and before the backstop |
| (1) `elaborate_identity`, `decodeElaboratedU_source`/`_wellFormed`/`_lexical`, `checkAct_lexical`, `checkAct_joined` | **done**, proved and audited | `Elaborate.lean`, `Decode.lean`, `Wire.lean` |
| (1) `elaborate_faithful` with `readAs` and `IntendedActs` (`Faithful.lean`) | **ap-3db** (size): a semantic proof over `holdsCatala` and `forget`, of the order of ap-3cb's 230 lines | — |
| (1) the hook in `Norms/Wire.lean` | **ap-3db** (safety, section 6) | — |
| (1) `readings_lexical_only` (`Readings/Wire.lean`) | **ap-3db**: with the hook unchanged, the readings route still refuses every joined act through `Lexical.check`. ap-1bg holds `lean/VE/Readings/` | — |
| (2) every `acts@0` entry point calls `decodeElaboratedU`, with twin theorems | **ap-3db** | — |
| (3) the `acts-elaborate` relay (shape, encoder theorem, schema, binding, `split`, fuzz, `_lean_route`) | **ap-3dc** | — |
| (4) A6, A7, A14 with its residual | **done in Lean, from the act text** (`checkAct`, `actsOf`, `elaborateMap`); through the route: **ap-3dc** | `DecodeExamples.lean` |
| (4) precedence split pairwise | **done in Lean** (A6 with a rule `over` the source); route: ap-3dc | `DecodeExamples.lean`; ap-3c's E4 |
| (4) differing act lists refused (D-24) | ap-3c's E7 fixtures (unchanged, still passing); through the route: ap-3dc | `ElaborateExamples.lean` |
| (4) byte-identity of all-simple documents (`decodeElaboratedU_lexical`) | **done**: the theorem, and wire fixtures with and without `acts@0` | `Decode.lean`, `DecodeExamples.lean` |
| (4) `test_reference_table_complete` | **ap-3dc** (it tests the relay's reference table) | — |
| (4) `splitAtoms`/`splitMap` computed once and charged against the stated limit | **done** (section 6.3) | `elaborateMap`, `splitsOf`; `DecodeExamples.lean` `big` |
| Seeded bugs (plan): *must* distributes over *or* (T8) | already planted by ap-3b (`must-not-as-must`, T8). The Python display bug needs the relay: ap-3dc | — |

## 3. Fixtures (`lean/VE/Acts/DecodeExamples.lean`, each check on both sides)

- **`checkAct`.**
  - A lexical act passes through normalised, with no tree.
  - A6, A7 and A14 are read from their text into G6, G7 and G14v. A7's act is one atom: "by" is not a split marker.
  - A14's residual (the sixth act, *false*) is refused with D-3.
  - D-15 gives G5d's exact text. The spec marked it "hand, not yet run"; it now runs and matches.
  - D-16 is refused with no frames. D-17 is refused at L7, while L5 and L6 are not limits. D-18 is refused at the
    start, the middle and the end, and after letters.
  - D-6 and a wrong slot keep `Lexical.check`'s texts. A comma outside a fixed phrase also goes to the grammar.
- **The pilot units from their text** (`actsOf`, then `elaborateMap`).
  - A6 gives two prohibitions, and a rule over the source splits pairwise.
  - A7 stays one obligation, unchanged.
  - A14 gives five prohibitions.
  - `actsOf` checks each act at its predicate's arity, and raises the first refusal in order.
- **Step 6.**
  - E13 (255 and 256 declared predicates) is pinned, and two split sources count each source once and each part
    once.
  - E14 (53 and 54 bytes) and E15 (252 and 253 extra rules) are pinned.
  - The order holds: step 5 before step 6, and step 6 before step 7.
- **The spec's `splitAtoms` and `partNames`** are pinned on the first and the last entry of `acts`.
- **A request at the limits:** 32 sources and 128 rules become 64 parts and 256 part rules, all accepted (section
  6.3).
- **`decodeElaboratedU` over the wire.**
  - All-lexical `acts@0` documents, with and without `norm-defaults@0`, give the source itself, an empty map, the
    block's fixed phrases and the declared count.
  - Without `acts@0` no act is read (a *nor* act).
  - A joined act is still refused by the norms decoder with D-4.

## 4. Seeded bugs and mutants (Lean only, plus one test table; no Python or Rust product code changed)

[`seed_bugs.py`](seed_bugs.py) plants each bug and cuts the theorem sections of `Wire.lean`, `Elaborate.lean` and
`Decode.lean`, so a fixture must fail and not only a proof. It then builds the fixtures and restores the files. It
refuses to run when a new or changed definition has no bug.

- Command: `uv run python docs/act-phrases/ap-3d/seed_bugs.py`, exit 0, on `f7abfd968`. Its product files are
  byte-identical to the final HEAD's, and the merge changed none of them.
- Result in [`mutants.json`](mutants.json): **all 22 KILLED**, and the restored build exits 0.

| File | Definition: bug (the fixture file that fails) |
|---|---|
| `lean/VE/Acts/Wire.lean` | `joinedAct`: slot check off, first meaning only, limit as `InvalidInput` (DecodeExamples); `checkAct`: joined refused, a tree on a lexical act (DecodeExamples) |
| `lean/VE/Acts/Lexical.lean` | `checkWith`: D-6's text; `joinCheck`: D-4's text (LexicalExamples) |
| `lean/VE/Acts/Table.lean` | `meaningTexts`: subject kept (DecodeExamples, G5d) |
| `lean/VE/Acts/Elaborate.lean` | `atomsOf`: one atom splits; `splitsOf`: no split; `partNamesIn`: unsplit dropped (ElaborateExamples); `declaredAfter`: parts not counted, sources not counted; `elaborateMap`: step 6 skipped, steps 5 and 6 swapped (DecodeExamples) |
| `lean/VE/NormDefaults/Wire.lean` | `authorLimits`: 57 bytes, rules without the unspecified names (DecodeExamples, E14, E15) |
| `lean/VE/Acts/Decode.lean` | `actsOf`: trees dropped; `elaborateSource`: acts read without `acts@0`, declared 0, fixed empty; `decodeElaboratedU`: the norms dropped (DecodeExamples) |

**trust_mutants** (`mac-pytest.sh --trustmut -- --max-mutants 1000 --allow … --rescore … --json …`; full run on
the merged HEAD `a838ea643`, cloud pool):

- 19 definitions, 260 mutants: **162 KILLED, 0 SURVIVOR, 0 UNKNOWN, 54 INVALID, 44 ALLOWED, 0 NOT RUN**
  ([`trust-mutants.json`](trust-mutants.json)).
- The first run had 18 survivors. Three groups were real gaps, now with fixtures: `splitAtoms` and `partNames` were
  read only by theorems, and the slot check was pinned on a middle word only. Its UNKNOWNs did not elaborate. A later
  run found `actsOf`'s arity unpinned (M063, M162), now fixed.
- [`trust-mutants-allow.json`](trust-mutants-allow.json) gives one reason per entry:
  - **Six equivalent mutants.** Five read `elaborateSource`'s profile list differently. They stay equivalent until
    ap-3db, because every act the current hook admits is lexical. The sixth drops the first token in `joinedAct`,
    which is always the subject slot.
  - **Mutants that do not elaborate** (type errors, a list operator on a match pattern).
  - **`splitReg`'s whole body cut to `[]`.** It fails ElaborateExamples' E1 guard, a kill the tool cannot certify.

## 5. Trust, size, tests and checks

- **Trust:** `uv run python tools/trust_map.py --check` on the final tree prints `PASS`, against `e8ea6a70dc63`:
  K +0, S −2, D +71, G +22, tied −15, trusted +102.
  - Per file: `Decode.lean` +35, `Wire.lean` +26, `Lexical.lean` +25, `Elaborate.lean` +16.
  - `Lexical.lean`'s +25 is `check`'s body, moved into `checkWith` and `joinCheck`. Their tie through `check_spec`
    names `check` only.
  - Recorded with `--allow` (V +104) and signed by R16. FOLLOW-UPS "## ap-3d" asks for the ties pass.
- **Size:** `git diff --numstat` against the merge base, hand-written lines, added plus deleted.
  - Lean product: 435 lines. `Elaborate.lean` 207 (`elaborate_identity` and its lemmas are about 80), `Wire.lean`
    95, `Decode.lean` 84, `NormDefaults/Wire.lean` 22, `Lexical.lean` 16 (+2 proof lines), `Table.lean` 4,
    `lean/VE.lean` 3.
  - Fixtures: `DecodeExamples.lean`, 155 lines.
  - Tables: `trust-classes.json` 49, `ve/assurance-manifest.json` 57, `tests/test_acts_lexical_mutants.py` 6.
  - Evidence and docs: `seed_bugs.py` 116, `check_statements.py` 47, the allow file 104 (written by a script), DELTA
    33, and this report.
  - Total: about 1,000 lines without this report, over the ~600 guideline. The cut already moved parts (2) to (4),
    and what remains is the definitions the task names first, their theorems, the fixtures R16 requires and the
    evidence.
- **Builds and checks on the merged tree:**
  - `regen_generated.py --write --skip route-cases` wrote 33 entries, and `--check --skip route-cases` checked 33
    entries. `route-cases` needs the Rust binary this worktree does not build; no route changed.
  - `lake build` passes (1,172 jobs).
  - `python3 lean/audit.py` prints PASS (686 files, 7,646 theorems).
  - `python3 tools/check_lean_imports.py` prints "Lean layer graph kept".
  - `uv run pytest -q tests/test_assurance_manifest.py`: 138 passed.
  - `gate_collection.py --check --prebuilt`: 30,654 collected, 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Selected tests:** `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`.
  - The first run, before the merge, stopped at `tools/check_lean_imports.py`: the new outward import
    `VE.Acts.DecodeExamples -> VE.Service.ActsExamples`. The fixtures now build their own JSON.
  - The second run (`2392f002`) failed 2 tests of `tests/test_acts_lexical_mutants.py`: the sweep's `SCOPE` named
    `check`, whose body moved. It now reads `checkWith` and `joinCheck` under `check`'s mutant names. Its 73
    generated ids equal main's, compared by script. Rerunning the file: 84 passed.
  - The final run on `e53527e7c` (merged, clean) covered 466 of 507 units, with exit 0 and 0 failed ids. Log:
    `/tmp/ap3d-sel3.log`, summary line "exit=0; failed/error ids=0".
  - The only later commit `96861ee4f` restores main's key order in `trust-classes.json` and
    `ve/assurance-manifest.json`, with identical content. After it, `tests/test_assurance_manifest.py` gives 138
    passed and `trust_map.py --check` passes.
  - No test in `main-known-red.txt` was hit.
- **Not run:** the full gate (the chain runs it on the final HEAD), AP-7, any pilot.

## 6. Deviations and choices

1. **Why the hook is not switched here.**
   - With `Norms/Wire.lean`'s hook on `checkAct`, every caller of `decodeSourceU` and `Norms.Wire.decodeSource`
     would admit joined acts. That is about 15 files: the norms and norm-defaults routes, `Service/Document`,
     English, the readings route and the wire-contract hooks.
   - Every caller that does not yet run on `decodeElaboratedU` would then read a joined act as one opaque
     predicate: "must not torture or ill-treat" as one prohibition instead of the table's two. That widens what is
     accepted, with a meaning the plan refuses (D2, D3).
   - `decodeElaboratedU_source` requires `decodeSourceU` itself to accept them, so no single guard can sit between
     the two. A parameter on `decodeSourceU` would change an approved statement.
   - So the hook, the entry points with their twins and `readings_lexical_only` go together, as ap-3db.
   - Until then `elaborateSource` reads no frames (`V := ⟨[], []⟩`): the `acts` block's `frames` field is refused
     as unknown, as the spec's 3.1 requires until its batch lands. Every decoded document has `D.acts = []`.
2. **`Lexical.check` factored.** `checkAct` needs 1.3's conditions 1 to 5 without condition 6. The first version
   dispatched on `check`'s D-4 and D-5 texts. That was replaced before review: matching text is fragile, and the
   checklist forbids it.
   - `check` is now `checkWith (joinCheck name)`: the same body, split at condition 6.
   - `checkAct` runs `checkWith` with a last step that returns the tokens. One owner, and no text is read.
   - The AP-1 proofs (`check_iff`, `check_no_join`, `check_extends`) needed only their `unfold` line.
     `tests/test_acts_lexical_mutants.py` reads the two parts.
3. **Computed once, and the limit.**
   - `elaborateMap` reads each act once, in step 1 (`D.acts.mapM readingOf`). `splitsOf` keeps those readings'
     atoms, and every later step looks the split up (`sa`, one `SplitMap` `M`). In ap-3c, `splitAtoms` re-read the
     rules for every reference.
   - The spec-level `splitAtoms D`, `splitMap` and `partNames D` keep their statements. `splits_eq` proves the
     table equal to `splitAtoms D`, so `elaborateMap_ok` and ap-3c's theorems still hold.
   - The charge: each act's listing stops at `maxReadings` (64) and the step budget (`checkAct`, D-17). Elaboration
     is bounded by the decoded source's limits: 64 regulated predicates and 256 rules, from `decodeSource`'s
     `validate`.
   - The fixture `big` runs at those limits and ends within them. Speed is not measured in the suite.
   - ap-3cb's wip proofs must pass the new arguments (FOLLOW-UPS "## ap-3d"); their statements are unchanged.
4. **Without `acts@0`, `elaborateSource` reads no act.** Today's act check admits *nor*, which `checkAct` would send
   to the grammar. A fixture pins this.
5. **Assurance manifest.** `NormDefaults/Wire.lean` and `Lexical.lean` were re-pinned after their ranges were
   reviewed, with the new declarations listed. `Acts/Wire.lean` and `Acts/Decode.lean` are pinned whole, and
   `DecodeExamples.lean` is classified as fixtures.

## 7. Pilot bytes and next items

- **Pilot bytes expected to move:** 0 B (*estimate*). No route reads the elaboration until ap-3db, and no relay
  until ap-3dc. u079b's 76 B (A7) and the AP-3 rows of u027 and u0123.s03 wait for those two.
- **ap-3db (Lean):**
  - the hook calls `checkAct`, and the `acts` block's `frames` and `adverbs` are decoded by `decodeVocab`
    (`checkVocab`, D-31);
  - `readings_lexical_only` (D-33);
  - every `acts@0` entry point of spec 6.4 classified and on `decodeElaboratedU`, each reached soundness theorem
    with its twin;
  - `elaborate_faithful` with `readAs` and `IntendedActs` (`Faithful.lean`), and E5j.
- **ap-3dc (relay):** the `acts-elaborate` row (shape, `runElaborate_fits`, schema, binding through `SplitMap`,
  `split` with D-28), its fuzz tests, `ve/norms.py` `_lean_route` for `acts@0` with the Python path refusing,
  `test_reference_table_complete`, A6, A7 and A14 through the route, the Python display seeded bug, and u0218.s18's
  regression document (DEC 16).
- **Then:** ap-4 and AP-7's experiment.

## 8. Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer; no mode, route or row is added (ap-3dc).
2. PASS: section 2 lists every task row with its file or the item it moves to. The diff has no Python product
   change, no report test and no authority switch. Overlap: ap-2bb (`Linearize.lean`, `GrammarExamples.lean`) is
   not edited, only imported, and is merged. `lean/VE/Readings/` (ap-1bg) is not edited.
3. PASS: [mutants.json](mutants.json) (22 seeded bugs, all KILLED by a fixture with the theorems cut);
   [trust-mutants.json](trust-mutants.json) (0 survivor, 0 unknown; the allow file gives a reason per entry).
4. PASS: no existing input changes behaviour. `check_iff`/`check_spec` still prove `check` equal to `Accepts`, and
   LexicalExamples' fixtures pass. The wire fixtures compare `e.U'` with `e.s.U`
   (`DecodeExamples.lean` `dec`).
5. N.A.: Python reads no new Lean answer.
6. PASS: merged with main (`e8ea6a70d`). The selected run was on the merged `e53527e7c`, and the one later commit is
   named in section 5. The commit list is from `main..HEAD --no-merges`; the base is `git merge-base`.
7. PASS: DELTA row 1 cites R16 and meets it: itemised per file, `trust_map.py --check` on the final tree, every new
   trusted definition killed by a named fixture, and the FOLLOW-UPS row. No reserved signature;
   `review-ready.py --delta-dri-needed` prints "No DELTA row reserved for the DRI".
8. PASS: no user-visible change, and DELTA says why (the hook is unchanged; `DecodeExamples.lean`'s last guard pins
   D-4).
9. PASS: `select_tests.py --base e8ea6a70d` selected 466 of 507 units. They include `lake build`, which builds the
   fixtures every seeded bug breaks, and `tests/test_acts_lexical_mutants.py`, which caught the moved body. That is
   a seeded change the selection held.
10. PASS: each theorem is about the returned value (`checkAct`'s, `decodeElaboratedU`'s `e`, `elaborate`'s), and
    `check_statements.py` prints 7 EQUAL. With the theorems cut, each seeded bug still breaks a fixture. No
    hypothesis was added.
11. PASS: step 6's limits are read from `authorLimits`, the route's own, at each boundary (E13 to E15).
    `checkAct`'s limit is D-17 (L7). Elaboration is total. No deadline is added.
12. PASS: each act is read once (`splitsOf`) instead of once per reference. The fixture `big` runs at the route's
    limits. No route runs it yet, so there is no pilot timing.
13. PASS: no test removed or renamed. The sweep's 73 ids equal main's, and `gate_collection.py --check --prebuilt`
    reports 0 removed, 0 stale and 0 malformed.
14. PASS: both directions for every check (section 3). Each claim here names its command and output. The spec was
    re-read for each statement (6.3, 6.4, 6.6), each text (D-15 to D-18) and each fixture (E13 to E15, A6, A7,
    A14).

## 9. Commits (`main..HEAD --no-merges`)

- this report (the last commit)
- `96861ee4f` ap-3d: trust-classes.json and the assurance manifest keep main's key order (the merge had moved blocks); only this item's entries differ
- `e53527e7c` ap-3d evidence: trust_mutants on the merged HEAD (a838ea643, full run): 162 killed, 0 survivor, 0 unknown, 54 invalid, 44 allowed
- `a838ea643` ap-3d: previous trust_mutants JSON kept for the rescore
- `fe2d4a49a` ap-3d: regenerated inventories after the main merge
- `d9697cdfe` test_acts_lexical_mutants: the sweep reads check's two parts (checkWith, joinCheck) under check's mutant names; the 73 generated ids are main's
- `2392f0027` ap-3d evidence: trust_mutants on the final Lean (f7abfd968, rescored in checks mode): 162 killed, 0 survivor, 0 unknown, 54 invalid, 44 allowed
- `f7abfd968` ap-3d: fixture for actsOf's arity (trust_mutants survivors M063, M162)
- `1008e8983` ap-3d evidence: seeded bugs on the final code (22 killed); previous trust_mutants JSON kept for the rescore
- `63fe50bb6` ap-3d: assurance manifest: NormDefaults/Wire.lean and Lexical.lean re-pinned after review of their ranges; Acts/Wire.lean and Acts/Decode.lean pinned whole; DecodeExamples.lean classified as fixtures
- `e2d4ab32e` ap-3d: the wire fixtures build their own JSON (no outward import of VE.Service: tools/check_lean_imports.py)
- `f45fc5327` ap-3d: DELTA (R16 row) and the statement check
- `862317c1c` ap-3d evidence: trust_mutants on the final Lean (full run, 40d31bcae): 162 killed, 0 survivor, 0 unknown, 54 invalid, 44 allowed
- `40d31bcae` ap-3d: second trust_mutants run kept as trust-mutants-run2.json
- `1a50250b5` ap-3d: the theorems' statements equal the spec's text (check_statements.py: 7 EQUAL); regenerated inventories
- `54e038fd0` ap-3d evidence: trust_mutants on the final Lean (rescored, checks mode; cloud): 162 killed, 0 survivor, 0 unknown, 54 invalid, 44 allowed
- `78af74cf6` ap-3d: declarations.txt after the fixture edit
- `db07cd058` ap-3d: allow reason for splitReg's body; first trust_mutants run kept as trust-mutants-run1.json
- `839492579` ap-3d: fixtures for trust_mutants' survivors (splitAtoms and partNames on every entry, a slot joined at the end or after letters); allow file (equivalent and non-elaborating mutants)
- `aca5e510b` ap-3d: R16 allowance V +104 (K +0, S -2; trusted +102)
- `fdd5de9cd` ap-3d: regenerated inventories after the check factoring
- `5bfae5c8c` ap-3d evidence: seeded bugs (22, each new or changed definition, all killed by a fixture with the theorems cut)
- `7df79eec5` ap-3d: seed_bugs.py: declaredAfter's text
- `842e924c5` ap-3d: Lexical.check factored into checkWith (conditions 1-5) and joinCheck (condition 6); checkAct reads checkWith, no error text; trust classes; seeded-bug script
- `e536189c8` ap-3d: checkAct and meaningTexts (D-15 to D-18), authorLimits and checkAuthorN_split, step 6 with the splits read once, elaborate_identity, decodeElaboratedU and its theorems, fixtures
