# Prover fairness report

## BRANCH

`codex/prover-fair`, based on integration merge `7a85024`.

## SUMMARY

- Fair, bounded gamma rounds and closure-driven ground-instance selection remove witness starvation.
- Search-only NNF/AC hints and existing-witness redundancy checks improve completeness; depth frontiers backtrack.
- Empty-sort-only differences retain checked countermodels and gain two checked nonemptiness certificates.
- UNKNOWN acceptance is null; a checked refutation can immediately make strict-strength helpers false.
- The unchanged `ve-tableau-checker@2` replays every emitted certificate; no new Lean rule is needed.

## VERIFY

The same 602 inputs were measured before and after, serially, with a two-second
wall deadline **per comparison**. All 237 baseline UNKNOWN pairs are certified
EQUIVALENT after the change. Two other pairs time out after the change and remain
in the denominator as UNKNOWN. The requested targets are met: **0.33% overall**
and **0.56% at depth ≥3**. The baseline has one timeout; the after run has two.

Every number is traced to the committed [before summary](prover-fair/before.json),
[after summary](prover-fair/after.json), and corresponding
[before rows](prover-fair/before.jsonl) / [after rows](prover-fair/after.jsonl).
Rows contain exact environment/AST inputs, their hashes, timings, decisions,
and certificate sizes. Matching per-row input hashes were checked across runs.
The measured comparison includes its production proof/model replay; an additional
independent replay of every returned certificate/model is outside the timing.

All arrows below mean before → after. Certificate sizes are compact UTF-8 JSON,
including bindings and trace, measured per certificate, not per formula pair.
The after statistics include the new conditional certificates as well as ordinary
ones. There are 576 before certificates and 1,218 after certificates; 71 after
pairs have the empty-sort-only refinement.

| Slice | Pairs | UNKNOWN | Median ms | p95 ms | Median certificate bytes | p95 certificate bytes |
|---|---:|---:|---:|---:|---:|---:|
| Overall | 602 | 237/602 (39.37%) → 2/602 (0.33%) | 14.66 → 9.83 | 276.13 → 110.42 | 820 → 708 | 39055 → 1075 |
| Depth 1 | 100 | 0/100 (0.00%) → 0/100 (0.00%) | 4.59 → 9.62 | 9.87 → 50.02 | 613 → 520 | 1064 → 652 |
| Depth 2 | 142 | 57/142 (40.14%) → 0/142 (0.00%) | 12.41 → 11.40 | 130.51 → 83.60 | 708.5 → 690 | 1377 → 1004 |
| Depth 3 | 120 | 31/120 (25.83%) → 0/120 (0.00%) | 16.67 → 7.41 | 489.84 → 57.87 | 1683 → 730 | 113760 → 984 |
| Depth 4 | 120 | 64/120 (53.33%) → 0/120 (0.00%) | 20.18 → 8.77 | 292.93 → 151.97 | 1688 → 802 | 109545 → 1072 |
| Depth 5 | 120 | 85/120 (70.83%) → 2/120 (1.67%) | 24.22 → 15.41 | 333.04 → 251.95 | 849 → 898 | 82494 → 1261 |
| Depth ≥3 | 360 | 180/360 (50.00%) → 2/360 (0.56%) | 20.87 → 9.06 | 364.25 → 144.87 | 1683 → 802 | 113722 → 1171 |

The fixed generator uses seed 20260921 and ten variants per depth/family, plus
the two exact reviewer regressions. It includes commutation, association,
De Morgan, contraposition, quantifier duals, double negation, one-point rules,
same-quantifier swap, vacuous quantifiers, prenexing/un-prenexing with empty-sort
traps, and near misses. At depth one, same-quantifier distribution replaces the
inapplicable two-binder swap. Half of the connective variants use binary relation
matrices depending on **every** binder. One-point variants cover both declared
constants and bound parameters. Quantifier depth is computed from the actual
AST, including closed side formulas. Consequently depth one has 100 pairs and
depth two has 142; other depths have 120 each. Family-level statistics are in the
JSON summaries. No failed row is removed.

The baseline is the actual merged oracle, extracted without altering another
worktree. Proof budgets are 10,000 aggregate search steps per implication,
model-domain cap 2, 10,000 model attempts, and 100,000 evaluation steps. Conditional
proofs have their own proof budget. The benchmark installs a main-process alarm;
no worker threads/processes or parallel tests are used. Core API budgets remain
work limits, not a built-in wall-clock SLA. Platform, Python version, and SHA-256
of each implementation module are recorded in the summaries.

Full serial regression result: **559 passed, 2 skipped in 436.73 s**. The only
skips are the optional `llguidance` and `xgrammar` grammar backends, which are not
installed. Existing Lean build/conformance tests passed. `git diff --check` passed.

Reproduction, in this order (never in parallel):

```sh
export UV_CACHE_DIR=/private/tmp/ve-uv-cache-views
mkdir -p /private/tmp/ve-prover-fair-baseline
git archive 7a85024 ve | tar -x -C /private/tmp/ve-prover-fair-baseline
uv run python tests/prover_fair_benchmark.py --baseline-root /private/tmp/ve-prover-fair-baseline --output docs/prover-fair/before.json
uv run python tests/prover_fair_benchmark.py --output docs/prover-fair/after.json
uv run python tests/prover_fair_fuzz.py --pairs 7000 --output docs/prover-fair/fuzz.json
uv run pytest -q
git diff --check
```

The final differential audit passed **7,000 generated pairs (5,429 distinct)**,
with **zero certified counterexamples**: 9,519 ordinary and 504 conditional
certificates replayed, 4,481 returned models independently rechecked, and
854,970,215 pair/interpretation combinations covered in 62.01 s. The initial
5,000 draws contained only 3,971 distinct pairs; the run was extended to exceed
5,000 distinct pairs as well.

The differential audit independently enumerates **every** relation interpretation
for sizes 0–3 per sort, with all constant denotations (including aliases) where
constants require inhabitants. It covers one-sort unary/binary, two-sort
unary/cross-sort binary, and constant-bearing signatures. An independent bitset
interpreter evaluates all interpretations exactly; it is cross-checked against a
separate scalar interpreter over every interpretation through size two before
the fuzz run. It does not use VE's evaluator to judge certificate soundness.
The seed, pair digest, counts, runtime, and any certified counterexamples are in
[the fuzz result](prover-fair/fuzz.json). Each positive direction is checked, even
inside a DIFFERENT comparison; conditional directions are checked over every
inhabited model. Every returned model is also evaluated with the independent
scalar interpreter.

Trusted replay functions (`_initial_branch`, `_kind`, `_term_token`, `_closed`,
`_derive`, `_apply`, `_binding`, `_Replayer`, and `check_entailment_certificate`)
were compared as Python ASTs against `7a85024` and are identical. The rule version
and wire format are unchanged. The normal-form keys influence scheduling only;
no rewritten formula enters a certificate. Existing witnesses can suppress
redundant search expansions, but every selected delta still uses a fresh
checker-generated eigenparameter.

## GAPS

- This synthetic engineering suite guided implementation and is not held out.
  It is not the reviewer's private distribution;
  its baseline rate must not be compared as if it were the reported 10.9%.
- Two depth-five rows (`near_misses`, variant 5; `prenex_empty_trap`, variant 5)
  reach the two-second deadline. Their baseline comparisons were DIFFERENT.
  Bounded proof/model/conditional-refinement scheduling remains incomplete.
- The size-three audit establishes bounded differential evidence, not a proof of
  unrestricted FOL soundness or completeness. Random pairs may repeat.
- Timings are a single paired serial run on a loaded machine, not repeated-run
  estimates. Production work budgets do not promise a two-second wall limit.
- Nonemptiness certificates assume all declared sorts inhabited; they do not
  identify a minimal subset of sorts. Failed conditional proofs yield no detail.
- Process/load inspection was unavailable: `ps -axo pid,etime,time,pcpu,comm | rg 'pytest|python|uv$'` returned `zsh:1: operation not permitted: ps`. No workaround was attempted; serial verification continued.
- No new trusted rule was added, so there is no Lean rule-set change to track.
  Existing Lean conformance/build checks are exercised by the full pytest run;
  no new Lean theorem is added here.

## PLAN CHANGES

None. Experiments can explicitly select a policy for
`relation_detail == "differs_only_on_empty_sorts"` while retaining the original
logical status, relation, distinguishing models, and conditional certificates.
