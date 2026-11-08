# Typed attitudes as conditions of norms (`attitudes@0`): buildable plan

**Changes in this draft (at-rev, DRI 2026-11-02 fp-attitudes item 1).** Draft 7, branch `refresh/attitudes-20261028`
on at-0's commit `2b60e7bfb`. It applies the attitudes fidelity pilot's findings AT-R1 to AT-R4, structure first
(`manage-agents/reviews/dri-decisions-20261102-fp-attitudes.md` items 1-3, SIGNED; the pilot read this plan at
`885b74220`; its record is `manage-agents/reviews/fidelity-pilot-20261102/attitudes/`), and nothing else. D-A2,
D-A3, DEC 5 and DEC 13 are kept as signed; no DELTA row, trust line or signature is added.

1. **AT-R1 (A): a closed `wants` node as a set part** (sections 3.7, 3.11, 4 AT-1 and the batch table; spec 2.2-2.6,
   3.1, 20): the attitudes document carries its reading-set parts (PC-11's `attitude` case, DEC 13(a),
   profile-composition rule 8, F11.1); each is checked as a closed condition, and D14c words a closed `wants` of one
   unary base predicate on a constant there, and only there. AT-1 states it (fixture C-e, u0035.s12's shape). D-A3
   already writes a content about a constant closed, so no ruling is needed.
2. **AT-R2 (A): a holder report inside a composed document** (sections 3.11, 4 AT-8, 5): an attitude candidate, whose
   node's content is the one position PC-11 registers ("our", "its" resolve there); `reports@0` stays refused beside
   the chain; no `{"report": …}` unit, `contexts` block or `attributed` kind there. The "own review" deferral is
   replaced; no new PC kind is requested.
3. **AT-R3 (B): E3's set within PC's "under every choice" frame rule** (section 4 E3): the row lists the frames it
   covers; over a list lead-in its report-only candidate is withdrawn.
4. **AT-R4 (B): coverage of the family's own words** (section 3.7a, new): a stated row or a named GAP, with owner and
   reason, for each of the six forms the pilot found.

Statements: AT-1's change (`AttDoc.parts`, `keys`, `renderCheck`/`checkCond`'s `part`, `checkParts`, `checkAtt`,
`att_conservative_doc`) and AT-5's two round-trip hypotheses, spec section 20; AT-1w, AT-2 and AT-3a statements
unchanged, except AT-2's `keyOrigin` (opaque in the stub), whose prose gives a part's key its origin, the part's
place (review fix). Requests to profile-composition (3.11): PC-11 hands parts and their places; the reports x chain
pair no longer waits on AT-8.

**Changes in draft 6 (refresh 2026-10-28), kept as history.** Draft 6, branch `refresh/attitudes-20261028` (main `6d0a10526` plus
this plan and its spec from `research/attitudes-p1` `923f0a0ea`). It applies the converged staleness review
(`manage-agents/debates/refresh-attitudes-20261028/`, verdict **REFRESH**, converged after round 2; cited **Astra
r1/r2 n** for item n of that reviewer's proposed joint position in round 1 or 2, **Fable r1/r2** for Fable's) and
nothing else. The spec's draft 5 carries the Lean side (its sections 0 and 18).

1. **Landed and met** (status, sections 0, 4, 6, 9): AT-0p **LANDED** in the constitution pilot (DRI AT2); A8
   **MET**: u0165.s01–s07 (874 B) judged FAITHFUL in four audits (15 Oct 18Z; 19 Oct, AT3's added audit; 26 Oct;
   27 Oct); E1 and E2 **MET** and the table frozen (Astra r1 6; Fable r1 1, 2).
2. **Baseline refreshed** (sections 1, 2 D-A10, 6): the newest pilot run `run-20261028T0600Z` (2,951 B claimed;
   49 open terms; two reading sets, eight choices; u0165.s03's wide and narrow candidates kept) and the constitution
   census (AT in any role 551 units, 105,469 B: involvement, not an unlock estimate; κ caveat). Historical rows stay;
   the same refresh is appended, dated, to [docs/research/attitudes.md](../research/attitudes.md) (its appendix),
   whose 2026-10-12 measurements are kept as written (Astra r1 6; Fable r1 2; the DRI's census note).
3. **AT-0 reopened, bounded** (sections 4 AT-0, 9): the refreshed AT-0 reconciles the spec with E1/E2, restores and
   pins the stub, imports the merged interfaces, writes and elaborates the restated statements (the one declaration
   of each generated name, AT-2's contracts with PK-1, the row's admission; spec 2.4, 2.9, 6.2, 7.3), reruns
   fixtures and search, and has the reviewers check RR-1 to RR-3 and every statement this refresh changes (spec
   section 18) (Astra r1 1, r2 3; Fable r1 "closing AT-0").
4. **PK-1 as built; AT-2 widened** (sections 3.6, 3.9, 4 AT-2 and AT-4, 5): `consts := []`, (owner, prefix) rows,
   `assemble U used`, `(packPremises L.packs "attitudes").map (·.2)`; the double declaration of generated names is
   resolved (one declaration, in `envAtt`; the pack a `constraint` pack with no names, as soft's and rights' are);
   AT-2 carries PK-1's first-provider obligations as restated and elaborated in spec 2.9 and 6.2 (entries and
   `OriginsExact`; the environment, where `envX` is today's base environment, so nothing is threaded; no `ExpandsOn`,
   which a `constraint` pack does not owe; its own point check); AT-4 imports `SupPacks`' lemmas; AT-2 to AT-4
   re-estimated (Astra r1 2, r2 1; Fable r2).
5. **AT-3a against main** (sections 3.6, 4 AT-3a): registration through the kind table of
   `lean/VE/Defaults/Route.lean`, one new kind (`attitudes-elaborate`), the duplicate status, conflict and report
   kinds removed, the row's admission aligned with its composition theorem over `VE.Compose.Route`, `normFields` and
   soft's `shared := false` budget reused (Astra r1 3, r2 2).
6. **AT-3b is Lean and Python** (sections 4 AT-3b, 5): a call site in `lean/VE/Service/Document.lean` after SC-1b's,
   a typed, bound relay in `ve/document/`, rows in the rd-9 relay-binding inventory (Astra r1 4; Fable r1 4).
7. **Owners and shared pieces** (sections 3.9, 3.11 new, 4 AT-5, AT-8, AT-9): `VE.Attribution.Words` is a planned
   module with namespace `VE.Reports` (C14); refusal rows in en-sw's `SourceWords.lean` (C1), AT-5 waits for en-sw;
   `NegatedFactive`'s candidates from presupposition's projection (PS-NF); the hedge wrapper is attitudes' (C17);
   relay binding in the rd-9 inventory (D9); D2's overlap and purpose-explanation's D7 boundary recorded; new
   interfaces marked NEW (Astra r1 5, r2 4; Fable r1 5, r2).
8. **Dependencies and order** (sections 0, 4, 5, 6): merged prerequisites dropped; PK-1's old integration order
   dropped (et-4 may register the `events` pack first; `packOrder` fixes X's order); AT-6a waits for sc-2b, not SC-2;
   the batch order is the joint one (section 5); sc-5rc's dependency row is updated by the queue owner without
   re-blocking merged or in-flight work (Astra r1 order, r2 5; Fable r1 6, r2 order).
9. **WG-5 and the no-go case** (sections 4, 10 item 5): under the approved queue (edit 10, DRI AP2) WG-5's dependent
   rewrite follows AT-6b and AP-3 Group A; a no-go leaves dependent rewrites blocked; only an amended queue (WG-5
   before AT-6b, or a companion-only WG-5) is a new DRI decision (Astra r2 5; Fable r2 1).
10. **Rulings applied, not reserved** (sections 4 AT-1, AT-1w, AT-3a, AT-3b, 5, 7, 10): items 1–4 of section 10
    resolved by the DRI's AT1–AT4; the trust baseline's growth covered by R16 or R6 with their evidence, escalating
    only beyond them (no blanket "DRI signature, ruling D3"); generated files by R12 through
    `tools/regen_generated.py`; the obsolete committed `tools/gate-collection.json` removed from the generated lists
    (Astra r1 trust line; Fable r2).

**Synthesis round 2 edits (2026-10-30).** Applied from `manage-agents/debates/plan-synthesis-2/edits-attitudes.md`
(items 1–12 and the DRI's DEC 13; DRI-decided) and nothing else: the pack (3.6, AT-2), the AR-10 row and refusal
texts (AT-3a), the decider token (D-A6), AT-8's owner, E3's row, the likelihood ruling and "possible" (3.11, AT-9),
the hedge bridge (3.12, new), the decoder's `own` placeholder (AT-3a), the purposes boundary, the order (5).
Quality, for the PLANS-INDEX row (plan steward): soundness reads "typed, unproved" until AT-1 proves the statements.

> **Status.** Draft 6, 2026-10-28 (refresh). AT-0p has landed and A8 is met; E1 and E2 ran and met; the table is
> frozen. AT-0 PASS waits on the refreshed AT-0 (section 4 AT-0, section 9); the M10 path is AT-1w → AT-1 → AT-2 →
> AT-3a after it. Names and line numbers the refresh adds were read on main `6d0a10526`; no model calls were made.
> The history below is kept as written.
>
> **Draft 5's status (2026-10-13), kept as history.** Draft 5, 2026-10-13, branch `research/attitudes-p1`. Draft 5 applies phase 1 (pilots and
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

**Changes in draft 5 (from phase 1), kept as history.** No batch is cancelled and none is added; no Lean statement
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

**Pilot path** (refresh; arrows are merge order; F7, debate round 3). Done: AT-0p (landed, A1–A8 met), E1 and E2
(met), the closure review and the frozen table. Left: refreshed **AT-0 PASS** → AT-1w → AT-1 → AT-2 → AT-3a →
sc-2b and AT-3b → the pilot translation as sc-2 and sc-2b leave it → AT-6a (strict companion, structured input,
measured) → **DRI go/no-go** (F7) → AT-4 → AT-6b (main translation measured); then, under the approved queue (edit
10, DRI AP2), AP-3 Group A and WG-5's dependent rewrite. AT-5 (English) follows a "go", once AT-3b and en-sw have
merged (alongside AT-4). The constitution's milestone M10 (WG-3, AT-2/AT-3a, then WG-5) builds on this path; section
10 item 5 records what WG-5 waits for. About 40 to 48 hours from the refreshed AT-0 to AT-6b and AT-5 (**estimate**,
section 4's table; AT-2 to AT-4 re-estimated, AT-2 again once its pack was restated). Off the path, outside core approval and each with its own statement
review: AT-7 (nesting), AT-8 (holder reports in norm documents as attitude candidates, after E3; at-rev), AT-9 (numeric bands, on risk stage B's
trigger), E3, E4 (research). Merged or in-flight work is not re-blocked by this order.

**Pilot path, draft 5 (kept as history).** AT-0p (pilot, no code; measured in phase 1, PASS on
A1–A7; landing in the pilot DEFERRED, section 9) → E1 and E2 in parallel (DEFERRED: they wait for the DRI's
authorisation of their model calls; with G3, E2 does not wait for E1), then the closure review, then the table is
frozen → AT-0 PASS → AT-1w → AT-1 → AT-2 → AT-3a → AT-3b → AT-6a
(strict companion, structured input, measured) → **DRI go/no-go** → AT-4 → AT-6b (main translation measured) → AT-5
(English; after a "go" it may start once AT-3b and `qa-q2` have merged, alongside AT-4). About 46 to 55 hours by
the table's estimates, experiments included (estimates, not evidence of speed).

**The smallest batch that moves a pilot number** is AT-0p: the pilot rewrites the seven guards with the existing
language, so the seven "mistaken belief" points move from UNDECIDED to SETTLED no and the seven units can pass the
next audit. Phase 1 measured exactly that on working copies of the pinned run (P1 2): 7 of 7 points UNDECIDED →
SETTLED no, claimed bytes unchanged at 2,951, open terms 33 → 46. It also measured the untyped repair's limit: at
the impossible point (the case false, Claude knowingly engaging in it) all seven rules answer UNDECIDED (A4), which
only typed factivity removes. The smallest *product* batch that moves one is AT-3b (it needs AT-1w to AT-3a),
measured by AT-6a. Every
product batch claims 0 bytes and AT-0p alone moves the audit's number, so the DRI decides go or no-go after AT-6a
(F7), on AT-6a's measured results and the next audit's verdict on AT-0p's seven units, before AT-4 and AT-6b.
**Refresh:** AT-0p has landed, and that verdict is in: the seven units (874 B) were judged FAITHFUL in four audits
(15 Oct 18Z; 19 Oct, the audit the DRI's AT3 added; 26 Oct; 27 Oct), so A8 is MET and the go/no-go's audit input
exists; only AT-6a's measurement is left for it.

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

The rows above are the pinned run `run-20261012T1800Z` and phase 1, kept as measured. **Baseline refresh
(2026-10-28; Astra r1 6, Fable r1 2).** AT-0p has landed; batches starting now start from the newest run.

| What | Value | How |
|---|---|---|
| Newest pilot run | `run-20261028T0600Z`: 2,951 B claimed (unchanged); 49 open terms in the main translation; two reading sets, eight choices; u0165.s03 a reading set with its wide and narrow candidates, which every later step keeps | the run's ledger, as both reviewers read it |
| The seven hard-constraint units | 874 B audit-verified: FAITHFUL in four audits (15 Oct 18Z; 19 Oct, AT3's added audit; 26 Oct; 27 Oct). A8 MET | the audits' verdicts |
| Constitution census (2026-10-28), AT in any role | 551 units, 105,469 B (59 % of claim bytes): involvement, **not** an unlock estimate | `constitution-census-20261028.md` |
| Census, AT as primary family | 181 units, 33,574 B (7,507 B NORMATIVE, 26,067 B DESCRIPTIVE); Opus-corrected about 26,103 B. **Soft**: AT's primary label agrees on 8 of 18 sampled units (44 %), κ 0.63 overall, most disagreements going to DF on "we want Claude to …" | the census and the DRI's caveat (dri-research2, 2026-10-28) |
| Census, AT as the last blocker | 62 units, 9,364 B: units whose only family still uncovered, once every queued row lands, is AT (an upper bound on what attitudes alone could complete) | the census's last-blocker line |

Batches are sized on any-role counts and on reading the units, not on the soft primary shares. The old tag counts
(25 primary units, 3,268 B; 628 co-blocker units) are the pinned run's grep and are superseded by the census for
planning.

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
  `decided_by` the document's `attitudes.decided_by`, else `unstated`, the one W2 token (cross-plan synthesis round 2, C2). Rendered
  legend lines take their wording from the token's owner.
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
  `reports@0` and move to `lean/VE/Attribution/Words.lean` (a planned module, `VE.Attribution.Words`, declaring in
  attribution's namespace `VE.Reports`; refresh, C14); `VE.Attitudes.Words` imports that file and adds only
  `knows` and `thinks` (F6). Refusals and their rewrites are rows in english-lean's catalogue (edit 9), which is
  en-sw's `lean/VE/EnglishGrammar/SourceWords.lean` (refresh, C1), each with
  its category and its candidate readings (SR-5); `NegatedFactive`'s candidates come from presupposition's
  projection (DRI PS-NF). `reports@0`'s Python literals (`_VERBS`, `_SYNONYMS`, `_REJECTED`
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
  The first 13 are measured: AT-0p took the main translation from 33 to 46 (P1 2, A7); AT-6a's further 7 are an
  **estimate**: +7 on the run AT-6a and AT-6b start from (the newest run, `run-20261028T0600Z`, has 49; SC-1b, SC-2
  and sc-2b land in between and may change the count; refresh), not draft 5's "46 → 53". How the residual is
  displayed is not this plan's decision.

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
> by: unstated).
> What counts as intentionally doing the weapons uplift in a situation is not decided by VE (decided by: unstated).

No symbol appears in what people read or write. The structured form (JSON content) is what the pilot writes today;
the English form becomes writable in AT-5.

### 3.2 Syntax, keys and names

A guard is W1's guard grammar with one more atom, an attitude condition. A **key** is (mode, holder sort, slot sort,
content). Keys are listed once each (`VE.Reports.dedup`, reused); each key gets the predicate
`attitudes__<mode>__<i>` on (holder sort, slot sort). Names are fresh in `E`, at most 64 bytes and pairwise
distinct (checked by `WellFormedAtt`, proved by `names_fresh`, `names_injective`); `attitudes__` is registered in
PK-1's `reservedPrefixes` (edit 6) as the (owner, prefix) row `("attitudes", "attitudes__")`, by AT-2 (refresh). On
the layered and readings routes each generated name has exactly one declaration, `envAtt A` (through `toU`):
drafts 1–5 also declared it in the pack's `decls`, which `assemble` refuses as "already declared", and `U`'s
guards need the names declared in `U`, so the pack declares none (spec 2.4, 2.9; refresh, RF-5).

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
| norm-defaults, layered (the pilot's `readings/all-strict.ve.md`) | PK-1's assembler over `VE.NormDefaults.Wire.LayeredU` (`L.packs`, `X`, `background := backgroundBase ++ X ++ fillPremises`), `layered_conflict_sound`, `layered_report_sound`, `UndecidedAtX` | the frame is the `attitudes` pack: `kind := .constraint`, `decls := []` and `consts := []` (each key's name declared once, by `envAtt A`; refresh, RF-5), `labelled := (frameLabels A).zip (framePremises A)`, `origins` each label ↦ its full request occurrence, a key's occurrence carried by `attitudes-elaborate` (edit 6); assembled by `assemble U used` with the reserved-prefix row `("attitudes", "attitudes__")` (refresh, C7). Not one registration line: AT-2 also carries PK-1's first-provider obligations (AT-2 below) |
| norm-defaults statuses at a point | the layered route's status kind (`replayStatusX`) | PK-1 did not add the point check for all packs (it would change legacy soft answers, premise-packs.md 7); AT-2 checks the attitudes pack's premises on the point's model, legacy behaviour unchanged (refresh); then `SettledAs`/`UndecidedAt` agree with their X versions (`settled_frame_agree`, `undecided_frame_agree`, stated with the assembled X, AT-2) |
| readings, superposed and enumerated (the main translation) | `VE.Readings.Transfers`, `superpose_*_extra`, `fill_transfers`, PK-1's `VE.Readings.transfers_append` and `transfers_X` (`lean/VE/Readings/SupPacks.lean`, on main) | the assembled family, with the frame by `frame_transfers`, attitudes' provider obligation (AT-4) |

Attitude guard nodes are decoded, when `attitudes@0` is on, by the chain's norm decoders (W1's
`VE.Norms.Wire.decodeNorm` and soft's `VE.SoftNorms.Wire.decodeSoftNorm`; `VE.Readings.Wire.decodeNorm` and the
layered decoder dispatch to them), so one guard-node hook serves the norms, soft, layered and readings routes; the
`environment.attitudes` block is decoded by the `attitudes` pack provider. There is no `attitudes` service mode:
`attitudes-elaborate` is one new kind of the layered route, a row of the kind table `layeredRows`
(`lean/VE/Defaults/Route.lean`); status, conflict and report are today's layered kinds, which read the whole
assembled X (edit 7; refresh: drafts 1–5's `attitudes-status`, `-conflict` and `-report` duplicated them and are
removed, premise-packs.md 7). On main the hook reuses `normFields` (`lean/VE/Norms/Wire.lean:319`), the one decoder of
a norm's envelope, and keeps soft's `shared := false` budget (refresh). With `attitudes@0` off, those decoders are unchanged (SR-6). The attitudes
kinds' decoder, `decodeAttDoc`, also decodes the case's English lexicon with the English grammar's own decoders
(SR-3), and ends with `checkAtt`, so a decoded document is a checked one (SR-7).

### 3.7 English and one reading (AT-5)

| Wording | Reading | Status |
|---|---|---|
| "X knows that P" | knows | admitted |
| "X thinks it *w* that P", *w* in `Scale.lowerBound` | thinks *w* (lower bound) | admitted; any other word refused (A1) |
| "X believes that P", "X wants Y to VP", "X intends that P", "X says that P" | `reports@0`'s acts | admitted ("intends to VP" and "wants Y to VP" with an act phrase are not admitted. Intentional action stays residual until a reviewed act-performance bridge, designed by events-time-causation (ET-D2), fits this profile's contract: quantifier-free content over the base vocabulary, one slot. Act-phrases landing does not admit them; edit 3). "X wants Y to VP" only for one unary base predicate on the slot whose wording `reports@0`'s test turns into "Y to VP"; as a reading-set part only (PC-11's `attitude` case), also the closed content one unary base predicate on a constant `Y` (at-rev, AT-R1; u0035.s12); any other `wants` content is refused (SR-2) |
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

### 3.7a Coverage of the family's own words (at-rev, AT-R4)

The 2026-11-02 pilot found six forms of the family's own words with no row (decision item 1, AT-R4). Each now has a
stated row or a named GAP. D-A2 and D-A3 are signed scope and are not reopened; a GAP is a line of a writer's report,
never a status, and its units stay UNFORMALISED or pending where the form occurs.

| Form (pilot unit) | Row or GAP | Owner | Reason |
|---|---|---|---|
| `wants … to VP` with an act phrase, the holder or another term as the act's agent ("wants to pause a given model", u0220.s06; "want Claude to weigh", u0011.s05) | **GAP**; refused, as 3.7's row says | attitudes; trigger: a reviewed act-performance bridge (ET-D2, events-time-causation) that fits this contract, then its own statement review | D-A3 does not allow a row: an act regulated by a rule is no base vocabulary, and an act with the holder as agent names two guard terms (the holder and the slot), where D-A3 allows one; D-A2 refuses it (edit 3) |
| a noun object of `wants` ("a user wants information", u0135.s06) | **Row**: inside a consideration the words stay text (DEC 5; soft-norms' `factors`, verbatim). **GAP** elsewhere | attitudes | a noun phrase is no content formula (D-A3); a verb supplied for it ("to have", "to get") would be a guessed reading |
| "understand" as a mode ("says they understand the content is …", u0159.s11) | **GAP**; not a mode, never renamed `knows` (attribution's rule) | attitudes; trigger: pre-registered items as E2's for "understand" (factive? entails `believes`?), not planned in this draft | D-A2 admits no other mode; its frame relations are unmeasured |
| a two-participant believed content (a user and an essay, u0159.s11) | **GAP** | attitudes; AT-7 and E4 measure before one slot is widened (section 7, risks) | D-A3: at most one thing named by a guard variable; a second slot changes the key and the frame's typing |
| negated `wants` beyond `NegRaising` ("we don't want Claude to think …", u0246.s04) | **GAP**; the form is not read. "It is not the case that H wants Y to VP" stays admitted (3.7's negation row) where the source says that | attitudes (AT-5's rows in en-sw's `SourceWords.lean`) | it has two readings, not wanting and wanting not; the second, "H wants Y not to VP", has no admitted wording (D14c), so a catalogue row cannot list both as one-reading rewrites (SR-5) |
| a normative, quantified or modal believed content ("we believe all current Claude models should be", u0014.s03; "fears … necessarily apply", u0246.s04) | **Row**: refused at admission, D12 (`an attitude content has a quantifier`) or D13 (a regulated predicate fails the base typing). **GAP** for its meaning | attitudes | D-A3: quantifier-free over the base vocabulary, without regulated predicates (signed); whether a modal may be a content is attitudes' own open bar (profile-composition 17.1) |

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
| Extra base premises on routes | PK-1 packs (RD-9 composition owner; `lean/VE/NormDefaults/Packs.lean`, as built: `consts`, `assemble U used`, (owner, prefix) rows) over `LayeredU`, `BaseAdmissibleX`, `Transfers`; `VE.Readings.transfers_append`, `transfers_X` | attitudes is the `attitudes` provider, a `constraint` pack and PK-1's first further provider, with its first-provider obligations (AT-2; spec 2.9); no new route semantics |
| Layered kinds | the kind table `layeredRows` (`lean/VE/Defaults/Route.lean`) | one row, `attitudes-elaborate`; no duplicate of today's status, conflict or report kinds (refresh) |
| Likelihood words and their order | `VE.Attitudes.Scale`; closure is QS-1's over `VE.Closure` | attitudes owns `table`, E1/E2 gating, `lowerBound`, the frozen record of which item passed each entry, and the closure-review `#guard`; risk stage B extends it (AT-9) |
| Attitude verbs, synonyms, refusals (English) | the four report verbs stay under attribution (`VE.Attribution.Words`, a planned module that AT-1w creates, namespace `VE.Reports`, C14); `VE.Attitudes.Words` adds only `knows` and `thinks` | **moves** from `ve/report_english.py`; AT-5 deletes the Python literals |
| Intentional action ("intends to VP") | residual; the bridge's design is events-time-causation's (ET-D2), which owns the performance boundary | not admitted (edit 3) |
| Distribution over joined acts | none in attitudes | edit 4 |
| Hedged calc and causal claims | attitudes: the hedge bridge over `VE.Attitudes.Scale` around the requesting family's unit (DRI 2026-10-28, PLANS-INDEX C17; C22 decided in synthesis round 2, DECISIONS item 2: section 3.12) | refused until hedges-generics' H-4 discharges the gate (3.12); edit 5's "unowned" is superseded (refresh) |
| Refusals and source-word reading sets | english-lean: en-sw's `lean/VE/EnglishGrammar/SourceWords.lean` (not on main; row type fixed there; PLANS-INDEX C1) | AT-5 adds rows there, each with its category and candidate readings (SR-5), no separate refusal table; AT-5 waits for en-sw (refresh) |
| `NegatedFactive`'s candidate readings | presupposition's projection (DRI PS-NF) | AT-5's rows consume them (refresh) |
| Relay binding of attitudes answers | the rd-9 relay-binding inventory (DRI D9 ruling, 2026-10-28) | AT-3b adds its rows before relaying (refresh) |
| English lexical data and its validity | the English grammar: `VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`, `Lexicon.failures`; decoders `Env.decode`, `Overlay.decode`, `Run.decodeLexicon` | carried by the document (`AttDoc.lex`), checked in `WellFormedAtt` (D6a, D6b, and per condition D14d, RC-1), decoded at AT-3a; no attitude-local template classifier (SR-3) |
| The `wants` verb-phrase test | `reports@0` (`_subject_split`, `_infinitive`, `_finite` in `ve/report_english.py`) | **moves** into `lean/VE/Attribution/Words.lean` in AT-1w, which deletes the Python copy in the same batch (SR-3, RC-4) |
| The hand-named open term `restricted_action_knowing_or_quite_likely` | pilot translation | deleted by AT-0p (landed, DRI AT2), then AT-0p's atoms by AT-6 |

### 3.10 Conservativity

Any structure over `E` extends to `envAtt A` by reading every generated predicate as empty; every frame premise
then holds (its antecedent is false), and old formulas keep their values. So a document without attitude
conditions (and, at-rev, without reading-set parts) means what it meant, and old-language consequence is unchanged (`att_old_language_conservative`,
`att_conservative_doc`). Drafts 1–5 also called this extension the `attitudes` pack's expansion step as a PK-1
`vocabulary` pack (edit 6); the pack is a `constraint` pack (refresh, RF-5), which owes PK-1 no expansion step, and
this conservativity theorem over the document is unchanged.

### 3.11 Shared pieces (refresh)

Read against PLANS-INDEX (2026-10-28) and the DRI's 2026-10-28 rulings; new interfaces are marked NEW.

| Piece | Status | What this plan does |
|---|---|---|
| PK-1 as built (C7) | reused; this plan was written against round 1's interface | sections 3.6, 4 AT-2: `consts`, `assemble U used`, (owner, prefix) rows, `packPremises L.packs`, first-provider obligations |
| Report verbs' module (C14) | conflict to resolve: `VE.Attribution.Words` does not exist yet (namespace `VE.Reports`); `attitudes@0` and `reports@0` refuse each other | AT-1w creates the module; the refusal stands: `reports@0` stays refused beside the chain (profile-composition rule 7; AT-3a's row), and inside a composed document AT-8 writes a holder report as an attitude candidate (AT-8; at-rev, AT-R2) |
| **Request (at-rev, AT-R1) to profile-composition PC-11**: the slot is PC-11's decoder of a reading-set part in the `attitude` case | requested; no new case and no new kind (DEC 13(a)) | PC-11 reads the part's node with AT-3a's node decoder, hands it to the attitudes document as one of `AttDoc.parts` in document order before `checkAtt`, and takes its `attitude φ` from `partClaim` (spec 2.2, 2.5); so F11.1's "Anthropic wants Claude to be genuinely helpful …" checks through `checkParts`, a closed `wants` part (spec 2.6). With the node it hands the part's place (set, reading, part: PC's `candidateAt` place), the origin `keyOrigin` carries for a part's key (spec 2.9); PC-11 fixes that path |
| **Request (at-rev, AT-R2) to profile-composition**: the slot is the refused-pairs line "reports x norms, and reports x the chain", which says the pair waits for AT-8's bridge (C14, round 2) | requested | AT-8 builds no such bridge (AT-8, withdrawn): the pair stays refused (rule 7). It waits on a reports bridge that EXP-O1 or another owner PC names; until one is stated, nothing changes |
| Likelihood words (D2) | ruled (synthesis round 2, DECISIONS item 1): attitudes owns `VE.Attitudes.Scale` and the frozen table; risk stage B reads its bands through AT-9 | decided, no longer this plan's proposal. Attribution's `May(a, q)` and `Probably(a, q)` keep their built meaning and stay unrelated; no `reports@0` answer changes. Ordered implications ("likely" entails "possible") apply only to hedge premises admitted through the hedge bridge (3.12), never to report assessments |
| Hedge bridge (C17, C22) | owner attitudes (DRI 2026-10-28; synthesis round 2, DECISIONS item 2): hedges-generics' `lean/VE/Hedges/Bridge.lean` structures move under attitudes, with the frozen scale | section 3.12; hedged calc, count and causal units refused until H-4 discharges the gate |
| Source-word rows (C1) | owner english-lean, `SourceWords.lean` by en-sw | AT-5 waits for en-sw |
| Relay binding (D9) | owner the rd-9 inventory | AT-3b adds rows |
| Purpose-explanation's "we want vs norm" | boundary, closed in synthesis round 2: E3 and AT-8 own "we want Claude to …"; purpose-explanation's D7 attaches its links to whatever E3 yields; the census's AT/DF disagreements fall on these sentences | a boundary, not a duplicate; E3 and AT-8 depend on it |
| Projection (PS-NF), act performance (ET-D2) | owned elsewhere | consumed, not built here |
| **NEW**: the attitude guard node, the `attitudes` pack, the likelihood `Scale` and its frozen `table` | owned by attitudes | AT-1 to AT-3a |

**"possible" (synthesis round 2).** "possible" enters the frozen table only through attitudes' own pre-registered
items in E1's protocol (modality's proposal: "If Claude thinks it w that P, does Claude think it possible that P?"
for each lower-bound word, and a certainty item). If they pass, "possible" sits below every lower-bound word, and the
authors' epistemic "might" reads as `thinks "possible"`; until then both stay refused.

### 3.12 The hedge bridge (synthesis round 2: C17, C22; DECISIONS item 2) (NEW)

Attitudes owns the hedge bridge; the structures of hedges-generics' `lean/VE/Hedges/Bridge.lean` move under
attitudes, with the frozen scale.

- **Shape:** holder-free, attribution's assessment shape: one generated unary predicate per (meaning, word) on an
  assessment constant. No author holder, no `thinks w`. If the generation logic is shared with attribution, it is
  factored under attribution and called here.
- **Route:** the hedge elaboration declares one fresh context sort, one constant and the unary atoms per (meaning,
  word) in the base environment before `toU`, under the reserved prefix `attitudes__`, as `envAtt` does (RF-5).
  AT-3a lists the hedge sort and atoms in `envAtt`'s pattern. The `attitudes` pack stays `.constraint` with no
  names and carries `bridgePremises` only. `packOrder` is unchanged. The sort counts once against `sortCap := 8`.
- **Gate:** hedges-generics' H-4 proves, before any hedged foreign unit is admitted: typing, name freshness,
  vocabulary charging, `hedge_conservative` over empty (`Option`) carriers, `hedge_entails_base`, and compatibility
  with the layered route (`envAt` hides layer symbols only, `Norms/Tree.lean:173`). Until then hedged calc, count and
  causal units stay refused.
- **The wrapped unit** is named by the document model's NEW `UnitRef` (Lean recomputes `meaning` per family, H-5).
- **Fallback, not built:** `Pack.sorts` under a PK-1 item, only if H-4 cannot discharge its theorem on this route.

## 4. Batches

Every product batch: 2 to 6 hours for one builder, with the lean-first gate (selected tests while iterating; the
full gate once, on the final HEAD; corpus A/B where the batch changes an answer; `DELTA.md` by class), the Lean audit
(`python3 lean/audit.py`: no forbidden word even in comments, no primes in theorem names, names under about 57
characters), regenerated inventories through `uv run python tools/regen_generated.py --write` (never by hand),
`tools/lean_statements.py` showing additions only, and seeded bugs in each changed language (CLAUDE.md). The seeded
bugs, one per behaviour claimed: AT-1w, `wantsPhrase?` without the irregular `is` → `be` (the recorded infinitive of
"is classified as …" changes), and the relay accepting a row for a phrase it did not send (a fuzz test fails, RC-4); AT-1, factivity generated with its implication reversed (F-AT1's M2 `#guard` fails), the constant-slot check
(D14b) skipped (collision fixture C-b's `#guard` fails, SR-2), the lexicon-entry check (D14d) skipped for
constants (C-d's first document is admitted, RC-1), and D14c's closed `wants` admitted without the `part` flag (C-e's
second document, the node in a guard, is admitted; at-rev, AT-R1); AT-2, the frame
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
| AT-0p | Pilot repair with the existing language (no product code). **LANDED** (DRI AT2); A1–A7 PASS (phase 1); **A8 MET**: the seven units FAITHFUL in four audits (section 9) | 2 | pilot runner | — (first step of the hard-constraint queue, edit 10) |
| E1 | Likelihood-word order and lower-bound reading (experiment). **Run 2026-10-13: MET** (section 9) | 2–3 | experiment runner | — (DRI AT1) |
| E2 | Factivity, knows → believes, knows → thinks it *w* for all eight words (G3), negated "know", "unless", "P, and X does not know that P" with its six items (G5) (experiment). **Run 2026-10-13: MET** (section 9) | 2 | experiment runner | — (DRI AT1) |
| AT-0 | Statement spec `docs/spec/attitudes.md`, stub elaborated against main, small-scope counterexample search, statement review (round 1: FIX, SR-1 to SR-8; re-check: FAIL, RC-1 to RC-4; re-review: FIX, RR-1 to RR-3). **Refreshed** (2026-10-28): the stub restored, pinned and elaborated on main `6d0a10526`; the statements draft 5 had marked *to restate* written and elaborated, fixtures and search rerun (spec 7.3, 18; done); the reviewers check RR-1 to RR-3 and every statement spec section 18 lists | 2–3 left (**estimate**) | planner | — (E1, E2 and the closure review done) |
| AT-1w | `reports@0`'s `wants` test moved into Lean (new module `VE.Attribution.Words`, namespace `VE.Reports`), its Python copy deleted, `reports@0`'s Python English reading Lean's through a `reports` kind (RC-4) | 3–4 | Lean, Python | refreshed AT-0 PASS |
| AT-1 | Lean core: syntax, keys, elaboration, frame, semantics, admission with the lexicon and `renderable`, theorems, fixtures. At-rev (AT-R1; spec 20): the reading-set parts (`AttDoc.parts`, `partsOf`, `partClaim`, `checkParts`), D14c's closed `wants` part, `att_conservative_doc`'s `hp`, fixture C-e; the first batch that emits a closed `wants` set part | 5–6 | Lean | AT-1w (QS-1 is merged) |
| AT-2 | Lean: the layered route with the `attitudes` pack, a `constraint` pack and PK-1's first further provider: one declaration per name (in `envAtt`); `("attitudes", "attitudes__")`; `packEntry`, `furtherEntries` and their shape key; `OriginsExact`; `envX_declFree` (nothing threaded); the attitude-only `pointCheck`; statuses, conflicts and report through today's kinds | 5–6 (**estimate**; was 4–5, then 7–9 with `envX` threading and `ExpandsOn`, which the restated pack does not need) | Lean | AT-1; profile-composition's EXP-G1 (after PC-3) (PK-1, pk-1b merged) |
| AT-3a | Lean wire: the guard-node hook on `normFields` (soft's `shared := false` budget kept), the pack provider's block decoder, one kind `attitudes-elaborate` in `layeredRows` (`lean/VE/Defaults/Route.lean`), its shape and encoder theorem, the AR-10 row with admission aligned to `attitudes_row_composes` over `VE.Compose.Route` | 5–6 (**estimate**, unchanged: three fewer kinds, a real composition proof) | Lean | AT-2; PC-6 (after CI-5) (PK-1, AR-10a, `lf-16e`, `qa-q2`, AP-1, AP-3 merged) |
| AT-3b | The `attitudes@0` call site in Lean's document mode (`lean/VE/Service/Document.lean`, after SC-1b's), the typed, bound Python relay in `ve/document/` with request-path binding, rows in the rd-9 relay-binding inventory, fixtures and fuzz tests | 5–6 (**estimate**; was 4–5) | Lean, Python | AT-3a (`lf-16g`, SC-1b merged) |
| AT-6a | Pilot: the strict companion with typed attitudes, structured input, measured | 3 | pilot tooling | AT-3b; sc-2b; the pilot translation as sc-2 and sc-2b leave it (hard-constraint queue, edit 10) |
| — | **DRI go/no-go** (F7): AT-6a's measured results and the audit verdict on AT-0p's seven units (in: A8 MET) | — | DRI | AT-6a |
| AT-4 | Readings chain with the `attitudes` pack (superposed and enumerated), importing `VE.Readings.transfers_append` and `transfers_X` | 4–5 (**estimate**; was 5–6: PK-1's readings lemmas exist) | Lean, Python | "go"; AT-3b (`lf-14d`, RD-9, `lf-16e`, PK-1 merged) |
| AT-6b | Pilot: the main translation with typed attitudes, measured | 3 | pilot tooling | AT-4; the hard-constraint queue (edit 10) |
| AT-5 | English in Lean: wordings, refusals as `SourceWords.lean` rows with `NegatedFactive`'s candidates from presupposition's projection, rewrites; `reports@0`'s Python tables deleted | 5–6 | Lean, Python | "go"; AT-3b; en-sw merged; first in the English queue (edit 9) |
| AT-7 | Nested conditions (two levels) and "knows whether" | 5–6 | Lean | AT-4 |
| E3 | "We want Claude to X": report, rule, or both (experiment) | 3 | experiment runner | — (purpose-explanation's D7 attaches its links to E3's outcome) |
| AT-8 | Holder reports in norm documents as attitude candidates (E3's sets; F11.5's belief/fact set), bare reports included; no `reports@0` unit beside the chain (at-rev, AT-R2) | 5–6 | Lean, Python | E3; PC-11 (DEC 13) |
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
  WG-5`; each step starts from the translation as the previous step left it. The DRI's AP2 puts AP-3 Group A right
  after AT-6a/AT-6b, before WG-5 (refresh: that ruling postdates edit 10 and this plan's draft 5). SC-2's
  attitude-word fixture is its split-off sc-2b, which waits for AT-3a; AT-6a starts from the translation as sc-2 and
  sc-2b leave it.

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
| A8 | the 7 units (874 B) become candidates for audit verification | FAITHFUL in four audits (15 Oct 18Z; 19 Oct, AT3's; 26 Oct; 27 Oct): 874 B audit-verified | **MET** (refresh; DEFERRED in draft 5) |

Not bars, also measured: the other 21 probe points and the run's four conflict checks give their recorded answers;
the main translation keeps the run's assertions (premises `model`, plan `enumerate` with 8 choices, CONFLICT-FREE,
coverage 100 %); the rendering changes only the seven rules' "Open reading" lines. **Observation:** the rendering
names the new open terms by identifier ("… has the recorded relation "thinks_quite_likely_1" to that situation"),
as it named the deleted one, so an auditor reading only the rendering sees neither the description nor the factors
(section 7, risks; section 10, item 4).

**Landing.** AT-0p is measured, not landed: the pilot directory was read only in phase 1. The pilot runner lands
it in the next constitution run with `at0p.py` (copy, apply) on that run's inputs; SC-1b starts from that
translation (section 9, section 10 item 2). **Refresh:** landed (DRI AT2); A8 met in four audits (section 9).

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
- **AT-0's re-review (2026-10-14).** The bounded re-review of AT0C section 2
  (`manage-agents/attitudes-at0-review.final.md`) returned **FIX**: two B findings and one C, corrected as spec
  section 17's RR-1 to RR-3 (AT0C section 5). The admitted "both P and H does not know that P" is read whole, with one
  tree `assertedNotKnows c`, and a new AT-5 statement `assertedNotKnows_one_reading` says it has exactly that one
  derivation (RR-1); spec 7.6 gains AT-5 fixtures read by the English reader for the row and for the refusal's
  boundary (RR-2); the search's seed count is relabelled and the checked seeds counted (RR-3). The stub carries them,
  is re-pinned (`dea412eb…`) and elaborates with every `#guard` holding. Left: the reviewers' check of RR-1 to RR-3
  only.
- **Refreshed AT-0 (2026-10-28; Astra r1 1, r2 3; Fable r1, r2).** The staleness review found the plan and spec
  written against round 1's interfaces and draft 4's empty table, so the old bounded check of RR-1 to RR-3 alone is
  no longer enough. Spec draft 5 reconciles its normative text with E1/E2 (the frozen `table` in spec 2.1; D0, D4
  and QS-1's D5 text), restores the stub `dea412eb` from `923f0a0ea`, pins it at
  `docs/spec/attitudes/SpecStubs_attitudes.lean`, replaces the stand-ins for merged interfaces (QS-1, PK-1, AR-10)
  with imports and elaborates it against main `6d0a10526` (spec 13, 18). It also writes the statements its first
  commit had marked *to restate* (the generated names' one declaration, in `envAtt`; PK-1's environment, expansion,
  origins and point-check contracts; the profile row's admission), with computed fixtures (spec 2.4, 2.9, 6.2,
  7.3), and reruns every fixture and the search on the refreshed stub (spec 18). Left: the reviewers check RR-1 to
  RR-3 and every statement section 18 lists. AT-1w may then start.
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
cases and the Lean inventories, as AT-1 (no committed gate collection: `tools/gate_collection.py --check` compares
with the merge base; refresh). The new module is `VE.Attribution.Words`; its declarations are in attribution's
namespace `VE.Reports` (`VE.Reports.wantsPhrase?`; refresh, C14). It is a planned module, not a missing merged
prerequisite.

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
`lean/predicates.txt`, through `tools/regen_generated.py --write` (R12). No committed gate collection (refresh:
`tools/gate-collection.json` is no longer on main). No hand-written shared file.
Needs AT-1w; QS-1 (`lean/VE/Closure/Order.lean`, owned by quantities) has merged (edit 1).

The block below is draft 1's with the converged edits made; AT-0's elaborated text
([attitudes.md](attitudes.md) sections 2 to 4) governs where they differ. In particular the statement review's
corrections are written there, not here: `AttDoc` gains `lex` (the English grammar's `Env`, `Overlay` and
`Lexicon`); `checkAtt` gains D6a (`Lexicon.failures`) and D6b (`lexAgrees`) after the reserved-prefix check; and
`checkCond` ends with `renderCheck` (D14a unused slot, D14b slot at a constant, D14c `wants` without its wording,
D14d a predicate or constant with no lexicon entry), whose success is `renderable` (SR-2, SR-3, RC-1). The block
therefore also imports `VE.EnglishGrammar.Lexicon` and `VE.Attribution.Words`. Its `table` is the one before E1 and
E2 reported; the frozen table is spec 2.1's (refresh). At-rev (AT-R1; spec 2.2-2.6, 6.1, 20), also written there:
`AttDoc` gains `parts`, the closed nodes of PC-11's `attitude` parts; `keys` runs over `condsOf A ++ partsOf A`;
`partClaim` gives a part's claim; `renderCheck` and `checkCond` take a `part` flag, with which D14c also words a
closed `wants` of one unary base predicate on a constant; `checkAtt` runs `checkParts` after the rules' conditions;
`att_conservative_doc` gains `hp : A.parts = []`.

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
  /-- the decider of every generated open term; "unstated" (the one W2 token, C2) when the document names none -/
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
/-- A document with no attitude condition and no reading-set part (at-rev, AT-R1): no key, no frame, the same
    environment. -/
theorem att_conservative_doc (A : AttDoc) (h0 : condsOf A = []) (hp : A.parts = []) :
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
- **C-e, a closed `wants` set part (at-rev, AT-R1; u0035.s12's shape).** F-AT1 with the part "c0 wants s1 to be
  classified as …" (holder and content constants): admitted, its key named after the rules' keys
  (`attitudes__wants__1`), its claim `attitudes__wants__1(c0)`; the same node in F-AT1's guard, and the part with a
  compound content, refused at D14c (computed in the stub, spec 7.1).

Deleted, not duplicated: draft 1's `qf` (A5) and `Scale.step` (edit 1). `Act`, `dedup` and content identity are
`reports@0`'s; the closure is QS-1's; the lexicon and its validity are the English grammar's; the `wants` test is
`reports@0`'s, moved by AT-1w (SR-3, RC-4).

Shared files: none hand-written. In-flight overlap: none (new directories). No Python copy of the `wants` test
remains: AT-1w deleted it (RC-4).

Bytes unlocked: 0 (nothing calls the code).

Done when: the files build with standard axioms only, the fixtures `#guard`, `lean/ATTITUDES.md` lists every theorem
in plain words, the audit passes, and the gate passes (no answer can change).

### AT-2. The layered route with the `attitudes` pack (Lean, 5–6 h, estimate)

**Refresh (Astra r1 2, r2 1; Fable r1 3, r2).** PK-1 (with pk-1b's kind table) has merged, and as built it leaves
more to its first further provider than "one registration line" (premise-packs.md 2.7, 3, 5 and 7). AT-2 is that
provider, so it carries (as restated and elaborated in spec 2.9, 6.2 and 7.3):

- **One declaration per generated name.** `envAtt A`, through `toU`, declares every key's name, and drafts 1–5's
  pack declared it again in `decls`; `assemble U used` refuses that as "already declared" (PK-1 fixture A4;
  computed on F-AT1). The declaration stays in `envAtt`, since `U`'s guards read the names, and the pack is a
  `constraint` pack with `decls := []` and `consts := []`, as soft's and rights' are (`attitudesPack_declares_nothing`,
  `names_in_base`, `assemble_attitudes`).
- **PK-1 as built:** `consts := []`; the reserved-prefix row `("attitudes", "attitudes__")`; assembly by
  `assemble U used ps`; one pack's premises as `(packPremises L.packs "attitudes").map (·.2)`.
- **The deferred pieces:** `packEntry` and `furtherEntries` (2.7), in the same change as their optional key in the
  closed `layered_elaborate` shape, the generated schema and the relay; `OriginsExact` (obligation 5,
  `attitudesPack_originsExact`). `expandBy` and `ExpandsOn` (obligation 1) are a `vocabulary` pack's: a
  `constraint` pack keeps its local checks and makes no conservativity claim on the route (premise-packs.md 3), so
  they land with the first provider whose pack declares names; conservativity over the old language stays AT-1's.
- **Not a vocabulary provider (synthesis round 2, N2; DECISIONS item 7).** `attitudesPack` stays a `.constraint`
  pack with `decls := []`; each generated name is declared once, in `envAtt`, before `toU` (RF-5). PK-1's G1b is not
  a prerequisite of AT-2: G1b's trigger is the first pack with non-empty `decls`.
- **The environment:** the pack declares nothing, so `envX` is `envAt (fill U) 0` (`envX_declFree`), which already
  declares the names. Situations, certificates (the one binder `bindCertX`,
  `lean/VE/NormDefaults/LayeredAdmission.lean:83`) and `BaseAdmissibleX` stay as they are; nothing is threaded.
- **The point check for its own pack:** PK-1 refused to check every legacy pack at the point (it would change
  today's soft status answers), so AT-2 runs `pointCheck` on the attitudes premises at the point's base situation
  and keeps legacy point behaviour unchanged (`pointCheck_absent`, `pointCheck_sound`).
- **Diagnostics as PK-1 places them:** `InvalidModel(attitudes): the model violates a background premise: <label>`
  (`packFault`), and the collision witness checked without the soft pack's coherence premises (`xWithout`, DF7).

The re-estimate is 5–6 h (was 4–5; the first refresh commit's 7–9 h counted `envX` threading and `ExpandsOn`,
which the restated pack does not need). Hand-written shared files: `lean/VE/NormDefaults/Packs.lean` (the prefix
row, `OriginsExact`, `packEntry`, `furtherEntries`), `replayStatusX` in `lean/VE/NormDefaults/Layered.lean` (the
point check), `ResponseShape/Schemas/NormDefaults.lean` (the further-entries key) and its relay. PK-1's integration
order (AT-2/AT-3a → WG-3 → ET-4 → QT-B2) no longer binds: et-4 may register the `events` pack first, and `packOrder`
fixes the order inside X whichever provider lands first.

**Draft 5's text, kept as history:** Files: `lean/VE/Attitudes/Route.lean` and `RouteExamples.lean` (new). Generated as in AT-1. Hand-written shared
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
/-- The `attitudes` pack (edit 6); refresh: a `constraint` pack with no names (spec 2.9 has the governing text). -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .constraint, decls := [], consts := [],
    labelled := (frameLabels A).zip (framePremises A), origins := origins A }
/-- The `attitudes` pack's premises are `framePremises A` (replaces `FrameSource` and `frameSource_X`). -/
theorem attitudesPack_premises (A : AttDoc) (h : WellFormedAtt A = true) :
    (attitudesPack A).labelled.map (·.2) = framePremises A ∧ (attitudesPack A).labelled.map (·.1) = frameLabels A
/-- PK-1's typing obligation for this provider (A2). -/
theorem frame_typed_fill (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : WellFormedU U = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (envAt (fill U) 0) []
/-- Conservativity's expansion step: empty attitude relations satisfy every frame premise (drafts 1–5: PK-1's
    `vocabulary` expansion step; refresh: the pack is a `constraint` pack). -/
theorem empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) :
    Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A)
end VE.Attitudes
```

(`origins A` maps each frame label to its full request occurrence (refresh: a key's is in `attitudes-elaborate`'s
answer, since the pack has no names); a key's occurrence is holder term, mode, content, slot,
enclosing rule and guard location (A6, edit 6), and for a reading-set part's key (at-rev, AT-R1) its set, reading
and part (PC's `candidateAt` place, handed by PC-11's decoder); AT-3a fixes the paths, PC-11 the part's. `att_conflict_sound` is no new theorem: it
is `layered_conflict_sound` at PK-1's assembled X. Draft 1's `mistaken_belief_settled` and its placeholder
`decidesAt` become the fixture below, through `settled_of_table3` and `settledX_of_settled`.)

Fixtures (`RouteExamples.lean`): F-AT1's points through the layered route's status kind with the X check: M1 SETTLED
no; M4 UNDECIDED; M2 and M3 refused with PK-1's diagnostic naming the pack's first failing label
(`attitude:factive…`, `attitude:entails…`). F-AT1 is conflict-free under the assembled X. F-AT8 (SR-1): a base
predicate `unsaid__weapons_uplift_permitted` in a `knows` content, with `weapons_uplift_permitted` unspecified,
passes `checkAtt` but not `WellFormedU`, so `frame_unsaidFree` needs `hw`. Refresh: every legacy pack list
(`[]`, `[soft]`, `[soft, rights]`) answers byte-identically, the point check included; an author's
`attitudes__knows__1` is refused as PK-1's fixture A4 refuses it.

Deleted, not duplicated: no second status or conflict semantics; `SettledAsX` is the one missing counterpart of
`UndecidedAtX` and is defined from the same parts.

Shared files: as the refresh paragraph above lists (draft 5: the one provider registration line on `Layered.lean`).
In-flight overlap: none from `rd-9-int` or PK-1, which have merged; checked again with `git diff --name-only` before
the batch.

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
  decoder. The guard-node decoder accepts scope's `own` placeholder at the content position, so scope's sc-2b can
  state that `substOwn` passes through it (E1's missing lemma; grid Sc × At; synthesis round 2). Without
  `attitudes@0`, W1's, soft's and P0's decoders are unchanged: an attitude node gets today's answer
  (`array expected`) in today's fault order, and the new text `UnsupportedProfile: an attitude condition needs
  attitudes@0` is answered only by `decodeAttDoc` (SR-6; spec 5.1).
- **The attitudes kinds' decoder.** `decodeAttDoc` decodes the document, the `environment.attitudes` block and the
  case's English lexical data (`lexicon`, optional `overlay`), the last with the English grammar's own decoders
  (`Env.decode`, `Overlay.decode`, `Run.decodeLexicon`), here and not only in AT-5, because `attitudes-elaborate`
  answers a wording template per key (SR-3). Its last step is `checkAtt`, so it returns only checked documents
  (`decodeAttDoc_wellFormed`, SR-7); otherwise the first failing check's diagnostic is the kind's answer.
- **Kinds (refresh, Astra r1 3, r2 2).** One new kind, `attitudes-elaborate`, registered as a row of the current
  kind table, `layeredRows` in `lean/VE/Defaults/Route.lean` (beside defeasible's `defaultsRows`), needing the
  `attitudes` pack. Status, conflict and report are today's layered kinds, which already read the whole X; the point
  check is AT-2's, for the attitudes pack. Draft 5's `attitudes-status`, `attitudes-conflict` and
  `attitudes-report` would duplicate today's kinds and are removed (premise-packs.md 7 left the question to AT-0), so
  one owner answers each kind. `attitudes_elaborate_acceptance` is stated for the new kind and
  `attitudes_status_sound` for today's status kind (spec 6.3). The kind's shape and encoder theorem go into the
  layered route's response-shape files.
- **Registration (refresh).** `attitudes@0` is one row of AR-10's profile-gate table (`VE.Compose.profileTable`)
  with its composition proof, for the real table: AR-10's gate is conjunctive, so the drafted row
  (`requires := ["norms@0"]`) admits `[attitudes@0, norms@0, relational-fol@0]` and breaks `attitudes_row_composes`.
  The row's admission enforces the supported combinations only (completion chain or readings chain, never
  `reports@0`): both chains carry `norm-defaults@0`, so the row requires `norm-defaults@0` and `norms@0`, and a
  search over 512 profile lists finds no counterexample (spec 2.9, 7.3); the theorem's route parameter is `VE.Compose.Route`, the type `gateOf` answers (spec 2.9, 6.3).
  There is no hand edit to `ve/profiles.py`. AT-3a registers the row (requires `norms@0` and `norm-defaults@0`;
  refuses `reports@0`) with the slot `pack` (profile-composition PC-3), replacing the wording "norms-chain extra
  premises" (synthesis round 2). The row gives the reason text only (`attitudes@0 with reports@0 is not admitted`);
  `gateOf` alone writes the `UnsupportedProfile:` prefix. The other `UnsupportedProfile:` texts of this plan and
  its spec (`decodeAttDoc`'s off-profile text; `checkAtt`'s D4, D9, D0 and D14c) are decoder refusals, not the
  gate's, and keep their prefix.
- **The hook on main (refresh).** The guard-node hook reuses `normFields` (`lean/VE/Norms/Wire.lean:319`), the one
  decoder of a norm's envelope, and keeps soft decoding's `shared := false` budget (`SoftNorms/Phases.lean:242`).
  Both Lean admission paths (`Norms/Admission.lean:58`, `SoftNorms/Admission.lean:25`) call these decoders, so one
  hook suffices, and SR-6's fixture covers both.
- **Dependencies.** PK-1, pk-1b, AR-10a, `lf-16e`, `qa-q2`, `fix-main-relay`, AP-1 and AP-3 have merged (refresh), so
  AT-3a waits only for AT-2. Draft 5's integration order on `Layered.lean` is dropped (AT-2 above); the pack's
  position inside X is PK-1's fixed order: after weighing, before scales.

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
frame (label, formula), each key's and label's request origin, and the elaborated guards. Statuses, conflicts and
reports are today's layered kinds over the assembled X (refresh; draft 5 named three kinds of its own for them).

Statements (restated for the layered kinds, edit 7; refresh: `packPremises` over `L.packs`, as spec 6.3):

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
    Sat d.S.M.asStructure ((VE.NormDefaults.Packs.packPremises L.packs "attitudes").map (·.2)) ∧
    (∀ b, d.status = .settled b → SettledAsX.{0} L.U L.X d.S.M.asStructure d.r d.vs b) ∧
    (d.status = .undecided → VE.NormDefaults.Wire.UndecidedAtX.{0} L.U L.X d.S.M.asStructure d.r d.vs)
end VE.Attitudes.Wire
```

(`packPremises` is PK-1's accessor, `lean/VE/NormDefaults/Packs.lean:64`: one pack's labelled premises in a list of
packs, `[]` when the pack is absent. The existing
`ResponseShape.Encoders.NormDefaults.runCaseReported_fits` keeps its statement; its skeleton gains the new kind's
row. `attitudes_row_composes` is spec 6.3's, with `r : VE.Compose.Route`.)

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
`docs/spec/assurance-manifest.md`, `lean/checkers.lock`, `docs/trust-baseline.json`, AR-10's generated profile
data, all through `tools/regen_generated.py` (R12).

**Trust growth (refresh).** Draft 5 reserved "a DRI signature, ruling D3" for any growth of
`docs/trust-baseline.json`. Standing rulings cover the expected cases, so none is reserved: growth of at most 150
lines (K+S+V) of new Lean behaviour is signed by **R16** when the DELTA row itemises it per file, re-measured on the
final HEAD with `tools/trust_map.py`, every new trusted definition is exercised by a test that can fail, and a
FOLLOW-UPS row asks for the ties pass; growth that replaces a Python decision path the same change deletes is
signed by **R6**, with the allowance and its reason in the trust budget file (as AT-1w's and AT-5's deletions are).
The `trust_map.py --write --reason` record is kept. Only growth beyond those bounds (growth that replaces no
deleted path and is over 150 lines or in K) goes to the DRI.

In-flight overlap: none from `lf-16e`, `qa-q2` or `fix-main-relay`, which have merged (refresh); checked again with
`git diff --name-only` before the batch.

Bytes: 0.

### AT-3b. Document call site, relay and tests (Lean and Python, 5–6 h, estimate)

**Refresh (Astra r1 4; Fable r1 4).** `lf-16g` has merged and deleted the Python document loader (`ve/document.py`
is now the package `ve/document/`), and SC-1b took the first document-mode slot as a Lean call site. Lean owns
admission. So AT-3b is:

- **Lean:** the `attitudes@0` call site in Lean's document mode, `lean/VE/Service/Document.lean`, after SC-1b's;
  Lean admits the document and answers.
- **Python:** `ve/document/` relays the typed answer, bound to the request (R8), with the binding below; anything
  else is `CheckerUnavailable`, never a Python verdict.
- **Binding inventory:** before relaying, AT-3b adds the attitudes answer's rows to the rd-9 relay-binding
  inventory (`docs/spec/rd-9-relay-binding.md`, `INVENTORY` in `tests/test_relay_binding_inventory.py`), its owner
  by the DRI's D9 ruling (2026-10-28): every field classified as bound or Lean-derived, each bound field fuzzed.

Seeded bugs in both languages it changes (CLAUDE.md): the Python one below, and one in its Lean call site. The text
below is draft 5's, kept where it still holds; its "Python only" and "Python `ve/document*.py` today" are superseded.

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

Shared hand-written files: Lean's document mode `lean/VE/Service/Document.lean` (the call site), the relay in
`ve/document/` (refresh; draft 5: "Python `ve/document*.py` today; Lean's `document` mode if `lf-16e` has moved
it"), `tests/test_relay_binding_inventory.py` and `docs/spec/rd-9-relay-binding.md` (the rows),
`tools/layer_policy.py` (the layer of `ve/attitudes.py`). Generated: `tests/data/route-cases.jsonl` (recorded by
`tests/route_case_recorder.py`), `.importlinter` (`tools/check_python_layers.py --write`); no committed gate
collection (refresh: `tools/gate-collection.json` is no longer on main).

Seeded bugs (recorded with file and failing test): Python, the binding check that a label names its premise's mode
accepts any label, so `tests/test_attitudes_answer.py` must fail, then the check is restored; Lean, one in the call
site (refresh: the batch now changes Lean too).

In-flight overlap: none from `lf-16e` or `lf-16g`, which have merged. The document-mode queue after `lf-16g` was
AT-3b, SC-1b, QT-A4, ET-5, WG-4, ME-10 (edit 7); SC-1b has taken the first slot, so AT-3b comes after it (refresh).

Bytes: 0 by itself; AT-6a measures.

### AT-6a. Pilot: the strict companion with typed attitudes (pilot tooling, 3 h)

In `readings/all-strict.ve.md`, replace AT-0p's fourteen open terms with attitude conditions (D2's guard) and seven
hand-named intention terms ("…intentionally does the weapons uplift in that situation", F4), declare `attitudes@0`
and `environment.attitudes = {"holders": ["claude_instance"], "scale": [], "decided_by": "unstated"}`; the
cases carry the companion's English lexicon, as AT-3a's decoder requires (SR-3).
Re-run the unspecified probe and the conflict check. Report, measured: the points of the seven rules (expected: the
audit's case SETTLED no; unknowing UNDECIDED; impossible points refused, where AT-0p measured UNDECIDED, P1 2 A4),
the open terms (expected 21 for the seven rules: 14 generated, 7 hand-named; the companion from AT-0p's measured 44
to **about** 51), predicates used, time (one run, not a comparison), `DELTA` against AT-0p's run. No model calls. The
main translation is unchanged until AT-6b. The report says it checks structured input, not English: the zero-training
claim is accepted only after AT-5 and an audit of the English Lean renders (debate round 3).

Queue (edit 10): AT-6a's edits to the seven units land after SC-2 and start from the translation as SC-2 left it.
Where SC-2 has moved AT-0p's open terms into the u0173.s01 governor's condition, AT-6a replaces them there, with
`own` as the attitude content, not in the seven item guards. **Refresh (Fable r1 6, r2):** SC-2's attitude-word part
is its split-off **sc-2b**, which waits for AT-3a; AT-6a waits for sc-2b, not only SC-2, and starts from the pilot
translation as sc-2 and sc-2b leave it. It keeps u0165.s03's wide and narrow candidates. The expected open-term
count is +7 on that run (section 2, D-A10), not "44 to about 51".

Bytes (**estimate**): 0 claimed; the typed form of 874 B on the companion.

**DRI go/no-go** (F7). After AT-6a, the DRI decides whether AT-4, AT-6b and AT-5 proceed, on AT-6a's measured
results and the next audit's verdict on AT-0p's seven units. **Refresh:** that verdict is in (A8 MET in four audits),
so only AT-6a's results are left. What WG-5 waits for, and what a no-go leaves, is section 10 item 5 (Astra r2 5,
Fable r2 1): under the approved queue (edit 10, DRI AP2) WG-5's dependent rewrite follows AT-6b and AP-3 Group A,
so it waits for the "go", AT-4 and AT-6b; on a no-go, the dependent rewrites stay blocked.

### AT-4. The readings chain with the `attitudes` pack (Lean and Python, 4–5 h, estimate)

Files: `lean/VE/Attitudes/Readings.lean` (new); `ve/readings.py` passes the `attitudes` block through only. The
readings decoder's call reduces to the `attitudes` pack provider's registration plus the shared guard-node hook
(edit 7). `transfers_append` is PK-1's (edit 6), and with `transfers_X` it is on main as
`VE.Readings.transfers_append` (`lean/VE/Readings/SupPacks.lean`, merged in `b30b12f74`), which AT-4 imports; no
further PK-1 readings batch is needed (refresh, Astra r2; Fable r2 withdrew "readings half not built"). The
re-estimate (4–5 h, was 5–6) reflects that; `frame_transfers` stays as attitudes' provider obligation, with its
typing hypothesis discharged by a proved typing lemma instead of assumed (A2); `att_nd_superpose_*` are stated at the
assembled family, the frame at its `packOrder` place between the earlier packs `P` and the later packs `R`.

```lean
import VE.Attitudes.Route
import VE.Readings.SupExtra
import VE.Readings.SupPacks

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
**Refresh:** all three have merged, so AT-4 waits only for the "go" and AT-3b.

Bytes: 0 by itself; AT-6b measures.

### AT-6b. Pilot: the main translation with typed attitudes (pilot tooling, 3 h)

The same change as AT-6a in `translation.ve.md` (three "should" reading sets, superposed route). Report, measured:
conflict status over the eight choices; the denial and claim-to-be-human conclusions (expected unchanged); the seven
rules' points; open terms; predicates; the companion probe's decided units. Ask the next audit to sample the seven
units. If the scope design has landed, u0173.s01 is attached to the seven rules and claimed (263 B, **estimate**).
The "intentionally" readings are faithful only through the act-performance bridge (ET-D2); until then, AT-6b
reports them as residual (edit 3). Queue: as AT-6a (edit 10); after AT-6b, the DRI's AP2 slot for AP-3 Group A, then
WG-5 (refresh; section 10 item 5).

### AT-5. English in Lean (Lean and Python, 5–6 h)

Files: `lean/VE/Attribution/Words.lean` (new: the four report verbs and synonyms, with the reasons now in
`ve/report_english.py`; `reports@0`'s English does not depend on the newer profile, F6), `lean/VE/Attitudes/Words.lean`
(new: imports it and adds only `knows` and `thinks`), `lean/VE/Attitudes/English.lean` (new: wording templates for
generated predicates, composed from the content predicate's own template; the frame lines; the glossary line of
each degree word), the Lean English grammar's admission of the 3.7 rows (files in `lean/VE/EnglishGrammar/` that
AT-0 names). AT-5's refusals (`NegatedFactive`, `NegRaising`, bare "thinks that", `AttitudeAdverb`, an unresolved
holder) and their rewrites are rows in english-lean's catalogue, each with its category and its candidate readings
(SR-5); AT-5 adds no separate refusal table (edit 9). **Refresh (Fable r1 5; Astra r1 5):** that catalogue is
en-sw's `lean/VE/EnglishGrammar/SourceWords.lean` (DRI 2026-10-28, PLANS-INDEX C1; not on main), so AT-5 waits for
en-sw and adds its rows there in en-sw's row type; `NegatedFactive`'s candidate readings are generated by
presupposition's projection (DRI PS-NF), which AT-5's rows consume. `lean/VE/Attribution/Words.lean` exists from AT-1w (with
`VE.Reports.wantsPhrase?`); AT-5 adds the verbs to it, in namespace `VE.Reports` (C14). Every renderer and reader reads the document's own lexicon (`A.lex`) and
calls the English grammar's lexicon functions and `wantsPhrase?`, with no template classifier of its own (SR-3).
Whole-sentence fixtures (A4): `readRuleAll` of the 3.1 sentence and of each of the seven pilot guards has length 1;
round-trip of conditions alone is not enough.

```lean
namespace VE.Attitudes
/-- Rendering then reading an admitted attitude condition gives it back, under the document's own lexicon (SR-2). -/
theorem att_english_roundtrip (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : (Γ, c) ∈ condsOf A ++ partsOf A) : readCond A Γ (renderCond A Γ c) = .ok c
/-- Two admitted conditions of one document and context with one sentence are one condition (SR-2). -/
theorem renderCond_injective (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c c2 : Cond)
    (hc : (Γ, c) ∈ condsOf A ++ partsOf A) (hc2 : (Γ, c2) ∈ condsOf A ++ partsOf A)
    (he : renderCond A Γ c = renderCond A Γ c2) : c = c2
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
**Refresh:** `qa-q2` has merged; AT-5 now waits for en-sw (`SourceWords.lean`), the "go" and AT-3b.

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
- E3's outcome is written as one row in `lean/VE/EnglishGrammar/SourceWords.lean` (en-sw): "we want Claude to …" /
  "we think Claude should …" read as the reading set {report; report and soft rule} or as the report alone, as E3's
  bar decides (synthesis round 2).
- Nothing about the soft rule's force is concluded (weighing owns it).

**Frames and candidates (at-rev, AT-R3).** E3's row covers two frames, and only where the sentence is a unit of its
own, not a scope governor's lead-in, with the author as holder: "we want Claude to VP" and "we think Claude should
VP". Its candidates are `report` = `{"parts": [A]}` and `report-and-rule` = `{"parts": [A, R]}` (profile-composition
rule 8): A the author's attitude part (a closed node, spec 2.2; for "want", a closed `wants` part, AT-R1), R the soft
rule "every instance of Claude should VP". Neither candidate holds a scope effect, so PC's rule that a governor's
effect holds "under every choice" of a set on its unit is not engaged. Under "we think Claude should VP" the report's
content is normative and its mode bare "think", both refused (3.7, 3.7a), so A, and with it both candidates, stay
pending (rows `unknown`, rule 8). Not covered by the row, each a GAP where it occurs:
- **a list lead-in** ("we believe all current Claude models should be:", u0014.s03): a governor's frame holds under
  every choice of the set (profile-composition specification 3.5, PC-5: "under every choice of that set"), and withholding it under
  `report` orphans each item's part (scope's `ScopeOrphanPart`), so the report-only candidate has no construct and is
  **withdrawn**. A set left with one candidate is no set; the governor and its frame are scope's, and the author's
  attitude over the list has no PC form (AT-8's one-reading rule): GAP, owner attitudes with scope;
- "we believe … should …" and other modes than the two frames' (u0014.s03): not the row's wording;
- "we want Y to VP" with another subject than Claude, including a term of Claude's own (u0035.s12's "Claude's
  helpfulness"): not the row's wording; E3's record may extend the row by a plan change with its own review;
- negated frames ("we don't want Claude to …", u0246.s04) and "we want to VP" (the author as agent, u0287.s01): no
  admitted content (3.7a).

**Boundary with purpose-explanation (refresh, Astra r2 4; Fable r2).** Purpose-explanation's D7 assigns "we want
Claude to …" to attitudes and attaches its purpose links to whatever E3 produces, so E3's outcome is an input to that
plan, recorded as a dependency. These sentences are also the census's main AT/DF disagreements (the DRI's caveat).
Closed in synthesis round 2: E3 and AT-8 own "we want Claude to …"; purpose-explanation's D7 attaches its links to
whatever E3 yields. It is a boundary, not a duplicate (section 3.11).

### AT-8. Holder reports in norm documents (Lean and Python, 5–6 h)

Owner: attitudes (synthesis round 2). AT-8 also covers bare reports such as "Anthropic believes P". Its
{report; report and soft rule} sets (u0173.s02, u0067.s07) use PC-11's `CrossContent` `attitude` case; there is no
new case, and AT-8 comes after PC-11 (DRI DEC 13).

**Inside a composed document (at-rev, AT-R2).** `reports@0` stays refused beside the chain (profile-composition rule
7, until EXP-O1's bridge; AT-3a's row refuses `attitudes@0` with `reports@0`), so AT-8 writes no `{"report": …}` unit,
no `contexts` block and no `attributed` kind there. A holder report is an attitude candidate, the form PC already
admits and its rule 16 reaches: its node is a closed attitude part (spec 2.2, `AttDoc.parts`), checked by
`checkParts` and claimed by `partClaim` (spec 2.5, 2.6), in a reading set on its unit:
- E3's two frames: {report; report-and-rule} (E3, at-rev AT-R3);
- an author's belief, "we believe that P" or "Anthropic believes that P": {belief; fact}, PC-11's F11.5 shape, the
  attitude candidate or P asserted.

The candidate registers one position, PC-11's `attitudeKind`: the node's content as written. A reference inside it
("our" in "our understanding", u0244.s01; "its" in "its very foundations", u0287.s01) is resolved there by RESOLVE
before AT-2 elaborates the node, by S4's rules (a possessive of the author resolves to the author's constant; a
reference with two candidate targets is READINGS or UNFORMALISED, never guessed), and a judged word there is read by
the judgment reader. The holder ("we") is kept, not a position: AT-8 writes the author's declared constant, as F11.5
writes "we" out. A holder report with one reading only (E3's "report alone" outcome, a third party's bare report, the
attitude over a list lead-in) has no PC form inside a composed document: a set left with one candidate is no set,
and the `attitude` case is no unit content. It stays UNFORMALISED there, with a GAP line (owner attitudes). A unit
content of kind `attitude` would be a new PC kind; this revision does not request one (the conservative direction).

**Withdrawn (at-rev, AT-R2).** Draft 6's top-level report units beside rules, decoded with `reports@0`'s own decoder
on the attitudes route, and their theorem `reports_in_norms_conservative` (over `ReportKeysUnused` and `expandR`) are
withdrawn: the attitudes route is the chain, beside which `reports@0` stays refused, so AT-8 builds neither, and
draft 6's "its own review" of that composition is replaced by this section. The composition attribution.md 11.3
defers stays deferred, outside this plan, until a bridge admits `reports@0` beside the chain (EXP-O1).

Bytes (**estimate**): upper bound about 31 kB over the 183 units (183 × 169 B); the expected gain is far lower and
depends on E3, on the contents' own features, and (at-rev) on the one-reading reports that stay UNFORMALISED.
Purpose-explanation's links attach to its units through E3 (above).

### AT-9. Numeric bands on the scale (Lean, 3–4 h, on risk stage B's trigger)

`Scale` gains optional declared ranges per word; a declared range orders words it covers (a range wholly above
another implies the pair). Risk stage B reads its bands from `VE.Attitudes.Scale` instead of declaring its own.
Theorem: `bands_order_sound` (a declared pair agrees with the ranges). Bytes: 0 on the pinned pilots.
Ruling (synthesis round 2, DECISIONS item 1): attitudes owns `VE.Attitudes.Scale` and the frozen table; risk stage
B reads its bands through AT-9 (decided, no longer this plan's proposal). Attribution's `May(a, q)` and
`Probably(a, q)` keep their built meaning and stay unrelated; no `reports@0` answer changes. Ordered implications
("likely" entails "possible") apply only to hedge premises admitted through the hedge bridge (3.12), never to report
assessments.

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
| AT-0p | — (**landed**, DRI AT2) | (pilot directory only); first in the hard-constraint queue `AT-0p → SC-1b → SC-2 → AT-6a/AT-6b → WG-5` (edit 10) | — |
| E1, E2 | — (**run and met**, DRI AT1) | none (research scripts and evidence under `research/attitudes/`, `docs/research/evidence/attitudes/`) | — |
| AT-0 (refreshed) | — | none (docs and the stub `docs/spec/attitudes/SpecStubs_attitudes.lean`) | — |
| AT-1w | refreshed AT-0 PASS | `lean/VE/Attribution/Run.lean` (one `reports` kind), `lean/ResponseShape/Schemas/Reports.lean`, `lean/ResponseShape/Encoders/Reports.lean` (skeleton row), `ve/reports_route.py`, `ve/reports.py`, `ve/report_english.py` (`lean/VE/Attribution/Words.lean` is new here, namespace `VE.Reports`, with `wantsPhrase?` only; SR-3, RC-4, C14) | `reports.json`, route cases, as AT-1 |
| AT-1 | AT-1w (QS-1 merged) | none | `lean/VE.lean`, `lean/VE/Audit.lean`, frozen inventory, axioms, statements |
| AT-2 | AT-1; profile-composition's EXP-G1 (after PC-3) (PK-1, pk-1b merged) | `lean/VE/NormDefaults/Packs.lean` (the prefix row, `OriginsExact`, `packEntry`, `furtherEntries`), `replayStatusX` (the point check), the `layered_elaborate` shape's further-entries key and its relay (premise-packs.md 2.7) | as AT-1, the layered response schema |
| AT-3a | AT-2; PC-6 (after CI-5) (PK-1, AR-10a, `lf-16e`, `qa-q2`, `fix-main-relay`, AP-1, AP-3 merged) | `lean/VE/Norms/Wire.lean` (the hook on `normFields`) and the soft norm decoder, the kind table `layeredRows` in `lean/VE/Defaults/Route.lean` and the response-shape files, the AR-10 row, `ve/assurance-manifest.json`, `conformance/binding_probes.py`, `ROADMAP.md` | layered response schema, `ResponseShape` roots and audit, assurance doc, checker pins, trust baseline (R16 or R6, section 4 AT-3a), AR-10's profile data |
| AT-3b | AT-3a (`lf-16g`, SC-1b merged; next in the document-mode queue after SC-1b) | `lean/VE/Service/Document.lean` (the call site), the relay in `ve/document/`, the rd-9 relay-binding inventory (`tests/test_relay_binding_inventory.py`, `docs/spec/rd-9-relay-binding.md`), `tools/layer_policy.py` | route cases, `.importlinter` |
| sc-2b (scope's) | AT-3a | scope's files | scope's |
| AT-6a, AT-6b | AT-3b, sc-2b and the pilot translation as sc-2 and sc-2b leave it (AT-6a); AT-4 (AT-6b); the hard-constraint queue | (pilot directory only) | — |
| AT-4 | the DRI's "go"; AT-3b (`lf-14d`, RD-9, `lf-16e`, PK-1 with `SupPacks` merged) | the pack provider's readings registration, `ve/readings.py` | as AT-1, route cases |
| AT-5 | the DRI's "go"; AT-3b; en-sw (`lean/VE/EnglishGrammar/SourceWords.lean`); first in the English queue `AT-5 → QT-A6 → ME-11 → QT-B3 → SC-7` (`qa-q2` merged) | `lean/VE/Attribution/Words.lean` (AT-1w's, gains the verbs, F6), English grammar files, `SourceWords.lean` rows, `ve/report_english.py`, possibly `tools/regen_generated.py` | English grammar lock (needs a person's `--actions-version`), codes |
| AT-7 | AT-4 | AT-3a's decoder (own file) | as AT-1 |
| AT-8 | E3; PC-11 (DEC 13) | AT-3a's decoder (own file), `ve/attitudes.py` | as AT-1 |
| AT-9 | risk stage B trigger | `lean/VE/Attitudes/Scale.lean` (own), risk stage B's files | as AT-1 |

**Order on the constitution path (synthesis round 2).** CI-5 → PC-6 before AT-3a; profile-composition's EXP-G1
runs after PC-3 and before AT-2 and WG-3; AT-0 → at-1w → AT-1 → AT-2 → AT-3a → sc-2b / AT-3b → AT-6a.

How conflicts are avoided: every Lean batch writes new files under `lean/VE/Attitudes/`; the hand-written shared
Lean files are the guard-node hook on `lean/VE/Norms/Wire.lean` and the soft norm decoder (serialised after AP-1 and
AP-3), AT-2's PK-1 files (the prefix row, the further-entries key, the point check in `replayStatusX`; refresh: not one provider line,
and PK-1's integration order no longer binds, since et-4 may register `events` first and `packOrder` fixes X), the
layered route's kind table, the AR-10 row, AT-3b's document-mode call site and inventory rows, `lean/VE/Attribution/Words.lean` (new in AT-1w, extended in AT-5), and AT-1w's `reports` kind with its
shape, relay and `ve/report_english.py` (the `reports@0` files). The seven pilot units change in
the hard-constraint queue's order, each step starting from the translation as the previous step left it. Generated
inventories are never hand-edited or hand-merged (ruling R12; `tools/regen_generated.py --resolve` finishes a merge
whose only conflicts are generated). Overlap is checked before each batch with `git diff --name-only
main...<branch>` against the in-flight branches named above. Landing preference: AT lands after AP and before
SC-1/SC-2 (SC-2 needs AT-3a's decoder; edit 10). Refresh: AP-1, AP-3 and SC-1b have merged, and SC-2's attitude part
is sc-2b, after AT-3a.

**Batch order after the refresh (Astra r1, r2 5; Fable r2; Astra's order, which Fable took).**

1. Refreshed AT-0 PASS (section 4 AT-0).
2. AT-1w.
3. AT-1.
4. AT-2.
5. AT-3a.
6. sc-2b and AT-3b.
7. The pilot translation as sc-2 and sc-2b leave it (scope's pilot integration).
8. AT-6a.
9. The DRI's go/no-go (F7).
10. AT-4.
11. AT-6b.
12. Under the approved queue (edit 10, DRI AP2): AP-3 Group A, then WG-5's dependent rewrite (section 10 item 5).

AT-5 follows the "go", AT-3b and en-sw. AT-7, AT-8, AT-9, E3 and E4 are unchanged. Merged or in-flight work is not
re-blocked: only sc-2b's attitude-word fixture waits on AT-3a. **For the queue owner (not this plan's file):**
sc-5rc's dependency row in the feature plan is updated to match this order, without re-blocking merged or in-flight
work (Astra r1; Fable r2).

Sibling designs: **scope** (u0173.s01 attached to the seven rules, needed for its 263 B), **events-time-causation**
(the act-performance bridge, ET-D2); act-phrases supplies act identity only (edit 3), **weighing** (u0173.s02's
"more holistic and nuanced prioritization", u0145.s05), **quantities** (vague degrees other than likelihood,
"serious uplift"; this plan's scale covers likelihood words only), **events-time-causation** (u0173.s04's
"contributing", "deceive into thinking").

## 6. Expected effect per batch

AT-0p's row is **measured** (phase 1, P1 2), and its audit-verifiable bytes too (A8 MET; refresh); every other row
is an **estimate** until its pilot batch measures it. Refresh: AT-6a and AT-6b start from the translation SC-1b, SC-2
and sc-2b leave (the newest run, `run-20261028T0600Z`, has 49 open terms), so their counts are stated as changes on
that run.

| Batch | Claimed bytes | Audit-verifiable bytes | Answers |
|---|---:|---:|---|
| AT-0p (measured) | 0 new; 2,951 unchanged | 874 (7 units): FAITHFUL in four audits (A8 MET; refresh) | 7 audit-case points UNDECIDED → SETTLED no; open terms 33 → 46 (companion 44); the 7 impossible points stay UNDECIDED |
| AT-0 to AT-3b | 0 | 0 | none (no pilot uses them yet) |
| AT-6a | 0 | 874 typed (companion) | impossible points refused (AT-0p: UNDECIDED); open terms +7 at AT-6b on the main translation it starts from, +7 on the companion (21 for the seven rules: 14 generated, 7 hand-named; refresh: draft 5 counted from AT-0p's 46 and 44, before SC-1b, SC-2 and sc-2b) |
| AT-4 + AT-6b | 0, or 263 with the scope design | 874 typed (main) | the "intentionally" readings stay residual until the act-performance bridge (edit 3); with premise 3, `guard_collapse` shows the guard's verdicts do not depend on the hand-named intention term |
| AT-5 | 0 | 0 | the sentences of 3.1 writable in English |
| AT-7 | 0 now; up to 1,070 | — | — |
| AT-8 | 0 until E3; upper ≈ 31 kB | — | — |
| AT-9 | 0 | — | — |
| E4 | research | — | part of 13,379 B (section) |

NORTH-STAR row 8 (0.1920 from tags) recomputed on this basis: the buildable part's upper bound is about 0.036
(5 × 1,333 / 184,893; R 2.8). **Refresh, from the census (2026-10-28):** attitudes is the last uncovered family of
62 units, 9,364 B, once every queued row lands, an upper bound of about 0.051 of the document (9,364 / 184,893) on
what attitudes alone could complete; each unit still needs a faithful translation and an audit. AT's any-role
involvement (551 units, 105,469 B) is not an unlock estimate, and the soft primary share (33,574 B, about 26.1 kB
Opus-corrected) is not used to size or rank batches. Costs: E1 and E2's 2,480 model calls are spent; the rest is the
builders' 40 to 48 hours of section 4 (**estimate**), with no model calls.

## 7. Not claimed, open questions, risks

- **Not claimed:** that Claude knows or thinks anything in any case; any threshold for "quite likely"; any coverage
  before the pilot batches measure it; that proxy readers stand for human readers; that structured-input validation
  (AT-6a) shows the English is zero-training. Hedged calculation claims ("probably less than one sixth",
  math-evidence H-6p) are not attitude conditions. They need a separate, reviewed calc–attitudes bridge, which no
  plan owns yet. Attitudes landing does not lift math-evidence's `hedged` labels (edit 5). Refresh: the DRI has since
  given that bridge to attitudes (2026-10-28, PLANS-INDEX C17): a wrapper over `VE.Attitudes.Scale` around the
  requesting family's unit; synthesis round 2 decided its placement (C22, section 3.12): refused until H-4
  discharges the gate. Until then, the labels stay.
- **Open (for AT-0):** the guard-node hook point on `lean/VE/Norms/Wire.lean` and the diagnostic when
  `attitudes@0` is off; whether the layered status kind checks the point against every X premise; whether the
  `english-codes` generator can carry the word table; the readings decoder's registration point after `lf-14d`.
  (Answered in spec draft 1 and 2, section 10; the off-profile diagnostic is today's, SR-6. Refresh: spec draft 5's
  section 10 restates them against main: the hook on `normFields`; the point check is AT-2's for its own pack;
  document dispatch is a Lean call site; the readings route's registration after `lf-14d`, which has merged.)
- **Closed (RC-4):** draft 3 left open whether the `wants` test could exist in Lean and in Python between AT-1 and
  AT-5. The re-check found that interval breaks the one-owner rule. AT-1w, before AT-1, moves the test and deletes
  its Python copy in one merge, so it never exists twice; a batch of its own, since AT-1 with a relayed kind would
  exceed six hours.
- **Open (for the DRI):** how the residual displays 21 open terms (14
  generated, 7 hand-named); whether "is aware that" may be an input synonym of "knows that" (only if E2-style
  agreement is shown; else refused with that rewrite); the go/no-go after AT-6a (F7); an amendment of the
  hard-constraint queue for WG-5, if wanted (section 10 item 5). Not open: WG-5's place under the approved queue,
  which edit 10 and AP2 fix.
- **Closed (refresh): the DRI's AT1 confirmed G1–G6 unchanged and authorised the calls; E1 and E2 ran (section 9).**
  As draft 5 had it: **Open (for the DRI, before E1 and E2's first call; draft 5):** confirm or change G1 (pair direction), G2 (one
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
  terms (section 10, item 4). Refresh: resolved by the DRI's AT4 (auditors get the records; english-lean owns the
  rendering), and A8 has met. New: AT-2 grows beyond its draft-5 size (section 4), and en-sw, which AT-5 now waits
  for, is not yet on main.

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
| AT-0p, landing in the pilot | **LANDED** (refresh; DRI AT2; DEFERRED in phase 1, the pilot directory being read only) | SC-1b (queue 4.4); A8 | the pilot runner's next constitution run: `research/attitudes/at0p.py` (copy, apply) on that run's inputs, then the run's own `nd.py all`, probe and conflict checks |
| AT-0p, A8: the 7 units (874 B) audit-verifiable | **MET** (refresh): FAITHFUL in four audits, 15 Oct 18Z, 19 Oct (AT3's added audit), 26 Oct and 27 Oct; DEFERRED in phase 1 | 874 B audit-verifiable; one of the two inputs of the DRI's go/no-go after AT-6a (F7) | the pilot's next audit of a run with AT-0p landed, given the open-term records with the rendering (section 7, risks); its timing in queue 4.4 is section 10, item 3 |
| E1 | **Run 2026-10-13: MET** (E1E2 4.1). Lower bound confirmed for almost certain, very likely, quite likely, likely, more likely than not (40 of 40 each); not for as likely as not, unlikely, very unlikely (0 of 40). All 10 pairs among the five enter `above` (40 yes, 0 no each); the other 18 pairs have 0 yes | `table.lowerBound` (which words "thinks it *w*" admits), `table.above` (frame premise 4); through the closure review, AT-0 PASS | — (AT1 authorised it with G1, G2, G5, G6 unchanged; G6's no-cap rule and its self-check cases added before the first call, `a8e5ae57`) |
| E2 | **Run 2026-10-13: MET** (E1E2 4.2). Premise 1 ships (40, 40, 40), premise 2 ships (40, 40, 40), premise 3 for all five `lowerBound` words (40 each). "P, and X does not know that P" **admitted**: "Must P?" 40, 39, 40 yes; "Does Claude know that P?" 40, 40, 40 no | `table.factive` (if it fails, `knows` is not admitted at all), `table.knowsBelieves`, `table.knowsThinks`, the admission of "P, and X does not know that P"; through the closure review, AT-0 PASS | — (AT1; G5's three items and G6's agreement rule added before the first call, `a8e5ae57`) |
| E2's negated-"know" and "unless" items | **Run** with E2. Negated "know": item 1 splits (15 yes, 6 no, 19 cannot tell), item 2 agrees on cannot tell (38), item 3 on yes (40): the reading depends on the content, and the refusal stands. "unless": 40 of 40 yes on all three | nothing: both forms stay refused whatever they show (D-A7); evidence for a later admission's own review | — |
| Closure review and freezing `table` | **Done 2026-10-13** (E1E2 4.3): G4 removes no word; Lean's `Table.reviewed` through the stub pinned by sha256 `2178fb6e…` is `true`; the frozen table is `docs/research/evidence/attitudes/e-table.lean` | the frozen meaning of `attitudes@0`; AT-0 PASS (SR-8) | — |
| AT-0 stub at the current draft, fixtures and search on the frozen table | **Done 2026-10-13** (AT0C, below): the stub carries spec draft 4's Lean with the frozen `table`, is committed, pinned by sha256 `0c73f880…`, and elaborates with every `#guard` holding; every fixture and the search rerun on `table`, the asserted-not-know form (F-AT9) in the pool; no counterexample | the re-review's input; AT-0 PASS (SR-8) | — |
| AT-0 re-review of the changed statements | **FIX 2026-10-14** (`manage-agents/attitudes-at0-review.final.md`): two B findings (the admitted row's one derivation; its AT-5 fixtures) and one C (the seed count); corrected as spec section 17's RR-1 to RR-3 (AT0C 5), the stub re-pinned `dea412eb…` | AT-0 PASS | — |
| AT-0 PASS | **blocked** on the refreshed AT-0 (refresh; draft 5: on SR-8's last step) | AT-1w and every later batch; through AT-3a, sc-2b (synthesis 4.3) | done: the statements draft 5 had marked *to restate* written and elaborated, fixtures and search rerun (spec 7.3, 18); left: the reviewers' check of RR-1 to RR-3 ([docs/research/attitudes-at0-changed.md](../research/attitudes-at0-changed.md) section 5, AT0C) and of every statement spec section 18 lists. Draft 5's "RR-1 to RR-3 only" is no longer enough (section 4 AT-0) |
| Refresh's stub (2026-10-28) | **Done**: the stub `dea412eb` restored, pinned at `docs/spec/attitudes/SpecStubs_attitudes.lean` with QS-1's, PK-1's and AR-10's stand-ins replaced by imports and the refresh's statement changes, the restatements RF-5 to RF-7 included (sha256 `3575da56…`); elaborated against main `6d0a10526` with no error and every `#guard` holding; its output identical to the pinned run's except D5's QS-1 text, plus spec 7.3's 41 lines of refresh fixtures; the search's counts unchanged (`docs/spec/attitudes/stub-run-20261028.txt`) | the refreshed AT-0's input | — |

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
were caught (AT0C 1). The re-review of AT0C section 2 (2026-10-14) returned FIX; its two B findings and one C are
corrected as spec section 17's RR-1 to RR-3 (AT0C 5): the admitted row read whole, with the statement
`assertedNotKnows_one_reading`; AT-5 read fixtures for the row and the refusal's boundary; the seed count relabelled.
Three more seeded bugs were caught (AT0C 1). Left: the reviewers' check of RR-1 to RR-3 only, then spec draft 5.
**Refresh (2026-10-28):** spec draft 5 is the refresh's (its section 18), and what is left is the refreshed AT-0
(section 4 AT-0). The evidence directory `docs/research/evidence/attitudes/` and `research/attitudes/` (with
`experiments.py`'s stub pin) are on `research/attitudes-p1` at `923f0a0ea`, not on this branch; the refreshed AT-0
restores them where it merges.

## 10. Cross-plan issues for the DRI

Phase 1 changes none of the shared parts: the owners (synthesis section 1, edit 8), the shared items (PK-1, AR-10's
table, QS-1, ET-D2) and the build order (synthesis 4.1–4.4, edits 7, 9 and 10) stand as written above. Where a
phase-1 result bears on them, it is recorded here, for the DRI, and not edited into the shared part.

**Refresh (2026-10-28; Fable r1, r2; Astra r2 5).** Items 1–4 are **resolved by the DRI's rulings AT1–AT4**
(2026-10-13): AT1 authorised E1 and E2 (run, met); AT2 landed AT-0p at the next constitution run; AT3 chose option
(a), an added audit of u0165.s01–s07 between AT-0p and SC-1b (held 19 Oct); AT4 gave auditors the open-term records
and english-lean the rendering of an open term's description. They are kept below as written, and nothing in them is
reserved for the DRI any more. Item 5 is new.

1. **Resolved by the DRI's AT1** (E1 and E2 authorised and run, 2026-10-13; section 9). As written in draft 5:
   **E1 and E2 did not run in phase 1, so phase 2's AT-0 review cannot close.** Synthesis 4.1 puts E1 and E2 in
   phase 1 and AT-0's statement review in phase 2; AT-0 PASS needs E1's and E2's results (SR-8). Through the
   explicit dependency "AT-3a's guard decoder lands before SC-2" (4.3), and SC-2 writing u0173.s01's governor with
   attitude nodes (scope's edit 3), queue 4.4's third step and scope's 263 B claim wait on these 2,480 model calls,
   unless another of AT-3a's prerequisites (PK-1, AR-10's table, `lf-16e`, `qa-q2`) is later. Decision needed:
   when to authorise E1 and E2 (section 7), or how to reschedule; this plan does not move them.
2. **Resolved by AT2.** **Queue 4.4's first step is measured, not landed.** SC-1b starts from AT-0p's translation (C23, scope's edit 3).
   Phase 1 confirms what SC-1b will find: in each of u0165.s01–s07, the guard `(C_i(s) ∧ knowingly_engages_i(c, s))
   ∨ thinks_quite_likely_i(c, s)`, with `restricted_action_knowing_or_quite_likely` gone (P1 2;
   `at0p-measure.json`, `seven_units`). No conflict with the order; but SC-1b cannot start until the pilot runner
   lands AT-0p (section 9). Decision needed: when the pilot runner's next constitution run lands it.
3. **Resolved by AT3 (option a).** **The go/no-go's audit input and the queue's order.** F7's go/no-go after AT-6a reads the next audit's verdict
   on *AT-0p's* seven units. Queue 4.4 lands SC-1b and SC-2 on the same units before AT-6a, and SC-2 moves the
   attitude conjuncts out of the item guards. An audit run after SC-1b or SC-2 has landed judges their version, not
   AT-0p's. Not changed here; two options for the DRI: (a) an audit of the seven units between AT-0p's landing and
   SC-1b's (an added audit point; the queue's order unchanged), which this plan recommends, since it isolates
   AT-0p's effect; or (b) accept an audit of the queue's later state as F7's input, and say so in F7's record.
4. **Resolved by AT4.** **Open terms are rendered by identifier** (P1 2, observation): "… has the recorded relation
   "thinks_quite_likely_1" to that situation", not the term's description or factors. Every plan in queue 4.4 that
   adds hand-named open terms to the seven units (SC-1b, SC-2, WG-5, WG-8, QT-B4) and their audits meet it, and the
   synthesis assigns the document rendering of open terms to none of the seven plans. Decision needed: who owns the
   fix (rendering an open term's description, or giving auditors the open-term records), so that A8 and the later
   audits judge the rules rather than the identifiers.
5. **WG-5's start and the no-go case (new, refresh; Fable r2 1, Astra r2 5).** M10 (feature plan: "WG-3, AT-2/AT-3a,
   then WG-5", early to mid November) reaches WG-5 through the hard-constraint queue. Under the approved queue,
   which standing rulings fix and this plan does not reopen, WG-5's dependent rewrite of u0165.s01–s07 starts from
   the translation AT-6b leaves, after AP-3 Group A's slot (edit 10; DRI AP2). So it waits for the DRI's "go", AT-4
   and AT-6b (about 7 to 8 builder hours after the go, **estimate**), and on a **no-go** it does not start: the
   dependent rewrites stay blocked. Neither draft 5 nor either reviewer's order said so. Only an amendment of the
   queue is a decision for the DRI, and no standing ruling covers one: (a) WG-5 after AT-6a and before AT-6b, which
   Fable recommends, since AT-6a leaves the main translation unchanged and each step would still start from the
   previous step's translation; or (b) a companion-only WG-5, which Astra notes needs an amended queue. Until the DRI
   amends it, the plan follows the approved queue.
