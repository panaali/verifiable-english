# Weighing, phase 1: pilots and pre-registered experiments

> Status: complete (2026-10-13), branch `research/weighing-p1` from the converged weighing design (plan draft 4,
> [docs/spec/weighing-PLAN.md](../spec/weighing-PLAN.md)). Phase 1 of the cross-plan build order
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1): "Now, no product code", with WG-E1 under its own gates
> and WG-0 "once RD-9 SC-8 is on `main`". No product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) is changed and no
> model is called. Scripts are in `docs/research/weighing-phase1/`, evidence in `docs/research/evidence/weighing/`. The pilot
> inputs are read from git at pinned commits, never checked out or edited.

## 1. WG-0: the value order and the hard constraints' immunity

DEFERRED. The plan's prerequisite is "RD-9 SC-8 on `main`" (plan 5, WG-0 row). Checked on 2026-10-13 against `main`
at `d006b1f4`: `rd-9/integrate` (`5019007c`) is not an ancestor of `main`; `lean/VE/NormDefaults/LayeredEntail.lean`
and `LayeredAdmission.lean` are absent from `main`; and `ve/document.py:630-634` on `main` still refuses
`soft-norms@0` beside `norm-defaults@0` ("UnsupportedProfile: norm-defaults@0 documents on the soft and rights routes
await the Lean route"). WG-0's translation cannot be admitted until that refusal is gone, so it was not attempted.

## 2. WG-E1: collisions between different acts

### 2.1 The pre-registered bar, quoted from the plan before any data was read

Plan draft 4, WG-E1 (quoted verbatim):

> Pre-registered protocol: draw 40 units at random (seed `20261012`) from the units whose primary blocker is `norms`
> and whose text hits the CROSSACT class of research 2.1, which must be written and committed before any unit is drawn
> (draft 1 cited it, and research 2.1 is unfilled); for each, a reader classifies the conflict it expresses as
> (i) same act after identification, (ii) two exclusive positive acts, (iii) a choice of the best response among
> several, (iv) no conflict between acts. The reader records the act phrases and the citation for each. A second reader
> classifies 10 of them blind; agreement is reported.
>
> Bar: build exclusive acts (WG-10) only if (ii) is at least 8 of 40 **and** at least 5 of those 8 would change a
> checked answer of the translation (a conflict found or resolved). Otherwise record the result and close.

### 2.2 How the protocol is carried out (fixed in the same commit as this section, before the draw)

These rules fill in what the plan leaves to the experimenter. None of them changes the bar.

1. **The class.** CROSSACT is written in [research 2.1](weighing.md) and implemented once, in
   `research/weighing/wg_e1.py`. It is committed before `screen` or `draw` is run, and not edited afterwards.
2. **The draw.** The population is the CROSSACT units with primary blocker `norms`, in ledger order;
   `random.Random(20261012).sample(population, 40)`. If fewer than 40 units are in the class, every one is
   classified and the bar's thresholds stay absolute (8 and 5), never rescaled.
3. **What the reader reads.** The unit's excerpt, with 400 bytes of source on each side for the act phrases. Citations
   are source lines (`:n`) of the pinned source (sha256 `fa10ed48…`, as `metrics.json`).
4. **The categories, as the reader applies them.** The reader classifies the conflict the unit's main clause
   expresses:
   - (i) **same act after identification**: the two sides are one act and its omission once the phrases are
     identified (refusing a request is not complying with it; declining to help is not helping);
   - (ii) **two exclusive positive acts**: two different acts, each a positive description, that the text treats as
     not both doable in one situation, where neither is the mere omission of the other;
   - (iii) **a choice of the best response among several**: the text asks for the best or most fitting response from
     an open set, with no two particular acts set against each other;
   - (iv) **no conflict between acts**: anything else, including a conflict between values or considerations that
     names no two acts, a definition, an explanation, or a single norm.
   A unit that expresses more than one is counted under its main clause's category; a secondary category is recorded
   but not counted.
5. **"Would change a checked answer of the translation".** For each (ii) unit the reader records whether declaring its
   two acts exclusive would change a checked answer: `yes` when each act is the regulated act of a rule (a rule of the
   run's translation, named by its regulated predicate, or a rule the unit itself states in a form `norms@0` or
   `soft-norms@0` can write) and the two rules' forces cannot both be met at a situation the document allows when the
   acts are exclusive (two duties, or a duty and a prohibition of its counterpart), so that a conflict would be found
   or, through ranks, resolved; `no` otherwise, for example two permissions. Where the answer depends on rules only
   WG-0's translation would contain, the reader records `needs WG-0`. The verdict is PASS when clause 1 holds and at
   least 5 (ii) units are `yes`; "PASS pending WG-0" when that count reaches 5 only with the `needs WG-0` units;
   otherwise FAIL.
6. **The second reader.** The blind subset is fixed now: the first 10 units in draw order. A second reader needs a
   human or a model call, and this phase makes no model call; the agreement measurement is DEFERRED (section 2.4),
   and the frozen subset lets it be run later without a new draw. Agreement is reported by the plan, not part of its
   bar.

### 2.3 Result

**FAIL.** Clause 1 is not met: 1 of 40 units is (ii), against a bar of at least 8. Clause 2 is not met either: 0 of the
(ii) units would change a checked answer, against a bar of at least 5.

The pre-registration was committed at `f904d675`, before the screen ran. The screen and the draw are at `878e7345`,
and the reading, tally and sensitivity at `1369e004`. Evidence is in `docs/research/evidence/weighing/`:
`wg-e1-population.json`, `wg-e1-sample.json`, `wg-e1-classification.json`, `wg-e1-result.json` and
`wg-e1-sensitivity.json`.

| Measure | Value | Method |
|---|---:|---|
| Units with primary blocker `norms` | 669 | `wg_e1.py screen` on the pinned ledger |
| Of those, in CROSSACT | 106 | the same; most frequent cues: *rather than* 22, *priority* 16, *balance* 13, *conflict* 13 |
| Drawn | 40 | `random.Random(20261012).sample` |
| (i) same act after identification | 10 | first reader, `wg-e1-classification.json` |
| (ii) two exclusive positive acts | **1** | the same |
| (iii) best response among several | 2 | the same |
| (iv) no conflict between acts | 27 | the same |
| (ii) units that would change a checked answer | **0 of 1** | rule 5 of 2.2, against the run's translation and WG-0's planned rules |

- **The one (ii) unit** is u0204.s01, :531: "Options like raising concerns, seeking clarification, or declining to proceed
  are generally preferable to unilateral intervention." It is borderline with (iii), because the cautious side is an
  open list. It changes no checked answer. The translation regulates seeking clarification
  (`clarification_required`) but nothing on unilateral intervention, and WG-0's planned rules add nothing on it. The
  sentence states a preference, not a duty, so with the acts exclusive no two duties ever meet. Its shape is a
  preference between alternatives (research 4.7: `alternatives@0` with `risk@0`'s "less severe worst case"), not a
  collision of two rules.
- **Help against refuse is (i).** Every unit that names refusing ("decline to assist", "refuse to assist", "unhelpful
  responses": u0147.s04, u0179.s02, u0137.s02) reads as not doing the requested act. The guideline-against-ethics units
  (u0101.s01, u0020.s03) are one act that one consideration requires and another forbids. These collisions are
  soft's same-act collisions once act-phrases identifies the acts.
- **Most units are (iv)**, and the largest group among them names values or considerations without naming acts: the
  value order (u0017.s03, u0019.s05, u0213.s04), balancing considerations (u0066.s02, u0129.s03), and factor lists
  (u0183). The rest are explanations or single norms with a rejected contrast ("rather than adopting a fixed ethical
  framework").
- **Outside the sample.** The paragraph of u0200.s01 (:520) has an explicit exclusive pair in a later unit that was
  not drawn: "alerting authorities or refusing to continue the task" against "complete the assigned work". So (ii)
  exists in the source, but it is rare.
- **Robustness** (post hoc, not a bar). Under the most generous reading, every unit that sets two positively described
  acts or stances against each other counts as (ii). That gives 8 units, just reaching clause 1. None of them changes a
  checked answer, so the verdict is still FAIL (`wg-e1-sensitivity.json`). The observed (ii) rate is 1/40, with a 95%
  Clopper–Pearson upper bound of 0.132, below the bar's 0.20. If the true rate were 0.20, a draw with at most 1 (ii)
  would have probability 0.0015.
- **Limits.** There is one reader (2.4). CROSSACT is a lexical screen, so a unit outside it could express (ii); the bar
  is defined on the screen. Clause 2 was judged against the run's translation and the rules WG-0 plans to add, not
  against a WG-0 translation, which does not exist yet. Clause 1 decided the verdict without it.

### 2.4 Deferred

- **The second reader's blind classification and the agreement figure.** This needs a human or a model call, and this
  phase makes no model call. The subset is frozen: orders 1 to 10 of `wg-e1-sample.json`, marked `second_reader`. The
  second reader should get `excerpt`, `before` and `after` only, never `wg-e1-classification.json`. Agreement is part
  of the protocol but not of the bar, so the verdict stands without it. To change the verdict, 7 more of the 39
  non-(ii) units would have to be (ii) and 5 of them would have to change a checked answer.

### 2.5 The UDHR pilot

Not used. WG-E1's population is the constitution's ledger and WG-0 is a constitution batch; neither names the UDHR
pilot. `pilot/udhr-20261012T1800Z` (`b04b68b0`) was not read or modified.

## 3. Consequences for draft 2

**WG-10 is cancelled.** This is what D14 and WG-E1's bar say to do: "Otherwise record the result and close." Draft 2
should:

1. **Close WG-10 and drop its dependency.**
   - Mark the WG-10 row and section 5's WG-10 subsection closed by WG-E1 (FAIL, this report), keeping their text as
     history.
   - Remove `alternatives@0` (WG-10) from §6's design-wave row and from synthesis edit 10's dependency list.
   - D14's sentence "If WG-E1 passes, exclusive acts come from `alternatives@0` …" becomes a record of the outcome:
     WG-E1 failed (1 of 40), and no exclusive-act construct is planned.
   - Synthesis edit 7 has nothing left to apply.
2. **Make cross-act collisions residual.**
   - §2.7 changes from "collisions between different acts (until WG-E1, and then through `alternatives@0`, WG-10)" to
     "collisions between different acts (measured rare by WG-E1; not planned)".
   - §8's "Not claimed: anything about collisions between different acts before WG-10" changes to "anything about
     collisions between different acts".
   - Soft 4.5's stage 3 and NORTH-STAR's "priority across different obligations" row can cite this result.
3. **Fix WG-E1's row.**
   - Replace "Needs: WG-0; research 2.1's CROSSACT class written first" with "done: FAIL (`weighing-phase1.md`)".
     WG-E1 did not need WG-0, because clause 1 decided it.
   - Fix the text "(draft 1 cited it, and research 2.1 is unfilled)": research 2.1 is now written.
   - The second reader's agreement stays an open line, not a gate.
4. **Strengthen the dependency on act identity.** The constitution's help-against-refuse language is (i): refusing is
   not complying. So the path for it is soft's same-act collision after act-phrases identifies the acts (AP-1 to AP-3),
   not a new construct.
   - Draft 2's D6 and the split-map edit (synthesis edit 8) are confirmed. Weighing's targets name acts as AP identifies
     them.
   - Add a line to §6 or §8: the value-conflict units WG-E1 classified (i) need AP's identity of "decline", "refuse"
     and "unhelpful response" with "not comply" before weighing's conditions can target them.
5. **WG-0 and WG-5 are confirmed as the main path; WG-E2's target is confirmed.**
   - Of the 27 (iv) units, the largest group names a rank between values or a set of considerations without naming
     acts. That is what WG-0 (ranks, the holistic flag) and WG-2 to WG-5 (strength, conditions, factors) express.
   - The cost-benefit units (u0129.s03 :321, u0183 :479) are the open decision and factors that WG-E2 is expected to
     pick (:325-347). No change to WG-E2's bar.
6. **Best response stays research.** 2 of 40 units are (iii) (u0034.s01, :70; u0036.s01, :78), and the one (ii) unit
   has the shape of a preference among alternatives. Draft 2 should keep research 4.7 as research and plan no batch.
   This result neither raises nor lowers its priority.
7. **WG-0 is unchanged and still blocked.**
   - Its prerequisite, RD-9 SC-8 on `main`, does not hold on 2026-10-13: `rd-9/integrate` is not merged, and the
     `ve/document.py` refusal is still in place.
   - Draft 2 keeps WG-0 first on the constitution's path and keeps its "measured by WG-0" pilot effect. No estimate
     replaces it.
   - WG-5's dependency on WG-0 is unchanged.

Batches this phase confirms: WG-0 (priority), WG-2 to WG-5 (the constructs the sampled units need), and WG-E2 (its
expected target). Cancelled: WG-10. Changed: WG-E1's row (done), D14, §2.7, §6 and §8's wording, and the dependency
table (`alternatives@0` removed).
