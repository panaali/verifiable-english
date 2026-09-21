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
