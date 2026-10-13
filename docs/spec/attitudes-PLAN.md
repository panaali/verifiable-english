# Typed attitudes as conditions of norms (`attitudes@0`): buildable plan

> **Status.** Draft 5, 2026-10-13, branch `research/attitudes-p1`. Draft 5 applies phase 1 (pilots and
> pre-registered experiments, [docs/research/attitudes-phase1.md](../research/attitudes-phase1.md), cited as
> **P1 n** for its section n; its review `manage-agents/attitudes-p1-review.final.md`, FIX, applied in
> `8538355c`–`0f07bb4c`). Phase 1's six gaps in the pre-registration are cited as **G1–G6**. Drafts 1 to 4
> were written on branch `design/attitudes` (draft 4: 2026-10-13). Draft 1 (2026-10-12, at `49de179e`) was debated by
> Fable and Astra (`manage-agents/debates/design-attitudes/`, converged REVISE after round 3) and revised by the
> DRI's cross-plan synthesis of 2026-10-13 (`manage-agents/debates/plan-synthesis/SYNTHESIS.md`). Draft 2 made
> exactly those edits and no others; the debate's items are cited as **A1–A6** (Astra) and **F3–F7** (Fable), the
> synthesis's as **edit 1–10**. Draft 2 went straight to AT-0's statement review, which converged after round 3 on
> **FIX; the build may not start** (`manage-agents/debates/attitudes-spec/`). Draft 3 makes that review's
> corrections, cited as **SR-1 to SR-8** (listed in the spec's section 14), and no other change. The re-check of
> spec draft 2 (`manage-agents/attitudes-p3ver1.final.md`) returned FAIL on three problems; draft 4 and spec draft 3
> make its corrections, cited as **RC-1 to RC-4** (listed in the spec's section 15), and no other change. RC-4 adds
> one batch, AT-1w, so that the `wants` test has one owner at every merge.
> Research and measurements: [docs/research/attitudes.md](../research/attitudes.md) (cited as **R n**). Docs only:
> nothing here is built, proved or measured unless it says so. The Lean blocks are obligations, not proofs; their
> elaborated text is AT-0's statement spec [docs/spec/attitudes.md](attitudes.md), which governs where the two
> differ. Where a block names an existing declaration, the name was read on `main` at `49de179e`. Every byte figure
> is either measured from the pinned pilot ledgers (R 2) or marked **estimate**. No model calls were made.
>
> **Gate before any build.** AT-0's statement review must PASS (two planning reviewers converged; under the
> 2026-10-09 model split, Astra and Opus, with Fable arbitrating an item that does not converge). Elaborating a
> statement is not evidence that it holds: the review also runs a small-scope counterexample search (AT-0), and only
> AT-1's proofs establish the statements. The build starts only by DRI decision, after the dependencies of section 5
> land (research wave rule `STOP_BEFORE_BUILD=1`).

**Changes in this draft (draft 5, from phase 1).** No batch is cancelled and none is added; no Lean statement
changes; the cross-plan edits (edit 1–10) and the synthesis's owners, shared items and build order are unchanged.

1. **AT-0p measured: PASS on A1–A7** (P1 2). Its estimates are now measured values: 2,951 claimed bytes unchanged,
   open terms 33 → 46, the seven audit-case points UNDECIDED → SETTLED no. A8 (the next audit's verdict on the seven
   units) and AT-0p's landing in the pilot are **DEFERRED**, with their triggers (section 9). Sections 0, 1, 2
   (D-A10), 3.8, 4 (AT-0p), 5 and 6 updated. Section 3.8 now names the count `MAX_PREDICATES` bounds, declared
   plus unspecified ("filled"): 65 at the pinned run, 78 in AT-0p, **about** 85 with the intention terms (drafts
   1–4's 68 and about 88 were the readings route's size count, three higher).
2. **E1 and E2: DEFERRED** (no model calls in phase 1); items, seeded orders and scorers are ready (P1 3). Their
   trigger and what each gates are in section 9.
3. **E1/E2 protocol fixed before any answer** (G1–G6, P1 5), each a gap in draft 4's pre-registration, not a moved
   bar: pair direction (G1), one fresh context per call (G2), E2 asks the knows → thinks item for all eight words so
   it does not wait for E1 (G3), the closure resolution's one rule and its removal order (G4), the framing and E2's
   wordings, with three added "Does Claude know that P?" items for the asserted-not-know form (G5), and the
   treatment of answers that are not yes, no or cannot tell (G6). The DRI confirms or changes them before the first
   call (section 7).
4. **The debate-round-3 closure items are empty by construction** (P1 3, G4): E2 lists no such items; the closure
   review and its `#guard` are unchanged.
5. **"P, and X does not know that P" needs six items, not three** (G5): D-A7, 3.7, E2 and the checklist.
6. **E2's cost** is 1,040 calls (26 items × 40), not draft 4's implied 600–920 (40 × (15 + |`lowerBound`|));
   E1's 1,440 is unchanged (section 9).
7. **New sections:** 9 (phase-1 record: results, what each gates, DEFERRED triggers) and 10 (cross-plan issues for
   the DRI: four, none changing a shared item).

## 0. Summary

The constitution's latest audit rejected the seven hard constraints (u0165.s01–s07, 874 B) because a mistaken but
confident belief does not trigger them (R 2.2). This plan adds **attitude conditions** to rule guards: "if that
instance of Claude knows that …", "… thinks it quite likely that …", bound to the rule's party, to the rule's
action through one de re slot, and to a typed content (the category) over the base vocabulary. Lean elaborates each
distinct attitude to a generated predicate and regenerates a fixed set of **frame premises** (knowing is factive;
knowing implies believing, and thinking it *w* for each admitted word *w* whose own experiment item passed; a
stronger likelihood word implies a weaker one where the scale orders them). The elaborated document is first-order.
The frame is PK-1's `attitudes` premise pack (edit 6), which the norm-defaults and readings routes carry as their
extra base premises (`BaseAdmissibleX`, `Transfers`). No modal checker, no numbers, no new budget, no new service
mode (edit 7). Thresholds such as "quite likely" stay open terms with a decider. Intentional action ("intentionally
does …") stays a hand-named open term until a reviewed act-performance bridge exists (edit 3).

**Pilot path** (arrows are merge order; F7, debate round 3). AT-0p (pilot, no code; measured in phase 1, PASS on
A1–A7; landing in the pilot DEFERRED, section 9) → E1 and E2 in parallel (DEFERRED: they wait for the DRI's
authorisation of their model calls; with G3, E2 does not wait for E1), then the closure review, then the table is
frozen → AT-0 PASS → AT-1w → AT-1 → AT-2 → AT-3a → AT-3b → AT-6a
(strict companion, structured input, measured) → **DRI go/no-go** → AT-4 → AT-6b (main translation measured) → AT-5
(English; after a "go" it may start once AT-3b and `qa-q2` have merged, alongside AT-4). About 46 to 55 hours by
the table's estimates, experiments included (estimates, not evidence of speed). Off the path, outside core approval
and each with its own statement review: AT-7 (nesting), AT-8 (`reports@0` units in norm documents, after E3), AT-9
(numeric bands, on risk stage B's trigger), E3, E4 (research).

**The smallest batch that moves a pilot number** is AT-0p: the pilot rewrites the seven guards with the existing
language, so the seven "mistaken belief" points move from UNDECIDED to SETTLED no and the seven units can pass the
next audit. Phase 1 measured exactly that on working copies of the pinned run (P1 2): 7 of 7 points UNDECIDED →
SETTLED no, claimed bytes unchanged at 2,951, open terms 33 → 46. It also measured the untyped repair's limit: at
the impossible point (the case false, Claude knowingly engaging in it) all seven rules answer UNDECIDED (A4), which
only typed factivity removes. The smallest *product* batch that moves one is AT-3b (it needs AT-1w to AT-3a),
measured by AT-6a. Every
product batch claims 0 bytes and AT-0p alone moves the audit's number, so the DRI decides go or no-go after AT-6a
(F7), on AT-6a's measured results and the next audit's verdict on AT-0p's seven units, before AT-4 and AT-6b.

## 1. Evidence (short; details in R 2)

| What | Measured value | How |
|---|---|---|
| Hard-constraint units the audit rejects | 7 units, 874 B, OPEN | `AUDIT.md` verdicts; spans in `units.json` (147 + 139 + 89 + 175 + 116 + 160 + 48) |
| The qualification they lack | u0173.s01, 263 B, UNFORMALISED | `units.json` |
| Probe at "case false, knowledge atom true" | UNDECIDED for all 7 rules | `metrics.json`, `unspecified_probe.hard_constraint_points` |
| Primary `modality/belief` tag | 25 units, 3,268 B; none is a rule condition | grep count; spans summed; classification in R 2.3 |
| Co-blocker `modality/belief` | 628 units; bytes not summed (**estimate** ≈ 106 kB upper bound) | grep count of list entries |
| Other attitude-conditioned rules | 7 units, 1,070 B, co-blocked | R 2.8 |
| UDHR | 0 B for this design (upper 97 B) | R 2.5 |
| AT-0p: audit-case points (case false, thinks-quite-likely true) | 7 of 7 UNDECIDED → SETTLED no | P1 2, A1 and A5; `docs/research/evidence/attitudes/at0p-probe.json` |
| AT-0p: impossible points (case false, knowingly true) | 7 of 7 UNDECIDED (the untyped repair cannot refuse them) | P1 2, A4 |
| AT-0p: claimed bytes | 2,951 unchanged (CHECKED 73, LABELLED 349, OPEN 2,529; `bytes_by_status` identical) | P1 2, A6; `at0p-measure.json` |
| AT-0p: open terms | 33 → 46 in the main translation (14 added, 1 removed); 44 in the strict companion | P1 2, A7 |
| AT-0p: everything else | 21 of 21 other probe points and 4 of 4 conflict checks as recorded; render byte-identical outside the seven "Open reading" lines | P1 2 |

## 2. Decisions

- **D-A1. One new profile, no new checker.** `attitudes@0` is an elaboration (VISION rule 1) into the norms chain
  under `norm-defaults@0`, and into the readings chain under `readings@1`. Its premises are PK-1's `attitudes`
  pack (edit 6). It is one row of AR-10's profile-gate table, with its composition proof (edit 7). Nothing frozen
  changes (rule 2): with `attitudes@0` off, W1's, soft's and P0's decoders keep every answer and their fault order,
  `array expected` for an attitude object included; the new profile diagnostic is answered only by the attitudes
  kinds' decoder (SR-6).
- **D-A2. Modes.** `knows`; `thinks w` ("thinks it *w* that", *w* a word of `Scale.lowerBound`, A1); and
  `reports@0`'s four acts (`says`, `believes`, `wants`, `intends`) reused as `Mode.act a`, never copied. No other
  mode. "Intends to VP" and "wants Y to VP" with an act phrase are not admitted (edit 3).
- **D-A3. Contents.** A quantifier-free formula (`VE.Norms.Formula.qfree`, A5) over the **base vocabulary** (A2:
  `E` without its regulated and defined predicates, the vocabulary `BaseAdmissible` ranges over), about at most one
  thing named by a variable of the guard (the slot), which the content mentions; a content about a constant is
  written closed (SR-2). Admission is limited to the conditions 3.7 can word, so every admitted key has its
  sentence and no sentence stands for two keys (SR-2). The frame premises are typed over that base vocabulary
  extended by the generated attitude predicates, and their typing on every route is proved, not assumed. Content
  identity is equality of syntax trees, the identity `VE.Reports.content_structural` proves `reports@0`'s digests
  encode. This profile never hashes a content.
- **D-A4. The frame, and nothing else.** (1) knowing is factive; (2) knowing implies believing; (3) knowing implies
  thinking it *w*, generated per admitted word, only where E2's item for that word reaches the bar (A1); (4) thinking
  it *w₁* implies thinking it *w₂* when the scale puts *w₁* at or above *w₂*. All four relate keys with the same
  holder sort, slot sort and content. (2) ships only if E2 meets its bar; the pairs of (4) only where E1 meets its
  bar. The frozen table records, for each admitted entry, the E1 or E2 item that passed it, and a closure review
  (AT-0, a Lean `#guard`) checks that the reflexive-transitive closure of the frozen pairs adds no pair, and no
  premise-3 word, without its own passing item: "knows → strong" and "strong → weak" yield "knows → weak" even when
  that direct item failed. If a derived entry's item failed, the weaker word of that entry leaves `lowerBound`,
  with every pair and premise that names it, and this repeats until the closure is clean, before freezing. With
  several such entries, the weakest offending word (the last in E1's list) goes first, one word per round: the
  order is part of the rule, since another order can leave a different table that the review also accepts (G4: of
  draft 4's two options, "the weaker word leaves" or "the pair is dropped", only the first, with this order, has a
  unique outcome; spec 2.1).
  No derived entry can lack a direct item: E1 asks all 28 pairs and E2 every word's premise-3 item (P1 3). Decided
  before AT-0 closes, because the profile's meaning freezes when it ships.
- **D-A5. Likelihood words are lower bounds and stay open.** Only words whose lower-bound reading E1's certainty
  item confirms are admitted (`Scale.lowerBound`, A1); any other word, including words that point downward such as
  "unlikely", is refused by `attitudes@0`. For an admitted word, "quite likely" means "quite likely or more"; the
  glossary says so. Its threshold is a named open term. Numbers enter only from a document's declared bands, through
  risk stage B (AT-9), which extends this scale and never copies it.
- **D-A6. Every generated atom is an open term.** Its record is generated: arguments (holder sort, slot sort),
  factors from a Lean table by mode ("what counts as knowing that …", "how likely counts as quite likely"),
  `decided_by` the document's `attitudes.decided_by`, else `unresolved_decider`.
- **D-A7. One reading.** Refused, each with one-reading rewrites whose readings are exactly the form's candidate
  readings, read at the form's category (a guard in its rule's context, or a whole rule) (AT-5, SR-4, SR-5): a
  negated "knows" (the form "P, and X does not know that P", with its content asserted in the same condition, is
  admitted only if its six E2 items reach 36 of 40, A4, G5: the three asserted-content items and three "Does Claude
  know that P?" items, since the first three test only that P is asserted; E2's record holds that decision before
  AT-0 PASS, SR-8);
  "unless X knows that P" (its presupposition is unresolved; debate round 3); "does not think it *w* that"
  (neg-raising); bare "thinks that" (as `reports@0` refuses it); attitude adverbs ("knowingly", "intentionally",
  "deliberately"); a holder pronoun that does not resolve to a variable of the rule. AT-0 states a
  complement-boundary rule, and AT-5 checks whole sentences, not only conditions (A4).
- **D-A8. Lean owns the words.** The four report verbs (`says`, `believes`, `wants`, `intends`) belong to
  `reports@0` and move to `lean/VE/Attribution/Words.lean`; `VE.Attitudes.Words` imports that file and adds only
  `knows` and `thinks` (F6). Refusals and their rewrites are rows in english-lean's catalogue (edit 9), each with
  its category and its candidate readings (SR-5). `reports@0`'s Python literals (`_VERBS`, `_SYNONYMS`, `_REJECTED`
  in `ve/report_english.py`) are deleted in AT-5 and read from the generated export. The English lexical data
  (nouns, wordings, spellings) is the English grammar's (`VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`), carried by
  the document, validated by `Lexicon.failures` and tied to its environment inside `WellFormedAtt`; every predicate
  and constant an admitted condition names has its entry there (D14d, RC-1); admission, rendering and reading read
  that one lexicon (SR-3). `reports@0`'s `wants` verb-phrase test (`_subject_split`, `_infinitive`, and `_finite`,
  the form `_infinitive` checks against) moves into `lean/VE/Attribution/Words.lean` in AT-1w, before AT-1's
  admission check calls it, and AT-1w deletes the Python copy, `reports@0`'s Python English reading Lean's; so the
  test has one owner at every merge (SR-3, RC-4).
- **D-A9. Nothing from intending, wanting or saying.** No success, no desire, no obligation, no belief follows from
  them; no closure under consequence or conjunction; nothing across holders; no introspection. A joined act phrase
  under `intends` or `believes` is never split or distributed by act-phrases' modal × connective table
  (`VE.Acts.table`, which is defined only for *must*, *need not*, *may*, *must not* and *has the right to*).
  Attitudes defines no distribution of its own (edit 4).
- **D-A10. Residual honesty.** Generated open terms count in the residual like any other. The constitution's count
  rises by 20 in all: 21 open terms (14 generated, 7 hand-named intention terms, F4) replace one hand-named term.
  The first 13 are measured: AT-0p took the main translation from 33 to 46 (P1 2, A7); AT-6a's further 7
  (46 → 53) are an **estimate**. How the residual is displayed is not this plan's decision.

## 3. Design

### 3.1 What a writer writes and a reader sees

The pilot's rule u0165.s01 with u0173.s01's condition, as VE renders it (the act phrase and the category wording are
the pilot's existing ones). Every branch and every complement has an explicit boundary (A4): "either … or …, or
both" and "both … and …" are VE's framed connectives, and a complement clause after "knows that" or "thinks it *w*
that" ends at the first frame word opened outside it. The intention conjunct is a hand-named open term, not an
attitude condition (F4, edit 3):

> Every instance of Claude must not do the weapons uplift in each situation if either both that instance of Claude
> knows that that situation is classified as "mass_casualty_weapon_uplift" and that instance of Claude intentionally
> does the weapons uplift in that situation, or that instance of Claude thinks it quite likely that that situation
> is classified as "mass_casualty_weapon_uplift", or both.

The legend adds, rendered by Lean from the frame premises and the open-term records:

> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that
> situation is classified as "mass_casualty_weapon_uplift".
> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that instance
> of Claude thinks it quite likely that that situation is classified as "mass_casualty_weapon_uplift".
> "Quite likely" means quite likely or more likely. How likely counts as quite likely is not decided by VE (decided
> by: unresolved decider).
> What counts as intentionally doing the weapons uplift in a situation is not decided by VE (decided by: unresolved
> decider).

No symbol appears in what people read or write. The structured form (JSON content) is what the pilot writes today;
the English form becomes writable in AT-5.

### 3.2 Syntax, keys and names

A guard is W1's guard grammar with one more atom, an attitude condition. A **key** is (mode, holder sort, slot sort,
content). Keys are listed once each (`VE.Reports.dedup`, reused); each key gets the predicate
`attitudes__<mode>__<i>` on (holder sort, slot sort). Names are fresh in `E`, at most 64 bytes and pairwise
distinct (checked by `WellFormedAtt`, proved by `names_fresh`, `names_injective`); `attitudes__` is registered in
PK-1's `reservedPrefixes` (edit 6).

### 3.3 Elaboration

Each condition becomes `attitudes__<mode>__<i>(holder)` (closed content) or `attitudes__<mode>__<i>(holder, t)`
(slot term `t`). The rule becomes an ordinary `VE.Norms.Node` over `envAtt A = E + generated predicates`. The
document's regulated predicates, completions, act phrases and definitions are unchanged.

### 3.4 The frame

For each `knows` key `k`: `∀h ∀x. k(h, x) → content(x)` (label `attitude:factive`). For each ordered pair of keys
with the same subject that D-A4 relates: `∀h ∀x. k(h, x) → k′(h, x)` (label `attitude:entails`). Contents are
quantifier-free, so every frame premise is universal with a quantifier-free body (`frame_universalQF`), the shape
the norm-defaults evidence requires (`VE.NormDefaults.UniversalQF`). The frame is the premise list of PK-1's
`attitudes` pack (edit 6); its position inside X is PK-1's fixed order: after weighing, before scales.

### 3.5 Semantics and obligations

`Intended` (AT-1) says exactly: attitude relations are typed, knowing is factive, and each frame pair holds. The
obligations of VISION rule 4: faithfulness against this independent semantics (`att_elaboration_faithful`,
`frame_iff_intended`, model correspondence both ways); conservativity (`att_old_language_conservative`); the
audit's requirement (`mistaken_belief_admissible`); nothing beyond the frame, as a closure statement (F3, edit 2):
for any finite typed seed set of (key, tuple) whose `knows` members have true contents, the seed's frame closure
(`VE.Closure.Reachable .star` over `framePairs`, the tuple preserved) is `Intended` and is contained in every
intended model that holds the seed, so a seed forces an attitude exactly when frame pairs reach it
(`seed_intended`, `seed_least`, `forced_iff_reachable`; `mistaken_belief_admissible` is an instance); certificate
soundness and model validity are the existing routes' theorems instantiated with the assembled X (AT-2, AT-4); a
trust-cost line in ROADMAP (AT-3a).

### 3.6 Routes

| Route | Existing extra-premise mechanism | How the frame enters |
|---|---|---|
| norm-defaults, layered (the pilot's `readings/all-strict.ve.md`) | PK-1's assembler over `VE.NormDefaults.Wire.LayeredU` (`X`, `background := backgroundBase ++ X ++ fillPremises`), `layered_conflict_sound`, `layered_report_sound`, `UndecidedAtX` | the frame is the `attitudes` pack: `kind := .vocabulary` (expansion step: empty attitude relations satisfy every frame premise), `decls` the keys' names with `Key.sorts`, `labelled := (frameLabels A).zip (framePremises A)`, `origins` each key and label ↦ its full request occurrence (edit 6); AT makes no edit to `Layered.lean` beyond its one provider registration line (AT-2, AT-3a) |
| norm-defaults statuses at a point | the layered route's status kind (`replayStatusX`) | the status kind checks that the point satisfies every X premise; AT-0 confirms it does, else PK-1 adds the check once for all packs (edit 7); then `SettledAs`/`UndecidedAt` agree with their X versions (`settled_frame_agree`, `undecided_frame_agree`, stated with the assembled X, AT-2) |
| readings, superposed and enumerated (the main translation) | `VE.Readings.Transfers`, `superpose_*_extra`, `fill_transfers`, PK-1's `transfers_append` | the assembled family, with the frame by `frame_transfers`, attitudes' provider obligation (AT-4) |

Attitude guard nodes are decoded, when `attitudes@0` is on, by the chain's norm decoders (W1's
`VE.Norms.Wire.decodeNorm` and soft's `VE.SoftNorms.Wire.decodeSoftNorm`; `VE.Readings.Wire.decodeNorm` and the
layered decoder dispatch to them), so one guard-node hook serves the norms, soft, layered and readings routes; the
`environment.attitudes` block is decoded by the `attitudes` pack provider. There is no `attitudes` service mode:
`attitudes-elaborate`, `attitudes-status`, `attitudes-conflict` and `attitudes-report` are kinds of the layered
route over the assembled X (edit 7). With `attitudes@0` off, those decoders are unchanged (SR-6). The attitudes
kinds' decoder, `decodeAttDoc`, also decodes the case's English lexicon with the English grammar's own decoders
(SR-3), and ends with `checkAtt`, so a decoded document is a checked one (SR-7).

### 3.7 English and one reading (AT-5)

| Wording | Reading | Status |
|---|---|---|
| "X knows that P" | knows | admitted |
| "X thinks it *w* that P", *w* in `Scale.lowerBound` | thinks *w* (lower bound) | admitted; any other word refused (A1) |
| "X believes that P", "X wants Y to VP", "X intends that P", "X says that P" | `reports@0`'s acts | admitted ("intends to VP" and "wants Y to VP" with an act phrase are not admitted. Intentional action stays residual until a reviewed act-performance bridge, designed by events-time-causation (ET-D2), fits this profile's contract: quantifier-free content over the base vocabulary, one slot. Act-phrases landing does not admit them; edit 3). "X wants Y to VP" only for one unary base predicate on the slot whose wording `reports@0`'s test turns into "Y to VP"; any other `wants` content is refused (SR-2) |
| a slot its content does not mention; a slot at a constant | one sentence for two keys | refused at admission; a content about a constant is written closed; de re versus de dicto about a named constant is a later admission with its own E2 items (SR-2) |
| a condition naming a predicate or constant with no entry in the document's lexicon | no sentence | refused at admission (D14d, RC-1) |
| "P, and X does not know that P" | not knows, content asserted | admitted only if its six E2 items reach 36 of 40 (three "Must P?", three "Does X know that P?"); otherwise refused with its rewrites (A4, G5) |
| "unless X knows that P" (carve-out) | unresolved presupposition | refused, with rewrites; E2's three "unless" items are evidence for a later admission with its own statement review only (debate round 3) |
| "X does not know that P" elsewhere | two readings (with and without P) | refused `NegatedFactive`, with one-reading rewrites |
| "X does not think it *w* that P" | neg-raising: two readings | refused `NegRaising`, rewrites: "it is not the case that X thinks it *w* that P"; "X thinks it *w* that it is not the case that P" |
| "X thinks that P" | belief or opinion | refused (as `reports@0`), rewrites: "X believes that P"; "X thinks it likely that P" |
| "X knowingly / intentionally / deliberately VPs" | scope of the adverb | refused `AttitudeAdverb`, rewrite into conditions |
| "it thinks …" with "it" not a rule variable | unresolved holder | refused (discourse rule: no pronoun crosses a quote boundary) |

Each refused row with rewrites is a catalogue row with its category (a guard, read in its enclosing rule's context;
or a whole rule, as for "unless") and its candidate readings, written independently of the rewrites; the rewrites'
readings are exactly those candidates, pairwise distinct (SR-4, SR-5). The spec's section 3.4 governs the rows.

### 3.8 Limits and UNKNOWN

No new budget. Generated predicates count against `MAX_PREDICATES` (256), which bounds the declared plus the
unspecified predicates (norm-defaults 5.1, the **filled** count; `ve/norm_defaults_contract.py`). The constitution's
main translation has 50 declared and 65 filled at the pinned run; AT-0p's 14 binary open terms replace one
hand-named term, giving 63 declared and 78 filled (15 unspecified in both). With the 7 hand-named intention terms:
**about** 70 declared and 85 filled (**estimate**; AT-1's 14 generated predicates replace AT-0p's 14 open terms one
for one). The readings route's own size count (`sizesJson`) adds its three generated predicates and is checked
against the same 256: 68 and 81 measured (`readings/nd-all-check.json` of `research/attitudes/run-baseline` and
`run-at0p`), **about** 88 projected; drafts 1–4's "uses 68 … about 88" quoted that count as the limit's. Above the
limit, admission refuses (`InvalidInput`), never a verdict. A document's scale is bounded by a `VE.Closure.Caps`
value, checked by QS-1's `Order.admit` inside `WellFormedAtt` (A5, edit 1). Every UNKNOWN of the routes stays
UNKNOWN.

### 3.9 One owner per piece of logic

| Piece | Owner | This plan |
|---|---|---|
| Acts says, believes, wants, intends; their names | `VE.Reports.Act`, `Act.name` | reused as `Mode.act` |
| Content identity | AST equality (`VE.Reports.content_structural`) | reused; no hashing |
| Key de-duplication | `VE.Reports.dedup` | reused |
| Open-term record schema | W2 (`document.md`), `VE.Reports.Assessment` shape | generated records follow it |
| Quantifier-free formulas | `VE.Norms.Formula.qfree` | reused; draft 1's `qf` is deleted (A5) |
| Extra base premises on routes | PK-1 packs (RD-9 composition owner) over `LayeredU`, `BaseAdmissibleX`, `Transfers` | attitudes is the `attitudes` provider; no new route semantics |
| Likelihood words and their order | `VE.Attitudes.Scale`; closure is QS-1's over `VE.Closure` | attitudes owns `table`, E1/E2 gating, `lowerBound`, the frozen record of which item passed each entry, and the closure-review `#guard`; risk stage B extends it (AT-9) |
| Attitude verbs, synonyms, refusals (English) | the four report verbs stay under attribution (`VE.Attribution.Words`); `VE.Attitudes.Words` adds only `knows` and `thinks` | **moves** from `ve/report_english.py`; AT-5 deletes the Python literals |
| Intentional action ("intends to VP") | residual; the bridge's design is events-time-causation's (ET-D2) | not admitted (edit 3) |
| Distribution over joined acts | none in attitudes | edit 4 |
| Hedged calc claims | a separate bridge, unowned | edit 5 |
| Refusals and source-word reading sets | rows in english-lean's catalogue | AT-5 adds rows, each with its category and candidate readings (SR-5), no separate refusal table |
| English lexical data and its validity | the English grammar: `VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`, `Lexicon.failures`; decoders `Env.decode`, `Overlay.decode`, `Run.decodeLexicon` | carried by the document (`AttDoc.lex`), checked in `WellFormedAtt` (D6a, D6b, and per condition D14d, RC-1), decoded at AT-3a; no attitude-local template classifier (SR-3) |
| The `wants` verb-phrase test | `reports@0` (`_subject_split`, `_infinitive`, `_finite` in `ve/report_english.py`) | **moves** into `lean/VE/Attribution/Words.lean` in AT-1w, which deletes the Python copy in the same batch (SR-3, RC-4) |
| The hand-named open term `restricted_action_knowing_or_quite_likely` | pilot translation | deleted by AT-0p (measured on working copies, P1 2; lands with the pilot's next run, section 9), then AT-0p's atoms by AT-6 |

### 3.10 Conservativity

Any structure over `E` extends to `envAtt A` by reading every generated predicate as empty; every frame premise
then holds (its antecedent is false), and old formulas keep their values. So a document without attitude
conditions means what it meant, and old-language consequence is unchanged (`att_old_language_conservative`,
`att_conservative_doc`). The same extension is the `attitudes` pack's expansion step as a PK-1 `vocabulary` pack
(edit 6).

## 4. Batches

Every product batch: 2 to 6 hours for one builder, with the lean-first gate (selected tests while iterating; the
full gate once, on the final HEAD; corpus A/B where the batch changes an answer; `DELTA.md` by class), the Lean audit
(`python3 lean/audit.py`: no forbidden word even in comments, no primes in theorem names, names under about 57
characters), regenerated inventories through `uv run python tools/regen_generated.py --write` (never by hand),
`tools/lean_statements.py` showing additions only, and seeded bugs in each changed language (CLAUDE.md). The seeded
bugs, one per behaviour claimed: AT-1w, `wantsPhrase?` without the irregular `is` → `be` (the recorded infinitive of
"is classified as …" changes), and the relay accepting a row for a phrase it did not send (a fuzz test fails, RC-4); AT-1, factivity generated with its implication reversed (F-AT1's M2 `#guard` fails), the constant-slot check
(D14b) skipped (collision fixture C-b's `#guard` fails, SR-2), and the lexicon-entry check (D14d) skipped for
constants (C-d's first document is admitted, RC-1); AT-2, the frame
check skipped at a point (M2 is no longer refused); AT-3a, the decoder accepting `degree` on a mode other than
`thinks`, the decoder returning before `checkAtt` (a route fixture of a failing check answers an elaboration, SR-7),
and the hook answering the new profile text with `attitudes@0` off (a W1 compatibility fixture fails, SR-6); AT-3b,
below; AT-4, the frame dropped from one choice's base premises (an enumerated fixture fails); AT-5, a refused form
read with one of its two readings, and a rewrite read with a reading outside its row's candidates
(`refused_have_rewrites`'s fixtures fail, SR-5).
Statement review before Lean build: AT-0 reviews every statement below; a statement that changes during a build
reopens only that statement.

| # | Batch | Hours | Owner | Needs |
|---|---|---:|---|---|
| AT-0p | Pilot repair with the existing language (no product code). **Measured in phase 1: PASS on A1–A7; A8 and the landing DEFERRED** (section 9) | 2 | pilot runner | — (first step of the hard-constraint queue, edit 10) |
| E1 | Likelihood-word order and lower-bound reading (experiment). **DEFERRED** (section 9): items, orders and scorer ready | 2–3 | experiment runner | the DRI's confirmation of G1, G2, G5, G6 and authorisation of 1,440 calls |
| E2 | Factivity, knows → believes, knows → thinks it *w* for all eight words (G3), negated "know", "unless", "P, and X does not know that P" with its six items (G5) (experiment). **DEFERRED** (section 9) | 2 | experiment runner | the DRI's confirmation of G2–G6 and authorisation of 1,040 calls; not E1 (G3) |
| AT-0 | Statement spec `docs/spec/attitudes.md`, stub elaborated against main, small-scope counterexample search, statement review (round 1: FIX, SR-1 to SR-8; re-check: FAIL, RC-1 to RC-4; re-review of the changed statements) | 3–4 | planner | E1, E2 results and the closure review |
| AT-1w | `reports@0`'s `wants` test moved into Lean, its Python copy deleted, `reports@0`'s Python English reading Lean's through a `reports` kind (RC-4) | 3–4 | Lean, Python | AT-0 PASS |
| AT-1 | Lean core: syntax, keys, elaboration, frame, semantics, admission with the lexicon and `renderable`, theorems, fixtures | 5–6 | Lean | AT-1w; QS-1 merged (edit 1) |
| AT-2 | Lean: the layered route with the `attitudes` pack (statuses, conflicts, report) | 4–5 | Lean | AT-1; PK-1 merged (and so `rd-9-int`) |
| AT-3a | Lean wire: the guard-node hook in the chain's norm decoders, the pack provider's block decoder, the layered kinds, their shape and encoder theorem | 5–6 | Lean | AT-2; PK-1 and AR-10's table merged; `lf-16e`, `qa-q2` merged; on `lean/VE/Norms/Wire.lean` after act-phrases' AP-1 and AP-3 |
| AT-3b | Python relay with request-path binding, `ve document` hook, fixtures and fuzz tests | 4–5 | Python | AT-3a; first in the document-mode queue after `lf-16g` |
| AT-6a | Pilot: the strict companion with typed attitudes, structured input, measured | 3 | pilot tooling | AT-3b; after SC-2 in the hard-constraint queue (edit 10) |
| — | **DRI go/no-go** (F7): AT-6a's measured results and the next audit's verdict on AT-0p's seven units | — | DRI | AT-6a |
| AT-4 | Readings chain with the `attitudes` pack (superposed and enumerated) | 5–6 | Lean, Python | "go"; AT-3b; `lf-14d`, `rd-9-int` merged |
| AT-6b | Pilot: the main translation with typed attitudes, measured | 3 | pilot tooling | AT-4; after SC-2 in the hard-constraint queue (edit 10) |
| AT-5 | English in Lean: wordings, refusals as catalogue rows, rewrites; `reports@0`'s Python tables deleted | 5–6 | Lean, Python | "go"; AT-3b; `qa-q2` merged; first in the English queue (edit 9) |
| AT-7 | Nested conditions (two levels) and "knows whether" | 5–6 | Lean | AT-4 |
| E3 | "We want Claude to X": report, rule, or both (experiment) | 3 | experiment runner | — |
| AT-8 | `reports@0` units in norm documents | 5–6 | Lean, Python | E3; DRI decision with the attribution owners |
| AT-9 | Numeric bands on the scale (shared with risk stage B) | 3–4 | Lean | risk stage B's trigger |
| E4 | Claims as objects for honesty norms (experiment) | 4–5 | planner, Lean stub | AT-1 |

### AT-0p. Pilot repair with the existing language (pilot runner, 2 h)

No product code. In the constitution pilot, for each hard constraint i (seven categories `C_i`, the existing case
atoms), replace the guard `C_i(s) ∧ restricted_action_knowing_or_quite_likely(s)` by

```text
( C_i(s) ∧ knowingly_engages_<i>(c, s) ) ∨ thinks_quite_likely_<i>(c, s)
```

with fourteen binary open terms on (`claude_instance`, `situation`): `knowingly_engages_<i>` ("Claude knowingly and
intentionally engages in the action of the situation as an action of category i"; factor: what counts as knowingly
and intentionally engaging) and `thinks_quite_likely_<i>` ("Claude thinks it quite likely that the action of the
situation falls into category i"; factor: how likely counts as quite likely). `C_i(s)` stays explicit in the first
branch because VE cannot know, with untyped terms, that knowing implies the category. Delete
`restricted_action_knowing_or_quite_likely`.

- **Probe points to add** (four per rule, `probes/unspecified-probe.json`): case false and thinks-quite-likely true
  (expected SETTLED no, the audit's case); case true and knowingly true (SETTLED no); neither (UNDECIDED); case
  false and knowingly true (UNDECIDED: an impossible situation the untyped language cannot refuse).
- **Expected numbers (draft 4's estimates, pre-registered in P1 1.1 and now measured, below):** claimed bytes
  unchanged (2,951); the 7 units (874 B) become candidates for audit verification; open terms 33 → 46; the seven
  audit-case points UNDECIDED → SETTLED no.
- **Not claimed:** typing. AT-6a replaces the fourteen open terms with generated attitudes and seven hand-named
  intention terms (F4).
- **Queue (edit 10).** AT-0p is the first step of the u0165.s01–s07 queue: `AT-0p → SC-1b → SC-2 → AT-6a/AT-6b →
  WG-5`; each step starts from the translation as the previous step left it.

**Result (phase 1, P1 2).** Run on two working copies of the pinned run `run-20261012T1800Z`, with the run's own
scripts and probe method, after a byte-identical reproduction of its recorded translation and probe (script
`research/attitudes/at0p.py`, end to end `run_at0p.sh`; evidence `docs/research/evidence/attitudes/at0p-*.json`).

| # | Bar (P1 1.1) | Measured | Verdict |
|---|---|---|---|
| A1 | case false, thinks-quite-likely true: SETTLED no | 7 of 7 | **PASS** |
| A2 | case true, knowingly true: SETTLED no | 7 of 7 | **PASS** |
| A3 | neither: UNDECIDED | 14 of 14 (case true and case false) | **PASS** |
| A4 | case false, knowingly true: UNDECIDED | 7 of 7 | **PASS** |
| A5 | the audit-case points UNDECIDED → SETTLED no | 7 × UNDECIDED reproduced → 7 × SETTLED no | **PASS** |
| A6 | claimed bytes unchanged (2,951) | `bytes_by_status` identical: 2,951 = CHECKED 73 + LABELLED 349 + OPEN 2,529 (CHECKED + OPEN = 2,602, also unchanged) | **PASS** |
| A7 | open terms 33 → 46 | 46 (strict companion: 44) | **PASS** |
| A8 | the 7 units (874 B) become candidates for audit verification | needs the next audit | **DEFERRED** (section 9) |

Not bars, also measured: the other 21 probe points and the run's four conflict checks give their recorded answers;
the main translation keeps the run's assertions (premises `model`, plan `enumerate` with 8 choices, CONFLICT-FREE,
coverage 100 %); the rendering changes only the seven rules' "Open reading" lines. **Observation:** the rendering
names the new open terms by identifier ("… has the recorded relation "thinks_quite_likely_1" to that situation"),
as it named the deleted one, so an auditor reading only the rendering sees neither the description nor the factors
(section 7, risks; section 10, item 4).

**Landing.** AT-0p is measured, not landed: the pilot directory was read only in phase 1. The pilot runner lands
it in the next constitution run with `at0p.py` (copy, apply) on that run's inputs; SC-1b starts from that
translation (section 9, section 10 item 2).

### E1. Likelihood words: order and lower bounds (experiment, 2–3 h)

Pre-registered. Readers: Sonnet 5.5 as human proxy (`claude-sonnet-5-5`), 40 independent sessions with no shared
context, items in a seeded random order (seed `attitudes-E1`). Words: almost certain, very likely, quite likely,
likely, more likely than not, as likely as not, unlikely, very unlikely (8 words, 28 pairs), each pair as two
sentences "Claude thinks it *a* that the file is safe" / "… *b* …", question: "If the first sentence is true, must the
second be true?" (yes / no / cannot tell). Plus 8 items "If Claude is certain that the file is safe, does Claude
think it *w* that the file is safe?".

- **A pair enters the scale table** (`table.above`, with its item) iff at least 36 of 40 answer yes and at most 2
  answer no.
- **The lower-bound reading of a word** is confirmed iff at least 34 of 40 answer yes to its certainty item; the
  word then enters `Scale.lowerBound` (with its item). A word that fails is refused by `attitudes@0` (A1), and no
  pair names it.
- Nothing else is concluded. This measures agreement among proxy readers, not truth and not human readers. Cost
  **estimate**: 40 × 36 = 1,440 short calls, under the usage cap rules.

**Protocol fixed before any answer (draft 5; G1, G2, G5, G6 from P1 5).** The bars above are draft 4's, quoted in
P1 1.2 before any run, and do not move. These say what draft 4 left unsaid. They are phase 1's proposals, written
into `e1-items.json` and `research/attitudes/experiments.py` except where marked, and the DRI confirms or changes
each before the first call; after it, nothing here changes.

- **G1, pair direction.** Each of the 28 pairs is asked once, the earlier word in the list above as the first
  sentence, so a passing item is the scale pair (earlier, later). Item ids `E1.pair.<a>.<b>` and `E1.cert.<w>`.
- **G2, independence.** One fresh context per call: no system prompt beyond the preamble, no earlier turn. The 40
  "sessions" are 40 readers per item; the seeded order (`random.Random("attitudes-E1")`, 40 orders) fixes only the
  call order.
- **G5, framing.** Preamble: "Read the text and answer the question as an ordinary reader of English. Answer with
  exactly one of: yes, no, cannot tell." Pair items label their parts "First sentence:", "Second sentence:",
  "Question:"; certainty items label only "Question:". These choices can move answers; the DRI fixes them.
- **G6, answers that are not yes, no or cannot tell.** The first line is read; anything else is invalid. An invalid
  answer is not a yes (it counts against every yes bar) and, for the bar "at most 2 answer no", **counts as a no**
  (so 36 yes and 4 "Not necessarily." fails, as the bar intends). The invalid count is reported per item. Reader
  settings (temperature, output limit, extended thinking) are the reader's defaults, recorded with the answers.
  *Not yet in the scorer:* `experiments.py` still counts invalid as neither for the no cap; it changes, with a
  self-check case at the boundary, before the run and only after the DRI's decision.

**Status: run 2026-10-13, after the DRI's AT1 (section 9; [docs/research/attitudes-e1e2.md](../research/attitudes-e1e2.md)).** Was DEFERRED in phase 1 (P1 3). Ready then: 36 items, 40 seeded orders, the scorer with the bars as constants
(`PAIR_YES, PAIR_MAX_NO = 36, 2`; `CERT_YES = 34`), refusal of an answer set without exactly one answer per item and
reader, and a self-check of 24 cases (`docs/research/evidence/attitudes/e-selfcheck.json`: the bars at their
boundaries, and G4's resolution with one and with three violations, through Lean). Cost: 1,440 calls, as estimated.
**Gates:** `table.above` and `table.lowerBound`, hence every `thinks w` mode and frame premise 4; through the
closure review, AT-0 PASS.

### E2. Factivity and the knowing entailments (experiment, 2 h)

Same protocol. Items: three factivity items ("Claude knows that the file is safe. Must the file be safe?"); three
"knows → believes"; one "knows → thinks it *w*" item for each of E1's eight words, scored only for the words that
enter `lowerBound` (G3; draft 4 asked it per lower-bound word, which made E2 wait for E1); three negated-"know"
items ("Claude does not know that the file is safe. Must the file be safe?", where the expected answer splits);
three "unless X knows that P" items (for example, "… unless Claude knows that the user is an adult. The user is not
an adult. Must Claude not share the file?"); six "P, and X does not know that P" items (A4, G5): three asking "Must
P?" (expected yes) and three asking "P, and Claude does not know that P. Does Claude know that P?" (expected no).
Draft 4's further items, one for each pair the closure of E1's pairs derives without a direct E1 item and for each
premise-3 word reached only through the closure (debate round 3), are **empty by construction** (P1 3): E1 asks
all 28 pairs and E2 all eight words, so the closure can reach only an entry whose own item failed, which the
closure review below resolves (G4).

- Frame premise 1 ships iff all three factivity items reach 36 of 40. (If not, `knows` is not admitted at all.)
- Frame premise 2 ships iff its three items reach 36 of 40. Premise 3 ships per word, iff that word's item reaches
  36 of 40.
- **Closure review**, then freezing. The frozen table records, for each admitted entry, the item that passed it. A
  Lean `#guard` (`Table.reviewed`, evaluated through QS-1's closure) checks that the reflexive-transitive closure of
  the frozen pairs adds no pair, and no premise-3 word, without its own passing item. If a derived entry's item
  failed, the weaker word of that entry leaves `lowerBound`, with every pair and premise that names it, until the
  closure is clean, before freezing; of several offending words the weakest goes first, one per round (G4, D-A4;
  `resolve` in `experiments.py`, its output reviewed by Lean). **Pre-registered example:** if, of the pairs among
  "almost certain", "very likely", "quite likely" and "likely", only the chain's three pass, three derived pairs
  fail; the rule removes "likely", then "quite likely". Removing "quite likely" first would keep "likely" and also
  pass the review, so the review alone does not fix the outcome; the self-check runs this case through Lean
  (`removed_three_violations` in `e-selfcheck.json`).
- The negated-"know" items are expected to split (that is why D-A7 refuses the form); if instead 36 of 40 agree on
  one reading, AT-0 records it and keeps the refusal anyway (one reading must not depend on a majority). Invalid
  answers are left out of that agreement count (G6).
- "P, and X does not know that P" is admitted only if all six of its items reach 36 of 40 (G5; draft 4 said its
  three items, but those test only that P is read as asserted, so they could not admit the form); otherwise it is
  refused, with its rewrites. The "unless" items are evidence only: the form stays refused whatever they show, and a
  later admission needs its own statement review (debate round 3).

**Protocol fixed before any answer (draft 5; G2–G6 from P1 5).** As E1's (G2, G5's preamble and "Question:" label,
G6), plus: G3 and G5's three added items above, and E2's wordings, which draft 4 did not give, are those of
`docs/research/evidence/attitudes/e2-items.json` (seed `attitudes-E2`). The DRI confirms or changes each before the
first call. *Not yet in the item file and scorer:* G5's three added items (the scorer's decision for the form is
"refused" whatever the counts until they exist, `8538355c`) and G6's agreement rule; both are added, with
self-check cases, before the run.

**Status: run 2026-10-13, after the DRI's AT1 (section 9; [docs/research/attitudes-e1e2.md](../research/attitudes-e1e2.md)).** Was DEFERRED in phase 1 (P1 3). Ready then: 23 items, 40 seeded orders, the scorer (`E2_REACH = 36`), the
emitter of the Lean `Table` literal and its review by Lean's `Table.reviewed` (through the AT-0 stub, pinned by
sha256). Cost: 1,040 calls (26 items × 40; 920 without G5's three). **Gates:** `table.factive` (and with it every
`knows` condition), `table.knowsBelieves`, `table.knowsThinks`; the admission of "P, and X does not know that P";
the closure review and freezing; through them, AT-0 PASS (SR-8).

### AT-0. Statement spec and review (planner, 3–4 h)

- `docs/spec/attitudes.md`: sections 2 and 3 as a statement spec (definitions, wordings with one reading each, wire,
  diagnostics in order, the Lean blocks of AT-1 to AT-4 verbatim, fixtures, limits, review checklist), with E1's
  pairs and E2's frame decisions written in.
- `lean/SpecStubs_attitudes.lean`, untracked: every definition with the bodies given here and every statement as a
  `def … : Prop`, elaborated with `lake env lean` against a build of main. Every failure is fixed in the spec. Every
  theorem gets one `#guard` instance on F-AT1 or F-AT2 (A3).
- **Small-scope counterexample search** (debate round 3). For each theorem that can be decided on finite models (as
  `guard_collapse` can), a `#guard` tries every AttDoc with at most two keys and two holders, on models with at
  most two elements. A counterexample fails the review. This search would have caught A3: its counterexample is a
  one-element model. Elaborating a statement is not evidence that it holds; only AT-1's proofs establish it.
- Pins the integration points this plan can only name: the guard-node hook point in the chain's norm decoders (on
  `lean/VE/Norms/Wire.lean`, serialised after act-phrases' AP-1 and AP-3), and that no second guard decoder remains;
  the diagnostic text when `attitudes@0` is off; whether the layered status kind checks that the point satisfies
  every X premise (if not, PK-1 adds the check once for all packs); whether `ve document` dispatch is Python or
  Lean's `document` mode after `lf-16e`; the export of the English table (AT-5).
- Review checklist: section 8.
- **Round 1 of the statement review (2026-10-13): FIX** (`manage-agents/debates/attitudes-spec/`, converged after
  round 3). Spec draft 2 and this draft make its corrections, SR-1 to SR-8 (spec section 14). Before PASS, in this
  order (SR-8): E1 and E2 are recorded in `table` with their items, including E2's decision on asserted-content
  negated knowledge; the closure review holds and the table is frozen; the stub is updated to spec draft 2 and
  elaborated; every fixture and the counterexample search are rerun on the frozen table, with the new refusals
  (D6a–D6b, D14a–D14d) in the search's pool; the reviewers re-review only the statements that changed.
- **The re-check of spec draft 2 (2026-10-13): FAIL** (`manage-agents/attitudes-p3ver1.final.md`): SR-1, SR-2, SR-4,
  SR-5, SR-7 and SR-8 present and correct; three problems remain. Spec draft 3 and this draft correct them, RC-1 to
  RC-4 (spec section 15): D14d, the lexicon entry of every symbol a condition names (RC-1); the SR-6 fault-order
  fixture (RC-2); the D15 fixture's lexicon (RC-3); and AT-1w, so that the `wants` test has one owner at every merge
  (RC-4). The stub is updated to spec draft 3, not 2, before the steps above.
- **Phase 1 (draft 5).** E1 and E2 are DEFERRED (section 9), so SR-8's first step has not started and AT-0 PASS
  waits on their trigger. Spec draft 4 changes no Lean statement. The stub's `Table` and `Table.reviewed` are the
  closure review E2's emitter calls, and `experiments.py` refuses a stub whose sha256 is not the pinned
  `2178fb6e…` (`8538355c`). So updating the stub to spec draft 3 or later also updates that pin in the same commit
  and reruns the self-check; if `Table` or `Table.reviewed` changed, the closure review's statement is re-reviewed
  before any table is frozen.
- **After E1 and E2 (2026-10-13).** E1 and E2 are recorded and the table frozen (section 9). The stub is updated to
  spec draft 4's Lean with the frozen table (`Table` and `Table.reviewed` unchanged, so the closure review needs no
  re-review), committed and re-pinned (`0c73f880…`), elaborated, and every fixture and the search are rerun on the
  frozen table with the asserted-not-know form in the pool: no counterexample (section 9, AT0C). Only the
  re-review of the changed statements remains
  ([docs/research/attitudes-at0-changed.md](../research/attitudes-at0-changed.md) section 2).
- Done when the stub elaborates, the search finds no counterexample, the spec is committed, and the review
  converges on PASS.

### AT-1w. `reports@0`'s `wants` test moved into Lean (Lean, Python, 3–4 h)

`reports@0`'s `wants` verb-phrase test is Python only on `main` (`_subject_split`, `_infinitive`, and `_finite`, the
form `_infinitive` checks against; `ve/report_english.py`). AT-1's admission check D14c and AT-5's renderer call it
in Lean, and one owner per piece of logic means it must never exist in both languages at once (RC-4). So this batch,
before AT-1, moves it and switches its Python callers in one merge (spec section 10, item 6).

Files: `lean/VE/Attribution/Words.lean` (new: only `wantsPhrase?` and the finite form it checks against; AT-5 adds
the verbs, F6). Hand-written shared files: `lean/VE/Attribution/Run.lean` (one new kind of the existing `reports`
mode, answering for each verb phrase the case sends its infinitive under the test, absent when the test refuses it,
and for each infinitive its finite form), `lean/ResponseShape/Schemas/Reports.lean` (the kind's row, typed to the
leaves; `ResponseShape.Encoders.Reports.runCaseReported_fits` keeps its statement, its skeleton gaining the row),
`ve/reports_route.py` and `ve/reports.py` (the relay, reached by `ve/report_english.py` through the `reports`
document object it is already given, since the surface layer does not import the relay, `tools/layer_policy.py`),
`ve/report_english.py` (`_infinitive` and `_finite` deleted; the printer's `_subject_split` and the parser's "to
VP" readings take both forms from Lean). Generated: `ve/backends/lean_service_schema/reports.json`, recorded route
cases, the Lean inventories and the gate collection, as AT-1.

Python checks the kind's rows for schema and binding only: each phrase it sent answered once, in order, nothing
extra (the DRI rulings' R8). Fixtures: before deleting them, the batch records `_infinitive` and `_finite` on every phrase the suite's
`reports@0` cases reach, and Lean's kind answers the same; every existing `reports@0` English test
(`tests/test_report_english.py`, `tests/test_reports.py`) keeps its answer; fuzz tests drop, empty, retype, duplicate
and reorder each row's members and add a row for a phrase not sent.

Bytes unlocked: 0. Done when no `reports@0` English answer changes, the Python copy is gone, the audit passes, and
the gate passes.

### AT-1. Lean core (Lean, 5–6 h)

Files: `lean/VE/Attitudes/Scale.lean`, `Syntax.lean`, `Frame.lean`, `Semantics.lean`, `Theorems.lean`,
`Examples.lean` (`#guard`s), all new; `lean/VE/Attribution/Words.lean` is AT-1w's (its `wantsPhrase?` is the test
admission check D14c calls; SR-3, RC-4); `lean/ATTITUDES.md` (new). Generated (regenerate, never hand-edit):
`lean/VE.lean` (import union), `lean/VE/Audit.lean` (one `#print axioms` line per theorem),
`lean/VE/Route/frozen-sources.sha256`, `lean/axioms.txt`, `lean/statements.txt`, `lean/declarations.txt`,
`lean/predicates.txt`, `tools/gate-collection.json` (unchanged unless a test is added). No hand-written shared file.
Needs AT-1w, and QS-1 (`lean/VE/Closure/Order.lean`, owned by quantities) merged (edit 1).

The block below is draft 1's with the converged edits made; AT-0's elaborated text
([attitudes.md](attitudes.md) sections 2 to 4) governs where they differ. In particular the statement review's
corrections are written there, not here: `AttDoc` gains `lex` (the English grammar's `Env`, `Overlay` and
`Lexicon`); `checkAtt` gains D6a (`Lexicon.failures`) and D6b (`lexAgrees`) after the reserved-prefix check; and
`checkCond` ends with `renderCheck` (D14a unused slot, D14b slot at a constant, D14c `wants` without its wording,
D14d a predicate or constant with no lexicon entry), whose success is `renderable` (SR-2, SR-3, RC-1). The block
therefore also imports `VE.EnglishGrammar.Lexicon` and `VE.Attribution.Words`.

```lean
import VE.Attribution.Content
import VE.Norms.Tree
import VE.Norms.SmallModel
import VE.NormDefaults.Evidence
import VE.Closure.Order

namespace VE.Attitudes
open VE.Reports (Act)
universe u

/-! ## The likelihood scale (D-A5). Risk stage B adds declared ranges to these words (AT-9); it never copies them. -/

/-- A likelihood word as written after "thinks it", in lower case: "quite likely". -/
abbrev Word := String
/-- The id of the pre-registered E1 or E2 item that passed an entry. -/
abbrev Item := String

/-- `above` lists pairs `(a, b)` read "a is at least as likely as b". -/
structure Scale where
  words : List Word
  above : List (Word × Word)
  deriving DecidableEq, Repr

def Scale.toOrder (σ : Scale) : VE.Closure.Order Word := ⟨σ.words, σ.above⟩

/-- The reflexive and transitive closure of `above`: QS-1's (edit 1). -/
def Scale.atLeast (σ : Scale) (a b : Word) : Bool := (σ.toOrder).atLeast a b

/-- The frozen table (A1, debate round 3): `lowerBound` holds the words whose E1 certainty item passed; every
    admitted entry records the E1 or E2 item that passed it. Before E1 and E2 report, nothing is admitted. -/
structure Table where
  candidates : List Word
  lowerBound : List (Word × Item)
  above : List (Word × Word × Item)
  factive : Option Item
  knowsBelieves : Option Item
  knowsThinks : List (Word × Item)

def table : Table :=
  { candidates := ["almost certain", "very likely", "quite likely", "likely", "more likely than not",
      "as likely as not", "unlikely", "very unlikely"],
    lowerBound := [], above := [], factive := none, knowsBelieves := none, knowsThinks := [] }

/-- The closure review: the closure of the frozen pairs adds no pair, and no premise-3 word, without its own item. -/
def Table.reviewed (t : Table) : Bool := tableReviewedBody t
#guard table.reviewed

/-- The bounds on a document's scale, checked by QS-1's `Order.admit` inside `WellFormedAtt` (A5, edit 1). -/
def scaleCaps : VE.Closure.Caps := ⟨8, 64⟩

/-! ## Syntax (3.2) -/

/-- `act a` is the act `a` of reports@0 with its name and English verbs; `knows` and `thinks w` are new. -/
inductive Mode where
  | act (a : Act)
  | knows
  | thinks (w : Word)
  deriving DecidableEq, Repr

def Mode.slug : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks_" ++ w.map (fun c => if c == ' ' then '_' else c)

/-- One attitude condition. `holder` is a term of the guard. `slot = some (s, t)`: the content's variable 0 has sort
    `s` and stands for the guard's term `t`; `slot = none`: the content is closed. -/
structure Cond where
  holder : VE.Term
  mode : Mode
  slot : Option (String × VE.Term)
  content : VE.Formula
  deriving DecidableEq, Repr

/-- W1's guard formulas with attitude conditions as atoms. -/
inductive AFormula where
  | base (φ : VE.Formula)
  | att (c : Cond)
  | not (a : AFormula)
  | and (a b : AFormula)
  | or (a b : AFormula)
  | implies (a b : AFormula)
  | all (s : String) (a : AFormula)
  | ex (s : String) (a : AFormula)
  deriving DecidableEq, Repr

/-- A W1 rule whose guard and carve-outs may carry attitude conditions (the fields of `VE.Norms.Node`). -/
structure ARule where
  name : String
  pred : String
  sign : Bool
  guard : AFormula
  carveOuts : List AFormula
  over : List String
  deriving DecidableEq, Repr

structure AttDoc where
  E : VE.Environment
  lits : List String
  regulated : List VE.Norms.Regulated
  definitions : List VE.Norms.Definition
  rules : List ARule
  /-- the holder sorts -/
  holders : List String
  /-- `table` plus the document's declared pairs between its own words -/
  scale : Scale
  /-- the decider of every generated open term; "unresolved_decider" when the document names none -/
  decidedBy : String

/-- What makes two conditions one attitude (D-A3): no hashing, syntax-tree equality of the content. -/
structure Key where
  mode : Mode
  holderSort : String
  slotSort : Option String
  content : VE.Formula
  deriving DecidableEq, Repr

def Key.sorts (k : Key) : List String := k.holderSort :: k.slotSort.toList

def Cond.key (A : AttDoc) (Γ : List String) (c : Cond) : Option Key :=
  match c.holder.sortOf A.E Γ with
  | some hs => if A.holders.contains hs then some ⟨c.mode, hs, c.slot.map (·.1), c.content⟩ else none
  | none => none

def AFormula.conds : List String → AFormula → List (List String × Cond)
  | _, .base _ => []
  | Γ, .att c => [(Γ, c)]
  | Γ, .not a => a.conds Γ
  | Γ, .and a b => a.conds Γ ++ b.conds Γ
  | Γ, .or a b => a.conds Γ ++ b.conds Γ
  | Γ, .implies a b => a.conds Γ ++ b.conds Γ
  | Γ, .all s a => a.conds (s :: Γ)
  | Γ, .ex s a => a.conds (s :: Γ)

/-- A rule's guard context: its predicate's sorts, the last argument as variable 0 (W1's `(sorts pred).reverse`). -/
def ruleContext (A : AttDoc) (r : ARule) : List String :=
  match A.regulated.find? (·.name == r.pred) with
  | some d => d.sorts.reverse
  | none => []

def condsOf (A : AttDoc) : List (List String × Cond) :=
  A.rules.flatMap (fun r => (r.guard :: r.carveOuts).flatMap (·.conds (ruleContext A r)))

def keys (A : AttDoc) : List Key := VE.Reports.dedup ((condsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)

/-- `E` plus one predicate per key, on the key's sorts. -/
def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

/-! ## Elaboration (3.3) -/

def atom (A : AttDoc) (k : Key) (h : VE.Term) : Option VE.Term → VE.Formula
  | none => .unary (name A k) h
  | some t => .binary (name A k) h t

def AFormula.elab (A : AttDoc) : List String → AFormula → Option VE.Formula
  | _, .base φ => some φ
  | Γ, .att c => (c.key A Γ).map (fun k => atom A k c.holder (c.slot.map (·.2)))
  | Γ, .not a => (a.elab A Γ).map .not
  | Γ, .and a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.and x))
  | Γ, .or a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.or x))
  | Γ, .implies a b => (a.elab A Γ).bind (fun x => (b.elab A Γ).map (.implies x))
  | Γ, .all s a => (a.elab A (s :: Γ)).map (.all s)
  | Γ, .ex s a => (a.elab A (s :: Γ)).map (.ex s)

def ARule.elab (A : AttDoc) (r : ARule) : Option VE.Norms.Node :=
  (r.guard.elab A (ruleContext A r)).bind (fun g =>
    (r.carveOuts.mapM (·.elab A (ruleContext A r))).map (fun cs => ⟨r.name, r.pred, r.sign, g, cs, r.over⟩))

/-- The elaborated W1 document over `envAtt A`. -/
def toNorms (A : AttDoc) : Option VE.Norms.Doc :=
  (A.rules.mapM (·.elab A)).map (fun ns => ⟨envAtt A, A.lits, ⟨A.regulated, A.definitions, ns⟩⟩)

/-- The base vocabulary (A2): `E` without the regulated and defined predicates. -/
def baseEnv (A : AttDoc) : VE.Environment :=
  VE.Norms.hide A.E (A.regulated.map (·.name) ++ A.definitions.map (·.name))

/-- The executable check (spec 4.1, bodies in the stub): every condition's key exists (a holder of a holder sort);
    its slot term has the slot's sort in its context; its content is `VE.Norms.Formula.qfree` (A5) and well formed
    over the base vocabulary `baseEnv A` (A2) in the slot's context (`[s]`, or `[]` when closed); `knows` is used
    only if `table.factive` is set, and every `thinks w` uses a word of `table`'s `lowerBound` (A1); every
    `A.scale.above` pair is between two such words and contains `table.above`, and the scale passes
    `Order.admit scaleCaps` (A5, edit 1); every base formula is well formed over `E`; generated names are undeclared
    in `E`, at most 64 bytes and pairwise distinct; `E`'s predicates plus the keys stay within
    `VE.Reports.maxPredicates`; every rule's predicate is regulated; `decidedBy` is non-empty; the document's English
    lexicon is valid and describes `E`, and every condition is one 3.7 can word: a slot mentioned by its content, a
    slot term that is a variable, a `wants` content with its one wording, every predicate and constant with its
    lexicon entry (SR-2, SR-3, RC-1). -/
def WellFormedAtt (A : AttDoc) : Bool := wellFormedBody A

/-- The guard-level part of `WellFormedAtt`, as a proposition over one formula in context `Γ`. -/
def AWellFormed (A : AttDoc) (Γ : List String) (a : AFormula) : Prop := aWellFormedBody A Γ a

/-! ## The frame (3.4) -/

/-- An attitude of mode `m` implies one of mode `m′` on the same subject (D-A4), read from the frozen table:
    premise 2 when E2 passed it; premise 3 per word, where that word's own E2 item passed (A1); premise 4 for the
    pairs of the scale. -/
def entailsMode (σ : Scale) : Mode → Mode → Bool
  | .knows, .act .believes => table.knowsBelieves.isSome
  | .knows, .thinks w => table.knowsThinks.any (fun p => σ.atLeast p.1 w)
  | .thinks w, .thinks w2 => w != w2 && σ.atLeast w w2
  | _, _ => false

def sameSubject (k k2 : Key) : Bool :=
  k.holderSort == k2.holderSort && k.slotSort == k2.slotSort && k.content == k2.content

def framePairs (A : AttDoc) : List (Key × Key) :=
  (keys A).flatMap (fun k =>
    ((keys A).filter (fun k2 => sameSubject k k2 && entailsMode A.scale k.mode k2.mode)).map (k, ·))

/-- `∀h. body` or `∀h ∀x. body`: the slot is variable 0, the holder variable 1 (or 0 when closed). -/
def closeOver (k : Key) (body : VE.Formula) : VE.Formula :=
  match k.slotSort with
  | none => .all k.holderSort body
  | some s => .all k.holderSort (.all s body)

def atomAt (A : AttDoc) (k : Key) : VE.Formula :=
  match k.slotSort with
  | none => .unary (name A k) (.var 0)
  | some _ => .binary (name A k) (.var 1) (.var 0)

/-- Frame premise 1. -/
def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

/-- Frame premises 2 to 4. -/
def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  ((keys A).filter (·.mode == .knows)).map (factive A) ++ (framePairs A).map (entails A)

def frameLabels (A : AttDoc) : List String :=
  ((keys A).filter (·.mode == .knows)).map (fun _ => "attitude:factive") ++
    (framePairs A).map (fun _ => "attitude:entails")

/-! ## Semantics (3.5), independent of `elab` -/

structure AttModel (A : AttDoc) where
  S : VE.Structure.{u}
  J : Key → List S.Carrier → Prop

/-- A key's content at a tuple: closed content at `[h]`, slot content at `[h, x]` with `x` as variable 0. -/
def contentAt (S : VE.Structure.{u}) (k : Key) : List S.Carrier → Prop
  | [_] => k.slotSort = none ∧ k.content.denote S []
  | [_, x] => k.slotSort.isSome ∧ k.content.denote S [x]
  | _ => False

/-- What the attitude words mean, and nothing more: typed relations, factive knowing, the frame pairs. -/
def Intended (A : AttDoc) (m : AttModel.{u} A) : Prop :=
  (∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) ∧
  (∀ k ∈ keys A, k.mode = .knows → ∀ vs, m.J k vs → contentAt m.S k vs) ∧
  (∀ p ∈ framePairs A, ∀ vs, m.J p.1 vs → m.J p.2 vs)

def AFormula.denote (A : AttDoc) (m : AttModel.{u} A) : List String → VE.Valuation m.S → AFormula → Prop
  | _, ρ, .base φ => φ.denote m.S ρ
  | Γ, ρ, .att c => ∃ k, c.key A Γ = some k ∧ ∃ vh, c.holder.denote m.S ρ = some vh ∧
      match c.slot with
      | none => m.J k [vh]
      | some (_, t) => ∃ vx, t.denote m.S ρ = some vx ∧ m.J k [vh, vx]
  | Γ, ρ, .not a => ¬ a.denote A m Γ ρ
  | Γ, ρ, .and a b => a.denote A m Γ ρ ∧ b.denote A m Γ ρ
  | Γ, ρ, .or a b => a.denote A m Γ ρ ∨ b.denote A m Γ ρ
  | Γ, ρ, .implies a b => a.denote A m Γ ρ → b.denote A m Γ ρ
  | Γ, ρ, .all s a => ∀ v, m.S.domain s v → a.denote A m (s :: Γ) (v :: ρ)
  | Γ, ρ, .ex s a => ∃ v, m.S.domain s v ∧ a.denote A m (s :: Γ) (v :: ρ)

/-- The structure over `envAtt A`: each generated name read as its key's relation. -/
def interp (A : AttDoc) (m : AttModel.{u} A) : VE.Structure.{u} :=
  { m.S with relation := fun r vs =>
      match keyOf A r with
      | some k => m.J k vs
      | none => m.S.relation r vs }

/-- An `envAtt A` structure read back as an attitude model. -/
def restrict (A : AttDoc) (T : VE.Structure.{u}) : AttModel.{u} A :=
  ⟨{ T with relation := fun r vs => keyOf A r = none ∧ T.relation r vs },
    fun k vs => k ∈ keys A ∧ T.relation (name A k) vs⟩

/-! ## Theorems (bodies in AT-1; statements reviewed in AT-0) -/

theorem names_fresh (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64
theorem names_injective (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2
theorem envAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (hφ : φ.WellFormed A.E Γ) : φ.WellFormed (envAtt A) Γ
theorem toNorms_isSome (A : AttDoc) (h : WellFormedAtt A = true) : (toNorms A).isSome = true
/-- Typed over the base vocabulary extended by the generated names (A2), the environment PK-1's typing asks for. -/
theorem frame_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (baseEnvAtt A) []
theorem frame_universalQF (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ

/-- Faithfulness, guards: the elaborated guard means what the attitude guard means. -/
theorem att_elaboration_faithful (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (Γ : List String) (ρ : VE.Valuation m.S) (hρ : VE.Valuation.Typed m.S Γ ρ)
    (a : AFormula) (ha : AWellFormed A Γ a) (φ : VE.Formula) (he : a.elab A Γ = some φ) :
    φ.denote (interp A m) ρ ↔ a.denote A m Γ ρ
/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
theorem frame_iff_intended (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) :
    VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m
/-- Model correspondence, both ways. -/
theorem interp_admissible (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hI : Intended A m) : (interp A m).Admissible (envAtt A)
theorem restrict_admissible (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) : (restrict A T).S.Admissible A.E
theorem interp_restrict (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (r : String) (vs : List T.Carrier) :
    (interp A (restrict A T)).relation r vs ↔ T.relation r vs
theorem old_formula_invariant (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A) (Γ : List String)
    (ρ : VE.Valuation m.S) (φ : VE.Formula) (hφ : φ.WellFormed A.E Γ) :
    φ.denote (interp A m) ρ ↔ φ.denote m.S ρ

/-- Conservativity (VISION rule 4). -/
theorem att_old_language_conservative (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed A.E []) (hφ : φ.WellFormed A.E []) :
    VE.Entails.{u} (envAtt A) (Γ ++ framePremises A) φ ↔ VE.Entails.{u} A.E Γ φ
/-- A document with no attitude condition: no key, no frame, the same environment. -/
theorem att_conservative_doc (A : AttDoc) (h0 : condsOf A = []) :
    keys A = [] ∧ framePremises A = [] ∧ envAtt A = A.E

/-- Frame premise 1 as a fact of every intended model. -/
theorem knows_factive (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode = .knows) (vs : List m.S.Carrier) (hJ : m.J k vs) : contentAt m.S k vs
/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content. No hypothesis
    about the content appears. -/
theorem mistaken_belief_admissible (A : AttDoc) (h : WellFormedAtt A = true) (S : VE.Structure.{u})
    (hS : S.Admissible A.E) (k : Key) (hk : k ∈ keys A) (hm : k.mode ≠ .knows) (vs : List S.Carrier)
    (hvs : VE.TupleTyped S k.sorts vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs
/-- The frame closure of a seed (F3, edit 2): `(k2, vs)` when a seed member `(k, vs)` reaches `k2` through frame
    pairs, the tuple preserved. `Relation.ReflTransGen` is not in the pinned Lean core; `Reachable .star` is QS-1's,
    with `reachable_star_iff` where a relation-level form is needed. -/
def seedClosure (A : AttDoc) {C : Type u} (seed : List (Key × List C)) (k2 : Key) (vs : List C) : Prop :=
  ∃ k, (k, vs) ∈ seed ∧ VE.Closure.Reachable .star (fun a b => (a, b) ∈ framePairs A) k k2
/-- Nothing beyond the frame: the closure of any finite typed seed whose `knows` members have true contents is
    intended, every intended model holding the seed holds it, so a seed forces exactly what frame pairs reach. -/
theorem seed_intended (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) : Intended A ⟨S, seedClosure A seed⟩
theorem seed_least (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (seed : List (Key × List m.S.Carrier))
    (hs : ∀ p ∈ seed, m.J p.1 p.2) : ∀ k vs, seedClosure A seed k vs → m.J k vs
theorem forced_iff_reachable (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) (k : Key) (vs : List S.Carrier) :
    (∀ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ → (∀ p ∈ seed, J p.1 p.2) → J k vs) ↔
      seedClosure A seed k vs
/-- R 5's collapse, repaired (A3): when a frame pair links the two keys, `(ck ∧ a) ∨ ct` is `ct`. -/
theorem guard_collapse (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (Γ : List String)
    (ρ : VE.Valuation m.S) (ck ct : Cond) (a : AFormula) (k kt : Key) (hk : ck.key A Γ = some k)
    (hkt : ct.key A Γ = some kt) (hp : (k, kt) ∈ framePairs A) (hh : ck.holder = ct.holder)
    (hsl : ck.slot.map (·.2) = ct.slot.map (·.2)) :
    AFormula.denote A m Γ ρ (.or (.and (.att ck) a) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct)
theorem framePairs_transitive (A : AttDoc) (k1 k2 k3 : Key)
    (h12 : (k1, k2) ∈ framePairs A) (h23 : (k2, k3) ∈ framePairs A) (hne : k1 ≠ k3) : (k1, k3) ∈ framePairs A
end VE.Attitudes
```

(`wellFormedBody` and `aWellFormedBody` stand for the bodies AT-0 writes in the stub from the conjuncts listed in
the docstring; `tableReviewedBody` for the closure review's. `atLeast_refl` and `atLeast_trans` are QS-1's (edit
1). The spec's statements of `contentAt`, `mistaken_belief_admissible` and the others above are AT-0's elaborated
versions. No comment above uses a word `lean/audit.py` forbids.)

Proof notes. Conservativity: extend by the empty attitude relations (every frame premise has a false antecedent);
the other direction restricts (`restrict_admissible`) and uses `old_formula_invariant`, which needs `names_fresh`.
`seed_intended`: no frame pair has a `knows` key as its target (`entailsMode`), so factivity is only needed of the
seed's own `knows` members; reachability is closed under one more frame pair, which gives the third conjunct; frame
pairs relate keys with the same sorts, which gives typing. `seed_least`: induction on the path. `forced_iff_reachable`
is the two together. `mistaken_belief_admissible` is `seed_intended` at the seed `[(k, vs)]`. `guard_collapse` is
the third conjunct of `Intended` at `hp`. `framePairs_transitive` uses QS-1's `atLeast_trans` (edit 1): a premise-3
word reached from an admitted word through the scale is itself reached from that word.

Fixtures (`Examples.lean`, `#guard` on executable checks over finite models; every theorem has one instance on F-AT1
or F-AT2, A3):

- **F-AT1 (u0165.s01 with u0173.s01; `intends` kept only as a fixture, F4).** `E`: sorts `claude_instance`, `situation`; base `mass_casualty_weapon_uplift
  (situation)`; regulated `weapons_uplift_permitted (claude_instance, situation)`, a permission, act "{0} do the
  weapons uplift in {1}". One rule, sign false, guard `or (and (att knows) (att intends)) (att (thinks "quite
  likely"))`, each condition with holder `var 1`, slot `("situation", var 0)`, content
  `unary "mass_casualty_weapon_uplift" (var 0)`. Expected: keys named `attitudes__knows__1`,
  `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`; two frame premises (`attitude:factive`,
  `attitude:entails` knows → thinks quite likely). One instance `c`, one situation `s`:
  - M1, category false, thinks true: frame holds, guard holds (the audit's case).
  - M2, category false, knows and thinks true: frame fails (factive).
  - M3, category true, knows true, thinks false: frame fails (entails).
  - M4, category true, no attitude: frame holds, guard fails (u0173.s04's unknowing contribution).
- **F-AT2 (two categories, u0165.s01 and u0165.s07).** Contents for two case atoms: six keys, `__1` and `__2` per
  mode, and no frame pair across contents (`forced_iff_reachable`'s instance).
- **F-AT3 (degree order).** A document using "very likely" and "quite likely" on one content with the declared pair
  ("very likely", "quite likely"): one `attitude:entails` premise in that direction, none in the other.
- **F-AT0 (conservative).** F-AT1 with the attitude conditions removed: no key, no frame, `envAtt = E`.
- **The closure review.** `table.reviewed` holds; a table whose closure derives a pair or a premise-3 word without
  its own item fails it.
- **The lexicon and the renderable subset (SR-2, SR-3, RC-1, RC-3).** Every fixture carries the spec's fixture
  lexicon, extended for D15's 240 predicates (RC-3). D6a, D6b and D14a–D14d each fail at their own check; the
  collision pairs C-a (`knows ⊤` closed and with an unused slot) and C-b (`C(s1)` closed and `C(var 0)` slotted at
  the constant `s1`), the `wants` pair C-c, and C-d (a constant and a predicate declared in `E` with no lexicon
  entry, refused at D14d) (spec section 7.1).

Deleted, not duplicated: draft 1's `qf` (A5) and `Scale.step` (edit 1). `Act`, `dedup` and content identity are
`reports@0`'s; the closure is QS-1's; the lexicon and its validity are the English grammar's; the `wants` test is
`reports@0`'s, moved by AT-1w (SR-3, RC-4).

Shared files: none hand-written. In-flight overlap: none (new directories). No Python copy of the `wants` test
remains: AT-1w deleted it (RC-4).

Bytes unlocked: 0 (nothing calls the code).

Done when: the files build with standard axioms only, the fixtures `#guard`, `lean/ATTITUDES.md` lists every theorem
in plain words, the audit passes, and the gate passes (no answer can change).

### AT-2. The layered route with the `attitudes` pack (Lean, 4–5 h)

Files: `lean/VE/Attitudes/Route.lean` and `RouteExamples.lean` (new). Generated as in AT-1. Hand-written shared
file: one provider registration line on `lean/VE/NormDefaults/Layered.lean` (PK-1's), first in PK-1's integration
order (AT-2/AT-3a → WG-3 → ET-4 → QT-B2; edit 7). Needs PK-1 merged, and so `rd-9-int`.

Edit 6 (overriding debate F5's mechanism, keeping its requirement): the frame is PK-1's `attitudes` pack, so the
`attitude:factive` and `attitude:entails` diagnostics reach the layered paths through PK-1's per-pack labels, with
every existing profile's layered output byte-identical. `FrameSource` and `frameSource_X` are replaced by one
statement, the pack's premises are `framePremises A`; `att_conflict_sound` is RD-9's `layered_conflict_sound` at
PK-1's assembled X; `settled_frame_agree` and `undecided_frame_agree` are stated with the assembled X (the frame plus
any other packs). The typing obligation is over the base vocabulary extended by the generated names (A2).

```lean
import VE.Attitudes.Theorems
import VE.NormDefaults.Layered

namespace VE.Attitudes
-- the opens of `VE/NormDefaults/Status.lean`, where `SettledAs` is stated, plus that namespace itself
open VE.Norms VE.Route VE.NormDefaults
open VE.NormDefaults.Wire (BaseAdmissibleX ConflictFreeX UndecidedAtX LayeredU)
universe u

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the bases that also satisfy `X` (the counterpart of `UndecidedAtX`, which exists). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((outcomeBase (fill U) r.name).denote (withFill U B F) (tupleVal vs) ↔ b = true)

/-- A premise that reads no `unsaid__` table of `U`. -/
def UnsaidFree (U : UDoc) (φ : VE.Formula) : Prop := ∀ p ∈ U.unspec, unsaidName p ∉ preds φ
/-- At a base satisfying the assembled X, when X reads no unsaid table, SETTLED with and without X agree. -/
theorem settled_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAs U B r vs b ↔ SettledAsX U X B r vs b
theorem undecided_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) :
    UndecidedAt U B r vs ↔ UndecidedAtX U X B r vs
/-- `hw` is needed (SR-1): a base predicate named `unsaid__<p>` in a `knows` content otherwise puts that name into
    a factive premise. -/
theorem frame_unsaidFree (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : WellFormedU U = true) : ∀ φ ∈ framePremises A, UnsaidFree U φ
/-- The `attitudes` pack (edit 6). -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .vocabulary, decls := (keys A).map (fun k => (name A k, k.sorts)),
    labelled := (frameLabels A).zip (framePremises A), origins := origins A }
/-- The `attitudes` pack's premises are `framePremises A` (replaces `FrameSource` and `frameSource_X`). -/
theorem attitudesPack_premises (A : AttDoc) (h : WellFormedAtt A = true) :
    (attitudesPack A).labelled.map (·.2) = framePremises A ∧ (attitudesPack A).labelled.map (·.1) = frameLabels A
/-- PK-1's typing obligation for this provider (A2). -/
theorem frame_typed_fill (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : WellFormedU U = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (envAt (fill U) 0) []
/-- PK-1's expansion step for a `vocabulary` pack: empty attitude relations satisfy every frame premise. -/
theorem empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) :
    Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A)
end VE.Attitudes
```

(`origins A` maps each key and frame label to its full request occurrence: holder term, mode, content, slot,
enclosing rule and guard location (A6, edit 6); AT-3a fixes the paths. `att_conflict_sound` is no new theorem: it
is `layered_conflict_sound` at PK-1's assembled X. Draft 1's `mistaken_belief_settled` and its placeholder
`decidesAt` become the fixture below, through `settled_of_table3` and `settledX_of_settled`.)

Fixtures (`RouteExamples.lean`): F-AT1's points through the layered route's status kind with the X check: M1 SETTLED
no; M4 UNDECIDED; M2 and M3 refused with PK-1's diagnostic naming the pack's first failing label
(`attitude:factive…`, `attitude:entails…`). F-AT1 is conflict-free under the assembled X. F-AT8 (SR-1): a base
predicate `unsaid__weapons_uplift_permitted` in a `knows` content, with `weapons_uplift_permitted` unspecified,
passes `checkAtt` but not `WellFormedU`, so `frame_unsaidFree` needs `hw`.

Deleted, not duplicated: no second status or conflict semantics; `SettledAsX` is the one missing counterpart of
`UndecidedAtX` and is defined from the same parts.

Shared files: the one provider registration line on `Layered.lean` above. In-flight overlap: `rd-9-int` and PK-1
edit norm-defaults files; this batch starts after both merge.

Bytes: 0.

Done when: builds, audit passes, fixtures `#guard`, `lean/ATTITUDES.md` updated, gate passes.

### AT-3a. Wire: the guard-node hook and the layered kinds (Lean, 5–6 h)

Edit 7: there is no `attitudes` service mode.

- **Decoding.** Attitude guard nodes (the wire below, unchanged) are decoded, when `attitudes@0` is on, by the
  chain's norm decoders: W1's `VE.Norms.Wire.decodeNorm` and soft's `VE.SoftNorms.Wire.decodeSoftNorm`.
  `VE.Readings.Wire.decodeNorm` (`Readings/Wire.lean:119–124`) and the layered decoder dispatch to them, so one
  guard-node hook serves the norms, soft, layered and readings routes. The `environment.attitudes` block (holders,
  scale, decider) is decoded by the `attitudes` pack provider. AT-0 pins the exact hook point and confirms that no
  second guard decoder remains. On `lean/VE/Norms/Wire.lean` the edit is serialised after act-phrases' AP-1 and
  AP-3. The generated keys and frame go to the `attitudes` pack. This is the decoder scope's SC-2 depends on: scope
  substitutes a rule's guard JSON for `own` inside a condition that may contain attitude nodes, then calls this
  decoder. Without `attitudes@0`, W1's, soft's and P0's decoders are unchanged: an attitude node gets today's answer
  (`array expected`) in today's fault order, and the new text `UnsupportedProfile: an attitude condition needs
  attitudes@0` is answered only by `decodeAttDoc` (SR-6; spec 5.1).
- **The attitudes kinds' decoder.** `decodeAttDoc` decodes the document, the `environment.attitudes` block and the
  case's English lexical data (`lexicon`, optional `overlay`), the last with the English grammar's own decoders
  (`Env.decode`, `Overlay.decode`, `Run.decodeLexicon`), here and not only in AT-5, because `attitudes-elaborate`
  answers a wording template per key (SR-3). Its last step is `checkAtt`, so it returns only checked documents
  (`decodeAttDoc_wellFormed`, SR-7); otherwise the first failing check's diagnostic is the kind's answer.
- **Kinds.** `attitudes-elaborate` becomes a kind of the layered route; `attitudes-status`, `attitudes-conflict` and
  `attitudes-report` are the layered route's own status, conflict and report kinds over the assembled X. Checking
  the frame on a point's model is the layered status kind's check that the point satisfies every X premise; AT-0
  confirms the kind performs that check, and if it does not, the check is added once in PK-1 for all packs.
  `attitudes_wire_acceptance` and `attitudes_status_sound` are restated for these kinds. The kind's shape and
  encoder theorem go into the layered route's response-shape files.
- **Registration.** `attitudes@0` is one row of AR-10's profile-gate table with its composition proof. There is no
  hand edit to `ve/profiles.py`.
- **Dependencies.** AT-3a also waits for PK-1 (and so `rd-9-int`) and AR-10's table. AT-2/AT-3a is first in the
  integration order on `Layered.lean` (AT-2/AT-3a → WG-3 → ET-4 → QT-B2); its position inside X is still PK-1's
  fixed order: after weighing, before scales.

Files (new): `lean/VE/Attitudes/Wire.lean` (decoder of the `attitudes` environment block as the pack provider, the
guard-node hook's attitude case, elaboration of the environment and norms JSON). The layered kinds live in the
layered route's run and response-shape files.

Wire (structured content; JSON never carries `null`):

```text
environment.attitudes = { "holders": [sort, …], "scale": [[word, word], …], "decided_by": token }
guard node             = { "attitude": { "holder": term, "mode": "knows" | "thinks" | "believes" | "wants"
                           | "intends" | "says", "degree": word (only with "thinks"),
                           "slot": { "sort": sort, "term": term } (optional), "content": formula } }
case.lexicon           = the English grammar's lexicon export ("ve.english-lexicon@1"); case.overlay optional (SR-3)
```

`attitudes-elaborate` answers the generated predicates (name, sorts, key, wording template, open-term record), the
frame (label, formula), each key's and label's request origin, and the elaborated guards; `attitudes-status`
answers a point's status with every X premise checked on the model first; `attitudes-conflict` and
`attitudes-report` are the layered route's over the assembled X.

Statements (restated for the layered kinds, edit 7):

```lean
namespace VE.Attitudes.Wire
/-- The decoder ends with `checkAtt` (SR-7): a decoded document is well formed, its lexicon included. -/
theorem decodeAttDoc_wellFormed (j : Lean.Json) (A : AttDoc) (hd : decodeAttDoc j = .ok A) :
    WellFormedAtt A = true
/-- The answer is exactly the encoding of the elaboration of the case's own decoded document. -/
theorem attitudes_elaborate_acceptance (j : Lean.Json) (A : AttDoc) (hd : decodeAttDoc j = .ok A)
    (L : VE.NormDefaults.Wire.LayeredU) (hL : VE.NormDefaults.Wire.decodeLayered j = .ok L) (id : String) :
    VE.NormDefaults.Wire.layeredCase L id "attitudes-elaborate" j =
      .ok (some (VE.Route.Wire.ok id (encodeElaboration A)))
/-- A replayed status point satisfies the frame; SETTLED and UNDECIDED hold over the assembled X; UNKNOWN claims
    nothing. -/
theorem attitudes_status_sound (j : Lean.Json) (L : VE.NormDefaults.Wire.LayeredU)
    (d : VE.NormDefaults.Wire.StatusX L) (hr : VE.NormDefaults.Wire.replayStatusX L j = .ok d) :
    Sat d.S.M.asStructure (VE.NormDefaults.Packs.packPremises L "attitudes") ∧
    (∀ b, d.status = .settled b → SettledAsX.{0} L.U L.X d.S.M.asStructure d.r d.vs b) ∧
    (d.status = .undecided → VE.NormDefaults.Wire.UndecidedAtX.{0} L.U L.X d.S.M.asStructure d.r d.vs)
end VE.Attitudes.Wire
```

(`packPremises` stands for PK-1's accessor of one pack's premises in a decoded `LayeredU`. The existing
`ResponseShape.Encoders.NormDefaults.runCaseReported_fits` keeps its statement; its skeleton gains the new kinds'
rows.)

Fixtures: F-AT1 as wire cases, each kind, with the fixture lexicon; malformed cases (an attitude node without
`attitudes@0` on the attitudes kinds, unknown mode, `degree` on a non-`thinks` mode, a slot term of the wrong sort, a
holder of a non-holder sort, a content with a quantifier, a generated name over 64 bytes, a missing `lexicon`)
refused with their diagnostic in the spec's order; F-AT1 with one change per check of spec 5.2 (D1, D6a, D6b, D9,
D14a, D14b, D14c, D14d, D18) answering that check's diagnostic, not an elaboration (SR-7). Compatibility (SR-6): on
W1's, soft's and P0's routes with `attitudes@0` off, malformed and well-formed attitude objects, and documents pairing
an attitude node with an earlier or a later fault, answer byte for byte what `main` answered before the hook (recorded
first; `array expected` at `49de179e`). On W1's route a document pairing an unknown predicate with an attitude node
answers `array expected` in both orders, since `decodeSource` decodes every rule before `validate` raises the
unknown predicate (spec 7.6, RC-2).

Deleted from draft 1 (edit 7): the `Protocol.lean` mode constructor, its name, the `modes` entry, the `runMode` case
and `VE.Service.runMode_attitudes`; the `MODES` entry in `ve/backends/service_schema.py`; the generated
`attitudes.json`; `lean/VE/Attitudes/Run.lean`, `ResponseShape/Schemas/Attitudes.lean` and
`ResponseShape/Encoders/Attitudes.lean`.

Shared hand-written files: `lean/VE/Norms/Wire.lean` (the guard-node hook, after AP-1 and AP-3), the soft norm
decoder's matching hook, the layered route's kind table and response-shape files (PK-1's), the AR-10 table row,
`ve/assurance-manifest.json` (pins of the new JSON decoder, reviewed by hand), `conformance/binding_probes.py`
(`BUILDERS`: a probe for the new binding), `ROADMAP.md` (the trust-cost line, VISION rule 4). Generated:
`lean/ResponseShape.lean`, `lean/ResponseShape/Audit.lean`, the layered route's response schema,
`docs/spec/assurance-manifest.md`, `lean/checkers.lock`, `docs/trust-baseline.json` (growth needs
`trust_map.py --write --reason` and a DRI signature, ruling D3), AR-10's generated profile data.

In-flight overlap: `lf-16e` and `qa-q2` both edit the service's kinds and schemas; start after both merge.
`fix-main-relay` touches `service_schema.py`; after it merges.

Bytes: 0.

### AT-3b. Relay, document hook and tests (Python, 4–5 h)

Files (new): `ve/attitudes.py` (sends the layered route's attitudes kinds with `rows` from `ve/backends/relay.py`,
each case with the document's English lexicon export (`ve.english-lexicon@1`) and overlay, which Lean decodes and
validates (SR-3);
binds the answer to the request, A6: an answer's generated environment cannot authenticate itself, so each
generated key is bound to a request condition by its request path, the full occurrence: holder term, mode, content
tree, slot term, enclosing rule and guard location; each frame premise is bound to answer keys, and each label to
its premise's mode; every rule id and unit id names one in the request; no row is empty or extra; anything else is
`CheckerUnavailable`. Python checks provenance and field identity only, without reconstructing Lean's frame
semantics), `tests/test_attitudes_lean.py` (the route's own documents: F-AT1 to F-AT3 and the seven hard
constraints), `tests/test_attitudes_answer.py` (fuzz: each member of a genuine answer dropped, emptied, retyped,
duplicated or reordered, an index pushed out of range, one and two faults at a time; and swaps between valid entries
of the same type, such as two keys' holders, two keys' request paths or two labels; every mutant is
`CheckerUnavailable` or changes nothing shown).

Shared hand-written files: the `ve document` dispatch (Python `ve/document*.py` today; Lean's `document` mode if
`lf-16e` has moved it, as AT-0 records), `tools/layer_policy.py` (the layer of `ve/attitudes.py`). Generated:
`tests/data/route-cases.jsonl` (recorded by `tests/route_case_recorder.py`), `.importlinter`
(`tools/check_python_layers.py --write`), `tools/gate-collection.json`.

Seeded bug (Python is the only language this batch changes; recorded with file and failing test): the binding check
that a label names its premise's mode accepts any label; `tests/test_attitudes_answer.py` must fail, then the check
is restored.

In-flight overlap: `lf-16e` (document dispatch). AT-3b's document-dispatch edit is first in the document-mode queue
after `lf-16g`: AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10 (edit 7).

Bytes: 0 by itself; AT-6a measures.

### AT-6a. Pilot: the strict companion with typed attitudes (pilot tooling, 3 h)

In `readings/all-strict.ve.md`, replace AT-0p's fourteen open terms with attitude conditions (D2's guard) and seven
hand-named intention terms ("…intentionally does the weapons uplift in that situation", F4), declare `attitudes@0`
and `environment.attitudes = {"holders": ["claude_instance"], "scale": [], "decided_by": "unresolved_decider"}`; the
cases carry the companion's English lexicon, as AT-3a's decoder requires (SR-3).
Re-run the unspecified probe and the conflict check. Report, measured: the points of the seven rules (expected: the
audit's case SETTLED no; unknowing UNDECIDED; impossible points refused, where AT-0p measured UNDECIDED, P1 2 A4),
the open terms (expected 21 for the seven rules: 14 generated, 7 hand-named; the companion from AT-0p's measured 44
to **about** 51), predicates used, time (one run, not a comparison), `DELTA` against AT-0p's run. No model calls. The
main translation is unchanged until AT-6b. The report says it checks structured input, not English: the zero-training
claim is accepted only after AT-5 and an audit of the English Lean renders (debate round 3).

Queue (edit 10): AT-6a's edits to the seven units land after SC-2 and start from the translation as SC-2 left it.
Where SC-2 has moved AT-0p's open terms into the u0173.s01 governor's condition, AT-6a replaces them there, with
`own` as the attitude content, not in the seven item guards.

Bytes (**estimate**): 0 claimed; the typed form of 874 B on the companion.

**DRI go/no-go** (F7). After AT-6a, the DRI decides whether AT-4, AT-6b and AT-5 proceed, on AT-6a's measured
results and the next audit's verdict on AT-0p's seven units.

### AT-4. The readings chain with the `attitudes` pack (Lean and Python, 5–6 h)

Files: `lean/VE/Attitudes/Readings.lean` (new); `ve/readings.py` passes the `attitudes` block through only. The
readings decoder's call reduces to the `attitudes` pack provider's registration plus the shared guard-node hook
(edit 7). `transfers_append` is PK-1's (edit 6); `frame_transfers` stays as attitudes' provider obligation, with its
typing hypothesis discharged by a proved typing lemma instead of assumed (A2); `att_nd_superpose_*` are stated at the
assembled family, the frame at its `packOrder` place between the earlier packs `P` and the later packs `R`.

```lean
import VE.Attitudes.Route
import VE.Readings.SupExtra

namespace VE.Readings
-- the opens of `VE/Readings/SupExtra.lean`
open VE.Rights (RightsDoc correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

/-- Frame typing over any environment extending the frame's own vocabulary (A2: proved, not assumed). -/
theorem frame_shared (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true) (E' : VE.Environment)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) E') : ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed E' []
/-- The frame is over the shared base vocabulary (generated names are fresh, not choice symbols), so every choice
    reads it unchanged. -/
theorem frame_transfers (N : NDoc) (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true)
    (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N))) :
    Transfers.{u} (fillDoc N) (VE.Attitudes.framePremises Att) (fun _ => VE.Attitudes.framePremises Att)
theorem att_nd_superpose_conflict_free (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R') (A : Choice) (hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
    ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R) ↔
      ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
        ConflictFreeP.{u} (correlate (choiceDoc (fillDoc N) c).1)
          (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c)
end VE.Readings
```

(`attQ N Att P R := fillPremises (supU N) ++ (P ++ (framePremises Att ++ R))` and `attQ'` its per-choice
counterpart; `EnvExtends E E'` says `E`'s sorts, constants and predicates are declared alike in `E'`.)
`att_nd_superpose_all` and `att_nd_superpose_countermodel` follow `superpose_all_extra` and
`superpose_countermodel_extra` at the same family (written out in the spec); the enumerated route checks each choice
with the assembled X in its base premises. Every existing readings fixture answers byte-identically (the existing
theorems are the `Att` without conditions, `att_conservative_doc`).

Shared hand-written files: the pack provider's registration on the readings route, `ve/readings.py`
(pass-through). Generated: as AT-1, plus recorded route cases.

In-flight overlap: `lf-14d` (reading plans and verdicts move to Lean; `ve/readings.py` becomes a relay), `rd-9-int`
(soft norms with reading sets), `lf-16e` (Lean document mode for `readings@1`). Start after all three merge.

Bytes: 0 by itself; AT-6b measures.

### AT-6b. Pilot: the main translation with typed attitudes (pilot tooling, 3 h)

The same change as AT-6a in `translation.ve.md` (three "should" reading sets, superposed route). Report, measured:
conflict status over the eight choices; the denial and claim-to-be-human conclusions (expected unchanged); the seven
rules' points; open terms; predicates; the companion probe's decided units. Ask the next audit to sample the seven
units. If the scope design has landed, u0173.s01 is attached to the seven rules and claimed (263 B, **estimate**).
The "intentionally" readings are faithful only through the act-performance bridge (ET-D2); until then, AT-6b
reports them as residual (edit 3). Queue: as AT-6a (edit 10).

### AT-5. English in Lean (Lean and Python, 5–6 h)

Files: `lean/VE/Attribution/Words.lean` (new: the four report verbs and synonyms, with the reasons now in
`ve/report_english.py`; `reports@0`'s English does not depend on the newer profile, F6), `lean/VE/Attitudes/Words.lean`
(new: imports it and adds only `knows` and `thinks`), `lean/VE/Attitudes/English.lean` (new: wording templates for
generated predicates, composed from the content predicate's own template; the frame lines; the glossary line of
each degree word), the Lean English grammar's admission of the 3.7 rows (files in `lean/VE/EnglishGrammar/` that
AT-0 names). AT-5's refusals (`NegatedFactive`, `NegRaising`, bare "thinks that", `AttitudeAdverb`, an unresolved
holder) and their rewrites are rows in english-lean's catalogue, each with its category and its candidate readings
(SR-5); AT-5 adds no separate refusal table (edit 9). `lean/VE/Attribution/Words.lean` exists from AT-1w (with
`wantsPhrase?`); AT-5 adds the verbs to it. Every renderer and reader reads the document's own lexicon (`A.lex`) and
calls the English grammar's lexicon functions and `wantsPhrase?`, with no template classifier of its own (SR-3).
Whole-sentence fixtures (A4): `readRuleAll` of the 3.1 sentence and of each of the seven pilot guards has length 1;
round-trip of conditions alone is not enough.

```lean
namespace VE.Attitudes
/-- Rendering then reading an admitted attitude condition gives it back, under the document's own lexicon (SR-2). -/
theorem att_english_roundtrip (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : (Γ, c) ∈ condsOf A) : readCond A Γ (renderCond A Γ c) = .ok c
/-- Two admitted conditions of one document and context with one sentence are one condition (SR-2). -/
theorem renderCond_injective (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c c2 : Cond)
    (hc : (Γ, c) ∈ condsOf A) (hc2 : (Γ, c2) ∈ condsOf A) (he : renderCond A Γ c = renderCond A Γ c2) : c = c2
/-- Each refused form of 3.7 with rewrites, at its category and in its context (SR-4, SR-5): refused with its code;
    each rewrite has exactly one reading; the rewrites' readings are exactly the row's candidates; the candidates
    are pairwise distinct. -/
theorem refused_have_rewrites (A : AttDoc) (h : WellFormedAtt A = true) (site : Site) (s : String) (r : Refusal)
    (hr : refusalOf A site s = some r) :
    2 ≤ r.rewrites.length ∧
      match site, r.candidates with
      | .guard Γ, .guards cs =>
          readGuard A Γ s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readGuardAll A Γ s2).length = 1) ∧
            r.rewrites.flatMap (readGuardAll A Γ) = cs ∧ cs.Nodup
      | .rule, .rules cs =>
          readRule A s = .error r.code ∧ (∀ s2 ∈ r.rewrites, (readRuleAll A s2).length = 1) ∧
            r.rewrites.flatMap (readRuleAll A) = cs ∧ cs.Nodup
      | _, _ => False
end VE.Attitudes
```

(`renderCond`, `readCond` (atomic conditions only), `readGuard`, `readGuardAll` (a guard or carve-out in its
enclosing rule's context), `readRule`, `readRuleAll` (a whole rule), `refusalOf`, `Site`, `Candidates` and
`Refusal` (a code, its candidate readings and its rewrites) are the batch's new definitions, as the spec's section
6.5 writes them; each `…All` lists every derivation, as the all-derivations gate does.)

Deleted: `_VERBS`, `_SYNONYMS` and `_REJECTED` in `ve/report_english.py`; it reads the exported table instead. No
second verb table remains. The `wants` test is not touched here: AT-1w moved it and deleted its Python copy (RC-4).

Shared files: the English grammar files; the export's generator (the `english-codes` entry if its format can carry
the table, else a new `attitude-words` entry in `tools/regen_generated.py`, which is hand-written); the generated
`lean/VE/EnglishGrammar/Fixed/*.lean` and `ve/english_grammar/LOCK.json`, whose generator refuses a changed hashed
file without a new `--actions-version` (a person decides).

In-flight overlap: `qa-q2` (Lean-rendered English answers). Start after it merges. AT-5 is first in the
`lean/VE/EnglishGrammar/*` queue (`AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7`); QT-E does not gate AT-5 (edit 9).

Bytes: 0; makes the 3.1 sentences writable in English. The zero-training claim is accepted only after AT-5 and an
audit of the English Lean renders.

### AT-7. Nested conditions and "knows whether" (Lean, 5–6 h)

Two levels: a content may mention a generated level-1 atom (an attitude of someone named by a constant or by the
slot), so "the user says that the user intends to harm" (u0149.s03) and "a user who wants to know whether they are
talking to a human" (u0080.s04) elaborate in two rounds. "X knows whether P" is sugar for "X knows that P or X knows
that it is not the case that P", one reading. The frame is generated per level; every premise stays first-order and
universal.

```lean
namespace VE.Attitudes
/-- Two-level documents: level-2 contents are formulas over `envAtt` of level 1. Conservative over level 1. -/
theorem nested_conservative (A : AttDoc2) (h : WellFormedAtt2 A = true) (Γ : List VE.Formula) (φ : VE.Formula)
    (hΓ : ∀ a ∈ Γ, a.WellFormed (envAtt A.lower) []) (hφ : φ.WellFormed (envAtt A.lower) []) :
    VE.Entails.{u} (envAtt2 A) (Γ ++ framePremises2 A) φ ↔
      VE.Entails.{u} (envAtt A.lower) (Γ ++ framePremises A.lower) φ
/-- A nested attitude is free unless the frame relates it: saying that one intends implies nothing about intending. -/
theorem says_not_intends (A : AttDoc2) (h : WellFormedAtt2 A = true) : NestedIndependent A
end VE.Attitudes
```

(`AttDoc2`, `WellFormedAtt2`, `envAtt2`, `framePremises2` and `NestedIndependent` are the batch's new definitions:
`AttDoc2` is an `AttDoc` for level 1, `lower`, and the level-2 conditions over `envAtt lower`.)

Profile: `attitudes@1` (a new version admits more documents; `attitudes@0` documents keep their meaning,
`nested_conservative` at level 1 alone). Bytes: 0 now; up to 1,070 B over seven units when their co-blockers land
(**estimate**). Shared files: none beyond AT-3a's (the decoder gains a field). Needs AT-4.

### E3. "We want Claude to X" (experiment, 3 h)

Pre-registered. Sample 40 of the 183 author-attitude units (R 2.4) with `random.Random("attitudes-E3")` over the
unit ids sorted. Readers as E1, each shown the sentence with its paragraph, asked: "Does this sentence (a) only say
what Anthropic wants, (b) tell Claude what to do, or (c) both?". One independent audit of the same 40.

- If at least 32 of 40 readers choose (b) or (c) on at least 30 units, AT-8 records such units as a reading set
  {report; report and soft rule}, with the IDE showing both. If at most 8 of 40 do, AT-8 records the report alone.
  Otherwise each unit is a reading set.
- Nothing about the soft rule's force is concluded (weighing owns it).

### AT-8. `reports@0` units in norm documents (Lean and Python, 5–6 h)

Top-level report units beside rules: the attitudes route decodes them with `reports@0`'s own decoder and adds their
signed premises `VE.Reports.premises` to the document's asserted premises. No `reports@0` statement changes: the
gate `reports_gate_sound` stays as it is, and the combination is admitted only on the attitudes route.

```lean
namespace VE.Attitudes
/-- Report premises in a norm document change old-language consequence by exactly their forced disequalities
    (`VE.Reports.reports_no_leak`), and the rules' statuses not at all when no guard mentions a report key. -/
theorem reports_in_norms_conservative (A : AttDoc) (D : VE.Reports.ReportDoc)
    (hD : VE.Reports.WellFormedReports D = true) (hsep : ReportKeysUnused A D) (U : VE.NormDefaults.UDoc)
    (hU : toU A U.unspec = some U) (B : VE.Structure.{u}) (r : VE.Norms.Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAsX U (framePremises A) B r vs b ↔ SettledAsX U (framePremises A ++ VE.Reports.premises D) (expandR D B) r vs b
end VE.Attitudes
```

(`ReportKeysUnused` and `expandR` are this batch's: no guard mentions a report predicate, and the expansion of a base
with report relations.) Owner: the composition attribution.md 11.3 defers; DRI decision with the attribution owners
before build, so that one owner remains. Bytes (**estimate**): upper bound about 31 kB over the 183 units (183 × 169
B); the expected gain is far lower and depends on E3 and on the contents' own features.

### AT-9. Numeric bands on the scale (Lean, 3–4 h, on risk stage B's trigger)

`Scale` gains optional declared ranges per word; a declared range orders words it covers (a range wholly above
another implies the pair). Risk stage B reads its bands from `VE.Attitudes.Scale` instead of declaring its own.
Theorem: `bands_order_sound` (a declared pair agrees with the ranges). Bytes: 0 on the pinned pilots.

### E4. Claims as objects for honesty norms (experiment, 4–5 h)

Pre-registered. A stub profile with a sort of claims, one constant per content the document names, and a generated
`holds_<claim>` table restricted to first-order contents over `E` (no claim about a claim, so no self-reference).
Formalise 12 honesty units (u0112.s01 to s07, u0113.s02, u0114.s03, u0115.s01, u0118.s01, u0120.s04) in the stub.

- Success bar: the stub's conservativity statement elaborates; an independent audit finds at least 8 of 12 faithful;
  no unit needs a claim about a claim. Then a profile plan follows.
- Failure: the honesty section stays UNFORMALISED for this reason, recorded in the ledger.
- Opportunity: part of the 13,379-byte honesty section (R 2.4), co-blocked by speech acts and causation.

## 5. Dependencies and merge conflicts

| Batch | Waits for | Hand-written shared files | Generated files (regenerate) |
|---|---|---|---|
| AT-0p | — (measured in phase 1; lands with the pilot's next constitution run, section 9) | (pilot directory only); first in the hard-constraint queue `AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5` (edit 10) | — |
| E1, E2 | the DRI's confirmation of G1–G6 and authorisation of 2,480 model calls (section 9) | none (research scripts and evidence under `research/attitudes/`, `docs/research/evidence/attitudes/`) | — |
| AT-1w | AT-0 | `lean/VE/Attribution/Run.lean` (one `reports` kind), `lean/ResponseShape/Schemas/Reports.lean`, `lean/ResponseShape/Encoders/Reports.lean` (skeleton row), `ve/reports_route.py`, `ve/reports.py`, `ve/report_english.py` (`lean/VE/Attribution/Words.lean` is new here, with `wantsPhrase?` only; SR-3, RC-4) | `reports.json`, route cases, as AT-1 |
| AT-1 | AT-1w; QS-1 (edit 1) | none | `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements |
| AT-2 | AT-1; PK-1 (after `rd-9-int`) | one provider registration line on `lean/VE/NormDefaults/Layered.lean`, first in PK-1's integration order AT-2/AT-3a → WG-3 → ET-4 → QT-B2 | as AT-1 |
| AT-3a | AT-2; PK-1; AR-10's table; `lf-16e`, `qa-q2`, `fix-main-relay`; on `lean/VE/Norms/Wire.lean` after AP-1 and AP-3 | `lean/VE/Norms/Wire.lean` and the soft norm decoder (the guard-node hook), the layered route's kind table and response-shape files, the AR-10 row, `ve/assurance-manifest.json`, `conformance/binding_probes.py`, `ROADMAP.md` | layered response schema, `ResponseShape` roots and audit, assurance doc, checker pins, trust baseline (signed), AR-10's profile data |
| AT-3b | AT-3a; `lf-16e`; first in the document-mode queue after `lf-16g` (AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10) | document dispatch (Python or Lean), `tools/layer_policy.py` | route cases, `.importlinter`, gate collection |
| AT-6a, AT-6b | AT-3b (AT-6a); AT-4 (AT-6b); SC-2 in the hard-constraint queue | (pilot directory only) | — |
| AT-4 | the DRI's "go"; `lf-14d`, `rd-9-int`, `lf-16e`; PK-1 | the pack provider's readings registration, `ve/readings.py` | as AT-1, route cases |
| AT-5 | the DRI's "go"; AT-3b; `qa-q2`; first in the English queue `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` | `lean/VE/Attribution/Words.lean` (AT-1w's, gains the verbs, F6), English grammar files, english-lean's catalogue rows, `ve/report_english.py`, possibly `tools/regen_generated.py` | English grammar lock (needs a person's `--actions-version`), codes |
| AT-7 | AT-4 | AT-3a's decoder (own file) | as AT-1 |
| AT-8 | E3; DRI decision | AT-3a's decoder (own file), `ve/attitudes.py` | as AT-1 |
| AT-9 | risk stage B trigger | `lean/VE/Attitudes/Scale.lean` (own), risk stage B's files | as AT-1 |

How conflicts are avoided: every Lean batch writes new files under `lean/VE/Attitudes/`; the hand-written shared
Lean files are the guard-node hook on `lean/VE/Norms/Wire.lean` and the soft norm decoder (serialised after AP-1 and
AP-3), one provider line on PK-1's `Layered.lean` (in PK-1's integration order), the layered route's kind table, the
AR-10 row, `lean/VE/Attribution/Words.lean` (new in AT-1w, extended in AT-5), and AT-1w's `reports` kind with its
shape, relay and `ve/report_english.py` (the `reports@0` files). The seven pilot units change in
the hard-constraint queue's order, each step starting from the translation as the previous step left it. Generated
inventories are never hand-edited or hand-merged (ruling R12; `tools/regen_generated.py --resolve` finishes a merge
whose only conflicts are generated). Overlap is checked before each batch with `git diff --name-only
main...<branch>` against the in-flight branches named above. Landing preference: AT lands after AP and before
SC-1/SC-2 (SC-2 needs AT-3a's decoder; edit 10).

Sibling designs: **scope** (u0173.s01 attached to the seven rules, needed for its 263 B), **events-time-causation**
(the act-performance bridge, ET-D2); act-phrases supplies act identity only (edit 3), **weighing** (u0173.s02's
"more holistic and nuanced prioritization", u0145.s05), **quantities** (vague degrees other than likelihood,
"serious uplift"; this plan's scale covers likelihood words only), **events-time-causation** (u0173.s04's
"contributing", "deceive into thinking").

## 6. Expected effect per batch

AT-0p's row is **measured** (phase 1, P1 2), except its audit-verifiable bytes, which wait on A8; every other row is
an **estimate** until its pilot batch measures it.

| Batch | Claimed bytes | Audit-verifiable bytes | Answers |
|---|---:|---:|---|
| AT-0p (measured) | 0 new; 2,951 unchanged | 874 (7 units) if the next audit accepts them (A8, DEFERRED) | 7 audit-case points UNDECIDED → SETTLED no; open terms 33 → 46 (companion 44); the 7 impossible points stay UNDECIDED |
| AT-0 to AT-3b | 0 | 0 | none (no pilot uses them yet) |
| AT-6a | 0 | 874 typed (companion) | impossible points refused (AT-0p: UNDECIDED); open terms in the main translation 46 → 53 at AT-6b, the companion 44 → 51 (21 for the seven rules: 14 generated, 7 hand-named), counted from AT-0p's measured terms; SC-1b and SC-2 land in between (edit 10) and may change the starting counts |
| AT-4 + AT-6b | 0, or 263 with the scope design | 874 typed (main) | the "intentionally" readings stay residual until the act-performance bridge (edit 3); with premise 3, `guard_collapse` shows the guard's verdicts do not depend on the hand-named intention term |
| AT-5 | 0 | 0 | the sentences of 3.1 writable in English |
| AT-7 | 0 now; up to 1,070 | — | — |
| AT-8 | 0 until E3; upper ≈ 31 kB | — | — |
| AT-9 | 0 | — | — |
| E4 | research | — | part of 13,379 B (section) |

NORTH-STAR row 8 (0.1920 from tags) recomputed on this basis: the buildable part's upper bound is about 0.036
(5 × 1,333 / 184,893; R 2.8).

## 7. Not claimed, open questions, risks

- **Not claimed:** that Claude knows or thinks anything in any case; any threshold for "quite likely"; any coverage
  before the pilot batches measure it; that proxy readers stand for human readers; that structured-input validation
  (AT-6a) shows the English is zero-training. Hedged calculation claims ("probably less than one sixth",
  math-evidence H-6p) are not attitude conditions. They need a separate, reviewed calc–attitudes bridge, which no
  plan owns yet. Attitudes landing does not lift math-evidence's `hedged` labels (edit 5).
- **Open (for AT-0):** the guard-node hook point on `lean/VE/Norms/Wire.lean` and the diagnostic when
  `attitudes@0` is off; whether the layered status kind checks the point against every X premise; whether the
  `english-codes` generator can carry the word table; the readings decoder's registration point after `lf-14d`.
  (Answered in spec draft 1 and 2, section 10; the off-profile diagnostic is today's, SR-6.)
- **Closed (RC-4):** draft 3 left open whether the `wants` test could exist in Lean and in Python between AT-1 and
  AT-5. The re-check found that interval breaks the one-owner rule. AT-1w, before AT-1, moves the test and deletes
  its Python copy in one merge, so it never exists twice; a batch of its own, since AT-1 with a relayed kind would
  exceed six hours.
- **Open (for the DRI):** AT-8's owner (attribution or attitudes); how the residual displays 21 open terms (14
  generated, 7 hand-named); whether "is aware that" may be an input synonym of "knows that" (only if E2-style
  agreement is shown; else refused with that rewrite); the go/no-go after AT-6a (F7).
- **Open (for the DRI, before E1 and E2's first call; draft 5):** confirm or change G1 (pair direction), G2 (one
  fresh context per call), G3 (all eight knows → thinks items in E2), G4 (the weaker word leaves `lowerBound`,
  weakest offending word first), G5 (the preamble and labels, E2's wordings, the three added "Does Claude know that
  P?" items) and G6 (invalid answers count as no for E1's no cap and are left out of the negated-"know" agreement;
  reader settings recorded), as written in section 4; and authorise E1's and E2's 2,480 calls under the usage cap.
  Each decision is recorded in this plan before any answer exists.
- **Risks:** the readings route is being rebuilt (AT-4 may need a second statement pass); E2 may reject premise 3
  for "quite likely", in which case `guard_collapse` has no instance on the pilot and the hand-named intention term
  changes verdicts; one slot may be too narrow for the honesty and intentions sections (AT-7 and E4 measure before
  widening it); PK-1, QS-1 and AR-10's table are reviewed by their owners, and a changed interface reopens the
  statements that name it. From phase 1: the rendering names AT-0p's open terms by identifier, not by their
  descriptions and factors (P1 2), so A8's audit may judge the identifiers rather than the rules unless it is given
  the open-term records; AT-5's Lean wording templates remove this for generated attitudes, not for hand-named
  terms (section 10, item 4).

## 8. Review checklist (for AT-0)

- `Intended` says what the attitude words mean and nothing more (D-A4, D-A9): no closure, no introspection,
  nothing from intending, wanting or saying.
- `mistaken_belief_admissible` has no hypothesis about the content's truth, and its conclusion is about the given
  structure `S` (no existential carrier mismatch, the deviation `lean/REPORTS.md` records for `holder_atom_free`).
- `att_old_language_conservative` has no hypothesis that the frame is empty.
- Every frame premise is universal with a quantifier-free body (`frame_universalQF`), as the norm-defaults evidence
  requires.
- Generated names cannot collide with `reports__`, `unsaid__`, `soft__`, `risk__` or `ve__` names (prefix
  `attitudes__`; `names_fresh` covers declared names, and the route checks the generated families of the profiles it
  combines).
- E1's pairs and E2's decisions are written into `table` and `entailsMode` before PASS, each entry with the item
  that passed it, and the closure review `#guard` holds (debate round 3). E2's record includes the decision on
  asserted-content negated knowledge, taken on all six of its items (SR-8, G5). A derived entry whose item failed
  was resolved by G4's one rule, and the record says which words left `lowerBound` and why.
- E1 and E2 ran under the protocol the DRI confirmed before the first call (G1–G6, section 4), and the item files,
  orders and scorer used are the committed ones.
- Every key a hypothesis names is in `keys A` (A3).
- Every theorem has one `#guard` instance on F-AT1 or F-AT2, and the small-scope counterexample search finds none
  (debate round 3); after the review's corrections, the stub is updated and elaborated and the search rerun with the
  new refusals in its pool (SR-8).
- Contents are typed over the base vocabulary, and the frame's typing on every route is proved, not assumed (A2).
- The 3.7 table gives every refused form two or more rewrites with one reading each, and those readings are exactly
  the form's candidate readings, at its category and in its context (SR-4, SR-5).
- Admission is what English can word: every admitted condition has its one sentence and no sentence two admitted
  conditions (`renderable`, `att_english_roundtrip` on admitted occurrences, `renderCond_injective`; SR-2).
- Admission, rendering and reading share one validated lexicon from the English grammar, tied to the document's
  environment (SR-3), with an entry for every predicate and constant an admitted condition names (D14d, RC-1).
- The `wants` test has one owner at every merge: AT-1w moves it into Lean and deletes its Python copy before AT-1
  calls it (RC-4).
- A decoded document is a checked document (`decodeAttDoc_wellFormed`, SR-7); with `attitudes@0` off, W1's, soft's
  and P0's answers are unchanged (SR-6); every statement's hypotheses suffice (`frame_unsaidFree` has `hw`, SR-1).
- No Lean comment uses a word `lean/audit.py` forbids; no theorem name has a prime or exceeds about 57 characters
  with its namespace.

## 9. Phase-1 record: results, what each gates, and DEFERRED triggers (draft 5)

Phase 1 (P1) ran every pre-registered item that needs no model call, with its bars quoted from draft 4 before any
run (`c0cf207c`). Batches **kept**: all. **Changed:** E2's item list (G3: all eight knows → thinks items; G5: six
items for the asserted-not-know form; the debate-round-3 closure items dropped as empty by construction) and the
closure resolution (G4). **Dropped or added:** none. Nothing in phase 1 cancels a product batch: E1 and E2 have
produced no data, and AT-0p's A4 measures the limit the typed frame removes.

| Item | Result | What it gates | Trigger (for DEFERRED) |
|---|---|---|---|
| AT-0p, A1–A7 | **PASS** (P1 2; section 4) | the data of the hard-constraint queue's first step; SC-1b's starting translation, once landed (C23); the motivation of AT-1 to AT-6a (A4) | — |
| AT-0p, landing in the pilot | **DEFERRED** (the pilot directory was read only) | SC-1b (queue 4.4); A8 | the pilot runner's next constitution run: `research/attitudes/at0p.py` (copy, apply) on that run's inputs, then the run's own `nd.py all`, probe and conflict checks |
| AT-0p, A8: the 7 units (874 B) audit-verifiable | **DEFERRED** | 874 B audit-verifiable; one of the two inputs of the DRI's go/no-go after AT-6a (F7) | the pilot's next audit of a run with AT-0p landed, given the open-term records with the rendering (section 7, risks); its timing in queue 4.4 is section 10, item 3 |
| E1 | **Run 2026-10-13: MET** (E1E2 4.1). Lower bound confirmed for almost certain, very likely, quite likely, likely, more likely than not (40 of 40 each); not for as likely as not, unlikely, very unlikely (0 of 40). All 10 pairs among the five enter `above` (40 yes, 0 no each); the other 18 pairs have 0 yes | `table.lowerBound` (which words "thinks it *w*" admits), `table.above` (frame premise 4); through the closure review, AT-0 PASS | — (AT1 authorised it with G1, G2, G5, G6 unchanged; G6's no-cap rule and its self-check cases added before the first call, `a8e5ae57`) |
| E2 | **Run 2026-10-13: MET** (E1E2 4.2). Premise 1 ships (40, 40, 40), premise 2 ships (40, 40, 40), premise 3 for all five `lowerBound` words (40 each). "P, and X does not know that P" **admitted**: "Must P?" 40, 39, 40 yes; "Does Claude know that P?" 40, 40, 40 no | `table.factive` (if it fails, `knows` is not admitted at all), `table.knowsBelieves`, `table.knowsThinks`, the admission of "P, and X does not know that P"; through the closure review, AT-0 PASS | — (AT1; G5's three items and G6's agreement rule added before the first call, `a8e5ae57`) |
| E2's negated-"know" and "unless" items | **Run** with E2. Negated "know": item 1 splits (15 yes, 6 no, 19 cannot tell), item 2 agrees on cannot tell (38), item 3 on yes (40): the reading depends on the content, and the refusal stands. "unless": 40 of 40 yes on all three | nothing: both forms stay refused whatever they show (D-A7); evidence for a later admission's own review | — |
| Closure review and freezing `table` | **Done 2026-10-13** (E1E2 4.3): G4 removes no word; Lean's `Table.reviewed` through the stub pinned by sha256 `2178fb6e…` is `true`; the frozen table is `docs/research/evidence/attitudes/e-table.lean` | the frozen meaning of `attitudes@0`; AT-0 PASS (SR-8) | — |
| AT-0 stub at the current draft, fixtures and search on the frozen table | **Done 2026-10-13** (AT0C, below): the stub carries spec draft 4's Lean with the frozen `table`, is committed, pinned by sha256 `0c73f880…`, and elaborates with every `#guard` holding; every fixture and the search rerun on `table`, the asserted-not-know form (F-AT9) in the pool; no counterexample | the re-review's input; AT-0 PASS (SR-8) | — |
| AT-0 PASS | **blocked** on SR-8's last step | AT-1w and every later batch; through AT-3a, SC-2 (synthesis 4.3) | the reviewers' re-review of the changed statements only, listed in [docs/research/attitudes-at0-changed.md](../research/attitudes-at0-changed.md) (AT0C) |

Cost, for the DRI's scheduling: E1 1,440 calls, E2 1,040 (920 without G5's three items); 2,480 in all. Hours as
section 4 (estimates).

**E1 and E2, run after phase 1 (2026-10-13; cited as E1E2 n, [docs/research/attitudes-e1e2.md](../research/attitudes-e1e2.md)).** The DRI's
AT1 authorised the 2,480 calls with G1–G6 unchanged. The bars were quoted and the pre-run scorer changes committed
before the first call (`a8e5ae57`); all 2,480 calls answered, by `claude-sonnet-5-5`, one fresh process each. Both
experiments MET their summary definitions (E1E2 1.3, 4.4); the rows above give the results. Consequences for the
next drafts are in E1E2 6: the frozen table written in, three words refused, the asserted-not-know form admitted
(the one statement change, re-reviewed under SR-8), negated "know" and "unless" still refused.

**AT-0's stub, fixtures and search on the frozen table (2026-10-13; cited as AT0C,
[docs/research/attitudes-at0-changed.md](../research/attitudes-at0-changed.md)).** The stub now carries spec draft
4's Lean (draft 3's) with E1E2's frozen table in `table`, and is committed at
`research/attitudes/stub/SpecStubs_attitudes.lean`, sha256 `0c73f880…`; `experiments.py` pins that hash, its
self-check holds 35 of 35 on it, and its review of the frozen table is `true` with `e-table.lean` unchanged. It
elaborates against `49de179e` with no error and every `#guard` holding (10 min 53 s). Draft 2's and 3's statements,
definitions and diagnostics elaborate as the spec writes them, and every value the spec marked *expected* is
computed as stated (D6a, D6b, D14a–D14d, D15, C-a to C-d, F-AT8). The fixtures run on `table`; their values are
unchanged, except D4 and D0, whose words the table now admits (D4 uses "as likely as not", same text; D0 is now
`thinks "as likely as not"`, refused). New fixture F-AT9, the admitted "both P and H does not know that P": true
exactly where P holds and the knowing does not. The search, with the spec's five new pool members and the admitted
form: 477 documents (210 of draft 1's, all admitted), 190 refused at their member's row, 287 checked on 9,184
document-model pairs, no counterexample to T1–T5, T7, T8 or the new T9 (the admitted form's reading). Two seeded bugs
were caught (AT0C 1). Left: the reviewers' re-review of AT0C section 2 only, then spec draft 5.

## 10. Cross-plan issues for the DRI

Phase 1 changes none of the shared parts: the owners (synthesis section 1, edit 8), the shared items (PK-1, AR-10's
table, QS-1, ET-D2) and the build order (synthesis 4.1–4.4, edits 7, 9 and 10) stand as written above. Where a
phase-1 result bears on them, it is recorded here, for the DRI, and not edited into the shared part.

1. **Resolved by the DRI's AT1** (E1 and E2 authorised and run, 2026-10-13; section 9). As written in draft 5:
   **E1 and E2 did not run in phase 1, so phase 2's AT-0 review cannot close.** Synthesis 4.1 puts E1 and E2 in
   phase 1 and AT-0's statement review in phase 2; AT-0 PASS needs E1's and E2's results (SR-8). Through the
   explicit dependency "AT-3a's guard decoder lands before SC-2" (4.3), and SC-2 writing u0173.s01's governor with
   attitude nodes (scope's edit 3), queue 4.4's third step and scope's 263 B claim wait on these 2,480 model calls,
   unless another of AT-3a's prerequisites (PK-1, AR-10's table, `lf-16e`, `qa-q2`) is later. Decision needed:
   when to authorise E1 and E2 (section 7), or how to reschedule; this plan does not move them.
2. **Queue 4.4's first step is measured, not landed.** SC-1b starts from AT-0p's translation (C23, scope's edit 3).
   Phase 1 confirms what SC-1b will find: in each of u0165.s01–s07, the guard `(C_i(s) ∧ knowingly_engages_i(c, s))
   ∨ thinks_quite_likely_i(c, s)`, with `restricted_action_knowing_or_quite_likely` gone (P1 2;
   `at0p-measure.json`, `seven_units`). No conflict with the order; but SC-1b cannot start until the pilot runner
   lands AT-0p (section 9). Decision needed: when the pilot runner's next constitution run lands it.
3. **The go/no-go's audit input and the queue's order.** F7's go/no-go after AT-6a reads the next audit's verdict
   on *AT-0p's* seven units. Queue 4.4 lands SC-1b and SC-2 on the same units before AT-6a, and SC-2 moves the
   attitude conjuncts out of the item guards. An audit run after SC-1b or SC-2 has landed judges their version, not
   AT-0p's. Not changed here; two options for the DRI: (a) an audit of the seven units between AT-0p's landing and
   SC-1b's (an added audit point; the queue's order unchanged), which this plan recommends, since it isolates
   AT-0p's effect; or (b) accept an audit of the queue's later state as F7's input, and say so in F7's record.
4. **Open terms are rendered by identifier** (P1 2, observation): "… has the recorded relation
   "thinks_quite_likely_1" to that situation", not the term's description or factors. Every plan in queue 4.4 that
   adds hand-named open terms to the seven units (SC-1b, SC-2, WG-5, WG-8, QT-B4) and their audits meet it, and the
   synthesis assigns the document rendering of open terms to none of the seven plans. Decision needed: who owns the
   fix (rendering an open term's description, or giving auditors the open-term records), so that A8 and the later
   audits judge the rules rather than the identifiers.
