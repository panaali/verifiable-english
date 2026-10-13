# Weighing, phase 1: pilots and pre-registered experiments

> Status: in progress (2026-10-13), branch `research/weighing-p1` from the converged weighing design (plan draft 4,
> [docs/spec/weighing-PLAN.md](../spec/weighing-PLAN.md)). Phase 1 of the cross-plan build order
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md` 4.1): "Now, no product code", with WG-E1 under its own gates
> and WG-0 "once RD-9 SC-8 is on `main`". No product code (`ve/`, `lean/VE/`, `rust/`, `tools/`) is changed and no
> model is called. Scripts are in `research/weighing/`, evidence in `docs/research/evidence/weighing/`. The pilot
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

PENDING (filled after the draw).

### 2.4 Deferred

PENDING.

## 3. Consequences for draft 2

PENDING.
