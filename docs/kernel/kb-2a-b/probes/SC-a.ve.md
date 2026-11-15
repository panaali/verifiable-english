---
{
 "format": "ve-document@1",
 "environment": {
  "language": "ve.core@0.2",
  "profiles": [
   "norms@0",
   "readings@1",
   "relational-fol@0",
   "scope@0",
   "soft-norms@0"
  ],
  "spec_revision": "ve-v0.2-expand2-2026-09-25",
  "vocabulary": {
   "sorts": {
    "proposal": {
     "description": "a proposed activity for a model at one moment: further development, an internal or external deployment, or a step of the framework's own process. Every rule speaks about every proposal"
    },
    "level": {
     "description": "a capability level named by the framework (a Tracked or a Critical Capability Level)"
    },
    "domain": {
     "description": "a risk domain named by the framework"
    },
    "measure": {
     "description": "a security level, or a named group of security measures, that the framework recommends"
    },
    "threat": {
     "description": "a source of risk that a security measure addresses"
    }
   },
   "predicates": {
    "critical": {
     "arguments": [
      "level"
     ],
     "description": "{0} is a Critical Capability Level (CCL): absent mitigation, a model at it may pose heightened risk of severe harm (Glossary)",
     "verbalisation": "{0} is critical"
    },
    "tracked": {
     "arguments": [
      "level"
     ],
     "description": "{0} is a Tracked Capability Level (TCL): absent mitigation, a model at it may pose heightened risk of significant but not severe harm (Glossary)",
     "verbalisation": "{0} is tracked"
    },
    "concerns": {
     "arguments": [
      "level",
      "domain"
     ],
     "description": "{0} is a level of the risk domain {1} (the section that defines it)",
     "verbalisation": "{0} concerns {1}"
    },
    "misuse": {
     "arguments": [
      "level"
     ],
     "description": "{0} is a misuse T/CCL: a level of the CBRN, cyber or harmful manipulation domains (1.2, Section 2)",
     "verbalisation": "{0} is misuse"
    },
    "ml_rd_and_misalignment": {
     "arguments": [
      "level"
     ],
     "description": "{0} is an ML R&D and misalignment T/CCL (1.2, Section 3)"
    },
    "recommends": {
     "arguments": [
      "level",
      "measure"
     ],
     "description": "the framework recommends {1} for models reaching {0} (tables 2.2.1.a to 3.2.2.a)",
     "verbalisation": "{0} recommends {1}"
    },
    "includes": {
     "arguments": [
      "measure",
      "measure"
     ],
     "description": "{0} includes {1} (2.1.1: Security Level 2+ adds measures to RAND SL2)",
     "verbalisation": "{0} includes {1}"
    },
    "addresses": {
     "arguments": [
      "measure",
      "threat"
     ],
     "description": "{0} is designed to address risks from {1} (2.1.1)",
     "verbalisation": "{0} addresses {1}"
    },
    "reached": {
     "arguments": [
      "proposal",
      "level"
     ],
     "description": "the model of {0} has reached {1}, as the critical capability assessment found. Open term OT1, decided by the developer (\"we\", 1.3.2)",
     "verbalisation": "{0} has reached {1}"
    },
    "approaches": {
     "arguments": [
      "proposal",
      "level"
     ],
     "description": "the model of {0} has reached an alert threshold for {1}. Open term OT1, decided by the developer (\"we\", 1.3.2)",
     "verbalisation": "{0} approaches {1}"
    },
    "at_least_as_strong": {
     "arguments": [
      "measure",
      "measure"
     ],
     "description": "{0} is at least as strong as {1}. The text states no such order (footnotes 12 and 13 say only \"may include\"); the vocabulary has the word so that question S4 can be asked"
    },
    "applies": {
     "arguments": [
      "proposal",
      "measure"
     ],
     "description": "security mitigations reaching {1} have been applied to the model weights of {0}",
     "verbalisation": "{0} applies {1}"
    },
    "further_development": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is further development of the model"
    },
    "internal": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is an internal deployment: a release restricted to Google employees for internal use",
     "verbalisation": "{0} is internal"
    },
    "high_risk": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is a high-risk internal deployment: for use cases with the potential to enable severe threat scenarios. Open term OT7, decided by no one the text names (unstated)"
    },
    "external": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is an external deployment: a model release to entities outside Google",
     "verbalisation": "{0} is external"
    },
    "low_risk": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is a low-risk external deployment: a small scale and private release restricted to particular external groups. Open term OT8, decided by no one the text names (unstated)"
    },
    "first_deployment": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is the first external deployment of a new model"
    },
    "frontier": {
     "arguments": [
      "proposal"
     ],
     "description": "the model of {0} is a frontier AI model (Glossary definition). Open term OT9, decided by no one the text names (unstated)",
     "verbalisation": "{0} is frontier"
    },
    "subsequent": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is an external deployment of a subsequent version of a model",
     "verbalisation": "{0} is subsequent"
    },
    "new_capabilities": {
     "arguments": [
      "proposal"
     ],
     "description": "the model of {0} has meaningful new capabilities or material increases in performance. Open term OT10, decided by the developer (\"we\")"
    },
    "could_undermine_justification": {
     "arguments": [
      "proposal"
     ],
     "description": "the capability increase of {0} could materially undermine the justification for why its risks are acceptable. Open term OT10, decided by the developer (\"we believe\")"
    },
    "post_training_run_completed": {
     "arguments": [
      "proposal"
     ],
     "description": "a post-training run of the model of {0} has completed"
    },
    "material_safety_case_update": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} is a material update to a safety case"
    },
    "mitigates": {
     "arguments": [
      "proposal",
      "level"
     ],
     "description": "the deployment mitigations of {0} have brought the residual risk from {1} (of harm, of severe harm or of significant harm, as the bullet for {1} says) to an acceptable level. Open term OT2, decided by the developer (\"We assess\", 1.3.5)",
     "verbalisation": "{0} mitigates {1}"
    },
    "unlikely_misalignment_propensities": {
     "arguments": [
      "proposal"
     ],
     "description": "the model of {0} is very unlikely to possess the propensities that would be required for material risk of significant harm through misalignment risk. Open term OT6, decided by the developer (\"we assess\")"
    },
    "security_assessed_adequate": {
     "arguments": [
      "proposal"
     ],
     "description": "the level of security applied to the model weights of {0} is assessed adequate. Open term OT4, decided by the developer (\"we otherwise assess\")"
    },
    "open_release_benefits_outweigh_risks": {
     "arguments": [
      "proposal"
     ],
     "description": "the benefits of the open release of the model weights of {0} outweigh the risks. Open term OT5, decided by the developer (\"we assess\")"
    },
    "like_public_models": {
     "arguments": [
      "proposal"
     ],
     "description": "the model of {0} does not possess capabilities meaningfully different from other publicly available models that have weaker security applied. Open term OT16, decided by the developer (2.2)"
    },
    "governance_found_acceptable_with_safety_case_where_ccl_reached": {
     "arguments": [
      "proposal"
     ],
     "description": "the appropriate governance function has determined the residual risk of {0} to be acceptable, including a safety case where the model of {0} has reached a CCL (footnote 4, 2.1.2 and 3.1.2 step 2: \"including (with) a safety case where a CCL has been reached\"); a determination without that safety case at a CCL is not this finding. Open term OT3, decided by the appropriate governance function (unnamed)"
    },
    "internal_risk_unacceptable_without_safeguards": {
     "arguments": [
      "proposal"
     ],
     "description": "the risk assessment deems the residual risk of {0} from internal deployment unacceptable without additional safeguards. Decided by the developer's periodic risk assessment (3.2.1)"
    },
    "unmitigated_public_safety_risk": {
     "arguments": [
      "proposal"
     ],
     "description": "the CCL that the model of {0} has reached poses an unmitigated and material risk to overall public safety. Open term OT11, decided by the developer (\"we assess\", 5.2)"
    },
    "sharing_facilitates_safety": {
     "arguments": [
      "proposal"
     ],
     "description": "sharing information about {0} with government authorities will facilitate safety of frontier AI. Open term OT11, decided by the developer (5.2)"
    },
    "adherence_undermined": {
     "arguments": [
      "proposal"
     ],
     "description": "at {0} there are reasonable grounds to believe the adequacy of the Framework or the adherence to it has been materially undermined. Open term OT13, decided by the developer (\"we have reasonable grounds to believe\", 5.1)"
    },
    "circumvention_evidence": {
     "arguments": [
      "proposal"
     ],
     "description": "post-market monitoring of {0} shows that safeguards are being circumvented (a stipulated situation for gap G8; no rule mentions it)"
    },
    "assessed": {
     "arguments": [
      "proposal"
     ],
     "description": "a critical capability assessment (CCA) of the model takes place before {0} (1.3.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be preceded by a critical capability assessment"
     }
    },
    "modification_checked": {
     "arguments": [
      "proposal"
     ],
     "description": "before {0}, the developer determines whether a substantial modification has been made (1.3.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be preceded by a determination of any substantial modification"
     }
    },
    "further_need_checked": {
     "arguments": [
      "proposal"
     ],
     "description": "before {0}, the developer determines whether a further critical capability assessment is required (1.3.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be preceded by a determination of any further capability assessment needed"
     }
    },
    "further_assessed": {
     "arguments": [
      "proposal"
     ],
     "description": "a further CCA takes place before {0} (1.3.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be preceded by a further critical capability assessment"
     }
    },
    "change_assessed": {
     "arguments": [
      "proposal"
     ],
     "description": "material capability change assessments on various checkpoints follow {0} (1.3.2); the checkpoints are part of the act, not a situation variable",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be followed by material capability change assessments on various checkpoints"
     }
    },
    "proximity_assessed": {
     "arguments": [
      "proposal",
      "level"
     ],
     "description": "the proximity of the model of {0} to {1} is assessed and the risk posed is analysed, involving internal and external experts as needed (1.3.3 \"we will assess the proximity of the model to the CCL and analyze the risk posed, involving internal and external experts as needed\"); \"as needed\" qualifies the experts' involvement, which is part of the act, not the assessment and the analysis",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be followed by an assessment of proximity to {1} with a risk analysis"
     }
    },
    "residual_assessed": {
     "arguments": [
      "proposal"
     ],
     "description": "the model of {0} is subject to residual risk assessments as part of evaluating its deployment mitigations (1.3.4 \"Models reaching TCLs or CCLs will be subject to residual risk assessments as part of evaluating their deployment mitigations\")",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be subject to residual risk assessments in evaluating deployment mitigations"
     }
    },
    "safety_case": {
     "arguments": [
      "proposal"
     ],
     "description": "the residual risk assessment for {0} is informed by a supplemental safety case (1.3.4)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have its residual risk assessment informed by a safety case"
     }
    },
    "periodic_assessed": {
     "arguments": [
      "proposal"
     ],
     "description": "periodic residual risk assessments of the misalignment risk posed are carried out for {0} (3.2.1)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be subject to periodic residual risk assessments of misalignment risk"
     }
    },
    "periodic_covers_internal": {
     "arguments": [
      "proposal"
     ],
     "description": "the periodic residual risk assessments for {0} also account for the safety implications of high-risk internal deployments (3.2.1)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have its periodic assessments cover high-risk internal deployments"
     }
    },
    "safeguards_added": {
     "arguments": [
      "proposal"
     ],
     "description": "the additional safeguards the risk assessment calls for are applied to {0} (3.2.1)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have the additional safeguards applied"
     }
    },
    "harm_mitigated": {
     "arguments": [
      "proposal"
     ],
     "description": "DM-h: the deployment mitigations of {0} bring the residual risk of harm to an acceptable level (1.3.5 bullet 2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have mitigations make the residual risk of harm acceptable"
     }
    },
    "severe_harm_mitigated": {
     "arguments": [
      "proposal"
     ],
     "description": "DM-s: as DM-h, for the residual risk of severe harm (1.3.5 bullet 3)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have mitigations make the residual risk of severe harm acceptable"
     }
    },
    "significant_harm_mitigated": {
     "arguments": [
      "proposal"
     ],
     "description": "DM-g: as DM-h, for the residual risk of significant harm (1.3.5 bullet 4)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have mitigations make the residual risk of significant harm acceptable"
     }
    },
    "secured": {
     "arguments": [
      "proposal"
     ],
     "description": "SEC: security mitigations reaching the recommended security level have been applied to the model weights of {0} (1.3.5 bullets 2 and 3)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have security mitigations that reach the recommended security level"
     }
    },
    "adequately_secured": {
     "arguments": [
      "proposal"
     ],
     "description": "SEC-t: the level of security applied to the model weights of {0} is assessed adequate (1.3.5 bullet 4)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have a level of security assessed as adequate"
     }
    },
    "proceed": {
     "arguments": [
      "proposal"
     ],
     "description": "{0} may take place",
     "regulated": {
      "role": "permission",
      "default": "deny",
      "act": "{0} proceed"
     }
    },
    "acceptable": {
     "arguments": [
      "proposal"
     ],
     "verbalisation": "{0} is acceptable",
     "description": "{0} is deemed to pose an acceptable level of (residual) risk (1.3.5): a classification, never a permission to proceed",
     "regulated": {
      "role": "plain",
      "default": "deny"
     }
    },
    "case_submitted": {
     "arguments": [
      "proposal"
     ],
     "description": "the material update {0} to a safety case is submitted to the appropriate governance function (2.1.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be submitted to review by the appropriate governance function"
     }
    },
    "insider_mitigations_added": {
     "arguments": [
      "proposal"
     ],
     "description": "mitigations against insider misuse beyond the established baseline safeguards are added for {0} (2.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} add mitigations against insider misuse beyond the baseline controls"
     }
    },
    "applied": {
     "arguments": [
      "proposal",
      "measure"
     ],
     "description": "{1} is applied to the model weights of {0} (2.1.1, 2.2, 3.2.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} apply {1} to the model weights"
     }
    },
    "yearly_review": {
     "arguments": [
      "proposal"
     ],
     "description": "the framework is reviewed at least once a year, at the time of {0} (5.1)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be covered by a review of the framework at least once a year"
     }
    },
    "frequent_review": {
     "arguments": [
      "proposal"
     ],
     "description": "the framework is reviewed more often than yearly, at the time of {0} (5.1)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} be covered by a more frequent review of the framework"
     }
    },
    "shared": {
     "arguments": [
      "proposal"
     ],
     "description": "relevant information about the model of {0} is shared with appropriate government authorities (5.2)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} share relevant information with appropriate government authorities"
     }
    },
    "holistic": {
     "arguments": [
      "proposal"
     ],
     "description": "the mitigation for {0} and the effects of such mitigation are assessed holistically, and the mitigation and its effects are both proportionate with the expected impact of the model's risk (1.3.5 Note \"The mitigation and the effects of such mitigation should also be assessed holistically and be proportionate with expected impact of a model's risk\": one subject, the mitigation and its effects, with both demands)",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have holistically assessed mitigations proportionate with expected impact"
     }
    },
    "within_levels": {
     "arguments": [
      "proposal"
     ],
     "description": "the residual risk of {0} is brought within the acceptable levels, as determined by the T/CCLs as relevant (Glossary, Residual Risk Assessments: \"The residual risk should be brought within the acceptable levels, as determined by the T/CCLs as relevant\")",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have its residual risk brought within the acceptable levels"
     }
    },
    "elicitation_considered": {
     "arguments": [
      "proposal"
     ],
     "description": "the risk assessment for {0} takes into account the fact that other actors may put significantly more effort into eliciting capabilities than the developer puts into assessing risk, and its evaluations are conservative accordingly (Note on ML R&D CCLs \"Risk assessment must take into account the fact that other actors may put significantly more effort into eliciting capabilities than we put into assessing risk, thus requiring conservatism in the form of evaluations\")",
     "regulated": {
      "role": "obligation",
      "default": "deny",
      "act": "{0} have its risk assessment conservatively weigh greater elicitation by others"
     }
    }
   },
   "constants": {
    "cbrn_uplift_tcl": {
     "sort": "level",
     "description": "L1: CBRN uplift TCL (2.2.1)"
    },
    "cbrn_uplift_level_1": {
     "sort": "level",
     "description": "L2: CBRN uplift level 1 (table 2.2.1.a)"
    },
    "cyber_uplift_level_1": {
     "sort": "level",
     "description": "L3: Cyber uplift level 1 (table 2.2.2.a)"
    },
    "harmful_manipulation_level_1": {
     "sort": "level",
     "description": "L4: Harmful manipulation level 1 (exploratory) (table 2.2.3.a)"
    },
    "stealth_and_situational_awareness_tcl": {
     "sort": "level",
     "description": "L5: Stealth and Situational Awareness TCL (3.2.1)"
    },
    "ml_rd_acceleration_level_1": {
     "sort": "level",
     "description": "L6: ML R&D acceleration level 1 (table 3.2.2.a)"
    },
    "ml_rd_automation_level_1": {
     "sort": "level",
     "description": "L7: ML R&D automation level 1 (table 3.2.2.a)"
    },
    "cbrn": {
     "sort": "domain",
     "description": "CBRN: chemical, biological, radiological or nuclear threats (1.2)"
    },
    "cyber": {
     "sort": "domain",
     "description": "Cyber (1.2)"
    },
    "harmful_manipulation": {
     "sort": "domain",
     "description": "Harmful Manipulation (1.2)"
    },
    "ml_rd_and_misalignment_domain": {
     "sort": "domain",
     "description": "ML R&D and Misalignment (Glossary, Risk Domains)"
    },
    "security_level_2_plus": {
     "sort": "measure",
     "description": "Security Level 2+ (2.1.1): RAND SL2 with additional measures"
    },
    "security_level_3": {
     "sort": "measure",
     "description": "Security level 3 (table 3.2.2.a), generally aligned with RAND SL3 (footnote 6)"
    },
    "security_level_4": {
     "sort": "measure",
     "description": "Security level 4 (table 3.2.2.a), generally aligned with RAND SL4 (footnote 6)"
    },
    "rand_security_level_2": {
     "sort": "measure",
     "description": "RAND Security Level 2 (SL2), the baseline of Security Level 2+ (2.1.1)"
    },
    "sl2_plus_additional_measures": {
     "sort": "measure",
     "description": "the additional security measures of Security Level 2+, designed to address risks from insider threats and well-resourced non-state external actors (2.1.1)"
    },
    "insiders": {
     "sort": "threat",
     "description": "insider threats (2.1.1)"
    },
    "well_resourced_non_state_external_actors": {
     "sort": "threat",
     "description": "well-resourced non-state external actors (2.1.1)"
    }
   }
  }
 },
 "units": [
  {
   "id": "s135-bullet2-dm",
   "kind": "norm",
   "meaning": {
    "open": [
     "ot2_residual_risk_acceptable"
    ]
   },
   "support": "testimony",
   "content": {
    "norm": {
     "guard": [
      "and",
      [
       "unary",
       "external",
       [
        "var",
        0
       ]
      ],
      [
       "exists",
       "level",
       [
        "and",
        [
         "binary",
         "reached",
         [
          "var",
          1
         ],
         [
          "var",
          0
         ]
        ],
        [
         "unary",
         "misuse",
         [
          "var",
          0
         ]
        ]
       ]
      ]
     ],
     "name": "f9-dm",
     "over": [],
     "predicate": "harm_mitigated",
     "sign": true,
     "unless": []
    }
   },
   "span": [
    0,
    490
   ]
  },
  {
   "id": "s135-bullet2-only",
   "kind": "norm",
   "meaning": "specified",
   "support": "testimony",
   "span": [
    490,
    585
   ]
  }
 ],
 "open_terms": [
  {
   "name": "ot2_residual_risk_acceptable",
   "arguments": [],
   "decided_by": "developer",
   "necessary": [],
   "sufficient": [],
   "factors": [
    "the deployment mitigations have brought the residual risk to an acceptable level (1.3.5)",
    "the effectiveness of mitigations",
    "the scope of the deployment",
    "capabilities and mitigations of other publicly available models",
    "the historical incidence and severity of related events"
   ],
   "precedents": [],
   "jurisdiction": "fsf_v3_1",
   "version": 1
  }
 ],
 "scope": {
  "version": "scope@0",
  "governors": [
   {
    "id": "g1",
    "unit": "s135-bullet2-only",
    "reach": {
     "rules": [
      "f9-dm"
     ]
    },
    "units": [
     "s135-bullet2-dm"
    ],
    "effect": {
     "reguard": [
      "and",
      "own",
      [
       "unary",
       "external",
       [
        "var",
        0
       ]
      ]
     ]
    }
   }
  ]
 },
 "reading_sets": [
  {
   "id": "rs8_bullet2",
   "unit": "s135-bullet2-only",
   "version": 1,
   "status": "open",
   "readings": [
    {
     "id": "scope",
     "kind": "norm",
     "meaning_id": "pending",
     "content": null,
     "admission": {
      "who": "translator",
      "why": "RS8 = scope",
      "distinguishing_models": {
       "rel": "2d33048abfa36ee723426c8fa4543c57fc0552d7c83b45aa8a596e16cf89cc2c"
      }
     }
    },
    {
     "id": "rel",
     "kind": "norm",
     "meaning_id": "pending",
     "content": null,
     "admission": {
      "who": "translator",
      "why": "RS8 = rel",
      "distinguishing_models": {
       "scope": "2d33048abfa36ee723426c8fa4543c57fc0552d7c83b45aa8a596e16cf89cc2c"
      }
     }
    }
   ],
   "models": {
    "2d33048abfa36ee723426c8fa4543c57fc0552d7c83b45aa8a596e16cf89cc2c": {
     "complete": true,
     "domains": {
      "domain": [
       "cbrn",
       "cyber",
       "harmful_manipulation",
       "ml_rd_and_misalignment_domain"
      ],
      "level": [
       "cbrn_uplift_level_1",
       "cbrn_uplift_tcl",
       "cyber_uplift_level_1",
       "harmful_manipulation_level_1",
       "ml_rd_acceleration_level_1",
       "ml_rd_automation_level_1",
       "stealth_and_situational_awareness_tcl"
      ],
      "measure": [
       "rand_security_level_2",
       "security_level_2_plus",
       "security_level_3",
       "security_level_4",
       "sl2_plus_additional_measures"
      ],
      "proposal": [
       "p"
      ],
      "threat": [
       "insiders",
       "well_resourced_non_state_external_actors"
      ]
     },
     "constants": {
      "cbrn": "cbrn",
      "cbrn_uplift_level_1": "cbrn_uplift_level_1",
      "cbrn_uplift_tcl": "cbrn_uplift_tcl",
      "cyber": "cyber",
      "cyber_uplift_level_1": "cyber_uplift_level_1",
      "harmful_manipulation": "harmful_manipulation",
      "harmful_manipulation_level_1": "harmful_manipulation_level_1",
      "insiders": "insiders",
      "ml_rd_acceleration_level_1": "ml_rd_acceleration_level_1",
      "ml_rd_and_misalignment_domain": "ml_rd_and_misalignment_domain",
      "ml_rd_automation_level_1": "ml_rd_automation_level_1",
      "rand_security_level_2": "rand_security_level_2",
      "security_level_2_plus": "security_level_2_plus",
      "security_level_3": "security_level_3",
      "security_level_4": "security_level_4",
      "sl2_plus_additional_measures": "sl2_plus_additional_measures",
      "stealth_and_situational_awareness_tcl": "stealth_and_situational_awareness_tcl",
      "well_resourced_non_state_external_actors": "well_resourced_non_state_external_actors"
     },
     "relations": {
      "acceptable": [],
      "addresses": [
       [
        "sl2_plus_additional_measures",
        "insiders"
       ],
       [
        "sl2_plus_additional_measures",
        "well_resourced_non_state_external_actors"
       ]
      ],
      "adequately_secured": [],
      "adherence_undermined": [],
      "applied": [],
      "applies": [],
      "approaches": [],
      "assessed": [],
      "at_least_as_strong": [],
      "case_submitted": [],
      "change_assessed": [],
      "circumvention_evidence": [],
      "concerns": [
       [
        "cbrn_uplift_level_1",
        "cbrn"
       ],
       [
        "cbrn_uplift_tcl",
        "cbrn"
       ],
       [
        "cyber_uplift_level_1",
        "cyber"
       ],
       [
        "harmful_manipulation_level_1",
        "harmful_manipulation"
       ],
       [
        "ml_rd_acceleration_level_1",
        "ml_rd_and_misalignment_domain"
       ],
       [
        "ml_rd_automation_level_1",
        "ml_rd_and_misalignment_domain"
       ],
       [
        "stealth_and_situational_awareness_tcl",
        "ml_rd_and_misalignment_domain"
       ]
      ],
      "could_undermine_justification": [],
      "critical": [
       [
        "cbrn_uplift_level_1"
       ],
       [
        "cyber_uplift_level_1"
       ],
       [
        "harmful_manipulation_level_1"
       ],
       [
        "ml_rd_acceleration_level_1"
       ],
       [
        "ml_rd_automation_level_1"
       ]
      ],
      "elicitation_considered": [],
      "external": [],
      "first_deployment": [],
      "frequent_review": [],
      "frontier": [],
      "further_assessed": [],
      "further_development": [],
      "further_need_checked": [],
      "governance_found_acceptable_with_safety_case_where_ccl_reached": [],
      "harm_mitigated": [],
      "high_risk": [],
      "holistic": [],
      "includes": [
       [
        "security_level_2_plus",
        "rand_security_level_2"
       ],
       [
        "security_level_2_plus",
        "sl2_plus_additional_measures"
       ]
      ],
      "insider_mitigations_added": [],
      "internal": [
       [
        "p"
       ]
      ],
      "internal_risk_unacceptable_without_safeguards": [],
      "like_public_models": [],
      "low_risk": [],
      "material_safety_case_update": [],
      "misuse": [
       [
        "cbrn_uplift_level_1"
       ],
       [
        "cbrn_uplift_tcl"
       ],
       [
        "cyber_uplift_level_1"
       ],
       [
        "harmful_manipulation_level_1"
       ]
      ],
      "mitigates": [],
      "ml_rd_and_misalignment": [
       [
        "ml_rd_acceleration_level_1"
       ],
       [
        "ml_rd_automation_level_1"
       ],
       [
        "stealth_and_situational_awareness_tcl"
       ]
      ],
      "modification_checked": [],
      "new_capabilities": [],
      "open_release_benefits_outweigh_risks": [],
      "periodic_assessed": [],
      "periodic_covers_internal": [],
      "post_training_run_completed": [],
      "proceed": [],
      "proximity_assessed": [],
      "reached": [
       [
        "p",
        "cbrn_uplift_level_1"
       ]
      ],
      "recommends": [
       [
        "cbrn_uplift_level_1",
        "security_level_2_plus"
       ],
       [
        "cyber_uplift_level_1",
        "security_level_2_plus"
       ],
       [
        "harmful_manipulation_level_1",
        "security_level_2_plus"
       ],
       [
        "ml_rd_acceleration_level_1",
        "security_level_3"
       ],
       [
        "ml_rd_automation_level_1",
        "security_level_4"
       ]
      ],
      "residual_assessed": [],
      "safeguards_added": [],
      "safety_case": [],
      "secured": [],
      "security_assessed_adequate": [],
      "severe_harm_mitigated": [],
      "shared": [],
      "sharing_facilitates_safety": [],
      "significant_harm_mitigated": [],
      "subsequent": [],
      "tracked": [
       [
        "cbrn_uplift_tcl"
       ],
       [
        "stealth_and_situational_awareness_tcl"
       ]
      ],
      "unlikely_misalignment_propensities": [],
      "unmitigated_public_safety_risk": [],
      "within_levels": [],
      "yearly_review": []
     }
    }
   }
  }
 ]
}
---
○ We assess that the deployment mitigations have brought the residual risk of harm to an acceptable level, based on considerations such as the effectiveness of mitigations, the scope of the deployment, what capabilities and mitigations are available on other publicly available models (e.g. if other models are similarly capable and have few mitigations, then the marginal risk added by our external deployment is likely low), and the historical incidence and severity of related events. This is required only for external deployment, not internal deployment or further development. 