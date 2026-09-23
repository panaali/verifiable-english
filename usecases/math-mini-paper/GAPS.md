# Gaps

Ranked by (how often it blocked something in this paper or in `boundary.md`) ×
(how much of ordinary mathematics it unlocks). Each entry gives the smallest
concrete example that hit it, why v0/v0.1 cannot express it, and a syntax and
semantics sketch. The original sketches are **design proposals**; the dated
G5 update below records the subsequent proved closure-induction implementation.

A recurring theme: the gaps that block *statements* (G1–G3) are mostly cheap and
well understood; the gaps that block *proofs* (G4, G5) are the ones that decide
whether VE can host mathematics at all.

---

## G1. Function symbols and operations — blocks every arithmetic statement; very high importance

**Smallest example.** Euclid: `N = p₁ · p₂ · … · p_k + 1`. Also `x + y`, `|A|`,
`f(x)`, `P(A)`, the group operation in Lagrange's theorem — and, in this paper,
the inability to write `x ⊓ y` or `sup S` anywhere in the order-theory section.

**Why v0 cannot express it.** VE is explicitly *function-free*
(`docs/spec/v0-language.md`: "No pronouns, implied quantifiers, higher-order
arguments, function symbols, or embedded Lean source occur in v0"). Terms are
variables and constants only. The standard relational workaround — replace
`f(x) = y` by a binary predicate `f_graph(x, y)` plus totality and
single-valuedness axioms — works for *unary* functions only, because a binary
operation needs a ternary graph predicate, which G2 forbids.

**Sketch.** A `functions@0` profile: declare `f: (s1, …, sn) -> s` in the
vocabulary; extend `term` with `f(t1, …, tn)`; the denotation is the obvious
one over total functions; finite models supply a table. Rendering: a declared
template `"the sum of {0} and {1}"`, with the existing lint. The tableau needs
congruence closure over terms and a term-depth bound for γ-instantiation
(unbounded term depth is exactly where first-order proof search becomes
semi-decidable in the painful sense). The evaluator stays terminating on finite
models. Cost: moderate for the checker, large for the prover.

**Cheaper intermediate.** Allow only *unary* function symbols. That already gives
`successor`, `inverse`, `complement`, `closure` operators, and costs almost
nothing.

---

## G2. Arity above two — blocks operations, betweenness, and most of the standard relational encodings; very high importance

**Smallest example.** `divides(a, b)` is fine, but `sum(a, b, c)` ("a + b = c")
is not; neither is `between(a, b, c)` nor `cosets(g, H, x)`.

**Why v0 cannot express it.** The vocabulary admits "unary predicate identifiers
with one argument sort; binary predicate identifiers with an ordered pair of
argument sorts" and nothing else. This is the single restriction that closes off
the usual work-around for G1.

**Sketch.** Allow `arguments` arrays of length 1..k for a declared cap k (k = 4
covers essentially all of elementary mathematics). Grammar needs a new atom form
`p(t1, ..., tn)` — VE's infix binary form does not generalise — which is a real
surface-syntax change, not just a schema relaxation. The fluent view needs
templates with n placeholders and the lint's "verb in position 1, no auxiliary"
rule generalised. Semantics, evaluation, tableau rules and identity hashing are
otherwise unchanged: this is the *cheapest high-value* extension in this list.

---

## G3. Sets, subsets and second-order quantification — blocks Cantor, Lagrange, and the general form of T2; very high importance

**Smallest example.** In this paper: T2's real statement, "for *every* binary
relation R, no element R-lists exactly the R-non-self-listing elements". We could
only instantiate it at `lists` and at `mentions`. Outside this paper: `|A| <
|P(A)|`, "every subgroup", "the set of primes is infinite" in its set form.

**Why v0 cannot express it.** VE quantifies over elements of declared sorts only.
There are no relation variables, no predicate variables, no sort of subsets, and
no comprehension.

**Sketch (weakest useful version).** Not second-order logic — *schematic*
first-order logic. Allow a statement to contain a **relation parameter** `?R`
with a declared signature, and define a schematic statement to be valid when its
instantiation at every vocabulary symbol of that signature is valid. The
certificate becomes one certificate per instance, or one certificate over a fresh
uninterpreted symbol (sound, and strictly stronger: proving the schema at a fresh
symbol proves every instance). The latter is cheap: introduce `?R` as a fresh
predicate symbol not in Σ, prove once. This would turn T2 into a single theorem
rather than a conjunction of instances.

**Sketch (the real version).** A two-sorted encoding with a sort `set` and a
binary `member: (point, set)` plus an extensionality axiom and a comprehension
*schema*. This is statable today (it is what set theory does), but without G1/G2
you cannot form `P(A)`, and without G5 you cannot prove anything interesting
about it.

---

## G4. Definitions, named lemmas and proof structure — blocked T7 in this paper; very high importance for *usability*

**Smallest example.** T7. The mathematician's statement (T7mono) exhausts a
5-million-step tableau budget. Split into T7a and T7b it is trivial — but VE
cannot cite T7a and T7b, so the composite theorem has to list them as
hypotheses, and the fact that they are themselves theorems is a cut performed by
the human reader. Second example: every definition axiom (D2–D5) is copied
verbatim into every theorem that mentions the defined symbol.

**Why v0 cannot express it.** VE has no definition mechanism, no abbreviation, no
theorem store, and no cut rule at the document level. `prove_entailment` takes a
flat premise list. The spec is deliberate about this ("Predicate symbols have no
hidden definitions or inference rules").

**Sketch.** Two additions, both conservative and both checkable:

1. **Conservative definitions.** A vocabulary entry
   `{"defined": {"arity": 1, "body": <formula AST>}}` for a *new* symbol not
   occurring in its own body. Semantics: the environment denotes only structures
   satisfying the biconditional — equivalently, unfolding is a sound rewrite.
   The identity hash already covers the environment, so a changed definition
   changes the artifact. Checking: the tableau gains a `define-unfold@0` rule in
   both polarities, exactly parallel to `closure-star@0`. This removes the
   copy-the-axiom-everywhere tax with no new proof power.
2. **A cut / lemma-citation rule.** A theorem store `{name: (env_id, premise
   meaning_ids, conclusion meaning_id, certificate)}`; a certificate node
   `{"rule": "cite", "lemma": <name>}` that may add the lemma's conclusion to a
   branch provided the checker re-verifies the lemma's own certificate and the
   citing theorem's hypothesis list includes the lemma's hypotheses (or the
   lemma is a validity). Soundness is the cut rule and is a one-line Lean
   argument on top of the existing branch-soundness theorem. **This is the
   cheapest change with the largest effect on whether a multi-page document is
   writable at all**, and the only one in this list I would call a prerequisite
   for "mathematics paper" rather than "mathematics exercise".

---

## G5. Induction (and least-fixed-point reasoning generally) — blocked T9 and T9e; decisive for mathematics

**2026-09-22 update:** the closure-specific rule is implemented and proved sound
in Lean. Both T9 and T9e now have Python/Lean-accepted certificates in the
[induction supplement](../closure-induction/README.md). The original certificates,
results and no-invariant search regressions are retained unchanged as historical
evidence. The discussion below describes the original gap; arithmetic induction
and cyclic proof acceptance remain outside the implementation.

**Smallest example.** T9: *r ⊆ s* and *s* transitive imply `tc[r] ⊆ s`. Every
mathematician proves this by induction on path length; `closure@0` implements
unfolding and composition, which give only T9a–T9d. Outside this paper: Euclid,
the pigeonhole principle, Lagrange, and essentially every theorem with a number
in it.

**Why v0.1 cannot express it.** `docs/spec/v0.1-profiles.md` is explicit:
"These are induction-free *search rules*; their metatheorems use finite-path
induction. No arbitrary invariant/induction rule, cyclic proof acceptance, or
'saturated means satisfiable' rule is added." Monotonicity under universal
inclusion is listed as "designed only; no replay rule or inclusion oracle.
Regression remains ResourceLimit" — which our T9e run reproduces exactly.

**Sketch.** For closure specifically, a **closure-induction rule** is both
natural and checkable:

```text
closure-induct@0:
  from  ∀a b. (R(a,b) → Q(a,b))                (base: edges satisfy Q)
  and   ∀a b c. (Q(a,b) ∧ R(b,c) → Q(a,c))     (step: Q is R-closed on the right)
  infer ∀a b. (tc[R](a,b) → Q(a,b))
```

where `Q` is any VE formula with two designated free positions (i.e. a `Body`
edge, which the AST already has). The certificate node names the two premises and
the `Body` instance; the checker re-derives the two side conditions as ordinary
sub-entailments. Its Lean soundness proof is the least-fixed-point induction
principle for `R⁺`, which `closure@0`'s semantics already defines as `μX.(R ∪
R;X)`. This is a *bounded*, closure-specific induction — it adds no general
arithmetic induction and no cyclic-proof acceptance — and it would turn T9 and
T9e from `ResourceLimit` into certified theorems. Of everything in this list it
is the one with the best power-to-risk ratio for the existing profile.

General mathematical induction (over a numeric sort, over a well-founded
relation, over term structure) is a much larger step and drags in G1, G2 and G6.

---

## G6. Numbers, arithmetic and units — blocks everything quantitative; high importance, low surprise

**Smallest example.** "There are infinitely many primes." `p ∣ N`, `N > 1`,
`p ≤ k`, `2ⁿ`, and every physics derivation.

**Why v0 cannot express it.** There is no numeric sort, no literals, no
arithmetic. The spec says so directly: "Arithmetic and claims about textual
formatting need specified extensions or input adapters; a predicate named
`uses_decimals` does not implement either check." `docs/spec/v0.1-profiles.md`
sketches an `order@0` numeric candidate but this paper did not use it and the
coverage ledger lists its decisions as open.

**Sketch.** A built-in sort `int` with literals, `+`, `*`, `<`, `=`, and a
decision procedure (linear integer arithmetic is decidable; once multiplication
of variables enters, it is not). Note that `closure` is already forbidden from
ranging over a built-in numeric sort, which shows the design has anticipated the
interaction. Realistically: LIA only, with nonlinear facts supplied as premises.

---

## G7. No biconditional connective — a papercut, hit in every definition; medium importance

**Smallest example.** D2–D5. Each is written `(A→B) and (B→A)`, roughly doubling
the length of every definition axiom and every fluent rendering of one.

**Why v0 cannot express it.** The grammar has `not`, `and`, `or`,
`if … then` and nothing else.

**Sketch.** `"(", formula, ") if and only if (", formula, ")"`, denoting `⟦a⟧ ↔
⟦b⟧`, wire tag `["iff", a, b]`, tableau α-rule for the positive sign (two
implications) and β-rule for the negative. Fluent view: "either both … or
neither". Entirely routine, and it makes definitions half as long to read. Note
the interaction with G4.1: with real definitions, most uses of `iff` disappear.

---

## G8. Restricted / typed quantification over a defined subclass — medium importance

**Smallest example.** "for every prime p …", "for every subgroup H …", "for every
upper bound of S …". In VE these become `for every point x, (if (x is prime),
then …)`, which is correct but doubles the depth of every statement and is the
main source of the paper's unreadable nesting.

**Why v0 cannot express it.** Sorts are the only classification and they are
fixed by the vocabulary; there is no way to introduce a sub-sort defined by a
formula.

**Sketch.** Pure sugar at the surface: `for every point x that is prime, (φ)`
parsing to the implication, and the *canonical printer already emits it* — T8's
fluent rendering shows "for every point P that is not the same point as P2",
proving the renderer has the concept. Making it accepted input as well as output
costs little and would cut statement size noticeably. No semantic change, no new
tableau rule.

---

## G9. Real numbers, units, and dimensional analysis — blocks physics; high importance if physics is a target, otherwise none

**Smallest example.** Any one-page derivation: `p = mv`, `F = dp/dt`, "in SI
units".

**Why v0 cannot express it.** No reals, no measures, no dimensions, no
derivatives (which additionally need limits, hence second-order machinery or a
real-closed-field theory).

**Sketch.** Out of scope for any small extension of VE. A dimensional-consistency
*checker* over a units algebra is a genuinely useful and small thing to build,
but it belongs beside VE, not inside it.

---

## G10. Proof-search strength for statements VE can already express — not a language gap; medium importance

**Smallest example.** T7mono: four universal variables, two γ-premises,
`ResourceLimit` at 5 × 10⁶ steps, while the two three-variable halves take 57 ms
and 48 ms.

**Why it happens.** The tableau instantiates γ-formulas at every available
parameter and splits on β; with 4 parameters, a 2-variable and a 3-variable
γ-premise, the reachable branch space is large and the search order is not
goal-directed.

**Sketch.** Nothing about the *language* need change, and the trust boundary is
unaffected because the certificate is checked independently either way. Options:
unification-driven instantiation (free-variable tableaux), ordered resolution as
an alternative search front-end that emits the same certificate format, or simply
a user-visible "try these lemmas first" hint list. Cheapest honest fix: exactly
G4.2, a cut rule, which lets a human do the decomposition once and have it
checked.

---

## Ranking summary

| Rank | Gap | Blocks statements | Blocks proofs | Cost |
|---|---|---|---|---|
| 1 | G4 definitions + lemma citation | no | **yes (usability)** | low |
| 2 | G2 arity > 2 | **yes** | no | low |
| 3 | G5 induction (closure-specific first) | no | **yes** | medium |
| 4 | G1 function symbols | **yes** | yes | medium/high |
| 5 | G3 sets / schematic relation parameters | **yes** | yes | low (schematic) / high (sets) |
| 6 | G6 arithmetic | **yes** | yes | high |
| 7 | G7 biconditional | no | no | trivial |
| 8 | G8 restricted quantifiers | no | no | trivial |
| 9 | G10 proof search | no | yes | medium |
| 10 | G9 reals and units | **yes** | yes | out of scope |

The top five, in one line each: **lemma citation and real definitions**;
**predicates of arity three and up**; **an induction rule for the closure
profile**; **function symbols**; **relation parameters (schematic theorems)**.
