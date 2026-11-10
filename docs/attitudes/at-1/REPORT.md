# at-1 report: the attitudes Lean core, last part (spec 6.1's eight remaining statements and row at-1b-tie)

Status: done at HEAD (the commit carrying this report), review fixes included (section "Review fixes"). No signature is reserved; no DELTA row.
Changed: the eight remaining 6.1 statements are proved, their text unchanged (`Theorems.lean`); 7.4's and 7.5's points (`Examples.lean`); ATTITUDES.md lists all 27.
Trust: `AFormula.toFormula` S to D[V], tied (row at-1b-tie): K +0, S -10, tied +10, trusted -10. Shortfalls: at-1b 20, at-1a 49, 69 in all (signed, -trust item 3).
Open: review C items F2, F3 (the ties pass), F6, unchanged. Next: at-2 and at-3a, then pc-11; no at-1e ((3) stayed here, section "Size").

Details. `Theorems.lean` also gains the helper lemmas, and at-1d's `denote_interp_base` and `tupleTyped_interp` are now instances of
general lemmas. `tools/trust-classes.json` records the tie move and the new fixtures. The tie move is D +10, with no new trusted line, so
no R16 growth and no FOLLOW-UPS row.

Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core" (from line 792). Spec: docs/spec/attitudes.md 6.1 (the eight statements at
1275-1279 and 1284-1311, the proof notes at 1345-1352), 2.5, 2.8, 7.2, 7.4, 7.5, section 11. Statement gate: AT-0 is done
(reviews/dri-decisions-20261103-fp-attitudes-r2.md item 3). The row keeps the parent id (reviews/dri-decisions-20261102-attitudes-scope.md item 1).

## Deliverables

| Task line | Delivered | Commit | Check |
|---|---|---|---|
| (1) `old_formula_invariant`, `att_elaboration_faithful`, each with 7.5's guard or a Prop example on F-AT1's points | Proved. `old_formula_invariant` is `denote_interp_of` (at-1d's `denote_interp_base`, generalised to any environment that declares no generated name) at `keyOf_old`. `att_elaboration_faithful` goes by induction on `AFormula`, over `toFormula`'s cases; its `att` case reads the atom through `interp_name`. Examples: φ = "every situation is the category", true on both sides with the category true and false on both with it false, each side read directly (`cat_interp`); the elaborated guard `guard1E` (`guard1_elab`, by `rfl`) read on `interp` directly (`atom_interp_M`) at M1-M4 gives true, true, false, false, and the theorem gives the attitude side | 0de99986bf, fc9c1eb496, 2d577d5fc4 | the examples under "`old_formula_invariant`" and "`att_elaboration_faithful`" in `Examples.lean` |
| Row at-1b-tie | `AFormula.toFormula` (10 lines) moved from S to D[V], tied to `att_elaboration_faithful`. `tools/trust_map.py` accepts the tie (section "Trust") | fc9c1eb496 | `trust_map.py --check`: PASS |
| Size after (1) | 290 lines (278 added and 12 changed). The commit includes all eight proofs: see the order deviation in "Size" | fc9c1eb496 | section "Size" |
| (2) `interp_admissible`, `restrict_admissible`, `restrict_intended`, `interp_restrict`, each pinned on F-AT1, with a refusing case where a hypothesis fails | Proved. Examples, following 7.4's rows. `interp_admissible`: M1's typed `J` gives an admissible `interp`; `thinks` at the reversed (untyped) tuple gives neither an intended model nor an admissible `interp`. `restrict_admissible` and `restrict_intended`: M1 on `interp` (RM1's relations) satisfies the frame, and its restriction is admissible and intended; M2 on `interp` (RM2) breaks the factive premise, and its restriction, read directly, knows the false category, so it is not intended. `hT` failing: the reversed tuple satisfies the frame (a `#guard`) but is not admissible, and its restriction holds an untyped tuple, so it is not intended; the category at the instance `0` is admissible neither before nor after the restriction. `interp_restrict`: a generated name's tuple in `J` holds on both sides, and the restriction does not keep it as an old relation; a tuple not in `J` holds on neither side. Both sides are read directly, and the theorem relates every name | 0de99986bf, 693048ded9, 2d577d5fc4 | the examples from "`interp_admissible` (7.4, its hypothesis)" to "`interp_restrict` (7.4)" |
| Size after (2) | 381 lines (369 added and 12 changed) at 693048ded9, which holds the examples for both (2) and (3); about 330 without (3)'s 38 lines of examples | 693048ded9 | section "Size" |
| (3) `att_old_language_conservative` (both directions, as the proof note says) and `att_conservative_doc` | Proved. Left to right: extend by the empty relations (`interp_admissible` with the vacuous `Intended`, `empty_relations_frame`, `old_formula_invariant`). Right to left: restrict (`restrict_admissible`; `interp_restrict` through `denote_withRelation`, then `old_formula_invariant`). Examples: `[φ] ⊢ φ` holds on both sides; `[] ⊢ φ` holds on neither, with the empty relations as the countermodel to both (a Prop example and a `#guard` that computes it). `att_conservative_doc`: a `#guard` on F-AT0 (no condition, no part: no key, no frame, `envAtt` declares what `E` declares), on F-AT1 (the conditions make the keys, the frame and `envAtt` differ) and on `c_e_only` (C-e's part with no condition makes a key); and the theorem at F-AT0 | 0de99986bf, 693048ded9 | the examples and guards under "`att_old_language_conservative`" and "`att_conservative_doc`" |
| Statement gate | `docs/attitudes/at-1/spec_text_check.py` (at-1d's pattern, with the ` :=` anchor), for the eight statements and their docstrings | 0de99986bf | section "Spec re-read" |
| `lean/ATTITUDES.md` | at-1's row; the plan's "Done when" (attitudes-PLAN.md:1240, "lists every theorem in plain words"): a section listing the 27 statements of 6.1 | 8294a8da2e, 2d577d5fc4 | |
| Generated files (R12) | `regen_generated.py --write`: `wrote 38 entries` (the Lean inventories, `axioms.txt`, `VE/Audit.lean`, and codemap rows already stale on main) | 223ba4c085 | section "Runs" |

Not delivered: nothing. Kept out on purpose: `Frame.lean`, `Semantics.lean`, `Route.lean` and `Syntax.lean` are unchanged, because no proof
needed a change there. The tie is a side-table entry, so `Syntax.lean` has no edit. Also kept out: `lean/VE/NormDefaults/` (AT-2) and
`lean/VE/Compose/Dispatch.lean` (AT-3a).
Branch overlap: none of the in-flight `lean-first/*`, `feature/*`, `infra/*` or `foundation/*` branches touches `lean/VE/Attitudes`,
`lean/ATTITUDES.md` or `docs/attitudes/at-1`. Fourteen branches touch `tools/trust-classes.json`, a shared side table, but in other
modules' sections. This item's edits there are confined to the `VE/Attitudes/Examples.lean` and `VE/Attitudes/Syntax.lean` entries.

Helper lemmas (`Theorems.lean`):
- `keyOf_old`: a name `A.E` declares is no generated name.
- `denote_interp_of`, with `denote_interp_base` now its instance at `keyOf_base`.
- `tupleTyped_withRelation`, with `tupleTyped_interp` now its instance.
- `interp_name`: `interp` reads a key's name as `J`.
- `envAtt_name`, `term_interp`.
- `denote_withRelation`: relations that agree everywhere give every formula one meaning. This is the step from `T` to
  `interp A (restrict A T)` in the proof note's "other direction".

Three statements carry a hypothesis their proof does not read, and Lean's linter warns about it: `h` in `interp_admissible`,
`restrict_admissible` and `interp_restrict`, and `hT` in `interp_restrict`. Each is the spec's text, and removing one would change the
statement, so they stay.

## Spec re-read

- `python3 docs/attitudes/at-1/spec_text_check.py`: `8 statements, 0 missing, 8 of 8 found`, rc 0. It also fails in the other
  direction: `att_conservative_doc` without `(hp : A.parts = [])` gives `1 missing`, rc 1; `old_formula_invariant`'s conclusion with
  ` ∨ True` appended gives `1 missing`, rc 1 (the ` :=` anchor). The script is a substring match on the whitespace-normalised source,
  at-1d's pattern. A verbatim copy inside a comment, beside a different real declaration, would also pass; Lean's build and
  `lean/statements.txt` (the compiled statements) are the check on the real declaration.
- Statements checked against the spec text: `att_elaboration_faithful` :1276-1279 (with its docstring); `interp_admissible` :1284-1286 (with the
  docstring "Model correspondence, both ways."); `restrict_admissible` :1287-1288; `restrict_intended` :1289-1290; `interp_restrict`
  :1291-1293; `old_formula_invariant` :1294-1296; `att_old_language_conservative` :1303-1306; `att_conservative_doc` :1307-1310. No hypothesis was added
  or removed.
- 7.4's rows for the eight are all examples: `att_elaboration_faithful` (M1 true both ways, M4 false both ways, plus M2 and M3 for 7.5's
  M1-M4); `old_formula_invariant` (category true and false); `att_old_language_conservative` (`[φ] ⊢ φ`; `[] ⊢ φ` with the computed
  countermodel); `interp_restrict` (in `J`, not in `J`); `restrict_intended` (RM1 intended, RM2 not); `interp_admissible` (typed,
  untyped). 7.4's `restrict_intended` row names RM1 and RM2, which are finite models over generated names; the examples use
  `interp fat1 (M false [keyQ])` and `interp fat1 (M false [keyK, keyQ])`, whose relations equal RM1's and RM2's pointwise. Building
  `St RM1` would need `name fat1 keyQ` computed, and the kernel does not reduce `String.map` (at-1c's note on F-AT9).
- `WellFormedAtt fat1` is taken as a hypothesis, as in at-1d (the kernel does not reduce it); at-1d's `#guard WellFormedAtt fat1 && …`
  evaluates it.

## Seeded bugs and mutants

Each bug was planted and the file restored (`git status` clean after each). A mutant that breaks a proof in `Theorems.lean` stops lake
before `Examples.lean`. So, as in at-1d, `Theorems.lean` and `Examples.lean` were also elaborated as one scratch file (after
`lake build` of the mutated upstream module): there a failed proof stays a declaration and elaboration goes on, which shows the examples
that fail on their own. `docs/attitudes/at-1/mutants.json` lists each bug with its failing checks (line numbers as of this HEAD).
Only Lean product code changed (`Theorems.lean`); the planted bugs sit in the definitions the statements are about. No Python or Rust
product code changed (`spec_text_check.py` is evidence).

| Bug | File | Failing check |
|---|---|---|
| (task) `restrict` keeping a generated relation as an old one | `lean/VE/Attitudes/Semantics.lean` | `interp_restrict`'s example (`Examples.lean:1281`, at :1295); the `restrict_intended` (:1238) and `hT`-failing (:1264) examples; at-1c's restrict example (:986); the proofs of `restrict_admissible` (`Theorems.lean:898`) and `interp_restrict` (:907) |
| (task) `interp` reading `m.S` for a generated name | `Semantics.lean` | `atom_interp_M` (`Examples.lean:1194`), which `att_elaboration_faithful`'s example (:1200) reads M1-M4 with; at-1c's interp example (:979); the proofs of `interp_name` (:815), so `att_elaboration_faithful`, and of `denote_interp_of`, `interp_admissible`, `interp_restrict` |
| (task; the tied definition) `toFormula` swapping the holder and the slot | `lean/VE/Attitudes/Syntax.lean` | `guard1_elab` (`Examples.lean:1193`) and at-1b's `guard1F` `#guard` (:338); the proof of `att_elaboration_faithful` (`Theorems.lean:847`) |
| (task) `framePremises` non-empty on a document with no condition (`++ [.top]`) | `lean/VE/Attitudes/Frame.lean` | `att_conservative_doc`'s `#guard` (`Examples.lean:1315`) and at-1c's F-AT0 guard (:743); the proof of `att_conservative_doc` (`Theorems.lean:953`) |
| (new guard) `framePremises` unsatisfiable (`++ [.bottom]`) | `Frame.lean` | the conservativity countermodel's `#guard` (`Examples.lean:1310`), the `hT`-failing frame guard (:1262), and :1315 |
| `interp` dropping the old relations | `Semantics.lean` | `cat_interp` (`Examples.lean:1171`), which `old_formula_invariant`'s example (:1175) reads the `interp` side with; the `restrict_intended` refusing example (:1238); the proof of `denote_interp_of` (`Theorems.lean:624`) |
| (changed file) `att_conservative_doc` without `hp` | `lean/VE/Attitudes/Theorems.lean` | `spec_text_check.py`: `1 missing`, rc 1 |
| (changed file) `old_formula_invariant` with ` ∨ True` appended | `Theorems.lean` | `spec_text_check.py`: `1 missing`, rc 1 |

R16's per-definition mutants: none are due, because no trusted definition is new (`trust_map.py --check`: trusted -10). The tied
definition `AFormula.toFormula` has its mutant (the holder/slot swap), which breaks a named example and the proof.

## Trust

`uv run python tools/trust_map.py --check`: `against a3454b6ba598: K +0, S -10, D +10, G +0, tied +10, unclassified +0, trusted -10`;
`VE/Attitudes/Syntax.lean: trusted -10`; `PASS`. The theorems are class P. `Examples.lean`'s six new definitions (`allCat`, `ρ10`,
`guard1E`, `Mrev`, `catAt0`, `c_e_only`) are entered as class T.

**Row at-1b-tie, measured.** `AFormula.toFormula` (10 lines) moved from S to D[V], tied to `att_elaboration_faithful`
(reviews/dri-decisions-20261105-at-1b-trust.md item 3): `S -10, D +10, tied +10`.

The measured shortfalls, as that decision's item 3 asks each row to report. at-1b's baseline row (+165) already nets the at-1a-tie's
first half (`gross +180`, `-15`), and item 2 counts those 15 lines as at-1a's cut-back, not at-1b's, so they come off at-1a's row
only:
- at-1b's own trusted lines are +180 - 10 = +170, against 150: 20 over.
- at-1a's are +221 - 15 (at-1b's ties) - 7 (at-1c's `baseEnvAtt`) = +199, against 150: 49 over.
- In all, 69 lines stay above the two caps, against the decision's estimate of about 44; the difference is the about 25 lines of
  at-1a ties the estimate expected from at-1, not made (below). The decision signs that remainder as the spec's own check text and
  requires no further cut before merge, so no new signature is needed.

`tests/test_attitudes_at1_report.py::test_the_trust_shortfalls_are_the_measured_ones` recomputes these figures from the baseline rows
at 223ba4c085 and the tie move measured there by `trust_map.measure_rev` against a3454b6ba5. The first version of this report took the
15 lines off at-1b's row a second time (review F1), which put at-1b 15 lines too low and the total at 54;
`test_the_reviewed_report_text_with_the_tie_subtracted_twice_is_refused` keeps that text refused.

The ties the estimate expected from at-1 were not made:
- `Cond.key`, `AFormula.conds`, `condsOf` and `partsOf`, the FOLLOW-UPS at-1a row's "about 25". No 6.1 statement states their
  properties. `condsOf` appears only as `att_conservative_doc`'s hypothesis `condsOf A = []`, and `Cond.key` only as
  `guard_collapse`'s hypotheses. A `condsOf` that always answered `[]` would leave `att_conservative_doc` true, so tying to it would
  take unpinned lines out of reading. That is the reason the decision gave for `toNorms` (item 3).
- `AttModel`, `contentAt`, `Intended`, `AFormula.denote`, `interp`, `restrict` and `seedClosure` (Semantics.lean S, from the FOLLOW-UPS
  at-1c row) also stay S. This task names only row at-1b-tie's move, and these definitions are what the eight statements are about.
  `AFormula.denote` is the other side of `att_elaboration_faithful`, the theorem `toFormula` is tied to, so tying both to it would pin
  neither. Whether `interp` and `restrict` tie to the correspondence theorems is the ties pass's question (FOLLOW-UPS rows at-1a and
  at-1c stay open).

DELTA: none. `grep -rln VE.Attitudes lean/VE/Service lean/VE/Route lean/Main.lean ve/` lists no file, so no route reads these modules.
No verdict, wording or route changed.

## Size

`git diff --numstat a3454b6ba5`, without generated files (codemap, the Lean inventories, `axioms.txt`, `VE/Audit.lean`) and the
tool-written `trust-mutants.json`:

| Commit | Lines (added, changed) | What it holds |
|---|---|---|
| 0de99986bf | 219, 10 | all eight proofs and helpers (`Theorems.lean` +177 -10), `spec_text_check.py` 42 |
| fc9c1eb496 | 278, 12 | (1)'s examples (+49) and the tie (`trust-classes.json`) |
| 693048ded9 | 369, 12 | (2)'s and (3)'s examples (+80), `interp_name`, `envAtt_name` |
| 8294a8da2e | 381, 15 | `mutants.json`, ATTITUDES.md's row |
| 2d577d5fc4 (final code) | 459, 15 | the self-review's fixes: the `hT`-failing refusals, direct reads, the plain-words list (+41) |

Per file at the final code: `Theorems.lean` +186 -10; `Examples.lean` +164; `ATTITUDES.md` +44 -3; `spec_text_check.py` 42;
`mutants.json` 10; `trust-classes.json` +13 -2. With this report, at 36a5944147, the total is 667 added and 15 changed, under the
expected 700-1,000 (the first version said "about 610", review F4). The review fixes add `tests/test_attitudes_at1_report.py`, which
recomputes every sized row and that total from `git diff --numstat` of the pinned commits, without the files a generator writes
(`tools/regen_generated.py`, merge kind `regenerate`) and `trust-mutants.json`; `trust-classes.json` (merge kind `json`) counts. The proofs and
helper lemmas came to about 180, under the 400-600 estimate, because at-1d's helpers carried the load. The examples and guards came to
about 165.

Order deviation: the task asked to measure the size after (1) and again after (2), so the ~700 seam could cut (3) away. All eight proofs
went in one commit (0de99986bf) before any example, because they share their helper lemmas. So no commit holds (1) alone or (1) and (2)
alone, and the seam could not fire at the points the task names. at-1b-size item 2 warned about this ordering. The outcome is the one
the seam guards: the whole item, (3) included, is about 460 lines of code and evidence against the ~700 seam, so (3) stays and there is
no at-1e.

## Pilot bytes

None expected: this is a structure row (bytes 0), and the content stays a named open residual.

## Runs

- `lake build` (full, at the final code with the regenerated `Audit.lean`): `Build completed successfully (1358 jobs)`.
  `python3 lean/audit.py`: `PASS: 825 source files; 9313 named theorem declarations audited … only the declared standard axiom
  allowlist`. `lean/axioms.txt`: the eight statements and their helpers use at most `propext`, `Classical.choice` and `Quot.sound`.
  `denote_withRelation` and `tupleTyped_withRelation` use none. No `sorry`.
- `uv run python tools/regen_generated.py --write`: `wrote 38 entries`. `uv run python tools/lean_statements.py` after it: `added: 0,
  removed: 0, changed: 0`.
- `uv run python tools/trust_map.py --check`: PASS (section "Trust").
- `python3 -I manage-agents/tools-local/light-lane.py check`: `NOT` (`Theorems.lean` and `VE/Audit.lean` are not in
  `tools/trust-classes.json`, and the side table changed), so the sweep ran:
  `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/attitudes/at-1/trust-mutants.json`, on ve-cloud-2 at
  223ba4c0 (the final Lean): `0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED, 0 NOT RUN`, exit 0.
  No trusted declaration's text changed, so none was selected.
- Selected tests, once, on the committed tree 5efe1a8d5e (clean): `MAC_PYTEST_NO_DEFER=1 zsh manage-agents/mac-pytest.sh --select --
  --base a3454b6ba5 --run`: `104/580 test units`; it ran on GitHub Actions in 5 shards (run at-1-5efe1a8d-t328250): `SHARD 1/5 … 28
  units, 28 passed`, `2/5 … 23 passed`, `3/5 … 21 passed`, `4/5 … 19 passed`, `5/5 … 20 passed`, `0 failed` in each; `exit=0; 2208s`.
  Each shard also ran its commands (`lake build`, `python3 lean/audit.py`, `tools/check_lean_imports.py`, `tools/test_layer_policy.py`),
  all exit 0. Only this report changed after the run.
- Not run here: the full gate (the chain runs it). No test in main-known-red.txt was touched.

SELF-REVIEW: 0 A, 5 B, 4 C; fixed 9. The five B: the `hT`-failing refusal for `restrict_intended`, a mutant for the conservativity
`#guard`, ATTITUDES.md's plain-words list, the trust shortfalls in this report, and the per-commit size. The four C: direct reads on
both sides of `old_formula_invariant` and `interp_restrict`; the RM1/RM2 note; `restrict_admissible`'s refusal (`catAt0`); and the
line numbers regenerated after the fixes, with the method stated above and the gate script's limit noted in "Spec re-read".

## Review fixes

The final review of 36a5944147 (one A, five C):
- F1 (A): the trust shortfalls took the at-1a-tie's 15 lines off at-1b's row a second time. Fixed in section "Trust" (at-1b 170,
  20 over; at-1a 199, 49 over; 69 in all). The class is a report figure typed by hand: `tests/test_attitudes_at1_report.py` now
  recomputes the shortfalls (`test_the_trust_shortfalls_are_the_measured_ones`) and every sized row and the total of section "Size"
  (`test_the_sizes_are_the_measured_ones`) from pinned trees. The reviewed text stays refused
  (`test_the_reviewed_report_text_with_the_tie_subtracted_twice_is_refused`, `test_the_reviewed_report_total_of_about_610_is_refused`).
  The review's probe: rc 1 before, rc 0 after. No verdict, binding, trusted code or signature changes: item 3 of the -trust decision
  signs the remainder with no further cut, so there is still no DELTA row.
- F4 and F5 (C), same class and file: the total is the measured 667 (section "Size"), and the opening summary is 4 lines.
- F2, F3 and F6 (C): unchanged. F3 is for the ties pass; F6 is the order deviation already stated in "Size".

Seeded bugs: no Lean, Python or Rust product code changed. Text mutants of the fixed report (an "over" figure, at-1b's total, the sum,
a size row, the total, an unpinned commit) each make the test fail; the reviewed head's text fails it too.
Runs on 532697c845: selected tests `100/581 test units`, 2 shards on GitHub Actions (run at-1-532697c8-t336114), 55 and 45 passed,
exit 0; `lake build`: `Build completed successfully (1358 jobs)`; `python3 lean/audit.py`: PASS. Not run: the full gate (the chain
runs it), and trust mutants (no Lean changed). No test in main-known-red.txt was touched.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed, and no service mode, schema or relay changed (the grep in "Trust").
2. PASS: "Deliverables" gives each task line with its commit and check. `git diff --stat a3454b6ba5 -- tests ve 'tools/*.py'` is
   empty at the reviewed head, so there is no Python copy of a Lean decision. The review fixes add one report test,
   `tests/test_attitudes_at1_report.py`, which reads only pinned commits. No in-flight branch touches these files.
3. PASS: `docs/attitudes/at-1/mutants.json` has 8 mutants, each failing a named guard, example, proof or the statement gate.
   `trust-mutants.json` has 0 mutants, because no trusted declaration's text changed.
4. N.A.: Lean only, read by no route; no Python or Rust product code changed.
5. N.A.: no relayed field.
6. N.A. here: the chain gates the final HEAD; `trust-mutants.json` names 223ba4c0, whose Lean equals HEAD's.
7. PASS: no DELTA row, no signature reserved, trusted -10 (`trust_map.py --check`).
8. PASS: no user-visible output changes (theorems, fixtures and a trust-class move; the route grep).
9. PASS: the selected run in "Runs", through `mac-pytest.sh --select`.
10. PASS: `spec_text_check.py` checks every statement verbatim and fails on a removed hypothesis or appended text. Each proof depends
    on the definitions it claims: each seeded bug breaks a proof or an example that reads the definition directly.
11. N.A.: no evaluator, budget or deadline; nothing runs these definitions on a route.
12. N.A.: no runtime path changes.
13. PASS: no test removed or renamed. at-1d's `denote_interp_base` and `tupleTyped_interp` keep their names and statements, and only
    their proofs became one-line instances.
14. PASS, both directions, for each iff and each hypothesis:
    - `att_elaboration_faithful`: M1 and M2 true, M3 and M4 false.
    - `old_formula_invariant`: true and false.
    - `interp_restrict`: in `J` and not in `J`.
    - `restrict_intended`: intended, then refused when `hX` fails and when `hT` fails.
    - `interp_admissible`: admissible and not.
    - `restrict_admissible`: admissible and not.
    - Conservativity: entailed on both sides and refuted on both.
    - `att_conservative_doc`: empty, and non-empty through a condition or a part.
    The spec re-read is in section "Spec re-read".
15. PASS, the four classes. Overclaim: "no route reads" rests on the grep, and "verbatim" on `spec_text_check.py`. No silent cut:
    (1)-(3) are all built, and the order deviation is stated in "Size". Every check can fail: `mutants.json` has a mutant for each new
    `#guard` (:1262, :1310, :1315) and for each claimed behaviour. Limits before work: N.A., no evaluator.
