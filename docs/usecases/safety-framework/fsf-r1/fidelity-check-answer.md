# Part A

I judged these against the quoted source sentences only. I could not check the surrounding Framework text.

## rs2_misuse
- **A1.** Both readings are faithful on actor, act and strength. "Take place only after ... determines ... acceptable" becomes "must not proceed ... unless governance_found_acceptable", and that is right.
  - Both drop the parenthetical "including a safety case where a CCL has been reached". The safety case is part of what the determination consists of.
  - Both drop the "after" ordering and the "appropriate governance function" as actor. These are probably limits of the vocabulary.
  - The `p` scoping (a reached misuse level) is not in the sentence. It comes from the translator's reading of the section.
- **A2.** This is a genuine ambiguity. The words say "external deployments of a model", with no restriction to models at a level, which favours `u`. The parenthetical "where a CCL has been reached" also implies that review applies even when no CCL has been reached. `p` is the reading from section context (the process for models reaching a T/CCL), and a careful reader would accept it.
- **A3.** The line is empty of content ("cannot yet show in words"), but the difference is real. For an external proposal that has reached no misuse level and is not found acceptable, `u` forbids it and `p` does not.
- **Verdict: FAITHFUL WITH NOTE.** The safety-case clause is omitted in both readings.

## rs2_ml_rd
- **A1.** The same as rs2_misuse.
  - The scope "external or high_risk" is encoded as classification "high_risk". The source says "high-risk internal deployments". If a high-risk further-development proposal can carry that classification, the rule catches something the source does not name. This depends on how the vocabulary defines the classification.
  - The safety-case clause is dropped in both readings.
- **A2.** Genuine, for the same reason as rs2_misuse.
- **A3.** The difference is real. A proposal that is external or high-risk, with no ML R&D level reached, is forbidden under `u` and free under `p`.
- **Verdict: FAITHFUL WITH NOTE.** Same two notes as above.

## rs4_elicitation
- **A1.** The `strict` reading is faithful in strength: the source says "must".
  - The `default` reading weakens "must" to "should", which lets a decider find an exception the source does not grant. That is wrong on strength.
  - Both readings generalise "Note on ML R&D CCLs" to "every proposal". They also drop "requiring conservatism in the form of evaluations".
- **A2.** This is not a genuine ambiguity. "Must" is unambiguous, and the same document uses "should" elsewhere, so the distinction is deliberate. A careful reader would not accept `default`.
- **A3.** The line describes a real difference: where the decider applies an exception, `strict` still binds and `default` does not. It also states that the sentence says *must*, which itself shows that `default` is not what the text says.
- **Verdict: UNFAITHFUL** for the `default` reading and for the pair as a genuine ambiguity. `strict` is faithful, with a note about the dropped ML R&D scope.

## rs4_holistic
- **A1.** The `default` reading is faithful on strength, because the source says "should".
  - Mitigations are assessed and are proportionate to expected impact. The source also says the effects of mitigation are assessed, and "thus balancing safety with innovation". Both are dropped, which is acceptable.
  - The source makes the mitigation proportionate. The reading makes the assessment proportionate. This is a slight shift.
  - The `strict` reading raises "should" to "must", which is wrong.
- **A2.** Not a genuine ambiguity, for the same reason as rs4_elicitation. The `strict` reading is not what the text says.
- **A3.** The line is real and accurate. It even says "This sentence says *should*".
- **Verdict: UNFAITHFUL** for `strict`. `default` is faithful with the notes above.

## rs4_within
- **A1.** `default` is faithful on strength ("should"). Both readings add the condition "if there is a level such that that proposal has reached that level". The source says only "as determined by the T/CCLs as relevant". Reading "as relevant" as "only where a level has been reached" is the translator's interpretation, and it is arguably an added condition. The `strict` reading is wrong on strength, as above.
- **A2.** Not a genuine ambiguity.
- **A3.** The line is real, as in rs4_holistic.
- **Verdict: UNFAITHFUL** for `strict`. `default` is faithful with a note about the added reached-level condition.

## rs6_insider
- **A1.** Both readings use "need not", which matches "not required", and both are limited to a reached misuse level.
  - Both drop "At this stage". This temporal qualifier means the statement can be revised.
  - `different` keeps the source's referents: mitigations beyond the baseline controls, against insider misuse.
  - `same` identifies "additional mitigations" with the SL2+ insider-threat measures, and makes the object "apply each measure to the model weights". The source does not say "weights". It also says "insider misuse" while SL2+ addresses "insider threats", which are different risks.
  - `same` releases any measure that "addresses insiders". Baseline controls such as background checks also address insiders, so the rule over-releases. The source only releases measures beyond the established safeguards.
- **A2.** This is a plausible ambiguity. The section is about security levels and "additional ... measures", so a reader could take "additional mitigations" to mean the SL2+ additions. The "insider misuse" wording argues against that.
- **A3.** The difference is real. Under `same`, a reached-misuse proposal is released from applying any insider-addressing measure to the weights. Under `different` it is not. The printed line has no content.
- **Verdict: FAITHFUL WITH NOTE.** `same` is overbroad, and "At this stage" is dropped.

## rs9_bullet3
- **A1.** The `different` reading is faithful:
  - It keeps "severe harm".
  - It keeps the scope "external deployment and high-risk internal deployment" (high-risk is a classification here, so the rs2_ml_rd note applies).
  - It keeps the ML R&D CCL condition.

  The `same` reading deletes "severe". The source wording is "residual risk of severe harm", and the intro distinguishes "significant and severe risks". Bullet 2 says "harm", so bullet 3 is deliberately a different condition.

  In both readings, the source's "We assess that ... mitigations have brought the risk to an acceptable level" is a condition for being "deemed acceptable". The translation recasts it as "must have mitigations make ... acceptable". The bullet-3 scope sentence ("This is required only for...") partly supports that, but it is a recast.
- **A2.** Not a genuine ambiguity of the text. Identifying two differently worded conditions as one act is a modelling decision, not a reading the words allow. A careful reader would not accept `same`.
- **A3.** The line is a raw dump of the whole situation, and the only substantive difference it shows is the word "severe". I also cannot derive from the two displayed rules why p is "not required" under the severe wording, because the rules shown do not release it. Other rules in the situation may account for this, but the line does not make that visible.
- **Verdict: UNFAITHFUL** for `same`. `different` is faithful with the notes above.

# Part B

## C1: F16 against F15
- **B1.** No, they are different acts and different actors.
  - F15 says "additional mitigations beyond these established safeguards are not required". The context is "risks of insider misuse posed by the misuse T/CCLs" and "baseline controls (such as background checks and access restrictions)". The actor is "we", the developer, "at this stage".
  - F16 is SL2+, "additional security measures designed to address risks from insider threats and well-resourced non-state external actors". Via s22-recommend, it is "the minimum appropriate level of security the field of frontier AI should apply".
  - The translation merges these through RS6=same and the predicate "addresses insiders", and through the frame "apply to the model weights".
- **B2.** No, F16 is over-strong.
  - The source says "recommend", and "should apply" attached to "the field of frontier AI". The strict `must` binding the developer (RS3=Ds, strict) is the translator's choice.
  - F15 "not required" is correctly "need not".
- **B3.** Yes, in part.
  - "At this stage" scopes F15.
  - s22-adjusted says the recommended levels "may be adjusted" and gives exceptions: models not meaningfully different from publicly available ones, and open-release benefit. This softens F16 further.
  - "Insider misuse" and "insider threats" are different phrases.
- **B4.** A careful reader might see a mild tension. A recommendation to use SL2+ with insider-threat measures sits beside "additional mitigations ... not required" for insider misuse. They would not see a contradiction, because one is a field recommendation and the other is the developer's current-stage obligation about a different risk.
- **Classification: translation artefact.** The cause is the RS6=same identification of "insider misuse" mitigations with the SL2+ insider-threat measures, combined with strengthening "recommend / should" to `must` for the developer.

## C3: F9 bullet 2 against F10 bullet 3
- **B1.** No, they are different acts.
  - Bullet 2 concerns "residual risk of harm" for a misuse T/CCL, assessed on the effectiveness of mitigations, the scope of the deployment, what is available on other publicly available models, and historical incidence.
  - Bullet 3 concerns "residual risk of severe harm" for an ML R&D CCL, assessed on effectiveness of mitigations, model propensities, and severity of related events.
  - The two bullets sit under different CCL families. The translation collapses them into one predicate by dropping "severe" (RS9=same).
- **B2.** Yes, the strengths match. The source says "required only for ..." in both bullets, so f10 as `must` and f9 as `need not` are fair. The weakness is the object, not the strength.
- **B3.** Yes. Each scope sentence is attached to its own bullet:
  - "This is required only for external deployment, not internal deployment or further development."
  - "This is required only for external deployment and high-risk internal deployment, not further development."

  Bullet 2's "not required for internal" releases only the bullet-2 condition, which concerns misuse risk. It does not release bullet 3's severe-harm condition for the ML R&D CCL. The intro also says the bullets treat "different model risks".
- **B4.** No. A model at both a misuse and an ML R&D CCL, proposed for high-risk internal deployment, owes the bullet-3 assessment for ML R&D. It owes no bullet-2 assessment for misuse. These are separate requirements and do not contradict each other.
- **Classification: translation artefact.** The cause is RS9=same, which merges "harm" and "severe harm" into one act. That lets bullet 2's internal-deployment exemption spill onto bullet 3's requirement.

# Summary

- rs2_misuse: FAITHFUL WITH NOTE
- rs2_ml_rd: FAITHFUL WITH NOTE
- rs4_elicitation: UNFAITHFUL (`default` weakens "must")
- rs4_holistic: UNFAITHFUL (`strict` strengthens "should")
- rs4_within: UNFAITHFUL (`strict` strengthens "should")
- rs6_insider: FAITHFUL WITH NOTE
- rs9_bullet3: UNFAITHFUL (`same` drops "severe")
- C1: translation artefact
- C3: translation artefact
