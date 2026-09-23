# T1d v4 status (2026-09-23, wrap-up; not frozen, no model calls)

## Done (commits a0c3fae and this one)
- Generator v4 (`materials.py`): every candidate certified subject (principal, twin, alias, group, role) is a hub
  from one template (3 relation edges to hubs, local links, D + 2 chains, one intact). Hub in-degrees are matched,
  and the resource and its twin get chain granters in both labels. The directory lists every non-resource entity.
  Items are sized by bytes (170-195 kB raw prompt, cap 200 kB, so Haiku fits), not 20,000 facts. No padding.
- Leakage audit v4 (`leakage.py`): 1-2-hop degree profiles of the account/subject and resource/certified resource,
  plus directory features. Kind-matched honest references for group/role. 2,000 permutations (smallest Holm p
  .020), unrounded p. Pooled-group Holm replaces the pooled-unadjusted rule. Univariate Mann-Whitney + Holm.
  Burned `leakdev`: univariate clean (850 tests, min Holm p 1.0); multivariate AUCs 0.36-0.59.
- Fresh v4 `audit` + `full` prepared with Lean: every expected outcome holds.
- NI bound = (1 - alpha_j) Tango interval, with a regression test. Power scenarios use one shared raw rate
  (`power.py`, not yet rerun). Stratum renamed "related-entity".
- Run harness (`run.py`, `transport.py`) and `analysis.py`: success / refutation (harm or NI failure) /
  inconclusive. Tests pass (61).
- Part 2 moved to `PART2-RESULTS.md`.

## Remaining
1. **Leakage audit not completed.** The single run on audit + full hung with no CPU progress for more than 2 h
   and was killed; `leakage.json` is still v3. Likely cause: a fork-context `multiprocessing.Pool` created after
   numpy/sklearn had started BLAS/OpenMP threads (a macOS fork deadlock), made worse by machine load of 20-50.
   Fix: use `get_context('spawn')` or `forkserver`, set `OMP_NUM_THREADS=1`, and log progress. Then rerun ONCE
   (fresh seeds are untouched by any result).
2. Rerun `power.py`. Then run `run.py materialize` and `manifest` (writes the items, evidence, prompt hashes,
   schedule and HASHES-draft).
3. Rewrite `PREREG-T1d.md` to v4. It still describes v3 (20,000 facts). Also: high effort becomes a SECONDARY
   endpoint; success = lower false approval AND NI at 10 pp; refutation = harm or NI failure; non-rejection is
   inconclusive; budget = ten five-hour windows plus the weekly cap.
