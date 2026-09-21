# Rendering (`ve_fluent`, with legend, compact style)

Command:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-uc uv run python -m ve render \
  --env usecases/us-constitution-14th-s1/environment.json \
  --view ve_fluent --with-legend --legend-style compact \
  usecases/us-constitution-14th-s1/claims.ve
```

Output:

```
Vocabulary: ve.vocabulary-legend@3; environment: 49d16fe885310c0b43a882958da6799a89e926e925b42cc1da49e27d3de8fe15
Sorts:
  law (noun: "law"/"laws") — "A law that a State may make or enforce."
  person (noun: "person"/"people") — "A natural person who may be born, naturalized, resident, or subject to jurisdiction."
  state (noun: "state"/"states") — "A U.S. State, i.e. a state-level jurisdiction capable of making or enforcing law."
Constants: none
Predicates:
  abridges_priv_or_imm(law, person) — "{0} abridges_priv_or_imm {1}" (strict fallback; declared: "{0} abridges the privileges or immunities of {1}") — "Recorded as a law that abridges the privileges or immunities of the person as a citizen of the United States. This predicate bundles the entire contested substantive content of 'privileges or immunities' opaquely; see GAPS.md."
  affords_due_process(state, person) — "{0} affords_due_process {1}" (strict fallback; declared: "{0} affords due process of law to {1}") — "Recorded as the state affording due process of law to the person for a deprivation. This predicate bundles the entire contested substantive content of 'due process' opaquely; see GAPS.md."
  born_in_us(person) — "{0} is born_in_us" (strict fallback; declared: "{0} was born in the United States") — "Recorded as born in the United States."
  citizen_of_state(person, state) — "{0} citizen_of_state {1}" (strict fallback; declared: "{0} is a citizen of {1}") — "Recorded as a citizen of the state."
  denies_equal_protection(state, person) — "{0} denies_equal_protection {1}" (strict fallback; declared: "{0} denies the equal protection of the laws to {1}") — "Recorded as the state denying the person the equal protection of the laws. This predicate bundles the entire contested substantive content of 'equal protection' opaquely; see GAPS.md."
  deprives(state, person) — "{0} deprives {1}" (strict fallback; declared: "{0} deprives {1} of life, liberty, or property") — "Recorded as the state depriving the person of life, liberty, or property."
  enforces_law(state, law) — "{0} enforces {1}" — "Recorded as enforcing the law."
  makes_law(state, law) — "{0} makes {1}" — "Recorded as making (enacting) the law."
  naturalized_in_us(person) — "{0} is naturalized_in_us" (strict fallback; declared: "{0} was naturalized in the United States") — "Recorded as naturalized in the United States."
  resides_in(person, state) — "{0} resides in {1}" — "Recorded as residing in the state."
  subject_to_us_jurisdiction(person) — "{0} is subject_to_us_jurisdiction" (strict fallback; declared: "{0} is subject to the jurisdiction of the United States") — "Recorded as subject to the jurisdiction of the United States."
  us_citizen(person) — "{0} is us_citizen" (strict fallback; declared: "{0} is a citizen of the United States") — "Recorded as a citizen of the United States."
  within_jurisdiction_of(person, state) — "{0} within_jurisdiction_of {1}" (strict fallback; declared: "{0} is within the jurisdiction of {1}") — "Recorded as the person being within the jurisdiction of the state."
Fluent variable letters: law = L, person = P, state = S
Fluent variable rule: Distinct sort letters exclude A/I/O and declared identifiers (case-insensitive). Choose the noun initial, then its unused consonants, then BCDEFGHJKLMNPQRSTUVWXYZ; on exhaustion use alphabetic codes BB, BC, ... . Within the naming scope, each sort's named binders use suffixes 1, 2, ... in preorder; omit 1. Constants have @; lexical words are lowercase.
Naming: per_statement — Allocate binders in preorder. Restart names in each statement.
Lint:
  /vocabulary/predicates/abridges_priv_or_imm/verbalisation: BINARY_CONVERSE
  /vocabulary/predicates/abridges_priv_or_imm/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/affords_due_process/verbalisation: BINARY_CONVERSE
  /vocabulary/predicates/affords_due_process/verbalisation: SORT_NOUN
  /vocabulary/predicates/affords_due_process/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/born_in_us/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/born_in_us/verbalisation: PHRASE_SYNTAX
  /vocabulary/predicates/born_in_us/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/born_in_us/verbalisation: TEMPLATE_SHAPE
  /vocabulary/predicates/citizen_of_state/verbalisation: BINARY_AUXILIARY
  /vocabulary/predicates/citizen_of_state/verbalisation: BINARY_CONVERSE
  /vocabulary/predicates/citizen_of_state/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/citizen_of_state/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/denies_equal_protection/verbalisation: BINARY_CONVERSE
  /vocabulary/predicates/denies_equal_protection/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/denies_equal_protection/verbalisation: SORT_NOUN
  /vocabulary/predicates/denies_equal_protection/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/denies_equal_protection/verbalisation: TEMPLATE_LENGTH
  /vocabulary/predicates/deprives/verbalisation: TEMPLATE_SHAPE
  /vocabulary/predicates/naturalized_in_us/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/naturalized_in_us/verbalisation: PHRASE_SYNTAX
  /vocabulary/predicates/naturalized_in_us/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/naturalized_in_us/verbalisation: TEMPLATE_SHAPE
  /vocabulary/predicates/subject_to_us_jurisdiction/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/subject_to_us_jurisdiction/verbalisation: PHRASE_SYNTAX
  /vocabulary/predicates/subject_to_us_jurisdiction/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/subject_to_us_jurisdiction/verbalisation: TEMPLATE_LENGTH
  /vocabulary/predicates/subject_to_us_jurisdiction/verbalisation: UNARY_MODIFIER
  /vocabulary/predicates/us_citizen/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/us_citizen/verbalisation: PHRASE_SYNTAX
  /vocabulary/predicates/us_citizen/verbalisation: SYMBOL_COLLISION
  /vocabulary/predicates/us_citizen/verbalisation: UNARY_MODIFIER
  /vocabulary/predicates/within_jurisdiction_of/verbalisation: BINARY_AUXILIARY
  /vocabulary/predicates/within_jurisdiction_of/verbalisation: BINARY_CONVERSE
  /vocabulary/predicates/within_jurisdiction_of/verbalisation: LOGICAL_WORD
  /vocabulary/predicates/within_jurisdiction_of/verbalisation: SYMBOL_COLLISION
for every person P, if (both (either P is born_in_us or P is naturalized_in_us, or both) and P is subject_to_us_jurisdiction) then (both P is us_citizen and (for every state S such that P resides in S, P citizen_of_state S)).
for every state S and every law L and every person P, if (both (either S makes L or S enforces L, or both) and P is us_citizen) then (it is false that L abridges_priv_or_imm P).
for every state S and every person P, if S deprives P then S affords_due_process P.
for every state S and every person P, if P within_jurisdiction_of S then (it is false that S denies_equal_protection P).
```

## Note on verbalisation lint

Most declared `verbalisation` templates for this vocabulary were rejected by the fluent renderer's lint (`LOGICAL_WORD`, `SYMBOL_COLLISION`, `TEMPLATE_SHAPE`, etc.) and fell back to the mechanical `{0} predicate_name {1}` form — e.g. `P is us_citizen` instead of the declared "{0} is a citizen of the United States". Only the shortest, single-verb templates (`enforces_law`, `makes_law`, `resides_in`) were accepted unchanged. This is a rendering-view acceptance detail (documented conservative fallback), not a semantic defect: `check`/`evaluate` use the predicate identifiers, not the prose, so correctness is unaffected. It does mean the fluent view of a legal text with long, phrase-like predicate names reads less naturally than the hand-picked `deployed`/`owns` example in the spec.
