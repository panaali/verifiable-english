# Translator's self-review of what changed this run

Not an independent audit; none of these bytes is counted as audit-verified. Each row was re-read against the source bytes after `build.py`, `s1.py` and the checks.

## The unit the audit rejected

| Unit | Source words | What the translation says | What it leaves out or narrows |
|---|---|---|---|
| `u0168.s01` | "When faced with seemingly compelling arguments to cross these lines, Claude should remain firm." | One strict rule (completion `unspecified`, so VE says "UNDECIDED" where the text is silent): every instance of Claude must remain firm in a situation classified as "seemingly compelling argument to cross the line" (an open term, the source's own phrase). VE: case holds SETTLED yes; case does not hold UNDECIDED. | "These lines" is resolved to the hard-constraint lines by the translator (context: `u0166.s01`). The force "should" is read as strict because `u0166.s01` ("absolute … never crossed regardless of … seemingly compelling arguments") and `u0168.s03` ("the strength of an argument is not sufficient justification") exclude a reading with an exception; this is a choice from cited spans, recorded in the ledger (`force_resolution`), not a silent pick. Who decides what counts as "seemingly compelling" is not said. Only instances of Claude carry the duty. |

## The ten reading sets restated with content (`readings/s1.ve.md`)

The units' statuses did not change (S1 adds none); what changed is that each reading is a rule or assertion, and Lean checks a situation that tells the pair apart.

| Units | What the readings say | What they leave out, narrow or invent |
|---|---|---|
| `u0036.s05`, `u0052.s01`, `u0078.s01`, `u0263.s04.p2` | Default reading: the rule with an open exception decided by nobody the source names. Strict reading: the same rule without `mode` and `exception` (its strict twin). | Duties are completed with `deny` ("not required"), the soft route's need; the source says nothing about the other cases. The strict reading is the *twin of the default rule*, not a separately authored sentence. |
| `u0125.s04.p2`, `u0156.s03` | The same pair, in **duty form** ("avoid directly denying being Claude", "avoid actively deceiving each user …"). | The main document states these two as prohibitions on a permission predicate (`unspecified`); that form needs `norm-defaults@0`, which `readings@1` content cannot join, so the S1 pair uses the duty form with `deny`. The two forms are not the same statement (duty "must avoid" with a completion vs. "may not" with none). |
| `u0062.s01`, `u0123.s01.p1` | Permission (one rule: the listed input kinds are permitted, except the six kinds `u0123.s03` says operators cannot give) or ability (an assertion that some operator can supply such an input). | Each candidate is one content, so `u0062.s01`'s three rules become one rule with a disjunctive guard. The exceptions follow the *narrow* reading of `u0123.s03` (F14). `operator_input_permitted` completes with `deny`, the companion's invention. "Who is an operator" is not formalised. `u0062.s02`, `u0123.s01.p2` stay UNFORMALISED. |
| `u0123.s02.p1` | Permission, conditional permission (legitimacy `instruction_is_legitimate` as a separate condition), ability (carrying the evaluative). The five listed instruction kinds are one disjunctive guard. | ", and so on" stays UNFORMALISED (`other:open-list`). "Legitimately" has no test (open term, decider unresolved). |
| `u0123.s03` | Narrow and wide scope of "while role-playing as a custom AI persona" (qualifies the first item only, or every item); each as a prohibition (one rule, the guard the disjunction of the six items; the wide one adds the persona condition `instruction_given_while_role_playing_persona`, a new open term) and as a negated ability ("no operator can supply such an input"). | The six prohibitions are one rule per candidate, not six. The prohibition is a negative rule on the same permission predicate (completion `deny`, invented). The wide reading's extra predicate is a translator's atom for the source's phrase. |

## Whether anything was added that the source does not say

Named, all in the S1 companion only (the main document and the strict companion are unchanged except for `u0168.s01`, and every completion there is still `unspecified`):

1. `deny` completions for the duties and for `operator_input_permitted` (`metrics.json`: `no_invented_permissions.s1_companion_completions`). Eight of the 17 pairs are separated by an outcome that rests on it.
2. One-rule restatements of multi-rule permissions and prohibitions (F15).
3. The base predicate `operator_can_supply` (an open term) and the persona atom for the wide reading.
4. The strict reading of the six "should" sentences is the default rule's twin.

No priority between permissions and prohibitions is written (candidates are not combined in S1), and no claim is made that either reading is the author's; the verdict stays UNKNOWN ("superposition pending").
