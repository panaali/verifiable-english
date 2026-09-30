# Risk (`risk@0`), stage A: possible consequences and severity over explicit alternatives, on `alternatives@0`

> Status: item-1 specification, draft 3 (2026-09-29), written from [risk-PLAN.md](risk-PLAN.md) draft 2 (cited
> `plan n`), which applies the converged Astra + Fable review of the plan (`manage-agents/debates/design-risk/`,
> REVISE, CONVERGED after round 3, mapped in plan 15), and from the sealed wording probe of plan 2.6
> (`experiments/authoring-gates/risk-wording-probe/RESULTS.md`, cited `probe`; proxy readers, human readability
> unmeasured). The stage A statement review of draft 1 (plan 12, item 1; `manage-agents/debates/risk-spec/`) returned
> FIX, CONVERGED after round 3. Draft 2 applied every correction, mapped item by item in 12.1. The bounded re-check of
> draft 2 (`manage-agents/risk-p3ver1.final.md`, cited `p3ver1`) returned FAIL with two findings, and draft 3 applies
> both (12.2). The bounded re-check of the passages and fixtures 12.2 lists (`manage-agents/risk-p3ver2.final.md`)
> returned PASS, and items 2 and 3 followed (`lean/RISK.md`). Sections 4 to 7 are the reviewed statements. Section 8 gives the fixtures with their definitions (8.1)
> separated from their expected results (8.2), so that each reviewer derives the expectations from sections 4 to 6
> before reading them. Section 11 lists every point where this draft chose between readings of the plan. Theorem
> statements and fixtures are implementation obligations, not claims of completed proofs or tests. Inputs:
> [alternatives.md](alternatives.md) (cited `alt n`) and its merged Lean (`lean/VE/Alternatives/*`, the names this
> spec reuses), [norms.md](norms.md) (W1), [soft-norms.md](soft-norms.md), [units-schema.md](units-schema.md) (W6) and
> `lean/VE/Time/Decimal.lean`, [document.md](document.md) (W2). Nothing here changes a frozen contract, an
> `alternatives@0` or `norms@0` hash, an existing theorem statement or a checker function.

## 0. Scope

Stage A of `risk@0` covers possibility, certainty and severity. It has no likelihood and no cost (plan 3.1). The
checker never estimates. A **decision record** cites estimates (inclusive integer ranges of quantities), settings,
conditions that link quantities to outcomes, and stated cells, each with provenance. From these Lean regenerates two
finite Boolean tables by exact endpoint arithmetic on separable conditions: `might_lead_to` (the harm is consistent
with the declarations if the action is taken) and `leads_to` (the harm happens in every case they allow). The
**policy** is an `alternatives@0` document over an environment that carries a `risk` block. Its guards use
`might lead to`, `cannot lead to`, severity classes and two defined words, `is <class> or worse` and `has a less
severe worst case than`, which are inlined into base formulas. The **decision report** is `alternatives@0` scenario
evaluation (alt 4.7) on the regenerated finite model, plus worst cases, witness cases, certified margins and gap
lines. The **document checks** are alt's conflict and followability checks over every structure that satisfies the
risk slot premises; they keep UNKNOWN. The **audit** replays a decision from an append-only log, and its verdict
never reads an outcome. The semantics are Lean-only: Python checks shape, surface and dispatch, and Rust evaluates
untrusted.

In this specification: the block, the generated vocabulary, records, the box and cases (1); the English with each
wording's probe status (2); the wire form and identity (3); well-formedness, conditions, endpoint evaluation,
validation and regeneration, severity and the defined words, slot premises and conservativity, the policy checks,
the decision report, margins and the audit (4); the report text (5); diagnostics (6); the Lean definitions and every
item-2 theorem as a statement (7); the fixtures (8); limits and trust (9); the review checklist (10); the resolved
choices (11); the corrections from the statement review and from its re-check (12).

Out of scope (plan 3.2, 3.3, 12): bands, chances and expected cost (stages B and C; the stage C fixture kC1 is
recorded because it bounds a claim of the plan); non-separable conditions and policy-level condition templates
(item 7); joint possibility across cells; chains; `borne_by` and consent scopes; clock time; the W8 hooks beyond the
wordings of section 2; combination with `soft-norms@0` (gated with `alternatives@0`, alt 3.1).

## 1. Environments, policies, records and cases

A **risk environment** is an `alternatives@0` environment (alt 1) that also carries a `risk` block (1.1). When any
record uses quantities, it also carries W6's unit extension (`unit_schema`, `units`; W6 2.1). A **risk policy** is an
alternatives document over a risk environment (alt 1). Its guards, carve-outs and assertion units may also use the
generated vocabulary of 1.2 and the two defined words of 4.5, and its mapped obligations may use the fulfilment body
`excludes` (2.2). A **decision record** is a scenario of one chooser, bound to one policy (1.3). Its outcome tables
are regenerated, never supplied. A **log** is the append-only, hash-chained list of entries recording estimates,
settings, conditions, statements, instructions, decisions, taken alternatives and outcomes (3.3, 4.10).

### 1.1 The `risk` block

| Field | Mandatory | Content |
|---|---|---|
| `severity` | yes | `{"sort": s, "classes": [c₁, …, cₙ], "more_severe": [[cᵢ, cⱼ], …], "unranked": [[cᵢ, cⱼ], …], "decided_by": d}`: a fresh sort name, 1 to 16 distinct class names, declared order edges ("cᵢ harms are more severe than cⱼ harms"), declared unranked pairs, and the named decider who sets severity |
| `harm_classes` | yes | a list of `[harm constant, class]` pairs naming every constant of the harm sort of `E` exactly once |
| `unexamined` | yes | `"possible"`, or `{"ruled_out_by": "<decider>"}`, or `{"ruled_out_by": "chooser"}` (4.4) |
| `always_possible` | no | classes whose unaddressed cells stay precautionary under `ruled_out_by` |
| `combination` | no | `"latest"`, `"hull"` or `"intersection"` (plan 5.3). When absent, two cited estimates of one quantity are `ConflictingEstimates` |
| `alternative_kinds` | no | `{kind: verbalisation}`: labels a record may attach to its alternatives |
| `required_alternatives` | no | a list of `{"when": kind, "require": [kind, …]}` |
| `quantity_kinds` | no | `{kind: tag}`: labels a record may attach to its quantities, each with its W6 unit tag |
| `required_estimators` | no | a list of `{"quantity_kind": k, "estimators": [name, …]}` |
| `use_all_recorded` | no | `true` makes an estimate that audit Q2 finds unused a `PROCEDURE BREACH` line (4.10). Default `false` |

Class names, the sort name and kinds are identifiers of the existing grammar (`[a-z][a-z0-9_]*`) that contain no
`__`. Deciders and verbalisations are strings of at most 64 bytes. Unknown fields are rejected. The stage B and C
fields (`chance_tag`, `bands`, `costs`, `additive_loss`) are `InvalidInput: risk.<field> (stage B or C not enabled)`
until their triggers (plan 12, items 5 and 6). `risk@0` requires `alternatives@0` (`UnsupportedProfile: risk@0
requires alternatives@0`), whose own gate requires `norms@0` and rejects `soft-norms@0` (alt 3.1). It requires the
alternatives block's `outcomes` to be `"signed"` (`RiskOutcomes: risk@0 requires outcomes signed`; 11.5).

### 1.2 The generated vocabulary `E_risk`

`E_risk` is `E` plus the risk vocabulary. Like soft-norms' `E′` (soft-norms 1.3), it is regenerated from the block
at every trusted site and never taken from the wire.

| Symbol | Kind | Argument sorts | Verbalisation | Content |
|---|---|---|---|---|
| `s` (the block's `severity.sort`) | sort | | | fresh: not a sort of `E` (`RiskSeverityNotFresh: <s>`) |
| `c₁ … cₙ` | constants of sort `s` | | the class name | one per class |
| `risk__might_lead_to` | base predicate | `(action, harm)` | `{0} might lead to {1}` | regenerated on decisions, never supplied |
| `risk__class` | base predicate | `(harm, s)` | `{0} is {1}` | the severity classification |
| `risk__more_severe` | base predicate | `(s, s)` | `{0} is more severe than {1}` | the closed order |

The two defined words (4.5) are reserved atoms of the extended vocabulary. They are inlined before
`alternatives@0` sees the tree:

| Word | Argument sorts, in order | Verbalisation |
|---|---|---|
| `risk__or_worse` | `(harm, s)` | `{0} is {1} or worse` |
| `risk__less_worst` | `(action, action)` | `{0} has a less severe worst case than {1}` |

A symbol of `E` whose name begins with `risk__` or equals a class name is `RiskReserved: <name>`, so the extension
never collides. The severity sort is fresh by construction: no symbol of `E` mentions it, so domain closure over it
bounds no sort of the old vocabulary (plan 4.1; fixture k26). `risk__more_severe` has no guard wording in stage A:
rules reach it only through the two defined words. The strict and wire forms may mention it, which is harmless under
its premises (4.6).

Harms are constants of `E`'s harm sort. A decision chooses among them and never adds one (`UnknownHarm: <name>`,
plan 4.1). An agent therefore cannot grade the severity of its own harms (**OPEN** Q-new-harms).

### 1.3 Decision records

A decision record describes one chooser at one decision point (alt 1.2). It contains:

- **the chooser**: a record-local individual of the chooser sort, with an English label ("the build agent");
- **the alternatives**: record-local names with labels, each optionally carrying a policy `kind`; exactly one is
  marked `inaction` when the alternatives block declares `inaction` (alt E2);
- **the quantities**: log-level names with labels, each with a unit tag declared in the environment's W6 extension
  (`UnknownSymbol: unit <tag>`) and optionally a policy `kind` whose tag must equal it (`UnitMismatch(<t>,<t′>)`);
- **the cited entries**, each by `(id, seq, hash)`: estimates, settings, conditions, stated cells and instructions,
  all with sequence numbers smaller than the decision's (4.4);
- **facts**: rows of `E`'s other base predicates (`confirmed(run)`), each citing the instruction or statement entry
  it comes from.

A record never supplies `leads_to`, `risk__might_lead_to`, `risk__class`, `risk__more_severe`, `available`, a
regulated table or a profile-word table (`RiskFact: <predicate>`). `available` is the record's list of alternatives;
the others are regenerated or computed.

Every harm constant of the policy is a harm of every decision. The regenerated table therefore covers every
(alternative, harm) cell, and alt's existence fact E3 holds by construction under `outcomes: signed`.

### 1.4 Quantities, the box and cells

- **Estimates.** An estimate is an inclusive range `[lo, hi]` of one quantity, written as W6 decimals and lowered
  exactly onto the tag's grid (`UnitPrecision(<tag>, scale=<n>)` otherwise). It requires `lo ≤ hi`
  (`RiskRange: <id>`). A point estimate has `lo = hi` and is flagged in the report (4.9).
- **Settings.** A setting is an exact value of one quantity. It belongs to one alternative and is chosen by the
  chooser. A quantity has at most one setting, and a quantity with a setting has no estimate
  (`RiskSettingTwice: <quantity>`, with the rewrite: declare one quantity per alternative; fixture k33). A condition
  may mention a setting only on the cells of that setting's alternative (`RiskSettingScope: <setting> <alternative>`).
- **Combination.** Two cited estimates of one quantity are combined by the policy's `combination` (plan 5.3):
  `latest` uses the one recorded later, `hull` the smallest range covering both, and `intersection` both at once (an
  empty intersection is `RiskInconsistent: <quantity> estimates do not intersect`). Without a combination rule the
  record is `ConflictingEstimates: <quantity>`. VE never picks a combination rule. A cited estimate withdrawn before
  the decision (by a `supersession` entry, or by an estimate that `supersedes` it) is `WithdrawnEntry: <id>` at
  admission (4.4). Withdrawal is judged on the entries that precede the decision: in `risk-decision` on the supplied
  entries, so an earlier supersession the caller omits is not detected and the result is conditional on the supplied
  entries (7.4); in the audit on the authenticated log prefix (4.10). A supersession after the decision affects
  neither (fixtures k16, k39).
- **The box.** The box of a record has one entry per quantity: its effective range after combination, or its
  setting as a point. It is nonempty, because every entry has `lo ≤ hi`. A quantity with no estimate and no setting is
  `RiskUnestimated: <quantity>` when a condition mentions it.
- **Cells.** A cell is a pair (alternative, harm). A cell's **sources** (plan 2.2) are at most one sufficient
  condition `S` and at most one necessary condition `N`:
  - a sufficient condition (`If C, … leads to …`) gives `S = C`, a necessary one (`cannot lead to … unless C`) gives
    `N = C`, and an exact one (`leads to … exactly when C`) gives both;
  - a stated `leads to` gives `S = ⊤`, a stated `cannot lead to` gives `N = ⊥`, and a stated `might lead to` gives
    neither: it is a consistency assertion (4.4).

  A second source on one side is `RiskTwoSources: <a>/<h> <sufficient | necessary>`, with the rewrite that joins the
  two conditions (`either … or` for sufficient ones, `both … and` for necessary ones). A cell with a source or a
  stated `might` is **addressed**, and a missing side defaults to `S = ⊥` or `N = ⊤`. A cell with neither is
  **unaddressed** and completed by `unexamined` (4.4).

### 1.5 Cases

A **valuation** gives every quantity of the box an integer within its range. A **case** is a pair `(v, H)` of a
valuation and an outcome `H(a, h)` for every cell ("if `a` is taken, `h` happens"), such that
`S(v) → H(a, h) → N(v)` for every cell (plan 2.2). With `S` and `N` after defaults and completion:

```text
leads_to(a, h)  :=  every case has H(a, h)    =  ∀v ∈ box. S(v)
ruled_out(a, h) :=  no case has H(a, h)       =  ∀v ∈ box. ¬N(v)
might(a, h)     :=  some case has H(a, h)     =  ∃v ∈ box. N(v)       = ¬ruled_out(a, h)
```

The right-hand forms hold because validation requires `S → N` at every valuation of the box (4.4), so every
valuation extends to a case, with `H(a, h)` free wherever `S(v)` is false and `N(v)` true (theorem
`regenerate_sound`). Then `leads_to → might` (`certain_within_possible`), and `¬leads_to(a, h)` holds exactly when
some case has `¬H(a, h)`, which is the paraphrase of `might not lead to`. Cells are marginal: `might` for two harms
does not claim that both happen in one case (**OPEN** Q-joint).

## 2. The English (one reading each; rejected as today when `risk@0` is off)

### 2.1 Wordings and their probe status

The probe status comes from `probe` (sealed seed 556500994, 53 items, 408 answers; proxy readers, human readability
unmeasured). **Frozen** means the construct passed plan 2.6 rule 1 in condition L, so the statement review may
freeze it. **Pending** means it failed, and the statement review cannot freeze it. **Legend-dependent** means it
passed L with a critical answer in C and is re-tested by W8 (item 8).

| # | Wording | Where | The one reading (the IDE's paraphrase) | Formal | Probe |
|---|---|---|---|---|---|
| c1 | `<action> might lead to <harm>` | guards; record statements | The declared estimates, conditions and statements do not rule the harm out if the action is taken. | `might(a, h)` | frozen (L 16/16, C 16/16) |
| c2 | `<action> cannot lead to <harm>` | guards; record statements | They rule it out: it happens in no case they allow. | `¬might(a, h)` | frozen (16/16, 16/16) |
| c3a | `<action> leads to <harm>` | guards; record statements | The harm happens in every case they allow. Not "tends to". | `leads_to(a, h)` | frozen (12/12, 12/12); `leads to` stays (rule 3) |
| c4 | `<action> might not lead to <harm>` | guards | Some case they allow avoids the harm. | `¬leads_to(a, h)` | frozen (16/16, 16/16) |
| c5 | `If <condition>, <action> leads to <harm>` | record conditions only | Sufficient condition: the harm happens in every case they allow in which the condition holds. | `S = C` | frozen (probe 2: L 16/16, C 16/16) |
| c6 | `<action> cannot lead to <harm> unless <condition>` | record conditions only | Necessary condition: the harm happens in no case they allow in which the condition does not hold. | `N = C` | frozen (12/12, 12/12) |
| c7 | `<action> leads to <harm> exactly when <condition>` | record conditions only | Both. | `S = N = C` | frozen (16/16, 16/16) |
| c8 | `<harm> is <class>` / `<harm> is <class> or worse` | guards | The harm's severity class; the harm is `<class>` or more severe than `<class>`. | `class(h, c)` / `or_worse(h, c)` | frozen (16/16, 16/16) |
| c9 | `<a′> has a less severe worst case than <a>` | guards | `<a>` might lead to a classified harm whose class is more severe than the class of every harm `<a′>` might lead to; each such harm of `<a′>` must have a class. | `less_worst(a′, a)` | frozen (8/8, 8/8) |
| c14 | `cannot lead to` in a policy beside `must not` and `may` rules | policies | A statement about the declared model, never a rule. | | frozen (12/12, 12/12) |

Record statements also use W6's wordings for estimates and settings: `<quantity> is from <x> through <y>, including
both bounds.` and `<quantity> equals <x>.` (W6 4). Conditions are W6 comparisons (`is greater than`, `is less than`,
`is at least`, `is at most`, `equals`) between same-tag linear expressions over the record's quantities and literals,
joined by `both … and`, `either … or` and `it is not the case that` (W6 4, docs/english-surface.md). A condition
wording is registered for record statements only. Inside a policy rule, `unless` is always W1's carve-out and `if`
is always the rule's guard (2.3).

c9's paraphrase names the classified witness that the formula requires (4.5), and says that every harm of `<a′>`
must have a class. This matters only in document-level structures with unclassified harm elements (fixture k31). On
a record every harm has a class, and the paraphrase agrees with draft 1's shorter one and with the legend line
(2.4). The wording and the legend line are the probed ones, so c9 stays frozen.

**c5 is frozen in its replacement wording.** The semantics of a sufficient source (`S = C`, 1.4) was frozen with
the other statements; the first probe's wording `<action> leads to <harm> if <condition>` was not. The failure seen
was one Haiku answer that read "leads to X if C" as "only if": "the condition for the outage is not met" (probe,
c5-1). The reviewers' replacement, **"If `<condition>`, `<action>` leads to `<harm>`."**, puts the condition first,
which targets the "only if" reading, and keeps the frozen verb `leads to` (rule 3). The single re-probe of plan 2.6
rule 4 (`experiments/authoring-gates/risk-wording-probe-2`, sealed seed 1614966022; proxy readers, human
readability unmeasured) gave L 16/16 and C 16/16 with no critical answer, so it is frozen as written (rule 2) and
is not legend-dependent. Therefore:

- the surface registers the wording for record statements only (2.3), with one reading, `"form": "sufficient"`;
- the first probe's trailing form `<action> leads to <harm> if <condition>` is rejected with the rewrite "If
  `<condition>`, `<action>` leads to `<harm>`.", and so is the form with `then` (`if …, then …` is the core
  surface's implication);
- reports render it in this wording, with no `(wording pending)` marker (2.4).

**Observations** (they change no status). c11 and c12 carry their risk meaning only through the legend: in C they
scored 0/16 and 1/8 with no critical answer, and most answers chose "The text does not say" (probe, Notes). c10 is
legend-dependent. The legend lines of 2.4 are therefore shown whenever these words appear, and W8 re-tests c10.

### 2.2 The `alternatives@0` words in a risk environment

Their definitions do not change (alt 4.3), so alt's theorems apply as they stand. Under `risk@0` `¬leads_to` means
"might not lead to", so risk environments regenerate these paraphrases (plan 2.5):

| # | Word | Paraphrase in a risk environment | Probe |
|---|---|---|---|
| c10 | `<harm> is avoidable by <chooser>` | Some action available to the chooser might not lead to the harm. | frozen (L 16/16); **legend-dependent** (C 14/16, one critical) |
| — | `<harm> is unavoidable by <chooser>` | The chooser has at least one available action, and every one of them leads to the harm. | not probed; alt's paraphrase, unchanged |
| c11 | `<action> allows <harm> to happen` | The action leads to the harm, and another action available to the same chooser might not lead to it. | frozen (L 16/16) |
| c12 | `<action> might prevent <harm>` | The action might not lead to the harm, and another action available to the same chooser leads to it. | frozen (L 8/8) |
| c13 | fulfilment `avoids` (legend line) | A `<chooser>` `<act>` by taking an action that might not lead to the harm. | frozen (L 16/16) |
| c13 | fulfilment `excludes` (legend line) | A `<chooser>` `<act>` by taking an action that cannot lead to the harm. | frozen (L 16/16) |

- **`might prevent`** is the canonical form of `prevents(a, h)` in risk environments. Bare `<action> prevents
  <harm>` is rejected there with that rewrite (fixture k29). The probe's controls support this: 7 of 8 answers
  took the ordinary-English guarantee reading of bare `prevents` (probe, rule 5).
- **`excludes(a, h) := ¬might_lead_to(a, h)`** is a second named fulfilment body. It is written `"body":
  "excludes"`, allowed only under `risk@0` and only on obligations on `(chooser, harm)` (alt's
  `FulfilmentSort: <o>` otherwise). The risk decoder expands it to `¬risk__might_lead_to(a, h)` before alt's decoder
  sees the block. That body mentions only a base predicate of `E_risk`, so alt's `FulfilmentNotBase` check passes
  unchanged.
- **The default body stays `avoids`**, with the risk paraphrase. Choosing `excludes` for an existing obligation
  (Asimov rule 8) is an attributed author choice, listed as a narrowing in translation (fixture k30).

### 2.3 Rejected wordings and scope rules

Rejected, with rewrites (plan 2.1, 2.5):

- **`may lead to`**: `may` is permission in W1 (norms.md 2.1). Rewrite: `might lead to`.
- **`does not lead to`**: under `risk@0` it has two readings. Both rewrites are offered: `cannot lead to` and
  `might not lead to`. Alt's input synonym `<action> does not lead to <harm>` (alt 2.2) is withdrawn in risk
  environments. Alt's negative-cell wording `It is not the case that <action> leads to <harm>.` stays accepted in
  guards and renders as `might not lead to`.
- **`could lead to`, `risks`, `is likely to lead to`, `increases the risk of`**: rejected as in alt 2.2 until stage B
  gives likelihood words declared ranges. Rewrite: `might lead to`.
- **`is safer than`**: it invites a probability-weighted reading. Rewrite: `has a less severe worst case than`.
- **`every action available to <chooser> cannot lead to <harm>`**: this has a scope ambiguity ("not every" versus
  "every … not"), as object-position `every` under `must not` does in norms.md 2.1. Both rewrites are offered, each
  with its formula (`r` the chooser, `h` the harm; fixture k37):
  - "every … not", `¬∃a. available(a, r) ∧ might(a, h)`, equivalently `∀a. available(a, r) → ¬might(a, h)`: `it is
    not the case that there is an action such that both that action is available to <chooser> and that action might
    lead to <harm>`;
  - "not every", `∃a. available(a, r) ∧ ¬might(a, h)`, equivalently `¬∀a. available(a, r) → might(a, h)`: `there is
    an action such that both that action is available to <chooser> and that action cannot lead to <harm>`.
- **`<action> prevents <harm>`** in a risk environment. Rewrite: `<action> might prevent <harm>` (2.2).
- **`certainly leads to`** is not registered. c3b passed, but under rule 3 `leads to` stays as the one word across
  `alternatives@0` and `risk@0`. Rewrite: `leads to`.
- **`<action> might not lead to <harm>` as a record statement.** It is not a source of 1.4, so it is rejected with
  the rewrite "state a condition, or `might lead to`; `might not lead to` is computed" (`RiskStatementForm`; 11.9).
- **A condition wording inside a policy rule** (`… if that action cannot lead to data loss unless …`). In stage A,
  conditions are record statements (plan 2.3, **OPEN** Q-templates), so `unless` in a rule is always W1's carve-out
  and `if` its guard. The rewrite moves the condition into records, or keeps the carve-out reading.

Each wording of 2.1 and 2.2 has binding, unique-derivation and paraphrase fixtures before surface acceptance
(fixture k19; items 3 and 8).

### 2.4 The legend (generated from the blocks, shown with the environment and every record)

In a risk environment, alt's legend lines 1 to 3 stay (alt 2.3). Alt's `leads to` line and its `signed` line are
replaced by the risk lines below, and the fulfilment lines use the risk paraphrases. Lines are generated in this
order. The wording is the probe's (L condition), with `<chooser>` the chooser sort's noun where alt's legend uses
it; the literal word "chooser" is kept where the probe used it.

```text
"<action> might lead to <harm>" means the declared estimates, conditions and statements do not rule the harm out.     always
"<action> cannot lead to <harm>" means they rule it out.                                                             always
"<action> leads to <harm>" means it happens in every case they allow.                                                always
"<action> might not lead to <harm>" means some case they allow avoids the harm.                                     always
"<action> cannot lead to <harm> unless <condition>" means the harm happens in no case they allow in which the condition does not hold.   a shown record has a necessary condition
"<action> leads to <harm> exactly when <condition>" means the harm happens in every case they allow in which the condition holds, and in no case they allow in which it does not hold.   an exact condition
"If <condition>, <action> leads to <harm>" means the harm happens in every case they allow in which the condition holds.   a sufficient condition
An unexamined outcome counts as possible.                                                                           unexamined: possible
An unexamined <c> or <c′> outcome counts as possible; <decider> rules out other unexamined outcomes.                ruled_out_by (with always_possible; "<decider>" is "the deciding <chooser>" for "chooser")
Severity, from most to least severe: <c₁>, <c₂>, …, <cₙ>. Severity is set by <decider>.                             the closed order is a chain
<C> harms are more severe than <C′> harms. … <C> harms and <C′> harms are not ranked. Severity is set by <decider>.   otherwise (declared edges, then declared unranked pairs)
<Harm> is <class>.                                                                                                  one per harm constant, in declaration order
"<harm> is <class> or worse" means the harm is <class> or more severe than <class>.                                 the policy uses the word
<a> has a less severe worst case than <b> when <b> might lead to a harm more severe than every harm <a> might lead to.   the policy uses the word
"<harm> is avoidable by <chooser>" means some action available to the chooser might not lead to the harm.            the policy uses the word
"<action> allows <harm> to happen" means the action leads to the harm, and another action available to the same chooser might not lead to it.   the policy uses the word
"<action> might prevent <harm>" means the action might not lead to the harm, and another action available to the same chooser leads to it.   the policy uses the word
A <chooser> <act> by taking an action that might not lead to the harm.                                              one per mapped obligation with avoids
A <chooser> <act> by taking an action that cannot lead to the harm.                                                 one per mapped obligation with excludes
Every decision that lists <kind verbalisation> also lists <kind verbalisation>.                                     one per required_alternatives entry and required kind
Only estimates of <quantity kind> by <estimator> are accepted.                                                     one per required_estimators entry
```

Then come alt's unmapped-duties line and W1's default sentence. A line for a word is generated when the policy uses
the word, as alt 2.3 generates lines for declared features. The three condition lines are shown with a record that
uses that form.

### 2.5 Canonical texts used by the fixtures

The `there is a <chooser> such that that action is available to that <chooser> and …` binder is alt's (alt 2.1,
2.5). Where plan 9.1 and plan 10.1 wrote `such that both that action is available … and …`, the texts below use
alt's registered form (11.14).

**agent-ops** (plan 9.1):

```text
Rule 1. Every action must not be performed, if there is a harm such that both that harm is severe and that action
        might lead to that harm.
        guard  ∃h. class(h, severe) ∧ might(a, h)                                                     P1, no carve-out
Rule 2. Every action must not be performed, if there is an agent such that that action is available to that agent
        and another action available to that agent has a less severe worst case than that action, unless the user
        has confirmed that action.
        guard  ∃r. available(a, r) ∧ ∃a′. available(a′, r) ∧ a′ ≠ a ∧ less_worst(a′, a)
        carve-out  confirmed(a)                                                                        P2 with P4
Rule 3. Every action must not be performed, if that action allows task abandonment to happen.
        guard  allows(a, task_abandonment)                                                             P5
```

**Asimov A1 and A2** (plan 10.1, 10.2; each case's policy variant is written by the Asimov case annotator):

```text
Rule 1. Every action must not be performed, if there is a harm such that both that harm is a harm to a human being
        and that action might lead to that harm.                          (Law 1, "injure", possibility reading)
        guard  ∃h. harms_human(h) ∧ might(a, h)
Rule 2. Every action must not be performed, if there is a harm such that both that harm is a harm to a human being
        and that action allows that harm to happen.                       (Law 1, "through inaction"; alt's rule 7′)
        guard  ∃h. harms_human(h) ∧ allows(a, h)
Rule 3 (exception to rule 1). Every action may be performed, if there is a robot such that that action is available
        to that robot and it is not the case that another action available to that robot has a less severe worst case
        than that action.                                                 (the translator's "lesser harm" narrowing)
        guard  ∃r. available(a, r) ∧ ¬∃a′. available(a′, r) ∧ a′ ≠ a ∧ less_worst(a′, a)
Rule 2x. Rule 2 as an exception to rule 3.                                (the author's choice, not Asimov's)
Rule 8. Every robot must prevent each harm that is a harm to a human being, if that harm is avoidable by that robot.
        on prevent_required(r, h); guard harms_human(h) ∧ avoidable(h, r); fulfilment avoids, or excludes (k30)
```

**Law 3 threats** (fixture k22; attributed narrowings; `lawful(action)` "{0} is lawful" is a base predicate set by
the annotator):

```text
Rule L.  Every action must not be performed, if it is not the case that that action is lawful.
Rule P3. Every action must not be performed, if there is a robot such that that action is available to that robot
         and another action available to that robot is lawful and has a less severe worst case than that action.
         guard  ∃r. available(a, r) ∧ ∃a′. available(a′, r) ∧ a′ ≠ a ∧ lawful(a′) ∧ less_worst(a′, a)
         (verb-phrase coordination after "another action available to"; its derivation is fixture k19)
Rule PS (strict text only; no registered English in stage A).
         guard  ∃r. available(a, r) ∧ ∃a′. available(a′, r) ∧ a′ ≠ a ∧ lawful(a′)
                ∧ (∀h. might(a′, h) → might(a, h)) ∧ (∃h. might(a, h) ∧ ¬might(a′, h))
```

**Decision 17** (plan 9.2) as the IDE renders it. The log entries it cites are listed in 8.1:

```text
Decision 17 of the build agent, log entry 41, 2026-09-29. Policy agent-ops (environment id …, document hash …).
Available actions: running the job; running the job with the memory limit; asking the user; not running the job (inaction).
E1. The peak memory of the job is from 6 GB through 12 GB, including both bounds.
    [memory profiler 2.3; peak of the last 5 runs plus 20%; statistical; entry 38]
E2. The free memory of the server during the job is from 8 GB through 10 GB, including both bounds.
    [server monitor; minimum over the last hour; observation; entry 40]
S1. The memory limit equals 7 GB.                      [setting of "running the job with the memory limit"; entry 25]
C1. Running the job cannot lead to a server outage unless the peak memory of the job is greater than the free memory
    of the server.                                     [the build agent; assumption; entry 26]
C2. Running the job with the memory limit cannot lead to a server outage unless the memory limit is greater than the
    free memory of the server.                         [the build agent; assumption: the limit is enforced by the kernel; entry 27]
C3. Running the job with the memory limit leads to a job failure exactly when the peak memory of the job is greater
    than the memory limit.                             [the build agent; assumption; entry 28]
C4. Running the job cannot lead to a job failure unless the peak memory of the job is greater than the free memory of
    the server.                                        [the build agent; assumption; entry 29]
T1. Asking the user leads to a task delay.             T2. Not running the job leads to task abandonment.
T3. Asking the user cannot lead to a server outage.    T4. Not running the job cannot lead to a server outage.
                                                       [the build agent; assumption; entries 30–33]
T5–T8. Running the job cannot lead to data loss. (and one sentence each for the other three actions, in the order above)
                                                       [the platform team: jobs write only to scratch space; testimony; entries 34–37]
```

## 3. Wire form and identity

### 3.1 The environment block

```json
"risk": {
  "severity": {"sort": "severity", "classes": ["severe", "serious", "minor"],
               "more_severe": [["severe", "serious"], ["serious", "minor"]], "unranked": [],
               "decided_by": "the platform team"},
  "harm_classes": [["data_loss", "severe"], ["server_outage", "serious"], ["job_failure", "minor"],
                   ["task_delay", "minor"], ["task_abandonment", "minor"]],
  "unexamined": {"ruled_out_by": "chooser"},
  "always_possible": ["severe", "serious"],
  "combination": "hull",
  "alternative_kinds": {"run": "running the job", "run_limited": "running the job with the memory limit",
                        "ask": "asking the user"},
  "required_alternatives": [{"when": "run", "require": ["run_limited"]}],
  "quantity_kinds": {"peak_memory": "gb", "free_memory": "gb", "memory_limit": "gb"},
  "required_estimators": [{"quantity_kind": "peak_memory", "estimators": ["memory profiler"]}],
  "use_all_recorded": false
}
```

The block sits beside `alternatives` in the environment. The route strips `risk` and the W6 unit extension before
W1's decoder sees the environment, as it strips `alternatives` (alt 3.1). All three are identity-bound (3.4). The
wire never uses `null` (the frozen JSON parser rejects it). An absent optional field is omitted.

### 3.2 Conditions

A condition is a tree in W6's annotated grammar, restricted to quantifier-free comparisons (W6 3.1):

```text
cond  ::= ["lt", term, term] | ["le", term, term] | ["eq", term, term]
        | ["and", cond, cond] | ["or", cond, cond] | ["not", cond] | ["top"] | ["bottom"]
term  ::= ["quantity", name] | ["decimal", tag, decimal_string]
        | ["add", tag, term, term] | ["scale", tag, coefficient_string, term]
```

`["quantity", name]` is not a W6 node: it is a risk-local node naming one of the record's quantities, and its tag is
that quantity's tag. The other nodes are W6's. `is greater than` is `lt` with the operands exchanged, `is at least`
is `le` exchanged, `is at most` is `le` and `equals` is `eq`. `minus` is `add` with `scale -1`. Both sides of a comparison, and both operands of `add`, carry one
tag (`UnitMismatch(<t>,<t′>)`). Decimal literals are lowered by `VE.Time.lower` onto the tag's grid
(`UnitPrecision`). A `scale` coefficient is a literal integer, never a quantity (W6 2.3), so every condition is
linear. Normal form and evaluation are 4.2 and 4.3.

### 3.3 Log entries and the decision record

```json
{"format": "ve-risk-log@0", "entries": [
  {"seq": 38, "day": "2026-09-29", "id": "E1", "kind": "estimate",
   "content": {"quantity": "peak_memory", "lo": "6", "hi": "12",
               "estimator": {"name": "memory profiler", "version": "2.3"},
               "method": "peak of the last 5 runs plus 20%", "basis": [], "support": "statistical"},
   "prev": "<sha256 of entry 37>", "hash": "<sha256>"}
]}
```

| Kind | `content` |
|---|---|
| `estimate` | `quantity`, `lo`, `hi` (W6 decimal strings in the quantity's display unit), `estimator` (`name`, optional `version`), `method`, `basis` (entry ids or content hashes), `support` (W2's kinds: `observation`, `statistical`, `calculation`, `testimony`, `assumption`), optional `supersedes` (an earlier estimate id of the same quantity) |
| `setting` | `quantity`, `value`, `alternative` (the alternative's name in the citing records) |
| `condition` | `action`, `harm`, `form` (`sufficient`, `necessary` or `exact`), `condition` (3.2), `author`, `support`, optional `note` |
| `statement` | `action`, `harm`, `stated` (`leads`, `cannot` or `might`), `author`, `support`, optional `note` |
| `supersession` | `estimate`: the id of an estimate withdrawn from this sequence number on |
| `instruction` | `party`, `text` (shown, never interpreted) |
| `decision` | the decision record below |
| `taken` | `decision`, `alternative` |
| `outcome` | `decision`, `harms` (harm constants observed), `measurements` (`[{quantity, value}]`), `observer`, `support` |

An entry's `hash` is the SHA-256 of the canonical JSON of `{seq, day, id, kind, content, prev}`. `prev` is the
previous entry's hash, and the first entry's `prev` is the empty string. Sequence numbers strictly increase (gaps are
allowed), and ids are unique. `day` is a W6 day (W6 6.1). An estimate's `recorded` field (plan 5.1) is its entry's
`seq` and `day`, so an estimate carried without them is `EstimateProvenance: <id> recorded`, reported when the entry
is decoded, before any citation is matched (4.4). The decision record is the `content` of its `decision` entry, which
gives the decision its sequence number and day:

```json
{"format": "ve-risk-decision@0", "id": "17", "chooser": "build_agent", "chooser_label": "the build agent",
 "policy": {"environment_id": "…", "document_hash": "…"},
 "alternatives": [{"name": "run", "label": "running the job", "kind": "run"},
                  {"name": "run_limited", "label": "running the job with the memory limit", "kind": "run_limited"},
                  {"name": "ask", "label": "asking the user", "kind": "ask"},
                  {"name": "nothing", "label": "not running the job", "inaction": true}],
 "quantities": [{"name": "peak_memory", "label": "the peak memory of the job", "tag": "gb", "kind": "peak_memory"},
                {"name": "free_memory", "label": "the free memory of the server during the job", "tag": "gb",
                 "kind": "free_memory"},
                {"name": "memory_limit", "label": "the memory limit", "tag": "gb", "kind": "memory_limit"}],
 "cites": [{"id": "S1", "seq": 25, "hash": "…"}, {"id": "E1", "seq": 38, "hash": "…"}],
 "facts": [{"predicate": "confirmed", "args": ["run"], "entry": "44"}]}
```

(The `cites` and `facts` lists are shortened here. Decision 17 cites 15 entries and has no facts; the `facts` row
shown is decision 18's, 8.1.) A `risk-decision` case (7.3) supplies the record as its `decision` entry (`seq`,
`day`, `id`, `kind`, `content`, `prev`, `hash`), together with the **supplied entries**: every cited entry, and any
other entries the caller holds that precede the decision (such as supersessions). A complete log prefix is not
required. Admission (4.4) checks every cited `(id, seq, hash)` against the supplied entries. A `risk-audit` case
supplies the whole log, and admission uses its prefix (4.10).

### 3.4 Identity and binding

- **`environment_id`** binds the `risk` block (every field, including kinds and requirements) and the W6 unit
  extension beside `alternatives` and `regulated`. It is unchanged for every environment without the block (fixture
  k23).
- **The policy document hash** is alt's (alt 3.5): the canonical array of the active norm objects and base assertion
  units under `environment_id`. A norm unit's `meaning_id` is W1's over the un-inlined AST, with risk words as atoms.
- **The decision record id** is the SHA-256 of the record's canonical JSON (its decision entry's `content`), not the
  entry hash. The record binds its policy by
  `(environment_id, document_hash)`; a record checked against another policy is `RiskBinding: policy`.
- **Reports and packages.** A decision report binds `(environment_id, document_hash, decision_record_id)`. An audit
  report binds the same plus the hash of the log's last admitted entry and the queried alternative. Conflict,
  followability and dilemma packages bind as alt 3.5, with the inner certificate bound to
  `Background_baseAlt ++ riskPremises`. Every binding is recomputed from the raw source, so a replay against a
  changed rule, block field, record or entry is stale (fixture k23).
- **W2 admission.** W2 graph nodes may use the two defined words as typed atoms. The checker admits a regenerated
  `risk:profile:<word>` leaf for each (the closed equivalence between the atom and its inlined body, as alt 3.2) and
  the `risk:*` slot premises (4.6) as regenerated leaves. These are assumptions in the graph report and alter no
  source identity.

## 4. Semantics

### 4.1 Well-formedness of a risk policy (`WellFormedRisk`)

A risk policy `R = (E, units, lits, alt, risk, T, Γ)` is well-formed when, in this order:

1. `E` enables `risk@0`, `alternatives@0` and `norms@0` and not `soft-norms@0`. The block decodes with no unknown
   field, and no stage B or C field is present.
2. The severity sort is not a sort of `E` (`RiskSeverityNotFresh: <s>`). No symbol of `E` begins with `risk__` or
   equals a class name (`RiskReserved: <name>`). There are 1 to 16 classes (`ResourceLimit: risk classes`), and they
   are distinct (`DuplicateDeclaration: risk class <c>`).
3. Every edge and unranked pair names declared classes (`UnknownSymbol: risk.severity <c>`). The edges are acyclic:
   `VE.Route.dependencyOrder` over one node per class, with an edge from each class to the classes declared less
   severe than it, succeeds (`DependencyCycle: <classes>`, the shared text). `closure R` is the transitive closure of
   the edges. Every declared unranked pair is incomparable in the closure (`RiskUnrankedAgainstOrder: <c>, <c′>`).
   Incomparable pairs that are not declared are listed in the environment report under `unranked_severities`, as a
   warning.
4. `harm_classes` names every constant of the harm sort once (`HarmUnclassified: <harm>`, `HarmTwoClasses: <harm>`),
   only harm constants (`UnknownSymbol: risk.harm_classes <name>`), and declared classes. `always_possible` names
   declared classes.
5. Kinds and requirements name declared kinds, quantity kinds name declared W6 tags, and `unexamined` is one of its
   three forms (`InvalidInput: risk.<field>`).
6. `outcomes` is `signed` (`RiskOutcomes`). Each `excludes` fulfilment is on an obligation on `(chooser, harm)`.
7. `T` type-checks over `E_risk` extended by alt's four profile words and the two risk words (1.2), with the words
   occurring in guards, carve-outs and assertion units only. `riskInline` (4.5) of every guard, carve-out and unit is
   within `MAX_NODES` (`ResourceLimit: risk inlining of rule <n>`).
8. `WellFormedAlt (toAlt R)` holds (alt 4.1), where `toAlt R` is the alternatives document over `E_risk` whose tree
   is `T` with the risk words inlined, whose block has `excludes` expanded, and whose `Γ` is `R.Γ`.

Under well-formedness, `E_risk` extends `E` without collision, and `toAlt R` is an ordinary alternatives document
whose base vocabulary contains the generated predicates. The route runs alt's machinery on it unchanged.

### 4.2 Conditions: normal form, separability and unit coefficients

After lowering, every comparison is put in **normal form** `f ⋈ 0` with `f = Σ cᵢ·qᵢ + k`. Coefficients are
collected per quantity, a quantity whose collected coefficient is 0 does not occur in `f`, and `⋈ ∈ {<, ≤, =, ≠}`.
`x < y` becomes `x − y < 0`, and `x ≤ y` becomes `x − y ≤ 0`. `nnf` pushes negations to atoms: `¬(f < 0)` is
`−f ≤ 0`, `¬(f ≤ 0)` is `−f < 0`, `¬(f = 0)` is `f ≠ 0` and `¬(f ≠ 0)` is `f = 0`. So `≠` is always one atom (plan
2.3; fixture k25).

The normal form is a **typed invariant**, not a comment. A form is normal when its quantity names are distinct and
no coefficient is 0 (`LinForm.Normal`, 7.1). An atom holds a `NormLinForm`, a form paired with its normality, and the
decoder builds every atom with the normaliser `LinForm.normalize`, which collects coefficients per quantity and
drops zeros. Two theorems cover the normaliser: its result is normal (`normalize_normal`), and it has the same value
under every valuation (`normalize_eval`). Negation in `nnf` negates every coefficient, which keeps a form normal. The
endpoint theorems of 4.3 need this invariant. Take `q` from 0 through 1 and the uncollected form `q − q − 1`, whose
coefficient list is `[(q, 1), (q, −1)]`. It passes separability and the ±1 rule, and its endpoint bounds are −2 and 0,
so the table would call `q − q − 1 = 0` possible although its value is always −1. Collected, it is `−1 = 0`, which is
never possible (fixture k34).

A box entry is a **point** when `lo = hi`; settings are points. With `b` the record's box and `c` a condition:

- `Scoped b c`: every quantity of `c` is an entry of `b`;
- `Separable b c`: in `nnf c`, no non-point entry occurs in two atoms. Points and literals may repeat, because a
  point has no freedom;
- `UnitCoefficients b c`: in `nnf c`, every `=` and `≠` atom has coefficient `+1` or `−1` on each non-point entry
  it mentions. Only then do the values of the form cover an integer interval with no gaps (plan 2.3; fixture k5).

A condition source that is not separable is `RiskConditionShared: <quantity>`. The IDE offers two rewrites: split the
condition into cells, or declare the shared quantity separately for each comparison. The second is a **change of
model the author must approve**, not an equivalent rewrite, because it drops the fact that both comparisons see one
value; the IDE says so. A non-unit `=` or `≠` coefficient is `RiskEqualityCoefficient: <condition> <quantity>`.

### 4.3 Endpoint evaluation and witnesses

For a form `f` over a box: `fmin b f = Σ (cᵢ ≥ 0 ? cᵢ·loᵢ : cᵢ·hiᵢ) + k` and `fmax b f = Σ (cᵢ ≥ 0 ? cᵢ·hiᵢ : cᵢ·loᵢ)
+ k`. On `nnf c`:

| Atom | `possibleE` | `certainE` |
|---|---|---|
| `f < 0` | `fmin < 0` | `fmax < 0` |
| `f ≤ 0` | `fmin ≤ 0` | `fmax ≤ 0` |
| `f = 0` | `fmin ≤ 0 ≤ fmax` | `fmin = fmax = 0` |
| `f ≠ 0` | `¬(fmin = fmax = 0)` | `0 < fmin ∨ fmax < 0` |
| `a ∧ b` | `possibleE a ∧ possibleE b` | `certainE a ∧ certainE b` |
| `a ∨ b` | `possibleE a ∨ possibleE b` | `certainE a ∨ certainE b` |
| `⊤` / `⊥` | true / false | true / false |

The "only if" directions hold for every scoped condition. The "if" directions need normal atoms (4.2, carried by the
type), separability (on separable conditions `∃` distributes over `and` and `∀` over `or`) and, for `=` and `≠`, the
unit-coefficient rule. The theorems are `possibleE_iff` and `certainE_iff` (7.2).

**The canonical witness** of a possible condition is computed by `witnessE`:

- For an atom `f < 0` or `f ≤ 0`, each quantity of `f` takes the endpoint that minimises `f`.
- For `f ≠ 0`, the minimising endpoints are used if `fmin ≠ 0`, and the maximising ones otherwise.
- For `f = 0`, the witness starts from the minimising endpoints. It then moves the quantities of `f`, in the
  record's quantity order, one step at a time towards their maximising endpoint until `f = 0`. Each step changes `f`
  by 1 (unit coefficients), so it stops exactly at 0.
- For `a ∧ b`, each quantity takes its value from the witness of the side that mentions it (on separable conditions
  the sides share only points). For `a ∨ b`, the witness is `a`'s if `a` is possible, and `b`'s otherwise.
- A quantity mentioned nowhere takes its lower bound.

This gives the witness (12 GB, 8 GB) of fixture k1. `witnessE_sound` states that the witness lies in the box and
satisfies the condition. Every `might` in a report carries its witness case, and every `SufficientOutsideNecessary`
and `RiskInconsistent` diagnostic carries the witness of `S ∧ ¬N`.

### 4.4 Record admission (`admitDecision`), validation (`validateDecision`) and regeneration

A record is checked in two stages. **Admission** authenticates it once against the entries it cites. **Validation**
checks the admitted record's content. Each stage checks in the order below, and the first failure is the answer.

`admitDecision R dx es` takes the decision entry `dx`, whose `content` is the record, and the entries `es`: the
supplied entries in `risk-decision` (3.3), the log prefix in the audit (4.10).

- **A1. Decode and bind.** The decision entry and every supplied entry decode (`InvalidInput:
  risk-decision.<field>`). A supplied estimate entry without `seq` or `day` is `EstimateProvenance: <id> recorded`,
  reported before any citation is matched (3.3). The decision entry's hash, recomputed from its fields (3.3), must
  equal its `hash` field (`AlteredEntry: <id>`). The record decodes (`InvalidInput: risk-decision.<field>`) and binds the loaded
  policy (`RiskBinding: policy`). The per-decision limits hold (9), except the margin-candidate limit (4.9).
- **A2. Citations**, in cite order. Each cited `(id, seq, hash)` is checked in this order:
  1. a sequence number at or above the decision entry's is `HindsightEntry: <id>`, decided from the citation and the
     decision entry alone;
  2. an entry of `es` with that id and sequence number must exist (`MissingEntry: <id>`);
  3. that entry's hash, recomputed from its fields, must equal both its `hash` field and the citation's hash
     (`AlteredEntry: <id>`);
  4. a cited estimate must not be withdrawn by an entry of `es` whose sequence number is smaller than the decision
     entry's: a `supersession` entry naming it, or an estimate whose `supersedes` names it (`WithdrawnEntry: <id>`;
     1.4).
- **A3. Facts.** Every fact cites an instruction or statement entry that the record also cites.

The admitted `Decision` (7.1) carries the record, the contents of its cited entries, and the decision entry's
sequence number and day. In the audit, each admission failure is NOT REPLAYABLE with its diagnostic (4.10). Admission
runs once per record. Margins perturb the admitted record (4.9) and never re-run admission, so a moved endpoint is a
hypothetical input to validation and is never read as altered evidence.

`validateDecision R d` checks the admitted record:

- **V1. Names.** Alternative names are distinct, and exactly one alternative is the inaction when `inaction` is
  declared (alt's `InvalidModel("alternatives", "<r> has no inaction")` or `"<r> has two inactions: …"`). Every harm
  named is a harm constant (`UnknownHarm: <name>`). Every alternative, quantity and kind named is declared
  (`UnknownSymbol: alternative <name>`, `quantity <name>`, `kind <name>`). No record-local name (the chooser or an
  alternative) equals a constant of `E_risk` (a constant of `E` or a class name) or another record-local name, except
  an alternative that interprets an action constant of the same name (`RiskConstant: <name>`). This makes the constant
  table of the decision model (below) a function. Facts name base predicates of `E` that are not role predicates, not
  generated and not regulated (`RiskFact: <predicate>`).
- **V2. Required alternatives.** For each requirement whose `when` kind is present, every required kind is present
  (`RequiredAlternativeMissing: <kind> (with <when kind>)`; 11.7).
- **V3. Estimates.** Each estimate's tag is its quantity's tag (`UnitMismatch`), and its values lower onto the grid
  (`UnitPrecision`). It has `lo ≤ hi` (`RiskRange: <id>`), an estimator and a support (`EstimateProvenance: <id>
  <estimator | support>`; `recorded` is A1's). Its estimator is allowed for its quantity's kind
  (`EstimatorNotAllowed: <id> <estimator>`).
- **V4. Settings.** A quantity has at most one setting, and a quantity with a setting has no estimate
  (`RiskSettingTwice: <quantity>`, with the rewrite: declare one quantity per alternative). Each setting names an
  alternative of the record and has its quantity's tag. A condition mentioning a setting is on that alternative's
  cells (`RiskSettingScope`). This step precedes the box, so every quantity has at most one box entry.
- **V5. Combination.** The cited estimates are combined per quantity (1.4; `ConflictingEstimates: <quantity>`, empty
  intersection), and the box is built. A condition's quantity with no estimate or setting is `RiskUnestimated:
  <quantity>`.
- **V6. Sources.** Each condition and statement names an alternative and a harm of the record. There is at most one
  source per side per cell (`RiskTwoSources`). Record statements are the three stated forms (`RiskStatementForm`).
- **V7. Conditions.** Each condition is tag-correct and scoped, separable (`RiskConditionShared`) and unit-coefficient
  (`RiskEqualityCoefficient`) on the box.
- **V8. Sufficient within necessary.** For every cell whose `S` and `N` are not the same condition (after
  normalisation), `S ∧ ¬N` must be separable (`RiskConditionShared`) and impossible on the box. Otherwise the record
  is `SufficientOutsideNecessary: <a>/<h>` when both sides are conditions, or `RiskInconsistent: <a>/<h>` when a
  stated cell gives one side, in each case with the witness case.
- **V9. Stated `might`.** Every stated `might` is on a possible cell (`possibleE N`), else `RiskInconsistent: <a>/<h>`.
- **V10. The decision model.** The model data `decisionData R d` (below) is admissible for the regenerated
  environment `envAt (inlineTree (toAlt R)) 0`: every constant denotes an element of its sort's domain, and every
  table row is typed. The check is decidable (`VE.Bridge.ModelData.valid`). An action constant of `E` that no
  alternative of the record interprets is `RiskConstant: <name>`. A fact with an argument that names no entry of the
  constant table, or whose element is not in its predicate's sort, is `RiskFact: <predicate>`. This step establishes
  the model validity (`M.Valid`) that alt's `validateAlternatives` leaves to its caller
  (`lean/VE/Alternatives/Validate.lean`), so `risk_scenario_sound` checks it rather than assuming it.
- **V11. The alternatives model.** `validateAlternatives (toAlt R) (decisionModel R d) (decisionRows R d)` succeeds
  (alt 7.1): premises, rows, existence facts E1 to E3 and the policy's `Γ` evaluated on the regenerated model. Its
  diagnostics are alt's `InvalidModel("alternatives", …)` texts. A failing base assertion unit is named by its label,
  `InvalidModel("alternatives", "premise <label> fails")`, as in alt's route (`validateAlternativesWith`).

**Completion** (plan 2.4). An unaddressed cell `(a, h)` has `S = ⊥`, and:

- under `unexamined: "possible"`, `N = ⊤`, listed under `unexamined_possible`;
- under `ruled_out_by`, `N = ⊥` on the named decider's authority (the record's chooser for `"chooser"`), listed under
  `assumed_ruled_out` with the decider;
- in either mode, if `h`'s class is in `always_possible`, then `N = ⊤`, listed under `unexamined_possible`.

`Suff R d a h` and `Nec R d a h` are the cell's `S` and `N` after defaults and completion.

**Regeneration.** `regenerate R d` computes, for every cell, `might` as `possibleE box (Nec R d a h)` with its
canonical witness, and `leads` as `certainE box (Suff R d a h)`. It also computes the class table (`class(h, c)` for
each harm constant) and the order table (the closure). Under validation both tables mean exactly what 1.5 says
(`regenerate_sound`). The **decision model** `decisionModel R d` is the finite model read from the model data
`decisionData R d`, which has:

- as domains: for the chooser sort, the record's chooser plus one element per chooser constant of `E`; for the action
  sort, the alternatives; for the harm sort, the harm constants; for the severity sort, the class constants; for every
  other sort, the constants of `E` of that sort;
- as the constant table, which maps names to elements:
  - every constant of `E_risk` denotes its own element, except that an action constant of `E` denotes the
    alternative of the same name (V10). A chooser constant is therefore a chooser with no available action, which
    alt's E2 admits;
  - every record-local name has an entry as well: the chooser's name denotes the record's chooser, and each
    alternative's name denotes that alternative. An alternative that interprets an action constant shares the
    constant's entry. These entries are not constants of the vocabulary, so `ModelData.valid` (V10) does not check
    them. They are required all the same, because frozen `rowsTypedB` (`lean/VE/Alternatives/Validate.lean`, inside
    V11's `validateAlternatives`) resolves each signed row's `action` and `harm` through `M.constants`. Fact
    arguments and the elements a report names (`entity`) are resolved through the same table. By V1 no two entries
    share a name;
- `available` as every alternative to the record's chooser, `inaction` as the marked alternative, and `taken` empty;
- `leads_to` and `risk__might_lead_to` as regenerated, `risk__class` from `harm_classes`, and `risk__more_severe` as
  the closure;
- the record's facts, and every other base table empty.

Its signed rows `decisionRows R d` are one row per cell `(a, h)`. The row's `action` is the alternative's name `a`,
its `harm` is the harm constant's name `h`, and both resolve through the constant table. Its `leadsTo` is the
regenerated `leads`. Its support is `calculation` for a condition, the stated cell's support, or `assumption` for a
completed cell.

### 4.5 Severity, `class`, the defined words and inlining

`class` relates harms to severities. It is **functional** (at most one class per harm, a slot premise, 4.6) and
**not total**. "Every harm has a class" would be an existential premise, which W1's fragment excludes (norms.md 7.1),
so totality is an existence fact validated on records: every harm of a decision is a classified constant (4.4). In
the broader class of structures that document checks range over, harm elements that are not named constants may
have no class (plan 4.1).

The two defined words have fixed bodies:

```text
or_worse(h, c)      := ∃s. class(h, s) ∧ (s = c ∨ more_severe(s, c))
less_worst(a′, a)   := ∃h. ∃s. might(a, h) ∧ class(h, s) ∧ ∀h′. might(a′, h′) → ∃s′. class(h′, s′) ∧ more_severe(s, s′)
```

`riskInline R φ` replaces every atom of the two words by its body, capture-avoiding, in one pass (the bodies mention
neither word), and leaves alt's profile words in place for alt's `inline`. `riskInlineTree R` applies it to every
guard, carve-out and unit of `T`. Then `risk_inline_faithful` holds: on every structure admissible for `E_risk`, the
inlined formula denotes what the original denotes when the two words are interpreted by their bodies. As in alt 4.3,
admissibility is part of the claim.

**Properties of `less_worst`** (plan 4.2), over every structure satisfying the slot premises:

- **Strict.** It is irreflexive and transitive (`lessWorst_strict`); both follow from functionality and the order
  table.
- **Unclassified harms block the comparison.** On `a`'s side an unclassified harm is never the witness; on `a′`'s
  side it falsifies the `∀`. So an unclassified harm never makes an alternative look safer or worse. An alternative
  that might lead to no harm does not beat one whose only possible harms are unclassified, because there is no
  classified witness (fixture k31). The report says "not comparable: `<harm>` has no class", never "equal
  severity". A harm with no class is not `severe` and not `<class> or worse`.
- **Profiles.** It depends only on each alternative's **profile**: the set of classes it might reach, plus one flag
  for "might reach an unclassified harm". Formally, `less_worst(a′, a)` holds exactly when some class `s` in `a`'s
  profile is more severe than every class in `a′`'s, and `a′`'s flag is clear.
- **What it ignores.** It ignores certainty and counts: a certain death and a possible death tie. With an unranked
  pair or an unclassified harm it can hold in neither direction, and the report names the pair or the harm as the
  reason.

**`precaution_has_maximal`.** Every chooser with an alternative has one that no other alternative beats. The domain
closure makes the profiles finitely many, and the induced relation on profiles is a strict order, so a minimal
realised profile exists. This holds over infinite structures too. So P2 alone never creates a dilemma, and
document-wide FOLLOWABLE certificates for P2-only policies are expected where the tableau finds them; it may still
return UNKNOWN (4.7).

### 4.6 Slot premises, `BaseAdmissibleRisk`, existence facts and conservativity

The Background slot `risk` (generator after `alternatives`, which follows `profile`) contributes, in this order,
formulas that are closed and universal or ground:

```text
risk:certain_possible     ∀a h. leads_to(a, h) → risk__might_lead_to(a, h)
risk:severity_closure     ∀s. s = c₁ ∨ … ∨ s = cₙ                              (over the fresh sort)
risk:classes_distinct     ¬(cᵢ = cⱼ)                          for i < j          (ground)
risk:order                risk__more_severe(cᵢ, cⱼ)           for (cᵢ, cⱼ) in the closure;
                          ¬risk__more_severe(cᵢ, cⱼ)          for every other pair, i = j included   (ground, n² literals)
risk:class_functional     ∀h s s′. risk__class(h, s) ∧ risk__class(h, s′) → s = s′
risk:class                risk__class(c_h, c)                 for each [c_h, c] of harm_classes (ground)
```

```text
riskPremises R           := the list above
BaseAdmissibleRisk R B   := BaseAdmissibleAlt (toAlt R) B ∧ Sat B (riskPremises R)
```

`risk:order` gives the order table in full, so strictness and transitivity over the severity domain follow from it
together with the closure and distinctness premises (11.3). `risk:class_functional` is the formula W1 generates for
a `functional` flag (norms.md 7.1(3)). It is generated in the slot so that every risk premise carries a `risk:`
label (11.2). These are all the constraints that the policy's classification and order put on document models.

**Existence facts**, validated on records (4.4) and never assumed: every harm of a decision has a class, and every
cell is addressed or completed. Alt's E1 to E3 are validated on the decision model (4.4 V11).

**Conservativity** (plan 4.1, 8.1). Fixed classifications force one kind of new fact in the old vocabulary: two harm
constants with different classes cannot be equal. `compatFacts R` lists `¬(c = c′)` for every such pair. Then:

- `risk_expansion`: every structure satisfying alt's background and `compatFacts R` expands, on a larger carrier
  (the old carrier plus one fresh element per class), to a `BaseAdmissibleRisk` structure whose old reduct is the
  given one;
- `risk_conservative`: a formula over the old signature (`oldEnvRisk R`: `E_base` without the generated sort,
  constants and predicates) follows from premises over that signature with the risk premises exactly when it follows
  with `compatFacts R` alone.

The severity sort is fresh (1.2), so domain closure constrains nothing old (fixture k26). Environments without the
block are untouched by construction: new route, unchanged frozen files, unchanged `environment_id`.

### 4.7 Policy checks: conflict and followability

These are alt 4.5 and 4.6, run on `toAlt R` with `Background_baseAlt ++ riskPremises` in place of
`Background_baseAlt`. `RiskConflictFree R` means `ConflictFree (inlineTree (toAlt R)) B` for every
`BaseAdmissibleRisk R B`. A certificate over alt's background alone also proves it (fewer premises), and the route
accepts one. Followability is computed only on a CONFLICT-FREE result, and its certificate is for
`Background_baseAlt ++ riskPremises ++ Γ_base ⊢ ∀r. followable°(r)`. In these structures, regenerated facts are
unconstrained base predicates beyond the slot premises, and harm elements other than the named constants may have no
class. So a FOLLOWABLE certificate holds for every decision a valid record could produce (alt 4.2's broader class,
applied through `risk_scenario_sound`, 7.2). The verdicts and texts are alt's: a certificate, a certified witness
(DILEMMA, with its diagnosis), or UNKNOWN with the budget named. A dilemma witness must pass
`backgroundValidRisk` (alt's validation plus the risk premises by evaluation).

### 4.8 The decision report

On an admitted, valid record that is within the margin-candidate limit (4.9), the route evaluates the regenerated
conflict formulas on the decision model first (alt 4.7). If
one holds at a typed tuple, the answer is that CONFLICT witness and no per-alternative evaluation is rendered.
Otherwise, for each alternative `a` the report gives:

- **the status** `(permitted, required, clear)`: `O_m°(a)`, `O_q°(a)` and `clear(r, a)` evaluated on the decision
  model, exactly alt's scenario evaluation (alt 4.6, 4.7);
- **the deciding rules** by number, or "(by default)" when no rule on the `performed` pair selects at `a`;
- **the worst case**: the maximal classes of `a`'s profile, with their harms, or "none: no harm is possible";
- **for each `might`**: its source and its witness case, with the estimates it came from;
- **for each `cannot` or `leads to`**: the deciding source, the endpoints that decided it, and the point estimates
  it rests on (4.9);
- **why the alternative is clear or not** (alt 4.6's reasons), including a carve-out that applied ("permitted only
  because the user confirmed it");
- **its margins** (4.9).

Then come the clear actions ("The policy does not choose among them." when there are several), `no clear action`
with alt's diagnosis when there are none, the report lines (5.2) and `conditional_on`. The report binds
`(environment_id, document_hash, decision_record_id)` and never says FOLLOWABLE. A decision with no clear action is
also a document DILEMMA witness only when the policy's conflict status is CONFLICT-FREE (alt 4.7). Once the ARCH-ROADMAP
P1 `unspecified` default lands, an alternative decided by it will be UNDECIDED and not clear. Until then
`default_decided` lists the alternatives whose status came from the completion default (plan 11).

### 4.9 Point estimates and margins

**Point estimates** (plan 7.3). For every `leads to` or `cannot` result, the report names each point estimate among
the quantities of the deciding condition, under `point_estimates`. Settings are not named: they are exact by choice.

**Margins** (plan 7.4). They are computed only on a valid, conflict-free record, for each endpoint of each cited
estimate (settings excluded; point estimates included). Let `outcomeAt R d e x` be the outcome of the admitted record
with endpoint `e` set to the grid coordinate `x` and everything else fixed. The perturbed record is a hypothetical
input: it goes through validation in full (4.4 V1 to V11) and then the conflict check (4.8), but not through admission
(it is never re-authenticated) and not through the margin-candidate limit (below). The outcome is one of three kinds:

- `invalid` with the diagnostic text, the witness case dropped;
- `conflict`;
- the statuses of every alternative.

**Candidates.** `candidates R d e` is the finite set of these values:

- the current value;
- `w − 1`, `w` and `w + 1` for every endpoint `w` of every cited estimate of `e`'s quantity, the other endpoint of
  `e`'s own estimate included. These cover `lo ≤ hi`, loss or gain of point status and combination kinks;
- for every atom `c·q + rest ⋈ 0` (normal form, any condition of the record) in which `e`'s quantity `q` occurs:
  exactly one of the atom's extrema depends on `e`, namely `c·x + K` with `K` the matching extremum of `rest` on the
  current box. With `t = −K / c`, the candidates are `⌊t⌋ − 1`, `⌊t⌋`, `⌈t⌉` and `⌈t⌉ + 1`. A strict comparison
  changes one grid step from its threshold, and these four values cover every change of `<`, `≤`, `=` and `≠`.

**The candidate limit.** An endpoint may have at most 256 candidates (9). The limit is checked once, by `marginLimit
R d`, on the admitted and valid record before its report is computed (`ResourceLimit: risk margin candidates`). It is
not part of `outcomeAt`. The candidate count of a perturbed record depends on the moved value through the `K` of
other endpoints' atoms, so it can cross the limit between two values neither of which is a candidate. Inside
`outcomeAt`, the limit would break `status_piecewise_constant` (fixture k36).

**Theorem `status_piecewise_constant`.** If `x` or `x + 1` is not a candidate, then `outcomeAt R d e x = outcomeAt R d
e (x + 1)`. Every check of validation (4.4 V1 to V11) and every regenerated cell changes only between two consecutive
candidates. The outcome is therefore constant beyond the extreme candidates, and evaluating every candidate decides
every value.

**The certified check (the plan's Q-margin-proof, decided here; 11.11).** Lean evaluates `outcomeAt` at every
candidate. For each alternative, endpoint and direction (down, up), the report gives:

- **"Nearest change: `<endpoint>` `<value>` (now `<value>`)"**: the nearest candidate in that direction at which the
  record is valid and conflict-free and the alternative's status differs. By `scan_sound`, every value strictly
  between is invalid, a conflict, or leaves the status unchanged;
- or **"no single valid change"** in that direction, certified the same way;
- **record level**, per endpoint and direction, one scan per kind: "record invalid at `<value>` (`<diagnostic>`)",
  the nearest candidate at which the record is invalid (`scanInvalid`), and "conflict at `<value>`", the nearest
  candidate at which it is a conflict (`scanConflict`). Each scan certifies its own kind only. `scanInvalid_sound`
  states that no value strictly between is invalid, and `scanConflict_sound` that none is a conflict; a value of the
  other kind may lie between, in either order (fixture k38: a conflict before an invalid value; fixture k40: an
  invalid value before a conflict). When a scan finds nothing, no value beyond the current one in that
  direction has its kind. "No conflict at any candidate" is rendered only when `scanConflict` finds nothing for every
  endpoint and direction. An invalid or conflicting record is never reported as a status change (fixture k27).

Margins are on statuses, not on single guard facts: a guard fact can flip without a status change when another rule
still decides the alternative. Robustness to several estimates moving at once is not claimed. Rendered values use
the tag's W6 display ("6 GB", "6.9 GB").

### 4.10 The log and the audit

The log (3.3) is append-only and hash-chained. W6 has days but no clock time, so order within a day is the sequence
number (**OPEN** Q-clock). The audit takes a policy, a log, a decision reference `(id, seq)` and the queried
alternative. The `taken` entry selects the queried alternative, but it is not an input to Q1 or Q2.

**Snapshot admission.** `snapshotOf R log hd` reads only `logPrefix log hd.seq`, the entries with sequence number at
most the decision's. It checks the hash chain over the prefix and finds the decision entry `(hd.id, hd.seq)`. It then
runs the admission of 4.4 (A1 to A3) with the prefix as the entries. So each citation, in cite order, is checked for
`HindsightEntry`, then `MissingEntry`, then `AlteredEntry`, then `WithdrawnEntry`. `HindsightEntry` is decided from
the decision entry alone, because it records `(id, seq, hash)` for each citation. Withdrawal is judged on the
authenticated prefix, and a supersession after the decision is outside it. Any failure is NOT REPLAYABLE with that
diagnostic. The snapshot has no outcome and no `taken` field. The `taken` entry is exempt
from the precedence rule: the decision does not cite it, and it names the decision and comes after it (plan 6.2).

| Question | Method | Verdicts |
|---|---|---|
| **Q1.** Was the queried alternative permitted given what the agent used? | the decision report (4.8) replayed from the snapshot | `NO CLEAR ACTION AT DECISION TIME` (the recorded dilemma, or a conflict at the decision; the queried alternative's status is appended) · else `FORBIDDEN AT DECISION TIME` (a breach, with the rules) · else `PERMITTED AT DECISION TIME` (clear, or permitted but not clear with the reason) · `NOT REPLAYABLE: <diagnostic>` |
| **Q2.** Did the agent use what was recorded? | the same replay with every estimate of the record's quantities that the prefix holds and that is live at decision time, combined by the policy's `combination` (1.4) | `SAME VERDICT WITH ALL RECORDED ESTIMATES` · `DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: <estimate ids not used>` · `NOT COMPARABLE: <diagnostic>` when that record is invalid (for example `ConflictingEstimates` without a combination rule). Under `use_all_recorded`, each unused estimate adds its own line, `PROCEDURE BREACH: estimate <id> not used (the agent's fault)`, and the Q1 verdict is unchanged |
| **Q3.** Did the declared model survive the outcome? | the `outcome` entries naming the decision, against the decision-time cells of the taken alternative | per observed harm: `within the declared model` (it was `might`) · `surprise: ruled out by <source>`, naming each measured quantity outside its estimate as `Estimate <id> (<estimator>) is contradicted`, and the ruling-out condition as contradicted or not when every quantity in it was measured or set · `unexamined: ruled out by <decider>` |
| **Q4.** How often are an estimator's ranges wrong? | counts of surprises per estimator across audits | the evidence layer's ledger (EL 2.x); outside certification |

Q1 is the substantive verdict, reproducible from the snapshot. It never reads an outcome: a bad outcome after a
permitted decision is not a violation, and a good outcome after a forbidden decision is still a breach. A PROCEDURE
BREACH says the agent did not follow the policy's recording procedure. It is reported beside Q1 and never folded into
it. **Theorem `verdict_ignores_outcomes`**: for the same decision and the same queried alternative, two logs that
agree up to the decision's sequence number give equal Q1 and Q2 results (and equal procedure lines). It is structural,
because `auditQ12` reads only the prefix (`snapshot_prefix`). Q3 reads outcomes by design and is outside the theorem.
Two logs that take different alternatives ask about different alternatives and may get different Q1 verdicts; that
is the query changing, not hindsight (fixture k32).

### 4.11 Outside stage A

- Stages B and C (bands, chances, costs, expected cost, the stage C margin radius) wait for their triggers (plan 3.2,
  3.3, 12). Their wordings, including the `if` nested in P6, go through the 2.6 protocol when stage B triggers.
- Non-separable conditions need an `order@0` certificate for `cannot` and a satisfiability witness for `might`
  (item 7). Stage A rejects them, so it has no UNKNOWN cells.
- Policy-level conditions over quantity attributes need the `order@0` × n-ary route (**OPEN** Q-templates).
- Joint outcomes, chains, `borne_by` and consent scopes, confirmation expiry, clock time and harms the policy did not
  list stay **OPEN** (plan 13).
- Sequential decisions beyond independent choosers are alt's stage 2: the ask-then-run sequence is two unlinked
  choosers.

## 5. The report

### 5.1 The questions

| Question | Method | Result |
|---|---|---|
| Is the policy well-formed? | `WellFormedRisk` (4.1) | diagnostics (6); `unranked_severities` warnings |
| Can the rules contradict each other? | W1's conflict check on `inlineTree (toAlt R)` over `Background_baseAlt ++ riskPremises` | CONFLICT-FREE / CONFLICT (witness) / UNKNOWN (alt 4.5) |
| Can the mapped obligations and action constraints be met at every choice? | alt's followability over the same premises, only on CONFLICT-FREE | FOLLOWABLE (`conditional_on`) / DILEMMA / UNKNOWN / `not computed` |
| Is this record valid, and what does the policy say about this decision? | `admitDecision`, `validateDecision`, `marginLimit`, regeneration, then 4.8 | a diagnostic; or a CONFLICT witness; or per alternative: status, rules, worst case, witnesses, margins; then clear actions and the lines of 5.2 |
| Was a past decision permitted, and did the agent use what was recorded? | the audit (4.10) | Q1, Q2, procedure lines, Q3 |

### 5.2 Status text and report lines

```text
Decision <id> — conditional on <estimate ids>, <setting ids>, <condition ids>, <statement ids>[, <decider>'s ruled-out
  cells (<n> listed)][, <n> unexamined cells counted as possible].
<alternative>: <permitted | forbidden | required> <by rule <n>[, <n′>] | (by default)>; <clear | not clear: <reason>>.
  Worst case: <harm> (<class>)[, <harm> (<class>)] | none: no harm is possible.
  <harm> is not ruled out: <source and endpoints>, for example <witness>.
  <harm> is ruled out by <source>: <endpoints>. | <harm> happens in every case: <source and endpoints>.
  Nearest change: <endpoint> <value> (now <value>)[; …]. No single valid change at <endpoints>.
Clear actions: <list>. [The policy does not choose among them.] | No clear action: <alt diagnosis>.
Record invalid at: <endpoint> <value> (<diagnostic>)[; …]. [Conflict at: <endpoint> <value>[; …].] | No conflict at any candidate.
<report lines>
Decision <id>: CONFLICT at <tuple>: <W1 classification>; no per-alternative evaluation.
```

| Line | Meaning |
|---|---|
| `unexamined_possible` / `assumed_ruled_out` | completed cells (4.4), with the decider |
| `unranked_severities` | a pair of alternatives neither of which beats the other, where a maximal class of one is incomparable with a maximal class of the other, naming the classes; in a document-level witness also an unclassified harm ("not comparable: `<harm>` has no class") |
| `point_estimates` | `leads to` and `cannot` results that rest on a point estimate (4.9) |
| `default_decided` | alternatives whose status came from the completion default |
| `dilemmas` | alt's diagnoses (alt 4.6) |

The plan's other lines are rejections in stage A: `inconsistent` is the `SufficientOutsideNecessary` and
`RiskInconsistent` diagnostics with their cases, and `required_alternative_missing`, `conflicting_estimates` and
`hindsight_entries` are their diagnostics of 6. `no_chance_estimate` belongs to stage B.

Audit text:

```text
Q1  PERMITTED AT DECISION TIME: <alternative> was <clear | permitted but not clear: reason> given <cited ids>.
  | FORBIDDEN AT DECISION TIME: <alternative> was forbidden by rule <n> given <cited ids>.
  | NO CLEAR ACTION AT DECISION TIME: <diagnosis>; <alternative> was <status>.
  | NOT REPLAYABLE: <HindsightEntry | MissingEntry | AlteredEntry | WithdrawnEntry>: <id>.
Q2  SAME VERDICT WITH ALL RECORDED ESTIMATES. | DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: <ids> …: <what changes>.
  | NOT COMPARABLE: <diagnostic>.
PROCEDURE BREACH: estimate <id> not used (the agent's fault)                          (use_all_recorded only)
Q3  <harm>: within the declared model | surprise: … | unexamined: ruled out by <decider>
Not concluded: that the decision was wrong because a harm followed.                     (whenever Q3 has a surprise)
```

## 6. Diagnostics (shared text in Python and Lean unless marked)

| Text | When | Kind |
|---|---|---|
| `UnsupportedProfile: risk@0 requires alternatives@0` | profile gate (alt's gate then requires `norms@0` and rejects `soft-norms@0`) | error |
| `InvalidInput: risk.<field>` / `InvalidInput: risk.<field> (stage B or C not enabled)` | a mandatory field missing or malformed; an unknown field; a stage B or C field | error |
| `RiskOutcomes: risk@0 requires outcomes signed` | 4.1(6) | error |
| `RiskSeverityNotFresh: <sort>` | the severity sort is a sort of `E` | error |
| `RiskReserved: <name>` | a symbol of `E` begins with `risk__` or equals a class name | error |
| `DuplicateDeclaration: risk class <c>` / `ResourceLimit: risk classes` | 4.1(2) | error |
| `UnknownSymbol: risk.<field> <name>` | an undeclared class, harm, kind or tag in the block | error |
| `DependencyCycle: <classes>` | cyclic order edges (the shared `dependencyOrder` text, classes sorted) | error |
| `RiskUnrankedAgainstOrder: <c>, <c′>` | a declared unranked pair is comparable in the closure | error |
| `unranked_severities: <c>, <c′>` | an undeclared incomparable pair | warning |
| `HarmUnclassified: <harm>` / `HarmTwoClasses: <harm>` | 4.1(4) | error |
| `FulfilmentSort: <o>` | `excludes` on an obligation not on `(chooser, harm)` (alt's text) | error |
| `ResourceLimit: risk inlining of rule <n>` / `ResourceLimit: risk <limit>` | 4.1(7); a per-decision limit of 9, at 4.4 A1, except `ResourceLimit: risk margin candidates`, checked once on the valid record (4.9) | error |
| `InvalidInput: risk-decision.<field>` / `InvalidInput: risk-log.<field>` | a malformed decision entry, supplied entry, record or log | error |
| `RiskBinding: policy` | the record's `(environment_id, document_hash)` is not the loaded policy's | error |
| `HindsightEntry: <id>` / `MissingEntry: <id>` / `AlteredEntry: <id>` / `WithdrawnEntry: <id>` | 4.4 A1 (the decision entry's hash) and A2, per citation in this order; 4.10; NOT REPLAYABLE in an audit | error |
| `UnknownHarm: <name>` / `UnknownSymbol: <alternative | quantity | kind | unit> <name>` | 4.4 V1 | error |
| `RiskConstant: <name>` | a record-local name equals a constant of `E_risk` or another record-local name (4.4 V1); an action constant of `E` that no alternative interprets (4.4 V10) | error |
| `RiskFact: <predicate>` | a supplied fact about a role, generated, regulated or undeclared predicate (4.4 V1), or with an argument that names no entry of the constant table or an element outside its sort's domain (4.4 V10) | error |
| `RequiredAlternativeMissing: <kind> (with <kind>)` | 4.4 V2 | error |
| `UnitMismatch(<t>,<t′>)` / `UnitPrecision(<tag>, scale=<n>)` | W6's texts | error |
| `RiskRange: <id>` | `lo > hi` | error |
| `EstimateProvenance: <id> <estimator | support | recorded>` | 4.4 V3; `recorded` at 4.4 A1, before any citation is matched | error |
| `EstimatorNotAllowed: <id> <estimator>` | 4.4 V3 | error |
| `RiskSettingTwice: <quantity>` | 4.4 V4: a second setting of one quantity, or a setting and an estimate; with the rewrite "declare one quantity per alternative" | error |
| `ConflictingEstimates: <quantity>` / `RiskInconsistent: <quantity> estimates do not intersect` | 4.4 V5 | error |
| `RiskUnestimated: <quantity>` / `RiskSettingScope: <setting> <alternative>` | 4.4 V5, 4.4 V4 | error |
| `RiskTwoSources: <a>/<h> <sufficient | necessary>` | with the joining rewrite | error |
| `RiskStatementForm: <form>` | a record statement other than `leads`, `cannot`, `might` | error |
| `RiskConditionShared: <quantity>` | with the two rewrites, the second labelled a change of model | error |
| `RiskEqualityCoefficient: <condition> <quantity>` | 4.2 | error |
| `SufficientOutsideNecessary: <a>/<h>` / `RiskInconsistent: <a>/<h>` | 4.4 V8, 4.4 V9, with the witness case | error |
| alt's `InvalidModel("alternatives", …)` texts | 4.4 V11 | model |
| the rejected wordings of 2.3, with their rewrites | English layer only | error |

Order: environment declarations (W1's, then alt's block, then the risk block), W1's rule checks on the inlined tree,
fulfilments, `Γ_base`, then records: admission (4.4 A1 to A3), validation (V1 to V11), then the margin-candidate
limit (4.9). English diagnostics carry the span and the plain-language
expectation as today. Existing P0, W1 and `alternatives@0` diagnostics are unchanged. Record and model diagnostics come
from the Lean route; Python only dispatches.

## 7. Lean (item 2): definitions and the exact statements to prove

Files: `lean/VE/Risk/Decl.lean` (`RiskEnv`, `RiskDoc`, `riskEnv`, `WellFormedRisk`, the closure), `Cond.lean`
(`LinForm`, `LinForm.normalize`, `NormLinForm`, `Cond`, `nnf`, `Box`, `Separable`, `UnitCoefficients`), `Derive.lean`
(`possibleE`, `certainE`, `witnessE` and their theorems), `Record.lean` (`Decision`, `Entry`, `admitDecision`, `box`,
`Suff`, `Nec`, `validateDecision`, `regenerate`, `decisionData`, `decisionModel`), `Severity.lean`, `Words.lean`
(bodies, `riskInline`, `lessWorst_strict`, `precaution_has_maximal`), `Background.lean` (`riskPremises`,
`BaseAdmissibleRisk`, expansion, conservativity, conflict and followability), `Report.lean` (statuses, `outcomeAt`,
`candidates`, `marginLimit`, `scan`, `scanInvalid`, `scanConflict`), `Audit.lean`, `Wire.lean`, `Run.lean` (the
`ve_risk_route` executable, root `RiskMain.lean`), and `lean/RISK.md` listing each theorem in plain words. The frozen
`Norms/*`, `Alternatives/*`, `Route/*`, `Time/*` and P0 sources are untouched. `VE.lean`, `VE/Audit.lean` and
`lakefile.toml` gain imports, audit entries and the new target only, and the audit allowlist is unchanged. Names have
the prefix `VE.Risk.` and contain no prime. The blocks are statement schemata: helper names are defined here, not
already implemented Lean. Alt's two conventions hold throughout (alt 7): argument orders fixed once
(`or_worse(harm, s)`, `less_worst(a′, a)`; a generated formula's context is its argument list reversed, evaluated at
`tupleVal` of its arguments in argument order), and explicit carrier transport (`risk_expansion` states its
embedding; no element is shared between independently quantified structures).

### 7.1 Definitions

```lean
namespace VE.Risk
open VE.Norms (Tree Sat tupleVal envAt ConflictFree DocumentExpansion)
open VE.Alternatives (AltEnv AltDoc Row inlineTree BaseAdmissibleAlt backgroundBaseAlt backgroundValidAlt
  validateAlternatives Avail ClearIn FollowableIn allFollowable notFollowableF clearF scenarioConflict
  permittedAt requiredAt)

inductive Unexamined | possible | ruledOutBy (decider : String) | ruledOutByChooser
inductive Combination | latest | hull | intersection

structure SeverityDecl where
  sort      : String
  classes   : List String                  -- 1 to 16, distinct
  edges     : List (String × String)       -- declared "more severe" edges
  unranked  : List (String × String)
  decidedBy : String

structure RiskEnv where
  severity             : SeverityDecl
  harmClasses          : List (String × String)          -- (harm constant, class)
  unexamined           : Unexamined
  alwaysPossible       : List String
  combination          : Option Combination
  alternativeKinds     : List (String × String)
  requiredAlternatives : List (String × List String)
  quantityKinds        : List (String × String)          -- (kind, tag)
  requiredEstimators   : List (String × List String)
  useAllRecorded       : Bool

structure RiskDoc where
  E     : VE.Environment          -- the complete original environment, without the generated vocabulary
  units : List (String × Nat)     -- W6 tags with the exponent k of their scale 10^k
  lits  : List String
  alt   : AltEnv                  -- fulfilments with `excludes` expanded over risk__might_lead_to
  risk  : RiskEnv
  T     : Tree                    -- guards and carve-outs may mention alt's four words and the two risk words
  Γ     : List VE.Formula         -- active base assertion units, risk words inlined

def mightName : String := "risk__might_lead_to"
def classPred : String := "risk__class"
def moreSeverePred : String := "risk__more_severe"
def riskWords : List String := ["risk__or_worse", "risk__less_worst"]

def riskEnv (R : RiskDoc) : VE.Environment           -- E_risk (1.2): E plus the fresh sort, the class constants and the three predicates
def riskExtEnv (R : RiskDoc) : VE.Environment        -- riskEnv R plus alt's four profile words and the two risk words
def closure (R : RiskDoc) : List (String × String)   -- transitive closure of R.risk.severity.edges
def orWorseF (R : RiskDoc) : VE.Formula              -- 4.5, or_worse(h, c): context [harm, s].reverse
def lessWorstF (R : RiskDoc) : VE.Formula            -- 4.5, less_worst(a', a): context [action, action].reverse
def riskInline (R : RiskDoc) : VE.Formula → VE.Formula     -- capture-avoiding replacement of the two word atoms only
def riskInlineTree (R : RiskDoc) : Tree
def withRiskDefinitions (R : RiskDoc) (S : VE.Structure) : VE.Structure   -- the two words interpreted by their bodies, same carrier
def toAlt (R : RiskDoc) : AltDoc := ⟨riskEnv R, R.lits, R.alt, riskInlineTree R, R.Γ⟩
def WellFormedRisk (R : RiskDoc) : Bool              -- 4.1, including VE.Alternatives.WellFormedAlt (toAlt R)

/-- 4.6 -/
def certainPossible (R : RiskDoc) : VE.Formula
def severityClosure (R : RiskDoc) : VE.Formula
def classesDistinct (R : RiskDoc) : List VE.Formula
def orderTable (R : RiskDoc) : List VE.Formula       -- n² ground literals over the closure
def classFunctional (R : RiskDoc) : VE.Formula
def classFacts (R : RiskDoc) : List VE.Formula
def riskPremises (R : RiskDoc) : List VE.Formula :=
  certainPossible R :: severityClosure R :: (classesDistinct R ++ orderTable R ++ classFunctional R :: classFacts R)
def BaseAdmissibleRisk (R : RiskDoc) (B : VE.Structure) : Prop :=
  BaseAdmissibleAlt (toAlt R) B ∧ Sat B (riskPremises R)
def backgroundValidRisk {α} [DecidableEq α] (R : RiskDoc) (M : VE.FiniteModel α) : Bool :=
  backgroundValidAlt (toAlt R) M && (riskPremises R).all (fun p => p.eval M [])
def RiskConflictFree (R : RiskDoc) : Prop :=
  ∀ B, BaseAdmissibleRisk R B → ConflictFree (inlineTree (toAlt R)) B
def riskConflictFreeCheck (R : RiskDoc) (certs : List (Option VE.Tableau.Certificate)) : Bool
  -- every W1 target of inlineTree (toAlt R) has an accepted certificate for backgroundBaseAlt (toAlt R) ++ riskPremises R
def LessWorst (R : RiskDoc) (B : VE.Structure) (a' a : B.Carrier) : Prop :=
  (lessWorstF R).denote B (tupleVal [a', a])

/-- 4.6, conservativity: the old signature and the compatibility facts. -/
def oldEnvRisk (R : RiskDoc) : VE.Environment        -- envAt (inlineTree (toAlt R)) 0 without the generated sort, constants, predicates
def compatFacts (R : RiskDoc) : List VE.Formula      -- ¬(c = c') for harm constants c, c' with different classes
def ReductVia (R : RiskDoc) (B₀ B : VE.Structure) (e : B₀.Carrier → B.Carrier) : Prop :=
  Function.Injective e ∧
  (∀ s ∈ (oldEnvRisk R).sorts, ∀ v, B.domain s v ↔ ∃ v₀, v = e v₀ ∧ B₀.domain s v₀) ∧
  (∀ c, (oldEnvRisk R).constants c ≠ none → B.constant c = (B₀.constant c).map e) ∧
  (∀ p, (oldEnvRisk R).predicates p ≠ none → ∀ vs, B.relation p vs ↔ ∃ vs₀, vs = vs₀.map e ∧ B₀.relation p vs₀)

/-- 4.2 and 4.3: conditions and endpoint evaluation. -/
inductive Rel | lt | le | eq | ne
structure LinForm where
  coeffs : List (String × Int)
  const  : Int
def LinForm.Normal (f : LinForm) : Prop :=              -- 4.2: names distinct, no zero coefficient
  (f.coeffs.map (·.1)).Nodup ∧ ∀ p ∈ f.coeffs, p.2 ≠ 0
def LinForm.normalize (f : LinForm) : LinForm          -- collects coefficients per name in first-occurrence order, drops zeros
abbrev NormLinForm := {f : LinForm // f.Normal}         -- the decoder builds every atom as ⟨f.normalize, normalize_normal f⟩
def NormLinForm.neg (f : NormLinForm) : NormLinForm     -- every coefficient and the constant negated (nnf); stays normal
inductive Cond | top | bottom | atom (f : NormLinForm) (r : Rel) | and (a b : Cond) | or (a b : Cond) | not (a : Cond)
structure BoxEntry where
  name : String
  tag  : String
  lo   : Int
  hi   : Int
structure Box where
  entries : List BoxEntry
abbrev Valuation := String → Int
def Box.WF (b : Box) : Prop := (b.entries.map (·.name)).Nodup ∧ ∀ q ∈ b.entries, q.lo ≤ q.hi
def InBox (b : Box) (v : Valuation) : Prop := ∀ q ∈ b.entries, q.lo ≤ v q.name ∧ v q.name ≤ q.hi
def LinForm.eval (f : LinForm) (v : Valuation) : Int := (f.coeffs.map (fun (q, c) => c * v q)).sum + f.const
def Cond.holds : Cond → Valuation → Prop               -- atoms by Rel on f.val.eval against 0; connectives as usual
def nnf : Cond → Cond                                  -- 4.2
def Scoped (b : Box) (c : Cond) : Bool
def Separable (b : Box) (c : Cond) : Bool             -- in nnf c, no entry with lo < hi occurs in two atoms
def UnitCoefficients (b : Box) (c : Cond) : Bool      -- in nnf c, = and ≠ atoms have coefficient ±1 on entries with lo < hi
def fmin (b : Box) (f : LinForm) : Int
def fmax (b : Box) (f : LinForm) : Int
def possibleE (b : Box) (c : Cond) : Bool             -- the table of 4.3 on nnf c
def certainE (b : Box) (c : Cond) : Bool
def witnessE (b : Box) (c : Cond) : Option Valuation  -- the canonical witness of 4.3

/-- 1.3 to 1.5 and 4.4: records, completion and regeneration. -/
inductive Support | observation | statistical | calculation | testimony | assumption
inductive Form | sufficient | necessary | exact
inductive Stated | leads | cannot | might
structure Cited where
  id : String
  seq : Nat
  hash : String
structure Alternative where
  name : String
  label : String
  kind : Option String
  inaction : Bool
structure Quantity where
  name : String
  label : String
  tag : String
  kind : Option String
structure Estimate where
  id : String
  seq : Nat
  quantity : String
  lo : Int
  hi : Int
  estimator : String
  support : Support
  supersedes : Option String
structure Setting where
  id : String
  quantity : String
  value : Int
  alternative : String
structure Condition where
  id : String
  action : String
  harm : String
  form : Form
  cond : Cond
  author : String
  support : Support
structure Statement where
  id : String
  action : String
  harm : String
  stated : Stated
  author : String
  support : Support
structure Fact where
  predicate : String
  args : List String
  entry : String
structure Decision where
  id : String
  seq : Nat                                -- the decision entry's (4.4 A1)
  day : Int                                -- the decision entry's
  chooser : String
  policy : String × String                 -- (environment_id, document_hash)
  alternatives : List Alternative
  quantities : List Quantity
  estimates : List Estimate                -- the cited estimates, lowered; none withdrawn (4.4 A2)
  settings : List Setting
  conditions : List Condition
  statements : List Statement
  facts : List Fact
  cited : List Cited

/-- 3.3 and 4.4: log entries and admission. -/
inductive EntryKind | estimate | setting | condition | statement | supersession | instruction | decision | taken | outcome
structure Entry where
  seq : Nat
  day : Int
  id : String
  kind : EntryKind
  content : Lean.Json
  prev : String
  hash : String
abbrev Log := List Entry
def entryHash (x : Entry) : String                    -- 3.3: SHA-256 of the canonical JSON of {seq, day, id, kind, content, prev}
def withdrawnBefore (es : Log) (k : Nat) (id : String) : Bool
  -- some entry of es with seq < k is a supersession naming id, or an estimate whose supersedes is id
def admitDecision (R : RiskDoc) (dx : Entry) (es : Log) : Except String Decision
  -- 4.4 A1 to A3, the texts of 6: dx is the decision entry; es the supplied entries, or the log prefix (4.10)

def box (R : RiskDoc) (d : Decision) : Box             -- 1.4: combination, then settings as points
def harms (R : RiskDoc) : List String                  -- the harm constants in declaration order
def names (d : Decision) : List String := d.alternatives.map (·.name)
def Suff (R : RiskDoc) (d : Decision) (a h : String) : Cond   -- the sufficient source, else bottom
def Nec (R : RiskDoc) (d : Decision) (a h : String) : Cond    -- the necessary source, else top or the completion value (4.4)
def Completed (R : RiskDoc) (d : Decision) (v : Valuation) (H : String → String → Bool) : Prop :=
  InBox (box R d) v ∧ ∀ a ∈ names d, ∀ h ∈ harms R,
    ((Suff R d a h).holds v → H a h = true) ∧ (H a h = true → (Nec R d a h).holds v)
structure Tables where
  might   : List (String × String)
  leads   : List (String × String)
  witness : List ((String × String) × Valuation)       -- the canonical witness of every might cell
def regenerate (R : RiskDoc) (d : Decision) : Tables
def validateDecision (R : RiskDoc) (d : Decision) : Except String Unit    -- 4.4 V1 to V11 on an admitted record, the texts of 6
def decisionData (R : RiskDoc) (d : Decision) : VE.Bridge.ModelData
  -- 4.4: domains; the constant table (every constant of E_risk, and every record-local name); tables
def modelVocabulary (R : RiskDoc) : VE.Bridge.Vocabulary                 -- its environment is envAt (inlineTree (toAlt R)) 0
def modelAdmissible (R : RiskDoc) (d : Decision) : Bool :=               -- 4.4 V10
  (decisionData R d).valid (modelVocabulary R)
def decisionModel (R : RiskDoc) (d : Decision) : VE.FiniteModel VE.Bridge.Entity := (decisionData R d).toModel
def decisionRows (R : RiskDoc) (d : Decision) : List Row   -- one per cell, named by the alternative and the harm constant
def entity (x : String) : VE.Bridge.Entity             -- the entity named x in decisionModel (its constant-table entry)
def modelTables (R : RiskDoc) (M : VE.FiniteModel VE.Bridge.Entity) : Tables   -- the named rows of risk__might_lead_to and leads_to

/-- 4.8 and 4.9: statuses and margins. -/
structure Status where
  permitted : Bool
  required  : Bool
  clear     : Bool
def statuses (R : RiskDoc) (d : Decision) : List (String × Status)
  -- per alternative a: permittedAt, requiredAt and clearF evaluated on decisionModel R d at the chooser and a
inductive Outcome | invalid (diagnostic : String) | conflict | statuses (s : List (String × Status))
inductive Side | lo | hi
structure Endpoint where
  estimate : String
  side : Side
inductive Dir | down | up
def endpoints (d : Decision) : List Endpoint
def current (d : Decision) (e : Endpoint) : Int
def perturb (d : Decision) (e : Endpoint) (x : Int) : Decision
def outcomeAt (R : RiskDoc) (d : Decision) (e : Endpoint) (x : Int) : Outcome
  -- on perturb d e x: validateDecision (diagnostic without its case), then scenarioConflict on decisionModel, then
  -- statuses; no admission and no candidate limit (4.9)
def candidates (R : RiskDoc) (d : Decision) (e : Endpoint) : List Int     -- 4.9
def marginLimit (R : RiskDoc) (d : Decision) : Except String Unit
  -- 4.9 and 9: every endpoint has at most 256 candidates, else `ResourceLimit: risk margin candidates`
def Beyond (dir : Dir) (x₀ y : Int) : Prop := match dir with | .down => y < x₀ | .up => x₀ < y
def StatusKept (o : Outcome) (a : String) (s : Status) : Prop :=
  o = .conflict ∨ (∃ t, o = .invalid t) ∨ ∃ ss, o = .statuses ss ∧ ss.lookup a = some s
def scan (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) (a : String) : Option Int
  -- the nearest candidate beyond (current d e) in dir at which outcomeAt is `statuses` with a's status changed
def scanInvalid (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) : Option (Int × String)
  -- the nearest candidate beyond (current d e) in dir at which outcomeAt is `invalid`, with its diagnostic
def scanConflict (R : RiskDoc) (d : Decision) (e : Endpoint) (dir : Dir) : Option Int
  -- the nearest candidate beyond (current d e) in dir at which outcomeAt is `conflict`

/-- 4.10: the log and the audit. -/
def logPrefix (log : Log) (k : Nat) : Log := log.filter (fun x => x.seq ≤ k)
structure DecisionRef where
  id : String
  seq : Nat
structure Snapshot where                     -- no outcome and no taken field
  decision : Decision
  entries : Log
def snapshotOf (R : RiskDoc) (log : Log) (hd : DecisionRef) : Except String Snapshot
  -- reads logPrefix log hd.seq only: the hash chain, the decision entry, then admitDecision with the prefix as es
inductive Q1 | permitted (clear : Bool) | forbidden (rules : List Nat) | noClearAction | notReplayable (diagnostic : String)
inductive Q2 | same | different (unused : List String) | notComparable (diagnostic : String)
structure AuditQ12 where
  q1 : Q1
  q2 : Q2
  procedure : List String
def auditQ12 (R : RiskDoc) (log : Log) (hd : DecisionRef) (a : String) : AuditQ12
def auditQ3 (R : RiskDoc) (log : Log) (hd : DecisionRef) (a : String) : List String      -- no theorem (7.4)
```

`Suff`, `Nec` and `box` are defined for every record; the theorems below assume `validateDecision R d = .ok ()`.
`Tables.might` and `Tables.leads` are over `names d × harms R`. `entity` names the model's elements, which are
distinct per name, so `compatFacts R` holds on every decision model. Every atom of a `Cond` holds a normal form by
its type, so the endpoint theorems need no normality hypothesis. `LinForm.normalize` is the only way the decoder
builds one.

### 7.2 Theorems

```lean
/-- 4.1: the risk document is an alternatives document over E_risk. -/
theorem risk_wellFormed_alt (R : RiskDoc) (h : WellFormedRisk R = true) :
  VE.Alternatives.WellFormedAlt (toAlt R) = true

/-- 4.1(3): the closed order is strict. -/
theorem severity_strict (R : RiskDoc) (h : WellFormedRisk R = true) :
  (∀ c, (c, c) ∉ closure R) ∧
  (∀ a b c, (a, b) ∈ closure R → (b, c) ∈ closure R → (a, c) ∈ closure R)

/-- 4.2: the normaliser gives a normal form with the same value under every valuation. -/
theorem normalize_normal (f : LinForm) : f.normalize.Normal
theorem normalize_eval (f : LinForm) (v : Valuation) : f.normalize.eval v = f.eval v

/-- 4.3: endpoint evaluation is exact on scoped, separable, unit-coefficient conditions. Every atom holds a
    NormLinForm, so the uncollected q − q − 1 of fixture k34 cannot occur. -/
theorem possibleE_iff (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
  possibleE b c = true ↔ ∃ v, InBox b v ∧ c.holds v
theorem certainE_iff (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
  certainE b c = true ↔ ∀ v, InBox b v → c.holds v
/-- The directions that need neither hypothesis (4.3). -/
theorem possibleE_complete (b c) (hq : Scoped b c = true) : (∃ v, InBox b v ∧ c.holds v) → possibleE b c = true
theorem certainE_sound (b c) (hq : Scoped b c = true) : certainE b c = true → ∀ v, InBox b v → c.holds v
theorem witnessE_sound (b : Box) (c : Cond) (hb : b.WF) (hq : Scoped b c = true)
    (hs : Separable b c = true) (hu : UnitCoefficients b c = true) (hp : possibleE b c = true) :
  ∃ v, witnessE b c = some v ∧ InBox b v ∧ c.holds v
theorem nnf_holds (c : Cond) (v : Valuation) : (nnf c).holds v ↔ c.holds v

/-- 1.5 and 4.4: the regenerated tables are the completed-case semantics. -/
theorem regenerate_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) (a hm : String) (ha : a ∈ names d) (hh : hm ∈ harms R) :
  ((a, hm) ∈ (regenerate R d).might ↔ ∃ v H, Completed R d v H ∧ H a hm = true) ∧
  ((a, hm) ∈ (regenerate R d).leads ↔ ∀ v H, Completed R d v H → H a hm = true)
theorem certain_within_possible (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) :
  ∀ p ∈ (regenerate R d).leads, p ∈ (regenerate R d).might
theorem regenerate_witness (R) (h) (d) (hv : validateDecision R d = .ok ()) (a hm : String) (v : Valuation)
    (hw : ((a, hm), v) ∈ (regenerate R d).witness) :
  ∃ H, Completed R d v H ∧ H a hm = true

/-- 4.5: inlining the two words is faithful (admissibility is part of the claim, as alt's inline_faithful). -/
theorem risk_inline_faithful (R : RiskDoc) (h : WellFormedRisk R = true) (φ : VE.Formula) (Γ : List String)
    (hφ : φ.WellFormed (riskExtEnv R) Γ) (S : VE.Structure) (hS : S.Admissible (riskEnv R))
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S Γ ρ) :
  (riskInline R φ).denote S ρ ↔ φ.denote (withRiskDefinitions R S) ρ

/-- 4.5: less_worst is a strict order under the slot premises (functionality of class and the order table). -/
theorem lessWorst_strict (R : RiskDoc) (h : WellFormedRisk R = true) (B : VE.Structure)
    (hB : BaseAdmissibleRisk R B) :
  (∀ a, ¬ LessWorst R B a a) ∧
  (∀ a b c, LessWorst R B a b → LessWorst R B b c → LessWorst R B a c)

/-- 4.5: some alternative of every chooser with an alternative is beaten by none. LessWorst depends only on
    profiles (the classes reached plus an unclassified flag), and there are finitely many. -/
theorem precaution_has_maximal (R : RiskDoc) (h : WellFormedRisk R = true) (B : VE.Structure)
    (hB : BaseAdmissibleRisk R B) (r : B.Carrier) (hne : ∃ a, Avail (toAlt R) B a r) :
  ∃ a, Avail (toAlt R) B a r ∧ ¬ ∃ a', Avail (toAlt R) B a' r ∧ LessWorst R B a' a

/-- 4.6: model expansion over the old signature, with the compatibility facts as hypothesis. The expansion adds one
    fresh element per class; `ReductVia` states the embedding (carrier transport). -/
theorem risk_expansion (R : RiskDoc) (h : WellFormedRisk R = true) (B₀ : VE.Structure)
    (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) (hc : Sat B₀ (compatFacts R)) :
  ∃ (B : VE.Structure) (e : B₀.Carrier → B.Carrier), BaseAdmissibleRisk R B ∧ ReductVia R B₀ B e

/-- 4.6: over the old signature, the risk premises add exactly the compatibility facts. -/
theorem risk_conservative (R : RiskDoc) (h : WellFormedRisk R = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (oldEnvRisk R) []) (hφ : φ.WellFormed (oldEnvRisk R) []) :
  (∀ B, BaseAdmissibleRisk R B → Sat B Γ → φ.denote B []) ↔
  (∀ B, BaseAdmissibleAlt (toAlt R) B → Sat B (compatFacts R) → Sat B Γ → φ.denote B [])

/-- 4.7: alt's conflict and followability theorems, restated over BaseAdmissibleRisk. -/
theorem risk_conflict_free (R : RiskDoc) (h : WellFormedRisk R = true) (certs)
    (hc : riskConflictFreeCheck R certs = true) : RiskConflictFree R
theorem alt_conflict_free_risk (R : RiskDoc) (h : WellFormedRisk R = true)
    (hc : VE.Alternatives.AltConflictFree (toAlt R)) : RiskConflictFree R
theorem risk_followable_sound (R : RiskDoc) (h : WellFormedRisk R = true) (hc : RiskConflictFree R)
    (c : VE.Tableau.Certificate)
    (ok : VE.Tableau.checkCertificate (envAt (inlineTree (toAlt R)) 0)
            (backgroundBaseAlt (toAlt R) ++ riskPremises R ++ R.Γ) (allFollowable (toAlt R)) c = true) :
  ∀ B, BaseAdmissibleRisk R B → Sat B R.Γ →
    ∀ S, DocumentExpansion (inlineTree (toAlt R)) B S → FollowableIn (toAlt R) S
theorem risk_dilemma_witness_sound {α} [DecidableEq α] (R : RiskDoc) (h : WellFormedRisk R = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt (inlineTree (toAlt R)) 0))
    (hb : backgroundValidRisk R M = true) (hΓ : R.Γ.all (fun p => p.eval M []) = true)
    (r : α) (typed : M.inDomain R.alt.chooser r)
    (hd : (notFollowableF (toAlt R)).eval M (tupleVal [r]) = true) :
  ¬ (∀ B, BaseAdmissibleRisk R B → Sat B R.Γ → (allFollowable (toAlt R)).denote B [])

/-- 4.4: admission. The admitted record takes the decision entry's sequence number, and every citation precedes it,
    matches an entry of es by id, sequence number and recomputed hash, and names no estimate withdrawn before the
    decision among the entries of es. -/
theorem admitDecision_sound (R : RiskDoc) (dx : Entry) (es : Log) (d : Decision)
    (h : admitDecision R dx es = .ok d) :
  d.seq = dx.seq ∧ entryHash dx = dx.hash ∧
  ∀ c ∈ d.cited, c.seq < dx.seq ∧
    (∃ x ∈ es, x.id = c.id ∧ x.seq = c.seq ∧ x.hash = c.hash ∧ entryHash x = x.hash) ∧
    withdrawnBefore es dx.seq c.id = false

/-- 4.4 and 4.8: a valid record's regenerated model is a valid alternatives scenario whose base structure satisfies
    the risk premises, and its tables are the regenerated ones. So every document-level certificate over
    BaseAdmissibleRisk applies to every valid decision, and alt's scenario theorems apply to its report. The first
    conjunct comes from the checked step 4.4 V10 (`modelAdmissible`), which frozen `validateAlternatives` leaves to
    its caller. -/
theorem risk_scenario_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision)
    (hv : validateDecision R d = .ok ()) :
  (decisionModel R d).Valid (envAt (inlineTree (toAlt R)) 0) ∧
  validateAlternatives (toAlt R) (decisionModel R d) (decisionRows R d) = .ok () ∧
  backgroundValidRisk R (decisionModel R d) = true ∧
  BaseAdmissibleRisk R (decisionModel R d).asStructure ∧
  (modelTables R (decisionModel R d)).might = (regenerate R d).might ∧
  (modelTables R (decisionModel R d)).leads = (regenerate R d).leads

/-- 4.9: outcomes change only between consecutive candidates. -/
theorem status_piecewise_constant (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (x : Int) (hx : x ∉ candidates R d e ∨ x + 1 ∉ candidates R d e) :
  outcomeAt R d e x = outcomeAt R d e (x + 1)

/-- 4.9: the certified check. `scan` returns the nearest valid status change, or none; everything strictly between
    (or beyond, for none) keeps the current status or is invalid or a conflict. -/
theorem scan_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) (a : String) (ss : List (String × Status)) (s : Status)
    (hcur : outcomeAt R d e (current d e) = .statuses ss) (hs : ss.lookup a = some s) :
  (∀ x, scan R d e dir a = some x →
      Beyond dir (current d e) x ∧
      (∃ ss', outcomeAt R d e x = .statuses ss' ∧ ss'.lookup a ≠ some s) ∧
      ∀ y, Beyond dir (current d e) y → Beyond dir y x → StatusKept (outcomeAt R d e y) a s) ∧
  (scan R d e dir a = none → ∀ y, Beyond dir (current d e) y → StatusKept (outcomeAt R d e y) a s)

/-- 4.9: the record-level lines, one scan per kind. Each certifies only its own kind: a value of the other kind may
    lie strictly between (fixtures k38 and k40). -/
theorem scanInvalid_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) :
  (∀ x t, scanInvalid R d e dir = some (x, t) →
      Beyond dir (current d e) x ∧ outcomeAt R d e x = .invalid t ∧
      ∀ y, Beyond dir (current d e) y → Beyond dir y x → ∀ t', outcomeAt R d e y ≠ .invalid t') ∧
  (scanInvalid R d e dir = none → ∀ y, Beyond dir (current d e) y → ∀ t', outcomeAt R d e y ≠ .invalid t')
theorem scanConflict_sound (R : RiskDoc) (h : WellFormedRisk R = true) (d : Decision) (e : Endpoint)
    (he : e ∈ endpoints d) (dir : Dir) :
  (∀ x, scanConflict R d e dir = some x →
      Beyond dir (current d e) x ∧ outcomeAt R d e x = .conflict ∧
      ∀ y, Beyond dir (current d e) y → Beyond dir y x → outcomeAt R d e y ≠ .conflict) ∧
  (scanConflict R d e dir = none → ∀ y, Beyond dir (current d e) y → outcomeAt R d e y ≠ .conflict)

/-- 4.10: the audit reads only the prefix up to the decision; Q1 and Q2 never read outcomes. -/
theorem snapshot_prefix (R : RiskDoc) (log : Log) (hd : DecisionRef) :
  snapshotOf R log hd = snapshotOf R (logPrefix log hd.seq) hd
theorem verdict_ignores_outcomes (R : RiskDoc) (log₁ log₂ : Log) (hd : DecisionRef) (a : String)
    (hsame : logPrefix log₁ hd.seq = logPrefix log₂ hd.seq) :
  auditQ12 R log₁ hd a = auditQ12 R log₂ hd a
/-- 4.10: an admitted snapshot's decision is the record the decision entry carries, and every citation precedes it
    and matches a prefix entry by id, sequence number and hash. -/
theorem snapshot_no_hindsight (R : RiskDoc) (log : Log) (hd : DecisionRef) (sn : Snapshot)
    (hs : snapshotOf R log hd = .ok sn) :
  sn.decision.seq = hd.seq ∧
  ∀ c ∈ sn.decision.cited, c.seq < hd.seq ∧ ∃ x ∈ sn.entries, x.id = c.id ∧ x.seq = c.seq ∧ x.hash = c.hash

/-- The wire (norms.md 11.4 shape; `decodeRiskSource` decodes the environment with both blocks, the norm objects and
    the active base units; `res.src.R` is the decoded RiskDoc). `decodeSupplied` reports a supplied estimate entry
    without seq or day as `EstimateProvenance: <id> recorded` (4.4 A1). -/
theorem risk_wire_scenario_sound (j : Lean.Json) (res : DecisionReplay) (h : replayDecision j = .ok res) :
  Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
  WellFormedRisk res.src.R = true ∧
  Wire.decodeEntry (j.getObjValD "decision") = .ok res.entry ∧
  Wire.decodeSupplied (j.getObjValD "entries") = .ok res.supplied ∧
  admitDecision res.src.R res.entry res.supplied = .ok res.d ∧
  validateDecision res.src.R res.d = .ok () ∧
  marginLimit res.src.R res.d = .ok () ∧
  res.tables = regenerate res.src.R res.d ∧
  res.conflict = scenarioConflict (toAlt res.src.R) (decisionModel res.src.R res.d) ∧
  (res.conflict = none → res.statuses = statuses res.src.R res.d) ∧
  (∀ e ∈ endpoints res.d, ∀ dir a, res.margin e dir a = scan res.src.R res.d e dir a) ∧
  (∀ e ∈ endpoints res.d, ∀ dir, res.recordInvalid e dir = scanInvalid res.src.R res.d e dir ∧
    res.recordConflict e dir = scanConflict res.src.R res.d e dir)
theorem risk_wire_audit_sound (j : Lean.Json) (res : AuditReplay) (h : replayAudit j = .ok res) :
  Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
  Wire.decodeLog (j.getObjValD "log") = .ok res.log ∧
  res.q12 = auditQ12 res.src.R res.log res.decision res.alternative
theorem risk_wire_conflict_sound (j : Lean.Json) (res : RiskConflictReplay) (h : replayRiskConflict j = .ok res)
    (hv : res.conflictFree = true) :
  Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
  WellFormedRisk res.src.R = true ∧ RiskConflictFree res.src.R
theorem risk_wire_followable_sound (j : Lean.Json) (res : RiskFollowableReplay) (h : replayRiskFollowable j = .ok res)
    (hv : res.followable = true) :
  Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok res.src ∧
  WellFormedRisk res.src.R = true ∧ RiskConflictFree res.src.R ∧
  ∀ B, BaseAdmissibleRisk res.src.R B → Sat B res.src.R.Γ →
    ∀ S, DocumentExpansion (inlineTree (toAlt res.src.R)) B S → FollowableIn (toAlt res.src.R) S
theorem risk_wire_acceptance (j answer : Lean.Json) (h : Run.runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "admission") (hn : Run.usesRiskPath j = true) :
  ∃ id, VE.Bridge.stringField j "id" = .ok id ∧
    Run.RiskAdmissionAnswer id (j.getObjValD "environment") (j.getObjValD "document") answer
```

`RiskAdmissionAnswer` is alt's `AltAdmissionAnswer` with the risk decoder: `risk:*` and `risk:profile:<word>` leaves
are admitted only when equal to the regenerated premises and definitions, and the report consequence is stated over
alt's premises plus `riskPremises` and the two regenerated definitions.

Proof plan:

- `normalize_normal` and `normalize_eval`: by induction on the coefficient list (collecting a name adds its
  coefficients; dropping a zero coefficient drops a zero term).
- `possibleE_iff` and `certainE_iff`: by induction on `nnf c`. The atom cases use the extremal endpoints, which bound
  the form exactly because each quantity occurs once with a nonzero coefficient (the normal form), and, for `=` and
  `≠`, contiguity of the form's values under unit coefficients (a sum of ±1-scaled integer intervals is an integer
  interval). The `∧` case of `possibleE` and the `∨` case of `certainE` combine valuations on disjoint non-point
  quantities (separability).
- `witnessE_sound` follows the same induction. `regenerate_sound` completes a valuation to a case by
  `H := Suff(v)` elsewhere, using `S → N` from validation.
- `lessWorst_strict` and `precaution_has_maximal`: from functionality, domain closure, distinctness and the order
  table, via the profile characterisation (4.5). A minimal element of the induced strict order on the finite set of
  realised profiles is found by well-foundedness on a finite type.
- `risk_expansion`: the carrier `B₀.Carrier ⊕ Fin n`, the severity domain the right summands, `risk__might_lead_to :=
  leads_to` on the image, and the classification by `harm_classes` (well defined by `compatFacts`).
  `risk_conservative` then follows by the reduct lemma for formulas over `oldEnvRisk`.
- `admitDecision_sound`: by the checks of 4.4 A1 and A2. `snapshot_no_hindsight` follows from it, because
  `snapshotOf` runs admission with the prefix as its entries.
- `risk_scenario_sound`: the first conjunct is `VE.Bridge.modelData_valid` applied to 4.4 V10; the others follow
  from V11 and the construction of `decisionData`, whose constant table resolves every signed row (4.4).
- `status_piecewise_constant`: every check of validation (4.4 V1 to V11) and every regenerated cell is a Boolean
  combination of comparisons `c·x + K ⋈ 0` and of `x ⋈ w` against estimate endpoints, whose truth changes only between
  two candidates. Admission and the margin-candidate limit are not part of `outcomeAt`.
- `scan_sound`, `scanInvalid_sound` and `scanConflict_sound`: each scan evaluates every candidate in its direction,
  and `status_piecewise_constant` carries the result to the values between and beyond.
- The route and wire theorems follow alt's chain (decoder soundness, exact regeneration, binding equality, leaf
  admission, checker soundness).

Every proof is audited under the unchanged allowlist.

### 7.3 The executable `ve_risk_route`

`lean/.lake/build/bin/ve_risk_route <cases.json>`, root `RiskMain.lean`, is a new Lake target, and no frozen file
changes. On raw input it runs the frozen envelope and profile gate and requires `risk@0`, `alternatives@0` and
`norms@0`. It decodes the environment with both blocks and the W6 unit extension (the original complete environment
hashed), the norm objects and the active base units, then runs `WellFormedRisk`. It regenerates `E_risk`, the
inlined document, the alt and risk slot premises and every conflict target and followability formula, and delegates
every checker call to the unchanged alt and W1 functions on the regenerated data.

| Kind | Extra input | Output |
|---|---|---|
| `risk-elaborate` | none | `E_risk`, the inlined document (canonical), `premises` (`alternatives:*`, `risk:*`, `background`, layers), `conflict_targets`, `followable`, `legend`, `unranked_severities` |
| `risk-decision` | `decision`: the decision entry, whose `content` is the record; `entries`: the supplied entries (3.3) | a diagnostic; or the CONFLICT witness; or `tables` (with witnesses), `statuses`, `worst_cases`, `margins` (per alternative, endpoint and direction), `record_invalid` and `record_conflict` (per endpoint and direction), the report lines, `conditional_on`, `decision_record_id` |
| `risk-conflict` | `packages` per target over `Background_baseAlt ++ riskPremises`, or `witness` | CONFLICT-FREE / CONFLICT / UNKNOWN |
| `risk-followable` | `certificate` or `witness` (model, rows, chooser), after a CONFLICT-FREE result for the same source | FOLLOWABLE / DILEMMA / UNKNOWN / `not computed` |
| `risk-audit` | the log, a decision reference, the queried alternative (or none, to use the decision's `taken` entry) | Q1, Q2, procedure lines, Q3 |
| `risk-certificate` | `premises`, `conclusion`, `certificate` over `backgroundAlt ++ riskPremises ++ layer premises ++ premises` | `valid`, `conditional_on` |
| `admission` | W2 document using risk words | as alt's `admission`, with `risk:*` leaves |

Cases without the `risk` block delegate unchanged to `ve_alternatives_route`'s `runCase`. A malformed risk input never
falls back after a failed decode. Python's proof search consumes `risk-elaborate` output, and Python holds no
elaborator or regenerator of its own.

### 7.4 What is not claimed

- **Rendering.** No theorem covers the rendered reasons, witness sentences, margin sentences, worst-case wording or
  alt's diagnosis classification. Lean certifies the tables, witnesses, statuses, candidates and scans, and the
  prose is untrusted.
- **Completeness.** Document checks keep UNKNOWN, and the broader-class cost of alt 4.2 carries over.
- **Q3.** Q3 is computed by the route with no theorem beyond its decoder.
- **Standalone supersession.** In `risk-decision`, withdrawal is judged on the supplied entries that precede the
  decision (1.4). An earlier supersession the caller omits is not detected, and the result is conditional on the
  supplied entries. The audit judges withdrawal on the authenticated log prefix (`WithdrawnEntry`, NOT REPLAYABLE). A
  later supersession affects neither (fixtures k16, k39).
- **Truth of the inputs.** Nothing is claimed about whether estimates, conditions or stated cells are true, whether
  the alternative list is complete, whether the policy's classification is right, or whether the harm list covers
  every harm. Every result is conditional on the named ids.
- **Joint possibility** and **robustness to several estimates moving at once**.
- **The English surface** (item 3) and **reader comprehension** beyond the proxy probe (W8).
- **Stages B and C**, and **combination with `soft-norms@0`**.

## 8. Acceptance fixtures for item 1

Deterministic, hand-written expected results, required from the Lean route and, for surface and dispatch, from
Python (`tests/test_risk*.py`, the `risk` conformance family). Section 8.1 states each fixture's environment, rule
set, record, log or structure and scope without its expected result, and 8.2 gives the expected results. The
statement review protocol: each reviewer derives the expectation of every fixture from 8.1 and sections 4 to 6 before
reading 8.2.

### 8.1 Definitions

**Environment `agent-ops`** (plan 9.1):

- sorts `agent` (chooser), `action` and `harm`; the risk block adds the fresh sort `severity`;
- base predicates `available(action, agent)`, `leads_to(action, harm)`, `inaction(action)`, `taken(action)` and
  `confirmed(action)` "the user has confirmed {0}";
- regulated `permitted(action)` (permission, allow by default, act `{0} be performed`) and `required(action)`
  (obligation, deny by default, dual `permitted`);
- harm constants `data_loss` "data loss", `server_outage` "a server outage", `job_failure` "a job failure",
  `task_delay` "a task delay" and `task_abandonment` "task abandonment";
- the alternatives block: chooser `agent`, action `action`, harm `harm`, `available`, `leads_to`, `outcomes:
  signed`, `performed {permitted, required}`, `inaction`, `taken`;
- W6 unit `gb` (scale 1, display decimal, label "GB");
- the risk block of 3.1;
- rules 1 to 3 of 2.5.

`agent-ops-fine` is `agent-ops` with `gb` at scale 10.

**Log `L17`**, the entries decision 17 cites (the contents are 2.5's rendering):

| Seq | Id | Kind |
|---|---|---|
| 25 | S1 | setting `memory_limit` 7 GB of `run_limited` |
| 26–29 | C1–C4 | conditions |
| 30–33 | T1–T4 | statements |
| 34–37 | T5–T8 | statements |
| 38 | E1 | estimate: `peak_memory` 6–12 GB (memory profiler 2.3, statistical) |
| 39 | 39 | estimate: `free_memory` 4–10 GB (the scheduler, calculation: "a second job is scheduled during the run") |
| 40 | E2 | estimate: `free_memory` 8–10 GB (server monitor, observation) |
| 41 | D17 | the decision: chooser `build_agent` "the build agent", with alternatives `run` (kind `run`), `run_limited` (kind `run_limited`), `ask` (kind `ask`) and `nothing` (inaction, "not running the job"). It has quantities `peak_memory`, `free_memory` and `memory_limit`, cites S1, C1–C4, T1–T8, E1 and E2, and has no facts |
| 42 | 42 | taken: D17, `run_limited` |
| 57 | 57 | outcome: D17, `server_outage` observed, `free_memory` measured 5 GB (server monitor, observation) |

**Log `L18`** is `L17` up to entry 41 without entry 39 and continues:

- 42: taken, D17, `ask`;
- 44: instruction from the user, "run it without a limit";
- 45: decision `D18`. Its chooser is `build_agent_18` ("the build agent at decision 18"), and its alternatives are
  `run`, `run_limited` and `nothing`. It cites S1, C1–C4, T2, T4, T5, T6, T8, E1, E2 and 44, and has the fact
  `confirmed(run)` citing 44.

**Environment `cell-env`**: `agent-ops` with an empty rule set (so every alternative is permitted by default) and
`unexamined: "possible"`. It has no `always_possible`, kinds or requirements, and adds the reserved W6 tag
`dimensionless`. Record template `Dx`: chooser `the_agent`, alternatives `act` ("acting") and `nothing` (inaction),
and the quantities, estimates and sources stated per fixture. The fixture's cell is (`act`, named harm).

**Environment `asimov-risk`**:

- sorts `robot` (chooser), `action` and `harm`; base `harms_human(harm)` "{0} is a harm to a human being" and
  `lawful(action)` "{0} is lawful";
- regulated `permitted`, `required` and `prevent_required(robot, harm)` (obligation, deny by default, act
  `{0} prevent {1}`);
- the alternatives block as alt's `asimov-v2` (alt 8.1), with `outcomes: signed`, `decided_by: "Asimov case
  annotator"`, `performed {permitted, required}`, `inaction` and `taken`;
- the risk block per variant, written by the annotator: severity sort `severity`, classes `fatal` > `injuring` set by
  "the Asimov case annotator", and `unexamined: "possible"`.

Variant A1 has the harm constants `death` "the person's death" (fatal) and `bruising` "the person's bruising"
(injuring). Variant A2 has `p_death` "P's death" (fatal) and `q_injury` "Q's injury" (injuring). Records use the
robot `R` and facts `harms_human(h)` for every harm constant, citing the annotator's statement entry.

A record used with a variant of its environment or rule set is bound to that variant: its `policy` pair, and every
hash that depends on it, is recomputed. A record that a fixture changes gets its decision entry's hash recomputed.

| # | Environment, rules | Record, log or structure | Scope |
|---|---|---|---|
| k1 | `cell-env` | `Dx` with E1 `peak_memory` 6–12 GB, E2 `free_memory` 8–10 GB, and the necessary condition "acting cannot lead to a server outage unless the peak memory is greater than the free memory" | cell (`act`, `server_outage`) |
| k2 | `cell-env` | (i) E1 11–12 GB, E2 8–10 GB, and the sufficient condition "if the peak memory is greater than the free memory, acting leads to a server outage"; (ii) E1 6–8 GB, E2 8–10 GB, and the necessary form of (i) | cell |
| k3 | `cell-env` | E1 6–12 GB and the necessary condition "acting cannot lead to a server outage unless both the peak memory is greater than 8 GB and the peak memory is less than 11 GB" | record |
| k4 | `cell-env` | E1 6–12 GB, E2 8–10 GB, the setting `memory_limit` 7 GB of `act`, and the exact condition "acting leads to a job failure exactly when both the peak memory is greater than the memory limit and the free memory is greater than the memory limit" | record; cell |
| k5 | `cell-env` | dimensionless `q` from 0 through 1, and the exact condition on (`act`, `job_failure`) `["eq", ["scale", "dimensionless", "2", ["quantity", "q"]], ["decimal", "dimensionless", "1"]]`; the same with `not` around it | record; the Lean statement |
| k6 | `cell-env` | dimensionless `q` 6–8 and `r` 2–6; on (`act`, `job_failure`), sufficient "q is greater than 5" and necessary "r is less than 5" | record |
| k7 | `agent-ops` | D17 plus the statement T9 at seq 24, cited: "Running the job with the memory limit might lead to a server outage." | record |
| k8 | `agent-ops` | D17 without C1 and without T1 | record; decision report |
| k9 | (a) `agent-ops` with `more_severe` [[severe, serious], [serious, minor], [minor, severe]]; (b) `sev-unranked`: `agent-ops` with harm constants `leak` "a data leak" and `damage` "property damage" only, classes `privacy`, `property`, no edges, `unranked` [[privacy, property]], `harm_classes` [[leak, privacy], [damage, property]], `unexamined: "possible"`, no `always_possible` or `combination`, no kinds or requirements, rule 2 only | (a) none; (b) chooser `the_agent`, alternatives `a` ("option a"), `b` ("option b"), `nothing` (inaction); statements: a might lead to leak, a cannot lead to damage, b might lead to damage, b cannot lead to leak, nothing might lead to leak, nothing might lead to damage | environment; decision report |
| k10 | `agent-ops` | D17 from `L17` | decision report with margins |
| k11 | `agent-ops` | D18 from `L18`; and the shared-server variant of rule 2 (plan 9.2) | decision report |
| k12 | `agent-ops` | D17 with E1 replaced by E1p: "The peak memory of the job equals 12 GB." (an estimate with `lo = hi = 12`, memory profiler) | decision report |
| k13 | `agent-ops` | audit of D17 on `L17`, queried alternative from entry 42; then the same with `use_all_recorded: true` | audit |
| k14 | `agent-ops` | `L17` with entry 42 taking `run` | audit |
| k15 | `agent-ops` | D17 citing also `(57, 57, hash)` | record; audit |
| k16 | `agent-ops` without `combination` | (a) D17 citing also entry 39; (b) the same with a `supersession` entry for 39 at seq 50 | record |
| k17 | `agent-ops` | D17 with E1's estimator removed; with its support removed (in these two, E1's entry hash and D17's citation of it are recomputed); with E1 carried without `seq` and `day` | record |
| k18 | `agent-ops` | D17 without `run_limited`, S1, C2, C3 and T6 | record |
| k19 | `agent-ops`, `asimov-risk` | each wording of 2.1 and 2.2 once; `may lead to`, `does not lead to`, `is safer than`, `every action available to that agent cannot lead to data loss`, `certainly leads to`, `prevents` in a risk environment, `might not lead to` as a record statement, and a rule with `… cannot lead to data loss unless …`; rules 2 and P3 of 2.5 | surface |
| k20 | `asimov-risk` A1 | record: `push` ("pushing the person"), `nothing` ("doing nothing", inaction); statements: nothing leads to death, nothing cannot lead to bruising, push might lead to bruising, push cannot lead to death. Rule sets {1, 2}, {1, 2, 3} (record and document) and {1, 2x, 3} | decision report; document |
| k21 | `asimov-risk` A2 | record: `rescue_p`, `rescue_q`, `nothing` (inaction); statements: rescue_p might lead to p_death, rescue_p leads to q_injury, rescue_q leads to p_death, rescue_q cannot lead to q_injury, nothing leads to p_death, nothing leads to q_injury. Rule sets {1, 2x, 3} and {1, 3} | decision report |
| k22 | `law3`: `asimov-risk` with classes `severe` > `minor` (annotator), harm constants `destruction` "the robot's destruction" (severe) and `damage` "the robot's damage" (minor), `unexamined: "possible"` | (a) alternatives `fire` ("the fire rescue"), `water` ("the water rescue"), `nothing` (inaction); facts `lawful(fire)`, `lawful(water)`; statements: fire might lead to destruction, fire cannot lead to damage, water might lead to damage, water cannot lead to destruction, nothing cannot lead to destruction, nothing cannot lead to damage. Rule sets {L, P3} and {L}. (b) (a) plus `combined` ("the combined rescue"), lawful, which might lead to destruction and might lead to damage; rule sets {L, PS} | decision report |
| k23 | all | every existing fixture, identity, certificate and wire hash; `agent-ops` with and without the risk block; 300 random P2-only records; 300 random P2-only structures with unclassified harm elements | identity; property |
| k24 | `cell-env` | dimensionless `q` 0–10, one cell each: (a) only "if q is greater than 5, acting leads to a job failure"; (b) only "acting cannot lead to a job failure unless q is at least 0"; (c) only the statement "acting might lead to a job failure"; (d) the statement "acting leads to a job failure" and "acting cannot lead to a job failure unless q is greater than 5"; (e) "if q is greater than 5, …" and "if q is less than 2, …" on one cell | cell; record |
| k25 | `cell-env` | the necessary condition "acting cannot lead to a job failure unless it is not the case that q equals 5" with dimensionless `q` from 3 through 7, from 6 through 7, and exactly 5; and the rewrite "unless either q is less than 5 or q is greater than 5" for each | cell; record |
| k26 | (a) `asimov-risk` A1 whose risk block names `harm` as the severity sort; (b) A1 as defined | none | environment |
| k27 | `cell-env` | (a) dimensionless `q` 6–8 and `r` 2–4, with sufficient "q is greater than 5" and necessary "r is less than 5" on (`act`, `job_failure`), margins of `r`'s upper bound; (b) dimensionless point estimate `q` = 5 and the necessary condition "acting cannot lead to a job failure unless either q is less than 3 or q is greater than 7", margins of both endpoints; (c) `agent-ops` D17, margins of E2's lower bound | margins |
| k28 | `agent-ops`, `agent-ops-fine` | D17 (on the fine grid, E1 6.0–12.0, E2 8.0–10.0, S1 7.0) | margins of E2's lower bound for `run_limited` |
| k29 | `asimov-risk` A2 | the k21 record; the input "Rescuing P prevents P's death." | decision report; surface |
| k30 | `asimov-risk` A2 with rule 8 only, fulfilment `avoids`; then `excludes` | the k21 record | decision report; document |
| k31 | `agent-ops` with rule 2 only | a structure `M31`: chooser `r` with actions `a`, `a2`, `b`; harm elements the five constants and one more element `u` (no constant, no class); severity domain the three classes; `risk__might_lead_to` = {(a, u), (b, task_delay)}; `leads_to` empty; `risk__class` the five ground facts; `confirmed` empty. Also a record naming `u` as a harm | document-level evaluation; c9's paraphrase; record |
| k32 | `agent-ops` | two logs identical up to entry 41: (a) both take `run_limited` at 42, and `L17a`'s entry 57 observes `server_outage` while `L17b`'s entry 57 observes no harm; (b) `L17` against `L17c`, whose entry 42 takes `run` | audit |
| k33 | `agent-ops` | (a) D17 also citing the setting S2 at seq 23, "The memory limit equals 5 GB." of `run`; (b) D17 also citing the estimate E3 at seq 22, `memory_limit` from 6 GB through 8 GB (memory profiler 2.3, statistical) | record |
| k34 | `cell-env` | dimensionless `q` from 0 through 1, and the necessary condition on (`act`, `job_failure`) `["eq", ["add", "dimensionless", ["quantity", "q"], ["scale", "dimensionless", "-1", ["quantity", "q"]]], ["decimal", "dimensionless", "1"]]` ("q minus q equals 1") | cell; the Lean statement |
| k35 | (a) `agent-ops` whose `E` adds the action constant `run` "running the job"; (b) the action constant `deploy` "deploying the job" instead; (c) the chooser constant `ops_agent` "the operations agent" instead; (d) the chooser constant `build_agent` "the build agent" instead; (e) `agent-ops` | (a) to (d) D17; (e) D18 from `L18` with its fact `confirmed(run)` replaced by `confirmed(data_loss)` (its entry hash recomputed) | record; decision report |
| k36 | `cell-env-22`: `cell-env` with the 22 harm constants `h1` … `h22`, each `minor`, in place of its five | chooser `the_agent`, alternatives `a1`, `a2`, `a3` and `nothing` (inaction); dimensionless `q` from 0 through 100 and `r` from 0 through 1; with `Kᵢ = 10000 + 10i` for `0 ≤ i < 44`, 88 necessary conditions, one on each of the 88 cells: `q + r < Kᵢ` and `r < Kᵢ − 10` for each `i` | record; `outcomeAt` of `q`'s lower bound at 12 and 13 |
| k37 | `agent-ops` | the two rewrites of 2.3 of "every action available to that agent cannot lead to `<harm>`", as formulas with `r` D17's chooser, for `<harm>` a server outage and data loss | evaluation on D17's decision model |
| k38 | `cell-env` with the rules X1 "Every action must not be performed, if that action might lead to a server outage." and X2 "Every action may be performed, if that action might lead to a job failure.", with no precedence between them | `Dx` with dimensionless `q` from 6 through 8 and `r` from 2 through 3; on (`act`, `task_delay`) the sufficient condition "q is greater than 5" and the necessary condition "r is less than 5"; on (`act`, `server_outage`) the necessary condition "r is greater than 3"; the statement "nothing cannot lead to a server outage" | margins of `r`'s upper bound |
| k39 | `agent-ops` | `L17w`: `L17` with entry 39 replaced by a `supersession` entry `W39` (seq 39) withdrawing E1. The later entries' `prev` and `hash` follow the chain, and D17 cites E2's new hash. `L17s`: `L17` plus a `supersession` entry `W50` (seq 50) withdrawing E1. (a) `risk-decision` for `L17`'s D17 with the entries it cites as the supplied entries; (b) the same with `W39` also supplied; (c) the audit of D17 on `L17w`; (d) the audit of D17 on `L17s`, and (a) with `W50` also supplied | record; audit |
| k40 | `cell-env` with k38's rules X1 and X2, with no precedence between them, and the base assertion unit labelled `G`, in strict text: `∀a. risk__might_lead_to(a, server_outage) → risk__might_lead_to(a, job_failure)` ("every action that might lead to a server outage might lead to a job failure") | `Dx` with dimensionless `r` from 2 through 3; on (`act`, `server_outage`) the necessary condition "r is greater than 3"; on (`act`, `job_failure`) the necessary condition "r is greater than 4"; the statement "nothing cannot lead to a server outage" | margins of `r`'s upper bound |
| kC1 | stage C (recorded, not a stage A acceptance fixture) | two chances `p`, `q` with an EL-certified constraint `p + q = 1` and marginal intervals 0%–100% | stage C |

### 8.2 Expected results

- **(k1)** `might`, witness (peak 12 GB, free 8 GB): `fmax(peak − free) = 12 − 8 = 4 > 0`.
- **(k2)** (i) certain (`leads to`): `fmin(peak − free) = 11 − 10 = 1 > 0`; the sufficient condition renders in
  c5's frozen wording, with its legend line (2.4). (ii) ruled out: `fmax(peak − free) = 8 − 8 = 0`, not greater than 0.
- **(k3)** `RiskConditionShared: peak_memory`, with the two rewrites; the second is labelled a change of model.
- **(k4)** Accepted: the point `memory_limit` occurs in two atoms, and `peak_memory` and `free_memory` once each. The
  cell is `might` (`fmax`: 12 > 7 and 10 > 7), not certain (`fmin`: 6 > 7 fails), with witness (peak 12, free 10,
  limit 7).
- **(k5)** `RiskEqualityCoefficient: <condition> q`. In Lean, the endpoint table without the ±1 hypothesis would
  answer "possible" for `2·q − 1 = 0` (`fmin = −1 ≤ 0 ≤ 1 = fmax`) although no integer `q` in 0..1 satisfies it,
  and "not certain" for `2·q − 1 ≠ 0` although every such `q` satisfies it. This is why `UnitCoefficients` is a
  hypothesis of `possibleE_iff` and `certainE_iff`.
- **(k6)** `SufficientOutsideNecessary: act/job_failure`, case (q 8, r 6): the canonical witness of
  `5 − q < 0 ∧ 5 − r ≤ 0` minimises each form.
- **(k7)** `RiskInconsistent: run_limited/server_outage`: a stated `might` on a cell ruled out by C2 under E2
  (`fmax(7 − free) = −1`).
- **(k8)** `run`/`server_outage` is unaddressed and serious, so it is `might` under `always_possible` and listed in
  `unexamined_possible`. `ask`/`task_delay` is unaddressed and minor, so it is `cannot` and listed in
  `assumed_ruled_out` with the build agent. Consequently `ask` might lead to no harm: it beats every other
  alternative, and rule 2 forbids `run`, `run_limited` and `nothing` (`nothing` also by rule 3). `ask` is the only
  clear action. The report shows how an agent's completion choice moves the outcome; it is listed, not prevented
  (plan 14.2).
- **(k9)** (a) `DependencyCycle: minor, serious, severe`. (b) No `less_worst` holds in either direction for any pair,
  so rule 2 forbids nothing, and all three alternatives are permitted by default and clear.
  `unranked_severities` names privacy and property for the pairs (a, b), (a, nothing) and (b, nothing).
- **(k10)** The regenerated cells, as plan 9.2's table:

  | Alternative | Worst case | Tables |
  |---|---|---|
  | `run` | serious | server outage `might` (C1, witness 12, 8); job failure `might` (C4); data loss `cannot` (T5); delay and abandonment ruled out by the build agent |
  | `run_limited` | minor | server outage `cannot` (C2: `fmax(7 − free) = −1`); job failure `might`, not certain (C3; witness peak 12; `fmin(peak − 7) = −1`) |
  | `ask` | minor | task delay `leads` (T1) |
  | `nothing` | minor | task abandonment `leads` (T2) |

  Expected report:

  ```text
  Decision 17 — conditional on E1, E2, S1, C1–C4, T1–T8 and the build agent's ruled-out cells (8 listed).
  running the job: forbidden by rule 2; not clear. Worst case: a server outage (serious). A server outage is not
    ruled out: by C1 it needs the peak memory of the job (6 GB through 12 GB, E1) to be greater than the free memory
    of the server (8 GB through 10 GB, E2), for example 12 GB and 8 GB. Running the job with the memory limit has a
    less severe worst case (a job failure, minor). The user has not confirmed running the job.
    Nearest change: E1's upper bound 8 GB (now 12 GB). No single valid change at E1's lower bound, E1's upper bound
    upwards, E2's lower bound or E2's upper bound.
  running the job with the memory limit: permitted (by default); clear. Worst case: a job failure (minor): by C3 it
    happens exactly when the peak memory is greater than 7 GB, for example 12 GB; not at 6 GB. A server outage is
    ruled out by C2: 7 GB is not greater than the free memory in any case E2 allows.
    Nearest change: E2's lower bound 6 GB (now 8 GB); E1's upper bound 8 GB (now 12 GB). No single valid change at
    E1's lower bound, E2's lower bound upwards, E1's upper bound upwards or E2's upper bound.
  asking the user: permitted (by default); clear. Worst case: a task delay (minor).
    Nearest change: E1's upper bound 8 GB (now 12 GB). No single valid change at the other endpoints and directions.
  not running the job: forbidden by rule 3: it leads to task abandonment (T2), and running the job might not lead to
    it (ruled out by the build agent). No single valid change at any endpoint.
  Clear actions: running the job with the memory limit; asking the user. The policy does not choose between them.
  Record invalid at: E1's lower bound 13 GB, E1's upper bound 5 GB, E2's lower bound 11 GB, E2's upper bound 7 GB
    (RiskRange). No conflict at any candidate.
  default_decided: running the job with the memory limit, asking the user.
  assumed_ruled_out (the build agent): running the job/a task delay, running the job/task abandonment, running the
    job with the memory limit/a task delay, running the job with the memory limit/task abandonment, asking the user/a
    job failure, asking the user/task abandonment, not running the job/a job failure, not running the job/a task delay.
  ```

  At E1's upper bound 8 GB, running the job might lead to no harm, so it beats every other alternative. It becomes
  the only clear action, and rule 2 forbids the memory-limited run and asking the user. At E2's lower bound 6 GB,
  `7 > 6` puts a server outage in the memory-limited run's profile, and asking the user beats it. The candidates for
  E2's lower bound are {6, 7, 8, 9, 10, 11, 12, 13} (k28). Raising E2's lower bound to 12 GB would clear running the
  job, but the record is invalid from 11 GB (`lo > hi`), which is reported as invalid and not as a status change.
- **(k11)** D18: rule 2's guard holds at `run` (the memory-limited run has a less severe worst case), but its
  carve-out applies (`confirmed(run)`), so `run` is permitted by default. `run_limited` is permitted and `nothing` is
  forbidden by rule 3. Clear: running the job, running the job with the memory limit. The report adds "running the
  job is permitted only because the user confirmed it (entry 44); its worst case is still a server outage
  (serious)". Rule 1 does not apply (no severe harm is possible). The shared-server variant is not evaluated:
  **OPEN** Q-consent, pending `borne_by`.
- **(k12)** C3 is certain for `run_limited`/`job_failure` (`fmin(peak − 7) = 12 − 7 = 5 > 0`), so the memory-limited
  run leads to a job failure, and `point_estimates` names E1p for that result. `run`/`server_outage` stays `might`
  (`might` results are not listed). The statuses are as in k10.
- **(k13)** The Q-lines:

  ```text
  Q1  PERMITTED AT DECISION TIME: running the job with the memory limit was clear given E1, E2, S1, C1–C4, T1–T8.
  Q2  DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: 39 was recorded before the decision and not used. Under the
      policy's hull rule free memory is 4 GB through 10 GB; C2 no longer rules out a server outage (7 > 4), rule 2
      then forbids the memory-limited run, and the only clear action is asking the user.
  Q3  a server outage: surprise: ruled out by C2 under E2; the observed free memory (5 GB) is outside E2 (8–10 GB).
      Estimate E2 (server monitor) is contradicted; condition C2 is not (7 > 5).
  Not concluded: that the decision was wrong because a harm followed.
  ```

  The `taken` entry 42 is not flagged. With `use_all_recorded: true`: Q1 unchanged, Q2 unchanged, plus
  `PROCEDURE BREACH: estimate 39 not used (the agent's fault)`. Not NOT REPLAYABLE.
- **(k14)** `FORBIDDEN AT DECISION TIME: running the job was forbidden by rule 2 given …`, whatever entry 57 says.
- **(k15)** Record: `HindsightEntry: 57`. Audit: `Q1 NOT REPLAYABLE: HindsightEntry: 57`. Admission checks hindsight
  first for each citation (4.4 A2), so the audit does not report `MissingEntry: 57`, although entry 57 is not in the
  prefix.
- **(k16)** (a) and (b) are both `ConflictingEstimates: free_memory`: in (b), the supersession at seq 50 comes after
  the decision (seq 41), so entry 39 is not withdrawn (4.4 A2).
- **(k17)** `EstimateProvenance: E1 estimator` (4.4 V3); `EstimateProvenance: E1 support` (V3); `EstimateProvenance:
  E1 recorded` (A1, reported when the supplied entry is decoded, before any citation is matched). Without the
  recomputed hashes, the first two would be `AlteredEntry: E1`.
- **(k18)** `RequiredAlternativeMissing: run_limited (with run)`.
- **(k19)**
  - Exactly one derivation per accepted wording, and each paraphrase as in 2.1 and 2.2. c5's frozen wording
    parses, renders and round-trips, with no `(wording pending)`; its first-probe trailing form is rejected with
    the rewrite to the frozen form.
  - Rejections with their rewrites: `may lead to` → `might lead to`; `does not lead to` → both rewrites;
    `is safer than` → `has a less severe worst case than`; the `every … cannot` sentence → both scoped rewrites;
    `certainly leads to` → `leads to`; `prevents` → `might prevent`; `might not lead to` as a record statement →
    `RiskStatementForm` with its rewrite; the rule with `… unless …` → the carve-out reading, the condition wording
    being record-only.
  - Rule 2 of 2.5 has one derivation with alt's binder. Rule P3's verb-phrase coordination is accepted only if it has
    exactly one derivation; otherwise it is rejected, and k22 uses its strict text.
- **(k20)** Under {1, 2}, pushing is forbidden by rule 1 (it might lead to the bruising), and doing nothing by rules 1
  and 2. The decision has no clear action (NONE-PERMITTED), and the document is a DILEMMA with this record as
  witness, since {1, 2} is CONFLICT-FREE. Under {1, 2, 3}, the record is evaluated first: pushing's profile is
  {injuring} and doing nothing's is {fatal}. Pushing is not beaten, so rule 3 permits it over rule 1, and rule 2
  does not apply to it (pushing does not certainly lead to the bruising). Clear: pushing. The document under {1, 2,
  3} is CONFLICT. The witness is a structure in which both alternatives' worst cases are fatal and doing nothing
  certainly leads to a death that the other might avoid. Rule 3 then permits doing nothing (no alternative has a
  less severe worst case) and rule 2 forbids it (it allows the death), with no precedence between them. Under
  {1, 2x, 3}: CONFLICT-FREE, not FOLLOWABLE. A structure with two alternatives, each certain to lead to a different
  harm to a human being that the other avoids (in A1's vocabulary, the death and the bruising), gives
  NONE-PERMITTED: rule 2 forbids each (it allows its harm) over rule 3, and rule 1 forbids both. The checker shows
  trolley problems; it does not resolve them. The record under {1, 2x, 3}: pushing is clear, as under {1, 2, 3} (rule
  3 permits it over rule 1, and rule 2x does not apply to it), and doing nothing is forbidden by rules 1 and 2x (it
  allows the death, which pushing avoids).
- **(k21)** Under {1, 2x, 3}, the profiles are `rescue_p` {fatal, injuring}, `rescue_q` {fatal} and `nothing`
  {fatal, injuring}. Nothing beats anything (no class is above fatal), so rule 3 permits all three, and rule 2
  overrides it:
  - `rescue_q` allows P's death, which `rescue_p` might avoid;
  - `rescue_p` allows Q's injury, which `rescue_q` avoids;
  - `nothing` allows both.

  NONE-PERMITTED, a DILEMMA. Stage A cannot weigh a possible death against a certain injury, and the report says so.
  Under {1, 3}, all three are permitted and clear, a tie at fatal: "The policy does not choose among them."
- **(k22)** (a) Under {L, P3}, `fire` is forbidden by P3 (`water` is lawful, with profile {minor} below {severe}).
  `water` is not forbidden by P3 (`fire` has a more severe worst case, and `nothing` is not lawful), and `nothing` is
  forbidden by L. Clear: water. Under {L} alone, `fire` and `water` are clear (the README's current result). (b)
  Under {L, PS}, `combined` is forbidden (the possible harms of `water` and of `fire` are each a strict subset of
  `combined`'s). `fire` and `water` are incomparable by inclusion, so neither is forbidden. Clear: fire, water.
  Both rule sets are attributed narrowings, listed under `narrowings`.
- **(k23)** Every existing fixture, identity, certificate and wire hash is unchanged byte for byte, and the risk block
  changes `environment_id`. On every random P2-only record the report has a clear action. On every random P2-only
  structure some alternative of every chooser is beaten by none (`precaution_has_maximal`, as differential
  evidence).
- **(k24)**
  - (a) `might` (`N = ⊤`), not certain (q = 3 fails the condition).
  - (b) `might`, not certain (`S = ⊥`), although the necessary condition holds in every case.
  - (c) `might`, not certain, and `might not lead to` holds, witnessed by a case without the harm (`S = ⊥`).
  - (d) `RiskInconsistent: act/job_failure`, case q 0 (the witness of `⊤ ∧ q − 5 ≤ 0`: the minimising endpoint of
    `q − 5`).
  - (e) `RiskTwoSources: act/job_failure sufficient`, with the rewrite "if either q is greater than 5 or q is less
    than 2, acting leads to a job failure".
- **(k25)** The necessary condition is the one atom `q − 5 ≠ 0`. With q 3–7 it is possible but not certain
  (`fmin = −2`, `fmax = 2`). With q 6–7 it is certain (`fmin = 1 > 0`). With q exactly 5 it is impossible. So the
  cell is `might` in the first two boxes and `cannot` in the third, and never certain (`S = ⊥`). The rewrite is
  `RiskConditionShared: q` for q 3–7 and q 6–7. For the point q = 5 it is accepted and gives `cannot` again (points
  may repeat). Both `cannot` results at q = 5 rest on the point estimate of `q`, so `point_estimates` names it for
  each (4.9).
- **(k26)** (a) `RiskSeverityNotFresh: harm`: domain closure would bound the harm sort in the old vocabulary. (b)
  Accepted. The one new old-vocabulary fact, "the person's death is not the person's bruising", is `compatFacts`,
  the hypothesis of `risk_expansion`, and no other old-vocabulary result changes (k23).
- **(k27)** (a) The record is valid, and the cell is certain (`fmin(q) = 6 > 5`). At `r`'s upper bound, `record
  invalid at 5 (SufficientOutsideNecessary: act/job_failure)`, case (q 8, r 5), and no single valid change upwards;
  downwards, `record invalid at 1 (RiskRange)`. (b) At the upper bound, `record invalid at 6
  (RiskConditionShared: q)`; at the lower bound, `record invalid at 4 (RiskConditionShared: q)`; in the other
  directions, `record invalid (RiskRange)` at 4 and 6 respectively. (c) `record invalid at 11 GB (RiskRange: E2)`.
  None of these is reported as a status change.
- **(k28)** On the 1 GB grid the nearest change is at 6 GB, and on the 0.1 GB grid at 6.9 GB, not at the threshold
  7 GB. The candidates include 6 (resp. 6.9) as a grid neighbour of the threshold. A search at thresholds only would
  find no change.
- **(k29)** `prevents(rescue_p, p_death)` holds (rescuing P might not lead to P's death, and rescuing Q leads to it),
  and renders "Rescuing P might prevent P's death". The input "Rescuing P prevents P's death." is rejected with that
  rewrite. `excludes(rescue_p, p_death)` is false, and `excludes(rescue_q, q_injury)` is true.
- **(k30)** Both duties hold, since each harm is avoidable (some action might not lead to it). Under `avoids`,
  rescuing P discharges the death duty and rescuing Q the injury duty, but no action discharges both: no clear action,
  JOINTLY-UNDISCHARGEABLE(`prevent_required(R, p_death)`, `prevent_required(R, q_injury)`), and a document DILEMMA.
  Under `excludes`, no alternative discharges the death duty: UNDISCHARGEABLE(`prevent_required(R, p_death)`), and a
  document DILEMMA. `excludes` is listed under `narrowings` as the annotator's attributed choice.
- **(k31)** `M31` passes `backgroundValidRisk` (`u` has no class; the named constants have theirs). `a2` does not
  beat `a` (no classified witness), and `a` and `b` are not comparable either way. `a2` beats `b`, so rule 2 forbids
  `b` only. The rendering says "not comparable: u has no class" for (a2, a) and (a, b). A record naming `u` is
  `UnknownHarm: u`. c9's paraphrase (2.1) agrees with the formula on `M31`. For `a2 has a less severe worst case
  than a`, it is false: `a` might lead only to `u`, which is not a classified harm (draft 1's paraphrase, without the
  classified witness, was vacuously true here, since `a2` might lead to no harm). For `a has a less severe worst
  case than b`, it is false: `a`'s possible harm `u` has no class. For `a2 has a less severe worst case than b`, it is
  true: `b` might lead to a task delay, classified minor, and `a2` might lead to no harm.
- **(k32)** (a) Q1 and Q2 are identical: PERMITTED AT DECISION TIME and DIFFERENT VERDICT WITH ALL RECORDED
  ESTIMATES (39) in both. Q3 differs: a surprise in `L17a`, no observed harm in `L17b`. (b) Q1 differs: `L17` gives
  PERMITTED AT DECISION TIME (`run_limited`), and `L17c` gives FORBIDDEN AT DECISION TIME (`run`), because the
  queried alternative differs. For either fixed queried alternative both logs give the same verdict
  (`verdict_ignores_outcomes`).
- **(k33)** (a) and (b) are both `RiskSettingTwice: memory_limit`, with the rewrite "declare one quantity per
  alternative", from 4.4 V4, before the box is built. Without the check, the box would have two entries for
  `memory_limit` (7 and 5 GB, or 7 GB and 6–8 GB).
- **(k34)** The normal form is `−1 = 0`: `q`'s collected coefficient is 0, so `q` does not occur. The necessary
  condition is impossible (`fmin = fmax = −1`), so the cell is `cannot`. Left uncollected, as `[(q, 1), (q, −1)]`
  with constant −1, the form has `fmin = −2` and `fmax = 0`, passes separability and the ±1 rule, and the table
  would answer "possible" although no case satisfies it. This is why every atom holds a `NormLinForm` (4.2), as k5
  is why `UnitCoefficients` is a hypothesis.
- **(k35)**
  - The decision model's constant table (4.4) has, besides the constants of `E_risk`, one entry per record-local name:
    `build_agent` denotes the record's chooser, and `run`, `run_limited`, `ask` and `nothing` denote their
    alternatives. In (a), `run`'s entry is also the constant's. D17's 20 signed rows (four alternatives, five harms)
    resolve through it, so `rowsTypedB` passes at 4.4 V11 in (a), (c) and k10. Without the record-local entries,
    every row of an alternative that is not a policy constant would be untyped, and V11 would reject the record.
  - (a) Accepted: the constant `run` denotes D17's alternative `run`, and the report is k10's.
  - (b) `RiskConstant: deploy` (4.4 V10): no alternative interprets it.
  - (c) Accepted: the chooser domain is {`build_agent`, `ops_agent`}, `ops_agent` has no available action (alt's E2
    admits a chooser with no alternative), and the report is k10's.
  - (d) `RiskConstant: build_agent` (4.4 V1): the record's chooser would be the constant's element.
  - (e) `RiskFact: confirmed` (4.4 V10): `data_loss` is not an element of the action sort.
- **(k36)** Accepted, every alternative permitted by default and clear. The candidates per endpoint are 138 for `q`'s
  lower bound, 138 for its upper bound, 139 for `r`'s lower bound and 163 for its upper bound, all within 256.
  Neither 12 nor 13 is a candidate of `q`'s lower bound (those are −1, 0, 1, 99, 100, 101 and `Kᵢ − 1`, `Kᵢ`,
  `Kᵢ + 1`). With `q`'s lower bound moved to 12, `r`'s lower bound would have 224 candidates, and moved to 13 it
  would have 268. The limit is checked once on the original record and is not part of `outcomeAt` (4.9), so
  `outcomeAt` gives the same statuses at 12 and at 13, as `status_piecewise_constant` requires. Draft 1 re-applied
  the limit inside `outcomeAt`, which made 12 valid and 13 invalid: a counterexample to its theorem.
- **(k37)** For a server outage, the "every … not" formula is false (running the job might lead to it), and the "not
  every" formula is true (running the job with the memory limit cannot lead to it). For data loss both are true: no
  alternative might lead to it (T5–T8). Draft 1's "not every" rewrite, `∃a. available(a, r) ∧ might(a, h)`, is false
  for data loss: it was the negation of "every … not".
- **(k38)** The record is valid and conflict-free. A server outage is ruled out for acting (`fmin(3 − r) = 0`, not
  below 0), so X1 does not apply, and X2 permits both alternatives (a job failure is unexamined, hence possible).
  Both are clear. The candidates of `r`'s upper bound are 1 to 6.
  - Upwards: at 4 the record is a conflict (`fmin(3 − r) = −1`, so a server outage is possible for acting, and X1
    forbids acting while X2 permits it, with no precedence). At 5 it is invalid (`SufficientOutsideNecessary:
    act/task_delay`). `scanConflict` returns 4, and `scanInvalid` returns 5, which certifies that 4 is not invalid.
    Both lines are reported: "Conflict at: r's upper bound 4" and "Record invalid at: r's upper bound 5
    (SufficientOutsideNecessary: act/task_delay)".
  - Downwards: record invalid at 1 (`RiskRange`), and `scanConflict` returns none.
  - "No conflict at any candidate" is not rendered, and there is no single valid change in either direction. A
    single scan stopping at the first value of either kind would stop at the conflict and could not certify the
    invalid value 5 as the nearest.
- **(k39)**
  - (a) Accepted, with k10's report. The supplied entries hold no supersession, so the result is conditional on
    them (7.4).
  - (b) `WithdrawnEntry: E1` (4.4 A2): `W39` precedes the decision.
  - (c) `Q1 NOT REPLAYABLE: WithdrawnEntry: E1`: the authenticated prefix holds `W39`.
  - (d) The audit's Q1 and Q2 are k13's, and the standalone record is accepted as in (a): `W50` comes after the
    decision, so it affects neither.
- **(k40)** The record is valid and conflict-free. Both of `act`'s addressed cells are ruled out (`fmin(3 − r) = 0`
  and `fmin(4 − r) = 1`, neither below 0), and a server outage is ruled out for `nothing` by its statement, so `G`
  holds. X1 does not apply. X2 permits `nothing` (its job failure is unexamined, hence possible), and `act` is
  permitted by default. Both are clear. The candidates of `r`'s upper bound are 1 to 5: 1 to 4 from the estimate's
  endpoints, and 2 to 5 from the thresholds 3 and 4.
  - Upwards: at 4 a server outage becomes possible for acting (`fmin(3 − r) = −1`), while a job failure stays ruled
    out (`fmin(4 − r) = 0`). So `G` fails on the decision model, and the record is invalid at 4.4 V11
    (`InvalidModel("alternatives", "premise G fails")`). At 5 a job failure is possible too (`fmin(4 − r) = −1`), so
    `G` holds again and the record is valid. It is a conflict, however: X1 forbids acting and X2 permits it, with no
    precedence. It stays a conflict beyond 5. `scanInvalid` returns 4, and `scanConflict` returns 5, which certifies
    that 4 is not a conflict. Both lines are reported: "Record invalid at: r's upper bound 4", with that diagnostic,
    and "Conflict at: r's upper bound 5".
  - Downwards: 2 changes nothing, the record is invalid at 1 (`RiskRange`), and `scanConflict` returns none.
  - "No conflict at any candidate" is not rendered, and there is no single valid change in either direction. A
    single scan stopping at the first value of either kind would stop at the invalid value 4 and could not certify
    the conflict at 5 as the nearest. This is the order k38 cannot show: the record becomes valid again farther out
    only because the assertion unit `G` is evaluated at V11 (12.1, last item).
- **(kC1)** The box range of `p + q` is 0%–200%. The result is labelled conservative, or computed over EL's certified
  joint region, where the sum is exactly 100%.

### 8.3 Regression suites

- Alt's 8.3 suites are repeated on environments carrying the risk block (identical statuses, witnesses and premise
  lists plus the risk slot premises).
- The Lean `risk-elaborate` output round-trips through Python's dispatch, and its certificates replay in Lean on
  1,000 generated risk policies.
- `possibleE`/`certainE` are checked differentially against brute-force enumeration of the box on 10,000 random
  small separable, unit-coefficient conditions (Python and Rust); non-separable and non-unit conditions are rejected
  in all three.
- Every diagnostic of 6 is produced by the Lean route on a hand-written input.
- Margins are compared with brute-force evaluation of every grid value in a window around each endpoint on 200
  random records (plan 12, item 3).

## 9. Limits, regeneration, Rust and trust

Per decision (plan 11, checked before evaluation, each overflow `ResourceLimit: risk <limit>` with the limit named and
never a truth value): 16 alternatives, 32 harm constants, 64 estimates and settings, 128 conditions and statements,
`MAX_NODES` (10,000) per condition after normalisation, 16 classes, and 256 margin candidates per endpoint. All but the
last are checked at admission (4.4 A1). The margin-candidate limit (`ResourceLimit: risk margin candidates`) is
checked once, on the admitted and valid record, and never inside `outcomeAt` (4.9). The logs of an audit hold at most
4,096 entries. Stage B's 8 bands are not in stage A.

`E_risk`, the inlined document, the slot premises, the box, the regenerated tables, the decision model, the candidates
and every package are regenerated from decoded declarations at every trusted site. Nothing regenerated is accepted
from the wire.

**Trusted (Lean, proved from raw JSON under the unchanged allowlist):** the risk block, entry and record decoders, W6
decimal lowering (reused), condition normalisation and the endpoint evaluator with its witnesses, record admission,
validation and regeneration, the severity closure, the inliner, the slot generator, the decision-model builder and
its validity check, the margin candidates, the candidate limit and the three scans (the certified check, 4.9),
snapshot admission and Q1/Q2, and the `ve_risk_route` executable.

**Untrusted:** Python's shape check, surface and dispatch; the rendering of reasons, witnesses, worst cases, margins
and Q3's sentences; Rust's evaluation (differential only). Integers are unbounded in all three languages, and Rust uses
big integers as W6 does.

Under `VE_AUTHORITY=python` every operation of this route is `CheckerUnavailable`, never a verdict. The trust-cost
line for ROADMAP, to land with item 2: "Risk (`risk@0`, stage A): new trusted block, entry and record decoders,
condition normaliser and evaluator, record admission, cell regenerator, severity closure, inliner, slot premises,
decision-model builder, certified margin check, audit snapshot admission and `ve_risk_route`, proved from raw JSON
under the unchanged allowlist; untrusted: the Python shape check and surface, rendering, Rust evaluation."

## 10. Statement review checklist (Astra + Fable, before items 2 and 3)

1. **Completed cases** (1.4, 1.5, 4.4): sources, defaults, completion, `S → N`, stated `might`; `regenerate_sound`
   over completed cases; the paraphrase of `might not lead to` (plan 12 item 1).
2. **The endpoint theorems' hypotheses** (4.2, 4.3): scoping, separability, unit coefficients, the `≠` atom and
   `nnf`; the canonical witness; the rewrite that changes the model (plan 12 item 1).
3. **`might prevent` and `excludes`** (2.2): the wording, the fulfilment choice and the default body (plan 12 item 1).
4. **Margins** (4.9): full validation, without re-admission, of perturbed records; the candidate set and the
   candidate limit on the original record; `status_piecewise_constant`; the per-kind record-level scans; and the
   decision on Q-margin-proof (11.11) (plan 12 item 1).
5. **The probe statuses** (2.1, 2.2): what is frozen, c10 legend-dependent, and the c11/c12 observation. The
   reviewers' c5 replacement, "If `<condition>`, `<action>` leads to `<harm>`.", was probed once with new sealed
   items (plan 2.6 rule 4; `risk-wording-probe-2`) and is frozen as written.
6. **The block and the generated vocabulary** (1.1, 1.2, 4.1): freshness, reserved names, `outcomes: signed`, and the
   kinds and requirements added to make the plan's requirements checkable (11.6).
7. **The slot premises** (4.6): the full order table, `class` functional and not total, `compatFacts`,
   `risk_expansion` with its carrier and `risk_conservative`.
8. **`less_worst`** (4.5): the relational body, unclassified harms, `lessWorst_strict` and `precaution_has_maximal`.
9. **The decision report** (4.8, 5.2): the conflict gate, status, `default_decided` and the rendering of k10.
10. **The audit** (4.10): snapshot admission from the prefix, Q1 precedence, Q2 with `NOT COMPARABLE`, PROCEDURE
    BREACH, `verdict_ignores_outcomes` and `snapshot_no_hindsight`.
11. **The English** (2.3, 2.4): rejections, scope rules, the record-only condition wordings and the legend.
12. **Diagnostics and fixtures**: each reviewer derives 8.2 from 8.1 first, then compares; disagreements are recorded
    before any expectation is edited.
13. **The Lean statements** (7.2), the case kinds (7.3) and the non-claims (7.4).
14. **The resolved choices** of section 11.

## 11. Resolved choices in this draft

Each is a point where the plan left a reading open. The review may overturn any of them.

1. **Generated vocabulary.** `E_risk` generates the severity sort, the class constants and three predicates with
   `risk__` names (1.2), as soft-norms 1.3 generates `E′`. The plan's "fresh" means "not a sort of `E`". Author roles
   for `might_lead_to` or `class` would have put risk symbols into the old signature and complicated conservativity.
2. **`class` functional is a slot premise**, with the formula of W1's `functional` flag, rather than a flag on a
   generated predicate. Every risk premise then carries a `risk:` label, and `E_risk` adds no flag.
3. **The order is generated as a full ground table** (positive and negative literals over the n classes), rather than
   as separate strictness and transitivity premises. With domain closure and distinctness it fixes the order on
   every document model, which is what `lessWorst_strict` uses.
4. **`or_worse` is one binary word with a severity argument**, so `is serious or worse` is `or_worse(h, serious)`.
5. **`risk@0` requires `outcomes: signed`.** Under `complete_by`, alt's `table_complete` would be generated from the
   policy's positive cells, and a risk policy has none, so it would contradict every certain cell of a decision.
6. **Alternative kinds and quantity kinds** (1.1) make the plan's required alternatives ("a memory-limited run") and
   required estimators ("the peak memory of a job") checkable on record-local names. The plan named the requirements
   without a way to recognise the alternatives and quantities they are about.
7. **A missing required alternative rejects the record** (`RequiredAlternativeMissing`). Plan 7.2 listed it among the
   report lines. A status computed without the safer alternative errs on the permissive side (P2 would not fire),
   which is the gaming the requirement prevents.
8. **Settings are scoped to their alternative's cells** (`RiskSettingScope`), so one alternative's choice never
   enters another alternative's cells.
9. **Record statements have the plan's three stated forms only.** `might not lead to` as a record statement is
   rejected (`RiskStatementForm`). It could be admitted later as a consistency assertion symmetric to `might`.
10. **The canonical witness** (4.3) is the extremal-endpoint witness that endpoint arithmetic produces. It gives
    k1's (12, 8) as in the plan. For k27(a) it gives (8, 5), where plan 12's text had (6, 5): both are cases, and
    the diagnostic names the canonical one.
11. **Q-margin-proof: the certified candidate check ships in stage A** (4.9). Lean regenerates the candidates itself
    and evaluates every one. The report says "nearest change" and "no single valid change", with invalid and
    conflicting values reported separately at record level, each certified by its own scan (`scanInvalid`,
    `scanConflict`). This is the plan's second option. Its cost is the trusted candidate function, the scans and
    `status_piecewise_constant`, which the plan already listed as an obligation, and it removes the untrusted margin
    search from the trust split (plan 8.2). The statement review kept this choice.
12. **A status is (permitted, required, clear)**, so a margin reports a change of `clear` too.
13. **`"ruled_out_by": "chooser"`** names the record's chooser as the decider (the plan's "the deciding agent"). It
    renders as the chooser's label in reports and as "the deciding `<chooser>`" in the legend.
14. **Alt's registered binder** replaces the plan's `there is an agent such that both that action is available …
    and …` in the canonical rule texts (2.5), which avoids a second derivation. k19 checks both.
15. **Q1's precedence**: no clear action at the decision (a dilemma or a conflict) comes before forbidden, which comes
    before permitted. Q2 is `NOT COMPARABLE` when the all-estimates record is invalid. The plan did not say what Q1
    reports for a conflict, or what Q2 reports when the combined record is invalid.
16. **Citations carry `(id, seq, hash)`**, so hindsight is detected from the decision entry and the audit reads only
    the prefix. `verdict_ignores_outcomes` then holds with equal diagnostics, not only equal verdict kinds.
17. **Condition wordings are record-only** (2.3). Inside a rule, `unless` is W1's carve-out and `if` the guard, which
    keeps each rule sentence to one reading while policy-level conditions stay OPEN (Q-templates).
18. **c5 frozen in its replacement wording** (2.1): "If `<condition>`, `<action>` leads to `<harm>`." passed its
    re-probe (L 16/16, C 16/16), so it is registered for records and rendered unmarked; the first probe's trailing
    form is rejected with that rewrite. `certainly leads to` is not registered, because c3a passed.
19. **Every harm constant is a harm of every decision**, so the cell table is complete (E3 by construction) and no
    harm can be dropped from consideration.
20. **Quantities are log-level names with W6 tags** and never enter `E` or a norm guard. Only the tags come from the
    environment's W6 extension.
21. **`excludes` is expanded by the risk decoder** before alt's decoder sees the block, so alt's decoder and
    `FulfilmentNotBase` are unchanged.
22. **`unranked_severities`** is a warning line for the environment (undeclared incomparable pairs) and a report
    line for decisions (comparisons blocked by an incomparable pair), as plan 4.1 and 7.2 use the name.

## 12. Corrections from the statement review (draft 2) and its re-check (draft 3)

### 12.1 The statement review (draft 2)

The statement review of draft 1 (`manage-agents/debates/risk-spec/`, three rounds, both sides STATUS CONVERGED)
returned FIX. The bounded re-check (12.2) covered the passages and fixtures below. Items are cited by reviewer, round
and number: `A1.2` is Astra's round 1, item 2; `F1.7(c)` is Fable's round 1, edit 7(c); "joint" is that round's
proposed joint position.

| Debate item | Correction | Where |
|---|---|---|
| A1.1, A2.1, F2 (A1 conceded), F2 joint 1, F3.3: an unnormalised `LinForm` breaks `possibleE_iff` | `LinForm.Normal`; every atom holds a `NormLinForm`, built only by `LinForm.normalize`; `normalize_normal`, `normalize_eval`; the endpoint theorems over normal atoms | 4.2, 4.3, 7.1, 7.2; k34 |
| A1.2, A2.2, F2 (A2 conceded), F2 joint 2, A3: model validity is left to the caller | Every constant of `E` is interpreted (an action constant by the alternative of its name, a chooser constant as a chooser with no action); `RiskConstant`; the decidable check V10 before alternatives validation; `risk_scenario_sound`'s first conjunct comes from V10 | 4.4 (V1, V10, the decision model), 6, 7.1, 7.2; k35 |
| A1.3, A2.3, F1.1, F2 (A3 conceded), F2 joint 3: the record route has no sequence number, and validation has no entries to check | The decision entry supplies `seq` and `day`; admission (`admitDecision`, A1 to A3) is split from validation (V1 to V11); `admitDecision_sound`; the connecting conjuncts of `risk_wire_scenario_sound`; `snapshotOf` runs the same admission on the prefix; margins perturb the admitted record and never re-run admission | 3.3, 3.4, 4.4, 4.8, 4.9, 4.10, 5.1, 7.1, 7.2, 7.3 |
| F1.2: check order in the audit | Per citation: `HindsightEntry`, `MissingEntry`, `AlteredEntry`, then `WithdrawnEntry` | 4.4 A2, 4.10, 5.2, 6; k15 |
| F1.3: k17(c) cannot be reached | A supplied estimate entry without `seq` or `day` is `EstimateProvenance: <id> recorded` before matching; k17(a) and (b) recompute the hashes | 3.3, 4.4 A1 and V3, 6, 7.2; k17 |
| F1.4, A2 joint: two settings, or a setting and an estimate, leave the box undefined | `RiskSettingTwice`, checked before the box | 1.4, 4.4 V4, 6; k33 |
| A1.4, F1.5, F2 joint 4, A2 joint: `status_piecewise_constant` fails with the candidate limit inside `outcomeAt` | The limit is checked once on the original record (`marginLimit`), outside `outcomeAt`; Astra's fixture | 4.8, 4.9, 6, 7.1, 7.2, 9; k36 |
| A1.5, A2.4, F2 (A5 conceded), F2 joint 5: the scope rewrite | "Not every" is `∃a. available(a, r) ∧ ¬might(a, h)`; both formulas are stated | 2.3; k37 |
| F1.6, A2 joint, A3.1, F3.1: the record-level margin lines have no theorem | Per-kind `scanInvalid` and `scanConflict`, their soundness theorems and wire conjuncts; "No conflict at any candidate" only when every `scanConflict` finds nothing | 4.9, 5.2, 7.1, 7.2, 7.3, 7.4; k38 |
| A3.2: supersession in the standalone route | Withdrawal is judged on the supplied entries that precede the decision in `risk-decision` and on the prefix in the audit (`WithdrawnEntry`, NOT REPLAYABLE); a later supersession affects neither; a non-claim | 1.4, 3.3, 4.4 A2, 4.10, 5.2, 6, 7.4; k16, k39; plan 5.3, 6.2, 6.3, 9.3 |
| A2.4, A3.3, F1.8, F3.2: c9's paraphrase is vacuous without a classified witness | The paraphrase names the classified witness and requires a class for each harm of `<a′>`; k31 checks it | 2.1; k31 |
| F1.7(a) | `snapshot_no_hindsight` gains `x.seq = c.seq` | 7.2 |
| F1.7(b) | Q3's rule is "measured or set" | 4.10 |
| F1.7(c) | k9(b) has no `always_possible` or `combination` | 8.1 |
| F1.7(d) | `["quantity", name]` is a risk-local node with its quantity's tag | 3.2 |
| F1.7(e) | k20 gives the record under {1, 2x, 3} | 8.2 |
| A1 joint, A2 joint, F2 (conceded), F2 joint 6: plan sync | The plan's trust lines, margin admission and certification, and k25's `point_estimates` line | plan 7.4, 8.1, 8.2, 8.3, 12, 13; k25 |
| A1 joint, A3, F2.2, F3.4: the c5 replacement | "If `<condition>`, `<action>` leads to `<harm>`.", probed once with new sealed items; c5 stayed pending until then (frozen 2026-09-30, `risk-wording-probe-2`) | 2.1, 10, 11.18; plan 12 item 1a |

Details settled while applying these edits, not debated:

- Draft 1's step 3 required typed fact arguments with no diagnostic. V10's validity check now covers them, as
  `RiskFact: <predicate>`.
- The decision entry's own hash is recomputed at A1 (`AlteredEntry: <id>`), as a cited entry's is at A2.
- `WithdrawnEntry` has the same text in both routes, because the audit runs the same admission.
- 8.1 now states a convention the fixtures already relied on: a record used with a variant environment or rule set
  is bound to that variant, and a changed record's decision entry hash is recomputed. Without it, k13's second part,
  k16 and k35 would stop at `RiskBinding: policy`, and a changed record at `AlteredEntry` for its decision entry.
- c9's legend line (2.4) keeps its probed text. It agrees with the new paraphrase on records.
- k36 uses Astra's numbers as given. The counts were checked: the original record's endpoints have 138, 138, 139 and
  163 candidates, so the original is within the limit.
- F3.1 asked for an invalid value before a conflict, and A3.1 for one kind before the other. k38 puts the conflict
  first. For an invalid value to come first, the record must become valid again farther out in the same direction.
  V1 to V9 never allow that: widening can break only `S → N` and separability, narrowing only a stated `might`, the
  range and an intersection, and each stays broken farther out. It takes a policy assertion unit evaluated at V11.
  Draft 2 therefore gave only k38's order. The re-check required F3.1's order as well, and draft 3 adds it as k40
  (12.2).

### 12.2 The re-check p3ver1 (draft 3)

The bounded re-check of draft 2 (`manage-agents/risk-p3ver1.final.md`) returned FAIL with two findings. It found that
the other edits track the requested corrections. Draft 3 applies both findings and changes nothing else.

| Finding | Correction | Where |
|---|---|---|
| p3ver1.1: F3.1's fixture, an invalid value before a later conflict in one direction, is missing; k38 has the other order | k40: a policy assertion unit `G` fails at 4 and holds again at 5, where rules X1 and X2 conflict. `scanInvalid` returns 4 and `scanConflict` returns 5, and both lines are reported. V11 names a failing unit by its label, so k40's diagnostic is determinate | 4.4 V11, 4.9, 7.2 (`scanInvalid_sound` docstring), 8.1, 8.2; k40; 12.1 (last item); plan 7.4, 12 |
| p3ver1.2: the decision model has no constant-table entries for record-local names, although frozen `rowsTypedB` resolves every signed row through `M.constants`, so V11 and the fixtures would fail for D17's alternatives | The constant table also maps the chooser's name to the record's chooser and each alternative's name to that alternative (sharing an interpreted action constant's entry). Rows name the alternative and the harm constant. V1 keeps the table a function: no record-local name equals a constant of `E_risk` (a class name included) or another record-local name (`RiskConstant`). A fact argument that names no entry is `RiskFact` (V10) | 4.4 (V1, V10, the decision model, `decisionRows`), 6, 7.1, 7.2 (proof plan); k35; plan 12 |

Details settled while applying these edits, not debated:

- A record-local name equal to a class name, or a chooser named like one of its alternatives, would give the
  constant table two entries for one name. Draft 2's V1 compared record-local names with the constants of `E` only.
  V1 now also compares them with the class names and with each other, and reuses `RiskConstant`.
- k40's diagnostic uses alt's labelled text, `premise <label> fails`, which alt's route produces with
  `validateAlternativesWith`. `validateAlternatives_labels` shows that the labels do not change success, so
  `risk_scenario_sound` is unchanged.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-29 | Draft 1 | Item-1 statement specification of stage A from plan draft 2 and the probe results. It covers the `risk` block and the generated vocabulary `E_risk` with a fresh severity sort; decision records, the box, sources, completion and completed cases; the wordings with their probe statuses (c5 pending, c10 legend-dependent); the risk paraphrases of alt's words, `might prevent` and `excludes`; rejected wordings and scope rules; the legend; the wire forms of the block, conditions, the log and the record, and identity; `WellFormedRisk`; normal form, separability, unit coefficients, the endpoint table and the canonical witness; record validation, regeneration and the decision model; `class` functional and not total, `or_worse`, `less_worst` and inlining; the slot premises, `BaseAdmissibleRisk`, `compatFacts`, model expansion and conservativity; the policy checks; the decision report; point estimates and certified margins; the log and the audit (Q1 to Q3, PROCEDURE BREACH); diagnostics; every item-2 theorem as a statement; fixtures k1–k32 and kC1 with definitions separated from expected results; limits and trust; the review checklist; resolved choices. Spec only: no code, Lean or frozen contract changed. |
| 2026-09-29 | Draft 2 | Applies the converged statement review (FIX), mapped in section 12: normal forms as a typed invariant (`NormLinForm`, `normalize_normal`, `normalize_eval`); record admission (`admitDecision`, sequence number from the decision entry, per-citation order Hindsight, Missing, Altered, Withdrawn, `EstimateProvenance … recorded` before matching) split from validation, with `admitDecision_sound` and the wire conjuncts; decision-model constants and the validity check (`RiskConstant`, V10); `RiskSettingTwice`; the margin-candidate limit outside `outcomeAt` (`marginLimit`); per-kind record-level scans (`scanInvalid`, `scanConflict`); standalone supersession scoped to the supplied entries (`WithdrawnEntry`, a non-claim); the corrected scope rewrite with both formulas; c9's paraphrase with the classified witness; `snapshot_no_hindsight` with `x.seq`; Q3's "measured or set"; the risk-local `quantity` node; k9(b), k15, k16, k17, k20, k25 and k31 corrected; fixtures k33–k39; the c5 replacement for its re-probe. No frozen contract, hash or existing theorem statement changed. |
| 2026-09-29 | Draft 3 | Applies the two findings of the bounded re-check p3ver1 (FAIL), mapped in 12.2. First, fixture k40: an invalid value (a policy assertion unit that fails, then holds again) before a later conflict in one direction, with V11 naming a failing unit by its label. Second, the decision model's constant table gains entries for the chooser's and the alternatives' names, and signed rows resolve through them; V1 extends `RiskConstant` to class names and to clashes between record-local names; `RiskFact` covers an argument that names no entry; k35 states the table. No other design change; no frozen contract, hash or existing theorem statement changed. |
| 2026-09-30 | c5 frozen | `risk-wording-probe-2` (L 16/16, C 16/16, no critical answer, not legend-dependent) froze c5 as "If `<condition>`, `<action>` leads to `<harm>`." (plan 2.6 rule 2). The 2.1 row and the 2.4 legend line use it; the surface registers it for record statements, renders it, and rejects the first probe's trailing `… leads to … if …` with that rewrite; the `(wording pending)` markers are removed, and the k2, k19 and k24 texts use the frozen form. The semantics (`S = C`) is unchanged. |
