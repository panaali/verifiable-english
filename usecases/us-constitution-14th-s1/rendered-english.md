# English rendering

Generated from the unchanged environment and strict claims. Quoted predicate names indicate missing or rejected lexical metadata.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/us-constitution-14th-s1/environment.json --view ve_english \
  usecases/us-constitution-14th-s1/claims.ve
```

## Statements

```text
For every person, if the following holds:
  (a) all of the following hold:
    (i) either that person was born in the United States or that person was naturalized in the United States, or both;
    (ii) that person is subject to the jurisdiction of the United States;
then the following holds:
  (b) all of the following hold:
    (i) that person is a citizen of the United States;
    (ii) for every state, if that person resides in that state, then that person has the recorded relation "citizen_of_state" to that state.
For every state, for every law, for every person, if the following holds:
  (a) all of the following hold:
    (i) either that state makes that law or that state enforces that law, or both;
    (ii) that person is a citizen of the United States;
then the following holds:
  (b) it is not the case that that law has the recorded relation "abridges_priv_or_imm" to that person.
For every state, for every person, if that state has the recorded relation "deprives" to that person, then that state affords due process of law to that person.
For every state, for every person, if the following holds:
  (a) that person has the recorded relation "within_jurisdiction_of" to that state;
then the following holds:
  (b) it is not the case that that state denies the equal protection of the laws to that person.
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: 49d16fe885310c0b43a882958da6799a89e926e925b42cc1da49e27d3de8fe15
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: law = L, person = P, state = S
Sort law: {"noun": "law", "description": "A law that a State may make or enforce."}
Sort person: {"noun": "person", "description": "A natural person who may be born, naturalized, resident, or subject to jurisdiction."}
Sort state: {"noun": "state", "description": "A U.S. State, i.e. a state-level jurisdiction capable of making or enforcing law."}
Predicate abridges_priv_or_imm: {"arguments": ["law", "person"], "template": "{0} has the recorded relation \"abridges_priv_or_imm\" to {1}", "declared_template": "{0} abridges the privileges or immunities of {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as a law that abridges the privileges or immunities of the person as a citizen of the United States. This predicate bundles the entire contested substantive content of 'privileges or immunities' opaquely; see GAPS.md."}
Predicate affords_due_process: {"arguments": ["state", "person"], "template": "{0} affords due process of law to {1}", "declared_template": "{0} affords due process of law to {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as the state affording due process of law to the person for a deprivation. This predicate bundles the entire contested substantive content of 'due process' opaquely; see GAPS.md."}
Predicate born_in_us: {"arguments": ["person"], "template": "{0} was born in the United States", "declared_template": "{0} was born in the United States", "negative_template": null, "declared_negative_template": null, "description": "Recorded as born in the United States."}
Predicate citizen_of_state: {"arguments": ["person", "state"], "template": "{0} has the recorded relation \"citizen_of_state\" to {1}", "declared_template": "{0} is a citizen of {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as a citizen of the state."}
Predicate denies_equal_protection: {"arguments": ["state", "person"], "template": "{0} denies the equal protection of the laws to {1}", "declared_template": "{0} denies the equal protection of the laws to {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as the state denying the person the equal protection of the laws. This predicate bundles the entire contested substantive content of 'equal protection' opaquely; see GAPS.md."}
Predicate deprives: {"arguments": ["state", "person"], "template": "{0} has the recorded relation \"deprives\" to {1}", "declared_template": "{0} deprives {1} of life, liberty, or property", "negative_template": null, "declared_negative_template": null, "description": "Recorded as the state depriving the person of life, liberty, or property."}
Predicate enforces_law: {"arguments": ["state", "law"], "template": "{0} enforces {1}", "declared_template": "{0} enforces {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as enforcing the law."}
Predicate makes_law: {"arguments": ["state", "law"], "template": "{0} makes {1}", "declared_template": "{0} makes {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as making (enacting) the law."}
Predicate naturalized_in_us: {"arguments": ["person"], "template": "{0} was naturalized in the United States", "declared_template": "{0} was naturalized in the United States", "negative_template": null, "declared_negative_template": null, "description": "Recorded as naturalized in the United States."}
Predicate resides_in: {"arguments": ["person", "state"], "template": "{0} resides in {1}", "declared_template": "{0} resides in {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as residing in the state."}
Predicate subject_to_us_jurisdiction: {"arguments": ["person"], "template": "{0} is subject to the jurisdiction of the United States", "declared_template": "{0} is subject to the jurisdiction of the United States", "negative_template": null, "declared_negative_template": null, "description": "Recorded as subject to the jurisdiction of the United States."}
Predicate us_citizen: {"arguments": ["person"], "template": "{0} is a citizen of the United States", "declared_template": "{0} is a citizen of the United States", "negative_template": null, "declared_negative_template": null, "description": "Recorded as a citizen of the United States."}
Predicate within_jurisdiction_of: {"arguments": ["person", "state"], "template": "{0} has the recorded relation \"within_jurisdiction_of\" to {1}", "declared_template": "{0} is within the jurisdiction of {1}", "negative_template": null, "declared_negative_template": null, "description": "Recorded as the person being within the jurisdiction of the state."}
Lint /vocabulary/predicates/abridges_priv_or_imm/verbalisation: BINARY_CONVERSE
Lint /vocabulary/predicates/abridges_priv_or_imm/verbalisation: LOGICAL_WORD
Lint /vocabulary/predicates/citizen_of_state/verbalisation: BINARY_AUXILIARY
Lint /vocabulary/predicates/citizen_of_state/verbalisation: BINARY_CONVERSE
Lint /vocabulary/predicates/citizen_of_state/verbalisation: LOGICAL_WORD
Lint /vocabulary/predicates/citizen_of_state/verbalisation: SYMBOL_COLLISION
Lint /vocabulary/predicates/deprives/verbalisation: TEMPLATE_SHAPE
Lint /vocabulary/predicates/within_jurisdiction_of/verbalisation: BINARY_AUXILIARY
Lint /vocabulary/predicates/within_jurisdiction_of/verbalisation: BINARY_CONVERSE
Lint /vocabulary/predicates/within_jurisdiction_of/verbalisation: LOGICAL_WORD
Lint /vocabulary/predicates/within_jurisdiction_of/verbalisation: SYMBOL_COLLISION
```
