# T1d Part 2 results: offline verification comparison for universal rule-level claims (completed exploratory analysis)

2026-09-23. Opus build worker (branch `opus/t1d`). **Status: completed exploratory analysis, outside the
T1d confirmatory claims.** Part 2 was run in full before any T1d freeze, so it cannot be preregistered;
the second-round Opus review asked for it to be reported as results rather than as part of the
preregistration (v4 of [PREREG-T1d.md](PREREG-T1d.md) now only points here). Nothing below changes
if Part 1 is frozen, and no Part 1 confirmatory claim depends on it. No model calls.

Reproduce (repository root, `UV_CACHE_DIR=/private/tmp/ve-uv-cache-t1d`):

```sh
PYTHONPATH=. uv run --project experiments/T1d/solvers --locked python -m ve_experiments.t1d.part2
PYTHONPATH=. uv run --project experiments/T1d/solvers --locked --with pytest pytest -q tests/test_t1d_part2.py
```

Outputs: `part2-verification.json` (summary) and `part2-claims.jsonl.gz` (every claim row). Z3 5.1.0.0
and cvc5 1.4.0 are pinned in the separate uv project `experiments/T1d/solvers`. The second-round Astra
review independently reconciled all 11,355 claim rows and reran the 30 selected mutants through every
verifier and the Python/Lean rebinding rejection.


The model-monitor study is **dropped**: a monitor holding the formal gold rules can diff them or re-run
CHC, and every honest item would carry a label-revealing diff. Part 2 asks an offline question only: on
universal claims ∀u. T1(u) → ∀x. T2(x) → ¬tc⁺[step](u, x) over rule sets with permitted policy
changes (tag axioms, admin constraints, guarded edge rules including "unless" guards), what does each
verifier prove, refute or leave unknown?

* **Claims** (`rules.py`, generator unchanged). Gold rule sets are generated from seeds
  SEED_BASE + attempt; each gold claim is false (validator). Every single-rule mutation candidate of
  every type (added exception, narrowed scope, dropped inheritance, negation flip) of every attempted
  gold set is also a claim. Selection of the 30-set sample uses the independent validator only (v2
  also required Z3 agreement). **All attempted claims are denominators.**
* **Verifiers**, each reporting proved / refuted / unknown on every claim:
  * `validator`: pure Python over tag vectors; the reference (no `ve`, no solver);
  * `z3_chc`: Z3 Spacer over constrained Horn clauses (a decider);
  * `ground_z3`, `ground_cvc5`: the reviewers' baseline, ground inductiveness of the **same** DNF
    invariant VE uses, as three propositional queries (initiation, consecution, safety); proves or
    reports unknown, never refutes;
  * `ve`: closure@0 certificate from the dedicated untrusted builder, replayed in Python and, for
    every Python-valid certificate, by the Lean-proved checker; proves or reports unknown. A failed
    build is **unknown**, not "false".
* **Trust.** `validate`, `premises()`, `goal()` (with `step_body`/`step_case`) are trusted code new in
  T1d; an encoding error would make VE certify the wrong statement. `invariant_dnf` and the builder
  are untrusted (replayed); the builder is frozen by hash at freeze. CHC and the ground check rely on
  the tag-vector abstraction (argued exact in `rules.py`); VE's premises are first-order formulas over
  entities and do not.
* **Timing** is end to end (VE and ground times include invariant construction).
* **Regressions** on the selected sample: forged certificates for the false gold claims must not
  replay; each mutant's certificate, **rebound to the gold inputs** (binding fields replaced so the
  input check passes), must fail logically, not at the binding, in Python and in Lean, and the Python
  failure must be located at the mutated rule (the failing branch holds the gold's mutated edge case,
  or the failing split is a disjunction node containing it; for a dropped rule, which reshapes the step
  disjunction, the failure must be in the step-case analysis).

Results (`part2-verification.json`; every claim row in `part2-claims.jsonl.gz`). 145 gold sets were
attempted to select 30 (115 had no validator-true mutant of the assigned type); **11,355 claims**
were evaluated: 145 gold claims, 11,210 mutation candidates.

| Claims (validator verdict) | n | Z3 CHC | Ground check, Z3 | Ground check, cvc5 | VE (Python + Lean) |
|---|---|---|---|---|---|
| All claims, true | 475 | 475 proved | 475 proved | 475 proved | 475 proved |
| All claims, false | 10,880 | 10,880 refuted | 10,880 unknown | 10,880 unknown | 10,880 unknown |
| of which attempted gold claims (false) | 145 | 145 refuted | 145 unknown | 145 unknown | 145 unknown |
| Selected sample, true (mutants) | 30 | 30 proved | 30 proved | 30 proved | 30 proved |
| Selected sample, false (golds) | 30 | 30 refuted | 30 unknown | 30 unknown | 30 unknown |

* **No definite verdict contradicts the validator** anywhere (candidate-level disagreement log
  empty); Z3 CHC returned no `unknown`; every Python-valid VE certificate also replayed in Lean
  (475/475); BFS on the concrete witness state confirms every false claim.
* Candidates by type, validator-true / total: added exception 143 / 4,809; narrowed scope
  272 / 4,809; dropped inheritance 11 / 540; negation flip 49 / 1,052. Selected: 8, 8, 7, 7.
* **Forged** certificates for the 30 false gold claims: rejected 30/30 in Python and 30/30 in Lean.
* **Mutant certificates rebound to the gold inputs**: rejected 30/30 in Python and 30/30 in Lean;
  30/30 Python failures are logical, not at the binding ("literal cannot be expanded" 14, "open or
  malformed close node" 11, "wrong tableau branch count" 5); **30/30 located at the mutated rule**.
  For the 23 literal mutations and 2 of the 7 dropped rules the failing branch holds the gold's
  mutated edge case; for the other 5 dropped rules the failure is a split of the reshaped step
  disjunction (the structural criterion).
* End-to-end time on the 30 true selected claims (median / max): Z3 CHC 0.009 / 0.014 s; ground Z3
  0.010 / 0.017 s; ground cvc5 0.010 / 0.015 s; VE (invariant + build + Python replay) 0.09 / 0.75 s,
  plus Lean replay. Max VE replay 3,126 steps, trace depth 118.
* The generic `prove_entailment` search still hits ResourceLimit at 200,000 steps on 3/3 sets.
* Closed-world "unless" snapshots (unchanged): 15/16 certify in Python and Lean; the negated guard is
  essential in 16/16; 13/13 negation-flip forgeries rejected.

Caveat: the validator, CHC and the ground check share the tag-vector abstraction, so their agreement
is not independent evidence about the abstraction itself; VE's Lean-replayed certificates are the one
route that does not use it, and they agree on all 475 true claims.

**What Part 2 can and cannot show.** Z3 CHC is the only verifier here that also refutes. The ground
Z3/cvc5 check proves what VE proves, given the same invariant, in milliseconds. VE's distinct property
is a small, independently replayable, Lean-proved checker whose premises do not depend on the
tag-vector abstraction. Part 2 makes no claim about monitors or English.


## Limitations (disclosed)

1. **Dropped-rule localisation** in the rebinding regression is structural for 5 of 7 dropped rules
   (the failure is a split of the reshaped step disjunction), weaker than the literal mutations'
   "the branch holds the mutated case".
2. **Closed-world snapshots** still fail 1/16 at the JSON nesting limit (a log-depth builder is
   needed); they are outside the comparison.
3. **`ve assist` authoring** is unfixed; Part 2 includes no agent-authored transcriptions.
4. The analysis was designed and run by the same worker without preregistration; treat every number
   as exploratory.
