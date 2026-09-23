# Language expansion, round 1 (2026-09-22), for review

Lead's direction: while credit lasts, one agent expands VE in parallel with the experiments; proofs for stable parts
now, English-surface proof after expansion settles. Guidance note had paused "policy-grade" extensions until the pushback
study or T1c shows signal; the lead overrides that for a small, reviewed first round.

Round 1 (in order):
1. NUMBERS: the Python stage of `order@0` (Lean stage merged: linear integer arithmetic, gated off). Parser/printer/
   type checker/evaluator for integer sorts, constants, `<`, `<=`, `+` with constants (linear), equality; certificates
   for linear-arithmetic steps checked by a small decision procedure whose soundness is proved in Lean (Fourier-Motzkin
   or simplex certificate replay, whichever the Lean stage supports); countermodels with integer values; English surface
   wording ("at most", "more than", "at least n"); conformance Python vs Lean on every certificate; profile gate enabled
   only after the Lean items below are done.
2. LEMMA CITATION + CONSERVATIVE DEFINITIONS (math use case gap G4): a certified claim can be cited by meaning_id as a
   premise in later arguments; definitions `P(x) := phi(x)` are conservative (new symbol, defining formula, no
   recursion) with a Lean theorem that adding a definition proves no new facts about the old vocabulary; English
   rendering "by Theorem n" / "call x ... if ...".
Proof work in parallel (stable, prerequisite): the two findings from the order@0 review: an executable finite-model
validity checker proved equivalent to `M.Valid E` (so order countermodels are checkable end to end), and a general
profile-gate theorem (decoding succeeds only for the exact declared profile lists), both in Lean.
Deferred: English-surface unambiguity proof (after round 1's grammar settles); strings/attributes/sets; VEX evidence.
Every change: tests green, no change to existing identities or certificates, Lean audit axioms unchanged, cross-family
review (Gemini while Codex is unavailable) before merge.

## After review (2026-09-22): Opus xhigh and Gemini both "revise"; adopted

Wrong premise fixed: the Lean order@0 stage has NO arithmetic tableau rules and Python returns UNKNOWN for arithmetic
entailment, so arithmetic certificates are new trusted Lean code in a new versioned envelope. Round 1 = NUMBERS ONLY;
lemma citation and definitions move to round 2 (bundle-only citation re-checked in the same Lean run, strictly-earlier
DAG, checked environment-extension relation, whole-lemma citation, explicit predicate definitions only).
Slices: (1) [in progress, opus/order-proofs] executable finite-model validity checker proved equivalent to M.Valid +
general profile-gate theorem; (2) Python order@0: parse/print/type-check/evaluate/countermodels, entailment still
UNKNOWN; FREEZE canonical forms (subtraction/negation sugar, decimal numerals) and reserve `$int` before minting any
meaning_id; (3) FARKAS closing rule: branch literals with nonnegative integer multipliers, t<u as t+1<=u, sum to 0<=-k
with k>0; gcd tightening and a split rule c<=k or c>=k+1 for integer-only unsatisfiability; t!=u via a split rule;
equalities of terms like c+1 vs 1+c only via a certified t<=u and u<=t, never trusted normalisation; closure@0 x order@0
stays rejected (gate theorem first); Lean soundness proof; >= 500 cases replayed in Python and Lean. English: "at least
n" only for comparisons, never as a counting quantifier.
