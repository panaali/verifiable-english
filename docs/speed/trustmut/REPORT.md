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

Every edit keeps each line after its declaration where it was (`relined`, review F9, section 1c), so the proof
cuts and the roles, which read the checkout's line numbers, read the mutated text right. A check is a command whose
outcome Lean computes from definitions alone, never from a proof (`classify` in the tool, the one rule every module
goes through): `#guard`, `#guard_expr`, `#eval`, `#reduce`, `#check`, or an `example` or theorem proved by
`decide`/`native_decide`/`rfl`, with no other tactic block in it and no binder before its colon; a
`#guard_msgs … in` is the command it wraps, bare or with its docstring. Every other `example` or theorem is a proof,
whatever its statement names, and so are a check form with a tactic block inside and every `#print` (`#print axioms`
included). A proof that fails is cut to `sorry` (a `#` command blanked, with its docstring) and the build repeated
before any other error is read, so it is never a kill (BUILDER-CHECKLIST 3; pk-1's `assemble_wellFormed`); since
F11 nothing is cut up front. Since review F11 each verdict that counts for nothing has one positive condition and
everything else is UNKNOWN (section 1e): KILLED only when every error is a check's own refutation (a message that
states one, at a line the checkout has there, of a statement Lean elaborates as without the mutant and computes
through no proof the mutant broke), and the build without the mutant passes (section 1a); INVALID only when every
error in the mutated declaration is Lean refusing the text the mutant wrote. An error in a definition, even beside
a failing check (section 1b), a parse error at a check (section 1c) and a check out of budget (section 1d) are
UNKNOWN. The modules built for a mutant are those of the mutated module's directory that hold checks, and any
module of its cone holding a check whose compiled statement (`lean/statements.txt`, `-- uses`) names the
definition.

Review fix F1: the first tool also counted every `example` as a check, and a tactic-proved theorem outside the
mutated module whose statement names the definition. Those kills were broken proof scripts (pk-1's M028,
`X := []`, left `assemble_wellFormed` true and only broke its tactics). With the one rule above, 77 former kills
are no longer kills: pk-1 21 at `PacksLegacy.lean` now SURVIVOR and 5 at `LayeredAdmission.lean` now UNKNOWN (with
those proofs cut, a proof term inside the `def` at `Readings/UnspecifiedWire.lean:526` fails; it cannot be cut, so
the tool fails closed); qt-a1 16 at `Cardinality/Theorems.lean` and 35 at the tactic-proved `example`s of
`Cardinality/Examples.lean`, so no qt-a1 mutant is killed: its definitions are exercised by proofs only, which is
its finding. The ap-2 counts are unchanged. Every kill left is at a `#guard` or an `rfl` theorem
(`Packs.lean:117`).

Review fix F6 (same class): `#guard_msgs in` on its own line was its own one-line command, which the rule called a
check, and Lean reports a wrapped proof's failure at that line, so a broken tactic proof under it killed. Now
`tools/trust_map.py` opens a command at the `#guard_msgs … in` line before it, as at `set_option … in` (its span is
what it wraps), `classify` decides by the wrapped command, and a cut proof loses its wrapper (the `sorry` warning
would fail it) but keeps the comments after it (a docstring there belongs to the next command, and a
`#guard_msgs` reads its docstring). No `.lean` file at this HEAD or at any of the six replay HEADs has a
`#guard_msgs`, and the cut only keeps comment text the source already had, so the replays below stand as run.

Replays on the reviewed HEADs, every mutant run (`replay.py --run`, 8 jobs on the VM, base = the branch's merge
base with main), rerun with the tool after review fix F8: every mutant's verdict and kill line is the same as
in the F1 round's evidence (and in the F7 round's) (compared by mutant id). Review fix F9 changes none of them, so
they were not rerun: `replay.py` checks the saved evidence against F9's two new rules and prints "0 mutants change
their line count, 0 kills are parse errors" (every kill is a `#guard`'s "Expression … did not evaluate to `true`"
but one `rfl` theorem's "Not a definitional equality"), and `relined` only changes an edit that adds lines.
Review fix F10 changes none of them either: `replay.py` checks the saved evidence against its rule and prints
"0 kills or INVALID gave no answer; the kills: 1440 'Expression', 1 'Not a definitional equality:'" (section 1d).
Review fixes F11/F12 (section 1e) were replayed on ap-2 F11 (`aa2fd56e3`) with the final tool: all 359 kills and
33 survivors are the same mutants as before; 12 former INVALID are now UNKNOWN (a refusal outside the text the
mutant wrote, or not one of `REFUSED`: "Invalid field notation: Type of … is not known" at a later line, "failed to
synthesize", "don't know how to synthesize", "Type mismatch", "Unknown identifier `A`" outside the edit). The
other five replays were not rerun on the final tool (each probe of a kill adds an elaboration, and the DRI's
addendum of 23Z asks to end the round): their kills are all `#guard`s and one `rfl`
theorem, the forms the replay shows unchanged, and their INVALID counts would move to UNKNOWN the same way, which
counts toward the exit code (fail closed). "Survivors on the named lines" are survivors on a line the
review names for that finding; "within the default 60" says whether one of them is among the first 60 mutants of
the tool's order:

| Finding | HEAD | Mutants (run / survivors / invalid / unknown) | Seconds at 8 jobs | Survivors on the named lines | Flagged | Within the default 60 |
|---|---|---|---|---|---|---|
| pk-1 F1 | `6b58a0ff7` | 248 / 91 / 35 / 5 | 1027 | 10: `Packs.lean:423` list-empty; `Packs.lean:423` list-first; `Packs.lean:423` list-drop-last; `Packs.lean:423` list-last; `Packs.lean:423` list-drop-first | yes | yes |
| qt-a1 F1 | `b20a8e306` | 140 / 133 / 7 / 0 | 231 | 43: `Semantics.lean:24` arm-true; `Semantics.lean:52` arm-true; `Semantics.lean:24` arm-false; `Semantics.lean:52` arm-false; `Semantics.lean:14` not-drop; `Semantics.lean:55` not-drop ... | yes | yes |
| ap-2 F1 | `584ac3bb3` | 413 / 117 / 21 / 0 | 327 | 29: `Syntax.lean:80` lt-le; `Read.lean:19` lit-plus; `Read.lean:19` lit-minus; `Syntax.lean:80` lit-minus; `Syntax.lean:119` any-all; `Syntax.lean:119` list-empty ... | yes | yes |
| ap-2 F7 | `e13a4e413` | 413 / 59 / 21 / 0 | 372 | 18: `Syntax.lean:119` any-all; `Syntax.lean:83` list-first; `Syntax.lean:96` list-first; `Syntax.lean:113` list-first; `Syntax.lean:113` list-drop-last; `Syntax.lean:119` list-first ... | yes | yes |
| ap-2 F10 | `3d1085285` | 413 / 35 / 21 / 0 | 300 | 4: `Syntax.lean:78` list-first; `Syntax.lean:78` list-last; `Syntax.lean:79` list-last | yes | no |
| ap-2 F11 | `aa2fd56e3` | 413 / 33 / 9 / 12 | 1917 | 6: `Syntax.lean:88` list-drop-last; `Syntax.lean:122` list-first; `Syntax.lean:122` list-drop-last; `Syntax.lean:89` list-drop-first; `Syntax.lean:121` list-last; `Syntax.lean:121` list-drop-first | yes | no |

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

Times (the "Seconds" column, 8 jobs on the 32-core VM while other work ran). `replay.py` prints, from the saved
evidence (review F14: this report quotes it and claims nothing of its own about the budget):

> Step 1's budget (1200 s a replay): 5 of 6 replays within it; over it: ap-2 F11 1917 s (final tool). On the final tool 0 of 1 within it.
> Profiled replays: ap-2 F11 1917 s at 8 jobs, tool be422c2d3, 5-minute load 39-65 (mean 52.1); thread seconds: probe 9314, builds 5434 (the probe 63% of the two).

So the task's 20-minute budget is **not met**. The DRI's note of 2026-10-20 asked for one more ap-2 F11 replay at 8 jobs:
ap-2 F11 took 1,917 s with the final tool, at the 5-minute load the profile line gives (the
VM was not quiet), and every one of the 413 mutants has the verdict and detail of the F11 round's run (where ap-2 F11 took 1,546 s). The
probe of section 1e causes the excess: the threads spent 9,314 s in it against 5,434 s in builds, so at 8 jobs it
is about 1,160 s of the 1,917, and the builds alone about 680 s. It elaborates each kill's check module once more in
the mutant's build (359 kills here), which the five other replays, run with the F8 tool, did not do. No speed fix
was made: every way to probe less (once per module instead of per mutant, or not for some kills) changes what a kill
rests on, which needs a hunt, and the note bounds the round. A waiver of the budget, or a faster probe, is the
DRI's decision (escalated in `reviews/escalations-20261020.md`). With the F8 tool qt-a1 took 231 s, the four ap-2
HEADs 276–372 s (ap-2 F11 276 s), and pk-1 1027 s: its mutated modules (`Packs.lean`, `PacksLegacy.lean`) are
proof-heavy. The F7 round, which added the control builds of section 1a, measured 222 s, 255–275 s and 733 s, and
the F1 round 299 s, 280–485 s and 873 s, so the controls add no time these runs could measure (no check there fails
without the mutant, so each control is built once per stage and set of cuts, and cached). A first pk-1 run that
built every check module importing the mutated one, not only those of its directory, was stopped after an hour;
that is why `--deep` is opt-in.

## 1a. Review fix F7: a check whose outcome a proof can change never kills

F7 was the third form of one class (F1, F6, F7): a command counted as a check while its outcome depends on a
proof that the mutant breaks or that the tool cuts to `sorry`. `#guard_msgs in #print axioms T` lists `sorryAx`
once T's proof is cut, so in the mutated module (proofs cut up front) every mutant was KILLED (in the review's
probe, known survivors included). Lean 4.24 also refuses `#eval` of a value that depends on `sorry`
("aborting evaluation since the expression depends on the 'sorry' axiom"), so an `#eval` check reading a cut proof
killed the same way. The fix removes the class in three places:

- **The rule** (`classify`): a check is only a form whose outcome Lean computes from definitions, with no tactic
  block in it (a mutant can break a tactic and nothing else); `#print` in any spelling is a proof. Every `#`
  command now opens its own span in `tools/trust_map.py` (`#guard_expr`, `#eval!`, `#check_failure` were read as
  part of the declaration before them), and any command that is not a check form is no check (UNKNOWN on error).
- **The cut**: a failing proof is cut before any other error is read (Lean adds a failed theorem with `sorry`, so
  a check reading it fails only for that reason), and a `#` command is cut by blanking it with its docstring.
- **The control**: an error in a check is a kill only when the same build without the mutant (the same cuts; one
  build per stage and set of cuts, cached across mutants) passes. What fails there too reads a cut proof: it is
  cut as well, never a kill. An outside `--test` file that fails without the mutant too makes the mutant UNKNOWN.
  This closes the class for forms the rule does not name, since it asks Lean rather than the text.

The DRI's truth table (`FORMS` in `tests/test_trust_mutants.py`; each form bare, under `#guard_msgs in` and with
its docstring too, in the mutated module and in another module; reading the definition's value, and reading a
proof the tool cuts: a theorem `r_p : r 1 = 1` proved by a tactic, through `⟨0, …r_p…⟩ : Fin (r 1)`):

| Form | Class | Why | Reads the value: the mutant is | Reads a cut proof: the mutant is |
|---|---|---|---|---|
| `#guard` | check | evaluates compiled code, where proofs are erased | KILLED | SURVIVOR |
| `#guard_expr` | check | compares terms by definitional equality (since F11: a stuck reduction fails alike) | UNKNOWN (was KILLED) | SURVIVOR |
| `#eval` that throws | check | evaluates; refuses `sorry`, which the control catches (since F11: its message is the file's own) | UNKNOWN (was KILLED) | SURVIVOR (control) |
| `#eval` of the value (added for F11) | check | its output is formatted by instances Lean picks after elaboration | UNKNOWN with its docstring; SURVIVOR bare or `(drop info)` | (no proof reading) |
| `#reduce` | check | reduces; proofs are not reduced (since F11: it prints a stuck term as readily as a value) | UNKNOWN with its docstring (was KILLED); SURVIVOR bare or `(drop info)` | SURVIVOR |
| `#check` | check | elaborates the term against its type; proofs show as `⋯` (since F11: a type mismatch states no refutation) | UNKNOWN (was KILLED) | SURVIVOR |
| `#print` | proof | shows a theorem's proof term and a definition's text | SURVIVOR | SURVIVOR |
| `#print axioms` | proof | lists `sorryAx` once a proof is cut | SURVIVOR | SURVIVOR |
| `decide` `example` | check | kernel reduction of a decision procedure | KILLED | SURVIVOR |
| `rfl` `example` | check | definitional equality (since F11: a kill when `decide` then refutes the statement) | KILLED | SURVIVOR |
| tactic `example` | proof | a proof script (review F1) | SURVIVOR | SURVIVOR |
| tactic theorem | proof | a proof script (review F1) | SURVIVOR | SURVIVOR |
| `#guard` with a tactic block | proof | the mutant breaks the tactic, not the comparison | SURVIVOR | (its tactic is the proof) |
| a definition with a proof inside it, a `#guard` of its value beside it (F8's form, added for F9) | other | a definition cannot be cut; the mutant breaks its `by decide` | UNKNOWN | SURVIVOR |

Every row holds in both settings and all three wrappings: `test_the_truth_table_statuses` runs the package (the
definitions `n + 0`, one mutant each, the rows that must survive sharing one per wrapping, setting and reading; the rows' own definitions are classed T in the package's trust-classes.json, so only `r` is mutated) and `test_the_truth_table_classes` checks each row's role on the package's own spans;
`test_classify_truth_table` and `test_classify_reads_every_command` check `classify` alone, with the spellings
`#eval!`, `set_option … in`, nested wrappers, `#synth`, `#check_failure` and `#exit`.

The sweep (`docs/speed/trustmut/sweep.py --run`, evidence `evidence/sweep.json` with the sha256 of the tool, of
`trust_map.py` and of the tables it ran): the same table with the rich body `!(n < 1) && (n ≤ 3 || decide (n = 5))
&& n != 2 && ([n] ++ [1]).all (· ≥ 1) && [n, 3].any (· == 3) && true`, which carries every operator of the test
package and every other operator but the arms (54 mutants each), and the value read as `(List.range 6).map r`; the
arms and the multi-line forms are the F9 table (section 1c), in the same run. All 3,024 mutants ran (1,362 s at 16
jobs on the tool after F9; rerun on the tool and tables after F10 in 812 s, every mutant's verdict and detail the
same): 1,330 KILLED, 1,484 SURVIVOR, 210 UNKNOWN, 0 INVALID. Rerun on the tool of `f49efae15` (hunt 7's fixes,
section 1e), with the `#eval`-of-the-value row added (3,132 mutants, 2,390 s at 8 jobs): 630 KILLED, 1,522
SURVIVOR, 980 UNKNOWN, 0 INVALID, and `sweep.py` exits 0: the KILLED are the non-equivalent mutants of the
`#guard`, `decide` and `rfl` rows (210 each); the UNKNOWN those of the rows whose check states no refutation
(`#guard_expr`, the throwing `#eval`, `#check` in every wrapping, `#reduce` and the `#eval` of the value with their
docstrings) and of F8's form. The sweep was not rerun on the final tool: the tool's three later commits are
`d09bf54d4` (two checks the seeded-bug run found dead removed), `0ee7bfc45` (a time limit on each build) and
`05ea60664` (an outside `--test` file's imports built), and the sweep's packages have no outside file. No row that
reads a proof, and no row that is no check, has a KILLED mutant; every row expected to kill does; before F11 the
UNKNOWN were exactly the non-equivalent mutants of the six definitions F8's form reads (35 each), UNKNOWN at that
definition. The definitions a row expecting KILLED or UNKNOWN reads keep 19 survivors each (18 + 28 such
definitions), all equivalent mutants, equal to the original on every `n`, not only on 0..5:
- the conjunct `([n] ++ [1]).all (· ≥ 1)` is true whenever `!(n < 1)` is, so none of its mutants changes anything:
  `all-any`, `append-left`, `append-right`, `list-empty`/`list-drop-first`/`list-drop-last` of `[n]`, `[1]` and
  `[n] ++ [1]`, `list-first` and `list-last` of `[n] ++ [1]`, `[1]` -> `[2]` (lit-plus) and `≥ 1` -> `≥ 0`
  (lit-minus; `n = 0` is already false by the first conjunct);
- `n < 1` -> `n < 0` (lit-minus): at `n = 0` the `.all` conjunct is false anyway;
- `[n, 3].any (· == 3)` is always true, and so are its `list-drop-first` (`[3]`) and `list-last` (`[3]`) cuts.

## 1b. Review fix F8: an error in a definition is UNKNOWN, even beside a failing check

F8 was the same class in one more place: a mutant broke the `by decide` of a subtype definition
(`def loneBox : {x : Nat // lone x = x} := ⟨0, by decide⟩`), Lean put `sorry` there, and an `#eval loneBox.val`
check in the same module refused it ("depends on the 'sorry' axiom"); the control has no such break, so it passed,
and the tool read the check's error before the definition's and reported KILLED, although the value is 0 whatever
`lone` is. A definition cannot be cut (its proof term is part of what it defines), so the tool now kills only when
every error left after the cuts and the control is inside a check or a `--test` file; any other error (a
definition, a command that is no check) makes the mutant UNKNOWN at the first of them, whichever check fails
beside it. `test_an_error_in_a_definition_beside_a_failing_check_is_unknown` reads three such definitions, each by
one check form (`#eval` under `#guard_msgs`, `#guard`, a `decide` `example`); PROBE F8 prints UNKNOWN at the first.
The rerun replays and the sweep (section 1) change no verdict: none of their kills had a definition error beside
it. The same fix reads the control cache once per mutant and never pops it (review follow-up: a thread could pop a
key another had just found, a KeyError), so a control with no located error is never stored.

## 1c. Review fix F9: a kill is a check's own error, and no edit moves a line

F9 was the fifth form of one class (F1, F6, F7, F8, F9): the tool reported KILLED although no check failed on the
mutant. This time the error came from the tool's own edit. `arm-default` copied a two-line catch-all arm
(`| _ => [2,⏎3]`) into `| 0 => [1]`; only shorter replacements were padded, so every later line moved down one,
the up-front cut of the tactic proof below ran at its old line numbers and left `<;> trivial` behind, and Lean's
parse error at the old line of a `#guard` (which does not read `pick 0`) read as a failing check. The fix, the
DRI's three steps (note 2026-10-19b):

1. **No edit moves a line.** `relined` (one function for every operator) keeps each line after the mutated
   declaration where it was: a shorter replacement is padded with line ends, as before; a longer one takes its
   extra line ends from the blank lines right after the declaration (outside every comment), so the declaration
   ends on the line it ended on or on a blank line below it, and its lines (`Mutant.lines`) run over them. When
   too few blank lines follow, the edit is written as it is and the guard `moved` sees it: any line outside the
   mutated declaration that is not the checkout's line makes the mutant UNKNOWN ("the mutant moves this line"),
   never KILLED.
2. **A kill is attributed.** `attributed` decides each error: it kills only inside a check (or a `--test` file), at
   a line the mutant and the cuts left as the checkout has it, and never as a parse error (Lean's parser messages
   start "unexpected " or "expected "): a cut left behind or a moved line is no check's failure. Any other error
   (a parse error, a definition, a proof that cannot be cut, a command that is no check) is UNKNOWN (fail closed).
3. **The table has the axis.** `LINES` in `tests/test_trust_mutants.py`: every operator whose replacement can span
   lines, with fewer, the same or more lines than what it replaces, each definition followed by a three-line
   tactic proof (cut up front in the mutated module, the trap of F9) and then its check, read by a check that
   compares the value and by one that reads nothing (`#guard true`), in the mutated module and in another; and the
   forms table (section 1a) has F8's form, a definition with a proof inside it.

| Shape | Operators and lines | Compared by a check | Read by nothing |
|---|---|---|---|
| `default-more`: `\| 0 => [7]`, `\| _ => [2,⏎3]` (PROBE F9's form) | `arm-default`: more | 16 KILLED | 16 SURVIVOR |
| `default-more-tight`: the same, no blank line after it (its UNKNOWN: "moves this line") | `arm-default`: more | 15 KILLED, 1 UNKNOWN | 15 SURVIVOR, 1 UNKNOWN |
| `default-fewer`: `\| 0 => [7,⏎8]`, `\| _ => [2]` | `arm-default`: fewer | 16 KILLED | 16 SURVIVOR |
| `default-same`: `\| 0 => [7]`, `\| _ => [2]` | `arm-default`: same | 12 KILLED | 12 SURVIVOR |
| `arm-bool`: `\| 0 => 1 <⏎2`, `\| _ => 2 < 1` (its compared survivors are equivalent, below) | `arm-false`: fewer, `arm-true`: same | 6 KILLED, 11 SURVIVOR | 17 SURVIVOR |
| `list-multi`: `[n,⏎5]` | `list-first`, `list-drop-last`: same; `list-empty`: fewer | 7 KILLED | 7 SURVIVOR |
| `list-single`: `[n, 5]` | `list-first`, `list-drop-last`, `list-empty`: same | 7 KILLED | 7 SURVIVOR |
| `append-left-multi`: `[n] ++ [5,⏎6]` | `append-left`: fewer, `append-right`: same | 19 KILLED | 19 SURVIVOR |
| `append-right-multi`: `[n,⏎5] ++ [6]` | `append-right`: fewer, `append-left`: same | 19 KILLED | 19 SURVIVOR |

Each row holds in both settings (36 definitions, 516 mutants, every one run: 234 KILLED, 278 SURVIVOR, 4 UNKNOWN,
0 INVALID; the sweep's evidence, and `test_a_replacement_of_any_line_count_is_decided_by_the_checks` on the same
package, both through `lines_problems`). Every KILLED is at its own comparing check's line, and no mutant of a
definition no check reads is KILLED. Only `arm-default` can write more lines: `arm-true`/`arm-false` write one
token, the list cuts wrap the list they cut (`(xs.take 1)` has its lines), `list-empty` and `append-*` write one
line or none, and the token operators keep the line. The 22 survivors of the compared rows are all `arm-bool`'s and
all equivalent (each arm keeps its value on every `n`): `arm-true` of `1 <⏎2` and `arm-false` of `2 < 1` (each
arm's own value), `1 <⏎2` read as `1 ≤ 2`, `0 < 2` or `1 < 3` (still true), and `2 < 1` read as `2 ≤ 1`, `2 = 1`,
`2 < 0`, `1 < 1`, `2 < 2` or `3 < 1` (still false).

PROBE F9 printed KILLED at `Defs.lean:11: unexpected token '<;>'` before the fix; PROBE F1, F6, F7, F8 and F9
exit 0 on the final tool (`evidence/probes.json`, section 1e). The seeded bugs TM26–TM32 plant each
rule of the fix (section 3).

## 1d. Review fix F10: a check that gives no answer never kills

F10 was the sixth form of the class (KILLED although no check refuted the mutant). With `def size : Nat := 124`
and `example : (List.replicate size true).length = size := by decide`, `lit-plus` (125) sent `decide` over Lean's
recursion limit at the check's own line, so `attributed` read a kill, although the check holds for every `size`
(`lit-minus` survives): it ran out of budget, which is UNKNOWN (CLAUDE.md: verdicts are three-valued). The fix
removes the class wherever a Lean error decides a verdict:

- **One table**, `NO_ANSWER` in the tool: the messages Lean 4.24 gives when it gives no answer. Its runtime
  exceptions (`Exception.isRuntime`: "maximum recursion depth", "(deterministic) timeout …, maximum number of
  heartbeats"), the kernel's ("(kernel) deep recursion detected", "(kernel) deterministic timeout", "(kernel)
  interrupted"), a stack overflow, and a `decide` or `native_decide` that cannot decide ("Tactic `decide` failed
  …": the instance got stuck, or the kernel could not check what the elaborator reduced; "Tactic `native_decide`
  failed: Could not evaluate …"). A refutation reads otherwise ("proved that the proposition … is false",
  "evaluated that … is false", "Expression … did not evaluate to `true`", a `#guard_msgs` diff of two answers) and
  still kills.
- **Every reader**: `attributed` (a check, or a `--test` file under lean/); the mutated declaration (out of budget
  there is UNKNOWN, not INVALID, which means Lean refused the text); and an outside `--test` file, whose output is
  now read (before, any non-zero exit killed). Every error must still kill (section 1b), so a mutant one check
  refutes while another runs out of budget is UNKNOWN.
- **The whole message**: `ERROR` reads each error to the next line Lake or Lean starts, not only its first line,
  so a `#guard_msgs` that quotes the error it got on a later line, or a pretty-printer failure that wraps it, is
  read too. A runtime exception normally leads its message (Lean's `Core.tryCatch` rethrows it rather than wrap
  it). The detail keeps the first line, marked "no answer: ".

The table, `BUDGET` in `tests/test_trust_mutants.py` (`test_a_check_out_of_budget_or_stuck_is_unknown`, one
package, run end to end): each definition is `if n ≤ 3 then n else 100000`, read at 3 by a check that holds for
every value, which Lean cannot finish at 100000. `le-lt` and `lit-minus` of the 3 send it there; every other
mutant survives. Columns: the two mutants, before the fix (the F9 tool on the same package) and after:

| Row | Check | Lean at the mutant | Before | After |
|---|---|---|---|---|
| decide | `decide` `example` | maximum recursion depth | KILLED | UNKNOWN |
| rfl | `rfl` `example` | maximum recursion depth | KILLED | UNKNOWN |
| reduce | bare `#reduce` | maximum recursion depth | KILLED | UNKNOWN |
| guard-msgs | `#reduce` under `#guard_msgs` with `info: 3` | the recursion error at the `#reduce`, and the diff quoting it | KILLED | UNKNOWN |
| heartbeats | `decide` under `set_option maxHeartbeats 1000` | (deterministic) timeout at `whnf` | KILLED | UNKNOWN |
| kernel | `decide +kernel` | "[Error pretty printing: maximum recursion depth …" | KILLED | UNKNOWN |
| stuck | `decide` of `d 3 = d 3 + 0`, the other branch a well-founded `wf 1` | the instance did not reduce | KILLED | UNKNOWN |
| in-definition | a `def … : Fin 5 := ⟨…, by decide⟩` reading it | recursion depth in that definition | UNKNOWN (F8) | UNKNOWN |
| (its own `3` -> `4`) | the same, in the mutated declaration | recursion depth | INVALID | UNKNOWN |
| outside | the `decide` check in an outside `--test` file | recursion depth | KILLED | UNKNOWN |
| refuted | `example : d 3 = 3 := by decide` | proved false | KILLED | KILLED |
| refuted-outside | the same in an outside `--test` file | proved false | KILLED | KILLED |

PROBE F10's form is in the same package (`size`; `test_probe_f10_a_check_out_of_budget_is_no_kill`): before the
fix `lit-plus` was KILLED, now `[('lit-plus', 'UNKNOWN', 'lean/Demo/Defs.lean:5: no answer: maximum recursion depth
has been reached'), ('lit-minus', 'SURVIVOR', '')]`, and PROBE F10 exits 0 on the final tool. Lean 4.24's failing `#guard_msgs` also
logs the wrapped command's own error at its line, so the guard-msgs row is UNKNOWN by that error as well; the
whole-message read is checked on Lake's output by `test_an_error_is_read_with_its_whole_message`, and every message
of the table, at a check and in a `--test` file, by `test_a_check_that_gives_no_answer_never_kills`. The kernel's
own messages are in that unit table only: Lean 4.24 reaches its elaborator's limits first on these checks.

The evidence: no saved replay kill or INVALID gave no answer (`replay.py`, section 1; every kill is a `#guard`'s
or an `rfl`'s refutation), and the sweep, rerun on the tool after F10, gives every mutant the same verdict and
detail (section 1a). The seeded bugs TM33–TM40 plant each rule of the fix (section 3).

## 1e. Review fixes F11 and F12: the rule inverted, and an adversarial hunt

F11 was the seventh form of one class (F1, F6, F7, F8, F9, F10, F11): the tool reported KILLED although no check
refuted the mutant. `def bR (n) := if n ≤ 3 then n else wf 1` (`wf` well-founded) read by
`example : bR 3 + 0 = 0 + bR 3 := rfl`: the `le-lt` and `lit-minus` mutants reach `wf 1`, `rfl` gets stuck and says
"Type mismatch", the same message a real `rfl` refutation gives, and the tool read it as a kill although the check
holds for every value. F12 was the same class on the other side: `simp`'s step limit inside the mutated
declaration (`⟨3, by simp (config := { maxSteps := 9 })⟩`, 9 -> 8) gave INVALID, which counts for nothing, although
running out of budget is UNKNOWN. The DRI's note (reviews/speed-trustmut-dri-note-20261019c.md, PIPELINE-LIMITS L81)
named the cause: `attributed` was a deny-list (any error at a check killed unless it matched `PARSE` or `NO_ANSWER`),
so each recheck found one more message it missed. The fix changes the rule's shape.

### The rule: one positive condition per verdict that counts for nothing

KILLED (`settle`, `judge`, `run`'s `reading`, the Lean probe `READS`). Every error Lean reports, in lean/ and in an
outside `--test` file, is a check's own refutation:
- it is inside a check (`classify`: `#guard`, an `example` or theorem proved by `decide`, `native_decide` or `rfl`
  with no hypothesis before its colon, or one of those under `#guard_msgs … in`), at a line the mutant and the cuts
  left as the checkout has it (review F9), and its message states a refutation: one of `REFUTED`, matched whole
  ("Tactic `decide` proved that the proposition … is false", "Tactic `native_decide` evaluated that the
  proposition … is false", "Expression … did not evaluate to `true`"), or a `#guard_msgs` diff with such a
  refutation on one side only (the check's truth changed);
- an `rfl` check's failure (the same message whether the sides differ or the reduction got stuck) counts only when
  `decide`, asked in its place, then refutes the statement (`decided`; never `native_decide`, which runs compiled
  code an `rfl` check never reads);
- Lean, in the mutant's own build, elaborates the check (and the `Decidable` instance it synthesizes for it) to the
  same term as without the mutant, and every definition it reads, outside the mutated one, to the same value (a
  hash per constant: an elaborator that reads the source, `include_str` in a helper, an instance search that runs
  out of budget and picks another instance, or a package's `leanOptions` all change one);
- nothing it computes, through logic or compiled code (definitions, `opaque` values, proofs, the `@[csimp]` lemmas
  from Lean's own table, `implemented_by` targets, a `partial def`'s `_unsafe_rec`, `initialize` functions),
  reaches `sorryAx` or runs IO (`unsafeIO`, `unsafeBaseIO`, `unsafeEIO`, an `initialize`d value). Since nothing is
  cut up front any more, a cut proof is one the mutant broke, so a `sorryAx` there means the check computes
  through a broken proof (a `Decidable` instance or `@[csimp]` lemma resting on it);
- and the same build without the mutant (its control, the same cuts) passes (review F7).

INVALID (`invalid`, `refused`): every error in the mutated declaration is a parse error or a name, field, pattern or
exhaustiveness error (`REFUSED`: "Unknown identifier/constant", "Invalid field/projection/pattern", "Missing
cases", "ambiguous"), located inside the text the mutant wrote and outside every tactic block, and none quotes
Lean's budget.

Everything else is UNKNOWN, which counts toward the exit code.

### The safe cases, one test each

UNKNOWN at a check (`JUDGED` in `tests/test_trust_mutants.py`, `test_a_check_kills_only_when_its_message_states_a_refutation`,
and `test_a_check_that_gives_no_answer_never_kills` for the budget messages): a stuck or false `rfl` that `decide`
does not refute, `#guard_expr`'s and `#check`'s definitional equality, an `#eval` that throws, any `info` in a
`#guard_msgs` diff (`#reduce` prints a stuck term; `#eval`'s output is formatted by instances Lean picks after
elaboration and can read files), a diff between two refutations, a budget quote, a warning, a diff Lean does not
show as two sides, a refutation with more text after it or quoted inside another message, a stuck `decide`,
unsolved goals, an unclassified message, a parse error at an `rfl` check. The end-to-end rows (`STUCK`,
`test_a_check_that_states_no_refutation_is_unknown`) run them through Lean in lean/ and in an outside file.

UNKNOWN in the mutated declaration (`REFUSALS`, `test_invalid_only_when_lean_refuses_the_mutated_text`;
`test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal`): `simp`'s step limit (F12), unsolved
goals, `omega`, a stuck or refuting `decide`, a name error inside a tactic block, a type mismatch (a false or
stuck proof term gives one), "fail to show termination", the recursion depth, heartbeats, instance search (its
own size and heartbeat budgets), "don't know how to synthesize", "Function expected" (a coercion's instance
search), a refusal that quotes a budget, a refusal beside a tactic failure, outside the mutant's text (a proof term
it broke), a parse error outside its text (the tool's own padding), an unclassified message.

PROBE F11 and PROBE F12 are `test_probe_f11_a_stuck_rfl_check_is_no_kill` and
`test_probe_f12_a_tactic_out_of_steps_in_the_mutated_definition_is_unknown`.

### The adversarial hunt (the DRI's step 2)

Seven hunts, each a fresh subagent given only the class description, the earlier probes and the code, each run on
the tool after the previous hunt's fixes. Every probe is in `docs/speed/trustmut/hunt/` (README there) and, but F1,
a row of `tests/test_trust_mutants.py` (`HUNT`, one package per form).

| Hunt | Probes that failed (forms) | What let them through | The fix (the rule's shape where it changed) |
|---|---|---|---|
| 1 | H1, H1r, H2, H3, H4, H5, H7 (H6 decided: a refusal) | `decide` refutes only the goal, not a hypothesis; instance search's own budget read as a refusal; a refutation through an instance or `@[csimp]` lemma on a proof the tool cut; `native_decide` asked of an `rfl` check | a check with a binder before its colon is a proof; instance search out of `REFUSED`; a kill needs the statement to read the definition; `decide` only |
| 2 | N1, N1g, N1r, N2, N2n, N3, N5, N7, N8, N10 (N4 decided out of class) | a tautology mentioning the definition beside the cut-proof bridge; an `#eval` printing the definition's text; "Function expected" from a coercion's search; two commands on one line; a section `variable`; another command on the mutated declaration's last line | Lean elaborators at each check's own position (`READS`): the theorems behind its `Decidable` instances, hypotheses, reflection; a cut proof loses its attributes; one command per check; a shared last line UNKNOWN |
| 3 | P1, P2, P3, P4, P5, P7, P8, P8d, P9 | private names, `DecidableLE`-style abbreviations, `attribute [csimp]`, MetaM reflection, a theorem chain, a class's proof field, instance choice changed by the mutant, `#eval!` of a Prop | the probe runs in each mutant's own build and walks every bridge for `sorryAx` |
| 4 | Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q12 | proofs passed explicitly, `opaque` values, `#eval`'s output chosen after elaboration, csimp behind the synthesized instance, source text read by elaborators and by IO, a silent budget fallback, a proof term outside the mutant's text | the shape changed: nothing cut up front (so `sorryAx` means a proof the mutant broke) and one full walk; the check's term must hash as without the mutant; no `#eval` output is an answer; a refusal only inside the mutant's own text |
| 5 | R1, R2, R3, R5, R6, R7, R8 | `partial def`'s `_unsafe_rec`, `unsafeIO`, the tool's own line padding, package `leanOptions`, `initialize`, an unexpander printing one refutation two ways, `include_str` in a helper | the walk follows compiled code and flags IO; every definition read outside the mutated one must hash the same; the probe runs as `lake lean`; a diff kills only when one side is empty; a parse error only inside the mutant's text |
| 6 | S1, S2, S3, S5, S6, S7, S8, S9 | the exemption covered the definition's whole namespace; walk order; IO without the `unsafe*` names; IO in a dependency package; a check printing a probe line; library `leanOptions`; a `local` csimp | only the mutated constant and its auxiliaries are exempt; IO by its types; every package but Lean's core is walked; a nonce on the probe's lines; the probe elaborates the module at its own path; every `@f = @g` theorem is a possible csimp lemma |
| 7 | T1, T2, T3, T5 (T6 decided: the mutant's own text) | an `axiom`; a core function's csimp; source read only through the mutated definition; another declaration's `_unsafe_rec` named under the mutated one | an axiom of the tree is no answer; core csimp walked; everything reached is compared but the mutated declaration and what Lean generated for it (Lean's declaration ranges) |

Forms tried that were fine, per hunt, are in each hunt's report (the G probes of hunt 1 are saved too); among them
an auto-param, a negative `#guard_msgs` `rfl`, free variables, Lean's module system, a cross-module csimp, `#print`
spoofing, `decide +kernel`, matchers shared across declarations.

Decided boundaries (recorded, not signed: they are this item's reading of the class, which the recheck judges):
1. N4: an `@[implemented_by]` that makes the mutated definition the code that runs: `#guard` and `native_decide`
   observe compiled code, so its changed value is a refutation of what runs.
2. H6: a refusal Lean gives, with no budget involved, to the text the mutant wrote (since hunt 2 "Function expected"
   is no refusal, so H6 itself is now UNKNOWN).
3. T6: a silent budget effect in Lean's elaboration of the mutant's own text (`(⟨0⟩ : W 127) == ⟨0⟩` picks a
   fallback instance): what the mutant's text means as Lean elaborates it, as INVALID lets the compiler decide.
   Since hunt 7's fixes the probe compares the instance the check reads, so PROBE T6 exits 0 on the final tool
   (`evidence/probes.json`: UNKNOWN, "`Demo.wFallback`, which it reads, is not what it is without the mutant").

Hunt 7's two unreported probes (T5w, T7: a helper of a structure, well-founded and structural) found something
else: a mutant of `instance [s : Small n] : Small (n + 1)` makes Lean's build of the module run forever, and the
tool's builds had no time limit, so the run hung. Every
build of a mutant now has `--build-timeout` (default 1,800 s, the suite's hang bound); past it the process group
is killed and the mutant is UNKNOWN (`test_a_build_past_its_time_limit_is_unknown`, an expired limit injected;
TM79).

The class is not closed. Each of the seven hunts found new forms (7, 10, 9, 11, 7, 8, 4 failing probes, the decided
ones not counted); the seventh found the fewest. The DRI's addendum (23Z, for the rounds after this one) bounds the hunt and asks for an
allow-list; this round stopped after the seventh hunt and its fixes.

### The evidence

- PROBE F11 failed before the fix (`le-lt` and `lit-minus` KILLED at "Type mismatch") and prints `[('le-lt',
  'UNKNOWN', 'lean/Demo/Defs.lean:7: Type mismatch (an `rfl` check `decide` does not refute)'), …]` after; PROBE
  F12 failed (`eq-le`, `eq-ne`, `lit-minus` INVALID at "`simp` failed: maximum number of steps exceeded", `lit-plus`
  INVALID at "unsolved goals") and prints them UNKNOWN after. PROBE F1, F6–F16, F15c and F16c exit 0 on the final tool.
- Every probe of the hunt directory, run by `hunt/run.py` on this branch (`evidence/probes.json`, with the sha256 of
  the tool, the test file, this report (its quote of the summary left out), `claims.py` and `hunt/F15c.md`):

  > Probes on 8820e8cd6 (this checkout's sources): 84 of 85 exit 0; non-zero: N4 (1, boundary 1); not run: F14c (it checks this file's sentences against this file: run after run.py), T5w (a mutant's build runs until --build-timeout), T7 (a mutant's build runs until --build-timeout).

- The sweep (section 1a), on the tool of `f49efae15`: every forms row and every lines row as the tables expect,
  `sweep.py` exits 0; the survivors are the same equivalent mutants.
- The replay of ap-2 F11 (`aa2fd56e3`) with the final tool (section 1): the same 359 kills and 33 survivors; 12
  INVALID now UNKNOWN.
- The F11/F12 package before and after (`STUCK`; the tool at `260efe231` against the F11/F12 fix's):
  before, every far mutant of `rfl`, `by rfl`, `#guard_expr`, `#reduce` under `#guard_msgs`, `#check`, a throwing
  `#eval` and both outside rows was KILLED and the subtype's own mutants and `simp`'s were INVALID; after, the far
  mutants are KILLED only at the `rfl` checks `decide` refutes, UNKNOWN elsewhere.
- Cost: each kill now elaborates its check's module once more in the mutant's build (the probe), and the control
  pass elaborates each check module once; nothing is cut up front, so a proof the mutant breaks costs one more build.
  Section 1's profile line gives the time ap-2 F11's threads spent in the probe and in builds.

## 1f. Recheck F13 and F14: an outside check's imports, and the time budget

**F13 (the class of H4 and N1, through a file the tool only reads).** An outside `--test` file is run with `lake
env lean`, which builds nothing, and `targets` ignored the file's imports. So a module of lean/ it imports (directly,
or through another module) kept its pre-mutant `.olean`: a proof the mutant broke there (`p_iff : P n ↔ f n =
true`, with a `Decidable (P n)` instance on it) was never rechecked, cut or seen by the probe's walk, and `decide`
refuted `¬ P 3` through the instance, a KILL although it holds for every `f`. The class is "a check reads a module
that was not rebuilt with the mutant"; inside lean/ Lake rebuilds each check module's imports, so the outside file
was its one member. The fix closes it where the stage list is made: `main` reads every outside file's imports
(`check_lean_imports.imports`, the repository's one header reader) into `Tree.imported`, and `targets` builds them
with the mutant as it builds a check module, so their failing proofs are cut and the probe finds `sorryAx` (UNKNOWN,
as the same check inside lean/ gives: hunt H4). A header the reader refuses stops the run (exit 2) before any
build. PROBE F13 failed before the fix (`body-true`, `lt-le`, `lt-eq`, `lit-plus` KILLED) and gives them UNKNOWN
after ("it computes through a proof the mutant broke"); it is a test with a second form, an import reached only
through a module of another directory (`test_probe_f13_an_outside_check_reads_its_imports_built_with_the_mutant`,
`BRIDGED`), and the refused header is `test_an_outside_test_whose_header_cannot_be_read_stops_the_run`. Seeded
bugs TM80 (the imports left out of `targets`) and TM81 (the header error dropped) fail them. The probe is saved as
`hunt/F13.sh`.

**F14 (an overclaim, in two forms).** Section 1 claimed the time budget held for all six replays, although ap-2
F11 took 1,546 s on the F11 round's tool. The first fix took the claim out of sections 1, 4 and 5 but repeated its
words in this paragraph, and said here and in `hunt/README.md` that PROBE F14 then passed; it did not (the recheck:
`AssertionError: 1546`). The class is a sentence that states a result (a budget met, a probe or test that passes,
a run on the final tool, a count) that no saved evidence gives. The fix removes it where such sentences are checked:

- `claims.py` (in this directory) checks three things against the saved evidence, and no more (review F16): the
  sentences of this report and of `hunt/README.md` that `CLAIM` reads, the step-1 table of section 1 (`tabled()`),
  and the sentences `named()` lists (`bindings()`). A sentence `CLAIM` reads must lie inside a text `claims.py`
  writes from the saved evidence: the replays and their profiles, the sweep, the seeded bugs, the probes, the
  selected tests, the evidence of an earlier round as git keeps it, and `sweep.py`'s and `F14.sh`'s exit codes now.
  A number `CLAIM` reads that the evidence does not give is UNBOUND, and so is a claim `claims.py` has no evidence
  for; `NOT_CLAIMS` names the words that report no result, each with its reason. A number in a form `CLAIM` does
  not read, outside the table and `named()`, is not checked. It prints one line per sentence, table row and named
  sentence (the list the DRI's note of 2026-10-20 asks for) and exits 1 on any UNBOUND.
- `hunt/run.py` runs every probe and saves its exit code, time and last line in `evidence/probes.json`, with the
  sha256 of the tool, the test file, this report, `claims.py` and `hunt/F15c.md` (`SOURCES`; the report's quote of
  the summary, written after the run, left out): a sentence that says a probe passes quotes that file.
- `replay.py --run` now runs the tool in its own process with a profile (`profiled`): the 5-minute load, sampled
  every 15 s, and the time the threads spent in the probe and in builds, saved in the replay's evidence; the
  report quotes `replay.py`'s budget and profile lines.

Run on the report as the F13/F14 round left it, `claims.py` listed as UNBOUND, among others: loads no evidence
saved, "on the final tool" for the sweep and the seeded bugs (they ran on earlier tools), the sweep's count of
definitions, hunt 1's count of failing probes (the decided H6 counted, where hunt 2's decided N4 was not), the
INVALID range of section 4, and every probe claim, for which nothing was saved. Each such sentence is now bound, reworded or deleted. PROBE F14 is `hunt/F14.sh`; PROBE F14c,
`hunt/F14c.sh`, runs `claims.py`, the class's probe. Neither is a suite test: both read this report, and batch
evidence is checked at the gate and merge, never by a permanent test (R11, D4).

**F15 (a wrong count of F14's class).** Section 4 gave each replay's INVALID mutants as "21–35", and the F14
paragraph above said every such sentence was bound; the evidence gives 7–35 (qt-a1 has the fewest INVALID). `claims.py`
wrote the right text, but `CLAIM` read a count only with at most one word between the number and what it counts, so
nothing compared the two. The class is a count `CLAIM` does not read. The fix is in `CLAIM`: its count form (`COUNT`,
`COUNTED`) takes up to three words between them, and it also reads "N each", "all N", "about N" and a number of
lines; a number inside a name (ap-2, F14, Lean 4.24) is no count, and a sentence that starts with a digit is a
sentence of its own. Run on this report, the wider check found three more counts no evidence gave: section 5's sizes
of the review rounds' tests (now measured from the test file, `parts()`; each was off), its estimate of the lines the
unused operators take (reworded: nothing measures it), and a task line's own number (`NOT_CLAIMS`). PROBE F15 is
`hunt/F15.sh`; PROBE F15c, `hunt/F15c.sh`, runs `claims.py` on `hunt/F15c.md`, one wrong count of each form, and
requires each UNBOUND as a sentence of its own.

**F16 (F14's class, a third form: numbers `CLAIM` does not read).** The step-1 table (survivor counts, seconds,
the yes/no columns), the former kills of review F1 by file, pk-1's count at `UnspecifiedWire.lean:526`, the
seeded-bug count of section 6 and its collection counts were read by no check, although `claims.py` wrote the
table's rows, and the F14 paragraph above and `hunt/README.md` said every such sentence was checked. Every
number there was right, so the fault was the claim. Following the DRI's note of 2026-10-20b, the fix narrows the
claim and does not widen `CLAIM`: `tabled()` compares the table, every cell of every row, with `replay.table()`
(a row missing or extra is UNBOUND too); `named()` lists each other sentence once, with its words, the numbers
its evidence gives and that evidence, and `bindings()` requires the sentence in the report with those numbers
(a sentence missing is UNBOUND, so a rewording cannot drop it); and the F14 paragraph above, `hunt/README.md`
and the round-4 task line now say what `claims.py` checks, no more. PROBE F16, `hunt/F16.sh`, failed before the
fix (on its first copy, a survivor count of pk-1's row, `claims.py` exited 0; section 1e's evidence has its
exit code after the fix). It also requires each copy to have an UNBOUND line the report itself does not have, so
a stale `evidence/probes.json` (as during `hunt/run.py`) cannot pass it. PROBE F16c,
`hunt/F16c.sh`, the class's probe, changes each cell of the table and each number of each named sentence alone,
and removes each named sentence alone, and requires UNBOUND on every copy and on none of the report itself.

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
statement script) and runs the tool on it with `TMPDIR` in `tmp_path` and `VE_LEAN_SHARE=off`; a second package is
the truth table of section 1a (`table_package`), a third the line axis of section 1c (`lines_package`), a fourth
the budget table of section 1d (`budget_package`), a fifth F11/F12's table (`stuck_package`, section 1e), and each
hunt form has a package of its own (`HUNT`, section 1e); the generator, the check rule (`classify`), the spans, the
cuts, the line-keeping edit (`relined`, `moved`), the kill rule (`judge`, `refutes`, `settle` with faked builds,
`decided`), the refusal rule (`invalid`, `refused`, `in_tactic`), the probe's rewrite (`named`) and the error readers
(`ERROR`, `LEAN_ERROR`) have tests without Lean. The file has 301 tests at this checkout (`pytest --collect-only`);
section 6 gives the selected run.

Each rule has a seeded bug in `docs/speed/trustmut/mutants.json` (the `tools/mutants.py` format), 91 of them: TM1–TM40
from the earlier rounds (TM8, TM23, TM25, TM30, TM31, TM33–TM36 retargeted at the inverted rule) and TM41–TM78 for
F11, F12 and the hunts, among them the Lean probe's own lines (`READS` is Lean text inside the tool: TM48, TM59,
TM60, TM63, TM65, TM71–TM74, TM77, TM78), TM79 for the build time limit, TM80, TM81 for review F13, TM82–TM85
for F14's class (`claims.py`, `replay.py`'s budget line, `hunt/run.py`'s summary; each command-mode, killed when
its command exits non-zero), TM86–TM93 for F15's (`CLAIM`'s count forms and `parts()`: `hunt/F15c.sh`) and TM94–TM99
for F16's (the table, the named sentences: `hunt/F16.sh`, `hunt/F16c.sh`; the probes' hashes: `hunt/F14c.sh`).
`claims.py` is one of the probes' hashed sources, so any change to it makes `hunt/F14c.sh` fail; its seeds are
killed by commands that do not read `evidence/probes.json` (TM82 by `hunt/F15c.sh`, TM83 and TM93 by the one-line
checks `mutants.json` gives). `uv run python tools/mutants.py docs/speed/trustmut/mutants.json` kills 91 of 91, each at a named test or command, the file
restored to its exact bytes (`mutants-evidence.json`: TM1–TM78 on `d09bf54d4` in three worktrees of it, the rows
joined in order, `--no-baseline` since the whole test file passes there; TM79 and the build-path seeds TM1, TM2,
TM22 and TM36 again on `0ee7bfc45`, which adds the build time limit; TM80 and TM81 on `05ea60664`, the F13 fix;
TM82–TM93 on `5d2df727f`, round 5, after `claims.py` last changed). No seeded bug became UNKNOWN under the
stricter rule. The first run (four worktrees at once on the loaded
VM) found TM57's and TM62's checks dead (the edit-span rule and the probe's `sorryAx` already cover their forms), so
the checks and the seeds were removed; TM79 was too weak (TM71 plants T5's bug); TM42's and TM44's rules lacked a
test that only they decide (a one-sided `#eval` info diff; a refusal at an edit inside a tactic block), now added;
TM1–TM4 hit the nested run's 1,800 s limit under that load and were killed in the second run. Python is the only product language here: no Lean file
of `lean/` and no Rust changed (the probe's Lean text is part of the tool). The parametrized tests have ids without
spaces: `tools/mutants.py` reads a failing id up to its first space.

| Mutant | Rule | Bug planted (the replacement) | Failing test |
|---|---|---|---|
| TM1 | a failing proof is cut and the build repeated, never left to decide the mutant | failing proofs are not cut | `test_a_failing_proof_is_no_kill` |
| TM2 | the importing check modules are built | the second build stage is empty | `test_a_well_guarded_definition_has_no_survivor` |
| TM3 | a guard over `[]` leaves a survivor | `list-empty` leaves the list unchanged | `test_a_guard_over_the_empty_list_leaves_survivors` |
| TM4 | `--allow` suppresses exactly its operator | any operator of the definition is allowed | `test_allow_suppresses_exactly_its_operator` |
| TM5 | a scratch copy is used | the scratch sources are hard links to the checkout | `test_mutants_are_built_in_a_scratch_copy` |
| TM6 | the rest are listed as NOT RUN | only the first NOT RUN row prints | `test_max_mutants_lists_the_rest_as_not_run` |
| TM7 | every list method's receiver is cut | `find?` unescaped in `LIST_METHODS` (a real regression of the rewrite, caught by the ap-2 replays) | `test_the_generator_cuts_every_list_a_condition_reads` |
| TM8 | an `example` is a check only when decide, native_decide or rfl proves it (review F1) | `return "check" if kind == "command" or proved and not tactics and c...` | `test_an_example_proved_by_a_tactic_is_no_kill` |
| TM9 | a tactic-proved theorem whose statement names the definition is a proof (review F1) | it is a check outside the mutated module (the first tool's rule) | `test_a_failing_proof_is_no_kill` |
| TM10 | a check outside the directory whose statement names the definition is built | only the directory's checks are built | `test_a_decide_check_outside_the_directory_naming_the_definition_kills` |
| TM11 | a `#guard_msgs … in` line opens the command it wraps (review F6), in `tools/trust_map.py` | the wrapper is its own command again | `test_a_proof_wrapped_in_guard_msgs_is_no_kill`, `test_a_guard_msgs_wrapper_is_in_the_span_of_what_it_wraps` |
| TM12 | a `#guard_msgs` around a tactic proof is a proof (review F6) | any wrapper is a check | `test_a_proof_wrapped_in_guard_msgs_is_no_kill` |
| TM13 | a cut proof loses its `#guard_msgs` wrapper (review F6) | the wrapper is kept | `test_a_proof_wrapped_in_guard_msgs_is_no_kill` |
| TM14 | a cut proof keeps the comments after it, the next `#guard_msgs`'s docstring (review F6) | the cut runs to the span's end | `test_a_cut_proof_loses_its_guard_msgs_wrapper_and_keeps_the_comments_after_it` (since F7 the control cuts the check that loses its docstring, so the end-to-end test no longer sees it) |
| TM15 | a check error kills only when the build without the mutant passes (F7) | no control | `test_the_truth_table_statuses` |
| TM16 | every `#print` is a proof (F7) | `#print` is other | `test_the_truth_table_classes`, `test_the_truth_table_statuses` |
| TM17 | a check form with a tactic block is a proof (F7) | tactic blocks are not counted | `test_the_truth_table_classes`, `test_the_truth_table_statuses` |
| TM18 | a `#` command is cut by blanking it (F7) | it cannot be cut | `test_the_truth_table_statuses` |
| TM19 | a blanked command loses its docstring (F7) | the docstring stays | `test_a_cut_command_is_blanked_with_its_docstring` |
| TM20 | failing proofs are cut before a check error is read (F7) | not when a check fails too | `test_the_truth_table_statuses` |
| TM21 | every `#` command opens its own span, in `tools/trust_map.py` (F7) | the old list of seven commands | `test_every_hash_command_opens_its_own_span` |
| TM22 | an outside `--test` file kills only when it passes without the mutant (F7) | any failing file kills (since F10 on the new lines) | `test_an_outside_test_that_fails_without_the_mutant_is_no_kill` |
| TM23 | only an error inside a check kills; one in a definition or a proof is UNKNOWN (`judge`) | `if built != checkout or not built.strip() or PARSE.match(message):` | `test_only_a_checks_own_error_kills` |
| TM24 | the blanking stops at a string the command before is still writing (F7) | it does not | `test_a_cut_command_is_blanked_with_its_docstring` |
| TM25 | an error in a definition is UNKNOWN even beside a failing check (review F8; `settle` reads every error) | `if bad := next((x for x in rows[:1] if x[3] == NONE), None):` | `test_settle_kills_only_when_every_error_is_a_checks_refutation_of_the_definition` |
| TM26 | a longer replacement takes its extra line ends from the blank lines after its declaration (F9) | it never does | `test_an_edit_keeps_every_line_after_its_declaration`, `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |
| TM27 | those blank lines are never inside a comment (F9) | the comment test dropped | `test_an_edit_keeps_every_line_after_its_declaration` |
| TM28 | a mutant that moves a line after its declaration is UNKNOWN (F9) | no guard | `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |
| TM29 | the guard compares each line, not only the count (F9) | it compares the count | `test_moved_finds_the_first_line_after_the_declaration_that_moved` (first named the edit test, where it survived: no case there keeps the count and moves a line; the new test has one) |
| TM30 | a parse error never kills, nor sends an `rfl` check to `decide` (review F9: a cut left behind) | `if role != "check" or built != checkout or not built.strip():` | `test_a_check_kills_only_when_its_message_states_a_refutation` |
| TM31 | a check's error kills only at a line the mutant and the cuts left as the checkout has it (review F9) | `if role != "check" or not built.strip() or PARSE.match(message):` | `test_only_a_checks_own_error_kills` |
| TM32 | the mutated declaration's lines run over the blank lines its edit takes (F9) | they end where the declaration did | `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |
| TM33 | a check that gives no answer never kills (review F10; since F11 because it states no refutation) | `if REFUTED.fullmatch(message) or NO_ANSWER.search(message):` | `test_a_check_that_gives_no_answer_never_kills`, `test_a_check_out_of_budget_or_stuck_is_unknown[decide]`, `test_probe_f10_a_check_out_of_budget_is_no_kill` |
| TM34 | an error is read with its whole message (review F10; a refutation is matched whole, F11) | `ERROR = re.compile(r"^error: (?:\./)*(\S+?\.lean):(\d+):(\d+): (.*)...` | `test_an_error_is_read_with_its_whole_message`, `test_a_check_wrapped_in_guard_msgs_kills` |
| TM35 | a refusal that quotes Lean's budget is no refusal: UNKNOWN, not INVALID (review F10, F12) | `return not elsewhere and bool(PARSE.match(message) or REFUSED.searc...` | `test_invalid_only_when_lean_refuses_the_mutated_text` |
| TM36 | an outside --test file kills only by the rule inside lean/: one that gives no answer, or a stuck `rfl`, never kills (review F10, F11) | `if status == "INVALID": return status, detail` | `test_a_check_out_of_budget_or_stuck_is_unknown[outside]`, `test_a_check_that_states_no_refutation_is_unknown[outside-equal]` |
| TM37 | a decide that gets stuck or cannot evaluate gives no answer (UNKNOWN, marked so in the detail) (review F10) | `\|stack overflow")` | `test_a_check_that_gives_no_answer_never_kills`, `test_a_check_out_of_budget_or_stuck_is_unknown[stuck]` |
| TM38 | a check out of heartbeats gives no answer (UNKNOWN, marked so in the detail) (review F10) | `` | `test_a_check_that_gives_no_answer_never_kills`, `test_a_check_out_of_budget_or_stuck_is_unknown[heartbeats]` |
| TM39 | the kernel's limits give no answer (review F10) | `` | `test_a_check_that_gives_no_answer_never_kills` |
| TM40 | a check over the recursion limit gives no answer (UNKNOWN, marked so in the detail) (review F10, PROBE F10) | `NO_ANSWER = re.compile(r"` | `test_a_check_that_gives_no_answer_never_kills`, `test_probe_f10_a_check_out_of_budget_is_no_kill`, `test_a_check_out_of_budget_or_stuck_is_unknown[rfl]` |
| TM41 | an `rfl` check's failure kills only when `decide` then refutes its statement (review F11, PROBE F11) | `if pending := {}:` | `test_probe_f11_a_stuck_rfl_check_is_no_kill`, `test_a_check_that_states_no_refutation_is_unknown[rfl]`, `test_settle_kills_only_when_every_error_is_a_checks_refutation_of_the_definition` |
| TM42 | a `#guard_msgs` diff kills only between refutations: no `info` (an `#eval`'s or `#reduce`'s) is an answer (review F11, hunt Q4, Q7, Q8) | `return said if all(m.startswith("info:") or m.startswith("error:") ...` | `test_a_check_kills_only_when_its_message_states_a_refutation` |
| TM43 | INVALID needs every error of the mutated declaration to be a refusal (review F12) | `for f, n, message, column in errors[:1]: at = starts[` | `test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal` |
| TM44 | an error inside a tactic block of the mutated declaration is a tactic's, never a refusal (review F12) | `if not refused(message, not edit[0] <= at < max(edit[1], edit[0] + ...` | `test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal` |
| TM45 | a tactic out of budget in the mutated declaration is UNKNOWN, never INVALID (review F12, PROBE F12) | `return not NO_ANSWER.search(message) and not message.startswith("un...` | `test_probe_f12_a_tactic_out_of_steps_in_the_mutated_definition_is_unknown`, `test_invalid_only_when_lean_refuses_the_mutated_text` |
| TM46 | a check with a hypothesis before its colon is a proof: `decide` refutes only its goal (hunt H1) | `closed = True` | `test_only_guards_and_decide_rfl_proofs_are_checks`, `test_a_hunt_form_gets_no_verdict_that_hides_it[H1]` |
| TM47 | a kill needs the check to refute the mutated definition: Lean finds it in the statement, no hypothesis, no reflection, no cut theorem behind its instance (hunt H4, H5, N1-N3, N8) | `if bad := None:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[H4]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[H5]`, `test_settle_kills_only_when_every_error_is_a_checks_refutation_of_the_definition` |
| TM48 | a refusal counts only inside the text the mutant wrote: a proof term it broke elsewhere fails as a tactic does (hunt Q9) | `if not refused(message, in_tactic(code, at, lo, hi)):` | `test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal`, `test_a_hunt_form_gets_no_verdict_that_hides_it[Q9]` |
| TM49 | an `rfl` check is asked `decide`, never `native_decide`, which evaluates compiled code (hunt H7) | `return text[:s] + "by native_decide" + "\n" * text.count("\n", s, e...` | `test_a_check_that_states_no_refutation_is_unknown[rfl-native]`, `test_decided_rewrites_only_the_rfl_and_keeps_every_line` |
| TM50 | instance search that fails (its own budget, hunt H2, H3) is no refusal: UNKNOWN | `REFUSED = re.compile(r"failed to synthesize\|[Uu]nknown (?:identifie...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[H2]`, `test_invalid_only_when_lean_refuses_the_mutated_text` |
| TM51 | an outside --test file's `rfl` check is asked `decide` in its copy, as inside lean/ (review F11) | `copy.write_text(t.read_text())` | `test_a_check_that_states_no_refutation_is_unknown[outside-decide]` |
| TM52 | a check that computes through a proof the mutant broke never kills (hunt H4, N1, N2, P1-P9, Q1-Q3, Q5) | `if False:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[N1]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[N1g]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[P1]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[Q1]` |
| TM53 | a check whose goal has a hypothesis (a section variable) never kills (hunt N8) | `if False:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[N8]` |
| TM54 | a kill needs Lean to elaborate the check as without the mutant (hunt Q6, Q10, Q12, P8) | `if False:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[Q6]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[Q10]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[P8]` |
| TM55 | a cut proof loses its attributes: a `sorry` is no `@[csimp]` lemma (hunt N2) | `for a in re.finditer(r"@\[", ""):` | `test_a_hunt_form_gets_no_verdict_that_hides_it[N2]`, `test_a_cut_proof_loses_its_guard_msgs_wrapper_and_keeps_the_comments_after_it` |
| TM56 | a span with two commands is no check (hunt N7) | `\|#[a-z_]+!?)(?![\w'])", bare)) > 9:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[N7]`, `test_only_guards_and_decide_rfl_proofs_are_checks` |
| TM58 | "Function expected" (a coercion's instance search out of budget says it) is no refusal (hunt N5) | `REFUSED = re.compile(r"[Ff]unction expected\|[Uu]nknown (?:identifie...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[N5]`, `test_invalid_only_when_lean_refuses_the_mutated_text` |
| TM59 | the walk reads each `@[csimp]` lemma of what it reaches, wherever its attribute is given (hunt P3, Q5) | `todo := todo ++ (Lean.Compiler.getImplementedBy? env c).toList ++` | `test_a_hunt_form_gets_no_verdict_that_hides_it[P3]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[Q5]` |
| TM60 | the walk reads an `opaque` definition's value (hunt Q3) | `let value := (info.value?).getD (mkConst ``True)` | `test_a_hunt_form_gets_no_verdict_that_hides_it[Q3]` |
| TM61 | the probe reads the mutant's build, where the instance Lean picks can change (hunt P8) | `texts[f] if f in texts else read(f), tree.roles.get(f, ()))` | `test_a_hunt_form_gets_no_verdict_that_hides_it[P8]` |
| TM63 | the probe's copy keeps every line of the file, so what a check reads of its source is the file's (hunt Q6) | `lines.insert(first, "import TmTrustProbe")` | `test_a_hunt_form_gets_no_verdict_that_hides_it[Q6]` |
| TM64 | nothing is cut up front: a cut proof is one the mutant broke, which is what the probe's `sorry` means (hunt H4-Q5) | `for first, last, r, _ in sorted(tree.roles[m.file], reverse=True): ...` | `test_an_outside_test_that_fails_without_the_mutant_is_no_kill` |
| TM65 | the walk reads a `partial def`'s compiled body (`_unsafe_rec`) (hunt R1) | `(Lean.getInitFnNameFor? env c).toList` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R1]` |
| TM66 | a check that runs IO (`unsafeIO`, an `initialize`d value) never kills (hunt R2, R6) | `if False:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R2]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[R6]` |
| TM67 | a kill needs every definition the check reads, outside the mutated one, as without the mutant (hunt R8) | `if drift := None:` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R8]` |
| TM68 | the probe elaborates a file as the build does, with the module's options (hunt R5) | `said = lake({**env, "TM_TRUST_NONCE": nonce}, "env", "lean", str(pa...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R5]` |
| TM69 | a `#guard_msgs` diff kills only when the check's truth changed: one side empty (hunt R7) | `return expected is not None and generated is not None and expected ...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R7]` |
| TM70 | a parse error counts as a refusal only inside the mutant's own text, not one the tool's padding made (hunt R3) | `return not NO_ANSWER.search(message) and bool(PARSE.match(message) ...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[R3]`, `test_invalid_needs_every_error_of_the_mutated_declaration_to_be_a_refusal` |
| TM71 | only the mutated declaration and what Lean generated for it (its owner, its source range) are exempt from the comparison (hunt S1, S2, T5) | `let o := mutated` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S1]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[S2]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[T5]` |
| TM72 | every constant a check reaches is compared, through the mutated definition too (hunt S3, T3) | `if !(info matches .thmInfo _) && !(← inside c) && !(seen.toList.any...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S3]`, `test_a_hunt_form_gets_no_verdict_that_hides_it[T3]` |
| TM73 | IO is known by its types, not by the `unsafe*IO` names (hunt S5) | `let io := [``unsafeBaseIO, ``unsafeEIO, ``unsafeIO]` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S5]` |
| TM74 | the walk reads every package but Lean's own core (hunt S6) | `fun i => [`Init, `Std, `Lean, `Lake, `Helper].any` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S6]` |
| TM75 | the probe reads only lines with its own nonce (hunt S7) | `if line.startswith(nonce + " "): line = line[len(nonce) + 1:] name,...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S7]` |
| TM76 | the probe elaborates a module at its own path, with its library's options (hunt S8) | `return lean.parent / f"probe-{Path(f).name}" if Path(f).is_absolute...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S8]` |
| TM77 | every theorem `@f = @g` is a possible `@[csimp]` lemma, a `local` one included (hunt S9) | `if let some (.thmInfo info) := (env.find? t).filter (fun _ => (Lean...` | `test_a_hunt_form_gets_no_verdict_that_hides_it[S9]` |
| TM78 | a check that computes through an axiom of the tree never kills (hunt T1) | `pure ()` | `test_a_hunt_form_gets_no_verdict_that_hides_it[T1]` |
| TM79 | a mutant's build past `--build-timeout` is killed and the mutant UNKNOWN, never a hung run (hunt T5w, T7) | `out, err = child.communicate()` | `test_a_build_past_its_time_limit_is_unknown` |
| TM80 | the modules an outside --test file imports are built with the mutant (review F13) | `tree.imported` left out of `targets` | `test_probe_f13_an_outside_check_reads_its_imports_built_with_the_mutant` |
| TM81 | an outside --test file whose imports cannot be read stops the run (review F13) | the header error not reported | `test_an_outside_test_whose_header_cannot_be_read_stops_the_run` |
| TM82 | a sentence that states a result is UNBOUND unless each such word lies inside a text the evidence gives (review F14's class) | `loose = []` | `hunt/F15c.sh` |
| TM83 | a PROBE list binds only when every probe it names, a range expanded, exits 0 in `evidence/probes.json` | a range not expanded | `names()` on "F1, F6–F9 and N4" (`mutants.json`) |
| TM84 | the report's budget line is `replay.py`'s, from the saved evidence and the 1,200 s budget (review F14) | `BUDGET = 2000` | `hunt/F14c.sh` |
| TM85 | the probes' summary counts only the probes that exit 0; the README and the report quote it | exit 1 counted as 0 | `hunt/F14c.sh` |
| TM86 | a count reads up to three words between the number and what it counts (review F15) | one word | `hunt/F15c.sh` |
| TM87 | "N each" is a count (review F15's class) | the form dropped | `hunt/F15c.sh` |
| TM88 | "about N" is a count | the form dropped | `hunt/F15c.sh` |
| TM89 | "all N" is a count | the form dropped | `hunt/F15c.sh` |
| TM90 | a number of lines is a count | `lines` dropped from `COUNTED` | `hunt/F15c.sh` |
| TM91 | a number inside a name (ap-2, F14) is no count | `\b` in place of the name guard | `hunt/F15c.sh` |
| TM92 | a sentence that starts with a digit is a sentence of its own | no split before a digit | `hunt/F15c.sh` |
| TM93 | section 5's test sizes are measured from the test file | one of F9's two runs of lines left out | `parts()` against section 5 (`mutants.json`) |
| TM94 | a cell of the step-1 table that differs from `replay.py`'s row is UNBOUND (review F16) | every row OK | `hunt/F16.sh` |
| TM95 | every column of the table is compared, the yes/no columns included | the first five columns only | `hunt/F16c.sh` |
| TM96 | a named sentence whose numbers the evidence does not give is UNBOUND (review F16) | any numbers OK | `hunt/F16.sh` |
| TM97 | a named sentence missing from the report is UNBOUND | a missing one not reported | `hunt/F16c.sh` |
| TM98 | the saved probes hold for the report they ran on: its sha256 is saved (the recheck's C item) | `REPORT.md` left out of `SOURCES` | `hunt/F14c.sh` |
| TM99 | the report's quote of the probes' summary, written after the run, is left out of its sha256 | the quote hashed | `hunt/F14c.sh` |

## 4. Limits and follow-ups

- Outside the operators (step 1 shows each needs a reviewer today): a premise or conjunct dropped (qt-a1's
  `Admitted`), an argument replaced by a constant (pk-1's `fullEnv`), one list swapped for a sibling list (ap-2 F7's
  31o and 31i), a reserved list swapped for another (`mresv`), fault order. Follow-up: add them where step 1 says.
- The mutation sites are found on the blanked text, not by Lean; Lean decides each mutant (INVALID when it does not
  elaborate), so a site misread costs a build, never a verdict. 7–35 of each replay's mutants are INVALID.
- Checks are built from the mutated module's directory by default; a check elsewhere that does exercise the
  definition is reached only by `--deep`, `--test` or a check whose statement names it. A survivor may therefore
  be false (fail closed), never a kill.
- A tactic-proved `example` or theorem never kills, even when the mutant makes its statement false: the tool cannot
  tell that from a proof script that breaks on a true statement (review F1), so such a definition shows survivors
  until a `#guard` or a `decide`/`rfl` check reads it (qt-a1: 133 survivors, no kill).
- A `#guard_msgs` whose spec spans lines is not read as a wrapper: it is no check, and a proof under it cannot
  lose it, so its failure is UNKNOWN (fail closed), unless the control shows it fails without the mutant (then it
  is cut).
- A check that reads a proof the tool cuts is cut in that mutant's build (section 1a), so it cannot kill there even
  when the mutant also changes the value it reads (the sweep's `#eval` rows): a survivor may be false, never a
  kill. An outside `--test` file that fails without the mutant cannot be cut (the tool only reads it), so the
  mutant is UNKNOWN.
- Each control is one more build per stage and set of cuts, cached across mutants; a mutant whose broken proofs
  differ needs its own. The F8-tool replays measure no added time for the controls (section 1); the probe of
  section 1e does add time: ap-2 F11 took 1,917 s with the final tool against 276 s with the F8 tool, over step
  1's budget; the probe is about 1,160 s of it (section 1). A waiver, or a faster probe, is the DRI's decision.
- The probes ran on the final tool (`evidence/probes.json`). The sweep ran on the tool of `f49efae15` (section 1a),
  the seeded bugs on the commits section 3 names; of the replays only ap-2 F11 ran on the final tool, the other
  five are the F8 tool's (section 1).
- Since F11 a kill comes only from `#guard`, a `decide`/`native_decide` `example` or theorem, an `rfl` one that
  `decide` then refutes, or one of those under `#guard_msgs` whose truth changed. A definition read only by
  `#eval`, `#reduce`, `#check` or `#guard_expr` shows UNKNOWN (a failure there states no refutation) or SURVIVOR;
  write a `#guard` for it. A named theorem in an outside `--test` file is no check (the tool reads its commands
  without compiled declarations: unrecorded).
- The kill rule rests on a probe (`READS`, Lean inside the tool) that runs per kill in the mutant's build: its
  walk, hash and flags are this item's reading of what a check computes through. Seven hunts found forms it missed
  (section 1e); the class is open, and the decided boundaries there (N4, H6, T6) are for the recheck to judge.
- INVALID is narrower: 12 of ap-2 F11's 21 are now UNKNOWN (a refusal outside the mutant's own text), so a run
  shows more UNKNOWN to allow-list or investigate.
- A mutant whose build runs past `--build-timeout` is UNKNOWN; raise it for a slow tree.
- A check that runs out of Lean's budget, or whose `decide` gets stuck, gives no answer (section 1d): the mutant
  is UNKNOWN even when another check refutes it (every error must kill), so raise that check's budget
  (`set_option maxRecDepth … in`) to decide it. Since F11 the verdict rests on `REFUTED` (Lean 4.24's refutation
  messages, matched whole): a toolchain that rewords one makes those kills UNKNOWN (fail closed), and the `BUDGET`,
  `STUCK` and `JUDGED` rows fail; `NO_ANSWER` only marks the detail.
- A longer replacement with no blank line after its declaration to take its extra lines is UNKNOWN (fail closed),
  and so is any parse error outside the mutated declaration; the six replays have neither.
- A build that fails with no located error is retried twice, then UNKNOWN; a control that fails that way is not
  cached (it would make every mutant sharing it UNKNOWN): under load a test that expects a SURVIVOR can then see
  UNKNOWN (fail closed, never a kill).
- A proof term inside a definition (not a theorem or `example`) that fails cannot be cut, so the mutant is UNKNOWN
  (pk-1: 5, at `Readings/UnspecifiedWire.lean:526`).
- Equivalent mutants (for example `.take 1` of a list that always has one element) are not detected; they go in the
  allow file with a reason.

## 5. Task lines and where they are delivered

| Task line | Delivered by |
|---|---|
| 1 MEASURE: operators first, replays on pk-1 6b58a0ff, qt-a1 b20a8e30, ap-2 584ac3bb and the recheck HEADs; table; stop rule | section 1; `replay.py`, `evidence/*.json`; 6 of 6 flagged |
| 2 `tools/trust_mutants.py`: `--base`, trust_map classification ∩ diff, scratch copy with lean_share's build, only importing check modules plus `--test`, kill rule, SURVIVOR line, `--allow`, `--jobs`, `--max-mutants` with NOT RUN, `--json`, time budget | the tool; times in section 1. The 20-minute budget: **not met** (ap-2 F11 took 1,917 s with the final tool, the probe of section 1e about 1,160 s of it; `replay.py`'s budget and profile lines; review F14), escalated to the DRI for a waiver |
| 3 tests in a new `tests/test_trust_mutants.py` (six behaviours) and one seeded bug per rule | section 3; TM1–TM40 |
| Review F7 (DRI note 2026-10-19): the class, the truth table, probes F1, F6, F7 and a sweep, REPORT:27 | section 1a; `sweep.py`, `evidence/sweep.json`; the check rule in section 1 |
| Recheck F8: a definition's error beside a failing check, probe F8 | section 1b; TM25; replays and sweep rerun |
| Recheck F9 (DRI note 2026-10-19b): no edit moves a line or the mutant is UNKNOWN, a kill is a check's own error, the line axis and F8's form in the tables, probes F1, F6–F9, a sweep, 25 seeded bugs still killed | section 1c; `relined`, `moved`, `attributed`; `LINES`, `lines_package`; `sweep.py`; TM26–TM32 (32 of 32) |
| Recheck F10: a check out of budget counts as a kill; probe F10 | section 1d; `NO_ANSWER`, `ERROR`; `BUDGET`, `budget_package`; `replay.py` F10 line; sweep rerun; TM33–TM40 (40 of 40) |
| Recheck F11/F12 (DRI note 2026-10-19c): the rule inverted (one positive condition for KILLED and for INVALID), a test per safe case, F11 and F12 as tests, an adversarial hunt until none (bounded by the 23Z addendum for later rounds), probes F1 and F6–F12, the sweep, the seeded bugs | section 1e; `settle`, `judge`, `refutes`, `invalid`, `refused`, `READS`/`probe`; `JUDGED`, `REFUSALS`, `STUCK`, `HUNT`; `docs/speed/trustmut/hunt/`; sweep and ap-2 F11 replay rerun; TM41–TM79 (37 seeds) |
| Recheck F13/F14: an outside check's imports built with the mutant; the budget claim; probes F13, F14 | section 1f; `Tree.imported`, `targets`; `BRIDGED`; `replay.py` `budget()`; `hunt/F13.sh`, `hunt/F14.sh`; TM80, TM81 |
| Round 4 (DRI note 2026-10-20): F14 as a class (the claim sentences `CLAIM` reads checked against the evidence, the list in the final); PROBE F13 and F14 rerun; ap-2 F11 (`aa2fd56e3`) with the final tool, timed once at 8 jobs, the load recorded, and whether the probe causes the excess | section 1f; `claims.py`, `hunt/run.py`, `evidence/probes.json`, `hunt/F14c.sh`; `replay.py` `profiled`, `profile()`; section 1 |
| Recheck F15: section 4's INVALID range against the evidence; `CLAIM` reads that form; PROBE F15 | section 1f; `COUNT`, `COUNTED`, `parts()`; `hunt/F15.sh`, `hunt/F15c.sh`, `hunt/F15c.md`; TM86–TM93 |
| Recheck F16 (DRI note 2026-10-20b): the step-1 table cell by cell, the named counts bound one by one, the claim narrowed to what `claims.py` checks, PROBE F16 and F14–F15c rerun, the claim inputs in the probes' hashes | section 1f; `tabled()`, `named()`, `bindings()`; `hunt/run.py` `SOURCES`; `hunt/F16.sh`, `hunt/F16c.sh`; TM94–TM98 |
| 4 orchestrator lines, gate-check opinion | section 2 |
| Rules: R2/R3 unchanged, nothing reads the tool; `trust_map.py --check`, review-ready and gate unchanged; no timing test | `DELTA.md`; no file of the gate or review-ready changed; trust_map's two changes (F6, F7) measure +0 here; the tests assert no time |
| Trust +0; DELTA rows only with a ruling, none reserved | `DELTA.md` has no rows |
| Size: at most ~500 changed lines outside generated files | over: see below |

Size: about 5,700 changed lines outside the generated `tests/history-dependent.json` and the saved evidence
(`evidence/*.json`, `mutants-evidence.json`, the hunt probes), against the merge base (`git diff --numstat`): most
of it is the tool, the test, the seeded bugs' `mutants.json` and this report. That is over eleven times the guideline. The size rule's
fallback is to deliver steps 1-3 for the operators step 1 showed matter; every operator but `arm-default`,
`body-true`/`body-false`, `ne-eq`, `all-any` and `append-*` left a survivor on a finding's line, and removing those
saves only their entries in `OPERATORS` and the few generator lines that write them, so all are kept. The bulk is the runner the task asks for (selection, scratch copies with
the shared build, staged builds, proof cuts, control builds, the kill rule) and the review rounds' tests (the
F7 truth table and its package are about 230 of the test's lines, F9's line axis about 160, F10's budget
table about 150), and splitting it
would leave no usable tool.

## 6. Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; the tool reads Lake's build log, and a failure it cannot place is UNKNOWN.
2. PASS: section 5 maps every task line to its delivery; no rule break (no product code, no permanent report
   test: `replay.py` and `claims.py` read saved evidence, D4).
3. PASS: seeded bugs TM1–TM93, 91 (`mutants.json`, `mutants-evidence.json`), each failing its named test or command;
   `--allow` names an exact (definition, operator) pair (`test_allow_suppresses_exactly_its_operator`).
4. N.A.: no Python, Lean or Rust product code changed.
5. N.A.: no relayed field.
6. PASS: based on main at cb033316a; the chain runs the gate on the final HEAD.
7. PASS: DELTA has no rows and reserves nothing; trust +0 (no Lean file changed).
8. PASS: `git diff --stat main...HEAD -- ve lean rust conformance` is empty.
9. PASS: the tests `tools/select_tests.py` selects, `tests/test_trust_mutants.py` among them (`repo_map.py file
   tools/trust_mutants.py`), on the Mac runner (`evidence/selected.json`) on `a71b9c573`: 32 units, exit 0; `lake build` exits 0 and
   `python3 lean/audit.py` exits 0 there (no Lean file changed).
10. N.A.: no Lean statement or proof.
11. PASS: `--max-mutants 0` runs nothing and exits 3, never 0 (`test_max_mutants_lists_the_rest_as_not_run[0]`).
12. N.A.: no product code; the tool's own times are in section 1.
13. N.A.: no test of main removed or renamed; `tools/gate_collection.py --check`: 301 added, 0 removed by a trailer,
    0 refused, 0 stale and 0 malformed trailers.
