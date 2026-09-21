# English rendering

Generated from the unchanged environment and strict claims. Quoted predicate names indicate missing or rejected lexical metadata.

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-fluent uv run python -m ve render \
  --env usecases/birthright-citizenship-debate/environment.json --view ve_english \
  usecases/birthright-citizenship-debate/claims.ve
```

## Statements

```text
For every person, if the following holds:
  (a) both that person is classified as "born_in_us" and that person is classified as "subject_to_jurisdiction";
then the following holds:
  (b) that person is classified as "us_citizen".
For every person, if that person is classified as "has_noncitizen_domiciled_parent", then that person is classified as "subject_to_jurisdiction".
```

## Vocabulary and scope legend

```text
English vocabulary: ve.english-legend@1; environment: 8937bcba42188c0dab8fe6d85252d527e99cc0c91a6f9ff9f62d42e6f029b3d5
A unique sort uses that noun. Two simultaneous entities of a sort use first and second throughout the statement. Beyond two, all entities of that sort use numbered letters. Scope is lexical and restarts per statement.
Constants use their identifier names; reserved or compound names are quoted.
Starting from the first endpoint, the second is reachable. A step body binds source first and destination second; outer references stay fixed.
Numbered letters: person = P
Sort person: {"noun": "person", "description": "A person whose U.S. citizenship status under the 14th Amendment's Citizenship Clause is at issue in the debate."}
Predicate born_in_us: {"arguments": ["person"], "template": "{0} is classified as \"born_in_us\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as born on U.S. soil. Both sides of the debate accept this predicate and its extension without dispute."}
Predicate has_noncitizen_domiciled_parent: {"arguments": ["person"], "template": "{0} is classified as \"has_noncitizen_domiciled_parent\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen permanently domiciled/residing in the U.S. but legally ineligible for naturalization (the parental profile in United States v. Wong Kim Ark, 1898). Both sides accept Wong Kim Ark's outcome for this profile."}
Predicate has_noncitizen_temporary_parent: {"arguments": ["person"], "template": "{0} is classified as \"has_noncitizen_temporary_parent\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen present in the U.S. only temporarily (tourist, student, or other non-immigrant visa) -- the 'birth tourism' profile Krikorian raises."}
Predicate has_noncitizen_undocumented_parent: {"arguments": ["person"], "template": "{0} is classified as \"has_noncitizen_undocumented_parent\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as having at least one parent who is a non-citizen present in the U.S. without legal immigration status. This is the profile the 'end birthright citizenship' side argues falls outside subject_to_jurisdiction, and the 'keep it' side argues falls inside it."}
Predicate subject_to_jurisdiction: {"arguments": ["person"], "template": "{0} is classified as \"subject_to_jurisdiction\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as satisfying 'subject to the jurisdiction thereof' (14th Amendment, Citizenship Clause). THIS IS THE CONTESTED PREDICATE: both sides use the same word 'jurisdiction' and accept the same syntactic role for it in the Citizenship Clause, but assign it different extensions. Krikorian/Cooper read it as complete, exclusive political allegiance (owing no allegiance to a foreign sovereign); Mayes/Newman read it as being present in U.S. territory and bound by / enforceable under U.S. law. See claim-graph.md."}
Predicate us_citizen: {"arguments": ["person"], "template": "{0} is classified as \"us_citizen\"", "declared_template": null, "negative_template": null, "declared_negative_template": null, "description": "Recorded as a U.S. citizen under the Citizenship Clause reading at issue. Both sides accept the predicate; they dispute its extension for specific people because they dispute the extension of subject_to_jurisdiction."}
Constant child: {"name": "child", "sort": "person", "description": "A representative child born in the United States, used to test the debate's central syllogism concretely (the debate's own paradigm example, not a real individual)."}
```
