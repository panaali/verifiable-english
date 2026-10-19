# speed-trustmut: mechanical mutants of new trusted Lean definitions

Infra item speed-trustmut (acting DRI dri-improve, 2026-10-18 16Z; PIPELINE-LIMITS L77). Trust +0: no Lean file
changes. The tool is `tools/trust_mutants.py`; the step-1 replay script is `docs/speed/trustmut/replay.py` and its
saved evidence `docs/speed/trustmut/evidence/<head>.json` (D4: saved, never recomputed from a live diff).

## 1. Measure: would the tool have flagged the six B findings?

The operators (`OPERATORS` in the tool), applied inside the compiled range of each trusted definition the branch
adds or changes, comments and strings excluded; a definition the base already has is mutated on its changed lines
only:

| Operator | What it plants |
|---|---|
| `arm-true`, `arm-false`, `arm-default` | each pattern-match arm's result -> `True`/`False` (`true`/`false` for Bool), or the catch-all arm's result |
| `body-true`, `body-false` | a Prop or Bool definition's body -> a constant |
| `not-drop` | a `¬` or prefix `!` dropped |
| `and-or`, `or-and` | `∧`/`∨` and `&&`/`\|\|` swapped |
| `lt-le`, `le-lt`, `lt-eq`, `le-eq`, `eq-le`, `eq-ne`, `ne-eq` | `<`, `≤`, `=` (and `==`, `!=`, `≠`) swapped (the first replays' `>`/`≥` swaps are gone: no finding needed them) |
| `lit-plus`, `lit-minus` | a numeric literal ±1 |
| `bool-flip` | a `true`/`false`/`True`/`False` literal flipped |
| `all-any`, `any-all` | `.all` and `.any` swapped |
| `list-empty`, `list-first`, `list-last`, `list-drop-first`, `list-drop-last` | a list -> `[]`, its first element only, its last only, without its first, without its last. A list is a list method's receiver or result, a `for … in` range, an operand of `++`, a list literal, or a `List`-typed body |
| `append-left`, `append-right` | each operand of `++` dropped |

A mutant Lean refuses inside the mutated declaration is INVALID: the compiler decides what a mutant means, never
the text. A check is a `#guard`/`#guard_msgs`, or an `example` or theorem proved by `decide`/`native_decide`/`rfl`
(`classify` in the tool, the one rule every module goes through). Every other `example` or theorem is a proof,
whatever its statement names: a failing proof is cut to `sorry` and the build repeated, so it is never a kill
(BUILDER-CHECKLIST 3; pk-1's `assemble_wellFormed`). The modules built for a mutant are those of the mutated
module's directory that hold checks, and any module of its cone holding a check whose compiled statement
(`lean/statements.txt`, `-- uses`) names the definition.

Review fix F1: the first tool also counted every `example` as a check, and a tactic-proved theorem outside the
mutated module whose statement names the definition. Those kills were broken proof scripts (pk-1's M028,
`X := []`, left `assemble_wellFormed` true and only broke its tactics). With the one rule above, 77 former kills
are no longer kills: pk-1 21 at `PacksLegacy.lean` now SURVIVOR and 5 at `LayeredAdmission.lean` now UNKNOWN (with
those proofs cut, a proof term inside the `def` at `Readings/UnspecifiedWire.lean:526` fails; it cannot be cut, so
the tool fails closed); qt-a1 16 at `Cardinality/Theorems.lean` and 35 at the tactic-proved `example`s of
`Cardinality/Examples.lean`, so no qt-a1 mutant is killed: its definitions are exercised by proofs only, which is
its finding. The ap-2 counts are unchanged. Every kill left is at a `#guard` or an `rfl` theorem
(`Packs.lean:117`).

Replays on the reviewed HEADs, every mutant run (`replay.py --run`, 8 jobs on the VM, base = the branch's merge
base with main). "Survivors on the named lines" are survivors on a line the review names for that finding;
"within the default 60" says whether one of them is among the first 60 mutants of the tool's order:

| Finding | HEAD | Mutants (run / survivors / invalid / unknown) | Seconds at 8 jobs | Survivors on the named lines | Flagged | Within the default 60 |
|---|---|---|---|---|---|---|
| pk-1 F1 | `6b58a0ff7` | 248 / 91 / 35 / 5 | 873 | 10: `Packs.lean:423` list-empty; `Packs.lean:423` list-first; `Packs.lean:423` list-drop-last; `Packs.lean:423` list-last; `Packs.lean:423` list-drop-first | yes | yes |
| qt-a1 F1 | `b20a8e306` | 140 / 133 / 7 / 0 | 299 | 43: `Semantics.lean:24` arm-true; `Semantics.lean:52` arm-true; `Semantics.lean:24` arm-false; `Semantics.lean:52` arm-false; `Semantics.lean:14` not-drop; `Semantics.lean:55` not-drop ... | yes | yes |
| ap-2 F1 | `584ac3bb3` | 413 / 117 / 21 / 0 | 466 | 29: `Syntax.lean:80` lt-le; `Read.lean:19` lit-plus; `Read.lean:19` lit-minus; `Syntax.lean:80` lit-minus; `Syntax.lean:119` any-all; `Syntax.lean:119` list-empty ... | yes | yes |
| ap-2 F7 | `e13a4e413` | 413 / 59 / 21 / 0 | 280 | 18: `Syntax.lean:119` any-all; `Syntax.lean:83` list-first; `Syntax.lean:96` list-first; `Syntax.lean:113` list-first; `Syntax.lean:113` list-drop-last; `Syntax.lean:119` list-first ... | yes | yes |
| ap-2 F10 | `3d1085285` | 413 / 35 / 21 / 0 | 316 | 4: `Syntax.lean:78` list-first; `Syntax.lean:78` list-last; `Syntax.lean:79` list-last | yes | no |
| ap-2 F11 | `aa2fd56e3` | 413 / 33 / 21 / 0 | 485 | 6: `Syntax.lean:88` list-drop-last; `Syntax.lean:122` list-first; `Syntax.lean:122` list-drop-last; `Syntax.lean:89` list-drop-first; `Syntax.lean:121` list-last; `Syntax.lean:121` list-drop-first | yes | no |

Exact reviewer mutants among the survivors (the rest of each finding's survivors are the same class on its lines):
- pk-1 F1: `coherenceLabels := []` (M035, list-empty), and `X := []` (M028, this item's review F1). `fullEnv := envAt (fill U) 0` is outside the operators
  (an argument replaced by `0`); one survivor per finding is enough, so this is a follow-up.
- qt-a1 F1: `.eq` read as `≤` (eq-le, `Semantics.lean:26`), `.lt` read as `≤` (`:24`), the `¬` of `Body.holds`
  dropped (`:14`), `.or` read as `∧` (`:16`), each `Cmp.holds` case (`:32`–`:34`), `.quantity` read as `True`
  (`:52`), the `.not`, `.and`, `.or` and `.implies` cases (`:55`–`:58`), and `WellFormed.fresh` reversed
  (bool-flip, `Syntax.lean:70`). The three `Admitted` premises (`Syntax.lean:86`, `:88`, `:91`: a premise dropped)
  are outside the operators.
- ap-2 F1: `128 ≤` (lt-le, `Syntax.lean:80`) and the step budget (lit-plus/lit-minus, `Read.lean:19`); the 31r
  head-word half by `.any` read as `.all` (`:119`). `mresv` for `resv`, `wordOk` without `actWord` and the fault
  order are outside the operators.
- ap-2 F7: 31c on the first head word only (`(f.head.take 1)`, `:83`) and 31r on the first head word only
  (`(fun x_tm => (x_tm.head.take 1)`, `:119`). The marker-list swaps (31o, 31i) and 31g's `""` filter are outside.
- ap-2 F10: `ms` keeping only the first modifier marker (`(f.mods.take 1)`, `:78`).
- ap-2 F11: all four: `(fs.drop 1).find?` (`:89`), `for f in fs.dropLast` (`:88`), `for f in fs.drop 1`
  (`:121`) and `f.head.dropLast.head?` (`:122`).

Result: the tool flags all 6 of the 6 findings (stop rule: at least 3), so steps 2 and 3 follow. At the default
`--max-mutants 60` it flags 4: ap-2 has 413 mutants, and its F10 and F11 survivors are tier-2 and tier-3 list cuts,
so they print as NOT RUN and the run exits 3 (incomplete) until it is rerun with a larger `--max-mutants`.

Times (the "Seconds" column, measured with the final tool after the F1 fix, 8 jobs on the 32-core VM while other
work ran): every replay is within the 20-minute budget. qt-a1 took 299 s, the four ap-2 HEADs 280–485 s (5-minute
load up to 30), and pk-1 873 s (5-minute load 14–22; 1,142 s at load 30–41 before the fix): its mutated modules (`Packs.lean`, `PacksLegacy.lean`) are proof-heavy. A first pk-1 run that built
every check module importing the mutated one, not only those of its directory, was stopped after an hour at load
51; that is why `--deep` is opt-in.

## 2. Orchestrator lines (not edited here: /home/seyran/code/manage-agents is the orchestrator's)

For `BUILDER-CHECKLIST.md` (under item 3) and `prompts/build-checklist.txt` (a new line after 13):

> For trusted Lean growth under R16, run `uv run python tools/trust_mutants.py --max-mutants 1000 --json
> docs/<batch>/trust-mutants.json` on the final Lean change; fix (a guard that kills it) or `--allow` (one line: why
> the mutant is equivalent) every SURVIVOR and UNKNOWN until it exits 0, and commit the evidence JSON and the allow
> file. Exit 3 means mutants were NOT RUN: raise `--max-mutants`.

For the review prompt (R16 rows):

> Rerun `uv run python tools/trust_mutants.py --max-mutants 1000` on the HEAD and compare with the committed
> evidence; plant hand mutants only beyond its operators (`OPERATORS` in the tool: for example a premise dropped, an
> argument replaced by a constant, a list swapped for a sibling list, or a check that lives outside the mutated
> module's directory, which only `--deep` builds).

A later gate check: not yet worth it, in my view. The tool's verdicts depend on which checks it builds (the
mutated module's directory by default), so a survivor can be a false one that `--deep` or `--test` resolves, and an
equivalent mutant needs a human reason; both are review judgements. A cheap check worth considering after a few
items have used it: when trust_map reports trusted growth, the committed `trust-mutants.json` names the final
HEAD's Lean tree and lists no SURVIVOR or UNKNOWN outside the allow file (reading saved evidence, no rerun). That is a
DRI decision; nothing here adds it.

## 3. Tests and seeded bugs

`tests/test_trust_mutants.py` builds a four-module Lean package under `tmp_path` (its declaration and predicate
lists written by `tools/lean_statements.py`'s own per-module script, its `lean/statements.txt` by that tool's
statement script) and runs the tool on it with `TMPDIR` in
`tmp_path` and `VE_LEAN_SHARE=off`; one test checks the generator and one the check rule (`classify`) alone, without Lean. Each rule has a seeded bug
in `docs/speed/trustmut/mutants.json` (the `tools/mutants.py` format); `uv run python tools/mutants.py
docs/speed/trustmut/mutants.json` kills 10 of 10, each at its named test, the file restored to its exact bytes
(`mutants-evidence.json`). Python is the only language whose code changed (no Lean, no Rust).

| Mutant | Rule | Bug planted in `tools/trust_mutants.py` | Failing test |
|---|---|---|---|
| TM1 | a failing proof is no kill | a `proof` error counts as a kill | `test_a_failing_proof_is_no_kill` |
| TM2 | the importing check modules are built | the second build stage is empty | `test_a_well_guarded_definition_has_no_survivor` |
| TM3 | a guard over `[]` leaves a survivor | `list-empty` leaves the list unchanged | `test_a_guard_over_the_empty_list_leaves_survivors` |
| TM4 | `--allow` suppresses exactly its operator | any operator of the definition is allowed | `test_allow_suppresses_exactly_its_operator` |
| TM5 | a scratch copy is used | the scratch sources are hard links to the checkout | `test_mutants_are_built_in_a_scratch_copy` |
| TM6 | the rest are listed as NOT RUN | only the first NOT RUN row prints | `test_max_mutants_lists_the_rest_as_not_run` |
| TM7 | every list method's receiver is cut | `find?` unescaped in `LIST_METHODS` (a real regression of the rewrite, caught by the ap-2 replays) | `test_the_generator_cuts_every_list_a_condition_reads` |
| TM8 | an `example` is a check only when `decide`/`native_decide`/`rfl` proves it (review F1) | every `example` is a check | `test_an_example_proved_by_a_tactic_is_no_kill` |
| TM9 | a tactic-proved theorem whose statement names the definition is a proof (review F1) | it is a check outside the mutated module (the first tool's rule) | `test_a_failing_proof_is_no_kill` |
| TM10 | a check outside the directory whose statement names the definition is built | only the directory's checks are built | `test_a_decide_check_outside_the_directory_naming_the_definition_kills` |

## 4. Limits and follow-ups

- Outside the operators (step 1 shows each needs a reviewer today): a premise or conjunct dropped (qt-a1's
  `Admitted`), an argument replaced by a constant (pk-1's `fullEnv`), one list swapped for a sibling list (ap-2 F7's
  31o and 31i), a reserved list swapped for another (`mresv`), fault order. Follow-up: add them where step 1 says.
- The mutation sites are found on the blanked text, not by Lean; Lean decides each mutant (INVALID when it does not
  elaborate), so a site misread costs a build, never a verdict. 21–35 of each replay's mutants are INVALID.
- Checks are built from the mutated module's directory by default; a check elsewhere that does exercise the
  definition is reached only by `--deep`, `--test` or a check whose statement names it. A survivor may therefore
  be false (fail closed), never a kill.
- A tactic-proved `example` or theorem never kills, even when the mutant makes its statement false: the tool cannot
  tell that from a proof script that breaks on a true statement (review F1), so such a definition shows survivors
  until a `#guard` or a `decide`/`rfl` check reads it (qt-a1: 133 survivors, no kill).
- A proof term inside a definition (not a theorem or `example`) that fails cannot be cut, so the mutant is UNKNOWN
  (pk-1: 5, at `Readings/UnspecifiedWire.lean:526`).
- Equivalent mutants (for example `.take 1` of a list that always has one element) are not detected; they go in the
  allow file with a reason.

## 5. Task lines and where they are delivered

| Task line | Delivered by |
|---|---|
| 1 MEASURE: operators first, replays on pk-1 6b58a0ff, qt-a1 b20a8e30, ap-2 584ac3bb and the recheck HEADs; table; stop rule | section 1; `replay.py`, `evidence/*.json`; 6 of 6 flagged |
| 2 `tools/trust_mutants.py`: `--base`, trust_map classification ∩ diff, scratch copy with lean_share's build, only importing check modules plus `--test`, kill rule, SURVIVOR line, `--allow`, `--jobs`, `--max-mutants` with NOT RUN, `--json`, time budget | the tool; times in section 1 |
| 3 tests in a new `tests/test_trust_mutants.py` (six behaviours) and one seeded bug per rule | section 3; 23 tests; TM1–TM10 |
| 4 orchestrator lines, gate-check opinion | section 2 |
| Rules: R2/R3 unchanged, nothing reads the tool; `trust_map.py --check`, review-ready and gate unchanged; no timing test | `DELTA.md`; no file of the gate, trust_map or review-ready changed; the tests assert no time |
| Trust +0; DELTA rows only with a ruling, none reserved | `DELTA.md` has no rows |
| Size: at most ~500 changed lines outside generated files | over: see below |

Size: about 1,160 changed lines outside the generated `tests/history-dependent.json` and the saved evidence
(`evidence/*.json`, `mutants-evidence.json`): `tools/trust_mutants.py` 510, the test 257, `replay.py` 94, the
seeded bugs' `mutants.json` 104, this report and DELTA about 195. That is about twice the guideline. The size rule's
fallback is to deliver steps 1-3 for the operators step 1 showed matter; every operator but `arm-default`,
`body-true`/`body-false`, `ne-eq`, `all-any` and `append-*` left a survivor on a finding's line, and removing those
saves under 20 lines, so all are kept. The bulk is the runner the task asks for (selection, scratch copies with
the shared build, staged builds, proof cuts, the kill rule), and splitting it would leave no usable tool.

## 6. Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; the tool reads Lake's build log, and a failure it cannot place is UNKNOWN.
2. PASS: section 5 maps every task line to its delivery; no rule break (no product code, no permanent report
   test: `replay.py` reads saved evidence, D4).
3. PASS: seeded bugs TM1–TM10 (`mutants.json`, `mutants-evidence.json`), each failing only its named test;
   `--allow` names an exact (definition, operator) pair (`test_allow_suppresses_exactly_its_operator`).
4. N.A.: no Python, Lean or Rust product code changed.
5. N.A.: no relayed field.
6. PASS: synced with main (cb033316a) before the final runs; the chain runs the gate on the final HEAD.
7. PASS: DELTA has no rows and reserves nothing; trust +0 (no Lean file changed).
8. PASS: `git diff --stat main...HEAD -- ve lean rust conformance` is empty.
9. PASS: `tools/select_tests.py` selects 24 units, `tests/test_trust_mutants.py` among them
   (`repo_map.py file tools/trust_mutants.py`).
10. N.A.: no Lean statement or proof.
11. PASS: `--max-mutants 0` runs nothing and exits 3, never 0 (`test_max_mutants_lists_the_rest_as_not_run[0]`).
12. N.A.: no product code; the tool's own times are in section 1.
13. N.A.: no test removed or renamed; `tools/gate_collection.py --check --prebuilt`: 23 added, 0 refused, 0 stale,
    0 malformed.
