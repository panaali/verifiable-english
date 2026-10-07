# Pick a reading under unspecified defaults (`readings@1` × `norm-defaults@0`): buildable plan

> Status: plan, draft 2 (2026-10-07). Draft 2 applies the converged review (Astra and Fable, debate
> `design-readings-defaults`, converged in round 3): **BUILD with mandatory RD-0 corrections**, edits E1 to E5 and A1 to
> A4, each marked where it lands. The statement spec [readings-defaults.md](readings-defaults.md) (RD-0) elaborated
> every statement of this plan; where its Lean differs from the blocks below, the spec is authoritative and its
> section 12 lists each difference. Draft 1 follows.
>
> Draft 1 (2026-10-06), branch `design/readings-defaults` from `main` at `6cbe1a26`. Written from the
> brief (`manage-agents/prompts/brief-readings-defaults.txt`), ARCH-ROADMAP's line of 2026-10-05, the UDHR pilot runs
> `udhr-translate-20261005T1800Z` and `-20261006T1800Z` (pilot commit `bd6c7ab2`, read with `git show`), and, at
> `6cbe1a26`: [composition-s1.md](composition-s1.md), [composition-s2.md](composition-s2.md) (S2a, merged),
> [norm-defaults.md](norm-defaults.md), `docs/lean-first/{b3,b3b,b3d,b10a}/DELTA.md`, the lean-first plan
> (`ve-design-lean-first/docs/LEAN-FIRST-PLAN.md`, draft 3), [senses.md](senses.md) and
> [senses-PLAN.md](senses-PLAN.md), `lean/VE/{Readings,NormDefaults,Compose}/*.lean`, `lean/READINGS.md`, and
> `ve/{document,readings,readings_route,readings_verdicts,readings_s1,norm_defaults,norm_defaults_route}.py`,
> `ve/backends/senses.py`, `ve/__main__.py`. Planning only: no code, proof or test changed, and no model was called.
> **The Lean statements below were not elaborated in this session** (the session's permissions refused every `lake`
> and `lean` command). Every name they use was read in the merged sources; elaborating them is RD-0's first step.
> Fixture values marked *derived* were worked out by reading the sources and were not run. Numbers marked
> *recorded* are copied from the cited records.

## 0. Summary

The UDHR translation keeps its norm readings in 156 small companion documents, because `readings@1` refuses content
beside `norm-defaults@0` (S1's named abstention, kept by S2a 4.10). So the main document's verdict over its premises
is UNKNOWN, "non-assertion reading elaboration pending", and no unit with a reading set has a checked verdict inside
the document. This plan builds the composition in Lean in four steps, each with one owner:

1. **`fill` as a readings document.** On the norms chain every rule is strict, so `soften` changes nothing and
   norm-defaults' `fill` can be applied to the readings document itself: the unsaid predicates join the frame as
   base predicates, each synthetic rule `F_p` becomes a fixed unit, and every root rule on an unspecified predicate
   is placed under it. Four equalities (`fillDoc_one`, `_free`, `_choice`, `_sup`) say that each reading's document,
   each choice's document and the superposed document of the filled document are exactly `fill` of the original
   ones. Every theorem of S1 and S2a then applies to the filled document unchanged. What the completion adds on top
   is one premise family, `Fill_T` ("whatever must be done may be done", at gaps), which this plan carries
   explicitly.
2. **Readings checked one way at a time under the completion.** Admission runs norm-defaults' author checks on every
   reading's document, separation compares two readings on one base with one filling (the witness's filling must
   satisfy its `Fill_T`), and each compatible choice is checked by norm-defaults' own checkers on the regenerated
   document. The ALL, SOME and NONE fold, its conditions and the choice of English sentences move from Python into
   Lean.
3. **Readings that carry their own vocabulary.** The UDHR declares 156 unspecified regulated predicates, and the
   frozen norms decoder accepts at most 64 per environment, so one frame cannot hold them. A reading may therefore
   carry its companion's environment inline. A set whose readings all do so becomes a **component** with its own
   frame: its readings' declarations merged, and identical declarations unified. The document's meaning is the
   product of its components, and the report says, in English, that each such sentence was checked by itself.
4. **The UDHR, migrated and measured.** A script inlines the companions, leaves on W2 every set whose readings
   declare a name differently (listed as needing one vocabulary, not decided; E1), gives the three asserted
   readings that have no companion one copied from the main frame, proposes separating situations, and records the
   load time, the limits and the **Lean-decided share** before and after, all measured at one commit.

Superposition under the completion (S2a's route with `Fill_T` carried) and the Lean fold for the superposed route
follow. They are not on the UDHR's path, since every UDHR component has at most 6 readings. Wiring the sense
dictionary into `ve document` does not fit these batches (section 6). It is listed as the next batch, RD-8.

## 1. Evidence

### 1.1 The UDHR pilot, run 20261006T1800Z (recorded)

| Measure | Value | Source |
|---|---|---|
| Units; source bytes | 130; 10,916 (100% accounted) | `metrics.json` |
| Units by status (CHECKED, LABELLED, READINGS, UNFORMALISED) | 1, 34, 49, 46 | `unit_counts_by_status` |
| Bytes by status | 57, 535, 4,200, 6,124 | `bytes_by_status` |
| Claimed covered bytes | 4,792 (43.90%) | `claimed_covered_bytes` |
| Audit-verified covered bytes | 2,543 (23.30%) | `audit_verified_covered_bytes` |
| Reading sets; candidates | 49; 158 | `reading_set_count`, `reading_set_candidates` |
| Companion documents | 156 (155 belong to set candidates; u074's belongs to the CHECKED fixed unit, `build.py` `KEPT_COMPANIONS`) | `companion_documents`, `reading_sets[*].candidates[*].companion` |
| Regulated predicates in the companions | 156, all `unspecified`: 109 obligations, 18 permissions, 29 plain | `vocabulary_use` |
| Regulated predicates in the main document; its limit | 1; 64 | `vocabulary_use.regulated_limit`; `lean/VE/Norms/Wire.lean:145` |
| Main document profiles | `documents@1`, `norms@0`, `relational-fol@0` (no `readings@1`) | `translation.ve.md` |
| Premises verdict of the main document | UNKNOWN, "non-assertion reading elaboration pending" | `verdict.json` |
| W2 reading plan | `route: UNKNOWN`, `budget.max_choices: 64` | `verdict.json` |
| Load, check and render of the main document | under a second each, with the tag's own limits | `SUMMARY.md` |
| Each companion | loads, checks (premises `model`) and passes its status witnesses (SETTLED inside a rule, UNDECIDED outside), as a separate document | `checks.companion_documents`, `SUMMARY.md` |
| Sets mixing a companion reading with an asserted reading that has no companion | 3: `rs_u052` (`case_excluded`), `rs_u112` (`exercise_unprotected`), `rs_u114` (`no_implied_right`) | `metrics.json` `reading_sets` |
| Sets with one reading | 4: `rs_u054`, `rs_u061`, `rs_u099a`, `rs_u099b` | the same |
| Largest set | 6 readings (for example `rs_u048`, `rs_u063`, `rs_u066`, `rs_u070`, `rs_u073`, `rs_u084a`) | the same |

Two counts are *derived* here from the rule predicates of the 156 companions (`git grep` at `bd6c7ab2`), and RD-5's
script recounts them:

- **29 sets have a predicate name that two or more of their readings' companions declare**: `rs_u020`, `u022a`,
  `u022b`, `u022c`, `u024`, `u027`, `u037`, `u045a`, `u045b`, `u046`, `u048`, `u049`, `u051`, `u055`, `u059`,
  `u063`, `u064`, `u066`, `u070`, `u073`, `u077`, `u081`, `u084a`, `u084b`, `u087`, `u096`, `u105a`, `u105b`,
  `u111`. Some pairs declare the name differently: `rs_u022a`, `rs_u027` and `rs_u055` each declare one predicate
  whose first sort is `state` in one reading and `bearer` ("a State, group or person") in another (in `rs_u022a`,
  `avoid_life_required` takes `(bearer, person)` in `anyone_negative` and `(state, person)` in `state_negative`).
  These are the UDHR's State-or-anyone axis; E1 leaves such sets on W2.
- *Derived in draft 2* (`git show` at `bd6c7ab2`): the main frame declares `arises_from_non_political_crime` and
  `arises_from_acts_contrary_to_un` without the `verbalisation` that `u052.invocation_barred`'s companion gives
  them, so a companion for `case_excluded` copied from the main frame (RD-5) declares them differently, and
  `rs_u052` is not migrated either. RD-5's script recounts this for `rs_u052`, `rs_u112` and `rs_u114`.

### 1.2 What the code does today (read at `6cbe1a26`)

- **The abstention.** `Readings/Wire.lean:511` `abstention` refuses a content-bearing set beside `norm-defaults@0`
  on every chain with `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented`. Its frame is
  decoded with each `unspecified` completion read as `deny` (`placeholderFrame`, DRI ruling 4). `Route.lean`'s
  `routeOf` returns `.abstention`.
- **W2's path.** With no `readings@1` content, a norm reading has `content: null`, and `ve/document.py:1250` reports
  the premises as UNKNOWN with the reason above. That is the UDHR's case.
- **The 64 limit.** The norms environment decoder refuses more than 64 regulated predicates (`Norms/Wire.lean:145`,
  `Norms/Tree.lean:304`, norms.md's 11.1 table). W1 also caps rules at 256, and norm-defaults caps rules plus
  unspecified predicates at 256 (`NormDefaults/Wire.lean:82`).
- **Separation is mandatory.** In a content-bearing set, every ordered pair of readings with content needs a
  recorded situation that separates them (`Readings/Run.lean:216-236`; S1 3). The UDHR has none.
- **The fold is Python's.** On the enumerated route, Lean replays each choice's evidence through `readings-choice`,
  and `ve/readings_verdicts.py` (1,126 lines) combines the results into ALL, SOME, NONE, CONFLICT-FREE and the
  premise statuses. It also computes the labels an answer depends on by replaying certificates (`_replays`,
  `_dependencies`), computes the restrictions, and picks the English sentences (`readings_route.Wording`). On the
  superposed route ALL is one Lean-checked certificate, but SOME and NONE are assembled in Python.
- **norm-defaults in Lean (batch 10a).** `fill`, `Fill_T` (`fillPremises`), `WellFormedU`, `checkAuthorN`, the
  conflict check `conflictFreeCheckU`, entailment `premisesU`, statuses and the report (`Report.lean`, with extra
  base premises `X`), and the soft and rights branches (`Layered.lean`) exist. At runtime, Python is still the
  authority for norm-defaults documents; batch 10b switches the callers.
- **Senses.** Only `ve senses check` reaches the sense reader (`ve/__main__.py:54`, `ve/backends/senses.py`).

### 1.3 Measured references (not predictions for this plan)

- Lean-first batch 3d: the UDHR translation of run 20261003T0600Z (`readings@1` on the rights chain, 39
  content-bearing sets, 176 readings) loaded through `ve document check` in 49.3 and 49.6 s wall at load 5.9 to 6.9
  on 32 cores. The base had failed at the route's 120 s limit (`docs/lean-first/b3d/DELTA.md`).
- Batch 10a: norm-defaults report cases cost about 2.9 ms of Lean CPU per case, and the other new kinds about 2.3 ms
  (`docs/lean-first/b10a/DELTA.md`, gate item 4).

## 2. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | On the norms chain, the composition is S1 and S2a run on `fillDoc N`, the readings document with `fill` applied to it, with `Fill_T` added where admissibility is read | `fill` adds one base predicate and one strict rule per unspecified predicate, and parents only. With every rule strict, `soften` is the identity on the tree (`soften_hard_identity`), so `fill` commutes with taking any reading's or choice's document (3.1). Every S1 and S2a theorem is then reused on `fillDoc N` as stated | a second readings theory for UDocs, which would duplicate S2a's simulation |
| D2 | The soft and rights chains keep the abstention, with today's text | norm-defaults 2.3 runs `fill` after `soften`. Inside `soften`, a strict `F_p` would block every default rule, so D1's commutation fails there. The soft chain (the constitution's strict and default readings) needs the after-`soften` theory of `Layered.lean`, carried through S2a: RD-9 | lifting the abstention everywhere |
| D3 | Under the completion, one compatible choice at a time first (the enumerated route), superposed later (RD-6) | Every UDHR component has at most 6 readings. Superposition needs `Fill_T` carried through S2a's five theorems, which is RD-6's work | superposition first |
| D4 | Separation under the completion compares two readings on **one base and one filling**. The witness's filling must satisfy the witness's `Fill_T`; the other reading is not achieving where the filling breaks its `Fill_T` | The unsaid tables are base predicates of the filled frame, so S1's `separates` reads them as shared base tables and needs no change. A filling is "how the text's silences are answered". Two readings that leave the same point unsaid agree on it under every shared filling; a reading that decides a point the other leaves unsaid is separated by the filling that answers the other way. Shared fillings are the definition, not an approximation (E5, closing Q2): with independent fillings a reading would be separated from itself at any gap. An unseparated pair is equal meaning or a search miss | enumerating the other side's fillings over the probe's cone (it would separate a reading from itself) |
| D5 | ALL, SOME, NONE, the conflict and premise statuses, the conditions (`conditional_on`, restrictions), the labels used, and which English sentences an answer gets are computed in Lean from the evidence. Python searches for evidence and renders sentences | lean-first rule 1 (Lean owns verdicts and folds); the brief | a Python fold over Lean-checked parts (today) |
| D6 | A reading may carry its own vocabulary: `"companion": {"environment": {…}, "open_terms": […]}` on the candidate, inline (`open_terms` beside `environment`: E4) | The UDHR's 156 regulated predicates exceed the frozen limit of 64 per environment. Inline keeps one file, one identity and no Python file reading, and Lean reads only JSON it already receives | companions by file path and digest (Python I/O plus a Lean front-matter parser); raising the frozen limit (a frozen-contract change, kept as open question Q1) |
| D7 | A set whose readings all carry companions is a **component**: its frame is the merge of its readings' environments. A name declared twice must be declared byte-identically, otherwise the document is refused. Components share nothing. The document's meaning is the product of the components' meanings | One sentence's readings must share one vocabulary, or the questions "do they differ?" and "does this follow under every reading?" have no common terms. Different sentences' companions declare terms independently, so nothing in the document relates them | auto-renaming conflicting names (hidden machinery); merging every component into one frame (over the limit) |
| D8 | The English says that a component was checked by itself (E31). No document-level sentence claims more than the conjunction of the components' results | The product is the meaning VE checks. A reader who identifies "person" across two sentences reads a joint meaning that VE did not check, so the sentence says what was done | an unqualified "the document is consistent" |
| D9 | The UDHR is migrated by a script, not by hand: companions are inlined, and situations are proposed and checked by Lean. A set whose readings declare a name differently is **not migrated** (E1): it stays on W2 with content null and no companions, is listed as "needs one vocabulary", and is not decided | D7's own reason: readings that share no vocabulary cannot be asked "do they differ?". Renaming makes the two declarations two predicates: a query on one never reads the other reading, and separation passes because the other reading's gap is filled "no", so the script's choice would manufacture Lean's certificate (for `rs_u022a`, query 1 of draft 1 would have answered SOME while omitting the `anyone` reading) | renaming inside one set by `_r<k>` (draft 1; review E1); re-translation onto one `bearer` sort (a pilot task, and it would not isolate the language change) |
| D10 | The measure is the **Lean-decided share** (3.9), reported beside the unchanged claimed and audit-verified shares, and beside what qualifies it (E2): the maximum rules per choice document, the decided bytes whose companions were already checked outside the document, and that a one-rule reading is CONFLICT-FREE by construction | "Verified" is ambiguous in this project. Audit-verified bytes come from independent audits, which this plan does not run. Most UDHR readings hold one rule each, and their companions already pass outside the document, so a rise in the share measures routing into Lean, not new assurance | reporting audit-verified bytes as the effect; the share alone |
| D11 | Wiring senses into `ve document` is the next batch (RD-8), not part of these | It does not touch the UDHR (whose units carry JSON content, not English fences). It changes the environment and meaning identities of fenced units, which the Python-owned W2 loader computes, and it needs Lean to render front-matter defaults as preamble lines. Section 6 | folding it into RD-4 |
| D12 | No new Python semantics (lean-first rule 6). Python's generators read Lean's regenerated filled document instead of building `fill` | one owner of `fill` | Python `UnspecifiedDocument` building the generators' input |

## 3. Design

### 3.1 `fill` as a readings document (norms chain)

`NDoc` pairs a readings `Doc` with the frame's unspecified predicates. `fillDoc N` makes three changes:

1. the frame's environment declares `unsaid__p` with `p`'s sorts, for every unspecified `p` (norm-defaults' `E‴`);
2. every norm content whose rule is a root on an unspecified predicate (an empty `over`), whether a fixed unit or a
   reading, gains `over := [unsaid--p']`;
3. after every item, one strict fixed unit per unspecified predicate, in the frame's regulated order, holding
   `F_p` (`fillNode`). Its unit id is its rule name.

When no unit id and no declared name of the document begins `unsaid--` (`fillNamesFree`, which admission's step 2
enforces, 3.2), the `F_p` units use no name a set declares, so they are attached to no set, and the `over` entries
`fill` adds attach no fixed unit to a set. They are in `free`, in every reading's document `one`, in every choice's
document and in `sup`, and they come last, as `fill` puts `fillNodes` last. The hypothesis is needed (review A1):
if a candidate declares the rule name `unsaid--p`, a fixed root rule on `p` gains `over = [unsaid--p]` and becomes
attached to that candidate's set, so `free (fillDoc N)` drops it while `fill (freeU N)` keeps it (fixture F-ND5).
`fill`'s condition for placing a rule under `F_p` reads only that rule's predicate and `over`. S2a's qualification
renames rules but keeps `over`, and its gating changes guards. So the change commutes with `one`, `free`,
`choiceDoc` and `sup`. With every rule strict and no party, `soften` keeps the environment and maps each rule to
its W1 node (`soften_hard_identity`). Hence (RD-1), under `normsShaped N.D` and `fillNamesFree N`:

```text
soften (correlate (one (fillDoc N) s i).1)      = fill (oneU N s i)
soften (correlate (choiceDoc (fillDoc N) c).1)  = fill (choiceU N c)
soften (correlate (sup (fillDoc N)).1)          = fill (supU N)
```

The assertions are unchanged. Every S1 and S2a theorem about `fillDoc N` is therefore a theorem about the filled
documents of norm-defaults 2.3. What the completion adds on top is `Fill_T`. It is a base premise of each reading's
or choice's own document (norm-defaults 2.4), and it is not a premise of W1 or of the soft chain, so this plan adds
it explicitly:

- in separation, as a check on the witness's filling (D4);
- in each choice's checks, through norm-defaults' `BaseAdmissibleU` (the 10a checkers);
- on the superposed route (RD-6), as a premise family of the slot after `Choice_D`, as S2a 4.10 sketched. On `sup`
  it is `fillPremises (supU N)`; under an encoded choice it reads as `fillPremises (choiceU N c)` (`fill_transfers`).

### 3.2 Admission under the completion

The order (RD-2a), stopping at the first error:

1. S1's admission on `N.D` as today: the author's document with placeholder `deny`, S1's texts. On the norms chain
   the abstention no longer applies under `norm-defaults@0`.
2. Reserved names. A unit id, rule name or declared name of the document beginning `unsaid--` is
   `InvalidInput: reserved name <n>` (norm-defaults 2.1's text). Predicate names beginning `unsaid__` are already
   refused by `checkAuthorN`. This step is what makes RD-1's hypothesis `fillNamesFree` hold of every admitted
   document (A1).
3. For `free D`, then every reading with content in set and index order, norm-defaults' author checks on that
   document's UDoc, with `checkAuthorN`'s texts and order. Then `WellFormedU`, refused with
   `InvalidInput: norm-defaults document is not well formed`. A reading's text carries
   ` under <set>@<v>:<i>`, as S1 suffixes chain texts: for example
   `ResourceLimit: rules under rs_1@1:0`.
4. S1's checks on `fillDoc N` (`admissionText`). By RD-1's equalities and `fill_wellFormed`, they can fail only on
   the soft chain's limits for generated formulas, which apply to the filled tree (`checkSoft` 6.11 to 6.15). This
   is *derived*, and fixture F-ND9 in RD-2a checks one such limit. Their texts carry the reading's suffix.

`AdmittedND` carries `WellFormedND N` and `WellFormedDoc (fillDoc N)`. Every later kind starts from it.

### 3.3 Separation under the completion

A situation's base is over the filled frame's author vocabulary, which now includes the unsaid predicates. Their
tables are the filling, shared by both readings. S1's check runs unchanged on `fillDoc N`, and the witness's step 2
also checks the witness's own `Fill_T` on the base. A failure has S1's text,
`distinguishing model violates a generated premise`. `separates_soundU` (RD-1) gives `AchievesU` for the witness
and its negation for the other reading. `achievesU_iff` says what that means in norm-defaults' terms: an admissible
filled situation of the reading's filled document where the probe has the value.

*Derived example* (fixture F-ND1). Take "Every agent must help each user" against "Every agent must help each user
who asks". The base has one agent `a` and one user `u`, and nobody asks. The filling has `help_permitted(a, u)` yes
and `help_required(a, u)` no. The first reading's rule gives `help_required(a, u)` true, and `Fill_T` holds,
because the permission is filled yes where the duty holds. Under the second reading no rule decides, so the filling
answers no. They are separated by the probe `help_required(a, u)` with value true, witnessed by the first reading.

### 3.4 Checking each choice under the completion (enumerated route)

Under `norm-defaults@0` on the norms chain, `routeOf` takes the enumerated route with the finding
`ReadingsNotSuperposable: <sets>` and cause `the unspecified completion`, until RD-6. Its English is E29, "The
readings of … were checked one way at a time, not together." For each compatible choice, at most 64, the evidence is
checked by norm-defaults' own functions on the regenerated `choiceU N c`, with no JSON round trip through the lower
route:

| Inner kind of `readings-choice` | Lean check on `choiceU N c` | Theorem it rests on |
|---|---|---|
| `norm-defaults-conflict` with `packages` | `conflictFreeCheckU` | `conflictFreeCheckU_sound` |
| `norm-defaults-conflict` with a filled `witness` | 10a's witness replay | `normDefaults_wire_witness_sound` (core) |
| `norm-defaults-certificate` (needs `conflict` packages, as S2a 14.8 requires) | `checkCertificate` over `premisesU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ)` | `acceptanceU` (10a's acceptance lemma, moved to UDocs) |
| `choice-model` (a base model with a separate `filling`) | `modelCheckU` | `modelCheckU_sound` |
| `norm-defaults-status`, `norm-defaults-report` | 10a's status replay and report on `choiceU N c` | `normDefaults_wire_status_sound`, `report_sound` (cores) |

The certificates in packages are bound to `E‴_base` of the choice (`baseEnvironmentJsonU`) and to the choice's
document hash (`choiceHash`, as today). Python's generators get the choice's filled document from Lean
(`norm-defaults-elaborate` as an inner kind, 10a's `regeneratedU`). They run the generic prover and model search on
Lean's formulas and never build `fill` (D12).

### 3.5 Verdicts across readings in Lean

`readings-verdicts` (RD-3) takes the case, a question (`conflict`, `premises`, or a query: `conclusion` with
`premises` and optional `assumed`), and evidence keyed by choice. Lean enumerates the compatible choices that take
`assumed` (at most 64; beyond that the answer is W2's budget shape and E28), checks each piece of evidence as in 3.4,
and folds, as composition-s2 4.6 states:

- **Conflict:** CONFLICT when some choice has a checked witness (the witness's choice is named), CONFLICT-FREE when
  every choice's certificates are accepted, UNKNOWN otherwise, naming the first unchecked choice.
- **Query:** first the gate of composition-s2 4.6 as built (14.8; review A2): no entailment verdict unless every
  choice taking `assumed` is CONFLICT-FREE. The fold takes the conflict rows of those choices beside the query rows
  and answers `UNKNOWN (conflict status: <CONFLICT | UNKNOWN>)`, naming the first choice with that status, unless
  `foldConflict` on the conflict rows is CONFLICT-FREE. Past the gate: ALL when every choice is `proved`
  (certificate accepted and CONFLICT-FREE); NONE when every choice is `refuted` (checked countermodel); SOME with at
  least one of each, query rows without a result tolerated; UNKNOWN otherwise, naming the first choice without a
  result. Beyond 64 choices: `UNKNOWN (not ALL: countermodel under <choice>)` when a countermodel was checked, else
  the budget answer. The soundness statements take the conflict rows' hypotheses and also conclude that every
  covered choice is CONFLICT-FREE.
- **Premises:** per document and per reading, S2a 6's `model`, `dead`, `narrowed`, `INCONSISTENT` or `UNKNOWN`,
  from checked models and certificates of ⊥. A choice is INCONSISTENT only when it is also CONFLICT-FREE (4.5's
  table; `Holds.inconsistent` carries `ConflictFreeU`, A2).
- **Conditions:** `restrictions` (the couplings and narrowings in force that exclude some complete choice taking
  `assumed`), computed in Lean by `restrictionsFor`. `conditional_on` is computed by `usedLabels`, Lean's greedy
  replay: each slot or `Fill_T` label's formulas are replaced by `⊤`, in label order, while every certificate the
  answer rests on still checks. This is the rule composition-s2 2.3 "as built" gave Python, now Lean's.
- **English plan:** the list of sentences the answer gets, by composition-s2 2.3, with the readings each names, the
  model it shows and the condition each E3 line states. For a shown model, it also lists which filled gaps the
  result depends on: the model's unsaid atoms in the cone of the conclusion or target (10a's `coneOf`). Python
  renders the frames and the situations; it selects nothing. Each line names its readings by set and index, so the
  `<reading>` slot can show the candidate's own sentence (3.7, A4).

### 3.6 Readings that carry their own vocabulary, and components

**Wire.** A candidate may carry `"companion": {"environment": E, "open_terms": T}`, where `E` is a complete
environment (the companion's) and `T` the companion's open-term declarations (E4; `[]` when it has none). Its
`content` is written over `E`, and its `meaning.open` references name entries of `T`. Its `meaning_id` is computed
by Lean, with the existing identity function, over `E`'s `environment_id` and the canonical content. The recorded
`meaning_id` must equal it (W2's text, `reading meaning id does not match content`).

**The split (Lean, RD-4a).** A set whose readings all carry a companion is a companion set. A set that mixes
readings with and without a companion is refused:
`InvalidInput: reading set <set> mixes readings with and without their own vocabulary`. For each companion set,
Lean builds a component case:

- the environment is the companions' environments merged. Their `language`, `spec_revision` and `profiles` must be
  equal (else `InvalidInput: the readings of <set> declare different <language | spec_revision | profiles>`). Their
  `sorts`, `constants` and `predicates` are united by name, a repeated name only with byte-identical canonical
  declarations (else `InvalidInput: readings <set>@<v>:<i> and <set>@<v>:<j> declare <name> differently`), and
  `readings@1` is added. The merged environment is decoded by the frozen decoders, so every frozen limit applies to
  it;
- the document is the set's unit, the set, the narrowings on the set (they travel with it; A3), and the set's open
  terms: the companions' `open_terms` united by name, a repeated name only with byte-identical entries (else
  `InvalidInput: readings <set>@<v>:<i> and <set>@<v>:<j> declare open term <name> differently`), each validated
  against the merged frame, so conditions that use companion terms are checked in the companion vocabulary (E4).

The main case is the document without the companion sets. It keeps only its own open terms (E4). Their units stay
in it, without a set and without content, so the main component's checks do not read them. Profiles containing
`soft-norms@0` or `rights@0` in a companion are
`UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` (D2). A main
fixed unit that uses a rule name a companion reading declares does not find it in its own component, and the chain
reports `UnknownRule: rule <name>`, its existing text.

**The split contract (review A3, E3).** By the split each companion set is its own component, so a cross-component
coupling is exactly one that names a companion set together with another set. It is refused:
`InvalidInput: coupling <id> links <set> and <set'>, which do not share one vocabulary`. Nothing is dropped or
duplicated: every reading set, coupling and narrowing lands in exactly one case. A companion set's narrowings, and
their restriction labels, travel with it. `restrictionsFor` and `usedLabels` run per component on its own `Doc`, and
the product answer lists each component's `restrictions` and `conditional_on` under it. `--under` naming a set
outside the query's component is refused:
`InvalidInput: --under names <set>, which is not a reading set of the sentence the conclusion is about`. A set left
unseparated stays in the main case as content-less W2 without companions, never a component, and pending W2 sets stay
visible there with W2's UNKNOWN. Each of these has a fixture (RD-4a, RD-4b).

**Meaning.** Components share no symbol, because each is decoded only against its own frame. The document's meaning
is their product: under one compatible choice per component, the document is CONFLICT-FREE when every component's
chosen document is, and a situation is one situation per component (`ConflictFreeK`, `ConsistentK`). The product
fold of RD-4b gives:

- **conflict:** CONFLICT-FREE when every component is, CONFLICT when some component has a witness;
- **premises:** `model` when every component has a model;
- **per reading:** `model` when its component has one under that reading and every other component has a model;
- **a query** is typed against exactly one component's frame. The CLI flag `--sentence <unit>` picks it when the
  terms fit several, and a conclusion with no fitting component is refused. ALL in that component is ALL for the
  document (restriction). NONE and SOME for the document also need every other component to have a model under
  every compatible choice (NONE) or under some choice (SOME); otherwise UNKNOWN, with that reason.

### 3.7 English

New sentences. Each goes through W7's all-derivations gate, and none can be written by an author:

| # | Wording | The one reading | Formal content |
|---|---|---|---|
| E30 | `Under every reading of sentence <n>, <result sentence>` | For every compatible choice of sentence `n`'s component, and every situation of that choice's filled document, the result holds | RD-3's fold on a component with one open set |
| E31 | `Sentence <n> was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.` | Sentence `n` is a component: its frame is its readings' declarations merged, and no verdict combines it with another component | RD-4's split |
| E32 | `Each open sentence below was checked by itself, under each of its readings.` | The lines after it are per-component answers; together they claim the product of 3.6 and nothing more | RD-4b's report |
| R7 | `the text does not say whether <clause>: no rule decides this situation.` | Under the readings named (E12's frame), the point is UNDECIDED: two admissible fillings, checked, give it different values | `norm-defaults-status` on the choice's document. The sentence is norm-defaults 4.2's, after E12's colon |

Reused verbatim (their existing gates apply):

- after a shown `<situation>`, one sentence per filled gap the result depends on:
  `Here the text does not say whether <clause>; this situation answers 'yes'.` (or `'no'`), from norm-defaults 3.2
  and `ve/norm_defaults_english.py:288`;
- as the E3 line for a used `unsaid:pair:<r>,<m>` label, norm-defaults 4.1's pair sentence,
  `Whenever a <noun> must <act>, it may <act>.`;
- for a latent conflict under a reading, R4 followed by norm-defaults 4.2's latent-conflict sentence.

**The reading's own sentence (review A4, in RD-3).** Composition-s2 2.1's `<reading>` slot rule changes: when a
set's candidates differ beyond the deontic verb, `<reading>` is the candidate's own rendered sentence, in italics;
a set whose candidates differ only in the verb keeps the italic verb. "Reading 2" is no longer shown. The change is to
the slot rule itself, so every sentence carrying the slot shows the candidate's sentence: E6, E7 and E9 (conditions),
E12 with its R4 witness line, E17, and the "Under <reading>" sentences. Lean's `Line.readings` already carries set
and index; Python's `reading_names` already renders each candidate's sentence to compare frames. It is a W7 wording
change, DRI-signed in RD-3's DELTA.

Non-wordings: any `unsaid__` or `unsaid--` name, `F_p`, a qualified `rd-` name, a component, a bit or `ve__here`.
The quote marks of the reused filled-gap sentence are existing wording. Whether they meet the zero-training rule is
for norm-defaults' reader test (its 4.3); this plan does not change them, and the new sentences carry none.

*Derived examples* on F-ND1:

- conflict: "Under every reading of the open sentence, no two rules on the same act contradict each other. This
  holds provided that: Whenever an agent must help a user, it may help that user.";
- query "every agent must help each user": "Read sentence 1 as *every agent must help each user*: the conclusion
  follows: …" and "Read sentence 1 as *every agent must help each user who asks that agent*: the conclusion does
  not follow. It fails here: a is an agent; u is a user. Here the text does not say whether a must help u; this
  situation answers 'no'." (the `<reading>` slot as A4 words it; the exact sentences are RD-3's renderer's).

### 3.8 Limits

| Limit | Value | Applies to | Owner |
|---|---|---|---|
| Regulated predicates per environment | 64 | the main frame and each component's merged frame | frozen norms decoder |
| Rules; rules plus unspecified predicates | 256; 256 | every reading's, choice's and superposed document | W1; `checkAuthorN` |
| Unspecified predicate name | 56 bytes | every frame | `checkAuthorN` |
| Precedence height of a rule on an unspecified predicate | 15 | every document | `checkAuthorN` |
| AST nodes, `F_p` guards included | 10,000 | every document | `checkAuthorN`, W1 |
| Sorts; predicates | 32; 256 | every frame (`ve/limits.py`, the environment decoders) | frozen decoders |
| Compatible choices checked one at a time | 64 per component | the enumerated route | `maxChoices` |
| Readings per set | 64 | W2 | today's check |
| Document bytes | 4,000,000 | the file | `ve/document.py` `MAX_DOCUMENT_BYTES` (Python, until lean-first batch 17) |
| Pilot document load | 120 s wall | `ve document load` and `check` of the UDHR | lean-first section 4 budget |

### 3.9 The measure: Lean-decided share

A unit is **Lean-decided** when every verdict VE reports about its formal content was produced by a Lean answer and
is not UNKNOWN:

- a fixed unit with content: its component's conflict status (CONFLICT-FREE or CONFLICT) and premise status
  (`model` or `INCONSISTENT`) are decided;
- the unit of an open set: its component's conflict status under every reading is decided, and every reading's
  premise status is `model`, `INCONSISTENT`, `dead` or `narrowed`;
- labelled and unformalised units are never Lean-decided (they have no formal content).

Lean's answer (`readings-verdicts` with components, RD-4b) lists the decided unit ids. The measuring script
(`tools/lean_decided_share.py`, RD-5) sums those units' span bytes, using the spans the report's coverage block
already uses. It decides nothing itself.

**Before.** The rule applied to the recorded report of run 20261006T1800Z gives 0 bytes, *derived*: the document's
premises are UNKNOWN and it has no readings block, so no unit qualifies. RD-5 recomputes the figure with the script,
at the batch's commit, on the committed run. **After:** measured on the migrated run, at the same commit. The upper
bound the rule allows is the CHECKED and READINGS bytes, 57 + 4,200 = 4,257 (39.00%), arithmetic and not a
prediction. Claimed coverage (43.90%) and audit-verified coverage (23.30%) are reported unchanged beside it. The
pilot's own per-companion checks, run outside the document, are reported separately as context.

**What qualifies the share (review E2).** Beside the share the report gives: the maximum number of rules in any
choice's document; the decided bytes whose companions were already checked outside the document (the pilot's
per-companion checks); and the sentence that a reading holding one rule is CONFLICT-FREE by construction (a single
rule cannot contradict another). Most UDHR companions hold one rule each, so the move from 0 measures routing those
checks into Lean inside the document, not new assurance; section 5 says so.

### 3.10 One owner per piece of logic

| Logic | Owner | Python |
|---|---|---|
| `fill`, `E‴`, `Fill_T`, author limits | Lean `VE.NormDefaults` (10a), applied to readings by `fillDoc` | none (D12) |
| Admission under the completion, its order and texts | Lean `admitND` | relays the text |
| Separation, with the witness's `Fill_T` | Lean (`separates` on `fillDoc N`, `fillHolds`) | proposes situations (the retained S1 search) over Lean's filled document |
| Each choice's checks | Lean 10a checkers on `choiceU N c` | proposes certificates, models and fillings (generic prover and search over Lean's formulas) |
| Fold, conditions, restrictions, labels used, wording selection | Lean `readings-verdicts` | renders sentences from Lean's plan |
| Companion merge (environments and open terms), components, the split contract, their meaning ids, the product fold | Lean | passes `companion` through W2's structural validation unread |
| Decided units | Lean | sums span bytes (W2 coverage arithmetic) |
| Files, CLI, rendering, the UDHR migration | Python, and pilot tooling under `usecases/` | — |

### 3.11 Conservativity

- `readings@1` or `norm-defaults@0` off, or on the soft or rights chain: nothing here is reachable, and every
  answer, identity and text is byte-identical. K18 keeps its abstention.
- A document whose sets have no content keeps W2's route (S1 4.9), so the committed UDHR and constitution runs
  answer as today.
- `fill` without unspecified predicates is the identity (`fill_conservative`), so `fillDoc` is the identity there
  (`fillDoc_conservative`, RD-1).
- No frozen file, canonical byte, existing identity or approved theorem statement changes. New statements go in new
  files. Definitions that change (`abstention`, `routeOf`, the inner kinds of `readings-choice`) change no
  statement.

## 4. Batches

Every batch: 2 to 6 hours for one builder, from the build checklist, with the lean-first gate of LEAN-FIRST-PLAN 5.1
(full suite in chunks; corpus A/B over the probe matrix, the conformance and readings corpora and every historical
pilot document, changes listed in `DELTA.md` by class; deletion ledger; latency within section 4's budgets). Each
batch also runs the audit, the frozen-inventory and assurance-manifest updates, trust classes, gate collection and
`tools/lean_statements.py` (additions only), and the relay lint. Statement review before Lean build (PLAN-EXPAND2
rule 10): RD-0 reviews every statement below, and a batch whose statement changes during the build reopens only that
statement.

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| RD-0 | Statement spec `docs/spec/readings-defaults.md`, the stub elaborated against the merged build, statement review (Astra and Fable, converged; PASS only when both accept every statement as true under its hypotheses) | 3–4 | planner | — |
| RD-1 | `fillDoc`, its four equalities, separation under the completion (theory) | 5–6 | Lean | RD-0 |
| RD-2a | Admission, separation and per-choice checks under the completion (wire) | 5–6 | Lean | RD-1 |
| RD-2b | Relay and generators under the completion; fixtures through `ve document` | 4–5 | Python | RD-2a |
| RD-3 | `readings-verdicts` on the enumerated route: the fold, conditions, English plan; Python's fold deleted | 5–6 | Lean, Python | RD-2b |
| RD-4a | Readings with their own vocabulary: merge, split, meaning ids (wire) | 5–6 | Lean | RD-2a |
| RD-4b | Components in the verdicts and the report: product fold, `--sentence`, pass-through | 4–5 | Lean, Python | RD-3, RD-4a |
| RD-5 | The UDHR: migration, situations, loading within limits, Lean-decided share before and after | 4–6 | pilot tooling, measurement | RD-4b |
| RD-6a | S2a with a carried base-premise family (generalized statements, old ones as instances) | 5–6 | Lean | RD-1 |
| RD-6b | Superposition under the completion: `fill_transfers`, route, wire, generators | 5–6 | Lean, Python | RD-6a, RD-3 |
| RD-7 | `readings-verdicts` on the superposed route; Python's superposed fold and wording selection deleted | 5–6 | Lean, Python | RD-3 |
| RD-8 | Senses in `ve document` (next batch, section 6) | 4–6 | Lean, Python | none of these |
| RD-9 | Soft chain under the completion (the constitution's strict and default readings): design batch | 3 | planner | RD-6b |

**The pilot path (converged review):** RD-0 PASS → RD-1 → RD-2a → RD-2b → RD-3 → RD-4a → RD-4b → RD-5, about 35
to 44 builder hours by these estimates (estimates, not evidence of buildability or speed). RD-4a needs only RD-2a,
its declared dependency, so it may run beside RD-2b and RD-3; RD-4b waits for both RD-3 and RD-4a. RD-6a, RD-6b,
RD-7, RD-8 and RD-9 are off the pilot path; their statements are re-reviewed before their own build. (The reviewers'
round-3 texts crossed on RD-4a's earliest start, "after RD-0" and "after RD-2a"; this draft keeps the table's
declared dependency, which Astra's text names, since F-C1 needs RD-2a's admission.)

### RD-0. Statement spec and review (planner, 3–4 h)

- `docs/spec/readings-defaults.md`: sections 3.1 to 3.8 written as a statement spec, in the form of the S2a spec
  (definitions, English with one reading each, wire, diagnostics in order, Lean statements, fixtures, limits,
  review checklist), with the blocks of RD-1 to RD-6 verbatim.
- `lean/SpecStubs_readings_defaults.lean`, untracked: every definition with the bodies given here, and every
  statement as a `def … : Prop`. Elaborated with `lake env lean` against a build of `main` (or
  `lake --dir <worktree with the build>/lean env lean <stub>`). Every elaboration failure is fixed in the spec, not
  in the merged code.
- Statement review (Astra and Fable, converged). RD-1 opens on a PASS. PASS requires both reviewers to accept each
  statement as true under its hypotheses, F-ND5 included; that the stub elaborates is not enough (review). RD-6's
  `Q' c` condition is stated in the spec, off the pilot path.
- The corrections of the converged review (E1 to E5, A1 to A4) are in the spec before PASS; the draft-1 statements
  are not implemented verbatim.
- Done when the stub elaborates, the spec is committed, and the review has converged.

### RD-1. `fillDoc` and separation under the completion (Lean, 5–6 h)

Files: `lean/VE/Readings/Unspecified.lean` (new), `lean/VE/Readings/UnspecifiedExamples.lean` (new, `#guard`s),
`lean/READINGS.md` (a section). Nothing frozen changes.

```lean
import VE.Readings.SupWireSound
import VE.NormDefaults.Layered

namespace VE.Readings
open VE.Norms (Regulated Sat envAt size restrictAll DocumentExpansion)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u

/-- A readings document and its frame's `unspecified` predicates (norm-defaults 2.1), read from the environment
    before DRI ruling 4's placeholder `deny` replaced them. -/
structure NDoc where
  D : Doc
  unspec : List String

/-- A document of the route as a norm-defaults document (norm-defaults 7's `UDoc`). -/
def asU (N : NDoc) (X : RightsDoc) : VE.NormDefaults.UDoc := ⟨soften (correlate X), N.unspec⟩
def freeU (N : NDoc) : VE.NormDefaults.UDoc := asU N (free N.D).1
def oneU (N : NDoc) (s : String) (i : Nat) : VE.NormDefaults.UDoc := asU N (one N.D s i).1
def choiceU (N : NDoc) (c : Choice) : VE.NormDefaults.UDoc := asU N (choiceDoc N.D c).1
def supU (N : NDoc) : VE.NormDefaults.UDoc := asU N (sup N.D).1

/-- What the norms chain's decoder guarantees: the frame has no rule and no rights block, and every content is an
    assertion or a strict rule with no party, no exception and no `hard` flag. -/
def strictRule (M : SoftNode) : Bool :=
  M.mode == .strict && M.alterable.isEmpty && M.exception.isNone && !M.hard
def contentStrict : Content → Bool
  | .assertion _ => true
  | .norm M => strictRule M
  | _ => false
def normsShaped (D : Doc) : Bool :=
  D.chain == .norms && D.frame.soft.T.nodes.isEmpty && noRights D.frame &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => contentStrict c
    | .bar _ _ => false
    | .set R => R.candidates.all (fun a => (a.content.map contentStrict).getD true))

/-! ## `fill` on the readings document (norm-defaults 2.3; 3.1 of the plan) -/

/-- `fillRoot` on a readings content: a root rule on an unspecified predicate is placed under its `F_p`. -/
def fillSoftNode (N : NDoc) (M : SoftNode) : SoftNode :=
  if M.pred ∈ N.unspec ∧ M.over = [] then { M with over := [VE.NormDefaults.fillName M.pred] } else M
def fillContent (N : NDoc) : Content → Content
  | .norm M => .norm (fillSoftNode N M)
  | c => c
def fillItem (N : NDoc) : Item → Item
  | .fixed u c cs => .fixed u (fillContent N c) cs
  | .bar u b => .bar u b
  | .set R => .set { R with candidates := R.candidates.map (fun a => { a with content := a.content.map (fillContent N) }) }
/-- A W1 node as a strict readings rule. -/
def strictNodeOf (M : VE.Norms.Node) : SoftNode :=
  { toNode := M, mode := .strict, rank := none, alterable := [], exception := none, hard := false }
/-- `F_p` for every unspecified predicate, in the frame's regulated order, each a fixed unit named by its rule. -/
def fillUnits (N : NDoc) : List Item :=
  (N.D.frame.soft.T.regulated.filter (fun r => r.name ∈ N.unspec)).map (fun r =>
    .fixed (VE.NormDefaults.fillName r.name) (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [])
/-- `E‴` on the frame: every `unsaid__p` a base predicate with `p`'s sorts (norm-defaults' `fillEnv`). -/
def fillFrameEnv (N : NDoc) : VE.Environment :=
  { N.D.frame.soft.E with predicates := fun n =>
      match N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) with
      | some p => some (VE.SoftNorms.sortsOf N.D.frame.soft p)
      | none => N.D.frame.soft.E.predicates n }
def fillDoc (N : NDoc) : Doc :=
  { N.D with frame := { N.D.frame with soft := { N.D.frame.soft with E := fillFrameEnv N } },
             items := N.D.items.map (fillItem N) ++ fillUnits N }

/-- No unit id and no declared name begins `unsaid--` (the names `fill` adds are free; 3.2 step 2). -/
def fillNamesFree (N : NDoc) : Bool :=
  N.D.items.all (fun it => !(itemUnit it).startsWith "unsaid--" && it.names.all (fun n => !n.startsWith "unsaid--")) &&
    N.D.sets.all (fun R => (declaredBy R).all (fun n => !n.2.startsWith "unsaid--"))

/-- Taking a reading's, the free, a choice's or the superposed document commutes with `fill` (3.1). Each needs
    `fillNamesFree` (review A1; fixture F-ND5 fails without it). -/
theorem fillDoc_one (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String) (i : Nat) :
    soften (correlate (one (fillDoc N) s i).1) = VE.NormDefaults.fill (oneU N s i) ∧
      (one (fillDoc N) s i).2 = (one N.D s i).2
theorem fillDoc_free (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) :
    soften (correlate (free (fillDoc N)).1) = VE.NormDefaults.fill (freeU N) ∧ (free (fillDoc N)).2 = (free N.D).2
theorem fillDoc_choice (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (c : Choice) :
    soften (correlate (choiceDoc (fillDoc N) c).1) = VE.NormDefaults.fill (choiceU N c) ∧
      (choiceDoc (fillDoc N) c).2 = (choiceDoc N.D c).2
theorem fillDoc_sup (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) :
    soften (correlate (sup (fillDoc N)).1) = VE.NormDefaults.fill (supU N) ∧ (sup (fillDoc N)).2 = (sup N.D).2
/-- The open sets, their candidates, labels, couplings and narrowings are untouched. -/
theorem compatible_fillDoc (N : NDoc) (c : Choice) : Compatible (fillDoc N) c ↔ Compatible N.D c
theorem attached_fillDoc (N : NDoc) (hf : fillNamesFree N = true) (u : String) (hu : u ∈ fixedNames N.D) :
    attached (fillDoc N) u = attached N.D u
theorem fillDoc_conservative (N : NDoc) (h0 : N.unspec = []) : fillDoc N = N.D

/-! ## Admission's facts (3.2) -/

def unspecDeclared (N : NDoc) : Bool :=
  decide N.unspec.Nodup &&
    N.unspec.all (fun p => N.D.frame.soft.T.regulated.any (fun r => r.name == p && !r.allowByDefault))
def WellFormedND (N : NDoc) : Bool :=
  WellFormedDoc N.D && normsShaped N.D && unspecDeclared N && fillNamesFree N &&
  VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))

/-! ## Separation under the completion (3.3) -/

/-- A reading achieves a probe value under the completion: S1's `Achieves` on the filled document, the filling
    respecting `Fill_T` of that reading's own document (norm-defaults 2.4). -/
def AchievesU (N : NDoc) (s : String) (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier)
    (q : Probe B.Carrier) (v : Bool) : Prop :=
  Achieves (fillDoc N) s i B F q v ∧ Sat B (VE.NormDefaults.fillPremises (oneU N s i))
def SeparatedU (N : NDoc) (s : String) (i j : Nat) : Prop :=
  ∃ (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool),
    (AchievesU N s i B F q v ∧ ¬ AchievesU N s j B F q v) ∨ (AchievesU N s j B F q v ∧ ¬ AchievesU N s i B F q v)
/-- The witness's step 2 under the completion: its `Fill_T` holds on the situation's base. -/
def fillHolds {α : Type u} [DecidableEq α] (N : NDoc) (s : String) (i : Nat) (M : VE.FiniteModel α) : Bool :=
  (VE.NormDefaults.fillPremises (oneU N s i)).all (fun φ => φ.eval M [])

theorem separates_soundU {α : Type u} [DecidableEq α] (N : NDoc) (hF : WellFormedDoc (fillDoc N) = true)
    (s : String) (i j : Nat) (hi : (candidate (fillDoc N) s i).bind (·.content) ≠ none)
    (hj : (candidate (fillDoc N) s j).bind (·.content) ≠ none) (σ : Situation α)
    (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separates (fillDoc N) s i j σ = true)
    (hf : fillHolds N s i σ.base = true) :
    AchievesU N s i σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value ∧
      ¬ AchievesU N s j σ.base.asStructure (tablesOf σ.fixed) σ.probe σ.value
theorem separates_separatedU {α : Type u} [DecidableEq α] (N : NDoc) (hF : WellFormedDoc (fillDoc N) = true)
    (s : String) (i j : Nat) (hi : (candidate (fillDoc N) s i).bind (·.content) ≠ none)
    (hj : (candidate (fillDoc N) s j).bind (·.content) ≠ none) (σ : Situation α)
    (valid : σ.base.Valid (authorEnv (fillDoc N))) (h : separates (fillDoc N) s i j σ = true)
    (hf : fillHolds N s i σ.base = true) : SeparatedU.{u} N s i j
/-- On the norms chain no key is generated: `AchievesU` is an admissible filled situation of the reading's filled
    document (norm-defaults' `BaseAdmissibleU`) where the probe has the value. -/
theorem achievesU_iff (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String)
    (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool) :
    AchievesU N s i B F q v ↔
      B.Admissible (authorEnv (fillDoc N)) ∧ VE.NormDefaults.BaseAdmissibleU (oneU N s i) B ∧
        Observes (one (fillDoc N) s i).1 (one (fillDoc N) s i).2 B q v
end VE.Readings
```

Proof notes. The four equalities follow from one lemma about `build` (`build_fillDoc`: building with any `keep` and
any `pick` that are the same on `N.D` and on `fillDoc N` gives the filled document) and one about `sup`'s fold
(`sup_fillDoc`). `soften_hard_identity` carries them across `soften` (its `WellFormedSoft` hypothesis is unused in
its proof; the lemma needed is `envPrime_of_no_decisions` with the strict rules), and `correlate_noRights` across
`correlate`. Environments are equal by `funext` on `predicates`: `choiceEnv` overrides `ve__` names and the fill
override `unsaid__` names, so the two overrides commute. `separates_soundU` is `separates_sound` on `fillDoc N` plus
`hf`; `achievesU_iff` uses `fillDoc_one` and the empty `genKeys` of a strict document. `build_fillDoc` needs
`fillNamesFree`: it is what keeps `attached` unchanged (`attached_fillDoc`), hence `keep` the same on both documents,
and keeps `copies` from expanding an added `unsaid--` entry in `sup` (review A1).

Fixtures (`UnspecifiedExamples.lean`, `#guard`; draft 1's values were *derived*, the spec computes them):

- **F-ND1.** Environment `E1`: sorts `agent`, `user`; base predicate `asks(user, agent)`; `help_required(agent,
  user)` an obligation, `unspecified`, act `{0} help {1}`, permission `help_permitted`; `help_permitted(agent, user)`
  a permission, `unspecified`, the same act. Set `rs_1`, unit `u1`: reading 0 is `must-help`, strict, sign +, guard
  ⊤; reading 1 is `must-help`, guard `asks(user, agent)`.
  - `fillDoc` has two `F_p` units, `unsaid--help-required` and `unsaid--help-permitted`, last. Both readings' rules
    gain `over := [unsaid--help-required]`.
  - `fillDoc_one` holds by `decide` on the instance.
  - The situation of 3.3 (one agent, one user, empty `asks`, filling `help_permitted(a, u)` yes, `help_required`
    empty) separates with witness 0, and `fillHolds` is true.
  - The same base with `help_permitted` empty has `fillHolds` false (witness 0 breaks `Fill_T`).
- **F-ND5 (collision, review A1).** F-ND1's frame, a fixed unit `u0` with the root rule `be-helpful` on
  `help_required`, and a set whose reading declares a rule named `unsaid--help-required`. `fillNamesFree` is false;
  `u0` is attached to no set in the document and to `rs_1` in `fillDoc`, so `free (fillDoc N)` drops `be-helpful`
  while `fill (freeU N)` keeps it: `fillDoc_free` fails without its hypothesis. Admission refuses the document at 3.2
  step 2 (RD-2a's F-ND5).
- **F-ND0.** With `unspec = []`, `fillDoc N = N.D` on K1's norms-chain twin (`fillDoc_conservative`).

Deleted, not duplicated: nothing deleted. No second `fill`: `fillDoc` calls `fillName`, `fillNode` and `unsaidName`
and restates only `fillRoot`'s condition, on readings contents, with its equality proved.

Done when: the file builds with no `sorry` and standard axioms only, the fixtures `#guard`, `lean/READINGS.md`
lists every theorem in plain words, and the gate passes (no answer can change, since nothing calls the new file).

### RD-2a. Admission, separation and choices under the completion (Lean wire, 5–6 h)

Files: `lean/VE/Readings/UnspecifiedWire.lean` (new). Changes to definitions only: `Readings/Wire.lean`
(`abstention`), `Readings/Route.lean` (`routeOf`'s row), `Readings/SupRun.lean` (`readings-choice`'s inner kinds
under the profile). In `VE.NormDefaults`, the cores of three wire theorems move to UDoc-level lemmas placed beside
them (`EntailsU` and `acceptanceU` in `NormDefaults/Wire.lean`, which defines `premisesU`; `modelCheckU` in
`NormDefaults/Report.lean`, beside `admissibleX_of_fill`), and the wire theorems keep their statements. The block
below shows them in one namespace for reading; RD-0 places each in its file.

```lean
namespace VE.NormDefaults
open VE.Norms
universe u

/-- Entailment on a filled document: the conclusion of `normDefaults_wire_acceptance`, named. -/
def EntailsU (U : UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, BaseAdmissibleU U (restrictAll (fill U).T S) →
    DocumentExpansion (fill U) (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []
/-- `normDefaults_wire_acceptance`'s core on any well-formed UDoc (its proof moves here; its statement is kept). -/
theorem acceptanceU (U : UDoc) (h : WellFormedU U = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesU U Γ) φ cert = true) :
    EntailsU.{u} U Γ φ
/-- A finite base model with a separate filling: the base background, `Fill_T`, and each premise read through the
    outcome substitution of `fill U`; the second component is the conclusion's value. -/
def modelCheckU {α : Type u} [DecidableEq α] (U : UDoc) (M : VE.FiniteModel α) (F : FiniteFill U α)
    (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  (backgroundValid U.D M && fillValid U M F &&
     Γ.all (fun a => (subst (fill U).T (size (fill U)) a).eval (M.withFill F) []),
   (subst (fill U).T (size (fill U)) φ).eval (M.withFill F) [])
theorem modelCheckU_sound {α : Type u} [DecidableEq α] (U : UDoc) (h : WellFormedU U = true)
    (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0)) (F : FiniteFill U α) (Γ : List VE.Formula)
    (φ : VE.Formula) (hm : (modelCheckU U M F Γ φ).1 = true) :
    BaseAdmissibleU U (withFill U M.asStructure (finFill M F)) ∧
    (∀ a ∈ Γ, (subst (fill U).T (size (fill U)) a).denote (withFill U M.asStructure (finFill M F)) []) ∧
    ((subst (fill U).T (size (fill U)) φ).denote (withFill U M.asStructure (finFill M F)) [] ↔
      (modelCheckU U M F Γ φ).2 = true)
end VE.NormDefaults

namespace VE.Readings.Wire
open Lean

/-- The frame's unspecified predicates, from the environment the frame was decoded from. -/
def unspecOf (re : ReadingsEnvironment) (D : Doc) : List String :=
  (D.frame.soft.T.regulated.map (·.name)).filter ((VE.NormDefaults.Wire.unspecifiedNames re.lowerJson).contains ·)
/-- 3.2 steps 2 and 3: reserved names, then norm-defaults' author checks and `WellFormedU` on `free D` and on each
    reading's document with content, in admission order, a reading's text suffixed ` under <set>@<v>:<i>`. -/
def ndText (re : ReadingsEnvironment) (N : NDoc) : Option String

structure AdmittedND where
  b : Admitted2
  N : NDoc
  hN : N.D = b.D
  wfU : WellFormedND N = true
  wfF : WellFormedDoc (fillDoc N) = true

/-- 3.2: S1's and S2a's admission as today; then, under `norm-defaults@0` on the norms chain, `ndText`; then S1's
    checks of the filled document (`admissionText re (fillDoc N)`), each reading's document built once. -/
def admitND (environment document : Json) : Except String AdmittedND

/-- A replayed separation under the completion: the admitted document, the pair, the situation over the filled
    frame's author vocabulary. -/
structure SeparateReplayU where
  r : AdmittedND
  set : String
  witness : Nat
  other : Nat
  hw : (candidate (fillDoc r.N) set witness).bind (·.content) ≠ none
  ho : (candidate (fillDoc r.N) set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (authorEnv (fillDoc r.N))
def replaySeparateU (j : Json) : Except String SeparateReplayU

theorem readings_wire_nd_separate_sound (j : Json) (x : SeparateReplayU) (h : replaySeparateU j = .ok x)
    (hs : separates (fillDoc x.r.N) x.set x.witness x.other x.σ = true)
    (hf : fillHolds x.r.N x.set x.witness x.σ.base = true) :
    AchievesU x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
      ¬ AchievesU x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value

/-- A choice's replay under the completion: a compatible choice of the admitted document and its decoded
    evidence. -/
structure ChoiceReplayU where
  r : AdmittedND
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  certs : List (Option VE.Tableau.Certificate)
def replayChoiceU (j : Json) : Except String ChoiceReplayU

theorem readings_wire_nd_choice_conflict (j : Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (hv : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
    Compatible x.r.N.D x.c ∧ VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c)
theorem readings_wire_nd_choice_entails (j : Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill (choiceU x.r.N x.c))
            (size (VE.NormDefaults.fill (choiceU x.r.N x.c))))
            (VE.NormDefaults.Wire.premisesU (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ)) φ cert = true)
    (hcf : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
    VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ) φ
end VE.Readings.Wire
```

Wire answers:

- `readings-validate` and `readings-separate` under the profile on the norms chain answer S1's rows, computed on
  `fillDoc N`, with two additions: per reading `fill_premises` (label `unsaid:pair:<r>,<m>`, AST), and once
  `filled` (`environment`: the lower environment with each `unspecified` read as `deny`, `norm-defaults@0` removed
  and every `unsaid__p` added as in 10a's `withUnsaid`; `units`: the filled contents and the `F_p` units). Python's
  search and English read `filled`.
- `readings-elaborate`: the enumerated row with `finding` `{"text": "ReadingsNotSuperposable: <every open set>",
  "cause": "the unspecified completion"}`; `enumeratedCheckText` also runs `ndText`'s checks on each enumerated
  choice's UDoc.
- `readings-choice` with the inner kinds of 3.4, answered on `choiceU N c` with the norm-defaults route's answer
  shapes (`ResponseShape` encoders reused; new rows get `*_fits` theorems).

Fixtures (`tests/test_readings_nd_lean.py` through the service; expected values *derived*):

| # | Case | Expected |
|---|---|---|
| F-ND1 | 3.3's document, `readings-validate` | admitted; pair (0, 1) separated with witness 0; `fill_premises` lists `unsaid:pair:help_required,help_permitted` for both readings. Before this batch: the abstention text |
| F-ND1′ | F-ND1 with the witness filling's `help_permitted` empty | `distinguishing model violates a generated premise` |
| F-ND2 | norm-defaults' u6 as readings. Fixed `no-x`, "Every agent must not X." (`x_permitted`, sign −). Set `rs_2`: reading 0 "Every agent must X, if that agent may Y." (`x_required`, guard `y_permitted(agent)`); reading 1 "Every agent may Y." (`y_permitted`, sign +). All completions `unspecified` | admitted. Choice 0 has a filled witness (`y_permitted(a)` yes) with verdict CONFLICT at the pair target of `(x_required, x_permitted)`, a latent conflict. Choice 1 is CONFLICT-FREE (packages); `x_required(a)` is SETTLED no (`norm-defaults-status`, `table3`). Pair (1, 0) is separated by probe `y_permitted(a)`, value true, witness 1, filling empty |
| F-ND3 | 7 sets of 2 readings, each as F-ND1 | `readings-elaborate`: enumerated, `choice_count: "over 64"`, `choices_checked: "over 64"` |
| F-ND4 | 252 fixed rules on `p` (`unspecified`, 4 unspecified predicates in the frame), one set with one rule on `p` | `ResourceLimit: rules under rs_1@1:0` (free has 252 + 4; the reading's document 253 + 4) |
| F-ND5 | RD-1's collision document: a fixed root rule on `help_required` and a reading's rule named `unsaid--help-required` | `InvalidInput: reserved name unsaid--help-required` (3.2 step 2, before any document's check, so no suffix) |
| F-ND6 | K18 (the soft chain under the profile) | the abstention text, unchanged |
| F-ND7 | every S1 fixture K1 to K22 and S2a fixture M1 to M20 | byte-identical answers |
| F-ND8 | tampering: a package bound to choice 0's document replayed for choice 1; a filling with an ill-typed tuple; `unsaid__` table supplied as a base table outside the profile | refused or UNKNOWN, never CONFLICT-FREE, `proved` or `model` |
| F-ND9 | a reading whose rule's guard is large enough that the filled tree's generated layer for its predicate passes `checkAuthorN`'s 10,000-node author budget but not the soft chain's limit for one generated layer (built by the test, sized from `generatedSizes`) | `ResourceLimit: generated norm layer layer:norms:<p> under rs_1@1:0` (3.2 step 4) |

Deleted, not duplicated: none deleted. The three 10a wire theorems now call the UDoc lemmas, so their proofs exist
once. No readings function evaluates `Fill_T` except `fillHolds`.

Done when: the fixtures pass in Lean and through the service, the corpus A/B lists only `availability` changes for
documents that reached the abstention on the norms chain (expected none in the corpora, *derived*: the
constitution's documents are on the soft chain), the DRI signs any listed change, and the gate passes.

### RD-2b. Relay and generators under the completion (Python, 4–5 h)

- `ve/readings_route.py`: send the environment unchanged; read `filled`, `fill_premises` and the inner kinds'
  answers; raise Lean's texts verbatim.
- `ve/readings_s1.py`: under the profile, build the documents for English and search from Lean's `filled`, not from
  the environment. Delete `_placeholder_frame` if the corpus A/B shows no other caller (the ledger records it).
- `ve/readings_verdicts.py` (`Enumerated`, `_ChoiceDocument`): for each compatible choice, ask Lean for the
  choice's `norm-defaults-elaborate` row, then run `entailment.prove_entailment` and `search.find_countermodel` over
  its `base_environment`, background, `fill` premises and targets. Send each certificate, witness and filled model
  back as evidence. No Python `UnspecifiedDocument` is built for a readings document.
- The S1 search's witness filter evaluates Lean's `fill_premises` (the evaluator is the retained, generator-internal
  duplicate of lean-first rule 3, unchanged).
- `tools/relay_lint.py` gains a rule: no `unsaid__` or `unsaid--` literal in `ve/readings*.py`.

Fixtures: F-ND1 and F-ND2 through `ve document load`, `check`, `render` and `readings --conclusion` (the queries of
RD-3's table, with the Python fold still in place), and a generator run on F-ND1 that finds the 3.3 situation.

Deleted, not duplicated: Python builds no `fill`; `_placeholder_frame` goes if unused (ledger).

Done when: the CLI fixtures pass, the relay lint passes, the gate passes, and the A/B lists no change outside
documents under the profile.

### RD-3. Verdicts across readings in Lean, enumerated route (Lean and Python, 5–6 h)

Files: `lean/VE/Readings/Verdicts.lean` (new), the kind `readings-verdicts` in `Readings/Run.lean`, its response
shape. Python: `ve/readings_verdicts.py` keeps only evidence generation and the relay.

```lean
namespace VE.Readings
universe u

inductive ChoiceResult | proved | refuted | free | conflict | model | inconsistent | unknown
  deriving DecidableEq, Repr
inductive ReadingVerdict | all | some | none | unknown
  deriving DecidableEq, Repr

def foldConflict (rs : List (Choice × ChoiceResult)) : ChoiceResult :=
  if rs.any (·.2 == .conflict) then .conflict
  else if !rs.isEmpty && rs.all (·.2 == .free) then .free else .unknown
/-- composition-s2 4.6 over the checked choices, with its gate (14.8; review A2): `conflicts` are the conflict rows
    of the same choices, and no entailment verdict is given unless `foldConflict conflicts` is CONFLICT-FREE. -/
def foldEntailment (conflicts rs : List (Choice × ChoiceResult)) : ReadingVerdict :=
  if foldConflict conflicts != .free then .unknown
  else if rs.isEmpty then .unknown
  else if rs.all (·.2 == .proved) then .all
  else if rs.all (·.2 == .refuted) then .none
  else if rs.any (·.2 == .proved) && rs.any (·.2 == .refuted) then .some
  else .unknown

/-- A situation of a reading's filled document where the premises hold and the conclusion fails. -/
def CounterU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (VE.Norms.restrictAll (VE.NormDefaults.fill U).T S) ∧
    VE.Norms.DocumentExpansion (VE.NormDefaults.fill U) (VE.Norms.restrictAll (VE.NormDefaults.fill U).T S) S ∧
    VE.Norms.Sat S Γ ∧ ¬ φ.denote S []
/-- What a checked result says of its choice; RD-2a's theorems establish it for every result Lean records. -/
def Holds (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) : ChoiceResult → Prop
  | .proved => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .refuted => CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .free => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
  | .conflict => ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
  | .model => ∃ S : VE.Structure.{0},
      VE.NormDefaults.BaseAdmissibleU (choiceU N c) (VE.Norms.restrictAll (VE.NormDefaults.fill (choiceU N c)).T S) ∧
      VE.Norms.DocumentExpansion (VE.NormDefaults.fill (choiceU N c))
        (VE.Norms.restrictAll (VE.NormDefaults.fill (choiceU N c)).T S) S ∧ VE.Norms.Sat S (choiceDoc N.D c).2
  | .inconsistent => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU N c) (choiceDoc N.D c).2 .bottom   -- 4.5's table (review A2)
  | .unknown => True
/-- The rows are exactly the compatible choices taking `A`. -/
def Covers (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) : Prop :=
  ∀ c, (Compatible N.D c ∧ ∀ x ∈ A, x ∈ c) ↔ c ∈ rs.map (·.1)

/-- Each takes the conflict rows `cs` beside the query rows `rs` and also concludes that every covered choice is
    CONFLICT-FREE (review A2). -/
theorem fold_all_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hcc : Covers N A cs) (hc : Covers N A rs)
    (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hr : ∀ x ∈ rs, Holds.{u} N Γ φ x.1 x.2)
    (h : foldEntailment cs rs = .all) :
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
theorem fold_none_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hcc : Covers N A cs) (hc : Covers N A rs)
    (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hr : ∀ x ∈ rs, Holds.{u} N Γ φ x.1 x.2)
    (h : foldEntailment cs rs = .none) :
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
theorem fold_some_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hcc : Covers N A cs) (hc : Covers N A rs)
    (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hr : ∀ x ∈ rs, Holds.{u} N Γ φ x.1 x.2)
    (h : foldEntailment cs rs = .some) :
    (∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)) ∧
    (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧
       VE.NormDefaults.EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
    (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ)
theorem fold_conflict_free_sound (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) (hc : Covers N A rs)
    (hr : ∀ x ∈ rs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict rs = .free) :
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
theorem fold_conflict_sound (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) (hc : Covers N A rs)
    (hr : ∀ x ∈ rs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict rs = .conflict) :
    ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)

/-! ## Conditions -/

/-- The couplings and narrowings in force that exclude some complete choice taking `A` (composition-s2 4.6). -/
def restrictionsFor (D : Doc) (A : Choice) : List String
theorem restrictionsFor_spec (D : Doc) (A : Choice) (l : String) :
    l ∈ restrictionsFor D A ↔ ∃ c, complete D c = true ∧ (∀ x ∈ A, x ∈ c) ∧ excludedBy D l c = true
/-- `L` with the formulas of every label outside `keep` replaced by `⊤`. -/
def blank (L : VE.Compose.Labelled) (keep : List String) : List VE.Formula :=
  L.map (fun x => if keep.contains x.1 then x.2 else .top)
/-- Greedy, in label order: a label is dropped when every check still passes without it. -/
def usedLabels (check : List VE.Formula → Bool) (pre : List VE.Formula) (L : VE.Compose.Labelled)
    (post : List VE.Formula) : List String :=
  (L.map (·.1)).foldl (fun keep l =>
    if check (pre ++ blank L (keep.erase l) ++ post) then keep.erase l else keep) (L.map (·.1))
theorem usedLabels_sound (check : List VE.Formula → Bool) (pre : List VE.Formula) (L : VE.Compose.Labelled)
    (post : List VE.Formula) (hl : L.wellLabelled = true) (h : check (pre ++ L.formulas ++ post) = true) :
    check (pre ++ blank L (usedLabels check pre L post) ++ post) = true

/-! ## The English plan (composition-s2 2.3; 3.7 of the plan) -/

structure Line where
  frame : String                  -- E3, E5, E7, E10, E12, E13, E17, E26, E27, E28, E29, E30, E31, E32
  result : Option String          -- R1 to R7
  readings : List (String × Nat)  -- the candidates named, in source order
  model : Option String           -- the id of the checked model shown
  gaps : List (String × List String × Bool)  -- filled gaps the result depends on: predicate, tuple, value
  label : Option String           -- an E3, E5 or E7 line's premise label
/-- The plan of the case's decoded document `D` (review E5: `D` is bound to the case). -/
def englishPlan (D : Doc) (route : Route) (question : String) (answer : Lean.Json) : List Line
/-- composition-s2 2.4's non-wordings hold of every plan. -/
theorem plan_no_every_for_models (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
    ∀ l ∈ englishPlan D route q a, l.model.isSome → l.frame ∉ ["E10", "E26", "E30"]
theorem plan_model_names_every_set (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
    ∀ l ∈ englishPlan D route q a, l.model.isSome → l.readings.map (·.1) = D.sets.map (·.id)
end VE.Readings
```

`excludedBy D l c` is the Boolean that coupling or narrowing `l` fails on `c` (`couplingHolds`, `narrowingHolds`).
`englishPlan` takes the case's decoded `Doc`, so `plan_model_names_every_set` speaks of the document the plan was
made for (E5; draft 1's `D` was unbound, which made the statement false). The `<reading>` slot of every line shows
the named candidate's own sentence (3.7, A4).

The kind `readings-verdicts`: `question`, optional `assumed`, `premises`, `conclusion`, and `evidence` as a list of
`{choice, conflict, model, unsat, certificate, countermodel}`. Lean decodes each piece and checks it as in 3.4.
Missing evidence is `unknown`. The answer: `route`, `verdict`, `per_choice` (choice, result, the evidence form),
`conditional_on`, `restrictions`, `assumed`, `english`. The wire theorem chains RD-2a's replay theorems with the fold
theorems: from a successful answer whose verdict is ALL, NONE, SOME, CONFLICT-FREE or CONFLICT, the conclusion of
the matching `fold_*_sound` holds of the case's decoded document. For documents without the profile, the per-choice
checks are today's `readings-choice` evidence kinds, and the fold and English plan are the same functions; their
theorem is stated over the lower route's decoded documents, which is today's semantics of the enumerated route.

Python: `Enumerated` sends one `readings-verdicts` request per question and returns Lean's answer. Its combination
code is deleted: the result folding in `conflict`, `premises` and `entailment`, `_dependencies`, `_replays`, `_used`
for this route, and `restrictions`. `readings_route.Wording` renders from `english` for this route. The ledger
records the exact lines; the estimate is about 350 Python lines.

Fixtures (expected values *derived*):

| Case | Expected |
|---|---|
| F-ND1, conflict | CONFLICT-FREE under every reading, `conditional_on: ["unsaid:pair:help_required,help_permitted"]`. English: E26 with R1, E3 with the pair sentence |
| F-ND1, `∀ agent ∀ user. help_required` | SOME. E12 R2 (reading 0); E12 R3 (reading 1) with one filled-gap sentence, `help_required(a, u)` answered no |
| F-ND1, the same `--under rs_1:0` | ALL; E12 naming reading 0 only |
| F-ND1, `∀ agent ∀ user. help_required → help_permitted` | ALL, `conditional_on: ["unsaid:pair:help_required,help_permitted"]`. The entailment certificate alone does not need the label (W1's Background has the pair premise), but the conflict certificates the answer also rests on do (composition-s2 2.3 as built) |
| F-ND2, conflict | CONFLICT under reading 0 (latent), witness choice named; English: E12 R4 and the latent-conflict sentence |
| F-ND3, the query of F-ND1 | UNKNOWN (budget), or `UNKNOWN (not ALL: countermodel under …)` when a countermodel was supplied; English E28 |
| Missing evidence for one of two choices | UNKNOWN naming that choice |
| A certificate for choice 0 supplied as choice 1's | that choice `unknown`; never ALL |
| `usedLabels` on a certificate that never reads a slot label | `[]`; on one that needs it | `[label]` |
| The gate (review A2): conflict rows all CONFLICT-FREE, query rows `[proved, refuted, unknown]` | SOME |
| The gate: conflict rows `[free, free, unknown]`, any query rows | `UNKNOWN (conflict status: UNKNOWN)`, naming choice 2 |
| The gate: conflict rows `[free, conflict]`, query rows `[proved, proved]` | `UNKNOWN (conflict status: CONFLICT)`, naming choice 1; never ALL |
| Reading display (review A4): F-ND1's SOME | each E12 shows the candidate's own sentence in its `<reading>` slot, never "reading 2"; a verb-only set (S2a's M4) keeps the italic verb |
| S2a's enumerated fixtures (M8, M9, M12) | the same verdicts and English as today (Python fold before, Lean fold after), listed in DELTA as `none`; the A4 slot change listed as a signed `wording` change |

Deleted, not duplicated: Python's enumerated fold, its label replay and its restrictions, and the wording selection
for the enumerated route. None of these is left behind as a fallback.

Done when: the fixtures pass, the A/B over the readings and pilots corpora is identical except for listed wording or
order changes (DRI-signed, the A4 slot change among them), and the gate passes.

### RD-4a. Readings with their own vocabulary (Lean wire, 5–6 h)

Files: `lean/VE/Readings/Companions.lean` (new: merge, split, meaning ids).

```lean
namespace VE.Readings.Wire
open Lean

/-- The companion sets of a document: those whose every reading carries `companion`; a set mixing the two is
    refused (3.6). -/
def companionSets (document : Json) : Except String (List String)
/-- The merged environment of a set's companions (3.6): the same language, revision and profiles; sorts, constants and
    predicates united by name in reading order, a repeated name only with byte-identical canonical declarations;
    `readings@1` added. `sources` names each environment for the diagnostic (`<set>@<v>:<i>`). -/
def mergeCompanions (sources : List (String × Json)) : Except String Json
theorem mergeCompanions_extends (sources : List (String × Json)) (m : Json) (h : mergeCompanions sources = .ok m) :
    ∀ src ∈ sources, ∀ k ∈ ["sorts", "constants", "predicates"], ∀ (n : String) (d : Json),
      ((src.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d →
        ((m.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d
/-- The open terms of a set's companions (E4): united by name, a repeated name only with byte-identical entries;
    each validated against the merged environment. -/
def mergeOpenTerms (sources : List (String × Json)) : Except String (List Json)
/-- The case of one companion set (its unit, the set, the narrowings on it and its merged open terms, over the merged
    environment) and the main case (the document without its companion sets, with its own open terms). A coupling
    that names a companion set together with another set is refused (E3, A3). -/
def componentCase (environment document : Json) (set : String) : Except String (Json × Json)
def mainCase (environment document : Json) : Except String (Json × Json)
/-- A reading's identity over its own environment: `VE.Route.Wire.meaningId` over the companion's `environment_id`
    and the content's canonical AST; it must equal the recorded `meaning_id`. -/
def companionMeaningId (companion content : Json) : Except String String
end VE.Readings.Wire
```

Every kind under `readings@1` first splits the case. A kind that names one component (`readings-choice`,
`readings-separate`) takes `component` (a set id, or `main`). `readings-validate` and `readings-elaborate` answer
per component.

Fixtures (*derived*):

| # | Case | Expected |
|---|---|---|
| F-C1 | two companion sets, each two readings over disjoint frames (F-ND1's frame twice, the second with `help`→`warn` and `asks`→`calls`), plus a main fixed norm | three components; each admitted and separated; per-component answers as F-ND1's |
| F-C2 | in one set, `avoid_life_required` declared `(bearer, person)` and `(state, person)` | `InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare avoid_life_required differently` |
| F-C3 | one reading with a companion, one without | `InvalidInput: reading set rs_a mixes readings with and without their own vocabulary` |
| F-C4 | the companions of one set with different `profiles` | `InvalidInput: the readings of rs_a declare different profiles` |
| F-C5 | identical `person` sorts in two readings of one set | one `person` sort in the merged frame |
| F-C6 | a main fixed rule whose `over` names a companion reading's rule | `UnknownRule: rule <name>` in the main component |
| F-C7 | `companionMeaningId` on three UDHR companions (`u022a.entitlement`, `u048.state_negative`, `u074.prohibition`) | equal to the `meaning_id` recorded in run 20261006T1800Z's main document, or to the companion unit's id for u074. If they differ, the batch adds the canonical norm encoder Python's `rule.to_dict()` uses, with a byte-parity fixture |
| F-C8 | a companion with `soft-norms@0` | `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` |
| F-C9 (E3, A3) | F-C1 with a coupling over the two companion sets | `InvalidInput: coupling <id> links <set> and <set'>, which do not share one vocabulary`; a coupling over two main sets is kept in the main case |
| F-C10 (E4) | two readings of one set whose companions declare open term `ill_treatment` differently; then identically | refused, `… declare open term ill_treatment differently`; identical entries give one entry in the component's document, its conditions checked against the merged frame; the main case keeps only its own open terms |
| F-C11 (A3) | F-C1 with a narrowing on the first companion set | the narrowing, with its label `narrowing:<id>`, is in that component's case only; that component's `restrictions` list it, the other component's do not |
| F-C12 (A3) | F-C1 with the second companion set left unseparated (its candidates written with `content: null`, no companions) | the set is in the main case as W2, with W2's UNKNOWN, never a component; nothing else changes |

Deleted, not duplicated: nothing deleted. Python computes no companion meaning id and merges nothing.

Done when: the fixtures pass, A/B is identical (no corpus document has `companion`), and the gate passes.

### RD-4b. Components in the verdicts and the report (Lean and Python, 4–5 h)

Files: `lean/VE/Readings/Components.lean` (new); `readings-verdicts` answers over components.

```lean
namespace VE.Readings
universe u

/-- A document's components: the main document and one document per companion set (3.6). -/
structure Components where
  main : NDoc
  parts : List (String × NDoc)
def Components.all (K : Components) : List NDoc := K.main :: K.parts.map (·.2)
def CompatibleK (K : Components) (cs : List Choice) : Prop :=
  cs.length = K.all.length ∧ ∀ k (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c → Compatible N.D c
def ConflictFreeK (K : Components) (cs : List Choice) : Prop :=
  ∀ k (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
def ConsistentU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (VE.Norms.restrictAll (VE.NormDefaults.fill U).T S) ∧
    VE.Norms.DocumentExpansion (VE.NormDefaults.fill U) (VE.Norms.restrictAll (VE.NormDefaults.fill U).T S) S ∧
    VE.Norms.Sat S Γ
def ConsistentK (K : Components) (cs : List Choice) : Prop :=
  ∀ k (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c → ConsistentU (choiceU N c) (choiceDoc N.D c).2

/-- Per component, the checked rows of every compatible choice (`Covers` with `A = []`). -/
def RowsSound (K : Components) (rows : List (List (Choice × ChoiceResult))) (Γ : List VE.Formula) (φ : VE.Formula) :
    Prop :=
  rows.length = K.all.length ∧ ∀ k (N : NDoc) r, K.all[k]? = some N → rows[k]? = some r →
    Covers N [] r ∧ ∀ x ∈ r, Holds.{u} N Γ φ x.1 x.2

theorem foldK_conflict_free (K : Components) (rows : List (List (Choice × ChoiceResult)))
    (hr : RowsSound.{u} K rows [] .bottom) (h : rows.all (fun r => foldConflict r == .free) = true) :
    ∀ cs, CompatibleK K cs → ConflictFreeK.{u} K cs
theorem foldK_consistent (K : Components) (rows : List (List (Choice × ChoiceResult)))
    (hr : RowsSound.{u} K rows [] .bottom) (h : rows.all (fun r => r.any (·.2 == .model)) = true) :
    ∃ cs, CompatibleK K cs ∧ ConsistentK K cs
/-- A query typed in component `k`: ALL there is ALL for the document (restriction). The fold takes component
    `k`'s conflict rows `cs` (review A2). -/
theorem foldK_all (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (cs r : List (Choice × ChoiceResult)) (hcc : Covers N [] cs) (hc : Covers N [] r)
    (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hrs : ∀ x ∈ r, Holds.{u} N Γ φ x.1 x.2)
    (h : foldEntailment cs r = .all) :
    ∀ cs', CompatibleK K cs' → ∀ c, cs'[k]? = some c → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      VE.NormDefaults.EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
/-- NONE for the document: NONE in component `k` and a model of every other component under every compatible
    choice. -/
theorem foldK_none (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List (List (Choice × ChoiceResult))) (hr : RowsSound.{u} K rows [] .bottom)
    (cs r : List (Choice × ChoiceResult)) (hcc : Covers N [] cs) (hc : Covers N [] r)
    (hrc : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (hrs : ∀ x ∈ r, Holds.{u} N Γ φ x.1 x.2)
    (h : foldEntailment cs r = .none)
    (hm : ∀ j r', j ≠ k → rows[j]? = some r' → r'.all (·.2 == .model) = true) :
    ∀ cs', CompatibleK K cs' → (∀ j (M : NDoc) c, j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
      ∀ c, cs'[k]? = some c → CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
end VE.Readings
```

The answer adds `components` (per component: the unit, route, verdict rows, English), the product verdicts, and
`decided_units` by 3.9's rule. English: E32 and, per companion component, E31 and E30. CLI:
`ve document readings --conclusion … --sentence <unit>`. A conclusion that types in no component, or in more than one
without `--sentence`, is refused with
`InvalidInput: the conclusion uses terms of no sentence checked by itself` or
`InvalidInput: the conclusion's terms fit sentences <n>, <m>; name one with --sentence`. `--under` naming a set
outside the query's component is refused (A3):
`InvalidInput: --under names <set>, which is not a reading set of the sentence the conclusion is about`. The product
answer lists each component's `restrictions` and `conditional_on` under that component (A3).

Python: `ve/readings.py` `validate_reading_sets` allows `companion` under `readings@1` and does not compute
`s1_content_meaning_id` for such a reading, since Lean computes and compares it. `ve/document.py` counts a
companion reading as content-bearing. `ve/readings_verdicts.py` generates evidence per component. Rendering uses the
companion environment Lean accepted (display only).

Fixtures: F-C1 through `ve document check` (CONFLICT-FREE, `model`, three components, E31 twice); a query typed in
one component (ALL, E30); F-C1 with the second component's reading 1 made inconsistent (an asserted reading with ⊥),
where a query's NONE in the first component becomes UNKNOWN with the reason "another sentence's readings are not all
consistent" (*derived*); `decided_units` on F-C1 lists every unit with content. Split contract (A3), one fixture
each: `--under` naming the other component's set is refused with the text above, and naming the query's own set is
accepted; F-C11's answer lists `narrowing:<id>` under its component only; F-C12's main component reports the
unseparated set's W2 UNKNOWN.

Deleted, not duplicated: none. Python's W2 validation passes `companion` through unread.

Done when: the fixtures pass, A/B is identical outside companion documents, and the gate passes.

### RD-5. The UDHR: migration and measurement (pilot tooling and measurement, 4–6 h)

On a pilot branch (`pilot/udhr-readings-defaults`), with scripts under
`usecases/udhr-pilot/run-<stamp>/`:

1. **`migrate.py`** reads run 20261006T1800Z at `bd6c7ab2` and writes a new main document:
   - add `readings@1` to the main profiles;
   - for every reading with a companion, set `content` to the companion unit's content, `kind` to its kind,
     `companion.environment` to the companion's environment and `companion.open_terms` to the companion's open
     terms (E4);
   - for the three asserted readings without a companion, write a companion whose environment is the main
     environment restricted to the symbols the assertion mentions, with the norm companions' profiles, language and
     revision;
   - **no renaming (E1).** A set in which two readings declare a sort, constant or predicate differently is not
     migrated: it stays as it was on W2 (content null, no companions), is listed as "needs one vocabulary" with the
     first differing name, and is not decided. Re-translating such a set onto one `bearer` sort is a pilot task, not
     this batch's. A set in which two readings declare an open term differently stops the migration, naming the set
     and the term (E4). The sets whose merged frame the frozen decoder refuses (for example `DuplicateActRole`,
     `Norms/Tree.lean:273`) are listed the same way;
   - drop W2's `models`, add S1's `situations` and `distinguishing_models` (step 2), and take every `meaning_id`
     from Lean's `readings-validate` answer;
   - record every set not migrated (with its reason) and every copied declaration in `unmigrated.json`.
2. **`situations.py`** proposes, for each ordered pair `(a, b)` of a set, the 3.3 pattern: a base with one element
   per sort the probe needs, guards made true, every filling empty except what the witness's `Fill_T` forces, and
   the probe the witness's regulated predicate at that tuple. It asks Lean (`readings-separate`) and tries a second
   pattern with `a` and `b` exchanged. A pair left unseparated keeps its set as it was (W2, content null), and the
   set's bytes are not decided. Unseparated pairs are listed.
3. **Checks**, all at one commit, in the foreground: `ve document load`, `check`, `render` of the migrated document;
   every component's status witnesses (`norm-defaults-status` through `readings-choice`) compared with the
   companions' recorded `witnesses.json`. The 156 companions are re-checked as standalone documents too, so
   "nothing changed for a reading checked alone" is checked, not assumed.
4. **Measurements**, each with host load recorded:

   | Measure | Before (run 20261006T1800Z, as committed) | After (migrated) |
   |---|---|---|
   | `ve document load` wall and CPU | measured | measured, ≤ 120 s wall |
   | `ve document check` wall and CPU | measured | measured |
   | Document bytes | measured (about 281 KB: `git show` printed 280.7 KB for the main document) | measured, ≤ 4,000,000 |
   | Components; regulated predicates per component (max); readings per component (max) | — | measured; ≤ 64; ≤ 64 |
   | Premises verdict | UNKNOWN *recorded* | measured |
   | Conflict verdict | — | measured |
   | Lean-decided bytes and share (3.9) | measured (0 *derived*) | measured |
   | Maximum rules in one choice's document; decided bytes whose companions were already checked outside the document (E2) | — | measured |
   | Claimed covered; audit-verified | 4,792 (43.90%); 2,543 (23.30%) *recorded* | unchanged unless units changed status |
   | Sets admitted with every pair separated; unseparated pairs | — | measured |
   | Sets not migrated ("needs one vocabulary", E1) | — | measured, listed |

5. **Queries**, a demonstration of ALL, SOME and NONE with conditions, each answer recorded verbatim, each on a set
   that merges unchanged (E1; draft 1's three demonstrations were on `rs_u022a`, `rs_u055` and `rs_u052`, none of
   which migrates unchanged, 1.1). Expected answers per reading, *derived* from the companions at `bd6c7ab2`:
   - `rs_u029` (readings `entitlement`, `state_claim`), "every State must recognise each person everywhere as a
     person before the law": SOME. Under `state_claim` the conclusion follows (its rule's guard is ⊤). Under
     `entitlement` it does not follow: no rule decides the duty, and a situation whose filling answers that gap 'no'
     is a countermodel.
   - `rs_u081` (readings `entitlement`, `state_claim`, `state_claim_within_resources`), "every State whose
     organization and resources allow it must secure each person social security": SOME over every reading
     (`entitlement` does not follow, gap answered 'no'; both State readings follow), and ALL under
     `--under rs_u081:2`, naming that reading.
   - `rs_u081`, "no State must secure any person social security": NONE. Under each reading a checked situation
     with one State and one person refutes it: by the rule under `state_claim`, by the rule where the resources allow
     it under `state_claim_within_resources`, and under `entitlement` by a filling that answers the gap 'yes' (the
     filled-gap sentence shows it).

`tools/lean_decided_share.py` (new, Python, display): sums the span bytes of Lean's `decided_units`.

Deleted, not duplicated: nothing in `ve/`. The migration is data tooling and decides nothing Lean decides.

Done when: the migrated document loads within every limit of 3.8, the table is filled with measured values, the
`DELTA.md` and the pilot's `SUMMARY.md` report before and after, and every unseparated pair, set not migrated or
failed check is listed rather than worked around.

### RD-6a. S2a with a carried base-premise family (Lean, 5–6 h)

Off the UDHR path. Needed for documents with more than 64 choices in one frame. Files:
`lean/VE/Readings/SupExtra.lean`. The approved S2a statements become instances with `Q = []`; none is restated.

```lean
namespace VE.Readings
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

/-- A base-premise family that superposition carries: `Q' c` is over the vocabulary of `c`'s own document, so it
    mentions no choice symbol (review A1), and at a slot-admissible base of `sup D` encoding a compatible choice, `Q`
    holds exactly when the choice's own family holds of the pulled base. -/
def Transfers (D : Doc) (Q : List VE.Formula) (Q' : Choice → List VE.Formula) : Prop :=
  (∀ c, Compatible D c → ∀ a ∈ Q' c, a.WellFormed (choiceEnvFull D c) []) ∧
  ∀ c, Compatible D c → ∀ B : VE.Structure.{u}, BaseAdmissibleP (correlate (sup D).1) (slotP D) B →
    Encodes D c B → (VE.Norms.Sat B Q ↔ VE.Norms.Sat (pull D c B) (Q' c))

theorem superpose_conflict_free_extra (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q') :
    ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q) ↔
      ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) →
        ConflictFreeP.{u} (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c)
theorem superpose_all_extra (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra D A Q Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c) B)
    (hp : VE.Norms.Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc D c).1 B) []
theorem superpose_countermodel_extra {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheck D A Γ M = true)
    (hQ : Q.all (fun a => a.eval M []) = true)
    (hn : (VE.SoftNorms.circ (correlate (sup D).1) φ).eval M [] = false) :
    ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
      BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c)
        (pull D c M.asStructure) ∧
      VE.Norms.Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
      ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) []
theorem transfers_nil (D : Doc) : Transfers.{u} D [] (fun _ => [])
end VE.Readings
```

`supCertificateCheckExtra` is `supCertificateCheck` with `Q` after `slotUnder D A`. The up-direction uses
`Transfers`' first conjunct (review A1; draft 1 assumed it without stating it): `Q' c` is well formed over the
vocabulary of `c`'s own document, which has no choice symbol, and `base_up`'s extension agrees with the original base
on every predicate except the choice vocabulary. Each old theorem's proof becomes its `_extra` form at
`transfers_nil`. RD-6a and RD-6b are off the pilot path; their statements are re-reviewed before their own build.

Fixtures: every S2a fixture answers byte-identically (the kinds still call the old statements' functions).

Done when: builds, audit passes, `tools/lean_statements.py` shows additions only, and the gate passes.

### RD-6b. Superposition under the completion (Lean and Python, 5–6 h)

```lean
namespace VE.Readings
universe u
theorem fill_transfers (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true) :
    Transfers.{u} (fillDoc N) (VE.NormDefaults.fillPremises (supU N)) (fun c => VE.NormDefaults.fillPremises (choiceU N c))
/-- CONFLICT-FREE under every reading with the completion, read in norm-defaults' terms. -/
theorem nd_superpose_conflict_free (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    VE.Compose.ConflictFreeP.{u} (correlate (sup (fillDoc N)).1)
        (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
theorem nd_superpose_all (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : VE.Compose.ConflictFreeP.{u} (correlate (sup (fillDoc N)).1)
        (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra (fillDoc N) A (VE.NormDefaults.fillPremises (supU N)) Γ φ cert = true) :
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
      VE.NormDefaults.EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
end VE.Readings
```

Proof notes for `fill_transfers`: a `Fill_T` formula is `bindAll` of `pairConflict` and two `gapF`s, built by outcome
substitution through the filled tree. By `circ_canon` its truth at a base is a sentence over the complete
vocabulary of the filled document read in the canonical expansion. `pull_canon` (S2a, on `fillDoc N`) makes the two
expansions agree on every layer symbol of the choice's document, and `sim_decides` on `N.D` makes the author rules'
decisions agree (the `F_p` rules are fixed units, so they are their own images). Hence the two `Fill_T` lists agree
at an encoded slot-admissible base.

Route: under the profile on the norms chain, `routeOf` takes the superposed row when `superposable (fillDoc N)` and
`WellFormedU (supU N)` both hold. Otherwise it takes the enumerated row, with `ReadingsNotSuperposable`'s cause.
The superposed kinds run on `fillDoc N` with `Fill_T` appended to the slot (labels `unsaid:pair:<r>,<m>`). DRI ruling
5's check of every compatible choice, up to 1024, runs `WellFormedU` on each choice's UDoc as well. Python's
generators read the slot from `readings-elaborate` as today, `Fill_T` included.

Fixtures (*derived*): F-ND1 and F-ND2 take the superposed route with the same verdicts as RD-3's enumerated answers;
F-ND3 (128 choices) gets decided verdicts (E10 for its conflict status); a 200-document differential of generated
norms-chain documents under the profile, with at most 64 choices, gives identical verdicts on both routes.

Done when: as RD-3, plus the differential.

### RD-7. Verdicts across readings in Lean, superposed route (Lean and Python, 5–6 h)

`readings-verdicts` gains the superposed route: ALL from one certificate under `A = []`; SOME from a certificate
under one complete choice and a countermodel encoding another; NONE from a countermodel per compatible choice, at
most 64; per-reading premise statuses; dead readings. The wire theorems chain `readings_wire_all_sound`,
`readings_wire_model_sound` and `dead_sound` with the folds. The English plan covers composition-s2 2.3 items 1 to 6.
Python's `Superposed` keeps only evidence generation; its SOME and NONE assembly, `_dependencies`, `_replays`,
`_mentions` and the wording selection are deleted (ledger). Fixtures: S2a M1 to M20 with the same verdicts and
English, listed in DELTA as `none` or as signed `wording` changes.

### RD-8. Senses in `ve document` (Lean and Python, 4–6 h)

Specified in section 6, because it is independent of the other batches.

### RD-9. Soft chain under the completion (design, 3 h)

A planner batch, not specified here. It needs `fill` after `soften` per choice (10a's `Layered.lean`), `Coh_T`
regenerated on the filled tree, and `Transfers` for `Soft_T ++ Fill_T` (RD-6a's family on the soft chain). It is the
constitution's need (S2a 11: its main translation uses `norm-defaults@0`, and its force readings are strict against
default).

## 5. What RD-5 reports, and how

The DELTA and the pilot summary give the measured table of RD-5 step 4. Every number is measured at one commit and
with host load recorded, except the three *recorded* figures, which are copied with their source. The report states:

- the Lean-decided share before and after, defined in 3.9;
- that claimed and audit-verified shares are unchanged by this work, and that the next audit decides on the
  migrated units;
- that every sentence with readings was checked by itself (E31), so the share says nothing about whether two
  sentences' readings fit together;
- beside the share (E2): the maximum rules in one choice's document, the decided bytes whose companions were already
  checked outside the document, and that a reading holding one rule is CONFLICT-FREE by construction. Most UDHR
  readings hold one rule, and their companions already passed their checks as separate documents, so the move from 0
  measures those checks routed into Lean inside the document, not new assurance;
- the unseparated pairs, the sets not migrated ("needs one vocabulary", E1) and the copied declarations, as lists.

## 6. Senses in `ve document`: the next batch (RD-8)

**Why not in these batches.** Today only `ve senses check` calls the sense reader, `senses.read` through the one-shot
`ve_senses_route`, and it is admission only (`ve/__main__.py:54`; senses-integration-report). Wiring it into
`ve document` changes how fenced English units (`surface: english`) are read. Python's `parse_english` reads them
today (`ve/document.py:193`). It also changes those units' environment (the projected one) and so their
`environment_id` and meaning ids, which the W2 loader computes in Python until lean-first batch 17. None of this
touches the UDHR: its units carry JSON content, not English fences. So the work shares no code and no measurement
with RD-1 to RD-5. Senses B11 put it after the Lean document mode; RD-8 does it earlier, with a narrower scope that
needs no document mode.

**RD-8 (4–6 h, Lean and Python).**

- **Front matter.** `"senses": {"packs": [<bundled name> | <path>], "own": [...], "defaults": {<word>: <index>}}`,
  W2-validated as a key only. Python reads the pack bytes (`ve.senses.load_pack`, `bundled_pack`).
- **Lean.** `senses.read` gains optional `defaults`. Lean renders them with the merged `Assignment.lines`
  (`lean/VE/Senses/Assignment.lean:37`) and prepends them to the source, so the preamble stays the reader's one
  channel (senses D5). Lean refuses `defaults` together with written preamble lines:
  `InvalidInput: defaults are given both in the front matter and as lines`.
- **Python.** For a document with `senses`, every `surface: english` fence is sent in unit order, one sentence per
  fence, in one `senses.read` request, and `parse_english` is not called for those fences. Each fence's unit gets
  Lean's formula, and the formula environment of those units is Lean's projected `environment`, as the soft route's
  extended environment is used today. A fence whose sentence has candidates (an unresolved word) is refused with
  Lean's `Unresolved` text, unless the document has a reading set for that unit. `ve senses propose-readings` (senses
  B7) writes such sets.
- **Fixtures.** The senses spec's s1, s9, s16 and s22 as `ve-document@1` fences: the same formulas and the same
  refusals as `ve senses check`. A document with defaults in the front matter reads as the same text with the lines
  written. The relay lint forbids a `parse_english` call on the senses path.
- **Deleted, not duplicated.** No Python sense logic. `parse_english` is bypassed, not copied, for senses documents.
- **Needs.** The merged `senses.read` route (`ve_senses_route`, senses B5 and the part of B6 that merged); senses
  B6's remaining service modes are not needed. It is independent of RD-1 to RD-7.

## 7. Not claimed, open questions, risks

- **Not claimed.** No theorem relates the product of components to a merged frame. A merged UDHR frame would exceed
  the frozen limit of 64 regulated predicates (156 of them), so it cannot be built. `product_merge_faithful` (each
  verdict of the product equals the merged document's when no two components share a symbol that an assertion
  mentions) is open; RD-0's reviewers decide whether to state it. No speed is claimed for any batch. No claim is made
  about the UDHR's audit outcome.
- **Q1, the regulated limit.** Should the LIMITS CONTRACT (ARCH-ROADMAP P1) raise 64 for frames whose rules are
  per-component? That is a frozen-contract change with a DRI signature. It is not needed by this plan, but it is
  needed for cross-sentence questions on the UDHR.
- **Q2, closed (E5).** D4's shared fillings are the definition of separation under the completion: with
  independent fillings a reading would be separated from itself at any gap. An unseparated pair is equal meaning or a
  search miss; RD-5 lists them.
- **Q3, the reused quote marks** in the filled-gap sentence (3.7): for norm-defaults' reader test.
- **Q4, moved into RD-3 (A4).** The `<reading>` slot shows the candidate's own sentence (3.7); zero-training English
  cannot defer it.
- **Risk.** Lean-first 10b will delete `ve/norm_defaults.py`. RD-2b's generators use only the generic prover and
  search over Lean's regenerated formulas, so 10b removes nothing they need. The batch checks this (relay lint and
  the A/B).
- **Risk.** RD-5 depends on Lean finding separating situations for every pair. Pairs it cannot separate keep their
  sets on W2 and are counted as not decided. The share is then lower, and it is reported as measured.

## 8. Review checklist (for RD-0)

1. `fillDoc`'s three changes and the four equalities of 3.1: each well typed, and true of the merged `build`, `sup`,
   `soften` and `fill`.
2. `normsShaped` is what the norms chain's decoder guarantees: `Wire.decodeNorm` on `.norms` gives strict rules with
   no party, exception or `hard` flag.
3. Admission's order (3.2), each text exactly as `checkAuthorN` and S1 word it, and the suffix rule.
4. D4's shared fillings and `separates_soundU`: the witness's `Fill_T` is checked, the other side's may fail, and
   `achievesU_iff` says what is achieved.
5. Each per-choice check of 3.4 binds its evidence to the regenerated `choiceU N c`.
6. The folds and `Holds`, including universes: witnesses are in universe 0, as in `Layered.lean`.
7. `usedLabels_sound` and `restrictionsFor_spec`.
8. The English of 3.7: one reading each, W7 gate, non-wordings, and E31's honesty about what was checked.
9. 3.6's merge rule, the split, the product definitions and RD-4b's conditions for NONE and SOME.
10. 3.9's rule for Lean-decided units, and that the script decides nothing.
11. Conservativity (3.11) and fixture F-ND7.
12. Every batch's deletion list, and that no batch leaves a Python fallback for logic it moves.
13. (Draft 2, converged review.) Every statement true under its hypotheses, not only well typed: `fillNamesFree` on
    the four equalities, `attached_fillDoc` and `achievesU_iff`, with F-ND5 (A1); the conflict gate in
    `foldEntailment` and its soundness statements, and `Holds.inconsistent` (A2); the split contract (A3, E3); the
    `<reading>` slot (A4); no renaming (E1); E2's qualifiers beside the share; `D` bound in
    `plan_model_names_every_set` (E5); `Transfers`' typing conjunct (RD-6a).
