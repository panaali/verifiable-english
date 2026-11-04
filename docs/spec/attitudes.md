# Typed attitudes as conditions of norms (`attitudes@0`): statement spec (AT-0)

**Changes in this draft (at-0-finish, DRI 2026-11-02 at-0 items 1-4).** Draft 8, branch `refresh/attitudes-20261028`
on draft 7. It finishes AT-0's statement spec by the decider's ruling (`manage-agents/reviews/dri-decisions-20261102-at-0.md`,
SIGNED) and adds no other design; section 19's DR-11 lists every change.

1. **The attitudes route's decoder** (sections 2.9, 4, 5.1, 6.3, 7.3, 7.6): `decodeLayeredAtt`, a wrapper above
   `Layered.lean`, runs the existing decoder and assembles `attitudesPack`. `decodeSoftU` and `decodeRightsU` do not
   change.
2. **`attitudes_elaborate_acceptance`** (section 6.3): `hp` added, `hL` kept and read through the wrapper.
3. **The review's agreed edits** (sections 5.1, 6.2, 6.3, 12) and **OPEN-4 ruled** (section 19).

**Changes in draft 7 (at-rev, DRI 2026-11-02 fp-attitudes item 1), kept as history.** Draft 7, branch `refresh/attitudes-20261028`
on draft 6 (`2b60e7bfb`). It applies the attitudes fidelity pilot's findings AT-R1 and AT-R2 where they reach
statements (`manage-agents/reviews/dri-decisions-20261102-fp-attitudes.md` item 1; AT-R3 and AT-R4 change the plan
only) and nothing else; section 20 lists every statement that changes.

1. **AT-R1, a closed `wants` set part** (sections 2.2, 2.3, 2.5, 2.6, 3.1, 4, 5.2, 6.1, 6.5, 7.1, 7.5): the document
   carries its reading-set parts (`AttDoc.parts`, PC-11's `attitude` case, DEC 13(a)); each is checked as a closed
   condition (`checkParts`), named with the rules' keys and claimed at its holder (`partClaim`); D14c words a closed
   `wants` of one unary base predicate on a constant there, and only there. Fixture C-e, u0035.s12's shape.
2. **AT-R2, a holder report beside the chain** (sections 1, 4): written as an attitude candidate, never as a
   `{"report": …}` unit; `reports@0` stays refused beside the chain. The "own review" deferral is gone.

**Changes in draft 6 (AT-0, 2026-11-02), kept as history.** Draft 6, branch `refresh/attitudes-20261028`. It reconciles this spec
with PLAN draft 6 and elaborates the stub on main `9ba2140e2`. No design is added: section 19 lists every change,
and what the plan leaves open is an **OPEN** line there for the DRI.

1. **The decider token is `unstated`** in the stub as well as here (syn2code-attitudes-4, C2).
2. **Against main's interfaces** (sections 1, 2.9, 7.3): `Pack` gained `conditions`, `ProfileRow` gained `interface`
   (PC-3), and en-sw's `SourceWords.lean` merged. `attitudesPack` and `attitudesRow` take main's forms.
3. **Stale text reconciled with the plan** (sections 1, 2.1, 9, 10, 12, 13): the D2 ruling, the purposes boundary,
   "possible", the signed AT-3a order, scope's `own`, the search's rerun result.
4. **The row's checks widened** to 4,096 lists (section 7.3), with computed answers for `reports@0`, `alternatives@0`,
   `ve.discourse@1` and the at3a-order fixture.
5. **The statement review's FIX** (`manage-agents/debates/at-0/`, rounds 1–2; section 19's FR-1 to FR-6): the kind's
   acceptance theorem on `layeredKindCase`, `:` refused in generated names, `decodeAttDoc`'s off-profile text, the row's
   count, `pointCheck` moved to `Packs.lean`.

**Changes in draft 5 (refresh 2026-10-28), kept as history.** Draft 5, branch `refresh/attitudes-20261028` (main `6d0a10526` plus
this spec and its plan, from `research/attitudes-p1` `923f0a0ea`). It applies the converged staleness review
(`manage-agents/debates/refresh-attitudes-20261028/`, verdict REFRESH, converged after round 2; cited **Astra r1/r2
n** for item n of that reviewer's proposed joint position in round 1 or 2, and **Fable r1/r2**) and nothing else.
Section 18 lists the statements this refresh changes, for AT-0's re-review.

1. **E1 and E2 are done; `table` is the frozen table** (status, sections 2.1, 12, 13): E1 MET and E2 MET
   (2026-10-13, [attitudes-e1e2.md](../research/attitudes-e1e2.md)), `table` as frozen there and in the pinned stub,
   `Table.reviewed` true. Drafts 1–4 still showed the empty table (Astra r1 1, r2 3; Fable r1 1).
2. **The stub is restored, pinned and refreshed** (status, sections 0, 13): the stub `dea412eb` from `923f0a0ea` is
   committed at `docs/spec/attitudes/SpecStubs_attitudes.lean`; QS-1's, PK-1's and AR-10's stand-ins are replaced by
   imports of their merged modules, and it is elaborated against main `6d0a10526` (Astra r1 1, r2 3; Fable r2).
3. **Diagnostics as main answers them** (section 5.2): D5 is QS-1's own text, `ResourceLimit: At most 64 order
   pairs`; D0 and D4 as AT0C recomputed them on the frozen table (Astra r1 1).
4. **PK-1 as built** (sections 1, 2.9, 6.2–6.4, 10; PLANS-INDEX C7): `attitudesPack` has `consts := []`; the
   reserved-prefix row is the pair `("attitudes", "attitudes__")`; assembly is `assemble U used`; one pack's premises
   are `(packPremises L.packs "attitudes").map (·.2)`; `transfers_append` and `transfers_X` exist in
   `lean/VE/Readings/SupPacks.lean` (Astra r1 2, r2 1; Fable r1 3, r2).
5. **Generated names are declared once, in `envAtt`** (sections 2.4, 2.9, 6.2, 7.3): drafts 1–4 declared them in
   `envAtt A`, the environment of `toU A unspec`, and again in `attitudesPack A`'s `decls`, which `assemble` refuses
   (`… is already declared`, PK-1 fixture A4; computed on F-AT1). Resolved before any name is inserted: the pack is
   a `constraint` pack with no names, as soft's and rights' are, since `U`'s guards need the names declared (Astra r1
   2, r2 1; Fable r2).
6. **AT-2 is more than one registration line** (sections 2.9, 6.2, 7.3, 10 item 2): PK-1 leaves its first provider
   the entries (`packEntry`, `furtherEntries`, their shape key), `OriginsExact`, the environment and expansion
   obligations and the point check for its own pack (premise-packs.md 2.7, 3, 5, 7). With item 5's policy they are
   restated and elaborated: `envX` is today's base environment (nothing threaded), a `constraint` pack owes no
   `ExpandsOn`, `OriginsExact` holds over the labels, and `pointCheck` checks the attitudes premises only. PK-1's
   diagnostic placement and collision-witness exception apply (section 5.3) (Astra r1 2, r2 1; Fable r2).
7. **The profile row and its theorem** (sections 2.9, 6.3, 7.6): gate rows are conjunctive, so the row with
   `requires := ["norms@0"]` admits `[attitudes@0, norms@0, relational-fol@0]`, which makes `attitudes_row_composes`
   false. The row now requires `norm-defaults@0` and `norms@0`, which both supported chains carry; a search over
   512 profile lists finds no counterexample to the unchanged theorem; the gate's answer is a `VE.Compose.Route`
   (Astra r1 3, r2 2; Fable r2).
8. **One new kind** (sections 4, 6.3): `attitudes-elaborate` registers through the current kind table
   (`layeredRows`, `lean/VE/Defaults/Route.lean`); the duplicate status, conflict and report kinds are removed, since
   today's kinds read the whole X (Astra r1 3, r2 2).
9. **The guard-node hook on main** (section 10 item 1): `normFields` (`lean/VE/Norms/Wire.lean:319`), keeping soft
   decoding's `shared := false` budget; both Lean admission paths call the decoders, and SR-6's fixture covers both
   (Astra r1 3; Fable r1 6).
10. **Document mode** (section 10 item 3, 7.6): `lf-16g` deleted the Python loader; AT-3b is a call site in
    `lean/VE/Service/Document.lean` (after SC-1b's) with a typed, bound relay in `ve/document/`, and rows in the rd-9
    relay-binding inventory (Astra r1 4; Fable r1 4).
11. **Owners and shared pieces** (section 1): the report verbs' module is `VE.Attribution.Words`, new in AT-1w, with
    namespace `VE.Reports` (C14); refusal rows go to en-sw's `lean/VE/EnglishGrammar/SourceWords.lean` (C1);
    `NegatedFactive`'s candidates come from presupposition's projection (PS-NF); the hedge wrapper is attitudes' (C17);
    D2's overlap and purpose-explanation's D7 boundary are recorded; new interfaces are marked NEW (Astra r1 5, r2 4;
    Fable r1 5, r2).

> **Status.** Draft 6, 2026-11-02. AT-0's statement spec for [attitudes-PLAN.md](attitudes-PLAN.md) draft 6. E1 and
> E2 ran and MET (2026-10-13); `table` is frozen (section 2.1). The stub is pinned at
> `docs/spec/attitudes/SpecStubs_attitudes.lean`, sha256 `068912b3…`, and elaborated against main `9ba2140e2`, with
> no error and every `#guard` holding; every fixture and the search are rerun on it (sections 9, 13, 19). AT-0 PASS
> needs the statement review of `manage-agents/debates/at-0/`: RR-1 to RR-3 (section 17), every statement section 18
> lists, and section 19's changes. The OPEN lines of section 19 do not gate AT-1w: each is the DRI's or a later
> batch's. The history below is kept as written.
>
> **Draft 5's status (2026-10-28), kept as history.** Draft 5, 2026-10-28 (refresh). AT-0's statement spec for
> [attitudes-PLAN.md](attitudes-PLAN.md) draft 6. E1 and E2 ran and MET (2026-10-13); `table` is frozen (section
> 2.1). The stub is pinned at `docs/spec/attitudes/SpecStubs_attitudes.lean` and elaborated against main
> `6d0a10526`, with the restated statements (freshness, the AT-2 contracts, the profile row's admission) and every
> fixture and the search rerun on them (sections 13, 18). AT-0 PASS needed the reviewers' check of RR-1 to RR-3
> (section 17) and of every statement section 18 lists.
>
> **Draft 4's status (2026-10-13), kept as history.** Draft 4, branch `research/attitudes-p1`. AT-0's statement spec for
> [attitudes-PLAN.md](attitudes-PLAN.md) draft 5 (cited as **PLAN**; its debate items as **A1–A6**, **F3–F7**, the
> cross-plan synthesis edits as **edit 1–10**). For AT-0's statement review; nothing here is built or proved.
> Draft 4 applies phase 1 ([docs/research/attitudes-phase1.md](../research/attitudes-phase1.md), cited as **P1 n**;
> its gaps in the pre-registration as **G1–G6**), listed in section 16; it changes no Lean statement or definition.
> Section 17 applies AT-0's bounded re-review (`manage-agents/attitudes-at0-review.final.md`, **FIX**), cited as
> **RR-1 to RR-3**: one statement and its definitions are added (section 6.5), and AT-5 fixtures (section 7.6).
> Drafts 1 to 3 were written on branch `design/attitudes`.
> Draft 2 applies the statement review of draft 1 (Astra and Fable, `manage-agents/debates/attitudes-spec/`,
> converged after round 3 on **FIX; the build may not start**). Its corrections are cited as **SR-1 to SR-8** and
> listed in section 14; draft 2 makes them and no other change. Draft 3 applies the re-check of draft 2
> (`manage-agents/attitudes-p3ver1.final.md`, **FAIL**: SR-1, SR-2, SR-4, SR-5, SR-7 and SR-8 present and correct,
> three problems remaining). Its corrections are cited as **RC-1 to RC-4** and listed in section 15; draft 3 makes
> them and no other change.
>
> **What was checked, and how.** Draft 1's definitions and statements were type-checked in the untracked stub
> `lean/SpecStubs_attitudes.lean`, each statement as `def <name> (binders) : Prop := <conclusion>` (the stub
> prefixes unused binder names with `_`), by `lake --dir /home/seyran/code/ve-nightly/lean env lean
> lean/SpecStubs_attitudes.lean` against the build of `main` at `49de179e`, this branch's base (the branch adds
> docs only). Draft 1's fixture numbers were computed by `#eval`, `#guard` or `decide` in that stub, not by hand.
> **Draft 2's and draft 3's changes are not elaborated**: the stub in the worktree is still draft 1's, and every
> definition, statement, diagnostic text and fixture value that section 14 or 15 lists as changed or new is written
> here, not computed. They are marked *expected* where a value is given. Elaborating a statement is not evidence that it holds:
> a small-scope counterexample search (section 9) found none on draft 1, and only AT-1's proofs will establish the
> statements. No model calls were made.
>
> **Not passable yet.** AT-0 PASS needs, in this order (SR-8): E1's and E2's outcomes written into `table` with
> their items, including E2's decision on the asserted-content negated knowledge row (section 3.1's last row,
> section 11 item 16); the closure review holding on the frozen table; the stub updated to the current draft (draft
> 3's Lean, which draft 4 keeps; section 13) and elaborated; every fixture and the section 9 search re-run on the
> frozen table, with the new refusals (D6a–D6b, D14a–D14d) in the search's pool; and the reviewers' re-review of
> the statements sections 14 and 15 list as changed, and only those. Until E1 and E2 report, the frozen `table`
> admits nothing: `knows` and every "thinks it *w*" are refused (fixture D0, section 5). The fixtures use `fixtureTable`, a hypothetical E1/E2 outcome written only for
> fixtures. Phase 1 prepared E1 and E2 (items, seeded orders, scorers with the PLAN's bars, and the emitter of the
> `Table` literal reviewed by this spec's `Table.reviewed`) but ran neither: both need model calls, and both are
> **DEFERRED** until the DRI confirms their protocol (G1–G6, PLAN section 4) and authorises the calls (PLAN section
> 9). So SR-8's first step has not started.

**Changes in draft 4 (from phase 1), kept as history.** No Lean statement, definition, diagnostic or fixture value
changes, so the stub needs no edit for this draft (it is untracked, outside this worktree, and pinned by sha256 in
`research/attitudes/experiments.py`; section 13).

1. **E1 and E2: DEFERRED** (status above; section 12's row). `table` stays empty and reviewed.
2. **The closure resolution has one rule** (section 2.1, G4): a derived entry whose item failed removes the weaker
   word from `lowerBound`, with every pair and premise naming it, until `Table.reviewed` holds; with several such
   entries, the weakest offending word goes first, one per round, since another order can leave a different
   reviewed table (self-check case with three violations; 24 checks, all hold). The debate-round-3 items for
   entries derived without a direct item are empty by construction (P1 3).
3. **"P, and X does not know that P" is admitted only if six E2 items reach 36 of 40** (section 3.1's last row,
   section 11 item 16; G5): three "Must P?" and three "Does X know that P?". Draft 3's three items tested only that
   P is read as asserted.
4. **AT-0p's A4 measured** what F-AT1's M2 shows in Lean: without typing, the impossible point is UNDECIDED in all
   seven pilot rules (P1 2); with the frame, M2 fails factivity (section 16).
5. **Section 13** records the stub's sha256 pin; the status's "stub updated to draft 2" now reads "to the current
   draft", as PLAN draft 4 already said; **section 16** is new and lists these changes.
6. **Section 8's predicate count** names the count the limit uses: `MAX_PREDICATES` (256) bounds the declared
   plus the unspecified predicates (norm-defaults 5.1, "filled"): 65 at the pinned run (50 declared), 78 in AT-0p
   (63 declared), **about** 85 with the seven intention terms. Draft 3's "68 … about 88" was the readings route's
   size count, which adds the route's own three generated predicates (bit declarations and decisions, `sizesJson`)
   to the filled count.

## 0. Reading this spec

- Section 1 says who owns what. Section 2 defines the profile in Lean. Section 3 gives the English, with one reading
  per wording. Section 4 is the wire. Section 5 lists the diagnostics in order. Section 6 states the theorems of
  AT-1 to AT-5. Section 7 lists the fixtures with their computed values, and section 9 the counterexample search.
  Section 10 answers the integration questions the PLAN left to AT-0. Section 11 lists every place where this spec
  differs from the PLAN's Lean text, with the reason. Section 12 is the review checklist. Section 14 lists draft 2's
  corrections (SR-1 to SR-8), section 15 draft 3's (RC-1 to RC-4), section 16 draft 4's (phase 1), section 17
  the AT-0 re-review's (RR-1 to RR-3), section 18 the refresh's and section 19 draft 6's, with its OPEN lines, each
  with the places it changes.
- Names owned by other plans are used through their reviewed interfaces only. QS-1's `VE.Closure.Order`, `Caps`,
  `Order.admit`, `Order.atLeast` (`lean/VE/Closure/Order.lean`, owner: quantities), PK-1's `PackKind`,
  `RequestPath`, `Pack`, `packOrder`, `packPremises`, `assemble` (`lean/VE/NormDefaults/Packs.lean`, owner: the RD-9
  composition owner) and AR-10's `ProfileRow`, `profileTable`, `gateOf`, `Route` (`lean/VE/Compose/Dispatch.lean`,
  owner: AR-10) are merged, and the refreshed stub imports them (refresh, Astra r2 3); drafts 1–4's stand-ins for them
  are gone. The functions new in AT-2 (`keyOrigin`, `labelOrigin`), AT-3a (`decodeAttDoc`, `encodeElaboration`) and AT-5
  (`renderCond`, `renderAssertedNotKnows`, `readCond`, `readGuard`, `readGuardAll`, `readRule`, `readRuleAll`,
  `refusalOf`) are stand-ins; their bodies are those batches' work. So is `VE.Reports.wantsPhrase?`, `reports@0`'s
  `wants` test, which AT-1w, the batch before AT-1, moves into the new module `VE.Attribution.Words`
  (`lean/VE/Attribution/Words.lean`) in the namespace of attribution's declarations, `VE.Reports` (section 2.6,
  section 10 item 6; SR-3, RC-4; refresh, C14). The English
  grammar's lexical data (`VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`, `Lexicon.failures`, `Env.predicate?`) is
  used as it is on `main`. A changed interface reopens only the statements that name it.

## 1. Owners

| Piece | Owner | Here |
|---|---|---|
| The four report acts and their names | `VE.Reports.Act`, `Act.name` (`reports@0`) | reused as `Mode.act` |
| Their English verbs and synonyms | `lean/VE/Attribution/Words.lean`, module `VE.Attribution.Words`, namespace `VE.Reports` (planned, not on main: AT-1w creates it with the `wants` test, SR-3, RC-4; AT-5 adds the verbs, F6; refresh, C14) | `VE.Attitudes.Words` imports it and adds only `knows` and `thinks` |
| Content identity | syntax-tree equality (`VE.Reports.content_structural`) | reused; no hashing |
| De-duplication of keys | `VE.Reports.dedup` | reused |
| Quantifier-free formulas | `VE.Norms.Formula.qfree` | reused (A5) |
| Order closure, caps | QS-1: `VE.Closure.Order`, `Order.atLeast := reachEval .star`, `Caps`, `Order.admit`, `atLeast_refl`, `atLeast_trans`, `reachable_star_iff` | `Scale.atLeast` is `Order.atLeast`; no second closure (edit 1) |
| Likelihood words, `table`, E1/E2 gating, `lowerBound`, the record of which item passed each entry, the closure review | attitudes (`VE.Attitudes.Scale`) | section 2.1 |
| Extra base premises on the layered and readings routes | PK-1 packs (`lean/VE/NormDefaults/Packs.lean`: `Pack` with `consts`, `assemble U used`, `reservedPrefixes` as (owner, prefix) rows, `packPremises`); `VE.Readings.transfers_append`, `transfers_X` (`lean/VE/Readings/SupPacks.lean`) | attitudes is the `attitudes` provider (edit 6), with the first provider's obligations of premise-packs.md 2.7, 3 and 5 (section 2.9; refresh, C7) |
| Profile registration | AR-10's profile-gate table (`VE.Compose.profileTable`, `gateOf`, answering a `VE.Compose.Route`) | one row, slot `pack`, interface `.pack "attitudes"` (PC-3), with admission aligned to `attitudes_row_composes` (edit 7; refresh) |
| Layered kinds | the kind table `layeredRows` (`lean/VE/Defaults/Route.lean`, PK-1's `KindRow`, `dispatch`) | one row, `attitudes-elaborate`, needing the `attitudes` pack; status, conflict and report are today's kinds over the whole X (refresh) |
| Refusals and their rewrites (English), source-word reading sets | english-lean: `lean/VE/EnglishGrammar/SourceWords.lean`, built by en-sw (on main, `sourceWords` empty; its row type `SourceWordRow`; PLANS-INDEX C1) | rows added by AT-5 (edit 9), each with its category and candidate readings (SR-5); how section 3.4's rows fit `SourceWordRow` is OPEN-1 (section 19) |
| `NegatedFactive`'s candidate readings | presupposition's projection (DRI PS-NF) | AT-5's rows consume them; attitudes does not compute a projection (refresh) |
| Relay binding of an attitudes answer | the rd-9 relay-binding inventory (`docs/spec/rd-9-relay-binding.md`, `INVENTORY` in `tests/test_relay_binding_inventory.py`; PLANS-INDEX D9) | AT-3b adds the attitudes rows before relaying (refresh) |
| English lexical data: sort nouns, predicate wordings, constant spellings, and their validity | the English grammar: `VE.EnglishGrammar.Env`, `Overlay`, `Lexicon`, `Lexicon.failures`, `Lexicon.valid` (`lean/VE/EnglishGrammar/Lexicon.lean`); decoded by `Env.decode`, `Overlay.decode`, `Run.decodeLexicon` | carried as `AttDoc.lex`; checked by D6a–D6b, and per condition by D14d (RC-1); read by D14c, `renderCond` and the readers (SR-3) |
| The `wants` verb-phrase test ("Y to VP") | `reports@0`: `_subject_split` and `_infinitive` (with `_finite`, the form `_infinitive` checks against) in `ve/report_english.py:85–131` (Python only on `main`, 6d0a10526) | moved into Lean as `VE.Reports.wantsPhrase?` (module `VE.Attribution.Words`) by AT-1w, before AT-1's check D14c calls it; AT-1w also deletes the Python copy, `reports@0`'s Python English reading both forms from Lean, so the test has one owner at every merge (RC-4, section 10 item 6); D14c and `renderCond` call it; no attitude-local classifier (SR-3) |
| Intentional action ("intends to VP") | residual; events-time-causation's ET-D2 designs the bridge (the performance boundary) | not admitted (edit 3) |
| Distribution over joined acts | act-phrases, deontic modals only | none here (edit 4) |
| Hedged calculation and causal claims | attitudes: the hedge bridge (DRI 2026-10-28, PLANS-INDEX C17; C22 decided in synthesis round 2, DECISIONS item 2): hedges-generics' `lean/VE/Hedges/Bridge.lean` structures move under attitudes, with the frozen scale | not attitude conditions (edit 5); hedged calc, count and causal units refused until hedges-generics' H-4 discharges the gate (below; PLAN 3.12) |

**Shared pieces (refresh).** Reused or in conflict, to resolve with their owners: PK-1 as built (C7, above); the
report verbs' module and namespace (C14, above; `attitudes@0` and `reports@0` refuse each other); the likelihood
words (D2, ruled in synthesis round 2, DECISIONS item 1: attitudes owns `VE.Attitudes.Scale` and the frozen table,
risk stage B reads its bands through AT-9, attribution's `May(a, q)` and `Probably(a, q)` keep their built meaning and
stay unrelated, and ordered implications apply only to hedge premises admitted through the hedge bridge, never to
report assessments); source-word rows (C1); relay binding (D9). **The hedge bridge (synthesis round 2, NEW; PLAN 3.12).** Holder-free, in attribution's
assessment shape: one generated unary predicate per (meaning, word) on an assessment constant, no author holder, no
`thinks w` (generation logic shared with attribution is factored under attribution and called here). The hedge
elaboration declares one fresh context sort, one constant and the unary atoms per (meaning, word) in the base
environment before `toU`, under the reserved prefix `attitudes__`, as `envAtt` does (RF-5); AT-3a lists the hedge
sort and atoms in `envAtt`'s pattern; the `attitudes` pack stays `.constraint` with no names and carries
`bridgePremises` only; `packOrder` is unchanged; the sort counts once against `sortCap := 8`. Gate: H-4 proves,
before any hedged foreign unit is admitted, typing, name freshness, vocabulary charging, `hedge_conservative` over
empty (`Option`) carriers, `hedge_entails_base` and compatibility with the layered route (`envAt` hides layer
symbols only, `Norms/Tree.lean:173`). The wrapped unit is named by the document model's NEW `UnitRef` (Lean
recomputes `meaning` per family, H-5). Fallback, not built: `Pack.sorts` under a PK-1 item, only if H-4 cannot
discharge its theorem on this route. Boundaries kept: presupposition owns projection (PS-NF); ET-D2 owns act performance; AT-8
comes after PC-11 and uses `CrossContent`'s `attitude` case (DEC 13): inside a composed document a holder report is an
attitude candidate whose node is a reading-set part (section 4), never a `{"report": …}` unit, and `reports@0` stays
refused beside the chain (profile-composition's rule 7; at-rev, AT-R2; PLAN AT-8).
Purpose-explanation: closed in synthesis round 2 as a boundary, not a duplicate. E3 and AT-8 own "we want Claude to
…", and its D7 attaches its links to whatever E3 yields; the census's AT/DF disagreements fall on these sentences.
**NEW** here, owned by attitudes: the attitude guard node, the `attitudes` pack, the
likelihood `Scale` and its frozen `table`.

## 2. Definitions

All Lean in this section is in `namespace VE.Attitudes` with `open VE.Reports (Act)` and `universe u`, in the order
the stub elaborates it. AT-1 places it in `lean/VE/Attitudes/{Scale,Syntax,Frame,Semantics}.lean`.

### 2.1 Words, the scale and the frozen table

A **likelihood word** is written after "thinks it", in lower case. A word is **admitted** only if E1's certainty
item confirms its lower-bound reading ("quite likely" read as "quite likely or more"); every other word, including
words that point downward such as "unlikely", is refused (A1). A **scale pair** `(a, b)` reads "a is at least as
likely as b". The **frozen table** records each admitted entry with the pre-registered item that passed it. Its
**closure review** (debate round 3) holds exactly when the reflexive and transitive closure of the frozen pairs
adds no pair, and no premise-3 word, without its own passing item; every entry is between admitted words; and
premises 2 and 3 are present only with premise 1.

**Resolution before freezing (draft 4, G4).** E1 asks all 28 pairs (the earlier word of `e1Words` first, G1) and E2
asks the premise-3 item of all eight words (G3), so every entry the closure can derive has its own item; the
review can fail only on a derived entry whose item failed. Each round collects the **offending words**: for a
derived pair `(a, b)` whose own item failed, its weaker word `b` (the later in `e1Words`, since every pair is asked
earlier word first); for a premise-3 word reached through the closure whose own item failed, that word. The
offending word latest in `e1Words` (the weakest) leaves `lowerBound`, and with it every pair and premise-3 entry
that names it; the closure is recomputed, and this repeats, one word per round, until `Table.reviewed` holds.
**The order is part of the rule.** With several violations, removing another offending word first can leave a
different table that `Table.reviewed` also accepts: if, of the pairs among "almost certain", "very likely", "quite
likely" and "likely", only the chain's three pass, removing "quite likely" first leaves a reviewed table that keeps
"likely", while the rule removes "likely", then "quite likely". Of the PLAN draft 4's two options ("the weaker word
leaves `lowerBound`, or the scale pair is dropped") only the first, with this order, has a unique outcome. The
procedure is `resolve` in `research/attitudes/experiments.py`; its output is accepted only if Lean's
`Table.reviewed` holds on it, so the review stays Lean's. The self-check runs that three-violation case
(`removed_three_violations` = `["likely", "quite likely"]` in `docs/research/evidence/attitudes/e-selfcheck.json`)
and has Lean review both tables, so that the order, not the review, is what makes the outcome unique.

```lean
abbrev Word := String
/-- The id of the pre-registered E1 or E2 item that passed an entry, e.g. "E1.pair.very-likely.quite-likely". -/
abbrev Item := String

/-- `above` lists pairs `(a, b)` read "a is at least as likely as b". -/
structure Scale where
  words : List Word
  above : List (Word × Word)
  deriving DecidableEq, Repr

def Scale.toOrder (σ : Scale) : VE.Closure.Order Word := ⟨σ.words, σ.above⟩

/-- The reflexive and transitive closure of `above`: QS-1's, never a second closure. -/
def Scale.atLeast (σ : Scale) (a b : Word) : Bool := σ.toOrder.atLeast a b

/-- The frozen meaning of `attitudes@0`: each admitted entry with the item that passed it. -/
structure Table where
  /-- E1's words, in E1's order -/
  candidates : List Word
  /-- words whose certainty item passed (E1, at least 34 of 40): the only words admitted after "thinks it" -/
  lowerBound : List (Word × Item)
  /-- `(a, b, item)`: "a is at least as likely as b", passed by its own E1 or E2 item -/
  above : List (Word × Word × Item)
  /-- frame premise 1 (E2's three factivity items); `none`: `knows` is not admitted -/
  factive : Option Item
  /-- frame premise 2 (E2's three knows-believes items); `none`: no such premise -/
  knowsBelieves : Option Item
  /-- frame premise 3, per word (E2's per-word items); a word not listed gets no premise 3 of its own -/
  knowsThinks : List (Word × Item)
  deriving DecidableEq, Repr

def Table.words (t : Table) : List Word := t.lowerBound.map (·.1)
def Table.scale (t : Table) : Scale := ⟨t.words, t.above.map (fun p => (p.1, p.2.1))⟩
def Table.hasPair (t : Table) (a b : Word) : Bool := t.above.any (fun p => p.1 == a && p.2.1 == b)

/-- The closure review: the closure of the frozen pairs adds no pair, and no premise-3 word, without its own
    passing item; every entry is between admitted words; premises 2 and 3 need premise 1. -/
def Table.reviewed (t : Table) : Bool :=
  let ws := t.words
  t.candidates.length ≤ 8 &&
  ws.all t.candidates.contains &&
  t.above.all (fun p => ws.contains p.1 && ws.contains p.2.1) &&
  t.knowsThinks.all (fun p => ws.contains p.1) &&
  ws.all (fun a => ws.all (fun b => a == b || !t.scale.atLeast a b || t.hasPair a b)) &&
  t.knowsThinks.all (fun p => ws.all (fun w => !t.scale.atLeast p.1 w || t.knowsThinks.any (·.1 == w))) &&
  (t.factive.isSome || (t.knowsBelieves.isNone && t.knowsThinks.isEmpty))

def e1Words : List Word :=
  ["almost certain", "very likely", "quite likely", "likely", "more likely than not", "as likely as not",
    "unlikely", "very unlikely"]

/-- The frozen table: E1's and E2's outcomes (2026-10-13), each entry with the item that passed it. -/
def table : Table :=
  { candidates := e1Words,
    lowerBound := [("almost certain", "E1.cert.almost-certain"), ("very likely", "E1.cert.very-likely"),
      ("quite likely", "E1.cert.quite-likely"), ("likely", "E1.cert.likely"),
      ("more likely than not", "E1.cert.more-likely-than-not")],
    above := [("almost certain", "very likely", "E1.pair.almost-certain.very-likely"),
      ("almost certain", "quite likely", "E1.pair.almost-certain.quite-likely"),
      ("almost certain", "likely", "E1.pair.almost-certain.likely"),
      ("almost certain", "more likely than not", "E1.pair.almost-certain.more-likely-than-not"),
      ("very likely", "quite likely", "E1.pair.very-likely.quite-likely"),
      ("very likely", "likely", "E1.pair.very-likely.likely"),
      ("very likely", "more likely than not", "E1.pair.very-likely.more-likely-than-not"),
      ("quite likely", "likely", "E1.pair.quite-likely.likely"),
      ("quite likely", "more likely than not", "E1.pair.quite-likely.more-likely-than-not"),
      ("likely", "more likely than not", "E1.pair.likely.more-likely-than-not")],
    factive := some "E2.factive",
    knowsBelieves := some "E2.knows-believes",
    knowsThinks := [("almost certain", "E2.knows-thinks.almost-certain"), ("very likely", "E2.knows-thinks.very-likely"),
      ("quite likely", "E2.knows-thinks.quite-likely"), ("likely", "E2.knows-thinks.likely"),
      ("more likely than not", "E2.knows-thinks.more-likely-than-not")] }

/-- The bounds on a document's scale (A5): E1's eight words and 64 pairs, checked by QS-1's `Order.admit`. -/
def scaleCaps : VE.Closure.Caps := ⟨8, 64⟩
```

`#guard table.reviewed` holds (section 7.6). The table is E1E2 4.3's (`docs/research/evidence/attitudes/e-table.lean`,
G4 removing no word), as the pinned stub carries it: five words admitted after "thinks it" ("as likely as not",
"unlikely" and "very unlikely" refused), the ten pairs among them, premises 1 and 2, and premise 3 for each of the
five (refresh; drafts 1–4 showed the table before E1 and E2 reported, with nothing admitted).

**"possible" (synthesis round 2; PLAN 3.11).** "possible" is not in `table`. It enters only through attitudes' own
pre-registered items in E1's protocol, which have not run; until they pass, `thinks "possible"` is refused at D9 and
the authors' epistemic "might" stays refused. `Table.reviewed` bounds `candidates` to eight words and `e1Words` has
eight, so a ninth word is a statement change (OPEN-6, section 19).

### 2.2 Modes, conditions, guards, rules, documents

A **mode** is `knows`, `thinks w`, or one of `reports@0`'s four acts. An **attitude condition** names a holder (a
term of the guard), a mode, an optional **slot** (a sort and a term of the guard: the content's variable 0 stands
for that term, de re), and a **content**: a quantifier-free formula over the base vocabulary in context `[s]` (with
a slot of sort `s`) or `[]` (closed). An **attitude guard** is W1's guard formula with attitude conditions as atoms.
An **attitudes document** is W1's document with attitude guards and carve-outs, its holder sorts, the frozen table,
its own scale pairs, its decider, and its English lexical data (SR-3): the English grammar's lexical view of the
environment, its vocabulary overlay and its selected lexicon. Admission, rendering and reading all take that one
lexicon from the document, so they cannot disagree about it. (at-rev, AT-R1) It also carries its **reading-set
parts**: the closed attitude nodes of PC-11's `attitude` case (DEC 13(a), profile-composition's rule 8), each an
attitude condition read in the empty context, so its holder is a constant and it has no slot; `[]` on a document
without a reading set.

```lean
/-- `act a` is the act `a` of reports@0; `knows` and `thinks w` are new. -/
inductive Mode where
  | act (a : Act)
  | knows
  | thinks (w : Word)
  deriving DecidableEq, Repr

def Mode.slug : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks_" ++ w.map (fun c => if c == ' ' then '_' else c)

/-- The mode's English words, for diagnostics. -/
def Mode.words : Mode → String
  | .act a => a.name
  | .knows => "knows"
  | .thinks w => "thinks it " ++ w

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

/-- A W1 rule whose guard and carve-outs may carry attitude conditions. -/
structure ARule where
  name : String
  pred : String
  sign : Bool
  guard : AFormula
  carveOuts : List AFormula
  over : List String
  deriving DecidableEq, Repr

/-- The English grammar's lexical data for one document (SR-3), from its owner `VE.EnglishGrammar`. -/
structure Lex where
  /-- the lexical view of the environment -/
  env : VE.EnglishGrammar.Env
  /-- the vocabulary overlay; `{}` when the case has none -/
  overlay : VE.EnglishGrammar.Overlay
  /-- the selected nouns, wordings, negatives, aliases and spellings -/
  lexicon : VE.EnglishGrammar.Lexicon

structure AttDoc where
  E : VE.Environment
  lits : List String
  /-- the author's declared predicate names, as decoded (the count `MAX_PREDICATES` bounds) -/
  authorPredicates : List String
  regulated : List VE.Norms.Regulated
  definitions : List VE.Norms.Definition
  rules : List ARule
  /-- the holder sorts -/
  holders : List String
  /-- the frozen table; the decoder always sets `table` -/
  T : Table
  /-- the document's own pairs between admitted words -/
  declared : List (Word × Word)
  /-- the decider of every generated open term; "unstated" (the one W2 token, C2) when the document names none;
      rendered legend lines take their wording from the token's owner -/
  decidedBy : String
  /-- the English lexical data; checked by `checkAtt` (D6a, D6b) -/
  lex : Lex
  /-- (at-rev, AT-R1) the closed attitude nodes of the document's reading-set parts (PC-11's `attitude` case), in
      document order; `[]` on a document without a reading set -/
  parts : List Cond := []

/-- The table's pairs and the document's own. -/
def AttDoc.scale (A : AttDoc) : Scale := ⟨A.T.words, A.T.scale.above ++ A.declared⟩
```

### 2.3 Keys and generated names

A **key** is (mode, holder sort, slot sort, content). Two conditions are one attitude exactly when their keys are
equal: content identity is syntax-tree equality, never a hash (D-A3). Keys are listed once each, in document order
(rules, then guard before carve-outs, pre-order; then the reading-set parts, at-rev AT-R1). Each key gets the predicate `attitudes__<mode>__<i>` on its sorts,
`i` the 1-based position among the keys of that mode.

```lean
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

/-- A rule's guard context: its predicate's sorts, the last argument as variable 0. -/
def ruleContext (A : AttDoc) (r : ARule) : List String :=
  match A.regulated.find? (·.name == r.pred) with
  | some d => d.sorts.reverse
  | none => []

def condsOf (A : AttDoc) : List (List String × Cond) :=
  A.rules.flatMap (fun r => (r.guard :: r.carveOuts).flatMap (·.conds (ruleContext A r)))

/-- (at-rev, AT-R1) The reading-set parts, each read in the empty context: a part is closed. -/
def partsOf (A : AttDoc) : List (List String × Cond) := A.parts.map (fun c => ([], c))

def keys (A : AttDoc) : List Key :=
  VE.Reports.dedup ((condsOf A ++ partsOf A).filterMap (fun p => p.2.key A p.1))

/-- `attitudes__<mode>__<i>`, `i` the 1-based position among the keys of that mode. -/
def name (A : AttDoc) (k : Key) : String :=
  "attitudes__" ++ k.mode.slug ++ "__" ++ toString (((keys A).filter (·.mode == k.mode)).idxOf k + 1)

def keyOf (A : AttDoc) (r : String) : Option Key := (keys A).find? (fun k => name A k == r)
```

### 2.4 Environments

`A.E` is the author's whole environment. The **base vocabulary** `baseEnv A` is `E` without the regulated and
defined predicates: the vocabulary `BaseAdmissible` ranges over, and the only one a content may use (A2). `envAtt
A` adds one predicate per key to `E` (the elaborated document's environment); `baseEnvAtt A` adds them to the base
vocabulary (the frame's vocabulary).

```lean
def baseEnv (A : AttDoc) : VE.Environment :=
  VE.Norms.hide A.E (A.regulated.map (·.name) ++ A.definitions.map (·.name))

def envAtt (A : AttDoc) : VE.Environment :=
  { A.E with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => A.E.predicates r }

def baseEnvAtt (A : AttDoc) : VE.Environment :=
  let B := baseEnv A
  { B with predicates := fun r =>
      match keyOf A r with
      | some k => some k.sorts
      | none => B.predicates r }
```

**Freshness against PK-1 as built: one declaration, in `envAtt` (refresh, RF-5).** Drafts 1–4 declared every
key's name twice: in `envAtt A`, the environment of `toU A unspec` (section 2.9), and in `attitudesPack A`'s
`decls`. PK-1's `assemble U used` checks every generated name against `fullEnv U` and refuses one already declared
(premise-packs.md 2.4 check 4, fixture A4); on F-AT1 drafts 1–4's pack answers `InvalidInput: generated name
attitudes__knows__1 of pack attitudes is already declared` (computed, section 7.3). The declaration stays in
`envAtt A`, and the pack declares nothing. The other side cannot keep it: the elaborated guards are inside `U`, so
`U`'s environment must declare the names for `VE.Norms.validate` and `WellFormedU` to type those guards, and a
name `U` declares is one `assemble` refuses from a pack. This is how soft and rights stand today: their generated
names are declared inside `U` by `soften` and `correlate`, and their packs declare none (premise-packs.md 2.6).
So `envAtt`, `baseEnvAtt`, `toNorms`, `toU` and the statements over them (`envAtt_extends`, `toNorms_wellFormed`,
`frame_typed_fill`, `frame_unsaidFree`) keep their text; `attitudesPack` is restated as a `constraint` pack (section
2.9), and `names_in_base` states that `U`'s base vocabulary declares each name with its sorts (section 6.2).

**Not a vocabulary provider (synthesis round 2, N2).** `attitudesPack` stays a `.constraint` pack with
`decls := []`; each generated name is declared once, in `envAtt`, before `toU` (RF-5). PK-1's G1b is not a
prerequisite of AT-2: G1b's trigger is the first pack with non-empty `decls`.

### 2.5 Elaboration

Each condition becomes `attitudes__<mode>__<i>(holder)` (closed content) or `attitudes__<mode>__<i>(holder, t)`
(slot term `t`); the rule becomes an ordinary `VE.Norms.Node`; the document becomes a W1 document over `envAtt A`.
Regulated predicates, completions, act phrases and definitions are unchanged. (`elab` is a Lean keyword, so the
PLAN's `AFormula.elab` and `ARule.elab` are named `toFormula` and `toNode`; section 11.)

```lean
def atom (A : AttDoc) (k : Key) (h : VE.Term) : Option VE.Term → VE.Formula
  | none => .unary (name A k) h
  | some t => .binary (name A k) h t

def AFormula.toFormula (A : AttDoc) : List String → AFormula → Option VE.Formula
  | _, .base φ => some φ
  | Γ, .att c => (c.key A Γ).map (fun k => atom A k c.holder (c.slot.map (·.2)))
  | Γ, .not a => (a.toFormula A Γ).map .not
  | Γ, .and a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.and x))
  | Γ, .or a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.or x))
  | Γ, .implies a b => (a.toFormula A Γ).bind (fun x => (b.toFormula A Γ).map (.implies x))
  | Γ, .all s a => (a.toFormula A (s :: Γ)).map (.all s)
  | Γ, .ex s a => (a.toFormula A (s :: Γ)).map (.ex s)

def ARule.toNode (A : AttDoc) (r : ARule) : Option VE.Norms.Node :=
  (r.guard.toFormula A (ruleContext A r)).bind (fun g =>
    (r.carveOuts.mapM (fun (a : AFormula) => a.toFormula A (ruleContext A r))).map
      (fun cs => ⟨r.name, r.pred, r.sign, g, cs, r.over⟩))

/-- The elaborated W1 document over `envAtt A`. -/
def toNorms (A : AttDoc) : Option VE.Norms.Doc :=
  (A.rules.mapM (fun (r : ARule) => r.toNode A)).map
    (fun ns => ⟨envAtt A, A.lits, ⟨A.regulated, A.definitions, ns⟩⟩)

/-- (at-rev, AT-R1) A reading-set part's claim, PC-11's `attitude φ`: the part's atom at its holder, closed. -/
def partClaim (A : AttDoc) (c : Cond) : Option VE.Formula := (AFormula.att c).toFormula A []
```

A reading-set part is no rule: `toNorms` elaborates the rules alone, and PC-11 owns the part's claim as a candidate
premise gated by its choice atom (`crossSlotParts`). Its key is one of `keys A`, so `envAtt` declares its name and
the frame of section 2.7 covers it: a `knows` part brings its factive premise, a `wants` part none (D-A9).

### 2.6 The well-formedness check

`checkAtt` runs the checks in the order of section 5.2 and stops at the first failure; `WellFormedAtt` is its
success. Its last step is W1's own `VE.Norms.validate` on the elaborated document, so nothing W1 checks is checked
twice. `AWellFormed` is the guard-level condition `att_elaboration_faithful` reads.

**Admission is what English can word (SR-2).** `checkAtt` admits only conditions that section 3.1 can word, so every
admitted key has the wording template that `attitudes-elaborate` answers (section 4) and the legend's line
(section 3.3). After D7–D14 have typed the condition and admitted its mode, `renderable` adds four checks, each
with its own diagnostic: a slot's content mentions the slot (D14a: otherwise `knows ⊤` with an unused slot and the
closed `knows ⊤` are two keys with one sentence); a slot term is a variable of the guard (D14b: otherwise `C(var 0)`
slotted at a constant `s1` and the closed `C(s1)` are two keys with one sentence; write the closed content; telling
de re from de dicto about a named constant is a later admission with its own E2 items); a `wants` content is section
3.1's one `wants` wording (D14c); and every predicate and constant the condition names, in its holder, its slot term
and its content, has its entry in the lexicon, agreeing with `A.E` (D14d, RC-1). The lexicon those checks and the
renderer read is `A.lex`; `checkAtt` validates it with the English grammar's own `Lexicon.failures` (D6a) and checks
that it describes `A.E` (D6b), so `WellFormedAtt` carries both to every statement that assumes it (SR-3). D6b checks
the lexicon's symbols against `A.E`; the converse cannot be checked document-wide, since `A.E.constants` is a
function and cannot be listed, and `A.E` may declare predicates outside `authorPredicates` (fixture D16 does). So
D14d checks it per condition, for the symbols the renderer must word (RC-1). The sorts a condition names need no
check of their own: the holder's sort is a holder sort (D8), holder sorts and the slot sort are sorts of `A.E` (D2,
D10), every sort of `A.E` is in the lexical view (D6b), and each of those has its noun (D6a's V1).

**Reading-set parts (at-rev, AT-R1).** After the rules' conditions, `checkParts` checks each part with the same
checks in the empty context (`checkCond A [] c (part := true)`), so a part whose holder or slot term is a variable
fails W1's `termSort`, and a slot at a constant fails D14b: a part is closed. `part` changes one thing: D14c also
words a closed `wants` whose content is one unary base predicate on a constant, "H wants Y to VP" with `Y` that
constant's spelling (section 3.1). In a guard or carve-out that node stays refused at D14c, as before; a part is
never read there. This is D-A3's own rule (a content about a constant is written closed), which D14c had narrowed
for `wants`: no other content, mode or site is admitted.

```lean
def throwIf (b : Bool) (msg : String) : Except String Unit := if b then .error msg else .ok ()

/-- Whether a quantifier-free content mentions variable 0, the slot. -/
def mentionsSlot : VE.Formula → Bool
  | .unary _ t => t == .var 0
  | .binary _ t u => t == .var 0 || u == .var 0
  | .eq t u => t == .var 0 || u == .var 0
  | .not a => mentionsSlot a
  | .and a b => mentionsSlot a || mentionsSlot b
  | .or a b => mentionsSlot a || mentionsSlot b
  | .implies a b => mentionsSlot a || mentionsSlot b
  | _ => false

/-- A predicate a condition names has its lexicon entry (RC-1): the lexical view declares it with `A.E`'s argument
    sorts, and the lexicon selects its wording. -/
def lexPred (A : AttDoc) (p : String) : Bool :=
  (A.lex.env.predicate? p).any (fun d => A.E.predicates p == some d.args && d.arity == d.args.length) &&
    (A.lex.lexicon.wordings.lookup p).isSome

/-- A term a condition names has its lexicon entry (RC-1): a variable needs none; the lexical view declares a
    constant with its `A.E` sort, and the lexicon selects its spelling. -/
def lexTerm (A : AttDoc) : VE.Term → Bool
  | .var _ => true
  | .const c => (A.lex.env.constants.find? (·.name == c)).any (fun d => A.E.constants c == some d.sort) &&
      (A.lex.lexicon.spellings.lookup c).isSome

/-- Every predicate and constant of a content has its lexicon entry (RC-1). -/
def lexCovers (A : AttDoc) : VE.Formula → Bool
  | .top | .bottom => true
  | .unary p t => lexPred A p && lexTerm A t
  | .binary p t u => lexPred A p && lexTerm A t && lexTerm A u
  | .eq t u => lexTerm A t && lexTerm A u
  | .not a | .all _ a | .ex _ a => lexCovers A a
  | .and a b | .or a b | .implies a b => lexCovers A a && lexCovers A b

/-- The conditions section 3.1 can word, after D7–D14 (SR-2): one definition, whose first failing part is the
    condition's diagnostic. `wantsPhrase?` is reports@0's `wants` test (section 1); the wording it reads is the
    document's selected one. `part`: the condition is a reading-set part (at-rev, AT-R1), where D14c also words a
    closed `wants` of one unary base predicate on a constant; in a guard or carve-out it stays refused. -/
def renderCheck (A : AttDoc) (c : Cond) (part : Bool := false) : Except String Unit := do
  throwIf (match c.slot with | some _ => !mentionsSlot c.content | none => false)
    "InvalidInput: an attitude content does not mention its slot"
  throwIf (match c.slot with | some (_, .const _) => true | _ => false)
    "InvalidInput: an attitude slot term is not a variable of the guard"
  let worded : Bool := match c.mode, c.slot, c.content with
    | .act .wants, some _, .unary p (.var 0) =>
        ((A.lex.lexicon.wordings.lookup p).bind VE.Reports.wantsPhrase?).isSome
    | .act .wants, none, .unary p (.const _) =>
        part && ((A.lex.lexicon.wordings.lookup p).bind VE.Reports.wantsPhrase?).isSome
    | .act .wants, _, _ => false
    | _, _, _ => true
  throwIf (!worded) "UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0"
  throwIf (!(lexTerm A c.holder && c.slot.all (fun p => lexTerm A p.2) && lexCovers A c.content))
    "InvalidInput: an attitude condition names a symbol with no entry in the English lexicon"

def renderable (A : AttDoc) (c : Cond) : Bool := (renderCheck A c).toBool

/-- The lexicon describes the document's environment (SR-3): the same sorts; the author's predicates and no others
    (symbols the lexical view marks generated aside), each with its `A.E` argument sorts; every constant with its
    `A.E` sort. It checks the lexicon's symbols against `A.E`; that each symbol a condition names is in the
    lexicon is D14d's check, `lexCovers` (RC-1). -/
def lexAgrees (A : AttDoc) : Bool :=
  let L := A.lex.env
  let ps := L.predicates.filter (!·.generated)
  L.sorts.all (fun d => d.generated || A.E.sorts.contains d.name) &&
  A.E.sorts.all (fun s => L.sorts.any (·.name == s)) &&
  ps.all (fun d => A.authorPredicates.contains d.name && A.E.predicates d.name == some d.args &&
    d.arity == d.args.length) &&
  A.authorPredicates.all (fun p => ps.any (·.name == p)) &&
  L.constants.all (fun d => d.generated || A.E.constants d.name == some d.sort)

/-- One condition, in its context `Γ`; `part` as `renderCheck`'s. -/
def checkCond (A : AttDoc) (Γ : List String) (c : Cond) (part : Bool := false) : Except String Unit := do
  let hs ← VE.Norms.termSort A.E Γ c.holder
  throwIf (!A.holders.contains hs) s!"InvalidInput: attitude holder of sort {hs} is not of a holder sort"
  let admitted : Bool := match c.mode with
    | .knows => A.T.factive.isSome
    | .thinks w => A.T.words.contains w
    | .act _ => true
  throwIf (!admitted) s!"UnsupportedProfile: '{c.mode.words}' is not admitted by attitudes@0"
  let ctx ← match c.slot with
    | none => pure []
    | some (s, t) => do
      throwIf (!A.E.sorts.contains s) s!"UnknownSymbol: Unknown slot sort {VE.Norms.pyRepr s}"
      let ts ← VE.Norms.termSort A.E Γ t
      throwIf (ts != s) s!"TypeMismatch: attitude slot term has sort {VE.Norms.pyRepr ts}, not {VE.Norms.pyRepr s}"
      pure [s]
  throwIf (!VE.Norms.Formula.qfree c.content) "InvalidInput: an attitude content has a quantifier"
  VE.Norms.typeDiagnostic (baseEnv A) ctx c.content
  throwIf (!c.content.check (baseEnv A) ctx) "InvalidInput: ill-typed attitude content"
  renderCheck A c part

def checkConds (A : AttDoc) : List (List String × Cond) → Except String Unit
  | [] => pure ()
  | (Γ, c) :: rest => do checkCond A Γ c; checkConds A rest

/-- (at-rev, AT-R1) The reading-set parts, in order: each is checked as a condition in the empty context, with
    `part`, so a holder or slot term that is a variable fails `termSort`, and a slot at a constant fails D14b. -/
def checkParts (A : AttDoc) : List Cond → Except String Unit
  | [] => pure ()
  | c :: rest => do checkCond A [] c (part := true); checkParts A rest

def checkNames (A : AttDoc) : List Key → Except String Unit
  | [] => pure ()
  | k :: rest => do
    let n := name A k
    throwIf ((A.E.predicates n).isSome || (A.regulated.map (·.name) ++ A.definitions.map (·.name)).contains n)
      s!"DuplicateDeclaration: generated predicate {n}"
    throwIf (n.utf8ByteSize > 64) s!"ResourceLimit: generated predicate {n} exceeds 64 bytes"
    throwIf (n.any (· == ':')) s!"InvalidInput: generated predicate {n} contains ':'"
    checkNames A rest

def checkAtt (A : AttDoc) : Except String Unit := do
  throwIf (!VE.Route.Admission.token A.decidedBy) "InvalidInput: attitudes decided_by is not a token"
  for s in A.holders do
    throwIf (!A.E.sorts.contains s) s!"UnknownSymbol: Unknown holder sort {VE.Norms.pyRepr s}"
  throwIf (!A.T.reviewed) "InvalidInput: the attitude table is not closure-reviewed"
  for p in A.declared do
    throwIf (!(A.T.words.contains p.1 && A.T.words.contains p.2))
      s!"UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit"
  match VE.Closure.Order.admit scaleCaps A.scale.toOrder with
  | .error e => throw e
  | .ok () => pure ()
  for p in A.authorPredicates do
    throwIf (p.startsWith "attitudes__") s!"InvalidInput: predicate {p} uses the reserved prefix attitudes__"
  match (VE.EnglishGrammar.Lexicon.failures A.lex.env A.lex.overlay A.lex.lexicon).head? with
  | some (code, kind, n) => throw s!"InvalidInput: the English lexicon fails {code} for {kind} {n}"
  | none => pure ()
  throwIf (!lexAgrees A) "InvalidInput: the English lexicon does not describe the document's environment"
  checkConds A (condsOf A)
  checkParts A A.parts
  throwIf (A.authorPredicates.length + (keys A).length > VE.Reports.maxPredicates) "ResourceLimit: MAX_PREDICATES"
  checkNames A (keys A)
  throwIf (!decide ((keys A).map (name A)).Nodup) "InvalidInput: generated predicate names collide"
  match toNorms A with
  | none => throw "InvalidInput: an attitude condition has no key"
  | some D => VE.Norms.validate D

def WellFormedAtt (A : AttDoc) : Bool := (checkAtt A).toBool

def AWellFormed (A : AttDoc) : List String → AFormula → Prop
  | Γ, .base φ => φ.WellFormed A.E Γ
  | Γ, .att c => ∃ k, c.key A Γ = some k ∧ k ∈ keys A ∧
      match c.slot with
      | none => True
      | some (s, t) => t.sortOf A.E Γ = some s
  | Γ, .not a => AWellFormed A Γ a
  | Γ, .and a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .or a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .implies a b => AWellFormed A Γ a ∧ AWellFormed A Γ b
  | Γ, .all s a => s ∈ A.E.sorts ∧ AWellFormed A (s :: Γ) a
  | Γ, .ex s a => s ∈ A.E.sorts ∧ AWellFormed A (s :: Γ) a
```

### 2.7 The frame

D-A4, read from the table. For keys `k`, `k2` on the same subject (holder sort, slot sort, content):

1. **factive**, for each `knows` key: `∀h ∀x. k(h, x) → content(x)`;
2. `knows → believes`, when `T.knowsBelieves` is set;
3. `knows → thinks w`, when some word `w0` with its own premise-3 item is at or above `w` on the document's scale;
4. `thinks w → thinks w2`, when `w ≠ w2` and `w` is at or above `w2` on the document's scale.

Nothing else is a frame pair: no pair starts at says, believes, wants or intends, and none ends at knows (D-A9;
`framePairs_modes`). Within the frozen table, premise 3 through the closure adds nothing the review has not passed
(`Table.reviewed`). A document's own scale pairs extend the order as the author's stipulation; premise 3 then
reaches through them too, and the legend shows each declared pair (section 3.3).

```lean
def entailsMode (A : AttDoc) : Mode → Mode → Bool
  | .knows, .act .believes => A.T.knowsBelieves.isSome
  | .knows, .thinks w => A.T.knowsThinks.any (fun p => A.scale.atLeast p.1 w)
  | .thinks w, .thinks w2 => w != w2 && A.scale.atLeast w w2
  | _, _ => false

def sameSubject (k k2 : Key) : Bool :=
  k.holderSort == k2.holderSort && k.slotSort == k2.slotSort && k.content == k2.content

def framePairs (A : AttDoc) : List (Key × Key) :=
  (keys A).flatMap (fun k =>
    ((keys A).filter (fun k2 => sameSubject k k2 && entailsMode A k.mode k2.mode)).map (k, ·))

/-- `∀h. body` or `∀h ∀x. body`: the slot is variable 0, the holder variable 1 (or 0 when closed). -/
def closeOver (k : Key) (body : VE.Formula) : VE.Formula :=
  match k.slotSort with
  | none => .all k.holderSort body
  | some s => .all k.holderSort (.all s body)

def atomAt (A : AttDoc) (k : Key) : VE.Formula :=
  match k.slotSort with
  | none => .unary (name A k) (.var 0)
  | some _ => .binary (name A k) (.var 1) (.var 0)

def knowsKeys (A : AttDoc) : List Key := (keys A).filter (·.mode == .knows)

def factive (A : AttDoc) (k : Key) : VE.Formula := closeOver k (.implies (atomAt A k) k.content)

def entails (A : AttDoc) (p : Key × Key) : VE.Formula :=
  closeOver p.1 (.implies (atomAt A p.1) (atomAt A p.2))

def framePremises (A : AttDoc) : List VE.Formula :=
  (knowsKeys A).map (factive A) ++ (framePairs A).map (entails A)

/-- One label per premise, distinct (PK-1 requires distinct labels). -/
def frameLabels (A : AttDoc) : List String :=
  (knowsKeys A).map (fun k => "attitude:factive:" ++ name A k) ++
    (framePairs A).map (fun p => "attitude:entails:" ++ name A p.1 ++ ":" ++ name A p.2)
```

### 2.8 Semantics, independent of the elaboration

An **attitude model** is a structure over `E` with one relation per key. `Intended` says what the attitude words
mean, and nothing more: the relations are typed and range over the document's keys, knowing is factive, and each
frame pair holds. `AFormula.denote` reads attitude guards directly in such a model; `interp` reads the elaborated
document's generated names as the keys' relations; `restrict` reads an `envAtt` structure back. The **frame closure**
of a seed (a finite list of key-tuple pairs) adds, at the same tuple, every key the seed's keys reach through frame
pairs (`VE.Closure.Reachable .star`; `Relation.ReflTransGen` is not in the pinned Lean core, edit 2).

```lean
structure AttModel (A : AttDoc) where
  S : VE.Structure.{u}
  J : Key → List S.Carrier → Prop

/-- A key's content at a tuple: closed content at `[h]`, slot content at `[h, x]` with `x` as variable 0. -/
def contentAt (S : VE.Structure.{u}) (k : Key) : List S.Carrier → Prop
  | [_] => k.slotSort = none ∧ k.content.denote S []
  | [_, x] => k.slotSort.isSome ∧ k.content.denote S [x]
  | _ => False

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

def interp (A : AttDoc) (m : AttModel.{u} A) : VE.Structure.{u} :=
  { m.S with relation := fun r vs =>
      match keyOf A r with
      | some k => m.J k vs
      | none => m.S.relation r vs }

def restrict (A : AttDoc) (T : VE.Structure.{u}) : AttModel.{u} A :=
  ⟨{ T with relation := fun r vs => keyOf A r = none ∧ T.relation r vs },
    fun k vs => k ∈ keys A ∧ T.relation (name A k) vs⟩

def seedClosure (A : AttDoc) {C : Type u} (seed : List (Key × List C)) (k2 : Key) (vs : List C) : Prop :=
  ∃ k, (k, vs) ∈ seed ∧ VE.Closure.Reachable .star (fun a b => (a, b) ∈ framePairs A) k k2
```

### 2.9 The route views and the `attitudes` pack

```lean
open VE.Norms (Regulated Sat envAt)
open VE.NormDefaults (UDoc SettledAs UndecidedAt FillTables withFill BaseAdmissibleU fill unsaidName)
open VE.NormDefaults.Wire (BaseAdmissibleX UndecidedAtX)

/-- The norm-defaults view of an attitudes document. -/
def toU (A : AttDoc) (unspec : List String) : Option UDoc := (toNorms A).map (fun D => ⟨D, unspec⟩)

/-- SETTLED over the fillings that also satisfy `X` (the counterpart of `UndecidedAtX`). -/
def SettledAsX (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated) (vs : List B.Carrier)
    (b : Bool) : Prop :=
  ∀ F : FillTables U B, BaseAdmissibleX U X (withFill U B F) →
    ((VE.Norms.outcomeBase (fill U) r.name).denote (withFill U B F) (VE.Norms.tupleVal vs) ↔ b = true)

/-- A premise that reads no `unsaid__` table of `U`. -/
def UnsaidFree (U : UDoc) (φ : VE.Formula) : Prop := ∀ p ∈ U.unspec, unsaidName p ∉ VE.Norms.preds φ

/-- The `attitudes` pack (edit 6), restated against PK-1 as built (refresh, RF-5): a `constraint` pack with no
    generated names; each key's name is declared once, by `envAtt A` (section 2.4). `labelOrigin` gives each frame
    label's full request occurrence; a key's origin (holder term, mode, content, slot, enclosing rule and guard
    location, A6; for a reading-set part's key, at-rev AT-R1, its set, reading and part: PC's `candidateAt` place) is
    `keyOrigin`, carried by `attitudes-elaborate`'s answer (section 4). AT-3a fixes the paths, PC-11 a part's. -/
def attitudesPack (A : AttDoc) : VE.NormDefaults.Packs.Pack :=
  { id := "attitudes", kind := .constraint, decls := [], consts := [],
    labelled := (frameLabels A).zip (framePremises A),
    origins := (frameLabels A).map (fun l => (l, labelOrigin A l)), conditions := [] }

/-- `attitudes@0`'s row in AR-10's table (edit 7), its admission aligned with `attitudes_row_composes` (refresh,
    RF-7), registered by AT-3a with the slot `pack` and the interface `.pack "attitudes"` (profile-composition PC-3;
    synthesis round 2). The refusal gives the reason text only; `gateOf` alone writes the `UnsupportedProfile:`
    prefix. -/
def attitudesRow : VE.Compose.ProfileRow :=
  { profile := "attitudes@0", requires := ["norm-defaults@0", "norms@0"],
    refuses := [("reports@0", "attitudes@0 with reports@0 is not admitted")],
    slot := "pack", interface := .pack "attitudes" }
```

AT-2 adds to `lean/VE/NormDefaults/Packs.lean`, as PK-1's first further provider, the PK-1 stub's text of
`OriginsExact` (obligation 5), `packEntry` and `furtherEntries` (2.7); the refreshed stub carries them (its section
S3a). It also adds `pointCheck` there, not in `lean/VE/Attitudes/Route.lean`: `replayStatusX` calls it from
`lean/VE/NormDefaults/Layered.lean`, which imports `Packs.lean`, and `Attitudes/Route.lean` imports `Layered.lean`, so
a call into that module would be an import cycle (FR-6). The body uses only what `Packs.lean` has: `packPremises` and
`invalidModel`.

```lean
namespace VE.NormDefaults.Packs
/-- AT-2's point check (premise-packs.md 7), for its own pack only: the first `attitudes` premise a replayed
    status point fails, with PK-1's text (`packFault`'s, pack and label). `replayStatusX` runs it on the base
    situation after `situationX`; no other pack's premises are checked at the point. -/
def pointCheck (qs : List VE.NormDefaults.Packs.Pack) (holds : VE.Formula → Bool) : Except String Unit :=
  match (VE.NormDefaults.Packs.packPremises qs "attitudes").find? (fun a => !holds a.2) with
  | some (l, _) => .error (VE.Route.Wire.invalidModel "attitudes" ++ ": " ++ l)
  | none => .ok ()
end VE.NormDefaults.Packs
```

**Against PK-1 as built (refresh, C7).** The pack generates no constants (`consts := []`) and no predicates
(`decls := []`), and states no sufficient condition (`conditions := []`, profile-composition 1.9, which every pack
built today leaves empty). AT-2 adds the row `("attitudes", "attitudes__")` to `reservedPrefixes`, whose rows are (owner,
prefix) pairs (premise-packs.md 2.3); with no pack names, the row's use is the author-name refusal (`reserved`), as
for `soft__` and `rights__`. `decodeSoftU` and `decodeRightsU` assemble with `assemble U used ps` (the vocabulary count `checkAuthorN`
charged) and do not change; the attitudes route's decoder assembles this pack above them, into the list they return
(`decodeLayeredAtt`, section 6.3; DRI at-0 item 1). The route reads the pack back with `packPremises L.packs "attitudes"`,
which answers labelled premises. Since
the pack has no names and its labels are distinct (`frameLabels_nodup`), `assemble` refuses it for nothing of its
own (`assemble_attitudes`). The pack's position inside X is PK-1's fixed `packOrder`: after weighing, before scales,
whichever provider lands first.

**AT-2's contracts with PK-1 (refresh, RF-6).** premise-packs.md 2.7, 3, 5 and 7 leave these to the first provider;
with the declaration in `U` (section 2.4) they are:

- **Environment.** The pack declares nothing, so `envX U qs = envAt (fill U) 0` for every list of soft, rights and
  attitudes packs (`envX_declFree`), and `envAt (fill U) 0` already declares each key's name with its sorts
  (`names_in_base`). PK-1's typing environment (obligation 2), `extendEnv (envAt (fill U) 0) [] []`, is that same
  environment, where `frame_typed_fill` types the frame. Situations, certificates (`bindCertX`,
  `lean/VE/NormDefaults/LayeredAdmission.lean:83`) and `BaseAdmissibleX` stay over `envAt (fill U) 0`: nothing is
  threaded, and drafts 1–4's "thread `envX`" item is void.
- **Expansion.** A `constraint` pack keeps its own local checks and makes no conservativity claim on the route
  (premise-packs.md 3 (1)); its local checks are `checkAtt`, `frame_typed_fill`, `frame_unsaidFree` and the point
  check. `ExpandsOn` and `expandBy` are a `vocabulary` pack's obligation, so they land with the first provider
  whose pack declares names, not in AT-2. Conservativity over the old language stays AT-1's theorem over the
  document (`empty_relations_frame`, `att_old_language_conservative`), whose expansion is by empty attitude
  relations.
- **Origins.** `OriginsExact (attitudesPack A)`: every frame label has exactly one origin and nothing else has one
  (`attitudesPack_originsExact`). The pack's entry (`packEntry`, through `furtherEntries` and the `attitudes` key
  AT-2 adds to `layered_elaborate`, its generated schema and its relay) has the premises with their origins and an
  empty `names` array; the keys and their origins are `attitudes-elaborate`'s.
- **The point check.** `VE.NormDefaults.Packs.pointCheck` on the attitudes pack's premises only; a pack list without it passes
  (`pointCheck_absent`), so every legacy status answer is today's; a passed check gives the frame at the point
  (`pointCheck_sound`), the first conjunct of `attitudes_status_sound`. Its text is PK-1's placement: at RM2
  `InvalidModel(attitudes): the model violates a background premise: attitude:factive:attitudes__knows__1`
  (computed, section 7.3).

**Refusal texts (synthesis round 2).** Where an attitudes refusal is the AR-10 gate's, the row gives the reason
text only and `gateOf` writes the `UnsupportedProfile:` prefix: the `reports@0` refusal above, and the requires
refusal `UnsupportedProfile: attitudes@0 requires norm-defaults@0` (gateOf's text). The other `UnsupportedProfile:`
texts of this spec (`decodeAttDoc`'s off-profile text, 5.1; `checkAtt`'s D4, D9, D0 and D14c, 5.2) are decoder
refusals, not the gate's, and keep their prefix.

**The row and its theorem (refresh, RF-7).** AR-10's gate is conjunctive (`rowChecks`, `gateOf`,
`lean/VE/Compose/Dispatch.lean:889–899`): drafts 1–4's row (`requires := ["norms@0"]`) admits
`["attitudes@0", "norms@0", "relational-fol@0"]` (route `norms`), on which `attitudes_row_composes` (section 6.3) is
false. A row cannot require a disjunction, but both supported chains carry `norm-defaults@0`: the layered route,
and the readings route, which reads the completion only with `norm-defaults@0` beside `readings@1` on the norms
chain (`lean/VE/Readings/UnspecifiedWire.lean:39–42`). So the row requires `norm-defaults@0` and `norms@0` and
refuses `reports@0`; the theorem's statement is unchanged and holds of it. Computed on the table AT-3a builds (AR-10's
base rows, the row, then the wrappers; section 7.3): over all 512 lists of nine profiles (`attitudes@0`,
`closure@0`, `norm-defaults@0`, `norms@0`, `readings@1`, `relational-fol@0`, `reports@0`, `rights@0`,
`soft-norms@0`), drafts 1–4's row admits six lists that falsify the theorem and the restated row none; the restated
row refuses `["attitudes@0", "norms@0", "relational-fol@0"]` with `UnsupportedProfile: attitudes@0 requires
norm-defaults@0`, and every list without `attitudes@0` gets today's answer. Draft 6 reruns this on main's table and
over 4,096 lists of twelve profiles (section 7.3): no counterexample, and 23 lists with `attitudes@0` admitted. The
row's own `reports@0` text is unreachable: `reports@0`'s row comes first and refuses `norms@0`, so a list holding both
answers `UnsupportedProfile: reports@0 with norms@0 layers` (computed). The row keeps its refusal, as the plan writes
it. The batch that adds the row proves the
theorem for the real `profileTable` (AR-10's rule). Admission does not put the pack on every admitted route. A
list without `soft-norms@0` or `rights@0` has no layered route: `layeredRoute` answers `none`, and `decodeLayered`
refuses it (`lean/VE/NormDefaults/Layered.lean:154`), so it reaches no `LayeredU`, no `dispatch` and no frame. On a
layered list, a kind that needs the pack where it is absent is refused by PK-1's `dispatch` (premise-packs.md 2.10).
So the row admits 11 of the 23 lists on routes where the frame does not apply: `normDefaults` 4, `discourse` 6
(PC-7a's batch) and `alternatives` 1 (outside the chain). `attitudes_row_composes` holds on them, since it speaks of
the list; what those routes answer is OPEN-2 (section 19).

## 3. English, one reading each

AT-5 builds this in the Lean English grammar; until then the structured form (section 4) is what a writer writes.
`H` is the holder's rendering (a rule variable as "that instance of Claude", a constant by its name); `P` is the
content rendered as a clause, with the slot term in place of variable 0 ("that situation is classified as
"mass_casualty_weapon_uplift""); `w` is an admitted word.

### 3.1 Wordings that are admitted

| Mode | Wording (rendered and read) | Reading |
|---|---|---|
| `knows` | "H knows that P" | knows |
| `thinks w` | "H thinks it w that P" | thinks it w or more likely (lower bound, D-A5) |
| `act .believes` | "H believes that P" | `reports@0`'s believes |
| `act .says` | "H says that P" | `reports@0`'s says |
| `act .intends` | "H intends that P" | `reports@0`'s intends, of a content; never intentional action |
| `act .wants` | "H wants Y to VP", only when the content is one unary base predicate on the slot term `Y` whose template is a verb phrase (as `reports@0` words it); as a reading-set part only (at-rev, AT-R1), also the closed content one unary base predicate on a constant `Y`, spelled from the lexicon (u0035.s12's shape, "Anthropic wants Claude's helpfulness to flow from …"); any other `wants` content has no reviewed wording | `reports@0`'s wants |
| negation of a whole condition | "it is not the case that …" (VE's external negation) | negation, nothing asserted |
| "P, and X does not know that P" | written "both P and H does not know that P", read whole (below) | `P ∧ ¬knows(P)`, one tree: `assertedNotKnows c = and P̂ (not K)` (section 6.5); admitted only if its six E2 items reach 36 of 40: three "Must P?", three "Does X know that P?" (A4, G5) |

**The last row is read whole (RR-1).** The grammar reads "both P and H does not know that P" as one construction,
only when its first conjunct is the clause P of the complement: the same content with the same slot term (so the
same `P̂`, section 3.4), the holder written once. Its one derivation is the tree `assertedNotKnows c`, `and P̂ (not
K)` with `K := att c` for the `knows` condition `c` (section 6.5); `assertedNotKnows_one_reading` states it. The
second conjunct is not read as an occurrence of section 3.4's refused "H does not know that P": composing that row's
two candidates under "both P and …" would give `and P̂ (and P̂ (not K))` and `and P̂ (not K)`, equivalent formulas
but two trees, so two derivations under the all-derivations gate. Every other occurrence of "H does not know that P"
is refused as `NegatedFactive` (section 3.4's first row): a first conjunct with another content or another slot term,
the conjuncts in the other order, the row's shape under "either … or", and the bare form; "unless H knows that P"
stays refused by that table's second row. Section 7.6's AT-5 fixtures check each (RR-2). The row may stand anywhere a
guard formula may, for example as a disjunct.

"Intends to VP" and "wants Y to VP" with an act phrase are not admitted; intentional action stays residual until a
reviewed act-performance bridge (ET-D2) fits this profile's contract, and act-phrases landing does not admit them
(edit 3). A joined act phrase under `intends` or `believes` is never split or distributed (edit 4).

The structured form admits exactly the conditions this table words (SR-2, section 2.6), so no admitted document holds
a condition without a sentence, and no sentence stands for two admitted conditions: a slot is mentioned by its
content (D14a), a slot term is a variable of the guard (D14b; about a constant, write the closed content, "H knows
that s1 is classified as …"), and `wants` takes only its row's wording (D14c; its closed form only as a reading-set
part, where the slot form cannot occur, so the two never share a context). `H`, `P`, `Y` and the verb phrase are
rendered from the document's own lexicon (`A.lex`), the one `checkAtt` validated (SR-3), which has an entry for every
predicate and constant an admitted condition names (D14d, RC-1).

### 3.2 Boundaries: framed connectives and the complement-boundary rule

In a guard written in English, every binary connective is framed, as VE's `relational-fol@0` grammar writes them:
"both A and B", "either A or B, or both", "if A, then B". **Complement-boundary rule** (A4): a content clause after
"knows that", "believes that", "says that", "intends that" or "thinks it w that" ends at the first frame word ("and"
of "both", "or" of "either", ", or both", ", then") whose frame opened outside the clause, or at the end of the
sentence; a content that is itself compound opens its own frame right after "that" ("H knows that both P1 and P2").
So every "and" and "or" closes the innermost open frame, and a sentence has one parse. An adverb written inside a
declared predicate's template (the hand-named "{0} intentionally does the weapons uplift in {1}") is part of that
one predicate, matched whole, and is not the refused attitude adverb of section 3.4; its factor ("what counts as
intentionally doing …") is decided by its decider (section 11, item 15).

### 3.3 The pilot sentence and its legend

u0165.s01 with u0173.s01's condition, as Lean renders it (F4: the intention conjunct is the hand-named open term):

> Every instance of Claude must not do the weapons uplift in each situation if either both that instance of Claude
> knows that that situation is classified as "mass_casualty_weapon_uplift" and that instance of Claude intentionally
> does the weapons uplift in that situation, or that instance of Claude thinks it quite likely that that situation
> is classified as "mass_casualty_weapon_uplift", or both.

The legend, rendered by Lean, one line per frame premise and per open-term record:

> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that
> situation is classified as "mass_casualty_weapon_uplift".
> If an instance of Claude knows that a situation is classified as "mass_casualty_weapon_uplift", then that instance
> of Claude thinks it quite likely that that situation is classified as "mass_casualty_weapon_uplift".
> "Quite likely" means quite likely or more likely. How likely counts as quite likely is not decided by VE (decided
> by: unstated).
> What counts as intentionally doing the weapons uplift in a situation is not decided by VE (decided by: unstated).

A document's own scale pair adds the line "This document says that "very likely" is at least as likely as "quite
likely"." Templates: factive "If H₀ knows that P₀, then P₀."; premise 2 "If H₀ knows that P₀, then H₀ believes that
P₀."; premises 3 and 4 "If H₀ knows that P₀ / thinks it w₁ that P₀, then H₀ thinks it w₂ that P₀.", with `H₀` the
indefinite holder ("an instance of Claude") and `P₀` the content with the indefinite slot ("a situation"), then
"that …" on repetition, as VE renders bound variables today.

### 3.4 Refused forms (rows in english-lean's catalogue, edit 9)

**Where the rows live (refresh).** english-lean's catalogue for these rows is `lean/VE/EnglishGrammar/SourceWords.lean`,
which en-sw builds and whose row type it fixes (DRI 2026-10-28, PLANS-INDEX C1); AT-5 adds rows there and waits for
en-sw. `NegatedFactive`'s candidate readings are generated by presupposition's projection, its one owner (DRI PS-NF):
the two rows below state the readings the projection must give, and AT-5's rows consume them rather than compute
them.

Refusals with mechanical rewrites (`refused_have_rewrites` applies, SR-4, SR-5). Each row records its category and
its candidate readings, written here independently of its rewrites: the form is refused; each rewrite has exactly
one reading; the rewrites' readings are exactly the candidates, in the row's order; the candidates are pairwise
distinct. A guard row is read in its enclosing rule's context `Γ = ruleContext A r`, so "that instance of Claude"
resolves to the rule's variable; a rule row is read as a whole rule, whose context is its own. In the candidates,
`σ` is the slot, `K := att ⟨H, knows, σ, P⟩`, `T w := att ⟨H, thinks w, σ, P⟩`, `B := att ⟨H, act believes, σ, P⟩`,
`P̂ := base (assertedOf c)`, the content with the slot term for variable 0 (`P` itself when closed; section 6.5: a
content is quantifier-free, D12, so variable 0 is replaced directly, not by `Formula.subst` of
`lean/VE/Core/Substitution.lean`, which is over `VE.Core.Formula`), and `r` is the enclosing rule with guard `g` and
carve-outs `cs` (the refused carve-out removed).

| Refused form | Why | Code | Category | Candidate readings | Rewrites |
|---|---|---|---|---|---|
| "H does not know that P" (anywhere but section 3.1's admitted row, read whole: the second conjunct of "both P and …" with the same `P̂`) | with and without `P` | `NegatedFactive` | guard (`AFormula`) | `and P̂ (not K)`; `not K` | "both P and it is not the case that H knows that P"; "it is not the case that H knows that P" |
| "unless H knows that P" (a carve-out) | its presupposition is unresolved (debate round 3) | `NegatedFactive` | rule (`ARule`): the readings move the condition from a carve-out into the guard, which a guard formula cannot represent | `{ r with guard := and g (not K), carveOuts := cs }`; `{ r with guard := and g (and P̂ (not K)), carveOuts := cs }` | "if it is not the case that H knows that P" (in the guard); "if both P and it is not the case that H knows that P" |
| "H does not think it w that P" | neg-raising: two readings | `NegRaising` | guard (`AFormula`) | `not (T w)`; `att ⟨H, thinks w, σ, not P⟩` | "it is not the case that H thinks it w that P"; "H thinks it w that it is not the case that P" |
| "H thinks that P" | belief or opinion (as `reports@0`) | `BareThinks` | guard (`AFormula`) | `B`; then `T w` for each admitted `w`, in `table`'s order | "H believes that P"; "H thinks it w that P" for each admitted `w` |

Refusals with advice only (the rewrite needs what the sentence lacks; the catalogue row's advice text names it):

| Refused form | Why | Code | Advice |
|---|---|---|---|
| "H knowingly / intentionally / deliberately VPs" | scope of the adverb | `AttitudeAdverb` | "Write the attitude as its own condition about the case it concerns: 'both H knows that <case> and …'. Intentional action has no reviewed wording; name it as an open term." |
| "it thinks …", "they know …" with a pronoun that is not a rule variable | unresolved holder (no pronoun crosses a quote boundary) | `UnresolvedHolder` | "Name the holder: 'that instance of Claude', or a declared constant." |

E2's three "unless" items are evidence for a later admission only, with its own statement review. If E1 admits no
word, `BareThinks` has one rewrite, and the review revisits that row (section 12).

## 4. Wire (structured content; JSON never carries `null`)

```text
environment.attitudes = { "holders": [sort, …], "scale": [[word, word], …], "decided_by": token }
guard node             = { "attitude": { "holder": term, "mode": "knows" | "thinks" | "believes" | "wants"
                           | "intends" | "says", "degree": word (only with "thinks"),
                           "slot": { "sort": sort, "term": term } (optional), "content": formula } }
```

- Terms and formulas are W1's indexed JSON (`VE.Norms.Wire.budgetFormula`), sharing its node budget.
- The block decodes to `holders`, `declared` (the `scale` pairs) and `decidedBy`; `T` is always `table`.
- The English lexical data (SR-3) comes with the case as the English grammar's requests carry it: `lexicon` (the
  export `ve.english-lexicon@1`, naming the environment) and, optionally, `overlay`. `decodeAttDoc` decodes them
  with the grammar's own decoders (`VE.EnglishGrammar.Env.decode`, `Overlay.decode`, `Run.decodeLexicon`, as
  `Run.decodeCase` does) into `lex`, at AT-3a, because `attitudes-elaborate` already answers a wording template per
  key. A case without `lexicon` fails with the decoder's own text.
- `decodeAttDoc` ends with `checkAtt` (SR-7): it returns a document only when every check of section 5.2 passes,
  and otherwise answers the first failing check's diagnostic, which is then the kind's answer
  (`decodeAttDoc_wellFormed`, section 6.3).
- Attitude nodes are admitted in guards and carve-outs only (not in soft exception conditions, not in definitions),
  and, from PC-11 on, as the closed node of a reading-set part in PC-11's `attitude` case (at-rev, AT-R1): PC-11's
  decoder reads the part with this section's node decoder and hands the node to the attitudes document as one of
  `AttDoc.parts`, in document order, before `checkAtt` (a request row in the PLAN's section 3.11). Inside a composed
  document a holder report is such a part, never a `{"report": …}` unit; `reports@0` stays refused beside the chain
  (at-rev, AT-R2; PLAN AT-8).
- The layered route's kinds (edit 7; refresh): one new kind, `attitudes-elaborate`, a row of the kind table
  `layeredRows` (`lean/VE/Defaults/Route.lean`) needing the `attitudes` pack; it answers the generated predicates
  (name, sorts, key, wording template, open-term record), the frame (label, formula), each key's and label's request
  origin, and the elaborated guards. Status, conflict and report are today's `norm-defaults-status`, `-conflict` and
  `-report`, which already read the whole assembled X (premise-packs.md 2.7, 7); drafts 1–4's `attitudes-status`,
  `attitudes-conflict` and `attitudes-report` duplicated them and are removed, so one owner answers each kind.
  AT-3a widens `runOtherCase`'s test (`lean/VE/NormDefaults/Run.lean:219–220`, which passes only `norm-defaults-*` and
  `defaultsKinds`), so that `attitudes-elaborate` reaches `runLayered` (FR-1).
- The attitudes route's decoder (DRI at-0 item 1): AT-3a's `runLayered` decodes with `decodeLayeredAtt` (section 6.3),
  which answers `decodeLayered`'s result as it is unless the profile list has `attitudes@0`; then it assembles the pack
  of `decodeAttDoc`'s document into that result.

## 5. Diagnostics, in order

### 5.1 Decoding (AT-3a; texts fixed here, computed when AT-3a exists)

**With `attitudes@0` off, nothing changes (SR-6).** W1's, soft's and P0's entry points, and every route that calls
them, keep today's answers and today's fault order for every input, malformed attitude objects included: a JSON
object with the key `attitude` where a formula is expected answers `array expected` (computed on `main` at
`49de179e`), as today. The new code is not reached on those routes, so no frozen W1, soft or P0 diagnostic changes
(PLAN D-A1). The text `UnsupportedProfile: an attitude condition needs attitudes@0` is `decodeAttDoc`'s alone, for a
case whose profile list lacks `attitudes@0`. Through the `attitudes-elaborate` kind it is not reachable: `runLayered`
calls `decodeLayeredAtt`, which without `attitudes@0` is `decodeLayered` alone and never calls `decodeAttDoc`, so, on a
layered list, a case with an attitude node and without `attitudes@0` answers `array expected`, and one with no node
answers `dispatch`'s `UnsupportedProfile: case kind attitudes-elaborate needs the attitudes premise pack` (FR-3).
Elsewhere under `norm-defaults@0`, the kind answers `UnsupportedProfile: case kind attitudes-elaborate is not available
on the norm-defaults route`.

With `attitudes@0` on, in this order, as the decoder meets them: fields other than those of section 4: the
decoder's `exactFields` text; an unknown mode: `InvalidInput: unknown attitude mode <m>`; `degree` with a mode other
than `thinks`: `InvalidInput: degree is allowed only with thinks`; `thinks` without `degree`: `InvalidInput: thinks
needs a degree`; then the block: a case with no block, the decoder's own text; `decided_by` and `holders` as section 5.2, a `scale` entry that is not a pair of
strings: `InvalidInput: a scale entry is a pair of words`; then the lexical data (`lexicon`, `overlay`): the English
grammar decoders' own texts; then `checkAtt`, in section 5.2's order (SR-7). This is `decodeAttDoc`'s order; on the
route, a fault `decodeLayered` meets answers first, since `decodeLayeredAtt` runs it first.

### 5.2 `checkAtt`, in order (each fixture fails exactly its own check)

Draft 1's rows were computed in the stub. Rows D6a, D6b and D14a–D14c are new in draft 2 (SR-2, SR-3), and D14d in
draft 3 (RC-1): their texts are fixed here, and the values marked *expected* were computed as stated in AT0C (stub
`0c73f880`, then `dea412eb`, on the frozen table; [attitudes-at0-changed.md](../research/attitudes-at0-changed.md)).
Every fixture document now carries the fixture lexicon (section 7), extended with the symbols
a row adds where its check comes after D6b (D15, RC-3), so that an earlier row's answer is unchanged by it. The
fixtures run on the frozen `table` (AT0C), so D4 and D0 use words it refuses, and D5 answers QS-1's own text, now
that `Order.admit` is main's (refresh, Astra r1 1).

| # | Check | Fixture (F-AT1 with one change) | Diagnostic |
|---|---|---|---|
| D1 | `decided_by` is a token | `decidedBy := ""` | `InvalidInput: attitudes decided_by is not a token` |
| D2 | holder sorts declared | `holders := ["robot"]` | `UnknownSymbol: Unknown holder sort 'robot'` |
| D3 | table closure-reviewed | `T := badTableKnows` | `InvalidInput: the attitude table is not closure-reviewed` |
| D4 | declared pairs between admitted words | `declared := [("as likely as not", "quite likely")]` (AT0C; draft 1: `("likely", "quite likely")`, a word the frozen table admits) | `UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit` |
| D5 | scale caps (QS-1's `Order.admit`) | 64 declared pairs (74 edges with the frozen table's 10) | `ResourceLimit: At most 64 order pairs` (QS-1's text on main; drafts 1–4's stand-in answered `ResourceLimit: order edges`) |
| D6 | no author predicate uses `attitudes__` | author predicate `attitudes__x` | `InvalidInput: predicate attitudes__x uses the reserved prefix attitudes__` |
| D6a | the English lexicon is valid (`Lexicon.failures` empty; its first failure is named) | the lexicon selects no wording for `mass_casualty_weapon_uplift` | *expected* `InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift` |
| D6b | the lexicon describes `A.E` (`lexAgrees`) | the lexical view declares `mass_casualty_weapon_uplift` on (`claude_instance`) | *expected* `InvalidInput: the English lexicon does not describe the document's environment` |
| D7 | holder term typed | holder `var 5` | `UnboundVariable: Variable index 5 is outside its scope` |
| D8 | holder of a holder sort | holder `var 0` (a situation) | `InvalidInput: attitude holder of sort situation is not of a holder sort` |
| D9 | mode admitted | `thinks "unlikely"` | `UnsupportedProfile: 'thinks it unlikely' is not admitted by attitudes@0` |
| D0 | mode admitted, frozen table | F-AT1's rule with the condition `thinks "as likely as not"`, `T := table` (AT0C; draft 1: F-AT1 under the empty table, refusing `knows`, which the frozen table admits) | `UnsupportedProfile: 'thinks it as likely as not' is not admitted by attitudes@0` |
| D10 | slot sort declared | slot sort `place` | `UnknownSymbol: Unknown slot sort 'place'` |
| D11 | slot term of the slot's sort | slot `(situation, var 1)` | `TypeMismatch: attitude slot term has sort 'claude_instance', not 'situation'` |
| D12 | content quantifier-free | content `∃ situation. C(var 0)` | `InvalidInput: an attitude content has a quantifier` |
| D13 | content over the base vocabulary | content `weapons_uplift_permitted(var 0, var 0)` | `UnknownSymbol: Unknown predicate 'weapons_uplift_permitted'` |
| D14 | content typed in its context | closed content `C(var 0)` | `UnboundVariable: Variable index 0 is outside its scope` |
| D14a | a slot's content mentions the slot (`renderable`) | the `knows` content `⊤`, slot kept | *expected* `InvalidInput: an attitude content does not mention its slot` |
| D14b | a slot term is a variable of the guard (`renderable`) | the `knows` slot `(situation, s1)`, `s1` a constant of sort `situation` | *expected* `InvalidInput: an attitude slot term is not a variable of the guard` |
| D14c | a `wants` content has section 3.1's wording (`renderable`; a reading-set part also its closed row, at-rev AT-R1) | the `intends` condition made `wants`, content `and C(var 0) csam_generation(var 0)`; also C-e's second and third documents (computed) | *expected* `UnsupportedProfile: this 'wants' content has no reviewed wording in attitudes@0` |
| D14d | every predicate and constant of the condition has its lexicon entry (`renderable`, RC-1) | the `knows` content the closed `C(s1)`, `s1` declared in `E` but in neither the lexical view nor the lexicon (C-d's first document) | *expected* `InvalidInput: an attitude condition names a symbol with no entry in the English lexicon` |
| D15 | predicates within `MAX_PREDICATES` | 240 more author predicates, each declared in `E` on `situation` and in the fixture lexicon with its quoted fallback wording `{0} is classified as "<name>"`, so that D6a and D6b still pass (RC-3) | `ResourceLimit: MAX_PREDICATES` (as `reports@0`; *expected* with the extended lexicon) |
| D16 | generated names undeclared | `E` declares `attitudes__knows__1` | `DuplicateDeclaration: generated predicate attitudes__knows__1` |
| D17 | generated names at most 64 bytes | a table word of 58 bytes | `ResourceLimit: generated predicate attitudes__thinks_extraordinarily_overwhelmingly_and_almost_certainly_likely__1 exceeds 64 bytes` |
| D18 | W1's check of the elaborated document | a base conjunct `C(var 1)` | `TypeMismatch: Predicate 'mass_casualty_weapon_uplift' expects ('situation',), received ('claude_instance',)` |

The table is in `checkAtt`'s order: D1–D6, D6a, D6b, D7–D9 (D0 is D9's check on the frozen table), D10–D14,
D14a–D14d, D15–D18. Draft 1's numbers are kept, so its fixtures keep their names. The check `generated predicate {n}
contains ':'` is inside D17's step, and `generated predicate names collide` follows D17. Neither can fire with E1's
words (no slug has a colon, and no two slugs coincide). They stay as guards on other tables, since `frameLabels_nodup`
and `assemble_attitudes` quantify over every `A` and a colon in a word could make two frame labels equal (FR-2).

### 5.3 On the route

A point whose model breaks a frame premise is refused, never evidence, with PK-1's diagnostic naming the first
failing premise's pack and label in X order. Drafts 1–4 put the label inside the parentheses (computed then, RM2:
`InvalidModel(attitude:factive:attitudes__knows__1): the model violates a background premise`). PK-1 as built puts
the pack there and the label after it (`packFault`, premise-packs.md 2.8, which asks this spec to align; refresh,
Astra r1 2): at RM2 *expected* `InvalidModel(attitudes): the model violates a background premise:
attitude:factive:attitudes__knows__1`, and at RM3 the label is
`attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1`. Every accepted witness satisfies the whole
assembled X, the frame included (`filledX_whole`); the one exception is defeasible's collision witness, checked
against X without the soft pack's coherence premises (`xWithout`, premise-packs.md 2.9, DF7), which still contains
the frame. Every UNKNOWN stays UNKNOWN.

## 6. Statements

Each is checked in the stub as `def <name> (binders) : Prop := <conclusion>`. Namespaces and opens as in section 2.

### 6.1 AT-1 (`lean/VE/Attitudes/Theorems.lean`)

```lean
theorem names_fresh (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, A.E.predicates (name A k) = none ∧ (name A k).utf8ByteSize ≤ 64 ∧
      name A k ∉ A.regulated.map (·.name) ++ A.definitions.map (·.name)
theorem names_injective (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ k ∈ keys A, ∀ k2 ∈ keys A, name A k = name A k2 → k = k2
theorem keyOf_name (A : AttDoc) (h : WellFormedAtt A = true) : ∀ k ∈ keys A, keyOf A (name A k) = some k
theorem envAtt_extends (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (φ : VE.Formula)
    (hφ : φ.WellFormed A.E Γ) : φ.WellFormed (envAtt A) Γ
theorem toNorms_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∃ D, toNorms A = some D ∧ VE.Norms.WellFormed D = true
/-- Typed over the base vocabulary extended by the generated names (A2). -/
theorem frame_wellFormed (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (baseEnvAtt A) []
theorem frame_universalQF (A : AttDoc) (h : WellFormedAtt A = true) :
    ∀ φ ∈ framePremises A, VE.NormDefaults.UniversalQF φ
theorem frameLabels_nodup (A : AttDoc) (h : WellFormedAtt A = true) :
    (frameLabels A).length = (framePremises A).length ∧ (frameLabels A).Nodup
/-- D-A9: no frame pair starts at says, believes, wants or intends, and none ends at knows. -/
theorem framePairs_modes (A : AttDoc) :
    ∀ p ∈ framePairs A, (p.1.mode = .knows ∨ ∃ w, p.1.mode = .thinks w) ∧ p.2.mode ≠ .knows
theorem framePairs_transitive (A : AttDoc) (k1 k2 k3 : Key) (h12 : (k1, k2) ∈ framePairs A)
    (h23 : (k2, k3) ∈ framePairs A) (hne : k1 ≠ k3) : (k1, k3) ∈ framePairs A

/-- Faithfulness, guards: the elaborated guard means what the attitude guard means. -/
theorem att_elaboration_faithful (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (Γ : List String) (ρ : VE.Valuation m.S) (a : AFormula) (ha : AWellFormed A Γ a) (φ : VE.Formula)
    (he : a.toFormula A Γ = some φ) : φ.denote (interp A m) ρ ↔ a.denote A m Γ ρ
/-- Faithfulness, the frame: the frame premises hold exactly when the relations mean what `Intended` says. -/
theorem frame_iff_intended (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hJ : ∀ k vs, m.J k vs → k ∈ keys A ∧ VE.TupleTyped m.S k.sorts vs) :
    VE.Norms.Sat (interp A m) (framePremises A) ↔ Intended A m
/-- Model correspondence, both ways. -/
theorem interp_admissible (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (hS : m.S.Admissible A.E) (hI : Intended A m) : (interp A m).Admissible (envAtt A)
theorem restrict_admissible (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) : (restrict A T).S.Admissible A.E
theorem restrict_intended (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (hX : VE.Norms.Sat T (framePremises A)) : Intended A (restrict A T)
theorem interp_restrict (A : AttDoc) (h : WellFormedAtt A = true) (T : VE.Structure.{u})
    (hT : T.Admissible (envAtt A)) (r : String) (vs : List T.Carrier) :
    (interp A (restrict A T)).relation r vs ↔ T.relation r vs
theorem old_formula_invariant (A : AttDoc) (h : WellFormedAtt A = true) (m : AttModel.{u} A)
    (Γ : List String) (ρ : VE.Valuation m.S) (φ : VE.Formula) (hφ : φ.WellFormed A.E Γ) :
    φ.denote (interp A m) ρ ↔ φ.denote m.S ρ

/-- The expansion step of conservativity: empty attitude relations satisfy every frame premise, over any
    structure. (Drafts 1–4 also called it the pack's PK-1 `vocabulary` expansion step; the pack is a `constraint`
    pack, section 2.9.) -/
theorem empty_relations_frame (A : AttDoc) (S : VE.Structure.{u}) :
    VE.Norms.Sat (interp A ⟨S, fun _ _ => False⟩) (framePremises A)
/-- Conservativity (VISION rule 4). No hypothesis that the frame is empty. -/
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
/-- The frame closure of a typed seed whose knowing members have true contents is intended. -/
theorem seed_intended (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) : Intended A ⟨S, seedClosure A seed⟩
/-- Every intended model holding the seed holds its frame closure. -/
theorem seed_least (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (seed : List (Key × List m.S.Carrier))
    (hs : ∀ p ∈ seed, m.J p.1 p.2) : ∀ k vs, seedClosure A seed k vs → m.J k vs
/-- Nothing beyond the frame (F3, edit 2): a seed forces an attitude exactly when frame pairs reach it from a seed
    member at the same tuple. No closure under consequence or conjunction, nothing across holders, contents or
    tuples. -/
theorem forced_iff_reachable (A : AttDoc) (S : VE.Structure.{u}) (seed : List (Key × List S.Carrier))
    (hseed : ∀ p ∈ seed, p.1 ∈ keys A ∧ VE.TupleTyped S p.1.sorts p.2)
    (hfact : ∀ p ∈ seed, p.1.mode = .knows → contentAt S p.1 p.2) (k : Key) (vs : List S.Carrier) :
    (∀ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ → (∀ p ∈ seed, J p.1 p.2) → J k vs) ↔
      seedClosure A seed k vs
/-- The audit's requirement (R 2.2): any attitude other than knowing may be held of a false content; an instance
    of `seed_intended` with the seed `[(k, vs)]`. No hypothesis about the content appears. -/
theorem mistaken_belief_admissible (A : AttDoc) (S : VE.Structure.{u}) (k : Key) (hk : k ∈ keys A)
    (hm : k.mode ≠ .knows) (vs : List S.Carrier) (hvs : VE.TupleTyped S k.sorts vs) :
    ∃ J : Key → List S.Carrier → Prop, Intended A ⟨S, J⟩ ∧ J k vs
/-- R 5's collapse (repaired, A3): when a frame pair links the two keys, `(ck ∧ a) ∨ ct` is `ct`. -/
theorem guard_collapse (A : AttDoc) (m : AttModel.{u} A) (hI : Intended A m) (Γ : List String)
    (ρ : VE.Valuation m.S) (ck ct : Cond) (a : AFormula) (k kt : Key) (hk : ck.key A Γ = some k)
    (hkt : ct.key A Γ = some kt) (hp : (k, kt) ∈ framePairs A) (hh : ck.holder = ct.holder)
    (hsl : ck.slot.map (·.2) = ct.slot.map (·.2)) :
    AFormula.denote A m Γ ρ (.or (.and (.att ck) a) (.att ct)) ↔ AFormula.denote A m Γ ρ (.att ct)
/-- The frozen table passes its closure review. -/
theorem table_reviewed : table.reviewed = true
```

Proof notes. `names_*` and `keyOf_name` from `checkNames` and the `Nodup` check. Conservativity: extend by the empty
relations (`empty_relations_frame`, `old_formula_invariant`); the other direction restricts (`restrict_admissible`,
`interp_restrict`). `frame_iff_intended`: closed contents are typed in `[]` and slot contents in `[s]`, so the
premise's extra binders do not change them, and contents use no generated name (`names_fresh`). `seed_intended`: no
frame pair ends at `knows` (`framePairs_modes`), so factivity is needed of the seed only; reachability is closed
under one more pair; frame pairs relate keys with the same sorts. `seed_least`: induction on `VE.Closure.Path`.
`forced_iff_reachable` is the two together. `guard_collapse` is the third conjunct of `Intended` at `hp`.
`framePairs_transitive` uses QS-1's `atLeast_trans`. `table_reviewed` by `decide`.

### 6.2 AT-2 (`lean/VE/Attitudes/Route.lean`)

```lean
/-- The `attitudes` pack's premises are `framePremises A` (replaces PLAN draft 1's `FrameSource` and
    `frameSource_X`). -/
theorem attitudesPack_premises (A : AttDoc) (h : WellFormedAtt A = true) :
    (attitudesPack A).labelled.map (·.2) = framePremises A ∧ (attitudesPack A).labelled.map (·.1) = frameLabels A
/-- The declaration policy (refresh, RF-5): the pack declares nothing; `U`'s base vocabulary declares every key's
    name with its sorts, so every checker over `envAt (fill U) 0` already reads them. -/
theorem attitudesPack_declares_nothing (A : AttDoc) :
    (attitudesPack A).kind = .constraint ∧ (attitudesPack A).names = []
theorem names_in_base (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : VE.NormDefaults.WellFormedU U = true) :
    ∀ k ∈ keys A, (envAt (fill U) 0).predicates (name A k) = some k.sorts
/-- The environment contract: with packs that declare nothing (soft, rights, attitudes), `envX` is today's base
    environment, which is also PK-1's obligation-2 environment `extendEnv (envAt (fill U) 0) [] []`. -/
theorem envX_declFree (U : UDoc) (qs : List VE.NormDefaults.Packs.Pack)
    (h : ∀ p ∈ qs, p.decls = [] ∧ p.consts = []) : VE.NormDefaults.Packs.envX U qs = envAt (fill U) 0
/-- Freshness (PK-1 2.4 checks 4–6): `assemble` refuses the attitudes pack for no name, since it has none, and
    for no label, since frame labels are distinct (`frameLabels_nodup`). -/
theorem assemble_attitudes (A : AttDoc) (h : WellFormedAtt A = true) (U : UDoc) (used : Nat) (hu : used ≤ 256) :
    VE.NormDefaults.Packs.assemble U used [attitudesPack A] = .ok [attitudesPack A]
/-- Origins (PK-1 obligation 5): every label has exactly one origin, and nothing else has one. -/
theorem attitudesPack_originsExact (A : AttDoc) (h : WellFormedAtt A = true) :
    VE.NormDefaults.Packs.OriginsExact (attitudesPack A)
-- lean/VE/NormDefaults/Packs.lean (stub S3a)
/-- A list without the attitudes pack answers today's status: the point check passes. -/
theorem pointCheck_absent (qs : List VE.NormDefaults.Packs.Pack) (holds : VE.Formula → Bool)
    (h : ∀ p ∈ qs, p.id ≠ "attitudes") : VE.NormDefaults.Packs.pointCheck qs holds = .ok ()
/-- A passed check means every premise of the attitudes pack holds at the point. -/
theorem pointCheck_sound (qs : List VE.NormDefaults.Packs.Pack) (holds : VE.Formula → Bool)
    (h : VE.NormDefaults.Packs.pointCheck qs holds = .ok ()) :
    ∀ a ∈ VE.NormDefaults.Packs.packPremises qs "attitudes", holds a.2 = true
/-- PK-1's typing obligation for this provider (A2): its environment `extendEnv (envAt (fill U) 0) [] []` is
    `envAt (fill U) 0`. -/
theorem frame_typed_fill (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : VE.NormDefaults.WellFormedU U = true) :
    ∀ φ ∈ framePremises A, φ.WellFormed (envAt (fill U) 0) []
/-- `hw` is needed (SR-1): without it, a base predicate named `unsaid__<p>` used in a `knows` content puts that
    name into a factive premise (fixture F-AT8). -/
theorem frame_unsaidFree (A : AttDoc) (h : WellFormedAtt A = true) (unspec : List String) (U : UDoc)
    (hU : toU A unspec = some U) (hw : VE.NormDefaults.WellFormedU U = true) : ∀ φ ∈ framePremises A, UnsaidFree U φ
theorem settledX_of_settled (U : UDoc) (X : List VE.Formula) (B : VE.Structure.{u}) (r : Regulated)
    (vs : List B.Carrier) (b : Bool) (hs : SettledAs U B r vs b) : SettledAsX U X B r vs b
/-- At a base satisfying an assembled `X` that reads no unsaid table, SETTLED with and without `X` agree. -/
theorem settled_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) (b : Bool) :
    SettledAs U B r vs b ↔ SettledAsX U X B r vs b
theorem undecided_frame_agree (U : UDoc) (X : List VE.Formula) (hfree : ∀ φ ∈ X, UnsaidFree U φ)
    (B : VE.Structure.{u}) (hX : Sat B X) (r : Regulated) (vs : List B.Carrier) :
    UndecidedAt U B r vs ↔ UndecidedAtX U X B r vs
```

`frame_unsaidFree`'s proof note (SR-1): `WellFormedU U` includes norm-defaults' `reservedFree`, which requires
`U.D.E.predicates (unsaidName p) = none` for each `p ∈ U.unspec` (`lean/VE/NormDefaults/Tree.lean:109`). A frame
premise names only generated `attitudes__` names and base predicates of its content, which is typed over `baseEnv A`;
the environment of `toU A unspec` is `envAtt A`, which declares every such base predicate, so none of them is an
`unsaidName p`. `att_conflict_sound` is no new theorem: it is `VE.NormDefaults.Wire.layered_conflict_sound` at
PK-1's assembled X (edit 6). PLAN draft 1's `mistaken_belief_settled` and its placeholder `decidesAt` become fixture
R1 (section 7.3), through the existing `settled_of_table3` and `settledX_of_settled`.

**Restated against PK-1 as built (refresh, RF-5, RF-6; Astra r2 1, Fable r2).** The statements from
`attitudesPack_declares_nothing` to `pointCheck_sound` are new; `attitudesPack` is restated (section 2.9); the
others keep their text, since the one declaration stays in `envAtt` (section 2.4). Proof notes:
`attitudesPack_declares_nothing` and `attitudesPack_originsExact` by unfolding (`names = []`, and origins are
`frameLabels A` mapped); `names_in_base` from `names_fresh`, `keyOf_name` and `envAt`'s base level over `envAtt A`;
`envX_declFree` by `extendEnv_nil` after the flat maps are empty; `assemble_attitudes` by `assembleIn`'s seven
checks (`attitudes` is in `packOrder`; one pack; `frameLabels_nodup`; no names; `used ≤ 256`); `pointCheck_absent`
from `packPremises_absent`; `pointCheck_sound` from `List.find?_eq_none`. No `ExpandsOn` is stated: the pack is a
`constraint` pack (section 2.9). AT-2 reuses `bindCertX` for certificates, unchanged, and keeps every legacy pack's
point behaviour (`pointCheck_absent`).

### 6.3 AT-3a (`lean/VE/Attitudes/Wire.lean`; the layered kind)

```lean
namespace VE.Attitudes.Wire
/-- The decoder ends with `checkAtt` (SR-7): a decoded document is well formed, its lexicon included, so the
    elaborate kind never encodes a document that was not checked. -/
theorem decodeAttDoc_wellFormed (j : Lean.Json) (A : VE.Attitudes.AttDoc) (hd : decodeAttDoc j = .ok A) :
    VE.Attitudes.WellFormedAtt A = true
/-- A replayed status point satisfies the frame; SETTLED and UNDECIDED hold over the assembled X; UNKNOWN claims
    nothing. -/
theorem attitudes_status_sound (j : Lean.Json) (L : VE.NormDefaults.Wire.LayeredU)
    (d : VE.NormDefaults.Wire.StatusX L) (hr : VE.NormDefaults.Wire.replayStatusX L j = .ok d) :
    VE.Norms.Sat d.S.M.asStructure ((VE.NormDefaults.Packs.packPremises L.packs "attitudes").map (·.2)) ∧
    (∀ b, d.status = .settled b → VE.Attitudes.SettledAsX.{0} L.U L.X d.S.M.asStructure d.r d.vs b) ∧
    (d.status = .undecided → VE.NormDefaults.Wire.UndecidedAtX.{0} L.U L.X d.S.M.asStructure d.r d.vs)
end VE.Attitudes.Wire

namespace VE.Attitudes
/-- The row's composition fact: an admitted list with `attitudes@0` lists `norms@0` and a completion chain, and never
    `reports@0`. It does not say that the list's route reads the pack (section 2.9, OPEN-2). -/
theorem attitudes_row_composes (ps : List String) (r : VE.Compose.Route)
    (h : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r) (ha : "attitudes@0" ∈ ps) :
    "norms@0" ∈ ps ∧ ("norm-defaults@0" ∈ ps ∨ "readings@1" ∈ ps) ∧ "reports@0" ∉ ps
end VE.Attitudes

-- `lean/VE/Defaults/Route.lean`, namespace `VE.NormDefaults.Wire` (the stub, one file, keeps them in `VE.Attitudes.Wire`)
/-- A case whose profile list has `attitudes@0`; `decodeAttDoc` answers a missing block. -/
def attitudesOn (j : Lean.Json) : Bool :=
  (VE.NormDefaults.Wire.profilesOf (j.getObjValD "environment")).contains "attitudes@0"
/-- `attitudesPack A` assembled into the list the existing decoder returned. The count is `0`: the pack has no names,
    and `decodeSoftU` or `decodeRightsU` has already passed `assemble`'s limit over the same names at its own count. -/
def withAttitudesPack (L : VE.NormDefaults.Wire.LayeredU) (A : VE.Attitudes.AttDoc) :
    Except String VE.NormDefaults.Wire.LayeredU := do
  let packs ← VE.NormDefaults.Packs.assemble L.U 0 (L.packs ++ [VE.Attitudes.attitudesPack A])
  pure { L with packs := packs }
/-- The attitudes route's decoder (DRI at-0 item 1): the existing decoder, then the pack when `attitudes@0` is on.
    `decodeSoftU` and `decodeRightsU` do not change. -/
def decodeLayeredAtt (j : Lean.Json) : Except String VE.NormDefaults.Wire.LayeredU := do
  let L ← VE.NormDefaults.Wire.decodeLayered j
  if attitudesOn j then withAttitudesPack L (← VE.Attitudes.Wire.decodeAttDoc j) else pure L
/-- Without `attitudes@0` the wrapper is today's decoder, so no legacy route changes. -/
theorem decodeLayeredAtt_off (j : Lean.Json) (h : attitudesOn j = false) :
    decodeLayeredAtt j = VE.NormDefaults.Wire.decodeLayered j
/-- With `attitudes@0`, the answer carries the pack of the case's own decoded document. -/
theorem decodeLayeredAtt_pack (j : Lean.Json) (L : VE.NormDefaults.Wire.LayeredU) (hb : attitudesOn j = true)
    (h : decodeLayeredAtt j = .ok L) :
    ∃ A, VE.Attitudes.Wire.decodeAttDoc j = .ok A ∧ "attitudes" ∈ L.packs.map (·.id) ∧
      VE.NormDefaults.Packs.packPremises L.packs "attitudes" = (VE.Attitudes.attitudesPack A).labelled
/-- The answer is exactly the encoding of the elaboration of the case's own decoded document. -/
theorem attitudes_elaborate_acceptance (j : Lean.Json) (A : VE.Attitudes.AttDoc)
    (hd : VE.Attitudes.Wire.decodeAttDoc j = .ok A)
    (L : VE.NormDefaults.Wire.LayeredU) (hL : decodeLayeredAtt j = .ok L)
    (hp : "attitudes" ∈ L.packs.map (·.id)) (id : String) :
    VE.NormDefaults.Wire.layeredKindCase L id "attitudes-elaborate" j =
      .ok (some (VE.Route.Wire.ok id (VE.Attitudes.Wire.encodeElaboration A)))
/-- Main's theorem, restated: with the row in `layeredRows`, its kind is no longer `kindCase`'s. -/
theorem layeredKindCase_other (L : VE.NormDefaults.Wire.LayeredU) (id kind : String) (j : Lean.Json)
    (hk : kind ∉ VE.NormDefaults.Wire.defaultsKinds) (ha : kind ≠ "attitudes-elaborate") :
    VE.NormDefaults.Wire.layeredKindCase L id kind j = VE.NormDefaults.Wire.kindCase L id kind j
```

`attitudes_elaborate_acceptance` is stated in `lean/VE/Defaults/Route.lean`, not `lean/VE/Attitudes/Wire.lean`:
`layeredRows` holds the row, whose `run` calls `decodeAttDoc` and `encodeElaboration`, so `Defaults/Route.lean` imports
`Attitudes/Wire.lean`, as it imports `Defaults/Wire.lean` for `defaultsRows`. `layeredCase` cannot answer the kind: it
stays today's four kinds (`kindCase_eq`). Main's `layeredKindCase_other` becomes false once the row is in
`layeredRows`, since `kindCase` answers `none` at the new kind, so AT-3a adds `ha` (FR-1).

**The wrapper (DRI at-0 item 1, SIGNED; item 2).** `Layered.lean` cannot import `attitudesPack` or `decodeAttDoc` (a
cycle), so the attitudes route's decoder is `decodeLayeredAtt`, in the layer of the row above. AT-3a's `runLayered` calls
it in place of `decodeLayered`. `decodeSoftU`, `decodeRightsU` and `decodeLayered` keep their text, so every existing
theorem about them stays true, and `decodeLayeredAtt_off` gives today's answer on a case without `attitudes@0`, which
is every legacy list. Item 1's "no attitudes block" is read that way: the guard hook is keyed on the profile (section
10 item 1), so a case with `attitudes@0` and no block would otherwise reach `L.U`'s generated names with no frame, and
accept a point section 5.3 refuses. It answers `decodeAttDoc`'s text instead, as a refusal; on main such a list is
refused too. On main `decodeLayered` refuses both the profile and the block in soft's `checkSource`, which
`decodeRightsU` also runs (`lean/VE/Rights/Wire.lean:117`): the block at the envelope check
(`lean/VE/SoftNorms/Phases.lean:60–61`, first) and `attitudes@0` at the profile check (`:197`,
`VE.Route.Gate.known`'s fixed registry); the row reaches neither. Until both admit such a case, `decodeLayeredAtt` never
reaches `withAttitudesPack`, and `decodeLayeredAtt_pack` and `attitudes_elaborate_acceptance` hold vacuously. Who admits
them is OPEN-11 (section 19). `hL` is kept (item 2) and names the wrapper: `decodeLayered` alone never returns the
pack, so with `hp` a hypothesis over it could not hold and the theorem would say nothing. `hp` is `dispatch`'s test,
kept by item 2; with the wrapper it follows from `hd`, `hL` and `decodeAttDoc`'s off-profile refusal (section 5.1).
Without the pack, the kind answers `dispatch`'s text (section 5.1). Which kinds read the wrapper's list is OPEN-10.

`decodeAttDoc_wellFormed` holds by construction, since `decodeAttDoc`'s last step is `checkAtt` (section 4); with
it, `attitudes_elaborate_acceptance` speaks only of checked documents, and a case whose document fails a check of
section 5.2 gets that check's diagnostic as the kind's answer (fixtures in section 7.6).
`attitudes_status_sound` is false on today's `main` for the `table3` and `enumerate` methods (section 10, item 2);
it holds once AT-2 adds the point check for the attitudes pack (PK-1 did not take it for all packs,
premise-packs.md 7). It speaks of today's status kind (`replayStatusX`), not of a new one. `packPremises` is PK-1's
accessor (`lean/VE/NormDefaults/Packs.lean:67`): over the pack list `L.packs`, answering labelled premises, hence
`.map (·.2)` (refresh). `attitudes_row_composes` takes the gate's answer as a `VE.Compose.Route`, the type `gateOf`
returns (drafts 1–4's stand-in answered a `String`). It was false for drafts 1–4's row; with the restated row
(`requires := ["norm-defaults@0", "norms@0"]`, section 2.9) it holds on every list of section 7.3's search
(refresh, RF-7; Astra r2 2). The
existing `ResponseShape.Encoders.NormDefaults.runCaseReported_fits` keeps its statement; its skeleton gains the new
kind's row. No `VE.Service.runMode_attitudes`, no `attitudes.json`, no `MODES` entry (edit 7).

### 6.4 AT-4 (`lean/VE/Attitudes/Readings.lean`)

```lean
namespace VE.Readings
open VE.Rights (correlate)
open VE.Compose (BaseAdmissibleP ConflictFreeP)

/-- One environment's declarations are among another's. -/
def EnvExtends (E E' : VE.Environment) : Prop :=
  (∀ s ∈ E.sorts, s ∈ E'.sorts) ∧ (∀ c s, E.constants c = some s → E'.constants c = some s) ∧
    (∀ p ss, E.predicates p = some ss → E'.predicates p = some ss)

/-- The assembled family with the frame at its `packOrder` place: earlier packs `P`, later packs `R`. -/
def attQ (N : NDoc) (Att : VE.Attitudes.AttDoc) (P R : List VE.Formula) : List VE.Formula :=
  VE.NormDefaults.fillPremises (supU N) ++ (P ++ (VE.Attitudes.framePremises Att ++ R))
def attQ' (N : NDoc) (Att : VE.Attitudes.AttDoc) (P' R' : Choice → List VE.Formula) (c : Choice) :
    List VE.Formula :=
  VE.NormDefaults.fillPremises (choiceU N c) ++ (P' c ++ (VE.Attitudes.framePremises Att ++ R' c))

/-- Frame typing over any environment extending the frame's own vocabulary (A2: proved, not assumed). -/
theorem frame_shared (Att : VE.Attitudes.AttDoc) (hA : VE.Attitudes.WellFormedAtt Att = true)
    (E' : VE.Environment) (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) E') :
    ∀ φ ∈ VE.Attitudes.framePremises Att, φ.WellFormed E' []
/-- The attitudes pack's provider obligation on the readings route. -/
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
theorem att_nd_superpose_all (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R')
    (hQw : VE.Compose.SlotWellFormed (correlate (sup (fillDoc N)).1) (attQ N Att P R))
    (A : Choice) (hAc : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ attQ N Att P R))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra (fillDoc N) A (attQ N Att P R) Γ φ cert = true)
    (c : Choice) (hc : Compatible (fillDoc N) c) (hAc2 : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
      (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c) B)
    (hp : VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 B) ((choiceDoc (fillDoc N) c).2 ++ Γ)) :
    φ.denote (expand (choiceDoc (fillDoc N) c).1 B) []
theorem att_nd_superpose_countermodel {α : Type u} [DecidableEq α] (N : NDoc) (Att : VE.Attitudes.AttDoc)
    (hA : VE.Attitudes.WellFormedAtt Att = true) (hN : WellFormedND N = true)
    (hF : WellFormedDoc (fillDoc N) = true) (hs : superposable (fillDoc N) = true)
    (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (hE : EnvExtends (VE.Attitudes.baseEnvAtt Att) (sharedEnv (fillDoc N)))
    (P R : List VE.Formula) (P' R' : Choice → List VE.Formula) (hP : Transfers.{u} (fillDoc N) P P')
    (hR : Transfers.{u} (fillDoc N) R R') (A : Choice)
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (M : VE.FiniteModel α)
    (valid : M.Valid (VE.Norms.envAt (VE.SoftNorms.soften (correlate (sup (fillDoc N)).1)) 0))
    (hm : supModelCheckExtra (fillDoc N) A (attQ N Att P R) Γ M = true)
    (hn : (VE.SoftNorms.circ (correlate (sup (fillDoc N)).1) φ).eval M [] = false) :
    ∃ c, Compatible (fillDoc N) c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes (fillDoc N) c M.asStructure ∧
      BaseAdmissibleP (correlate (choiceDoc (fillDoc N) c).1)
        (VE.Rights.limPremises (choiceDoc (fillDoc N) c).1 ++ attQ' N Att P' R' c)
        (pull (fillDoc N) c M.asStructure) ∧
      VE.Norms.Sat (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure))
        ((choiceDoc (fillDoc N) c).2 ++ Γ) ∧
      ¬ φ.denote (expand (choiceDoc (fillDoc N) c).1 (pull (fillDoc N) c M.asStructure)) []
end VE.Readings
```

`transfers_append` is PK-1's and is not restated (edit 6); it is on main, with `transfers_X`, as
`VE.Readings.transfers_append` and `VE.Readings.transfers_X` (`lean/VE/Readings/SupPacks.lean`), which AT-4 imports
(refresh). The three `att_nd_superpose_*` are
`superpose_*_extra` at `D := fillDoc N` and `Q := attQ N Att P R`, with `Transfers` from `fill_transfers`,
`frame_transfers`, `hP`, `hR` and PK-1's `transfers_append` (or `transfers_X` over the assembled packs).

### 6.5 AT-5 (`lean/VE/Attitudes/English.lean`)

```lean
namespace VE.Attitudes
/-- Where a text is read (SR-4): a guard or carve-out, in its enclosing rule's context; or a whole rule, whose
    context is its own. -/
inductive Site where
  | guard (Γ : List String)
  | rule

/-- A catalogue row's candidate readings, written independently of its rewrites, at the row's category (SR-5). -/
inductive Candidates where
  | guards (fs : List AFormula)
  | rules (rs : List ARule)

structure Refusal where
  code : String
  candidates : Candidates
  rewrites : List String

/-- Rendering then reading an admitted attitude condition gives it back, under the document's own lexicon `A.lex`,
    which `WellFormedAtt` validates and ties to `A.E` (D6a, D6b), with an entry for every symbol the condition
    names (D14d); a reading-set part in the empty context (at-rev, AT-R1). -/
theorem att_english_roundtrip (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : (Γ, c) ∈ condsOf A ++ partsOf A) : readCond A Γ (renderCond A Γ c) = .ok c
/-- Rendering is injective on the admitted occurrences of one document, lexicon and context: two admitted conditions
    with one sentence are one condition (one key, holder term and slot term); parts included (at-rev, AT-R1). -/
theorem renderCond_injective (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c c2 : Cond)
    (hc : (Γ, c) ∈ condsOf A ++ partsOf A) (hc2 : (Γ, c2) ∈ condsOf A ++ partsOf A)
    (he : renderCond A Γ c = renderCond A Γ c2) : c = c2
/-- Each refused form with mechanical rewrites (SR-4, SR-5), at its row's category and in its context: the form is
    refused with the row's code; each rewrite has exactly one reading; the rewrites' readings are exactly the row's
    candidates, in order; the candidates are pairwise distinct. -/
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

/-- `P̂` (section 3.4): the content with the slot term for variable 0; the content itself when closed. A content is
    quantifier-free (D12), so variable 0 is replaced directly. -/
def slotTermIn (t : VE.Term) : VE.Term → VE.Term
  | .var 0 => t
  | u => u
def slotIn (t : VE.Term) : VE.Formula → VE.Formula
  | .unary p u => .unary p (slotTermIn t u)
  | .binary p u v => .binary p (slotTermIn t u) (slotTermIn t v)
  | .eq u v => .eq (slotTermIn t u) (slotTermIn t v)
  | .not a => .not (slotIn t a)
  | .and a b => .and (slotIn t a) (slotIn t b)
  | .or a b => .or (slotIn t a) (slotIn t b)
  | .implies a b => .implies (slotIn t a) (slotIn t b)
  | φ => φ
def assertedOf (c : Cond) : VE.Formula :=
  match c.slot with
  | none => c.content
  | some (_, t) => slotIn t c.content
/-- The one reading of section 3.1's admitted row, read whole (RR-1): `and P̂ (not K)`. -/
def assertedNotKnows (c : Cond) : AFormula := .and (.base (assertedOf c)) (.not (.att c))
/-- Section 3.1's admitted row has exactly one reading, its own (RR-1): for each admitted `knows` occurrence, the
    row's text in that context is admitted and its every derivation is `assertedNotKnows c`. -/
theorem assertedNotKnows_one_reading (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
    (hc : (Γ, c) ∈ condsOf A) (hk : c.mode = .knows) :
    readGuard A Γ (renderAssertedNotKnows A Γ c) = .ok (assertedNotKnows c) ∧
      readGuardAll A Γ (renderAssertedNotKnows A Γ c) = [assertedNotKnows c]
end VE.Attitudes
```

`renderAssertedNotKnows A Γ c` (section 3.1's last row for the `knows` condition `c`, in context `Γ`) is AT-5's, as
the other readers and renderers are. `renderCond` and `readCond` (atomic conditions only), `readGuard` and `readGuardAll` (a guard or carve-out, in the
context given), `readRule` and `readRuleAll` (a whole rule) and `refusalOf` (a lookup in english-lean's catalogue,
which instantiates a row's candidates for the text and its site) are AT-5's; each `…All` lists every derivation, as
the all-derivations gate does. All of them read `A.lex` and call the English grammar's lexicon functions and
`wantsPhrase?`; none has a template classifier of its own (SR-3). `renderCond_injective` follows from
`att_english_roundtrip` (apply `readCond A Γ` to `he`). Whole-sentence acceptance (A4): `readRuleAll A s` has length 1
for the section 3.3 sentence and for each of the seven pilot guards rendered as rules.

## 7. Fixtures (draft 1's computed in the stub; draft 2's and draft 3's new ones *expected*)

**Refresh.** Every value below marked *expected* was computed as stated in AT0C, and the refreshed stub recomputes
them all on main (section 13): its output equals the pinned run's except D5's text. Since AT0C the fixtures run on
the frozen `table` (F-AT1 and the documents built from it); `fixtureTable` and its variants remain where a fixture
needs a table of its own (F-AT3, F-AT7, the closure-review tables). **Draft 6.** On main `9ba2140e2`, with the decider token `unstated`, the
output is the refreshed stub's, line for line, plus the lines of section 7.3's draft 6 table
(`docs/spec/attitudes/stub-run-20261102.txt`).

The fixture environment: sorts `claude_instance`, `situation`; base predicates the seven category atoms on
`situation` (`mass_casualty_weapon_uplift`, `critical_infrastructure_attack_uplift`, `damaging_cyberweapon`,
`undermining_ai_oversight`, `disempowering_humanity`, `illegitimate_power_seizure`, `csam_generation`) and seven
hand-named `intentionally_does_restricted_action_<i>` on (`claude_instance`, `situation`); the regulated permission
`weapons_uplift_permitted (claude_instance, situation)`, act "{0} do the weapons uplift in {1}", default deny (the
placeholder `unspecified` requires it). Holder sort `claude_instance`. Every condition: holder `var 1`, slot
`("situation", var 0)`, content `<category>(var 0)`. `fixtureTable`: words "very likely" and "quite likely", the
pair ("very likely", "quite likely"), premises 1 and 2, premise 3 for both words (all hypothetical).

The **fixture lexicon** (SR-3; new in draft 2): the lexical view of that environment, no overlay, and a lexicon that
selects the pilot's wordings: nouns "instance of Claude" and "situation"; each category atom `{0} is classified as
"<category>"`; each hand-named term its own pilot wording (`{0} intentionally does the weapons uplift in {1}` for
the first, section 3.3; no two alike, as V4 requires); the regulated act's wording. Its letters and spellings are
the grammar's defaults. `Lexicon.valid` holds on it and `lexAgrees` holds (*expected*). Draft 2 adds a constant
`s1 : situation` (spelled "s1") for the D14b fixture and its collision pair only. Draft 3 extends it for D15 with
that row's 240 predicates (RC-3), and leaves out of it the symbols C-d's documents (and so D14d's fixture) declare
in `E` only (RC-1).

### 7.1 Documents

| Fixture | Document | Computed |
|---|---|---|
| F-AT1 | u0165.s01: guard `(knows C ∧ intends C) ∨ thinks quite likely C`; `intends` kept only as a fixture (F4) | check ok; names `attitudes__knows__1`, `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`; 2 frame premises, labels `attitude:factive:attitudes__knows__1`, `attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1`; elaborated guard `or (and knows__1(v1,v0) intends__1(v1,v0)) thinks_quite_likely__1(v1,v0)` |
| F-AT2 | u0165.s01 and u0165.s07, F-AT1's shape on two categories | check ok; six keys `__1` and `__2` per mode; 4 frame premises (factive ×2, knows→thinks ×2), none across contents; from `knows__1`: reaches `thinks_quite_likely__1`, not `thinks_quite_likely__2`, not `knows__2` |
| F-AT3 | "very likely" or "quite likely" on one content, table without the pair, document declares it | with the pair: one premise `thinks_very_likely__1 → thinks_quite_likely__1`; without it: none; `atLeast` (very, quite) true, (quite, very) false |
| F-AT5 | the pilot's shape (F4), seven rules: `(knows C_i ∧ intentionally_does_restricted_action_i(c, s)) ∨ thinks quite likely C_i` | check ok; 14 generated keys + 7 hand-named = 21 open terms; 14 frame premises |
| F-AT6 | knows, very likely, quite likely on one content | 4 premises: factive, knows→very, knows→quite, very→quite (`framePairs_transitive`'s instance) |
| F-AT7 | knows and very likely, table with premise 3 for "quite likely" only | 1 premise (factive); with "very likely"'s own item: 2 (factive, knows→very) |
| F-AT0 | F-AT1 with the attitude conditions removed | check ok; 0 keys; 0 premises; `envAtt` agrees with `E` on every declared name and on three generated-looking names |
| Tables | `table`, `fixtureTable`, `fixtureTableNoPair`, `badTableKnows` (premise 3 for "very likely" only, with the pair), `badTablePair` (adds "likely" and the pair ("quite likely", "likely") but not ("very likely", "likely")) | reviewed: true, true, true, false, false; `badTablePair`'s closure derives ("very likely", "likely") without an item |
| F-AT8 (SR-1) | F-AT1 with a base predicate `unsaid__weapons_uplift_permitted` on `situation` (with a wording) and the `knows` content `unsaid__weapons_uplift_permitted(var 0)`; `unspec := ["weapons_uplift_permitted"]` | *expected*, as the reviewer evaluated draft 1 through Lean: check ok; `toU` gives a document; its factive premise names `unsaid__weapons_uplift_permitted`; `WellFormedU` false. So `frame_unsaidFree` without `hw` is false, and with `hw` it does not apply |
| C-a (SR-2) | two documents: F-AT1 with the `knows` content the closed `⊤` (no slot); and with the content `⊤`, slot kept | *expected*: draft 1 admitted both, as two keys differing only in `slotSort`, with one sentence (section 3's rendering does not show an unused slot); draft 2 admits the first and refuses the second at D14a |
| C-b (SR-2) | two documents: F-AT1 with the `knows` content the closed `mass_casualty_weapon_uplift(s1)`; and with the content `mass_casualty_weapon_uplift(var 0)`, slot `(situation, s1)` | *expected*: draft 1 admitted both (two keys, unrelated relations) with one sentence "… knows that s1 is classified as "mass_casualty_weapon_uplift""; draft 2 admits the first and refuses the second at D14b |
| C-c (SR-2) | F-AT1 with the `intends` condition made `wants`: content `mass_casualty_weapon_uplift(var 0)`; and content `and mass_casualty_weapon_uplift(var 0) csam_generation(var 0)` | *expected*: the first is admitted ("that instance of Claude wants that situation to be classified as …", `wantsPhrase?` of `is classified as …` is `be classified as …`); the second is refused at D14c |
| F-AT9 (RR-1) | F-AT1's rule with the guard section 3.1's last row reads, `assertedNotKnows (cond knows C)` = `and C(var 0) (not knows C)`; on `table` | check ok; one key, `attitudes__knows__1`; one frame premise, `attitude:factive:attitudes__knows__1`; elaborated guard `and C(v0) (not knows__1(v1, v0))`. At (category, knows) = (true, absent), (true, present), (false, absent), (false, present): intended true, true, true, false; guard true, false, false, false under the attitude semantics and on `interp` |
| RR-2's documents | F-AT9 with `s1` declared and spelled; F-AT1's rule with the row on C-b's closed content `C(s1)`; F-AT1's rule with the guard `or (assertedNotKnows (cond knows C)) (thinks quite likely C)` | check ok, each (the documents section 7.6's AT-5 read fixtures are read in) |
| C-d (RC-1) | two documents: C-b's first document (the closed `knows` content `mass_casualty_weapon_uplift(s1)`) with `s1` declared in `E` but in neither the lexical view nor the lexicon; and F-AT1 with a base predicate `extra_case` on `situation`, declared in `E` but in none of `authorPredicates`, the lexical view and the lexicon, and the `knows` content `extra_case(var 0)` | *expected*: draft 2 admitted both (D6a and D6b pass, since `lexAgrees` checks only the lexicon's symbols against `A.E`), so `renderCond` had no spelling for `s1` and no wording for `extra_case`, and `att_english_roundtrip` failed on them (the re-check's counterexample); draft 3 refuses both at D14d |
| C-e (at-rev, AT-R1; u0035.s12's shape) | three documents, `s1 : situation` and `c0 : claude_instance` declared and spelled: F-AT1 with one reading-set part, the closed `wants` node holder `c0`, content `mass_casualty_weapon_uplift(s1)`; F-AT1 with that node as a disjunct of its guard and no part; and F-AT1 with the part's content `and mass_casualty_weapon_uplift(s1) csam_generation(s1)` | computed: the first passes `checkAtt`, its names `attitudes__knows__1`, `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`, `attitudes__wants__1` (the part's key after the rules'), its part's claim `attitudes__wants__1(c0)` ("c0 wants s1 to be classified as …"); the second and third are refused at D14c |

### 7.2 F-AT1's points (one instance `0`, one situation `1`)

| Point | Category | Attitudes | Frame holds | Intended | Guard (attitude semantics) | Guard (elaborated, on `interp`) |
|---|---|---|---|---|---|---|
| M1 | false | thinks | true | true | true | true |
| M2 | false | knows, thinks | false | false | true | true |
| M3 | true | knows | false | false | false | false |
| M4 | true | none | true | true | false | false |

### 7.3 F-AT1 on the layered route (`toU fat1 ["weapons_uplift_permitted"]`, `WellFormedU` true)

| Point | First failing frame label | `table3` | `enumerateSettled` | Two fillings (yes, no): valid, outcome | Status |
|---|---|---|---|---|---|
| RM1 (M1) | none | `some false` | `some false` | valid, valid; false, false | SETTLED no (R1: `settled_of_table3`, then `settledX_of_settled`) |
| RM2 (M2) | `attitude:factive:attitudes__knows__1` | — | — | — | refused (`InvalidModel(…)`, section 5.3) |
| RM3 (M3) | `attitude:entails:attitudes__knows__1:attitudes__thinks_quite_likely__1` | — | — | — | refused |
| RM4 (M4) | none | `none` | `none` | valid, valid; true, false | UNDECIDED (u0173.s04's unknowing contribution) |

The frame reads no unsaid table on `U` and is typed over `envAt (fill U) 0` and `baseEnvAtt` (computed); it holds
on both of RM4's filled situations.

**Refresh (computed in the refreshed stub, section 18).** The declaration policy, the point check and the row, on
F-AT1 and `U1 = toU fat1 ["weapons_uplift_permitted"]`:

| Fixture | Computed |
|---|---|
| `assemble U1 0 [p]`, `p` drafts 1–4's pack (declaring the names) | `InvalidInput: generated name attitudes__knows__1 of pack attitudes is already declared` |
| `assemble U1 0 [attitudesPack fat1]` | `ok ["attitudes"]` |
| `toNorms fat1` with its environment `fat1.E` instead of `envAtt fat1` | `VE.Norms.WellFormed` and `WellFormedU` false (the guards are untyped); with `envAtt fat1`, both true |
| `envAt (fill U1) 0` on the three names | `attitudes__knows__1`, `attitudes__intends__1`, `attitudes__thinks_quite_likely__1`, each `some ["claude_instance", "situation"]` |
| `envX U [attitudesPack A] = envAt (fill U) 0` | holds by `rfl`, for every `U` and `A` |
| `OriginsExact`, on F-AT1's pack | origins' keys = the two frame labels; `names = []` |
| `furtherEntries [attitudesPack fat1]` | one entry, `attitudes`, with the two labelled premises and `"names": []` |
| `VE.NormDefaults.Packs.pointCheck` at RM1; at RM2; at RM2 with no attitudes pack | `ok`; `InvalidModel(attitudes): the model violates a background premise: attitude:factive:attitudes__knows__1`; `ok` |
| The gate on `["attitudes@0", "norms@0", "relational-fol@0"]`: drafts 1–4's row; the restated row | `ok norms`; `UnsupportedProfile: attitudes@0 requires norm-defaults@0` |
| Lists of the nine profiles (512) admitted with `attitudes@0` and falsifying `attitudes_row_composes`: drafts 1–4's row; the restated row | 6; none |
| Lists without `attitudes@0`: the gate with the row against `profileTable` | identical on all 256 |

**Draft 6 (computed in the stub on main `9ba2140e2`).** The row in main's form, on main's wider table. The wide lists are
the 4,096 sublists of `acts@0`, `alternatives@0`, `attitudes@0`, `norm-defaults@0`, `norms@0`, `readings@1`,
`relational-fol@0`, `reports@0`, `rights@0`, `scope@0`, `soft-norms@0`, `ve.discourse@1`.

| Fixture | Computed |
|---|---|
| `attitudesRow`: slot, interface, `slotAgrees` (PC-3's C1) | `"pack"`, `.pack "attitudes"`, true |
| Wide lists falsifying `attitudes_row_composes` | 0 |
| Wide lists without `attitudes@0`: the gate with the row against `profileTable` | identical on all 2,048 |
| Wide lists admitted with `attitudes@0`, by route | `readings` 8, `discourse` 6, `normDefaults` 4, `soft` 2, `rights` 2, `alternatives` 1 |
| `["attitudes@0", "norm-defaults@0", "norms@0", "relational-fol@0", "reports@0"]` | `UnsupportedProfile: reports@0 with norms@0 layers` (`reports@0`'s row answers first) |
| `["alternatives@0", "attitudes@0", "norm-defaults@0", "norms@0", "relational-fol@0"]` | `ok alternatives` (OPEN-2) |
| `["attitudes@0", "norm-defaults@0", "norms@0", "relational-fol@0", "right-clauses@0", "rights@0", "soft-norms@0"]`; `["attitudes@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0", "relational-fol@0"]` | `ok clauses`; `ok normDefaults` (OPEN-2) |
| `["acts@0", "attitudes@0", "norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"]` (at3a-order, condition c) | `UnsupportedProfile: acts@0 with soft-norms@0 is not implemented` |
| scope.md's example node with F-AT1's rule: holder `var 0`, no slot; holder `var 1`, no slot; holder `var 1`, slot `(situation, var 0)` | D8's text; D14's text; `ok` (section 10 item 1, OPEN-5) |

**Draft 8 (computed in the stub on main `ea108ea4e`).** The wrapper's parts, on `VE.Defaults.Fixtures`' document DF-α
(`decodeAttDoc` is a stand-in in the stub; on main every case below is refused or answered before the wrapper calls it).

| Fixture | Computed |
|---|---|
| DF-α's case: no `attitudes@0`, no block | `attitudesOn` false; `decodeLayeredAtt` and `decodeLayered` both `[soft]` |
| The block without `attitudes@0` | false; both `InvalidInput: invalid environment envelope` |
| `attitudes@0` without the block | true; both `UnsupportedProfile: Unsupported profile attitudes@0` (main: soft's profile check, `SoftNorms/Phases.lean:197`; the row does not reach it, OPEN-11) |
| `attitudes@0` and the block | true; both `InvalidInput: invalid environment envelope` (main: soft's envelope check, `:60–61`, OPEN-11) |
| `withAttitudesPack` with F-AT1's document, on `[soft]`; on `[soft, rights]`; on a list already holding the pack | `[soft, attitudes]`; `[soft, rights, attitudes]`; `InvalidInput: premise pack attitudes is given twice` |
| `withAttitudesPack` on `[soft]`: route, `envId`, `docHash`; `packPremises`' labels | unchanged; `frameLabels` of F-AT1 |

### 7.4 Each iff and "exactly when", both directions

| Claim | Both sides true | Both sides false |
|---|---|---|
| `frame_iff_intended` | M1, M4 | M2, M3 |
| `att_elaboration_faithful` | M1 (guard true both ways) | M4 (false both ways) |
| `guard_collapse` (a = `intends`) | M1; and `knows`+`intends`+`thinks`, category true (intended; both true) | M4 |
| `guard_collapse` (a = hand-named term, F-AT5) | `knows`+`thinks`, term true, category true | no attitude, term true, category true |
| `forced_iff_reachable` | seed `[knows]` forces and reaches `thinks quite likely` | seed `[thinks]` neither forces nor reaches `knows`; seed `[knows]` neither forces nor reaches `intends` |
| `old_formula_invariant` (φ = every situation is C) | category true: M and `interp` both true | category false: both false |
| `att_old_language_conservative` | `[φ] ⊢ φ` on both sides (proved in the stub by `example`) | `[] ⊢ φ`: empty attitude relations satisfy the frame and refute φ (computed), a countermodel to both sides |
| `interp_restrict` | a generated name's tuple in `J` | a generated name's tuple not in `J` (both relations empty) |
| `restrict_intended` (its hypothesis) | RM1 satisfies the frame: restriction intended | RM2 breaks it: restriction not intended |
| `interp_admissible` (its hypothesis) | M1's typed `J`: admissible | an untyped `J` (tuple reversed): not admissible |
| `settled_frame_agree` | RM1, `b = false`: SETTLED with and without X | RM4, either `b`: the two valid fillings disagree, and X holds on both |
| `undecided_frame_agree` | RM4 | RM1 (`enumerateSettled` gives `some false`, so no two admissible fillings disagree) |
| premise 3 exactly where its item passed (D-A4) | F-AT7 with the item | F-AT7 without it |
| premise 4 exactly when the scale orders the words | F-AT3 with the pair | F-AT3 without it; and the reverse direction |
| `Table.reviewed` exactly when the closure adds nothing unreviewed | `fixtureTable`, `table` | `badTableKnows`, `badTablePair` |
| `checkAtt` | F-AT0 to F-AT8, the first document of C-a and of C-b, the first of C-c, and the first of C-e (a closed `wants` part, at-rev) pass | D1 to D18, D0, D6a, D6b and D14a–D14d each fail at their own check (draft 2's and draft 3's rows *expected*) |
| D14d: admitted exactly when every symbol has its entry (RC-1) | C-b's first document, `s1` in the lexical view and the lexicon: admitted | C-d's two documents: refused at D14d (*expected*) |
| `frame_unsaidFree`'s `hw` (SR-1) | F-AT1 with `unspec := ["weapons_uplift_permitted"]`: `WellFormedU` true, the frame unsaid-free | F-AT8: `WellFormedU` false, a factive premise names an unsaid table (*expected*) |
| `renderCond_injective` (SR-2) | the three conditions of F-AT1: three sentences | each collision pair C-a, C-b: one sentence for two keys in draft 1; in draft 2 one of the two is not admitted (*expected*) |

### 7.5 One `#guard` per theorem (A3)

`names_fresh` (F-AT1); `names_injective`, `keyOf_name` (F-AT2); `envAtt_extends` (F-AT1's category atom);
`toNorms_wellFormed` (F-AT1); `frame_wellFormed`, `frame_universalQF`, `frameLabels_nodup` (F-AT2);
`framePairs_modes`, `framePairs_transitive` (F-AT6); `att_elaboration_faithful`, `frame_iff_intended` (F-AT1, M1–M4);
`empty_relations_frame` (F-AT1, F-AT2); `seed_intended`, `mistaken_belief_admissible` (F-AT1, M1); `guard_collapse`
(F-AT1); `table_reviewed`; `settledX_of_settled` (RM1, through `table3 = some false`); `attitudesPack_premises`
(F-AT1); the diagnostics D1–D18 all fail. Every `#guard` of draft 1 holds. Draft 2 adds, to be written and run when
the stub is updated: `frame_unsaidFree` on F-AT1 (with `hw`) and F-AT8 (without it); the diagnostics D6a, D6b and
D14a–D14c; the collision pairs C-a, C-b and the `wants` pair C-c. Draft 3 adds D14d and C-d (RC-1), and reruns D15
with its extended lexicon (RC-3). Section 17 adds F-AT9's (one key, the factive premise, its four points), RR-1's
(the row's tree is `and P̂ (not K)`, not the composed `and P̂ (and P̂ (not K))`; `P̂` at a constant slot term and
on a closed content; F-AT9's and the closed row's `knows` occurrences meet `assertedNotKnows_one_reading`'s
hypotheses) and RR-2's (its documents admitted, its texts distinct, exactly the three row texts with one reading). At-rev
(AT-R1) adds C-e's two: the part admitted, named after the rules' keys and claimed at its holder; the node in a guard
and the compound part refused at D14c. Section 18's restated statements have their `#guard`s
in section 7.3: `attitudesPack_declares_nothing`, `names_in_base`, `assemble_attitudes`, `attitudesPack_originsExact`,
`pointCheck_absent` and `pointCheck_sound`; `envX_declFree` holds by `rfl` on the fixture. Draft 8's are in section 7.3:
`decodeLayeredAtt_off` on the two cases without `attitudes@0`, and `decodeLayeredAtt_pack`'s pack and labels on
`withAttitudesPack`, its last step. The statements about wire,
route kinds, readings and English (sections 6.3 to 6.5) have no finite instance before their batches; section 7.6
lists their acceptance fixtures.

### 7.6 Acceptance fixtures of later batches (not computable before them)

- AT-2: F-AT1's points through the layered status kind with the point check (RM1 SETTLED no, RM4 UNDECIDED, RM2 and
  RM3 refused with the labels above); F-AT1 conflict-free under the assembled X; every existing profile's layered
  output byte-identical, the status kind's on `[]`, `[soft]` and `[soft, rights]` included (`pointCheck_absent`);
  `[soft, attitudes]` assembled with no name refused; the `attitudes` entry of `layered_elaborate` as section 7.3's
  `furtherEntries` row (refresh).
- AT-3a: F-AT1 as wire cases, each kind that reads `runLayered`'s `L` (OPEN-10), with the fixture lexicon, decoded
  through `decodeLayeredAtt` (DRI at-0 item 1; OPEN-11), `attitudes-elaborate` answering the elaboration and every list
  without `attitudes@0` byte-identical to `main`;
  section 5.1's malformed cases with their texts;
  `attitudes_row_composes`'s lists (`norms@0` with `norm-defaults@0` on the soft and rights routes, the same with
  `readings@1` on the readings route, and a list with `reports@0` refused, with the text section 7.3 computes), and
  `["attitudes@0", "norms@0", "relational-fol@0"]`, which drafts 1–4's row admits and the restated row refuses with
  `UnsupportedProfile: attitudes@0 requires norm-defaults@0` (refresh, section 2.9). The row's values pass `interface_slot`
  and `interface_functional` on the real table (PC-3's C1, C2).
- AT-3a, the signed order (at3a-order item 1, conditions c and d): `["acts@0", "attitudes@0", "norm-defaults@0",
  "norms@0", "relational-fol@0", "soft-norms@0"]` stays refused through `actsRefuses` (section 7.3); SR-6's fixture
  below stays selected; if AT-3a merges first, PC-6 adds its F6.11.
- AT-3a, the decoder's last step (SR-7): `attitudes-elaborate` on F-AT1's wire case with one change of section 5.2
  (D1, D6a, D6b, D9, D14a, D14b, D14c, D14d, D18) answers that row's diagnostic, not an elaboration; and with the
  `lexicon` field missing, the decoder's own text. Without `attitudes@0`, `decodeAttDoc` called directly on a
  case with an attitude node answers `UnsupportedProfile: an attitude condition needs attitudes@0`, and the kind
  answers as section 5.1 says (FR-3).
- AT-3a, unchanged contracts (SR-6): on W1's, soft's and P0's routes, with `attitudes@0` off, a guard holding
  `{"attitude": {}}`, `{"attitude": 1}`, a well-formed attitude node, or an attitude node with an extra field
  answers exactly what `main` at AT-3a's base answers (`array expected` at `49de179e`); and fault order is today's:
  a document pairing an unknown predicate in one rule with an attitude node in another answers what `main` answers,
  in both orders. On W1's route that is `array expected` in both orders, read from the code (RC-2): `decodeSource`
  decodes every rule (`lean/VE/Norms/Wire.lean:303`) before `validate` (`:306`), where the unknown predicate is raised
  (`lean/VE/Norms/Tree.lean:241`). Soft's and P0's answers are whatever `main` answers. Recorded from `main` before
  the hook lands, then compared byte for byte after it.
- AT-3b: fuzz mutants as PLAN AT-3b, including swaps of two keys' holders, request paths and labels, on the rows
  AT-3b adds to the rd-9 relay-binding inventory (every field of the answer classified as bound or Lean-derived, each
  bound field's mutants `CheckerUnavailable`; refresh).
- AT-4: every existing readings fixture byte-identical; the main translation's eight choices with the frame.
- AT-5: `att_english_roundtrip` on every condition of F-AT1 to F-AT9 and of C-c's admitted document;
  `renderCond_injective` on F-AT2's six conditions in their context; `refused_have_rewrites` on each row of section
  3.4's first table, at its site (the guard rows in F-AT1's rule context, the "unless" row as a whole rule of
  F-AT1), against the row's candidates; `readRuleAll` of the section 3.3 sentence and of the seven pilot guards has
  length 1.
- AT-5, the admitted row and its boundary (RR-2; the stub's `readFixtures`, each read in F-AT1's rule context
  `[situation, claude_instance]`, with `P(t, C)` = "t is classified as "C"" and `C`, `C'` the first and the last
  category). `assertedNotKnows_one_reading` on F-AT9's `knows` occurrence and on the closed row's. Each text below
  read by the English reader, not a constructed guard: an admitted text answers `readGuard = .ok a` and
  `readGuardAll = [a]`; a refused one `readGuard = .error "NegatedFactive"` (`readRule` for the rule):

  | Fixture | Text | Answer |
  |---|---|---|
  | row | "both P(that situation, C) and that instance of Claude does not know that P(that situation, C)" | `[assertedNotKnows (cond knows C)]` (F-AT9's guard) |
  | row-closed | "both P(s1, C) and that instance of Claude does not know that P(s1, C)" | `[and C(s1) (not knows C(s1)), closed]` |
  | row-nested | "either both P(that situation, C) and that instance of Claude does not know that P(that situation, C), or that instance of Claude thinks it quite likely that P(that situation, C), or both" | `[or (assertedNotKnows …) (thinks quite likely C)]` |
  | content-mismatch | "both P(that situation, C') and … does not know that P(that situation, C)" | refused |
  | slot-mismatch | "both P(s1, C) and … does not know that P(that situation, C)" | refused |
  | slot-mismatch-closed | "both P(that situation, C) and … does not know that P(s1, C)" | refused |
  | order | "both that instance of Claude does not know that P(that situation, C) and P(that situation, C)" | refused |
  | either | "either P(that situation, C) or that instance of Claude does not know that P(that situation, C), or both" | refused |
  | bare | "that instance of Claude does not know that P(that situation, C)" | refused |
  | unless | "Every instance of Claude must not do the weapons uplift in each situation if P(that situation, C), unless that instance of Claude knows that P(that situation, C)." (a whole rule) | refused |

  F-AT9 and the search's T9 evaluate a constructed guard and do not call the reader, so they cover the row's
  meaning, not this boundary.

## 8. Limits

No new budget. Generated predicates count against `MAX_PREDICATES` (256, with the author's; D15). A document's
scale: at most 8 words and 64 pairs (`scaleCaps`, D5). A generated name is at most 64 bytes (D17). Formulas share
W1's node budget (10,000) and depth (64). A refused document is refused, never given a verdict. Every UNKNOWN of the
routes stays UNKNOWN. `MAX_PREDICATES` bounds the declared plus the unspecified predicates (norm-defaults 5.1, the
"filled" count; `ve/norm_defaults_contract.py`). The constitution's main translation has 50 declared and 65 filled at
the pinned run, and AT-0p's has 63 declared and 78 filled (50 − 1 hand-named term + 14 open terms; 15 unspecified).
With the seven hand-named intention terms it would have **about** 70 declared and 85 filled (**estimate**: AT-1's 14
generated predicates replace AT-0p's 14 open terms one for one). The readings route's size count (`sizesJson`) adds
its own three generated predicates to the filled count and is checked against the same 256: 68 at the pinned run and
81 in AT-0p, measured (`readings/nd-all-check.json` in `research/attitudes/run-baseline` and `run-at0p`; the filled
counts are these less three), **about** 88 with the intention terms.

## 9. Small-scope counterexample search (debate round 3)

Method (stub section S6). Vocabulary: sorts `claude_instance`, `situation`, `user`; base `p_case`, `q_case` on
`situation`; holder sorts `claude_instance` and `user`. A pool of twelve conditions: `knows`, `thinks quite likely`,
`thinks very likely`, `believes`, `intends` of `p_case(x)`; `knows` and `thinks quite likely` of `q_case(x)`; `knows`
of `¬p_case(x)`; closed `knows ⊤` and `thinks quite likely ⊥`; and, under `∃ user`, a user's `knows` and `thinks
quite likely` of `p_case(x)`. Documents: every condition alone, and every pair under `or`, `and` and `not (or …)`:
210 documents, each with at most two keys and two holder sorts. Models: five domain layouts of at most two elements
(sorts may share an element), with every `p_case` and `q_case`; on each, every typed attitude relation. Checked per
document and model: `frame_iff_intended` (T1), `att_elaboration_faithful` at every valuation (T2), `guard_collapse`
with `a` ranging over `p_case(x)`, `⊤` and an `intends` condition (T3), `seed_intended` and `forced_iff_reachable`
for every seed (T4), `mistaken_belief_admissible` (T5), `framePairs_transitive` and `framePairs_modes` (T7),
`empty_relations_frame` and `old_formula_invariant` (T8). As a control, PLAN draft 1's `guard_collapse` (no `hp`, the
thinks condition drawn from the whole pool) is checked the same way.

Draft 1's result (computed; the rerun on the frozen table follows):

| | Count |
|---|---:|
| documents, all well formed, each with at most two keys | 210 |
| document-model pairs | 6,720 |
| collapse instances tried (a frame pair links the two conditions) | 480 |
| candidate seeds enumerated (every sublist of the atoms; T4 checks those with no nonfactive knowing, RR-3) | 63,188 |
| counterexamples to T1, T2, T3, T4, T5, T7, T8 | 0 each |
| counterexample valuations to PLAN draft 1's `guard_collapse` (the control) | 17,096 |

The control shows the search finds A3's counterexample class, as the debate expected: a `thinks` condition whose key
is not in the document. The search is evidence against small counterexamples only; AT-1's proofs decide.

**The rerun on the frozen table (SR-8, RC-1; AT0C, RR-3; rerun in draft 6 on main `9ba2140e2`).** The search runs on
the frozen table, with a lexicon for the search vocabulary (valid, and `lexAgrees` holds) and five more pool members:
four that the new checks refuse, `knows ⊤` with an unused slot (D14a), `knows p_case(var 0)` slotted at a constant
`c0 : situation` (D14b), `wants` of `p_case(x) ∧ q_case(x)` (D14c) and the closed `knows p_case(c1)` with a constant
`c1 : situation` that `E` declares and the lexicon does not (D14d); and one they admit, `wants` of `p_case(x)`; and
the admitted row (F-AT9) as T9. Every document holding a refused member fails `checkAtt` at that member's row. The
stub's final `#guard` asserts these counts:

| | Count |
|---|---:|
| documents; of them well formed; of them refused at their member's row | 477; 287; 190 |
| draft 1's 210 documents, all still well formed | 210 |
| refusals at the wrong row; well-formed documents that should have been refused | 0; 0 |
| document-model pairs | 9,184 |
| collapse instances tried | 768 |
| candidate seeds enumerated; seeds T4 checks (no nonfactive knowing, RR-3) | 88,188; 64,177 |
| admitted-row documents; points tried (T9) | 40; 2,080 |
| counterexamples to T1, T2, T3, T4, T5, T7, T8, T9 | 0 each |
| counterexample valuations to PLAN draft 1's `guard_collapse` (the control) | 34,237 |

## 10. Integration points AT-0 pins

1. **Guard-node hook.** One point: `VE.Norms.Wire.decodeNorm`'s guard and carve-out decoding
   (`budgetFormula 64 count` at `lean/VE/Norms/Wire.lean:266–272`). Soft's `ruleFields` calls `decodeNorm` for the
   W1 fields (`lean/VE/SoftNorms/Phases.lean:240–241`) and `VE.Readings.Wire.decodeNorm` calls it too
   (`Readings/Wire.lean:119–124`), so no second guard decoder remains. With `attitudes@0` on, `decodeNorm` reads
   guards and carve-outs as `AFormula` (W1's formula grammar plus the `{"attitude": …}` object, one node budget) and
   returns an `ARule`; the chain's source decoder elaborates the whole document once (`toNorms`), since names depend
   on all keys. With it off, `decodeNorm` and every caller are unchanged and answer `array expected` for the object,
   as today; section 5.1's new text belongs to `decodeAttDoc` only (SR-6). Soft exception conditions
   (`exceptionFields`, `decodeBudgeted`) admit no attitude node. Serialised after act-phrases' AP-1 and AP-3.
   **On main at `6d0a10526` (refresh, Astra r1 3, Fable r1 6).** The line numbers above are `49de179e`'s. The one
   decoder of a norm's envelope is now `normFields` (`lean/VE/Norms/Wire.lean:319`), shared by `decodeNorm`
   (`:341`, which budgets the guard and carve-outs with `budgetFormula`) and the family readers
   (`lean/VE/Norms/Family.lean:379`); soft calls `decodeNorm` with `shared := false` (each formula its own budget,
   `lean/VE/SoftNorms/Phases.lean:241–242`), and `VE.Readings.Wire.decodeNorm` calls it at `Readings/Wire.lean:132` (draft 6, on `9ba2140e2`; `:123` on `6d0a10526`).
   The hook reuses `normFields` and keeps soft's `shared := false` budget. Both Lean admission paths call these
   decoders (`lean/VE/Norms/Admission.lean:58`, `lean/VE/SoftNorms/Admission.lean:25`), so one hook still suffices,
   and SR-6's compatibility fixture covers both paths. AP-1 and AP-3 are merged.
   **The order with PC-6 (draft 6).** The DRI's at3a-order ruling (`reviews/dri-decisions-20261029-at3a-order.md` item 1,
   SIGNED) lets AT-3a land before PC-6, and profile-composition 3.6 states the same; `at-3a`'s row waits on `at-2`
   only. Its conditions bind AT-3a whichever merges first: (a) no guard-node parser outside `normFields` and
   `lean/VE/Attitudes/Wire.lean`, and the soft decoder's edit only passes the `attitudes@0` switch and keeps
   `shared := false`; (b) `actsRefuses` and `decodeRegulatedIn` untouched, so the row admits no list with both `acts@0`
   and `soft-norms@0`; (c) and (d) the fixtures of section 7.6. Whichever of AT-3a and PC-6 merges second rebases on
   `Norms/Wire.lean`. PLAN section 5 and its AT-3a row still read "PC-6 before AT-3a"; the signed ruling governs (OPEN-4, ruled, section 19).
   **Scope's `own` (draft 6).** `own` never reaches this decoder on a scope document: scope's `substOwn` replaces it in
   the JSON before the chain's decoder runs (scope.md 1.4: "Scope decodes no condition"), so AT-3a's hook reads a formula
   at `content`, and this spec adds no `own` diagnostic. The substituted node is checked as any node is, so `reguard`
   needs the holder at a holder sort and a slot for the rule's variable (section 7.3). Scope's example node has neither
   (OPEN-5, section 19).
2. **The point check.** `VE.NormDefaults.Wire.replayStatusX` does not check X on the point's model for the `table3`
   and `enumerate` methods today: `situationX` checks the model's validity and literals only, and only the
   `undecided` method checks `extraValid` on its two fillings (`Layered.lean:253–263, 341–369`). So PK-1 adds the
   check once, for all packs: every X premise that reads no unsaid table is checked on the point's model before any
   method; the others stay on fillings, as today.
   **Superseded (refresh, Astra r1 2, r2 1).** PK-1 did not take this request: checking legacy soft premises at the
   point would change today's status answers (premise-packs.md 7). AT-2 adds the check for the attitudes pack's own
   premises only, under AT-0's review, and every legacy pack's point behaviour stays as it is. `replayStatusX` is at
   `lean/VE/NormDefaults/Layered.lean:337` on `6d0a10526`. The check is `VE.NormDefaults.Packs.pointCheck` (section 2.9), run on
   the base situation after `situationX` and before any method; its statements are `pointCheck_absent` and
   `pointCheck_sound` in the same namespace (section 6.2), its fixtures section 7.3's (refresh, RF-6; FR-6).
3. **`ve document` dispatch.** On `main` at `49de179e` both `ve/document.py` and Lean's `document` mode
   (`lean/VE/Service/Document.lean`) exist; AT-3b's dispatch edit is first in the document-mode queue after `lf-16g`
   (edit 7).
   **Superseded (refresh, Astra r1 4, Fable r1 4).** `lf-16g` has merged and deleted the Python loader; `ve/document.py`
   is now the package `ve/document/`. Lean owns admission: SC-1b took the first document-mode slot as a Lean call site
   (`lean/VE/Service/Document.lean`, `scope@0`), and AT-3b is the next call site there, Lean admitting `attitudes@0`
   documents, with Python in `ve/document/` relaying typed answers bound to the request (R8). Before AT-3b relays
   anything, it adds the attitudes answer's rows to the rd-9 relay-binding inventory (`docs/spec/rd-9-relay-binding.md`,
   `INVENTORY` in `tests/test_relay_binding_inventory.py`; owner of relay binding by the DRI's D9 ruling, 2026-10-28).
   So AT-3b is Lean and Python, not "Python or Lean".
4. **The English word table's export.** `ve/english_grammar/codes.json` (`tools/english_codes.py`) has the fixed
   format `codes`, `statuses`, `unsentenced` (`CODES_FORMAT`); it does not carry a word table. AT-5 adds a new
   generated entry `attitude-words` in `tools/regen_generated.py` (a hand-written registration). The refusal rows
   are not in that export: they go to en-sw's `lean/VE/EnglishGrammar/SourceWords.lean` (section 3.4; refresh, C1).
5. **The readings route.** The decoder's call reduces to the `attitudes` pack provider's registration plus the hook of
   item 1 (edit 7); it lands after `lf-14d`, which has merged (refresh).
6. **The `wants` test's one owner (RC-4).** On `main` the test is Python only: `_subject_split` calls `_infinitive`,
   which accepts a candidate only when `_finite` gives the finite phrase back, and the parser's "to VP" readings call
   `_finite` (`ve/report_english.py:85–131` on `6d0a10526`). AT-1w, the batch before AT-1, moves it into Lean as
   `VE.Reports.wantsPhrase?` in the new module `VE.Attribution.Words` (with the finite form it checks against;
   refresh, C14: every attribution file declares in `VE.Reports`), and in the same batch deletes
   `_infinitive` and `_finite`: `reports@0`'s Python English takes both forms from Lean through one new kind of the
   existing `reports` mode (`lean/VE/Attribution/Run.lean`), relayed by `ve/reports_route.py` and checked for schema
   and binding only. `ve/report_english.py` is in the surface layer, which does not import the relay
   (`tools/layer_policy.py`), so it reaches the kind through the `reports` document object its callers already pass
   it. `ResponseShape.Encoders.Reports.runCaseReported_fits` keeps its statement; its skeleton gains the kind's row.
   Every `reports@0` English answer is unchanged: AT-1w records `_infinitive` and `_finite` on every phrase the
   suite's `reports@0` cases reach, before deleting them, and Lean's kind answers the same. So at no merge does the
   test exist in two languages; AT-5 no longer touches it.

## 11. Where this spec differs from the PLAN's Lean text, and why

Each is a statement-level decision for the review; none changes the PLAN's design.

1. `AFormula.elab`, `ARule.elab` are `toFormula`, `toNode`: `elab` is a Lean keyword (elaboration error).
2. `AttDoc` carries `T : Table`, `declared` and `authorPredicates` instead of `scale : Scale`: A1's per-word
   gating needs the table with its items, `MAX_PREDICATES` needs the author's predicate list (as `ReportDoc`), and
   fixtures need a hypothetical table. The decoder always sets `T := table`.
3. `entailsMode` reads `A.T` and `A.scale`; premise 3 for `w` holds when an item-passed word is at or above `w`. In
   the frozen table the closure review makes this the same as the per-word list; a document's declared pair extends
   it as the author's stipulation, shown in the legend. This keeps `framePairs_transitive` true.
4. Labels are distinct per premise (`attitude:factive:<name>`, `attitude:entails:<name>:<name>`): PK-1 refuses
   repeated labels. The PLAN's `attitude:factive`/`attitude:entails` are their prefixes.
5. `contentAt` takes a structure, not a model (the seed theorems have no model yet).
6. `att_elaboration_faithful` drops `hS` and `hρ`, and `frame_iff_intended` drops `hS`: neither is needed, so the
   statements are stronger. `AWellFormed` requires each condition's key to be in `keys A`; without it the statement
   is false for a condition outside the document (A3's lesson).
7. `mistaken_belief_admissible` drops `h` and `hS`; `framePairs_transitive` drops `h`.
8. `guard_collapse` takes any `a` in place of `.att ci` (it covers the hand-named intention term, F4) and compares
   slot terms (`hsl`); `hp` replaces PLAN draft 1's mode and subject hypotheses (A3).
9. `toNorms_isSome` becomes `toNorms_wellFormed`: `WellFormedAtt` ends with W1's `validate`, so the elaborated
   document is W1-well-formed, not only present.
10. New statements: `keyOf_name`, `frameLabels_nodup`, `framePairs_modes` (D-A9), `restrict_intended`,
    `empty_relations_frame` (PK-1's expansion step), `frame_typed_fill` (PK-1's typing), `frame_unsaidFree`,
    `settledX_of_settled`, `attitudesPack_premises`, `frame_shared`, `attitudes_row_composes`; in draft 2,
    `decodeAttDoc_wellFormed` (SR-7) and `renderCond_injective` (SR-2).
11. `settled_frame_agree` and `undecided_frame_agree` are stated for any unsaid-free assembled X, with
    `frame_unsaidFree` for the frame (edit 6 asks for the assembled X; soft's coherence premises can read unsaid
    tables, so the hypothesis is needed).
12. `checkNames` also refuses a generated name equal to a regulated or defined name (else `hide` could hide it).
13. The `MAX_PREDICATES` refusal is `ResourceLimit: MAX_PREDICATES`, `reports@0`'s text, not the PLAN's
    `InvalidInput`.
14. `refused_have_rewrites` adds `2 ≤ r.rewrites.length` (the PLAN's checklist) and applies to section 3.4's first
    table; `AttitudeAdverb` and `UnresolvedHolder` get advice rows, since their rewrites need what the sentence
    lacks. Draft 2 (SR-4, SR-5) states it at the row's category and site, against the row's candidate readings.
15. A declared predicate's template may contain "intentionally" (the hand-named intention term, F4); the
    `AttitudeAdverb` refusal applies to an adverb modifying an act phrase or attitude verb in a guard, not to a
    template matched whole.
16. The section 3.4 rewrites use VE's external negation "it is not the case that …" for negated knowledge. That it
    carries no presupposition for readers is VE's convention (as `reports@0`'s `_NOT`), not measured; the review
    decides whether it needs E2-style items. The statement review (SR-8) made this decision, with the admission of
    section 3.1's last row (asserted-content negated knowledge), part of E2's record: both are written into the
    frozen table's record before PASS. Draft 4 (G5): that admission is decided on six items, since the three
    "Must P?" items test only that P is read as asserted; the three added items ask "Does Claude know that P?".
17. `attitudes_elaborate_acceptance` names `layeredKindCase`, not the PLAN's `layeredCase`, and sits in
    `lean/VE/Defaults/Route.lean`. AT-3a also widens `runOtherCase`'s test and restates `layeredKindCase_other` (section
    6.3, FR-1).
18. `pointCheck`, `pointCheck_absent` and `pointCheck_sound` are in `VE.NormDefaults.Packs`, and the PLAN's AT-2 block
    has `pointCheck` beside the route's statements (section 2.9, FR-6).
19. `attitudes_elaborate_acceptance` adds `hp`, and its `hL` names `decodeLayeredAtt`, not the PLAN's `decodeLayered`.
    `decodeLayeredAtt`, `attitudesOn`, `withAttitudesPack` and their two theorems are new; they fill the plan's
    gap by the DRI's ruling (at-0 items 1, 2; section 6.3), and the frozen plan is not edited.

## 12. Review checklist

| Item (PLAN section 8) | State in this draft |
|---|---|
| `Intended` says what the words mean and nothing more | section 2.8; `forced_iff_reachable`, `framePairs_modes` |
| `mistaken_belief_admissible` has no hypothesis about the content, and is about the given `S` | yes |
| `att_old_language_conservative` has no hypothesis that the frame is empty | yes |
| every frame premise universal with a quantifier-free body | `frame_universalQF`; F-AT2's `#guard` |
| generated names cannot collide with other families | prefix `attitudes__` in PK-1's `reservedPrefixes`; D6, D16 |
| E1's pairs and E2's decisions in `table` with their items, closure review holds | **done** (refresh): E1 and E2 ran 2026-10-13 and MET; `table` is the frozen table (section 2.1), `Table.reviewed` true, G4 removing no word; the asserted-content negated knowledge row admitted on its six items (section 11, item 16; SR-8, G5) |
| every key a hypothesis names is in `keys A` (A3) | yes (`hk`, `hp`, `AWellFormed`, `hseed`) |
| one `#guard` per theorem; the search finds no counterexample | draft 1: section 7.5, section 9; drafts 2–4 and RR-1 to RR-3: done in AT0C (stub `dea412eb`, 477 documents, no counterexample). Draft 5: the restated statements written and elaborated, their fixtures `#guard`s (section 7.3), and every fixture and the search rerun on the refreshed stub (section 18). Draft 6: rerun on main `9ba2140e2` (sections 9, 19), no counterexample |
| statements against main's merged interfaces (refresh; draft 6) | the stub imports QS-1, PK-1 and AR-10 from main `9ba2140e2` (section 13), and `Pack.conditions` and `ProfileRow.interface` are met (section 19); the freshness resolution (one declaration, in `envAtt`), PK-1's environment, expansion, origins and point-check contracts and the row's admission are restated and elaborated (sections 2.4, 2.9, 6.2, 7.3, 18) |
| contents over the base vocabulary; the frame's typing proved on every route (A2) | D13; `frame_wellFormed`, `frame_typed_fill`, `frame_shared` |
| every refused form has two or more one-reading rewrites | section 3.4's first table; advice rows for two forms (section 11, item 14); `BareThinks` needs an admitted word |
| the admitted "both P and H does not know that P" has one derivation, and the refusal's exception is exactly that row (RR-1, RR-2) | section 3.1's whole-row reading; `assertedNotKnows_one_reading`; section 7.6's AT-5 read fixtures (row, closed, nested; content, slot term, order, "either", bare, "unless" refused) |
| the rewrites are the refused form's readings, at its category and in its context (SR-4, SR-5) | section 3.4's candidate readings; `refused_have_rewrites` with `Site` and `Candidates` |
| every admitted condition has its one sentence, and no sentence two admitted conditions (SR-2) | `renderable` in `checkCond` (D14a–D14d); `att_english_roundtrip` on `(Γ, c) ∈ condsOf A`; `renderCond_injective`; C-a, C-b, C-c, C-d |
| admission, rendering and reading share one validated lexicon from its owner (SR-3) | `AttDoc.lex`; D6a (`Lexicon.failures`), D6b (`lexAgrees`), and per condition D14d (`lexCovers`: every predicate and constant the condition names has its entry, RC-1); decoded at AT-3a (section 4) |
| the `wants` test has one owner at every merge (SR-3, RC-4) | AT-1w moves it into Lean and deletes the Python copy (`_infinitive`, `_finite`), `reports@0`'s Python English reading Lean's through a `reports` kind, before AT-1 calls it (section 10 item 6) |
| a decoded document is a checked document (SR-7) | `decodeAttDoc` ends with `checkAtt`; `decodeAttDoc_wellFormed`; section 7.6's route fixtures |
| W1, soft and P0 answers unchanged with `attitudes@0` off (SR-6) | section 5.1; section 10 item 1; section 7.6's compatibility fixtures |
| `frame_unsaidFree` holds as stated (SR-1) | `hw` added; F-AT8 |
| a decoded attitudes case carries its pack, and a case without `attitudes@0` decodes as today (DRI at-0 item 1) | `decodeLayeredAtt`, its two theorems, section 7.3's draft 8 table; which kinds read it, OPEN-10; who admits the case, OPEN-11 |
| no forbidden word in a Lean comment; no prime; names under about 57 characters | the longest is `VE.NormDefaults.Wire.attitudes_elaborate_acceptance` (51); the stub's stand-ins use `opaque`, which AT-1's files must not |

## 13. Reproducing

**Draft 8 (at-0-finish, 2026-11-02).** The stub at `docs/spec/attitudes/SpecStubs_attitudes.lean` has sha256
`b9f84e5a32e1837add9fc2cf3aff8208259de6fb89cd04375973704606301e64`. It elaborates against main `ea108ea4e`, the same way as draft 6 below
(`spec-stub-check.sh`: rc 0, errors 0, warnings 0, sorry 0, 266 s). Its `#eval` output is at-rev's run, line for line, plus
8 lines for section 7.3's draft 8 table. This sha256 replaces draft 6's pin; `stub-run-20261102.txt` stays draft 6's
output and is not regenerated. OPEN-8 still holds for `STUB_SHA256`.

**Draft 6 (2026-11-02), kept as history.** The stub at `docs/spec/attitudes/SpecStubs_attitudes.lean` has sha256
`068912b38b4a41c7a7774e3348c153a7b8538ed7cbfe2f699b79ba26189ffd7c`. It elaborates against main `9ba2140e2`: copy it, untracked, to `lean/SpecStubs_attitudes.lean` of a
worktree of that commit, then run `zsh manage-agents/spec-stub-check.sh <worktree> lean/SpecStubs_attitudes.lean`
(rc 0, errors 0, warnings 0, sorry 0, 531 s). This branch's base is `6d0a10526`, which is why the check runs in a
worktree of main. The run's full output is `docs/spec/attitudes/stub-run-20261102.txt`. This sha256 replaces the
pin of section 18. `research/attitudes/experiments.py` is still not on this branch, so its `STUB_SHA256` is not
changed here (OPEN-8, section 19); `Table` and `Table.reviewed` are unchanged.

**Refresh (2026-10-28), kept as history.** The stub is committed at `docs/spec/attitudes/SpecStubs_attitudes.lean`, beside the other
plans' committed stubs (`docs/spec/premise-packs/SpecStubs_pk1.lean`), and not under `lean/`, whose every `.lean`
file `lean/audit.py` audits. It is the stub pinned at `dea412eb…` (`research/attitudes/stub/SpecStubs_attitudes.lean`
at `923f0a0ea`) with section 18's Lean changes and nothing else: the stand-ins for QS-1, PK-1 and AR-10 replaced by
imports of `VE.Closure.Order` and `VE.Compose.Dispatch` (PK-1's `VE.NormDefaults.Packs` comes through
`VE.NormDefaults.Layered`), and the restatements of RF-5 to RF-7 with their fixtures. It elaborates against main `6d0a10526`: from a built `lean/` of that commit,
`PATH=~/.elan/bin:$PATH lake env lean <worktree>/docs/spec/attitudes/SpecStubs_attitudes.lean` (this run used the
`ve-nightly` build of `6d0a10526`, since this branch changes no file under `lean/`). The sha256 and the run's result
are in section 18; the run's full output is `docs/spec/attitudes/stub-run-20261028.txt`. The pinned original does not elaborate on
main: its PK-1 stand-ins redeclare `VE.NormDefaults.Packs.PackKind`, `RequestPath`, `Pack`, `packOrder` and
`packPremises`, which `Layered.lean` now imports. `research/attitudes/experiments.py` is not on this branch, so its
`STUB_SHA256` pin is not changed here; `Table` and `Table.reviewed` are unchanged.

Drafts 1–4, kept as history. From the worktree root, with the `ve-nightly` build at `49de179e`:
`lake --dir /home/seyran/code/ve-nightly/lean env lean lean/SpecStubs_attitudes.lean`. The stub is untracked and
not committed; it holds no `sorry`. Its sections: S0 stand-ins, S1 definitions, S2–S3 statements, S4 evaluators,
S5 fixtures and `#guard`s, S6 the search. The stub is still draft 1's: updating it to draft 3 (the lists of sections
14 and 15) and elaborating it is the next step, and the command above is the one to run then.

Phase 1's closure-review emitter (`research/attitudes/experiments.py table`) evaluates this spec's `Table.reviewed`
through a copy of that stub, read only, and refuses a stub whose sha256 is not
`2178fb6eb1dfc2be9e908643538190a17da0b78a346954418d247e386b6a35e8` (`STUB_SHA256`, `8538355c`). The stub's `Table`
and `Table.reviewed` equal section 2.1's apart from comments (compared by hand, P1 3). So the stub's update to
draft 3 or later changes that pin in the same commit and reruns `experiments.py selfcheck`; if section 2.1's Lean
changed, the closure review's statement is re-reviewed before any table is frozen. Draft 4 changes no Lean.

## 14. Draft 2: the statement review's corrections

The review of draft 1 (`manage-agents/debates/attitudes-spec/`: `astra.md`, `fable.md`, `result.txt`) converged
after round 3 on **FIX; the build may not start**. Astra's four findings (round 1) and Fable's additions (rounds 1–3)
became one joint position; draft 2 applies it and changes nothing else.

| # | Correction | Where |
|---|---|---|
| SR-1 | `frame_unsaidFree` was false as stated: a base predicate `unsaid__<p>` in a `knows` content, with `p` unspecified, passes `checkAtt` and puts an unsaid name into a factive premise. It gains `hw : WellFormedU U = true`, as `frame_typed_fill` has; the counterexample is a fixture (Astra 1) | 6.2; F-AT8 in 7.1, 7.4 |
| SR-2 | The English round trip's hypothesis `c.key A Γ ≠ none` admitted refused modes and slot collisions. The renderable subset now governs admission: `renderable`, defined once and called by `checkCond` after D14, refuses an unused slot (D14a), a slot term that is not a guard variable (D14b) and a `wants` content without section 3.1's wording (D14c), each with its own text in a fixed order. The round trip takes `(Γ, c) ∈ condsOf A` under `WellFormedAtt A`; `renderCond_injective` is added. De re versus de dicto about a named constant is left to a later admission with its own E2 items (Astra 2, Fable 1) | 2.6; 3.1; 5.2; 6.5; C-a, C-b, C-c in 7.1 |
| SR-3 | `AttDoc` had no lexicon, so the wording check and the renderer read nothing. `AttDoc.lex` carries the English grammar's `Env`, `Overlay` and `Lexicon`; `checkAtt` validates it with `Lexicon.failures` (D6a) and ties it to `A.E` on names and arities (D6b); `decodeAttDoc` decodes it at AT-3a with the grammar's own decoders. D14c and the readers call the grammar's lexicon functions and `reports@0`'s `wants` test (`wantsPhrase?`, moved into Lean by AT-1); no attitude-local template classifier (Astra round 2, Fable round 3) | 1; 2.2; 2.6; 4; 6.5; 7; 12 |
| SR-4 | The rewrites were read as atomic conditions in context `[]`, which cannot hold conjunction, negation or rule syntax, nor resolve a rule's variables. `readCond` reads atomic conditions only; rewrites are read as guards (`AFormula`, in the enclosing rule's context) or as whole rules (`ARule`), by `readGuard`, `readGuardAll`, `readRule`, `readRuleAll` (Astra 3) | 3.4; 6.5 |
| SR-5 | `refused_have_rewrites` did not tie the rewrites to the refused form's readings. Each catalogue row carries its category and its candidate readings, written independently of the rewrites; the theorem says the form is refused, each rewrite has exactly one reading, the rewrites' readings are exactly the candidates, and the candidates are pairwise distinct (Fable 2) | 3.4; 6.5; 7.6 |
| SR-6 | Draft 1 changed W1's frozen answer `array expected` for an attitude object when `attitudes@0` is off. Old entry points keep it; the new text appears only at `decodeAttDoc`. W1, soft and P0 compatibility fixtures cover malformed attitude objects and fault order (Astra 4) | 5.1; 10 item 1; 7.6 |
| SR-7 | `attitudes_elaborate_acceptance` could vouch for unchecked documents. `decodeAttDoc` ends with `checkAtt`; `decodeAttDoc_wellFormed` is added, with route fixtures where a check's failure is the kind's answer (Fable 3) | 4; 5.1; 6.3; 7.6 |
| SR-8 | PASS waits on E1 and E2 recorded in `table` (with the asserted-content negated knowledge decision), the closure review, the stub updated and elaborated, every fixture and the section 9 search rerun on the frozen table with the new refusals in the pool, and a re-review of the changed statements only (both reviewers) | status; 9; 11 item 16; 12 |

Statements changed or added, for the re-review: `frame_unsaidFree`, `decodeAttDoc_wellFormed`,
`att_english_roundtrip`, `renderCond_injective`, `refused_have_rewrites`; definitions changed or added: `Lex`,
`AttDoc.lex`, `mentionsSlot`, `renderCheck`, `renderable`, `lexAgrees`, `checkCond`, `checkAtt`, `Site`,
`Candidates`, `Refusal`; the diagnostics D6a, D6b, D14a–D14c and section 5.1's profile-off rule. Every other statement
is draft 1's, unchanged.

## 15. Draft 3: the re-check's corrections

The re-check of draft 2 (`manage-agents/attitudes-p3ver1.final.md`) returned **FAIL**: SR-1, SR-2, SR-4, SR-5, SR-7
and SR-8 are present and correct in both files, with no substantive change unrelated to the review, and three
problems remain. Draft 3 corrects them and changes nothing else.

| # | Correction | Where |
|---|---|---|
| RC-1 | SR-3's lexicon check worked one way only. `lexAgrees` checks the lexicon's symbols against `A.E`, not the reverse: `A.E.constants` is a function and cannot be listed, and a predicate is covered only when it is in `authorPredicates`, while `A.E` may declare others (fixture D16 does). So a condition could be admitted while naming a constant or predicate with no lexicon entry: the closed content `C(s1)`, with `s1` missing from the lexical view, passed D6a, D6b and D14a–D14c, and `att_english_roundtrip` and `renderCond_injective` could then fail. `renderCheck` gains D14d, its last part: every predicate and constant of the condition, in its holder, its slot term and its content, has its lexicon entry (`lexPred`, `lexTerm`, `lexCovers`): the lexical view declares it with its `A.E` sorts and the lexicon selects its wording or spelling. The counterexample and its predicate twin are fixture C-d; the section 9 rerun gains a D14d pool member | 1; 2.6; 3.1; 5.2; 6.5 (docstring only); 7; 7.1; 7.4; 7.5; 7.6; 9; 12 |
| RC-2 | An SR-6 fixture misstated `main`'s fault order. `decodeSource` decodes every rule (`lean/VE/Norms/Wire.lean:303`) before `validate` (`:306`), where "Unknown predicate" is raised (`lean/VE/Norms/Tree.lean:241`), so on W1's route a document pairing an unknown predicate with an attitude node answers `array expected` in both orders, not the unknown predicate in one of them. The fixture now says so, and leaves soft's and P0's answers to the recording from `main` | 7.6 |
| RC-3 | The D15 fixture ("240 more author predicates") failed at D6b, since `lexAgrees` requires a lexicon entry for every author predicate, against section 5.2's claim that each earlier row keeps its answer. The fixture declares the 240 predicates in `E` and in the fixture lexicon, each with its quoted fallback wording | 5.2; 7; 7.5 |
| RC-4 | Between AT-1 and AT-5 the `wants` test existed in Lean and in Python, against the one-owner rule SR-3 requires; draft 2 only marked it open. The PLAN's own fallback is taken: the Python switch moves before the Lean check that calls the test. A new batch AT-1w, before AT-1, moves the test into Lean and deletes the Python copy (`_infinitive` and `_finite`, the finite form it checks against), `reports@0`'s Python English reading both forms through a new kind of the `reports` mode; AT-5 no longer touches the test. A batch of its own, because AT-1 with a relayed kind would exceed the PLAN's six hours per batch | 0; 1; 10 item 6; 12 |

Statements changed or added, for the re-review: none; `att_english_roundtrip`'s docstring names D14d.
Definitions changed or added: `lexPred`, `lexTerm`, `lexCovers` (new), `renderCheck` (gains D14d), `lexAgrees`
(docstring only). Diagnostics: D14d (new); the D15 fixture. Fixtures: C-d (new); the SR-6 fault-order fixture. Plan:
AT-1w (new), with the `reports` route kind of section 10 item 6. Every other statement and definition is draft 2's,
unchanged.

## 16. Draft 4: phase 1

Phase 1 ([docs/research/attitudes-phase1.md](../research/attitudes-phase1.md)) ran the pilot AT-0p and prepared E1
and E2 without running them (no model calls). Its results reach this spec only through the frozen table's inputs
and one admitted English row; no Lean statement, definition, diagnostic or fixture value changes, so nothing here
needs re-elaboration and the stub is not edited. The PLAN (draft 5, sections 4, 9 and 10) carries the protocol, the
results and the triggers.

| # | Change | From | Where |
|---|---|---|---|
| P1-1 | E1 and E2 are DEFERRED; `table` stays empty and reviewed; SR-8's first step waits on the DRI's authorisation and its confirmation of the protocol (G1–G6) | P1 3, 4 | status; 12 |
| P1-2 | The closure review's resolution is one rule: the weaker word of a derived entry whose item failed leaves `lowerBound`, with every pair and premise-3 entry naming it, until `Table.reviewed` holds; of several offending words the weakest (the last in `e1Words`) goes first, one per round, since another order can leave a different reviewed table (self-check: three violations remove "likely", then "quite likely"). The debate-round-3 items for entries derived without a direct item are empty by construction, since E1 asks every pair (earlier word first, G1) and E2 every word's premise-3 item (G3). `Table.reviewed` and its fixtures are unchanged | G1, G3, G4 | 2.1; 12 |
| P1-3 | "P, and X does not know that P" is admitted only if six E2 items reach 36 of 40: the three "Must P?" items and three "Does X know that P?" items | G5 | 3.1; 11 item 16; 12 |
| P1-4 | The stub's sha256 pin in phase 1's emitter, and what updating the stub must do with it | P1 3 (`8538355c`) | 13 |
| P1-5 | The status's step "the stub updated to draft 2" reads "to the current draft" (draft 3's Lean, which this draft keeps), as PLAN draft 4 already said | — | status |
| P1-6 | The predicate count names the count `MAX_PREDICATES` bounds: declared plus unspecified (norm-defaults 5.1, "filled"), 65 at the pinned run and 78 in AT-0p, **about** 85 with the intention terms; draft 3's 68 and about 88 were the readings route's size count, which adds its own three generated predicates | checker of PLAN draft 5 | 8 |

Measured context, not a change: AT-0p's A4 (P1 2) found that the untyped repair, with the case false and Claude
knowingly engaging in it, answers UNDECIDED in all seven pilot rules. In the typed profile the matching point is
F-AT1's M2 (`knows` true, the category false), where the frame fails factivity (section 7.1), and the layered route
refuses it with the pack's first failing label (PLAN AT-2). So the gap F-AT1's M2 covers is now measured on the
pilot, not only argued.

Statements changed or added, for the re-review: none. Definitions: none. Diagnostics: none. Fixtures: none.

## 17. AT-0's re-review: corrections RR-1 to RR-3

The bounded re-review of AT-0's changed statements (`manage-agents/attitudes-at0-review.final.md`, on
[docs/research/attitudes-at0-changed.md](../research/attitudes-at0-changed.md)) returned **FIX** with two B findings
and one C. Each is corrected as a class; nothing else changes. The stub carries every change and elaborates with
every `#guard` holding (that document's section 1).

| # | Finding | Correction | Where |
|---|---|---|---|
| RR-1 | (B) "Give the same guard" overstated the argument: composing `NegatedFactive`'s two candidates under "both P and …" gives `and P̂ (and P̂ (not K))` and `and P̂ (not K)`, equivalent formulas but two trees, so equivalence does not give one derivation under the all-derivations rule | The row is read whole: one construction, only when the first conjunct is the complement's clause with the same content and slot term, whose one tree is `assertedNotKnows c = and P̂ (not K)`. New: `assertedNotKnows_one_reading` (each admitted `knows` occurrence's row text answers `readGuard = .ok (assertedNotKnows c)` and `readGuardAll = [assertedNotKnows c]`), the definitions `slotTermIn`, `slotIn`, `assertedOf`, `assertedNotKnows`, and AT-5's renderer `renderAssertedNotKnows`. `P̂` is now `assertedOf` (a content is quantifier-free, so variable 0 is replaced directly; the old citation of `Formula.subst` was over `VE.Core.Formula`) | 0; 3.1; 3.4; 6.5; 7.1 (F-AT9); 7.5; 12 |
| RR-2 | (B) The admitted row's one reading was claimed to be carried by AT-5's acceptance fixtures, but section 7.6 had none for it, and F-AT9 and T9 evaluate a constructed guard without the reader | Section 7.6 gains the row's AT-5 fixtures, read by the English reader: the row's exact one reading alone, on a closed content and nested in "either … or"; and the refusal's boundary: another content, another slot term (either side), the conjuncts reversed, the row's shape under "either … or", the bare form and "unless". The stub records them (`readFixtures`, `readFixtures_hold`), with their documents and the computable checks | 3.1; 7.1; 7.5; 7.6; 12 |
| RR-3 | (C) "Seeds tried" counted every sublist of the atoms, while T4 checks only the seeds with no nonfactive knowing | Relabelled "candidate seeds enumerated"; the search also counts the seeds T4 checks (`seedsChecked`) | 9 |

Statements changed or added, for the re-review: `assertedNotKnows_one_reading` (new). Definitions: `slotTermIn`,
`slotIn`, `assertedOf`, `assertedNotKnows` (new); `renderAssertedNotKnows` (AT-5's, a stand-in in the stub).
Diagnostics: none. Fixtures: F-AT9 (now in section 7.1), RR-2's three documents and the ten AT-5 read fixtures.

## 18. Refresh (2026-10-28): the staleness review's edits

The staleness review of the plan and this spec against main `6d0a10526`
(`manage-agents/debates/refresh-attitudes-20261028/`: `TOPIC.md`, `astra.md`, `fable.md`, `result.txt`) converged
after round 2 on **REFRESH**. This draft makes the edits both reviewers' round-2 positions agree on, and no other
change. Where their round-2 texts differ (E3/AT-8 against purpose-explanation; WG-5's placement), both readings are
recorded and nothing is decided here (section 1; PLAN section 10 item 5).

| # | Change | Debate | Where |
|---|---|---|---|
| RF-1 | E1 and E2 done; `table` frozen, as the pinned stub carries it; status reconciled | Astra r1 1, r2 3; Fable r1 1 | status; 2.1; 12 |
| RF-2 | Stub `dea412eb` restored from `923f0a0ea`, pinned at `docs/spec/attitudes/SpecStubs_attitudes.lean`, merged-interface stand-ins replaced by imports, elaborated on main | Astra r1 1, r2 3; Fable r2 | 0; 13 |
| RF-3 | D5 answers QS-1's own text; D0 and D4 as AT0C recomputed them | Astra r1 1 | 5.2; 7 |
| RF-4 | PK-1 as built: `consts := []`, (owner, prefix) rows, `assemble U used`, `(packPremises L.packs "attitudes").map (·.2)`, `SupPacks`' lemmas | Astra r1 2, r2 1; Fable r1 3, r2 | 1; 2.9; 6.3; 6.4 |
| RF-5 | The double declaration of generated names resolved before insertion: one declaration, in `envAtt`; the pack a `constraint` pack with no names | Astra r1 2, r2 1; Fable r2 | 2.4; 2.9; 6.2; 7.3 |
| RF-6 | AT-2 carries PK-1's first-provider obligations, restated: environment (`envX_declFree`, `names_in_base`), expansion (none owed by a `constraint` pack), origins (`OriginsExact`, `packEntry`, `furtherEntries`), its own point check (`pointCheck`); PK-1's diagnostic placement and collision-witness exception | Astra r1 2, r2 1; Fable r2 | 2.9; 5.3; 6.2; 7.3; 7.6; 10 item 2 |
| RF-7 | The profile row broke `attitudes_row_composes`; the row restated to require `norm-defaults@0` and `norms@0`, searched over 512 lists; the route is a `VE.Compose.Route` | Astra r1 3, r2 2; Fable r2 | 2.9; 6.3; 7.3; 7.6 |
| RF-8 | One new kind through `layeredRows`; the duplicate status, conflict and report kinds removed | Astra r1 3, r2 2 | 1; 4; 6.3 |
| RF-9 | The hook on `normFields`, soft's `shared := false`, both admission paths | Astra r1 3; Fable r1 6 | 10 item 1 |
| RF-10 | AT-3b a Lean call site with a typed, bound relay, after SC-1b; rd-9 inventory rows | Astra r1 4; Fable r1 4 | 7.6; 10 item 3 |
| RF-11 | Owners and shared pieces: C14 (`VE.Reports.wantsPhrase?` in the new `VE.Attribution.Words`), C1 (`SourceWords.lean`), PS-NF, C17, D2, D9, purpose-explanation's D7; NEW marked | Astra r1 5, r2 4; Fable r1 5, r2 | 0; 1; 2.6; 3.4; 10 items 4, 6 |

**Statements and definitions changed, for AT-0's re-review** (with RR-1 to RR-3). Changed and elaborated in the
refreshed stub: `table` (the frozen table, as AT0C already ran it); `attitudesPack` (`consts := []`);
`attitudes_status_sound` (`(packPremises L.packs "attitudes").map (·.2)`); `attitudes_row_composes`
(`r : VE.Compose.Route`); `renderCheck` (`VE.Reports.wantsPhrase?`, a namespace only). **Restated** before AT-2
(RF-5 to RF-7; draft 5's first commit had marked them *to restate*): `attitudesPack` (a `constraint` pack,
`decls := []`, origins for its labels only); `attitudesRow` (`requires := ["norm-defaults@0", "norms@0"]`); new
definitions `pointCheck` and, as AT-2's additions to `Packs.lean` in the PK-1 stub's text, `OriginsExact`,
`packEntry`, `furtherEntries`; new statements `attitudesPack_declares_nothing`, `names_in_base`, `envX_declFree`,
`assemble_attitudes`, `attitudesPack_originsExact`, `pointCheck_absent`, `pointCheck_sound`; `empty_relations_frame`'s
docstring (no longer the pack's PK-1 expansion step). `envAtt_extends`, `toNorms_wellFormed`, `frame_typed_fill` and
`frame_unsaidFree` keep their text: the one declaration is the one they already read, and PK-1's obligation-2
environment is `envAt (fill U) 0`. No `ExpandsOn` is stated for the pack (section 2.9). Diagnostics: D0, D4, D5
(RF-3); section 5.3's text (RF-6), now computed (`pointCheck` at RM2). Fixtures: section 7.3's refresh table (new,
computed); section 7.6's AT-2 and AT-3a lists; AT-3b's gains the inventory rows. Every other statement and
definition is draft 4's with RR-1 to RR-3, unchanged.

**Consequence for PK-1's text (for its owner, not edited here).** premise-packs.md 3 and 5 say `ExpandsOn` and
`expandBy` "land with the first provider that proves them (AT-2)". With the attitudes pack a `constraint` pack,
AT-2 proves neither, so they land with the first provider whose pack declares names (events' `date__` constants in
ET-4 is the one named so far); `OriginsExact`, `packEntry` and `furtherEntries` still land in AT-2.

**The refreshed stub's run.** `docs/spec/attitudes/SpecStubs_attitudes.lean`, sha256
`3575da56047dc0343cb1c8658e291af8b16d7e5bbb1a18ef572b36a8edfa5c1f`, elaborated against main `6d0a10526`: exit 0,
no error, every `#guard` holding, 8 min 57 s, at most 1.5 GB. Its `#eval` output is the first refresh run's (stub
`c2472f73…`, 216 lines, itself the pinned run's `docs/research/evidence/attitudes/at0-stub-run.txt` at `923f0a0ea`
except the D5 row, which answers `ResourceLimit: At most 64 order pairs`) line for line, followed by 41 new lines:
section 7.3's refresh fixtures. So every fixture value and the section 9 search's counts (477 documents, no
counterexample) are unchanged on the refreshed definitions, and the restated statements' fixtures hold. The output
is `docs/spec/attitudes/stub-run-20261028.txt`.

## 19. Draft 6: the statement spec reconciled with PLAN draft 6 and with main

Draft 6 is AT-0's reconciliation (backlog row `at-0`, `reviews/dri-decisions-20261102-attitudes-scope.md` items 1, 3).
Plans are frozen until 12 November, so it adds no design and edits no plan. It changes the stub only where main or
syn2code-attitudes-4 requires it.

| # | Change | From | Where |
|---|---|---|---|
| DR-1 | The decider token in the stub is `unstated`: the field's comment and the fixtures' `decidedBy`. No output line changes | edits-attitudes item 4; syn2code-attitudes-4; C2 | stub; 13 |
| DR-2 | `attitudesPack` sets `conditions := []` | main's `Pack` field (profile-composition 1.9) | 2.9 |
| DR-3 | `attitudesRow` in main's form: `slot := "pack"`, `interface := .pack "attitudes"`, reason text only. The stub still carried draft 5's slot and prefixed text | edits-attitudes items 2, 3; PC-3 | 2.9; 7.3; 7.6 |
| DR-4 | `attitudes_row_composes`'s docstring says what the statement says; "runs on a chain that carries its pack" is unsupported on 11 of the 23 admitted lists. The statement is unchanged | the wide search | 6.3; stub |
| DR-5 | The row's search widened to 4,096 lists on main's table, and its computed answers recorded, the unreachable `reports@0` text included | main's table | 2.9; 7.3; 7.6 |
| DR-6 | The D2 ruling, the purposes boundary, AT-8's place and "possible" written as the plan rules them; `SourceWords.lean` is on main | edits-attitudes items 5–9, 11; DEC 13 | 1; 2.1 |
| DR-7 | The at3a-order conditions and scope's `own` pinned at the hook, with their fixtures | at3a-order item 1; edits-attitudes item 10; scope.md 1.4 | 7.3; 7.6; 10 item 1 |
| DR-8 | Section 9 gives the rerun's result; it still said "not yet run" and showed draft 1's counts | stub run | 9 |
| DR-9 | Citations moved to `9ba2140e2`: `Dispatch.lean:889–899`, `UnspecifiedWire.lean:39–42`, `Packs.lean:67`, `Readings/Wire.lean:132`. The other cited Lean files are unchanged from `6d0a10526` | main | 2.9; 6.3; 10 item 1 |
| DR-10 | Stale wording: section 5.1's `attitudes-*` kinds, section 7.5's restated statements, sections 12 and 13 | reading | 5.1; 7.5; 12; 13 |
| DR-11 | Draft 8 (at-0-finish): `decodeLayeredAtt`, `attitudesOn`, `withAttitudesPack`, `decodeLayeredAtt_off`, `decodeLayeredAtt_pack`; `hp` on `attitudes_elaborate_acceptance`, its `hL` through the wrapper; `decodeAttDoc` and `encodeElaboration` qualified in 6.3; `pointCheck_absent` and `pointCheck_sound` by plain names under a file comment; 5.1 limited to layered lists; the longest name; OPEN-4 ruled, OPEN-9 reworded, OPEN-10 and OPEN-11 new; the statement review's FIX-1 to FIX-4 (`manage-agents/at-0-finish-review.final.md`); stub rerun on main `ea108ea4e`, sha256 `b9f84e5a` | `reviews/dri-decisions-20261102-at-0.md` items 1-4 (SIGNED); `debates/at-0/result.txt`'s agreed edits | header; 2.9; 4; 5.1; 6.2; 6.3; 7.3; 7.5; 7.6; 10; 11; 12; 13; 19; stub |

**The statement review's FIX** (`manage-agents/debates/at-0/`, rounds 1–2; two Opus seats, since Codex was capped). One
seat ended CONVERGED on the joint position; the other's last round left two placement points open, and the first
seat then conceded both. These are its edits, and nothing else.

| # | Edit | Where |
|---|---|---|
| FR-1 | `attitudes_elaborate_acceptance` was false on main: `layeredCase` answers `none` at a kind outside today's four. It names `layeredKindCase` and sits in `lean/VE/Defaults/Route.lean`; AT-3a widens `runOtherCase`'s test and restates `layeredKindCase_other` with `ha` | 4; 6.3; 11 item 17; stub |
| FR-2 | `frameLabels_nodup` and `assemble_attitudes` were false for a reviewed table whose words hold `:`: two frame pairs could share a label. `checkNames` refuses `:` in a generated name; the frozen table cannot fire it | 2.6; 5.2; stub |
| FR-3 | The off-profile text is `decodeAttDoc`'s alone; the kind answers `array expected` or `dispatch`'s text | 5.1; 7.6 |
| FR-4 | The row's count is 11 of 23, not 7; the `normDefaults` lists have no layered route; `clauses` and `judgments@0` are added to OPEN-2; `scope.md 1.4` | 2.9; 19; 10 item 1; stub |
| FR-5 | `keyOrigin` and `labelOrigin` are in section 0's stand-in list | 0 |
| FR-6 | `pointCheck`, `pointCheck_absent` and `pointCheck_sound` move to `VE.NormDefaults.Packs`, bodies unchanged: in `Attitudes/Route.lean` the call from `replayStatusX` is an import cycle | 2.9; 6.2; 7.3; 10 item 2; 11 item 18; stub |

**Statements and definitions changed, for the review.** Definitions: `attitudesPack`, `attitudesRow`, `checkNames`,
`pointCheck` (moved). Statements: `attitudes_elaborate_acceptance`, `layeredKindCase_other` (restated from main),
`pointCheck_absent` and `pointCheck_sound` (moved); `attitudes_row_composes` changes its docstring only. Diagnostics:
the `:` refusal; section 5.1's text. Fixtures: section 7.3's draft 6 table; section 7.6's off-profile fixture.
Every other declaration is section 18's. Each Lean declaration of this spec was compared with the stub's by a script
on draft 6: they agree, apart from comments, the stub's `_`-prefixed binders and its open `Json`.

**The stub's run.** `docs/spec/attitudes/SpecStubs_attitudes.lean`, sha256 `068912b38b4a41c7a7774e3348c153a7b8538ed7cbfe2f699b79ba26189ffd7c`, against main `9ba2140e2`: rc
0, no error, no warning, no `sorry`, every `#guard` holding, 531 s. Its output is draft 5's 257 lines unchanged and in
order, plus 18 lines for section 7.3's draft 6 table; so every fixture value and the section 9 counts hold on current
main. Elaborating a statement is not evidence that it holds: only AT-1 to AT-5's proofs establish them.

**OPEN lines.** Each is something the plan leaves open or a conflict between frozen texts. None is decided here and
none gates AT-1w.

- **OPEN-1 (AT-5; english-lean).** `SourceWordRow` has no form for section 3.4's rows. `.refuse` holds a code, advice
  and one rewrite; `.readings` holds candidates with no code; section 3.4 needs a code, a category, at least two
  rewrites and candidate formulas together (`Refusal`, SR-5). The plan says rows are added and "the row type is fixed
  there", and gives no mapping.
- **OPEN-2 (AT-3a; DRI or PC-4).** The row as the plan writes it admits 11 of the 23 wide lists on routes where the
  frame does not apply (section 2.9): `normDefaults` 4 (no layered route, so no frame), `discourse` 6 and `alternatives`
  1, for which PLAN 3.6 lists no hook and no pack. Outside the twelve profiles it also admits `right-clauses@0` (`ok
  clauses`, computed) and `["attitudes@0", "documents@1", "judgments@0", "norm-defaults@0", "norms@0",
  "relational-fol@0"]` (`ok normDefaults`, computed), which profile-composition.md says stays refused until PC-1b. The
  plan does not say whether the row refuses these or what those routes answer; PC-7a is the planned attitudes ×
  discourse batch.
- **OPEN-3 (PC-1b; profile-composition).** PC-1b's `withAttitudeContents` reads "the keys of the attitudes pack the
  route assembled", one per mode and content. This pack holds no keys, a key here is (mode, holder sort, slot sort,
  content), and `LayeredU` does not carry an `AttDoc`. The pairs exist as `(keys A).map (fun k => (name A k, k.content))`
  and in `attitudes-elaborate`'s answer; no text says how the route reaches them.
- **OPEN-4 (RULED, DRI 2026-11-02 at-0 item 3, SIGNED).** PLAN section 5 and its AT-3a row, from edit 12, read "PC-6
  before AT-3a". The signed at3a-order ruling, profile-composition 3.6 and backlog row `at-3a` let AT-3a land first. The
  signed at3a-order ruling governs, and this spec follows it; the plan's text waits for the freeze to lift.
- **OPEN-5 (sc-2b; scope).** PLAN AT-3a says the decoder "accepts scope's `own` placeholder at the content position";
  merged scope.md substitutes before decoding, so section 10 item 1 reads this as no decoder change. Whether it asks
  more is not stated. scope.md's example node (holder `var 0`, no slot) answers D8, and with the holder corrected D14
  (section 7.3), so sc-2b's reguard needs a slot, which that example does not show.
- **OPEN-6 (a later statement review).** "possible" would be a ninth candidate, and `Table.reviewed` refuses more than
  eight. The plan does not say whether the bound or `e1Words` changes. Nothing changes until its items run.
- **OPEN-7 (AT-3a; hedges-generics H-4).** PLAN 3.12 says AT-3a lists the hedge sort and atoms "in `envAtt`'s pattern",
  but gives no statement for them, and `AttDoc` and `envAtt` have no hedge field. This spec carries no hedge Lean, and
  hedged calc, count and causal units stay refused. AT-3a builds nothing for them until a reviewed statement exists.
- **OPEN-8 (the merge of this branch).** PLAN section 9 says the refreshed AT-0 restores `docs/research/evidence/attitudes/`
  and `research/attitudes/` "where it merges". They are not on this branch, so `experiments.py`'s stub pin and
  self-check are not updated. Spec section 2.1 cites both. Whoever merges these docs restores them and updates the pin
  in that commit.
- **OPEN-9 (AT-3a).** `names_in_base`, `frame_typed_fill` and `frame_unsaidFree` assume `toU A unspec = some U`, but
  `L.U` is `soften`'s (`Layered.lean:103`) and `AttDoc` has no soft fields. With `hp`, no statement is false, but nothing
  types the frame on a soft document with defaults, and nothing relates `A` to `L.U` beyond `hd` and `hL` decoding the
  same case. PLAN draft 6 dropped draft 5's registration line; where the pack is assembled is ruled (DRI at-0 item 1:
  `decodeLayeredAtt`, not `decodeSoftU` or `decodeRightsU`). A case with `attitudes@0` and no block answers `decodeAttDoc`'s
  text.
- **OPEN-10 (AT-3a; DRI).** The wrapper reaches only what `runLayered` dispatches over its `L`: the status, conflict,
  report and elaborate kinds. `softCase`'s `norm-defaults-certificate` (`replayLayeredEntailment`) and `admission`
  (`admitDocumentX`) call `decodeSoftU` directly, before `runLayered` (`Run.lean:119–127`), and the `defaults-*` rows
  decode again through `viewOf` (`Defaults/Wire.lean:120`, `decodeLayered`), so none of these reads the frame. They
  use fewer premises: a certificate accepted there also holds under the frame, and one that needs a frame premise
  fails; but a model accepted there need not satisfy the frame, so `defaults-coherence`'s COLLISION (`collisionCheck`
  over `v.R`, `Defaults/Wire.lean:400`) and the countermodels of `needs` and `defaults-model` (`xModelOk` over `L.X`,
  `:252`, `:489`) can rest on a point the frame excludes; section 5.3's collision witness contains the frame only if
  these rows read the wrapper's list. Item 1 does not say whether they should read the pack; this spec changes none
  of them.
- **OPEN-11 (AT-3a; DRI).** F-AT1's wire cases need `decodeLayered` to decode a case with `attitudes@0` and the block,
  but soft's envelope and profile checks refuse both (`SoftNorms/Phases.lean:60–61`, `:197`; section 6.3), and neither
  the row nor section 10 item 1's guard hook reaches them. The at3a-order ruling's condition (a) limits AT-3a's edit to
  the soft norm decoder to passing the `attitudes@0` switch and keeping `shared := false`. No text says whether admitting
  the block and the profile there, with `attitudes@0` on, is inside that condition. Until it is ruled, the wrapper never
  assembles the pack on a real case.

## 20. Draft 7 (at-rev, DRI 2026-11-02 fp-attitudes item 1): the statements AT-R1 changes

Applied from `manage-agents/reviews/dri-decisions-20261102-fp-attitudes.md` item 1 (SIGNED) and nothing else; the
pilot's record is `manage-agents/reviews/fidelity-pilot-20261102/attitudes/`. AT-R2 changes sections 1 and 4 in
prose only; AT-R3 and AT-R4 change the plan only (PLAN 3.7, E3, AT-8). The stub elaborates on main `9ba2140e2`
(`spec-stub-check.sh`, lean rc 0, errors 0, warnings 0, sorry 0, every `#guard` holds; its `#eval` output is draft
6's, line for line, plus C-e's).

| Statement | Change | Batch | Sections |
|---|---|---|---|
| `AttDoc` | new field `parts : List Cond := []`, the reading-set parts (PC-11's `attitude` case) | AT-1 | 2.2 |
| `partsOf` (new), `keys` | keys over `condsOf A ++ partsOf A`: a part's key follows the rules' keys; unchanged on a document without parts | AT-1 | 2.3 |
| `partClaim` (new) | a part's claim, `(AFormula.att c).toFormula A []`, PC-11's `attitude φ` | AT-1 (names from AT-2's `envAtt`) | 2.5 |
| `renderCheck`, `checkCond` | a `part` flag, default `false`; with it, D14c also words a closed `wants` of one unary base predicate on a constant; without it, as draft 6 | AT-1 | 2.6, 3.1, 5.2 |
| `checkParts` (new), `checkAtt` | the parts are checked after the rules' conditions, before the names | AT-1 | 2.6 |
| `att_conservative_doc` | the hypothesis `hp : A.parts = []` is added (without it the statement is false for a document whose only attitude is a part) | AT-1 | 6.1 |
| `att_english_roundtrip`, `renderCond_injective` | over `condsOf A ++ partsOf A` | AT-5 | 6.5 |
| fixture C-e | u0035.s12's shape: the part admitted, the node in a guard and the compound part refused at D14c | AT-1 | 7.1, 7.4, 7.5 |
| `keyOrigin` (opaque in the stub) | its prose: a part's key has as origin its set, reading and part (PC's `candidateAt` place), handed by PC-11's decoder (review fix, B3) | AT-2 (path fixed by PC-11) | 2.9 |

Unchanged: every other statement of AT-1w, AT-1, AT-2 and AT-3a, every diagnostic text, the frame. AT-2's
statements quantify over `keys A` and so cover a part's key without a change in their text. AT-3a's node decoder is
unchanged: PC-11 calls it on a part (section 4); filling `AttDoc.parts` from PC-11's decoder is a request row in the
PLAN's section 3.11, since PC-11 is profile-composition's batch.
