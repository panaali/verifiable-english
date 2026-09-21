# English rendering

Generated from the unchanged environment and strict claims. The reviewed display-only overlay has its own digest in the legend; it does not change environment or meaning identity.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/us-constitution-14th-s1/environment.json --view ve_english \
  --english-vocabulary usecases/us-constitution-14th-s1/environment.english.json \
  usecases/us-constitution-14th-s1/claims.ve
```

## Statements

```text
For every person, if all of the following hold:
  (a) either that person was born in the United States or that person was naturalized in the United States, or both;
  (b) that person is subject to the jurisdiction of the United States, then both of the following hold:
  (a) that person is a citizen of the United States;
  (b) for every state that that person resides in, that person is a citizen of that state.
For every state, for every law, for every person, if all of the following hold:
  (a) either that state makes that law or that state enforces that law, or both;
  (b) that person is a citizen of the United States, then that law does not abridge the privileges or immunities of that person.
For every state, for every person who that state deprives of life, liberty, or property, that state affords due process of law to that person.
For every state, for every person who is within the jurisdiction of that state, that state does not deny the equal protection of the laws to that person.
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: 49d16fe885310c0b43a882958da6799a89e926e925b42cc1da49e27d3de8fe15
Display overlay digest: ae4741bfe4a84aab00116945191867317df7b2b58837bfda3c5d11a070c76d64
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: law = L, person = P, state = S
Sort law: {"noun": "law", "description": "A law that a State may make or enforce.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": {"singular": "law", "plural": "laws"}}
Sort person: {"noun": "person", "description": "A natural person who may be born, naturalized, resident, or subject to jurisdiction.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": {"singular": "person", "plural": "people"}}
Sort state: {"noun": "state", "description": "A U.S. State, i.e. a state-level jurisdiction capable of making or enforcing law.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": {"singular": "state", "plural": "states"}}
Predicate abridges_priv_or_imm: {"arguments": ["law", "person"], "template": "{0} abridges the privileges or immunities of {1}", "declared_template": "{0} abridges the privileges or immunities of {1}", "negative_template": "{0} does not abridge the privileges or immunities of {1}", "declared_negative_template": null, "description": "Recorded as a law that abridges the privileges or immunities of the person as a citizen of the United States. This predicate bundles the entire contested substantive content of 'privileges or immunities' opaquely; see GAPS.md.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} abridges the privileges or immunities of {1}"}
Predicate affords_due_process: {"arguments": ["state", "person"], "template": "{0} affords due process of law to {1}", "declared_template": "{0} affords due process of law to {1}", "negative_template": "{0} does not afford due process of law to {1}", "declared_negative_template": null, "description": "Recorded as the state affording due process of law to the person for a deprivation. This predicate bundles the entire contested substantive content of 'due process' opaquely; see GAPS.md.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} affords due process of law to {1}"}
Predicate born_in_us: {"arguments": ["person"], "template": "{0} was born in the United States", "declared_template": "{0} was born in the United States", "negative_template": "{0} was not born in the United States", "declared_negative_template": null, "description": "Recorded as born in the United States.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} was born in the United States"}
Predicate citizen_of_state: {"arguments": ["person", "state"], "template": "{0} is a citizen of {1}", "declared_template": "{0} is a citizen of {1}", "negative_template": "{0} is not a citizen of {1}", "declared_negative_template": null, "description": "Recorded as a citizen of the state.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is a citizen of {1}"}
Predicate denies_equal_protection: {"arguments": ["state", "person"], "template": "{0} denies the equal protection of the laws to {1}", "declared_template": "{0} denies the equal protection of the laws to {1}", "negative_template": "{0} does not deny the equal protection of the laws to {1}", "declared_negative_template": null, "description": "Recorded as the state denying the person the equal protection of the laws. This predicate bundles the entire contested substantive content of 'equal protection' opaquely; see GAPS.md.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} denies the equal protection of the laws to {1}"}
Predicate deprives: {"arguments": ["state", "person"], "template": "{0} deprives {1} of life, liberty, or property", "declared_template": "{0} deprives {1} of life, liberty, or property", "negative_template": "{0} does not deprive {1} of life, liberty, or property", "declared_negative_template": null, "description": "Recorded as the state depriving the person of life, liberty, or property.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} deprives {1} of life, liberty, or property"}
Predicate enforces_law: {"arguments": ["state", "law"], "template": "{0} enforces {1}", "declared_template": "{0} enforces {1}", "negative_template": "{0} does not enforce {1}", "declared_negative_template": null, "description": "Recorded as enforcing the law.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} enforces {1}"}
Predicate makes_law: {"arguments": ["state", "law"], "template": "{0} makes {1}", "declared_template": "{0} makes {1}", "negative_template": "{0} does not make {1}", "declared_negative_template": null, "description": "Recorded as making (enacting) the law.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} makes {1}"}
Predicate naturalized_in_us: {"arguments": ["person"], "template": "{0} was naturalized in the United States", "declared_template": "{0} was naturalized in the United States", "negative_template": "{0} was not naturalized in the United States", "declared_negative_template": null, "description": "Recorded as naturalized in the United States.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} was naturalized in the United States"}
Predicate resides_in: {"arguments": ["person", "state"], "template": "{0} resides in {1}", "declared_template": "{0} resides in {1}", "negative_template": "{0} does not reside in {1}", "declared_negative_template": null, "description": "Recorded as residing in the state.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} resides in {1}"}
Predicate subject_to_us_jurisdiction: {"arguments": ["person"], "template": "{0} is subject to the jurisdiction of the United States", "declared_template": "{0} is subject to the jurisdiction of the United States", "negative_template": "{0} is not subject to the jurisdiction of the United States", "declared_negative_template": null, "description": "Recorded as subject to the jurisdiction of the United States.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is subject to the jurisdiction of the United States"}
Predicate us_citizen: {"arguments": ["person"], "template": "{0} is a citizen of the United States", "declared_template": "{0} is a citizen of the United States", "negative_template": "{0} is not a citizen of the United States", "declared_negative_template": null, "description": "Recorded as a citizen of the United States.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is a citizen of the United States"}
Predicate within_jurisdiction_of: {"arguments": ["person", "state"], "template": "{0} is within the jurisdiction of {1}", "declared_template": "{0} is within the jurisdiction of {1}", "negative_template": "{0} is not within the jurisdiction of {1}", "declared_negative_template": null, "description": "Recorded as the person being within the jurisdiction of the state.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is within the jurisdiction of {1}"}
```
