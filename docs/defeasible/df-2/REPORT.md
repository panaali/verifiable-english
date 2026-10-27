# df-2: the meaning (build report)

No DRI signature is reserved: the one delta (trust, DELTA T1) is signed by standing ruling R16. **The meaning theorem
is proved in full, not under the fallback.** **Size cut:** DF-π's two `example`s (spec 8.5) are **df-2b** (section 5).

Branch `feature/df-2`, base main f39c78dde (the merge base). Plan and spec as on main (df-1a's verbatim copies,
unchanged here).

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`). df-1ac's comparator now takes a spec
section: `python3 docs/defeasible/df-1ac/evidence/compare_statements.py lean/VE/Defaults/Meaning.lean 7.3` gives
**12 OK, 0 not OK** (`evidence/statements.out`). The 12 are `withOpen`, `SwitchesOff`, `DefaultBase`, `softX`,
`leastDecisions`, `replacementSafe`, `replace_admissible`, `defaultBase_of_dflt`, `default_entails_minimal`,
`ReplacementHolds`, `default_entails_minimal_of` and the `defaults-model` corollary `defaults_model_default_base`.
- They are compared token for token after whitespace normalisation, with comments, docstrings and proofs removed.
- With no section argument the comparator still checks 7.2 against `Wire.lean`, with output byte-identical to
  df-1ad's saved `statements.out` (42 OK).
- It reports DIFF for both plan seeded bugs (`evidence/statements-mutants.out`).
- No statement changed and no hypothesis was added.

## 1. Plan rows delivered

| Row (task deliverables; plan DF-2, spec 7.3, 8.2, 8.5, 8.9) | Delivered | Where, test |
| --- | --- | --- |
| (1) `withOpen`, `SwitchesOff`, `DefaultBase` (unsaid tables varied), `softX`, `leastDecisions`, `replacementSafe`, `ReplacementHolds` | yes, spec text | `Meaning.lean` (6c67c0472); `compare_statements.py … 7.3` |
| (1) `replace_admissible`, `defaultBase_of_dflt`, `default_entails_minimal` | yes, **proved** (standard axioms only) | `Meaning.lean`; `lean/VE/Audit.lean`; `lean/audit.py` |
| (1) the fallback `default_entails_minimal_of` | yes, proved; `default_entails_minimal` is derived from it with `replace_admissible` | `Meaning.lean` |
| (1) the `defaults-model` corollary `defaults_model_default_base` | yes, proved | `Meaning.lean` |
| (1) DF-π's two `example`s | **df-2b** (size) | section 5 |
| (2) seeded bug: `default_entails_minimal` without `hcoh` | yes (P1): the build fails, and the comparator reports DIFF. DF-γ's counterexample is spec 8.5's computed row (left side true, right side false), computed in the DF-S stub and not recomputed here | `mutants.json`, `evidence/mutants.out` |
| (2) seeded bug: `DefaultBase` with the filling fixed (draft 1) | yes (P2): `default_entails_minimal_of`'s proof breaks, and the comparator reports DIFF. The DF-π example that also fails under it is df-2b | same |
| (2) one mutant per new trusted definition | yes: 17 hand mutants and `trust_mutants.py` (section 3) | same; `trust-mutants.json` |
| (3) `lean/DEFAULTS.md`'s minimality sentence | yes: the theorem is proved in full, so the reading is stated for documents that pass the gate and `replacementSafe`; otherwise nothing claims it | `lean/DEFAULTS.md` (5857f0b1f) |
| Generated inventories, through `regen_generated.py --write` | `Audit.lean`, `axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt` | `regen_generated.py --check` |

## 2. How the proof goes, and what it reads from the document

The proof is the plan's (3.4), with no change to any statement. A few facts were needed that no existing lemma stated.
Each is now a lemma in `Meaning.lean`:

- `cond_declared`, `cond_free`: an exception condition names only predicates of the source environment, so it names
  no decision and no unsaid predicate. This is read off `checkSoftRule`'s typing check `C.check D.E …` through
  `forIn_each`.
- `decision_arity`: every decision predicate has arity 1 or 2, so its atom is its table on typed tuples. For `outweighs`
  the arity is that of the act key, a regulated predicate (`pair_regs`). Without this the theorem would be false: at
  arity 3 the atom is `⊥`, and an exception there would be unconstrained.
- `excepted_inj`, `excepted_only`: from `decNodup`, an exception predicate belongs to one rule and is neither a switch
  nor an `outweighs` predicate. So the least decisions hold on exception predicates only.

`replace_admissible` builds the base `B₀` with the least decisions and no unsaid tables. It applies `fill_extends` to
`B₀`, keeping `B`'s unsaid tables off the pair members, and shows that the result is `withOpen U D B δ_B F`. The
check `replacementSafe` carries `R`, and `hcoh` gives `Coh_T`.

`default_entails_minimal`'s (→) takes `ReplacementHolds` from `replace_admissible`. Minimality then gives `B`'s
decisions equal to `δ_B`, and `Dflt_T` holds in `B` (`sat_dflt`). (←) is `defaultBase_of_dflt`.

**Observation, no statement changed:** the proofs never read `DefaultBase`'s `SwitchesOff D B` conjunct. Minimality
already forces every switch off, because the least decisions have none. So the conjunct is implied, not an extra
condition.

## 3. Seeded bugs (Lean only) and trust

No Python or Rust product file changed. Two evidence scripts changed, and neither is product code:
- `docs/defeasible/df-1ac/evidence/compare_statements.py` gains its section argument.
- `docs/defeasible/df-1a/evidence/run_mutants.py` gets a fix, described below.

The mutants are run by `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-2/mutants.json`.
Each keeps every theorem and must fail inside the ones it names. Saved run: `evidence/mutants.out`, control 0
failures, **17 of 17 fail**.

| # | `lean/VE/Defaults/Meaning.lean`, definition: bug | Fails (theorem) |
| --- | --- | --- |
| P1 | `default_entails_minimal` stated without `hcoh` (plan) | `default_entails_minimal` |
| P2 | `DefaultBase` with the filling fixed, draft 1 (plan) | `defaultBase_of_dflt`, `default_entails_minimal_of` |
| D1 | `DefaultBase`: minimality read the wrong way | `defaultBase_of_dflt`, `default_entails_minimal_of` |
| W1, W2 | `withOpen` keeps `B`'s decisions; keeps `B`'s unsaid tables | `replace_admissible`, `defaultBase_of_dflt`; `replace_admissible` |
| S1 | `SwitchesOff` reads the switch premises negated | `defaultBase_of_dflt`, `default_entails_minimal_of` |
| X1 | `softX` drops `R` | `softX_eq`, `defaults_model_default_base` |
| L1, L2 | `leastDecisions` not restricted to typed tuples; reads the necessary conditions | `least_le`, `replace_admissible` (L2 also `sat_dflt`) |
| R1 | `replacementSafe` without its pair-member check | `replace_admissible` |
| H1 | `ReplacementHolds` asks `softX` in place of `defaultX` | `default_entails_minimal_of`, `default_entails_minimal` |
| T1–T6 | `trust_mutants.py`'s operators on the two Props no check can decide: T1–T4 `DefaultBase` body true or false, `∧`→`∨` twice; T5, T6 `ReplacementHolds` body true or false | T1–T4 `defaultBase_of_dflt`, `default_entails_minimal_of`; T5, T6 `default_entails_minimal_of` |

**The runner fix.** `run_mutants.py` matched only untagged Lean errors (`error: `). P1 fails with
`error(lean.unknownIdentifier): Unknown identifier hcoh`, so the runner first reported it as SURVIVES. The pattern now
reads both forms. The control and every other mutant are unchanged, and the stricter pattern can only add failures.
The saved runs of df-1a to df-1ae were made with the old pattern (FOLLOW-UPS "## df-2" asks for one rerun).

**`trust_mutants.py`** ran on the Mac on the final Lean, as a full run:
- Result: 20 killed, 4 invalid, **45 allowed**, 0 survivors, 0 UNKNOWN, exit 0 (`trust-mutants.json`,
  `trust-mutants-allow.json`).
- The kills come from the `#guard`s of the new `MeaningExamples.lean`:
  - `softX` against the decoder's own `X`;
  - `SwitchesOff` and `leastDecisions` at one-element situations, decided through `eval_withFill`;
  - spec 8.2's `replacementSafe` row (DF-π and DF-α).
- Why each allowed mutant is allowed (one line each in the allow file):
  - `DefaultBase` and `ReplacementHolds` quantify over every table or structure, so no check can evaluate them. The
    allow lines cite T1–T6.
  - The `SwitchesOff` and `leastDecisions` mutants that elaborate are refuted at the guard line their UNKNOWN reports.
    The tool cannot count a check that goes through a `Decidable` instance Lean rebuilds from the mutated body; this
    is the `VE.Acts.Lexical.Accepts` precedent.
  - The rest do not elaborate.

**Trust** (R16, DELTA T1): **S +35, V +5, K +0**, all in `Meaning.lean`.
- S: `withOpen`, `SwitchesOff`, `DefaultBase`, `leastDecisions` and `ReplacementHolds`.
- G[V]: `softX`.
- C: `replacementSafe`.
- The allowance is recorded with `trust_map.py --allow`. FOLLOW-UPS "## df-2" asks for the ties pass.

## 4. Evidence

- `lake build`: 1,111 jobs, every `#guard` passes. `python3 lean/audit.py`: PASS (631 files, 7,125 theorems, standard
  axioms only). `#print axioms` for `default_entails_minimal` and `defaults_model_default_base`: `propext`,
  `Classical.choice`, `Quot.sound`.
- `regen_generated.py --check`: 33 entries, exit 0. `trust_map.py --check`: PASS with the R16 allowance.
- `tools/check_*_statements.py` (4): exit 0. `gate_collection.py --check --prebuilt`: 19,534 collected; 0 added,
  0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests on the Mac: `mac-pytest.sh --select -- --base f39c78dde --run` at HEAD 5857f0b1f (clean). It ran
  76 of 466 units, including `lake build`, with **0 failed** (1,239 s). Later commits change only docs, the JSON layout
  of `mutants.json` and the allow file, and the `trust_mutants.py` evidence.
- Pre-existing failures (`main-known-red.txt`): none failed.
- Not run by me: the full gate (the chain runs it on the final HEAD).

**Pilot bytes:** 0 expected. No CLI path, service mode or English row reads `Meaning.lean`.

**Size** (`git diff --numstat f39c78dde`, hand-written lines only; generated files and tool outputs left out):

| File | Lines |
| --- | --- |
| `Meaning.lean` | 495 (about 75 are spec 7.3's definitions and statements) |
| `MeaningExamples.lean` | 81 (R16's checks) |
| `DEFAULTS.md` | 33 |
| `trust-classes.json`, `VE.lean` | 33 |
| `mutants.json`, allow file | 57 |
| evidence scripts (two fixes) | 12 |
| DELTA, this report | about 170 |

That is about 880 lines, above the ~600 guideline. I measured after (1)'s proofs: 515 lines with `Meaning.lean` alone.
At that point I cut DF-π's examples, which need a document the kernel can evaluate (section 5). The rest is the
seeded-bug and R16 evidence the item cannot finish without. `Meaning.lean` cannot be split further: its theorems are
one argument.

## 5. Next items

- **df-2b**, DF-π's two `example`s (spec 8.5):
  - draft 1's fixed-filling minimality holds at `B_π`;
  - `¬ DefaultBase U D (softX U D []) B_π`.

  Both are over a document the kernel can evaluate, a `SoftDoc` literal rather than `decodeSoftU`'s JSON, by
  `decide` through `eval_withFill`. Under seeded bug P2 the second example must fail as well. `MeaningExamples.lean`
  already has DF-π decoded (`dπ`) and the one-element situations.
- Then **DF-3** (readings, after df-1b). DF-E1 needs the DRI's model-call budget.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): 74f2d42a7,
eda119a59, 0d6e2ff35, 5857f0b1f, debe5ccfe, c81815f68, 5ea75367d, 0f5b67d1c, 9cd80fcb0, 0cd4551db, 4d26d61c9,
27b81cec5, 6c67c0472.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no shape, schema, relay or mode changes; `regen_generated.py --check`
   rewrites no schema.
2. **Every deliverable built.** PASS. Section 1 gives each row its commit and test, or names df-2b under the size
   rule. A diff grep finds no Python product file and no permanent report test. Overlap with in-flight branches is only
   the shared ledgers `lean/VE.lean` (imports) and `tools/trust-classes.json` (own entries), plus generated files (R12).
3. **Tests can fail.** PASS. `evidence/mutants.out`: 17 of 17 fail, at least one per new definition and the plan's
   two. `trust_mutants.py` exits 0 (`trust-mutants.json`). The comparator reports DIFF on P1 and P2
   (`evidence/statements-mutants.out`), and the planted false guards fail (checked by hand before commit).
4. **Python, Lean and Rust agree.** N.A.: nothing reaches the new code from Python or Rust. The guards decode real JSON
   through `decodeSoftU`, including a 2-switch rule and a rule with two conditions.
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS. The base is the merge base f39c78dde, the commit list comes from
   `main..HEAD --no-merges`, and the chain gates the final HEAD.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence.
8. **Every user-visible change in DELTA.** PASS: there is none besides trust (`regen_generated.py --check`: no schema,
   pin or answer changes; bytes 0).
9. **Test selection.** PASS. The 76 selected units include `lake build`, in which every seeded bug fails
   (`select_tests.py` plan: `+ lake build`).
10. **Statements say what is claimed.** PASS. `compare_statements.py … 7.3`: 12 OK. No hypothesis was added. The
    theorems are about `EntailsX` and `DefaultBase` themselves, which `lean/DEFAULTS.md` describes.
11. **Budgets fail closed.** N.A.: no budget, limit or deadline is added.
12. **No CPU or memory regression.** N.A.: no route runs the new code; no pilot run (L70).
13. **Test-removed trailers.** PASS: `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale,
    0 malformed.
