# Rendering (`ve_fluent`, with legend, compact style)

Command:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python -m ve render \
  --env usecases/birthright-citizenship-debate/environment.json \
  --view ve_fluent --with-legend --legend-style compact \
  usecases/birthright-citizenship-debate/claims.ve
```

Output (the two shared-core statements from `claims.ve`; see `claim-graph.md`
for the full claim graph and `countermodel/` for the entailment tests):

```
Vocabulary: ve.vocabulary-legend@3; environment: 8937bcba42188c0dab8fe6d85252d527e99cc0c91a6f9ff9f62d42e6f029b3d5
Sorts:
  person (noun: "person"/"people") — "A person whose U.S. citizenship status under the 14th Amendment's Citizenship Clause is at issue in the debate."
Constants:
  @child : person — "A representative child born in the United States, used to test the debate's central syllogism concretely (the debate's own paradigm example, not a real individual)."
Predicates:
  born_in_us(person) — "{0} is born_in_us" (strict fallback; declared: none) — "Recorded as born on U.S. soil. Both sides of the debate accept this predicate and its extension without dispute."
  has_noncitizen_domiciled_parent(person) — "{0} is has_noncitizen_domiciled_parent" (strict fallback; declared: none) — "Recorded as having at least one parent who is a non-citizen permanently domiciled/residing in the U.S. but legally ineligible for naturalization (the parental profile in United States v. Wong Kim Ark, 1898). Both sides accept Wong Kim Ark's outcome for this profile."
  has_noncitizen_temporary_parent(person) — "{0} is has_noncitizen_temporary_parent" (strict fallback; declared: none) — "Recorded as having at least one parent who is a non-citizen present in the U.S. only temporarily (tourist, student, or other non-immigrant visa) -- the 'birth tourism' profile Krikorian raises."
  has_noncitizen_undocumented_parent(person) — "{0} is has_noncitizen_undocumented_parent" (strict fallback; declared: none) — "Recorded as having at least one parent who is a non-citizen present in the U.S. without legal immigration status. This is the profile the 'end birthright citizenship' side argues falls outside subject_to_jurisdiction, and the 'keep it' side argues falls inside it."
  subject_to_jurisdiction(person) — "{0} is subject_to_jurisdiction" (strict fallback; declared: none) — "Recorded as satisfying 'subject to the jurisdiction thereof' (14th Amendment, Citizenship Clause). THIS IS THE CONTESTED PREDICATE: both sides use the same word 'jurisdiction' and accept the same syntactic role for it in the Citizenship Clause, but assign it different extensions. Krikorian/Cooper read it as complete, exclusive political allegiance (owing no allegiance to a foreign sovereign); Mayes/Newman read it as being present in U.S. territory and bound by / enforceable under U.S. law. See claim-graph.md."
  us_citizen(person) — "{0} is us_citizen" (strict fallback; declared: none) — "Recorded as a U.S. citizen under the Citizenship Clause reading at issue. Both sides accept the predicate; they dispute its extension for specific people because they dispute the extension of subject_to_jurisdiction."
Fluent variable letters: person = P
Fluent variable rule: Distinct sort letters exclude A/I/O and declared identifiers (case-insensitive). Choose the noun initial, then its unused consonants, then BCDEFGHJKLMNPQRSTUVWXYZ; on exhaustion use alphabetic codes BB, BC, ... . Within the naming scope, each sort's named binders use suffixes 1, 2, ... in preorder; omit 1. Constants have @; lexical words are lowercase.
Naming: per_statement — Allocate binders in preorder. Restart names in each statement.
Lint: none
for every person P such that (both P is born_in_us and P is subject_to_jurisdiction), P is us_citizen.
for every person P such that P is has_noncitizen_domiciled_parent, P is subject_to_jurisdiction.
```

No verbalisation templates were declared for the debate vocabulary (unlike
the constitution use case), so the fluent view uses the mechanical
`P is predicate_name` fallback throughout; `Lint: none` because there is
nothing to reject when nothing was declared.
