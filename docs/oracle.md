# Semantic oracle and experiment validation

`ve.equivalence.compare(env, a, b, budgets=None)` compares two closed, checked
formula ASTs in **all** VE structures, with the same empty-sort semantics as
`evaluate`, finite search, and the tableau. A declared constant inhabits its
sort; other sorts may be empty. Invalid input raises rather than receiving a
logical label. Optional budgets are a `Budgets` instance or a dictionary of its
fields (`max_proof_steps`, `max_domain_size`, `max_models`, `max_evaluations`).
Bounds are per implication direction, search, or replay; they are not an
aggregate time allowance. Host cancellation propagates.

| Label | Required evidence |
|---|---|
| `EQUIVALENT` | Replayed entailment certificates in both directions, returned in `result.certificates` |
| `DIFFERENT` | At least one distinguishing model, replayed by `check_countermodel` evaluating both formulas |
| `UNKNOWN` | No checked difference, and at least one implication still unproved; a reason and per-direction attempts are retained |

`meaning_id` is a structural, alpha-invariant commitment, not a semantic hash.
Even identical ASTs get two certificates. Complementary compound formulas can
close a tableau immediately, but a zero proof budget still cannot certify them.
This closure rule uses checker version `ve-tableau-checker@2`; regenerate version-1
certificates rather than treating the changed checker as an unchanged artifact.
`NotFound` and `ResourceLimit` never become entailment claims. In particular,
“at most three objects” and `true` are not equivalent just because size-three
search finds no difference.

`result.failed_directions` contains `a_not_implies_b`, `b_not_implies_a`, or both.
`result.models` maps those names to complete `FiniteModel` objects. Each direction
also contains its proof, model, attempts, and status. `result.relation` describes
**b relative to a**:

| a implies b | b implies a | Relation |
|---|---|---|
| proved | proved | `equivalent` |
| proved | countermodel | `weaker` |
| countermodel | proved | `stronger` |
| countermodel | countermodel | `incomparable` |
| either unresolved | | `unknown` |

A single checked difference suffices for `DIFFERENT` even when `relation` is
`unknown`. Calling that a weakening would guess the other implication.
`is_weaker(env, candidate, reference, budgets=None)` and `is_stronger(...)` test
**strict** strength: `True`, `False`, or `None` when the relation is undecided.
They return `False` for equivalence; callers must not treat `None` as a negative
semantic answer.

## Two-variable fragment and limits

`in_two_variable_fragment(f)` checks syntactic membership up to capture-avoiding
renaming in relational FO2 with equality and constants. It accepts a formula or
a document of closed formulas. It counts simultaneously live variable identities
rather than quantifier nesting depth, total binder count, or the largest De
Bruijn index. Bound variables may reuse a name after its previous binding is no
longer needed. Even an unused binder needs a name that does not capture either
outer variable used in its body. Three-variable formulas equivalent to FO2
formulas are not recognized by this syntactic checker. Environment typing remains
a separate prerequisite. No counting quantifiers or function symbols are added.

FO2 with equality has the finite model property; satisfiable formulas have finite
models of at most exponential size in the formula length. Satisfiability is
NEXPTIME-complete. These are mathematical facts, not a completeness guarantee for
this implementation. See Grädel, Kolaitis, and Vardi, [On the Decision Problem for
Two-Variable First-Order Logic (1997)](https://www.cambridge.org/core/product/identifier/S1079898600007666/type/journal_article).
Finite sorts and constants can be represented using unary sort predicates and
singleton predicates with FO2 axioms; allowing empty sorts preserves the finite
model property. A dummy element can represent an otherwise empty total universe.

Our algorithm is bounded finite enumeration plus a bounded general tableau. It
does **not** implement an FO2 decision procedure, derive a sufficient model bound,
or promise to find a proof under the current search schedule. A finite bound of
two objects can miss even a one-variable formula requiring witnesses in three
mutually exclusive unary categories. Thus `UNKNOWN` remains possible in FO2.
Outside FO2 there can also be satisfiable formulas with only infinite models.
The existing grammar still has its own binding-depth settings; use the fragment
checker as an explicit generator gate. It does not silently narrow the grammar.

Tableau search and replay share a nesting bound derived from the JSON cap of
256 levels: each expansion introduces a node object and a `children` array.
Eight levels are reserved for certificate/package envelopes, giving a maximum
trace depth of 124. Search beyond that returns `ResourceLimit`, and every emitted
certificate has already passed wire validation and replay.

## Reference and attack validation

`validate_reference(env, f, budgets=None)` returns `VALID` only with a checked
non-vacuous satisfying model and a checked falsifying model. It returns `INVALID`
with a certificate establishing validity, unsatisfiability, or incompatibility
with the declared non-vacuity conditions. Missing bounded witnesses are `UNKNOWN`.
The experiment generator must validate references separately from attacks; a
successful attack validation is not an assertion that its reference is suitable.

There is no canonical general-purpose definition of “semantic non-vacuity.” This
implementation declares an operational, syntax-sensitive **guard coverage**
criterion: every declared sort is inhabited, and every implication antecedent
has a satisfying assignment to its enclosing bound variables. Enclosing variables
are existentially closed for this check, including those originally universally
bound. Guard coverage examines every syntactic branch, independently of evaluator
short-circuiting. It does not require every antecedent to hold at every object,
and does not certify relevance, causal importance, or truth of empirical claims.
For formulas with no implications the criterion reduces to inhabited sorts.

`ve.attacks.validate_attack(env, faithful, attacked, budgets=None)`:

1. Rejects alpha-identical and certified logically equivalent “fake” attacks.
2. Requires `DIFFERENT` and enough checked evidence to classify `weakening`,
   `strengthening`, or `incomparable`. A checked difference with an unresolved
   other direction returns `UNKNOWN`, retaining its model.
3. Stores a complete distinguishing model for **each failed direction**, with
   both truth values, model identity, and quality flags.
4. Searches first for witnesses with nonempty sorts and guard coverage for both
   formulas, then for nonempty witnesses. If those searches do not succeed within
   budget, it retains the original checked witness and emits a warning. It never
   claims such a preferred witness is impossible merely because search failed.

Logical classification includes empty-sort counterexamples, even if a preferred
nonempty witness does not exist. Quality preferences never change the semantics.
With `forall p` versus `exists p`, one failed direction needs a two-object mixed
model and the other fails only on the empty sort. Both are retained and labeled.
All output records are diagnostics (JSON null is permitted); semantic input
packages retain VE's strict JSON subset.

## JSONL batch CLI

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run python -m ve.attacks attacks.jsonl \
  --output validated.jsonl --max-domain-size 2 --max-proof-steps 10000
```

Each line is an object with `environment` (a complete VE environment), `faithful`
and `attacked` (either one VE statement including its final newline or a tagged
formula AST array), and optional `id` and `budgets`. Per-row budgets override CLI
defaults. No other fields are accepted. `-` selects stdin/stdout. The CLI streams
one diagnostic per input row, including malformed rows, stores witnesses and
certificates, and emits counts on stderr. Input rows are capped at 16 MiB.
Exit codes: 0 = all valid; 1 = rejected fake attack(s); 2 = any invalid input or
UNKNOWN. A file cannot be used as both input and output.

## Reproducible uncertainty audit

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run python -m experiments.oracle.measure_unknown
UV_CACHE_DIR=/private/tmp/ve-uv-cache uv run pytest -q
```

The audit draws 400 pairs at seed 20260921, independently and uniformly across ten
requirement template families and six mutations. Vocabulary order and binary
relation orientation are randomized. It includes identities, double negation,
weakenings, strengthenings, replacements, and quantifier changes. Every formula
passes the FO2 gate. Every pair, including fake attacks and unsuitable references,
stays in the denominator. The output contains complete distinguishing witnesses,
per-direction statuses, and reasons. Proofs can be regenerated with the same
inputs and budgets. The summary reports oracle UNKNOWN separately from attack
classification UNKNOWN and reference validation, with worst-case bounds on both
difference and equivalence rates. This is a synthetic engineering audit, not an
estimate of a held-out task distribution or an experiment outcome.

Measured results and the exact budgets are committed in
[`experiments/oracle/results/summary.json`](../experiments/oracle/results/summary.json);
the corresponding pairs and checked witnesses are in
[`sample.jsonl`](../experiments/oracle/results/sample.jsonl).

At these budgets, **8/400 comparisons were UNKNOWN (2.0%)**, all in the
three-category coverage family. There were 253 DIFFERENT and 139 EQUIVALENT
pairs, giving a difference-rate interval of **63.25–65.25%** under the two extreme
UNKNOWN assignments. Attack validation was UNKNOWN for **15/400 (3.75%)**;
reference validation was UNKNOWN for **36/400 (9.0%)**. The latter references
need at least three objects for satisfaction. The run took 50.168 seconds,
including reference and preferred-witness validation. The Phase T target of
**under 2% UNKNOWN is not met** by this run. Raising a domain cap alone is not a
completeness fix: model and evaluation budgets and the enumeration order also
limit what is reached.

## Fair search and empty-sort-only refinements

The prover schedules gamma expansions by increasing instantiation count, then
formula age and parameter age, with complementary ground instances prioritized.
It starts at one instance per universal and increases that bound geometrically.
Search-only NNF, trivial-connective, and associative/commutative keys rank
connections; signed negations and alpha rules still use ordinary certificate
steps. Comparison gives model search a turn after an initial 128-step proof
pass, then spends any remaining proof budget on unresolved directions. Search skips a gamma body already present on the branch and delays a delta
whose body is already satisfied by an existing parameter of the correct sort.
This comparison ignores unused outer bindings. It does not identify distinct
parameters or turn a dependent witness into a uniform witness. Delta expansion,
when selected, still creates a fresh checker-generated witness.

A certificate-depth frontier returns to earlier search choices; it no longer
immediately aborts the entire search. The aggregate step budget covers retries
and all instantiation rounds. Search remains incomplete under finite budgets.
The signed-instance keys are scheduling hints only: the original formulas,
indices, eigenparameters, closure tests, certificate schema, and trusted replay
rules are unchanged (`ve-tableau-checker@2`). No additional Lean rule is required.

`compare` retains its original three-valued status and strict-strength `relation`.
It now also returns `relation_detail: "differs_only_on_empty_sorts"` when:

1. At least one independently checked distinguishing model has an empty sort.
2. Both implications have replayed certificates with additional nonemptiness
   premises, one `Exists(sort, Top())` for each sort listed in `nonempty_sorts`.

In Python these additional certificates are in `nonempty_certificates`. In JSON,
`nonempty_equivalence` holds `sorts` and `certificates`. To replay the forward
certificate, pass `(a, *(Exists(sort, Top()) for sort in sorts))` as premises and
`b` as conclusion; reverse `a` and `b` for the reverse certificate. The sorts are
all environment sorts in sorted order; this is a sufficient condition and does
not identify a minimal set of relevant sorts. Failed conditional proof search
leaves the detail null. A bounded absence of inhabited countermodels never
justifies this detail. `forall p` versus `exists p`, for example, has a nonempty
mixed countermodel and is not classified as an empty-sort-only difference.

Attack validation retains such checked differences and their original logical
classification, exposes the detail for experiment policy, and avoids searching
for an inhabited witness once its impossibility is certified. It does not choose
an experiment's empty-sort policy. UNKNOWN rows have `accepted: null`; rejected
rows have `false`. Strict-strength helpers can return `False` from a checked
refutation even when the other implication remains unresolved.

The serial benchmark and exhaustive finite-semantics audit are documented in
[the prover fairness report](prover-fair-report.md).
