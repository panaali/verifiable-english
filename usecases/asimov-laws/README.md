# Asimov's laws: a checked action reading

[Source text](source.md) quotes the Three Laws from Isaac Asimov's 1942
“Runaround” and the later Zeroth Law. In brief: **0** bars injuring humanity;
**1** bars injuring a human; **2** requires following qualified human orders unless a higher
law conflicts; **3** requires self preservation unless a higher law conflicts.
Laws 0 and 1 also address harm *through inaction*; that part is outside this
checked reading. The 1942 wording of Law 1 says “under any conditions”; adding
the later Zeroth Law requires a revised priority reading, which this example
does not settle.

## Authoring VE

These are the checked rules in [rules.ve](rules.ve). An `action` is one proposed
act by one robot. Rule numbers are display order; [the manifest](rules.manifest.json)
preserves their stable names. The permission rules form the W1 precedence
chain **0 > 1 > 2 > 3** (Rules 4 > 3 > 2 > 1). Rule 5 and Rule 6 require an
action only when it is permitted. Rule 6 is an illustrative assumption: it
requires every permitted protective action, while the source requires the robot
to preserve its existence without requiring every available means.

```text
Rule 1. Every action may be performed, if that action is protective.
Rule 2 (exception to rule 1). Every action may be performed, if that action is ordered.
Rule 3 (exception to rule 2). Every action must not be performed, if that action is classified as "injures_human".
Rule 4 (exception to rule 3). Every action must not be performed, if that action is classified as "injures_humanity".
Rule 5. Every action must be performed, if both that action is ordered and that action may be performed.
Rule 6. Every action must be performed, if both that action is protective and that action may be performed.
```

The natural English reading of each checked rule is:

| Rule | Reading |
| --- | --- |
| 1 (Law 3) | A protective candidate action is permitted. |
| 2 (Law 2) | An ordered candidate action is permitted, taking precedence over Rule 1. |
| 3 (Law 1) | An action judged to injure a human is forbidden, taking precedence over Rule 2. |
| 4 (Law 0) | An action judged to injure humanity is forbidden, taking precedence over Rule 3. |
| 5 (Law 2) | An ordered action is required if it is permitted. |
| 6 (Law 3, illustrative assumption) | Every protective action is required if it is permitted. |

The [environment](environment.json) sets completion defaults for candidate
actions: when no permission rule applies, **permission defaults to allow**;
when no obligation rule applies, **obligation defaults to not required**. These
are modeling choices, not claims from Asimov's text. For example, an action
with no `ordered`, `protects_robot`, or injury annotation is permitted but not
required.

## Boundary and result

- **Checked:** W1 parses the six rules and checks their precedence, outcomes,
  and permission/obligation dual. The W1 conflict check returns
  **CONFLICT-FREE** with a replayed certificate for this rule document. For a
  qualified human order to perform an action marked `injures_human`, the action is neither
  permitted nor required. Without Rule 3's precedence over Rule 2, that same
  situation gives a **CONFLICT** witness: Rule 2 permits and Rule 3 forbids.
- **Open:** `injures_human` and `injures_humanity` are judgments by the named
  **Asimov case annotator**, a human assigned to each scenario. No injury or
  harm threshold is invented. The annotator also supplies `ordered` and
  `protects_robot`. A conflict certificate proves consistency for *any* such
  assignments; it does not prove the assignments true.
- **UNFORMALISED:** “Through inaction, allow ... to come to harm” needs a
  causal account of what the robot could have prevented. W1 has no such
  account. The difference between *injure* and *come to harm* also remains
  open. The checked direct injury bans are not counted as a faithful rendering
  of the inaction clauses.
- **UNFORMALISED:** The source's Law 3 preservation obligation concerns keeping
  the robot in existence. Rule 6 does not faithfully express that obligation:
  it requires *each* permitted protective action, even when two compatible
  alternatives are available and either one would suffice. Both actions can be
  required while the W1 conflict check still returns **CONFLICT-FREE**.
- **UNFORMALISED:** Competing *different* actions, such as obeying an order
  versus saving the robot, are not compared. W1 precedence is per regulated
  predicate and per candidate action. Rules 5 and 6 can both require different
  actions; the permission chain does not resolve that choice. Likewise, the
  Zeroth Law's possible tradeoff between one human and humanity is not decided.

Closing these gaps needs explicit actions and alternatives, temporal and
counterfactual causation for preventable harm, and priority across obligations
for different actions. The case annotator would still have to justify the
open injury judgments.

Run the focused checks from the repository root:

```sh
PATH="$HOME/.elan/bin:$PATH" uv run pytest -q tests/test_asimov_laws.py
```
