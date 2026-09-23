# Supplied-invariant closure induction

`ve-tableau-closure-checker@1` adds the rule

```text
P(x), forall a,b. (P(a) and E(a,b) -> P(b))
  |- forall y. (tc[E](x,y) -> P(y))
```

The identical rule holds for `rtc`. `P` is an arbitrary unary formula supplied
by the certificate author, not an inferred truth or a finite-model observation.
It may contain quantifiers, negation, captured parameters, or nested closure.
The edge may be Named or Body. Paths have their standard finite-path semantics
over arbitrary admissible structures, including infinite structures.

The environment/profile/revision and meaning-ID domains are unchanged. The
five certificate envelope fields are unchanged. New certificates use checker
version `ve-tableau-closure-checker@1`. Version `@0` certificates replay unchanged
with exactly their old rules, and cannot use an induction node. V0 FOL versions
and the original Lean FOL checker are unchanged.

An induction trace node has exactly these fields:

```json
{
  "rule": "closure-induct@1",
  "at": 0,
  "sort": "item",
  "invariant": ["unary", "p", ["var", 0]],
  "children": [{"rule": "close"}, {"rule": "close"}, {"rule": "close"}]
}
```

`at` must name a **positive** `Reach(k,E,x,y)` in the current branch. `sort`
must match the homogeneous edge sort. The invariant's typing context is
`sort :: path.bindings`: index 0 is its single local variable, and index 1
onward captures the path's ambient bindings. Both checkers type-check it.
Substitution preserves quantifier binders and the two local Body binders.

Replay reconstructs these children, in this exact order:

1. Original branch plus negative `P(x)` (prove the base).
2. Original branch plus negative `forall a,b. (P(a) and E(a,b) -> P(b))`
   (prove preservation by one edge).
3. Original branch plus positive `P(y)` (continue the original deduction).

All three child traces must close. The JSON example's `close` leaves are valid
only when the corresponding contradictions are already present. The invariant
is data, and never licenses skipping either obligation. Replay supplies fresh
quantifier witnesses through the existing delta rule; induction introduces no
witnesses and accepts no cyclic graph. Existing fuel/depth/AST limits apply.
The universal conclusion follows by ordinary tableau quantifier/implication
rules; the induction node acts on its positive path instance.

[`reachable_induction`](../../lean/VE/Closure/Induction.lean) proves propagation
along both kinds of finite paths. `closure_induction` proves the substituted
formula rule; `Tableau.induct_sound` proves preservation of branch satisfiability.
`replay_sound` and `checkCertificate_sound` include the new trace constructor.
See [the theorem statements and audit boundary](../../lean/CLOSURE.md).

Python search accepts `prove_entailment(..., invariants=[P])`. A plain formula
has only the induction variable free. For captured parameters, use
`InductionInvariant(P, bindings=("w:0",))`: index 1 of `P` denotes that tableau
parameter. Constant captures may use `c:name` tokens or literal `Const` terms.
Search rebases the formula to each path's binding list, and the certificate
contains that rebased AST. These hints only schedule proof search; replay checks
the resulting certificate independently. Without hints, search retains its
previous behavior and incompleteness regressions. Search does not invent an
invariant and is not complete even when a suitable one is supplied.

[The examples](../../usecases/closure-induction/README.md) certify T9, T9e, and
the policy that no member of group G reaches resource R, even with a group cycle.
T9 and the policy use automatic search with supplied invariants. T9e uses an
explicit untrusted schedule and includes the proved transitivity of `tc[s]` in
its invariant, avoiding a change to the old exact-context composition rule.

Rust implements closure syntax/evaluation/countermodel search, but has no
tableau certificates or replay implementation to mirror. This rule therefore
has Python/Lean parity, not a Rust certificate acceptance claim.

Run serially from the repository root:

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-induct
export LEAN_NUM_THREADS=1
lake -d lean build
uv run python lean/audit.py
uv run python -m conformance.induction
uv run python usecases/closure-induction/verify.py
VE_LEAN_PREBUILT=1 uv run pytest -q
```
