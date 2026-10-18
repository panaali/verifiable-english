### Set rs2_misuse (unit s212-step2)
Source text:
> 2. Pre-deployment review of residual risk assessment: external deployments of a model take place only after the appropriate governance function determines the residual risk to be acceptable (including a safety case where a CCL has been reached).

Reading `p` (rule f12-p; translator's note: F12, 2.1.2 step 2, within the process for models reaching a misuse T/CCL):
    Rule 1. Every proposal must not proceed, if all of the following hold: (a) that proposal is external; (b) there is a level such that both that proposal has reached that level and that level is misuse, unless that proposal is classified as "governance_found_acceptable".

Reading `u` (rule f12-u; translator's note: F12, 2.1.2 step 2, about every model):
    Rule 1. Every proposal must not proceed, if that proposal is external, unless that proposal is classified as "governance_found_acceptable".

VE's separation line for ['p', 'u']: These two readings differ in a checked situation that VE cannot yet show in words.

### Set rs2_ml_rd (unit s312-step2)
Source text:
> 2. Pre-deployment review of residual risk assessment: external deployments and high-risk internal deployments of a model take place only after the appropriate governance function determines the residual risk to be acceptable (including a safety case where a CCL has been reached).

Reading `p` (rule f13-p; translator's note: F13, 3.1.2 step 2, within the process for models reaching an ML R&D and misalignment T/CCL):
    Rule 1. Every proposal must not proceed, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that both that proposal has reached that level and that level is classified as "ml_rd_and_misalignment", unless that proposal is classified as "governance_found_acceptable".

Reading `u` (rule f13-u; translator's note: F13, 3.1.2 step 2, about every model):
    Rule 1. Every proposal must not proceed, if either that proposal is external or that proposal is classified as "high_risk", or both, unless that proposal is classified as "governance_found_acceptable".

VE's separation line for ['p', 'u']: These two readings differ in a checked situation that VE cannot yet show in words.

### Set rs4_elicitation (unit note-ml-rd-must)
Source text:
> Note on Machine Learning R&D CCLs: Risk assessment must take into account the fact that other actors may put significantly more effort into eliciting capabilities than we put into assessing risk, thus requiring conservatism in the form of evaluations.

Reading `default` (rule f20-elicitation-default; translator's note: F20, Note on ML R&D CCLs, read as a default norm):
    Rule 1. Every proposal should have its risk assessment consider greater elicitation effort by others.

Reading `strict` (rule f20-elicitation-strict; translator's note: F20, Note on ML R&D CCLs "Risk assessment must take into account the fact that other actors may put significantly more effort into eliciting capabilities"):
    Rule 1. Every proposal must have its risk assessment consider greater elicitation effort by others.

VE's separation line for ['strict', 'default']: This sentence says *must*. (1) *Every proposal must have its risk assessment consider greater elicitation effort by others.* (2) *Every proposal should have its risk assessment consider greater elicitation effort by others.* They differ here: suppose the decider decides the exception applies to p. Under (1) p still must. Under (2) p is not required to. It is not certified that these two readings differ only where the decider decides that the exception applies.

### Set rs4_holistic (unit s135-holistic)
Source text:
> The mitigation and the effects of such mitigation should also be assessed holistically and be proportionate with expected impact of a model’s risk, thus balancing safety with innovation.

Reading `default` (rule f20-holistic-default; translator's note: F20, 1.3.5 Note, read as a default norm):
    Rule 1. Every proposal should have its mitigations assessed holistically in proportion to expected impact.

Reading `strict` (rule f20-holistic-strict; translator's note: F20, 1.3.5 Note "should also be assessed holistically and be proportionate with expected impact"):
    Rule 1. Every proposal must have its mitigations assessed holistically in proportion to expected impact.

VE's separation line for ['strict', 'default']: This sentence says *should*. (1) *Every proposal must have its mitigations assessed holistically in proportion to expected impact.* (2) *Every proposal should have its mitigations assessed holistically in proportion to expected impact.* They differ here: suppose the decider decides the exception applies to p. Under (1) p still must. Under (2) p is not required to. It is not certified that these two readings differ only where the decider decides that the exception applies.

### Set rs4_within (unit g-within)
Source text:
> The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as relevant.

Reading `default` (rule f20-within-default; translator's note: F20, Glossary, read as a default norm):
    Rule 1. Every proposal should have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.

Reading `strict` (rule f20-within-strict; translator's note: F20, Glossary "The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as relevant"):
    Rule 1. Every proposal must have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.

VE's separation line for ['strict', 'default']: This sentence says *should*. (1) *Every proposal must have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.* (2) *Every proposal should have its residual risk brought within the acceptable levels, if there is a level such that that proposal has reached that level.* They differ here: suppose the decider decides the exception applies to p. Under (1) p still must. Under (2) p is not required to. It is not certified that these two readings differ only where the decider decides that the exception applies.

### Set rs6_insider (unit s22-insider-not-required)
Source text:
> At this stage, additional mitigations beyond these established safeguards are not required.

Reading `different` (rule f15-diff; translator's note: F15, 2.2: insider misuse is not insider threat to weights):
    Rule 1. Every proposal need not add mitigations against insider misuse beyond the baseline controls, if there is a level such that both that proposal has reached that level and that level is misuse.

Reading `same` (rule f15-same; translator's note: F15, 2.2 "additional mitigations beyond these established safeguards are not required"; RS6 same: the SL2+ insider-threat measures):
    Rule 1. Every proposal need not apply each measure to the model weights, if all of the following hold: (a) there is a level such that both that proposal has reached that level and that level is misuse; (b) that measure addresses insiders.

VE's separation line for ['same', 'different']: These two readings differ in a checked situation that VE cannot yet show in words.

### Set rs9_bullet3 (unit s135-bullet3-dm)
Source text:
> ○ We assess that the deployment mitigations have brought the residual risk of severe harm to an acceptable level, based on considerations such as the effectiveness of mitigations, and information pertaining to model propensities and the severity of related events. 5

Reading `different` (rule f10-dm-diff; translator's note: F10, 1.3.5 bullet 3, DM-s as a gate):
    Rule 1. Every proposal must have mitigations make the residual risk of severe harm acceptable, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that all of the following hold: (i) that proposal has reached that level; (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment".

Reading `same` (rule f10-dm-same; translator's note: F10, 1.3.5 bullet 3, DM as a gate; RS9 same: one act with bullet 2):
    Rule 1. Every proposal must have mitigations make the residual risk of harm acceptable, if all of the following hold: (a) either that proposal is external or that proposal is classified as "high_risk", or both; (b) there is a level such that all of the following hold: (i) that proposal has reached that level; (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment".

VE's separation line for ['same', 'different']: These two readings differ here: cbrn is a domain; cyber is a domain; harmful_manipulation is a domain; ml_rd_and_misalignment_domain is a domain; cbrn_uplift_level_1 is a level; cbrn_uplift_tcl is a level; cyber_uplift_level_1 is a level; harmful_manipulation_level_1 is a level; ml_rd_acceleration_level_1 is a level; ml_rd_automation_level_1 is a level; stealth_and_situational_awareness_tcl is a level; insider_threat_measures is a measure; security_level_2_plus is a measure; security_level_3 is a measure; security_level_4 is a measure; p is a proposal; insiders is a threat; insider_threat_measures addresses insiders; cbrn_uplift_level_1 concerns cbrn; cbrn_uplift_tcl concerns cbrn; cyber_uplift_level_1 concerns cyber; harmful_manipulation_level_1 concerns harmful_manipulation; ml_rd_acceleration_level_1 concerns ml_rd_and_misalignment_domain; ml_rd_automation_level_1 concerns ml_rd_and_misalignment_domain; stealth_and_situational_awareness_tcl concerns ml_rd_and_misalignment_domain; cbrn_uplift_level_1 is critical; cyber_uplift_level_1 is critical; harmful_manipulation_level_1 is critical; ml_rd_acceleration_level_1 is critical; ml_rd_automation_level_1 is critical; p is classified as "high_risk"; security_level_2_plus includes insider_threat_measures; p is internal; cbrn_uplift_level_1 is misuse; cbrn_uplift_tcl is misuse; cyber_uplift_level_1 is misuse; harmful_manipulation_level_1 is misuse; ml_rd_acceleration_level_1 is classified as "ml_rd_and_misalignment"; ml_rd_automation_level_1 is classified as "ml_rd_and_misalignment"; stealth_and_situational_awareness_tcl is classified as "ml_rd_and_misalignment"; p has reached ml_rd_acceleration_level_1; cbrn_uplift_level_1 recommends security_level_2_plus; cyber_uplift_level_1 recommends security_level_2_plus; harmful_manipulation_level_1 recommends security_level_2_plus; ml_rd_acceleration_level_1 recommends security_level_3; ml_rd_automation_level_1 recommends security_level_4; cbrn_uplift_tcl is tracked; stealth_and_situational_awareness_tcl is tracked. Under *Every proposal must have mitigations make the residual risk of harm acceptable, if all of the following hold:
  (a) either that proposal is external or that proposal is classified as "high_risk", or both;
  (b) there is a level such that all of the following hold:
    (i) that proposal has reached that level;
    (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment"*, p still must. Under *Every proposal must have mitigations make the residual risk of severe harm acceptable, if all of the following hold:
  (a) either that proposal is external or that proposal is classified as "high_risk", or both;
  (b) there is a level such that all of the following hold:
    (i) that proposal has reached that level;
    (ii) both that level is critical and that level is classified as "ml_rd_and_misalignment"*, p is not required to.
