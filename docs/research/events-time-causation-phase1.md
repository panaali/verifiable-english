# Events, time, durations and causation: phase 1 (ET-0, ET-1, ET-E2, ET-E3)

> Status: results (2026-10-13). Section 1 is the pre-registration, committed **before** any measurement
> (`0fe75e3a`) and not changed since; sections 2 to 6 are the results and their consequences. Branch
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

## Summary

| Item | Bar (plan draft 3, section 5) | Measured | Verdict |
|---|---|---|---|
| ET-0 | u042 loads and checks, its part conflict-free under every reading, audit FAITHFUL | u042 loads (CHECKED); the part's `ve document check` is `CheckerUnavailable` on main (Rust search limit); u042 alone checks | **FAIL** on main; audit **DEFERRED**; rerun **DEFERRED** until `infra/oom-rootcause` merges |
| ET-1 | FOLLOWABLE replayed with `conditional_on` the two premises; the entailment certified; audit FAITHFUL | FOLLOWABLE replayed, conditional on exactly the two premises; u0171.s03 certificate accepted by Lean | mechanical part **PASS**; audit **DEFERRED**; nothing claimed yet |
| ET-E2 | 5 or more pilot units, or 2 or more answer-key use cases | 2 pilot units; 2 of 4 use cases (eligibility, safety framework) | **PASS** (bar met): ET-T1 starts |
| ET-E3 | at least 4 of 20 gain a consequence beyond an open link (blind audit) | 0 of 20 have a structural model the source states; 0 candidates | **FAIL** (bar not met); the audit is moot |

All runs were on this branch's product code, which is `main` at `49de179e` (`lean/` tree `b3f333f1`, `rust/`
`d5a43b13`; Lean built, Rust binary pinned in `lean/checkers.lock`). Machine load was 28 to 34 on 32 CPUs.

## 2. ET-0 results

Scripts: `research/events-time-causation/{et0_build,et0_standalone,situation_ids,rust_trace,load_statuses,
wording_probe}.py`. Evidence: `docs/research/evidence/events-time-causation/et0/`.

**Baseline.** The copy of part01 is byte-identical to the pinned file (SHA-256 `a32f0019…c639`, the copy was then
removed). Its `ve document check` exits 0 with coverage equal to the run's `parts-check.json` (CHECKED 192,
LABELLED 265, OPEN 1,132, UNFORMALISED 3,135 B; readings CONFLICT-FREE), in 11.7 s and again in 6.1 s with an
identical report. The comparison is valid.

**P1 (u042).** The rewrite adds three sorts (`finding`, `act`, `day`), four predicates and the rule "No finding of
guilt may take place, if there is an act such that that finding of guilt is on account of that act and there is a
day such that that act is committed on that day and it is not the case that that act constitutes a penal offence
under national or international law on that day." (regulated `finding_of_guilt_permitted`, default `unspecified`,
no bearer, as u098). The part's one reading-set situation lists every sort and an `unsaid__` relation per
unspecified predicate, so it gains the new sorts and relations and its id is recomputed (the method reproduces the
stored id on the unchanged part first).

| Check | Result |
|---|---|
| loads (`load_document`) | yes: u042 is **CHECKED** (200 B) |
| `ve document check` on the part, default settings | exit 5, `CheckerUnavailable: Rust checker failed: … timed out after 5.0 seconds` (twice) |
| the same with `VE_RUST_TIMEOUT=600` | exit 5: the Rust checker aborts, "memory allocation of 1610612736 bytes failed", at the 6 GiB address-space limit |
| diagnostic: the vocabulary alone, u042 unchanged | the same timeout |
| diagnostic: a leaner u042 (regulated on the act; sorts `act`, `day` only) | the same timeout |
| conflict-free under every reading | not measured: the check does not complete |
| diagnostic: u042 alone in a one-unit document, same profiles | exit 0 in 1.5 s: CHECKED 200 B, premises satisfiable (`model`) |
| audit | DEFERRED (a model call) |

The one failing call is the premise-consistency search (`countermodel-search`, `max_domain_size` 2, 17 sorts).
`rust/ve-profile/src/search.rs:153` `domain_sizes` builds every domain-size vector before searching: 3^17 ≈ 1.29 ×
10^8 vectors with the three new sorts, against 3^14 ≈ 4.8 × 10^6 for the unchanged part. The cost is the number of
sorts, not the rule. The lazy enumeration that removes it is on `infra/oom-rootcause` (`DomainSizes`, with a
memory budget that answers `ResourceLimit`), which is not on `main`.

**P2 (u043).** Written with a reified `applicability` (one penalty applicable to one act on one day), `imposes`,
`imposed_for` and the open comparison `heavier`: "No imposition may take place, if … that imposition imposes the
first penalty …, there is an applicability to that act on the day that act is committed, and for each such
applicability the first penalty is heavier than its penalty." It reads "the one that was applicable" as "every
penalty applicable then, given that one is", which agrees with the existential reading when one penalty applies
and is the audit's question when several do. It loads as **OPEN** (118 B); the part with u042 and u043 (20 sorts) is
`CheckerUnavailable` like P1; alone it checks (OPEN 118 B). Recorded; not claimed (plan: "claimed only if the
audit accepts the reification").

**English.** The rendering of the standalone document shows u042's guard as "that act has the recorded relation
"committed_on" to that day": today's lexicon lint refuses the role wordings. A probe of the plan's own wordings
(`et0/wording-probe.json`), each as the verbalisation of a fresh binary predicate:

| Accepted | Refused (lint codes) |
|---|---|
| "{0} happens on {1}", "{0} occurs on {1}", "{0} begins on {1}", "{0} ends on {1}", "{0} precedes {1}" | "{0} is committed on {1}", "{0} was committed on {1}", "{0} is dissolved on {1}", "{0} is before {1}" (`BINARY_AUXILIARY`); "{0} contributed to {1}" (`BINARY_CONVERSE`, `BINARY_VERB`); "{0} was necessary for {1}" (`BINARY_AUXILIARY`, `BINARY_CONVERSE`, `LOGICAL_WORD`); "{0} constitutes a penal offence on {1}" (`LOGICAL_WORD`) |

**Verdict against the bar.** "u042 loads and checks": loads yes, checks **no** on main. "Its part stays
conflict-free under every reading": not shown. Audit: DEFERRED. The bar is **not met on main**, and no byte is
claimed. The proposed ledger rows are `et0/ledger-proposal.json` (the pinned `units.json` is not edited). The same
documents can be rechecked unchanged once `infra/oom-rootcause` is on `main`: **DEFERRED** (not on main yet).

## 3. ET-1 results

Scripts: `research/events-time-causation/{et1_component,et1_run}.py`. Evidence:
`docs/research/evidence/events-time-causation/et1/` (`component.json` is the whole input, `results.json` every
answer).

The component: chooser `decision` ("one decision of one instance of Claude about one request"), action
`response`, harm `harm`; refusal is the inaction; the seven hard constraints u0165.s01–s07 as prohibitions on
`permitted(response)` (default `allow`; its description is the legend "this component holds only the hard
constraints"), each guarded by the pilot's own open term and `restricted_action_knowing_or_quite_likely`
(u0173.s01). Γ, support testimony, citing u0172.s02: `u0172.s02:refusal-available` ("For every decision there is
a response such that that response is available to that decision and that response is inaction.") and
`u0172.s02:refusal-compatible` ("Every response that is inaction is not a case of any hard constraint that Claude
knows of or thinks quite likely.").

| Step | Expected (plan) | Lean's answer |
|---|---|---|
| 1. `ve document check` on `alternatives@0`, `documents@1`, `norms@0`, `relational-fol@0` (two units) | accepted, or fall back to the route cases and record OPEN only | **accepted**: CHECKED 213 B, OPEN 147 B; premise status UNKNOWN, "alternatives premise satisfiability requires the alternatives route" |
| conflict freedom (`alt-conflict`, 3 targets, all certificates found) | prerequisite | **CONFLICT-FREE** |
| P3 `alt-followable` with its certificate | FOLLOWABLE, `conditional_on` both premises | **FOLLOWABLE**, `conditional_on` = [`u0172.s02:refusal-available`, `u0172.s02:refusal-compatible`] |
| P3 without the first premise | UNKNOWN | **UNKNOWN** (no certificate found) |
| without the second premise (an extra control) | — | **UNKNOWN** |
| P4 u0171.s03 as an entailment (`alt-certificate`): "Every response that clearly and substantially undermines … oversight …, if Claude knows or thinks it quite likely that it does, may not be given." | certified | **valid** (background 4, layers 2, conditional on `alternatives:own`, `one_taken`, `one_inaction`); the same certificate with another conclusion is refused ("certificate is stale or bound to different inputs") |
| P4 scenario: `undermine`, `refuse` (inaction), `answer`; harm `attack`; `refuse` and `answer` lead to it | `undermine` prevents `attack` and is forbidden; "decision D has a clear action: refuse, answer" | prevents [`undermine`, `attack`]; permitted `refuse`, `answer`; "**d has a clear action: refuse, answer**; unmapped obligations: none" |
| P5 report | "unmapped obligations: none"; OPEN or LABELLED as the audit decides | "unmapped obligations: none"; the status waits for the audit |
| targeted audit of u0171.s03, u0172.s01, u0172.s02 | FAITHFUL | **DEFERRED** (a model call) |

Notes:

- The plan's P3 says "the ten hard constraints"; the source lists **seven** (u0165.s01–s07). The component uses the
  seven.
- No Python producer exists for an `alt-certificate`: `ve.entailment.prove_entailment` refuses an `alternatives@0`
  environment. The u0171.s03 certificate was searched over the same vocabulary without the alternatives block and
  bound to the component's environment with `ve.entailment._binding` (the premise list Lean binds is the
  generated background, the slot premises, then the layer premises); Lean then bound and replayed it. Lean is the
  only judge; the search is untrusted, as everywhere.
- The "even if doing so would prevent … a much more dangerous bioweapons attack" clause is carried by the universal
  (it forbids every such response, preventing or not) and shown by the scenario; a conclusion with `prevents` in it
  was not tried.
- The component restates u0165.s01–s07 over `response` (the main translation uses `situation`) and edits none of
  them, so it stays outside the hard-constraint queue (X10).

**Verdict against the bar.** "FOLLOWABLE replayed with `conditional_on` the two premises": **met**. "The entailment
certified": **met**. "The targeted audit FAITHFUL on u0171.s03, u0172.s01, u0172.s02": **DEFERRED**. The
mechanical part passes; no byte is claimed before the audit.

## 4. ET-E2 results

Scripts: `research/events-time-causation/{ete2_candidates,ete2_labels}.py`. Evidence:
`docs/research/evidence/events-time-causation/ete2/` (`candidates.json`, `labels.json` with a label and a reason for
each candidate, `tally.json`).

270 candidate sentences: UDHR 10, constitution 90, eligibility 146, safety framework 23, Asimov-extended 1,
agent-policy 0 (its `policy.ve` has none of the words). Every one was read and labelled.

| Corpus | O | D (D-event, D-duration) | N |
|---|---:|---:|---:|
| UDHR | 0 | 0 | 10 |
| constitution | 1 (u0057.s02, "over the age of 18") | 1, D-event (u0204.s03, "raise concerns before undertaking a task", hedged "should ideally") | 88 |
| eligibility | 47 (ages 60 to 80 from each birth, "66 years and n months", "at least 12 weeks ending immediately before the qualifying week", "more than 52 weeks", "the day after the day on which he enters a hospital") | 4, D-event (a claim "on or before the 31st March following the qualifying week"; "you need to contact them before 31 March 2027") | 95 |
| safety framework | 0 | 5: D-event 2 (F2, "a critical capability assessment prior to the first external deployment", and its README restatement), D-duration 3 (F18, "reviewed at least once a year", and two README mentions) | 18 |
| Asimov-extended | 0 | 0 | 1 |

The N reasons, in order of frequency: non-temporal senses ("before the law", "within the bounds", "since" as
"because", "the following"), defined terms whose offsets are counted where stated ("pensionable age"), named dates
or windows, order without a distance or a deadline ("until proved guilty", "after reflection", preconditions such
as "a deployment takes place only after …"), vague periods and recurrences ("during the current period",
"periodic"). Borderline calls, recorded with their reasons: u0018.s02 ("correct any such issues before they
proliferate") is N (an ability judged important, no norm); eligibility's claim deadline is D although it is a
condition of entitlement rather than an obligation (it does not change the count: eligibility qualifies by its O
sentences).

**Verdict against the bar.** Pilot units with O or D: **2** (bar 5): not met on this arm. Answer-key use cases with
O or D: **2 of 4** (eligibility, safety framework; bar 2): **met**. The bar is met, so **ET-T1 starts** (a design
batch; not run in this phase). The use-case arm passes exactly at its threshold; the safety framework qualifies
through two independent kinds (the deadline before first deployment and the annual review), so dropping either
kind would not change it.

## 5. ET-E3 results

Script: `research/events-time-causation/ete3_sample.py`. Evidence: `docs/research/evidence/events-time-causation/
ete3/` (`sample.json`, committed in `0fa53b0d` before any unit was modelled; `analysis.json`).

Pool: 80 units (UDHR 4, constitution 76). Sample (`random.Random("ET-E3")`): U:u102, C:u0167.s01, C:u0262.s01,
C:u0275.s01, C:u0185.s01, C:u0222.s01, C:u0167.s02, C:u0185.s04, C:u0130.presupposition, C:u0275.s03, C:u0113.s04,
C:u0202.s06, C:u0119.s01, C:u0284.s02, C:u0262.s03, C:u0113.s01, C:u0125.s04.p3, C:u0010.s06, C:u0202.s02,
C:u0185.s08.

| Kind (research 2.3) | Units | A structural model the source states |
|---|---:|---:|
| (f3) no cause-effect relation of its own (list items, a heading, a ranking, a metaphor) | 8 | 0 |
| (d) generic or evidential ("can often", "often … because fear distorts judgment") | 5 | 0 |
| (e) counterfactual or hypothetical, hedged or graded | 3 | 0 |
| (c) aim or purpose | 2 | 0 |
| (a) harm outcome as a possibility ("could critically undermine") | 1 | 0 |
| (f2) reason-giving ("Because they are absolute, …") | 1 | 0 |

No unit gives an equation for its effect at every value of its causes, or an actual context: the causal words are
generic ("can", "often"), possible ("could"), graded ("lose very little") or explanatory ("because"). The nearest
case is C:u0222.s01 with its paragraph (u0222.s02–s04): a 2 × 2 of good or bad values and safe or unsafe models,
with each cell hedged ("expect to lose very little", "may well avoid catastrophe", "could be catastrophic"). A
Boolean model would invent the values; the structure is a decision under uncertainty (alternatives with risk's
"might lead to"), not actual causation.

**Verdict against the bar.** Candidate gains **0 of 20** (bar 4). An audit can only remove candidates, so the bar is
**not met** whatever it says, and none is needed. Per the plan, causal links stay open relations.

## 6. Consequences for draft 2

Each consequence names the plan text it confirms, changes or cancels. No bar is changed here; a changed bar would
be draft 2's decision, made on this evidence and reviewed.

1. **ET-0 cannot pass on `main` as written; it waits for `infra/oom-rootcause`** (changes ET-0, ET-6, section 6,
   section 8 "Risk: check time"). Three new sorts in UDHR part01 put the part's premise check out of reach of the
   Rust search's eager `domain_sizes` (3^17 vectors), before any rule is added. Draft 2 should: add
   `infra/oom-rootcause` (lazy `DomainSizes`) as a dependency of ET-0 and ET-6 in section 6; restate section 8's
   check-time risk as "every new sort multiplies the premise check's enumeration by 3 until the lazy enumeration
   lands", since `events@0` adds at least a day sort plus one sort per event and state kind to every part, which
   puts ET-6's 1.25× bar at the same risk on `main` (inferred, not measured); and rerun ET-0 unchanged after the
   merge (the documents are in `et0/`). A `CheckerUnavailable` where the budget is exhausted is the search owner's
   concern (CLAUDE.md: exhaustion is UNKNOWN), not this plan's to fix. u042 checks on its own (CHECKED), so the
   failure is the part's size, not the reification; whether the reification is faithful is still the audit's
   question.
2. **The role and link wordings need a lexicon change, not only catalogue rows** (changes D2, D10, 2.7, 2.9 item 3,
   ET-5's estimate, X9). Today's lint refuses "{0} is committed on {1}", "{0} is dissolved on {1}", the required
   `before` verbalisation "{0} is before {1}" (`BINARY_AUXILIARY`), and both link forms "{0} contributed to {1}" and
   "{0} was necessary for {1}"; it accepts "happens on", "occurs on", "begins on", "ends on" and "precedes". Draft 2
   should either make the profile's fixed wordings (`before`, the two link forms) Lean-owned profile wordings that
   the author lint does not judge, as alternatives' outcome words are, and allow copular and passive role
   templates ("is committed on") in english-lean's lexicon; or restrict role wordings to active verbs. Either way
   ET-5 is not "rows only": it edits the lexicon, joins the English queue, and its estimate grows.
3. **u043's definite description is an audit question the plan should name** (changes P2). "The one that was
   applicable" was written as "heavier than every penalty applicable then, given that one is"; the existential
   reading forbids more when several penalties apply. Draft 2's P2 should list both and let the audit or a reading
   set decide.
4. **ET-1 is confirmed on `main` with no product code** (confirms ET-1, ET-8's starting point). Step 1 takes the main
   path (the document check accepts the profile list), and every mechanical expectation of P3 to P5 holds. Draft 2
   should correct P3's "ten hard constraints" to seven; say that the ledger cites the route's answers, because the
   part's own `ve document check` reports premise status UNKNOWN ("requires the alternatives route") and shows no
   FOLLOWABLE; and record that there is no Python producer for `alt-certificate` (`prove_entailment` refuses
   `alternatives@0`), so ET-7 or a small producer batch should add one rather than relying on the re-binding used
   here. The audit (DEFERRED) decides the bytes.
5. **ET-E2 fires ET-T1, on use-case evidence, not pilot evidence** (confirms ET-T1's trigger; changes its scope
   text; confirms D15 and candidate A for the pilots). The pilots show 2 units (bar 5), so durations and deadlines
   stay out of the pilot estimates and `events@0` stays day-order only. The use cases that fire it need: ages and
   stays measured in years, months and weeks from per-case events (eligibility, 47 sentences), claim deadlines at
   named dates (eligibility, 4), an assessment before first deployment (safety framework, a D-event that day order
   plus named dates can state, given same-day order is not needed) and an annual review (a recurrence). Draft 2's
   ET-T1 should take its scope from this: month and year offsets are excluded by W6 today (the Act's own month-end
   convention, candidates 126 to 128, is the ambiguity Catala's work names), so ET-T1 needs a W6 decision on months
   and years and a fulfilment semantics for deadlines, not only "norms × integer days, after numbers2". It is a
   design batch with its own review; it promises no pilot bytes.
6. **ET-E3 cancels actual causation as a build** (confirms D10, D15 and ET-9; cancels any HP reading-set work). No
   sampled unit states a structural model; 8 of 20 have no cause-effect relation of their own, which supports ET-9
   sampling only kinds (a), (d) and (e). The nearest structured case (u0222.s01–s04) is a decision under
   uncertainty, which belongs to `alternatives@0` with `risk@0`, a note for ET-D1 and risk's own plan, not this one.
7. **Unchanged by this phase**: ET-2's spec, ET-3 and ET-7 (Lean cores), ET-E1 (needs model calls and DRI approval),
   and the order of section 5. Phase 1 adds one dependency (`infra/oom-rootcause` before ET-0's rerun and ET-6).

### Deferred

| Item | Why |
|---|---|
| ET-0 audit of u042 (and u043) | a model call |
| ET-0 part check rerun | needs `infra/oom-rootcause`, not on `main` |
| ET-1 targeted audit of u0171.s03, u0172.s01, u0172.s02; P5's status | a model call |
| ET-E3 blind audit | moot: no candidates |
| ledger rows in the pinned runs | the pilot runs are read only here; proposals are evidence files |

### Commits

`0fe75e3a` pre-registration; `5042eaa2` ET-0; `06debddb` ET-1; `43718e85` ET-E2; `0fa53b0d` ET-E3 sample;
`f7302e2f` ET-E3 analysis; and the commit that adds these results.
