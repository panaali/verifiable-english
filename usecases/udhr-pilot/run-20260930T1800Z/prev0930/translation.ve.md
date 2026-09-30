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
        "avoid_effective_remedy_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person an effective remedy by the competent national tribunals. Source clause: the right to an effective remedy by the competent national tribunals for acts violating the fundamental rights granted to the person by the constitution or by law.",
          "regulated": {
            "act": "{0} avoid denying {1} an effective remedy by the competent national tribunals",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_equal_protection_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person equal protection of the law. Source clause: to be entitled without any discrimination to equal protection of the law.",
          "regulated": {
            "act": "{0} avoid denying {1} equal protection of the law",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_fair_hearing_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person a fair public hearing. Source clause: to be entitled in full equality to a fair and public hearing by an independent and impartial tribunal, in the determination of the person's rights and obligations and of any criminal charge against the person.",
          "regulated": {
            "act": "{0} avoid denying {1} a fair public hearing",
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
        "avoid_nationality_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid refusing the person a nationality. Source clause: the right to a nationality.",
          "regulated": {
            "act": "{0} avoid refusing {1} a nationality",
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
        "avoid_protection_against_discrimination_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid exposing the person to discrimination in violation of this Declaration. Source clause: to be entitled to equal protection against any discrimination in violation of this Declaration.",
          "regulated": {
            "act": "{0} avoid exposing {1} to discrimination in violation of this Declaration",
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
        "avoid_protection_against_interference_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person protection by law against arbitrary interference. Source clause: the right to the protection of the law against arbitrary interference with privacy, family, home or correspondence and against attacks upon honour and reputation.",
          "regulated": {
            "act": "{0} avoid denying {1} protection by law against arbitrary interference",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_public_service_access_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid denying the person equal access to public service. Source clause: the right of equal access to public service in the person's country.",
          "regulated": {
            "act": "{0} avoid denying {1} equal access to public service",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_recognition_as_person_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid refusing the person recognition as a person before the law. Source clause: the right to recognition everywhere as a person before the law.",
          "regulated": {
            "act": "{0} avoid refusing {1} recognition as a person before the law",
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
          "description": "The bearer is a state"
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
            "person"
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
            "person"
          ],
          "description": "The bearer is required to give the person a fair public hearing by an independent impartial tribunal. Source clause: to be entitled in full equality to a fair and public hearing by an independent and impartial tribunal, in the determination of the person's rights and obligations and of any criminal charge against the person.",
          "regulated": {
            "act": "{0} give {1} a fair public hearing by an independent impartial tribunal",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_leave_and_return_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to allow the person to leave any country as well as return to their own country. Source clause: the right to leave any country, including the person's own, and to return to the person's country.",
          "regulated": {
            "act": "{0} allow {1} to leave any country as well as return to their own country",
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
        "secure_nationality_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to grant the person a nationality. Source clause: the right to a nationality.",
          "regulated": {
            "act": "{0} grant {1} a nationality",
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
          "person",
          "charged_person"
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
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid depriving each holder of life (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "178cac08796e6673742192025d396dd273967714697e708d1e163f717b5a6811"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect the life of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "16c02b4854eddd768ba4a9b013984857e57c5eb3e6a24d7907a94a1f66e9191a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid depriving each holder of life (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "a4d564ba7017361c18ca1a6603ccb9e827ea4422364244ac7156e1ba164b6d68"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect the life of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "607381858e968b8d08ff0dd621a1eb89433727d14a5de13e50451d4c2e8bdf65"
        }
      ],
      "status": "open",
      "unit": "u022a",
      "version": 1
    },
    {
      "id": "rs_u022b",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid depriving each holder of liberty (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "d55c738cf0e1e24057a5c82183433362a8fbb568ea6dcf4bbc207a863ec31e20"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure the liberty of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "ae1a842080e0a37bba9b410012ef001d3d8fb1f3a52707030da0219d90c71f4f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid depriving each holder of liberty (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "a2f69e9d26fd3592a7e50a8bd91a8887cef42fb35115af3404c849d9e35f41d3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure the liberty of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "a271f1463357bd9808fba7091d57e2ad68a9fcda05a0790cc6eea4a3d52a3ff2"
        }
      ],
      "status": "open",
      "unit": "u022b",
      "version": 1
    },
    {
      "id": "rs_u022c",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid endangering the security of the person of each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "391cc05312526caeca966133c345047e8776f3f45fccdc980a43c10dadcf8a42"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must safeguard the security of the person of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "0d9eadb98816565c90ca9199fc972ec2a3b6c307061ee1d31470d7e5dfb01d1a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid endangering the security of the person of each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "b2dbfe2c9ceec8aa999b836894c2c0ef011975acf3e14f90cd27d7206b4ad51f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must safeguard the security of the person of each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "0eada52c041bcf63f850f112e550bd5189606db6395cd39c2181164d4c4bf138"
        }
      ],
      "status": "open",
      "unit": "u022c",
      "version": 1
    },
    {
      "id": "rs_u029",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid refusing each holder recognition as a person before the law (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-recognition-as-a-person-by-state",
                    "over": [],
                    "predicate": "avoid_recognition_as_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "recognition-as-a-person"
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
          "meaning_id": "b9824abcc60b1bd4fa5789ea76f23f284a202eece1682641bf45340a546afe49"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must recognise each holder everywhere as a person before the law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "8cae90d1bcc6ab466877b0484936d86fd2dc60b3e178d5aa3d483293ad602c27"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid refusing each holder recognition as a person before the law (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-recognition-as-a-person-by-anyone",
                    "over": [],
                    "predicate": "avoid_recognition_as_person_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "recognition-as-a-person"
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
          "meaning_id": "bc903a2c9226bceb731353053cbce662faed2e946b2e6e83cd307f12fc92a791"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must recognise each holder everywhere as a person before the law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "69bc909e5ea5ededd18be315ca52e3496932bf100c5895ce080f06c8dcd7532e"
        }
      ],
      "status": "open",
      "unit": "u029",
      "version": 1
    },
    {
      "id": "rs_u032",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder equal protection of the law (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-equal-protection-of-the-law-by-state",
                    "over": [],
                    "predicate": "avoid_equal_protection_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-protection-of-the-law"
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
          "meaning_id": "6f71b2b950e5ff67bc4107e18b9aea7adc4ac8b03f03b030a5f1fbc53ba49c78"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder equal protection of the law without any discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "727c0fca6e03bfef6bcfc95f166ff028b6a3af422fe33ec2416a88cba6aa9080"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder equal protection of the law (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-equal-protection-of-the-law-by-anyone",
                    "over": [],
                    "predicate": "avoid_equal_protection_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-protection-of-the-law"
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
          "meaning_id": "67eb261581ca9b14a8979b2215650bad385322f1c227770b03fd67b6a0a452dc"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder equal protection of the law without any discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "fbd6ed995845d75d590cc563c949edcaeac495ce11c4b7b518a329eff0dff58c"
        }
      ],
      "status": "open",
      "unit": "u032",
      "version": 1
    },
    {
      "id": "rs_u033a",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid exposing each holder to discrimination in violation of this Declaration (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-protection-against-discrimination-by-state",
                    "over": [],
                    "predicate": "avoid_protection_against_discrimination_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-discrimination"
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
          "meaning_id": "e517c1b6aa55e6d3338ce2a919ee0afc5c31e6a3b0db07bc7e9f57d07d01eeca"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder equally against discrimination in violation of this Declaration (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "260a7d17a8589b95a69575014b98d4f5708560f47eae070be5663bb72b6b5657"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid exposing each holder to discrimination in violation of this Declaration (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-protection-against-discrimination-by-anyone",
                    "over": [],
                    "predicate": "avoid_protection_against_discrimination_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-against-discrimination"
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
          "meaning_id": "423c32c99f77415bfa3c3cfbe273144fdc18618d3585bb1f2c3ba7274849f30f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder equally against discrimination in violation of this Declaration (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "5a791af0242cf5a5e223a4788df269fe99e57ccb03268751cf94be198d4555ce"
        }
      ],
      "status": "open",
      "unit": "u033a",
      "version": 1
    },
    {
      "id": "rs_u033b",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid inciting discrimination against each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "2c2359c5cb12d0baa3d4cae5785361f9640992070a70cb73242e80c104379284"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder equally against incitement to discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "dd6c2e968021e2948fc92eb4b4eccf2e6bb972108c3784f71dd7276ceb674ee4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid inciting discrimination against each holder (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "49a58098b1ae1116dc52dd0e5a8827f33ffed783e2106cc4df35a6aa763fe388"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder equally against incitement to discrimination (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "7d09e2c548b52a56dc47f886a0f0f0c3c4d57df160b179f67a4d69d24061d1e8"
        }
      ],
      "status": "open",
      "unit": "u033b",
      "version": 1
    },
    {
      "id": "rs_u035",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder an effective remedy by the competent national tribunals (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate; 'by the competent national tribunals' names the state's tribunals as the provider)."
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
                    "name": "avoid-effective-remedy-by-state",
                    "over": [],
                    "predicate": "avoid_effective_remedy_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "effective-remedy"
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
          "meaning_id": "09b324f5e662577db8bd3111299669c608b6c1f6c51cafa176757b93ff4045d0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must provide each holder an effective remedy by the competent national tribunals (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate; 'by the competent national tribunals' names the state's tribunals as the provider)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "d312d7395d6574e7e8fc339d2779039ccca38b18b36f16971ffc5c9fc8dfc4d3"
        }
      ],
      "status": "open",
      "unit": "u035",
      "version": 1
    },
    {
      "id": "rs_u039",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder a fair public hearing (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-fair-and-public-hearing-by-state",
                    "over": [],
                    "predicate": "avoid_fair_hearing_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "fair-and-public-hearing"
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
          "meaning_id": "f03e30bdbf56c07b3410e54d2bf375b73861d94fd3c7078ff7efda18c84da377"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder a fair public hearing by an independent impartial tribunal (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "2a49b217dc17a262f8e89d3ae5f3793a3c3cbb99f85e2e458641ecf355da4b70"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder a fair public hearing (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-fair-and-public-hearing-by-anyone",
                    "over": [],
                    "predicate": "avoid_fair_hearing_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "fair-and-public-hearing"
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
          "meaning_id": "10228288e801102d8ec74240188b9286f995e1e21085ad5183b9dec9676f3ada"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder a fair public hearing by an independent impartial tribunal (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "973d236838c57d3b423c8d6a88672bd34dd2027ed483d35ec449d70d691f8629"
        }
      ],
      "status": "open",
      "unit": "u039",
      "version": 1
    },
    {
      "id": "rs_u041",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid treating each holder as guilty before guilt has been proved (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "bd0b6428d44840108047b615b580354be25b02c5f4ff5afe048ec551c0186679"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must presume each holder innocent until proved guilty according to law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "ed70ba80eef4596fec807ee582967860ad1fda4bcc0646f648879d8d79c83321"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid treating each holder as guilty before guilt has been proved (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "d9454447cfe3fa84d21c20ebbe415d30c76ef977e15e7c57e20d3f2b441f6ef9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must presume each holder innocent until proved guilty according to law (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "56f003fb83df970dd27b9e7f7ee00f4354dc1101a2a4daf5d26c669d1e1374dd"
        }
      ],
      "status": "open",
      "unit": "u041",
      "version": 1
    },
    {
      "id": "rs_u046",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder protection by law against arbitrary interference (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-protection-of-the-law-against-interference-by-state",
                    "over": [],
                    "predicate": "avoid_protection_against_interference_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-of-the-law-against-interference"
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
          "meaning_id": "5a2f35ec1757c5d99233d22930d2acb8562481fcf9371aa3cbd8cd4f8319a3d1"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must protect each holder by law against arbitrary interference (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "cace3349088cf14f840036620164049c5654e7d5faa2d24a30a0930c05bcce60"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder protection by law against arbitrary interference (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-protection-of-the-law-against-interference-by-anyone",
                    "over": [],
                    "predicate": "avoid_protection_against_interference_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "protection-of-the-law-against-interference"
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
          "meaning_id": "51dba9b095d661f0a9dec59f5c98f15da8ce9c8f2bef3fb9ec74e062ea56ab7e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must protect each holder by law against arbitrary interference (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "1aa80c9ae1f8de4d78a211c851f91ecb548eb0b20be508828f94d20c2e71e98c"
        }
      ],
      "status": "open",
      "unit": "u046",
      "version": 1
    },
    {
      "id": "rs_u048",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of movement as well as residence within each state (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "b1baece0f295f029db206096f9ec6d9ec7bd39aff3f3bb1e2853bd7259683d37"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of movement as well as residence within each state (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "37461664022df2866a95f1ff88805be3b3165ab9260418b749b45590d0f1192b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of movement as well as residence within each state (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "e5a6db0873b42fbbacd4e56a2e2c46a11fb6081e65d7a70e4f84127e1ae95e40"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of movement as well as residence within each state (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "790596013a4877f757d2612b32c8db8d02e7d5b8e998683c04c014ba34b561fb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "c2bbbcb2cb54d9205a1a4163f985ad927a39d3f58e3a8087d6bf59170455004e"
        }
      ],
      "status": "open",
      "unit": "u048",
      "version": 1
    },
    {
      "id": "rs_u049",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from leaving any country as well as returning to their own (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_negative",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "e1bdad9d608c54b17f4a505e8dbc58c7edfd96ec6e5068031f0b1ce28c9bf236"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must allow each holder to leave any country as well as return to their own country (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "secure-freedom-to-leave-and-return-by-state",
                    "over": [],
                    "predicate": "secure_leave_and_return_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-to-leave-and-return"
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
          "meaning_id": "09a1b2ca6b6d5164352739196c9f8304191837ff829698c9c2204aad3f76b948"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from leaving any country as well as returning to their own (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_negative",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "68df7ce5e36e7affeb3d81ab2cfeb716f8205ba9ae68946a46461f5bc688c0ee"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must allow each holder to leave any country as well as return to their own country (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "secure-freedom-to-leave-and-return-by-anyone",
                    "over": [],
                    "predicate": "secure_leave_and_return_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "freedom-to-leave-and-return"
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
          "meaning_id": "ffe009c74cfcb89974d1584a8b2354e1a1f1f2f1496b22ee82e00a7487237f23"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "48172cbdb48db1aa0e1109d956de496fdc0cb24705d7e96bd545937ab76371f7"
        }
      ],
      "status": "open",
      "unit": "u049",
      "version": 1
    },
    {
      "id": "rs_u051",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from seeking as well as enjoying asylum from persecution (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "2c698ca348f9260273a6ea85d6eb9e7bdd19bcbbecf0c4183584caada2c1fac3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "eb305a8264e58b054bd95b0475a93e1390da53d0f46387837eac7456da8d4cd0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from seeking as well as enjoying asylum from persecution (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "29d88f57321ace8a4f6d2a82182d8d615bcb74b0ee52fe9d1e648422184dcbe5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must grant each holder asylum from persecution in other countries (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "20284cfb1d0c6f70103678d6403ee53c464176adaee47997ba662211cd109439"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "9c8042ffcce3e1710cc62dd778b69874eace10bb9d039241635fce575373aaef"
        }
      ],
      "status": "open",
      "unit": "u051",
      "version": 1
    },
    {
      "id": "rs_u054",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid refusing each holder a nationality (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-nationality-by-state",
                    "over": [],
                    "predicate": "avoid_nationality_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "nationality"
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
          "meaning_id": "ad9557514cd66f680ef641effad3ff73d0a0e6434c6eee047d42b10373512deb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must grant each holder a nationality (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "secure-nationality-by-state",
                    "over": [],
                    "predicate": "secure_nationality_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "nationality"
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
          "meaning_id": "89e76e2d1ba4682a676d318acff3b79fe34f12e003f4d68ac4d753d759c5387f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid refusing each holder a nationality (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-nationality-by-anyone",
                    "over": [],
                    "predicate": "avoid_nationality_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "nationality"
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
          "meaning_id": "de3a77fb31e296cce962e3bde649278576f66cdc7f408dbd2cb3b8d59c509682"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must grant each holder a nationality (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "secure-nationality-by-anyone",
                    "over": [],
                    "predicate": "secure_nationality_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "nationality"
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
          "meaning_id": "9c7ce65030155ef0577b2b53b433d8089d5006452e976c25dcacbf7a5167d48f"
        }
      ],
      "status": "open",
      "unit": "u054",
      "version": 1
    },
    {
      "id": "rs_u063",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid barring each holder from owning property (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "34ebff2c1a9ce897fea939341294100958e236faa72a6d83de4c19c3d830e1e4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure the ownership of property by each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "837571c0e9dfefdf21046b7aeba88650e2ec6be23d6c4d0bc2e11cd5a64c5968"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid barring each holder from owning property (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "a7e4d697e1ed50cf83ffb940696571a00213d3390bb20ff19e69abc1eb7e1122"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure the ownership of property by each holder (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "91cbccdccf0fdde05f2f26cb2fe84662c35b159f6663d3045056e94246b8dd2a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "a0af7bcd9406d2068ddcbae194760b51c1bbf3171a252c6b00e9cdb6e29f8b93"
        }
      ],
      "status": "open",
      "unit": "u063",
      "version": 1
    },
    {
      "id": "rs_u066",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of thought conscience as well as religion (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "9f2146bd19191fc16473692d398abd687cdbe36979a202e9850275455fcb76c3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of thought conscience as well as religion (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "be4ec45bfd1606bd450a2aea5741390519577848d3c9a3c9a9d3ad55152d65f3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of thought conscience as well as religion (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "d5648648ea6cee08e4acb781911a48dc820b51643088ccb4a38ac3cf9f5ab3e8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of thought conscience as well as religion (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "872579c06b053223340f0e344b6082ebc5c13ec3f264fd145513ec54189aeec4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "87df6cb235d520a86eeb0310ae5caea58b2f858f7d64215adde0afa420e48907"
        }
      ],
      "status": "open",
      "unit": "u066",
      "version": 1
    },
    {
      "id": "rs_u070",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of opinion as well as expression (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "ecfba5bb617559d0e8436119a990ca602219b1c42f3eab46b84d78cabed3860b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of opinion as well as expression (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "e2c90f3883bf8e8047e57676673941ff766f4fd4c8f468f8a4d0ddc96fe00076"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of opinion as well as expression (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "4a1bf748b2c7120ce6066ee4538e688bf14fb396ed959bb3b38d83ed2e9251c8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of opinion as well as expression (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "2ea7ed6a91f78055adc30dc3e172cc7ff5da09a4d8dbe8a300a08b6098abab5c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "15a9d16b0ed897fb2d08a9269b716eda5827d2a12e18f3e4c6031850d74e5198"
        }
      ],
      "status": "open",
      "unit": "u070",
      "version": 1
    },
    {
      "id": "rs_u073",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder freedom of peaceful assembly as well as association (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "930d158dd857922da6380efe69c8e1b340878deac1f80b70f0a66913470216c3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must secure each holder freedom of peaceful assembly as well as association (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "955002a10d33ba44014c96add1698a73d05d2c29e97aff6c594d43de32ed5f5d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder freedom of peaceful assembly as well as association (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "6d02a176abd80631e2ea98ad883a27887f612ae8522643231e783c9fa0f5390f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "liberty": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must secure each holder freedom of peaceful assembly as well as association (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "meaning_id": "e903c7de43a94dff1432753ce4ba43caaabdc48936db53be4a0767ca55226ee2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
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
          "meaning_id": "e32659d8024dab9cb298d7ac05023b7049df4486aad5d1e1d2b4d25046f1aa87"
        }
      ],
      "status": "open",
      "unit": "u073",
      "version": 1
    },
    {
      "id": "rs_u077",
      "models": {
        "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708": {
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
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must avoid denying each holder equal access to public service (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-equal-access-to-public-service-by-state",
                    "over": [],
                    "predicate": "avoid_public_service_access_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-access-to-public-service"
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
          "meaning_id": "a254754d1a2c3b73c33af0beedfe1d09e50e81f7dc9b81a8e963c0d89a6c1180"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state must give each holder equal access to public service (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "state_positive",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "a220297678aec79cfb4078b9e8721768272770aa5e3e222dd451bfb3ab612cd9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must avoid denying each holder equal access to public service (the duty is to avoid harming the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
                    "name": "avoid-equal-access-to-public-service-by-anyone",
                    "over": [],
                    "predicate": "avoid_public_service_access_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "equal-access-to-public-service"
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
          "meaning_id": "6bc8128544bf14cfe721ef659daeb217446f0de3762c56930b9b9f38d3224556"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_negative": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708",
              "state_positive": "36b6915db15ed767539c8c4a6491dc5ae1afa771d8e7636ac36e51211a7c5708"
            },
            "who": "translator",
            "why": "Claim reading: every state, group and person must give each holder equal access to public service (the duty is to secure the right; the source names no bearer and no polarity, so this is the translator's candidate)."
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
          "id": "anyone_positive",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "a4cb719423373080d98839a1e77874b24293bc4ee64e0238a54e83d3aefc0796"
        }
      ],
      "status": "open",
      "unit": "u077",
      "version": 1
    },
    {
      "id": "rs_u017",
      "models": {
        "49ece57b718d0bd80af1defcd335359667b287dea68f9849a1b026ebc22665f8": {
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
            "avoid_effective_remedy_required": [],
            "avoid_equal_protection_required": [],
            "avoid_fair_hearing_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_nationality_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_discrimination_required": [],
            "avoid_protection_against_incitement_required": [],
            "avoid_protection_against_interference_required": [],
            "avoid_public_service_access_required": [],
            "avoid_recognition_as_person_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
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
            "secure_leave_and_return_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_nationality_required": [],
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
              "default": "49ece57b718d0bd80af1defcd335359667b287dea68f9849a1b026ebc22665f8"
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
              "strict": "49ece57b718d0bd80af1defcd335359667b287dea68f9849a1b026ebc22665f8"
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
        "48caa3a35ff1f1819f48c3d99b9d82c5d4ee51625e36ebdae7d0291b3a0ace83": {
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
            "avoid_effective_remedy_required": [],
            "avoid_equal_protection_required": [],
            "avoid_fair_hearing_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_nationality_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_discrimination_required": [],
            "avoid_protection_against_incitement_required": [],
            "avoid_protection_against_interference_required": [],
            "avoid_public_service_access_required": [],
            "avoid_recognition_as_person_required": [],
            "avoid_security_of_person_required": [],
            "avoid_thought_conscience_religion_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "exercise_contrary_to_un": [],
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
            "secure_leave_and_return_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_nationality_required": [],
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
              "case_excluded": "48caa3a35ff1f1819f48c3d99b9d82c5d4ee51625e36ebdae7d0291b3a0ace83"
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
              "invocation_barred": "48caa3a35ff1f1819f48c3d99b9d82c5d4ee51625e36ebdae7d0291b3a0ace83"
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
          "meaning_id": "32b8b23445e8be9b77f63bb3cffc2507c75cf4580f0c89327e215ad9475cc279"
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
        "c179c778e9db3d4fc1364329d6a056c8b167d54c0afe0ad4875864b40a32be56": {
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
            "avoid_effective_remedy_required": [],
            "avoid_equal_protection_required": [],
            "avoid_fair_hearing_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_nationality_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_discrimination_required": [],
            "avoid_protection_against_incitement_required": [],
            "avoid_protection_against_interference_required": [],
            "avoid_public_service_access_required": [],
            "avoid_recognition_as_person_required": [],
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
            "secure_leave_and_return_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_nationality_required": [],
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
              "exercise_unprotected": "c179c778e9db3d4fc1364329d6a056c8b167d54c0afe0ad4875864b40a32be56"
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
              "exercise_prohibited": "c179c778e9db3d4fc1364329d6a056c8b167d54c0afe0ad4875864b40a32be56"
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
          "meaning_id": "ba0a16cc5f6383ffea52ce04cfc9111a25cdfc0b317713b7a2235f6385e41b61"
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
        "4267bec96a45971a1ea21d9a1db8d290702ae5e0f65db448b72f62157befad3f": {
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
            "avoid_effective_remedy_required": [],
            "avoid_equal_protection_required": [],
            "avoid_fair_hearing_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_nationality_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_presumed_innocent_required": [],
            "avoid_property_required": [],
            "avoid_protection_against_discrimination_required": [],
            "avoid_protection_against_incitement_required": [],
            "avoid_protection_against_interference_required": [],
            "avoid_public_service_access_required": [],
            "avoid_recognition_as_person_required": [],
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
            "secure_leave_and_return_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_nationality_required": [],
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
              "no_implied_right": "4267bec96a45971a1ea21d9a1db8d290702ae5e0f65db448b72f62157befad3f"
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
              "interpretive_ban": "4267bec96a45971a1ea21d9a1db8d290702ae5e0f65db448b72f62157befad3f"
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
          "meaning_id": "36ab5878f9d1aad8b8fbd18bbbc127239385f8d24ac871bc54ac86544d362080"
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
          "independent_and_impartial"
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
      "kind": "right",
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
