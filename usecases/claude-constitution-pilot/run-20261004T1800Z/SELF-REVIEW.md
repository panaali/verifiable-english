# Translator's self-review of what changed this run

Not an independent audit; none of these bytes is counted as audit-verified. Each row was re-read against the source bytes after `build.py`, `s1.py` and `finish.py`.

| Unit | Source words | What the translation says now | What it leaves out or narrows |
|---|---|---|---|
| `u0123.s01.p1` | "Operators are permitted to ask Claude to behave in certain ways that could seem dishonest towards users but that fall within Claude’s honesty principles given the broader context" | One rule (completion `unspecified`): every operator may give Claude each operator input classified as "an instruction to behave in a way that could seem dishonest but falls within the honesty principles", except when it is one of the six kinds `u0123.s03` forbids. VE: the input alone → SETTLED yes; the input that also acts against Anthropic’s guidelines → SETTLED no; no such input → UNDECIDED. | "Ask" is read as "give the input" (the operator-input sort of `u0062.s01`); the classification is one open term with three open factors (what could seem dishonest, what falls within the honesty principles, what the broader context is). The limits of `u0123.s03` are read in their narrow scope. Nothing says what holds where the text is silent. |
| `u0062.s01` | "Operators can give Claude a specific set of instructions, a persona, or information." | Reading set of two: the scoped permission (three rules, elaborated in the strict companion) and the ability to give those inputs. | The ability candidate carries no content (no rule can state it beside `norm-defaults@0`); it says supply, not induce, as the audit asks. |
| `u0123.s02.p1` | "Operators can legitimately instruct Claude to role-play …" | Reading set of three; the ability candidate now says "able to instruct", plus the evaluative "legitimately" as an open term. | Same: no content for the ability or conditional-permission candidates. Not sampled by the audit, repaired for the same defect. |

## Whether anything was added that the source does not say

* In the main document and the strict companion every completion is still `unspecified` (`metrics.json`: `no_invented_permissions.completions`), and no duty is completed to "not required".
* No new open term, no new predicate: `u0123.s01.p1` reuses the open term `instruction_dishonest_looking_within_honesty` and the six limit atoms it already had in the strict companion.
* The demonstration companions (`readings/s1.ve.md`, `readings/all-default.ve.md`) still contain the `deny` completions and the invented relation `operator_can_supply`; they are excluded from coverage, from audit-verified bytes and from every unit's status. In `s1.ve.md`, `u0123.s01.p1` now carries no content (the soft chain cannot state the main document's rule).
