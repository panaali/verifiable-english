# wg-2 REPORT: weighing's block, strength, conditions and grants (Lean)

No DRI signature is reserved. One DRI question is open and blocks nothing: the layer row for `VE.Weighing.*`
(`manage-agents/inbox/dri/20261104T025807Z-wg-2-3977838.md`, section 3). The size line binds: this item is the first
coherent part of WG-2, and the rest is **wg-2b** (section 2).

Plan: docs/spec/weighing-PLAN.md "WG-2" (lines 1226-1245) and the batch row (line 1104). Spec: docs/spec/weighing.md
sections 1 and 5. Both files are copied verbatim from 19c1eb676. The statement gate passed (WG-1's gate at 1ae4b7402;
wg-rev changed no WG-2 statement). Base: c3d9ea938. Commits: `git log --oneline main..HEAD --no-merges`, c49030526
to the HEAD.

## 1. Plan rows delivered

| Row (task "Deliver") | Delivered | Commit | Evidence |
|---|---|---|---|
| (1) `Tree.lean`: `CondKind`, `Target`, `CondDecl`, `FactorDecl`, `GrantDecl`, `WeighEnv`, `WeighDoc`, `rankOrder`, `strictPair`, `targetF`, `targetSorts` | yes, verbatim from weighing.md 1.1-1.3 (the stub's text). A script compared every definition with the stub's: all equal | bff4a560b | `Examples.lean` guards; mutants.json |
| (1) `strictWitness` | **no: wg-2b** (R16 cap, section 2) | 04442baec | - |
| (1) `strictPair` through QS-1's `VE.Closure`, proved equal to soft's `outranksPlus` | yes: `rankOrder_above` (soft's `outranksPlus` is QS-1's `above`, by `VE.Closure.outranksPlus_eq_above`). No rank closure of its own | 74bfbe9a8 | `strictPair_outranks`, `_down`, `_up` |
| (2) `Conditions.lean`: `strengthPremises`, `condPremise`, `grantConds`, `weighLabelled`, `weighPremises`, `propImplies`, `checkWeigh`, `WellFormedWeigh` | yes, verbatim from weighing.md 1.4-1.6. A grant premise is `condPremise`'s necessary `.off` case (`grantEntries`) | bff4a560b | guards; mutants.json; trust-mutants.json |
| (2) theorems of weighing.md 5.1-5.4 | **11 of 22** proved, statements as written: `strictPair_outranks`, `strictPair_of_always`, `strictPair_down`, `strictPair_up`, `propImplies_sound`, `condition_necessary`, `condition_sufficient`, `grant_needed`, `delegation_bounded`, `weigh_conservative`, `wellFormedWeigh_empty`. The other 11 are wg-2b's | 74bfbe9a8, 03d7e78a2 | `python3 lean/audit.py`: "PASS: 759 source files; 8408 named theorem declarations audited …; only the declared standard axiom allowlist" |
| (2) each theorem in `lean/VE/Audit.lean` | yes, through `regen_generated.py` (`lean-audit-manifests`): 24 `#print axioms` lines | 1fe968ba3 | `lean/axioms.txt` (propext, Quot.sound, Classical.choice only) |
| (3) `Examples.lean`: W-α to W-θ, W-κ, W-λ, W-μ | **part**: W-α (with a strict-flag twin), W-ε, W-λ's act text, W-μ in full (7.2's rows: accepted, labels, 4 of 256, the outcomes, the swapped refusal), θ19/θ20's 12/13-atom bound, plus W-α3 and a W-ζ3 chain so that every list has more than one entry. The other rows are wg-2b's | f61d43692, 0e9e5207f, f43e5900e, adfe58d0b | `lake build VE.Weighing.Examples` |
| (4) `lean/WEIGHING.md`: every definition and theorem in plain words | yes for everything delivered; wg-6a's zone text is kept, and WG-2's sections are added after it | 04442baec | the file |
| (4) `lean/VE.lean` import, frozen inventory, assurance manifest | the import, by hand (the `lean-roots` union). The frozen inventory needs no row: `regen_generated.py --write` left `frozen-sources.sha256` unchanged, since weighing is not frozen. The assurance manifest has `Weighing/Examples.lean` under `other_json` (fixtures that parse JSON) | f61d43692, d7c1dc7db | `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified` passed |
| "Deleted, not duplicated": `excPremisesOf` as the `.excepted` instance of one generator | **not moved**, for the reason in section 3 | - | `lean_statements.py`: "removed: 0, changed: 0" |
| `lean_statements.py` shows additions only | yes | 1fe968ba3, adfe58d0b | output "removed: 0 / changed: 0"; `git diff main -- lean/statements.txt` has no `-` line |

## 2. Cut to wg-2b (the size line and R16's cap)

The size line is ~600 hand-written lines. The definitions of (1) and (2) are 319 lines of the spec's own text, and
the fixtures that kill every trust mutant add 163. With the side table (145) and the evidence, this part already
measures +1008 (section 6). The trust mutants needed the fixtures, so they could not be cut. What moves, unchanged
in the spec:

- theorems: `holistic_iff_no_always_chain`, `strictWitness_isSome`, `strictWitness_chain`, `strength_iff`,
  `always_dominates`, `always_no_override`, `all_always_is_strict`, `grant_within_grantor`, `weighPremises_wellFormed`,
  `weighPremises_substructure`, `weigh_alone_base_free` (with `SameBase`, `freeWitness`, `strictFlag`, `RankChain`);
- definitions: `strictWitness`, `chainEdges`, `chainsFrom`, `chainLt`, cut at 04442baec. With them, trust measured
  +154 (`trust_map.py --check`, "trusted +154"), over R16's 150. They are display-only, and both of their theorems
  are wg-2b's;
- fixtures: the rest of weighing.md 7.2 (W-β, W-γ, W-δ, W-ζ/ζ2, W-η, W-θ with θ11, W-κ's sixteen branches, the
  grant cycles, the `strength_iff` regressions F9/F10/F13) and 7.3's "exactly when" rows.

## 3. Deviations and answers to the task's questions

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

There is one hand mutant per new definition, 38 in all, each killed by a `#guard`. The run cut
`Conditions.lean`'s theorems, so a broken proof kills none: [mutants.json](mutants.json), with file, definition,
mutant, test and check. `splitRefusal`'s mutant fails `Acts/ElaborateExamples.lean:150`.

Trust mutants (build checklist 13a): `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/weighing/wg-2/trust-mutants-allow.json --rescore docs/weighing/wg-2/trust-mutants.json --json
docs/weighing/wg-2/trust-mutants.json` exited 0 on the HEAD adfe58d0b (tree e4ded25a23ae; Lean is unchanged since):
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
[DELTA.md](DELTA.md) has the one R16 row per file.

## 6. Size

Hand-written lines, from `git diff --numstat $(git merge-base HEAD main)`, verbatim copies and generated files left
out: +1008 -4. Of these: Lean product 504 (`Conditions.lean` 390, of which 190 are the spec's definitions;
`Tree.lean` 101; `VE.lean` 3; `Acts/Elaborate.lean` +7 -3), fixtures 163, `trust-classes.json` 145, evidence 119
(`mutants.json` 40, `trust-mutants-allow.json` 79), docs 69 (`WEIGHING.md` 46, `DELTA.md` 23), plus this report.
The size line is ~600. Section 2 says what was cut, and why the fixtures stay.

## 7. Tests run

- `cd lean && lake build` (default targets): "Build completed successfully (1273 jobs)". Then
  `lake build VE.Weighing.Examples` after each fixture edit: no error.
- `python3 lean/audit.py`: PASS (section 1).
- Selected tests, `zsh mac-pytest.sh --select -- --base c3d9ea938 --run` (on eb933aa9e): the fast stage
  reported "1 failed, 1611 passed". The failure was `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`
  (Examples.lean was not classified). It is fixed in d7c1dc7db, and the rerun of that id on the Mac printed
  "1 passed". The selection's final run on the HEAD is in section 9.

## 8. Pilot bytes, DELTA, next item

No answer, verdict or byte changes: nothing calls the new code (DELTA.md). No pilot bytes are expected to move.
Next: **wg-2b** (section 2's theorems, `strictWitness`, the rest of 7.2 and 7.3), then wg-3 (block decoder,
`stripWeighing`, the `weighing` pack, AR-10's row; after AT-2/AT-3a, PC-3, PC-9 and EXP-G1). en-wg sits beside it
after en-sw.

Spec re-read: `strictPair_outranks`, `strictPair_of_always`, `strictPair_down`, `strictPair_up` against
docs/spec/weighing.md:946-957; `propImplies_sound` against :1038; `condition_necessary`, `condition_sufficient`
against :1042-1052; `grant_needed`, `delegation_bounded` against :1058-1080; `weigh_conservative`,
`wellFormedWeigh_empty` against :1122-1124; `condPremise` :340, `grantConds` :363, `checkWeigh` :463, `strictPair`
:256, `splitRefusal` :517. A script compared each delivered theorem's statement and each definition with the stub's
text: all SAME.

## 9. Selected tests on the final code

See the commit that follows this report: the selection run on the HEAD and its result.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A.: no service mode, relay or schema reads the new code.
2. Every deliverable built or moved: PASS, with section 1's table and section 2's cut. The cut is named in the
   FOLLOW-UP line (wg-2b). Grep of the diff: no Python file and no permanent report test. The shared files are
   VE.lean and Audit.lean only (in-flight branch check at the start).
3. Tests can fail: PASS: mutants.json (38 killed by guards), trust-mutants.json (exit 0), S1-S3 (section 4).
4. Python, Lean and Rust agree: N.A.: Lean only, and nothing calls it.
5. R8 binding: N.A.: no relayed answer.
6. Gate evidence matches the final HEAD: PASS for the trust mutants (tree e4ded25a23ae; Lean is unchanged after
   it). The gate itself is the chain's.
7. No unsigned item: PASS: DELTA.md's three rows cite R16. The one open question asks for no signature.
8. Every user-visible change in DELTA: PASS: none changes (DELTA.md). The trust growth is the R16 rows.
9. Test selection finds the tests: PASS: `--select` picked 116 units, among them `test_assurance_manifest.py`, which
   caught the unclassified file.
10. Statements say what is claimed: PASS: statements are as written (script comparison, section 8), and
    `lean_statements.py` reported removed 0, changed 0. Each proof's definition was mutated: mutants.json, and each
    proof broke in the first runner's log.
11. Budgets fail closed: PASS: `maxPropAtoms`. The guard `!propImplies (conj 13) …` (`Examples.lean:78`) refuses 13
    atoms and accepts 12. `ResourceLimit` is `checkWeigh`'s, which is unchanged spec text.
12. No CPU or memory regression: N.A.: no runtime path calls the code. The fixtures build in seconds (`lake build
    VE.Weighing.Examples`).
13. Removed tests trailer: N.A.: no test was removed.
14. Both directions, cited evidence, spec re-read: PASS: each check is guarded both ways. Examples: accepted vs
    `StrengthOnUndeclaredEdge`, `NoSuchDecision`, `ConditionOnStrictPair`, `ConditionsDisagree`,
    `GrantNotAttributed`, a sufficient switch condition; `strictPair` true and false; 12 and 13 atoms; W-λ's split
    and non-split target. Spec re-read lines are in section 8.
