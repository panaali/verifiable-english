# Commands and imperatives addressed to a reader: the item-1 statement spec (CI-0)

> Status: **statement spec against plan draft 3**, 2026-11-02 (backlog row ci-0). It applies the plan's section 12
> (synthesis round 2, N7, C12, C21, C24, N12, and the fidelity-pilot findings (a) to (e)), which governs where it
> differs from the 2026-10-28 text below (the plan's status note). `main` (`d8f58bf3b`) is merged into the branch
> (`79bc5705c`), and the stub was re-written to match this spec and re-elaborated against that build: every
> definition and `def … : Prop` statement of CI-1 to CI-7b, with the readers of CI-1 to CI-4 and CI-7a executable;
> CI-6's classifier and CI-7b's purpose reader are signatures. `spec-stub-check.sh`: lean rc 0, no error, no warning,
> no `sorry`, no axiom (stub sha256 `81e2c4ae…`). Every fixture marked computed below was re-run on that build; the
> CI-1 rows W1 to W30, F0's rows and CI-3's rows are unchanged from 2026-10-28. Section 0 records the draft-3 and
> `main` differences (S19 to S31) and the statement review's corrections (S32 to S36); section 17 lists the OPEN lines (O1 to O10), which the plan leaves open and this spec does not
> decide. Plans are frozen until Nov 12, so nothing here is new design.
>
> Earlier status: **statement spec, review-corrected draft**, 2026-10-28, branch `design/commands-imperatives` from `main` at `6d0a10526`. Docs
> only: no product code, no test, no generated file, no model call. It is item 1 (CI-0) of the plan,
> [commands-imperatives-PLAN.md](commands-imperatives-PLAN.md) (draft 2, adopted by the DRI on 2026-10-28,
> `manage-agents/reviews/dri-decisions-20261028-commands-imperatives.md` item 1; cited below as "the plan" and "DRI item
> N"). It extends `speech-acts@0` ([speech-acts.md](speech-acts.md), cited as SA) and changes none of its meaning.
>
> **How the original statements were checked.** The pre-review definitions and theorem statements were elaborated in a scratch
> Lean file, `lean/SpecStubs_commands-imperatives.lean`, with `lake env lean` against a build of this branch's base (233
> modules, Lean toolchain of `lean/lean-toolchain`). Definitions are real Lean; each theorem is stated as a `def … : Prop`
> of the same name, so those original statements type-checked and none was assumed. The stub had no `sorry`, no axiom,
> no error and no warning. CI-1's reader was implemented in the stub; the original CI-1 fixture outcomes, texts and
> counts were computed by `#eval`. The stub is not committed (CI-0's rule); its original outputs are quoted here.
> The post-review corrections in sections 6–12 were not executed by that original
> stub. A temporary patched copy was used to re-elaborate CI-3's revised reader and evaluate its sequence and limit
> counterexamples; the remaining revised rows are requirements for the named batches. Elaborating
> a statement as `Prop` checks its type, not its truth. Where this spec and the plan's Lean blocks differ, this spec
> is the one to build; section 0 records the original differences.

## 0. What changed from the plan's statements, and why

The plan's Lean blocks had never been elaborated. Elaborating them, and running the reader on the fixtures, changed
these points. Each change either keeps an existing verdict (D3, DRI item 2) or makes a statement true.

| # | Plan (draft 2) | This spec | Reason (computed in the stub unless marked) |
|---|---|---|---|
| S1 | Every reader takes `E` and `O : Overlay` | Readers take `E` only; `Context` has no `O` | english-lean folds the overlay into `E` (`Env.decode`, `Encode.lean:314`) and calls its readers with `{}` (`EnglishGrammar/Run.lean:17-20`, record L11). Passing `O` again invites a second, different overlay. The request decoder refuses an overlay fault as `english.read` does (`overlayCheck`) |
| S2 | The body matches a filled act "under `surfaceWords`" | It matches under Python's rule: the wording trimmed of ASCII whitespace (`wording_text`), then `A`-`Z` folded (`ascii_fold`) on both sides, with no other normalisation | `surfaceWords` collapses whitespace, so `Click  Ask.` (two spaces) would read; Python refuses it (W28). That is refused to read for a wording no batch adds, which DRI item 2(b) does not sign |
| S3 | `actMatches` keeps only acts whose slot 0 has the addressee's sort | `actMatches` keeps every act, as Python does. `readCommand` refuses a single reading with `UnboundSlot: you` when the scope has no addressee and `TypeMismatch: addressee` when the act's slot 0 has another sort (`addressed`) | The filter would turn Python's `AmbiguousDerivation` (two acts with one phrase and different slot-0 sorts, which W1's act identity allows, `Norms/Tree.lean:273-281`) into one reading: unsigned refused to read. The refusal texts are `checkSpeech`'s own (`SpeechActs/Tree.lean:274-276`) |
| S4 | `guard_limit`: some act match; `guard_unread`: one act match | Both need exactly one act match | Python reads the condition only after exactly one act match (`speech_english.py:240-244`); with two it refuses `AmbiguousDerivation` first |
| S5 | `readCommand_one_iff`: `withinLimits ∧ eraseDups = [r]` | Adds `addressed se sc r = true`; `readCommand_complete` gains the same hypothesis | S3 |
| S6 | (none) | New `readCommand_prefix` | The four prefix refusals come first, in Python's order |
| S7 | `candidate_reads_back` | Adds `(actVerb a).isSome`, and the match is `fold t = fold p.body` | S2; only an act with a verb is matched (`speech_english.py:134`) |
| S8 | `GuardFault.unread` from "english.read's texts" | The exact sources: the `english.read` translation row's code and text, said of "The condition" (`ofCondition`, the pattern of `VE.Question.Run.ofQuestion`); `IllTyped` when a reading does not decode closed and typed; `ConclusionWithoutPremise` for a marked reading | The plan named no source for the decode and mark cases |
| S9 | Fixture constants `Draft1`, `DocumentAssistant`, … | Lower-case names: `draft`, `assistant`, `calls`, `question1`, `meaning1`, `token1`, `reader` | The environment decoder refuses `DocumentAssistant`: "Invalid ASCII identifier" (`VE.Surface.identifier`, `Surface.lean:71`: a name begins with `a`-`z`) |
| S10 | CI-2: `Texts.lean` gains `legend`; the paraphrase comes from `Texts` | No new legend and no new paraphrase: `VE.SpeechActs.Run.legend` (`SpeechActs/Run.lean:64`) and `VE.SpeechActs.Run.paraphrase` (`:59`) already exist in Lean | One owner (DRI item 4(e): one legend, speech-acts'). The plan's CI-2 text is aligned |
| S11 (superseded by S22) | CI-2 `proofTask`: "a selected query" | The selected query must also be one of the request's query ids, or `InvalidInput: query required` | `proofTask_bound` is otherwise false |
| S12 | CI-3 `seq_eq` with `List.Forall₂` | Length and `zip` form, and each step has no condition | No Mathlib in this project; a condition inside a sequence is `ConditionScope` |
| S13 | CI-3 `stepOrder_forward` compares pairs with unit ids | Restated over the step names (`u`, or `u.1` … `u.n`), with `Nodup` | A sequence's order pairs name steps, which are not unit ids |
| S14 | CI-3 `readStep` | When one shape applies, its own outcome passes through (its refusal text included); a condition written first splits at every `, ` | Otherwise "If draft is approvable, click Ask." loses the condition's `NoDerivation` text (computed both ways) |
| S15 (superseded by S23) | CI-4 `candidate_fills` with `E.declaredSpelling O` | `E.declaredSpelling {}` | S1 |
| S16 | CI-5 `decode_acts_compatible` with `decodeNormsEnvironment j'` | `decodeNormsEnvironment j' (acts := true)`; CI-5 also passes `(acts := true)` in `decodeSpeechEnvironmentFull` | With the default, the decoder refuses an `acts@0` environment: "UnsupportedProfile: Unsupported profile acts@0"; with `(acts := true)` it decodes the same environment |
| S17 (superseded by S27) | CI-5 `command_act_simple` names "the `VE.Acts` predicate" | `VE.Acts.Lexical.joinFree` (**NEW**), factored out of the last step of `VE.Acts.Lexical.check` (`Acts/Lexical.lean:133-136`), which `check` then calls | One owner for the join test. It reads the existing `joinWords`, including `for`, without changing AP-1's verdicts |
| S18 | CI-4's third MIXED row: "change “Rule 4.” to “Rule 4 (exception to rule 1).”" | Not buildable at `@0` | A three-place act `{0} change {1} to {2}` is refused: "invalid signature: change_required" (`speech-acts@0` admits `relational-fol@0`, not `nary@0`) |

**Draft 3 and `main` (2026-11-02).** Rows S19 to S31 come from re-elaborating against plan draft 3 and `main`.

| # | Plan (draft 3) | This spec | Reason (computed in the stub unless marked) |
|---|---|---|---|
| S19 | `readUnit` (draft 2) | `readInstruction` everywhere; `commandFence_needs_context` in `VE.SpeechActs.Source` | N7 (plan 12.1). `VE.SpeechActs.Source.readUnit` is still `Source/Run.lean:62` on `main` |
| S20 | `many` bounded by `readingsBound`, the existing `64` of `Wire.lean:761` | `VE.SpeechActs.Wire.readingsBound := 64`; `manyOf` gives `many` up to 64 readings, else `limit`, in `readCommand`, in a sequence's product, in `combineShapes` and in CI-6's `classify`; new `readCommand_bound` | N7. The literal is still at `Wire.lean:761` on `main`. `manyOf` on 64 readings is `many`, on 65 `limit` (section 5, W31). `maxCandidates` stays the search cap |
| S21 | `Context.queries : List QueryRecord` | `QueryRecord` is `(q.id, q.target)` of each query `decodeDocument` decodes (`VE.SpeechActs.Query`, `Tree.lean:45`; `Wire.lean:938`) | `VE.SpeechActs.Source.QueryRecord` (`Source/Run.lean:343`) is a different structure (unit, query, certificate): `VE.Commands.QueryRecord` must not be opened beside it |
| S22 | The proof task: P through `guardOf`, one record's target, `QueryMismatch: <u>` | In that order: `limit`, the reader's refusal, `many`, then exactly one record whose target equals the reading, then exactly one proof predicate, then `checkedAddressee` | The plan's prose order. `QueryMismatch` precedes `MissingObligationRole`, so P4 (no proof predicate, no matching record) would be `QueryMismatch`; P4 here has a matching record. `<u>` and `many`'s readings are OPEN O1 and O2 |
| S23 | CI-4: "the spelling a fill reads is the lexicon's selected one, `L.spellings`" (N7), but the CI-4 block's `candidate_fills` and D8 still read `declaredSpelling` | `slotFills` reads `L.spellings` (only where the spelling differs from the name); `candidate_fills` says `(f.const, f.words) ∈ L.spellings` | Section 12 governs. Consequence: `Copy "Rule 4.".` no longer reads (the lexicon selects `"rule4"`; the display fails V6), `Copy "rule4".` reads, and so does `Review "meaning1".` over `E_web`. The label rows are unchanged |
| S24 | "`L.valid` checked first" | The request decoder refuses with english.read's own row whenever that row is `invalidGrammar`: `L.failures` or the V6 policy | `L.valid E {}` is `(L.failures E {}).isEmpty` and leaves out V6: the lexicon that selects the display `"Rule 4."` has `L.valid = true` while english.read refuses it with `InvalidGrammar: The vocabulary selection was not accepted (invalidGrammar lexicon: V6 constant rule4). No text was read.` |
| S25 | CI-2's request is `english.read`'s | Decoded as `decodeCase` decodes it on `main`: english-lean's environment is `Env.decode (decidingEnvironment environment) overlay` (jt-2c), while every identity reads the environment as written | `EnglishGrammar/Run.lean:323-325` on `main`, read, not run |
| S26 | CI-3: a `Then` unit after its named source antecedent | `StepUnit` gains `antecedent : Option String`; `stepOrder` pairs only with that earlier instruction unit; `thenWithoutStep` lists the rest | Finding (c). The authoring source of the field is OPEN O3 |
| S27 | CI-5: `VE.Acts.Lexical.joinFree` (NEW), factored out of `check` | `main` has already done the factoring: `checkWith` and `joinCheck` (`Acts/Lexical.lean:121-146`), which `check` calls. `joinFree` is only the Bool view of `joinCheck` on the act's tokens | One owner of the join test. The draft-2 stub's `joinFree` checked `and`/`or`/`nor` only; `joinCheck` reads `joinWords`, `for` included (`{0} pay for {1}` is not join-free, as AP-1 decides today) |
| S28 | CI-5's `Dispatch.lean` re-proofs at `:906`, `:1030`, `:1165` | On `main`: `rowChecks_erase` (`:972`, `simp` at `:979`), `todayGate_base` (`:1113`, `simp` at `:1160`), `gate_acts` (`:1253`, `simp only` at `:1263`); `today_speech` (`:481`) does not unfold `actsRefuses` | Read on `main`. Also `Compose/Examples.lean:275` checks `actsRefuses.length == 7`, which CI-5's removal of `speech-acts@0` makes 6: CI-5 also edits that `#guard` (not in the plan's file list) CI-5 also removes the row at `Compose/Examples.lean:267` (inside the `#guard` at `:265`) and re-pins `Service/ActsExamples.lean:196` on its new outcome (not computed here): both pin "acts@0 with speech-acts@0 is not implemented", and `Plain.run` gates through `gateOf` (`Norms/Plain.lean:218`). `ve/profile_table.json` is regenerated. |
| S29 | CI-6 waits for en-sw | en-sw has merged (`EnglishGrammar/SourceWords.lean`, no rows). The eight lexical cues fit `SourceWordRow` as `refuse` and as `readings` rows | Section 10. A row's `word` must be in normal form (`suppose`, not `Suppose`), and a `refuse` row's rewrite may not contain the cue even inside a word ("foresee" for `see`) |
| S30 | CI-6: the heading flag before `proofTask`, no cue inside P | `CI6.readInstruction` applies `headingForms` (the heading cue alone) to a proof task when the flag is set, and nothing else | N7. Statements `proofTask_no_cue`, `proofTask_heading` |
| S31 | CI-7 split into CI-7a and CI-7b | CI-7a is executable in the stub (`purposeSplit`, `purposeReadingsBy`, `partReads`, `refusePurposiveBy`), with `readStep` in `readImperative`'s place on wordings with no cue; CI-7b's readers are signatures | N7. CI-7a's text is this spec's: `PurposeClause: a command with a purpose clause` |
| S32 | The proof predicate on "`(addressee sort, query)`" (plan, CI-2's `proofTask` docstring) | The filter is `g.sorts.drop 1 == ["query"]`, slot 0 unconstrained; `checkedAddressee` then refuses a wrong or missing addressee | The plan's own P7 (a matching proof task with no addressee is `UnboundSlot: you`) needs it: with no addressee no predicate is on `(addressee sort, query)`, which would give `MissingObligationRole`. The plan says "ported from `parse_speech`", whose filter is this one (`speech_english.py:217`). So P4′ (a second proof predicate with slot 0 `service`) is `MissingObligationRole` |
| S33 | `actMatches` "without repeats (Python's `dict.fromkeys`)" | The first match per `(predicate, constants)`: two matches whose fills name the same constants by different words are one | Python's key is `(predicate, args, role)` with `args` constants (`speech_english.py:148, 234-237`). With `eraseDups` on `(name, fills)`, definites "the Desk" and "the desk" on `desk1` made "Open the desk." `many` of one command, and under CI-4 the name `notes` and its spelling "Notes" made "Look at Notes." `many`; both are `one` now (computed) |
| S34 | `hasCommandFence`: "a unit of kind `instruction`" with fence content | A unit or `MIXED` part (`VE.Discourse.Loader.partsOf`) of `metadata.units` with fence content whose kind decodes to one that `Wire.wraps` `.instruction` | A2 says a command fence is "never" taken from the payload. A quoted instruction (`["attributed", a, "says", "instruction"]`) takes command content (`Wire.lean:493`), and the wrapper's `needed` has no kind test (`Source/Run.lean:700`); `MIXED` parts are expanded by `readUnits`. Computed: plain and quoted instruction fences are command fences, an asserted one is not |
| S35 | D9: the four quotes are mapped "before every other check" | At CI-4, `trimmed` applies `typographic` first, so every reader matches the normalised wording; the three `asciiWording` callers test `asciiWording (typographic text)` | Section 8. The plan lists `Wire.lean:680` and `Source/Run.lean:686`; `Source/Run.lean:87` (`readUnit`'s unit check) is a third caller. W13 becomes `InvalidInput: no single speech-act reading` at CI-4 |
| S36 | CI-3's `ConditionScope` text (the plan, CI-3: refused "with the rewrites") | `ConditionScope: a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only` (this spec's text) | The plan fixes the content (the two rewrites), not the words. A rewrite inside one sentence is itself refused (`.seq` refuses a guarded step), so the text asks for one sentence per step; it does not say `Then`, so it assumes nothing about O3 (review two) |

## 1. CI-1: definitions

Module `VE.Commands.Read` (new), namespace `VE.Commands`; imports `VE.SpeechActs.Wire` and `VE.EnglishGrammar.Run`.
`VE.Commands.Texts` holds the codes and texts.

```lean
open VE.SpeechActs (Scope Force)
open VE.SpeechActs.Wire (SpeechEnvironment surfaceWords actVerb asciiWording decodeClosedField asciiSpace)
open VE.EnglishGrammar (Env Lexicon TranslateOutcome translateRequest fillHoles)

def maxWordingBytes : Nat := 400
def maxCandidates : Nat := 4096     -- the search cap; also the cap of the condition reader's enumeration

-- In `lean/VE/SpeechActs/Wire.lean` (CI-1, N7): the name of the existing `64` at `:761` (reading sets hold 1 to 64
-- readings); no new literal.
def VE.SpeechActs.Wire.readingsBound : Nat := 64

structure Fill where
  const : String      -- a declared constant
  words : String      -- the words that name it in the wording
  deriving DecidableEq, Repr

structure Reading where
  force : Force
  act   : String          -- the realising regulated predicate
  fills : List Fill       -- one per slot after slot 0, in slot order
  guard : VE.Formula      -- `.top` when the wording has no `, if`
  deriving DecidableEq, Repr

def Reading.command (u : String) (r : Reading) : VE.SpeechActs.Command :=
  { unit := u, force := r.force, act := r.act, args := r.fills.map (·.const), guard := r.guard }

/-- Python's `wording_text`: the wording without leading or trailing ASCII whitespace. -/
def trimmed (s : String) : String :=
  String.mk ((s.toList.dropWhile asciiSpace).reverse.dropWhile asciiSpace).reverse

/-- Python's `ascii_fold`: `A`-`Z` to `a`-`z`, nothing else. -/
def fold (s : String) : String := s.map Char.toLower

structure Parts where
  force : Force
  body : String
  condition : Option String
  deriving DecidableEq, Repr

/-- Python's `rsplit(", if ", 1)`. -/
def splitLastIf (s : String) : String × Option String :=
  match s.splitOn ", if " with
  | [x] => (x, none)
  | xs => (", if ".intercalate xs.dropLast, xs.getLast?)

/-- The prefix refusals, in Python's order (`parse_speech`). -/
def prefixRefusal (s : String) : Option (String × String) :=
  let t := trimmed s
  if !asciiWording t then some ("InvalidInput", "non-ASCII speech wording")
  else if t.isEmpty then some ("InvalidInput", "speech wording")
  else if t.startsWith "You may " then some ("PermissionNotCommand", "use an equality-guarded W1 rule")
  else if t.startsWith "Please " then some ("InvalidInput", "please needs author approval")
  else none

def parts (s : String) : Option Parts :=
  let t := trimmed s
  if (prefixRefusal s).isSome || !t.endsWith "." then none
  else
    let (plain, condition) := splitLastIf (t.dropRight 1)
    if plain.startsWith "Do not " then some ⟨.forbid, plain.drop 7, condition⟩
    else some ⟨.require, plain, condition⟩

/-- A prohibition is never `¬required` (SA 1.2). -/
def roleOf : Force → VE.Norms.Role
  | .require => .obligation
  | .forbid => .permission

/-- The fills of a slot of sort `srt`: each constant of `srt` by its name, then each definite phrase bound to it
(Python's `_command_candidates`). CI-4 adds the lexicon's selected spelling (S23). -/
def slotFills (se : SpeechEnvironment) (sc : Scope) (srt : String) : List Fill :=
  (se.ne.rv.vocabulary.constants.filter (·.2 == srt)).flatMap fun (c, _) =>
    ⟨c, c⟩ :: (sc.definites.filter (·.2 == c)).map fun (p, _) => ⟨c, p⟩

/-- The act phrase after `{0} ` with hole `{i}` filled by `(fs[i-1]).words`, through english-lean's `fillHoles`
(`Lexicon.lean:222`); `none` unless the holes are exactly `1` to `fs.length`. Python: `act[4:].format(None, …)`. -/
def filled (act : String) (fs : List Fill) : Option String :=
  let (hs, t) := fillHoles (act.drop 4) fun k => ((fs[k - 1]?).map (·.words)).getD ""
  if hs.all (fun k => decide (1 ≤ k ∧ k ≤ fs.length)) &&
      (List.range fs.length).all (fun i => hs.contains (i + 1)) then some t else none

def tuples : List (List Fill) → List (List Fill)
  | [] => [[]]
  | xs :: rest => xs.flatMap fun x => (tuples rest).map (x :: ·)

/-- The regulated predicates a command can name: a role that is not `plain`, and an act with a verb. -/
def commandable (g : VE.Norms.Regulated) : Bool := g.role != .plain && (g.act.bind actVerb).isSome

/-- Every phrase match of a body, whatever the role. -/
def phraseMatches (se : SpeechEnvironment) (sc : Scope) (body : String) : List (VE.Norms.Regulated × List Fill) :=
  (se.ne.regulated.filter commandable).flatMap fun g =>
    let a := g.act.getD ""
    (tuples ((g.sorts.drop 1).map (slotFills se sc))).filterMap fun fs =>
      match filled a fs with
      | some t => if fold t == fold body then some (g, fs) else none
      | none => none

/-- The matches whose role is the force's, the first per `(predicate, constants)` (Python's `dict.fromkeys` on
`(predicate, args, role)`, `speech_english.py:234-237`; S33). -/
def actMatches (se : SpeechEnvironment) (sc : Scope) (s : String) : List (String × List Fill) :=
  match parts s with
  | none => []
  | some p => ((phraseMatches se sc p.body).filter (·.1.role == roleOf p.force)).foldl (fun acc (g, fs) =>
      if acc.any (fun (a, gs) => a == g.name && gs.map (·.const) == fs.map (·.const)) then acc
      else acc ++ [(g.name, fs)]) []

/-- Why a condition gave no single guard. -/
inductive GuardFault
  | ambiguous (gs : List VE.Formula)     -- two or more distinct guards; every one becomes a reading
  | limit                                -- the enumeration stopped at its budget or its cap
  | unread (code text : String)          -- english-lean's refusal, its code and text
  deriving Repr, DecidableEq

/-- english-lean's text of a sentence-0 refusal, said of the condition (as `VE.Question.Run.ofQuestion`). -/
def ofCondition (text : String) : String := text.replace "Sentence 1 " "The condition "

/-- The decision on one translation outcome of the sentence `c ++ "."`:
an incomplete set or `.budget` is `limit`; a marked reading is `ConclusionWithoutPremise`; a reading that does not
decode closed and typed over the environment is `IllTyped`; otherwise the distinct guards: one is `.ok`, two or more
`ambiguous`, none (and every other outcome) the code and text of `english.read`'s translation row for the sentence. -/
def guardOfOutcome (se : SpeechEnvironment) (E : Env) (L : Lexicon) (c : String) :
    TranslateOutcome → Except GuardFault VE.Formula
  | .readings rs complete =>
    if !complete then .error .limit
    else if rs.any (·.2.1) then
      .error (.unread "ConclusionWithoutPremise" (ofCondition (VE.EnglishGrammar.Run.noPremiseText 0)))
    else match rs.mapM (fun r => decodeClosedField se.ne.rv.environment r.1.encode) with
      | .error _ => .error (.unread "IllTyped" (ofCondition (VE.EnglishGrammar.Run.illTypedText (some 0))))
      | .ok gs => match gs.eraseDups with
        | [g] => .ok g
        | [] =>
          let fs := VE.EnglishGrammar.Run.translation ⟨E, {}, L, none, []⟩ maxCandidates (c ++ ".")
          .error (.unread (strField fs "code") (ofCondition (strField fs "text")))
        | gs => .error (.ambiguous gs)
  | .budget => .error .limit
  | _ =>
    let fs := VE.EnglishGrammar.Run.translation ⟨E, {}, L, none, []⟩ maxCandidates (c ++ ".")
    .error (.unread (strField fs "code") (ofCondition (strField fs "text")))

def guardOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) :
    Except GuardFault VE.Formula :=
  guardOfOutcome se E L c (translateRequest E {} L maxCandidates b (c ++ "."))

def guardsOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) : List VE.Formula :=
  match guardOf se E L b c with
  | .ok g => [g]
  | .error (.ambiguous gs) => gs
  | .error _ => []

def candidates (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) :
    List Reading :=
  match parts s with
  | none => []
  | some p =>
    let gs := match p.condition with
      | none => [VE.Formula.top]
      | some c => guardsOf se E L b c
    (actMatches se sc s).flatMap fun (a, fs) => gs.map fun g => ⟨p.force, a, fs, g⟩

/-- The fill tuples the matcher tries: over the commandable predicates, the product of their slots' fill counts. -/
def tupleCount (se : SpeechEnvironment) (sc : Scope) : Nat :=
  ((se.ne.regulated.filter commandable).map fun g =>
    ((g.sorts.drop 1).map fun srt => (slotFills se sc srt).length).foldl (· * ·) 1).sum

def withinLimits (se : SpeechEnvironment) (sc : Scope) (s : String) : Bool :=
  (trimmed s).utf8ByteSize ≤ maxWordingBytes && tupleCount se sc ≤ maxCandidates

/-- The addressee is bound and has the sort of the act's slot 0. -/
def addressed (se : SpeechEnvironment) (sc : Scope) (r : Reading) : Bool :=
  match sc.addressee, se.ne.regulated.find? (·.name == r.act) with
  | some (srt, _), some g => g.sorts.head? == some srt
  | _, _ => false

inductive Outcome
  | one (r : Reading)
  | many (rs : List Reading)       -- 2 to 64 readings: speech-acts' candidate pipeline in translation (D11);
                                   -- `AmbiguousDerivation` in authoring
  | refused (code text : String)   -- a code of `Texts.codeClasses`, or english-lean's for the condition
  | limit                          -- "VE stopped reading this command at its work limit."
  deriving Repr, DecidableEq

def coordinated (t : String) : Bool := (t.splitOn " and ").length > 1 && !t.startsWith "Do not "

/-- The refusal of a wording with no candidate, in Python's order (section 3). -/
def refusal (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : Outcome :=
  let t := trimmed s
  let other : Outcome := if coordinated t then .refused "CoordinatedActs" "split into two commands"
    else .refused "InvalidInput" "no single speech-act reading"
  match parts s with
  | none => other
  | some p =>
    match actMatches se sc s with
    | [] =>
      match (phraseMatches se sc p.body).find? (·.1.role != roleOf p.force) with
      | some (g, _) =>
        .refused (if p.force = .require then "MissingObligationRole" else "MissingPermissionRole") (g.act.getD g.name)
      | none => other
    | [_] =>
      match p.condition with
      | some c =>
        match guardOf se E L b c with
        | .error .limit => .limit
        | .error (.unread code text) => .refused code text
        | _ => other
      | none => other
    | _ => .refused "AmbiguousDerivation" "multiple declared acts match"

/-- Shared by the ordinary command and the proof task; a single reading still needs an addressed slot 0. -/
def checkedAddressee (se : SpeechEnvironment) (sc : Scope) (r : Reading) : Outcome :=
  if addressed se sc r then .one r
  else if sc.addressee.isNone then .refused "UnboundSlot" "you"
  else .refused "TypeMismatch" "addressee"

/-- `many` holds at most the speech wire's bound; more is `limit` (N7). -/
def manyOf (rs : List Reading) : Outcome :=
  if rs.length ≤ VE.SpeechActs.Wire.readingsBound then .many rs else .limit

def readCommand (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : Outcome :=
  match prefixRefusal s with
  | some (code, text) => .refused code text
  | none =>
    if !withinLimits se sc s then .limit
    else match (candidates se sc E L b s).eraseDups with
      | [r] => checkedAddressee se sc r
      | [] => refusal se sc E L b s
      | rs => manyOf rs

namespace Texts
/-- Every code the reader writes, with its class: `VEError`, the class Python raises for each today. -/
def codeClasses : List (String × String) :=
  [("InvalidInput", "VEError"), ("PermissionNotCommand", "VEError"), ("UnboundSlot", "VEError"),
   ("TypeMismatch", "VEError"), ("MissingObligationRole", "VEError"), ("MissingPermissionRole", "VEError"),
   ("AmbiguousDerivation", "VEError"), ("CoordinatedActs", "VEError")]
def limitText : String := "VE stopped reading this command at its work limit."
/-- Local command codes first; english-lean owns condition and proof-sentence codes. -/
def classOf (code : String) : Option String :=
  (codeClasses.lookup code).orElse fun _ => VE.EnglishGrammar.Run.codeClasses.lookup code
end Texts

```

`strField fs k` is the string field `k` of a row (`""` when absent). `candidates` is a specification: the implementation
may match the act's literal words first and fill the gaps, provided it is proved equal (plan, risk 2).

**What the reader shows.** The answer carries speech-acts' scope legend and its rendering of the selected command
(section 8 specifies the display input). CI-1 and CI-2 write no second legend or paraphrase. An ambiguous act match
in authoring says `AmbiguousDerivation: multiple declared acts match`; an ambiguous condition uses english-lean's
`Ambiguous` text for that condition. The encoder identifies a condition ambiguity when every reading has the same
`(act, fills)` and at least two distinct guards; it uses the condition's `english.read` translation row, with
`ofCondition` changing `Sentence 1` to `The condition`. Other `many` command answers use the act-match text.
In translation, `rs` goes through speech-acts' candidate pipeline (`Source/Run.lean:141-187`, `Wire.lean:749-780`),
one `command` content per reading (D11; section 12 maps every alternative shape).

## 2. The English: each wording and its one reading

Every wording below has exactly one reading, conditional on the legend, which the reader sees first. The paraphrases are
the outputs of `VE.SpeechActs.Run.paraphrase` and `legend` on `E_web` (section 4), computed in the stub.

| Wording | When it reads | The one reading, as the reader is shown it |
|---|---|---|
| `<Act phrase after slot 0, slots filled>.` ("Click Check rule conflict.") | exactly one declared obligation act, its slots filled by a constant's name or a bound definite phrase, equals the wording up to `A`-`Z` case | "In this task, you are required to click Check rule conflict." |
| `Do not <same shape>.` ("Do not share the token.") | the same, on a permission act | "In this task, you are not permitted to share the token." |
| `<command>, if <condition>.` ("Click Check rule conflict, if draft is approved.") | the command reads, and english-lean reads `<condition>.` with exactly one meaning | "In this task, you are required to click Check rule conflict, where the stated condition holds." The guard is `approved(draft)` |
| `Prove that <sentence> using these premises.` (CI-2) | english-lean reads `<sentence>.` with one meaning, exactly one of the request's query records has that meaning as its target, and exactly one obligation predicate has the act `{0} submit a proof of {1}` on `(…, query)` | a command on that predicate with the matched record's query as its only argument (SA 1.4) |
| the legend | always | "This document is task webapp-copy.", "In this task, you are reader.", then one line per definite in phrase order: "In this task, the document assistant control is assistant." … "In this task, the token is token1." |

**What a condition may say (computed, section 4, W19 to W21).** A condition is one sentence of english-lean over the
environment's lexicon. It names a constant by english-lean's spelling: a name that is one lower-case word as it is
(`draft`; "Draft" also reads, W21), any other name quoted (`"token1"`), or a declared display. **It cannot use the scope's
definite phrases**: "…, if the reading is approved." has no reading (W20). A negative needs a declared negative wording
or "it is not the case that": over `E_web`, "draft is not approved" has no reading, and "it is not the case that draft
is approved" reads `¬approved(draft)`. Python's condition reader today, P0's English (`_formula`,
`speech_english.py:15-20`), reads over the same producer's selections (`english.py:390-527`, which english-lean's
`policyPredicate` and `policySpellings` mirror), so these limits should not be new; this was read from the code, not
run, and CI-2's A/B confirms it.

## 3. CI-1: statements

```lean
-- In every statement: (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String).

/-- The prefix refusals come first, in Python's order. -/
theorem readCommand_prefix (code text : String) (h : prefixRefusal s = some (code, text)) :
    readCommand se sc E L b s = .refused code text

theorem readCommand_one_iff (r : Reading) :
    readCommand se sc E L b s = .one r ↔
      withinLimits se sc s = true ∧ (candidates se sc E L b s).eraseDups = [r] ∧ addressed se sc r = true

theorem readCommand_many (rs : List Reading) :
    readCommand se sc E L b s = .many rs ↔
      withinLimits se sc s = true ∧ rs = (candidates se sc E L b s).eraseDups ∧ 2 ≤ rs.length ∧
        rs.length ≤ VE.SpeechActs.Wire.readingsBound

/-- Completeness: a wording with a candidate that fits the addressee is never refused. -/
theorem readCommand_complete (r : Reading) (hl : withinLimits se sc s = true)
    (hr : r ∈ candidates se sc E L b s) (ha : addressed se sc r = true)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    readCommand se sc E L b s = .one r ∨ ∃ rs, readCommand se sc E L b s = .many rs ∧ r ∈ rs

/-- Over the speech wire's bound, `limit` (N7): never a refusal and never a truncated `many`. -/
theorem readCommand_bound (hp : prefixRefusal s = none) (hl : withinLimits se sc s = true)
    (hn : VE.SpeechActs.Wire.readingsBound < (candidates se sc E L b s).eraseDups.length) :
    readCommand se sc E L b s = .limit

/-- Every candidate is the wording: its act, with a verb, filled by its fills, is the body up to `A`-`Z` case. -/
theorem candidate_reads_back (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∃ p g a t, parts s = some p ∧ p.force = r.force ∧ g ∈ se.ne.regulated ∧ g.name = r.act ∧
      g.role = roleOf r.force ∧ g.act = some a ∧ (actVerb a).isSome ∧ filled a r.fills = some t ∧
      fold t = fold p.body

theorem candidate_guard (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    match (parts s).bind (·.condition) with
    | none => r.guard = .top
    | some c => r.guard ∈ guardsOf se E L b c

/-- An ambiguous condition is never a silent choice: every guard is a reading. -/
theorem guard_ambiguous (c : String) (gs : List VE.Formula) (m : String × List Fill)
    (hl : withinLimits se sc s = true) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error (.ambiguous gs)) (hm : m ∈ actMatches se sc s)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    ∃ rs, readCommand se sc E L b s = .many rs ∧ ∀ g ∈ gs, ∃ r ∈ rs, r.guard = g

/-- Exhaustion is `limit`, never a refusal and never "no reading" (verdicts are three-valued). -/
theorem guard_limit (c : String) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error .limit) (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .limit

/-- An unread condition refuses with english-lean's code and text. -/
theorem guard_unread (c code text : String) (hl : withinLimits se sc s = true)
    (hc : (parts s).bind (·.condition) = some c) (hg : guardOf se E L b c = .error (.unread code text))
    (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .refused code text

/-- A fill is a constant's own name or a phrase the scope binds to it (CI-4 adds the spelling). -/
theorem candidate_fills (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∀ f ∈ r.fills, f.words = f.const ∨ (f.words, f.const) ∈ sc.definites

/-- A read command passes the semantic core's own check in every speech document over the same decoded environment
with a valid scope. -/
theorem readCommand_typed (j : Lean.Json) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r)
    (hE : D.E = se.ne.rv.environment) (hS : D.scope = sc) (hR : D.regulated = se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true

/-- Every refusal names a classed code, or is english-lean's refusal of the condition. -/
theorem refused_classed (code text : String) (h : readCommand se sc E L b s = .refused code text) :
    (Texts.classOf code).isSome = true
```

`refused_classed` needs the condition reader's fallback, which re-reads the sentence at `workBudget` for its code
and text (`guardOfOutcome`, `EnglishGrammar/Run.lean:517`), to agree with the read at `b`: `translation`'s `one` row
has no code. `VE.Grammar.parse_mono` (`Grammar/TableProofs.lean:109`) rules that row out (the re-read gives the same
empty set, or `.budget`, whose code `Budget` is classed, `Run.lean:116`); CI-1's proof uses it. Where `b` comes from
is OPEN O7.

`readCommand_typed` needs `hd`: `commandOk` checks `D.E.predicates c.act == some r.sorts` and the fills' sorts
(`SpeechActs/Tree.lean:212-220`), which hold for the regulated declarations and constants of a decoded environment and
not for an arbitrary `se`. `scopeOk D` gives the addressee's typing; `addressed` (inside `one`) gives slot 0's sort; the
guard is closed and typed because `decodeClosedField` checks it (`Route/Wire.lean:548`). The plan's alternative, a
`commandOk` filter on the candidates, is not taken: it would report a typing fault as "no reading".

## 4. CI-1: diagnostics, in order, with their exact texts

The relayed message is `<code>: <text>`, byte-identical to Python's where Python has the case.

| # | When | Outcome |
|---|---|---|
| 1 | the trimmed wording holds a non-ASCII character | `InvalidInput: non-ASCII speech wording` |
| 2 | it is empty | `InvalidInput: speech wording` |
| 3 | it begins `You may ` | `PermissionNotCommand: use an equality-guarded W1 rule` |
| 4 | it begins `Please ` | `InvalidInput: please needs author approval` |
| 5 | it is over 400 bytes, or the fill tuples exceed 4,096 | `limit`: "VE stopped reading this command at its work limit." |
| 6 | exactly one reading, and the scope has no addressee | `UnboundSlot: you` |
| 7 | exactly one reading, and the act's slot 0 is not the addressee's sort | `TypeMismatch: addressee` |
| 8 | two or more readings, at most 64 (more: `limit`, as row 5) | `many`; authoring uses `AmbiguousDerivation: multiple declared acts match` for distinct acts and english-lean's `Ambiguous` text for distinct guards |
| 9 | no reading, no final `.` | as row 13 or 14 |
| 10 | no act of the force's role matches, but one of the other role does | `MissingObligationRole: <act>` for a requirement, `MissingPermissionRole: <act>` for a prohibition; `<act>` is the first such act in the environment's (code point) order of predicate names |
| 11 | two or more act matches, and the condition gave no guard | `AmbiguousDerivation: multiple declared acts match` (Python reads no condition then) |
| 12 | one act match, and the condition: | exhausted: `limit`; unread: english-lean's code and text, said of "The condition" |
| 13 | otherwise, with ` and ` in the trimmed wording and no leading `Do not ` | `CoordinatedActs: split into two commands` |
| 14 | otherwise | `InvalidInput: no single speech-act reading` |

Rows 6, 7 and 11 are where the order differs from Python's single pass: Python reads a command without checking the
addressee and leaves rows 6 and 7 to `checkSpeech` (`SpeechActs/Tree.lean:274-276`), which gives the same two texts for
an active unit. For a dormant (quoted) unit Python reads the command and Lean refuses it: class b2 (DRI item 2(b)). Row
10's "first" act is Lean's order, which may differ from Python's dict order when two wrong-role acts match: an R2 row
(fault order) if the A/B finds one.

## 5. CI-1: fixtures (all computed)

`E_web`: profiles `norms@0`, `relational-fol@0`, `speech-acts@0`; sorts `user`, `control`, `ledger`, `text`, `reading`,
`token`; task `webapp-copy`; addressee `(user, reader)`; constants `reader : user`, `draft : reading`, `assistant :
control`, `calls : ledger`, `question1 : text`, `meaning1 : text`, `token1 : token`; definites "the document assistant
control" ↦ `assistant`, "the meaning" ↦ `meaning1`, "the private server calls ledger" ↦ `calls`, "the question" ↦
`question1`, "the token" ↦ `token1`; obligations (default deny) `click_check_required` `{0} click Check rule conflict`,
`click_review_required` `{0} click Review meaning`, `click_ask_required` `{0} click Ask`, `choose_vocabulary_required`
`{0} choose a listed rule vocabulary`, `choose_revision_required` `{0} choose a unit revision to restore`,
`use_required(user, control)` `{0} use {1}`, `check_required(user, ledger)` `{0} check {1}`, `write_required(user,
text)` `{0} write {1} as a statement`, `review_required(user, text)` `{0} review {1}`, `review_meaning_required`
`{0} review the meaning`; the permission (default allow) `share_permitted(user, token)` `{0} share {1}`; the predicate
`approved(reading)` "{0} is approved". The lexicon is the one Python's producer selects (english-lean's V6 policy:
`policyNouns`, `policyPredicate`, `policySpellings`), with one letter per sort; it passes V1 to V6 (no failure). Budget
`workBudget` (2,100,000) unless a row says otherwise. The fill tuples of `E_web` number **20**.

| Row | Wording | Computed outcome |
|---|---|---|
| W1 | "Click Check rule conflict." (tour.js) | `one`: require, `click_check_required`, no fills, `.top` |
| W2 | "Click Review meaning." (tour.js, two segments) | `one`: `click_review_required` |
| W3 | "Choose a listed rule vocabulary." (app.js, two segments) | `one`: `choose_vocabulary_required` |
| W4 | "Choose a unit revision to restore." (app.js) | `one`: `choose_revision_required` |
| W5 | "Use the document assistant control." (app.js) | `one`: `use_required`, fill (`assistant`, "the document assistant control") |
| W6 | "Check the private server calls ledger." (app.js) | `one`: `check_required`, fill (`calls`, "the private server calls ledger") |
| W7 | "Write the question as a statement." (index.html) | `one`: `write_required`, fill (`question1`, "the question") |
| W8 | "Click Check rule conflict, if draft is approved." | `one`: `click_check_required`, guard `approved(draft)` |
| W9 | "Do not share the token." | `one`: forbid, `share_permitted`, fill (`token1`, "the token") |
| W10 | "Review the meaning." | `many`, two readings: `review_meaning_required`; `review_required` with (`meaning1`, "the meaning") |
| W11 | "Click Use this wording under the one you mean." (tour.js) | `InvalidInput: no single speech-act reading` |
| W12 | "Choose authoring or translation mode." (app.js) | `InvalidInput: no single speech-act reading` (SA 2.3's ruling) |
| W13 | "Open “Vocabulary & small world” to fix it." (app.js) | `InvalidInput: non-ASCII speech wording` |
| W14 | "Then click Ask." (tour.js) | `InvalidInput: no single speech-act reading` (CI-3 reads it) |
| W15 | "You may close the desk." | `PermissionNotCommand: use an equality-guarded W1 rule` |
| W16 | SA section 9's command rows over F0 | the table below |
| W17 | an ambiguous condition | see below: no condition over `E_web` has two derivations |
| W18 | W8 with budget 0 | `limit` |
| W19 | "Click Check rule conflict, if draft is approvable." | `NoDerivation: The condition has no reading with the current vocabulary. Unknown English phrase 'is approvable'. Nearest declared wordings: 'is approved'; 'assistant'; 'calls'.` |
| W20 | "Click Check rule conflict, if the reading is approved." | `NoDerivation: The condition has no reading with the current vocabulary. Unknown English phrase 'the reading'. Nearest declared wordings: 'reading'; '"meaning1"'; 'reader'.` |
| W21 | "Click Check rule conflict, if Draft is approved." | `one`, guard `approved(draft)` (english-lean reads "Draft" as `draft`) |
| W22 | "Do not click Ask." | `MissingPermissionRole: {0} click Ask` |
| W23 | "Share the token." | `MissingObligationRole: {0} share {1}` |
| W24 | "Please click Ask." | `InvalidInput: please needs author approval` |
| W25 | "Click Ask and Review meaning." | `CoordinatedActs: split into two commands` |
| W26 | "Do not click Ask and Review meaning." | `InvalidInput: no single speech-act reading` (Python's `Do not` exception to row 13) |
| W27 | "  click ask.  " | `one`: `click_ask_required` (trimmed; case folded) |
| W28 | "Click  Ask." (two spaces) | `InvalidInput: no single speech-act reading` (S2: whitespace is not collapsed) |
| W29 | "Click Ask" (no period) | `InvalidInput: no single speech-act reading` |
| W30 | "" | `InvalidInput: speech wording` |
| W32 | "Open the desk." over F0 with definites "the Desk" and "the desk" on `desk1` (S33) | `one`: `open_required`, (`desk1`, "the Desk"); with ", if check is disabled." the same, guarded `disabled(check)` (Python reads the condition: one act match) |
| W31 | `manyOf` on constructed candidate lists (N7's bound) | 2 and 64 readings: `many`; 65: `limit` (no fixture environment reaches 65 candidates; the decision is checked on the list, as W17's is) |

**W16, SA section 9 over F0.** F0 with lower-case names (S9): sorts `user`, `control`, `token`, `desk`, `service`,
`thing`, `query`; constants `alice`, `check`, `token1`, `desk1`, `atlas`, `beacon`, `tom`, `q1`; SA 3.1's regulated
declarations (`click`, `share`, `submit a proof of`) plus `open_required`/`open_permitted`; addressee `(user, alice)`;
definites "the token", "the desk", "the writing desk". Lexicon V1 to V6: no failure. Fill tuples: **12**.

| SA fixture | Wording | Computed outcome |
|---|---|---|
| (α) | "Click Check." | `one`: `click_required`, fill (`check`, "check") |
| (β) | "Do not share the token." | `one`: forbid, `share_permitted`, (`token1`, "the token") |
| (γ) | "Open the desk." / "Do not open the desk." | `one`: `open_required` / forbid `open_permitted`, (`desk1`, "the desk") |
| (δ) | "Click Check, if check is disabled." | `one`: `click_required`, guard `disabled(check)` |
| (ξ) | "Click Check." with no addressee | `UnboundSlot: you` |
| (ξ) | "Share the token." without the definite "the token" | `InvalidInput: no single speech-act reading` |
| (ξ) | "Share the token." with it | `MissingObligationRole: {0} share {1}` |
| (π) | "Click Check and save." | `CoordinatedActs: split into two commands` |
| (ρ) | "You may close the desk." | `PermissionNotCommand: use an equality-guarded W1 rule` |
| (σ) | "Please click Check." | `InvalidInput: please needs author approval` |
| (αα) | "Open the writing desk." | `one`: `open_required`, (`desk1`, "the writing desk") |
| (αα) | "Choose authoring or translation mode." | `InvalidInput: no single speech-act reading` |
| S3 | "Click Check." with addressee `(service, atlas)` | `TypeMismatch: addressee` |
| (μ) | "Prove that tom is an animal using these premises." | `readCommand`: `InvalidInput: no single speech-act reading`; the proof task is `readInstruction`'s (CI-2, P1) |

**W17.** Fourteen conditions were tried over `E_web`'s lexicon (coordinations of `and` and `or`, quantifiers,
negation, `if … then`, modal forms). None has two derivations: each reads with one meaning or has none. english-lean's
V4 refuses every shared selection except two modal predicates' shared modal form (`Lexicon.lean:489-492`), and two
such predicates differ in their argument sorts (W1's act identity), which the grammar's actions separate. So W17 checks
the decision rule on a constructed translation outcome: `guardOfOutcome` on the complete set {`approved(draft)`,
`¬approved(draft)`} is `.error (.ambiguous [approved(draft), ¬approved(draft)])`, and on the same set marked incomplete
it is `.error .limit`. What `readCommand` then does is `guard_ambiguous` and `guard_limit`, proved in CI-1. W17's
`#guard` in `Examples.lean` is on `guardOfOutcome`.

**Both directions of each iff.** `readCommand_one_iff`: W1 has 1 candidate, within the limits and addressed, and reads
`one`; W10 has 2 candidates and does not; "Click Check." under addressee `(service, atlas)` has 1 candidate that is not
addressed, and does not (`TypeMismatch`); with no addressee, 1 candidate, not addressed (`UnboundSlot`).
`readCommand_many`: W10 (2 candidates, `many`) and W1 (1 candidate, not `many`); the bound's direction is W31.

**The web fixture.** The 59 segments of R 2.1 are `#guard`s with their outcome; the measured number is the count of
`one` rows. W1 to W7 are nine segments (W2 and W3 twice each in the pinned catalogue, `1ff7a7b72`), all `one`. Their
bytes, summed by program: **273 B**, equal to R's hand count. The other 50 segments are CI-1's to pin; no number other
than these nine is claimed before CI-8 measures.

**Seeded bugs (CI-1):** `roleOf .forbid = .obligation` (fails W9 and W22); `candidates` keeping only the first fill
tuple (fails W10); dropping the guard (fails W8); `guardOfOutcome` keeping only the first guard (fails W17); `limit`
mapped to a refusal (fails W18); `fold` replaced by `surfaceWords` (fails W28); the addressee check dropped (fails
S3's `TypeMismatch` row); `manyOf` truncating to 64 readings instead of `limit` (fails W31).

## 6. CI-2: the reading context, the proof task, the one entry

Module `VE.Commands.Run` (new).

```lean
/-- A decoded query record of the request (N7): `(q.id, q.target)` of a query `decodeDocument` decodes
(`VE.SpeechActs.Query`, `Tree.lean:45`; the query loop at `Wire.lean:938`). Premise ids stay with `decodeDocument`. -/
structure QueryRecord where
  id : String
  target : VE.Formula
  deriving DecidableEq, Repr

/-- The reading context of one command fence (A2). Every field is required: a request or a payload without it is
`InvalidInput: command reading context`. -/
structure Context where
  se : SpeechEnvironment
  sc : Scope                   -- the effective scope (the environment's, with the document's bindings)
  E : Env                      -- english-lean's environment, the overlay applied (`Env.decode`, S25)
  L : Lexicon
  b : Nat
  queries : List QueryRecord   -- the request's decoded query records: the proof task's target context

def proofAct : String := "{0} submit a proof of {1}"   -- today `PROOF_TASK_ACT`, `ve/speech_acts.py:15`

/-- A proof task's sentence, between `Prove that ` and ` using these premises.`; `none` otherwise. -/
def proofSentence (s : String) : Option String :=
  let t := trimmed s
  if (prefixRefusal s).isNone && t.startsWith "Prove that " && t.endsWith " using these premises." then
    some ((t.drop "Prove that ".length).dropRight " using these premises.".length)
  else none

def ofPart (part text : String) : String := text.replace "The condition " (part ++ " ")

/-- OPEN O2 (section 17): the readings `many` lists for an ambiguous P. -/
opaque proofMany : Context → List VE.Formula → Outcome

/-- The proof task (SA 2.1; N7), in the plan's order: P through `guardOf` (budget `limit`, unread the reader's
refusal said of "The sentence to prove", ambiguous `many`); exactly one record whose target equals P's reading,
otherwise `QueryMismatch: <u>` (OPEN O1: the unit id is not in `Context`); exactly one obligation predicate with the
act `{0} submit a proof of {1}` on `(…, query)`, otherwise `MissingObligationRole`; then `checkedAddressee`, with the
matched record's id as the only fill and `.top` as the guard. `none` when the wording is not a proof task. The
`follows` loop stays question-answering's. -/
def proofTask (ctx : Context) (s : String) : Option Outcome :=
  match proofSentence s with
  | none => none
  | some p => some <|
    match guardOf ctx.se ctx.E ctx.L ctx.b p with
    | .error .limit => .limit
    | .error (.unread code text) => .refused code (ofPart "The sentence to prove" text)
    | .error (.ambiguous gs) => proofMany ctx gs
    | .ok φ =>
      match ctx.queries.filter (·.target == φ) with
      | [q] =>
        match ctx.se.ne.regulated.filter (fun g => g.role == .obligation && g.act == some proofAct &&
            g.sorts.drop 1 == ["query"]) with
        | [g] => checkedAddressee ctx.se ctx.sc ⟨.require, g.name, [⟨q.id, q.id⟩], .top⟩
        | _ => .refused "MissingObligationRole" proofAct
      | _ => .refused "QueryMismatch" "<u>"

/-- The one public entry: the `english.command` mode and the source wrapper both call it. -/
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

/-- The request: `english.read`'s (`id`, `environment`, `overlay`?, `lexicon`, `cap`), decoded as `decodeCase`
decodes it on `main` (S25), the wording, the unit, and the request's query records. An overlay fault is refused as
`english.read` refuses it, and so is a lexicon english.read refuses (`invalidGrammar`: `L.failures` or the V6
policy, S24), before any wording is read. Python sends no proof-task selection: Lean derives the match. -/
structure Request where
  id : String
  unit : String
  ctx : Context
  s : String

def Run.decodeRequest (j : Lean.Json) : Except String Request

/-- The answer: the wording and `readInstruction`'s outcome. For `one`: the command object (SA 3.2), each fill's
words with its span in code points of the wording (none for the proof task's query), the paraphrase
(`VE.SpeechActs.Run.paraphrase`) and the legend (`VE.SpeechActs.Run.legend`). For `many`: every reading. For
`refused`: the code, its class and the text. The request id and the command unit are echoed from `q`. -/
def Run.encode (q : Request) (o : Outcome) : Lean.Json

def Run.caseReported (j : Lean.Json) : Lean.Json :=
  match Run.decodeRequest j with
  | .ok q => Run.encode q (readInstruction q.ctx q.s)
  | .error e => Lean.Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str e)]

theorem runMode_englishCommand (j : Lean.Json) : runMode .englishCommand j = VE.Commands.Run.caseReported j := rfl

/-- The encoder theorem. -/
theorem caseReported_eq (j : Lean.Json) (q : Request) (hd : Run.decodeRequest j = .ok q) :
    Run.caseReported j = Run.encode q (readInstruction q.ctx q.s)

/-- Each public-entry refusal has a diagnostic class, including proof-task and condition codes. -/
theorem readInstruction_refused_classed (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = .refused code text) : (Texts.classOf code).isSome = true

/-- The typing theorem covers the whole entry, the proof task included (N7). -/
theorem readInstruction_typed (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : readInstruction ctx s = .one r)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true

-- In `lean/VE/SpeechActs/Source/Run.lean`, beside `decodeSpeechSource` (N7), not in `VE.Commands`.
/-- A2: a command fence is never taken from the payload: one without the reading context is refused. -/
theorem commandFence_needs_context (payload evidence : Lean.Json) (h : hasCommandFence payload = true)
    (hc : (payload.getObjVal? "reading_context").toOption = none) :
    ∃ e, VE.SpeechActs.Source.decodeSpeechSource payload evidence = .error e
```

`Texts.codeClasses` gains `("QueryMismatch", "VEError")` in CI-2. `hasCommandFence payload` is true when a unit or
`MIXED` part (`VE.Discourse.Loader.partsOf`) of the payload's `metadata.units` has fence content and its kind decodes
to one that `Wire.wraps` `.instruction` (S34). This set is also the plan's "every command fence": with the reading
context each one the wrapper resolves (`needed`, `Source/Run.lean:700`, which skips an authored choice) is read by
`readInstruction`, and a supplied `resolved_fences` command that differs is `InvalidInput: resolved speech fences`. In the stub, `runMode` is modelled by a
one-constructor mode type and `runMode_englishCommand` is proved by `rfl`; `decodeRequest` and `encode` are
signatures (`opaque`). The encoder must use `q.id`, `q.unit`, `q.ctx.sc` and `q.ctx.E` when writing the echoed id,
command unit, legend and paraphrase; its display function is `q.ctx.E.declaredSpelling {}`. It cannot recover them
from the wording or outcome. `readInstruction_typed` adds `hq` to `readCommand_typed`'s hypotheses: `commandOk` checks
each argument's sort (`Tree.lean:218`), and `proofTask` fills the `query` slot with the record's id, so the theorem is
false for a record whose id is not a declared constant of sort `query`. The statement is proved as written; whether a decoded
request or document always satisfies `hq` is CI-2's to check (read, not run). `hq` changes no outcome.

**Fixtures (computed, F0).** `atlasReviewed` is `reviewed(atlas)`, `beaconReviewed` is `reviewed(beacon)`.

| Row | Records | Wording | Outcome |
|---|---|---|---|
| P1 | (`q1`, `atlasReviewed`) | "Prove that tom is an animal using these premises." | `NoDerivation: The sentence to prove has no reading with the current vocabulary. Unknown English phrase 'is an animal'. Nearest declared wordings: 'is classified as "animal"'; 'alice'; 'atlas'.` |
| P1′ | (`q1`, `atlasReviewed`) | "Prove that atlas is reviewed using these premises." | `one`: `submit_required`, fill (`q1`, "q1"), `.top` |
| P2 | none | P1′'s wording | `QueryMismatch: <u>` |
| P3 | (`q1`, `beaconReviewed`): an existing query with the wrong target (N7) | P1′'s wording | `QueryMismatch: <u>` |
| P3′ | F0 plus `q2 : query`; (`q1`, `atlasReviewed`), (`q2`, `atlasReviewed`) | P1′'s wording | `QueryMismatch: <u>` (two matching records) |
| P3″ | F0 plus `q2 : query`; (`q1`, `beaconReviewed`), (`q2`, `atlasReviewed`) | P1′'s wording | `one`: `submit_required`, fill (`q2`, "q2") |
| P4 | `E_web` (no proof predicate), (`q1`, `approved(draft)`) | "Prove that draft is approved using these premises." | `MissingObligationRole: {0} submit a proof of {1}` |
| P4′ | F0 plus `submitx_required(service, query)` with the same act, (`q1`, `atlasReviewed`) | P1′'s wording | `MissingObligationRole: {0} submit a proof of {1}` (two proof predicates) |
| P5 | (`q1`, `atlasReviewed`) | "Prove that tom is a dog using these premises." | `NoDerivation: The sentence to prove has no reading … 'is a dog' …` |
| P6 | (`q1`, `atlasReviewed`) | "Click Check." | `one`: `click_required` (not a proof task: `readCommand`) |
| P7 | the same, no addressee | P1′'s wording | `UnboundSlot: you` (after the record and the proof predicate match) |
| P8 | the same, budget 0 | P1′'s wording | `limit` |

No fixture reaches an ambiguous P (W17: no sentence over `E_web` or F0 has two derivations), so `many` for the proof
task has no computed row; its content is OPEN O2.

**Context fixture for CI-2.** Use the same wording `"Click Check."` and the same reading in two requests with ids
`r1` and `r2`, units `u1` and `u2`, and scopes binding `you` to different declared users. The encoded answers echo
`r1`/`r2`, name `u1`/`u2` in the commands, and carry the different `VE.SpeechActs.Run.legend` lines for those scopes.
The request id, command unit and legend cannot be a cache keyed only by wording and outcome.

**The proof task's target and SA's fixture (μ) (finding F5).** english-lean's producer selects `{0} is classified as
"animal"` and `{0} is classified as "cat"` for F0's glosses `{0} is an animal` and `{0} is a cat` (computed), so P1, SA's
own (μ), is refused by the ported reader. Python reads it today: `_sentence` (`speech_english.py:96-103`) first matches
the wording against the declared gloss (`_copular`), and only then asks P0. A live test depends on it:
`test_proof_task_wording_uses_an_act_both_linters_accept` (`tests/test_speech_acts_conformance.py:183`) reads "Prove that
tom is a cat using these premises." with the gloss `{0} is a cat`, for which english-lean selects `{0} is classified as
"cat"` (computed). In CI-2's A/B this is a read-to-refused row, class b2, which DRI item 2(b) signs. The converged
review adopted option (a): one owner; the proof task's sentence is read by english-lean, as the condition is; the
test's wording moves to a gloss english-lean selects (as P1′), and the A/B lists the b2 rows with their reason. Since
draft 3 the reader also checks that the sentence's reading is the target of exactly one query record (N7), which
Python did in `ve/speech_document.py:175-181` before `parse_speech`; that selection moves to Lean and Python's is
deleted.

**The deletion ledger (DRI item 2(a)).** Each deleted Python check and what replaces it:

| Deleted (`ve/speech_english.py`, `ve/speech_document.py`) | Lean check | Test |
|---|---|---|
| `You may ` → `PermissionNotCommand` | `prefixRefusal`, diagnostic 3 | W15, (ρ) |
| `Please ` → please needs author approval | `prefixRefusal`, diagnostic 4 | W24, (σ) |
| ` and ` coordination flag | `coordinated`, diagnostic 13 | W25, W26, (π) |
| proof task, `PROOF_TASK_ACT` | `proofTask`, `proofAct` | P1′ to P8 |
| the proof task's query selection (`speech_document.py:175-181`: `_sentence`, then the one query whose target matches) | `proofTask`'s record match | P2, P3, P3′, P3″ |
| `text.endswith(".")`, `rsplit(", if ")`, `Do not ` | `parts`, `splitLastIf` | W8, W9, W29 |
| `_command_candidates` (every act with a verb, constants and definites) | `slotFills`, `tuples`, `phraseMatches` | W5 to W7, W10 |
| `ascii_fold(plain) == ascii_fold(phrase)` | `fold`, `filled` | W27, W28 |
| one match, `AmbiguousDerivation`, wrong role | `readCommand`, `refusal`, diagnostics 8, 10, 11 | W10, W22, W23 |
| the condition through `_formula` | `guardOf` | W8, W18, W19 |
| the scope sentences of `legend` | `VE.SpeechActs.Run.legend` (existing) | the legend lines of section 2 |

`_sentence` stays for assertions and `follows`, and `_copular` for which-questions and `follows` (question-answering's
Q3); the same `speech_document.py` loop keeps its `Does it follow from these premises that …?` branch, which is
question-answering's (`follows`, N7). `act_verb` stays while a listed caller remains; the W1 default sentences of
`legend` stay norms' `default_sentence`. `tests/frozen_speech/speech_acts.py` keeps its own frozen `PROOF_TASK_ACT`
(test data).

**Relay binding (DRI item 4(d)).** CI-2 adds the `english.command` rows to `tests/test_relay_binding_inventory.py`.
BOUND: the id, the unit, the wording, each fill's words and constant, the act, each span, the query. LEAN: the guard,
the paraphrase, the legend lines, the code, class and text. The inventory's fuzz retypes and rebinds each bound field;
its replayed-answer test covers the mode; an answer naming a constant or a query that is not in the request is
`CheckerUnavailable`.

**Seeded bugs (CI-2):** Lean, `caseReported` answering from a cached wording (fails the replayed-answer test); Lean,
`proofTask` ignoring the records' targets (fails P3); Lean, `proofTask` taking the first matching record (fails P3′);
Lean, `proofTask` skipping the shared addressee check (fails P7); Python, `read_command` accepting a fill the request
does not hold (fails the rebinding fuzz).

## 7. CI-3: steps and conditions written first

```lean
inductive Shape
  | core (s : String)                      -- a merged wording
  | preposed (c x : String)                -- `If <c>, <x>.`
  | after (x : String)                     -- `Then <x>.`: a step after its named source antecedent (finding (c))
  | seq (xs : List String)                 -- `<x₁>, then <x₂>[, then …].`, 2 to 8 steps, none conditioned
  deriving DecidableEq, Repr

def capitalise (x : String) : String :=
  match x.toList with
  | c :: cs => String.mk (c.toUpper :: cs)
  | [] => x

def hasThen (s : String) : Bool := ((trimmed s).splitOn ", then ").length > 1

/-- Every split of `If <c>, <x>.` at a `, `, left to right; `Then <x>.`; the sequence; else the merged wording. -/
def shapes (s : String) : List Shape :=
  let t := trimmed s
  if !(t.endsWith ".") then [.core s] else
  let body := t.dropRight 1
  let pre : List Shape :=
    if body.startsWith "If " then
      let ws := (body.drop 3).splitOn ", "
      (List.range (ws.length - 1)).map fun i =>
        .preposed (", ".intercalate (ws.take (i + 1))) (", ".intercalate (ws.drop (i + 1)))
    else []
  let aft : List Shape := if body.startsWith "Then " then [.after (body.drop 5)] else []
  let xs := body.splitOn ", then "
  let sq : List Shape := if 2 ≤ xs.length && xs.length ≤ 8 && !body.startsWith "If " then [.seq xs] else []
  match pre ++ aft ++ sq with
  | [] => [.core s]
  | l => l

/-- One competing reading of a unit, as `many` lists it. CI-3 adds `shape`; CI-6 `form`; CI-7 `purpose`. -/
inductive Alt
  | shape (sh : Shape) (rs : List Reading)
  | form (f : Form)                          -- CI-6
  | purpose (r : Reading) (p : String)       -- CI-7b
  deriving DecidableEq, Repr

inductive StepOutcome
  | one (r : Reading) (afterPrevious : Bool)
  | steps (rs : List Reading)
  | many (alts : List Alt)
  | refused (code text : String)
  | limit
  | mixed (r : Reading) (p : String)         -- CI-7b
  deriving DecidableEq, Repr

/-- A merged outcome as a step outcome; `after` marks a `Then <x>.` step. -/
def lift (sh : Shape) (after : Bool) : Outcome → StepOutcome
  | .one r => .one r after
  | .many rs => .many (rs.map fun r => .shape sh [r])
  | .refused code text => .refused code text
  | .limit => .limit

def conditionScope : StepOutcome :=
  .refused "ConditionScope" "a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only"

/-- The individual shape's complete outcomes. Core, preposed and after use `lift`; `seq` combines every step,
including all readings of a `many` step. The precedence and cap are specified immediately below. -/
def readingTuples : List (List Reading) → List (List Reading)
  | [] => [[]]
  | xs :: rest => xs.flatMap fun x => (readingTuples rest).map (x :: ·)

def shapeOutcome (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) : Shape → StepOutcome
  | .core s => lift (.core s) false (readCommand se sc E L b s)
  | .preposed c x =>
    if hasThen (x ++ ".") then conditionScope
    else lift (.preposed c x) false (readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ "."))
  | .after x => lift (.after x) true (readCommand se sc E L b (capitalise x ++ "."))
  | .seq xs =>
    let os := xs.map fun x => readCommand se sc E L b (capitalise x ++ ".")
    let firstFault := os.findSome? fun o => match o with
      | .refused code text => some (.refused code text)
      | .one r => if r.guard == .top then none else some conditionScope
      | .many rs => if rs.any (·.guard != .top) then some conditionScope else none
      | .limit => none
    match firstFault with
    | some fault => fault
    | none =>
      if os.any (fun o => match o with | .limit => true | _ => false) then .limit
      else
        let choices := os.map fun o => match o with
          | .one r => [r]
          | .many rs => rs
          | _ => []
        let all := readingTuples choices
        if all.length > maxCandidates then .limit
        else match all with
          | [rs] => .steps rs
          | [] => .refused "InvalidInput" "no single speech-act reading"
          | alts => if alts.length ≤ VE.SpeechActs.Wire.readingsBound
              then .many (alts.map fun rs => .shape (.seq xs) rs) else .limit

/-- Each alternative is a complete interpretation of its shape: a sequence alternative has exactly one reading
for every step. `one` and `steps` contribute one alternative; `many` contributes each of its alternatives. -/
def shapeAlts (sh : Shape) (o : StepOutcome) : List Alt :=
  match o with
  | .one r _ => [.shape sh [r]]
  | .steps rs => [.shape sh rs]
  | .many alts => alts
  | _ => []

/-- Combine the outcomes of competing shapes as specified below. -/
def combineShapes (os : List (Shape × StepOutcome)) : StepOutcome :=
  let alts := os.flatMap fun (sh, o) => shapeAlts sh o
  if alts.length > VE.SpeechActs.Wire.readingsBound then .limit
  else if 2 ≤ alts.length then .many alts
  else if os.any (fun (_, o) => match o with | .limit => true | _ => false) then .limit
  else match os.findSome? (fun (_, o) => match o with
      | .one _ _ => some o
      | .steps _ => some o
      | .many _ => some o
      | _ => none) with
    | some o => o
    | none =>
      if os.any (fun (_, o) => match o with
          | .refused code _ => code == "ConditionScope"
          | _ => false) then conditionScope
      else .refused "InvalidInput" "no single speech-act reading"

/-- A single shape passes through; multiple shapes combine their complete alternatives and limit flags. -/
def readStep (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : StepOutcome :=
  let os := (shapes s).map fun sh => (sh, shapeOutcome se sc E L b sh)
  match os with
  | [(_, o)] => o
  | _ => combineShapes os

/-- A shape has a completed reading, including an alternative of `many`. -/
def reads (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (sh : Shape) : Bool :=
  !(shapeAlts sh (shapeOutcome se sc E L b sh)).isEmpty
```

`shapeOutcome` is used for both the one-shape and multiple-shape cases. For `.core`, `.preposed` and `.after`, it
passes through `lift` and preserves the underlying refusal text. A preposed condition followed by `, then ` is
`ConditionScope`. For `.seq xs`, read **every** step in order. The first refusal wins; a non-`.top` guard is
`ConditionScope`. If no step refuses, any `limit` yields `limit`. Otherwise take the Cartesian product of the steps'
`one` and `many` readings. Each product member is `Alt.shape (.seq xs) rs` with `rs.length = xs.length`; a product
over `maxCandidates` (the search cap) yields `limit`. One product member yields `steps rs`; two to 64
(`readingsBound`, N7) yield `many` with every completed member; more yield `limit`. Thus an ambiguous first step never
drops the final step.

For several shapes, `combineShapes` collects all completed `shapeAlts`, preserving their shape and order. If their
count exceeds `readingsBound` (64), it yields `limit`. If at least two are established, it yields `many` with all completed
alternatives, even when a sibling shape reached `limit`; `many` does not certify exhaustive enumeration. With fewer
than two, any `limit` yields `limit`. Otherwise the single completed outcome wins. With none, the existing
`ConditionScope` then `InvalidInput` refusal order applies. Every emitted alternative is complete for its shape.

```lean
-- `readInstruction` now returns `StepOutcome`: a proof task's outcome is `lift (.core s) false`, else `readStep`.
theorem readInstruction_step (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readStep ctx.se ctx.sc ctx.E ctx.L ctx.b s   -- replaces `readInstruction_command`

/-- The CI-3 public entry has a class for every step and condition refusal. -/
theorem readInstruction_refused_classed_step (ctx : Context) (s code text : String)
    (h : readInstruction ctx s = StepOutcome.refused code text) : (Texts.classOf code).isSome = true

/-- `readInstruction_typed` through CI-3's entry (N7: the typing theorem covers every later batch): a `one`, and
every member of `steps`. It holds because each `one` and each `steps` member is a `readCommand` `one` (`many` has at
least two readings), and `commandOk` ignores the unit. -/
theorem readInstruction_typed_step (j : Lean.Json) (ctx : Context) (r : Reading) (D : VE.SpeechActs.SpeechDoc)
    (u : String) (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok ctx.se)
    (h : (∃ x, readInstruction ctx s = StepOutcome.one r x) ∨
      ∃ rs, readInstruction ctx s = StepOutcome.steps rs ∧ r ∈ rs)
    (hE : D.E = ctx.se.ne.rv.environment) (hS : D.scope = ctx.sc) (hR : D.regulated = ctx.se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true)
    (hq : ∀ q ∈ ctx.queries, (q.id, "query") ∈ ctx.se.ne.rv.vocabulary.constants) :
    VE.SpeechActs.commandOk D (r.command u) = true

/-- Conservative: a merged wording keeps its reading. -/
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

/-- At least two completed alternatives establish ambiguity, including two from one shape. -/
theorem shapes_ambiguous
    (h : 2 ≤ (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound) :
    ∃ alts, readStep se sc E L b s = .many alts ∧ 2 ≤ alts.length

/-- Every reported sequence alternative contains every step. -/
theorem seq_ambiguous (xs : List String) (alts : List Alt) (hs : shapes s = [.seq xs])
    (hr : readStep se sc E L b s = .many alts) :
    ∀ a ∈ alts, ∃ rs, a = .shape (.seq xs) rs ∧ rs.length = xs.length

/-- With fewer than two completed alternatives, a stopped sibling prevents uniqueness. -/
theorem shapes_limit (hs : 2 > (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length)
    (hl : ∃ sh ∈ shapes s, shapeOutcome se sc E L b sh = .limit) :
    readStep se sc E L b s = .limit

/-- When no shape stopped and the cap holds, a `many` answer lists every completed alternative. -/
theorem shapes_complete (alts : List Alt)
    (hl : ∀ sh ∈ shapes s, shapeOutcome se sc E L b sh ≠ .limit)
    (hc : (((shapes s).map fun sh => shapeAlts sh (shapeOutcome se sc E L b sh)).flatten).length ≤
      VE.SpeechActs.Wire.readingsBound)
    (hr : readStep se sc E L b s = .many alts) :
    ∀ sh ∈ shapes s, ∀ a ∈ shapeAlts sh (shapeOutcome se sc E L b sh), a ∈ alts

def stepCommands (u : String) (rs : List Reading) : List VE.SpeechActs.Command :=
  rs.mapIdx fun i r => r.command (u ++ "." ++ toString (i + 1))

/-- A sequence contributes exactly its steps' demands, named `cmd-<u>.1` … `cmd-<u>.n`, and no other rule. -/
theorem stepCommands_policy (D : VE.SpeechActs.SpeechDoc) (u : String) (rs : List Reading)
    (pre post : List VE.SpeechActs.Command) (h : D.commands = pre ++ stepCommands u rs ++ post) :
    (VE.SpeechActs.policy D).T.nodes =
      D.norms ++ (pre ++ stepCommands u rs ++ post).map (VE.SpeechActs.demand D)

structure StepUnit where
  id : String
  instruction : Bool             -- a translated instruction unit
  steps : Nat                    -- 1 for a single command
  after : Bool                   -- a `Then <x>.` unit
  antecedent : Option String     -- for a `Then` unit: the source antecedent the writer names (finding (c); OPEN O3)
  deriving DecidableEq, Repr

/-- The step names in document order: `u`, or `u.1` … `u.n` for a sequence. -/
def stepNames (us : List StepUnit) : List String :=
  us.flatMap fun u => if u.steps ≤ 1 then [u.id] else (List.range u.steps).map fun i => u.id ++ "." ++ toString (i + 1)

def lastStep (u : StepUnit) : String := if u.steps ≤ 1 then u.id else u.id ++ "." ++ toString u.steps
def firstStep (u : StepUnit) : String := if u.steps ≤ 1 then u.id else u.id ++ ".1"

/-- The named antecedent of the unit at position `k`, when it is an earlier translated instruction unit. -/
def antecedentOf (us : List StepUnit) (k : Nat) (u : StepUnit) : Option StepUnit :=
  u.antecedent.bind fun a => ((us.take k).filter (·.instruction)).find? (·.id == a)

/-- The stated order: consecutive steps of a sequence, and an `after` unit after the last step of its source
antecedent, never after the nearest earlier instruction unit by default (finding (c)). No rule and no premise (D4). -/
def stepOrder (us : List StepUnit) : List (String × String) :=
  (List.range us.length).flatMap fun k =>
    match us[k]? with
    | none => []
    | some u =>
      let inner := if u.steps ≤ 1 then [] else (List.range (u.steps - 1)).map fun i =>
        (u.id ++ "." ++ toString (i + 1), u.id ++ "." ++ toString (i + 2))
      let prev := if u.after then
          match antecedentOf us k u with
          | some v => [(lastStep v, firstStep u)]
          | none => []
        else []
      prev ++ inner

/-- The `Then` units whose antecedent is not an earlier translated instruction unit: `ThenWithoutStep` in
authoring (a document check in `Source/Run.lean`), a GAP in translation (finding (c)). -/
def thenWithoutStep (us : List StepUnit) : List String :=
  (List.range us.length).filterMap fun k =>
    match us[k]? with
    | some u => if u.after && (antecedentOf us k u).isNone then some u.id else none
    | none => none

theorem stepOrder_forward (us : List StepUnit) (p : String × String) (hn : (stepNames us).Nodup)
    (h : p ∈ stepOrder us) :
    ∃ i j : Nat, i < j ∧ (stepNames us)[i]? = some p.1 ∧ (stepNames us)[j]? = some p.2
```

**Does W1's act linter make `hs` unnecessary? (computed facts).** `then` is in `actReserved` (`Acts/LexicalBase.lean:7-9`),
so `canonicalAct` refuses it in every act phrase; under `acts@0` it is a `clauseWord`, refused even inside a fixed phrase
(`Acts/Lexical.lean:22, 72`). No act word or fill holds a comma outside an `acts@0` fixed phrase, and a fixed phrase cannot
hold `then`. So a matched body never holds `, then `, and `hasThen s = true` with `readCommand s = one r` only when `, then `
lies inside the condition (english-lean has no such sentence: "draft is approved, then click Ask" has no reading). `hs`
stays, and is discharged for every wording whose condition has no `, then `. `readStep_conservative` held on all eleven
CI-1 rows that read `one` (W1 to W9, W21, W27).

**English.** "If draft is approved, click Ask." reads as "Click Ask, if draft is approved." Its command paraphrase
is "In this task, you are required to click Ask, where the stated condition holds." A sequence's paraphrase is
"In this task, you are required to do these in order: first click Check rule conflict, then click Ask. The order is
stated; VE does not reason about it." Speech-acts owns the rendering (S10); CI-3 adds `paraphraseSteps` there,
without a second paraphrase table.

**Fixtures (computed over `E_web`).**

| Wording | `readStep` |
|---|---|
| "Then click Ask." (tour.js) | `one click_ask_required, afterPrevious` |
| "Then click Check rule conflict." (tour.js) | `one click_check_required, afterPrevious` |
| "Click Check rule conflict, then click Ask." | `steps [click_check_required, click_ask_required]` |
| "If draft is approved, click Ask." | `one click_ask_required`, guard `approved(draft)` (equal to `readCommand` of "Click Ask, if draft is approved.") |
| "If draft is approvable, click Ask." | `NoDerivation: The condition has no reading … 'is approvable' …`, equal to `readCommand` of the rewritten form (preposed_eq's other direction) |
| "Then click Use this wording under the one you mean." | `InvalidInput: no single speech-act reading`, as `readCommand` of "Click Use this wording …." (after_eq's other direction) |
| "If draft is approved, click Check rule conflict, then click Ask." | `ConditionScope: a condition with a sequence of steps: write one sentence per step, with the condition on each step or on the first only` |
| "Click Ask, if draft is approved, then click Ask." | `ConditionScope: …` (a step with a condition) |
| "Add an exception or precedence, then check for a conflict in plain English." (index.html) | `InvalidInput: no single speech-act reading` (its first step is refused) |
| "Add an exception or precedence, then click Ask." | the same (seq_eq's other direction: the first step does not read) |
| "Click Check rule conflict." | `one click_check_required` (conservative) |
| "Review the meaning, then click Ask." | `many`: two complete `.seq` alternatives; each ends in `click_ask_required` after its respective W10 first step |

**Constructed aggregation fixtures for CI-3.** Two complete shape outcomes plus one `limit` yield `many` with both
complete alternatives; one complete shape outcome plus one `limit` yields `limit`. A sequence whose first step is
`many` and whose second is `one` retains the second reading in every alternative. A stopped step in a sequence yields
`limit` unless an earlier step refused. These rows pin the precedence without depending on an accidental ambiguity
of `E_web`'s lexicon. The reported alternatives may be fewer than all possible alternatives after a sibling limit,
but each reported alternative contains every step of its shape.

The revised `shapeOutcome`, `shapeAlts`, `combineShapes` and `readStep` bodies were inserted into a temporary copy of
the original stub and accepted by `lake env lean`. Its `#eval` returned both complete W10 sequence alternatives,
`limit` for `[one, limit]`, and `many` for `[one, one, limit]`. A separate bounded Lean check accepted the exact
`hasThen` and `firstStep` definitions, the two-unit order pair, the composed code-class lookup and the
`purposeSplit` body. These checks do not prove the stated theorems; CI-3 and CI-7 must supply those proofs.

**The stated order (computed; finding (c)).** On [`u1` (instruction), `u2` (instruction, 2 steps), `u3` (`Then`,
antecedent `u2`), `u4` (not an instruction), `u5` (`Then`, antecedent `u3`), `u6` (`Then`, no antecedent), `u7` (`Then`,
antecedent `u4`)], `stepOrder` is [(`u2.1`, `u2.2`), (`u2.2`, `u3`), (`u3`, `u5`)] and `thenWithoutStep` is [`u6`, `u7`]:
`u6` is not paired with `u5`, the nearest earlier instruction unit, and `u7` names a unit that is not an instruction.
The pilot's pattern (uweb.tour.552_0): [`a` (instruction), `b` (`Then`, antecedent `x`, not translated)] gives no pair
and `ThenWithoutStep` for `b`, where draft 2 would have paired `a` with `b`. "Then click Ask." with no earlier
instruction unit is `ThenWithoutStep`. The counterexample [`a` (one step), `b` (two steps, `after`, antecedent `a`)]
has names `[a, b.1, b.2]` and order `[(a, b.1), (b.1, b.2)]`; `stepOrder_forward` applies to both pairs. The
reader's own outcome is unchanged: "Then click Ask." is `one click_ask_required, afterPrevious` for `readStep`; the
antecedent is a document fact, not a reading fact. `ThenWithoutStep`'s text is CI-3's document check's (it has none in
the plan or here; CI-3 adds it to `Texts` with the class `VEError`).

**A sequence with a refused step in translation (finding (d), computed).** `readStep` keeps the authoring rule, the
first refusal wins with the step's code and text, which does not yet name the step (OPEN O8): "Click Ask, then add an exception or precedence." is `InvalidInput: no single
speech-act reading`, with step outcomes [`one click_ask_required`, `InvalidInput`]. In translation the same unit is a
MIXED unit: a demand part for `click_ask_required` and a GAP part with the refused step's code and its owner (OPEN O4
when the step's object kind is not in section 12's table); the stated order keeps only the pairs between read steps
(here none). This is the translation writer's rule, not a new reader outcome: the writer gets each step's code by reading the
step alone (`capitalise x ++ "."`, as `shapeOutcome` reads it), and `StepOutcome` gains no constructor.

**`surfaceKind` flips ((iii)), computed on the test corpus.** No wording in `tests/*speech*.py`,
`tests/frozen_speech/` or the Q1.4 A/B corpus (`docs/question-answering/q1-4/evidence/speech_ab.py`) begins with `If `
or `Then `, so no signed choice there flips. SA's (ββ) premise "If Alice must click Check then Atlas is reviewed." has no
comma, so the new `if ` case leaves it `asserted`. CI-3's A/B still lists every flip on the pinned A/B corpus with its
class (b3 when it adds a conflict; a removed conflict stops the batch, DRI item 2(b)).

**Seeded bugs (CI-3):** `stepOrder` reversed (fails the order fixture); `stepOrder` pairing a `Then` unit with the
nearest earlier instruction unit (fails the uweb.tour.552_0 fixture); `preposed` dropping the condition (fails the
equality fixture); `readStep` returning the generic refusal for one shape (fails "If draft is approvable, click Ask.").

## 8. CI-4: labels, quoted wordings, `this` phrases, typographic quotes

**Rendering at the speech-acts owner.** CI-4 extends `VE.SpeechActs.Run.nameOf`, `actRest` and `paraphrase` to
receive `spell : String → Option String`, obtained from the same decoded english-lean environment as the reader.
`nameOf D spell a` selects the first definite phrase bound to `a`, else `spell a`, else `a`. CI-3 adds
`VE.SpeechActs.Run.paraphraseSteps D spell cs`; it renders the **complete** command list in step order and then says
`The order is stated; VE does not reason about it.` The legend stays `VE.SpeechActs.Run.legend sc`.

```lean
def nameOf (D : VE.SpeechActs.SpeechDoc) (spell : String → Option String) (a : String) : String :=
  ((D.scope.definites.find? (·.2 == a)).map (·.1)).orElse (fun _ => spell a) |>.getD a

def actRest (D : VE.SpeechActs.SpeechDoc) (spell : String → Option String)
    (c : VE.SpeechActs.Command) : String

def paraphrase (D : VE.SpeechActs.SpeechDoc) (spell : String → Option String)
    (c : VE.SpeechActs.Command) : String

def paraphraseSteps (D : VE.SpeechActs.SpeechDoc) (spell : String → Option String)
    (cs : List VE.SpeechActs.Command) : String
```

The single-command sentence keeps speech-acts' existing force and guard wording. Fixture with a declared display:
`click_required(user, control)` and `checkconflict` displayed as `Check rule conflict`, with no definite bound to it,
renders `In this task, you are required to click Check rule conflict.` A bound definite wins over that display.
W8 renders `In this task, you are required to click Check rule conflict, where the stated condition holds.` A complete
two-step list renders `In this task, you are required to do these in order: first click Check rule conflict, then
click Ask. The order is stated; VE does not reason about it.` These are CI-3/CI-4 output fixtures, not original
CI-0 stub results.

```lean
namespace VE.SpeechActs.Wire

/-- U+2018 and U+2019 to `'`, U+201C and U+201D to `"`; every other character is kept. -/
def typographic (s : String) : String :=
  s.map fun c => if c == '‘' || c == '’' then '\'' else if c == '“' || c == '”' then '"' else c

theorem typographic_ascii_id (s : String) (h : asciiWording s = true) : typographic s = s

theorem typographic_only (s : String) :
    asciiWording (typographic s) = true ↔
      ∀ c ∈ s.toList, c.toNat < 128 ∨ c = '‘' ∨ c = '’' ∨ c = '“' ∨ c = '”'

/-- Today's `phraseOk`, kept under this name. -/
def phraseOk₀ (p : String) : Bool   -- the body of today's `phraseOk`, `Wire.lean:66-69`

/-- Today's phrases, or a `this` phrase of the same normal form. -/
def phraseOk (p : String) : Bool :=
  phraseOk₀ p ||
    (let ws := VE.Norms.Wire.words p
     " ".intercalate ws == p && p.utf8ByteSize ≤ 80 && ws.length ≥ 2 && ws.head? == some "this" &&
       ws.all VE.Norms.Wire.actWord)

theorem phraseOk_mono (p : String) (h : phraseOk₀ p = true) : phraseOk p = true

end VE.SpeechActs.Wire

namespace VE.Commands
/-- CI-4's fills (N7; S23): each constant by its name, then the lexicon's selected spelling (`L.spellings`) when it
differs from the name, then its definite phrases. The request decoder has already refused a lexicon english.read
refuses (S24), so `L` here passes `L.valid` and the V6 policy. -/
def slotFills (se : SpeechEnvironment) (sc : Scope) (L : Lexicon) (srt : String) : List Fill :=
  (se.ne.rv.vocabulary.constants.filter (·.2 == srt)).flatMap fun (c, _) =>
    ⟨c, c⟩ :: (((L.spellings.lookup c).toList.filter (· != c)).map fun sp => ⟨c, sp⟩) ++
      (sc.definites.filter (·.2 == c)).map fun (p, _) => ⟨c, p⟩

/-- A fill is a constant's own name, the lexicon's selected spelling of it, or a phrase the scope binds to it. -/
theorem candidate_fills (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∀ f ∈ r.fills, f.words = f.const ∨ (f.const, f.words) ∈ L.spellings ∨ (f.words, f.const) ∈ sc.definites
end VE.Commands
```

`phraseOk_mono` was proved in the stub (`simp`). The CI-4 chain (`phraseMatches`, `actMatches`, `candidates`,
`tupleCount`) is CI-1's with this `slotFills`; the stub ran it. The spelling fills raise `E_web`'s fill tuples from 20 to
25 (the quoted names `"question1"`, `"meaning1"`, `"token1"`), and `E_web4`'s are 52; the cap stays 4,096.

**Does english-lean's spelling check accept a capitalised label and a quoted wording? (DRI item 3(a), computed.)**
- A capitalised label is accepted with no change. With the overlay displays "Check rule conflict" and "Nearest declared
  wordings", english-lean's producer selects them as the constants' spellings (`policySpellings`), and the lexicon has no
  V1 to V6 failure.
- A quoted wording is accepted as a declared display: the overlay with the display `"Rule 4."` passes `english.read`'s
  overlay check (`overlayCheck`: no failure). english-lean's lexicon selects the quoted name `"rule4"` for it, because
  `letterWords` fails on the quote and the period. A lexicon that selected the display instead fails V6.
- Since draft 3, CI-4's reader reads the lexicon's selection (`L.spellings`, N7), not the display (S23). So a label
  reads (english-lean selects it), and a quoted wording reads only as english-lean selects it: `Copy "rule4".` reads,
  `Copy "Rule 4.".` does not. **CI-4 needs no change to english-lean's checks**; reading a quoted display such as
  `"Rule 4."` would need english-lean to select it, which is english-lean's row in `Lexicon.lean`/`Policy.lean` with its
  owner (plan section 11, issue 3; DRI item 3(a)), with a refusal test for an undeclared spelling. No batch here asks
  for it.

**Fixtures (computed).** `E_web4`: `E_web` without `click_check_required`, plus `click_required(user, control)`
`{0} click {1}`, `look_required(user, control)` `{0} look at {1}`, `copy_required(user, text)` `{0} copy {1}`, and the
constants `checkconflict : control`, `nearest : control`, `rule4 : text`, displayed "Check rule conflict", "Nearest
declared wordings" and `"Rule 4."` by the overlay.

| Wording | CI-4 candidates (`L.spellings`) | CI-1 reader on the same environment |
|---|---|---|
| "Click Check rule conflict." | one: `click_required`, (`checkconflict`, "Check rule conflict") | (W1's act is removed) |
| "Look at Nearest declared wordings." | one: `look_required`, (`nearest`, "Nearest declared wordings") | `InvalidInput: no single speech-act reading` |
| `Copy "Rule 4.".` | none: refused (english-lean selects `"rule4"`, S23) | `InvalidInput: no single speech-act reading` |
| `Copy "rule4".` | one: `copy_required`, (`rule4`, `"rule4"`) | `InvalidInput: no single speech-act reading` |
| the label rows with no overlay (undeclared) | none: refused | refused |
| `Copy "rule4".` with no overlay | one: the same (the quoted name is the lexicon's spelling with or without a display) | refused |
| "Click Ask." | one: `click_ask_required` (unchanged) | the same |

Over `E_web` itself: `Review "meaning1".` is one `review_required`, (`meaning1`, `"meaning1"`); `Do not share "token1".` is
one forbid `share_permitted`, (`token1`, `"token1"`); W1 and W10 are unchanged (one-word names add no fill). With
`notes : control` displayed "Notes", english-lean selects "Notes" beside the name `notes`; "Look at Notes." is one
`look_required` with the first fill, (`notes`, "notes") (S33; computed).

**D9 through the entry (S35).** At CI-4 `trimmed` applies `typographic` first:
`trimmed s := String.mk (((typographic s).toList.dropWhile asciiSpace).reverse.dropWhile asciiSpace).reverse`. So
every reader (`prefixRefusal`, `parts`, the proof task, the shapes, the splits) matches the normalised wording, and no
statement changes (`typographic_ascii_id`: an ASCII wording is its own image). `decodeUnitIn` (`Wire.lean:680`) and
the source wrapper (`Source/Run.lean:87`, `readUnit`'s unit check, and `:686`, the fence check) test
`asciiWording (typographic text)`; the plan lists the first and the last. `decodeUnitIn` also passes
`typographic source` to `choiceKindConflicts` (`Wire.lean:690`), the only path to `surfaceKind`: `wordBreak` breaks at
`"` but not at `“`, so otherwise a signed choice on `Copy“rule4”.` and on `Copy"rule4".` would be classed differently. Computed: `Copy “rule4”.` reads as
`Copy "rule4".` (one `copy_required`, (`rule4`, `"rule4"`)); W13 "Open “Vocabulary & small world” to fix it." is
`InvalidInput: no single speech-act reading` at CI-4 (no act; its split part does not read at CI-7a either).

`typographic` then `asciiWording` on W13 is `true`; on "Is it the case that atlas is checKed?" with U+212A it is
`false` (SA's fixture stays refused): the two directions of `typographic_only`. `phraseOk "this unit"` is true and
`phraseOk₀ "this unit"` false; `phraseOk "the token"` is true. "Enter a reason to keep this unit unresolved." (app.js)
is no longer a CI-4 row (finding (b)): its purpose/goal complement makes it a GAP naming purpose-explanation in
translation, D7's audit (CI-8's) does not count it, and CI-7a refuses it as `PurposeClause` once its command part
"Enter a reason." reads. CI-4 counts 0 segments. Over `E_web` it is `InvalidInput: no single speech-act reading`
(computed). The reader has no goal-complement check: a declared whole act with such a complement reads as W4 does
(D7 is a measurement rule, not a product check).

**Not buildable at `@0` (S18).** Draft 2's CI-4 row "Make rule 4 an exception to rule 1: change “Rule 4.” to “Rule 4
(exception to rule 1).”" needs a three-place act; `{0} change {1} to {2}` is refused ("invalid signature:
change_required"). So CI-4 reads the command part of one MIXED unit, "Look at Nearest declared wordings: “may read the
handbook” is the closest one.", and the plan counts 1 MIXED unit for CI-4, not draft 2's 2. "Open “Vocabulary & small
world” to fix it." holds a purpose clause: refused (CI-7a's `PurposeClause` once its command part reads; D6; DRI item
4(c)).

**The speech-acts corpus rows the spelling fills change (D3).** Under `L.spellings` every constant has a spelling: its
name when the name is one lower-case word, else the quoted name (computed on `E_web`: `"question1"`, `"meaning1"`, `"token1"`). The
first adds no fill (`slotFills` drops a spelling equal to the name). The second adds a fill only for a wording that
quotes a constant's name, and no command wording in `tests/*speech*.py`, `tests/frozen_speech/` or the Q1.4 A/B corpus
quotes one (by Grep, both quote styles). A display comes only from the overlay (`Env.decode`), and the speech path
sends the empty overlay (`speech_english.py:160`). So the fills change no existing row there. CI-4's A/B lists any row
on its pinned corpus.

**Seeded bugs (CI-4):** `typographic` also mapping U+212A (fails the Kelvin fixture); `slotFills` ignoring
`L.spellings` (fails the label row); `slotFills` reading `declaredSpelling` instead (fails the `Copy "Rule 4.".` row);
`slotFills` reading an undeclared label (fails the no-overlay row).

## 9. CI-5: `speech-acts@0` with `acts@0`, simple acts only

```lean
/-- AR-10 (act-phrases 4.4, revised; DRI item 3(b)): `acts@0` changes no route, and the speech route is one it may
join. -/
theorem gate_acts (ps : List String) (h : "acts@0" ∈ ps) (r : VE.Compose.Route)
    (hg : VE.Compose.gateOf VE.Compose.profileTable ps = .ok r) :
    VE.Compose.gateOf VE.Compose.profileTable (ps.erase "acts@0") = .ok r ∧
      (r = .norms ∨ r = .normDefaults ∨ r = .readings ∨ r = .speechActs)

/-- Decoder compatibility: the speech route decodes its regulated declarations with the norms decoder, `acts@0`'s hook
on, on the environment without the speech block. -/
theorem decode_acts_compatible (j : Lean.Json) (se : SpeechEnvironment)
    (h : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se) :
    ∃ j', VE.SpeechActs.Wire.stripSpeech j = .ok j' ∧
      VE.Norms.Wire.decodeNormsEnvironment j' (acts := true) = .ok se.ne

/-- Every profile list the merged gate admits is still admitted. -/
theorem profileGate_mono (ps : List String) (h : VE.SpeechActs.Wire.profileGate₀ ps = .ok ()) :
    VE.SpeechActs.Wire.profileGate ps = .ok ()

/-- Without `acts@0` the decoded speech environment is the merged one. -/
theorem decode_without_acts (j : Lean.Json) (ps : List String)
    (hp : VE.SpeechActs.Wire.profilesField j = .ok ps) (h : "acts@0" ∉ ps) :
    VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = VE.SpeechActs.Wire.decodeSpeechEnvironmentFull₀ j

namespace VE.Acts.Lexical   -- `lean/VE/Acts/Lexical.lean`, shared with act-phrases (plan 12.1)
/-- NEW (S17, S27): a simple act; the Bool view of `main`'s join test `joinCheck` (`Lexical.lean:138`: no word of
`joinWords` — `and`, `or`, `nor`, `for` — and no comma outside a fixed phrase) on the act's tokens under the fixed
phrases. `check` (`:145`) already calls `joinCheck` through `checkWith` (`:121`); CI-5 adds no second join test. -/
def joinFree (fx : List String) (act : String) : Bool :=
  match lex fx act with
  | .ok ts => match joinCheck "" act ts with
    | .ok _ => true
    | .error _ => false
  | .error _ => false
end VE.Acts.Lexical

/-- Under `acts@0` a read command's act is one simple act. -/
theorem command_act_simple (j : Lean.Json) (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : "acts@0" ∈ se.profiles) (r : Reading) (hr : readCommand se sc E L b s = .one r) :
    ∃ g a fx, g ∈ se.ne.regulated ∧ g.name = r.act ∧ g.act = some a ∧
      VE.Norms.Wire.actsFixed se.profiles se.json = .ok fx ∧ VE.Acts.Lexical.joinFree fx a = true
```

`profileGate₀` and `decodeSpeechEnvironmentFull₀` are today's definitions under those names; the new `allowlist` is
`["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]` (code point order). `command_act_simple` needs
the decoder hypothesis because AP-1's `check` enforces `joinFree` at declaration. There is no CI-5 reader refusal:
a decoded `@0` environment cannot contain such a joined act. The batch that first lets AP-2 declare a joined act
adds `JoinedCommandAct: write one command for each act` and restates `readCommand_one_iff` and
`readCommand_complete` for that reachable refusal.

**Computed facts.** Today's gate refuses the list: `UnsupportedProfile: speech-acts@0 with acts@0`; the CI-5 gate admits
it. On the stripped `acts@0` speech environment, `decodeNormsEnvironment` with its default refuses ("UnsupportedProfile:
Unsupported profile acts@0") and with `(acts := true)` decodes, hence S16. The theorems of `Compose/Dispatch.lean` that
unfold `actsRefuses`, which CI-5 re-proves with unchanged statements, are, on `main`, `rowChecks_erase` (`:972`,
`simp` at `:979`) and `todayGate_base` (`:1113`, `simp` at `:1160`); `gate_acts` (`:1253`, `simp only` at `:1263`) is
the revised one. `today_speech` (`:481`) does not unfold it. `Compose/Examples.lean:275` checks
`actsRefuses.length == 7`; removing `speech-acts@0` makes it 6, so CI-5 edits that `#guard` too (S28). CI-5 also removes the row at `Compose/Examples.lean:267` (inside the `#guard` at `:265`) and re-pins `Service/ActsExamples.lean:196` on its new outcome (not computed here): both pin "acts@0 with speech-acts@0 is not implemented", and `Plain.run` gates through `gateOf` (`Norms/Plain.lean:218`). `ve/profile_table.json` is regenerated. `actsRefuses`
on `main` also lists `closure@0`, `order@0` and `ve.discourse@1`; CI-5 removes only `speech-acts@0`.
`gate_acts`' conclusion gains `r = .speechActs` only (C12): `.clauses` and `.discourse` are profile-composition PC-6's,
after CI-5, in act-phrases' one revision. `joinFree`, computed: `{0} click Ask` true; `{0} click Check and save`,
`{0} pay for {1}` and `{0} click A, B` false; AP-1's `check` refuses `{0} click Check and save` with "InvalidInput: act
phrase for click_required joins acts with 'and' outside a fixed phrase".

**The statement review's counterexample (DRI item 3(b)).** Under `acts@0` with `speech-acts@0`, an act joined outside a
fixed phrase is still refused at declaration by AP-1's `check` ("joins acts with 'and' outside a fixed phrase").
AP-2's admission of joined acts is a later statement review and implementation change. The reviewers check the
declaration-time counterexample and the unchanged route without `acts@0` against the revised `gate_acts`.

**Fixtures:** as the plan's (three `acts@0` segments, 125 B estimate); a declaration of "Click Check and save."
is refused by AP-1's join check; every CI-1 to CI-4 row is unchanged with `acts@0` off, by
`decode_without_acts`. A `JoinedCommandAct` reader fixture belongs to the later AP-2 admission batch.

## 10. CI-6: imperative-shaped non-commands

```lean
inductive Form
  | command | supposition | permission | conditionalClaim | remark | heading
  deriving DecidableEq, Repr

/-- The forms of a wording: the classifier over the `CI-6` rows of `VE.EnglishGrammar.SourceWords` and the two
structural cues (a heading; `<imperative> and <declarative clause>.`). With no cue it returns `[.command]`. -/
def forms (s : String) (heading : Bool) : List Form

/-- The forms the heading cue alone gives (a rule or a reading set, as CI-E1 decides). -/
def headingForms : List Form

/-- A form list applied to an outcome: `[.command]` keeps it; no command form is `NotACommand: <form's text>`; a
command form beside others is `many` with every non-command form and the command's alternatives. -/
def classify (s : String) (fs : List Form) (o : StepOutcome) : StepOutcome :=
  if fs == [.command] then o
  else if !fs.contains .command then .refused "NotACommand" (formText (fs.headD .remark))
  else
    let alts : List Alt := (fs.filter (· != .command)).map Alt.form ++ shapeAlts (.core s) o
    if alts.length ≤ VE.SpeechActs.Wire.readingsBound then .many alts else .limit   -- N7 (S20); OPEN O6

def readImperative (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (heading : Bool) : StepOutcome :=
  classify s (forms s heading) (readStep se sc E L b s)

/-- The entry (N7): `Context` gains `heading : Bool`; the heading flag applies before `proofTask`, and no other cue
runs inside P. -/
def readInstruction (ctx : Context) (s : String) : StepOutcome :=
  match proofTask ctx s with
  | some o => if ctx.heading then classify s headingForms (lift (.core s) false o) else lift (.core s) false o
  | none => readImperative ctx.se ctx.sc ctx.E ctx.L ctx.b s ctx.heading

theorem nonCommand_no_demand (heading : Bool) (h : Form.command ∉ forms s heading) (r : Reading) (x : Bool) :
    readImperative se sc E L b s heading ≠ .one r x ∧ ∀ rs, readImperative se sc E L b s heading ≠ .steps rs

theorem forms_nonempty (s : String) (heading : Bool) : (forms s heading).length > 0

theorem command_unchanged (heading : Bool) (h : forms s heading = [.command]) :
    readImperative se sc E L b s heading = readStep se sc E L b s

theorem forms_ambiguous (heading : Bool) (h : 2 ≤ (forms s heading).length) (h1 : Form.command ∈ forms s heading)
    (hn : ((forms s heading).filter (· != .command)).length + (shapeAlts (.core s) (readStep se sc E L b s)).length ≤
      VE.SpeechActs.Wire.readingsBound) :
    ∃ alts, readImperative se sc E L b s heading = .many alts ∧
      ∀ f ∈ forms s heading, f ≠ .command → Alt.form f ∈ alts

theorem readInstruction_imperative (ctx : Context) (s : String) (h : proofTask ctx s = none) :
    readInstruction ctx s = readImperative ctx.se ctx.sc ctx.E ctx.L ctx.b s ctx.heading

/-- No cue runs inside P: without the heading flag a proof task's outcome is `proofTask`'s. -/
theorem proofTask_no_cue (ctx : Context) (s : String) (o : Outcome) (h : proofTask ctx s = some o)
    (hh : ctx.heading = false) : readInstruction ctx s = lift (.core s) false o

/-- The heading flag reaches the proof task: under a heading form list with no command, no demand. -/
theorem proofTask_heading (ctx : Context) (s : String) (o : Outcome) (r : Reading) (x : Bool)
    (h : proofTask ctx s = some o) (hh : ctx.heading = true) (hc : Form.command ∉ headingForms) :
    readInstruction ctx s ≠ .one r x
```

`forms`, `headingForms` and `formText` (one English text per form, in `Texts.lean`) are signatures in the stub; the
rest elaborates. `classify` is the draft-2 stub's `readImperative` with its empty-list fallback removed (the plan: "no
empty-list fallback is allowed"; `forms_nonempty`) and shared with the proof task. The proof task gets the heading cue
only, so "Prove that A and B using these premises." keeps its command reading (the structural `and` cue never runs
inside P), and a heading "Prove that …" is never a single demand when the heading cue has no command form. Both
callers (the mode and the source wrapper) are tested.

**The cue rows against en-sw's `SourceWordRow` (computed; S29).** en-sw has merged: `lean/VE/EnglishGrammar/SourceWords.lean`
defines `SourceWordRow` (`word`, `frame`, `profile`, `owner`, `kind`: `readings` with at least two candidates of
`wording` and `situation`, `refuse code advice rewrite`, or `fixed`) and `sourceWords = []`. Each of the eight lexical
cues (`suppose`, `imagine`, `consider a case where`, `consider a situation where`, `feel free to`, `at any time`,
`note that`, `see`), with owner `CI-6` and profile `speech-acts@0`, passes `validIdentity` and `validKind` both as a
`refuse` row (code `NotACommand`, an advice text and a rewrite) and as a `readings` row, and the eight together pass
`sourceWordsValid` in each kind. So every cue fits the row type, and english-lean needs no change. Three
constraints for CI-6's rows: `word` is in the catalogue's normal form (`sourceWordNormal "Suppose" = "suppose"`; the
capitalised word fails `validIdentity`); `frame` carries the position (`at any time` is clause-final, the others
initial: the key is `(word, frame, profile)`); and a `refuse` row's rewrite may not contain the cue even inside a word
(a rewrite with "foresee" fails for `see`). The row type has no field for a `Form`: a `readings` row names its forms
by its candidates' wordings, and `forms` maps them; that mapping is CI-6's. The structural cues are not rows.
`listItem` stays deferred and list items under a lead-in are refused (DRI item 4(b)).

**Supposition and modality (C24).** CI-6's supposition classification ("Suppose", "Imagine", "Consider") applies to
modality's reader; modality's MD-4 owns the scenario meaning. The CI-6 → MD-4 pointer is added by whichever of CI-6
and MD-4 merges second.

CI-6's default fixture has no cue: `forms "Click Ask." false = [.command]`, so its CI-3 reading is unchanged.
`Texts.codeClasses` gains `ConditionScope` and `ThenWithoutStep` at CI-3, so that CI-3's
`readInstruction_refused_classed_step` holds when it is stated, and `NotACommand` at CI-6; the composed
`Texts.classOf` also covers english-lean's refusal codes. CI-3 and CI-6 each restate
`readInstruction_refused_classed` and `readInstruction_typed_step` for their extended public entry.

**D11, `Alt.form` (computed).** In translation `many` goes through speech-acts' candidate pipeline, where each reading
carries exactly one tagged content, and under the kind `instruction` only the tag `command` is admitted
(`contentKindOk`: `command` true; `ast`, `norm`, `question`, `binding` false). An `Alt.form` alternative has no command
content, so a `many` that holds one is refused in translation (section 12).

## 11. CI-7a and CI-7b: purpose clauses

CI-7 is two batches (N7). **CI-7a** (after CI-4 and CI-6) reads every split and refuses; **CI-7b** (after CI-7a,
speech-acts' `documents@1` lift (C21's named bridge, after CI-2) and purpose-explanation's usable interface) makes
`many` or MIXED through `VE.Purposes`. Until CI-7b, a purpose clause on an instruction is refused (D6).

```lean
/-- Every ` to ` cut of `<x> to <p>.`, left to right, then every `, ` split of `To <p>, <x>.`, left to right, with
nonempty parts and no environment veto (N7): a declared whole act does not exclude a split; the environment enters
only through reading. `To fix it, open X to show Y.` lists its ` to ` cut before its `, ` split. -/
def purposeSplit (_se : SpeechEnvironment) (s : String) : List (String × String) :=
  let t := trimmed s
  if !t.endsWith "." then [] else
  let body := t.dropRight 1
  let ws := body.splitOn " to "
  let trailing := (List.range (ws.length - 1)).map fun i =>
    (" to ".intercalate (ws.take (i + 1)), " to ".intercalate (ws.drop (i + 1)))
  let leading := if body.startsWith "To " then
    let ps := (body.drop 3).splitOn ", "
    (List.range (ps.length - 1)).map fun i =>
      (", ".intercalate (ps.drop (i + 1)), ", ".intercalate (ps.take (i + 1)))
    else []
  (trailing ++ leading).filter fun (x, p) => !x.isEmpty && !p.isEmpty

/-- Each split with its command part's full outcome under CI-6 (same heading flag), and the completeness flag:
`true` when no split's outcome is `limit` (N7). -/
def purposeReadings (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (heading : Bool) : List ((String × String) × StepOutcome) × Bool :=
  let xs := (purposeSplit se s).map fun (x, p) => ((x, p), readImperative se sc E L b (capitalise x ++ ".") heading)
  (xs, xs.all fun (_, o) => o != .limit)

/-- A split's command part reads: its outcome is `one` or `many` (the plan's definition; OPEN O5 on `steps`). -/
def partReads : StepOutcome → Bool
  | .one _ _ | .many _ => true
  | _ => false

/-- CI-7a: `PurposeClause` when a split's command part reads; else `limit` when the enumeration is incomplete; else
`readImperative`'s. -/
def refusePurposive (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (heading : Bool) : StepOutcome :=
  let (xs, complete) := purposeReadings se sc E L b s heading
  if xs.any (fun x => partReads x.2) then .refused "PurposeClause" Texts.purposeClause
  else if !complete then .limit
  else readImperative se sc E L b s heading

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

/-- Without a split, the reading is CI-6's (CI-7a's `refusePurposive` and CI-7b's `readPurposive` alike). -/
theorem purpose_none (heading : Bool) (h : purposeSplit se s = []) :
    refusePurposive se sc E L b s heading = readImperative se sc E L b s heading

-- CI-7b (signatures; after C21's bridge and purpose-explanation's reader).
def purposeForSplit (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat)
    (x p : String) (heading : Bool) : List Alt

/-- The unsplit wording's complete alternatives, then each split's `purposeForSplit`, from `purposeReadings`;
`many` alternatives preserved. -/
def purposeAlts (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (heading : Bool) : List Alt

def readPurposive (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)
    (heading : Bool) : StepOutcome

theorem purpose_reading (r : Reading) (p : String) (heading : Bool)
    (h : Alt.purpose r p ∈ purposeAlts se sc E L b s heading) :
    ∃ x, (x, p) ∈ purposeSplit se s ∧
      (readImperative se sc E L b (capitalise x ++ ".") heading = .one r false ∨
       ∃ alts, readImperative se sc E L b (capitalise x ++ ".") heading = .many alts ∧
         (∃ sh, Alt.shape sh [r] ∈ alts))

theorem purpose_nonCommand (x p : String) (heading : Bool) (hs : (x, p) ∈ purposeSplit se s)
    (hn : Form.command ∉ forms (capitalise x ++ ".") heading) :
    purposeForSplit se sc E L b x p heading = []

theorem purpose_mixed (r : Reading) (p : String) (heading : Bool)
    (h : purposeAlts se sc E L b s heading = [.purpose r p])
    (hl : (purposeReadings se sc E L b s heading).2 = true) :
    readPurposive se sc E L b s heading = .mixed r p

theorem purposes_ambiguous (heading : Bool) (h : 2 ≤ (purposeAlts se sc E L b s heading).length)
    (hc : (purposeAlts se sc E L b s heading).length ≤ VE.SpeechActs.Wire.readingsBound) :
    readPurposive se sc E L b s heading = .many (purposeAlts se sc E L b s heading)

theorem purpose_none_b (heading : Bool) (h : purposeSplit se s = []) :
    readPurposive se sc E L b s heading = readImperative se sc E L b s heading
```

`readInstruction`, outside the proof task, is now `refusePurposive` at CI-7a and `readPurposive` at CI-7b, each
stated as CI-3's `readInstruction_step` is. CI-7a adds `("PurposeClause", "VEError")` to `Texts.codeClasses`, with
the text `a command with a purpose clause` (this spec's; the plan fixes one code and one text and names neither
text), and restates `readInstruction_refused_classed` and `readInstruction_typed_step` (CI-7b adds `mixed` to the
latter's hypothesis `h`). At CI-7b the unsplit outcome is retained: two completed
alternatives yield `many` even beside a limited split; with fewer than two, a limit yields `limit`; over 64
(`readingsBound`) yields `limit`; no split command part classified as a heading or other non-command yields `mixed`.

**Fixtures, CI-7a (computed over `E_web` and the A6 environment).** `readImperative` is `readStep` on these wordings
(no cue, `command_unchanged`), so the stub ran `refusePurposive` with `readStep` in its place.

| Wording | Splits (command part reads?) and completeness | `refusePurposive` |
|---|---|---|
| W4 "Choose a unit revision to restore." | (`Choose a unit revision`, no), complete | `one choose_revision_required` (W4 unchanged) |
| the same in A6 (`E_web` plus `{0} choose a unit revision`): a whole act plus its command part | (`Choose a unit revision`, yes) | `PurposeClause: a command with a purpose clause` |
| "Review the meaning to fix it." (its command part is W10's `many`) | (`Review the meaning`, yes) | `PurposeClause: …` |
| "Click Ask, if draft is approved to fix it.", budget 0: an exhausted split | (`Click Ask, if draft is approved`, `limit`), incomplete | `limit` |
| the same, full budget | (… , yes) | `PurposeClause: …` |
| "To fix it, click Ask." (a leading split) | (`click Ask`, yes) | `PurposeClause: …` |
| "Click Ask." | none | `one click_ask_required` (`purpose_none`) |
| "Click Check rule conflict, then click Ask to fix it." | (`Click Check rule conflict, then click Ask`, `steps`: not "reads"), complete | `InvalidInput: no single speech-act reading` (the whole wording's sequence; OPEN O5) |
| "Enter a reason to keep this unit unresolved." (finding (b)) | (`Enter a reason`, no), complete | `InvalidInput: no single speech-act reading` (no act over `E_web`) |
| "To fix it, open X to show Y." | (`To fix it, open X`, no), (`open X to show Y`, no), complete: the ` to ` cut first, then the `, ` split | `InvalidInput: no single speech-act reading` |

**Fixtures, CI-7b (the plan's):** "Remove the review rule in the IDE to find a countermodel.", "Edit JSON to bring
your own vocabulary or world.", "To fix it, change print back to read and click Review meaning.", "To ask “May a new
employee read the handbook?”, write this statement to test." and "Mode is fixed for this document; start a new
document to change it." (5 segments, 315 B to READINGS or MIXED; estimate). In the A6 environment, W4 is `many` with
the unsplit and purpose readings. A leading `To <p>, <x>.` fixture, and a purposive heading fixture in which the split
part has no command form and yields no `mixed` demand. CI-7b pins these before extending the response encoder.

**Seeded bugs:** CI-7a, `refusePurposive` answering `readImperative`'s reading when a split's command part reads
(fails the A6 row); CI-7a, the completeness flag ignored (fails the exhausted-split row); CI-7b, `readPurposive`
dropping the unsplit reading when a split reads (fails the A6 fixture).

## 12. Plan section 12: command objects, writer rules, and D11's mapping

These rules come from plan section 12 (findings (a), (b), (e)) and N7's D11. They are about translation and
measurement; no reader outcome above changes, except where a section already says so.

**(a) Command objects.** The first build (CI-1 to CI-5) covers only these object kinds: a declared constant by name or
by its lexicon spelling (CI-1, CI-4), a definite or `this` phrase the scope binds (CI-4), the proof task's matched query
record (CI-2), and the arguments of one declared simple `acts@0` act (CI-5). Every other kind is a named GAP with its
owner. In authoring the wording stays refused as today; in translation the unit is a GAP unit that names the kind and
its owner, never a prose placeholder.

| Object kind | Pilot unit | Wording (computed over `E_web`, `readStep`) | GAP owner |
|---|---|---|---|
| that-clause object | uweb.tour.515_1 | "Check that it says what you meant.": `InvalidInput: no single speech-act reading` | commands-imperatives, CI-E3 hypothesis B (content parts attitudes' and presupposition's) |
| question object, polar or single-wh | uweb.index.38_0 | "For a new word, choose what kind of thing it names.": `InvalidInput: …` | commands-imperatives, CI-E3 hypothesis A |
| multiple-wh question object | uweb.drafts.889_0 | "Confirm who acts on whom for a relation.": `InvalidInput: …` | question-answering |
| confirmation of a proposed answer | uweb.drafts.889_0 | (the same unit) | presupposition |
| free-relative object over modalities | uweb.index.133_0 | "Review what is required, forbidden or permitted." (constructed): `InvalidInput: …` | question-answering |

Each is refused in authoring over `E_web` (no act matches). An environment that declares a matching act phrase (an
opaque act, SA 2.1) makes it read, as any declared act does; D7's audit (CI-8's, not a product check) does not count
such a segment.

**(b) Purpose and goal complements.** "Enter a reason to keep this unit unresolved." (uweb.drafts.898_0) is a GAP
naming purpose-explanation in translation; CI-4 counts 0 segments; CI-7a refuses it once "Enter a reason." reads
(sections 8 and 11).

**(e) Writer rule: repeated instructions.** When two distinct source instructions translate to the same demand on the
same arguments (the pilot's u1 = u6 and u9 = u10), each unit carries a GAP naming events-time-causation (the occasion),
never "GAPS none". The reader has no part in it: two units with equal `Reading`s are two commands
(`stepCommands_policy` names them by unit).

**D11: `many` onto speech-acts' candidate pipeline (computed).** A speech reading set holds 1 to 64 readings
(`Wire.lean:761`), each with one tagged content whose tag the kind admits (`contentKindOk`, `Wire.lean:772`); under
the kind `instruction` only `command` is admitted. So:

| Alternative | In translation |
|---|---|
| `Outcome.many rs` (CI-1/CI-2) | one reading per `r`, content `command` (2 to 64, by `manyOf`) |
| `Alt.shape (.core _ / .preposed _ _ / .after _) [r]` (CI-3) | one reading, content `command` |
| `Alt.shape sh rs`, `rs.length ≥ 2` (`.seq xs`, or `.core s` from `classify`) (CI-3, CI-6) | no single `command` content: refused in translation (the plan's second option; a new tag would change speech-acts' wire) |
| `Alt.form f` (CI-6) | no `command` content: refused in translation |
| `Alt.purpose r p` (CI-7b) | CI-7b's MIXED or reading set through `VE.Purposes` (after C21's bridge) |

"Refused in translation" means the unit's `many` is not emitted as a reading set; the unit is a GAP naming the kind
(a sequence of steps, or a non-command form) and commands-imperatives as its owner, as (a) treats an object kind the
build does not cover.

## 13. Limits

`maxWordingBytes` 400, the plan's provisional limit. `maxCandidates` 4,096, the search cap: the fill tuples number 20
on `E_web` (25 with CI-4's spelling fills), 52 on `E_web4` under CI-4, and 12 on F0, so the cap leaves over 75 times
the largest measured count, and it also caps the condition reader's enumeration (`translate`'s `cap`). CI-1 may lower
it only with a measured reason. `readingsBound` 64, the speech wire's existing bound (`Wire.lean:761`, N7): every
`many` holds at most 64 alternatives, and more is `limit`; at least 2, except CI-6's `classify`, which can give a
one-alternative `many` (OPEN O6). Over a limit the outcome is `limit`, never a refusal, never
"no reading" and never a truncated `many`. For competing complete shape or purpose alternatives, two established
alternatives yield `many` even beside an exhausted sibling; fewer than two beside exhaustion yield `limit`. This does
not alter the condition reader's own exhaustion rule in section 1.

## 14. CI-0's computed answers (the plan's "Computes in the stub")

| Question | Answer |
|---|---|
| Every CI-1 fixture outcome over `E_web` | section 5 (W1 to W30), all computed; unchanged on `main` (2026-11-02) |
| Fill candidates for the fixture and the corpus, setting `maxCandidates` | 20 (`E_web`), 12 (F0); under CI-4 25 (`E_web`) and 52 (`E_web4`); 4,096 kept (section 13) |
| Does `VE.Norms.Wire`'s act linter refuse `then`? | yes, and `acts@0` refuses it inside fixed phrases too; `hs` stays, discharged unless the condition holds `, then ` (section 7) |
| May a condition use the scope's definite phrases? | no (W20); conditions name constants by english-lean's spellings (section 2) |
| A condition with two derivations over `E_web` for W17 | none among 14 tried, and V4 leaves no valid source; W17 is on a constructed outcome (section 5) |
| Signed-choice rows that the new `surfaceKind` cases flip | none in the speech-acts tests or the Q1.4 A/B corpus (section 7) |
| Does english-lean's spelling check accept a capitalised label and a quoted wording? | the label yes; the quoted wording as a declared display yes, as a lexicon selection no. Since draft 3 the fill reads the lexicon's selection (S23), so `"Rule 4."` does not read and the quoted name `"rule4"` does; CI-4 needs no english-lean change (section 8) |
| Speech-acts corpus rows the spelling fills change | none: no corpus command wording quotes a constant's name, and one-word names add no fill (section 8) |
| `Dispatch.lean` theorems unfolding `actsRefuses` that CI-5 re-proves | on `main`: `rowChecks_erase` (`:972`), `todayGate_base` (`:1113`); `gate_acts` (`:1253`) revised; plus the `#guard` at `Compose/Examples.lean:275` (S28, section 9); and `Compose/Examples.lean:267`, `Service/ActsExamples.lean:196` (S28) |
| CI-6's cue rows against `SourceWordRow` | en-sw has merged: all eight cues fit as `refuse` and as `readings` rows; constraints on `word`, `frame` and the rewrite (S29, section 10) |
| D11: map `Alt.shape (.seq …)` and `Alt.form` onto speech-acts' candidate pipeline, or refuse them in translation (N7) | refuse both: a speech reading has one tagged content, and under `instruction` only `command` (section 12) |
| The bound of `many` (N7) | `readingsBound` 64, the literal at `Wire.lean:761`; `manyOf` 64 → `many`, 65 → `limit` (W31) |
| The proof task over decoded query records (N7) | P1′ to P8 (section 6); no ambiguous P exists over the fixtures (OPEN O2) |
| `L.valid` first (N7) | `L.valid` misses V6; the decoder refuses as english.read does (S24) |
| The text Python gives today for an ambiguous condition | `AmbiguousDerivation: English has two derivations:` followed by two parse trees (P0's `ve/surface/unambiguity.py:77`, read, not run); Lean gives `many` with one reading per guard, shown in authoring with english-lean's `Ambiguous` text for the condition. An R1 row if the A/B finds one; no fixture condition reaches it (W17) |

**Findings beyond the list.** F5 (SA's (μ) under english-lean, section 6), S9 (identifiers begin with a lower-case
letter), S16 (`acts := true`), S18 (no three-place acts at `@0`); since draft 3, S21 (two `QueryRecord`s), S24 (V6),
S27 (`joinCheck` already factored on `main`), S28 (CI-5's extra `#guard`), and `readInstruction_typed`'s hypothesis
`hq` (section 6).

## 15. Re-estimated hours

| Batch | Plan (draft 3) | Now | Why |
|---|---:|---:|---|
| CI-1 | 5–6 | 5–6 | `readingsBound` (one name in `Wire.lean`) and `readCommand_bound` add little |
| CI-2 | 5–6 | 7–9 | the proof task over query records with `QueryMismatch` and its order, `readInstruction_typed` with `hq`, `commandFence_needs_context` in `Source/Run.lean`, the decoder's english.read refusals (S24, S25), Python's query selection deleted, the inventory rows, the A/B with F5's b2 row |
| CI-3 | 4–6 | 5–7 | the antecedent in `StepUnit` and `ThenWithoutStep` (finding (c)), the bound in two places, `readInstruction`'s extension with its response shape, encoder theorem and inventory rows |
| CI-4 | 5–6 | 5–6 | `L.spellings` is simpler than `declaredSpelling`; the quoted-wording fixtures change (S23) |
| CI-5 | 5–6 | 5–6 | `joinFree` is a view of `joinCheck` (S27); one more `#guard` (S28) |
| CI-6 | 4–6 | 5–7 | rows in `SourceWords.lean` (now checkable), `heading` in `Context`, `classify` shared with the proof task, `Alt.form` in the shape and inventory |
| CI-7a | 2–3 | 2–3 | executable in the stub already |
| CI-7b | 2–3 | 3–4 | `Alt.purpose` and `StepOutcome.mixed` in the shape, encoder and inventory, after C21's bridge |

Builder hours for CI-1 to CI-8 (CI-8 3–4): about 40 to 52 (draft 2's spec said 40 to 50). These are estimates.

## 16. Statement review checklist (two Opus seats, one bounded review, before CI-1)

1. D9 and `typographic`: the four characters only; `typographic_ascii_id`, `typographic_only` (section 8).
2. D4: the stated order is no rule and no premise; `stepOrder_forward`, `stepCommands_policy`; since draft 3 a `Then`
   unit is paired only with its named antecedent, and `thenWithoutStep` lists the rest (section 7, finding (c)).
3. The shapes of `Outcome`, `GuardFault`, `StepOutcome` and `Alt`; `readInstruction`'s `Context` without `O` (S1), with
   `queries : List QueryRecord` (S21) and, at CI-6, `heading`.
4. DRI item 1's conditions: `readCommand_typed` with `hd` and `scopeOk D`, and `readInstruction_typed` with `hq`; `many`
   for an ambiguous condition (`guard_ambiguous`, W17); `limit` for exhaustion (`guard_limit`, W18) and over the bound
   (`readCommand_bound`, W31); a context-less fence refused (`commandFence_needs_context`, now in `Source/Run.lean`).
5. S2 and S3: matching as Python matches, and the addressee refusals after the match.
6. The proof task (N7): its order (S22), `proofTask_bound` over records, P2 to P3″ (no record, wrong target, two
   records, one of two), F5's option (a), and the deleted Python selection.
7. The conservativeness hypotheses: decoded `hd` and exact-text `hs` of `readStep_conservative`; `forms_nonempty`,
   `command_unchanged`; `proofTask_no_cue`; `purpose_none`, `purpose_passes` and `purpose_nonCommand`.
8. CI-5's revised `gate_acts` (`.speechActs` only, C12), `decode_acts_compatible` with `(acts := true)`, the joined-act
   counterexample (DRI item 3(b)), and the extra `#guard` (S28).
9. `joinFree` as the Bool view of `main`'s `joinCheck`, one owner of the join test (S17, S27).
10. CI-4's fills from `L.spellings` (S23) and the decoder's english.read lexicon refusal (S24).
11. CI-7a: `purposeSplit` with no veto, `purposeReadings`' completeness flag, `partReads`, `refusePurposive`'s three
    theorems and its computed rows, and the text `a command with a purpose clause`.
12. Section 12: the object kinds and owners, the writer rules (b) and (e), and D11's mapping.
13. Every iff has a fixture in each direction (sections 5, 6, 7, 8, 11). The theorem statements need proofs or
    executable bounded checks in their batches; elaboration as `Prop` is insufficient.
14. The OPEN lines (section 17) are open, not decided: check that nothing above assumes an answer to one.

Converged FIX edits are applied to this spec before CI-1 starts.

## 17. OPEN lines (for the DRI; plans are frozen until Nov 12)

The plan leaves these open. The stub marks each where it is used; nothing here chooses an answer.

- **O1. `QueryMismatch: <u>`'s unit.** The plan's text is the unit id, but its `Context` has no unit and
  `readInstruction ctx s` takes none; only `Request` has `unit`. The stub writes the literal `<u>`. Either `Context`
  gains the unit, or the encoder writes `q.unit` as the text. Until decided, CI-2's fixtures P2 to P3′ check the code
  only.
  **Ruled** (reviews/dri-decisions-20261102-ci-0.md item 2): the wire encoder writes the request's unit `q.unit` as the text; P2, P3 and P3′ check
  code and text.
- **O2. What `many` lists for an ambiguous sentence to prove.** The plan says "ambiguous gives `many`" and "one
  reading must equal exactly one record's target". It does not say which proof readings `many` holds when P has two
  readings: one per reading that matches exactly one record, and what happens to a reading that matches none or two.
  The stub has `proofMany` as a signature. No fixture reaches it (W17). Whatever the answer, `proofMany` never returns
  `one`, and any refusal it gives has a classed code: `proofTask_bound`, `proofTask_addressed`, `readInstruction_typed`,
  `readInstruction_refused_classed` and CI-3's `readInstruction_typed_step` depend on that, and CI-2 cannot close those
  proofs until O2 is answered.
  **Ruled** (reviews/dri-decisions-20261102-ci-0.md item 3): `proofMany` lists, in the reader's order, one proof reading per reading whose target
  equals exactly one record's target; fewer than two left is `QueryMismatch`, never `one`.
- **O3. A `Then` unit's antecedent in authoring.** Finding (c) names "the earlier translated instruction unit the
  writer names". A source document's unit schema (`Source/Run.lean:40-41`: `id`, `span`, `kind`, `meaning`, `support`,
  optional `content`, `surface`, `meaning_id`, `status`) has no field for it. Without one, every authored `Then` unit
  is `ThenWithoutStep` under `thenWithoutStep`, including tour.js's "Then click Ask." in a document. The reader's
  outcome (`one …, afterPrevious`) does not depend on it.
- **O4. The owner of a refused step's GAP part (finding (d)).** "Each refused step is a GAP part with its code and its
  owner": when the step's object kind is in section 12's table, that table names the owner; otherwise (for example
  "Add an exception or precedence.") the plan names none.
- **O5. A split whose command part is a sequence (CI-7a).** The plan's `partReads` counts `one` and `many`, not
  `steps`. So "Click Check rule conflict, then click Ask to fix it." is `InvalidInput: no single speech-act reading`
  (the whole wording's sequence, whose second step is refused), not `PurposeClause`. Both are refusals; only the code
  and text differ. Also, `Then click Ask to fix it.`'s command part is `one r true`: `PurposeClause` at CI-7a, but
  CI-7b's `purpose_reading` (`one r false`) allows it no alternative.
- **O6. A one-alternative `many` from `classify` (CI-6).** When a wording has a command form beside another form and
  its command part does not read (refused, or `limit`), `classify` gives `many` with the non-command forms only: for
  "Skip it at any time." with no `skip` act, one alternative (`Alt.form .permission`). A `limit` command part is lost
  the same way, and CI-7a's `partReads` then counts that `many` as reading. `forms_ambiguous` demands `many`, section
  13 says a `many` has at least two alternatives, and the plan does not choose between them.
- **O7. Where `Context.b` comes from.** The plan's request has "the budget", but `english.read`'s request has only
  `cap`, and no field gives the work budget `b` (english-lean reads at `workBudget`). With `b > workBudget`, the
  condition reader's fallback (which re-reads at `workBudget` for the code and text) can report `Budget` as a refusal
  where the read at `b` found no reading.
  **Ruled** (reviews/dri-decisions-20261102-ci-0.md item 4): `Context.b = workBudget`; the request has no budget field.
- **O8. The refused step's name (finding (d)).** Plan 12.2(d) says that in authoring the refusal's text names the
  refused step, and gives no format; choosing one needs a new `shapeOutcome` body. Until decided, the step's own code
  and text pass through, and CI-3's refused-sequence rows check the code only.
- **O9. The authoring refusal for a `StepOutcome.many` with shape or form alternatives.** The plan makes `many` in
  authoring "a refusal with the rewrites" and names `AmbiguousForce` (CI-6), with no class, text or rewrites;
  `Texts.codeClasses` lacks it, and section 4's row 8 covers only `Outcome.many`.
- **O10. A proof wording over 400 bytes.** `proofTask` runs before `withinLimits`, so such a proof wording is not
  `limit`; neither the plan nor section 4's row 5 says whether it should be.
  **Ruled** (reviews/dri-decisions-20261102-ci-0.md item 5): `proofTask` gives `limit` for a proof wording over 400 bytes before reading it. O3 to O6,
  O8 and O9: the refusal the spec gives stands (item 5).
