# order@0: implemented boundary (Stages 1–3, round 1 of language expansion)

Branch `opus/numbers`, from `ve-integration` after slice (1) (finite-model gate
and general profile gate, merged at 05ad851). This round adds slice (2), the
Python stage, and slice (3), Farkas certificates with a Lean soundness proof.
The Lean statements are in [ORDER.md](../../lean/ORDER.md). The Stage 1 record
(`codex/order`) is in the git history of this file.

The fragment is ground linear integer arithmetic inside many-sorted relational
FOL: a built-in integer sort, integer constants, numerals, `+`, scaling by a
literal integer, `<`, `<=` and equality. Integer terms occur as comparison
operands and as integer predicate arguments. Quantifiers range over user sorts
only; integer quantification is rejected, so every integer term is ground and no
Presburger procedure is needed. Standard unbounded integers, no overflow.

## Wire envelope and identities (frozen before any meaning_id was minted)

```json
{"language": "ve.core@0.1", "profiles": ["order@0", "relational-fol@0"],
 "spec_revision": "ve-v0.1-order-2026-09-22", "vocabulary": {...}}
```

* The profile list must be exactly this list. `closure@0 x order@0` is rejected
  in Python (`UnsupportedProfile`) and in Lean on every route
  (`combined_profiles_rejected`). The Stage 1 fixture revision
  `ve-v0.1-order-2026-09-21` stays rejected everywhere.
* Identity domains: `ve-environment-v0.1-order`, `ve-meaning-v0.1-order`,
  `ve-model-v0.1-order`, `ve-source-v0.1-order`. v0 and closure identities,
  views and certificates are unchanged (their fixtures and suites pass as before).
* `$int` is the reserved spelling of the integer sort. It is not an identifier,
  so no vocabulary can declare it, a model cannot list a domain for it, and
  `for every $int x` neither parses nor type-checks. It may appear only as a
  predicate argument sort or constant sort, and only in an order environment.

### Frozen canonical forms

| Surface (`ve_strict`) | AST data | Notes |
|---|---|---|
| `12`, `-5` | `["num", "12"]`, `["num", "-5"]` | Canonical decimal strings: optional `-`, no leading zeros, no `-0`, no `+`, at most 40 characters. A `-` directly before a digit is part of the numeral. |
| `[t + u]` | `["add", t, u]` | Every sum is bracketed. |
| `[t - u]` | `["add", t, ["scale", "-1", u]]` | Subtraction is sugar; `[t + -u]` parses to the same AST and prints as `[t - u]`. |
| `-t` (t not a numeral) | `["scale", "-1", t]` | Negation is sugar. `Scale(-1, Num k)` prints `[-1 * k]`, never `-k`. |
| `[k * t]` | `["scale", "k", t]` | The coefficient must be a numeral. |
| `t < u`, `t <= u`, `t equals u` | `["lt", t, u]`, `["le", t, u]`, `["eq", t, u]` | No `>`/`>=` constructors. |

Nothing is normalised: `[@n + 1]` and `[1 + @n]` are different ASTs with
different meaning_ids forever. `tests/test_order.py::test_frozen_meaning_ids`
pins four meaning identities and the environment identity. The other views
render the same terms (`fol_*` with parentheses); `ve_natural`, `ve_fluent` and
English say "is less than" and "is at most".

## Python stage (slice 2)

`ve/ast.py` (`Num`, `Add`, `Scale`, `Lt`, `Le`; typing), `ve/environment.py`,
`ve/parser.py`, `ve/printer.py`, `ve/fluent.py`, `ve/model.py`, `ve/evaluate.py`
and `ve/search.py`. Models give integer constants and integer relation cells as
canonical decimal strings; absent rows are false.

Countermodel search: numerals are never enumerated or reassigned. Integer
constants range over a finite *search* set, `[-3, 3]` plus every numeral and
its neighbours; integer relation cells range over the values of the integer
argument terms that actually occur. Every candidate is validated and
re-evaluated before it is returned. These are search bounds, not semantic
integer bounds: exhaustion is `NotFound`, never entailment.

The grammar export (`ve.grammar`) and the named-FOL adapter (`ve.fol`) raise
`UnsupportedProfile` for order environments.

## Farkas certificates (slice 3)

`prove_entailment` on an order environment runs an untrusted search
(`ve/order.py`: tableau rules, Fourier-Motzkin with provenance, gcd cuts,
branch and bound) and returns a certificate only after independent replay.
Checker version `ve-order-farkas-checker@1`; the five binding fields are as in
v0. Trace nodes:

* `close`: complementary formulas, or complementary predicate atoms whose
  argument pairs are equal by (a) the same resolved token, or one positive
  object equality between the two tokens, (b) an identical linearizable term,
  or (c) certified `t <= u` and `u <= t` already on the branch. `P(c+1)` against
  `not P(1+c)` therefore closes only after two splits, never by normalisation.
  A negated equality closes on equal arguments by the same evidence.
* `expand`: the v0 propositional and user-sort quantifier rules.
* `order-split@1` (`formula`: a `le`/`lt` with linearizable sides): two children,
  the formula and its negation. This is the `c <= k` or `c >= k + 1` split.
* `order-neq@1` (`at`: a negated integer equality): children `t < u`, `u < t`.
* `order-farkas@1` (`cuts`, `literals`, `final_cuts`): each literal reads as
  `0 <= p` (`t < u` as `t + 1 <= u`; negated `<=`/`<` as the opposite bound;
  a positive equality as `0 = p`, which alone may take a negative multiplier).
  Multipliers are canonical decimal strings. Each cut combines literals and
  earlier cuts with nonnegative multipliers, requires a divisor `g > 0`
  dividing every collected coefficient, and yields the rounded-down quotient
  (gcd tightening). The final combination must have every coefficient zero and
  a negative constant: `0 <= -k`, `k > 0`.

Lean: `VE.Order.Tableau.checkCertificate_sound` (no `sorry`, no custom axioms,
no `native_decide`; `omega` inside proofs). The Lean route is
`ve_conformance order`, with case kinds `certificate`, `countermodel` (through
the proved `checkCountermodel` gate) and `evaluate`.

## English surface

Comparisons only. Rendering: "t is less than u", "t is at most u"; parsing also
accepts "t is more than u" and "t is at least u" (operands swapped). "At least n"
is a comparison between terms, never a counting quantifier: "At least 3 items
are p." does not parse. Integer terms keep the frozen bracketed spelling. In
order environments, predicate templates containing comparison words fall back
to the formal wording. The English audit
(`python -m conformance.english_surface`) includes an `order` vocabulary,
appended last so every earlier row keeps its seed and digests.

## Conformance (Python vs Lean)

`python -m conformance.order` (report: `conformance/order-report.json`),
also run by `tests/test_order.py`:

* 546 generated certificates (Farkas sums, rewritten formulas, integer-only
  gcd/split cases, congruence, quantified, random), accepted by both.
* 4496 mutated or hand-built certificates: 4493 rejected by both, and 3
  mutations that happen to remain valid accepted by both. Named hazards (bare
  close on commuted arguments, `2c = 1` without cuts or with a wrong divisor,
  negative multipliers, forward cut references, splits on objects, the
  closure x order envelope) are rejected by both.
* 106 Python countermodels confirmed by Lean's `checkCountermodel`; 200 random
  formula/model evaluations identical.
* Zero disagreements.

## Trusted-code inventory

| File | Role |
|---|---|
| `lean/VE/Order/Linear.lean` | Linear forms, linearization, collection, gcd tightening; proved. |
| `lean/VE/Order/Tableau.lean` | Order tableau checker and `checkCertificate_sound`. |
| `lean/VE/Order/Wire.lean` | JSON decoders and the `order` route; boundary code, identity digests. |
| `lean/VE/Order/WireGate.lean` | Order route gate and combined rejection theorems. |
| `lean/VE/Order/ProfileGate.lean` | Closure branch now also excludes a singular `profile` field; singular `order@0` gate. |
| `lean/VE/Order/TableauChecks.lean` | Executable regressions. |
| `lean/Main.lean` | Adds the `order` subcommand; other routes unchanged. |
| `ve/order.py` | Python replayer (mirror of the Lean checker) and untrusted search. |

## What remains

* Integer quantification, parity/quotients and relational numeric lookups
  (design B beyond this fragment); FRET order witnesses (no integer movers exist).
* Rust support; grammar export and named-FOL adapter for order.
* Object equality in the order tableau is single-step (no congruence closure);
  such entailments may be `NotFound`. Proof search is incomplete by design;
  failure is inconclusive.
* A Lean parser/printer for the order surface (only the evaluator, countermodel
  gate and certificate checker are compared with Python).
* Round 2: lemma citation and conservative definitions.
