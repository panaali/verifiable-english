# Process disclosure

The project was organized around a Claude-side worker and a GPT-side worker,
with additional task-specific AI instances, under a Claude-side AI orchestrator.
The human user set the objective, changed scope, supplied compute access, and
requested review. The protocol required cross-family review before integration
merges. The log records review requests, rejected merges, revisions, and
integration failures. This is a production record, not a controlled comparison
of development methods. This drafting pass used GPT-6 Astra after the Claude
scaffold author exhausted quota; a subsequent Claude-side manuscript audit is
pending.
<!-- src: PROTOCOL.md; paper/sources/process-log-excerpts.md;
paper/sources/manifest.json; user drafting handoff recorded in paper/README.md. -->

The following defects illustrate what review actually caught. Counts from the
external orchestrator log are preserved as reported observations, not independent
reruns by the paper author.

| Defect caught | Consequence and recorded response |
|---|---|
| Judges could read ground truth from disk | The initial CLI harness retained tools. Prompt separation therefore did not isolate labels. Review required disabling tools and invalidating tool-using trials. |
| Cache collapsed repeated samples | Repeated assignments could reuse a response instead of obtaining the intended new sample. Review required trial-specific cache identity and explicit repeat handling; a cache replay is not an independent draw. |
| Converse template in the natural view | A relation such as `owns(person, service)` accepted wording like `{0} is owned by {1}`. The apparent direction could change only in the natural display. Revised lexical checks and a common identity-bearing legend narrowed this attack surface. Arbitrary semantic lies remain possible. |
| Unfair universal-rule scheduling | Early gamma choices repeatedly used some instances and starved useful witnesses. Semantically equivalent formulas became UNKNOWN. Fair bounded rounds and connection priorities changed search, while replay rules remained fixed. |
| Certificate-version mismatch after merges | Python's oracle introduced compound-formula closure before the Lean adapter supported that certificate version. Separately reviewed branches failed integration. The fix proved the existing rule in Lean, aligned decoding depth, repaired fixture naming, and added regressions. |
| Structural shortcut in E5 | An uncited dossier unmatched by any cited dossier revealed the label despite lexical balancing. Revision changed copy construction and added a complete duplication-signature audit; fresh model calibration remains necessary. |

<!-- src: paper/sources/process-log-excerpts.md, entries 01:03, 01:24, 02:11,
02:48, 03:10, 03:50; paper/sources/review-views.md; docs/rendering-views.md;
docs/prover-fair-report.md; docs/integration-fix-report.md;
paper/sources/e5-prereg-draft.md. -->

Further episodes affected both measurement and scheduling:

| Episode | Consequence and response |
|---|---|
| JSON legend swamped the statement | The roughly 4,000-character legend put all tested Qwen judges outside the primary FA gate. A compact, common legend replaced it, and calibration was rerun before freezing. |
| Explanation balance failed | A style-only classifier distinguished labels (AUC .78), and length SMD was -.22. Fixed-form e2 passed but helped judges detect bad statements. Final e3 asserts one faithful reading verbatim across each base item's candidates; it also lowered FA on dev. |
| Genuine instruction treated as possible injection | A worker ignored an actual orchestrator message because it arrived inside tool output. The orchestrator resent it as a task message and work resumed. The delivery channel made legitimate coordination resemble untrusted content. |
| Usage-limit outage | The 04:00--04:50 Claude session limit interrupted the paper, Colab, and implementation workers. The orchestrator reduced Claude concurrency and moved drafting/build work to the separately metered GPT worker. |
| Colab idle shutdown and restart | Runtime idling required restart and dependency restoration; missing `ninja` blocked dev jobs, and E5 prompts also exceeded the initial context setting. Jobs were resubmitted after installation and revised preflight. A later queue/watchdog stall cost roughly two hours before orchestration resumed. |

The E5 duplication shortcut and certificate-version mismatch in the earlier
table remain relevant: structural balance did not guarantee task validity, and
separately reviewed changes did not guarantee a compatible integrated checker.
E1's later cross-review also required isolated CLI settings, routing E1b through
the common runner, enforced oracle/balance gates, and invalidation of truncated
or tool-using trials before parsing. These changes preceded the scored freeze.
<!-- src: paper/sources/process-log-excerpts.md; paper/sources/process-log-v1.md;
paper/sources/process-operations.md; paper/sources/e1-prereg-frozen.md. -->

The quantitative context is deliberately separated by audit population:

| Process observation | Reported count or rate | Evidential status |
|---|---|---|
| Reviewer's oracle distribution, before scheduling fix | 10.9% UNKNOWN overall; 32% at depth at least 3 | External log report, not the public paired benchmark |
| Committed paired scheduling benchmark | 237/602 UNKNOWN before; 2/602 after | Synthetic development suite, including timeouts |
| E5 shortcut on reviewed spread items | 384/384 identified | External review observation on superseded material |
| Revised E5 duplication-signature feature bound | 0.50 best accuracy | Finite-inventory structural audit described in revision; not a semantic-classifier bound |

<!-- src: paper/sources/process-log-excerpts.md, 02:11 and 03:50;
docs/prover-fair/before.json; docs/prover-fair/after.json;
paper/sources/e5-prereg-draft.md, offline leak audit.
Do not compare the private 10.9% distribution to the 602-pair benchmark as one experiment. -->

These examples show that cross-family review detected concrete mistakes in
semantics, measurement, and integration. They do not measure how many defects
remained, prove that another family was necessary, or show that AI review can
replace expert human judgment. In particular, a theorem can be valid about an
unfaithful formal definition, and both reviewers can accept the same bad
translation. Tests and theorem checking reduce specific uncertainties; review
must still inspect the statements and measurement contracts.

## Compute and cost

The supplied accounting reports about 12 Colab compute units used on L4 before
the scored run. The scored runtime is an A100-80GB at 7.5 units/hour; the older
A100-40GB rate of 5.4 does not apply. The orchestrator estimated 2--2.5 hours
(about 15--19 units), but this was a budget forecast, not a completed measurement.
E1 assigns 13,110 prompts per judge (8,740 sign-off and 4,370 E1b), or 26,220
for its two Qwen judges. E4 adds 720 calls. Retries, setup, idling, and optional
hosted references must be accounted separately from assigned scored calls.

**[RESULT-COST: insert completed scored wall time, units, actual token usage,
and any metered hosted cost; do not replace the final bill with the forecast.]**

Local MLX pilots and hosted generation/review used separate resources without a
complete dollar ledger in the supplied records. Quota limits shaped both the
single-family scored roster and the decision not to execute E5. Colab units are
reported as units, not converted to dollars using an assumed purchase price.
<!-- src: paper/sources/v1-handoff.md; paper/sources/process-log-v1.md;
paper/sources/e1-prereg-frozen.md; paper/sources/e4-prereg-frozen.md. -->
