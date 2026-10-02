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

All thirteen sentences in [rules.ve](rules.ve) are **CHECKED**: the English
parser finds one reading for each and reproduces the identity-bound
[manifest](rules.manifest.json). The text uses no parser listing
scaffolding (`first clause: … end first clause`), and a test rejects it.
`classified as` and `has the recorded relation` mark a predicate whose own
wording the vocabulary lint does not admit. For `injures_human`,
`harms_human`, `harm_to`, `ordered` and the other base predicates, that is the
annotator's judgment. For `breaks_first_law`, `breaks_zeroth_law`,
`has_lawful_option` and `lawfully_avoidable_threat`, it is a name derived only
by Rules 3–7 and 12 below.
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
| 12 | A harm to the robot is a lawfully avoidable threat when some permitted action avoids it. | definition used by Rule 13 |
| 13 | Law 3: the robot must avoid each lawfully avoidable threat to its continued existence, as long as that does not conflict with Laws 1 and 2. The first *Except when* drops the duty when some required action does not prevent the harm. The second drops every such duty when each permitted action leads to one of these threats, so that no permitted action protects the robot from all of them. A selected action fulfils this mapped duty when it does not lead to that harm. | source priority; yielding jointly is this translation's |

Rules 1–2 and 11 keep the v1 candidate-action reading. Rule 9 lets the Zeroth
Law excuse a First Law breach only when it is necessary. A lawful option breaks
neither law, so it allows no avoidable harm to humanity and prevents every
collective harm that the excused action prevents. It is also permitted. While
one exists, the First Law ban stands. Rule 13 replaces v1's demand to take
*every* protective action with one prevention duty per threat that any safe
alternative can fulfil. Rule 12 and Rule 13's two exceptions state Law 3's own
priority clause. An order that destroys the robot is obeyed, and so is a
rescue that destroys it. Law 3 protects one existence, so it yields to Laws 1
and 2 for all threats together, not threat by threat. If one rescue destroys
the robot by fire and the only other by water, both rescues are clear, as
they are when the two deaths are recorded as one outcome. A threat that every
permitted action meets does not release the robot from another threat that
some permitted action avoids. The tests check, on sampled models with two
threats to the robot, that the duty never removes the last clear action; this
is not a certificate. The first exception uses `prevents`, so it also applies
when no alternative leads to the harm and some action is required. Every
action then avoids the harm, so the clear actions are unchanged. The
[environment](environment.json) defaults permission to allow, obligation to
not required and each derived name to false if no rule applies. These completion defaults and the `protects_robot`
annotation are modeling choices.

## Checker result and coverage

The alternatives route replayed **eight conflict certificates** for the
thirteen rules: `breaks_first_law`, `breaks_zeroth_law`, `has_lawful_option`,
`lawfully_avoidable_threat`, `permitted`, `prevent_required`, `required`, and
the `required→permitted` dual. The document verdict is **CONFLICT-FREE**.

The spec §8 fixtures give **17 Asimov-shaped entries**, but they are not 17
independent scenarios. Each entry pairs a model with its own rule set; this
case replaces every rule set with the full Asimov document. Entries that
differed only in their rule set then collapse: `b-A0`, `b-A2` and `b-B` share
one model, as do `b-A1` and `bprime-A`; `c-7`, `c-8` and `c-8m`; `o-7` and `o-8`;
`d-full` and `d-prevention`; and `j` and `bprime-A5`. That leaves **nine distinct
models**. The full rule set has a clear action in **six** of them (`a`, `c`,
`o`, `d`, `e`, `l5`) and none in **three** (`b-A0`, `b-A1`, `j`). Counting
entries would give 10 of 17 and would count the same model up to three
times. For example, scenario `a` permits `pull` and bars harmful inaction;
`o` leaves only `rescue` clear, because `act` does unrelated work while an
avoidable harm happens; `e` has `act` clear because it prevents collective
harm and the robot has no lawful option, so the injury is necessary;
`d-full` has both `shield` and `retreat` clear under Rule 13. In `b-A0` and
`b-A1` every alternative allows or causes a harm to a human being, so no
action is permitted. Scenario `j` requires two incompatible orders. With the
conflict certificates, the checker replays these as **DILEMMA** witnesses
(`NONE-PERMITTED` and `OVER-REQUIRED`). Thus the full rule set is **not
document-wide FOLLOWABLE**. A scenario's clear action is a result for that
declared model, not a global FOLLOWABLE certificate.

Twenty-two review regressions add named models for the four repaired
readings, each checked against an independent Python reading of the source.
The same reading must match Lean's scenario report on 24 sampled models. On
300 more, it must agree with Python's and Rust's evaluation of Lean's
followability formula. On that sample a Law 3 that yields only threat by
threat, or not at all, leaves some model without a clear action that the full
rule set has; with the fire and water rescues, Lean replays the threat-by-threat
reading as a **DILEMMA** (`JOINTLY-UNDISCHARGEABLE`).

| Coverage | v1 | v2 |
| --- | --- | --- |
| Checked rules | 6 | 13 |
| Document conflict verdict | CONFLICT-FREE | CONFLICT-FREE (8 replayed targets) |
| Direct injury, ordered action | Checked, with annotator inputs | Checked, with annotator inputs |
| Harm through inaction | Missing | Checked via `allows` on every alternative and signed `leads_to` outcomes |
| Explicit alternatives and prevention | Missing | Checked via available actions, `prevents`, and mapped `avoids` fulfilment |
| Zeroth priority across a human-injury ban | Open | Checked, with Rule 9's necessity test (a translation choice) |
| Law 3 yields to Laws 1 and 2 | Partial: yields to Law 1 only | Checked via Rule 12 and Rule 13's two exceptions, jointly across threats |
| Followability | No alternatives check | 6 of 9 distinct spec models (17 entries) have a clear action; 3 do not |

## The completion defaults and `unspecified`

The environment completes `permitted` to allow, `required` and `prevent_required` to not required, and each
derived name (`breaks_first_law`, `breaks_zeroth_law`, `has_lawful_option`, `lawfully_avoidable_threat`) to false.
**The allow is not in the source.** Asimov's laws forbid and require; they never say that whatever they leave open
is permitted. Since `norm-defaults@0` merged, VE has a completion that says exactly that: `unspecified`, "the
text does not say". This case should use it for `permitted`, and it does not yet:

| | Before `norm-defaults@0` | Now |
|---|---|---|
| `permitted` | allow (a modeling choice) | **allow, unchanged** (a modeling choice; `unspecified` is blocked, below) |
| `required`, `prevent_required` | not required unless a rule requires | unchanged |
| derived names | false unless a rule derives them | unchanged: each is this translation's own definition, so false-unless-derived is part of the definition, not a claim about the source |
| verdicts | CONFLICT-FREE; 6 of 9 distinct spec models have a clear action | **unchanged** |

**Why it is not switched.** Every verdict here (FOLLOWABLE, DILEMMA, the clear actions) comes from
`alternatives@0`, and `norm-defaults@0` does not combine with it yet (docs/spec/norm-defaults.md 3.3,
"Integration gap"): the alternatives route still consumes completed allow/deny norms and cannot classify a
permission the text leaves open. Both engines reject the switched environment: Python with `UnsupportedProfile:
alternatives@0 with norm-defaults@0 is not implemented`, and Lean's alternatives route with `UnsupportedProfile:
Unsupported profile norm-defaults@0` (a test checks both). Rust decodes no `alternatives@0` environment; it
evaluates the base formulas Lean produces, so it has no separate leg. The spec forbids reporting a two-valued
decision for a silent permission, so the case keeps allow rather than pretend.

**What would change.** Under the combined profile, an alternative is clear only if it is clear under every
admissible filling of the silences, so an alternative that only the default permits would become "undecided:
the text does not say whether it may be performed", and not clear. Most clear actions here rest on the default:
rules 1, 2 and 9 grant the only permissions. The [extended case](../asimov-extended/README.md#the-permission-default)
measures the deny side of this on 51 records: with nothing permitted by default, these rules give a clear action
in 13 of them instead of 37. That is a bound, not the `unspecified` result, which is not computed. `required` and
`prevent_required` are candidates too (the laws list duties and do not say that no other exists); they are not
measured.

## OPEN: fidelity and evidence

- **OPEN — injury and harm thresholds.** `injures_human`,
  `injures_humanity`, `harms_human`, `harms_humanity`, and `harm_to` remain
  annotator judgments. `leads_to` connects a chosen action to an outcome; it
  does not by itself establish proximate injury, the source's “injure” versus
  “come to harm” distinction, or whether a threatened loss is serious enough.
- **OPEN — exact Zeroth Law exception.** The combined 1942 and later wordings
  do not specify a test for when human injury conflicts with protecting
  humanity. Rule 9 permits a First Law breach that prevents a harm to humanity
  only when the robot has no lawful option. Proportionality and tradeoffs
  among different harms need an explicit author judgment or a richer policy:
  two necessary breaches are both permitted, however unequal.
- **OPEN — simultaneous demands.** Two permitted orders can require
  incompatible actions, as scenario `j` shows. W1 precedence resolves
  competing rules about one regulated predicate on one action; it does not
  rank different mapped obligations or choose among actions. When no permitted
  action avoids every threat to the robot, Rule 13 lifts all of its duties,
  whether a higher law or another threat stands in the way. The source speaks
  of one existence and gives no ranking between threats, so an action that
  meets two threats is then as clear as one that meets only one of them.
  Preferring the alternative that meets fewer threats needs a ranking the
  source does not give.
- **OPEN — the permission default.** `permitted` completes to allow, which the source does not state.
  `unspecified` is the faithful completion, and it waits for `norm-defaults@0` to combine with `alternatives@0`
  (see [above](#the-completion-defaults-and-unspecified)).
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
