---
{
  "environment": {
    "language": "ve.core@0.2",
    "profiles": [
      "documents@1",
      "norms@0",
      "readings@1",
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
        "avoid_arbitrary_arrest_detention_exile_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid arbitrarily arresting the person as well as detaining as well as exiling them. Source clause: No one shall be subjected to arbitrary arrest, detention or exile.",
          "regulated": {
            "act": "{0} avoid arbitrarily arresting {1} as well as detaining as well as exiling them",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_arbitrary_deprivation_of_property_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid arbitrarily depriving the person of property. Source clause: No one shall be arbitrarily deprived of his property.",
          "regulated": {
            "act": "{0} avoid arbitrarily depriving {1} of property",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_arbitrary_interference_private_life_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid arbitrary interference with the private life of the person. Source clause: No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence.",
          "regulated": {
            "act": "{0} avoid arbitrary interference with the private life of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_arbitrary_loss_of_nationality_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid arbitrarily depriving the person of nationality as well as barring its change. Source clause: No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality.",
          "regulated": {
            "act": "{0} avoid arbitrarily depriving {1} of nationality as well as barring its change",
            "default": "deny",
            "role": "obligation"
          }
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
        "avoid_attacks_upon_honour_and_reputation_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid attacks upon the honour as well as reputation of the person. Source clause: nor to attacks upon his honour and reputation (No one shall be subjected to ...).",
          "regulated": {
            "act": "{0} avoid attacks upon the honour as well as reputation of {1}",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_cultural_life_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from taking part in the cultural life of the community. Source clause: Everyone has the right freely to participate in the cultural life of the community.",
          "regulated": {
            "act": "{0} avoid barring {1} from taking part in the cultural life of the community",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_distinction_by_country_status_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid making any distinction against the person by the status of their country. Source clause: no distinction shall be made on the basis of the political, jurisdictional or international status of the country or territory to which a person belongs, whether it be independent, trust, non-self-governing or under any other limitation of sovereignty.",
          "regulated": {
            "act": "{0} avoid making any distinction against {1} by the status of their country",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_education_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from education. Source clause: Everyone has the right to education.",
          "regulated": {
            "act": "{0} avoid barring {1} from education",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_enjoyment_of_the_arts_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from enjoying the arts. Source clause: Everyone has the right freely to enjoy the arts (the right is carried from u105a).",
          "regulated": {
            "act": "{0} avoid barring {1} from enjoying the arts",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_free_choice_of_employment_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid restricting the free choice of employment of the person. Source clause: Everyone has the right to free choice of employment (the right is carried from u084a).",
          "regulated": {
            "act": "{0} avoid restricting the free choice of employment of {1}",
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
        "avoid_marriage_without_free_and_full_consent_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid entering the person into marriage without their free as well as full consent. Source clause: Marriage shall be entered into only with the free and full consent of the intending spouses.",
          "regulated": {
            "act": "{0} avoid entering {1} into marriage without their free as well as full consent",
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
        "avoid_slavery_and_slave_trade_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to avoid slavery as well as the slave trade in all their forms. Source clause: slavery and the slave trade shall be prohibited in all their forms.",
          "regulated": {
            "act": "{0} avoid slavery as well as the slave trade in all their forms",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_slavery_or_servitude_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid holding the person in slavery as well as servitude. Source clause: No one shall be held in slavery or servitude.",
          "regulated": {
            "act": "{0} avoid holding {1} in slavery as well as servitude",
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
        "avoid_torture_or_ill_treatment_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid subjecting the person to torture as well as ill-treatment. Source clause: No one shall be subjected to torture or to cruel, inhuman or degrading treatment or punishment.",
          "regulated": {
            "act": "{0} avoid subjecting {1} to torture as well as ill-treatment",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_trade_unions_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from forming as well as joining trade unions. Source clause: Everyone has the right to form and to join trade unions for the protection of his interests.",
          "regulated": {
            "act": "{0} avoid barring {1} from forming as well as joining trade unions",
            "default": "deny",
            "role": "obligation"
          }
        },
        "avoid_work_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to avoid barring the person from work. Source clause: Everyone has the right to work.",
          "regulated": {
            "act": "{0} avoid barring {1} from work",
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
        "direct_education_to_personality_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to direct education to the full development of the human personality. Source clause: Education shall be directed to the full development of the human personality.",
          "regulated": {
            "act": "{0} direct education to the full development of the human personality",
            "default": "deny",
            "role": "obligation"
          }
        },
        "direct_education_to_respect_for_rights_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to direct education to strengthen respect of human rights as well as freedoms. Source clause: and to the strengthening of respect for human rights and fundamental freedoms (Education shall be directed ...).",
          "regulated": {
            "act": "{0} direct education to strengthen respect of human rights as well as freedoms",
            "default": "deny",
            "role": "obligation"
          }
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
        "make_elementary_education_compulsory_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to make elementary education compulsory. Source clause: Elementary education shall be compulsory.",
          "regulated": {
            "act": "{0} make elementary education compulsory",
            "default": "deny",
            "role": "obligation"
          }
        },
        "make_higher_education_accessible_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to make higher education equally accessible to all on the basis of merit. Source clause: and higher education shall be equally accessible to all on the basis of merit.",
          "regulated": {
            "act": "{0} make higher education equally accessible to all on the basis of merit",
            "default": "deny",
            "role": "obligation"
          }
        },
        "make_technical_education_available_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to make technical as well as professional education generally available. Source clause: Technical and professional education shall be made generally available.",
          "regulated": {
            "act": "{0} make technical as well as professional education generally available",
            "default": "deny",
            "role": "obligation"
          }
        },
        "of_age_for_elementary_education": {
          "arguments": [
            "person"
          ],
          "description": "The person is of the age at which elementary education is compulsory, if there is one; the source states no age",
          "verbalisation": "{0} is of the age for elementary education"
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
        "prohibit_slavery_and_slave_trade_required": {
          "arguments": [
            "bearer"
          ],
          "description": "The bearer is required to prohibit slavery as well as the slave trade in all their forms. Source clause: slavery and the slave trade shall be prohibited in all their forms.",
          "regulated": {
            "act": "{0} prohibit slavery as well as the slave trade in all their forms",
            "default": "deny",
            "role": "obligation"
          }
        },
        "receive_elementary_education_required": {
          "arguments": [
            "person"
          ],
          "description": "The person is required to receive elementary education. Source clause: Elementary education shall be compulsory.",
          "regulated": {
            "act": "{0} receive elementary education",
            "default": "deny",
            "role": "obligation"
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
        "secure_cultural_life_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person free participation in the cultural life of the community. Source clause: Everyone has the right freely to participate in the cultural life of the community.",
          "regulated": {
            "act": "{0} secure {1} free participation in the cultural life of the community",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_education_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person education. Source clause: Everyone has the right to education.",
          "regulated": {
            "act": "{0} secure {1} education",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_enjoyment_of_the_arts_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person the enjoyment of the arts. Source clause: Everyone has the right freely to enjoy the arts (the right is carried from u105a).",
          "regulated": {
            "act": "{0} secure {1} the enjoyment of the arts",
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
        "secure_free_choice_of_employment_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person free choice of employment. Source clause: Everyone has the right to free choice of employment (the right is carried from u084a).",
          "regulated": {
            "act": "{0} secure {1} free choice of employment",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_just_and_favourable_conditions_of_work_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person just as well as favourable conditions of work. Source clause: Everyone has the right to just and favourable conditions of work (the right is carried from u084a).",
          "regulated": {
            "act": "{0} secure {1} just as well as favourable conditions of work",
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
        "secure_protection_against_unemployment_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to protect the person against unemployment. Source clause: Everyone has the right to protection against unemployment (the right is carried from u084a).",
          "regulated": {
            "act": "{0} protect {1} against unemployment",
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
        "secure_scientific_advancement_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person a share in scientific advancement as well as its benefits. Source clause: Everyone has the right freely to share in scientific advancement and its benefits (the right is carried from u105a).",
          "regulated": {
            "act": "{0} secure {1} a share in scientific advancement as well as its benefits",
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
        "secure_social_security_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person social security. Source clause: Everyone, as a member of society, has the right to social security.",
          "regulated": {
            "act": "{0} secure {1} social security",
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
        },
        "secure_trade_unions_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to secure the person forming as well as joining trade unions. Source clause: Everyone has the right to form and to join trade unions for the protection of his interests.",
          "regulated": {
            "act": "{0} secure {1} forming as well as joining trade unions",
            "default": "deny",
            "role": "obligation"
          }
        },
        "secure_work_required": {
          "arguments": [
            "bearer",
            "person"
          ],
          "description": "The bearer is required to provide the person with work. Source clause: Everyone has the right to work.",
          "regulated": {
            "act": "{0} provide {1} with work",
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
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which statuses count: political, jurisdictional, international",
        "whether the country or territory is independent, trust, non-self-governing or under another limitation of sovereignty",
        "whether the status of a territory counts as the status of the country to which a person belongs"
      ],
      "jurisdiction": "universal",
      "name": "status_of_country_or_territory",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as slavery"
      ],
      "jurisdiction": "universal",
      "name": "slavery",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as servitude"
      ],
      "jurisdiction": "universal",
      "name": "servitude",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as the slave trade",
        "which forms are meant by 'all their forms'"
      ],
      "jurisdiction": "universal",
      "name": "slave_trade",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which treatment is cruel",
        "which treatment is inhuman",
        "which treatment is degrading",
        "whether punishment is covered as well as treatment"
      ],
      "jurisdiction": "universal",
      "name": "ill_treatment",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "whether privacy, family, home and correspondence are the whole of it",
        "what makes interference with each of them arbitrary"
      ],
      "jurisdiction": "universal",
      "name": "private_life",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes consent free",
        "what makes consent full",
        "who the intending spouses are"
      ],
      "jurisdiction": "universal",
      "name": "free_and_full_consent",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "who must attend: persons, parents or children",
        "up to what age",
        "who makes it compulsory"
      ],
      "jurisdiction": "universal",
      "name": "compulsory",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes education generally available"
      ],
      "jurisdiction": "universal",
      "name": "generally_available",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what counts as merit",
        "who judges merit"
      ],
      "jurisdiction": "universal",
      "name": "merit",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what the full development of the human personality requires"
      ],
      "jurisdiction": "universal",
      "name": "full_development_of_the_human_personality",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what social security covers"
      ],
      "jurisdiction": "universal",
      "name": "social_security",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "what makes conditions of work just",
        "what makes them favourable"
      ],
      "jurisdiction": "universal",
      "name": "just_and_favourable_conditions_of_work",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    },
    {
      "arguments": [],
      "decided_by": "unstated",
      "factors": [
        "which State, if any, must grant the nationality",
        "whether birth, descent or residence decides"
      ],
      "jurisdiction": "universal",
      "name": "bearer_of_the_nationality_duty",
      "necessary": [],
      "precedents": [],
      "sufficient": [],
      "version": 1
    }
  ],
  "reading_sets": [
    {
      "id": "rs_u022a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "20787a54784cc02231c2234984a7403fb0e25f94b28e3c1ea0d2703ed9bb1097",
              "anyone_positive": "df41857b536ed7fac38201f0e0bbb0fa98a7c16248891f780983e7fd55a7d28f",
              "state_positive": "df41857b536ed7fac38201f0e0bbb0fa98a7c16248891f780983e7fd55a7d28f"
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
          "meaning_id": "319f91f429ff78b3ffe429c25a86b9e584dd7ea8cdea27b267373103529d3e37"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "5b332efba1d7dba3a314bb582f2a16bf724f8541db818db948a5369846cf28ad",
              "anyone_positive": "0f61fc6bfdf1a6e105e07921fe4be0439cc3fe3e6e7d9c2fdd13deae557dce47",
              "state_negative": "df41857b536ed7fac38201f0e0bbb0fa98a7c16248891f780983e7fd55a7d28f"
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
          "meaning_id": "9dd3c2c3d0cc91c227161f2ca3cf3e7a78e7606f0deb7dbc7ff78ea3a18eddae"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "cedde5b6c0fd723e33d01546d05c43a7a9dfcf1fa73122c5450f299a3b63fab0",
              "state_negative": "20787a54784cc02231c2234984a7403fb0e25f94b28e3c1ea0d2703ed9bb1097",
              "state_positive": "5b332efba1d7dba3a314bb582f2a16bf724f8541db818db948a5369846cf28ad"
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
          "meaning_id": "0390717a4d9b35cc6831d253e1bbbe2b8d120251d270e43cb9005777d99e9720"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "cedde5b6c0fd723e33d01546d05c43a7a9dfcf1fa73122c5450f299a3b63fab0",
              "state_negative": "df41857b536ed7fac38201f0e0bbb0fa98a7c16248891f780983e7fd55a7d28f",
              "state_positive": "0f61fc6bfdf1a6e105e07921fe4be0439cc3fe3e6e7d9c2fdd13deae557dce47"
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
          "meaning_id": "c3fdd7bcdcd5baeb5a6cf112950d0453c8a237b2691a35fa98f8a249d564ee13"
        }
      ],
      "situations": {
        "0f61fc6bfdf1a6e105e07921fe4be0439cc3fe3e6e7d9c2fdd13deae557dce47": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "20787a54784cc02231c2234984a7403fb0e25f94b28e3c1ea0d2703ed9bb1097": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "5b332efba1d7dba3a314bb582f2a16bf724f8541db818db948a5369846cf28ad": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "cedde5b6c0fd723e33d01546d05c43a7a9dfcf1fa73122c5450f299a3b63fab0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "df41857b536ed7fac38201f0e0bbb0fa98a7c16248891f780983e7fd55a7d28f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        }
      },
      "status": "open",
      "unit": "u022a",
      "version": 1
    },
    {
      "id": "rs_u022b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "be929a29492f1ecc0fa323383c8326b0c3b3427593e7f2a227675a9868de9d1d",
              "anyone_positive": "e3ee979a3a276eac97523df3e3200e0db2d3ab4c86683d8624b9ccad5c1b179d",
              "state_positive": "e3ee979a3a276eac97523df3e3200e0db2d3ab4c86683d8624b9ccad5c1b179d"
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
          "meaning_id": "b3910eed5938ae3ad48acc35dc8f2a232eb8bfdd6bd0e9416c7dd55e1b43d02b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "24a2840b67c6e25adcd8f4c63a7870fa9a0c8b1acfaa37564f7d97bf59d2315a",
              "anyone_positive": "fd7f38d94e993b4f9e6df9d4956656b632c20dc75f9a18305172b64385e5adcb",
              "state_negative": "e3ee979a3a276eac97523df3e3200e0db2d3ab4c86683d8624b9ccad5c1b179d"
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
          "meaning_id": "a4dd839ad01810f0d7be6a4fbcf8095a868858e59951d19760e9fecfb91faf40"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "3bbd6ba2d45d323a500de083188aa81eef4460728e13f2bb41b4f2eec0e9843d",
              "state_negative": "be929a29492f1ecc0fa323383c8326b0c3b3427593e7f2a227675a9868de9d1d",
              "state_positive": "24a2840b67c6e25adcd8f4c63a7870fa9a0c8b1acfaa37564f7d97bf59d2315a"
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
          "meaning_id": "fb953c999883bd46316757ee7cdd60f2af929a86181622960d611b4f4cf37429"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "3bbd6ba2d45d323a500de083188aa81eef4460728e13f2bb41b4f2eec0e9843d",
              "state_negative": "e3ee979a3a276eac97523df3e3200e0db2d3ab4c86683d8624b9ccad5c1b179d",
              "state_positive": "fd7f38d94e993b4f9e6df9d4956656b632c20dc75f9a18305172b64385e5adcb"
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
          "meaning_id": "b49625dcdfb08ae0a18352d9122a5a821f4dfe5e5485ebd065137957251cee73"
        }
      ],
      "situations": {
        "24a2840b67c6e25adcd8f4c63a7870fa9a0c8b1acfaa37564f7d97bf59d2315a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_liberty_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "3bbd6ba2d45d323a500de083188aa81eef4460728e13f2bb41b4f2eec0e9843d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_liberty_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "be929a29492f1ecc0fa323383c8326b0c3b3427593e7f2a227675a9868de9d1d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_liberty_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "e3ee979a3a276eac97523df3e3200e0db2d3ab4c86683d8624b9ccad5c1b179d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_liberty_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "fd7f38d94e993b4f9e6df9d4956656b632c20dc75f9a18305172b64385e5adcb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_liberty_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        }
      },
      "status": "open",
      "unit": "u022b",
      "version": 1
    },
    {
      "id": "rs_u022c",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "bc2df6f1546c671f359d33855102d271beeea88735635522bcbf189c56b385cf",
              "anyone_positive": "8dd424873ff0b128721e2f9ba610b3c82e104857abb06e077e1655f9a8eb148f",
              "state_positive": "8dd424873ff0b128721e2f9ba610b3c82e104857abb06e077e1655f9a8eb148f"
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
          "meaning_id": "b6042e44d8cf9f9443c8bad5c1a14653500d0e3c9231396364c03c367636f292"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "cbd943fe4d5cba4cc2387c3b1b3d3a451567101cbb00ea881a6e7d4edd218278",
              "anyone_positive": "adb488713455bb4bc372afd945eac5cde76eca9d67e28002aee9bf1a3bbdcb00",
              "state_negative": "8dd424873ff0b128721e2f9ba610b3c82e104857abb06e077e1655f9a8eb148f"
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
          "meaning_id": "e7f4a8706837eda8d3438374ad0f71b95ddadbaa1c3ecaf3ce97f3f4937db55f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "2d4349b3da38d02e3ca89c1a55b106f0cdc488a890911a902d051e81ef91b76e",
              "state_negative": "bc2df6f1546c671f359d33855102d271beeea88735635522bcbf189c56b385cf",
              "state_positive": "cbd943fe4d5cba4cc2387c3b1b3d3a451567101cbb00ea881a6e7d4edd218278"
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
          "meaning_id": "42150ea002457245881d6b9bde8b278568475dcd6e7e3b723a64866b867f54e3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "2d4349b3da38d02e3ca89c1a55b106f0cdc488a890911a902d051e81ef91b76e",
              "state_negative": "8dd424873ff0b128721e2f9ba610b3c82e104857abb06e077e1655f9a8eb148f",
              "state_positive": "adb488713455bb4bc372afd945eac5cde76eca9d67e28002aee9bf1a3bbdcb00"
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
          "meaning_id": "1b80492bf0a3575ffce9dbb95a888a6aa1fc8289319becff58a52fd73edee20c"
        }
      ],
      "situations": {
        "2d4349b3da38d02e3ca89c1a55b106f0cdc488a890911a902d051e81ef91b76e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_security_of_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "8dd424873ff0b128721e2f9ba610b3c82e104857abb06e077e1655f9a8eb148f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_security_of_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "adb488713455bb4bc372afd945eac5cde76eca9d67e28002aee9bf1a3bbdcb00": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_security_of_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "bc2df6f1546c671f359d33855102d271beeea88735635522bcbf189c56b385cf": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_security_of_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "cbd943fe4d5cba4cc2387c3b1b3d3a451567101cbb00ea881a6e7d4edd218278": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_security_of_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        }
      },
      "status": "open",
      "unit": "u022c",
      "version": 1
    },
    {
      "id": "rs_u029",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "887acd5d64353b956d2b8d7fe8ab7a5e8f9a7e030f876513c698cc10def609db"
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
          "meaning_id": "8840f6b711e5440ee70af672adb512018b8e82e139a13f94b9588e5a6ce19b2d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "887acd5d64353b956d2b8d7fe8ab7a5e8f9a7e030f876513c698cc10def609db"
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
          "meaning_id": "fc9307cf20ffd155b0b1c1a0ffbab029410ff425a8516c4a39c998ab1ed1f0ee"
        }
      ],
      "situations": {
        "887acd5d64353b956d2b8d7fe8ab7a5e8f9a7e030f876513c698cc10def609db": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_recognition_as_person_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        }
      },
      "status": "open",
      "unit": "u029",
      "version": 1
    },
    {
      "id": "rs_u032",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "2508a10ec65c1c2cf726a0983761f93965439da0da88f49ad0805842eb8dc868"
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
          "meaning_id": "786e00295b41b03eddcfc3ca7187b29eeda66dc47215c092363869d9a365a6d4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "2508a10ec65c1c2cf726a0983761f93965439da0da88f49ad0805842eb8dc868"
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
          "meaning_id": "871a153e2a17ea5032be8badd0f1000f0d2290629e7b423bfbaec3aea9d629b0"
        }
      ],
      "situations": {
        "2508a10ec65c1c2cf726a0983761f93965439da0da88f49ad0805842eb8dc868": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_equal_protection_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        }
      },
      "status": "open",
      "unit": "u032",
      "version": 1
    },
    {
      "id": "rs_u033a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "9273ad554a48a4c14e201e9af34f4e1cdd4906ede24d9e3c8ac20867953bbd18"
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
          "meaning_id": "a3e7fba8cf1d1c8e1439ba93836fca638d1019fc88792188bb3906692ea45ab1"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "9273ad554a48a4c14e201e9af34f4e1cdd4906ede24d9e3c8ac20867953bbd18"
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
          "meaning_id": "8442f0d71a9848d3d0713869e5b98161530bc72b94e831e6379f5b53972c8d79"
        }
      ],
      "situations": {
        "9273ad554a48a4c14e201e9af34f4e1cdd4906ede24d9e3c8ac20867953bbd18": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_discrimination_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        }
      },
      "status": "open",
      "unit": "u033a",
      "version": 1
    },
    {
      "id": "rs_u033b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "1cc9618da90f69c4b4ab1a035047cd3f1af2c28481cbffde023b425e8062cc5c"
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
          "meaning_id": "9af9318ca1dca9356b633718228ec50ed6046421d4f112cdaabc0fd410db27bb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "1cc9618da90f69c4b4ab1a035047cd3f1af2c28481cbffde023b425e8062cc5c"
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
          "meaning_id": "d5c6f9ffe33dfb54ea2c607ed4275908268a81df94e037dc0facb1d8971ef7b5"
        }
      ],
      "situations": {
        "1cc9618da90f69c4b4ab1a035047cd3f1af2c28481cbffde023b425e8062cc5c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_incitement_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        }
      },
      "status": "open",
      "unit": "u033b",
      "version": 1
    },
    {
      "id": "rs_u046",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "45869d6f082ed59871c094293540df8da91b6bb3998bc8c386dbe4a5787a752c"
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
          "meaning_id": "a4f436df8dac74f137e494deb265f52ebf955bd6561c0c1c6ae40397da75cd13"
        },
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "45869d6f082ed59871c094293540df8da91b6bb3998bc8c386dbe4a5787a752c"
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
          "meaning_id": "165e2e05477df3757e4a7eba3c01e23ab2d25b6dc8c4f3a0772d6c6a96ac9fc4"
        }
      ],
      "situations": {
        "45869d6f082ed59871c094293540df8da91b6bb3998bc8c386dbe4a5787a752c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_interference_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        }
      },
      "status": "open",
      "unit": "u046",
      "version": 1
    },
    {
      "id": "rs_u048",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "f3dfb1212dbba77fb651c3235299e6dae80813bf4c77573f569c9779848b43d5",
              "anyone_positive": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f",
              "liberty": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f",
              "state_positive": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f"
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
          "meaning_id": "c2002703f1aef641a88d7128957b0c9e000b3ebbe69c40af73920c87611e2779"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "6ac182b4b92d987512bcfa7e2d4b32bdc7670522eeb093931f40dee4f9a1e366",
              "anyone_positive": "8b21e2cb761e58ed047354e365cbcebed86cc85c826d82ba3a1cfccb0647aa11",
              "liberty": "2aae0d0f2dd61fcc6b9f4b53a2e0741b049b3a0a06861a4d460810bd9e25abb0",
              "state_negative": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f"
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
          "meaning_id": "98ceb57902a0689a6480c27b2c6a546cd1ae5b28dc2d0ff41db9e5e6014d0ba3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "c15f1202c6a681bccfe889a9573a86e72a94381323c3eb03a4b2bd34d4a56f8e",
              "liberty": "c15f1202c6a681bccfe889a9573a86e72a94381323c3eb03a4b2bd34d4a56f8e",
              "state_negative": "f3dfb1212dbba77fb651c3235299e6dae80813bf4c77573f569c9779848b43d5",
              "state_positive": "6ac182b4b92d987512bcfa7e2d4b32bdc7670522eeb093931f40dee4f9a1e366"
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
          "meaning_id": "fe721229f06df4eef51e0bb795bbfdc85c03aab75ce13a98f2fec2ab67573332"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "c15f1202c6a681bccfe889a9573a86e72a94381323c3eb03a4b2bd34d4a56f8e",
              "liberty": "7f66159000aa3032ae1b7ab181c08d286ed193e5bb50495f7ac437c75dd6d7f5",
              "state_negative": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f",
              "state_positive": "8b21e2cb761e58ed047354e365cbcebed86cc85c826d82ba3a1cfccb0647aa11"
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
          "meaning_id": "66fdeeea635e737fe3f504c4bb95025e233971515cac7b549aabd22480c4ff63"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "c15f1202c6a681bccfe889a9573a86e72a94381323c3eb03a4b2bd34d4a56f8e",
              "anyone_positive": "7f66159000aa3032ae1b7ab181c08d286ed193e5bb50495f7ac437c75dd6d7f5",
              "state_negative": "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f",
              "state_positive": "2aae0d0f2dd61fcc6b9f4b53a2e0741b049b3a0a06861a4d460810bd9e25abb0"
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
          "meaning_id": "411e6fff6d6ec6925121fc899f0b4b5cdb179b78d8e59f3482fd4092476a213a"
        }
      ],
      "situations": {
        "2aae0d0f2dd61fcc6b9f4b53a2e0741b049b3a0a06861a4d460810bd9e25abb0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_movement_and_residence",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "6ac182b4b92d987512bcfa7e2d4b32bdc7670522eeb093931f40dee4f9a1e366": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_movement_and_residence_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "7f66159000aa3032ae1b7ab181c08d286ed193e5bb50495f7ac437c75dd6d7f5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_movement_and_residence",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive"
        },
        "8b21e2cb761e58ed047354e365cbcebed86cc85c826d82ba3a1cfccb0647aa11": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_movement_and_residence_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "b5756dca0db0eeae2d5810f606769c10d7dd82b1a9750598528e7fc40c4e540f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_movement_and_residence_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "c15f1202c6a681bccfe889a9573a86e72a94381323c3eb03a4b2bd34d4a56f8e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_movement_and_residence_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "f3dfb1212dbba77fb651c3235299e6dae80813bf4c77573f569c9779848b43d5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_movement_and_residence_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        }
      },
      "status": "open",
      "unit": "u048",
      "version": 1
    },
    {
      "id": "rs_u049",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "125f72fd5eb95e310f4b9949b9083770108fccb0594cbd5496fb2a91f555c757",
              "liberty": "91189814db0e784a20c55e57bb873ca2114225e4c71d2c8dee80173d02cf2ce5"
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
          "meaning_id": "519d394079ca60d942ed8410c9913be55e845f74653e397f293f26a18012cfb3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "983d1bacdea2b27a2a473469cf6f07a41b2d7c614faac5c75dd4b3ae98d02017",
              "state_claim": "125f72fd5eb95e310f4b9949b9083770108fccb0594cbd5496fb2a91f555c757"
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
          "meaning_id": "b34a97bc6c0432370bfc31ea8b32fcf3147ceb1e3d1fb39b6a61413887e7a1dd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim": "983d1bacdea2b27a2a473469cf6f07a41b2d7c614faac5c75dd4b3ae98d02017",
              "state_claim": "91189814db0e784a20c55e57bb873ca2114225e4c71d2c8dee80173d02cf2ce5"
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
          "meaning_id": "cb5caafa8acfad5dd46b726f655e20e7ef19ef2c4504f6d7392a23f1be25df45"
        }
      ],
      "situations": {
        "125f72fd5eb95e310f4b9949b9083770108fccb0594cbd5496fb2a91f555c757": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_leave_and_return_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim"
        },
        "91189814db0e784a20c55e57bb873ca2114225e4c71d2c8dee80173d02cf2ce5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_leave_and_return_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_claim"
        },
        "983d1bacdea2b27a2a473469cf6f07a41b2d7c614faac5c75dd4b3ae98d02017": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_leave_and_return_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_claim"
        }
      },
      "status": "open",
      "unit": "u049",
      "version": 1
    },
    {
      "id": "rs_u063",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "d8b543c5a3e5d4b17fe7aa0f3b6b2a19e2869bb68aaf597eac557b0512fccf5d",
              "anyone_positive": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879",
              "liberty": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879",
              "state_positive": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879"
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
          "meaning_id": "6ee73e47a9b5285d0928af3e77a13d2fdb364748932d9e300982f304a83cd115"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "821d803456aa2ec3daf967eb527d6d132e73e929c44c0e453791e6acce713acb",
              "anyone_positive": "776deeaf4012401a27fb5d8a3c4787611d25208500d89e4fac91fe5f6d1ae790",
              "liberty": "26737493db3f5ff5fedd543cfd0d86e30c8371b4b42d86a08d21121c7154dc8b",
              "state_negative": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879"
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
          "meaning_id": "c65a50bddf3d1e19a808b8e400e593749d3dd08a6cd610d7fb3062a668c9664f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "1bcee0bb6ed776522032540aec83a8fdd44783ae1c40dad6ffd3b8cb5178e346",
              "liberty": "1bcee0bb6ed776522032540aec83a8fdd44783ae1c40dad6ffd3b8cb5178e346",
              "state_negative": "d8b543c5a3e5d4b17fe7aa0f3b6b2a19e2869bb68aaf597eac557b0512fccf5d",
              "state_positive": "821d803456aa2ec3daf967eb527d6d132e73e929c44c0e453791e6acce713acb"
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
          "meaning_id": "55d715e59d308c8d5822b9bfc6963c7e95ea30e94bacf2e4c7b7a93577c514fe"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "1bcee0bb6ed776522032540aec83a8fdd44783ae1c40dad6ffd3b8cb5178e346",
              "liberty": "e5ce0a45a473682c808c57631d43ede13c590532a662c3b7b46f94169dba479a",
              "state_negative": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879",
              "state_positive": "776deeaf4012401a27fb5d8a3c4787611d25208500d89e4fac91fe5f6d1ae790"
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
          "meaning_id": "fce2f099a416a487b78a1403066765db6d5039d3dc84ec751d7ce1ac394f8922"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "1bcee0bb6ed776522032540aec83a8fdd44783ae1c40dad6ffd3b8cb5178e346",
              "anyone_positive": "e5ce0a45a473682c808c57631d43ede13c590532a662c3b7b46f94169dba479a",
              "state_negative": "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879",
              "state_positive": "26737493db3f5ff5fedd543cfd0d86e30c8371b4b42d86a08d21121c7154dc8b"
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
          "meaning_id": "1fb3d8aa833d2c916e79fcd66d4707448d768c2240312477bb87ba71a189b72f"
        }
      ],
      "situations": {
        "015f0fbef51b9d525222dd75eb7feeeaff948130eeb0f4b7c60e54e1673f0879": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "1bcee0bb6ed776522032540aec83a8fdd44783ae1c40dad6ffd3b8cb5178e346": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "26737493db3f5ff5fedd543cfd0d86e30c8371b4b42d86a08d21121c7154dc8b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_property",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "776deeaf4012401a27fb5d8a3c4787611d25208500d89e4fac91fe5f6d1ae790": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "821d803456aa2ec3daf967eb527d6d132e73e929c44c0e453791e6acce713acb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "d8b543c5a3e5d4b17fe7aa0f3b6b2a19e2869bb68aaf597eac557b0512fccf5d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "e5ce0a45a473682c808c57631d43ede13c590532a662c3b7b46f94169dba479a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_property",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive"
        }
      },
      "status": "open",
      "unit": "u063",
      "version": 1
    },
    {
      "id": "rs_u066",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "9c682f8aa24caee58fc26db20f066fd81878edc70e093a5db6d312bf3d429131",
              "anyone_positive": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c",
              "liberty": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c",
              "state_positive": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c"
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
          "meaning_id": "bc3ad09a1a36b45c468df4b16ae1d51506b930af464d9c2161292979874591ab"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "b2a7825942c8d15c189985fa050f8d5141c32dc6ee6944ce84c969781cfd6e1d",
              "anyone_positive": "26bc1c70073c26ec3b078dbc7039059f1ccd993cf78a6d53fb2504fced2715b4",
              "liberty": "eaa0547da234a8e33638761e11572a4b6622a29a5af929a5573e22f792019404",
              "state_negative": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c"
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
          "meaning_id": "e1683619b335ea6f7e2dec2251a669632e7e252eb2595e8d1f55a010ad85662c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "ce751dbab944b38a856a20aa4ed594b00599cba35d21b868090dd4d9c2c5d077",
              "liberty": "ce751dbab944b38a856a20aa4ed594b00599cba35d21b868090dd4d9c2c5d077",
              "state_negative": "9c682f8aa24caee58fc26db20f066fd81878edc70e093a5db6d312bf3d429131",
              "state_positive": "b2a7825942c8d15c189985fa050f8d5141c32dc6ee6944ce84c969781cfd6e1d"
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
          "meaning_id": "7e360df66ab78bc6a2c8e5a093181ba74dd6c1ea0059a76c7640769822a6a71a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "ce751dbab944b38a856a20aa4ed594b00599cba35d21b868090dd4d9c2c5d077",
              "liberty": "cfdccfcbf02cf87cce2bd969c21e48e43feea474822f578055d505b24d81b0af",
              "state_negative": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c",
              "state_positive": "26bc1c70073c26ec3b078dbc7039059f1ccd993cf78a6d53fb2504fced2715b4"
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
          "meaning_id": "0c5d8d9b7e569dcfd0e374d901b78b28fa2dff80ccc19337a96edd95e10aa73f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "ce751dbab944b38a856a20aa4ed594b00599cba35d21b868090dd4d9c2c5d077",
              "anyone_positive": "cfdccfcbf02cf87cce2bd969c21e48e43feea474822f578055d505b24d81b0af",
              "state_negative": "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c",
              "state_positive": "eaa0547da234a8e33638761e11572a4b6622a29a5af929a5573e22f792019404"
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
          "meaning_id": "150e58494c8462b02eb38da5fdcde8d896178e81cb4013679b4dc6f0eef41a05"
        }
      ],
      "situations": {
        "26bc1c70073c26ec3b078dbc7039059f1ccd993cf78a6d53fb2504fced2715b4": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_thought_conscience_religion_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "613d05de6c5310c8343870b4cd8267d5d6f7b1d3eb4e1068253fdd34b1700f4c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_thought_conscience_religion_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "9c682f8aa24caee58fc26db20f066fd81878edc70e093a5db6d312bf3d429131": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_thought_conscience_religion_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "b2a7825942c8d15c189985fa050f8d5141c32dc6ee6944ce84c969781cfd6e1d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_thought_conscience_religion_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "ce751dbab944b38a856a20aa4ed594b00599cba35d21b868090dd4d9c2c5d077": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_thought_conscience_religion_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "cfdccfcbf02cf87cce2bd969c21e48e43feea474822f578055d505b24d81b0af": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_thought_conscience_religion",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive"
        },
        "eaa0547da234a8e33638761e11572a4b6622a29a5af929a5573e22f792019404": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_thought_conscience_religion",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        }
      },
      "status": "open",
      "unit": "u066",
      "version": 1
    },
    {
      "id": "rs_u070",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "a9f1e809c01a19020a1fc908851cc0cf1e3ab7bf59b3f9bc3a2075515d983fb7",
              "anyone_positive": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f",
              "liberty": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f",
              "state_positive": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f"
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
          "meaning_id": "ce66fc91673e4e363b35d2d362a198973ae98452d9538be26aa6fbbaf8107ed0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "bfebca8dfb74071580e313cabc6ee42ebcfcb847aa736bd38d02811adf593ed8",
              "anyone_positive": "47764f421a2f5a9fdbae8347a27e7c051aeddb051e679348d356da53a476ad8c",
              "liberty": "4c1baa2769f6f76e8192cbaf09c912790b1c351841b13147feb4b373b6eed055",
              "state_negative": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f"
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
          "meaning_id": "6cc3743f53225f3e6f68a4321e793c58b14dfed03548b3e258fe71682b4eca8e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "2ba1c34a592ec1c85b979b827624c3bb9a88a9400d638735a280223afa00664f",
              "liberty": "2ba1c34a592ec1c85b979b827624c3bb9a88a9400d638735a280223afa00664f",
              "state_negative": "a9f1e809c01a19020a1fc908851cc0cf1e3ab7bf59b3f9bc3a2075515d983fb7",
              "state_positive": "bfebca8dfb74071580e313cabc6ee42ebcfcb847aa736bd38d02811adf593ed8"
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
          "meaning_id": "18e94843ce26c911566c5ae4bb548485aa24fe5872f1d94205a9aea66949912d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "2ba1c34a592ec1c85b979b827624c3bb9a88a9400d638735a280223afa00664f",
              "liberty": "3e8a3986bd4abff7872f2263b70829a03885d757467fcca5025235f4ed091fce",
              "state_negative": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f",
              "state_positive": "47764f421a2f5a9fdbae8347a27e7c051aeddb051e679348d356da53a476ad8c"
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
          "meaning_id": "7a00e3c209ddd8211d893c343d08a19e50f61d87e53cce13f5ecb85dd7c54ca8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "2ba1c34a592ec1c85b979b827624c3bb9a88a9400d638735a280223afa00664f",
              "anyone_positive": "3e8a3986bd4abff7872f2263b70829a03885d757467fcca5025235f4ed091fce",
              "state_negative": "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f",
              "state_positive": "4c1baa2769f6f76e8192cbaf09c912790b1c351841b13147feb4b373b6eed055"
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
          "meaning_id": "7d4d8ebdd1f563542e10ab5a5f350de8e0a1a43ae1963c5919840de8741cb21e"
        }
      ],
      "situations": {
        "2ba1c34a592ec1c85b979b827624c3bb9a88a9400d638735a280223afa00664f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_opinion_and_expression_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "3e8a3986bd4abff7872f2263b70829a03885d757467fcca5025235f4ed091fce": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_opinion_and_expression",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive"
        },
        "47764f421a2f5a9fdbae8347a27e7c051aeddb051e679348d356da53a476ad8c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_opinion_and_expression_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "4c1baa2769f6f76e8192cbaf09c912790b1c351841b13147feb4b373b6eed055": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_opinion_and_expression",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "977dc2ec6ef8a2613d97636849db233281bcf19ba7558211079ee9f4a326344f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_opinion_and_expression_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        },
        "a9f1e809c01a19020a1fc908851cc0cf1e3ab7bf59b3f9bc3a2075515d983fb7": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_opinion_and_expression_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "bfebca8dfb74071580e313cabc6ee42ebcfcb847aa736bd38d02811adf593ed8": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_opinion_and_expression_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        }
      },
      "status": "open",
      "unit": "u070",
      "version": 1
    },
    {
      "id": "rs_u073",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "232a8ce9c1524699d14dd1d95f214c7d1d1830b9f2db963d57c301d3bc64c5e6",
              "anyone_positive": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017",
              "liberty": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017",
              "state_positive": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017"
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
          "meaning_id": "f7d1f4a3d6c700c49021d8a658515fa92d84122d16e8c30c452def6dcc4d971f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "0acdb52d69c92aa4a5554624dd7a4302375f95cad0498ab4c219ba0389cbcfe9",
              "anyone_positive": "41c8a53e87e3850e6ce28a3727999a66cf291279bc528c056835c0db85e6f6d5",
              "liberty": "2e3a31cf6369bf48953b02ad7cfbc09b4f87548ef8d71d9814753208080de4c7",
              "state_negative": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017"
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
          "meaning_id": "249e0b015fe646d24991d974c81fccc615f1bdf7c54593a8e1f012b5a71a7ac6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_positive": "16c56ca45e856e618528a1818289882b47b4559f27f0f1854dd0ddb7ed8ee414",
              "liberty": "16c56ca45e856e618528a1818289882b47b4559f27f0f1854dd0ddb7ed8ee414",
              "state_negative": "232a8ce9c1524699d14dd1d95f214c7d1d1830b9f2db963d57c301d3bc64c5e6",
              "state_positive": "0acdb52d69c92aa4a5554624dd7a4302375f95cad0498ab4c219ba0389cbcfe9"
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
          "meaning_id": "080b1a2e7212d82a467b6c544ed5d8e6247e10b9873a4b39ee92c57f3c38bd0f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "16c56ca45e856e618528a1818289882b47b4559f27f0f1854dd0ddb7ed8ee414",
              "liberty": "3a918ab9a7422ef867c6f5507b809e709ef9a455f7f08c55ed69be41c49169f5",
              "state_negative": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017",
              "state_positive": "41c8a53e87e3850e6ce28a3727999a66cf291279bc528c056835c0db85e6f6d5"
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
          "meaning_id": "47ce9eb4f0d021ef75b1bc249a956e0055cacaa3d03af37b1dc5be5ddbb8683c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative": "16c56ca45e856e618528a1818289882b47b4559f27f0f1854dd0ddb7ed8ee414",
              "anyone_positive": "3a918ab9a7422ef867c6f5507b809e709ef9a455f7f08c55ed69be41c49169f5",
              "state_negative": "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017",
              "state_positive": "2e3a31cf6369bf48953b02ad7cfbc09b4f87548ef8d71d9814753208080de4c7"
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
          "meaning_id": "0d394dfef48f5223bbc7de816171a9fe3d7f89c27c620c9deac747a3930c63dc"
        }
      ],
      "situations": {
        "0acdb52d69c92aa4a5554624dd7a4302375f95cad0498ab4c219ba0389cbcfe9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_assembly_and_association_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "16c56ca45e856e618528a1818289882b47b4559f27f0f1854dd0ddb7ed8ee414": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_assembly_and_association_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative"
        },
        "232a8ce9c1524699d14dd1d95f214c7d1d1830b9f2db963d57c301d3bc64c5e6": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_assembly_and_association_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative"
        },
        "2e3a31cf6369bf48953b02ad7cfbc09b4f87548ef8d71d9814753208080de4c7": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_assembly_and_association",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "3a918ab9a7422ef867c6f5507b809e709ef9a455f7f08c55ed69be41c49169f5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "person_may_assembly_and_association",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive"
        },
        "41c8a53e87e3850e6ce28a3727999a66cf291279bc528c056835c0db85e6f6d5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_assembly_and_association_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive"
        },
        "946d00a95fba9d5da205cf165d96d7a503a8dc2274b56015ed2bfef48f55c017": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_assembly_and_association_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative"
        }
      },
      "status": "open",
      "unit": "u073",
      "version": 1
    },
    {
      "id": "rs_u017",
      "models": {
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "default": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
              "strict": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
        "ab2607311a949c8ff9ee8fea945ac888e1805b3c2193d3f2e661bf376097306e": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "case_excluded": "ab2607311a949c8ff9ee8fea945ac888e1805b3c2193d3f2e661bf376097306e"
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
              "invocation_barred": "ab2607311a949c8ff9ee8fea945ac888e1805b3c2193d3f2e661bf376097306e"
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
          "meaning_id": "6d449f80a320d41ca9d45bc1667b0b2269b7ee3552b1ba6a0e5a5be77417d974"
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
        "a86bf596d4775ee22c02abb1d3d24a1c8dad9eddaf5d3ca1eda89649c979875f": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [
              [
                "e0"
              ]
            ],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [
              [
                "e0"
              ]
            ],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "exercise_unprotected": "a86bf596d4775ee22c02abb1d3d24a1c8dad9eddaf5d3ca1eda89649c979875f"
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
              "exercise_prohibited": "a86bf596d4775ee22c02abb1d3d24a1c8dad9eddaf5d3ca1eda89649c979875f"
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
          "meaning_id": "4ebccddc3f4023e86b813f6becdc369f59df3465aa28e5b86a22e90a9ffab37b"
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
        "eadf54496014517e1974894f35def9fe68b632be520662b657546189c5827ebd": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [
              [
                "b0"
              ]
            ],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "no_implied_right": "eadf54496014517e1974894f35def9fe68b632be520662b657546189c5827ebd"
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
              "interpretive_ban": "eadf54496014517e1974894f35def9fe68b632be520662b657546189c5827ebd"
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
          "meaning_id": "0cf4026366ca7d388321a736d17d9a37c865cbc32c0d78276486689447ebf4c7"
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
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "state_claim": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 8 read as a duty on a competent national tribunal to provide the victim of a violation of a fundamental right granted by the constitution or by law with an effective remedy. Both conditions are guards on the violation (one person's right violated by one act), so each victim of an act is owed a remedy. Strict force (readings/u035.tribunal_claim.ve.md)."
          },
          "content": null,
          "id": "tribunal_claim",
          "kind": "norm",
          "meaning_id": "3f707ac3d82b3ef628fbc6e7b01cdf3bce10c50fd96becce7678af623a5e099f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "tribunal_claim": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 8 read as a duty on a State to ensure that competent national tribunals give the victim of such a violation an effective remedy (same guard). Strict force (readings/u035.state_claim.ve.md)."
          },
          "content": null,
          "id": "state_claim",
          "kind": "norm",
          "meaning_id": "825b2568ba4104640d68617d096742fd15bb689ec3946ec77f9a31f1e38f0805"
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
        },
        {
          "readings": [
            "tribunal_claim",
            "state_claim"
          ],
          "reason": "Rejected 2026-10-02T1800Z (the duties covered each violating act but had no victim argument, so a remedy for one victim could satisfy the duty while another victim of the same act received none).",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u035",
      "version": 3
    },
    {
      "id": "rs_u051",
      "models": {
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_avoid": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "state_avoid": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
              "anyone_avoid": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "liberty": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 14(1) read as a duty on every State to avoid barring a person who suffers or is threatened with persecution from seeking as well as enjoying asylum in other countries; the guard does not require the person to have begun seeking. No positive duty to grant asylum is a candidate (readings/u051.state_avoid.ve.md)."
          },
          "content": null,
          "id": "state_avoid",
          "kind": "norm",
          "meaning_id": "75d3f2e66f1ea9e3633cab09c2ae5dbed7f5336cb2d41385f2dd711748198ee9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "state_avoid": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "As state_avoid, bound on every State, group and person (the source names no bearer) (readings/u051.anyone_avoid.ve.md)."
          },
          "content": null,
          "id": "anyone_avoid",
          "kind": "norm",
          "meaning_id": "993299f6b5b1ef9e65a345232b808a5fbca56dc4da9e223019e5b56d2b42bb63"
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
        },
        {
          "readings": [
            "liberty",
            "state_avoid",
            "anyone_avoid"
          ],
          "reason": "Rejected 2026-10-02T1800Z (the noninterference duties applied only to someone already seeking or enjoying asylum, leaving a person's opportunity to begin seeking it outside them).",
          "version": 3
        }
      ],
      "status": "open",
      "unit": "u051",
      "version": 4
    },
    {
      "id": "rs_u077",
      "models": {
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "residence_country_claim": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
              "nationality_country_claim": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "liberty": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 15(1) read as an entitlement: whichever bearer owes the person a nationality must grant it. The source names no bearer, so who owes it is the open relation owes_nationality_to; the duty is never on the person and the right is not read as already fulfilled (readings/u054.claim.ve.md)."
          },
          "content": null,
          "id": "claim",
          "kind": "norm",
          "meaning_id": "4013e1cf319cbe64db7206b9a94b6455856df2f2d7afb041b95409cc0c9105ff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "claim": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
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
        },
        {
          "readings": [
            "claim",
            "liberty"
          ],
          "reason": "Rejected 2026-10-02T1800Z (the claim made the person obliged to receive a nationality; a right to a nationality does not oblige its holder to accept one).",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u054",
      "version": 3
    },
    {
      "id": "rs_u111",
      "models": {
        "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf": {
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
            "avoid_arbitrary_arrest_detention_exile_required": [],
            "avoid_arbitrary_deprivation_of_property_required": [],
            "avoid_arbitrary_interference_private_life_required": [],
            "avoid_arbitrary_loss_of_nationality_required": [],
            "avoid_assembly_and_association_required": [],
            "avoid_attacks_upon_honour_and_reputation_required": [],
            "avoid_cultural_life_required": [],
            "avoid_distinction_by_country_status_required": [],
            "avoid_education_required": [],
            "avoid_enjoyment_of_the_arts_required": [],
            "avoid_free_choice_of_employment_required": [],
            "avoid_leave_and_return_required": [],
            "avoid_liberty_required": [],
            "avoid_life_required": [],
            "avoid_marriage_without_free_and_full_consent_required": [],
            "avoid_movement_and_residence_required": [],
            "avoid_opinion_and_expression_required": [],
            "avoid_property_required": [],
            "avoid_security_of_person_required": [],
            "avoid_slavery_and_slave_trade_required": [],
            "avoid_slavery_or_servitude_required": [],
            "avoid_thought_conscience_religion_required": [],
            "avoid_torture_or_ill_treatment_required": [],
            "avoid_trade_unions_required": [],
            "avoid_work_required": [],
            "compel_association_membership_permitted": [],
            "declaration_implies_destructive_right": [],
            "direct_education_to_personality_required": [],
            "direct_education_to_respect_for_rights_required": [],
            "exercise_contrary_to_un": [],
            "is_state": [],
            "make_elementary_education_compulsory_required": [],
            "make_higher_education_accessible_required": [],
            "make_technical_education_available_required": [],
            "of_age_for_elementary_education": [],
            "person_may_assembly_and_association": [],
            "person_may_leave_and_return": [],
            "person_may_movement_and_residence": [],
            "person_may_opinion_and_expression": [],
            "person_may_property": [],
            "person_may_thought_conscience_religion": [],
            "prohibit_slavery_and_slave_trade_required": [],
            "receive_elementary_education_required": [],
            "right_protects_exercise": [],
            "secure_assembly_and_association_required": [],
            "secure_cultural_life_required": [],
            "secure_education_required": [],
            "secure_enjoyment_of_the_arts_required": [],
            "secure_equal_protection_required": [],
            "secure_free_choice_of_employment_required": [],
            "secure_just_and_favourable_conditions_of_work_required": [],
            "secure_liberty_required": [],
            "secure_life_required": [],
            "secure_movement_and_residence_required": [],
            "secure_opinion_and_expression_required": [],
            "secure_property_required": [],
            "secure_protection_against_discrimination_required": [],
            "secure_protection_against_incitement_required": [],
            "secure_protection_against_interference_required": [],
            "secure_protection_against_unemployment_required": [],
            "secure_recognition_as_person_required": [],
            "secure_scientific_advancement_required": [],
            "secure_security_of_person_required": [],
            "secure_social_security_required": [],
            "secure_thought_conscience_religion_required": [],
            "secure_trade_unions_required": [],
            "secure_work_required": []
          }
        }
      },
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as one or both of the two listed aims, and no other; 'shall' read as a strict duty ('must'); the duty is on every State to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.strict_listed_aims_state.ve.md)."
          },
          "content": null,
          "id": "strict_listed_aims_state",
          "kind": "norm",
          "meaning_id": "71c4b4ea701e1c97dc738afd3b4bd49326550932ca95ed676c068d4b27190ffb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as one or both of the two listed aims, and no other; 'shall' read as a strict duty ('must'); the duty is on every State, group and person to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.strict_listed_aims_anyone.ve.md)."
          },
          "content": null,
          "id": "strict_listed_aims_anyone",
          "kind": "norm",
          "meaning_id": "89598e4ea1d38906786d542db3311902d01b073292684a70cca2d1d5db6f2a4e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as requiring both aims; 'shall' read as a strict duty ('must'); the duty is on every State to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.strict_both_aims_state.ve.md)."
          },
          "content": null,
          "id": "strict_both_aims_state",
          "kind": "norm",
          "meaning_id": "f5ff62d37dcc54a1ed333d0f376c781e3c4a72a5df36b7621f1c09da7b30572f"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as requiring both aims; 'shall' read as a strict duty ('must'); the duty is on every State, group and person to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.strict_both_aims_anyone.ve.md)."
          },
          "content": null,
          "id": "strict_both_aims_anyone",
          "kind": "norm",
          "meaning_id": "ba10ea16e2012dcccf5e092e6e1ec9f6387f3a23efe405d76fe0d5d0effb9c09"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as one or both of the two listed aims, and no other; 'shall' read as a defeasible rule ('should': soft-norms@0 companion, exception decided by no stated decider, declared completion 'deny' = not required); the duty is on every State to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.default_listed_aims_state.ve.md)."
          },
          "content": null,
          "id": "default_listed_aims_state",
          "kind": "norm",
          "meaning_id": "e20e6e59fd36717bce79907009a05fcf7532499f3fcd69b8610232a67b985526"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as one or both of the two listed aims, and no other; 'shall' read as a defeasible rule ('should': soft-norms@0 companion, exception decided by no stated decider, declared completion 'deny' = not required); the duty is on every State, group and person to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.default_listed_aims_anyone.ve.md)."
          },
          "content": null,
          "id": "default_listed_aims_anyone",
          "kind": "norm",
          "meaning_id": "a04a5b53518fd54536fa53105942d95a480885447f81b00707b4fcbd3e65f1e7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as requiring both aims; 'shall' read as a defeasible rule ('should': soft-norms@0 companion, exception decided by no stated decider, declared completion 'deny' = not required); the duty is on every State to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.default_both_aims_state.ve.md)."
          },
          "content": null,
          "id": "default_both_aims_state",
          "kind": "norm",
          "meaning_id": "11fa43ff2d7a9fc7fb40b244583d6559e921165b5ca1224ac81d3a6ea0586c45"
        },
        {
          "admission": {
            "distinguishing_models": {
              "default_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "default_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_both_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_anyone": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf",
              "strict_listed_aims_state": "785d286a68d198996e3c1a49f4c16c3bc35fd7d04cc906c1e8cf8772c4266dbf"
            },
            "who": "translator",
            "why": "Article 29(2): 'solely for the purpose of securing A and of meeting B' read as requiring both aims; 'shall' read as a defeasible rule ('should': soft-norms@0 companion, exception decided by no stated decider, declared completion 'deny' = not required); the duty is on every State, group and person to avoid imposing a limitation that is not determined by law or not solely for these aims. The conditions are necessary, never sufficient: a limitation that meets them stays UNDECIDED (readings/u111.default_both_aims_anyone.ve.md)."
          },
          "content": null,
          "id": "default_both_aims_anyone",
          "kind": "norm",
          "meaning_id": "e4b93bbe510d5e125ebabab4c6defcadc552d00787af8c96a59c39a76b409b1b"
        }
      ],
      "rejected_history": [
        {
          "readings": [
            "limitation-29 (rights@0 limitation)"
          ],
          "reason": "rejected by the 2026-10-02T0600Z audit: the assembled document reported zero limitation terms, so the limitation constrained none of the rights, which were all reading-set candidates; it is replaced by norm candidates whose guards carry the necessary conditions",
          "version": 1
        },
        {
          "readings": [
            "strict_listed_aims",
            "strict_both_aims",
            "default_listed_aims",
            "default_both_aims"
          ],
          "reason": "Rejected 2026-10-02T1800Z (the readings obliged every person to be free of each deficient limitation, tied no limitation to the affected person or to a particular right, and put the obligation on the right holder).",
          "version": 2
        }
      ],
      "status": "open",
      "unit": "u111",
      "version": 3
    },
    {
      "id": "rs_u020",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "c677eab28d2b555670d04c15dee36345576ac1ab1f25b8787caf35b6fff2ced8",
              "avoid_anyone_strict": "910cbd12ae987502fd0aa98f13d0e80731ea03575054ea1e9d9fa687c487a709",
              "avoid_state_default": "9a60fe2b47fb94ec3c75b3889483facaa96c28f1237fd04c3bacb1dda4b03707"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid making any distinction against each person by the status of their country. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "no-distinction-by-country-status-avoid-state",
              "over": [],
              "predicate": "avoid_distinction_by_country_status_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "6c6ed9c48112c49005be98e0e57bb500a1e7416895ee3350487889fa08927ac0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "76c4616b2684f8f539df7a0aa5f65ec5b0ce6a90c74a95840e9cde1f72a907f0",
              "avoid_anyone_strict": "9a60fe2b47fb94ec3c75b3889483facaa96c28f1237fd04c3bacb1dda4b03707",
              "avoid_state_strict": "9a60fe2b47fb94ec3c75b3889483facaa96c28f1237fd04c3bacb1dda4b03707"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid making any distinction against each person by the status of their country unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "no-distinction-by-country-status-avoid-state",
              "over": [],
              "predicate": "avoid_distinction_by_country_status_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "d7a602c1f09d8a5959bfbb9fc2780e3b5b0efe2a1e506582e8c4659fba97005e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "c677eab28d2b555670d04c15dee36345576ac1ab1f25b8787caf35b6fff2ced8",
              "avoid_state_default": "9a60fe2b47fb94ec3c75b3889483facaa96c28f1237fd04c3bacb1dda4b03707",
              "avoid_state_strict": "910cbd12ae987502fd0aa98f13d0e80731ea03575054ea1e9d9fa687c487a709"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid making any distinction against each person by the status of their country. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "no-distinction-by-country-status-avoid-anyone",
              "over": [],
              "predicate": "avoid_distinction_by_country_status_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "7b9d6affb746df231278e2624139bab1083354694df968b5fb5b96ad70ace9cc"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "c677eab28d2b555670d04c15dee36345576ac1ab1f25b8787caf35b6fff2ced8",
              "avoid_state_default": "76c4616b2684f8f539df7a0aa5f65ec5b0ce6a90c74a95840e9cde1f72a907f0",
              "avoid_state_strict": "c677eab28d2b555670d04c15dee36345576ac1ab1f25b8787caf35b6fff2ced8"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid making any distinction against each person by the status of their country unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "no-distinction-by-country-status-avoid-anyone",
              "over": [],
              "predicate": "avoid_distinction_by_country_status_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "f697436f4464fd9b370f04cd2d61de6039f9e9fbe38a55320aaf2e7736f64f81"
        }
      ],
      "situations": {
        "76c4616b2684f8f539df7a0aa5f65ec5b0ce6a90c74a95840e9cde1f72a907f0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_distinction_by_country_status_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "910cbd12ae987502fd0aa98f13d0e80731ea03575054ea1e9d9fa687c487a709": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_distinction_by_country_status_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "9a60fe2b47fb94ec3c75b3889483facaa96c28f1237fd04c3bacb1dda4b03707": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-distinction-by-country-status-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_distinction_by_country_status_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "c677eab28d2b555670d04c15dee36345576ac1ab1f25b8787caf35b6fff2ced8": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-distinction-by-country-status-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_distinction_by_country_status_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        }
      },
      "source_word": [
        2537,
        2542
      ],
      "status": "open",
      "unit": "u020",
      "version": 1
    },
    {
      "id": "rs_u024",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "81160e658d6b6699d90d45f8e788b97967b81949530ca21347d873b47074b72a",
              "avoid_anyone_strict": "742b0063a2272797dd42f245e8ac08aca1f563e0a8c8a185ac529d1de0524839",
              "avoid_state_default": "9696633f7c10669d399844a4fe7020a67f1e7c5e264b6ef604c673e2b65b603c"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid holding each person in slavery as well as servitude. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "no-slavery-or-servitude-avoid-state",
              "over": [],
              "predicate": "avoid_slavery_or_servitude_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "72e77b9d01fcf00fb81f713a256673e2c7e816cb2e18080e71c64abb2cadb937"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "17770815409d1b74b78d3cb364cb7d7b8281adb9de44c0d4ce0f594f10c2020c",
              "avoid_anyone_strict": "9696633f7c10669d399844a4fe7020a67f1e7c5e264b6ef604c673e2b65b603c",
              "avoid_state_strict": "9696633f7c10669d399844a4fe7020a67f1e7c5e264b6ef604c673e2b65b603c"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid holding each person in slavery as well as servitude unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "no-slavery-or-servitude-avoid-state",
              "over": [],
              "predicate": "avoid_slavery_or_servitude_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "82235c001cf9369b3a0c582edb3178667d186c0828e4f3982ea2365c0b2d61ad"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "81160e658d6b6699d90d45f8e788b97967b81949530ca21347d873b47074b72a",
              "avoid_state_default": "9696633f7c10669d399844a4fe7020a67f1e7c5e264b6ef604c673e2b65b603c",
              "avoid_state_strict": "742b0063a2272797dd42f245e8ac08aca1f563e0a8c8a185ac529d1de0524839"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid holding each person in slavery as well as servitude. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "no-slavery-or-servitude-avoid-anyone",
              "over": [],
              "predicate": "avoid_slavery_or_servitude_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "30459b19f6ff999d1806dc9157fdf1a3b371c94940a3f9c8518c5dab16146afe"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "81160e658d6b6699d90d45f8e788b97967b81949530ca21347d873b47074b72a",
              "avoid_state_default": "17770815409d1b74b78d3cb364cb7d7b8281adb9de44c0d4ce0f594f10c2020c",
              "avoid_state_strict": "81160e658d6b6699d90d45f8e788b97967b81949530ca21347d873b47074b72a"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid holding each person in slavery as well as servitude unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "no-slavery-or-servitude-avoid-anyone",
              "over": [],
              "predicate": "avoid_slavery_or_servitude_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "f669ab0989ff8760b2dd0b56d03c57967ee9b00ea3904924daab8818f94f3adb"
        }
      ],
      "situations": {
        "17770815409d1b74b78d3cb364cb7d7b8281adb9de44c0d4ce0f594f10c2020c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_or_servitude_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "742b0063a2272797dd42f245e8ac08aca1f563e0a8c8a185ac529d1de0524839": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_or_servitude_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "81160e658d6b6699d90d45f8e788b97967b81949530ca21347d873b47074b72a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-slavery-or-servitude-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_or_servitude_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "9696633f7c10669d399844a4fe7020a67f1e7c5e264b6ef604c673e2b65b603c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-slavery-or-servitude-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_or_servitude_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        }
      },
      "source_word": [
        2876,
        2881
      ],
      "status": "open",
      "unit": "u024",
      "version": 1
    },
    {
      "id": "rs_u025",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "3cc4da37a58ef834fd81df868f78f1d3e5b7cd849d53ac4bf6541f5dab7f5283",
              "avoid_anyone_strict": "834602fce47124cffa33699dab8d70fc1b12bc5d19926d10e0d81d68ac8bc34b",
              "avoid_state_default": "3cc4da37a58ef834fd81df868f78f1d3e5b7cd849d53ac4bf6541f5dab7f5283",
              "avoid_state_strict": "834602fce47124cffa33699dab8d70fc1b12bc5d19926d10e0d81d68ac8bc34b",
              "prohibit_state_default": "94f784688e97d30675254b1f42e06c069eff8f6071d9be076d2a99574dc16f85"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must prohibit slavery as well as the slave trade in all their forms. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "slavery-and-slave-trade-prohibit-state",
              "over": [],
              "predicate": "prohibit_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "prohibit_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "prohibit",
            "force": "strict"
          },
          "meaning_id": "0917037a27308461f9d3ab4adb4873358a1c2b1984357865f9b222995f84bf49"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "501716dcedede16d058de6ec61a8449337512380902163ef94ef2e661d40acbe",
              "avoid_anyone_strict": "c6b69887b10d6a096172a7a885ca1210e445d8fc45753223481eb2fd91b62f94",
              "avoid_state_default": "501716dcedede16d058de6ec61a8449337512380902163ef94ef2e661d40acbe",
              "avoid_state_strict": "c6b69887b10d6a096172a7a885ca1210e445d8fc45753223481eb2fd91b62f94",
              "prohibit_state_strict": "94f784688e97d30675254b1f42e06c069eff8f6071d9be076d2a99574dc16f85"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must prohibit slavery as well as the slave trade in all their forms unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "slavery-and-slave-trade-prohibit-state",
              "over": [],
              "predicate": "prohibit_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "prohibit_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "prohibit",
            "force": "default"
          },
          "meaning_id": "733e6838c4ca8caa625aa9e8b9a3bd90d4bb3d6e94cac054c18355b6079eb96b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "ee053791fa424e2d0835e1ab8a85ae7f49a3bf215c47937eb2c22a3c93a5d5fc",
              "avoid_anyone_strict": "eb2395e32848559eb1c8db2322ca9c18aaedcfc1fb0ec619b88e2f26ab8feabd",
              "avoid_state_default": "59257f46f9b7296e42eba9801cdf60d01aaee90ebeb57bb00fd371f2e5c50b33",
              "prohibit_state_default": "c6b69887b10d6a096172a7a885ca1210e445d8fc45753223481eb2fd91b62f94",
              "prohibit_state_strict": "834602fce47124cffa33699dab8d70fc1b12bc5d19926d10e0d81d68ac8bc34b"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid slavery as well as the slave trade in all their forms. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "slavery-and-slave-trade-avoid-state",
              "over": [],
              "predicate": "avoid_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "avoid",
            "force": "strict"
          },
          "meaning_id": "0db3b725df7dcbeece5de352409c9815f4fbfa76345faa9e3649a49976fa1683"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "1fbfdd4074c02aff986eef9a73e7636c03de7edfd42283691bdf4edee5316da4",
              "avoid_anyone_strict": "59257f46f9b7296e42eba9801cdf60d01aaee90ebeb57bb00fd371f2e5c50b33",
              "avoid_state_strict": "59257f46f9b7296e42eba9801cdf60d01aaee90ebeb57bb00fd371f2e5c50b33",
              "prohibit_state_default": "501716dcedede16d058de6ec61a8449337512380902163ef94ef2e661d40acbe",
              "prohibit_state_strict": "3cc4da37a58ef834fd81df868f78f1d3e5b7cd849d53ac4bf6541f5dab7f5283"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid slavery as well as the slave trade in all their forms unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "slavery-and-slave-trade-avoid-state",
              "over": [],
              "predicate": "avoid_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "avoid",
            "force": "default"
          },
          "meaning_id": "1dff910d7b523710862884d9521a0c681ca571c504e1af967418fb4f957c85d6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "ee053791fa424e2d0835e1ab8a85ae7f49a3bf215c47937eb2c22a3c93a5d5fc",
              "avoid_state_default": "59257f46f9b7296e42eba9801cdf60d01aaee90ebeb57bb00fd371f2e5c50b33",
              "avoid_state_strict": "eb2395e32848559eb1c8db2322ca9c18aaedcfc1fb0ec619b88e2f26ab8feabd",
              "prohibit_state_default": "c6b69887b10d6a096172a7a885ca1210e445d8fc45753223481eb2fd91b62f94",
              "prohibit_state_strict": "834602fce47124cffa33699dab8d70fc1b12bc5d19926d10e0d81d68ac8bc34b"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid slavery as well as the slave trade in all their forms. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "slavery-and-slave-trade-avoid-anyone",
              "over": [],
              "predicate": "avoid_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "duty": "avoid",
            "force": "strict"
          },
          "meaning_id": "121283e237a5abfec0c7407d5c6e5e79e1386bbd1747c70b1fce70afb7213768"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "ee053791fa424e2d0835e1ab8a85ae7f49a3bf215c47937eb2c22a3c93a5d5fc",
              "avoid_state_default": "1fbfdd4074c02aff986eef9a73e7636c03de7edfd42283691bdf4edee5316da4",
              "avoid_state_strict": "ee053791fa424e2d0835e1ab8a85ae7f49a3bf215c47937eb2c22a3c93a5d5fc",
              "prohibit_state_default": "501716dcedede16d058de6ec61a8449337512380902163ef94ef2e661d40acbe",
              "prohibit_state_strict": "3cc4da37a58ef834fd81df868f78f1d3e5b7cd849d53ac4bf6541f5dab7f5283"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid slavery as well as the slave trade in all their forms unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "slavery-and-slave-trade-avoid-anyone",
              "over": [],
              "predicate": "avoid_slavery_and_slave_trade_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "duty": "avoid",
            "force": "default"
          },
          "meaning_id": "e1f3d7d464d99b7c0093c11a2941d423c31d5b359e07032c14a0101132544293"
        }
      ],
      "situations": {
        "1fbfdd4074c02aff986eef9a73e7636c03de7edfd42283691bdf4edee5316da4": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "3cc4da37a58ef834fd81df868f78f1d3e5b7cd849d53ac4bf6541f5dab7f5283": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "prohibit_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "prohibit_state_strict"
        },
        "501716dcedede16d058de6ec61a8449337512380902163ef94ef2e661d40acbe": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "prohibit_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "prohibit_state_default"
        },
        "59257f46f9b7296e42eba9801cdf60d01aaee90ebeb57bb00fd371f2e5c50b33": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "slavery-and-slave-trade-avoid-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "834602fce47124cffa33699dab8d70fc1b12bc5d19926d10e0d81d68ac8bc34b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "prohibit_state_strict"
        },
        "94f784688e97d30675254b1f42e06c069eff8f6071d9be076d2a99574dc16f85": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "slavery-and-slave-trade-prohibit-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "prohibit_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "prohibit_state_default"
        },
        "c6b69887b10d6a096172a7a885ca1210e445d8fc45753223481eb2fd91b62f94": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "prohibit_state_default"
        },
        "eb2395e32848559eb1c8db2322ca9c18aaedcfc1fb0ec619b88e2f26ab8feabd": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "ee053791fa424e2d0835e1ab8a85ae7f49a3bf215c47937eb2c22a3c93a5d5fc": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "slavery-and-slave-trade-avoid-anyone"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_slavery_and_slave_trade_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        }
      },
      "source_word": [
        2943,
        2948
      ],
      "status": "open",
      "unit": "u025",
      "version": 1
    },
    {
      "id": "rs_u027",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "28dd91df71884c9bd041b93a5c99341510a3a0e2e760b394dfa8cbb7f5d0ecdf",
              "avoid_anyone_strict": "bc28e57839838e8ff48311d334cd2702c1bea01793ca15b653139cf222716390",
              "avoid_state_default": "1f8e4d37f932c5298ea2c157018be14da5157544e159fadc8c2e7010e6e7dd38"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid subjecting each person to torture as well as ill-treatment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "no-torture-or-ill-treatment-avoid-state",
              "over": [],
              "predicate": "avoid_torture_or_ill_treatment_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "fe1e5ed1f67d71d207933f5c4382f92d6e5913f7f29c73d8ed26104bf377f8d8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "717c6909c1de3de3b6d6e9910c2fce6631aff2267c7e0057990d7f74a1e507de",
              "avoid_anyone_strict": "1f8e4d37f932c5298ea2c157018be14da5157544e159fadc8c2e7010e6e7dd38",
              "avoid_state_strict": "1f8e4d37f932c5298ea2c157018be14da5157544e159fadc8c2e7010e6e7dd38"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid subjecting each person to torture as well as ill-treatment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "no-torture-or-ill-treatment-avoid-state",
              "over": [],
              "predicate": "avoid_torture_or_ill_treatment_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "5b1de5ce3d941602bf68b7189aec27f801702e240f7200bef893a497e71d4c4a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "28dd91df71884c9bd041b93a5c99341510a3a0e2e760b394dfa8cbb7f5d0ecdf",
              "avoid_state_default": "1f8e4d37f932c5298ea2c157018be14da5157544e159fadc8c2e7010e6e7dd38",
              "avoid_state_strict": "bc28e57839838e8ff48311d334cd2702c1bea01793ca15b653139cf222716390"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid subjecting each person to torture as well as ill-treatment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "no-torture-or-ill-treatment-avoid-anyone",
              "over": [],
              "predicate": "avoid_torture_or_ill_treatment_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "19fa0d2d7d60600c8a33666618dea472fb205ad6c8caed2035972faef56ddef8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "28dd91df71884c9bd041b93a5c99341510a3a0e2e760b394dfa8cbb7f5d0ecdf",
              "avoid_state_default": "717c6909c1de3de3b6d6e9910c2fce6631aff2267c7e0057990d7f74a1e507de",
              "avoid_state_strict": "28dd91df71884c9bd041b93a5c99341510a3a0e2e760b394dfa8cbb7f5d0ecdf"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid subjecting each person to torture as well as ill-treatment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "no-torture-or-ill-treatment-avoid-anyone",
              "over": [],
              "predicate": "avoid_torture_or_ill_treatment_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "3c9815abe0e698e372133a4605d4497b7c62ac3ec7e5f99b1a39d9cdfdb0cd33"
        }
      ],
      "situations": {
        "1f8e4d37f932c5298ea2c157018be14da5157544e159fadc8c2e7010e6e7dd38": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-torture-or-ill-treatment-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_torture_or_ill_treatment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "28dd91df71884c9bd041b93a5c99341510a3a0e2e760b394dfa8cbb7f5d0ecdf": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-torture-or-ill-treatment-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_torture_or_ill_treatment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "717c6909c1de3de3b6d6e9910c2fce6631aff2267c7e0057990d7f74a1e507de": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_torture_or_ill_treatment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "bc28e57839838e8ff48311d334cd2702c1bea01793ca15b653139cf222716390": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_torture_or_ill_treatment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        }
      },
      "source_word": [
        3005,
        3010
      ],
      "status": "open",
      "unit": "u027",
      "version": 1
    },
    {
      "id": "rs_u037",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "f8d30b95520404437e24431865a6128012a122c460e3a0d4c4826673b6af3fd7",
              "avoid_anyone_strict": "db768d357728f9f25d3bc3277a88adc919e0e1bdbc91ad2376e317d6617af2e5",
              "avoid_state_default": "9f6e3994210c58071729591de9b7aa427a827a0a3eb05fbec499816d4b95c97e"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid arbitrarily arresting each person as well as detaining as well as exiling them. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "arbitrary-arrest-detention-exile-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "98ecb2ab17566b1311451bf3d8c87d8abd50885740010dd3f09716503782e600"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "818a275cadf032682eaa91a61a1c53a627f8233a8b74fe75d78d73e8c8896ae6",
              "avoid_anyone_strict": "9f6e3994210c58071729591de9b7aa427a827a0a3eb05fbec499816d4b95c97e",
              "avoid_state_strict": "9f6e3994210c58071729591de9b7aa427a827a0a3eb05fbec499816d4b95c97e"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid arbitrarily arresting each person as well as detaining as well as exiling them unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "arbitrary-arrest-detention-exile-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "1f14efbd10714c681cf6db0d77903b22f460a15661b401440dc6cb56ee19dfdf"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "f8d30b95520404437e24431865a6128012a122c460e3a0d4c4826673b6af3fd7",
              "avoid_state_default": "9f6e3994210c58071729591de9b7aa427a827a0a3eb05fbec499816d4b95c97e",
              "avoid_state_strict": "db768d357728f9f25d3bc3277a88adc919e0e1bdbc91ad2376e317d6617af2e5"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid arbitrarily arresting each person as well as detaining as well as exiling them. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "arbitrary-arrest-detention-exile-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "34594e2e9fc44fe071d8ebce9a05880c880bd0bc7144ab9649d01c694e8fb79c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "f8d30b95520404437e24431865a6128012a122c460e3a0d4c4826673b6af3fd7",
              "avoid_state_default": "818a275cadf032682eaa91a61a1c53a627f8233a8b74fe75d78d73e8c8896ae6",
              "avoid_state_strict": "f8d30b95520404437e24431865a6128012a122c460e3a0d4c4826673b6af3fd7"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid arbitrarily arresting each person as well as detaining as well as exiling them unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "arbitrary-arrest-detention-exile-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "8eb298919e90c9c184f64340a801759f556b351bef58bb1e9563023cab91edec"
        }
      ],
      "situations": {
        "818a275cadf032682eaa91a61a1c53a627f8233a8b74fe75d78d73e8c8896ae6": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "9f6e3994210c58071729591de9b7aa427a827a0a3eb05fbec499816d4b95c97e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "arbitrary-arrest-detention-exile-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "db768d357728f9f25d3bc3277a88adc919e0e1bdbc91ad2376e317d6617af2e5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "f8d30b95520404437e24431865a6128012a122c460e3a0d4c4826673b6af3fd7": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "arbitrary-arrest-detention-exile-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_arrest_detention_exile_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        }
      },
      "source_word": [
        3658,
        3663
      ],
      "status": "open",
      "unit": "u037",
      "version": 1
    },
    {
      "id": "rs_u045a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "3a0b82e0fff7696178ce4346a6a62a2f67e089c97dfd3765e72944c450644376",
              "avoid_anyone_strict": "e121294351d5bdb4bfeae2163adcdbb15a8b59a7561d3ba7757d7abd140c0441",
              "avoid_state_default": "440e5a4cf6e6f8aa7b4611c4de19fc25f5986472c0d4ab6a3c931517517293d3"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid arbitrary interference with the private life of each person. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "interference-with-private-life-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "6f3303520c06f1ee5c61157624ce920a3fffea303771ec312718a5e9558d873e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "9ba34234d2c125fc17e0ac7783f0002541ce76d5f511be6a13e34b58ddcf0e4b",
              "avoid_anyone_strict": "440e5a4cf6e6f8aa7b4611c4de19fc25f5986472c0d4ab6a3c931517517293d3",
              "avoid_state_strict": "440e5a4cf6e6f8aa7b4611c4de19fc25f5986472c0d4ab6a3c931517517293d3"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid arbitrary interference with the private life of each person unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "interference-with-private-life-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "78bae1a97489c44348c490c2684c6e4391a0cf80c874cdde845249071caec556"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "3a0b82e0fff7696178ce4346a6a62a2f67e089c97dfd3765e72944c450644376",
              "avoid_state_default": "440e5a4cf6e6f8aa7b4611c4de19fc25f5986472c0d4ab6a3c931517517293d3",
              "avoid_state_strict": "e121294351d5bdb4bfeae2163adcdbb15a8b59a7561d3ba7757d7abd140c0441"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid arbitrary interference with the private life of each person. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "interference-with-private-life-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "7e0b3ab01976276b67641d8aaeab613e3b6539217a1dced0d1fe70265e8a42b7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "3a0b82e0fff7696178ce4346a6a62a2f67e089c97dfd3765e72944c450644376",
              "avoid_state_default": "9ba34234d2c125fc17e0ac7783f0002541ce76d5f511be6a13e34b58ddcf0e4b",
              "avoid_state_strict": "3a0b82e0fff7696178ce4346a6a62a2f67e089c97dfd3765e72944c450644376"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid arbitrary interference with the private life of each person unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "interference-with-private-life-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "6531f24216a0dee7c93792adc1d4229178fd3914093a93e85d73e4cc85902982"
        }
      ],
      "situations": {
        "3a0b82e0fff7696178ce4346a6a62a2f67e089c97dfd3765e72944c450644376": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "interference-with-private-life-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "440e5a4cf6e6f8aa7b4611c4de19fc25f5986472c0d4ab6a3c931517517293d3": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "interference-with-private-life-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "9ba34234d2c125fc17e0ac7783f0002541ce76d5f511be6a13e34b58ddcf0e4b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "e121294351d5bdb4bfeae2163adcdbb15a8b59a7561d3ba7757d7abd140c0441": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_interference_private_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        }
      },
      "source_word": [
        4491,
        4496
      ],
      "status": "open",
      "unit": "u045a",
      "version": 1
    },
    {
      "id": "rs_u045b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "04ef5ff50e221013c6bb59ed2bdb5ecad9ac8985853f9d3f97ffa8a80d04beed",
              "avoid_anyone_strict": "984aba543e52cce1f14291ea3f4a5a7711d628ea0c0366e9e0df1ccc0ca5b0c1",
              "avoid_state_default": "fecf703f202ca682652d8035a7925ca33bfeafd3e5c936ea7ea3cd015b6225ea"
            },
            "who": "translator",
            "why": "Strict reading (the source carries or opens its force): every state must avoid attacks upon the honour as well as reputation of each person. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "attacks-upon-honour-reputation-avoid-state",
              "over": [],
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "542e1ee892d9761f6cc0e57cb3c3168628e6f06bd0b145717666c04c41122c9e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "6ae763f51ed5eb4282b374c4af7ca982f1118c60a0dd6c7cf91ee9540ff59b1f",
              "avoid_anyone_strict": "fecf703f202ca682652d8035a7925ca33bfeafd3e5c936ea7ea3cd015b6225ea",
              "avoid_state_strict": "fecf703f202ca682652d8035a7925ca33bfeafd3e5c936ea7ea3cd015b6225ea"
            },
            "who": "translator",
            "why": "Defeasible reading (the source carries or opens its force): every state must avoid attacks upon the honour as well as reputation of each person unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "attacks-upon-honour-reputation-avoid-state",
              "over": [],
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "974efe836c17ee68ea11352c796fdc1f82926347de4d7f27d364e24852873c9d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "04ef5ff50e221013c6bb59ed2bdb5ecad9ac8985853f9d3f97ffa8a80d04beed",
              "avoid_state_default": "fecf703f202ca682652d8035a7925ca33bfeafd3e5c936ea7ea3cd015b6225ea",
              "avoid_state_strict": "984aba543e52cce1f14291ea3f4a5a7711d628ea0c0366e9e0df1ccc0ca5b0c1"
            },
            "who": "translator",
            "why": "Strict reading (the source carries or opens its force): every state, group and person must avoid attacks upon the honour as well as reputation of each person. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "attacks-upon-honour-reputation-avoid-anyone",
              "over": [],
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "4f0440fe4c1ce5ff586861ecbe22a1583beb8faca08b53255997cd2fa5ccf40e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "04ef5ff50e221013c6bb59ed2bdb5ecad9ac8985853f9d3f97ffa8a80d04beed",
              "avoid_state_default": "6ae763f51ed5eb4282b374c4af7ca982f1118c60a0dd6c7cf91ee9540ff59b1f",
              "avoid_state_strict": "04ef5ff50e221013c6bb59ed2bdb5ecad9ac8985853f9d3f97ffa8a80d04beed"
            },
            "who": "translator",
            "why": "Defeasible reading (the source carries or opens its force): every state, group and person must avoid attacks upon the honour as well as reputation of each person unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "attacks-upon-honour-reputation-avoid-anyone",
              "over": [],
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "0b3a5db5e9fb27ad84a0c5e947658d9e0fb5979940e6e061625c07c068adc957"
        }
      ],
      "situations": {
        "04ef5ff50e221013c6bb59ed2bdb5ecad9ac8985853f9d3f97ffa8a80d04beed": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "attacks-upon-honour-reputation-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "6ae763f51ed5eb4282b374c4af7ca982f1118c60a0dd6c7cf91ee9540ff59b1f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "984aba543e52cce1f14291ea3f4a5a7711d628ea0c0366e9e0df1ccc0ca5b0c1": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "fecf703f202ca682652d8035a7925ca33bfeafd3e5c936ea7ea3cd015b6225ea": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "attacks-upon-honour-reputation-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_attacks_upon_honour_and_reputation_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        }
      },
      "status": "open",
      "unit": "u045b",
      "version": 1
    },
    {
      "id": "rs_u055",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "517b81127accdd40bd500f0120d0baa42b79a32383dd760b3c14bea0448163d0",
              "avoid_anyone_strict": "d5d2204661046b52f4c728e8761fc9bee98f719ef2c19f5ae4c30bb651965ded",
              "avoid_state_default": "4219a79133fe40f7b5ff2ec35c98e259312493fe6ac2b9dd477355e5629546d5"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid arbitrarily depriving each person of nationality as well as barring its change. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "no-arbitrary-loss-of-nationality-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "e933e3c93bcd949c1bce1b64b0ee48b378da447ae846435b4181e1dc721a77e4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "ef66f47d9a8c7a463d1f5413e483c2a145c7703ef41cc73416185af8c0b8dca9",
              "avoid_anyone_strict": "4219a79133fe40f7b5ff2ec35c98e259312493fe6ac2b9dd477355e5629546d5",
              "avoid_state_strict": "4219a79133fe40f7b5ff2ec35c98e259312493fe6ac2b9dd477355e5629546d5"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid arbitrarily depriving each person of nationality as well as barring its change unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "no-arbitrary-loss-of-nationality-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "5913d4b31ebc58ff6d5e0aa5b6c8ca92d881c2587721c3300cfe3e7cb83c4146"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "517b81127accdd40bd500f0120d0baa42b79a32383dd760b3c14bea0448163d0",
              "avoid_state_default": "4219a79133fe40f7b5ff2ec35c98e259312493fe6ac2b9dd477355e5629546d5",
              "avoid_state_strict": "d5d2204661046b52f4c728e8761fc9bee98f719ef2c19f5ae4c30bb651965ded"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid arbitrarily depriving each person of nationality as well as barring its change. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "no-arbitrary-loss-of-nationality-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "6300ef3fa9835886e4a9d6e9fc4b30e8316a73c1c3d2a54670f1b21d5add6829"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "517b81127accdd40bd500f0120d0baa42b79a32383dd760b3c14bea0448163d0",
              "avoid_state_default": "ef66f47d9a8c7a463d1f5413e483c2a145c7703ef41cc73416185af8c0b8dca9",
              "avoid_state_strict": "517b81127accdd40bd500f0120d0baa42b79a32383dd760b3c14bea0448163d0"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid arbitrarily depriving each person of nationality as well as barring its change unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "no-arbitrary-loss-of-nationality-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "2a9f03182d2a7eb9e6f5a47dd6af3528438a36de9b6f9e80e3f06d08f15299b9"
        }
      ],
      "situations": {
        "4219a79133fe40f7b5ff2ec35c98e259312493fe6ac2b9dd477355e5629546d5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-arbitrary-loss-of-nationality-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "517b81127accdd40bd500f0120d0baa42b79a32383dd760b3c14bea0448163d0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-arbitrary-loss-of-nationality-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "d5d2204661046b52f4c728e8761fc9bee98f719ef2c19f5ae4c30bb651965ded": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "ef66f47d9a8c7a463d1f5413e483c2a145c7703ef41cc73416185af8c0b8dca9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_loss_of_nationality_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        }
      },
      "source_word": [
        5294,
        5299
      ],
      "status": "open",
      "unit": "u055",
      "version": 1
    },
    {
      "id": "rs_u059",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "63cd9ab348f919fd0007690223c35349f49ad0bd3b8b7066d81bf392b5d278d4",
              "avoid_anyone_strict": "fcfa68bc17950247625d7b3633e95274e287e9bf25c9a0048723a83dbba818f0",
              "avoid_state_default": "c91c837ca9b980ef661bf176614f1d5effe85aced71d97e72fd5d4afbaf5aa6e"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid entering each person into marriage without their free as well as full consent. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "marriage-only-with-consent-avoid-state",
              "over": [],
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "cc39419de668c87f4eaebf633b6f91921b5b4f088a6166543ac53c3c65b6d220"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "302e14811e76daa32384521e0aec10eaf1616ea8c97fc71893387e42a19f2131",
              "avoid_anyone_strict": "c91c837ca9b980ef661bf176614f1d5effe85aced71d97e72fd5d4afbaf5aa6e",
              "avoid_state_strict": "c91c837ca9b980ef661bf176614f1d5effe85aced71d97e72fd5d4afbaf5aa6e"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid entering each person into marriage without their free as well as full consent unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "marriage-only-with-consent-avoid-state",
              "over": [],
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "b57359db83bcca9f1bd7e4b25e8d98bf187caf85a85255958d3c16ab8f19376d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "63cd9ab348f919fd0007690223c35349f49ad0bd3b8b7066d81bf392b5d278d4",
              "avoid_state_default": "c91c837ca9b980ef661bf176614f1d5effe85aced71d97e72fd5d4afbaf5aa6e",
              "avoid_state_strict": "fcfa68bc17950247625d7b3633e95274e287e9bf25c9a0048723a83dbba818f0"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid entering each person into marriage without their free as well as full consent. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "marriage-only-with-consent-avoid-anyone",
              "over": [],
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "ffe56b7e73e7f81aa04c13352960cf6119fbf8c4a6128d0229de6ffd69a5011c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "63cd9ab348f919fd0007690223c35349f49ad0bd3b8b7066d81bf392b5d278d4",
              "avoid_state_default": "302e14811e76daa32384521e0aec10eaf1616ea8c97fc71893387e42a19f2131",
              "avoid_state_strict": "63cd9ab348f919fd0007690223c35349f49ad0bd3b8b7066d81bf392b5d278d4"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid entering each person into marriage without their free as well as full consent unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "marriage-only-with-consent-avoid-anyone",
              "over": [],
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "9da788e3061a71aed5bc2edbd756f7e651598bf437e9fa5fbfb32ecf298e9862"
        }
      ],
      "situations": {
        "302e14811e76daa32384521e0aec10eaf1616ea8c97fc71893387e42a19f2131": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        },
        "63cd9ab348f919fd0007690223c35349f49ad0bd3b8b7066d81bf392b5d278d4": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "marriage-only-with-consent-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "c91c837ca9b980ef661bf176614f1d5effe85aced71d97e72fd5d4afbaf5aa6e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "marriage-only-with-consent-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "fcfa68bc17950247625d7b3633e95274e287e9bf25c9a0048723a83dbba818f0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_marriage_without_free_and_full_consent_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        }
      },
      "source_word": [
        5648,
        5653
      ],
      "status": "open",
      "unit": "u059",
      "version": 1
    },
    {
      "id": "rs_u064",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "489ef1e7492443f57d8ed5455a911c0ae10cd974a22492069746527efc61f388",
              "avoid_anyone_strict": "1f0f4cce800f8c967e607a462b540508e20e431775f8c735a0753a612259b123",
              "avoid_state_default": "1df4df34f4ade86cffd68792245f78a239fc3003a45fffd87de4cf6f4efe6a9e"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must avoid arbitrarily depriving each person of property. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "name": "no-arbitrary-loss-of-property-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "42955a789ec1333b3312743d5d6b01813017bf757e6f916e5192e760306746c7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "5f72906bbdcc60af297f2a714ff1deafa6cce788b272d51dc599972a532c2032",
              "avoid_anyone_strict": "1df4df34f4ade86cffd68792245f78a239fc3003a45fffd87de4cf6f4efe6a9e",
              "avoid_state_strict": "1df4df34f4ade86cffd68792245f78a239fc3003a45fffd87de4cf6f4efe6a9e"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must avoid arbitrarily depriving each person of property unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  1
                ]
              ],
              "mode": "default",
              "name": "no-arbitrary-loss-of-property-avoid-state",
              "over": [],
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "577192e0814fee57f711cdd5a4a0dc07f8afbc6ac27ed397d37a11a358dced41"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_default": "489ef1e7492443f57d8ed5455a911c0ae10cd974a22492069746527efc61f388",
              "avoid_state_default": "1df4df34f4ade86cffd68792245f78a239fc3003a45fffd87de4cf6f4efe6a9e",
              "avoid_state_strict": "1f0f4cce800f8c967e607a462b540508e20e431775f8c735a0753a612259b123"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must avoid arbitrarily depriving each person of property. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "no-arbitrary-loss-of-property-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "7a8eb961df3e5bc365615318fcee53ddbff502462285c8c6636509425113fa65"
        },
        {
          "admission": {
            "distinguishing_models": {
              "avoid_anyone_strict": "489ef1e7492443f57d8ed5455a911c0ae10cd974a22492069746527efc61f388",
              "avoid_state_default": "5f72906bbdcc60af297f2a714ff1deafa6cce788b272d51dc599972a532c2032",
              "avoid_state_strict": "489ef1e7492443f57d8ed5455a911c0ae10cd974a22492069746527efc61f388"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must avoid arbitrarily depriving each person of property unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "no-arbitrary-loss-of-property-avoid-anyone",
              "over": [],
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "avoid_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "7689261e707a238fab5a1f0ae5ab465027878a64110279413a98c9a3c711addd"
        }
      ],
      "situations": {
        "1df4df34f4ade86cffd68792245f78a239fc3003a45fffd87de4cf6f4efe6a9e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-arbitrary-loss-of-property-avoid-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_default"
        },
        "1f0f4cce800f8c967e607a462b540508e20e431775f8c735a0753a612259b123": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_state_strict"
        },
        "489ef1e7492443f57d8ed5455a911c0ae10cd974a22492069746527efc61f388": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "no-arbitrary-loss-of-property-avoid-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "avoid_anyone_default"
        },
        "5f72906bbdcc60af297f2a714ff1deafa6cce788b272d51dc599972a532c2032": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_arbitrary_deprivation_of_property_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "avoid_anyone_default"
        }
      },
      "source_word": [
        5970,
        5975
      ],
      "status": "open",
      "unit": "u064",
      "version": 1
    },
    {
      "id": "rs_u098",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "receive_default": "89daac09a04907b306cc87e9351f7b001d030353b6ce42e7cbfc0c82ebe1367a",
              "require_state_default": "cd6019da13bea3f687141c7129d728872534c4480e576d1805c115b114bea682",
              "require_state_strict": "cd6019da13bea3f687141c7129d728872534c4480e576d1805c115b114bea682"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): each person must receive elementary education. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. Scope: only where the person is of the age for elementary education (a named open relation; the source states no age)."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "of_age_for_elementary_education",
                [
                  "var",
                  0
                ]
              ],
              "name": "elementary-education-compulsory-receive",
              "over": [],
              "predicate": "receive_elementary_education_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "receive_strict",
          "kind": "norm",
          "labels": {
            "duty": "receive",
            "force": "strict"
          },
          "meaning_id": "2f6c65b3be1e2d313354f13959b97c1f9176854b37322b21f8149f09da709521"
        },
        {
          "admission": {
            "distinguishing_models": {
              "receive_strict": "89daac09a04907b306cc87e9351f7b001d030353b6ce42e7cbfc0c82ebe1367a",
              "require_state_default": "87b28af53bd9e5fe14488510167ac308b2ba28eab5acd3a7ad0bf0df59789a52",
              "require_state_strict": "87b28af53bd9e5fe14488510167ac308b2ba28eab5acd3a7ad0bf0df59789a52"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): each person must receive elementary education unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. Scope: only where the person is of the age for elementary education (a named open relation; the source states no age)."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "of_age_for_elementary_education",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "elementary-education-compulsory-receive",
              "over": [],
              "predicate": "receive_elementary_education_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "receive_default",
          "kind": "norm",
          "labels": {
            "duty": "receive",
            "force": "default"
          },
          "meaning_id": "80339d8f5d029099beb3d0c64658cd9cd8e520a3c6d5f7f5b8e6b80b4a401fdb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "receive_default": "87b28af53bd9e5fe14488510167ac308b2ba28eab5acd3a7ad0bf0df59789a52",
              "receive_strict": "cd6019da13bea3f687141c7129d728872534c4480e576d1805c115b114bea682",
              "require_state_default": "3661cde381c1b00c52b5e6909f5d4d79d91c298344e6daaf81b65e4fa672ba4d"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must make elementary education compulsory. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "elementary-education-compulsory-require-state",
              "over": [],
              "predicate": "make_elementary_education_compulsory_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "require_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "require",
            "force": "strict"
          },
          "meaning_id": "b3378a6e115314731cfe6f2c75806b73db1195dcd88f7835dc77ac04b59d4ae6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "receive_default": "87b28af53bd9e5fe14488510167ac308b2ba28eab5acd3a7ad0bf0df59789a52",
              "receive_strict": "cd6019da13bea3f687141c7129d728872534c4480e576d1805c115b114bea682",
              "require_state_strict": "3661cde381c1b00c52b5e6909f5d4d79d91c298344e6daaf81b65e4fa672ba4d"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must make elementary education compulsory unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "elementary-education-compulsory-require-state",
              "over": [],
              "predicate": "make_elementary_education_compulsory_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "require_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "duty": "require",
            "force": "default"
          },
          "meaning_id": "cd37913829e0b4ba1727cf13ead243a88460b80658a254a5f4ecca14ded62bfc"
        }
      ],
      "situations": {
        "3661cde381c1b00c52b5e6909f5d4d79d91c298344e6daaf81b65e4fa672ba4d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "elementary-education-compulsory-require-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_elementary_education_compulsory_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "require_state_default"
        },
        "87b28af53bd9e5fe14488510167ac308b2ba28eab5acd3a7ad0bf0df59789a52": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [
                [
                  "person"
                ]
              ],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "receive_elementary_education_required",
              "tuple": [
                "person"
              ]
            }
          },
          "value": true,
          "witness": "receive_default"
        },
        "89daac09a04907b306cc87e9351f7b001d030353b6ce42e7cbfc0c82ebe1367a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [
                [
                  "person"
                ]
              ],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "elementary-education-compulsory-receive"
              },
              "tuples": [
                [
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "receive_elementary_education_required",
              "tuple": [
                "person"
              ]
            }
          },
          "value": false,
          "witness": "receive_default"
        },
        "cd6019da13bea3f687141c7129d728872534c4480e576d1805c115b114bea682": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [
                [
                  "person"
                ]
              ],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "receive_elementary_education_required",
              "tuple": [
                "person"
              ]
            }
          },
          "value": true,
          "witness": "receive_strict"
        }
      },
      "source_word": [
        8954,
        8959
      ],
      "status": "open",
      "unit": "u098",
      "version": 1
    },
    {
      "id": "rs_u099a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "26e89d14eef2a94099e5b6f449d55ea6dfa9ea170d584a4aa7d7c64d6f0ac523",
              "make_anyone_strict": "7c8ab6e28d0c435702af33988e09a8bb1646331e9bb4c2a9c9a5fa9e53a310d0",
              "make_state_default": "c323f691a540159fdec65dba0bb44f67d08b558c4cd4a38b099db4d207cbfb9f"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must make technical as well as professional education generally available. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "technical-education-available-make-state",
              "over": [],
              "predicate": "make_technical_education_available_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "f2234da9f32da511180160d2bfb5696fe0bbd9e5ff044755043e7ff8126777ff"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "ec14cfd13cb221170c3a5c144436cb538e8d2a1056d4b8b8b422997ffac2d1a9",
              "make_anyone_strict": "c323f691a540159fdec65dba0bb44f67d08b558c4cd4a38b099db4d207cbfb9f",
              "make_state_strict": "c323f691a540159fdec65dba0bb44f67d08b558c4cd4a38b099db4d207cbfb9f"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must make technical as well as professional education generally available unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "technical-education-available-make-state",
              "over": [],
              "predicate": "make_technical_education_available_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "8a4736e8bc824a962cf82aed8976a5027bb7bf2d23a80a18c565ddda0956e7d5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "26e89d14eef2a94099e5b6f449d55ea6dfa9ea170d584a4aa7d7c64d6f0ac523",
              "make_state_default": "c323f691a540159fdec65dba0bb44f67d08b558c4cd4a38b099db4d207cbfb9f",
              "make_state_strict": "7c8ab6e28d0c435702af33988e09a8bb1646331e9bb4c2a9c9a5fa9e53a310d0"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must make technical as well as professional education generally available. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "technical-education-available-make-anyone",
              "over": [],
              "predicate": "make_technical_education_available_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "0bbeb4755b3e18dd3e544ee55a8118a755caaee9cc8fef39f2028e356dd5f79b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_strict": "26e89d14eef2a94099e5b6f449d55ea6dfa9ea170d584a4aa7d7c64d6f0ac523",
              "make_state_default": "ec14cfd13cb221170c3a5c144436cb538e8d2a1056d4b8b8b422997ffac2d1a9",
              "make_state_strict": "26e89d14eef2a94099e5b6f449d55ea6dfa9ea170d584a4aa7d7c64d6f0ac523"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must make technical as well as professional education generally available unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "technical-education-available-make-anyone",
              "over": [],
              "predicate": "make_technical_education_available_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "924cea13783b9fe7a47d51067411ce36a0f7698e9e20864e68813acce6b98f3c"
        }
      ],
      "situations": {
        "26e89d14eef2a94099e5b6f449d55ea6dfa9ea170d584a4aa7d7c64d6f0ac523": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "technical-education-available-make-anyone"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_technical_education_available_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_anyone_default"
        },
        "7c8ab6e28d0c435702af33988e09a8bb1646331e9bb4c2a9c9a5fa9e53a310d0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_technical_education_available_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_state_strict"
        },
        "c323f691a540159fdec65dba0bb44f67d08b558c4cd4a38b099db4d207cbfb9f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "technical-education-available-make-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_technical_education_available_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_state_default"
        },
        "ec14cfd13cb221170c3a5c144436cb538e8d2a1056d4b8b8b422997ffac2d1a9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_technical_education_available_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "make_anyone_default"
        }
      },
      "source_word": [
        9012,
        9017
      ],
      "status": "open",
      "unit": "u099a",
      "version": 1
    },
    {
      "id": "rs_u099b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "309e46894633fd82f1d5c2622eafebbd8ebda83524e34e613dcf96805b8d7913",
              "make_anyone_strict": "53a4831a00775a1a2a57f4d51d8aa5f1b24a02e3d3e64c8b0c3f0ed5bbfb200e",
              "make_state_default": "84a941c6adc77cdeb7592c418c6e1a0e31f3c6caef7c14d3d9bd8213f584ba64"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must make higher education equally accessible to all on the basis of merit. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "higher-education-on-merit-make-state",
              "over": [],
              "predicate": "make_higher_education_accessible_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "77a8dff53fd0f273eaf9f1c525396f407c1f150b34acd54aa528542111f5b431"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "aaa3dce191113c003de39e39e84de3119bfc4f56c589056eba4f0e1670db6241",
              "make_anyone_strict": "84a941c6adc77cdeb7592c418c6e1a0e31f3c6caef7c14d3d9bd8213f584ba64",
              "make_state_strict": "84a941c6adc77cdeb7592c418c6e1a0e31f3c6caef7c14d3d9bd8213f584ba64"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must make higher education equally accessible to all on the basis of merit unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "higher-education-on-merit-make-state",
              "over": [],
              "predicate": "make_higher_education_accessible_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "9cbc5899732becc4a582fcc61fd37fd2f4810a8657a80a49f363ef8d3af2556d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_default": "309e46894633fd82f1d5c2622eafebbd8ebda83524e34e613dcf96805b8d7913",
              "make_state_default": "84a941c6adc77cdeb7592c418c6e1a0e31f3c6caef7c14d3d9bd8213f584ba64",
              "make_state_strict": "53a4831a00775a1a2a57f4d51d8aa5f1b24a02e3d3e64c8b0c3f0ed5bbfb200e"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must make higher education equally accessible to all on the basis of merit. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "higher-education-on-merit-make-anyone",
              "over": [],
              "predicate": "make_higher_education_accessible_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "c2ff4d4040c7356ff343386b7972a8b75cf24f10ab0aa9505b006d5e65392cdd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "make_anyone_strict": "309e46894633fd82f1d5c2622eafebbd8ebda83524e34e613dcf96805b8d7913",
              "make_state_default": "aaa3dce191113c003de39e39e84de3119bfc4f56c589056eba4f0e1670db6241",
              "make_state_strict": "309e46894633fd82f1d5c2622eafebbd8ebda83524e34e613dcf96805b8d7913"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must make higher education equally accessible to all on the basis of merit unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "higher-education-on-merit-make-anyone",
              "over": [],
              "predicate": "make_higher_education_accessible_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "make_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "4f4f4802c2a159138a9baf85e792e5e5754b5bcdcda5f0d03d0d99ef99740498"
        }
      ],
      "situations": {
        "309e46894633fd82f1d5c2622eafebbd8ebda83524e34e613dcf96805b8d7913": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "higher-education-on-merit-make-anyone"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_higher_education_accessible_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_anyone_default"
        },
        "53a4831a00775a1a2a57f4d51d8aa5f1b24a02e3d3e64c8b0c3f0ed5bbfb200e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_higher_education_accessible_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_state_strict"
        },
        "84a941c6adc77cdeb7592c418c6e1a0e31f3c6caef7c14d3d9bd8213f584ba64": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "higher-education-on-merit-make-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_higher_education_accessible_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "make_state_default"
        },
        "aaa3dce191113c003de39e39e84de3119bfc4f56c589056eba4f0e1670db6241": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "make_higher_education_accessible_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "make_anyone_default"
        }
      },
      "source_word": [
        9067,
        9072
      ],
      "status": "open",
      "unit": "u099b",
      "version": 1
    },
    {
      "id": "rs_u100a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "a8c23af4bc17c889f20bcc15bc7bfaf80dba47dbfd7fbb3fb66e04f89906f2a5",
              "direct_anyone_strict": "8b7462af674fb9f276db52cc5eabf6bd72ae79ee20a8e882e3eb600e97c08ffd",
              "direct_state_default": "a70db964c43881d7cfbfffc93756c785a00e55e80f0147f08fed1e4f75564b67"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state must direct education to the full development of the human personality. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "education-to-personality-direct-state",
              "over": [],
              "predicate": "direct_education_to_personality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "27e6ce2a4d79221ef0be70d8ee32927a3566c758a26d2a54d57bf01bbeb2fe89"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "f87ab178216f1640131c52445fd73101a82bf91cd1603ab7a72b12293a92a5bb",
              "direct_anyone_strict": "a70db964c43881d7cfbfffc93756c785a00e55e80f0147f08fed1e4f75564b67",
              "direct_state_strict": "a70db964c43881d7cfbfffc93756c785a00e55e80f0147f08fed1e4f75564b67"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state must direct education to the full development of the human personality unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "education-to-personality-direct-state",
              "over": [],
              "predicate": "direct_education_to_personality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "622c44323389086617ad63ea18096dd37fd2c32a029eaf42dfe2a4c2b1d24e7b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "a8c23af4bc17c889f20bcc15bc7bfaf80dba47dbfd7fbb3fb66e04f89906f2a5",
              "direct_state_default": "a70db964c43881d7cfbfffc93756c785a00e55e80f0147f08fed1e4f75564b67",
              "direct_state_strict": "8b7462af674fb9f276db52cc5eabf6bd72ae79ee20a8e882e3eb600e97c08ffd"
            },
            "who": "translator",
            "why": "Strict reading ('shall' read as 'must'): every state, group and person must direct education to the full development of the human personality. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "education-to-personality-direct-anyone",
              "over": [],
              "predicate": "direct_education_to_personality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "355e1661309a57e67fa92c27c5ad5603465a194662ebd3a370967cefb7bba6ac"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_strict": "a8c23af4bc17c889f20bcc15bc7bfaf80dba47dbfd7fbb3fb66e04f89906f2a5",
              "direct_state_default": "f87ab178216f1640131c52445fd73101a82bf91cd1603ab7a72b12293a92a5bb",
              "direct_state_strict": "a8c23af4bc17c889f20bcc15bc7bfaf80dba47dbfd7fbb3fb66e04f89906f2a5"
            },
            "who": "translator",
            "why": "Defeasible reading ('shall' read as 'should'): every state, group and person must direct education to the full development of the human personality unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "education-to-personality-direct-anyone",
              "over": [],
              "predicate": "direct_education_to_personality_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "77b4f78b375c5593588cd152422ebb95b679f37b72e3edb3cf54f2aa0c33390b"
        }
      ],
      "situations": {
        "8b7462af674fb9f276db52cc5eabf6bd72ae79ee20a8e882e3eb600e97c08ffd": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_personality_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_state_strict"
        },
        "a70db964c43881d7cfbfffc93756c785a00e55e80f0147f08fed1e4f75564b67": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "education-to-personality-direct-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_personality_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_state_default"
        },
        "a8c23af4bc17c889f20bcc15bc7bfaf80dba47dbfd7fbb3fb66e04f89906f2a5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "education-to-personality-direct-anyone"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_personality_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_anyone_default"
        },
        "f87ab178216f1640131c52445fd73101a82bf91cd1603ab7a72b12293a92a5bb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_personality_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "direct_anyone_default"
        }
      },
      "source_word": [
        9139,
        9144
      ],
      "status": "open",
      "unit": "u100a",
      "version": 1
    },
    {
      "id": "rs_u100b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "b01467a2d1162174d7c8ef8792409f69f0e6f5d81b124498cd228cc97b96f6dd",
              "direct_anyone_strict": "8f84c0f01546ae2523606a06b24f0401bbea49600f83ba49288d76a734f068d4",
              "direct_state_default": "84eae2ab2064aa2c5dd6e793b72ed1bbc4455334b1e70ffb3f9c6552cda72349"
            },
            "who": "translator",
            "why": "Strict reading (the source carries or opens its force): every state must direct education to strengthen respect of human rights as well as freedoms. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "name": "education-to-respect-for-rights-direct-state",
              "over": [],
              "predicate": "direct_education_to_respect_for_rights_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_state_strict",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "strict"
          },
          "meaning_id": "1236f00c582b152273400c40427290e328a45dd43780de2486e1fe1838d138f6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "bf379af022a2616a93560ec496956c008a2d14e06308b36e4c4806a50707ce1a",
              "direct_anyone_strict": "84eae2ab2064aa2c5dd6e793b72ed1bbc4455334b1e70ffb3f9c6552cda72349",
              "direct_state_strict": "84eae2ab2064aa2c5dd6e793b72ed1bbc4455334b1e70ffb3f9c6552cda72349"
            },
            "who": "translator",
            "why": "Defeasible reading (the source carries or opens its force): every state must direct education to strengthen respect of human rights as well as freedoms unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "unary",
                "is_state",
                [
                  "var",
                  0
                ]
              ],
              "mode": "default",
              "name": "education-to-respect-for-rights-direct-state",
              "over": [],
              "predicate": "direct_education_to_respect_for_rights_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_state_default",
          "kind": "norm",
          "labels": {
            "bearer": "state",
            "force": "default"
          },
          "meaning_id": "b642d5b88fe7be4c25977e2e01e8bb80649fe2d5c67defffcd67001c60c69450"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_default": "b01467a2d1162174d7c8ef8792409f69f0e6f5d81b124498cd228cc97b96f6dd",
              "direct_state_default": "84eae2ab2064aa2c5dd6e793b72ed1bbc4455334b1e70ffb3f9c6552cda72349",
              "direct_state_strict": "8f84c0f01546ae2523606a06b24f0401bbea49600f83ba49288d76a734f068d4"
            },
            "who": "translator",
            "why": "Strict reading (the source carries or opens its force): every state, group and person must direct education to strengthen respect of human rights as well as freedoms. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source."
          },
          "content": {
            "norm": {
              "guard": [
                "top"
              ],
              "name": "education-to-respect-for-rights-direct-anyone",
              "over": [],
              "predicate": "direct_education_to_respect_for_rights_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_anyone_strict",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "strict"
          },
          "meaning_id": "af7613b23eea55fa4c312b52f66ece34a04f34a935e7f6dcc205b7a6e3c2a48b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "direct_anyone_strict": "b01467a2d1162174d7c8ef8792409f69f0e6f5d81b124498cd228cc97b96f6dd",
              "direct_state_default": "bf379af022a2616a93560ec496956c008a2d14e06308b36e4c4806a50707ce1a",
              "direct_state_strict": "b01467a2d1162174d7c8ef8792409f69f0e6f5d81b124498cd228cc97b96f6dd"
            },
            "who": "translator",
            "why": "Defeasible reading (the source carries or opens its force): every state, group and person must direct education to strengthen respect of human rights as well as freedoms unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone."
          },
          "content": {
            "norm": {
              "exception": {
                "decided_by": "unstated",
                "factors": [],
                "necessary": [],
                "sufficient": []
              },
              "guard": [
                "top"
              ],
              "mode": "default",
              "name": "education-to-respect-for-rights-direct-anyone",
              "over": [],
              "predicate": "direct_education_to_respect_for_rights_required",
              "sign": true,
              "unless": []
            }
          },
          "id": "direct_anyone_default",
          "kind": "norm",
          "labels": {
            "bearer": "anyone",
            "force": "default"
          },
          "meaning_id": "2cddd96fe12deeaafcd0ba888e63ce919fb957161ead56a53f7f54f167dd02b2"
        }
      ],
      "situations": {
        "84eae2ab2064aa2c5dd6e793b72ed1bbc4455334b1e70ffb3f9c6552cda72349": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "education-to-respect-for-rights-direct-state"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_respect_for_rights_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_state_default"
        },
        "8f84c0f01546ae2523606a06b24f0401bbea49600f83ba49288d76a734f068d4": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_respect_for_rights_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_state_strict"
        },
        "b01467a2d1162174d7c8ef8792409f69f0e6f5d81b124498cd228cc97b96f6dd": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "education-to-respect-for-rights-direct-anyone"
              },
              "tuples": [
                [
                  "b"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_respect_for_rights_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": false,
          "witness": "direct_anyone_default"
        },
        "bf379af022a2616a93560ec496956c008a2d14e06308b36e4c4806a50707ce1a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "direct_education_to_respect_for_rights_required",
              "tuple": [
                "b"
              ]
            }
          },
          "value": true,
          "witness": "direct_anyone_default"
        }
      },
      "status": "open",
      "unit": "u100b",
      "version": 1
    },
    {
      "id": "rs_u081",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "b31aaa21f84c2a522be5a9c3556e1a7dfcb4861015d93a42b42bec6b9fb4b95f",
              "anyone_claim_strict": "097e68d4a606351deb6366f139f63d28badd87e17080d9872f0f278e24b03779",
              "state_claim_default": "e6a04f85ecbca254496689b604929bf2eaff2f8c923774c67fe25cc7ee6751e7"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder social security. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-social-security-by-state",
                    "over": [],
                    "predicate": "secure_social_security_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "social-security"
            }
          },
          "id": "state_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "fc833a04ad269bc9e6ffb0079c419108e143fcc469f9cfb6635696de24bb1b14"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "0b362d8ac9cbe7da65b1eb957fc1b1dc3d4e002df346299ad270d460e021b647",
              "anyone_claim_strict": "e6a04f85ecbca254496689b604929bf2eaff2f8c923774c67fe25cc7ee6751e7",
              "state_claim_strict": "e6a04f85ecbca254496689b604929bf2eaff2f8c923774c67fe25cc7ee6751e7"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder social security unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-social-security-by-state",
                    "over": [],
                    "predicate": "secure_social_security_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "social-security"
            }
          },
          "id": "state_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "217155317e2169464c97d6a2ccc82d85e3c14195d4c8d566762c62e2ed6d91e8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "b31aaa21f84c2a522be5a9c3556e1a7dfcb4861015d93a42b42bec6b9fb4b95f",
              "state_claim_default": "e6a04f85ecbca254496689b604929bf2eaff2f8c923774c67fe25cc7ee6751e7",
              "state_claim_strict": "097e68d4a606351deb6366f139f63d28badd87e17080d9872f0f278e24b03779"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder social security. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-social-security-by-anyone",
                    "over": [],
                    "predicate": "secure_social_security_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "social-security"
            }
          },
          "id": "anyone_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "4e8c98c6d9405ffd3bebd1a275540c2d315f92555ba0fbaafeacee4dc0f96a9d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_strict": "b31aaa21f84c2a522be5a9c3556e1a7dfcb4861015d93a42b42bec6b9fb4b95f",
              "state_claim_default": "0b362d8ac9cbe7da65b1eb957fc1b1dc3d4e002df346299ad270d460e021b647",
              "state_claim_strict": "b31aaa21f84c2a522be5a9c3556e1a7dfcb4861015d93a42b42bec6b9fb4b95f"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder social security unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-social-security-by-anyone",
                    "over": [],
                    "predicate": "secure_social_security_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "social-security"
            }
          },
          "id": "anyone_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "1f43fd35a7208986a7f0067904b44caab64dc632e0032ad4a3f1041e573f8958"
        }
      ],
      "situations": {
        "097e68d4a606351deb6366f139f63d28badd87e17080d9872f0f278e24b03779": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_social_security_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_strict"
        },
        "0b362d8ac9cbe7da65b1eb957fc1b1dc3d4e002df346299ad270d460e021b647": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_social_security_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_claim_default"
        },
        "b31aaa21f84c2a522be5a9c3556e1a7dfcb4861015d93a42b42bec6b9fb4b95f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-social-security-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_social_security_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_claim_default"
        },
        "e6a04f85ecbca254496689b604929bf2eaff2f8c923774c67fe25cc7ee6751e7": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-social-security-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_social_security_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_default"
        }
      },
      "status": "open",
      "unit": "u081",
      "version": 1
    },
    {
      "id": "rs_u084a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b4528034c145ab9b371cb8d44e41b1d0e9915012bd124e856e2ea072203f8713",
              "anyone_negative_strict": "b899422a7e25f3d82df1ac759c63bcf6608a935e2d5cfa9d2ef1d6a0b8297049",
              "anyone_positive_default": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "anyone_positive_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_negative_default": "2410c2772a3587fc07d30c908047db68fbda9d98925f4fbd269403c196d4a62b",
              "state_positive_default": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_positive_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid barring each holder from work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-work-by-state",
                    "over": [],
                    "predicate": "avoid_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "e4a80cc2ef019cdce81ebed5deee004c6d9f5c150b97ec209308911e2f2e8c33"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "0688a7bafbbd32c81c047f17e88487bcf645bf3de320e63393459a641db8a43c",
              "anyone_negative_strict": "2410c2772a3587fc07d30c908047db68fbda9d98925f4fbd269403c196d4a62b",
              "anyone_positive_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "anyone_positive_strict": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_negative_strict": "2410c2772a3587fc07d30c908047db68fbda9d98925f4fbd269403c196d4a62b",
              "state_positive_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_positive_strict": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid barring each holder from work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-work-by-state",
                    "over": [],
                    "predicate": "avoid_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "48c88e0519b91d48f6396918b0e0989559c4028abbdee4a86a03d033113b4dea"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b85ab74fa10b5100777338d865f1924a82392086ac9ccff2e652572defe32998",
              "anyone_negative_strict": "5812df1215e45bb21a13bf015362cb6c102951d1eddfe8ccb705a9b08e7c5cb2",
              "anyone_positive_default": "d32b5e145db691147f6d357eb1502253901cae0f5b76253b11b009490119860e",
              "anyone_positive_strict": "aad8279673fc4bfe16509eac206c42a90f1c9c2ec8d6981ed1ed5d7556c87ddb",
              "state_negative_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_negative_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_positive_default": "5af82110730e8fe63665378814cff932f4774bb7af6ff551b99a3648749f35d8"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must provide each holder with work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-work-by-state",
                    "over": [],
                    "predicate": "secure_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "f1388f96cdb55a1dfb61f9c96953b834bea2a7e69b826019529a7cd10b3982d6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "78fb909951fe5ed3a8a3bf4b0aa792a03c3ad2c1c3abfb1308ad244f172c01d1",
              "anyone_negative_strict": "9feda78369b1e92041dc371dbfdced1cec88cd9ee960eb49cf3685da801f50e1",
              "anyone_positive_default": "42ce4c8e18707e535ea27ac9d4dc4f333d75a55da5959cb39402d0e6c2040089",
              "anyone_positive_strict": "5af82110730e8fe63665378814cff932f4774bb7af6ff551b99a3648749f35d8",
              "state_negative_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_negative_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_positive_strict": "5af82110730e8fe63665378814cff932f4774bb7af6ff551b99a3648749f35d8"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must provide each holder with work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-work-by-state",
                    "over": [],
                    "predicate": "secure_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "2e8b0ccfceea28022c807f0657d36736b45467d3f530d2e3bb32fa57732e6db4"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b4528034c145ab9b371cb8d44e41b1d0e9915012bd124e856e2ea072203f8713",
              "anyone_positive_default": "67af25f081dd256006948a6bc76562f9028bfee435ae3590a7b41455cda40921",
              "anyone_positive_strict": "67af25f081dd256006948a6bc76562f9028bfee435ae3590a7b41455cda40921",
              "state_negative_default": "2410c2772a3587fc07d30c908047db68fbda9d98925f4fbd269403c196d4a62b",
              "state_negative_strict": "b899422a7e25f3d82df1ac759c63bcf6608a935e2d5cfa9d2ef1d6a0b8297049",
              "state_positive_default": "9feda78369b1e92041dc371dbfdced1cec88cd9ee960eb49cf3685da801f50e1",
              "state_positive_strict": "5812df1215e45bb21a13bf015362cb6c102951d1eddfe8ccb705a9b08e7c5cb2"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid barring each holder from work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-work-by-anyone",
                    "over": [],
                    "predicate": "avoid_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "0a96d6c7004c690a650117754f12c2a86a66408d74c943babbd953d603c9c8e0"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "b4528034c145ab9b371cb8d44e41b1d0e9915012bd124e856e2ea072203f8713",
              "anyone_positive_default": "62929fe0275ffd7dea86204c8b7072364f5c76fabb0f6cac972cfe7ae79f6ea6",
              "anyone_positive_strict": "62929fe0275ffd7dea86204c8b7072364f5c76fabb0f6cac972cfe7ae79f6ea6",
              "state_negative_default": "0688a7bafbbd32c81c047f17e88487bcf645bf3de320e63393459a641db8a43c",
              "state_negative_strict": "b4528034c145ab9b371cb8d44e41b1d0e9915012bd124e856e2ea072203f8713",
              "state_positive_default": "78fb909951fe5ed3a8a3bf4b0aa792a03c3ad2c1c3abfb1308ad244f172c01d1",
              "state_positive_strict": "b85ab74fa10b5100777338d865f1924a82392086ac9ccff2e652572defe32998"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid barring each holder from work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-work-by-anyone",
                    "over": [],
                    "predicate": "avoid_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "46825159078d74b0aea916c2eb081e16976fe9b2d46a9f72885a2efc0e76870b"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "62929fe0275ffd7dea86204c8b7072364f5c76fabb0f6cac972cfe7ae79f6ea6",
              "anyone_negative_strict": "67af25f081dd256006948a6bc76562f9028bfee435ae3590a7b41455cda40921",
              "anyone_positive_default": "d32b5e145db691147f6d357eb1502253901cae0f5b76253b11b009490119860e",
              "state_negative_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_negative_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_positive_default": "5af82110730e8fe63665378814cff932f4774bb7af6ff551b99a3648749f35d8",
              "state_positive_strict": "aad8279673fc4bfe16509eac206c42a90f1c9c2ec8d6981ed1ed5d7556c87ddb"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must provide each holder with work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-work-by-anyone",
                    "over": [],
                    "predicate": "secure_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "546bf77ae80971e92a34f80b9c8f526932b15de2af3e8899e7dd782dcef0b1c5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "62929fe0275ffd7dea86204c8b7072364f5c76fabb0f6cac972cfe7ae79f6ea6",
              "anyone_negative_strict": "67af25f081dd256006948a6bc76562f9028bfee435ae3590a7b41455cda40921",
              "anyone_positive_strict": "d32b5e145db691147f6d357eb1502253901cae0f5b76253b11b009490119860e",
              "state_negative_default": "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418",
              "state_negative_strict": "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9",
              "state_positive_default": "42ce4c8e18707e535ea27ac9d4dc4f333d75a55da5959cb39402d0e6c2040089",
              "state_positive_strict": "d32b5e145db691147f6d357eb1502253901cae0f5b76253b11b009490119860e"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must provide each holder with work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-work-by-anyone",
                    "over": [],
                    "predicate": "secure_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "work"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "1ea684a331cf94c275c47a69765726069fe06631a5908a1f37470667cd6cd998"
        }
      ],
      "situations": {
        "0688a7bafbbd32c81c047f17e88487bcf645bf3de320e63393459a641db8a43c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "2410c2772a3587fc07d30c908047db68fbda9d98925f4fbd269403c196d4a62b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-work-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "42ce4c8e18707e535ea27ac9d4dc4f333d75a55da5959cb39402d0e6c2040089": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "5812df1215e45bb21a13bf015362cb6c102951d1eddfe8ccb705a9b08e7c5cb2": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "5af82110730e8fe63665378814cff932f4774bb7af6ff551b99a3648749f35d8": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-work-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "62929fe0275ffd7dea86204c8b7072364f5c76fabb0f6cac972cfe7ae79f6ea6": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "67af25f081dd256006948a6bc76562f9028bfee435ae3590a7b41455cda40921": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "78fb909951fe5ed3a8a3bf4b0aa792a03c3ad2c1c3abfb1308ad244f172c01d1": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "9feda78369b1e92041dc371dbfdced1cec88cd9ee960eb49cf3685da801f50e1": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "aad8279673fc4bfe16509eac206c42a90f1c9c2ec8d6981ed1ed5d7556c87ddb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "b4528034c145ab9b371cb8d44e41b1d0e9915012bd124e856e2ea072203f8713": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-work-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "b85ab74fa10b5100777338d865f1924a82392086ac9ccff2e652572defe32998": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "b899422a7e25f3d82df1ac759c63bcf6608a935e2d5cfa9d2ef1d6a0b8297049": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "cd54d670dcec019ee7b70b5cc34b9be535b8cf0bc3b82014a31638366df63418": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        },
        "d32b5e145db691147f6d357eb1502253901cae0f5b76253b11b009490119860e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-work-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        },
        "eaa62610ee92a79ae5573448aaee7f6156d0cee98dca828420e9e3fbcbf16bc9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        }
      },
      "status": "open",
      "unit": "u084a",
      "version": 1
    },
    {
      "id": "rs_u084b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "185a2b6104a106204c21bc0a5c3dfc72f44203666994d2521c5b287dcaedf0e1",
              "anyone_negative_strict": "379c3096c694f1c41151c79ca397c3d2689ba542561ffd07c539aada0ad31484",
              "anyone_positive_default": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "anyone_positive_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_negative_default": "c3cacd0722d907db344e283a972f64e79a1dfeb202e630c22862c2d1077fec2b",
              "state_positive_default": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_positive_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid restricting the free choice of employment of each holder. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-free-choice-of-employment-by-state",
                    "over": [],
                    "predicate": "avoid_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "b45493f64bec442419d1329fd600c400b3e596cd3d1308f40571fb8333b8a095"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "d315034a715fb13195b82a18ab6d6c72768d3cbfd025c80cf2e25d7a94c9baed",
              "anyone_negative_strict": "c3cacd0722d907db344e283a972f64e79a1dfeb202e630c22862c2d1077fec2b",
              "anyone_positive_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "anyone_positive_strict": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_negative_strict": "c3cacd0722d907db344e283a972f64e79a1dfeb202e630c22862c2d1077fec2b",
              "state_positive_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_positive_strict": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid restricting the free choice of employment of each holder unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-free-choice-of-employment-by-state",
                    "over": [],
                    "predicate": "avoid_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "cb769af5086d67640578321d3512a7bea375dc83a07e91f21ce901ca0c7d421a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "7a2a5b9a9c6236275e7d7a683c1ec4156a89ad9b44ffaa9ad0841ac59f2aa57b",
              "anyone_negative_strict": "1e8601cf5f9e8029701d7f0ecfd23be708f8efaadd5e7ba6450c8273d99678c2",
              "anyone_positive_default": "a8e3c08157368acdc4c218c1a379650592c97c69a1662b1d52d1f5f6fd7952b0",
              "anyone_positive_strict": "2746797323411d1d6ff90a58115b07356755e39b7454f3cdb3432edc250fecc9",
              "state_negative_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_negative_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_positive_default": "e172056d51ceaa812988116d85a526a20cb7e624e4d4b2f80296f6a76f6dd0e5"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder free choice of employment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-free-choice-of-employment-by-state",
                    "over": [],
                    "predicate": "secure_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "872860cd6e2c9d309907dc8111c6ad6ebdfedffddb9f5dbf218f39e5bcccb865"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "3d917766612cb0e6d62716a425c5bd0a844640d0de303041a191a06c7e04c1bd",
              "anyone_negative_strict": "456063833f949d1516e366d65a091c0f4b54ddab296e095f4385ecac755a9941",
              "anyone_positive_default": "b4d2d76291771beb624445bfb9c4d67b3fa6b02bb90b65466bac6aa041e3ef3a",
              "anyone_positive_strict": "e172056d51ceaa812988116d85a526a20cb7e624e4d4b2f80296f6a76f6dd0e5",
              "state_negative_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_negative_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_positive_strict": "e172056d51ceaa812988116d85a526a20cb7e624e4d4b2f80296f6a76f6dd0e5"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder free choice of employment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-free-choice-of-employment-by-state",
                    "over": [],
                    "predicate": "secure_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "3b2085c823d515bf360c05388fa129251b89e7306d10ba1b9842c69fb0b050f1"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "185a2b6104a106204c21bc0a5c3dfc72f44203666994d2521c5b287dcaedf0e1",
              "anyone_positive_default": "8f7d82182d49c6af658554da8012c23b0f21140ed1c18bc7ed2fd42f9102f992",
              "anyone_positive_strict": "8f7d82182d49c6af658554da8012c23b0f21140ed1c18bc7ed2fd42f9102f992",
              "state_negative_default": "c3cacd0722d907db344e283a972f64e79a1dfeb202e630c22862c2d1077fec2b",
              "state_negative_strict": "379c3096c694f1c41151c79ca397c3d2689ba542561ffd07c539aada0ad31484",
              "state_positive_default": "456063833f949d1516e366d65a091c0f4b54ddab296e095f4385ecac755a9941",
              "state_positive_strict": "1e8601cf5f9e8029701d7f0ecfd23be708f8efaadd5e7ba6450c8273d99678c2"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid restricting the free choice of employment of each holder. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-free-choice-of-employment-by-anyone",
                    "over": [],
                    "predicate": "avoid_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "40c4c56400eac1cda4cd148fa45415b845d453d9602b611196fdc0e75cf8a1d7"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "185a2b6104a106204c21bc0a5c3dfc72f44203666994d2521c5b287dcaedf0e1",
              "anyone_positive_default": "14db87b15360446264877a3c5614a023ae55e9dac14920f25bc428057ad0e97a",
              "anyone_positive_strict": "14db87b15360446264877a3c5614a023ae55e9dac14920f25bc428057ad0e97a",
              "state_negative_default": "d315034a715fb13195b82a18ab6d6c72768d3cbfd025c80cf2e25d7a94c9baed",
              "state_negative_strict": "185a2b6104a106204c21bc0a5c3dfc72f44203666994d2521c5b287dcaedf0e1",
              "state_positive_default": "3d917766612cb0e6d62716a425c5bd0a844640d0de303041a191a06c7e04c1bd",
              "state_positive_strict": "7a2a5b9a9c6236275e7d7a683c1ec4156a89ad9b44ffaa9ad0841ac59f2aa57b"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid restricting the free choice of employment of each holder unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-free-choice-of-employment-by-anyone",
                    "over": [],
                    "predicate": "avoid_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "c90264d4ea80ea23da82109081f666c7b149abfae39f57f627a66d48579ee876"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "14db87b15360446264877a3c5614a023ae55e9dac14920f25bc428057ad0e97a",
              "anyone_negative_strict": "8f7d82182d49c6af658554da8012c23b0f21140ed1c18bc7ed2fd42f9102f992",
              "anyone_positive_default": "a8e3c08157368acdc4c218c1a379650592c97c69a1662b1d52d1f5f6fd7952b0",
              "state_negative_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_negative_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_positive_default": "e172056d51ceaa812988116d85a526a20cb7e624e4d4b2f80296f6a76f6dd0e5",
              "state_positive_strict": "2746797323411d1d6ff90a58115b07356755e39b7454f3cdb3432edc250fecc9"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder free choice of employment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-free-choice-of-employment-by-anyone",
                    "over": [],
                    "predicate": "secure_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "ab34dc4ecfa946859b621e257dde3cb2b68c868abf7deffbbc14da1bb8f69755"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "14db87b15360446264877a3c5614a023ae55e9dac14920f25bc428057ad0e97a",
              "anyone_negative_strict": "8f7d82182d49c6af658554da8012c23b0f21140ed1c18bc7ed2fd42f9102f992",
              "anyone_positive_strict": "a8e3c08157368acdc4c218c1a379650592c97c69a1662b1d52d1f5f6fd7952b0",
              "state_negative_default": "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f",
              "state_negative_strict": "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716",
              "state_positive_default": "b4d2d76291771beb624445bfb9c4d67b3fa6b02bb90b65466bac6aa041e3ef3a",
              "state_positive_strict": "a8e3c08157368acdc4c218c1a379650592c97c69a1662b1d52d1f5f6fd7952b0"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder free choice of employment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-free-choice-of-employment-by-anyone",
                    "over": [],
                    "predicate": "secure_free_choice_of_employment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "free-choice-of-employment"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "13ffd21813354bd646a0c32efe14b71cc320bbf867283f0f63bb02c063907566"
        }
      ],
      "situations": {
        "14db87b15360446264877a3c5614a023ae55e9dac14920f25bc428057ad0e97a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "185a2b6104a106204c21bc0a5c3dfc72f44203666994d2521c5b287dcaedf0e1": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-free-choice-of-employment-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "1e8601cf5f9e8029701d7f0ecfd23be708f8efaadd5e7ba6450c8273d99678c2": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "2746797323411d1d6ff90a58115b07356755e39b7454f3cdb3432edc250fecc9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "379c3096c694f1c41151c79ca397c3d2689ba542561ffd07c539aada0ad31484": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "3d917766612cb0e6d62716a425c5bd0a844640d0de303041a191a06c7e04c1bd": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "456063833f949d1516e366d65a091c0f4b54ddab296e095f4385ecac755a9941": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "7a2a5b9a9c6236275e7d7a683c1ec4156a89ad9b44ffaa9ad0841ac59f2aa57b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "8f7d82182d49c6af658554da8012c23b0f21140ed1c18bc7ed2fd42f9102f992": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "a8e3c08157368acdc4c218c1a379650592c97c69a1662b1d52d1f5f6fd7952b0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-free-choice-of-employment-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        },
        "ae270804f7f28de34046b7c0163fb670f0b60a7c8ae711a2a6ab5ef52adad716": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        },
        "b4d2d76291771beb624445bfb9c4d67b3fa6b02bb90b65466bac6aa041e3ef3a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "c3cacd0722d907db344e283a972f64e79a1dfeb202e630c22862c2d1077fec2b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-free-choice-of-employment-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "cd37e08c2349a9ff70168893b145019469ac9646d19758d7cec5a444a3e6859f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        },
        "d315034a715fb13195b82a18ab6d6c72768d3cbfd025c80cf2e25d7a94c9baed": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "e172056d51ceaa812988116d85a526a20cb7e624e4d4b2f80296f6a76f6dd0e5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-free-choice-of-employment-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_free_choice_of_employment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        }
      },
      "status": "open",
      "unit": "u084b",
      "version": 1
    },
    {
      "id": "rs_u084c",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "10dfdb2acf5c53fd169e6f4d9c8b96fb187b17ea53afb8c7a1a069be0338dd94",
              "anyone_claim_strict": "cc9124a29a544e5c0f44ae6c893d64e6cd0bee893792f5e831b9a63ed83cb42d",
              "state_claim_default": "3969ede7581440a73b6c99f893127074148bd82f8df7e89b51c016c82f82e698"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder just as well as favourable conditions of work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-favourable-work-conditions-by-state",
                    "over": [],
                    "predicate": "secure_just_and_favourable_conditions_of_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "favourable-work-conditions"
            }
          },
          "id": "state_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "9fbfe6123ddccd8a27b619ddfc4caede0cf7d876996abbf6d842f539639aab8e"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "1d6a3b6192c8f536dc2ad72cccee8c2d33647447dc86ff9760423b14a132da5c",
              "anyone_claim_strict": "3969ede7581440a73b6c99f893127074148bd82f8df7e89b51c016c82f82e698",
              "state_claim_strict": "3969ede7581440a73b6c99f893127074148bd82f8df7e89b51c016c82f82e698"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder just as well as favourable conditions of work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-favourable-work-conditions-by-state",
                    "over": [],
                    "predicate": "secure_just_and_favourable_conditions_of_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "favourable-work-conditions"
            }
          },
          "id": "state_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "8fd35667d199df2d67e4723a48737df4affc92ee0aa2b57d5dd85ae1818c48ad"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "10dfdb2acf5c53fd169e6f4d9c8b96fb187b17ea53afb8c7a1a069be0338dd94",
              "state_claim_default": "3969ede7581440a73b6c99f893127074148bd82f8df7e89b51c016c82f82e698",
              "state_claim_strict": "cc9124a29a544e5c0f44ae6c893d64e6cd0bee893792f5e831b9a63ed83cb42d"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder just as well as favourable conditions of work. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-favourable-work-conditions-by-anyone",
                    "over": [],
                    "predicate": "secure_just_and_favourable_conditions_of_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "favourable-work-conditions"
            }
          },
          "id": "anyone_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "79c1c437938ea28e23e0ea10ffc094840626b531da2f5e3e7131f75462e24880"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_strict": "10dfdb2acf5c53fd169e6f4d9c8b96fb187b17ea53afb8c7a1a069be0338dd94",
              "state_claim_default": "1d6a3b6192c8f536dc2ad72cccee8c2d33647447dc86ff9760423b14a132da5c",
              "state_claim_strict": "10dfdb2acf5c53fd169e6f4d9c8b96fb187b17ea53afb8c7a1a069be0338dd94"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder just as well as favourable conditions of work unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-favourable-work-conditions-by-anyone",
                    "over": [],
                    "predicate": "secure_just_and_favourable_conditions_of_work_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "favourable-work-conditions"
            }
          },
          "id": "anyone_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "4bfe9032fff20b802004f4f2114b35921acaa926a9ff9a28beca8b89d1ce83ad"
        }
      ],
      "situations": {
        "10dfdb2acf5c53fd169e6f4d9c8b96fb187b17ea53afb8c7a1a069be0338dd94": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-favourable-work-conditions-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_just_and_favourable_conditions_of_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_claim_default"
        },
        "1d6a3b6192c8f536dc2ad72cccee8c2d33647447dc86ff9760423b14a132da5c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_just_and_favourable_conditions_of_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_claim_default"
        },
        "3969ede7581440a73b6c99f893127074148bd82f8df7e89b51c016c82f82e698": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-favourable-work-conditions-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_just_and_favourable_conditions_of_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_default"
        },
        "cc9124a29a544e5c0f44ae6c893d64e6cd0bee893792f5e831b9a63ed83cb42d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_just_and_favourable_conditions_of_work_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_strict"
        }
      },
      "status": "open",
      "unit": "u084c",
      "version": 1
    },
    {
      "id": "rs_u084d",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "b7cc25c611459978bf1fc29bbf8cc8201aee93f890ec2e9aaf8dfe6611c922bc",
              "anyone_claim_strict": "6f7d8b9ea2a4f63c0140cb87a69d679ac0fa983f7ca28308f0e7362d14385f61",
              "state_claim_default": "dfaddc4316fe7bddcad94be0a49f6aee2677d069ac59a3ad58a3c1ec41052cbc"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must protect each holder against unemployment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-unemployment-protection-by-state",
                    "over": [],
                    "predicate": "secure_protection_against_unemployment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "unemployment-protection"
            }
          },
          "id": "state_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "5088ba08ce4ac3b835ccd1782f12768ffce7bed9be5abdfcd661d65248de17bb"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "c00b165a7402d1a8f5aae8dc126b1f02d58edab3efc4f446850001a5f98bd2ac",
              "anyone_claim_strict": "dfaddc4316fe7bddcad94be0a49f6aee2677d069ac59a3ad58a3c1ec41052cbc",
              "state_claim_strict": "dfaddc4316fe7bddcad94be0a49f6aee2677d069ac59a3ad58a3c1ec41052cbc"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must protect each holder against unemployment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-unemployment-protection-by-state",
                    "over": [],
                    "predicate": "secure_protection_against_unemployment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "unemployment-protection"
            }
          },
          "id": "state_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "f315d0c8981622e38abd426f1dcf52d171efa4cef9301a41afe2606154521121"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "b7cc25c611459978bf1fc29bbf8cc8201aee93f890ec2e9aaf8dfe6611c922bc",
              "state_claim_default": "dfaddc4316fe7bddcad94be0a49f6aee2677d069ac59a3ad58a3c1ec41052cbc",
              "state_claim_strict": "6f7d8b9ea2a4f63c0140cb87a69d679ac0fa983f7ca28308f0e7362d14385f61"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must protect each holder against unemployment. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-unemployment-protection-by-anyone",
                    "over": [],
                    "predicate": "secure_protection_against_unemployment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "unemployment-protection"
            }
          },
          "id": "anyone_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "df7b63fc9d3c5c899d52a7b314ea58214b7a152b3b68080e5178489cb72593cd"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_strict": "b7cc25c611459978bf1fc29bbf8cc8201aee93f890ec2e9aaf8dfe6611c922bc",
              "state_claim_default": "c00b165a7402d1a8f5aae8dc126b1f02d58edab3efc4f446850001a5f98bd2ac",
              "state_claim_strict": "b7cc25c611459978bf1fc29bbf8cc8201aee93f890ec2e9aaf8dfe6611c922bc"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must protect each holder against unemployment unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-unemployment-protection-by-anyone",
                    "over": [],
                    "predicate": "secure_protection_against_unemployment_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "unemployment-protection"
            }
          },
          "id": "anyone_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "b90897e035af4b7033cb5d33befdeda27896305dd532f4823572f428909dfa0f"
        }
      ],
      "situations": {
        "6f7d8b9ea2a4f63c0140cb87a69d679ac0fa983f7ca28308f0e7362d14385f61": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_unemployment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_strict"
        },
        "b7cc25c611459978bf1fc29bbf8cc8201aee93f890ec2e9aaf8dfe6611c922bc": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-unemployment-protection-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_unemployment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_claim_default"
        },
        "c00b165a7402d1a8f5aae8dc126b1f02d58edab3efc4f446850001a5f98bd2ac": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_unemployment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_claim_default"
        },
        "dfaddc4316fe7bddcad94be0a49f6aee2677d069ac59a3ad58a3c1ec41052cbc": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-unemployment-protection-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_protection_against_unemployment_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_default"
        }
      },
      "status": "open",
      "unit": "u084d",
      "version": 1
    },
    {
      "id": "rs_u087",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "62822fbdd56588a029115acfa8e78b2ecca798b554de625cedb009f4f2e18777",
              "anyone_negative_strict": "46f10a4da446d4b7860cc13655c44d1e12eea528e2d86c944fb5544928f18bdb",
              "anyone_positive_default": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "anyone_positive_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_negative_default": "a219b20b990417c95955835f0e122c8d0a49ebcb187b4dadc2ec9f9e1aceceaf",
              "state_positive_default": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_positive_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid barring each holder from forming as well as joining trade unions. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-trade-unions-by-state",
                    "over": [],
                    "predicate": "avoid_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "eaf81c72c2e0be6fde6002318b1a0aff7652a64c7fc031a700bfd2196baa54d3"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "0902bf42786ed6cd2bd546a0adff0e84eca30937e9069809597c2ac737468a8a",
              "anyone_negative_strict": "a219b20b990417c95955835f0e122c8d0a49ebcb187b4dadc2ec9f9e1aceceaf",
              "anyone_positive_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "anyone_positive_strict": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_negative_strict": "a219b20b990417c95955835f0e122c8d0a49ebcb187b4dadc2ec9f9e1aceceaf",
              "state_positive_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_positive_strict": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid barring each holder from forming as well as joining trade unions unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-trade-unions-by-state",
                    "over": [],
                    "predicate": "avoid_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "3d94b1d86239a85d0af84b75940c206663325b92372f2e53a824b1ebde7d9219"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "917c28e32ebd4dbbacad714335addb2e7d04eb23ed8feb27adea81923b3e30b4",
              "anyone_negative_strict": "8fb81866e25c0909939da5721269c744411c53e6ea68c94199d58548e31f9bfe",
              "anyone_positive_default": "5fc5ce3b6b041fcdc2057943504913034bc97340dedafbe86b4f77426117a30e",
              "anyone_positive_strict": "012d82a636790fca45b77890b578809f2af182eeae5df41328d4f7f25a9b7c4a",
              "state_negative_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_negative_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_positive_default": "4eec84d7fc08c73703d9b41a3722b40961fcce2542588924a0629a9ff1bae1fe"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder forming as well as joining trade unions. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-trade-unions-by-state",
                    "over": [],
                    "predicate": "secure_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "2d3d109f9a9aed4e4027a3fd3ab8654183c77dc594140b0a790e4b9f2b18c47a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "179e82eb6f738238b7d800c9e70383f51e4becdeedba3a227b3b8064fb7769b7",
              "anyone_negative_strict": "f4c378c2e784eba537501f59b17b7a518e13b31351be14ce6cc9dd2bbe440119",
              "anyone_positive_default": "37062a6be5f6cf6eb3636870c931689956cb23a0db2b78d82c5e3f45863106d8",
              "anyone_positive_strict": "4eec84d7fc08c73703d9b41a3722b40961fcce2542588924a0629a9ff1bae1fe",
              "state_negative_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_negative_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_positive_strict": "4eec84d7fc08c73703d9b41a3722b40961fcce2542588924a0629a9ff1bae1fe"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder forming as well as joining trade unions unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-trade-unions-by-state",
                    "over": [],
                    "predicate": "secure_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "db5a0f26ea64bcdb4aace3baefd8f07bd3cc2c7da03209e3a9861b4aee79862d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "62822fbdd56588a029115acfa8e78b2ecca798b554de625cedb009f4f2e18777",
              "anyone_positive_default": "06b00adec732dc461cee257c54b4081a0174ef1389974fbe3e519a8aa67fec6b",
              "anyone_positive_strict": "06b00adec732dc461cee257c54b4081a0174ef1389974fbe3e519a8aa67fec6b",
              "state_negative_default": "a219b20b990417c95955835f0e122c8d0a49ebcb187b4dadc2ec9f9e1aceceaf",
              "state_negative_strict": "46f10a4da446d4b7860cc13655c44d1e12eea528e2d86c944fb5544928f18bdb",
              "state_positive_default": "f4c378c2e784eba537501f59b17b7a518e13b31351be14ce6cc9dd2bbe440119",
              "state_positive_strict": "8fb81866e25c0909939da5721269c744411c53e6ea68c94199d58548e31f9bfe"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid barring each holder from forming as well as joining trade unions. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-trade-unions-by-anyone",
                    "over": [],
                    "predicate": "avoid_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "b83c10fcb1ef969e4847e580e1e31797b25f6f4f2175e1c24dc3a84225e74e56"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "62822fbdd56588a029115acfa8e78b2ecca798b554de625cedb009f4f2e18777",
              "anyone_positive_default": "475e31f341ace0bf39b08abbbe0763586ad78cff0708ba7c08e21eebbb15b97c",
              "anyone_positive_strict": "475e31f341ace0bf39b08abbbe0763586ad78cff0708ba7c08e21eebbb15b97c",
              "state_negative_default": "0902bf42786ed6cd2bd546a0adff0e84eca30937e9069809597c2ac737468a8a",
              "state_negative_strict": "62822fbdd56588a029115acfa8e78b2ecca798b554de625cedb009f4f2e18777",
              "state_positive_default": "179e82eb6f738238b7d800c9e70383f51e4becdeedba3a227b3b8064fb7769b7",
              "state_positive_strict": "917c28e32ebd4dbbacad714335addb2e7d04eb23ed8feb27adea81923b3e30b4"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid barring each holder from forming as well as joining trade unions unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-trade-unions-by-anyone",
                    "over": [],
                    "predicate": "avoid_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "76dd9969ad63e9acb9af7d06a7eeccc163709fe8b3d776836920fdcf797ffda9"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "475e31f341ace0bf39b08abbbe0763586ad78cff0708ba7c08e21eebbb15b97c",
              "anyone_negative_strict": "06b00adec732dc461cee257c54b4081a0174ef1389974fbe3e519a8aa67fec6b",
              "anyone_positive_default": "5fc5ce3b6b041fcdc2057943504913034bc97340dedafbe86b4f77426117a30e",
              "state_negative_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_negative_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_positive_default": "4eec84d7fc08c73703d9b41a3722b40961fcce2542588924a0629a9ff1bae1fe",
              "state_positive_strict": "012d82a636790fca45b77890b578809f2af182eeae5df41328d4f7f25a9b7c4a"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder forming as well as joining trade unions. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-trade-unions-by-anyone",
                    "over": [],
                    "predicate": "secure_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "ea279cf14ada4ce31ef29f0ba219c3ef07faf94875e5389827f52eaa9b75d3c8"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "475e31f341ace0bf39b08abbbe0763586ad78cff0708ba7c08e21eebbb15b97c",
              "anyone_negative_strict": "06b00adec732dc461cee257c54b4081a0174ef1389974fbe3e519a8aa67fec6b",
              "anyone_positive_strict": "5fc5ce3b6b041fcdc2057943504913034bc97340dedafbe86b4f77426117a30e",
              "state_negative_default": "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24",
              "state_negative_strict": "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee",
              "state_positive_default": "37062a6be5f6cf6eb3636870c931689956cb23a0db2b78d82c5e3f45863106d8",
              "state_positive_strict": "5fc5ce3b6b041fcdc2057943504913034bc97340dedafbe86b4f77426117a30e"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder forming as well as joining trade unions unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-trade-unions-by-anyone",
                    "over": [],
                    "predicate": "secure_trade_unions_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "trade-unions"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "c984c4494520d5978c065d8f17fcc2545f85b418984c3d97a085502f9e5e6a55"
        }
      ],
      "situations": {
        "012d82a636790fca45b77890b578809f2af182eeae5df41328d4f7f25a9b7c4a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "06b00adec732dc461cee257c54b4081a0174ef1389974fbe3e519a8aa67fec6b": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "0902bf42786ed6cd2bd546a0adff0e84eca30937e9069809597c2ac737468a8a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "179e82eb6f738238b7d800c9e70383f51e4becdeedba3a227b3b8064fb7769b7": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "37062a6be5f6cf6eb3636870c931689956cb23a0db2b78d82c5e3f45863106d8": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "46f10a4da446d4b7860cc13655c44d1e12eea528e2d86c944fb5544928f18bdb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "475e31f341ace0bf39b08abbbe0763586ad78cff0708ba7c08e21eebbb15b97c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "4eec84d7fc08c73703d9b41a3722b40961fcce2542588924a0629a9ff1bae1fe": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-trade-unions-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "5fc5ce3b6b041fcdc2057943504913034bc97340dedafbe86b4f77426117a30e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-trade-unions-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        },
        "62822fbdd56588a029115acfa8e78b2ecca798b554de625cedb009f4f2e18777": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-trade-unions-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "877a0f7eaa2553ed679e69ba475dfed9327ffdfd2441b4a0b41fd1438bd47bee": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        },
        "8e9b3d003bcbfe37edae06ce21f3eb3bc1447a11b3a27b9bb4f8dd8dfaf83d24": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        },
        "8fb81866e25c0909939da5721269c744411c53e6ea68c94199d58548e31f9bfe": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "917c28e32ebd4dbbacad714335addb2e7d04eb23ed8feb27adea81923b3e30b4": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "a219b20b990417c95955835f0e122c8d0a49ebcb187b4dadc2ec9f9e1aceceaf": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-trade-unions-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "f4c378c2e784eba537501f59b17b7a518e13b31351be14ce6cc9dd2bbe440119": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_trade_unions_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        }
      },
      "status": "open",
      "unit": "u087",
      "version": 1
    },
    {
      "id": "rs_u096",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "5e0dc345e6de3204623267c669e445ae199e362d174d364b84fd350a909de5c9",
              "anyone_negative_strict": "a1ef5751a815cffe077af5b8081e36c537fadf4de5864e10eb7ced5fd0e03f19",
              "anyone_positive_default": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "anyone_positive_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_negative_default": "14ce5f62da9ab2f4668faf4688a12716c3f8a16e33df7ee835302967890accb5",
              "state_positive_default": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_positive_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid barring each holder from education. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-education-by-state",
                    "over": [],
                    "predicate": "avoid_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "f4ce7add41fe17e559a92476611d35d019bf1062f75d8458ad93165984ff5f74"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "247029efb2b1bf5ba180fbc8fef05a96a7acabfeca5e0e7a1a67d8e492fdc02d",
              "anyone_negative_strict": "14ce5f62da9ab2f4668faf4688a12716c3f8a16e33df7ee835302967890accb5",
              "anyone_positive_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "anyone_positive_strict": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_negative_strict": "14ce5f62da9ab2f4668faf4688a12716c3f8a16e33df7ee835302967890accb5",
              "state_positive_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_positive_strict": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid barring each holder from education unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-education-by-state",
                    "over": [],
                    "predicate": "avoid_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "780741ae0b4507304a11b2c2ef789b9a399d7f13d2d93c912fd516186d89a4c2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "94fb9e483dcaa90c01648c254e61bc93ed923045255c0e17f683071547d17164",
              "anyone_negative_strict": "2aeca563d23aee63a0a43b92ba6d58b6255dd34f784b55a360ed7fc78ec06959",
              "anyone_positive_default": "36b5509ca0581d9f3e9297a6250df882c2db60d95a2c1237c064012970cef54f",
              "anyone_positive_strict": "5bf164233a29b3ae7241d153be0e66f54999cfcb1c7010d43177372f667214d5",
              "state_negative_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_negative_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_positive_default": "d033697a3efe27a91cbfd37386d41d1abc7323aab084e743d5f30c20dc88bd31"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder education. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-education-by-state",
                    "over": [],
                    "predicate": "secure_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "5464e6b52e34a25249ac755a5c3dd7a7fad176763de64c596adf57b15a35612c"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "22fba6a2c347234e6cee6c71873cf6bf9f235d9238c82efa52e781ab540bca90",
              "anyone_negative_strict": "c2f9d32344f00af15d5a7a85596705cb3293ae9a89025b09923addbdb4edc044",
              "anyone_positive_default": "ad79f3fb9dbc83516f53b1726b952aaeb810587e394e3f8d5f1ee7893b20d675",
              "anyone_positive_strict": "d033697a3efe27a91cbfd37386d41d1abc7323aab084e743d5f30c20dc88bd31",
              "state_negative_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_negative_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_positive_strict": "d033697a3efe27a91cbfd37386d41d1abc7323aab084e743d5f30c20dc88bd31"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder education unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-education-by-state",
                    "over": [],
                    "predicate": "secure_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "fda729a6b08675eb5d28165df2fab2e7f46ee97cadea928b6ce6aec7d6be118a"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "5e0dc345e6de3204623267c669e445ae199e362d174d364b84fd350a909de5c9",
              "anyone_positive_default": "1fb67c81fb5ddd7dedd122e739c206f76050b10cc2f322fc11c22379c990b0f5",
              "anyone_positive_strict": "1fb67c81fb5ddd7dedd122e739c206f76050b10cc2f322fc11c22379c990b0f5",
              "state_negative_default": "14ce5f62da9ab2f4668faf4688a12716c3f8a16e33df7ee835302967890accb5",
              "state_negative_strict": "a1ef5751a815cffe077af5b8081e36c537fadf4de5864e10eb7ced5fd0e03f19",
              "state_positive_default": "c2f9d32344f00af15d5a7a85596705cb3293ae9a89025b09923addbdb4edc044",
              "state_positive_strict": "2aeca563d23aee63a0a43b92ba6d58b6255dd34f784b55a360ed7fc78ec06959"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid barring each holder from education. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-education-by-anyone",
                    "over": [],
                    "predicate": "avoid_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "611821f99caea6b85d42a9332fd2362200cb26d4a2b7d3faf9ae78403ce701d6"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "5e0dc345e6de3204623267c669e445ae199e362d174d364b84fd350a909de5c9",
              "anyone_positive_default": "9567540e46ed6e1097fd9e8eb82c9e8eb3af5ad70dc1012c88bdf77541849215",
              "anyone_positive_strict": "9567540e46ed6e1097fd9e8eb82c9e8eb3af5ad70dc1012c88bdf77541849215",
              "state_negative_default": "247029efb2b1bf5ba180fbc8fef05a96a7acabfeca5e0e7a1a67d8e492fdc02d",
              "state_negative_strict": "5e0dc345e6de3204623267c669e445ae199e362d174d364b84fd350a909de5c9",
              "state_positive_default": "22fba6a2c347234e6cee6c71873cf6bf9f235d9238c82efa52e781ab540bca90",
              "state_positive_strict": "94fb9e483dcaa90c01648c254e61bc93ed923045255c0e17f683071547d17164"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid barring each holder from education unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-education-by-anyone",
                    "over": [],
                    "predicate": "avoid_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "e31596e26cc10077682b312e083696dc6ddf456ff1c9f2f27f504696c4499d62"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "9567540e46ed6e1097fd9e8eb82c9e8eb3af5ad70dc1012c88bdf77541849215",
              "anyone_negative_strict": "1fb67c81fb5ddd7dedd122e739c206f76050b10cc2f322fc11c22379c990b0f5",
              "anyone_positive_default": "36b5509ca0581d9f3e9297a6250df882c2db60d95a2c1237c064012970cef54f",
              "state_negative_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_negative_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_positive_default": "d033697a3efe27a91cbfd37386d41d1abc7323aab084e743d5f30c20dc88bd31",
              "state_positive_strict": "5bf164233a29b3ae7241d153be0e66f54999cfcb1c7010d43177372f667214d5"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder education. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-education-by-anyone",
                    "over": [],
                    "predicate": "secure_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "6b5980f08510f0bd472a23b34f0eab450ca71c0d5741cbe2050cf13dffe7d0b5"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "9567540e46ed6e1097fd9e8eb82c9e8eb3af5ad70dc1012c88bdf77541849215",
              "anyone_negative_strict": "1fb67c81fb5ddd7dedd122e739c206f76050b10cc2f322fc11c22379c990b0f5",
              "anyone_positive_strict": "36b5509ca0581d9f3e9297a6250df882c2db60d95a2c1237c064012970cef54f",
              "state_negative_default": "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9",
              "state_negative_strict": "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63",
              "state_positive_default": "ad79f3fb9dbc83516f53b1726b952aaeb810587e394e3f8d5f1ee7893b20d675",
              "state_positive_strict": "36b5509ca0581d9f3e9297a6250df882c2db60d95a2c1237c064012970cef54f"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder education unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-education-by-anyone",
                    "over": [],
                    "predicate": "secure_education_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "education"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "7ec816aac107e26fabe225582b244b44eb94b5e024ac0ea88ef5ffa678f954a6"
        }
      ],
      "situations": {
        "14ce5f62da9ab2f4668faf4688a12716c3f8a16e33df7ee835302967890accb5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-education-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "1fb67c81fb5ddd7dedd122e739c206f76050b10cc2f322fc11c22379c990b0f5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "22fba6a2c347234e6cee6c71873cf6bf9f235d9238c82efa52e781ab540bca90": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "247029efb2b1bf5ba180fbc8fef05a96a7acabfeca5e0e7a1a67d8e492fdc02d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "2aeca563d23aee63a0a43b92ba6d58b6255dd34f784b55a360ed7fc78ec06959": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "36b5509ca0581d9f3e9297a6250df882c2db60d95a2c1237c064012970cef54f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-education-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        },
        "5bf164233a29b3ae7241d153be0e66f54999cfcb1c7010d43177372f667214d5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "5e0dc345e6de3204623267c669e445ae199e362d174d364b84fd350a909de5c9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-education-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "728f5ac644d7701e789e2bc2a6f72383a877ada3ad8d90233896ae439a395e63": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        },
        "94fb9e483dcaa90c01648c254e61bc93ed923045255c0e17f683071547d17164": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "9567540e46ed6e1097fd9e8eb82c9e8eb3af5ad70dc1012c88bdf77541849215": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "a1ef5751a815cffe077af5b8081e36c537fadf4de5864e10eb7ced5fd0e03f19": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "ad79f3fb9dbc83516f53b1726b952aaeb810587e394e3f8d5f1ee7893b20d675": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "c2f9d32344f00af15d5a7a85596705cb3293ae9a89025b09923addbdb4edc044": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "d033697a3efe27a91cbfd37386d41d1abc7323aab084e743d5f30c20dc88bd31": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-education-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "d2466d56eb32cf9c9d73eee2301dc8482af80d99d77d962c9181f722098a72e9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_education_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        }
      },
      "status": "open",
      "unit": "u096",
      "version": 1
    },
    {
      "id": "rs_u105a",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "c102aaafde350bd9f8f8271c4b6c0196049b82a5e38b06dff899730985f689ca",
              "anyone_negative_strict": "df716768412298e05b8fd540391fd86e1a0e89129103a377f8e17aa706974436",
              "anyone_positive_default": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "anyone_positive_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_negative_default": "c135aa4c76cd7af4bb4ce430aecaf4030d25fda921ad80107e360ea63039b635",
              "state_positive_default": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_positive_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid barring each holder from taking part in the cultural life of the community. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-cultural-life-by-state",
                    "over": [],
                    "predicate": "avoid_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "beb3c7f56a30c74ee0ce3de2f357ac3c638b0b256f9e3b0332b5966ccda79905"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "84b42f5164b553f87261562473870a0b26d1557f7fcc54eecd060cc3bcbb6f0e",
              "anyone_negative_strict": "c135aa4c76cd7af4bb4ce430aecaf4030d25fda921ad80107e360ea63039b635",
              "anyone_positive_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "anyone_positive_strict": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_negative_strict": "c135aa4c76cd7af4bb4ce430aecaf4030d25fda921ad80107e360ea63039b635",
              "state_positive_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_positive_strict": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid barring each holder from taking part in the cultural life of the community unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-cultural-life-by-state",
                    "over": [],
                    "predicate": "avoid_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "4bc130cb60242c12c00383e9b9f3244bf8de45c2726e384319b9bd1528fdae33"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "3a693053b49e9856ff10ec341a111c732e0057b1ec12bf408c75a3615aad808c",
              "anyone_negative_strict": "7beebbad66ceb0451e7dae8dc64ff74aaaa5e19929bbbdd4fc33268a4e91dce5",
              "anyone_positive_default": "e128c842d61166cda17b3bcf51e9aa7401eb2c2307c6b86654b67de166bb696c",
              "anyone_positive_strict": "7c8c0c02d54cc808448180d5af4ca58d7edf271e22361c69bb981b893cdeb80e",
              "state_negative_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_negative_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_positive_default": "a43360ae7d5fb13f6e9f34667eea9c08a75cad29a8eb62f435a2b44bfa4e60b6"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder free participation in the cultural life of the community. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-cultural-life-by-state",
                    "over": [],
                    "predicate": "secure_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "79724dc15122b140b86d30a5d7883ed913dc0a02572b5da0ffd5438f432bff50"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "83dc88dbe6401427fb5f9834742d4d7ca62c567f351d3550815e26eff795098c",
              "anyone_negative_strict": "b393d439325b5d399a310113b09af55f08bed437222f47a1344bd14e42146e3d",
              "anyone_positive_default": "df61a1dfbaf5d622b6d8f7fb542b8f406bbce40746a3afc3d47eb767c8eae625",
              "anyone_positive_strict": "a43360ae7d5fb13f6e9f34667eea9c08a75cad29a8eb62f435a2b44bfa4e60b6",
              "state_negative_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_negative_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_positive_strict": "a43360ae7d5fb13f6e9f34667eea9c08a75cad29a8eb62f435a2b44bfa4e60b6"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder free participation in the cultural life of the community unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-cultural-life-by-state",
                    "over": [],
                    "predicate": "secure_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "d3a1445664746e31bbb140ade6db5e1d68c25a1571c35b337abbe01d71d85879"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "c102aaafde350bd9f8f8271c4b6c0196049b82a5e38b06dff899730985f689ca",
              "anyone_positive_default": "d02b6c89b7e69d591fc651d14471b1ddebcfcf38fa082777245e63605fdd7b01",
              "anyone_positive_strict": "d02b6c89b7e69d591fc651d14471b1ddebcfcf38fa082777245e63605fdd7b01",
              "state_negative_default": "c135aa4c76cd7af4bb4ce430aecaf4030d25fda921ad80107e360ea63039b635",
              "state_negative_strict": "df716768412298e05b8fd540391fd86e1a0e89129103a377f8e17aa706974436",
              "state_positive_default": "b393d439325b5d399a310113b09af55f08bed437222f47a1344bd14e42146e3d",
              "state_positive_strict": "7beebbad66ceb0451e7dae8dc64ff74aaaa5e19929bbbdd4fc33268a4e91dce5"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid barring each holder from taking part in the cultural life of the community. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-cultural-life-by-anyone",
                    "over": [],
                    "predicate": "avoid_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "88fc6abda5e0f7dd1ad83e54e065d27e317cf4ca93b9883670fcd8070130b063"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "c102aaafde350bd9f8f8271c4b6c0196049b82a5e38b06dff899730985f689ca",
              "anyone_positive_default": "84a8007d733703b65796bf0fbd5db43cee10bb579d9d379f6f154e0240392e49",
              "anyone_positive_strict": "84a8007d733703b65796bf0fbd5db43cee10bb579d9d379f6f154e0240392e49",
              "state_negative_default": "84b42f5164b553f87261562473870a0b26d1557f7fcc54eecd060cc3bcbb6f0e",
              "state_negative_strict": "c102aaafde350bd9f8f8271c4b6c0196049b82a5e38b06dff899730985f689ca",
              "state_positive_default": "83dc88dbe6401427fb5f9834742d4d7ca62c567f351d3550815e26eff795098c",
              "state_positive_strict": "3a693053b49e9856ff10ec341a111c732e0057b1ec12bf408c75a3615aad808c"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid barring each holder from taking part in the cultural life of the community unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-cultural-life-by-anyone",
                    "over": [],
                    "predicate": "avoid_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "ed9a36dcd42cde5c66d98fbc439a04f539119e74b762c7a9b24ff9d31a360b22"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "84a8007d733703b65796bf0fbd5db43cee10bb579d9d379f6f154e0240392e49",
              "anyone_negative_strict": "d02b6c89b7e69d591fc651d14471b1ddebcfcf38fa082777245e63605fdd7b01",
              "anyone_positive_default": "e128c842d61166cda17b3bcf51e9aa7401eb2c2307c6b86654b67de166bb696c",
              "state_negative_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_negative_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_positive_default": "a43360ae7d5fb13f6e9f34667eea9c08a75cad29a8eb62f435a2b44bfa4e60b6",
              "state_positive_strict": "7c8c0c02d54cc808448180d5af4ca58d7edf271e22361c69bb981b893cdeb80e"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder free participation in the cultural life of the community. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-cultural-life-by-anyone",
                    "over": [],
                    "predicate": "secure_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "5121d25d12f894c2272a168cac2f88397d0a3d9f498dbad0698d1123e3ad310d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "84a8007d733703b65796bf0fbd5db43cee10bb579d9d379f6f154e0240392e49",
              "anyone_negative_strict": "d02b6c89b7e69d591fc651d14471b1ddebcfcf38fa082777245e63605fdd7b01",
              "anyone_positive_strict": "e128c842d61166cda17b3bcf51e9aa7401eb2c2307c6b86654b67de166bb696c",
              "state_negative_default": "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e",
              "state_negative_strict": "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb",
              "state_positive_default": "df61a1dfbaf5d622b6d8f7fb542b8f406bbce40746a3afc3d47eb767c8eae625",
              "state_positive_strict": "e128c842d61166cda17b3bcf51e9aa7401eb2c2307c6b86654b67de166bb696c"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder free participation in the cultural life of the community unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-cultural-life-by-anyone",
                    "over": [],
                    "predicate": "secure_cultural_life_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "cultural-life"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "10a721c3242ca4b6b6575a8c2a2565d3fea0b3f2dff3ea4e147fafab21f9ddb1"
        }
      ],
      "situations": {
        "3a693053b49e9856ff10ec341a111c732e0057b1ec12bf408c75a3615aad808c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "3d0556e44d34153882c3c15d24256c85767eead693f9cae987e541f3f3161cbb": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        },
        "7beebbad66ceb0451e7dae8dc64ff74aaaa5e19929bbbdd4fc33268a4e91dce5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "7c8c0c02d54cc808448180d5af4ca58d7edf271e22361c69bb981b893cdeb80e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "83dc88dbe6401427fb5f9834742d4d7ca62c567f351d3550815e26eff795098c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "84a8007d733703b65796bf0fbd5db43cee10bb579d9d379f6f154e0240392e49": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "84b42f5164b553f87261562473870a0b26d1557f7fcc54eecd060cc3bcbb6f0e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "a43360ae7d5fb13f6e9f34667eea9c08a75cad29a8eb62f435a2b44bfa4e60b6": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-cultural-life-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "add0e17c239fde71cfe0b973ef3d29acf197bead43c92e9d151c3820ecef040e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        },
        "b393d439325b5d399a310113b09af55f08bed437222f47a1344bd14e42146e3d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "c102aaafde350bd9f8f8271c4b6c0196049b82a5e38b06dff899730985f689ca": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-cultural-life-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "c135aa4c76cd7af4bb4ce430aecaf4030d25fda921ad80107e360ea63039b635": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-cultural-life-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "d02b6c89b7e69d591fc651d14471b1ddebcfcf38fa082777245e63605fdd7b01": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "df61a1dfbaf5d622b6d8f7fb542b8f406bbce40746a3afc3d47eb767c8eae625": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "df716768412298e05b8fd540391fd86e1a0e89129103a377f8e17aa706974436": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "e128c842d61166cda17b3bcf51e9aa7401eb2c2307c6b86654b67de166bb696c": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-cultural-life-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_cultural_life_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        }
      },
      "status": "open",
      "unit": "u105a",
      "version": 1
    },
    {
      "id": "rs_u105b",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b1d0edef2da88becd1231399e24aafdd266b2ad39412b63185995ca405074c26",
              "anyone_negative_strict": "8e96a4f3b2bb6b568705968b311cdf54193f0749be3ba19d2e41842ee5313887",
              "anyone_positive_default": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "anyone_positive_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_negative_default": "f210e4e1529e95e9fa4dcad67f057b35c5bbd8f5566bc6607ab8c048dd65cdd9",
              "state_positive_default": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_positive_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must avoid barring each holder from enjoying the arts. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-enjoyment-of-the-arts-by-state",
                    "over": [],
                    "predicate": "avoid_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "state_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "c8c1c54dd2bb8f798e3249713541b113449cdb279b44b4a9779cf70e19d7d752"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b89c99ab63e43cf4b309e842f90513c92c4f010ebab82c8f0d0e1edb9871c3e0",
              "anyone_negative_strict": "f210e4e1529e95e9fa4dcad67f057b35c5bbd8f5566bc6607ab8c048dd65cdd9",
              "anyone_positive_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "anyone_positive_strict": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_negative_strict": "f210e4e1529e95e9fa4dcad67f057b35c5bbd8f5566bc6607ab8c048dd65cdd9",
              "state_positive_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_positive_strict": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must avoid barring each holder from enjoying the arts unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "avoid-enjoyment-of-the-arts-by-state",
                    "over": [],
                    "predicate": "avoid_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "state_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "800ace4d82c286c9a175a8d48da1c2624183fc71fa0b701d3558d5b1c26e2444"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "9d65b413303e8a544a5d1d425b13b9f6af7736577fe499784e38cc636eb36a4d",
              "anyone_negative_strict": "86d01d4254276fa7abeaa7d67575bb79d781e744237f99935800d609b21bae7e",
              "anyone_positive_default": "93ac16f9f711a9c961cc36b1987cbadc0ec56ee4f1f034b9d23d415d222dda93",
              "anyone_positive_strict": "ff6aac61773aa5a44b473e553613fd8656342163125f210de0d867ee2185c637",
              "state_negative_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_negative_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_positive_default": "bd88c9a6c4a041487a9658325c42f523a9c4c82b50fc11343cdbd830656e5330"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder the enjoyment of the arts. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-enjoyment-of-the-arts-by-state",
                    "over": [],
                    "predicate": "secure_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "state_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "91aca1773d18aa745f20ffc1ed9df3ec80a06cba0effd0506cd6a1821f56d919"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "faad53e3f9522b0a8258142f8e02fefd12118b01fb39e647665e5a7e56843100",
              "anyone_negative_strict": "85493b3d3824dc3b120fd90efa71ec13c21aba9c2f6c26684c9a169d05318309",
              "anyone_positive_default": "87d6b4588b22f0b59b9de00dc3002925a67a3ceaa5167c159ed58559d2297b48",
              "anyone_positive_strict": "bd88c9a6c4a041487a9658325c42f523a9c4c82b50fc11343cdbd830656e5330",
              "state_negative_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_negative_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_positive_strict": "bd88c9a6c4a041487a9658325c42f523a9c4c82b50fc11343cdbd830656e5330"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder the enjoyment of the arts unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-enjoyment-of-the-arts-by-state",
                    "over": [],
                    "predicate": "secure_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "state_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "585a6227601a38cea8ca746971079caf75b6ed8eebbd6739c07c375f99d8e886"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "b1d0edef2da88becd1231399e24aafdd266b2ad39412b63185995ca405074c26",
              "anyone_positive_default": "cb47ae27650a84baf5073ed315983e464120f26f23287af50f32fc6bb6b6108e",
              "anyone_positive_strict": "cb47ae27650a84baf5073ed315983e464120f26f23287af50f32fc6bb6b6108e",
              "state_negative_default": "f210e4e1529e95e9fa4dcad67f057b35c5bbd8f5566bc6607ab8c048dd65cdd9",
              "state_negative_strict": "8e96a4f3b2bb6b568705968b311cdf54193f0749be3ba19d2e41842ee5313887",
              "state_positive_default": "85493b3d3824dc3b120fd90efa71ec13c21aba9c2f6c26684c9a169d05318309",
              "state_positive_strict": "86d01d4254276fa7abeaa7d67575bb79d781e744237f99935800d609b21bae7e"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must avoid barring each holder from enjoying the arts. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to avoid harming the right."
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
                    "name": "avoid-enjoyment-of-the-arts-by-anyone",
                    "over": [],
                    "predicate": "avoid_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "anyone_negative_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "3b7a1ba4147ccef8d1710af2e3af21a27d26223b59a6b05e93ab8e0b5f48b2aa"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_strict": "b1d0edef2da88becd1231399e24aafdd266b2ad39412b63185995ca405074c26",
              "anyone_positive_default": "6e935525cf0db4fa37f514062566f791d7cb7f0e2004625adfa941fbd1a003c2",
              "anyone_positive_strict": "6e935525cf0db4fa37f514062566f791d7cb7f0e2004625adfa941fbd1a003c2",
              "state_negative_default": "b89c99ab63e43cf4b309e842f90513c92c4f010ebab82c8f0d0e1edb9871c3e0",
              "state_negative_strict": "b1d0edef2da88becd1231399e24aafdd266b2ad39412b63185995ca405074c26",
              "state_positive_default": "faad53e3f9522b0a8258142f8e02fefd12118b01fb39e647665e5a7e56843100",
              "state_positive_strict": "9d65b413303e8a544a5d1d425b13b9f6af7736577fe499784e38cc636eb36a4d"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must avoid barring each holder from enjoying the arts unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to avoid harming the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "avoid-enjoyment-of-the-arts-by-anyone",
                    "over": [],
                    "predicate": "avoid_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "anyone_negative_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "negative"
          },
          "meaning_id": "144238b827783f6aa5a33f860e8fb449eca49e58af4c5bb5ac427f71f8b1e633"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "6e935525cf0db4fa37f514062566f791d7cb7f0e2004625adfa941fbd1a003c2",
              "anyone_negative_strict": "cb47ae27650a84baf5073ed315983e464120f26f23287af50f32fc6bb6b6108e",
              "anyone_positive_default": "93ac16f9f711a9c961cc36b1987cbadc0ec56ee4f1f034b9d23d415d222dda93",
              "state_negative_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_negative_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_positive_default": "bd88c9a6c4a041487a9658325c42f523a9c4c82b50fc11343cdbd830656e5330",
              "state_positive_strict": "ff6aac61773aa5a44b473e553613fd8656342163125f210de0d867ee2185c637"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder the enjoyment of the arts. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The duty is to secure the right."
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
                    "name": "secure-enjoyment-of-the-arts-by-anyone",
                    "over": [],
                    "predicate": "secure_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "anyone_positive_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "d2a0f1203c24374bcd82a8bc6b88b05b47ed054e98da2622976de6f27bbc8360"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_negative_default": "6e935525cf0db4fa37f514062566f791d7cb7f0e2004625adfa941fbd1a003c2",
              "anyone_negative_strict": "cb47ae27650a84baf5073ed315983e464120f26f23287af50f32fc6bb6b6108e",
              "anyone_positive_strict": "93ac16f9f711a9c961cc36b1987cbadc0ec56ee4f1f034b9d23d415d222dda93",
              "state_negative_default": "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f",
              "state_negative_strict": "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a",
              "state_positive_default": "87d6b4588b22f0b59b9de00dc3002925a67a3ceaa5167c159ed58559d2297b48",
              "state_positive_strict": "93ac16f9f711a9c961cc36b1987cbadc0ec56ee4f1f034b9d23d415d222dda93"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder the enjoyment of the arts unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The duty is to secure the right. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-enjoyment-of-the-arts-by-anyone",
                    "over": [],
                    "predicate": "secure_enjoyment_of_the_arts_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "enjoyment-of-the-arts"
            }
          },
          "id": "anyone_positive_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim",
            "polarity": "positive"
          },
          "meaning_id": "5b7db4952cf50113d9a1d274d65df1a13857a1ced34d4b4daf976362d3a4e5ad"
        }
      ],
      "situations": {
        "6e935525cf0db4fa37f514062566f791d7cb7f0e2004625adfa941fbd1a003c2": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "822763ab8accf103e4d3192ffe2f8612b8d907d257dc8cf104abbc2e2a241c7f": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_default"
        },
        "85493b3d3824dc3b120fd90efa71ec13c21aba9c2f6c26684c9a169d05318309": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "86d01d4254276fa7abeaa7d67575bb79d781e744237f99935800d609b21bae7e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        },
        "87d6b4588b22f0b59b9de00dc3002925a67a3ceaa5167c159ed58559d2297b48": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_positive_default"
        },
        "8e96a4f3b2bb6b568705968b311cdf54193f0749be3ba19d2e41842ee5313887": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_strict"
        },
        "91a48ddd5de67f667b3ed59b42d1f9ac236caf1123d3175f62e14085112a7b2a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_negative_strict"
        },
        "93ac16f9f711a9c961cc36b1987cbadc0ec56ee4f1f034b9d23d415d222dda93": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-enjoyment-of-the-arts-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_positive_default"
        },
        "9d65b413303e8a544a5d1d425b13b9f6af7736577fe499784e38cc636eb36a4d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_strict"
        },
        "b1d0edef2da88becd1231399e24aafdd266b2ad39412b63185995ca405074c26": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-enjoyment-of-the-arts-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_negative_default"
        },
        "b89c99ab63e43cf4b309e842f90513c92c4f010ebab82c8f0d0e1edb9871c3e0": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_default"
        },
        "bd88c9a6c4a041487a9658325c42f523a9c4c82b50fc11343cdbd830656e5330": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-enjoyment-of-the-arts-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_default"
        },
        "cb47ae27650a84baf5073ed315983e464120f26f23287af50f32fc6bb6b6108e": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_negative_strict"
        },
        "f210e4e1529e95e9fa4dcad67f057b35c5bbd8f5566bc6607ab8c048dd65cdd9": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "avoid-enjoyment-of-the-arts-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "avoid_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_negative_default"
        },
        "faad53e3f9522b0a8258142f8e02fefd12118b01fb39e647665e5a7e56843100": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "state_positive_default"
        },
        "ff6aac61773aa5a44b473e553613fd8656342163125f210de0d867ee2185c637": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_enjoyment_of_the_arts_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_positive_strict"
        }
      },
      "status": "open",
      "unit": "u105b",
      "version": 1
    },
    {
      "id": "rs_u105c",
      "readings": [
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "4411184d99048c937a763b3f8b37c5370f350acdad4867300d9306bfca3e2b4d",
              "anyone_claim_strict": "2c62c74b3812686378804e16e64dc3bf55399482f54b5ef274dcb5ebbcbac4f5",
              "state_claim_default": "95a6e4d19e0604d55096575ee4f2085f4338089dc2a26cd67470017ca5f6a30a"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state must secure each holder a share in scientific advancement as well as its benefits. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-scientific-advancement-by-state",
                    "over": [],
                    "predicate": "secure_scientific_advancement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "scientific-advancement"
            }
          },
          "id": "state_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "07c67592c5abb68a98ba1adbb76612ba35d6b808cfe5619131009d0a55ed65c2"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "7475e272ba96ff5ddf8746cf588a9d8a1018f21dd503d1b3621ac4771c1024c3",
              "anyone_claim_strict": "95a6e4d19e0604d55096575ee4f2085f4338089dc2a26cd67470017ca5f6a30a",
              "state_claim_strict": "95a6e4d19e0604d55096575ee4f2085f4338089dc2a26cd67470017ca5f6a30a"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state must secure each holder a share in scientific advancement as well as its benefits unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "unary",
                      "is_state",
                      [
                        "var",
                        1
                      ]
                    ],
                    "mode": "default",
                    "name": "secure-scientific-advancement-by-state",
                    "over": [],
                    "predicate": "secure_scientific_advancement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "scientific-advancement"
            }
          },
          "id": "state_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "state",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "676dd500386a2e39cb297807fd655d96717365194d531219a16817c802eb2f8d"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_default": "4411184d99048c937a763b3f8b37c5370f350acdad4867300d9306bfca3e2b4d",
              "state_claim_default": "95a6e4d19e0604d55096575ee4f2085f4338089dc2a26cd67470017ca5f6a30a",
              "state_claim_strict": "2c62c74b3812686378804e16e64dc3bf55399482f54b5ef274dcb5ebbcbac4f5"
            },
            "who": "translator",
            "why": "Claim reading, Strict reading (the source carries or opens its force): every state, group and person must secure each holder a share in scientific advancement as well as its benefits. The source names no bearer, so the bearer is the translator's candidate. Outside this rule the declared completion is 'deny' (not required): it grants no permission to anyone and is not stated by the source. The right's one duty."
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
                    "name": "secure-scientific-advancement-by-anyone",
                    "over": [],
                    "predicate": "secure_scientific_advancement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "scientific-advancement"
            }
          },
          "id": "anyone_claim_strict",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "strict",
            "incident": "claim"
          },
          "meaning_id": "6f27b56748315d1d8ce1ced903e65c0e43fffa28f5edcb563587180cafe8fb49"
        },
        {
          "admission": {
            "distinguishing_models": {
              "anyone_claim_strict": "4411184d99048c937a763b3f8b37c5370f350acdad4867300d9306bfca3e2b4d",
              "state_claim_default": "7475e272ba96ff5ddf8746cf588a9d8a1018f21dd503d1b3621ac4771c1024c3",
              "state_claim_strict": "4411184d99048c937a763b3f8b37c5370f350acdad4867300d9306bfca3e2b4d"
            },
            "who": "translator",
            "why": "Claim reading, Defeasible reading (the source carries or opens its force): every state, group and person must secure each holder a share in scientific advancement as well as its benefits unless this rule's exception applies; the source names no decider (decided_by unstated). The declared completion is 'deny' (not required), as for the strict reading: not stated by the source, grants no permission to anyone. The right's one duty. The exception's factor is the organization and resources of each State, from Article 22 (the translator's cross-reference, not a checked one)."
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
                    "exception": {
                      "decided_by": "unstated",
                      "factors": [
                        "the organization and resources of each State (Article 22)"
                      ],
                      "necessary": [],
                      "sufficient": []
                    },
                    "guard": [
                      "top"
                    ],
                    "mode": "default",
                    "name": "secure-scientific-advancement-by-anyone",
                    "over": [],
                    "predicate": "secure_scientific_advancement_required",
                    "sign": true,
                    "unless": []
                  }
                }
              ],
              "name": "scientific-advancement"
            }
          },
          "id": "anyone_claim_default",
          "kind": "right",
          "labels": {
            "bearer": "anyone",
            "force": "default",
            "incident": "claim"
          },
          "meaning_id": "3a9371fe40ba06b4940e1675db126f11172d14acf70729c1b23548fdea629d03"
        }
      ],
      "situations": {
        "2c62c74b3812686378804e16e64dc3bf55399482f54b5ef274dcb5ebbcbac4f5": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_scientific_advancement_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_strict"
        },
        "4411184d99048c937a763b3f8b37c5370f350acdad4867300d9306bfca3e2b4d": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-scientific-advancement-by-anyone"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_scientific_advancement_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "anyone_claim_default"
        },
        "7475e272ba96ff5ddf8746cf588a9d8a1018f21dd503d1b3621ac4771c1024c3": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
              ]
            },
            "relations": {
              "arises_from_acts_contrary_to_un": [],
              "arises_from_non_political_crime": [],
              "asylum_right_covers_case": [],
              "declaration_implies_destructive_right": [],
              "exercise_contrary_to_un": [],
              "is_state": [],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_scientific_advancement_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": true,
          "witness": "anyone_claim_default"
        },
        "95a6e4d19e0604d55096575ee4f2085f4338089dc2a26cd67470017ca5f6a30a": {
          "base": {
            "constants": {},
            "domains": {
              "actor": [
                "a"
              ],
              "bearer": [
                "b"
              ],
              "exercise": [
                "e"
              ],
              "person": [
                "person"
              ],
              "prosecution": [
                "prosecution"
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
                  "b"
                ]
              ],
              "of_age_for_elementary_education": [],
              "right_protects_exercise": []
            }
          },
          "decisions": [
            {
              "key": {
                "excepted": "secure-scientific-advancement-by-state"
              },
              "tuples": [
                [
                  "b",
                  "person"
                ]
              ]
            }
          ],
          "fixed": [],
          "probe": {
            "outcome": {
              "predicate": "secure_scientific_advancement_required",
              "tuple": [
                "b",
                "person"
              ]
            }
          },
          "value": false,
          "witness": "state_claim_default"
        }
      },
      "status": "open",
      "unit": "u105c",
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
      "kind": "norm",
      "meaning": {
        "open": [
          "status_of_country_or_territory"
        ]
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
      "kind": "norm",
      "meaning": {
        "open": [
          "slavery",
          "servitude"
        ]
      },
      "span": [
        2869,
        2915
      ],
      "support": "none"
    },
    {
      "id": "u025",
      "kind": "norm",
      "meaning": {
        "open": [
          "slavery",
          "slave_trade"
        ]
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
      "kind": "norm",
      "meaning": {
        "open": [
          "ill_treatment"
        ]
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
      "kind": "norm",
      "meaning": {
        "open": [
          "arbitrary"
        ]
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
        "time"
      ],
      "meaning": {
        "unformalised": "time"
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
        "time"
      ],
      "meaning": {
        "unformalised": "time"
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
      "kind": "norm",
      "meaning": {
        "open": [
          "arbitrary",
          "private_life"
        ]
      },
      "span": [
        4484,
        4584
      ],
      "support": "none"
    },
    {
      "id": "u045b",
      "kind": "norm",
      "meaning": "specified",
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
      "meaning": {
        "open": [
          "bearer_of_the_nationality_duty"
        ]
      },
      "span": [
        5239,
        5284
      ],
      "support": "none"
    },
    {
      "id": "u055",
      "kind": "norm",
      "meaning": {
        "open": [
          "arbitrary"
        ]
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
      "kind": "norm",
      "meaning": {
        "open": [
          "free_and_full_consent"
        ]
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
      "kind": "norm",
      "meaning": {
        "open": [
          "arbitrary"
        ]
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
        "other_right_lines_across_open_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_across_open_sets"
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
        "other_right_lines_across_open_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_across_open_sets"
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
        "other_right_lines_across_open_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_across_open_sets"
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
        "other_right_lines_across_open_sets"
      ],
      "meaning": {
        "unformalised": "other_right_lines_across_open_sets"
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
        "other_grounding_of_authority"
      ],
      "meaning": {
        "unformalised": "other_grounding_of_authority"
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
        "time"
      ],
      "meaning": {
        "unformalised": "time"
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
      "kind": "right",
      "meaning": {
        "open": [
          "social_security"
        ]
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
      "kind": "right",
      "meaning": "specified",
      "span": [
        7573,
        7606
      ],
      "support": "none"
    },
    {
      "id": "u084b",
      "kind": "right",
      "meaning": "specified",
      "span": [
        7606,
        7636
      ],
      "support": "none"
    },
    {
      "id": "u084c",
      "kind": "right",
      "meaning": {
        "open": [
          "just_and_favourable_conditions_of_work"
        ]
      },
      "span": [
        7636,
        7679
      ],
      "support": "none"
    },
    {
      "id": "u084d",
      "kind": "right",
      "meaning": "specified",
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
      },
      "span": [
        7806,
        8022
      ],
      "support": "none"
    },
    {
      "id": "u087",
      "kind": "right",
      "meaning": "specified",
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
        "time"
      ],
      "meaning": {
        "unformalised": "time"
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
        "other_comparison"
      ],
      "meaning": {
        "unformalised": "other_comparison"
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
        "other_comparison"
      ],
      "meaning": {
        "unformalised": "other_comparison"
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
      "kind": "right",
      "meaning": "specified",
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
        "quantities"
      ],
      "meaning": {
        "unformalised": "quantities"
      },
      "span": [
        8857,
        8933
      ],
      "support": "none"
    },
    {
      "id": "u098",
      "kind": "norm",
      "meaning": {
        "open": [
          "compulsory"
        ]
      },
      "span": [
        8933,
        8975
      ],
      "support": "none"
    },
    {
      "id": "u099a",
      "kind": "norm",
      "meaning": {
        "open": [
          "generally_available"
        ]
      },
      "span": [
        8975,
        9045
      ],
      "support": "none"
    },
    {
      "id": "u099b",
      "kind": "norm",
      "meaning": {
        "open": [
          "merit"
        ]
      },
      "span": [
        9045,
        9126
      ],
      "support": "none"
    },
    {
      "id": "u100a",
      "kind": "norm",
      "meaning": {
        "open": [
          "full_development_of_the_human_personality"
        ]
      },
      "span": [
        9126,
        9205
      ],
      "support": "none"
    },
    {
      "id": "u100b",
      "kind": "norm",
      "meaning": {
        "open": [
          "rights_and_freedoms_set_forth"
        ]
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
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
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
        "causation"
      ],
      "meaning": {
        "unformalised": "causation"
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
        "other_priority_of_rights"
      ],
      "meaning": {
        "unformalised": "other_priority_of_rights"
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
      "kind": "right",
      "meaning": "specified",
      "span": [
        9592,
        9677
      ],
      "support": "none"
    },
    {
      "id": "u105b",
      "kind": "right",
      "meaning": "specified",
      "span": [
        9677,
        9696
      ],
      "support": "none"
    },
    {
      "id": "u105c",
      "kind": "right",
      "meaning": "specified",
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
        "other_act_phrase_grammar"
      ],
      "meaning": {
        "unformalised": "other_act_phrase_grammar"
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
