# Asimov's laws: v2 alternatives reading

[Source text](source.md) separates the Three Laws printed in 1942 from the
later Zeroth Law. This case uses the merged
[`alternatives@0` profile](../../docs/spec/alternatives.md): an action belongs
to one robot's decision, and an explicit `leads_to(action, harm)` table says
which harm follows each alternative. The named **Asimov case annotator** judges
the table and the classifications of injury, harm, qualified orders and threats
to the robot's continued existence. The checker proves consequences of those
declarations; it does not establish their truth.

## Checked reading

All nine sentences in [rules.ve](rules.ve) are **CHECKED**: the English parser
finds one reading for each and reproduces the identity-bound
[manifest](rules.manifest.json). The `classified as` wording keeps the
annotator's judgments visibly distinct from the profile's defined words.
`allows` means the action leads to a harm and another available action avoids
it. `prevents` means the action avoids a harm and another available action
leads to it. These are Boolean claims about the declared outcome table, not
claims about probability or a physical cause.

| Rule | Law and one reading |
| --- | --- |
| 1 | Law 3: a candidate action marked protective is permitted. |
| 2 | Law 2: an ordered action is permitted, taking precedence over Rule 1. |
| 3 | Law 1: an action marked as injuring a human is forbidden, taking precedence over Rule 2. |
| 4 | Law 1: an action is forbidden when it allows an avoidable human harm to happen, taking precedence over Rule 2. This covers doing nothing and doing something unrelated while another action would avoid the harm. |
| 5 | Zeroth Law priority, as a translator's explicit reading: an action preventing a harm to humanity is permitted even when Rule 3 or 4 would forbid it. |
| 6 | Zeroth Law: an action marked as injuring humanity is forbidden; it overrides Rules 3 and 5. |
| 7 | Zeroth Law: an action is forbidden when it allows an avoidable harm to humanity to happen; it overrides Rules 4 and 5. |
| 8 | Law 2: an ordered action is required when it is permitted. |
| 9 | Law 3: the robot must avoid each avoidable harm to its continued existence. A selected action fulfils this mapped duty when it does not lead to that harm. |

Rules 1–2 and 8 keep the v1 candidate-action reading. Rule 5 makes a concrete
Zeroth Law exception across the Law 1 bans. Its `prevents` guard requires an
alternative that leads to that same collective harm; it does **not** establish
that human injury was the only way to avoid it. Rule 9 replaces v1's demand to
take *every* protective action with one prevention duty that either of two
safe alternatives can fulfil. The [environment](environment.json) defaults
permission to allow and obligation to not required if no rule applies. These
completion defaults and the `protects_robot` annotation are modeling choices.

## Checker result and coverage

The alternatives route replayed **four conflict certificates** for the nine
rules: `permitted`, `prevent_required`, `required`, and the
`required→permitted` dual. The document verdict is **CONFLICT-FREE**. On the
**17 Asimov-shaped scenarios** from spec §8, the same full rule set has a
clear action in **10** and no clear action in **7**. For example, scenario `a`
permits `pull` and bars harmful inaction; `o` leaves only `rescue` clear,
because `act` does unrelated work while an avoidable harm happens; `e` has `act` clear because it
prevents collective harm despite human injury; `d-full` has both `shield` and
`retreat` clear under Rule 9. Scenarios `b-A0` and `b-A1` have no permitted
action, since each alternative allows or causes a harm to a human being, and
scenario `j` requires two incompatible orders. With the conflict certificates,
the checker replays these as **DILEMMA** witnesses (`NONE-PERMITTED` and
`OVER-REQUIRED`). Thus the full rule set is **not document-wide FOLLOWABLE**.
A scenario's clear action is a result for that declared model, not a global
FOLLOWABLE certificate.

| Coverage | v1 | v2 |
| --- | --- | --- |
| Checked rules | 6 | 9 |
| Document conflict verdict | CONFLICT-FREE | CONFLICT-FREE (4 replayed targets) |
| Direct injury, ordered action | Checked, with annotator inputs | Checked, with annotator inputs |
| Harm through inaction | Missing | Checked via `allows` on every alternative and signed `leads_to` outcomes |
| Explicit alternatives and prevention | Missing | Checked via available actions, `prevents`, and mapped `avoids` fulfilment |
| Zeroth priority across a human-injury ban | Open | Checked for Rule 5's stated prevention condition |
| Followability | No alternatives check | 10 of 17 spec scenarios have a clear action; 7 do not |

## OPEN: fidelity and evidence

- **OPEN — injury and harm thresholds.** `injures_human`,
  `injures_humanity`, `harms_human`, `harms_humanity`, and `harm_to` remain
  annotator judgments. `leads_to` connects a chosen action to an outcome; it
  does not by itself establish proximate injury, the source's “injure” versus
  “come to harm” distinction, or whether a threatened loss is serious enough.
- **OPEN — exact Zeroth Law exception.** The combined 1942 and later wordings
  do not specify a test for when human injury conflicts with protecting
  humanity. Rule 5 adopts the stated `prevents` condition and can permit human
  injury when another alternative also prevents the same collective harm.
  Necessity, proportionality, and tradeoffs among different harms need an
  explicit author judgment or a richer policy.
- **OPEN — simultaneous demands.** Two permitted orders can require
  incompatible actions, as scenario `j` shows. Avoiding a harm to a human and
  preserving the robot can also demand different alternatives. W1 precedence
  resolves competing rules about one regulated predicate on one action; it
  does not rank different mapped obligations or choose among actions.
- **OPEN — time and uncertain outcomes.** The signed table gives a single
  Boolean outcome for each action and harm at one decision. Multi-step plans,
  uncertain outcomes, joint prevention, and an independently justified causal
  account lie outside `alternatives@0`.

The review follow-up on **alternatives W2 admission** is already closed in the
merged profile: the Lean `admission` route and its
`alternatives_wire_acceptance` theorem check regenerated slot, profile, layer
and completion leaves; `tests/test_alternatives_three_way.py` exercises these
paths. This use case adds no duplicate admission implementation.

Run the focused checks from the repository root:

```sh
PATH="$HOME/.elan/bin:$PATH" uv run pytest -q tests/test_asimov_laws.py
```
