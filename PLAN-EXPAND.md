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
