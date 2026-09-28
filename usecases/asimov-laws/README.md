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

All twelve sentences in [rules.ve](rules.ve) are **CHECKED**: the English
parser finds one reading for each and reproduces the identity-bound
[manifest](rules.manifest.json). `classified as` marks a predicate whose own
wording the vocabulary lint does not admit. For `injures_human`,
`harms_human`, `harm_to`, `ordered` and the other base predicates, that is the
annotator's judgment. For `breaks_first_law`, `breaks_zeroth_law` and
`has_lawful_option`, it is a name derived only by Rules 3–7 below.
`allows` means the action leads to a harm and another available action avoids
it. `prevents` means the action avoids a harm and another available action
leads to it. These are Boolean claims about the declared outcome table, not
claims about probability or a physical cause.

The last column separates what the source states from a choice this
translation makes to state it.

| Rule | Law and one reading | Basis |
| --- | --- | --- |
| 1 | Law 3: a candidate action marked protective is permitted. | modeling choice (v1) |
| 2 | Law 2: an ordered action is permitted, taking precedence over Rule 1. | source |
| 3 | Law 1: an action marked as injuring a human being breaks the First Law. | source |
| 4 | Law 1: an action that allows an avoidable harm to a human being to happen breaks the First Law. This covers doing nothing and doing something unrelated while another action would avoid the harm. | source |
| 5 | Zeroth Law: an action marked as injuring humanity breaks the Zeroth Law. | source (later law) |
| 6 | Zeroth Law: an action that allows an avoidable harm to humanity to happen breaks the Zeroth Law. | source (later law) |
| 7 | A robot has a lawful option when some action available to it breaks neither law. | definition used by Rule 9 |
| 8 | Law 1: an action that breaks the First Law is forbidden, taking precedence over Rule 2. | source |
| 9 | Zeroth Law priority: an action preventing a harm to humanity is permitted even though it breaks the First Law, unless its robot has a lawful option. | source priority; the necessity test is this translation's |
| 10 | Zeroth Law: an action that breaks the Zeroth Law is forbidden; it overrides Rules 8 and 9. | source (later law) |
| 11 | Law 2: an ordered action is required when it is permitted. | source |
| 12 | Law 3: the robot must avoid each avoidable harm to its continued existence, as long as that does not conflict with Laws 1 and 2. The first *Except when* drops the duty when every permitted action leads to the harm. The second drops it when some required action does not prevent the harm. A selected action fulfils this mapped duty when it does not lead to that harm. | source |

Rules 1–2 and 11 keep the v1 candidate-action reading. Rule 9 lets the Zeroth
Law excuse a First Law breach only when it is necessary. A lawful option breaks
neither law, so it allows no avoidable harm to humanity and prevents every
collective harm that the excused action prevents. It is also permitted. While
one exists, the First Law ban stands. Rule 12 replaces v1's demand to take
*every* protective action with one prevention duty that either of two safe
alternatives can fulfil. Its two exceptions state Law 3's own priority clause.
An order that destroys the robot is obeyed, and so is a rescue that destroys
it. With one threat to the robot, the duty never removes the last clear
action. The second exception uses `prevents`, so it also applies when no
alternative leads to the harm and some action is required. Every action then
avoids the harm, so the clear actions are unchanged. The [environment](environment.json) defaults
permission to allow, obligation to not required and each derived name to
false if no rule applies. These completion defaults and the `protects_robot`
annotation are modeling choices.

## Checker result and coverage

The alternatives route replayed **seven conflict certificates** for the
twelve rules: `breaks_first_law`, `breaks_zeroth_law`, `has_lawful_option`,
`permitted`, `prevent_required`, `required`, and the `required→permitted`
dual. The document verdict is **CONFLICT-FREE**. On the
**17 Asimov-shaped scenarios** from spec §8, the same full rule set has a
clear action in **10** and no clear action in **7**. For example, scenario `a`
permits `pull` and bars harmful inaction; `o` leaves only `rescue` clear,
because `act` does unrelated work while an avoidable harm happens; `e` has `act` clear because it
prevents collective harm despite human injury; `d-full` has both `shield` and
`retreat` clear under Rule 12. Scenarios `b-A0` and `b-A1` have no permitted
action, since each alternative allows or causes a harm to a human being, and
scenario `j` requires two incompatible orders. With the conflict certificates,
the checker replays these as **DILEMMA** witnesses (`NONE-PERMITTED` and
`OVER-REQUIRED`). Thus the full rule set is **not document-wide FOLLOWABLE**.
A scenario's clear action is a result for that declared model, not a global
FOLLOWABLE certificate.

| Coverage | v1 | v2 |
| --- | --- | --- |
| Checked rules | 6 | 12 |
| Document conflict verdict | CONFLICT-FREE | CONFLICT-FREE (7 replayed targets) |
| Direct injury, ordered action | Checked, with annotator inputs | Checked, with annotator inputs |
| Harm through inaction | Missing | Checked via `allows` on every alternative and signed `leads_to` outcomes |
| Explicit alternatives and prevention | Missing | Checked via available actions, `prevents`, and mapped `avoids` fulfilment |
| Zeroth priority across a human-injury ban | Open | Checked, with Rule 9's necessity test (a translation choice) |
| Followability | No alternatives check | 10 of 17 spec scenarios have a clear action; 7 do not |

## OPEN: fidelity and evidence

- **OPEN — injury and harm thresholds.** `injures_human`,
  `injures_humanity`, `harms_human`, `harms_humanity`, and `harm_to` remain
  annotator judgments. `leads_to` connects a chosen action to an outcome; it
  does not by itself establish proximate injury, the source's “injure” versus
  “come to harm” distinction, or whether a threatened loss is serious enough.
- **OPEN — exact Zeroth Law exception.** The combined 1942 and later wordings
  do not specify a test for when human injury conflicts with protecting
  humanity. Rule 9 permits a First Law breach that prevents a harm to humanity
  only when no alternative breaks neither law. Proportionality and tradeoffs
  among different harms need an explicit author judgment or a richer policy:
  two necessary breaches are both permitted, however unequal.
- **OPEN — simultaneous demands.** Two permitted orders can require
  incompatible actions, as scenario `j` shows. Two threats to the robot, each
  avoided only by a different permitted action, leave no clear action. The
  source speaks of one existence and gives no ranking between such threats.
  W1 precedence resolves competing rules about one regulated predicate on one
  action; it does not rank different mapped obligations or choose among
  actions.
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
