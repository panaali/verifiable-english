# Commands and imperatives addressed to a reader: buildable plan

> Status: **plan draft 3** (2026-10-30): the cross-plan synthesis round 2 edits and the DRI's fidelity-pilot revision,
> section 12 (`manage-agents/debates/plan-synthesis-2/edits-commands-imperatives.md`,
> `manage-agents/reviews/dri-decisions-20261030-fp-commands-imperatives.md` item 1). Before it: **plan draft 2,
> statement-review corrections applied**, 2026-10-28, branch `design/commands-imperatives` from `main` at `6d0a10526`. Docs only: no
> product code, no test, no generated file, no model call. Research: [docs/research/commands-imperatives.md](../research/commands-imperatives.md),
> cited below as R with its section numbers. The design extends `speech-acts@0` ([speech-acts.md](speech-acts.md),
> cited as SA) and does not redesign it.
>
> **Draft 2** applies the joint position of the plan debate (`manage-agents/debates/design-commands-imperatives`,
> converged on REVISE after round 2, both reviewers keeping the architecture), and nothing beyond it. The change log
> below maps each point to the section that applies it, in the reviewers' own labels: A1 to A6 are Astra's round-1
> points, which Fable conceded in round 2, and (i) to (iv) are Fable's four further fixes, which Astra accepted. The
> hours are draft 1's. A2 and A3 add work to CI-2, CI-3, CI-6 and CI-7, and CI-0 re-estimates those batches.
>
> **Adopted.** The DRI signed draft 2 as the plan on 2026-10-28 (`manage-agents/reviews/dri-decisions-20261028-commands-imperatives.md`,
> item 1) and recorded the cross-plan rulings that sections 9 and 11 now carry (items 2 to 5). Three places of draft 2
> contradicted those rulings and are aligned with them: D6 and CI-4's purpose-clause row (item 4(c)), and CI-2's legend
> (item 4(e)). The later item-1 statement review changed the operative statements and fixtures as recorded below.
>
> **Status of the Lean blocks.** They are this plan's proposed statements. The item-1 spec
> ([commands-imperatives.md](commands-imperatives.md)) is authoritative. Its original CI-0 stub elaborated statements
> as propositions, which did not prove them; the converged statement review in
> `manage-agents/debates/commands-imperatives-spec` required the further corrections now recorded in both files.
> Revised CI-2 to CI-7 definitions, theorem statements and constructed counterexamples must be re-elaborated and
> exercised by their batches. Where an older plan block still differs, the spec is the one to build. The
> exception is section 12 (2026-10-30: the cross-plan synthesis round 2 edits, which apply the converged plan
> debate's round-2 edits, N7, and the DRI's fidelity-pilot revision): it is newer than the spec, so where they differ
> section 12 and the blocks it revises govern, and the batch re-elaborates the spec's statement to match. For
> example, VE identifiers begin with a lower-case letter, so the spec's `E_web` names `draft`, not `draft`. The names
> of existing definitions they use were read from this branch's base
> `6d0a10526`: `VE.SpeechActs.{Scope, Command, Force, SpeechDoc, demand, policy, commandOk, scopeOk}`,
> `VE.SpeechActs.Wire.{SpeechEnvironment, surfaceWords, actVerb, asciiWording, decodeClosedField, parseScope,
> encodeScope, phraseOk, profileGate, allowlist, surfaceKind, choiceKindConflicts, stripSpeech,
> decodeSpeechEnvironmentFull}`, `VE.SpeechActs.Source.decodeSpeechSource`, `VE.Norms.{Regulated, Role}`,
> `VE.Norms.Wire.decodeNormsEnvironment`, `VE.EnglishGrammar.{Env, Overlay, Lexicon, ConstDecl, translate,
> TranslateOutcome, fillHoles}`, `VE.EnglishGrammar.Env.declaredSpelling`, `VE.Compose.{profileTable, gateOf,
> actsRefuses, gate_acts, today_speech}` and `EFormula.encode`. CI-0's stub elaborates every block against `main`
> before any build; a failure is fixed in the spec, never in merged code.
>
> **Bytes.** Every byte figure is an **estimate**: R 2.1's hand classification of the pinned web-copy segments, with
> R's hand byte counts. CI-8 recomputes the bytes by program, and no coverage number is published before it does.

**Change log, draft 1 to draft 2.** Each point of the joint position, and the section that applies it.

| Point | What draft 2 does | Where |
|---|---|---|
| Agreed: the architecture | `Command` and `demand` unchanged; Lean reads command English; D4, the stated order is no rule | D1, D2, D4 (unchanged) |
| A1, guard outcomes | `guardOf` returns `Except GuardFault VE.Formula` over english-lean's `translate`. An ambiguous condition gives `many` with every guard; an exhausted one gives `limit`; an unread one refuses with the reader's code and text. `readCommand_typed` gains a decoded-environment hypothesis and `scopeOk D` | 2 CI-1 (statements, diagnostics, rows W17 to W19) |
| A2, reading context | A command fence without reading context is `InvalidInput`; the "when the payload carries" path goes | 2 CI-2 |
| A3, one public entry | `readUnit` is called by the mode and by the source wrapper. CI-3, CI-6 and CI-7 each extend it with its response shape, encoder theorem and inventory rows. `StepOutcome.many` carries readings (`Alt`). CI-7 depends on CI-6. `listItem` is deferred until a scope x speech row exists (C4) | D2, D5, 1, 2 CI-2, CI-3, CI-6, CI-7, 4, 5 |
| A5, labels | Labels and quoted wordings are english-lean constant spellings (`ConstDecl.display`, `Overlay.constants`, `Lexicon.spellings`, `declaredSpelling`). `this` phrases go into `definites` through a widened `phraseOk`. There is no `Scope.names`, and `encodeScope` is unchanged. `encodeScope_no_names` and `names_irrelevant` are dropped | D3, D8, 2 CI-4, 7 (pieces 2 and 4), R 2.6, 6 and 8 |
| A6, purpose splits | `purposeSplit` takes the environment and lists every split. The answer is `many` when the unsplit wording and a split both read. `readPurposive`'s `Option` goes | 2 CI-7 |
| The proof task | CI-2 ports "Prove that ... using these premises." into `VE.Commands` | D2, 2 CI-2, 10 |
| D9, relay binding | CI-2 adds `english.command` rows to RD-9's relay-binding inventory and states no binding contract of its own | 2 CI-2, 9, 10 |
| CI-5, the gate | CI-5 edits AR-10's rows in `Compose/Dispatch.lean`, revises `gate_acts` with act-phrases' agreement and the decoder compatibility proof, then regenerates the JSON. No `allowlists` | 2 CI-5, 5, 11 |
| C1, source words | CI-6's cues are `SourceWordRow`s in `lean/VE/EnglishGrammar/SourceWords.lean`, written once en-sw lands | 2 CI-6, 4, 7 (piece 9) |
| D11, reading sets | Piece 10 uses W2 reading sets and does not build them | D5, 7 (piece 10) |
| (i), the import cycle | `typographic` lives in `SpeechActs/Wire.lean`, beside `asciiWording` | D9, 2 CI-4, 7 (piece 3) |
| (ii), `filled` | `filled` is defined through `fillHoles`. Piece 1 is marked NEW, closest to `fillHoles`, and is no longer offered to E3 | 2 CI-1, 7 (piece 1), R 7 and 8 |
| (iii), `surfaceKind` | The A/B lists every signed-choice row that the new `if `/`then ` cases flip in `choiceKindConflicts` | 2 CI-3, 9 |
| (iv), `environment.json` | Generated from Lean through `regen_generated`, not a hand copy with an equality test | 2 CI-8, 5 |
| NEW adapters | Every genuinely new adapter is marked NEW, with its closest existing abstraction | 7 |
| Batch order | CI-0, then CI-1. CI-2 after q1-4b. CI-3, then CI-4. CI-5 after CI-2, ap-1bd and the gate-contract revision. CI-E1 to CI-E3 and CI-8 after CI-2. CI-6 after CI-3, CI-E1 and en-sw. CI-7 after CI-4, CI-6 and purpose-explanation's usable interface | 1, 5 |
| Review | The converged statement review is FIX. Its corrections are applied before CI-1 starts; the affected statements and constructed fixtures are checked again by their batches | 2 CI-0; spec sections 6–12 |

Sections 9 to 11 come from the revision brief, not from the debate. Section 9 records each delta under the DRI ruling
that covers it (DRI-RULINGS.md and the 2026-10-28 decisions), section 10 records the index findings, and section 11
lists the cross-plan issues, each now decided by the DRI (2026-10-28, `reviews/dri-decisions-20261028-commands-imperatives.md`;
written in after draft 2, with D6, CI-2's legend and CI-4's purpose-clause row aligned to items 4(c) and 4(e)). Two remarks are not applied, because neither is a plan change of the joint
position. Fable's round-1 remark that spans be counted in code points is not in either round-2 position (it is applied since
synthesis round 2, N7: CI-2 and section 12). Fable's "no
extra plan round" is about the debate process, so it is the DRI's call.

## 0. Decisions

- **D1. The meaning does not change.** Every wording this plan adds elaborates into `VE.SpeechActs.Command` objects and
  their `demand`. No statement in `Tree.lean` or `Demand.lean` changes; the W1 policy, premises and identities stay as
  SA defines them.
- **D2. Lean owns the reading.** `VE.Commands.readCommand` enumerates every candidate reading of a command wording, and
  its theorems say the enumeration is complete and the answer unique. `VE.Commands.readInstruction` is the one public entry
  (renamed from `readUnit`, since the caller already defines `VE.SpeechActs.Source.readUnit`, `Source/Run.lean:62`;
  synthesis round 2, N7): the `english.command` mode and the source wrapper both call it, and each later batch extends it (A3). It also reads
  the proof task, "Prove that ... using these premises.". Python builds the request, relays Lean's answer, checks its
  schema and binding, and displays Lean's text. CI-2 deletes Python's command branch of `parse_speech`, the proof task
  included. Until CI-2 merges, CI-1's reader has no caller (as Q1.1 had none before Q1.4), so there is never a release
  with two owners.
- **D3. Every extension is conservative, with a theorem.** A wording that read with one reading before a batch reads
  with the same reading after it, under the hypotheses each batch states (CI-3 to CI-6). For CI-4 these are
  `phraseOk_mono` and `typographic_ascii_id`. The spelling fills have no such theorem, because draft 2 drops
  `names_irrelevant` (A5), so the CI-4 A/B lists every row they change.
- **D4. A sequence is two or more demands and a stated order.** At `@0` the order is not a rule, not a premise, and takes
  part in no check. The report says so in English. When events-time-causation lands, the order becomes a condition on
  `done` facts; that is not this plan's.
- **D5. A non-command never becomes a demand.** Suppositions, permissions, an imperative joined to a claim, remarks and
  imperative headings get `NotACommand: <form>`, with an English explanation. In translation, a sentence whose form the
  cue table does not settle is a W2 reading set over its forms (R 4). This plan builds no reading-set representation of
  its own (D11). List items governed by a lead-in wait. `scope@0` refuses `speech-acts@0` (C4), so no speech-acts
  document has a governed list, and CI-6 adds no `listItem` form until a scope x speech row exists.
- **D6. Purpose clauses wait for purpose-explanation.** Until CI-7 lands, a purpose clause on an instruction ("Open X
  to fix it.") is refused under `speech-acts@0`, never read as plain content (DRI 2026-10-28, item 4(c)). CI-7 is two
  batches (synthesis round 2, N7): CI-7a refuses a purpose clause whenever a split's command part reads; CI-7b waits
  for C21's named bridge, speech-acts' `documents@1` lift (after CI-2), and an executable purpose reader named by
  purpose-explanation's plan (PX3(a)). CI-7b then makes "Open X to fix it." a MIXED unit: the command part is read, and the purpose part goes to that reader. The command is
  not made conditional on the purpose by default.
- **D7. What counts as unlocked.** A web segment counts only when Lean reads it with one reading, and when its declared
  act phrase holds no numeral, quantity word, time word, attitude word, listed judgment word or purpose/goal
  infinitival complement (section 12, finding (b)). A declared gloss is an
  opaque atom (SA 2.1), so without this rule a fixture could hide a quantity or an open term inside an act and claim
  it. The rule is CI-8's, applied to the fixture vocabulary; it is not a product check.
- **D8. Labels and quoted wordings are constant spellings; `this` phrases are definites** (A5). A button label ("Check
  rule conflict") or a quoted wording (`"Rule 4."`) is the declared spelling of a constant. It comes from english-lean's
  constant display: `ConstDecl.display`, an overlay's `constants` or the lexicon's selected `spellings`, read through
  `Env.declaredSpelling` (`Lexicon.lean:399`). The reader's slot fills read `declaredSpelling`. A `this` phrase ("this
  unit") is task-local, so it is a definite of the speech scope, admitted by a widened `phraseOk`. `Scope` gains no
  field and `encodeScope` is unchanged, so every `environment_id` stays. If english-lean's spelling checks refuse
  capitals or quotes, the widening is english-lean's row, made with its owner (section 11).
- **D9. Typographic quotes and apostrophes** (U+2018, U+2019, U+201C, U+201D) are the only non-ASCII characters a speech
  wording may hold. One Lean function, `VE.SpeechActs.Wire.typographic`, beside `asciiWording` ((i)), maps them to
  ASCII before every other check. This changes a reviewed rule of SA 3.2. CI-0's statement review covers it, and,
  since it widens what is accepted, it is also a DRI decision (section 9). Every other non-ASCII character is still
  refused.
- **D10. The measured number** is the pinned web-copy fixture: the 59 imperative segments of R 2.1, copied with their
  source file and the catalogue blob `1ff7a7b72` into `usecases/webapp-commands/`. The live web page is refreshed only
  on the lead's request or at a milestone (CURRENT-STATE rule), so no batch edits branch `expand/webapp`.

## 1. Batches

| # | Batch | Hours | Owner | Needs | Web fixture: segments / bytes read with one reading (estimate) |
|---|---|---:|---|---|---|
| CI-0 | Statement spec `docs/spec/commands-imperatives.md`, stub, computed fixtures, statement review of draft 2's contracts | 3–4 | planner | — | 0 (not a build batch) |
| CI-1 | **Lean command reader** for the merged wordings, with structured guard outcomes; the web fixture as `#guard`s | 5–6 | Lean | CI-0 | **+9 / +273 B** (from 0) |
| CI-2 | `english.command` mode and `readInstruction`, called by the mode and the source wrapper; the proof task ported (query records, `QueryMismatch`); relay-binding inventory rows; Python's command branch, proof task and `legend` deleted | 5–6 | Lean, Python | CI-1; q1-4b merged | 0 (one owner) |
| CI-3 | `Then <command>.`, `<command>, then <command>.`, `If <condition>, <command>.`, through `readInstruction` | 4–6 | Lean | CI-2 | +2 / +46 B |
| CI-4 | Labels and quoted wordings as constant spellings, `this` phrases, typographic quotes, through `readInstruction` | 5–6 | Lean, Python (the ASCII mirror's deletion) | CI-3 | 0 ("Enter a reason to keep this unit unresolved." is a GAP, section 12 finding (b)); the command part of 1 MIXED unit (of the other two, one needs a three-place act, S18, and one holds a purpose clause, D6) |
| CI-5 | `speech-acts@0` with `acts@0` (simple acts only); AR-10's rows and `gate_acts` revised | 5–6 | Lean | CI-2; ap-1bd merged; the gate-contract revision | +3 / +125 B |
| CI-6 | Imperative-shaped non-commands: the classifier, its cue rows in `SourceWords.lean`, texts; `listItem` deferred | 4–6 | Lean | CI-3; CI-E1; en-sw merged | 0 on the web fixture; constitution up to 744 B LABELLED if the pilot adopts it |
| CI-7a | Purpose clauses refused: every split read; `PurposeClause` when a split's command part reads, `limit` when an unfinished split could change that | 2–3 (*estimate*) | Lean | CI-4; CI-6 | 0 (refusals) |
| CI-7b | Purpose clauses through `VE.Purposes`: `many` or MIXED | 2–3 (*estimate*) | Lean | CI-7a; speech-acts' `documents@1` lift (C21), after CI-2; purpose-explanation's usable interface | 5 segments / 315 B to READINGS or MIXED |
| CI-8 | Measurement: the fixture harness, the generated `E_web` JSON, the tutorial census, the report | 3–4 | Python (files), one Lean print entry | CI-2; re-run after each later batch | measures the column |
| CI-E1 | Experiment: command or not | 3–4 | evaluation | CI-2 | gates CI-6 |
| CI-E2 | Experiment: choice commands ("Choose A or B.") | 3–4 | evaluation | CI-2 | +4 / +189 B if it passes and is built |
| CI-E3 | Experiment: commands whose object is a question | 3–4 | evaluation | CI-2 | up to +5 / +271 B if it passes and is built |

The first build batch, CI-1, is the smallest one that moves a measured number. A smaller change exists: declaring the
fixture's vocabulary and measuring with Python's `parse_speech`. It would move the same 9 segments, but Python would be
deciding the meaning, which the lead directive forbids. So the smallest legitimate batch is the Lean reader with the
fixture.

**Totals (estimates).** CI-1 to CI-5 read 14 of the 59 segments (444 B, about 17% of the imperative bytes and 1.7% of
the brief's 25,963 B of sentence bytes; the purpose/goal complement of finding (b), section 12, is a GAP). The three
experiments could add up to 9 segments (460 B). The other 36 segments (1,659 B) wait on quantities, time, attitudes
and anaphora, purposes, or examples (R 2.1). Builder hours: about
35 to 45 for CI-1 to CI-8, plus 3 to 4 planner hours for CI-0 and 9 to 12 for the experiments.

**What every batch carries** (as question-answering-PLAN 7): 2 to 6 hours for one builder; the lean-first gate of
LEAN-FIRST-PLAN 5.1 (the full suite in chunks, the corpus A/B with every change in `DELTA.md` by class, the deletion
ledger, the relay lint); `python3 lean/audit.py`; the generated inventories through `tools/regen_generated.py --write`,
never by hand; `tools/gate_collection.py --write`; every new module mapped in `tools/layer_policy.py`; the
relay-binding inventory rows of every new response field (D9); each delta recorded under the DRI ruling that covers it
(section 9); seeded bugs in each changed language, each with the test it fails; no literal sleeps or short timeouts;
hermetic tests under `tmp_path`; the full gate once, on the final HEAD.

## 2. The batches

### CI-0. Statement spec and review (planner, 3–4 h)

- **Writes** `docs/spec/commands-imperatives.md`: the definitions and theorem statements of CI-1 to CI-7 (from section 2
  of this plan), the English with one reading each, the diagnostics in order with their exact texts, the fixtures with
  computed expectations, limits, and the review checklist. It also writes `lean/SpecStubs_commands-imperatives.lean`,
  untracked, with every definition and `def … : Prop` statement, elaborated with `lake env lean` against a build of
  `main`. It re-estimates the hours of CI-2, CI-3, CI-6 and CI-7, which draft 2 widened.
- **Computes in the stub:**
  - every CI-1 fixture outcome over `E_web` (CI-1, fixtures);
  - the number of fill candidates for the fixture and for the speech-acts conformance corpus, which sets
    `maxCandidates`;
  - whether `VE.Norms.Wire`'s act linter refuses `then`, which decides the hypothesis of `readStep_conservative` (CI-3);
  - whether a condition may use the scope's definite phrases ("..., if the reading is approved."). Python's `_formula`
    reads a condition with P0's English over the environment. If the lexicon holds no definite phrase, the spec says so
    and the fixtures name constants (W8);
  - a condition with two derivations over `E_web`'s lexicon for W17, or the fact that none exists, in which case W17
    uses a constructed lexicon (A1);
  - the signed-choice rows of the speech-acts corpus that the new `surfaceKind` cases flip (CI-3, (iii));
  - whether english-lean's spelling checks accept a capitalised label and a quoted wording (CI-4, A5);
  - the speech-acts corpus rows that the spelling fills change (CI-4, D3);
  - which theorems of `Compose/Dispatch.lean` that unfold `actsRefuses` CI-5 re-proves (their statements are unchanged,
    except `gate_acts`);
  - if en-sw has merged, CI-6's cue rows against its `SourceWordRow` type.
- **Review:** Astra and Fable, one bounded round on draft 2's revised contracts before CI-1 starts: D9 (the typographic
  exception to SA 3.2), D4 (the stated order as no rule), the shapes of `Outcome`, `GuardFault`, `StepOutcome` and
  `Alt`, `readInstruction`'s `Context`, and the conservativeness hypotheses of CI-3 to CI-6. The review converged on FIX:
  apply the accepted corrections to both documents before CI-1 starts. The CI-2 to CI-7 batches re-elaborate revised
  statements and execute the new counterexample fixtures; type-checking a `Prop` alone is not a proof.
- **Done when** the spec is committed, the stub elaborates with no `sorry` in a definition, and the review has
  converged.

### CI-1. The Lean command reader (Lean, 5–6 h)

**Files (new):** `lean/VE/Commands/Read.lean`, `lean/VE/Commands/Texts.lean`, `lean/VE/Commands/Examples.lean`.
**Shared files touched:** `lean/VE.lean` and `lean/VE/Audit.lean` (one import line each), `tools/layer_policy.py` (the
prefix `VE.Commands.` beside `VE.Question.` on the line that maps English modules; `VE.Commands.Examples` in the
examples list), the frozen inventory and theorem lists through their generators, and `lean/VE/SpeechActs/Wire.lean`
(`readingsBound`, the name of the existing `64` at `:761`; nothing else). Nothing else in `lean/VE/SpeechActs/`, and
nothing in `lean/VE/EnglishGrammar/` or `ve/`, changes.

**Statements** (namespace `VE.Commands`; imports `VE.SpeechActs.Wire` and `VE.EnglishGrammar.Run`; the full
executable definitions are in the item-1 spec, section 1):

```lean
open VE.SpeechActs (Scope Force)
open VE.SpeechActs.Wire (SpeechEnvironment actVerb asciiWording decodeClosedField asciiSpace)
open VE.EnglishGrammar (Env Lexicon TranslateOutcome translateRequest fillHoles)

/-- Provisional limits; CI-0 measures both on the fixtures and the speech-acts corpus. `maxCandidates` is also the
cap of the condition reader's enumeration (`guardOf`). -/
def maxWordingBytes : Nat := 400
def maxCandidates : Nat := 4096
-- `readingsBound` is the speech wire's bound (`Wire.lean:761`): CI-1 names that existing literal in `Wire.lean`, adding no new one (N7).
-- `many` holds at most `readingsBound` readings; more yields `limit`. `maxCandidates` stays the search cap.

/-- What fills one act slot after slot 0: a declared constant and the words that named it, its own name or a
definite phrase the scope binds to it (SA 1.1). CI-4 adds its declared spelling. -/
structure Fill where
  const : String
  words : String
  deriving DecidableEq, Repr

/-- One reading of a command wording (SA 2.1). -/
structure Reading where
  force : Force
  act   : String          -- the realising regulated predicate
  fills : List Fill       -- one per slot after slot 0, in slot order
  guard : VE.Formula      -- `.top` when the wording has no `, if`
  deriving DecidableEq, Repr

/-- The command object of SA 3.2 that a reading denotes. -/
def Reading.command (u : String) (r : Reading) : VE.SpeechActs.Command :=
  { unit := u, force := r.force, act := r.act, args := r.fills.map (·.const), guard := r.guard }

/-- A wording split as SA 2.1 writes it: `Do not ` gives forbid, nothing gives require; the body; the condition after
the last `, if `. `none` unless the wording ends with one `.`. -/
structure Parts where
  force : Force
  body : String
  condition : Option String
  deriving DecidableEq, Repr

def trimmed (s : String) : String  -- remove leading/trailing ASCII whitespace only
def fold (s : String) : String     -- fold `A`–`Z` only
def parts (s : String) : Option Parts

/-- The role that realises a force (SA 1.2): a prohibition is never `¬required`. -/
def roleOf : Force → VE.Norms.Role
  | .require => .obligation
  | .forbid => .permission

/-- The fills of a slot of sort `srt`: each constant of `srt` by its name, each definite phrase bound to one. CI-4
adds each constant's `E.declaredSpelling {}`. -/
def slotFills (se : SpeechEnvironment) (sc : Scope) (srt : String) : List Fill

/-- The act phrase after `{0} ` with each hole `{i}` filled by `(fs[i-1]).words`, through english-lean's `fillHoles`
((ii); `Lexicon.lean:222`), without collapsing whitespace; `none` unless the holes are exactly the slots `1` to
`fs.length`. -/
def filled (act : String) (fs : List Fill) : Option String :=
  let (hs, t) := fillHoles (act.drop 4) fun k => ((fs[k - 1]?).map (·.words)).getD ""
  if hs.all (fun k => decide (1 ≤ k ∧ k ≤ fs.length)) &&
      (List.range fs.length).all (fun i => hs.contains (i + 1)) then
    some t
  else none

/-- Why a condition gave no single guard (A1). -/
inductive GuardFault
  | ambiguous (gs : List VE.Formula)     -- two or more guards; every one becomes a reading
  | limit                                -- the enumeration stopped at its budget or its cap
  | unread (code text : String)          -- the reader's own refusal, with its code and English text
  deriving Repr

/-- A condition's guard (A1). The one sentence `c ++ "."` is read with every derivation by english-lean's
`translateRequest` (cap `maxCandidates`), and each reading is decoded closed over the environment (`decodeClosedField`):
- exactly one guard after `eraseDups`: `.ok`;
- two or more: `.error (.ambiguous gs)`, every guard kept;
- `.budget`, or `.readings _ false` (the cap was reached): `.error .limit`;
- any other outcome, no reading, or a decoding error: `.error (.unread code text)`, with the code and text that
  `english.read` reports for that sentence (english-lean's texts; this plan writes none). -/
def guardOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) :
    Except GuardFault VE.Formula

/-- Every guard a condition can have: its one guard, or each of an ambiguous condition's; none on a fault. -/
def guardsOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) :
    List VE.Formula :=
  match guardOf se E L b c with
  | .ok g => [g]
  | .error (.ambiguous gs) => gs
  | .error _ => []

/-- Every act match of the force's role with a verb, including a mismatched slot-0 sort; the shared addressee
check runs only after a unique reading. Matching trims ASCII edge whitespace and folds `A`–`Z` only. -/
def actMatches (se : SpeechEnvironment) (sc : Scope) (s : String) :
    List (String × List Fill)

/-- Every reading: each act match with each guard of the condition (`guardsOf`), or with `.top` when there is no
condition. -/
def candidates (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) : List Reading

def withinLimits (se : SpeechEnvironment) (sc : Scope) (s : String) : Bool

inductive Outcome
  | one (r : Reading)
  | many (rs : List Reading)       -- a W2 reading set in translation; authoring text depends on the cause
  | refused (code text : String)   -- a command code or english-lean's condition code, with its text
  | limit                          -- "VE stopped reading this command at its work limit."
  deriving Repr

def readCommand (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) : Outcome

def checkedAddressee (se : SpeechEnvironment) (sc : Scope) (r : Reading) : Outcome
```

```lean
variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

theorem readCommand_one_iff (r : Reading) :
    readCommand se sc E L b s = .one r ↔
      withinLimits se sc s = true ∧ (candidates se sc E L b s).eraseDups = [r] ∧ addressed se sc r = true

theorem readCommand_many (rs : List Reading) :
    readCommand se sc E L b s = .many rs ↔
      withinLimits se sc s = true ∧ rs = (candidates se sc E L b s).eraseDups ∧ 2 ≤ rs.length ∧
        rs.length ≤ VE.SpeechActs.Wire.readingsBound

/-- Completeness: a wording with an addressed candidate is never refused. -/
theorem readCommand_complete (r : Reading) (hl : withinLimits se sc s = true)
    (hr : r ∈ candidates se sc E L b s) (ha : addressed se sc r = true)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    readCommand se sc E L b s = .one r ∨ ∃ rs, readCommand se sc E L b s = .many rs ∧ r ∈ rs

/-- Every candidate is the wording: its act with its fills is the body, under the one normalisation. -/
theorem candidate_reads_back (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∃ p g a t, parts s = some p ∧ p.force = r.force ∧ g ∈ se.ne.regulated ∧ g.name = r.act ∧
      g.role = roleOf r.force ∧ g.act = some a ∧ (actVerb a).isSome ∧ filled a r.fills = some t ∧
      fold t = fold p.body

theorem candidate_guard (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    match (parts s).bind (·.condition) with
    | none => r.guard = .top
    | some c => r.guard ∈ guardsOf se E L b c

/-- An ambiguous condition is never a silent choice: every guard is a reading (A1). -/
theorem guard_ambiguous (c : String) (gs : List VE.Formula) (m : String × List Fill)
    (hl : withinLimits se sc s = true) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error (.ambiguous gs)) (hm : m ∈ actMatches se sc s)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    ∃ rs, readCommand se sc E L b s = .many rs ∧ ∀ g ∈ gs, ∃ r ∈ rs, r.guard = g

/-- Exhaustion is `limit`, never a refusal and never "no reading" (A1; verdicts are three-valued). -/
theorem guard_limit (c : String) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error .limit) (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .limit

/-- An unread condition refuses with the reader's code and text (A1). -/
theorem guard_unread (c code text : String) (hl : withinLimits se sc s = true)
    (hc : (parts s).bind (·.condition) = some c) (hg : guardOf se E L b c = .error (.unread code text))
    (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .refused code text

/-- A fill is a constant's own name or a phrase the scope binds to it (CI-4 adds the spelling). -/
theorem candidate_fills (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∀ f ∈ r.fills, f.words = f.const ∨ (f.words, f.const) ∈ sc.definites

/-- A read command passes the semantic core's own check in every speech document over the same decoded environment
with a valid scope (A1: an arbitrary `se` and `sc` do not give `commandOk`'s typing). -/
theorem readCommand_typed (j : Lean.Json) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r)
    (hE : D.E = se.ne.rv.environment) (hS : D.scope = sc) (hR : D.regulated = se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true

/-- Local command codes take precedence; otherwise use english-lean's diagnostic class table. -/
def Texts.classOf (code : String) : Option String :=
  (Texts.codeClasses.lookup code).orElse fun _ => VE.EnglishGrammar.Run.codeClasses.lookup code

theorem refused_classed (code text : String) (h : readCommand se sc E L b s = .refused code text) :
    (Texts.classOf code).isSome = true
```

The joint position offered two repairs for `readCommand_typed`: hypotheses, or a `commandOk` filter on the candidates.
Draft 2 takes the hypotheses. A filter would report a typing fault as "no reading", and `readCommand_complete` would
need a weaker statement.

**Diagnostics, in Python's order, with Python's texts** (so the CI-2 A/B is byte-identical): a non-ASCII wording,
`InvalidInput: non-ASCII speech wording`; `You may …`, `PermissionNotCommand: use an equality-guarded W1 rule`; `Please
…`, `InvalidInput: please needs author approval`; no addressee, `UnboundSlot: you`; a match whose act has the other role
only, `MissingObligationRole: <act>` or `MissingPermissionRole: <act>`; an unread condition, the reader's code and text
(A1); an exhausted condition reading, `limit` ("VE stopped reading this command at its work limit."); an ambiguous
condition, `many` with one reading per guard, shown in authoring with english-lean's `Ambiguous` condition text when
all readings share `(act, fills)` and differ in guard; two or more
distinct act matches, `AmbiguousDerivation: multiple declared acts match`; none, with ` and ` in the body, `CoordinatedActs: split into two
commands`; otherwise `InvalidInput: no single speech-act reading`.

**Fixtures** (`Examples.lean`, `#guard`s over `E_web`: sorts `user`, `control`, `ledger`, `text`, `reading`,
`token`; the addressee `(user, Reader)`; the task `webapp-copy`; the constant `draft` of sort `reading`; definites "the
document assistant control", "the private server calls ledger", "the question", "the meaning", "the token"; acts
`{0} click Check rule conflict`, `{0} click Review meaning`, `{0} click Ask`, `{0} choose a listed rule vocabulary`,
`{0} choose a unit revision to restore`, `{0} use {1}`, `{0} check {1}`, `{0} write {1} as a statement`, `{0} share {1}`
(permission), `{0} review {1}` and `{0} review the meaning`; the predicate `{0} is approved` on `reading`). Rows:

| Row | Wording (source) | Expected |
|---|---|---|
| W1 | "Click Check rule conflict." (tour.js) | `one`, require, no fills, `.top` |
| W2 | "Click Review meaning." (tour.js, twice) | `one` |
| W3 | "Choose a listed rule vocabulary." (app.js, twice) | `one` |
| W4 | "Choose a unit revision to restore." (app.js) | `one` |
| W5 | "Use the document assistant control." (app.js) | `one`, fill (DocumentAssistant, "the document assistant control") |
| W6 | "Check the private server calls ledger." (app.js) | `one` |
| W7 | "Write the question as a statement." (index.html) | `one` |
| W8 | "Click Check rule conflict, if draft is approved." | `one`, guard `approved(draft)` |
| W9 | "Do not share the token." (SA's fixture) | `one`, forbid on the permission predicate |
| W10 | "Review the meaning." | `many`, two readings (the unary act, and `{0} review {1}` with "the meaning") |
| W11 | "Click Use this wording under the one you mean." (tour.js) | `refused`, `InvalidInput: no single speech-act reading` |
| W12 | "Choose authoring or translation mode." (app.js) | `refused`, the same (SA 2.3's ruling) |
| W13 | "Open “Vocabulary & small world” to fix it." (app.js) | `refused`, `InvalidInput: non-ASCII speech wording` |
| W14 | "Then click Ask." (tour.js) | `refused` (CI-3 reads it) |
| W15 | "You may close the desk." | `refused`, `PermissionNotCommand: …` |
| W16 | every command row of SA section 9 | as SA computes |
| W17 | "Click Check rule conflict, if <a condition with two derivations>." (CI-0 picks it) | `many`, one reading per guard (A1) |
| W18 | W8 with budget 0 | `limit` (A1) |
| W19 | "Click Check rule conflict, if draft is approvable." | `refused`, with english-lean's code and text for the condition (A1) |

The pinned 59 segments of R 2.1 are also `#guard`s with their expected outcome; the measured number is the count of
`one` rows. Expected (estimate): the 9 segments of W1 to W7 (273 B).

**Deleted, not duplicated:** nothing yet. The reader has no caller until CI-2, and CI-2 deletes the Python branch.
**Seeded bugs:** `roleOf .forbid = .obligation` (fails W9 and `candidate_reads_back`'s use in `readCommand_typed`);
`candidates` keeping only the first fill tuple (fails W10); dropping the guard (fails W8); `guardOf` keeping only the
first guard (fails W17); `limit` mapped to a refusal (fails W18).
**Done when:** the statements are proved, the `#guard`s pass, the audit is clean, and the A/B shows no change, since no
mode changes.
**Conflicts:** gi-1 (next ready) edits `lean/VE.lean`; whichever lands second rebases its one import line. No in-flight
branch touches `lean/VE/Commands/`.

### CI-2. One owner: the mode, the one entry, the proof task and the deletions (Lean and Python, 5–6 h)

**Lean files:** `lean/VE/Commands/Run.lean` (new): `Context`, `proofTask`, `readInstruction`, and the `english.command` case,
whose request is the `english.read` request plus the speech environment JSON, the wording and the request's decoded
query records (id, target), with Lean's code, text and span on refusal. Also new or touched: the `lean/VE/Service/Protocol.lean` entry;
`runMode_englishCommand : runMode .englishCommand j = VE.Commands.Run.caseReported j := rfl`; the response shape under
`lean/ResponseShape/Schemas/` and its encoder theorem under `lean/ResponseShape/Encoders/`; a branch of `runMode_fits`;
and `Texts.lean`, which gains the proof task's act wording `{0} submit a proof of {1}` (today `PROOF_TASK_ACT`,
`ve/speech_acts.py:15`). `commandFence_needs_context` is stated and proved in `lean/VE/SpeechActs/Source/Run.lean`,
beside `decodeSpeechSource`, which it is about, not in `VE.Commands` (N7). `Texts.lean` gains no legend: the scope legend is speech-acts' `VE.SpeechActs.Run.legend`
(`SpeechActs/Run.lean:64`), the one legend (DRI 2026-10-28, item 4(e)), and the answer carries its lines. In `lean/VE/SpeechActs/Source/Run.lean`, every command fence (a fence of an
`instruction` unit) is read by `VE.Commands.readInstruction`. The encoder receives the decoded request id, unit and context,
so the response can echo the id, name the command unit and render the scope's legend. That is a different definition from the wrapper's own
structural `VE.SpeechActs.Source.readUnit` (`Source/Run.lean:62`), which splits a unit's bytes. A payload that has a
command fence and no reading context is `InvalidInput: command reading context` (A2). A supplied `resolved_fences`
command that differs from Lean's reading is `InvalidInput: resolved speech fences`.

**Python files:** `ve/backends/english_lean.py` gains `read_command`. It builds the request from the same lexicon
producer as `read_question`, sends the request's query records (id, target) and no proof-task selection (Lean
derives the match, N7), raises Lean's code and text verbatim, and is in the relay
lint. `ve/speech_document.py` resolves command fences through it and always sends the reading context. The manifest
operation is `command.read`, `authority: lean-only`; `tools/relay_lint.py` lists the path;
`tests/test_relay_binding_inventory.py` gains the `english.command` rows (D9). **Deleted:** in `ve/speech_english.py`,
`_command_candidates` and the command branch of `parse_speech` (the `You may`, `Please`, coordination, proof-task and
`text.endswith(".")` blocks), and the scope sentences of `legend`, which Python displays from the relayed lines of
`VE.SpeechActs.Run.legend` (its W1 default sentences stay norms' `default_sentence`). Also deleted: `PROOF_TASK_ACT`, whose only product callers are in the deleted branch, so the wording has one owner,
in Lean (`tests/frozen_speech/speech_acts.py` keeps its own frozen copy, which is test data). The deletion ledger lists what stays and why: `_sentence` stays for assertions and `follows`, and `_copular` for
which-questions and `follows`, which are question-answering's Q3 (question-answering-PLAN.md:718, 964); `act_verb`
stays only while a listed caller remains.

**Statements:**

```lean
-- CI-1's `variable` line is in scope.

/-- A decoded query record of the request (N7): its id and its target formula. -/
structure QueryRecord where
  id : String
  target : VE.Formula

/-- The reading context of one command fence (A2). Every field is required: a request or a payload without it is
`InvalidInput: command reading context`. -/
structure Context where
  se : SpeechEnvironment
  sc : Scope
  E : Env
  L : Lexicon
  b : Nat
  queries : List QueryRecord   -- the request's decoded query records (id, target): the proof task's target context

/-- The proof task (SA 2.1), ported from `parse_speech` (`ve/speech_english.py:212-222`) in its order: `Prove that
<P> using these premises.`, with `P` read through `guardOf` (N7): ambiguous gives `many`, the budget gives `limit`,
unread gives the reader's refusal. One reading must equal exactly one record's target, otherwise
`QueryMismatch: <u>`. `MissingObligationRole: {0} submit a proof of {1}` unless exactly one obligation predicate has
that act on `(addressee sort, query)`; otherwise the reading passes through `checkedAddressee`, with the matched
record's id as its only fill and `.top` as its guard. Premise ids stay with `decodeDocument`, and the `follows` loop
stays question-answering's. `none` when the wording is not a proof task. -/
def proofTask (ctx : Context) (s : String) : Option Outcome

/-- The one public entry (A3): the `english.command` mode and the source wrapper both call it. CI-3, CI-6 and CI-7
extend it, each with its response shape, encoder theorem and inventory rows. -/
def readInstruction (ctx : Context) (s : String) : Outcome :=
  (proofTask ctx s).getD (readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s)

theorem readInstruction_command (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readCommand ctx.se ctx.sc ctx.E ctx.L ctx.b s

/-- The proof task names the one query record whose target is P's reading (N7). -/
theorem proofTask_bound (ctx : Context) (s p : String) (r : Reading) (hp : proofSentence s = some p)
    (h : proofTask ctx s = some (.one r)) :
    ∃ φ q, guardOf ctx.se ctx.E ctx.L ctx.b p = .ok φ ∧ ctx.queries.filter (·.target == φ) = [q] ∧
      r.fills.map (·.const) = [q.id]

theorem proofTask_addressed (ctx : Context) (s : String) (r : Reading)
    (h : proofTask ctx s = some (.one r)) : addressed ctx.se ctx.sc r = true

/-- The request: the `english.read` request's environment, overlay, lexicon and budget, the speech environment and
scope, the request's decoded query records, and the wording. -/
structure Request where
  id : String
  unit : String
  ctx : Context
  s : String

def Run.decodeRequest (j : Lean.Json) : Except String Request

/-- The answer: the wording and `readInstruction`'s outcome. For `one`: the reading's command object (SA 3.2), each fill's
words with its span in code points of the wording (N7), and speech-acts' paraphrase and legend using the decoded context. For `many`:
every reading. The request id and command unit are echoed from `q`. -/
def Run.encode (q : Request) (o : Outcome) : Lean.Json

theorem runMode_englishCommand (j : Lean.Json) : runMode .englishCommand j = VE.Commands.Run.caseReported j := rfl

/-- The encoder theorem: the answer encodes exactly `readInstruction`'s outcome for the request's context and wording. -/
theorem caseReported_eq (j : Lean.Json) (q : Request) (hd : Run.decodeRequest j = .ok q) :
    Run.caseReported j = Run.encode q (readInstruction q.ctx q.s)

theorem readInstruction_refused_classed (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true

/-- The typing theorem covers the whole entry, the proof task included (N7): `readCommand_typed` for every reading
`readInstruction` returns. -/
theorem readInstruction_typed (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : readInstruction ctx s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true

-- In `lean/VE/SpeechActs/Source/Run.lean` (N7), not in `VE.Commands`.
/-- A2: a command fence is never taken from the payload: one without the reading context is refused. -/
theorem commandFence_needs_context (payload evidence : Lean.Json) (h : hasCommandFence payload = true)
    (hc : (payload.getObjVal? "reading_context").toOption = none) :
    ∃ e, VE.SpeechActs.Source.decodeSpeechSource payload evidence = .error e
```

**Fixtures:** CI-1's rows through the mode and through `ve speech` on fixture documents (exit codes 0 and 2). The proof
task: "Prove that draft is approved using these premises." with exactly one query record whose target is
`approved(draft)` reads `one` on the proof predicate; with no such record, or two, it is `QueryMismatch: <u>`; an
existing query with the wrong target is `QueryMismatch: <u>` (N7); with two proof predicates it is
`MissingObligationRole: {0} submit a proof of {1}`. A payload with a command fence and no reading context is `InvalidInput: command reading context`. Every
speech-acts test and conformance case with a command is byte-identical, or listed in `DELTA.md` under the ruling that
covers it, or as needing the DRI (section 9).
Add P7: a matching proof task with no addressee returns `UnboundSlot: you`. Send the same wording and reading under
two requests with different ids, units and scopes; encoded answers echo their own ids and units and carry different
scope legends. The `caseReported_eq` test compares each answer to `Run.encode q (readInstruction q.ctx q.s)`.
**Relay binding (D9).** CI-2 adds the `english.command` rows to `tests/test_relay_binding_inventory.py`. They classify
every field of the generated response schema as BOUND (the id, unit, wording, each fill's words and constant, the act, the span,
the query) or LEAN (the guard, the paraphrase). The inventory's fuzz retypes and rebinds each bound field, and its
replayed-answer test (`test_another_requests_genuine_answer_is_unavailable`) covers the mode; an answer naming a
constant or a query not in the request is `CheckerUnavailable`. CI-2 states no binding contract of its own.
**Seeded bugs:** Lean, `caseReported` answering from a cached wording (fails the inventory's replayed-answer test);
Lean, `proofTask` ignoring the records' targets (fails the wrong-target fixture); Lean, `proofTask` skipping the shared
addressee check (fails P7); Python, `read_command` accepting a fill
the request does not hold (fails the rebinding fuzz).
**Done when:** the gate passes, the DRI has signed the deletion ledger (section 9: moving an authority), the relay
lint passes on the command path, and `tools/repo_map.py --check` lists the new mode with its schema.
**Conflicts:** q1-4b edits `ve/speech_english.py` and `ve/backends/english_lean.py`. CI-2 starts after q1-4b merges and
rebases on it; it edits no line q1-4b owns (`_polar`, `_copular`'s polar use).

### CI-3. Steps and conditions written first (Lean, 4–6 h)

**Files:** `lean/VE/Commands/Steps.lean` (new), `Run.lean` (`readInstruction` calls `readStep`), `Examples.lean`.
**Shared:** `lean/VE/SpeechActs/Wire.lean`, `surfaceKind` only: a wording that starts `if ` and whose clause after the
first comma starts with an act verb, or that starts `then ` and continues with one, is `instruction`.
`lean/VE/SpeechActs/Source/Run.lean`: the stated order is derived content of the decoded source (`OrderMismatch` when a
stated order disagrees). The `english.command` response shape, its encoder theorem and its rows in
`tests/test_relay_binding_inventory.py`, extended for `steps` and `many` (A3).

**The document form of a sequence** reuses W2's MIXED parts and adds no content kind: "Click Check rule conflict, then
click Ask." is one `instruction` unit whose parts are its steps (spans split before `, then `). Each part carries an
ordinary command object, and Lean checks the parts against `readStep` of the whole wording.

**`surfaceKind` and signed choices ((iii)).** The new `if ` and `then ` cases can flip `choiceKindConflicts`
(`Wire.lean:657`) for a signed choice. A unit whose wording starts `If …, <verb>` or `Then <verb>` was `asserted` and
becomes `instruction`. A signed `asserted` choice of it, accepted before, is then `InvalidInput: choice kind`, and a
signed `instruction` choice that conflicted before no longer does. CI-0's stub lists these rows on the speech-acts
corpus, and the CI-3 A/B lists every signed-choice row that flips. Each flip is a verdict change, so it needs the DRI
(section 9).

```lean
-- CI-1's `variable` line is in scope.

/-- The step shapes (CI-3), beside the merged wordings. -/
inductive Shape
  | core (s : String)                      -- a merged wording
  | preposed (c x : String)                -- `If <c>, <x>.`
  | after (x : String)                     -- `Then <x>.`: a step after its named source antecedent (section 12, finding (c))
  | seq (xs : List String)                 -- `<x₁>, then <x₂>[, then <x₃> …].`, 2 to 8 steps, none conditioned
  deriving DecidableEq, Repr

/-- The first ASCII letter in upper case. -/
def capitalise (x : String) : String

/-- The wording holds the exact bytes `, then ` after trimming only ASCII edge whitespace. -/
def hasThen (s : String) : Bool := ((trimmed s).splitOn ", then ").length > 1

def shapes (s : String) : List Shape

/-- One competing reading of a unit, as `many` lists it (A3). CI-3 has `shape`; CI-6 adds `form` and CI-7 `purpose`,
each with its response shape, encoder theorem and inventory rows. -/
inductive Alt
  | shape (sh : Shape) (rs : List Reading)  -- a shape and its readings: one per step, one for the other shapes
  deriving Repr

inductive StepOutcome
  | one (r : Reading) (afterPrevious : Bool)
  | steps (rs : List Reading)
  | many (alts : List Alt)                 -- every competing reading (A3): a W2 reading set in translation, a
                                           -- refusal with the rewrites in authoring
  | refused (code text : String)
  | limit

def readStep (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) :
    StepOutcome

/-- The individual shape retains one, many, refusal and limit; a sequence enumerates complete combinations. -/
def shapeOutcome (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) :
    Shape → StepOutcome

/-- Completed alternatives of a shape. -/
def shapeAlts (sh : Shape) (o : StepOutcome) : List Alt

/-- The shape has at least one completed reading. -/
def reads (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (sh : Shape) : Bool

/-- CI-2's entry, extended (A3): `readInstruction` returns `StepOutcome` (CI-2's `one r` is `one r false`, and its `many rs`
is one `Alt.shape (.core s) [r]` per reading); outside the proof task it is `readStep`. -/
-- This replaces `readInstruction_command` because `readInstruction` now returns `StepOutcome`.
theorem readInstruction_step (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readStep ctx.se ctx.sc ctx.E ctx.L ctx.b s

theorem readInstruction_refused_classed_step (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = StepOutcome.refused code text) : (Texts.classOf code).isSome = true

/-- Conservative: a merged wording keeps its reading. CI-0's stub decides whether W1's act linter, by refusing the
reserved word `then` in every act phrase, makes the hypothesis `hs` unnecessary. -/
theorem readStep_conservative (j : Lean.Json) (r : Reading)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r) (hs : hasThen s = false) :
    readStep se sc E L b s = .one r false

theorem preposed_eq (c x : String) (r : Reading) (h : shapes s = [.preposed c x]) :
    readStep se sc E L b s = .one r false ↔
      readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ ".") = .one r

theorem after_eq (x : String) (r : Reading) (h : shapes s = [.after x]) :
    readStep se sc E L b s = .one r true ↔ readCommand se sc E L b (capitalise x ++ ".") = .one r

theorem seq_eq (xs : List String) (rs : List Reading) (h : shapes s = [.seq xs]) :
    readStep se sc E L b s = .steps rs ↔ xs.length = rs.length ∧
      ∀ p ∈ xs.zip rs, readCommand se sc E L b (capitalise p.1 ++ ".") = .one p.2 ∧ p.2.guard = .top

/-- Two shapes that both read make the wording ambiguous, never a silent choice; the answer carries each (A3). -/
theorem shapes_ambiguous
    (h : 2 ≤ (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound) :
    ∃ alts, readStep se sc E L b s = .many alts ∧ 2 ≤ alts.length

theorem seq_ambiguous (xs : List String) (alts : List Alt) (hs : shapes s = [.seq xs])
    (hr : readStep se sc E L b s = .many alts) :
    ∀ a ∈ alts, ∃ rs, a = .shape (.seq xs) rs ∧ rs.length = xs.length

theorem shapes_limit (hs : 2 > (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hl : ∃ sh ∈ shapes s, shapeOutcome se sc E L b sh = .limit) :
    readStep se sc E L b s = .limit

theorem shapes_complete (alts : List Alt)
    (hl : ∀ sh ∈ shapes s, shapeOutcome se sc E L b sh ≠ .limit)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound)
    (hr : readStep se sc E L b s = .many alts) :
    ∀ sh ∈ shapes s, ∀ a ∈ shapeAlts sh (shapeOutcome se sc E L b sh), a ∈ alts

/-- A sequence contributes exactly its steps' demands, named `cmd-<u>.1` … `cmd-<u>.n`, and no other rule. -/
def stepCommands (u : String) (rs : List Reading) : List VE.SpeechActs.Command :=
  rs.mapIdx fun i r => r.command (u ++ "." ++ toString (i + 1))

theorem stepCommands_policy (D : VE.SpeechActs.SpeechDoc) (u : String) (rs : List Reading)
    (pre post : List VE.SpeechActs.Command) (h : D.commands = pre ++ stepCommands u rs ++ post) :
    (VE.SpeechActs.policy D).T.nodes =
      D.norms ++ (pre ++ stepCommands u rs ++ post).map (VE.SpeechActs.demand D)

/-- The stated order: consecutive steps of a sequence, and an `after` unit after its source antecedent, the earlier
translated instruction unit the writer names for it (section 12, finding (c)). It is no rule and no premise. -/
def stepOrder (units : List StepUnit) : List (String × String)

def firstStep (u : StepUnit) : String := if u.steps ≤ 1 then u.id else u.id ++ ".1"
-- An `after` pair is `(lastStep v, firstStep u)`, where `v` is the named source antecedent, never the nearest earlier
-- instruction by default: a `Then` unit whose source antecedent is not a translated unit of the document is
-- `ThenWithoutStep` in authoring and a GAP in translation.
theorem stepOrder_forward (us : List StepUnit) (p : String × String) (hn : (stepNames us).Nodup)
    (h : p ∈ stepOrder us) :
    ∃ i j : Nat, i < j ∧ (stepNames us)[i]? = some p.1 ∧ (stepNames us)[j]? = some p.2
```

**English and display.** "If draft is approved, click Ask." reads as "Click Ask, if draft is approved." Its guard is
`approved(draft)`; speech-acts' single-command paraphrase says "In this task, you are required to click Ask, where
the stated condition holds." A
sequence's paraphrase is "In this task, you are required to do these in order: first click Check rule conflict, then
click Ask. The order is stated; VE does not reason about it." A condition with a sequence ("If P, click A, then click
B.") is refused as `ConditionScope`, with the two rewrites offered in English: the condition on each step, or the
condition on the first only.

**Outcome combination.** `shapeOutcome` handles a single shape in both the one-shape and multiple-shape paths.
A sequence reads every step: its first refusal wins; otherwise any exhausted step yields `limit`; otherwise the
Cartesian product of the steps' readings yields complete alternatives, one reading per step. The product is capped at
`maxCandidates`. Across competing shapes, two or more completed alternatives yield `many`, even beside a limited
shape; with fewer than two, a limit yields `limit`. The cap yields `limit` when exceeded, and `many` holds at most
the speech wire's bound (`Wire.lean:761`) (`readingsBound`), else `limit`, with no new literal (N7). This `many` does not claim
that enumeration is exhaustive. Each reported sequence alternative still contains every step. The condition reader's
own exhaustion rule is unchanged (spec sections 7 and 12).

**Fixtures:** "Then click Ask." and "Then click Check rule conflict." (tour.js) read as `after` steps (+2 segments,
46 B); "Click Check rule conflict, then click Ask." gives two steps and one order pair; "If draft is approved, click
Ask." equals W8's shape; "Add an exception or precedence, then check for a conflict in plain English."
(index.html) splits, and its first step is refused, so the whole is refused in authoring (in translation it is the
MIXED unit of section 12, finding (d)); "Then click Ask." with no earlier instruction unit is `ThenWithoutStep`, and so
is a `Then` unit whose source antecedent is not a translated unit, even when an unrelated instruction unit precedes it
(uweb.tour.552_0, finding (c)); "If P, click A, then click B." is `ConditionScope`; every row on CI-0's list of
signed choices that `surfaceKind` flips gives its new outcome ((iii)); every CI-1 row is unchanged.
Add the counterexample `Review the meaning, then click Ask.`: its W10 first step is `many`, and both complete
alternatives end in `click_ask_required`. Constructed sibling outcomes `[one, limit]` yield `limit`; `[one, one,
limit]` yield `many` with both completed alternatives. The order counterexample has units `a` (one step) and `b`
(two steps, `after`, antecedent `a`): order pairs are `(a, b.1)` and `(b.1, b.2)`.
**Seeded bugs:** `stepOrder` reversed (fails `stepOrder_forward`'s fixture); `preposed` dropping the condition (fails
the equality fixture).
**Deleted, not duplicated:** nothing; every shape calls `readCommand`.
**Conflicts:** `Wire.lean` is speech-acts' file. Before starting, check `git diff main...<branch> --stat` of every
in-flight branch for `lean/VE/SpeechActs/`; none touched it at 2026-10-28 17:44Z (NOW.md).

### CI-4. Labels, quoted wordings, `this` phrases and typographic quotes (Lean, 5–6 h)

**Rendering owner.** `VE.SpeechActs.Run.nameOf`, `actRest` and `paraphrase` receive
`spell : String → Option String` from the decoded english-lean environment. A constant is rendered by the first
bound definite phrase, then its declared display, then its name. CI-3 adds
`VE.SpeechActs.Run.paraphraseSteps D spell cs` for the complete ordered command list. The scope legend remains
`VE.SpeechActs.Run.legend sc`. CI-3/CI-4 pin exact outputs for a declared label, a conditional command and a
complete two-step sequence (spec section 8). No second rendering table is introduced.

**Files:** `lean/VE/Commands/Read.lean` (`slotFills` reads `declaredSpelling`), `Examples.lean`. **Shared:**
`lean/VE/SpeechActs/Wire.lean` gains `typographic`, beside `asciiWording` ((i)). `VE.Commands` imports `Wire.lean`, so
`Wire.lean` could not call a definition in `VE.Commands`. In the same file, `phraseOk` also accepts `this <words>`, and
every caller of `asciiWording` applies `typographic` first: `decodeUnitIn` (`Wire.lean:680`) and the fence check
(`Source/Run.lean:686`). `Tree.lean` does not change: `Scope` gains no field, and `parseScope` and `encodeScope` keep
their keys and encoding, so every `environment_id` stays (A5). Python's request builder sends english-lean's overlay
and lexicon, as it does for `read_question`, and makes no check of its own.

**Labels, quoted wordings and `this` phrases (A5).** A label or a quoted wording is a constant's declared spelling in
english-lean's constant display: `ConstDecl.display`, an overlay's `constants`, or the lexicon's selected `spellings`,
read through `Env.declaredSpelling` (`Lexicon.lean:399`). The constant `CheckRuleConflict`, displayed "Check rule
conflict", fills the slot of `{0} click {1}`. `Rule4Wording`, displayed `"Rule 4."`, fills a slot with the quoted
wording. The spelling a fill reads is the lexicon's selected one, `L.spellings`, after `L.valid` is checked first (N7);
`declaredSpelling` does not replace the lexicon's selected spelling. A `this` phrase is task-local: `In this task,
this unit is Unit7.` binds it in `definites`. The legend shows
the definites as it does today, the inspector shows each constant with its spelling, and the default view shows the
paraphrase with the spelling as written ("you are required to click Check rule conflict"). If english-lean's spelling
checks refuse capitals or quotes, the widening is english-lean's row, made with its owner (section 11, issue 3). CI-0's
stub finds out which.

```lean
namespace VE.SpeechActs.Wire

/-- The one typographic normalisation ((i)): U+2018 and U+2019 to `'`, U+201C and U+201D to `"`; every other
character is kept, so `asciiWording` still refuses it. -/
def typographic (s : String) : String

theorem typographic_ascii_id (s : String) (h : asciiWording s = true) : typographic s = s

theorem typographic_only (s : String) :
    asciiWording (typographic s) = true ↔
      ∀ c ∈ s.toList, c.toNat < 128 ∨ c = '‘' ∨ c = '’' ∨ c = '“' ∨ c = '”'

/-- Old phrases stay valid: `phraseOk` is `phraseOk₀` (a definite phrase starting with `the`) or a `this` phrase. -/
theorem phraseOk_mono (p : String) (h : phraseOk₀ p = true) : phraseOk p = true

end VE.SpeechActs.Wire

namespace VE.Commands
-- CI-1's `variable` line is in scope.

/-- A fill is a constant's own name, its declared spelling (A5), or a phrase the scope binds to it. This restates
CI-1's `candidate_fills` with the spelling. -/
theorem candidate_fills (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∀ f ∈ r.fills, f.words = f.const ∨ E.declaredSpelling {} f.const = some f.words ∨
      (f.words, f.const) ∈ sc.definites
```

`phraseOk₀` is today's definition, kept under that name in `Wire.lean` with a comment, so `phraseOk_mono` compares
against the reviewed original. `scope_in_identity` and `canonical_scope` keep their statements, and CI-4 re-proves them
only if the change to `phraseOk` reaches their proofs. Draft 1's `nameOk`, `occursIn`, `encodeScope_no_names` and
`names_irrelevant` are gone (A5).

**Conservativeness (D3).** CI-4's theorems are `phraseOk_mono` and `typographic_ascii_id`. The spelling fills have
none: a spelling that an existing environment already declares can now fill a slot. So CI-0's stub computes the
speech-acts corpus rows this changes, and the CI-4 A/B lists every one.

**Fixtures:** "Enter a reason to keep this unit unresolved." (app.js) is not read as an opaque act with guard ⊤: its
purpose/goal complement makes it a GAP (section 12, finding (b); uweb.drafts.898_0), so it counts 0. "Click Check rule
conflict." reads with the label as the spelling of `CheckRuleConflict`, an object of `{0} click {1}`, and the unary act
of CI-1 is removed from `E_web` (the same segment, now a structured object). The command part of "Look at Nearest
declared wordings: “may read the handbook” is the closest one." reads inside a MIXED unit (the rest stays
UNFORMALISED). "Make rule 4 an exception to rule 1: change “Rule 4.” to “Rule 4 (exception to rule 1).”" is not a CI-4
row: its command needs the three-place act `{0} change {1} to {2}`, which `@0` refuses (item-1 spec, section 8, S18).
"Open “Vocabulary & small world” to fix it." stays refused: it holds a purpose clause, which waits for CI-7 (D6; DRI
2026-10-28, item 4(c)). "Is it the case that atlas is checKed?" with U+212A is still refused (SA's fixture). A
spelling that collides with another constant's name or spelling is refused by english-lean's lexicon check, with its
code.
**Seeded bugs:** `typographic` also mapping U+212A (fails the Kelvin fixture); `slotFills` ignoring `declaredSpelling`
(fails the label fixture).
**Deleted, not duplicated:** Python's mirror of the ASCII check on the speech path, if any caller of `ascii_wording`
remains after CI-2, moves to Lean's answer; the ledger names it.
**Conflicts:** `Wire.lean` and `Source/Run.lean` are shared speech-acts files; CI-4 runs after CI-3, never beside it.

### CI-5. `speech-acts@0` with `acts@0`, simple acts only (Lean, 5–6 h)

**Needs:** CI-2; ap-1bd merged (typing and the model path reading `acts@0`); act-phrases' D9 (words shared inside a
joined filler) decided; and the gate-contract revision. That revision is act-phrases' agreement to revise
act-phrases.md 4.4 and `gate_acts`, and the DRI's decision, since `gate_acts` is an approved theorem statement
(sections 9 and 11).

**Shared:**
- `lean/VE/Compose/Dispatch.lean`, AR-10's rows. `actsRefuses` (`Dispatch.lean:758`) no longer refuses
  `speech-acts@0`, and `gate_acts` (`:1165`) is revised. The theorems that unfold `actsRefuses` are re-proved with
  unchanged statements. The speech-acts row (`:767`, `refusing "speech-acts@0" speechOthers`) already admits `acts@0`.
  `speechAllow` and the legacy `today` gate do not change, because neither registers `acts@0`.
- `lean/VE/SpeechActs/Wire.lean`: `allowlist` gains `acts@0`, so `profileGate` admits it, and `today_speech`
  (`Dispatch.lean:481`) is re-checked.
- `docs/spec/act-phrases.md` 4.4, with its owner.
- `lean/VE/Acts/Lexical.lean` (`VE.Acts.Lexical.joinFree`), a file shared with act-phrases.
- `ve/profile_table.json`, regenerated through `tools/regen_generated.py --write` (its generator is
  `tools/profile_table.py`).

There is no `allowlists`.

The regulated declarations need no new decoder. The speech route already decodes them with
`VE.Norms.Wire.decodeNormsEnvironment` on the environment without the speech block. That decoder reads `acts@0` when
the profile list names it (`Norms/Wire.lean:83`), and `decode_acts_compatible` states this.

A command's act may then be an `acts@0` act: up to 400 bytes, with declared fixed phrases and frames, read by AP-1 or by
AP-2 as one simple act. AP-1's declaration check uses the existing `joinWords` table, including *for*, and refuses
joined acts outside fixed phrases. No `JoinedCommandAct` reader refusal is reachable under the decoded `@0`
environment. The batch that first admits AP-2 joined acts adds that refusal and revises the affected reader iffs;
act-phrases' readings route (D-33) is not involved here.

```lean
/-- AR-10 (act-phrases 4.4, revised with its owner): `acts@0` changes no route, and the speech route is one it may
join. -/
theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : VE.Compose.Route)
    (hg : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r) :
    VE.Compose.gateOf VE.Compose.profileTable (ps.erase "acts@0") = .ok r ∧
      (r = .norms ∨ r = .normDefaults ∨ r = .readings ∨ r = .speechActs)

/-- Decoder compatibility (act-phrases 4.4, finding F2): the speech route decodes its regulated declarations with
the norms route's decoder, `acts@0`'s hook included, on the environment without the speech block. -/
theorem decode_acts_compatible (j : Lean.Json) (se : SpeechEnvironment)
    (h : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se) :
    ∃ j', VE.SpeechActs.Wire.stripSpeech j = .ok j' ∧
      VE.Norms.Wire.decodeNormsEnvironment j' (acts := true) = .ok se.ne

/-- Every environment the merged gate admits is still admitted, on the same route. -/
theorem profileGate_mono (ps : List String) (h : VE.SpeechActs.Wire.profileGate₀ ps = .ok ()) :
    VE.SpeechActs.Wire.profileGate ps = .ok ()

/-- Without `acts@0` the decoded speech environment is the merged one. -/
theorem decode_without_acts (j : Lean.Json) (ps : List String)
    (hp : VE.SpeechActs.Wire.profilesField j = .ok ps) (h : "acts@0" ∉ ps) :
    VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = VE.SpeechActs.Wire.decodeSpeechEnvironmentFull₀ j

/-- `check` calls this factored predicate, which uses the existing `joinWords` including `for`. -/
def VE.Acts.Lexical.joinFree (fx : List String) (act : String) : Bool

/-- Under `acts@0` a read command's act is one simple act in a decoded environment. -/
theorem command_act_simple (j : Lean.Json) (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : "acts@0" ∈ se.profiles) (r : Reading) (hr : readCommand se sc E L b s = .one r) :
    ∃ g a fx, g ∈ se.ne.regulated ∧ g.name = r.act ∧ g.act = some a ∧
      VE.Norms.Wire.actsFixed se.profiles se.json = .ok fx ∧ VE.Acts.Lexical.joinFree fx a = true
```

`gate_acts`' conclusion gains `r = .speechActs` only (simple acts; C12). `.clauses` and `.discourse` are
profile-composition PC-6's, after CI-5, in act-phrases' one revision; CI-5 does not add them.

`profileGate₀` and `decodeSpeechEnvironmentFull₀` are today's definitions, kept under those names as `phraseOk₀` is in
CI-4. Every theorem of `Demand.lean` quantifies over any `SpeechDoc`, so it holds for these documents unchanged.

**Fixtures:** "Choose a scenario and its listed facts." (the fixed phrase "a scenario and its listed facts"), "Choose
declared kinds of things for the new word." (a frame for *choose* with the marker *for*, "the new word" bound) and
"Enter a clarification or restatement." (the fixed phrase "clarification or restatement"): +3 segments, 125 B. "Click
Check and save." is refused at declaration by AP-1's join check. Every CI-1 to CI-4 row is unchanged with
`acts@0` off. A reader-level `JoinedCommandAct` fixture belongs to the later AP-2 admission batch.
**Seeded bug:** the gate admitting `acts@0` with `soft-norms@0` (fails SA's fixture φ).
**Deleted, not duplicated:** the act phrase is decoded by `acts@0`'s own decoder; the speech route writes no act
grammar of its own, and no profile list of its own beside AR-10's rows.
**Conflicts:** ap-1bd touches `Standalone.lean` and `Readings/Wire.lean`, not `SpeechActs/`; CI-5 waits for its merge
only for the typing it relies on. Before starting, check every in-flight branch's diff for
`lean/VE/Compose/Dispatch.lean`.

### CI-6. Imperative-shaped non-commands (Lean, 4–6 h)

**Needs:** CI-3, CI-E1's verdict on which cue rows are rules, and en-sw merged (C1). **Files:**
`lean/VE/Commands/Forms.lean` (new: the classifier only), `Run.lean` (`readInstruction` calls `readImperative`), `Texts.lean`,
`Examples.lean`. **Shared:** `lean/VE/EnglishGrammar/SourceWords.lean`, rows only, with owner `CI-6`, and its generated
view `ve/english_grammar/source_words.json` through the english_grammar generator. Also the `english.command` response
shape, its encoder theorem and its inventory rows, extended for `Alt.form`, and the request, which gains the unit's
heading flag, carried to `readInstruction` as a new `Context` field `heading : Bool` (A3). `readInstruction` applies the heading
flag before `proofTask`, and no cue runs inside P (N7; tested through both callers). `surfaceKind` is not changed.

**The cues are source-word rows (C1).** Following the DRI decision of 2026-10-28 (items 1 and 2), the lexical cues
(`Suppose`, `Imagine`, `Consider a case where`, `Consider a situation where`, `Feel free to`, `at any time`, `Note
that`, `See`) are `SourceWordRow`s in `SourceWords.lean`, with `owner` `CI-6` and `profile` `speech-acts@0`. A cue
that CI-E1 kept as a rule is a `refuse` row, carrying the `NotACommand: <form>` code, its English text and a rewrite.
Every other cue is a `readings` row, so its form joins the list. `Forms.lean` holds no word list. It keeps only the
classifier and the structural cues: a heading, and `<imperative> and <declarative clause>.`. If a cue does not fit
en-sw's row kinds, CI-0 records it, and the change is english-lean's to make (the DRI fixed the row type).

```lean
inductive Form
  | command | supposition | permission | conditionalClaim | remark | heading
  deriving DecidableEq, Repr

/-- The forms a wording can have, given whether it is a heading: the classifier over the `CI-6` rows of
`VE.EnglishGrammar.SourceWords` and the two structural cues. A row is a rule only if CI-E1 kept it; every other cue
adds its form to the list. With no cue, return `[.command]`. -/
def forms (s : String) (heading : Bool) : List Form

theorem forms_nonempty (s : String) (heading : Bool) : (forms s heading).length > 0

-- `Alt` gains `| form (f : Form)`: a non-command form, which yields no demand.

-- CI-1's `variable` line is in scope.
def readImperative (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) (heading : Bool) : StepOutcome

/-- A non-command never yields a demand. -/
theorem nonCommand_no_demand (heading : Bool) (h : Form.command ∉ forms s heading) (r : Reading) (x : Bool) :
    readImperative se sc E L b s heading ≠ .one r x ∧ ∀ rs, readImperative se sc E L b s heading ≠ .steps rs

/-- Conservative: where the only form is a command, the reading is CI-3's. -/
theorem command_unchanged (heading : Bool) (h : forms s heading = [.command]) :
    readImperative se sc E L b s heading = readStep se sc E L b s

/-- A command form beside another form is never a single reading: a W2 reading set in translation,
`AmbiguousForce` with the rewrites in authoring (the relay maps `many` by mode); the answer carries every form. -/
theorem forms_ambiguous (heading : Bool) (h : 2 ≤ (forms s heading).length) (h1 : Form.command ∈ forms s heading)
    (hn : (forms s heading).length ≤ VE.SpeechActs.Wire.readingsBound) :
    ∃ alts, readImperative se sc E L b s heading = .many alts ∧
      ∀ f ∈ forms s heading, f ≠ .command → Alt.form f ∈ alts
```

`readInstruction`, outside the proof task, is now `readImperative`, stated as CI-3's `readInstruction_step` is.
`Texts.codeClasses` gains `ConditionScope`, `ThenWithoutStep` and `NotACommand`, and the extended public entry
restates `readInstruction_refused_classed` with the composed class lookup. Pin the default fixture
`forms "Click Ask." false = [.command]`; no empty-list fallback is allowed.

**The cue rows to test in CI-E1:** `Suppose …`, `Imagine …`, `Consider a case where …`, `Consider a situation where …`
(supposition); `… at any time`, `Feel free to …` (permission); `<imperative> and <declarative clause>.` (conditional
claim: "If you <x>, <clause>."); `Note that …`, `See …` (remark; the asserted complement of `Note that` is
presupposition's factive, not this plan's); an imperative heading (heading).
**Supposition and modality (C24).** CI-6's supposition classification ("Suppose", "Imagine", "Consider") applies to
modality's reader; modality's MD-4 owns the scenario meaning. The CI-6 → MD-4 pointer is added by whichever of CI-6
and MD-4 merges second.
**English:** "This sentence asks you to imagine a situation; it gives no instruction." and the like, one text per form,
in `Texts.lean`.
**Fixtures:** constitution u0156.s01, u0068.s02, u0029.s01 (supposition); tutorial "Suppose an account cannot reach a
secret through a network of access grants." (supposition) and "Add a grant from the report to the secret, and the
certificate fails." (conditional claim); web "Change the facts of a scenario and VE decides it again." (conditional
claim; its "again" still blocks it); "Skip it at any time." (permission and command: a reading set); every CI-1 to
CI-5 row unchanged.
**Bytes:** 0 on the web fixture. In the constitution, the six suppositions (744 B) can be LABELLED with a stated reason
if the pilot's translator and audit adopt the rule (estimate; their decision).
**Seeded bug:** `forms` returning `[.command]` for `Suppose …` (fails the u0156.s01 fixture).
**Deferred, not built: `listItem`** (A3, C4). `scope@0` refuses `speech-acts@0`, so nothing can supply a lead-in. The
form waits until a scope x speech row exists (section 11, issue 5); until then, the constitution's u0231.s03 under
u0230.s03 is not a fixture here.
**Deleted, not duplicated:** the cue words live only in `SourceWords.lean`. A supposition's frame is not built here.

### CI-7a and CI-7b. Purpose clauses (Lean; CI-7a 2–3 h after CI-4 and CI-6, CI-7b 2–3 h after C21's bridge; *estimates*)

CI-7 is split in two (synthesis round 2, N7, the converged plan debate's round 2).
**CI-7a needs** CI-4 and CI-6, because it calls `readImperative` (A3). It reads every split and refuses: if any
split's command part reads (one or many), the unit is refused as `PurposeClause`, with one code and one text;
otherwise, if an unfinished split could change that, the answer is `limit`; otherwise it is `readImperative`'s. A
purpose or goal infinitival complement is never folded into an opaque act with guard ⊤ (section 12, finding (b)).
**CI-7b needs** CI-7a; the named bridge C21, which is speech-acts' `documents@1` lift, after CI-2 (owner named by
synthesis round 2), reached through `VE.Purposes`' S1 link; and purpose-explanation's usable interface, a reader
for the purpose part and not only a merged spec, since that plan owns the purpose relation and its English. Until
the bridge lands, a purpose clause on an instruction is refused (D6). This plan
fixes only the split and its theorems. Under CI-7b, "Open X to fix it." and "To fix it, open X." become a MIXED unit: the command
part is read by `readImperative`, and the purpose part goes to purpose-explanation's reader. In translation, the unit
is a reading set: (a) a goal-conditional command, if attitudes can state the goal; (b) a command with a stated
rationale. **Shared:** `Run.lean` (`readInstruction` calls `refusePurposive` at CI-7a and `readPurposive` at CI-7b), `Texts.lean`
(`PurposeClause`, CI-7a), and, at CI-7b, the `english.command` response shape, its encoder theorem and its inventory
rows, extended for `Alt.purpose` and `StepOutcome.mixed` (A3).

```lean
-- CI-1's `variable` line is in scope.

/-- Every ` to ` cut of `<x> to <p>.`, left to right, then every `, ` split of `To <p>, <x>.`, left to right,
with nonempty parts, with no environment veto (N7): a declared whole act does not exclude a split, and the
environment enters only through reading. The unsplit wording is considered separately. -/
def purposeSplit (se : SpeechEnvironment) (s : String) : List (String × String)

-- Its operative body is in the item-1 spec, section 11: split trimmed text at every eligible separator, list the
-- ` to ` splits before the `, ` splits, and filter empty parts. `se` does not exclude a split inside a declared act.

-- `Alt` gains `| purpose (r : Reading) (p : String)`: a split's command reading and its purpose text.
-- `StepOutcome` gains `| mixed (r : Reading) (p : String)`: a MIXED unit whose purpose part is UNFORMALISED (D6).

/-- The alternatives contributed by one split after `readImperative` classifies its command part. -/
def purposeForSplit (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (x p : String) (heading : Bool) : List Alt

/-- Each split with its command part's full outcome under CI-6 (`one`, `many`, `refused` or `limit`, under the same
heading flag), plus a completeness flag: `true` when no split's enumeration was cut short (N7). -/
def purposeReadings (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) (heading : Bool) : List ((String × String) × StepOutcome) × Bool

/-- A split's command part reads: its outcome is `one` or `many`. -/
def partReads : StepOutcome → Bool
  | .one _ _ | .many _ => true
  | _ => false

/-- CI-7a: `PurposeClause` when a split's command part reads; else `limit` when the enumeration is incomplete;
else `readImperative`'s. -/
def refusePurposive (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) (heading : Bool) : StepOutcome

theorem purpose_refused (heading : Bool)
    (h : ∃ x, x ∈ (purposeReadings se sc E L b s heading).1 ∧ partReads x.2 = true) :
    refusePurposive se sc E L b s heading = .refused "PurposeClause" Texts.purposeClause

theorem purpose_unfinished (heading : Bool)
    (h : ∀ x ∈ (purposeReadings se sc E L b s heading).1, partReads x.2 = false)
    (hc : (purposeReadings se sc E L b s heading).2 = false) :
    refusePurposive se sc E L b s heading = .limit

theorem purpose_passes (heading : Bool)
    (h : ∀ x ∈ (purposeReadings se sc E L b s heading).1, partReads x.2 = false)
    (hc : (purposeReadings se sc E L b s heading).2 = true) :
    refusePurposive se sc E L b s heading = readImperative se sc E L b s heading

-- CI-7b's statements follow.

/-- The unsplit wording's complete alternatives, then each split's `purposeForSplit`, from `purposeReadings`;
`many` alternatives preserved. -/
def purposeAlts (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) (heading : Bool) : List Alt

def readPurposive (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (s : String) (heading : Bool) : StepOutcome

/-- Each purpose reading is a split whose command part CI-6 reads as a command, with the same heading flag. -/
theorem purpose_reading (r : Reading) (p : String) (heading : Bool)
    (h : Alt.purpose r p ∈ purposeAlts se sc E L b s heading) :
    ∃ x, (x, p) ∈ purposeSplit se s ∧
      (readImperative se sc E L b (capitalise x ++ ".") heading = .one r false ∨
       ∃ alts, readImperative se sc E L b (capitalise x ++ ".") heading = .many alts ∧
         (∃ sh, Alt.shape sh [r] ∈ alts))

theorem purpose_nonCommand (x p : String) (heading : Bool)
    (hs : (x, p) ∈ purposeSplit se s)
    (hn : Form.command ∉ forms (capitalise x ++ ".") heading) :
    purposeForSplit se sc E L b x p heading = []

/-- One purpose reading and nothing else: a MIXED unit. -/
theorem purpose_mixed (r : Reading) (p : String) (heading : Bool)
    (h : purposeAlts se sc E L b s heading = [.purpose r p])
    (hl : (purposeReadings se sc E L b s heading).2 = true) :
    readPurposive se sc E L b s heading = .mixed r p

/-- No match hides another reading (A6): with two or more readings, the unsplit wording's among them, the answer
lists every one. -/
theorem purposes_ambiguous (heading : Bool) (h : 2 ≤ (purposeAlts se sc E L b s heading).length)
    (hc : (purposeAlts se sc E L b s heading).length ≤ VE.SpeechActs.Wire.readingsBound) :
    readPurposive se sc E L b s heading = .many (purposeAlts se sc E L b s heading)

/-- Without a split, the reading is CI-6's (CI-7a's `refusePurposive` and CI-7b's `readPurposive` alike). -/
theorem purpose_none (heading : Bool) (h : purposeSplit se s = []) :
    readPurposive se sc E L b s heading = readImperative se sc E L b s heading
```

`readInstruction`, outside the proof task, is now `refusePurposive` at CI-7a and `readPurposive` at CI-7b, each stated
as CI-3's `readInstruction_step` is. CI-7a adds `PurposeClause` to `Texts.codeClasses`. At CI-7b the unsplit outcome
is retained. Two completed alternatives yield `many` even beside a limited split; with fewer
than two, a limit yields `limit`; over the speech wire's bound (`Wire.lean:761`) yields `limit`. No split command part classified as a heading
or other non-command yields `mixed`. Restate `readInstruction_refused_classed` for this extension, adding any new local
refusal code to `Texts.codeClasses`.

**Fixtures, CI-7a:** W4 unchanged; a whole act plus its command part (the A6 environment) is `PurposeClause`; an
ambiguous split (its command part `many`) is `PurposeClause`; an exhausted split, with no split that reads, is `limit`.
**Fixtures, CI-7b:** "Remove the review rule in the IDE to find a countermodel.", "Edit JSON to bring your own vocabulary or
world.", "To fix it, change print back to read and click Review meaning.", "To ask “May a new employee read the
handbook?”, write this statement to test." and "Mode is fixed for this document; start a new document to change it."
(5 segments, 315 B to READINGS or MIXED; estimate). An infinitival relative inside a declared act ("Choose a unit
revision to restore.") is a candidate split, but its command part has no declared act in `E_web`, so W4 remains
`one`. In the A6 environment that declares both the whole act and its command part, the wording is `many` with both
readings. Add a leading `To <p>, <x>.` fixture and a purposive heading fixture in which the split part has no command
form and yields no `mixed` demand.
**Seeded bugs:** CI-7a, `refusePurposive` answering `readImperative`'s reading when a split's command part reads
(fails the whole-act fixture); CI-7b, `readPurposive` dropping the unsplit reading when a split reads (fails the A6
fixture).
**Deleted, not duplicated:** the purpose part is read only by purpose-explanation's reader; this batch holds no
purpose wording.

### CI-8. Measurement and report (Python, files, with one Lean print entry; 3–4 h)

**Files (new):**
- `usecases/webapp-commands/segments.json`: the 59 segments, each with its source file, text, catalogue blob
  `1ff7a7b72` and R 2.1's group.
- `usecases/webapp-commands/environment.json` (`E_web`), **generated** from `VE.Commands.Examples.E_web` ((iv)).
  `lean/VE/Commands/WebEnvMain.lean` prints it, as `VE/Compose/ProfilesMain.lean` prints the profile table. A
  generator, `tools/webapp_commands_env.py --write` and `--check` (closest existing: `tools/profile_table.py`), is
  registered in `tools/regen_generated.py`. The file is never written by hand.
- `usecases/webapp-commands/harness.py`: builds one `english.command` request per segment, and writes
  `evidence/coverage.json` with Lean's outcome, the bytes computed by program, and D7's vocabulary audit.
- `usecases/webapp-commands/REPORT.md` and `docs/spec/commands-imperatives-report.md`.

**The tutorial census:** the bytes of `docs/onboarding/ve-tutorial.html` pinned by sha256, and every imperative-shaped
sentence listed with Lean's `forms` (after CI-6) or the reader's outcome.
**Tests** read the saved evidence only, never a live diff. `tools/regen_generated.py --check` keeps `environment.json`
equal to Lean's `E_web`, so there is no hand copy and no equality test.
**Done when:** the report gives, for each batch merged so far, the measured segments and bytes, the difference from R's
estimates with a reason for each, and the declared vocabulary's size (acts, constants, spellings, phrases).

## 3. Experiments (pre-registered)

The DRI authorised all three on 2026-10-28 (item 5): Sonnet 5.5 stands in for the human raters, on subscription
accounts under the usage-cap rules (88% per account), and no money is spent. This plan makes no model call itself.
Raters see plain English only. The bars below are fixed before the first call and do not move after it.

**CI-E1. Command or not.**
- *Items:* every imperative-shaped sentence of the pinned corpora: the 59 web segments, the tutorial's (at least 43),
  the constitution's 21 units of R 2.3, the frameworks' 8 remarks.
- *Labels:* two independent raters assign each item one of command, permission, supposition, conditional claim, remark,
  heading or list item. Disagreements are adjudicated by a third, blind to the cue table.
- *Pre-registered bar:* a cue row becomes a rule in CI-6 only if (1) on its items the table never says "command" where
  the adjudicated label is not "command" (no false command), and (2) it agrees with the adjudicated label on at least
  95% of its items, with at least 5 items. Every other row only adds its form, so its sentences are reading sets. The
  list-item label is still collected, but CI-6 builds no list-item row while `listItem` is deferred.
- *Result recorded* in `docs/spec/commands-imperatives-e1.md`, with every item and label.

**CI-E2. Choice commands.**
- *Hypothesis:* English readers read "Choose A or B." as "choose exactly one of A and B; either is allowed" (free
  choice), not as "choose A, or else choose B" and not as "choose at least one".
- *Items:* the 4 web segments of R 2.1's choice group, plus 6 constructed items of the same shapes (two to four listed
  alternatives; listed acts).
- *Method:* each rater picks the paraphrase that says what the sentence asks, among the three, in random order.
- *Pre-registered bar:* at least 90% of the judgements pick the free-choice paraphrase, and at least 8 of the 10 items
  reach 80% on their own.
- *If it passes,* a later batch (CI-9, about 5 h) builds `Choose <A>, <B> … or <Z>.` as a command to answer a which-one
  question over the listed alternatives (SA 1.3's `which_one` with `Answer question <n>.`), whose compliance is the
  answer token. +4 segments, 189 B (estimate). *If it fails,* the choice stays refused, as SA 2.3 rules today.

**CI-E3. Commands whose object is a question.**
- *Hypothesis A:* "Confirm who acts on whom for a relation." and "For a new word, choose what kind of thing it names." are
  read as a requirement to answer a question.
- *Hypothesis B:* "Check that it says what you meant." is read as asking the reader to say whether the displayed reading
  is the intended one, which is SA's `Which reading did you mean?`, whose answer is testimony.
- *Pre-registered bar:* for each hypothesis, at least 90% of the judgements pick that paraphrase over two alternatives,
  on the 5 web items plus 5 constructed ones.
- *If either passes,* a later batch maps that form onto SA's existing question modes, with no new semantics; up to +5
  segments, 271 B (estimate; one item also needs attitudes for "meant").

## 4. Dependencies

| Needed from | Design and branch | Batches waiting | Why |
|---|---|---|---|
| q1-4b merged | question-answering, `feature/q1-4b` | CI-2 | the same two Python files |
| gi-1 | the generated-inventory design, not launched | CI-1 (rebase only) | `lean/VE.lean` imports |
| rd-9's relay-binding inventory | rd-9, `tests/test_relay_binding_inventory.py` | CI-2, CI-3, CI-6, CI-7 (rows only) | D9: the one owner of relay binding |
| english-lean's constant spellings | english-lean (`Lexicon.lean`) | CI-4 | labels and quoted wordings (A5); a widening, if one is needed, is english-lean's row |
| ap-1bd merged; act-phrases D9 decided | act-phrases, `feature/ap-1bd` | CI-5 | `acts@0` typing; joined fillers |
| the gate-contract revision | act-phrases (4.4, `gate_acts`) and composition (AR-10's rows) | CI-5 | admitting `acts@0` with `speech-acts@0` |
| en-sw merged | english-lean, backlog row en-sw (ready, p84) | CI-6 | C1: the cue rows are `SourceWordRow`s |
| speech-acts' candidate pipeline | speech-acts (`Source/Run.lean:141-187`, `Wire.lean:749-780`) | CI-1 on, in translation | D11: `many` is emitted through it; CI-0 maps `Alt.shape (.seq …)` and `Alt.form` onto it, or refuses them in translation |
| `judgments@0` with speech acts (jt-2c) | judgment-terms | a later batch; D7 meanwhile | an open term inside a command's act or guard |
| a `scope@0` x `speech-acts@0` row | scope (sc-1ae, then sc-2) and AR-10; none planned | CI-6's deferred `listItem` form | C4: lead-ins govern list items |
| frames and suppositions | scope and discourse (shared piece 5) | CI-6 classifies; the frame's meaning is theirs | "In that case" |
| et-4, then ET-5/ET-6 | events-time-causation, `feature/et-4` | order with time (not this plan) | 223 B of web copy is time |
| qt-a3c, then QT-A4 | quantities, `feature/qt-a3c` | none here | 473 B of web copy is quantities inside commands |
| attitudes AT-3 | attitudes | none here | "what you meant", "you intended" (214 B with anaphora) |
| presupposition PS-* | presupposition | none here | "it", "its", "again"; the factive of `Note that` |
| purpose-explanation's usable interface | wave started 2026-10-28 | CI-7b | the purpose relation and a reader for the purpose part |
| speech-acts' `documents@1` lift, after CI-2 | speech-acts (C21's named bridge, owner named by synthesis round 2) | CI-7b | a purpose clause on an instruction is refused until it lands |
| author commitments | queued wave | the deferred list items under "We will:" | the "we" binding (shared piece 8) |
| definitions | wave started 2026-10-28 | none | a definition is never a command |

## 5. Order and merge-conflict plan

CI-0, then CI-1. CI-2 after q1-4b's merge, with the proof task, the inventory rows and `readInstruction`. CI-3, then CI-4,
each wired through `readInstruction` (both edit `Wire.lean` and `Source/Run.lean`, so never in parallel). CI-5 after CI-2,
ap-1bd and the gate-contract revision. It may run beside CI-3 or CI-4 only if it rebases its `Wire.lean` hunk
(`allowlist`, a different definition) after whichever lands first. CI-E1 to CI-E3 and CI-8 after CI-2, beside anything;
CI-8 is re-run after each later batch. CI-6 after CI-3, CI-E1 and en-sw, with `listItem` deferred until a scope x
speech row exists. CI-7a after CI-4 and CI-6; CI-7b after CI-7a, speech-acts' `documents@1` lift (C21) and purpose-explanation's usable
interface.

New files carry most of the work (`lean/VE/Commands/*`, `usecases/webapp-commands/*`). Every shared file a batch
touches:

| Batch | Shared files |
|---|---|
| CI-1 | `lean/VE.lean`, `lean/VE/Audit.lean`, `tools/layer_policy.py`, `lean/VE/SpeechActs/Wire.lean` (`readingsBound` only); generated inventories via `tools/regen_generated.py --write` |
| CI-2 | `lean/VE/Service/Protocol.lean`, `lean/VE/SpeechActs/Source/Run.lean`, `ve/backends/english_lean.py`, `ve/speech_english.py`, `ve/speech_acts.py` (`PROOF_TASK_ACT`), `ve/speech_document.py`, `tools/relay_lint.py`, `tests/test_relay_binding_inventory.py`, the assurance manifest; generated route map and schemas via their generators |
| CI-3 | `lean/VE/SpeechActs/Wire.lean` (`surfaceKind`), `lean/VE/SpeechActs/Source/Run.lean` (the derived order), `tests/test_relay_binding_inventory.py`; the response shape and schema via their generators |
| CI-4 | `lean/VE/SpeechActs/Wire.lean` (`typographic`, `phraseOk`, `asciiWording`'s caller), `lean/VE/SpeechActs/Source/Run.lean` (the fence check's `asciiWording`) |
| CI-5 | `lean/VE/Compose/Dispatch.lean` (`actsRefuses`, `gate_acts`), `lean/VE/SpeechActs/Wire.lean` (`allowlist`), `lean/VE/Acts/Lexical.lean` (`joinFree`, shared with act-phrases), `docs/spec/act-phrases.md` (4.4); the profile table via its generator |
| CI-6 | `lean/VE/EnglishGrammar/SourceWords.lean` (rows only), `tests/test_relay_binding_inventory.py`; `ve/english_grammar/source_words.json`, the response shape and schema via their generators |
| CI-7a | none beyond `lean/VE/Commands/*` (`Texts.lean` gains `PurposeClause`) |
| CI-7b | `tests/test_relay_binding_inventory.py`; the response shape and schema via their generators |
| CI-8 | `tools/regen_generated.py` (the generator row) |

## 6. Risks

1. **The CI-2 A/B finds differences.** Python fills slots with `str.format` on `act[4:]` and folds case with
   `ascii_fold`; Lean's `filled` (through `fillHoles`) must do the same. Otherwise each difference is a `DELTA.md` row:
   SIGNED by R1 or R2 when its conditions hold, or a verdict change that needs the DRI (section 9). CI-0's stub
   computes the expected rows on the speech-acts corpus first.
2. **Too many fill candidates.** The product over slots of constants and phrases grows fast. `candidates` is a
   specification; the implementation may match the act's literal words first and fill the gaps, provided it is proved
   equal to the specification. `limit` is reported in English, never as "no reading".
3. **Opaque acts inflate claims.** D7 is the guard. CI-8 reports the declared vocabulary's size beside every number.
4. **D9 reopens a reviewed rule** (SA 3.2's ASCII-only wording). If CI-0's review or the DRI refuses it, CI-4 keeps
   ASCII and the three quoted segments stay refused (about 220 B).
5. **MIXED parts for steps** may interact with the coverage projection (SA 6). CI-3's fixtures include a coverage row
   for a two-step unit.
6. **The fixture drifts from the live page.** It is pinned by blob. Refreshing it is a milestone item on the lead's
   request.

## 7. Shared pieces and new adapters

R 8 lists the shared pieces. This plan builds three of them, each marked **NEW** with its closest existing
abstraction, and reuses or depends on the rest.

| Piece | This plan | Status | Others that need it |
|---|---|---|---|
| 1. Act-phrase instance matcher | builds `filled` (through `fillHoles`) and `slotFills` in `VE.Commands.Read`, for commands only; it is not offered as the module E3's norm sentences import ((ii)) | **NEW**; closest: english-lean's `fillHoles` (`Lexicon.lean:222`) | E3-norms ("Every user must <act>"), `Must Alice <act>?`, attitudes over acts and events choose their own owner with english-lean |
| 2. Display names for constants | reuses english-lean's constant spellings: `ConstDecl.display`, `Overlay.constants`, `Lexicon.spellings`, `Env.declaredSpelling` (A5); `this` phrases are `definites` through a widened `phraseOk` | reuse (owner english-lean); the `this` case of `phraseOk` is **NEW**, closest: `phraseOk` and `Scope.definites` | UDHR article names, presupposition, discourse's content names |
| 3. Typographic normalisation | builds `typographic` in `SpeechActs/Wire.lean`, beside `asciiWording` (CI-4, (i)) | **NEW**; closest: `asciiWording` and `surfaceWords` (`Wire.lean:613-619`); english-lean's lexer keeps `’` as a word character (`chunkChar`, `Lexer.lean:53`) | every English reader |
| 4. Quoted wordings as terms | quoted wordings are constant spellings (piece 2) | reuse | attribution, the constitution's quoted instructions |
| 5. Suppositions and frames | classifies (CI-6) | depends on scope and discourse | scope, discourse, math-evidence ("Let", "Assume"), defeasible |
| 6. Order between units | states it, no logic (`stepOrder`, CI-3) | **NEW**; closest: W2's MIXED parts (the steps' spans), and events-time-causation's `before`, which gives it a meaning later | events-time-causation, scope's step lists |
| 7. Purpose relation | splits it off (CI-7) | depends on purpose-explanation | purpose-explanation |
| 8. The pronoun legend | uses SA's "you" | reuse | author commitments ("we"), attitudes |
| 9. Imperative-form classification | the classifier `forms` in `Forms.lean` (CI-6); its lexical cues are `SourceWordRow`s in english-lean's `SourceWords.lean` (C1) | the classifier is **NEW**, closest: `surfaceKind` (`Wire.lean:641`); the rows reuse en-sw's table | scope, author commitments, headings |
| 10. Reading sets over force | uses speech-acts' candidate pipeline (`Source/Run.lean:141-187`, `Wire.lean:749-780`); `many` carries the alternatives (D11). CI-0 maps `Alt.shape (.seq …)` and `Alt.form` onto it, or refuses them in translation | reuse (owner: speech-acts) | defeasible ("should") |

**New adapters** that are not shared pieces, each with its closest existing abstraction:

| Adapter | Batch | Closest existing abstraction |
|---|---|---|
| `GuardFault`, `guardOf`, `guardsOf` | CI-1 | english-lean's `TranslateOutcome` (`Read.lean:63`), whose cases it keeps |
| `Context` and `readInstruction`, the one public entry | CI-2 | `VE.Question.Run`'s request with its `Caller` (`Question/Run.lean:181-185`), the `english.question` mode's entry |
| `proofTask` | CI-2 | the Python branch it replaces (`ve/speech_english.py:212-222`), and the query records the speech wire derives (`Wire.lean:862`) |
| `Alt`, the alternatives of `many` | CI-3, CI-6, CI-7 | speech-acts' candidate pipeline (`Source/Run.lean:141-187`, `Wire.lean:749-780`), the shape that translation emits (D11) |
| `purposeSplit`, `purposeReadings` | CI-7 | none in VE; purpose-explanation's reader takes the purpose part |
| the `E_web` generator | CI-8 | `tools/profile_table.py` with `VE/Compose/ProfilesMain.lean` |

## 8. Not in this plan

Time, deadlines, fulfilment and the meaning of the order of steps (events-time-causation); quantities inside commands
(quantities); intentions, goals and "what you meant" (attitudes); "it", "its" and "again" (presupposition); purposes
(purpose-explanation); list lead-ins and frames (scope, discourse), and list items governed by a lead-in until a scope
x speech row exists (C4); "we will" (author commitments); requests ("Could you …?"), which stay reading sets with the
request reading unsupported (SA 2.3); assent and confirmation as acts, for which this plan has no item
(action-assurance keeps that as its own open item; synthesis round 2, N12); runtime UI templates; obedience, authority and ability, which VE never certifies;
and any edit to the live web page on `expand/webapp`.

## 9. DRI rulings: what a standing ruling signs, and what still needs the DRI

From `manage-agents/DRI-RULINGS.md` and the DRI decisions of 2026-10-28
(`reviews/dri-decisions-20261028-catalogue-owner.md`). A batch records each covered delta in its `DELTA.md` as
`SIGNED by standing ruling R<n> (DRI-RULINGS.md)`, with the evidence the ruling asks for. This plan reserves no DRI
signature that a standing ruling covers.

| Delta | Batches | Signed by | Evidence the ruling asks for |
|---|---|---|---|
| A diagnostic or English line reworded in an A/B | CI-2, and every later A/B | R1, when it keeps the base's quoted names, path and specificity | a test over the saved delta that every head record keeps the base's path and quoted names |
| Fault order | CI-2 (Lean's order is the single owner's) | R2 | the order deterministic, one sentence per rule in `DELTA.md` |
| Added fields that carry Lean's English or locations (paraphrases, fill spans, rewrites) | CI-2, CI-3, CI-6, CI-7 | R3 | goldens updated; a test that each field equals Lean's text or the true location; ids and positions bound to the request |
| Lean CPU above the relative allowance | every batch | R4, within 1 s Lean CPU and 2 s wall per document check | saved evidence on the final HEAD |
| Trusted Lean growth that replaces Python's command branch | CI-2, which deletes that branch in the same change | R6 | the allowance and its reason, `tools/trust_map.py --allow`, in `docs/trust-baseline.json` |
| Trusted Lean growth for new Lean behaviour, at most 150 lines (K+S+V) per item | CI-1, CI-3, CI-4, CI-5, CI-6, CI-7 | R16 | a `DELTA.md` row itemised per file, re-measured on the final HEAD with `tools/trust_map.py`; every new trusted definition exercised by a test that can fail; a FOLLOW-UPS.md row for the ties pass |
| Relay-binding rows | CI-2, CI-3, CI-6, CI-7 | DRI 2026-10-28, item 4 (D9) | one inventory row per relayed answer, and no binding of the plan's own |
| Source-word rows | CI-6 | DRI 2026-10-28, items 1 and 2 (C1) | rows only, checked by en-sw's checks |
| Generated files (inventories, schemas, the profile table, `source_words.json`, `environment.json`) | all | R12 | regenerated through `tools/regen_generated.py`, never hand-edited or counted as overlaps |

No standing ruling covers the following (DRI-RULINGS.md, "Never covered"). The DRI decided them on 2026-10-28
(`manage-agents/reviews/dri-decisions-20261028-commands-imperatives.md`). A batch cites a signed item in its `DELTA.md`
Ruling cell as `SIGNED by the DRI 2026-10-28 (reviews/dri-decisions-20261028-commands-imperatives.md item N)`, and only
when the item's conditions hold on the batch's final HEAD.

| # | Delta | Ruling | Conditions on the final HEAD |
|---|---|---|---|
| 1 | **CI-2 moves an authority.** Command English moves from Python to Lean, and Python's command branch of `parse_speech` and `PROOF_TASK_ACT` are deleted in the same change | SIGNED, item 2(a) | `DELTA.md` holds the deletion ledger: every deleted Python check with the Lean check or test that replaces it. The A/B over the pinned command corpus shows every sentence Python refused still refused or read as `many`. Trusted growth for the replacement is recorded under R6 (the table above) |
| 2 | **A verdict change in an A/B** (CI-2 to CI-5) | SIGNED, item 2(b), for three classes only: **b1**, a wording the batch's approved section adds (CI-3's steps and conditions written first; CI-4's labels, quoted wordings, `this` phrases and typographic quotes; CI-5's simple `acts@0` acts) going from refused to read, each row listed and covered by a fixture; **b2**, a change in the refusing direction (read to refused, one reading to `many`, a decided answer to UNKNOWN); **b3**, a CI-3 `choiceKindConflicts` flip that adds a conflict on a signed choice | The A/B file lists every changed row with its class, and a test pins the b1 rows to their fixtures. **Not signed, and the batch stops:** a previously read wording that now reads differently (it breaks D3's conservativity and is a bug to fix), and a CI-3 flip that removes a conflict from a signed choice (listed as needing a DRI signature) |
| 3 | **CI-4 widens what is accepted.** D9 reopens SA 3.2; `phraseOk` accepts `this` phrases; labels and quoted wordings read through english-lean's declared constant spellings (`declaredSpelling`) | SIGNED, item 3(a), for declared spellings only: an undeclared label or quoted wording stays refused | A CI-4 test that an undeclared label and an undeclared quoted wording are refused; `phraseOk_mono` and `typographic_ascii_id` proved. If english-lean's spelling checks must accept capitals or quotes, that change is english-lean's row in `Lexicon.lean`, made by its owner, with a refusal test for an undeclared spelling; the item-1 spec says whether it is needed |
| 4 | **CI-5 changes an approved theorem statement.** `gate_acts`'s conclusion gains `r = .speechActs`, and AR-10's `actsRefuses` no longer refuses `speech-acts@0` | SIGNED, item 3(b), for simple acts only (no joined fillers until act-phrases D9 says so), by the DRI as DRI and as arbiter between act-phrases and composition; no separate owner agreement is needed | `decode_acts_compatible` proved; the revised statement passes a statement review with a counterexample showing a complex or joined act under `speech-acts@0` still refused; act-phrases.md 4.4 revised in the same batch; `speechAllow` and the legacy `today` gate unchanged; `ve/profile_table.json` regenerated; CI-5 starts only after CI-2 and ap-1bd have merged. Any other change to `gate_acts` is not covered |
| 5 | **Trusted growth above R16's 150 lines, or any growth in K,** in a batch other than CI-2 | RESERVED for the DRI, item 3(c) | none signed here |

## 10. Index findings

The duplicates and contradictions with other plans that the debate named, against
`manage-agents/plans/PLANS-INDEX.md` (2026-10-28), and how draft 2 settles each.

| Finding | Index entry | What the debate found in draft 1 | How draft 2 settles it |
|---|---|---|---|
| D9, relay binding | D9; DRI 2026-10-28, item 4 (owner: rd-9's relay-binding inventory; plans add rows) | CI-2 stated its own binding contract (its own relay tests) | CI-2 adds `english.command` rows to `tests/test_relay_binding_inventory.py` and states no binding of its own. CI-3, CI-6 and CI-7 add the rows of their extensions (sections 2 and 9) |
| D11, three meanings of "reading set" | D11 | Piece 10 "builds" reading sets over force | Piece 10 uses W2 authored reading sets. `many` carries the alternatives, and translation emits them as a W2 reading set. This plan builds no reading-set representation (D5, section 7) |
| C1, the source-word owner | C1; DRI 2026-10-28, items 1 and 2 (owner: english-lean's `SourceWords.lean`, built by en-sw; plans add rows only) | CI-6's lexical cue table was a local set of source-word rows | CI-6 writes its cues as `SourceWordRow`s in `lean/VE/EnglishGrammar/SourceWords.lean` and waits for en-sw. `Forms.lean` keeps only the classifier (CI-6) |
| C4 and C12, the refusal matrix | C4 (`acts@0` x speech-acts; `scope@0` x speech-acts); C12 and the "act identity" row (`acts@0` refuses the soft chain and speech-acts) | CI-5 edited only `Wire.lean` and added `allowlists`, but AR-10's `actsRefuses` also refuses, and `gate_acts` excludes the speech route. CI-6's `listItem` needed a lead-in that `scope@0` cannot supply beside speech-acts | `acts@0` x speech-acts: CI-5 edits AR-10's rows in `Dispatch.lean` and revises `gate_acts`, with act-phrases' agreement and the DRI's decision (section 11, issues 1 and 2). `scope@0` x speech-acts is not settled here: `listItem` is deferred until a scope x speech row exists (section 11, issue 5) |
| `names` against english-lean's spellings (a new duplicate) | not yet in the index; the nearest rows are english-lean's lexicon and D12 (named unit sets) | `Scope.names` duplicated english-lean's constant display (`ConstDecl.display`, `Overlay.constants`, `Lexicon.spellings`, `declaredSpelling`, `Lexicon.lean:318-402`) | There is no `Scope.names`. Labels and quoted wordings are english-lean constant spellings, and `this` phrases are `definites`; `encodeScope` is unchanged (D8, CI-4) |
| The proof task's owner | the speech-acts row ("English in Python") and the question-answering row | The deletion ledger left "Prove that … using these premises." with question-answering's Q3, which covers only which-questions and `follows` (question-answering-PLAN.md:718, 964) | CI-2 ports the proof task into `VE.Commands` (`proofTask`) and deletes Python's branch and `PROOF_TASK_ACT` (D2, CI-2) |

The new duplicate (`names` against spellings) is settled inside this plan. The plan steward's next pass can record it
as settled.

## 11. Cross-plan issues for the DRI

What the joint position left to another plan's owner. The DRI decided every issue on 2026-10-28
(`manage-agents/reviews/dri-decisions-20261028-commands-imperatives.md`, cited below as "item N"); they stay listed so
that the schedule and synthesis round 2 count them.

1. **act-phrases: the gate contract (CI-5). Decided, item 3(b).** `gate_acts`'s conclusion gains `r = .speechActs`, and
   `actsRefuses` no longer refuses `speech-acts@0`, for simple acts only, with the decoder compatibility proof
   `decode_acts_compatible`. act-phrases.md 4.4 is revised in the same batch. The DRI signs as DRI and as the arbiter
   between act-phrases and composition, so no separate owner agreement is needed. Conditions: section 9, row 4.
2. **composition (AR-10): the edited row (CI-5). Decided, item 3(b).** `actsRefuses` lives in
   `lean/VE/Compose/Dispatch.lean`, which composition owns; `ve/profile_table.json` is regenerated from it. `speechAllow`
   and the legacy `today` gate do not change.
3. **english-lean: constant spellings (CI-4). Decided, item 3(a).** Labels ("Check rule conflict") and quoted wordings
   (`"Rule 4."`) are read only as declared constant spellings; an undeclared one stays refused. If english-lean's
   spelling checks must accept capitals or quotes, that change is english-lean's row in `Lexicon.lean`, made by its
   owner with a refusal test for an undeclared spelling. The item-1 spec computes whether it is needed.
4. **english-lean: en-sw (CI-6). Decided, item 4(a)** (and catalogue-owner items 1 and 2). CI-6 adds `SourceWordRow`s
   only and waits for en-sw's merge (backlog row en-sw, ready).
5. **scope and AR-10: a `scope@0` x `speech-acts@0` row (CI-6). Decided, item 4(b).** No row is created here. `listItem`
   stays deferred, and list items under a lead-in are refused, never read as standalone commands, until scope's owner and
   AR-10 add a supported row. Recorded under C4 for synthesis round 2.
6. **purpose-explanation: a usable interface (CI-7). Decided, item 4(c).** PX3(a) stands. CI-7a waits for CI-4 and
   CI-6; CI-7b waits for C21's named bridge, speech-acts' `documents@1` lift after CI-2 (synthesis round 2), and an
   executable purpose reader named by purpose-explanation's plan, not only a merged spec. Meanwhile a purpose clause on an instruction is refused under `speech-acts@0`, never read as plain content (D6).
7. **rd-9: inventory rows for a mode outside RD-9 (CI-2 on). Decided, item 4(d).** CI-2, CI-3, CI-6 and CI-7 add rows to
   `tests/test_relay_binding_inventory.py`, which classifies only the soft and rights routes today (its `ROUTES`).
   `english.command` is the first family from outside RD-9; round 2's generic-binder question counts it.
8. **The pronoun legend (shared piece 8). Decided, item 4(e).** There is one legend, speech-acts' binding
   (`VE.SpeechActs.Run.legend`). commitments' "we" joins it (reviews/dri-decisions-20261028-commitments.md item 2(d)), and
   this plan defines no second legend (CI-2).
9. **The E3 norm reader. Decided, item 4(f).** commitments' CM-4 does not reuse CI-1's matcher for norm sentences; the
   E3 norm reader's owner is english-lean (section 7, piece 1).

**Order and experiments (item 5).** The order is section 5. CI-E1 (two independent raters plus a blind adjudicator),
CI-E2 and CI-E3 are AUTHORISED with Sonnet 5.5 as the human proxy, under the usage-cap rules (88% per account) on
subscription accounts; no money is spent. Item counts and byte figures are estimates. The bars do not move after the
first call. A cue row becomes a CI-6 rule only on CI-E1's bar; otherwise it stays a reading set.

## 12. Synthesis round 2 and the fidelity-pilot revision (2026-10-30)

Applied from `manage-agents/debates/plan-synthesis-2/edits-commands-imperatives.md` (DRI-decided; sources: that
debate's `SYNTHESIS.md` sections 2 and 3, C12, C21, C24, N7, N12, and the converged plan debate's round-2 joint
position) and `manage-agents/reviews/dri-decisions-20261030-fp-commands-imperatives.md` item 1 (the fidelity pilot's
REVISE, findings (a) to (e) only). Where these differ from the item-1 spec, this section and the blocks it revises
govern (status note).

### 12.1 The synthesis round 2 edits and where each is applied

| Edit | What changes | Where |
|---|---|---|
| N7, the entry | `VE.Commands.readUnit` renamed `readInstruction` (the caller already defines `VE.SpeechActs.Source.readUnit`, `Source/Run.lean:62`); `commandFence_needs_context` moved to `Source/Run.lean`; the typing theorem `readInstruction_typed` covers the whole entry, proof task included | D2, CI-2, and every later batch |
| N7, the proof task | `Context` carries the decoded query records (id, target); `proofTask` reads P through `guardOf` (ambiguous `many`, budget `limit`, unread the reader's refusal); one reading must equal exactly one record's target, otherwise `QueryMismatch: <u>`; premise ids stay with `decodeDocument`; the `follows` loop stays question-answering's; fixture: an existing query with the wrong target | CI-2 |
| N7, purposes | `purposeSplit` lists every ` to ` cut with no environment veto; `purposeReadings` keeps each split's full outcome plus a completeness flag; CI-7 split into CI-7a (refuse as `PurposeClause`, else `limit`, else `readImperative`'s) and CI-7b (`many` or MIXED through `VE.Purposes`); fixtures W4 unchanged, whole act plus command part, ambiguous split, exhausted split | section 1, D6, CI-7a and CI-7b, sections 4, 5, 11 |
| N7, D11 | `many` targets speech-acts' candidate pipeline (`Source/Run.lean:141-187`, `Wire.lean:749-780`), not `Route/Readings.lean`; CI-0 maps `Alt.shape (.seq …)` and `Alt.form` onto it, or refuses them in translation | sections 4, 7 |
| N7, the heading flag | `readInstruction` applies the heading flag before `proofTask`; no cue runs inside P | CI-6 |
| N7, the bound of `many` | at most the speech wire's bound (`Wire.lean:761`), else `limit`; no new literal (`readingsBound` names the existing one) | CI-1, CI-3, CI-6, CI-7b |
| N7, spellings and spans | spellings from `L.spellings`, `L.valid` checked first; spans count code points | CI-2, CI-4 |
| C24 | CI-6's supposition classification applies to modality's reader; MD-4 owns the scenario meaning; the CI-6 → MD-4 pointer is added by whichever merges second | CI-6 |
| CI-5's files | `lean/VE/Acts/Lexical.lean`, shared with act-phrases | CI-5, section 5 |
| C12 | `gate_acts`' conclusion gains `r = .speechActs` only (simple acts); `.clauses` and `.discourse` are PC-6's, after CI-5, in act-phrases' one revision | CI-5 |
| C21 | CI-7b's bridge is speech-acts' `documents@1` lift, after CI-2; until it lands a purpose clause on an instruction is refused | D6, CI-7b, sections 4, 11 |
| N12 | no item for assent or confirmation as acts; action-assurance keeps that as its own open item | section 8 |
| PLANS-INDEX quality row | soundness reads "typed, unproved" until CI-1 proves the statements | the plan steward's row (`manage-agents/plans/PLANS-INDEX.md`), not this file |

### 12.2 The fidelity-pilot revision (findings (a) to (e))

The pilot (`manage-agents/reviews/fidelity-pilot-20261029/commands-imperatives/`) measured 1 of 10 units FAITHFUL; 7
of 10 were this family's own. The revision covers exactly these findings; other families' GAPs are theirs.

**(a) Command objects.** The first build (CI-1 to CI-5) covers these object kinds only: a declared constant by name
or by its declared spelling (labels and quoted wordings, CI-1 and CI-4), a definite or `this` phrase the scope binds
(CI-4), the proof task's matched query record (CI-2), and the arguments of one declared simple `acts@0` act (CI-5).
Every other object kind is a named GAP with its owning family. In authoring the wording stays refused as today; in
translation the unit is a GAP unit that names the kind and its owner, never a silent prose placeholder.

| Object kind | Pilot unit | GAP owner |
|---|---|---|
| that-clause object ("Check that it says what you meant.") | uweb.tour.515_1 | commands-imperatives, CI-E3 hypothesis B (its content parts stay attitudes' and presupposition's) |
| question object, polar or single-wh ("For a new word, choose what kind of thing it names."; the asked consequence of uweb.index.38_0) | uweb.index.38_0 | commands-imperatives, CI-E3 hypothesis A (mapped onto SA's question modes only if it passes) |
| multiple-wh question object ("Confirm who acts on whom for a relation.") | uweb.drafts.889_0 | question-answering (SA's question modes have no multiple-wh question) |
| confirmation of a proposed answer ("confirm" presupposes the answer it asks to confirm) | uweb.drafts.889_0 | presupposition |
| free-relative object over modalities (what is required, forbidden or permitted) | uweb.index.133_0 | question-answering (a free relative is an embedded which-all question; the modalities are W1's roles) |

**(b) Purpose and goal complements.** A purpose or goal infinitival complement ("Enter a reason to keep this unit
unresolved.", uweb.drafts.898_0, where the reason is required only in the unresolved branch) is carried as the
command's guard or recorded as a GAP, never folded into an opaque act with guard ⊤ (D6, C21). At `@0` no reader
states that guard, so the unit is a GAP naming purpose-explanation (C21); D7 does not count it (CI-4 now counts 0
segments), and CI-7a refuses it as `PurposeClause` once its command part reads.

**(c) "Then" and its antecedent.** A `Then` unit is ordered after its source antecedent, the earlier translated
instruction unit the writer names, never after the nearest earlier instruction unit of the document by default
(uweb.tour.552_0; `stepOrder`, spec lines 909-911). When the source antecedent is not a translated unit, the unit is
`ThenWithoutStep` in authoring and a GAP in translation (CI-3).

**(d) CI-3, a sequence with a refused step.** In authoring the first refusal wins, as today, and the text names the
refused step. In translation the unit keeps its formalisable steps: it is a MIXED unit in which each step that reads
is a demand part and each refused step is a GAP part with its code and its owner; the stated order keeps only the
pairs between read steps (uweb.index.38_0).

**(e) Writer rule: repeated instructions.** When two distinct source instructions translate to the same demand on
the same arguments (the pilot's u1 = u6 and u9 = u10), each unit carries a GAP naming events-time-causation (the
occasion, which stays that family's), never "GAPS none".

**Condition.** The family-scoped re-pilot on a fresh draw (the pool minus the 10 units already seen) shows at least
8 of 10 FAITHFUL. Until then the CI build rows stay held (FIDELITY_PILOT_GATE).
