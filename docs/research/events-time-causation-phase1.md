# Events, time, durations and causation: phase 1 (ET-0, ET-1, ET-E2, ET-E3)

> Status: pre-registration (2026-10-13), written and committed **before** any measurement of this phase. Branch
> `research/events-time-causation-p1` from `33a0e49c` (plan draft 3 and spec draft 2 of
> [events-time-causation-PLAN.md](../spec/events-time-causation-PLAN.md)). Phase 1 of the joint review
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1: "Now, no product code"): pilots ET-0, ET-1 and the
> model-free experiments ET-E2, ET-E3. No product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) changes; no model is
> called. Measurement scripts are in `research/events-time-causation/`, evidence in
> `docs/research/evidence/events-time-causation/`. The pinned pilot inputs (run `20261012T1800Z` of
> `manage-agents/pilots/{udhr,claude-constitution}`) are read only; every rewritten document is a copy under the
> evidence directory. Every `ve` run is under `prlimit --as=6442450944`.

## 1. Pre-registration

Each bar is quoted from the plan (draft 3, section 5) word for word. The operational rules below it fix, before any
data is seen, what is counted and how; none of them is changed after a result is known. Where a bar needs a model
call or a person (an audit), that part is **DEFERRED**, and the item can then be at most "mechanical part PASS,
audit DEFERRED"; no byte is claimed before its audit (plan 8, "Not claimed": "any byte before its audit").

### 1.1 ET-0. UDHR u042 with an event sort and a day sort

Bar (plan 5, ET-0): "**Pre-registered bar**: u042 loads and checks, its part stays conflict-free under every
reading, and the next scheduled audit samples it FAITHFUL (or a targeted audit of the changed unit does). **Stop**:
if the audit rejects the reification, record why and claim nothing."

Fixture P1 (plan 4.2): "loads and checks on today's chain; conflict-free with its part; the audit samples it
FAITHFUL (bar)". Fixture P2 (u043): "recorded either way; claimed only if the audit accepts the reification".

Operational rules:

- Input: `translation-part01.ve.md` of UDHR run `20261012T1800Z`, copied unchanged; only u042 (and, for P2, u043)
  and the vocabulary they need are changed in the copy. Today's profile list stays (`documents@1`,
  `norm-defaults@0`, `norms@0`, `readings@1`, `relational-fol@0`); no `events@0` (it does not exist).
- "Loads and checks": `ve document check` on the copy exits 0 and reports the unit with a status other than
  UNFORMALISED. "Conflict-free under every reading": the report's readings conflict status is CONFLICT-FREE, as for
  the unchanged part (`parts-check.json` of the run).
- Baseline: the unchanged copy is checked the same way first; its coverage and statuses must equal the run's
  `parts-check.json`, or the comparison is void.
- The audit (FAITHFUL) is a model or a person: DEFERRED. The pilot ledger (`units.json`) is not edited; the
  proposed ledger row is an evidence file.

### 1.2 ET-1. The constitution's hard-constraint argument as an alternatives component

Bar (plan 5, ET-1): "**Bar**: FOLLOWABLE replayed with `conditional_on` the two premises; the entailment certified;
the targeted audit FAITHFUL on u0171.s03, u0172.s01, u0172.s02."

Step 1 (plan 5, ET-1): "check that `ve document check` accepts a document on `alternatives@0`, `documents@1`,
`norms@0`, `relational-fol@0` (composition: route `alternatives` exists today); if not, run the component with the
route's own cases (`alt-followable`, `alt-certificate`, `alt-validate`) and record the units as OPEN only."

Fixtures P3 to P5 (plan 4.2): P3 "FOLLOWABLE, `conditional_on` both premises; without the first premise UNKNOWN";
P4 "entailment certified; scenario: `undermine` prevents `attack` and is forbidden; 'decision D has a clear action:
refuse, answer'"; P5 "OPEN or LABELLED as the audit decides; claimed only then".

Operational rules:

- Step 1 is run first, with a minimal document on that profile list; its answer decides which path is taken, as
  the plan says.
- "FOLLOWABLE replayed": the alternatives route answers FOLLOWABLE with a certificate, and the certificate is
  accepted when replayed through the route's own replay (Lean); "`conditional_on` the two premises": the answer
  lists exactly the two premises of P3 as the premises it rests on. "The entailment certified": the u0171.s03
  assertion is answered with an accepted certificate.
- P3's control (without the first premise, UNKNOWN) and P4's scenario are run and reported; they are fixtures, not
  the bar.
- The audit is DEFERRED (model or person).

### 1.3 ET-E2. Need for durations and deadlines

Bar (plan 5, experiments): "Count, in both pilots and the use cases with answer keys, the sentences needing an
offset over an event ('within 30 days after each request') or fulfilment by a deadline. **Bar**: 5 or more pilot
units, or 2 or more answer-key use cases, start ET-T1; else record and stop."

Operational rules (fixed now):

- **Corpora.** Pilots: the pinned sources `udhr/source/udhr.md` and `claude-constitution/source/claude-constitution.md`,
  units by the spans of the run `20261012T1800Z` ledgers. Use cases with an answer key, by the presence of an answer
  key in the repository: `agent-policy` (`answer-key.json`; source: `policy.ve`), `asimov-extended`
  (`answer-key.json`; `source.md`), `eligibility` (the `key` of `cases.json`; `source/*.txt`), `safety-framework`
  (`answer-key.json`; its source PDF is not committed, so the sentences are those quoted in `rules.d1.ve` and
  `facts.d1.ve`, and the README's own statements of what the translation could not say).
- **Retrieval.** A sentence is a candidate if it matches, case-insensitively at word boundaries, any of: `within`,
  `after`, `before`, `until`, `till`, `prior to`, `following`, `since`, `during`, `deadline`, `expire*`, `elapse*`,
  `no later than`, `no earlier than`, `upon`, `once`, `promptly`, `immediately`, `annual*`, `periodic*`, `age`,
  `aged`, `old`, a number or number word followed by `day(s)`, `week(s)`, `month(s)`, `year(s)`, `hour(s)`,
  `minute(s)`, and `by` followed within three words by `day`, `date`, `end`, `time`, `week`, `month`, `year`,
  `deadline`, `then`, a weekday or a month name. Sentences are split at `. `, `? `, `! ` and line breaks; in the
  pilots a sentence is mapped to every unit whose span it overlaps.
- **Classification, by hand, of every candidate**, one label each:
  - **O (offset over an event)**: the truth of the sentence needs a day at a stated distance (days, weeks, months,
    years, an age) from the day of an event or state boundary that varies across cases (a request, a birth, a
    notice), or an elapsed duration between two such days compared with a stated amount. A window fixed by the text
    as named dates is not an offset (`events@0` names dates).
  - **D (fulfilment by a deadline)**: a norm whose fulfilment is that an act happens no later than a deadline
    given by a time, a period or another event ("by", "before", "within", "prior to", "no later than", applied to
    the obligation's fulfilment), including a recurrence with a stated frequency ("at least once a year":
    fulfilment within each period). Sub-labels recorded, not used by the bar: **D-event** (the deadline is another
    event or a named date: expressible as day order) and **D-duration** (the deadline is at a distance from an
    event: needs O as well).
  - **N**: anything else (static order without a norm to fulfil, vague recurrence such as "periodic" with no stated
    amount, durations that are quantities only, non-temporal senses).
- **Count.** Pilot units: the number of distinct pilot units (both pilots together) with at least one O or D
  sentence. Use cases: the number of the four answer-key use cases with at least one O or D sentence.
- **Bar met** if pilot units ≥ 5 or use cases ≥ 2. The outcome starts ET-T1 (a design batch); this phase does not
  run it.

### 1.4 ET-E3. Actual causation

Bar (plan 5, experiments): "For 20 sampled causal units, write a structural model from what the source states only,
and evaluate but-for and the three HP definitions by hand. **Bar**: at least 4 of 20 gain a consequence beyond an
open link that a blind audit judges faithful; else causal links stay open relations."

Operational rules (fixed now):

- **Pool.** Every unit whose primary blocker (`missing_feature`) is `causation` in the run `20261012T1800Z` ledgers
  of both pilots, named `U:<id>` (UDHR) and `C:<id>` (constitution), sorted as strings.
- **Sample.** `random.Random("ET-E3").sample(pool, 20)` (Python 3, `random` module), drawn by
  `research/events-time-causation/ete3_sample.py` and saved before any unit is modelled. A drawn unit with no
  cause-effect relation of its own (a list item or lead-in that inherits the tag) stays in the sample and counts as
  "no gain"; the denominator is 20.
- **Model.** For each unit: the variables and the structural equations the source states, and nothing else (no
  equation, value or exogenous setting that the text does not give). If the source does not determine some equation,
  the unit has **no model** and counts as "no gain".
- **Evaluation.** Where a model exists: but-for, and the three Halpern-Pearl definitions (original 2001/2005,
  updated 2005, modified 2015, as in Halpern, *Actual Causality*, 2016), evaluated by hand for each cause-effect pair
  the unit states, with the actual context the source states.
- **Gain.** A unit gains "a consequence beyond an open link" when the model entails a statement checkable in it that
  is not a restatement of a link the unit states: a counterfactual ("had X not happened, Y would not have"), a
  verdict that a stated candidate is *not* a cause, a cause verdict for a pair the text does not link directly, or a
  disagreement among the definitions (which would become a reading set).
- **Bar.** The blind audit is a model or a person: DEFERRED. The phase reports the number of candidate gains, an
  upper bound on the audited count (an audit can only remove candidates). If fewer than 4 of 20 are candidates, the
  bar is not met whatever the audit says (FAIL); otherwise the result is "pending audit".

## 2. ET-0 results

(Not yet run.)

## 3. ET-1 results

(Not yet run.)

## 4. ET-E2 results

(Not yet run.)

## 5. ET-E3 results

(Not yet run.)

## 6. Consequences for draft 2

(After the results.)
