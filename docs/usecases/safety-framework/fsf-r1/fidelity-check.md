# fsf-r1: independent fidelity check and R14 source check

- **Checker:** a Claude Code subagent on Sonnet 5.5, a different model from the translator and from this item's
  builder (Opus 5.5), run once on 2026-10-18. It read only the two input files below, which hold the source
  sentences, each reading's VE text and VE's separation line. It did not see the rest of the Framework, and it says
  so.
- **Inputs:** [fidelity-input.md](fidelity-input.md) has the seven content-bearing sets.
  [conflicts-input.md](conflicts-input.md) has C1 and C3 with their source passages.
- **Questions:**
  - Part A (fidelity): A1, A2 and A3 for each set.
  - Part B: R14's four questions for each conflict (DRI-RULINGS.md R14).

## The checker's verdicts (verbatim summary lines)

```
- rs2_misuse: FAITHFUL WITH NOTE
- rs2_ml_rd: FAITHFUL WITH NOTE
- rs4_elicitation: UNFAITHFUL (`default` weakens "must")
- rs4_holistic: UNFAITHFUL (`strict` strengthens "should")
- rs4_within: UNFAITHFUL (`strict` strengthens "should")
- rs6_insider: FAITHFUL WITH NOTE
- rs9_bullet3: UNFAITHFUL (`same` drops "severe")
- C1: translation artefact
- C3: translation artefact
```

## What each verdict means here, and what this item does with it

The readings themselves did not change in fsf-r1. Every candidate is the reading's rule of `rules.d1.ve` from Oct 1;
`test_a_set_carries_content_exactly_when_each_reading_is_one_rule_and_that_rule_is_its_content` checks this. So each
verdict is about the Oct 1 translation, now shown to a second model for the first time.

| Item | Checker's reason | Action in fsf-r1 |
|---|---|---|
| rs2_misuse, rs2_ml_rd | Faithful. Both readings drop the parenthetical "including a safety case where a CCL has been reached" and the order "only after". The RS2 = U reading is favoured by the words; RS2 = P comes from the section context. For rs2_ml_rd, "high_risk" may cover more than "high-risk internal deployments" if the classification is not limited to internal ones. | None. The order of events is O7 ("process and deadline wording" in gaps.json). The "high_risk" premise `activities-high-risk` (every high-risk proposal is internal) already limits it. |
| rs6_insider | A plausible ambiguity. "At this stage" is dropped. RS6 = same is overbroad: it releases every measure that addresses insiders, the baseline controls included. | Recorded. RS6 = same feeds only C1, which is a translation artefact (below). |
| rs4_elicitation, rs4_holistic, rs4_within | Not a genuine ambiguity. "Must" says strict and "should" says default, and the document uses both words, so the contrast is deliberate. rs4_within also adds the condition "a level has been reached" for "as relevant". | **Not applied; a finding for the DRI.** The translation follows soft-norms.md 2.2: "In translation any force word (`should`, `must`, `always`, `never`) is a READINGS unit `{strict, default}` unless a cited source unit narrows it". The Oct 1 results review (finding B, PLAN section 12 item 21) required both forces for every "should" and "must". The checker argues in effect that the document's own contrast of the two words is such a narrowing. Applying it would be a plan change: rule 2.2 is general, the pilots use it, and `test_every_should_keeps_its_strict_reading` pins it. So it goes to the DRI as the next item's question (REPORT.md, next items). |
| rs9_bullet3 | RS9 = same deletes "severe": bullet 3 says "residual risk of severe harm" against bullet 2's "harm", deliberately. | **Not applied; a finding.** RS9 = same is the cause of C3 (below). Dropping it changes C3 and C-doc, and the key's C3 answer was written with RS9. That is a translation change against a frozen key, so it goes to the next item with the RS4 question. |
| C1 | Translation artefact. F15 concerns "insider misuse" and F16 concerns "insider threats". RS6 = same merges them. RS3 = Ds with strict force turns "recommend ... the field ... should apply" into the developer's "must". "At this stage" and 2.2's adjustment cases also bear on it. | **Applied: README.** C1 is no longer a finding about the source. It is a conflict between two readings the translation keeps, and its causes are the ones the checker names. |
| C3 | Translation artefact. RS9 = same merges "harm" with "severe harm", and each bullet's "required only for" sentence is attached to its own bullet. | **Applied: README.** As for C1. |

R14 is met: no conflict is presented as a finding about the source. Before this item the README presented C1 and C3
as "Conflicts found" without a source check. That broke R14, which was written after this use case's C1.

## The checker's full answer

The answer is in [fidelity-check-answer.md](fidelity-check-answer.md), as the checker returned it (HTML entities such as `&amp;` decoded). It quotes
single sentences of the source, as the README and PLAN do; the source itself is not committed.
