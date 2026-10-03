---
{
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "documents@1",
      "norms@0",
      "relational-fol@0",
      "rights@0",
      "soft-norms@0"
    ],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
      "constants": {},
      "predicates": {
        "arises_from_acts_contrary_to_un": {
          "arguments": [
            "prosecution"
          ],
          "description": "The prosecution genuinely arises from acts contrary to the purposes and principles of the United Nations"
        },
        "arises_from_non_political_crime": {
          "arguments": [
            "prosecution"
          ],
          "description": "The prosecution genuinely arises from a non-political crime"
        },
        "asylum_right_covers_case": {
          "arguments": [
            "prosecution"
          ],
          "description": "The right to seek and to enjoy asylum (Article 14, paragraph 1) may be invoked in the case of the prosecution"
        },
        "avoid_assembly_and_association_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person freedom of peaceful assembly as well as association. Source clause: the right to freedom of peaceful assembly and association.",
          "regulated": {
            "act": "{0} avoid denying {1} freedom of peaceful assembly as well as association",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_leave_and_return_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from leaving any country as well as returning to their own. Source clause: the right to leave any country, including the person's own, and to return to the person's country.",
          "regulated": {
            "act": "{0} avoid barring {1} from leaving any country as well as returning to their own",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_liberty_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid depriving the person of liberty. Source clause: the right to liberty.",
          "regulated": {
            "act": "{0} avoid depriving {1} of liberty",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_life_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid depriving the person of life. Source clause: the right to life.",
          "regulated": {
            "act": "{0} avoid depriving {1} of life",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_movement_and_residence_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person freedom of movement as well as residence within each state. Source clause: the right to freedom of movement and residence within the borders of each state.",
          "regulated": {
            "act": "{0} avoid denying {1} freedom of movement as well as residence within each state",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_opinion_and_expression_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person freedom of opinion as well as expression. Source clause: the right to freedom of opinion and expression.",
          "regulated": {
            "act": "{0} avoid denying {1} freedom of opinion as well as expression",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_property_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from owning property alone as well as jointly with others. Source clause: the right to own property alone as well as in association with others.",
          "regulated": {
            "act": "{0} avoid barring {1} from owning property alone as well as jointly with others",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_security_of_person_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid endangering the security of the person of the person. Source clause: the right to security of person.",
          "regulated": {
            "act": "{0} avoid endangering the security of the person of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_thought_conscience_religion_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person freedom of thought conscience as well as religion. Source clause: the right to freedom of thought, conscience and religion.",
          "regulated": {
            "act": "{0} avoid denying {1} freedom of thought conscience as well as religion",
            "default": "deny",
            "role": "obligation"
          }
        },
        "compel_association_membership_permitted": {
          "arguments": [
            "actor",
            "person"
          ],
          "description": "The actor is permitted to compel the person to belong to an association",
          "regulated": {
            "act": "{0} compel {1} to belong to an association",
            "default": "allow",
            "role": "permission"
          }
        },
        "declaration_implies_destructive_right": {
          "arguments": [
            "bearer"
          ],
          "description": "This Declaration implies for the bearer a right to engage in any activity or to perform any act aimed at the destruction of any of the rights and freedoms set forth in it"
        },
        "exercise_contrary_to_un": {
          "arguments": [
            "exercise"
          ],
          "description": "The exercise is contrary to the purposes and principles of the United Nations"
        },
        "is_state": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is a state",
          "verbalisation": "{0} is a state"
        },
        "person_may_assembly_and_association": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to enjoy freedom of peaceful assembly as well as association. Source clause: the right to freedom of peaceful assembly and association.",
          "regulated": {
            "act": "{0} enjoy freedom of peaceful assembly as well as association",
            "default": "deny",
            "role": "permission"
          }
        },
        "person_may_leave_and_return": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to leave any country as well as return to their own country. Source clause: the right to leave any country, including the person's own, and to return to the person's country.",
          "regulated": {
            "act": "{0} leave any country as well as return to their own country",
            "default": "deny",
            "role": "permission"
          }
        },
        "person_may_movement_and_residence": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to move as well as reside within the borders of each state. Source clause: the right to freedom of movement and residence within the borders of each state.",
          "regulated": {
            "act": "{0} move as well as reside within the borders of each state",
            "default": "deny",
            "role": "permission"
          }
        },
        "person_may_opinion_and_expression": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to enjoy freedom of opinion as well as expression. Source clause: the right to freedom of opinion and expression.",
          "regulated": {
            "act": "{0} enjoy freedom of opinion as well as expression",
            "default": "deny",
            "role": "permission"
          }
        },
        "person_may_property": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to own property alone as well as in association with others. Source clause: the right to own property alone as well as in association with others.",
          "regulated": {
            "act": "{0} own property alone as well as in association with others",
            "default": "deny",
            "role": "permission"
          }
        },
        "person_may_thought_conscience_religion": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to enjoy freedom of thought conscience as well as religion. Source clause: the right to freedom of thought, conscience and religion.",
          "regulated": {
            "act": "{0} enjoy freedom of thought conscience as well as religion",
            "default": "deny",
            "role": "permission"
          }
        },
        "right_protects_exercise": {
          "arguments": [
            "exercise"
          ],
          "description": "The right or freedom protects the exercise"
        },
        "secure_assembly_and_association_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person freedom of peaceful assembly as well as association. Source clause: the right to freedom of peaceful assembly and association.",
          "regulated": {
            "act": "{0} secure {1} freedom of peaceful assembly as well as association",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_equal_protection_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to give the person equal protection of the law without any discrimination. Source clause: to be entitled without any discrimination to equal protection of the law.",
          "regulated": {
            "act": "{0} give {1} equal protection of the law without any discrimination",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_liberty_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the liberty of the person. Source clause: the right to liberty.",
          "regulated": {
            "act": "{0} secure the liberty of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_life_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the life of the person. Source clause: the right to life.",
          "regulated": {
            "act": "{0} protect the life of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_movement_and_residence_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person freedom of movement as well as residence within each state. Source clause: the right to freedom of movement and residence within the borders of each state.",
          "regulated": {
            "act": "{0} secure {1} freedom of movement as well as residence within each state",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_opinion_and_expression_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person freedom of opinion as well as expression. Source clause: the right to freedom of opinion and expression.",
          "regulated": {
            "act": "{0} secure {1} freedom of opinion as well as expression",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_property_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the ownership of property by the person alone as well as with others. Source clause: the right to own property alone as well as in association with others.",
          "regulated": {
            "act": "{0} secure the ownership of property by {1} alone as well as with others",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_protection_against_discrimination_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the person equally against discrimination in violation of this Declaration. Source clause: to be entitled to equal protection against any discrimination in violation of this Declaration.",
          "regulated": {
            "act": "{0} protect {1} equally against discrimination in violation of this Declaration",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_protection_against_incitement_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the person equally against incitement to such discrimination. Source clause: to be entitled to equal protection against any incitement to such discrimination.",
          "regulated": {
            "act": "{0} protect {1} equally against incitement to such discrimination",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_protection_against_interference_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the person by law against such interference as well as attacks. Source clause: the right to the protection of the law against arbitrary interference with privacy, family, home or correspondence and against attacks upon honour and reputation.",
          "regulated": {
            "act": "{0} protect {1} by law against such interference as well as attacks",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_recognition_as_person_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to recognise the person everywhere as a person before the law. Source clause: the right to recognition everywhere as a person before the law.",
          "regulated": {
            "act": "{0} recognise {1} everywhere as a person before the law",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_security_of_person_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to safeguard the security of the person of the person. Source clause: the right to security of person.",
          "regulated": {
            "act": "{0} safeguard the security of the person of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_thought_conscience_religion_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person freedom of thought conscience as well as religion. Source clause: the right to freedom of thought, conscience and religion.",
          "regulated": {
            "act": "{0} secure {1} freedom of thought conscience as well as religion",
            "default": "deny",
            "role": "obligation"
          }
        }
      },
      "rights": {
        "alters": {},
        "bearers": [
          "bearer"
        ],
        "holders": [
          "person"
        ],
        "protected": []
      },
      "sorts": {
        "actor": {
          "description": "a person, group, or institution capable of compelling a person",
          "verbalisation": {
            "plural": "actors",
            "singular": "actor"
          }
        },
        "bearer": {
          "description": "a State, group or person",
          "verbalisation": {
            "plural": "bearers",
            "singular": "bearer"
          }
        },
        "exercise": {
          "description": "one exercise of a right or freedom by a person on one occasion",
          "verbalisation": {
            "plural": "exercises",
            "singular": "exercise"
          }
        },
        "person": {
          "description": "a human person",
          "verbalisation": {
            "plural": "people",
            "singular": "person"
          }
        },
        "prosecution": {
          "description": "a prosecution of a person",
          "verbalisation": {
            "plural": "prosecutions",
            "singular": "prosecution"
          }
        }
      }
    }
  },
  "format": "ve-document@1",
  "open_terms": [
    {
      "arguments": [
        "person"
      ],
      "decided_by": "unstated",
      "factors": [
        "equal legal standing",
        "equal legal protection",
        "scope of comparators"
      ],
      "jurisdiction": "universal",
      "name": "equal_before_law",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "meaning of dignity",
        "scope of inherence"
      ],
      "jurisdiction": "universal",
      "name": "inherent_dignity",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which rights",
        "conditions on transfer or loss"
      ],
      "jurisdiction": "universal",
      "name": "inalienable_rights",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "essential for which end",
        "degree of necessity"
      ],
      "jurisdiction": "universal",
      "name": "essential",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "comparison class",
        "measure of importance"
      ],
      "jurisdiction": "universal",
      "name": "greatest_importance",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "meaning of natural",
        "meaning of fundamental",
        "what counts as family"
      ],
      "jurisdiction": "universal",
      "name": "natural_group_unit",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "legality",
        "reasonableness",
        "procedural safeguards"
      ],
      "jurisdiction": "universal",
      "name": "arbitrary",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "procedural fairness",
        "public access",
        "independence"
      ],
      "jurisdiction": "universal",
      "name": "fair",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "health needs",
        "living conditions",
        "resources"
      ],
      "jurisdiction": "universal",
      "name": "adequate",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "fairness criteria",
        "comparison group"
      ],
      "jurisdiction": "universal",
      "name": "just",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "hours",
        "work setting",
        "health and rest"
      ],
      "jurisdiction": "universal",
      "name": "reasonable",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "authenticity of election or prosecution",
        "procedural evidence"
      ],
      "jurisdiction": "universal",
      "name": "genuine",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "reciprocal conduct",
        "meaning of brotherhood"
      ],
      "jurisdiction": "universal",
      "name": "spirit_of_brotherhood",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "meaning of justice in the Preamble",
        "scope of the claimed foundation"
      ],
      "jurisdiction": "universal",
      "name": "justice",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which purposes and principles count",
        "what makes an act contrary to them"
      ],
      "jurisdiction": "universal",
      "name": "contrary_to_un_purposes_and_principles",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what separates a political from a non-political crime",
        "who classifies the crime"
      ],
      "jurisdiction": "universal",
      "name": "non_political_crime",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which items of the Declaration count as rights and freedoms"
      ],
      "jurisdiction": "universal",
      "name": "rights_and_freedoms_set_forth",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what it is to aim at the destruction of a right",
        "whether purpose or effect decides"
      ],
      "jurisdiction": "universal",
      "name": "aimed_at_destruction_of_rights",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as discrimination",
        "which distinctions are meant"
      ],
      "jurisdiction": "universal",
      "name": "discrimination",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes protection equal",
        "the comparators"
      ],
      "jurisdiction": "universal",
      "name": "equal_protection_of_the_law",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes a remedy effective"
      ],
      "jurisdiction": "universal",
      "name": "effective",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which national tribunals are competent"
      ],
      "jurisdiction": "universal",
      "name": "competent",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which rights the constitution or law grants",
        "which of them are fundamental"
      ],
      "jurisdiction": "universal",
      "name": "fundamental_rights_granted",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes a tribunal independent",
        "what makes a tribunal impartial"
      ],
      "jurisdiction": "universal",
      "name": "independent_and_impartial",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which guarantees are necessary for a defence"
      ],
      "jurisdiction": "universal",
      "name": "guarantees_necessary_for_defence",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as persecution",
        "whether persecution that is only threatened counts"
      ],
      "jurisdiction": "universal",
      "name": "persecution",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "who the comparators are for equality of the hearing",
        "what full equality requires"
      ],
      "jurisdiction": "universal",
      "name": "full_equality",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what it is for a limitation to be determined by law"
      ],
      "jurisdiction": "universal",
      "name": "determined_by_law",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what due recognition and respect for the rights and freedoms of others requires"
      ],
      "jurisdiction": "universal",
      "name": "due_recognition_and_respect",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which requirements are just"
      ],
      "jurisdiction": "universal",
      "name": "just_requirements",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "whose morality",
        "which requirements of morality"
      ],
      "jurisdiction": "universal",
      "name": "morality",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as public order"
      ],
      "jurisdiction": "universal",
      "name": "public_order",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as the general welfare"
      ],
      "jurisdiction": "universal",
      "name": "general_welfare",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes a society democratic"
      ],
      "jurisdiction": "universal",
      "name": "democratic_society",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as protection of the family",
        "what society owes as distinct from the State"
      ],
      "jurisdiction": "universal",
      "name": "protection_of_the_family",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which duties the community may require",
        "who decides"
      ],
      "jurisdiction": "universal",
      "name": "duties_to_the_community",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as free and full development of a personality"
      ],
      "jurisdiction": "universal",
      "name": "free_and_full_development",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    }
  ],
  "reading_sets": [
    {
      "id": "rs_u022a",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid depriving each holder of life (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-life-by-state",
                    "over": [],
                    "predicate": "avoid_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "life"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "3510b5cd52f5f167d19d309542737f1cdff7880ecc80cec7615851e3006fd1b2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect the life of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-life-by-state",
                    "over": [],
                    "predicate": "secure_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "life"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "3d2b57f5d13506113d64a2e46bec7a634bcea7a7c5a044fcfbcc4e5e3dfbe025"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid depriving each holder of life (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-life-by-anyone",
                    "over": [],
                    "predicate": "avoid_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "life"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "b0ee9554691261b6518d115aee51f438265e3d09cdb93a66c87913bd89340b03"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect the life of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-life-by-anyone",
                    "over": [],
                    "predicate": "secure_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "life"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "570cf11a735e67d906a04903a8f7ab0a7ecbcdcfa0982c3d70f8b97b3e2ae934"
        }
      ],
      "status": "open",
      "unit": "u022a",
      "version": 1
    },
    {
      "id": "rs_u022b",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid depriving each holder of liberty (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-liberty-by-state",
                    "over": [],
                    "predicate": "avoid_liberty_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "liberty"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "a54411993ab9e39db87706706065480c3f93107fc8e49d88aaf0b0e9e5d85f4c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure the liberty of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-liberty-by-state",
                    "over": [],
                    "predicate": "secure_liberty_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "liberty"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "a3f4851887f5629e0bd42d13e1b0295208aad845721b786a27db7c14a8efef4f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid depriving each holder of liberty (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-liberty-by-anyone",
                    "over": [],
                    "predicate": "avoid_liberty_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "liberty"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "89d7e1cafeb5dfd64fe6660a3fa2cde0e23e74b76d97f20cf0c7aeed1700baee"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure the liberty of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-liberty-by-anyone",
                    "over": [],
                    "predicate": "secure_liberty_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "liberty"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "a61bbe5dc053f9daa9b7935277907ef71991d82e0fd2e4af22a6487f943c3906"
        }
      ],
      "status": "open",
      "unit": "u022b",
      "version": 1
    },
    {
      "id": "rs_u022c",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid endangering the security of the person of each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-security-of-person-by-state",
                    "over": [],
                    "predicate": "avoid_security_of_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "security-of-person"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "0780f407bcdde92abe41d927b5a04b5a2a8e40f78e8ebfafda96226567430f26"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must safeguard the security of the person of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-security-of-person-by-state",
                    "over": [],
                    "predicate": "secure_security_of_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "security-of-person"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "d3855e3e762fcd38fe154dcd91818aa68c32a4b5a275ad9a2dd93395293ecf56"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid endangering the security of the person of each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-security-of-person-by-anyone",
                    "over": [],
                    "predicate": "avoid_security_of_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "security-of-person"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "ebef8c8f7c19e28d613bafe6729582d9fe79361f20b23f876b5c4985b9e01db5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must safeguard the security of the person of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-security-of-person-by-anyone",
                    "over": [],
                    "predicate": "secure_security_of_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "security-of-person"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "effbae43aa6957017f3f6f104b25135e59fbe46a5e8c0d580b92e9755ad92028"
        }
      ],
      "status": "open",
      "unit": "u022c",
      "version": 1
    },
    {
      "id": "rs_u029",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must recognise each holder everywhere as a person before the law (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-recognition-as-a-person-by-state",
                    "over": [],
                    "predicate": "secure_recognition_as_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "recognition-as-a-person"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "4d494d4e0e6a2d67013307042dc5530ec102f3ca9b70a0ca9c715e90c32cb643"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must recognise each holder everywhere as a person before the law (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-recognition-as-a-person-by-anyone",
                    "over": [],
                    "predicate": "secure_recognition_as_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "recognition-as-a-person"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "3da931e7bdf62bb9e099b40aa662ae8ae68e9f31b1eb2c99fb92cf77f16e821c"
        }
      ],
      "status": "open",
      "unit": "u029",
      "version": 1
    },
    {
      "id": "rs_u032",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder equal protection of the law without any discrimination (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-equal-protection-of-the-law-by-state",
                    "over": [],
                    "predicate": "secure_equal_protection_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-protection-of-the-law"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "78ce2f258f5c29dd759941e2e9f35e1f3943fa7286c7819492c91ed1aac3dfeb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder equal protection of the law without any discrimination (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-equal-protection-of-the-law-by-anyone",
                    "over": [],
                    "predicate": "secure_equal_protection_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-protection-of-the-law"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "521619477428c653fd1e65c621d5da0b6ddff5b0caedba8d2e930a6b5fa5eaf5"
        }
      ],
      "status": "open",
      "unit": "u032",
      "version": 1
    },
    {
      "id": "rs_u033a",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder equally against discrimination in violation of this Declaration (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-protection-against-discrimination-by-state",
                    "over": [],
                    "predicate": "secure_protection_against_discrimination_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-discrimination"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "c9b598d83819b4af58e5290cd10d5c08271d47e0e9dffa231e707a5e0e30401d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder equally against discrimination in violation of this Declaration (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-protection-against-discrimination-by-anyone",
                    "over": [],
                    "predicate": "secure_protection_against_discrimination_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-discrimination"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "07b5bb8763c3eb31bc255bf919912400f9ec8ef980c25e8f94bb6b1071f23fa8"
        }
      ],
      "status": "open",
      "unit": "u033a",
      "version": 1
    },
    {
      "id": "rs_u033b",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder equally against incitement to such discrimination (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-protection-against-incitement-by-state",
                    "over": [],
                    "predicate": "secure_protection_against_incitement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-incitement"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "eabd35b71ea6e79851b7150e432187aeeccc2c58982d4fbf7089ee91b0b90189"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder equally against incitement to such discrimination (the right's one duty; the source names no bearer, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-protection-against-incitement-by-anyone",
                    "over": [],
                    "predicate": "secure_protection_against_incitement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-incitement"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "e5c1ce0d8a776266e3d7e520d3602cf5732618187b08ddd46395d55d544dd485"
        }
      ],
      "status": "open",
      "unit": "u033b",
      "version": 1
    },
    {
      "id": "rs_u046",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder by law against such interference as well as attacks (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'such interference or attacks' keeps the source's anaphor: it is read as the arbitrary interference with privacy, family, home or correspondence (u045a) and the attacks upon honour and reputation (u045b), not a checked reference; 'or' is worded 'as well as' (protection against each)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-protection-of-the-law-against-interference-by-state",
                    "over": [],
                    "predicate": "secure_protection_against_interference_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-of-the-law-against-interference"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "030c54239ecc46d628fc701e289688b141743cb00842cdae6c957aa14e2e1d15"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder by law against such interference as well as attacks (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'such interference or attacks' keeps the source's anaphor: it is read as the arbitrary interference with privacy, family, home or correspondence (u045a) and the attacks upon honour and reputation (u045b), not a checked reference; 'or' is worded 'as well as' (protection against each)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-protection-of-the-law-against-interference-by-anyone",
                    "over": [],
                    "predicate": "secure_protection_against_interference_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-of-the-law-against-interference"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "46ba185431adc5fa97dff7b69ba620ed305958222bb7986a3d7592104df63cac"
        }
      ],
      "status": "open",
      "unit": "u046",
      "version": 1
    },
    {
      "id": "rs_u048",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of movement as well as residence within each state (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'the borders of' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-freedom-of-movement-and-residence-by-state",
                    "over": [],
                    "predicate": "avoid_movement_and_residence_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-movement-and-residence"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "19c81e7604f39a1784bd0a9e50401ebadd925d685178dcc89d57b3c46a9e9b09"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of movement as well as residence within each state (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'the borders of' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-freedom-of-movement-and-residence-by-state",
                    "over": [],
                    "predicate": "secure_movement_and_residence_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-movement-and-residence"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "48bb00f1fdcc06d1e902fe39a7bcefc17c89f68ec9abf0bd5da9fecd4d84f61f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of movement as well as residence within each state (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'the borders of' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-freedom-of-movement-and-residence-by-anyone",
                    "over": [],
                    "predicate": "avoid_movement_and_residence_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-movement-and-residence"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "728d465d57abea3ef51df1c2302199f6d966bca12b0278ee860bd44b570e70a7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of movement as well as residence within each state (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'the borders of' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-freedom-of-movement-and-residence-by-anyone",
                    "over": [],
                    "predicate": "secure_movement_and_residence_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-movement-and-residence"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "5a825124a60a85ae41012a169bb0ee5f2fcf7ed2d57d8ddb74cf05065ab68538"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may move as well as reside within the borders of each state (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-freedom-of-movement-and-residence",
                    "over": [],
                    "predicate": "person_may_movement_and_residence",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-movement-and-residence"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "fd19a16bc654ab75b810e8c5aee930a6dc286ea26f468db7a0cd71e597d4d4fa"
        }
      ],
      "status": "open",
      "unit": "u048",
      "version": 1
    },
    {
      "id": "rs_u049",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from leaving any country as well as returning to their own (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'including his own'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-freedom-to-leave-and-return-by-state",
                    "over": [],
                    "predicate": "avoid_leave_and_return_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-to-leave-and-return"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "b9a6f41fa7b1225710177f2ec3398d9886d30f6b1cce23f7a1f5c39471caa688"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from leaving any country as well as returning to their own (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'including his own'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-freedom-to-leave-and-return-by-anyone",
                    "over": [],
                    "predicate": "avoid_leave_and_return_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-to-leave-and-return"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "62c0aa2efe951eeb85d3cfe9f33042a4c3899e543ce2cb7b7899d8e9e2773da1"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_claim": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may leave any country as well as return to their own country (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-freedom-to-leave-and-return",
                    "over": [],
                    "predicate": "person_may_leave_and_return",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-to-leave-and-return"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "53e376798353966a986844487389f265bcd94615fdc3d3f19da3a77a2cab2d90"
        }
      ],
      "status": "open",
      "unit": "u049",
      "version": 1
    },
    {
      "id": "rs_u063",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from owning property alone as well as jointly with others (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'jointly with others' and 'with others' stand for 'in association with others' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-ownership-of-property-by-state",
                    "over": [],
                    "predicate": "avoid_property_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "ownership-of-property"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "d77b2d70478686d11d2555c6f22a42acfc542ca0c905fe0e751182acec954f09"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure the ownership of property by each holder alone as well as with others (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'jointly with others' and 'with others' stand for 'in association with others' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-ownership-of-property-by-state",
                    "over": [],
                    "predicate": "secure_property_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "ownership-of-property"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "c57faf8762ba55c3532c13156f16567fb49ac3ad68b603212b1ee57cd135fd09"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from owning property alone as well as jointly with others (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'jointly with others' and 'with others' stand for 'in association with others' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-ownership-of-property-by-anyone",
                    "over": [],
                    "predicate": "avoid_property_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "ownership-of-property"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "5d96f49d9a6c158a6d08c393928af09f1075cd0cb2ca29f998de096c1ec79a0e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure the ownership of property by each holder alone as well as with others (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'jointly with others' and 'with others' stand for 'in association with others' in the two duties."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-ownership-of-property-by-anyone",
                    "over": [],
                    "predicate": "secure_property_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "ownership-of-property"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "daae8af05cec9aca2b5101b7dc5cffd19d9dba24bad3e90063602383cea86e61"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may own property alone as well as in association with others (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-ownership-of-property",
                    "over": [],
                    "predicate": "person_may_property",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "ownership-of-property"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "f5e044a9ed70a4ab4c012511106c8ed8599410caf7ffec11a187d1fbed72c33c"
        }
      ],
      "status": "open",
      "unit": "u063",
      "version": 1
    },
    {
      "id": "rs_u066",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of thought conscience as well as religion (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-freedom-of-thought-conscience-and-religion-by-state",
                    "over": [],
                    "predicate": "avoid_thought_conscience_religion_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-thought-conscience-and-religion"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "84210c93aa66d34bb00bcfe315639e0c8093b6e738bbfc86198647f72ce944f9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of thought conscience as well as religion (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-freedom-of-thought-conscience-and-religion-by-state",
                    "over": [],
                    "predicate": "secure_thought_conscience_religion_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-thought-conscience-and-religion"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "3fccb659c13a69d930515fc18b5e45b84aecf792af05b1d640559ca44832c3c7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of thought conscience as well as religion (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-freedom-of-thought-conscience-and-religion-by-anyone",
                    "over": [],
                    "predicate": "avoid_thought_conscience_religion_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-thought-conscience-and-religion"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "5c1b24b470cb440b35be4b5673182b8c09079456b4e5afbd03a1dbac6e3a30f5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of thought conscience as well as religion (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-freedom-of-thought-conscience-and-religion-by-anyone",
                    "over": [],
                    "predicate": "secure_thought_conscience_religion_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-thought-conscience-and-religion"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "70f69b107a5509467699d38f402fb90af40cf7a2869e51085835994f6cde5aa4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may enjoy freedom of thought conscience as well as religion (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-freedom-of-thought-conscience-and-religion",
                    "over": [],
                    "predicate": "person_may_thought_conscience_religion",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-thought-conscience-and-religion"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "1c8ac468a64f93ffd86caba55e30fc9cf0f4069c04792b19fdd791926a65e50c"
        }
      ],
      "status": "open",
      "unit": "u066",
      "version": 1
    },
    {
      "id": "rs_u070",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of opinion as well as expression (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-freedom-of-opinion-and-expression-by-state",
                    "over": [],
                    "predicate": "avoid_opinion_and_expression_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-opinion-and-expression"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "d582d7eb5d0136757b8f7a952464d74e9da7d17723542f3e01adcdc6c74872cc"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of opinion as well as expression (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-freedom-of-opinion-and-expression-by-state",
                    "over": [],
                    "predicate": "secure_opinion_and_expression_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-opinion-and-expression"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "c01dce087248cedbe3f563f3cff8a2c68ce7bb399d7bbb0291e7e85bae8e13e5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of opinion as well as expression (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-freedom-of-opinion-and-expression-by-anyone",
                    "over": [],
                    "predicate": "avoid_opinion_and_expression_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-opinion-and-expression"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "4d4a354ecc44dc3d8de6623ccd0179f40772c464bc219ce34e8154c10746e64b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of opinion as well as expression (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-freedom-of-opinion-and-expression-by-anyone",
                    "over": [],
                    "predicate": "secure_opinion_and_expression_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-opinion-and-expression"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "9f7d4e0e93f49362fe629be45585e96cf17de83909194a98e0d5c5bfe83f0225"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may enjoy freedom of opinion as well as expression (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-freedom-of-opinion-and-expression",
                    "over": [],
                    "predicate": "person_may_opinion_and_expression",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-opinion-and-expression"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "478b1fb898ba37e4901f77cbce6d6dfbd51f216918075472666c0eb2bdc7c5bf"
        }
      ],
      "status": "open",
      "unit": "u070",
      "version": 1
    },
    {
      "id": "rs_u073",
      "models": {
        "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0",
              "b1"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [
              [
                "b0"
              ]
            ],
            "right_protects_exercise": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of peaceful assembly as well as association (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "avoid-freedom-of-peaceful-assembly-and-association-by-state",
                    "over": [],
                    "predicate": "avoid_assembly_and_association_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-peaceful-assembly-and-association"
            }
          },
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "d33f60156deea03d3245a3ab28ace4cc58443c149869fa36390710058440bdf8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of peaceful assembly as well as association (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "name": "secure-freedom-of-peaceful-assembly-and-association-by-state",
                    "over": [],
                    "predicate": "secure_assembly_and_association_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-peaceful-assembly-and-association"
            }
          },
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "b7e43f22b9768ee3b967132aed7d70faaad90c6d45b3171d07755fa4fffb0231"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of peaceful assembly as well as association (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-freedom-of-peaceful-assembly-and-association-by-anyone",
                    "over": [],
                    "predicate": "avoid_assembly_and_association_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-peaceful-assembly-and-association"
            }
          },
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "b510c1c5e5483c7209a9f546b070841520394c5abcaae626158a136963ec98bb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "liberty": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of peaceful assembly as well as association (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). "
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-freedom-of-peaceful-assembly-and-association-by-anyone",
                    "over": [],
                    "predicate": "secure_assembly_and_association_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-peaceful-assembly-and-association"
            }
          },
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "9603d1664185c0e3ea0c19ee00da01a13c4ab2917d6b62cb63c51978ae4a98b7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "anyone_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_negative": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b",
              "state_positive": "39afa8c6577b19ec4b32bb6dca92b8d264c090ceb718a994bc875906a2a72c6b"
            },
            "who": "translator",
            "why": "Liberty reading: every person may enjoy freedom of peaceful assembly as well as association (the holder is permitted; no duty on anyone follows from this line)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "liberty",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "person-may-freedom-of-peaceful-assembly-and-association",
                    "over": [],
                    "predicate": "person_may_assembly_and_association",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-of-peaceful-assembly-and-association"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "90009af50314c99de29ab9d8fe3b22de2514562233b57b20c3f94a51719e8f0b"
        }
      ],
      "status": "open",
      "unit": "u073",
      "version": 1
    },
    {
      "id": "rs_u017",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "default": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 1 'should' read as a strict obligation on every human being to act towards each other human being in a spirit of brotherhood, with the completion unspecified (norm-defaults@0): the rule is unconditional, so VE reports gaps: none (readings/u017.strict.ve.md)."
          },
          "content": null,
          "id": "strict",
          "kind": "norm",
          "meaning_id": "d925badb406d293d79dff75bb848ba63321051d7a3c357354707d283b58b8eb2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "strict": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 1 'should' read as a defeasible rule: the same obligation holds unless the rule's exception applies, and the source names no decider (readings/u017.default.ve.md)."
          },
          "content": null,
          "id": "default",
          "kind": "norm",
          "meaning_id": "c7e4f886c9808a803a3b3bcb8963c2484945726ad7d290689d1c221ccfe5d688"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "strict",
            "default"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        },
        {
          "readings": [
            "strict",
            "default"
          ],
          "reason": "replaced 2026-10-02: the norm candidate declared a completion (allow or deny) that the source does not state (u052, u112 and u114 also kept their conditions in a sort description); it is now a norm-defaults@0 companion with the completion unspecified and the conditions in guards",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u017",
      "version": 3
    },
    {
      "id": "rs_u052",
      "models": {
        "790a8cace39080bf6893ce3bc720a70f0bd4d3c8f1a162c10d065654c249061b": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [
              [
                "p0"
              ]
            ],
            "asylum_right_covers_case": [
              [
                "p0"
              ]
            ],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "case_excluded": "790a8cace39080bf6893ce3bc720a70f0bd4d3c8f1a162c10d065654c249061b"
            },
            "who": "translator",
            "why": "Article 14(2) read as a prohibition on invoking the asylum right in the case of a prosecution that genuinely arises from a non-political crime or from acts contrary to UN purposes and principles. The two grounds are guards over the prosecution; for any other prosecution the text says nothing, and VE reports UNDECIDED, not permitted (readings/u052.invocation_barred.ve.md)."
          },
          "content": null,
          "id": "invocation_barred",
          "kind": "norm",
          "meaning_id": "5762358497be41b6b58902eedd2c4500953e62a91ef79b0b9a23df625334149a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "invocation_barred": "790a8cace39080bf6893ce3bc720a70f0bd4d3c8f1a162c10d065654c249061b"
            },
            "who": "translator",
            "why": "Article 14(2) read as a statement about the right's coverage: for every prosecution that genuinely arises from a non-political crime or from acts contrary to UN purposes and principles, the asylum right cannot be invoked in the case of that prosecution. A formula over prosecutions in this document; it says nothing about a person's other cases."
          },
          "content": [
            "forall",
            "prosecution",
            [
              "implies",
              [
                "or",
                [
                  "unary",
                  "arises_from_non_political_crime",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "unary",
                  "arises_from_acts_contrary_to_un",
                  [
                    "var",
                    0
                  ]
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "asylum_right_covers_case",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "id": "case_excluded",
          "kind": "asserted",
          "meaning_id": "d907638b2ced20736dc4eb450eda1f4c1a24226f87cdf7b0458c3cb44c9a1e98"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "invocation_barred",
            "right_inapplicable"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        },
        {
          "readings": [
            "invocation_barred",
            "entitlement_withheld"
          ],
          "reason": "rejected by the 2026-09-29 audit: the assertion and norm readings applied to the person or to every exercise of a person, not to the case or the single exercise",
          "version": 2
        },
        {
          "readings": [
            "invocation_barred",
            "entitlement_withheld"
          ],
          "reason": "replaced 2026-10-02: the norm candidate declared a completion (allow or deny) that the source does not state (u052, u112 and u114 also kept their conditions in a sort description); it is now a norm-defaults@0 companion with the completion unspecified and the conditions in guards",
          "version": 3
        }
      ],
      "status": "open",
      "unit": "u052",
      "version": 4
    },
    {
      "id": "rs_u112",
      "models": {
        "f4ea5a60d301cd5bf0ba418bab61099c6f9d68fba7ca96ab7a5638a8ac0d554d": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [
              [
                "e0"
              ]
            ],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [
              [
                "e0"
              ]
            ],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "exercise_unprotected": "f4ea5a60d301cd5bf0ba418bab61099c6f9d68fba7ca96ab7a5638a8ac0d554d"
            },
            "who": "translator",
            "why": "Article 29(3) read as a prohibition on carrying out an exercise of a declared right or freedom that is contrary to UN purposes and principles. Both conditions are guards over the exercise; other exercises are UNDECIDED (readings/u112.exercise_prohibited.ve.md)."
          },
          "content": null,
          "id": "exercise_prohibited",
          "kind": "norm",
          "meaning_id": "4a63c0cd1d6989afa0129e72e734bd61a025f33aa4d51645e6cd0e7089453c4c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "exercise_prohibited": "f4ea5a60d301cd5bf0ba418bab61099c6f9d68fba7ca96ab7a5638a8ac0d554d"
            },
            "who": "translator",
            "why": "Article 29(3) read as a limit on the rights' scope: no right or freedom protects an exercise contrary to UN purposes and principles. A formula over single exercises (not persons), so one contrary exercise removes protection from that exercise only."
          },
          "content": [
            "forall",
            "exercise",
            [
              "implies",
              [
                "unary",
                "exercise_contrary_to_un",
                [
                  "var",
                  0
                ]
              ],
              [
                "not",
                [
                  "unary",
                  "right_protects_exercise",
                  [
                    "var",
                    0
                  ]
                ]
              ]
            ]
          ],
          "id": "exercise_unprotected",
          "kind": "asserted",
          "meaning_id": "f2918755b54900745b966c12b50ecfed2aadd030a159aed0e2da479c338775d3"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "exercise_restricted"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        },
        {
          "readings": [
            "exercise_prohibited",
            "scope_limited"
          ],
          "reason": "rejected by the 2026-09-29 audit: the assertion and norm readings applied to the person or to every exercise of a person, not to the case or the single exercise",
          "version": 2
        },
        {
          "readings": [
            "exercise_prohibited",
            "scope_limited"
          ],
          "reason": "replaced 2026-10-02: the norm candidate declared a completion (allow or deny) that the source does not state (u052, u112 and u114 also kept their conditions in a sort description); it is now a norm-defaults@0 companion with the completion unspecified and the conditions in guards",
          "version": 3
        }
      ],
      "status": "open",
      "unit": "u112",
      "version": 4
    },
    {
      "id": "rs_u114",
      "models": {
        "ccfa813dee2fc1a7b15cdbff60f980f570ea6b8419525ad6069b3ac0b2a43508": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [
              [
                "b0"
              ]
            ],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "no_implied_right": "ccfa813dee2fc1a7b15cdbff60f980f570ea6b8419525ad6069b3ac0b2a43508"
            },
            "who": "translator",
            "why": "Article 30 read as a prohibition on adopting an interpretation that implies, for a State, group or person, a right to destroy declared rights. The implication is the guard over the interpretation; other interpretations are UNDECIDED (readings/u114.interpretive_ban.ve.md)."
          },
          "content": null,
          "id": "interpretive_ban",
          "kind": "norm",
          "meaning_id": "ac33b613575929bf96a3e33e2e8b1d3579c6ade86c9cfbf347e90f3ac2917a0b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "interpretive_ban": "ccfa813dee2fc1a7b15cdbff60f980f570ea6b8419525ad6069b3ac0b2a43508"
            },
            "who": "translator",
            "why": "Article 30 read as a statement of the Declaration's content: it implies for no State, group or person a right to engage in any activity or act aimed at destroying any declared right."
          },
          "content": [
            "forall",
            "bearer",
            [
              "not",
              [
                "unary",
                "declaration_implies_destructive_right",
                [
                  "var",
                  0
                ]
              ]
            ]
          ],
          "id": "no_implied_right",
          "kind": "asserted",
          "meaning_id": "8c3f94f0ad54ff37db29e747d707726f90abba4b60407e88c2a17078ed77f6fc"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "interpretive_bar"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        },
        {
          "readings": [
            "interpretive_ban",
            "no_implied_right"
          ],
          "reason": "replaced 2026-10-02: the norm candidate declared a completion (allow or deny) that the source does not state (u052, u112 and u114 also kept their conditions in a sort description); it is now a norm-defaults@0 companion with the completion unspecified and the conditions in guards",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u114",
      "version": 3
    },
    {
      "id": "rs_u035",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 8 read as a duty on a competent national tribunal to provide an effective remedy against an act that violates a fundamental right granted by the constitution or by law (both conditions are guards; the bearer is named by the source's 'by the competent national tribunals'). Strict force; the remedy is owed to the victim of the act, who is not an argument (predicates have at most two) (readings/u035.tribunal_claim.ve.md)."
          },
          "content": null,
          "id": "tribunal_claim",
          "kind": "norm",
          "meaning_id": "5511d061c32961d91065dbf021e3ae1b29d9565cae7d96367bfb771c940d3d0f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "tribunal_claim": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 8 read as a duty on a State to ensure that competent national tribunals provide an effective remedy against such an act (same guard on the act). Strict force (readings/u035.state_claim.ve.md)."
          },
          "content": null,
          "id": "state_claim",
          "kind": "norm",
          "meaning_id": "945f0fb6eece3b1ad25b1511bc1e38c089a9422ffd24a46cb15db84ea77696fb"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "state_claim",
            "anyone_claim"
          ],
          "reason": "rejected by the 2026-10-01T1800Z audit: the checked duty had no argument for the rights-violating act and its prose holder sort could not ensure an effective remedy for each qualifying violation",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u035",
      "version": 2
    },
    {
      "id": "rs_u051",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_avoid": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "state_avoid": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 14(1) read as a liberty: a person may seek and enjoy asylum from persecution in other countries (the unconditional permission names no other case) (readings/u051.liberty.ve.md)."
          },
          "content": null,
          "id": "liberty",
          "kind": "norm",
          "meaning_id": "13eb11c8c14d2eea783d413bf6249da08756bbf19613686e43a0f0561ba3eae3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_avoid": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "liberty": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 14(1) read as a duty on every State to avoid barring a person who seeks or enjoys asylum from persecution from seeking as well as enjoying it in other countries. 'From persecution' is a guard on the person; no positive duty to grant asylum is a candidate (the audit found it strengthened the source) (readings/u051.state_avoid.ve.md)."
          },
          "content": null,
          "id": "state_avoid",
          "kind": "norm",
          "meaning_id": "3452e29a815b747a4148a92b9685a24f7847a7c209a1ce87a46ec9f2d666a421"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "state_avoid": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "As state_avoid, bound on every State, group and person (the source names no bearer) (readings/u051.anyone_avoid.ve.md)."
          },
          "content": null,
          "id": "anyone_avoid",
          "kind": "norm",
          "meaning_id": "6c32fa41dbadbc331af620734ddc2e3902545a6baee1f8bd54792fed775836b9"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "state_negative",
            "state_positive",
            "anyone_negative",
            "anyone_positive",
            "liberty"
          ],
          "reason": "rejected by the 2026-10-01T1800Z audit: the positive candidates required every bearer to grant asylum to every person and omitted seeking",
          "version": 1
        },
        {
          "readings": [
            "liberty",
            "state_avoid",
            "anyone_avoid"
          ],
          "reason": "rejected by the 2026-10-02T0600Z audit: the two avoiding duties applied only if the person is persecuted, so a person seeking asylum from persecution that is only threatened fell outside the guard and the right to seek asylum from persecution was weakened; the guard is now the person's seeking or enjoying asylum from persecution, suffered or threatened",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u051",
      "version": 3
    },
    {
      "id": "rs_u077",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "residence_country_claim": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 21(2) read as a duty on the country of which the person is a national to give equal access to public service. 'His country' is the relation is_nationality_country_of in the guard, so unrelated bearers are not bound (readings/u077.nationality_country_claim.ve.md)."
          },
          "content": null,
          "id": "nationality_country_claim",
          "kind": "norm",
          "meaning_id": "997fd20b8242ab2448c1be56021dd503b3b843dc1a68916fb992f491d08188c8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "nationality_country_claim": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 21(2) read with 'his country' as the country in which the person resides (guard is_residence_country_of); the source does not say which country is meant (readings/u077.residence_country_claim.ve.md)."
          },
          "content": null,
          "id": "residence_country_claim",
          "kind": "norm",
          "meaning_id": "cb19d71a65224e5a9f19dff1ee0f54832ee35a6eb1efee934879f951fd59494d"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "state_claim",
            "anyone_claim"
          ],
          "reason": "rejected by the 2026-10-01T1800Z audit: no checked relation connected a bearer to the holder's country, so the candidates bound unrelated bearers",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u077",
      "version": 2
    },
    {
      "id": "rs_u061",
      "models": {},
      "readings": [
        {
          "admission": {
            "distinguishing_models": {},
            "who": "translator",
            "why": "Article 16(3), second clause read as a duty on society and on the State to protect the family. The subject (the family) is read from u060 and is not a checked reference; the guard names the two protectors the source names. One reading is offered; no other is known to the translator, and the set stays open (readings/u061.claim.ve.md)."
          },
          "content": null,
          "id": "claim",
          "kind": "norm",
          "meaning_id": "dc40209a450b53f2021e9d5be195ff8ba30c3695ad3d7f2cef9c3deadd93661e"
        }
      ],
      "status": "open",
      "unit": "u061",
      "version": 1
    },
    {
      "id": "rs_u110",
      "models": {},
      "readings": [
        {
          "admission": {
            "distinguishing_models": {},
            "who": "translator",
            "why": "Article 29(1) read as a duty on each person to perform duties to the community in which alone the free and full development of the person's personality is possible; the relative clause is a guard (a base relation between community and person) and which duties is the named open term duties_to_the_community. One reading is offered and the set stays open (readings/u110.duty.ve.md)."
          },
          "content": null,
          "id": "duty",
          "kind": "norm",
          "meaning_id": "a0b08cc3600b2ae2a4c2c4bc8449cd619bdb79406baf55a238dd780b76f68ca0"
        }
      ],
      "status": "open",
      "unit": "u110",
      "version": 1
    },
    {
      "id": "rs_u054",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 15(1) read as an entitlement: each person must receive a nationality. The duty is stated for the person as the one entitled and names no bearer, because the source names none; the right is not read as already fulfilled (readings/u054.claim.ve.md)."
          },
          "content": null,
          "id": "claim",
          "kind": "norm",
          "meaning_id": "5fd2b0290dae989637dddded836dba5b33ef12ad8cc70d6225d477507180611a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "claim": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 15(1) read as a liberty: each person is permitted to have a nationality (readings/u054.liberty.ve.md)."
          },
          "content": null,
          "id": "liberty",
          "kind": "norm",
          "meaning_id": "f72bacd30bee2d9c84788fa731aeb1aebcd0011348425d4c25b3db234208d08a"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "each_person_has_a_nationality",
            "some_state_grants_each"
          ],
          "reason": "rejected by the 2026-10-02T0600Z audit: both asserted readings turned a right to a nationality into an accomplished fact (everyone already has one, or some state already grants one to everyone); the source does not say the right is fulfilled",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u054",
      "version": 2
    },
    {
      "id": "rs_u111",
      "models": {
        "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "exercise": [
              "e0"
            ],
            "person": [
              "p0"
            ],
            "prosecution": [
              "p0"
            ]
          },
          "relations": {
            "arises_from_acts_contrary_to_un": [],
            "arises_from_non_political_crime": [],
            "asylum_right_covers_case": [],
            "avoid_assembly_and_association_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_equal_protection_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_recognition_as_person_required": [],
            "secure_security_of_person_required": [],
            "secure_thought_conscience_religion_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "default_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "Article 29(2) read as a strict duty to keep each person free of a limitation unless it is determined by law and solely for one or both of the two aims the text lists. The conditions are necessary, never sufficient: a limitation that meets them is UNDECIDED (readings/u111.strict_listed_aims.ve.md)."
          },
          "content": null,
          "id": "strict_listed_aims",
          "kind": "norm",
          "meaning_id": "7703e9a5ee6e771baa7e5618bee5b5afac5f96c77529c2340c3173cde193aad0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "default_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "As strict_listed_aims, with 'solely for the purpose of securing ... and of meeting ...' read as requiring both aims (readings/u111.strict_both_aims.ve.md)."
          },
          "content": null,
          "id": "strict_both_aims",
          "kind": "norm",
          "meaning_id": "81d9212042460f958f1c50565207bebada779bb5e04f87e85f6a8f66beedd1b2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "As strict_listed_aims, with 'shall' read as a defeasible rule whose exception has no stated decider (soft-norms@0 companion; the completion declared there is 'deny' = not required) (readings/u111.default_listed_aims.ve.md)."
          },
          "content": null,
          "id": "default_listed_aims",
          "kind": "norm",
          "meaning_id": "19812908f48b1abe62abf83932b7affdcf51967c581f8b8afa16677cdf2a9fbd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_both_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2",
              "strict_listed_aims": "3072f95984d7c2ef605e263cca932213f736ab1d36b8de3f3e2c70db894c96a2"
            },
            "who": "translator",
            "why": "As strict_both_aims, with 'shall' read as a defeasible rule (soft-norms@0 companion) (readings/u111.default_both_aims.ve.md)."
          },
          "content": null,
          "id": "default_both_aims",
          "kind": "norm",
          "meaning_id": "d7f2918f29e651aa8a7eb40ac7c86c737c52b446a5f47474cf7ed7f640760356"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "limitation-29 (rights@0 limitation)"
          ],
          "reason": "rejected by the 2026-10-02T0600Z audit: the assembled document reported zero limitation terms, so the limitation constrained none of the rights, which were all reading-set candidates; it is replaced by norm candidates whose guards carry the necessary conditions",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u111",
      "version": 2
    }
  ],
  "units": [
    {
      "id": "u001",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        0,
        41
      ],
      "support": "none"
    },
    {
      "id": "u002",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        41,
        54
      ],
      "support": "none"
    },
    {
      "id": "u003",
      "kind": [
        "unformalised",
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
      },
      "span": [
        54,
        236
      ],
      "support": "none"
    },
    {
      "id": "u004",
      "kind": [
        "unformalised",
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
      },
      "span": [
        236,
        363
      ],
      "support": "none"
    },
    {
      "id": "u005",
      "kind": [
        "attributed",
        "unstated",
        "says",
        "asserted"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        363,
        552
      ],
      "support": "none"
    },
    {
      "id": "u006",
      "kind": [
        "unformalised",
        "modality_belief"
      ],
      "meaning": {
        "unformalised": "modality_belief"
      },
      "span": [
        552,
        747
      ],
      "support": "none"
    },
    {
      "id": "u007",
      "kind": [
        "unformalised",
        "modality_belief"
      ],
      "meaning": {
        "unformalised": "modality_belief"
      },
      "span": [
        747,
        838
      ],
      "support": "none"
    },
    {
      "id": "u008a",
      "kind": [
        "attributed",
        "peoples_of_un",
        "believes",
        "asserted"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        838,
        1037
      ],
      "support": "none"
    },
    {
      "id": "u008b",
      "kind": [
        "attributed",
        "peoples_of_un",
        "intends",
        "norm"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        1037,
        1134
      ],
      "support": "none"
    },
    {
      "id": "u009",
      "kind": [
        "attributed",
        "member_states",
        "promised",
        "norm"
      ],
      "meaning": {
        "unformalised": "attribution"
      },
      "span": [
        1134,
        1330
      ],
      "support": "none"
    },
    {
      "id": "u010",
      "kind": [
        "unformalised",
        "other_evaluative_open_claim"
      ],
      "meaning": {
        "unformalised": "other_evaluative_open_claim"
      },
      "span": [
        1330,
        1462
      ],
      "support": "none"
    },
    {
      "id": "u011",
      "kind": "meta",
      "meaning": {
        "contextual": "preamble_transition_or_speaker"
      },
      "span": [
        1462,
        1479
      ],
      "support": "none"
    },
    {
      "id": "u012",
      "kind": "meta",
      "meaning": {
        "contextual": "preamble_transition_or_speaker"
      },
      "span": [
        1479,
        1502
      ],
      "support": "none"
    },
    {
      "id": "u013a",
      "kind": [
        "attributed",
        "general_assembly",
        "says",
        "norm"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1502,
        1622
      ],
      "support": "none"
    },
    {
      "id": "u013ba",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1622,
        1817
      ],
      "support": "none"
    },
    {
      "id": "u013bb",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        1817,
        2058
      ],
      "support": "none"
    },
    {
      "id": "u014",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2058,
        2072
      ],
      "support": "none"
    },
    {
      "id": "u015",
      "kind": [
        "unformalised",
        "time"
      ],
      "meaning": {
        "unformalised": "time"
      },
      "span": [
        2072,
        2136
      ],
      "support": "none"
    },
    {
      "id": "u016",
      "kind": [
        "unformalised",
        "other_metaphorical_endowment"
      ],
      "meaning": {
        "unformalised": "other_metaphorical_endowment"
      },
      "span": [
        2136,
        2179
      ],
      "support": "none"
    },
    {
      "id": "u017",
      "kind": "norm",
      "meaning": {
        "open": [
          "spirit_of_brotherhood"
        ]
      },
      "span": [
        2179,
        2244
      ],
      "support": "none"
    },
    {
      "id": "u018",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2244,
        2258
      ],
      "support": "none"
    },
    {
      "id": "u019",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        2258,
        2509
      ],
      "support": "none"
    },
    {
      "id": "u020",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        2509,
        2776
      ],
      "support": "none"
    },
    {
      "id": "u021",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2776,
        2790
      ],
      "support": "none"
    },
    {
      "id": "u022a",
      "kind": "right",
      "meaning": "specified",
      "span": [
        2790,
        2820
      ],
      "support": "none"
    },
    {
      "id": "u022b",
      "kind": "right",
      "meaning": "specified",
      "span": [
        2820,
        2829
      ],
      "support": "none"
    },
    {
      "id": "u022c",
      "kind": "right",
      "meaning": "specified",
      "span": [
        2829,
        2855
      ],
      "support": "none"
    },
    {
      "id": "u023",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2855,
        2869
      ],
      "support": "none"
    },
    {
      "id": "u024",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        2869,
        2915
      ],
      "support": "none"
    },
    {
      "id": "u025",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        2915,
        2984
      ],
      "support": "none"
    },
    {
      "id": "u026",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        2984,
        2998
      ],
      "support": "none"
    },
    {
      "id": "u027",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        2998,
        3095
      ],
      "support": "none"
    },
    {
      "id": "u028",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3095,
        3109
      ],
      "support": "none"
    },
    {
      "id": "u029",
      "kind": "right",
      "meaning": "specified",
      "span": [
        3109,
        3187
      ],
      "support": "none"
    },
    {
      "id": "u030",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3187,
        3201
      ],
      "support": "none"
    },
    {
      "id": "u031",
      "kind": [
        "unformalised",
        "norms"
      ],
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        3201,
        3229
      ],
      "support": "none"
    },
    {
      "id": "u032",
      "kind": "right",
      "meaning": {
        "open": [
          "discrimination",
          "equal_protection_of_the_law"
        ]
      },
      "span": [
        3229,
        3306
      ],
      "support": "none"
    },
    {
      "id": "u033a",
      "kind": "right",
      "meaning": {
        "open": [
          "discrimination",
          "equal_protection_of_the_law"
        ]
      },
      "span": [
        3306,
        3402
      ],
      "support": "none"
    },
    {
      "id": "u033b",
      "kind": "right",
      "meaning": {
        "open": [
          "discrimination",
          "equal_protection_of_the_law"
        ]
      },
      "span": [
        3402,
        3455
      ],
      "support": "none"
    },
    {
      "id": "u034",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3455,
        3469
      ],
      "support": "none"
    },
    {
      "id": "u035",
      "kind": "norm",
      "meaning": {
        "open": [
          "effective",
          "competent",
          "fundamental_rights_granted"
        ]
      },
      "span": [
        3469,
        3637
      ],
      "support": "none"
    },
    {
      "id": "u036",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3637,
        3651
      ],
      "support": "none"
    },
    {
      "id": "u037",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        3651,
        3719
      ],
      "support": "none"
    },
    {
      "id": "u038",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3719,
        3734
      ],
      "support": "none"
    },
    {
      "id": "u039",
      "kind": [
        "unformalised",
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
      },
      "span": [
        3734,
        3935
      ],
      "support": "none"
    },
    {
      "id": "u040",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        3935,
        3950
      ],
      "support": "none"
    },
    {
      "id": "u041",
      "kind": [
        "unformalised",
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
      },
      "span": [
        3950,
        4151
      ],
      "support": "none"
    },
    {
      "id": "u042",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        4151,
        4351
      ],
      "support": "none"
    },
    {
      "id": "u043",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        4351,
        4469
      ],
      "support": "none"
    },
    {
      "id": "u044",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4469,
        4484
      ],
      "support": "none"
    },
    {
      "id": "u045a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        4484,
        4584
      ],
      "support": "none"
    },
    {
      "id": "u045b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        4584,
        4633
      ],
      "support": "none"
    },
    {
      "id": "u046",
      "kind": "right",
      "meaning": {
        "open": [
          "arbitrary"
        ]
      },
      "span": [
        4633,
        4724
      ],
      "support": "none"
    },
    {
      "id": "u047",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4724,
        4739
      ],
      "support": "none"
    },
    {
      "id": "u048",
      "kind": "right",
      "meaning": "specified",
      "span": [
        4739,
        4837
      ],
      "support": "none"
    },
    {
      "id": "u049",
      "kind": "right",
      "meaning": "specified",
      "span": [
        4837,
        4935
      ],
      "support": "none"
    },
    {
      "id": "u050",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        4935,
        4950
      ],
      "support": "none"
    },
    {
      "id": "u051",
      "kind": "norm",
      "meaning": {
        "open": [
          "persecution"
        ]
      },
      "span": [
        4950,
        5042
      ],
      "support": "none"
    },
    {
      "id": "u052",
      "kind": "norm",
      "meaning": {
        "open": [
          "genuine",
          "non_political_crime",
          "contrary_to_un_purposes_and_principles"
        ]
      },
      "span": [
        5042,
        5224
      ],
      "support": "none"
    },
    {
      "id": "u053",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5224,
        5239
      ],
      "support": "none"
    },
    {
      "id": "u054",
      "kind": "norm",
      "meaning": "specified",
      "span": [
        5239,
        5284
      ],
      "support": "none"
    },
    {
      "id": "u055",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        5284,
        5392
      ],
      "support": "none"
    },
    {
      "id": "u056",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5392,
        5407
      ],
      "support": "none"
    },
    {
      "id": "u057",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5407,
        5545
      ],
      "support": "none"
    },
    {
      "id": "u058",
      "kind": "norm",
      "meaning": {
        "unformalised": "norms"
      },
      "span": [
        5545,
        5636
      ],
      "support": "none"
    },
    {
      "id": "u059",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        5636,
        5733
      ],
      "support": "none"
    },
    {
      "id": "u060",
      "kind": [
        "unformalised",
        "other_evaluative_open_claim"
      ],
      "meaning": {
        "unformalised": "other_evaluative_open_claim"
      },
      "span": [
        5733,
        5799
      ],
      "support": "none"
    },
    {
      "id": "u061",
      "kind": "norm",
      "meaning": {
        "open": [
          "protection_of_the_family"
        ]
      },
      "span": [
        5799,
        5857
      ],
      "support": "none"
    },
    {
      "id": "u062",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        5857,
        5872
      ],
      "support": "none"
    },
    {
      "id": "u063",
      "kind": "right",
      "meaning": "specified",
      "span": [
        5872,
        5960
      ],
      "support": "none"
    },
    {
      "id": "u064",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        5960,
        6018
      ],
      "support": "none"
    },
    {
      "id": "u065",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6018,
        6033
      ],
      "support": "none"
    },
    {
      "id": "u066",
      "kind": "right",
      "meaning": "specified",
      "span": [
        6033,
        6104
      ],
      "support": "none"
    },
    {
      "id": "u067",
      "kind": [
        "unformalised",
        "other_right_lines_in_reading_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_in_reading_sets"
      },
      "span": [
        6104,
        6166
      ],
      "support": "none"
    },
    {
      "id": "u068",
      "kind": [
        "unformalised",
        "other_right_lines_in_reading_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_in_reading_sets"
      },
      "span": [
        6166,
        6329
      ],
      "support": "none"
    },
    {
      "id": "u069",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6329,
        6344
      ],
      "support": "none"
    },
    {
      "id": "u070",
      "kind": "right",
      "meaning": "specified",
      "span": [
        6344,
        6405
      ],
      "support": "none"
    },
    {
      "id": "u071a",
      "kind": [
        "unformalised",
        "other_right_lines_in_reading_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_in_reading_sets"
      },
      "span": [
        6405,
        6470
      ],
      "support": "none"
    },
    {
      "id": "u071b",
      "kind": [
        "unformalised",
        "other_right_lines_in_reading_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_in_reading_sets"
      },
      "span": [
        6470,
        6573
      ],
      "support": "none"
    },
    {
      "id": "u072",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6573,
        6588
      ],
      "support": "none"
    },
    {
      "id": "u073",
      "kind": "right",
      "meaning": "specified",
      "span": [
        6588,
        6664
      ],
      "support": "none"
    },
    {
      "content": {
        "norm": {
          "guard": [
            "top"
          ],
          "name": "no-compelled-association-membership",
          "over": [],
          "predicate": "compel_association_membership_permitted",
          "sign": false,
          "unless": []
        }
      },
      "id": "u074",
      "kind": "norm",
      "meaning": "specified",
      "span": [
        6664,
        6721
      ],
      "status": "CHECKED",
      "support": "none"
    },
    {
      "id": "u075",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        6721,
        6736
      ],
      "support": "none"
    },
    {
      "id": "u076",
      "kind": [
        "unformalised",
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
      },
      "span": [
        6736,
        6861
      ],
      "support": "none"
    },
    {
      "id": "u077",
      "kind": "norm",
      "meaning": "specified",
      "span": [
        6861,
        6938
      ],
      "support": "none"
    },
    {
      "id": "u078",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        6938,
        7015
      ],
      "support": "none"
    },
    {
      "id": "u079a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7015,
        7124
      ],
      "support": "none"
    },
    {
      "id": "u079b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7124,
        7200
      ],
      "support": "none"
    },
    {
      "id": "u080",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        7200,
        7215
      ],
      "support": "none"
    },
    {
      "id": "u081",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7215,
        7281
      ],
      "support": "none"
    },
    {
      "id": "u082",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7281,
        7558
      ],
      "support": "none"
    },
    {
      "id": "u083",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        7558,
        7573
      ],
      "support": "none"
    },
    {
      "id": "u084a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7573,
        7606
      ],
      "support": "none"
    },
    {
      "id": "u084b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7606,
        7636
      ],
      "support": "none"
    },
    {
      "id": "u084c",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7636,
        7679
      ],
      "support": "none"
    },
    {
      "id": "u084d",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7679,
        7721
      ],
      "support": "none"
    },
    {
      "id": "u085",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7721,
        7806
      ],
      "support": "none"
    },
    {
      "id": "u086",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        7806,
        8022
      ],
      "support": "none"
    },
    {
      "id": "u087",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8022,
        8119
      ],
      "support": "none"
    },
    {
      "id": "u088",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8119,
        8134
      ],
      "support": "none"
    },
    {
      "id": "u089",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8134,
        8260
      ],
      "support": "none"
    },
    {
      "id": "u090",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8260,
        8275
      ],
      "support": "none"
    },
    {
      "id": "u091",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8275,
        8476
      ],
      "support": "none"
    },
    {
      "id": "u092",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8476,
        8639
      ],
      "support": "none"
    },
    {
      "id": "u093",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8639,
        8712
      ],
      "support": "none"
    },
    {
      "id": "u094",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8712,
        8802
      ],
      "support": "none"
    },
    {
      "id": "u095",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        8802,
        8817
      ],
      "support": "none"
    },
    {
      "id": "u096",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8817,
        8857
      ],
      "support": "none"
    },
    {
      "id": "u097",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8857,
        8933
      ],
      "support": "none"
    },
    {
      "id": "u098",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8933,
        8975
      ],
      "support": "none"
    },
    {
      "id": "u099a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        8975,
        9045
      ],
      "support": "none"
    },
    {
      "id": "u099b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9045,
        9126
      ],
      "support": "none"
    },
    {
      "id": "u100a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9126,
        9205
      ],
      "support": "none"
    },
    {
      "id": "u100b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9205,
        9285
      ],
      "support": "none"
    },
    {
      "id": "u101",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9285,
        9389
      ],
      "support": "none"
    },
    {
      "id": "u102",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9389,
        9475
      ],
      "support": "none"
    },
    {
      "id": "u103",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9475,
        9577
      ],
      "support": "none"
    },
    {
      "id": "u104",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        9577,
        9592
      ],
      "support": "none"
    },
    {
      "id": "u105a",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9592,
        9677
      ],
      "support": "none"
    },
    {
      "id": "u105b",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9677,
        9696
      ],
      "support": "none"
    },
    {
      "id": "u105c",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9696,
        9755
      ],
      "support": "none"
    },
    {
      "id": "u106",
      "kind": [
        "unformalised",
        "other_force_variants_in_one_reading_set"
      ],
      "meaning": {
        "unformalised": "other_force_variants_in_one_reading_set"
      },
      "span": [
        9755,
        9926
      ],
      "support": "none"
    },
    {
      "id": "u107",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        9926,
        9941
      ],
      "support": "none"
    },
    {
      "id": "u108",
      "kind": [
        "unformalised",
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
      },
      "span": [
        9941,
        10085
      ],
      "support": "none"
    },
    {
      "id": "u109",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        10085,
        10100
      ],
      "support": "none"
    },
    {
      "id": "u110",
      "kind": "norm",
      "meaning": {
        "open": [
          "duties_to_the_community",
          "free_and_full_development"
        ]
      },
      "span": [
        10100,
        10218
      ],
      "support": "none"
    },
    {
      "id": "u111",
      "kind": "norm",
      "meaning": {
        "open": [
          "determined_by_law",
          "due_recognition_and_respect",
          "just_requirements",
          "morality",
          "public_order",
          "general_welfare",
          "democratic_society"
        ]
      },
      "span": [
        10218,
        10555
      ],
      "support": "none"
    },
    {
      "id": "u112",
      "kind": "norm",
      "meaning": {
        "open": [
          "rights_and_freedoms_set_forth",
          "contrary_to_un_purposes_and_principles"
        ]
      },
      "span": [
        10555,
        10676
      ],
      "support": "none"
    },
    {
      "id": "u113",
      "kind": "meta",
      "meaning": "specified",
      "span": [
        10676,
        10691
      ],
      "support": "none"
    },
    {
      "id": "u114",
      "kind": "norm",
      "meaning": {
        "open": [
          "rights_and_freedoms_set_forth",
          "aimed_at_destruction_of_rights"
        ]
      },
      "span": [
        10691,
        10916
      ],
      "support": "none"
    }
  ]
}
---
# Universal Declaration of Human Rights

## Preamble

Whereas recognition of the inherent dignity and of the equal and inalienable rights of all members of the human family is the foundation of freedom, justice and peace in the world,

Whereas disregard and contempt for human rights have resulted in barbarous acts which have outraged the conscience of mankind, and the advent of a world in which human beings shall enjoy freedom of speech and belief and freedom from fear and want has been proclaimed as the highest aspiration of the common people,

Whereas it is essential, if man is not to be compelled to have recourse, as a last resort, to rebellion against tyranny and oppression, that human rights should be protected by the rule of law,

Whereas it is essential to promote the development of friendly relations between nations,

Whereas the peoples of the United Nations have in the Charter reaffirmed their faith in fundamental human rights, in the dignity and worth of the human person and in the equal rights of men and women and have determined to promote social progress and better standards of life in larger freedom,

Whereas Member States have pledged themselves to achieve, in co-operation with the United Nations, the promotion of universal respect for and observance of human rights and fundamental freedoms,

Whereas a common understanding of these rights and freedoms is of the greatest importance for the full realization of this pledge,

Now, therefore,

The General Assembly,

Proclaims this Universal Declaration of Human Rights as a common standard of achievement for all peoples and all nations, to the end that every individual and every organ of society, keeping this Declaration constantly in mind, shall strive by teaching and education to promote respect for these rights and freedoms and by progressive measures, national and international, to secure their universal and effective recognition and observance, both among the peoples of Member States themselves and among the peoples of territories under their jurisdiction.

## Article 1

All human beings are born free and equal in dignity and rights. They are endowed with reason and conscience and should act towards one another in a spirit of brotherhood.

## Article 2

Everyone is entitled to all the rights and freedoms set forth in this Declaration, without distinction of any kind, such as race, colour, sex, language, religion, political or other opinion, national or social origin, property, birth or other status. Furthermore, no distinction shall be made on the basis of the political, jurisdictional or international status of the country or territory to which a person belongs, whether it be independent, trust, non-self-governing or under any other limitation of sovereignty.

## Article 3

Everyone has the right to life, liberty and security of person.

## Article 4

No one shall be held in slavery or servitude; slavery and the slave trade shall be prohibited in all their forms.

## Article 5

No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment.

## Article 6

Everyone has the right to recognition everywhere as a person before the law.

## Article 7

All are equal before the law and are entitled without any discrimination to equal protection of the law. All are entitled to equal protection against any discrimination in violation of this Declaration and against any incitement to such discrimination.

## Article 8

Everyone has the right to an effective remedy by the competent national tribunals for acts violating the fundamental rights granted him by the constitution or by law.

## Article 9

No one shall be subjected to arbitrary arrest, detention or exile.

## Article 10

Everyone is entitled in full equality to a fair and public hearing by an independent and impartial tribunal, in the determination of his rights and obligations and of any criminal charge against him.

## Article 11

1. Everyone charged with a penal offence has the right to be presumed innocent until proved guilty according to law in a public trial at which he has had all the guarantees necessary for his defence.

2. No one shall be held guilty of any penal offence on account of any act or omission which did not constitute a penal offence, under national or international law, at the time when it was committed. Nor shall a heavier penalty be imposed than the one that was applicable at the time the penal offence was committed.

## Article 12

No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence, nor to attacks upon his honour and reputation. Everyone has the right to the protection of the law against such interference or attacks.

## Article 13

1. Everyone has the right to freedom of movement and residence within the borders of each state.

2. Everyone has the right to leave any country, including his own, and to return to his country.

## Article 14

1. Everyone has the right to seek and to enjoy in other countries asylum from persecution.

2. This right may not be invoked in the case of prosecutions genuinely arising from non-political crimes or from acts contrary to the purposes and principles of the United Nations.

## Article 15

1. Everyone has the right to a nationality.

2. No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality.

## Article 16

1. Men and women of full age, without any limitation due to race, nationality or religion, have the right to marry and to found a family. They are entitled to equal rights as to marriage, during marriage and at its dissolution.

2. Marriage shall be entered into only with the free and full consent of the intending spouses.

3. The family is the natural and fundamental group unit of society and is entitled to protection by society and the State.

## Article 17

1. Everyone has the right to own property alone as well as in association with others.

2. No one shall be arbitrarily deprived of his property.

## Article 18

Everyone has the right to freedom of thought, conscience and religion; this right includes freedom to change his religion or belief, and freedom, either alone or in community with others and in public or private, to manifest his religion or belief in teaching, practice, worship and observance.

## Article 19

Everyone has the right to freedom of opinion and expression; this right includes freedom to hold opinions without interference and to seek, receive and impart information and ideas through any media and regardless of frontiers.

## Article 20

1. Everyone has the right to freedom of peaceful assembly and association.

2. No one may be compelled to belong to an association.

## Article 21

1. Everyone has the right to take part in the government of his country, directly or through freely chosen representatives.

2. Everyone has the right of equal access to public service in his country.

3. The will of the people shall be the basis of the authority of government; this will shall be expressed in periodic and genuine elections which shall be by universal and equal suffrage and shall be held by secret vote or by equivalent free voting procedures.

## Article 22

Everyone, as a member of society, has the right to social security and is entitled to realization, through national effort and international co-operation and in accordance with the organization and resources of each State, of the economic, social and cultural rights indispensable for his dignity and the free development of his personality.

## Article 23

1. Everyone has the right to work, to free choice of employment, to just and favourable conditions of work and to protection against unemployment.

2. Everyone, without any discrimination, has the right to equal pay for equal work.

3. Everyone who works has the right to just and favourable remuneration ensuring for himself and his family an existence worthy of human dignity, and supplemented, if necessary, by other means of social protection.

4. Everyone has the right to form and to join trade unions for the protection of his interests.

## Article 24

Everyone has the right to rest and leisure, including reasonable limitation of working hours and periodic holidays with pay.

## Article 25

1. Everyone has the right to a standard of living adequate for the health and well-being of himself and of his family, including food, clothing, housing and medical care and necessary social services, and the right to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of livelihood in circumstances beyond his control.

2. Motherhood and childhood are entitled to special care and assistance. All children, whether born in or out of wedlock, shall enjoy the same social protection.

## Article 26

1. Everyone has the right to education. Education shall be free, at least in the elementary and fundamental stages. Elementary education shall be compulsory. Technical and professional education shall be made generally available and higher education shall be equally accessible to all on the basis of merit.

2. Education shall be directed to the full development of the human personality and to the strengthening of respect for human rights and fundamental freedoms. It shall promote understanding, tolerance and friendship among all nations, racial or religious groups, and shall further the activities of the United Nations for the maintenance of peace.

3. Parents have a prior right to choose the kind of education that shall be given to their children.

## Article 27

1. Everyone has the right freely to participate in the cultural life of the community, to enjoy the arts and to share in scientific advancement and its benefits.

2. Everyone has the right to the protection of the moral and material interests resulting from any scientific, literary or artistic production of which he is the author.

## Article 28

Everyone is entitled to a social and international order in which the rights and freedoms set forth in this Declaration can be fully realized.

## Article 29

1. Everyone has duties to the community in which alone the free and full development of his personality is possible.

2. In the exercise of his rights and freedoms, everyone shall be subject only to such limitations as are determined by law solely for the purpose of securing due recognition and respect for the rights and freedoms of others and of meeting the just requirements of morality, public order and the general welfare in a democratic society.

3. These rights and freedoms may in no case be exercised contrary to the purposes and principles of the United Nations.

## Article 30

Nothing in this Declaration may be interpreted as implying for any State, group or person any right to engage in any activity or to perform any act aimed at the destruction of any of the rights and freedoms set forth herein.
