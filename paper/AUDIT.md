# Claude-side claim audit of `paper/sections/*.md`

Auditor: Claude (Opus 5), adversarial verification pass, 2026-09-21.
Scope: every number, every statistical decision, every assurance/speed/novelty
claim, every citation, and the disclosure set, checked against committed
evidence. Nothing in the paper was rewritten; this file is findings only.

## What was checked and reproduced

Numeric verification was exhaustive rather than sampled. Every count, rate,
interval, corpus size, theorem count, token count, compute figure and date in
the eleven body sections was traced to its source file.

- **E1.** All 20 cell rates, both co-primary contrasts and their HA constraints,
  all 48 exploratory contrasts, both bootstrap sensitivity rows, the E1b table,
  the covariate table, the fluent-contraction shares, the attack-family,
  oracle-direction and empty-sort breakdowns, and the exclusion ledger were
  matched line by line against `experiments/E1/RESULTS.md` (identical to
  `paper/sources/e1-results.md`). The frozen inventory arithmetic closes:
  12 x 8 = 96 base items; 280 good (96 + 184) + 594 bad (280 + 184 + 130) = 874;
  243 + 142 + 209 = 594; 128+64+25+2+37+4+0+0 = 260 excluded; 874 + 260 = 1,134;
  594 - 41 = 553; 8,740 x 2 = 17,480 trials; 4,370 = 874 x 5 per judge for E1b;
  13,110 x 2 = 26,220 prompts. The dev e3 table, the balance figures
  (SMD +0.005, hedging 0, AUC 0.469 against thresholds |SMD| < 0.20 and
  AUC in [0.40, 0.60]), the e1/e2 history (-0.22, AUC 0.78; AUC 0.525;
  0.31 -> 0.05), the explanation-sample counts (111 samples, 15 rejected,
  54-63 words), the full judge ladder (local MLX, Colab L4, JSON-legend
  .96/.77/.15, compact gate cell, hosted references) and the power
  approximations (.09/.13, .145/.18, half-widths .07/.10, t = 2.593) all match
  `experiments/E1/PREREG.md`, `BALANCE-scored.json`, `BALANCE-dev.json`,
  `judges.json`, `DEV-qwen.md`, `DEV-qwen-e3.md`, `paper/sources/local-ladder.md`,
  `colab-ladder.json` and `process-log-v1.md`.
- **E4.** All six cell counts, all four frozen contrasts, the dev table, the
  gate band, the token audit and the manifest fields were matched against
  `/Users/seyran/code/manage-agents/colab/results/e4-scored-a/out/score-summary.json`
  and the two run manifests. `paper/analysis/e4_sensitivity.py` was re-executed
  and reproduces `paper/generated/e4-sensitivity-table.md` byte for byte,
  including -0.117 [-0.231, -0.002] and the 300/658/7-token audit.
- **Statistical decisions.** Both frozen rules were applied literally and
  correctly. E1: P2 lower bound -0.043 > -0.05 and not > 0, so "refuted, not
  harmful"; P1 spans -0.05, so inconclusive; the combined per-judge claim is
  correctly reported as NOT supported and explicitly not refuted. Both HA
  constraints (lower bound >= -0.10, point estimate >= -0.05, VE-strict HA >= .70)
  are satisfied and correctly described. E4: the 14B FA upper bound is below
  zero and the paired HA lower bound (+0.027) is above -0.05, so protection is
  supported; the paper correctly refuses to read -0.267 as a >= 22-point
  reduction. Confidence levels are right everywhere: 97.5% only for the two E1
  co-primaries and their HA constraints, 95% for every bootstrap, every
  exploratory contrast, E1b and all of E4.
- **Lean.** `python3 lean/audit.py` was run: PASS, 41 source files, **200** named
  theorem declarations, allowlist exactly `{propext, Classical.choice, Quot.sound}`.
  The four claim-limit reviews in `/Users/seyran/code/manage-agents/review-lean.md`
  were read in full; the paper avoids every forbidden phrase ("Lean-verified VE",
  completeness, verified claim-graph checker, verified Python/Rust binary,
  `NotFound` = non-entailment) and correctly reports 3,500 / 2,622 / 0 / 2,634 / 65.
- **Rust.** `docs/rust.md` confirms the honest characterisation; the paper uses
  ~30x on the larger evaluation kernels, never 56-67x, never a pruned-search
  ratio. 3,000/3,000 closure agreements and the 5.38 / 15.01 closure kernel
  ratios are correct.
- **Conformance/coverage.** All eight conformance corpus sizes, the certificate
  ledger (811 = 732 + 77 + 2; 795/795; 592/592; 63/63), the 5,000/5,000 fuzz
  stream, the E0 per-dataset tables, the agreement/kappa table, the corrections
  table (114 witnesses, 3 defective, 111/210) and the full projection table
  (114/141/128/155 and 111/141/125/155) match `conformance/*.json`,
  `paper/sources/e0-metrics.json` and `docs/spec/v0.1-coverage.md`.
- **Use cases.** 9 claims / 4 DIRECT / 5 NO, 0 DIRECT + 1 REIFIED + 3 OPAQUE,
  and runs 1-5 (NotFound, Found, Found, NotFound, NotFound) at
  `--nonempty-domains --max-domain-size 3` all match the snapshots. The paper
  explicitly declines the snapshot's stronger "NotFound proves entailment"
  wording, which is the correct call.
- **Citations.** All 23 URLs cited in the sections appear in `paper/references.md`,
  all 23 references are cited, and every one resolves to a repository doc that
  carries the same URL. Exactly one entry is marked unverified in the repository
  (`doi.org/10.1007/978-3-540-85658-0_3`), and the paper flags it in both
  `references.md` and 02-background.md.
- **Placeholders.** Only `RESULT-T-GATE` and `RESULT-T-TRAINING` remain. All 13
  `<!-- INCLUDE -->` targets exist. The built PDF's sections are byte-identical
  to the ve-integration sections.

**No numeric mismatch was found.** Every finding below is a wording, scope,
provenance or disclosure issue.

## Findings

| # | Severity | Location | Claim as written | Evidence | Required wording or value |
|---|---|---|---|---|---|
| 1 | must-fix | 00-abstract.md:7 | "Lean proves specified reference evaluator, **serialization**, certificate, and graph properties" | 05-assurance.md:55-60 lists "canonical serialization and hash binding" among what executable acceptance *trusts*, not proves; `manage-agents/review-lean.md:20-21` "May NOT claim ... verified decoding"; :62-64 "MUST NOT claim ... verified Python checker or JSON layer". Lean proves the reference *printer/parser* round trip, not the JSON wire layer. | "Lean proves specified reference evaluator, printer/parser round-trip, certificate, and graph properties". |
| 2 | must-fix | 00-abstract.md:26 | "Coverage without extensions is low." (unscoped sentence) | 06-coverage.md:160-161 scopes the finding to "this real policy text"; 06-coverage.md:61 "No pooled population coverage percentage is justified"; second-rater lenient fits reach 26/30 (ProofWriter) and 25/30 (FOLIO) in `paper/generated/e0-coverage-table.md`. As written the abstract states a general coverage result E0 explicitly disclaims. | "Coverage of this policy text is low without extensions." |
| 3 | must-fix | 00-abstract.md:18-23 | "Machine-checked components did help in a separate countermodel-display demonstration: for 14B ... for 7B ..." | `experiments/E2E4/E4/PREREG.md:87-89` "**Neither selected judge passed this gate**"; :4-6 "pilot-sized ... mechanism demonstration, not a confirmatory efficacy study"; :9-11 "one model family (Qwen2.5)". 07-experiments.md:393-394 and 09-limitations.md:77 disclose this; the abstract does not. | "...in a separate, pilot-sized countermodel-display demonstration whose two Qwen2.5 judges both failed its own calibration gate: for 14B ...". |
| 4 | must-fix | 00-abstract.md:16-17; 01-introduction.md:49-50; 09-limitations.md:6-9 | "Hosted **small** models read FOL near-perfectly in development calibration, **so model readability is not the bottleneck** on these tasks." | (i) `experiments/E1/PREREG.md:96-98` classifies gpt-5.6-luna and claude-haiku-4-5 as **strong-end reference** judges (accuracy 0.97 each, 1.00 in the G1 strong-model mean); "small" is nowhere established. (ii) The Haiku row is labelled "(JSON legend)" and was never remeasured under the frozen compact prompt (PREREG.md:98; disclosed at 07-experiments.md:119 but not where the inference is drawn). (iii) 07-experiments.md:120 states these judges "cannot support or refute the E1 claim", which the inference then does. | "The two hosted reference judges (one measured only under the earlier JSON legend) were at ceiling on these development items, so these items do not saturate capable readers." Drop "small" and drop the general "not the bottleneck" inference, or keep it only in the task-specific form already used at 07-experiments.md:144-145. |
| 5 | must-fix | 10-process.md:81 (compute table, row 1) | "Development before scored runs \| L4 \| About 12 \| **Previously committed runner handoff**; includes earlier development." | `paper/sources/v1-handoff.md:3`: "The **user reports** about 12 Colab units used on L4 before the scored run." The section header (10-process.md:76-77) promises to distinguish "runner estimates from recorded runtime fields and from a metered bill"; an unaided human self-report is none of the three and is the weakest row in the table. | Provenance cell: "Human self-report relayed in the v1 handoff; not a runner estimate, a recorded runtime field, or a bill." |
| 6 | should-fix | 07-experiments.md:448-453 | "the primary FA contrast -0.267 [-0.392, -0.142] **supports protection under the preregistered rule**" (no floor caveat for 14B) | `experiments/E2E4/E4/PREREG.md` Refutation condition: "**Floor/ceiling outcomes cannot identify the primary mechanism** even if they exclude the planning reference." The 14B checked arm is 0/60, a treatment-side floor; the paper applies the floor caveat only to the 7B prose arm (07-experiments.md:472-474). | Add one clause: "The checked arm is itself at floor (0/60), so the frozen rule's floor caveat limits mechanism identification here too." |
| 7 | should-fix | 00-abstract.md:22 | "+0.80 [0.56, 1.04] from near-universal rejection (95% intervals)" | 07-experiments.md:476-477 discloses "The unbounded cluster-t interval is reported as specified, including its endpoint above one"; the abstract quotes the infeasible endpoint without that note. | "+0.80 [0.56, 1.04] (unbounded cluster-t; the upper endpoint exceeds the feasible maximum)". |
| 8 | should-fix | 05-assurance.md:94-95 | "about thirty times faster on the larger measured finite-evaluation kernels" | `docs/rust.md:299` characterises the kernel as "**roughly 20-30x**"; the paper reports the top of that range. The two rows actually shown (31.46 at size 32, 30.14 at size 64) do support ~30x, but the documented range is not given. | "roughly 20-30x on the evaluation kernel, about thirtyfold on the two largest measured workloads shown below". |
| 9 | should-fix | 10-process.md:26 (defect table) | "added a **complete** duplication-signature audit" | 07-experiments.md:534-535 "its chance bound covers only the audited features, not all classifiers or semantic leakage"; 10-process.md:59 "Finite-inventory structural audit described in revision; not a semantic-classifier bound". "Complete" invites the reading the same paper twice denies. | "added a duplication-signature audit over the enumerated features". |
| 10 | should-fix | 10-process.md:10-11 | "a subsequent Claude-side manuscript audit is **pending**" | This audit is that pass. The sentence goes stale the moment this file lands. | Replace with a statement of the audit and its outcome, or "a Claude-side manuscript audit was performed and its findings are recorded in `paper/AUDIT.md`". |
| 11 | nit | 06-coverage.md:49-50 | "Each fit cell gives the count, percentage, and **nominal Wilson interval**" | The level (95%) appears only inside the generated table captions (`paper/generated/e0-first-table.md`, `e0-coverage-table.md`). | State the level in the body text: "nominal 95% Wilson interval". |
| 12 | nit | 07-experiments.md:89-90 | "The style feature lists were revised before freezing to remove logical content words" | `experiments/E1/PREREG.md:56-57`: "revised **twice** on the day they were written". | Add "twice". |
| 13 | nit | 05-assurance.md:18 | `Graph.check_sound`; `check_entails` row: "...establishes acyclicity, unique names, exact claim provenance, and root entailment..." | `review-lean.md:45-46` "MAY NOT claim: ... verified end-to-end argument graphs". The paper is saved by the table preamble (05-assurance.md:5-6, "concern the named Lean reference definitions") and by 05-assurance.md:50 / 09-limitations.md:89, but the row itself reads absolutely. | Prefix the row's plain-language cell with "For the Lean reference graph checker:". |
| 14 | nit | 03-language.md:98; 07-experiments.md:134 | "roughly 4,000-character JSON legend" | Correct (`experiments/E1/PREREG.md`), but `experiments/E1/judges.json` records the *final compact* prompt at "3,900 characters per prompt". The two near-identical numbers measure different things (old legend alone vs. whole final prompt) and can be misread as showing no change. | Optionally add "(the final compact prompt is about 3,900 characters in total)" once, at 03-language.md:98. |
| 15 | nit | 06-coverage.md:52-53 | "its Gatekeeper core-rule counts do not all cover opaque exemptions" | Correct and already disclosed; the underlying spread is 10/30 strict in the frozen first-rater table versus "7/30 strictly" in `paper/sources/process-log-excerpts.md:9` and `experiments/E0/SURVEY.md:33`, both of which are the same data under two readings. | No change required; retain the sentence. Recorded here so the 7-vs-10 discrepancy is not read as an error. |

## Severity counts

- must-fix: **5**
- should-fix: **5**
- nit: **5**

## Overall judgement

**Yes, with five clause-level corrections: the paper is honest and supportable
as written.** This is an unusually clean manuscript by the standard this audit
applies. I could not find a single wrong number. The two preregistered decision
rules are applied literally, including the uncomfortable ones: E1's primary
claim is reported as not supported, P2 as refuted, and the paper refuses both to
call it refuted as a whole and to read the E4 -0.267 as a >= 22-point reduction.
Both the preregistered and the post hoc E4 contrasts are present and labelled,
and the post hoc analysis is reproducible from committed code. Confidence levels
are correct throughout (97.5% only where Bonferroni requires it). Exploratory
results are fenced under headings that say so, and the fluent-rendering result
-- the paper's most tempting positive -- is kept as a replication hypothesis in
every place it appears. The Lean section respects all four reviewers' explicit
prohibitions; the speed claim is the honest ~30x kernel figure, not the API or
pruned-search ratios; the use-case section overrides its own source's
over-strong `NotFound` language. Disclosure is thorough: AI authorship, no human
participants, one-family judges, dev/scored separation, and six process failures
including two that invalidated measurements.

The residual risk is concentrated in the **abstract**, which is the only part of
the paper that outruns its evidence, and does so four times (findings 1-4): it
generalises the policy-use-case coverage result into an unscoped one, omits that
both E4 judges failed their own gate, calls two strong-end reference judges
"small" and converts their ceiling into a general readability conclusion, and
lets "serialization" be read as the JSON layer that the reviewers forbid
claiming. Every one of these is already stated correctly in the body, so the
patches are clause-level and cost the paper nothing. Finding 5 is a provenance
misattribution in a table whose entire stated purpose is provenance separation.

After those five edits I would not object to any claim in the paper.

<!-- Audit inputs: experiments/E1/{PREREG,RESULTS,DEV-qwen,DEV-qwen-e3}.md,
BALANCE-{dev,scored}.json, judges.json; experiments/E2E4/E4/PREREG.md;
manage-agents/colab/results/e4-scored-a/out/{score-summary.json,*/manifest.json};
paper/analysis/e4_sensitivity.py (re-executed); manage-agents/review-lean.md,
review-views.md, ve-run-log.md; lean/audit.py (re-executed), METATHEORY.md,
CLOSURE.md, README.md; docs/rust.md, docs/oracle.md, docs/prover-fair-report.md,
docs/prover-fair/{before,after}.json, docs/spec/v0.1-coverage.md;
conformance/*.json; experiments/E0/SURVEY.md, closure_witnesses/report.json;
paper/sources/* ; paper/generated/* ; paper/reference-audit.json. -->

## Resolution

Resolved by GPT-6 Astra on 2026-09-21. All manuscript changes are in
`f32be8b`; item 5 follows the user's explicit provenance correction rather
than the audit's proposed self-report wording. `make html pdf` passed with
`XDG_CACHE_HOME="$PWD/.cache" TECTONIC_CACHE_DIR="$PWD/.cache/tectonic"`
from `paper/`; no test suites were run.

| Item | Resolution | Fix commit |
|---|---|---|
| 1 | Replaced serialization with printer/parser round-trip. | `f32be8b` |
| 2 | Scoped low coverage to this policy text. | `f32be8b` |
| 3 | Disclosed pilot size, Qwen2.5 judges, and both calibration-gate failures. | `f32be8b` |
| 4 | Used the hosted-reference wording and JSON-legend caveat in all three locations. | `f32be8b` |
| 5 | Labelled about 12 units as the orchestrator's estimate from runner uptime times 1.7 units/hour, neither a Colab bill nor a user report. | `f32be8b` |
| 6 | Added the 14B checked-arm floor caveat. | `f32be8b` |
| 7 | Explained the unbounded cluster-t endpoint in the abstract. | `f32be8b` |
| 8 | Stated the 20-30x range and the two largest workloads' thirtyfold result. | `f32be8b` |
| 9 | Scoped the duplication-signature audit to enumerated features. | `f32be8b` |
| 10 | Recorded the completed Claude-side audit and its location. | `f32be8b` |
| 11 | Specified nominal 95% Wilson intervals. | `f32be8b` |
| 12 | Specified that style features were revised twice. | `f32be8b` |
| 13 | Prefixed the graph result with its Lean reference checker scope. | `f32be8b` |
| 14 | Added the final compact prompt's total character count. | `f32be8b` |
| 15 | Retained the Gatekeeper opaque-exemption sentence as requested; no change required. | No fix needed; retained in `f32be8b`. |
