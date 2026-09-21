# Task B — the boundary: Euclid's infinitude of primes

*Evidence for everything below is in `boundary/probe.py`, `boundary/results.json`,
`boundary/euclid-statement.ve` and `boundary/euclid-countermodel.json`. Run
`uv run python usecases/math-mini-paper/boundary/probe.py`.*

The result chosen: **Euclid, *Elements* IX.20 — there are infinitely many
primes.** It is short, universally cited, and its proof is a page in any first
course. It is also, unlike the eight results in `paper.md`, irreducibly
arithmetic.

---

## 1. The surprise: the statement *is* expressible, and that is the problem

Take the sort `number`, the unary predicate `prime` and the binary predicate
`lt`. Then "there is no largest prime" is a perfectly legal VE statement:

```text
for every number x0, (if (x0 is prime), then (there exists number x1, ((x1 is prime) and (x0 lt x1)))).
```

which the tool renders as

> for every number N that is prime, there is a number N2 such that both N2 is
> prime and N precedes N2

This parses, type-checks, canonicalises, hashes, and reads correctly in English.
It is also **worthless**, and the tool says so immediately: with no premises the
prover returns `NotFound`, and the countermodel search returns, at domain size 1,

```json
{"complete": true,
 "domains": {"number": ["e0"]},
 "constants": {},
 "relations": {"prime": [["e0"]], "lt": [], "divides": [], "associate": [], "unit": []}}
```

— one object, which is "prime", with nothing above it.

So the honest description of VE's position is *not* "the statement is
inexpressible". It is: **VE can express the shape of the statement but cannot
express the theory that gives it content.** `prime` is an uninterpreted unary
symbol, and no VE axiom can pin it down. That is a sharper and more useful
finding than "syntax error", because it is the failure mode a careless user would
actually hit: a statement that looks verified and means nothing.

## 2. What exactly is missing for the STATEMENT

To make the statement mean what Euclid meant, `prime` must be *defined*, and the
definition is

> *p* is prime iff *p* > 1 and for all *a*, *b*: if *a · b = p* then *a* = 1 or
> *b* = 1.

Blocked by, in order of bite:

| Missing construct | Where it bites | `GAPS.md` |
|---|---|---|
| **Arity above two** | `a · b = p` is the ternary relation `times(a, b, p)`. VE admits unary and binary predicates only. The probe's attempt to write it fails with `UnknownSymbol: Unknown predicate 'times'` because it cannot even be *declared*. | G2 |
| **Function symbols / operations** | The natural form is the term `a * b`; VE terms are variables and constants only. | G1 |
| **Arithmetic and literals** | `p > 1`, `1`, `+ 1`. No numeric sort, no literals. | G6 |
| **A definition mechanism** | Even given the above, `prime` would have to be introduced as a biconditional axiom repeated in every theorem, as D2–D5 are in `paper.md`. | G4 |
| **Induction** | Not needed for the statement; decisive for the proof (§3). | G5 |
| **Sets / second-order quantification** | Needed only for the *set form* ("the set of primes is infinite"); the ∀∃ form above avoids it. | G3 |

**The smallest VE extension that would admit the statement.** Exactly two
things:

1. **G2, predicates of arity up to 3** (`times: (number, number, number)`), and
2. **G4.1, conservative definitions** (so `prime` can be introduced by a
   checked biconditional rather than copied everywhere).

With those, and an axiom set for the multiplicative monoid of positive integers
written by hand (associativity, commutativity, identity, cancellation, an order
axiom or two), the statement and its meaning are both in VE. Note that arithmetic
with a *numeric sort* (G6) is **not** required for the statement — a relational
axiomatisation suffices. Note also that G2 alone changes the surface grammar: VE's
binary atoms are infix (`a divides b`), and a ternary atom has no infix form, so
`times(a, b, c)` is a new production, not a schema relaxation.

What VE can state *today* about this material, and does in the probe: that
`divides` is reflexive and transitive, and that a prime has no proper divisor —
as an **axiom**, since without multiplication it cannot be a theorem.

## 3. What would still be missing for the PROOF

Euclid's argument, step by step, against VE-with-G2-and-G4:

| Proof step | Needs |
|---|---|
| "Suppose the primes are exactly *p₁, …, p_k*." | A finite *set* or *list* of unknown size, and quantification over it. G3, plus a recursion principle. |
| "Let *N* = *p₁ · p₂ · ⋯ · p_k* + 1." | An **iterated** binary operation over that list — a fold. Even with ternary `times`, VE has no way to write a product of *k* unknown factors: it is a recursive definition, which the spec forbids outright ("no recursive definition"). G1 + G3 + recursion. |
| "*N* > 1, so *N* has a prime divisor *q*." | Strong induction on *N*. G5. |
| "*q* ∈ {p₁,…,p_k}, so *q* ∣ *p₁⋯p_k*." | Membership in the list; the product's divisibility properties. G3. |
| "*q* ∣ *N* and *q* ∣ *N* − 1, so *q* ∣ 1, so *q* = 1: contradiction." | Subtraction, the unit, and the lemma *d ∣ a ∧ d ∣ b ⟹ d ∣ a − b*, itself proved from the ring axioms. G1, G6. |

Two of these are qualitatively different from the rest. **Recursion/folding** is
explicitly excluded by VE's design, not merely absent: the environment forbids
"recursive definition" and the one fixed-point construct in the whole language
(`closure@0`) is a *fixed* operator over a binary relation, not a user-definable
recursion. **Induction** is likewise excluded by design — `closure@0`'s rules are
documented as "induction-free search rules". Adding either is not an incremental
extension; it changes what kind of system VE is.

There is also a structural gap that has nothing to do with logic: Euclid's proof
is *four lemmas and a contradiction*, and VE has no way to name a lemma (G4.2).
`paper.md` §5 shows this failing on a statement with four variables and two
premises; at Euclid's scale it is not a difficulty, it is a wall.

**Summary.** The statement needs two cheap extensions. The proof needs
recursion, induction, arithmetic and proof structure — that is, it needs a proof
assistant.

## 4. The same result in Lean 4 + Mathlib

*From my own knowledge of Mathlib, not checked against the current source in this
session. I name only what I am confident exists; I have deliberately not invented
lemma names for the intermediate steps.*

In Mathlib the theorem is already there, in the ∀∃ form, as
`Nat.exists_infinite_primes : ∀ (n : ℕ), ∃ p, n ≤ p ∧ Nat.Prime p`. So a user
writes:

```lean
theorem infinitely_many_primes (n : ℕ) : ∃ p, n ≤ p ∧ Nat.Prime p :=
  Nat.exists_infinite_primes n
```

and that is the whole development. The comparison that matters is not the length
but *what the ecosystem supplies underneath*:

- `ℕ` is an inductive type with a recursor, so induction is a primitive of the
  logic, not a rule someone must add to a tableau checker.
- `Nat.Prime` is a **definition**, unfoldable, with hundreds of lemmas about it,
  all citable by name. VE has neither definitions nor citation.
- `*`, `+`, `-`, `∣` are functions and a relation on a type with a full algebraic
  hierarchy (`CommSemiring`, `Monoid`, …) organised by typeclasses. VE has no
  functions, no arity above two, and no hierarchy.
- Finite sets (`Finset`) and folds (`Finset.prod`) make "the product of the
  primes below *n*" a *term*. In VE it is not expressible at any length.
- The proof is a proof *term*, checked by a small kernel — the same trust
  architecture VE uses for certificates, and the closest genuine similarity
  between the two systems.

The structural difference is that Lean's statement is an ordinary term of its
logic, so Mathlib can and does state and prove all of it; VE's statement is a
formula of a fragment chosen so that checking is cheap and so that *no user can
smuggle computation into a predicate*. Those goals are in direct tension with
doing mathematics.

One thing Lean does **not** give you, and where VE is genuinely ahead: a
mechanical, lint-constrained, injective English rendering of the statement, and
an exhaustive small-model countermodel search that hands you a concrete
refutation when a conjecture is false. `decide` and `Decidable` instances cover
some of the latter for concrete finite goals, but not "find me the structure that
breaks this" for an open vocabulary.

---

## 5. Judgement: (a) extend VE toward mathematics, (b) a statement layer over Lean, or (c) do not target mathematics

**Recommendation: (b), with a narrowly scoped piece of (a).**

### Against (a) — extending VE's own logic toward mathematics

The extensions needed are, in order: arity > 2, function symbols, definitions,
lemma citation, arithmetic, recursion, induction, sets. That list does not
converge on "a better VE"; it converges on a re-implementation of a dependently
typed proof assistant, with a checker that must then be trusted for all of it.
Every step also costs VE something specific that it was built to have:

- Function symbols make terms unbounded in depth, which is precisely where
  finite-model evaluation and bounded countermodel search stop being useful — and
  the countermodel search is, on the evidence of `paper.md`, VE's most valuable
  single feature. (26 countermodels, all re-checked; the refuted conjecture; 25
  hypothesis-necessity witnesses.)
- Induction and recursion break the "everything is checkable by replaying a
  finite data structure" property only mildly for the checker, but they destroy
  the property that a *reader* can confirm a statement means what it says by
  reading one sentence of English. A recursive definition is not renderable as a
  lint-constrained English phrase.
- Every extension enlarges the Lean metatheory that has to be redone. The
  existing Lean side is 11 headline results and ~99 supporting lemmas for a
  language with no functions and two arities. Scaling that to Mathlib's ambit is
  a decade of work that Mathlib has already done.

And the payoff is poor: mathematicians already have Lean, Rocq and Isabelle, and
will not adopt a weaker system for the sake of a nicer surface syntax.

### Against (c) — do not target mathematics at all

Two concrete things this exercise produced argue against walking away entirely.
First, the `paper.md` run is a genuine artifact: 15 certificates, double-checked,
with 25 necessity countermodels and a refuted conjecture, on content that is in
every discrete-mathematics course. Elementary relational mathematics — orders,
equivalences, diagonal arguments, relational algebra, modal frame conditions,
relational database dependencies — is exactly VE's fragment, and that is a real
teaching and specification niche. Second, mathematics is the cheapest honest
stress test VE has: it has unambiguous ground truth, so every `ResourceLimit` and
`NotFound` in this paper is an unarguable measurement of the prover, uncontaminated
by disputes about what the English meant. Dropping mathematics would cost that
instrument.

### For (b) — a verified, readable statement layer over Lean

This is where VE's actual advantages are, and they are real ones that Lean does
not have:

1. **A rendering with a lint.** VE's `ve_fluent` view is mechanical, refuses
   vocabulary templates containing logical words or colliding heads, never drops
   a condition, never collapses a quantifier scope, and has an inverse parser in
   the test suite. Applied to Lean theorem *statements* (not proofs), that is a
   direct answer to the standard complaint about formalisation — "how do I know
   the theorem you formalised is the theorem I care about?" — which is the one
   part of the Lean workflow that is still trust-me.
2. **Semantic comparison of statements.** `ve.compare` decides equivalence /
   weaker / stronger for statements in the two-variable fragment and returns
   `UNKNOWN` honestly otherwise. "Is your `Nat.Prime`-free restatement of my
   theorem the same theorem?" is a question Lean cannot answer and VE partly can.
3. **Countermodels for statement bugs.** The overwhelmingly common formalisation
   error is a mis-stated hypothesis, not a wrong proof — and a mis-stated
   hypothesis usually shows up as *unnecessary*. `paper.md`'s 25 necessity
   countermodels are a template for a Lean-side tool: for each hypothesis of a
   formalised statement, exhibit a small model where dropping it breaks the
   theorem, or flag it as suspicious.

The scope discipline that makes (b) work: **VE never sees a proof.** It ingests
the first-order, relational *shell* of a Lean statement — the quantifier
structure, the connectives, the predicate applications — with everything it
cannot represent (functions, arithmetic, sets, typeclass side conditions) held as
opaque atoms with declared descriptions. It then renders, compares and searches
for countermodels *within* that shell. That is strictly less than the statement
means, and the tool must say so at every step, which VE's existing
"OPAQUE-with-provenance" conventions already know how to do.

### The narrowly scoped piece of (a) worth doing anyway

Independently of Lean, two of the `GAPS.md` items pay for themselves inside VE's
existing domain (specifications, policy, debate) and should be built regardless:
**G4 (conservative definitions and a cut/lemma-citation rule)** and **G5's
closure-specific `closure-induct@0`**. The first removes the copy-every-axiom tax
that makes multi-theorem VE documents unreadable, and its soundness proof is one
Lean lemma on top of the existing branch-soundness theorem. The second turns the
paper's only two *language*-level failures (T9, T9e) into certified theorems
without admitting general induction. **G2, arity up to three or four**, is a close
third: cheap, semantically trivial, and it unblocks a large class of ordinary
non-mathematical statements ("A transferred X to B", "A approved X on date D")
that VE currently cannot say either.

None of those three is a step toward mathematics. They are repairs that this
mathematical stress test happened to expose.
