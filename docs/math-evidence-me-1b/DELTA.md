# me-1b delta: the `VE.Calc` meaning and checker

Base `05b85b631` (`git merge-base HEAD main`). me-1b is the second of the three items that replace
foundation/me-1 (reviews/dri-decisions-20261017b.md #6). It carries over me-1's `lean/VE/Calc/Syntax.lean`,
`Eval.lean` and `Decls.lean` (7b93539a4) unchanged and adds `lean/VE/Calc/Examples.lean`, which does not import
`VE.Calc.Render`: its `#guard` fixtures and `example`s exercise every new trusted definition. No Render file is in
this item (me-1c).

**Public output: none.** me-1b registers no service mode, command or route, and no Python or Rust file changes:
`Claim.run`, `Claim.decide` and the meanings are reached only by the Lean build and its fixtures. No diagnostic,
fault order, verdict or English line a user can see changes, so none of this is a row below.

## User-visible deltas

Trust growth, re-measured with `uv run python tools/trust_map.py --check` on the final code: K +0, S +107,
untied V +0, trusted +107 against `05b85b631f80` (`VE/Calc/Decls.lean` +70, `VE/Calc/Syntax.lean` +37,
`VE/Calc/Eval.lean` +0: its three definitions are C, checked by the proofs below). Recorded as one allowance
(S 107) in `docs/trust-baseline.json` with `trust_map.py --allow`; `trust_map.py --check` passes. R16's cap is
150 lines per item, none in K. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section
"## me-1b" (infra item ties-me-1b). Line numbers below are `lean/VE/Calc/Examples.lean`; the seeded bugs that
make these checks fail are in [`mutants.json`](mutants.json). The proofs `Expr.eval_iff`, `Claim.decide_holds`,
`Claim.decide_undefined`, `Claim.decide_fails`, `Claim.run_decided`, `Claim.run_unknown` and
`Claim.run_complete` compile and are audited (`python3 lean/audit.py --check`).

| # | File | Trusted lines (class, declaration: lines) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Calc/Syntax.lean` | +37: S 37 (`Expr` 10, `Values` 2, `Denotes` 10, `Claim` 6, `Claim.Holds` 6, `Claim.Defined` 3) | `example`s 188-224 state `Denotes` (subtraction's operand order, a nonzero divisor, an unknown name), `Claim.Holds` (`within` at both inclusive ends and just outside, a 27/200 rounding, a failing order) and `Claim.Defined` (a defined claim, a zero divisor) from their constructors; `Expr.eval_iff` and `Claim.decide_*` tie them to `Claim.decide`, which the spec-fixture `#guard`s 19-108 pin (V-1, V-2, V-4, V-9, V-10, D-1, H-4, H-5, H-9, DL-1, DL-2, DL-4, the reversed V-2 difference at 40, undefined operands at 103-108); `Expr`, `Values` and `Claim` are the types every check is written in and can fail only by not compiling; seeded bugs 1-3 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 2 | `lean/VE/Calc/Decls.lean` | +70: S 70 (`Counted` 5, `Source` 6, `Decl` 4, `Decl.valueUnder` 7, `values` 3, `WellFormed` 6, `Small` 3, `Val` 4, `NameOverflows` 8, `Expr.Overflows` 4, `Claim.Overflows` 3, `NameExhausted` 7, `Expr.ReadsExhausted` 3, `Claim.ReadsExhausted` 3, `FindingKind` 4) | `#guard`s 148-178: every `Source` and `Counted` kind on both paths (`values`, `Decl.valueUnder`, `Claim.run`; review C4's free and counted sources), a later declaration shadowing an earlier one, an exhausted count read directly and through a definition; 124-145: `Small` at limit − 1, limit and limit + 1 in numerator, denominator and sign, on `Val.guard` and `Claim.run`, and the unknown's text that names the limit (129); 110-122: V-11 and the fault order; 180-184: V-13 (`FindingKind`); `example`s 229-255 (`WellFormed`, and three lists that break each of its conditions), 262-298 (`Claim.Overflows`, `Expr.Overflows`, `NameOverflows` through `.here` and `.dep`, `Claim.ReadsExhausted`, `Expr.ReadsExhausted`, `NameExhausted` through `.here` and `.dep`, and a claim with neither cause); `Claim.run_decided`, `run_unknown` and `run_complete` tie the causes to `Claim.run`; seeded bugs 5-10 | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
| 3 | `lean/VE/Calc/{Syntax,Eval,Decls}.lean`: ties pass (infra item ties-me-1b, R16's FOLLOW-UPS row "## me-1b") | −3: S −3, untied V ±0, K ±0. `values` (3, Decls.lean) moves from S to G[V], tied in `tools/trust-classes.json` to the existing theorems `values_stated`, `values_defined`, `values_free`, `values_counted` and `values_missing`. Per file, trusted before → after: Decls.lean 70 → 67, Syntax.lean 37 → 37, Eval.lean 0 → 0; all files 52,161 → 52,158 (S 10,327 → 10,324, G[V] 27,948 → 27,951, tied 320 → 323). me-1b's growth over main before its merge (`802b8ff9b`) falls from +107 to +104 (S +107 → +104). The 104 lines left are listed, each with why no existing theorem ties it, in "Trust ties pass" below; no allowance is raised or added and no trusted line is written | `python3 tools/trust_map.py --check` on main `c2b1a7d44` PASS before ("against 802b8ff9b1ca: … S +107, … trusted +107") and after the tie (74deff11d, "against c2b1a7d442b4: K +0, S -3, D +0, G +3, tied +3, … trusted -3"); seeded ties M1–M4 each fail `trust_map.py --check` and `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`; Lean mutations L1–L2 of `values` each break `lake build VE.Calc.Decls` in a tying theorem; [`evidence/ties/`](evidence/ties/) | R16 ties pass |

`lean/VE/Calc/Eval.lean` adds no trusted line (`Expr.eval`, `Claim.decide` and `Claim.tieSensitive` are C), so it
has no row; its seeded bug 4 (`tieSensitive` at 54-61) is in `mutants.json`.

## Trust ties pass (infra item ties-me-1b, 2026-10-18)

Row 3. Method: `python3 tools/trust_map.py --check` was run on main with me-1b merged (`c2b1a7d44`), whose base is main
before the merge (`802b8ff9b`). The growth is all in `lean/VE/Calc/`: trusted +107, all S, in Decls.lean (+70) and
Syntax.lean (+37), the 21 declarations of rows 1-2; Eval.lean adds none. For each, every theorem in `lean/statements.txt`
whose `-- uses` line names it was read. All of them are me-1b's own theorems in `VE.Calc`. me-1b registers no service
mode, so there is no render, wire, encoder or decoder theorem. The tool ties only C, D and G declarations, so a tied
declaration moves from S to G[V] (as in ties-qs-1 and ties-me-1a). A tie was added only where the statements, on their
own, fix what the declaration means in terms of declarations that stay trusted, never through a C declaration
(`Expr.eval`, `Claim.decide`, `Claim.run`): those are checked against these meanings, so tying a meaning to them would
let both change together with every theorem still true. ties-me-1a rejected `RoundsTo`'s tie to `Rounding.round` for the
same reason.

### Tie added (commit 74deff11d)

| File | Declaration (lines) | Tying theorems (anchors) | What the statements fix |
| --- | --- | --- | --- |
| `VE/Calc/Decls.lean` | `VE.Calc.values` (3, lines 28-30), S to G[V] | `values_stated` (67), `values_defined` (110), `values_free` (73), `values_counted` (79), `values_missing` (48) (`Decl`, `Source`, `Counted`, `WellFormed`, `Denotes`, `Expr`, all S) | For a `WellFormed` list `ds` and every name `n`: if no declaration is named `n`, `values ds n = none` (`values_missing`); otherwise the one declaration named `n` (names are unique) fixes it by its source: `stated q` gives `some q`, `free` gives `none`, `counted t _` gives `t.get`, and `defined e` gives `some q` exactly when `Denotes (values ds) e q`. In the last case `e` reads only earlier names (the second condition of `WellFormed`), so by induction over the declaration order these statements fix `values ds` completely. It is fixed through `Denotes` and the data types, never through `Decl.valueUnder` or `Expr.eval`, which `values`' definition calls. These are the five statements spec section 2.3 gives as the meaning of `values` |

Shown to be real by two Lean mutations of `values` (each planted alone, then restored; `lake build VE.Calc.Decls`
exit 1). L1 starts the fold at `some 0`, so an undeclared name has a value; the build breaks in `values_missing`
(Decls.lean:50). L2 reads every declaration under the empty valuation, so a defined name no longer sees the names it
reads; the build breaks in `values_defined` (Decls.lean:131), and also in `values_missing` and `values_at`.

What the tie leaves open: on a list that is not `WellFormed`, the statements say nothing about `values`. One such case
is a repeated name, where `#guard` `Examples.lean:169` pins that the later declaration is read. No theorem reads
`values` on such a list: every theorem about `values` and `Claim.run` assumes `WellFormed`, and the spec's decoder
admits only `WellFormed` lists (`Wire.decodeCase_wellFormed`, spec 3.4). So last-wins on a repeated name is held
by that `#guard` alone, not by the tie.

Rejected candidates (the FOLLOW-UPS row lists them; each was checked and not added):

- `Expr.eval_iff` (and `eval_sound`, `Denotes.eval_complete`) for `Denotes`: they fix `Denotes` completely, but only in
  terms of `Expr.eval`, which is C because these theorems check it against `Denotes`. Changing both the same way (say,
  `sub` swaps its operands in each) keeps all three true. `Denotes.unique` says only that `Denotes` is a function. The
  tool would accept `eval_iff` through the binder types `Expr` and `Values`, which say nothing about values.
- `Claim.decide_holds` and `decide_fails` for `Claim.Holds`, and `decide_undefined` and `decide_fails` for
  `Claim.Defined`: the same circle with `Claim.decide` (C).
- `values_stated`, `values_free`, `values_counted`, `values_defined` for `Decl.valueUnder`: their `-- uses` lines do not
  name it, so the tool refuses them. `values_at` (`values ds d.name = d.valueUnder (values pre)`) names it but fixes it
  only through `values`, which is tied here and is no longer an anchor. `Decl.valL_agrees` and `fold_valuesL_agrees`
  use it as the reference that the C path `Decl.valL` is checked against (`Val.Agrees`, P), and `fold_values_other` only
  says the fold leaves other names alone.
- `Claim.run_unknown` and `run_complete` for `Claim.Overflows` and `Claim.ReadsExhausted`, `Expr.evalL_causes` and
  `evalL_causes_on_names` for `Expr.Overflows`, `Expr.ReadsExhausted`, `NameOverflows`, `NameExhausted` and `Small`, and
  `Expr.overflow_lift` and `exhausted_lift`: these bound the C path (`Claim.run`, `Expr.evalL`) by the causes and do not
  fix the causes. Replacing `Claim.Overflows` by `True` keeps `run_unknown` and `run_complete` true (the latter
  vacuously), and the same holds for each other cause in its theorems. The lift theorems are monotonicity facts.
- `findingKind_source_iff` for `findingKind`: `findingKind` is G[R], which is not counted as trusted, so a tie would
  raise `tied` and lower nothing. It also fixes only the `.source` case. `FindingKind`, its anchor, stays S.

### Per-file counts (`trust_map.py`; base `802b8ff9b`, before `c2b1a7d44` (main with me-1b merged), after `74deff11d`)

| File | S before | S after | G[V] before | G[V] after | Tied before | Tied after | Trusted before | Trusted after |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `VE/Calc/Decls.lean` | 70 | 67 | 0 | 3 | 0 | 3 | 70 | 67 |
| `VE/Calc/Syntax.lean` | 37 | 37 | 0 | 0 | 0 | 0 | 37 | 37 |
| `VE/Calc/Eval.lean` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **All files** | **10,327** | **10,324** | **27,948** | **27,951** | **320** | **323** | **52,161** | **52,158** |

No other file changes. K (997) and untied V are unchanged, and the class falls by exactly the 3 tied lines. Saved in
[`evidence/ties/check-before.txt`](evidence/ties/check-before.txt), [`check-after.txt`](evidence/ties/check-after.txt)
(the tie measured against `802b8ff9b`, before it was committed), [`check-after-vs-main.txt`](evidence/ties/check-after-vs-main.txt)
and [`trust-counts.json`](evidence/ties/trust-counts.json). The S 107 allowance of rows 1-2 is untouched; no allowance
is raised or added.

### Declarations no existing theorem ties

None of these was tied, and no trusted code was written to make up for one (104 lines).

| File | Declaration (lines, class) | Why no existing theorem ties it | A theorem that would |
| --- | --- | --- | --- |
| `VE/Calc/Syntax.lean` | `Expr` (10), `Values` (2), `Claim` (6), all S | Data types: the theorems name them as binder types, and they are the anchors of every Calc statement | None: a type is meaning; it stays S |
| `VE/Calc/Syntax.lean` | `Denotes` (10, S) | The meaning of an expression. Its only complete characterisation, `Expr.eval_iff`, goes through `Expr.eval` (C); see the rejected candidates above. It is the anchor of the `values` tie | None in the tree: no earlier profile defines rational arithmetic on expressions to bind it to; it stays S |
| `VE/Calc/Syntax.lean` | `Claim.Holds` (6, S), `Claim.Defined` (3, S) | The meaning of a claim and of "defined". `decide_*` fix them only through `Claim.decide` (C), which they check | None in the tree: they are the meanings `decide` is proved against. When ME-2 registers `calc`, its encoder theorem ties the encoder (D) to the verdict, and these stay S |
| `VE/Calc/Decls.lean` | `Counted` (5), `Source` (6), `Decl` (4), `Val` (4), `FindingKind` (4), all S | Data types; anchors of the `values` tie and of `findingKind_source_iff` | None: they stay S. `Val` is the operational path's result type |
| `VE/Calc/Decls.lean` | `Decl.valueUnder` (7, S) | See the rejected candidates: no statement fixes it in terms of declarations that stay trusted | `valueUnder_eq_some : d.valueUnder σ = some q ↔ d.source = .stated q ∨ (∃ e, d.source = .defined e ∧ Denotes σ e q) ∨ ∃ t r, d.source = .counted t r ∧ t.get = some q` (anchors `Source`, `Denotes`), provable from `Expr.eval_iff`. Not in the tree, and this item adds none |
| `VE/Calc/Decls.lean` | `WellFormed` (6, S) | The admission condition: every `values` and `Claim.run` theorem takes it as a hypothesis, and none fixes it | None that ties it: the spec's `Wire.decodeCase_wellFormed` (ME-2) binds the decoder (D) to it, so it stays S as that tie's anchor |
| `VE/Calc/Decls.lean` | `Small` (3, S) | The digit limit's meaning; `evalL_causes` uses it only in a hypothesis | `small_iff : Small q ↔ q.num.natAbs < 10 ^ maxDigits ∧ q.den < 10 ^ maxDigits` would fix it, but only against core `Nat` power and `maxDigits` (G[R], no anchor), which the tool does not accept (as `tenPow` in ties-me-1a); it stays S |
| `VE/Calc/Decls.lean` | `NameOverflows` (8), `Expr.Overflows` (4), `Claim.Overflows` (3), `NameExhausted` (7), `Expr.ReadsExhausted` (3), `Claim.ReadsExhausted` (3), all S | The causes of an UNKNOWN. The theorems that name them bound `Claim.run` and `Expr.evalL` (C) by them, and none fixes them (see above) | None that is not circular: a converse ("the cause holds → `run` is UNKNOWN") would rest on `Claim.run` (C), and it is false as stated, because an earlier undefined expression decides first (fault order, spec 2.4). They stay S as the anchors of `run_unknown` and `run_complete` |

### Seeded ties (each planted alone on 74deff11d, then restored; `trust_map.py --check` exit 1)

Listed in [`evidence/ties/seeded-ties.json`](evidence/ties/seeded-ties.json), outputs in `evidence/ties/seed-<id>.txt`. Each of
M1–M4 also fails `tests/test_trust_ratchet.py::test_committed_budget_passes_its_check`.

| Id | Seed | File | Failure |
| --- | --- | --- | --- |
| M1 | `values_stated`'s `-- uses` line loses `VE.Calc.values` | `lean/statements.txt` (generated; edited only for the seed) | "the statement of VE.Calc.values_stated does not mention VE.Calc.values of VE.Calc.Decls" |
| M2 | `values_missing`'s `-- uses` line loses its anchors `VE.Calc.Decl` and `VE.Calc.Decl.name` | `lean/statements.txt` | "the statement of VE.Calc.values_missing mentions no K, S or untied [V] declaration of the tree, validly classified, to tie it to" |
| M3 | `values` tied only to the unrelated `VE.Calc.findingKind_source_iff` | `tools/trust-classes.json` | "the statement of VE.Calc.findingKind_source_iff does not mention VE.Calc.values of VE.Calc.Decls" |
| M4 | `values` tied only to `VE.Calc.Denotes.unique` (same profile, about `Denotes` only) | `tools/trust-classes.json` | "the statement of VE.Calc.Denotes.unique does not mention VE.Calc.values of VE.Calc.Decls" |
| L1 | `values` starts its fold at `(fun _ => some 0)` | `lean/VE/Calc/Decls.lean:29` | `lake build VE.Calc.Decls`: "VE/Calc/Decls.lean:50:2: Type mismatch" (`values_missing`) |
| L2 | `values` reads each declaration under `(fun _ => none)` | `lean/VE/Calc/Decls.lean:29` | `lake build VE.Calc.Decls`: "VE/Calc/Decls.lean:131:4: Type mismatch" (`values_defined`) |
