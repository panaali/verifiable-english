# Profile composition: the composition contract, the matrix, and the batches that lift measured refusals

> **Change log: pc-fid-rev2, DRI 2026-10-30 pc-fid-rev2 item 1**
> (`manage-agents/reviews/dri-decisions-20261030-pc-fid-rev2.md`, item 1, SIGNED: the 2026-10-30 family-scoped
> re-pilot, 5/10 FAITHFUL and COMPOSES; this draft applies R1 to R4 and nothing else). Draft 6. The plan's section 16
> maps each finding to its batch, its statements, its fixtures and the unit it answers:
> - R1 (B; ursp.t2_argument, ursp.t4_argument, the document's break): **opened**, PC-2b. A set whose candidates differ
>   on more than one axis is coupled on one combined axis whose values are its candidates, or every candidate of every
>   set a coupling names carries that coupling's axis (the plan's 15.2 rule 10). Main's refusal stays:
>   `admitS2Rest_couplings` (proved, main's code) and `compatibleChoices_admitS2` (3.2), row 20 of 4, F2.10 (stub: both
>   admitted forms, the refused unlabelled form with main's exact `CouplingLabelMissing` text, the five choices).
> - R2 (A; ursp.t3_plan): **staged**, PC-6c (after act phrases' readings elaboration). An act phrase with more than one
>   derivation inside a reading candidate is one candidate per derivation, or a narrowing with a cited source unit,
>   else act phrases' GAP; never one derivation without a reason (3.6; the plan's 15.2 rule 11). Row 21 (act phrases'
>   D-15, kept), F6.17 (stub: main's act grammar gives the fixture's phrase two derivations, each one reading of three
>   atoms under *must*; D-15's text for the unnarrowed form).
> - R3 (A; ursp.t4_evidentiary): **staged**, PC-12 (new), after modality's MD-4a and its row batch. A modal or scenario
>   condition that limits which situations a rule binds is the last conjunct of the candidate rule's guard
>   (`scenarioGuard`, 3.11), filled by `STUB[modality-counterfactual]`, which takes the rule's quantified variable as
>   the scenario's situation variable or is refused `ScenarioUnbound` (modality's code and text). Row 22, F12.1 (stub),
>   F12.2, F12.3. The scenario construct stays modality's.
> - R4(a) (A; ursp.t4_plan_moonshot): **opened**, PC-1 and PC-2b, on their existing statements (`judgedIn_soft`,
>   `chainReadings_rows`; no new statement). A purpose clause with both readings is a reading set {limiting: a guard
>   judgment conjunct, rationale: the rule as written and purpose-explanation's link}, or a narrowing with a cited
>   source unit; never a link part alone (3.1; the plan's 15.2 rule 12). F2.11 (stub: the reader finds the limiting
>   candidate's judgment, and the rationale candidate's guard holds none).
> - R4(b): **slot named**. A filler act phrases' grammar does not derive (a run of words beside a fixed phrase in one
>   argument) fills the act's argument position as `STUB[act-phrases]`; the follow-up row ap-mixed-filler owns it, and
>   this specification designs nothing of it.
> - Review fix (pc-fid-rev2's statement review, finding 1, A; DRI 2026-10-30 pc-fid-rev2 item 2): R1's "nothing main
>   refuses has a row" is now bound. `compatibleChoices_admitS2` also concludes `cs = VE.Readings.choices a.D` (the
>   chain's choices are main's choices of the admitted `Doc`), and `readingsCaseOf_keeps` (new) states that the case's
>   document carries the front matter's `reading_sets` and `couplings` unchanged (3.2; 9, open point 12).
>
> Where it landed: this log; 0; 3.1 (the limiting purpose); 3.2 (`admitS2Rest_couplings`, `readingsCaseOf`,
> `readingsCaseOf_keeps`, `compatibleChoices_admitS2`, the coupling rule); 3.6 (PC-6c's derivation rule); 3.11 (new,
> PC-12); 4 (rows 20 to 22, the fault order); 5 (F2.10, F2.11, F6.17, 5.10 new: F12.1 to F12.3); 6; 7 (choices 32 to
> 36); 8; 9 (the refreshed run with the review fix: 258 declarations, 107 with `sorry`, 105 guards and 11 proofs pass;
> the revision's two seeded mutants; open points 12 to 15). Nothing the DRI signed in pc-d2, pc-fid-rev or the
> cross-plan rulings changes: every earlier statement and expected value keeps its text, `CouplingLabelMissing` stays
> main's refusal, and `.layer` still grants nothing.
>
> **Change log: pc-fid-rev DRI ruling, 2026-10-30 item 1**
> (`manage-agents/reviews/dri-decisions-20261030-pc-fid-rev.md`, item 1, SIGNED: the acts × scope pair lemma carried
> no governor effect, section 9's open point 9). `SplitReach` gains the conjunct `∀ g ∈ D.governors, ∀ g₀ ∈ D₀.governors, g.id = g₀.id → g.effect = g₀.effect`: acts' split
> leaves every governor's effect as written (3.6). So `PairFacts ("acts@0", "scope@0")` and `ActsScopeRuns`, which
> read it, carry the effect, and no stack of three or more holding acts and scope is listed until PC-6b proves it. An
> effect the split would have to rewrite is refused by the pair lemma, never mapped by a guess (9, open point 9; owner
> act phrases, PC-6b). Where it landed: 1.5 (`PairFacts`' docstring; the M1 paragraph and the argument for every
> pair), 3.6 (`SplitReach`), F6.12's expected answer, 9 (the refreshed run, the new proof `splitReach_effect`, the
> ruling's seeded mutant, open point 9). The conjunct elaborates, so the ruling's fallback is not used. Nothing else
> changes.
>
> **Change log: pc-fid-rev, DRI 2026-10-29 item 4** (`manage-agents/reviews/dri-decisions-20261029-pc-d2-r2.md`,
> item 4: the 2026-10-29 fidelity pilot's composition cells). Draft 5. Every PC-owned break the pilot measured is
> opened (exact statement, theorem, fixture) or staged (the PC item that opens it, its designed rule and fixtures):
> - B1, acts inside reading candidates: **staged**, PC-6c, after act phrases' readings elaboration (act-phrases SR8,
>   F11). 1.5 (`PairFacts`), 3.6 (`ActsChoiceFaithful`), F6.14 to F6.16.
> - B2, commitments beside judgments: the document mode **opened**, PC-4's record rule, with `documentLayers`' records
>   derived from the table; the commitments mode **staged on CM-2 (a request row)**. 3.4 (`recordProfile`,
>   `documentLayersOf`, `checkDocSets_ignores_commitments`, `CommitmentsBesideJudgments`), F4.11, F4.15, F4.16.
> - B3, a governor's own set, or a set a frontier reach covers, beside readings: **staged**, PC-5b, after scope's
>   SC-5. 3.5, F5.6 to F5.8, row 19 of 4.
> - B4, discourse beside readings: **opened**, PC-7c. 3.7 (`setShape`, `ResolveKeepsSets`), F7.6 to F7.8.
> - B5, attitudes beside judgments: **staged**, PC-1b, after AT-3a and AT-2. 3.1 (`withAttitudeContents`,
>   `opensIn_attitude`), F1.9 to F1.11.
> - B6, the four-rewriter document stack: **opened**, PC-4b, one rule for any number of rewriters. 1.5
>   (`StackRuns`, `RewriterFacts`, `PairFacts`, `ReadingsFaithful`, `RouteFacts`' generic clause, `stack_evidence`,
>   `stackRuns_all`, the listing rule), 3.4, F4.12 to F4.14, F4.17.
> - Review fixes (the pc-fid-rev statement review, findings 1 to 3): `PairFacts ("ve.discourse@1", "scope@0")` keeps
>   each governor's id, unit, recorded reach and reach, and resolves its effect at its unit (`ResolvedEffect`, 1.5);
>   `ActsChoiceFaithful` is stated over cases, keeps the reading sets' shapes and couplings, and reads a defined
>   `readingsChosen` (3.6); `documentLayers`' records are derived by `recordProfile` (3.4), and B2's commitments mode
>   is staged.
>
> Section 9 records the run of this draft's stub. Nothing the DRI signed is changed: E1s (row 7b), F4.7 and every
> pc-d2 statement keep their text; `RouteFacts`' five entries are as they were, and its generic clause covers only
> stacks with no entry of their own. Draft 4's header follows.
>
> Status: item-1 specification, draft 4 (2026-10-29), branch `design/profile-composition`, written from
> [profile-composition-PLAN.md](profile-composition-PLAN.md) draft 5. Draft 4 applies the pc-d2 statement review's
> FIX (`manage-agents/debates/pc-d2-review/DRI-RULING.md`, edits 1 to 10; the acting DRI's decision
> `manage-agents/reviews/dri-decisions-20261029-pc-d2.md`). Its round 2 applies the acting DRI's decision
> `manage-agents/reviews/dri-decisions-20261029-pc-d2-r2.md`, item 1, alone: the clash check is symmetric (1.7, F1.3o).
> Section 9 records the Lean run of the stub file as the DRI ruling of 2026-10-30 (item 1) leaves it: all 223
> declarations elaborate, 104 of them with `sorry`, and all 90 guards and 10 proofs pass (round 2's run: 191, 92, 67
> and 8).
> Elaboration with `sorry` establishes typing only: it shows that a statement is well formed, never that it is true.
> Edits to main's own definitions are elaborated against named stand-ins, and acyclic imports are checked by PC-4's
> `lake build`, not by the one-file stub (9). The ruling's item 11 is one confirmation review of edits 1 to 10, of
> the refreshed section 9 and of every fixture the ruling names. Nothing is built before that pass. Draft 3's claim
> that "every statement elaborates" is withdrawn: its run predated the G3 amendment's statements. Section 9 lists two
> open points found while applying the ruling; round 2 resolves the first.
>
> Earlier drafts. Draft 1 was written from plan draft 2, which is
> plan draft 1 with the converged design debate applied (`manage-agents/debates/design-profile-composition/{fable,astra}.md`,
> CONVERGED after round 3: REVISE, then one statement review, then BUILD) and the acting DRI's cross-plan rulings of
> 2026-10-29 (`DRI-CROSSPLAN.md` in that directory). Draft 2 applied the statement review's ruling
> (`manage-agents/debates/profile-composition-spec/DRI-RULING.md`, items 1 to 13: FIX) to this specification and the
> plan; the plan's section 14 maps each item. Draft 3 applies the verification of draft 2
> (`manage-agents/profile-composition-p3ver1.final.md`: FAIL, two findings). G3 and 2a's lemma are stated under the
> DRI's G3 amendment to ruling item 2a (synthesis round 2, DECISIONS item 3): the exchange applies only when it is
> injective on all stated values, and F1.3l is the regression, refused by validation on both sides (1.7). Draft 3's
> Lean run (77 declarations with `sorry`) predated that amendment's statements; draft 4's run replaces it (9).
>
> Sections 1 and 3 are the statements, section 2 the English and section 5 the acceptance fixtures. They are
> implementation obligations, not proofs. Section 7 lists every point where this draft chose between readings of
> the plan, and section 9 records how the statements were checked.
>
> Inputs, all on main at `d25bc343b`:
> - [composition.md](composition.md) (the stack, E1 and E2, the feature names) and
>   [composition-PLAN.md](composition-PLAN.md) (S2b, S4);
> - [judgment-terms.md](judgment-terms.md) 4 and 8 (`Judgments.status`, the document-mode hook, the diagnostics);
> - [premise-packs.md](premise-packs.md) 2 (`Pack`, `assemble`, `X`, `transfers_X`);
> - [rd-9-soft-chain.md](rd-9-soft-chain.md) (`LayeredU`, `acceptanceX`) and [defeasible.md](defeasible.md)
>   (`Dflt_T`, `DefaultBase`);
> - [scope.md](scope.md) 1 and 11 (GOVERN, `checkDocSets`) and [act-phrases.md](act-phrases.md) 6 (`SplitMap`);
> - `lean/VE/Compose/Dispatch.lean` (AR-10's `ProfileRow`, `profileTable`, `gateOf`, `gate_acts`, `gate_scope`);
> - `lean/VE/Service/Document.lean` and `lean/VE/Service/ScopeAdmission.lean` (the document mode).
>
> This specification changes no frozen contract and no checker function. It changes approved theorem statements
> under this review: `gate_acts` and `gate_scope` (3.6, 3.7), and the decision-name statements that split rules
> make false, listed one by one with their callers in 1.10. Draft 1's claim that only two statements change is
> withdrawn. It amends the text of composition.md's E1 and E2 before their first registration (2.1). It changes the
> answer to some requests without `judgments@0` in one place, PC-1's clash validation (1.7, row 16 of 4).

## 0. Scope, one paragraph

A **composed document** lists two or more profiles that each change what the document means or how it is checked.
This specification fixes four things:
- how each profile takes part in a composed document: one **interface**, a field of AR-10's row (1.2);
- in which order rewriting profiles run: the **stack**, read from those rows (1.3);
- what an admitted combination rests on. Structural laws (1.4) are not enough; each admitted stack needs a
  **typed statement about its route** (1.5).
- how the document mode refuses everything else: one module, in today's order and texts, plus two new rules. A list
  whose stack has two or more rewriters and is not listed is refused with E1 (the stack rule), and so is a list
  holding a `.layer` profile other than `documents@1` and `judgments@0` that its own theorem does not cover (the
  layer rule, 3.4).

The batches then lift the refusals the pilots measured:
- `judgments@0` beside the soft and rights chains (PC-1);
- the soft and rights chains under `norm-defaults@0` and `readings@1` in the document mode (PC-2a to PC-2c);
- `judgments@0` beside `scope@0` (PC-5);
- `acts@0` beside soft-norms and rights (PC-6, on PC-6a's decision key), and the constitution stack (PC-6b);
- discourse beside scope and acts (PC-7b);
- from the 2026-10-29 fidelity pilot (pc-fid-rev): `commitments@0` beside `judgments@0` (PC-4's record rule),
  discourse beside readings (PC-7c) and any number of rewriters whose pairs are listed (PC-4b); and, staged on
  another family's item, acts beside readings (PC-6c), a governor's own reading set (PC-5b) and attitudes beside
  judgments (PC-1b);
- from the 2026-10-30 re-pilot (pc-fid-rev2): how a set whose candidates differ on more than one axis is coupled
  (PC-2b; main's `CouplingLabelMissing` stays), an act phrase with several derivations inside a candidate (PC-6c),
  a purpose clause's two readings (PC-1, PC-2b), and, staged on modality's MD-4a, the scenario slot in a candidate's
  guard (PC-12).

Priority stays two typed graphs, each with the check it already has (1.8). "No exception" gets one definition,
owned by defeasible, read from metadata the packs export (1.9). A split rule keeps one decision (1.10).

Every answer stays three-valued. No composition turns UNKNOWN into a verdict, and none chooses a reading.

Out of scope:
- composition S2b and S4, which PC-8 and PC-7a schedule; composition-PLAN and its specifications own them;
- the meaning of another family's sentences: weighing's zones, attitudes' guard nodes, events' calendar;
- "decided given calls", which is now a request to judgment-terms' JT-4 (2.4);
- the constitution "parts with a checked interface" route, an escalated round-2 decision that no batch here
  assumes;
- any coverage number. Every unlock in the plan is a ceiling or an estimate until a pilot re-run measures it.

## 1. Definitions

### 1.1 The stack

| Rank | Step | Profiles | Interface (1.2) | Hands its successor |
|---|---|---|---|---|
| 1 | RESOLVE | `ve.discourse@1` | `rewrite 10` | the same document, references closed (composition S4) |
| 1a | ACTS | `acts@0` | `rewrite 11` | rules over split acts, and the `SplitMap` |
| 1b | GOVERN | `scope@0` | `rewrite 12` | governed units (reads `SplitMap`) |
| 2 | STRUCTURE | `right-clauses@0` | `rewrite 20` | rights lines; `Rel_D` |
| 3 | SUPERPOSE | `readings@1` | `rewrite 30` | one reading-free document; `Choice_D` |
| 4 | CHAIN | `rights@0`, `soft-norms@0`, `norm-defaults@0`, `norms@0`; then packs in `packOrder`, the defaults assumption `Dflt_T` (only when asked), `norm-defaults@0`'s fill (last) | `chain` | a W1 tree and the composed premises `X` |
| 5 | CHECK | `relational-fol@0`, `closure@0`, `nary@0`, `order@0` | `checker` | a certificate, a finite model, or UNKNOWN with its limit |
| L | LAYERS | `judgments@0`, `documents@1`; planned: `cardinality@0` (qt-a3c), `presupposition@0` (PS-4), `modality@0` (MD-2), `hedges@0` (H-3), `purposes@0` (PE-2), `examples@0` (E-2) | `layer` | report fields only; no verdict changes |
| B | BASE | `data@0`, `definitions@0`, `time@0` | `base` | as today |
| P | PACKS (inside rank 4) | planned: `weighing@0`, `attitudes@0`, `scales@0`, `events@0` | `pack id` | their premises in `X`, in `packOrder` |
| O | OUTSIDE | `alternatives@0`, `risk@0`, `speech-acts@0`, `reports@0`; planned: `commitments@0` (its own mode), `calc@0`, `arith@0` | `outside` | their own route heads; a pair with the chain needs a reviewed bridge |

Ranks 1, 1b, 2 and 3 are composition.md 1.1's. Rank 1a (acts before scope, after discourse) is adopted as the
plan's stack position (DRI ruling 4(2), consistent with SC1). Nothing is admitted by its rank alone. Rank 1c is
retired (synthesis round 2, C15): `presupposition@0` is `.layer`, and no row has rank 13. `cardinality@0` is
`.layer`, not `outside`. The rank is a number so that the stack order is a sort, not a second list (1.3).

**The planned rows' values** (PC-3 assigns them; each owning plan confirms its value in its row batch, and a
planned profile has no row, so it stays refused, until that batch lands):

| Profile | Interface | Slot of its row | Source of the slot |
|---|---|---|---|
| `cardinality@0` | `.layer` | `"layer"` | qt-a3c's row (`Dispatch.lean:798` on main after qt-a3c) |
| `presupposition@0` | `.layer` | `"layer"` | synthesis round 2 (C15); PS-4's row |
| `modality@0` | `.layer` | `"layer"` | modality-counterfactual-PLAN MD-2 ("the row uses the `layer` slot") |
| `hedges@0` | `.layer` | `"layer"` | hedges-generics 2.2 (a document layer like `judgments@0`) |
| `purposes@0` | `.layer` | `"layer"` | purpose-explanation 2.5 (the document mode's outer wrapper; it adds a member to the answer) |
| `examples@0` | `.layer` | `"layer"` | hedges-generics E-2 (report lines only, `examples_never_close`); E-2 defines its `requires` |
| `commitments@0` | `.outside` | `"commitments"` | commitments D13 (one profile, one mode, `ve commitments`): its pairs are its own mode's |
| `weighing@0`, `attitudes@0`, `scales@0`, `events@0` | `.pack id`, `id` the pack's | `"pack"` | synthesis round 2 (N1) |
| `calc@0`, `arith@0` | `.outside` | their row batch's route head (me-2nb, me-12b), added to `slotAgrees .outside`'s list in that batch | — |

`commitments@0`'s slot `"commitments"` is no route head, so in the document mode it is a document record (3.4's record
rule, pc-fid-rev): read by no decoder there, its pairs its own mode's.

The definitions field (definitions PD-1a's `definitions` front-matter block, `ve.definitions@1`) is a key in
`metadataKeys`, not a profile, so it has no row and no interface of its own. Its formula units are read under
`definitions@0`, whose interface is `.base`. A profile without a row, and so without a value, stays absent from
`profileTable` and is refused by the gate, as today (`Unsupported profile p`).

### 1.2 The interface: a field of AR-10's row (PC-3)

The plan's separate `interfaces` table, its `Step` type and its totality theorem C0 are deleted. The table had
already drifted from AR-10's: it gave `documents@1` the `base` interface, while main's row says `"layer"`
(`Dispatch.lean:787`). The interface is now one more field of the row that already registers the profile, so it
cannot drift.

```lean
-- lean/VE/Compose/Dispatch.lean (AR-10's file; the edit is reviewed by AR-10's owner)
namespace VE.Compose

/-- How a profile takes part in a composed document (profile-composition 1.2). A rewriter's rank is its place in
the stack (1.1); the stack order is read from it (1.3). -/
inductive Interface
  | checker | base | layer | rewrite (rank : Nat) | chain | pack (id : String) | outside
  deriving DecidableEq, Repr

structure ProfileRow where
  profile   : String
  requires  : List String
  refuses   : List (String × String)
  slot      : String
  interface : Interface      -- (new) the value of 1.1's Interface column
  deriving Repr
```

Every row of `baseRows` and `wrapperRows` gains its value from 1.1's column. The proofs that write a row literally
(`gate_legacy`, `gate_acts`, `gate_scope`) gain the same last component. `cardinality@0`'s row (qt-a3c) carries
`.layer`, so PC-3 waits for qt-a3c (DRI ruling 2(a)).

**C1 on cardinality's row.** This specification takes the first option: cardinality's slot is `"layer"`, as qt-a3c's
row writes it (`⟨"cardinality@0", ["order@0", "relational-fol@0", "time@0"], refusing "cardinality@0"
cardinalityOthers, "layer"⟩`), and `slotAgrees "layer" .layer = true`. `slotAgrees` is not widened, and its
`.outside` list no longer names a `"cardinality"` slot, which no row has (F3.4b).

```lean
/-- The slots each interface may sit on. -/
def slotAgrees (slot : String) : Interface → Bool
  | .checker => slot == "checker"
  | .base => slot == "layer"
  | .layer => slot == "layer"
  | .rewrite _ => slot == "layer" || ["discourse", "clauses", "readings", "govern"].contains slot
  | .chain => ["norms", "normDefaults", "soft", "rights"].contains slot
  | .pack _ => slot == "pack"
  | .outside => ["alternatives", "risk", "speechActs", "reports", "commitments"].contains slot

/-- C1. The slot and the interface of every row agree. -/
theorem interface_slot : ∀ r ∈ profileTable, slotAgrees r.slot r.interface = true := by decide

/-- C2. A profile with several rows (`risk@0`, `right-clauses@0`, `readings@1`) has one interface. -/
theorem interface_functional :
    ∀ r ∈ profileTable, ∀ s ∈ profileTable, r.profile = s.profile → r.interface = s.interface := by decide
```

`.pack id` is for the planned pack providers (weighing, attitudes, scales, events): they register rows with
`interface = .pack id` and AR-10's slot `"pack"`, which PC-3 adds in `lean/VE/Compose/Dispatch.lean`, so
`slotAgrees (.pack _) "pack" = true` (N1). Soft and rights are the packs `soft` and `rights` of the chain, so their
rows keep `.chain`. `gateOf` alone writes the `UnsupportedProfile:` prefix.

**`.layer` grants nothing by itself.** An interface value admits no list. G3 (1.7) is `judgments@0`'s own theorem,
and `documents@1` is the record layer that `judgments@0` requires. Any other `.layer` profile composes only through
its own transparency theorem, stated for every admitted list that contains it (not pair by pair) and added in its row
batch as an entry of `LayerFacts` (1.5). Until that entry covers a list, PC-4's layer rule refuses the list with E1
(3.4, row 17 of 4). On main the rule refuses nothing: the only `.layer` profiles of `profileTable` are
`documents@1` and `judgments@0` (F4.10).

### 1.3 The stack order (PC-3)

`rewriters`, `stackOf` and `Contract.listedStacks` (1.5) are in `lean/VE/Compose/Stack.lean` (new, PC-3; owner
composition). It imports only `VE.Compose.Dispatch`, so `Compose/Matrix.lean` reads them without importing
`Contract.lean`, which imports `Service/Document.lean` (3.4, the imports).

```lean
-- lean/VE/Compose/Stack.lean (new; composition)
/-- The rewriting profiles of a table with their ranks, each profile once, in table order. -/
def rewriters (t : List ProfileRow) : List (Nat × String) :=
  (t.filterMap fun r => match r.interface with
    | .rewrite k => some (k, r.profile)
    | _ => none).eraseDups

/-- The rewriting profiles a list enables, in stack order. -/
def stackOf (t : List ProfileRow) (ps : List String) : List String :=
  (((rewriters t).filter fun x => ps.contains x.2).mergeSort fun a b => decide (a.1 ≤ b.1)).map (·.2)

/-- C3. Ranks are distinct, so the stack order is determined. -/
theorem rewriter_ranks_distinct : ((rewriters profileTable).map (·.1)).Nodup := by decide
```

On main's table, `rewriters profileTable` is `[(11, "acts@0"), (10, "ve.discourse@1"), (20, "right-clauses@0"),
(30, "readings@1"), (12, "scope@0")]` (F3.5). `stackOf` sorts by rank, so the stack of
`["acts@0", "norms@0", "relational-fol@0", "scope@0"]` is `["acts@0", "scope@0"]`. No pipeline takes its order from
any other list.

### 1.4 Structural laws: well-formedness and name freshness (G2, PC-3)

G2 is renamed **"well-formedness and name freshness"**. It is not a soundness theorem. A rewriter that replaces
every claim with its negation can satisfy all three laws, so nothing is admitted on G2 alone (1.5).

```lean
-- lean/VE/Compose/Contract.lean (new; composition)
namespace VE.Compose.Contract

structure Rewriter (σ : Type) where
  profile : String
  run     : σ → Except String σ
  on      : σ → Bool
  writes  : List String          -- the prefixes of the names it may introduce

structure Rewriter.Laws {σ : Type} (WF : σ → Prop) (names : σ → List String) (r : Rewriter σ) : Prop where
  preserves : ∀ D D', WF D → r.run D = .ok D' → WF D'
  off       : ∀ D, r.on D = false → r.run D = .ok D
  fresh     : ∀ D D', r.run D = .ok D' → ∀ n ∈ names D', n ∈ names D ∨ ∃ p ∈ r.writes, n.startsWith p = true

def pipeline {σ : Type} : List (Rewriter σ) → σ → Except String σ
  | [], D => .ok D
  | r :: rs, D => r.run D >>= pipeline rs

/-- The pipeline of a list in the stack order AR-10's rows give; a profile with no rewriter of this document type
is skipped. -/
def pipelineOf {σ : Type} (t : List ProfileRow) (ps : List String) (rw : String → Option (Rewriter σ)) :
    List (Rewriter σ) :=
  (stackOf t ps).filterMap rw

theorem pipeline_preserves {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D D' : σ) (hD : WF D) (h : pipeline rs D = .ok D') : WF D'

theorem pipeline_off {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D : σ) (hoff : ∀ r ∈ rs, r.on D = false) : pipeline rs D = .ok D

theorem pipeline_names {σ : Type} (WF : σ → Prop) (names : σ → List String) (rs : List (Rewriter σ))
    (hl : ∀ r ∈ rs, r.Laws WF names) (D D' : σ) (h : pipeline rs D = .ok D') :
    ∀ n ∈ names D', n ∈ names D ∨ ∃ r ∈ rs, ∃ p ∈ r.writes, n.startsWith p = true
```

### 1.5 Typed route evidence and M1 (PC-3, PC-4)

The document mode works on cases (`Lean.Json`), and GOVERN rewrites a case before the chain reads it
(`checkDocSets`). So the document mode's rewriters have one type, `Rewriter Json`. Profiles that work inside
another route's decoder (acts on the norm decoders, readings in the chain's loader) have no case rewriter until a
batch writes one; `pipelineOf` skips them.

```lean
/-- GOVERN as a rewriter of document-mode cases: `checkDocSets`' scope branch before the chain. -/
def scopeRewriter : Rewriter Json where
  profile := "scope@0"
  run := fun j =>
    if "scope@0" ∈ VE.Service.Document.profilesOf j then do
      let D ← VE.Scope.decodeScope j
      let out ← VE.Scope.governSetsWith VE.Scope.governFast D
      pure (if (VE.Scope.governedSetUnits D).isEmpty then VE.Service.Document.withUnits j out
        else VE.Service.Document.withSets j out)
    else .ok j
  on := fun j => decide ("scope@0" ∈ VE.Service.Document.profilesOf j)
  writes := []

/-- The document mode's case rewriters, by profile. -/
def docRewriters (p : String) : Option (Rewriter Json) :=
  if p == "scope@0" then some scopeRewriter else none

/-- A document-mode entry `run` runs its list's pipeline, then the chain, then scope's fold, whenever it answers. -/
def ScopeRunsOf (run : Json → Except String Json) : Prop :=
  ∀ j ans, run j = .ok ans → "scope@0" ∈ VE.Service.Document.profilesOf j →
    ∃ D j' a, VE.Scope.decodeScope j = .ok D ∧
      pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewriters) j = .ok j' ∧
      VE.Service.Document.checkCore j' = .ok a ∧ ans = VE.Scope.foldGovernors D a

/-- The document mode's run statement (scope's instance). -/
def ScopeRuns : Prop := ScopeRunsOf VE.Service.Document.checkDocSets

/-- The theorem tying the document mode's run to the pipeline (scope's instance); from `scope_admission_sets`
(ScopeAdmission.lean:158) and `governSetsFast_eq`. -/
theorem checkDocSets_pipeline : ScopeRuns

/-- A run statement alone says nothing about meaning: an entry that refuses every case satisfies it (F3.7). -/
theorem refuseAll_runs : ScopeRunsOf (fun _ => .error "refused")
```

**Typed route evidence.** Each listed stack's admission rests on a proposition about that route: a `Prop`, never a
`Lean.Name`. Draft 1's `pairTheorems : List (String × String × Lean.Name)` is deleted, because a listed name says
nothing about whether that theorem is about the route.

Each entry of `RouteFacts` is the stack's run statement conjoined with what the plan (2.3) promises besides it:
each rewriter's own faithfulness and its semantic preservation, each written out as a `Prop` below. A run
statement only describes a successful run, so it would hold of a document mode that refused every case:
`refuseAll_runs` shows this for `ScopeRunsOf`, and `ActsScopeRuns` has the same form. The faithfulness and
preservation conjuncts are statements about the rewriters' own functions, and they do not follow from a run
statement.

```lean
/-- GOVERN's own faithfulness (scope 1.4, SC-1, SC-5): the run path is the statement, per choice included
(`governFast_eq`, Scope/Theorems.lean:545; `governSetsFast_eq`, ReadingsTheorems.lean:16), and a unit is governed
by exactly the governors whose reach covers it (`governorsOf_iff`, Theorems.lean:328). -/
def ScopeFaithful : Prop :=
  (∀ D, VE.Scope.governFast D = VE.Scope.govern D) ∧
  (∀ D, VE.Scope.governSetsWith VE.Scope.governFast D = VE.Scope.governSets D) ∧
  ∀ D u g, g ∈ VE.Scope.governorsOf D u ↔
    g ∈ D.governors ∧ VE.Scope.unary g.effect = true ∧ ∃ us, VE.Scope.covered D g.reach = .ok us ∧ u ∈ us

/-- GOVERN's semantic preservation: an admitted block with no governor and no part hands the chain the document
unchanged (`govern_identity`, Theorems.lean:308). -/
def ScopePreserves : Prop :=
  ∀ D, VE.Scope.admitBlock D = .ok () → D.governors = [] → VE.Scope.partUnits D = [] →
    VE.Scope.govern D = .ok D.doc

/-- Per choice (`readings@1` beside scope, SC-5rc): the choices governed are the joint choices over the governed
sets, and a fault under one choice refuses the document (`scope_set_choices`, `governSets_choice_refused`,
ReadingsTheorems.lean:20, :43). -/
def ScopeSetsFaithful : Prop :=
  (∀ D cs, VE.Scope.setChoices D = .ok cs → ∀ K n cs',
    VE.Discourse.compatibleChoices K (VE.Scope.setShapes D) n = .ok cs' →
      (∀ c ∈ cs', c ∈ cs) ∧ (K.constraints = [] → cs' = cs)) ∧
  ∀ D, VE.Scope.governedSetUnits D ≠ [] → ∀ cs, VE.Scope.setChoices D = .ok cs → ∀ ch ∈ cs, ∀ e,
    VE.Scope.governChoice D ch = .error e → (VE.Scope.governSets D).isOk = false

/-- Acts' own faithfulness (act-phrases 6, `elaborate_faithful`; `IntendedActs` is act-phrases'): the elaborated
document's intended reading is the table's reading of the source. -/
def ActsFaithful : Prop :=
  ∀ (D : VE.Acts.ActsDoc) (U' : VE.NormDefaults.UDoc), VE.Acts.elaborate D = .ok U' →
    ∀ S : VE.Structure.{u}, VE.Norms.holdsCatala U'.D.T S ↔ VE.Acts.IntendedActs D S

/-- Acts' semantic preservation: a document none of whose predicates splits elaborates to itself (act-phrases'
`elaborate_identity`). -/
def ActsPreserves : Prop :=
  ∀ (D : VE.Acts.ActsDoc) (U' : VE.NormDefaults.UDoc), VE.Acts.elaborate D = .ok U' →
    (∀ p, VE.Acts.splitAtoms D p = none) → U' = D.U

/-- (pc-fid-rev, PC-4b, B6) The ordered pipeline theorem for any stack `s`: the document mode runs `s`'s case
rewriters in stack order, then the chain; with `scope@0` in `s` it folds GOVERN's governors, decoded from GOVERN's
own input (the case after the rewriters ranked before it). `docRewritersDiscourse` (3.7) holds every case rewriter. -/
def StackRuns (s : List String) : Prop :=
  ∀ j ans, VE.Service.Document.checkDocSets j = .ok ans →
    stackOf profileTable (VE.Service.Document.profilesOf j) = s →
    ∃ j' a, pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewritersDiscourse) j = .ok j' ∧
      VE.Service.Document.checkCore j' = .ok a ∧
      ("scope@0" ∈ s → ∃ jg D, pipeline ((s.takeWhile (· != "scope@0")).filterMap docRewritersDiscourse) j = .ok jg ∧
        VE.Scope.decodeScope jg = .ok D ∧ ans = VE.Scope.foldGovernors D a) ∧
      ("scope@0" ∉ s → ans = a)

/-- (pc-fid-rev) SUPERPOSE's own faithfulness: main's `superpose_faithful` (Readings/Faithful.lean:232) as a
proposition. Under every compatible choice the superposed document has the choice document's values. -/
def ReadingsFaithful : Prop :=
  ∀ (D : VE.Readings.Doc), VE.Readings.WellFormedDoc D = true → D.chain ≠ .rights →
    VE.Readings.superposable D = true → ∀ (c : VE.Readings.Choice), VE.Readings.Compatible D c →
      ∀ (S : VE.Structure.{u}), VE.Readings.Encodes D c S → VE.Norms.Sat S (VE.Readings.choicePremises D) →
        ∀ r ∈ (VE.Rights.correlate (VE.Readings.choiceDoc D c).1).T.regulated, ∀ vs : List S.Carrier,
          VE.SoftNorms.ValueSoft (VE.Rights.correlate (VE.Readings.sup D).1) r S vs =
            VE.SoftNorms.ValueSoft (VE.Rights.correlate (VE.Readings.choiceDoc D c).1) r (VE.Readings.pull D c S) vs

/-- Proved (in the stub): it is main's theorem. -/
theorem readingsFaithful : ReadingsFaithful.{u}

/-- (PC-4b) Each rewriter's own faithfulness and preservation, stated once. -/
def RewriterFacts : String → Prop
  | "scope@0" => ScopeFaithful ∧ ScopePreserves
  | "acts@0" => ActsFaithful.{u} ∧ ActsPreserves
  | "ve.discourse@1" => DiscourseFaithful.{u} ∧ DiscoursePreserves
  | "readings@1" => ReadingsFaithful.{u}
  | _ => False

-- S4's names, as PC-7b and PC-4b read them (stubs; pc-fid-rev review)
/-- (PC-7b) The environment and manifest `resolveCase` resolves a case under: its front matter's. -/
def VE.Discourse.caseManifest (j : Json) : Except String (VE.Environment × VE.Discourse.Manifest)
/-- (PC-4b) The content a governor's effect carries: a `frame`'s part, a `reguard`'s or a `carve_out`'s condition;
none for `precedes`, `yields` and `title`. -/
def VE.Discourse.effectContent (e : VE.Scope.Effect) : Option VE.Compose.Content
/-- (PC-4b) The effect with the content it carries replaced by `c`. -/
def VE.Discourse.withEffectContent (e : VE.Scope.Effect) (c : VE.Compose.Content) : VE.Scope.Effect

/-- (PC-4b) RESOLVE on a governor's effect: the source effect after `resolveContent` at the governor's unit, under
the case's environment and manifest; an effect that carries no content is unchanged. -/
def ResolvedEffect (j : Json) (g₀ g : VE.Scope.Governor) : Prop :=
  match VE.Discourse.effectContent g₀.effect with
  | none => g.effect = g₀.effect
  | some c => ∃ E K c', VE.Discourse.caseManifest j = .ok (E, K) ∧
      VE.Discourse.resolveContent E K g₀.unit c = .ok c' ∧ g.effect = VE.Discourse.withEffectContent g₀.effect c'

/-- (PC-4b) Each pair's interaction lemma, over every case: what the later rewriter reads once the earlier one has
run, as a function of what it read before. A pair with no entry has none, so no stack holding it has `RouteFacts`.
The first entry is PC-6b's `SplitReach` over every case: it keeps each governor's id, unit, recorded reach and effect
and maps its reach through the split (the effect clause, DRI 2026-10-30, item 1); the third follows from PC-7b's
`resolve_then_split` through `resolveCase`; the fourth (pc-fid-rev review) is PC-4b's: it keeps what GOVERN reads of
each governor, its id, unit, recorded reach and reach, as `SplitReach` does, and resolves its effect at its unit
(`ResolvedEffect`), so PC-7b's `resolve_then_govern` is a projection of its first conjunct; the fifth is PC-7c's
(3.7), the sixth PC-6c's (3.6). -/
def PairFacts : String × String → Prop
  | ("acts@0", "scope@0") => ∀ j j₁ M D₀ D, actsRewriter.run j = .ok j₁ → VE.Acts.splitMapOfCase j = .ok M →
      VE.Scope.decodeScope j = .ok D₀ → VE.Scope.decodeScope j₁ = .ok D → SplitReach M D₀ D
  | ("scope@0", "readings@1") => ScopeSetsFaithful
  | ("ve.discourse@1", "acts@0") => ∀ j j₁, discourseRewriter.run j = .ok j₁ →
      (VE.Acts.splitMapOfCase j₁).map (·.rules) = (VE.Acts.splitMapOfCase j).map (·.rules)
  | ("ve.discourse@1", "scope@0") => ∀ j j₁, discourseRewriter.run j = .ok j₁ →
      (VE.Scope.decodeScope j₁).map (fun D =>
          (D.layout.map (·.id), D.governors.map (fun g => (g.id, g.unit, g.units, g.reach)))) =
        (VE.Scope.decodeScope j).map (fun D =>
          (D.layout.map (·.id), D.governors.map (fun g => (g.id, g.unit, g.units, g.reach)))) ∧
      ("ve.discourse@1" ∈ VE.Service.Document.profilesOf j → ∀ D₀ D, VE.Scope.decodeScope j = .ok D₀ →
        VE.Scope.decodeScope j₁ = .ok D → ∀ g ∈ D.governors, ∀ g₀ ∈ D₀.governors, g.id = g₀.id →
          ResolvedEffect j g₀ g)
  | ("ve.discourse@1", "readings@1") => ResolveKeepsSets
  | ("acts@0", "readings@1") => ActsChoiceFaithful
  | _ => False

/-- What a listed stack's admission rests on: its run statement, and each rewriter's faithfulness and preservation.
`readings@1` has no case rewriter in the document mode (7, choice 2); its stack adds GOVERN's per-choice facts.
The third entry is PC-6b's (3.6), the fourth and fifth PC-7b's (3.7); each is written here once, and its stack is
listed only by the batch that proves it. (pc-fid-rev, PC-4b) A stack with no entry of its own has the generic
clause: its run statement, each rewriter's facts, and each pair's lemma at positions `i < j`. -/
def RouteFacts : List String → Prop
  | ["scope@0"] => ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves
  | ["scope@0", "readings@1"] => ScopeRuns ∧ ScopeFaithful ∧ ScopePreserves ∧ ScopeSetsFaithful
  | ["acts@0", "scope@0"] =>                     -- the constitution set's ordered pipeline (3.6, PC-6b)
      ActsScopeRuns ∧ ActsFaithful.{u} ∧ ActsPreserves ∧ ScopeFaithful ∧ ScopePreserves
  | ["ve.discourse@1", "acts@0"] =>              -- RESOLVE, then acts' split (3.7, PC-7b)
      DiscourseActsRuns ∧ DiscourseFaithful.{u} ∧ DiscoursePreserves ∧ ActsFaithful.{u} ∧ ActsPreserves
  | ["ve.discourse@1", "scope@0"] =>             -- RESOLVE, then GOVERN (3.7, PC-7b)
      DiscourseScopeRuns ∧ DiscourseFaithful.{u} ∧ DiscoursePreserves ∧ ScopeFaithful ∧ ScopePreserves
  | s =>                                         -- (PC-4b) every other stack
      2 ≤ s.length ∧ StackRuns s ∧ (∀ p ∈ s, RewriterFacts.{u} p) ∧ (∀ x ∈ Matrix.stackPairs s, PairFacts x)

-- lean/VE/Compose/Stack.lean (1.3), so that `Compose/Matrix.lean` reads it without importing this file
/-- The stacks the document mode admits. `["acts@0", "scope@0"]` joins only with PC-6b, which proves
`ActsScopeRuns` (3.6); `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]` with PC-7b (3.7); the
entries of the listing rule below with PC-4b, PC-6c and PC-7c (pc-fid-rev). -/
def listedStacks : List (List String) := [["scope@0"], ["scope@0", "readings@1"]]

/-- M1 (evidence). Every listed stack has its route facts. -/
theorem listed_evidence : ∀ s ∈ listedStacks, RouteFacts s

/-- (PC-4b) The generic entry from its parts: a stack of three or more rewriters has its route facts when the
document mode runs it, each of its rewriters has its facts and each of its pairs, at positions `i < j`, its lemma. -/
theorem stack_evidence (s : List String) (h3 : 3 ≤ s.length) (hr : StackRuns s)
    (hp : ∀ p ∈ s, RewriterFacts.{u} p) (hx : ∀ x ∈ Matrix.stackPairs s, PairFacts x) : RouteFacts.{u} s

/-- (PC-4b) The document mode runs every stack: one pipeline call over its case rewriters, in stack order. -/
theorem stackRuns_all (s : List String) : StackRuns s

/-- What an owned `.layer` profile other than `documents@1` and `judgments@0` rests on in a list that contains it:
its own transparency theorem over that whole list, added by its row batch (1.2). None on main. -/
def LayerFacts : String → List String → Prop
  | _, _ => False

/-- (PC-4) Each entry of `Matrix.layerCovers` has its layer's facts on every list it covers. On main
`layerCovers = []`, so it holds by `simp` (proved in the stub); a row batch that adds an entry proves its case. -/
theorem layer_evidence : ∀ x ∈ Matrix.layerCovers, ∀ ps, x.2 ps = true → LayerFacts x.1 ps

/-- (PC-4) M1 for layers: a list the layer rule passes (3.4) has, for each other layer it lists, that layer's facts. -/
theorem layer_admitted (ps : List String) (hd : Matrix.layerRule ps = none) :
    ∀ l ∈ ps, Matrix.otherLayer profileTable l = true → LayerFacts l ps
```

`LayerFacts`, `layer_evidence` and `layer_admitted` are in `Contract.lean`, above `Document.lean`, because a layer's
theorem is about the document mode (for `purposes@0`, purpose-explanation's `checkDocPurposes_base` at that list).
`layerCovers` is a table of lists (`List String → Bool`) in `Matrix.lean`, below it (3.4).

**M1 covers every listed set, not only pairs.** Draft 1's sentence "None needs a lemma of its own beyond its pairs"
is deleted. `documentRefusal` decides on the whole list, so each set the baselines need names the theorem for its
whole stack (the plan's 3.3 set table). The constitution set `soft + judgments + scope + acts` applies two
rewriters in a fixed order, so it needs `ActsScopeRuns`: the acts × scope `SplitMap` lemma (`SplitReach`, a
conjunct of `ActsScopeRuns`, 3.6, which also keeps each governor's effect as written) and scope's own facts combine
only through that ordered statement.

**Any number of rewriters (pc-fid-rev, PC-4b, B6).** The pilot's one document lists four rewriters,
`["ve.discourse@1", "acts@0", "scope@0", "readings@1"]` in stack order (F4.12), and no entry covered it. Listing
stacks one by one does not scale, so the general rule is one clause of `RouteFacts` for every stack with no entry of
its own, built from three parts, each a proposition:
- **the whole stack's ordered pipeline theorem**, `StackRuns s`: the document mode's answer is the pipeline of `s`'s
  case rewriters, in rank order, then the chain, then scope's fold where `s` holds `scope@0`. It is one theorem for
  every `s` (`stackRuns_all`), proved once PC-4b writes the document mode's one pipeline call. This is the lemma
  "beyond its pairs" that ruling 1(b) requires: a stack is not admitted by its pairs alone;
- **each rewriter's own facts**, `RewriterFacts`, stated once per rewriter: the conjuncts every two-rewriter entry
  already carries, and SUPERPOSE's `superpose_faithful`, which main proves (`readingsFaithful`, proved in the stub);
- **each pair's interaction lemma**, `PairFacts`, at every pair of positions `i < j` (`Matrix.stackPairs`, which
  `Contract.lean` reads through `Service/Document.lean`'s import of `Compose/Matrix.lean`), not only adjacent ones.

*Why every pair, and why that is enough.* A rewriter reads a fixed part of the case: GOVERN the unit ids, the layout
and each governor's id, unit, reach, recorded reach and effect (`ScopeFaithful` reads `g.reach` and `g.effect`; so the
acts × scope lemma, `SplitReach`, keeps the id, unit, recorded reach and effect and maps the reach through the split,
DRI 2026-10-30, item 1, and the discourse × scope lemma keeps the first four and gives the effect as the source's
resolved at the governor's unit, `ResolvedEffect`, when `ve.discourse@1` is listed and RESOLVE runs); acts' split the
rule names and the act phrases; SUPERPOSE the reading sets' shapes, the couplings and the narrowings. Each
rewriter's faithfulness is stated over its own input. Rewriter `j` runs on the
output of every rewriter ranked before it, so what it reads must be known as a function of what it would read on the
source, through each earlier rewriter in turn: pair `(i, j)` gives that step for `i`. An adjacent pair `(j-1, j)`
does not say what rewriter `j-2` did to `j`'s reads, so adjacent pairs alone are not enough. Every pair lemma is
stated over every case, with no hypothesis on the other profiles of the list. So the lemma for `(i, j)` also holds on
`i`'s actual input, the output of the rewriters before `i`, and by induction along the pipeline `j`'s reads on its
input are the source's, transported by the pair lemmas. `j`'s faithfulness then says that its output means what the
source intends, so the stack's answer is the composition of its parts' answers. A triple has no interaction of its
own: each rewriter's reads are a function of its input alone. This is the splitting-sequence argument of 2.1 (no
step reads a later step's names), with each pair's reads written out. `stack_evidence` is the statement, and
`listed_evidence` uses it for every listed stack of three or more rewriters.

*The listing rule (conservative; ruling 10 and 1(b) kept).* A stack of three or more rewriters is admitted only when
a batch lists it in `listedStacks`, with its case of `listed_evidence` given by `stack_evidence`. Its pairs being
listed does not admit it (F4.13: the whole-stack text, E1s, exactly as F4.7). From PC-4b on, a batch that lists a
pair also lists, in the same commit, every stack of three or more rewriters whose pairs are then all listed, so
`listedStacks` stays closed under its pairs (F4.14). Named: PC-4b lists `["ve.discourse@1", "acts@0", "scope@0"]`
(F4.7's triple); PC-6c `["acts@0", "scope@0", "readings@1"]`; PC-7c `["ve.discourse@1", "scope@0", "readings@1"]`;
whichever of PC-6c and PC-7c merges second `["ve.discourse@1", "acts@0", "readings@1"]` and the pilot document's
`["ve.discourse@1", "acts@0", "scope@0", "readings@1"]`. The stack rule (3.4, `stackRefusalIn`) is unchanged: it
names the first unlisted pair, or the whole stack when every pair is listed and the stack is not.

**Layers carry to larger stacks only through their own whole-list theorem.** `judgments@0` has no rewriter. It
composes with every admitted list because PC-1's transparency theorem (1.7) is stated on `checkDocSets` for every
list, not per pair. Every other `.layer` profile composes only through its `LayerFacts` entry, stated for every
admitted list that contains it, and PC-4's layer rule refuses each list its entry does not cover (1.2, 3.4).

### 1.6 Packs: G1 and G4 through SupPacks' join, and G1b (PC-3; G1b owned by PK-1's owner)

G1 and G4 are not restated. Superposed readings use `Readings/SupPacks.lean`'s join, under which `Choice_D` and
PK-1's `X` form one premise list, `slotUnder D A ++ Packs.X qs`. The composed statement is
`superpose_all_extra` at `Q := Packs.X qs`, discharged by `transfers_X`. PLANS-INDEX D14's "joined only by" is
now the rule. Off readings, G1 is `acceptanceX` at `X := Packs.X qs`, applied directly (PC-2a).

```lean
-- lean/VE/Compose/Contract.lean (namespace VE.Readings, opens as SupExtra.lean)
theorem composed_superpose_all (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (qs : List VE.NormDefaults.Packs.Pack) (Qc : VE.NormDefaults.Packs.Pack → Choice → List VE.Formula)
    (hq : ∀ p ∈ qs, Transfers.{u} D (p.labelled.map (·.2)) (Qc p))
    (hQw : VE.Compose.SlotWellFormed (correlate (sup D).1) (VE.NormDefaults.Packs.X qs))
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ VE.NormDefaults.Packs.X qs))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra D A (VE.NormDefaults.Packs.X qs) Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc D c).1)
      (VE.Rights.limPremises (choiceDoc D c).1 ++ qs.flatMap (fun p => Qc p c)) B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc D c).1 B) []
```

**G1b, vocabulary packs.** Its owner is PK-1's owner (the RD-9 composition owner, SYNTHESIS 2.1), in a new module
beside `PacksLegacy.lean` (`lean/VE/NormDefaults/PacksVocab.lean`). `Packs.lean` is not touched by this plan. G1b is
needed before the first pack with non-empty `decls` (N2). Attitudes' pack is `.constraint` with `decls := []` (its
names are declared in `envAtt`, RF-5); events' pack kind matches the pattern et-4 chooses (C8).

Draft 3's G1b had two defects (pc-d2, edit 4). `acceptanceXV` took any `qs`, while only `assembleIn` checks that a
pack's names are fresh (`Packs.lean:100`). So a pack could redeclare a predicate `p` the document defines and
supply `¬p(a)`: the certificate replayed, the restricted base (which forgets `p`'s new declaration) satisfied the
pack's premise, and the expansion still made `p(a)` true. And its `EntailsXV` kept `BaseAdmissibleX` and
`DocumentExpansion`, which require admissibility over the old vocabulary. `Structure.Admissible`
(`Semantics.lean:24`) makes every predicate the environment does not declare empty, so a fresh pack predicate was
empty in every structure considered: G1b held vacuously on exactly the packs it is for, and F3.2 had no model.
Draft 4 adds assembly's freshness as a hypothesis, and replaces (does not conjoin) the old-vocabulary admissibility
inside the base and expansion predicates. The base is stated over `envX U qs`, the expansion over `fullEnvX U qs`,
and the background, filling and expansion obligations are kept.

```lean
-- lean/VE/NormDefaults/PacksVocab.lean (new; PK-1's owner)
namespace VE.NormDefaults.Packs

/-- The complete environment extended by the packs' names. -/
def fullEnvX (U : UDoc) (qs : List Pack) : VE.Environment :=
  extendEnv (fullEnv U) (qs.flatMap (·.decls)) (qs.flatMap (·.consts))

/-- A base over the packs' vocabulary: `BaseAdmissibleX`'s obligations (the background base, the filling premises,
`X`), with its admissibility over `envX U qs` in place of `envAt (fill U) 0`. -/
def BaseAdmissibleXV (U : UDoc) (qs : List Pack) (B : VE.Structure.{u}) : Prop :=
  B.Admissible (envX U qs) ∧ Sat B (VE.Norms.backgroundBase (fill U)) ∧ Sat B (VE.NormDefaults.fillPremises U) ∧
    Sat B (X qs)

/-- An expansion of `B` to the complete vocabulary with the packs' names: `DocumentExpansion`'s obligations (the
background and the layer premises), with its admissibility over `fullEnvX U qs` in place of
`envAt (fill U) (size (fill U))`. -/
def DocumentExpansionXV (U : UDoc) (qs : List Pack) (B S : VE.Structure.{u}) : Prop :=
  restrictAll (fill U).T S = B ∧ S.Admissible (fullEnvX U qs) ∧
    Sat S (VE.Norms.background (fill U) ++ VE.Norms.elaborate (fill U).T)

/-- `EntailsX` over the extended vocabulary. -/
def EntailsXV (U : UDoc) (qs : List Pack) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, BaseAdmissibleXV U qs (restrictAll (fill U).T S) →
    DocumentExpansionXV U qs (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

/-- G1b, acceptance, under assembly's freshness: no pack name is declared in `fullEnv U`. -/
theorem acceptanceXV (U : UDoc) (h : VE.NormDefaults.WellFormedU U = true) (qs : List Pack)
    (hfresh : ∀ n ∈ names qs, declaredIn (fullEnv U) n = false)
    (hX : ∀ a ∈ X qs, a.WellFormed (envX U qs) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (fullEnvX U qs) (VE.NormDefaults.Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsXV.{u} U qs Γ φ

/-- On constraint packs G1b is G1. -/
theorem entailsXV_constraint (U : UDoc) (qs : List Pack) (hk : ∀ p ∈ qs, p.decls = [] ∧ p.consts = [])
    (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsXV.{u} U qs Γ φ ↔ VE.NormDefaults.EntailsX.{u} U (X qs) Γ φ

/-- G1b, countermodels: a conflict-free base over the packs' vocabulary that satisfies `Γ` and refutes `φ`
refutes the entailment (the vocabulary analogue of `norms_route_countermodel`, `Norms/Layer.lean:285`). -/
theorem countermodelXV (U : UDoc) (h : VE.NormDefaults.WellFormedU U = true) (qs : List Pack)
    (hfresh : ∀ n ∈ names qs, declaredIn (fullEnv U) n = false)
    (hc : ∀ B : VE.Structure.{u}, BaseAdmissibleXV U qs B → VE.Norms.ConflictFree (fill U) B)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (envX U qs) [])
    (hφ : φ.WellFormed (envX U qs) []) (B : VE.Structure.{u}) (hB : BaseAdmissibleXV U qs B) (hs : Sat B Γ)
    (hn : ¬ φ.denote B []) : ¬ EntailsXV.{u} U qs Γ φ
```

`names qs` and `declaredIn` are `Packs.lean`'s (`:61`, `:86`); `hfresh` is the check `assembleIn` makes with
`E := fullEnv U` (`:101`, through `assemble`, `:110`), so every pack list `assemble` returns satisfies it. A pack that breaks it is
refused before any certificate, with `assemble`'s text (row 18 of 4, F3.2b). The fixtures are F3.2 (acceptance),
F3.2b (the collision), F3.2c (a satisfiable positive fresh predicate) and F3.2d (the vocabulary countermodel).
`entailsXV_constraint` keeps its statement: on constraint packs `envX U qs = envAt (fill U) 0` and
`fullEnvX U qs = fullEnv U`, so the new predicates are `BaseAdmissibleX` and `DocumentExpansion`.

If et-4 lands an acceptance instance for the events pack's `date__` names, `acceptanceXV` generalises it and the
instance is deleted in its favour.

### 1.7 Layers: success-only transparency (G3, PC-1)

Draft 1 compared the whole `Except` answer. That is false: the judgments layer refuses on its own,
`JudgmentListedUnused` first (`Judgments/Status.lean:157`, raised through `Document.lean:1811`). The restated G3
compares successes only. It is stated on `checkDocSets`, the document mode's entry, for every list, over
**comparison pairs**: a case with the layer and its twin without it, where
- the two have the same semantic content, and their profiles differ only by `judgments@0`;
- neither states a unit `status` (2b);
- each identity the case states is exchanged in the twin for the same content's identity under the twin's
  environment (2a).

On a comparison pair:
- an answer the document mode gives with the layer, it also gives without it, with equal verdict fields. Each
  unit's status is unchanged or OPEN. The one exception is the W2 check that the layer relaxes, which is named.
- a refusal with the layer is either the same refusal without it, or one of a named list of the layer's own
  refusals.

**Validation of the original request is a separate matter from transparency.** The original request's own checks
refuse an authored unit status or identity that is wrong: `invalid unit status` and `unit status contradicts
content, meaning, or active reading set` (`Document.lean:1312`, `:1818`), and the identity checks below. Those
refusals are fixtures of the original request (F1.3j, F1.3k), never layer refusals (2d). For identities, 2a's lemma
says one more thing: an authored identity is refused with the layer exactly when it is refused in the twin (F1.3b,
F1.3f).

**2a. Identities are exchanged, not erased or recomputed.** Removing `judgments@0` changes the environment's
profiles and identity. Every identity Lean digests under them changes too: a unit's or a reading's `meaning_id`
(`Route.Wire.meaningId`, `Route/Wire.lean:272`, under `identityVersion profiles` and the `environment_id`), and a
model's key (`Loader.modelId`, `Discourse/Loader.lean:436`). Take each stated unit `meaning_id`, reading
`meaning_id`, model key and `admission.distinguishing_models` reference whose content decodes; a reference's
content is the model it names. Let `v₁` be the identity Lean computes for that content under the case's
environment, and `v₂` the identity under the twin's. The twin applies `swap v₁ v₂`: `v₁` becomes `v₂`, `v₂`
becomes `v₁`, and any other value is kept. Every other stated value is kept unchanged. On the stated values,
`swap v₁ v₂ x` is `v₂` exactly when `x` is `v₁` (`swap_correct`, under the amendment's hypothesis below). So a
stated identity is correct in the twin exactly when it is correct with the layer (`withoutJudgments_ids`), and the
checks at `Document.lean:1310`, `Discourse/Loader.lean:466` and `Loader.lean:547-555` give the same answer in the
same fault order on both sides, with no hash-collision hypothesis.

**The G3 amendment (DRI, synthesis round 2, DECISIONS item 3: an amendment to ruling item 2a, before PC-1).**
Model keys are object keys, and a reference that names no model keeps its value. So the exchange can send two
strings of one reading set to one value: a correct key `v₁(d)` becomes `v₂(d)` while another key, or a reference
that names no model, already reads `v₂(d)` (F1.3l). The exchange therefore applies only when `swap` is injective on
all stated values together: model keys and `distinguishing_models` references, dangling references included
(`swapInjective`). Lean decides this before the transformation. A request where it is not injective (a stated
value, resolved or not, equals the other environment's identity of a different stated value) is refused by
validation on both sides, with the same text and the same fault order (`checkDocSets_swapClash`). That refusal is
never a layer refusal: it is not added to `layerRefusal`'s whitelist (2d stands). G3, `swap_correct` and
`withoutJudgments_ids` are stated under this hypothesis. F1.3l stays the regression, expected as refused on both
sides by that validation, and F1.3l and the other ruling-2g fixtures stay selected in PC-1.

**Where the validation runs, and its text (pc-d2, edit 2).** The text is `swapClash` (row 16 of 4):

`distinguishing model ids and references do not map one to one between the environments with and without judgments@0`

The check is the first line of `checkDocSets` and of `checkDoc`, before the gate (`gateOf`) and before every other
check, on every request: with `judgments@0` and without it (`clashRefusal`, `checkDocSets_clashFirst`). Both sides
read the same two environments. `statedPairs` computes each content's identity under `layerProfiles j` (the
profiles with `judgments@0` in its sorted place) and under `plainProfiles j` (the profiles without it), and a
request and its twin have the same `plainProfiles`. When `swapInjective j` is false, the twin keeps the stated
values as written (`withoutJudgments`), so its exchange is not one-to-one either (`swapInjective_twin`), and both
sides answer `swapClash` first. If the check ran after the gate, F1.3m (F1.3l without `documents@1`) would answer
the gate's text with the layer, `UnsupportedProfile: judgments@0 requires documents@1`, and `swapClash` without it.
`layerRefusal` accepts that gate text, so `checkDocSets_swapClash` would be false.

**The check is symmetric (pc-d2 FIX round 2, DRI 2026-10-29: `manage-agents/reviews/dri-decisions-20261029-pc-d2-r2.md`,
item 1).** The second conjunct of `swapInjective` can fail on the twin of a request whose own exchange is one-to-one
(section 9, open point 1, now resolved). A check that read only the request would then leave G3 requiring the
request's own answer from its twin, while `checkDocSets_swapClash` requires that twin to answer `swapClash`. So the
check reads both sides. On a request that lists `judgments@0`, `clashRefusal` answers `swapClash` when `swapInjective
j` is false or when `swapInjective (withoutJudgments j)` is false, the twin being G3's (`clashRefusalOf`;
`clashRefusal_some` states exactly when it refuses). The twin lists no `judgments@0`, so its own check reads its own
exchange, and that exchange is not one-to-one in both cases: by `swapInjective_twin` when the request's is not, and
as given when only the twin's is not. So this check refuses a request with the layer exactly when it refuses its
twin, and then both answer `swapClash` first (`checkDocSets_swapClash`, restated with the symmetric hypothesis). G3
keeps its statement, with its one hypothesis `hk`: on a request with `hk` whose twin is not one-to-one, both sides
answer `swapClash`, and G3's refusal clause holds by its first disjunct. F1.3o is the fixture: the open point's two
requests and their common twin each answer row 16's text. The check refuses more than a one-sided check, and admits
nothing that one refuses.

**A change to plain requests (PC-1).** A request without `judgments@0` now runs the same check against the
environment with `judgments@0` added. One whose stated model keys and references are not one-to-one between the two
environments is refused with `swapClash` before the gate, where today it reaches the later checks. PC-1 owns this
change; F1.3m's twin is its fixture, and every plain request of `tests/data` keeps its answer (F1.3n). A plain
request is no G3 case and has no twin, so its check reads its own exchange alone; the symmetric check changes no
plain request's answer (7, choice 24).

**2b. Authored unit statuses are omitted on both sides.** G3 takes `noUnitStatus j`. An authored status restates
one side's computed answer: F1.1's unit is OPEN with the layer and CHECKED without it, so one authored status is
valid on one side only.

**2c. Omitting statuses loses no answer.** Take an original request with `judgments@0` that succeeds. Its
status-omitted form succeeds with equal verdict fields and equal computed statuses (`checkDocSets_withoutStatuses`,
F1.3i). So G3's domain keeps every answer the layer gives.

**2d. `layerRefusal` is narrow.** `decodedEnvironment` gates a list only when it lists a document layer
(`Document.lean:610-611`), so the twin is never gated there (F1.3d). `layerRefusal` therefore accepts, beside the
layer's own codes and the document-mode texts that name the layer (until PC-4 and PC-5 replace those, 4), exactly
the gate texts of `judgments@0`'s rows, read from `profileTable`, and nothing else. It does not accept `unit status
contradicts content, meaning, or active reading set`, `invalid unit status`, or any identity-mismatch text. Those
are validation refusals of the original request, never judgments-layer refusals.

**2e. `verdictFields` drops exactly the environment-dependent identities**, besides the fields the layer may
change (`judgments`, `document_id`, `source_id`, `coverage`, every unit's `status`). The identities are named one
by one:
- each unit's `meaning_id`;
- each reading's `meaning_id` in the reading sets an answer echoes (the front matter's `reading_sets`, as
  `Document.lean:1599` passes them on);
- each echoed model key and `distinguishing_models` reference.

No other field is dropped.

```lean
-- lean/VE/Judgments/Chain.lean and lean/VE/Service/Document.lean (PC-1; owner judgment-terms)
namespace VE.Service.Document

/-- The transposition of `a` and `b` (2a): `a` becomes `b`, `b` becomes `a`, any other value is kept. -/
def swap (a b x : String) : String := if x == a then b else if x == b then a else x

/-- A request's profiles without `judgments@0`: its twin's (2a). -/
def plainProfiles (j : Json) : List String := (profilesOf j).filter (· != "judgments@0")

/-- A request's profiles with `judgments@0` in its sorted place: on a request that lists `judgments@0` with sorted,
unique profiles (as the envelope requires, `Route/Gate.lean:72`), its own. A request and its twin have the same
`plainProfiles`, so the same two environments. -/
def layerProfiles (j : Json) : List String := ("judgments@0" :: plainProfiles j).mergeSort fun a b => decide (a ≤ b)

/-- The stated values the exchange reads, over every reading set of the case: each model key and each
`admission.distinguishing_models` reference, dangling references included (the G3 amendment). -/
def statedIds (j : Json) : List String

/-- The triples `(x, v₁, v₂)` of 2a: each stated value `x` whose content decodes (a reference's content is the
model it names), with the identity Lean computes for that content under `layerProfiles j` (`v₁`; on a request with
`judgments@0`, its own environment) and under `plainProfiles j` (`v₂`; the twin's). -/
def statedPairs (j : Json) : List (String × String × String)

/-- The exchange of 2a on one stated value: `swap v₁ v₂` for its pair, every other value kept. -/
def exchange (j : Json) (x : String) : String

/-- The G3 amendment on given values, pairs and exchange: the exchange is one-to-one on the values, and no value,
resolved or not, equals the twin environment's identity (`v₂`) of a different stated value. -/
def swapInjectiveOf (ids : List String) (pairs : List (String × String × String)) (ex : String → String) : Bool :=
  ids.all (fun x => ids.all fun y => x == y || ex x != ex y) &&
    pairs.all fun (y, _, v₂) => ids.all fun x => x == y || x != v₂

/-- The G3 amendment, on a request: decided before the transformation, on every request, plain ones included. -/
def swapInjective (j : Json) : Bool := swapInjectiveOf (statedIds j) (statedPairs j) (exchange j)

/-- 2a, on one value, under the amendment: a stated value is exchanged to the twin's identity of a content exactly
when it is the case's identity of that content. -/
theorem swap_correct (j : Json) (hk : swapInjective j = true) (v₁ v₂ x : String) (hp : (x, v₁, v₂) ∈ statedPairs j)
    (hx : x ∈ statedIds j) : (exchange j x == v₂) = (x == v₁)

/-- A place where a case states an identity, read in the case as written: unit `i`'s `meaning_id`; reading `r`'s
`meaning_id` in reading set `s`; the model stated under key `k` in set `s`; reading `r`'s reference for reading `o`
in set `s`'s `admission.distinguishing_models`. -/
inductive IdSite
  | unit (i : Nat) | reading (s r : Nat) | model (s : Nat) (k : String) | reference (s r : Nat) (o : String)

/-- The case with `judgments@0` taken out of its document's environment, each stated identity whose content
decodes exchanged by `swap v₁ v₂` (2a) when `swapInjective j`, every other byte as written. -/
def withoutJudgments (j : Json) : Json

/-- A site's place in the twin: a model's key is exchanged; every other site keeps its place. -/
def IdSite.twin (j : Json) : IdSite → IdSite

/-- Whether the identity a case states at a site is correct: equal to the identity Lean computes for its content
under the case's environment (`Route.Wire.meaningId`, `Loader.modelId`); `false` when the content does not decode;
`none` when the case states nothing there. -/
def correctAt (j : Json) : IdSite → Option Bool

/-- 2a. A stated identity is correct in the twin exactly when it is correct with the layer. -/
theorem withoutJudgments_ids (j : Json) (hk : swapInjective j = true) (s : IdSite) :
    correctAt (withoutJudgments j) (s.twin j) = correctAt j s

/-- No unit of the case states a `status` (2b). -/
def noUnitStatus (j : Json) : Bool

/-- The case with every unit's authored `status` removed, every other byte as written (2c). -/
def withoutStatuses (j : Json) : Json

/-- An answer without the fields the layer may change (`judgments`, `document_id`, `source_id`, `coverage`, every
unit's `status`) and without exactly the environment-dependent identities (2e): each unit's `meaning_id`, each
echoed reading's `meaning_id`, each echoed model key and `distinguishing_models` reference. -/
def verdictFields (a : Json) : Json

/-- Each unit's id and status, in unit order. -/
def unitStatuses (a : Json) : List (String × String)

/-- The layer's own refusal codes, in judgment-terms 8.2's order, `JudgmentListedUnused` first. -/
def judgmentCodes : List String :=
  ["JudgmentListedUnused", "JudgmentNotListed", "JudgmentNotChecked", "JudgmentUnbound", "JudgmentArguments",
   "JudgmentRegulated", "JudgmentCriterionAsUnit", "JudgmentDecider"]

/-- The gate texts of `judgments@0`'s rows, read from `profileTable` (2d): each requirement's, then each refusal's. -/
def judgmentGateTexts : List String :=
  (VE.Compose.profileTable.filter (·.profile == "judgments@0")).flatMap fun r =>
    (r.requires.map (VE.Compose.needText r) ++ r.refuses.map (·.2)).map VE.Compose.unsupported

/-- A refusal of the layer: one of its codes, a document-mode refusal that names it (until PC-4 and PC-5 replace
those, 4), or exactly a gate text of its rows (2d). -/
def layerRefusal (e : String) : Bool :=
  judgmentCodes.any (fun c => e.startsWith (c ++ ": ")) || e.startsWith "CheckerUnavailable: judgments@0 with " ||
    judgmentGateTexts.contains e

/-- The W2 check the layer relaxes (judgment-terms 8.2, row (W2): repeated `arguments`). -/
def layerRelaxes : List String := ["invalid open-term arguments"]

/-- G3, over comparison pairs (2a, 2b). -/
theorem checkDocSets_judgments_transparent (j : Json) (hj : "judgments@0" ∈ profilesOf j)
    (hs : noUnitStatus j = true) (hk : swapInjective j = true) :
    (∀ a, checkDocSets j = .ok a →
      (∃ b, checkDocSets (withoutJudgments j) = .ok b ∧ verdictFields a = verdictFields b ∧
        (unitStatuses a).map (·.1) = (unitStatuses b).map (·.1) ∧
        ∀ x ∈ (unitStatuses a).zip (unitStatuses b), x.1.2 = x.2.2 ∨ x.1.2 = "OPEN") ∨
      ∃ e ∈ layerRelaxes, checkDocSets (withoutJudgments j) = .error e) ∧
    (∀ e, checkDocSets j = .error e → checkDocSets (withoutJudgments j) = .error e ∨ layerRefusal e = true)

/-- The validation text of a request whose exchange is not one-to-one (the G3 amendment; row 16 of 4). -/
def swapClash : String :=
  "distinguishing model ids and references do not map one to one between the environments with and without judgments@0"

/-- The symmetric check on given decisions (pc-d2 round 2): `swapClash` unless the request's exchange is one-to-one
and, when the request has a twin, the twin's is too. -/
def clashRefusalOf (own : Bool) (twin : Option Bool) : Option String :=
  if own && twin.getD true then none else some swapClash

/-- The amendment's validation, symmetric (pc-d2 round 2): the first check of `checkDocSets` and `checkDoc`, before
the gate, on every request, plain ones included (PC-1). It reads the request's exchange and, on a request that lists
`judgments@0`, its twin's (`withoutJudgments j`, G3's twin). A request without `judgments@0` has no twin. -/
def clashRefusal (j : Json) : Option String :=
  clashRefusalOf (swapInjective j)
    (if "judgments@0" ∈ profilesOf j then some (swapInjective (withoutJudgments j)) else none)

/-- The check refuses exactly when the request's exchange is not one-to-one, or the request lists `judgments@0` and
its twin's is not (proved in the stub, 9). -/
theorem clashRefusal_some (j : Json) :
    clashRefusal j = some swapClash ↔
      (swapInjective j = false ∨
        ("judgments@0" ∈ profilesOf j ∧ swapInjective (withoutJudgments j) = false))

/-- On every request, plain ones included, a request whose exchange is not one-to-one, or that lists `judgments@0`
and whose twin's exchange is not, is refused with `swapClash` before any other check (the change to plain requests;
the symmetric check). -/
theorem checkDocSets_clashFirst (j : Json)
    (hk : swapInjective j = false ∨
      ("judgments@0" ∈ profilesOf j ∧ swapInjective (withoutJudgments j) = false)) :
    checkDocSets j = .error swapClash ∧ checkDoc j = .error swapClash

/-- The twin of a request whose exchange is not one-to-one keeps its stated values as written and has its two
environments, so its exchange is not one-to-one either. -/
theorem swapInjective_twin (j : Json) (hj : "judgments@0" ∈ profilesOf j) (hk : swapInjective j = false) :
    swapInjective (withoutJudgments j) = false

/-- The G3 amendment, symmetric (pc-d2 round 2): a request with `judgments@0` whose exchange, or whose twin's, is not
one-to-one is refused by validation on both sides, with the same text and the same fault order (first), and that
text is never a layer refusal. -/
theorem checkDocSets_swapClash (j : Json) (hj : "judgments@0" ∈ profilesOf j)
    (hk : swapInjective j = false ∨ swapInjective (withoutJudgments j) = false) :
    checkDocSets j = .error swapClash ∧ checkDocSets (withoutJudgments j) = .error swapClash ∧
      layerRefusal swapClash = false

/-- 2c. Omitting authored statuses changes no successful answer, so G3's domain loses none. -/
theorem checkDocSets_withoutStatuses (j : Json) (hj : "judgments@0" ∈ profilesOf j) (a : Json)
    (h : checkDocSets j = .ok a) :
    noUnitStatus (withoutStatuses j) = true ∧
      ∃ b, checkDocSets (withoutStatuses j) = .ok b ∧ verdictFields a = verdictFields b ∧
        unitStatuses a = unitStatuses b
```

The identities stay over the list as written (the jt-2c rule). `withoutJudgments` changes the text, so
`document_id` and `source_id` are outside `verdictFields`. It also changes the environment identity, so 2a
exchanges the stated identities and 2e drops the computed ones.

### 1.8 Priority: two typed graphs (PC-9)

There is no composition priority graph. W1's `over` relates rules and is checked by W1's precedence check
(`precedenceNodes`, `dependencyOrder`). Soft's `outranks` relates ranks and is checked by soft's rank check
(`RanksValid.order`, `rankNodes`). `VE.Closure` stays the one closure.

Scope's `precedes` and `yields` already join W1's graph: `addOver` writes them into the governed rule's `over`
(`Scope/Govern.lean:177`), and the chain validates the governed document. Acts' copies "`M over N` gives
`M-a<i> over N-a<i>`" (`splitNode`) are W1 edges too.

Draft 1's `pairs` erased the vertex type. Rule `a` over rule `b` beside rank `b` outranking rank `a` then made a
"cycle" from two acyclic graphs (F9.1). No mixed cycle is refused until a reviewed bridge (NM-1) gives a mixed
statement a meaning, and F9.1's mixed fixture moves to that bridge's review. Until then, a priority statement
between a rule and a rank is not admitted by any route on main, and WG-3's specification refuses one through E1
(2.3).

```lean
-- lean/VE/Norms/Tree.lean's owner (W1); a fact about the typed check, recorded by PC-9
/-- W1's precedence check reads no rank pair. -/
theorem precedence_apart (D : VE.SoftNorms.SoftDoc) (o : List (String × String)) :
    VE.Norms.precedenceNodes ({ D with soft := { D.soft with outranks := o } } : VE.SoftNorms.SoftDoc).base.T =
      VE.Norms.precedenceNodes D.base.T
```

Soft's rank check reads `SoftEnv` alone (`rankNodes : SoftEnv → List DepNode`), so it reads no rule edge by its
type.

### 1.9 One "no exception" (PC-9 statements; defeasible owns the build)

The owner is defeasible's `Dflt_T` (`lean/VE/Defaults/Premises.lean`), made uniform, in defeasible's files
(`lean/VE/Defaults/Uniform.lean`, new). Every decision premise takes the form `Dflt_T` already uses for
exceptions: a decision is taken only where a stated sufficient condition forces it.

The conditions come from soft's own exceptions (in the `SoftDoc`) and from **provider-exported condition
metadata**: PK-1 adds a field to `Pack`, keyed by soft's existing `DecisionKey`. No condition is read off the
shape of a labelled formula. Weighing keeps its WG-6 record. Once EXP-D3 proves the equality, the record is
`dfltUniform`'s instance (DF2 made concrete).

```lean
-- PK-1's field (PK-1's owner; a prerequisite of PC-9 and of defeasible's DF-U, not built by this plan)
structure Pack where
  ...                                                       -- as premise-packs.md 2.1
  conditions : List (VE.SoftNorms.DecisionKey × VE.Formula) -- (new) each stated sufficient condition and its decision
```

`softPack` and `rightsPack` (`Layered.lean:58, 61`) export `[]`. Soft's exceptions are already in the `SoftDoc`,
and rights states no decision condition.

**PC-9's prerequisites (pc-d2, edit 7).** `dfltUniformOf` reads two names no batch before PC-9 defined in draft 3:
PK-1's `Pack.conditions` and the decision key `decisionRule` (1.10). Both now land before PC-9. PK-1's owner adds
`Pack.conditions` in PK-1's own batch, and PC-9 waits for it. The compatible decision-key lookup (`splitFrom`,
`decisionRule`, `decisionRule_unsplit`: on an unsplit rule the key is today's, the rule's own name) is staged in
PC-6a, under soft-norms' ownership, before PC-9 (1.10). PC-6 keeps the split, the revised names and the table.
F6.7 reads both PC-6's split and PC-9's `dfltUniformOf`, so it is built in whichever of PC-6 and PC-9 merges second.

```lean
-- lean/VE/Defaults/Uniform.lean (new; defeasible)
namespace VE.Defaults

def packConditions (qs : List Pack) (k : DecisionKey) : List VE.Formula :=
  qs.flatMap fun p => (p.conditions.filter (·.1 == k)).map (·.2)

/-- A decision with no stated condition is never taken; otherwise it is taken only where one holds. -/
def noneOr (d : VE.Formula) : List VE.Formula → VE.Formula
  | [] => .not d
  | cs => .implies d (anyF cs)

/-- A rule's decisions are looked up by its decision key, `decisionRule N` (1.10, PC-6a), never by `N.name`:
provider metadata on a source rule reaches every part of it after a split (F6.7). -/
def dfltUniformOf (D : SoftDoc) (qs : List Pack) (N : SoftNode) : List (String × VE.Formula) :=
  (match N.mode, N.exception with
   | .default, some e =>
       [("default:exception:" ++ N.name, bindAll (sortsOf D N.pred)
         (.implies (exceptedF D N) (anyF (e.sufficient ++ packConditions qs (.excepted (decisionRule N))))))]
   | _, _ => []) ++
  N.alterable.map (fun π =>
    ("default:switch:" ++ N.name ++ ":" ++ π, bindAll (sortsOf D N.pred)
      (noneOr (atom (offName N π) (sortsOf D N.pred)) (packConditions qs (.off (decisionRule N) π)))))

def dfltUniformLabelled (D : SoftDoc) (qs : List Pack) : List (String × VE.Formula) :=
  D.T.nodes.flatMap (dfltUniformOf D qs) ++
  (outweighsTriples D).map (fun (a, L, H) =>
    ("default:ranking:" ++ L ++ ":" ++ H ++ ":" ++ a,
     bindAll (actSortsOf D a) (noneOr (outweighsF D a L H) (packConditions qs (.outweighs a L H)))))

def dfltUniform (D : SoftDoc) (qs : List Pack) : List VE.Formula := (dfltUniformLabelled D qs).map (·.2)

/-- On packs that state no condition (today's `[soft]`, `[soft, rights]`), the uniform premises are today's,
label for label. -/
theorem dfltUniform_legacy (D : SoftDoc) (qs : List Pack) (h : ∀ p ∈ qs, p.conditions = []) :
    dfltUniformLabelled D qs = dfltLabelled D

/-- The least decision tables of the stated conditions on `B`'s facts. -/
def leastUniform (D : SoftDoc) (qs : List Pack) (B : VE.Structure.{u}) : String → List B.Carrier → Prop

/-- The stated conditions are all that force a decision: the least tables keep the base admissible (the uniform
analogue of `ReplacementHolds`, Meaning.lean:70). -/
def ConditionsExact (U : UDoc) (D : SoftDoc) (qs : List Pack) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) B →
    ∃ F : String → List B.Carrier → Prop,
      BaseAdmissibleX U (VE.NormDefaults.Packs.X qs) (withOpen U D B (leastUniform D qs B) F) ∧
      SwitchesOff D (withOpen U D B (leastUniform D qs B) F)

/-- Proved by defeasible's named batch DF-U (DRI ruling 2(b)), against `DefaultBase`. -/
theorem dfltUniform_sound (U : UDoc) (h : WellFormedU U = true) (D : SoftDoc) (hU : U.D = soften D)
    (hD : WellFormedSoft D = true) (qs : List Pack) (hex : ConditionsExact.{u} U D qs) (B : VE.Structure.{u})
    (hB : DefaultBase U D (VE.NormDefaults.Packs.X qs) B) : Sat B (dfltUniform D qs)

/-- The guard the defaults kinds read until EXP-D3 settles (one line in `defaultsRows`, `Defaults/Route.lean:17`):
some provider states a decision condition. Every pack is read, not only `weighing`. -/
def providerConditions (qs : List Pack) : Bool := qs.any (!·.conditions.isEmpty)

def providerRefusal : String := "UnsupportedProfile: defaults with provider conditions is not implemented"
```

The hazard this prevents (research 5.2). `dfltLabelled` adds `¬outweighs(a, L, H)` for every ranking triple. A
weighing condition "C → outweighs(a, L, H)" would then make `--assume-no-exception` assume ¬C without saying so.
Today's `dfltLabelled` ignores every pack's `conditions`, so the hazard is any provider's, not weighing's alone,
and the guard reads every pack. Draft 1's `weighingConditions` read only the pack with id `weighing`. Until EXP-D3
settles, the guard refuses (DRI ruling 4(1)). The refusal and its sentence (2.1, E1d) name no provider: a pack
other than `weighing` never gets a weighing diagnostic (F9.6).

### 1.10 Split rules share one decision (PC-6)

Today `exceptedName` and `offName` are built from the node's own name (`SoftNorms/Tree.lean:266-267`). So once
acts renames parts, `N-a1` to `N-a4` would get four exception atoms, and one call by the decider would quietly
become four. A **decision key** names the rule whose decisions a rule reads. On an unsplit rule the key is today's.
It comes in two batches. PC-6a (soft-norms' ownership, before PC-9) adds the field and the lookup, which no
document sets yet, so every key is today's. PC-6 (after it) makes acts' parts set the field, and revises the names
and the table.

```lean
-- lean/VE/SoftNorms/Tree.lean (soft-norms' file). PC-6a: the field, the lookup and its unsplit form
structure SoftNode extends Node where
  ...                                  -- mode, rank, alterable, exception, hard: unchanged
  splitFrom : Option String := none    -- (new) the source rule of a part acts generated; none for an authored rule

/-- The rule whose decisions a rule reads. -/
def decisionRule (N : SoftNode) : String := N.splitFrom.getD N.name

/-- With nothing split, the key is today's: the rule's own name (proved in the stub, by `simp`). -/
theorem decisionRule_unsplit (N : SoftNode) (h : N.splitFrom = none) : decisionRule N = N.name

-- PC-6: the two names read the key (reviewed by soft-norms' owner)
def exceptedName (N : SoftNode) : String := "soft__excepted__" ++ ruleKey (decisionRule N)        -- revised
def offName (N : SoftNode) (π : String) : String := "soft__off__" ++ ruleKey (decisionRule N) ++ "__" ++ π  -- revised

/-- Unsplit, the names are today's, byte for byte. -/
theorem exceptedName_unsplit (N : SoftNode) (h : N.splitFrom = none) :
    exceptedName N = "soft__excepted__" ++ ruleKey N.name
theorem offName_unsplit (N : SoftNode) (π : String) (h : N.splitFrom = none) :
    offName N π = "soft__off__" ++ ruleKey N.name ++ "__" ++ π
```

**The decision table.** `keyedDecisions` (`Tree.lean:303`) keys every entry by `decisionRule N`: `.excepted
(decisionRule N)` and `.off (decisionRule N) π`, not `N.name`. It keeps one copy of equal entries
(`List.eraseDups`, first occurrence in node order), so a split rule's parts give one entry. `decisions` becomes
`(keyedDecisions D).map (·.2)`, so `keyedDecisions_names` holds by definition. `exceptedDecisions`, `offDecisions`
and `outweighsDecisions` are unchanged: one entry per node, or per triple. Every reader of a decision by key
(`whatOf`, `Defaults/Premises.lean:68`; `dfltUniformOf`, 1.9; the wire's `decisions`, `SoftNorms/Wire.lean:224`)
therefore finds the source rule's decision on every part (F6.7).

**Shared decisions: the invariant restated (the ruling's second option).** This specification takes one option:
the invariant is restated as equality of decision keys, with consistent sorts and exception metadata. It does not
distinguish authored from elaborated documents. Today `decNodup` (`Soften.lean:738`) makes decision names
distinct, node by node, and `excepted_inj` concludes that two default rules with one exception name are one rule.
Two parts of a split rule are distinct rules with one exception name, so both fail on every split document. Under
the restated invariant:
- `decNodup` keeps its text. On the deduplicated entries it now says that two decisions with one name have one key
  and one argument-sort list, and it still refuses two keys whose names collide, as today.
- `SoftValid` gains `decMeta`: rules with one decision key have the same mode, exception and alterable parties.
  `softSemanticCheck` (`Soften.lean:679`, beside `:692`) and `softSemanticCheckOnce` (`Once.lean:109`, beside
  `:126`) check its decidable form.
- On a document with no split rule, every key is a distinct node name, so both are today's (`decisions_unsplit`,
  `decMeta_unsplit`), and no document is newly refused.

```lean
-- lean/VE/SoftNorms/Soften.lean (soft-norms' owner): the new field of `SoftValid`
  decMeta : ∀ N ∈ D.T.nodes, ∀ M ∈ D.T.nodes, decisionRule N = decisionRule M →
    N.mode = M.mode ∧ N.exception = M.exception ∧ N.alterable = M.alterable

-- lean/VE/SoftNorms/Tree.lean
/-- Where today's names are distinct (today's `decNodup`), the table is today's concatenation; on an unsplit rule
its names are today's bytes (`exceptedName_unsplit`, `offName_unsplit`). -/
theorem decisions_unsplit (D : SoftDoc)
    (hd : ((exceptedDecisions D ++ offDecisions D ++ outweighsDecisions D).map (·.1)).Nodup) :
    decisions D = exceptedDecisions D ++ offDecisions D ++ outweighsDecisions D

-- lean/VE/SoftNorms/Soften.lean
/-- With no split rule and distinct rule names, `decMeta` holds: each key is one rule. -/
theorem decMeta_unsplit (D : SoftDoc) (h : ∀ N ∈ D.T.nodes, N.splitFrom = none)
    (hn : (D.T.nodes.map (·.name)).Nodup) :
    ∀ N ∈ D.T.nodes, ∀ M ∈ D.T.nodes, decisionRule N = decisionRule M →
      N.mode = M.mode ∧ N.exception = M.exception ∧ N.alterable = M.alterable

-- lean/VE/Defaults/Meaning.lean (revised; replaces `excepted_inj`, :105)
/-- Two default rules with the same exception predicate read one decision: the same decision key, the same
argument sorts and the same exception. -/
theorem excepted_key {N M : SoftNode} (hN : N ∈ D.T.nodes) (hn : N.mode = .default) (hM : M ∈ D.T.nodes)
    (hm : M.mode = .default) (h : exceptedName N = exceptedName M) :
    decisionRule N = decisionRule M ∧ sortsOf D N.pred = sortsOf D M.pred ∧ N.exception = M.exception

-- lean/VE/Defaults/Meaning.lean (revised, :100): the names of the deduplicated table, by membership
theorem decisionNames_split (q : String) : q ∈ decisionNames D ↔
    q ∈ (VE.SoftNorms.exceptedDecisions D).map (·.1) ∨ q ∈ (VE.SoftNorms.offDecisions D).map (·.1) ∨
      q ∈ (VE.SoftNorms.outweighsDecisions D).map (·.1)

-- lean/VE/SoftNorms/Semantics.lean (revised, :834)
theorem decisionNames_eq (D : SoftDoc) (q : String) : q ∈ decisionNames D ↔
    q ∈ (exceptedDecisions D).map (·.1) ∨ q ∈ D.T.nodes.flatMap (fun N => N.alterable.map (offName N)) ∨
      q ∈ (outweighsDecisions D).map (·.1)
```

**Every revised statement and every caller.** The statements are the six above: `decMeta`, `decisions_unsplit`
and `decMeta_unsplit` (new), and `excepted_key`, `decisionNames_split` and `decisionNames_eq` (revised). The
revised definitions are `exceptedName` and `offName` (`Tree.lean:266-267`), `decisions` (`:292`) and
`keyedDecisions` (`:303`).
Section 9 elaborates each. The callers follow, by file and line. Each keeps its statement unless the list says
otherwise; each proof is redone.

| Revised | Its callers |
|---|---|
| `excepted_inj` → `excepted_key` (`Defaults/Meaning.lean:105`) | `sat_dflt` (`:234`), use at `:255`; `replace_admissible` (`:300`), use at `:382`. Each rewrites `hC` with `N'.exception = N.exception` and the typing with `sortsOf D N'.pred = sortsOf D N.pred`, instead of `cases` on `N' = N` |
| `decisionNames_split` (`Meaning.lean:100`) | `excepted_inj` (`:108`, replaced); `excepted_only` (`:117`, use at `:120`); `excepted_only`'s uses at `:268`, `:279` keep their form |
| `decisionNames_eq` (`SoftNorms/Semantics.lean:834`) | `weighing_sub_decisions` (`:839`, use at `:840`); `strict_off_not_weighing` (`:847`, use at `:850`), re-proved from `decMeta`: a strict and a default rule never share a key. `strict_off_not_weighing`'s use at `:895` and `decFresh` at `:889` keep their form |
| `SoftValid` (`Soften.lean:727`): the field `decMeta` | `softValid_of_wellFormed` (`Soften.lean:748`, the only constructor; its proof unfolds `decisions` at `:801`); `softSemanticCheck` (`:679`); `softSemanticCheckOnce` (`Once.lean:109`) |
| `decisions` (`Tree.lean:292`) and `keyedDecisions` (`:303`) | proofs that unfold `decisions`: `keyedDecisions_names` (`Tree.lean:308`, statement kept, now by definition); `mem_decisions` (`Readings/SupEnv.lean:39`, statement kept, proof at `:44` by `List.mem_eraseDups`); `Readings/Live.lean:272`, `:282`, `:292`; `Readings/Unspecified.lean:484`; `Readings/Force.lean:666`, `:766`; `Readings/Lines.lean:664-665` (splits `decNodup` by `List.nodup_append`); `Readings/Separate.lean:72`; `Readings/ChoiceFacts.lean:223`, `:228`. Uses of `decNodup` through `find_key` or `inj_of_nodup_map` keep their form: `Readings/SupEnv.lean:111`, `Readings/UpSlot.lean:28`, `Readings/ChoiceTyped.lean:183` |
| `exceptedName`, `offName` (`Tree.lean:266-267`) | unchanged on unsplit rules (`exceptedName_unsplit`, `offName_unsplit`); every caller reads the same bytes there |

`mem_decisions` keeps its statement, because the table keeps every entry's value and drops only repeats. Its uses
are not touched: `Defaults/Meaning.lean` (`:149`, `:249`, `:262`, `:273`, `:289`, `:322`, `:371`, `:430`),
`Defaults/Wire.lean:588`, `Defaults/Premises.lean` (`:141`, `:153`, `:158`), and in `Readings/`: `BaseUp.lean`
(`:317-353`), `BaseDown.lean` (`:153-170`), `ChoiceWF.lean` (`:41-53`), `ChoiceTyped.lean` (`:124-616`),
`UpPremises.lean` (`:66`, `:197`), `UpSlot.lean:310`, `Situation.lean:228`, `SupEnv.lean` (`:58`, `:142`, `:314`).
If the build finds a caller this table does not list, or a statement in it that is false, the build stops and
reports it to the confirmation pass.

**Argument mapping.** A part `p__i` keeps its source predicate's argument sorts (`splitEnv`,
`Acts/Elaborate.lean:104`). So a part's decision atoms take the source's arguments in the same positions; the map
is the identity on positions (`split_sorts`, 3.6).

**`outweighs` decisions** are per act (`pairTriple` reads `act D N`), and a split act's parts are distinct acts
(act-phrases 6.5). PC-6 therefore admits a split only under strict outranking. Under holistic outranking a split
rule is refused (4, row 9) until soft-norms' owner decides how an `outweighs` decision reads across parts.

## 2. English

Every sentence below passes the all-derivations gate before it is registered (english-lean). Each row gives the
wording, its one reading, and what in Lean licenses it. A sentence is produced only from that Lean source, never
recomputed in Python.

### 2.1 E1 and E2, amended before their first registration (PC-4)

composition.md 2.1 fixes E1 and E2 with "turns on". "Turns on" has two readings: "depends on", and "switches on".
No product code has registered E1 or E2 (they appear in no Lean or Python source on main), so PC-4 registers them
with "uses". The amendment goes into composition.md 2.1 in PC-4's change, under this review.

| ID | Wording | One reading | Lean source |
|---|---|---|---|
| E1 | `This document uses two features. The first is <feature a>. The second is <feature b>. VE cannot check these two together yet. Nothing in this document was checked.` | Both named features are enabled, and no route checks them together. No verdict of any kind was produced. | a refusal `UnsupportedProfile: <a> with <b>` or `UnsupportedProfile: <a> with <b> is not implemented`, with `<a>` and `<b>` mapped by 2.2 |
| E2 | `This document uses <feature a>, which needs <feature b>. Nothing in this document was checked.` | Feature a is enabled; feature b, which it is built on, is not. | a refusal `UnsupportedProfile: <a> requires <b>` |
| E1s (whole stack) | `This document uses <k> features: <feature 1>, …, and <feature k>. VE can check any two of them together, but not all <k> together yet. Nothing in this document was checked.` | All k named features are enabled. Every pair of them has a route, and no route checks all k together. No verdict of any kind was produced. | a refusal `UnsupportedProfile: stack <p1>, …, <pk> is not implemented` (3.4), `<k>` a number word, each `<pi>` mapped by 2.2 |
| E1d (defaults) | `This question assumes no exception, and this document's providers state decision conditions. VE cannot check these two together yet. Nothing in this document was checked.` | The question was asked with `--assume-no-exception`, and some premise pack of the document states a sufficient condition for a decision. No route checks the two together. No verdict was produced. | the refusal `UnsupportedProfile: defaults with provider conditions is not implemented` (1.9) |

E1s's text is produced only when every pair of the stack is listed, so "any two of them together" is true where it
is shown. It is registered through the all-derivations gate with E1 and E2 in PC-4, and in any case before PC-7b
lists a second pair. E1d is its own wording, not E1's: "defaults" is a kind of request, not a feature the document
uses (`defaultsRows`, `Defaults/Route.lean:17`), so E1's "This document uses two features" would be false for it.

E1, E1s, E1d and E2 are produced only for `UnsupportedProfile` texts. A `CheckerUnavailable` answer is not a refusal of the
combination: it hands the document to the retained path. It keeps its own text, and E1 is never applied to it.

### 2.2 Feature names (PC-4)

One name per profile and per non-profile token, pairwise distinct, used only in E1 and E2. composition.md 2.2's
nine rows are kept as written. PC-4 adds the rest.

| Token | `<feature>` | Source |
|---|---|---|
| `ve.discourse@1` | resolved references | composition.md 2.2 |
| `right-clauses@0` | clauses on right lines | composition.md 2.2 |
| `readings@1` | readings that carry rules | composition.md 2.2 |
| `norms@0` | rules | composition.md 2.2 |
| `rights@0` | rights | composition.md 2.2 |
| `alternatives@0` | alternatives | composition.md 2.2 |
| `risk@0` | risk statements | composition.md 2.2 |
| `speech-acts@0` | commands and questions | composition.md 2.2 |
| `reports@0` | reports of what someone said | composition.md 2.2 |
| `acts@0` | act phrases | this plan |
| `scope@0` | sentences that govern other sentences | this plan |
| `judgments@0` | judgment words | this plan |
| `soft-norms@0` | rules with exceptions | this plan |
| `norm-defaults@0` | what the text leaves unsaid | this plan |
| `documents@1` | document records | this plan |
| `closure@0` | chains of relations | this plan |
| `order@0` | orderings | this plan |
| `nary@0` | relations among three or more things | this plan |
| `relational-fol@0` | statements about things and their relations | this plan |
| `data@0` | relations that are functions | this plan |
| `definitions@0` | definitions | this plan |
| `time@0` | points in time | this plan |
| `cardinality@0` | counts | this plan (with qt-a3c's row) |
| `holistic outranking` | balancing rules of different rank | this plan |

Draft 1's rows `defaults` and `weighing conditions` are deleted: PC-9's refusal now has its own sentence, E1d,
which names no feature.

Planned profiles register their own names when their rows land, each through the all-derivations gate in the batch
named: `weighing@0` weighing (WG-3); `attitudes@0` beliefs and aims (AT-3a); `events@0` dates and events (et-4);
`modality@0` statements of what is possible or necessary (MD-2); `presupposition@0` phrases that take something for
granted (PS-4). The last two are named here so that PC-4's layer rule (3.4) has a worded E1 for each from the batch
that makes the profile owned (F4.9). Every other `.layer` profile (`hedges@0`, `purposes@0`, `examples@0`) registers
its name in the batch that adds its row, before that batch makes it owned, because the layer rule renders it with E1.
A pair whose token has no row here is never rendered by E1. Its diagnostic is shown as it is, which the english-lean
gate counts as an unworded refusal.

### 2.3 Instances this plan introduces

| Where | Diagnostic | Rendered |
|---|---|---|
| PC-4 stack rule (3.4), first unlisted pair | `UnsupportedProfile: acts@0 with scope@0 is not implemented` | `This document uses two features. The first is act phrases. The second is sentences that govern other sentences. VE cannot check these two together yet. Nothing in this document was checked.` |
| PC-4 stack rule (3.4), every pair listed (F4.7) | `UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0 is not implemented` | `This document uses three features: resolved references, act phrases, and sentences that govern other sentences. VE can check any two of them together, but not all three together yet. Nothing in this document was checked.` |
| PC-9 guard (1.9) | `UnsupportedProfile: defaults with provider conditions is not implemented` | `This question assumes no exception, and this document's providers state decision conditions. VE cannot check these two together yet. Nothing in this document was checked.` |
| PC-4 layer rule (3.4), `risk@0` with `modality@0` before modality's agreement theorem (F4.9, DEC 15) | `UnsupportedProfile: modality@0 with risk@0 is not implemented` | `This document uses two features. The first is statements of what is possible or necessary. The second is risk statements. VE cannot check these two together yet. Nothing in this document was checked.` |
| PC-6 holistic split (1.10) | `UnsupportedProfile: acts@0 with holistic outranking is not implemented` | `This document uses two features. The first is act phrases. The second is balancing rules of different rank. VE cannot check these two together yet. Nothing in this document was checked.` |
| WG-3's specification (1.8; not built here) | `UnsupportedProfile: <rule-priority token> with <rank-priority token> is not implemented`, its tokens registered by WG-3 | E1 |

### 2.4 Wordings requested of judgment-terms' JT-4 (not built by this plan)

PC-10 has left this plan. It is a request to JT-4, on WG-6 records (judgment-terms D14: no `Call` type). The
sentences are filed under PLANS-INDEX D8 as answer vocabulary, and are built only if the corrected EXP-J1 passes.
The converged wordings are recorded here so the review sees them once:

| For | Wording | One reading |
|---|---|---|
| a unit whose only openness is bound judgments | `Not checked: it depends on <k> judgment calls. <decider> decides whether <judged words>.` | The unit stays OPEN. Under every assignment of its judged atoms each of its points has a status, and that is all that is open. |
| a conditional answer | E3's `This holds provided that:` followed by `<decider> decides that <judged words>` | A supposition attributed to its decider, as E14 words one. |
| an answer that uses no call premise | E13's frame, `This does not depend on how <judged words> is decided.` | The labels the checked certificate uses (`VE.Readings.usedLabels`, `Readings/Verdicts.lean:789`) include no call premise. No new scan of a certificate's leaves. |

What JT-4's definition must state (the converged correction of draft 1's `DecidedGivenCalls`):
- the assignments are exhaustive over the unit's judged atoms;
- there is at least one point, so `points = []` is never vacuously accepted;
- the unit has no other openness: it is complete, and depends on no unbound open term.

UNDECIDED points are reported as UNDECIDED, and no wording suggests a settled answer. The column goes into
reports only; no coverage status is added before round 2 (DRI ruling 4(3)).

### 2.5 Not wordings, and never produced

- "Checked, except for <k> judgment calls" or any sentence opening with "Checked" on an OPEN unit.
- "turns on" in E1 or E2.
- "Sentences <n> and <m> each come before the other" for a rule and a rank (draft 1's `PriorityCycle`). No mixed
  cycle is refused, so the sentence has no source.
- A judgment, decision or call stated as a fact.

## 3. Lean statements by batch

Names marked (new) are added by the batch; every other name is on main at `d25bc343b`. Proof notes give the
intended route; the review checks statements, not proofs.

### 3.1 PC-1: `judgments@0` beside the soft and rights chains

Files: `lean/VE/Judgments/Chain.lean` (new; namespace and owner judgment-terms; built with its review);
`lean/VE/Service/Document.lean` (the `judgmentsApart` entries, the reader's call sites).

```lean
namespace VE.Judgments

/-- PC-1 (1). Formulas whose every predicate is reserved, or already read, change no scan. -/
theorem opensIn_generated (J : List String) (fs gs : List VE.Formula)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hg : ∀ g ∈ gs, ∀ p ∈ VE.Norms.preds g,
      VE.NormDefaults.Packs.reserved p = true ∨ ∃ f ∈ fs, p ∈ VE.Norms.preds f) :
    opensIn J (fs ++ gs) = opensIn J fs

/-- PC-1 (2). What a soft rule's unit reads: its author rule (guard and author carve-outs). -/
def softContent (N : VE.SoftNorms.SoftNode) : Content := .rule N.toNode

theorem softContent_formulas (N : VE.SoftNorms.SoftNode) : (softContent N).formulas = N.guard :: N.carveOuts

/-- PC-1 (3). The author formulas of a rights source, as written: holder guards, line guards and author
carve-outs, limitation conditions, aims. -/
def rightsAuthorFormulas (R : VE.Rights.RightsDoc) : List VE.Formula

/-- PC-1 (3). Every judgment the rights route's rules and limitation premises read is read by an author formula. -/
theorem correlate_judged (defs : List VE.Definitions.Def) (J : List String) (R : VE.Rights.RightsDoc)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hd : ∀ d ∈ defs, VE.NormDefaults.Packs.reserved d.name = false) :
    ∀ j ∈ dependsOnC defs J (((VE.Rights.correlate R).T.nodes.map fun N => Content.rule N.toNode) ++
      (VE.Rights.limPremises R).map Content.formula),
    j ∈ dependsOn defs J (rightsAuthorFormulas R)

/-- PC-1 (3). The author formulas of one rights block, by its unit. -/
def blockFormulas (R : VE.Rights.RightsDoc) (block : Json) : Except String (List VE.Formula)

/-- PC-1 (3). The scan reads names only, so one conjunction carries a block's formulas for it; it is never a claim. -/
def andAll (fs : List VE.Formula) : VE.Formula := fs.foldr .and .top
theorem preds_andAll (fs : List VE.Formula) : VE.Norms.preds (andAll fs) = fs.flatMap VE.Norms.preds
```

```lean
namespace VE.Service.Document

/-- PC-1 (4). What a unit reads for judgment dependence: formulas and W1 rules as before (`judged`), a soft rule
through the soft route's decoder and `softContent`, a rights block through `blockFormulas` and `andAll`. -/
def UnitContent.judgedIn (S : Option VE.SoftNorms.Wire.SoftEnvironment) (R : Option RightsDoc) :
    UnitContent → Except String (Option VE.Judgments.Content)

theorem judgedIn_legacy (S : Option VE.SoftNorms.Wire.SoftEnvironment) (R : Option RightsDoc) (c : UnitContent)
    (h : c.judged.isSome = true) : c.judgedIn S R = .ok c.judged

theorem judgedIn_soft (se : VE.SoftNorms.Wire.SoftEnvironment) (R : Option RightsDoc) (rule : Json)
    (N : VE.SoftNorms.SoftNode) (h : VE.SoftNorms.Wire.decodeSoftNorm se rule = .ok N) :
    (UnitContent.soft rule).judgedIn (some se) R = .ok (some (VE.Judgments.softContent N))
```

PC-1 (5) is G3, `checkDocSets_judgments_transparent`, with 2a's `swap_correct` and `withoutJudgments_ids`, the G3
amendment's `plainProfiles`, `layerProfiles`, `statedIds`, `statedPairs`, `exchange`, `swapInjectiveOf`,
`swapInjective`, `swapClash`, `clashRefusalOf`, `clashRefusal` (symmetric: the request and its twin, pc-d2 round 2),
`clashRefusal_some`, `checkDocSets_clashFirst`, `swapInjective_twin` and `checkDocSets_swapClash`, and 2c's
`checkDocSets_withoutStatuses` (1.7). PC-1 adds `clashRefusal`'s line as the first line of `checkDocSets` and
`checkDoc` (3.4 shows `checkDocSets` with it), the change to plain requests that 1.7 records. `judgedViews`
(`Document.lean:1709`) calls `judgedIn` with the soft layer's `SoftEnvironment` (`softRules`) and the document's `RightsDoc`. `judgmentsApart` becomes
`["alternatives@0", "risk@0"]`.

**Draft 1's `dependsOn_primeNode` is withdrawn: it is false.** `primeNode D N` adds the derived carve-out
(`Soften.lean:110-117`). That carve-out reads `dominatedF`, which reads each opponent's `eligibleF`, which reads the
opponent's guard. So a judgment in an opponent's guard shows up in `dependsOnC [.rule (primeNode D N)]`, while N's
own text never uses it (F1.8). The unit's content is its author rule, as judgment-terms D4 defines dependence ("a
unit's content ... uses it"). The reader is therefore defined on the author rule (`softContent`), and no theorem
relates it to `primeNode`.

**PC-1b: the reader over attitude guard nodes (pc-fid-rev, B5; staged: after PC-1, AT-3a and AT-2).** Attitudes
beside judgments is G3 once the reader covers every content kind of the route (1.2's `layer` row; the plan's 3.3 row
2: "the judgment reader extended to attitude guard nodes"). Under `attitudes@0`, AT-3a's guard node `{"attitude":
{"holder", "mode", "degree"?, "slot"?, "content"}}` is decoded by the chain's norm decoders (synthesis 2.7) into
AT-2's generated atom (`attitudes__<mode>__<k>`, one per mode and content, an open term of the attitudes block, decided
by its `decided_by`), and the content leaves the rule's guard. So `judgedIn` (3.1) on the decoded rule sees the atom,
not the content, and a judgment inside the content is invisible: with it listed, the unit is refused with
`JudgmentListedUnused` (a G3 layer refusal, so no theorem is broken, but the unit is lost). PC-1b reads each generated
atom's content from AT-2's keys:

```lean
namespace VE.Judgments

/-- PC-1b. The formulas a unit reads under `attitudes@0`: its own, then the content of each generated attitude atom
they use, read from `keys` (AT-2's generated predicate with the content it stands for, quantifier-free over the base
vocabulary, AT-3a's node). The generated atom itself is an open term of attitudes' block, never a judgment. -/
def withAttitudeContents (keys : List (String × VE.Formula)) (fs : List VE.Formula) : List VE.Formula :=
  fs ++ (keys.filter fun k => fs.any fun f => (VE.Norms.preds f).contains k.1).map (·.2)

/-- PC-1b. A judgment inside an attitude's content is read by the unit, in `J`'s order. -/
theorem opensIn_attitude (J : List String) (keys : List (String × VE.Formula)) (fs : List VE.Formula) :
    opensIn J (withAttitudeContents keys fs) =
      J.filter (fun j => (opensIn J fs ++
        opensIn J ((keys.filter fun k => fs.any fun f => (VE.Norms.preds f).contains k.1).map (·.2))).contains j)
```

`judgedIn` (owner judgment-terms; this plan builds it) passes each content's formulas through `withAttitudeContents`
with the keys of the attitudes pack the route assembled, when `attitudes@0` is listed; without it, `keys = []` and
`withAttitudeContents [] fs = fs`, so every answer of PC-1 is unchanged. What the unit then reads is the dependence
judgment-terms D4 defines: the unit's content uses the judged predicate, inside the holder's belief. Nothing else
changes: the generated atom keeps its own open-term line (AT-2), the attitude's content adds no premise (attitudes:
nothing follows from a belief), and G3, stated for every list, covers lists with `attitudes@0` once the reader reads
its node. The fixtures are F1.9 to F1.11. Where the pilot's writer stubs attitudes (`STUB[attitudes]`), the stub fills
one guard conjunct of the rule (the node's position), with its holder, its slot (the rule's quantified variable) and
its content; the judged predicate inside the content is a judgment term of this plan's reader.

**A purpose clause after a rule (pc-fid-rev2, R4(a); PC-1 and PC-2b, no new statement).** "<rule>, so that <Y>",
"<rule>, to <Y>", "<rule> for <Y>" can be read two ways (purpose-explanation D6(a)): the purpose limits the rule (the
rule's guard gains the open condition "doing so serves <Y>", purpose-explanation's content-level purpose, written as
a judgment term, never as a link: its plan, lines 33-36 and 116) or it is the rule's rationale (the rule as written,
and purpose-explanation's link, which adds no premise: its D1). Where both readings are open, the unit holds one reading
set, on the part that holds the rule and the clause: `limiting`, the rule whose guard has one more conjunct, a bound
judgment over the rule's quantified variables (`that situation is classified as "<j>"`), and `rationale`, the rule as
written with the link; or the set is narrowed to one of them by a narrowing that cites a source unit (document
88-91). Never a link part alone: that fixes the rationale reading and drops the other. Nothing new is needed to read
it: on the soft chain the unit's content is its author rule (`softContent_formulas`), so `judgedIn_soft` reads the
guard conjunct and the unit is OPEN through it (F2.11); the set is a chain reading set (`chainReadings_rows`, 3.2).
With an outer set (a "will" read as conditional, unconditional or an overview), the candidates are the pairs, as in
3.6's derivation rule: each outer candidate that holds the rule, once per purpose reading, labelled on both axes; a
candidate with no rule has no purpose reading. Under PC-6's split the conjunct is in every part rule's guard, so each
part is read. The slots: the judgment's words are `STUB[purpose-explanation]` (its record is judgment-terms' JT-2, with
the decider the text names, or `unresolved_decider`); the link is purpose-explanation's, and whether the clause's
marker admits a link is its D2. Neither is designed here.

### 3.2 PC-2a, PC-2b, PC-2c: the soft and rights chains in the document mode

File: `lean/VE/Service/DocumentChain.lean` (new; composition).

```lean
namespace VE.Service.DocumentChain
open VE.Service.Document

/-- The `norm-defaults` mode's case that a document's soft or rights units make: environment `E.lower`, the free
norms (or the rights document), and the front matter's `completions`. -/
def requestOf (E : Env) (front : Json) (units : List SourceUnit) : Json

/-- The layered document: the norm-defaults mode's own decoder on that case (rd-9 SC-8), never a second elaboration. -/
def layeredOf (E : Env) (front : Json) (units : List SourceUnit) :
    Except String VE.NormDefaults.Wire.LayeredU :=
  VE.NormDefaults.Wire.decodeLayered (requestOf E front units)

/-- PC-2a (1). A soft document gets today's packs. -/
theorem layeredOf_ids (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) (hs : E.soft = true) : L.packs.map (·.id) = ["soft"]

/-- PC-2a (2). `acceptanceX` at the document's layered document, applied directly: `L.wfU`, and
`decodeSoftU_X_wellFormed` (LayeredAdmission.lean:53) or, for rights, `decodeRightsU_X_wellFormed`. -/
theorem layeredOf_entails (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (VE.Norms.envAt (VE.NormDefaults.fill L.U) (VE.Norms.size (VE.NormDefaults.fill L.U)))
      (VE.NormDefaults.Wire.premisesX L.U L.X Γ) φ cert = true) :
    VE.NormDefaults.EntailsX.{u} L.U L.X Γ φ
```

The document mode's soft branch under `norm-defaults@0` is `layeredOf`, then `Wire.validateCompletions` on `L.U`.
The norm-defaults mode answers the same case through the same `decodeLayered`. So "two entry points, one answer"
holds by construction, not by a parity theorem; the parity test (F2.3) checks the retired Python branch against it.

```lean
/-- PC-2b. The rows of a question over the document's reading sets. -/
structure ChainRows where
  conflicts : List (VE.Readings.Choice × VE.Readings.ChoiceResult)
  rows      : List (VE.Readings.Choice × VE.Readings.ChoiceResult)
  verdict   : VE.Readings.ReadingVerdict

/-- The compatible choices of the document's active reading sets, pending readings included, in canonical order:
df-3's enumeration, which this batch reuses and does not rewrite. -/
def compatibleChoices (E : Env) (front : Json) : Except String (List VE.Readings.Choice)
def pendingAt (front : Json) (c : VE.Readings.Choice) : Bool
/-- The layered route's answer on one choice's document; `unknown` on a pending choice or an abstention. -/
def rowAt (E : Env) (front : Json) (units : List SourceUnit) (q : Json) (c : VE.Readings.Choice) :
    VE.Readings.ChoiceResult
def conflictAt (E : Env) (front : Json) (units : List SourceUnit) (c : VE.Readings.Choice) :
    VE.Readings.ChoiceResult
def chainReadings (E : Env) (front : Json) (units : List SourceUnit) (q : Json) : Except String ChainRows

/-- PC-2b. The rows are exactly the compatible choices, in order; pending choices and UNKNOWN are kept; the verdict
is `VE.Readings`' fold (no new fold). -/
theorem chainReadings_rows (E : Env) (front : Json) (units : List SourceUnit) (q : Json) (r : ChainRows)
    (h : chainReadings E front units q = .ok r) :
    ∃ cs, compatibleChoices E front = .ok cs ∧ r.rows.map (·.1) = cs ∧ r.conflicts.map (·.1) = cs ∧
      (∀ x ∈ r.rows, x.2 = rowAt E front units q x.1) ∧ (∀ x ∈ r.conflicts, x.2 = conflictAt E front units x.1) ∧
      (∀ c ∈ cs, pendingAt front c = true → rowAt E front units q c = .unknown) ∧
      r.verdict = VE.Readings.foldEntailment r.conflicts r.rows

/-- PC-2b. The layered route's reading document and each choice's extra base premises (the choice's layered `X`),
as the `readings-verdicts` replay reads them (`XVerdicts.N`, `XVerdicts.Xf`, Readings/VerdictsWire.lean:298). -/
def chainDoc (E : Env) (front : Json) (units : List SourceUnit) :
    Except String (VE.Readings.NDoc × (VE.Readings.Choice → List VE.Formula))

/-- PC-2b. The question's premises and conclusion, decoded as the readings route decodes them. -/
def questionOf (E : Env) (q : Json) : Except String (List VE.Formula × VE.Formula)

/-- PC-2b (cover). Both row lists are exactly the compatible choices, under the layered `xSem`, conflict rows
included. -/
theorem chainReadings_covers (E : Env) (front : Json) (units : List SourceUnit) (q : Json) (r : ChainRows)
    (h : chainReadings E front units q = .ok r) :
    ∃ N Xf, chainDoc E front units = .ok (N, Xf) ∧
      VE.Readings.CoversG (VE.Readings.xSem.{u} N Xf) [] r.conflicts ∧
      VE.Readings.CoversG (VE.Readings.xSem.{u} N Xf) [] r.rows

/-- PC-2b (rows hold). Every row holds of its choice under the layered `xSem`, conflict rows included: the
hypothesis of every generic fold theorem. Proved from the `XVerdicts` evidence the layered route decodes: these rows
are its `conflictRows` and `queryRows`, and `x_rowsHold` (VerdictsWire.lean:334) gives `RowsHoldG`. -/
theorem chainReadings_rowsHold (E : Env) (front : Json) (units : List SourceUnit) (q : Json) (r : ChainRows)
    (h : chainReadings E front units q = .ok r) :
    ∃ N Xf Γ φ, chainDoc E front units = .ok (N, Xf) ∧ questionOf E q = .ok (Γ, φ) ∧
      VE.Readings.RowsHoldG (VE.Readings.xSem.{u} N Xf) [] Γ φ r.conflicts r.rows
```

`chainReadings_rows` alone does not license the fold theorems. It fixes which choices are rows and how the verdict
is folded, not that each row's result holds of its choice: rows that are the compatible choices, each marked
`proved` at random, satisfy it (F2.6d). `RowsHold` (`Readings/Verdicts.lean:82`) and its generic form `RowsHoldG`
(`:223`) need every row to hold. With `chainReadings_rowsHold`, the generic fold theorems that take `RowsHoldG`
apply at `xSem N Xf`: `foldG_all_sound`, `foldG_none_sound` and `foldG_some_sound` (`Verdicts.lean:237`, `:251`,
`:270`) for the verdict, and `foldG_conflict_free_sound` and `foldG_conflict_sound` (`:294`, `:306`) for the
conflict rows. Draft 1 cited `fold_all_sound`, `fold_none_sound` and `fold_some_sound` (`:401-413`) here. Those
are the `ndSem` instances, which also take `RowsHold`, and this draft replaces them with the generic theorems.

**Couplings (pc-fid-rev2, R1).** The chain's readings branch keeps main's couplings as main decodes them, and relaxes
none of main's checks. A coupling on an axis is admitted only when every candidate of every set it names carries a
label on that axis, and the sets share a value (`decodeCouplings`, `Readings/SupWire.lean:35`); otherwise the
document is refused at decode, before any route is chosen, with `CouplingLabelMissing: <coupling id>, <set id>` (row
20). Main's S2a admission returns that text (`admitS2Rest_couplings`, proved below from main's code). The chain's
choices are main's choices of that admission's document (`compatibleChoices_admitS2`: the admission succeeds and
`cs = VE.Readings.choices a.D`), and the case's document that admission reads carries the front matter's reading sets
and couplings unchanged (`readingsCaseOf_keeps`), so the couplings main checks are the ones the writer wrote and
nothing main refuses has a row here.

```lean
-- a lemma about main's `admitS2Rest` (Readings/SupWire.lean:148), proved in the stub (section 9); PC-2b adds it to
-- lean/VE/Service/DocumentChain.lean with this proof, and no line of SupWire.lean changes
theorem VE.Readings.Wire.admitS2Rest_couplings (a : Admitted) (document : Json) (ss : Array Json)
    (sets : List SetJ) (e : String)
    (hr : document.getObjValD "reading_sets" = .arr ss) (hs : ss.toList.mapM decodeSet = .ok sets)
    (h : decodeCouplings document sets a.doc.units = .error e) : admitS2Rest a document = .error e := by
  simp [admitS2Rest, hr, hs, bind, Except.bind, h]

-- lean/VE/Service/DocumentChain.lean (PC-2b)
/-- The `readings` route's environment and document that the chain's readings branch makes of a case's front matter;
df-3's enumeration reads the choices from their S2a admission. -/
def readingsCaseOf (E : Env) (front : Json) : Json × Json

/-- PC-2b (pc-fid-rev2, R1; review fix). The case's document carries the front matter's reading sets and couplings
unchanged, so the S2a admission below decodes the couplings the writer wrote. -/
theorem readingsCaseOf_keeps (E : Env) (front : Json) :
    (readingsCaseOf E front).2.getObjValD "reading_sets" = front.getObjValD "reading_sets" ∧
      (readingsCaseOf E front).2.getObjValD "couplings" = front.getObjValD "couplings"

/-- PC-2b (pc-fid-rev2, R1; review fix). The chain's choices are main's choices of its S2a admission of that case: a
front matter main refuses has no compatible choice, so no row and no verdict. -/
theorem compatibleChoices_admitS2 (E : Env) (front : Json) (cs : List VE.Readings.Choice)
    (h : compatibleChoices E front = .ok cs) :
    ∃ a, VE.Readings.Wire.admitS2 (readingsCaseOf E front).1 (readingsCaseOf E front).2 = .ok a ∧
      cs = VE.Readings.choices a.D
```

The writing rule (the plan's 15.2 rule 10). A set whose candidates differ on more than one axis (the RSP use case's
one set {F, Ds_strict, Ds_default}: the addressee, and for the Ds candidates the force) is written in one of two ways:
- **(a) one combined axis** whose values are the set's candidates (axis `rs2`, values `F`, `Ds_strict`,
  `Ds_default`), and one coupling on it over the sets that share the reading; or
- **(b) one coupling per axis**, every candidate of every set that coupling names carrying its axis. A candidate the
  axis does not apply to (F has no force) carries a value of its own, its candidate id (`force=F`), that no other
  candidate of its set carries, the same in every set of the coupling, so the coupling never joins it to another
  candidate.

A set that shares only some of the axes (ursp.t4_evidentiary's set shares the addressee, not the force: its force is
its own) is named only by the couplings of the axes it shares and carries their labels; in (a) it is coupled with the
others on the shared axis, and their candidates carry that axis too. Both forms give the same compatible choices
(F2.10: 5 of 27 for the three sets). Writing a coupling over a set with an unlabelled candidate is refused, as main
refuses it.

```lean
/-- PC-2c (1). A rights document gets packs `["soft", "rights"]`, filled last (`rights_is_slot`). -/
theorem layeredOf_rights (E : Env) (front : Json) (units : List SourceUnit) (L : VE.NormDefaults.Wire.LayeredU)
    (h : layeredOf E front units = .ok L) (hr : E.rights = true) : L.packs.map (·.id) = ["soft", "rights"]

/-- PC-2c (2), in `LayeredAdmission.lean` beside its soft twin. -/
theorem decodeRightsU_X_wellFormed (environment document : Json) (L : VE.NormDefaults.Wire.LayeredU)
    (h : VE.NormDefaults.Wire.decodeRightsU environment document = .ok L) :
    ∀ a ∈ L.X, a.WellFormed (VE.Norms.envAt (VE.NormDefaults.fill L.U) 0) []
```

Each of PC-2a and PC-2c changes a request or response shape, through the deletions in `ve/document/load.py` and
`ve/document/lean.py`. So each adds its rows to rd-9's relay-binding inventory (D9), with fuzz tests that retype
and rebind each field.

### 3.3 PC-3: the contract

PC-3 builds 1.2 to 1.6:
- the `interface` field, with C1 to C3 by `decide`, and the values of 1.1 for every row it touches; the planned
  rows' values are 1.1's table, which each owning plan confirms in its row batch (F3.4b, F3.4c);
- `lean/VE/Compose/Stack.lean` with `rewriters`, `stackOf` and `Contract.listedStacks` (1.3), and `pipelineOf`;
- G2 (`pipeline_preserves`, `pipeline_off`, `pipeline_names`), by induction;
- `scopeRewriter`, `ScopeRunsOf`, `checkDocSets_pipeline` and `refuseAll_runs`;
- `ScopeFaithful`, `ScopePreserves` and `ScopeSetsFaithful`, each a conjunction of statements already proved on main
  (1.5), so `listed_evidence` for the two listed stacks needs no new proof beyond `checkDocSets_pipeline`;
- `RouteFacts`, `listedStacks` and `listed_evidence`;
- `composed_superpose_all`, by `superpose_all_extra` and `transfers_X`.

G1b (`BaseAdmissibleXV`, `DocumentExpansionXV`, `EntailsXV`, `acceptanceXV`, `entailsXV_constraint`,
`countermodelXV`) is built by PK-1's owner in `PacksVocab.lean`, with its fixtures F3.2 to F3.2d. Its new proof
expands base structures to the packs' names, as `PacksLegacy.lean:71` already types `X` over `envX`.

Draft 1's `Composed` structure, `composed_acceptance`, abstract `Transparent` and `transparent_pair` are deleted:
- `composed_acceptance` was `acceptanceX` restated;
- the abstract `Transparent` compared refusals, which is false (1.7);
- layers compose through their own whole-list theorems (G3 for `judgments@0`, `LayerFacts` for the others, 1.5), so
  `transparent_pair` is not needed.

### 3.4 PC-4: the document mode's composition refusals in one module, E1 everywhere

Files: `lean/VE/Compose/Matrix.lean` (new; composition, computed from AR-10's rows) and
`lean/VE/Service/DocumentBase.lean` (new; owner composition, created by PC-4).

Today the document mode refuses at two sites:
- `environmentOf`, `Document.lean:685-696`: checks 1 to 4 below, on the listed profiles;
- `check`, `Document.lean:1744`: on the list as written, before `environmentOf`.

PC-4 moves both into this module without changing their order or texts. It adds two rules. The stack rule sits at
the second site, and in the document mode's two scope entries, `checkDocSets` and `checkDoc`, right after their
gate. The layer rule sits at the first site, after today's checks.

**The imports (pc-d2, edit 8).** `Matrix.lean` reads names `Document.lean` defines, and `Document.lean` calls
`Matrix.documentRefusal`, `Matrix.caseRefusal` and `Matrix.stackRefusal`. One module cannot import the other in both
directions, so every name both sides read moves to one lower module:
- `lean/VE/Service/DocumentBase.lean` (new; owner composition, created by PC-4; namespace `VE.Service.Document`, so
  no qualified name changes): `unavailable`, `judgmentsApart`, `Block` and `blockOf`, moved from `Document.lean`
  (`:49`, `:59`, `:80-85`), not copied. It imports only Lean core. PC-1 and PC-5 edit `judgmentsApart` there once
  PC-4 has landed.
- `lean/VE/Compose/Stack.lean` (PC-3, 1.3): `rewriters`, `stackOf` and `Contract.listedStacks`, which the stack rule
  reads. It imports `VE.Compose.Dispatch` only.

The imports, each one way:
- `Compose/Stack.lean` imports `Compose/Dispatch.lean`;
- `Compose/Matrix.lean` imports `Compose/Dispatch.lean`, `Compose/Stack.lean` and `Service/DocumentBase.lean`, and
  neither `Service/Document.lean` nor `Compose/Contract.lean`;
- `Service/Document.lean` imports `Service/DocumentBase.lean` and `Compose/Matrix.lean`;
- `Compose/Contract.lean` imports `Service/Document.lean` and `Compose/Stack.lean`.

So `Dispatch ← Stack ← Matrix ← Document ← Contract`, with `DocumentBase` below `Matrix` and `Document`, has no cycle.
The one-file stub cannot check this (section 9): PC-4's own `lake build` does, and a cycle fails it.

```lean
namespace VE.Compose.Matrix

/-- A document-mode refusal; `pending` defers to the environment's own first fault, as today's check 2 does. -/
inductive Refusal | pending (text : String) | refused (text : String)
  deriving DecidableEq, Repr

/-- A `.layer` profile other than `documents@1` and `judgments@0`, by its rows' interface (1.2). -/
def otherLayer (t : List ProfileRow) (p : String) : Bool :=
  t.any (fun r => r.profile == p && r.interface == .layer) && !["documents@1", "judgments@0"].contains p

/-- The profile of a list's route head: the row `routeOf` reads (the first head of `heads` with a listed row). -/
def headProfile (t : List ProfileRow) (ps : List String) : Option String :=
  heads.findSome? fun h => (t.find? fun r => r.slot == h.1 && ps.contains r.profile).map (·.profile)

/-- The lists each other layer's own transparency theorem covers (`Contract.LayerFacts`, 1.5), by layer. Empty on
main; a layer's row batch adds its entry with its theorem (`Contract.layer_evidence`). -/
def layerCovers : List (String × (List String → Bool)) := []

/-- The layer rule (row 17 of 4; PC-4 owns it). An other layer in a list its own theorem does not cover is refused
with E1: the layer, then the list's route head (`headProfile`), or else its first other profile. -/
def layerRuleIn (t : List ProfileRow) (covers : List (String × (List String → Bool))) (ps : List String) :
    Option String :=
  match ps.find? (fun p => otherLayer t p && !covers.any (fun x => x.1 == p && x.2 ps)) with
  | none => none
  | some l =>
    let p := (headProfile t ps <|> ps.find? (· != l)).getD "relational-fol@0"
    some (VE.Compose.unsupported s!"{l} with {p} is not implemented")

def layerRule (ps : List String) : Option String := layerRuleIn profileTable layerCovers ps

/-- The refusals at `environmentOf`'s site, in today's order and texts, then the layer rule; `environmentOf` calls
it where checks 1 to 4 are today, throwing `(environmentFault environment).getD r` for `.pending r` and `r` for
`.refused r`. -/
def documentRefusal (listed : List String) (senses : Bool) : Option Refusal :=
  if listed.contains "judgments@0" && (VE.Service.Document.judgmentsApart.find? listed.contains).isSome then
    (VE.Service.Document.judgmentsApart.find? listed.contains).map fun p =>
      .refused (VE.Service.Document.unavailable s!"judgments@0 with {p} needs its composed Lean route")
  else if listed.contains "judgments@0" && senses then
    some (.refused (VE.Service.Document.unavailable "judgments@0 with senses needs its composed Lean route"))
  else match VE.Compose.pendingWithDefaults listed with
  | some r => some (.pending r)
  | none =>
    let block := VE.Service.Document.blockOf listed
    if listed.contains "rights@0" && (block != .none || listed.contains "norm-defaults@0") then
      some (.refused (VE.Service.Document.unavailable
        "rights with norm-defaults, alternatives or risk needs its composed Lean route"))
    else if listed.contains "soft-norms@0" && !listed.contains "rights@0" &&
        (block != .none || listed.contains "norm-defaults@0" || listed.contains "readings@1") then
      some (.refused (VE.Service.Document.unavailable
        "soft-norms with norm-defaults, readings, alternatives or risk needs its composed Lean route"))
    else (layerRule listed).map Refusal.refused

/-- The pairs of a stack at positions `i < j`, ordered by `i`, then by `j`. -/
def stackPairs : List String → List (String × String)
  | [] => []
  | a :: rest => rest.map (a, ·) ++ stackPairs rest

/-- The stack rule over a list of listed stacks: a list whose stack has two or more rewriters and is not listed is
refused. The text names the first pair, in `stackPairs` order, whose two-profile stack is unlisted (E1); when every
pair is listed, it names the whole stack (E1s, 2.1). -/
def stackRefusalIn (listed : List (List String)) (ps : List String) : Option String :=
  let s := stackOf profileTable ps
  if s.length < 2 || listed.contains s then none
  else match (stackPairs s).find? (fun x => !listed.contains [x.1, x.2]) with
    | some (a, b) => some (VE.Compose.unsupported s!"{a} with {b} is not implemented")
    | none => some (VE.Compose.unsupported s!"stack {", ".intercalate s} is not implemented")

/-- The stack rule (row 7 of 4). -/
def stackRefusal (ps : List String) : Option String := stackRefusalIn Contract.listedStacks ps

/-- The refusals at `check`'s site, on the list as written: today's, then the stack rule. -/
def caseRefusal (ps : List String) : Option String :=
  if ["scope@0", "judgments@0"].all ps.contains then
    some (VE.Service.Document.unavailable "judgments@0 with scope@0 needs its composed Lean route")
  else stackRefusal ps

/-- The stack rule refuses every unlisted stack of two or more rewriters ... -/
theorem unlisted_refused (ps : List String) (h2 : 2 ≤ (stackOf profileTable ps).length)
    (hl : stackOf profileTable ps ∉ Contract.listedStacks) : ∃ e, stackRefusal ps = some e

/-- ... and M1 (coverage): every list it passes with two or more rewriters has a listed stack, hence
`RouteFacts` (`listed_evidence`). -/
theorem admitted_listed (ps : List String) (hd : stackRefusal ps = none)
    (h2 : 2 ≤ (stackOf profileTable ps).length) : stackOf profileTable ps ∈ Contract.listedStacks
```

**Where the stack rule is called.** On a list with `scope@0`, the document mode never reaches `check`'s site with
an unlisted stack: `checkDocSets` calls `decodeScope` (`Document.lean:1911`), whose `environmentOf (lowerScope …)`
(`:1891`) throws `CheckerUnavailable: document checks under acts@0 need its Lean profile route` first. So
`stackRefusal` is also called in `checkDocSets` and `checkDoc`, right after `gateOf` and before `decodeScope`. Both
entries begin with PC-1's clash validation (1.7), before the gate, on every request:

```lean
-- lean/VE/Service/Document.lean: the same two lines in `checkDoc` (:1898) and `checkDocSets` (:1910)
def checkDocSets (j : Json) : Except String Json := do
  if let some e := clashRefusal j then throw e                                   -- (new, PC-1) row 16
  if "scope@0" ∈ profilesOf j then do
    let _ ← VE.Compose.gateOf VE.Compose.profileTable (profilesOf j)
    if let some e := VE.Compose.Matrix.stackRefusal (profilesOf j) then throw e   -- (new, PC-4) row 7
    let D ← VE.Scope.decodeScope j
    let out ← VE.Scope.governSetsWith VE.Scope.governFast D
    let a ← checkCore (if (VE.Scope.governedSetUnits D).isEmpty then withUnits j out else withSets j out)
    pure (VE.Scope.foldGovernors D a)
  else checkCore j
```

**Fault order.** On every request, row 16 (`clashRefusal`) is first. Then, on a list with `scope@0`:
1. the gate (`gateOf`, in `checkDocSets` and `checkDoc`);
2. the stack rule, row 7;
3. `decodeScope`, whose `environmentOf` raises rows 1 to 5 in their order, then row 17 (the layer rule);
4. row 6, in `check` (`caseRefusal`, whose own stack rule then passes).

On a list without `scope@0`, `check`'s site raises row 7 (row 6 needs `scope@0`), and then `environmentOf` raises
rows 1 to 5 and then row 17. `scope_admission_sets` and `checkDocSets_pipeline` keep their statements; a listed stack
passes the new line, and so does every request whose exchange is one-to-one and, when it lists `judgments@0`, whose
twin's is too (1.7).

**The layer rule** (row 17, pc-d2 edit 5). It refuses with E1 any owned `.layer` profile other than `documents@1`
and `judgments@0` that appears in a list its own transparency theorem does not cover (`LayerFacts`, over the whole
admitted list, 1.5). PC-4 owns the rule. Each layer's row batch lifts it only for the lists its theorem covers, by an
entry of `layerCovers` and its case of `layer_evidence`. "Owned" is the site's: `documentRefusal` runs only after
`environmentOf` has refused every profile outside `ownedProfiles` (`Document.lean:683`), so a layer whose batch has
not made it owned still gets today's `CheckerUnavailable`. E1 needs two features, so the text names the layer and the
profile of the list's route head (`headProfile`, the row `routeOf` reads). Every admitted list has another profile,
because `relational-fol@0` is mandatory. `risk@0` beside `modality@0` (DEC 15) is its first instance (F4.9):
`UnsupportedProfile: modality@0 with risk@0 is not implemented`, until modality's agreement theorem with risk's
`might_lead_to` and `leads_to` lands and its row batch adds the entry. On main the rule refuses nothing, because
`profileTable`'s only `.layer` profiles are `documents@1` and `judgments@0` (F4.10).

**The record rule (pc-fid-rev, B2; PC-4 owns it).** The 3.1 matrix of the plan refused `layer` × `outside` "until
the outside route has `Content`", and so refused `judgments@0` beside `commitments@0`, whose interface PC-3 makes
`.outside` on its own slot `"commitments"` (1.1). That cell is for outside profiles that are route heads of the
document mode (`alternatives@0`, `risk@0`: `judgmentsApart`). `commitments@0` is not one: its slot is no head of
`heads`, it has its own service mode (`ve commitments`, commitments D13), and the chain never reads its block
(commitments D1, CM-2's `decodeDocument_ignores_commitments`). So the document mode reads such a profile as a
**document record**: every decoder reads the environment without it, as `documentLayers` already do (`Dispatch.lean`,
"each decoder reads the environment without them; the gate and the identities read the list as written"), and no
decoder reads its front-matter block.

```lean
-- lean/VE/Compose/Dispatch.lean (AR-10's; PC-4 edits it after `heads`, below `Matrix.lean`, so `documentLayers`
-- reads the rows with no import cycle)
namespace VE.Compose

/-- (B2) An own-mode outside profile: `.outside`, on a slot that is no route head of `heads`, so it has its own
service mode and no route in the document mode. None on main; `commitments@0` once CM-2 adds its row. -/
def recordProfile (t : List ProfileRow) (p : String) : Bool :=
  t.any fun r => r.profile == p && r.interface == .outside && !heads.any (·.1 == r.slot)

/-- (B2, PC-4; pc-fid-rev review) The document layers of a table: `judgments@0` and the table's records. -/
def documentLayersOf (t : List ProfileRow) : List String :=
  "judgments@0" :: (t.map (·.profile)).eraseDups.filter (recordProfile t)

/-- AR-10's list, derived from the rows by PC-4: `["judgments@0"]` on main, as today; `commitments@0` joins it with
CM-2's row, with no edit to the list (stub: `documentLayers'`, the list on `profileTableCM`). -/
def documentLayers : List String := documentLayersOf profileTable

end VE.Compose

namespace VE.Service.Document

/-- (B2) The case with its document's `commitments` front-matter block removed, every other byte as written
(`commitments@0` stays listed, so the environments, and the identities they give, are the case's). -/
def withoutCommitmentsBlock (j : Json) : Json

/-- (B2, PC-4) The document mode never reads a record's block: a case answers as the case without its `commitments`
block, verdict fields and unit statuses equal, a refusal the same refusal. Beside `judgments@0` the answer is then
G3's, which is stated for every list. -/
theorem checkDocSets_ignores_commitments (j : Json)
    (hr : VE.Compose.recordProfile VE.Compose.profileTable "commitments@0" = true)
    (hc : "commitments@0" ∈ profilesOf j) :
    (checkDocSets j).map verdictFields = (checkDocSets (withoutCommitmentsBlock j)).map verdictFields ∧
      (checkDocSets j).map unitStatuses = (checkDocSets (withoutCommitmentsBlock j)).map unitStatuses

/-- (B2) Discharged by commitments' CM-2 for its own mode's entry `run` and its answer without identities `fields`:
its decoders read the environment without `judgments@0`, so on G3's comparison pairs its answer with the layer is its
answer on G3's twin. -/
def CommitmentsBesideJudgments (run : Json → Except String Json) (fields : Json → Json) : Prop :=
  ∀ j, "judgments@0" ∈ profilesOf j → noUnitStatus j = true → swapInjective j = true →
    (run j).map fields = (run (withoutJudgments j)).map fields
```

So the cell is open in the document mode and staged in the commitments mode:
- **in the document mode (opened)**, a list with `commitments@0` has the route and the stack of the list without it
  (F4.11), its block is never read (`checkDocSets_ignores_commitments`), and `judgments@0` beside it is G3's;
- **in the commitments mode (staged on CM-2, a request row)**, a judged atom is a base predicate, because the mode's
  decoders read the environment without the document layers; `CommitmentsBesideJudgments` is the statement CM-2 is
  asked to prove for its entry (F4.16). Commitments' plan does not carry it yet: its D13 gives this composition to
  judgment-terms.

`documentLayers` is AR-10's list, and PC-4 derives its records from the rows (`documentLayersOf`), so the row's slot
and interface are its one owner and there is no second list to cross-check: on main the derived list is
`["judgments@0"]`, main's, and with CM-2's row it holds `commitments@0` too (F4.11). The rule adds no refusal and
admits nothing the list without the record does not admit: the identities read the list as written, so a case with
the record and its twin without it differ only there. `checkDocSets_ignores_commitments`
is vacuous on main (`recordProfile profileTable "commitments@0"` is false: no row) and binding from CM-2's row on,
which re-proves it with its row, as each layer's row batch re-proves the layer rule's cases. Commitments' own checks
(`BearerNotOrgan`, `BearerNotBound`, `NoRuleLabel`, `StrengthMismatch`) are its own mode's answers, never the document
mode's. Where the pilot's writer stubs commitments (`STUB[commitments]`), the stub fills the front-matter block entry
of a unit or of a candidate (its bearer and strength), never a unit's content; the bearer it names is the first
argument of the annotated rule's act (commitments D5).

**Any number of rewriters (pc-fid-rev, PC-4b, B6).** `stackRefusalIn` keeps its statement and texts. PC-4b changes
what it reads: `listedStacks` gains the stacks 1.5's listing rule names, each with its `listed_evidence` case from
`stack_evidence`, and `checkDocSets` and `checkDoc` run one pipeline call over the case rewriters (`pipelineOf …
docRewritersDiscourse`) in place of the scope branch and PC-6b's and PC-7b's lines, so that `stackRuns_all` holds.
`unlisted_refused` and `admitted_listed` keep their statements: a list the rule passes has a listed stack, and a
listed stack has its `RouteFacts` (`listed_evidence`). F4.12 to F4.14 are the fixtures.

The definitions above are written against main (`d25bc343b`), so their fixtures (F4.3) can be checked today. PC-4
lands after PC-1, PC-2a, PC-2b and PC-2c, so it writes them with the texts current then: section 4's rows 1, 2, 4
and 5 as those batches leave them. PC-5 deletes `caseRefusal`'s first branch, or the inline check at :1744 if PC-5
lands before PC-4. Later batches edit this module, not `Document.lean`.

The stack rule changes one class of answers. An unlisted stack, such as `acts@0` with `scope@0`, is refused by
E1's `UnsupportedProfile`: in `checkDocSets` and `checkDoc` when the list has `scope@0`, at `check`'s site
otherwise. Today it ends as `environmentOf`'s `CheckerUnavailable` (`acts@0` is not an owned profile). F4.4 records
each such list in `tests/data`, end to end through `checkDocSets`, and the review accepts this as the DRI's signed
rule (ruling 1(b)).

**Stacks of three or more rewriters.** Naming the stack's first two profiles is wrong once pairs are listed. After
PC-7b lists `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]`, the stack `["ve.discourse@1",
"acts@0", "scope@0"]` would say that resolved references and act phrases cannot be checked together, and that pair
is admitted. So the text names the first pair, over positions `i < j` ordered by `i` and then `j`, whose two-profile
stack is unlisted. When every pair is listed, it names the whole stack, with E1s's text (F4.7, F4.8). E1s is
registered before PC-7b lists a second pair (2.1).

The plan's grid (3.2) becomes a derived view:

```lean
/-- The smallest sorted list holding `p`, `q`, `relational-fol@0` and everything their rows require. -/
def closeReq (t : List ProfileRow) (p q : String) : List String

inductive Cell | admitted | refused (text : String)
  deriving DecidableEq, Repr

def cellOf (p q : String) : Cell :=
  let ps := closeReq profileTable p q
  match gateOf profileTable ps with
  | .error e => .refused e
  | .ok _ => match caseRefusal ps, documentRefusal ps false with
    | some e, _ => .refused e
    | none, some (.pending e) => .refused e
    | none, some (.refused e) => .refused e
    | none, none => .admitted
```

Moving the inline refusals changes no answer. That is checked by fixtures (F4.3), not by a theorem: the old inline
checks are deleted, not kept beside the new functions for a proof to compare against.

### 3.5 PC-5: `judgments@0` beside `scope@0`

Files: `lean/VE/Judgments/Chain.lean` (judgment-terms), `lean/VE/Scope/Wire.lean` (`foldGovernors`; scope's owner),
`Compose/Matrix.lean` (`caseRefusal`'s first branch deleted).

The layer reads each unit as the chain reads it after GOVERN: `checkCore` runs on `withUnits j out`, so a governed
unit's composed rule is its content. A governed unit therefore depends on its own judgments and on its governors'
conditions' judgments, in `J`'s order. The scan is `J.filter`, so the result is never a concatenation.

```lean
namespace VE.Judgments

/-- PC-5 (1). Dependence of joined contents: `J` filtered by either part's dependence, in `J`'s order. -/
theorem dependsOnC_append (defs : List VE.Definitions.Def) (J : List String) (cs ds : List Content) :
    dependsOnC defs J (cs ++ ds) =
      J.filter (fun j => (dependsOnC defs J cs ++ dependsOnC defs J ds).contains j)

/-- PC-5 (2), `govern_judged`: a carve-out governor adds its condition to the rule's reads. -/
theorem govern_carveOut_judged (defs : List VE.Definitions.Def) (J : List String) (N : VE.Norms.Node)
    (ψ : VE.Formula) :
    dependsOnC defs J [.rule { N with carveOuts := N.carveOuts ++ [ψ] }] =
      J.filter (fun j => (dependsOnC defs J [.rule N] ++ dependsOn defs J [ψ]).contains j)

/-- PC-5 (2), `govern_judged`: a plain narrowing conjoins its condition to the guard. -/
theorem govern_narrow_judged (defs : List VE.Definitions.Def) (J : List String) (N : VE.Norms.Node)
    (C : VE.Formula) :
    dependsOnC defs J [.rule { N with guard := .and N.guard C }] =
      J.filter (fun j => (dependsOnC defs J [.rule N] ++ dependsOn defs J [C]).contains j)
```

```lean
namespace VE.Scope

/-- PC-5 (3), scope's owner: a plain narrowing (`["and", "own", C]`, scope 1.4) makes the guard `["and", g, C]`,
which the chain decodes as `.and g C`. -/
theorem applyEffect_narrowing (u : String) (o g C : Json) (hg : o.getObjVal? "guard" = .ok g)
    (hC : hasOwn depthLimit C = false) :
    applyEffect u (.reguard (Json.arr #[.str "and", .str "own", C])) o =
      .ok (o.setObjVal! "guard" (Json.arr #[.str "and", g, C]))

/-- PC-5 (4). The fold keeps the chain's `judgments` member (`foldGovernors` today rebuilds the answer without it). -/
theorem foldGovernors_judgments (D : SDoc) (a : Json) :
    (foldGovernors D a).getObjValD "judgments" = a.getObjValD "judgments"
```

A `reguard` whose condition does not mention `own` replaces the guard (scope 1.4). The governed unit then no
longer reads its old guard, and its dependence is the composed rule's, by `dependsOnC`'s definition. No theorem
claims otherwise.

A governor unit has no content of its own. Its status is scope's fold of what it governs (`governorStatus`, the
weakest), so it is OPEN when a governed unit is OPEN. It is not a row of the usage map.

A governed `specified` unit whose governor's condition uses a bound judgment is refused with today's
`JudgmentNotChecked: <unit> <term>`, because its content now uses the judgment (F5.5). The author lists the
judgment in the unit's `open` meaning.

**PC-5b: a governor's own reading set beside readings (pc-fid-rev, B3; staged: after scope's SC-5 and PC-5).** The
stack `["scope@0", "readings@1"]` is listed on main, with `ScopeSetsFaithful` (1.5). Its order is GOVERN before
SUPERPOSE: GOVERN runs once per joint choice of the governed sets (`governSetsWith`, lf-14d's choices) and hands the
chain the governed sets (`withSets`); the chain's readings fold then reads every remaining set. On main the sets
governed per choice are those of `governedSetUnits` (scope 11.1): a governed unit's own set. Two kinds of set stay
refused, by scope, with scope's texts (row 19 of 4):
- a set on a governor's own unit, where the governing words themselves have readings (scope 11.1: "SC-5's case"):
  `ScopeReadings: <unit>`;
- a set that a frontier reach covers ("this", "these"): no frontier reach is admitted before SC-5, `UnsupportedProfile:
  scope@0 frontier reach requires SC-5`; after SC-5 a frontier reach with several live candidates is itself a reading
  set over the reach, coupled to the units it may cover (scope 1.7).

Both are scope's to define (its SC-5 addendum, scope 9.4, settles the per-choice `govern` over lf-14d's joint choices,
the fixing of a frontier reach and its recorded units). This plan's part is the composition, and it needs no new
statement: `ScopeSetsFaithful` and `ScopeRuns` are stated over `governedSetUnits`, `setChoices`, `governChoice` and
`governSets`, so once SC-5 extends `governedSetUnits` to these sets (and `setChoices` to the reach sets), the same
statements cover them. PC-5b, after SC-5 and PC-5, re-proves the `["scope@0", "readings@1"]` case of
`listed_evidence` on SC-5's functions, keeps `foldGovernors_judgments` and `dependsOnC_append` for the governors SC-5
adds (a governor's judgments are read by the units it governs, in `J`'s order, under every choice), and adds F5.6 to
F5.8. The designed rule a writer follows, under the full ruled grid:
- the governor's sentence with several readings is a reading set **on the governor's own unit**, each reading in the
  governor unit's own form (a reading that states no rule, or one that adds a rule beside the governor's effect);
  the governor's effect and reach sit in the scope block, under every choice of that set;
- a deictic reach ("this") is the `frontier` reach; its candidates are scope's (layout only, scope 1.7);
- a governed list item's readings are written **in the item's own form** (a `part` under a frame, a `norm` under a
  re-guard or carve-out alone; scope 11.1), and are governed per choice on main today; a reading that changes what
  the lead-in supplies (its act, its strength) is a reading of the lead-in, so it is a set on the governor's own unit,
  coupled to the item's set;
- under each joint choice the document is governed by `govern (atChoice D ch)`, and a fault under one choice refuses
  the document (`ScopeSetsFaithful`, its second clause); a resource limit stays UNKNOWN.

Where the pilot's writer stubs scope (`STUB[scope]`), the stub fills the scope block's governor (unit, reach,
effect) and the reading set's unit; this plan's part is the stack `["scope@0", "readings@1"]` and its order.

### 3.6 PC-6a, PC-6 and PC-6b: the decision key; `acts@0` beside soft-norms and rights; the constitution stack

**PC-6a, the decision key (soft-norms' ownership; before PC-9 and PC-6).** File: `lean/VE/SoftNorms/Tree.lean`
(soft-norms' file; its owner reviews; this plan builds it). It adds `SoftNode.splitFrom : Option String := none`,
`decisionRule` and `decisionRule_unsplit` (1.10), and nothing else. No decoder sets `splitFrom`, so every key is
today's and no answer changes. Its fixture is F6.1b. PC-9's `dfltUniformOf` reads `decisionRule` from it (1.9).

**PC-6.** Files:
- `lean/VE/Acts/Soft.lean` (new; act phrases);
- `lean/VE/SoftNorms/Tree.lean` (the two names, `keyedDecisions` and `decisions`, on PC-6a's field; soft-norms'
  owner reviews);
- `lean/VE/SoftNorms/Soften.lean`, `Once.lean` and `Semantics.lean`, `lean/VE/Defaults/Meaning.lean`, and the
  `Readings/` proofs 1.10 lists (the restated invariant; soft-norms' and defeasible's owners review);
- `lean/VE/SoftNorms/Phases.lean` (`declarations` keeps `acts@0` and calls W1's decoder with `acts := true`);
- `lean/VE/Compose/Dispatch.lean` (`actsRefuses` loses `soft-norms@0` and `rights@0`; `gate_acts` revised);
- `ve/profile_table.json` (regenerated).

```lean
namespace VE.SoftNorms

/-- The `soft-norms@0` environment decoder with W1's environment decoder under the act hook, with the
inherited profiles plus `acts@0`. -/
def strippedOf (environment : Json) (profiles : List String) : Json

/-- PC-6 (1). One regulated-act decoder: soft's regulated declarations are W1's, act hook included. Rights reads
them through soft's decoder (`decodeRightsSource`), so it gets the same declarations. -/
theorem declarations_acts (environment : Json) (profiles : List String) (ne : VE.Norms.Wire.NormsEnvironment)
    (s : SoftEnv) (h : Phases.declarations environment profiles = .ok (ne, s)) :
    ∃ ne', VE.Norms.Wire.decodeNormsEnvironment (strippedOf environment profiles) (displayConstants := true)
      (acts := true) = .ok ne' ∧ ne'.regulated = ne.regulated
```

```lean
namespace VE.Acts

/-- A soft document split by a checked elaboration `E`, the pair `elaborateMap A` returns (Elaborate.lean:151).
`E.1` carries each part's act, which `splitReg` (Elaborate.lean:93) builds from `A`'s atoms and fixed phrases;
`E.2` is the split map. The map alone does not determine the parts: it holds names and indices only (F6.9). Each
part copies its source's mode, rank, alterable parties and exception, and reads its decisions
(`splitFrom := some (decisionRule N)`). -/
def splitSoft (E : VE.NormDefaults.UDoc × SplitMap) (D : VE.SoftNorms.SoftDoc) : VE.SoftNorms.SoftDoc

/-- PC-6 (2). Split rules share one decision: the exception and every switch. -/
theorem split_shares_decisions (A : ActsDoc) (E : VE.NormDefaults.UDoc × SplitMap) (hE : elaborateMap A = .ok E)
    (D : VE.SoftNorms.SoftDoc) (hA : A.U.D = D.base) (N : VE.SoftNorms.SoftNode) (hN : N ∈ D.T.nodes)
    (P : VE.SoftNorms.SoftNode) (hP : P ∈ (splitSoft E D).T.nodes) (i : Nat) (hm : (P.name, N.name, i) ∈ E.2.rules) :
    P.mode = N.mode ∧ P.rank = N.rank ∧ P.alterable = N.alterable ∧ P.exception = N.exception ∧
      VE.SoftNorms.exceptedName P = VE.SoftNorms.exceptedName N ∧
      ∀ π, VE.SoftNorms.offName P π = VE.SoftNorms.offName N π

/-- PC-6 (3). The argument mapping: a part's decision atoms take its source's argument sorts, in order. -/
theorem split_sorts (A : ActsDoc) (E : VE.NormDefaults.UDoc × SplitMap) (hE : elaborateMap A = .ok E)
    (D : VE.SoftNorms.SoftDoc) (hA : A.U.D = D.base) (N : VE.SoftNorms.SoftNode) (hN : N ∈ D.T.nodes)
    (P : VE.SoftNorms.SoftNode) (hP : P ∈ (splitSoft E D).T.nodes) (i : Nat) (hm : (P.name, N.name, i) ∈ E.2.rules) :
    VE.SoftNorms.sortsOf (splitSoft E D) P.pred = VE.SoftNorms.sortsOf D N.pred

/-- PC-6 (4). Preservation, before any refusal is lifted: under strict outranking the split document has the
source's decisions, one per decision key (1.10's table). -/
theorem split_decisions (A : ActsDoc) (E : VE.NormDefaults.UDoc × SplitMap) (hE : elaborateMap A = .ok E)
    (D : VE.SoftNorms.SoftDoc) (hA : A.U.D = D.base) (hs : D.soft.outranking = .strict) :
    VE.SoftNorms.decisions (splitSoft E D) = VE.SoftNorms.decisions D

/-- PC-6 (5). Dropping the soft attributes commutes with splitting: the split document's base is the checked
elaboration's document. -/
theorem splitSoft_base (A : ActsDoc) (E : VE.NormDefaults.UDoc × SplitMap) (hE : elaborateMap A = .ok E)
    (D : VE.SoftNorms.SoftDoc) (hA : A.U.D = D.base) :
    (splitSoft E D).base = E.1.D
```

Every PC-6 split statement is stated under the elaboration's success (`hE`) and the alignment of the acts
document with the soft document (`hA`). `splitSoft_base` was stated on `splitMap A` and `splitDoc A` with no
success hypothesis. Its revision reads the elaboration's own result, so the parts' acts are the ones the checked
elaboration produced.

**`gate_acts`, revised under review (C12).** One revision of `gate_acts` is owned by act phrases. CI-5's (CIX3)
lands first, and PC-6 follows it or merges into the same reviewed revision. CI-5's exact addition is the disjunct
`r = .speechActs` (CI-5's revised `gate_acts` in commands-imperatives.md, on that plan's branch). PC-6's change is three disjuncts: `.soft`, `.rights`
and `.clauses`. On main, acts' `rights@0` refusal is the only thing that keeps `right-clauses@0` out of an acts
list (`Dispatch.lean:1178`). Once PC-6 drops it, `heads` puts `clauses` before every chain route (`:825`), so
`["acts@0", "norms@0", "relational-fol@0", "right-clauses@0", "rights@0", "soft-norms@0"]` gates to `.clauses`
(F6.8). No parallel `gate_acts_chain` theorem is added.

```lean
theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : Route) (hg : gateOf profileTable ps = .ok r) :
    gateOf profileTable (ps.erase "acts@0") = .ok r ∧
      (r = .norms ∨ r = .normDefaults ∨ r = .readings ∨ r = .speechActs ∨ r = .soft ∨ r = .rights ∨ r = .clauses)
```

PC-7b adds `r = .discourse` to this statement, in the same reviewed revision as `gate_scope` (3.7).

**Wire contract (C6).** PC-6 changes the public `soft-norms@0` decoder. A named `soft-norms@0` wire-contract step
lands before PC-6 lifts any refusal: the wire-contract owner's step, in shadow, off the verdict and identity
paths (PX3, MCX3). PC-6 also adds its rows to rd-9's relay-binding inventory (D9).

**AT-3a and PC-6 share `lean/VE/Norms/Wire.lean`** (the at3a-order amendment, item 1). AT-3a may land before PC-6:
whichever of the two merges second rebases on `Norms/Wire.lean`, and neither hand-merges the other's lines. AT-3a
hooks its attitude guard node only into `normFields`. The `acts@0` + `soft-norms@0` refusal (row 8 of 4) stays until
PC-6 lifts it. AT-3a's SR-6 fixture (an attitude guard node decoded through `normFields` on both the norms and the
soft admission paths, and today's `array expected` without `attitudes@0`) stays selected in PC-6. PC-6 adds the
amendment's condition (d) fixture, F6.11 (C): a soft norm whose regulated act goes through the unified decoder and
whose guard holds an attitude node, decoded once, through `normFields`. Its input needs AT-3a's guard node, so it is
built on the rebased `Norms/Wire.lean` by whichever of PC-6 and AT-3a merges second (section 9, open point 2).

**PC-6b, the constitution stack (act phrases' `actsRewriter`; scope's owner reviews the order).** `["acts@0",
"scope@0"]` is not listed until PC-6b proves `ActsScopeRuns`: acts' case rewriter, then GOVERN on the split case
(scope's SC-4 reads `SplitMap`), then the chain. PC-6b builds `actsRewriter`, `splitMapOfCase`, `docRewritersActs`,
`ruleParts`, `SplitReach` and `ActsScopeRuns`; it proves `ActsScopeRuns`, `ActsFaithful` and `ActsPreserves`, and it
registers the stack: `["acts@0", "scope@0"]` joins `listedStacks` with its `RouteFacts` entry (1.5), so
`listed_evidence` covers it. Its place in the order is after PC-4 (the stack rule and `listedStacks`), PC-6 (acts
beside soft-norms), ap-3d (the acts relay) and scope's SC-4 (the `SplitMap` reach); PC-7b comes after it. Until
then the stack rule refuses the set (F4.4); after it, F4.4's list passes the rule (F6.13) and F6.12 holds.

```lean
-- lean/VE/Compose/Contract.lean (PC-6b)
/-- (new, act phrases) acts' split as a case rewriter. -/
def actsRewriter : Rewriter Json

def docRewritersActs (p : String) : Option (Rewriter Json) :=
  if p == "scope@0" then some scopeRewriter else if p == "acts@0" then some actsRewriter else none

/-- (new, act phrases) The names a rule stands for after the split: its parts in `M.rules`, or itself. -/
def VE.Acts.ruleParts (M : VE.Acts.SplitMap) (n : String) : List String :=
  match M.rules.filter (·.2.1 == n) with
  | [] => [n]
  | xs => xs.map (·.1)

/-- The acts × scope `SplitMap` lemma (scope's SC-4 reads `SplitMap.rules`, scope-PLAN:1169). GOVERN on the split
case `D` has the case's unit ids, governors and recorded reaches (`D₀`, the case as written), a `rules` reach names
the parts of every rule it names, and each governor's effect is as written (DRI 2026-10-30, item 1: an effect the
split would have to rewrite is not designed here, so `SplitReach` does not hold on it). -/
def SplitReach (M : VE.Acts.SplitMap) (D₀ D : VE.Scope.SDoc) : Prop :=
  D.layout.map (·.id) = D₀.layout.map (·.id) ∧
  D.governors.map (fun g => (g.id, g.unit, g.units)) = D₀.governors.map (fun g => (g.id, g.unit, g.units)) ∧
  (∀ g ∈ D.governors, ∀ g₀ ∈ D₀.governors, g.id = g₀.id →
    match g₀.reach with
    | .rules ns => g.reach = .rules (ns.flatMap (VE.Acts.ruleParts M))
    | r => g.reach = r) ∧
  ∀ g ∈ D.governors, ∀ g₀ ∈ D₀.governors, g.id = g₀.id → g.effect = g₀.effect

/-- The constitution set's ordered pipeline: acts' split, then GOVERN on the split case, then the chain; with the
`SplitMap` conjunct (1.5). -/
def ActsScopeRuns : Prop :=
  ∀ j ans, VE.Service.Document.checkDocSets j = .ok ans → "acts@0" ∈ VE.Service.Document.profilesOf j →
    "scope@0" ∈ VE.Service.Document.profilesOf j →
    ∃ j₁ M D₀ D j₂ a, actsRewriter.run j = .ok j₁ ∧ VE.Acts.splitMapOfCase j = .ok M ∧
      VE.Scope.decodeScope j = .ok D₀ ∧ VE.Scope.decodeScope j₁ = .ok D ∧ SplitReach M D₀ D ∧
      scopeRewriter.run j₁ = .ok j₂ ∧
      pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewritersActs) j = .ok j₂ ∧
      VE.Service.Document.checkCore j₂ = .ok a ∧ ans = VE.Scope.foldGovernors D a
```

`splitMapOfCase` (PC-6b, act phrases) is the split map of a case. `SplitReach` is stated on what scope's block
decodes to (`SDoc`), so it does not depend on how `actsRewriter` writes the case. (pc-fid-rev) PC-6b also proves
`SplitReach` for `actsRewriter` over every case, not only under a successful `checkDocSets` (the statement PC-4b's
`PairFacts` names as its first entry, 1.5); `ActsScopeRuns`' conjunct follows from it.

**PC-6c: acts beside readings (pc-fid-rev, B1; staged: after act phrases' readings elaboration, PC-6b and PC-4b).**
The grid's cell was "single acts; O": on the readings route only AP-1's single acts may be declared (act-phrases
D-33, `readings_lexical_only`), because "nothing elaborates a reading set's candidates" until a readings elaboration
"with its own candidate elaboration and preservation theorems" passes its own statement review (act-phrases SR8,
finding F11). That elaboration is act phrases': how a candidate's joined act is carried (a W2 candidate holds one
rule, composition's `Content.norm`) is act phrases' and readings' design, not this plan's. The composition is this
plan's, and it can be stated now, independently of that representation: **under every compatible choice, acts beside
readings is acts on the choice's document.**

```lean
-- act phrases' readings elaboration (a STUB here; act-phrases SR8, F11; not designed by this plan)
def VE.Acts.choiceActs (D : VE.Readings.Doc) (c : VE.Readings.Choice) : VE.Acts.ActsDoc

-- lean/VE/Compose/Contract.lean (PC-6c; pc-fid-rev review)
/-- (stub) The environment, front matter and source units the document mode's `check` reads a case with. -/
def caseChain (j : Json) :
    Except String (VE.Service.Document.Env × Json × List VE.Service.Document.SourceUnit)

/-- The document the composed route checks under choice `c` of the case `j₁`: the choice document of `chainDoc` on
`j₁`. -/
def readingsChosen (j₁ : Json) (c : VE.Readings.Choice) : Except String VE.Rights.RightsDoc := do
  let (E, front, units) ← caseChain j₁
  let (N, _) ← VE.Service.DocumentChain.chainDoc E front units
  pure (VE.Readings.choiceDoc N.D c).1

/-- (PC-6c) Over every case: acts' split keeps every reading set's shape, in order, and the couplings and the
narrowings; and under every compatible choice `c` of the source's reading document, the document the composed route
checks on the split case is PC-6's split of the source's choice document, under that document's checked
elaboration. -/
def ActsChoiceFaithful : Prop :=
  ∀ j j₁, actsRewriter.run j = .ok j₁ →
    (caseSets j₁).map setShape = (caseSets j).map setShape ∧ caseChoiceLinks j₁ = caseChoiceLinks j ∧
    ∀ E front units N Xf (c : VE.Readings.Choice) (M : VE.NormDefaults.UDoc × VE.Acts.SplitMap),
      caseChain j = .ok (E, front, units) → VE.Service.DocumentChain.chainDoc E front units = .ok (N, Xf) →
      VE.Readings.Compatible N.D c → VE.Acts.elaborateMap (VE.Acts.choiceActs N.D c) = .ok M →
      (VE.Acts.choiceActs N.D c).U.D = (VE.Readings.choiceDoc N.D c).1.soft.base →
        ∃ X, readingsChosen j₁ c = .ok X ∧ X.soft = VE.Acts.splitSoft M (VE.Readings.choiceDoc N.D c).1.soft
```

The statement is over cases, as every pair lemma is (1.5): `j` is the case as written and `j₁` the case after acts'
split. `readingsChosen j₁ c` is defined, not a stub: the choice document of PC-2b's `chainDoc` (3.2) on `j₁`, so what
the document mode's readings branch checks under `c`. `choiceActs D c`, act phrases', is the acts document of the
choice's reading-free document (`choiceDoc`, main's, `Readings/Choice.lean:96`). The first two conjuncts are what
SUPERPOSE reads of the case (`setShape`, `caseSets` and `caseChoiceLinks`, 3.7): acts' split keeps them, which 1.5's
argument needs for this pair. The third is a transparency theorem: acts and readings meet only through the choice,
and under each choice the answer is the parts' answer, PC-6's split (`splitSoft`, 3.6) of the source's choice
document, whose own meaning `ActsFaithful` and `split_shares_decisions` give. With it, the stack `["acts@0",
"readings@1"]` (rank order: ACTS 1a, then SUPERPOSE 3) has `RouteFacts` by the generic clause: `StackRuns`,
`RewriterFacts` of both (`readingsFaithful` is main's), and `PairFacts ("acts@0", "readings@1") =
ActsChoiceFaithful`. PC-6c, after act phrases' readings elaboration (which lifts D-33 under its own review), PC-6b
(`actsRewriter`) and PC-4b (the generic clause):
- proves `ActsChoiceFaithful` for `actsRewriter` and the elaboration's `choiceActs`;
- lists `["acts@0", "readings@1"]` and, by 1.5's listing rule, `["acts@0", "scope@0", "readings@1"]` (its pairs are
  PC-6b's, main's and this one), with their `listed_evidence` cases;
- adds F6.14 to F6.16.

The designed rule a writer follows, under the full ruled grid: a joined act inside a reading candidate is written in
acts' notation, as in a fixed unit (an "A or B" act under *must* stays one act, its bearer chooses; joined acts under
*must* split into part rules `<rule>-a<i>`, one decision per source rule, PC-6); one split per predicate, so every rule
on a split predicate, in a fixed unit or in any candidate, is split by the same `SplitMap`; under each choice the
checked document is the split of the chosen document; a candidate whose content the elaboration cannot carry stays
pending (`content: null`), its rows `unknown`, never dropped. Until PC-6c the stack rule refuses the pair with
`UnsupportedProfile: acts@0 with readings@1 is not implemented` (row 7, F6.14), before the readings route's own D-33.

**An act phrase with more than one derivation inside a candidate (pc-fid-rev2, R2).** The derivations are act
phrases': the meanings `VE.Acts.readings` lists, in derivation order (act-phrases 1.6, 5.2). A split object, or a
split marker's list, followed by a modifier has two: the modifier over the last part, or over every part (act-phrases
5.2, `PXh`; F6.17 computes both for the fixture's phrase). Composition never chooses one of them, so a candidate
whose act has `n ≥ 2` derivations is written in one of two ways:
- **one candidate per derivation**: `n` candidates in its place, each holding the same rule words and naming its
  derivation by its index in act phrases' order (label axis `act`, values `1` to `n`), beside the candidate's own
  labels (3.2's coupling rule: a coupled axis is carried by every candidate). With an outer set (RS1's `cond`,
  `uncond`, `ov`), the candidates are the pairs: `cond-1`, `cond-2`, `uncond-1`, `uncond-2`, and `ov`, which holds no
  act;
- **or a narrowing** (document 88-91) that keeps the candidates of the derivations a cited source unit supports.

Under each choice the chosen candidate's act then has one derivation, so it has one reading under its op (act
phrases' `table`: three atoms under *must*, F6.17), and the checked document is PC-6's split of the choice's document
(`ActsChoiceFaithful`): `in the annual report` on the last part rule under `cond-1`, on every part rule under `cond-2`.
Two candidates of one set may name two derivations of one phrase, because no choice's document holds both. How a
candidate carries its derivation on the wire is act phrases' readings elaboration's (act-phrases SR8, F11; AP-4's
source names the phrase and the sets it is read into); this plan does not design it. If that elaboration cannot fix
a candidate to one derivation, the acts and readings stack cannot state the nesting soundly: the act is a GAP owned
by act phrases, the candidates that hold it stay pending (`content: null`), their rows `unknown`, and
`ActsChoiceFaithful` binds none of their choices (it holds under `elaborateMap (choiceActs N.D c) = .ok M` only; 9,
open point 10). Never one derivation without a narrowing: a candidate that writes the phrase as one act, with no
derivation named, declares a phrase with two meanings, which act phrases refuse at the declaration with D-15
(`InvalidInput: act phrase for <name> has more than one reading: 1. … 2. …`, row 21; F6.17 gives its text for the
fixture). A frame declaration chosen to remove a derivation the source's words have is a narrowing too, and needs
the same cited reason: the marker "in" declared as an argument marker instead of a modifier marker leaves one
derivation, the modifier's words on every part (section 9's second mutant).

### 3.7 PC-7a and PC-7b: discourse beside the chain, scope and acts

PC-7a is composition-PLAN S4, built in composition's own lane. It has no dependency on PC-3: S4 wires `dispatch`,
and nothing in it reads `Rewriter`.

PC-7b states two lemmas over S4's names, which S4's specification fixes (`resolveDocument`, composition-PLAN
S4), and over acts' case split map (PC-6b, act phrases). PC-7b comes after PC-7a, PC-6b and sc-1c.

```lean
namespace VE.Discourse

/-- PC-7b (1). Resolution keeps unit ids, layout and each governor's recorded reach (one `ContentName`). -/
theorem resolve_then_govern (environment j resolved : Json) (h : resolveDocument environment j = .ok resolved) :
    (VE.Scope.decodeScope resolved).map (fun D => (D.layout.map (·.id), D.governors.map (·.units))) =
      (VE.Scope.decodeScope j).map (fun D => (D.layout.map (·.id), D.governors.map (·.units)))

/-- PC-7b (2). Resolution introduces no name (`resolve_no_new_symbols`), so acts' split map is unchanged. -/
theorem resolve_then_split (environment j resolved : Json) (h : resolveDocument environment j = .ok resolved) :
    (VE.Acts.splitMapOfCase resolved).map (·.rules) = (VE.Acts.splitMapOfCase j).map (·.rules)
```

**`gate_scope` and `gate_acts`, revised under review in one revision.** `gate_scope`'s docstring says "never ...
the discourse route". PC-7b makes that false, so the statement is revised, not shadowed by a new theorem. PC-7b also
deletes acts' `ve.discourse@1` refusal, so an acts list can gate to `.discourse` (`heads` puts `discourse` first,
`Dispatch.lean:825`). `gate_acts` therefore gains `r = .discourse` in the same reviewed revision as `gate_scope`,
owned by act phrases (C12), after 3.6's revision (F7.2):

```lean
theorem gate_scope (ps : List String) (h : "scope@0" ∈ ps) (r : Route) (hg : gateOf profileTable ps = .ok r) :
    gateOf profileTable (ps.erase "scope@0") = .ok r ∧
      (r = .discourse ∨ r = .clauses ∨ r = .readings ∨ r = .rights ∨ r = .soft ∨ r = .normDefaults ∨ r = .norms)

theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : Route) (hg : gateOf profileTable ps = .ok r) :
    gateOf profileTable (ps.erase "acts@0") = .ok r ∧
      (r = .norms ∨ r = .normDefaults ∨ r = .readings ∨ r = .speechActs ∨ r = .soft ∨ r = .rights ∨ r = .clauses ∨
        r = .discourse)
```

PC-7b also lists `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]` in `listedStacks`, each with its
`RouteFacts` entry (1.5): the stack's run statement, discourse's own faithfulness and preservation, and the other
rewriter's. Each is written out as a `Prop`. S4's names (`resolveContent`, `positions`, `formulaMentions`,
`IntendedAt`, composition-PLAN S4) are S4's specification's, and `resolveCase` is `resolveDocument` on a case's
document under its front matter's environment. The run statements are proved from S4's `composed_admission` with
`resolve_then_govern` or `resolve_then_split`. PC-7b lists two pairs, so E1s is registered before it lands (2.1).

```lean
-- lean/VE/Compose/Contract.lean (PC-7b)
/-- RESOLVE as a case rewriter: S4's resolution of the case's document. -/
def discourseRewriter : Rewriter Json where
  profile := "ve.discourse@1"
  run := fun j =>
    if "ve.discourse@1" ∈ VE.Service.Document.profilesOf j then VE.Discourse.resolveCase j else .ok j
  on := fun j => decide ("ve.discourse@1" ∈ VE.Service.Document.profilesOf j)
  writes := []

def docRewritersDiscourse (p : String) : Option (Rewriter Json) :=
  if p == "ve.discourse@1" then some discourseRewriter else docRewritersActs p

/-- Discourse's own faithfulness (S4's `resolve_position_faithful`): every formula position of a resolved content
means what the unit's references intend. -/
def DiscourseFaithful : Prop :=
  ∀ (E : VE.Environment) (K : VE.Discourse.Manifest) (unit : String) (c c' : VE.Compose.Content),
    VE.Discourse.resolveContent E K unit c = .ok c' → ∀ (k : Nat) (ctx : List String) (A : VE.Formula),
      (VE.Discourse.positions c')[k]? = some (ctx, A) → ∀ S : VE.Structure.{u}, S.Admissible E →
        ∀ ρ : VE.Valuation S, VE.Valuation.Typed S ctx ρ → (A.denote S ρ ↔ VE.Discourse.IntendedAt E K unit k S ρ)

/-- Discourse's semantic preservation (S4's `resolve_identity`): the content of a unit whose formulas mention no
reference is unchanged. -/
def DiscoursePreserves : Prop :=
  ∀ (E : VE.Environment) (K : VE.Discourse.Manifest) (unit : String) (c : VE.Compose.Content),
    VE.Discourse.formulaMentions K unit = [] → VE.Discourse.resolveContent E K unit c = .ok c

/-- The run statement of `["ve.discourse@1", "scope@0"]`: RESOLVE, then GOVERN on the resolved case, then the chain
and scope's fold. -/
def DiscourseScopeRuns : Prop :=
  ∀ j ans, VE.Service.Document.checkDocSets j = .ok ans → "ve.discourse@1" ∈ VE.Service.Document.profilesOf j →
    "scope@0" ∈ VE.Service.Document.profilesOf j → "acts@0" ∉ VE.Service.Document.profilesOf j →
    ∃ j₁ D j₂ a, discourseRewriter.run j = .ok j₁ ∧ VE.Scope.decodeScope j₁ = .ok D ∧ scopeRewriter.run j₁ = .ok j₂ ∧
      pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewritersDiscourse) j = .ok j₂ ∧
      VE.Service.Document.checkCore j₂ = .ok a ∧ ans = VE.Scope.foldGovernors D a

/-- The run statement of `["ve.discourse@1", "acts@0"]`: RESOLVE, then acts' split, then the chain. -/
def DiscourseActsRuns : Prop :=
  ∀ j ans, VE.Service.Document.checkDocSets j = .ok ans → "ve.discourse@1" ∈ VE.Service.Document.profilesOf j →
    "acts@0" ∈ VE.Service.Document.profilesOf j → "scope@0" ∉ VE.Service.Document.profilesOf j →
    ∃ j₁ j₂, discourseRewriter.run j = .ok j₁ ∧ actsRewriter.run j₁ = .ok j₂ ∧
      pipeline (pipelineOf profileTable (VE.Service.Document.profilesOf j) docRewritersDiscourse) j = .ok j₂ ∧
      VE.Service.Document.checkCore j₂ = .ok ans
```

Each run statement excludes the third rewriter: a list with all three has the stack `["ve.discourse@1", "acts@0",
"scope@0"]`, which is not listed, so the stack rule refuses it (F4.7). The fixtures are F7.3 to F7.5. (pc-fid-rev)
PC-4b lists that triple by 1.5's listing rule, with the generic clause of `RouteFacts`; PC-7b's two run statements
keep their exclusions and are the `StackRuns` of their pairs.

**PC-7c: discourse beside readings (pc-fid-rev, B4; after PC-7a, PC-7b and PC-4b).** The grid's cell Rd × Dc was
"s→PC-7a", but no batch listed the stack `["ve.discourse@1", "readings@1"]`, so the stack rule refused it (F4.8). S4
(PC-7a) is designed for it: `resolveContent` and `positions` are over composition's `Content`, which is the content
of a reading candidate as well as of a unit (composition.md 1.6; composition-PLAN S4: "a reading candidate's content
… shared by S1, S2 and S4"), and `composed_admission` dispatches the base list, `readings@1` included, on the resolved
document. What the readings route reads of the case is the sets' shapes, the couplings and the narrowings (lf-14d's
enumeration reads nothing else, scope 11.2's `shapeOf`), so the pair's lemma is that RESOLVE keeps them:

```lean
namespace VE.Compose.Contract

/-- (PC-7c) The reading sets of a case's document, from its front matter, in order; its couplings and narrowings. -/
def caseSets (j : Json) : List Json
def caseChoiceLinks (j : Json) : Json × Json

/-- (PC-7c) What the readings route reads of a set to enumerate its choices: its id, unit and version, and its
readings' ids, in order. -/
def setShape (s : Json) : String × String × Nat × List String :=
  (VE.Scope.idOf s, VE.Scope.setUnit s, VE.Scope.setVersion s, (VE.Scope.readingsJson s).map VE.Scope.idOf)

/-- (PC-7c, B4) RESOLVE keeps every reading set's shape, in order, and the couplings and the narrowings: it rewrites
the readings' contents alone, each through `resolveContent` at its set's unit, so `DiscourseFaithful`, stated over
every `Content`, covers them. -/
def ResolveKeepsSets : Prop :=
  ∀ j j', discourseRewriter.run j = .ok j' →
    (caseSets j').map setShape = (caseSets j).map setShape ∧ caseChoiceLinks j' = caseChoiceLinks j
```

PC-7c proves `ResolveKeepsSets` from S4's `resolveDocument` (it maps `resolveContent` over every content, and copies
every other byte), proves `StackRuns ["ve.discourse@1", "readings@1"]` (PC-7b's RESOLVE line, then `checkCore`, whose
readings route superposes the resolved sets), lists the pair with its generic `RouteFacts` (`DiscourseFaithful`,
`DiscoursePreserves`, `readingsFaithful`, `ResolveKeepsSets`), and, by 1.5's listing rule, lists
`["ve.discourse@1", "scope@0", "readings@1"]`. Its fixtures are F7.6 to F7.8. So a reference inside a reading
candidate resolves under each candidate as it does in a unit, the choices are the same, and the per-choice answers
are those of the same document with the reference written out. A reference S4 resolves is a **formula position**
(`positions`): a term of a guard, a carve-out or an assertion. Words inside an act phrase are no position (act
phrases' identity is the phrase's canonical string), so a reference there stays words of the act, and the writer who
needs it resolved writes it as an argument of the act's predicate. A collective antecedent ("this content", two
earlier outputs together) is outside discourse's scope (discourse.md: collective plurals); where the pilot's writer
stubs it (`STUB[discourse]`), the stub fills that argument position.

### 3.8 PC-9: typed priority, and the "no exception" statements

PC-9 builds the statements of 1.8 and 1.9 with their fixtures, and the guard. It proves:
- `precedence_apart`, by `rfl` after unfolding;
- `dfltUniform_legacy`, by `List.append_nil` and the two `noneOr` cases.

Its prerequisites are PC-3, PK-1's `Pack.conditions` and PC-6a's `decisionRule` (1.9). Defeasible's named batch
DF-U proves `dfltUniform_sound` after PC-9. EXP-D3 decides `record_eq_dflt` (3.9). F6.7 is built in whichever of
PC-6 and PC-9 merges second.

The guard is one line in `defaultsRows` (`lean/VE/Defaults/Route.lean`): a defaults kind whose packs satisfy
`providerConditions` answers `providerRefusal`, rendered by E1d (2.1).

### 3.9 Statements the experiments own

- **EXP-D3** proves, on coherent documents with weighing's WG-6 record, that where no stated condition holds the
  record and `dfltUniform` admit the same bases (`record_eq_dflt`, its statement fixed by EXP-D3 against WG-6's
  record type), or finds a counterexample of at most three rules. Until either, the guard refuses.
- **EXP-O1** states `alt_soft_transfers`: alternatives' slot premises (`BaseAdmissibleAlt`) as a constraint pack
  over the soft chain, with `Transfers` and the followability certificate unchanged. Statements only.
- **EXP-G1** decides whether `X`'s order matters for `Sat`, `Transfers` and `acceptanceXV` when every name is
  declared by some pack of the list.
- **EXP-J1** writes no product code. Its result informs JT-4 (2.4).

### 3.10 PC-11: one mixed-kind candidate type, its premises gated

File: `lean/VE/Compose/CrossContent.lean` (new; owner `VE.Compose.Content`, composition). PC-11 comes after WG-3,
AT-2, AT-3a, PC-9 and EXP-G1. `CrossContent` is the only mixed-kind candidate type (DEC 13): attitudes' AT-8 uses its
`attitude` case and adds none, and modality's MD-2 adds its modal-claim case here, under this interface.

```lean
-- lean/VE/Compose/CrossContent.lean (new; PC-11)
namespace VE.Compose

/-- A candidate of a mixed-kind reading set: today's content (1.6 of composition.md), or an attitude candidate,
whose claim is attitudes' elaboration of its node (AT-2's names). -/
inductive CrossContent
  | content (c : Content)
  | attitude (φ : VE.Formula)
  deriving DecidableEq, Repr

/-- The premises a candidate owns: an assertion's formula and an attitude candidate's claim. A norm, right or
limitation candidate owns none here: the chain reads it through `sup`, as today. -/
def CrossContent.premises : CrossContent → List VE.Formula
  | .content (.assertion φ) => [φ]
  | .content _ => []
  | .attitude φ => [φ]

/-- A set's candidate-owned premises, each gated by its candidate's choice atom (`gate`, `Compose/Slot.lean:70`). -/
def crossSlot (cs : List (VE.Formula × CrossContent)) : List VE.Formula :=
  cs.flatMap fun x => gate x.1 x.2.premises

/-- PC-11 (1). Where exactly one candidate's choice atom holds, the set's gated premises hold exactly when that
candidate's own premises do (from `sat_gate_on` and `sat_gate_off`, `Slot.lean:78`, `:87`). -/
theorem crossSlot_choice (B : VE.Structure.{u}) (cs : List (VE.Formula × CrossContent)) (i : Nat)
    (hi : i < cs.length) (hon : (cs[i]'hi).1.denote B [])
    (hoff : ∀ (k : Nat) (hk : k < cs.length), k ≠ i → ¬ (cs[k]'hk).1.denote B []) :
    VE.Norms.Sat B (crossSlot cs) ↔ VE.Norms.Sat B (cs[i]'hi).2.premises

/-- PC-11 (2). A set with no attitude candidate owns today's gated premises: an assertion's formula, nothing else. -/
theorem crossSlot_legacy (cs : List (VE.Formula × Content)) :
    crossSlot (cs.map fun x => (x.1, CrossContent.content x.2)) =
      cs.flatMap fun x => gate x.1 (match x.2 with | .assertion φ => [φ] | _ => [])
```

`crossSlot_choice` is the gated mixed-candidate obligation: under a choice, an unchosen attitude candidate
constrains nothing, and the chosen one's claim is a premise. `crossSlot_legacy` says the type changes no set
without an attitude candidate. The fixtures are F11.1 to F11.4.

### 3.11 PC-12: the scenario slot in a candidate's guard (pc-fid-rev2, R3; staged on modality's MD-4a)

"Might X, in which case <rule>" limits which situations the rule binds, so it changes verdicts. Modality's MD-4
designs the scenario: a supposition opens a named scenario σ (its name, its situation sort, its condition C, a formula
about one situation of that sort), admitted per compatible choice (MD-4a's `admitAll`; `ScenarioClosed` and
`ScenarioUndecided` are modality's texts), and a governed rule gains C through scope's `reguard ["and", "own", C]`
(modality-counterfactual-PLAN 768-770). `CrossContent`'s `assertion` case (3.10) is a candidate that is a modal claim;
it is not a condition inside a candidate's rule, and `modality@0`'s `.layer` interface gives report fields only.
This plan designs the slot only; the construct is modality's.

```lean
-- lean/VE/Service/DocumentChain.lean (PC-12; staged on MD-4a)
/-- The scenario slot of a candidate's rule: the scenario's condition `C`, over the rule's quantified variable, as the
last conjunct of the rule's guard. It is the rule scope's `reguard ["and", "own", C]` gives (`Scope/Govern.lean:63`),
MD-4a's composition of a `suppose` governor with a governed rule, so the condition written inside the sentence and
the same condition governing from a unit of its own give one rule. -/
def scenarioGuard (u : String) (C norm : Json) : Except String Json :=
  VE.Scope.applyEffect u (.reguard (.arr #[.str "and", .str "own", C])) norm
```

The slot, which a writer follows under the full ruled grid:
- **Position.** One conjunct of the guard of every candidate whose rule the condition limits, after the rule's own
  conditions: the guard `own ∧ C` (`scenarioGuard`, F12.1). In VE: "…, if both that situation has crossed the fourth
  threshold and ⟨STUB[modality-counterfactual]: "<the condition's words>" (scenario σ1, at that situation)⟩." A
  candidate the condition does not limit (an asserted ⊤, as ursp.t4_evidentiary's F) holds no conjunct. When the
  supposition is a unit of its own ("Suppose that …", then "In that case, …"), it is modality's governor in the scope
  block (effect `suppose`, its reach), which is scope's slot (the plan's 15.2 rule 9), and its `reguard` gives the
  same guard.
- **What the stub receives.** `STUB[modality-counterfactual]` fills C and names σ (its name and sort); the slot passes
  the rule's quantified variable ("that situation") as σ's situation variable, so C's one free variable is that
  variable, of σ's sort. "Might" itself, σ's possibility, is not a conjunct: it is σ's admission, modality's.
- **The refusal.** A C with no free variable (a closed condition), or with a free variable other than the rule's, is
  refused `ScenarioUnbound` (modality's `Scenario.check`, its code and text; the DRI's fp-apol F5 precedent: a
  scenario-governed rule takes the scenario's situation variable or is refused). Row 22.
- **Until MD-4a lands**, every candidate that holds the slot is pending (`content: null`), its rows `unknown`, never
  dropped.
- **The list.** `modality@0` is `.layer`: the layer rule (row 17) refuses it beside a list its own `LayerFacts` does not
  cover (F12.1: `UnsupportedProfile: modality@0 with readings@1 is not implemented` on the soft chain with readings,
  whose route head is `readings@1`). Modality's row batch adds the chain lists to `layerCovers` with that theorem; the
  slot is reached only after it. The conjunct is a formula of the rule's guard: the chain reads it as it reads any
  conjunct, and PC-1's reader finds a bound judgment inside it (`govern_narrow_judged`'s guard, 3.5).

PC-12, after MD-4a (modality's scenarios and its `Scope/Effects.lean` case), modality's row batch (its row and its
`layerCovers` entries), PC-2b and PC-4, defines `scenarioGuard` and adds F12.1 to F12.3. It adds no route and no refusal of
its own: `ScenarioUnbound` and the admission's texts are modality's.

## 4. Diagnostics

Every text is computed in Lean. "Kept" means byte-identical.

| # | Text | Raised by | Batch | Fate |
|---|---|---|---|---|
| 1 | `CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route` | `documentRefusal` (today `environmentOf`) | PC-1 | deleted |
| 2 | `CheckerUnavailable: judgments@0 with rights@0 needs its composed Lean route` | as 1 | PC-1 | deleted |
| 3 | `CheckerUnavailable: judgments@0 with alternatives@0 needs its composed Lean route`, and the same with `risk@0` | as 1 | — | kept (F1.5) |
| 4 | `CheckerUnavailable: soft-norms with norm-defaults, readings, alternatives or risk needs its composed Lean route` | `documentRefusal` | PC-2a | becomes `CheckerUnavailable: soft-norms with readings, alternatives or risk needs its composed Lean route`; PC-2b makes it `CheckerUnavailable: soft-norms with alternatives or risk needs its composed Lean route` |
| 5 | `CheckerUnavailable: rights with norm-defaults, alternatives or risk needs its composed Lean route` | `documentRefusal` | PC-2c | becomes `CheckerUnavailable: rights with alternatives or risk needs its composed Lean route` |
| 6 | `CheckerUnavailable: judgments@0 with scope@0 needs its composed Lean route` | `caseRefusal` (today `check`, :1744) | PC-5 | deleted |
| 7 | `UnsupportedProfile: <a> with <b> is not implemented`, `<a>`, `<b>` the first pair of an unlisted stack (positions `i < j`, by `i` then `j`) whose two-profile stack is unlisted | `stackRefusal`, in `checkDocSets` and `checkDoc` after the gate, and at `check`'s site | PC-4 | new; E1. (pc-fid-rev) Its pilot instances: `acts@0 with readings@1` until PC-6c (F6.14), `ve.discourse@1 with readings@1` until PC-7c (F7.6), `ve.discourse@1 with acts@0` on the pilot document until PC-7b (F4.12) |
| 7b | `UnsupportedProfile: stack <p1>, …, <pk> is not implemented`, for an unlisted stack every pair of which is listed | `stackRefusal`, as 7 | PC-4 | new; E1s. (pc-fid-rev) Kept: from PC-4b on, the batch that lists a stack's last pair lists the stack (1.5's listing rule), so a document of the ruled grid reaches it only between a pair's listing and that batch's merge (F4.7, F4.13) |
| 8 | `UnsupportedProfile: acts@0 with soft-norms@0 is not implemented`, and the same with `rights@0` | `gateOf` (`actsRefuses`) | PC-6 | deleted |
| 9 | `UnsupportedProfile: acts@0 with holistic outranking is not implemented` | the soft decoder, when `splitSoft` would split a rule of a document whose outranking is holistic | PC-6 | new; E1 |
| 10 | `UnsupportedProfile: acts@0 with ve.discourse@1 is not implemented`; `UnsupportedProfile: scope@0 with ve.discourse@1` | `gateOf` | PC-7b | deleted |
| 11 | `UnsupportedProfile: defaults with provider conditions is not implemented` | `defaultsRows` (`providerConditions`) | PC-9 | new; E1d |
| 12 | `JudgmentListedUnused: <unit> <term>` and the seven other `judgmentCodes` | `Judgments.status`, `Judgments.admit` | — | kept; G3's named layer refusals |
| 13 | `invalid open-term arguments` | W2's open-term check, without the layer | — | kept; G3's named relaxation |
| 14 | `UnsupportedProfile: judgments@0 requires documents@1` | `gateOf` at `decodedEnvironment` (`Document.lean:611`) | — | kept; a layer refusal (`judgmentGateTexts`, 1.7 2d) |
| 15 | `invalid unit status`; `unit status contradicts content, meaning, or active reading set`; `unit meaning id does not match content`; `reading meaning id does not match content`; `distinguishing models must be supplied by id`; `distinguishing model id does not match model` | the original request's validation (`Document.lean:1310-1818`, `Discourse/Loader.lean:466-555`) | — | kept; never layer refusals (1.7 2d) |
| 16 | `distinguishing model ids and references do not map one to one between the environments with and without judgments@0` | `clashRefusal` (`swapClash`), the first line of `checkDocSets` and `checkDoc`, on every request, plain ones included, when the request's exchange or, with `judgments@0`, its twin's is not one-to-one (symmetric, pc-d2 round 2; 1.7) | PC-1 | new; validation, never a layer refusal (`layerRefusal swapClash = false`); shown as it is, never through E1 (it is no `UnsupportedProfile` text) |
| 17 | `UnsupportedProfile: <layer> with <p> is not implemented`, `<layer>` an owned `.layer` profile other than `documents@1` and `judgments@0` whose `LayerFacts` entry does not cover the list, `<p>` the list's route head (F4.9: `UnsupportedProfile: modality@0 with risk@0 is not implemented`) | `documentRefusal` (`layerRule`), after rows 1 to 5 | PC-4 | new; E1. Each layer's row batch lifts it for the lists its theorem covers |
| 18 | `InvalidInput: generated name <n> of pack <i> is already declared` | `assemble` (`Packs.lean:101`), for a pack name declared in `fullEnv U` | — | kept (PK-1's); the refusal G1b's `hfresh` matches (F3.2b) |
| 19 | `ScopeReadings: <unit>` (a reading set on a governor's own unit, or one a governor reaches that is not governed per choice); `UnsupportedProfile: scope@0 frontier reach requires SC-5` | scope's `admitBlock` (`Scope/Govern.lean:249`) and frontier reach (`:92`), inside `decodeScope`'s GOVERN | — | kept, scope's texts (pc-fid-rev, B3): SC-5 lifts them for the sets it governs per choice; PC-5b then re-proves `listed_evidence` on them (F5.6 to F5.8). Never a composition refusal: the stack `["scope@0", "readings@1"]` is listed |
| 20 | `CouplingLabelMissing: <coupling id>, <set id>`: the first set, in the coupling's order, with a candidate that has no label on the coupling's axis; or, when every set is labelled but they share no value, the coupling's first set | main's `decodeCouplings` (`Readings/SupWire.lean:66`, `:72`), inside S2a's admission (`admitS2Rest`) | — | kept, main's text (pc-fid-rev2, R1): `admitS2Rest_couplings` (proved) and `compatibleChoices_admitS2` (PC-2b); refused before any route; never a composition refusal, and no batch relaxes it (F2.10) |
| 21 | `InvalidInput: act phrase for <name> has more than one reading: 1. … 2. …` (act phrases' D-15: each meaning rendered by `Act.text` with no modal word) | act phrases' `checkAct` (AP-3), at the declaration | — | kept, act phrases' text (pc-fid-rev2, R2): an act written as one derivation where the grammar gives several, with no narrowing; never a composition refusal (F6.17) |
| 22 | `ScenarioUnbound` (modality's code; its text is modality's specification 2.3's) | modality's `Scenario.check` (MD-4a, MD-4b) | — | kept, modality's (pc-fid-rev2, R3): a scenario slot whose condition is closed, or has a free variable other than the rule's quantified variable; the slot is PC-12's (staged), the refusal modality's (F12.3) |

Fault order. Row 16 comes first on every request, before the gate (1.7). Rows 1 to 5 keep today's order inside
`documentRefusal`, which `environmentOf` calls where checks 1 to 4 are today, and row 17 comes after them. On a list
with `scope@0` the order is row 16, the gate, row 7 (or 7b), `decodeScope` (rows 1 to 5, then 17), then row 6 in
`check` (3.4). On a list without `scope@0`, row 16 is checked first and row 7 (or 7b) at `check`'s site, before
`environmentOf`. Row 19 is scope's, inside `decodeScope`, so after row 7. Row 20 is main's S2a admission's, in the
readings branch once the environment is decoded (after rows 1 to 5 and 17), before any choice is enumerated. Row 21 is
act phrases', at the vocabulary's declarations; row 22 is modality's, at its scenario check; neither is a document-mode
composition check. The record rule (3.4) adds no row: a record is read by no decoder. Row 9 is checked after the soft decoder's own checks and before `splitSoft`. Row 11 is checked
before any defaults premise is generated. Row 18 is `assemble`'s, before any certificate is checked.

Python changes no decision. Its retained refusals at `ve/document/load.py:180-182` already send these documents to
Lean. The branches PC-2a and PC-2c delete (`load.py:184-197`, `:186-190`) are deleted after the parity test, not
copied.

## 5. Acceptance fixtures

(C) marks a fixture the DRI made a condition (ruling 1; pc-d2's decision, item 1: F1.3m, F3.2b, F3.2c, F4.9,
F6.11, F9.7; and pc-d2 round 2's decision, item 1: F1.3m, F1.3n, F1.3o); each stays selected in the batch that builds
it. "Stub"
means the expected value is a `#guard` or `decide` in the scratch stub file (section 9), to be kept as a `#guard`
in the batch's `Examples.lean`. Every "exactly when" or "iff" claim has a fixture for each direction; the Dir.
column names the direction.

### 5.1 PC-1

| # | Document | Expected | Dir. |
|---|---|---|---|
| F1.1 | constitution u0052.s01, "Claude should always use good judgment when evaluating conversational inputs.", as a soft default rule, `good_judgment` bound | admitted; OPEN; usage `good_judgment: [u0052.s01]`; G3 success: `verdictFields` equal to the twin's, and each unit's status the twin's or OPEN | G3 success, first disjunct |
| F1.2 | constitution u0036.s05, "Claude should ask for clarification in cases of genuine ambiguity.", as a force set (strict, default), `genuinely_ambiguous` bound in the guard of both candidates | admitted; OPEN; both candidates scanned | |
| F1.2b | F1.2 with the bound term only in the default candidate's `unless` clause | still found: carve-outs are read (`softContent_formulas`) | reader includes author carve-outs |
| F1.3 (C) | F1.2 listing an unused judgment `reasonable` | `JudgmentListedUnused: u0036.s05 reasonable` (today's text and order); the twin without the layer is admitted; `layerRefusal` holds (stub) | G3 refusal, second disjunct |
| F1.3b | F1.1 with an authored unit `meaning_id` that is wrong under both environments (neither `v₁` nor `v₂`) | `unit meaning id does not match content` with the layer, and in the twin: the exchange keeps the value, so the refusal is unchanged | G3 refusal, first disjunct (2a) |
| F1.3c | F1.1 with a judgment declared with `arguments: ["person", "person"]` | admitted with the layer; the twin refused with `invalid open-term arguments` | G3 success, second disjunct |
| F1.3d | F1.1 without `documents@1` | with the layer: `UnsupportedProfile: judgments@0 requires documents@1` (`Document.lean:611`); the twin is admitted; `layerRefusal` accepts the text (`judgmentGateTexts`, stub) | G3 refusal, second disjunct (2d) |
| F1.3e | F1.1 with a correct authored unit `meaning_id` (`v₁`) | both admitted; the twin states `v₂`; `verdictFields` equal after 2e | G3 success, first disjunct (2a) |
| F1.3f | F1.1 with a unit `meaning_id` copied from the twin's answer (`v₂`) | refused on both sides with `unit meaning id does not match content`: the twin states `v₁` | G3 refusal, first disjunct (2a) |
| F1.3g | F1.1 with a reading set on its unit, a reading with content and its required reading `meaning_id` (`Discourse/Loader.lean:449`, `:466`) | both admitted after the exchange; without it, the twin would refuse with `reading meaning id does not match content` | G3 success, first disjunct (2a) |
| F1.3h | F1.3g with two readings, their distinguishing models under correct model keys, and `admission.distinguishing_models` references to them | both admitted after the exchange (`Loader.lean:540-555`); `verdictFields` equal after 2e | G3 success, first disjunct (2a) |
| F1.3i | F1.1 with an authored `status: "OPEN"` | the original succeeds; its status-omitted form succeeds with equal `verdictFields` and equal computed statuses; that form and its twin succeed under G3 (the twin's unit is CHECKED, the layer's OPEN) | 2c; G3 success, first disjunct |
| F1.3j | F1.1 with an authored `status: "CHECKED"` | original-request validation: `unit status contradicts content, meaning, or active reading set` (`Document.lean:1818`); `layerRefusal` rejects the text (stub); outside G3's domain (2b) | validation, not counted under `layerRefusal` |
| F1.3k | F1.1 with an authored `status: 5` | original-request validation: `invalid unit status` (`Document.lean:1314`); `layerRefusal` rejects the text (stub) | validation |
| F1.3l | F1.3h with one more reading whose reference names no model and reads the twin's key of a stated model `d` (`v₂(d)`); `d` separates every pair of readings that references it | the exchange would send that reference and `d`'s key to one value, so `swapInjective` is false (on these values, `swapInjectiveOf` is false: stub). With the layer and in the twin, the answer is `.error "distinguishing model ids and references do not map one to one between the environments with and without judgments@0"` (row 16), first, before the gate (`checkDocSets_swapClash`); `layerRefusal` rejects the text (stub) | the G3 amendment's regression; validation, not counted under `layerRefusal` |
| F1.3m (C) | F1.3l without `documents@1` | with the layer: `.error "distinguishing model ids and references do not map one to one between the environments with and without judgments@0"`, not the gate's `UnsupportedProfile: judgments@0 requires documents@1`, which the check precedes; in the twin (a plain request): the same text. Same text, same fault order (first) on both sides; `layerRefusal` rejects it (stub) | the check runs before the gate on both sides |
| F1.3n (C) | every request of `tests/data` without `judgments@0` | byte-identical answers before and after PC-1: the clash check refuses none of them | the change to plain requests refuses only non-one-to-one requests |
| F1.3o (C) | section 9's open point 1, on F1.3h's reading set with its two distinguishing models given one content `c` (`a1` and `a2` its identities with and without `judgments@0`, `w` a third string): `j₁`, with `judgments@0` and `documents@1`, states model A under `a1` and model B under `w`; `j₂` is `j₁` with A under `a2`; `t`, the plain request stating A under `a2` and B under `w`, is the twin of both (`j₁`'s exchange sends `a1` to `a2` and keeps `w`; `j₂`'s is not one-to-one, so its twin keeps its values) | `j₁`, `j₂` and `t` each answer `.error "distinguishing model ids and references do not map one to one between the environments with and without judgments@0"` (row 16), first, before every other check: `j₁` because its twin's exchange is not one-to-one (its own is), `j₂` because its own is not, `t` because its own is not (stub: `clashRefusalOf` on each side's values, and on F1.3h's values `none`). G3's refusal clause holds on `j₁` by its first disjunct, and `checkDocSets_swapClash` holds on `j₁` and on `j₂`; `layerRefusal` rejects the text (stub) | the symmetric check: a request with the layer is refused exactly when its twin is |
| F1.4 | UDHR u111 (Art. 29(2)) as a rights limitation, `just_requirements`, `morality`, `public_order`, `general_welfare` bound | admitted; OPEN; `Lim_D` premises byte-identical with and without the layer | `correlate_judged` |
| F1.5 | F1.1 plus `alternatives@0` | `CheckerUnavailable: judgments@0 with alternatives@0 needs its composed Lean route` (kept) | |
| F1.6 | F1.1 and its profile-free twin | the same `verdictFields`; different identities | |
| F1.7 (harness, not repo) | DeepMind probe JT-a (s134-rra in D1's environment) | admitted, OPEN, usage `reached: [s134-rra]` (today refused) | |
| F1.8 | two default soft rules on one act, M of higher rank with `harmful` bound in its guard, N with no judgment | N is OPEN only if its own text uses a judgment: N is not under `harmful` in the usage map; `dependsOnC [.rule (primeNode D N)]` does contain `harmful` (why the reader is the author rule) | reader excludes generated reads |

PC-1b (pc-fid-rev, B5; staged: after PC-1, AT-3a and AT-2). Built from the shape of the pilot unit
**ufsf.s132_subsequent** (a strict rule whose guard holds a belief whose content is a judgment):

| # | Document | Expected | Dir. |
|---|---|---|---|
| F1.9 | `opensIn ["could_weaken", "new_capabilities"]` on the guard `new_capabilities(r) ∧ attitudes__believes__1(r)`, with the key `attitudes__believes__1 ↦ could_weaken(r)`, through `withAttitudeContents`; and on the guard alone | `["could_weaken", "new_capabilities"]`; `["new_capabilities"]` (stub) | the reader reads an attitude's content |
| F1.10 | `withAttitudeContents` with a key the formulas do not use (`attitudes__believes__2 ↦ could_weaken(r)`) on `[new_capabilities(r)]` | `[new_capabilities(r)]` (stub) | an unused key adds nothing |
| F1.11 | profiles `["attitudes@0", "documents@1", "judgments@0", "norms@0", "relational-fol@0"]`, an `environment.attitudes` block with holder sort `company` and `decided_by` `the_lab`; unit u1, kind norm, meaning `{"open": ["could_weaken", "new_capabilities"]}`: "Every release must be preceded by a safety review, if both that release has new capabilities and the lab believes that the capability gain of that release could weaken its safety case."; the second conjunct is AT-3a's node `{"attitude": {"holder": "the_lab", "mode": "believes", "slot": {"sort": "release", "term": <that release>}, "content": could_weaken(<slot>)}}`; `new_capabilities` and `could_weaken` bound, decider `unresolved_decider` | admitted; u1 OPEN; usage `could_weaken: [u1]`, `new_capabilities: [u1]` (J's order); verdict fields equal to the twin's without `judgments@0` (G3); the generated atom keeps attitudes' open-term line. With PC-1's reader alone (PC-1b's seeded bug): `JudgmentListedUnused: u1 could_weaken` | the layer reads the composed node |

### 5.2 PC-2a, PC-2b, PC-2c

| # | Document | Expected | Dir. |
|---|---|---|---|
| F2.1 | constitution u0073.s05, "Claude should generally comply with the system prompt's instructions if doing so is not unsafe, unethical, or against Anthropic's guidelines", soft default rule, three exceptions on `unspecified` | admitted; `layeredOf_ids` gives `["soft"]`; the case and no exception SETTLED yes; an exception UNDECIDED | admitted |
| F2.1b | F2.1 with a `completions` entry naming an absent unit | refused with `validateCompletions`' text, from both entry points | refused |
| F2.2 | constitution u0125.s04.p2, "Claude should never directly deny that it is Claude", strict | the same answer from `ve document check` and from `ve document readings --conclusion` | |
| F2.3 | parity: every document of `tests/data` the retained loader accepts under soft-norms plus norm-defaults | byte-identical answers before and after | |
| F2.4 (harness) | DeepMind probe DF-c | admitted | |
| F2.5 | constitution u0156.s03, "Claude shouldn't actively deceive the user about the existence of a system prompt or its content.", force set with a default candidate carrying content | both readings check; the status line keeps "conditional on <k> coherence premises" | |
| F2.6 | the constitution's three "should" sets together | 8 rows, one per compatible choice, every one CONFLICT-FREE, as the Oct 12 pilot recorded (`readings/nd-all-result.json`) | rows = choices |
| F2.6b | F2.6 with one reading of one set pending (`content: null`) | the row count is still the number of compatible choices; each choice with the pending reading is a row with `unknown`; the verdict is `unknown` by `foldEntailment` | pending kept |
| F2.6c | F2.6 with a coupling that excludes one choice | that choice is not a row; every other is | incompatible not a row |
| F2.6d | a hand-built `ChainRows` for F2.6 whose rows are the 8 compatible choices, one of them `proved` where its choice's document has a checked countermodel | satisfies `chainReadings_rows`' shape conditions; fails `RowsHoldG` at that row (`HoldsG … .proved` is false), so `chainReadings_rowsHold` is what licenses `foldG_*_sound` | rows hold, not only cover |
| F2.7 (harness) | DeepMind probe SC-a (scope, soft, norm-defaults, readings, without RS8's set) | admitted; both units OPEN, 585 B | |
| F2.8 | UDHR u022a (Article 3, `has_the_right_to_life`) as a `rights@0` claim with completion `unspecified` | `layeredOf_rights` gives `["soft", "rights"]`; a situation outside the right is UNDECIDED | |
| F2.9 | UDHR u111 as a limitation reading set (both aims, or listed aims) on the enumerated route | rows = the two choices | |

pc-fid-rev2 (R1, PC-2b; R4(a), PC-1 and PC-2b). Built from the shapes of the re-pilot units **ursp.t2_argument**
(with ursp.t4_argument's and ursp.t4_evidentiary's sets) and **ursp.t4_plan_moonshot**, in this fixture's own words:

| # | Document | Expected | Dir. |
|---|---|---|---|
| F2.10 (R1; ursp.t2_argument's shape) | profiles `["documents@1", "judgments@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]`; u1 "A lab should file a safety case at the second threshold.", u2 the same at the fourth, u3 "At the fourth threshold, reviews of AI threats should meet strict standards."; `crossed` bound. Sets `rs-file-u1`, `rs-file-u2`: `F`, asserted, content `["top"]` (a recommendation to the field); `Ds_strict`, "Every situation must file a safety case, if that situation has crossed the second threshold." (u2: the fourth); `Ds_default`, the same with "should" and the exception decided by `unstated`. Set `rs-std-u3`: `F`; `Ds_strict` and `Ds_default`, its own force (axis `std`). (a) labels `rs2` = the candidate's id and `addressee` (`F` or `Ds`); couplings `c-rs2` on `rs2` over u1's and u2's sets, `c-addressee` on `addressee` over all three. (b) labels `addressee` and `force` (`F` for F, `strict`, `default`); couplings `c-addressee` over all three, `c-force` over u1's and u2's. (c) (b) with F carrying no `force` label, as the pilot wrote it | (a) and (b): main decodes the couplings, `["c-rs2", "c-addressee"]` and `["c-addressee", "c-force"]` (stub); the same 5 compatible choices of 27 (stub): F in all three sets, or one Ds reading in u1 and u2 with either of u3's; after PC-1 and PC-2b, admitted, five rows, the units OPEN through `crossed`. (c): `CouplingLabelMissing: c-force, rs-file-u1` (main's text, row 20; stub), before any route; no row | the rule's two forms are admitted; the unlabelled form is main's refusal |
| F2.11 (R4(a); ursp.t4_plan_moonshot's shape) | profiles as F2.10; u1 "The lab will run red-team exercises, to find weaknesses in its safeguards."; its set `rs-purpose`: `limiting`, "Every lab must run red-team exercises, if both that lab has crossed the fourth threshold and that lab is classified as "serves_finding_weaknesses"."; `rationale`, "Every lab must run red-team exercises, if that lab has crossed the fourth threshold.", with purpose-explanation's link for the clause; `crossed` and `serves_finding_weaknesses` bound, the latter's record "Whether running red-team exercises at a lab serves finding weaknesses in its safeguards is a judgment; the text does not say who makes it." | the reader finds both judgments in `limiting`'s guard and only `crossed` in `rationale`'s (`opensIn`: `["crossed", "serves_finding_weaknesses"]`, `["crossed"]`; stub). After PC-1 and PC-2b: admitted; u1 OPEN; usage `crossed: [u1]`, `serves_finding_weaknesses: [u1]`; two rows. A lab past the fourth threshold that runs no exercise and for which the judgment does not hold: no rule violated under `limiting`, rule 1 violated under `rationale`, so the readings differ and neither is dropped. A narrowing keeping `limiting` that cites a source unit: one row | both purpose readings kept, the limiting one read by the reader |

### 5.3 PC-3, and G1b (PK-1's owner)

F3.2 to F3.2d are built in PK-1's G1b module (`PacksVocab.lean`'s examples), and F3.2b and F3.2c stay selected
there (the DRI's condition).

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F3.1 | `checkDocSets_pipeline` on a two-unit scope document (`ContractExamples.lean`) | the document mode's answer equals `pipeline [scopeRewriter]`, then `checkCore`, then `foldGovernors` | |
| F3.1b | a document with no governor | `scopeRewriter.run` is the identity on the case's units (`govern_identity`) | |
| F3.2 | `acceptanceXV` on a hand-built pack declaring one `attitudes__k__1` predicate (the `#guard` at `PacksLegacyExamples.lean:56`, extended to a certificate) | accepted | |
| F3.2b (C) | the name collision: over fixture μ (`legacyU muX`), the pack `⟨"soft", .vocabulary, [("soft__excepted__may_publish", ["person", "person"])], [], [("soft:collide", ¬soft__excepted__may_publish(a, b))], []⟩`, which redeclares a predicate the filled tree declares and supplies its negation | `declaredIn (fullEnv (legacyU muX)) "soft__excepted__may_publish"` is true (stub), so `acceptanceXV`'s `hfresh` fails and G1b says nothing about it; `assemble (legacyU muX) 0 [collide]` refuses it with `InvalidInput: generated name soft__excepted__may_publish of pack soft is already declared` (row 18; stub). Under draft 3's statement, which had no `hfresh`, a certificate of `¬soft__excepted__may_publish(a, b)` from it would be accepted while every expansion of a base where the decision holds makes it true | freshness is a hypothesis |
| F3.2c (C) | a satisfiable positive fresh predicate: over fixture μ, the pack `⟨"soft", .vocabulary, [("soft__fresh", ["person"])], [], [("soft:fresh", soft__fresh(c))], []⟩`, `c` a constant of sort `person` | it assembles (`ok [soft] [soft:fresh]`, and `soft__fresh` is not declared in `fullEnv`: stub); `EntailsXV (legacyU muX) [q] [] .bottom` is false: a base over `envX` with `soft__fresh = {c}` satisfies `BaseAdmissibleXV` and expands (`DocumentExpansionXV`), so F3.2's statement has a model. Under draft 3's `EntailsXV` the same entailment of `.bottom` held vacuously, because admissibility over the old vocabulary made `soft__fresh` empty | fresh predicates are not vacuous |
| F3.2d | the vocabulary countermodel: F3.2c's pack without its premise, `Γ = []`, `φ = soft__fresh(c)` | a conflict-free base over `envX` with `soft__fresh` empty refutes `φ`, so `¬ EntailsXV (legacyU muX) [q] [] φ` (`countermodelXV`); the checker accepts no certificate for it | countermodels over the extended vocabulary |
| F3.3 | `entailsXV_constraint` on `[softPack U D]` | a certificate gives both sides; a checked countermodel refutes both | ↔ both ways |
| F3.4 | `interface_slot`, `interface_functional`, `rewriter_ranks_distinct` | `decide` (stub) | |
| F3.4b | C1 on the planned rows of 1.1's table (`plannedSlots`), and on qt-a3c's `cardinality@0` row with slot `"layer"` | `slotAgrees` true on each (stub) | cardinality's slot is `"layer"` |
| F3.4c | the interface values of the planned rows | `.layer` for `cardinality@0`, `presupposition@0`, `modality@0`, `hedges@0`, `purposes@0`, `examples@0`; `.outside` for `commitments@0`; `.pack "weighing"` for `weighing@0` (stub) | |
| F3.5 | `rewriters profileTable` | `[(11, "acts@0"), (10, "ve.discourse@1"), (20, "right-clauses@0"), (30, "readings@1"), (12, "scope@0")]` (stub) | |
| F3.6 | `stackOf profileTable` on `["norms@0", "readings@1", "relational-fol@0", "scope@0"]`, `["acts@0", "norms@0", "relational-fol@0", "scope@0"]`, `["norms@0", "relational-fol@0", "scope@0"]`, `["norms@0", "relational-fol@0"]` | `["scope@0", "readings@1"]`, `["acts@0", "scope@0"]`, `["scope@0"]`, `[]` (stub) | |
| F3.7 | `ScopeRunsOf` of an entry that refuses every case | holds (`refuseAll_runs`, stub). A run statement alone is not evidence: `RouteFacts` adds `ScopeFaithful` and `ScopePreserves`, which are statements about GOVERN's own functions | run statement is not faithfulness |

### 5.4 PC-4

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F4.1 | `gateOf profileTable ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"]` | `.error "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"` before PC-6 (stub); `.ok` after | |
| F4.2 | E1's rendering of F4.1 and of F4.4 | passes the all-derivations gate | |
| F4.3 | `documentRefusal` on `["documents@1", "judgments@0", "norms@0", "relational-fol@0", "soft-norms@0"]`, `["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]`, `["norms@0", "relational-fol@0", "soft-norms@0"]` (senses off) | `.refused "CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route"`, `.refused "CheckerUnavailable: soft-norms with norm-defaults, readings, alternatives or risk needs its composed Lean route"`, `none` (stub); and every document-mode refusal of `tests/data` keeps its text | |
| F4.4 (C) | `["acts@0", "norms@0", "relational-fol@0", "scope@0"]`: three profiles beside the mandatory `relational-fol@0`, two rewriters, unlisted | the gate admits it (route `norms`, stub); `stackRefusal` answers `UnsupportedProfile: acts@0 with scope@0 is not implemented` (stub); E1 as in 2.3. End to end (`tests/data`): `checkDocSets` on a case whose document lists these profiles and one governor answers that `UnsupportedProfile` text, not today's `CheckerUnavailable: document checks under acts@0 need its Lean profile route` | refused when unlisted, through the document mode's entry |
| F4.5 | `["norms@0", "readings@1", "relational-fol@0", "scope@0"]` (listed) and `["norms@0", "relational-fol@0", "scope@0"]` (one rewriter) | `stackRefusal` gives `none` for both (stub) | not refused when listed or single |
| F4.7 | `stackRefusalIn L ["acts@0", "norms@0", "relational-fol@0", "scope@0", "ve.discourse@1"]`, `L` = main's `listedStacks` with `["acts@0", "scope@0"]`, `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]` (every pair of the triple listed) | `some "UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0 is not implemented"` (stub); E1s as in 2.3 | whole stack when every pair is listed |
| F4.8 | `stackRefusalIn L ["norms@0", "readings@1", "relational-fol@0", "scope@0", "ve.discourse@1"]`, `L` = main's `listedStacks` with `["ve.discourse@1", "scope@0"]` and `["ve.discourse@1", "acts@0"]` (stack `["ve.discourse@1", "scope@0", "readings@1"]`; only its pair `(ve.discourse@1, readings@1)` unlisted, and it is not the first pair) | `some "UnsupportedProfile: ve.discourse@1 with readings@1 is not implemented"` (stub) | the first unlisted pair, not the first two profiles |
| F4.6 | the plan's grid (3.2) | regenerated from `cellOf`; the plan's prose is not a second source | |
| F4.9 (C) | `risk@0` beside `modality@0` before modality's agreement theorem (DEC 15): `["alternatives@0", "modality@0", "norms@0", "relational-fol@0", "risk@0"]` over `profileTable` with `modality@0`'s row as MD-2 registers it (`⟨"modality@0", [], [], "layer"⟩`, `profileTableMD`) | the gate admits it (route `risk`, stub); `layerRuleIn profileTableMD [] …` answers `some "UnsupportedProfile: modality@0 with risk@0 is not implemented"` (stub), rendered by E1 with both feature names as in 2.3; with a `layerCovers` entry for modality that covers the list, `none` (stub). End to end, once MD-2 makes `modality@0` owned, `checkDocSets` answers that text until modality's row batch adds the entry with its theorem | refused until covered; lifted only where covered |
| F4.10 | the layer rule on main's table | `otherLayer profileTable p` is false for every profile of `profileTable`, and `layerRule` on F1.1's list (`["documents@1", "judgments@0", "norms@0", "relational-fol@0", "soft-norms@0"]`) is `none` (stub): the rule refuses nothing that is admitted today | `.layer` grants nothing, and takes nothing today |

pc-fid-rev (B2, the record rule, PC-4; B6, any number of rewriters, PC-4b). Built from the shapes of the pilot units
**ufsf.s52_aim**, **ufsf.s22_recommend** and **ursp.t1_plan** (B2) and of the pilot's one document (B6):

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F4.11 | `recordProfile` on main's table and on `profileTableCM` (main's with `⟨"commitments@0", ["norms@0"], [], "commitments"⟩`, CM-2's row); `gateOf` and `stackOf` on ufsf.s52_aim's list `["commitments@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]` against the same list without `commitments@0`; `documentLayersOf` on main's table and on `profileTableCM` (`documentLayers'`); `withoutDocumentLayers'` on an environment listing `commitments@0` and `judgments@0` | no record on main; `commitments@0` a record with CM-2's row, and no other outside profile one (each sits on a route head); both lists gate to `.readings` and have the stack `["readings@1"]`; the derived list is main's `documentLayers` on main's table and `["judgments@0", "commitments@0"]` with CM-2's row (one owner, derived; no second list); the environment's profiles without the two (stub) | a record changes no route and no stack |
| F4.12 | `stackOf profileTable` on the pilot document's 14-profile list (`pilotDocList`); `stackRefusal` on it; `stackRefusalIn` on it with the full ruled grid's stacks (`fullGridStacks`: main's, PC-6b's, PC-7b's, PC-6c's and PC-7c's pairs, and the listing rule's stacks) | `["ve.discourse@1", "acts@0", "scope@0", "readings@1"]`; `some "UnsupportedProfile: ve.discourse@1 with acts@0 is not implemented"`; `none` (stub) | refused until listed; admitted once listed |
| F4.13 | `stackRefusalIn` on the same list with every pair of its stack listed but not the stack | `some "UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0, readings@1 is not implemented"` (stub; E1s, as F4.7) | pairs alone admit nothing (ruling 10, 1(b)) |
| F4.14 | the listing rule's invariant on `fullGridStacks`: every stack of three or more has every pair listed, and every listed stack is in rank order | true; true (stub). Its seeded mutant (the full grid without `["acts@0", "readings@1"]`) fails this guard, F4.13's and F6.14's second (9) | no stack admitted beyond its pairs |
| F4.15 (end to end; ufsf.s52_aim's shape) | profiles as F4.11's list, legend "In this document, “we” means the lab."; unit u1, kind norm, meaning `{"open": ["reached"]}`, its reading set `rs_aim`: `attempt`, "Rule 1. Every release should notify the regulator, if that release has reached a critical level. The exception to rule 1 is decided by the lab."; `goal`, kind asserted, content `["top"]`, label `no_rule = goal`; `reached` bound, decided by `the_lab`; a `commitments` block annotating both candidates (bearer `the_lab`; `attempt`; `noRule goal`) | with CM-2's row, PC-1 and PC-2b: admitted; u1 OPEN; usage `reached: [u1]`; two rows, one per choice; verdict fields and unit statuses equal to the same request without its `commitments` block (`checkDocSets_ignores_commitments`) and, by G3, to its twin without `judgments@0`. Before CM-2's row: one refusal, the same text with and without the block (the profile has no row) | the block is never read; judgments beside it is G3 |
| F4.16 (CM-2's tests; ursp.t1_plan's and ufsf.s22_recommend's shape) | the commitments mode on unit u1 "We commit to publish a risk report in each situation, if that situation has crossed the second threshold.", annotated `binding`, bearer `the_lab`, with `crossed` bound (decided by `the_lab`) and `judgments@0` listed, and on its G3 twin | the same answer fields (its lines and its annotation checks) on both (`CommitmentsBesideJudgments`); a judged atom is a base predicate to the commitments mode | commitments' mode beside the layer |
| F4.17 (end to end; the pilot document's shape; built by whichever of PC-6c and PC-7c merges second) | one document of five units on disjoint predicates, in the shapes of F1.11, F4.15, F5.8 (a), F6.16 and F7.8, under the pilot document's list | the gate admits it; the stack rule passes (`["ve.discourse@1", "acts@0", "scope@0", "readings@1"]` listed); the answer is `pipeline [discourseRewriter, actsRewriter, scopeRewriter]`, then `checkCore`, then `foldGovernors` (`StackRuns`, by `stackRuns_all`); each unit's answer equals its answer in a document of its own | four rewriters in one stack |

### 5.5 PC-5

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F5.1 (C) | `J = [a, b]`, unit dependence `[b]`, governor dependence `[a]` | `dependsOnC [] ["a", "b"]` of the joined reads is `["a", "b"]`, `J`'s order (stub); draft 1's concatenation would give `["b", "a"]` (stub) | in J's order |
| F5.2 | `J = [a, b, c]`, the same reads | `["a", "b"]`: `c` is in neither part, so it is absent (stub) | absent when in neither |
| F5.3 | constitution u0218.s17, "Not undermining legitimate human oversight and control of AI", as a narrowing lead-in governing u0218.s18 and u0218.s21, `legitimate` bound, both governed units `open` listing it | the governed units OPEN; usage `legitimate: [u0218.s18, u0218.s21]`; u0218.s17 OPEN by scope's fold | |
| F5.4 | F5.3 | the answer carries the chain's `judgments` member (`foldGovernors_judgments`) | |
| F5.5 | F5.3 with u0218.s18's meaning `specified` | `JudgmentNotChecked: u0218.s18 legitimate` | the layer reads the composed rule |

PC-5b (pc-fid-rev, B3; staged: after scope's SC-5 and PC-5). Built from the shapes of the pilot units
**ufsf.s135_bullet3_only**, **ufsf.s135_bullet4_only** and **ursp.s31_off_cycle_public**, under
`["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "scope@0"]`:

| # | Document | Expected | Dir. |
|---|---|---|---|
| F5.6 (ufsf.s135_bullet3_only's shape) | u1: "Every release must have its residual risk accepted, if that release has reached a critical level."; u2, the governor "This applies only where the release is external or high-risk, and is not under further development." (`reguard`, `own and C`, reach `frontier`), with a reading set on u2: `note`, kind asserted, content `["top"]`; `release`, "Every release need not have its residual risk accepted, if both that release is under further development and that release has reached a critical level."; `high_risk` bound | today: `UnsupportedProfile: scope@0 frontier reach requires SC-5`; with u2's reach written `{"rules": ["r1"]}`: `ScopeReadings: u2` (row 19). After SC-5 and PC-5b: governed per joint choice of the reach's live candidates and u2's two readings, as SC-5 defines it; `ScopeSetsFaithful` on it (the choices governed are `setChoices`', and a fault under one choice refuses the document); u1 OPEN through `high_risk` (PC-5, `J`'s order); the choice count is Lean's | a governor's own set is governed per choice |
| F5.7 (ufsf.s135_bullet4_only's shape) | F5.6 with a second rule u3 under another list and, after it, a governor u4 with u2's words and its own reading set | two governors on two units; each frontier's candidates are computed from its own position (layout only, scope 1.7), so no reach is shared; the two governors' sets are two sets of one joint choice; the same refusals as F5.6 today | the same words make two governors |
| F5.8 (ursp.s31_off_cycle_public's shape) | a lead-in u1 "When a model is deployed, the lab must publish a report on that model:" (`frame`, `list` reach) and its item u2 "if that model is far more capable than every model the lab has reported on." (`far_more_capable` bound). (a) A set on u2 whose readings are parts: `wide`, guard `deployed ∧ far_more_capable`; `narrow`, guard `deployed ∧ far_more_capable ∧ internal`. (b) A set on u1 whose second reading publishes the report on the deployment's day (a different act) | (a) today, on main: governed per choice (scope 11, sc-5r; the stack `["scope@0", "readings@1"]` is listed): two choices, each the frame merged with its part; u2 OPEN through `far_more_capable`. (b) today: `ScopeReadings: u1` (a set on the governor's own unit, row 19); after SC-5 and PC-5b, governed per choice, the lead-in's two readings each merged with u2's part | an item's readings are parts; the lead-in's readings are the governor's set |

### 5.6 PC-6a, PC-6, PC-6b

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F6.1b (PC-6a) | `decisionRule` on every rule of today's documents, which set no `splitFrom` | `decisionRule N = N.name` (`decisionRule_unsplit`, proved in the stub); every decision key, name and answer is today's | the staged key changes nothing |
| F6.1 | constitution u0036.s05 (one act, force set) | unchanged by the split: `splitFrom = none`, names today's (`exceptedName_unsplit`) | unsplit keeps today's names |
| F6.2 (C) | constitution u0218.s18 with its four acts "adjust, correct, retrain, or shut down" as a default soft rule, given for this fixture an exception and one alterable party | four part rules; one exception atom and one switch atom, both the source's (`split_shares_decisions`); `decisions` unchanged (`split_decisions`). An assignment where the decider excepts "adjust" but not "shut down" cannot be written: the model check refuses it | split shares one decision |
| F6.3 | constitution u0165.s07, "Generate child sexual abuse material (CSAM)", strict under norm-defaults | byte-identical answers before and after | |
| F6.4 | a UDHR right with a two-act line (u048, movement and residence) under `rights@0` | admitted through soft's declarations (`declarations_acts`) | |
| F6.5 | F6.2 in a document whose outranking is holistic | `UnsupportedProfile: acts@0 with holistic outranking is not implemented`, E1 | refused when holistic |
| F6.6 | the `soft-norms@0` wire-contract step's shadow corpus | passes before any refusal is lifted | |
| F6.7 | F6.2 with a hand-built pack whose `conditions` hold `(.excepted "u0218.s18", C)`, metadata on the source rule; built in whichever of PC-6 (the split) and PC-9 (`dfltUniformOf`) merges second | after the split, each of the four parts' exception premise includes `C` (`packConditions qs (.excepted (decisionRule P))`); keyed by `P.name`, none would. `keyedDecisions` has one `.excepted "u0218.s18"` entry | provider metadata reaches every part |
| F6.8 | `gateOf` on `["acts@0", "norms@0", "relational-fol@0", "right-clauses@0", "rights@0", "soft-norms@0"]` with PC-6's `actsRefuses` | `.ok .clauses` (stub, on `profileTable` with acts' row changed as PC-6 changes it); main refuses it with `UnsupportedProfile: acts@0 with soft-norms@0 is not implemented` | `gate_acts`' `.clauses` disjunct |
| F6.9 | two `ActsDoc`s with the same `U` and the same `splitMap`, whose `acts` give one predicate two different pairs of atoms | `splitReg` gives different part acts, so the two checked elaborations' documents differ while `(D.base, splitMap A)` is the same: `splitSoft` reads the elaboration's document `E.1` | splitSoft needs the elaboration, not the map |
| F6.10 | F6.2's split document | two part rules with one exception name are distinct nodes, so draft 1's `excepted_inj` conclusion `N = M` is false there; `excepted_key` holds (one key, one sort list, one exception) and `decNodup` holds on the deduplicated table | shared decisions keep the invariant |
| F6.11 (C) | the at3a-order amendment's condition (d), beside AT-3a's SR-6 (kept selected): a soft norm whose regulated act goes through the unified decoder and whose guard holds an attitude node, under `attitudes@0`; built on the rebased `Norms/Wire.lean` by whichever of PC-6 and AT-3a merges second | decoded once, through `normFields`: the soft node's guard equals the guard the W1 admission path decodes from the same norm object, and its regulated declaration equals W1's (`declarations_acts`). Without `attitudes@0`, the same norm gets SR-6's answer, `array expected`, in today's fault order | one decoder, one guard-node hook |
| F6.12 (PC-6b) | the constitution set's document: u0218.s17's lead-in governing u0218.s18, whose four acts split as in F6.2, under `["acts@0", "norms@0", "relational-fol@0", "scope@0", "soft-norms@0"]` | `ActsScopeRuns` on it: the answer equals `pipeline [actsRewriter, scopeRewriter]`, then `checkCore`, then `foldGovernors`; the lead-in's `rules` reach names the four parts, and each governor's effect unchanged (`SplitReach`; DRI 2026-10-30, item 1) | the ordered pipeline |
| F6.13 (PC-6b) | `stackRefusalIn (listedStacks ++ [["acts@0", "scope@0"]])` on F4.4's list | `none` (stub): once PC-6b registers the stack, F4.4's refusal is lifted | listed after its proof |
| F6.14 (PC-6c; ursp.t1_plan's and ufsf.s132_subsequent's list) | `stackRefusal` and `stackRefusalIn fullGridStacks` on `["acts@0", "documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0"]` | `some "UnsupportedProfile: acts@0 with readings@1 is not implemented"` until PC-6c lists the pair; `none` under the full ruled grid (stub) | refused until listed |
| F6.15 (PC-6c; ursp.t1_plan's shape) | that list; unit u1, kind norm, meaning `{"open": ["crossed"]}`, its reading set: `cond`, "Every lab must keep or strengthen its safeguards in each situation, if that situation has crossed the second threshold."; `uncond`, "Every lab must keep or strengthen its safeguards in each situation."; the `acts` block declares "keep or strengthen its safeguards" as one act (an "or" join under *must*: one act, its bearer chooses, nothing splits); `crossed` bound | after PC-4, before PC-6c: F6.14's text (row 7). After PC-6c: admitted; two rows, one per choice; under each choice the checked document is the choice's document unchanged (no predicate splits: `ActsChoiceFaithful` with `splitSoft` the identity, `ActsPreserves`); u1 OPEN | one act in a candidate, nothing split |
| F6.16 (PC-6c; ufsf.s132_subsequent's shape) | that list; unit u2, its reading set: `D`, "Every release must be preceded by a modification check and be preceded by a capability check, if both that release is subsequent and that release has new capabilities."; `R`, pending (`content: null`: two rules, which a W2 candidate does not hold); `new_capabilities` bound | after PC-6c: admitted; two rows; under `D` the checked document holds the two part rules `r1-a1` and `r1-a2`, each with `D`'s guard and one shared decision (`split_shares_decisions`), PC-6's split of `D`'s choice document (`ActsChoiceFaithful`); under `R` the row is `unknown`, never dropped; the verdict is `foldEntailment`'s over both rows | a joined act in a candidate splits per choice |
| F6.17 (PC-6c, pc-fid-rev2 R2; ursp.t3_plan's shape) | that list; unit u3 "The lab will describe the test results, the safeguards and the residual risk in the annual report."; the `acts` block declares the frame "describe" (object `""` required and split, modifier marker "in") and the fixed phrases “the test results”, “the safeguards”, “the residual risk”, “the annual report”; the act phrase "{0} describe the test results, the safeguards and the residual risk in the annual report"; its reading set `rs-describe`: `cond-1` and `cond-2`, "Every lab must describe the test results, the safeguards and the residual risk in the annual report, if that lab has crossed the third threshold.", labels `rs1 = cond` and `act = 1`, `act = 2`; `uncond-1` and `uncond-2`, the same rule without its condition, labels `rs1 = uncond`; `ov`, asserted, content `["top"]`, label `rs1 = ov`; `crossed` bound | main's act grammar lists two derivations, in this order: 1, "in the annual report" on the last part; 2, on every part (stub; `read` gives `many`, never one). Under *must* each has one reading of three atoms (stub), paraphrased "{0} must describe the test results; {0} must describe the safeguards; and {0} must describe the residual risk in the annual report." and "{0} must describe the test results in the annual report; {0} must describe the safeguards in the annual report; and {0} must describe the residual risk in the annual report." (stub). After act phrases' readings elaboration and PC-6c: admitted; five rows; under `cond-1` the checked document holds `r1-a1`, `r1-a2`, `r1-a3`, each with `cond`'s guard and one shared decision, the modifier on `r1-a3` only; under `cond-2` on all three; the `uncond` rows likewise with no guard; `ov`'s row its ⊤. If the elaboration cannot fix a candidate to one derivation: the four act candidates pending, their rows `unknown` (act phrases' GAP). With a narrowing that keeps `cond-2`, `uncond-2` and `ov` and cites a source unit: three rows. Written with `cond` and `uncond` alone (one derivation, no narrowing): refused at the declaration with `InvalidInput: act phrase for described has more than one reading: 1. describe the test results, describe the safeguards and describe the residual risk in the annual report. 2. describe the test results in the annual report, describe the safeguards in the annual report and describe the residual risk in the annual report.` (D-15, row 21; stub, from main's `Act.text`) | one candidate per derivation; never one derivation without a reason |

### 5.7 PC-7b

| # | Fixture | Expected |
|---|---|---|
| F7.1 | constitution u0125.s01, "Honesty operates at the level of the overall system.", followed by a constructed unit (not source text) that refers back to "this" honesty norm under a scope lead-in | the reference resolves, the governor applies, and the answers equal those of the same document with the reference written out |
| F7.2 | `gateOf` on `["acts@0", "norms@0", "relational-fol@0", "ve.discourse@1"]` with PC-7b's rows | `.ok .discourse`, which the revised `gate_acts` (3.7) allows; 3.6's revision would be false here. Main refuses it with `UnsupportedProfile: acts@0 with ve.discourse@1 is not implemented` |
| F7.3 | `DiscoursePreserves` on F7.1's first unit, u0125.s01, whose formulas mention no reference | `resolveContent` returns its content unchanged, and `discourseRewriter.run` is the identity on a case whose units mention no reference |
| F7.4 | `DiscourseScopeRuns` on F7.1's document (`ve.discourse@1` and `scope@0`, no `acts@0`) | the answer equals `pipeline [discourseRewriter, scopeRewriter]`, then `checkCore`, then `foldGovernors`; and, by `DiscourseFaithful` at the resolved position, the answer equals the written-out document's (F7.1) |
| F7.5 | `DiscourseActsRuns` on F6.2's u0218.s18 rule followed by a constructed unit (not source text) that refers back to "this" rule, under `["acts@0", "norms@0", "relational-fol@0", "soft-norms@0", "ve.discourse@1"]` | the answer equals `pipeline [discourseRewriter, actsRewriter]`, then `checkCore`; the four part rules are F6.2's; the answers equal those of the same document with the reference written out |
| F7.6 (PC-7c; ursp.t2_plan's list) | `stackOf profileTable` on `["acts@0", "documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "ve.discourse@1"]`; `stackRefusalIn` on it with PC-6b's and PC-7b's pairs listed; with the full ruled grid | `["ve.discourse@1", "acts@0", "readings@1"]`; `some "UnsupportedProfile: ve.discourse@1 with readings@1 is not implemented"`; `none` (stub) |
| F7.7 (PC-7c; ursp.t2_plan's coupled set) | `setShape` on a set `rs-plan-a` on unit u2, version 1, readings `cond` and `uncond` | `("rs-plan-a", "u2", 1, ["cond", "uncond"])` (stub): what `ResolveKeepsSets` keeps |
| F7.8 (PC-7c; ursp.t2_plan's shape) | a `ve-document@2` document, profiles `["documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0", "ve.discourse@1"]`; the manifest registers the entity `t2` for "the second threshold" (unit u1); units u2 and u3 each hold a reading set, `cond` and `uncond`, coupled on one axis (one joint choice); u2's `cond`: "Every situation must have its protections strengthened, if that situation has crossed this threshold."; u3's `cond`: "Every situation must have its threat pathways mapped, if that situation has crossed this threshold."; `crossed` bound | after PC-7a, PC-7b and PC-4b, before PC-7c: F7.6's text (row 7). After PC-7c: admitted; "this threshold" resolves to `t2` in both `cond` candidates; the sets' shapes, the coupling and the narrowings as written (`ResolveKeepsSets`); two rows, one per joint choice; each row's answer equals that of the same document with "the second threshold" written in place of the reference (`DiscourseFaithful`); u2 and u3 OPEN |

### 5.8 PC-9

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F9.1 (C) | rule `a` over rule `b` (W1), rank `b` outranks rank `a` (soft) | each graph passes its own check (`dependencyOrder` on `[⟨a, [b]⟩, ⟨b, []⟩]` and on `[⟨a, []⟩, ⟨b, [a]⟩]`, stub); nothing is refused. Draft 1's single graph over the same strings, `[⟨a, [b]⟩, ⟨b, [a]⟩]`, is a cycle (stub) | mixed pair not refused |
| F9.2 | rule `a` over rule `b` and rule `b` over rule `a` | refused by W1's precedence check (its cycle diagnostic; stub on the same node list) | a cycle in one graph is refused |
| F9.3 | a soft rule with a hand-built `Pack` `⟨"weighing", .constraint, [], [], [(l, φ)], [], [(.outweighs a L H, C)]⟩` stating "privacy outweighs disclosure when the data are medical", run with `--assume-no-exception` | `providerRefusal`, rendered by E1d (2.3). Today's definitions would silently assume "the data are never medical" | refused when a condition is stated |
| F9.6 | F9.3 with the pack's id `scales` instead of `weighing` | exactly `UnsupportedProfile: defaults with provider conditions is not implemented` and E1d's sentence; no produced text contains "weighing" (stub on the text) | every provider is guarded, none misnamed |
| F9.4 | F9.3 with the pack's `conditions = []` | no refusal; `dfltUniformLabelled = dfltLabelled` (`dfltUniform_legacy`) | not refused without one |
| F9.5 | today's constitution force sets under `[soft]` | `dfltUniform = dfltPremises` | |
| F9.7 (C) | F9.3 asked without `--assume-no-exception` (synthesis edit 9, the second direction) | routes normally: no `providerRefusal`, no E1d sentence; the answer is byte-identical to F9.4's document (the same pack with `conditions = []`) asked without the flag, because only the defaults kinds read `conditions` | refused only with the flag |

### 5.9 PC-11

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F11.1 | u0007.s01, "Anthropic wants Claude to be genuinely helpful … while avoiding actions that are unsafe, unethical, or deceptive.", as a two-candidate set: Anthropic's aim (an `attitude` candidate), or a soft norm with a weighing between being helpful and avoiding harm | both sides check; under the aim's choice the aim's claim is a premise and the norm is not in the chain; under the norm's choice the aim's gated premise is vacuous (`crossSlot_choice`). The choice count is an estimate until Lean computes it from the admitted readings | per choice, one candidate |
| F11.2 | u0112.s11, likewise | as F11.1 | |
| F11.3 | `crossSlot` on an assertion candidate `p(a)` gated by `x1(h)` and an attitude candidate `attitudes__wants__1(a)` gated by `x2(h)` | `[x1(h) → p(a), x2(h) → attitudes__wants__1(a)]` (stub) | each candidate's premise gated by its own atom |
| F11.4 | `crossSlot_legacy` on today's readings documents (no attitude candidate) | the gated premises are today's, byte for byte | the type changes no existing set |

### 5.10 PC-12 (pc-fid-rev2, R3; staged on modality's MD-4a)

Built from the shape of the re-pilot unit **ursp.t4_evidentiary**, in this fixture's own words.

| # | Fixture | Expected | Dir. |
|---|---|---|---|
| F12.1 | `scenarioGuard "u1" C N`, `N` a candidate norm `{"name": "r1", "guard": ["unary", "crossed_fourth", ["var", 1]], "unless": []}`, `C` = `["unary", "ai_runs_research", ["var", 1]]`; `layerRuleIn profileTableMD []` on `["documents@1", "judgments@0", "modality@0", "norm-defaults@0", "norms@0", "readings@1", "relational-fol@0", "soft-norms@0"]` | `N` with guard `["and", ["unary", "crossed_fourth", ["var", 1]], ["unary", "ai_runs_research", ["var", 1]]]` (stub): the condition is the last conjunct, after the rule's own; before modality's row batch covers the list, `some "UnsupportedProfile: modality@0 with readings@1 is not implemented"` (row 17; stub) | the slot's position; `.layer` grants nothing |
| F12.2 (end to end, after MD-4a, modality's row batch and PC-12) | F12.1's list; u1 "At the fourth threshold, AI systems might run the safety research, in which case reviews of AI threats should meet strict standards."; its set `rs-std`: `F`, asserted, content `["top"]`, label `addressee = F`; `Ds_strict`, "Every situation must have its reviews of AI threats meet strict standards, if both that situation has crossed the fourth threshold and AI systems run the safety research at that situation.", labels `addressee = Ds`, `std = strict`; `Ds_default`, the same with "should", the exception decided by `unstated`; the last conjunct of both Ds guards is scenario σ1's condition (sort `situation`, condition `ai_runs_research` at the rule's variable); `crossed` bound | σ1 admitted by modality (one `.model` row per compatible choice); admitted; three rows. A situation past the fourth threshold in which AI systems do not run the safety research and the reviews meet no standard: no Ds rule violated (the conjunct fails); with the conjunct dropped (the seeded bug), `Ds_strict` is violated there. Before MD-4a: both Ds candidates pending, their rows `unknown`, never dropped | the condition limits the situations the rule binds |
| F12.3 | F12.2 with σ1's condition written closed, about one named situation (`ai_runs_research(s_1)`, a constant) | refused `ScenarioUnbound` (modality's text, row 22), not admitted as a guard about every situation | a scenario takes the rule's situation variable or is refused |

## 6. Limits

- G2 says nothing about meaning; only `RouteFacts` admits a stack.
- G3 is success-only. A document refused with the layer may be admitted without it, by a named layer refusal.
- G3 is stated over comparison pairs: identities exchanged (2a), and no authored unit status (2c shows this loses
  no answer). A case outside that domain is still checked; G3 just says nothing about it.
- `listedStacks` on main is `[["scope@0"], ["scope@0", "readings@1"]]`. The constitution set is refused until
  PC-6b proves `ActsScopeRuns` and lists it. A stack of three or more rewriters is admitted only once a batch lists
  it (1.5's listing rule); its pairs being listed admit nothing (F4.13).
- Acts beside readings waits for act phrases' readings elaboration (PC-6c), and a governor's own reading set for
  scope's SC-5 (PC-5b); attitudes beside judgments for AT-3a and AT-2 (PC-1b). Until each, the list is refused, with
  row 7's, row 19's or the layer's own text.
- The record rule says nothing about commitments' own mode beyond `CommitmentsBesideJudgments`, which CM-2 is asked
  to prove (staged on CM-2, a request row).
- A `.layer` profile other than `documents@1` and `judgments@0` is refused with E1 in every list its own whole-list
  theorem does not cover (the layer rule); `risk@0` with `modality@0` stays refused until modality's agreement theorem.
- G3's amendment refuses a request whose stated model keys and references are not one-to-one between the two
  environments, plain requests included (row 16). Section 9's open point 1 records a case where its second conjunct
  refuses a twin of a one-to-one request; the symmetric check then refuses that request too (1.7, F1.3o).
- `ConditionsExact` is a hypothesis of `dfltUniform_sound`, not a check. Until EXP-D3 and defeasible's batch, the
  guard refuses every provider's stated condition, weighing's included.
- No mixed priority statement has a meaning before NM-1.
- Under holistic outranking a split rule is refused (1.10).
- (pc-fid-rev2) A coupling is main's: a set with an unlabelled candidate on a coupled axis is refused with
  `CouplingLabelMissing` (row 20), and no batch relaxes it. An act phrase with several derivations inside a candidate
  waits for act phrases' readings elaboration to carry one derivation per candidate; until then, or if it cannot, the
  candidates holding it are pending. The scenario slot waits for modality's MD-4a and its row batch (PC-12); until
  then the candidates holding it are pending, and `modality@0` in the list is refused by the layer rule.
- No coverage figure here is measured. The unlocks in the plan are ceilings or estimates.

## 7. Choices this specification makes

1. **The interface's rank is a number on the row** (1.1, 1.2), so the stack order is a sort of AR-10's rows and no
   second ordered list exists.
2. **The document mode's rewriters are case rewriters** (`Rewriter Json`, 1.5). Acts and readings have none on
   main, and `pipelineOf` skips them. That is why `["scope@0", "readings@1"]`'s facts are scope's.
3. **The stack rule sits in `checkDocSets` and `checkDoc` right after the gate, and at `check`'s site** after
   today's :1744 check (3.4). Both see the list as written, before `lowerScope` drops `scope@0`. On a scope list,
   `check`'s site alone would never be reached: `decodeScope` refuses first (draft 1's placement).
4. **`documentRefusal` takes `senses`** and returns `pending` for today's check 2, so it reproduces today's order
   and texts exactly (3.4).
5. **G3's success direction names one relaxation**, `invalid open-term arguments` (1.7). Judgment records may
   repeat argument sorts, and W2 open terms may not. G3 is stated over comparison pairs (the ruling's 2a to 2e):
   identities exchanged, authored statuses omitted on both sides, `layerRefusal` narrow.
6. **The soft reader is the author rule**, because `dependsOn_primeNode` is false (3.1, F1.8).
7. **A rights block is read through `blockFormulas` and one carrier conjunction `andAll`**, so that
   `UnitView.own` keeps its type (3.1). The scan reads names only.
8. **A governor unit is not a usage-map row**; its status is scope's fold (3.5).
9. **A split under holistic outranking is refused** (1.10), the conservative side of an undecided question.
10. **`outweighs` decisions stay per act** (1.10), and the decision key covers exceptions and switches, as the
    DRI's ruling 1(e) names.
11. **E1 and E2 say "uses"** (2.1), amending composition.md 2.1 before any registration.
12. **`Pack.conditions` is keyed by soft's `DecisionKey`**, so a reader finds a decision by its key and never by
    spelling its name (Tree.lean:297). The key a rule reads is `decisionRule N` (1.9, 1.10).
13. **A reference's content is the model it names** (1.7, 2a), so a reference that names no model keeps its value,
    as the ruling's "any other stated value is kept unchanged" says. G3 and 2a's lemma take the hypothesis of the
    DRI's G3 amendment to ruling item 2a (`swapInjective`), and a request outside it is refused by validation on
    both sides (`checkDocSets_swapClash`, F1.3l).
14. **Shared decisions take the ruling's second option** (1.10): the invariant is restated as equality of
    decision keys with consistent sorts (`decNodup` on the deduplicated table) and exception metadata (`decMeta`).
    The table deduplicates equal entries, not keys, so `mem_decisions` and its uses keep their statements.
15. **E1 on three or more rewriters** names the first unlisted pair, by positions `(i, j)`, `i < j`, ordered by
    `i` then `j`. When every pair is listed it names the whole stack with E1s (3.4).
16. **The defaults guard reads every provider** (`providerConditions`, 1.9), and its sentence E1d names no
    provider and no document feature (2.1).

Draft 4 (the pc-d2 FIX) makes these choices where the ruling left one open:

17. **The clash validation is the first check of every request** (1.7, row 16): before the gate, in `checkDocSets`
    and `checkDoc`, with and without `judgments@0`. Its text is one constant, `swapClash`, so both sides answer it
    byte for byte. `statedPairs` reads `layerProfiles` and `plainProfiles`, which a request and its twin share.
18. **C1 on cardinality takes the first option** (1.2): its slot is `"layer"`, as qt-a3c's row writes it, and
    `slotAgrees` is not widened.
19. **The layer rule names the layer and the list's route head** (3.4): E1 needs two features, and the route head
    (`headProfile`, the row `routeOf` reads) is the profile whose route the layer would join. For F4.9 it is
    `risk@0`, so both features DEC 15 names are rendered.
20. **A layer's coverage is a table of list predicates** (`layerCovers : List (String × (List String → Bool))`),
    each entry tied to a `LayerFacts` proposition by `layer_evidence`, so a theorem over a whole admitted list
    lifts exactly the lists it covers, and a name proves nothing.
21. **The staged decision key is PC-6a** (soft-norms' file, before PC-9) and the constitution stack is PC-6b (after
    PC-4 and PC-6), so each named prerequisite is one batch.
22. **The shared document-mode names move to `Service/DocumentBase.lean`, and `listedStacks` to
    `Compose/Stack.lean`** (3.4), keeping their qualified names, so no caller's text changes.
23. **G1b's countermodel theorem takes conflict-freedom** (`hc`), as `norms_route_countermodel` does: a base expands
    to a structure of the complete vocabulary only when no conflict blocks it.

Round 2 of the pc-d2 FIX makes this choice where its decision (item 1) left one open:

24. **A request without `judgments@0` has no twin** (1.7). The twin the symmetric check reads is G3's,
    `withoutJudgments j`, for a request that lists `judgments@0`. So a plain request's check reads its own exchange
    alone, and no plain request's answer changes from round 1's (F1.3n).

pc-fid-rev (DRI 2026-10-29, item 4) makes these choices where the order left one open:

25. **An own-mode outside profile is a document record in the document mode** (3.4, B2). The cell `layer` ×
    `outside` refused until the outside route had `Content`; a profile whose slot is no route head has no route in
    the document mode, so it is read by no decoder there, and the list's answer is the list's without it. This is
    the conservative reading: it admits nothing the list without the record does not admit.
26. **The generic clause of `RouteFacts` needs every pair, not only adjacent ones** (1.5, B6). A rewriter reads what
    every earlier rewriter wrote, so adjacent pairs leave a gap; every pair at positions `i < j` closes it.
27. **A stack of three or more is still listed by a batch** (1.5, B6). Pairs being listed do not admit a stack: the
    stack rule, E1s and F4.7 are unchanged (statement-review ruling 10; ruling 1(b), an ordered pipeline theorem per
    listed stack, which `StackRuns` at that stack is). The listing rule makes the batch that lists a stack's last pair
    list the stack, with `stack_evidence`. Admitting a stack automatically when its pairs are listed would change when
    E1s is reached, so it is not adopted.
28. **Acts beside readings is stated per choice** (3.6, B1). How a candidate's joined act is carried is act phrases'
    readings elaboration's; the composition is the per-choice statement `ActsChoiceFaithful`, which holds whatever
    that representation is.
29. **RESOLVE resolves a reading's content as it resolves a unit's** (3.7, B4), because composition's `Content` is
    both, and the readings route reads only the sets' shapes, couplings and narrowings, which RESOLVE keeps.
30. **A judgment inside an attitude's content is read by the unit** (3.1, B5): the plan's 3.3 row 2 had already
    ruled "the judgment reader extended to attitude guard nodes"; PC-1b states it.
31. **A governor's own reading set waits for SC-5** (3.5, B3): scope 11.1 assigns it there. This plan's statements
    are stated over scope's functions, so they need no new statement when SC-5 extends them.

pc-fid-rev2 (DRI 2026-10-30 pc-fid-rev2, item 1) makes these choices where the order left one open:

32. **In form (b) of the coupling rule, a candidate the axis does not apply to carries its own id** (3.2, R1), a value
    no other candidate of its set carries. So a coupling on that axis alone never joins it to another candidate, and
    the rule holds whether or not the sets are also coupled on another axis. Any shared value would decode; a shared
    value would join F to a Ds candidate when the force coupling stands alone, so it is not adopted.
33. **A candidate names its derivation by act phrases' index, as a label** (3.6, R2; axis `act`). The index is the
    derivation order `VE.Acts.readings` lists, Lean's, so no second numbering exists; how the elaboration reads it on
    the wire is act phrases'.
34. **A frame declaration that removes a derivation counts as a narrowing** (3.6, R2). Declaring a modifier marker as
    an argument marker silently fixes the all-parts reading (section 9's second mutant), which is the choice the order
    forbids without a cited reason.
35. **The scenario slot is a new staged batch, PC-12** (3.11, R3), not a case of PC-11's `CrossContent`: a mixed-kind
    candidate is a whole candidate, while the slot is one conjunct inside a candidate's rule. Its position is defined
    by scope's `reguard`, which modality's MD-4a already uses for governed rules, so the inline and the governed forms
    give one rule and no second composition of a condition with a rule exists.
36. **A limiting purpose needs no new statement** (3.1, R4(a)). It is a bound judgment in a guard, which PC-1's reader
    and PC-2b's rows already cover; the order's rule is a writing rule, and F2.11 checks the reader on its shape.

## 8. Review checklist

- Is every statement in sections 1 and 3 true as stated? Give a counterexample where not, especially for
  `correlate_judged`, `split_decisions` and G3.
- Does `documentRefusal` reproduce `environmentOf`'s order and texts exactly?
- Does each English sentence of 2.1 to 2.3 have one reading?
- Does any statement duplicate a definition that another family owns?
- Does any (C) fixture fail to test what the DRI named?

The confirmation review of draft 4 (pc-d2's DRI-RULING item 11) covers only edits 1 to 10, the refreshed section
9 (build step, Lean output, the stub's hash, every guard's result) and every fixture the ruling names. Draft 5's one
statement review (DRI 2026-10-29, item 4; one round, the sprint rule) covers the pc-fid-rev change log's statements
(1.5, 3.1, 3.4 to 3.7), their fixtures (F1.9 to F1.11, F4.11 to F4.17, F5.6 to F5.8, F6.14 to F6.16, F7.6 to F7.8),
row 19 of 4 and the refreshed section 9; then the family-scoped re-pilot runs on a fresh draw. Draft 6's one
statement review (DRI 2026-10-30 pc-fid-rev2, item 2; one round, at most one apply round) covers the pc-fid-rev2
change log's statements and rules (3.1's limiting purpose, 3.2's coupling rule with `admitS2Rest_couplings` and
`compatibleChoices_admitS2`, 3.6's derivation rule, 3.11), their fixtures (F2.10, F2.11, F6.17, F12.1 to F12.3), rows
20 to 22 of 4 and the refreshed section 9; then a family-scoped re-pilot on a fresh draw. The plan's
change log (its first section) lists where each edit is applied. Batches stay held until that review passes, and
then follow the amended order (plan section 8).

## 9. Statement check record

Every Lean statement of sections 1 and 3, with stubs for every new name, is written in
`lean/SpecStubs_profile-composition.lean`. Fixtures marked "stub" in section 5 are `#guard` lines or proofs in that
file. The file is a scratch file. It is untracked on this branch, and it is never committed.

**What the run shows, and what it does not.** Elaboration with `sorry` establishes typing only: a statement that
elaborates with `sorry` is well formed against main's names, and nothing more. It is not proved, and it may be
false (round 1's open point 1, below, was a pair of statements that elaborated and could not both be true). The run
checks that every statement is well formed, that every `#guard` computes the value written, and the ten proofs
below. It does not check:
- the acyclic imports of 3.4. The stub is one file, so it holds every module at once; PC-4's own `lake build` checks
  the imports, and a cycle fails it;
- the new lines in `checkDocSets` and `checkDoc` (PC-1's clash check, PC-4's stack rule), which edit main's
  functions. PC-1's F1.3m and F1.3o and PC-4's F4.4 test them end to end;
- edits to main's definitions, which the stub states against named stand-ins: `ProfileRow.interface` (a function of
  the profile name, for the new field), `SoftNode.splitFrom` (a function that returns `none`, for PC-6a's field),
  `Pack.conditions` (a function that returns `[]`, for PK-1's field), `exceptedNameK`, `offNameK`,
  `exceptedDecisionsK`, `offDecisionsK`, `keyedDecisionsK`, `decisionsK`, `decisionNamesK`, `excepted_keyK`,
  `decisionNames_splitK` and `decisionNames_eqK` (1.10's revised names and table), `DecMeta` (the field `decMeta`),
  `gate_acts'`, `gate_scope'` and `gate_acts''` (the revised gate theorems), and `profileTablePC6` and
  `profileTableMD` (the table as PC-6 and MD-2 leave it).

**Run on 2026-10-30 (pc-fid-rev2, DRI 2026-10-30 pc-fid-rev2 item 1: R1 to R4; with its review fix, item 2).** On
this branch, `lean/` tree of `73711d1ba` (tree `b589be842`, the same as every earlier run's since `560abc9a9`: every
commit since changes `docs/` only), with Lean 4.24.0 (x86_64-unknown-linux-gnu, commit `797c613eb9b6`). The stub file
is at SHA-256 `c55eb55a7f1ee27a9e281069b0fb2ea343d2cc30156f38c3828efc8762ecd235` (1,775 lines). Every expected value
was read from the code on this branch (main at `d25bc343b` for `lean/`; `Readings/SupWire.lean` and
`docs/spec/act-phrases.md` are the same on main at `432763b06`), computed by the run, and for `profileTableMD` from
MD-2's row as the stub writes it.

The run, from the worktree:

```
cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_profile-composition.lean
```

The build. `lean/.lake` was empty, so this run built it. `python3 tools/lean_share.py restore` refused with exit code
3 twice: first `lean/ differs from HEAD (lean/SpecStubs_profile-composition.lean)`, then, with the stub moved out of
`lean/` and back after, `no stored build for this key (71747c34ed4c9100)`. `cd lean && PATH=~/.elan/bin:$PATH lake
build` answered `Build completed successfully (1135 jobs).`, exit code 0, and `lake build --no-build` then answered
`All targets up-to-date (1135 jobs).`. The review fix's run built nothing: `lake build --no-build` answered `All
targets up-to-date (1135 jobs).` on that build.

Baseline. The stub as the DRI ruling of 2026-10-30 left it (SHA-256
`d4c2d849bff8233d53dea13349d63e4678bed1e2e4c55fcfd6c14e2b804750fb`, 1,591 lines) was rerun first, on this build: exit
code 0, 104 `sorry` warnings and no other message, as the ruling's run recorded. This revision edits that file in
place: two imports (`VE.Readings.UnspecifiedExamples`, `VE.Acts.MeaningExamples`, both modules of main's `VE`
library), one phrase of the header comment, and one block appended at the end. So every earlier declaration and
guard keeps its text, two lines lower than in the ruling's record.

The review fix (pc-fid-rev2's statement review, finding 1) edits the revision's stub (SHA-256
`40f3113976aed1a8ed3669952d57eae815cfafafaa034744043b1a8b75517ed9`, 1,767 lines) in place. That stub, rerun first on
this build from a scratch copy: exit code 0, 106 `sorry` warnings and no other message, the last two at lines 1616
(`readingsCaseOf`) and 1620 (`compatibleChoices_admitS2`), as the revision's run recorded and the statement review
reproduced. The fix adds the theorem `readingsCaseOf_keeps` before `compatibleChoices_admitS2` and the conjunct
`cs = VE.Readings.choices a.D` to its conclusion, with their docstrings. No other line changes, and every line after
1617 is eight lines lower than in the revision's stub.

**Lean output (this run).** Exit code 0. The output is 107 lines, each `warning: declaration uses 'sorry'`, with no
error and no other message. The first three lines and the last four:

```
SpecStubs_profile-composition.lean:38:4: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:47:4: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:56:4: warning: declaration uses 'sorry'
… (100 more lines, the same warning)
SpecStubs_profile-composition.lean:1539:8: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:1616:4: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:1620:8: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:1627:8: warning: declaration uses 'sorry'
```

The file has 258 declarations: 175 `def`, 75 `theorem`, 5 `inductive` and 3 `structure`. All elaborate. pc-fid-rev2 adds
35: 32 `def` and 3 `theorem`, one of those theorems from the review fix. The 107 that use `sorry` are the ruling's 104,
by the same names in the same order (the 42 stub definitions and 62 theorems listed under the ruling's run below), and
three new ones, last: `readingsCaseOf` (a stub definition, line 1616), `readingsCaseOf_keeps` (a theorem, the review
fix, line 1620) and `compatibleChoices_admitS2` (a theorem, line 1627). The other 151 declarations elaborate without
`sorry`. Eleven are theorems the file proves: the ruling's ten (below; their lines are two lower here) and
`admitS2Rest_couplings` (new, line 1604, by `simp [admitS2Rest, hr, hs, bind, Except.bind, h]`): main's S2a admission
returns main's coupling refusal, a statement about main's code. The other new definitions are `scenarioGuard` (3.11,
defined as the specification gives it) and the fixtures' data: `rdg`, `three`, `cpl`, `couplingIds`, `errOf`, `setU3`,
`setsA`, `couplingsA`, `setsB`, `couplingsB`, `setsU`, `candL`, `rset`, `docOf`, `rsetU3`, `docA`, `docB` (F2.10);
`describeV`, `describeFx`, `describePhrase`, `describeAtom`, `describeTree`, `describeMeanings`, `describeD15` (F6.17);
`varOne`, `crossedFourth`, `runsResearch`, `dsNorm` (F12.1); `labGuard`, `limitingGuard` (F2.11). No guard computes with
a `sorry` definition.

**pc-fid-rev2's mutants** (the revision's run, on its stub, SHA-256 `40f31139…`, so its line numbers: eight above
this run's for F6.17 and F12.1). That run tried two scratch copies of its final stub, each with one change, run as
`lean/Scratch_mutant-<name>.lean` and deleted after. The review fix adds no mutant: its two statements are typed with
`sorry`, so no guard computes with them, and neither mutant's guard changed.
- **`scenarioGuard` as a carve-out** (`VE.Scope.applyEffect u (.carveOut C) norm`: the condition put in the rule's
  `unless` list instead of its guard, PC-12's seeded bug). Exit code 1; F12.1's first guard fails:

  ```
  Scratch_mutant-slot.lean:1750:0: error: Expression
    (Service.DocumentChain.scenarioGuard "u1" runsResearch dsNorm).toOption ==
      some (dsNorm.setObjVal! "guard" (Json.arr #[Json.str "and", crossedFourth, runsResearch]))
  did not evaluate to `true`
  ```
- **The frame "describe" with "in" declared as an argument marker** (`⟨["describe"], ["", "in"], [""], []⟩`: a frame
  declaration that removes a derivation, 3.6). Exit code 1; F6.17's five guards fail (lines 1731, 1733, 1735, 1736 and
  1740): main's grammar then lists one derivation, "in the annual report" an argument of every part, so `read` no
  longer gives `many` and D-15's text is not the declaration's answer. The first:

  ```
  Scratch_mutant-frame.lean:1731:0: error: Expression
    Acts.MeaningExamples.rd describeV describeFx describePhrase == Acts.Listing.ok [describeTree false, describeTree true]
  did not evaluate to `true`
  ```

  Beside these messages, each copy's output held the 106 `sorry` warnings of the revision's final run, omitted here.

**The DRI ruling's run (2026-10-30, item 1, `manage-agents/reviews/dri-decisions-20261030-pc-fid-rev.md`:
`SplitReach`'s effect clause), kept; its stub's line numbers.** On this branch,
`lean/` tree of `e9a0b2dd4` (tree `b589be842`, the same as `7afd055d6`'s, `81a8c5473`'s, `d7291184a`'s and
`560abc9a9`'s: every commit since changes `docs/` only), with Lean 4.24.0 (x86_64-unknown-linux-gnu, commit
`797c613eb9b6`). The stub file was at SHA-256
`d4c2d849bff8233d53dea13349d63e4678bed1e2e4c55fcfd6c14e2b804750fb` (1,591 lines). Every expected value was read from
the code on this branch (main at `d25bc343b`), or, for qt-a3c's `cardinality@0` row, from main after qt-a3c, and for
the rows CM-2 and MD-2 add, from those plans' rows as the stub's `profileTableCM` and `profileTableMD` write them.

The run, from the worktree:

```
cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_profile-composition.lean
```

The build. This run ran no `lake build`: `lake build --no-build` answered `All targets up-to-date (1135 jobs).`, the
build of the pc-d2 rounds (round 1 built it: `Build completed successfully (1135 jobs).`, after `python3
tools/lean_share.py restore` refused with exit code 3, no stored build for the key).

Baseline. The stub as the review fixes left it (SHA-256
`08c9828ec63c78f640c7272449b91698a33b0a16c53c633e7a4c26d877d49951`, 1,581 lines) was rerun here, from a copy, on this
build: exit code 0, 104 `sorry` warnings and no other message, as the review fixes' run recorded (with 90 passing
guards and 9 proofs). The ruling edits that file in place. (The stub
as pc-fid-rev left it, SHA-256 `d8efbf48…`, 1,532 lines: exit code 0, 101 warnings and 89 guards, reproduced by its
statement review.)

**Lean output (final run).** Exit code 0. The output is 104 lines, each `warning: declaration uses 'sorry'`, with no
error and no other message. The first three lines and the last:

```
SpecStubs_profile-composition.lean:36:4: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:45:4: warning: declaration uses 'sorry'
SpecStubs_profile-composition.lean:54:4: warning: declaration uses 'sorry'
… (100 more lines, the same warning, one per declaration named below)
SpecStubs_profile-composition.lean:1537:8: warning: declaration uses 'sorry'
```

The file has 223 declarations: 143 `def`, 72 `theorem`, 5 `inductive` and 3 `structure`. All elaborate. pc-fid-rev
added 25: 20 `def` and 5 `theorem`; it moved `RouteFacts` (with its generic clause) and `listed_evidence` to the end
of the file, after the names the clause reads, and added `import VE.Readings.Faithful`. The review fixes add 6 `def`
(`caseManifest`, `effectContent`, `withEffectContent`, `documentLayersOf`, `caseChain`, `ResolvedEffect`); they move
`recordProfile` from `VE.Compose.Matrix` to `VE.Compose` (`Dispatch.lean`'s namespace, 3.4), and `readingsChosen`
from `VE.Acts` to `VE.Compose.Contract`, where it is defined, so it no longer uses `sorry`. The DRI ruling adds one
theorem, `splitReach_effect` (proved, below), and the effect conjunct of `SplitReach`; neither uses `sorry`. The 104
that use `sorry` are pc-fid-rev's 101 without `readingsChosen`, by the same names in the same order, and the review
fixes' 4 new ones (`caseManifest`, `effectContent`, `withEffectContent`, `caseChain`); the ruling's run has the same
104 in the same order. In file order:
- 42 stub definitions (body `sorry`): `IntendedActs`, `splitMapOfCase`, `resolveDocument`, `resolveContent`,
  `positions`, `formulaMentions`, `IntendedAt`, `resolveCase`, `caseManifest`, `effectContent`, `withEffectContent`
  (the last three new in the review fixes), `actsRewriter`, `closeReq`, `rightsAuthorFormulas`, `blockFormulas`,
  `UnitContent.judgedIn`, `statedIds`, `statedPairs`, `exchange`, `withoutJudgments`, `IdSite.twin`, `correctAt`,
  `noUnitStatus`, `withoutStatuses`, `verdictFields`, `unitStatuses`, `withoutCommitmentsBlock` (new in pc-fid-rev),
  `requestOf`, `compatibleChoices`, `pendingAt`, `rowAt`, `conflictAt`, `chainReadings`, `chainDoc`, `questionOf`,
  `strippedOf`, `splitSoft`, `leastUniform`, `choiceActs`, `caseSets`, `caseChoiceLinks` (the last three new in
  pc-fid-rev), `caseChain` (new in the review fixes).
- 62 theorems (proof `sorry`; typed, not true): `pipeline_preserves`, `pipeline_off`, `pipeline_names`,
  `checkDocSets_pipeline`, `unlisted_refused`, `admitted_listed`, `layer_admitted`, `gate_acts'`, `gate_scope'`,
  `gate_acts''`, `crossSlot_choice`, `crossSlot_legacy`, `opensIn_generated`, `correlate_judged`, `preds_andAll`,
  `dependsOnC_append`, `govern_carveOut_judged`, `govern_narrow_judged`, `opensIn_attitude` (new), `judgedIn_legacy`,
  `judgedIn_soft`, `swap_correct`, `withoutJudgments_ids`, `checkDocSets_judgments_transparent`,
  `checkDocSets_clashFirst`, `swapInjective_twin`, `checkDocSets_swapClash`, `checkDocSets_withoutStatuses`,
  `checkDocSets_ignores_commitments` (new), `layeredOf_ids`, `layeredOf_rights`, `layeredOf_entails`,
  `decodeRightsU_X_wellFormed`, `chainReadings_rows`, `chainReadings_covers`, `chainReadings_rowsHold`,
  `acceptanceXV`, `entailsXV_constraint`, `countermodelXV`, `composed_superpose_all`, `applyEffect_narrowing`,
  `foldGovernors_judgments`, `exceptedName_unsplit`, `offName_unsplit`, `decisions_unsplit`, `decMeta_unsplit`,
  `excepted_keyK`, `decisionNames_splitK`, `decisionNames_eqK`, `declarations_acts`, `split_shares_decisions`,
  `split_sorts`, `split_decisions`, `splitSoft_base`, `resolve_then_govern`, `resolve_then_split`,
  `precedence_apart`, `dfltUniform_legacy`, `dfltUniform_sound`, `listed_evidence` (moved), `stack_evidence` and
  `stackRuns_all` (new).

The other 119 declarations elaborate without `sorry`. Ten of them are theorems the file proves:
`interface_slot`, `interface_functional` and `rewriter_ranks_distinct` (by `decide`, lines 125, 127, 156),
`refuseAll_runs` (by `unfold`, `intro`, `simp`, line 252), `splitReach_effect` (new in the DRI ruling, by `simp`, line
305: a split case whose one governor keeps its id, unit, recorded reach and reach, `.frontier`, but whose effect
changes, `.precedes` to `.yields`, has no `SplitReach`), `layer_evidence` (by `intro`, `simp`, line 571, true on main
because `layerCovers = []`), `softContent_formulas` (by `rfl`, line 667), `clashRefusal_some` (by `unfold`,
`by_cases`, `cases`, `simp`, line 877), `decisionRule_unsplit` (by `simp`, line 1187) and `readingsFaithful` (new in
pc-fid-rev, line 1420, the term `superpose_faithful D h hch hs c hc S he hq r hr vs`: `ReadingsFaithful` is main's
`superpose_faithful`, word for word, so its `RewriterFacts` entry asks nothing new of SUPERPOSE). No guard computes
with a `sorry` definition: Lean refuses to evaluate one, and the run has no error.

A `#guard` that computes another value is an error, and so is a proof that does not close. The DRI ruling adds no
guard and one proof, `splitReach_effect`. This run tried one scratch copy of the stub with one change, the ruling's
seeded mutant, run as `lean/Scratch_mutant-effect.lean` from the final stub at the SHA-256 above and deleted after:
- **`SplitReach` without the effect conjunct** (`∀ g ∈ D.governors, ∀ g₀ ∈ D₀.governors, g.id = g₀.id → g.effect =
  g₀.effect` deleted), on a governor whose effect changes. Exit code 1; the proof of `splitReach_effect` fails:
  without the conjunct `SplitReach` holds on that case, so its negation leaves `False`:

  ```
  Scratch_mutant-effect.lean:306:88: error: unsolved goals
  M : Acts.SplitMap
  D₀ D : Scope.SDoc
  hl : D.layout = D₀.layout
  h₀ :
    D₀.governors =
      [{ id := "g1", unit := "u1", effect := Scope.Effect.precedes, reach := Scope.Reach.frontier, units := [] }]
  h :
    D.governors =
      [{ id := "g1", unit := "u1", effect := Scope.Effect.yields, reach := Scope.Reach.frontier, units := [] }]
  ⊢ False
  ```

  Beside this message, the copy's output held the 104 `sorry` warnings of the final run, omitted here. A second
  scratch copy (`lean/Scratch_sanity-effect.lean`, deleted after) added, after `SplitReach`, the same case with the
  effect unchanged (`.precedes` on both sides) and proved `SplitReach M D₀ D` on it by the same `simp`: exit code 0,
  the 104 warnings only. So the clause refuses a changed effect and admits an unchanged one.

**The review fixes' mutant** (on their stub, SHA-256 `08c9828e…`, so its line numbers), not rerun: its guards are
unchanged and pass. That run tried one scratch copy of its stub with one change, the seeded bug of the derivation,
run as `lean/Scratch_mutant-layers.lean` and deleted after:
- **`documentLayersOf t := ["judgments@0"]`** (the list not derived from the rows, so CM-2's row would not reach it).
  Exit code 1; F4.11's guard on `profileTableCM` and its guard on the decoders' environment fail, while the guard on
  main's table still passes (main has no record, so only a table with a record shows the derivation):

  ```
  Scratch_mutant-layers.lean:400:22: warning: unused variable `t`

  Note: This linter can be disabled with `set_option linter.unusedVariables false`
  Scratch_mutant-layers.lean:436:0: error: Expression
    documentLayers' == ["judgments@0", "commitments@0"]
  did not evaluate to `true`
  Scratch_mutant-layers.lean:438:0: error: Expression
    (withoutDocumentLayers'
            (Json.mkObj
              [("profiles",
                  Json.arr
                    #[Json.str "commitments@0", Json.str "judgments@0", Json.str "norms@0",
                      Json.str "relational-fol@0"])])).getObjValD
        "profiles" ==
      Json.arr #[Json.str "norms@0", Json.str "relational-fol@0"]
  did not evaluate to `true`
  ```

  Beside these messages, the copy's output held the 104 `sorry` warnings of that round's run, omitted here.

**pc-fid-rev's mutants** (on its stub, SHA-256 `d8efbf48…`, so its line numbers), not rerun: their guards are
unchanged and pass. That run tried two scratch copies of its stub, each with one change, each run as
`lean/Scratch_<name>.lean` and deleted after:
- **the full grid without the pair `["acts@0", "readings@1"]`** (B1's pair missing, its stacks kept). Exit code 1;
  three guards fail, F4.13's (with that pair unlisted the first unlisted pair, not the whole stack, is named), F4.14's
  invariant, and F6.14's second:

  ```
  Scratch_mutant-grid.lean:1505:0: error: Expression
    stackRefusalIn (List.filter (fun x => decide (x.length ≤ 2)) fullGridStacks) pilotDocList ==
      some "UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0, readings@1 is not implemented"
  did not evaluate to `true`
  Scratch_mutant-grid.lean:1509:0: error: Expression
    fullGridStacks.all fun s =>
      decide (s.length < 3) || (stackPairs s).all fun x => fullGridStacks.contains [x.fst, x.snd]
  did not evaluate to `true`
  Scratch_mutant-grid.lean:1515:0: error: Expression
    stackRefusalIn fullGridStacks ["acts@0", "documents@1", "judgments@0", "norms@0", "readings@1", "relational-fol@0"] ==
      none
  did not evaluate to `true`
  ```
- **PC-1b's reader without the attitude contents** (`withAttitudeContents keys fs := fs`, PC-1b's seeded bug). Exit
  code 1; F1.9's first guard fails:

  ```
  Scratch_mutant-attitude.lean:685:26: warning: unused variable `keys`

  Note: This linter can be disabled with `set_option linter.unusedVariables false`
  Scratch_mutant-attitude.lean:698:0: error: Expression
    opensIn ["could_weaken", "new_capabilities"]
        (withAttitudeContents [("attitudes__believes__1", Formula.unary "could_weaken" (Term.const "r"))]
          [(Formula.unary "new_capabilities" (Term.const "r")).and
              (Formula.unary "attitudes__believes__1" (Term.const "r"))]) ==
      ["could_weaken", "new_capabilities"]
  did not evaluate to `true`
  ```

  Beside these messages, each copy's output held the `sorry` warnings of that run, omitted here. Round 1's and
  round 2's mutants (F4.9's text; F1.3o's guard; the one-sided clash check) are recorded below, under the earlier
  rounds' records, and were not rerun: their guards are unchanged and pass.

**The executable guards (this run).** 105 `#guard` commands and the 11 proofs: the ruling's 90 and 10, and
pc-fid-rev2's 15 guards and one proof (the last rows). Every one passes; none fails. Lines are this run's stub's, at
SHA-256 `c55eb55a…` (the ruling's lines plus 2; pc-fid-rev2's lines after 1617 are the revision's plus 8, the review
fix).

| Fixture | Guard | Expected | Result |
|---|---|---|---|
| F3.4 | `interface_slot`, `interface_functional`, `rewriter_ranks_distinct` | `decide` succeeds | passes: three proofs, no `sorry` (lines 127, 129, 158) |
| F3.4b | `slotAgrees` on every row of `plannedSlots`; on qt-a3c's `cardinality@0` row (slot `"layer"`) | true; true | passes (2 guards, lines 140, 141) |
| F3.4c | the interface values of the planned rows | six `.layer`; `.outside` for `commitments@0`; `.pack "weighing"` | passes (3 guards, lines 143, 145, 146) |
| F3.5 | `rewriters profileTable` | `[(11, "acts@0"), (10, "ve.discourse@1"), (20, "right-clauses@0"), (30, "readings@1"), (12, "scope@0")]` | passes (1 guard, line 160) |
| F3.6 | `stackOf profileTable` on its four lists | `["scope@0", "readings@1"]`, `["acts@0", "scope@0"]`, `["scope@0"]`, `[]` | passes (4 guards, lines 162-165) |
| F3.7 | `refuseAll_runs` | proved | passes (line 254) |
| 1.5 | `layer_evidence` on main | proved | passes (line 573) |
| 1.5 (new) | `readingsFaithful` | proved from main's `superpose_faithful` | passes (line 1422) |
| 3.6 (new, DRI 2026-10-30 item 1) | `splitReach_effect`: a governor whose effect changes, its id, unit, recorded reach and reach kept | proved: no `SplitReach`; without the effect conjunct (the ruling's mutant) the proof fails | passes (line 307) |
| F4.1 | `gateOf` on acts with soft-norms | `.error "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"` | passes (1 guard, line 526) |
| F4.3 | `documentRefusal` on its three lists | the two `.refused` texts, then `none` | passes (3 guards, lines 530, 532, 534) |
| F4.4 | `stackRefusal`; `gateOf` on the same list | `some "UnsupportedProfile: acts@0 with scope@0 is not implemented"`; `.ok .norms` | passes (2 guards, lines 505, 522) |
| F4.5 | `stackRefusal` on its two lists | `none`, `none` | passes (2 guards, lines 507, 508) |
| F4.7 | `stackRefusalIn` with every pair listed | `some "UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0 is not implemented"` | passes (1 guard, line 510) |
| F4.8 | `stackRefusalIn` with one later pair unlisted | `some "UnsupportedProfile: ve.discourse@1 with readings@1 is not implemented"` | passes (1 guard, line 515) |
| F4.9 | `gateOf profileTableMD`; `layerRuleIn profileTableMD []`; with a covering entry, on the risk and modality list | `.ok .risk`; `some "UnsupportedProfile: modality@0 with risk@0 is not implemented"`; `none` | passes (3 guards, lines 541, 544, 546) |
| F4.10 | `otherLayer profileTable` on every profile; `layerRule` on F1.1's list | false for each; `none` | passes (2 guards, lines 549, 550) |
| F4.11 (B2; revised in the review fixes) | `recordProfile` on main's table, on `profileTableCM` for `commitments@0` and for the four other outside profiles; `gateOf` with and without `commitments@0`; `stackOf profileTableCM`; `documentLayersOf profileTable` against main's `documentLayers`; `documentLayers'` (the list derived from `profileTableCM`); `withoutDocumentLayers'` | none on main; true; false for each; both `.ok .readings`; `["readings@1"]`; equal; `["judgments@0", "commitments@0"]`; `["norms@0", "relational-fol@0"]` | passes (8 guards, lines 433, 434, 435, 437, 443, 447, 448, 450) |
| F4.12 (new, B6) | `stackOf` on `pilotDocList`; `stackRefusal` on it; `stackRefusalIn fullGridStacks` on it | `["ve.discourse@1", "acts@0", "scope@0", "readings@1"]`; `some "UnsupportedProfile: ve.discourse@1 with acts@0 is not implemented"`; `none` | passes (3 guards, lines 1566, 1567, 1568) |
| F4.13 (new, B6) | `stackRefusalIn` with the pairs alone | `some "UnsupportedProfile: stack ve.discourse@1, acts@0, scope@0, readings@1 is not implemented"` | passes (1 guard, line 1570) |
| F4.14 (new, B6) | the listing rule's invariant; rank order | true; true | passes (2 guards, lines 1574, 1575) |
| F5.1, F5.2 | the six `dependsOnC` and list guards | as section 5.5 | passes (6 guards, lines 708-715) |
| F1.9, F1.10 (new, B5) | `opensIn` through `withAttitudeContents` and on the guard alone; an unused key | `["could_weaken", "new_capabilities"]`; `["new_capabilities"]`; the formulas unchanged | passes (3 guards, lines 736, 740, 744) |
| F6.1b | `decisionRule_unsplit` | proved | passes (line 1189) |
| F6.8 | `gateOf profileTablePC6` on the `.clauses` list | `.ok .clauses` | passes (1 guard, line 609) |
| F6.13 | `stackRefusalIn` with `["acts@0", "scope@0"]` listed, on F4.4's list | `none` | passes (1 guard, line 519) |
| F6.14 (new, B1) | `stackRefusal`; `stackRefusalIn fullGridStacks` on the acts and readings list | `some "UnsupportedProfile: acts@0 with readings@1 is not implemented"`; `none` | passes (2 guards, lines 1578, 1580) |
| F7.6 (new, B4) | `stackOf` on ursp.t2_plan's list; `stackRefusalIn` with PC-6b's and PC-7b's pairs; with the full grid | `["ve.discourse@1", "acts@0", "readings@1"]`; `some "UnsupportedProfile: ve.discourse@1 with readings@1 is not implemented"`; `none` | passes (3 guards, lines 1584, 1586, 1590) |
| F7.7 (new, B4) | `setShape` on a two-reading set | `("rs-plan-a", "u2", 1, ["cond", "uncond"])` | passes (1 guard, line 1542) |
| F9.1, F9.2 | the three `dependencyOrder` guards | ok, ok, error | passes (3 guards, lines 1321, 1322, 1324) |
| F9.6 | `providerRefusal` contains `weighing` | false | passes (1 guard, line 1379) |
| 2a | `swap` on `v₁`, on `v₂`, on a third value | `v₂`, `v₁`, the value | passes (3 guards, lines 915-917) |
| F1.3 | `layerRefusal` on `JudgmentListedUnused: u0036.s05 reasonable`, on `CheckerUnavailable: judgments@0 with alternatives@0 …`, on `document needs units` | true, true, false | passes (3 guards, lines 919-921) |
| F1.3d | `judgmentGateTexts`; `layerRefusal` on its one text | `["UnsupportedProfile: judgments@0 requires documents@1"]`; true | passes (2 guards, lines 923, 924) |
| F1.3b, F1.3f, F1.3h, F1.3j, F1.3k | `layerRefusal` on the six validation texts of row 15 | false for each | passes (6 guards, lines 926-931) |
| F1.3l, F1.3m, F1.3o | `layerRefusal swapClash` | false | passes (1 guard, line 933) |
| F1.3l | `swapInjectiveOf` on F1.3l's values (`d`'s key `k1`, a dangling reference `k2`) | false | passes (1 guard, line 936) |
| F1.3h | `swapInjectiveOf` on a correct key and a reference to it | true | passes (1 guard, line 938) |
| open point 1 (resolved) | `swapInjectiveOf` on `j₁`'s values; on its twin's (`j₂`'s); the first conjunct alone on the twin's | true; false; true | passes (3 guards, lines 942, 943, 945) |
| F1.3o (C) | `j₁`'s exchange on its values (its twin's values); `clashRefusalOf` on `j₁`'s side and its twin's; on `j₂`'s and its twin's; on `t`'s, with no twin | `["a2", "w"]`, `t`'s; `some` of row 16's text, written out, three times | passes (4 guards, lines 949, 951, 955, 959) |
| F1.3o, the other direction | `clashRefusalOf` on F1.3h's values and its twin's (`k2` twice) | `none` | passes (1 guard, line 963) |
| F1.3o | `clashRefusal_some` | proved | passes (line 879) |
| F3.2b | `declaredIn (fullEnv (legacyU muX)) "soft__excepted__may_publish"`; `assemble` on the colliding pack | true; `InvalidInput: generated name soft__excepted__may_publish of pack soft is already declared` | passes (2 guards, lines 1128, 1129) |
| F3.2c | `assemble` on the fresh positive pack; `declaredIn` on `soft__fresh` | `ok [soft] [soft:fresh]`; false | passes (2 guards, lines 1132, 1135) |
| F11.3 | `crossSlot` on an assertion and an attitude candidate | `[x1(h) → p(a), x2(h) → attitudes__wants__1(a)]` | passes (1 guard, line 647) |
| 1.7 | `softContent_formulas` | proved | passes (line 669) |
| 3.2 (new, pc-fid-rev2 R1) | `admitS2Rest_couplings` | proved: main's S2a admission returns `decodeCouplings`' refusal | passes (line 1604) |
| F2.10 (new, R1) | `couplingIds` on form (a), on form (b), on the unlabelled form (c) | `some ["c-rs2", "c-addressee"]`; `some ["c-addressee", "c-force"]`; the error `"CouplingLabelMissing: c-force, rs-file-u1"` | passes (3 guards, lines 1684-1686) |
| F2.10 (new, R1) | `choices` on form (a)'s `Doc`; form (b)'s against it; the sets without couplings | the five choices written out; equal; 27 | passes (3 guards, lines 1708, 1711, 1712) |
| F6.17 (new, R2) | `rd` on the phrase; `rd1` | `.ok [describeTree false, describeTree true]` (the modifier on the last part, then on every part); `many` | passes (2 guards, lines 1739, 1741) |
| F6.17 (new, R2) | `table .must` on each derivation: its readings' sizes; their paraphrases | `[[3], [3]]`; the two paraphrases of 5.6 | passes (2 guards, lines 1743, 1744) |
| F6.17 (new, R2) | `describeD15`, D-15's text from main's `Act.text` | the text of 5.6, written out | passes (1 guard, line 1748) |
| F12.1 (new, R3) | `scenarioGuard "u1" runsResearch dsNorm`; `layerRuleIn profileTableMD []` on the soft chain with readings and `modality@0` | `dsNorm` with guard `["and", crossedFourth, runsResearch]`; `some "UnsupportedProfile: modality@0 with readings@1 is not implemented"` | passes (2 guards, lines 1758, 1761) |
| F2.11 (new, R4(a)) | `opensIn ["crossed", "serves_finding_weaknesses"]` on `limiting`'s guard; on `rationale`'s | `["crossed", "serves_finding_weaknesses"]`; `["crossed"]` | passes (2 guards, lines 1771, 1773) |

**Statements new or revised in pc-fid-rev**, each elaborated by this run: `withAttitudeContents` and
`opensIn_attitude` (3.1, PC-1b); `recordProfile`, `profileTableCM`, `documentLayers'`, `withoutDocumentLayers'`,
`withoutCommitmentsBlock`, `checkDocSets_ignores_commitments` and `CommitmentsBesideJudgments` (3.4, PC-4);
`ReadingsFaithful` and `readingsFaithful` (proved), `StackRuns`, `RewriterFacts`, `PairFacts`, `RouteFacts` with its
generic clause, `stack_evidence` and `stackRuns_all` (1.5, PC-4b); `readingsChosen`, `choiceActs` and
`ActsChoiceFaithful` (3.6, PC-6c); `caseSets`, `caseChoiceLinks`, `setShape` and `ResolveKeepsSets` (3.7, PC-7c);
and the fixtures' `pilotDocList` and `fullGridStacks`. The pc-d2 statements and their guards are unchanged.

**Statements new or revised in the review fixes** (pc-fid-rev's statement review, findings 1 to 3), each elaborated
by this run: `caseManifest`, `effectContent`, `withEffectContent`, `ResolvedEffect` and `PairFacts ("ve.discourse@1",
"scope@0")` (1.5, finding 1); `caseChain`, `readingsChosen` (defined) and `ActsChoiceFaithful` (3.6, finding 2);
`recordProfile` (moved to `VE.Compose`), `documentLayersOf`, `documentLayers'` (derived) and
`checkDocSets_ignores_commitments` (its hypothesis names the moved `recordProfile`) (3.4, finding 3).

**Statements new or revised in the DRI ruling** (2026-10-30, item 1), each elaborated by this run: `SplitReach` (its
effect conjunct, 3.6), and through it `ActsScopeRuns` and `PairFacts ("acts@0", "scope@0")` (1.5), whose text is
unchanged; and section 9's `splitReach_effect` (proved). The conjunct elaborates, so the ruling's fallback is not used.

**Statements new in pc-fid-rev2** (DRI 2026-10-30 pc-fid-rev2, item 1), each elaborated by this run:
`admitS2Rest_couplings` (proved, main's code), `readingsCaseOf` and `compatibleChoices_admitS2` (3.2, PC-2b, R1);
`scenarioGuard` (3.11, PC-12, R3, defined). 3.1's limiting purpose (R4(a)) and 3.6's derivation rule (R2) add no
statement: they are writing rules on statements already elaborated (`judgedIn_soft`, `softContent_formulas`,
`chainReadings_rows`; `ActsChoiceFaithful`), and F2.11 and F6.17 check their fixtures' computable parts on main's
functions (`opensIn`; `VE.Acts.readings`, `read`, `table`, `paraphrase`, `Act.text`). No earlier statement changes.
The review fix (pc-fid-rev2's statement review, finding 1; DRI 2026-10-30 pc-fid-rev2, item 2), elaborated by this
run: `readingsCaseOf_keeps` (new) and `compatibleChoices_admitS2`'s conjunct `cs = VE.Readings.choices a.D` (3.2,
PC-2b, R1); both typed with `sorry` (open point 12).

Earlier rounds' records, kept:

**Round 2's mutants** (on its stub, SHA-256 `ff78b9ff…`, so its line numbers). Round 1 showed on a scratch copy
with F4.9's expected text changed that Lean refuses such a guard: line 474 (`did not evaluate to true`), exit code 1.
Round 2 ran two scratch copies of its stub file, each with one change:
- F1.3o's `j₁` guard expecting `none`. Exit code 1:

  ```
  /tmp/pc-d2-fix2/mutant-expect.lean:852:0: error: Expression
    clashRefusalOf (swapInjectiveOf ["a1", "w"] [("a1", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2"))
        (some (swapInjectiveOf ["a2", "w"] [("a2", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2"))) ==
      none
  did not evaluate to `true`
  ```
- round 1's one-sided check, `clashRefusalOf`'s test `own && twin.getD true` replaced by `own` (the seeded bug of
  the symmetric check). Exit code 1: the proof of `clashRefusal_some` fails on the case of a request with the layer
  whose own exchange is one-to-one and whose twin's is not, and F1.3o's `j₁` guard fails:

  ```
  /tmp/pc-d2-fix2/mutant-onesided.lean:768:33: warning: unused variable `twin`

  Note: This linter can be disabled with `set_option linter.unusedVariables false`
  /tmp/pc-d2-fix2/mutant-onesided.lean:783:88: error: unsolved goals
  case pos.true.false
  j : Json
  h : "judgments@0" ∈ profilesOf j
  ⊢ False
  /tmp/pc-d2-fix2/mutant-onesided.lean:852:0: error: Expression
    clashRefusalOf (swapInjectiveOf ["a1", "w"] [("a1", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2"))
        (some (swapInjectiveOf ["a2", "w"] [("a2", "a1", "a2"), ("w", "a1", "a2")] (swap "a1" "a2"))) ==
      some
        "distinguishing model ids and references do not map one to one between the environments with and without judgments@0"
  did not evaluate to `true`
  ```

  Beside these messages, each copy's output held the same 92 `sorry` warnings as the final run, omitted here.

**Statements new or revised since draft 3's run** (the G3 amendment and pc-d2 edits 2 to 8), each elaborated by
this run: `plainProfiles`, `layerProfiles`, `statedIds`, `statedPairs`, `exchange`, `swapInjectiveOf`,
`swapInjective`, `swap_correct` (restated), `withoutJudgments_ids` and `checkDocSets_judgments_transparent` (with
`hk`), `swapClash`, `clashRefusal`, `checkDocSets_clashFirst`, `swapInjective_twin` and `checkDocSets_swapClash`
(1.7); the planned interface values, `slotAgrees` with `.pack` and the `.outside` list, `plannedSlots` (1.1, 1.2);
`discourseRewriter`, `docRewritersDiscourse`, `DiscourseFaithful`, `DiscoursePreserves`, `DiscourseScopeRuns`,
`DiscourseActsRuns`, the five-entry `RouteFacts` and `LayerFacts` (1.5, 3.7) with S4's names as stubs;
`otherLayer`, `headProfile`, `layerCovers`, `layerRuleIn`, `layerRule`, `documentRefusal` with the layer rule,
`layer_evidence` and `layer_admitted` (3.4); `BaseAdmissibleXV`, `DocumentExpansionXV`, `EntailsXV`,
`acceptanceXV` (with `hfresh`) and `countermodelXV` (1.6); `decisionRule_unsplit` (1.10); `CrossContent`,
`CrossContent.premises`, `crossSlot`, `crossSlot_choice` and `crossSlot_legacy` (3.10).

**Statements new or revised in round 2** (the symmetric check), each elaborated by this run: `clashRefusalOf` and
`clashRefusal_some` (new, proved), `clashRefusal` (symmetric), and `checkDocSets_clashFirst` and
`checkDocSets_swapClash` (restated with the symmetric hypothesis) (1.7). G3 (`checkDocSets_judgments_transparent`)
and `swapInjective_twin` are unchanged.

**Fixtures that are not stubs.** These are examples or tests in the batch that builds them, because their inputs
need the batch's code or a whole document: F1.3b to F1.3o (PC-1's `tests/data` and `ChainExamples.lean`; the guards
above check their texts), F1.11 (PC-1b), F2.6d (PC-2b), F3.1, F3.2 and F3.2b to F3.2d's semantic parts (PK-1's G1b
module), F4.4's and F4.9's end-to-end cases (PC-4's `tests/data`, F4.9 once MD-2 makes `modality@0` owned), F4.15
(PC-4, once CM-2 adds commitments' row), F4.16 (CM-2's tests), F4.17 (whichever of PC-6c and PC-7c merges second),
F5.6 to F5.8 (PC-5b; F5.8 (a) runs on main today), F6.7 (whichever of PC-6 and PC-9 merges second), F6.9 to F6.12
(PC-6's and PC-6b's `SoftExamples.lean`; F6.11 by whichever of PC-6 and AT-3a merges second), F6.15 and F6.16
(PC-6c), F7.1 to F7.5 (PC-7b), F7.8 (PC-7c), F9.3, F9.6 on a run and F9.7 (PC-9's `UniformExamples.lean`), F11.1,
F11.2 and F11.4 (PC-11), and, from pc-fid-rev2, the end-to-end parts of F2.10 and F2.11 (PC-2b, with PC-1) and of
F6.17 (PC-6c), and F12.2 and F12.3 (PC-12, after MD-4a).

**Open points found while applying the rulings.** Round 1 found two. Neither was an edit the ruling made, and
neither changed a ruled statement or a ruled expected value. Round 2's decision resolves the first; the second
stands. Round 2's run adds none. pc-fid-rev adds points 3 to 7; none changes a ruled statement or expected value, and
none needs a ruling. Its review fixes revise points 5 and 6 and add points 8 to 11; point 9 was put to the DRI, whose
decision of 2026-10-30 (item 1) replaces it. pc-fid-rev2 adds points 12 to 15; none changes a signed statement or
expected value, and none needs a ruling. (Line numbers in points 1 to 11 are the ruling's stub's; this run's are 2
higher.) Lean accepted the symmetric
check and every restated statement, and every guard computed the ruled value. So the ruled fallback (G3 with the added hypothesis `¬ swapClash (twin j)`) was not
needed, and there is no Lean message to record.
1. **The amendment's second conjunct and G3. Resolved in round 2 by the symmetric check** (DRI 2026-10-29,
   `manage-agents/reviews/dri-decisions-20261029-pc-d2-r2.md`, item 1). `swapInjective` has two conjuncts, both
   from the signed amendment (synthesis round 2, DECISIONS item 3): the exchange is one-to-one on the stated values,
   and no stated value equals the twin environment's identity (`v₂`) of a different stated value. Let `c` be one
   model content, `a1` and `a2` its identities with and without `judgments@0`, and `w` a third string. Request `j₁`
   (with `judgments@0` and `documents@1`) states `c` twice in one reading set: model A under key `a1`, model B under
   key `w`. Request `j₂` is `j₁` with A under `a2`.
   - `swapInjective j₁` is true (line 940), so G3 applies to `j₁`. Its exchange sends `a1` to `a2` and keeps `w`, so
     its twin `t` states A under `a2` and B under `w` (line 947).
   - `swapInjective t` is false (line 941: `a2`, A's key, equals the twin identity of B's content). `j₂` states the
     same values, so `swapInjective j₂` is false, and `j₂`'s twin keeps them as written: it is `t` as well.

   Round 1's check read only the request. `j₁` passed it, and validation then refused `j₁` for B's key
   (`distinguishing model id does not match model`), which is not a layer refusal. So G3 required `t` to give that
   refusal, while `checkDocSets_swapClash` for `j₂` required `t` to answer `swapClash`. One request cannot answer
   both texts.

   **The resolution.** The DRI ruled the conservative form: refuse, never accept more. The check is symmetric, and
   both conjuncts stay. `j₁` answers `swapClash` because its twin's exchange is not one-to-one (line 949), `j₂`
   because its own is not (line 953), and `t` because its own is not (line 957). On `j₁`, G3's refusal clause then
   holds by its first disjunct, since `t` answers `swapClash` too. The restated `checkDocSets_swapClash` holds on
   `j₁` and on `j₂`. G3 keeps its statement, with no new hypothesis. F1.3o (C) is the fixture (5.1). The symmetric
   check is stated decidably: `clashRefusal` is a `Bool` test of both sides, and `clashRefusal_some` is proved (line
   877). So the ruled fallback is not used.
2. **F6.11 when PC-6 merges before AT-3a.** The at3a-order amendment's condition (d) reads "If AT-3a merges first,
   PC-6 … adds one fixture", and edit 1 says "PC-6 adds condition (d)'s fixture". When PC-6 merges first, the
   fixture's attitude guard node does not exist yet. This draft applies the amendment's shared-file rule: F6.11 is
   PC-6's fixture, built on the rebased `Norms/Wire.lean` by whichever of PC-6 and AT-3a merges second (3.6). The
   confirmation review may rule it otherwise.
3. **Acts beside events stays `p→E`** (the plan's grid, A × E). The pilot document lists `acts@0` and `events@0`.
   By interface (pack × rewrite: the stack's route statement plus G1) the pair composes, but the grid keeps `p→E` for
   an event role on an act (events-time-causation ET-D2, synthesis DEC 11: act performance). No pilot unit puts an
   event role on an act, so F4.17's units hold none. Whether events' row (et-4) refuses `acts@0` is that row batch's.
   It is none of B1 to B6, so the order does not reach it, and it is not changed here.
4. **`stack_evidence`, `stackRuns_all` and the moved `listed_evidence` are typed, not proved.** `stackRuns_all` needs
   PC-4b's one pipeline call in `checkDocSets` and `checkDoc`; `stack_evidence` needs `RouteFacts`' generic clause to
   reduce on a list of three or more, which a proof shows by cases on the list and the stub does not attempt.
5. **`PairFacts`' discourse entries read `discourseRewriter.run`**, while PC-7b's `resolve_then_split` reads
   `resolveDocument`; the discourse × scope entry is PC-4b's since the review fixes, and `resolve_then_govern` is a
   projection of its first conjunct. The link (`resolveCase` is `resolveDocument` on the case's document, under its
   front matter's environment and manifest, `caseManifest`) is S4's and PC-7b's definition; both are stubs here, so
   this run cannot check it. PC-7b's build does.
6. **PC-6c's representation of a split candidate is act phrases'.** `ActsChoiceFaithful` holds whatever act phrases'
   readings elaboration chooses, but that elaboration must give `choiceActs` (`readingsChosen` is defined, from
   `chainDoc`, since the review fixes). Whatever it is,
   scope's per-choice GOVERN (rank 1b, before SUPERPOSE) still reads acts' `SplitMap`: for the triple
   `["acts@0", "scope@0", "readings@1"]`, PC-6c re-proves `PairFacts ("acts@0", "scope@0")` over the elaboration's
   cases before the listing rule lists the triple.
7. **The commitments mode's answer projection.** `CommitmentsBesideJudgments` takes the projection `fields` (the
   mode's answer without its identities) as a parameter. Which identities that answer carries is CM-2's to name.
8. **`ResolvedEffect` asks S4 to resolve the scope block's effects.** PC-4b proves the discourse × scope entry from
   S4's `resolveDocument` only if it resolves each governor's effect at the governor's unit. 3.7 describes
   `resolveDocument` as resolving every content and copying every other byte, and S4 does not name the scope block.
   If S4 copies the block, the clause holds only for effects whose positions mention no reference. Until S4 says
   which, PC-4b cannot prove the entry, so no stack of three or more that holds discourse and scope is listed (the
   conservative direction). `effectContent` and `withEffectContent` are stubs: how an effect's part or condition is
   read as a `Content` is S4's and S1's to fix.
9. **Ruled by the DRI, 2026-10-30** (`manage-agents/reviews/dri-decisions-20261030-pc-fid-rev.md`, item 1):
   `SplitReach`, so `PairFacts ("acts@0", "scope@0")`, keeps each governor's effect as written (3.6; F6.12 and the
   mutant above are the decision's conditions). An effect act phrases' split would have to rewrite (one that names a
   split rule) is not designed here: the pair lemma does not hold on it, so it is refused and never mapped by a guess;
   its owner is act phrases (PC-6b).
10. **`choiceActs` stays act phrases' stub.** `ActsChoiceFaithful`'s per-choice conjunct holds under
    `elaborateMap (choiceActs N.D c) = .ok M`, so it binds only where act phrases' elaboration succeeds. `caseChain` is
    a stub: its tie to what `check` reads of a case is PC-6c's definition.
11. **B2's document mode still has one CM-2 step.** `checkDocSets_ignores_commitments` is vacuous on main and binding
    from CM-2's row on, "which re-proves it with its row" (3.4). The derivation removes the list edit, but not that
    re-proof. The request row to CM-2 should carry it beside `CommitmentsBesideJudgments`.
12. **`compatibleChoices_admitS2` and `readingsCaseOf_keeps` are typed, not proved (R1).** `readingsCaseOf` is a stub:
    which environment and document PC-2b's readings branch hands df-3's enumeration is PC-2b's definition, and
    `readingsCaseOf_keeps` fixes the part of it that matters here: that document's `reading_sets` and `couplings` are
    the front matter's. `admitS2Rest_couplings` is proved on main's code, and it binds PC-2b's rows through both
    statements, which PC-2b proves: `compatibleChoices_admitS2` makes the chain's choices main's `choices` of the
    admitted `Doc`, and `readingsCaseOf_keeps` makes that admission decode the couplings as written, so a definition
    that dropped them would not prove it. One consequence for PC-2b: main's `choices` is cut after `maxChoices + 1`
    (`Readings/Choice.lean:117-118`), while `chainReadings_covers` asks the rows to be every compatible choice, so
    when a case has more than `maxChoices + 1` compatible choices under `xSem`, the three statements leave
    `chainReadings` no `.ok`; that case's whole-document answer is the UNKNOWN that names the limit (point 15), not
    rows. Until PC-2b, F2.10's end-to-end part is PC-2b's test; its decode and choice guards run on main today.
13. **How a candidate carries its derivation is act phrases' (R2).** The rule fixes one derivation per candidate and
    names it by act phrases' index; whether act phrases' readings elaboration reads that label, declares a predicate
    per derivation, or uses AP-4's source is its design (act-phrases SR8, F11). Under AP-3 alone, D-15 refuses the
    phrase's declaration in both forms, since the phrase has two meanings; the per-derivation form is admitted only
    through that elaboration, which is why R2 is staged on it. If it can do none of them, the act is act phrases' GAP
    and F6.17's four act candidates stay pending; no statement here changes. This run also measured,
    while choosing F6.17's words, that main's grammar lists no derivation for a split list whose parts are runs of
    several filler words ("{0} describe test results, safeguards and risk in reports": 0 readings; with single words or
    fixed phrases in the parts: 2), so F6.17 uses fixed phrases, as the pilot's writer did. Why is act phrases'
    (act-phrases 5.2, D9 (i), F13); it is recorded here because a writer meets it, and like R4(b)'s filler it is a
    slot `STUB[act-phrases]` fills, not a composition rule.
14. **The scenario slot's wire and the layer (R3).** `scenarioGuard` fixes the slot's position; how a candidate names
    σ (its name, sort and condition) in the front matter is modality's MD-4a, and `ScenarioUnbound`'s text is modality's
    specification 2.3's, not on main, so row 22 names the code. The slot is reached only once modality's own
    `LayerFacts` covers the chain lists (the layer rule, F12.1's second guard). If modality cannot state that theorem
    for a list whose rules hold its conditions, the layer rule's refusal stands: this plan designs no relaxation.
15. **The re-pilot document's choice count grows (R2, R4(a)).** One candidate per derivation and per purpose reading
    makes ursp.t3_plan's and ursp.t4_plan_moonshot's sets five candidates each; coupled on `rs1` they give 9 joint
    choices instead of 3. By the sets' sizes the document has 360 compatible choices instead of 120, still over the
    enumerated route's 64, so a whole-document readings answer stays UNKNOWN naming the limit (the plan's rule "honest
    UNKNOWN"), never a refusal and never a verdict. The count is Lean's.
