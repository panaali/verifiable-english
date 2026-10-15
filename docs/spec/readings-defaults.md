# Pick a reading under unspecified defaults (`readings@1` × `norm-defaults@0`): statement spec (RD-0)

> Status: item-1 statement spec, draft 2 (2026-10-07). Draft 2 applies the converged Astra + Fable statement review
> of draft 1 (`manage-agents/debates/readings-defaults-spec/{astra,fable}.md`, CONVERGED in round 3: **FIX**, five
> items, build closed). Each lands where marked: **SR1** per-choice admission (`ndChoiceText`, 4.1 step 5, 5 row 5,
> F-ND10); **SR2** the product gate on ALL, SOME and NONE (`foldK_all`, `foldK_some`, 4.5, F-C17); **SR3**
> `restrictionsFor` computed locally, as Python computes it, with `hA` (1.8, 6.5, 8.2 rows 3.11 to 3.13); **SR4**
> decided units per compatible choice (`setDecided`, 1.10, 8.4); **SR5** conservativity as three separate
> guarantees (1.1, 4.6, F-ND7). The changed statements were elaborated as described in 12.9. The gate for draft 2: a
> targeted re-review of exactly what SR1 to SR5 changed (definitions, hypotheses and conclusions, diagnostics,
> fixtures, the measurement rule and the conservativity prose), for truth under their hypotheses as well as
> elaboration. Statements no SR item touches keep the acceptance draft 1's review gave them. RD-1 stays closed until
> that re-review gives PASS. Draft 1's status follows.
>
> Draft 1 (2026-10-07), branch `design/readings-defaults`, written from
> [readings-defaults-PLAN.md](readings-defaults-PLAN.md) draft 2, which applies the converged Astra + Fable review of
> the plan (`manage-agents/debates/design-readings-defaults/{astra,fable}.md`, CONVERGED in round 3: BUILD with
> mandatory RD-0 corrections E1 to E5 and A1 to A4). It is RD-0's deliverable: sections 3.1 to 3.8 of the plan as a
> statement spec, with the Lean of RD-1 to RD-6. **Every Lean statement here was elaborated** in the untracked scratch
> file `lean/SpecStubs_readings-defaults.lean` with `lake --dir <ve-nightly>/lean env lean <stub>`, against the
> build of `eaddd934`, whose `lean/` differs from this branch's base `6cbe1a26` only in
> `ResponseShape/Schemas/Check.lean`, `Service/Standalone.lean` and generated lists. In the stub each
> `theorem T b : C` below is `def T b : Prop := C`, with the same binders and conclusion. Fixture values marked
> *computed* are the stub's `#eval` output; values marked *derived* were worked out by reading the sources and are
> obligations of the batch named. Theorem statements and fixtures are implementation obligations, not claims of
> completed proofs. The scratch stub is not committed. No model was called.
>
> Inputs, read at `6cbe1a26`: [composition-s1.md](composition-s1.md), [composition-s2.md](composition-s2.md),
> [norm-defaults.md](norm-defaults.md), `lean/VE/Readings/{Doc,Choice,Separate,Route,Wire,SupWire}.lean`,
> `lean/VE/NormDefaults/{Tree,Premises,Semantics,Evidence,Wire,Report}.lean`, `lean/VE/SoftNorms/{Tree,Soften}.lean`,
> `lean/VE/Compose/{Content,Slot}.lean`, `ve/readings_verdicts.py` (the enumerated route's gate, lines 819 to 857),
> `ve/openterms.py`, and the UDHR pilot at `bd6c7ab2` (`git show`).
>
> The gate: RD-1 opens on the PASS of the Astra + Fable statement review of this file. PASS requires both reviewers to
> accept each statement as **true under its hypotheses**, F-ND5 included; that the stub elaborates is not enough.

## 0. Scope, one paragraph

`readings@1` refuses content beside `norm-defaults@0` today (S1's named abstention, kept by S2a 4.10), so a document
whose sentences have several readings and whose regulated predicates leave gaps to the reader gets no checked verdict
for those sentences. On the **norms chain** this file closes that gap. Every rule there is strict, so norm-defaults'
`fill` can be applied to the readings document itself (`fillDoc`), and taking a reading's, a choice's or the
superposed document commutes with it (the four equalities of 6.2). Admission adds norm-defaults' author checks per
reading; separation compares two readings on one base and one shared filling; each compatible choice is checked by
norm-defaults' own checkers; the fold across choices (ALL, SOME, NONE, CONFLICT-FREE, premise statuses), its gate on
conflict freedom, its conditions and the choice of English sentences move into Lean. Readings may carry their own
vocabulary and open terms; a set whose readings all do so becomes a **component**, checked by itself, and the
document's meaning is the product of its components. Out of scope: the soft and rights chains (D2: the abstention
stays, RD-9), superposition under the completion (RD-6, off the pilot path; its statements are given and re-reviewed
before their build), senses in `ve document` (RD-8), and any coverage number before RD-5 measures it.

In this spec: definitions (1), the English (2), wire and identity (3), the semantics in order (4), diagnostics (5),
the Lean statements (6), what is not claimed (7), the acceptance fixtures (8), limits (9), the measure (10), the
review checklist (11), and the differences from the plan's blocks (12).

## 1. Definitions

### 1.1 Where this applies

A document is **under the completion** when its environment's profiles contain `readings@1` and `norm-defaults@0`,
its chain is the norms chain (no `soft-norms@0`, no `rights@0`), and some reading set has a candidate with content.
For such a document the route of composition-s2 1.1 changes in one row: the abstention row becomes the enumerated
row, with the finding `ReadingsNotSuperposable: <every open set>` and the cause `the unspecified completion` (until
RD-6). Every other document keeps its route and its verdicts. What does reach it, the Lean fold (1.7) and the
`<reading>` slot (2.3), is listed with the other guarantees in 4.6 (SR5).

### 1.2 The document with its unspecified predicates

`NDoc` pairs a readings `Doc` (S1 1.1) with the frame's `unspecified` predicates, read from the environment before
DRI ruling 4's placeholder `deny` replaced them (`unspecOf`, 6.3). `asU N X` reads a document of the route as a
norm-defaults document (norm-defaults 7's `UDoc`): `freeU`, `oneU N s i`, `choiceU N c` and `supU N` are the free
document, reading `i` of set `s`'s document, choice `c`'s document and the superposed document, each with `N.unspec`.

`normsShaped D` is what the norms chain's decoder guarantees: the chain is `.norms`, the frame has no rule and no
rights block, and every content is an assertion or a strict rule with no party, no exception and no `hard` flag.

### 1.3 `fill` on the readings document

`fillDoc N` makes three changes, each a restatement of norm-defaults 2.3 on readings contents:

1. the frame declares `unsaid__p` with `p`'s sorts for every unspecified `p` (`fillFrameEnv`, norm-defaults' `E‴`);
2. every norm content whose rule is a root (empty `over`) on an unspecified predicate, in a fixed unit or a reading,
   gains `over := [unsaid--p']` (`fillSoftNode`, norm-defaults' `fillRoot`);
3. after every item, one strict fixed unit per unspecified predicate, in the frame's regulated order, holding `F_p`
   (`fillUnits`, norm-defaults' `fillNodes`); its unit id is its rule name.

`fillNamesFree N` holds exactly when no unit id and no declared name of the document begins `unsaid--`. Admission's
step 2 (4.1) enforces it, and RD-1's equalities need it (review A1): if a candidate declares the rule name
`unsaid--p`, a fixed root rule on `p` gains `over = [unsaid--p]` after filling and becomes attached to that
candidate's set, so the free document of `fillDoc N` loses it while `fill (freeU N)` keeps it (fixture F-ND5,
*computed*).

### 1.4 Admission's facts

`WellFormedND N` is S1's `WellFormedDoc N.D`, `normsShaped N.D`, `fillNamesFree N`, norm-defaults' `WellFormedU` of
the free document, and `WellFormedU` of every reading's document with content. `AdmittedND` carries it with
`WellFormedDoc (fillDoc N)`. (`WellFormedU` already contains norm-defaults' `unspecDeclared`, so the plan's
readings-level copy of it is dropped: 12.)

### 1.5 Separation under the completion

A situation's base is over the filled frame's author vocabulary, which includes the `unsaid__` predicates; their
tables are **the filling**, shared by both readings (D4). `AchievesU N s i B F q v` is S1's `Achieves` on `fillDoc N`
together with `Fill_T` of reading `i`'s own document holding on `B`. `fillHolds N s i M` evaluates that `Fill_T` on a
finite base. Shared fillings are the definition, not an approximation (review E5): if each reading chose its own
filling, a reading would be separated from itself at any gap. An unseparated pair is therefore equal meaning or a
search miss, and RD-5 lists such pairs.

### 1.6 Per-choice results

`ChoiceResult` is `proved`, `refuted`, `free`, `conflict`, `model`, `inconsistent` or `unknown`. `Holds N Γ φ c r`
says what result `r` claims of choice `c` (6.4): `proved` is CONFLICT-FREE and entailment on the filled document of
the choice; `refuted` a countermodel (`CounterU`); `free` and `conflict` the conflict status; `model` a model of the
choice's premises (`ConsistentU`); `inconsistent` CONFLICT-FREE together with `⊥` entailed (composition-s2 4.5's table:
INCONSISTENT only when CONFLICT-FREE; review A2); `unknown` nothing. `Covers N A rs` holds exactly when the rows of
`rs` are the compatible choices taking `A`.

### 1.7 The folds

- `foldConflict rs`: CONFLICT when some row is `conflict`; CONFLICT-FREE when there are rows and every row is
  `free`; UNKNOWN otherwise.
- `foldEntailment cs rs` (review A2): `cs` are the conflict rows and `rs` the query rows of the same choices. No
  entailment verdict unless `foldConflict cs` is CONFLICT-FREE (composition-s2 4.6 as built, 14.8). Past that gate:
  ALL when every query row is `proved`, NONE when every one is `refuted`, SOME with at least one of each (rows without
  a result tolerated), UNKNOWN otherwise.
- `reasonOf cs rs` names what an UNKNOWN rests on: `conflictStatus s c`, the conflict status `s` and the first choice
  with it, or `noResult c`, the first choice whose query row is neither `proved` nor `refuted`. Its text is
  `UNKNOWN (conflict status: CONFLICT)` or `UNKNOWN (conflict status: UNKNOWN)` with the choice in S2a 7's form
  (`choiceText`, for example `rs_1@1:2`), as `ve/readings_verdicts.py:837` words it today.
- `foldPremises ps`: `model` when some row is `model`; INCONSISTENT when there are rows and every row is
  `inconsistent`; UNKNOWN otherwise.

### 1.8 Conditions

`restrictionsFor D A` lists the labels `coupling:<id>` and `narrowing:<id>` of the couplings and narrowings that
exclude some complete choice taking `A`, couplings first, each in document order (`choiceCore D`'s order). It is
computed locally, as Python's `restrictions` computes it (`ve/readings_verdicts.py:117-139`), and never enumerates
the complete choices (SR3): a coupling is listed when two consecutive sets of it have candidates that `A` allows and
whose labels on its axis differ; a narrowing in force is listed when `A` does not fix its set and it drops one of the
set's candidates. `restrictionsFor_spec` (6.5) says that this is the meaning above whenever some compatible choice
takes `A`, which the wire establishes first (4.4).
`usedLabels check pre L post` drops slot and `Fill_T` labels greedily, in label order, while every certificate the
answer rests on still checks with the dropped labels' formulas read as `⊤`: the rule composition-s2 2.3 "as built"
gave Python, now Lean's.

### 1.9 Readings with their own vocabulary, and components

A candidate may carry `"companion": {"environment": E, "open_terms": T}` (D6; `open_terms` beside `environment`,
review E4). A set is a **companion set** exactly when every one of its readings carries a companion; a set that mixes
the two is refused. A companion set cannot use `main` as its id, because `main` names the document component;
a set without companions may still use that id. The **split** of a document (RD-4a) gives:

- for each companion set, a component case: the environment is its companions' environments merged (the same
  `language`, `spec_revision` and `profiles`; `sorts`, `constants` and `predicates` united by name, a repeated name
  only with byte-identical canonical declarations; `readings@1` added; decoded by the frozen decoders, so every frozen
  limit applies); the document is the set's unit, the set, the narrowings on the set (they travel with it, review A3),
  and the set's open terms: the companions' `open_terms` united by name, a repeated name only with byte-identical
  entries, each validated against the merged frame (E4);
- the main case: the document without the companion sets, with only its own open terms. The companion sets' units
  stay in it, without a set and without content. A set left on W2 (content null, no companions; a set not migrated or
  not separated) stays in it, visible with W2's UNKNOWN, and is never a component.

Nothing is lost or duplicated: every reading set, coupling and narrowing lands in exactly one case
(`split_keeps_links`). A coupling that names a companion set together with another set would link two components and
is refused (E3, A3).

`Components` is the main `NDoc` and one `NDoc` per companion set. The document's meaning is the product of its
components: a reading of the document is one compatible choice per component (`CompatibleK`); it is CONFLICT-FREE
when every component's chosen document is (`ConflictFreeK`); a situation is one situation per component
(`ConsistentK`). No symbol is shared, because each component is decoded against its own frame only.

### 1.10 Lean-decided units (plan 3.9)

A unit is **Lean-decided** exactly when every verdict VE reports about its formal content is a Lean answer that is not
UNKNOWN: for a fixed unit with content, its component's conflict status is CONFLICT-FREE or CONFLICT and its premise
status `model` or INCONSISTENT (`fixedDecided`); for the unit of an open set, its component's conflict result under
every compatible choice is CONFLICT-FREE or CONFLICT, a choice without checked evidence counting as UNKNOWN, and every
reading's premise status is `model`, INCONSISTENT, `dead` or `narrowed` (`setDecided`; SR4). The conflict results are
read per choice, not as one folded status, so a CONFLICT under one choice cannot hide an UNKNOWN under another
(8.4). A `dead` reading (S2a's checked `DeadReading`) or a `narrowed` one (dropped by a narrowing in force, E7) is in
no compatible choice, so its own status, established by those existing checks, decides it. Labelled and
unformalised units never are.

## 2. The English (one reading each)

Every sentence here goes through W7's all-derivations gate before it is shown, and none can be written by an author.
None is an IDE question, so none goes through W8.

### 2.1 New sentences

| # | Wording | The one reading | Paraphrase a reader may use | Formal content |
|---|---|---|---|---|
| E30 | `Under every reading of sentence <n>, <result sentence>` | For every compatible way of reading sentence `n`, and every situation that its rules allow, with the text's silences answered in any way the rules allow, the result holds. Nothing else in the document varies, since sentence `n` was checked by itself | "However sentence `n` is read, …" | `foldEntailment` or `foldConflict` on the component of sentence `n` (one open set) |
| E31 | `Sentence <n> was checked by itself, with the terms its readings declare; VE did not check it together with the other sentences.` | Sentence `n` is a component: its terms are its readings' declarations merged, and no verdict combines it with another sentence | "Sentence `n`'s check did not look at the other sentences." | the split (1.9) |
| E32 | `Each open sentence below was checked by itself, under each of its readings.` | The lines after it are per-component answers; together they claim the product of 1.9 and nothing more | "The answers below are sentence by sentence." | the product fold (6.6) |
| R7 | `the text does not say whether <clause>: no rule decides this situation.` | Under the readings named (E12's frame), the point is UNDECIDED: two admissible fillings, both checked, give it different values | "The text leaves this open here." | `norm-defaults-status` on the choice's document; norm-defaults 4.2's sentence after E12's colon |
| R8 | `VE could not check whether two rules on the same act contradict each other.` | Under the readings named (E12's frame), the conflict status is not certified: no checked evidence settles it either way | "VE does not know whether the rules clash under this reading." | 2.4 item 3: the gate's `UNKNOWN (conflict status: UNKNOWN)`, the choice `reasonOf` names (added in RD-4b's review fix round; W7 wording, DRI sign-off pending) |
| R9 | `VE could not check whether the conclusion follows.` | Under the readings named (E12's frame), the query has no checked result | "VE does not know whether the conclusion holds under this reading." | 2.4 item 3: an UNKNOWN from a missing result, the choice `reasonOf` names (added with R8) |

### 2.2 Reused sentences (their existing gates apply)

- After a shown `<situation>`, one sentence per filled gap the result depends on (the model's `unsaid__` atoms in the
  cone of the conclusion or target, 10a's `coneOf`), exactly one per such gap and none for a gap outside the cone:
  `Here the text does not say whether <clause>; this situation answers 'yes'.` (or `'no'`), norm-defaults 3.2.
- As the E3 line for a used `unsaid:pair:<r>,<m>` label, norm-defaults 4.1's pair sentence:
  `Whenever a <noun> must <act>, it may <act>.`
- For a latent conflict under a reading, R4 followed by norm-defaults 4.2's latent-conflict sentence.

### 2.3 The `<reading>` slot (review A4)

Composition-s2 2.1's `<reading>` row changes: when a set's candidates differ beyond the deontic verb, `<reading>` is
the candidate's own rendered sentence, in italics, without its final period; when they differ only in the verb, it is
the italic verb, as today. "Reading 2" is never shown. The change is to the slot rule, so every sentence carrying the
slot shows it: E6, E7 and E9 (conditions), E12 with its R4 witness line, E17, and the "Under <reading>" sentences.
Lean's plan names each reading by set and index (`Line.readings`); Python renders the candidate's sentence with the
renderer `reading_names` already uses to compare frames. This is a W7 wording change, DRI-signed in RD-3's DELTA.

### 2.4 Which sentences an answer gets

Composition-s2 2.3, items 1 to 7, unchanged, on the enumerated route, with these additions:

1. A component's lines are preceded by E31, and the document's by E32 when it has a companion component. E30 replaces
   E26 for a companion component.
2. A shown model is followed by its filled-gap sentences (2.2).
3. An UNKNOWN from the gate is worded as composition-s2 4.6 words `UNKNOWN (conflict status: <status>)`, naming the
   choice by E12; an UNKNOWN from a missing result names that choice the same way. For the document's ALL, SOME or
   NONE (4.5), the choice named is the other sentence's (SR2). As built (RD-4b review, B3; `gateItems`): under a
   CONFLICT, E12 with R4 shows the choice's checked witness, as a CONFLICT is worded; under an uncertified status,
   E12 with R8; for a missing result, E12 with R9. The document's lines are E32, then E31 when the other sentence is a
   companion, then that line; a case without an open sentence has no reading to name and gets none.
4. The product answer lists, under each component, that component's `restrictions` and `conditional_on` (A3); an E3
   line never cites a label of another component.

RD-6b's filled superposed query route preserves the gated UNKNOWN verdict, status, and choice, but currently emits no
English plan for that result. Item 3's E12 wording applies to the enumerated route. Extending the Lean superposed
planner with E12 for gated UNKNOWN remains follow-up work.

`englishPlan D route question answer` is Lean's list of `Line`s, computed from the case's decoded document `D` and the
checked answer (review E5: `D` is the case's, not any document).

### 2.5 Non-wordings

Any `unsaid__` or `unsaid--` name, `F_p`, a qualified `rd-` name, a component, a bit, `ve__here`, "reading <i>". E10,
E26 or E30 for a model-based result. A model line naming fewer sets than its component has
(`plan_model_names_every_set`). The quote marks of the reused filled-gap sentence are existing wording; whether they
meet the zero-training rule is for norm-defaults' reader test (its 4.3); no new sentence here carries any.

### 2.6 Examples (on F-ND1, *derived*; RD-3's renderer fixes the exact sentences)

- Conflict: "Under every reading of the open sentence, no two rules on the same act contradict each other." then E3:
  "This holds provided that: Whenever an agent must help a user, it may help that user."
- Query `∀ agent ∀ user. help_required`: "Read sentence 1 as *every agent must help each user*: the conclusion
  follows: …" and "Read sentence 1 as *every agent must help each user who asks that agent*: the conclusion does not
  follow. It fails here: a is an agent; u is a user. Here the text does not say whether a must help u; this situation
  answers 'no'."

## 3. Wire form and identity

- **Document.** A candidate may carry `companion: {environment, open_terms}` (1.9). W2's structural validation passes
  it through unread; Lean reads it. A companion candidate's `meaning_id` is computed by Lean
  (`companionMeaningId`: `VE.Route.Wire.meaningId` over the companion's `environment_id` and the content's canonical
  AST) and must equal the recorded one (W2's text, `reading meaning id does not match content`).
- **`readings-validate`, `readings-separate`** under the completion answer S1's rows computed on `fillDoc N`, adding
  per reading `fill_premises` (label `unsaid:pair:<r>,<m>`, AST) and once `filled` (`environment`: the lower
  environment with each `unspecified` read as `deny`, `norm-defaults@0` removed and every `unsaid__p` added, as 10a's
  `withUnsaid`; `units`: the filled contents and the `F_p` units; `chain`: `norms`, the chain the completion took,
  which the client reads and never derives, rd-9 review F25). Python's search and English read `filled`.
- **`readings-elaborate`**: the enumerated row with `finding` `{"text": "ReadingsNotSuperposable: <every open set>",
  "cause": "the unspecified completion"}`; `enumeratedCheckText` runs on `fillDoc N` and, for each of the at most 64
  compatible choices, also runs `ndChoiceText` (4.1 step 5; SR1).
- **`readings-choice`** gains, under the completion, the inner kinds of the plan's 3.4 table, answered on
  `choiceU N c` with norm-defaults' answer shapes; certificates are bound to `E‴_base` of the choice and to its
  document hash (`choiceHash`).
- **`readings-verdicts`** (new, RD-3): request `question` (`conflict`, `premises`, or a query with `conclusion`,
  `premises` and optional `assumed`), `evidence` as a list of `{choice, conflict, model, unsat, certificate,
  countermodel}`, and, with components, `sentence` (a unit). Missing evidence is `unknown`. Answer: `route`,
  `verdict`, `status` (with the gate's text), `per_choice` (choice, conflict row, query row, evidence form),
  `conditional_on`, `restrictions`, `assumed`, `english` (the plan's lines), and with components `components` (per
  component: the unit, route, rows, English), the product verdicts and `decided_units`.
- **Components.** Every kind under `readings@1` first splits the case. A kind that names one component
  (`readings-choice`, `readings-separate`) takes `component` (a set id, or `main`); `readings-validate` and
  `readings-elaborate` answer per component.

Identity: no identity changes. `fillDoc N`, the filled documents, the split and every compatible choice are
regenerated from the decoded document at every trusted site and bound to the chain's document hash; none is on the
wire as authority. Certificates and models are evidence checked against the regenerated premises.

## 4. Semantics, in order

### 4.1 Admission (plan 3.2), stopping at the first error

0. With companions: the split (1.9), in the order of 5's rows 6 to 13; then steps 1 to 5 on the main case and on
   each component case in source order.
1. S1's admission on `N.D` as today (the author's document with placeholder `deny`, S1's texts). On the norms chain
   the abstention no longer applies under `norm-defaults@0`.
2. Reserved names: a unit id, rule name or declared name beginning `unsaid--` is
   `InvalidInput: reserved name <n>`. This is what makes `fillNamesFree` hold of every admitted document.
3. For the free document, then every reading with content in set and index order: norm-defaults' author checks on
   that document's UDoc (`checkAuthorN`'s texts and order), then `WellFormedU`
   (`InvalidInput: norm-defaults document is not well formed`). A reading's text carries ` under <set>@<v>:<i>`.
4. S1's checks on `fillDoc N` (`admissionText`), with the reading's suffix. By the equalities and `fill_wellFormed`
   they can fail only on the limits for generated formulas that apply to the filled tree (*derived*; F-ND9).
5. Each choice (SR1). When the compatible choices number at most 64 (`maxChoices`), for each of them in canonical
   order (`choices`, the same on `N.D` and on `fillDoc N` by `compatible_fillDoc`): first S2a's step 5 on the filled
   document, `choiceChainText (fillDoc N) c`; then `ndChoiceText re N c`, which is norm-defaults' author checks on
   `choiceU N c` (`checkAuthorN`'s texts and order) and then `WellFormedU`
   (`InvalidInput: norm-defaults document is not well formed`), its text suffixed ` under <choice>` in
   `choiceText`'s form (for example ` under rs_1@1:0, rs_2@1:0`). The first text found is the answer. Beyond 64 no
   choice is checked here, as today (W2's budget, E28). Step 3 does not cover a choice: a choice's document holds
   the chosen readings of several sets, and `limitsU` bounds one document, so each reading's document can be within
   the limits while their choice is not (F-ND10). `replayChoiceU` runs `ndChoiceText` on its own choice as well
   (6.3), so every replayed choice, one beyond the budget included, has `WellFormedU` checked.

### 4.2 Separation (plan 3.3)

S1's `separates` runs unchanged on `fillDoc N`; the witness's step 2 also requires `fillHolds` of the witness on the
base, else S1's text `distinguishing model violates a generated premise`. `separates_soundU` gives `AchievesU` for
the witness and its negation for the other reading; `achievesU_iff` says what that means in norm-defaults' terms.

### 4.3 Each choice (plan 3.4)

For each compatible choice, at most 64 per component, the evidence is checked by norm-defaults' own functions on the
regenerated `choiceU N c`, with no JSON round trip through the lower route (`readings_wire_nd_choice_conflict`,
`readings_wire_nd_choice_entails`, `modelCheckU_sound`, and 10a's witness, status and report cores). A certificate
counts as `proved` only with the choice's conflict packages (S2a 14.8). `replayChoiceU` first runs `ndChoiceText` on
the choice and refuses with its text, which is how `ChoiceReplayU.wfc` is established (SR1).

### 4.4 Verdicts (plan 3.5)

Lean enumerates the compatible choices taking `assumed` (at most 64; beyond that W2's budget shape and E28), checks
each piece of evidence as in 4.3, and folds with 1.7: the conflict question with `foldConflict`, a query with
`foldEntailment` over the conflict rows and the query rows, the premises with `foldPremises` per document and per
reading. Readings no compatible choice takes are `ReadingsUnsatisfiable` (S2a's `untakenText`, 5 row 15). That check
comes first, after the budget check and before any condition, as `ve/readings_verdicts.py:825-845` orders them, so
`restrictionsFor` is called only when some compatible choice takes `assumed` (its hypothesis `hA`, 6.5; SR3).
Conditions by 1.8, computed locally, with no cap on the complete choices: thirty binary sets narrowed to one
compatible choice give their thirty labels without the 2^30 complete choices (8.2 row 3.13).
Beyond 64: `UNKNOWN (not ALL: countermodel under <choice>)` when a countermodel was checked, else the budget answer.

### 4.5 Components (plan 3.6)

The product fold (6.6):

- **conflict:** CONFLICT-FREE when every component is; CONFLICT when some component has a checked witness (every
  component having a compatible choice, which admission ensures);
- **premises:** `model` when every component has a model;
- **a query** is typed against exactly one component's frame; `--sentence <unit>` picks it when the terms fit
  several. `--under` names sets of that component only. ALL there is ALL for the document when every other
  component is CONFLICT-FREE under every compatible choice; their models are not needed (SR2). NONE for the document
  needs every other component CONFLICT-FREE with a model under every compatible choice; SOME needs every other
  component CONFLICT-FREE with a model under some choice. Otherwise UNKNOWN. When another component is not
  CONFLICT-FREE the answer is `UNKNOWN (conflict status: CONFLICT)` if some other component's conflict fold is
  CONFLICT, else `UNKNOWN (conflict status: UNKNOWN)`, naming the first choice with that status in the first other
  component (in `Components.all`'s order) that has it, as `reasonOf` names a choice; otherwise, for NONE and SOME,
  the reason is "another sentence's readings are not all consistent". The queried component's own verdict stays in
  its `components` entry. (The CONFLICT-FREE condition is A2's gate applied to a reading of the whole document, and
  `foldK_all`, `foldK_none` and `foldK_some` each conclude `ConflictFreeK` of every compatible product choice: 12.)

### 4.6 Conservativity (SR5)

Three guarantees, one per kind of change, then what none of them changes:

- **Completion support** (RD-1, RD-2a: `fillDoc`, and admission, separation and choices under the completion). Only
  a document under the completion (1.1) reaches it. Such a document that reached the abstention on the norms chain
  now gets the enumerated route: an `availability` change, F-ND1's case. A document outside 1.1 keeps its route.
  With `readings@1` off nothing here is reachable; with `norm-defaults@0` off, or on the soft or rights chain, no
  step of 4.1 to 4.3 that is specific to the completion runs, and K18 keeps its abstention with today's text. A
  document whose sets have no content keeps W2's route (S1 4.9). Without unspecified predicates `fillDoc N = N.D`
  (`fillDoc_conservative`; F-ND0, *computed*).
- **Companion splitting** (RD-4a, RD-4b). Only a document with `companion` reaches it. RD-4a and RD-4b change no
  answer, identity or text of a document without `companion`: that is their A/B claim, and only theirs.
- **Fold and wording migration** (RD-3). The Lean fold of 1.7 replaces Python's for every `readings@1` document on
  the enumerated route, with or without `norm-defaults@0`, and the `<reading>` slot rule of 2.3 reaches every
  `readings@1` answer that shows the slot. Verdicts are byte-identical. The English is byte-identical except the
  2.3 slot, the one signed English exception (RD-3's DELTA, class `wording`); among the S1 and S2a fixtures it
  changes S2a's M8, M9 and M12 only (8.2, F-ND7).
- None of the three changes a frozen file, a canonical byte, an identity or an approved theorem statement. New
  statements go in new files; `abstention`, `routeOf` and `readings-choice`'s inner kinds change as definitions only.

## 5. Diagnostics, in order

| # | Text | When | Step |
|---|---|---|---|
| 1 | S1's and S2a's admission texts | as today | 4.1 step 1 |
| 2 | `InvalidInput: reserved name <n>` | a unit id, rule name or declared name begins `unsaid--` | 4.1 step 2 (no suffix) |
| 3 | `checkAuthorN`'s texts in its order: `InvalidInput: reserved name <n>` (a predicate `unsaid__…`), `ResourceLimit: vocabulary size`, `ResourceLimit: rules`, `ResourceLimit: unspecified name length`, `ResourceLimit: AST exceeds 10,000 nodes`, `ResourceLimit: precedence depth`; then `InvalidInput: norm-defaults document is not well formed` | the free document, then each reading's, a reading's text suffixed ` under <set>@<v>:<i>` | 4.1 step 3 |
| 4 | S1's chain texts on the filled tree, suffixed | e.g. `ResourceLimit: generated norm layer layer:norms:<p> under rs_1@1:0` | 4.1 step 4 |
| 5 | per choice, S2a's chain text (`choiceChainText (fillDoc N) c`), then `checkAuthorN`'s texts in row 3's order and `InvalidInput: norm-defaults document is not well formed` (`ndChoiceText`), each suffixed ` under <choice>` in `choiceText`'s form (SR1) | a compatible choice's document, at most 64 choices, in canonical order; e.g. `ResourceLimit: rules under rs_1@1:0, rs_2@1:0` (F-ND10); `replayChoiceU` gives the same text for its own choice | 4.1 step 5 |
| 6 | `InvalidInput: reading set <set> mixes readings with and without their own vocabulary` | a set mixes the two | split |
| 6a | `InvalidInput: reading set main conflicts with the reserved component name` | a companion set has id `main` | split |
| 7 | `InvalidInput: coupling <id> links <set> and <set'>, which do not share one vocabulary` | a coupling names a companion set with another set (E3, A3) | split |
| 8 | `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` | a companion's profiles contain `soft-norms@0` or `rights@0` | split, per set in source order |
| 9 | `InvalidInput: the readings of <set> declare different <language \| spec_revision \| profiles>` | companions of one set differ in those | split |
| 10 | `InvalidInput: readings <set>@<v>:<i> and <set>@<v>:<j> declare <name> differently` | a sort, constant or predicate repeated with different canonical bytes | split |
| 11 | `InvalidInput: readings <set>@<v>:<i> and <set>@<v>:<j> declare open term <name> differently` | an open term repeated with different bytes (E4) | split |
| 12 | the frozen decoders' texts on the merged frame (e.g. `DuplicateActRole`) | the merged frame is refused | split |
| 13 | `reading meaning id does not match content` | a recorded `meaning_id` differs from `companionMeaningId` | split |
| 14 | `UnknownRule: rule <name>` | a main fixed unit names a companion reading's rule | admission of the main case |
| 15 | `ReadingsUnsatisfiable: no compatible reading takes <choice>` | `assumed` names readings no compatible choice takes; checked before `restrictionsFor` runs (SR3) | 4.4 |
| 16 | `InvalidInput: the conclusion uses terms of no sentence checked by itself` | the conclusion types in no component | 4.5 |
| 17 | `InvalidInput: the conclusion's terms fit sentences <n>, <m>; name one with --sentence` | it types in several and no `--sentence` | 4.5 |
| 18 | `InvalidInput: --under names <set>, which is not a reading set of the sentence the conclusion is about` | `--under` outside the query's component (A3) | 4.5 |

Statuses, not errors: `UNKNOWN (conflict status: CONFLICT)`, `UNKNOWN (conflict status: UNKNOWN)`,
`UNKNOWN (not ALL: countermodel under <choice>)`, W2's budget answer; the finding
`ReadingsNotSuperposable: <sets>` with cause `the unspecified completion`.

## 6. Lean: definitions and the exact statements to prove

### 6.1 Files and placement

| Batch | File | Declarations |
|---|---|---|
| RD-1 | `lean/VE/Readings/Unspecified.lean` (new), `UnspecifiedExamples.lean` (new, `#guard`s) | 6.2 |
| RD-2a | `lean/VE/NormDefaults/Wire.lean` (`EntailsU`, `acceptanceU`), `NormDefaults/Report.lean` (`modelCheckU`, `modelCheckU_sound`), beside the 10a theorems whose cores they become; `lean/VE/Readings/UnspecifiedWire.lean` (new) | 6.3 |
| RD-3 | `lean/VE/Readings/Verdicts.lean` (new); the kind `readings-verdicts` in `Readings/Run.lean` | 6.4, 6.5 |
| RD-4a | `lean/VE/Readings/Companions.lean` (new) | 6.6 (wire part) |
| RD-4b | `lean/VE/Readings/Components.lean` (new) | 6.6 |
| RD-6a, RD-6b | `lean/VE/Readings/SupExtra.lean` (new), off the pilot path | 6.7 |

Each block below was elaborated as written inside one namespace with these `open`s; the builder places each
declaration in its file, where `EntailsU`, `acceptanceU`, `modelCheckU` and `modelCheckU_sound` are
`VE.NormDefaults` names. A wire function shown without a body (`ndText`, `ndChoiceText`, `admitND`, the replays, the
RD-4a decoders, `englishPlan`) is specified by its docstring and by sections 3 to 5; the stub gave it a placeholder
body, so only its type was checked.

```lean
open VE.Readings
open VE.Norms (Regulated Sat envAt size restrictAll DocumentExpansion)
open VE.SoftNorms (SoftNode SoftDoc soften)
open VE.Rights (RightsDoc correlate)
open VE.Compose (Content)
universe u
```

### 6.2 RD-1: `fillDoc` and separation under the completion

```lean
/-- A readings document and its frame's `unspecified` predicates (norm-defaults 2.1). -/
structure NDoc where
  D : Doc
  unspec : List String

/-- A document of the route as a norm-defaults document (norm-defaults 7's `UDoc`). -/
def asU (N : NDoc) (X : RightsDoc) : VE.NormDefaults.UDoc := ⟨soften (correlate X), N.unspec⟩
def freeU (N : NDoc) : VE.NormDefaults.UDoc := asU N (free N.D).1
def oneU (N : NDoc) (s : String) (i : Nat) : VE.NormDefaults.UDoc := asU N (one N.D s i).1
def choiceU (N : NDoc) (c : Choice) : VE.NormDefaults.UDoc := asU N (choiceDoc N.D c).1
def supU (N : NDoc) : VE.NormDefaults.UDoc := asU N (sup N.D).1

/-- What the norms chain's decoder guarantees (1.2). -/
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

/-- `fillRoot` on a readings content (1.3, change 2). -/
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
/-- `F_p` for every unspecified predicate, in the frame's regulated order, each a fixed unit named by its rule
    (1.3, change 3). -/
def fillUnits (N : NDoc) : List Item :=
  (N.D.frame.soft.T.regulated.filter (fun r => r.name ∈ N.unspec)).map (fun r =>
    .fixed (VE.NormDefaults.fillName r.name) (.norm (strictNodeOf (VE.NormDefaults.fillNode r))) [])
/-- `E‴` on the frame (1.3, change 1). -/
def fillFrameEnv (N : NDoc) : VE.Environment :=
  { N.D.frame.soft.E with predicates := fun n =>
      match N.unspec.find? (fun p => VE.NormDefaults.unsaidName p == n) with
      | some p => some (VE.SoftNorms.sortsOf N.D.frame.soft p)
      | none => N.D.frame.soft.E.predicates n }
def fillDoc (N : NDoc) : Doc :=
  { N.D with frame := { N.D.frame with soft := { N.D.frame.soft with E := fillFrameEnv N } },
             items := N.D.items.map (fillItem N) ++ fillUnits N }
/-- No unit id and no declared name begins `unsaid--` (4.1 step 2). -/
def fillNamesFree (N : NDoc) : Bool :=
  N.D.items.all (fun it => !(itemUnit it).startsWith "unsaid--" && it.names.all (fun n => !n.startsWith "unsaid--")) &&
    N.D.sets.all (fun R => (declaredBy R).all (fun n => !n.2.startsWith "unsaid--"))

/-- Taking a reading's, the free, a choice's or the superposed document commutes with `fill` (review A1: each
    needs `fillNamesFree`; F-ND5). -/
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
/-- DRI 2026-10-07: `hs` added (F-ND11: without it the lists can differ in order); `singlyAttached` is part of
    `WellFormedDoc`, so every admitted document has it. The membership-only form `mem_attached_fillDoc` is kept. -/
theorem attached_fillDoc (N : NDoc) (hf : fillNamesFree N = true) (hs : singlyAttached N.D = true) (u : String)
    (hu : u ∈ fixedNames N.D) : attached (fillDoc N) u = attached N.D u
theorem fillDoc_conservative (N : NDoc) (h0 : N.unspec = []) : fillDoc N = N.D

def WellFormedND (N : NDoc) : Bool :=
  WellFormedDoc N.D && normsShaped N.D && fillNamesFree N && VE.NormDefaults.WellFormedU (freeU N) &&
  N.D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || VE.NormDefaults.WellFormedU (oneU N R.id i)))

/-- S1's `Achieves` on the filled document, the filling respecting `Fill_T` of the reading's own document. -/
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
    (hf : fillHolds N s i σ.base = true) :
  SeparatedU.{u} N s i j
/-- On the norms chain no key is generated: `AchievesU` is an admissible filled situation of the reading's filled
    document where the probe has the value. -/
theorem achievesU_iff (N : NDoc) (hn : normsShaped N.D = true) (hf : fillNamesFree N = true) (s : String)
    (i : Nat) (B : VE.Structure.{u}) (F : Tables B.Carrier) (q : Probe B.Carrier) (v : Bool) :
  AchievesU N s i B F q v ↔
    B.Admissible (authorEnv (fillDoc N)) ∧ VE.NormDefaults.BaseAdmissibleU (oneU N s i) B ∧
      Observes (one (fillDoc N) s i).1 (one (fillDoc N) s i).2 B q v
```

Proof notes. The four equalities follow from one lemma about `build` (building with a `keep` and a `pick` that
agree on `N.D` and `fillDoc N` gives the filled document) and one about `sup`'s fold. `fillNamesFree` is what keeps
`attached` unchanged (`attached_fillDoc`), hence `keep`, and what keeps `copies` from expanding an added `unsaid--`
entry in `sup`. `soften_hard_identity` (its `WellFormedSoft` hypothesis is unused; the lemma needed is
`envPrime_of_no_decisions`) carries them across `soften`, `correlate_noRights` across `correlate`. Environments are
equal by `funext` on `predicates`: `choiceEnv` overrides `ve__` names and `fillEnv` `unsaid__` names, which are
disjoint. `separates_soundU` is `separates_sound` on `fillDoc N` with `hf`; `achievesU_iff` uses `fillDoc_one` and the
empty `genKeys` of a strict document.

### 6.3 RD-2a: admission, separation and choices under the completion

```lean
/-- Entailment on a filled document: the conclusion of `normDefaults_wire_acceptance`, named. -/
def EntailsU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) →
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S → Sat S Γ → φ.denote S []
/-- `normDefaults_wire_acceptance`'s core on any well-formed UDoc (its proof moves here; its statement is kept). -/
theorem acceptanceU (U : VE.NormDefaults.UDoc) (h : VE.NormDefaults.WellFormedU U = true) (Γ : List VE.Formula)
    (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill U) (size (VE.NormDefaults.fill U)))
      (VE.NormDefaults.Wire.premisesU U Γ) φ cert = true) :
  EntailsU.{u} U Γ φ
/-- A finite base model with a separate filling: the base background, `Fill_T`, and each premise read through the
    outcome substitution of `fill U`; the second component is the conclusion's value. -/
def modelCheckU {α : Type u} [DecidableEq α] (U : VE.NormDefaults.UDoc) (M : VE.FiniteModel α)
    (F : VE.NormDefaults.FiniteFill U α) (Γ : List VE.Formula) (φ : VE.Formula) : Bool × Bool :=
  (VE.Norms.backgroundValid U.D M && VE.NormDefaults.fillValid U M F &&
     Γ.all (fun a => (VE.Norms.subst (VE.NormDefaults.fill U).T (size (VE.NormDefaults.fill U)) a).eval (M.withFill F) []),
   (VE.Norms.subst (VE.NormDefaults.fill U).T (size (VE.NormDefaults.fill U)) φ).eval (M.withFill F) [])
theorem modelCheckU_sound {α : Type u} [DecidableEq α] (U : VE.NormDefaults.UDoc)
    (h : VE.NormDefaults.WellFormedU U = true) (M : VE.FiniteModel α) (valid : M.Valid (envAt U.D 0))
    (F : VE.NormDefaults.FiniteFill U α) (Γ : List VE.Formula) (φ : VE.Formula)
    (hm : (modelCheckU U M F Γ φ).1 = true) :
  VE.NormDefaults.BaseAdmissibleU U (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) ∧
  (∀ a ∈ Γ, (VE.Norms.subst (VE.NormDefaults.fill U).T (size (VE.NormDefaults.fill U)) a).denote
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) []) ∧
  ((VE.Norms.subst (VE.NormDefaults.fill U).T (size (VE.NormDefaults.fill U)) φ).denote
      (VE.NormDefaults.withFill U M.asStructure (VE.NormDefaults.finFill M F)) [] ↔
    (modelCheckU U M F Γ φ).2 = true)

/-- The frame's unspecified predicates, from the environment the frame was decoded from. -/
def unspecOf (re : VE.Readings.Wire.ReadingsEnvironment) (D : Doc) : List String :=
  (D.frame.soft.T.regulated.map (·.name)).filter ((VE.NormDefaults.Wire.unspecifiedNames re.lowerJson).contains ·)
/-- 4.1 steps 2 and 3: reserved names, then norm-defaults' author checks and `WellFormedU` on the free document and
    on each reading's document with content, in admission order, a reading's text suffixed ` under <set>@<v>:<i>`. -/
def ndText (re : VE.Readings.Wire.ReadingsEnvironment) (N : NDoc) : Option String
/-- 4.1 step 5 for one choice, after S2a's `choiceChainText (fillDoc N) c`: norm-defaults' author checks on
    `choiceU N c` in `checkAuthorN`'s order, then `WellFormedU`, the text suffixed ` under <choice>` in
    `choiceText`'s form (SR1). -/
def ndChoiceText (re : VE.Readings.Wire.ReadingsEnvironment) (N : NDoc) (c : Choice) : Option String
structure AdmittedND where
  b : VE.Readings.Wire.Admitted2
  N : NDoc
  hN : N.D = b.D
  wfU : WellFormedND N = true
  wfF : WellFormedDoc (fillDoc N) = true
/-- 4.1: S1's and S2a's admission as today; then, under the completion, `ndText`; then S1's checks of the filled
    document (`admissionText re (fillDoc N)`), each reading's document built once; then step 5 on the at most 64
    compatible choices, `choiceChainText (fillDoc N) c` and `ndChoiceText re N c` for each (SR1). -/
def admitND (environment document : Lean.Json) : Except String AdmittedND
structure SeparateReplayU where
  r : AdmittedND
  set : String
  witness : Nat
  other : Nat
  hw : (candidate (fillDoc r.N) set witness).bind (·.content) ≠ none
  ho : (candidate (fillDoc r.N) set other).bind (·.content) ≠ none
  σ : Situation VE.Bridge.Entity
  valid : σ.base.Valid (authorEnv (fillDoc r.N))
def replaySeparateU (j : Lean.Json) : Except String SeparateReplayU
theorem readings_wire_nd_separate_sound (j : Lean.Json) (x : SeparateReplayU) (h : replaySeparateU j = .ok x)
    (hs : separates (fillDoc x.r.N) x.set x.witness x.other x.σ = true)
    (hf : fillHolds x.r.N x.set x.witness x.σ.base = true) :
  AchievesU x.r.N x.set x.witness x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value ∧
    ¬ AchievesU x.r.N x.set x.other x.σ.base.asStructure (tablesOf x.σ.fixed) x.σ.probe x.σ.value
structure ChoiceReplayU where
  r : AdmittedND
  c : Choice
  hc : Compatible r.N.D c
  wfc : VE.NormDefaults.WellFormedU (choiceU r.N c) = true
  certs : List (Option VE.Tableau.Certificate)
/-- Runs `ndChoiceText` on its choice and refuses with its text, so `wfc` is checked for every replayed choice,
    one beyond the 64 of 4.1 step 5 included (SR1). -/
def replayChoiceU (j : Lean.Json) : Except String ChoiceReplayU
theorem readings_wire_nd_choice_conflict (j : Lean.Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (hv : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
  Compatible x.r.N.D x.c ∧ VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c)
theorem readings_wire_nd_choice_entails (j : Lean.Json) (x : ChoiceReplayU) (h : replayChoiceU j = .ok x)
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (VE.NormDefaults.fill (choiceU x.r.N x.c))
            (size (VE.NormDefaults.fill (choiceU x.r.N x.c))))
            (VE.NormDefaults.Wire.premisesU (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ)) φ cert = true)
    (hcf : VE.NormDefaults.Wire.conflictFreeCheckU (choiceU x.r.N x.c) x.certs = true) :
  VE.NormDefaults.ConflictFreeU.{u} (choiceU x.r.N x.c) ∧
    EntailsU.{u} (choiceU x.r.N x.c) ((choiceDoc x.r.N.D x.c).2 ++ Γ) φ
```

The three 10a wire theorems keep their statements and call the UDoc lemmas, so each proof exists once. No readings
function evaluates `Fill_T` except `fillHolds`.

### 6.4 RD-3: the fold

```lean
inductive ChoiceResult | proved | refuted | free | conflict | model | inconsistent | unknown
  deriving DecidableEq, Repr
inductive ReadingVerdict | all | some | none | unknown
  deriving DecidableEq, Repr
def foldConflict (rs : List (Choice × ChoiceResult)) : ChoiceResult :=
  if rs.any (·.2 == .conflict) then .conflict
  else if !rs.isEmpty && rs.all (·.2 == .free) then .free else .unknown
/-- composition-s2 4.6 with its gate (14.8; review A2): `conflicts` are the conflict rows of the same choices. -/
def foldEntailment (conflicts rs : List (Choice × ChoiceResult)) : ReadingVerdict :=
  if foldConflict conflicts != .free then .unknown
  else if rs.isEmpty then .unknown
  else if rs.all (·.2 == .proved) then .all
  else if rs.all (·.2 == .refuted) then .none
  else if rs.any (·.2 == .proved) && rs.any (·.2 == .refuted) then .some
  else .unknown
def foldPremises (rs : List (Choice × ChoiceResult)) : ChoiceResult :=
  if rs.any (·.2 == .model) then .model
  else if !rs.isEmpty && rs.all (·.2 == .inconsistent) then .inconsistent else .unknown
/-- What an UNKNOWN entailment names (1.7). -/
inductive Reason | conflictStatus (status : ChoiceResult) (c : Choice) | noResult (c : Choice)
  deriving DecidableEq, Repr
def reasonOf (conflicts rs : List (Choice × ChoiceResult)) : Option Reason :=
  match foldConflict conflicts with
  | .free =>
    if foldEntailment conflicts rs == .unknown then
      (rs.find? (fun x => x.2 != .proved && x.2 != .refuted)).map (fun x => .noResult x.1)
    else none
  | s => (conflicts.find? (fun x => if s == .conflict then x.2 == .conflict else x.2 != .free)).map
      (fun x => .conflictStatus s x.1)

/-- A situation of a choice's filled document where the premises hold and the conclusion fails. -/
def CounterU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) ∧
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S ∧
    Sat S Γ ∧ ¬ φ.denote S []
/-- A situation of a choice's filled document where the premises hold. -/
def ConsistentU (U : VE.NormDefaults.UDoc) (Γ : List VE.Formula) : Prop :=
  ∃ S : VE.Structure.{0},
    VE.NormDefaults.BaseAdmissibleU U (restrictAll (VE.NormDefaults.fill U).T S) ∧
    DocumentExpansion (VE.NormDefaults.fill U) (restrictAll (VE.NormDefaults.fill U).T S) S ∧ Sat S Γ
/-- What a checked result says of its choice; RD-2a's theorems establish it for every result Lean records. -/
def Holds (N : NDoc) (Γ : List VE.Formula) (φ : VE.Formula) (c : Choice) : ChoiceResult → Prop
  | .proved => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .refuted => CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
  | .free => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
  | .conflict => ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
  | .model => ConsistentU (choiceU N c) (choiceDoc N.D c).2
  | .inconsistent => VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧
      EntailsU.{u} (choiceU N c) (choiceDoc N.D c).2 .bottom
  | .unknown => True
/-- The rows are exactly the compatible choices taking `A`. -/
def Covers (N : NDoc) (A : Choice) (rs : List (Choice × ChoiceResult)) : Prop :=
  ∀ c, (Compatible N.D c ∧ ∀ x ∈ A, x ∈ c) ↔ c ∈ rs.map (·.1)
/-- The fold theorems' shared hypotheses: conflict rows `cs` and query rows `rs`, both exactly the compatible
    choices taking `A`, each row's result holding of its choice. -/
def RowsHold (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula) (cs rs : List (Choice × ChoiceResult)) :
    Prop :=
  Covers N A cs ∧ Covers N A rs ∧ (∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) ∧ ∀ x ∈ rs, Holds.{u} N Γ φ x.1 x.2

theorem fold_all_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .all) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
theorem fold_none_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .none) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
theorem fold_some_sound (N : NDoc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N A Γ φ cs rs) (h : foldEntailment cs rs = .some) :
  (∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)) ∧
  (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
  (∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ)
theorem fold_conflict_free_sound (N : NDoc) (A : Choice) (cs : List (Choice × ChoiceResult)) (hc : Covers N A cs)
    (hr : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict cs = .free) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
theorem fold_conflict_sound (N : NDoc) (A : Choice) (cs : List (Choice × ChoiceResult)) (hc : Covers N A cs)
    (hr : ∀ x ∈ cs, Holds.{u} N [] .bottom x.1 x.2) (h : foldConflict cs = .conflict) :
  ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
theorem fold_premises_model_sound (N : NDoc) (A : Choice) (ps : List (Choice × ChoiceResult)) (hc : Covers N A ps)
    (hr : ∀ x ∈ ps, Holds.{u} N [] .bottom x.1 x.2) (h : foldPremises ps = .model) :
  ∃ c, Compatible N.D c ∧ (∀ x ∈ A, x ∈ c) ∧ ConsistentU (choiceU N c) (choiceDoc N.D c).2
theorem fold_premises_inconsistent_sound (N : NDoc) (A : Choice) (ps : List (Choice × ChoiceResult))
    (hc : Covers N A ps) (hr : ∀ x ∈ ps, Holds.{u} N [] .bottom x.1 x.2) (h : foldPremises ps = .inconsistent) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c) ∧ EntailsU.{u} (choiceU N c) (choiceDoc N.D c).2 .bottom
```

The wire theorem of `readings-verdicts` chains 6.3's replay theorems with these: from a successful answer whose
verdict is ALL, NONE, SOME, CONFLICT-FREE, CONFLICT, `model` or INCONSISTENT, the matching theorem's conclusion holds
of the case's decoded document. Its exact form is fixed in RD-3's statement review, as S2a fixed
`readings_wire_all_sound`. Without the profile, the per-choice checks are today's `readings-choice` evidence kinds and
the fold is the same function.

### 6.5 RD-3: conditions and the English plan

```lean
/-- The coupling or narrowing labelled `l` fails on `c` (`couplingHolds`, `narrowingHolds`). -/
def excludedBy (D : Doc) (l : String) (c : Choice) : Bool :=
  D.couplings.any (fun K => "coupling:" ++ K.id == l && !couplingHolds D c K) ||
    D.narrowings.any (fun N => "narrowing:" ++ N.id == l && !narrowingHolds D c N)
/-- `A` names no candidate of set `s`, or names candidate `i`. -/
def allows (A : Choice) (s : String) (i : Nat) : Bool := (A.index s).all (· == i)
/-- The number of candidates of set `s`, found as `candidate` finds it; 0 when `D` has no such set. -/
def candCount (D : Doc) (s : String) : Nat := ((D.sets.find? (·.id == s)).map (·.candidates.length)).getD 0
/-- Two consecutive sets of `K` have candidates that `A` allows and whose labels on `K`'s axis differ (or one is
    missing); a coupling naming a set `D` lacks is skipped (`ve/readings_verdicts.py:126-134`). -/
def couplingExcludes (D : Doc) (A : Choice) (K : Coupling) : Bool :=
  K.sets.all (fun x => D.sets.any (·.id == x.1)) &&
  (K.sets.zip K.sets.tail).any (fun (x, y) =>
    (List.range (candCount D x.1)).any (fun i => allows A x.1 i &&
      (List.range (candCount D y.1)).any (fun j => allows A y.1 j &&
        match (candidate D x.1 i).bind (labelOf · K.axis), (candidate D y.1 j).bind (labelOf · K.axis) with
        | some l, some l' => l != l'
        | _, _ => true)))
/-- `N` is in force on a set that `A` does not fix, and drops one of its candidates
    (`ve/readings_verdicts.py:135-138`). -/
def narrowingExcludes (D : Doc) (A : Choice) (N : Narrowing) : Bool :=
  match inForce D N with
  | some R => (A.index R.id).isNone && R.candidates.any (fun a => !N.keeps.contains a.id)
  | none => false
/-- The couplings and narrowings in force that exclude some complete choice taking `A`, couplings first, each in
    document order (1.8). Computed locally, as Python computes it; it never enumerates the complete choices (SR3). -/
def restrictionsFor (D : Doc) (A : Choice) : List String :=
  (D.couplings.filter (couplingExcludes D A)).map ("coupling:" ++ ·.id) ++
    (D.narrowings.filter (narrowingExcludes D A)).map ("narrowing:" ++ ·.id)
/-- The local computation is the existential meaning, given distinct set ids, `supReady`'s coupling shape, and a
    compatible choice taking `A` (SR3). -/
theorem restrictionsFor_spec (D : Doc) (hn : (D.sets.map (·.id)).Nodup)
    (hk : D.couplings.all (couplingShape D) = true) (A : Choice) (hA : ∃ c, Compatible D c ∧ ∀ x ∈ A, x ∈ c)
    (l : String) :
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

structure Line where
  frame : String                  -- E3, E5, E7, E10, E12, E13, E17, E26, E27, E28, E29, E30, E31, E32
  result : Option String          -- R1 to R7
  readings : List (String × Nat)  -- the candidates named, in source order (the `<reading>` slot, 2.3)
  model : Option String           -- the id of the checked model shown
  gaps : List (String × List String × Bool)  -- filled gaps the result depends on: predicate, tuple, value
  label : Option String           -- an E3, E5 or E7 line's premise label
/-- The plan of the case's decoded document `D` (2.4; review E5). -/
def englishPlan (D : Doc) (route : Route) (question : String) (answer : Lean.Json) : List Line
/-- composition-s2 2.4's non-wordings hold of every plan. -/
theorem plan_no_every_for_models (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
  ∀ l ∈ englishPlan D route q a, l.model.isSome → l.frame ∉ ["E10", "E26", "E30"]
theorem plan_model_names_every_set (D : Doc) (route : Route) (q : String) (a : Lean.Json) :
  ∀ l ∈ englishPlan D route q a, l.model.isSome → l.readings.map (·.1) = D.sets.map (·.id)
```

`restrictionsFor_spec` needs three hypotheses (SR3). `hn`, distinct set ids: with a repeated id, `candidate` and
`inForce` read the first set of that id while `complete` reads each, so the two sides could disagree. `hk`, each
coupling's sets distinct open sets of `D` (`couplingShape`): two consecutive sets must be choosable independently,
and a coupling naming a set `D` lacks, which the local check skips, excludes every complete choice. `hA`, some
compatible choice takes `A`: without it the statement is false. With F-ND1's narrowing `n1` (keeping reading 0) and
`A = [(rs_1, 1)]`, the local check skips the set `A` fixes and gives `[]`, while the complete choice taking reading 1
violates `n1` (8.2 row 3.11, *computed*). Proof sketch: given a compatible choice taking `A`, changing the one or two
sets the local check names gives a complete choice that takes `A` and that the coupling or narrowing excludes;
conversely, a narrowing on a set `A` fixes excludes no complete choice taking `A`, because the compatible choice
taking `A` picks a kept candidate there. The wire establishes the hypotheses before it calls `restrictionsFor`: `hA`
by the untaken check (5 row 15), which comes first, as in Python (4.4); `hn` and `hk` are part of `supReady`, which
`choices_spec`, and so every `Covers` the wire establishes, already needs.

### 6.6 RD-4a and RD-4b: companions and components

```lean
section Companions
open Lean
/-- The array at `k`, `[]` when absent. -/
def arr (j : Json) (k : String) : List Json :=
  match j.getObjValD k with
  | .arr xs => xs.toList
  | _ => []
/-- The companion sets of a document: those whose every reading carries `companion`; a set mixing the two is
    refused (1.9). -/
def companionSets (document : Json) : Except String (List String)
/-- The merged environment of a set's companions (1.9). `sources` names each environment `<set>@<v>:<i>`. -/
def mergeCompanions (sources : List (String × Json)) : Except String Json
/-- The merged open terms of a set's companions (1.9, E4), each validated against the merged environment. -/
def mergeOpenTerms (sources : List (String × Json)) : Except String (List Json)
/-- Every case of the split: `main`, then one per companion set in source order, each an environment and a
    document (1.9); refuses a coupling across components (E3, A3). -/
def splitCase (environment document : Json) : Except String (List (String × Json × Json))
/-- A reading's identity over its own environment (3). -/
def companionMeaningId (companion content : Json) : Except String String
theorem mergeCompanions_extends (sources : List (String × Json)) (m : Json) (h : mergeCompanions sources = .ok m) :
  ∀ src ∈ sources, ∀ k ∈ ["sorts", "constants", "predicates"], ∀ (n : String) (d : Json),
    ((src.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d →
      ((m.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d
theorem mergeCompanions_identical (sources : List (String × Json)) (m : Json) (h : mergeCompanions sources = .ok m) :
  ∀ src ∈ sources, ∀ src' ∈ sources, ∀ k ∈ ["sorts", "constants", "predicates"], ∀ (n : String) (d d' : Json),
    ((src.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d →
      ((src'.2.getObjValD "vocabulary").getObjValD k).getObjVal? n = .ok d' → d = d'
theorem mergeOpenTerms_identical (sources : List (String × Json)) (ts : List Json)
    (h : mergeOpenTerms sources = .ok ts) :
  (∀ src ∈ sources, ∀ t ∈ arr src.2 "open_terms", t ∈ ts) ∧
  ∀ t ∈ ts, ∀ t' ∈ ts, t.getObjValD "name" = t'.getObjValD "name" → t = t'
/-- No reading set, coupling or narrowing is lost or duplicated by the split (A3). -/
theorem split_keeps_links (environment document : Json) (parts : List (String × Json × Json))
    (h : splitCase environment document = .ok parts) :
  ∀ k ∈ ["reading_sets", "couplings", "narrowings"], ∀ x ∈ arr document k,
    (parts.filter (fun p => (arr p.2.2 k).contains x)).length = 1
end Companions

/-- A document's components: the main document and one document per companion set (1.9). -/
structure Components where
  main : NDoc
  parts : List (String × NDoc)
def Components.all (K : Components) : List NDoc := K.main :: K.parts.map (·.2)
def CompatibleK (K : Components) (cs : List Choice) : Prop :=
  cs.length = K.all.length ∧
    ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c → Compatible N.D c
def ConflictFreeK (K : Components) (cs : List Choice) : Prop :=
  ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c →
    VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
def ConsistentK (K : Components) (cs : List Choice) : Prop :=
  ∀ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N → cs[k]? = some c →
    ConsistentU (choiceU N c) (choiceDoc N.D c).2
/-- One component's checked rows: its conflict rows and its premise rows, over every compatible choice. -/
structure ComponentRows where
  conflicts : List (Choice × ChoiceResult)
  premises : List (Choice × ChoiceResult)
def RowsSound (K : Components) (rows : List ComponentRows) : Prop :=
  rows.length = K.all.length ∧ ∀ (k : Nat) (N : NDoc) (r : ComponentRows), K.all[k]? = some N → rows[k]? = some r →
    Covers N [] r.conflicts ∧ Covers N [] r.premises ∧ (∀ x ∈ r.conflicts, Holds.{u} N [] .bottom x.1 x.2) ∧
      ∀ x ∈ r.premises, Holds.{u} N [] .bottom x.1 x.2
/-- Every component other than `k` is CONFLICT-FREE under every reading and has a model under every compatible
    choice (`every = true`) or under some choice (`every = false`). -/
def OthersSettled (rows : List ComponentRows) (k : Nat) (every : Bool) : Prop :=
  ∀ (j : Nat) (r : ComponentRows), j ≠ k → rows[j]? = some r → foldConflict r.conflicts = .free ∧
    (if every then r.premises.all (·.2 == .model) = true else foldPremises r.premises = .model)

theorem foldK_conflict_free (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (h : rows.all (fun r => foldConflict r.conflicts == .free) = true) :
  ∀ cs, CompatibleK K cs → ConflictFreeK.{u} K cs
theorem foldK_conflict (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (hne : ∀ (k : Nat) (N : NDoc), K.all[k]? = some N → ∃ c, Compatible N.D c)
    (h : rows.any (fun r => foldConflict r.conflicts == .conflict) = true) :
  ∃ cs, CompatibleK K cs ∧ ∃ (k : Nat) (N : NDoc) (c : Choice), K.all[k]? = some N ∧ cs[k]? = some c ∧
    ¬ VE.NormDefaults.ConflictFreeU.{0} (choiceU N c)
theorem foldK_consistent (K : Components) (rows : List ComponentRows) (hr : RowsSound.{u} K rows)
    (h : rows.all (fun r => foldPremises r.premises == .model) = true) :
  ∃ cs, CompatibleK K cs ∧ ConsistentK K cs
/-- ALL for the document: ALL in component `k`, every other component CONFLICT-FREE under every compatible choice
    (A2's gate on a reading of the whole document; SR2). -/
theorem foldK_all (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .all)
    (ho : ∀ (j : Nat) (r' : ComponentRows), j ≠ k → rows[j]? = some r' → foldConflict r'.conflicts = .free) :
  ∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs' ∧
    ∀ c, cs'[k]? = some c → EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
/-- NONE for the document: NONE in component `k`, every other component settled under every compatible choice. -/
theorem foldK_none (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .none)
    (ho : OthersSettled rows k true) :
  ∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs' ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∀ c, cs'[k]? = some c → CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
/-- SOME for the document: SOME in component `k`, every other component settled under some choice; every compatible
    product choice is CONFLICT-FREE (SR2). -/
theorem foldK_some (K : Components) (k : Nat) (N : NDoc) (hk : K.all[k]? = some N) (Γ : List VE.Formula)
    (φ : VE.Formula) (rows : List ComponentRows) (hrs : RowsSound.{u} K rows)
    (cs r : List (Choice × ChoiceResult)) (hr : RowsHold.{u} N [] Γ φ cs r) (h : foldEntailment cs r = .some)
    (ho : OthersSettled rows k false) :
  (∀ cs', CompatibleK K cs' → ConflictFreeK.{u} K cs') ∧
  (∃ cs', CompatibleK K cs' ∧ ∃ c, cs'[k]? = some c ∧ EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ) ∧
  (∃ cs', CompatibleK K cs' ∧
    (∀ (j : Nat) (M : NDoc) (c : Choice), j ≠ k → K.all[j]? = some M → cs'[j]? = some c →
      ConsistentU (choiceU M c) (choiceDoc M.D c).2) ∧
    ∃ c, cs'[k]? = some c ∧ CounterU (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ)

/-- 1.10: the Lean-decided rule. -/
inductive Premise | model | inconsistent | dead | narrowed | unknown
  deriving DecidableEq, Repr
def fixedDecided (status premises : ChoiceResult) : Bool :=
  (status == .free || status == .conflict) && (premises == .model || premises == .inconsistent)
/-- The unit of an open set (SR4): `rows` are its component's conflict rows, one per compatible choice (`Covers N []`,
    a choice without checked evidence `unknown`); `readings` the premise status of each of the set's readings. A
    `dead` or `narrowed` reading is in no compatible choice, so its own status decides it. -/
def setDecided (rows : List (Choice × ChoiceResult)) (readings : List Premise) : Bool :=
  rows.all (fun x => x.2 == .free || x.2 == .conflict) && readings.all (· != .unknown)
```

Proof notes for SR2. In `foldK_all`, `ConflictFreeK` holds at `k` because `foldEntailment cs r = .all` needs
`foldConflict cs = .free` (then `fold_conflict_free_sound` on `RowsHold`'s conflict rows), and at every other `j`
by `ho` and `fold_conflict_free_sound` on `RowsSound`'s rows of `j`; the models of the other components are not
needed for ALL. `foldK_some` gets its first conjunct the same way, from `OthersSettled`'s CONFLICT-FREE part.

### 6.7 RD-6a and RD-6b (off the pilot path; re-reviewed before their build)

```lean
section Extra
open VE.Compose (BaseAdmissibleP ConflictFreeP)
/-- A carried base-premise family: `Q' c` is over the vocabulary of `c`'s own document, so it mentions no choice
    symbol (review A1), and at a slot-admissible base of `sup D` encoding `c`, `Q` holds exactly when `Q' c` holds of
    the pulled base. -/
def Transfers (D : Doc) (Q : List VE.Formula) (Q' : Choice → List VE.Formula) : Prop :=
  (∀ c, Compatible D c → ∀ a ∈ Q' c, a.WellFormed (choiceEnvFull D c) []) ∧
  ∀ c, Compatible D c → ∀ B : VE.Structure.{u}, BaseAdmissibleP (correlate (sup D).1) (slotP D) B →
    Encodes D c B → (Sat B Q ↔ Sat (pull D c B) (Q' c))
/-- `supCertificateCheck` with `Q` after `slotUnder D A`. -/
def supCertificateCheckExtra (D : Doc) (A : Choice) (Q Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate) : Bool :=
  let X := correlate (sup D).1
  VE.Tableau.checkCertificate (envAt (soften X) (size (soften X)))
    (VE.Compose.backgroundP X (slotUnder D A ++ Q) ++ VE.Norms.elaborate (soften X).T ++ ((sup D).2 ++ Γ)) φ cert
/-- `supModelCheck` with `Q` after `slotUnder D A`. -/
def supModelCheckExtra {α : Type u} [DecidableEq α] (D : Doc) (A : Choice) (Q Γ : List VE.Formula)
    (M : VE.FiniteModel α) : Bool :=
  let X := correlate (sup D).1
  VE.Compose.backgroundValidP X (slotUnder D A ++ Q) M && ((sup D).2 ++ Γ).all (fun a => (VE.SoftNorms.circ X a).eval M [])
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
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)) :
  φ.denote (expand (choiceDoc D c).1 B) []
theorem superpose_countermodel_extra {α : Type u} [DecidableEq α] (D : Doc) (h : WellFormedDoc D = true)
    (hch : D.chain ≠ .rights) (hs : superposable D = true) (A : Choice)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (M : VE.FiniteModel α)
    (valid : M.Valid (envAt (soften (correlate (sup D).1)) 0)) (hm : supModelCheckExtra D A Q Γ M = true)
    (hn : (VE.SoftNorms.circ (correlate (sup D).1) φ).eval M [] = false) :
  ∃ c, Compatible D c ∧ (∀ x ∈ A, x ∈ c) ∧ Encodes D c M.asStructure ∧
    BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c)
      (pull D c M.asStructure) ∧
    Sat (expand (choiceDoc D c).1 (pull D c M.asStructure)) ((choiceDoc D c).2 ++ Γ) ∧
    ¬ φ.denote (expand (choiceDoc D c).1 (pull D c M.asStructure)) []
theorem transfers_nil (D : Doc) : Transfers.{u} D [] (fun _ => [])

theorem fill_transfers (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true) :
  Transfers.{u} (fillDoc N) (VE.NormDefaults.fillPremises (supU N)) (fun c => VE.NormDefaults.fillPremises (choiceU N c))
theorem nd_superpose_conflict_free (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome) :
  ConflictFreeP.{u} (correlate (sup (fillDoc N)).1) (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)) ↔
    ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → VE.NormDefaults.ConflictFreeU.{u} (choiceU N c)
theorem nd_superpose_all (N : NDoc) (hN : WellFormedND N = true) (hF : WellFormedDoc (fillDoc N) = true)
    (hs : superposable (fillDoc N) = true) (hsu : VE.NormDefaults.WellFormedU (supU N) = true)
    (A : Choice) (hA : ∀ x ∈ A, (candidate N.D x.1 x.2).isSome)
    (hcf : ConflictFreeP.{u} (correlate (sup (fillDoc N)).1)
        (slotUnder (fillDoc N) A ++ VE.NormDefaults.fillPremises (supU N)))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv (fillDoc N)) [])
    (hφ : φ.WellFormed (sharedEnv (fillDoc N)) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra (fillDoc N) A (VE.NormDefaults.fillPremises (supU N)) Γ φ cert = true) :
  ∀ c, Compatible N.D c → (∀ x ∈ A, x ∈ c) → EntailsU.{u} (choiceU N c) ((choiceDoc N.D c).2 ++ Γ) φ
end Extra
```

The up-direction of the `_extra` theorems uses `Transfers`' first conjunct: `base_up`'s extension agrees with the
original base on every predicate except the choice vocabulary, which a formula well formed over `c`'s own document
cannot mention. The approved S2a statements are the instances at `transfers_nil`; none is restated. For
`fill_transfers`: a `Fill_T` formula is `bindAll` of `pairConflict` and two `gapF`s, and `circ_canon`, `pull_canon` on
`fillDoc N` and `sim_decides` on `N.D` make the two `Fill_T` lists agree at an encoded slot-admissible base (the
`F_p` units are fixed, so they are their own images).

## 7. What is not claimed

- No theorem relates the product of components to a merged frame: the UDHR's merged frame would hold 156 regulated
  predicates, beyond the frozen 64. `product_merge_faithful` stays open (plan 7).
- No completeness of separation is claimed: an unseparated pair is equal meaning or a search miss (1.5).
- No speed, no audit outcome and no coverage figure before RD-5 measures it.
- The `readings-verdicts` wire theorem's exact form is fixed in RD-3's review (6.4); the wire functions without a body
  here were checked for their types only.

## 8. Acceptance fixtures

Each "exactly when" or iff claim of this spec has a fixture for each direction; the claim is named in the last
column. *Computed* values are the stub's `#eval` output on `ve-nightly`'s build.

### 8.1 Lean fixtures of RD-1 (`UnspecifiedExamples.lean`, `#guard`)

**F-ND1.** Sorts `agent`, `user`; base predicate `asks(user, agent)`; `help_required(agent, user)` an obligation,
`unspecified` (placeholder `deny`), act `{0} help {1}`, permission `help_permitted`; `help_permitted(agent, user)` a
permission, `unspecified`, the same act. Set `rs_1` on unit `u1`: reading 0 `every` is the strict rule `must-help` on
`+help_required`, guard ⊤; reading 1 `asks` is `must-help` with guard `asks(user, agent)`. `N.unspec` lists both
predicates. The base `base1 P`: one agent `a`, one user `u`, `asks` empty, `unsaid__help_permitted` = `P`,
`unsaid__help_required` empty; the probe is the outcome of `help_required` at `(a, u)`.

| # | Case | Expected | Source | Claim |
|---|---|---|---|---|
| 1.1 | units of `fillDoc` | `u1`, `unsaid--help-required`, `unsaid--help-permitted`, the `F_p` units last | *computed* | 1.3 |
| 1.2 | `over` of both readings in `fillDoc` | `[unsaid--help-required]` each | *computed* | 1.3 change 2 |
| 1.3 | `normsShaped`, `fillNamesFree`, `WellFormedDoc` of `N.D` and of `fillDoc N`, `WellFormedND` | all true | *computed* | 1.4 |
| 1.4 | the four equalities on the instance (sorts, literals, regulated, rules, and predicates on every name used, `ve__bit__1__0` for `sup`) | `fillDoc_one` true for readings 0 and 1, `fillDoc_free` true, `fillDoc_choice` true for both choices, `fillDoc_sup` true | *computed* | 6.2 |
| 1.5 | `separates (fillDoc N) rs_1 0 1` on `base1 [(a, u)]`, value true; `fillHolds` of reading 0 | true; true: separated with witness 0 | *computed* | `separates_soundU` |
| 1.6 | the same with `P` empty | `separates` true but `fillHolds` false: the witness's filling breaks its `Fill_T`, so admission refuses the situation (`distinguishing model violates a generated premise`) | *computed* | `achievesU_iff` (←: no `AchievesU` without `Fill_T`) |
| 1.7 | witness 1, value false, on `base1 [(a, u)]` | `separates` true, `fillHolds` of reading 1 true: separated the other way (the shared filling answers the gap of reading 1 'no') | *computed* | `separates_soundU`, the other direction |
| 1.8 | witness 1 with value true; witness 0 with value false | false, false: not separated | *computed* | `separates` false cases |
| 1.9 | F-ND1 with a narrowing `n1` keeping reading `every`: `compatible` of choices `[(rs_1, 0)]` and `[(rs_1, 1)]` on `fillDoc N` and on `N.D` | `(true, true)` and `(false, false)` | *computed* | `compatible_fillDoc`, both directions |
| 1.10 | compatible choices (what `Covers` ranges over) of F-ND1 and of F-ND1 with `n1` | `[[(rs_1,0)],[(rs_1,1)]]` and `[[(rs_1,0)]]` | *computed* | `Covers` |

**F-ND5 (collision; review A1).** F-ND1's frame; a fixed unit `u0` with the strict root rule `be-helpful` on
`help_required`; set `rs_1` whose one reading declares a rule named `unsaid--help-required` (on `help_permitted`).

| # | Case | Expected | Source | Claim |
|---|---|---|---|---|
| 5.1 | `fillNamesFree`, `WellFormedDoc`, `normsShaped` | false, true, true: S1 alone admits it | *computed* | `fillNamesFree` (← direction; 1.3 gives the → direction) |
| 5.2 | `attached u0` in `N.D` and in `fillDoc N` | `[]` and `[rs_1]` | *computed* | `attached_fillDoc` fails without `hf` |
| 5.3 | rule names of `soften (correlate (free (fillDoc N)).1)` and of `fill (freeU N)` | `[unsaid--help-required, unsaid--help-permitted]` and `[be-helpful, unsaid--help-required, unsaid--help-permitted]`; the equality is false | *computed* | `fillDoc_free` needs `hf` |
| 5.4 | admission | `InvalidInput: reserved name unsaid--help-required` (4.1 step 2, no suffix) | *derived*, RD-2a | 5 row 2 |

**F-ND0.** F-ND1 with `unspec = []`: `fillDoc` has the items of `N.D` (unit `u1` only, item lists equal) and the same
free document (*computed*; `fillDoc_conservative`).

### 8.2 Lean fixtures of RD-3 (`#guard`)

The choices `c0`, `c1`, `c2` stand for three compatible choices; rows are given as results in choice order.

| # | Conflict rows | Query rows | Expected | Source | Claim |
|---|---|---|---|---|---|
| 3.1 | free, free, free | proved, refuted, unknown | SOME, no reason | *computed* | gate passed; SOME tolerates a missing result |
| 3.2 | free, free, unknown | proved, proved, proved | UNKNOWN, `conflictStatus unknown c2`: `UNKNOWN (conflict status: UNKNOWN)` naming `rs_1@1:2` | *computed* | gate (A2) |
| 3.3 | free, conflict | proved, proved | UNKNOWN, `conflictStatus conflict c1`: `UNKNOWN (conflict status: CONFLICT)` naming `rs_1@1:1`; never ALL | *computed* | gate (A2) |
| 3.4 | free, free | proved, proved | ALL | *computed* | ALL exactly when every row proved, past the gate (→) |
| 3.5 | free, free | refuted, refuted | NONE | *computed* | NONE likewise |
| 3.6 | free, free, free | proved, proved, unknown | UNKNOWN, `noResult c2` | *computed* | ALL's ← direction: one row short |
| 3.7 | `foldConflict` of [free, free], [free, unknown, conflict], [free, unknown], [] | CONFLICT-FREE, CONFLICT, UNKNOWN, UNKNOWN | *computed* | `foldConflict`, each direction |
| 3.8 | `foldPremises` of [inconsistent, model], [inconsistent, inconsistent], [inconsistent, unknown] | `model`, INCONSISTENT, UNKNOWN | *computed* | `foldPremises` |
| 3.9 | `restrictionsFor` with `n1` under `A = []`; under `A = [(rs_1, 0)]`; F-ND1 without `n1` | `[narrowing:n1]`; `[]`; `[]`; each equal to the existential side (the stub's brute force over the complete choices), a compatible choice taking `A` in the first two | *computed* | `restrictionsFor_spec`, narrowing part, both directions |
| 3.10 | `usedLabels` with `L = [(unsaid:pair:help_required,help_permitted, P), (other, ⊥)]`: a check needing `P`; a check needing nothing; a check needing both | `[unsaid:pair:…]`; `[]`; both labels | *computed* | `usedLabels_sound` |
| 3.11 | `restrictionsFor` with `n1` under `A = [(rs_1, 1)]`, which no compatible choice takes | `[]`, while the existential side is `[narrowing:n1]`: false without `hA`. The wire never reaches it: `ReadingsUnsatisfiable: no compatible reading takes rs_1@1:1` first (5 row 15; the text *derived*, RD-3) | *computed* | `restrictionsFor_spec` needs `hA` (SR3) |
| 3.12 | two sets `rs_1`, `rs_2`, each F-ND1's readings with reading 0 labelled `all` and reading 1 `some` on axis `who`, and coupling `k1` over both: `restrictionsFor` under `A = []`; `[(rs_1, 0)]`; `[(rs_1, 0), (rs_2, 0)]` | `couplingShape` true; compatible choices `[(rs_1,0),(rs_2,0)]` and `[(rs_1,1),(rs_2,1)]`; `[coupling:k1]`; `[coupling:k1]`; `[]`; each equal to the existential side | *computed* | `restrictionsFor_spec`, coupling part, both directions (SR3) |
| 3.13 | thirty sets `rs_1` to `rs_30` of two readings each (F-ND3's), each with a narrowing `n<k>` keeping reading 0 | one compatible choice of 2^30 = 1,073,741,824 complete ones; `restrictionsFor` under `A = []` gives the 30 labels `narrowing:n1` to `narrowing:n30` without enumerating them | *computed* | no cap and no product (SR3) |

Through the service (`tests/test_readings_nd_lean.py`, RD-3; *derived*):

| Case | Expected |
|---|---|
| F-ND1, conflict | CONFLICT-FREE under every reading, `conditional_on: ["unsaid:pair:help_required,help_permitted"]`; E26 with R1, E3 with the pair sentence |
| F-ND1, `∀ agent ∀ user. help_required` | SOME: E12 R2 for reading `every`, E12 R3 for reading `asks` with one filled-gap sentence (`help_required(a, u)` answered 'no'); each `<reading>` slot shows the candidate's sentence (2.3) |
| F-ND1, the same with `--under rs_1:0` | ALL; E12 naming reading `every` only |
| F-ND1, `∀ agent ∀ user. help_required → help_permitted` | ALL, `conditional_on: ["unsaid:pair:help_required,help_permitted"]` (the conflict certificates need the label) |
| F-ND2 (plan RD-2a), conflict | CONFLICT under reading 0 (latent), witness choice named; E12 R4 and the latent-conflict sentence |
| F-ND3, the query of F-ND1 | UNKNOWN (budget), or `UNKNOWN (not ALL: countermodel under …)` with a countermodel; E28 |
| A certificate for choice 0 supplied as choice 1's | that choice `unknown`; never ALL |
| F-ND1 with `n1`, the query of F-ND1 with `--under rs_1:1` (SR3) | `ReadingsUnsatisfiable: no compatible reading takes rs_1@1:1`, before any condition is computed |
| 3.13's thirty sets through `readings-verdicts`, the conflict question (SR3) | `restrictions` lists the 30 labels, within the latency budgets of lean-first section 4 (the batch gate's) |
| S2a's M8, M9, M12 | the same verdicts and English (Python fold before, Lean fold after), DELTA `none`; the 2.3 slot change a signed `wording` change; S2a's M4 (verb-only) keeps the italic verb |

### 8.3 Wire fixtures of RD-2a (through the service; *derived* unless marked)

| # | Case | Expected |
|---|---|---|
| F-ND1 | `readings-validate` | admitted; pair (0, 1) separated with witness 0; `fill_premises` lists `unsaid:pair:help_required,help_permitted` for both readings. Before RD-2a: the abstention text |
| F-ND1′ | F-ND1's situation with `unsaid__help_permitted` empty | `distinguishing model violates a generated premise` (8.1 row 1.6) |
| F-ND2 | norm-defaults' u6 as readings (plan RD-2a) | admitted; choice 0 CONFLICT (latent); choice 1 CONFLICT-FREE; pair (1, 0) separated |
| F-ND3 | seven sets of two readings each, as F-ND1 | `readings-elaborate`: enumerated, `choice_count: "over 64"`. *Computed*: the search stops at 65 choices (64 + 1) of 2^7 = 128 |
| F-ND4 | 252 fixed rules on `p` (four unspecified predicates), one set with one more rule on `p` | `ResourceLimit: rules under rs_1@1:0`. *Computed*: the free document has 252 + 4 = 256 (within 256), the reading's document 253 + 4 = 257 (beyond); no fixed unit uses a name, so none is attached |
| F-ND5 | 8.1's collision document | `InvalidInput: reserved name unsaid--help-required` |
| F-ND6 | K18 (the soft chain under the profile) | the abstention text, unchanged |
| F-ND7 | every S1 fixture K1 to K22 and S2a fixture M1 to M20 | byte-identical verdicts, identities and English, except the signed 2.3 slot on M8, M9, M12 (from RD-3 on; 4.6, SR5) |
| F-ND8 | tampering: a package bound to choice 0's document replayed for choice 1; an ill-typed filling tuple; an `unsaid__` table outside the profile | refused or UNKNOWN, never CONFLICT-FREE, `proved` or `model` |
| F-ND9 | a guard large enough that the filled tree's generated layer for its predicate passes `checkAuthorN`'s 10,000-node budget but not the soft chain's limit for one generated layer (sized by the test from `generatedSizes`) | `ResourceLimit: generated norm layer layer:norms:<p> under rs_1@1:0` |
| F-ND10 (SR1) | 251 fixed rules on `p` (F-ND4's frame, four unspecified predicates), and two sets `rs_1`, `rs_2` of one reading each, each holding one more rule on `p` | steps 1 to 4 pass; 4.1 step 5 refuses the document, on its one compatible choice, with `ResourceLimit: rules under rs_1@1:0, rs_2@1:0`. *Computed*: the free document has 251 + 4 = 255 rules, each reading's document 252 + 4 = 256 (within 256), the choice's 253 + 4 = 257. S2a's chain text on the filled choice document is the same text here (W1's 256 rules, *derived*); RD-2a's `#guard` on `WellFormedU (choiceU N c)` pins the norm-defaults check itself |

### 8.4 Fixtures of RD-4a and RD-4b (*derived*)

| # | Case | Expected | Claim, direction |
|---|---|---|---|
| F-C1 | two companion sets of two readings each over disjoint frames (F-ND1's frame twice, the second with `help`→`warn`, `asks`→`calls`), plus a main fixed norm | three components, each admitted and separated; per-component answers as F-ND1's; E32, E31 twice | companion set (→) |
| F-C2 | in one set, `avoid_life_required` declared `(bearer, person)` and `(state, person)` | `InvalidInput: readings rs_a@1:0 and rs_a@1:1 declare avoid_life_required differently` | merge (←: different bytes) |
| F-C3 | one reading with a companion, one without | `InvalidInput: reading set rs_a mixes readings with and without their own vocabulary` | companion set (←) |
| F-C4 | companions of one set with different `profiles` | `InvalidInput: the readings of rs_a declare different profiles` | 5 row 9 |
| F-C5 | identical `person` sorts in two readings of one set | one `person` sort in the merged frame | merge (→: identical bytes unify) |
| F-C6 | a main fixed rule whose `over` names a companion reading's rule | `UnknownRule: rule <name>` in the main component | 5 row 14 |
| F-C7 | `companionMeaningId` on `u022a.entitlement`, `u048.state_negative`, `u074.prohibition` | equal to run 20261006T1800Z's recorded `meaning_id` (the unit's id for u074); if not, the batch adds the canonical encoder Python's `rule.to_dict()` uses, with a byte-parity fixture | 3 |
| F-C8 | a companion with `soft-norms@0` | `UnsupportedProfile: readings with their own vocabulary on the soft or rights chain are not implemented` | 5 row 8 |
| F-C9 | F-C1 with a coupling over the two companion sets; then a coupling over two main sets | refused, 5 row 7; the second is kept in the main case | coupling refused exactly when it spans components, both directions |
| F-C10 | two readings of one set declaring open term `ill_treatment` differently; then identically | refused, 5 row 11; one entry in the component's document, validated against the merged frame; the main case keeps only its own open terms | open-term merge, both directions |
| F-C11 | F-C1 with a narrowing on the first companion set | the narrowing and its label are in that component's case only (`split_keeps_links`); that component's `restrictions` list it, the other's do not | narrowings travel (A3) |
| F-C12 | F-C1 with the second companion set left on W2 (content null, no companions) | in the main case with W2's UNKNOWN, never a component; nothing else changes | pending sets visible (A3) |
| F-C13 | a query on F-C1 with `--under` naming the other component's set; then its own set | refused, 5 row 18; accepted | `--under`, both directions |
| F-C14 | a conclusion over no component's terms; over both components' shared terms without `--sentence`; the same with `--sentence`; over one component's terms | 5 row 16; 5 row 17; accepted; accepted | conclusion typing, each case |
| F-C15 | F-C1 with the second component's reading 1 asserting ⊥ | a query's NONE in the first component becomes UNKNOWN, "another sentence's readings are not all consistent" | `foldK_none`'s `OthersSettled` |
| F-C16 | `decided_units` on F-C1; on F-C1 with one choice's evidence missing | every unit with content; that component's units absent (its conflict rows read per choice, SR4) | 1.10, both directions |
| F-C17 (SR2) | F-C1 with F-ND2's fixed unit `no-x` and set `rs_2` added to the main case, so the main component is CONFLICT under `rs_2`'s reading 0 (latent); the query `∀ agent ∀ user. help_required → help_permitted` with `--sentence` naming the first companion set's unit, where it is ALL (as on F-ND1) | for the document, `UNKNOWN (conflict status: CONFLICT)` naming `rs_2@1:0`; the same with the main component's conflict evidence missing, `UNKNOWN (conflict status: UNKNOWN)` naming its first choice, `rs_2@1:0`; on F-C1 itself, ALL. Each time the companion component's own ALL is in its `components` entry | `foldK_all`'s `ho`, both directions |

1.10's rule itself, *computed*: `fixedDecided` is true for (CONFLICT-FREE, `model`) and false for (CONFLICT-FREE,
UNKNOWN) and (UNKNOWN, `model`). `setDecided` (SR4), with rows over two choices `c0`, `c1`, is true for rows
`[free, free]` with readings `[model, dead, narrowed, inconsistent]` and for rows `[conflict, free]` with
`[model, model]`; it is false for rows `[free, free]` with `[model, unknown]`, for rows `[free, unknown]` with
`[model, model]`, and for rows `[conflict, unknown]` with `[model, model]`, the case a single folded status (CONFLICT)
would have hidden.

### 8.5 RD-6 (off the pilot path; *derived*)

F-ND1 and F-ND2 take the superposed route with the same verdicts as 8.2's enumerated answers: F-ND1 CONFLICT-FREE on
both routes, F-ND2 CONFLICT on both (`nd_superpose_conflict_free`, each direction). F-ND3 (128 choices) gets decided
verdicts. A 200-document differential of generated norms-chain documents under the profile, at most 64 choices,
gives identical verdicts on both routes.

### 8.6 RD-5's demonstrations (UDHR, sets that merge unchanged; *derived* from the companions at `bd6c7ab2`)

| Set | Query | Expected, per reading |
|---|---|---|
| `rs_u029` (`entitlement`, `state_claim`) | every State must recognise each person everywhere as a person before the law | SOME: follows under `state_claim` (guard ⊤); does not follow under `entitlement` (no rule decides the duty; the gap answered 'no') |
| `rs_u081` (`entitlement`, `state_claim`, `state_claim_within_resources`) | every State whose organization and resources allow it must secure each person social security | SOME: does not follow under `entitlement`; follows under both State readings. With `--under rs_u081:2`: ALL, naming that reading |
| `rs_u081` | no State must secure any person social security | NONE: refuted under `state_claim` and `state_claim_within_resources` by their rules (resources allowing), under `entitlement` by a filling answering the gap 'yes' (its filled-gap sentence shown) |

Both sets merge unchanged: `rs_u029`'s companions repeat only the sort `person`, identically; `rs_u081`'s repeat
`person`, `state` and `secure_social_security_required` with identical declarations, and the open term
`social_security` with identical entries. `rs_u022a`, `rs_u027` and
`rs_u055` declare one predicate over `state` in one reading and over `bearer` in another, and `rs_u052`'s copied
companion would declare `arises_from_*` without the `verbalisation` its other companion gives them, so none of them
migrates (plan 1.1, E1).

## 9. Limits

As the plan's 3.8, unchanged: 64 regulated predicates per environment (the main frame and each merged frame); 256
rules and 256 rules plus unspecified predicates per document, each choice's included (*computed* boundaries: F-ND4
for a reading's document, F-ND10 for a choice's, SR1); 56 bytes per unspecified
name; precedence height 15; 10,000 AST nodes with the `F_p` guards; 32 sorts and 256 predicates per frame; 64
compatible choices per component on the enumerated route (*computed*: F-ND3 stops at 65); 64 readings per set;
4,000,000 document bytes; 120 s wall for the pilot's load.

## 10. The measure (plan 3.9 and 5)

The Lean-decided share sums the span bytes of Lean's `decided_units` (1.10); `tools/lean_decided_share.py` decides
nothing. Before: 0 bytes (*derived*). The upper bound the rule allows is the CHECKED and READINGS bytes,
57 + 4,200 = 4,257 of 10,916, 39.00% (*computed*), arithmetic and not a prediction; claimed coverage 43.90% and
audit-verified 23.30% (*computed* from the recorded 4,792 and 2,543 bytes) are reported unchanged beside it. Beside
the share (review E2): the maximum rules in one choice's document, the decided bytes whose companions were already
checked outside the document, and, beside a Lean answer only, the sentence that a rule checked by itself is
CONFLICT-FREE by construction (the isolated rule; a one-rule reading checked with the other rules can be a CONFLICT,
as S2a's M8 is under one choice). The
report says that a rise measures checks routed into Lean inside the document, not new assurance.

## 11. Statement review checklist (Astra + Fable, before RD-1)

Draft 2's targeted re-review covers the SR parts of items 4, 8, 10, 12 and 13, with 1.1, 1.8, 1.10, 2.4 item 3,
4.1 step 5, 4.3 to 4.6, rows 5 and 15 of 5, the changed declarations of 6.3, 6.5 and 6.6, and the fixtures marked SR.

1. Every statement of 6 is true under its hypotheses, not only well typed (the gate).
2. The four equalities with `normsShaped` and `fillNamesFree`; F-ND5 shows the second is needed; `attached_fillDoc`
   and `achievesU_iff` carry it too.
3. `normsShaped` is what `Wire.decodeNorm` on `.norms` guarantees.
4. Admission's order (4.1), each text as `checkAuthorN` and S1 word it, and the suffix rule; step 5 and
   `ndChoiceText`, with `replayChoiceU` establishing `wfc` (SR1, F-ND10).
5. Shared fillings (1.5, E5) and `separates_soundU`: the witness's `Fill_T` is checked, the other side's may fail.
6. The gate (A2): `foldEntailment` takes the conflict rows; every entailment theorem concludes conflict freedom of
   every covered choice; `Holds.inconsistent` carries `ConflictFreeU`; 8.2 rows 3.1 to 3.3.
7. Universes: witnesses and countermodels in universe 0, as in `Layered.lean`; `ConflictFreeU.{u}` elsewhere.
8. `restrictionsFor`'s local body and `restrictionsFor_spec` with `hn`, `hk` and `hA` (SR3, 8.2 rows 3.9 and 3.11
   to 3.13); `usedLabels_sound`.
9. The English of 2 (one reading each, the `<reading>` slot of A4, non-wordings, E31's honesty).
10. The split contract (A3, E3, E4) and `split_keeps_links`; the product statements with `OthersSettled`, and the
    product gate on ALL, SOME and NONE, each concluding `ConflictFreeK` (SR2, F-C17).
11. `Transfers`' typing conjunct (RD-6, off path).
12. 1.10's rule, conflict results read per compatible choice (SR4), and that the script decides nothing; E2's
    qualifiers.
13. Conservativity (4.6) as three guarantees, the 2.3 slot the one signed English exception, and F-ND7 (SR5).

## 12. Differences from the plan's Lean blocks

The plan's blocks with the converged edits applied are the input; elaborating them changed these points, each fixed
here and not in merged code:

1. **Binder types.** The plan's `∀ k (N : NDoc) (c : Choice), K.all[k]? = …` and `∃ k (N : NDoc) c, …` do not
   elaborate (the index type is not inferred; mixed binder syntax). Here `(k : Nat)`, `(c : Choice)`,
   `(r : ComponentRows)` are written out.
2. **`ConsistentU` moved to RD-3** and `Holds.model` defined by it, instead of restating its body (one definition).
3. **`RowsHold`** names the four hypotheses every gated fold theorem shares (conflict rows and query rows covered, each
   holding); the plan's statements list them inline. The statements are the same.
4. **RD-4b's rows** carry conflict rows and premise rows per component (`ComponentRows`), since the gate needs both;
   `foldK_none` and the new `foldK_some` take `OthersSettled`, which adds CONFLICT-FREE of the other components, and
   `foldK_all` takes `RowsSound` and the other components' CONFLICT-FREE fold (`ho`; SR2): a reading of the whole
   document is CONFLICT-FREE only when each of its components' choices is, so A2's gate applies to it (4.5). All
   three conclude `ConflictFreeK` of every compatible product choice; draft 1's `foldK_all` gated component `k` only,
   and its `foldK_some` did not conclude it.
5. **Added statements**: `foldPremises` with `fold_premises_model_sound` and `fold_premises_inconsistent_sound` (D5's
   premise statuses had no Lean statement); `reasonOf` (what an UNKNOWN names); `foldK_conflict` and `foldK_some`
   (plan 3.6's CONFLICT and SOME rows); `mergeCompanions_identical`, `mergeOpenTerms_identical` and
   `split_keeps_links` (D7, E4 and A3 as statements); `supModelCheckExtra` (used by `superpose_countermodel_extra`,
   which the plan stated with `supModelCheck` and `hQ`); `fixedDecided` and `setDecided` (3.9's rule; `setDecided`
   reads its component's conflict rows per compatible choice, SR4, where draft 1 took one folded status).
6. **`restrictionsFor`** has a body, local as Python's (SR3; draft 1's enumerated every complete choice), and
   `restrictionsFor_spec` takes distinct set ids, `supReady`'s coupling shape and a compatible choice taking `A`, each
   needed (6.5).
7. **The plan's readings-level `unspecDeclared`** is dropped: `WellFormedU (freeU N)` contains norm-defaults'
   `unspecDeclared` of the same regulated list.
8. **`superpose_countermodel_extra`** reads `Q` through `supModelCheckExtra` (`Q` after `slotUnder D A` in the base
   check) instead of the plan's extra hypothesis `hQ : Q.all (fun a => a.eval M []) = true` beside `supModelCheck`.
   The two say the same of `M`; this form mirrors `supCertificateCheckExtra`, so the checker RD-6b runs is the one the
   theorem names. Off the pilot path; its review may restore the plan's form.
9. **Draft 2 (statement review, SR1 to SR5).** Added `ndChoiceText` (the plan's RD-2a block had none, and no step
   established `ChoiceReplayU.wfc`). Changed `restrictionsFor` (item 6), `foldK_all` and `foldK_some` (item 4) and
   `setDecided`'s arguments (item 5). Dropped `completeFrom` and `restrictionLabels`, which only draft 1's
   enumerating body used. Elaboration: the changed declarations and the new fixtures were elaborated in the same
   untracked stub with `lake --dir <ve-nightly>/lean env lean <stub>`, against `ve-nightly` at `48cc65a6` (`main`).
   Its `lean/` differs from `6cbe1a26` in the attribution, rights, norms and response-shape files, the generated
   lists, `Readings/Separate.lean` (2 lines) and the move of `Readings/Layers.lean` to `SoftNorms/Once.lean`; it does
   not differ in `Readings/{Doc,Choice,Route,Wire}.lean` or `NormDefaults/*.lean`, which the changed statements read.
   The same run re-elaborated every draft-1 statement and reproduced every draft-1 *computed* value. Values marked
   *computed* in SR rows are that run's `#eval` output; the stub's brute force over the complete choices (an oracle
   for rows 3.9 and 3.12 only) is not part of the spec.
