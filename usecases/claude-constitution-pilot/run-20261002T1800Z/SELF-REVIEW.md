# Translator's self-review of the units that changed this run

Not an independent audit; none of these bytes is counted as audit-verified. Each row was re-read against the source bytes after `build.py` and the checks.

| Unit | Source words | What the translation says | What it leaves out or narrows |
|---|---|---|---|
| `u0062.s01` | "Operators can give Claude a specific set of instructions, a persona, or information." | Reading set: permission (three rules: operators may give each kind, except inputs of the six limited kinds of `u0123.s03`) or ability (no content). | Who is an operator is not formalised. The exceptions follow the narrow reading of `u0123.s03`. `u0062.s02` stays UNFORMALISED. |
| `u0123.s01.p1` | "Operators are permitted to ask Claude to behave in certain ways that could seem dishonest … but that fall within Claude's honesty principles given the broader context" | Reading set: permission (one rule, same six exceptions) or ability. | The "since Anthropic maintains meta-transparency …" reason clause stays UNFORMALISED[causation]. Not sampled by the audit; changed only to carry the same scope. |
| `u0123.s02.p1` | "Operators can legitimately instruct Claude to role-play …, decline …, promote …, focus …, respond …" | Reading set of three: permission, conditional permission (legitimacy as a condition), ability (with the evaluative). Permission elaborated as five scoped rules. | ", and so on" stays UNFORMALISED (`other:open-list`). Candidates other than `permission` carry no content. "Legitimately" has no test (open term `instruction_is_legitimate`, decider unresolved). |
| `u0166.s04.p4` | "cannot be unlocked by any operator or user." | One checked ability statement: no operator and no user is able to unlock a hard constraint. No norm, no duty. | "Unlock" and "able" are open terms; "cannot" is carried by the predicate (no modality); "these" is the seven hard constraints only by a note (the sort is not tied to the rules). VE's wording of the relation is generic. |

**Whether anything was added that the source does not say.** No completion is chosen (every regulated predicate is `unspecified`); the permissions are not given a default for inputs outside the listed
kinds (VE: UNDECIDED); no priority between permissions and prohibitions is written, because with the exceptions none is needed (VE: CONFLICT-FREE). The exceptions assume the narrow scope of `u0123.s03`
(recorded). The ability reading of the operator sentences is recorded without content, so it asserts nothing.
What the translator did choose, and cites: that a permission and an adjacent limit are read as one scoped permission (the instruction of the 2026-10-02 audit), and that "cannot be unlocked" is an ability, not a duty (the same audit).
