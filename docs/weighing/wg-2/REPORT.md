# wg-2 REPORT: weighing's block, strength, conditions and grants (Lean)

**Stops for the DRI (L52): `strength_iff`'s approved statement is false off the decoder, and changing it needs the
DRI's signature** (DELTA.md row 4, section 3). Fix round for review F1, F-ready1 and F3 (F2 in section 6): 22 of
weighing.md 5.1-5.4's 23 theorems are proved as written, with `strictWitness` and its chains (f6e03a5df); seeded bugs
W1-W8 (Lean) and P1 (`tools/layer_policy.py`) are each killed (3653b4f65). Open, blocking nothing: the
`VE.Weighing.*` layer row (`manage-agents/inbox/dri/20261104T025807Z-wg-2-3977838.md`); wg-2b keeps 7.2/7.3's fixtures.

Plan: docs/spec/weighing-PLAN.md "WG-2" (lines 1226-1245) and the batch row (line 1104). Spec: docs/spec/weighing.md
sections 1 and 5. Both files are copied verbatim from 19c1eb676. The statement gate passed (WG-1's gate at 1ae4b7402;
wg-rev changed no WG-2 statement). Base: c3d9ea938. Commits: `git log --oneline main..HEAD --no-merges`, c49030526
to the HEAD.

## 1. Plan rows delivered

| Row (task "Deliver") | Delivered | Commit | Evidence |
|---|---|---|---|
| (1) `Tree.lean`: `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `rankOrder`, `strictPair`, `targetF`, `targetSorts` | yes, verbatim from weighing.md 1.1-1.3 (the stub's text). A script compared every definition with the stub's: all equal | bff4a560b | `Examples.lean` guards; mutants.json |
| (1) `strictWitness` (with `chainEdges`, `RankChain`, `chainsFrom`, `chainLt`) | yes, verbatim from the stub; no trusted line (tied, C, G[I]: section 5) | f6e03a5df | W-β's witness rows, the shortest/least pair (`Examples.lean`); W1-W5 |
| (1) `strictPair` through QS-1's `VE.Closure`, proved equal to soft's `outranksPlus` | yes: `rankOrder_above` (soft's `outranksPlus` is QS-1's `above`, by `VE.Closure.outranksPlus_eq_above`). No rank closure of its own | 74bfbe9a8 | `strictPair_outranks`, `_down`, `_up` |
| (2) `Conditions.lean`: `strengthPremises`, `condPremise`, `grantConds`, `weighLabelled`, `weighPremises`, `propImplies`, `checkWeigh`, `WellFormedWeigh` | yes, verbatim from weighing.md 1.4-1.6. A grant premise is `condPremise`'s necessary `.off` case (`grantEntries`) | bff4a560b | guards; mutants.json; trust-mutants.json |
| (2) theorems of weighing.md 5.1-5.4 | **22 of 23** proved, statements as written (the first round counted 22 and missed `factors_inert`, review F1). The first round's 11 (`strictPair_outranks`, `strictPair_of_always`, `strictPair_down`, `strictPair_up`, `propImplies_sound`, `condition_necessary`, `condition_sufficient`, `grant_needed`, `delegation_bounded`, `weigh_conservative`, `wellFormedWeigh_empty`) and this round's 11 (`holistic_iff_no_always_chain`, `strictWitness_isSome`, `strictWitness_chain`, `always_dominates`, `always_no_override`, `all_always_is_strict`, `factors_inert`, `grant_within_grantor`, `weighPremises_wellFormed`, `weighPremises_substructure`, `weigh_alone_base_free`). **`strength_iff` is not proved: as approved it is false** (section 3; DELTA.md row 4) | 74bfbe9a8, 03d7e78a2, f6e03a5df | `python3 lean/audit.py`: "PASS: 759 source files; 8487 named theorem declarations audited …; only the declared standard axiom allowlist" |
| (2) each theorem in `lean/VE/Audit.lean` | yes, through `regen_generated.py` (`lean-audit-manifests`), every new theorem and lemma included | 1fe968ba3, f6e03a5df | `lean/axioms.txt` (propext, Quot.sound, Classical.choice only) |
| (3) `Examples.lean`: W-α to W-θ, W-κ, W-λ, W-μ | **part**: W-α (with a strict-flag twin), W-ε, W-λ's act text, W-μ in full (7.2's rows: accepted, labels, 4 of 256, the outcomes, the swapped refusal), θ19/θ20's 12/13-atom bound, plus W-α3 and a W-ζ3 chain so that every list has more than one entry. The other rows are wg-2b's | f61d43692, 0e9e5207f, f43e5900e, adfe58d0b | `lake build VE.Weighing.Examples` |
| (4) `lean/WEIGHING.md`: every definition and theorem in plain words | yes for everything delivered; wg-6a's zone text is kept, and WG-2's sections are added after it | 04442baec | the file |
| (4) `lean/VE.lean` import, frozen inventory, assurance manifest | the import, by hand (the `lean-roots` union). The frozen inventory needs no row: `regen_generated.py --write` left `frozen-sources.sha256` unchanged, since weighing is not frozen. The assurance manifest has `Weighing/Examples.lean` under `other_json` (fixtures that parse JSON) | f61d43692, d7c1dc7db | `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` passed |
| "Deleted, not duplicated": `excPremisesOf` as the `.excepted` instance of one generator | **not moved**, for the reason in section 3 | - | `lean_statements.py`: "removed: 0, changed: 0" |
| `lean_statements.py` shows additions only | yes | 1fe968ba3, adfe58d0b | output "removed: 0 / changed: 0"; `git diff main -- lean/statements.txt` has no `-` line |

## 2. Cut to wg-2b (fixtures only)

The task places the size cut after rows (1)-(2) and their proofs, and R16 does not authorize deferring a theorem
(review F1). So this fix round restores all of (1)-(2): the 11 theorems the first round cut and `factors_inert`, which
its follow-up list missed, with `strictWitness`, `chainEdges`, `chainsFrom`, `chainLt`, `RankChain`, `strictFlag`,
`SameBase` and `freeWitness`. The first round measured +154 with the chain definitions in
(04442baec); here they are classified as tied G[V], C, G[I] or P, so trust stays at +131 (section 5). `strength_iff` is
the one theorem not delivered, and not for size (section 3). What still moves to wg-2b, unchanged in the spec: the rest
of weighing.md 7.2 (W-γ, W-δ, W-ζ/ζ2, W-η, W-θ with θ11, W-κ's sixteen branches, the grant cycles, the `strength_iff`
regressions F9/F10/F13; W-β's witness rows are here) and 7.3's "exactly when" rows.

## 3. Deviations and answers to the task's questions

- **`strength_iff` is false as approved (the reason this item stops).** Its forward direction needs `outweighsName`
  to be injective on the query, and the spec's argument for that ("every such name starts with a letter
  (`validSoftName`, `Surface.identifier`)") holds for ranks (`checkSoftEnv`) but not for predicates: no part of
  `WellFormedSoft` or `checkWeigh` refuses a regulated predicate whose name starts with `_`; only the wire decoder does.
  Counterexample, in `Examples.lean` as `#guard`s: `cxW`, α's document with ranks `c`, `c_`, `l`, edge and `always`
  `(c_, l)`, plus a regulated plain `_x_permitted` over `assistant`. `WellFormedWeigh cxW` holds, `l` and `c` are
  declared ranks, `_x_permitted` is declared, and the premise at `(_x_permitted, l, c)` is in `Str_T`, because
  `outweighsName "_x_permitted" "l" "c" = outweighsName "x_permitted" "l" "c_"`. But that triple is no `outweighs`
  decision and `strictPair cxW "c" "l"` is false. The decoder refuses the name ("Invalid ASCII identifier:
  '_x_permitted'", also guarded), so no accepted wire document reaches it. The reverse direction holds for every
  triple (`strength_mem`). Changing the statement, or adding the hypothesis it needs, is never covered by a standing
  ruling, so DELTA.md row 4 reserves the DRI's signature. Two candidate fixes: a hypothesis that `a` begins with a
  letter, or a soft check (`checkSoft`) that refuses a regulated or defined name beginning with `_` (as the decoder
  already does). The theorem is not stated or proved in another form here.
- **Python (review F3).** The first round wrote "No Python … changes", but `tools/layer_policy.py` changes the layer
  of `VE.Weighing.{Tree,Conditions,Examples}` (2 lines). DELTA.md and the self-review now say so. The layering question
  stays open (next item). P1 seeds a bug in that file (section 4).
- **The stub's path.** `lean/SpecStubs_weighing.lean` at `lean/` fails `tools/check_lean_imports.py` ("unmapped Lean
  module: SpecStubs_weighing", "no default target builds"). The byte-identical copy is at
  `docs/spec/weighing/SpecStubs_weighing.lean` (`cmp` against 19c1eb676: identical), as pk-1 and sc-5r keep theirs
  under `docs/spec/`.
- **The layer row (open DRI question).** `WeighDoc` carries `VE.Acts.SplitMap`, and `targetCheck` calls
  `VE.Acts.splitRefusal`. Both live in `Acts/Elaborate.lean`, layer 3, so `check_lean_imports.py` refused
  "new outward Lean import: VE.Weighing.Tree -> VE.Acts.Elaborate". `tools/layer_policy.py` now puts
  `VE.Weighing.{Tree,Conditions,Examples}` at layer 3, and `Zone.lean` stays at 2. WG-3's provider line in the
  layer-2 `NormDefaults/Layered.lean` will need its own answer. Asked with msg.sh (inbox file above); there is no
  reply yet.
- **`splitRefusal`.** weighing.md 1.6 says that WG-2 factors AP's two inline texts into
  `VE.Acts.splitRefusal (role name)` in `Acts/Elaborate.lean`. Done with the same bytes: `refsOk` calls it, and
  `Acts/ElaborateExamples.lean`'s guards pass unchanged (`lake build` built it).
- **The guard decoder.** AT-3a's guard node is not on `main` (`lean/VE/Attitudes/` does not exist). `condPremise`
  takes `CondDecl.condition` as a formula, as the spec states it. The decoder that fills the field is WG-3's, and
  today it is W1's budgeted decoder (the plan's fallback, weighing.md 3.1).
- **One generator.** `excPremisesOf` is not literally an instance of `condPremise`: `condPremise` is stated over
  `Target`, which has no `.excepted` case (weighing.md 1.1, a fixed statement). Making both instances of a third,
  lower generator would add a definition to `SoftNorms/Soften.lean` and touch soft's proofs that unfold
  `excPremisesOf`, which grows an item already over its size line. So soft is unchanged (`lean_statements.py`:
  removed 0, changed 0), and R6 does not apply.
- **Names.** No name clashes with `Zone.lean`, which is unchanged. `RankChain` (a Prop that only wg-2b's statements
  use) moved with them.
- **The rulings built as written.** OPEN-5: W-λ refuses the act target with AP's text (the guard at
  `Examples.lean:74`). No split-part target is designed. WG-R1 and WG-R2 move no WG-2 fixture.

## 4. Seeded bugs and mutants

The plan's three seeded bugs, each failing W-μ (my runner, `/tmp`, records the first failing check;
[mutants.json](mutants.json)):

| Bug | File | Failing check |
|---|---|---|
| S1: `(targetSorts _).reverse` without `.reverse` in `checkWeigh` | lean/VE/Weighing/Conditions.lean | `Examples.lean:146` `#guard verdict wμ == "accepted" && …` |
| S2: `tupleVal vs` as `vs` (in W-μ's `outcome`) | lean/VE/Weighing/Examples.lean | `Examples.lean:150` W-μ's outcome at `(a1, u2)` |
| S3: `atom`'s `.binary p (var 1) (var 0)` swapped (in `targetF`'s switch atom) | lean/VE/Weighing/Tree.lean | `Examples.lean:149` W-μ's 4 of 256 |

S2 and S3 are planted where weighing reads the argument order. The same swap in `Norms/Basic.lean`'s `tupleVal` or
`atom` breaks W1's own proofs (`bindAll_denote_nil`, `atom_denote`) before W-μ is built.

Fix round (my runner `/tmp/wg2/mut/run.py`: apply, `lake build VE.Weighing.Examples`, record the first error,
restore; [mutants.json](mutants.json) W1-W8, P1):

| Bug | File | Failing check |
|---|---|---|
| W1: `chainLt` without the list-order tie-break | lean/VE/Weighing/Tree.lean | `Examples.lean:187` `#guard verdict wTie == "accepted" && …` (picks `[a, c, d]`) |
| W2: `chainLt` without the length comparison | lean/VE/Weighing/Tree.lean | `Examples.lean:185` `#guard verdict wShort == "accepted" && …` (picks `[a, b, c, d]`) |
| W3: `strictWitness` filters with `all` for `any` | lean/VE/Weighing/Tree.lean | `Conditions.lean:641`, `strictWitness_chain`'s proof |
| W4: `strictWitness`'s fuel `ranks.length - 2` | lean/VE/Weighing/Tree.lean | `Conditions.lean:662`, `strictWitness_isSome`'s proof (omega) |
| W5: `chainsFrom` stops after one step | lean/VE/Weighing/Tree.lean | `Conditions.lean:477`, `chainsFrom_chain`'s proof |
| W6: `strictFlag` sets `holistic` | lean/VE/Weighing/Conditions.lean | `Conditions.lean:1086`, `all_always_is_strict`'s proof |
| W7: `freeWitness` turns every switch on | lean/VE/Weighing/Conditions.lean | `Conditions.lean:1530`, `weigh_alone_base_free`'s proof |
| W8: `SameBase` without `p ∉ decisionNames` | lean/VE/Weighing/Conditions.lean | `Conditions.lean:1539`, `weigh_alone_base_free`'s proof |
| P1: `lean_layer` puts `VE.Weighing.*` at layer 2 | tools/layer_policy.py | `python3 tools/check_lean_imports.py` exit 1: "new outward Lean import: VE.Weighing.Tree -> VE.Acts.Elaborate" and "… VE.Weighing.Conditions -> VE.EnglishGrammar.Rules" (select_tests runs it for a changed `layer_policy.py`) |

Each was restored, and the file is byte-identical to the commit (`git diff --quiet`).

The first round: there is one hand mutant per new definition, 38 in all, each killed by a `#guard`. The run cut
`Conditions.lean`'s theorems, so a broken proof kills none: [mutants.json](mutants.json), with file, definition,
mutant, test and check. `splitRefusal`'s mutant fails `Acts/ElaborateExamples.lean:150`.

Trust mutants (build checklist 13a): `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/weighing/wg-2/trust-mutants-allow.json --rescore docs/weighing/wg-2/trust-mutants.json --json
docs/weighing/wg-2/trust-mutants.json` exited 0: in a full run on adfe58d0b (tree e4ded25a23ae), and in a `--rescore` of it on ee34862a0 (tree 8cf7a935c74c; only the allow file's line reference changed), which the JSON records:
231 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 23 ALLOWED ([trust-mutants.json](trust-mutants.json)). Each allow has
one line of reason ([trust-mutants-allow.json](trust-mutants-allow.json)). Most allowed mutants do not elaborate
(`[]` loses the next projection's type, or a dropped `Target` constructor), and grantConds' list-first and list-last
on the grantor's own grants are equivalent, because `DuplicateDeclaration: grant` refuses a second grant with the
same rule and party. The first run found 65 SURVIVOR and 21 UNKNOWN; W-α3, W-ζ3 and the direct guards kill all of
them except those allowed.

## 5. Trust

`uv run python tools/trust_map.py --check`: "against c3d9ea9380cb: K +0, S +132, … trusted +131", "PASS: K, S and
untied [V] within c3d9ea9380cb and the allowances introduced since". Per file: `Tree.lean` +68 S, `Conditions.lean`
+64 S, `Acts/Elaborate.lean` -1. This is recorded with `trust_map.py --allow … --signed "SIGNED by standing ruling R16
(DRI-RULINGS.md), wg-2, 2026-10-18"`, and the FOLLOW-UPS.md row is under "## wg-2". The classes in
`tools/trust-classes.json` follow soft's own: premises and types S, checks C (`checkWeigh`, `targetCheck`,
`propImplies` and its helpers), limits and warnings G[R], labels, paths and keys G[I], fixtures T. `rankOrder`,
`strictPair`, `WeighEnv.empty`, `weighPremises` and `WellFormedWeigh` are tied to the theorems that state them.
[DELTA.md](DELTA.md) has the one R16 row per file. Fix round, on f6e03a5df: the same "trusted +131" and per-file
figures, "unclassified +0". `chainEdges`, `RankChain` and `strictWitness` (Tree) and `strictFlag` and `SameBase`
(Conditions) are G[V] tied to the theorems whose statements name them; `chainsFrom` is C; `chainLt` is G[I], the
display order of the witness; `freeWitness` is P, the proof's structure; the new fixtures are T.

## 6. Size (review F2)

Hand-written lines, from `git diff --numstat $(git merge-base HEAD main) HEAD` on the fix round's final commit, with
verbatim spec copies (`docs/spec/`) and generated files (`Audit.lean`, the `lean/*.txt` inventories, the codemap,
`trust-baseline.json`, `assurance-manifest.json`, `trust-mutants.json`) left out: about +2,550 -3. Lean product 1,708:
`Conditions.lean` 1,570 (200 lines of definitions, nearly all the spec's text; 1,327 of theorems and proof lemmas; 43
headers and comments), `Tree.lean` 128 (112 of definitions), `VE.lean` 3, `Acts/Elaborate.lean` +7 -3. Fixtures 236
(`Examples.lean`), `trust-classes.json` 193, `tools/layer_policy.py` 2, evidence 128 (`mutants.json` 49,
`trust-mutants-allow.json` 79), docs (`WEIGHING.md` 77, `DELTA.md`, this report). The size line is ~600. Rows (1)-(2)
come before it, proofs included (review F1), so it binds only the fixtures that wg-2b keeps (section 2). The overrun
is the proofs.

## 7. Tests run

- `cd lean && lake build` (default targets): "Build completed successfully (1273 jobs)". Then
  `lake build VE.Weighing.Examples` after each fixture edit: no error.
- `python3 lean/audit.py`: PASS (section 1).
- Selected tests, `zsh mac-pytest.sh --select -- --base c3d9ea938 --run` (on eb933aa9e): the fast stage
  reported "1 failed, 1611 passed". The failure was `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (Examples.lean was not classified). It is fixed in d7c1dc7db, and the rerun of that id on the Mac printed
  "1 passed". The selection's final run on the HEAD is in section 9.
- Fix round: `cd lean && lake build` (default targets) on the final Lean: "Build completed successfully (1273
  jobs)"; `python3 lean/audit.py`: "PASS: 759 source files; 8487 named theorem declarations audited …"; `uv run
  python tools/regen_generated.py --check --skip route-cases`: "checked 34 entries", none stale; `python3
  tools/check_lean_imports.py`: "Lean layer graph kept (759 modules, 22 reviewed legacy edges)" (the new import of
  `VE.Readings.SupEnv`, layer 2, is inward); `git diff $(git merge-base HEAD main) -- lean/statements.txt`: no removed line.
- Review probe F1, after the fix (f6e03a5df): `#check VE.Weighing.strictWitness`, `factors_inert`,
  `weigh_alone_base_free` elaborate, exit 0. Before it, the three names were absent from the source
  (`git show beb5d6569:lean/VE/Weighing/Conditions.lean`: 0 matches) and the reviewer's run failed; I did not rerun it
  there. The regression is `Examples.lean`'s last `example`, which names all 11 restored theorems, and
  `lean/VE/Audit.lean`'s `#print axioms` lines: the build fails if one is missing.
- Probe F-ready1: `python3 manage-agents/review-ready.py <worktree> wg-2` on cc18864a1: "PASS [mutants] Python:
  seeded bug in changed file tools/layer_policy.py". Its other FAILs: `[delta]` "L52 RESERVED BY DESIGN" (row 4),
  and `[gate]`, as no full gate ran on this round's code (the chain's).

## 8. Pilot bytes, DELTA, next item

No answer, verdict or byte changes: nothing calls the new code (DELTA.md). No pilot bytes are expected to move.
Next: the DRI's answer on `strength_iff` (DELTA.md row 4), then **wg-2b** (the rest of 7.2 and 7.3's fixtures),
then wg-3 (block decoder,
`stripWeighing`, the `weighing` pack, AR-10's row; after AT-2/AT-3a, PC-3, PC-9 and EXP-G1). en-wg sits beside it
after en-sw.

Spec re-read: `strictPair_outranks`, `strictPair_of_always`, `strictPair_down`, `strictPair_up` against
docs/spec/weighing.md:946-957; `propImplies_sound` against :1038; `condition_necessary`, `condition_sufficient`
against :1042-1052; `grant_needed`, `delegation_bounded` against :1058-1080; `weigh_conservative`,
`wellFormedWeigh_empty` against :1122-1124; `condPremise` :340, `grantConds` :363, `checkWeigh` :463, `strictPair`
:256, `splitRefusal` :517. A script compared each delivered theorem's statement and each definition with the stub's
text: all SAME. Fix round: the same comparison, whitespace-normalised, of the 11 restored theorems against
weighing.md 5's code blocks and of `chainEdges`, `RankChain`, `chainsFrom`, `chainLt`, `strictWitness`, `strictFlag`,
`SameBase` and `freeWitness` against the stub: all SAME.

## 9. Selected tests on the final code

`zsh mac-pytest.sh --select -- --base c3d9ea938 --run` on 443fa19c (clean tree, Lean unchanged after it): "recorded 110 units for tree 92f6db0594; … 0 failed", "exit=0; failed/error ids=0" (ve-mac-1). `uv run python tools/regen_generated.py --check --skip route-cases`: "checked 34 entries", none stale (`route-cases` needs the Rust release binary, which this worktree has not built; nothing it reads changed).

Fix round: `zsh mac-pytest.sh --select -- --base c3d9ea938 --run` on cc18864a1 (clean; the Lean is f6e03a5df's):
"recorded 110 units for tree 19537ed546; 0 others left to the static graph until they run; 0 failed", "ran LOCALLY
(VM) because: no mac-pytest slot on ve-mac-1 within 600s; … exit=0; 7685s". The chunked heavy files: test_trust_mutants
564 passed, test_acts_vocab_mutants 643 passed, test_english_evidence 77 passed, 0 failed. The trust mutants (section
4) ran on the snapshot c548eb971, which is f6e03a5df plus an uncommitted `mutants.json`: same Lean, "231 KILLED, 0
SURVIVOR, 0 UNKNOWN, 8 INVALID, 23 ALLOWED", exit 0.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A.: no service mode, relay or schema reads the new code.
2. Every deliverable built or moved: rows (1)-(2) are built except `strength_iff`, which is false as approved and
   reserved for the DRI (DELTA.md row 4); only fixtures move to wg-2b (section 2). One Python file changes:
   `tools/layer_policy.py` (2 lines, review F3); no permanent report test. The shared files are
   VE.lean and Audit.lean only (in-flight branch check at the start).
3. Tests can fail: PASS: mutants.json (38 killed by guards, then W1-W8 in Lean and P1 in Python), trust-mutants.json
   (exit 0), S1-S3 (section 4).
4. Python, Lean and Rust agree: N.A.: Lean only, and nothing calls it.
5. R8 binding: N.A.: no relayed answer.
6. Gate evidence matches the final HEAD: PASS for the trust mutants (snapshot c548eb971, Lean identical to
   f6e03a5df and to the HEAD). The gate itself is the chain's.
7. No unsigned item: FAIL by design (L52): DELTA.md's rows 1-3 cite R16, and row 4 reserves the DRI's signature for
   `strength_iff`'s statement. The layer question asks for no signature.
8. Every user-visible change in DELTA: PASS: none changes (DELTA.md). The trust growth is the R16 rows.
9. Test selection finds the tests: PASS: `--select` picked 116 units, among them `test_assurance_manifest.py`, which
   caught the unclassified file.
10. Statements say what is claimed: PASS: statements are as written (script comparison, section 8), and
    `lean_statements.py` reported removed 0, changed 0. Each proof's definition was mutated: mutants.json, and each
    proof broke in the first runner's log. Fix round: the 11 restored statements are as written, and `strength_iff`
    is not stated in any form, since it is false as approved (section 3).
11. Budgets fail closed: PASS: `maxPropAtoms`. The guard `!propImplies (conj 13) …` (`Examples.lean:78`) refuses 13
    atoms and accepts 12. `ResourceLimit` is `checkWeigh`'s, which is unchanged spec text.
12. No CPU or memory regression: N.A.: no runtime path calls the code. The fixtures build in seconds (`lake build
    VE.Weighing.Examples`).
13. Removed tests trailer: N.A.: no test was removed.
14. Both directions, cited evidence, spec re-read: PASS: each check is guarded both ways. Examples: accepted vs
    `StrengthOnUndeclaredEdge`, `NoSuchDecision`, `ConditionOnStrictPair`, `ConditionsDisagree`,
    `GrantNotAttributed`, a sufficient switch condition; `strictPair` true and false; 12 and 13 atoms; W-λ's split
    and non-split target. Spec re-read lines are in section 8.
