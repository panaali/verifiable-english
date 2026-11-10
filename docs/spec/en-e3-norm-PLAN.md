# en-e3-norm PLAN: english-lean's E3 norm step

Plan draft 1, 2026-10-29, branch `design/en-e3-norm`. Research: [docs/research/en-e3-norm.md](../research/en-e3-norm.md).

Draft 2, 2026-11-02: the converged EN-0 edits of the design debate (`MA/debates/design-en-e3-norm`, round 3: REVISE
inside EN-0, docs only, then BUILD) and the DRI's cross-plan orders (`MA/debates/design-en-e3-norm/DRI-CROSSPLAN.md`;
`MA/reviews/dri-decisions-20261102-en-e3-norm.md`), applied as edits. Where the two differ, the orders decide. EN-1 is
done by en-s6 and en-s6b against `docs/spec/english-lean-s6.md`. The item-1 statement spec of EN-2 and EN-3 is
[docs/spec/en-e3-norm.md](en-e3-norm.md).

Draft 3, 2026-11-02: the statement review's edits (`MA/debates/en-e3-norm-spec/DRI-RULING.md`, FIX, edits 1 to 22),
applied to D10, the shared-file table (2.2), EN-1's note on `_consequence`, EN-2, EN-3, EN-4's deletions and the
deletion summary (section 8). The spec, draft 2, carries the rest.

Draft 4, 2026-11-02: the verifier's findings on those edits (`MA/en-e3-norm-p3ver1.final.md`, FAIL), applied to D2, the
shared-file table (2.2), EN-2's recipe and delta classes, EN-3, EN-4's deletions and the deletion summary (section 8).
The spec, draft 3, carries the rest.

Draft 5, 2026-11-02: the verifier's report on draft 4 (`MA/en-e3-norm-p3ver2.final.md`, FAIL), applied to the shared-file
table (2.2), EN-2's recipe and EN-3. The table gains the files that EN-2, EN-3 and EN-4 must change and it did not list.
`tools/relay_lint.py` leaves EN-3's row. The spec, draft 4, carries the rest.

Draft 6, 2026-11-02: the verifier's report on draft 5 (`MA/en-e3-norm-p3ver3.final.md`, FAIL), applied by the acting DRI
to the shared-file table (2.2): EN-3's row gains `conformance/binding_probes.py`. The spec, draft 5, carries the rest.

**Owner:** english-lean, at its E3 statement layer (DRI 2026-10-28, commitments item 2(f)). This is the backlog row
en-e3-norm. Round 2 asks that it be scheduled as an item with its own estimate, because CM-4, the commands-imperatives
readers that need it, and QT-B3 wait for it (`MA/debates/plan-synthesis-2/edits-english-lean.md` item 3).

**Scope:** one Lean reader that turns a norm sentence into a `norms@0` rule (or a `soft-norms@0` default rule), with
one reading or a reading set licensed by owners' rows. A norm sentence has these parts:
- a subject;
- a force or commitment word, taken from rows;
- an act, using the lexicon and act phrases' checks;
- conditions and exceptions, read by the formula grammar;
- numeric and temporal phrases, which the reader parses and hands off without interpreting them.

The reader has two modes:
- **authoring**: VE's own rule blocks, replacing `ve/norm_english.py`;
- **translation**: a source's sentences.

Check mode is a use of translation mode.

**Not in scope, owned elsewhere** (research 1.3):
- commitment strengths and wordings, CM-4's rows, lead-ins (CM-5) and `bare_will_refused` (commitments);
- likelihood words (attitudes); "usually" and the other D6 words (DF-4); the row type (en-sw); weighing frames (en-wg);
- what any deadline, cadence, count or comparison means: ET-5, ET-T1, ET-D2, W6, QT-A6, QT-B3, QT-E;
- pronouns (discourse).

**Conventions:**
- Path prefixes: no prefix is this worktree (main at `ffddf155c`); `MA/` is `/home/seyran/code/manage-agents`; `CM/` is
  `/home/seyran/code/ve-design-commitments`.
- Byte figures are measured where the method is named, and marked **estimate** otherwise.
- Lean blocks use main's names exactly where they cite them. New names are proposals: EN-0's stub elaborates every
  block against main and records each correction, as the precedents do ("CM-0 binds").

## 0. Design decisions

- **D1. One reader.**
  - Every norm sentence, authored or source, is read by one grammar on english-lean's proved engine (`VE.Grammar`).
  - The norm frames are rows of one generated table, `ve/english_grammar/norms@0.json`, rendered by
    `tools/english_grammar_gen.py` (round 2 DEC 12: no fourth engine).
  - Commands' matcher is not used (DRI, commands-imperatives item 4(f)).
  - en-wg's weighing frames join the same grammar. An overlap between frames is then a `many` outcome, never two
    readers that disagree.
- **D2. Conditions are the formula grammar's own reading.**
  - The norm grammar keeps every rule of `grammar E L` as a prefix, under the same numbers.
  - A condition subtree therefore has exactly the value `english.read` gives it (`condition_same`, EN-1).
  - No second condition reader exists. Python's `_parse_guard` loses its W1 calls in EN-3. The function, with its
    `require_unique_derivation` wrapper, goes in EN-4 with its last caller, `_parse_soft_notes`
    (`ve/norm_english.py:468`).
- **D3. `many` is not a reading set** (round 2, D11).
  - In authoring, two derivations are refused, with both shown.
  - In translation, a sentence must have exactly one structure. A reading set arises only when a matched row of kind
    `readings` (en-sw's `SourceWordRow`) gives two or more candidate wordings.
  - Each candidate is an authored sentence: the row's wording with the sentence's parts filled in. The authoring mode
    reads each candidate, and needs exactly one reading for it.
  - So the reader is shown every reading as plain English, and each reading is itself a VE sentence with one reading.
  - A candidate that the authoring mode refuses is kept as a W2 **pending** candidate, carrying the refusal's code. It
    is never dropped. Any choice that uses it is UNKNOWN.
  - Example: until C12's `gate_acts` revision, a default candidate whose act needs an acts@0 fixed phrase is pending,
    because acts@0 refuses soft-norms@0.
  - A route refusal comes from composition's gate: the pending candidate's code is the gate's own text
    (`VE.Compose.gateOf profileTable`, "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"), and
    `Matrix.documentRefusal`'s once profile-composition's PC-4 lands. No `JoinRoute` code is copied.
  - When a sentence matches several readings rows, the candidates are every combination of them: the choice vectors of
    `VE.Discourse.allChoices` (`Discourse/Joint.lean`, PLANS-INDEX D1) over one set per matched row, complete by
    `mem_allChoices` and counted by `length_allChoices`. Each candidate records every row that contributed. Over the
    W2 limit (`VE.Readings.maxChoices`) the outcome is UNKNOWN (`limit`), as `compatible_budget` gives
    `ResourceLimit: joint choices`, never a shortened list.
  - The set is a W2 authored set (PLANS-INDEX D11). It is not composition's superposed set and not english-lean's
    `many`.
- **D4. One output path.**
  - A reading becomes a rule only through the existing decoders: `VE.Norms.Wire.decodeNorm` for W1, and soft-norms'
    `decodeSoftNorm` for default rules.
  - It never builds a `Node` by hand (`toNode`, EN-1). No second rule format exists.
- **D5. Numeric and temporal phrases are unformalised spans; MIXED is a measurement only.** This is commitments' D14,
  kept a measurement rule (design debate round 3; DRI 2026-11-02).
  - The reader parses these phrases and records each as an `UnformalisedSpan` (NEW; not ve-limits' `Residual`, which
    holds an OPEN unit's open terms or its active reading set): its span, the matching row, its place in the one parse
    and the row's meaning owner. Main's `Norm/Value.lean` keeps the name `Residual` for the clause's carrier field
    (merged in EN-1); the answer and the measure name the record `UnformalisedSpan`.
  - The owner is the row's meaning owner. For cadence words it is a W2 or judgment-terms open term, or ET-T1 (section 5).
    Where no meaning owner exists, the owner is `unowned` and the row carries the round-2 request (section 9). A span may
    cite a ve-limits code as its class, never as its owner. en-e3-norm is never the owner: it writes the placeholder
    refuse-rows with the meaning owner's name or `unowned`.
  - No product rule drops a span. A clause with an unformalised span never reaches `toNode` or `toSoft`. The reader
    answers MIXED as its own outcome, never `.one`, and check mode answers `partial` with the spans, never `verified`.
  - Draft 1's weakening rule (a span split off at the act of a `must` clause, for a restricting row) is removed from
    the product:
    - W1 adds `required → permitted` under deny completion, and a breach is ¬permitted ∧ done
      (`docs/spec/norms.md:222-226`). Reading "must publish within 30 days" as "must publish" also permits publishing
      on day 60, so a breach the source has disappears.
    - The restricting mark is not sound either: dropping the count from "consult at least zero reviewers" adds an
      obligation to consult.
  - Product use of any such projection waits for its owner's theorem that the projection keeps every breach, in the
    obligation and the permission half alike. That is a request to the owners (section 7, R9), not EN-7 work.
  - The place and the row's restricting mark stay recorded data of each span: EN-7 classifies MIXED by them (only at
    place `act` of a `must` clause, outside negation, for a restricting row; anywhere else UNFORMALISED). They license
    nothing.
  - The restricting mark is a field of this plan's own frame rows ("norm.modifier"). It is reviewed with them, and it is
    never inferred.
  - No residual word may appear inside a source spelling of an act. Hand translations do this today (703 B, research
    2.3).
- **D6. Strengths are commitments'; force words are their specs' owners'.**
  - The reader applies rows. It does not decide what "we will", "should" or "may" mean.
  - Commitment words come from CM-4's rows, and their authored wordings from `Commitments/Read.lean`.
  - "must", "should" and "may" in translation are soft-norms 2.2 ({strict, default}) and norms 2 ({permission,
    might}). This plan asks those owners for their rows (section 7, request R1).
  - The "might" candidate is pending under its meaning owner, modality-counterfactual: norms.md says "may" never means
    "might" in the norm wordings (`norms.md:61, 87, 173`). A set that holds it is SOURCE-READ-PENDING (D11).
  - A row narrowed by a cited unit (the use cases' N1) is narrowed by the row owner's mechanism. The reader only
    reports which row produced which candidate.
- **D7. Acts come from the lexicon, never from free text.**
  - An act phrase in a source sentence must match a declared act wording, or a declared **source spelling** of one
    (NEW).
  - A source spelling is an alias, not a new list: the source view adds the use case's source spellings to
    `Lexicon.aliases` (predicate, input wording, negated) and to the environment's fixed aliases, so V1-V5 check them
    with every other alias (`sourceView`, EN-2's first step). Draft 1's `SourceLexicon.spellings` restated
    `Lexicon.aliases` and is dropped. Authoring mode never reads a source spelling.
  - A source spelling passes act phrases' lexical checks (clause words, joins outside fixed phrases), english-lean's
    distinctness check (V4), and D5's ban on residual words.
  - What the act means stays a trusted declaration shown in the legend, as today (english-lean-PLAN 2.4).
- **D8. Bearers.**
  - The reader returns the bearer as read: "Every <noun>", a declared constant or organ, "we", or an agentless
    passive.
  - "we" elaborates only through the one pronoun legend: speech-acts' binding, once commitments' CM-1 moves it. Until
    then "we" is refused with `AuthorLegendMissing`.
  - The binding is read from the moved `VE.Legend` (`eqsFrom` and the binding check, `CM/…/commitments-PLAN.md:405-408`).
    This plan does not restate speech-acts' `eqGuard`.
  - Organs are commitments' S2.
- **D9. Check mode.**
  - It compares a hand rule with the reader's readings, field by field: force, mode, sign, predicate, guard,
    exceptions.
  - The hand side is the unit's existing content, not a bare node list: a W1 or soft-norms rule with its soft decisions
    (`VE.Compose.Content.norm`), or a W2 authored set (`VE.Readings.ReadingSet`) with the document's cited narrowings.
  - It reports `verified` only when the hand content agrees with the whole set: the reader's one reading, or every
    candidate of the reader's set, never membership in one candidate. A narrowing is cited in the document, never
    silent.
  - It reports `partial` with the spans for a reading with an unformalised span, never `verified`; `pending` with the
    codes when every candidate is pending; and `unknown` when the reader stopped at its budget.
  - It reports `verified`, `mismatch` (naming fields, including "set not collapsed" and "hidden residual"), or `unread`
    (with the reader's code). It never repairs a hand rule.
  - These results (verified, partial, pending, mismatch with its fields, unread, unknown) are a new answer vocabulary,
    listed NEW under PLANS-INDEX D8 (section 9), with no rename.
  - For a use case whose rules speak about one "situation" sort (RSP deviation 1), the bearer is compared under that
    use case's declared convention and reported as a note.
- **D10. Authority moves per layer, after a delta** (english-lean S6).
  - Each layer (W1 blocks, then soft blocks) runs in shadow beside Python, produces a delta report over every recorded
    corpus, gets the DRI's decision on its delta rows (changed rejections, admissions and meanings), and only then
    becomes the authority.
  - Python's reader for that layer is then deleted, not kept as a fallback.
  - EN-2 changes no route's answer: it runs in shadow only. The DRI decides every row of EN-2's delta report that is
    not `agree` or `both-refuse`, once per layer (spec section 6). That decision is the stop point between EN-2 and
    EN-3; no other signature is reserved.
  - EN-2 deletes nothing, so its new trusted Lean lines (`Norm/Run.lean`, `Norm/Owners.lean`, any OPEN-2 hunk in
    `Norm/Rules.lean`) go under R16 at EN-2's merge (estimated at 150 or fewer). In EN-3, R6 covers only the lines
    that replace Python's deleted W1 path: `Norm/Render.lean`'s frame and `Norm/Run.lean`'s render kind (request,
    decoder, encoder). Other new trusted Lean lines go under R16 (+150 per item; above that, the item is cut).
- **D11. The source-read measure.**
  - For each norm unit of a use case, EN-10 records one of: SOURCE-READ, SOURCE-READ-PENDING, MIXED, MISMATCH, or
    UNREAD with a code.
    - SOURCE-READ: the reader's reading is the unit's rule, or the reader's set is the unit's set. A set with a pending
      candidate is listed with that candidate's code.
    - SOURCE-READ-PENDING: as SOURCE-READ, but the set holds a candidate that stays pending under its owner (R1's
      "might", until modality-counterfactual's row exists). Its bytes are kept out of the source-read bytes.
    - MIXED: the rule is read, and the residual bytes are UNFORMALISED.
    - MISMATCH: the reader reads the sentence, and the hand rule differs from its reading.
    - UNREAD: the reader refuses the sentence, with a code.
  - Source-read bytes are the SOURCE-READ bytes plus the read part of MIXED units.
  - SOURCE-READ-PENDING bytes are not source-read bytes.
  - Statuses (CHECKED, OPEN, …) are not changed by this measure, except that a MIXED unit's residual bytes are counted
    UNFORMALISED.
  - These columns are their own measure (source-reading fidelity, NEW). They sit beside ve-limits' bytes-per-class
    report and share its byte partition and the existing classification table; neither replaces the other.
  - `SourceOutcome.readings` is a W2 authored set (PLANS-INDEX D11), not a fourth meaning of "reading set".

## 1. Batches

| # | Batch | Kind | Hours | Needs | Number moved (measured on fixtures, or **estimate**) |
|---|---|---|---:|---|---|
| EN-0 | Statement spec, stub, computed fixtures, statement review | planner | 3-4 | — | 0; records the baseline: 0 of 120 pinned rule blocks read by Lean |
| **EN-1** | **Authored W1 rule blocks in Lean (authoring mode), no wiring.** Done by en-s6 (merged) and en-s6b (building); statements: `docs/spec/english-lean-s6.md` | Lean | 5-6 | EN-0 | **pinned rule blocks Lean reads to Python's node: 0 → 103 of 120 (RSP 64 of 76, FSF 39 of 44; the 17 "should" blocks are EN-4's)** |
| EN-2 | First step: the EN-0 corrections that EN-1 does not do (owners' `Op` and `Mode`, the source view, the span gate); mode `english.statement`, shadow relay, delta report | Lean runner, shape, Python relay | 5-6 | EN-1 | live shadow agreement over every recorded corpus; the delta report |
| EN-3 | Authority for W1 blocks, Lean rendering, Python's W1 matcher deleted | Lean and Python | 4-5 | EN-2, the DRI's delta decision | `english.statement` (W1 part) authority python → lean |
| EN-4 | Soft rule blocks ("should", "generally may", exception notes) | Lean and Python | 5-6 | EN-3, `feature/rd9-docroute` merged, DF-4's rows | Lean-read rule English on every formal norm unit: RSP 17,589 B, FSF 7,923 B (status unchanged) |
| EN-5 | Translation mode: one structure, force rows, source spellings | Lean | 5-6 | EN-3, en-sw merged, R1 rows, the fidelity pilot fp-en-e3-norm's CONTINUE | source-read: PF 0.3-0.8 kB, FSF 0.1-0.3 kB, constitution a few units (**estimate**) |
| EN-E2 | Experiment: parse ambiguity of real norm sentences | experiment, model-free | 2-3 | EN-5 | gates EN-8's attachment rows |
| EN-7 | Unformalised spans and MIXED (a measurement only) | Lean | 4-5 | EN-5; ET-5's rows where landed | MIXED: RSP 1.3-2.5 kB, PF 1-2 kB, FSF 0.4-0.6 kB (**estimate**); 703 B of hidden atoms reported (measured) |
| EN-6 | Commitment rows applied; "we" through the legend; passives | Lean | 3-4 | EN-5, CM-4's rows (CM-4 after EN-5, section 7 R6), CM-1's legend move | source-read: RSP 2-3.5 kB, PF 1-1.5 kB, constitution 1-2 kB (**estimate**) |
| EN-8 | Two clauses sharing a guard, numbered conditions, act joins on the norms route | Lean | 5-6 | EN-6, EN-E2 | RSP +1-2 kB, PF +0.5-1 kB, FSF +0.2 kB (**estimate**) |
| EN-9 | List items under a lead-in | Lean | 3-4 | EN-8, CM-5 (after `feature/sc-1ae`) | PF Appendix C.3 +2-3 kB (mostly MIXED); RSP +0.8-1.5 kB; constitution 0.4-0.7 kB (**estimate**) |
| EN-10 | Check mode (kind `check`) and the use-case accounting | Lean kind, use case | 4-5 | EN-5 (re-run after each later batch), `usecase-rsp-run`, `usecase-safetyfw-b` | publishes the measured numbers that replace this table's estimates |
| EN-E1 | Experiment: does check mode catch the FSF audit's unfaithful units? | experiment, model-free | 3 | EN-8, EN-10 | gates offering check mode as a translators' pre-commit check |
| EN-E3 | Experiment, conditional: certified rewriting (research D3) | experiment, model-free | 3 | EN-E2 failed, or EN-9 below the low estimates | decides whether D3 is designed |

**Total:** about 47-57 h of batches, plus 8-9 h of experiments.

english-lean's own estimate for a statement layer is "about 1 w each" (`docs/spec/english-lean-PLAN.md:608`). EN-1 to
EN-4 (19-23 h) are the norm and soft layers; the estimate is lower because the engine and its proofs exist since S1b.
EN-2's shadow window is calendar time, not work hours.

**Order** (design debate round 3, adopted by the DRI 2026-11-02):
1. EN-0; EN-1 (done by en-s6 and en-s6b); EN-2.
2. The shadow window and the DRI's delta decision: the stop point between EN-2 and EN-3.
3. EN-3; then EN-4 once `feature/rd9-docroute` and DF-4's rows have landed.
4. The fidelity paper pilot (backlog row fp-en-e3-norm), then EN-5 once en-sw and the owners' rows exist.
   - The pilot runs before EN-5 (translation mode), not before EN-2 or EN-3. EN-1 to EN-4 read authored blocks only;
     their test is the 120-block Lean-vs-Python node comparison plus the shadow delta.
   - The kill line is the standing one: fewer than 8 of 10 FAITHFUL and COMPOSES gives REVISE. No EN-5 batch starts
     before the pilot's RESULT.md says CONTINUE.
5. EN-E2 and EN-10 after EN-5. EN-10 is re-run after each later batch.
6. CM-4's providers (after EN-5, CM-2, en-sw and CM-E1), then EN-6 (after CM-1).
7. EN-7, as a measurement only.
8. EN-8 after EN-E2.
9. EN-9 after CM-5 and `feature/sc-1ae`.
10. EN-E1 last.

**The first product batch, EN-1, is the smallest that moves a pilot number.** It needs nothing unbuilt.
- It reads the 76 RSP and 44 FSF rule blocks of the pinned translations in Lean.
- Python's node for each block is the expected value, recorded by EN-0.
- The block counts are a measured search of `usecases/*/rules.d1.ve` for `^Rule [0-9]+`. The "should" blocks, a search
  for `Every <noun> should`, number RSP 12 and FSF 5.

## 2. Dependencies, conflicts and shared files

### 2.1 Other items, by branch or state

| Item | State | Needed by | How the batch avoids a conflict |
|---|---|---|---|
| en-sw: `lean/VE/EnglishGrammar/SourceWords.lean`, `ve/english_grammar/source_words` | queued, rank 113, ready | EN-5 onward | EN-5 reads its rows and adds rows only in its own frame keys, in separate hunks (C1 rule). EN-1 to EN-4 do not touch it. If en-sw lands second to EN-1, the only shared file is the generated `ve/english_grammar/LOCK.json`, and `tools/regen_generated.py --resolve` finishes that merge. |
| `feature/rd9-docroute` | in flight: `ve/document/`, `lean/VE/SoftNorms/Phases.lean`, `ve/norms.py`, `ve/norm_defaults.py` | EN-4 | EN-4 starts after it merges; EN-1 to EN-3 touch none of its files |
| `infra/usecase-safetyfw-b` | in flight (the PF baseline) | EN-10's PF columns | EN-10 adds columns to `measure` scripts only after it merges |
| usecase-rsp-run | ready | EN-10's RSP columns | the same |
| sc-1c | queued; edits `lean/VE/Service/Protocol.lean` | — | EN-2 adds one dispatch line to the same file; whichever merges second rebases one hunk |
| ET-5 | ready; rows "until", "by", "within", "during", "since", "while" | EN-7 | EN-7 reads them where they have landed; it writes no row for ET-5's words |
| DF-4's rows ("usually", "normally", "generally", `FREQUENCY_WORDS`) | planned; en-sw queue position 3 | EN-4 (the refusal at `ve/norm_english.py:422`), EN-6 | EN-4 replaces Python's hard-coded refusal by a lookup of DF-4's rows. If they are not there, EN-4 waits; it does not copy the word list. |
| CM-1 (the legend move), CM-4 (rows, `lean/VE/Commitments/Read.lean`), CM-5 (`lean/VE/Commitments/Lead.lean`) | design-ready, not building | EN-6, EN-9 | EN-6 and EN-9 read those modules and write nothing in `VE.Commitments` |
| C12: one `gate_acts` revision (CI-5 then PC-6) | design-ready | EN-8's joins on the soft and readings routes | until it lands, EN-8 reads joins on the norms route only and refuses them elsewhere with the gate's own refusal (no `JoinRoute` code) |
| profile-composition PC-4 (`lean/VE/Compose/Matrix.lean`, `Matrix.documentRefusal`) | designed, not on main | EN-5 and EN-8 (route refusals of candidates) | read only: until it lands, the refusal text is `VE.Compose.gateOf profileTable`'s; after it, `Matrix.documentRefusal`'s |
| fidelity paper pilot (backlog row fp-en-e3-norm) | filed | EN-5 | no EN-5 batch starts before its RESULT.md says CONTINUE (fewer than 8 of 10 FAITHFUL and COMPOSES gives REVISE) |
| en-wg (weighing frames) | blocked by en-sw and wg-2 | — | it edits the same two `Ty`/`Sem` places as EN-1. EN-1 adds a `statement` type with one constructor family (section 9, NEW 1); en-wg adds its constructor in a separate hunk; whichever is second rebases a one-line conflict. The weighing refresh's disjointness fixtures (ruling (d)) become `many`-refusal fixtures of the one grammar. |
| QT-E (the quantities step of E3: `ve/surface/time.py`'s 13 forms) | planned | EN-7 | the amount and duration terminal classes of english-lean 2.5 are added once, by whichever batch lands first; the other reuses them |
| QT-B3 (comparison wordings) | planned; "may instead follow english-lean E3's norm step" | — | EN-5's act slot accepts an argument filler nonterminal. QT-B3 adds its comparison rows there when it builds. Until then "at least as strong as" is a residual with owner QT-B3. |

### 2.2 Shared files, per batch

Every other file a batch touches is new. Each batch's changed files are a subset of its row here and the new files
its section names (statement review, edit 19). A generated column names the files particular to the batch; every row
also includes whatever else `tools/regen_generated.py --write` refreshes, such as `lean/declarations.txt`,
`lean/predicates.txt`, `lean/checkers.lock` and `docs/codemap/`. A file that an earlier batch creates and a later one
edits is in the later batch's row. The trust ledgers are not refreshed by `--write`, so a row that adds trusted Lean
lines names them.

| Batch | Shared hand-written files | Generated files (never hand-edited; regenerated) |
|---|---|---|
| EN-1 | `lean/VE/EnglishGrammar/Syntax.lean` (`Ty`: one hunk); `lean/VE/EnglishGrammar/Actions.lean` (`Sem`: one hunk); `lean/VE/Audit.lean` (`#print axioms` lines, appended); `tools/layer_policy.py` (rows for the new modules); `lean/VE.lean` (imports, appended). If the generator's row format has no per-table action list, also one hunk each in `lean/VE/EnglishGrammar/Catalogue.lean` (`ntTy`, `FixedAct`); EN-0 decides this by reading `tools/english_grammar_gen.py`. | `lean/VE/EnglishGrammar/Fixed/Norms.lean` (new), `ve/english_grammar/LOCK.json`, `Fixed/Version.lean` (`actions_version` bump), the frozen Lean inventory |
| EN-2 | `lean/VE/Service/Protocol.lean` and `lean/VE/Service/Registry.lean` (one mode); `lean/VE/Service/RegistryExamples.lean` (the `#guard`'s mode count); `lean/VE/EnglishGrammar/Run.lean` (one code hunk: eight `codeClasses` rows, english.statement's status-code table, field table and unsentenced set, and their lines in the `english.grammar` export; spec M8, M9); `tools/english_codes.py` (`from_lean` and `render`: the export's new members, which it would otherwise not copy into `codes.json`; spec M9); `ve/english_grammar/__init__.py` (their reader beside `codes()`); `lean/ResponseShape/Schemas.lean` (the shape's import); `lean/ResponseShape/Skeletons.lean` (the mode's skeleton and case); `lean/ResponseShape/Encoders.lean` (the import and the mode's case of the every-mode theorem); `ve/backends/lean_service.py` (`DEADLINES`: the mode's entry); `lean/VE/Audit.lean` (`runMode_englishStatement` and the new theorems' `#print axioms` lines); `lean/ResponseShapeAudit.lean` (`statementCaseReported_fits`); possibly `lean/VE/EnglishGrammar/Norm/Rules.lean` (OPEN-2: one hunk, counted in EN-2's R16 total); `lean/VE.lean` (imports of `Norm/Owners`, `Norm/Run` and their examples, appended); `tools/layer_policy.py` (`VE.EnglishGrammar.Norm.RunExamples` joins the runner-boundary fixtures of :161, since it imports the layer-4 `Norm.Run`); `tools/relay_mutation_gate.py` (`SERVICE_READERS`: the relay's reader); `tools/relay-gate-allow.json` (what stays accepted by design); `ve/norm_english.py` (relay hunk, shadow only); `tests/test_lean_service.py` (`_SCHEMA_SEEDS`: the mode's seed, and the mode in the `wrong-row-type` list); `tests/test_relay_binding_inventory.py` (rows, D9); `tests/data/route-cases.jsonl` (appended fixtures) | `ve/backends/lean_service_schema/english.statement.json` (the english.statement schema), `ve/english_grammar/codes.json`, the mode inventory, `tests/data/relay-gate-cases.jsonl` (`tools/relay_mutation_gate.py --record`: the route's `ok` fixture), `tools/trust-classes.json` and `docs/trust-baseline.json` (by `tools/trust_map.py`; the allowance carries the DRI's signature) |
| EN-3 | `lean/VE/EnglishGrammar/Run.lean` (one hunk: its four codes, `rendered`, and the render codes in the status-code table); `lean/VE/EnglishGrammar/Norm/Run.lean` (kind `render`: request, decoder, encoder, and the dispatch on `kind`); `lean/VE/EnglishGrammar/Norm/RunExamples.lean` (fixture E15: the render decoder exists only at EN-3); `lean/ResponseShape/Schemas/EnglishStatement.lean` (`rendered` and kind `render`'s rows); `lean/ResponseShape/Encoders/EnglishStatement.lean` (`statementCaseReported_fits` over both kinds, `render_fits`); `lean/VE/Audit.lean` and `lean/ResponseShapeAudit.lean` (EN-3's theorems, `render_fits`); `lean/VE.lean` (imports of `Norm/Render` and its examples, appended); `tools/layer_policy.py` (`VE.EnglishGrammar.Norm.Render` gets a layer-4 row, since `renderFields` reads `Run.status` and `Run.coded`; `VE.EnglishGrammar.Norm.RenderExamples` joins the runner-boundary fixtures of :161, since R10 reads `statementStatusCodes` in the layer-4 `Run.lean`); `ve/norm_english.py` (deletions, the W1 and render relays); `ve/assurance-manifest.json` (`english.statement` W1 part); `conformance/binding_probes.py` (`BUILDERS`: one hand-written accepted case for each of `english.statement.w1`'s binding keys, kinds `blocks` and `render`, since `tests/test_assurance_manifest.py:416` requires the keys to equal the manifest's exactly; spec 2.5); `docs/lean-first/e2/LEDGER.md` (deletion rows, and the EN-4 row for `_consequence`, `_parse_guard` and `render_rule_sentence`'s soft branch); `tools/relay_mutation_gate.py` (`SERVICE_READERS`: the render relay's reader); `tools/relay-gate-allow.json` (kind `render`'s rows); `tests/test_english_e2_ledger_sites.py` (`KEPT`: `parse_english`'s site goes, `_parse_guard`'s stays); `tests/test_norm_english.py` (`_block_grammar`'s import at `:8` and its test at `:33-37` go, or the module fails at collection; the `match`es on deleted texts; EN-3's tests, spec 2.5); `tests/test_english_unambiguity.py` (W1's half, `:292`); `tests/test_numeral_conversion.py` (W1's half, `:111-115`); `tests/test_risk_english.py` and `tests/test_alternatives_profile.py` (rule guards' `match`es on Python's advice); `tests/test_english_statement_answer.py` (kind `render`'s fuzz tests, P1 and P4); `tests/test_english_statement_shadow.py` (the shadow goes, its saved-evidence tests stay); `tests/test_relay_binding_inventory.py` (kind `render`'s rows); `tests/data/route-cases.jsonl` (R-rt fixtures, appended) | `ve/backends/lean_service_schema/english.statement.json` (regenerated for kind `render`), `ve/english_grammar/codes.json`, `tests/data/relay-gate-cases.jsonl` (`tools/relay_mutation_gate.py --record`: kind `render`'s answers), `tools/trust-classes.json` and `docs/trust-baseline.json` (by `tools/trust_map.py`; the allowance carries the DRI's signature) |
| EN-4 | `ve/norm_english.py`, `ve/surface/softnorms.py` (deletions of the norm-block frames only, not weighing's); `ve/assurance-manifest.json`; `docs/lean-first/e2/LEDGER.md` (the EN-4 row's deletions); `tests/test_english_e2_ledger_sites.py` (`KEPT`: `_parse_guard`'s site goes); `tests/test_english_unambiguity.py` (`:377`, the soft reader's text); `tests/test_numeral_conversion.py` (the soft half, `:116-121`); `tools/inventory_lint.py` (`EXCEPTIONS`: `_parse_guard`'s row goes) | as EN-1 (table rows) |
| EN-5 to EN-9 | `lean/VE/EnglishGrammar/SourceWords.lean` (this plan's own rows only, in separate hunks); `lean/VE/Audit.lean` | `Fixed/Norms.lean`, `LOCK.json` |
| EN-10 | `usecases/anthropic-rsp/measure.py`, `usecases/safety-framework/measure_r2.py`, the PF measure script once it exists; `ve/norm_english.py` (relay of the `check` kind) | `docs/usecases/safetyfw/*/units.json`, `gaps.json` (each by its own script) |

## 3. Batches in detail

### EN-0. Statement spec, stub, computed fixtures, statement review (planner, 3-4 h)

**What:**
- Write `docs/spec/en-e3-norm.md`, the statement spec. Elaborate every Lean block of this plan against main with a
  stub: each statement as a `Prop`-valued definition or `#guard`, with no product file changed.
- Record every correction the elaboration forces.
- Compute the fixtures:
  - For each of the 120 pinned rule blocks, run Python's current `parse_english` once and save the node:
    `tests/data/norm-blocks/rsp.jsonl` (76) and `fsf.jsonl` (44), with the source block's text and the git commit.
  - Collect the constitution's rule units with an English round trip into `constitution.jsonl`. The count is recorded,
    not estimated.
  - Write the expected outcome of every source fixture named in EN-5 to EN-9 by hand, from the rules below.
- The statement review covers the spec and this plan together.
- Decide the `Catalogue.lean` question of section 2.2.
- Per the DRI (2026-11-02, item 2), `docs/spec/en-e3-norm.md` states EN-2 and EN-3 against main. EN-1's statements
  are `docs/spec/english-lean-s6.md` and are not re-specified.

**Moves:** 0 B. The baseline is 0 of 120 blocks read by Lean.

### EN-1. Authored W1 rule blocks in Lean (Lean, 5-6 h)

**Done by en-s6 (merged) and en-s6b (building).** The statements are main's `docs/spec/english-lean-s6.md` (reviewed:
spec-el-s6 FIX, then spec-el-s6-r2 PASS). They supersede this section's sketch, which stays as draft 1 wrote it and is
not re-specified. The EN-0 corrections that touch EN-1, checked against `english-lean-s6.md` and
`lean/VE/EnglishGrammar/Norm/` on main:
- Sentence events plus block assembly instead of one rule per sentence: **done in EN-1** (`english-lean-s6.md` R1:
  `Piece`, `assemble`; on main in `Norm/Value.lean`).
- Plain roles beside the modal words: **done in EN-1** (R2: `Polarity.plain`).
- A seeded mutation that flips a real sign: **done in EN-1** (`english-lean-s6.md` 6: `.mustNot` mapped to `true` in
  `Force.sign`; f1, f2 and f21 fail). This section's swap of `needNot` and `mustNot` changes nothing and is not used.
- `VE.Acts.Op`/`opOf` instead of `Force`: not done (main's `Force` restates `Op` without `right`). **EN-2's first
  step**: `Force.op`, `Polarity.op?` and `opOf_agrees`; fixtures O1 and O2.
- soft-norms' `Mode`: not done (main's `Mode.default` carries the decider). **EN-2's first step**: `Mode.soft` and
  `soft_strict_iff`; the decider stays exception data (EN-4's notes); fixture O3.
- A source view over `Lexicon.aliases`: not done (EN-1 reads no source). **EN-2's first step**: `sourceView` and
  `sourceView_nil`; fixtures O4 and O5. EN-5 reads it instead of `SourceLexicon.spellings`.
- A clause with an unformalised span never reaches `toNode`: not in EN-1's statements (`Clause.toNode` has no gate;
  `readNorm_authoring` proves every authored clause has none). **EN-2's first step**: `UnformalisedSpan`,
  `Clause.toNodeChecked` and `toNodesChecked`; fixtures O6 and O7.

No merged statement is edited. The names, statements and fixtures are in `docs/spec/en-e3-norm.md` section 2.2.

**What:**
- The W1 rule-block surface of `ve/norm_english.py:207-245`, as grammar rows:
  - `Rule <n>.`, `Rule <n> (exception to rule <m>).`, `Rule <n> (exception to rules <m>, <k> and <j>).`;
  - the standalone `Rule <n> takes precedence over rule <m>.`;
  - the consequence;
  - `, if <formula>`, `, unless <formula>`, `, except when <formula>`;
  - `Except when <formula>.`.
- The consequence rows are generated from the regulated predicates and the four modal words, as `_consequence` does
  today (`:90-109`):
  - `Every <noun> must|need not|may|must not <act>`;
  - the "any" variant for a second slot;
  - `No <noun> may` for a permission rule of sign false;
  - the plain-role wordings.
- Actions build a `NormStatement`.
- A block's sentences are read in order, with the rule number and the clause carried in the state (`readDocument`).
- No mode, no relay, no Python change.

**Files (new):**
- `lean/VE/EnglishGrammar/Norm/Value.lean`, `Norm/Rules.lean`, `Norm/Read.lean`, `Norm/Elab.lean`,
  `Norm/Examples.lean`;
- `ve/english_grammar/norms@0.json` (the table source);
- the generated `lean/VE/EnglishGrammar/Fixed/Norms.lean`;
- `tests/test_english_statement_blocks.py` (reads the EN-0 fixtures through `lake env` and compares).

Shared files: section 2.2.

**Lean (Value.lean):**

```lean
namespace VE.EnglishGrammar.Norm

/-- The four W1 modal words (`VE.Acts.Op` without `right`). -/
inductive Force where
  | must | needNot | may | mustNot
  deriving DecidableEq, Repr

/-- W1's stored sign: obligation `must` true, `need not` false; permission `may` true, `must not` false
(`ve/norm_english.py:97-100`). -/
def Force.sign : Force → Bool
  | .must => true | .needNot => false | .may => true | .mustNot => false

/-- `strict` is W1; `default d` is a soft-norms default rule whose exception `d` decides. -/
inductive Mode where
  | strict
  | default (decider : String)
  deriving DecidableEq, Repr

/-- Whom a clause binds, as read (D8). -/
inductive Bearer where
  | every (sort : String)     -- "Every <noun>", "No <noun> may"
  | named (const : String)    -- a declared constant or organ: "The RSO", "OpenAI Leadership"
  | author                    -- "we", only through the one pronoun legend (CM-1's move)
  | unstated                  -- an agentless passive: "<x> will be <done>"
  deriving DecidableEq, Repr

/-- Where a residual phrase stands in the one parse (D5). -/
inductive Place where
  | act | guard | carveOut | bearer
  deriving DecidableEq, Repr

/-- A phrase the reader parses and does not formalise (D5, EN-7). Empty in authoring mode. -/
structure Residual where
  start : Nat
  stop : Nat
  row : String     -- the matched `SourceWordRow`'s key, rendered "word|frame|profile"
  owner : String   -- that row's `owner`, e.g. "ET-T1", "W6", "QT-A6", or "en-e3-norm" for a pending refusal
  place : Place
  deriving DecidableEq, Repr

/-- One reading of one norm clause. -/
structure Clause where
  bearer : Bearer
  force : Force
  mode : Mode
  pred : String               -- the regulated predicate the act wording names
  args : List ETerm           -- the act's other slots
  guard : EFormula            -- the conjunction of its conditions; `.top` when none
  carveOuts : List EFormula   -- unless / except when
  residuals : List Residual
  deriving DecidableEq, Repr

structure Header where
  number : Nat
  exceptionTo : List Nat
  deriving DecidableEq, Repr

inductive NormStatement where
  | rule (h : Header) (c : Clause)   -- one authored block
  | precedence (n m : Nat)           -- "Rule n takes precedence over rule m."
  | source (cs : List Clause)        -- one source sentence: its clauses (EN-5, EN-8)
  deriving DecidableEq, Repr

def NormStatement.clauses : NormStatement → List Clause
  | .rule _ c => [c] | .precedence _ _ => [] | .source cs => cs
```

**Lean (Rules.lean):**

```lean
/-- The norm grammar: `grammar E L`'s rules unchanged and first, then the norm table's rows and the consequence rows
generated from the regulated predicates; its start symbol is the norm block's sentence. -/
def normGrammar (E : Env) (L : Lexicon) : Grammar Terminal
/-- `acts E L` first, then the norm actions. -/
def normActs (E : Env) (L : Lexicon) : Array (Action sig)
/-- `ty E L` on the old nonterminals; the norm types on the new ones. -/
def normTy (E : Env) (L : Lexicon) : Nat → Ty

/-- The identity renaming, from `grammar E L` into `normGrammar E L` with its start set to the old one. -/
def prefixMap : VE.Grammar.RuleMap := ⟨id, id⟩

theorem prefixMap_ok (E : Env) (L : Lexicon) :
    prefixMap.Ok (grammar E L) { normGrammar E L with start := (grammar E L).start } (acts E L) (normActs E L)

/-- D2: a condition is the formula grammar's own reading. A tree that derives an old symbol derives it in the norm
grammar, with the same value. (From `rule_map_sem`, `Extension.lean:139`, and `prefixMap.tree t = t`;
`Tree.derives` does not read `start`.) -/
theorem condition_same (E : Env) (L : Lexicon) (X : VE.Grammar.Sym Terminal) (t : VE.Grammar.Tree Tok)
    (h : t.derives (grammar E L) X = true) :
    t.derives (normGrammar E L) X = true ∧
    t.sem (normGrammar E L) sig (normActs E L) = t.sem (grammar E L) sig (acts E L)
```

`readNorm` checks `normGrammar E L`'s well-formedness and typing at run time, as `read` does for `grammar E L`
(`Read.lean:39-41`). So no general well-formedness theorem is needed.

**Lean (Read.lean):**

```lean
/-- The value of a whole norm sentence; the state threads the block (rule number, clause so far) and the formula
grammar's referents. -/
structure NState where
  base : DState
  block : Option (Header × Option Clause)
  deriving DecidableEq, Repr

def NState.init : NState := ⟨DState.init, none⟩

def normMeaning (G : VE.Grammar.Grammar Terminal) (acts : Array (VE.Grammar.Action sig)) :
    VE.Grammar.Meaning Tok NState Reject NormStatement

inductive NormOutcome where
  | ok (rs : List NormStatement)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (why : String)   -- the index of the first sentence with no, two or a rejected reading
  | budget
  deriving Repr

/-- Authoring mode: a block text (one or more rule blocks and precedence lines) with exactly one reading per sentence,
or the first failure. -/
def readNorm (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : NormOutcome

def NormOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List NormStatement) : Prop :=
  L.valid E O = true ∧ ∃ sents st2, lex s = .ok sents ∧
    VE.Grammar.DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init
      (sents.map (·.toList)) (rs.map (·, false)) st2

theorem readNorm_sound : readNorm E O L b s = .ok rs → NormOneReading E O L s rs          -- from `doc_sound`
theorem readNorm_unique : NormOneReading E O L s rs → NormOneReading E O L s rs2 → rs2 = rs   -- from `doc_unique`
theorem readNorm_complete : NormOneReading E O L s rs →
    readNorm E O L b s = .ok rs ∨ (∃ i, readNorm E O L b s = .stopped i "budget") ∨ readNorm E O L b s = .budget
                                                                                          -- from `doc_complete`
/-- Rule numbers run 1, 2, … in block order; a precedence line names existing rules (`ve/norm_english.py:293-306`). -/
theorem readNorm_numbered (h : readNorm E O L b s = .ok rs) :
    (rs.filterMap fun | .rule h _ => some h.number | _ => none) = List.range' 1 (ruleCount rs) ∧
    ∀ n m, .precedence n m ∈ rs → 1 ≤ n ∧ n ≤ ruleCount rs ∧ 1 ≤ m ∧ m ≤ ruleCount rs
```

**Lean (Elab.lean):**

```lean
/-- The rule's wire object, exactly the document wire's `norm` content:
`{"name", "predicate", "sign", "guard", "unless", "over"}`. -/
def Clause.wire (name : String) (over : List String) (c : Clause) : Lean.Json

/-- D4: a W1 node only through the one decoder. -/
def Clause.toNode (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  VE.Norms.Wire.decodeNorm (c.wire name over)

/-- The decoder keeps what the reader read. Proved from `decodeNorm`'s field reads; if the proof exceeds the batch,
EN-0 moves it to a `#guard` over every fixture and records that it did. -/
theorem toNode_fields (h : c.toNode n o = .ok nd) :
    nd.name = n ∧ nd.pred = c.pred ∧ nd.sign = c.force.sign ∧ nd.over = o
```

**Fixtures** (`Norm/Examples.lean`, `#guard`, plus the 120 recorded blocks):
- From the RSP's `rules.d1.ve` (`:16`, `:22`, `:28`, `:40`):
  - "Rule 1. Every situation must have the Frontier Safety Roadmap maintained." (f6-maintain);
  - "Rule 1. Every situation must have past Roadmaps kept available." (f6-keep-past);
  - "Rule 1. Every situation is classified as \"in_scope\", if that situation is classified as \"publicly_deployed\"."
    (f8-public, a plain role);
  - "Rule 1. Every situation must have the deviation reported, if both that situation is classified as
    \"describes_mitigation_and_deviates\" and that situation is noteworthy." (f10-in-line).
- From the constitution: "Rule 1. Every instance of Claude must not directly deny being Claude." (u0125.s04.p2's
  reading, permission predicate, sign false).
- Refused:
  - "Rule 2. Every situation must have past Roadmaps kept available." as the first block (`Expected Rule 1 with its
    own block`, english-lean S2 fixture n1);
  - a consequence with an undeclared act;
  - a condition with two derivations (both trees shown);
  - "Rule 1 takes precedence over rule 3." with two rules.

**Seeded bug:** swap `needNot` and `mustNot` in `Force.sign`. The constitution fixture and its recorded node fail;
restore. A second one: drop the carve-out in the `, unless` action. The carve-out fixture fails; restore.

**Deleted, not duplicated:** nothing is deleted yet; EN-3 deletes.
- The consequence rows are generated from the same declarations as Python's `_consequence`. Its W1 call sites go at
  EN-3; the function stays, for the soft path, until EN-4 (spec 2.5).
- The formula grammar is reused unchanged (`condition_same`).

**Moves:** 103 of the 120 pinned blocks read in Lean to Python's node (expected; any disagreement is EN-2's delta).

### EN-2. Mode `english.statement`, shadow, delta report (Lean runner, shape, Python relay, 5-6 h)

**What:** a relayed Lean route by `docs/ROUTE-RECIPE.md`, mode `english.statement`.

**First step: the EN-0 corrections that EN-1 does not do** (`Norm/Owners.lean`, new; spec 2.2). No merged statement
changes.
- `Force.op`, `Polarity.op?` and `opOf_agrees`: a consequence's sign is act phrases' op (`VE.Acts.opOf`). Fixtures:
  O1 (the six fitting role and polarity pairs agree) and O2 (outside the premise they differ).
- `Mode.soft` and `soft_strict_iff`: a clause's mode is soft-norms' `Mode`; the decider is exception data. Fixture O3.
- `sourceView` and `sourceView_nil`: source spellings are aliases, checked by V1-V5. Fixtures O4 (a fresh spelling is
  valid; a spelling equal to another predicate's wording fails V4) and O5 (a spelling in the lexicon only fails V2).
- `UnformalisedSpan`, `Clause.toNodeChecked` and `toNodesChecked`: a clause with a span never becomes a node.
  Fixtures O6 (a clause without spans gives its node) and O7 (with a span, the refusal `UnformalisedSpan`).

**The seven recipe steps:**
1. `Norm/Run.lean`, the runner: the request carries the environment, overlay, lexicon, budget and text, and the
   answer gives each sentence's statement, with each rule block's byte span from the lexer's sentence positions, or
   the first stop with its code (spec 2.3).
2. `lean/ResponseShape/Schemas/EnglishStatement.lean`, the shape; its members per status are english.statement's own
   field table (`statementFields`), defined in Lean beside `statementStatusCodes` and exported by `english.grammar` to
   `ve/english_grammar/codes.json`.
3. `lean/ResponseShape/Encoders/EnglishStatement.lean`, the encoder theorem.
4. The generated `ve/backends/lean_service_schema/english.statement.json` and `ve/english_grammar/codes.json`, whose
   new members `tools/english_codes.py` must be taught to copy (spec M9).
5. `ve/norm_english.py` `parse_english` calls Lean in shadow through `ve/backends/relay.py` and compares Lean's nodes
   with its own, only when `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` are both set (spec 2.4);
   `ve/backends/service_schema.py` checks the typed answer.
6. Fixtures recorded in `tests/data/route-cases.jsonl`, and the relay mutation gate's in
   `tests/data/relay-gate-cases.jsonl`.
7. Fuzz tests `tests/test_english_statement_answer.py`, which retype and rebind every field, each rule row's `span`
   included. `tests/test_lean_service.py`'s `_SCHEMA_SEEDS` gains the mode's seed.

The relay binds the answer to the request: every rule number and span it names exists in the request, and no block
row is empty or extra. Each rule row has exactly one span, inside the source, on UTF-8 character boundaries, and the
spans increase without overlapping. The relay has no layout check (spec 2.4).

**Delta report** (`docs/en-e3-norm/en-2/DELTA.md` and `delta.json`, saved evidence):
- every disagreement between Python and Lean over the whole recorded corpus: tests, the soft and rights calls that
  reach the W1 path with `_w1=True` (`ve/norm_english.py:542`, `:613`, through `ve/surface/rights.py:44`), the 120
  pinned blocks, and the constitution and UDHR units;
- classified as `lean-unavailable` (listed by id; tested first, so a `CheckerUnavailable` answer is always a delta
  row), or else `agree`, `lean-unknown` (Lean's `budget` or a ResourceLimit code), `lean-stricter` (a changed
  rejection), `lean-looser`, `different-node` or `both-refuse`; each record has exactly one class (spec 2.4);
- every block that Lean answers `NodeRefused` or `NodeLimit`.

The DRI decides every row that is not `agree` or `both-refuse` (english-lean S6 gate; spec section 6).
- `lean-unknown` rows have their own section and are not decided as rejections; `lean-unavailable` rows are decided
  each, unless there are none. The layout rows are decided here, and a refused layout is a Lean code.
- That decision, once for the W1 layer, is the stop point between EN-2 and EN-3. No other signature is reserved.
- EN-2 changes no route's answer: Python's reader still decides.

**Tests the en-e3 task file keeps and adds** (DRI 2026-11-02, item 2):
- `tests/test_english_statement_blocks.py` (the 120-block comparison) stays selected;
- `tests/test_english_statement_shadow.py`, the shadow agreement test: it reads the saved delta evidence
  (`docs/en-e3-norm/en-2/delta.json`) and checks that every disagreement the shadow log records over the pinned blocks
  is a row of DELTA.md with its class, and that every record has exactly one class. It also checks that with the
  comparator flag set and `VE_SHADOW_LOG` unset, Lean is not called and no file is written in the working directory.

**Lean** (bound in the spec as `Run.statementCase`, `answer_one_iff` and `answer_one_rows`, spec 2.3):

```lean
/-- The mode's answer: Lean's outcome, encoded; the encoder theorem is the recipe's step 3. -/
def runStatement (req : Lean.Json) : Lean.Json
theorem runStatement_ok_reads (h : decodeRequest req = .ok (E, O, L, b, s))
    (hr : readNorm E O L b s = .ok rs) : answerStatements (runStatement req) = some (rs.map NormStatement.encode)
```

**Fixtures:** the 120 blocks through the mode; one request with a stale environment (refused); one with an ambiguous
condition (stopped, both trees in the answer).

**Seeded bugs:**
- Python: let the relay accept an answer with one block row more than the request. The fuzz test fails; restore.
- Lean: let the runner answer `ok` when `readNorm` stops. The route fixture fails; restore.

**Deleted, not duplicated:** nothing yet. Python's reader still decides (shadow).

**Moves:** the shadow agreement count over the corpus (measured, in DELTA.md).

### EN-3. Authority for W1 blocks, Lean rendering, Python's W1 matcher deleted (Lean and Python, 4-5 h)

**Needs:** the DRI's decision on EN-2's delta.

**What:**
- `english.statement`'s W1 part becomes Lean's: manifest `authority: lean`, bindings to `readNorm` and `renderChecked`.
- Rule-block English for display comes from Lean, checked by reading it back (english-lean 3.5's per-output check).
- The rendering has its numbering context and the check reads the whole document back (design debate round 3).
  Draft 1's per-block check cannot hold: "Rule 1." and its rule sentence are two sentences, and a lone "Rule 2" is
  refused by `readNorm_numbered`.
- The guard and carve-out English come from Python's formula renderer (`_guard_text`), as an untrusted producer: main
  has no Lean formula renderer, and the read-back makes a wrong text fail.

**Lean (Norm/Render.lean):**

```lean
/-- The English of a W1 document: rule i is numbered i, each `over` entry is its target's number in the header,
the consequence is the first of en-s6b's wordings for the predicate and sign, and the guard and carve-out texts are
the producer's. -/
def renderDocument (E : Env) (L : Lexicon) (nds : List VE.Norms.Node) (gs : List GuardTexts) : Except String String

/-- The rendered text, only if Lean reads the whole text back to the document's rules, renumbered by position. -/
def renderChecked (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node) (gs : List GuardTexts) :
    Except String String

theorem renderChecked_reads_back (h : renderChecked E O L b nds gs = .ok s) :
    ∃ rs want, numbered nds = .ok want ∧ readNorm E O L b s = .ok rs ∧ toNodesChecked rs = .ok want ∧
      renderDocument E L nds gs = .ok s
```

Kind `render` of the mode has its own request, `{id, environment, lexicon, kind: "render", rules, guard_texts}` plus
the optional members; the decoder refuses any extra member and any other kind, and the runner dispatches on `kind`.
`render_fits` states that its rows fit and that every refusal code is in the table (spec 2.5, section 4). The relay
binds a `rendered` answer: one block per rule, no empty header or sentence, no extra row. The decoder's fixture E15
joins `Norm/RunExamples.lean` here. `Norm/Render.lean` and `Norm/RenderExamples.lean` read the layer-4 `Run.lean`, so
`tools/layer_policy.py` places both in layer 4 (spec 2.5).

R6 covers only the trusted Lean lines that replace the deleted W1 path below: `Norm/Render.lean`'s frame and
`Norm/Run.lean`'s render kind (request, decoder, encoder). Other new trusted lines go under R16 (D10). EN-2's lines were
counted under R16 at EN-2's merge, and en-s6b's at en-s6b's.

**Callers** (spec 2.5): the `_w1=True` calls of `_parse_soft_english` (`:542`) and `_render_soft_english` (`:613`),
reached through `ve/surface/rights.py:44`, go to Lean at EN-3; they are in EN-2's shadow corpus. `_consequence`
(called from `:378`, `:399`, `:621` and `ve/surface/rights.py:119`) and the soft branch of `render_rule_sentence`
(called from `rights.py`, `document/render.py` and `readings_route.py:1185`) stay until EN-4, under an E2 ledger row.
So does `_parse_guard` (`:54-73`), which `_parse_soft_notes` (`:468`) still calls. Only the W1 call sites of
`_consequence` and `_parse_guard` (`:339-340`) go.

**Deleted** from `ve/norm_english.py` (spec 2.5):
- `:283-296` (the line split, the standalone precedence regex and its `require_unique_derivation` call, the
  `UnknownRule` display check), `:303-305` (the `_HEADER` match), `:323-342` (the reference parse, the clause string
  splits, the consequence and guard parses, the block's `require_unique_derivation` call) and `:346-347` (the second
  `UnknownRule` check);
- `_HEADER` (`:207`), `_parse_consequence` (`:248-268`), and `_block_grammar` and its Lark audit (`:210-245`).

Rewritten: `:297-322`, the block count, the renaming and the manifest's block mapping, checked against Lean's rows:
the blocks are the source's substrings at Lean's spans, and each entry's span must equal both Lean's span in code
points and `:314`'s offset over those blocks. The manifest checks run only on `one`; on any other status Python
relays Lean's refusal. `:343-349` builds the norms from Lean's nodes.

`parse_english` becomes the relay: identity checks of the export manifest stay in Python, as request binding. The E2
deletion ledger (`docs/lean-first/e2/LEDGER.md`) records the rows. `EnglishParser` stays only for the layers not yet
moved: soft blocks until EN-4, legends, reports and others (english-lean S7 decides its retirement).

`tools/relay_lint.py` does not change: `RELAYED_FUNCTIONS` gains neither relay, because both keep raises with their own
text (the manifest checks, `GuardOnOwnOutcome` and the handle check; spec 2.5).

**Tests:** a test asserts that `ve/norm_english.py` has no block parser left (no `_parse_consequence`, no Lark grammar
for blocks, no `_HEADER`, no W1 call of `_consequence` or `_parse_guard`); it does not require either function to be
absent. A soft block with a "Rule n is excepted when …" note still reads, through `_parse_soft_notes` and
`_parse_guard`. The relay fixtures P1 to P4 of the spec (render binding, span binding, manifest).

Existing tests that pin what a deleted line did move to Lean's class and text (spec 2.5): `tests/test_norm_english.py`,
which fails at collection until its `_block_grammar` import goes, `tests/test_english_unambiguity.py`,
`tests/test_numeral_conversion.py`, `tests/test_risk_english.py` and `tests/test_alternatives_profile.py`.

**Seeded bugs:**
- Python keeps a fallback to its own parser when Lean is unavailable. The test fails: Lean unavailable must give
  `CheckerUnavailable`, never a Python reading. Restore.
- Python deletes `_parse_guard` with the W1 path. The soft-note test fails. Restore.

**Moves:** the authority of `english.statement`'s W1 part: python → lean. Status bytes: 0.

### EN-4. Soft rule blocks (Lean and Python, 5-6 h)

**Needs:**
- EN-3;
- `feature/rd9-docroute` merged;
- DF-4's rows in `SourceWords.lean`, so that "normally", "typically", "usually" and "as a rule" are refused through
  their owner's row, not through `ve/norm_english.py:422`'s list.

**What:** the soft surface of `ve/norm_english.py:376-550`, as grammar rows:
- the default consequences "should", "should not", "generally may", "generally need not", "generally must",
  "generally must not";
- the notes:
  - "Rule <n> serves <rank>.";
  - "Rule <n> is excepted when <formula>." and "Rule <n> is excepted only when <formula>.";
  - "The exception to rule <n> is decided by <decider>.";
  - "The exception to rule <n> takes account of <factors>.";
- the header's party options.

Output goes through soft-norms' decoder.

**Lean (Norm/Soft.lean):**

```lean
structure SoftNotes where
  rank : Option String
  decidedBy : Option String
  sufficient : List EFormula
  necessary : List EFormula
  factors : List String
  deriving DecidableEq, Repr

/-- D4: a default rule only through soft-norms' decoder, `VE.SoftNorms.Wire.decodeSoftNorm (se : SoftEnvironment)
(j : Json)` (`SoftNorms/Wire.lean:69`), with the environment it takes. The wire's mode is `c.mode.soft` (soft-norms'
`Mode`); the decider is `n.decidedBy`. A clause with an unformalised span is refused first, as `toNodeChecked` does. -/
def Clause.toSoft (se : VE.SoftNorms.Wire.SoftEnvironment) (name : String) (over : List String) (n : SoftNotes)
    (c : Clause) : Except String VE.SoftNorms.SoftNode :=
  if c.residuals.isEmpty then VE.SoftNorms.Wire.decodeSoftNorm se (c.softWire name over n)
  else .error (unformalisedText c.residuals.length)

/-- A strict rule carries no exception decision (`ve/norm_english.py:535-537`). -/
theorem strict_no_notes (h : readNorm E O L b s = .ok rs) (hc : .rule hd c ∈ rs) (hm : c.mode = .strict) :
    notesOf rs hd.number = none
```

**Fixtures:**
- "Rule 1. Every situation should advance the industry-wide recommendations." (RSP `rules.d1.ve:14`, s1-advance-default);
- the 12 RSP and 5 FSF "should" blocks;
- a block with "The exception to rule 1 is decided by \"company\".";
- "Rule 1. Every situation should usually …", refused with DF-4's row code.

**Disjoint from weighing:** "Safety always outranks ethics." and "Safety outranks ethics." (the weighing refresh's
C-2 pair) are not read as norm blocks. If en-wg has landed, each has exactly one derivation, a weighing one.

**Seeded bug:** read "generally may" as strict. Its fixture fails; restore.

**Deleted** (Python):
- `_soft_consequence`, `_soft_rewrite_consequence`, `_parse_soft_notes` and `_parse_soft_english`'s rewriting;
- `_consequence`, `_parse_guard` and the soft branch of `render_rule_sentence`, kept by EN-3 for the soft path under an
  E2 ledger row;
- the regexes `_SOFT_NOTE`, `_SOFT_DECIDER`, `_SOFT_FACTORS`, `_SOFT_HEADER`;
- the hard-coded frequency-word refusal.

`ve/surface/softnorms.py` loses only the norm-block frames; weighing's frames are en-wg's.

**Moves:** Lean-read rule English on every formal norm unit (measured from the ledgers, research 2.3): RSP 17,589 B,
FSF 7,923 B. Status bytes: 0.

### EN-5. Translation mode: one structure, force rows, source spellings (Lean, 5-6 h)

**Needs:**
- EN-3;
- en-sw merged;
- the R1 rows: "must", "must not", "should", "should not", "may", "may not", "need not", "is required to", "are
  required to", "shall", "shall not", "should never", each with its owner's candidates (section 7);
- the fidelity paper pilot (fp-en-e3-norm) with RESULT.md saying CONTINUE (section 1, order item 4).

**What:** a source sentence's frame:
- optional connective ("Additionally,", "Finally,", "However,", "In addition,");
- a bearer: a declared constant or organ, "Every/each <noun>", "No <noun>", or a bare plural through a row;
- a force word through a row;
- an act: a declared wording or source spelling, with argument fillers;
- optional conditions "if/when/where <formula>," (leading) or ", if/when/where <formula>" (trailing);
- optional ", unless <formula>";
- a final ".".

How it is read:
- The sentence must have exactly one structure.
- Each matched readings-row gives its candidates as authored wordings, which `readNorm` reads (D3).
- A refuse-row gives the row's code and advice.
- Connectives are read and recorded, and add no rule content. Their presuppositions are presupposition's.

**Lean (Norm/Source.lean):**

```lean
/-- D7: the source spellings `A` are aliases of the source view (`sourceView`, EN-2's first step), so V1-V5 check
them; draft 1's `SourceLexicon` is dropped. Valid: `Lexicon.valid` of the view, act phrases' lexical checks on each
spelling, and no spelling contains a word of a row in `R` that is not `fixed` (D5). -/
def sourceValid (E : Env) (O : Overlay) (L : Lexicon) (A : List (String × String × Bool)) (R : List SourceWordRow) :
    Bool

theorem spelling_has_no_row_word (hv : sourceValid E O L A R = true) (hp : (p, w, neg) ∈ A)
    (row : SourceWordRow) (hr : row ∈ R) (hk : ∀ x, row.kind ≠ .fixed x) : ¬ containsPhrase (splitWs w) (splitWs row.word)

/-- The grammar of source sentences: `normGrammar` of the view plus the source frame rows, one terminal row per row of
`R` in a norm frame. -/
def sourceGrammar (E : Env) (L : Lexicon) (R : List SourceWordRow) : VE.Grammar.Grammar Terminal

inductive CandReading where
  | rule (A : NormStatement)    -- `readNorm`'s one reading of the filled wording
  | noRule (reason : String)    -- commitments' no-rule candidate (S1), as its row names it
  | pending (code : String)     -- `readNorm` refused the filled wording, or the gate refused its route (D3)

/-- One matched readings-row of the sentence's one structure. -/
structure Slot where
  key : String
  candidates : List SourceWordReading

/-- The slot as `VE.Discourse.allChoices` reads it: id, version and number of readings (scope's `shapeOf`). -/
def slotShape (sl : Slot) : VE.Route.Admission.ReadingSet := ⟨sl.key, 0, sl.candidates.map fun _ => .top⟩

/-- Every combination, in `allChoices` order; `none` over the W2 limit (UNKNOWN). -/
def choicesOf (slots : List Slot) : Option (List VE.Discourse.Choice)

structure Candidate where
  rows : List String               -- every row that contributed, one per slot, in slot order
  choice : VE.Discourse.Choice     -- the combination it is
  wording : String                 -- the authored sentence the reader is shown
  reading : CandReading

inductive SourceOutcome where
  | one (A : NormStatement)                       -- no readings row matched; exactly one reading; no span
  | readings (cs : List Candidate)                -- a W2 authored set (PLANS-INDEX D11); one structure (D3)
  | mixed (A : NormStatement) (spans : List UnformalisedSpan)   -- D5: its own outcome, never `.one`
  | unformalised (spans : List UnformalisedSpan) (why : String)
  | parses (t u : VE.Grammar.Tree Tok)            -- two structures and no row: refused, both shown
  | refused (code advice : String)                -- a refuse row, or no derivation
  | limit                                         -- over the budget or the W2 limit: UNKNOWN

/-- `E` and `L` are the source view's. -/
def readSource (E : Env) (O : Overlay) (L : Lexicon) (R : List SourceWordRow) (b : Nat) (s : String) : SourceOutcome

/-- One structure: a reading, a set or a MIXED reading comes from the sentence's only derivation. -/
theorem source_one_structure (h : (∃ A, readSource E O L R b s = .one A) ∨
      (∃ cs, readSource E O L R b s = .readings cs) ∨ ∃ A us, readSource E O L R b s = .mixed A us) :
    ∃ w t, lexSource s = .ok w ∧ VE.Grammar.Derives (sourceGrammar E L R) (.n ntSource) w t ∧
      ∀ u, VE.Grammar.Derives (sourceGrammar E L R) (.n ntSource) w u → u = t

/-- D3: every licensed combination, in `allChoices` order (complete by `mem_allChoices`, counted by
`length_allChoices`), each recording every contributing row. -/
theorem readings_complete (h : readSource E O L R b s = .readings cs) :
    ∃ chs, choicesOf (slotsOf E L R s) = some chs ∧ cs.map (·.choice) = chs ∧ ∀ c ∈ cs, c.rows = c.choice.map (·.1)

/-- Over the W2 limit the answer is UNKNOWN, never a shortened set (as `compatible_budget`). -/
theorem readings_budget (hs : slotsOf E L R s ≠ [])
    (h : VE.Discourse.productSize ((slotsOf E L R s).map slotShape) > VE.Readings.maxChoices) :
    readSource E O L R b s = .limit

/-- D3: a rule candidate is the authoring reader's one reading of its filled wording; a pending one carries the
reader's refusal or the gate's (`routeRefusal`, never a `JoinRoute` copy). -/
theorem candidates_from_rows (h : readSource E O L R b s = .readings cs) (c : Candidate) (hc : c ∈ cs) :
    c.wording = fillHoles (slotWordings (slotsOf E L R s) c.choice) (sourceParts E L R s) ∧
    (∀ A, c.reading = .rule A → readNorm E O L b c.wording = .ok [A]) ∧
    (∀ k, c.reading = .pending k → (∀ rs, readNorm E O L b c.wording ≠ .ok rs) ∨
      routeRefusal (profilesOf c.wording) = some k)

theorem readings_two (h : readSource E O L R b s = .readings cs) : 2 ≤ cs.length

/-- D5: `.one` carries no span; MIXED carries its spans, bounded, disjoint and owned by their rows. -/
theorem one_no_spans (h : readSource E O L R b s = .one A) : ∀ cl ∈ A.clauses, cl.residuals = []

/-- Two structures are never a set. -/
theorem parses_refused (h : readSource E O L R b s = .parses t u) : t ≠ u
```

`SourceWordRow`, `SourceWordReading` and the kinds are en-sw's (`lean/VE/EnglishGrammar/SourceWords.lean`, on main
with no rows). The spec states `slotShape`, `choicesOf` and `routeRefusal` exactly and type-checks them against main
(spec 2.6).

The hole syntax in candidate wordings ("{act}", "{bearer}", "{condition}") and the norm frame keys ("norm.force",
"norm.subject", "norm.connective", "norm.modifier") are this plan's (section 9, NEW 2). Rows that use them are norm
rows.

**Fixtures (source):**
- PF line 21: "Employees must authenticate using multi-factor authentication (MFA) and managed devices meeting
  security baselines."
  - Until hedges-generics approves R2's norm-frame row against D-H4 (section 7), this fixture does not apply: the
    sentence is refused with the owner's code.
  - With the "must" row (R1) and a bare-plural row (R2), the result is `readings` with two candidates: "Every employee
    must authenticate using …" (strict) and "Every employee should authenticate using …" (default).
  - The act is a declared spelling whose "and" lies inside an acts@0 fixed phrase. acts@0 refuses soft-norms@0, which
    the default candidate needs, so until C12 the default candidate is pending with the gate's refusal,
    "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented".
- PF line 21: "Changes to critical infrastructure should undergo multi-person approval and review." gives `readings`,
  strict and default. For the same reason, the default candidate is pending until C12.
- Constitution u0125.s04.p2: "Claude should never directly deny that it is Claude" gives `readings` from the "should
  never" row: "Every instance of Claude must not directly deny being Claude." and its default twin. The audited
  translation keeps the strict reading only. EN-10 will report "set not collapsed" (D9; research 2.6).
- Refused:
  - "Risk assessment must take into account the fact that other actors may put significantly more effort into eliciting
    capabilities than we put into assessing risk, thus requiring conservatism in the form of evaluations." (FSF
    note-ml-rd-must): "may" and "more … than" are inside the act, so no clean spelling exists, and the result is
    `refused SourceSpellingHides`.
  - "We will publish a Risk Report." before EN-6 and CM-1: `refused AuthorLegendMissing`.

**Seeded bug:** let a two-candidate row return its first candidate as `.one`. The `readings_two` fixtures fail;
restore. A second one: drop the last choice vector of `choicesOf`. The two-slot fixture (four combinations) fails;
restore.

**Deleted, not duplicated:**
- The use cases' hand-written word-to-reading tables for force words: the FSF `translation.py` sets for "should" and
  "must", and the PF and RSP PLAN RS9 and RS13 word rules. These now point at the R1 rows. The PLAN tables keep their
  cited narrowings and their frozen key cells.
- CM-4 does the same for commitment words (`CM/…/commitments-PLAN.md:883-885`).

**Moves (estimate):** source-read on PF 0.3-0.8 kB, FSF 0.1-0.3 kB, and a few constitution units.

### EN-7. Unformalised spans and MIXED, a measurement only (Lean, 4-5 h)

**Needs:** EN-5. ET-5's rows where they have landed, and the amount and duration terminal classes (with QT-E,
section 2.1).

**A measurement only** (D5, DRI 2026-11-02). D5's weakening rule is removed from the product. MIXED is its own outcome
(`SourceOutcome.mixed`), never `.one`; no rule is made from a sentence with a span, and check mode answers `partial`.
The place rule below classifies MIXED for the measure and licenses nothing.

**What:** numerals, ranges ("3-6"), spelled numbers and unit words are terminal classes. The residual phrases are rows,
looked up in `R`:
- ET-5's "within", "by", "until", "since", "during", "while";
- QT-A6's "about" and "approximately", and its count words;
- QT-B3's comparatives when built.
- Words whose meaning owner has no row yet get pending refuse-rows in this plan's frame "norm.modifier", with the
  meaning owner named in the advice and in the row's `owner` field, or `unowned` with the round-2 request where no
  meaning owner exists ("promptly"); never `en-e3-norm`:
  - "every", "at least", "at most", "no later than", "no more than", "prior to", "before", "after", "following",
    "upon", "once a";
  - "quarterly", "annually", "monthly", "yearly", "regularly", "periodically", "continually", "over time",
    "promptly".
- When an owner builds a reading for one of these words, it takes that row over (section 9, NEW 4).

**The place rule** (the measure's classification). Each span's place comes from the one parse, and its restricting
mark from its row:
- MIXED only at place `act` of a `must` clause, outside negation, for a restricting row (D5).
- Anywhere else the outcome is `unformalised`: a guard, an exception, a bearer, a `may`, `need not` or `must not`
  clause, or a non-restricting row such as "at most".

**Lean (Norm/Residual.lean):**

```lean
/-- The restricting mark of the row a span matched (D5); `false` for a row this table does not mark. Recorded data;
it licenses nothing. -/
def restricting (R : List SourceWordRow) (u : UnformalisedSpan) : Bool

/-- The span's owner is its row's meaning owner (`unowned` for a placeholder row), never this plan. -/
def ownerOk (R : List SourceWordRow) (u : UnformalisedSpan) : Bool

/-- Every span is nonempty and inside the sentence, and no byte is in two spans: the read part is the rest, so the
read part and the spans partition the sentence's bytes. -/
def spansPartition (s : String) (us : List UnformalisedSpan) : Bool

/-- D5: MIXED is classified only at the act of a `must` clause, for a restricting row; it is never `.one`. -/
theorem mixed_place (h : readSource E O L R b s = .mixed A us) (u : UnformalisedSpan) (hu : u ∈ us) :
    ∃ cl ∈ A.clauses, u ∈ cl.residuals.map Residual.span ∧ u.place = .act ∧ cl.force = .modal .must ∧
      restricting R u = true

/-- Anywhere else the sentence stays UNFORMALISED, naming every span of its parse. -/
theorem span_elsewhere (ht : uniqueParse E L R s t) (u : UnformalisedSpan) (hu : u ∈ spansOf t)
    (hp : ¬ (u.place = .act ∧ forceAt t u = .modal .must ∧ restricting R u = true)) :
    ∃ us why, readSource E O L R b s = .unformalised us why ∧ u ∈ us

/-- MIXED's spans: nonempty, bounded, disjoint (a partition of the sentence's bytes), and owned by their rows. -/
theorem mixed_spans (h : readSource E O L R b s = .mixed A us) :
    us ≠ [] ∧ spansPartition s us = true ∧ ∀ u ∈ us, ownerOk R u = true
```

**Fixtures:**
- RSP s31-timing: "We will publish a Risk Report every 3-6 months." The clause "publish a Risk Report" is read; the
  residual "every 3-6 months" is placed at `act`, with owners ET-T1 and W6.
  - Before EN-6, "we" is refused; the fixture uses "The company will …" with a declared constant.
  - After EN-6, it is the source sentence itself.
- RSP s362-ask-30-days: "… within 30 days of receipt." is MIXED with residual owner ET-T1.
- FSF s51-yearly: "The Frontier Safety Framework will be reviewed at least once a year". After EN-6 (CM-4's passive
  row), it is MIXED with residual "at least once a year" (ET-T1, W6).
- RSP s4-non-disparagement: "We will not impose contractual non-disparagement obligations on employees, candidates,
  or former employees in a way that could impede or discourage them from publicly raising safety concerns about
  Anthropic." The hedged modifier sits in a `mustNot` clause, so the result is `unformalised` with the residual named
  (owner: hedges-generics and attitudes for "could", events-time-causation for the causal link).
- A guard residual, "If we determine within 30 days that …, we will …": `unformalised`.
- A non-restricting residual, "The company must review the policy at most once a year.": `unformalised`. Doing A at
  most once a year does not imply doing A.
- A permission with a residual, "The company may share the report within 30 days.": `unformalised`. A permission
  within 30 days is not a permission at any time.

**Seeded bugs:**
- Classify a span under `mustNot` as MIXED. The s4-non-disparagement fixture fails; restore.
- Mark "at most" as restricting. The "at most once a year" fixture fails; restore.
- Answer `.one` for a MIXED sentence. The s362-ask-30-days fixture fails; restore.
- Write `en-e3-norm` as a span's owner. The `ownerOk` fixture fails; restore.

**Not duplicated:** no residual is given a meaning. The owners are named in section 5.

**Moves (estimate):** MIXED: RSP 1.3-2.5 kB, PF 1-2 kB, FSF 0.4-0.6 kB. With EN-10, the 703 B of hidden atoms are
reported (measured, research 2.3).

### EN-6. Commitment rows applied; "we" through the legend; passives (Lean, 3-4 h)

**Needs:** EN-5; CM-4's rows (`CM/…/commitments-PLAN.md:833-840`) and `lean/VE/Commitments/Read.lean`'s wordings;
CM-1's move of the "we" binding. CM-4 provides rows and wordings only and runs after EN-5 (section 7, R6); any CM-4
fixture that reads a whole sentence into a rule is this batch's.

**What:**
- The frames for each CM-4 row, whose candidates are commitments' authored wordings, are read by `readNorm` extended
  with `Commitments/Read.lean`'s wording rows. The extension is a table those wordings generate, not a copy. The rows:
  - "we will <act>", "<organ> will <act>" and "<x> will be <done>";
  - the effort row ("we will try to", …);
  - the goal row;
  - the permission row ("we may <act>", "<organ> may", "<organ> can");
  - the release row ("we will not necessarily <act>");
  - "we commit to <act>".
- `Bearer.author` elaborates through the moved binding: the guard gains the binding's equation, read from the moved
  `VE.Legend` (`eqsFrom` and the binding check, `CM/…/commitments-PLAN.md:405-408`). This batch does not restate
  speech-acts' `eqGuard` (`SpeechActs/Tree.lean:115-122`).
- The no-rule candidate is commitments' S1 (`kind: "asserted"`, content top).

**Lean:**

```lean
/-- The author bearer, only through the one legend (D8): no legend, no rule. *(CM-1 binds the legend's module.)* -/
theorem author_needs_legend (h : readSource E O S R b s = .one A ∨ ∃ cs, readSource E O S R b s = .readings cs)
    (hb : ∃ cl ∈ readingsClauses (readSource E O S R b s), cl.bearer = .author) : legendOf E ≠ none
```

**Fixtures:**
- RSP s4-website: "We will maintain the current version of the RSP on our website." gives `readings` {binding:
  "We commit to maintain the current version of the RSP on our website.", noRule forecast}. Commitments' mechanism
  narrows it by the RSP's N1 (`usecases/anthropic-rsp/PLAN.md:90`).
- RSP s362-may-split: "… we may choose to split the review process across different external reviewers based on
  their subject matter expertise." gives {permission, noRule possibility}.
- RSP appa-uplevel-not-delay: "However, we will not necessarily delay AI development and deployment in this
  scenario." gives {release, noRule scopeNote}. "AI development and deployment" is a fixed phrase.
- RSP s34-usually: "We will usually also seek feedback from trusted external parties with relevant expertise." gives
  DF-4's row's set, or DF-4's refusal if its row is `refuse`.
- RSP s2-keep-past: "We will also keep past Roadmaps available at that link." gives {binding, noRule forecast}; "also"
  is a connective.
- Refused: "To avoid redundancy, we will likely analyze similar models collectively …" (attitudes' row: likelihood).

**Seeded bug:** read "We will" with no legend as an author rule. `author_needs_legend`'s fixture fails; restore.

**Not duplicated:** strengths, wordings, organs and the no-rule candidate are commitments'. This batch only reads with
them.

**Moves (estimate):** source-read: RSP 2-3.5 kB, PF 1-1.5 kB, constitution 1-2 kB.

### EN-8. Two clauses sharing a guard, numbered conditions, act joins on the norms route (Lean, 5-6 h)

**Needs:** EN-6, and EN-E2's result, which caps the attachment rows.

**What:**
- Two norm clauses joined by "and" under one leading condition give `NormStatement.source` with two clauses.
- A condition with numbered parts, "(1) <formula> and (2) <formula>", is read as their conjunction.
- Act joins are read with acts@0's grammar (AP-2) on the norms route. On the soft and readings routes they are refused
  with the gate's own refusal (`routeRefusal`: `VE.Compose.gateOf profileTable`, then `Matrix.documentRefusal` after
  PC-4) until C12's `gate_acts` revision. No `JoinRoute` code is copied.
- An "if" inside one conjunct of a joined act is refused as `parses`, unless a row of this plan's frame
  "norm.attach" licenses the set {that conjunct, every conjunct}. EN-E2's result caps such rows: only patterns seen
  three or more times on the pinned texts.

**Lean:**

```lean
/-- The clauses of one source sentence share its leading condition. -/
theorem shared_guard (h : readSource E O S R b s = .one (.source cs)) (hl : leadingCondition E S R s = some g) :
    ∀ cl ∈ cs, guardHas cl.guard g
```

**Fixtures:**
- RSP s4-notify-board with s4-may-public-notice: "If we determine that a report is (1) substantiated and (2) involves
  a material safety risk, we will promptly notify the Board and we may provide public notice of the same."
  - It gives two clauses: binding "notify the Board" with the span "promptly", owner `unowned` (no meaning owner; the
    round-2 request), and permission "provide public notice of the same".
  - "of the same" is refused (`Anaphor`) until discourse binds it. So the second clause stays UNREAD.
- RSP s361-consult: "In selecting external reviewers, we will consult with the Board and obtain the approval of the
  LTBT." gives a join of two acts on the norms route. "In selecting <np>," is a condition frame with its own row, a
  state predicate the lexicon declares.
- RSP s4-investigate: "When we receive a report, we will promptly investigate, take appropriate and proportional
  corrective action if it is substantiated, and document the report and our findings." gives `parses` (refused): the
  embedded "if" has two attachments and no row, and "it" refers back to the guard's "a report".
- PF line 14: "If we deem that a deployment warrants third party stress testing of safeguards and if high quality
  third-party testing is available, we will work with third parties to evaluate safeguards."
  - Two leading conditions give a conjunction.
  - "to evaluate safeguards" is a purpose clause, refused with purposes' code until a purpose reader exists (C21).

**Seeded bug:** attach the embedded "if" to the last conjunct silently. The s4-investigate fixture fails; restore.

**Moves (estimate):** RSP +1-2 kB, PF +0.5-1 kB, FSF +0.2 kB.

### EN-9. List items under a lead-in (Lean, 3-4 h)

**Needs:** EN-8; CM-5 (`lean/VE/Commitments/Lead.lean`, `inherited`), which needs `feature/sc-1ae` and its AR-10 row.

**What:**
- An item governed by a lead-in is read with the lead-in's bearer and row: "We will:", "We commit to the following
  governance measures …:", "We will require the following practices for High capability models:".
- An imperative item ("Ensure …", "Apply …") is read as the act of the lead-in's clause. Its restrictor ("for High
  capability models") becomes the guard over the item's bearer.
- The governor is scope's. The inherited row is commitments'. This batch only reads the item with them.

**Lean:**

```lean
/-- An item's reading uses the row its lead-in passes down, unless the item has its own (CM-5's `inherited_own`).
*(EN-0 binds `annotationRow` to the field of commitments' annotation that names its row.)* -/
theorem item_row (hg : VE.Commitments.inherited G as item = some a) (h : readItem E O S R G b item = .one A) :
    rowOfReading A = annotationRow a
```

**Fixtures:**
- PF Appendix C.3, line 21: "Ensure all access is regularly audited and reviewed." under "We will require the
  following practices for High capability models:". It gives {binding, noRule forecast}; the act "ensure all access
  is audited and reviewed" with a fixed phrase; the span "regularly" (pending, owner its row's meaning owner as section
  5 lists it, never `en-e3-norm`; MIXED as a measurement); and the guard "High capability model".
- RSP section 4: "We commit to the following governance measures to promote internal and external accountability."
  with its items. "to promote …" is a purpose clause on the lead-in: refused there, and the items are still read.
- Constitution u0230.s03 "We will:" with u0231.s01-s09: CM-0p's block.

**Moves (estimate):** PF +2-3 kB, mostly MIXED; RSP +0.8-1.5 kB; constitution 0.4-0.7 kB.

### EN-10. Check mode and the use-case accounting (Lean kind and use case, 4-5 h)

**Needs:** EN-5. It is re-run after each later batch; usecase-rsp-run and usecase-safetyfw-b are merged first.

**What:**
- Kind `check` of mode `english.statement`: the hand rule or rules of a unit, compared with `readSource`'s readings
  (D9).
- The use-case measure scripts add the D11 columns per norm unit: SOURCE-READ, SOURCE-READ-PENDING, MIXED, MISMATCH,
  or UNREAD with a code. They save them as evidence (`docs/usecases/safetyfw/*/units.json`).
- The hand side is the unit's W2 document and unit id: its fixed rule content with its soft decisions, or its W2
  authored set with the document's cited narrowings (D9).
- Hidden residuals: a hand rule whose predicate's declared wording contains a residual row's word is reported
  `mismatch [hiddenResidual w]`.

**Lean (Norm/Check.lean):**

```lean
inductive Field where
  | force | mode | sign | predicate | guard | carveOuts | setNotCollapsed | hiddenResidual (word : String)
  | bearerNote
  deriving DecidableEq, Repr

/-- NEW under PLANS-INDEX D8. `partialSpans` is the wire word `partial` (`partial` is a Lean keyword). -/
inductive CheckResult where
  | verified                                  -- agreement with the whole set, never one candidate
  | partialSpans (spans : List UnformalisedSpan)   -- a reading with an unformalised span: never `verified`
  | pending (codes : List String)             -- every candidate is pending
  | mismatch (fields : List Field)
  | unread (code : String)
  | unknown                                   -- the reader stopped at its budget: UNKNOWN

/-- The unit `u` of W2 document `D` is the hand side: a fixed rule (`VE.Compose.Content.norm`, with its soft
decisions) or a W2 authored set and the document's cited narrowings. -/
def checkHand (E : Env) (O : Overlay) (L : Lexicon) (R : List SourceWordRow) (b : Nat) (s : String)
    (D : VE.Readings.Doc) (u : String) : CheckResult

/-- Set-level verification: the hand rules agree with the reader's one reading, or with every rule candidate of its
set, and the pending candidates match in number. -/
theorem verified_whole_set (h : checkHand E O L R b s D u = .verified) :
    (∃ A nds, readSource E O L R b s = .one A ∧ toNodes [A] = .ok nds ∧ sameSet nds (handNodes D u)) ∨
    (∃ cs nds, readSource E O L R b s = .readings cs ∧ ruleCandidateNodes cs = .ok nds ∧
      sameSet nds (handNodes D u) ∧ pendingCount cs = handPending D u)

theorem mixed_partial (h : readSource E O L R b s = .mixed A us) : checkHand E O L R b s D u = .partialSpans us

theorem pending_only (h : readSource E O L R b s = .readings cs) (hne : cs ≠ [])
    (hp : ∀ c ∈ cs, ∃ k, c.reading = .pending k) : checkHand E O L R b s D u = .pending (pendingCodes cs)

theorem limit_unknown (h : readSource E O L R b s = .limit) : checkHand E O L R b s D u = .unknown

theorem mismatch_named (h : checkHand E O L R b s D u = .mismatch fs) :
    fs ≠ [] ∧ ((∃ A, readSource E O L R b s = .one A) ∨ ∃ cs, readSource E O L R b s = .readings cs)

/-- `unread` only when the reader produced no reading. -/
theorem unread_is_reader (h : checkHand E O L R b s D u = .unread c) :
    match readSource E O L R b s with
    | .one _ | .readings _ | .mixed _ _ | .limit => False
    | _ => True
```

**Fixtures:**
- The RSP's 34 CHECKED commitment units.
- The FSF's 38 norm units.
- The constitution's u0125.s04.p2 (`mismatch [setNotCollapsed]`).
- The five RSP and one FSF hidden-atom units of research 2.3 (`mismatch [hiddenResidual …]`).

**Seeded bugs:**
- Lean: report `verified` when the predicate matches and the sign differs. A fixture fails; restore.
- Lean: report `verified` when the hand rule is one candidate of the reader's set. The constitution fixture
  (`mismatch [setNotCollapsed]`) fails; restore.
- Python: let the measure script count a MIXED unit's residual bytes as read. The evidence test fails; restore.
- Python: count SOURCE-READ-PENDING bytes as source-read. The evidence test fails; restore.

**Moves:** the measured numbers that replace this plan's estimates. No status byte moves, except MIXED residuals,
which are counted UNFORMALISED.

## 4. Experiments (pre-registered; bars do not move after the first run)

### EN-E1. Does check mode catch the FSF audit's unfaithful units? (model-free, 3 h)

- **Input:**
  - the 47 audited FSF units with both auditors' verdicts (`MA/reviews/uc-audit2-20261028.md:70-87`;
    `MA/debates/uc-audit-safety-framework-20261028T2347Z/`);
  - the reader at EN-8, with EN-10's check mode;
  - the hand rules as they were audited, from the FSF commit the audit names.
- **Run:** `checkHand` on each unit. Record verified, mismatch with its fields, or unread with its code. No model call.
- **Bar (pass needs all three):**
  1. no FAITHFUL unit is `mismatch` (0 of 29);
  2. at least 9 of the 18 UNFAITHFUL units are `mismatch`, or `unread` with a refusal span that overlaps the words the
     audit quotes as mistranslated;
  3. at least 5 FAITHFUL units are `verified`. This bar rules out a reader that refuses everything.
- **Prediction, before the run:** 12 of 18 have causes in the classes a whole-sentence reader checks (research 2.5).
  The bar is set below it.
- **Pass:** check mode is offered as a pre-commit check for norm units in `MA/prompts/translation-fidelity-checklist.md`
  classes 1, 3, 5, 7 and 11 (a DRI decision).
- **Fail on bar 1:** the frame or row that produced the false mismatch is withdrawn and the run repeated once.
- **Fail on bar 2 or 3:** check mode is recorded as not catching the audit's classes; no gate claim.

### EN-E2. How ambiguous are real norm sentences under the frames? (model-free, 2-3 h)

- **Input:**
  - every norm sentence of the three frameworks: RSP commitment sentences by commitments' census lists, PF sentences
    by the same census, and the FSF's 38 norm units;
  - the reader at EN-5, with the rows that exist.
- **Run:** count `one`, `readings`, `parses`, `refused` and `limit`, and the largest derivation count.
- **Bar:**
  - `parses` (two structures, no row) on at most 10% of the sentences whose words all have rows;
  - `limit` never.
- **Pass:** EN-8 may add attachment rows only for patterns seen three or more times.
- **Fail:** EN-8 adds no attachment row. EN-E3 is run.

### EN-E3. Certified rewriting against frames (conditional, model-free, 3 h)

- **Runs when:** EN-E2 fails, or EN-9 reaches less than the low end of section 1's estimates.
- **Run:**
  - Write the rewrite steps that would normalise the refused sentences: passive to active, list distribution,
    numbered conditions, and so on.
  - Count the trusted rewrite rows against the frame rows D2 would need for the same sentences.
- **Bar:** design D3 only if it reads at least 25% more bytes with no more trusted rows than D2.

## 5. What each numeric and temporal form needs, and what the reader returns meanwhile

Owners and states are from the research (1.3) and the agents' reading of each plan (file:line there).

| Form (example, unit) | Needs (owner: piece) | State of that piece | Until then the reader returns |
|---|---|---|---|
| "within 30 days of receipt", "within one week of submitting …" (RSP s362-ask-30-days, s362-one-week) | ET-T1: durations over events, deadline fulfilment; ET-D2: "x does A"; ME/W6: `elapsed_day` | ET-T1 fired, design only, no backlog row; ET-D2 design only | MIXED with residual (ET-T1) in the act of a `must` clause; else `unformalised` |
| "within <n> days of <date>" | ET-5's reading set W1-W3 over named dates (`events-time-causation.md:451`) | ready | ET-5's row as a readings row, once landed; before that a residual (ET-5) |
| "by <date>", "no later than <date>" as a deadline on an act | ET-5 rows for "by" (B1/B2); events' `before ∨ =` (built); ET-T1 for fulfilment by an act | rows ready; fulfilment not designed | residual (ET-T1) |
| "until we are able to do so", "until and unless …" (RSP Appendix A) | ET-5 "until" sets U1/U2 per modality | ready | ET-5's readings row, once landed; "unless" is the W1 carve-out |
| "every 3-6 months" (RSP s31-timing) | ET-T1: recurrence; W6: months; a range of durations (no owner: calc's `Claim.within` is for numbers) | not designed; W6 undecided | residual (ET-T1, W6); MIXED |
| "at least once a year", "annually", "yearly" (FSF s51-yearly, PF line 16) | ET-T1: recurrence; W6: years | not designed | residual; MIXED |
| "quarterly" (RSP s4-quarterly) | ET-T1; W6 | not designed | residual; MIXED |
| "On approximately an annual basis" (RSP s4-compliance-review) | ET-T1; W6; QT-A6's "about"/"approximately" row (D5) | planned | residual; MIXED |
| "regularly", "periodically", "continually", "over time" (RSP s4-internal-review, s4-ltbt-brief; FSF s321-periodic; PF Appendix C.3) | no stated frequency: an open term with a decider (W2, judgment terms), or ET-T1 | — | residual (pending; owner the row's meaning owner, an open term's or ET-T1, never `en-e3-norm`); the translator may instead declare an open term on the act's predicate, as the FSF does (`ot12_periodic`) |
| "promptly" (RSP s4-investigate, s4-notify-board, s34-step4) | **no owner** (agents' search: no row, no plan) | — | residual (pending, owner `unowned` with the round-2 request); named in section 9 for round 2. ve-limits' `time` row classifies the sentence; it does not give "promptly" a meaning |
| "prior to the first external deployment", "before they are deployed", "Following approval of …" (FSF s132-cca; PF line 12; RSP s34-step4) | ET-T1: D-event fulfilment; ET-D2 | design only | residual (ET-T1); MIXED in an act; `unformalised` in a guard ("Following …") |
| "no more than 30 days prior to the publication of the report" (RSP, the coverage date) | ET-T1 and QT: a bound on a duration between two events | not designed | `unformalised` (it constrains a date, not an act) |
| "at least 200", "at least one external reviewer", "one or more", "more than one option" (RSP s4-unredacted-200, s362-all-sections, s4-recipients) | QT-A1 `CountAtom` (built) over a finite sort; QT-A6 English (planned); a counted act object, which neither act phrases nor quantities owns | count core built; the rest planned or unowned | residual (QT-A6); MIXED in an act; `unformalised` at place `bearer` ("at least one recipient will be …") |
| "within a factor of 5" (RSP t4-cost-factor) | **no owner** | — | `unformalised` (it sits in a definition, not a norm) |
| "at least as strong as", "equally or more robust" (RSP T1, T2 plans; FSF `at_least_as_strong`) | QT-B3: comparison wordings as act-argument fillers | planned; follows this step | residual (QT-B3) |
| "Security Level 2+" (FSF) | quantities' ordered scales (QS-1, built), with the scale's declaration | built core | read as a declared constant's spelling; no comparison is inferred |

## 6. Risks and open questions

1. **The `Ty` change moves every English identity.**
   - Adding the statement types changes `actions_version`, so `grammar_id` and the recorded identities of every English
     fixture change.
   - The generator regenerates them, and EN-1's commit carries the regenerated files only. The identity tests confirm
     that no reading changed: same formulas, new identities.
   - If the generator's row format forces edits to `Catalogue.lean`, that is one more shared hunk (EN-0 decides).
2. **Source sentences may parse many ways.** EN-E2 measures this before EN-8 adds anything.
3. **"should" and "must" rows.**
   - The FSF fidelity check (`usecases/safety-framework/README.md:70-73`) and the constitution audit of u0125.s04.p2
     both argued for one reading in context. Soft-norms 2.2 keeps both.
   - The rows are their owners' and the DRI's decision. The reader applies whatever the rows say, and check mode
     reports where an audited translation collapsed a set.
4. **Dependencies that are not scheduled.**
   - en-sw (ready) gates EN-5 onward. CM-1 and CM-4 (design-ready) gate EN-6. CM-5 and sc-1ae gate EN-9.
   - If they slip, EN-1 to EN-4 still move Lean's authority over every formal norm unit, and EN-5 and EN-7 still read
     third-person and constant-bearer sentences.
5. **Joins on the soft and readings routes** wait for C12's one `gate_acts` revision. Many commitment sentences are
   reading sets, so many joined acts stay refused by the gate (`routeRefusal`) until then.
6. **The RSP's "situation" convention.**
   - Hand rules speak about situations, not about Anthropic (RSP deviation 1).
   - Check mode compares the bearer under each use case's declared convention and reports it as a note (D9).
   - New translations under this reader would use commitments' legend instead. Whether to re-express the RSP is the
     use case's decision, not this plan's.
7. **Pending rows for words with no owner** ("promptly", cadence words): see section 9, NEW 4. Round 2 should confirm
   that a meaning owner may take such a row over by a later edit. Each such row names its meaning owner, or `unowned`
   with the round-2 request; never `en-e3-norm` (D5).

## 7. Requests to other owners

- **R1. Rows for force words in translation** (soft-norms 2.2 and norms 2). These are today applied by hand in the use
  cases (PF RS9, RS13; FSF `translation.py`):

  | Words | Candidates |
  |---|---|
  | "must", "should" | {strict, default} |
  | "must not", "should not", "should never" | {strict prohibition, default prohibition} |
  | "may" | {permission, might} |
  | "may not" | {prohibition, might not} |
  | "need not" | {release} |
  | "is required to", "are required to" | {strict} |
  | "shall", "shall not" | a reading set for the row's owner to state |

  - Owner: soft-norms (2.2) and norms (2), with the DRI's pending "should" question (section 6, item 3).
  - EN-5 can transcribe them under those owners' review if no batch of theirs is queued. The owner field names soft-norms
    or norms.
  - **To modality-counterfactual:** R1's epistemic "might" candidate (and "might not") is pending under you, its meaning
    owner. Until your row exists, a set that holds it is SOURCE-READ-PENDING (D11), and its bytes are kept out of the
    source-read bytes.
- **R2. A row for bare-plural subjects in norm sentences** ("Employees must …"), reading "Every <noun>". Owner:
  hedges-generics, which owns bare generics.
  - **To hedges-generics:** R2's universal-only reading needs your owner-approved norm-frame row, set against D-H4
    (a bare generic reads as {every, by default, more than half, characteristic}). Until that row exists, R2's fixtures
    do not apply, and the sentence is refused with your code.
- **R3. A row for present-tense practice** ("We conduct …", "SAG reviews …"), giving {commitment, description}. This is
  the PF key's RS0. Owner: commitments (census kind R; no CM-4 row today).
- **R4. Discourse:** anaphors inside the act of a source sentence ("of the same", "it", "this content") and guard
  binders ("When we receive a report, … the report …").
- **R5. ET-T1:** take over this plan's pending "norm.modifier" rows for cadence and deadline words when ET-T1 builds.
  Each such row names ET-T1 in its advice.
- **R6. To commitments (CM-4's Needs line).** CM-4's Needs line (`CM/…/commitments-PLAN.md:228, 248, 823`) waits for the
  whole "E3 norm step", while EN-6 waits for CM-4: a cycle. Please make it name EN-5, which provides the norm frame keys
  and holes (section 9, NEW 2), `readSource` and the row interface. Any CM-4 fixture that reads a whole sentence into a
  rule moves to EN-6. Order: EN-5, then CM-4 (after CM-2, en-sw and CM-E1), then EN-6 (after CM-1, which uses the moved
  `VE.Legend`; EN-6 does not restate speech-acts' `eqGuard`).
- **R7. To quantities (QT-B3).** QT-B3 may follow EN-5 (`MA/debates/plan-synthesis/SYNTHESIS.md` line 322). Its
  comparison rows go only into en-sw's `SourceWords.lean` (C1, O15), as this plan's rows do.
- **R8. To profile-composition (PC-4).** The route refusals of candidates read `Matrix.documentRefusal` once PC-4 lands
  (until then `VE.Compose.gateOf profileTable`'s text). This plan copies no refusal code (`JoinRoute` is dropped).
- **R9. To the meaning owners of numeric and temporal phrases** (ET-T1, ET-5, W6, QT-A6, QT-B3; soft-norms and norms for
  the rule side). Product use of a projection that drops a phrase from a rule (draft 1's D5) waits for your theorem
  that the projection keeps every breach, in the obligation and the permission half alike (W1's `required → permitted`
  under deny completion, `docs/spec/norms.md:222-226`). Until then MIXED is a measurement only (D5, EN-7).

## 8. What is deleted, and what is not duplicated (summary)

**Deleted:**

| Batch | What goes |
|---|---|
| EN-3 | `ve/norm_english.py`'s W1 block parser: `_HEADER`, `_parse_consequence`, `_block_grammar`, the line, header and clause splits, the `UnknownRule` checks, the W1 call sites of `_consequence` and `_parse_guard` (spec 2.5 lists the lines); Python's authority over `english.statement` (W1) |
| EN-4 | the soft block parser and its regexes, including the hard-coded frequency-word refusal; `_consequence`, `_parse_guard` and `render_rule_sentence`'s soft branch; the norm-block frames of `ve/surface/softnorms.py` |
| EN-5 | the use cases' hand-written word-to-reading tables for force words (they point at rows) |

**Not duplicated:**
- the grammar engine and its proofs;
- the formula grammar (`condition_same`);
- the lexicon and V4 (the source view adds source spellings to `Lexicon.aliases`; no second list);
- act phrases' lexical checks and AP-2 joins;
- act phrases' `VE.Acts.Op` and `opOf` (`Force.op` is proved to agree, `opOf_agrees`), and soft-norms' `Mode`
  (`Mode.soft`);
- `Discourse/Joint.lean`'s choice enumeration (`allChoices`, `mem_allChoices`, `length_allChoices`) and W2's limit;
- composition's gate and matrix for route refusals (`VE.Compose.gateOf`, `Matrix.documentRefusal`);
- ve-limits' classification codes, as a span's class only;
- the moved `VE.Legend` (after CM-1);
- `decodeNorm` and soft-norms' decoder;
- W2 reading sets and their separations;
- en-sw's rows, CM-4's rows and `Commitments/Read.lean`'s wordings;
- speech-acts' binding (after CM-1);
- scope's governors and CM-5's `inherited`;
- ET-5, ET-T1, W6, QT-A6, QT-B3, QT-E meanings;
- discourse's pronouns.

## 9. Shared pieces

Abstractions several topics could share. NEW pieces name the closest existing abstraction. The cross-plan review may
move any of them.

| # | Piece | NEW or reused | Closest existing | Who else needs it |
|---|---|---|---|---|
| 1 | **Statement value type** in english-lean's action library: one `Ty` family for sentence-level statements (norm blocks, source norm sentences), with its meaning type `Meaning Tok NState Reject NormStatement` | NEW | en-wg's weighing-statement value type (weighing refresh ruling (b)); `Ty.sentence` | en-wg, commands' B shape, definitions' PD-4 wrapper, any later S6 layer (legends, reports, speech) |
| 2 | **Norm frame keys and holes** for en-sw rows ("norm.force", "norm.subject", "norm.connective", "norm.modifier", "norm.attach"; holes "{act}", "{bearer}", "{condition}") | NEW | en-sw's `frame` field; commands' declared spellings for holes | CM-4, R1-R3's owners, DF-4, attitudes (rows that fill a norm frame) |
| 3 | **Source spellings** of act wordings: the source view over `Lexicon.aliases` (`sourceView`), validated by V1-V5, act phrases' lexical checks and D5 | reused (draft 1's `SourceLexicon` dropped) | `Lexicon.aliases` and the environment's fixed aliases; commands' CI-4 declared spellings (`Env.declaredSpelling`) | commands, attitudes over acts, questions about acts ("Must Alice <act>?") |
| 4 | **Unformalised span record with owner** (`UnformalisedSpan`: span, row, owner, place; the owner is the row's meaning owner or `unowned`), plus pending refuse-rows for words whose meaning owner has no row | NEW (renamed from draft 1's `Residual`; it is not ve-limits' `Residual`, which holds an OPEN unit's open terms or its active reading set) | ve-limits' `Residual` (distinct; its codes may appear as a span's class, never as its owner); W2's `support` provenance line (math-evidence shared piece 5); events' residual line format (events shared pieces, `docs/spec/events-time-causation-PLAN.md:1147`); ET-5's stop-gap rows | ET-T1, W6, QT-A6, QT-B3 (each sees exactly which bytes it unlocks); commitments' CM-M0 and CM-7 (D14 measurement) |
| 5 | **The monotone-place rule** for classifying MIXED (D5: only at the act of a `must` clause, and only for a row marked restricting); a measurement rule that licenses no split | NEW | act phrases' modal and connective `table` (polarity by modal); D14 (commitments) and D7 (commands), which are measurement rules | commands (MIXED commands), hedges-generics (hedged parts), purposes (a purpose clause on a norm) |
| 6 | **Check mode**: a unit's hand content (a rule with its soft decisions, or a W2 set with its cited narrowings) against a sentence's readings, field by field, verified only against the whole set | NEW | `english.check` (index of the first candidate that reads back); the translation-fidelity checklist | every use case and pilot translation; uc-audit |
| 6a | **Check mode's results** (verified, partial, pending, mismatch with its fields, unread, unknown): an answer vocabulary over the three-valued machine | NEW, listed under PLANS-INDEX D8 (no rename) | QA leads, weighing zones, speech-acts answers, action-assurance's verdicts (the other D8 vocabularies) | every use case; uc-audit |
| 7 | **Candidates as authored wordings**: a row's reading set is a list of plain-English sentences, each with one reading; several rows combine through `Discourse/Joint.lean`'s choices (PLANS-INDEX D1), UNKNOWN over W2's limit | reused shape, made a rule here | W2 authored reading sets; commitments' 3.1 table; `VE.Discourse.allChoices` | CM-4, DF-4, attitudes, ET-5 (their rows' candidates are read the same way) |
| 8 | **The source-read measure** (D11): SOURCE-READ, SOURCE-READ-PENDING, MIXED, MISMATCH, or UNREAD per unit (source-reading fidelity) | NEW, over the shared byte partition and the shared code table | the use cases' span accounting (`bytes_by_status`, blockers); ve-limits' bytes-per-class report (a different measure, kept separate) | every pilot; NORTH-STAR's expressible-bytes metric |
| 9 | **The mode `english.statement`** (kind `blocks` in EN-2; `render` in EN-3; `check` in EN-10) | NEW service mode | `english.read`, `english.check` | Python's `ve/norm_english.py` relay; the use-case measure scripts |
| — | Reused, not new: source-word rows (en-sw, C1); `many` is not a set (round 2, D11); `SourceOutcome.readings` is a W2 authored set (PLANS-INDEX D11); the formula grammar; `decodeNorm`; act phrases' `VE.Acts.Op` and `opOf`; soft-norms' `Mode`; `Lexicon.aliases`; `Discourse/Joint.lean` (`allChoices`, `mem_allChoices`, `length_allChoices`, `compatible_budget`'s rule); composition's gate and matrix (`VE.Compose.gateOf`, `Matrix.documentRefusal`); ve-limits' classification table; the pronoun legend (speech-acts, moved to `VE.Legend` by CM-1); scope's `frame` governor (CM-5); events' day sort and named dates | reused | — | — |

**Unowned words this plan names for round 2:** "promptly", "within a factor of", and ranges of durations ("3-6
months").
