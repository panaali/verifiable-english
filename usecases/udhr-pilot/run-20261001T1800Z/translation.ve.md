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
        "avoid_asylum_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from seeking as well as enjoying asylum in other countries. Source clause: the right to seek and to enjoy in other countries asylum from persecution.",
          "regulated": {
            "act": "{0} avoid barring {1} from seeking as well as enjoying asylum in other countries",
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
        "grants_nationality": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer grants the person a nationality",
          "verbalisation": "{0} grants {1} a nationality"
        },
        "has_a_nationality": {
          "arguments": [
            "person"
          ],
          "description": "The person has a nationality",
          "verbalisation": "{0} has a nationality"
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
        "person_may_asylum": {
          "arguments": [
            "person"
          ],
          "description": "The person is permitted to seek as well as enjoy asylum from persecution in other countries. Source clause: the right to seek and to enjoy in other countries asylum from persecution.",
          "regulated": {
            "act": "{0} seek as well as enjoy asylum from persecution in other countries",
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
        "secure_asylum_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to grant the person asylum from persecution in other countries. Source clause: the right to seek and to enjoy in other countries asylum from persecution.",
          "regulated": {
            "act": "{0} grant {1} asylum from persecution in other countries",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_effective_remedy_required": {
          "arguments": [
            "bearer",
            "person_with_violated_rights"
          ],
          "description": "The bearer is required to provide the person an effective remedy by the competent national tribunals. Source clause: the right to an effective remedy by the competent national tribunals for acts violating the fundamental rights granted to the person by the constitution or by law.",
          "regulated": {
            "act": "{0} provide {1} an effective remedy by the competent national tribunals",
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
        "secure_fair_hearing_required": {
          "arguments": [
            "bearer",
            "person_in_determination"
          ],
          "description": "The bearer is required to give the person a fair public hearing by an independent impartial tribunal. Source clause: to be entitled in full equality to a fair and public hearing by an independent and impartial tribunal, in the determination of the person's rights and obligations and of any criminal charge against the person.",
          "regulated": {
            "act": "{0} give {1} a fair public hearing by an independent impartial tribunal",
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
        "secure_public_service_access_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to give the person equal access to public service in their own country. Source clause: the right of equal access to public service in the person's country.",
          "regulated": {
            "act": "{0} give {1} equal access to public service in their own country",
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
          "person",
          "person_in_determination",
          "person_with_violated_rights"
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
        "person_in_determination": {
          "description": "a person whose rights and obligations, or a criminal charge against whom, are being determined",
          "verbalisation": {
            "plural": "people in determination",
            "singular": "person in determination"
          }
        },
        "person_with_violated_rights": {
          "description": "a person whose fundamental rights granted by the constitution or by law are violated by an act",
          "verbalisation": {
            "plural": "people with violated rights",
            "singular": "person with violated rights"
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
        "what counts as persecution"
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
    }
  ],
  "reading_sets": [
    {
      "id": "rs_u022a",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "f3701a8014a4c782bb974b8a06a6d1f82f557977737aa80e2e223be4e99f7e47"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "aa22e28dc9d535af5627b7cbf3baeebef18d861dbc398d67a50f0f001e5a49bd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "d10297857687cf16d382e061fa49bfd037ed6ce55d92c86107c2d5754a465d41"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "62bbba4344a8d8df231f278e70aa3959595dccee0518fdc5eb6f0e2014ae6e22"
        }
      ],
      "status": "open",
      "unit": "u022a",
      "version": 1
    },
    {
      "id": "rs_u022b",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "4a5dc0ef0cacacd2773d0ef7adbf24cbafa4155d2f09c9b8c605bd5dd1dbec83"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "8feaf448c21d181420752e72603fdedd7a7b4ad75c792c66dc1b2e57af8b1b5a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "50ab37d33ac1c52622257bd1eb86779f1a40eb457cc839e3b32d94cff5355781"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "187d709de8d73613a694fdc4f70c1609c8b87bff60252c8ee867aa5072175e8e"
        }
      ],
      "status": "open",
      "unit": "u022b",
      "version": 1
    },
    {
      "id": "rs_u022c",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "857581c5fab08339e7d6ac742b307ad5be72862028f7b20a5491e87b3a44df0d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "d3478aead02ed6ecac7ab1d7f2171fac668a590318060c856c1313331ca09ff6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "90309eb43f9285ae63552102e321902e66473852ca7c61e7e083a26e76892c45"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "16724873d2d0cde33d6f68233421b1bce1ff610d659014b363ffd5a63ce3d4d3"
        }
      ],
      "status": "open",
      "unit": "u022c",
      "version": 1
    },
    {
      "id": "rs_u029",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "dbd44c14a2e681f849811bef93699b79f4b1fae78723076a5320637bb2bb1ad4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "26e5a77ce98eb11ce3b5750e00b8db10df8ed797ce955e4e6f47b8f75414560e"
        }
      ],
      "status": "open",
      "unit": "u029",
      "version": 1
    },
    {
      "id": "rs_u032",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "892b447f5b3f13a7972d040c2c0f2692d3dc09e636afe5e708d9d71ef732f454"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "cb6fecea44d7b9a113a1de2369d990dd747fa511aedab44897b4acdda46d2620"
        }
      ],
      "status": "open",
      "unit": "u032",
      "version": 1
    },
    {
      "id": "rs_u033a",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "e6822eb68ebbffd6bfc3095532625f215c298d9091a8c15fa0e7c4f28cb8b542"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "c34794d5f7f3da6ffaf7bd27d05bfe08f46a40229c64231be878e8ce0e2a6bc0"
        }
      ],
      "status": "open",
      "unit": "u033a",
      "version": 1
    },
    {
      "id": "rs_u033b",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "e82d0f7ef72484edeb919c775901110c76c7827c7d0dab4cd6de17066038f8a0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "25d08765fa7bea8dfdbf1815d456f5c577ea0923a82cf3349caddfa11e161f35"
        }
      ],
      "status": "open",
      "unit": "u033b",
      "version": 1
    },
    {
      "id": "rs_u035",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state must provide each holder (the holder sort person_with_violated_rights carries the scope in prose) an effective remedy by the competent national tribunals (the right's one duty; the source names no bearer, so this is the translator's candidate; 'by the competent national tribunals' makes the state the natural provider; the anyone reading is kept as the translator's wider candidate). Left out of the act phrase: the scope 'for acts violating the fundamental rights granted by the constitution or by law' is carried only by the description of the holder sort person_with_violated_rights (prose-scoped, not a checked clause)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person_with_violated_rights",
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
                    "name": "secure-effective-remedy-by-state",
                    "over": [],
                    "predicate": "secure_effective_remedy_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "effective-remedy"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "8b6d39d37dafe177e0243f86e5bed80a5d362f7371400393aaa56b3098dea5e9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must provide each holder (the holder sort person_with_violated_rights carries the scope in prose) an effective remedy by the competent national tribunals (the right's one duty; the source names no bearer, so this is the translator's candidate; 'by the competent national tribunals' makes the state the natural provider; the anyone reading is kept as the translator's wider candidate). Left out of the act phrase: the scope 'for acts violating the fundamental rights granted by the constitution or by law' is carried only by the description of the holder sort person_with_violated_rights (prose-scoped, not a checked clause)."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person_with_violated_rights",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-effective-remedy-by-anyone",
                    "over": [],
                    "predicate": "secure_effective_remedy_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "effective-remedy"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "1206e20e71b76a057082cd60cc01fde8ed939ac8872b9784910a603aa8030dd9"
        }
      ],
      "status": "open",
      "unit": "u035",
      "version": 1
    },
    {
      "id": "rs_u039",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder (the holder sort person_in_determination carries the scope in prose) a fair public hearing by an independent impartial tribunal (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'in full equality' (no slot: 88 bytes with it; named as the open term full_equality); 'in the determination of his rights and obligations and of any criminal charge against him' is carried only by the description of the holder sort person_in_determination (prose-scoped, not a checked clause); 'fair and public' and 'independent and impartial' shown without 'and'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person_in_determination",
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
                    "name": "secure-fair-and-public-hearing-by-state",
                    "over": [],
                    "predicate": "secure_fair_hearing_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "fair-and-public-hearing"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "928358168899c6b0fe7cbcd217286ba584d1135ecc5efa18572f9f6ff55f83ff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder (the holder sort person_in_determination carries the scope in prose) a fair public hearing by an independent impartial tribunal (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'in full equality' (no slot: 88 bytes with it; named as the open term full_equality); 'in the determination of his rights and obligations and of any criminal charge against him' is carried only by the description of the holder sort person_in_determination (prose-scoped, not a checked clause); 'fair and public' and 'independent and impartial' shown without 'and'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "person_in_determination",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-fair-and-public-hearing-by-anyone",
                    "over": [],
                    "predicate": "secure_fair_hearing_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "fair-and-public-hearing"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "be098a8e4265f574db3ded177c6288c43a6acad8cb858da6c781c453c8473fc3"
        }
      ],
      "status": "open",
      "unit": "u039",
      "version": 1
    },
    {
      "id": "rs_u046",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "eb4116196dcb60bfba381da233d93f238f88f53b0cc3e030d12309f11aff2407"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "8040a85abea8b18f1651e9d7b3fd7fdc4193e53b3a8f313b50e97836e6bd93d2"
        }
      ],
      "status": "open",
      "unit": "u046",
      "version": 1
    },
    {
      "id": "rs_u048",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "1aa616ac76c762d908eb0098356817e451678af6ae2142d35dda553c2eb9a810"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "7c0d699b0247a83c9716d765814cc3618f065ea72c8eb8e85673bd22fc3b27b5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "e44a6ef1e845d0857cc16b97a95c2236c4c7193d8c84c5b6afbabb1a223efad3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "9441e87759758ca769ac51e33d2850b9ab80c89a19bc1896fde64f1fb5b6d3fe"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "c4de486255be9d5b7967c50c1b282226261077a5f8ac7ccad7b719080850ff3b"
        }
      ],
      "status": "open",
      "unit": "u048",
      "version": 1
    },
    {
      "id": "rs_u049",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "68446bc69361523d90093ceb680c6475d25f0963cafb35562b0d8deba2772cb8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "1bd05dd14b32ead009d3cd656736bcda377a02f0540f538ce662de948e862ee5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "30b110e029ef97d9bb623ad8fa51ef6567e59a732879bb76710a49fddb7ac7a5"
        }
      ],
      "status": "open",
      "unit": "u049",
      "version": 1
    },
    {
      "id": "rs_u051",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from seeking as well as enjoying asylum in other countries (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'from persecution' in the avoiding duty (carried by 'asylum' and the open term persecution; the 80-byte limit forces a choice with 'in other countries'); 'seek' in the securing duty."
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
                    "name": "avoid-asylum-by-state",
                    "over": [],
                    "predicate": "avoid_asylum_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "asylum"
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
          "meaning_id": "1a5458c9ba585fe4ddbd6ec17909a416e86f04711898e58ea3d958f32040ed16"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'from persecution' in the avoiding duty (carried by 'asylum' and the open term persecution; the 80-byte limit forces a choice with 'in other countries'); 'seek' in the securing duty."
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
                    "name": "secure-asylum-by-state",
                    "over": [],
                    "predicate": "secure_asylum_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "asylum"
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
          "meaning_id": "0326602c721193a10c6dd23fe294d90ec6f7e6a532da94f240553e58091d1161"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from seeking as well as enjoying asylum in other countries (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'from persecution' in the avoiding duty (carried by 'asylum' and the open term persecution; the 80-byte limit forces a choice with 'in other countries'); 'seek' in the securing duty."
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
                    "name": "avoid-asylum-by-anyone",
                    "over": [],
                    "predicate": "avoid_asylum_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "asylum"
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
          "meaning_id": "8cf4af682ed917c9ad1319d20766be9b6ed62a58428cd5dd371e0537e27a9428"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'from persecution' in the avoiding duty (carried by 'asylum' and the open term persecution; the 80-byte limit forces a choice with 'in other countries'); 'seek' in the securing duty."
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
                    "name": "secure-asylum-by-anyone",
                    "over": [],
                    "predicate": "secure_asylum_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "asylum"
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
          "meaning_id": "7f0b4bb0c9debe60fd2bb24a804eb1b671011c1d0e9e23c455a8f091fe9ced11"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Liberty reading: every person may seek as well as enjoy asylum from persecution in other countries (the holder is permitted; no duty on anyone follows from this line)."
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
                    "name": "person-may-asylum",
                    "over": [],
                    "predicate": "person_may_asylum",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "asylum"
            }
          },
          "id": "liberty",
          "kind": "right",
          "labels": {
            "force": "strict",
            "incident": "liberty"
          },
          "meaning_id": "7db039f556ad1ea7065e234639c5b92232c951e1b4351bfa5b2be3767cc10912"
        }
      ],
      "status": "open",
      "unit": "u051",
      "version": 1
    },
    {
      "id": "rs_u063",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "d2cf163354868b8abba1de91bedab297097888af7ec4a7d184cfb92067326aa5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "b1ed572980f140a6d5cfabc5d81734b295bd9d509c77a6373acde660befd390e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "45bc4029789e712bdc5f9b087c074659ad2f27bc8c15677ccfb634997b6299e3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "b574981fbd705bb0bb77232bc272285200c55c845fd01c90998621cf9fffb476"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "1299beaf869f17e390f085ef0b36ec5d3f5b272866d7875f1e654052d76d3475"
        }
      ],
      "status": "open",
      "unit": "u063",
      "version": 1
    },
    {
      "id": "rs_u066",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "7ca9d5d5964f0a695964392d88b75f7db71e96c5f21370b3a59536b379dda55b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "3d070122f10903c0e52ef675823a7441a6625d6d55adc3fa0081f434ab547f8c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "9d73d15d3d7dd3a8db7d40de7ac684faa32455a4a7380a89c52026387a8b9ccb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "3f24e79652224459c45aef28be0a0b0e03392d9e16b545084929f20353edd4e7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "ad2ec32dff442b71154929dc727bfe4aed44814b86ffdf9a8e758cd7b05e571c"
        }
      ],
      "status": "open",
      "unit": "u066",
      "version": 1
    },
    {
      "id": "rs_u070",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "d2dfe63f9761b2d528dbff8de538b7f1deb4204ca9f57d9adb059c0c7ea6a375"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "491619e2a82dd6fdb4f339f456e58401e232c9c68157cb0c9a3e3d02ef600244"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "ee4077f38cc1d816467e8416dd6212c1cacfbc5063c9e37dada8eaf29b977ec7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "45264f168d63ab8525ca8fe6629e1c331900719cb266d988839be7ebf237bfad"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "2c278e069b9bd11279233400e091350894c91f2e4daa8c67b4e7eef8046818c2"
        }
      ],
      "status": "open",
      "unit": "u070",
      "version": 1
    },
    {
      "id": "rs_u073",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "986ff56b59a6df390767287a33305bb5135eb1852a56548e30874fc43f83ce03"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "85473322542fa6aa0334fa7dc2c55db55fab61d17a3e94e7f8c0f198b9614e2e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "7073210f141312819ba11f530583b909396a50d161da7ce98e074d19b6649e7f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "liberty": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "817472132ebdb2dc4dda78eb3bde017287c37cad95432ffea95ef1c281f6375d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "anyone_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_negative": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4",
              "state_positive": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
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
          "meaning_id": "4d116a8a8b537cea5df4cd0a11044e2f92cdf7ca760707625c9682d65db383aa"
        }
      ],
      "status": "open",
      "unit": "u073",
      "version": 1
    },
    {
      "id": "rs_u077",
      "models": {
        "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "grants_nationality": [],
            "has_a_nationality": [],
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
              "anyone_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder equal access to public service in their own country (the right's one duty; the source names no bearer, so this is the translator's candidate). "
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
                    "name": "secure-equal-access-to-public-service-by-state",
                    "over": [],
                    "predicate": "secure_public_service_access_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-access-to-public-service"
            }
          },
          "id": "state_claim",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "b91a42b9d734f29d6a03640a747afbb39609586a4a36c7d926b8770f894dc6ff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "4af741b9a5ffb4fb8ebef307d164ca7ebd37090658637e61bf4c6e461fea76f4"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder equal access to public service in their own country (the right's one duty; the source names no bearer, so this is the translator's candidate). "
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
                    "name": "secure-equal-access-to-public-service-by-anyone",
                    "over": [],
                    "predicate": "secure_public_service_access_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-access-to-public-service"
            }
          },
          "id": "anyone_claim",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "fdbaa817af9084b12a57533bffc3ae4719f618faf871095d25263612dec00a39"
        }
      ],
      "status": "open",
      "unit": "u077",
      "version": 1
    },
    {
      "id": "rs_u017",
      "models": {
        "87654e1318504c2f605993b66a395f4d95218e066ba020c055781b7995426a16": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "avoid_asylum_required": [],
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
            "grants_nationality": [],
            "has_a_nationality": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_asylum": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_asylum_required": [],
            "secure_effective_remedy_required": [],
            "secure_equal_protection_required": [],
            "secure_fair_hearing_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_public_service_access_required": [],
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
              "default": "87654e1318504c2f605993b66a395f4d95218e066ba020c055781b7995426a16"
            },
            "who": "translator",
            "why": "Article 1 'should' read as a strict obligation on every human being to act towards each other human being in a spirit of brotherhood (readings/u017.strict.ve.md)."
          },
          "content": null,
          "id": "strict",
          "kind": "norm",
          "meaning_id": "2c56fa86c37318cd98de4696764e694c87480bb422c45cda616091786923bac3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "strict": "87654e1318504c2f605993b66a395f4d95218e066ba020c055781b7995426a16"
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
        }
      ],
      "status": "open",
      "unit": "u017",
      "version": 2
    },
    {
      "id": "rs_u052",
      "models": {
        "1fd829efd4d75e6c32f5a7ae9a15474169452e9a445319d9390be38a50790971": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "avoid_asylum_required": [],
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
            "grants_nationality": [],
            "has_a_nationality": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_asylum": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_asylum_required": [],
            "secure_effective_remedy_required": [],
            "secure_equal_protection_required": [],
            "secure_fair_hearing_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_public_service_access_required": [],
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
              "case_excluded": "1fd829efd4d75e6c32f5a7ae9a15474169452e9a445319d9390be38a50790971"
            },
            "who": "translator",
            "why": "Article 14(2) read as a prohibition on invoking the asylum right in the case of an excluded prosecution: the norm ranges over (person, prosecution) pairs of the sort excluded_prosecution, so it bars the invocation in that case and nothing else (readings/u052.invocation_barred.ve.md)."
          },
          "content": null,
          "id": "invocation_barred",
          "kind": "norm",
          "meaning_id": "ec7b4286c37ce5ef1173dda4070b88fec673c7ed4d6ab4e99ee27c004f1d76b3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "invocation_barred": "1fd829efd4d75e6c32f5a7ae9a15474169452e9a445319d9390be38a50790971"
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
          "meaning_id": "01e8ec39f750a4a936f52982714b5eb7b4dea88d94838d8ecc71806d8f412f71"
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
        }
      ],
      "status": "open",
      "unit": "u052",
      "version": 3
    },
    {
      "id": "rs_u112",
      "models": {
        "b73561806b6bfe0d71b9fe2b063ee405187dc7c68a649351791b9765ec98e33d": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "avoid_asylum_required": [],
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
            "grants_nationality": [],
            "has_a_nationality": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_asylum": [],
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
            "secure_asylum_required": [],
            "secure_effective_remedy_required": [],
            "secure_equal_protection_required": [],
            "secure_fair_hearing_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_public_service_access_required": [],
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
              "exercise_unprotected": "b73561806b6bfe0d71b9fe2b063ee405187dc7c68a649351791b9765ec98e33d"
            },
            "who": "translator",
            "why": "Article 29(3) read as an unconditional prohibition on carrying out an exercise contrary to UN purposes and principles (readings/u112.exercise_prohibited.ve.md)."
          },
          "content": null,
          "id": "exercise_prohibited",
          "kind": "norm",
          "meaning_id": "6ceb92c97cc437e8ce32c3538e7c35395e6d6310aafb348dd73ea8c50011cf7d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "exercise_prohibited": "b73561806b6bfe0d71b9fe2b063ee405187dc7c68a649351791b9765ec98e33d"
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
          "meaning_id": "9f0724e1e9588aa00e773bafef427a3bbb9e3bdf8cd08c3095afb2b49b95ade1"
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
        }
      ],
      "status": "open",
      "unit": "u112",
      "version": 3
    },
    {
      "id": "rs_u114",
      "models": {
        "d2923ef657ca34d924d0b9274370d5aeeb0aa5cf67d14edbf42f90ff99518e50": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "avoid_asylum_required": [],
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
            "grants_nationality": [],
            "has_a_nationality": [],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_asylum": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_asylum_required": [],
            "secure_effective_remedy_required": [],
            "secure_equal_protection_required": [],
            "secure_fair_hearing_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_public_service_access_required": [],
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
              "no_implied_right": "d2923ef657ca34d924d0b9274370d5aeeb0aa5cf67d14edbf42f90ff99518e50"
            },
            "who": "translator",
            "why": "Article 30 read as a prohibition on interpreting the Declaration as implying, for any State, group or person, a right to destroy declared rights (readings/u114.interpretive_ban.ve.md)."
          },
          "content": null,
          "id": "interpretive_ban",
          "kind": "norm",
          "meaning_id": "43ede036d7830ea165274b71c96928bd8154135b35d1673c8219d4f952200f7f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "interpretive_ban": "d2923ef657ca34d924d0b9274370d5aeeb0aa5cf67d14edbf42f90ff99518e50"
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
          "meaning_id": "8fcd6350de22d29e2e0f1a7de6ed44dc895b45f95382f5bf82d55224a0a79c00"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "interpretive_bar"
          ],
          "reason": "null-content candidates rejected by the 2026-09-29 audit",
          "version": 1
        }
      ],
      "status": "open",
      "unit": "u114",
      "version": 2
    },
    {
      "id": "rs_u054",
      "models": {
        "7babb73ddb7093ba6c575c4e04f05c0924f6357306e0c4b5702e8ca885fc08f1": {
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
            "person_in_determination": [
              "p0"
            ],
            "person_with_violated_rights": [
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
            "avoid_asylum_required": [],
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
            "grants_nationality": [],
            "has_a_nationality": [
              [
                "p0"
              ]
            ],
            "is_state": [],
            "person_may_assembly_and_association": [],
            "person_may_asylum": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_asylum_required": [],
            "secure_effective_remedy_required": [],
            "secure_equal_protection_required": [],
            "secure_fair_hearing_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_public_service_access_required": [],
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
              "some_state_grants_each": "7babb73ddb7093ba6c575c4e04f05c0924f6357306e0c4b5702e8ca885fc08f1"
            },
            "who": "translator",
            "why": "Article 15(1) read as a statement that each person has some nationality (the right is read as fulfilled for everyone; no bearer is named)."
          },
          "content": [
            "forall",
            "person",
            [
              "unary",
              "has_a_nationality",
              [
                "var",
                0
              ]
            ]
          ],
          "id": "each_person_has_a_nationality",
          "kind": "asserted",
          "meaning_id": "64cb6f9bc83215680c43e7aaa3bef2413008fa2e99a50062d6e4f6acc58f2514"
        },
        {
          "admission": {
            "distinguishing_models": {
              "each_person_has_a_nationality": "7babb73ddb7093ba6c575c4e04f05c0924f6357306e0c4b5702e8ca885fc08f1"
            },
            "who": "translator",
            "why": "Article 15(1) read as a statement that for each person some state grants that person a nationality (one state discharges the right; which state is not stated)."
          },
          "content": [
            "forall",
            "person",
            [
              "exists",
              "bearer",
              [
                "and",
                [
                  "unary",
                  "is_state",
                  [
                    "var",
                    0
                  ]
                ],
                [
                  "binary",
                  "grants_nationality",
                  [
                    "var",
                    0
                  ],
                  [
                    "var",
                    1
                  ]
                ]
              ]
            ]
          ],
          "id": "some_state_grants_each",
          "kind": "asserted",
          "meaning_id": "cde09236ab0de3ad2bbd7039f2207a5b678336607ea8746a578d59088b5e5b24"
        }
      ],
      "status": "open",
      "unit": "u054",
      "version": 1
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
      "kind": "right",
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
      "kind": "right",
      "meaning": {
        "open": [
          "fair",
          "independent_and_impartial",
          "full_equality"
        ]
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
      "kind": "right",
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
      "kind": "asserted",
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
        "unformalised": "norms"
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
      "kind": "right",
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
        "unformalised": "norms"
      },
      "span": [
        10100,
        10218
      ],
      "support": "none"
    },
    {
      "content": {
        "limitation": {
          "conditions": [
            {
              "decided_by": null,
              "name": "determined_by_law",
              "role": "necessary",
              "verbalisation": "the limitation is determined by law"
            },
            {
              "decided_by": null,
              "name": "solely_for_permitted_purpose",
              "purposes": [
                "securing due recognition and respect for the rights and freedoms of others",
                "meeting the just requirements of morality, public order and the general welfare in a democratic society"
              ],
              "role": "necessary",
              "verbalisation": "the limitation is solely for a permitted purpose"
            }
          ],
          "decided_by": "unstated",
          "factors": [],
          "kinds": "all",
          "name": "limitation-29",
          "scope": "all"
        }
      },
      "id": "u111",
      "kind": "limitation",
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
