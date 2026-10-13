# Quantities, phase 1: pilot repair and pre-registered experiments

> **Status.** 2026-10-13, branch `research/quantities-p1` from `b76f2dc6` (quantities spec draft 2, plan draft 3).
> Phase 1 of [quantities-PLAN.md](../spec/quantities-PLAN.md) as the cross-plan synthesis orders it (`SYNTHESIS.md`
> 4.1, phase 1: "QT-0p … QX-1–QX-3, each under its own gates"). No product code changed (`ve/`, `lean/VE/`, `rust/`,
> `tools/` untouched), no model call, nothing pushed. Scripts: `research/quantities/`. Evidence:
> `docs/research/evidence/quantities/`. Every bar below is quoted from plan draft 3 before its result; no bar was
> changed after a result was seen.

## 0. Summary

| Item | Pre-registered bar (plan draft 3) | Result | Verdict | Commit |
|---|---|---|---|---|
| QT-0p | "C 0–128 B, U 0–76 B"; probes "no fourth type" SETTLED no, "higher education" UNDECIDED; done when both pilots re-run and the next audit samples the changed units | C +128 B claimed (113 CHECKED, 15 LABELLED); U +76 B (OPEN); both probes as registered; both pilots rebuilt and checked on main. Cost: the constitution's premise check falls from a model to UNKNOWN | **PASS** (bytes, probes, re-run); the audit step is **DEFERRED** | `2a83581c` |
| QX-1 | No numeric bar: "The experiment only shapes the rewrites and the members of each reading set" | Not run. Audit: the plan lists 42 items against a 36-item budget; most contexts are not written | **DEFERRED** (40 model sessions) | `8092c005` |
| QX-2 | "the decomposed form is faithful on at least 5 of 6 units, introduces no threshold on any, and is judged no worse than the current form on every unit" | Not run. Audit: the plan has a decomposed form for 2 of the 6 units; the latest audit found the current form of all 6 unfaithful | **DEFERRED** (blind model audit; material missing) | `8092c005` |
| QX-3 | No bar: "The answers shape rewrites only." | Not run. Audit: 4 of 20 items are stated; 2 of the 4 labels hold only with a premise the item does not state | **DEFERRED** (40 model sessions) | `8092c005` |

Language: `main` at `406736a4`, run from the 2026-10-13 0600Z pilot checkout (`ve-pilot-20261013T0600Z`, at
`406736a4`, with builds that match its code). `ve-integration` was not used: its `ve_service` build is stale (the
handshake fails with "unexpected handshake (modes: no element is valid)"). Every `ve` run is wrapped in
`prlimit --as=6442450944`, with `VE_RUST_TIMEOUT=600`. That variable is a hang guard only: Rust's work limits are its
evaluation budgets. One run under load average 62 failed the 5 s default. Inputs, read only:
`manage-agents/pilots/claude-constitution/run-20261012T1800Z` (`translation.ve.md` SHA-256 `adecddd3…`, recorded in
`qt0p/summary.json`) and `manage-agents/pilots/udhr/run-20261012T1800Z` (`translation-part03.ve.md` `20437df2…`).

## 1. QT-0p: pilot repair with the existing language

**Bar, quoted before the run** (plan 4, QT-0p): "Bytes: C 0–128 B, U 0–76 B, until audited. Done when both pilots
re-run with the repair and the next audit samples the changed units." Probes: "Is there a fourth type of principal?"
(SETTLED no); "Must higher education be free under this sentence?" (UNDECIDED). Section 7: "0–128 B claimed
(u0042.presupposition, u0043.s02); probe 'no fourth principal type' SETTLED no | 0–76 B (u097); probe 'higher
education' UNDECIDED".

### 1.1 What was written

- **Constitution** (`relational-fol@0`). New vocabulary: the sort `principal_type`, the constants `anthropic`,
  `operators` and `users`, and the unary predicate `claude_principal_type`.
  - u0042.presupposition (38 B), "Claude’s three types of principals": its presupposed claim "Claude has three types
    of principals" becomes *exactly three*. That is, there are x, y and z, pairwise different, each one of Claude's
    types, and every one of Claude's types is x, y or z. CHECKED.
  - u0043.s02 (90 B) becomes a MIXED unit. "At the moment, " (15 B) is LABELLED: it names the document's present
    without a date, and adds no indexical (edit 9). The rest (75 B) is CHECKED: the three facts, pairwise
    distinctness, and the closure "every one of Claude's types of principals is Anthropic, operators or users".
  - u0043.s01 is unchanged (UNFORMALISED, `counting`).
- **UDHR** (`norm-defaults@0`, completion `unspecified`). u097 (76 B), "Education shall be free, at least in the
  elementary and fundamental stages.", becomes a duty with no bearer, as u098 is written. Its guard is "elementary or
  fundamental", over the translation's own `education_kind` with its existing `is_elementary` and a new
  `is_fundamental`. Other stages fall to `unspecified` ("the text does not say"), which is exactly what "at least"
  leaves open. "Free" is the open term `free_education`, as "compulsory" is in u098. So the unit is OPEN, not CHECKED.

Three departures from the plan's wording, each so the text says no more than the source:
1. The heading's claim names no one. The plan says "the heading's presupposed claim is the same content", but the
   heading does not name the three types; u0043.s02 does.
2. The closure is limited to Claude's types: "every one of Claude's types is …", where the plan has
   `∀t:principal_type. t = anthropic ∨ …`. The plan's form would also say that no other kind of principal exists at
   all. Both forms give the same answer to the registered probe.
3. u097 uses the translation's own predicates on `education_kind`, not constants of a new sort `education_stage`.
   This keeps u097 and u098 on one vocabulary. Nothing in the source says the elementary and fundamental stages
   differ, so the guard does not assume it.

### 1.2 Method

1. **Companion documents** over exactly the units' bytes: `qt0p/constitution-u0042-u0043.ve.md` (source bytes
   23,448–23,677) and `qt0p/udhr-u097.ve.md`. Each was run through `ve document check`.
2. **Pilot re-run, constitution.** The added vocabulary changes the environment id, so every reading-set identity and
   situation has to be recomputed. The pilot's own rebuild, `nd.py all`, does that. It was run on copies of the
   pilot's inputs (`translation-without-content.ve.md`, `readings/all-strict.ve.md`, the pilot scripts, and main's
   `tools/readings_s1_pilot.py`), once unchanged (*baseline*) and once with the repair, and each result was checked
   with `ve document check` and `ve document coverage`. The baseline reproduces the pilot's recorded figures exactly:
   CHECKED 73, LABELLED 349, OPEN 2,529, UNFORMALISED 181,942, premises `model`, 0 pairs without a situation. The
   rebuilt baseline is byte-identical to the pilot's `translation.ve.md` (SHA-256 `adecddd3…` both), so main gives
   the same reference point as `ve-green-ts-B1`.
3. **Pilot re-run, UDHR.** The repair was spliced into a copy of `translation-part03.ve.md`. The part's two older
   reading sets, which carry `models` and formula content, were re-identified with main's own `meaning_id` and
   `FiniteModel.from_dict`; each model also gets an empty relation for each of the two new predicates. The part was
   then checked and its coverage measured, and the original part's coverage was measured on the same build.
4. **Probes.**
   - Constitution: `ve document readings --conclusion` on the rebuilt translation, as the pilot's own conclusion
     probes run. Lean's readings route refuses `readings@1` on a document with no reading set ("Unsupported profile
     readings@1"), so these probes cannot run on the companion document.
   - UDHR: Lean's `norm-defaults-status` rows, read as the UDHR pilot's `witnesses_nd.py` reads them.
5. **A model of the repaired content.** `ve.search.find_countermodel` with the conclusion "bottom" (the Rust
   enumerator, with the witness checked by Lean) was run at domain sizes 2 and 3.

### 1.3 Results

| Measure | Baseline (main) | Repaired | Change |
|---|---:|---:|---:|
| Constitution CHECKED / LABELLED / OPEN / UNFORMALISED (B) | 73 / 349 / 2,529 / 181,942 | 186 / 364 / 2,529 / 181,814 | +113 / +15 / 0 / −128 |
| Constitution claimed bytes (CHECKED + LABELLED + OPEN) | 2,951 (1.60%) | 3,079 (1.67%) | **+128** |
| Constitution premise check (whole translation) | `model` | **UNKNOWN** | lost |
| UDHR part03 CHECKED / LABELLED / OPEN / UNFORMALISED (B) | 379 / 105 / 534 / 1,986 | 379 / 105 / 610 / 1,910 | 0 / 0 / +76 / −76 |
| UDHR claimed bytes (whole declaration, pilot's figure plus the change) | 4,792 (43.90%) | 4,868 (44.60%) | **+76** |
| UDHR part03 premise check | `model` | `model` | unchanged |

| Probe | Registered | Measured |
|---|---|---|
| "Is there a fourth type of principal?": the negation, on the rebuilt constitution | SETTLED no | **ALL**, by certificate, on the superposed route: "This does not depend on how sentence 132 / 590 / 1001 is read." |
| Same, positive form "there is a fourth type" (an extra check, not registered) | (NONE would be the same answer) | UNKNOWN: no model within the readings route's search budget |
| Control: "Anthropic is one of Claude's types of principals" (extra) | — | ALL |
| "Must higher education be free under this sentence?": status of `education_free_required` at a stage that is neither elementary nor fundamental | UNDECIDED | **UNDECIDED** (no rule); the same in the companion and in the rebuilt part |
| Status at an elementary stage, a fundamental stage, and one that is both (controls) | SETTLED yes | SETTLED yes, by rule `u097-free-at-least-elementary-and-fundamental` |

**Why the premise check is UNKNOWN.** "Exactly three" needs three distinct objects of one sort. The document
check's premise search has a fixed budget of `max_domain_size: 2`, so it cannot find a model, and it proves no
inconsistency either. The repaired content is consistent: at domain size 3 the search finds, and Lean checks, the
model {e0 = anthropic, e1 = operators, e2 = users}, with each of them one of Claude's types. At domain size 2 it finds
none (`qt0p/summary.json`, `model_search`). The same budget is why the positive "fourth type" probe is UNKNOWN and not
NONE.

**Wording (seen, not measured).** The readings route's English shows the new predicate as
`classified as "claude_principal_type"` and ignores its verbalisation. This is the known `other:english_wording`
residual: a unary predicate is shown by its wording only when that wording is one word after "is".

**Verdict: PASS** on what phase 1 can measure. Both byte figures are at the top of their registered ranges (C 128 of
0–128 B, U 76 of 0–76 B). Both probes answer as registered, and both pilots were re-run with the repair. These bytes
are claimed, not audit-verified: the plan says "until audited", and the step "the next audit samples the changed
units" is an independent model audit, so it is **DEFERRED**. The repaired documents are measurement copies (their
SHA-256 is in `summary.json`); the pilots' own translations were not edited. Applying the repair is the next pilot
run's step, and the changed units for its audit are u0042.presupposition, u0043.s02 (both parts) and u097.

## 2. QX-1: "most", "many", "multiple", bare "16 of the 18", bare "105 percent of"

**Bar, quoted before any data** (plan 5, QX-1): there is no numeric bar. "The experiment only shapes the rewrites
and the members of each reading set; agreement among proxy readers never admits an ambiguous wording." Authoring
refuses "most" and "multiple" "whatever the result". (Research R5.2 gave a bar of "36 of 40 agreement on 5 of 6".
Draft 3 replaced it with the rule above, and the plan's rule is the one that holds.)

**Verdict: DEFERRED.** The readers are 40 independent Sonnet 5.5 sessions, so running QX-1 needs model calls.

**What the audit of the pre-registration found** (`qx/prereg-audit.json`; no model call):

1. **The item count is inconsistent.** The plan lists six contexts each for seven words or forms ("most"; "many",
   "few" and "several"; "multiple"; bare "n of the m"; bare "105 percent of"): 42 items. Its cost line budgets "40
   sessions × 36 items = 1,440 short calls". 42 items is 1,680 calls.
2. **"most" names five points for six contexts:** 50, 51, 60 and 95 of 100, and 3 of 5.
3. **Most contexts are not written.** Missing: all eighteen for "many", "few" and "several" (only their purpose is
   given: to separate the cardinal reading from the proportional one); the sixth "most" context; four of the six
   "multiple" contexts; and five of the six each for bare "n of the m" and bare "105 percent of". The answer format
   and the analysis are not stated either.
4. **What the fixed items can show** (each reading's answer is computed from the plan's own definitions):

| Item | Readings and their answers | Separates the readings? |
|---|---|---|
| "most" at 50 of 100 | more than half: no; open proportion grade: no answer | the only "most" item where "more than half" says no |
| "most" at 51, 60, 95 of 100 and 3 of 5 | more than half: yes; open grade: no answer | only against the open grade |
| "multiple" at 1 / at 2 | at least two: no / yes | one reading; checks agreement only |
| bare "16 of the 18": is 17 compatible? | exactly: no; at least: yes | yes (the spec's distinguishing model) |
| bare "105 percent of": is 105.4 compatible? | exact: no; to the nearest percent, `tiesUp` or `halfEven`: yes | yes (105.4 is not a tie, so the two rules agree) |

The seeded order (`Random("quantities-QX1")`) of these nine items is recorded. It will change once the missing
items are added, so it is not the order to run.

## 3. QX-2: the hard-constraint decomposition audit

**Bar, quoted before any data** (plan 5, QX-2): "the decomposed form is faithful on at least 5 of 6 units,
introduces no threshold on any, and is judged no worse than the current form on every unit. Then QT-B4 ships it;
otherwise the whole-clause terms stay, with the auditor's reason recorded."

**Verdict: DEFERRED.** The audit is "one blind independent audit (the reviewer pair of the model split) per unit",
so it needs model calls. The material it audits does not exist yet for four of the six units (below).

**What the audit of the material found** (from the pinned ledger and the run's `AUDIT.md`):

| Unit | Bytes | Graded words in the source | Decomposed form in the plan | Latest audit of the current form (run 20261012T1800Z) |
|---|---:|---|---|---|
| u0165.s01 | 147 | "serious" (uplift), "mass" (casualties) | FB1: `uplift` on `response`, grade `gives_serious_uplift` | UNFAITHFUL |
| u0165.s02 | 139 | "serious" (uplift) | none (FB1's dimension could carry it; the plan does not say) | UNFAITHFUL |
| u0165.s03 | 89 | "significant" (damage) | none | UNFAITHFUL |
| u0165.s04 | 175 | "clearly", "substantially" (undermine) | none | UNFAITHFUL |
| u0165.s05 | 116 | "vast majority" | FB6: `share_of_humanity_targeted` on `attempt`, grade `vast_majority` | UNFAITHFUL |
| u0165.s06 | 160 | "unprecedented", "absolute" (degrees of control) | none | UNFAITHFUL |
| **total** | **826** | | **2 of 6** | **0 of 6 faithful** |

1. **As written, the bar needs material the plan does not have.** "Faithful on at least 5 of 6 units" requires a
   decomposed form for at least five units. The plan gives two (FB1, FB6). At least three more dimensions and grades
   are needed before QX-2 can be run: damage for s03; undermining, with two adverbs, for s04; degrees of control for
   s06; and s02, which may reuse FB1's dimension.
2. **The comparator is itself rejected.** The latest audit rejected the current form of all six units, for its
   applicability guard ("actual restricted-category membership AND knowledge-or-likelihood" loses the
   mistaken-but-confident cases of u0173.s01), not for its open terms. "No worse than the current form" is therefore
   a comparison with an unfaithful baseline. The auditors would have to judge the graded word apart from the guard.
3. **The current form will change before QT-B4.** The hard-constraint queue (synthesis 4.4) rewrites u0165.s01–s07 in
   AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5 before QT-B4. A QX-2 run now would audit a form QT-B4 never starts from.

## 4. QX-3: inferences with proportional grades

**Bar, quoted before any data** (plan 5, QX-3): there is none. "The answers shape rewrites only." The plan asks for
"Twenty items, ten valid under counting semantics and ten invalid", and the majority schema "is not offered on any
vote".

**Verdict: DEFERRED.** The readers are 40 Sonnet 5.5 sessions, so running QX-3 needs model calls.

**What the audit of the pre-registration found** (`qx/prereg-audit.json`). The plan states 4 of the 20 items. Each
stated label was re-derived under counting semantics ("most S are P" = more than half of a nonempty S) by listing
every assignment of sizes to the regions, for every population of up to 12 objects. These enumerations are checks,
not proofs. Items 3 and 4 also have short exact arguments: monotonicity, and the countermodel shown.

| Item (plan) | Plan's label | Under counting semantics | Agrees? |
|---|---|---|---|
| "The vast majority voted. Did a majority vote?" | valid | depends on the grade's threshold: valid exactly when it is above one half. That is the bridge "the vast majority implies more than half", which the same section says is "not offered on any vote" and waits for QX-4's proof | **no** |
| "A majority voted yes and a majority voted no." | contradiction | satisfiable unless the item adds that no one voted both. With that premise it is a contradiction (FA1 needs the same kind of exclusion premise) | **no**, as stated |
| "Most S are P; every P is Q. Are most S Q?" | valid | valid: #(S and Q) ≥ #(S and P) > #S / 2; no countermodel up to 12 objects | yes |
| "Most S are P. Are most P S?" | invalid | invalid: the smallest countermodel is one object that is S and P plus one that is P only | yes |

## 5. Consequences for draft 2

Phase 1 cancels no batch. It confirms QT-0p. It changes the three experiments' specifications before they can run,
and it records one cost of QT-0p that the plan did not foresee.

- **QT-0p: confirmed, with a cost to record.**
  - The repair is buildable today and measured at the top of both ranges: C +128 B, U +76 B, claimed.
  - Draft 2 should replace "C 0–128 B, U 0–76 B (estimate)" with the measured figures, keeping "until audited".
  - New cost: once "exactly three" is in the translation, the whole constitution's premise check is UNKNOWN instead
    of `model`. The document check's premise search stops at domain size 2, and the model needs 3. Draft 2 should
    record this and choose one of:
    - keep the repair and accept UNKNOWN;
    - drop distinctness, which loses "three";
    - a larger or per-sort premise budget. That is product code (a check budget), outside phase 1. It would be a
      small item, not part of QT-A1.
  - Pilot tooling: companion documents cannot carry `readings@1` probes without a reading set, so QT-0p-style probes
    run on the full translation.
  - The audit sampling of the changed units stays the remaining step.
  - QT-A1 is not needed for these units, and nothing here changes QT-A1.
- **QX-1: the item list must be completed and reconciled before execution.**
  - Draft 2 should either budget 42 items (1,680 calls) or say which items are cut.
  - It should name the sixth "most" point and write and review the missing contexts: "many", "few", "several", the
    rest of "multiple", bare "n of the m" and bare "105 percent of". Writing them now is still pre-registration,
    because no data exists.
  - On the fixed items, only "most" at 50 of 100 distinguishes "more than half" from "at least half". Draft 2 may want
    a second boundary point.
  - Batches affected: QT-A6's reading-set rows for "most" and "multiple", and the spec's row j, stay "pending". The
    authoring refusals stand whatever QX-1 finds.
- **QX-2: cannot be run as written.**
  - Before execution, draft 2 must either add decomposed forms (dimension, grade, direction) for at least three more
    of u0165.s02, s03, s04 and s06, or restate the bar over the units it decomposes. Neither is a move after data:
    no audit has run.
  - QX-2 should audit the form QT-B4 will start from, which is after WG-5 in queue 4.4. It should not audit today's
    form, which was rejected (0 of 6) for its guard.
  - QT-B4's "826 B faithful" stays gated on QX-2. FB1 and FB6 (QT-B1) are unaffected.
  - The "audit-verifiable after the next audit" line in section 7 should say that the baseline is currently
    unfaithful.
- **QX-3: 16 of the 20 items are unwritten, and two stated labels need fixing.**
  - Item 1's label "valid" contradicts the plan's own rule that the vast-majority bridge is not offered. Replace the
    item, or label it "valid only with the unproved bridge" and keep it out of the valid ten.
  - Item 2 must state that no one voted both, or be relabelled "satisfiable".
  - Only rewrites (QT-A6) are affected. QX-4's bridge item is unchanged.
- **Unchanged:** the order (QT-0 next, then QS-1, QT-A1 …), the owners, and every Lean statement. Phase 1 touched no
  statement.

## 6. Deferred, with reasons

| Item | Reason |
|---|---|
| QT-0p's "next audit samples the changed units" | an independent audit is a model call; it belongs to the next pilot run's audit (units u0042.presupposition, u0043.s02.p1, u0043.s02.p2, u097) |
| Applying QT-0p to the pilots' own translations | pilot inputs are read only here; the pilot runner applies the repair (content in `qt0p/*.ve.md`) |
| QX-1 execution | 40 Sonnet 5.5 sessions (model calls); the item list is also incomplete (2) |
| QX-2 execution | a blind audit by the reviewer pair (model calls); decomposed forms are missing for 4 of 6 units (3) |
| QX-3 execution | 40 Sonnet 5.5 sessions (model calls); 16 of the 20 items are unwritten (4) |
| A larger premise budget for "exactly three" | product code (the document check's search budget) |
| News rows 7b and 22b (94 B) | not phase 1: the plan records them as a DRI decision item (a converged W6 ruling) |

No product code changed, so no seeded bug was planted. No pytest was run (no test or product file changed).

## 7. Reproduce

From the repository root (both scripts run `ve` from main's pilot checkout, under `prlimit --as=6442450944`):

    python3 research/quantities/qt0p.py        # 6.5 to 22 min, depending on machine load; writes docs/research/evidence/quantities/qt0p/
    python3 research/quantities/qx_prereg.py   # no ve run; writes docs/research/evidence/quantities/qx/prereg-audit.json
