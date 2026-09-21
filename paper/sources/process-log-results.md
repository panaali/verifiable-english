- 12:09 **E1 SCORED RESULT (frozen 555b3ae; results cb2b7ff on claude/e1; experiments/E1/RESULTS.md): CLAIM NOT SUPPORTED for the
  32B primary judge.** 874 candidates, 12 templates, 17,480 trials, 0 failures. False approval, ve_strict vs fol_symbols,
  97.5% cluster-t: P1 (asserted-faithful explanation) .152 vs .187... [C2 text: 0.152 (90/594) vs 0.187 (111/594), difference
  +0.027 [-0.065,+0.120]: CHECK SIGN/ORDER IN RESULTS.md before quoting] INCONCLUSIVE; P2 (no explanation) .296 vs .293,
  +0.003 [-0.043,+0.049]: REFUTED (a 0.05 reduction is excluded; not harmful). Honest-acceptance constraints hold.
  EXPLORATORY (95%): 14B P2 -0.106 [-0.202,-0.010], P1 -0.045 [-0.114,+0.023]; ve_fluent vs fol_symbols 14B -0.147
  [-0.216,-0.078] with explanation, -0.141 [-0.200,-0.083] without; 32B ~0 / -0.044 [-0.114,+0.027]; fol_keywords vs
  fol_symbols ~0 for both; explanation lowers FA in every view (32B fol_symbols -0.126) AND lowers honest acceptance
  (.914 -> .793): judges get more suspicious. E1b 32B: .830 fol_symbols, .842 ve_strict, .878 ve_fluent. Compute: scored job
  57 min on A100-80GB = ~7.1 units. Luna reference NOT run.
- 12:25 **E4 SCORED (frozen codex/e5 @ cbc6a80; 120 inferences, 12 templates; results in colab/results/e4-scored-a/out/score-summary.json).**
  Counts (false approval of INVALID inferences / honest acceptance of VALID ones): 14B checked_countermodel 0/60, 53/60; dishonest
  critic 9/60, 49/60; prose critique 16/60, 44/60 (18/120 parse failures scored worst case). 7B checked 0/60, 52/60; dishonest
  9/60, 31/60; prose 0/60, 4/60 (7B rejects nearly everything under a prose critique). PRIMARY (false approval, checked minus
  prose, cluster-t 95%, k=12): 14B -0.267 [-0.392,-0.142] = SUPPORTED for 14B; 7B 0.00 (prose arm at floor because 7B rejects
  all) but honest acceptance +0.80 [0.56,1.04]. Colab STOP sent (A100 runtime unassigns). First use-case agent done and
  committed (usecases/main e1d4069): debate reduces to the extension of one predicate; both sides valid given own premises.
