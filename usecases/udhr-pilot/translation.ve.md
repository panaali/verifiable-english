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
          "description": "The bearer is required to avoid barring the person from seeking as well as enjoying asylum from persecution. Source clause: the right to seek and to enjoy in other countries asylum from persecution.",
          "regulated": {
            "act": "{0} avoid barring {1} from seeking as well as enjoying asylum from persecution",
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
        "avoid_presumed_innocent_required": {
          "arguments": [
            "bearer",
            "charged_person"
          ],
          "description": "The bearer is required to avoid treating the person as guilty before guilt has been proved. Source clause: the right to be presumed innocent until proved guilty according to law in a public trial at which the person has had all the guarantees necessary for the defence of the person.",
          "regulated": {
            "act": "{0} avoid treating {1} as guilty before guilt has been proved",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_property_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from owning property. Source clause: the right to own property alone as well as in association with others.",
          "regulated": {
            "act": "{0} avoid barring {1} from owning property",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_protection_against_incitement_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid inciting discrimination against the person. Source clause: to be entitled to equal protection against any incitement to such discrimination.",
          "regulated": {
            "act": "{0} avoid inciting discrimination against {1}",
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
        "secure_presumed_innocent_required": {
          "arguments": [
            "bearer",
            "charged_person"
          ],
          "description": "The bearer is required to presume the person innocent until proved guilty according to law. Source clause: the right to be presumed innocent until proved guilty according to law in a public trial at which the person has had all the guarantees necessary for the defence of the person.",
          "regulated": {
            "act": "{0} presume {1} innocent until proved guilty according to law",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_property_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the ownership of property by the person. Source clause: the right to own property alone as well as in association with others.",
          "regulated": {
            "act": "{0} secure the ownership of property by {1}",
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
          "description": "The bearer is required to protect the person equally against incitement to discrimination. Source clause: to be entitled to equal protection against any incitement to such discrimination.",
          "regulated": {
            "act": "{0} protect {1} equally against incitement to discrimination",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_protection_against_interference_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the person by law against arbitrary interference. Source clause: the right to the protection of the law against arbitrary interference with privacy, family, home or correspondence and against attacks upon honour and reputation.",
          "regulated": {
            "act": "{0} protect {1} by law against arbitrary interference",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_public_service_access_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to give the person equal access to public service. Source clause: the right of equal access to public service in the person's country.",
          "regulated": {
            "act": "{0} give {1} equal access to public service",
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
          "charged_person",
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
        "charged_person": {
          "description": "a person charged with a penal offence",
          "verbalisation": {
            "plural": "charged people",
            "singular": "charged person"
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
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "70e2d0e9ee4f1cc5318e28e879b1d168d966b2e15b6534f3bf63c0d8550042ad"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "3b200e09c4f40921d5dcb4a857b6114d3d56e4b0fc11b36de1d7c0d7f2495a34"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "fe0db0228939b5a18bf10f9c3037831c229f239ecfbf565c03bcee3070a8a5fc"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "ea399d5c8406192407eee7c9cf8022ec362af366015496a975758fe18b725a03"
        }
      ],
      "status": "open",
      "unit": "u022a",
      "version": 1
    },
    {
      "id": "rs_u022b",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "e61ef2cac16e5961f3db54f037a78009c5ce6f229fb599a3190b4d4a244a21b9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "d94736d8c2b67d1e90489ecfc08767bf37f2abf218c2bd2a640614f8dc097be4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "5f4ce3ee93e683103632f44cd335e1bb0bc2a7e153bea6346e723bab219fab62"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "dce7b395effb14350edba6ed8fdb9e6ed8ebdbecf5900309c9597c6d41cab401"
        }
      ],
      "status": "open",
      "unit": "u022b",
      "version": 1
    },
    {
      "id": "rs_u022c",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "b8cc382ca7828fe8758ff48f7be7497261607ba36f0c8f09511aa606f050e2d1"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "dc36efa5235ea1e08ce2a08eafdf10728fee512747cae8137362a81b79f13563"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "0fd38dc16d169a96c669684caf6f4c43c6993dc7076019fb984d78866b49025a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "1e59ddbafde0008aac0e62c85463db8aeb1b071060d178a3f1ddc49f0b5dc793"
        }
      ],
      "status": "open",
      "unit": "u022c",
      "version": 1
    },
    {
      "id": "rs_u029",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "ea320332cae0c68fd1a5a3fe6486c9b9561802684f8d66bbb2ed972b86aa9da8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "fcf91fb661aceddde3c9682233dd004a83467f31e805e9f5319ffd5b0251c780"
        }
      ],
      "status": "open",
      "unit": "u029",
      "version": 1
    },
    {
      "id": "rs_u032",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "3e359444a6c057adc29a75c1cb8ffea0177a8b344dc1b30085211a7666bca5b6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "867ccb4dfaab9e8d6a9439a6f70cd575e2c3406ca22ea085618aaa0f1de2e007"
        }
      ],
      "status": "open",
      "unit": "u032",
      "version": 1
    },
    {
      "id": "rs_u033a",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "f01d92acf57b811d4da6aead267038ae07671cf177dad6670888457f494f2e51"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "f48ebcd9a11923fb42df099181fe0c92b84d1203a4acb6301f14c0d5e272834e"
        }
      ],
      "status": "open",
      "unit": "u033a",
      "version": 1
    },
    {
      "id": "rs_u033b",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid inciting discrimination against each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'such': read as discrimination in violation of this Declaration (u033a)."
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
                    "name": "avoid-protection-against-incitement-by-state",
                    "over": [],
                    "predicate": "avoid_protection_against_incitement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-incitement"
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
          "meaning_id": "75247ee1342c92f0075c50b8f66b594541bc771f4f38c0a694211a1776bb7e8f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder equally against incitement to discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'such': read as discrimination in violation of this Declaration (u033a)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "69235efe3a0f9c93b6ed41fbb729368a5360dad6c1b1c8300b8372ad628244f5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid inciting discrimination against each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'such': read as discrimination in violation of this Declaration (u033a)."
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
                    "name": "avoid-protection-against-incitement-by-anyone",
                    "over": [],
                    "predicate": "avoid_protection_against_incitement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-incitement"
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
          "meaning_id": "c1b51d89759859b6dc78cc58a6457531ffe5997692f7531b3885014096157298"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder equally against incitement to discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'such': read as discrimination in violation of this Declaration (u033a)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "7c65712172a0a3e38357dc15f2bd72aabbd4e31fddb22087749589700100b394"
        }
      ],
      "status": "open",
      "unit": "u033b",
      "version": 1
    },
    {
      "id": "rs_u035",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "e9b0501e519b05e8d7b4f500ed01a4648c65b04f4100eaf1dfd4ff453ee494c4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "c58e2bd9740093a3d341b8564ac3546759e97147db0f62b582babfa46ddf403b"
        }
      ],
      "status": "open",
      "unit": "u035",
      "version": 1
    },
    {
      "id": "rs_u039",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "b79251ff0d13a7050cf84fd7f4d3a8cf739246459098e85afdaab5bedd4d2137"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "f4c50f003cff758777e368f400655181acdb065e65905f3497336f83bfb35a32"
        }
      ],
      "status": "open",
      "unit": "u039",
      "version": 1
    },
    {
      "id": "rs_u041",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid treating each holder (the holder sort charged_person carries the scope in prose) as guilty before guilt has been proved (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in a public trial at which he has had all the guarantees necessary for his defence'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "charged_person",
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
                    "name": "avoid-presumption-of-innocence-by-state",
                    "over": [],
                    "predicate": "avoid_presumed_innocent_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "presumption-of-innocence"
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
          "meaning_id": "9b4f3f89b4b580492729efe46c7a521e952eb99618a4ebd6ffa4fd97a9e4df12"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must presume each holder (the holder sort charged_person carries the scope in prose) innocent until proved guilty according to law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in a public trial at which he has had all the guarantees necessary for his defence'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "charged_person",
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
                    "name": "secure-presumption-of-innocence-by-state",
                    "over": [],
                    "predicate": "secure_presumed_innocent_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "presumption-of-innocence"
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
          "meaning_id": "94994eec0329ea1d2f5a5e3a0beab0bca6f06f588801726b2c80a33be9b7f0a8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid treating each holder (the holder sort charged_person carries the scope in prose) as guilty before guilt has been proved (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in a public trial at which he has had all the guarantees necessary for his defence'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "charged_person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "avoid-presumption-of-innocence-by-anyone",
                    "over": [],
                    "predicate": "avoid_presumed_innocent_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "presumption-of-innocence"
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
          "meaning_id": "d2a1df18df01b59e23593f7a20f1aa7980ac9c5e23f1c7872e31e5bc7734dc02"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must presume each holder (the holder sort charged_person carries the scope in prose) innocent until proved guilty according to law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in a public trial at which he has had all the guarantees necessary for his defence'."
          },
          "content": {
            "right": {
              "guard": [
                "top"
              ],
              "holder": "charged_person",
              "lines": [
                {
                  "cites": {},
                  "holder_slot": null,
                  "kind": "claim",
                  "norm": {
                    "guard": [
                      "top"
                    ],
                    "name": "secure-presumption-of-innocence-by-anyone",
                    "over": [],
                    "predicate": "secure_presumed_innocent_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "presumption-of-innocence"
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
          "meaning_id": "449d1eb5d8e50094a7e6b9838a3000e8ab58a5169f5f28f1d347450347763f98"
        }
      ],
      "status": "open",
      "unit": "u041",
      "version": 1
    },
    {
      "id": "rs_u046",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder by law against arbitrary interference (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: the objects of the interference (privacy, family, home, correspondence) and the attacks upon honour and reputation ('such interference or attacks' is read from u045a and u045b)."
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
          "meaning_id": "92b69e62142ef810afa74f5b4f22e45d44de2f9a27cc17d857c64d099db9b6ff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder by law against arbitrary interference (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: the objects of the interference (privacy, family, home, correspondence) and the attacks upon honour and reputation ('such interference or attacks' is read from u045a and u045b)."
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
          "meaning_id": "7fb5309ff471bf4eac5fa8a450e9ac99f358c524500dee2b53c4d1785326dfc6"
        }
      ],
      "status": "open",
      "unit": "u046",
      "version": 1
    },
    {
      "id": "rs_u048",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "3e2572db11274eb3c275764c7ef751654845433b45885da8cbd3852f6aa2d471"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "b71834ba1cd5e4c7edc53cc08bf93ed57a1034b0517c7fe823ab6d9fca9b0b7d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "be1147c682658af958d1d2dcfb404c1720d30cd268409e28b7cdb83f40361616"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "1b7523ff0bb9e0a4a96945ab9f4a97cec4eb2c33977e8110b7586a51c05e624a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "79746fdfb3e778fb96d69b78f5a23ca192c8598e42bc62ddac8dbc0a6673d553"
        }
      ],
      "status": "open",
      "unit": "u048",
      "version": 1
    },
    {
      "id": "rs_u049",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "a244e2e557f8e6cfcd9dce32a353b3bd4950141f1196ed3bbb4199478f447685"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "4bbb59d336af1c0e34640cd5b21df1207cbfba70809ff300085970644266bdcd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "4664bd6cdc20249f6826e73c11f27ee6179e9e31a4efe0f0145f3f5beebf14a8"
        }
      ],
      "status": "open",
      "unit": "u049",
      "version": 1
    },
    {
      "id": "rs_u051",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from seeking as well as enjoying asylum from persecution (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in other countries' in the avoiding duty; 'seek' in the securing duty."
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
          "meaning_id": "118515fe7b7232e683b01488e828e4d4c3f024eb45a4cb42dace4aa3e1fe5c76"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in other countries' in the avoiding duty; 'seek' in the securing duty."
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
          "meaning_id": "e0164c0b6542638b176cb066ba4980e92a6dfaf1c4d7fea43be2d371102d6de6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from seeking as well as enjoying asylum from persecution (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in other countries' in the avoiding duty; 'seek' in the securing duty."
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
          "meaning_id": "df169902f407b2fffd32d5ac649acc265677cd442887de70c667a92b15440855"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'in other countries' in the avoiding duty; 'seek' in the securing duty."
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
          "meaning_id": "b924fab6f151ff3a33df54ff87ce2df33450d25909c992c31e1ca8c4969c2ebc"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "1bce017e59694585e49d5615b59161e128ccfbe810f4f7bf5176c7c9c92ccee8"
        }
      ],
      "status": "open",
      "unit": "u051",
      "version": 1
    },
    {
      "id": "rs_u063",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from owning property (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'alone as well as in association with others' in the two duties."
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
          "meaning_id": "cb0e88a77d6f82bae14c75b65bec66cfff110672115c06d15b85a414e9b43e4e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure the ownership of property by each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'alone as well as in association with others' in the two duties."
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
          "meaning_id": "59f46282d611dfd927253f390dffb130fe60bd3ed222f33d608cf29b70d681f5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from owning property (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'alone as well as in association with others' in the two duties."
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
          "meaning_id": "e4d01ed1040fa54edfab50cc447124c38ef4db9fc31fd31fed762a206144ff31"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure the ownership of property by each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate). Left out of the act phrase: 'alone as well as in association with others' in the two duties."
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
          "meaning_id": "9f928f7c58afb15b54ce53725b7595cf99e0695de1bf5212a5b40965b76f5747"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "c83eefdd76a2ef20fb7ed974916a8e449bb65414e63a7f9302ca488a087b7ac4"
        }
      ],
      "status": "open",
      "unit": "u063",
      "version": 1
    },
    {
      "id": "rs_u066",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "04be5750c33e6913944ffb154c7e34b330e8ae8373f4e447ecb6fdf811a8caff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "61fae6d9e5c29f6c98331447405d1f1d601b10d7c06fafdbd6c0c3a1d6325bda"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "70d44271dd34df8493ef565225a3fbc36cc2c8d63aa97e2fb52aaa009abf4b81"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "1fd3b7c0ca3830adb0c89a5ef508890923ce63643e27a5eb1bb85ed424b839a2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "305901d44f94af84cc827c2718fa1159107798e7f9f44b72022a76659696e640"
        }
      ],
      "status": "open",
      "unit": "u066",
      "version": 1
    },
    {
      "id": "rs_u070",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "3ae0c5140c605d8548f548464113ed0ce9196d5db2257ba2679f588ff30caebd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "d23a645ddc439635fdd4605fdd18a2939dee0c2e261f6fc539e1722cb91fdbb2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "0e219a098f22cc423a24902b39906459ed57a9d9c00432f95ec887366d9cb53b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "e120e33998a0999ca060b1d65d769597e7f9cb221a3b2df9db61519e5947b451"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "a9606f992612088c5401ce9061af09b6425c25211bd84ba3e6196a27da26c072"
        }
      ],
      "status": "open",
      "unit": "u070",
      "version": 1
    },
    {
      "id": "rs_u073",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "646fe85f71818343b6aef314deb4def3720002e7c6215be50d1bde2790a0241a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "b381a06eb51f8f0df343b9256a28a1c07a9c5b8b927c6ed496befc6a1308e1f4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "7dd88d2d38d1ed50dbb62e83a8e2a9e9410295edab4b468ec3b33e7c3ffbb47a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "liberty": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "8a87cb4d8b6816bd88a514f2747c7f6139064d2a865865e6184448c3a245e6ab"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "anyone_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_negative": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220",
              "state_positive": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
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
          "meaning_id": "53b7f07fcaa0b2fe1491e9baaa42d968fd87ed7b98e1ec3f31c024f09f97bc0f"
        }
      ],
      "status": "open",
      "unit": "u073",
      "version": 1
    },
    {
      "id": "rs_u077",
      "models": {
        "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220": {
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
            "charged_person": [
              "c0"
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
              "anyone_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder equal access to public service (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'in his country'."
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
          "meaning_id": "710973d80d3a2377f5b95f331aa9e45a7ca91b09a57fc4bc491262b70968615b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "a2cba5d2d78898ac202974f0ffb8521fcddfd221923526c02575419dcd7c6220"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder equal access to public service (the right's one duty; the source names no bearer, so this is the translator's candidate). Left out of the act phrase: 'in his country'."
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
          "meaning_id": "3ddae59da6d664f9aa5d131af5ae2b14b9e245f0ffb1716ca1458720265200e8"
        }
      ],
      "status": "open",
      "unit": "u077",
      "version": 1
    },
    {
      "id": "rs_u017",
      "models": {
        "0173d37afbac0fa3e3017dbc1552eadf65f7cdf888ac5f621c20d7e8b2b01f67": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "charged_person": [
              "c0"
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
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_incitement_required": [],
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
            "secure_presumed_innocent_required": [],
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
              "default": "0173d37afbac0fa3e3017dbc1552eadf65f7cdf888ac5f621c20d7e8b2b01f67"
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
              "strict": "0173d37afbac0fa3e3017dbc1552eadf65f7cdf888ac5f621c20d7e8b2b01f67"
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
        "af40f5b676bb47391e1666a1441edec4f0e64862917fe792f79c813d7af2f817": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "charged_person": [
              "c0"
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
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_incitement_required": [],
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
            "secure_presumed_innocent_required": [],
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
              "case_excluded": "af40f5b676bb47391e1666a1441edec4f0e64862917fe792f79c813d7af2f817"
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
              "invocation_barred": "af40f5b676bb47391e1666a1441edec4f0e64862917fe792f79c813d7af2f817"
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
          "meaning_id": "e70aa5d9a6560329afb949f77df1f05a37ff245d530b8a10561c684660a3159e"
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
        "d58f486c2a9020f03cea12f6d65d127d1b7082e9320add622b7668cd3ee20b8c": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "charged_person": [
              "c0"
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
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_incitement_required": [],
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
            "secure_presumed_innocent_required": [],
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
              "exercise_unprotected": "d58f486c2a9020f03cea12f6d65d127d1b7082e9320add622b7668cd3ee20b8c"
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
              "exercise_prohibited": "d58f486c2a9020f03cea12f6d65d127d1b7082e9320add622b7668cd3ee20b8c"
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
          "meaning_id": "04d90df1ef3d5cebebe308244e01f637b0d2aca29a1fae4927941cd2c9234680"
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
        "1ed89508e6b7de6ff0fbdad80b26e488a57676204d797f266202cbef9404ced9": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "charged_person": [
              "c0"
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
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_incitement_required": [],
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
            "secure_presumed_innocent_required": [],
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
              "no_implied_right": "1ed89508e6b7de6ff0fbdad80b26e488a57676204d797f266202cbef9404ced9"
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
              "interpretive_ban": "1ed89508e6b7de6ff0fbdad80b26e488a57676204d797f266202cbef9404ced9"
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
          "meaning_id": "2d632247af65bba856caa3b8be33796dc3cee7e3296a74b1705d9bc76575ba07"
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
        "2526487525d380439d3783ecf3d7c11db677ed7b4c9d8d4cb261a8f61d372284": {
          "complete": true,
          "constants": {},
          "domains": {
            "actor": [
              "a0"
            ],
            "bearer": [
              "b0"
            ],
            "charged_person": [
              "c0"
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
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_incitement_required": [],
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
            "secure_presumed_innocent_required": [],
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
              "some_state_grants_each": "2526487525d380439d3783ecf3d7c11db677ed7b4c9d8d4cb261a8f61d372284"
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
          "meaning_id": "c496a98f946e8275776a168db87f8773ba663cd994f3f3eaf8db2aad5bc3f2d7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "each_person_has_a_nationality": "2526487525d380439d3783ecf3d7c11db677ed7b4c9d8d4cb261a8f61d372284"
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
          "meaning_id": "92da9064dc9e54f0b66332aa8c1946ff5c491ed7e7a38e6e48e03a067db37a03"
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
      "kind": "right",
      "meaning": {
        "open": [
          "guarantees_necessary_for_defence"
        ]
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
