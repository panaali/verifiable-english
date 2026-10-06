# English in Lean, stage E2: Lean decides English admission (plan)

**Status:** plan, draft 3, 2026-10-06, branch `design/english-lean-e2`. Draft 1 was the pointer plan at
`929e72c1`, draft 2 the plan at `d1adcfc0`. Draft 3 applies the statement review of the spec (section 2). Item 1 is
track E2 of `docs/LEAN-FIRST-PLAN.md` (branch `design/lean-first`, sections 5.2 and 6.3) together with the E2 items
that english-lean S3 left open: stages E2.0 to E2.4 of `english-lean-S3-PLAN.md` draft 3
(the **S3 plan**) and the G3 evidence that the S3 integration report lists as open. This plan builds on the S3
integration, branch `english-lean-s3/integrate` at `531f2789` (the **S3 build**). That build holds the profile
reader, `admit`, `obligations` and `firstChecked` with their proofs, and `english.admission` there is still
`authority: python`. The S3 build is not yet on `main`: the S3 plan, `english-lean-s3.md` (the **S3 spec**) and
`english-lean-s3-report.md` (the **S3 report**) are cited from that branch and reach `main` when S3 merges. The
item-1 statement spec is [english-lean-e2.md](english-lean-e2.md), draft 2 (the **spec**).

**Nothing was built for this draft.** The spec's statements were elaborated in a scratch stub against the S3
build, and every value marked *computed* in its section 8 was computed by that stub. The stub ports Python's
vocabulary policy and checks it against Python's recorded lexicon identities on the corpus environments (spec
section 12): draft 2's text reproduces all 22. Python itself was not run, in either draft. Every Python outcome
named here was read from the source, recovered from an identity Python recorded, or run by the review. A script
beside the stub prints Python's outcome for each new fixture; running it is the spec's obligation py1.

**Review provenance.** The debate directory `manage-agents/debates/design-english-lean-e2/` holds a copy of the
review of the base plan (`english-lean-PLAN.md`): rounds of 2026-10-03, converged after round 3 on Fable's eight
edits of round 3 with Astra's three qualifications, Astra's text governing where the two differ. It is the same
text as `design-english-lean/` and `design-english-lean-s3/`, and the S2 and S3 plans applied the same joint
position. No round was held on the E2 pointer plan itself. This draft applies that joint position as it bears on
E2 (section 2), together with the pointer plan and the DRI's rulings (section 3). Where an edit and a DRI ruling
differ, the ruling governs.

The statement review of draft 1 of the spec and draft 2 of this plan is in
`manage-agents/debates/english-lean-e2-spec/`. It converged after round 3 on **FIX**: Fable's six items of round 2,
which Astra adopted, with Fable's four round-3 precisions. Astra's round 3 was written beside Fable's and did not
see them. Astra had reached one independently: an overlay refusal has its own code, of class `VEError`. The other
three only narrow what was agreed: constants are never refused, the stricter stage gates, and one bounded round on
the new definitions. Astra had said that no further round is needed. On that point the plan follows Fable, as the
DRI's rule for a point a review leaves open says. Draft 2 of the spec and this draft
apply all six items and change nothing else (section 2, "The statement review").

## 0. Decision in brief

E2 makes Lean the authority for `english.admission`. After the flip, Python sends the environment, the overlay, the
lexicon and the text, and relays Lean's answer, Lean's code and Lean's text. Python's hand parser and the Lark audit
run only as a logged comparator, and the next stage deletes them. Eight things are decided here.

1. **One gate.** E2 ends at GE2 (section 1). GE2 is the lean-first gate together with the G3 comparisons that S3
   left open. Authority moves only at GE2, and there is no calendar window (DRI amendment P1).
2. **V6 is checked beside `Lexicon.valid`, not inside it.** This changes where S3 D14 puts V6 but not what V6
   requires. V1 to V5 stay what one reading depends on. V6 is Python's vocabulary policy: a check
   `Lexicon.policyOk E O L` on the request's own environment, overlay and lexicon. Every mode that receives a
   producer's lexicon runs it (`english.read`, `english.check`, `english.grammar`, `senses.read`), and no mode runs
   it on a Lean-computed projection. The reason is computed (spec lx30): the senses layer declares glossed wordings
   such as `{0} is funny (meaning strange)` and calls `Lexicon.failures` on its projection. Under V6 every wording of
   the joke fixture's projection falls back to its quoted form, so V6 inside `valid` would make `project` fail on
   every document with a word of two senses. Kept outside, V6 leaves every S2, S3 and senses statement word for word
   (spec D2).
3. **V6 is stated by its tables, as Python's selection.** Lean ports the choice that `EnglishVocabulary` makes for
   each predicate, sort and constant (spec 2.3). A lexicon passes V6 when each selection is Python's choice or the
   quoted fallback, and each negative is Python's. This covers the three parts of S3 2.9 and four gaps the S3 text did
   not name, each a lexicon that V1 to V5 accept and Python's producer never makes (computed, spec lx25 to lx28):
   - a mechanical wording that Python refuses: `{0} likes {1}`, `{0} is holds`;
   - a negative of a ternary predicate;
   - a noun with a reserved word: `every item`;
   - a constant spelled with a reserved word: `hence`.

   Where Python enumerates the environment's symbols, the port enumerates the declared ones, as Python's
   `_ProfilePredicates` does; the symbols that profile blocks generate are looked up but own no word (spec 2.3).
   Draft 1 of the spec enumerated both, and so refused Python's own choice of `{0} is fully avoidable` under
   `alternatives@0` (spec lx32). On the suggested path the port follows Python's `re.I` (spec lx31c).
   **Measured:** draft 2's text reproduces Python's `lexicon_id` on all 22 use-case rows of
   `conformance/english-lean/lexicon-report.json`, all four overlay rows included. For the four rows that Lean's
   boundary refuses today, that holds once E2.0 decodes them (decision 5).
4. **Python still proposes the lexicon.** The producer stays untrusted, and V6 checks every lexicon it proposes.
   Because the port computes Python's choice, the next stage can make Lean the producer and delete the selection logic
   of `EnglishVocabulary`. This plan does not do that: every renderer reads the Python selection today
   (question 3).
5. **Two defects of the S3 build block the flip, and E2.0 fixes both** (both computed, spec ev14 and ev15).
   - *The overlay identity.* With an overlay, Python's lexicon names the display environment (the overlay merged
     in), but Lean's `decodeLexicon` compares it with the submitted environment's identity. Lean therefore refuses
     every request that carries an overlay: on the birthright use case with its overlay, `english.read` returns
     `InvalidInput: the lexicon names another environment`. The four `-reviewed` corpus configurations are such
     requests. The fix binds the lexicon to the display environment's identity.
   - *The boundary.* Lean's English boundary refuses 4 of the 22 corpus use-case environments that Python's reader
     admits: two with `norm-defaults@0`, one with `soft-norms@0`, and one with W6 units outside `risk@0`
     (`usecases/eligibility`). E2.0 gives these the treatment S3 gave `risk@0` and `alternatives@0`: the
     declarations are validated as submitted, a typing view drops what the typed check does not read, and the
     identity is computed over the submitted environment. A fourth part is needed for `norm-defaults@0`:
     `Env.decode` reads each modal form through the frozen `decodeRegulated`, which refuses `default: unspecified`,
     so it reads the entry with `unspecified` as the placeholder `deny`, as `NormDefaults.Wire` does; no frozen
     decoder is edited (spec D7, md1 to md5). E2.0 also lists the modal forms before the role wordings in
     `Env.decode`, so that a predicate that is both gets Python's modal form (spec D18).
6. **Lean's codes, classes and texts are the ones shown** (LEAN-FIRST DRI answer 3). Every response that is not
   `one` carries the Python class the relay raises, so the relay's own class tables go. `NotOneSentence` has the
   class `SyntaxError`. The texts of `ConclusionWithoutPremise` and `ConclusionNotDerived` come from Lean, the
   second precomputed per obligation with a slot for the prover's status, which the relay fills verbatim. Each mode
   answers with the first refusal in the order boundary, overlay check, V6, V1 to V5. `english.grammar` and
   `english.check` answer `invalidGrammar` for a refused vocabulary, so `{}` from `english.check` only means that
   no candidate reads back. The advice table of S3 4.3 is completed: the two `allows` messages that S3 left as
   obligations are rows (computed, spec ad15 to ad17).
7. **The senses layer keeps working through the relay** (DRI ruling 7). `senses.read` runs V6 on the request's own
   environment and lexicon before it projects, and the projection is never checked against V6. `Lexicon`, its wire
   form and the preimage of each of the six identities are unchanged. Every new field of `Env` has a default.
8. **Python's overlay refusals move to Lean.** For an overlay, Python's producer raises `VEError` at three sites:
   a duplicate wording, a reused risk wording, and a final comparison that refuses an entry it would not select as
   written (`english.py:373–375`, `:442–443`, `:511–517`). V6 alone cannot see these: it accepts the same lexicon
   with the entry on its fallback. Lean's overlay check states the three sites in Python's order, as O1 to O3, and
   answers `InvalidOverlay`, of class `VEError`; a constant entry is never refused (spec D17, 2.3, 8.11). On the
   admission path the producer is built with the three refusals off; every other caller keeps them. The consent
   gate and the rest of `display_environment` stay in Python.

## 1. Item 1: stage E2

| # | Content | Owner | Done when |
|---|---|---|---|
| E2.0 | **Service and boundary.** `english.read`, `english.grammar` and `english.check` become modes of `ve_service`, each pinned by an `rfl` theorem, with the response shapes of spec 4.4, `InvalidOverlay` and the translation mode's `NotOneSentence` included. Each mode answers in the order of spec 2.5: boundary, overlay check (wired in at E2.2, once E2.1 has built it), V6, V1 to V5; `english.grammar` and `english.check` run the grammar guard (`grammarFault`) and answer `invalidGrammar` for a refused vocabulary. `ResponseShape`'s `runMode_fits` is extended to the three modes. The prepared grammar is cached by `environment_id`, `overlay_digest` and `lexicon_id` (spec 2.7). The lexicon is bound to the display environment's identity (ev15). The boundary admits `norm-defaults@0`, `soft-norms@0` and the W6 units outside `risk@0` (ev14), with the fourth part, `placeholderEntry`, for the modal forms under `norm-defaults@0` (spec D7). `Env.decode` lists the modal forms first (spec D18). `ve_english_route` is deleted with its transport | Lean implementer | spec ev2 to ev4d, ev14, ev15, md1 to md5, gg1, gg2, cn19; the latency rows of GE2 measured on the service |
| E2.1 | **V6 and the overlay check.** `Policy.lean`: Python's selection as data and functions (spec 2.3, 5.2), with the declared-only enumeration and `re.I` on the suggested path; `Lexicon.policyFailures` and `Lexicon.policyOk`; the overlay check `overlayCheck`, O1 to O3. The new fields `SortDecl.plural`, `PredDecl.suggested`, `AltBlock.optional` and the `generated` flags, all with defaults. The **port parity harness**: on every corpus environment of the lexicon report and on the mutation set of spec 2.10, generated names included, Lean's choice equals Python's `EnglishVocabulary` symbol by symbol. The **overlay parity harness**: on every corpus overlay and every overlay mutant, Python's raise or no raise, and its site, equal `overlayCheck`'s. A difference is a port defect or a signed row of `DELTA.md` | Lean and Python implementers | spec lx15 to lx33, ov1 to ov10, ovc and pt1; parity on every corpus environment and overlay, mutants included; the bounded statement review of the port's tables (spec 10, items 1 to 6 and 14 to 16) has passed |
| E2.2 | **Admission.** `admitRequest`, `translateRequest`, `grammarFault`, `lexiconFailure`, `checkRequest` and `sensesRequest`, and `Overlay.decode` (spec 5.3). The modes run `overlayCheck` in the order of spec 2.5. The class table, the texts of 4.2 (the `unproved` text with its status slot) and the advice table of 4.3, all exported by `english.grammar`. `EFormula.decode`, for `english.check`. The statements of spec 5.5 | Lean implementer | spec cn10 to cn19, ad1 to ad19, tg1, tg2, lx24′, ev17; the statements of 5.5 proved; `lean/audit.py` clean |
| E2.3 | **The flip and the relay.** In the assurance manifest `english.admission` gets `authority: lean` and `target: lean` and leaves `dispatch.SHADOW_ONLY`. `parse_english`, `parse_english_with_metadata` and `parse_english_argument` relay `english.read`, with the producer built with its three overlay refusals off. The marked conclusions go to the entailment operation one obligation at a time, a refusal raising Lean's `unproved` text with the prover's status. The renderer's candidates go through `english.check`, whose `invalidGrammar` is raised with its class. Records carry claim C2 with the six identities, and C5 when obligations were proved. The comparator runs as spec 2.8 states | Python implementer | gate GE2; spec rl1 to rl11 |
| E2.4 | **Deletions.** The deletion ledger of spec 2.9: every Python decision site of formula-level admission is mapped to the Lean check that now owns it, removed from the admission path and kept as comparator, or kept for E3 with its caller named. The producer's three overlay refusals are owned by Lean and off on the admission path; `display_environment` and its consent gate are kept. The test-only references `conformance/english_lean_{engine,lexer,lexicon}.py` are deleted once nothing compares against them | Python implementer | `tools/relay_lint.py` passes on the admission path of `ve/english.py`; the ledger is signed |
| E2.5 | **Evidence.** The G3 harness that S3.5 owed and that the S3 report lists as open: the comparison at the dispatched boundary on the sealed corpus of every profile, the reverse corpus, the lexicon mutation replay with V6 lexicons, the three-way differential on the 57,765 core texts, the use-case documents and the pilots, the readability items. Then GE2's corpus A/B (spec 2.10) | Python implementer | the report `docs/spec/english-lean-e2-report.md` and `docs/lean-first/e2/DELTA.md`, every difference dispositioned |

**Gate GE2** (LEAN-FIRST 5.1, the pointer plan and the converged edits). All of the following hold at the batch head.

1. **Suite.** The full suite passes, with test changes limited to the listed wording and order changes.
2. **G3 comparisons, under Python authority before the flip.** On every sealed corpus text of every profile, Lean
   and Python agree at the dispatched boundary under the tree correspondence of S3 2.11 on:
   - the verdict (zero, one or many);
   - the formulas in wire form;
   - the canonical strict text;
   - the conclusion marks;
   - the witness multiplicity.

   Three further checks hold:
   - *Reverse corpus.* Every text that Lean accepts on the reverse corpus is accepted by Python with the same
     formulas, or is dispositioned under SEMANTICS-MIGRATION-PLAN 2.3. The reverse corpus is sampled from the
     `english.grammar` export of every corpus lexicon, with spacing and word-split mutants.
   - *Lexicon mutation replay.* Under every mutation, a corpus text either changes no formula or loses its reading
     because V1 to V6 refuse the mutant.
   - *Volume and coverage.* Fourteen fresh date seeds of the generated streams run at once, and every lexical family
     and every fixed rule of every profile occurs in at least one compared text.
3. **Corpus A/B.** Between the base commit and the batch head, over the 85,000 English pairs, the 12,750 audit
   texts, the 850 documents, the mixed and natural-view streams, every use-case document and harness with its answer
   key, and every historical pilot document, every result is identical or listed in `DELTA.md` as `wording`,
   `order`, `verdict` or `availability`. Each `verdict` or `availability` row is signed by the DRI. The comparator is
   on throughout, and no difference is undispositioned.
4. **Readability items.** Each item of the readability evaluation keeps its verdict and keeps or improves its
   message. A message improves when Lean's answer adds advice or a `wording` row replaces Python's text.
5. **V6 and overlay parity.** The port equals Python's selection on every corpus environment, and the overlay check
   equals Python's raise or no raise on every corpus overlay (E2.1).
6. **Availability.** Every corpus environment and every overlay that Python's reader admits is admitted by
   `english.read` with Python's identities (ev14, ev15).
7. **Senses.** The senses suite and its G-S gates pass through the relay unchanged.
8. **Deletion ledger.** The ledger of E2.4 is signed, and `tools/relay_lint.py` passes.
9. **Latency, on the service.** The base plan's budgets hold:

   | Measure | Budget |
   |---|---|
   | a corpus sentence, p95 | at most 20 ms |
   | a 150-token sentence | at most 50 ms |
   | the BlueDot document | at most 1 s |
   | grammar instantiation, cached thereafter | at most 100 ms |
   | the generated modules, `lake build` | at most 60 s |
   | `policyOk` on a 256-predicate environment | inside the instantiation budget |

   A 300-token sentence must also run inside the work budget, with its latency reported (DRI ruling 5). Each budget
   is met, or its revision is reviewed before the flip (G1a is a pass gate).

**Known `DELTA.md` rows** (the spec lists each):

- `wording`:
  - Lean's texts for every code, the three `InvalidOverlay` texts included;
  - the `unproved` text, which now carries the prover's status from `parse_english_argument` too;
  - the advice table, which is wider than Python's hints;
  - the two hints S3 lost;
  - the class of `RelativeForm`, always `SyntaxError`;
  - the class of `IllTyped`, taken from the typed check's message;
  - the overlay entry named when two entries fail at one site, which follows Lean's key order.
- `order`:
  - S2's F3;
  - S3's or38 class.
- `availability`, each signed:
  - texts that Python's 30 s Earley wall-clock limit refused and that Lean now decides;
  - any corpus environment that V6 refuses while Python accepted it, expected none;
  - any corpus overlay that the overlay check refuses while Python admitted it, expected none (none of the four
    today, spec ovc).

**Not in this stage:**

- deleting the comparator, which the next stage does (pointer plan);
- statement-layer English (E3), and with it the `EnglishParser` class, which `norm_english.py` and
  `norm_defaults_english.py` construct;
- Lean as the producer of the lexicon (question 3);
- `rights@0` wordings (S3 Q5);
- the static tier;
- a Lean renderer.

**Order.**

0. No stage builds on draft 1 of the spec. Before any stage starts, both reviewers check draft 2 of the spec in one
   bounded round: the new definitions (the overlay check, `placeholderEntry`, the two guards, `lexiconFailure`), the
   order of spec 2.5, and that each new fixture's expectation was computed, by Python for selections and raises
   (spec py1, run first) and by the stub for Lean. Nothing else reopens. The stage gates of the review then hold,
   each satisfied by draft 2: E2.0 needs the boundary and the guards and responses (review items 3 and 4); E2.1 the
   enumeration, the overlay check and `unaryPhrase` (items 1, 2 and 5); E2.2 the overlay check, the guards and
   responses, and the claims and texts (items 2, 4 and 6).
1. E2.0's two boundary fixes come first: without them, 8 of the 22 use-case rows of the lexicon report cannot be
   compared at all (the 4 environments the boundary refuses and the 4 overlay rows whose lexicon Lean refuses).
2. E2.5's G3 harness runs under Python authority in parallel with E2.1 and E2.2. E2.1 starts with the two parity
   harnesses, then the port. The bounded review of the port's tables comes before the flip.
3. E2.3 follows at GE2, then E2.4.

Effort: one lean-first batch (2 to 6 hours) for each of E2.0 to E2.4, and two for E2.5's corpus runs.

## 2. Converged edits applied

The joint position of the base-plan review (section "Review provenance"), as it bears on E2.

| # | Converged edit | Where applied in this stage |
|---|---|---|
| 1 | **Size.** No fixed ceiling; the attribute-property product factored | inherited (S3: 384 rows against 16,512 at 128 by 128). E2.5 measures the real sizes on the `english.grammar` export of every corpus lexicon; GE2 item 9 measures instantiation at the limit environment |
| 2 | **Cost.** Cap invariant, rule-suffix memoisation, measured steps | inherited. The budgets S1a could not measure are GE2 item 9, on the service, with `policyOk` added to instantiation |
| 2a | **G1a is a pass gate** | GE2 item 9: met, or the revision reviewed before the flip; a 5× miss triggers investigation only |
| 3 | **Parity.** Tree correspondence; verdicts, formulas and witness multiplicity, not rule sets | GE2 item 2, at the dispatched boundary, under S3 2.11's correspondence; after the flip the comparator records the same classes (spec 2.8) |
| 4 | **Reverse corpus.** Sampled from Lean's exported grammar, with spacing and word-split mutants, against the hand parser and Lark; Lark a logged comparator until retirement | GE2 item 2; the sampler reads `english.grammar` (E2.0). The hand parser and Lark stay as the comparator through this stage and are deleted in the next (pointer plan) |
| 5 | **`extension_safe`.** Semantic `Embeds`; vocabulary reselection is not an extension | unchanged: `grammar_extension` reads `Lexicon.valid`, which E2 does not change (decision 2). V6 is not monotone under extension (a new predicate can make an old wording collide), which is one more reason it stays outside `valid` (spec 2.4) |
| 6 | **Lexicon.** `valid` with V4 and V5; the lint sort; P1 per lexicon; mutation replay an empirical gate; no meaning-neutrality claim | E2.1: the lint codes that S0's sort left with Python move into Lean as V6 (decision 3); GE2 item 2 runs the mutation replay with V6; `english_reading_unique` is unchanged and still claims nothing about a second lexicon |
| 7 | **Contract.** `DocOneReading`; `read_ok` and `checkRendering` conclude formulas and marks; `EnglishOneReading` includes `Lexicon.valid`; evidence binds six identities | E2.2: `admitRequest_ok` concludes `EnglishOneReading` and V6; E2.3: every record carries the six identities; spec 2.7 binds the lexicon to the display environment (ev15) |
| 8 | **Options, shadow.** Option H in reserve; G4 a fresh-seed volume and coverage gate with zero undispositioned differences | option H: not needed. G4: superseded by the DRI (amendment P1); GE2 item 2 carries the volume and coverage targets of edit 8 |

Astra's three qualifications hold:

1. Mutation replay is empirical, and the guarantee is per lexicon (spec 9).
2. Semantic preservation reaches complete results, and `actions_version` covers every trusted definition file,
   `Policy.lean` and `Advice.lean` included (spec 2.11).
3. The budgets are pass gates (GE2 item 9).

**The statement review** (`debates/english-lean-e2-spec/`, converged FIX after round 3). Its six items, as applied:

| # | Item | Where applied | Gates |
|---|---|---|---|
| 1 | **Enumeration.** The port enumerates the declared symbols where Python does; the generated ones stay in V6's domain, the initial spellings, the fixpoint and the severity noun. Fixture `{0} is fully avoidable`; the class and severity-sort rows; the generated names in the mutation set | spec D1, D5, 2.3, 5.2, 2.10; lx32a to lx32c (draft 1 wrong, draft 2 Python's, computed) | E2.1 |
| 2 | **The overlay check.** Python's three refusals as a Lean check in Python's order, with its own code, `InvalidOverlay`, of class `VEError`; the admission path's producer stops raising, other callers keep the raise; ledger rows; paired fixtures; constants never refused; parity by raise against no raise | spec D16, D17, 2.3, 2.8, 2.9, 2.10, 4.2, 4.4, 5.2, 5.5 (`overlayCheck_constants`); ov1 to ov10, ovc; rl9, rl10 | E2.1, E2.2 |
| 3 | **The boundary.** D7 part four: modal extraction under `norm-defaults@0` through an adapter, frozen decoders unedited, with a direct `Env.decode` fixture and a malformed-declaration fixture. Modal forms before role wordings in E2.0 | spec D7, D18, 2.2, 5.3; md1 to md5 | E2.0 |
| 4 | **Guards and responses.** The translation and grammar guards defined; the order boundary, overlay check, V6, then V1 to V5, with lx24; `english.check` answers `invalidGrammar`, and `{}` only after the guard; `NotOneSentence → SyntaxError` | spec D8, D9, 2.5, 2.7, 4.2, 4.4, 5.3, 5.5 (`translateRequest_policy`, `grammarFault_none`); gg1, gg2, tg1, tg2, cn19, ev4d, ev17, lx24′, rl11 | E2.0, E2.2 |
| 5 | **`unaryPhrase`.** It follows `re.I`, with Python's letters; section 9 corrected; a Kelvin-sign fixture | spec 2.3, 5.2, 9; lx31c to lx31f | E2.1 |
| 6 | **Claims and texts.** Three rows of 8.10 scoped; the `unproved` text carries the prover's status | spec 8.10 (with lx33a, lx33b, ev15d, ad19), D11, 2.8, 4.2; cn15, rl2 | E2.2 |

The Python expectations of the new fixtures were read from the source, since Python could not be run in the planner
session; lx32a and lx31c were run by the review. Running the script beside the stub (spec py1) comes first in the
bounded round.

## 3. DRI rulings and amendments in force

| # | Ruling or amendment | Where applied |
|---|---|---|
| R1 | Spacing: no silent widening | unchanged; the reverse corpus's spacing mutants test it (GE2 item 2) |
| R2 | No symbol exempt from V1; `risk__more_severe` worded | in force since S3 (D9) |
| R3 | `coefficientNotNumeral`, `natural-negation`, `risk-every-cannot` | in force; in the class table (spec 4.2) |
| R4 | Lint sort: anything that changes accept or reject belongs in Lean | E2.1: V6 (decision 3) and the overlay check (decision 8). No code becomes a warning: together they are Python's acceptance, so they widen nothing (S3 D14, Q12); V6 alone would accept an overlay that Python refuses |
| R5 | Design point: 300 tokens, work budget 2,100,000 steps | GE2 item 9 |
| R7 | Senses: the lexicon data admits senses without changing identity rules | decision 7; spec 2.4, 2.11, lx30 |
| P1 | E2 moves authority on corpus evidence, with no calendar window | GE2 |
| P2 | The Python parser leaves the admission path, kept only as a logged comparator for this stage and deleted in the next | E2.3, E2.4; spec 2.8, 2.9 |
| P3 | One owner: Lean decides; Python transports and displays | decisions 2, 6; spec 2.8 |
| P4 | No Python copy of the grammar | the editor's Lark grammar, if kept, is generated from the `english.grammar` export and decides nothing (LEAN-FIRST 5.2) |

The pointer plan cites the rulings of `manage-agents/english-lean-dri-note.md` as "1-5, 7". That file has rulings 1
to 6. Ruling 7, the senses ruling, is in `english-lean-s2-dri-note.md`, which repeats 1 to 6 and adds it. Ruling 6
scoped the S0 and S1 merge and is not in force here.

## 4. What S3 left open, and where it goes

| Item (S3 report, "Open gates"; S3 plan, questions) | Here |
|---|---|
| G3: sealed core, reverse grammar, lexicon mutation, use cases and pilots, latency | E2.5; GE2 items 2 and 9 |
| E2.0 to E2.4 | E2.0 to E2.4, with the corrections of decisions 2, 3, 5, 6 and 8 |
| Build checklist line 1: E2's generated diagnostic table | E2.2 (the class table and texts, exported) |
| line 2: differential fuzz over the larger corpus | E2.5 (the three-way differential, 14 seeds) |
| line 10: the single `admit` relay across all entry points | E2.3 |
| S3 Q4: whether Lean computes the lexicon | question 3 |
| S3 Q5 and question 6: `rights@0` wordings | E3; GE2's `DELTA.md` lists any corpus text that becomes `availability` |
| S3 Q12: whether a V6 code becomes a warning | no: V6 is Python's acceptance (R4) |
| S3 spec 8.6: the obligations lx9b to lx9d, lx14 to lx24 | lx15 to lx24 computed here (spec 8.1, 8.2); lx9b to lx9d and lx14 stay S3's obligations, confirmed by E2.5 |
| S3 spec ad15 and ad16 | computed here (spec ad15 to ad17) |

## 5. Findings of this draft

Each finding below was computed by the stub (spec section 12).

1. **V6 refuses two S3 fixture lexicons.** Under `FA` and `FR`, Python selects the quoted fallback for `safe`,
   because `{0} is safe` collides with the head `is` of the role wording `{0} is available to {1}` and no rescue
   pattern matches. The S3 report measured the same thing on Python. The S3 fixture lexicons `LA` and `LR` select the
   declared wording, so they fail V6, and E2's admission fixtures use `safe` on its fallback (spec lx29, cn11,
   cn12). S3's `read` fixtures are unaffected, since `read` does not run V6.
2. **The overlay identity** (decision 5; spec ev15).
3. **The boundary refuses four corpus environments** (decision 5; spec ev14).
4. **V1 to V5 accept lexicons that Python never makes** (decision 3; spec lx25 to lx28).
5. **V6 inside `Lexicon.valid` would break the senses projection** (decision 2; spec lx30).
6. **A role predicate that is also modal.** `Env.decode` lists the role wordings before the modal forms, so
   `forms.wordings.lookup` gives a role predicate its role wording, while Python gives it the modal form
   (`english.py:521–527` runs last). The S3 build is affected. No corpus environment regulates a role predicate,
   and the boundary refuses such an environment (`AlternativesRegulated`, computed, spec md4). The port follows
   Python. E2.0 lists the modal forms first (spec D18).

Draft 3 adds the findings of the statement review, each computed by the stub unless it says otherwise.

7. **Generated symbols were enumerated.** Draft 1's port treated the symbols that profile blocks generate as owners
   and collisions, which Python never does. In three cases it refused what Python selects, among them
   `{0} is fully avoidable` under `alternatives@0` (spec lx32; Python's choice run by the review for that one, read
   from the source for the other two). Draft 2's text reproduces all 22 recorded identities.
8. **Python refuses overlays that V6 would accept.** The producer's three overlay refusals are not visible in the
   lexicon it selects; the overlay check reproduces them (spec 8.11). On the four corpus overlays it refuses none, as
   Python did.
9. **`unspecified` defaults stop `Env.decode`.** The frozen `decodeRegulated` refuses them before any modal form is
   read (spec md1a); the placeholder reading fixes it, and the four refused rows then give Python's identities
   (md5).
10. **The responses were incomplete.** `NotOneSentence` had no class, and `english.check` answered `{}` for a refused
    vocabulary as well as for no reading candidate (spec cn19, ev4d).
11. **`re.I` reaches the suggested path.** Python accepts a suggested `{0} is Keen` written with the Kelvin sign;
    draft 1 did not (spec lx31c; Python run by the review).
12. **The `unproved` text dropped the prover's status**, which Python shows. The text now has a slot for it.

## 6. Honest open questions

1. **The port is trusted.** `Policy.lean` is about 350 lines of ported heuristics: two pattern tables, eight word
   lists, the rescue, the idiom branch, a fixpoint over spellings, the overlay check. Its correctness is tested
   against Python (pt1: 22 of 22 corpus rows by `lexicon_id`; E2.1's two parity harnesses on every environment,
   overlay and mutant), not proved. A port defect that accepts more than Python can be seen only by comparing
   choices, which is why the parity harness compares Python's selection symbol by symbol and does not stop at
   "Python's lexicon passes". Draft 1's enumeration defect (finding 7) is such a defect, found by the review.
2. **The 17 round-trip configurations of the lexicon report are built in Python** (`conformance/english_surface.py`)
   and were not reproduced in the stub. E2.1's harness runs them.
3. **Lean as the producer.** V6 now computes Python's selection, so a Lean `english.lexicon` mode could produce the
   lexicon and `EnglishVocabulary`'s selection logic (`english.py:230–527`) could go. Every renderer reads the
   Python selection today (`render_english`, the natural views, the legends), and the senses plan expects `_RESERVED`
   to be deleted "with the Python producer". Recommendation: not in E2. The next stage makes Lean the producer and
   moves the renderers to its export; until then the ledger lists the selection logic as kept, a producer whose output
   V6 checks.
4. **Letters are not in V6.** `_fluent_variable_letters` is ported only to reproduce `lexicon_id`. A label is an
   upper-case letter run with a number, so no letter turns a word into a label. Two sorts with one letter give two
   derivations, which the per-sentence check refuses. Recommendation: leave letters to V1. The port is there if the
   review wants them in V6.
5. **The identity fix chooses Lean's side.** Python's export could instead name the submitted environment. That
   would change `lexicon_id` for every overlay document. Lean binding the lexicon to the display environment changes
   no identity value. Recommendation: Lean's side (spec 2.7).
6. **The boundary extension may meet the lean-first batch 12b.** That batch makes the `environment` mode accept every
   profile Python's registry accepts. If 12b lands first, E2.0 calls its decoders. Otherwise E2.0 adds typing-view
   reductions for the three profiles, which 12b later replaces.
7. **`EnglishParser` cannot be deleted in E2** (S3 plan, question 3). Until E3 moves the statement layers, Python
   still decides the formulas embedded in norm blocks.
8. **The conclusion check stays split** (S3 D10). Lean names the obligations and their premises; the entailment
   operation proves them. A Lean-side entailment call is for the lean-first batch that owns entailment.
9. **Performance at pilot size is still unmeasured** (S3 plan, question 8); GE2 item 9 measures it. If a budget is
   missed, the flip waits.
10. **Python was not run for the new fixtures.** The planner session's permissions refused running Python, so the
    Python column of each new fixture was read from the source, except the two cases the review ran. The script
    `lean/SpecStubs_english-lean-e2.py`, untracked beside the stub, prints each one. Recommendation: run it as the
    first step of the bounded round (spec py1); a difference corrects the spec before any stage starts.
