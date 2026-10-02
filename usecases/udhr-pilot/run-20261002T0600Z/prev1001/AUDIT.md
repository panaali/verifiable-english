**Faithful: 16/20.** This was a read-only audit with no model calls. The source hash matches the manifest, and all 130 unit spans match the source. The score describes a stratified sample, not a corpus-wide estimate.

Using Python `Random("20261001T1800Z")`, I took the sole CHECKED unit (**u074**), the sole OPEN unit (**u111**), then sampled 14 sorted READINGS IDs (**u077, u033a, u051, u022a, u032, u112, u022c, u063, u049, u046, u035, u033b, u029, u039**) and four sorted LABELLED IDs (**u104, u069, u090, u109**).

**Unfaithful units:**

- **u051, Article 14:** The positive candidates require every bearer to *grant* asylum to every person. The source grants a right to seek and enjoy asylum from persecution; those candidates also omit seeking.
- **u035, Article 8:** The checked duty has no argument for the rights-violating act. Its prose holder description cannot ensure an effective remedy for each qualifying violation.
- **u039, Article 10:** “In full equality” is an unattached open term. The checked duty also has no determination or charge argument, so one hearing can stand for distinct cases.
- **u077, Article 21(2):** “In their own country” now appears in the act phrase, but no checked relation connects a bearer to the holder’s country. The candidates still bind unrelated bearers.

**Highest-value language features:**

1. Strict and defeasible alternatives in one reading set: currently blocks **43 units, 4,175 bytes**.
2. Structured right lines with checked act and case scope, plus bearer–holder relations, to preserve conditions now left in prose.
3. Per-choice rights elaboration, so exceptions, Article 29 limitations, and “this right includes” clauses attach to the chosen right.

I could not write `AUDIT.md`: the requested directory is outside the permitted writable roots.