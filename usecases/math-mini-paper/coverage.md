# Coverage

Two questions: (1) how much of the VE language did this paper exercise, and
(2) how much of the mathematics we set out to write actually landed.

## 1. Language coverage

| VE construct | Used | Where |
|---|---|---|
| sorts (one) | yes | `point` in both environments |
| several sorts | **no** | all of this mathematics lives on one carrier |
| unary predicates | yes | `greatest`, `minimal`, `least` (all three defined by axioms) |
| binary predicates | yes | `lists`, `mentions`, `lt`, `le`, `sim`, `akin`, `r`, `s` |
| constants | **no** | no named elements were needed; every statement is universally closed |
| `true` / `false` | **no** | no use for them |
| equality (`equals`) | yes | T5 conclusion, T8 totality and D5 |
| `not` | yes | T1–T4, T8, all definition axioms with negative bodies |
| `and` | yes | everywhere |
| `or` | yes | T8 totality only (VE's `or` is binary, so ternary totality needs nesting) |
| `if … then` | yes | everywhere |
| biconditional | **absent from VE**; simulated by `(A→B) and (B→A)` in D2–D5 |
| `for every` | yes | everywhere |
| `there exists` | yes | T1/T2 (the diagonal element) and C2 (seriality) |
| quantifier nesting depth 4 | yes | T7/T7mono |
| `tc[r](a, b)` (`closure@0`, named plus) | yes | T9, T9a, T9b, T9d, T9e |
| `rtc[r](a, b)` (named star) | yes | T9b, T9c |
| `tc[s a, b \| (φ)](t, u)` (Body edge) | **no** | no statement here needed a compound edge relation |
| finite-model evaluation | yes | 26 countermodels re-checked |
| countermodel search | yes | 25 necessity searches + 1 conjecture refutation |
| tableau proof + certificate | yes | 15 certificates |
| Python certificate replay | yes | 15/15 valid |
| Lean `check-certificate` | yes | 15/15 valid, including four `closure@0` certificates |
| `ve_fluent` view | yes | every statement |
| vocabulary lint | yes | 0 findings on both environments |
| `compare` / semantic equivalence | **no** | no statement needed to be compared to a reference |
| argument graphs (`check_argument`) | **no** | there is no adversarial structure in a paper |

**Summary.** Everything in v0 except constants, `true`/`false` and multiple
sorts is exercised, plus the named-relation half of `closure@0`. The constructs
we did *not* use were not missing — they were simply irrelevant to this content,
with one exception: the biconditional, which VE genuinely lacks and which every
definition in this paper had to work around.

## 2. Content coverage

| Intended result | Status | Note |
|---|---|---|
| T1 diagonal lemma | **certified** (Python + Lean) | no hypotheses; valid outright |
| T2 same at two relations | **certified** | the *general* corollary ("for any relation") is not statable: second-order |
| T3 irreflexive + transitive ⟹ asymmetric | **certified**, 2/2 hypotheses necessary | |
| T4 asymmetric ⟹ irreflexive | **certified**, 1/1 | |
| T5 uniqueness of a greatest element | **certified**, 2/2 | antisymmetry countermodel exhibited as asked; the definition axiom is equally necessary |
| T6 preorder symmetrisation is an equivalence | **certified**, 3/3 | the transitivity countermodel needed a hand-supplied candidate (re-checked), because exhaustive search over 3-point domains with two binary relations exceeds the 10^6-node evaluation cap |
| T7 order respects ∼ | **adjusted**: certified only from two congruence lemmas | the direct statement (T7mono) is `ResourceLimit` at 1e6 and at 5e6 tableau steps |
| T8 minimal ⟹ least in a total order | **certified**, 3/3 | proved without transitivity or irreflexivity |
| T9 closure induction (r ⊆ s transitive ⟹ tc[r] ⊆ s) | **not certified**: `ResourceLimit` | `closure@0` has no induction rule; this is documented as designed-only in `docs/spec/v0.1-profiles.md` |
| T9e closure monotonicity | **not certified**: `ResourceLimit` | same cause; the spec predicts exactly this regression outcome |
| T9a–T9d (edge inclusion, plus ⊆ star, star reflexivity, plus transitivity) | **certified** | the strongest closure facts the prover certifies: everything obtainable by finite unfolding and path composition |
| Conjecture C1 (transitive + symmetric ⟹ reflexive) | **refuted** with a 1-element countermodel | prover says `NotFound`, which is inconclusive; the refutation is the separate finite-model judgment |
| C2 (with seriality) | **certified**, 3/3 | |

**Totals.** 19 entailment queries; 15 certified by the Python replay checker and
the same 15 by the Lean executable; 0 accepted by one checker and refused by the
other. 4 not certified: 3 `ResourceLimit` (T7mono, T9, T9e), 1 `NotFound` (C1,
which is false and separately refuted). 26 finite models: 25 hypothesis-necessity
countermodels (25/25 found and independently re-checked) plus C1's refutation.

## 3. What a mathematician would notice is missing from this paper

Not one result in this paper has a *proof* in the mathematician's sense — a
chain of named lemmas. Each is a single entailment from an explicit premise list,
which is why the premise lists are long and repetitive: the definition axioms are
copied into every theorem that touches the defined symbol. A paper written this
way is readable at 8 theorems; it would not be readable at 80. See `GAPS.md` G4.

Nor is any of this paper's content *quantitative*: no numbers, no functions, no
sets, no induction. That is not an accident of taste. See `boundary.md`.
