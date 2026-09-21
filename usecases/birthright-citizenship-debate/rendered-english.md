# English rendering

Generated from the unchanged environment and strict claims. The reviewed display-only overlay has its own digest in the legend; it does not change environment or meaning identity.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/birthright-citizenship-debate/environment.json --view ve_english \
  --english-vocabulary usecases/birthright-citizenship-debate/environment.english.json \
  usecases/birthright-citizenship-debate/claims.ve
```

## Statements

```text
Every person who is born in the United States and is subject to US jurisdiction is a US citizen.
Every person who has a noncitizen parent domiciled in the United States is subject to US jurisdiction.
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: 8937bcba42188c0dab8fe6d85252d527e99cc0c91a6f9ff9f62d42e6f029b3d5
Display overlay digest: 6669967f3970d60ef2aaa08ab007b43fa5cda8740a466b489e402d2a0737df3e
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: person = P
Sort person: {"noun": "person", "description": "A person whose U.S. citizenship status under the 14th Amendment's Citizenship Clause is at issue in the debate.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": {"singular": "person", "plural": "people"}}
Predicate born_in_us: {"arguments": ["person"], "template": "{0} is born in the United States", "declared_template": null, "negative_template": "{0} is not born in the United States", "declared_negative_template": null, "description": "Recorded as born on U.S. soil. Both sides of the debate accept this predicate and its extension without dispute.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is born in the United States"}
Predicate has_noncitizen_domiciled_parent: {"arguments": ["person"], "template": "{0} has a noncitizen parent domiciled in the United States", "declared_template": null, "negative_template": "{0} does not have a noncitizen parent domiciled in the United States", "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen permanently domiciled/residing in the U.S. but legally ineligible for naturalization (the parental profile in United States v. Wong Kim Ark, 1898). Both sides accept Wong Kim Ark's outcome for this profile.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} has a noncitizen parent domiciled in the United States"}
Predicate has_noncitizen_temporary_parent: {"arguments": ["person"], "template": "{0} has a noncitizen parent temporarily in the United States", "declared_template": null, "negative_template": "{0} does not have a noncitizen parent temporarily in the United States", "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen present in the U.S. only temporarily (tourist, student, or other non-immigrant visa) -- the 'birth tourism' profile Krikorian raises.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} has a noncitizen parent temporarily in the United States"}
Predicate has_noncitizen_undocumented_parent: {"arguments": ["person"], "template": "{0} has an undocumented noncitizen parent", "declared_template": null, "negative_template": "{0} does not have an undocumented noncitizen parent", "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen present in the U.S. without legal immigration status. This is the profile the 'end birthright citizenship' side argues falls outside subject_to_jurisdiction, and the 'keep it' side argues falls inside it.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} has an undocumented noncitizen parent"}
Predicate subject_to_jurisdiction: {"arguments": ["person"], "template": "{0} is subject to US jurisdiction", "declared_template": null, "negative_template": "{0} is not subject to US jurisdiction", "declared_negative_template": null, "description": "Recorded as satisfying 'subject to the jurisdiction thereof' (14th Amendment, Citizenship Clause). THIS IS THE CONTESTED PREDICATE: both sides use the same word 'jurisdiction' and accept the same syntactic role for it in the Citizenship Clause, but assign it different extensions. Krikorian/Cooper read it as complete, exclusive political allegiance (owing no allegiance to a foreign sovereign); Mayes/Newman read it as being present in U.S. territory and bound by / enforceable under U.S. law. See claim-graph.md.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is subject to US jurisdiction"}
Predicate us_citizen: {"arguments": ["person"], "template": "{0} is a US citizen", "declared_template": null, "negative_template": "{0} is not a US citizen", "declared_negative_template": null, "description": "Recorded as a U.S. citizen under the Citizenship Clause reading at issue. Both sides accept the predicate; they dispute its extension for specific people because they dispute the extension of subject_to_jurisdiction.", "suggested": false, "review_status": "reviewed", "overlay_verbalisation": "{0} is a US citizen"}
Constant child: {"name": "child", "sort": "person", "description": "A representative child born in the United States, used to test the debate's central syllogism concretely (the debate's own paradigm example, not a real individual)."}
```
