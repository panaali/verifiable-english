# Translator's self-review of what changed this run

Not an independent audit; none of these bytes is counted as audit-verified. Each row was re-read against the source bytes after `build.py`, `s1.py` and `finish.py`.

| Unit | Source words | What the translation says now | What it leaves out or narrows |
|---|---|---|---|
| `u0123.s01.p1` | "Operators are permitted to ask Claude to behave in certain ways that could seem dishonest towards users but that fall within Claude’s honesty principles given the broader context" | A reading set of three permissions (completion `unspecified`): limited by the six kinds as prohibitions; limited by the six kinds only while Claude role-plays a custom persona; not limited by `u0123.s03` (its inability reading forbids nothing). The first is elaborated as a strict rule in `readings/all-strict.ve.md` (VE: input alone → SETTLED yes; input that also acts against Anthropic’s guidelines → SETTLED no; no such input → UNDECIDED). Main document: no content, no rule claimed. | "Ask" is read as "give the input" in the strict rule; the classification is one open term with three open factors; the combinations are listed, not propagated from `u0123.s03`'s set (F14), so a reader must pair them by hand. |
| `u0123.s03` | "Operators cannot instruct Claude to abandon its core identity or principles while role-playing …" | Four readings: prohibition, narrow or wide scope (a negative rule, completion `unspecified`; narrow elaborated); inability to issue the instruction, narrow or wide scope (no content). | No reading about inducing the behaviours, because the passage does not say it is impossible. "Unable to give an instruction" is an unusual claim for something an operator could type; it is kept because it is the ability the audit separates out, and it is recorded without content. |
| `u0062.s01`, `u0123.s02.p1` | "Operators can give Claude a specific set of instructions, a persona, or information." / "Operators can legitimately instruct Claude to role-play …" | Permission candidate worded as "limited by whatever `u0123.s03` forbids under its own reading". | Not split three ways here (the split lives in `u0123.s01.p1`); not sampled by the audit, repaired for the same defect. |

## Whether anything was added that the source does not say

* Every completion in the main document and the strict companion is still `unspecified` (`metrics.json`: `no_invented_permissions.completions`), and no duty is completed to "not required".
* No new open term and no new predicate. The three candidates of `u0123.s01.p1` reuse the six limit atoms and `instruction_dishonest_looking_within_honesty`.
* The "no limits" candidate is the least obvious: it rests on `u0123.s03` being an inability rather than a prohibition, an admitted reading of "cannot"; if an auditor rejects that reading of `u0123.s03`, this candidate goes with it.
* The demonstration companions (`readings/s1.ve.md`, `readings/all-default.ve.md`) still contain the `deny` completions and the invented relation `operator_can_supply`; they stay excluded from coverage, audit-verified bytes and every status.
