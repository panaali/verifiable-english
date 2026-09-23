# Closure induction examples

All four deductions in [results.json](results.json) are certified by Python
replay and the independently proved Lean checker. Each directory contains the
exact query envelope (including its certificate), premises, and conclusion.
The checker version is `ve-tableau-closure-checker@1`.

| Deduction | Supplied invariant | Replay nodes | Certificate bytes |
|---|---|---:|---:|
| [T9](T9_induction/query.json): `r ⊆ s`, transitive `s` imply `tc[r] ⊆ s` | `s(x,z)` | 151 | 7,135 |
| [T9e](T9e_induction/query.json): `r ⊆ s` implies `tc[r] ⊆ tc[s]` | `tc[s](x,z) ∧ transitive(tc[s])` | 57 | 2,887 |
| [Policy, tc](policy_cyclic_plus/query.json): no G member reaches R | `group(z)` | 18 | 1,349 |
| [Policy, rtc](policy_cyclic_star/query.json): no G member reaches R | `group(z)` | 18 | 1,349 |

T9 and T9e use the exact premises and conclusions of the math mini-paper, with
no added assumptions. Positive closure need not be reflexive, so their proofs
first unfold one `r` edge. Inclusion establishes the invariant at the first
destination; induction handles the remaining path. T9 uses automatic search
with `InductionInvariant(Binary('s', Var(1), Var(0)), ('w:0',))`.

T9e uses an explicit certificate schedule in
[`conformance/induction.py`](../../conformance/induction.py). The invariant's
transitivity conjunct is proved in its base branch using the old composition
rule. It is then available in the preservation branch. It is not an additional
premise or a new trusted lemma. Automatic search with the smaller invariant
`tc[s](x,z)` remains limited by exact captured-context matching in composition.
The original mini-paper certificates, reports and no-hint regressions are
preserved unchanged; this directory is the new evidence for closing its G5 gap.

The policy has groups `g1`, `g2`, and resource `resource`. Both groups are in G,
and edges `g1 -> g2 -> g1` form a genuine directed cycle. Its rule says that an
edge from a G member ends at a G member, and the resource is not in G. The
conclusion quantifies over **every** G member, including unnamed entities in
arbitrary structures satisfying the rules. It is not merely a check of the
two named groups. The rtc version also rules out reaching R by zero steps.

The tests validate a finite model of all these premises, showing that the
deduction is not vacuous. Adding `g2 -> resource` gives a checked countermodel
when the preservation rule is removed. No finite domain bound is used in the
certificate's soundness theorem.

Reproduce from the repository root after building Lean:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-induct uv run python usecases/closure-induction/verify.py
```

The script constructs the certificates, replays each in Python and Lean, and
only then writes the artifacts. [The specification](../../docs/spec/closure-induction.md)
describes the rule and version compatibility.
