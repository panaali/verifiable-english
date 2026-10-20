# Graded words and comparisons in Lean (`lean/VE/Scales/*`)

Specification: [docs/spec/quantities.md](../docs/spec/quantities.md) sections 6.1, 6.2 and 9.3 (statement spec,
draft 3) and [docs/spec/quantities-PLAN.md](../docs/spec/quantities-PLAN.md) batch QT-B1. `lean/audit.py` audits
every theorem. No existing Lean source changed; `VE.lean` gained one import and `VE/Audit.lean` its generated entries.
No route, wire field or relay reads these files yet: QT-B2 puts the premises in PK-1's `scales` pack.

QT-B1 was delivered in two parts. qt-b1 holds the declarations, the generated premises, the block's check, the
intended meaning and the theorems that need no model construction. qt-b1b adds `Degrees.lean` (`StrictLinear`,
`intended_iff_degrees`), `Fresh` with `scales_conservative`, `grade_open`, the two model constructions they need,
fixture FB6 and 9.5's rows for the new theorems.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Direction`, `Grade`, `Dimension`, `ScaleDoc`, `Dimension.symbols`, `ScaleDoc.symbols`, `rel2`, `rel1` |
| `Premises.lean` | `premises` (the labelled premises of 6.1), `scalePremises`, `gradeOrder` (a QS-1 `Order`), `gradeCaps`, `aboveNodes`, `WellFormed` |
| `Intended.lean` | `Intended`: the meaning of a dimension, stated directly over a structure; `Fresh`: no symbol of the block occurs in a formula |
| `Theorems.lean` | `premises_iff_intended`, `premises_wellTyped`, `scalePremises_labels_nodup`, `scales_conservative`, `grade_open`, and the lemmas they use (`dim_iff`, `dim_ok`, `intended_iff_and`, `typed1`, `typed2`, `more_ne_same`, the `reread_*` lemmas); the proof helpers `reread` and `point` |
| `Degrees.lean` | `StrictLinear`, `intended_iff_degrees`; the proof helpers `asMuch`, `below`, `degreeSetoid` |
| `Examples.lean` | fixtures FB1 to FB4, FB6 and FB8, the seeded bug's fixture, and 9.5's rows for `premises_iff_intended`, `intended_iff_degrees` and `scales_conservative` |

## Theorems in plain words

* **`premises_iff_intended`** (faithful): in any structure that respects the declarations, the generated premises
  hold exactly when every dimension has its intended meaning: the comparative is irreflexive and transitive; the
  equative is an equivalence that excludes the comparative and can replace either side of it; "any two can be
  compared" holds where declared; each graded word is closed upward (or downward) along the comparative and under
  the equative; and "g above h" means whatever is g is h.
* **`premises_wellTyped`**: every premise is well typed in the declared environment (the `scales` pack's typing
  obligation, QT-B2).
* **`scalePremises_labels_nodup`**: no two premises share a label, so a reported label names one premise (A3).
* **`intended_iff_degrees`** (degrees): on a dimension where any two can be compared, the intended meaning holds
  exactly when each object can be given a degree on a strict linear scale so that "more than" is "a higher degree",
  "as much as" is "the same degree", and each graded word holds of every object at least as high (upper) or at
  least as low (lower) as one that has it. The degrees are built from the objects themselves: one degree for each
  group of objects that are "as much as" each other, and one lowest degree for every object outside the sort.
* **`scales_conservative`** (conservative): adding the scale premises to a list of formulas that use none of the
  block's predicates changes nothing that follows from it, among formulas that use none of them either.
* **`grade_open`** (no threshold): for each graded word, the premises alone allow a model with one object that has
  it and one with one object that does not; the premises never decide a graded word for any object.
* **`more_ne_same`** (one role per predicate): in a well-formed block no comparative is also an equative, in the
  same dimension or another. It follows from the check that no predicate appears twice in the block's symbols.

## The two model constructions

* **`reread D S grade`** keeps the objects, sorts and constants of `S` and every predicate outside the block, and
  rereads the block's predicates by their roles: nothing is "more" than anything, any two objects of a dimension's
  sort are "as much as" each other, and every object of the sort has each graded word when `grade` holds, none when
  it does not. These meanings satisfy every premise. Since a formula without the block's predicates means the same
  in `S` and in `reread D S grade`, a structure for the old formulas becomes one for the old formulas with the
  premises (`scales_conservative`). Only one fact about the block is needed beyond the declared signatures: a
  comparative is never an equative (`more_ne_same`), or "nothing is more" and "everything is as much" would clash
  on the same predicate.
* **`point`** has one object, in every sort, named by every constant, with no relation. `reread D point True` and
  `reread D point False` are `grade_open`'s two models.

## Fixtures (`Examples.lean`)

Models are `VE.Bridge.ModelData`, counted by enumeration with `Formula.eval`; `intended_of` turns a computed premise
check into `Intended` through `modelData_valid` and `premises_iff_intended`.

| Fixture | What it computes |
|---|---|
| FB1 (u0165.s01) | 64 models over two responses; facts and premises: 0; without the closed premise: some; the one instance `uplift/gives_serious_uplift/closed` at (r2, r1) with the facts: 0 |
| FB1's lower twin | "minor harm" (lower): 0 models; the seeded bug (comparative reversed) makes it 1 |
| FB2 (u0226.s01, s02) | without the endpoint premise: 3 and 1 over the two ends, 1 and 0 over three dispositions; with it: 1 and 0 over both (A2); `fb2_refuted`: with it, no disposition is more autonomous than fully autonomous in any admissible structure (`Entails`) |
| FB3 (u0043.s01) | the reading set {not all the same; pairwise different}: (true, false) on two levels, (true, true) on three; `trust_intended`, `trust_not_intended` (9.5: irreflexivity broken, "as much as" not transitive) |
| `intended_iff_degrees` (9.5) | degree maps into `0 < 1` and `0 < 1 < 2` that give the comparative and the equative: two levels (Anthropic and operators equal, users less) have exactly (1, 1, 0) into two degrees and 3 maps into three; three levels have 1; "as much as" not transitive, or irreflexivity broken: 0 of the 27 maps |
| FB4 (UDHR u094) | `∀c₁ c₂. same(c₁, c₂)` is well typed, holds with the premises on equal children and fails on unequal ones |
| FB6 (u0165.s05) | `vast_majority` (upper) on `share_of_humanity_targeted`: of the 4 models over one attempt, the premises hold in 2, one with the grade and one without; `fb6_open` is `grade_open`'s two witnesses |
| `scales_conservative` (9.5) | with the FB1 block, "r1 is flagged" follows from {r1 is flagged} with the premises and without them (`conservative_true`); "r1 is reviewed" follows from neither: `flaggedOnly` satisfies {r1 is flagged} and the premises and makes it false (`conservative_false`) |
| FB8 (hostile) | `WellFormed` refuses an undeclared comparative, an `above` cycle (`DependencyCycle: …`), `above` across directions, `comparable` without `same`, a graded word that is not a W2 open term, a predicate in two roles or two dimensions, an undeclared sort, a one-place equative, a two-place graded word, 17 grades; duplicate labels (6 labels, 4 or 5 distinct) |
| `order_cases`, `symbols_cases` | kahn's cycle check, QS-1's caps (16 grades, 64 pairs) and the symbol lists `WellFormed` reads |
| one role per predicate | every pair of positions of `Dimension.symbols` of one arity (comparative, equative, two graded words), shared across two dimensions or within one: refused; renamed apart: accepted; each dimension's own conjuncts checked in every position of the block |

## Differences from the spec's text

* `WellFormed` checks duplicate symbols and labels with core's decidable `List.Nodup` instead of comparing lengths
  with `VE.Cardinality.firstUse`; the two accept the same lists, and `scalePremises_labels_nodup` then needs no
  length lemma. It uses core's `Except.isOk` for the spec's `okB`, which would repeat it.
* The `above` conjuncts `p.1 != p.2` and "both ends are grades" are kept as written; kahn (a self-loop is a cycle)
  and `Order.admit` (pairs within the grades) refuse the same blocks, so no fixture separates them.
