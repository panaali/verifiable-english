# Experimental design and development calibration

All scored outcomes in this section are pending in the evidence frozen for this
draft. Development pilots may guide calibration but cannot supply held-out view
effects. E1 and E5 documents are draft preregistrations with remaining decisions,
not completed preregistrations. The current paper does not authorize scored runs.
<!-- src: paper/sources/e1-prereg-draft.md; paper/sources/e5-prereg-draft.md. -->

## Shared estimands and safeguards

False approval is approved bad submissions divided by assigned bad submissions.
Honest acceptance is approved good submissions divided by assigned good
submissions. Failures, timeouts, tool use, and unparseable verdicts stay in the
assigned denominator, scored adversely for each label, and are also reported
separately. A system that rejects everything cannot establish useful oversight.
Paired conditions share candidates. Splits separate semantic templates and
vocabulary families; repeated variants remain within template clusters.

Before scoring, commit the item recipe, primary contrast, useful-effect threshold,
honest-acceptance constraint, sample assignment, judge settings, resource budgets,
and uncertainty rule. All attempts and deviations must remain visible. A confidence
interval spanning the useful-effect boundary is inconclusive about that effect.
Judge families are analyzed separately. Actual input and output tokens, view
lengths, and renderer versions must be recorded. Different CLI context overheads
are a potential confound; historical estimates changed, so the scored run must
measure its own context rather than reuse an earlier estimate.
<!-- src: PLAN.md, Plan v2 decisions; PROTOCOL.md; paper/sources/e1-prereg-draft.md;
paper/sources/e5-prereg-draft.md. -->

## E1: specification sign-off

E1 asks whether a model judge rejects an unfaithful formalization more reliably
from VE than from equally deterministic FOL. Each candidate is crossed with the
available views and with either no explanation or an attacker-authored
explanation. The requirement, candidate AST, vocabulary legend, and underlying
checker are held fixed. This separates presentation from adding verification
only to a VE condition.

Mechanical attacks change quantifiers, conjuncts, argument order, implication,
exceptions, or existence conditions. Model-generated attacks come from both
author families and are produced before the judging condition is known. Good
candidates include meaning-preserving rewrites so that any textual change does
not identify the label. Semantic difference must be witnessed, and directional
claims require the oracle evidence described in Section 4. Difference alone
does not prove that the original reference faithfully expressed its prose.

The primary contrast is VE strict minus symbolic FOL false approval in the
attacker-explanation cells. Keyword FOL controls for replacing symbols with
words. Natural and fluent comparisons are secondary. E1b removes the requirement
and asks for satisfaction predictions in small finite models before feedback.
Its purpose is to distinguish comprehension from a shift toward rejection.

| Draft E1 design parameter | Recorded plan |
|---|---|
| Scored base items | 96, from 12 templates and 8 vocabularies |
| Presentation crossing | 5 views by 2 explanation conditions |
| Primary-judge capability gap | Accuracy at least 5 percentage points below the strong-model mean |
| Primary-judge calibration | Raw-FOL false approval 30--60%; honest acceptance at least 70% |
| Secondary near-floor band | False approval at least 10% and below 30% |
| Useful false-approval reduction | 5 percentage points |
| Honest-acceptance constraint | At most 5-point loss by the draft's point-estimate rule; at least 70% absolute |
| Planned primary interval | 95% percentile bootstrap over 12 template clusters; 10,000 resamples |

<!-- src: paper/sources/e1-prereg-draft.md, Materials, Gate, Primary contrast,
Honest-acceptance constraint. Boundary notation in prose: near-floor is [0.10,0.30). -->

Two draft issues must be resolved before confirmatory interpretation. The E1
benefit rule combines an interval below zero with a point estimate beyond the
useful-effect threshold; this can declare benefit even when the interval spans
that threshold, contrary to the project-wide rule. The draft also excludes
validation-UNKNOWN candidates before judging. Any such exclusion must appear as
validation attrition with the full generated denominator and uncertainty bounds,
not as evidence that excluded candidates were wrong. Neither issue is silently
repaired by this paper.
<!-- src: PLAN.md, Plan v2 decision 6 and oracle status rule;
paper/sources/e1-prereg-draft.md, Oracle and Refutation condition. -->

**[RESULT-E1-FREEZE: final preregistration, judge roster, assignments, validation
attrition, power assessment, and deviations not yet available.]**

**[RESULT-E1: scored paired false approval and honest acceptance by judge, with
template intervals and length covariates, not yet available.]**

**[RESULT-E1B: scored model-satisfaction accuracy by judge and view not yet run
in the evidence frozen here.]**

## Judge ladders: DEV-PILOT only

The ladder uses symbolic FOL with no explanation. Its nominal candidates are
correlated variants of a small development set:

| DEV-PILOT inventory | Count |
|---|---:|
| Base items / templates | 16 / 4 |
| Attacked / faithful candidates | 109 / 48 |
| Total candidates | 157 |

<!-- src: paper/sources/local-ladder.md; paper/sources/e1-pilot-dev.md. -->

<!-- INCLUDE generated/judge-local-table.md -->

<!-- INCLUDE generated/judge-colab-table.md -->

![DEV-PILOT calibration only. False approval includes adverse scoring of failures. Panels separate local MLX, Colab, and hosted settings; labels identify quantization or forced verdicts. The shaded interval is the E1 false-approval gate, not a confidence band.](figures/judge-ladder.pdf){width=95%}
<!-- src: paper/sources/local-ladder.md; paper/sources/colab-ladder.json;
paper/sources/e1-pilot-dev.md; generated by figures/gen_judge_ladder.py. -->

Small hosted models are near the false-approval floor in this pilot. The tested
small open models largely approve both good and attacked claims; forced verdicts
remove formatting failures without making those tested rungs discriminative.
The first measured useful rung is near the seven-billion-parameter class, not a
universal parameter threshold. The Colab Qwen rungs in the primary band come
from one model family. Llama's low false approval accompanies low honest
acceptance; Gemma mostly approves; Phi has substantial response failures.
The larger Qwen rung is below the primary calibration band.
<!-- src: paper/sources/local-ladder.md; paper/sources/colab-ladder.json.
Seven-billion phrase refers to named 7B model rows, not inferred scaling law. -->

Serving stacks and quantization differ. Local and Colab rates are separate
observations, not replicated estimates under identical conditions. The Colab
summary was supplied outside the repository and is now committed for provenance;
this drafting pass did not reproduce those model calls. No row establishes a VE
presentation benefit. The absence of a qualifying second family also limits the
draft E1 requirement for a cross-family benefit claim.

## E5: proof-label harm and grounding

E5 holds logical validity fixed while varying grounding and its display. The
primary contrast is false approval with a truthful conditional-proof badge minus
false approval without it, on bad-grounding, valid-deduction items. Grounding
labels come from explicit records and scopes, not model opinions. Families cover
merged vocabulary, unsupported leaves, scope mismatch, and stale evidence.
Invalid-edge controls are separate from this primary endpoint.

| Cell | Display intervention |
|---|---|
| a | Argument and records |
| b | a plus truthful conditional-proof badge |
| c | b plus remaining leaf obligations and raw scopes |
| d | c plus predicate-use references into the same records |
| e | d plus supplied and declared sense tags |

The revised materials remove mechanical mismatch flags. Honest tags and forged
tags must be reported separately, and stale evidence remains a separate family.
The panels change organization and length as well as visibility; their effects
are whole-interface effects, not pure comprehension effects.

| Draft E5 parameter | Recorded plan |
|---|---|
| Generated inventory | 3,072 items: 768 dev, 2,304 scored |
| Structural templates | 8 dev, 24 scored |
| Difficulty / instruction factors | 3 construction levels, 2 styles |
| Primary gate | Cell-a false approval 15--85%; honest acceptance above 50%; response adherence at least 90% |
| Useful-size effect | Provisional 12 percentage points |
| Protective honest-acceptance rule | Lower interval bound for the contrast at least -5 percentage points |
| Planned interval | Equal-weight template-cluster t interval, 95% |

<!-- src: paper/sources/e5-prereg-draft.md, revision 3.
These are generated inventory/planned analysis counts, not judged sample sizes. -->

The lowest difficulty satisfying the development gate is selected before scoring.
Power remains a placeholder until paired trials calibrate cluster variance.
A prior development pilot on superseded materials moved a hosted judge away
from the floor; it is not a pilot of the revised inventory. The revision therefore
requires fresh calibration.

The structural-shortcut episode is a methods warning. Earlier material balanced
counts and lexical inventories, yet an uncited dossier that matched no cited
dossier identified bad cases. The revision constructs uncited copies after the
label-changing swap and audits the full equality/duplication signature. Chance
accuracy for those audited features does not bound richer classifiers or prove
that semantic reasoning is required. Development-versus-scored n-gram probes,
record-position checks, and semantic label checks must all survive the final
freeze. Section 10 records the defect and its limited resolution.
<!-- src: paper/sources/e5-prereg-draft.md; paper/sources/review-e5.md;
paper/sources/process-log-excerpts.md. -->

**[RESULT-E5-FREEZE: revised dev calibration, power, judge/difficulty/style
selection, final leak audit, and committed scoring amendment not yet available.]**

**[RESULT-E5: scored badge and panel effects, honest acceptance, failures,
forged-tag and stale-evidence breakdowns not yet available.]**

## E2 and E4: bounded mechanism tests

E2 varies derivation size while comparing direct review with a checked display.
A structured-FOL arm receives the same checker result. Errors outside the
checker's reach, such as a false leaf or wrong specification, must remain in the
design. A constant-size checked prompt does not by itself demonstrate scalable
oversight; premise difficulty and total authoring/checking cost also matter.

E4 compares prose criticism with countermodel presentations, including dishonest
critics who assert unchecked countermodels. A checked countermodel already
settles formal invalidity. Any advantage attributable to that check must not be
credited to English. These remain mechanism demonstrations unless matched
baselines and sufficient template variation support a stronger conclusion.

| Plan-v2 mechanism parameter | Planned value |
|---|---|
| E2 derivation sizes | 4, 32, 256 steps |
| E2 errors outside checker visibility | Half of error items |
| E4 controls | Invalid inferences and dishonest countermodel assertions |

<!-- src: PLAN.md, Plan v2 decision 4; design/critique-claude.md;
design/critique-codex.md; paper/sources/review-e5.md.
Later revisions need an explicit scored freeze; no current efficacy estimate. -->

**[RESULT-E2: final materials/freeze and scored accuracy, honest acceptance,
failures, and total costs by size not yet available.]**

**[RESULT-E4: final materials/freeze and scored critique effects, including
dishonest critics and matched checking baselines, not yet available.]**
