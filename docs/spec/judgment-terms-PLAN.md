# Judgment terms: plan

> **Status.** Draft 4, 2026-10-14, branch `research/judgment-terms-p1` from `main` at `f98183bf`. Docs only. It applies
> phase 1's results ([docs/research/judgment-terms-phase1.md](../research/judgment-terms-phase1.md), cited as P1 and a
> section number; its review `manage-agents/judgment-terms-ph1-review.final.md`: ACCEPT, six minor findings, no fix
> round). Every number from phase 1 is measured and cites its evidence file under
> [docs/research/evidence/judgment-terms/](../research/evidence/judgment-terms/); no bar is moved. The statement spec
> is at draft 3, which adds one fixture and changes no statement.
>
> **Changes in this draft (4).**
> - New 0.1 and 0.2: each phase-1 result with PASS, FAIL or no bar and what it gates; each DEFERRED item with its
>   trigger.
> - JT-0p: bar part A **PASS**; bar part B (the blind audit, and with it the +132 B) **DEFERRED**. The prompt text
>   gains what the run needed: the sort `thing`, the two placeholder records replaced, the reading sets rebuilt, no
>   constant `verbalisation`, no template for u010's predicate, the ledger's `claimed: false` read by the claim, and the
>   metrics key `open_term_class_borderline`.
> - JT-5 is split. **JT-5a** switches the constitution (31 of 33 records already bind). The UDHR's records bind none
>   (52 of 52 refused), so **JT-5r**, a new re-translation step, comes first, and **JT-5b** switches the UDHR after it.
>   JT-5's bar is unchanged. It now says that a record no unit uses may be removed with its reason, because the removal
>   cannot change any status.
> - D2: one word over several sorts is one bound term per sort, the terms sharing their words. This adds fixture J-ω,
>   computed in the stub, and corrects 4.2's `arbitrary` row: one usage row per sort and per part.
> - Bytes (8): JT-5's figures are measured (UDHR 18 units, 1,945 B; constitution 13 units, 2,150 B). The JT-0p
>   claim stays an estimate.
> - D7: the measured decider spellings. JT-3: what is shown when the wording lint rejects a judgment's template.
>   Risks (9) updated.
> - 11 keeps R1 to R5 word for word, with the DRI's decisions. The new 11.2 lists phase 1's issues for other owners.
> - No batch is dropped.
>
> **Earlier drafts.** Drafts 1 to 3 (2026-10-13 and 2026-10-14) were written on branch `design/judgment-terms`, from
> `main` at `f98183bf`. Docs only: no product
> code, no tests, no generated file touched, no model calls. It builds the recommendation of
> [docs/research/judgment-terms.md](../research/judgment-terms.md) (cited as R and a section number): design B, "bound
> judgments". Every number is measured (R2 gives the method) or marked **estimate**. Draft 1 (2026-10-13) was
> reviewed by Astra and Fable (`manage-agents/debates/design-judgment-terms/`, converged in round 3 on **REVISE to
> draft 2, then BUILD**). Draft 2 applies that joint position: Fable's fixes 1–5 and edits A–D, Astra's two round-3
> clarifications and limits, and the u060 change. Its only other changes are pointers to the item-1 spec, one
> correction the spec's stub found (J-ι's second rule permits the arrest rather than requiring it, spec F2), and
> seeded bugs for the behaviours the fixes add. BUILD is authorised once JT-0's stub
> elaborates draft 2's statements and the statement review passes, before any product code. The statements of
> section 3 are written out in full, elaborated against `main`, in the item-1 statement spec
> [judgment-terms.md](judgment-terms.md); where the two differ, the spec's text wins.
>
> **Draft 3** (2026-10-14) applies the statement review's converged joint position
> (`manage-agents/debates/judgment-terms-spec/`, rounds 1 to 3: **FIX**; listed in the spec's section 0.1): Astra's A1
> to A5, Fable's F2, F3′ and F4 (with Astra's precision on completeness), and the F3 wording. It changes nothing else
> but the seeded bugs for the behaviours those fixes add. The corrected statements were re-elaborated and the changed
> fixtures recomputed in the stub (spec draft 2).

## 0. Summary

| # | Batch | Hours | Owner | Moves a pilot number? | After phase 1 |
|---|---|---:|---|---|---|
| JT-0p | Pilot: measure judgment terms in both ledgers; write UDHR u010 and u060 as asserted judgments (u010 claimed, u060 unclaimed) | 2 | pilot runner (prompt text from this plan, merged by the DRI) | **yes**: UDHR +132 B claimed (**estimate**), until audited | **kept**, run in part. Bar A PASS; bar B DEFERRED (0.2); prompt text completed (5) |
| JT-0 | Statement spec, Lean stub against `main`, statement review | 3–4 | planner, then reviewers | no | done (spec draft 2; draft 3 adds J-ω) |
| JT-1 | Lean core in a new directory: W2 records (repeated sorts under the profile), binding to base predicates, admission, computed status over one candidate list, dependence through definitions, legacy proofs; the shared scan `opensIn`, with rights' `nodeOpen` switched to it | 5–6 | Lean | no (integrity) | kept; fixture J-ω added |
| JT-2 | `judgments@0` in Lean's document mode: status hook, the usage map, AR-10 row, response shape, Python relay and fuzz tests; Python's W2 schema twin leaves the live path | 5–6 | Lean, Python | no (statuses become Lean-computed) | kept unchanged |
| JT-E1 | Experiment: do readers see which answers turn on which judgment? (proxy readability) | 3 | experiment runner | gate for JT-3's wording | kept; not run (DEFERRED). Today's arm confirmed: the asserted judgments render with identifiers (P1 2.2) |
| JT-3 | English: declaration line, legend line, sense-tied catalogue rows for evaluative words, refusals; the Lean-computed `undeclared_evaluative` report, its schema, binding check and fuzz tests | 5–6 | english-lean owner (texts from this plan), Lean, Python | no (readability) | kept; lint-rejected templates named (5) |
| JT-4 | Judgment atoms in WG-6's zone answers and records; deciders named; criteria as labelled premises ("conflict-free, given …"); English through WG-7 | 4–5 | Lean, Python | no (answers at situations) | kept unchanged |
| JT-5a | The constitution's main document switches `judgments@0` on | 2–3 | pilot runner | statuses computed by Lean on 13 units, 2,150 B (measured); 0 B | **changed**: JT-5's constitution half, first |
| JT-5r | UDHR re-translation: every used open term gets a predicate of its own, the changed units re-audited | 4–6 (**estimate**) | pilot runner, under act-phrases' attachment rules (owner: 11.2, X1) | 0 B gained; the changed units keep their claim only if re-audited FAITHFUL | **new**: the forecast refuses all 52 UDHR records (P1 2.6) |
| JT-5b | The UDHR's four parts switch `judgments@0` on | 2 | pilot runner | statuses computed by Lean on 18 units, 1,945 B (measured); 0 B | **changed**: JT-5's UDHR half, after JT-5r |
| JT-E2 | Experiment (research JT-R1): judgments over propositions ("it is essential that …") | 4 | experiment runner | possible later bytes (upper bound 3,238 B, co-blocked) | kept; not run (DEFERRED) |
| JT-E3 | Experiment: can raters agree which open terms are judgments? | 2 | experiment runner | validates JT-0p's instrument | kept; not run (DEFERRED); its frame exists (89 terms) |

**Order.**
1. **JT-0p now.** It changes only prompt text, adds no profile and claims u010 only. Phase 1 ran it on copies of the
   pinned run (bar part A PASS). The live prompt text and the blind audit wait for the DRI's merge (0.2).
2. **Draft 2, then JT-0.** The stub elaborates admission through `hide`, repeated sorts under the profile, the single
   candidate traversal, the compiled definitions interface, the `ConflictFreeX` claim and the `opensIn` equation. The
   statement review passes before any product code is written.
3. **JT-1**, including `opensIn` and the switch of rights' `nodeOpen` (with the frozen-sources rehash).
4. **JT-2**, once `lf-16g` (Lean document mode) and AR-10's table are on `main`.
5. **JT-E1, then JT-3**, which adds the catalogue rows and the `undeclared_evaluative` report with its schema, binding
   check and fuzz tests.
6. **JT-4**, once WG-6, WG-7, R1 and R2 are on `main`, with J-ι checked under its premise.
7. **JT-5a** (the constitution), under the "no declaration removed" bar. **JT-5r** (the UDHR's re-translation) may run
   any time after the DRI names its owner (11.2, X1), and needs no product code. **JT-5b** (the UDHR) runs after
   JT-5r's re-audit, under the same bar.

JT-E2 runs after attitudes' AT-3a and JT-E3 any time after JT-0p; each is authorised separately.

### 0.1 Phase-1 results and what they gate

Phase 1 ran JT-0p on copies of the pinned run 20261012T1800Z, plus three descriptive measurements with no bar
(P1 1.2). The checker's builds were the ones pinned in `lean/checkers.lock`.

| Item | Bar | Result | Verdict | What it gates |
|---|---|---|---|---|
| JT-0p bar part A | "The four UDHR parts load and check as before, with u010 and u060 OPEN" | u010 and u060 UNFORMALISED → OPEN. The other 128 units keep their status. Premises, readings and conflict are equal to the baseline. Coverage moves only the units' 132 B and 66 B (`bar-a.json`) | **PASS** | the u010/u060 encoding and the prompt text of JT-0p (5) may be merged by the DRI |
| JT-0p bar part B | "PASS if the targeted audit finds u010 FAITHFUL: claimed bytes +132 … FAIL otherwise" | not run: a model call by an auditor who did not write the units | **DEFERRED** (0.2) | the +132 B claim; until then the UDHR's claimed bytes stay 4,792 B (43.90%) |
| u060's audit verdict | recorded, no bytes either way | not run (same audit) | **DEFERRED** | nothing |
| Reproduction P1–P8 | exact equality with the figures the plan and R cite | all equal (`reproduction.json`, `reproduction-p1.json`) | **PASS** | the plan's inputs: 4,792 B; u010 132 B, u060 66 B; 4,924 B, 45.11%; 52 and 33 declared terms; 11 units, 1,333 B and 18 units, 1,945 B; 203 of 454 lines |
| Reproduction P9 | R2.3's 12 UNFORMALISED units, 1,942 B | 17 units, 2,792 B by the bare lexicon. R2.3's 12 are a hand selection among them; 13 units, 2,183 B with u013bb | **FAIL** | nothing in this plan: no batch, bar or byte row uses the figure. The research note relabels R2.3's table (0.2) |
| Instrument (JT-0p item 1) | none: "its numbers start a series" | UDHR 52 terms: 32 judgment (10 borderline), 18 classification, 1 attitude, 1 proportion. Constitution 37 terms: 18 judgment (4 borderline), 13 classification, 4 exception, 1 attitude, 1 proportion. Judgment-term units: UDHR 18 (1,945 B); constitution 507 (88,989 B), of which 13 are covered units with content (2,150 B) (`instrument-*.json`) | no bar; one rater | JT-E3's frame. The counts are not published as measured until JT-E3 passes |
| Integrity check by hand (JT-0p item 3, without the model audit) | none | 0 hits in the 20 CHECKED units of both pilots. The control finds 35 of the 49 OPEN and READINGS units (`integrity.json`) | no bar | JT-5a and JT-5b expect no unit to move to OPEN. D3 and D15 are preventive: neither pilot shows a judgment as checked today |
| Admission forecast (2.1, checks 1–5, read from the records) | none; a forecast, since Lean owns admission | UDHR: 52 of 52 records `JudgmentUnbound`, all 52 `unstated`. Constitution: 31 of 33 admitted, `good_judgment` unbound, `child_sexual_abuse_material` `JudgmentArguments` (`admission-forecast.json`) | no bar | JT-5's split (JT-5a, JT-5r, JT-5b) |
| JT-E1, JT-E2, JT-E3 | section 6 | not run | **DEFERRED** (0.2) | as section 6 says, unchanged |

Phase 1 also has three findings for other owners (P1 2.6: F1 renderer, F2 environment decoder, F3 reading-set ids).
They are listed in 11.2.

### 0.2 Deferred items and their triggers

| Item | Trigger | Then |
|---|---|---|
| JT-0p bar part B: the targeted blind audit of u010 (+132 B) and u060 | The DRI merges P1's `prompt-additions.md` into `manage-agents/prompts/` (one file per pilot, SC2). The next UDHR run (06:00 or 18:00 UTC) then audits u010 and u060, with an auditor that did not write them | PASS: claimed 4,924 B (45.11%). FAIL: u010 reverts, with the reason recorded |
| The instrument in the live pilot runs | The same merge | The first live run should reproduce `instrument-udhr.json` and `instrument-constitution.json` for unchanged units |
| JT-E1 | The DRI's authorisation and model budget. It runs before JT-3, which it gates (Order, step 5) | section 6 |
| JT-E2 | AT-3a on `main`, and the DRI's authorisation | section 6 |
| JT-E3 | The DRI's authorisation. It can run any time: its frame is P1's `open_term_class.tsv` (89 distinct terms; 91 rows, because the UDHR's two placeholders and their JT-0p renames each have a row) | section 6; PASS lets the instrument's counts be published as measured |
| JT-5r | The DRI names its owner (11.2, X1) | 5 |
| JT-5b | JT-5r re-audited, and JT-2 on `main` | 5 |
| Research note R: fill R2.2's constitution placeholders from P1 2.4; relabel R2.3's UNFORMALISED table as a hand selection (P9) and weigh u013bb; state the covered-unit rule (units with content, so not the LABELLED heading u0126, 19 B) | The note's next edit (outside this draft, which changes the plan and the spec only) | the note matches 0.1 |
| Two phase-1 claims that no committed script repeats (review finding 1): D1's no-op self-test, and F1's "13 accepted before" | JT-5a's reading-set rebuild, which commits the rebuild with its self-test (5) | the rebuild's self-test is a script command |

**What this plan does not build** (each has an owner, R1.3):
- degrees, comparatives and thresholds (quantities' `scales@0`);
- the three-valued enumeration, zone answers, decision records and precedents (weighing's WG-6, WG-7, WG-E2);
- knowing and likelihood (attitudes);
- attachment of "arbitrary" and "fair" inside act phrases (act-phrases);
- rendering and the source-word catalogue (english-lean);
- "unless there is good reason" (defeasible).

## 1. Decisions

| # | Decision | Why | Rejected |
|---|---|---|---|
| D1 | A judgment term is a W2 open term under the profile `judgments@0`. The nine-key record does not change | one record, one owner (W2, `docs/spec/document.md:79-83`); quantities' grades and attitudes' generated terms are already W2 open terms | a new `judgment` record or kind field (design C); a `class` field in the language (the class is a ledger annotation, D5) |
| D2 | **Binding.** Under the profile, every open term's `name` is a declared **base** predicate (declared in `hide E (names defs)`, so a W3-defined name is unbound), whose sorts are its `arguments`, and no rule regulates it. Under the profile `arguments` are sorts and may repeat (`[person, person]`): W2's validator (`Loader.openTermNames`) relaxes its distinctness check only under the profile, so the rule keeps one owner. A regulated predicate is refused because one atom has one role: its value is what the rules compute (a layer symbol, which WG-6 reads from the tables), while a judgment is a base atom its decider supplies. The predicate's template and description are the term's words. **One word over several sorts** is one bound term per sort, the terms sharing their words. Phase 1 found the UDHR's `arbitrary` applied to measures, interferences, intrusions and deprivations (P1 2.6). Each such term has its own usage-map row, and english-lean's legend may group them (fixture J-ω) | Lean can then compute everything else from content; rights already reads open names as predicate names (`lean/VE/Rights/Run.lean:159-162`) | a binding field (changes the nine-key schema); leaving the term unbound (design A); a second validator for judgment records; for one word over several sorts, a sort-polymorphic term or a shared supersort (a language change) |
| D3 | **Integrity.** Lean computes the status. Content that depends on a bound judgment is OPEN, never CHECKED: judgment dependence forces OPEN; otherwise the legacy status applies. Dependence is **syntactic use, directly or through W3 definitions** (D4); it does not follow one rule's outcome into another rule's guard, so an outcome downstream can still vary with a judgment (spec F3, fixture J-χ; the zone answers that, JT-4). `"meaning": "specified"` on such content is refused (`JudgmentNotChecked: <unit> <term>`); an `open` list must name every judgment the content depends on (`JudgmentNotListed`) and, when the unit's content is complete (no pending reading), no bound judgment it does not (`JudgmentListedUnused`). The content is one list per unit: its own content, or the candidates of its active reading set (2.2); the status, the set status and the usage map all read that list. The guarantee covers **declared** terms only (D15) | "never present a judgment as checked" becomes a theorem (`status_never_checked`) instead of a translator's promise; today OPEN is author-declared (`Loader.lean:210-213`) | downgrading silently (hides a translator error) |
| D4 | **Dependence goes through definitions.** A unit depends on a judgment if its content uses it, or uses a W3-defined predicate whose definition reaches it. The definitions are the route vocabulary's compiled W3 list, `rv.definitions` (dependency order; the list the norms tree copies, `Norms/Wire.lean:304`) | otherwise `wrongful_detention :↔ detention ∧ arbitrary` would let a judgment pass as CHECKED (fixture J-γ, and its rule-unit twin J-γ′) | direct use only |
| D5 | **One construct for classification and judgment words.** "Slavery" and "arbitrary" are both bound open terms; for the checker they are the same. The judgment / classification / exception / attitude class is recorded by the pilots' ledgers (JT-0p) for measurement only | the class changes no check; JT-E3 tests whether it can be measured reliably | a language-level class with different semantics |
| D6 | **Criteria are sentences.** Under the profile, `necessary` and `sufficient` are empty (`JudgmentCriterionAsUnit: <term>`). A criterion the source states ("no arrest ordered by a court is arbitrary") is a unit with its span, so it binds and is audited. On the layered route (JT-4) such a unit is a labelled premise in X, and the answer it supports is `ConflictFreeX`, "conflict-free, given <sentence>", kept apart from the answer without additional judgment criteria, which an assertion unit never changes. That answer is unconditional only on the plain route (`conflictFreeU_consistent`); on the layered route it is `ConflictFreeX L.U L.X`, which assumes the route's own premises (soft coherence, rights limitations), and its line names them | attribution's rule (`attribution.md:2512-2515`), one place for criteria; today the lists are typed and then dropped (`Loader.lean:387-398`), so a reader cannot tell whether they bind; `ConflictFreeU` quantifies over base situations, which an assertion does not constrain (`backgroundBase` holds only literal distinctness, `Norms/Prefix.lean:35`) | making the record's lists premises (a second, span-less place for criteria); claiming unconditional conflict freedom from a criterion unit. Soft norms' and rights' own condition premises are unchanged |
| D7 | **One spelling for "no one named".** Under the profile `decided_by` is a token; when the source names no decider it is `unresolved_decider` (attribution's and attitudes' value). `unstated` is refused with that rewrite (`JudgmentDecider: <term>`) | the pilots use both spellings for one meaning. Measured (P1 2.6): all 52 UDHR records say `unstated`, and none of the constitution's 33 does | accepting both (two spellings, one meaning) |
| D8 | **Answers at situations reuse WG-6.** The bound judgment names are added to WG-6's open names. "Settled whatever the judgment", "left to <decider>: these two admissible completions give different answers and differ on …", "not said", "inconsistent", "unknown" and judgment records are WG-6's answers and records | one owner of three-valued completion (SYNTHESIS O18); WG-6 already takes an explicit `opens` list | a judgment table of its own (design C) |
| D9 | **Graded words are quantities'.** A `scales@0` grade must be a W2 open term, so under `judgments@0` it is bound too, and its atoms are judgment atoms in zone answers. Nothing else is added for degrees | one owner (SYNTHESIS O4, quantities §10 item 3) | penumbral premises written by this plan |
| D10 | **Subsective phrases are conjunctions.** "Arbitrary arrest" is written `arrest(x) ∧ arbitrary(x)`. No generated premise "every arbitrary arrest is an arrest" | it follows from the conjunction; act-phrases owns restrictive-modifier specialisation (AP-5b) | a generated subsection premise |
| D11 | **Asserted judgments are ordinary assertions** over a bound judgment, OPEN ("The family is a natural and fundamental group unit of society.") | NORTH-STAR row 10's two UDHR units; no new construct | a new "evaluative claim" kind |
| D12 | **English: plain words, no symbols.** Declaration: "Whether an arrest is arbitrary is a judgment; the text does not say who makes it." or "… is a judgment for the governance function." Legend and zone wording as in 2.4. The rows are english-lean's (DRI AT4; SYNTHESIS O15), with texts from this plan, gated by JT-E1 | zero-training English; open terms are "strict only" today (`document.md:143`) | identifiers in what people read |
| D13 | **Authoring may precisify, translation may not.** In authoring the editor offers two ways out of a judgment word: define it (W3, the author's signed reading) or name who decides it. In translation it never defines | readings from the words only (VISION section 3) | defining in translation (design D) |
| D14 | **Deleted or not duplicated.** Python's copy of the W2 schema check (`ve/openterms.py`, against `Loader.openTermNames`) leaves the live document path in JT-2. The scan of open names in formulas is one function, `opensIn J (fs : List Formula)` (the two node types differ, so the formula scan is what is shared): rights' `nodeOpen` calls it in JT-1, and an equation theorem with rights' frozen fixtures shows rights' output bytes are unchanged. This plan adds no enumeration, scale, record type, precedent mechanism or English table | CLAUDE.md "one owner per piece of logic" | recording the overlap and switching rights in a later batch (leaves the scan duplicated) |
| D15 | **Undeclared evaluative words are reported, not refused.** Under the profile, Lean reports `undeclared_evaluative`: the base predicates whose words match a row of english-lean's single catalogue (`lean/VE/EnglishGrammar/*`) and that are not bound. Regulated predicates are included: D2 forbids binding one, so an evaluative word inside a regulated act is exactly the hidden case. It says only "these words match the catalogue; review them", never that a unit contains no other judgment, and never makes a regulated predicate admissible as a judgment. Its schema is typed, and the relay binds it: each name is a base predicate of the request (regulated ones included) and is not bound. It lands with JT-3's catalogue; until then the JT-0p and JT-5 audits check by hand | if a translator never declares `arbitrary`, it is an ordinary base predicate and its unit is CHECKED; nothing in translation catches it (2.4's refusal row is authoring's) | a refusal ("due date", "necessary condition", "effective date" would be refused wrongly); a second word list |

## 2. The design

### 2.1 Wire

- The environment's profile list contains `judgments@0`. The front matter's `open_terms` keeps the nine keys. Under
  the profile `arguments` are the predicate's sorts and may repeat (D2): a judgment between two people has
  `["person", "person"]`. Without the profile W2 still refuses repeated arguments with its own text.
- Example: u037, "No one shall be subjected to arbitrary arrest, detention or exile.", with the joined filler as
  act-phrases leaves it. The predicate `arbitrary` is declared in the environment with template `{0} is arbitrary`
  and sort `act`. The record:

  ```json
  {"name": "arbitrary", "arguments": ["act"], "decided_by": "unresolved_decider", "necessary": [], "sufficient": [],
   "factors": ["the Declaration gives no test for arbitrariness"], "precedents": [], "jurisdiction": "udhr",
   "version": 1}
  ```

  The unit's rule has the guard `arrest(a) ∧ arbitrary(a)` and the meaning `{"open": ["arbitrary"]}`.
- **Admission checks** (Lean; the first fault in record order wins, then unit order):
  1. `JudgmentUnbound: <term>`: no base predicate of that name. Admission reads `hide E (names defs)`, so a
     W3-defined name is unbound.
  2. `JudgmentArguments: <term>`: the predicate's sorts are not `arguments`.
  3. `JudgmentRegulated: <term>`: a rule regulates the predicate (one atom, one role: D2).
  4. `JudgmentCriterionAsUnit: <term>`: `necessary` or `sufficient` is not empty.
  5. `JudgmentDecider: <term>`: `decided_by` is `unstated`.
  6. Then, per unit: `JudgmentNotChecked: <unit> <term>`, `JudgmentNotListed: <unit> <term>`,
     `JudgmentListedUnused: <unit> <term>`. The last applies only to a complete unit: with an active reading set, the
     set has no pending reading (whatever the unit's own content); without one, the unit has its own content. A unit
     with nothing elaborated to read cannot show a listed judgment unused.

  W2's own schema check (`Loader.openTermNames`) runs first and keeps its texts.

### 2.2 Status

- **One traversal.** Each unit gives one list of contents: its own content, or, when an active reading set speaks for
  it, the candidates of that set. The unit status, the reading-set status and the usage map all read this one list.
  - Formula and norm candidates are both kept (a norm candidate is read as its rule, never as `readingsSets`' `top`
    projection); a pending candidate (`content: null`) gives nothing to read, but the traversal keeps it, so that the
    unit counts as incomplete (2.1, check 6).
  - Only the active version is read, as the loader already picks it (`Loader.activeOf`: the latest version per
    unit). Superseded versions, `rejected_history` and narrowings are not read.
  - An authored set is its one signed reading.
- A unit whose list uses a bound judgment syntactically, directly or through W3 definitions (D4), is OPEN: judgment
  dependence forces OPEN.
- Otherwise the legacy status applies: `Loader.w2Status` without an active set, `Loader.w2SetStatus` with one
  (`Loader.foldStatus`). An authored set whose reading depends on a judgment is OPEN, not CHECKED; a `contextual` or
  `unformalised` unit whose content uses one is OPEN, not LABELLED or UNFORMALISED (J-υ).
- Dependence does not follow rule chains: a rule whose guard reads a regulated predicate that another unit's rule decides
  on a judgment stays CHECKED (J-χ), although its outcome can still vary with that judgment. The unit that uses the
  judgment is OPEN, and the zone answer at a situation (JT-4) is the full answer.
- `residual.open_terms` is unchanged (declared terms).
- The document check gains one report field, `judgments`: for each bound judgment, the ids of the units that depend on
  it, plus the declared judgments that no unit uses. A unit represented only by a reading set appears in it. This is
  the static answer to "which rules depend on which judgment"; Lean computes it.

### 2.3 Checked, and not checked

**Checked by Lean:**
- the binding;
- the status rule;
- dependence through definitions;
- the usage map;
- consistency **whatever the judgments**, on the plain norm-defaults route. CONFLICT-FREE already quantifies over
  every base situation, so over every way of judging; the English line cites `conflictFreeU_consistent`
  (`lean/VE/NormDefaults/Status.lean:293`) itself. On the layered route CONFLICT-FREE assumes the route's own premises
  `L.X` (soft coherence, rights limitations), so its line names them and is never "whatever is judged" (2.4).
- with JT-4, consistency **given the criteria**: the criterion units as labelled premises in X, and `ConflictFreeX`
  (`lean/VE/NormDefaults/Layered.lean:159`, `layered_conflict_sound` at `:227`), reported apart from the answer
  without additional judgment criteria;
- with JT-4, zone answers at a situation: whether the outcome there is settled whatever the judgments, or two
  admissible completions give different answers and differ on named judgment atoms, each with its decider (the shown
  pair certified, R1); and whether a record of judgments is admissible or ruled out by named premises.

**Never checked:**
- any judgment itself;
- whether a decider considered the factors;
- the standard behind the word;
- where a vague boundary lies.

A record of judgments is a set of findings with a decider; answers under it say "given <decider>'s judgment that …".

### 2.4 English (texts for english-lean's rows; JT-E1 gates them)

The texts describe what Lean checked and nothing more: a `left to` answer names the witnessed pair of completions and
the atoms on which they differ, each with its decider; it does not claim that each atom controls the answer. JT-E1
measures proxy readability (a model standing in for a reader), not human comprehension.

| Row | Text | When |
|---|---|---|
| declaration | "Whether <the template with 'something' or the sort noun> is a judgment; the text does not say who makes it." / "… is a judgment for <decider>." | the legend of every bound judgment, one line per bound term (english-lean may group terms that share their words, D2; JT-E1 measures the grouped line if it does); also the authoring line that declares one. A template the wording lint rejects gives no wording to fill: the line falls back to today's identifier wording (JT-3) |
| legend, factors | "The text mentions these points: <factor>; <factor>." | when `factors` is not empty |
| unit status | "Open: this uses the judgment whether <atom>." | an OPEN unit's line, beside the source. Neutral on purpose: a criterion unit ("No arrest ordered by a court is arbitrary.") uses the judgment to limit it and does not depend on it |
| zone, settled | "Settled: whatever is judged here, the text requires …" | WG-7's settled answer when the cone has judgment atoms |
| zone, left to | "Left to <decider>: these two admissible completions give different answers and differ on whether <atom> (a judgment for <decider>)." / "… (the text does not say who makes it)." | WG-7's `left to` with judgment atoms; one clause per differing atom, each with its decider. What it says is what R1's certified pair (`LeftToPair`) proves of the shown completions |
| record | "Given <decider>'s judgment that <atom>, the text requires …" / "Ruled out: this judgment that <atom> contradicts <premise sentence>." | WG-7's record answers |
| conflict | "Conflict-free, whatever is judged." (`conflictFreeU_consistent`, plain route only) / "Conflict-free under the document's own conditions: <condition sentence>; …" (the layered route's `ConflictFreeX L.U L.X`, without additional judgment criteria) / "Conflict-free, given these sentences: <criterion sentence>; …", or with `L.X` "Conflict-free under the document's own conditions and these sentences: …" (`ConflictFreeX L.U (L.X ++ C)`, JT-4) / "These rules conflict where <atom>." | the document check's conflict line; the "given" line is shown beside the line without additional judgment criteria, never instead of it. "Whatever is judged" is used only for the plain route's unconditional answer |
| catalogue | "reasonable", "appropriate(ly)", "arbitrary/arbitrarily", "fair", "just", "legitimate", "genuine(ly)", "adequate", "effective", "necessary", "due", "good judgment", "overly <adj>": in translation, a bound judgment; never a definition the checker chooses. Each row is tied to its evaluative sense: "just" is not the "just" of "just as real" (C u0031.s03), "necessary" not that of "necessary condition", "due" not that of "due date" or "due to", "effective" not that of "effective date". "Overly cautious" is one judgment term, never "more cautious than appropriate" unless the text says "more … than". "Genuinely" with two readings ("genuinely arising": in fact arising; or arising in good faith) is a reading set. "Clearly" (evident, or a degree) is quantities' QX-2 row | english-lean's catalogue (O15) |
| refusal (authoring) | "'Reasonable' is a judgment. Say who decides it ('… is a judgment for the operator'), or define it ('In this document, a reasonable limit means …')." | an authored sentence that uses an undeclared evaluative word |

### 2.5 Zone answers with judgments (JT-4, on WG-6)

- At a situation `M`, the open atoms are WG-6's (decision atoms, unsaid atoms) plus the bound judgment atoms at every
  typed tuple of `M`.
- A **record** fixes some of them: a decider's findings.
- The answers, their evidence and budgets are WG-6's (`MAX_OPEN_ATOMS` 16; norm-defaults' status keeps 12).
- This plan adds three things:
  - the judgment names in `opens`;
  - the deciders of a `left to` answer, read from the records of the differing judgment atoms;
  - the theorem that the shown pair is certified (R1's `LeftToPair`: both completions admissible, opposite outcomes,
    agreement on every unsaid atom, and the differing atoms exactly those listed) and that every differing atom is a
    decision atom or a judgment atom.
- Fixture J-α (4.1): at an arrest `a`, "Left to no one the text names: these two admissible completions give
  different answers and differ on whether the arrest is arbitrary (the text does not say who makes it)." With the
  record `arbitrary(a)`, the answer is "settled: forbidden". With the record `¬arbitrary(a)`, it is "not said".
- **Criteria under premises** (D6, fixture J-ι): each asserted unit whose own formula content depends on a bound
  judgment and reads only base predicates is a labelled premise `judgment:<unit>`, appended to the layered route's X
  for the conditional conflict check only. Its answer is `ConflictFreeX L.U (L.X ++ criteria)`, shown as "Conflict-free,
  given …", beside the answer without additional judgment criteria. On the UDHR's plain route this needs R2.

## 3. Lean statements

Draft 2's statements are written out in full, elaborated against `main`, in [judgment-terms.md](judgment-terms.md)
(sections 1 to 7, with the stub's findings in its section 0); this section lists what each batch builds and what
changed from draft 1. Phase 1 changes no statement. The spec's draft 3 adds fixture J-ω, computed in the re-elaborated
stub. New files, in a new directory: `lean/VE/Judgments/Decl.lean`, `Scan.lean`, `Status.lean`,
`Examples.lean` (JT-1); `Zone.lean` and `ZoneExamples.lean` (JT-4). Plain-words companion: `lean/JUDGMENTS.md`. Names
have the prefix `VE.Judgments.`; `Loader` is `VE.Discourse.Loader`; `UnitContent` is `VE.Service.Document.UnitContent`;
`LayeredU`, `ConflictFreeX` and `conflictFreeX` are `VE.NormDefaults.Wire`'s.

### 3.1 W2, records and admission (JT-1, `Loader.lean` and `Decl.lean`; spec 1 and 2)

- `Loader.openTermNames` gains `(sorts : Bool := false)`: with it, repeated sorts are allowed; every other caller is
  unchanged. `openTermNames_sorts`: the flag only relaxes.
- `records rv j data formula : Except String (List Rec)` runs `openTermNames … (sorts := true)` first and then reads
  the fields it checked (`records_names`, `records_refuse`).
- `admit E defs regulated rs` reads the base vocabulary `hide E (names defs)`, where `defs` is the route vocabulary's
  `rv.definitions`; `faultOf` is checks 1–5 of 2.1. `faultOf_none_iff` (a record is admitted exactly when it is bound
  to a base predicate with its sorts, unregulated, without criterion lists, and not `unstated`), `admit_ok_iff`,
  `admit_first_fault`.

### 3.2 The shared scan (JT-1, `Scan.lean` and one hunk in `Rights/Run.lean`; spec 3)

- `opensIn J fs`: the names of `J` the formulas mention, in `J`'s order. `Scan.lean` imports only `VE.Norms.Tree`, so
  rights can import it. `opensIn_iff`, `opensIn_isEmpty`.
- Rights' `nodeOpen` calls it; `nodeOpen_eq` states today's body as an equation (proved in the stub).

### 3.3 Dependence, status and the usage map (JT-1, `Status.lean`; spec 4)

`Status.lean` does not import `VE.Service.Document`: the document mode calls it (JT-2), so the content type it reads is
its own, and the document mode maps its `UnitContent` onto it in one line.

- `Content` (a formula, or a rule read as its guard and carve-outs), `defEdges`, and
  `dependsOn defs J fs := opensIn J (fs ++ reachedBodies defs fs)` over the compiled definitions `defs`;
  `dependsOnC defs J cs` over a list of contents. `dependsOn_iff` (direct, or through a path of definitions),
  `dependsOn_no_defs`.
- **One traversal** (2.2): `UnitView` (id, meaning, listed names, asserted, own content, active set, whose candidates
  keep a pending reading as `none`), `UnitView.reads` (the own content, or the active set's elaborated candidates),
  `UnitView.complete` (with an active set, it has a reading and none is pending; without one, the unit has its own
  content), `UnitView.legacy` (today's status; `viewOf_legacy`: it is `Loader.foldStatus`'s value).
- `status defs J u`: the three unit refusals of 2.1 (the third only on a complete unit), then OPEN when the unit's list
  depends on a bound judgment, else `legacy`. `status_eq` (judgment dependence forces OPEN; otherwise the legacy status
  applies), `status_never_checked` (a judgment in the unit's own content or its definitions), `status_checked`,
  `status_ok_iff` (refused exactly when), `status_legacy`. Draft 1's separate `setStatus` is folded into `status`, since
  the view carries the active set.
- `usageMap defs J units`: `usageMap_sound`, `usageMap_complete`, `usageMap_unused`, `usageMap_rows` (no empty row).
- Draft 1's `conflictFree_every_judgment` is dropped: it restated `conflictFreeU_consistent` with an unused hypothesis.
  The unconditional English line (plain route only) cites `conflictFreeU_consistent` itself.

**Proof notes.**
- `dependsOn_iff` is `opensIn_iff` with `reachEval_iff` (`lean/VE/Closure/Paths.lean:190`).
- `status_*` are by cases on the definition.
- `usageMap_*` are list lemmas.

### 3.4 Criteria and zone answers (JT-4, `Zone.lean`; after WG-6; spec 5 and 6)

WG-6's plan states `zoneOf (L X M record r vs proposed)` with `openNames L := decisionNames L.D ++ unsaidNames L.U`
built in. This plan needs one change in WG-6's file: an explicit `opens` (request R1, section 11). WG-6's own answers
are the `opens = openNames L` instance.

- `criteria defs J base units`: each asserted unit with its own formula content, over base predicates only, that
  depends on a bound judgment, labelled `judgment:<unit>`. `criteria_iff`.
- `withCriteria L C` (the criteria after `L`'s labelled premises, read only by the conditional conflict check) and
  `conflictFree_given`: accepted certificates over that background give `ConflictFreeX L.U (L.X ++ C.map (·.2))` (the
  stub proved it from `layered_conflict_sound`). `conflictFree_given_mono` (draft 2's
  `conflictFree_unconditional_given`): the answer without additional judgment criteria implies the one given them;
  J-ι shows the converse fails. On the layered route neither answer is unconditional: both assume `L.X`.
- `opens L J := VE.Weighing.openNames L ++ J`, `zone`, `zone_settled`, `zone_leftTo` (the shown pair is R1's certified
  `LeftToPair`, and every differing atom is a decision atom or a judgment atom), `zone_no_judgments` (WG-6's answer
  when `J = []`). `leftToPair_leftTo` (the certified pair witnesses WG-6's `LeftToZ`) and `leftToPair_differ_ne_nil`
  (an empty `differ` is never certified) were proved in the stub over a stand-in `completionOf`.
- `deciders js differ`: `deciders_sound`, `deciders_complete`.

On the plain norm-defaults route (the UDHR's companions), `zone` and the criteria check need a `LayeredU` without packs
(request R2, section 11). Until it exists, JT-4's fixtures run on the layered route only.

### 3.5 The undeclared-word report (JT-3; spec 7)

- `undeclaredEvaluative rows preds J`: the base predicates (regulated ones included) whose words match a catalogue
  row, outside the row's other senses, and that are not bound. `undeclaredEvaluative_iff`.

### 3.6 What is not claimed

- No theorem says a judgment is right.
- **Declared terms only** (D15). An evaluative word written as an ordinary base predicate is not bound, and its unit
  can be CHECKED. `undeclared_evaluative` lists catalogue matches for review; it never claims that a unit contains no
  other judgment.
- No minimality of the judgments an answer lists: WG-6 lists exactly the atoms on which the two shown, certified
  completions differ, not a minimal set, and the English names them as such, never as each controlling the answer.
- "Conflict-free, given …" is not "conflict-free, whatever is judged": the two are reported apart. On the layered route
  neither is unconditional: both assume the route's own premises `L.X`, and the lines say so.
- No completeness beyond WG-6's budget: beyond it the answer is UNKNOWN with the budget as reason.
- No claim that a criterion written as a unit is faithful to the source: that is the audit's job.
- **No rule chains** (spec F3, settled by the statement review). Dependence is syntactic use, directly or through W3
  definitions; an outcome downstream, read through another rule's guard, can still vary with a judgment while its unit
  is CHECKED (J-χ). The zone answer at a situation is the full answer; JT-5 records each such unit.

## 4. Fixtures

### 4.1 Synthetic (`#guard` in Lean, and the same through the service in Python)

| # | Document | Expected |
|---|---|---|
| J-α | sorts `person`, `act`; base `arrest(act)`, `arbitrary(act)` (bound, `unresolved_decider`); a rule forbidding `subjects(person, act)` where `arrest(a) ∧ arbitrary(a)`; meaning `{"open": ["arbitrary"]}` | status OPEN; usage map `arbitrary ↦ [u1]`. JT-4: at `M` = one person, one arrest: `left to` (no one named), the two certified completions differ exactly on `arbitrary(a)`; record `arbitrary(a)` → settled no; record `¬arbitrary(a)` → not said. A wrong witness or an empty `differ` fails (A2's mutations) |
| J-β | J-α with meaning `"specified"` | `JudgmentNotChecked: u1 arbitrary` |
| J-γ | W3 `wrongful_detention(a) :↔ detention(a) ∧ arbitrary(a)`; a formula unit uses only `wrongful_detention`, meaning `"specified"` | `JudgmentNotChecked: u1 arbitrary` (dependence through a definition, D4) |
| J-γ′ | J-γ's twin in a rule unit: a rule whose guard uses only `wrongful_detention(a)`, meaning `"specified"` | `JudgmentNotChecked: u1 arbitrary` (D4 for rule units) |
| J-δ | open term `reasonable_limitation`, no predicate of that name | `JudgmentUnbound: reasonable_limitation` |
| J-ε | predicate `arbitrary(act)`, record `arguments: ["person"]` | `JudgmentArguments: arbitrary` |
| J-ζ | J-α's record with `necessary` = one formula | `JudgmentCriterionAsUnit: arbitrary` |
| J-η | J-α's record with `decided_by: "unstated"` | `JudgmentDecider: arbitrary` |
| J-θ | constant `the_family`; base `natural_and_fundamental_group_unit(thing)` (bound); assertion of it at `the_family`; meaning open | OPEN; usage map lists the unit (row 10's form, D11) |
| J-ι | J-α plus a rule permitting the arrest where `arrest(a) ∧ court_ordered(a)` (spec F2) | CONFLICT, witness with `arbitrary(a)` true: "These rules conflict where an arrest ordered by a court is judged arbitrary." The unit "No arrest ordered by a court is arbitrary." is a labelled premise in X on the layered route (JT-4; R2 for the UDHR): the answer is `ConflictFreeX`, "Conflict-free, given: No arrest ordered by a court is arbitrary.", shown beside the CONFLICT without additional judgment criteria, which stays (D6) |
| J-κ | 17 bound judgments in one guard over one tuple | JT-4: `unknown`, budget (17 open atoms, limit 16) |
| J-λ | each of J-α to J-θ without `judgments@0` | statuses and diagnostics as today, byte-identical (`status_legacy`; the profile-off path never calls `status`); zone answers as WG-6's (`zone_no_judgments`) |
| J-μ | a rule guarded by `arrest(a)` only, beside J-α's judgment declared and unused | settled whatever is judged; usage map lists `arbitrary` as unused |
| J-ν | a `scales@0` grade `gives_serious_uplift` that is also a W2 open term | binding passes; its atoms are judgment atoms in JT-4's zone |
| J-ξ | an **authored** reading set with its one signed reading (W2 allows no other), which uses `arbitrary`, on a unit with no content of its own | OPEN, where today's status is CHECKED (2.2); the usage map lists the unit (one traversal) |
| J-ξ′ | an **open** reading set of u055's two scopes, which really differ ("arbitrarily" over both acts, or over the deprivation only), both using `arbitrary`, with a distinguishing model that separates them (W2 requires one); no content of its own | OPEN; the usage map lists the unit |
| J-υ | a `contextual` unit whose formula uses `arbitrary` | OPEN, where today's status is LABELLED (F2) |
| J-τ′ | J-τ's meaning on units that are not complete: no own content; an active set whose readings are all pending; a set of one elaborated and one pending reading; own content beneath a set with a pending reading (the set takes precedence) | each OPEN, no `JudgmentListedUnused`; the same list on a complete authored set still gives `JudgmentListedUnused: u1 <the other>` |
| J-χ | J-α's unit, and a second rule unit, `specified`, whose guard reads the regulated `subjects` that J-α's rule decides | the second unit CHECKED; the usage map lists J-α's unit only (dependence does not follow rule chains, 2.2) |
| J-ο | a judgment over `["person", "person"]` | admitted under the profile; without it W2 refuses the record with its own text (`invalid open-term arguments`) |
| J-π | a W3-defined name (`wrongful_detention`) declared as a judgment | `JudgmentUnbound: wrongful_detention` (admission reads `hide E (names defs)`) |
| J-ρ | a regulated predicate (`subjects`) declared as a judgment | `JudgmentRegulated: subjects` |
| J-σ | two bound judgments used in one guard, meaning `{"open": ["arbitrary"]}` | `JudgmentNotListed: u1 <the other>` |
| J-τ | J-α's guard, meaning `{"open": ["arbitrary", <another bound judgment>]}` | `JudgmentListedUnused: u1 <the other>` |
| J-ω | one word over two sorts (D2, phase 1): sorts `measure`, `interference`; bound `arbitrary_measure(measure)` and `arbitrary_interference(interference)`, both with the template "{0} is arbitrary"; u037's rule uses the first, u045a's the second | both admitted; each unit OPEN; usage map `[(arbitrary_measure, [u037]), (arbitrary_interference, [u045a])]`, one row per term. The record `arbitrary_measure` with `arguments: ["interference"]` is `JudgmentArguments: arbitrary_measure` (one record cannot stand for the other sort) |

### 4.2 From the pilots (each sentence is the source text; ids from the run-20261012T1800Z ledgers)

| Unit | Sentence | Fixture use |
|---|---|---|
| U u037 | "No one shall be subjected to arbitrary arrest, detention or exile." | J-α's shape on the real translation once JT-5b runs; zone wording checked in JT-E1 |
| U u045a | "No one shall be subjected to arbitrary interference with his privacy, family, home or correspondence" | `arbitrary` reused across units and sorts. Corrected after phase 1 (P1 2.6): the run writes four predicates over four sorts in two parts. Part 1 has `is_arbitrary(measure)` (u037), `is_arbitrary_u045a(interference)` (u045a) and `is_arbitrary_u046(intrusion)` (u046). Part 2 has `is_arbitrary(measure)` (u055's two readings) and `is_arbitrary_u064(deprivation)` (u064). A usage map is per document, and D2 gives one bound term per sort, so there is one row per sort and per part: three in part 1, two in part 2 (J-ω's shape), never one row for all five units |
| U u055 | "No one shall be arbitrarily deprived of his nationality nor denied the right to change his nationality." | J-ξ′: an open reading set over the adverb's scope (act-phrases' D9), two readings that differ, with a separating model; the unit OPEN |
| U u111 | "… meeting the just requirements of morality, public order and the general welfare in a democratic society." | five bound judgments in one unit; the budget is not reached at one tuple each |
| U u089 | "Everyone has the right to rest and leisure, including reasonable limitation of working hours and periodic holidays with pay." | the catalogue row for "reasonable" (JT-3); not unlocked (time, R2.3) |
| U u010 | "Whereas a common understanding of these rights and freedoms is of the greatest importance for the full realization of this pledge," | JT-0p (two distinct legacy argument labels until JT-5b) and J-θ's binary form. Phase 1: OPEN in the checker (bar part A); renders with identifiers, since the wording lint rejects its template |
| U u060 | "The family is the natural and fundamental group unit of society" | JT-0p: written and audited, bytes unclaimed (`missing_feature: presupposition`, `claimed: false`); "the … unit" stays presupposition's. Phase 1: OPEN in the checker; its record is the only UDHR record the forecast admits (part 2) |
| C u0052.s01 | "Claude should always use good judgment when evaluating conversational inputs." | OPEN on `good_judgment`, a holistic judgment that is never decomposed. JT-5a confirms that `good_judgment(action, context)` sits in a guard, not as the regulated act (`JudgmentRegulated` otherwise); if it cannot sit in an admitted role, the limit is recorded, not worked around. Phase 1: no predicate `good_judgment` exists; the judgment sits inside the regulated `judgment_use_required` (P1 2.6) |
| C u0168.s01 | "When faced with seemingly compelling arguments to cross these lines, Claude should remain firm." | OPEN on `seemingly_compelling_argument_to_cross_line`; zone at the 49 probe points after JT-4 |
| C u0031.s03 | "The risks of Claude being too unhelpful or overly cautious are just as real to us as the risk of Claude being too harmful or dishonest." | catalogue row for "overly": one judgment term; the comparison of risks stays quantities' and weighing's. "Just as real" is the "just" of "equally", not the evaluative row: the reason catalogue rows are tied to a sense (2.4) |
| Safety framework F18 | "It is reviewed more often when there are reasonable grounds." | a bound judgment with a named decider ("we"), `left to` names it |

## 5. Batches

Every batch lists its files. A **shared file** is one that another plan or in-flight branch also edits; the rest are
new. Generated files are regenerated with their own tool (`tools/regen_generated.py --write`, or `--resolve` after a
merge), never edited or merged by hand. Each batch plants a bug in each behaviour it claims, in each language it
changes, shows a failing test, and restores it (CLAUDE.md).

### JT-0p. Pilot: measure judgment terms; asserted judgments (2 h; pilot; first batch)

- **What.** Text for the DRI's merged pilot prompts (`manage-agents/prompts/pilot-additions.txt`,
  `udhr-additions.txt`, and their audit additions). No repository file.
  1. **Instrument, both ledgers.**
     - Each declared or annotated open term gets a class in `metrics.json` under `open_term_class`, by R2.1's rule:
       `judgment`, `classification`, `exception`, `attitude` or `proportion`.
     - Each unit gets `judgment_terms` (its open terms of class `judgment`).
     - `metrics.json` gets `judgment_term_units` and `judgment_term_bytes`, by status and by `missing_feature`.
     - Added in draft 4 (review finding 6): `metrics.json` also gets `open_term_class_borderline`. It lists the terms
       of class `judgment` that mix a classification with a judgment (R2.3's "borderline"), so the counts can be given
       with and without them (P1 1.3.4).
  2. **UDHR u010 and u060 as asserted judgments.** This batch adds no profile, so W2's profile-off validator applies.
     - u010: binary `of_greatest_importance_for` between two named things. W2 refuses repeated `arguments` without
       the profile, so the record lists two distinct legacy argument labels, never `["thing", "thing"]`; the
       predicate keeps its sorts `(thing, thing)`. JT-5b replaces the labels by the sorts when the profile is switched
       on. No sort is invented beyond `thing`, which parts 1 and 2 did not declare and which the sorts `(thing, thing)`
       need (P1 1.3.2). The arity does not change.
     - u060: unary `natural_and_fundamental_group_unit_of_society` on `the_family`.
     - Both have `decided_by: "unresolved_decider"` and factors from the words. Each is a ground assertion with the
       meaning `{"open": [...]}`, so its status is OPEN.
     - u060's note says that "the" (uniqueness) is not represented and is presupposition's. u060 is written and
       audited, but its bytes stay unclaimed, recorded as `missing_feature: presupposition`: a unit whose meaning is
       admittedly partly missing contributes no whole-unit FAITHFUL bytes.
     - **What phase 1 needed** (P1 2.1, D1 to D3; the text is P1's `prompt-additions.md`):
       - the two new records replace the unused placeholders `greatest_importance` and `natural_group_unit` in the one
         record list all four parts share, so no second record holds the same words;
       - the reading sets of parts 1 and 2 are rebuilt as the pilot's build does: every meaning, model and situation
         id is a digest over the environment, and the new sort, constants and predicates change it;
       - constants carry `sort` and `description` only (the Rust checker and `v0-language.md:23` refuse a
         `verbalisation`);
       - `of_greatest_importance_for` gets no template: the lint rejects it, and its head word "is" would take 13
         other part-1 predicates' wording away (P1 F1);
       - the ledger marks u060 `claimed: false`, and the pilot's claimed bytes leave out every unit so marked. The
         checker counts u060 OPEN, so without this its 66 B would be claimed.
  3. **Audit addition.** A targeted blind audit of u010 and u060. On the sampled units, auditors also check that no
     CHECKED unit's content uses an open-term predicate, or an evaluative word of 2.4's catalogue written as an
     undeclared predicate (by hand, until JT-3's `undeclared_evaluative` lands; D15).
- **Pre-registered bar.** The four UDHR parts load and check as before, with u010 and u060 OPEN.
  - **PASS** if the targeted audit finds u010 FAITHFUL: claimed bytes +132 (4,792 → 4,924 B, 43.90% → 45.11%).
  - **FAIL** otherwise: u010 reverts and the reason is recorded.
  - u060's audit verdict is recorded; it claims no bytes either way.
  - The instrument has no bar; its numbers start a series. JT-E3 tests its reliability.
- **Phase 1 (P1 2.2).** The bar is unchanged and its two parts are reported apart. **Part A** ("load and check as
  before, with u010 and u060 OPEN") is **PASS** on copies of the pinned run. **Part B** (the targeted audit, and with
  it the +132 B) is **DEFERRED** until the DRI merges the prompt text and a UDHR run audits blind (0.2). The
  instrument's first point is in 0.1. The by-hand integrity check found no hidden judgment in the 20 CHECKED units.
- **Bytes.** UDHR +132 B (**estimate**, until the audit). Constitution 0 B.
- **Dependencies.** None in the repository; the next UDHR and constitution runs (06:00/18:00 UTC).
- **Conflicts.** None: prompts are merged by the DRI into one file per pilot (DRI SC2), and pilot runs are
  sequential.

### JT-0. Statement spec and stub (3–4 h; planner, then reviewers)

- **What.**
  - `docs/spec/judgment-terms.md`: draft 2's statements of section 3, elaborated against `main`, with the fixture
    values computed in Lean.
  - A stub (`lean/SpecStubs_judgment-terms.lean`), untracked and deleted before commit, run with `lake env lean`. It
    records every change the elaboration forces (exact field names of `VE.Definitions.Def`, `UnitContent`,
    `VE.Norms.Node`, and WG-6's names), and elaborates in particular: admission through `hide`; repeated sorts under
    the profile; the single candidate traversal; the compiled definitions interface; the `ConflictFreeX` claim; the
    `opensIn` equation.
  - Statement review: Sol stands in for Astra, Fable is arbiter (current DRI policy).
- **Gate.** The review passes, or each FIX is applied and re-checked once. No product code is written before it
  passes.
- **Files.** New: `docs/spec/judgment-terms.md`. Nothing shared.
- **Status.** Done: spec draft 2 (`85d6372d`). Draft 3 adds J-ω (D2's several sorts), computed in the re-elaborated
  stub; no statement changed.

### JT-1. Lean core (5–6 h; Lean)

- **What.** Sections 3.1 to 3.3 in `lean/VE/Judgments/{Decl,Scan,Status,Examples}.lean`, with fixtures J-α to J-θ,
  J-γ′, J-λ, J-μ, J-ξ, J-ξ′, J-ο to J-τ, J-τ′, J-υ, J-χ and J-ω as `#guard`s (and the spec's *internal* rows, which W2
  refuses on the wire), and `lean/JUDGMENTS.md`, every definition and theorem in plain words. No route, no service
  change.
  - W2's profile flag in `Loader.openTermNames` (one hunk; every existing caller unchanged, J-λ guards the text with
    the profile off).
  - The shared scan `opensIn` in `Scan.lean`, and rights' `nodeOpen` switched to it, with the equation theorem
    `nodeOpen_eq` (today's body); rights' frozen fixtures pass unchanged, so its output bytes do not move. Rights'
    own checks (default mode, alterable parties, limitations, bars) are not touched.
- **Shared files** (one hunk each):
  - `lean/VE.lean`: four imports;
  - `lean/VE/Audit.lean`: the theorem names of 3.1 to 3.3;
  - `lean/VE/Discourse/Loader.lean`: the `sorts` flag;
  - `lean/VE/Rights/Run.lean`: `nodeOpen` and `nodeOpen_eq`;
  - the generated statement, declaration and axiom inventories, and the frozen-sources inventory
    (`lean/VE/Route/frozen-sources.sha256`, which lists both `Loader.lean` and `Rights/Run.lean`), regenerated by
    their generators (`tools/regen_generated.py --write`).
- **Seeded bugs (Lean):**
  - `dependsOn` without the definition closure: J-γ and J-γ′ fail;
  - `status` returning CHECKED for `specified` content that uses a judgment: J-β fails;
  - `admit` reading `E` instead of `hide E (names defs)`: J-π is admitted and its fixture fails;
  - `admit` checking arguments before binding: J-δ's text changes;
  - rights' `nodeOpen` switched to `opensIn openNames [N.guard]` (carve-outs dropped): `nodeOpen_eq` no longer
    proves, so the build fails;
  - `JudgmentListedUnused` checked without `complete`: J-τ′'s incomplete units are refused and their fixture fails;
  - `complete` reading the unit's own content before its active set: J-τ′'s unit with own content beneath a pending
    set is refused and its fixture fails.
- **Dependencies.** None in flight: the directory is new; `Loader.lean` and `Rights/Run.lean` get one hunk each, and
  `Closure/Paths.lean`, `Definitions/Layer.lean` and `NormDefaults/Status.lean` are only imported.

### JT-2. `judgments@0` in Lean's document mode (5–6 h; Lean, Python)

- **Lean:**
  - In `lean/VE/Service/Document.lean`'s `check`, when the profile is on (spec 8.1):
    - `Judgments.records` in place of `Loader.openTermNames` (which it runs first), then `Judgments.admit` over
      `E.rv.environment` and `E.rv.definitions`;
    - after the fold, each unit's view (`Judgments.viewOf`: its own content with `UnitContent` mapped onto
      `Judgments.Content`, or its active set's candidates read from the raw readings, formula and norm, never from
      `readingsSets`' `top` projection, a pending reading kept as `none`), and its status from `Judgments.status`, in
      unit order; this covers the W2 sets and `readings@1`'s sets alike (the profile-off path is unchanged, J-λ);
    - the report gains `judgments` (the usage map, spec 8.3).
  - The profile's row in AR-10's table (`lean/VE/Compose/Dispatch.lean`): it requires `documents@1` and composes with
    `norms@0`, `norm-defaults@0`, `readings@1`, `definitions@0`, and `scales@0` and `attitudes@0` when those land. It
    refuses nothing, and the batch proves the composition statement for each newly admitted combination (SYNTHESIS
    2.2).
  - The response shape of the document mode's new field, and its encoder theorem (`lean/ResponseShape/Schemas/` and
    `Encoders/`, the document mode's files).
- **Generated:** the document mode's JSON schema under `ve/backends/lean_service_schema/` via
  `uv run python tools/response_schemas.py --write`; the gate's inventories via `tools/regen_generated.py --write`.
- **Python:**
  - The relay checks the new field's schema and binding only: every unit id is a unit of the request, every name is a
    declared open term, and no row is empty or extra (R8). It also checks Lean's order (spec 8.3): terms in
    declaration order, unit ids in the request's unit order, so that a reordered answer is `CheckerUnavailable`.
  - Fuzz tests in `tests/test_judgments_answer.py`: each member dropped, emptied, retyped, duplicated or reordered, an
    id pushed out of range. Every mutant is `CheckerUnavailable` or changes nothing shown.
  - Fixtures recorded in `tests/data/route-cases.jsonl` by the recorder.
  - The live document path stops calling `ve/openterms.py`: Lean's diagnostic is relayed. The file stays only while
    `tests/frozen_speech/speech_document.py` (frozen) imports it; the layer policy entry says so.
- **Seeded bugs:**
  - Lean: the status hook skipped under the profile, so J-β passes as CHECKED and the test fails.
  - Lean: the set candidates read through `readingsSets`' projection (norm candidates as `top`), so a norm-candidate
    variant of J-ξ is reported unused and its fixture fails.
  - Python: the relay accepts an id outside the request, so the fuzz test fails.
  - Python: the relay skips the order check, so the reorder fuzz test fails.
- **Dependencies.**
  - `lf-16g` (Lean document mode owns `ve document`; SYNTHESIS 4.2 queue: after `lf-16g`, AT-3b, SC-1b, QT-A4,
    ET-5, WG-4, ME-10 "in landing order"; JT-2 joins that queue);
  - AR-10's table on `main`.
- **Shared files:**
  - `lean/VE/Service/Document.lean`: the records and admission hook, the unit status hook and the report field (three
    hunks);
  - `lean/VE/Compose/Dispatch.lean`: one table row;
  - the document mode's ResponseShape files;
  - `ve/document.py` while it exists (one call removed);
  - `tools/layer_policy.py` (one entry).

### JT-E1. Readability (3 h; experiment; before JT-3)

Pre-registered in section 6.

### JT-3. English rows and the undeclared-word report (5–6 h; english-lean owner, Lean, Python)

- **What.** The rows of 2.4, in english-lean's files (`lean/VE/EnglishGrammar/*`) and its catalogue:
  - the declaration line, parsed in authoring to a W2 record and its predicate;
  - the legend and status lines (the status line neutral: "uses the judgment whether …");
  - the catalogue rows for the evaluative words, each tied to its evaluative sense, with their refusals and rewrites.
- **The `undeclared_evaluative` report** (D15, spec 7 and 8.4):
  - Lean computes it in the document mode from english-lean's single catalogue: the base predicates (regulated ones
    included) whose words match a row and that are not bound. It reports "these words match the catalogue; review
    them" and never claims that a unit contains no other judgment.
  - Its response shape is typed, with its encoder theorem; the generated schema is regenerated by its tool.
  - The Python relay checks the schema and binds it: each listed name is a base predicate of the request (a regulated
    one included, spec 8.4) and is not bound. A genuine answer naming a regulated predicate is accepted. Fuzz tests
    retype and rebind it.
- **Templates the lint rejects** (phase 1). The declaration and status lines fill the predicate's template. The
  wording lint rejects both of JT-0p's templates: u010's for `BINARY_AUXILIARY`, `BINARY_CONVERSE`, `LOGICAL_WORD`
  and `SYMBOL_COLLISION`, u060's for `LOGICAL_WORD`, `TEMPLATE_LENGTH` and `UNARY_MODIFIER` (P1 2.2). For such a term
  the lines fall back to today's identifier wording, and JT-3 adds no second source of templates (one owner). JT-E1's
  report counts its items whose judgment had no accepted template. Finding F1 (a rejected template still claims its
  head word) is english-lean's (11.2, X2). JT-3's lines read templates but declare none of their own, so F1 does not
  block JT-3.
- **Not this batch.** The zone, record and conflict wordings (2.4) are WG-7's display rows, extended in JT-4.
- **Queue.** english-lean's single queue on `lean/VE/EnglishGrammar/*` (SYNTHESIS 4.1 item 7: AT-5 → QT-A6 → ME-11 →
  QT-B3 → SC-7). JT-3 joins in landing order; it depends on none of them. The report's hunk joins the
  `Service/Document.lean` queue after JT-2.
- **Seeded bugs:**
  - Lean: the legend line drops the decider; the row fixture fails.
  - Lean: the report ignores a row's other senses, so `due_date` is listed and its fixture fails.
  - Python: the relay accepts a listed name that is a bound judgment; the fuzz test fails.
  - Python: the relay refuses a regulated predicate; the regulated row's relay test (spec 11.7) fails.
- **Shared files:** english-lean's grammar and catalogue files; `lean/VE/Service/Document.lean` (the report field, one
  hunk); the document mode's ResponseShape files and generated schema; the document relay and its tests.

### JT-4. Judgment atoms in zone answers (4–5 h; Lean, Python)

- **What.** Section 3.4 in `lean/VE/Judgments/{Zone,ZoneExamples}.lean`, with fixtures J-α (zone part), J-ι, J-κ and
  J-ν.
  - WG-7's two kinds read `judgments@0`: with the profile on, `opens` includes the bound judgments.
  - The `left to` answer names the deciders (`deciders`), each with its differing atom; `zone_leftTo` certifies the
    shown pair (R1's `LeftToPair`).
  - J-ι is checked under its premise: the criterion units are labelled premises (`criteria`), and the conditional
    answer is `conflictFree_given`'s `ConflictFreeX`, reported beside the answer without additional judgment criteria,
    never instead of it.
  - The English rows of 2.4 for zone, record and conflict are added to WG-7's display.
- **Python:** the relay binds the deciders to the request's open-term records. Fuzz cases are added to WG-7's fuzz
  file, among them A2's two mutations of J-α's `left to` answer: a wrong witness (one witness replaced by the other, or
  one of its atoms flipped) and an empty `differ`. Each is `CheckerUnavailable` (an empty `differ` is an empty row; a
  `differ` that is not exactly the atoms on which the two shown witnesses differ is unbound) or changes nothing shown.
- **Seeded bugs:**
  - Lean: `deciders` reads the first record only; `deciders_complete`'s fixture fails.
  - Lean: `zone` returns its first witness twice, or an empty `differ`; J-α's pair fixture fails.
  - Python: a decider not in the request is accepted; the fuzz test fails.
  - Python: the relay accepts an empty `differ`; its fuzz test fails.
- **Dependencies.** WG-6 and WG-7 on `main`, and request R1 (WG-6's explicit `opens` and the certified pair
  `LeftToPair`). R2 is needed for the UDHR's plain route, for zone answers and for J-ι's premise alike; without it the
  UDHR waits.
- **Shared files:**
  - `lean/VE/Weighing/Zone.lean`: R1's parameter and `LeftToPair`, if WG-6 has not already landed them;
  - WG-7's kind dispatch: one condition;
  - WG-7's ResponseShape file: a `deciders` member, if WG-7's shape lacks one;
  - `lean/VE.lean`, `lean/VE/Audit.lean`.

### JT-5. Pilots switch on: JT-5a (constitution), JT-5r (UDHR re-translation), JT-5b (UDHR)

Draft 3 had one batch. Phase 1's admission forecast (P1 2.6) splits it. 31 of the constitution's 33 records already
name a predicate with their sorts. **None** of the UDHR's 52 does: every record would be refused, first as
`JudgmentUnbound`. So the constitution switches first, and the UDHR switches after a re-translation step.

**Common to JT-5a and JT-5b.**
- **What.** Prompt additions: the pilot adds `judgments@0`, and each open term is bound to its predicate.
  - Until JT-3's `undeclared_evaluative` lands, the audit checks by hand for evaluative words written as undeclared
    predicates (D15).
  - Each unit whose rule guard reads a regulated predicate that another unit's rule decides on a bound judgment
    (J-χ's shape) is recorded unit by unit: its status stays as computed, and its outcome can still vary with the
    judgment (2.2).
  - **Rebuild** (P1 F3). Switching the profile on changes the environment id, and every reading-set id is a digest
    over it. So every reading set of the document is rebuilt with the pilot's own build (`_reidentified` in
    `tools/readings_s1_pilot.py`), not only the sets of units that change. The rebuild is committed as a script command
    with its self-test: with no added vocabulary, it reproduces every reading set byte for byte (review finding 1).
  - `decided_by: "unstated"` becomes `unresolved_decider` (D7).
- **Bar** (unchanged from draft 3). Every claimed unit keeps its status or moves to OPEN; no unit moves to CHECKED. A
  move to OPEN can come from CHECKED, or from LABELLED or UNFORMALISED when a `contextual` or `unformalised` unit's
  content uses a judgment (J-υ). Any move to OPEN is a finding: a judgment that was shown as checked or labelled,
  recorded unit by unit. No declaration is removed (no open term dropped from `open_terms`) to reach CHECKED.
- **What the bar means for unused records** (draft 4; P1 2.6, item 2 of its section 3). A record that no unit of the
  document uses may be removed to pass admission, with its reason recorded. "Uses" means that the unit lists the record
  in its meaning or in its ledger `open_terms`, and the usage map then lists the record as used. Removing such a record
  cannot change any unit's status, so it cannot reach CHECKED: a unit's status and refusals read only the judgments
  its list depends on and those its meaning lists (`status_eq`, `status_ok_iff`), and an unused record is neither. A
  used term is never removed. Usage is per document: a record that a shared list carries into a part where no unit
  uses it is unused there.
- **Expected moves: none.** No CHECKED or LABELLED unit with content in either pilot uses a judgment (0.1: no hit in
  20 units, and the control finds 35 of 49). A move to OPEN would be a finding, as the bar says.
- **Conflicts.** None in the repository.

#### JT-5a. The constitution switches on (2–3 h; pilot)

- **What.** The main document adds the profile. The u0165.s01–s07 rules keep queue 4.4's text; only the profile and
  the binding change, at a run after the queue's current step. Two of the 33 records need work (P1 2.6):
  - `good_judgment` has no predicate. u0052.s01's judgment sits inside the regulated `judgment_use_required` ("use
    good judgment" is the act). The runner first tries to write `good_judgment(action, context)` as a base predicate
    in a guard, not as the regulated act (D2). If it cannot sit in an admitted role, the constitution is **not**
    switched on. The refusal is recorded verbatim and goes to the DRI. No declaration is removed and no unit is
    reverted to pass admission.
  - `child_sexual_abuse_material`: the record's arguments `[material, context]` become the predicate's sorts
    `[situation]`, as u010's legacy labels do in JT-5b. The record's labels predate the profile, and the units use the
    predicate.
  - No constitution record says `unstated`.
- **Bytes.** 0 claimed. Statuses are Lean-computed on 13 units, 2,150 B: OPEN 12 (2,082 B) and READINGS 1 (68 B)
  (measured, `instrument-constitution.json`; one rater). Without the units whose only judgment terms are borderline
  (u0062.s01, u0123.s01.p1, u0123.s02.p1, u0123.s03), they are 9 units, 1,186 B. Only units with content count. The
  LABELLED heading u0126 (19 B, annotated `ethical_harm`) has none, so its status cannot change. These figures fill
  draft 3's placeholder CONSTITUTION-OPEN-JUDGMENT.
- **Dependencies.** JT-2 on `main` and in the pilots' green tag; JT-4 for the zone probes.

#### JT-5r. The UDHR's re-translation (4–6 h, **estimate**; pilot runner under act-phrases' rules; new)

- **Why** (P1 2.6, the forecast and the ledger). No UDHR predicate has an open term's exact name. 36 of the 52
  terms are used: 18 judgment, 16 classification, 1 attitude and 1 proportion. Under D5 all of them are bound alike.
  - Five used terms have a predicate of their own under another name, and need only a rename: `is_arbitrary*`,
    `is_slavery*`, `is_servitude`, `is_slave_trade` and `is_determined_by_law`. `arbitrary` becomes four bound terms
    (D2, J-ω).
  - The other 31 sit inside a larger predicate (a right, a regulated act or a relation), or in no predicate. For
    example, `effective` is inside `has_the_right_to_an_effective_remedy`, and `persecution` inside
    `has_the_right_to_seek_and_enjoy_asylum`.
  - Binding these 31 changes audited units. Draft 3's "rename either the predicate or the term" holds only for the
    five.
- **What.** Prompt text for the UDHR. No profile is switched on, and no product code changes.
  1. Each used term gets a base predicate of its own, with its sorts, one per sort (D2). Where one exists, it is
     renamed. Otherwise the judgment is split out of the larger predicate as a conjunct (D10: "an effective remedy"
     is `remedy(x) ∧ effective(x)`), or a predicate is added where the term is in none.
  2. A record with `arguments: []` gets its predicate's sorts.
  3. Each part keeps the records its units use. Unused records are removed with their reason, as JT-5's bar allows
     (16 terms are used by no unit in any part).
  4. Every changed unit is re-audited blind, by an auditor that did not write it.
- **Bar.** Every changed unit is re-audited FAITHFUL and keeps its status, and the claimed bytes do not change (4,792 B,
  or 4,924 B after JT-0p's PASS). A unit that fails reverts to its previous text, with the reason recorded. Its part
  then waits in JT-5b until it passes; the other parts go ahead.
- **Size.** At most 32 units and 3,939 B are touched. This sums the class rows of `instrument-udhr.json`: 18 units
  carry a judgment term (1,945 B), 12 a classification term (1,699 B), 1 an attitude term (225 B) and 1 a proportion
  term (70 B). The overlap was not measured, so a unit with terms of two classes is counted twice.
- **Owner.** Proposed: the pilot runner, under act-phrases' attachment rules (AP-5b, D10), with act-phrases reviewing
  the splits. The DRI decides (11.2, X1). No act-phrases file changes.
- **Dependencies.** The DRI's decision on the owner. JT-0p's audit first, so that u010's record is final and two prompt
  changes never touch part 1 at once.
- **Bytes.** 0 gained.

#### JT-5b. The UDHR switches on (2 h; pilot)

- **What.** The four parts add the profile; u010's legacy argument labels become the predicate's sorts
  `["thing", "thing"]`. The runner re-checks the four parts and their companions and records the usage map: one row
  per sort and per part (4.2, J-ω).
- **Bytes.** 0 claimed. Statuses are Lean-computed on 18 units, 1,945 B (OPEN 14 with 1,200 B, READINGS 4 with 745 B;
  measured, `instrument-udhr.json`, equal to P7). With JT-0p's u010 and u060 the figures are 20 units, 2,143 B (OPEN
  16 with 1,398 B, READINGS 4 with 745 B; `instrument-udhr-jt0p.json`).
- **Dependencies.** JT-5r re-audited (per part); JT-2 on `main` and in the pilots' green tag; JT-4 for the zone probes,
  with R2 for the UDHR's plain route.

### JT-E2 and JT-E3 (experiments)

Pre-registered in section 6.

## 6. Experiments (pre-registered; each runs only under its own authorisation, with model calls budgeted by the DRI)

### JT-E1. Do readers see which answers turn on which judgment?

- **Design.** Sonnet 5.5 as the proxy reader, with only what a human gets, as in the readability eval of 2026-10-03.
  - 40 items: 20 UDHR (u037, u045a, u046, u055, u064, u111, J-ι's criterion unit "No arrest ordered by a court is
    arbitrary." and synthetic variants), 20 constitution (u0052.s01, u0168.s01, the hard constraints as QT-B4 leaves
    them, synthetic variants).
  - Two arms: today's rendering (identifiers, 'classified as "arbitrary"') and 2.4's English.
  - Each item asks which conclusions hold whatever is judged and which turn on a judgment, and on whose.
- **Bars.**
  - (a) At least 90% correct with 2.4's English, and at least 15 points above the identifier arm.
  - (b) No critical misreading in 40: an answer that turns on a judgment read as settled or checked.
- **What it measures.** Proxy readability (a model standing in for a reader), not human zero-training comprehension;
  the report says so.
- **Then.** If either bar fails, JT-3's wording is revised once and re-run on fresh items. If it fails again, JT-3
  lands with the legend line only and the zone rows wait.
- **Status.** Not run: **DEFERRED** (0.2). Phase 1 confirms the identifier arm as written: JT-0p's asserted judgments
  render as 'Open reading: "the_family" is classified as "natural_and_fundamental_group_unit_of_society"' (P1 2.2).
  The report also counts the items whose judgment has no template the lint accepts (JT-3). The bars are unchanged.

### JT-E2. Judgments over propositions (research JT-R1)

- **Question.** Can "it is essential/important/better that P" be written faithfully, without new semantics, as an
  attitude guard node with the document as holder and the judgment as mode?
- **Items.** The 15 constitution units found by excerpt search (R5.2; 2,952 B) and UDHR u006 and u007 (286 B): 17
  units.
- **Protocol.**
  - A translator writes the candidate form under attitudes' content rules (quantifier-free content, one slot).
  - A different model audits blind.
  - Units whose other blockers are not yet met are written as partial companions and not claimed.
- **Bar.** At least 13 of 17 FAITHFUL, and none with invented content. AT-3a must be on `main`.
- **Then.** On PASS, a build batch is planned for the content-node reuse (shared piece S9). On FAIL, the units stay
  UNFORMALISED and the failure classes are recorded.
- **Status.** Not run: **DEFERRED** until AT-3a is on `main` and the DRI authorises it (0.2). Phase 1 measured nothing
  that bears on it.

### JT-E3. Can the judgment class be measured?

- **Items.** 60 open terms, sampled stratified from both ledgers' instruments (JT-0p).
- **Protocol.** Two raters (two different models) classify each term by R2.1's rule, independently.
- **Bar.** Cohen's κ at least 0.7.
- **Then.** If the bar fails, the instrument reports only "open term", and judgment-term counts are not published as
  measured.
- **Status.** Not run: **DEFERRED** until the DRI authorises it (0.2). Its input exists: the frame is P1's
  `open_term_class.tsv`, one rater's classes for 89 distinct terms (UDHR 52, constitution 37).
- **Reporting** (added in draft 4; the bar is unchanged). The constitution's counts turn on five heavily annotated
  terms: `ethical_harm` (275 units), `broad_safety` (222), `genuine_helpfulness` (88), `appropriate_oversight` (60)
  and `good_judgment` (42) (P1 2.4). The sample therefore includes all five. The report gives the judgment-term counts
  with and without the terms the raters disagree on, and with and without the borderline flag
  (`open_term_class_borderline`).

## 7. Dependencies and merge safety

| Item (branch) | Needed by | How this plan avoids conflicts |
|---|---|---|
| `lf-16e/f/g` (Lean document mode) | JT-2 | JT-2 starts after `lf-16g` merges, in SYNTHESIS 4.2's queue for `Service/Document.lean` |
| AR-10's profile table | JT-2 | one row, after the table lands (SYNTHESIS 4.3: "the table lands before any new profile row") |
| `rd-9/integrate` (RD-9), PK-1 | WG-6, hence JT-4 | JT adds no pack: bound judgments are declared base predicates, not generated ones, so PK-1's `packOrder` gains no row. The criteria are appended to X only inside the conditional conflict check (`withCriteria`), never to PK-1's assembled X |
| frozen sources: `lean/VE/Discourse/Loader.lean`, `lean/VE/Rights/Run.lean` | JT-1 | one hunk each, byte-neutral for every existing caller (J-λ, `nodeOpen_eq` and rights' frozen fixtures); `lean/VE/Route/frozen-sources.sha256` is regenerated by its tool after a merge, never merged by hand |
| WG-6, WG-7 (weighing plan) | JT-4 | JT-4 is a new file plus R1 (one parameter and the certified pair `LeftToPair`) and one condition in WG-7's dispatch; if WG-6 lands with both, JT-4 edits no weighing file |
| english-lean's queue | JT-3 | joins the queue in landing order; touches no other file |
| `qa-q2`, `lean-first/b14b`–`b14d`, `lf-16e/f` (editors of `Protocol.lean` and `service_schema.py`) | none | JT adds no service mode (SYNTHESIS C9) |
| quantities (`scales@0`) | J-ν only | no shared file: a grade's binding is checked by JT's admission over the same W2 records |
| queue 4.4 (u0165.s01–s07) | JT-5 (now JT-5a) | JT changes none of those units' text; the profile switch runs at a pilot run after the queue's current step |
| act-phrases' attachment rules (AP-5b; D10) | JT-5r (added in draft 4) | JT-5r is prompt text only and edits no act-phrases file; who owns it is 11.2's X1 |

**Shared files, all batches:**
- `lean/VE.lean`, `lean/VE/Audit.lean`;
- `lean/VE/Discourse/Loader.lean` and `lean/VE/Rights/Run.lean` (JT-1, one hunk each);
- `lean/VE/Service/Document.lean` (JT-2, and JT-3's report field);
- `lean/VE/Compose/Dispatch.lean`;
- the document mode's ResponseShape files;
- `lean/VE/Weighing/Zone.lean` (R1, only if needed);
- WG-7's dispatch and ResponseShape;
- `lean/VE/EnglishGrammar/*`;
- `ve/document.py` (while it exists) and the document relay's tests;
- `tools/layer_policy.py`;
- the generated inventories, the frozen-sources inventory and the generated schemas (by their tools only).

## 8. Bytes, by batch

| Batch | Constitution (184,893 B) | UDHR (10,916 B) | Kind |
|---|---|---|---|
| JT-0p | 0 | +132 B claimed (u010; u060 written and audited, 66 B unclaimed: `missing_feature: presupposition`): 4,792 → 4,924 B, 43.90% → 45.11%. Measured so far: the checker's OPEN bytes rise by 198 B (bar part A); the claim waits for part B | **estimate**, until the targeted audit (DEFERRED, 0.2) |
| JT-1 to JT-4 | 0 | 0 | integrity, answers, English |
| JT-5a | 0 claimed; Lean-computed status on 13 units, 2,150 B (9 units, 1,186 B without borderline-only units) | — | integrity; **measured** (P1 2.4, one rater) |
| JT-5r | — | 0 gained; at most 32 units, 3,939 B re-translated, each keeping its claim only if re-audited FAITHFUL | at risk, not gained |
| JT-5b | — | 0 claimed; Lean-computed status on 18 units, 1,945 B (20 units, 2,143 B with JT-0p) | integrity; **measured** (P1 2.4, equal to P7) |
| JT-E2 (if PASS, then a build) | up to 2,952 B, co-blocked by norms, quantities, attribution, causation or modality | up to 286 B (u006, u007), co-blocked by modality | **estimate**, upper bound |

No sum across rows: the bytes overlap with other plans' claims, and NORTH-STAR's rule forbids summing.

**Where D15's report will first matter** (measured, P1 2.4; no bytes). Some units contain a word of 2.4's catalogue
but carry no judgment term. Every one of them is UNFORMALISED today: UDHR 8 units (1,433 B), constitution 80 units
(16,755 B). Every covered unit with a catalogue word already carries a judgment term (UDHR 8 of 8, constitution 4 of
4). Once the 88 units are formalised, `undeclared_evaluative` is what flags an evaluative word left undeclared.

## 9. Risks and limits

- **The need is small in bytes.** R2 measures that judgment terms block 198 B as a primary blocker. If the DRI ranks
  by bytes, this plan's build batches rank low; their case is integrity (D3), answers (JT-4) and English (JT-3).
- **JT-4 waits on a chain:** RD-9 SC-A, PK-1, WG-6 and WG-7. If the chain slips, JT-1, JT-2 and JT-3 still land and
  are useful alone.
- **Binding may break pilots** whose terms and predicates have different names. JT-5's bar makes every move a recorded
  finding, not a silent change. Measured (P1 2.6): this risk is real for the UDHR, where no record binds, and small
  for the constitution, where 31 of 33 bind. Hence JT-5r, which changes audited units and can lose claimed bytes if a
  re-audit fails.
- **The integrity gain is preventive.** The hand check found no CHECKED unit in either pilot that uses a judgment
  (0.1). The translators already route every judgment to OPEN by hand. D3 and D15 protect new translations and
  authoring; they move no status on the current pilots.
- **The status and the usage map track syntactic use, directly or through definitions,** not rule chains (spec F3,
  settled by the statement review): a rule whose outcome feeds another rule's guard does not propagate, so the second
  unit can be CHECKED while its outcome still varies with the judgment (J-χ). The zone answer at a situation is the
  full answer, and JT-5a and JT-5b record each such unit.
- **Every reading set is rebuilt** at each profile switch (P1 F3), which touches every unit with a reading set, not
  only the units that change. The checker recomputes every id, and Lean replays every situation at load, so a wrong
  rebuild is refused rather than passed.
- **JT-E3 may fail.** Then the published judgment-term counts are "open-term" counts, as before.
- **Budgets.** Five judgments in one unit (u111) at many tuples can exceed WG-6's 16 open atoms: the answer is then
  UNKNOWN with that reason.

## 10. Shared pieces

Abstractions several topics could share. Each has a proposed owner and the interface this plan needs.

| # | Piece | Proposed owner | Users | Interface |
|---|---|---|---|---|
| S1 | One W2 record for every named open predicate, decoded as records (not names) | W2 / the discourse loader (`Loader.openTermNames`) | judgments, attitudes (generated records), quantities (grades), events (causal links), weighing (WG-0's rank terms) | `records` over `openTermNames` (3.1); one day a records-returning `openTermNames` with the names as projection |
| S2 | Binding an open term to its base predicate | this plan (`judgments@0`) | quantities' `Grade` ("a unary predicate that is a W2 open term"), events' `LinkNotOpen`, attitudes' generated atoms | `admit` (3.1) |
| S3 | Status computed from content for every open atom | this plan for W2 units; rights already does it (`nodeOpen`) | rights, soft, attitudes, events, quantities | the formula scan `opensIn` (3.2), which rights' `nodeOpen` calls from JT-1; `dependsOnC` and `status` (3.3) |
| S4 | Zone answers parameterised by their open names | weighing (WG-6) | judgments (JT-4), quantities (grade atoms), events (link atoms), attitudes (attitude atoms) | `zoneOfOpens L X M opens …` (request R1) |
| S5 | Records of findings with a decider | weighing (WG-6's records) with W2 `support` | judgments, weighing, risk (decision records), events | WG-6's `record`; "given <decider>'s judgment that …" |
| S6 | One decider vocabulary (`unresolved_decider` for no one named; `unstated` and `null` retired) | W2 | soft (`unstated`/`null`), rights, alternatives, attribution, attitudes, judgments | a token, one spelling (D7) |
| S7 | One legend row kind for open atoms ("Whether … is a judgment; … decides it") | english-lean (DRI AT4) | every plan with open atoms | 2.4's declaration and legend rows |
| S8 | Catalogue rows for evaluative words | english-lean | judgments, quantities ("serious", "clearly"), act-phrases ("arbitrarily", "freely"), defeasible ("good reason") | rows only (O15) |
| S9 | Propositional content atoms ("it is essential that P") | attitudes (AT-3a's content nodes) | judgments (JT-E2), attribution, events (hedged causal claims) | a guard node with the document as holder |
| S10 | Precedential constraint over findings | weighing (WG-E2) | judgments, weighing | WG-E2's protocol, unchanged |
| S11 | Graded open terms (a W2 record plus a dimension and a direction) | quantities (its §10 item 3) | judgments (J-ν), attitudes ("quite likely") | `VE.Scales.Grade` |

## 11. Cross-plan issues for the DRI

### 11.1 Requests R1 to R5 (text unchanged from draft 3)

The DRI decided these on 2026-10-14 (`manage-agents/debates/plan-synthesis/DRI-DECISIONS-PHASE2.md`, "Judgment terms
(wave 2)"):
- JT-R1 adopted, merged with defeasible's DF1;
- JT-R2 adopted (owner PK-1);
- JT-R3 adopted as a W2/english-lean catalogue item;
- JT-R4 adopted;
- JT-R5 noted.

The plan-synthesis directory has no `edits-judgment-terms.md`: SYNTHESIS predates this research-wave-2 plan and lists
no judgment-terms item (P1, status note). These decisions are therefore the cross-plan edits this plan keeps. Phase 1
conflicts with none of them; 11.2 says where it adds evidence.

- **R1 (to weighing, WG-6).** Please state `zoneOf` with an explicit `opens : List String`, so that WG-6's answers are
  the instance `opens = openNames L`, and state `zone_leftTo_sound`'s last conjunct as "every differing atom is in
  `opens` and not unsaid". Please also let `zone_leftTo_sound` certify the pair it returns (amended by the statement
  review, A2): its conclusion is `LeftToPair` (spec 6.1) instead of the existential `LeftToZ`, which follows from it.
  `LeftToPair` says that both returned assignments complete `M` (by `completionOf M record w`) to admissible
  completions with opposite outcomes, that the two agree on every unsaid atom, and that `differ` is exactly the atoms on
  which they differ, so that an empty `differ` is never certified. Then JT-4 edits no weighing file.
- **R2 (to RD-9 / PK-1).** A `LayeredU` with no packs for a plain norm-defaults document, so that zone answers and
  J-ι's criterion premises run on the UDHR's companions. Otherwise the UDHR's judgment answers wait.
- **R3 (to W2 / all plans).** One decider spelling (S6). This plan refuses `unstated` only under its own profile; other
  constructs are unchanged until their owners agree.
- **R4 (to quantities).** Under `judgments@0`, a grade must be bound (S2). `WellFormed E openTerms D` already requires
  a grade to be a W2 open term, so this adds only the sort check.
- **R5 (to NORTH-STAR).** Row 10 stays 0–198 B (UDHR); JT-0p claims 132 B of it (u010), and u060's 66 B wait on
  presupposition. R2's measurement does not support listing judgment terms as a
  large coverage blocker on the constitution. Their value is integrity and answers, which NORTH-STAR does not score.

### 11.2 Raised by phase 1 (draft 4)

Phase 1's results that touch another owner's part. None changes R1 to R5, the shared pieces (10), any owner, or the
build order. Each is a question or a request for the DRI.

- **X1 (act-phrases, pilot runner): who owns JT-5r?** The UDHR's binding needs 31 used terms split out of larger
  predicates in audited units (5, JT-5r). That is act-phrases' attachment work (AP-5b; D10), done as pilot prompt
  text. Proposed: the pilot runner writes it under act-phrases' rules, and act-phrases reviews the splits. No
  act-phrases file changes, and act-phrases' queue does not move. The DRI names the owner and the slot. Until then
  JT-5b waits and JT-5a goes ahead.
- **X2 (english-lean): may a rejected template take another predicate's wording?** In `ve/printer.py:201-204`, a
  template the lint rejects still registers its head word. So u010's rejected "{0} is of the greatest importance for
  {1}" made 13 accepted one-word "{0} is X" templates of part 1 render as 'classified as "…"' (P1 F1). The class at
  `ve/printer.py:186-187` says that it inspects "all declarations, including unusable templates", so this is a policy
  and not a bug (review finding 2). JT-0p avoids the case by giving u010's predicate no template. Question for
  english-lean, which owns the renderer: should only accepted templates claim a head word? It does not block JT-3.
  (The count of 13 comes from a run whose output was not saved; 0.2 has it re-run by a committed command.)
- **X3 (environment decoder): Python and Rust disagree on a constant's `verbalisation`.** The spec rejects the field
  (`docs/spec/v0-language.md:23`), and Rust refuses it. Python's loader accepts it, so the mismatch surfaced only as
  `CheckerUnavailable` on the readings conformance path (P1 F2). Request: the decoder's owner makes Python refuse it
  with the spec's text. JT-0p's prompt text already forbids the field.
- **X4 (pilot tooling; every plan that switches a profile on in a pilot): every reading set is rebuilt.** Every
  reading-set id is a digest over the environment id, so any change to the profile list or the vocabulary changes
  every set's ids (P1 F3; D1 shows the refusal). JT-5a and JT-5b do this. So will any other plan that switches a
  profile on in the pilots (attitudes, quantities' `scales@0`). Request: one committed rebuild command in the pilot
  tooling (`_reidentified` in `tools/readings_s1_pilot.py`), with its no-op self-test, for all plans to use (one
  owner).
- **X5 (the DRI's pilot prompts, SC2): the ledger's `claimed: false`.** The checker counts u060 OPEN. Its bytes stay
  unclaimed only if the pilots' claimed-bytes rule leaves out units marked `claimed: false` (P1 2.2). The same holds for
  any plan that writes a unit OPEN with a part of its meaning missing (presupposition's units first). Request: the
  rule goes into the merged prompt text once, for every plan.
- **X6 (R3, evidence only).** All 52 UDHR records say `unstated`, and none of the constitution's 33 does (P1 2.6).
  JT-R3 stands: `unstated` is refused only under `judgments@0`, and JT-5b's prompt rewrites the 52. No change is
  asked.
- **X7 (R5 and NORTH-STAR row 10, evidence only).** Row 10 stays 0–198 B. The 132 B remain an estimate until JT-0p's
  audit (0.2). No CHECKED unit in either pilot hides a judgment today (0.1), which supports R5's "their value is
  integrity and answers" as a preventive value. No change is asked.

## Change log

| Date | Draft | Change |
|---|---|---|
| 2026-10-13 | 1 | First draft: design B of the research note; decisions D1–D14; Lean statements for records, admission, status, dependence through definitions, the usage map, "conflict-free whatever is judged", and zone answers on WG-6; fixtures J-α to J-ξ and eleven pilot sentences; batches JT-0p to JT-5 with three pre-registered experiments; eleven shared pieces; five cross-plan requests. Planning only. |
| 2026-10-14 | 2 | The converged debate's joint position (REVISE to draft 2, then BUILD). Fix 1: arguments are sorts and may repeat under the profile (W2's own validator, one flag), admission reads `hide E (names defs)`, `Loader.lean` shared; fixtures J-ο, J-π. Fix 2: one candidate traversal per unit for status, set status and usage; J-ξ without unit content. Fix 3: J-ι's criterion as a labelled premise, `ConflictFreeX` "given …" apart from unconditional; `conflictFree_every_judgment` dropped. Fix 4: witnessed-pair zone wording with deciders, neutral unit line, sense-tied catalogue rows, JT-E1 as proxy readability. Fix 5: `opensIn` shared, rights switched in JT-1 with an equation theorem and the frozen-sources rehash. Edits A–D: `undeclared_evaluative` report (D15, JT-3) and "declared terms only"; `rv.definitions` named and J-γ′; fixtures J-ρ, J-σ, J-τ and D2's reason for `JudgmentRegulated`; JT-E1 bar (b) "no critical misreading in 40". u060's bytes unclaimed: JT-0p claims u010 only (+132 B); u010 keeps distinct legacy argument labels until JT-5; JT-5's "no declaration removed" bar and `good_judgment` role check. Section 3 now summarises the statements, which are written out and elaborated in [judgment-terms.md](judgment-terms.md). |
| 2026-10-14 | 3 | The statement review's joint position (FIX; spec section 0.1). A1: J-ξ an authored set with one reading, J-ξ′ an open set of u055's two scopes with a separating model (4.1, 4.2). A2: R1 also asks WG-6 for the certified pair `LeftToPair`; `zone_leftTo` concludes it; JT-4's wrong-witness and empty-`differ` mutations and seeded bugs. A3: "unconditional" and "whatever is judged" only for the plain route's `conflictFreeU_consistent`; the layered lines name `L.X` and say "without additional judgment criteria" (D6, 2.3, 2.4, 2.5, 3.4, 3.6, 4.1, JT-4); `conflictFree_unconditional_given` renamed `conflictFree_given_mono`. A4: "judgment dependence forces OPEN; otherwise the legacy status applies" (D3, 2.2, 3.3). A5: the `judgments` relay checks declaration and unit order (JT-2). F2: JT-5's bar is "keeps its status or moves to OPEN; none moves to CHECKED"; fixture J-υ. F3: dependence is syntactic use, directly or through W3 definitions; outcomes downstream can still vary (D3, 2.2, 3.6, 9); J-χ in 4.1; JT-5 records each such unit. F3′: `undeclared_evaluative` includes regulated predicates, and its relay accepts them (D15, 3.5, JT-3). F4: `JudgmentListedUnused` only on a complete unit, pending readings kept in the traversal (2.1, 2.2, 3.3, JT-2); fixture J-τ′. Seeded bugs for the new behaviours (JT-1 to JT-4). |
| 2026-10-14 | 4 | Phase 1's results (`docs/research/judgment-terms-phase1.md`; review ACCEPT, no fix round). New 0.1 (each result's verdict and what it gates) and 0.2 (DEFERRED items and their triggers). JT-0p: bar A PASS, bar B DEFERRED; prompt text completed (`thing`, placeholders replaced, reading-set rebuild, no constant `verbalisation`, no template for u010's predicate, `claimed: false`, `open_term_class_borderline`). JT-5 split into JT-5a (constitution, 13 units, 2,150 B measured), JT-5r (new: UDHR re-translation; 52 of 52 records unbound, 31 used terms to split out) and JT-5b (UDHR, 18 units, 1,945 B measured). JT-5's bar unchanged, and its meaning for unused records stated. D2: one bound term per sort, fixture J-ω; 4.2's `arbitrary` row corrected. D7's measured spellings. JT-3: templates the lint rejects. JT-E1 and JT-E3: status, and JT-E3's reporting. Bytes (8) and risks (9) updated. 11.1 keeps R1–R5 with the DRI's decisions; 11.2 adds X1–X7. No batch dropped; no bar moved. |
