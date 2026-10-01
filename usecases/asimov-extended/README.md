# Asimov's laws with authored tie-breaking rules

This use case keeps the merged [Asimov v2 rules](../asimov-laws/README.md) unchanged and adds rules that break
some of their ties. **The added rules are this project's, not Asimov's.** Asimov ranks laws, not harms, and says
nothing about orders that conflict with each other. Each added rule, derived name and report line says so. The
[plan](PLAN.md) and its answer key were written before any VE run. Its section 13 lists every change made since.

| File | What it holds |
| --- | --- |
| [base.ve](base.ve) | v2's 13 rules. The only change is `might prevent` for `prevents` in rules 9 and 13, which a risk environment requires; the meaning is the same. |
| [rules.ve](rules.ve) | the whole document: `base.ve` byte for byte, then rules 14–29, the additions (14–25) and four short definitions they use (26–29) |
| [environment.json](environment.json) | v2's vocabulary, the `risk@0` profile, 8 harms in 4 severity classes, the order data and the new derived names |
| [rules.manifest.json](rules.manifest.json), [base.manifest.json](base.manifest.json) | the identities of the 29-rule document and of the base rules alone |
| [source.md](source.md) | where each part comes from |
| [asimov_extended_cases.py](asimov_extended_cases.py) | the 51 decision records |
| [asimov_extended_reading.py](asimov_extended_reading.py) | an independent reading of all 29 rules for one robot |
| [asimov_extended_check.py](asimov_extended_check.py) | runs VE on every case and compares the results with the answer key |
| [answer-key.json](answer-key.json), [results.json](results.json) | the key from PLAN.md sections 6–8, and VE's results |

SHA-256: `base.ve` `c0eef6e84eec517ed5fcd6afae5352895bf424337b94b714640081e6f8b537f5`, `rules.ve`
`6180eecd325c2ce9b9861f46223c7a1d30b2c82028d91e93454fc58c0f4a392a`.

## Results in brief

- **Agreement with the answer key: 51 of 51 records under the v2 rules and 51 of 51 under the extended rules.**
  The independent reading agrees with VE on all 102 results. There is **no disagreement** at record level.
- **Conflicts:** the extended rules are **CONFLICT-FREE**. Lean replayed 18 certificates found by Python's
  prover. The v2 rules alone in the same environment are also CONFLICT-FREE.
- **Followability:** the extended rules are **not** followable everywhere. Lean confirms a **DILEMMA** at scenario
  `j` (two orders with no recorded time or authority: OVER-REQUIRED) and at P8 (every action breaks the Zeroth
  Law: NONE-PERMITTED), as the key says.
- **v2's three "no clear action" models:** two become clear (`b-A0`, `b-A1`) and one stays a dilemma (`j`). Over
  all 51 records, the v2 rules give a clear action in 37 and the extended rules in 49. **No record loses its clear
  action.**
- **Mutants:** 5 of 5 behave as the key says.
- **Sampled records (300, not certificates):** Lean agrees with the independent reading on all 300. The plan's
  claims Q1 and Q2 hold. **Q3 does not**: it fails on 2 records, a finding explained below.
- **The permission default is a modeling choice, not Asimov's.** Like v2, the environment lets an action that no
  rule forbids be performed. Asimov's text grants no such permission. With nothing permitted by default, v2's rules
  give a clear action in only 13 of the 51 records, and P9's base verdict is among those that change. The extended
  rules change in none of the 51 records and in 3 of the 300 sampled ones; see [the permission default](#the-permission-default).

## The rules and their check status

All 29 rules are **CHECKED**: the parser finds exactly one reading for each sentence, renders the document back
to the same text, and reproduces the manifest. No rule uses the parser's listing scaffolding ("first clause: …").
`classified as "…"` and `has the recorded relation "…"` mark a name with no English wording of its own, as in v2.

| Rules | Status | What they say |
| --- | --- | --- |
| 1–13 | CHECKED (Asimov, v2) | The Zeroth, First, Second and Third Laws, exactly as v2 reads them, with v2's completion defaults (a modeling choice, see OPEN). |
| 14 | CHECKED (addition) | An action is lawful if it breaks neither the First nor the Zeroth Law. |
| 15–16 | CHECKED (addition) | The candidates are the lawful actions. If no competing action is lawful, every action that keeps the Zeroth Law is a candidate. |
| 17, 25 | CHECKED (addition) | An action is possibly harmful if it might lead to a harm to a human being, or if nobody ordered it and it might lead to a harm to its own robot. |
| 18 | CHECKED (addition) | **Precaution.** A possibly harmful action is forbidden when a candidate action of the same robot has a less severe worst case. It overrides rules 9, 8, 2 and 1. |
| 19 | CHECKED (addition) | **Least severe worst case.** A candidate that no candidate beats on worst case may be performed. It overrides the First Law ban (rule 8). |
| 20–24 | CHECKED (addition) | **Competing orders.** An order is valid if it is lawful and rule 18 does not forbid it. More authority prevails. Between orders whose authority is not ranked, the earlier one stands. An order that a valid order prevails over is no longer required. |
| 26–29 | CHECKED (definition) | An action's own robot's harms; two actions compete when the same robot can take them; "has a less severe worst case" between competitors; "beaten by a candidate". |
| severity order | LABELLED (authored) | A harm to humanity is worse than a death, a death worse than an injury, an injury worse than property damage. The robot's own destruction counts as property damage. This is declared by the Asimov extension author, not derived. |
| harm classes, order data | LABELLED (annotator) | Which class each harm has, and who ordered what, when and with what authority, are the annotator's judgments in each record. |
| likelihood, counting | UNFORMALISED | See OPEN below. |

"A has a less severe worst case than B" means B might lead to a harm more severe than every harm A might lead
to. It compares only the worst class, so one death and two deaths count the same, and a certain harm counts the
same as a possible one.

## Every scenario

"v2" is rules 1–13 and "extended" is rules 1–29, both run by VE on the same decision record. Each result equals
the answer key.

### The v2 spec models

| Scenario | v2 | Extended | What changed and why |
| --- | --- | --- | --- |
| a | pull | pull | unchanged |
| b-A0, one death against one injury | none (nothing permitted) | **pull** | **resolved**: both actions break the First Law, so both are candidates; pull's worst case (an injury) beats the other's (a death) |
| b-A0, a death against a death | none | **nothing, pull** | **tie**: the outcomes are equal; choosing needs a preference between actions |
| b-A0, one injury against one death | none | **nothing** | **resolved**, the mirror case |
| b-A1 (pull also injures), the same three variants | none | **pull** / **nothing, pull** / **nothing** | as b-A0; rule 19 permits a direct injury when its worst case is the least severe |
| c-7 | nothing, pull | nothing, pull | unchanged |
| o-7 | rescue | rescue | unchanged |
| d-full | shield, retreat | shield, retreat | unchanged |
| e | act | act | unchanged |
| j | none (two orders required) | none (two orders required) | **still a dilemma**: nothing records which order came first or has more authority |
| l5 | pull2 | pull2 | unchanged |

### The 22 v2 review regressions

All 22 are **unchanged**, with v2's clear sets. Two of them still let the robot choose among actions that a
reader might rank: `two-necessary-injuries` (its harms carry no class) and `dominated-action-when-threats-conflict`
(preferring the action that meets fewer threats needs counting).

### Competing orders (authored)

| Scenario | v2 | Extended | Why |
| --- | --- | --- | --- |
| O1, a1 ordered earlier | none | **a1** | the earlier order stands |
| O2, a2 later but from more authority | none | **a2** | more authority prevails |
| O3, a1 earlier and from more authority | none | **a1** | both reasons agree |
| O4, at the same time, a2 from more authority | none | **a2** | authority alone decides |
| O5, as O2, but a2 might injure someone | none | **a1** | rule 18 forbids a2, so it is not a valid order and does not override a1 |
| O6, as O2, but a2 certainly kills someone | a1 | a1 | unchanged: the First Law already forbids a2 |

### Possibility and severity (authored)

| Scenario | v2 | Extended | Why; what still needs weighing |
| --- | --- | --- | --- |
| P1, two risky rescues | rescue_a, rescue_b | **rescue_b** | rescue_a might kill; rescue_b at worst injures |
| P2, a certain injury against a possible death | rescue | rescue | unchanged: doing nothing breaks the First Law, so it cannot beat the rescue. **Needs likelihood** (`risk@0` stage B) to weigh a certain injury against a possible death |
| P3, an order that might injure | obey | **nothing** | **changed**: rule 18 forbids the order, extending the First Law's priority over orders to possible harm (an authored reading) |
| P4, an order that might destroy the robot | obey | obey | unchanged: an order stays above the robot's own safety |
| P5, two necessary injuries of different severity | act, act2 | **act2** | the lesser breach; this answers v2's OPEN "two necessary breaches are both permitted, however unequal" |
| P6, two deaths against one | none | **nothing, pull** | **tie**: both worst cases are a death. **Needs counting** (`risk@0` stage C) or a preference between actions |
| P7, a possible injury against possible property damage | swerve, brake | **brake** | brake's worst case is less severe |
| P8, every action breaks the Zeroth Law | none | none | **still a dilemma**: no source or addition ranks one Zeroth Law breach above another |
| P9, an unordered action that might destroy the robot | nothing, act | **nothing** | rule 25: the robot avoids a needless possible loss of itself. The v2 result rests on the permission default: no v2 rule grants either action |
| P10, the only rescue might destroy the robot | rescue | rescue | unchanged: doing nothing breaks the First Law, so it cannot make the rescue needlessly risky |

**Totals** (the key's categories): 32 unchanged, 9 resolved, 3 ties, 4 sharpened (a smaller clear set), 1 changed,
2 dilemmas.

## Disagreements and findings

**No record disagrees with the answer key.** The findings below concern the plan's other claims. The key was not
edited; [PLAN.md](PLAN.md) section 13 records each item.

1. **The plan's sampled claim Q3 is false.** Q3 said that Ext is OVER-REQUIRED only when neither of two required
   orders prevails over the other. On 2 of the 300 sampled records (`Q051`, `Q067`) one order does prevail, and
   both are still required. In both records every action breaks the First Law. Rule 19 permits both orders, and
   rule 20 counts only a lawful order as valid, so the prevailing order overrides nothing. The plan listed this
   gap as OPEN ("rule 20 ignores the excuses of rules 9 and 19"); the sample shows that it happens.
2. **The plan's English needed rewording.** VE accepts "there is a robot such that that action is available to
   that robot and another action available to that robot …" only with the listing scaffolding, and "both … and
   …" joins only two simple statements. Four short definitions (rules 26–29) now carry those parts, and
   `needlessly_risky` became "possibly harmful and beaten by a candidate". On every record the formulas are
   equivalent to the plan's.
3. **The document is near VE's size limit.** Every derived name is copied into the conflict checks, so the
   deepest one (Law 3's duty, rule 13) nests within a level or two of VE's limit of 64. The rule names decide the
   order of the copied disjunctions. With the additions named `add-…` instead of `tie-…`, an earlier draft of the
   same rules was refused as too deep. A checker that kept derived names as definitions, without copying them,
   would remove this limit.
4. **More conflict certificates than planned.** 18 rather than 14 for the extended rules (the four definitions add
   targets), and 18 rather than 8 for the v2 rules alone, because the environment declares the new names even when
   no rule uses them. The verdicts are as keyed.

## The permission default

The environment completes `permitted` to allow, as v2's does: an action that no rule forbids may be performed. The
other completions are to deny: an action is not required, and a derived name is false, unless a rule says so.
v2's README lists these defaults as modeling choices. **The default allow is not in the source.** Asimov's laws
forbid and require; they never say that whatever they leave open is permitted. v2's rules grant permission only to
a protective action (rule 1), an ordered one (rule 2) and a First Law breach that the Zeroth Law excuses (rule 9).
Every other permission in the v2 results comes from the default.

`asimov_extended_check.py` measures how much rests on it. It decides every record again with `permitted`
completed to deny, and the independent reading has the same switch (`permission_default="deny"`). Lean and the
reading agree on all 102 decisions of the records and all 600 of the sample.

| Records | v2: clear set changes | v2: records with a clear action | Extended: clear set changes |
| --- | --- | --- | --- |
| the 51 decision records | 24, P9 among them | 13 (37 with the default) | none |
| the 300 sampled records | 129 | 138 (256 with the default) | 3 (`Q039`, `Q225`, `Q290`), each keeping a clear action |

So the v2 verdicts depend on the default throughout. In P9, neither `nothing` nor `act` is ordered or
protective, and no v2 rule grants them, so with nothing permitted by default the record has no permitted action.
The extended rules depend on it much less, because rule 19 grants permission to every candidate that no
candidate beats. They still use it in one case: an action that a candidate beats but that rule 18 does not
forbid. Rule 18 only forbids possible harm to a human being or to the robot. In `Q290`, `a2` damages property and
`a1` harms nothing, so only the default permits `a2`. In `Q039` and `Q225`, the same holds for an action that
might harm humanity.

## OPEN

- **The permission default.** An action that no rule forbids is permitted. This is v2's modeling choice, not
  Asimov's, and most v2 verdicts depend on it ([above](#the-permission-default)). Revising it needs an authored
  rule saying which actions the laws leave permitted. The extended rules' answers on the 51 records do not depend
  on it.

- **Counting and aggregation.** Worst-case comparison counts one death the same as two (P6), and one threat to the
  robot the same as two. The missing feature is `risk@0` stage C (costs, additive loss) or a way to state
  preferences between actions.
- **Equal outcomes.** When each action leads to one certain death (`b-A0` and `b-A1`, death against death), no
  count would help. Choosing needs a preference between actions, which the source does not give.
- **Likelihood.** A certain injury against a possible death (P2) is decided by the First Law's inaction clause, not
  by weighing. The missing feature is `risk@0` stage B (bands and chances).
- **Orders with nothing recorded between them.** `j` stays a dilemma until the record says which order came first
  or has more authority. For truly simultaneous orders of equal authority, a preference between actions is needed.
- **Zeroth Law breaches against each other** (P8): neither Asimov nor the additions rank them.
- **Order validity.** VE does not check that "ordered before" is a strict order or that "outranks" is one-way;
  both are annotator data. A valid order must be lawful, so an order excused by rule 9 or rule 19 never prevails
  (finding 1). A chain of overrides is not analysed.
- **Fidelity of the base rules.** Rules 1–13 are v2's translation of Asimov, and v2's completion defaults
  apply with them. The verdicts are faithful to the source only together with the permission default above.
- **Fidelity of the additions.** Rule 19 sets aside the source's "injure" versus "allow to come to harm"
  distinction in a dilemma. Rule 18 extends the First Law's priority over orders to possible harm (P3). The
  severity order and each harm's class are declared, never derived. Two possible harms are possible separately;
  the record does not say they happen together.
- **Law 3 against the additions.** That Law 3 never removes the last clear action is checked on the sample, not
  certified.

## Timing

One run of `asimov_extended_check.py` on 12 workers (16 cores, shared with other jobs at a load average near 29, so these
are rough): conflict certificates for the extended rules 57 s (18 targets found and replayed) and for the v2
rules 4 s; the two followability witnesses 10 s; the 102 decisions of the 51 records 49 s; the 600 decisions of
the 300 sampled records 227 s; the 702 decisions again with the permission default denied 599 s; the five
mutants, beside them, 874 s. The whole run took about 16 minutes.

On the sample, the v2 rules give a clear action in 256 of 300 records and the extended rules in 295. The 5
extended dilemmas are 1 NONE-PERMITTED (every action breaks the Zeroth Law, as Q2 says) and 4 OVER-REQUIRED.

## Running it

```sh
PATH="$HOME/.elan/bin:$PATH" uv run python usecases/asimov-extended/asimov_extended_check.py   # writes results.json
PATH="$HOME/.elan/bin:$PATH" uv run pytest -q tests/test_asimov_extended.py tests/test_asimov_laws.py
```
