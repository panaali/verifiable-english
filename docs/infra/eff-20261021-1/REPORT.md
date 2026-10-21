STOP RULE: the proposed pytest sweep on me-6b's reviewed HEAD took 862 s at four jobs, exceeding 3 × the 265 s Lean-only sweep (795 s). The control pytest selection had collection errors, so it gave no valid kill. No implementation of `--pytest` or new operators is retained.

# eff-20261021-1: measured stop

## Decision and evidence

The worktree started clean at `7855620f3` on `infra/eff-20261021-1`. The supplied `reviews/efficiency-daily-20261021.md` was absent; [PIPELINE-LIMITS.md L77, L90, L91, L93](/home/seyran/code/manage-agents/PIPELINE-LIMITS.md) and the eight first-review records under `/home/seyran/code/manage-agents/` supplied the primary finding descriptions. The Mac runner was reported offline at launch; the measurement was on this VM with `--jobs 4` and `VE_LEAN_SHARE=off`. `lean-prep.sh` could not log to its read-only shared log, so the scratch builds started cold.

| Reviewed tree and command | First 40 / candidates | Time | Result |
| --- | ---: | ---: | --- |
| me-6b `82c0e6ad8`, base `c5197da7`, Lean only | 40 / 138 | 265 s | 30 SURVIVOR, 9 UNKNOWN, 1 INVALID, 0 KILLED |
| Same tree and jobs, `--pytest` with the two reviewer probe IDs | 40 / 138 | 862 s | 39 UNKNOWN, 1 INVALID, 0 pytest kills; control test collection error |

The second run used `uv run python`. A prior invalid invocation used system `python3`, which lacked pytest, and took 834 s; it is excluded from the ratio. The valid invocation is **3.253×** the Lean-only time, already over the stop threshold without a successful pytest control. The named reviewer probe IDs, `test_fixture[factor-below-one]` and `[refuse-base-identifier]`, do not exist in the reviewed commit: the fix added them. The reviewed Units fixture instead compiles an outside Lean file via `lake env lean` from its checkout (`tests/test_calc_units.py` and `tests/lean_build.py` at `82c0e6ad8`). `VE_LEAN_SERVICE` cannot redirect that fixture to a scratch build. These are separate reasons this trial cannot establish a pytest kill.

The 138 candidates include the prototype's later-tier operators; the reviewed tool listed 119. Both timing runs used the same prototype and its first 40, which contain only the original tiers.

[Evidence](evidence.json) has 34 corpus rows. [Lean-only raw sweep](lean-only.json) and [pytest attempt raw sweep](pytest-attempt.json) retain every verdict and input digest. [verify_evidence.py](verify_evidence.py) checks their counts, times, reviewed source text, and every row. It deliberately exits 1 for the rows whose reviewed or fixed verdict was not replayed because the stop rule fired; no row is silently treated as passed. Thus the other stop test, at least eight reviewed SURVIVOR to fixed KILLED pairs, remains unmeasured. The corpus includes every hand mutant named in me-6b, me-9b, df-1ac, me-2, ap-1b, and the available first reviews me-5, me-9, and ap-1a. Each row records file, line, exact edit, reviewed and fixed commit, fixture added, current operator equivalent, G1/G2, and the observed or unmeasured verdict. The 34 rows classify 21 G1 and 13 G2 candidates; these classifications are a source inspection, not replay results. `UNMEASURED` explicitly prevents a success claim.

## Build outcome

A scratch-only prototype implemented the proposed phase, exact-hash scratch lock, later-tier operators and hermetic tests. Its focused tests passed, including a tiny Lean package whose mutant executable failed a pytest fixture while its control passed. It was reverted when the stop rule fired. The committed change is evidence and this report only. The checkout's tool and tests are byte-identical to the starting HEAD. No generated file, Lean, Rust, or product Python changed. There is no user-visible VE delta or trust growth, hence no DELTA table or DRI signature.

No full release gate was run, as directed; the chain will run it on the committed final HEAD. No failure from `main-known-red.txt` arose. The selected run on the VM selected 49 units; **all 49 test units passed**, including `tests/test_trust_mutants.py` (exit 0, 1,642.9 s). The wrapper itself exited 1 after the tests because `test_map.write_map` tried to create a temporary coverage-map file under the read-only `/home/seyran/.cache/ve-testmap`. That is a post-test bookkeeping failure, not a failed test. Earlier attempts were interrupted or failed during setup: the first snapshot saw no tracked changes and selected all units; a Mac checkout lock then expired; local retries exposed read-only uv and Lean build cache paths. The final run used writable caches for those stages and the existing coverage map for selection.

## Orchestrator lines, conditional on a later successful design

These are the exact replacement texts to consider **only after** a new measurement clears both stop rules. This item does not edit manage-agents.

**BUILDER-CHECKLIST item 3 trust_mutants bullet:**

> Trusted Lean growth under R16: run `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --pytest <the item's fixture tests> --json docs/<batch>/trust-mutants.json` on the final Lean change. Name each pytest node ID or test file explicitly; use `--exe NAME=ENV` for every non-default Lean executable those tests run. Fix or exactly allow every SURVIVOR and UNKNOWN; raise `--max-mutants` for NOT RUN. Commit evidence and allow reasons. For unchanged inputs, `--rescore` may reuse the same verdicts; changed fixture bytes, pytest args or executable digests must force a full run. Reviewers still plant forms beyond OPERATORS: compound operand omissions, argument constants, sibling lists, multi-read fault-order swaps, and Lean checks outside the mutated module's directory unless `--deep` was used.

**build-checklist.txt line 13a:**

> 13a. Trusted Lean growth (R16): run `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --pytest <the item's fixture tests> --json docs/<batch>/trust-mutants.json` on the final Lean change. Name worktree-relative pytest node IDs or test files and all non-default executables with `--exe NAME=ENV`. A mutant is killed by pytest only when the identical control selection passes and a mutant test fails; collection errors, skips, timeouts and missing binaries remain UNKNOWN. Fix or exactly allow every SURVIVOR and UNKNOWN; raise the cap for NOT RUN. Commit evidence. Reuse `--rescore` only on byte-identical tool, Lean, test, argument and executable inputs. Reviewers rerun without `--rescore` and plant compound operand omissions, argument constants, sibling lists, multi-read fault-order swaps, and out-of-directory Lean checks beyond OPERATORS.

`mac-pytest.sh --trustmut` **would need** to rewrite the path part of each `--pytest tests/file.py::test_id` argument to a worktree-relative path, preserving `::test_id`, just as it rewrites `--test`, `--allow` and `--rescore`. A VM absolute path cannot identify the corresponding Mac worktree file. This need remains unimplemented under the stop rule.

## Self-review against BUILDER-CHECKLIST

1. N.A. — no Lean response route or schema changed.
2. PASS — the stop decision, corpus and raw sweeps are in `evidence.json` and `verify_evidence.py`; no implementation claim remains.
3. N.A. — the stop rule ended implementation before a new check was retained; `verify_evidence.py` refuses the unmeasured rows (exit 1).
4. N.A. — no product behaviour changed.
5. N.A. — no relayed field changed.
6. N.A. — the chain runs the final-HEAD gate; this worker was explicitly told not to.
7. PASS — no DELTA row or trust growth; `git diff main...HEAD` was reviewed and contains only this evidence bundle.
8. PASS — no VE output changed; source files are unchanged.
9. PASS — 49 selected test units passed through `mac-pytest.sh --select`; `test_map.write_map` failed afterward on its read-only cache path.
10. N.A. — no Lean statement or theorem changed.
11. N.A. — no public budget, limit or deadline changed.
12. N.A. — no runtime product path changed; the 265 s and 862 s measurement is the task's own efficiency stop.
13. PASS — no test removed or renamed; test collection is unchanged by the evidence-only diff.
