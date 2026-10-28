# df-2b: DF-π's two `example`s (build report)

**Summary.** No DRI signature is reserved and there are no DELTA rows: the item adds test code only, and trust grows
by +0. DF-π's two `example`s (spec 8.5) are proved over a `SoftDoc` literal, by `decide` through `eval_withFill`:
`B_π` is a default base with draft 1's fixed filling, and `B_π` is not a `DefaultBase`. Seeded bug P2 makes the second
example fail, and four more bugs fail the examples they target. HEAD: the last commit on `feature/df-2b`. Not run by
me: the full gate (the chain runs it on the final HEAD). Next item: DF-3.

Branch `feature/df-2b`, base main 8a64ef81b (the merge base). The plan and spec are as on main (df-1a's verbatim
copies, unchanged here).

**Statement gate.** The defeasible statement review accepted spec 3.4 and 8.5 (df-2's REPORT, "DF-S passed",
`manage-agents/defeasible-p3ver1.final.md`). Each example states what 8.5 states, and neither is false as written:
- 8.5 says "`B_π` = {excepted_r1}, fillings no/no, is a default base with the filling fixed". Example 1 is
  `DefaultBaseFixed Uπ Dπ (softX Uπ Dπ []) Bπ`, where `DefaultBaseFixed` is the stub's draft-1 definition. That is
  `DefaultBase` with the competitor `withOpen U D B δ B.relation`, P2's text exactly.
- 8.5 says it "is not one with the filling varied". Example 2 is `¬ DefaultBase Uπ Dπ (softX Uπ Dπ []) Bπ`.
- `Meaning.lean`'s statements are unchanged.

## 1. Plan rows delivered

| Row (task deliverables; plan DF-2, spec 3.7, 8.5) | Delivered | Where, test |
| --- | --- | --- |
| (1) draft 1's fixed-filling minimality holds at `B_π` | yes, `example : DefaultBaseFixed Uπ Dπ (softX Uπ Dπ []) Bπ` | `lean/VE/Defaults/MeaningExamples.lean`; `lake build` |
| (2) `¬ DefaultBase U D (softX U D []) B_π` | yes, `example : ¬ DefaultBase Uπ Dπ (softX Uπ Dπ []) Bπ` | same |
| both over a `SoftDoc` literal the kernel can evaluate, by `decide` through `eval_withFill` | yes: `Dπ`, `Uπ = ⟨soften Dπ, unspec⟩`; a `#guard` checks that the literal is the decoded `dπ` | same |
| (3) seeded bug P2 also fails the second example | yes: `EXAMPLE example : ¬ DefaultBase …` | `mutants.json`, `evidence/mutants.out` |
| (3) one more bug per example | yes: D1 for example 2; W1, S2 and F1 for example 1 | same |
| Generated inventories, through `regen_generated.py --write` | `Audit.lean`, `axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt` | `regen_generated.py --check` (33 entries) |

Nothing is cut: no df-2c.

## 2. How the examples are decided

The situations are one-element finite models, `sitπ on fon = withFill Uπ (Mπ on) (finFill (Mπ on) (Fπ fon))`. `on`
lists the base predicates true at the one assistant, and `fon` lists the unsaid tables filled yes there.
`B_π = sitπ [excπ] []`.

- **Admissibility (`admissible_π`).** `BaseAdmissibleX` has four parts:
  - typing: by `rel_π` and `decide` on `envAt (fill Uπ) 0`;
  - the background: empty, because `lits = []`;
  - `Fill_T`: `decide` on `fillValid`, read through `eval_withFill`;
  - `X = softX Uπ Dπ [] = []`: by `decide`.
- **The competitor (`open_π`).** A `withOpen` competitor whose tables are a situation's is that situation. This is
  structure equality, by the relation characterisation `rel_π`.
- **Example 1.** Let `δ` be any competitor's decisions below `B_π`. If `δ` drops the exception at the assistant, the
  competitor with the filling kept is `sitπ [] []`. `decide` gives `fillValid … = false` there, so the competitor is
  not admissible.
- **Example 2.** The competitor `sitπ [] [unsaid__x_permitted]` is admissible (`fillValid … = true` by `decide`) and
  has no exception, so minimality fails.

**Why names go through three lemmas.** The kernel cannot reduce `String.map` or `String.startsWith` (both use
well-founded recursion). Rule names reach every decision predicate through `ruleKey`, which uses `String.map`, and
`SwitchesOff` filters labels with `startsWith`. So each such fact is proved once:
- `soften_π`: `soften Dπ = Sπ`, the softened document written out, from `exceptedName_π` (`VE.Readings.map_data`);
- `decisions_π` and `decisionNames_π`;
- `switch_π`: r1's label is not a switch label. It unfolds `String.substrEq`'s loop through the first mismatch with
  `VE.Readings`' `unfold_substrEq_loop`.

Every other check is `decide` on `Uπ_eq`'s literal. A first version proved a general `startsWith` lemma from
`VE.Question.Strings`. `check_lean_imports.py` refused that outward import, so it was replaced (cc40c3327).

## 3. Seeded bugs

Product code is unchanged, so there is no seeded bug per product language. The bugs are planted in the definitions the
examples check (`Meaning.lean`) and in one fixture. Each one makes its example's statement false; each was run and
restored. Run: `python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-2b/mutants.json`. Saved
output: `evidence/mutants.out`. Control: 0 failures. **5 of 5 fail.**

| # | File, definition: bug | Example made false | Fails |
| --- | --- | --- | --- |
| P2 | `Meaning.lean` `DefaultBase`: the filling fixed (draft 1; plan's seeded bug) | 2 | `EXAMPLE example : ¬ DefaultBase …`; also `default_entails_minimal_of`, `defaultBase_of_dflt` |
| D1 | `Meaning.lean` `DefaultBase`: minimality read the wrong way | 2 | `EXAMPLE example : ¬ DefaultBase …` |
| W1 | `Meaning.lean` `withOpen`: the competitor keeps `B`'s decisions | 1 | `THEOREM open_π` (the competitor lemma) |
| S2 | `Meaning.lean` `SwitchesOff`: reads every `Dflt_T` premise (prefix `default:`) | 1 | `THEOREM switchesOff_π`; also a df-2 `#guard` |
| F1 | `MeaningExamples.lean` `Bπ`: the permission's gap filled yes | 1 | `EXAMPLE example : DefaultBaseFixed …` |

**The runner change.** `docs/defeasible/df-1a/evidence/run_mutants.py` (an evidence script, not product code) now does
two more things:
- An error inside an `example` is reported as `EXAMPLE <statement>`. Before, it was "NOT A GUARD", and an entry's
  `examples` list names the examples it must fail.
- An entry with `"in": "fixtures"` edits the fixtures file.

No earlier fixtures file has an `example` (`grep -c '^example'`: 0 in `Examples.lean`, `RouteExamples.lean` and
`WireExamples.lean`), so earlier saved runs are unaffected.

## 4. Trust, DELTA, evidence

- **Trust:** `trust_map.py --check` PASS. K +0, S +0, D +0, G +0, unclassified +0, trusted +0. The ten new
  definitions are class T (a test module) in `tools/trust-classes.json`: `nπ`, `Dπ`, `Uπ`, `excπ`, `Sπ`, `Mπ`, `Fπ`,
  `sitπ`, `DefaultBaseFixed`, `Bπ`. No R16 allowance is needed, and no FOLLOW-UPS row.
- **DELTA:** none. No answer, schema, pin, English row or trusted line changes.
- **Build and audit:** `lake build` 1,121 jobs. `python3 lean/audit.py`: PASS (639 files, 7,211 theorems, standard
  axioms only). `check_lean_imports.py`: layer graph kept.
- **Generated files:** `regen_generated.py --check` 33 entries, exit 0. The removed lemma's stale `#print axioms` line
  was dropped before `lean_statements.py` and `audit.py --write`, as the df-1a recipe says.
- **Selected tests:** `mac-pytest.sh --select -- --base 8a64ef81b --run` at cc40c3327 (clean): 390 units on ve-mac-1, including `lake build` and
  `lean/audit.py`, **0 failed**, exit 0 (4,281 s). The later commit adds only this report.
- **Pre-existing failures** (`main-known-red.txt`): none failed.
- **Pilot bytes:** 0 expected. No CLI path, service mode or English row reads `MeaningExamples.lean`.

**Size** (`git diff --numstat 8a64ef81b`; generated files left out): `MeaningExamples.lean` +239 −1,
`run_mutants.py` +17 −5, `trust-classes.json` +10, `mutants.json` +102, `mutants.out` +27, and this report.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): cc40c3327,
b4fcd7063, e721e5986, 95159b450.

## 5. Next item

**DF-3** (default readings on documents, after df-1b).

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no shape, schema, relay or mode changes; `regen_generated.py --check`
   rewrites no schema.
2. **Every deliverable built.** PASS: section 1 gives each row its place and check. No product file changed. The only
   overlap with in-flight branches is the shared ledger `tools/trust-classes.json` (own entries).
3. **Tests can fail.** PASS: `evidence/mutants.out`, 5 of 5 fail where named, including the plan's P2 inside example 2.
4. **Python, Lean and Rust agree.** N.A.: nothing reaches the new code from Python or Rust. The literal is checked
   against the real decoder by a `#guard` (`holds dπ …`).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS: the base is the merge base 8a64ef81b, the commit list comes from
   `main..HEAD --no-merges`, and the chain gates the final HEAD.
7. **No unsigned item.** PASS: no DELTA row, and no signature is reserved.
8. **Every user-visible change in DELTA.** PASS: there is none (`regen_generated.py --check`: no schema, pin or
   answer changes; bytes 0).
9. **Test selection.** PASS: the selected plan includes `lake build` and `lean/audit.py`, which build the examples.
10. **Statements say what is claimed.** PASS: the statement gate above. Example 2 is `Meaning.lean`'s own
    `DefaultBase`. Example 1's `DefaultBaseFixed` is P2's text, and P2 fails example 2.
11. **Budgets fail closed.** N.A.: no budget, limit or deadline is added.
12. **No CPU or memory regression.** N.A.: no route runs the new code. The module elaborates in about 4 s.
13. **Test-removed trailers.** N.A.: no test is removed or renamed. `startsWith_prefix` was a lemma of this branch
    only.
