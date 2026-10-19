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
cuts and the roles, which read the checkout's line numbers, read the mutated text right. A mutant Lean refuses
inside the mutated declaration is INVALID: the compiler decides what a mutant means, never the text. A check is a command whose outcome Lean computes from definitions alone, never from a proof (`classify`
in the tool, the one rule every module goes through): `#guard`, `#guard_expr`, `#eval`, `#reduce`, `#check`, or an
`example` or theorem proved by `decide`/`native_decide`/`rfl`, with no other tactic block in it; a
`#guard_msgs … in` is the command it wraps, bare or with its docstring. Every other `example` or theorem is a proof,
whatever its statement names, and so are a check form with a tactic block inside and every `#print` (`#print axioms`
included). A failing proof is cut to `sorry` (a `#` command blanked, with its docstring) and the build repeated
before any other error is read, so it is never a kill (BUILDER-CHECKLIST 3; pk-1's `assemble_wellFormed`); an error
in a check kills only when the same build without the mutant passes (section 1a), and only when it is the check's
own error: at a line the checkout has there, and no parse error (section 1c). Any other command is no check: an
error there is UNKNOWN, and so is an error in a definition, even beside a failing check (section 1b). The modules
built for a mutant are those of the mutated module's directory that hold checks, and any module of its cone holding a check whose compiled statement
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
but one `rfl` theorem's "Not a definitional equality"), and `relined` only changes an edit that adds lines. "Survivors on the named lines" are survivors on a line the
review names for that finding; "within the default 60" says whether one of them is among the first 60 mutants of
the tool's order:

| Finding | HEAD | Mutants (run / survivors / invalid / unknown) | Seconds at 8 jobs | Survivors on the named lines | Flagged | Within the default 60 |
|---|---|---|---|---|---|---|
| pk-1 F1 | `6b58a0ff7` | 248 / 91 / 35 / 5 | 1027 | 10: `Packs.lean:423` list-empty; `Packs.lean:423` list-first; `Packs.lean:423` list-drop-last; `Packs.lean:423` list-last; `Packs.lean:423` list-drop-first | yes | yes |
| qt-a1 F1 | `b20a8e306` | 140 / 133 / 7 / 0 | 231 | 43: `Semantics.lean:24` arm-true; `Semantics.lean:52` arm-true; `Semantics.lean:24` arm-false; `Semantics.lean:52` arm-false; `Semantics.lean:14` not-drop; `Semantics.lean:55` not-drop ... | yes | yes |
| ap-2 F1 | `584ac3bb3` | 413 / 117 / 21 / 0 | 327 | 29: `Syntax.lean:80` lt-le; `Read.lean:19` lit-plus; `Read.lean:19` lit-minus; `Syntax.lean:80` lit-minus; `Syntax.lean:119` any-all; `Syntax.lean:119` list-empty ... | yes | yes |
| ap-2 F7 | `e13a4e413` | 413 / 59 / 21 / 0 | 372 | 18: `Syntax.lean:119` any-all; `Syntax.lean:83` list-first; `Syntax.lean:96` list-first; `Syntax.lean:113` list-first; `Syntax.lean:113` list-drop-last; `Syntax.lean:119` list-first ... | yes | yes |
| ap-2 F10 | `3d1085285` | 413 / 35 / 21 / 0 | 300 | 4: `Syntax.lean:78` list-first; `Syntax.lean:78` list-last; `Syntax.lean:79` list-last | yes | no |
| ap-2 F11 | `aa2fd56e3` | 413 / 33 / 21 / 0 | 276 | 6: `Syntax.lean:88` list-drop-last; `Syntax.lean:122` list-first; `Syntax.lean:122` list-drop-last; `Syntax.lean:89` list-drop-first; `Syntax.lean:121` list-last; `Syntax.lean:121` list-drop-first | yes | no |

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

Times (the "Seconds" column, measured with the final tool after the F8 fix, 8 jobs on the 32-core VM, 5-minute
load 14–31 while other work ran): every replay is within the 20-minute budget. qt-a1 took 231 s, the four ap-2
HEADs 276–372 s, and pk-1 1027 s: its mutated modules (`Packs.lean`, `PacksLegacy.lean`) are proof-heavy. The F7
round measured 222 s, 255–275 s and 733 s at load 3–12, and the F1 round 299 s, 280–485 s and 873 s under a load
up to 30, so the control builds of section 1a add
no measurable time on these trees (no check there fails without the mutant, so each control is built once per
stage and set of cuts, and cached). A first pk-1 run that built every check module importing the mutated one, not
only those of its directory, was stopped after an hour at load 51; that is why `--deep` is opt-in.

## 1a. Review fix F7: a check whose outcome a proof can change never kills

F7 was the third form of one class (F1, F6, F7): a command counted as a check while its outcome depends on a
proof that the mutant breaks or that the tool cuts to `sorry`. `#guard_msgs in #print axioms T` lists `sorryAx`
once T's proof is cut, so in the mutated module (proofs cut up front) every mutant was KILLED (27 of 27 in the
review's probe, known survivors included). Lean 4.24 also refuses `#eval` of a value that depends on `sorry`
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
| `#guard_expr` | check | compares terms by definitional equality | KILLED | SURVIVOR |
| `#eval` | check | evaluates; refuses `sorry`, which the control catches | KILLED | SURVIVOR (control) |
| `#reduce` | check | reduces; proofs are not reduced | KILLED with its docstring; SURVIVOR bare or `(drop info)` (nothing compares the output) | SURVIVOR |
| `#check` | check | elaborates the term against its type; proofs show as `⋯` | KILLED | SURVIVOR |
| `#print` | proof | shows a theorem's proof term and a definition's text | SURVIVOR | SURVIVOR |
| `#print axioms` | proof | lists `sorryAx` once a proof is cut | SURVIVOR | SURVIVOR |
| `decide` `example` | check | kernel reduction of a decision procedure | KILLED | SURVIVOR |
| `rfl` `example` | check | definitional equality | KILLED | SURVIVOR |
| tactic `example` | proof | a proof script (review F1) | SURVIVOR | SURVIVOR |
| tactic theorem | proof | a proof script (review F1) | SURVIVOR | SURVIVOR |
| `#guard` with a tactic block | proof | the mutant breaks the tactic, not the comparison | SURVIVOR | (its tactic is the proof) |
| a definition with a proof inside it, a `#guard` of its value beside it (F8's form, added for F9) | other | a definition cannot be cut; the mutant breaks its `by decide` | UNKNOWN | SURVIVOR |

Every row holds in both settings and all three wrappings: `test_the_truth_table_statuses` runs the package (the
definitions `n + 0`, one mutant each; 56 definitions, the rows that must survive sharing one per wrapping, setting
and reading; the rows' own definitions are classed T in the package's trust-classes.json, so only `r` is mutated) and `test_the_truth_table_classes` checks each row's role on the package's own spans;
`test_classify_truth_table` and `test_classify_reads_every_command` check `classify` alone, with the spellings
`#eval!`, `set_option … in`, nested wrappers, `#synth`, `#check_failure` and `#exit`.

The sweep (`docs/speed/trustmut/sweep.py --run`, evidence `evidence/sweep.json` with the sha256 of the tool, of
`trust_map.py` and of the tables it ran): the same table with the rich body `!(n < 1) && (n ≤ 3 || decide (n = 5))
&& n != 2 && ([n] ++ [1]).all (· ≥ 1) && [n, 3].any (· == 3) && true`, which carries every operator of the test
package and every other operator but the arms (54 mutants each), and the value read as `(List.range 6).map r`; the
arms and the multi-line forms are the F9 table (section 1c), in the same run. All 3,024 mutants ran (926 s at 16
jobs on the final tool after F9): 1,330 KILLED, 1,484 SURVIVOR, 210 UNKNOWN, 0 INVALID. No row that reads a proof,
and no row that is no check, has a KILLED mutant; every row expected to kill does; the UNKNOWN are exactly the
non-equivalent mutants of the six definitions F8's form reads (35 each), UNKNOWN at that definition. The
definitions a check or F8's definition reads keep 19 survivors each (38 + 6 such definitions), all equivalent
mutants, equal to the original on every `n`, not only on 0..5:
- the conjunct `([n] ++ [1]).all (· ≥ 1)` is true whenever `!(n < 1)` is, so its 16 mutants change nothing:
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
| `default-more`: `\| 0 => [7]`, `\| _ => [2,⏎3]` (PROBE F9's form) | `arm-default`: more | KILLED (16 of 16) | SURVIVOR (16 of 16) |
| `default-more-tight`: the same, no blank line after it | `arm-default`: more | UNKNOWN ("moves this line"), the other 15 KILLED | UNKNOWN, the other 15 SURVIVOR |
| `default-fewer`: `\| 0 => [7,⏎8]`, `\| _ => [2]` | `arm-default`: fewer | KILLED (16) | SURVIVOR (16) |
| `default-same`: `\| 0 => [7]`, `\| _ => [2]` | `arm-default`: same | KILLED (12) | SURVIVOR (12) |
| `arm-bool`: `\| 0 => 1 <⏎2`, `\| _ => 2 < 1` | `arm-false`: fewer, `arm-true`: same | KILLED (6), 11 SURVIVOR (equivalent, below) | SURVIVOR (17) |
| `list-multi`: `[n,⏎5]` | `list-first`, `list-drop-last`: same; `list-empty`: fewer | KILLED (7) | SURVIVOR (7) |
| `list-single`: `[n, 5]` | `list-first`, `list-drop-last`, `list-empty`: same | KILLED (7) | SURVIVOR (7) |
| `append-left-multi`: `[n] ++ [5,⏎6]` | `append-left`: fewer, `append-right`: same | KILLED (19) | SURVIVOR (19) |
| `append-right-multi`: `[n,⏎5] ++ [6]` | `append-right`: fewer, `append-left`: same | KILLED (19) | SURVIVOR (19) |

Each row holds in both settings (36 definitions, 516 mutants, every one run: 234 KILLED, 278 SURVIVOR, 4 UNKNOWN,
0 INVALID; the sweep's evidence, and `test_a_replacement_of_any_line_count_is_decided_by_the_checks` on the same
package, both through `lines_problems`). Every KILLED is at its own comparing check's line, and no mutant of a
definition no check reads is KILLED. Only `arm-default` can write more lines: `arm-true`/`arm-false` write one
token, the list cuts wrap the list they cut (`(xs.take 1)` has its lines), `list-empty` and `append-*` write one
line or none, and the token operators keep the line. The 22 survivors of the compared rows are all `arm-bool`'s and
all equivalent (each arm keeps its value on every `n`): `arm-true` of `1 <⏎2` and `arm-false` of `2 < 1` (each
arm's own value), `1 <⏎2` read as `1 ≤ 2`, `0 < 2` or `1 < 3` (still true), and `2 < 1` read as `2 ≤ 1`, `2 = 1`,
`2 < 0`, `1 < 1`, `2 < 2` or `3 < 1` (still false).

PROBE F1, F6, F7, F8 and F9 pass on the final tool (F9: `[('arm-default', 'SURVIVOR', '')]`, exit 0, where it
printed KILLED at `Defs.lean:11: unexpected token '<;>'` before the fix). The seeded bugs TM26–TM32 plant each
rule of the fix (section 3).

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
`tmp_path` and `VE_LEAN_SHARE=off`; a second package is the truth table of section 1a (`table_package`), a third
the line axis of section 1c (`lines_package`), and the generator, the check rule (`classify`), the spans, the
cuts, the line-keeping edit (`relined`, `moved`) and the kill rule (`attributed`) have tests without Lean. Each rule has a seeded bug
in `docs/speed/trustmut/mutants.json` (the `tools/mutants.py` format); `uv run python tools/mutants.py
docs/speed/trustmut/mutants.json` kills 32 of 32, each at its named test, the file restored to its exact bytes
(`mutants-evidence.json`, run on the final tool). Python is the only language whose code changed (no Lean, no
Rust). The parametrized tests have ids without spaces: `tools/mutants.py` reads a failing id up to its first space,
so TM14, TM19 and TM24 first showed as survivors although their tests failed.

| Mutant | Rule | Bug planted in `tools/trust_mutants.py` | Failing test |
|---|---|---|---|
| TM1 | a failing proof is cut and the build repeated, never left to decide the mutant | failing proofs are not cut | `test_a_failing_proof_is_no_kill` |
| TM2 | the importing check modules are built | the second build stage is empty | `test_a_well_guarded_definition_has_no_survivor` |
| TM3 | a guard over `[]` leaves a survivor | `list-empty` leaves the list unchanged | `test_a_guard_over_the_empty_list_leaves_survivors` |
| TM4 | `--allow` suppresses exactly its operator | any operator of the definition is allowed | `test_allow_suppresses_exactly_its_operator` |
| TM5 | a scratch copy is used | the scratch sources are hard links to the checkout | `test_mutants_are_built_in_a_scratch_copy` |
| TM6 | the rest are listed as NOT RUN | only the first NOT RUN row prints | `test_max_mutants_lists_the_rest_as_not_run` |
| TM7 | every list method's receiver is cut | `find?` unescaped in `LIST_METHODS` (a real regression of the rewrite, caught by the ap-2 replays) | `test_the_generator_cuts_every_list_a_condition_reads` |
| TM8 | an `example` is a check only when `decide`/`native_decide`/`rfl` proves it (review F1) | every `example` is a check | `test_an_example_proved_by_a_tactic_is_no_kill` |
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
| TM22 | an outside `--test` file kills only when it passes without the mutant (F7) | any failing file kills | `test_an_outside_test_that_fails_without_the_mutant_is_no_kill` |
| TM23 | only an error in a check (or a `--test` file) kills; one in a definition is UNKNOWN | any error kills (since F9 on `attributed`) | `test_an_error_outside_every_check_is_unknown` |
| TM24 | the blanking stops at a string the command before is still writing (F7) | it does not | `test_a_cut_command_is_blanked_with_its_docstring` |
| TM25 | an error in a definition is UNKNOWN even beside a failing check (F8) | a failing check wins (since F9 on `attributed`) | `test_an_error_in_a_definition_beside_a_failing_check_is_unknown` |
| TM26 | a longer replacement takes its extra line ends from the blank lines after its declaration (F9) | it never does | `test_an_edit_keeps_every_line_after_its_declaration`, `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |
| TM27 | those blank lines are never inside a comment (F9) | the comment test dropped | `test_an_edit_keeps_every_line_after_its_declaration` |
| TM28 | a mutant that moves a line after its declaration is UNKNOWN (F9) | no guard | `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |
| TM29 | the guard compares each line, not only the count (F9) | it compares the count | `test_moved_finds_the_first_line_after_the_declaration_that_moved` (first named the edit test, where it survived: no case there keeps the count and moves a line; the new test has one) |
| TM30 | a parse error never kills (F9) | the parse test dropped | `test_only_a_checks_own_error_kills` |
| TM31 | a check's error kills only at a line the checkout has there (F9) | any check line kills | `test_only_a_checks_own_error_kills` |
| TM32 | the mutated declaration's lines run over the blank lines its edit takes (F9) | they end where the declaration did | `test_a_replacement_of_any_line_count_is_decided_by_the_checks` |

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
- A `#guard_msgs` whose spec spans lines is not read as a wrapper: it is no check, and a proof under it cannot
  lose it, so its failure is UNKNOWN (fail closed), unless the control shows it fails without the mutant (then it
  is cut).
- A check that reads a proof the tool cuts is cut in that mutant's build (section 1a), so it cannot kill there even
  when the mutant also changes the value it reads (the sweep's `#eval` rows): a survivor may be false, never a
  kill. An outside `--test` file that fails without the mutant cannot be cut (the tool only reads it), so the
  mutant is UNKNOWN.
- Each control is one more build per stage and set of cuts, cached across mutants; a mutant whose broken proofs
  differ needs its own. The replays measure no added time (section 1).
- The sweep and the seeded bugs ran on the final tool (after F9); the replays on the tool after F8, which F9 changes
  for none of their mutants (section 1).
- A longer replacement with no blank line after its declaration to take its extra lines is UNKNOWN (fail closed),
  and so is any parse error outside the mutated declaration; the six replays have neither.
- A build that fails with no located error is retried twice, then UNKNOWN; a control that fails that way is not
  cached (it would make every mutant sharing it UNKNOWN). In the final selected run on the Mac runner (six test
  files at once) `test_a_guard_over_the_empty_list_leaves_survivors` failed once at its exact `SURVIVOR` line and
  passed when rerun alone; its log was gone, so the cause is not known. An unlocated Lake failure under load would
  give that (an UNKNOWN in place of the survivor: fail closed, never a kill).
- A proof term inside a definition (not a theorem or `example`) that fails cannot be cut, so the mutant is UNKNOWN
  (pk-1: 5, at `Readings/UnspecifiedWire.lean:526`).
- Equivalent mutants (for example `.take 1` of a list that always has one element) are not detected; they go in the
  allow file with a reason.

## 5. Task lines and where they are delivered

| Task line | Delivered by |
|---|---|
| 1 MEASURE: operators first, replays on pk-1 6b58a0ff, qt-a1 b20a8e30, ap-2 584ac3bb and the recheck HEADs; table; stop rule | section 1; `replay.py`, `evidence/*.json`; 6 of 6 flagged |
| 2 `tools/trust_mutants.py`: `--base`, trust_map classification ∩ diff, scratch copy with lean_share's build, only importing check modules plus `--test`, kill rule, SURVIVOR line, `--allow`, `--jobs`, `--max-mutants` with NOT RUN, `--json`, time budget | the tool; times in section 1 |
| 3 tests in a new `tests/test_trust_mutants.py` (six behaviours) and one seeded bug per rule | section 3; 115 tests; TM1–TM32 |
| Review F7 (DRI note 2026-10-19): the class, the truth table, probes F1, F6, F7 and a sweep, REPORT:27 | section 1a; `sweep.py`, `evidence/sweep.json`; the check rule in section 1 |
| Recheck F8: a definition's error beside a failing check, probe F8 | section 1b; TM25; replays and sweep rerun |
| Recheck F9 (DRI note 2026-10-19b): no edit moves a line or the mutant is UNKNOWN, a kill is a check's own error, the line axis and F8's form in the tables, probes F1, F6–F9, a sweep, 25 seeded bugs still killed | section 1c; `relined`, `moved`, `attributed`; `LINES`, `lines_package`; `sweep.py`; TM26–TM32 (32 of 32) |
| 4 orchestrator lines, gate-check opinion | section 2 |
| Rules: R2/R3 unchanged, nothing reads the tool; `trust_map.py --check`, review-ready and gate unchanged; no timing test | `DELTA.md`; no file of the gate or review-ready changed; trust_map's two changes (F6, F7) measure +0 here; the tests assert no time |
| Trust +0; DELTA rows only with a ruling, none reserved | `DELTA.md` has no rows |
| Size: at most ~500 changed lines outside generated files | over: see below |

Size: about 2,520 changed lines outside the generated `tests/history-dependent.json` and the saved evidence
(`evidence/*.json`, `mutants-evidence.json`): `tools/trust_mutants.py` 670, the test 800, `replay.py` 107,
`sweep.py` 158, the seeded bugs' `mutants.json` 329, `tools/trust_map.py` 10, this report and DELTA about 445. That
is nearly four times the guideline. The size rule's
fallback is to deliver steps 1-3 for the operators step 1 showed matter; every operator but `arm-default`,
`body-true`/`body-false`, `ne-eq`, `all-any` and `append-*` left a survivor on a finding's line, and removing those
saves under 20 lines, so all are kept. The bulk is the runner the task asks for (selection, scratch copies with
the shared build, staged builds, proof cuts, control builds, the kill rule) and the review rounds' tests (the
F7 truth table and its package are about 250 of the test's lines, F9's line axis about 170), and splitting it
would leave no usable tool.

## 6. Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; the tool reads Lake's build log, and a failure it cannot place is UNKNOWN.
2. PASS: section 5 maps every task line to its delivery; no rule break (no product code, no permanent report
   test: `replay.py` reads saved evidence, D4).
3. PASS: seeded bugs TM1–TM32 (`mutants.json`, `mutants-evidence.json`), each failing its named test;
   `--allow` names an exact (definition, operator) pair (`test_allow_suppresses_exactly_its_operator`).
4. N.A.: no Python, Lean or Rust product code changed.
5. N.A.: no relayed field.
6. PASS: based on main at cb033316a; the chain runs the gate on the final HEAD.
7. PASS: DELTA has no rows and reserves nothing; trust +0 (no Lean file changed).
8. PASS: `git diff --stat main...HEAD -- ve lean rust conformance` is empty.
9. PASS: `tools/select_tests.py` selects 32 units, `tests/test_trust_mutants.py` among them
   (`repo_map.py file tools/trust_mutants.py`); all pass on the Mac runner.
10. N.A.: no Lean statement or proof.
11. PASS: `--max-mutants 0` runs nothing and exits 3, never 0 (`test_max_mutants_lists_the_rest_as_not_run[0]`).
12. N.A.: no product code; the tool's own times are in section 1.
13. N.A.: no test of main removed or renamed; `tools/gate_collection.py --check`: 115 added, 0 refused, 0 stale,
    0 malformed.
