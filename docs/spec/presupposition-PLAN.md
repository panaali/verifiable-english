# Presupposition and definite descriptions (`presupposition@0`): buildable plan

> Status: plan draft 4, 2026-10-14, branch `research/presupposition-p1` (phase 1 ends at `458cc0cb`). Docs only: no
> product code, no test, no generated file, no model call. It applies phase 1's measured results
> ([docs/research/presupposition-phase1.md](../research/presupposition-phase1.md), cited below as Ph1, with its review
> `manage-agents/presupposition-ph1-review.final.md` and fix report `presupposition-ph1-fix.final.md`), and the DRI's
> wave-2 rulings for this plan (`DRI-DECISIONS-PHASE2.md`, "Presupposition (wave 2)": PS-C9, PS-NF, PS-8).
> `manage-agents/debates/plan-synthesis/edits-presupposition.md` does not exist and SYNTHESIS has no presupposition
> row (presupposition is a wave-2 plan), so those three rulings are this plan's cross-plan edits; they are applied as
> ruled. Shared owners, queues and build order are SYNTHESIS's and are not changed here; where phase 1 bears on a
> shared part, it is written in section 11, "Cross-plan issues for the DRI".

## Changes in this draft (draft 4)

- **Phase 1 recorded** (0.1): every pre-registered check with its PASS, FAIL or DEFERRED verdict and what it gates.
- **PS-0p split.** PS-0p keeps what runs now: the ledger, classes D and E, u0286, class B as audit items and the
  step-7 count as a translator field. **PS-0p-r** (u0013, u0095, u0002, u0235) is DEFERRED until the relational-noun
  wordings are admitted (Ph1 F1, F2, 2.5).
- **Bytes.** PS-0p: **+29 B** now (u0286, audit-gated), not +89 B; +145 B with PS-0p-r; stretch +294 B with class B.
  The plan's sentences as written claim 0 B (Ph1 F1–F6 FAIL).
- **No new sort, no premise-scale.** The sort `entity` keeps its name; the pilot declares its English noun as
  "thing"/"things", a document field (Ph1 2.5). Three pilot rules are added; the quoted fallback English is refused.
- **Classes D and E confirmed;** u0055 is a wh-title and goes to the audit instead of being deleted (Ph1 H3).
- **P4** is written in VE's enumerated uniqueness form (Ph1 2.5), not the one-line sentence.
- **PS-6r** (new, split from PS-6): the relational-noun wording rows; it enables PS-0p-r's +116 B.
- **PS-E2** tests the lines PS-6r produces, or labels its items as target wording.
- **PS-3**'s internal order is conditional on the step-7 re-count; Risk 7 is bounded above by 98 occurrences.
- **PS-7 and 1.6 counts** use phase 1's whole-unit census.
- **DRI rulings applied:** PS-C9 (no `presuppositions` mode: the report is a field of the Lean document mode's
  answer, PS-4 absorbs it, PS-2a after lf-16g); PS-NF (`NegatedFactive`'s candidates come from this plan's
  projection); PS-8 DEFERRED until qa-q2 merges.
- **Section 11**, Cross-plan issues for the DRI (new).

> Draft 3's header follows.
>
> Status: plan draft 3, 2026-10-14, branch `design/presupposition` from `main` at `f98183bf`. Design only: no product
> code, no tests, no generated file touched, no model calls. Research: [docs/research/presupposition.md](../research/presupposition.md)
> (cited below as R, with its section numbers). It follows the cross-plan synthesis of the seven wave-1 designs
> (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`, `DRI-DECISIONS-PHASE2.md`): shared owners, queues and landing
> rules are theirs and are cited, not restated. Every number is measured (the method is in R 2.1) or marked
> **estimate**. Every Lean definition and statement is owned by the spec, [presupposition.md](presupposition.md)
> section 4; this plan names files and cites the spec's sections, and holds no Lean declaration of its own.
>
> Draft 3 applies PS-S's statement review of spec draft 1 (`manage-agents/debates/presupposition-spec/`: `fable.md`,
> `astra.md` and the arbiter's `DRI-RULING.md`, verdict FIX; the spec's draft 2 carries the full list, tagged R-D1 to
> R-D6 and R-1 to R-14). The plan-level changes:
> - **In place** is never a reading of its own: at a shallow frame (`not ·`, or the antecedent of a root "if") it is
>   the conditioned reading's alias, by a Lean theorem over the whole unit; elsewhere it is not offered (1.4, 1.5,
>   1.7, 2.2; R-D1, R-D2). An open set needs at least two readings after merging (R-D3).
> - **Headings** get their own position, so P1 to P4 are admitted as the heading's own assumed unit with content
>   exactly `pre` (3, 5.2; R-10). PS-0p's audit rule "exactly the existence, nothing more" becomes a Lean check.
> - **Open sets with a conditioned rule reading** are on the norms chain only, separated under the unspecified
>   completion; coupling compares picks under it (1.6, 7; R-8, R-9).
> - **P12** is a projection fixture only; its coupling is deferred (5.2, PS-3; R-11).
> - **PS-E1** preregisters its mapping, aggregation, ordering, per-item frames and the scoring of option (e) before
>   any model call (PS-E1; R-12, R-D4).
> - **Section 4** cites the spec instead of restating Lean blocks (R-11).
>
> Draft 2's header follows.
>
> Draft 2 applies the converged Fable + Astra review of draft 1 (`manage-agents/debates/design-presupposition/`,
> `fable.md` and `astra.md`, round 3, CONVERGED: build with mandatory corrections, written here as draft 2):
> - **D2-1. W1 binders.** Rule binders come from the regulated predicate's `sorts`, never from `Node.over` (which holds
>   precedence names). The rule theorems quantify over typed tuples of those sorts. Conditioning keeps every rule's
>   name, predicate, sign, carve-outs and precedence (4.4).
> - **D2-2. Carriers at the root.** Asserted is `goal ∧ clause` and conditioned is `goal → clause`, so the first is
>   false and the second says nothing wherever the goal fails, at every frame. Local accommodation is a separate
>   candidate, measured by PS-E1. A conditioned rule is admitted only for an `unspecified` predicate; otherwise
>   `PresuppositionDefault` (1.4, 1.5).
> - **D2-3. Proved premises.** A certificate may use only the units strictly before the obligation's unit and the
>   declared background (4.6). A carrier cannot prove its own presupposition.
> - **D2-4. Rule acts.** No `body` argument; candidates are at most assumed and conditioned (3, 4.6).
> - **D2-5. Coupling.** An optional, proved compression under stated conditions (`coupling_complete`), never imposed
>   because two goals are equal (1.6, 4.7). A closed `pre` shared by several rules can be assumed once, as one
>   explicit, labelled choice.
> - **D2-6. PS-E1.** It measures candidates and wording only. Option (e), "true here", measures local accommodation. A
>   one-reading cell yields exactly one offered rewrite. Results are labelled proxy.
> - **D2-7. One owner of the description formulas.** Discourse's file gets the generalised builders; `uniqueD` and
>   `assertive` become wrappers, equal to today's by `rfl` (4.3).
> - **D2-8. Simultaneous elaboration.** Frames and goals are computed on the unit's carrier-free base content. Several
>   carriers in one unit compose by one operator that puts asserted goals above every condition (1.4, 4.2).
> - **D2-9. Fixtures and order.** New fixtures (5.1: S7d, S12–S21, M3). The five-rule fixture uses identical
>   applicability. The distinct-goal count moves to PS-0p. Batch order is in 6.
>
> PS-S's statement review, with its stubs elaborating, is the bounded re-check of draft 2. Nothing beyond PS-0p starts
> until that review passes. (Draft 3: the first review ruled FIX; the gate is now the ruling's, in PS-S below.)

## 0. Summary

**What gets built.**
- **Trigger rows.** A presupposition trigger ("the operator’s instructions", "Claude’s core values", "stop",
  "recognise that") is a row of a closed table. The row says what the trigger takes for granted (`pre`), and what the
  clause means with it asserted (`strong`) or with the clause silent where it fails (`weak`).
- **Obligations.** Each trigger occurrence in a unit is an obligation. Lean regenerates its position (a one-hole
  *frame* in the unit's carrier-free base content, or a W1 rule's act) and its **projected goal**: Karttunen's
  filtering, read off VE's connectives, quantifiers and W1 guards.
- **Carriers.** Each obligation has exactly one carrier. Asserted and conditioned act at the root of the unit:
  - **proved**: a checked certificate for the goal, from strictly earlier units and declared background. A theorem
    shows the readings then coincide, so there is no choice.
  - **assumed**: an explicit asserted unit whose content is the goal.
  - **conditioned**: the content is `goal → clause`, which says nothing where the goal fails. A rule's guard gains
    `pre`, and where `pre` fails the rule contributes no decision; this is admitted only for an `unspecified`
    predicate.
  - **asserted**: the content is `goal ∧ clause`, which is false where the goal fails. Not for rule acts.
  - **unresolved**: a reading set whose readings are exactly the row's measured candidates at that position, at
    least two after merging, or a question in authoring.
  - Local accommodation (the clause read with the presupposition in place) is measured by PS-E1 but is never a
    reading of its own: at a shallow frame it has the models of conditioned (a Lean theorem) and is that reading's
    alias wording; elsewhere it is not offered in presupposition@0.
  - A trigger in a heading has its own position: the heading's unit is the assumption, with content exactly `pre`.
- **Coupling.** An optional compression: obligations with equal goals and equal candidate lists, in one reading
  alternative, share one choice only when Lean proves that no admissible joint reading is lost. Otherwise they stay
  separate.
- **What readers see.** "Assumed: …", "This applies only where …", or nothing at all when the text already says it.

**What it reuses.**
- discourse@1's description formulas (generalised at their owner) and carrier words;
- P0 certificates; W1's `applies`, `bindAll` and `decides`; W5's flags;
- reading sets and lf-14d's joint choices;
- norm-defaults' `unspecified` predicates.

**What it adds to the trusted core.** Three structural functions (`plug`, `goal` and the root wrapper `carried`), the
projection, collapse and rule theorems, and per-row definedness lemmas.

**First batch that moves a number.** PS-0p is pilot-only. It claims the heading presuppositions that a word triggers
and nothing else blocks. Phase 1 measured what VE English can write today (0.1): **+29 B** (u0286, "Some thing is
unsolved.") now; +145 B (5 units) once the relational-noun wordings land (PS-0p-r, after PS-6r); stretch +294 B (9)
with class B. All are **estimates**, gated by the audit. It also removes 10 recorded heading "presuppositions" that
no word triggers (315 B; u0055, a wh-title, goes to the audit), stops the pilot assuming what the text withholds
(u0254, u0268), and records the distinct projected goals in rule acts (Risk 7), so that PS-3's order is decided on a
count.

| Batch | Kind | Hours | Depends on | Constitution bytes (estimate) | UDHR bytes (estimate) |
|---|---|---|---|---|---|
| PS-0p | pilot, no product code; distinct-goal count | 2–3 | none (DRI merges the prompt, SC2) | **+29** (u0286); stretch +178 with class B | 0 |
| PS-0p-r | pilot, no product code: u0013, u0095, u0002, u0235 | 1 | PS-6r, then the next pilot run (DEFERRED) | +116 (total with PS-0p: +145; stretch +294) | 0 |
| PS-S | draft-2 statements, spec and statement review (the re-check) | 5–6 | none | 0 | 0 |
| PS-1 | Lean core, new files, discourse's generalised builders | 6–7 | PS-S review passed | 0 | 0 |
| PS-E1 | experiment (readers' carriers and wording) | 3 | DRI authorises model calls; finishes before PS-2a | 0 | 0 |
| PS-6r | English: relational-noun wording rows | 2–3 | English queue (slot: 11, X1) | 0 itself; enables PS-0p-r's +116 | 0 |
| PS-E2 | experiment (rendering) | 2 | PS-E1, PS-6r (or items labelled target wording) | 0 | 0 |
| PS-2a | Lean: obligation check and report (no mode, PS-C9) | 4–5 | PS-1, PS-E1, lf-16g | 0 | 0 |
| PS-4 | on the composition stack: the report field and the status rule | 4–5 | PS-2a, AR-10 table, document-mode queue | 0 | 0 |
| PS-2b | Python binding of the field, display, fixtures, fuzz | 3–4 | PS-4 | 0 | 0 |
| PS-3 | Lean: proved coupling of equal goals; source identity | 4–5 | PS-2a, lf-14d; order inside it on the step-7 re-count | 0 | 0 |
| PS-5p | pilot fidelity | 3 | PS-2b; per unit: SC-3b, AP-2/AP-3, PS-7 | 0–72 B READINGS; fidelity 430 B | fidelity 441 B |
| PS-6 | English authoring rows | 5–6 | PS-E1, PS-E2, PS-2a, English queue | 0 (authoring) | 0 |
| PS-7 | change-of-state and iteration rows | 4–5 | PS-1, events ET-3/ET-4 (and ET-D2 for acts) | 0 claimed; enables 36–46 units, 6,887–9,641 B | 0 claimed |
| PS-8 | optional: one carrier vocabulary | 2–3 | DEFERRED (DRI PS-8): reconsider after qa-q2 merges | 0 | 0 |

### 0.1 Phase 1 results (PS-0p, measurement only)

Phase 1 ran PS-0p as a dry run on a scratch copy of the pinned constitution run (`20261012T1800Z`), with no model
call and no product code; the pinned translation's own check reproduced the pinned record byte for byte (Ph1 2.2,
control). Its verdicts, against the bars fixed before any count (Ph1 1.4):

| Check (Ph1) | Bar | Measured | Verdict | What it gates |
|---|---|---|---|---|
| PS-0p bar | the next audit accepts every claimed heading unit | needs the next pilot run and its audit | **DEFERRED** (trigger: the first constitution run after the DRI merges the prompt addition) | every PS-0p and PS-0p-r byte |
| H1, H2 | 29 heading units, 999 B; classes A–E 5/145, 4/149, 7/284, 2/72, 11/349 | identical | PASS | steps 2–5 as written |
| H3 | no trigger word in class E | u0055 "How to treat operators and users" has the wh-word "How" | **FAIL** | step 2 deletes 10, not 11; u0055 goes to the audit |
| H4 | each class D unit withheld, u0269.s02 among the hits | both (u0269.s02; also u0241.s06, not about Claude) | PASS | step 4, PS-5p's u0254 and u0268 |
| H5, H6 | no withholding hit for class A; trigger words in its titles | as expected | PASS | audit additions 1 and 3 by script |
| O1–O9 | source occurrences equal R 2.3's | 5 of 9 equal; O4, O6, O8, O9 differ by named words ("emotional", "remainder", "returned to", "discoveries") | O4, O6, O8, O9 **FAIL** (lexical) | nothing claimed; R 2.3's expressions to be recorded |
| U1–U5 | whole-unit counts at least R's lower bounds; UDHR 0 | 78; 30 / 7,151 B; 46 / 9,641 B; 195; 0 | PASS | step 1; 1.6's and PS-7's counts |
| F1 | the three existence sentences parse, round-trip, are exactly the existence | none parses (each alone: "Unknown English phrase 'entity is'") | **FAIL** | +89 B as written: 0 B |
| F2 | the two uniqueness sentences (open) | none parses | **FAIL** | P4's one-line form; PS-6r's uniqueness sentence |
| F3–F6 | the scratch translation loads; CHECKED +89 B; 8 of 8 conflict-free; probes byte-identical | does not load: the plan's binary wordings turn u0248's "is human" into a fallback | **FAIL** (F4, F5 not measurable) | the prompt addition as draft 3 wrote it must not be merged |
| Exploration (never counted) | — | quoted fallback English: loads, +145 B, 8 of 8, probes byte-identical, witnesses in the existing domain | information | the mechanism works; only the English is missing |
| Post-review (never counted) | — | noun "thing": only display text changes; u0286 as "Some thing is unsolved.": +29 B, 8 of 8, probes identical; every relational-noun wording tried fails the lint; VE's enumerated uniqueness form parses exactly | information | PS-0p now (u0286); PS-0p-r and PS-6r |
| Step 7 | none (a count) | formalised rules: 4 goal keys in one unit (u0156.s03), none equal; unformalised: at most 98 "the user"/"the operator" matches, 2 source-identity choices | reported | PS-3's internal order, after the re-count |
| Step 5 (class B) | claimed only if the audit accepts | needs the audit | **DEFERRED** (trigger: as the bar) | stretch +149 B |
| PS-E1, PS-E2 | 6/40 candidate, 36/40 one-reading, controls 11 of 12 …; 36/40 on 18 of 20 | model calls, not run in phase 1 | **DEFERRED** (triggers: DRI authorises the calls; PS-E2 also PS-6r) | PS-2a's table; PS-6's templates |

Every Rust-backed run used `VE_RUST_TIMEOUT=600` under `prlimit --as=6442450944` (6 GiB), recorded in the evidence;
peak resident sets were under 140 MiB (Ph1 5). At the 5 s default the pinned translation's own check is
CheckerUnavailable, so PS-0p's step 6 cannot run without a raised limit (11, X4).

## 1. The design

### 1.1 Position in the stack

The composition stack's order is RESOLVE (discourse), then scope@0's step 1b, then STRUCTURE, SUPERPOSE, CHAIN and
CHECK (composition-PLAN; scope-PLAN 1.1). `presupposition@0` is a checking wrapper at step **1c**: after discourse and
scope, so that names are resolved and governors' conditions are in the rules' guards, and before the chain.

It **does not rewrite content**. Translators and authors write the carrier's elaboration; Lean regenerates it from
the row, the recorded arguments and the path, and compares. This matches discourse's rule that the recorded targets
are the comparison point, never a filter.

There is no separate service mode (DRI PS-C9). The check's report is a field of the Lean document mode's answer, and
PS-4 adds it there together with the status rule; PS-2a builds only what that field needs, after lf-16g. A document
without the block gets today's answer (`no_block_unchanged`).

### 1.2 Trigger rows

A row has a name, a builder from recorded arguments to a `Reading` (`pre`, `strong`, `weak`), and a definedness
lemma `strong ↔ pre ∧ weak`. The rows of this plan:

| Row | Example | `pre` | `strong` | `weak` | Owner of the parts |
|---|---|---|---|---|---|
| `definite` | "the mission of Anthropic", "the operator" | `U(D) = ∃x (D x ∧ ∀y (D y → y = x))` | discourse's `assertive` | discourse's `presupposed` `∀x (D x → P x)` | discourse (formulas, through its generalised builders, 4.3); this plan (row) |
| `plural` (plural or mass possessive, plural definite) | "Claude’s core values", "the operator’s instructions", "his family" | `∃x D x` | `∃x D x ∧ ∀x (D x → P x)` | `∀x (D x → P x)` | this plan |
| `generic` | a factive's complement; a change of state's earlier state; an iteration's earlier event; a possessive act argument | supplied by the owner | `pre ∧ body` | `pre → body` | attitudes or attribution (factive verbs), events (state wordings), act phrases (arguments) |

The restriction `D` may mention the hole's other variables ("the operator of that situation"). The open versions of
the definite formulas weaken `D` past the second binder with W1's existing instantiation. They are built by
discourse's own generalised builders, in discourse's file, and `uniqueD` and `assertive` become their closed
wrappers, equal to today's bodies by `rfl` (4.3). No second copy of the formulas exists.

### 1.3 Projection: the projected goal

The trigger's position is a one-hole frame `f` over VE's formula constructors. Its projected goal `f.goal pre` is
built as follows:
- **Passes through:** negation, the left side of every connective, and the antecedent of "if".
- **Hypotheses added** for the right side of "and" and of "if" (the left side), and of "or" (the negation of the left
  side).
- **Universal closure** over every binder crossed, "some" included: the presupposition must hold for every witness
  that reaches the hole.

For a trigger in a rule's act, the goal is `∀x̄ (applies N → pre)` (`ruleGoal`, 4.4): the guard and the absence of
carve-outs are the local context. The binders `x̄` are the regulated predicate's argument sorts, in declared order.

**Goals come from the base content.** Every frame and goal is computed on the unit's carrier-free base content: the
content with each trigger's clause in place and no carrier added (for a rule, its guard without the conditions that
carriers add). So a `pre` added by one carrier never filters another obligation, and never proves its own goal.

**Not crossed:**
- reported content ("X says that …") is a plug (attribution owns it);
- the right conjunct does not satisfy the left one ("Her manager is ready, and Alice has exactly one manager" is
  unresolved; PS-E1 measures whether readers agree).

### 1.4 Obligations and carriers

Write `B` for the unit's base content (1.3), `f` for the trigger's frame in `B` and `G = f.goal pre` for its projected
goal.

| Carrier | What the document records | What Lean checks | Unit status (W2, through the document mode after PS-4) |
|---|---|---|---|
| proved | a unit-less asserted deduction node with a certificate (discourse's frozen `proved` form); the unit's content is `B` | `checkCertificate E premises G cert = true`, where `premises` are the units strictly before the obligation's unit and the declared background (W5 flags, literals, definitions); the recorded content equals `B` | as the unit's own content |
| assumed | an asserted unit whose content is `G` (discourse's frozen `assumed` form, generalised); the unit's content is `B` | the unit exists, has kind `asserted`, and its content is the regenerated `G`; the recorded content equals `B` | the assumed unit: CHECKED as an assumption, listed in the residual |
| conditioned | the unit's content is `G → B`; for a rule act, the rule with guard `g ∧ pre` | regenerated content equals the recorded content; for a rule, its predicate is `unspecified`, otherwise `PresuppositionDefault` | as the unit's own content |
| asserted | the unit's content is `G ∧ B`; never for a rule act | regenerated content equals the recorded content | as the unit's own content |
| unresolved | the unit carries an open reading set | its readings are exactly the row's emitted candidates at the position (PS-E1's table, in place excluded), at least two, pairwise separated by Lean-admitted situations | READINGS, or UNFORMALISED; never CHECKED or OPEN on one reading |

**Local accommodation** (the clause read with the presupposition in place: the content is `B` itself, with no goal
and no assumption) is measured by PS-E1 (option (e)) and used only at a shallow frame in a negated or antecedent
cell: `not ·`, or the antecedent of a root "if". There it has the models of the conditioned reading for the whole
unit (`inPlace_iff_conditioned_shallow`), so it is that reading's alias wording, never a reading of its own; a
recorded in-place carrier is admitted there and nowhere else. At every other frame, in place is not offered in
presupposition@0 (spec 1.4, 1.8, 8).

**Headings.** A trigger in a heading ("Claude’s core values") has the position `heading`: no frame and no body,
goal `pre`, carrier proved or assumed, and an assumed heading may name its own unit, whose content must then be
exactly `pre` (spec 1.4a). Elsewhere a unit never assumes itself.

**Several obligations in one unit** compose by one operator (`carried`, 4.2): the goals of asserted obligations
become left conjuncts, then the goals of conditioned obligations become antecedents, then `B`, each group in block
order. One obligation's condition therefore never sits above another's asserted goal. Lean proves the invariants for
the whole unit: it is false wherever an asserted goal fails, and where a conditioned goal fails it says only its
asserted goals. A rule's conditions are added to its guard in block order.

A certificate may come from any untrusted prover (Rust search, an external prover). Lean only checks it. No
certificate means no proved carrier; the obligation then stays unresolved unless another carrier is recorded.

### 1.5 When a presupposition fails

R 4.2 has the full table. In short, where the projected goal fails:
- **assumed:** such a situation is not a model of the premises. If the premises refute the goal, the existing
  inconsistency report shows it, with a `PresuppositionRefuted` line naming the trigger.
- **conditioned:** the sentence says nothing there, at every frame, under negation included
  (`conditioned_vacuous_off_goal`). A rule conditioned on `pre` contributes no decision where `pre` fails. The
  predicate is UNDECIDED there only where no other rule decides, because it is `unspecified` (norm-defaults). For a
  predicate with an allow or deny default, the default would decide where the text says nothing, so a conditioned
  carrier on its rules is refused with `PresuppositionDefault`.
- **asserted:** the sentence is false there, at every frame (`asserted_false_off_goal`).
- **local accommodation** (only at a shallow frame where PS-E1 measures it): the clause as written, with the
  presupposition read in place: true where `pre` fails at a shallow negated frame, possibly false at a nested one.
- **unresolved:** readings@1 verdicts.
- **Questions:** keep speech acts' PRESUPPOSITION-FAILED.

### 1.6 Ambiguity and coupling

- **Candidates come from the words only:** the row and the position class (top, negated, antecedent, consequent,
  rule act, rule guard, under a modal, under an attitude, reported). The table is the one PS-E1 measures. A position
  class with fewer than two emitted candidates admits no reading set: in translation the unit stays UNFORMALISED; in
  authoring the sentence is refused with advice.
- **Rule acts.** A rule's act has no `body` argument, and its candidates are at most assumed and conditioned. An
  unresolved rule obligation whose cell lists conditioned needs an `unspecified` predicate, like a conditioned one
  (`PresuppositionDefault` otherwise).
- **Separation and chains.** An open set with a conditioned rule reading needs `norm-defaults@0`, so it is on the
  norms chain only, and readings-defaults separates its readings under the unspecified completion; on the soft and
  rights chains readings@1's `abstention` refuses it. Without `norm-defaults@0`, readings@1's own separation applies.
- **Coupling is a proved compression, never imposed** (PS-3). Equal goals alone never force one choice. A group of
  obligations shares one choice only when:
  - their goals are equal as formulas, their candidate lists are equal, and they sit in the same reading
    alternative;
  - every candidate is a root carrier (assumed, conditioned, asserted);
  - Lean checks, over the existing constrained joint set, that every admissible mixed choice has an admissible
    uniform representative with the same models, the same `decides` at typed tuples and the same assumptions
    (`coupling_complete`). "The same models" is under the document's semantics: W1's elaboration without a
    norm-defaults block, the unspecified completion with one, never the placeholder `deny`.
  Otherwise the group stays uncoupled. Local-accommodation and unconditional-goal candidates are excluded from goal
  coupling; they couple only through an explicit shared source-choice identity with its own preservation proof. A
  joint set over budget is `ResourceLimit: joint choices`, UNKNOWN.
- **Source identity for a closed `pre`.** When several rules take one closed `pre` for granted ("the user" in five
  rules with different guards gives five different goals, since each `ruleGoal` contains its rule's `applies`),
  assuming `pre` once entails every one of their goals. Lean offers this as one explicit, labelled choice; it is
  never imposed.
- **Weights never select a carrier**, and a translator's narrowing is attributed and labelled (discourse 2.4,
  unchanged).

### 1.7 What the reader sees

- **Proved.** No extra line by default. "Why" shows: "‘the user’s request’ takes for granted that the user made a
  request; the rule's condition says so."
- **Assumed.** In the document's assumptions list: "Assumed (from ‘Claude’s core values’): Claude has at least one
  core value." This is the target wording: VE renders it only once PS-6r admits the relational noun. Today the
  renderer writes the quoted fallback ("… has the recorded relation "core_value_of" to claude"), which is not VE
  English (Ph1 2.3).
- **Conditioned.** The rule rewritten in full with its condition: "Where there is a system prompt, Claude must not
  actively deceive the user about its content." Where the condition fails: "Where there is no system prompt, this
  rule contributes no decision." For a plain claim: "Where Alice has a manager, every manager of Alice is ready."
- **Asserted.** "There is exactly one owner, and that owner is ready."
- **Local accommodation** (only at a shallow frame where PS-E1 measures it). The sentence with the presupposition
  read in place, shown beside the conditioned line as the same reading: "It is not so that both of these are so:
  there is exactly one owner, and that owner is ready."
- **Unresolved.** "Two readings: (1) Assumed: every situation this rule covers has operator instructions. (2) This
  rule applies only where the operator has given instructions." Each reading is followed by a situation where they
  differ, in document terms.
- **Authoring (PS-6).** One question: "‘the operator’s instructions’ takes for granted that the operator gave
  instructions. Is that always so, or does this rule apply only when it is so?" Each answer is shown as a rewritten
  sentence.
- No symbols, ids or arrows appear by default; obligation ids are in the provenance view.

## 2. English

### 2.1 Translation (what the pilots write)

- **Ledger fields.** Each unit gets `presupposition_triggers`, one entry per trigger: `words`, `class` (definite,
  possessive, plural, factive, change-of-state, iterative, wh-title), `pre` (in English) and `carrier` (proved,
  assumed, conditioned, asserted, unresolved, or `none` for a title). When a carrier is unresolved, `other_blockers`
  gains `presupposition`.
- **Heading units.** A heading with a trigger carries its presupposition, as the heading's own unit with content
  exactly `pre` (the `heading` position, 3). A heading without one is a title (scope's SC-3a) and has no
  `presupposed_claim` (PS-0p). A wh-title ("How to treat operators and users") has a trigger and goes to the audit
  (Ph1 H3).
- **Writing `pre` in VE English** (Ph1 2.2, 2.5). The existence sentence needs a sort noun that is not reserved: the
  pilot declares the sort `entity`'s noun as "thing"/"things" (a document field; no new sort), so "Some thing is
  unsolved." parses. The restriction needs an admitted wording: today the wording lint admits no relational-noun
  wording ("{0} is a core value of {1}" and every variant tried fall back to the quoted form), so a `pre` over a
  relational noun waits for PS-6r. Uniqueness is written in VE's enumerated form ("There is a first thing such that
  both of the following hold: (a) …; (b) for every second thing that …, the second thing is the same as the first
  thing."), which parses to exactly `U(D)`; the one-line form is refused. The quoted fallback ("has the recorded
  relation …") is never used to claim a unit: it is not VE English.
- **Vocabulary changes in a pilot run** (Ph1 4). After any change to the declared vocabulary, the run regenerates its
  separating situations (`nd.py all`; their model ids include the environment) and checks that every existing fenced
  unit still parses unchanged (in phase 1, declaring the binary "is a … of" wordings turned u0248's "is human" into a
  fallback and the translation stopped loading).
- **The block.** Once PS-2a lands, the translation document also carries the `presuppositions` block (3), which Lean
  checks. Before that, the ledger fields are the record and the audit checks them.

### 2.2 Authoring (PS-6)

- **Admitted with one reading.** A trigger construction in VE English is admitted with one reading when its
  obligation is proved, by an earlier sentence, a condition, a rule guard or W5 flags. In the same document, "If a
  user makes a request, Claude must answer the user’s request." is one sentence with one reading. Admission needs a
  certified collapse or an explicit rewrite; agreement among readers never admits a sentence by itself.
- **Otherwise refused.** The sentence is refused with `PresuppositionUnresolved: ‘<words>’ takes for granted that
  <pre>.` and offers exactly one rewrite per emitted reading at that position:
  - **assumed:** add the sentence "<goal>." to the document;
  - **conditioned:** "Where <goal>, <sentence>.", or "If <pre>, then <sentence>." for a rule (offered only for an
    `unspecified` predicate). At a shallow frame whose cell lists local accommodation, the sentence with the
    presupposition spelled out in place is shown beside it, as the same reading's other wording;
  - **asserted:** "<goal>, and <sentence>."
  - A one-reading cell offers exactly one rewrite; the original wording is still refused.
- **Rewrite discipline.** Each rewrite has exactly one reading (attitudes' `refused_have_rewrites` pattern). The two
  wordings that bracket a conjunction under "not" and under "if … then" ("both of these are so: …") are fixtures of
  it (spec 7.6).

## 3. Wire form (the `presuppositions` block)

```json
"presuppositions": {
  "version": "presupposition@0",
  "obligations": [
    {"id": "p1", "unit": "u0156.s03", "span": [95180, 95191], "row": "plural",
     "position": {"rule_act": "no-system-prompt-deception"},
     "arguments": {"sort": "entity", "restriction": ["binary", "content_of", ["var", 0], ["var", 1]]},
     "carrier": {"conditioned": {}}},
    {"id": "p2", "unit": "u0013.presupposition", "span": [6120, 6144], "row": "plural",
     "position": {"heading": {}},
     "arguments": {"sort": "entity", "restriction": ["binary", "core_value_of", ["var", 0], ["const", "claude"]]},
     "carrier": {"assumed": {"unit": "u0013.presupposition"}}}
  ]
}
```

- **Position.** `path` is a list of child indices into the unit's base content (1.3); `rule_act` names a W1 rule of
  the unit; `heading` marks the unit as a heading's presupposition (spec 1.4a).
- **Rule acts and headings.** At `rule_act` and at `heading`, `body` is absent: a rule's act is an atom, and a
  heading's unit is `pre` itself, so there is no clause to rebuild. A present `body` is
  `PresuppositionMismatch: <obligation>: body`. In p1 the conditioned carrier is admitted only because the rule's
  predicate is `unspecified` in the document's norm-defaults block.
- **Headings.** p2 is assumed on its own unit, which is admitted only if the unit is asserted and its content is
  exactly `pre`, "Some thing is a core value of Claude." (written once PS-6r admits the wording; Ph1 2.5). An
  obligation at a path or a rule act never assumes its own unit.
- **Formulas.** Formulas are P0 wire formulas over the hole's context with the described entity at index 0.
- **Ids and nulls.** Ids are tokens of the existing grammar. Optional fields are absent, never `null`.
- **Identity.** The block is inside the front matter, so it is identity-bound through `document_id` like discourse's
  block.
- **Python.** Python never reads the block's meaning; it sends it to Lean.

## 4. Lean: files (PS-1 unless marked; every declaration in the spec)

The spec, [presupposition.md](presupposition.md) section 4, owns every Lean definition, body and theorem statement
of this plan, and the stub transcribes them. Draft 2 of this plan restated them here, and they drifted from the spec;
draft 3 replaces each block with a reference (R-11). Each subsection names the file, its batch, what it holds, and
the spec section.

### 4.1 `lean/VE/Presupposition/Frame.lean` (spec 4.2)

- **What.** One-hole frames over VE's formula constructors (`Frame`), `plug`, `binders`, the projected goal `goal`
  (Karttunen 1974, Heim 1983: negation and left sides pass it through; the right side of "and" and "if" gains the
  left side as a hypothesis, the right side of "or" its negation; every binder closes it universally), the
  unconditional closure `close`, the incremental local context `Reach` (Schlenker 2009), `locate` (the regeneration
  step of PS-2a), the position classes and `cls`, and the shallow frames `Frame.shallow` with their `Decidable`
  instance (R-D1).
- **Statements.** `goal_denote`, `plug_congr` (local replacement), `reach_typed`, `plug_wellFormed`,
  `goal_wellFormed`, `close_wellFormed`, `locate_plug`, `Frame.shallowB_iff`.

### 4.2 `lean/VE/Presupposition/Reading.lean` (spec 4.3)

- **What.** `Reading` (`pre`, `strong`, `weak` over the hole's context) and its definedness `DefinedAt`; the root
  carriers `assertedAt`, `conditionedAt` and `inPlaceAt`; the one composition operator `carried` (asserted goals
  above every condition, D2-8) and its inverse shape `peel`.
- **Statements.** `collapse`, `collapse_certified`, `collapse_assumed`; `asserted_false_off_goal`,
  `conditioned_vacuous_off_goal`, `carriers_on_goal`; the whole-unit invariants `carried_denote`, `carried_asserted`,
  `carried_conditioned_off`, `carried_on_goals`, `peel_carried`; and R-D2's `carried_idle` and
  `inPlace_iff_conditioned_shallow`, which make in place at a shallow frame the conditioned reading's alias. No
  equivalence of in place with another candidate is stated at any other frame.

### 4.3 `lean/VE/Discourse/Descriptions.lean` (edited, D2-7) and `lean/VE/Presupposition/Rows.lean` (spec 4.1, 4.4)

Discourse's file is the one owner of the description formulas. PS-1 generalises its builders there; today's
`uniqueD` and `assertive` become wrappers, equal to their current bodies by `rfl`, so every discourse answer (S11) is
byte-identical. The file is listed in `lean/VE/Route/frozen-sources.sha256`, so PS-1 rehashes it.

- **Discourse's file (spec 4.1).** The builders `uniqueAt` and `assertiveAt` write the restriction at each binder;
  `raise1` weakens a restriction past the inner binder through W1's `VE.Norms.inst`; `uniqueOpen` and
  `assertiveOpen` are the open forms; `uniqueD` and `assertive` become their closed wrappers. Statements:
  `raise1_zero`, `uniqueOpen_zero`, `assertiveOpen_zero`.
- **Rows.lean (spec 4.4).** The rows `definite` (discourse's builders), `plural` (existence without uniqueness,
  distributive predication) and `generic` (the owner supplies `pre` and the clause); `buildReading` at a content
  position and `buildPre` at a rule act and a heading, whose errors name the field. Statements: `definite_defined`
  (generalising `VE.Discourse.description_definedness`), `plural_defined`, `generic_defined`.

If `VE.Norms.inst`'s list form cannot express the weakening for every `n`, the statement review adds one
`liftFrom` for `VE.Formula` beside `VE.Norms.inst`, in `Norms/Basic.lean`'s owner's file, as the single owner of
substitution. This plan defines none of its own, and no description formula outside discourse's file.

### 4.4 `lean/VE/Presupposition/Rules.lean` (spec 4.5)

- **What.** The rule goal `ruleGoal` (a trigger in a rule's act: its local context is the rule's applicability, the
  binders are the regulated predicate's sorts in declared order, never `N.over`, D2-1); the conditioned carrier for a
  rule, `conditionNode`; and `conditionRule`, the plan's `replaceNode` pinned, which conditions the named rule in
  place and keeps every rule's name, predicate, sign, carve-outs and precedence.
- **Statements.** `condition_applies`, `conditionRule_shape`, `rule_collapse_decides` (at any valuation where the
  rule's applicability gives the condition, conditioning changes no decision), `rule_collapse_typed` (the same at
  every typed tuple, from the rule goal), `rule_collapse_certified`, `conditioned_contributes_nothing` (where the
  condition fails the conditioned rule selects nothing), `unsaid_iff` (norm-defaults' `value3` gives UNDECIDED for an
  `unspecified` predicate exactly where neither sign decides), `source_identity_entails`.

Admission requires a valid tree: the recorded (conditioned) tree passes W1's `validate`, and so does the base tree
that Lean derives from it by removing the carriers' conditions.

### 4.5 `lean/VE/Presupposition/Agree.lean`: the existing pieces are instances (spec 4.6)

- `discourse_definite_is_row`: discourse@1's definite is the `definite` row on closed restrictions (one builder, no
  copy).
- `data_attribute_proved`: W5 `data@0`'s total and functional flags prove the goal of "the r of c"; the English
  `data@0` already admits is the proved case, needing no reading choice.
- `speech_question_top`: a question's presupposition is an obligation at the empty frame; `SupportedGiven` is the
  assumed carrier and `Supported` the proved one, and their answer texts are unchanged.

### 4.6 `lean/VE/Presupposition/{Wire,Admit,Run}.lean` (PS-2a; spec 4.7)

- **Run.lean (PS-C9).** It builds the report that the Lean document mode's answer carries as a field (PS-4); it
  defines no service mode and no runner of its own.
- **What.** The wire types (`Carrier`, `Candidate`, `Position` with `path`, `ruleAct` and `heading`, `Args`,
  `Obligation`), the candidate table and its shape check (`cellOk`, `tableOk`), the decoded document `PDoc` (with
  `defaults`, whether it carries `norm-defaults@0`), the regenerated obligation `Checked`, the `Report`, the
  readings of an open set (`RReading` with its `aliases`, `claimReading`, `ruleReading`, `emitted`, `aliasesOf`,
  `expectedReadings`), `carrierAllowed`, `restrictionPaths` and `entersRestriction`, and `admit`, the check in five
  steps (spec 4.7) over the decoded W2 document: `ve-document@2`'s units when discourse is present, the Lean document
  mode's decoded units after lf-16g.
- **Statements.** `admit_regenerates`, `admit_goals_from_base`, `admit_rule_goal`, `admit_heading_goal`,
  `admit_outside_restrictions`, `admit_claim_content`, `admit_rule_content`, `admit_proved_sound` (D2-3),
  `admit_assumed_sound` (the assumed unit is the obligation's own only at a heading), `admit_unconditional_sound`,
  `admit_conditioned_rule_unspecified` (conditioned, or unresolved with conditioned in the cell),
  `admit_carrier_candidate` (in the cell, in place only at a shallow frame), `admit_unresolved_readings` (exactly the
  expected readings, at least two), `admit_empty_table`, `admit_inPlace_alias`, `no_silent_accommodation`,
  `one_open_per_unit`, `candidates_ruleAct`, `no_block_unchanged`.
- **Diagnostics.** Spec 5: `PresuppositionUnknownRow`, `PresuppositionPosition`, `PresuppositionMismatch`,
  `PresuppositionCertificate`, `PresuppositionAssumedUnit`, `PresuppositionDefault`, `PresuppositionUnresolved`,
  `PresuppositionCandidates`, and `ResourceLimit: presuppositions` (UNKNOWN, never a rejection). Lean writes the
  text; Python prints it.

### 4.7 `lean/VE/Presupposition/Couple.lean` (PS-3; spec 4.8)

- **What.** Picks (one emitted candidate per unresolved obligation, never in place), groups (equal goals and equal
  cells, root carriers only; forming a group never couples it), the representative `rep`, `Uniform`, `couplable`
  (the check over the existing constrained joint set `J`, lf-14d's enumeration within its budget), `coupledSet`, and
  the semantics of a pick: `formulasUnder`, `treeUnder`, `assumptionsUnder`, `pickedU`, `SatUnder` (W1's elaboration
  without a norm-defaults block, the unspecified completion with one), `PickedWF`, `SameModels`, `SameDecides`. The
  `requires` constraints for the couplable groups go through lf-14d's API; their type is pinned when lf-14d lands.
- **Statements.** `coupling_complete` (no admissible joint reading is lost), `coupled_uniform`, `coupled_subset`,
  and `couplings_spec` once lf-14d lands. The source-identity choice for a closed `pre` is one explicit candidate,
  "assume `pre` once", offered beside the per-rule candidates, with `source_identity_entails` (4.4).

## 5. Fixtures

### 5.1 Synthetic (Lean `example`s on finite structures where `decide` applies, otherwise `#guard`s of the executable functions; the same documents through the service in PS-2b)

| Id | Fixture | Expected |
|---|---|---|
| S1 | "The owner is ready." (top level, `definite`) | unresolved. The regenerated contents are built from discourse's formulas: asserted `U ∧ assertive`, conditioned `U → assertive`. Assumed has the models of asserted. Discourse's ξ models (no owner; two owners) separate conditioned from them |
| S2 | "If Alice has exactly one manager, then her manager is ready." | goal `U → U`; proved by a one-step certificate; `collapse_certified` applies; one reading |
| S3 | "Alice’s manager is not ready." | the goal passes the negation: same goal as S1 |
| S4 | "Alice has no manager, or her manager is ready." (`plural`) | goal `¬¬∃m … → ∃m …`; proved |
| S5 | "Every person who has a manager trusts their manager." vs "Every person trusts their manager." | first: goal proved by the restrictor; second: goal `∀x (person x → ∃m …)` unresolved |
| S6 | W1 rule over `situation`, guard "a user makes a request in that situation", act "answer the user’s request" with `pre` = the guard's atom | `ruleGoal` proved by a syntactic certificate; `rule_collapse_typed`: the conditioned and the original rule decide alike at every typed situation |
| S7 | W1 rule over `situation`, guard ⊤, act "follow the operator’s instructions", predicate `unspecified` | unresolved. Assumed candidate "In every situation, the operator has given at least one instruction."; conditioned candidate: guard gains the atom. In a situation without instructions, assumed has no model; under conditioned the rule contributes no decision, so the predicate is UNDECIDED there when no other rule decides (norm-defaults `unspecified`), and decided when another rule decides (S7b) |
| S7d | S7 with an allow-by-default predicate | the conditioned carrier is refused: `PresuppositionDefault` (the default would decide where the text says nothing) |
| S8 | `resides_in` declared total and functional; "the State wherein that person resides" | `data_attribute_proved`; one reading. Without the flags: unresolved |
| S9 | "Her manager is ready, and Alice has exactly one manager." | unresolved: the right conjunct does not filter (incremental local context); pins the choice PS-E1 tests |
| S10 | "Alice has exactly one manager. Her manager is ready." (two units) | proved from the earlier unit (a premise), one reading |
| S11 | a discourse@1 document with ξ and η (regression) | byte-identical answers |
| S12 | "The owner is not ready." (negated `definite`, shallow frame) | goal `U` passes the negation. Where there is no owner: asserted false, conditioned true (says nothing), local accommodation true ("true here"). Where there is exactly one owner, all three agree (`collapse`). Local accommodation and conditioned agree in every model, so they are one reading: conditioned, with the in-place wording as its alias |
| S13 | "The owner is ready." with two owners, one of them unready | `U` fails: asserted false, conditioned true. Draft 1's local weak reading was false here, which is why carriers act at the root |
| S14 | W1 rule on `answer_required(agent, situation)`, act "answer the user’s request" | `ruleGoal` binds `agent` and `situation` from the predicate's sorts; the conditioned and original rules decide alike at every typed (agent, situation) pair. Mutant M3 takes the binders from `over` (empty): the goal is open, and the fixture fails |
| S15 | two obligations with one goal in two units, carriers assumed and conditioned | the document has the models of the uniform assumed choice (the assumed goal makes the condition idle) |
| S16 | "The owner is ready, or the manager is busy.", asserted on "the owner", conditioned on "the manager" | the unit is `U_owner ∧ (G_manager → B)`. Where neither goal holds it is false; the opposite nesting `G_manager → (U_owner ∧ B)` would be true there |
| S17 | "The owner is ready." with a proved carrier whose certificate cites its own unit, or the later unit "There is exactly one owner." | `PresuppositionCertificate`. With "There is exactly one owner." placed before it: proved |
| S18 | two obligations with one goal and candidates {assumed, conditioned}, plus an existing constraint that excludes both uniform pairs | the two mixed choices are admissible; their uniform representative is not, so `couplable` is false and the group stays uncoupled (two choices, not none) |
| S19 | "the user" in 5 rules with identical guards; then in 5 rules with different guards | identical guards: one goal, a couplable group, 2 joint choices instead of 32. Different guards: 5 goals, uncoupled; the one source-identity choice "assume that there is a user" is offered, labelled, never imposed |
| S20 | a rule act with a `body` argument | `PresuppositionMismatch: <obligation>: body` |
| S21 | "If the shop is open, then the owner is ready." | goal `open(shop) → U`: false where the shop is open and there is no owner, true where the shop is closed (both directions of `goal_denote`) |
| M1 | mutant: `goal` for `orR` without `.not` | S4 no longer proved; `plug_congr`'s proof fails (the seeded Lean bug of PS-1) |
| M2 | mutant: `admit` accepts `proved` without checking the certificate | P-cert fixture (a wrong certificate) is accepted; its test fails (the seeded Lean bug of PS-2a) |
| M3 | mutant: `ruleGoal` binds `N.over` instead of the predicate's sorts | S14 fails |

Draft 3 adds, with their exact models and values in spec 7: S22 (coupling under the unspecified completion), S23
(a heading), S24 (open descriptions: `raise1` is needed), S25 (`not (not ·)`: in place differs from conditioned),
S26 (two triggers in one unit at `not (not ·)`: in place differs from asserted and assumed), S27 (other negated
frames that are not shallow); the admission fixtures A5u-allow, A5u-deny and A18 to A28; and the authoring fixtures
E1 and E2 (the two bracketed paraphrases).

### 5.2 From the pilots (run `20261012T1800Z`; bytes are ledger spans)

| Id | Unit (bytes, status) | Fixture | Expected |
|---|---|---|---|
| P1 | u0013.presupposition (24, U) | "Claude’s core values": a heading obligation (position `heading`), `plural`, restriction `core_value_of(x, claude)`, no body, carrier assumed on its own unit, whose content is exactly `pre`, `∃x core_value_of(x, claude)` (English after PS-6r: "Some thing is a core value of Claude.") | admitted (`admit_heading_goal`, `admit_assumed_sound`); CHECKED as an assumption; "Assumed (from ‘Claude’s core values’): Claude has at least one core value." A unit that says more than `pre` is `PresuppositionAssumedUnit`. The formula round-trips through VE's renderer today (Ph1 2.3); its English waits for PS-6r |
| P2 | u0095.presupposition (36, U) | "Following Anthropic’s guidelines": a heading obligation, `plural`, `guideline_of(x, anthropic)` | as P1. It cannot prove "Anthropic’s guidelines" in u0073.s05, which comes before it: a proved carrier uses only strictly earlier units (D2-3) |
| P3 | u0286.presupposition (29, U) | "Acknowledging open problems": a heading obligation, `generic` (factive with a noun object), `pre` = `∃x open_problem(x)`; `open_problem` worded "{0} is unsolved", sort noun "thing": "Some thing is unsolved." | as P1. Writable today: in phase 1 it loads, CHECKED +29 B, 8 of 8 choices conflict-free, probes byte-identical (Ph1 2.5). Whether "unsolved thing" is exactly what "open problems" presupposes is the audit's question |
| P4 | u0002 (37), u0235 (19) | heading obligations, singular `definite`: `pre` is the uniqueness `U(D)`, "Anthropic has exactly one mission"; "Claude has exactly one nature" | as P1, with the content in VE's enumerated uniqueness form, which parses to exactly `U(D)` (Ph1 2.5). Until PS-6r admits "mission of" and "nature of", UNFORMALISED with the note "waits for the relational-noun wording (PS-6r)" |
| P5 | u0268 (22), u0254 (50) with u0269.s02 | possessive the text withholds | never assumed alone. Optional reading set {assumed: "Claude has wellbeing."; no claim}; claimed only if the audit accepts (PS-5p) |
| P6 | u0156.s03 (100, READINGS) | "its content" as `plural` in the rule's act, after act phrases split the object | candidates {assumed, conditioned}, separated by a situation without a system prompt. With the conditioned carrier (only if the predicate is `unspecified`), "… and, where there is one, about its content". The open set with the conditioned reading is on the norms chain only |
| P7 | u0073.s05 (234, OPEN) | "the system prompt’s instructions", with scope SC-3b's label condition in the guard and the bridging premise "An operator prompt that addresses a case gives at least one instruction for it." in an earlier unit or the background | proved: one reading. Without the bridging premise: unresolved {assumed, conditioned} |
| P8 | u0076.s01 (250, U) | "the operator’s system prompt" under "not", inside "if" | goal at rule level; candidates per PS-E1 (expected: conditioned, asserted, assumed). Assumed contradicts the u0073.s01 case "There’s no operator prompt" once that case is formalised (`PresuppositionRefuted` line). Projection fixture only; no unlock |
| P9 | u0220.s06 (251, U) | "continuing with an ongoing action" (PS-7) | proved within the phrase: one reading |
| P10 | u0168.s01 (96, OPEN) | "remain firm" (PS-7) | unresolved {assumed: "Claude is firm before such arguments", conditioned} unless the hard-constraint context proves it |
| P11 | UDHR u055 (108, READINGS) | "deprived of his nationality", "change his nationality" (`plural` in a prohibition, after act phrases) | candidates {assumed: "Everyone has a nationality.", conditioned}, separated by a stateless person |
| P12 | UDHR u049 (98, READINGS) | "his own", "return to his country", within the existing set (nationality or residence) | projection fixture only; coupling deferred (spec 8): the obligations sit inside another profile's open set, which presupposition@0 cannot address, and a pick cannot express that choice |
| P13 | 14th Amendment (use case L) | as S8 on the use case's own vocabulary | one reading with the flags |

## 6. Batches

**Order (D2-9; draft 4 applies phase 1 and PS-C9).**
1. PS-0p at the next constitution pilot run, once the DRI merges its prompt addition (SC2), alongside PS-S.
2. PS-1 after PS-S's review passes, with PS-E1 alongside once the DRI authorises its model calls. PS-E1 finishes
   before PS-2a.
3. PS-6r in the English queue, at the slot the DRI assigns (11, X1); until then, at the head of PS-6's slot.
   PS-0p-r at the first pilot run after PS-6r merges.
4. PS-E2 after PS-E1 and PS-6r (or with its items labelled target wording, 11, X1).
5. PS-2a after lf-16g; then PS-4 in the document-mode queue (it carries the report field, PS-C9); then PS-2b.
6. PS-3 after lf-14d merges and after PS-0p's step-7 re-count, which orders its two parts (PS-3).
7. PS-5p unit by unit, as each named dependency lands.
8. PS-6 and PS-7 in the English queue.
9. PS-8: DEFERRED (DRI PS-8); reconsidered after qa-q2 merges.

Discourse's generalised builders (PS-1) land before any consumer of them.

### PS-0p. Heading presuppositions in the pilot (pilot, no product code; 2–3 h)

- **Phase 1 (Ph1; 0.1).** Steps 1, 2 and 4 reproduce exactly (H1, H2, H4 PASS), except u0055 (H3 FAIL). Step 3 as
  draft 3 wrote it claims nothing (F1, F2 FAIL), and its check fails (F3–F6 FAIL: the binary wordings broke an
  existing unit). The mechanism passes with VE's fallback English (never counted), and u0286 passes with a clean
  wording (never counted). The bar is DEFERRED. This draft keeps what the data supports and moves the four
  relational units to PS-0p-r.
- **Goal.**
  - Claim the heading presuppositions that a word triggers and that nothing else blocks: today u0286 only.
  - Stop recording claims no word triggers.
  - Stop assuming what the text withholds.
  - Tag triggers as co-blockers.
  - Record the distinct projected goals in rule acts, so that PS-3's order is decided on a count (Risk 7).
- **Depends on.** Nothing in the repository. It is delivered as additions to the DRI-merged pilot prompts
  (`manage-agents/prompts/pilot-additions.txt` and `pilot-audit-additions.txt`; `DRI-DECISIONS-PHASE2.md`, SC2); the
  draft is `docs/research/evidence/presupposition/pilot-prompt-addition.md`. The UDHR has no heading presuppositions
  (Ph1 U5), so it gets no addition. It touches no repository file.
  - **No new sort** (`DRI-DECISIONS-PHASE2.md`, ET1): the new predicates are over the existing sort `entity`, whose
    English noun the pilot declares as "thing"/"things" (a document field, not a sort; Ph1 2.5). It needs no
    premise-scale: existential premises are witnessed by existing elements (Ph1 2.3: one element witnesses all five).
  - **Queue 4.4** (the hard constraints u0164, u0165, u0173) is untouched.
- **Steps.**
  1. **Ledger.** Add `presupposition_triggers` to every unit (2.1). Phase 1's regular-expression census (whole
     units: 78 role-definite units; 30 / 7,151 B possessive over a possibly missing object; 46 / 9,641 B change of
     state; 195 possessive) is a lower bound for some classes (it misses "the system prompt’s instructions") and
     over-matches a few words (O6, O8, O9); the field is the translator's.
  2. **Class E** (10 headings, 315 B). Remove `presupposed_claim` and note "no trigger word: a title (scope
     SC-3a)". The status stays UNFORMALISED; scope claims the titles. **u0055** ("How to treat operators and users",
     34 B) has the wh-word "How": keep it UNFORMALISED, replace its claim with a note, and list it for the audit.
  3. **Class A, u0286 only.** Declare the sort `entity`'s noun "thing"/"things" and `open_problem(entity)` worded
     "{0} is unsolved". The span becomes `kind: asserted`, `support: assumption`, `meaning: specified`, with the fence
     "Some thing is unsolved." (`∃x open_problem(x)`), English round trip, and the ledger fields `carrier: assumed`,
     `trigger: factive`, `trigger_words: Acknowledging`. u0013, u0095, u0002 and u0235 stay UNFORMALISED with the
     note "relational-noun wording not admitted in VE English (PS-6r)" (PS-0p-r). The quoted fallback wording is never
     used to claim a unit.
  4. **Class D** (u0254, u0268). Replace `presupposed_claim` with the note "the text withholds this (u0269.s02): not
     assumed". The status is unchanged.
  5. **Class B** (u0069, u0083, u0245, u0032; 149 B). Offer each to the audit as a separate item, in step 3's form
     (u0032 is OPEN, with `genuine_helpfulness`), only with a wording the lint admits without changing an existing
     one; phase 1 tested none of their wordings. An item whose wording needs a relational noun ("values other than
     helpfulness") waits for PS-6r. Each is claimed only if the audit accepts it.
  6. **Check.** After any vocabulary change, regenerate the separating situations (`nd.py all`) and check that every
     existing fenced unit still parses unchanged. Then `ve document check` on the translation, with the Rust limit
     raised under a memory cap (11, X4): it loads, the reading-set choices stay conflict-free (8 of 8 today), and the
     carried probes are byte-identical. Phase 1 measured this for u0286: +29 B, 8 of 8, probes identical.
  7. **Distinct goals, as a translator field.** For each formalised rule whose act contains "the user", "the
     operator", or a role or pronoun possessive, the translator records the unit, the words, the rule's name, guard and
     carve-outs (`presupposition-goals.json`). The count is of trigger occurrences in rule acts and of the distinct
     goals they project, as `(row, restriction, rule guard and carve-outs)` up to the unit's variable names, for "the
     user" and "the operator" separately, with how many share identical applicability. Phase 1 could not take it from
     the pinned ledger: formalised rules give 4 goal keys in one unit (u0156.s03), none equal; the unformalised units
     give an upper bound of 98 matches, sentence position unknown (Ph1 2.4). This is a count from the ledger, not a
     Lean computation; PS-3 reads it.
- **Audit additions.**
  - For each heading presupposition claimed: the trigger word is in the title.
  - The content is exactly the existence (for a singular description, existence and uniqueness) of what the trigger
    names, and nothing more: no "is desired", "is relevant" or "must". For u0286: "Some thing is unsolved." is
    accepted only if "unsolved thing" is exactly what "open problems" presupposes. Once PS-2a lands, Lean checks the
    formula: the unit is a heading obligation assumed on its own unit, and its content must equal `pre`
    (`admit_heading_goal`, `admit_assumed_sound`; spec fixtures S23, A24, A25). Whether the wording says that formula
    stays the audit's.
  - The source does not withhold it elsewhere: search for "whether" or "uncertain" with the noun.
  - A claim written in the quoted fallback ("has the recorded relation …", "is classified as …") is rejected as not
    VE English.
  - u0055's note.
- **Bar.** The next audit samples every claimed heading unit and accepts each. A rejected unit reverts to
  UNFORMALISED and nothing is claimed for it. **DEFERRED** (Ph1 3): it needs the next pilot run and its audit.
- **Bytes.** **+29 B** (u0286), stretch +178 B with class B. Estimates until audited. UDHR: 0. As draft 3 wrote the
  sentences: 0 B (Ph1 F1, F2).
- **Deleted.** 10 invented `presupposed_claim` fields (u0055's is replaced by a note).
- **Seeded bug.** None: no product code.

### PS-0p-r. The relational heading units (pilot, no product code; 1 h; DEFERRED)

- **Trigger.** PS-6r merges (the lint admits a relational-noun wording for "core value of", "guideline of", "mission
  of" and "nature of" without changing an existing wording); then the next constitution pilot run.
- **Steps.** As PS-0p's step 3, with PS-6r's wordings, the noun "thing" and the constant `anthropic` of sort
  `entity`:
  - **u0013:** `core_value_of(entity, entity)`; `∃x core_value_of(x, claude)`.
  - **u0095:** `guideline_of(entity, entity)`; `∃x guideline_of(x, anthropic)`.
  - **u0002 and u0235:** `mission_of`, `nature_of`; `U(D)` in VE's enumerated uniqueness form, or PS-6r's one-line
    sentence ("Anthropic has exactly one mission.") if it lands.
  Then PS-0p's step 6 check and its audit additions.
- **Evidence it will pass.** With the fallback wording, all five units load, CHECKED +145 B, 8 of 8 conflict-free,
  probes byte-identical, and the formulas round-trip exactly (Ph1 2.3, never counted). Only the English is missing.
- **Bar.** As PS-0p's.
- **Bytes.** +116 B (24 + 36 + 37 + 19), audit-gated; with PS-0p, +145 B, stretch +294 B.

### PS-S. Specification and statement review (planner; 5–6 h)

- **Status (draft 3).** Spec draft 1's review ruled FIX (`manage-agents/debates/presupposition-spec/DRI-RULING.md`).
  Spec draft 2 and this draft 3 apply it. PS-S passes only when, in order: both documents and the stub carry every
  edit of the ruling; the stub elaborates in a checkout whose Lean modules are built (draft 1's
  `unknown module prefix 'VE'` was a missing build, not evidence either way); every `#guard` passes, including S2,
  S4, S5, S9, the open-description fixtures and the fixtures of the ruling's corrections; and both reviewers do a
  bounded re-check of the edited sections. PS-1 starts only after that: R-D2's lemmas are Reading.lean's, so no part
  of PS-1 is released early. Draft 4 (and spec draft 3) change no Lean definition, body or statement: phase 1
  changes the English of P1–P4 and the pilot steps only, so the gate is unchanged.
- **First step.** This draft 2 of the plan.
- **Deliverable.** `docs/spec/presupposition.md`:
  - every Lean definition, body and statement (the spec's section 4 is their one owner; section 4 here cites it);
  - the types left open (`PDoc`, `Args`, `Position`, `Report`, `replaceNode` as `conditionRule`, the coupling types
    over lf-14d's joint set);
  - the wire block (3) and the diagnostics (4.6);
  - the candidate-table format (filled by PS-E1), what PS-E1's preregistration file must fix, and the English
    templates (filled after PS-E2).
- **Stubs.** The spec's statements elaborate in a scratch file, never committed. `lean/` admits no unproved
  theorem, and its audit bans the words for one, even in comments; the stubs state each theorem as a `Prop`-valued
  definition, so they need none. Fixture values are computed by `#guard` on finite models, not by hand.
- **Review.** Sol (standing in for Astra on credits) and Fable converge before PS-1. The review is the bounded
  re-check of draft 2. They check in particular:
  - `goal`'s `exF` case (universal closure over a witness);
  - the incremental versus symmetric choice (S9);
  - discourse's generalised builders and `raise1` through `VE.Norms.inst`;
  - the root carriers and `carried` against S12, S13 and S16;
  - `rule_collapse_typed`'s binders and `conditionRule`'s use of W1's tree;
  - `premisesBefore` against S17;
  - `coupling_complete`'s conditions against S18 and S19;
  - in the re-check after FIX, the edited sections against the fixtures listed in the spec's checklist item 10.
- **Bytes.** 0.

### PS-1. Lean core (6–7 h)

- **New files.** `lean/VE/Presupposition/Frame.lean`, `Reading.lean`, `Rows.lean`, `Rules.lean`, `Agree.lean` and
  `Examples.lean` (S1–S14, S16, S21, S23–S27 and P1–P4, P13 as `example`s or `#guard`s).
- **Statements.** 4.1–4.5 (spec 4.1 to 4.6), all proved, with the standard axiom allowlist unchanged
  (`python3 lean/audit.py`); among them R-D2's `inPlace_iff_conditioned_shallow` and `carried_idle`.
- **Shared files touched.**
  - `lean/VE/Discourse/Descriptions.lean`: the generalised builders, with `uniqueD` and `assertive` as wrappers equal
    to today's bodies by `rfl` (4.3); its hash in `lean/VE/Route/frozen-sources.sha256` is rehashed; S11 shows every
    discourse answer byte-identical. This lands before any consumer.
  - `lean/VE.lean`: one import.
  - `lean/VE/Audit.lean`: the new theorem names, or AR-1's generated manifest if it has merged (append by hand
    before AR-1 lands, regenerate after, never both).
  - `tools/layer_policy.py`: the new directory's layer.
  - `tools/trust-classes.json`: the new files' trust class, and the new definitions in `Descriptions.lean`.
  - Generated inventories (`lean/statements.txt`, `lean/declarations.txt`, `lean/checkers.lock` and any other that
    `tools/regen_generated.py --list` names) are regenerated with `--write`, never edited.
- **Reads, never edits.** `VE/Norms/{Basic,Elaborate,Prefix}.lean`, `VE/NormDefaults/Semantics.lean`,
  `VE/Data/Background.lean`, `VE/SpeechActs/Answer.lean`.
- **Seeded bugs.** M1 (5.1): S4's example and `plug_congr` fail. M3: S14 fails. Restore each.
- **Bytes.** 0.

### PS-E1. Experiment: which carriers do readers take? (3 h; no product code; model calls authorised by the DRI)

- **What it decides (D2-6).** Candidates and wording only. It never admits a sentence: admission needs a certified
  collapse or an explicit rewrite (2.2). Sonnet is a proxy; every result is labelled "proxy, an upper bound for
  careful readers", and none establishes what untrained human readers understand.
- **Pre-registered here, and in a committed file before any model call** (R-12). The file,
  `docs/research/presupposition-E1-prereg.md`, fixes (spec 6): the mapping of the seven trigger classes to the three
  row names; the aggregation rule per cell; the rule for classes of one row that disagree; the ordering rule (share
  highest first, ties in list order); the per-item frame and denotation table computed by the stub; and the
  equivalent-option rule for (e) below. The generator that writes `candidateTable` reads this file, and `tableOk`
  must hold on its output.
- **Items.** 7 trigger classes × 6 position classes × 2 items = 84 items.
  - Trigger classes: singular definite; possessive or plural; role definite in a rule; factive; change of state;
    iteration; heading noun phrase.
  - Position classes: top level; under negation; consequent with an unrelated antecedent; antecedent; rule act;
    rule guard.
  - **Controls:** 12 items where the text supplies the presupposition (the filters of R 4.1).
  - **Suspension:** 6 items with "whether" ("We are uncertain whether X has a manager; X’s manager is …").
  - **Proviso pairs:** 6 items ("If Alice is a diver, she will bring her wetsuit").
  - Total: 108 items.
- **Each item.** A sentence, a situation (where the projected goal fails, or holds for controls), and the question
  "What does the sentence say about this situation?". Options (a) and (b) mean the root carriers (1.4):
  - (a) it is false here: **asserted**. Rule-act items drop (a): a rule's act has no asserted carrier;
  - (b) it says nothing about this situation (for a rule: this rule decides nothing here): **conditioned**;
  - (c) it takes for granted that `pre`, so this situation goes against the text: **assumed**;
  - (d) cannot tell;
  - (e) in the negated and antecedent cells only, it is true here: **local accommodation**.
  - **Scoring (e)** (R-D4). Every negated and antecedent item uses a shallow frame (`not ·`, or the antecedent of a
    root "if"). (b) and (e) count as one class only for an item whose stub `#guard` shows that local accommodation
    and conditioned have the same value in that item's failing situation; otherwise they count apart. "True here" is
    never identified with local accommodation at a compound or nested frame.
- **Protocol.** Sonnet 5.5 as human proxy, 40 fresh trials per item (4,320 calls), as attitudes' E1/E2.
- **Bars, fixed before the run.**
  - A carrier is a **candidate** in a cell iff it gets at least 6/40 on each of the cell's two items.
  - A cell is **one-reading** iff one carrier gets at least 36/40 on both items. The row then lists only that
    carrier there. Authoring still refuses the original wording and offers exactly one rewrite, that carrier's
    (2.2); translation records that carrier as the translator's labelled narrowing.
  - A cell where (d) exceeds 10/40 on either item admits **no** carrier: refused in authoring, UNFORMALISED in
    translation.
  - **Controls:** at least 36/40 choose the answer the proved carrier predicts, on at least 11 of 12 items. If not,
    `collapse`'s English counterpart is in doubt, and PS-6 stops for review (PS-2a's mechanical check still stands).
  - **Suspension:** (c) at most 6/40 on each item. If not, "whether" does not suspend for readers, and class D's
    handling (R 2.2) is reopened.
  - **Proviso:** reported as the share of unconditional-assumption answers. If at least 6/40 on both items, the
    unconditional goal becomes an extra candidate in the consequent cells.
- **Output.** `docs/research/presupposition-E1.md`, and the candidate table that PS-2a and PS-6 read. A cell that
  lists local accommodation must also list conditioned (`cellOk`); local accommodation then licenses only the
  conditioned reading's alias wording, at shallow frames.
- **Bytes.** 0.

### PS-6r. English: relational-noun wording rows (2–3 h; in the English queue; new in draft 4)

- **Why (Ph1 2.2, 2.5).** VE English cannot write "Claude has at least one core value" today. The wording lint
  refuses every relational-noun wording phase 1 tried: "{0} is a core value / guideline / mission / nature of {1}"
  (BINARY_AUXILIARY, BINARY_CONVERSE, LOGICAL_WORD, SYMBOL_COLLISION, and it turns the existing "{0} is human" into a
  fallback), "belongs to / counts among / ranks among the core values of", "serves as a core value for", "is valued
  by", and the owner-first "{0} has core value {1}" (SYMBOL_COLLISION). The "is a N of" shape is admitted only through
  the finite idiom list of english-lean's catalogue (today `ve/english_vocabulary.py`, product code). This is the one
  blocker of PS-0p-r's +116 B.
- **Rows** (english-lean's catalogue; plans add rows only, SYNTHESIS O15):
  - a relational-noun row kind, "{0} is a N of {1}", so that "Some thing is a N of {1}." parses, for the nouns the
    pilots need first (core value, guideline, mission, nature), admitted by the lint without changing any existing
    wording's lint (the `human` collision is a fixture);
  - preferably the one-line uniqueness sentence "{1} has exactly one N." for a relational noun, parsing to exactly
    `U(D)`; until it lands, VE's enumerated form is the English of a uniqueness `pre`.
- **Depends on.** Nothing in this plan: it needs no Lean row, no candidate table and no PS-E1 result. Its slot in the
  English queue is the DRI's (11, X1); until assigned, it is the head of PS-6's slot.
- **Fixtures.** Each new wording parses and round-trips; "Some thing is a core value of Claude." parses to exactly
  `∃x core_value_of(x, claude)`; the enumerated and the one-line uniqueness sentences give the same formula; declaring
  the four wordings beside "{0} is human" leaves its lint unchanged; the quoted fallback is not produced for them.
- **Seeded bug,** in the language of the catalogue file PS-6r edits (Python while the idiom list is in
  `ve/english_vocabulary.py`, Lean once english-lean moves it): the collision check stops treating the new row kind
  as its own, so declaring the four wordings turns "{0} is human" into the fallback again; the collision fixture
  fails. Restore.
- **Bytes.** 0 itself; enables PS-0p-r's +116 B (audit-gated) and the English column of P1, P2 and P4.

### PS-E2. Experiment: the plain-English lines (2 h)

- **Depends on.** PS-E1 and PS-6r (Ph1 4): the assumed lines ("Assumed (from ‘Claude’s core values’): Claude has at
  least one core value.") are not what VE renders today; it writes the quoted fallback. PS-E2 tests the lines PS-6r's
  rows produce. If the DRI keeps PS-6r late (11, X1), PS-E2 runs after PS-E1 with each assumed item labelled "target
  wording, not rendered by VE today", and its assumed items rerun once PS-6r lands.
- **Items.** 20 rendered sentences: 5 each for proved (the "why" line), assumed ("Assumed (from …): …"),
  conditioned ("This applies only where …") and unresolved (two readings with a situation). Each has one question on
  what the document commits to in a named situation.
- **Protocol.** 40 trials each.
- **Bar.** At least 36/40 correct on at least 18/20 items. Otherwise the wording is revised and rerun once; a second
  failure keeps the lines in the provenance view only. **DEFERRED** (model calls; triggers above).
- **Bytes.** 0.

### PS-2a. Lean: obligations, check and report (4–5 h; after lf-16g; no service mode, DRI PS-C9)

- **Depends on.** PS-1; PS-E1 (the candidate table); lf-16g (the Lean document mode). DRI PS-C9: the report is a
  field of the Lean document mode's answer, not a new service mode, and PS-2a is limited to what that field needs.
  So PS-2a adds no `runMode` line, no `MODES` entry, no `presuppositions` schema and no Python relay; `Protocol.lean`
  and `service_schema.py` are not touched.
- **What it builds.** `lean/VE/Presupposition/{Wire,Admit,Run}.lean`: the wire types, `admit` and its statements
  (4.6, spec 4.7), and in `Run.lean` the report value that PS-4 puts in the document mode's answer:
  - one row per obligation, in the block's order: `id`, `unit`, `carrier`; `goal` (the P0 wire formula and its
    English line, rendered by Lean); `outcome` (checked, or the diagnostic); for unresolved obligations, the emitted
    readings' contents, each with its aliases;
  - plus `PresuppositionRefuted` lines from the existing inconsistency report.
- **Statements.** 4.6 (spec 4.7). `Examples.lean` gains the admission fixtures A1–A28 as `#guard`s on `admit`.
- **Shared files touched.** `lean/VE.lean`, `lean/VE/Audit.lean`. Generated: `lean/checkers.lock` and the
  inventories, through `tools/regen_generated.py --write`.
- **Seeded bug.** M2. Restore.
- **Bytes.** 0.

### PS-2b. Python binding of the report field, display, fixtures, fuzz (3–4 h; after PS-4)

- **Binding.** The document relay (the CLAUDE.md recipe's step 5 for the document mode) binds the `presuppositions`
  field of the answer: every obligation id, unit, span and choice it names exists in the request, and no row is
  empty or extra. Anything else is `CheckerUnavailable`. It checks schema and binding only (DRI ruling R8). No
  separate relay module.
- **CLI.** `ve document check` prints Lean's presupposition lines (display only); no new subcommand.
- **Tests.**
  - `tests/test_presuppositions_lean.py`: S1–S27 (S7d included), A1–A28 (A5u-allow and A5u-deny included; A26 and
    A27 on the soft and rights chains), P1–P13 as documents.
  - `tests/test_presuppositions_answer.py`: one-fault and two-fault mutants of the field in genuine document answers
    (each member dropped, emptied, retyped, duplicated or reordered; an index pushed out of range); each mutant is
    `CheckerUnavailable` or changes nothing shown.
  - Genuine cases recorded by `tests/route_case_recorder.py` into `tests/data/route-cases.jsonl` (document mode).
  - Waits use `HANG_TIMEOUT`; tests write only under `tmp_path`.
- **Shared files touched.** The document relay's binding (in the document-mode queue, after PS-4) and
  `tools/layer_policy.py`. `ve/__main__.py` only if `ve document check`'s display needs a line.
- **Seeded bug (Python).** The binding accepts an obligation id that is not in the request. A fuzz test fails.
  Restore.
- **Bytes.** 0.

### PS-3. Proved coupling of equal goals (4–5 h; after `lean-first/b14d` merges)

- **Order inside PS-3 (Ph1 2.4, 4; Risk 7).** Phase 1 could not count the distinct goals in rule acts: in the
  formalised pilot one unit (u0156.s03) has triggers in a rule act and its 4 goal keys are pairwise distinct, so goal
  coupling has nothing to compress there; the unformalised "the user"/"the operator" matches give only an upper bound
  of 98 (descriptive sentences and conditions included), against 2 source-identity choices. PS-0p's step 7 records
  the count as a translator field at the next pilot run. Then:
  - **if** the distinct goals in rule acts exceed the joint budget of 64 without shared applicability, the
    source-identity choice lands first (its own statement, `source_identity_entails`, and its labelled choice), and
    goal coupling (`coupling_complete`) follows as a second step;
  - otherwise the order below stands (coupling, then source identity, in one batch).
  Until the re-count, the priority of PS-3 against other batches is unchanged and its benefit is unmeasured.

- **Goal (D2-5).** An optional, proved compression. A group of obligations (equal goals, equal candidate lists, one
  reading alternative, root carriers only) becomes one choice, through generated `requires` constraints in lf-14d's
  joint-choice API (called, never edited), only when Lean's check over the existing constrained joint set passes:
  every admissible mixed choice has an admissible uniform representative with the same models, the same `decides`
  at typed tuples and the same assumptions (`coupling_complete`). A group that fails the check stays uncoupled.
  Equal goals never impose one choice by themselves.
- **Source identity.** For a closed `pre` taken for granted by several rules, Lean offers one extra, labelled choice,
  "assume `pre` once", which entails each rule's `ruleGoal` (`source_identity_entails`). It is offered, never imposed.
- **New file.** `lean/VE/Presupposition/Couple.lean` (4.7). It touches no shared file beyond `lean/VE.lean` and the
  audit list.
- **Semantics.** Picks are compared under the document's semantics: W1's elaboration without a norm-defaults block,
  the unspecified completion (`IntendedAt3`, each picked document passing `WellFormedU`) with one; never the
  placeholder `deny` (spec 4.8).
- **Fixtures.**
  - P12 (u049): projection fixture only; coupling deferred (spec 8). Its obligations sit inside the nationality or
    residence reading set, another profile's open set, which presupposition@0 cannot address.
  - S22: two picks on an `unspecified` predicate with a gap where no rule decides and the regulated atom is true:
    `SameModels` holds there under the completion.
  - S19: "the user" in 5 rules with identical applicability gives one group and 2 choices, not 2⁵. With different
    guards it gives 5 goals, uncoupled, plus the source-identity choice.
  - S15 (mixed carriers have the models of the uniform choice) and S18 (an external constraint that excludes both
    uniform pairs leaves the group uncoupled).
  - Joint enumeration over 64 is `ResourceLimit: joint choices`, so UNKNOWN (discourse 4.8, unchanged).
- **Bytes.** 0.

### PS-4. On the composition stack (4–5 h; after AR-10's table and lf-16g)

- **Goal.** `presupposition@0` becomes one row in AR-10's profile table, at step 1c. The Lean document mode's answer
  gains the `presuppositions` field, PS-2a's report (DRI PS-C9: PS-4 absorbs the report; there is no separate mode).
  The document mode applies the status rule: a unit with an unresolved obligation is READINGS or UNFORMALISED, never
  CHECKED or OPEN on one reading.
- **The field (CLAUDE.md recipe, steps 2–4, on the document mode's existing route).** The document mode's shape gains
  the field, typed to the leaves; its encoder theorem covers it; its generated schema is regenerated with
  `tools/response_schemas.py --write`. These are the document mode's files, edited in its queue slot.
- **Statements.**
  - The row's composition theorem for every combination it newly admits (with `norms@0`, `norm-defaults@0`,
    `readings@1`, `soft-norms@0`, `scope@0` where landed), as AR-10's rule requires.
  - `no_block_unchanged` for every legacy combination.
  - `status_unresolved_never_single` over the document mode's status function.
- **Shared files touched.**
  - `lean/VE/Compose/Dispatch.lean`: one row of AR-10's table.
  - The Lean document mode file: the status hook and the `presuppositions` field, in the document-mode queue after
    AT-3b, SC-1b, QT-A4, ET-5, WG-4 and ME-10 (SYNTHESIS 4.2). If `ve/document.py` still exists, its display only.
  - The document mode's shape and encoder files under `lean/ResponseShape/`, and `lean/ResponseShape/Audit.lean` if
    a theorem name is added. Generated: the document mode's schema and `lean/checkers.lock`, through
    `tools/regen_generated.py --write`.
  - Python's profile data is generated from AR-10's table.
- **Bytes.** 0.

### PS-5p. Pilot fidelity (pilot; 3 h; per unit, after the named dependency)

| Unit | Fidelity change | Needs |
|---|---|---|
| u0156.s03 | the fused predicate "existence-or-content" goes; the carrier is recorded | act phrases AP-2/AP-3 |
| u0073.s05 | proved through the label condition | scope SC-3b |
| u0168.s01 | "remain" carried | PS-7 |
| UDHR u045a, u049, u055, u064, u077 | existence carriers explicit; packed descriptions such as "the person's country of nationality" go | AP-2/AP-3; u049's carriers are not coupled with its existing set (P12: coupling deferred) |
| u0254, u0268 | the optional reading set {assumed, no claim}, offered to the audit | PS-2b |

- **Bytes.** Constitution: 0–72 B new READINGS (u0254, u0268), audit-gated; fidelity 430 B. UDHR: fidelity 441 B.
  Statuses are otherwise unchanged.
- **Deleted (pilot data).** The fused and packed predicates above.

### PS-6. English authoring rows (5–6 h; in the English queue)

- **Depends on.** PS-E1, PS-E2, PS-2a. The queue on `lean/VE/EnglishGrammar/*`: AP-1's hunk, then AT-5 → QT-A6 →
  ME-11 → QT-B3 → SC-7 (SYNTHESIS 4.1, 4.2); PS-6 comes after SC-7 unless the DRI assigns another slot.
- **Rows.**
  - **Admitted:** definite "the N of t", possessive "t’s N" and "its/their N", plural definite, and factive "knows
    that" (attitudes' row; only the presupposition column is added, DRI PS-NF). The relational nouns these rows
    name use PS-6r's wordings; the existence and uniqueness sentences themselves already parse with a sort noun
    that is not reserved (Ph1 2.5).
  - **Factive under negation (DRI PS-NF).** `NegatedFactive`'s candidates are generated by this plan's projection
    (the factive row's `pre` at a negated frame, through `goal` and the candidate table); attitudes' rows consume
    them and keep their own refusal wording.
  - **Each row carries:** its `pre` template, the candidate list per position class from PS-E1, and the rewrite
    templates of 2.2.
  - **Refusal:** `PresuppositionUnresolved` with rewrites.
  - **Statement:** an instance of attitudes' `refused_have_rewrites`. Each rewrite has exactly one reading, and the
    rewrites' readings are exactly the row's emitted readings, one rewrite per reading, in the row's order; a merged
    reading shows its alias wording beside its rewrite. A one-reading cell gives exactly one rewrite, and the
    original wording is still refused (D2-6). A rule's conditioned rewrite is offered only for an `unspecified`
    predicate.
  - **Fixtures:** E1 and E2 (spec 7.6), the bracketed paraphrases "It is not so that both of these are so: …" and
    "If the shop is open, then both of these are so: …", each with exactly one reading.
- **Shared files touched.** The catalogue files in the queue. The generated fixed tables are regenerated, never
  edited.
- **Seeded bug.** A rewrite list missing one candidate; the `refused_have_rewrites` instance fails.
- **Bytes.** 0 on the pilots; it serves authoring (VE's own documentation and web copy, unmeasured).

### PS-7. Change of state, continuation and iteration (4–5 h; after events ET-3/ET-4, and ET-D2 for acts)

- **Rows** (as `generic` instances over events' state sorts and `begins`/`ends`/"is in progress on"):

  | Trigger | `pre` |
  |---|---|
  | "stops" | in progress before the day |
  | "continues" / "remains" | in progress before and on |
  | "ceases" | as "stops" |
  | "resumes" | an earlier state that ended |
  | "again" | an earlier event of the same sort |
  | "returns to" | an earlier state at the place |
  | "no longer" | in progress before, not on |

- **Ownership.** "Still" is admitted only in the sense senses assigns; "stop … from" is the prevent sense, which
  this row never reads.
- **New file.** `lean/VE/Presupposition/Events.lean`, importing events' module. It edits no events file.
- **English rows.** In the English queue after PS-6.
- **Fixtures.** P9, P10, and UDHR u055's and u067's "change".
- **Bytes.** 0 claimed. It makes 36 to 46 constitution units (6,887 B to 9,641 B) faithfully expressible when their
  primary feature lands (**estimate**). R 2.3's excerpts gave the lower bound; phase 1's whole-unit census gave the
  upper figure (Ph1 U3), whose expression also matches "remainder" and "returned to the orchestrator" (O6, O8).

### PS-8. One carrier vocabulary (optional; 2–3 h; DEFERRED)

- **Status (DRI PS-8).** Not adopted now; reconsidered after qa-q2 merges. The trigger is qa-q2's merge; nothing
  below starts before the DRI reconsiders it.

- **Goal.** Discourse's `PresuppositionCarrier` and `presuppositionLine`, and speech acts' presupposition answer
  kinds, map into `Carrier`.
- **Statements.** Agreement theorems in `lean/VE/Presupposition/Agree.lean` (new code only).
- **Frozen texts.** They stay byte-identical. Discourse's and speech acts' files are not edited until their owners
  agree.
- **After.** qa-q2 has merged.
- **Bytes.** 0.

## 7. Dependencies and merge-conflict map

| In-flight or planned item | Branch / worktree | Needed by | How conflicts are avoided |
|---|---|---|---|
| Lean document mode | lf-16e, lf-16f, lf-16g (`ve-lf-16e`, …) | PS-2a, PS-4, PS-2b | DRI PS-C9: the report is a field of the document mode's answer, no new mode. PS-2a (new files only) after lf-16g; PS-4 (the field and the status rule) in the document-mode queue after ME-10; PS-2b's binding after PS-4 |
| Coupled reading sets in Lean | lf-14d (`lean-first/b14d`, `ve-lf-14d`) | PS-3 | called, never edited; PS-3 after it merges |
| Readings under norm-defaults | readings-defaults (merged: `lean/VE/Readings/Unspecified.lean`, `UnspecifiedWire.lean`; `abstention` in `lean/VE/Readings/Wire.lean`) | PS-2a (separation of open sets with a conditioned rule reading), PS-3 (`SatUnder` reads norm-defaults' `IntendedAt3` and `WellFormedU`) | called, never edited: `separates (fillDoc N)` with `fillHolds` for separation under the completion; on the soft and rights chains `abstention` refuses such sets before PS-2a's check |
| Protocol and schema registry | in-flight editors lf-16e, qa-q2 (`ve-qa-q2`), lf-14d; then the protocol queue | none (DRI PS-C9) | no dispatch line and no `MODES` entry: this plan adds no mode |
| Profile-gate table | AR-10 | PS-4 | one row with its composition proof; the table lands first |
| Generated audit manifests | AR-1 (`arch-20261010-1`) | PS-1 onwards | append by hand before AR-1, regenerate after |
| English catalogue queue | AP-1 hunk, AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7 | PS-6r, PS-6, PS-7 | PS-6r at the slot the DRI assigns (11, X1), otherwise at the head of PS-6's; PS-6 and PS-7 last, one batch at a time |
| Attitudes: "knows", `NegatedFactive` rows | AT-1, AT-5 (`design/attitudes`) | PS-6 factive row | DRI PS-NF: `NegatedFactive`'s candidates are generated by this plan's projection; attitudes' rows consume them; PS-6 adds only the presupposition column to attitudes' rows; no attitudes file edited |
| Events: state sorts, act-performance bridge | ET-3, ET-4, ET-D2 (`design/events-time-causation`) | PS-7 | new file importing events; no events file edited |
| Act phrases: argument structure | AP-2, AP-3 (`design/act-phrases`) | PS-5p (u0156.s03, UDHR possessives) | pilot use only |
| Scope: titles, label conditions | SC-3a, SC-3b (`design/scope`) | PS-0p (titles are scope's), PS-5p (u0073.s05) | pilot use only; no shared file |
| Quantities | QT-0p (u0042.presupposition), the superlative in u0027 | PS-0p | both excluded from PS-0p |
| Hard-constraint queue 4.4 | AT-0p → SC-1b → SC-2 → AT-6a/b → WG-5 | none | PS-0p touches no unit of u0164, u0165 or u0173 |
| Premise scale | infra/oom-rootcause, then premise-scale (`ve-premise-scale`) | none | PS-0p and PS-0p-r add no sort (DRI ET1); the sort `entity`'s noun is a document field, and existence premises are witnessed in the existing domain (Ph1 2.3, 2.5) |
| Discourse | merged; scope SC-3a moves anchor bodies out of `Access.lean`/`WellFormed.lean` | PS-1 edits `Descriptions.lean` (D2-7) | only `Descriptions.lean`, which SC-3a does not touch: generalised builders added, `uniqueD`/`assertive` kept as `rfl` wrappers, frozen hash rehashed; no other discourse file edited |
| Premise packs | PK-1 after `rd-9-int` (`ve-rd-9-int`) | none | assumed carriers are document units, not packs; `Layered.lean` untouched |
| Question answering | qa-q2 (`ve-qa-q2`) | PS-8 (DEFERRED) | DRI PS-8: reconsidered after qa-q2 merges; no speech-acts file edited |
| Composition S4, "discourse on the chain" | not in flight, not scheduled | none | the block carries each obligation's own restriction, so documents with norms need no discourse manifest; discourse mentions are read where present |
| Wave 2 siblings | judgment-terms, defeasible (`design/*`) | none | `pre` may contain open terms (judgment-terms' records); "normally"/"by default" are defeasible's |

**Every shared file a batch touches:**
- `lean/VE.lean` and `lean/VE/Audit.lean`: PS-1, PS-2a, PS-3, PS-7.
- `lean/VE/Discourse/Descriptions.lean` and `lean/VE/Route/frozen-sources.sha256`: PS-1.
- `tools/layer_policy.py`: PS-1, PS-2b. `tools/trust-classes.json`: PS-1.
- `lean/VE/Compose/Dispatch.lean`, the Lean document mode file, its `lean/ResponseShape/` shape and encoder files
  and `lean/ResponseShape/Audit.lean`: PS-4.
- The document relay's binding; `ve/__main__.py` only if the display needs it: PS-2b.
- english-lean's catalogue files (`lean/VE/EnglishGrammar/*`; the idiom list in `ve/english_vocabulary.py` while it
  is there): PS-6r, PS-6, PS-7.
- None: `lean/VE/Service/Protocol.lean` and `ve/backends/service_schema.py` (DRI PS-C9).

**Generated, never hand-edited or hand-merged:** the document mode's service schema, `lean/checkers.lock`,
`lean/statements.txt`, `lean/declarations.txt`, Python's profile data from AR-10's table, and the route cases (through the recorder).
`tools/regen_generated.py --write` regenerates them; `--resolve` finishes merges whose only conflicts are generated.

**The full gate** runs once, on each batch's committed final HEAD.

## 8. One owner per piece of logic

| Logic | Owner | This plan's use |
|---|---|---|
| Description formulas (closed and open: the generalised builders), `description_definedness`, the proved/assumed frozen forms | discourse@1 | the `definite` row calls discourse's builders; `uniqueD`/`assertive` are their closed wrappers; `definite_defined` generalises the lemma without copying the formulas |
| Certificates | P0's tableau checker | the proved carrier |
| Rule applicability, binding | W1 `applies`, `bindAll`, `decides`; binders from the regulated predicate's `sorts` | the rule frame |
| Substitution on `VE.Formula` | W1 `VE.Norms.inst` | `raise1` (in discourse's file); any missing lift is added there (4.3) |
| Attribute flags | W5 `data@0` | proved by declaration |
| UNDECIDED where no rule decides | norm-defaults `unspecified` (`value3`) | a conditioned rule contributes no decision where `pre` fails; admitted only for `unspecified` predicates |
| Reading sets, separating situations | readings@1 | unresolved |
| Separation under the unspecified completion; readings content beside `norm-defaults@0` off the norms chain | readings-defaults (`separates (fillDoc N)`, `fillHolds`, `SeparatedU`); readings@1's `abstention` | open sets with a conditioned rule reading |
| The unspecified completion's models and checks | norm-defaults (`IntendedAt3`, `WellFormedU`) | coupling's `SatUnder` with a norm-defaults block |
| Joint choices | lf-14d | coupling |
| Question presuppositions | speech acts | an empty frame (`speech_question_top`) |
| Knowing, thinking, their refusal rows | attitudes | the factive row's attitude part; `NegatedFactive`'s candidates come from this plan's projection (DRI PS-NF) |
| Report verbs, plugs | attribution | reported positions are blocked |
| State sorts, "in progress" | events | PS-7's `pre` |
| Act arguments | act phrases | possessive arguments become visible |
| Titles, label and heading conditions | scope | untriggered headings; label conditions as local context |
| Source-word rows and refusals; the wording lint and its idiom list | english-lean's catalogue | trigger rows are catalogue rows; PS-6r adds the relational-noun rows there |
| Profile registration, mode registry | AR-10 | one row; no mode line (DRI PS-C9) |
| Statuses; the answer's fields | the Lean document mode | the status rule; the `presuppositions` field (DRI PS-C9) |
| **Frames, projected goals, `plug_congr`, `collapse`, trigger-row readings, root carriers and `carried`, obligation checks, the coupling check, the presupposition lines** | **this plan** (new) | — |

**What is deleted or not duplicated:**
- **Product code.** No general presupposition logic exists, so nothing is deleted. Discourse's three formulas are
  imported, not copied; their open forms are generalised in discourse's own file, never restated here. PS-8
  (DEFERRED, DRI PS-8) would turn discourse's carrier type and line into thin agreements with the shared ones,
  keeping the frozen texts.
- **Pilot data.**
  - 10 untriggered `presupposed_claim` fields, and u0055's claim replaced by a note (PS-0p);
  - u0156.s03's "existence-or-content" (PS-5p);
  - packed existence assumptions in UDHR predicate descriptions (PS-5p).
- **Not duplicated.** Attitudes keeps its `NegatedFactive` rows, events its "missing fact" report, speech acts their
  answer kinds. Each is an instance of the shared pieces below, proved to agree, never re-implemented.

## 9. Risks and questions for the review

1. **The translation boundary.** Lean cannot see a trigger in free English. In translation, the presence of a
   trigger and its row are the translator's claim, checked by the audit (PS-0p's audit lines), as scope accepts for
   reaches. For a trigger in a rule's act, the link between the restriction and the act is also the translator's
   claim: the act is an atom, so Lean sees the restriction but not how the act uses it (D2-4). Lean checks
   everything after that: position, goal, carrier, candidates, coupling.
2. **Incremental local contexts.** S9 ("Her manager is ready, and Alice has exactly one manager") stays unresolved.
   If PS-E1 shows readers accept the right-to-left satisfaction, the symmetric local context becomes an extra
   *candidate*, never a silent filter.
3. **CHECKED as an assumption.** PS-0p's units are CHECKED under W2's rule for assumptions, and listed in the
   residual (phase 1: 19 assumptions become 20 with u0286, 24 with PS-0p-r). NORTH-STAR already says "CHECKED
   includes admitted assumptions, not proof of their truth". The audit decides each unit.
4. **Factive verbs other than "know".** Does "recognise"/"acknowledge"/"be aware" belong to attitudes (a new
   attitude word) or attribution (a report verb with a factive flag)? This plan needs only the complement as `pre`.
5. **A mode or a field.** Ruled (DRI PS-C9): a field of the Lean document mode's answer; PS-4 absorbs it.
6. **NORTH-STAR row 12.** Its "0–999 B" should be corrected per R 2.2 and phase 1: **at most 29 B direct today**
   (u0286, audit-gated), 145 B direct once PS-6r lands, 294 B stretch, 72 B as reading sets, 284 B co-blocked, 315 B
   not presuppositions at all (u0055's 34 B is a wh-title, for the audit). The DRI applies it at the next NORTH-STAR
   update (11, X5).
7. **Cost of coupling.** If distinct goals exceed the joint budget, verdicts are UNKNOWN, which is honest. Phase 1
   bounds the count above by 98 occurrences and could not take it exactly (Ph1 2.4); PS-0p's step 7 records it at
   the next pilot run, and PS-3's internal order follows it. Rules with different guards have different goals, so
   only identical applicability or the source-identity choice reduces the count. Still open.
8. **The English wording lint** (Ph1 2.2, 2.5). The lint refuses every relational-noun wording tried, and declaring
   one wording can change another's lint (the `human` collision). A pilot that adds wordings must check every
   existing unit still parses (PS-0p step 6); PS-6r's fixtures pin the collision. Until PS-6r, +116 B wait on
   English alone.

## 10. Shared pieces

Abstractions several topics could share. The cross-plan review may move them.

| Shared piece | Who would use it | Proposal |
|---|---|---|
| **Local contexts and projected goals** (`Frame`, `goal`, `Reach`, `plug_congr`) | presupposition; attitudes (`NegatedFactive`'s two candidates are a factive's projection under negation); scope (a governor's condition inserted into a guard is a filter, and can prove a presupposition: u0073.s05); events (the "missing fact where a wording needed it" is an obligation with an events `pre`); math-evidence ("the limit of", "the unique x such that": definedness obligations whose certificates may come from untrusted provers); quantities ("exactly three", superlatives take existence for granted); speech acts (`H(q)` at the empty frame) | one module, `VE.Presupposition.Frame`, owned here |
| **One carrier vocabulary**: proved, assumed, conditioned, asserted, unresolved; refuted as a report line | discourse 4.5, speech acts 4.5, W5, events' missing facts, attitudes' refusals, math-evidence's proof obligations | `VE.Presupposition.Carrier`, with discourse's words; agreement lemmas, frozen texts unchanged (PS-8) |
| **Trigger rows with per-position candidates and rewrites** | attitudes (AT-5), events (ET-5's wordings), act phrases, quantities (QT-A6) | a row kind `presupposition` in english-lean's catalogue: trigger, `pre` template, candidates per position class, rewrite templates; one rewrite generator (attitudes' `refused_have_rewrites` pattern) |
| **Collapse by proof**: readings that a certificate shows to agree are one reading, reported once | scope (deictic reaches that coincide), act phrases (attachments that coincide), quantities (roundings that coincide on the data), readings@1 generally | a generic lemma beside `collapse`: readings equal under certified premises are merged before a reading set is formed |
| **Coupling by identical content** | presupposition (same goal), scope (one set per governor), discourse (same target), rights (limitation scope) | lf-14d's joint choices with generated `requires` constraints, only where a preservation check over the existing joint set passes (`coupling_complete`'s pattern); otherwise the occurrences stay separate |
| **Existence facts are validated, never assumed** | events, presupposition, quantities (domain sizes), premise-scale | one obligation record and one "missing fact" line |
| **Plain-English assumption and condition lines** ("Assumed (from …): …", "This applies only where …") | presupposition, scope's provenance sentences, discourse's reviewed presentation, weighing's decision records | one wording table in Lean (the catalogue), one display format in Python |
| **Headings: title or presupposition** | scope (titles), presupposition (triggered claims), both pilots | one rule: a heading with a trigger (a wh-word included) carries its presupposition; without one it is a title; the pilot prompt states it once (PS-0p) |

## 11. Cross-plan issues for the DRI

Phase 1 bears on these shared parts. This draft does not change them; each is written here for the DRI, with a
recommendation. Until ruled, the plan follows the shared part as it stands (noted per item).

- **X1. The slot of PS-6r, the relational-noun wordings** (SYNTHESIS O15, 4.1, 4.2). PS-0p-r's +116 B and PS-E2's
  assumed items wait only on these wordings (Ph1 2.3, 2.5). The English queue puts this plan's English after SC-7,
  and the wording lint and its idiom list are english-lean's. Options: (a) PS-6r at the head of PS-6's slot, after
  SC-7 (the plan's default until ruled; PS-E2 then runs with target-wording labels); (b) PS-6r in an earlier slot of
  the English queue, owned by this plan, adding rows only (O15); (c) an english-lean catalogue item owns the
  relational-noun row kind, as AP3 gave english-lean the base-predicate verbalisations. **Recommendation: (b)**, as
  phase 1 does (Ph1 4, PS-6): it is small, needs no Lean row and no PS-E1 result, and unblocks a measured +116 B and
  PS-E2.
- **X2. The constitution pilot's noun for the sort `entity`** (SC2, the merged prompt). The pinned run declares it as
  "entity", a reserved word, so VE falls back to `entity of sort "entity"`; declaring "thing"/"things" changes only
  VE's own rendered text in that pilot (no status, choice or probe moves; Ph1 2.5). The declaration is shared by
  every plan's pilot additions. **Recommendation:** the DRI puts it once in the merged prompt for all plans.
  Presupposition's own prompt addition carries it until then.
- **X3. Vocabulary changes in pilot runs** (SC2; AP3). Any added predicate, constant or wording invalidates the
  recorded separating situations (their model ids include the environment), and an added wording can change an
  existing wording's lint (Ph1 2.2, 2.3: u0248's "is human" stopped parsing). Every plan's pilot additions declare
  vocabulary. **Recommendation:** one rule in the merged prompt for all plans: after any vocabulary change, run the
  situation step (`nd.py all`) and check that every existing fenced unit still parses unchanged.
- **X4. The Rust time limit in pilot checks** (ME1 and the DRI's 2026-10-14 note). ME1 lets pilots raise
  `VE_RUST_TIMEOUT` and say so; the 2026-10-14 note forbids the raised limit in pilot checks after the Rust process
  grew to 70 GB. At the 5 s default the pinned translation's own check is CheckerUnavailable, so PS-0p's step 6
  cannot run. Phase 1 ran every check at 600 s under `prlimit --as=6442450944` (inherited by the Rust child), recorded
  the cap and the peak child resident set (under 140 MiB) in its evidence, and nothing failed (Ph1 5).
  **Recommendation:** allow the raised limit in pilot checks only under a recorded address-space cap, until ME1's
  measured limit lands. Until ruled, PS-0p's step 6 is run as phase 1 ran it and says so.
- **X5. NORTH-STAR row 12** (the DRI applies NORTH-STAR updates). Phase 1 changes the direct figure: at most 29 B
  today (u0286, audit-gated), 145 B after PS-6r, 294 B stretch; 315 B, not 349 B, are not presuppositions at all
  (Risk 6).
- **X6. The document-mode queue after PS-C9** (SYNTHESIS 4.2). The ruling moves the report into the document mode's
  answer. PS-2a adds new files only (after lf-16g); PS-4 (the field and the status rule) keeps its slot after ME-10;
  PS-2b's binding of the field edits the document relay, so it joins the same queue after PS-4. The queue's listing
  names neither. **Recommendation:** add PS-4 then PS-2b after ME-10 to the queue.
- **X7. Model calls for PS-E1 and PS-E2.** Still unauthorised (4,320 and 800 Sonnet 5.5 proxy calls); AT1 authorised
  attitudes' experiments only. PS-E1 gates PS-2a; PS-E2 gates PS-6. The DRI decides when.
