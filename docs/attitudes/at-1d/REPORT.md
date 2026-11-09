# at-1d report: the attitudes Lean core, part four (spec 6.1's statements on `Intended`, the frame and the seed closure)

Status: done at HEAD (the commit carrying this report; Lean final at 2a03f1e30); deliverables (1)-(3) built, the seven statements proved with no change to their text; no signature reserved.
Changed: `Theorems.lean` gains the seven proofs and their helper lemmas; `Examples.lean` gains 7.4's and 7.5's points for each; `ATTITUDES.md` gains at-1d's row.
Trust: theorems (class P) and fixtures (class T) only; no new definition in product code, so no R16 growth, no DELTA row, no FOLLOW-UPS row.
Next item: at-1 (6.1's other eight statements and at-1b-tie's move of `AFormula.toFormula`), then at-2 and at-3a.

Plan: docs/spec/attitudes-PLAN.md "AT-1. Lean core". Spec: docs/spec/attitudes.md 6.1 (lines 1281-1283, 1312-1340, and the
proof notes at 1345-1352), 2.8, 7.2, 7.4, 7.5. Statement gate: AT-0 is done (reviews/dri-decisions-20261103-fp-attitudes-r2.md
item 3). The split from AT-1 is the feature planner's of 2026-11-09 (reviews/dri-decisions-20261102-attitudes-scope.md item 1).

## Deliverables

| Task line | Delivered | Commit | Check |
|---|---|---|---|
| (1) `knows_factive`, `seed_intended`, `seed_least`, `mistaken_belief_admissible`, each with 7.5's guard or a Prop example on F-AT1's points | proved; `mistaken_belief_admissible` is `seed_intended` at the seed `[(k, vs)]`, as the spec says. Examples: no intended model with the category false holds `knows` (M2's tuple); the closure of the seed [knows] at the category true is intended; `thinks quite likely` held of the false category (M1); every intended model holding `knows` holds `thinks quite likely` | 17e61342c, 05a52dfdf | `lake build VE.Attitudes.Examples`; section "Runs" |
| Size after (1) | a deviation in order: the seven proofs went in one commit (17e61342c) because they share their helper lemmas, so the size was measured after the proofs and the gate: 307 lines (`Theorems.lean` 266, `spec_text_check.py` 41), and after the examples 446. Both are under the ~700 seam, so the outcome is the one the order guards | d10feeeb2 | `git diff --numstat` (section "Size") |
| (2) `forced_iff_reachable` (both directions) and `frame_iff_intended` (both directions, each pinned where the frame and `Intended` both fail) | proved. `forced_iff_reachable` is `seed_intended` and `seed_least` together; its reachability side is at-1c's `seedClosure`. 7.4's row: [knows] forces and reaches `thinks quite likely`; [thinks] does not force `knows`; [knows] does not force `intends`, nor `thinks quite likely` at another holder (instance `2`). `frame_iff_intended`: both sides at M1, M4; neither at M2 (left to right: M2 is not intended, so the frame fails) and at M3 (right to left: the broken pair breaks the frame, so M3 is not intended); and right to left on F-AT7 with very likely's item (premise 3) | 17e61342c, 05a52dfdf | the examples under "`frame_iff_intended` (7.4, 7.5)" and "F-AT7 with very likely's item" |
| (3) `guard_collapse`, with guards where the collapse fails without the pair and where the holders differ | proved (the third conjunct of `Intended` at `hp`). Example: in every intended model of F-AT1, guard1 is `thinks quite likely`. Guards: without premise 3 (`fat1np`), knows and intends without thinks satisfy the frame and the collapse fails; with the holders different (instance 2 knows and intends, instance 0 does not think) it fails; on F-AT6's transitive pair knows → quite likely, the pair is present and the collapse holds at each of the 7 of 16 points satisfying the frame. 7.4's other points: F-AT1 with knows, intends and thinks and the category true (both true); F-AT5 with a = the hand-named term: knows and thinks with the term and the category true (both true), the term alone (both false) | 17e61342c, 05a52dfdf, 56fb3a335 | the three `#guard`s after "`guard_collapse` (F-AT1, a = `intends`)" |
| Statement gate: each statement equals the spec's text after whitespace normalisation | `docs/attitudes/at-1d/spec_text_check.py` (at-1c's pattern, the seven statements with their docstrings, each followed by ` :=` so appended text is refused) | d10feeeb2, 56fb3a335 | section "Spec re-read" |
| ATTITUDES.md row | at-1d's row; at-1's row now names its eight statements | e6b873252 | |
| Generated files (R12) | `regen_generated.py --write`: `wrote 38 entries` (the Lean inventories, and codemap rows already stale on main) | d306accb7 | `regen_generated.py --check`: `checked 38 entries` |

Not delivered: nothing. Nothing moved to at-1: the item is under the ~700-line seam (section "Size"), so `guard_collapse` stayed.
Kept out on purpose: `Frame.lean`, `Semantics.lean`, `Route.lean` (at-1c's definitions as merged), `lean/VE/NormDefaults/Packs.lean`
(AT-2), `lean/VE/Compose/Dispatch.lean` (AT-3a). Branch overlap: no in-flight `lean-first/*`, `feature/*`, `infra/*` or `foundation/*`
branch touches `lean/VE/Attitudes`, `lean/ATTITUDES.md` or `docs/attitudes/at-1d` (`git diff --name-only main...<branch>` for each).

Helper lemmas, in `Theorems.lean`: `sorts_of_pair`, `path_pairs` (a path of frame pairs ends at a key, by a last pair, with the start's
sorts), `keyOf_base`, `denote_interp_base` (a formula typed over `baseEnv` means the same on `interp` and on the base structure at
valuations agreeing on its context; the spec's proof note "contents use no generated name"), `tupleTyped_interp`, `closeOver_denote`,
`atomAt_interp`, `contentAt_interp` (the proof note "the premise's extra binders do not change them"). at-1's `old_formula_invariant` and
`att_elaboration_faithful` can reuse `denote_interp_base` and `atomAt_interp`.

## Spec re-read

- `python3 docs/attitudes/at-1d/spec_text_check.py`: `7 statements, 0 missing, 7 of 7 found`, rc 0. Opposite direction, each by editing
  and restoring `Theorems.lean`: `guard_collapse` without `(hh : ck.holder = ct.holder)` gives `1 missing` (`guard_collapse`), rc 1;
  `seed_intended`'s docstring without "typed" gives `1 missing` (`seed_intended`), rc 1.
- With the ` :=` anchor (self-review finding), appended text is refused too: `knows_factive`'s conclusion made `contentAt m.S k vs ∨ True`
  (proof `.inl …`, which builds) gives `1 missing` (`knows_factive`), rc 1. (at-1c's script lacks the anchor; this item does not edit it.)
- Spec re-read, statement against text: `frame_iff_intended` against docs/spec/attitudes.md:1280-1283; `knows_factive` :1312-1314;
  `seed_intended` :1315-1318; `seed_least` :1319-1321; `forced_iff_reachable` :1322-1329; `mistaken_belief_admissible` :1330-1334
  (proved as the spec says, through `seed_intended`); `guard_collapse` :1335-1340. No hypothesis added or removed.
- 7.4's rows for `frame_iff_intended` (M1, M4 / M2, M3), `guard_collapse` (a = `intends`: the instance for every intended model of
  F-AT1, whose values at M1 and M4 are at-1c's guard example) and `forced_iff_reachable` (both rows) are examples. 7.5's points
  (F-AT1, M1-M4 for `frame_iff_intended`; F-AT1, M1 for `seed_intended` and `mistaken_belief_admissible`; F-AT1 for `guard_collapse`)
  likewise.
- `frame_iff_intended` takes `WellFormedAtt A`, which the kernel does not reduce: `example : WellFormedAtt fat9 = true := by decide
  +kernel` (scratch file, F-AT9, one `knows` key and no degree) answers "Tactic `decide` failed … its `Decidable` instance … did not
  reduce to `isTrue` or `isFalse`". Its examples therefore take `WellFormedAtt fat1 = true` (and `fat7item`) as a
  hypothesis, and `#guard WellFormedAtt fat1 && WellFormedAtt fat7item` evaluates it. The other six statements need no
  `WellFormedAtt`, and their examples are unconditional.
- 7.4's `guard_collapse` row "a = hand-named term, F-AT5" is a `#guard` on `fat5` with `guardP 0` (added after the self-review).

## Seeded bugs and mutants

Each bug was planted, `lake build VE.Attitudes.Examples VE.Attitudes.Theorems` run, and the file restored (`git status` clean after each).
A mutant that breaks a proof in `Theorems.lean` stops lake before `Examples.lean`. So, to name the example that fails as well, each was
also run with `Theorems.lean` and `Examples.lean` elaborated as one scratch file, where a failed proof stays a declaration and
elaboration continues. `docs/attitudes/at-1d/mutants.json` lists every one with its failing checks (line numbers as of this HEAD).
Only Lean product code changed: no Python and no Rust.

| Bug (task) | File | Failing check |
|---|---|---|
| `seedClosure` closing across holders (a seed member at any tuple with the same tail) | `lean/VE/Attitudes/Semantics.lean` | the `forced_iff_reachable` example's two-holder point (`Examples.lean:1109`, and :1111, :1112); `seed_least`'s example (:1090); at-1c's seed-closure example (:999); the proofs of `seed_intended`, `seed_least`, `forced_iff_reachable`, `mistaken_belief_admissible` |
| `Intended` without factivity (the second conjunct's `contentAt` made `True`) | `Semantics.lean` | at-1c's direct M2 example (`Examples.lean:926`: not intended, knowing a false content) and the proof of `knows_factive` (`Theorems.lean:532`); also `seed_intended` (:544) and `frame_iff_intended` (:749, :754). `knows_factive`'s own example (:1073) only applies the theorem: lake does not build it under this bug, but in the one-file run it still elaborates, since only the statement is used |
| `framePremises` missing premise 3 (no `knows → thinks w` pair premise) | `lean/VE/Attitudes/Frame.lean` | `pair_breaks` (`Examples.lean:1042`), through which the right-to-left examples on F-AT7 and M3 read the broken premise; F-AT7's frame guard (:1069); the no-pair guard (:1130); the transitive-pair guard (:1146); at-1c's frame guards; the proofs `frame_iff_intended` (`Theorems.lean:749`, :755), `frame_wellFormed`, `empty_relations_frame` |
| `framePairs` dropping the transitive step (no pair with a middle key) | `Frame.lean` | `guard_collapse`'s guard on F-AT6's transitive pair (`Examples.lean:1146`); at-1c's F-AT6 and `framePairs_transitive` guards (:732, :872, :878); `mem_framePairs` (`Theorems.lean:314`) |
| (new guard) `checkNames` refusing names over 18 bytes | `lean/VE/Attitudes/Syntax.lean` | `#guard WellFormedAtt fat1 && WellFormedAtt fat7item` (`Examples.lean:1019`), the hypothesis guard of the `frame_iff_intended` examples |
| (new guard) the elaborated atom's holder fixed to variable 1 | `Syntax.lean` | the holders-differ guard (`Examples.lean:1147`) |
| (new guard) `factive` as its converse | `Frame.lean` | 7.4's remaining `guard_collapse` points (`Examples.lean:1136`), and :1147, :1155 |
| (changed file) `knows_factive`'s conclusion weakened to `… ∨ True` | `lean/VE/Attitudes/Theorems.lean` | `spec_text_check.py`: `1 missing` (`knows_factive`), rc 1 |
| (changed file) `guard_collapse` without `hh` | `Theorems.lean` | `spec_text_check.py`: `1 missing` (`guard_collapse`), rc 1; the proof (`Theorems.lean:768`, `hh` unknown) |
| (changed file) fixture `RMh` with instance 0 knowing | `lean/VE/Attitudes/Examples.lean` | the holders-differ guard (`Examples.lean:1147`) |

No new trusted definition (`tools/trust_map.py` lists none for this item; section "Trust"), so no per-definition mutant is due under
R16. The trust-mutants sweep: section "Runs".

## Trust

Theorems are class P and `Examples.lean`'s fourteen new definitions are fixtures, entered as class T in `tools/trust-classes.json`
(595f83c46). No product definition changed or was added. `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0`, `PASS`. Before the T entries it read `unclassified +24` (`VE/Attitudes/Examples.lean`) and
`regen_generated.py --check` failed at `trust-tables`; both pass now. No DELTA.md: no route, verdict, wording or definition changed, so there is no
user-visible delta.

## Size

`git diff --numstat $(git merge-base HEAD main)`, without generated files:

| Kind | Lines |
|---|---|
| Statements and proofs | `Theorems.lean` 267: the seven statements with docstrings about 45; their proofs about 65; helper lemmas about 155 (`denote_interp_base` 55; `closeOver_denote`, `atomAt_interp`, `contentAt_interp`, `tupleTyped_interp` 60; the rest 40) |
| Examples and guards | `Examples.lean` +146 -2 (two at-1c examples named as theorems for reuse) |
| Evidence | `spec_text_check.py` 42, `mutants.json` 12 (one line per mutant) |
| Docs and side tables | `ATTITUDES.md` +3 -2, `tools/trust-classes.json` +15 -1, this report |

`git diff --numstat a0102f0e5` at 2a03f1e30, without generated files (codemap, the Lean inventories, `VE/Audit.lean`) and the
tool-written `trust-mutants.json`: 485 added and 5 changed lines before this report. The report brings the total to about 600, inside
the 600-800 estimate. The proofs and helpers came in at about 220, under the 350-450 estimate. The helpers the at-1c measure counted
(`mem_framePairs`, `sameSubject_eq`, `key_checked`, `keyOf_name`) were already in `Theorems.lean`.

## Pilot bytes

None expected: a structure row (bytes 0). The content stays a named open residual.

## Runs

- `lake build` (full, on the Lean of 2a03f1e30, unchanged since d306accb7): `Build completed successfully (1328 jobs)`. `python3 lean/audit.py`:
  `PASS: 796 source files; 8827 named theorem declarations audited … only the declared standard axiom allowlist`. `#print axioms` (scratch
  file): `frame_iff_intended`, `forced_iff_reachable`, `mistaken_belief_admissible` use `propext`, `Classical.choice`, `Quot.sound`;
  `guard_collapse` and `knows_factive` only `propext` (`lean/axioms.txt` lists all seven and every helper). No `sorry`.
- `python3 tools/check_lean_imports.py`: `Lean layer graph kept (796 modules, 18 reviewed legacy edges)`. `Examples.lean` now imports
  `VE.Attitudes.Theorems`.
- `uv run python tools/regen_generated.py --write`: `wrote 38 entries` (the Rust release binary was built by `tools/rust_build.py --check`
  first, so `route-cases` ran too); `--check`: `checked 38 entries`. `uv run python tools/lean_statements.py`: `changed: 0`.
- `uv run python tools/trust_map.py --check`: PASS, trusted +0 (section "Trust").
- `python3 -I manage-agents/tools-local/light-lane.py check`: `NOT` (Theorems.lean is not in `tools/trust-classes.json`, and side tables
  changed), so the sweep ran: `zsh manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/attitudes/at-1d/trust-mutants.json`,
  in the cloud pool at 595f83c46 (the Lean of HEAD): `0 definitions, 0 mutants … 0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 0 ALLOWED,
  0 NOT RUN`, exit 0. No trusted definition is new, so no allow file is needed and at-1c's is not extended. The seeded bugs above
  are what this item's checks are measured by.
- `grep -rln VE.Attitudes lean/VE/Service lean/VE/Route lean/Main.lean ve/`: no file, so no route reads these modules.
- Selected tests: (below, after the final run).
- Not run here: the full gate (the chain runs it). No test in main-known-red.txt was touched.

SELF-REVIEW: 0 A, 4 B, 7 C; fixed 10 (the four B: the gate's ` :=` anchor, mutants in the changed Lean files, 7.4's two missing
`guard_collapse` points, this section; six C: HEAD and hashes, the full size, the order deviation, the factivity bug's test,
`tupleTyped_interp`'s docstring, the `decide +kernel` quote). The seventh C (the worktree's last build was of a mutated tree) needed no fix: the full
`lake build` above ran on the clean tree.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed; no service mode, schema or relay changes (the grep in "Runs").
2. PASS: "Deliverables" gives each task line with its commit and check; `git diff --stat a0102f0e5 -- tests ve 'tools/*.py'` is empty, so
   there is no Python copy of a Lean decision and no report test; no in-flight branch touches these files ("Deliverables").
3. PASS: `docs/attitudes/at-1d/mutants.json` (14 mutants, each failing a named guard, example, proof or the statement gate);
   `trust-mutants.json` 0 mutants because no trusted definition is new.
4. N.A.: Lean only, read by no route; no Python or Rust product code changed.
5. N.A.: no relayed field.
6. N.A. here: the chain gates the final HEAD; `trust-mutants.json` names 595f83c46, whose Lean equals HEAD's.
7. PASS: no DELTA row, no signature reserved, trust +0 (`trust_map.py --check`).
8. PASS: no user-visible output changes (theorems and fixtures only; the route grep).
9. PASS: the selected run below (`tools/select_tests.py` through `mac-pytest.sh --select`).
10. PASS: `spec_text_check.py` checks every statement verbatim and fails on a weakened conclusion or a removed hypothesis
    (`mutants.json`: `statement-*`); the proofs depend on the definitions they claim (each seeded bug breaks a proof).
11. N.A.: no evaluator, budget or deadline; nothing runs these definitions on a route.
12. N.A.: no runtime path changes.
13. PASS: no test removed or renamed (two at-1c `example`s became named theorems; they still elaborate).
14. PASS, both directions: `frame_iff_intended` both sides true (M1, M4) and false (M2 through →, M3 and F-AT7 through ←);
    `forced_iff_reachable` forced and not forced (three ways); the collapse holding (every intended model, F-AT6's transitive pair, 7.4's
    points) and failing (no pair, holders differ); the statement gate passing and failing. Spec re-read: section "Spec re-read".
15. PASS, the four classes. Overclaim: "no route reads" rests on the grep; "verbatim" on `spec_text_check.py`. No silent cut: all three
    deliverables were built, and 7.4's F-AT5 point was added rather than cut. Every check can fail: `mutants.json` has a mutant for
    each new `#guard` (:1019, :1069, :1130, :1136, :1147, :1155) and each claimed behaviour. Limits before work: N.A., no evaluator.
