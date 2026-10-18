# Graded words and comparisons in Lean (`lean/VE/Scales/*`)

Specification: [docs/spec/quantities.md](../docs/spec/quantities.md) sections 6.1, 6.2 and 9.3 (statement spec,
draft 3) and [docs/spec/quantities-PLAN.md](../docs/spec/quantities-PLAN.md) batch QT-B1. `lean/audit.py` audits
every theorem. No existing Lean source changed; `VE.lean` gained one import and `VE/Audit.lean` its generated entries.
No route, wire field or relay reads these files yet: QT-B2 puts the premises in PK-1's `scales` pack.

QT-B1 is delivered in two parts. This item (qt-b1) holds the declarations, the generated premises, the block's check,
the intended meaning and the theorems that need no model construction. **qt-b1b** holds `Degrees.lean`
(`StrictLinear`, `intended_iff_degrees`), `Fresh` with `scales_conservative`, `grade_open` and fixture FB6.

## Files

| File | Contents |
|---|---|
| `Syntax.lean` | `Direction`, `Grade`, `Dimension`, `ScaleDoc`, `Dimension.symbols`, `ScaleDoc.symbols`, `rel2`, `rel1` |
| `Premises.lean` | `premises` (the labelled premises of 6.1), `scalePremises`, `gradeOrder` (a QS-1 `Order`), `gradeCaps`, `aboveNodes`, `WellFormed` |
| `Intended.lean` | `Intended`: the meaning of a dimension, stated directly over a structure |
| `Theorems.lean` | `premises_iff_intended`, `premises_wellTyped`, `scalePremises_labels_nodup`, and the lemmas they use (`dim_iff`, `dim_ok`, `intended_iff_and`, `typed1`, `typed2`) |
| `Examples.lean` | fixtures FB1 to FB4 and FB8, the seeded bug's fixture, and 9.5's rows for `premises_iff_intended` |

## Theorems in plain words

* **`premises_iff_intended`** (faithful): in any structure that respects the declarations, the generated premises
  hold exactly when every dimension has its intended meaning: the comparative is irreflexive and transitive; the
  equative is an equivalence that excludes the comparative and can replace either side of it; "any two can be
  compared" holds where declared; each graded word is closed upward (or downward) along the comparative and under
  the equative; and "g above h" means whatever is g is h.
* **`premises_wellTyped`**: every premise is well typed in the declared environment (the `scales` pack's typing
  obligation, QT-B2).
* **`scalePremises_labels_nodup`**: no two premises share a label, so a reported label names one premise (A3).

## Fixtures (`Examples.lean`)

Models are `VE.Bridge.ModelData`, counted by enumeration with `Formula.eval`; `intended_of` turns a computed premise
check into `Intended` through `modelData_valid` and `premises_iff_intended`.

| Fixture | What it computes |
|---|---|
| FB1 (u0165.s01) | 64 models over two responses; facts and premises: 0; without the closed premise: some; the one instance `uplift/gives_serious_uplift/closed` at (r2, r1) with the facts: 0 |
| FB1's lower twin | "minor harm" (lower): 0 models; the seeded bug (comparative reversed) makes it 1 |
| FB2 (u0226.s01, s02) | without the endpoint premise: 3 and 1 over the two ends, 1 and 0 over three dispositions; with it: 1 and 0 over both (A2) |
| FB3 (u0043.s01) | the reading set {not all the same; pairwise different}: (true, false) on two levels, (true, true) on three; `trust_intended`, `trust_not_intended` (9.5: irreflexivity broken, "as much as" not transitive) |
| FB4 (UDHR u094) | `∀c₁ c₂. same(c₁, c₂)` is well typed, holds with the premises on equal children and fails on unequal ones |
| FB8 (hostile) | `WellFormed` refuses an undeclared comparative, an `above` cycle (`DependencyCycle: …`), `above` across directions, `comparable` without `same`, a graded word that is not a W2 open term, a predicate in two roles or two dimensions, an undeclared sort, a one-place equative, a two-place graded word, 17 grades; duplicate labels (6 labels, 4 or 5 distinct) |
| `order_cases`, `symbols_cases` | kahn's cycle check, QS-1's caps (16 grades, 64 pairs) and the symbol lists `WellFormed` reads |

## Differences from the spec's text

* `WellFormed` checks duplicate symbols and labels with core's decidable `List.Nodup` instead of comparing lengths
  with `VE.Cardinality.firstUse`; the two accept the same lists, and `scalePremises_labels_nodup` then needs no
  length lemma. It uses core's `Except.isOk` for the spec's `okB`, which would repeat it.
* The `above` conjuncts `p.1 != p.2` and "both ends are grades" are kept as written; kahn (a self-loop is a cycle)
  and `Order.admit` (pairs within the grades) refuse the same blocks, so no fixture separates them.
