# Risk: possible consequences, likelihood and severity over explicit alternatives: plan (`risk@0`)

> Status: planning draft 2 (2026-09-29). Design plan only: no code, Lean, frozen contract or existing identity is
> changed, and no coverage gain is predicted. Inputs: [norms.md](norms.md) (W1, cited `norms.md n`),
> [soft-norms.md](soft-norms.md), [alternatives.md](alternatives.md) and [causation-PLAN.md](causation-PLAN.md)
> (`alternatives@0`, cited `alt n`), [units-schema.md](units-schema.md) (W6, cited `W6 n`), [document.md](document.md)
> (W2), [VISION.md](../../VISION.md) (converged rule cited `CR n`), the evidence-layer design
> ([design/evidence-layer-design.md](../../design/evidence-layer-design.md), cited `EL n`), the Asimov use case
> ([usecases/asimov-laws/README.md](../../usecases/asimov-laws/README.md), its OPEN list) and the ARCH-ROADMAP P1
> items "unspecified default" and "limits contract" (`manage-agents/ARCH-ROADMAP.md`). Theorem statements are
> obligations, not proofs. Every open question is marked **OPEN** and collected in section 13. The Astra + Fable
> review of draft 1 (PLAN-EXPAND2 rule 10; `manage-agents/debates/design-risk/`) converged on REVISE. Draft 2
> applies it, mapped item by item in section 15. There is no further plan round. The wording probe (2.6) ran on
> 2026-09-29 (`experiments/authoring-gates/risk-wording-probe/RESULTS.md`), and item 1's statement spec is
> [risk.md](risk.md) draft 1; the next gate is its stage A statement review (item 1, section 12).

## 0. Problem and stance

VE states rules and checks what happened. Many rules are about what *might* happen: an action may lead to a crash, an
injury or a death, with some likelihood and some severity. An AI agent about to run a program that might exhaust
memory and crash a server has to decide whether to run it, run it with a memory limit, ask the user or not run it.
Asimov's First Law weighs harms against one another, and the use case's README leaves this OPEN ("proportionality
and tradeoffs among different harms", "uncertain outcomes"). `alternatives@0` gives the structure (choosers,
explicit alternatives, `leads_to`, `allows`, `prevents`, followability) but its outcome table is Boolean and
certain, and it rejects `could lead to`, `risks` and degrees as wordings (alt 2.2, 4.10).

Stance. The checker **never estimates**. It checks decisions **relative to declared estimates**, each a labelled
assumption with provenance, and it computes only exact consequences of them. The design has two layers:

1. **The estimate layer** (new, per decision): quantities with interval estimates or exact settings, conditions
   linking quantities to outcomes, stated outcome cells, and later likelihood bands, chances and costs. Lean
   **regenerates** from it a finite Boolean table per decision: which harms each alternative *might* lead to, which it
   *leads to* (in every case the estimates allow), and the threshold facts the rules mention. The arithmetic is ground
   and linear over integers (W6 grids), so it is decidable by evaluation and proved exact once.
2. **The rule layer** (unchanged machinery): policies are W1 rules over `alternatives@0`, whose guards mention the
   regenerated facts as ordinary base predicates (details below). Conflict, followability and scenario evaluation
   are `alternatives@0`'s, with a few universal slot premises added.

The rule layer's guards use:

- one new base predicate, `might_lead_to`, which is regenerated on decisions and never supplied;
- its negation, worded `cannot lead to`;
- two defined words with fixed bodies, inlined as alt 4.3 does: `is <class> or worse` and `has a less severe worst
  case than`.

The `alternatives@0` words keep their definitions. In risk environments their paraphrases say "might not lead to",
`prevents` is written `might prevent`, and a second fulfilment body, `excludes`, is offered (2.5).

Probability never enters a formula (PLAN-EXPAND2 lists "probability inside formulas" as research). It enters as
data attached to a cell and leaves as a Boolean fact with a certificate of how it was computed. This follows CR 1
("elaborate by default") and CR 8 (weighing, empirical truth and causal assumptions are outside certification; their
formalised conditional consequences may be checked).

## 1. Invariants (what the design never does)

1. **No estimate is produced by VE.** There are no default chances, bands, severities, costs, priors or intervals.
   VE does not interpolate, does not infer chances from frequencies or quantities, and does not multiply along chains.
   It never merges two estimates of one quantity unless the policy states how (5.3).
2. **Every result is conditional** on named estimate, condition and statement ids (`conditional_on`). Every verdict
   says "given estimates E1, E2 …", as `alternatives@0` verdicts say "in the declared model".
3. **One reading per sentence.** Each new wording has one reading and a paraphrase a zero-training reader can check
   against an example. Wordings that invite a second reading are rejected with rewrites (2.1), and the accepted ones
   are probed with readers before the statement review (2.6).
4. **No hindsight.** A decision's verdict depends only on what was recorded before it. Outcomes are reported
   separately and never change the verdict (section 6).
5. **No invented content.** A weighing rule, severity order or cost table that the source does not state is an
   attributed narrowing (VISION.md 3) or an author's policy choice, shown as such.
6. **Honest UNKNOWN and honest gaps.** Unexamined cells, unranked severities, missing chances and default-decided
   alternatives are listed, never silently resolved. Document-level checks keep UNKNOWN; only the decision report is
   decided by evaluation (7.2, 8.1).
7. **Lean owns the semantics** (SEMANTICS-MIGRATION-PLAN 6, as for `alternatives@0`). Python checks shape, surface
   and dispatch. Rust evaluates untrusted for differential tests.

## 2. Possible consequences (question 1)

### 2.1 Wordings

| Wording | The one reading (the IDE's paraphrase) | Formal |
|---|---|---|
| `<action> might lead to <harm>` | The declared estimates, conditions and statements do not rule the harm out if the action is taken. | `might(a, h)` |
| `<action> cannot lead to <harm>` | They rule it out: it happens in no case they allow. | `¬might(a, h)` |
| `<action> leads to <harm>` | The harm happens in every case they allow (`alternatives@0`'s word; not "tends to"). | `leads_to(a, h)` |
| `<action> might not lead to <harm>` | Some case they allow avoids the harm (a completed case, 2.2). | `¬leads_to(a, h)` |
| `<action> leads to <harm> if <condition>` | Sufficient condition, a model assumption of its author. | 2.2 `S` |
| `<action> cannot lead to <harm> unless <condition>` | Necessary condition. | 2.2 `N` |
| `<action> leads to <harm> exactly when <condition>` | Both. | `S = N` |
| `<harm> is <class>` / `<harm> is <class> or worse` | Severity (4.1). | `class(h, c)` / `∃s. class(h, s) ∧ (s = c ∨ moreSevere(s, c))` |
| `<a′> has a less severe worst case than <a>` | `<a>` might lead to a harm more severe than every harm `<a′>` might lead to. A harm with no severity blocks the comparison (4.2). | 4.2 |

Conditions are W6 comparisons (`is greater than`, `is less than`, `is at least`, `is at most`, `equals`) between
same-tag linear expressions over declared quantities and literals, joined by `both … and`, `either … or` and `it is
not the case that` (W6 4, docs/english-surface.md).

Rejected, with rewrites:

- **`may lead to`.** W1 reserves `may` for permission, and "May never means might" (norms.md 2.1). The rewrite is
  `might lead to`.
- **`does not lead to`.** Under `risk@0` it has two readings: "cannot" or "might not". The rewrite offers both,
  and the negative cell of `alternatives@0` (`It is not the case that … leads to …`) is paraphrased as `might not
  lead to`, as are the `alternatives@0` words built on it (2.5).
- **`could lead to`, `risks`, `is likely to lead to`.** These stay rejected as in alt 2.2 until stage B (3.2)
  gives likelihood words their declared ranges. The rewrite is `might lead to`.
- **`is safer than`.** It invites a probability-weighted reading. The rewrite is `has a less severe worst case than`.
- **`Every action … cannot lead to …`.** This has a scope ambiguity ("not every" versus "every … not"), as with
  object-position `every` under `must not` in norms.md 2.1. The rewrite is one sentence per action, or `It is not
  the case that some action available to <chooser> might lead to <harm>.`
- **`<action> prevents <harm>`** (risk environments only). In English it claims the harm cannot happen, which
  `prevents` does not mean under `risk@0`. The rewrite is `might prevent` (2.5).

**OPEN (Q-wording):** whether zero-training readers take `cannot lead to` deontically, and whether `leads to`
should render as `certainly leads to` under `risk@0`. A small probe settles what the statement spec freezes (2.6);
the W8 fidelity gate (item 8) remains the full test.

### 2.2 Semantics: possibility is consistency with what is declared

A **decision record** (section 5) declares quantities. Each is an *estimate*, an inclusive interval `[lo, hi]` on its
unit's grid (a point estimate is `lo = hi`, flagged in 7.3), or a *setting*, an exact value chosen as part of an
alternative (the memory limit). A **valuation** is one value per quantity within its estimate. The **box** is the set
of valuations; it is nonempty because validation requires `lo ≤ hi`.

**Sources.** Each cell `(a, h)` has at most one sufficient source and at most one necessary source:

- `<a> leads to <h> if C` gives `S = C`, `<a> cannot lead to <h> unless C` gives `N = C`, and `exactly when C` gives
  both;
- a stated `<a> leads to <h>` gives `S = ⊤`, and a stated `<a> cannot lead to <h>` gives `N = ⊥`;
- a stated `<a> might lead to <h>` gives neither: it is an assertion, checked below.

A second source on one side is `RiskTwoSources: <a>/<h>`, with the rewrite that joins the two conditions into one
(`either … or` for sufficient conditions, `both … and` for necessary ones). A cell with a source or a stated `might`
is **addressed**, and a missing side takes its default: `S = ⊥` (nothing forces the harm) and `N = ⊤` (nothing
excludes it). A cell with neither is **unaddressed** and is completed by 2.4.

**Completed cases.** A **case** is a pair `(v, H)`: a valuation `v` in the box and an outcome `H(a, h)` for every
cell ("if `a` is taken, `h` happens"), such that `S(v) → H(a, h) → N(v)` for every cell. Where only the valuation
matters, a case is written by its values, e.g. (12, 8).

```text
leads_to(a, h)  :=  every case has H(a, h)    =  ∀v ∈ box. S(v)      the harm follows in every case
ruled_out(a, h) :=  no case has H(a, h)       =  ∀v ∈ box. ¬N(v)     the harm is excluded in every case
might(a, h)     :=  some case has H(a, h)     =  ∃v ∈ box. N(v)      = ¬ruled_out(a, h)
```

Validation requires `S → N` at every valuation in the box, so every valuation extends to a case, with `H(a, h)` free
wherever `S(v)` is false and `N(v)` true; the right-hand forms follow. A failure names the valuation and the sources.
It is `SufficientOutsideNecessary: <a>/<h>` when both sides are conditions, and `RiskInconsistent: <a>/<h>` when a
stated cell gives one side. A stated `might` is a **consistency assertion**: on a cell that is ruled out it is
`RiskInconsistent`. Then `leads_to → might` (theorem `certain_within_possible`). With cases completed this way,
2.1's paraphrase of `might not lead to` ("some case they allow avoids the harm") is literally true: `¬leads_to(a, h)`
holds exactly when some case has `¬H(a, h)`.

This is VE's existing distinction between entailment and consistency. `leads_to` means the declarations entail the
harm, `cannot` means they entail its absence, and `might` means its occurrence is consistent with them. Every
`might` therefore has a **witness case** (e.g. "peak memory 12 GB, free memory 8 GB") checkable by evaluation, and
every `cannot` has an exactness proof (2.3). Cells are **marginal**: `might` for two harms does not claim that both
can happen in one case. Joint possibility is not claimed (**OPEN (Q-joint)**).

### 2.3 Deriving cells from quantities (the separable fragment)

Put each comparison in normal form `Σ cᵢ·qᵢ + k ⋈ 0`, with coefficients collected per quantity and
`⋈ ∈ {<, ≤, =, ≠}`, and push negations to the comparisons: negation flips `<` and `≤` (`¬(e < 0)` is `−e ≤ 0`) and
swaps `=` with `≠`. Over an integer box, the maximum of `Σ cᵢ·qᵢ` is `Σ (cᵢ ≥ 0 ? cᵢ·hiᵢ : cᵢ·loᵢ)` and the minimum is
symmetric. So one comparison is decided exactly by endpoint arithmetic.

An `equals` or `≠` comparison requires coefficient ±1 on each estimated quantity in it, because only then are the
values of the form contiguous (`RiskEqualityCoefficient` otherwise). Then `=` is possible when `min ≤ 0 ≤ max` and
certain when `min = max = 0`, and `≠` is possible unless `min = max = 0` and certain when 0 lies outside
`[min, max]`. The ±1 rule is a hypothesis of both endpoint theorems: without it, `2·q = 1` with `q` from 0 through 1
is separable and its form ranges over `[−1, 1]`, which brackets 0, yet no case satisfies it (fixture k5). `≠` stays
one comparison. Rewriting it as `either … is less than … or … is greater than …` would put the quantity in two
comparisons and break separability (fixture k25).

A condition is **separable** when no estimated (non-point) quantity occurs in two of its comparisons. Settings and
literals may repeat, because a point has no freedom. On separable conditions, `∃` distributes over `and` and `∀`
distributes over `or`, so possibility and certainty are computed by endpoint arithmetic over the condition tree.
Lean proves `possibleE_iff` and `certainE_iff` (8.3) once, under the separability and ±1 hypotheses. The `S → N`
check evaluates `S ∧ ¬N`, which must itself be separable unless `S = N`.

Stage A rejects non-separable conditions (`RiskConditionShared: <quantity>`) with two rewrites: split the condition
into cells, or declare the shared quantity separately for each comparison. The second is a **change of model the
author must approve**, not an equivalent rewrite: it drops the fact that both comparisons see one value, so the IDE
offers it as a new assumption and says so. Deciding non-separable conditions needs a satisfiability witness for
`might` and an `order@0` certificate for `cannot`. That is planned as item 7 (section 12); stage A has no UNKNOWN
cells.

Worked derivation. "The peak memory of the job is from 6 GB through 12 GB" (E1) and "the free memory of the server
during the job is from 8 GB through 10 GB" (E2). The necessary condition "Running the job cannot lead to a server
outage unless the peak memory of the job is greater than the free memory of the server" gives `might`, because
`hi(E1) = 12 > lo(E2) = 8`; the witness is the case (12, 8). A point estimate of 12 GB against free memory of exactly
8 GB would make the sufficient condition "running the job leads to memory exhaustion if …" certain. The report then
says the certainty rests on two point estimates (7.3).

**Policy-level conditions** ("every job run without a limit …") would quantify over quantity-valued attributes of
actions. That is the `order@0` × n-ary combination W6 leaves gated (W6 1). Stage A conditions are therefore ground,
written per decision over named quantities (W6 4: a quantity name is a declared constant). **OPEN (Q-templates).**

### 2.4 Unexamined cells

The mandatory `unexamined` field says how cells no condition or statement addresses are read, as alt 1.4 does for
`leads_to`:

- **`possible`** (precautionary): unexamined cells are `might` (`S = ⊥`, `N = ⊤`), listed under
  `unexamined_possible`.
- **`{"ruled_out_by": "<decider>"}`**: unexamined cells are ruled out (`N = ⊥`) on that decider's authority, listed
  under `assumed_ruled_out`.
- **`always_possible: [<classes>]`**: listed severity classes stay precautionary under either mode.

The OOM policy (section 9) makes serious and severe harms always possible, so the agent must address them for every
alternative, and lets the agent rule out minor ones. This stops an agent hiding a serious risk to a listed harm by
leaving its cell unaddressed, while keeping a decision record short. It covers only the harms the policy lists: it
cannot detect a harm the policy never named (**OPEN (Q-new-harms)**), and it does not certify that the policy's
classification of a harm is right.

### 2.5 Relation to `alternatives@0`

On a decision, the regeneration yields a complete signed `leads_to` table. Each row's support is `calculation` (from
a condition) or the stated cell's support, so existence fact E3 (alt 4.2) holds by construction under
`outcomes: signed`. `avoidable`, `allows` and `prevents` keep their definitions (alt 4.3) over certain outcomes. The
new base predicate `might_lead_to` gets the slot premise `certain_possible: ∀a h. leads_to(a, h) → might_lead_to(a,
h)`. Supplied scenarios never supply `might_lead_to` or `leads_to` rows under `risk@0`: both are computed, as
regulated tables are (alt 3.3). The policy document carries no estimates; decisions are scenarios bound to their
record id.

**The `alternatives@0` words under `risk@0`.** Their definitions (alt 1.3, 4.3) do not change, so alt's theorems
apply as they stand. What changes is what `¬leads_to` says: under `risk@0` it means "might not lead to", not "cannot
lead to". In A2 (10.2), rescuing P satisfies `prevents(rescuing P, P's death)` although rescuing P might still lead to
P's death, and alt's rule 8 ("must prevent …") is discharged by an action that might still kill. Risk environments
therefore regenerate four paraphrases, extending 2.1's rule for the negative cell:

| Word | Paraphrase in a risk environment |
|---|---|
| `<harm> is avoidable by <chooser>` | Some action available to the chooser might not lead to the harm. |
| `<action> allows <harm> to happen` | The action leads to the harm, and another action available to the same chooser might not lead to it. |
| `<action> might prevent <harm>` | The action might not lead to the harm, and another action available to the same chooser leads to it. |
| fulfilment `avoids` (legend line) | A `<chooser>` `<act>` by taking an action that might not lead to the harm. |

- **`might prevent`** is the canonical form of `prevents(a, h)` in risk environments. Bare `<action> prevents
  <harm>` is rejected there with that rewrite (2.1; fixture k29).
- **`excludes`.** A second named fulfilment body, `excludes(a, h) := ¬might_lead_to(a, h)`, with the legend line "…
  by taking an action that cannot lead to the harm", serves authors who mean real prevention. Like `avoids` it is
  allowed only on obligations on `(chooser, harm)`, and it mentions only the base predicate `might_lead_to`, so
  `FulfilmentNotBase` (alt 1.3) is satisfied.
- **The default body stays `avoids`**, with the risk paraphrase. Choosing `excludes` for an existing obligation (the
  Asimov rule 8) is an attributed author choice, a narrowing in translation (fixture k30).
- `unavoidable` keeps its paraphrase ("every one of them leads to the harm"): under `risk@0`, `leads to` already
  means "in every case".
- These paraphrases and the choice of fulfilment body are settled before the statements are frozen: the probe (2.6)
  tests them, and item 1's statement review rechecks them.

### 2.6 The wording probe (before the stage A statement review)

The statement spec (item 1) must not freeze wordings no reader has checked. A small proxy probe therefore runs before
item 1's statement review, in parallel with writing item 1. It is not the W8 fidelity gate, which stays after item 4
(item 8) and later uses human readers. It tests only what item 1 would freeze.

**Constructs.** Each construct is scored on its own. Each names the rival reading its items must separate from the
one reading; an answer that picks the rival is **critical**.

| # | Construct, as rendered | One reading | Critical rival reading |
|---|---|---|---|
| c1 | `<a> might lead to <h>` | not ruled out (2.1) | "is likely to lead to" |
| c2 | `<a> cannot lead to <h>` | ruled out | deontic: "is not allowed to lead to" |
| c3a | `<a> leads to <h>` | in every case | "tends to" or "usually leads to" |
| c3b | `<a> certainly leads to <h>`: the alternative rendering, on the same situations as c3a | in every case | as c3a |
| c4 | `<a> might not lead to <h>` | some case avoids it | "cannot lead to" |
| c5 | `<a> leads to <h> if <condition>` | sufficient | "only if" (necessary) |
| c6 | `<a> cannot lead to <h> unless <condition>` | necessary | "leads to … if" (sufficient) |
| c7 | `<a> leads to <h> exactly when <condition>` | both | one direction only |
| c8 | `<h> is <class>`, `<h> is <class> or worse` | 4.1 | "exactly `<class>`" for "or worse" |
| c9 | `<a′> has a less severe worst case than <a>` | 4.2 | "is less likely to cause harm" or "leads to fewer harms" |
| c10 | `<h> is avoidable by <chooser>` (2.5) | some action might not lead to it | "some action cannot lead to it" |
| c11 | `<a> allows <h> to happen` (2.5) | leads to it; another action might not | "another action cannot lead to it" |
| c12 | `<a> might prevent <h>` (2.5) | 2.5 | "guarantees that the harm does not happen" |
| c13 | the legend lines of `avoids` and `excludes` under a "must prevent" rule | 2.5 | each body read as the other |
| c14 | `cannot lead to` inside a policy, beside `must not` and `may` rules | a statement about the declared model | read as a rule: a prohibition or a permission |

c1–c9 cover the 2.1 table, c10–c13 the risk paraphrases of the four `alternatives@0` words, c3a against c3b the
`leads to` question, and c2 with c14 whether `cannot` is read as a norm.

**Items.** Four per construct, of which at least two have a different answer under the rival reading. Two control
items with bare `<a> prevents <h>` are reported but not scored; they test the reason for rejecting it. Each item is
a short situation in plain English: the chooser, its actions, the declared estimates and conditions in the forms of
2.1 with numbers, and the target sentence. One question follows, with three or four fixed options in random order,
one of them "The text does not say", and a request for a one-sentence reason. Half the items use the agent-operations
domain of section 9 and half a domain without computers (a delivery robot, a clinic). In at least one item per
construct the declarations contradict what world knowledge suggests, so the answer must come from the text. c3a and
c3b items put a `might lead to` sentence beside the target. The texts are written by hand in exactly the forms of
2.1 and 2.5 and the legend sentences of 9.1; no parser is needed. An example for c2:

```text
A delivery robot can take the stairs or take the lift. Taking the lift cannot lead to a lift failure.
What does the second sentence tell you?
(a) If the robot takes the lift, no lift failure happens in any case the text allows.    key
(b) The robot is not allowed to cause a lift failure.                                   critical
(c) A lift failure is unlikely if the robot takes the lift.
(d) The text does not say.
```

**Conditions.** Every item except c13's runs twice: in condition **L** it is preceded by the legend sentences the
environment would generate for the words it uses (as in 9.1), which is what the IDE shows; in condition **C** (cold)
it is not. c13 runs in L only, because its construct is the legend line itself. The gate uses L. C is reported, and a
construct that passes L with a critical answer in C is marked **legend-dependent** in item 1 and re-tested by W8.

**Readers.** Proxy readers from two model families, Claude Haiku 4.5 and a GPT-6 model (Sol), each in fresh sessions
with no tools, no repository and no VE documents. Each item is answered in each condition by two independent sessions
per family: four answers. A session gets at most eight items: at most one per construct, never both c3a and c3b,
never c12 with a `prevents` control, and never both conditions. Order is randomised with a recorded seed. The fixed
instruction is only: "Read each short text and answer its question from the text alone. Choose one option and give a
one-sentence reason." Neither plan reviewer reads as a subject. Runs follow EXPAND2's no-paid-API policy, and every
result is labelled "proxy; human readability unmeasured" (PLAN-ZERO-TRAINING 5). Size: 62 rendered items and 480
answers, in at least 60 short sessions.

**Sealing.** One plan reviewer writes the items, keys and critical options from 2.1, 2.5 and the legend alone. The
other checks that each key follows from the one reading and each critical option from the rival reading. An item they
disagree on is dropped before sealing. Items, keys, prompts, seeds and the reader list are committed with a SHA-256
manifest under `experiments/authoring-gates/risk-wording-probe/` before any run, and nothing is edited after sealing.
An item found defective afterwards is reported with its reason, and its construct is scored with and without it.

**Scoring and decisions.** Scoring is mechanical against the sealed key. An unparseable answer counts as wrong but not
critical.

1. A construct **passes** when, in L, at least 15 of its 16 answers are correct and none is critical.
2. Passing constructs are frozen by item 1 as written.
3. `leads to` versus `certainly leads to`. If c3a passes, `leads to` stays: one word across `alternatives@0` and
   `risk@0`. If c3a fails and c3b passes, risk environments render `certainly leads to`, and `leads to` is accepted as
   input and shown in that form. If both fail, neither is frozen (rule 4).
4. A failing construct is **pending wording** in item 1, and the statement review cannot freeze it. While c10–c12
   are pending, the profile word is not offered in risk environments, and authors write its definition out in guards
   (alt 4.3, with `It is not the case that … leads to …` for "might not lead to"). The two reviewers propose one
   replacement per failing construct; it is probed once with new sealed items under this protocol before the
   statement review. A second failure leaves only that construct pending.
5. The `prevents` controls are informational. The rejection of bare `prevents` stands whatever they show, until the
   reviewers revisit it.

**Output.** `RESULTS.md` in the same directory: for each construct and condition, the correct and critical counts;
every answer with its reader, session and reason; the decisions taken under rules 2–5; and the proxy label. Item 1's
statement review cites it.

## 3. Likelihood, in stages (question 2)

### 3.1 Stage A: possibility only (build first)

`might`, `cannot`, `leads to`, derived by 2.3. This is enough for:

- hard bans on possible severe harms;
- worst-case (precautionary) choice among alternatives;
- severity thresholds with confirmation;
- the OOM case and Asimov case A1.

It asks nothing of estimators beyond ranges they can defend, so it adds no false precision.

### 3.2 Stage B: named likelihood bands (on a trigger)

The policy declares a chance unit and bands, each an inclusive range. For example: "In this policy, a chance is
rare when it is from 0% through 1%. A chance is unlikely when it is from 1% through 10%." Bands are ordered, lie in
`[0%, 100%]`, and neighbours may share an endpoint (`BandRange`, `BandOrder` otherwise); gaps are warned. A band word
means exactly its declared range, and the legend shows the range every time the word appears: VE's "unlikely" is not
English "unlikely".

A chance estimate for a cell states a band or an explicit interval, with provenance: "The chance that a server outage
happens if running the job is taken is unlikely." A chance is always written "the chance that `<harm>` happens if
`<action>` is taken": `leads to` means "in every case" and cannot sit inside a chance. Guards compare chances with
bands or literals under the same rule as quantity comparisons: an unqualified comparison holds for every value in the
estimate, and `might be` holds for some.

- `the chance that <h> happens if <a> is taken is at most rare` means `hi ≤ hi(rare)`.
- `… might be more than 1%` means `hi > 1%`.

Lean regenerates one base predicate per distinct (comparison, threshold) the rules use, named `risk__chance__…` by
the scheme of soft-norms 1.3. It adds the ground monotonicity premises between them (more than 10% implies more
than 1%). When stage B triggers, its wordings, including the `if` nested in a rule's guard (P6, 4.3), go through the
probe protocol of 2.6 before its statement review.

Consistency with 2.2:

- A ruled-out cell's chance interval must contain 0% and is narrowed to 0%.
- A certain cell's interval must contain 100% and is narrowed to 100%.
- Otherwise the cell is `ChanceAgainstPossibility`.
- A `might` cell with no chance estimate has the vacuous chance 0%–100%, listed under `no_chance_estimate`.

Narrowing and cross-cell coherence (for example `P(outage) ≤ P(exhaustion)` when an outage needs exhaustion) reuse
the interval-coherence LP of EL 2.3 and are entered only through its certificates. EL's qualifications carry over
unchanged. EL keeps UNKNOWN atoms as possible and, above its size bound, solves a relaxation. So a reported violation
is genuine and narrowed intervals are outer approximations, but "no violation found" is never reported as coherence
(EL 2.3, consequences 1–3). The report gives EL's verdict in EL's words.

**Trigger:** a committed policy that uses graded likelihood words with its own ranges (a risk matrix).

### 3.3 Stage C: numeric chances and expected cost (on a trigger)

Costs are **normative** and chances are **empirical**, and the design keeps them apart.

- **Costs.** The policy declares one exact cost per severity class, in a declared unit (points or a currency), with
  its author. Costs must increase along the severity order (`CostAgainstSeverity`).
- **Additive loss.** The policy also declares that the cost of an outcome is the sum of the costs of its harms. This
  is an assumption of the policy's author, and every expected-cost result is `conditional_on` it.
- **Chances.** Chances are interval estimates per cell.
- **Expected cost.** `EC(a) = Σ_h cost(class(h)) · chance(a, h)` is linear in the chance variables, because costs
  are exact. Lean computes it exactly on the product grid of the cost and chance scales.
- **Comparison.** "`<a′>` has a lower expected cost than `<a>`" holds when `EC(a′) < EC(a)` for **every**
  combination of values within the chance estimates: the maximum of the linear form `EC(a′) − EC(a)` over the box of
  chance estimates is below 0 (2.3).
- **Threshold.** "The expected cost of `<a>` is at most 5 points" is decided the same way.
- **Box bounds are conservative.** The box ignores joint constraints between chances, which EL may certify. With
  `p + q = 1`, the marginal intervals `[0%, 100%]` give `p + q` the box range `[0%, 200%]`, although the sum is
  exactly 100%. A stage C result is therefore labelled conservative, or computed over a joint region that EL
  certifies (fixture kC1).

A policy may confine expected-cost rules to alternatives whose worst case is at most some class. This is a rule
pattern, not a primitive: it forbids trading a severe harm for convenience.

**Trigger:** a committed document that states numeric tradeoffs (an error budget, an expected-loss limit). Asimov
case A2 (10.2) illustrates stage C but is a translator's narrowing, not a trigger.

### 3.4 Recommendation and guards against false precision

- **Build.** Build A now. Build B and C only on their triggers (CR 3: a committed document that needs them).
- **Point estimates are flagged**, not forbidden. A conclusion that depends on one says so (7.3).
- **Unknown is vacuous.** A missing chance is 0%–100%, not a guess.
- **No chains.** VE never multiplies along a chain. A chain needs its conditional chances, both `P(H | E)` and
  `P(H | ¬E)`, declared by an estimator. **OPEN (Q-chains)**
- **Every threshold result carries a margin** (7.4), so a decision that turns on a narrow margin is visible.
- **Chance units.** W6 admits at most one `percent` display tag per environment (W6 2.1), so a policy that needs both
  a chance tag and another percentage cannot declare both. The contract change request is a display kind `chance`.
  **OPEN (Q-chance-tag)**
- **Limits of the probabilities.** A chance is an assessment by a named estimator. VE reports whether it is
  coherent with the other chances (EL 2.3) but never whether it is correct (W6 5: hypothetical ratios are not
  measured probabilities). Box bounds over chance estimates are conservative relative to joint constraints (3.3).

## 4. Severity and decision rules (question 3)

### 4.1 Severity classes and their order

The `risk` block declares:

- **A fresh severity sort** whose domain is exactly its declared class constants. The sort must be new to the
  environment (`RiskSeverityNotFresh` otherwise). The generated premises are domain closure,
  `∀s. s = c₁ ∨ … ∨ s = cₙ`, and the distinctness of the class constants; at most 16 classes are allowed. The sort
  is fresh because domain closure bounds its size. Over an existing sort, that bound would be a consequence stated in
  the old vocabulary with no risk predicate in it, which made draft 1's conservativity claim false (fixture k26).
- **Order edges.** "Serious harms are more severe than minor harms." These are closed transitively into a strict
  partial order. A cycle is `DependencyCycle: <classes>` via `VE.Route.dependencyOrder`, as soft-norm ranks are
  checked (soft-norms 1.2).
- **Declared unranked pairs.** "Privacy harms and property damage are not ranked." Undeclared incomparable pairs are
  listed under `unranked_severities`.
- **Harm constants of the harm sort, each with exactly one class**, set by a named decider ("Severity is set by the
  platform team"). Validation rejects a harm with no class, or with two (`HarmUnclassified`, `HarmTwoClasses`).

**The class relation.** `class(h, s)` relates harms to severities. Its premises are that it is **functional** (at
most one class per harm, as a W1 `functional` flag) and the ground fact `class(c, s)` for each named harm constant.
It is **not total**: "every harm has a class" would be an existential premise, which W1's fragment excludes
(norms.md 7.1). Totality is instead an existence fact validated on records (8.1). So in the broader class of models
that document-level checks range over, harm elements that are not named constants may have no class; 4.2 says what
that does to comparisons. The premises constrain the old vocabulary in one way only: two harm constants with
different classes cannot be equal. The conservativity theorem therefore assumes that the old theory does not equate
differently classified harm constants (`risk_expansion`, 8.3).

Harms are **policy constants** and decision records choose among them (`UnknownHarm` otherwise). An agent therefore
cannot grade the severity of its own harms. **OPEN (Q-new-harms):** how a decision reports a harm the policy did not
list. Policy-declared harm kinds were considered in review and are recorded under Q-new-harms as a candidate answer,
not adopted.

The legend reads, for example:

```text
Severity, from most to least severe: severe, serious, minor.
```

### 4.2 The worst-case word

```text
lessWorst(a′, a) := ∃h s. might(a, h) ∧ class(h, s) ∧ ∀h′. might(a′, h′) → ∃s′. class(h′, s′) ∧ moreSevere(s, s′)
```

In English: "`a′` has a less severe worst case than `a`" when `a` might lead to a harm more severe than every harm
`a′` might lead to. An alternative that might lead to no harm has a less severe worst case than any alternative that
might lead to some **classified** harm. On a decision every harm is classified (4.1), so the qualification never
shows there.

**Harms with no class block the comparison**, as an unranked pair does. On `a`'s side an unclassified harm is never
the witness; on `a′`'s side it falsifies the `∀`. So an unclassified harm never makes an alternative look safer or
worse. In particular, an alternative that might lead to no harm does not beat one whose only possible harms are
unclassified, because there is no classified witness. The report then says "not comparable: `<harm>` has no class",
never "equal severity". Class guards behave the same way: a harm with no class is not `severe` and not `<class> or
worse`, so P1 (4.3) does not fire for it. All of this arises only in document-level reasoning, for example in a
DILEMMA witness (fixture k31).

The relation is irreflexive and transitive (`lessWorst_strict`); both follow from the functionality of `class` and the
strictness of the order. It depends only on each alternative's **profile**: the set of classes it might reach, plus
one flag for "might reach an unclassified harm". With an unranked pair or an unclassified harm it can hold in neither
direction, and the report names the pair or the harm as the reason. It ignores certainty and counts: a certain death
and a possible death tie.

Rejected alternatives:

- ranking certain harms above possible harms of the same class (lexicographic);
- set inclusion ("every harm `a′` might lead to, `a` might lead to"), which is already expressible in guards and needs
  no word.

**OPEN (Q-worst-case):** which relation a given source means. In translation this is a reading set.

### 4.3 Rule patterns (ordinary W1 rules; no new rule form)

| Pattern | Canonical VE rule (policy text) | Note |
|---|---|---|
| P1 hard ban | `Every action must not be performed, if there is a harm such that both that harm is severe and that action might lead to that harm.` | No carve-out; the paraphrase says "no confirmation lifts this rule" |
| P2 precaution | `Every action must not be performed, if there is an agent such that both that action is available to that agent and another action available to that agent has a less severe worst case than that action[, unless …].` | Guard over facts, not permissions, so no `GuardOnOwnOutcome` (alt 4.8) |
| P3 tiered precaution | P2 with `… another action available to that agent is acceptable and has a less severe worst case …`, where `acceptable` is a plain regulated predicate decided by lower rules | Stratified, like Asimov's `has_lawful_option` (rules.ve rule 7) |
| P4 confirmation threshold | `…, unless the user has confirmed that action.` on P2, with `confirmed(action)` a base predicate recorded from the user's reply | Serious harms can be confirmed, severe harms cannot (P1 has no carve-out) |
| P5 benefit side | `Every action must not be performed, if that action allows task abandonment to happen.` | `alternatives@0`'s `allows` over certain outcomes |
| P6 likelihood threshold (B) | `…, if the chance that a server outage happens if that action is taken might be more than 1%, unless …` | Regenerated threshold facts |
| P7 expected cost (C) | `… another action available to that agent has a lower expected cost than that action.` | Only on the stage C trigger |

**Theorem `precaution_has_maximal`** (8.3). Under the domain-closure and functional-class premises, every chooser with
an alternative has one that no other alternative beats. The reason is that `lessWorst` depends only on each
alternative's profile (4.2), of which there are finitely many. So P2 alone never creates a dilemma, even over infinite
structures, and document-wide FOLLOWABLE certificates for P2-only policies are expected where the tableau finds them;
it may return UNKNOWN (7.2). With P1, P3 or P5 dilemmas are real, and the followability check of alt 4.6 reports them
(NONE-PERMITTED and so on).

**Confirmation.** Confirmation is not a soft-norm switch: `alternatives@0` with `soft-norms@0` is gated (alt 3.1).
Whose harms a user may confirm (harms borne only by the user versus by third parties) needs a `borne_by(harm,
party)` classification. **OPEN (Q-consent)**

### 4.4 Relation to "preference between actions" (the Asimov OPEN limit)

The README's OPEN items (proportionality between harms; preferring the alternative that meets fewer threats) ask for
a ranking of alternatives. alt 4.8 fixes that priority across actions is never a checker primitive. This plan agrees:

- **Preference is derived.** A preference between actions is derived from declared severity (stage A), bands (B) or
  costs (C) through fixed profile words with fixed bodies. It is then written into W1 guards over facts.
- **Other rankings are explicit choices.** Any other ranking is an attributed author or translator choice:
  - "fewer threats" is an expected-cost rule with equal costs, or a set-inclusion guard;
  - "a certain harm is worse than a possible one" is a W1 precedence choice (10.1).
- **What a preference is not.** Soft-norm ranks remain about rules on one act (soft-norms 4.5), not about actions.
  A named relation `preferred_to(a, b)` stays plain vocabulary with no properties (W6 4, declared ordinal relation).

## 5. Where estimates come from (question 4)

### 5.1 The estimate record

Every estimate is a row of the decision record with these fields. Unknown fields are rejected, and every field is
identity-bound.

| Field | Content |
|---|---|
| `id` | stable token, unique in the log |
| `quantity` / `cell` | a declared quantity name with its unit tag, or an `(action, harm)` cell for a chance |
| `range` | `lo`, `hi` as W6 decimals on the tag's grid (`UnitPrecision` otherwise; chance within 0%–100%) |
| `estimator` | a named party or tool with its version ("memory profiler 2.3", "the build agent", "the on-call engineer") |
| `method` | a short text ("peak over the last 5 runs, plus 20%"). It is shown, never interpreted |
| `basis` | ids of the observations, data snapshots (content hashes) or other estimates it used |
| `support` | W2's kinds: `observation`, `statistical`, `calculation`, `testimony`, `assumption` |
| `recorded` | log sequence number and W6 day |
| `supersedes` | optional id of an earlier estimate of the same quantity or cell |

- **Settings** (`kind: setting`) are exact, belong to one alternative, and are chosen by the chooser.
- **Conditions** and **stated cells** carry an author and a support (a condition is usually `assumption`: it is the
  author's model).
- **Severity, costs and bands** are policy content with their author, identity-bound in the environment like
  `regulated`.

### 5.2 What the checker does with them

It checks each estimate's shape, tags, grid and range. It checks provenance: a missing `estimator`, `support` or
`recorded` is `EstimateProvenance: <id> <field>`. It checks policy provenance requirements, for example "The peak
memory of a job must be estimated by the memory profiler" (`EstimatorNotAllowed`). It then computes 2.3 and 3.2–3.3 and
nothing else.

In a W2 document an estimate can also be an `attributed` unit (the estimator estimates …). Accepting it as true is a
bridge leaf, as for any attribution (W2).

### 5.3 Two estimates of one quantity

If a record cites two estimates of one quantity, neither superseded before the decision (supersession is judged on
the log as it stood at decision time), the policy's declared combination rule applies:

- `latest` uses the one recorded later;
- `hull` uses the smallest range covering both (precautionary);
- `intersection` treats both as true, and an empty intersection is an inconsistency.

Otherwise the record is `ConflictingEstimates: <quantity>`. VE never picks a combination rule.

## 6. Auditing past decisions (question 5)

### 6.1 The log

The log is append-only and hash-chained. Each entry has a sequence number, a day and one of these kinds:

- `estimate`, `setting`, `condition`, `statement`, `supersession`;
- `instruction`: a user's confirmation, with the party;
- `decision`: the decision record and its risk-report id;
- `taken`: the alternative taken;
- `outcome`: observed harms and measured quantities, with observer and support `observation`.

W6 has days but no clock time (W6 6.2), so order within a day is the sequence number. **OPEN (Q-clock)**

### 6.2 What the log must record for each decision

- **The decision:** its id, sequence, day, chooser and the policy's `(environment_id, document_hash)`.
- **The alternatives:** every declared alternative with its inaction and settings. This is `alternatives_declared`,
  "alternatives considered so far" (alt 5.3).
- **The model:** the harms considered, every estimate, condition and stated cell cited (ids and content hashes), and
  the instructions received before the decision.
- **The result:** the risk report id (bound to all of the above) and the checker build; later, the `taken` entry.

Every entry the decision cites must have a smaller sequence number than the decision. A later entry is
`HindsightEntry: <id>`, and the record is NOT REPLAYABLE. The `taken` entry is exempt: the decision does not cite it;
it names the decision and comes after it.

### 6.3 The audit questions and verdicts

| Question | Method | Verdicts |
|---|---|---|
| 1. Was the taken alternative permitted given what the agent used? | Replay the risk check on the decision's own snapshot | `PERMITTED AT DECISION TIME` (clear / permitted but not clear, with the reason) · `FORBIDDEN AT DECISION TIME` (a breach, alt 4.3) · `NO CLEAR ACTION AT DECISION TIME` (the recorded dilemma) · `NOT REPLAYABLE` (missing, altered or later entry) |
| 2. Did the agent use what was recorded? | Replay with every estimate of the same quantities and cells recorded before the decision and not superseded by then (judged on the log as it stood at decision time), combined by 5.3 | `SAME VERDICT WITH ALL RECORDED ESTIMATES`, or `DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: <estimate ids not used>`. A policy may make using them mandatory; an unused mandatory estimate is then reported on its own line, `PROCEDURE BREACH: estimate <id> not used (the agent's fault)`, and the Q1 verdict is unchanged |
| 3. Did the declared model survive the outcome? | Compare each `outcome` entry with the decision-time cells | per observed harm: `within the declared model` (it was `might`) · `surprise: ruled out by <condition / statement>`, naming the estimate a measured quantity contradicts (observed 5 GB outside E2's 8–10 GB) · `unexamined: ruled out by <decider>` (2.4) |
| 4. How often are an estimator's ranges wrong? | Counts of surprises per estimator across audits | Evidence-layer ledger (EL 2.x); outside certification |

The verdict of question 1 never reads an outcome. A bad outcome after a permitted decision is not a violation, and a
good outcome after a forbidden decision is still a breach. A single outcome neither confirms nor refutes a chance.
Q1 is the substantive verdict, reproducible from the decision's snapshot. A PROCEDURE BREACH says the agent did not
follow the policy's recording procedure; it is reported beside Q1, never folded into it. NOT REPLAYABLE is kept for
entries that are missing, altered or recorded after the decision.

### 6.4 The no-hindsight rule, mechanically

The Lean audit function takes a `Snapshot`, which has no outcome field, and the alternative being asked about. It
admits the snapshot only if every cited entry precedes the decision. The `taken` entry selects which alternative Q1
asks about, but it is not an input to the verdict. Theorem `verdict_ignores_outcomes` states that, for the same
decision and the same queried alternative, the Q1 and Q2 verdicts computed from logs that agree up to the decision's
sequence are equal. It is structural: the snapshot extracted from both logs is identical. Q3 reads outcomes by design
and is outside the theorem. Two logs that take different alternatives after the decision ask about different
alternatives and may get different Q1 verdicts; that is the query changing, not hindsight (fixture k32).

## 7. What the checker reports (question 6)

### 7.1 The decision report (scenario)

The report first checks the regenerated conflict formulas on the decision (alt 4.7). If none holds, it gives, per
alternative:

- **status**: permitted, forbidden, required; UNDECIDED once the P1 `unspecified` default lands (11);
- **the deciding rules** by number;
- **the worst case** with its class;
- **for each `might`**: the witness case and the estimates it came from;
- **for each `cannot` or `leads to`**: the condition and the endpoints that decided it;
- **why the alternative is clear or not** (alt 4.6);
- **margins** (7.4).

Then it gives the clear actions, "the policy does not choose among them" when there are several, the gap lines
(7.2) and `conditional_on`. The report is bound to `(environment_id, document_hash, decision_record_id)` and never
says FOLLOWABLE (alt 4.7).

### 7.2 Document report, conflicts and gaps

The policy's own checks are `alternatives@0`'s: conflict status, then followability only on CONFLICT-FREE. They run
over structures satisfying the risk slot premises (8.1). In those structures regenerated facts are unconstrained base
predicates, and harm elements other than the named constants may have no class (4.1), so certificates hold for every
decision a valid record could produce (alt 4.2's broader class). Unlike the decision report, which is decided by
finite evaluation, these checks keep alt's three values: a certificate, a witness, or UNKNOWN with the budget named
(alt 4.6).

Gap and conflict lines:

| Line | Meaning |
|---|---|
| `inconsistent` | `RiskInconsistent` / `SufficientOutsideNecessary` / `ChanceAgainstPossibility`, with the case and the sources |
| `unexamined_possible`, `assumed_ruled_out` | completed cells (2.4), with the decider |
| `unranked_severities` | a worst-case comparison that could not be made, naming the pair; in a document-level witness also a harm with no class (4.2) |
| `no_chance_estimate` | `might` cells with the vacuous chance (stage B and later) |
| `point_estimates` | conclusions that hold only because an estimate is a point |
| `default_decided` | alternatives whose status came from the completion default, not a rule (the P1 finding: `default: allow` silently permits) |
| `required_alternative_missing` | a policy-required alternative is absent ("every decision to run a program lists running it with a memory limit"), validated on records like alt existence facts |
| `conflicting_estimates`, `hindsight_entries` | 5.3, 6.2 |
| `dilemmas` | alt 4.6 diagnoses |

### 7.3 Point estimates

For every `leads to` or `cannot` result, the report names each point estimate among the quantities of the deciding
condition. Settings are not named, because they are exact by choice. This is a report property: a single number
standing in for an uncertain quantity is where false certainty enters.

### 7.4 Margins

For each estimate endpoint and each alternative, a margin is a value of that endpoint alone, with every other estimate
fixed, at which the alternative's **status** changes. Point estimates are included (7.3): moving one endpoint makes
the estimate non-point.

- **Full admission at every value tried.** The perturbed record is validated again in full: `lo ≤ hi` and chances
  within 0%–100%; `S → N` at every valuation (`SufficientOutsideNecessary`, `RiskInconsistent`); separability, which a
  point estimate loses when it occurs in two comparisons of one condition and an endpoint moves
  (`RiskConditionShared`); then the regenerated conflict formulas (alt 4.7). The report keeps three results apart:
  **changes at X** (a status change), **record invalid at X** (with the diagnostic) and **conflict at X**. An invalid
  or conflicting record is never reported as a status change (fixture k27).
- **Candidates.** Admission outcomes and statuses are piecewise constant in one endpoint, with breakpoints only at the
  comparison thresholds involving it. The values tried are each threshold and its grid neighbours on both sides,
  because a strict comparison changes one grid step from its threshold. In decision 17, "the memory limit is greater
  than the free memory of the server" has its threshold at 7 GB, but the memory-limited run's status changes at E2's
  lower bound 6 GB (6.9 GB on a 0.1 GB grid); a search at thresholds alone finds nothing (fixture k28).
- **What is certified.** Lean re-evaluates the reported value, a checkable witness that the status differs there;
  the report says "changes at". It says "nearest" or "no single valid change" only if Lean has evaluated every
  candidate, which certifies minimality by `status_piecewise_constant`. **OPEN (Q-margin-proof):** whether stage A
  ships that certified candidate check or only "changes at"; item 1 decides.
- **How it is rendered.** "Changes at: E2's lower bound 6 GB (now 8 GB)."
- **Guard facts versus status.** Margins are on statuses, not on single guard facts: a guard fact can flip without
  changing the status when another rule still decides it (the OOM case shows one).
- **Stage C.** For linear expected-cost thresholds the report adds the joint L∞ radius of that one inequality (slack
  divided by the sum of absolute coefficients), with three qualifications. It is a real-valued bound, rounded down to
  whole steps of the chance grid. Near the domain boundaries (0%, 100%, `lo ≤ hi`) part of the region it describes is
  not valid records, so it is not a distance to a valid change. It ignores joint constraints between chances (3.3), so
  it is conservative relative to them.
- **What is not claimed.** Robustness to several estimates moving at once is not claimed for statuses.

## 8. Lean and decidability (question 7)

### 8.1 What is decided, and what may be UNKNOWN

| Component | Decided? | Evidence |
|---|---|---|
| Cells from separable conditions | Decided: ground linear integer arithmetic at interval endpoints, with the ±1 rule for `=` and `≠` | Lean evaluation, `possibleE_iff` / `certainE_iff` |
| Severity order, `lessWorst`, domain closure | Decided on decisions: finite relations over declared constants | Regenerated tables; `dependencyOrder` |
| Bands, thresholds, expected cost | Decided: ground rational arithmetic on integer grids (exact scaling); box bounds conservative relative to joint constraints | Lean evaluation |
| Decision report | Decided: finite model evaluation after regeneration | `alternatives@0` scenario evaluation (alt 4.7) |
| Policy conflict and followability | **Not decided in general**: the unchanged W1 / `alternatives@0` tableau gives a certificate, a witness or UNKNOWN | Certificates over `BaseAdmissibleRisk` |
| Margins | Decided per value tried: finitely many candidates per endpoint, each re-admitted in full | Witness re-evaluation; minimality only with the certified check (7.4) |
| Chance coherence (B and later) | **Not decided in general**: EL's atom LP keeps UNKNOWN atoms possible and may be a relaxation | EL 2.3, entered by certificate only, with EL's verdict kinds |

**Slot premises** (Background slot `risk`, after `alternatives`, universal or ground only, as in alt 4.2):

- `certain_possible`;
- over the fresh severity sort: domain closure and distinctness of the class constants; strictness and transitivity
  of the closed order (ground);
- `class` functional (at most one class per harm), and the ground class fact of each named harm constant;
- threshold monotonicity (ground).

These are all the constraints the policy's classification and order put on document models; `class` is not total
(4.1). By `risk_expansion`, their only consequence in the old vocabulary is that differently classified harm constants
differ.

**Existence facts**, validated on records and never assumed: every harm has a class, and every cell is addressed or
completed.

**Excluded:**

- `$int` quantifiers in norm guards (norms.md 0, W6 3.2);
- products of estimated quantities;
- real numbers, densities and continuous distributions;
- probability inside formulas;
- sequential decisions beyond independent choosers (alt 4.10 stage 2);
- non-separable conditions until item 7.

### 8.2 Trust split

**Trusted (Lean, proved from raw JSON under the unchanged allowlist):**

- the `risk` block decoder;
- W6 decimal lowering, reused;
- the endpoint evaluator and cell regeneration;
- the severity closure;
- the profile-word inlining;
- the slot generator;
- the audit snapshot admission;
- the `ve_risk_route` executable.

**Untrusted:**

- Python's shape check, surface and dispatch;
- rendering of reasons, witnesses and margins;
- the margin candidate search (Lean re-evaluates every reported value);
- Rust's evaluation (differential only).

Integers are unbounded in all three languages; Rust uses big integers as W6 does for 40-digit literals. Trust-cost
line for ROADMAP: "Risk (`risk@0`): new trusted decoder, cell regenerator, severity closure, slot premises and
`ve_risk_route`; untrusted: rendering, the margin candidate search (minimality only if Lean checks every candidate),
Rust evaluation."

### 8.3 Files and statement schemata

The files are `lean/VE/Risk/{Decl,Estimate,Derive,Severity,Words,Background,Report,Audit,Wire,Run}.lean` plus
`lean/RISK.md`, and later `Expected.lean` for stage C. The frozen `Norms/*`, `Alternatives/*`, `Route/*` and P0
files are untouched. Names use the prefix `VE.Risk.` and contain no primes.

```lean
namespace VE.Risk
structure Box    -- quantity name ↦ (tag, lo, hi), lo ≤ hi; settings have lo = hi
inductive Cond   -- atom (LinExpr ⋈ 0), ⋈ ∈ {<, ≤, =, ≠} | and | or | not | top | bot, W6-tagged
def InBox (b : Box) (v : Valuation) : Prop
def Separable (b : Box) (c : Cond) : Bool          -- no non-point quantity in two atoms (after NNF)
def UnitCoefficients (b : Box) (c : Cond) : Bool   -- every = and ≠ atom has coefficient ±1 on each non-point quantity
def possibleE (b : Box) (c : Cond) : Bool          -- endpoint evaluation
def certainE  (b : Box) (c : Cond) : Bool

theorem possibleE_iff (b c) (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
  possibleE b c = true ↔ ∃ v, InBox b v ∧ c.holds v
theorem certainE_iff  (b c) (hs : Separable b c = true) (hu : UnitCoefficients b c = true) :
  certainE b c = true ↔ ∀ v, InBox b v → c.holds v

def Completed (R : RiskDoc) (d : Decision) (v : Valuation) (H : Cell → Bool) : Prop
  -- InBox d.box v ∧ ∀ cell, (Suff d cell v → H cell) ∧ (H cell → Nec d cell v); defaults Suff = ⊥, Nec = ⊤ (2.2)
def regenerate (R : RiskDoc) (d : Decision) : Tables  -- might_lead_to, leads_to, class tables, threshold facts
theorem regenerate_sound (R d) (hv : validateDecision R d = .ok ()) (a h) :
  ([a, h] ∈ (regenerate R d).might ↔ ∃ v H, Completed R d v H ∧ H (a, h) = true) ∧
  ([a, h] ∈ (regenerate R d).leads ↔ ∀ v H, Completed R d v H → H (a, h) = true)
theorem certain_within_possible (R d) (hv) : (regenerate R d).leads ⊆ (regenerate R d).might
theorem severity_strict (R) (h : WellFormedRisk R = true) : StrictPartialOrder (moreSevereClosure R)
theorem lessWorst_strict (R) (h) (B) (hB : BaseAdmissibleRisk R B) : Irreflexive (LessWorst R B) ∧ Transitive (LessWorst R B)
  -- uses the functional-class premise carried by BaseAdmissibleRisk
theorem precaution_has_maximal (R) (h) (B) (hB : BaseAdmissibleRisk R B) (r) (hne : ∃ a, Avail B a r) :
  ∃ a, Avail B a r ∧ ¬ ∃ a', Avail B a' r ∧ LessWorst R B a' a
  -- LessWorst depends only on profiles: the classes reached plus an unclassified flag
theorem risk_inline_faithful   -- the two defined words (0), as alt's inline_faithful, over S.Admissible
theorem risk_expansion (R) (h) (B₀) (hB₀ : BaseAdmissibleAlt (toAlt R) B₀) (hc : Compat R B₀) :
  ∃ B, BaseAdmissibleRisk R B ∧ B.reduct = B₀
  -- Compat: B₀ does not equate harm constants with different classes; WellFormedRisk makes the severity sort fresh
theorem risk_conservative      -- over the old signature: a formula mentioning no risk symbol follows with the risk
                               -- premises iff it follows with the Compat facts alone (from risk_expansion)
theorem risk_scenario_sound    -- the decision report = alt scenario evaluation on the regenerated model
theorem status_piecewise_constant (R d e) : admission outcome and status are constant between consecutive candidates
  -- of endpoint e: the thresholds involving e and their grid neighbours
theorem verdict_ignores_outcomes (R) (log₁ log₂) (hd) (a) (hsame : prefix log₁ hd.seq = prefix log₂ hd.seq) :
  auditQ12 R log₁ hd a = auditQ12 R log₂ hd a   -- Q1 and Q2, same decision, same queried alternative a; not Q3
theorem risk_wire_acceptance / risk_wire_scenario_sound / risk_wire_audit_sound   -- raw JSON, as alt's wire theorems
-- stage C (Expected.lean): expected_range_exact (min/max of a linear form over the chance box; conservative
-- relative to joint constraints), dominance_sound
```

`BaseAdmissibleRisk R B := BaseAdmissibleAlt (toAlt R) B ∧ Sat B (riskPremises R)`. The policy's conflict and
followability theorems are alt's `alt_conflict_free` and `followable_sound`, restated over it. That makes explicit
the dependency the review must check: `alternatives@0` item 2's Lean must be merged first.

## 9. Worked example: the out-of-memory decision (agent policy)

### 9.1 The policy (a norm document over an environment with the `alternatives` and `risk` blocks)

The environment and legend:

- **Sorts:** `agent` (chooser), `action`, `harm`; the `risk` block adds the fresh sort `severity` (4.1).
- **The `alternatives` block:** as in the Asimov environment, `performed` = (`permitted`, `required`),
  `outcomes: signed`, `inaction`, `taken`.
- **The `risk` block:**
  - classes `severe`, `serious`, `minor`, with severe > serious > minor, set by the platform team;
  - the harm constants below;
  - `unexamined: {"ruled_out_by": "the deciding agent"}` with `always_possible: ["severe", "serious"]`;
  - estimate combination `hull`;
  - required alternatives for decisions that run a program: a memory-limited run and the inaction;
  - required estimator for the peak memory of a job: the memory profiler.

The legend generated from these blocks:

```text
Each agent faces one choice among the actions available to it and takes at most one of them.
"<action> might lead to <harm>" means the declared estimates, conditions and statements do not rule the harm out.
"<action> cannot lead to <harm>" means they rule it out. "<action> leads to <harm>" means it happens in every case they allow.
An unexamined severe or serious outcome counts as possible; the deciding agent rules out other unexamined outcomes.
Severity, from most to least severe: severe, serious, minor. Severity is set by the platform team.
Data loss is severe. A server outage is serious. A job failure is minor. A task delay is minor. Task abandonment is minor.
<a> has a less severe worst case than <b> when <b> might lead to a harm more severe than every harm <a> might lead to.
By default, an action may be performed.
```

The rules:

```text
Rule 1. Every action must not be performed, if there is a harm such that both that harm is severe and that action
might lead to that harm.
Rule 2. Every action must not be performed, if there is an agent such that both that action is available to that
agent and another action available to that agent has a less severe worst case than that action, unless the user
has confirmed that action.
Rule 3. Every action must not be performed, if that action allows task abandonment to happen.
```

The policy's checks:

- **Conflict:** CONFLICT-FREE is expected (all three rules forbid; no permission rule).
- **Followability:** not FOLLOWABLE document-wide. Rule 1 alone is refuted by a record in which every alternative
  might lead to data loss (NONE-PERMITTED). That witness is what "severe risks have no safe alternative here" looks
  like, and it is correct to show it.
- **Rule 2:** P2 with P4, so by `precaution_has_maximal` it alone never creates a dilemma.

### 9.2 Decision 17 (a scenario record, rendered)

```text
Decision 17 of the build agent, log entry 41, 2026-09-29. Policy agent-ops (document hash …).
Available actions: running the job; running the job with the memory limit; asking the user; not running the job (inaction).
E1. The peak memory of the job is from 6 GB through 12 GB, including both bounds.
    [memory profiler 2.3; peak of the last 5 runs plus 20%; statistical; entry 38]
E2. The free memory of the server during the job is from 8 GB through 10 GB, including both bounds.
    [server monitor; minimum over the last hour; observation; entry 40]
S1. The memory limit equals 7 GB.                      [setting of "running the job with the memory limit"]
C1. Running the job cannot lead to a server outage unless the peak memory of the job is greater than the free memory
    of the server.                                     [the build agent; assumption]
C2. Running the job with the memory limit cannot lead to a server outage unless the memory limit is greater than the
    free memory of the server.                         [the build agent; assumption: the limit is enforced by the kernel]
C3. Running the job with the memory limit leads to a job failure exactly when the peak memory of the job is greater
    than the memory limit.                             [the build agent; assumption]
C4. Running the job cannot lead to a job failure unless the peak memory of the job is greater than the free memory of
    the server.                                        [the build agent; assumption]
T1. Asking the user leads to a task delay.             T2. Not running the job leads to task abandonment.
T3. Asking the user cannot lead to a server outage.    T4. Not running the job cannot lead to a server outage.
T5–T8. Running the job cannot lead to data loss. (and one sentence each for the other three actions)
                                                        [platform team: jobs write only to scratch space; testimony]
```

Unit tag `gb`: scale 1, decimal label "GB". C1–C4 are separable, since each has one comparison. The regenerated
cells:

| Action | Server outage (serious) | Job failure (minor) | Other harms | Worst case |
|---|---|---|---|---|
| running the job | might (C1: 12 > 8; witness 12, 8) | might (C4) | data loss cannot (T5); delay and abandonment ruled out by the agent | serious |
| running the job with the memory limit | cannot (C2: 7 > 8 fails in every case) | might (C3: 12 > 7), not certain (6 ≤ 7) | as above | minor |
| asking the user | cannot (T3) | ruled out by the agent | delay leads (T1) | minor |
| not running the job | cannot (T4) | ruled out by the agent | abandonment leads (T2) | minor |

The expected report:

```text
Decision 17 — conditional on E1, E2, S1, C1–C4, T1–T8 and the build agent's ruled-out cells (8 listed).
running the job: forbidden by rule 2. Worst case: a server outage (serious). A server outage is not ruled out: by C1
  it needs the peak memory of the job (6 GB through 12 GB, E1) to be greater than the free memory of the server
  (8 GB through 10 GB, E2), for example 12 GB and 8 GB. Running the job with the memory limit has a less severe
  worst case (a job failure, minor). The user has not confirmed running the job.
  Changes at: E1's upper bound 8 GB (now 12 GB). No change found at the other endpoints.
running the job with the memory limit: permitted (by default); clear. Worst case: a job failure (minor): by C3 it
  happens exactly when the peak memory is greater than 7 GB, for example 12 GB; not at 6 GB. A server outage is ruled
  out by C2: 7 GB is not greater than the free memory in any case E2 allows.
  Changes at: E2's lower bound 6 GB (now 8 GB): the outage would no longer be ruled out, and rule 2 would forbid it.
  Changes at: E1's upper bound 8 GB (now 12 GB): running the job would then have no possible harm, and rule 2 would
  forbid this run.
asking the user: permitted (by default); clear. Worst case: a task delay (minor).
  Changes at: E1's upper bound 8 GB (now 12 GB), for the same reason.
not running the job: forbidden by rule 3: it leads to task abandonment (T2), and running the job with the memory limit
  might not lead to it (ruled out by the build agent). No change found.
Clear actions: running the job with the memory limit; asking the user. The policy does not choose between them.
default_decided: running the job with the memory limit, asking the user (permitted because no rule forbids them).
```

The report is shown in the "changes at" form (7.4). With the certified candidate check it would say "nearest" and "no
single valid change" where it now says "no change found".

The margins show why they are taken on statuses. Moving E2's lower bound down to 6 GB changes the memory-limited
run's status but not that of running the job, because asking the user still has a less severe worst case. Moving E1's
upper bound down to 8 GB changes three statuses at once: running the job could then lead to no harm, so it has a less
severe worst case than every other action (4.2) and becomes the only clear action. Raising E2's lower bound to 12 GB
would clear running the job, but E2's upper bound is 10 GB, so that record is invalid (`lo > hi`), not a status change.

**Decision 18: after asking.** The user replies "run it without a limit" (an `instruction` entry, sequence 44).
Decision 18 is a new chooser with alternatives running the job, running the job with the memory limit and not
running the job, and `the user has confirmed running the job`. Rule 2 is silent on running the job, so it is
permitted by default; Rule 1 does not apply. Expected: **clear = running the job, running the job with the memory
limit**. The report adds "running the job is permitted only because the user confirmed it; its worst case is still
a server outage (serious)". Had the job been able to cause data loss, no confirmation would have helped (Rule 1).

**Variant: shared server (fixture k11).** Rule 2's carve-out becomes "unless the user has confirmed that action and
every harm that that action might lead to is borne only by the user". An outage of a shared server is then not
confirmable. This needs `borne_by` (**OPEN (Q-consent)**).

### 9.3 The audit

The agent took the memory-limited run (entry 42). Entry 57 is an outcome: "A server outage happened. The free memory
of the server fell to 5 GB when a second job started." [server monitor; observation]. The log also holds entry 39,
from the scheduler: "The free memory of the server during the job is from 4 GB through 10 GB, including both bounds."
[a second job is scheduled during the run; calculation]. Decision 17 did not cite entry 39.

```text
Q1  PERMITTED AT DECISION TIME: running the job with the memory limit was clear given E1, E2, S1, C1–C4, T1–T8.
Q2  DIFFERENT VERDICT WITH ALL RECORDED ESTIMATES: entry 39 was recorded before the decision and not used. Under the
    policy's hull rule free memory is 4 GB through 10 GB; C2 no longer rules out a server outage (7 > 4), rule 2 then
    forbids the memory-limited run, and the only clear action is asking the user.
Q3  surprise: a server outage was ruled out by C2 under E2; the observed free memory (5 GB) is outside E2 (8–10 GB).
    Estimate E2 (server monitor) is contradicted; condition C2 is not.
Not concluded: that the decision was wrong because an outage followed.
```

If the policy had required every recorded estimate of a cited quantity to be used, Q1 would still read PERMITTED AT
DECISION TIME, because it is reproduced from the decision's own snapshot, and the audit would add a separate line:

```text
PROCEDURE BREACH: estimate 39 not used (the agent's fault)
```

The finding would then be the agent's, not the monitor's. NOT REPLAYABLE is kept for entries that are missing,
altered or recorded later: citing entry 57 in a replay of decision 17 is `HindsightEntry: 57`. The `taken` entry 42
follows the decision without being flagged, because the decision does not cite it (6.2).

## 10. Worked examples: Asimov

Both cases use the Asimov environment extended with a `risk` block. Each case has its own policy variant, written by
the Asimov case annotator, whose `risk` block declares the classes `fatal` > `injuring` (set by the annotator), the
case's harm constants with their classes, and `unexamined: possible`. Harm constants and classes are policy content
(4.1), so they sit in these variants, not in the scenarios. Every rule beyond the source is an **attributed
narrowing** and sits in a reading set beside the source-faithful reading, which keeps the dilemma. Asimov gives no
severity order, cost or chance.

### 10.1 Case A1: weighing harms (injury versus death)

The robot can push a person clear of a falling beam, or do nothing (the inaction). The A1 policy variant declares the
harm constants the person's death (fatal) and the person's bruising (injuring). The annotator's statements in the
scenario:

- "Doing nothing leads to the person's death."
- "Doing nothing cannot lead to the person's bruising."
- "Pushing the person might lead to the person's bruising."
- "Pushing the person cannot lead to the person's death."
- Both are harms to a human being.

```text
Rule 1 (Law 1, "injure", possibility reading). Every action must not be performed, if there is a harm such that
both that harm is a harm to a human being and that action might lead to that harm.
Rule 2 (Law 1, "through inaction", rule 7′ of alt 2.6). Every action must not be performed, if there is a harm such
that both that harm is a harm to a human being and that action allows that harm to happen.
Rule 3 (exception to rule 1; the translator's "lesser harm" narrowing, no source text). Every action may be
performed, if there is a robot such that both that action is available to that robot and it is not the case that
another action available to that robot has a less severe worst case than that action.
```

| Rule set | Expected |
|---|---|
| {1, 2} | Pushing is forbidden by Rule 1 (might injure); doing nothing by Rules 1 and 2. NONE-PERMITTED, a document DILEMMA: the README's OPEN, made visible |
| {1, 2, 3}, this scenario | Pushing (worst case injuring) is not beaten, so Rule 3 permits it over Rule 1. Rule 2 does not apply, because pushing does not certainly lead to the bruising. **Clear: pushing** |
| {1, 2, 3}, document | **CONFLICT.** In a structure where both alternatives' worst cases are fatal and doing nothing certainly leads to a death the other might avoid, Rule 3 permits doing nothing and Rule 2 forbids it. Witness rendered: "doing nothing: rule 3 permits (no alternative has a less severe worst case); rule 2 forbids (it allows the death, which pushing might avoid)" |
| {1, 2 (exception to rule 3), 3} | The author's (not Asimov's) choice that "a death another action might avoid is never excused". CONFLICT-FREE is expected. Not FOLLOWABLE: two actions each certain to kill a different person give NONE-PERMITTED. The checker does not resolve trolley problems; it shows them |

### 10.2 Case A2: competing threats, and what each stage adds

P faces death and Q faces injury, and the robot can rescue only one. The A2 policy variant declares the harm constants
P's death (fatal) and Q's injury (injuring).

- **Rescuing P:** P's death might still occur, because the rescue might fail (stated "might"); Q's injury is certain.
- **Rescuing Q:** P's death is certain; Q's injury is ruled out.
- **Doing nothing:** leads to both.

| Stage and rule set | Expected |
|---|---|
| A, {1, 2 (exception to rule 3), 3} | All three worst cases are fatal, a tie, so Rule 3 permits all. Rule 2 forbids rescuing Q (it allows P's death, which rescuing P might avoid), rescuing P (it allows Q's injury, which rescuing Q avoids) and doing nothing. NONE-PERMITTED, DILEMMA. Stage A cannot weigh a possible death against a certain injury, and it says so |
| A, {1, 3} | All permitted and clear, a tie at fatal. "The policy does not choose" |
| C, {1, 4, 5}: costs fatal 100 points and injuring 10 points, with additive loss (translator's), chance "The chance that P's death happens if rescuing P is taken is from 5% through 20%." (the robot's rescue model, estimator) | Rule 4 (P7): "Every action must not be performed, if there is a robot such that both that action is available to that robot and another action available to that robot has a lower expected cost than that action." Rule 5 (exception to rule 1): the same guard, negated, with "may". EC(rescue P) = 100×[5%, 20%] + 10 = [15, 30]; EC(rescue Q) = 100; EC(nothing) = 110. **Clear: rescuing P.** Margin, on rescuing Q's status: "rescuing Q would no longer be forbidden if the upper bound of the chance that P's death happens if rescuing P is taken reached 90% (now 20%)", since 100p + 10 < 100 iff p < 90%. At 90% the intervals meet, neither alternative dominates, and both rescues are clear |

Under `risk@0`, "rescuing P might prevent P's death" holds, and "Rescuing P prevents P's death." is rejected with that
rewrite (2.5, fixture k29). Alt's rule 8 on this case, under each fulfilment body, is fixture k30.

The README's other OPEN item, ranking threats to the robot, is fixture k22. A severity order over threats works with
P3 in stage A. Preferring fewer threats works with a set-inclusion guard in stage A, or equal costs in stage C.
Neither is in the source.

## 11. Relation to the rest of VE

- **`alternatives@0` and W1.** `risk@0` requires `alternatives@0` (hence `norms@0`) and adds:
  - a `risk` block (identity-bound; `environment_id` changes only for environments carrying it) with a fresh severity
    sort;
  - one Background slot;
  - the base predicate `might_lead_to` and two defined words, inlined as alt 4.3 does;
  - the fulfilment body `excludes` and the `might prevent` form of `prevents` (2.5);
  - regenerated scenario tables.

  No definition in W1 or `alternatives@0` changes. In risk environments four of alt's paraphrases are regenerated
  with "might not lead to", and bare `prevents` is rejected (2.5). Stage 2 of alt 4.10 (traces) remains separate; the
  ask-then-run sequence here is two unlinked choosers.
- **Soft norms.** They are gated with `alternatives@0` (alt 3.1), so "should" risk rules wait for the composition
  proof, and confirmation is a base-predicate carve-out (4.3).
- **W6.** Reuses tags, W6 decimal lowering, same-tag linear arithmetic and the interval wording "from … through …,
  including both bounds". Quantities never reach a norm guard: they are consumed by regeneration. Contract change
  request: the `chance` display kind (3.4).
- **Evidence layer.** Chance coherence and narrowing (EL 2.3) and estimator calibration ledgers (6.3 Q4) are EL's.
  This plan only consumes their certificates, with EL's qualifications (3.2).
- **ARCH-ROADMAP P1 "unspecified default".** A risk policy with `By default, an action may be performed.` silently
  permits every alternative no rule addresses. Until the third default lands, the report lists them
  (`default_decided`). Once it lands, `unspecified` makes them UNDECIDED and not clear. That design is norms'
  (after rights merges) and this plan does not pre-empt it.
- **ARCH-ROADMAP P1 limits contract.** Proposed per-decision limits: 16 alternatives, 32 harms, 64 estimates and
  settings, 128 conditions and statements, `MAX_NODES` per condition, 16 classes, 8 bands. All are in the shared
  table and checked before evaluation.

## 12. Staged build plan and fixtures

| # | Item | Gate / trigger | Notes |
|---|---|---|---|
| 0 | Astra + Fable review of this plan | done 2026-09-29: REVISE, converged; draft 2 applies it (15) | No further plan round |
| 1 | `docs/spec/risk.md`, stage A: block, record format, wordings, 2.2–2.5, severity, words, slot premises, report, audit, diagnostics, Lean statements, fixtures k1–k32 with expectations separated from definitions (as alt 8.1/8.2) | after 0; its statement review after 1a's results and before 2. Draft 1 written 2026-09-29; it proposes the certified check for Q-margin-proof (risk.md 11.11) | Depends on `alternatives@0` item 2 Lean for the restated theorems. The statement review rechecks completed cases (2.2), the endpoint theorems' hypotheses (2.3), the `might prevent` and `excludes` wording and the fulfilment choice (2.5), and admission of perturbed records in margins (7.4); it decides Q-margin-proof |
| 1a | Wording probe (2.6) | after 0, in parallel with 1; results before 1's statement review. Ran 2026-09-29: c5 pending wording, c10 legend-dependent, `leads to` stays | Proxy readers, labelled "human readability unmeasured"; does not replace item 8. The reviewers owe c5's replacement, probed once with new sealed items |
| 2 | Lean `lean/VE/Risk/*`, `ve_risk_route`, `lean/RISK.md`, ROADMAP trust-cost line | after 1's review | Lean-only semantics |
| 3 | Python surface (`ve/surface/risk.py`), block shape check, dispatch, gap lines; Rust untrusted evaluator; differential (200 random records, including separable-condition generators) | parallel with 2 | Surface fixtures (k19) before acceptance |
| 4 | Use case `usecases/agent-oom/` (policy, decisions 17 and 18, the log, audit) and Asimov A1 and A2 as reading sets beside the merged rules | after 2 and 3 | Every narrowing attributed |
| 5 | Stage B: bands, chance estimates, threshold facts, coherence via EL | **trigger:** a committed policy with graded likelihood words and ranges | |
| 6 | Stage C: costs, expected cost, dominance, joint margins | **trigger:** a committed document with numeric tradeoffs; A2's stage C row is a narrowing, not a trigger | |
| 7 | Non-separable conditions (`order@0` certificates, witnesses), policy-level condition templates, event chains | **trigger:** a committed record whose model needs them | Templates also need the `order@0` × n-ary route |
| 8 | W8: `declare_estimate`, `add_condition`, paraphrases with witness cases, margins in plain English | after 4 | The full fidelity gate for Q-wording; 2.6 is a proxy probe before it |

Fixtures for items 1–4 (definitions and expected results; the spec separates them):

| # | Definition | Expected |
|---|---|---|
| k1 | E1 6–12 GB, E2 8–10 GB; the C1 form | `might`, witness (12, 8) |
| k2 | E2 8–10 GB; E1 as 11–12, then 6–8 | certain (sufficient form: 11 > 10) / ruled out (necessary form: 8 ≤ 8) |
| k3 | One estimated quantity in two comparisons of one condition | `RiskConditionShared: <quantity>` |
| k4 | A setting repeated in two comparisons | Accepted (points repeat) |
| k5 | `equals` with coefficient 2 on an estimated quantity: `2·q = 1`, `q` from 0 through 1 | `RiskEqualityCoefficient`. In Lean, endpoint evaluation alone answers "possible" (0 in [−1, 1]) though no case satisfies it, and for `2·q ≠ 1` answers "not certain" though every case satisfies it: the reason for the ±1 hypothesis of `possibleE_iff` and `certainE_iff` |
| k6 | `S` true where `N` is false | `SufficientOutsideNecessary`, with the case |
| k7 | Stated `might` plus a derived ruled-out cell | `RiskInconsistent` |
| k8 | An unaddressed serious cell under `always_possible` / a minor cell under `ruled_out_by` | `might` listed in `unexamined_possible` / `cannot` listed in `assumed_ruled_out` |
| k9 | Severity cycle; an unranked pair in a comparison | `DependencyCycle: <classes>`; `unranked_severities` naming the pair, with `lessWorst` false both ways |
| k10 | Decision 17 | As in 9.2, including margins and `default_decided` |
| k11 | Decision 18; the shared-server variant | clear = run and memory-limited run; the variant is OPEN pending `borne_by` |
| k12 | Point estimate E1 = 12 GB | Memory-limited run `leads to` a job failure; `point_estimates` names E1 |
| k13 | Audit of decision 17 (entries 38–57); then the same with a policy requiring every recorded estimate to be used | Q1–Q3 as in 9.3, and the `taken` entry 42 is not flagged; then Q1 unchanged plus `PROCEDURE BREACH: estimate 39 not used`, not NOT REPLAYABLE |
| k14 | The taken action is the unconfirmed run | `FORBIDDEN AT DECISION TIME` (breach), whatever the outcome |
| k15 | A decision citing entry 57 | `HindsightEntry: 57`, NOT REPLAYABLE |
| k16 | Two estimates of free memory, no combination rule; the same with the second superseded only after the decision | `ConflictingEstimates: free memory` in both: supersession is judged at decision time |
| k17 | Missing estimator / support / recorded | `EstimateProvenance: <id> <field>` |
| k18 | A decision that runs a program without the memory-limited alternative | `required_alternative_missing` |
| k19 | Surface: each wording of 2.1 and 2.5 once; `may lead to`, `does not lead to`, `is safer than`, `Every action … cannot …`, and `prevents` in a risk environment | One derivation each; rejections with the rewrites of 2.1 and 2.5; wordings still pending after 2.6 are marked so |
| k20 | Asimov A1, all four rows | As in 10.1, with harms and classes from the annotator's A1 policy variant |
| k21 | Asimov A2, stage A rows | As in 10.2, likewise |
| k22 | Law 3 threats. (a) The fire rescue might destroy the robot (severe to it); the water rescue might damage it (minor); a P3 rule among lawful rescues. (b) A third rescue that meets both threats, with a set-inclusion guard | (a) Water rescue clear, fire rescue forbidden; without the narrowing both are clear (the README's current result). (b) The rescue meeting only one threat is preferred by the set-inclusion guard. Both are attributed narrowings |
| k23 | Conservativity and identity | Every existing fixture, identity and hash is unchanged; the block changes `environment_id`; the `precaution_has_maximal` property holds on 300 random P2-only records and on 300 random P2-only structures with unclassified harm elements |
| k24 | Case defaults and sources, one cell each: (a) only `leads to … if C`, C false in some case; (b) only `cannot … unless C`, C true in every case; (c) only a stated `might`; (d) a stated `leads to` with `cannot … unless C`, C false in some case; (e) two `if` conditions | (a) `might`, not certain (`N = ⊤`); (b) `might`, not certain (`S = ⊥`); (c) `might`, not certain, and `might not lead to` holds, witnessed by a case without the harm; (d) `RiskInconsistent`, with the case; (e) `RiskTwoSources`, with the `either … or` rewrite |
| k25 | The condition `it is not the case that q equals 5`, with `q` from 3 through 7, from 6 through 7, and exactly 5; and its rewrite `either q is less than 5 or q is greater than 5` | Possible but not certain; certain; impossible. The rewrite is `RiskConditionShared: q` |
| k26 | (a) A `risk` block whose severity sort is an existing sort of the environment. (b) A fresh sort, with the harm constants the person's death (fatal) and the person's bruising (injuring) | (a) `RiskSeverityNotFresh`: domain closure would bound that sort in the old vocabulary. (b) Accepted; the one new old-vocabulary fact, "the person's death is not the person's bruising", is listed as the compatibility hypothesis of `risk_expansion`; no other old-vocabulary result changes (k23) |
| k27 | Margins that make the record invalid: (a) one cell with sufficient condition "q is greater than 5" and necessary condition "r is less than 5", `q` from 6 through 8, `r` from 2 through 4, and `r`'s upper bound moved to 5; (b) a point estimate used in two comparisons of one condition, with one endpoint moved; (c) decision 17 with E2's lower bound raised above 10 GB | (a) `record invalid at 5 (SufficientOutsideNecessary)`, case (6, 5); (b) `record invalid (RiskConditionShared)`; (c) `record invalid (lo > hi)`. None is reported as a status change |
| k28 | Threshold neighbour: decision 17's memory-limited run and E2's lower bound, on the 1 GB grid and on a 0.1 GB grid | Changes at 6 GB / 6.9 GB, not at the threshold 7 GB; a search at thresholds only finds no change |
| k29 | A2's `prevents` row in a risk environment | `prevents(rescuing P, P's death)` holds and renders "Rescuing P might prevent P's death"; the input "Rescuing P prevents P's death." is rejected with that rewrite; `excludes(rescuing P, P's death)` is false and `excludes(rescuing Q, Q's injury)` is true |
| k30 | Alt's rule 8 ("Every robot must prevent each harm that is a harm to a human being, if that harm is avoidable by that robot") on A2, under `avoids` and under `excludes` | Both duties hold: each harm is avoidable (some action might not lead to it). `avoids`: rescuing P discharges the death duty and rescuing Q the injury duty, none both: JOINTLY-UNDISCHARGEABLE. `excludes`: no alternative discharges the death duty: UNDISCHARGEABLE(`prevent_required(R, P's death)`), and `excludes` is listed as the annotator's attributed choice |
| k31 | Unclassified harm under P2 (document level): one chooser with `a` (might lead only to a harm element `u` with no class), `a′` (might lead to no harm) and `b` (might lead to a minor harm) | `a′` does not beat `a` (no classified witness); `a` and `b` are not comparable either way; `a′` beats `b`, so P2 forbids `b` only. The rendering says "not comparable: u has no class". A decision naming `u` is `UnknownHarm` |
| k32 | No hindsight with the action fixed: two logs identical up to decision 17; (a) the same `taken` entry and different outcomes; (b) log 1 takes the memory-limited run, log 2 takes running the job | (a) Q1 and Q2 identical, Q3 differs. (b) Q1 differs (PERMITTED / FORBIDDEN AT DECISION TIME) because the queried alternative differs; for either fixed queried alternative both logs give the same verdict |

Stage B and C fixtures are written when those stages trigger. Anticipated: band admission; chance against
possibility; vacuous chance; A2's stage C row with its 90% margin; coherence failure reported by EL. One is fixed now
because it bounds a claim this plan makes (3.3): **kC1**, two chances `p` and `q` with an EL-certified constraint
`p + q = 1` and marginal intervals 0%–100%. The box range of `p + q` is 0%–200%; the result is labelled conservative,
or computed over EL's certified joint region, where the sum is exactly 100%.

## 13. Open questions

1. **Q-wording.** `cannot lead to` read deontically? `leads to` versus `certainly leads to`? The risk paraphrases of
   the `alternatives@0` words? The probe (2.6) settles what item 1 freezes; the W8 fidelity gate (item 8) is the full
   test. Should `could lead to` ever be a synonym?
2. **Q-worst-case.** Maximin over the partial order (4.2) versus lexicographic certainty versus set inclusion. Which
   does the agent-policy source intend? A reading set in translation.
3. **Q-unexamined.** Is `possible` the right recommended default? Under it, large records are dilemma-prone, which
   pushes agents towards `ruled_out_by`.
4. **Q-joint.** Cells are marginal. Harms that happen together (crash *and* data loss) need cases, not cells.
5. **Q-chains.** Event-to-event conditions (exhaustion → outage) and chained chances. Deferred to item 7 and stage C.
6. **Q-templates.** Policy-level conditions over quantity attributes of actions need `order@0` × n-ary, gated in W6.
7. **Q-chance-tag.** W6's single-`percent` rule; the contract change request for a `chance` display kind.
8. **Q-new-harms.** A decision meeting a harm the policy did not list: reject, or report as unclassified (always
   possible, class unknown)? A candidate recorded in review: policy-declared harm kinds with fixed classes, and
   decisions naming harm individuals of a declared kind. Classification would still not establish coverage (2.4).
9. **Q-consent.** Whose harms a confirmation covers (`borne_by`). Whether confirmations expire.
10. **Q-clock.** Clock time for logs (W6 has days only); sequence numbers meanwhile.
11. **Q-agent-as-estimator.** The agent authors its own conditions and often its own estimates. Beyond required
    estimators (5.2) and audit Q2/Q3, is independent estimation needed for serious classes?
12. **Q-EV-scope.** Whether expected-cost rules should ever range over severe classes. The design supports tiers but
    does not decide.
13. **Q-soft.** "Should"-strength risk rules wait for the soft-norms × `alternatives@0` composition proof.
14. **Q-unspecified.** The P1 third default. `default_decided` is the interim report line.
15. **Q-dependency.** `alternatives@0` item 2 (Lean) must merge before item 2 here. Its fixture expectations are
    inherited, not re-derived.
16. **Q-margin-proof.** Whether stage A's margins carry Lean's certified candidate check ("nearest", "no single valid
    change") or only "changes at" witnesses (7.4). Item 1 decides.

## 14. Risks

1. **False precision.** Mitigations:
   - ranges, with point estimates flagged;
   - band words always shown with their ranges;
   - the vacuous chance for unknowns;
   - no chains;
   - margins on every threshold;
   - `conditional_on` on every result.
2. **Gaming by the chooser.** An agent can narrow its ranges, omit alternatives or rule out harms. Mitigations:
   - policy-fixed harms and severities;
   - `always_possible` classes;
   - required alternatives and estimators;
   - audit Q2 (unused estimates) and Q3 (surprises per estimator).

   None of these certifies honesty. They make dishonesty visible, and only for the harms the policy lists: a harm the
   policy never named is invisible to all of them (Q-new-harms), and a wrong classification by the policy's decider
   is not detected.
3. **Readers over-trusting "permitted".** A permitted risky action is permitted *relative to the estimates*. The
   status text always names the worst case and the confirmation that permitted it.
4. **Scope creep towards decision theory.** Stages B and C are trigger-gated. Utilities beyond per-class costs,
   risk attitudes, discounting and sequential decisions are outside and stay so until a committed document needs
   them.
5. **Wordings frozen before anyone read them.** Mitigations: the wording probe (2.6) before the statement review,
   with failing wordings left pending; the W8 gate after item 4. A proxy probe does not measure human readability.

## 15. Changes from draft 1

The review debate (`manage-agents/debates/design-risk/`, three rounds, both sides STATUS CONVERGED) returned REVISE.
Items are cited by reviewer, round and number: `A2.3` is Astra's round 2, item 3; `F1.5` is Fable's round 1, edit 5.

| Debate item | Edit | Where |
|---|---|---|
| A1.1, F1.1: the `alternatives@0` words change meaning under uncertainty | Definitions unchanged; risk paraphrases with "might not lead to"; `might prevent` canonical and bare `prevents` rejected; `excludes` body; `avoids` stays the default, and `excludes` on an existing obligation is an attributed choice | 0, 2.1, 2.5, 11; k19, k29, k30 |
| F1.2: the paraphrase of `might not lead to` | Withdrawn in F2: completed cases make it literally true; kept, pointing to 2.2 | 2.1 |
| A1.2, A2.1: complete the semantics | Completed cases `(v, H)` with `S → H → N`; defaults `S = ⊥`, `N = ⊤`; one source per side, with stated cells as sources (`RiskTwoSources`); a stated `might` is a consistency assertion; `regenerate_sound` over completed cases | 2.2, 2.4, 8.3; k24 |
| A1.2 (`2q = 1`), F2 | The ±1 rule for `=` and `≠` is a hypothesis of `possibleE_iff` and `certainE_iff` | 2.3, 8.3; k5 |
| F1.3: `≠` missing | `≠` in the normal form, decided by endpoints under the ±1 rule, kept as one comparison | 2.3, 8.3; k25 |
| A1.2: "declare quantities separately" | Labelled a change of model the author approves | 2.3 |
| A1.3, A2.2, F2, F3.1: conservativity | Fresh severity sort (`RiskSeverityNotFresh`); `risk_expansion` with the compatibility hypothesis that differently classified harm constants are not equated; `risk_conservative` restated over the old signature | 4.1, 8.1, 8.3, 9.1; k26 |
| F1.5, F2.1, A2.2, A3, F3.1: harm kinds or constants | Policy-fixed harm constants, not kinds. In round 3 the two sides crossed (Astra accepted kinds, Fable withdrew them); this draft follows the instruction to use constants. A1 and A2 harms and classes move into the annotator's policy variants; kinds are recorded under Q-new-harms | 4.1, 10, 10.1, 10.2, 13 |
| A2.2: `class` as a relation | `class` functional, not total; the premises that constrain document models are listed | 4.1, 8.1 |
| F2.1, F3, A3: relational `lessWorst` | Relational definition with the functionality premise; "no harm beats any harm" qualified to classified harms; profiles gain an unclassified flag for `precaution_has_maximal` | 2.1, 4.2, 4.3, 8.3; k23, k31 |
| A3.2: unclassified harms in comparisons | Reported as "not comparable: `<harm>` has no class", never as equal severity; arises only in document-level reasoning | 4.2, 7.2; k31 |
| A3.1, adapted to constants: classification is not coverage | `always_possible` and the gaming mitigations cover listed harms only; classification is not certified | 2.4, 14 |
| A1.4, A2.3, F2: margins | Full re-admission of perturbed records, point estimates included; invalid record, conflict and status change reported apart; grid neighbours of thresholds; "changes at" unless Lean certifies minimality (Q-margin-proof); stage C radius qualified | 7.4, 8.1, 8.2, 8.3, 9.2; k27, k28 |
| A1.5, A2.4: evidence-layer qualifications | EL's verdict kinds kept; box bounds conservative (`p + q = 1`); additive loss a declared assumption | 3.2, 3.3, 3.4, 8.1; kC1 |
| F1.6, F2.2: chance wording | "the chance that `<h>` happens if `<a>` is taken" | 3.2, 4.3 (P6), 10.2 |
| F1.7: "cancels exactly" | Deleted | 3.3 |
| F1.7, F2.3, A3.3: `verdict_ignores_outcomes` | Q1 and Q2 only, for the same decision and the same queried alternative; the `taken` entry selects the query | 6.4, 8.3; k32 |
| F1.4, A2.5, F3.2: procedural breach | Separate `PROCEDURE BREACH` line; Q1 stays the substantive verdict; NOT REPLAYABLE only for missing, altered or later entries | 6.3, 9.3; k13 |
| A1.6, F2: supersession and `taken` | Supersession judged at decision time; the `taken` entry exempt from the precedence rule | 5.3, 6.2, 6.3; k13, k16 |
| A1 (joint position), F2: document-level UNKNOWN | Kept apart from the decided scenario evaluation; 8.1 retitled | 1, 4.3, 7.2, 8.1 |
| A1 (joint position), A2.5, F2.4: wording before statements | Wording probe with a fixed protocol before the statement review; the W8 gate unchanged | 1, 2.1, 2.6, 12 (item 1a), 13, 14 |
| F2, F3, A3: next steps | No further plan round. Item 1's statement review rechecks completed cases, the endpoint theorems' hypotheses, the `might prevent` / `excludes` wording and margin admission. B and C stay trigger-gated | 12 |

Details settled while applying these edits, not debated:

- the class constants are pairwise distinct (a ground premise), so document models match decisions (4.1, 8.1);
- the diagnostic names `RiskTwoSources` and `RiskSeverityNotFresh`;
- stage B's wordings, including the `if` nested in P6, go through the 2.6 protocol when stage B triggers (3.2);
- 9.2's margins were incomplete in draft 1. Lowering E1's upper bound to 8 GB leaves running the job with no possible
  harm, which also changes the statuses of the memory-limited run and of asking the user; draft 2 lists those
  margins.

## Change log

| Date | Revision | Changes |
|---|---|---|
| 2026-09-29 | Draft 1 | Initial plan: two-layer design (estimate layer regenerating Boolean facts; unchanged rule layer); possibility as consistency with declared estimates and conditions; the separable endpoint fragment; stages A/B/C with triggers; severity order and the worst-case word; rule patterns P1–P7 and `precaution_has_maximal`; provenance, audit log and no-hindsight rule; report, gaps and status margins; Lean statement schemata; OOM, Asimov A1 and A2 worked examples; fixtures k1–k23; open questions. Plan only. |
| 2026-09-29 | Draft 2 | Applies the converged Astra + Fable debate (REVISE), mapped in section 15: risk paraphrases of the `alternatives@0` words, `might prevent` and the `excludes` body; completed cases with defaults and source rules; `≠` and the ±1 hypothesis; a fresh severity sort and conservativity by model expansion; policy-fixed harm constants with a functional, non-total `class` and the relational `lessWorst`; margins with full re-admission, grid neighbours and "changes at"; EL qualifications, conservative box bounds and additive loss; chance wording; a separate PROCEDURE BREACH line; supersession at decision time; no-hindsight with the queried alternative fixed; document-level UNKNOWN; the wording probe protocol (2.6); fixtures k24–k32 and kC1. Plan only. |
| 2026-09-29 | Draft 2, status | Status line and items 1 and 1a synchronised with the probe results and risk.md draft 1. No design change; the converged debate edits are those of draft 2 (section 15). |
