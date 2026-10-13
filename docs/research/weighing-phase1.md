# Weighing, phase 1: pilots and pre-registered experiments

> Status: complete (2026-10-13), branch `research/weighing-p1` from the converged weighing design (plan draft 4,
> [docs/spec/weighing-PLAN.md](../spec/weighing-PLAN.md)). Phase 1 of the cross-plan build order
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1): "Now, no product code", with WG-E1 under its own gates
> and WG-0 "once RD-9 SC-8 is on `main`". No product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) is changed. One
> model call is made: WG-E1's blind second reader, run after review and saved as evidence (2.4). Scripts are in
> `docs/research/weighing-phase1/`, evidence in `docs/research/evidence/weighing/`. The pilot inputs are read from git
> at pinned commits, never checked out or edited.

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
- **Help against refuse is (i).** The three units that name refusing ("decline to assist", "refuse to assist",
  "unhelpful responses": u0147.s04, u0179.s02, u0137.s02) read as not doing the requested act. The other seven (i)
  units are of other kinds: a guideline against ethics (u0101.s01, u0020.s03), safety against other values
  (u0019.s07), defer against judge (u0200.s01, u0221.s04), a promise (u0289.s05) and Anthropic's own conduct
  (u0274.s02). The review contested u0200.s01, u0221.s04 and u0274.s02, and the second reader did not share any of
  the three calls (2.4).
- **Most units are (iv).** (iv) is the catch-all category, and the classification records no field for what a (iv)
  unit would need. Among the 27, the first reader's notes name the value order (u0017.s03, u0019.s05, u0213.s04),
  balancing considerations (u0066.s02, u0129.s03) and a factor list (u0183); others are explanations, definitions or
  single norms with a rejected contrast ("rather than adopting a fixed ethical framework"). These groups were not
  counted, and the report makes no claim about their sizes.
- **Outside the sample.** The paragraph of u0200.s01 (:520) has an explicit exclusive pair in a later unit that was
  not drawn: "alerting authorities or refusing to continue the task" against "complete the assigned work". So (ii)
  exists in the source. In the sample it is 1 of 40 CROSSACT units (3 of 40 with the second reader's calls on the
  contested units, 2.4).
- **Robustness** (post hoc, not a bar). Under the most generous reading, every unit that sets two positively described
  acts or stances against each other counts as (ii). That gives 8 units, just reaching clause 1. None of them changes a
  checked answer, so the verdict is still FAIL (`wg-e1-sensitivity.json`). The observed (ii) rate is 1/40, with a 95%
  Clopper–Pearson upper bound of 0.132, below the bar's 0.20. If the true rate were 0.20, a draw with at most 1 (ii)
  would have probability 0.0015. With the second reader's calls on the three contested units, (ii) is 3 of 40: the
  upper bound is 0.204, and P(at most 3 | rate 0.20) is 0.028. Both of the new (ii) units are in the generous set
  above and change no checked answer, so clause 2 is still 0 and the verdict is still FAIL.
- **Limits.** CROSSACT is a lexical screen, so a unit outside it could express (ii); the bar is defined on the screen.
  The second reader's subset of 10 is mostly (iv), so it says little about the (i)/(ii) boundary, and on that
  boundary the two readers differed (2.4). Clause 2 was judged against the run's translation and the rules WG-0 plans
  to add, not against a WG-0 translation, which does not exist yet. Clause 1 decided the verdict without it.

### 2.4 The second reader

The plan: "A second reader classifies 10 of them blind; agreement is reported." The first submission deferred this
(rule 6 of 2.2: "this phase makes no model call"). The review rejected that reason: the plan allows model calls saved
as evidence and bars them only from suite tests (plan 8 and 9). So the second reader was run after the review, on the
subset rule 6 froze before the draw. Rule 6 is left as it was written; this section records what was done instead.

- **Setup.** `wg_e1.py blind` writes the input (`wg-e1-second-reader-input.json`) and the prompt
  (`wg-e1-second-reader-prompt.txt`). The prompt was committed at `c999832a`, before the reading. The second reader
  gets, for each unit, the 400 bytes before, the unit's full span from the pinned source, the 400 bytes after, and
  rule 4 of 2.2 read verbatim from this report. It gets nothing else: no first reading, no notes, no rule 5. The
  saved `excerpt` field is cut at about 180 characters, and the first reader read full spans, so the second reader
  gets full spans too.
- **The reader.** A fresh Claude Fable 5.1 subagent session. It is a different model from the first reader (Claude
  Opus 5.5) and shares none of its context. It made 0 tool calls, so it opened no file. Its answer is saved verbatim
  in `wg-e1-second-reader.json`.
- **Agreement (pre-registered subset, orders 1 to 10).** The readers agree on 10 of 10: nine (iv) and u0204.s01 (ii).
  Cohen's κ is 1.0, but chance agreement is 0.82 because 9 of the 10 are (iv), so this subset tests little beyond
  "(iv) is (iv)". The second reader recorded (ii) as a secondary category for u0012.s02 and u0199.s03, the two
  stance contrasts that the generous reading already counts (`wg-e1-agreement.json`).
- **The contested units (post hoc, not in the agreement figure).** The review named three (i) calls as contestable.
  They were added unmarked to the blind input:
  - u0200.s01 (:520): first reader (i), second reader (ii);
  - u0221.s04 (:590): first reader (i), second reader (ii);
  - u0274.s02 (:700): first reader (i), second reader (iv), with (ii) as its secondary category.

  So the readers agree on 0 of 3 where the boundary is hard. Under the second reader's calls, (ii) is 3 of 40,
  against a bar of 8. u0200.s01 is a question and states no rule, and u0221.s04's rule ("defer on those issues")
  meets no rule that requires Claude's own judgment on those issues (`wg-e1-sensitivity.json`). So clause 2 stays at
  0. The verdict does not change. To change it, 7 more of the 39 non-(ii) units would have to be (ii) and 5 of them
  would have to change a checked answer.

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
     WG-E1 failed (1 of 40; 3 of 40 under the second reader's calls on the contested units), and no exclusive-act
     construct is planned.
   - Synthesis edit 7 has nothing left to apply.
2. **Make cross-act collisions residual.**
   - §2.7 changes from "collisions between different acts (until WG-E1, and then through `alternatives@0`, WG-10)" to
     "collisions between different acts (not planned: WG-E1 found 1 of 40 sampled CROSSACT units to be two exclusive
     positive acts, 95% upper bound 0.13)". The scope is the CROSSACT screen of the constitution's `norms` units; (ii)
     pairs exist outside the sample (2.3).
   - §8's "Not claimed: anything about collisions between different acts before WG-10" changes to "anything about
     collisions between different acts".
   - Soft 4.5's stage 3 and NORTH-STAR's "priority across different obligations" row can cite this result.
3. **Fix WG-E1's row.**
   - Replace "Needs: WG-0; research 2.1's CROSSACT class written first" with "done: FAIL (`weighing-phase1.md`)".
     WG-E1 did not need WG-0, because clause 1 decided it.
   - Fix the text "(draft 1 cited it, and research 2.1 is unfilled)": research 2.1 is now written.
   - Record the second reader's result: 10 of 10 on the frozen subset, 0 of 3 on the contested units (2.4). The
     (i)/(ii) boundary is where readers differ; a later measurement that depends on it should have two readers on
     every unit, not on a subset.
4. **Act identity for refusals.** The three sampled units that name refusing (u0147.s04, u0179.s02, u0137.s02) are
   (i): refusing or declining to assist, or giving an unhelpful response, is not doing the requested act. For those,
   the path is soft's same-act collision after act-phrases identifies the acts (AP-1 to AP-3), not a new construct.
   - This is consistent with D6 and the split-map edit (synthesis edit 8), not a test of them.
   - Add a line to §6 or §8: units like these three need AP's identity of "decline to assist", "refuse to assist" and
     "unhelpful response" with not doing the requested act before weighing's conditions can target them.
   - The other seven (i) units are of other kinds (2.3), and two of the three the review contested were (ii) for the
     second reader. They are not evidence for this line.
5. **WG-0, WG-2 to WG-5 and WG-E2: consistent with, not tested by WG-E1.**
   - WG-E1 classified conflicts between acts. It did not measure which construct a unit needs, and (iv) is its
     catch-all. Some (iv) units name a rank between values (u0017.s03, u0019.s05, u0213.s04) or considerations to
     balance (u0066.s02, u0129.s03), which is the kind of text WG-0 (ranks, the holistic flag) and WG-2 to WG-5
     (strength, conditions, factors) are planned to express. How many such units there are was not counted.
   - Two cost-benefit units (u0129.s03 :321, u0183 :479) look like the open decision and factors WG-E2 is expected to
     pick (:325-347). Two citations do not confirm a target; WG-E2's own pre-registered measurement does that. No
     change to WG-E2's bar.
   - Draft 2 should not cite WG-E1 as evidence for these batches.
6. **Best response stays research.** 2 of 40 units are (iii) (u0034.s01, :70; u0036.s01, :78), and the one (ii) unit
   has the shape of a preference among alternatives. Draft 2 should keep research 4.7 as research and plan no batch.
   This result neither raises nor lowers its priority.
7. **WG-0 is unchanged and still blocked.**
   - Its prerequisite, RD-9 SC-8 on `main`, does not hold on 2026-10-13: `rd-9/integrate` is not merged, and the
     `ve/document.py` refusal is still in place.
   - Draft 2 keeps WG-0 first on the constitution's path and keeps its "measured by WG-0" pilot effect. No estimate
     replaces it.
   - WG-5's dependency on WG-0 is unchanged.

Cancelled: WG-10. Changed: WG-E1's row (done, with the second reader's result), D14, §2.7, §6 and §8's wording, and the
dependency table (`alternatives@0` removed). Not tested by this phase, and unchanged: WG-0 (blocked on RD-9 SC-8),
WG-2 to WG-5, WG-E2, and research 4.7.

## 4. Changes after review

- **Second reader run** (2.4), with its input and prompt committed before the reading (`111218fb`, `c999832a`) and
  the answer and agreement after (`1de755c6`). Rule 6 of 2.2 is unchanged as written.
- **Consequences narrowed** (3, items 2, 4 and 5, and the closing line), and the (iv) and refusal bullets of 2.3
  reworded, so that they claim only what the classification records.
- **Script moved** from `research/weighing/wg_e1.py` to `docs/research/weighing-phase1/wg_e1.py` (`68d62236`).
  `tools/layer_policy.py` has no layer for a top-level `research/`, so a branch that touched the old path made
  `select_tests.py` select all 368 test units and the Rust builds. At the new path it selects 82, about the same as
  any file added under `docs/` (79). Only `ROOT` and the usage lines changed in the move; `screen`, `draw` and `tally`
  rerun from the new path write byte-identical evidence. `blind` and `agree` were added after the move.
